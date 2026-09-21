"""List a creator's recent YouTube videos from a specific channel tab, via yt-dlp.

This reads a channel *tab* directly - by default the "/videos" tab - so you get
exactly what YouTube shows there: regular long-form videos, with Shorts and live
Streams excluded by YouTube itself (they live on separate /shorts and /streams
tabs). That's the crucial difference from the Data API, which only exposes one
"uploads" feed that lumps Videos + Shorts + Streams together.

It returns video ids, titles, durations, publish dates, and watch URLs - handy
for discovering a backlog before handing the URLs to download_youtube_subtitles.py
(see --out). No API key or quota required; yt-dlp does the work.

Use --format report for a plain-text .txt that lists each video's length, title
and URL, preceded by a per-creator duration summary (count, mean, median, total).

A note on dates: yt-dlp's fast channel listing reports *approximate* upload dates
(roughly month-level granularity), so the "last N months" cutoff is approximate,
not exact. The tab membership itself (which videos) is exact. The listing is
consumed lazily and stops paging once it crosses the cutoff, so even a daily
channel's multi-year backlog only costs a few seconds - it never reads the whole
tab just to keep the newest few months.

CLI examples:

    # Last 3 months of the /videos tab, printed as a table
    python youtube_api_recent_videos.py @PBDPodcast

    # A different tab, last month, as JSON
    python youtube_api_recent_videos.py @PBDPodcast --tab streams --months 1 --format json

    # Point straight at a tab URL (the tab in the URL is respected as-is)
    python youtube_api_recent_videos.py https://www.youtube.com/@PBDPodcast/videos

    # A file of creators (one handle/id/URL per line) -> one combined .txt of
    # every creator's URLs, grouped under a '# <creator>' header. Written next to
    # the input as <name>_urls.txt unless --out is given. The '#' headers are
    # ignored by download_youtube_subtitles --from-file, so it round-trips.
    python -m pipeline_titles.ingest.youtube_listing data/creator_lists/creator_list.txt
    python -m pipeline_titles.ingest.youtube_listing data/creator_lists/creator_list.txt --months 1 --out vods.txt

    # Same file, but a readable report with each video's length + title + URL and
    # per-creator mean/median duration stats -> written to creator_list_report.txt
    python -m pipeline_titles.ingest.youtube_listing data/creator_lists/creator_list.txt --format report
"""

import argparse
import csv
import json
import statistics
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Optional, Sequence

# Channel tabs yt-dlp can list. "/videos" is long-form uploads only (no Shorts,
# no Streams); the others target those dedicated tabs.
TABS = ("videos", "streams", "shorts")

# yt-dlp's YouTube-tab extractor normally omits upload dates from its fast flat
# listing; this arg asks it to include *approximate* ones so we can date-filter
# in a single cheap pass instead of a slow per-video extraction.
_APPROX_DATE_ARGS = {"youtubetab": {"approximate_date": [""]}}


# --------------------------------------------------------------------------- #
# Pure helpers (no network) - unit-testable.
# --------------------------------------------------------------------------- #
def subtract_months(dt: datetime, months: int) -> datetime:
    """Return `dt` shifted back by `months` calendar months.

    Calendar-aware so "3 months" means three months, not 90 days. If the source
    day doesn't exist in the target month (e.g. Mar 31 -> Feb), it clamps to that
    month's last valid day.
    """
    if months < 0:
        raise ValueError("months must be non-negative.")

    month_index = (dt.year * 12 + (dt.month - 1)) - months
    year, month0 = divmod(month_index, 12)
    month = month0 + 1

    if month == 12:
        next_month_first = datetime(year + 1, 1, 1)
    else:
        next_month_first = datetime(year, month + 1, 1)
    days_in_month = (next_month_first - datetime(year, month, 1)).days
    day = min(dt.day, days_in_month)

    return dt.replace(year=year, month=month, day=day)


