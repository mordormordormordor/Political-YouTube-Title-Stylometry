"""Stage 5a - monthly drift, January to September 2026.

Reads dimensions_monthly.csv (Stage 2 cell scores), formats.parquet (Stage 3),
topics.csv, titles_prepared.parquet and creators.csv (with the channel groups). Months
are the only safe time
unit (YouTube listing dates are month-accurate); September is 1-14 only and is
flagged partial_month = True everywhere - it is shown but its volume is never
compared with a full month.

Outputs (data/titles/analysis/):
    drift_group_monthly.csv    channel group x genre x month: mean of creator cell scores
                               (raw and topic-controlled), hook shares, n_creators
    drift_top30_monthly.csv    the 30 largest creators (unique titles): the same per
                               creator x genre x month (sparkline data for the cards)
    drift_creator_monthly.csv  every creator x genre x month (cards)
    topic_change_monthly.csv   month-to-month Jensen-Shannon distance between a
                               creator's consecutive monthly topic mixes
    topic_change_group_monthly.csv   the same per channel group x genre x month (mean, median)
    drift_trends.csv           per channel group x genre and per top-30 creator x genre: the
                               Spearman trend of each controlled score and hook share
                               over the nine months

CLI:
    python -m pipeline_titles.timeline
"""

from __future__ import annotations

import argparse
from typing import Optional, Sequence

import numpy as np
import pandas as pd

from pipeline_titles.common import ANALYSIS_DIR, FORMATS_PARQUET, LOW_N, MONTHS, PARTIAL_MONTH, TOPICS_CSV, load_creators, load_prepared, stage_timer

MIN_CELL = 15
HOOKS = ["curiosity_gap", "outrage", "humor"]
FORMATS = ["question", "breaking_live", "episode_show", "interview_guest", "reaction", "confrontation", "listicle", "howto_explainer"]


