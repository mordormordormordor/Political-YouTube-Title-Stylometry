"""Word association in titles: the first implementation of docs/word_association_protocol.md.

Every count is over unique titles (verbatim repeats within a creator x genre dropped, and a
title one organization posts on two of its channels counted once). A title's terms are its
content words (textstats.vocab_tokens's rule on the normalized title, possessives folded)
plus phrases: two content words adjacent or one stopword apart, in PHRASE_MIN_TITLES titles
from PHRASE_MIN_CHANNELS channels with title-level NPMI of at least PHRASE_NPMI ("press
conference", "strait of hormuz", "epstein files"; assoc_phrases.csv), and the year stage's
bound pairs whatever their NPMI. A phrase is a term beside its words, so "epstein" is
counted whether or not "epstein files" is in the title, and a word is never tested against
the phrase that contains it or against the other word of its phrase. Presence is binary: a
word counts once per title.

Two checks run through the tables. Replication: the channels are split into two random
halves (an organization's channels together) and every pair statistic is recomputed in each;
a pair is `replicated` when it passes in both with the sign of the full estimate, and only
replicated pairs become edges. Calibration: the temporal screen is compared with an
independent-shift null (every series rotated by its own offset, NULL_SHIFTS times) and the
pair table with a fixed-margins curveball permutation of the title x term matrix inside
every creator x week stratum (NULL_PERMS times); the empirical false-discovery rate at each
threshold is in assoc_temporal_calibration.csv and assoc_pairs_calibration.csv.

Six blocks, each writing its own tables to data/titles/analysis/assoc_*:

  1 temporal    daily share of each term (pooled, and by the share of active channels that
                used it); residuals after day-of-week and a cubic-spline trend; the
                correlation of every pair of residual series with an autocorrelation-adjusted
                effective n (Pyper & Peterman 1998), BH-FDR, and the lag (-LAG_MAX..LAG_MAX
                days) at which the two series agree most
  2 pairs       title-level co-mention of every pair: observed vs expected under global
                independence (log-likelihood ratio G^2, NPMI, log odds ratio) and, the test
                of record, the Cochran-Mantel-Haenszel statistic over creator x week strata
                (co-mention beyond what each word's frequency in each creator's week predicts),
                its BH-FDR q, the stratified lift O/E, and how many channels co-mention the pair
  3 network     the pairs that pass (q, lift, channels) as a weighted graph: Louvain
                communities, degree, strength, betweenness, and whether the case-study words
                share a community across Louvain seeds
  4 monthly     block 2 per month, each term's top neighbors per month, and the drift of each
                term's neighborhood (Jaccard of consecutive months)
  5 case        the Iran / war / Epstein protocol: detrended correlation with a circular-shift
                null, prewhitened cross-correlation, Granger tests, an event study around Iran
                spike days, a negative-binomial day-level regression with controls, CMH within
                creator x week and creator x day, per-group and leave-one-organization-out
                checks, and a random-effects meta-analysis over channels
  6 summary     assoc_summary.json

CLI:
    python -m pipeline_titles.associations
    python -m pipeline_titles.associations --case-only     # block 5 alone (fast)
"""

from __future__ import annotations

import argparse
import json
import math
from collections import Counter
from datetime import date, timedelta
from typing import Optional, Sequence

import networkx as nx
import numpy as np
import pandas as pd
import scipy.sparse as sp
from scipy import stats
from sklearn.preprocessing import SplineTransformer

from pipeline_titles.common import ANALYSIS_DIR, SEED, WINDOW_FROM, WINDOW_TO, load_creators, load_prepared, stage_timer
from pipeline_titles.year import adjacent_pairs, content_tokens, find_collocations, week_of

MIN_TITLES = 100            # a term enters the vocabulary with this many titles ...
MIN_CHANNELS = 10           # ... from this many channels
SERIES_MIN_TITLES = 250     # the daily screen needs about a title a day
PAIR_MIN_OBS = 20           # a pair is tabulated with this many co-mentions ...
PAIR_MIN_CHANNELS = 5       # ... and is an edge only when this many channels co-mention it
Q_FDR = 0.01
LIFT_MIN = 2.0              # observed / expected co-mentions within creator x week strata
LAG_MAX = 14                # days
SPLINE_KNOTS = 6            # cubic B-spline trend, about one knot per seven weeks
NULL_DRAWS = 2000
MONTH_PAIR_MIN_OBS = 10
MONTH_PAIR_MIN_CHANNELS = 3
NEIGHBORS = 20
LOUVAIN_SEEDS = 20
EVENT_Z = 2.0
PHRASE_MIN_TITLES = 50      # a phrase (two content words adjacent or one stopword apart) needs this many titles ...
PHRASE_MIN_CHANNELS = 10    # ... from this many channels ...
PHRASE_NPMI = 0.5           # ... and this much normalized PMI at the title level
NULL_PERMS = 10             # fixed-margins (curveball) permutations of the title x term matrix within creator x week strata
NULL_SHIFTS = 200           # independent circular shifts of every daily series
BOOT_DRAWS = 1000           # stationary-bootstrap draws for the case-study correlations
BOOT_BLOCK = 7.0            # mean block length, days

# The case-study concepts. "narrow" is the word itself; "broad" adds the words that name the same thing.
CONCEPTS = {
    "epstein": ["epstein"],
    "iran": ["iran"],
    "war": ["war"],
    "trump": ["trump"],
    "israel": ["israel"],
    "files": ["files"],
    "epstein_broad": ["epstein", "maxwell", "ghislaine", "ghislaine maxwell"],
    "iran_broad": ["iran", "iranian", "iranians", "tehran", "khamenei", "irgc", "hormuz"],
    "war_broad": ["war", "wars", "strike", "strikes", "airstrike", "airstrikes", "bomb", "bombs", "bombing", "missile", "missiles", "ceasefire"],
    "israel_broad": ["israel", "israeli", "netanyahu", "gaza", "idf"],
}
CASE_PAIRS = [("epstein", "iran"), ("epstein", "war"), ("iran", "war"), ("epstein", "trump"), ("epstein", "files"),
              ("epstein", "israel"), ("iran", "israel"), ("epstein_broad", "iran_broad"), ("epstein_broad", "war_broad")]
CONTROLS = ["trump", "israel", "political"]


# --------------------------------------------------------------------------- #
# small helpers
# --------------------------------------------------------------------------- #
def bh_q(p: np.ndarray) -> np.ndarray:
    """Benjamini-Hochberg adjusted p-values (monotone), NaN kept."""
    p = np.asarray(p, dtype=float)
    q = np.full_like(p, np.nan)
    ok = ~np.isnan(p)
    m = int(ok.sum())
    if m == 0:
        return q
    order = np.argsort(p[ok])
    ranked = p[ok][order] * m / np.arange(1, m + 1)
    ranked = np.minimum.accumulate(ranked[::-1])[::-1]
    out = np.empty(m)
    out[order] = np.minimum(ranked, 1.0)
    q[ok] = out
    return q


def drop_phrase_pairs(pairs: pd.DataFrame, vocab: pd.DataFrame) -> pd.DataFrame:
    """Drop the pairs that are one thing twice: a word with the phrase that contains it ("hormuz" with
    "strait of hormuz"), or the two content words of one phrase ("strait" with "hormuz")."""
    comp = {t: set(w.split("|")) for t, w in zip(vocab["term"], vocab["phrase_words"].fillna("")) if w}
    word_pairs = {frozenset(v) for v in comp.values()}
    a, b = pairs["term_a"].to_numpy(), pairs["term_b"].to_numpy()
    same = np.array([(x in comp and y in comp[x]) or (y in comp and x in comp[y]) or (frozenset((x, y)) in word_pairs) for x, y in zip(a, b)])
    return pairs[~same].reset_index(drop=True)


def design_matrix(days: pd.DatetimeIndex, knots: int = SPLINE_KNOTS) -> np.ndarray:
    """Intercept, six day-of-week dummies and a cubic B-spline trend with `knots` knots."""
    t = np.arange(len(days), dtype=float)[:, None]
    spl = SplineTransformer(n_knots=knots, degree=3, include_bias=False).fit_transform(t)
    dow = np.eye(7)[days.dayofweek][:, 1:]
    return np.column_stack([np.ones(len(days)), dow, spl])


def residualize(Y: np.ndarray, D: np.ndarray) -> np.ndarray:
    Q, _ = np.linalg.qr(D)
    return Y - Q @ (Q.T @ Y)


def standardize(R: np.ndarray) -> np.ndarray:
    s = R.std(axis=0, ddof=1)
    s[s == 0] = np.nan
    return (R - R.mean(axis=0)) / s


def log_share(count: np.ndarray, total: np.ndarray) -> np.ndarray:
    return np.log((count + 0.5) / (total[:, None] + 1.0))


def corr_at_lag(Z: np.ndarray, k: int) -> np.ndarray:
    """Z standardized (n x V). Returns C with C[i, j] = corr(z_i(t), z_j(t + k)) for k >= 0: i leads j by k days."""
    n = Z.shape[0]
    if k == 0:
        return (Z.T @ Z) / (n - 1)
    return (Z[:-k].T @ Z[k:]) / (n - k - 1)