def normalize_channel_url(creator: str, tab: str = "videos") -> str:
    """Turn a creator handle / channel id / URL into a channel *tab* URL.

    Mirrors download_youtube_subtitles.normalize_channel_url, but defaults to a
    specific tab so bare creators resolve to long-form videos::

        "@PBDPodcast"  -> https://www.youtube.com/@PBDPodcast/videos
        "PBDPodcast"   -> https://www.youtube.com/@PBDPodcast/videos
        "UCabc...23"   -> https://www.youtube.com/channel/UCabc...23/videos

    A full URL is respected as-is, so a link that already names a tab
    (.../videos, .../streams, a playlist) is passed through untouched and `tab`
    is ignored.
    """
    creator = creator.strip()
    if not creator:
        raise ValueError("creator must be a non-empty handle, channel id, or URL.")

    if creator.startswith(("http://", "https://")):
        return creator

    tab_path = f"/{tab}" if tab else ""
    if creator.startswith("@"):
        return f"https://www.youtube.com/{creator}{tab_path}"
    if creator.startswith("UC") and len(creator) == 24:
        return f"https://www.youtube.com/channel/{creator}{tab_path}"
    return f"https://www.youtube.com/@{creator}{tab_path}"


def read_creator_list(path: Path) -> list[str]:
    """Read creator handles/ids/URLs from a text file, one per line.

    Blank lines and lines starting with ``#`` are ignored so the file can be
    commented - mirroring read_video_list in download_youtube_subtitles.py. A
    trailing ``  # note`` after the creator is dropped too (a '#' preceded by
    whitespace starts a comment), so an annotated list such as
    title_stylometry_creators.txt reads cleanly.
    """
    creators: list[str] = []
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        for i, ch in enumerate(stripped):
            if ch == "#" and i > 0 and stripped[i - 1].isspace():
                stripped = stripped[:i].rstrip()
                break
        if stripped:
            creators.append(stripped)
    return creators


def build_watch_url(video_id: str) -> str:
    """Return the canonical watch URL for a video id."""
    return f"https://www.youtube.com/watch?v={video_id}"


def entry_to_video(entry: dict) -> Optional[dict]:
    """Convert one yt-dlp flat playlist entry to our video dict, or None.

    Returns {video_id, title, duration (seconds or None), published_at (aware UTC
    datetime or None), url}. `duration`/`published_at` are None when yt-dlp's flat
    listing couldn't supply them (e.g. an upcoming premiere has no duration yet).
    """
    video_id = entry.get("id")
    if not video_id:
        return None
    ts = entry.get("timestamp")
    published = datetime.fromtimestamp(ts, timezone.utc) if ts else None
    duration = entry.get("duration")
    return {
        "video_id": video_id,
        "title": entry.get("title") or "",
        "duration": float(duration) if duration is not None else None,
        "published_at": published,
        "url": entry.get("url") or build_watch_url(video_id),
    }


def filter_since(videos: Sequence[dict], since: Optional[datetime]) -> list[dict]:
    """Keep videos published on/after `since`; drop those with an unknown date.

    yt-dlp lists a tab newest-first, so the result stays newest-first. Entries
    with no resolvable date are dropped from a date-bounded query rather than
    guessed at.
    """
    if since is None:
        return list(videos)
    if since.tzinfo is None:
        since = since.replace(tzinfo=timezone.utc)
    return [v for v in videos if v["published_at"] and v["published_at"] >= since]


def filter_until(videos: Sequence[dict], until: Optional[datetime]) -> list[dict]:
    """Keep videos published on/before `until`; drop those with an unknown date.

    Symmetric with filter_since: an upper bound that trims the newest videos off a
    newest-first tab listing (e.g. to stop at Aug 1 and skip everything after).
    Undated entries are dropped from a bounded query rather than guessed at.
    """
    if until is None:
        return list(videos)
    if until.tzinfo is None:
        until = until.replace(tzinfo=timezone.utc)
    return [v for v in videos if v["published_at"] and v["published_at"] <= until]


# --------------------------------------------------------------------------- #
# Fetch (imports yt-dlp lazily so the pure helpers stay dependency-free).
# --------------------------------------------------------------------------- #
class ChannelFetchError(RuntimeError):
    """Raised when yt-dlp can't read a channel/tab."""


def _import_yt_dlp():
    try:
        import yt_dlp
    except ImportError as e:
        raise SystemExit(
            "yt-dlp is not installed. Install it with:\n"
            "    pip install -r requirements.txt\n"
            "or upgrade the standalone package:\n"
            "    pip install -U yt-dlp"
        ) from e
    return yt_dlp


# When date-bounded, stop paging this many days *before* the cutoff. yt-dlp's
# approximate dates are only ~month-accurate, so padding past the cutoff by a
# month guarantees we've seen every in-window video before we stop; the exact
# cut is applied afterwards by filter_since().
_STOP_BUFFER_DAYS = 31


