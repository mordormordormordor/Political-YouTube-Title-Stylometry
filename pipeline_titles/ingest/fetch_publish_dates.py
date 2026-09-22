"""Fetch the exact publish time of every YouTube video in the corpus from the
YouTube Data API v3 (videos.list), fifty ids per request.

yt-dlp's flat channel listing, which built videos.csv, only carries YouTube's
relative dates ("2 weeks ago"), so every YouTube row is `date_precision =
approx`, accurate to the month. The Data API returns the publish time to the
second, and for a live stream the actual start time too. One videos.list call
costs 1 quota unit and reads 50 ids; the free daily quota is 10,000 units, so
the whole corpus (about 304,000 ids, 6,100 calls) fits in one day with room.
Nothing is billed: a Google Cloud project with the YouTube Data API v3 enabled
and an API key is all it needs (README, Setup).

Reads the YouTube ids from data/titles/videos.csv.gz and writes:

    data/titles/publish_dates.jsonl   the ledger, one line per id as it is
                                      fetched (untracked): published_at,
                                      actual_start, scheduled_start, fetched_at;
                                      an id the API does not return (deleted,
                                      private) is recorded with `missing: true`
                                      so it is not asked for again. Resumable:
                                      ids already in the ledger are skipped.
    data/titles/publish_dates.csv.gz  the tracked export, rebuilt from the
                                      ledger at the end (or with --export):
                                      video_id, published_at, actual_start,
                                      scheduled_start, published_exact (the
                                      UTC date of actual_start for a stream
                                      that went live, else of published_at).
                                      common.load_videos merges it into the
                                      analysis table when it exists.

The key comes from --key, the YOUTUBE_API_KEY variable, or a .env file at the
project root with a YOUTUBE_API_KEY=... line (.env is gitignored). When the
day's quota runs out the run stops cleanly and says how many ids remain; run it
again after the quota resets (midnight Pacific time).

CLI:

    python -m pipeline_titles.ingest.fetch_publish_dates                 # everything not yet fetched
    python -m pipeline_titles.ingest.fetch_publish_dates --limit 500     # a first look
    python -m pipeline_titles.ingest.fetch_publish_dates --dry-run       # counts only, no request
    python -m pipeline_titles.ingest.fetch_publish_dates --export        # rebuild the CSV from the ledger
"""

from __future__ import annotations

import argparse
import gzip
import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable, Iterator, Optional, Sequence

PROJECT_ROOT = Path(__file__).resolve().parents[2]
TITLES_DIR = PROJECT_ROOT / "data" / "titles"
VIDEOS_CSV = TITLES_DIR / "videos.csv.gz"
LEDGER = TITLES_DIR / "publish_dates.jsonl"
EXPORT = TITLES_DIR / "publish_dates.csv.gz"
ENV_FILE = PROJECT_ROOT / ".env"
KEY_VAR = "YOUTUBE_API_KEY"

API_URL = "https://www.googleapis.com/youtube/v3/videos"
BATCH = 50
FIELDS = "items(id,snippet/publishedAt,liveStreamingDetails(actualStartTime,scheduledStartTime))"
TIMEOUT = 30
RETRIES = 5
# A short pause between calls: 6,100 calls take about fifteen minutes and never look like a burst.
SLEEP = 0.1

EXPORT_COLUMNS = ["video_id", "published_at", "actual_start", "scheduled_start", "published_exact"]


# --------------------------------------------------------------------------- pure helpers
def chunks(ids: Sequence[str], size: int = BATCH) -> Iterator[list[str]]:
    """Consecutive slices of `ids`, `size` long (the last may be shorter)."""
    for i in range(0, len(ids), size):
        yield list(ids[i : i + size])


def parse_env(text: str) -> dict[str, str]:
    """KEY=value lines of a .env file; '#' comments, blank lines and 'export ' prefixes ignored, simple quotes stripped."""
    out: dict[str, str] = {}
    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        if line.startswith("export "):
            line = line[len("export ") :]
        k, v = line.split("=", 1)
        v = v.strip()
        if len(v) >= 2 and v[0] == v[-1] and v[0] in "\"'":
            v = v[1:-1]
        out[k.strip()] = v
    return out


