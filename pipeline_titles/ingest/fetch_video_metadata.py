"""Fetch video-level metadata (titles, dates, lengths, views) for the Title
Stylometry corpus - no captions and NO per-video requests.

Everything comes from the channel's tab listing, which yt-dlp reads one page
(30 videos) per request: that is what makes this hundreds of times faster than
the caption pull. A whole channel back to January is a few seconds; the full
276-creator list is well under two hours. The price is that the listing only
carries what YouTube shows on the tab - title, duration, view count, live
status and an *approximate* upload date - not descriptions, tags, likes or
comment counts (those need one extraction per video, ~10 s each with polite
sleeps). Rumble channels are read from Rumble's own listing pages via
download_rumble_subtitles.list_channel_videos, which give exact dates.

Reads a creator list (default data/creator_lists/title_stylometry_creators.txt;
'#' comments, including trailing ones, are ignored) and writes into --out-dir:

    videos.jsonl     one line per (creator, tab, video): every flat field yt-dlp
                     returned plus creator / platform / tab / fetched_at
    channels.jsonl   one line per (creator, tab): channel name, id, follower
                     count, description, tags, verified flag, videos listed
    fetch_log.jsonl  one line per (creator, tab): ok/error, counts, timing -
                     this is also the resume ledger: a (creator, tab) already
                     logged ok is skipped unless --refresh
    videos.csv       compact export rebuilt from videos.jsonl at the end

CLI:

    python -m pipeline_titles.ingest.fetch_video_metadata --since 2026-01-01
    python -m pipeline_titles.ingest.fetch_video_metadata --since 2026-01-01 --tabs videos streams
    python -m pipeline_titles.ingest.fetch_video_metadata --creators my_list.txt --limit 200 --refresh
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Iterable, Optional, Sequence

from pipeline_titles.ingest.youtube_listing import (
    _APPROX_DATE_ARGS,
    _STOP_BUFFER_DAYS,
    _import_yt_dlp,
    normalize_channel_url,
)

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CREATORS = PROJECT_ROOT / "data" / "creator_lists" / "title_stylometry_creators.txt"
DEFAULT_OUT_DIR = PROJECT_ROOT / "data" / "titles"

TABS = ("videos", "streams", "shorts")
YOUTUBE, RUMBLE = "youtube", "rumble"

# Flat-entry / channel-info keys that are bulk or bookkeeping, not data.
_DROP_KEYS = {
    "thumbnails", "formats", "http_headers", "_type", "ie_key", "entries",
    "requested_entries", "__x_forwarded_for_ip", "extractor", "extractor_key",
    "webpage_url_basename", "webpage_url_domain", "original_url", "epoch",
    "playlist_count",
}

CSV_COLUMNS = [
    "creator", "platform", "tab", "video_id", "title", "published",
    "date_precision", "duration", "view_count", "live_status", "url",
    "channel_name", "channel_id",
]


# --------------------------------------------------------------------------- #
# Pure helpers (no network) - unit-tested.
# --------------------------------------------------------------------------- #
def strip_comment(line: str) -> str:
    """Drop a trailing '# ...' comment (and surrounding whitespace) from a line.

    A '#' only starts a comment at the beginning of the line or after
    whitespace, so a URL fragment like '.../watch?v=abc#t=5' would survive.
    """
    if line.lstrip().startswith("#"):
        return ""
    for i, ch in enumerate(line):
        if ch == "#" and i > 0 and line[i - 1].isspace():
            return line[:i].strip()
    return line.strip()


def read_creator_list(path: Path) -> list[str]:
    """Creators from a text file, one per line, comments and blanks removed."""
    return [
        c for line in Path(path).read_text(encoding="utf-8").splitlines()
        if (c := strip_comment(line))
    ]


def platform_of(creator: str) -> str:
    """'rumble' for a rumble.com URL, otherwise 'youtube'."""
    return RUMBLE if "rumble.com/" in creator.lower() else YOUTUBE


def flatten_entry(entry: dict, creator: str, tab: str, channel: dict, fetched_at: str) -> dict:
    """One videos.jsonl row from a yt-dlp flat entry.

    Keeps every scalar/list field yt-dlp gave (minus bulk keys), adds the
    provenance columns, and renders the approximate timestamp as an ISO date.
    """
    row = {k: v for k, v in entry.items() if k not in _DROP_KEYS}
    row["video_id"] = entry.get("id")
    ts = entry.get("timestamp")
    row["published"] = (
        datetime.fromtimestamp(ts, timezone.utc).strftime("%Y-%m-%d") if ts else None
    )
    row["date_precision"] = "approx" if ts else None
    row.update({
        "creator": creator, "platform": YOUTUBE, "tab": tab,
        "channel_name": channel.get("channel") or channel.get("uploader"),
        "channel_id": channel.get("channel_id"),
        "fetched_at": fetched_at,
    })
    return row


def rumble_row(video: dict, creator: str, channel: dict, fetched_at: str) -> dict:
    """One videos.jsonl row from a download_rumble_subtitles video dict."""
    return {
        "video_id": video.get("permalink_id"),
        "rumble_numeric_id": video.get("id"),
        "title": video.get("title") or "",
        "url": video.get("url"),
        "published": video.get("upload_date") or None,
        "date_precision": "exact" if video.get("upload_date") else None,
        "duration": video.get("duration"),
        "view_count": None,
        "live_status": "was_live" if video.get("live") else None,
        "creator": creator, "platform": RUMBLE, "tab": "videos",
        "channel_name": channel.get("channel"), "channel_id": channel.get("channel_id"),
        "fetched_at": fetched_at,
    }


def in_window(row: dict, since: Optional[str], until: Optional[str]) -> bool:
    """Keep rows whose 'published' (YYYY-MM-DD) falls in [since, until].

    Undated rows are dropped from a bounded query rather than guessed at.
    """
    d = row.get("published")
    if since is None and until is None:
        return True
    if not d:
        return False
    return (since is None or d >= since) and (until is None or d <= until)


def channel_record(info: dict, creator: str, tab: str, platform: str,
                   listed: int, fetched_at: str) -> dict:
    """One channels.jsonl row from yt-dlp's channel-level info (minus bulk keys)."""
    rec = {k: v for k, v in info.items() if k not in _DROP_KEYS}
    rec.update({
        "creator": creator, "platform": platform, "tab": tab,
        "channel_name": info.get("channel") or info.get("uploader"),
        "videos_listed": listed, "fetched_at": fetched_at,
    })
    return rec