def list_tab_videos(
    url: str,
    since: Optional[datetime] = None,
    limit: Optional[int] = None,
    quiet: bool = True,
    _retry: bool = True,
) -> list[dict]:
    """List a channel tab's videos (newest first) as video dicts, stopping early.

    Iterates yt-dlp's *lazy* flat listing (metadata only, no per-video calls) and
    stops paging as soon as it crosses `since` (minus a safety buffer). That's the
    difference between a few seconds and crawling a daily channel's entire
    multi-year backlog. With `since=None` it lists the whole tab (capped by
    `limit`). `limit`, if given, also caps the number of videos kept.
    """
    if limit is not None and limit < 1:
        raise ValueError("limit must be a positive integer.")

    stop_before: Optional[float] = None
    if since is not None:
        if since.tzinfo is None:
            since = since.replace(tzinfo=timezone.utc)
        stop_before = (since - timedelta(days=_STOP_BUFFER_DAYS)).timestamp()

    yt_dlp = _import_yt_dlp()
    opts = {
        "quiet": quiet,
        "no_warnings": quiet,
        "skip_download": True,
        "extract_flat": "in_playlist",
        "ignoreerrors": True,
        "extractor_args": _APPROX_DATE_ARGS,
    }

    videos: list[dict] = []
    with yt_dlp.YoutubeDL(opts) as ydl:
        # process=False keeps `entries` a lazy generator, so breaking out of the
        # loop stops further page requests instead of materialising the whole tab.
        info = ydl.extract_info(url, download=False, process=False)
        if not info:
            raise ChannelFetchError(f"Could not read {url!r} (no such channel/tab?).")

        try:
            for entry in info.get("entries") or []:
                if not entry:
                    continue
                # The tab is newest-first: once we're safely past the cutoff,
                # every remaining video is older, so stop paging.
                if stop_before is not None:
                    ts = entry.get("timestamp")
                    if ts is not None and ts < stop_before:
                        break
                video = entry_to_video(entry)
                if video:
                    videos.append(video)
                if limit is not None and len(videos) >= limit:
                    break
        except Exception as e:  # a mid-crawl page error shouldn't lose the rest
            print(f"  note: stopped listing {url} early ({e}).", file=sys.stderr)

    # approximate_date is best-effort: now and then an extraction returns every
    # entry date-less, which for a date-bounded query defeats the early-stop and
    # makes filter_since wipe the result. That's transient, so retry once.
    if (
        since is not None
        and videos
        and _retry
        and all(v["published_at"] is None for v in videos)
    ):
        return list_tab_videos(url, since=since, limit=limit, quiet=quiet, _retry=False)
    return videos


def get_recent_videos(
    creator: str,
    since: datetime,
    tab: str = "videos",
    limit: Optional[int] = None,
    quiet: bool = True,
    until: Optional[datetime] = None,
) -> list[dict]:
    """Return `creator`'s tab videos published in [`since`, `until`], newest first.

    Resolves the creator to a tab URL (default /videos), lists it, and filters by
    approximate upload date. `until` (optional) caps the newest end. A full URL
    passed as `creator` is used verbatim, so the tab named in it wins over `tab`.
    """
    url = normalize_channel_url(creator, tab)
    videos = list_tab_videos(url, since=since, limit=limit, quiet=quiet)

    # A date-bounded query drops undated videos (see filter_since); if any were
    # dropped, say so on stderr so a glitchy extraction never silently shrinks
    # the result into a misleading "nothing recent".
    if since is not None:
        undated = sum(1 for v in videos if v["published_at"] is None)
        if undated:
            print(
                f"  note: {undated} of {len(videos)} videos from {url} had no "
                f"date and were excluded from the window.",
                file=sys.stderr,
            )
    return filter_until(filter_since(videos, since), until)


def get_recent_videos_for_creators(
    creators: Sequence[str],
    since: datetime,
    tab: str = "videos",
    limit: Optional[int] = None,
    quiet: bool = True,
    progress: bool = True,
    until: Optional[datetime] = None,
) -> list[dict]:
    """Fetch recent videos for several creators. Returns one group per creator::

        {"creator": <as-given>, "videos": [...], "error": <str or None>}

    A creator that fails to resolve or list doesn't abort the run; the failure is
    recorded on that group's ``error`` field and reported to stderr.
    """
    groups: list[dict] = []
    for creator in creators:
        if progress:
            print(f"Fetching {creator} ...", file=sys.stderr)
        try:
            videos = get_recent_videos(
                creator, since=since, tab=tab, limit=limit, quiet=quiet, until=until
            )
            groups.append({"creator": creator, "videos": videos, "error": None})
        except (ChannelFetchError, ValueError) as e:
            print(f"  warning: {creator}: {e}", file=sys.stderr)
            groups.append({"creator": creator, "videos": [], "error": str(e)})
    return groups