def read_key(explicit: Optional[str] = None, env: Optional[dict] = None, env_file: Path = ENV_FILE) -> Optional[str]:
    """The API key: --key, then the environment, then the project's .env file."""
    if explicit:
        return explicit.strip()
    env = os.environ if env is None else env
    if env.get(KEY_VAR):
        return env[KEY_VAR].strip()
    if env_file.exists():
        return parse_env(env_file.read_text(encoding="utf-8")).get(KEY_VAR) or None
    return None


def parse_items(items: Iterable[dict], asked: Sequence[str], fetched_at: str) -> list[dict]:
    """Ledger rows for one response: a row per id asked, the API's times where it returned the id, `missing` otherwise."""
    by_id = {it.get("id"): it for it in items if it.get("id")}
    rows = []
    for vid in asked:
        it = by_id.get(vid)
        if it is None:
            rows.append({"video_id": vid, "missing": True, "published_at": None, "actual_start": None, "scheduled_start": None, "fetched_at": fetched_at})
            continue
        live = it.get("liveStreamingDetails") or {}
        rows.append({
            "video_id": vid,
            "missing": False,
            "published_at": (it.get("snippet") or {}).get("publishedAt"),
            "actual_start": live.get("actualStartTime"),
            "scheduled_start": live.get("scheduledStartTime"),
            "fetched_at": fetched_at,
        })
    return rows


def exact_date(row: dict) -> Optional[str]:
    """The UTC date (YYYY-MM-DD) the video went out: a stream's actual start if it went live, else its publish time."""
    stamp = row.get("actual_start") or row.get("published_at")
    if not stamp:
        return None
    return datetime.fromisoformat(str(stamp).replace("Z", "+00:00")).astimezone(timezone.utc).strftime("%Y-%m-%d")


class QuotaExceeded(Exception):
    """The day's quota is spent (HTTP 403, reason quotaExceeded)."""


def error_reason(payload: dict) -> str:
    try:
        return payload["error"]["errors"][0]["reason"]
    except (KeyError, IndexError, TypeError):
        return ""


# --------------------------------------------------------------------------- I/O
def youtube_ids(path: Path = VIDEOS_CSV) -> list[str]:
    """Every distinct YouTube video id in the analysis table, in file order."""
    import csv

    seen: dict[str, None] = {}
    with gzip.open(path, "rt", encoding="utf-8", newline="") as fh:
        for row in csv.DictReader(fh):
            if row.get("platform") == "youtube" and row.get("video_id"):
                seen.setdefault(row["video_id"], None)
    return list(seen)


