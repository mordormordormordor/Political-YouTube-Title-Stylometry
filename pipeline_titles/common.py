"""Shared paths, constants and helpers for the Title Stylometry analysis pipeline.

Every stage script (pipeline_titles/prepare.py, topics.py, features.py, ...)
imports from here so that file locations, the random seed, the genre names, the
low-n rule, the creator-balancing rule and the channel grouping (the left / neutral /
right groups of the leaning stage) are defined exactly once.

Stage interface (all under data/titles/analysis/):

    titles_prepared.parquet   Stage 0  one row per video, raw + normalized title, flags
    creators.csv              Stage 0  creator -> channel name / organization / clipper / subscribers
    leaning_by_creator.csv    Stage 0d each channel's title-leaning score and its group (left / neutral / right)
    annotations.parquet       Stage 0c spaCy tokens, POS and entities per unique title
    topics.csv                Stage 1  row_id -> topic
    features.csv              Stage 2  creator x genre x month style features
    dimensions.csv            Stage 2  creator x genre factor scores, raw and topic-controlled
    labels.csv                Stage 2  the LLM-rated title sample
    runtimes.jsonl            every stage appends its wall-clock time and LLM usage
"""

from __future__ import annotations

import contextlib
import hashlib
import json
import re
import time
import unicodedata
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterator, Optional

import numpy as np
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
TITLES_DIR = PROJECT_ROOT / "data" / "titles"
ANALYSIS_DIR = TITLES_DIR / "analysis"
CACHE_DIR = ANALYSIS_DIR / "cache"
REPORTS_DIR = PROJECT_ROOT / "pipeline_titles" / "reports"
VIDEOS_CSV = TITLES_DIR / "videos.csv.gz"          # the large tables are stored gzipped; pandas reads them by extension
PUBLISH_DATES_CSV = TITLES_DIR / "publish_dates.csv.gz"   # exact YouTube publish times from the Data API (ingest.fetch_publish_dates); optional
# The corpus window (the agreed scope, 2026-09-14). The listing fetch used its approximate
# dates to stop paging; with exact dates known, load_videos keeps only titles published inside it.
WINDOW_FROM, WINDOW_TO = "2026-01-01", "2026-09-14"
CHANNELS_JSONL = TITLES_DIR / "channels.jsonl"
CREATOR_LIST = PROJECT_ROOT / "data" / "creator_lists" / "title_stylometry_creators.txt"
RUNTIMES = ANALYSIS_DIR / "runtimes.jsonl"

# Stage outputs (the interface between stages).
PREPARED = ANALYSIS_DIR / "titles_prepared.parquet"
CREATORS_CSV = ANALYSIS_DIR / "creators.csv"
LEANING_BY_CREATOR = ANALYSIS_DIR / "leaning_by_creator.csv"
ANNOTATIONS = ANALYSIS_DIR / "annotations.parquet"
TOPICS_CSV = ANALYSIS_DIR / "topics.csv.gz"
TOPIC_LABELS_CSV = ANALYSIS_DIR / "topic_labels.csv"
FEATURES_CSV = ANALYSIS_DIR / "features.csv.gz"
FEATURES_TITLE = ANALYSIS_DIR / "features_title.parquet"
FEATURES_CREATOR = ANALYSIS_DIR / "features_creator.csv"
DIMENSIONS_CSV = ANALYSIS_DIR / "dimensions.csv"
DIMENSIONS_TITLE = ANALYSIS_DIR / "dimensions_title.parquet"
LABELS_CSV = ANALYSIS_DIR / "labels.csv.gz"
FORMATS_PARQUET = ANALYSIS_DIR / "formats.parquet"
HOOKS_PARQUET = ANALYSIS_DIR / "hooks.parquet"
CAPS_STYLE_TITLE = ANALYSIS_DIR / "caps_style_title.parquet"

SEED = 20260914
GENRES = ("videos", "streams")          # never pooled
BALANCE_CAP = 2500                      # titles per creator x genre in any pooled fit
LOW_N = 50                              # creator x genre below this is reported, never ranked
MIN_ENGAGEMENT_N = 100
MONTHS = [f"2026-{m:02d}" for m in range(1, 10)]
PARTIAL_MONTH = "2026-09"               # 1st-14th only: shown, never compared on volume
# The only between-channel grouping in the analysis: the left / neutral / right channel
# groups of the leaning stage (each channel's score from the title labels, thresholds
# +-0.05; see pipeline_titles/leaning.py). Channels without a score are "unscored".
GROUPS = ("left", "neutral", "right")
GROUP_LABEL = {"left": "left channels", "neutral": "neutral channels", "right": "right channels", "unscored": "unscored channels"}