# --------------------------------------------------------------------------- #
# Output formatting
# --------------------------------------------------------------------------- #
def format_duration(seconds: Optional[float]) -> str:
    """Render a length in seconds as H:MM:SS (or M:SS under an hour).

    Returns '??:??' for an unknown (None) duration so a value is always present.
    """
    if seconds is None:
        return "??:??"
    total = int(round(seconds))
    hours, rem = divmod(total, 3600)
    minutes, secs = divmod(rem, 60)
    if hours:
        return f"{hours}:{minutes:02d}:{secs:02d}"
    return f"{minutes}:{secs:02d}"


def duration_stats(videos: Sequence[dict]) -> dict:
    """Summarize the durations of `videos` (ignoring any with an unknown length).

    Returns count (all videos), with_duration (how many had a length), and the
    mean / median / total in seconds - or None for those three when nothing had a
    usable duration.
    """
    durations = [v["duration"] for v in videos if v.get("duration")]
    stats = {"count": len(videos), "with_duration": len(durations)}
    if durations:
        stats["mean"] = statistics.mean(durations)
        stats["median"] = statistics.median(durations)
        stats["total"] = sum(durations)
    else:
        stats["mean"] = stats["median"] = stats["total"] = None
    return stats


def format_stats_line(stats: dict) -> str:
    """One-line human summary of duration_stats(), e.g. for a report header."""
    if stats["with_duration"] == 0:
        return f"  {stats['count']} video(s) | no durations available"
    parts = [
        f"{stats['count']} video(s)",
        f"mean {format_duration(stats['mean'])}",
        f"median {format_duration(stats['median'])}",
        f"total {format_duration(stats['total'])}",
    ]
    # Note when the stats cover fewer videos than exist (some lacked a length).
    if stats["with_duration"] != stats["count"]:
        parts.append(f"({stats['with_duration']} timed)")
    return "  " + " | ".join(parts)


def _format_report_body(videos: Sequence[dict]) -> str:
    """A stats line followed by 'length + title' / URL lines, for one creator."""
    if not videos:
        return "  No videos found in the requested window."
    lines = [format_stats_line(duration_stats(videos)), ""]
    for v in videos:
        lines.append(f"  [{format_duration(v.get('duration'))}]  {v['title']}")
        lines.append(f"      {v['url']}")
    return "\n".join(lines)


def format_report(videos: Sequence[dict]) -> str:
    """Human-readable report: a duration stats summary, then each video's length,
    title and URL. Plain text, suitable for a .txt."""
    return _format_report_body(videos)


def format_table(videos: Sequence[dict]) -> str:
    """Human-readable table: publish date, video id, title (newest first)."""
    if not videos:
        return "No videos found in the requested window."
    lines = [format_stats_line(duration_stats(videos)).strip() + ":", ""]
    for v in videos:
        date = v["published_at"].strftime("%Y-%m-%d") if v["published_at"] else "????-??-??"
        dur = format_duration(v.get("duration"))
        lines.append(f"  {date}  {dur:>8}  {v['video_id']}  {v['title']}")
    return "\n".join(lines)


def format_urls(videos: Sequence[dict]) -> str:
    """One watch URL per line, ready for --from-file of the subtitle downloader."""
    return "\n".join(v["url"] for v in videos)


def _video_to_json(v: dict) -> dict:
    """A single video dict with its datetime rendered as an ISO-8601 string."""
    published = v["published_at"]
    return {**v, "published_at": published.isoformat() if published else None}


def format_json(videos: Sequence[dict]) -> str:
    """JSON array with ISO-8601 timestamps."""
    return json.dumps(
        [_video_to_json(v) for v in videos], indent=2, ensure_ascii=False
    )


