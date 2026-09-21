"""Rumble channel listing (vendored from the Political Quotes Project's
download_rumble_subtitles.py): the parts pipeline_titles.ingest.fetch_video_metadata
needs to page through https://rumble.com/c/<slug> and collect titles, dates and
durations. No captions, no downloads."""

from __future__ import annotations

import json
import re
import time
from typing import Optional, Sequence

USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/128.0 Safari/537.36"
)
RUMBLE_BASE = "https://rumble.com"
VIDEOS_PER_PAGE = 25

_CHANNEL_JSON_RE = re.compile(
    r'<script type="application/json">(.*?)</script>', re.S
)
_CC_KEY_RE = re.compile(r'"cc"\s*:\s*')
# Permalink ids look like "v7dug5i": a 'v' plus base-36 digits.
_PERMALINK_RE = re.compile(r"^v[a-z0-9]{4,10}$")



def normalize_channel_url(channel: str) -> str:
    """Turn a channel slug / path / URL into the bare channel listing URL.

    Accepts, for example::

        "nickjfuentes"                          -> https://rumble.com/c/nickjfuentes
        "c/nickjfuentes"                        -> https://rumble.com/c/nickjfuentes
        "user/someone"                          -> https://rumble.com/user/someone
        "https://rumble.com/c/nickjfuentes?page=2" -> https://rumble.com/c/nickjfuentes

    Any query string / trailing slash is dropped so ``?page=N`` can be appended.
    """
    channel = channel.strip()
    if not channel:
        raise ValueError("channel must be a non-empty slug, path, or URL.")
    if channel.startswith(("http://", "https://")):
        path = re.sub(r"^https?://[^/]+", "", channel)
    else:
        path = "/" + channel.lstrip("/")
    path = path.split("?", 1)[0].split("#", 1)[0].rstrip("/")
    if not path.startswith(("/c/", "/user/")):
        path = "/c" + path
    return RUMBLE_BASE + path


def channel_slug(channel_url: str) -> str:
    """Last path segment of a channel URL: '.../c/nickjfuentes' -> 'nickjfuentes'."""
    return channel_url.rstrip("/").rsplit("/", 1)[-1]


def channel_page_url(channel_url: str, page: int) -> str:
    return f"{channel_url}?page={page}"



def parse_channel_page(html: str) -> list[dict]:
    """Pull the video entries out of a channel listing page.

    Returns one dict per video (newest first, as listed) with the fields the
    downloader needs; anything else in the blob (recommendations, analytics) is
    ignored. An empty list means the page carried no videos - i.e. we've paged
    past the end of the channel.
    """
    m = _CHANNEL_JSON_RE.search(html)
    if not m:
        return []
    try:
        data = json.loads(m.group(1))
    except json.JSONDecodeError:
        return []
    videos: list[dict] = []
    for item in data.get("items", []) or []:
        if not isinstance(item, dict) or item.get("object_type") != "video":
            continue
        pid = item.get("permalink_id")
        if not pid:
            continue
        videos.append(
            {
                "permalink_id": pid,
                "id": item.get("id"),
                "title": item.get("title") or "",
                "url": item.get("url") or f"{RUMBLE_BASE}/{pid}",
                "upload_date": (item.get("upload_date") or "")[:10],
                "duration": item.get("duration") or 0,
                "live": bool(item.get("live")),
                "live_placeholder": bool(item.get("live_placeholder")),
            }
        )
    return videos



def in_window(upload_date: str, since: Optional[str], until: Optional[str]) -> bool:
    """True if ISO date `upload_date` ('YYYY-MM-DD') lies in [since, until]."""
    if not upload_date:
        return False
    if since and upload_date < since:
        return False
    if until and upload_date > until:
        return False
    return True



def _session():
    import requests  # already a project dependency (create_transcripts.py)

    s = requests.Session()
    s.headers.update({"User-Agent": USER_AGENT, "Accept-Language": "en-US,en;q=0.9"})
    return s


# A 429 from Rumble is a per-IP throttle that lasts minutes, not seconds: a short
# retry just burns the remaining attempts. Back off hard (30 s, 60 s, 90 s, ...) and
# honor a Retry-After header when Rumble sends one.
_RATE_LIMIT_BACKOFF = 30.0
_RATE_LIMIT_ATTEMPTS = 6


def _get(session, url: str, attempts: int = 3, timeout: float = 60.0, log=print):
    """GET with retries: brief ones for network errors / 5xx, long ones for 429."""
    last_exc: Optional[Exception] = None
    i = 0
    max_attempts = attempts
    while i < max_attempts:
        try:
            resp = session.get(url, timeout=timeout)
        except Exception as exc:  # network hiccup
            last_exc = exc
            wait = 2.0 * (i + 1)
        else:
            if resp.status_code < 500 and resp.status_code != 429:
                return resp
            last_exc = RuntimeError(f"HTTP {resp.status_code} for {url}")
            if resp.status_code == 429:
                max_attempts = max(max_attempts, _RATE_LIMIT_ATTEMPTS)
                retry_after = resp.headers.get("Retry-After")
                try:
                    wait = float(retry_after) if retry_after else _RATE_LIMIT_BACKOFF * (i + 1)
                except ValueError:
                    wait = _RATE_LIMIT_BACKOFF * (i + 1)
                log(f"  rate-limited (429) on {url}; waiting {wait:.0f}s "
                    f"(attempt {i + 1}/{max_attempts})")
            else:
                wait = 2.0 * (i + 1)
        i += 1
        if i < max_attempts:
            time.sleep(wait)
    raise RuntimeError(f"giving up on {url}: {last_exc}")


def list_channel_videos(
    channel_url: str,
    since: Optional[str],
    until: Optional[str],
    session=None,
    sleep: float = 1.0,
    max_pages: int = 400,
    log=print,
) -> list[dict]:
    """Walk the channel listing newest -> oldest and return videos in the window.

    Stops as soon as a page's oldest upload predates `since` (or the listing
    runs dry). Videos outside [since, until] are dropped.
    """
    session = session or _session()
    found: list[dict] = []
    for page in range(1, max_pages + 1):
        resp = _get(session, channel_page_url(channel_url, page))
        if resp.status_code != 200:
            log(f"  page {page}: HTTP {resp.status_code}, stopping.")
            break
        videos = parse_channel_page(resp.text)
        if not videos:
            log(f"  page {page}: no videos, end of channel.")
            break
        dates = [v["upload_date"] for v in videos if v["upload_date"]]
        log(f"  page {page}: {len(videos)} videos "
            f"({min(dates) if dates else '?'} .. {max(dates) if dates else '?'})")
        found.extend(v for v in videos if in_window(v["upload_date"], since, until))
        if since and dates and min(dates) < since:
            break
        time.sleep(sleep)
    # De-dup (a video can appear pinned on page 1 and again in sequence).
    seen: set[str] = set()
    unique = []
    for v in found:
        if v["permalink_id"] not in seen:
            seen.add(v["permalink_id"])
            unique.append(v)
    return unique