def ccf_series(x: np.ndarray, y: np.ndarray, max_lag: int) -> np.ndarray:
    """corr(x_t, y_{t+k}) for k = -max_lag..max_lag; positive k means x leads y."""
    out = np.empty(2 * max_lag + 1)
    n = len(x)
    for i, k in enumerate(range(-max_lag, max_lag + 1)):
        if k >= 0:
            a, b = x[: n - k], y[k:]
        else:
            a, b = x[-k:], y[: n + k]
        out[i] = np.corrcoef(a, b)[0, 1] if len(a) > 3 else np.nan
    return out


def prewhiten(x: np.ndarray, y: np.ndarray, max_p: int = LAG_MAX) -> tuple[np.ndarray, np.ndarray, int]:
    """Fit AR(p) to x by AIC and apply the same filter to both series (Box & Jenkins)."""
    from statsmodels.tsa.ar_model import AutoReg, ar_select_order
    sel = ar_select_order(x, maxlag=max_p, ic="aic", trend="c")
    lags = list(sel.ar_lags) if sel.ar_lags is not None else []
    if not lags:
        return x - x.mean(), y - y.mean(), 0
    res = AutoReg(x, lags=lags, trend="c").fit()
    phi = {int(l): float(c) for l, c in zip(lags, res.params[1:])}
    p = max(lags)

    def filt(s):
        s = s - s.mean()
        out = s[p:].copy()
        for l, c in phi.items():
            out -= c * s[p - l: len(s) - l]
        return out
    return filt(x), filt(y), p


def stationary_bootstrap_index(n: int, rng: np.random.Generator, mean_block: float = BOOT_BLOCK) -> np.ndarray:
    """Politis & Romano (1994): blocks of geometric length starting at random points, wrapped circularly."""
    idx = np.empty(n, dtype=int)
    pos = 0
    while pos < n:
        start = int(rng.integers(0, n))
        length = int(rng.geometric(1.0 / mean_block))
        block = (start + np.arange(length)) % n
        take = min(length, n - pos)
        idx[pos:pos + take] = block[:take]
        pos += take
    return idx


def cmh_pair(x: np.ndarray, y: np.ndarray, strata: np.ndarray) -> dict:
    """Cochran-Mantel-Haenszel over strata for two binary indicators: z (no continuity
    correction), p, the Mantel-Haenszel odds ratio with its Robins-Breslow-Greenland CI,
    the stratified lift O / E, and the strata that informed it."""
    x = x.astype(float); y = y.astype(float)
    S = int(strata.max()) + 1 if len(strata) else 0
    a = np.bincount(strata, weights=x * y, minlength=S)
    ni = np.bincount(strata, weights=x, minlength=S)
    nj = np.bincount(strata, weights=y, minlength=S)
    n = np.bincount(strata, minlength=S).astype(float)
    ok = n >= 2
    a, ni, nj, n = a[ok], ni[ok], nj[ok], n[ok]
    b, c, d = ni - a, nj - a, n - ni - nj + a
    E = ni * nj / n
    V = ni * nj * (n - ni) * (n - nj) / (n * n * (n - 1))
    O, Es, Vs = a.sum(), E.sum(), V.sum()
    z = (O - Es) / math.sqrt(Vs) if Vs > 0 else float("nan")
    p = float(2 * stats.norm.sf(abs(z))) if not math.isnan(z) else float("nan")
    R, Sm = a * d / n, b * c / n
    Rs, Ss = R.sum(), Sm.sum()
    if Rs > 0 and Ss > 0:
        or_mh = Rs / Ss
        P, Q = (a + d) / n, (b + c) / n
        var = (P * R).sum() / (2 * Rs ** 2) + ((P * Sm).sum() + (Q * R).sum()) / (2 * Rs * Ss) + (Q * Sm).sum() / (2 * Ss ** 2)
        se = math.sqrt(var)
        lo, hi = math.exp(math.log(or_mh) - 1.96 * se), math.exp(math.log(or_mh) + 1.96 * se)
    else:
        or_mh, se, lo, hi = float("nan"), float("nan"), float("nan"), float("nan")
    return {"observed": float(O), "expected": float(Es), "lift": float(O / Es) if Es > 0 else float("nan"),
            "z": float(z), "p": p, "or_mh": float(or_mh), "or_lo": float(lo), "or_hi": float(hi), "log_or_se": float(se),
            "strata": int(ok.sum()), "strata_informative": int(((ni > 0) & (nj > 0) & (ni < n) & (nj < n)).sum())}


def haldane_log_or(a: float, b: float, c: float, d: float) -> tuple[float, float]:
    lo = math.log((a + 0.5) * (d + 0.5) / ((b + 0.5) * (c + 0.5)))
    se = math.sqrt(1 / (a + 0.5) + 1 / (b + 0.5) + 1 / (c + 0.5) + 1 / (d + 0.5))
    return lo, se


def dersimonian_laird(theta: np.ndarray, se: np.ndarray) -> dict:
    """Random-effects pooling of per-channel log odds ratios."""
    w = 1 / se ** 2
    k = len(theta)
    if k < 2:
        return {"k": int(k), "theta_re": float("nan"), "se_re": float("nan"), "tau2": float("nan"), "i2": float("nan"), "q": float("nan"), "q_p": float("nan")}
    tf = (w * theta).sum() / w.sum()
    Q = (w * (theta - tf) ** 2).sum()
    C = w.sum() - (w ** 2).sum() / w.sum()
    tau2 = max(0.0, (Q - (k - 1)) / C) if C > 0 else 0.0
    ws = 1 / (se ** 2 + tau2)
    tre = (ws * theta).sum() / ws.sum()
    return {"k": int(k), "theta_re": float(tre), "se_re": float(math.sqrt(1 / ws.sum())), "tau2": float(tau2),
            "i2": float(max(0.0, (Q - (k - 1)) / Q)) if Q > 0 else 0.0, "q": float(Q), "q_p": float(stats.chi2.sf(Q, k - 1))}


# --------------------------------------------------------------------------- #
# corpus and terms
# --------------------------------------------------------------------------- #
def build_corpus() -> pd.DataFrame:
    prepared = load_prepared()
    creators = load_creators()
    uniq = prepared[~prepared["is_dup"]].copy()
    uniq["org"] = uniq["creator"].map(creators.set_index("creator")["organisation"]).fillna(uniq["creator"])
    uniq["group"] = uniq["creator"].map(creators.set_index("creator")["group"]).fillna("unscored")
    before = len(uniq)
    uniq = uniq.sort_values(["published", "row_id"]).drop_duplicates(["org", "title_key"], keep="first")
    uniq = uniq.sort_values("row_id").reset_index(drop=True)
    print(f"{before:,} unique titles, {before - len(uniq):,} same-organization cross-posts dropped, {len(uniq):,} kept", flush=True)
    topics_path = ANALYSIS_DIR / "topics.csv.gz"
    if topics_path.exists():
        t = pd.read_csv(topics_path, usecols=["row_id", "political"])
        uniq["political"] = uniq["row_id"].map(t.set_index("row_id")["political"]).fillna(True).astype(bool)
    else:
        uniq["political"] = True
    uniq["day"] = pd.to_datetime(uniq["published"])
    uniq["week"] = uniq["published"].map(week_of)
    return uniq


def title_candidates(tokens: list[tuple[str, bool]]) -> dict[str, tuple[str, str]]:
    """The title's candidate phrases: two content words adjacent ("press conference") or one stopword
    apart ("strait of hormuz"), each mapped to its two content words."""
    out = {}
    n = len(tokens)
    for i, (a, ca) in enumerate(tokens):
        if not ca:
            continue
        if i + 1 < n and tokens[i + 1][1]:
            out[f"{a} {tokens[i + 1][0]}"] = (a, tokens[i + 1][0])
        elif i + 2 < n and not tokens[i + 1][1] and tokens[i + 2][1]:
            out[f"{a} {tokens[i + 1][0]} {tokens[i + 2][0]}"] = (a, tokens[i + 2][0])
    return out


def find_phrases(candidates: list[dict[str, tuple[str, str]]], word_titles: Counter, creators: Sequence[str], n_docs: int) -> pd.DataFrame:
    """Candidate phrases in PHRASE_MIN_TITLES titles from PHRASE_MIN_CHANNELS channels with title-level
    NPMI >= PHRASE_NPMI (Bouma 2009: log(p_ab / (p_a p_b)) / -log(p_ab))."""
    titles: Counter = Counter()
    channels: dict[str, set[str]] = {}
    words: dict[str, tuple[str, str]] = {}
    for cand, creator in zip(candidates, creators):
        for name, ab in cand.items():
            titles[name] += 1
            channels.setdefault(name, set()).add(creator)
            words[name] = ab
    rows = []
    for name, n_ab in titles.items():
        if n_ab < PHRASE_MIN_TITLES or len(channels[name]) < PHRASE_MIN_CHANNELS:
            continue
        a, b = words[name]
        pmi = math.log(n_ab * n_docs / (word_titles[a] * word_titles[b]))
        npmi = pmi / -math.log(n_ab / n_docs)
        if npmi >= PHRASE_NPMI:
            rows.append({"phrase": name, "word_a": a, "word_b": b, "gap": int(name.count(" ") == 2), "titles": n_ab, "channels": len(channels[name]), "npmi": round(npmi, 4)})
    return pd.DataFrame(rows, columns=["phrase", "word_a", "word_b", "gap", "titles", "channels", "npmi"]).sort_values("titles", ascending=False).reset_index(drop=True)


