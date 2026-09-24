"""Add channels to the corpus and bring the analysis up to date.

    python -m pipeline_titles.add_channels @SecretScholars
    python -m pipeline_titles.add_channels @SecretScholars rumble.com/c/SomeChannel
    python -m pipeline_titles.add_channels @SecretScholars --fetch-only     # data only, no analysis
    python -m pipeline_titles.add_channels @SecretScholars --dry-run        # what would happen

A channel is a YouTube handle (@Name, or the channel URL) or a Rumble channel URL
(rumble.com/c/Name). The steps, each of which is safe to run again:

    1. creator list    the handle goes into data/creator_lists/title_stylometry_creators.txt
                       under a dated comment; a handle already there is left alone.
    2. listing         ingest.fetch_video_metadata over the list: a (creator, tab) already
                       settled in fetch_log.jsonl is skipped, so only the new channels (and
                       any earlier error) are fetched; seconds per channel. videos.csv.gz is
                       rebuilt from the raw superset videos.jsonl, which must be present.
    3. exact dates     ingest.fetch_publish_dates for the new ids only (Data API key in .env;
                       skipped with a warning when there is none: the channel's titles then
                       carry the listing's month-accurate dates and its January may include
                       December).
    4. the count       how many titles each new channel has inside the corpus window
                       (WINDOW_FROM..WINDOW_TO in common.py), uploads and streams, with a note
                       when a channel is below LOW_N (it is reported, never ranked).
    5. the analysis    run_all --incremental: every sample of record is kept and only the new
                       channels are taken in (leaning labels their titles through the Claude
                       Code CLI, about three calls per channel; topics assigns to the fitted
                       topics; the 3,000-title rating sample is re-keyed, not redrawn); every
                       other stage recomputes over the whole corpus, about a quarter of an hour.

Not done here: the hand-written numbers (README.md, reports/headlines.md) and the website's
import, which reads this repo's tables and needs re-running.
"""

from __future__ import annotations

import argparse
import re
import sys
from datetime import date
from pathlib import Path
from typing import Optional, Sequence

from pipeline_titles.common import CREATOR_LIST, LOW_N, TITLES_DIR, WINDOW_FROM, WINDOW_TO, load_videos
from pipeline_titles.ingest import fetch_video_metadata as listing

TABS = ("videos", "streams")            # the corpus scope (2026-09-14): edited uploads and live-stream VODs, no shorts


# --------------------------------------------------------------------------- #
# Pure helpers (unit-tested)
# --------------------------------------------------------------------------- #
def normalize_creator(text: str) -> str:
    """The creator as the list writes it: '@Handle' for YouTube (from '@Handle', 'Handle' or a
    youtube.com/@Handle URL), 'rumble.com/c/Slug' for Rumble (from any rumble.com/c/... URL)."""
    t = text.strip().rstrip("/")
    m = re.search(r"rumble\.com/c/([^/?#\s]+)", t, re.IGNORECASE)
    if m:
        return f"rumble.com/c/{m.group(1)}"
    m = re.search(r"youtube\.com/@([^/?#\s]+)", t, re.IGNORECASE)
    if m:
        return "@" + m.group(1)
    t = re.sub(r"/(videos|streams|shorts|featured)$", "", t)
    if not re.fullmatch(r"@?[A-Za-z0-9._-]+", t):
        raise ValueError(f"not a YouTube handle or a Rumble channel URL: {text!r}")
    return t if t.startswith("@") else "@" + t


def add_to_list(text: str, creators: Sequence[str], today: Optional[str] = None) -> tuple[str, list[str], list[str]]:
    """The creator list with `creators` appended under a dated comment. Returns (new text,
    added, already there); a creator already in the list (case-insensitively) is not added
    twice, and the text is unchanged when nothing is added."""
    present = {c.lower() for c in listing.read_creator_list_text(text)}
    added, already = [], []
    for c in dict.fromkeys(creators):
        (already if c.lower() in present else added).append(c)
        present.add(c.lower())
    if not added:
        return text, added, already
    block = f"\n# ---------- added {today or date.today().isoformat()} (pipeline_titles.add_channels) ----------\n" + "".join(f"{c}\n" for c in added)
    return text.rstrip("\n") + "\n" + block, added, already