def run(info: dict) -> None:
    from scipy.spatial.distance import jensenshannon
    from scipy.stats import spearmanr
    creators = load_creators()[["creator", "group", "organisation", "clipper"]]
    cells = pd.read_csv(ANALYSIS_DIR / "dimensions_monthly.csv.gz")
    fcols = [c for c in cells.columns if c.startswith("F") and c[1:].isdigit()]
    cells = cells[cells["n_titles"] >= MIN_CELL].drop(columns=["group", "organisation", "clipper"], errors="ignore").merge(creators, on="creator", how="left")
    prepared = load_prepared()[["row_id", "creator", "genre", "month", "is_dup", "low_n", "n_unique"]]
    fm = pd.read_parquet(FORMATS_PARQUET, columns=["row_id"] + HOOKS + FORMATS)
    u = prepared[~prepared["is_dup"]].merge(fm, on="row_id")
    hooks_m = u.groupby(["creator", "genre", "month"]).agg(n=("row_id", "size"), **{h: (h, "mean") for h in HOOKS + FORMATS}).reset_index()
    cm = cells.merge(hooks_m.drop(columns=["n"]), on=["creator", "genre", "month"], how="left")
    cm["partial_month"] = cm["month"] == PARTIAL_MONTH
    cm["low_n"] = cm["creator"].map(prepared.groupby("creator")["low_n"].first())
    score_cols = [f + "_controlled" for f in fcols] + fcols + HOOKS + FORMATS
    cm.to_csv(ANALYSIS_DIR / "drift_creator_monthly.csv.gz", index=False)

    # channel group x genre x month: mean of creator cells (non-low-n)
    ok = cm[~cm["low_n"].fillna(False).astype(bool)]
    group_m = ok.groupby(["group", "genre", "month"]).agg(n_creators=("creator", "nunique"), n_titles=("n_titles", "sum"),
                                                        **{c: (c, "mean") for c in score_cols}).reset_index()
    group_m["partial_month"] = group_m["month"] == PARTIAL_MONTH
    corpus_m = ok.groupby(["genre", "month"]).agg(n_creators=("creator", "nunique"), n_titles=("n_titles", "sum"), **{c: (c, "mean") for c in score_cols}).reset_index()
    corpus_m.insert(0, "group", "ALL (mean of creators)")
    corpus_m["partial_month"] = corpus_m["month"] == PARTIAL_MONTH
    pd.concat([group_m, corpus_m], ignore_index=True).to_csv(ANALYSIS_DIR / "drift_group_monthly.csv", index=False)

    # top 30 creators by unique titles (across genres)
    top30 = prepared[~prepared["is_dup"]].groupby("creator").size().nlargest(30).index.tolist()
    cm[cm["creator"].isin(top30)].to_csv(ANALYSIS_DIR / "drift_top30_monthly.csv", index=False)

    # month-to-month topic change (JS distance between consecutive months with >= MIN_CELL titles)
    topics = pd.read_csv(TOPICS_CSV, usecols=["row_id", "topic_id"])
    ut = u.merge(topics, on="row_id")
    rows = []
    for (c, g), grp in ut.groupby(["creator", "genre"]):
        mats = grp.groupby(["month", "topic_id"]).size().unstack(fill_value=0)
        n_month = mats.sum(axis=1)
        months = [m for m in MONTHS if m in mats.index and n_month[m] >= MIN_CELL]
        for a, b in zip(months, months[1:]):
            if MONTHS.index(b) - MONTHS.index(a) != 1:
                continue
            pa, pb = mats.loc[a].to_numpy(float), mats.loc[b].to_numpy(float)
            rows.append({"creator": c, "genre": g, "month_from": a, "month_to": b, "n_from": int(n_month[a]), "n_to": int(n_month[b]),
                         "js_distance": round(float(jensenshannon(pa / pa.sum(), pb / pb.sum(), base=2)), 4)})
    tc = pd.DataFrame(rows).merge(creators, on="creator", how="left")
    tc["partial_month"] = tc["month_to"] == PARTIAL_MONTH
    tc["low_n"] = tc["creator"].map(prepared.groupby("creator")["low_n"].first())
    tc.to_csv(ANALYSIS_DIR / "topic_change_monthly.csv", index=False)
    tcl = tc[~tc["low_n"].astype(bool)].groupby(["group", "genre", "month_to"]).agg(n_creators=("creator", "nunique"), mean_js=("js_distance", "mean"), median_js=("js_distance", "median")).reset_index()
    tcl.to_csv(ANALYSIS_DIR / "topic_change_group_monthly.csv", index=False)

    # trends: Spearman of month index vs value
    trend_rows = []
    for (group, g), grp in group_m.groupby(["group", "genre"]):
        if len(grp) < 5:
            continue
        x = grp["month"].map(MONTHS.index)
        for c in [f + "_controlled" for f in fcols] + HOOKS:
            r, p = spearmanr(x, grp[c])
            trend_rows.append({"level": "group", "group": group, "genre": g, "measure": c, "n_months": len(grp), "spearman_trend": round(float(r), 3), "p": round(float(p), 4),
                               "first_month_value": round(float(grp.iloc[0][c]), 4), "last_full_month_value": round(float(grp[grp["month"] != PARTIAL_MONTH].iloc[-1][c]), 4)})
    for (c_, g), grp in cm[cm["creator"].isin(top30)].groupby(["creator", "genre"]):
        if len(grp) < 5:
            continue
        x = grp["month"].map(MONTHS.index)
        for c in [f + "_controlled" for f in fcols] + HOOKS:
            r, p = spearmanr(x, grp[c])
            trend_rows.append({"level": "creator", "group": c_, "genre": g, "measure": c, "n_months": len(grp), "spearman_trend": round(float(r), 3), "p": round(float(p), 4),
                               "first_month_value": round(float(grp.iloc[0][c]), 4), "last_full_month_value": round(float(grp[grp["month"] != PARTIAL_MONTH].iloc[-1][c]), 4) if (grp["month"] != PARTIAL_MONTH).any() else np.nan})
    pd.DataFrame(trend_rows).to_csv(ANALYSIS_DIR / "drift_trends.csv", index=False)
    info.update(group_month_rows=len(group_m), top30=len(top30), topic_change_rows=len(tc))


def main(argv: Optional[Sequence[str]] = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.parse_args(argv)
    with stage_timer("stage5a_timeline") as info:
        run(info)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
