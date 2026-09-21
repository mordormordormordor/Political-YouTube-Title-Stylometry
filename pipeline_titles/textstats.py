"""Pure text-statistics helpers shared by profiles.py and leaning.py (unit-tested):
tokenization for vocabulary work, weighted log-odds with an informative Dirichlet
prior (Monroe, Colaresi & Quinn 2008), rank-turbulence divergence (Dodds et al.
2020), and the capitalization-style classifier."""

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
    curly apostrophes normalized and possessive 's dropped ("Trump’s" -> "trump")."""
    out = []
    for t in _TOKEN_RE.findall(str(text).lower().replace("’", "'")):
        if t.endswith("'s"):
            t = t[:-2]
        if len(t) >= min_len and t not in VOCAB_STOP:
            out.append(t)
    return out


def caps_style(title: str, acronyms: Iterable[str] = ()) -> str:
    """Capitalization style of one title.

    short_other: fewer than three 2+-letter words. all_caps: >= 90 % of words
    ALL CAPS. selective_caps: at least one ALL-CAPS word of 3+ letters that is
    neither a known acronym nor a generic label (LIVE, BREAKING, ...): emphasis
    capitals. mixed_other: the title's first letter or digit is a lower-case
    letter ("this is getting too crazy", "iPhone Duo"); a title that opens with
    a number, a quote, "U.S." or "I" is judged on what follows, since the word
    pattern skips those tokens and the old test on the first matched word
    filed "8 dead after ..." and "U.S. strikes ..." here. title_case: >= 80 %
    of the remaining content words (function words excluded) capitalized.
    sentence_case: fewer than 80 % of the remaining content words capitalized."""
    words = _WORD_RE.findall(title)
    if len(words) < 3:
        return "short_other"
    upper = [w for w in words if w.isupper()]
    if len(upper) / len(words) >= 0.9:
        return "all_caps"
    acr = set(acronyms)
    if any(len(w) >= 3 and w.lower() not in acr and w.lower() not in CAPS_LABELS for w in upper):
        return "selective_caps"
    first = next((ch for ch in title if ch.isalnum()), "")
    if first.isalpha() and first.islower():
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


def tied_ranks(counts: dict[str, float], types: Iterable[str]) -> dict[str, float]:
    """Descending tied ranks (mean of the tied positions, 1-based) over `types`, with
    types absent from `counts` counted as zero, so every absent type shares one last
    tied rank: the allotaxonometer convention (Dodds et al. 2023; MATLAB `tiedrank`)."""
    items = sorted(((t, counts.get(t, 0)) for t in types), key=lambda kv: -kv[1])
    out, i = {}, 0
    while i < len(items):
        j = i
        while j + 1 < len(items) and items[j + 1][1] == items[i][1]:
            j += 1
        mean_rank = (i + 1 + j + 1) / 2
        for k in range(i, j + 1):
            out[items[k][0]] = mean_rank
        i = j + 1
    return out


def rank_turbulence_divergence(counts_a: Counter, counts_b: Counter, alpha: float = 1 / 3) -> tuple[float, list[tuple[str, float, float, float]]]:
    """Rank-turbulence divergence D^R_alpha between two frequency systems, exactly as the
    allotaxonometer computes it (Dodds et al. 2023, EPJ Data Science; allotaxonometer-ui):
    ranks are tied ranks over the union of types with absent types counted as zero,
    the per-type term is (alpha + 1) / alpha * |r_a^-alpha - r_b^-alpha|^(1 / (alpha + 1)),
    and the sum is normalized by the value two disjoint systems of the same sizes would
    give, so D = 0 for identical rankings and 1 for systems with no type in common.
    Returns (D, [(type, contribution, rank_a, rank_b)]) sorted by |contribution|, with
    contribution = the type's normalized term, signed positive when the type is more
    prominent (lower rank) in A. Contributions sum to D in absolute value."""
    types = set(counts_a) | set(counts_b)
    ra, rb = tied_ranks(counts_a, types), tied_ranks(counts_b, types)
    n_a, n_b = sum(1 for t in types if counts_a.get(t, 0) > 0), sum(1 for t in types if counts_b.get(t, 0) > 0)
    inv_a_disjoint, inv_b_disjoint = 1 / (n_b + n_a / 2), 1 / (n_a + n_b / 2)   # rank an absent type would take if the systems were disjoint
    k, e = (alpha + 1) / alpha, 1 / (alpha + 1)
    term = lambda x, y: k * abs(x ** alpha - y ** alpha) ** e
    norm = sum(term(1 / ra[t], inv_b_disjoint) for t in types if counts_a.get(t, 0) > 0) + sum(term(inv_a_disjoint, 1 / rb[t]) for t in types if counts_b.get(t, 0) > 0)
    norm = norm if norm else 1.0
    contribs = []
    for t in types:
        a, b = ra[t], rb[t]
        c = term(1 / a, 1 / b) / norm
        contribs.append((t, c if a < b else -c, a, b))
    contribs.sort(key=lambda x: -abs(x[1]))
    return float(sum(abs(c) for _, c, _, _ in contribs)), contribs


