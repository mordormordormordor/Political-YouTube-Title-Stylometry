"""Stage 5b - does title style predict views, within creator?

For every creator x genre with >= 100 YouTube titles that carry a view count, an
OLS regression of log(1 + views) on the title's factor scores (Stage 2, raw
title-level), its hook labels (Stage 3), its length in tokens, with publish-month
dummies and topic dummies (topics with >= 5 titles for that creator, the rest
pooled) as controls; HC3 standard errors. Predictors are z-scored within the
creator, so a coefficient is the change in log views per one within-creator
standard deviation. Views are a snapshot taken at fetch time (2026-09-14), which
favors older videos; the month dummies absorb that within a creator, but
coefficients still describe views-to-date, not lifetime views.

Subscriber normalization: log(views / subscribers) = log(views) - log(subscribers),
a constant within creator, so it leaves every slope unchanged; the standardized
coefficients are therefore already comparable across creators, and subscriber
count is reported beside them.

Rumble rows have no view count and are excluded here.

Outputs (data/titles/analysis/):
    engagement_coefficients.csv   creator x genre x predictor: coefficient, HC3 SE, p, n, R2
    engagement_summary.csv        across creators (per genre, and per channel group): median,
                                  IQR, share positive, share significant (+/-), n_creators
    engagement_model.json         specification

CLI:
    python -m pipeline_titles.engagement
"""

from __future__ import annotations

import argparse
import json
import warnings
from typing import Optional, Sequence

import numpy as np
import pandas as pd

from pipeline_titles.common import (
    ANALYSIS_DIR, DIMENSIONS_TITLE, FEATURES_TITLE, FORMATS_PARQUET, MIN_ENGAGEMENT_N, TOPICS_CSV, load_creators, load_prepared, stage_timer,
)

HOOKS = ["curiosity_gap", "outrage", "humor"]
MIN_TOPIC_N = 5


def fit_creator(df: pd.DataFrame, predictors: list[str]) -> Optional[dict]:
    """OLS with HC3 for one creator x genre; returns {predictor: (coef, se, p)} plus fit stats."""
    import statsmodels.api as sm
    y = np.log1p(df["view_count"].to_numpy(float))
    X = df[predictors].astype(float)
    sd = X.std()
    keep = [c for c in predictors if sd[c] > 0]
    X = (X[keep] - X[keep].mean()) / X[keep].std()
    month_d = pd.get_dummies(df["month"], prefix="m", drop_first=True, dtype=float)
    topic_counts = df["topic_id"].value_counts()
    tp = df["topic_id"].where(df["topic_id"].isin(topic_counts[topic_counts >= MIN_TOPIC_N].index), other=-1)
    topic_d = pd.get_dummies(tp, prefix="t", drop_first=True, dtype=float)
    Xf = pd.concat([X, month_d, topic_d], axis=1)
    Xf = sm.add_constant(Xf, has_constant="add")
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        res = sm.OLS(y, Xf).fit(cov_type="HC3")
    out = {"n": int(len(df)), "r2": float(res.rsquared), "r2_adj": float(res.rsquared_adj), "n_topic_dummies": int(topic_d.shape[1]),
           "n_month_dummies": int(month_d.shape[1])}
    for c in keep:
        out[c] = (float(res.params[c]), float(res.bse[c]), float(res.pvalues[c]))
    return out


def run(info: dict) -> None:
    prepared = load_prepared()
    creators = load_creators()[["creator", "group", "organisation", "clipper", "subscribers"]]
    dt = pd.read_parquet(DIMENSIONS_TITLE)
    fcols = [c for c in dt.columns if c.startswith("F") and c[1:].isdigit()]
    fm = pd.read_parquet(FORMATS_PARQUET, columns=["row_id"] + HOOKS)
    tf = pd.read_parquet(FEATURES_TITLE, columns=["row_id", "n_tokens"])
    topics = pd.read_csv(TOPICS_CSV, usecols=["row_id", "topic_id"])
    df = prepared[(~prepared["is_dup"]) & prepared["has_views"] & (prepared["platform"] == "youtube")]
    df = df[["row_id", "creator", "genre", "month", "view_count"]].merge(dt[["row_id"] + fcols], on="row_id") \
        .merge(fm, on="row_id").merge(tf, on="row_id").merge(topics, on="row_id")
    predictors = fcols + HOOKS + ["n_tokens"]
    rows = []
    for (c, g), grp in df.groupby(["creator", "genre"]):
        if len(grp) < MIN_ENGAGEMENT_N:
            continue
        res = fit_creator(grp, predictors)
        for p in predictors:
            if p in res:
                coef, se, pv = res[p]
                rows.append({"creator": c, "genre": g, "predictor": p, "coef_per_sd": coef, "se_hc3": se, "p": pv, "n": res["n"],
                             "r2": res["r2"], "r2_adj": res["r2_adj"], "n_topic_dummies": res["n_topic_dummies"]})
    coefs = pd.DataFrame(rows).merge(creators, on="creator", how="left")
    coefs.to_csv(ANALYSIS_DIR / "engagement_coefficients.csv", index=False)
    info["creator_genre_models"] = int(coefs.groupby(["creator", "genre"]).ngroups)

    def summarise(g: pd.DataFrame) -> pd.Series:
        sign = np.sign(g["coef_per_sd"].median())
        return pd.Series({"n_creators": len(g), "median_coef_per_sd": g["coef_per_sd"].median(), "q25": g["coef_per_sd"].quantile(.25),
                          "q75": g["coef_per_sd"].quantile(.75), "share_positive": (g["coef_per_sd"] > 0).mean(),
                          "share_sig_positive": ((g["coef_per_sd"] > 0) & (g["p"] < .05)).mean(),
                          "share_sig_negative": ((g["coef_per_sd"] < 0) & (g["p"] < .05)).mean(),
                          "share_same_sign_as_median": (np.sign(g["coef_per_sd"]) == sign).mean(),
                          "median_r2": g["r2"].median()})
    s1 = coefs.groupby(["genre", "predictor"]).apply(summarize, include_groups=False).reset_index()
    s1.insert(0, "group", "ALL")
    s2 = coefs.groupby(["group", "genre", "predictor"]).apply(summarize, include_groups=False).reset_index()
    pd.concat([s1, s2], ignore_index=True).to_csv(ANALYSIS_DIR / "engagement_summary.csv", index=False)
    (ANALYSIS_DIR / "engagement_model.json").write_text(json.dumps({
        "dependent": "log(1 + view_count) (snapshot at fetch time, 2026-09-14)", "predictors": predictors,
        "controls": ["publish-month dummies", f"topic dummies (topics with >= {MIN_TOPIC_N} titles for the creator; others pooled)"],
        "standardisation": "predictors z-scored within creator x genre", "se": "HC3", "min_titles": MIN_ENGAGEMENT_N,
        "subscriber_normalisation": "log(views/subscribers) shifts the intercept only; slopes unchanged",
        "excluded": "Rumble (no view counts), verbatim repeats, titles without a view count"}, indent=2))
    print(s1.pivot(index="predictor", columns="genre", values="median_coef_per_sd").round(3).to_string())


def main(argv: Optional[Sequence[str]] = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.parse_args(argv)
    with stage_timer("stage5b_engagement") as info:
        run(info)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