# --------------------------------------------------------------------------- #
# Steps
# --------------------------------------------------------------------------- #
def fetch_listing(creators: Sequence[str], sleep: float) -> dict:
    """ingest.fetch_video_metadata over the whole list; settled jobs are skipped by its ledger."""
    raw = TITLES_DIR / "videos.jsonl"
    if not raw.exists():
        raise SystemExit(f"{raw} (the raw superset the fetcher rebuilds videos.csv.gz from) is missing; "
                         "run the full fetch first (README, Data) or restore it")
    return listing.fetch_all(creators, TITLES_DIR, WINDOW_FROM, None, TABS, None, sleep, refresh=False)


def fetch_dates() -> None:
    """ingest.fetch_publish_dates for the ids not yet in its ledger; a missing key is a warning."""
    from pipeline_titles.ingest import fetch_publish_dates as dates
    rc = dates.main([])
    if rc == 2:
        print("warning: no YouTube Data API key, so the new titles keep the listing's month-accurate dates "
              "(README, Setup). Run `python -m pipeline_titles.ingest.fetch_publish_dates` once there is one.", file=sys.stderr)


def report_new(creators: Sequence[str]) -> None:
    """Titles inside the corpus window per new creator, by genre, with a low-n note."""
    df = load_videos()
    print(f"\ncorpus window {WINDOW_FROM}..{WINDOW_TO}:")
    for c in creators:
        g = df[df["creator"] == c]
        if not len(g):
            print(f"  {c}: no titles in the window (check the handle and fetch_log.jsonl)")
            continue
        n = g.groupby("genre").size()
        exact = (g["date_precision"] == "exact").mean()
        note = "" if n.get("videos", 0) >= LOW_N else f"  (fewer than {LOW_N} uploads: reported, never ranked)"
        print(f"  {c}: {len(g)} titles, {n.get('videos', 0)} uploads, {n.get('streams', 0)} streams, "
              f"{exact:.0%} dated exactly, {g['month'].min()}..{g['month'].max()}{note}")


def main(argv: Optional[Sequence[str]] = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("creators", nargs="+", help="YouTube handles (@Name or URL) and Rumble channel URLs")
    ap.add_argument("--fetch-only", action="store_true", help="steps 1-4 only: add and fetch, no analysis")
    ap.add_argument("--no-dates", action="store_true", help="skip the Data API step")
    ap.add_argument("--sleep", type=float, default=0.5, help="seconds between listing pages (Rumble needs 10; default 0.5)")
    ap.add_argument("--dry-run", action="store_true", help="say what would be added and fetched, change nothing")
    a = ap.parse_args(argv)

    try:
        creators = [normalize_creator(c) for c in a.creators]
    except ValueError as e:
        print(e, file=sys.stderr)
        return 2
    text = Path(CREATOR_LIST).read_text(encoding="utf-8")
    new_text, added, already = add_to_list(text, creators)
    if already:
        print(f"already in the list: {', '.join(already)}")
    if a.dry_run:
        print(f"would add: {', '.join(added) or 'nothing'}; then fetch {TABS} since {WINDOW_FROM}, date the new ids, "
              f"and run run_all --incremental" + (" (skipped: --fetch-only)" if a.fetch_only else ""))
        return 0
    if added:
        Path(CREATOR_LIST).write_text(new_text, encoding="utf-8")
        print(f"added to {Path(CREATOR_LIST).name}: {', '.join(added)}")

    print(f"\n== listing ({', '.join(TABS)} since {WINDOW_FROM}; settled channels skipped)", flush=True)
    totals = fetch_listing(listing.read_creator_list(CREATOR_LIST), a.sleep)
    print("listing: " + ", ".join(f"{k}={v}" for k, v in totals.items()))
    if totals["error"]:
        print("a listing failed (see above and fetch_log.jsonl); running this command again retries it", file=sys.stderr)
    if not a.no_dates:
        print("\n== exact dates (Data API, new ids only)", flush=True)
        fetch_dates()
    report_new(creators)
    if a.fetch_only:
        print("\n--fetch-only: run `python -m pipeline_titles.run_all --incremental` for the analysis")
        return 1 if totals["error"] else 0

    print("\n== analysis (run_all --incremental)", flush=True)
    from pipeline_titles.run_all import main as run_all
    rc = run_all(["--incremental"])
    if rc == 0:
        print("\ndone. Not updated here: the hand-written counts in README.md and reports/headlines.md, "
              "and the website's import (words and politics website: scripts/import-*.mjs).")
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