def format_csv(videos: Sequence[dict]) -> str:
    """CSV with a header row: published_at,duration_seconds,duration,video_id,title,url."""
    from io import StringIO

    buf = StringIO()
    writer = csv.writer(buf)
    writer.writerow(
        ["published_at", "duration_seconds", "duration", "video_id", "title", "url"]
    )
    for v in videos:
        published = v["published_at"].isoformat() if v["published_at"] else ""
        secs = "" if v.get("duration") is None else int(round(v["duration"]))
        writer.writerow(
            [published, secs, format_duration(v.get("duration")),
             v["video_id"], v["title"], v["url"]]
        )
    return buf.getvalue().rstrip("\n")


FORMATTERS = {
    "table": format_table,
    "report": format_report,
    "urls": format_urls,
    "json": format_json,
    "csv": format_csv,
}


def _group_header(group: dict) -> str:
    """A '# <creator>' comment line, annotated with any fetch error."""
    header = f"# {group['creator']}"
    if group["error"]:
        header += f"  (ERROR: {group['error']})"
    return header


def format_grouped(groups: Sequence[dict], fmt: str) -> str:
    """Render several creators' results into one combined document.

    * urls / table / report: each creator's block is introduced by a '# <creator>'
      comment header (blank-line separated). 'report' adds a per-creator duration
      stats line and each video's length + title + URL. The '#' header lines are
      ignored by download_youtube_subtitles --from-file, so a urls document
      round-trips.
    * json: an array of {creator, error, videos} objects.
    * csv: the flat rows, with a leading 'creator' column.
    """
    if fmt == "urls":
        blocks = [
            "\n".join([_group_header(g)] + [v["url"] for v in g["videos"]])
            for g in groups
        ]
        return "\n\n".join(blocks)

    if fmt == "table":
        blocks = [
            "\n".join([_group_header(g), format_table(g["videos"])]) for g in groups
        ]
        return "\n\n".join(blocks)

    if fmt == "report":
        blocks = [
            "\n".join([_group_header(g), _format_report_body(g["videos"])])
            for g in groups
        ]
        # Two blank lines between creators so the sections read as distinct.
        return "\n\n\n".join(blocks)

    if fmt == "json":
        payload = [
            {
                "creator": g["creator"],
                "error": g["error"],
                "videos": [_video_to_json(v) for v in g["videos"]],
            }
            for g in groups
        ]
        return json.dumps(payload, indent=2, ensure_ascii=False)

    if fmt == "csv":
        from io import StringIO

        buf = StringIO()
        writer = csv.writer(buf)
        writer.writerow(
            ["creator", "published_at", "duration_seconds", "duration",
             "video_id", "title", "url"]
        )
        for g in groups:
            for v in g["videos"]:
                published = v["published_at"].isoformat() if v["published_at"] else ""
                secs = "" if v.get("duration") is None else int(round(v["duration"]))
                writer.writerow(
                    [g["creator"], published, secs, format_duration(v.get("duration")),
                     v["video_id"], v["title"], v["url"]]
                )
        return buf.getvalue().rstrip("\n")

    raise ValueError(f"Unknown format: {fmt!r}")


# --------------------------------------------------------------------------- #
# CLI
# --------------------------------------------------------------------------- #
def _resolve_since(months: int, since: Optional[str]) -> datetime:
    """Turn --months / --since into a concrete UTC cutoff (--since wins)."""
    if since is not None:
        try:
            dt = datetime.fromisoformat(since)
        except ValueError as e:
            raise SystemExit(f"--since must be ISO format (YYYY-MM-DD): {e}")
        return dt.replace(tzinfo=timezone.utc) if dt.tzinfo is None else dt
    return subtract_months(datetime.now(timezone.utc), months)


def _resolve_until(until: Optional[str]) -> Optional[datetime]:
    """Parse --until (YYYY-MM-DD) into an inclusive end-of-day UTC cutoff, or None.

    A bare date is extended to 23:59:59 so the whole named day is kept.
    """
    if until is None:
        return None
    try:
        dt = datetime.fromisoformat(until)
    except ValueError as e:
        raise SystemExit(f"--until must be ISO format (YYYY-MM-DD): {e}")
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    if (dt.hour, dt.minute, dt.second, dt.microsecond) == (0, 0, 0, 0):
        dt = dt.replace(hour=23, minute=59, second=59)
    return dt


# Extension and filename suffix for the default --out file, keyed by format.
_OUT_EXT = {"urls": ".txt", "report": ".txt", "table": ".txt", "json": ".json", "csv": ".csv"}
_OUT_SUFFIX = {"urls": "_urls", "report": "_report"}