def read_ledger(path: Path = LEDGER) -> dict[str, dict]:
    if not path.exists():
        return {}
    out: dict[str, dict] = {}
    with path.open(encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line:
                row = json.loads(line)
                out[row["video_id"]] = row
    return out


def export_csv(ledger: dict[str, dict], path: Path = EXPORT) -> int:
    """The tracked table: one row per fetched id the API returned, sorted by id."""
    import csv

    n = 0
    with gzip.open(path, "wt", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=EXPORT_COLUMNS)
        w.writeheader()
        for vid in sorted(ledger):
            row = ledger[vid]
            if row.get("missing") or not row.get("published_at"):
                continue
            w.writerow({
                "video_id": vid,
                "published_at": row.get("published_at") or "",
                "actual_start": row.get("actual_start") or "",
                "scheduled_start": row.get("scheduled_start") or "",
                "published_exact": exact_date(row) or "",
            })
            n += 1
    return n


def fetch_batch(session, key: str, ids: Sequence[str]) -> list[dict]:
    """One videos.list call, retried on transient errors; raises QuotaExceeded when the day is spent."""
    params = {"part": "snippet,liveStreamingDetails", "id": ",".join(ids), "maxResults": BATCH, "fields": FIELDS, "key": key}
    delay = 2.0
    for attempt in range(1, RETRIES + 1):
        r = session.get(API_URL, params=params, timeout=TIMEOUT)
        if r.status_code == 200:
            return r.json().get("items", [])
        payload = r.json() if r.headers.get("content-type", "").startswith("application/json") else {}
        reason = error_reason(payload)
        if r.status_code == 403 and reason in ("quotaExceeded", "dailyLimitExceeded"):
            raise QuotaExceeded(reason)
        if r.status_code in (400, 401, 403):
            raise SystemExit(f"videos.list refused ({r.status_code} {reason or r.reason}): {payload.get('error', {}).get('message', r.text[:200])}")
        if attempt == RETRIES:
            raise SystemExit(f"videos.list failed {RETRIES} times ({r.status_code} {reason or r.reason}); the ledger is intact, run again to resume")
        print(f"  {r.status_code} {reason or r.reason}; retrying in {delay:.0f}s", file=sys.stderr)
        time.sleep(delay)
        delay = min(delay * 2, 60)
    return []  # unreachable


# --------------------------------------------------------------------------- main
def main(argv: Optional[Sequence[str]] = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--key", help=f"API key (else ${KEY_VAR}, else .env)")
    ap.add_argument("--limit", type=int, help="fetch at most this many ids this run")
    ap.add_argument("--dry-run", action="store_true", help="report what would be fetched and stop")
    ap.add_argument("--export", action="store_true", help="only rebuild the CSV from the ledger")
    ap.add_argument("--videos", type=Path, default=VIDEOS_CSV)
    ap.add_argument("--ledger", type=Path, default=LEDGER)
    ap.add_argument("--out", type=Path, default=EXPORT)
    a = ap.parse_args(argv)

    ledger = read_ledger(a.ledger)
    if a.export:
        n = export_csv(ledger, a.out)
        print(f"wrote {a.out.relative_to(PROJECT_ROOT)}: {n:,} dated ids of {len(ledger):,} in the ledger")
        return 0

    ids = youtube_ids(a.videos)
    todo = [v for v in ids if v not in ledger]
    if a.limit:
        todo = todo[: a.limit]
    calls = (len(todo) + BATCH - 1) // BATCH
    print(f"{len(ids):,} YouTube ids, {len(ledger):,} in the ledger, {len(todo):,} to fetch: {calls:,} calls, {calls:,} quota units")
    if a.dry_run:
        return 0
    if not todo:
        n = export_csv(ledger, a.out)
        print(f"nothing to fetch; wrote {a.out.relative_to(PROJECT_ROOT)} ({n:,} dated ids)")
        return 0

    key = read_key(a.key)
    if not key:
        print(f"no API key: pass --key, set {KEY_VAR}, or put {KEY_VAR}=... in {ENV_FILE.name} (see README, Setup)", file=sys.stderr)
        return 2

    import requests

    session = requests.Session()
    a.ledger.parent.mkdir(parents=True, exist_ok=True)
    done = missing = 0
    started = time.time()
    try:
        with a.ledger.open("a", encoding="utf-8") as fh:
            for i, batch in enumerate(chunks(todo), start=1):
                fetched_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
                rows = parse_items(fetch_batch(session, key, batch), batch, fetched_at)
                for row in rows:
                    fh.write(json.dumps(row, ensure_ascii=False) + "\n")
                    ledger[row["video_id"]] = row
                    done += 1
                    missing += row["missing"]
                fh.flush()
                if i % 50 == 0 or i == calls:
                    rate = done / max(time.time() - started, 1e-9)
                    print(f"  {i:,}/{calls:,} calls, {done:,} ids ({missing:,} missing), {rate:,.0f} ids/s", file=sys.stderr)
                time.sleep(SLEEP)
    except QuotaExceeded as e:
        left = len(todo) - done
        print(f"quota exhausted ({e}) after {done:,} ids this run; {left:,} remain. The quota resets at midnight Pacific time; run again then.", file=sys.stderr)
    except KeyboardInterrupt:
        print(f"\ninterrupted after {done:,} ids; run again to resume", file=sys.stderr)

    n = export_csv(ledger, a.out)
    remaining = sum(1 for v in ids if v not in ledger)
    print(f"ledger: {len(ledger):,} ids ({remaining:,} still unfetched); wrote {a.out.relative_to(PROJECT_ROOT)} with {n:,} dated ids")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