def csv_row(row: dict) -> list:
    """Project a videos.jsonl row onto CSV_COLUMNS."""
    return [row.get(c) for c in CSV_COLUMNS]


def is_missing_tab_error(message: str) -> bool:
    """True when yt-dlp says the channel simply has no such tab (not a failure)."""
    return "does not have a" in message and "tab" in message


def summarize_log(log_path: Path) -> dict:
    """Latest status per (creator, tab) in fetch_log.jsonl, tallied.

    A job retried after an error appears twice in the ledger; only its most
    recent line counts, so the tally reflects where things stand now.
    """
    latest: dict[tuple[str, str], dict] = {}
    if log_path.is_file():
        for line in log_path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            try:
                rec = json.loads(line)
            except json.JSONDecodeError:
                continue
            latest[(rec.get("creator"), rec.get("tab"))] = rec
    tally = {"settled": len(latest), "ok": 0, "no_tab": 0, "error": 0, "videos_kept": 0}
    for rec in latest.values():
        st = rec.get("status")
        if st in tally:
            tally[st] += 1
        tally["videos_kept"] += int(rec.get("kept") or 0)
    tally["errors"] = [
        (c, t, rec.get("error", "")[:100]) for (c, t), rec in latest.items()
        if rec.get("status") == "error"
    ]
    return tally


def load_done(log_path: Path) -> set[tuple[str, str]]:
    """(creator, tab) pairs settled in fetch_log.jsonl: fetched ok, or the channel
    has no such tab (status 'no_tab', e.g. a channel that never streams). Real
    errors are NOT included, so a resume retries them."""
    done: set[tuple[str, str]] = set()
    if not log_path.is_file():
        return done
    for line in log_path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            rec = json.loads(line)
        except json.JSONDecodeError:
            continue
        if rec.get("status") in ("ok", "no_tab"):
            done.add((rec["creator"], rec["tab"]))
    return done


