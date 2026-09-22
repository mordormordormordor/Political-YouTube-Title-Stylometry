"""Stage 0 - prepare the title corpus for every later stage.

Reads data/titles/videos.csv and writes, under data/titles/analysis/:

    titles_prepared.parquet   one row per video (all 309,596 kept) with
                              title_raw, title_norm (show-name prefixes/suffixes,
                              episode numbers, date stamps and channel-brand tags
                              removed), stripped (what was removed), title_key,
                              is_dup / dup_count (verbatim repeats within a
                              creator x genre; first occurrence by date is kept),
                              in_balanced (creator-balanced subset, <= 2,500 unique
                              titles per creator x genre, seed 20260914),
                              low_n (creator x genre with < 50 unique titles)
    stripped_patterns.csv     per creator x genre: every brand pattern that was
                              stripped, its kind, share of titles and an example
    creator_genre_summary.csv rows, unique titles, repeat share, low-n flag,
                              balanced n, subscribers, months active
    zipf_check.csv            corpus Zipf exponent (creator-balanced subset) on raw
                              vs normalized titles, plus the head of each rank list

Brand detection rule (per creator x genre, on unique titles): a delimited leading
or trailing segment (split on ' | ', ' - ', ' – ', ' — ', ' • ', ' ~ ', a 'LABEL: '
colon label, a [bracketed] / (parenthesised) tag or a trailing #hashtag), with
digits collapsed to '#', that occurs in more than 20 % of the group's titles (and
in at least 10 titles) is a brand pattern and is removed wherever it appears in
that position. Generic format labels (LIVE, BREAKING, WATCH, FULL SHOW, ...) are
never stripped because they are style markers used by Stages 2 and 3. Episode
numbers and date stamps are removed from the first and last segment regardless of
frequency (patterns in EPISODE_RES / DATE_RES).

CLI:
    python -m pipeline_titles.prepare
    python -m pipeline_titles.prepare --min-share 0.2 --min-count 10
"""

from __future__ import annotations

import argparse
import re
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from typing import Optional, Sequence

import numpy as np
import pandas as pd

from pipeline_titles.common import (
    ANALYSIS_DIR, BALANCE_CAP, LOW_N, PREPARED, SEED, balanced_mask, load_channels,
    load_videos, nfkc, stage_timer, title_key,
)

MIN_SHARE = 0.20
MIN_COUNT = 10

# Segment separators: pipes with or without spaces; dashes, bullets, tildes and
# guillemets only when surrounded by spaces (so hyphenated words survive).
SEP_RE = re.compile(r"\s*(?:\|\||\|)\s*|\s+(?:-|–|—|•|~|»|«|//|::)\s+")
COLON_LABEL_RE = re.compile(r"^(?P<seg>[^:|\[\]()]{2,60}?):\s+(?P<rest>\S.*)$")
LEAD_BRACKET_RE = re.compile(r"^\s*[\[(](?P<seg>[^\]\)]{1,60})[\])]\s*(?P<rest>.*)$")
TRAIL_BRACKET_RE = re.compile(r"^(?P<rest>.*?)\s*[\[(](?P<seg>[^\]\)]{1,60})[\])]\s*$")
TRAIL_HASHTAGS_RE = re.compile(r"^(?P<rest>.*?)(?P<tags>(?:\s+#[A-Za-z_]\w*)+)\s*$")

# Generic labels that carry style (Stage 2 'leading colon-label', Stage 3 formats):
# never stripped even when a channel uses them on most titles.
GENERIC_LABELS = {
    "live", "breaking", "breaking news", "watch", "watch live", "exclusive", "just in",
    "developing", "update", "alert", "replay", "full show", "full episode", "full interview",
    "full speech", "full video", "highlights", "highlight", "clip", "clips", "reaction",
    "explained", "explainer", "analysis", "opinion", "interview", "debate", "new",
    "must watch", "trending", "viral", "shorts", "short", "premiere", "podcast", "vod",
    "stream", "livestream", "live stream", "full", "part #", "q&a", "special", "urgent",
    "top story", "top stories", "headlines", "news", "world", "world news", "us", "uk",
    "usa", "india", "video", "audio", "trailer", "teaser", "preview", "recap", "review",
    "documentary", "must see", "warning", "graphic", "must-watch", "hot take", "hot mic", "live replay",
    "live now", "watch now", "full stream", "full vod", "livestream replay", "stream replay", "replay live",
}