def _run_creator_file(
    path: Path,
    since: datetime,
    tab: str,
    limit: Optional[int],
    quiet: bool,
    fmt: Optional[str],
    out: Optional[Path],
    until: Optional[datetime] = None,
) -> int:
    """Fetch every creator listed in `path` and write one combined document."""
    creators = read_creator_list(path)
    if not creators:
        raise SystemExit(f"No creators found in {path} (all blank or commented).")

    fmt = fmt or "urls"
    if out is None:
        suffix = _OUT_SUFFIX.get(fmt, "_videos")
        out = path.with_name(f"{path.stem}{suffix}{_OUT_EXT[fmt]}")

    groups = get_recent_videos_for_creators(
        creators, since=since, tab=tab, limit=limit, quiet=quiet, until=until
    )
    out.write_text(format_grouped(groups, fmt) + "\n", encoding="utf-8")

    total = sum(len(g["videos"]) for g in groups)
    failed = [g["creator"] for g in groups if g["error"]]
    print(
        f"Wrote {total} video(s) across {len(creators)} creator(s) to {out}",
        file=sys.stderr,
    )
    if failed:
        print(f"  {len(failed)} creator(s) failed: {', '.join(failed)}", file=sys.stderr)
    return 0


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "List a creator's recent YouTube videos from a channel tab (default "
            "/videos) via yt-dlp - no API key needed. Dates are approximate."
        ),
    )
    parser.add_argument(
        "creator",
        help=(
            "A single creator - channel handle (@name or name), channel id "
            "(UC...), or a full YouTube channel/tab URL - OR the path to a text "
            "file listing one such creator per line. A file input writes one "
            "combined URL document (see --out); a single creator prints to stdout."
        ),
    )
    parser.add_argument(
        "--tab", choices=TABS, default="videos",
        help=(
            "Which channel tab to read for bare handles/ids (default: videos). "
            "Ignored when the creator is a full URL that already names a tab."
        ),
    )
    parser.add_argument(
        "--months", type=int, default=3, metavar="N",
        help="How many months back to include (default: 3). Ignored if --since is set.",
    )
    parser.add_argument(
        "--since", default=None, metavar="YYYY-MM-DD",
        help="Explicit cutoff date; overrides --months. Videos on/after this are kept.",
    )
    parser.add_argument(
        "--until", default=None, metavar="YYYY-MM-DD",
        help="Upper date bound (inclusive): drop videos published after this, so a "
             "pull can stop at, say, Aug 1 instead of running to today.",
    )
    parser.add_argument(
        "--limit", type=int, default=None, metavar="N",
        help=(
            "Cap to the newest N videos on the tab before date-filtering. Handy "
            "for very large channels (default: no cap)."
        ),
    )
    parser.add_argument(
        "--format", choices=sorted(FORMATTERS), default=None,
        help="Output format (default: 'table' for one creator, 'urls' for a file).",
    )
    parser.add_argument(
        "--out", type=Path, default=None, metavar="FILE",
        help=(
            "Write output to FILE. For a single creator, defaults to stdout; for a "
            "creator file, defaults to <name>_urls.txt next to the input."
        ),
    )
    parser.add_argument(
        "-v", "--verbose", action="store_true",
        help="Show yt-dlp's own progress/warning output.",
    )
    args = parser.parse_args(argv)

    if args.months < 0:
        parser.error("--months must be non-negative.")

    since = _resolve_since(args.months, args.since)
    until = _resolve_until(args.until)
    if until is not None and until < since:
        parser.error("--until must be on/after --since.")
    quiet = not args.verbose

    # A positional that names an existing file is a list of creators; anything
    # else (a handle, id, or URL) is a single creator. Handles never look like a
    # real file path, so this stays unambiguous in practice.
    if Path(args.creator).is_file():
        return _run_creator_file(
            Path(args.creator), since, args.tab, args.limit, quiet,
            args.format, args.out, until=until,
        )

    fmt = args.format or "table"
    try:
        videos = get_recent_videos(
            args.creator, since=since, tab=args.tab, limit=args.limit, quiet=quiet,
            until=until,
        )
    except (ChannelFetchError, ValueError) as e:
        raise SystemExit(f"Error: {e}")

    text = FORMATTERS[fmt](videos)
    if args.out:
        args.out.write_text(text + "\n", encoding="utf-8")
        print(f"Wrote {len(videos)} video(s) to {args.out}", file=sys.stderr)
    else:
        print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