# --------------------------------------------------------------------------- #
# Network
# --------------------------------------------------------------------------- #
def list_youtube_tab(
    creator: str, tab: str, since: Optional[str], limit: Optional[int],
    sleep: float, quiet: bool = True, _retry: bool = True,
) -> tuple[dict, list[dict]]:
    """(channel_info, flat entries) for one channel tab, newest first.

    Pages lazily and stops once the approximate dates are safely past `since`
    (same early-stop as youtube_api_recent_videos.list_tab_videos).
    """
    url = normalize_channel_url(creator, tab)
    stop_before: Optional[float] = None
    if since:
        dt = datetime.fromisoformat(since).replace(tzinfo=timezone.utc)
        stop_before = (dt - timedelta(days=_STOP_BUFFER_DAYS)).timestamp()

    yt_dlp = _import_yt_dlp()
    opts = {
        "quiet": quiet, "no_warnings": quiet, "skip_download": True,
        "extract_flat": "in_playlist",
        # Let the top-level failure RAISE with yt-dlp's own message ("This
        # channel does not have a streams tab", "This channel was removed",
        # ...) so the caller can classify it; with ignoreerrors the message is
        # only printed and we would just get None back.
        "ignoreerrors": False,
        "extractor_args": _APPROX_DATE_ARGS,
        "sleep_interval_requests": sleep,
    }
    entries: list[dict] = []
    with yt_dlp.YoutubeDL(opts) as ydl:
        info = ydl.extract_info(url, download=False, process=False)
        if not info:
            raise RuntimeError(f"could not read {url}")
        try:
            for entry in info.get("entries") or []:
                if not entry:
                    continue
                ts = entry.get("timestamp")
                if stop_before is not None and ts is not None and ts < stop_before:
                    break
                entries.append(dict(entry))
                if limit is not None and len(entries) >= limit:
                    break
        except Exception as e:  # a mid-crawl page error shouldn't lose the rest
            print(f"  note: stopped listing {url} early ({e}).", file=sys.stderr)
        channel_info = {k: v for k, v in info.items() if k != "entries"}

    # approximate_date is best-effort; an all-undated result is transient - retry once.
    if since and entries and _retry and all(e.get("timestamp") is None for e in entries):
        return list_youtube_tab(creator, tab, since, limit, sleep, quiet, _retry=False)
    return channel_info, entries


def list_rumble_channel(creator: str, since: Optional[str], until: Optional[str],
                        sleep: float) -> tuple[dict, list[dict]]:
    """(channel_info, video dicts) for a rumble.com/c/<slug> channel."""
    from pipeline_titles.ingest.rumble_listing import (
        _session, channel_slug, list_channel_videos,
        normalize_channel_url as rumble_url,
    )
    url = rumble_url(creator)
    videos = list_channel_videos(url, since, until, _session(), sleep, log=lambda *_: None)
    slug = channel_slug(url)
    return {"channel": slug, "channel_id": slug, "channel_url": url}, videos


# --------------------------------------------------------------------------- #
# Driver
# --------------------------------------------------------------------------- #
def _append(path: Path, records: Iterable[dict]) -> None:
    with path.open("a", encoding="utf-8") as fh:
        for rec in records:
            fh.write(json.dumps(rec, ensure_ascii=False) + "\n")