_MONTHS = r"(?:jan|feb|mar|apr|may|jun|jul|aug|sep|sept|oct|nov|dec)[a-z]*\.?"
_DAYS = r"(?:mon|tue|tues|wed|wednes|thu|thur|thurs|fri|sat|satur|sun)(?:day)?\.?,?\s*"
_NUMDATE = r"\d{1,2}[/.]\d{1,2}[/.](?:\d{4}|\d{2})"
_ISODATE = r"20\d{2}-\d{2}-\d{2}"
_MONDATE = rf"(?:{_DAYS})?(?:{_MONTHS}\s+\d{{1,2}}(?:st|nd|rd|th)?(?:,?\s+20\d{{2}})?|\d{{1,2}}(?:st|nd|rd|th)?\s+{_MONTHS}(?:,?\s+20\d{{2}})?)"
_EP = r"(?:ep|eps|epi|episode|episodes)\.?\s*#?\s*\d+[a-z]?|#\d{1,5}|s\d{1,2}\s*e\d{1,3}|season\s+\d+,?\s+episode\s+\d+"

EPISODE_RES = [
    re.compile(rf"^(?:{_EP})$", re.I),                                   # whole segment
    re.compile(rf"^(?:{_EP})\s*[:\-–—|.]\s*", re.I),                      # leading
    re.compile(rf"\s*[:\-–—|,(]\s*(?:{_EP})\)?\s*$", re.I),               # trailing, delimited
    re.compile(rf"\s+(?:ep|episode)\.?\s*#?\s*\d+[a-z]?\s*$", re.I),      # trailing 'Ep 12'
    re.compile(r"\s+#\d{2,5}\s*$"),                                        # trailing '#123'
]
DATE_RES = [
    re.compile(rf"^(?:{_NUMDATE}|{_ISODATE})$"),                          # whole segment
    re.compile(rf"^(?:{_MONDATE})$", re.I),
    re.compile(rf"^(?:{_NUMDATE}|{_ISODATE})\s*[:\-–—|,.]?\s*"),          # leading numeric date
    re.compile(rf"\s*[:\-–—|,(]?\s*(?:{_NUMDATE}|{_ISODATE}|\d{{1,2}}[/.]\d{{1,2}}[/.]\d{{1,4}})\)?\s*$"),  # trailing numeric date (year may be cut off)
    re.compile(rf"^(?:{_MONDATE})\s*[:\-–—|]\s*", re.I),                  # leading month date, delimited
    re.compile(rf"\s*[:\-–—|(]\s*(?:{_MONDATE})\)?\s*$", re.I),            # trailing month date, delimited
    re.compile(rf",?\s+{_DAYS}{_MONTHS}\s+\d{{1,2}}(?:st|nd|rd|th)?(?:,?\s+20\d{{2}})?\s*$", re.I),  # '..., Monday September 14'
]
_EDGE_PUNCT_RE = re.compile(r"^[\s|\-–—•~:;,.»«/]+|[\s|\-–—•~:;,»«/]+$")


def segment_key(seg: str) -> str:
    """Case-insensitive key of a segment with digit runs collapsed to '#'."""
    k = re.sub(r"\d+", "#", nfkc(seg).lower())
    k = re.sub(r"\s+", " ", k)
    return k.strip(" .,;:!?-–—|•~\"'“”‘’")


def split_segments(title: str) -> list[str]:
    return [s.strip() for s in SEP_RE.split(title) if s and s.strip()]


