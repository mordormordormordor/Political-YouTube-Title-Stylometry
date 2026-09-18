"""Stage 6b - Zipf's law and views over time, for document 7.

Three ways of cutting the corpus run through the whole stage:
    channel group   left / neutral / right channels (each channel's leaning group, Stage 0d)
    title label     left / neither / right titles (the judge's label of the sampled titles)
    caps style      ALL CAPS / selective CAPS / Title Case / Sentence case / mixed / short
                    (textstats.caps_style, written per title by the profiles stage)

Zipf's law for words. For every system (the corpus, each channel group, each title
label, each caps style) the rank-frequency table of its tokens and the OLS exponent of
log frequency on log rank over the top 100 / 1,000 / 5,000 types (prepare.zipf_slope,
the same tokeniser as the Stage 0 Zipf check, stopwords kept: Zipf's law is about the
whole vocabulary). Systems differ in size and the exponent depends on size, so a
size-matched exponent is reported beside it: SIZE_MATCH_N titles drawn SIZE_MATCH_REPEATS
times from the system, exponent over the top 200 ranks, averaged. Creator-level Zipf
exponents (Stage 0 check, Stage 2 subsampled Zipf / Heaps) are averaged per channel
group.

Zipf's law for views. Within a channel, videos ranked by views (hits.views_zipf_slope,
Stage 5c) give a rank-size slope; those slopes, the Gini and the top-10 % share are
summarised per channel group and per channel's dominant caps style.

Views over time. Views are a fetch-time snapshot (2026-09-14), so a January video has
had eight months to collect them and a September one two weeks: the raw curve falls
with publication month for everyone. Two measures per month:
    median views          over the videos of the group (and the median over channels of
                          each channel's median, so four Indian news channels cannot
                          carry a group)
    relative log views    mean over titles of log(1 + views) minus the mean log(1 + views)
                          of the same channel's videos in the same month: how a title
                          did against its own channel's average that month (0 = the
                          channel's average title; +0.1 = about 10 % more views); the
                          measure that makes caps styles and title labels comparable

Edited uploads and unique titles throughout. The word systems and the caps-style shares use
the creator-balanced subset on both platforms; the views block is YouTube only (Rumble has no
view counts); the views rank-size slopes, Gini and top-10 % share come from the hits stage,
which counts every video (repeats included).

Outputs (data/titles/analysis/):
    zipf_words.csv               one row per system: tokens, types, Zipf exponents, top words
    zipf_words_curves.csv        rank-frequency curves (ranks 1..5000) per system
    zipf_by_group.csv            creator-level Zipf / Heaps and the views rank-size slopes,
                                 Gini and top-10 % share, per channel group and per dominant
                                 caps style (n_creators_1500 = channels with enough tokens
                                 for the subsampled Zipf / Heaps exponents)
    views_by_month.csv           per grouping x group x month (and "all"): n videos, median
                                 views, creator-median views, relative log views
    caps_style_by_group.csv      caps-style shares per channel group and per title label
    label_by_caps_style.csv      title labels x caps style: share of each label within the
                                 style, and relative log views of the labelled titles per
                                 label x style

CLI:
    python -m pipeline_titles.zipf_views
"""

from __future__ import annotations

import argparse
from collections import Counter
from typing import Optional, Sequence

import numpy as np
import pandas as pd

from pipeline_titles.common import (
    ANALYSIS_DIR, CAPS_STYLE_TITLE, GROUPS, LOW_N, MONTHS, SEED, load_creators, load_prepared, stage_timer,
)
from pipeline_titles.leaning import LABELS as TITLE_LABELS, LABELS_CSV as LEANING_LABELS
from pipeline_titles.prepare import tokens, zipf_slope
from pipeline_titles.textstats import CAPS_STYLES

SIZE_MATCH_N = 2000
SIZE_MATCH_REPEATS = 20
SIZE_MATCH_RANKS = 200
CURVE_RANKS = 5000
MIN_SYSTEM_TITLES = 200


# --------------------------------------------------------------------------- #
# Pure helpers (unit-tested in tests/test_titles_zipf_views.py)
# --------------------------------------------------------------------------- #
def token_counter(titles: Sequence[str]) -> Counter:
    c: Counter = Counter()
    for t in titles:
        c.update(tokens(t))
    return c