# Tokens dropped from topic term lists and from lexical-diversity counts.  Kept
# deliberately short: titles are ~10 tokens and function words carry style.
STOPWORDS = sorted({
    "a", "an", "and", "are", "as", "at", "be", "by", "for", "from", "has", "have",
    "he", "her", "his", "in", "is", "it", "its", "of", "on", "or", "that", "the",
    "their", "they", "this", "to", "was", "were", "will", "with", "you", "your",
    "we", "our", "i", "my", "me", "them", "him", "she", "but", "not", "so", "if",
    "than", "then", "there", "these", "those", "what", "who", "how", "why", "when",
    "where", "which", "can", "do", "does", "did", "just", "about", "over", "into",
    "up", "out", "no", "new", "live", "news", "video", "full", "show", "episode",
    "ep", "watch", "vs", "amp", "s", "t", "re", "ve", "ll", "d", "m", "n",
})


# --------------------------------------------------------------------------- #
# Small pure helpers (unit-tested in tests/test_titles_common.py)
# --------------------------------------------------------------------------- #
def creator_slug(creator: str) -> str:
    """Filesystem-safe key: '@HasanAbi' -> 'HasanAbi', a Rumble URL -> 'rumble_GGreenwald'."""
    c = creator.strip()
    if "rumble.com/" in c.lower():
        return "rumble_" + re.sub(r"[^A-Za-z0-9_-]", "", c.rstrip("/").rsplit("/", 1)[-1])
    return re.sub(r"[^A-Za-z0-9_-]", "", c.lstrip("@"))


def month_of(published: str) -> str:
    """'2026-03-17' -> '2026-03'."""
    return str(published)[:7]


def nfkc(text: str) -> str:
    """Unicode NFKC + whitespace collapse (used for the normalized title only)."""
    return re.sub(r"\s+", " ", unicodedata.normalize("NFKC", str(text))).strip()


def title_key(text: str) -> str:
    """Case- and punctuation-insensitive key for matching titles across creators."""
    t = nfkc(text).lower()
    t = re.sub(r"[^\w\s]", " ", t)
    return re.sub(r"\s+", " ", t).strip()


def sha1(text: str) -> str:
    return hashlib.sha1(text.encode("utf-8")).hexdigest()


def balanced_mask(df: pd.DataFrame, cap: int = BALANCE_CAP, seed: int = SEED,
                  group_cols=("creator", "genre"), eligible: Optional[pd.Series] = None) -> pd.Series:
    """Boolean mask marking a creator-balanced subset: within each creator x genre
    every eligible row is kept when the group has <= cap of them, otherwise a random
    sample of `cap` (numpy RandomState(seed); groups visited in sorted order so the
    draw does not depend on row order)."""
    if eligible is None:
        eligible = pd.Series(True, index=df.index)
    rng = np.random.RandomState(seed)
    keep = pd.Series(False, index=df.index)
    sub = df[eligible]
    labels_all = sub.index.to_numpy()
    for _, idx in sub.groupby(list(group_cols), sort=True).indices.items():
        labels = np.sort(labels_all[idx])
        if len(labels) > cap:
            labels = rng.choice(labels, size=cap, replace=False)
        keep.loc[labels] = True
    return keep


def gini(values) -> float:
    """Gini coefficient of a non-negative array (0 = equal, 1 = one video has everything)."""
    x = np.sort(np.asarray(values, dtype=float))
    x = x[~np.isnan(x)]
    if len(x) == 0 or x.sum() == 0:
        return float("nan")
    n = len(x)
    cum = np.cumsum(x)
    return float((n + 1 - 2 * np.sum(cum) / cum[-1]) / n)


def top_share(values, frac: float = 0.10) -> float:
    """Share of the total held by the top `frac` of items (at least one item)."""
    x = np.sort(np.asarray(values, dtype=float))[::-1]
    x = x[~np.isnan(x)]
    if len(x) == 0 or x.sum() == 0:
        return float("nan")
    k = max(1, int(np.ceil(len(x) * frac)))
    return float(x[:k].sum() / x.sum())


# --------------------------------------------------------------------------- #
# Loading
# --------------------------------------------------------------------------- #
def apply_publish_dates(df: pd.DataFrame, dates: pd.DataFrame) -> pd.DataFrame:
    """Replace the listing's approximate `published` with the Data API's exact date where one is known.

    `dates` is publish_dates.csv.gz (video_id, published_at, actual_start, scheduled_start,
    published_exact). A row with a match gets `published` = published_exact (the UTC date a
    stream went live, else of the publish time), `date_precision` = "exact" and `published_at`
    = the full timestamp; every other row keeps what the listing said and an empty
    `published_at`. `month` is recomputed from `published`."""
    d = dates[dates["published_exact"].astype(str).str.len() > 0].drop_duplicates("video_id").set_index("video_id")
    exact = df["video_id"].map(d["published_exact"])
    stamp = df["video_id"].map(d["published_at"])
    has = exact.notna() & (exact.astype(str).str.len() > 0)
    out = df.copy()
    out["published_listed"] = out["published"]
    out.loc[has, "published"] = exact[has].astype(str)
    out.loc[has, "date_precision"] = "exact"
    out["published_at"] = stamp.where(has, "").fillna("").astype(str)
    out["month"] = out["published"].map(month_of)
    return out