def segments_with_seps(title: str) -> list[tuple[str, str]]:
    """[(segment, separator_before_it)] preserving the original separators, so a
    stripped title can be rebuilt without rewriting ' - ' as ' | '."""
    out, pos = [], 0
    for m in SEP_RE.finditer(title):
        seg = title[pos:m.start()]
        if seg.strip():
            out.append((seg.strip(), None))
        out.append((None, m.group(0)))
        pos = m.end()
    tail = title[pos:]
    if tail.strip():
        out.append((tail.strip(), None))
    segs, pending = [], ""
    for seg, sep in out:
        if seg is None:
            pending = sep if not pending else pending
        else:
            segs.append((seg, pending)); pending = ""
    return segs


def join_segments(segs: list[tuple[str, str]]) -> str:
    text = ""
    for i, (seg, sep) in enumerate(segs):
        text += seg if i == 0 else (sep or " | ") + seg
    return text


@dataclass
class BrandPatterns:
    """Brand strings detected for one creator x genre (keys are segment_key output)."""
    prefix: dict = field(default_factory=dict)     # key -> (count, example)
    suffix: dict = field(default_factory=dict)
    colon: dict = field(default_factory=dict)
    bracket: dict = field(default_factory=dict)
    hashtag: dict = field(default_factory=dict)

    def rows(self, n_titles: int) -> list[dict]:
        out = []
        for kind in ("prefix", "suffix", "colon", "bracket", "hashtag"):
            for key, (count, example) in getattr(self, kind).items():
                out.append({"kind": kind, "pattern": key, "count": count,
                            "share": round(count / max(n_titles, 1), 4), "example": example})
        return out


def _clean_edges(segs: list, removed: list) -> list:
    """Strip episode numbers / date stamps from the edges of the first and last
    segment and drop segments that were only a date / episode."""
    if segs:
        s0, r = _strip_dates_episodes(segs[0][0]); segs[0] = (s0, segs[0][1]); removed.extend(r)
    if len(segs) > 1:
        s1, r = _strip_dates_episodes(segs[-1][0]); segs[-1] = (s1, segs[-1][1]); removed.extend(r)
    kept = []
    for seg, sep in segs:
        if not seg.strip():
            continue
        s2, r = _strip_dates_episodes(seg)
        if not s2.strip() and r:
            removed.extend(r); continue
        kept.append((seg, sep))
    return kept


def _candidates(title: str) -> dict[str, list[str]]:
    """Candidate brand segments of one title, by kind (un-normalized text), taken
    from the same date/episode-cleaned segments that strip_title works on.
    Prefix candidates are the first segment (and the second when there are three
    or more); suffix candidates the last (and second-last when three or more)."""
    t = nfkc(title)
    out: dict[str, list[str]] = defaultdict(list)
    m = TRAIL_HASHTAGS_RE.match(t)
    if m:
        out["hashtag"].extend(m.group("tags").split())
        t = m.group("rest")
    m = LEAD_BRACKET_RE.match(t)
    if m:
        out["bracket"].append(m.group("seg"))
        t = m.group("rest")
    m = TRAIL_BRACKET_RE.match(t)
    if m:
        out["bracket"].append(m.group("seg"))
        t = m.group("rest")
    segs = [seg for seg, _ in _clean_edges(segments_with_seps(t), [])]
    if len(segs) >= 2:
        out["prefix"].append(segs[0])
        out["suffix"].append(segs[-1])
    if len(segs) >= 3:
        out["prefix"].append(segs[1])
        out["suffix"].append(segs[-2])
    m = COLON_LABEL_RE.match(segs[0] if segs else t)
    if m and len(m.group("seg").split()) <= 6:
        out["colon"].append(m.group("seg"))
    return out