def size_matched_zipf(titles: Sequence[str], n: int = SIZE_MATCH_N, repeats: int = SIZE_MATCH_REPEATS,
                      max_rank: int = SIZE_MATCH_RANKS, seed: int = SEED) -> tuple[float, float]:
    """Mean and sd of the Zipf exponent over `repeats` random draws of `n` titles
    (top `max_rank` ranks). NaN when the system holds fewer than `n` titles."""
    titles = list(titles)
    if len(titles) < n:
        return float("nan"), float("nan")
    rng = np.random.RandomState(seed)
    vals = []
    for _ in range(repeats):
        idx = rng.choice(len(titles), size=n, replace=False)
        expo, _ = zipf_slope(token_counter([titles[i] for i in idx]), max_rank)
        vals.append(expo)
    return float(np.mean(vals)), float(np.std(vals))


def zipf_fit_r2(counter: Counter, max_rank: int = 1000) -> float:
    """R2 of the straight line through log frequency vs log rank (how Zipf-like the head is)."""
    freqs = np.array(sorted(counter.values(), reverse=True)[:max_rank], dtype=float)
    if len(freqs) < 10:
        return float("nan")
    x, y = np.log(np.arange(1, len(freqs) + 1)), np.log(freqs)
    slope, intercept = np.polyfit(x, y, 1)
    ss_res = float(((y - (slope * x + intercept)) ** 2).sum()); ss_tot = float(((y - y.mean()) ** 2).sum())
    return float(1 - ss_res / ss_tot) if ss_tot > 0 else float("nan")


def relative_log_views(df: pd.DataFrame, view_col: str = "view_count") -> pd.Series:
    """log(1 + views) minus the mean log(1 + views) of the same creator's videos in the
    same month (the within-channel, within-month baseline; averages to 0 over a channel-month)."""
    lv = np.log1p(df[view_col].astype(float))
    base = lv.groupby([df["creator"], df["month"]]).transform("mean")
    return lv - base


def monthly_views_table(df: pd.DataFrame, grouping: str, col: str, order: Sequence[str]) -> pd.DataFrame:
    """Per group x month (plus month = 'all'): n videos, n creators, median views, the
    median over creators of each creator's median views, mean relative log views."""
    rows = []
    for g in order:
        sub = df[df[col] == g]
        if not len(sub):
            continue
        for m in list(MONTHS) + ["all"]:
            s = sub if m == "all" else sub[sub["month"] == m]
            if len(s) < 20:
                continue
            per_creator = s.groupby("creator")["view_count"].median()
            rows.append({"grouping": grouping, "group": g, "month": m, "n_videos": int(len(s)), "n_creators": int(s["creator"].nunique()),
                         "median_views": float(s["view_count"].median()), "creator_median_views": float(per_creator.median()),
                         "mean_log_views": round(float(np.log1p(s["view_count"]).mean()), 4),
                         "relative_log_views": round(float(s["rel_log_views"].mean()), 4),
                         "relative_log_views_se": round(float(s["rel_log_views"].std() / np.sqrt(len(s))), 4)})
    return pd.DataFrame(rows)