def write_csv(jsonl_path: Path, csv_path: Path) -> int:
    """Rebuild videos.csv from videos.jsonl (de-duplicated on platform+tab+id)."""
    seen: set[tuple] = set()
    n = 0
    with csv_path.open("w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(CSV_COLUMNS)
        if jsonl_path.is_file():
            for line in jsonl_path.read_text(encoding="utf-8").splitlines():
                if not line.strip():
                    continue
                row = json.loads(line)
                key = (row.get("platform"), row.get("tab"), row.get("video_id"))
                if key in seen:
                    continue
                seen.add(key)
                w.writerow(csv_row(row))
                n += 1
    return n


def fetch_all(
    creators: Sequence[str], out_dir: Path, since: Optional[str], until: Optional[str],
    tabs: Sequence[str], limit: Optional[int], sleep: float, refresh: bool,
    quiet: bool = True,
) -> dict:
    out_dir.mkdir(parents=True, exist_ok=True)
    videos_path = out_dir / "videos.jsonl"
    channels_path = out_dir / "channels.jsonl"
    log_path = out_dir / "fetch_log.jsonl"
    done = set() if refresh else load_done(log_path)

    jobs = [
        (c, t) for c in creators
        for t in ((["videos"]) if platform_of(c) == RUMBLE else tabs)
    ]
    totals = {"jobs": len(jobs), "skipped": 0, "ok": 0, "no_tab": 0, "error": 0, "videos": 0}
    for i, (creator, tab) in enumerate(jobs, 1):
        if (creator, tab) in done:
            totals["skipped"] += 1
            continue
        fetched_at = datetime.now(timezone.utc).isoformat(timespec="seconds")
        t0 = time.monotonic()
        platform = platform_of(creator)
        print(f"[{i}/{len(jobs)}] {creator} /{tab} ...", end=" ", flush=True)
        try:
            if platform == RUMBLE:
                info, vids = list_rumble_channel(creator, since, until, sleep)
                rows = [rumble_row(v, creator, info, fetched_at) for v in vids]
            else:
                info, entries = list_youtube_tab(creator, tab, since, limit, sleep, quiet)
                rows = [flatten_entry(e, creator, tab, info, fetched_at) for e in entries]
            listed = len(rows)
            undated = sum(1 for r in rows if not r.get("published"))
            rows = [r for r in rows if in_window(r, since, until)]
            _append(videos_path, rows)
            _append(channels_path, [channel_record(info, creator, tab, platform, listed, fetched_at)])
            rec = {"creator": creator, "tab": tab, "platform": platform, "status": "ok",
                   "listed": listed, "kept": len(rows), "undated": undated,
                   "seconds": round(time.monotonic() - t0, 1), "fetched_at": fetched_at}
            totals["ok"] += 1
            totals["videos"] += len(rows)
            print(f"{len(rows)} kept of {listed} listed ({rec['seconds']}s)")
        except Exception as e:  # noqa: BLE001 - one bad channel must not stop the run
            status = "no_tab" if is_missing_tab_error(str(e)) else "error"
            rec = {"creator": creator, "tab": tab, "platform": platform, "status": status,
                   "error": str(e)[:300], "seconds": round(time.monotonic() - t0, 1),
                   "fetched_at": fetched_at}
            totals[status] += 1
            print("no such tab" if status == "no_tab" else f"ERROR: {str(e)[:120]}")
        _append(log_path, [rec])

    totals["csv_rows"] = write_csv(videos_path, out_dir / "videos.csv")
    return totals


def main(argv: Optional[Sequence[str]] = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--creators", type=Path, default=DEFAULT_CREATORS,
                    help=f"creator list (default: {DEFAULT_CREATORS.name})")
    ap.add_argument("--out-dir", type=Path, default=DEFAULT_OUT_DIR)
    ap.add_argument("--since", default=None, metavar="YYYY-MM-DD",
                    help="keep videos published on/after this date")
    ap.add_argument("--until", default=None, metavar="YYYY-MM-DD",
                    help="keep videos published on/before this date")
    ap.add_argument("--tabs", nargs="+", choices=TABS, default=["videos"],
                    help="YouTube tabs to list (default: videos). Rumble has one listing.")
    ap.add_argument("--limit", type=int, default=None,
                    help="newest N per YouTube tab before date filtering")
    ap.add_argument("--sleep", type=float, default=0.5,
                    help="seconds between listing-page requests (default: 0.5)")
    ap.add_argument("--refresh", action="store_true",
                    help="re-fetch channels already marked ok in fetch_log.jsonl")
    ap.add_argument("-v", "--verbose", action="store_true")
    ap.add_argument("--status", action="store_true",
                    help="print the fetch ledger summary for --out-dir and exit (no network)")
    args = ap.parse_args(argv)

    if args.status:
        t = summarize_log(args.out_dir / "fetch_log.jsonl")
        n_jobs = sum(1 if platform_of(c) == RUMBLE else len(args.tabs)
                     for c in read_creator_list(args.creators)) if args.creators.is_file() else "?"
        print(f"jobs settled {t['settled']} / {n_jobs}   ok {t['ok']}   no_tab {t['no_tab']}   "
              f"error {t['error']}   videos kept {t['videos_kept']}")
        for c, tab, err in t["errors"]:
            print(f"  error: {c} /{tab}: {err}")
        return 0

    for d in (args.since, args.until):
        if d:
            datetime.fromisoformat(d)
    creators = read_creator_list(args.creators)
    if not creators:
        raise SystemExit(f"no creators in {args.creators}")
    totals = fetch_all(creators, args.out_dir, args.since, args.until, args.tabs,
                       args.limit, args.sleep, args.refresh, quiet=not args.verbose)
    print("Done: " + ", ".join(f"{k}={v}" for k, v in totals.items()))
    return 1 if totals["error"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
