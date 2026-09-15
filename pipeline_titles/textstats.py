"""Pure text-statistics helpers shared by profiles.py and leaning.py (unit-tested):
tokenisation for vocabulary work, weighted log-odds with an informative Dirichlet
prior (Monroe, Colaresi & Quinn 2008), rank-turbulence divergence (Dodds et al.
2020), and the capitalisation-style classifier."""

from __future__ import annotations

import re
from collections import Counter
from typing import Iterable, Optional, Sequence

import numpy as np

from pipeline_titles.common import STOPWORDS

try:
    from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS
except Exception:  # pragma: no cover
    ENGLISH_STOP_WORDS = frozenset()

VOCAB_STOP = frozenset(set(STOPWORDS) | set(ENGLISH_STOP_WORDS) | {"amp", "vs", "w", "ft", "ep", "pt", "live", "new", "news", "video", "full", "show", "watch", "podcast", "ing", "ed", "er"})
_TOKEN_RE = re.compile(r"[a-z][a-z'’-]*[a-z]|[a-z]")
_WORD_RE = re.compile(r"[A-Za-z][A-Za-z'’]+")
FUNCTION_WORDS = {"a", "an", "the", "of", "in", "on", "at", "to", "for", "and", "or", "but", "with", "by", "vs", "from", "as", "is",
                  "are", "was", "be", "it", "its", "nor", "per", "via", "into", "over", "than", "that", "this", "up", "out", "off", "so", "if"}
CAPS_LABELS = {"live", "breaking", "watch", "new", "full", "exclusive", "update", "replay", "part", "ep", "vs", "bonus", "premiere",
               "alert", "urgent", "just", "in", "developing", "clip", "clips", "reaction", "debate", "interview", "special", "episode",
               "show", "stream", "vod", "highlights", "review", "recap", "trailer", "official", "warning", "shorts", "audio", "video"}
CAPS_STYLES = ["all_caps", "selective_caps", "title_case", "sentence_case", "mixed_other", "short_other"]


def vocab_tokens(text: str, min_len: int = 2) -> list[str]:
    """Lower-cased word tokens minus stopwords and digits (for vocabulary tables);
    curly apostrophes normalised and possessive 's dropped ("Trump’s" -> "trump")."""
    out = []
    for t in _TOKEN_RE.findall(str(text).lower().replace("’", "'")):
        if t.endswith("'s"):
            t = t[:-2]
        if len(t) >= min_len and t not in VOCAB_STOP:
            out.append(t)
    return out


def caps_style(title: str, acronyms: Iterable[str] = ()) -> str:
    """Capitalisation style of one title.

    short_other: fewer than three 2+-letter words. all_caps: >= 90 % of words
    ALL CAPS. selective_caps: at least one ALL-CAPS word of 3+ letters that is
    neither a known acronym nor a generic label (LIVE, BREAKING, ...): emphasis
    capitals. title_case: first word capitalised and >= 80 % of the remaining
    content words (function words excluded) capitalised. sentence_case: first word
    capitalised and fewer than 80 % of the remaining content words capitalised.
    mixed_other: everything else (lower-case start, odd mixes)."""
    words = _WORD_RE.findall(title)
    if len(words) < 3:
        return "short_other"
    upper = [w for w in words if w.isupper()]
    if len(upper) / len(words) >= 0.9:
        return "all_caps"
    acr = set(acronyms)
    if any(len(w) >= 3 and w.lower() not in acr and w.lower() not in CAPS_LABELS for w in upper):
        return "selective_caps"
    if not words[0][0].isupper():
        return "mixed_other"
    content = [w for w in words[1:] if w.lower() not in FUNCTION_WORDS]
    if not content:
        return "title_case"
    share = sum(w[0].isupper() for w in content) / len(content)
    return "title_case" if share >= 0.8 else "sentence_case"


def weighted_log_odds(counts_a: Counter, counts_b: Counter, alpha0: float = 500.0, min_count: int = 1) -> dict[str, tuple[float, float, int, int]]:
    """Weighted log-odds ratio of word use in A vs B with an informative Dirichlet
    prior proportional to the pooled frequencies (Monroe, Colaresi & Quinn 2008).
    Returns {word: (delta, z, count_a, count_b)}; z = delta / sqrt(var)."""
    pooled = counts_a + counts_b
    n_pool = sum(pooled.values())
    n_a, n_b = sum(counts_a.values()), sum(counts_b.values())
    out = {}
    for w, y_pool in pooled.items():
        alpha_w = alpha0 * y_pool / n_pool
        ya, yb = counts_a.get(w, 0), counts_b.get(w, 0)
        if max(ya, yb) < min_count:
            continue
        la = np.log((ya + alpha_w) / (n_a + alpha0 - ya - alpha_w))
        lb = np.log((yb + alpha_w) / (n_b + alpha0 - yb - alpha_w))
        var = 1.0 / (ya + alpha_w) + 1.0 / (yb + alpha_w)
        delta = la - lb
        out[w] = (float(delta), float(delta / np.sqrt(var)), int(ya), int(yb))
    return out


def rank_turbulence_divergence(counts_a: Counter, counts_b: Counter, alpha: float = 1 / 3) -> tuple[float, list[tuple[str, float, float, float]]]:
    """Rank-turbulence divergence between two frequency systems (Dodds et al. 2020,
    tied ranks by the mean rank). Words missing from one system take rank
    (max rank of that system + 1). Returns (divergence, [(word, contribution,
    rank_a, rank_b)]) with contribution signed: positive = more prominent in A."""
    def ranks(c: Counter) -> dict[str, float]:
        items = sorted(c.items(), key=lambda kv: -kv[1])
        r, i, out = {}, 0, {}
        while i < len(items):
            j = i
            while j + 1 < len(items) and items[j + 1][1] == items[i][1]:
                j += 1
            mean_rank = (i + 1 + j + 1) / 2
            for k in range(i, j + 1):
                out[items[k][0]] = mean_rank
            i = j + 1
        return out
    ra, rb = ranks(counts_a), ranks(counts_b)
    fill_a, fill_b = (max(ra.values()) if ra else 0) + 1, (max(rb.values()) if rb else 0) + 1
    words = set(ra) | set(rb)
    contribs = []
    total = 0.0
    for w in words:
        a, b = ra.get(w, fill_a), rb.get(w, fill_b)
        c = abs(a ** -alpha - b ** -alpha)
        total += c
        contribs.append((w, c if a < b else -c, a, b))
    norm = total if total else 1.0
    contribs = [(w, c / norm, a, b) for w, c, a, b in contribs]
    contribs.sort(key=lambda x: -abs(x[1]))
    return float(total), contribs