def detect_brand_patterns(titles: Sequence[str], min_share: float = MIN_SHARE,
                          min_count: int = MIN_COUNT) -> BrandPatterns:
    """Brand patterns of one creator x genre: candidate segments whose key occurs in
    more than `min_share` of the (unique) titles and at least `min_count` times."""
    counts: dict[str, Counter] = {k: Counter() for k in ("prefix", "suffix", "colon", "bracket", "hashtag")}
    examples: dict[str, dict] = {k: {} for k in counts}
    n = len(titles)
    for title in titles:
        for kind, segs in _candidates(title).items():
            seen = set()
            for seg in segs:
                key = segment_key(seg)
                if not key or key in seen:
                    continue
                seen.add(key)
                counts[kind][key] += 1
                examples[kind].setdefault(key, seg)
    bp = BrandPatterns()
    for kind, ctr in counts.items():
        for key, c in ctr.items():
            if c >= min_count and c / max(n, 1) > min_share and key not in GENERIC_LABELS:
                getattr(bp, kind)[key] = (c, examples[kind][key])
    return bp


def _strip_dates_episodes(seg: str) -> tuple[str, list[str]]:
    removed = []
    for regs in (EPISODE_RES, DATE_RES):
        for rx in regs:
            m = rx.search(seg)
            if m and m.group(0).strip():
                removed.append(m.group(0).strip(" :-–—|,.()"))
                seg = (seg[:m.start()] + " " + seg[m.end():]).strip()
    return seg, [r for r in removed if r]


def _strip_once(t: str, brand: BrandPatterns) -> tuple[str, list[str]]:
    removed: list[str] = []
    m = TRAIL_HASHTAGS_RE.match(t)
    if m:                                   # trailing hashtags are discovery tags, never content
        removed.extend(m.group("tags").split()); t = m.group("rest")
    for _ in range(2):
        m = LEAD_BRACKET_RE.match(t)
        if m and segment_key(m.group("seg")) in brand.bracket:
            removed.append(m.group("seg")); t = m.group("rest"); continue
        break
    for _ in range(2):
        m = TRAIL_BRACKET_RE.match(t)
        if m and segment_key(m.group("seg")) in brand.bracket:
            removed.append(m.group("seg")); t = m.group("rest"); continue
        break
    segs = _clean_edges(segments_with_seps(t), removed)   # 'Show. Ep. 533 - title': brand segment is now clean
    for _ in range(2):
        if len(segs) >= 2 and segment_key(segs[0][0]) in brand.prefix:
            removed.append(segs.pop(0)[0]); continue
        break
    for _ in range(2):
        if len(segs) >= 2 and segment_key(segs[-1][0]) in brand.suffix:
            removed.append(segs.pop()[0]); continue
        break
    if segs:
        m = COLON_LABEL_RE.match(segs[0][0])
        if m and segment_key(m.group("seg")) in brand.colon:
            removed.append(m.group("seg")); segs[0] = (m.group("rest"), segs[0][1])
    kept = _clean_edges(segs, removed)                    # brand removal may expose a date / episode
    norm = join_segments(kept)
    norm = _EDGE_PUNCT_RE.sub("", norm)
    norm = re.sub(r"\s+", " ", norm).strip()
    return norm, [r for r in removed if r]


def _all_brand(norm: str, brand: BrandPatterns) -> bool:
    """True when every remaining segment is itself a brand key (a live-loop title
    such as 'LIVE: ABC News Live | ABC News' has no content to keep)."""
    keys = set(brand.prefix) | set(brand.suffix) | set(brand.colon) | set(brand.bracket)
    segs = split_segments(norm)
    return bool(segs) and all(segment_key(sg) in keys for sg in segs)


def strip_title(title: str, brand: Optional[BrandPatterns] = None) -> tuple[str, list[str], bool]:
    """Normalize one title. Returns (title_norm, removed strings, brand_only).

    If removing the brand patterns leaves nothing, or leaves only other brand
    segments (the title *was* the show name plus a date), the brand text is kept
    and only episode numbers, dates and hashtags are removed (brand_only=True)."""
    brand = brand or BrandPatterns()
    t = nfkc(title)
    norm, removed = _strip_once(t, brand)
    if norm and not _all_brand(norm, brand):
        return norm, removed, False
    norm2, removed2 = _strip_once(t, BrandPatterns())
    return (norm2 or t), removed2, True