def build_terms(uniq: pd.DataFrame) -> tuple[list[set[str]], pd.DataFrame, sp.csr_matrix, dict[str, int]]:
    token_lists = [content_tokens(t) for t in uniq["title_norm"]]
    creators = uniq["creator"].tolist()
    word_sets = [{t for t, ok in tokens if ok} for tokens in token_lists]
    word_titles: Counter = Counter()
    for ws in word_sets:
        word_titles.update(ws)
    candidates = [title_candidates(tokens) for tokens in token_lists]
    phrases = find_phrases(candidates, word_titles, creators, len(uniq))
    # the year stage's bound pairs are phrases too, whatever their NPMI
    bigrams_path = ANALYSIS_DIR / "year_bigrams.csv"
    bound = set(pd.read_csv(bigrams_path)["pair"]) if bigrams_path.exists() else set(find_collocations(token_lists, creators)["pair"])
    extra = [{"phrase": b, "word_a": b.split(" ")[0], "word_b": b.split(" ")[1], "gap": 0, "titles": 0, "channels": 0, "npmi": float("nan")} for b in bound if b not in set(phrases["phrase"])]
    phrases = pd.concat([phrases, pd.DataFrame(extra, columns=phrases.columns)], ignore_index=True)
    phrases["bound_pair"] = phrases["phrase"].isin(bound)
    phrase_words = dict(zip(phrases["phrase"], zip(phrases["word_a"], phrases["word_b"])))
    accepted = set(phrase_words)
    title_terms = [ws | (set(cand) & accepted) for ws, cand in zip(word_sets, candidates)]
    n_titles: Counter = Counter()
    channels: dict[str, set[str]] = {}
    for terms, creator in zip(title_terms, creators):
        for w in terms:
            n_titles[w] += 1
            channels.setdefault(w, set()).add(creator)
    for name in accepted:                      # the bound pairs' own counts
        if name in n_titles:
            phrases.loc[phrases["phrase"] == name, ["titles", "channels"]] = [n_titles[name], len(channels[name])]
    phrases.to_csv(ANALYSIS_DIR / "assoc_phrases.csv", index=False)
    vocab = pd.DataFrame([(w, n, len(channels[w]), w in accepted, "|".join(phrase_words[w]) if w in accepted else "") for w, n in n_titles.items()],
                         columns=["term", "n_titles", "n_channels", "is_phrase", "phrase_words"])
    vocab = vocab[(vocab["n_titles"] >= MIN_TITLES) & (vocab["n_channels"] >= MIN_CHANNELS)].sort_values(["n_titles", "term"], ascending=[False, True]).reset_index(drop=True)
    index = {w: i for i, w in enumerate(vocab["term"])}
    rows, cols = [], []
    for r, terms in enumerate(title_terms):
        for w in terms:
            j = index.get(w)
            if j is not None:
                rows.append(r); cols.append(j)
    X = sp.csr_matrix((np.ones(len(rows), dtype=np.float32), (rows, cols)), shape=(len(title_terms), len(vocab)))
    print(f"phrases: {len(phrases):,} ({int((phrases['gap'] == 1).sum())} with a stopword inside, {int(phrases['bound_pair'].sum())} bound pairs); "
          f"vocabulary: {len(vocab):,} terms ({int(vocab['is_phrase'].sum())} phrases) with >= {MIN_TITLES} titles from >= {MIN_CHANNELS} channels; {X.nnz:,} term mentions", flush=True)
    return title_terms, vocab, X, index


def concept_matrix(title_terms: list[set[str]], concepts: dict[str, list[str]]) -> pd.DataFrame:
    cols = {}
    for name, words in concepts.items():
        ws = set(words)
        cols[name] = np.fromiter((bool(t & ws) for t in title_terms), dtype=bool, count=len(title_terms))
    return pd.DataFrame(cols)