# --------------------------------------------------------------------------- #
def run(info: dict) -> None:
    prepared = load_prepared()
    creators = load_creators()[["creator", "group", "organisation", "clipper"]]
    caps = pd.read_parquet(CAPS_STYLE_TITLE)
    labels = pd.read_csv(LEANING_LABELS)
    judge = next((c for c in labels.columns if c.startswith("label_") and "claude_code" in c), next(c for c in labels.columns if c.startswith("label_")))
    labels = labels[["row_id", judge]].rename(columns={judge: "title_label"})
    labels["title_label"] = labels["title_label"].astype(str).str.split("|").str[0]
    labels = labels[labels["title_label"].isin(TITLE_LABELS)]

    uniq = prepared[(~prepared["is_dup"]) & (prepared["genre"] == "videos")].merge(creators, on="creator", how="left") \
        .merge(caps, on="row_id", how="left").merge(labels, on="row_id", how="left")
    uniq["caps_style"] = uniq["caps_style"].fillna("short_other")
    bal = uniq[uniq["in_balanced"] & ~uniq["low_n"]]

    # ---- Zipf's law for words ----
    systems: list[tuple[str, str, pd.Series]] = [("corpus", "all edited uploads (balanced)", bal["title_norm"])]
    systems += [("channel_group", g, bal.loc[bal["group"] == g, "title_norm"]) for g in GROUPS]
    lab = uniq[uniq["title_label"].notna()]
    systems += [("title_label", l, lab.loc[lab["title_label"] == l, "title_norm"]) for l in TITLE_LABELS]
    systems += [("caps_style", cs, bal.loc[bal["caps_style"] == cs, "title_norm"]) for cs in CAPS_STYLES]
    zrows, crows = [], []
    for kind, name, titles in systems:
        titles = titles.tolist()
        if len(titles) < MIN_SYSTEM_TITLES:
            continue
        ctr = token_counter(titles)
        rec = {"grouping": kind, "system": name, "n_titles": len(titles), "n_tokens": int(sum(ctr.values())), "n_types": len(ctr),
               "tokens_per_title": round(sum(ctr.values()) / len(titles), 2), "type_token_ratio": round(len(ctr) / max(sum(ctr.values()), 1), 4)}
        for mr in (100, 1000, 5000):
            expo, used = zipf_slope(ctr, mr)
            rec[f"zipf_top{mr}"] = round(expo, 4); rec[f"ranks_used_top{mr}"] = used
        rec["zipf_r2_top1000"] = round(zipf_fit_r2(ctr, 1000), 4)
        m, sd = size_matched_zipf(titles)
        rec["zipf_size_matched"] = round(m, 4) if m == m else np.nan; rec["zipf_size_matched_sd"] = round(sd, 4) if sd == sd else np.nan
        top = ctr.most_common(10)
        rec["top1_share"] = round(top[0][1] / max(sum(ctr.values()), 1), 4) if top else np.nan
        rec["top_10"] = " ".join(w for w, _ in top)
        zrows.append(rec)
        total = sum(ctr.values())
        for rank, (w, f) in enumerate(ctr.most_common(CURVE_RANKS), start=1):
            crows.append({"grouping": kind, "system": name, "rank": rank, "word": w, "count": f, "share": round(f / total, 6)})
    pd.DataFrame(zrows).to_csv(ANALYSIS_DIR / "zipf_words.csv", index=False)
    pd.DataFrame(crows).to_csv(ANALYSIS_DIR / "zipf_words_curves.csv.gz", index=False)
    info["zipf_systems"] = len(zrows)

    # ---- creator-level Zipf / Heaps and the views rank-size slopes, per group and per dominant caps style ----
    zc = pd.read_csv(ANALYSIS_DIR / "zipf_check_creators.csv")
    zc = zc[(zc["text"] == "normalised") & (zc["genre"] == "videos")][["creator", "zipf_exponent_top200", "top1_share"]]
    fc = pd.read_csv(ANALYSIS_DIR / "features_creator.csv")
    fc = fc[fc["genre"] == "videos"][["creator", "low_n", "zipf_1500", "heaps_beta_1500"]]
    hc = pd.read_csv(ANALYSIS_DIR / "hit_concentration.csv")
    hc = hc[hc["genre"] == "videos"][["creator", "n_videos", "gini", "top10_share", "zipf_views_all", "zipf_views_head", "powerlaw_like"]]
    cp = pd.read_csv(ANALYSIS_DIR / "caps_profile.csv")
    cp = cp[cp["genre"] == "videos"].copy()
    cp["dominant_caps_style"] = cp[CAPS_STYLES].idxmax(axis=1)
    per = creators.merge(fc, on="creator", how="left").merge(zc, on="creator", how="left").merge(hc, on="creator", how="left") \
        .merge(cp[["creator", "dominant_caps_style", "caps_any"]], on="creator", how="left")
    per = per[per["low_n"] == False]  # noqa: E712  (ranked creators with edited uploads)
    grows = []
    for grouping, col, order in (("channel_group", "group", list(GROUPS)), ("dominant_caps_style", "dominant_caps_style", CAPS_STYLES)):
        for g in order:
            sub = per[per[col] == g]
            if len(sub) < 3:
                continue
            hv = sub.dropna(subset=["zipf_views_all"])
            grows.append({"grouping": grouping, "group": g, "n_creators": int(len(sub)),
                          "zipf_words_top200_mean": round(float(sub["zipf_exponent_top200"].mean()), 4), "zipf_words_top200_median": round(float(sub["zipf_exponent_top200"].median()), 4),
                          "n_creators_1500": int(sub["zipf_1500"].notna().sum()),
                          "zipf_words_1500_mean": round(float(sub["zipf_1500"].mean()), 4), "heaps_beta_1500_mean": round(float(sub["heaps_beta_1500"].mean()), 4),
                          "top1_word_share_mean": round(float(sub["top1_share"].mean()), 4),
                          "n_creators_with_views": int(len(hv)), "zipf_views_all_median": round(float(hv["zipf_views_all"].median()), 4) if len(hv) else np.nan,
                          "zipf_views_head_median": round(float(hv["zipf_views_head"].median()), 4) if len(hv) else np.nan,
                          "gini_median": round(float(hv["gini"].median()), 4) if len(hv) else np.nan,
                          "top10_share_median": round(float(hv["top10_share"].median()), 4) if len(hv) else np.nan,
                          "powerlaw_like_share": round(float(hv["powerlaw_like"].astype(bool).mean()), 4) if len(hv) else np.nan,
                          "caps_any_mean": round(float(sub["caps_any"].mean()), 4)})
    pd.DataFrame(grows).to_csv(ANALYSIS_DIR / "zipf_by_group.csv", index=False)

    # ---- views over time ----
    v = uniq[uniq["has_views"] & (uniq["platform"] == "youtube") & uniq["view_count"].notna()].copy()
    v["rel_log_views"] = relative_log_views(v)
    tabs = [monthly_views_table(v[~v["low_n"]], "channel_group", "group", list(GROUPS)),
            monthly_views_table(v[v["title_label"].notna()], "title_label", "title_label", list(TITLE_LABELS)),
            monthly_views_table(v, "caps_style", "caps_style", CAPS_STYLES)]
    allm = v[~v["low_n"]].groupby("month").agg(n_videos=("row_id", "size"), n_creators=("creator", "nunique"), median_views=("view_count", "median")).reset_index()
    allm["creator_median_views"] = [float(v[(~v["low_n"]) & (v["month"] == m)].groupby("creator")["view_count"].median().median()) for m in allm["month"]]
    allm["mean_log_views"] = [round(float(np.log1p(v.loc[(~v["low_n"]) & (v["month"] == m), "view_count"]).mean()), 4) for m in allm["month"]]
    allm.insert(0, "grouping", "all"); allm.insert(1, "group", "all channels")
    pd.concat(tabs + [allm], ignore_index=True).to_csv(ANALYSIS_DIR / "views_by_month.csv", index=False)
    info["views_rows"] = int(len(v))

    # ---- caps style shares per channel group and per title label ----
    srows = []
    for grouping, frame, col, order in (("channel_group", bal, "group", list(GROUPS)), ("title_label", lab, "title_label", list(TITLE_LABELS))):
        for g in order:
            sub = frame[frame[col] == g]
            if not len(sub):
                continue
            shares = sub["caps_style"].value_counts(normalize=True).reindex(CAPS_STYLES, fill_value=0.0)
            srows.append({"grouping": grouping, "group": g, "n_titles": int(len(sub)), **{cs: round(float(shares[cs]), 4) for cs in CAPS_STYLES},
                          "caps_any": round(float(shares["all_caps"] + shares["selective_caps"]), 4)})
    pd.DataFrame(srows).to_csv(ANALYSIS_DIR / "caps_style_by_group.csv", index=False)

    # ---- title label x caps style: label shares within each style, and relative views per cell ----
    lv = v[v["title_label"].notna()]
    lrows = []
    for cs in CAPS_STYLES:
        sub = lab[lab["caps_style"] == cs]
        if len(sub) < 30:
            continue
        shares = sub["title_label"].value_counts(normalize=True).reindex(TITLE_LABELS, fill_value=0.0)
        rec = {"caps_style": cs, "n_titles": int(len(sub)), **{f"share_{l}": round(float(shares[l]), 4) for l in TITLE_LABELS}}
        for l in TITLE_LABELS:
            cell = lv[(lv["caps_style"] == cs) & (lv["title_label"] == l)]
            rec[f"relative_log_views_{l}"] = round(float(cell["rel_log_views"].mean()), 4) if len(cell) >= 20 else np.nan
            rec[f"n_{l}"] = int(len(cell))
        lrows.append(rec)
    pd.DataFrame(lrows).to_csv(ANALYSIS_DIR / "label_by_caps_style.csv", index=False)
    z = pd.DataFrame(zrows)
    print(z[["grouping", "system", "n_titles", "zipf_top1000", "zipf_size_matched"]].to_string(index=False))


def main(argv: Optional[Sequence[str]] = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.parse_args(argv)
    with stage_timer("stage6b_zipf_views") as info:
        run(info)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