def zipf_slope(counter: Counter, max_rank: int = 1000) -> tuple[float, int]:
    """OLS slope of log(freq) on log(rank) over the top `max_rank` types; returns
    (exponent = -slope, ranks used)."""
    freqs = np.array(sorted(counter.values(), reverse=True)[:max_rank], dtype=float)
    if len(freqs) < 10:
        return float("nan"), len(freqs)
    ranks = np.arange(1, len(freqs) + 1)
    slope = np.polyfit(np.log(ranks), np.log(freqs), 1)[0]
    return float(-slope), len(freqs)


_TOKEN_RE = re.compile(r"[a-z0-9']+")


def tokens(text: str) -> list[str]:
    return _TOKEN_RE.findall(str(text).lower())


# --------------------------------------------------------------------------- #
def run(min_share: float = MIN_SHARE, min_count: int = MIN_COUNT) -> pd.DataFrame:
    ANALYSIS_DIR.mkdir(parents=True, exist_ok=True)
    df = load_videos()
    df["title_raw"] = df["title"].astype(str)
    df["title_nfkc"] = df["title_raw"].map(nfkc)
    # verbatim duplicates within creator x genre (exact raw title after whitespace strip);
    # the earliest-published copy is the one kept for style/topic work
    df = df.sort_values(["creator", "genre", "published", "video_id"], kind="stable")
    dup_grp = df.groupby(["creator", "genre", "title_nfkc"], sort=False)
    df["dup_count"] = dup_grp["row_id"].transform("size").astype(int)
    df["is_dup"] = dup_grp.cumcount() > 0
    df = df.sort_values("row_id").reset_index(drop=True)

    # brand patterns per creator x genre on unique titles
    pattern_rows, norms, removed_col, fallback = [], {}, {}, {}
    for (creator, genre), g in df.groupby(["creator", "genre"], sort=True):
        uniq = g.loc[~g["is_dup"], "title_nfkc"].tolist()
        bp = detect_brand_patterns(uniq, min_share, min_count)
        for r in bp.rows(len(uniq)):
            pattern_rows.append({"creator": creator, "genre": genre, "n_unique_titles": len(uniq), **r})
        cache: dict[str, tuple[str, list[str]]] = {}
        for rid, t in zip(g["row_id"], g["title_nfkc"]):
            if t not in cache:
                cache[t] = strip_title(t, bp)
            norm, rem, fb = cache[t]
            norms[rid] = norm
            removed_col[rid] = " || ".join(rem)
            fallback[rid] = fb
    df["title_norm"] = df["row_id"].map(norms)
    df["stripped"] = df["row_id"].map(removed_col)
    df["norm_fallback"] = df["row_id"].map(fallback)      # brand-only title: brand text kept, dates/episodes removed
    df["title_key"] = df["title_norm"].map(title_key)
    df["title_key_raw"] = df["title_nfkc"].map(title_key)

    # low-n and balanced subset (unique titles only)
    uniq_n = df[~df["is_dup"]].groupby(["creator", "genre"]).size()
    df["n_unique"] = df.set_index(["creator", "genre"]).index.map(uniq_n).astype(int)
    df["low_n"] = df["n_unique"] < LOW_N
    df["in_balanced"] = balanced_mask(df, cap=BALANCE_CAP, seed=SEED, eligible=~df["is_dup"])
    df["has_views"] = df["view_count"].notna()

    cols = ["row_id", "creator", "platform", "genre", "video_id", "title_raw", "title_norm", "stripped",
            "norm_fallback", "title_key", "title_key_raw", "published", "published_at", "date_precision", "month",
            "duration", "view_count", "has_views", "live_status", "url", "channel_name", "channel_id",
            "is_dup", "dup_count", "n_unique", "low_n", "in_balanced"]
    out = df[cols].copy()
    out.to_parquet(PREPARED, index=False)

    pd.DataFrame(pattern_rows).sort_values(["creator", "genre", "share"], ascending=[True, True, False]) \
        .to_csv(ANALYSIS_DIR / "stripped_patterns.csv", index=False)

    # creator x genre summary
    ch = load_channels().rename(columns={"tab": "genre"})
    summ = (out.groupby(["creator", "platform", "genre"])
               .agg(n_rows=("row_id", "size"), n_unique=("is_dup", lambda s: int((~s).sum())),
                    n_balanced=("in_balanced", "sum"), n_with_views=("has_views", "sum"),
                    first_month=("month", "min"), last_month=("month", "max"),
                    n_norm_fallback=("norm_fallback", "sum"))
               .reset_index())
    summ["repeat_share"] = (1 - summ["n_unique"] / summ["n_rows"]).round(4)
    summ["low_n"] = summ["n_unique"] < LOW_N
    summ = summ.merge(ch[["creator", "genre", "channel_name", "channel_follower_count", "channel_is_verified"]],
                      on=["creator", "genre"], how="left")
    summ.to_csv(ANALYSIS_DIR / "creator_genre_summary.csv", index=False)

    # Zipf check: (a) pooled over the balanced subset (labeled raw-pooled figure) and
    # (b) the mean / median of creator x genre exponents, raw vs normalized titles
    bal = out[out["in_balanced"]]
    zrows, crows = [], []
    for name, col in (("raw", "title_raw"), ("normalised", "title_norm")):
        ctr = Counter()
        for t in bal[col]:
            ctr.update(tokens(t))
        for max_rank in (100, 1000, 5000):
            expo, used = zipf_slope(ctr, max_rank)
            zrows.append({"level": "pooled_balanced", "text": name, "max_rank": max_rank,
                          "zipf_exponent": round(expo, 4), "ranks_used": used, "n_titles": len(bal),
                          "n_tokens": sum(ctr.values()), "n_types": len(ctr),
                          "top_20": " ".join(w for w, _ in ctr.most_common(20))})
        for (creator, genre), g in bal.groupby(["creator", "genre"], sort=True):
            if len(g) < LOW_N:
                continue
            c = Counter()
            for t in g[col]:
                c.update(tokens(t))
            expo, used = zipf_slope(c, 200)
            crows.append({"creator": creator, "genre": genre, "text": name, "zipf_exponent_top200": round(expo, 4),
                          "n_titles": len(g), "n_tokens": sum(c.values()), "n_types": len(c),
                          "top_5": " ".join(w for w, _ in c.most_common(5)),
                          "top1_share": round(c.most_common(1)[0][1] / max(sum(c.values()), 1), 4) if c else float("nan")})
    cdf = pd.DataFrame(crows)
    for name in ("raw", "normalised"):
        sub = cdf[cdf["text"] == name]
        zrows.append({"level": "creator_level_mean", "text": name, "max_rank": 200,
                      "zipf_exponent": round(sub["zipf_exponent_top200"].mean(), 4), "ranks_used": 200,
                      "n_titles": int(sub["n_titles"].sum()), "n_tokens": int(sub["n_tokens"].sum()),
                      "n_types": int(sub["n_types"].sum()), "top_20": f"median {sub['zipf_exponent_top200'].median():.4f} over {len(sub)} creator x genre groups (>= {LOW_N} titles)"})
    pd.DataFrame(zrows).to_csv(ANALYSIS_DIR / "zipf_check.csv", index=False)
    cdf.to_csv(ANALYSIS_DIR / "zipf_check_creators.csv", index=False)
    return out


def main(argv: Optional[Sequence[str]] = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--min-share", type=float, default=MIN_SHARE)
    ap.add_argument("--min-count", type=int, default=MIN_COUNT)
    a = ap.parse_args(argv)
    with stage_timer("stage0_prepare", min_share=a.min_share, min_count=a.min_count) as info:
        out = run(a.min_share, a.min_count)
        info["rows"] = int(len(out)); info["unique"] = int((~out["is_dup"]).sum())
        info["balanced"] = int(out["in_balanced"].sum()); info["low_n_groups"] = int(out[out["low_n"]].groupby(["creator", "genre"]).ngroups)
    print(f"rows {info['rows']}  unique {info['unique']}  balanced {info['balanced']}  low-n groups {info['low_n_groups']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