# --------------------------------------------------------------------------- #
# block 1: temporal association
# --------------------------------------------------------------------------- #
def daily_tables(uniq: pd.DataFrame, X: sp.csr_matrix) -> tuple[pd.DatetimeIndex, np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """days, N titles per day, D counts (days x V), B channels using the term (days x V), A active channels per day."""
    days = pd.date_range(WINDOW_FROM, WINDOW_TO, freq="D")
    di = pd.Index(days).get_indexer(uniq["day"])
    Zd = sp.csr_matrix((np.ones(len(uniq), dtype=np.float32), (di, np.arange(len(uniq)))), shape=(len(days), len(uniq)))
    D = (Zd @ X).toarray().astype(np.float64)
    N = np.asarray(Zd.sum(axis=1)).ravel().astype(np.float64)
    ci, creators = pd.factorize(uniq["creator"])
    cd = di * len(creators) + ci
    Zcd = sp.csr_matrix((np.ones(len(uniq), dtype=np.float32), (cd, np.arange(len(uniq)))), shape=(len(days) * len(creators), len(uniq)))
    CD = (Zcd @ X).tocsr()
    CD.data[:] = 1.0                                  # a creator counts once per term per day
    n_cd = len(days) * len(creators)
    M = sp.csr_matrix((np.ones(n_cd, dtype=np.float32), (np.repeat(np.arange(len(days)), len(creators)), np.arange(n_cd))), shape=(len(days), n_cd))
    B = (M @ CD).toarray().astype(np.float64)
    active = np.asarray((Zcd.sum(axis=1) > 0).reshape(len(days), len(creators)).sum(axis=1)).ravel().astype(np.float64)
    return days, N, D, B, active


def channel_halves(uniq: pd.DataFrame, seed: int = SEED) -> np.ndarray:
    """A random split of the channels into two halves (each organization's channels stay together): 0 or 1 per title."""
    orgs = np.array(sorted(uniq["org"].unique()))
    rng = np.random.default_rng(seed)
    half = dict(zip(orgs, rng.permutation(len(orgs)) % 2))
    return uniq["org"].map(half).to_numpy().astype(int)


def series_stats(B: np.ndarray, active: np.ndarray, Dm: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """Residual breadth series, their standardized form, the lag-0 correlation matrix, the effective n
    (Pyper & Peterman 1998) and the lag-1..LAG_MAX autocorrelations."""
    R = residualize(log_share(B, active), Dm)
    Z = standardize(R)
    n = Z.shape[0]
    A = np.stack([(Z[:-k] * Z[k:]).sum(axis=0) / n for k in range(1, LAG_MAX + 1)], axis=1)
    inv_neff = 1.0 / n + (2.0 / n) * (A @ A.T)
    n_eff = np.clip(1.0 / np.maximum(inv_neff, 1e-9), 4, n)
    return R, Z, corr_at_lag(Z, 0), n_eff, A


def corr_p(r: np.ndarray, ne: np.ndarray) -> np.ndarray:
    t = r * np.sqrt((ne - 2) / np.maximum(1 - r ** 2, 1e-12))
    return 2 * stats.t.sf(np.abs(t), ne - 2)


def temporal_block(uniq: pd.DataFrame, X: sp.csr_matrix, vocab: pd.DataFrame) -> dict:
    rng = np.random.default_rng(SEED)
    days, N, D, B, active = daily_tables(uniq, X)
    Dm = design_matrix(days)
    keep = (vocab["n_titles"].to_numpy() >= SERIES_MIN_TITLES)
    terms = vocab["term"].to_numpy()[keep]
    R, Z, C0, n_eff, A = series_stats(B[:, keep], active, Dm)
    n, V = Z.shape
    best_val, best_lag = C0.copy(), np.zeros_like(C0, dtype=int)
    for k in range(1, LAG_MAX + 1):
        Ck = corr_at_lag(Z, k)
        for M, lag in ((Ck, k), (Ck.T, -k)):
            better = np.abs(M) > np.abs(best_val)
            best_val = np.where(better, M, best_val)
            best_lag = np.where(better, lag, best_lag)
    iu, ju = np.triu_indices(V, k=1)
    r = C0[iu, ju]
    ne = n_eff[iu, ju]
    p = corr_p(r, ne)
    pairs = pd.DataFrame({"term_a": terms[iu], "term_b": terms[ju], "r": r, "n_eff": ne, "p": p,
                          "best_lag_days": best_lag[iu, ju], "r_at_best_lag": best_val[iu, ju], "_i": iu, "_j": ju})
    # replication across two random halves of the channels
    halves = channel_halves(uniq)
    for h in (0, 1):
        m = halves == h
        _, _, Bh, ah = daily_tables(uniq[m].reset_index(drop=True), X[m])[1:5]
        _, _, Ch, neh, _ = series_stats(Bh[:, keep], ah, Dm)
        rh = Ch[pairs["_i"], pairs["_j"]]
        pairs[f"r_half_{'ab'[h]}"] = rh
        pairs[f"p_half_{'ab'[h]}"] = corr_p(rh, neh[pairs["_i"], pairs["_j"]])
    pairs = drop_phrase_pairs(pairs, vocab)
    pairs["q"] = bh_q(pairs["p"].to_numpy())
    same_sign = (np.sign(pairs["r_half_a"]) == np.sign(pairs["r"])) & (np.sign(pairs["r_half_b"]) == np.sign(pairs["r"]))
    pairs["replicated"] = (pairs["q"] < 0.05) & same_sign & (pairs["p_half_a"] < 0.05) & (pairs["p_half_b"] < 0.05)
    q = pairs["q"].to_numpy()
    # the shift null: every series rotated by its own random offset (autocorrelation kept, cross-correlation destroyed)
    thresholds = np.array([0.2, 0.25, 0.3, 0.35, 0.4, 0.5, 0.6])
    ii, jj = pairs["_i"].to_numpy(), pairs["_j"].to_numpy()
    obs_abs = np.abs(pairs["r"].to_numpy())
    cut05 = obs_abs[q < 0.05].min() if (q < 0.05).any() else np.nan
    cut01 = obs_abs[q < 0.01].min() if (q < 0.01).any() else np.nan
    thresholds = np.unique(np.concatenate([thresholds, [c for c in (cut05, cut01) if not np.isnan(c)]]))
    null_counts = np.zeros((NULL_SHIFTS, len(thresholds)))
    ar = np.arange(n)
    for b in range(NULL_SHIFTS):
        off = rng.integers(21, n - 21, size=V)
        Zs = Z[(ar[:, None] - off[None, :]) % n, np.arange(V)[None, :]]
        Cs = (Zs.T @ Zs) / (n - 1)
        null_abs = np.abs(Cs[ii, jj])
        null_counts[b] = [(null_abs >= t).sum() for t in thresholds]
    obs_counts = np.array([(obs_abs >= t).sum() for t in thresholds])
    calib = pd.DataFrame({"abs_r_threshold": thresholds, "observed_pairs": obs_counts, "null_pairs_mean": null_counts.mean(axis=0), "null_pairs_sd": null_counts.std(axis=0)})
    calib["empirical_fdr"] = np.where(calib["observed_pairs"] > 0, calib["null_pairs_mean"] / calib["observed_pairs"], np.nan)
    calib["note"] = ["q<0.05 cutoff" if np.isclose(t, cut05) else ("q<0.01 cutoff" if np.isclose(t, cut01) else "") for t in thresholds]
    calib.to_csv(ANALYSIS_DIR / "assoc_temporal_calibration.csv", index=False, float_format="%.4f")
    sig = pairs[pairs["q"] < 0.05].drop(columns=["_i", "_j"]).sort_values("r", ascending=False)
    sig.to_csv(ANALYSIS_DIR / "assoc_temporal_pairs.csv.gz", index=False, float_format="%.5f")
    # the daily table for the vocabulary (long form) and the residual series
    long = pd.DataFrame({"day": np.repeat(days.strftime("%Y-%m-%d"), V), "term": np.tile(terms, n),
                         "titles": D[:, keep].ravel(), "channels": B[:, keep].ravel(),
                         "share_pooled": (D[:, keep] / N[:, None]).ravel(), "share_channels": (B[:, keep] / active[:, None]).ravel(),
                         "residual": R.ravel()})
    long.to_csv(ANALYSIS_DIR / "assoc_daily.csv.gz", index=False, float_format="%.6f")
    pd.DataFrame({"day": days.strftime("%Y-%m-%d"), "titles": N, "active_channels": active}).to_csv(ANALYSIS_DIR / "assoc_days.csv", index=False)
    pd.DataFrame({"term": terms, "n_titles": vocab["n_titles"].to_numpy()[keep], "acf_lag1_residual": A[:, 0], "mean_channels_per_day": B[:, keep].mean(axis=0)}).to_csv(ANALYSIS_DIR / "assoc_series_terms.csv", index=False, float_format="%.4f")
    info = {"series_terms": int(V), "days": int(n), "pairs_tested": int(len(pairs)), "pairs_q01": int((q < 0.01).sum()), "pairs_q05": int(len(sig)),
            "pairs_replicated": int(pairs["replicated"].sum()), "shift_null_fdr_at_q05_cutoff": float(calib.loc[calib["note"] == "q<0.05 cutoff", "empirical_fdr"].iloc[0]) if (q < 0.05).any() else float("nan")}
    print(f"temporal: {V} series over {n} days; {info['pairs_q01']:,} pairs at q<0.01, {len(sig):,} at q<0.05 of {len(pairs):,}; {info['pairs_replicated']:,} replicate in both channel halves; "
          f"shift-null FDR at the q<0.05 cutoff {info['shift_null_fdr_at_q05_cutoff']:.3f}", flush=True)
    return info


# --------------------------------------------------------------------------- #
# block 2: title-level co-mention with creator x week strata
# --------------------------------------------------------------------------- #
def strata_of(uniq: pd.DataFrame, by: Sequence[str]) -> np.ndarray:
    key = uniq[list(by)].astype(str).agg("|".join, axis=1)
    return pd.factorize(key)[0]


def stratified_stats(X: sp.csr_matrix, strata: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Observed co-mentions O, expected E and variance V under independence within each stratum (CMH), all V x V, over strata with >= 2 titles."""
    S = int(strata.max()) + 1
    Zs = sp.csr_matrix((np.ones(X.shape[0], dtype=np.float32), (strata, np.arange(X.shape[0]))), shape=(S, X.shape[0]))
    Nst = (Zs @ X).toarray().astype(np.float64)
    ns = np.asarray(Zs.sum(axis=1)).ravel().astype(np.float64)
    ok = ns >= 2
    rows_ok = ok[strata]
    Xo = X[rows_ok]
    O = (Xo.T @ Xo).toarray().astype(np.float64)
    q = ns[ok]
    a = Nst[ok] / np.sqrt(q)[:, None]
    E = a.T @ a
    v = Nst[ok] * (q[:, None] - Nst[ok]) / (q[:, None] * np.sqrt(q - 1)[:, None])
    Vr = v.T @ v
    return O, E, Vr


def pair_channels(X: sp.csr_matrix, creator_idx: np.ndarray) -> sp.csr_matrix:
    """V x V: how many creators have at least one title that carries both terms."""
    acc = None
    for c in np.unique(creator_idx):
        Xc = X[creator_idx == c]
        P = (Xc.T @ Xc).tocsr()
        P.data[:] = 1.0
        acc = P if acc is None else acc + P
    return acc.tocsr()


def global_stats(X: sp.csr_matrix) -> dict[str, np.ndarray]:
    n = X.shape[0]
    ni = np.asarray(X.sum(axis=0)).ravel().astype(np.float64)
    O = (X.T @ X).toarray().astype(np.float64)
    a = O
    b = ni[:, None] - a
    c = ni[None, :] - a
    d = n - ni[:, None] - ni[None, :] + a
    ea = ni[:, None] * ni[None, :] / n
    eb = ni[:, None] * (n - ni[None, :]) / n
    ec = (n - ni[:, None]) * ni[None, :] / n
    ed = (n - ni[:, None]) * (n - ni[None, :]) / n

    def term(o, e):
        with np.errstate(divide="ignore", invalid="ignore"):
            t = o * np.log(o / e)
        return np.where(o > 0, t, 0.0)
    llr = 2 * (term(a, ea) + term(b, eb) + term(c, ec) + term(d, ed))
    with np.errstate(divide="ignore", invalid="ignore"):
        pmi = np.log((a / n) / ((ni[:, None] / n) * (ni[None, :] / n)))
        npmi = np.where(a > 0, pmi / (-np.log(a / n)), np.nan)
        log_or = np.log((a + 0.5) * (d + 0.5) / ((b + 0.5) * (c + 0.5)))
    return {"O": O, "E0": ea, "llr": llr, "npmi": npmi, "log_or": log_or, "ni": ni}


def curveball(X: sp.csr_matrix, strata: np.ndarray, rng: np.random.Generator, trades_per_title: int = 5) -> sp.csr_matrix:
    """A random binary matrix with every title's number of terms and every term's count within each
    stratum preserved (Strona et al. 2014): repeated trades of the terms two titles of one stratum do
    not share."""
    Xc = X.tocsr()
    rows = [set(Xc.indices[Xc.indptr[i]:Xc.indptr[i + 1]].tolist()) for i in range(Xc.shape[0])]
    order = np.argsort(strata, kind="stable")
    bounds = np.flatnonzero(np.diff(strata[order])) + 1
    for grp in np.split(order, bounds):
        k = len(grp)
        if k < 2:
            continue
        picks = rng.integers(0, k, size=(trades_per_title * k, 2))
        for r1, r2 in picks:
            if r1 == r2:
                continue
            a, b = rows[grp[r1]], rows[grp[r2]]
            shared = a & b
            ua, ub = list(a - shared), list(b - shared)
            if not ua or not ub:
                continue
            pool = ua + ub
            rng.shuffle(pool)
            rows[grp[r1]] = shared | set(pool[:len(ua)])
            rows[grp[r2]] = shared | set(pool[len(ua):])
    indptr = np.zeros(len(rows) + 1, dtype=np.int64)
    indptr[1:] = np.cumsum([len(r) for r in rows])
    indices = np.fromiter((j for r in rows for j in r), dtype=np.int32, count=int(indptr[-1]))
    return sp.csr_matrix((np.ones(len(indices), dtype=np.float32), indices, indptr), shape=Xc.shape)


def pairs_block(uniq: pd.DataFrame, X: sp.csr_matrix, vocab: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    rng = np.random.default_rng(SEED)
    terms = vocab["term"].to_numpy()
    g = global_stats(X)
    strata = strata_of(uniq, ["creator", "week"])
    O, E, Vr = stratified_stats(X, strata)
    creator_idx = pd.factorize(uniq["creator"])[0]
    PC = pair_channels(X, creator_idx)
    V = len(terms)
    iu, ju = np.triu_indices(V, k=1)
    obs = g["O"][iu, ju]
    keep = obs >= PAIR_MIN_OBS
    iu, ju = iu[keep], ju[keep]
    with np.errstate(divide="ignore", invalid="ignore"):
        z = np.where(Vr[iu, ju] > 0, (O[iu, ju] - E[iu, ju]) / np.sqrt(Vr[iu, ju]), np.nan)
        lift = O[iu, ju] / E[iu, ju]
    p = 2 * stats.norm.sf(np.abs(z))
    pairs = pd.DataFrame({
        "term_a": terms[iu], "term_b": terms[ju], "n_a": g["ni"][iu], "n_b": g["ni"][ju],
        "observed": obs[keep], "expected_global": g["E0"][iu, ju], "llr": g["llr"][iu, ju], "npmi": g["npmi"][iu, ju], "log_or": g["log_or"][iu, ju],
        "observed_strat": O[iu, ju], "expected_strat": E[iu, ju], "lift_strat": lift, "z_cmh": z, "p_cmh": p,
        "channels": np.asarray(PC[iu, ju]).ravel(),
    })
    # replication across two random halves of the channels (strata are creator x week, so the halves are disjoint)
    halves = channel_halves(uniq)
    for h in (0, 1):
        m = halves == h
        Oh, Eh, Vh = stratified_stats(X[m], pd.factorize(strata[m])[0])
        with np.errstate(divide="ignore", invalid="ignore"):
            zh = np.where(Vh[iu, ju] > 0, (Oh[iu, ju] - Eh[iu, ju]) / np.sqrt(Vh[iu, ju]), np.nan)
        pairs[f"observed_half_{'ab'[h]}"] = Oh[iu, ju]
        pairs[f"z_half_{'ab'[h]}"] = zh
        pairs[f"q_half_{'ab'[h]}"] = bh_q(2 * stats.norm.sf(np.abs(zh)))
        del Oh, Eh, Vh
    pairs = drop_phrase_pairs(pairs, vocab)
    pairs["q_cmh"] = bh_q(pairs["p_cmh"].to_numpy())
    same_sign = (np.sign(pairs["z_half_a"]) == np.sign(pairs["z_cmh"])) & (np.sign(pairs["z_half_b"]) == np.sign(pairs["z_cmh"]))
    pairs["replicated"] = (pairs["q_cmh"] < Q_FDR) & same_sign & (pairs["q_half_a"] < Q_FDR) & (pairs["q_half_b"] < Q_FDR)
    pairs = pairs.sort_values("z_cmh", ascending=False).reset_index(drop=True)
    pairs.to_csv(ANALYSIS_DIR / "assoc_pairs.csv.gz", index=False, float_format="%.5f")
    # the fixed-margins null: the same z over permuted matrices with every stratum's margins kept (E and Vr are unchanged by construction)
    zpos = pairs.loc[(pairs["q_cmh"] < Q_FDR) & (pairs["z_cmh"] > 0), "z_cmh"]
    cut = float(zpos.min()) if len(zpos) else float("nan")
    thresholds = np.unique(np.concatenate([[3.0, 4.0, 5.0, 6.0, 8.0, 10.0], [cut] if not np.isnan(cut) else []]))
    ok_rows = np.isin(strata, np.flatnonzero(np.bincount(strata) >= 2))
    fu, fj = np.triu_indices(V, k=1)
    null_pos = np.zeros((NULL_PERMS, len(thresholds)))
    null_neg = np.zeros((NULL_PERMS, len(thresholds)))
    for b in range(NULL_PERMS):
        Xp = curveball(X, strata, rng)
        Xp = Xp[ok_rows]
        Op = (Xp.T @ Xp).toarray().astype(np.float64)[fu, fj]
        with np.errstate(divide="ignore", invalid="ignore"):
            zp = np.where(Vr[fu, fj] > 0, (Op - E[fu, fj]) / np.sqrt(Vr[fu, fj]), np.nan)
        gate = Op >= PAIR_MIN_OBS
        null_pos[b] = [((zp >= t) & gate).sum() for t in thresholds]
        null_neg[b] = [((zp <= -t) & gate).sum() for t in thresholds]
        print(f"  permutation {b + 1}/{NULL_PERMS}: {int(null_pos[b][0]):,} pairs at z >= {thresholds[0]:.1f} (observed {int((pairs['z_cmh'] >= thresholds[0]).sum()):,})", flush=True)
    zc = pairs["z_cmh"].to_numpy()
    calib = pd.DataFrame({"z_threshold": thresholds,
                          "observed_positive": [(zc >= t).sum() for t in thresholds], "null_positive_mean": null_pos.mean(axis=0), "null_positive_sd": null_pos.std(axis=0),
                          "observed_negative": [(zc <= -t).sum() for t in thresholds], "null_negative_mean": null_neg.mean(axis=0), "null_negative_sd": null_neg.std(axis=0)})
    calib["empirical_fdr_positive"] = np.where(calib["observed_positive"] > 0, calib["null_positive_mean"] / calib["observed_positive"], np.nan)
    calib["empirical_fdr_negative"] = np.where(calib["observed_negative"] > 0, calib["null_negative_mean"] / calib["observed_negative"], np.nan)
    calib["note"] = ["q<0.01 cutoff" if np.isclose(t, cut) else "" for t in thresholds]
    calib.to_csv(ANALYSIS_DIR / "assoc_pairs_calibration.csv", index=False, float_format="%.4f")
    edges = pairs[edge_mask(pairs)]
    info = {"pairs_tabulated": int(len(pairs)), "pairs_q01_positive": int(((pairs["q_cmh"] < Q_FDR) & (pairs["z_cmh"] > 0)).sum()),
            "pairs_q01_negative": int(((pairs["q_cmh"] < Q_FDR) & (pairs["z_cmh"] < 0)).sum()), "pairs_replicated": int(pairs["replicated"].sum()),
            "edges": int(len(edges)), "strata": int(strata.max() + 1),
            "curveball_fdr_positive_at_q01_cutoff": float(calib.loc[calib["note"] == "q<0.01 cutoff", "empirical_fdr_positive"].iloc[0]) if not np.isnan(cut) else float("nan")}
    print(f"pairs: {len(pairs):,} tabulated (>= {PAIR_MIN_OBS} co-mentions); {info['pairs_q01_positive']:,} positive and {info['pairs_q01_negative']:,} negative at q<{Q_FDR} within creator x week; "
          f"{info['pairs_replicated']:,} replicate in both channel halves; {len(edges):,} edges (replicated, lift >= {LIFT_MIN}, >= {PAIR_MIN_CHANNELS} channels); "
          f"curveball FDR at the q<{Q_FDR} cutoff {info['curveball_fdr_positive_at_q01_cutoff']:.4f}", flush=True)
    return pairs, info


def edge_mask(pairs: pd.DataFrame) -> pd.Series:
    """An edge: positive, q < Q_FDR, replicated in both channel halves, lift >= LIFT_MIN, PAIR_MIN_CHANNELS channels."""
    return (pairs["q_cmh"] < Q_FDR) & (pairs["z_cmh"] > 0) & pairs["replicated"] & (pairs["lift_strat"] >= LIFT_MIN) & (pairs["channels"] >= PAIR_MIN_CHANNELS)


# --------------------------------------------------------------------------- #
# block 3: the network
# --------------------------------------------------------------------------- #
def network_block(pairs: pd.DataFrame, vocab: pd.DataFrame, focus: Sequence[str] = ("epstein", "iran", "war")) -> dict:
    edges = pairs[edge_mask(pairs)].copy()
    edges["weight"] = np.log2(edges["lift_strat"])
    G = nx.Graph()
    for r in edges.itertuples():
        G.add_edge(r.term_a, r.term_b, weight=float(r.weight), lift=float(r.lift_strat), z=float(r.z_cmh), channels=int(r.channels), observed=int(r.observed))
    comms = nx.community.louvain_communities(G, weight="weight", seed=SEED)
    comms = sorted(comms, key=len, reverse=True)
    member = {n: i for i, c in enumerate(comms) for n in c}
    strength = dict(G.degree(weight="weight"))
    degree = dict(G.degree())
    k = min(500, G.number_of_nodes())
    betw = nx.betweenness_centrality(G, k=k, seed=SEED) if G.number_of_nodes() > 0 else {}
    n_titles = vocab.set_index("term")["n_titles"]
    nodes = pd.DataFrame({"term": list(G.nodes())})
    nodes["n_titles"] = nodes["term"].map(n_titles)
    nodes["degree"] = nodes["term"].map(degree)
    nodes["strength"] = nodes["term"].map(strength)
    nodes["betweenness"] = nodes["term"].map(betw)
    nodes["community"] = nodes["term"].map(member)
    nodes = nodes.sort_values(["community", "strength"], ascending=[True, False]).reset_index(drop=True)
    nodes.to_csv(ANALYSIS_DIR / "assoc_nodes.csv", index=False, float_format="%.5f")
    edges[["term_a", "term_b", "observed", "expected_strat", "lift_strat", "z_cmh", "q_cmh", "channels", "npmi", "log_or", "weight"]].to_csv(ANALYSIS_DIR / "assoc_edges.csv", index=False, float_format="%.5f")
    rows = []
    for i, c in enumerate(comms):
        top = sorted(c, key=lambda t: -strength.get(t, 0))[:15]
        rows.append({"community": i, "size": len(c), "top_terms": ", ".join(top), "focus": ", ".join(t for t in focus if t in c)})
    pd.DataFrame(rows).to_csv(ANALYSIS_DIR / "assoc_communities.csv", index=False)
    # do the focus words share a community, across Louvain seeds?
    co = Counter()
    present = [t for t in focus if t in G]
    for s in range(LOUVAIN_SEEDS):
        cs = nx.community.louvain_communities(G, weight="weight", seed=SEED + s)
        m = {n: i for i, c in enumerate(cs) for n in c}
        for a in present:
            for b in present:
                if a < b and m[a] == m[b]:
                    co[(a, b)] += 1
    stability = {f"{a}|{b}": co[(a, b)] / LOUVAIN_SEEDS for a in present for b in present if a < b}
    focus_rows = []
    for t in present:
        nb = sorted(G[t].items(), key=lambda kv: -kv[1]["lift"])[:NEIGHBORS]
        focus_rows.append({"term": t, "community": member[t], "degree": degree[t], "strength": round(strength[t], 3), "betweenness": round(betw.get(t, 0), 5),
                           "neighbors": "; ".join(f"{n} ({d['lift']:.1f}x, {d['channels']} ch)" for n, d in nb)})
    pd.DataFrame(focus_rows).to_csv(ANALYSIS_DIR / "assoc_focus_neighbors.csv", index=False)
    info = {"nodes": G.number_of_nodes(), "edges": G.number_of_edges(), "communities": len(comms), "modularity": float(nx.community.modularity(G, comms, weight="weight")) if G.number_of_edges() else float("nan"),
            "focus_community": {t: member[t] for t in present}, "focus_co_membership_across_seeds": stability}
    print(f"network: {info['nodes']} nodes, {info['edges']} edges, {info['communities']} communities (modularity {info['modularity']:.3f}); focus communities {info['focus_community']}; co-membership {stability}", flush=True)
    return info


# --------------------------------------------------------------------------- #
# block 4: month by month
# --------------------------------------------------------------------------- #
def monthly_block(uniq: pd.DataFrame, X: sp.csr_matrix, vocab: pd.DataFrame, focus: Sequence[str] = ("epstein", "iran", "war")) -> dict:
    terms = vocab["term"].to_numpy()
    V = len(terms)
    months = sorted(uniq["month"].unique())
    neighbor_sets: dict[str, dict[str, set[str]]] = {}
    rows = []
    for m in months:
        rows_m = (uniq["month"] == m).to_numpy()
        Xm = X[rows_m]
        um = uniq[rows_m]
        strata = strata_of(um, ["creator", "week"])
        O, E, Vr = stratified_stats(Xm, strata)
        PC = pair_channels(Xm, pd.factorize(um["creator"])[0])
        iu, ju = np.triu_indices(V, k=1)
        keep = O[iu, ju] >= MONTH_PAIR_MIN_OBS
        iu, ju = iu[keep], ju[keep]
        with np.errstate(divide="ignore", invalid="ignore"):
            z = np.where(Vr[iu, ju] > 0, (O[iu, ju] - E[iu, ju]) / np.sqrt(Vr[iu, ju]), np.nan)
            lift = O[iu, ju] / E[iu, ju]
        p = 2 * stats.norm.sf(np.abs(z))
        q = bh_q(p)
        ch = np.asarray(PC[iu, ju]).ravel()
        ok = (q < Q_FDR) & (z > 0) & (lift >= LIFT_MIN) & (ch >= MONTH_PAIR_MIN_CHANNELS)
        df = pd.DataFrame({"a": iu[ok], "b": ju[ok], "lift": lift[ok], "z": z[ok], "observed": O[iu[ok], ju[ok]], "channels": ch[ok]})
        df["term_a"], df["term_b"] = terms[df["a"]], terms[df["b"]]
        df = drop_phrase_pairs(df, vocab).drop(columns=["term_a", "term_b"])
        both = pd.concat([df, df.rename(columns={"a": "b", "b": "a"})])
        both = both.sort_values(["a", "lift"], ascending=[True, False])
        both["rank"] = both.groupby("a").cumcount() + 1
        top = both[both["rank"] <= NEIGHBORS]
        neighbor_sets[m] = {terms[a]: set(terms[g["b"].to_numpy()]) for a, g in top.groupby("a")}
        for r in top.itertuples():
            rows.append({"month": m, "term": terms[r.a], "rank": int(r.rank), "neighbor": terms[r.b], "lift": float(r.lift), "z": float(r.z), "observed": int(r.observed), "channels": int(r.channels)})
        print(f"monthly {m}: {int(ok.sum()):,} edges of {int(keep.sum()):,} pairs with >= {MONTH_PAIR_MIN_OBS} co-mentions", flush=True)
    nb = pd.DataFrame(rows)
    nb.to_csv(ANALYSIS_DIR / "assoc_monthly_neighbors.csv.gz", index=False, float_format="%.4f")
    # drift: Jaccard of a term's neighbor set between consecutive months
    drift_rows = []
    all_terms = set().union(*[set(d) for d in neighbor_sets.values()])
    for t in all_terms:
        js = []
        for m0, m1 in zip(months, months[1:]):
            s0, s1 = neighbor_sets[m0].get(t), neighbor_sets[m1].get(t)
            if s0 and s1 and len(s0) >= 5 and len(s1) >= 5:
                js.append(len(s0 & s1) / len(s0 | s1))
        present = sum(1 for m in months if neighbor_sets[m].get(t))
        if js:
            drift_rows.append({"term": t, "months_with_neighbors": present, "month_pairs": len(js), "jaccard_mean": float(np.mean(js)), "jaccard_min": float(np.min(js))})
    drift = pd.DataFrame(drift_rows).sort_values(["jaccard_mean", "month_pairs"], ascending=[True, False])
    drift.to_csv(ANALYSIS_DIR / "assoc_drift.csv", index=False, float_format="%.4f")
    focus_rows = []
    for t in focus:
        for m in months:
            s = nb[(nb["month"] == m) & (nb["term"] == t)].sort_values("rank")
            focus_rows.append({"term": t, "month": m, "neighbors": "; ".join(f"{r.neighbor} ({r.lift:.1f}x)" for r in s.itertuples())})
    pd.DataFrame(focus_rows).to_csv(ANALYSIS_DIR / "assoc_focus_monthly.csv", index=False)
    return {"months": len(months), "terms_with_drift": int(len(drift))}


# --------------------------------------------------------------------------- #
# block 5: the case study
# --------------------------------------------------------------------------- #
def case_block(uniq: pd.DataFrame, title_terms: list[set[str]]) -> dict:
    rng = np.random.default_rng(SEED)
    Cm = concept_matrix(title_terms, CONCEPTS)
    Cm["political"] = uniq["political"].to_numpy()
    days = pd.date_range(WINDOW_FROM, WINDOW_TO, freq="D")
    di = pd.Index(days).get_indexer(uniq["day"])
    n_days = len(days)
    N = np.bincount(di, minlength=n_days).astype(float)
    ci, creators = pd.factorize(uniq["creator"])
    active = np.zeros(n_days)
    for d in range(n_days):
        active[d] = len(np.unique(ci[di == d]))
    counts = {c: np.bincount(di, weights=Cm[c].to_numpy().astype(float), minlength=n_days) for c in Cm.columns}
    breadth = {}
    for c in Cm.columns:
        key = di[Cm[c].to_numpy()] * len(creators) + ci[Cm[c].to_numpy()]
        breadth[c] = np.bincount(np.unique(key) // len(creators), minlength=n_days).astype(float)
    Dm = design_matrix(days)
    Y_pool = {c: np.log((counts[c] + 0.5) / (N + 1)) for c in Cm.columns}
    Y_br = {c: np.log((breadth[c] + 0.5) / (active + 1)) for c in Cm.columns}
    R_pool = {c: residualize(Y_pool[c][:, None], Dm).ravel() for c in Cm.columns}
    R_br = {c: residualize(Y_br[c][:, None], Dm).ravel() for c in Cm.columns}
    daily = pd.DataFrame({"day": days.strftime("%Y-%m-%d"), "titles": N, "active_channels": active})
    for c in Cm.columns:
        daily[f"{c}_titles"] = counts[c]
        daily[f"{c}_channels"] = breadth[c]
        daily[f"{c}_share"] = counts[c] / N
        daily[f"{c}_residual_pooled"] = R_pool[c]
        daily[f"{c}_residual_channels"] = R_br[c]
    daily.to_csv(ANALYSIS_DIR / "assoc_case_daily.csv", index=False, float_format="%.6f")
    out: dict = {"days": int(n_days), "titles": int(len(uniq)), "concepts": {c: {"titles": int(Cm[c].sum()), "channels": int(uniq.loc[Cm[c].to_numpy(), "creator"].nunique())} for c in CONCEPTS}}

    # ---- T1 contemporaneous, T2 lagged (prewhitened and circular-shift null), T3 Granger ----
    from statsmodels.tsa.stattools import grangercausalitytests
    from statsmodels.tsa.api import VAR
    ts_rows, ccf_rows = [], []
    for a, b in CASE_PAIRS:
        for kind, R in (("pooled", R_pool), ("channels", R_br)):
            x, y = R[a], R[b]
            r = float(np.corrcoef(x, y)[0, 1])
            rho = float(stats.spearmanr(x, y)[0])
            boot = np.array([np.corrcoef(x[idx], y[idx])[0, 1] for idx in (stationary_bootstrap_index(n_days, rng) for _ in range(BOOT_DRAWS))])
            r_lo, r_hi = float(np.nanpercentile(boot, 2.5)), float(np.nanpercentile(boot, 97.5))
            # sensitivity of the contemporaneous correlation to the trend's flexibility
            sens = {}
            for kn in (3, 6, 10):
                Dk = design_matrix(days, knots=kn)
                Yx, Yy = (Y_pool if kind == "pooled" else Y_br)[a], (Y_pool if kind == "pooled" else Y_br)[b]
                sens[kn] = float(np.corrcoef(residualize(Yx[:, None], Dk).ravel(), residualize(Yy[:, None], Dk).ravel())[0, 1])
            # circular-shift null for the contemporaneous r and for max |ccf| over the lag window
            cc = ccf_series(x, y, LAG_MAX)
            obs_max = float(np.nanmax(np.abs(cc)))
            null_r, null_max = np.empty(NULL_DRAWS), np.empty(NULL_DRAWS)
            for i in range(NULL_DRAWS):
                s = int(rng.integers(21, n_days - 21))
                ys = np.roll(y, s)
                null_r[i] = np.corrcoef(x, ys)[0, 1]
                null_max[i] = np.nanmax(np.abs(ccf_series(x, ys, LAG_MAX)))
            p_shift = float((np.abs(null_r) >= abs(r)).mean())
            p_max = float((null_max >= obs_max).mean())
            xw, yw, p_ar = prewhiten(x, y)
            ccw = ccf_series(xw, yw, LAG_MAX)
            band = 1.96 / math.sqrt(len(xw))
            best = int(np.nanargmax(np.abs(ccw))) - LAG_MAX
            # Granger both ways on the residual series, VAR order by AIC
            try:
                order = VAR(np.column_stack([x, y])).select_order(maxlags=LAG_MAX).aic
                order = int(max(1, order))
                g_ab = grangercausalitytests(np.column_stack([y, x]), maxlag=[order])[order][0]["ssr_ftest"]
                g_ba = grangercausalitytests(np.column_stack([x, y]), maxlag=[order])[order][0]["ssr_ftest"]
                granger = {"order": order, f"{a}_to_{b}_F": float(g_ab[0]), f"{a}_to_{b}_p": float(g_ab[1]), f"{b}_to_{a}_F": float(g_ba[0]), f"{b}_to_{a}_p": float(g_ba[1])}
            except Exception as ex:  # pragma: no cover
                granger = {"error": str(ex)}
            ts_rows.append({"a": a, "b": b, "series": kind, "r": r, "r_boot_lo": r_lo, "r_boot_hi": r_hi, "spearman": rho, "p_shift": p_shift,
                            "r_knots3": sens[3], "r_knots6": sens[6], "r_knots10": sens[10],
                            "max_abs_ccf_raw": obs_max, "p_max_ccf_shift": p_max,
                            "ar_order": p_ar, "prewhitened_best_lag": best, "prewhitened_ccf_at_best": float(ccw[best + LAG_MAX]),
                            "prewhitened_band": band, "prewhitened_ccf_lag0": float(ccw[LAG_MAX]), **granger})
            for k in range(-LAG_MAX, LAG_MAX + 1):
                ccf_rows.append({"a": a, "b": b, "series": kind, "lag_days": k, "ccf_residual": float(cc[k + LAG_MAX]), "ccf_prewhitened": float(ccw[k + LAG_MAX]), "band": band})
    ts = pd.DataFrame(ts_rows)
    ts.to_csv(ANALYSIS_DIR / "assoc_case_timeseries.csv", index=False, float_format="%.4f")
    pd.DataFrame(ccf_rows).to_csv(ANALYSIS_DIR / "assoc_case_ccf.csv", index=False, float_format="%.4f")

    # ---- T4 event study: Epstein around Iran spike days (and the reverse) ----
    ev_rows = []
    dow = days.dayofweek.to_numpy()
    for src, tgt in (("iran", "epstein"), ("war", "epstein"), ("epstein", "iran"), ("iran", "war")):
        x, y = R_pool[src], R_pool[tgt]
        zx = (x - x.mean()) / x.std(ddof=1)
        cand = np.where(zx >= EVENT_Z)[0]
        events = [d for d in cand if zx[d] == zx[max(0, d - 3): d + 4].max()]
        lags = np.arange(-LAG_MAX, LAG_MAX + 1)

        def response(ev):
            resp = np.full(len(lags), np.nan)
            for i, k in enumerate(lags):
                vals = [y[d + k] for d in ev if 0 <= d + k < n_days]
                resp[i] = np.mean(vals) if vals else np.nan
            return resp
        obs = response(events)
        null = np.empty((NULL_DRAWS, len(lags)))
        for i in range(NULL_DRAWS):
            draw = []
            for d in events:
                pool = np.where(dow == dow[d])[0]
                draw.append(int(rng.choice(pool)))
            null[i] = response(draw)
        lo, hi = np.nanpercentile(null, 2.5, axis=0), np.nanpercentile(null, 97.5, axis=0)
        for i, k in enumerate(lags):
            ev_rows.append({"source": src, "target": tgt, "events": len(events), "event_days": ",".join(days[events].strftime("%m-%d")), "lag_days": int(k), "response": float(obs[i]), "null_lo": float(lo[i]), "null_hi": float(hi[i]), "outside": bool(obs[i] < lo[i] or obs[i] > hi[i])})
    pd.DataFrame(ev_rows).to_csv(ANALYSIS_DIR / "assoc_case_events.csv", index=False, float_format="%.4f")

    # ---- T5 day-level negative-binomial regression of Epstein titles on the Iran / war shares with controls ----
    import statsmodels.api as sm
    reg_rows = []
    for target, covs in (("epstein", ["iran", "war"] + CONTROLS), ("epstein", ["iran"] + CONTROLS), ("epstein", ["war"] + CONTROLS), ("epstein_broad", ["iran_broad", "war_broad"] + CONTROLS)):
        y = counts[target]
        Xc = [Dm]
        names = []
        for c in covs:
            s = np.log((counts[c] + 0.5) / (N + 1))
            Xc.append(((s - s.mean()) / s.std(ddof=1))[:, None]); names.append(c)
        # the previous week's Iran share, for a lagged specification
        Xc = np.column_stack(Xc)
        for spec, Xs, nm in (("contemporaneous", Xc, names),):
            try:
                res = sm.NegativeBinomial(y, Xs, exposure=N).fit(disp=0, maxiter=500, cov_type="HAC", cov_kwds={"maxlags": 7})
                params, se, pv = res.params, res.bse, res.pvalues
                fam = "negative_binomial"
            except Exception:
                res = sm.GLM(y, Xs, family=sm.families.Poisson(), exposure=N).fit(cov_type="HAC", cov_kwds={"maxlags": 7})
                params, se, pv = res.params, res.bse, res.pvalues
                fam = "poisson"
            off = Dm.shape[1]
            for i, c in enumerate(nm):
                b, s_ = float(params[off + i]), float(se[off + i])
                reg_rows.append({"target": target, "spec": spec, "model": fam, "covariates": "+".join(nm), "covariate": c, "irr_per_sd": math.exp(b), "irr_lo": math.exp(b - 1.96 * s_), "irr_hi": math.exp(b + 1.96 * s_), "p_hac": float(pv[off + i])})
    # a lagged specification: Epstein today on Iran's mean log-share over the previous 1-7 days, controls contemporaneous
    s_iran = np.log((counts["iran"] + 0.5) / (N + 1))
    lag_mean = np.array([s_iran[max(0, d - 7): d].mean() if d > 0 else s_iran[0] for d in range(n_days)])
    Xl = [Dm, ((lag_mean - lag_mean.mean()) / lag_mean.std(ddof=1))[:, None]]
    nm = ["iran_lag1_7"]
    for c in CONTROLS:
        s = np.log((counts[c] + 0.5) / (N + 1)); Xl.append(((s - s.mean()) / s.std(ddof=1))[:, None]); nm.append(c)
    Xl = np.column_stack(Xl)
    try:
        res = sm.NegativeBinomial(counts["epstein"], Xl, exposure=N).fit(disp=0, maxiter=500, cov_type="HAC", cov_kwds={"maxlags": 7}); fam = "negative_binomial"
    except Exception:
        res = sm.GLM(counts["epstein"], Xl, family=sm.families.Poisson(), exposure=N).fit(cov_type="HAC", cov_kwds={"maxlags": 7}); fam = "poisson"
    off = Dm.shape[1]
    for i, c in enumerate(nm):
        b, s_ = float(res.params[off + i]), float(res.bse[off + i])
        reg_rows.append({"target": "epstein", "spec": "lagged", "model": fam, "covariates": "+".join(nm), "covariate": c, "irr_per_sd": math.exp(b), "irr_lo": math.exp(b - 1.96 * s_), "irr_hi": math.exp(b + 1.96 * s_), "p_hac": float(res.pvalues[off + i])})
    pd.DataFrame(reg_rows).to_csv(ANALYSIS_DIR / "assoc_case_regression.csv", index=False, float_format="%.4f")

    # ---- T6 title level: CMH within creator x week and creator x day; naive for comparison; by group; leave one organization out ----
    strata_w = strata_of(uniq, ["creator", "week"])
    strata_d = strata_of(uniq, ["creator", "published"])
    strata_none = np.zeros(len(uniq), dtype=int)
    pair_rows, chan_rows = [], []
    orgs = uniq["org"].to_numpy()
    groups = uniq["group"].to_numpy()
    for a, b in CASE_PAIRS:
        x, y = Cm[a].to_numpy(), Cm[b].to_numpy()
        row = {"a": a, "b": b, "co_mentions": int((x & y).sum()), "channels_co_mentioning": int(uniq.loc[x & y, "creator"].nunique())}
        for name, st in (("naive", strata_none), ("creator_week", strata_w), ("creator_day", strata_d)):
            r = cmh_pair(x, y, st)
            for k, v in r.items():
                row[f"{name}_{k}"] = v
        # by channel group (creator x week strata within the group), and the heterogeneity of the log odds ratios across groups
        thetas, ses = [], []
        for g in ("left", "neutral", "right"):
            m = groups == g
            r = cmh_pair(x[m], y[m], pd.factorize(strata_w[m])[0]) if m.sum() else {}
            row[f"group_{g}_or_mh"] = r.get("or_mh", float("nan")); row[f"group_{g}_or_lo"] = r.get("or_lo", float("nan")); row[f"group_{g}_or_hi"] = r.get("or_hi", float("nan"))
            row[f"group_{g}_z"] = r.get("z", float("nan")); row[f"group_{g}_co_mentions"] = r.get("observed", float("nan"))
            if r and not math.isnan(r.get("log_or_se", float("nan"))) and r["or_mh"] > 0:
                thetas.append(math.log(r["or_mh"])); ses.append(r["log_or_se"])
        if len(thetas) >= 2:
            th, se = np.array(thetas), np.array(ses)
            w = 1 / se ** 2
            tbar = (w * th).sum() / w.sum()
            Qh = float((w * (th - tbar) ** 2).sum())
            row["group_heterogeneity_q"] = Qh; row["group_heterogeneity_p"] = float(stats.chi2.sf(Qh, len(th) - 1))
        # leave one organization out
        ors, zs = {}, {}
        for o in np.unique(orgs):
            m = orgs != o
            r = cmh_pair(x[m], y[m], pd.factorize(strata_w[m])[0])
            ors[o] = r["or_mh"]; zs[o] = r["z"]
        ser = pd.Series(ors).dropna()
        if len(ser):
            row["loo_or_min"] = float(ser.min()); row["loo_or_min_org"] = str(ser.idxmin()); row["loo_or_max"] = float(ser.max()); row["loo_or_max_org"] = str(ser.idxmax())
            row["loo_z_min"] = float(min(zs.values())); row["loo_z_max"] = float(max(zs.values()))
        # per channel: aggregated 2 x 2 with Haldane's correction, channels with >= 5 titles of each, then DerSimonian-Laird
        th, se_, keep_rows = [], [], []
        for c in np.unique(ci):
            m = ci == c
            xa, ya = x[m], y[m]
            if xa.sum() < 5 or ya.sum() < 5:
                continue
            aa = float((xa & ya).sum()); bb = float(xa.sum() - aa); cc = float(ya.sum() - aa); dd = float(m.sum() - xa.sum() - ya.sum() + aa)
            lo, s = haldane_log_or(aa, bb, cc, dd)
            th.append(lo); se_.append(s)
            keep_rows.append({"a": a, "b": b, "creator": creators[c], "group": groups[m][0], "titles": int(m.sum()), "n_a": int(xa.sum()), "n_b": int(ya.sum()), "both": int(aa), "log_or": lo, "se": s})
        chan_rows.extend(keep_rows)
        dl = dersimonian_laird(np.array(th), np.array(se_))
        row.update({f"meta_{k}": v for k, v in dl.items()})
        if th:
            th_ = np.array(th); se_ = np.array(se_)
            row["meta_share_or_gt1"] = float((th_ > 0).mean()); row["meta_share_ci_excludes1_positive"] = float(((th_ - 1.96 * se_) > 0).mean()); row["meta_share_ci_excludes1_negative"] = float(((th_ + 1.96 * se_) < 0).mean())
        pair_rows.append(row)
    pairs = pd.DataFrame(pair_rows)
    pairs.to_csv(ANALYSIS_DIR / "assoc_case_pairs.csv", index=False, float_format="%.4f")
    pd.DataFrame(chan_rows).to_csv(ANALYSIS_DIR / "assoc_case_channels.csv", index=False, float_format="%.4f")
    # the co-mention titles themselves, for reading
    x, y = Cm["epstein"].to_numpy(), Cm["iran"].to_numpy()
    both = uniq.loc[x & y, ["published", "creator", "group", "title_raw", "view_count", "url"]].sort_values("published")
    both.to_csv(ANALYSIS_DIR / "assoc_case_epstein_iran_titles.csv", index=False)
    x, y = Cm["epstein"].to_numpy(), Cm["war"].to_numpy()
    uniq.loc[x & y, ["published", "creator", "group", "title_raw", "view_count", "url"]].sort_values("published").to_csv(ANALYSIS_DIR / "assoc_case_epstein_war_titles.csv", index=False)
    out["timeseries"] = ts.to_dict(orient="records")
    out["title_level"] = pairs.to_dict(orient="records")
    out["regression"] = reg_rows
    with open(ANALYSIS_DIR / "assoc_case_study.json", "w", encoding="utf-8") as f:
        json.dump(out, f, indent=1, default=float)
    print("case study written", flush=True)
    return {"case_pairs": len(CASE_PAIRS)}


# --------------------------------------------------------------------------- #
def run(info: dict, case_only: bool = False) -> None:
    uniq = build_corpus()
    title_terms, vocab, X, index = build_terms(uniq)
    vocab.to_csv(ANALYSIS_DIR / "assoc_vocab.csv", index=False)
    info.update({"titles": int(len(uniq)), "vocab": int(len(vocab)), "thresholds": {"min_titles": MIN_TITLES, "min_channels": MIN_CHANNELS, "series_min_titles": SERIES_MIN_TITLES,
                 "pair_min_obs": PAIR_MIN_OBS, "pair_min_channels": PAIR_MIN_CHANNELS, "q_fdr": Q_FDR, "lift_min": LIFT_MIN, "lag_max": LAG_MAX, "spline_knots": SPLINE_KNOTS}})
    if not case_only:
        info["temporal"] = temporal_block(uniq, X, vocab)
        pairs, pinfo = pairs_block(uniq, X, vocab)
        info["pairs"] = pinfo
        info["network"] = network_block(pairs, vocab)
        info["monthly"] = monthly_block(uniq, X, vocab)
    info["case"] = case_block(uniq, title_terms)
    with open(ANALYSIS_DIR / "assoc_summary.json", "w", encoding="utf-8") as f:
        json.dump(info, f, indent=1, default=float)


def main(argv: Optional[Sequence[str]] = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--case-only", action="store_true", help="run the case study alone")
    a = ap.parse_args(argv)
    with stage_timer("associations") as info:
        run(info, case_only=a.case_only)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