def in_window(df: pd.DataFrame, since: str = WINDOW_FROM, until: str = WINDOW_TO) -> pd.DataFrame:
    """The rows whose `published` (YYYY-MM-DD) lies in [since, until]; an undated row is kept."""
    p = df["published"].astype(str)
    keep = (p == "") | ((p >= since) & (p <= until))
    return df[keep].reset_index(drop=True)


def load_videos(path: Path = VIDEOS_CSV, dates_path: Path = PUBLISH_DATES_CSV, window: Optional[tuple[str, str]] = (WINDOW_FROM, WINDOW_TO)) -> pd.DataFrame:
    """videos.csv.gz with `genre` (= tab) and `month` added; view_count/duration numeric; the
    Data API's exact dates applied when publish_dates.csv.gz exists (see apply_publish_dates),
    and then only the titles published inside the corpus window (about 16,000 of the listing's
    "January" titles were December 2025 by their exact date). row_id is assigned after the
    filter, so it is contiguous; the caches downstream are keyed by title text, not row."""
    df = pd.read_csv(path, dtype=str, keep_default_na=False)
    df["genre"] = df["tab"]
    df["month"] = df["published"].map(month_of)
    df["published_at"] = ""
    if dates_path.exists():
        df = apply_publish_dates(df, pd.read_csv(dates_path, dtype=str, keep_default_na=False))
    if window:
        before = len(df)
        df = in_window(df, *window)
        if len(df) != before:
            print(f"load_videos: {before - len(df):,} titles published outside {window[0]}..{window[1]} dropped, {len(df):,} kept", flush=True)
    df["duration"] = pd.to_numeric(df["duration"], errors="coerce")
    df["view_count"] = pd.to_numeric(df["view_count"].replace("", np.nan), errors="coerce")
    df["row_id"] = np.arange(len(df), dtype=np.int64)
    return df


def load_channels(path: Path = CHANNELS_JSONL) -> pd.DataFrame:
    rows = [json.loads(line) for line in Path(path).read_text(encoding="utf-8").splitlines() if line.strip()]
    ch = pd.DataFrame(rows)
    keep = ["creator", "platform", "tab", "channel_name", "channel_id", "channel_follower_count",
            "channel_is_verified", "description", "tags", "videos_listed"]
    return ch[[c for c in keep if c in ch.columns]]


def load_prepared(path: Path = PREPARED) -> pd.DataFrame:
    return pd.read_parquet(path)


def load_creators(path: Path = CREATORS_CSV, with_group: bool = True, leaning_path: Path = LEANING_BY_CREATOR) -> pd.DataFrame:
    """creators.csv (one row per creator: channel_name, platform, organization, clipper,
    subscribers, counts) with `group` = the channel's leaning group (left / neutral /
    right from leaning_by_creator.csv; "unscored" when the leaning stage has not run)."""
    cr = pd.read_csv(path, dtype=str, keep_default_na=False)
    cr["clipper"] = cr["clipper"].str.lower().isin(["true", "1", "yes"])
    if with_group:
        cr["group"] = "unscored"
        if Path(leaning_path).exists():
            lb = pd.read_csv(leaning_path, usecols=["creator", "group"], dtype=str)
            cr["group"] = cr["creator"].map(lb.set_index("creator")["group"]).fillna("unscored")
    return cr


def read_jsonl(path: Path) -> list[dict]:
    if not Path(path).exists():
        return []
    return [json.loads(l) for l in Path(path).read_text(encoding="utf-8").splitlines() if l.strip()]


def append_jsonl(path: Path, record: dict) -> None:
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")


@contextlib.contextmanager
def stage_timer(stage: str, **extra) -> Iterator[dict]:
    """Time a stage and append {stage, seconds, started, finished, ...} to runtimes.jsonl.
    The yielded dict can be filled with extra fields (llm calls, tokens, cost)."""
    info: dict = {}
    t0 = time.time()
    started = datetime.now(timezone.utc).isoformat(timespec="seconds")
    try:
        yield info
    finally:
        rec = {"stage": stage, "seconds": round(time.time() - t0, 1), "started": started,
               "finished": datetime.now(timezone.utc).isoformat(timespec="seconds"), **extra, **info}
        append_jsonl(RUNTIMES, rec)
        print(f"[{stage}] done in {rec['seconds']} s")


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")
