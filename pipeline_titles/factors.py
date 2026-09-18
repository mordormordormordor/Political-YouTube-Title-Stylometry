"""Stage 2b - exploratory factor analysis of the aggregated style features, factor
scores for every cell, creator and title, and topic control.

Reads features.csv (creator x genre x month), features_title.parquet, topics.csv
and creators.csv. Writes, under data/titles/analysis/:

    efa_summary.json         features used / dropped (and why), n cells, KMO,
                             Bartlett, parallel-analysis result, retained factors,
                             variance explained, factor correlations (oblimin)
    scree.csv, scree.png     eigenvalues of the correlation matrix vs the
                             parallel-analysis 95th percentile
    factor_loadings.csv      oblimin loadings (plus varimax for comparison)
    factor_names.json        auto-generated names from the loadings; edit the
                             "name" fields by hand - report.py reads this file
    dimensions_monthly.csv   cell scores (creator x genre x month), raw and
                             topic-controlled
    dimensions.csv           creator x genre: raw score, topic-expected component,
                             topic-controlled (residual) score, percentile ranks
                             within genre (non-low-n creators), channel-group medians
    dimensions_title.parquet row_id, topic_id, raw and residual title-level scores
    dimensions_by_topic.csv  creator scores within the 5 largest shared topics
    topic_control_summary.csv  per factor: share of title-level and creator-level
                             variance explained by topic

Method. Cells with >= 15 unique titles enter the EFA (each creator x genre
contributes at most 9 monthly rows, so the matrix is creator-balanced by
construction). Features are the _p100 / _mean columns minus artefacts (see
EXCLUDE) and minus features below 0.5 per 100 titles or with |r| > 0.95 to an
earlier feature. Number of factors: Horn's parallel analysis (100 random matrices,
95th percentile), capped at MAX_FACTORS. Extraction: minres, oblimin rotation
(varimax reported beside it). Factor scores: regression method; the same weights
are applied to title-level features (binary features x100 so the units match),
which gives cell scores exactly by linearity.

Topic control: for every factor the topic mean is estimated on the creator-
balanced subset; a title's residual is its score minus its topic's mean; a
creator's topic-controlled score is the mean residual of its unique titles, and
raw minus controlled is the part of its raw score that its topic mix predicts.

CLI:
    python -m pipeline_titles.factors
    python -m pipeline_titles.factors --n-factors 6     # force a solution (for comparison only)
"""

from __future__ import annotations

import argparse
import json
from typing import Optional, Sequence

import numpy as np
import pandas as pd

from pipeline_titles.common import (
    ANALYSIS_DIR, DIMENSIONS_CSV, DIMENSIONS_TITLE, FEATURES_CSV, FEATURES_TITLE, LOW_N, SEED, TOPICS_CSV,
    load_creators, load_prepared, stage_timer,
)
from pipeline_titles.features import BINARY_OR_COUNT

MIN_CELL = 15
MIN_PREVALENCE = 0.5
MAX_FACTORS = 12
MAX_ABS_CORR = 0.95
EXCLUDE = {"n_chars_raw_mean", "brand_stripped_p100", "emoji_count_p100", "pipe_segments_raw_mean",
           "colon_segments_raw_mean", "brackets_raw_p100"}
FACTOR_NAMES_JSON = ANALYSIS_DIR / "factor_names.json"


def select_features(cells: pd.DataFrame) -> tuple[list[str], dict]:
    cols = [c for c in cells.columns if (c.endswith("_p100") or c.endswith("_mean")) and c not in EXCLUDE]
    keep, dropped = [], {}
    for c in cols:
        x = cells[c]
        if x.isna().mean() > 0.05:
            dropped[c] = "missing in > 5 % of cells"
        elif c.endswith("_p100") and x.mean() < MIN_PREVALENCE:
            dropped[c] = f"prevalence {x.mean():.2f} per 100 titles < {MIN_PREVALENCE}"
        elif x.std() < 1e-9:
            dropped[c] = "constant"
        else:
            keep.append(c)
    corr = cells[keep].corr().abs()
    final = []
    for c in keep:
        partner = next((k for k in final if corr.loc[c, k] > MAX_ABS_CORR), None)
        if partner:
            dropped[c] = f"|r| = {corr.loc[c, partner]:.3f} with {partner}"
        else:
            final.append(c)
    return final, dropped


def parallel_analysis(X: np.ndarray, n_iter: int = 100, percentile: float = 95, seed: int = SEED) -> tuple[np.ndarray, np.ndarray, int]:
    """Eigenvalues of corr(X), the percentile of random-data eigenvalues, and the
    number of observed eigenvalues above their random counterpart (Horn 1965)."""
    n, p = X.shape
    obs = np.sort(np.linalg.eigvalsh(np.corrcoef(X, rowvar=False)))[::-1]
    rng = np.random.RandomState(seed)
    rand = np.empty((n_iter, p))
    for i in range(n_iter):
        rand[i] = np.sort(np.linalg.eigvalsh(np.corrcoef(rng.normal(size=(n, p)), rowvar=False)))[::-1]
    thr = np.percentile(rand, percentile, axis=0)
    k = int(np.sum(obs > thr))
    return obs, thr, k


def auto_name(loadings: pd.Series, cut: float = 0.4, top: int = 4) -> str:
    strong = loadings[loadings.abs() >= cut].sort_values(key=np.abs, ascending=False).head(top)
    if strong.empty:
        strong = loadings.sort_values(key=np.abs, ascending=False).head(3)
    return " ".join(("+" if v > 0 else "-") + k.replace("_p100", "").replace("_mean", "") for k, v in strong.items())


def orient(loadings: np.ndarray) -> np.ndarray:
    """Sign vector flipping each factor so its largest-|loading| feature loads positively."""
    return np.array([1.0 if loadings[np.argmax(np.abs(loadings[:, j])), j] > 0 else -1.0 for j in range(loadings.shape[1])])


def _import_factor_analyzer():
    """factor_analyzer 0.5.1 still passes check_array(force_all_finite=...), which
    scikit-learn >= 1.6 renamed to ensure_all_finite; shim it before importing."""
    import sklearn.utils
    import sklearn.utils.validation as v
    orig = v.check_array

    def check_array(*a, **k):
        if "force_all_finite" in k:
            k["ensure_all_finite"] = k.pop("force_all_finite")
        return orig(*a, **k)
    v.check_array = check_array
    sklearn.utils.check_array = check_array
    from factor_analyzer import FactorAnalyzer, calculate_bartlett_sphericity, calculate_kmo
    return FactorAnalyzer, calculate_bartlett_sphericity, calculate_kmo


def run(n_factors_forced: Optional[int], info: dict) -> None:
    FactorAnalyzer, calculate_bartlett_sphericity, calculate_kmo = _import_factor_analyzer()
    monthly = pd.read_csv(FEATURES_CSV)
    cells = monthly[monthly["n_titles"] >= MIN_CELL].reset_index(drop=True)
    feats, dropped = select_features(cells)
    X = cells[feats].to_numpy(dtype=float)
    col_mean = np.nanmean(X, axis=0)
    X = np.where(np.isnan(X), col_mean, X)
    kmo_per, kmo_total = calculate_kmo(pd.DataFrame(X, columns=feats))
    chi2, bart_p = calculate_bartlett_sphericity(pd.DataFrame(X, columns=feats))
    obs, thr, k_pa = parallel_analysis(X)
    k_kaiser = int(np.sum(obs > 1))
    k = n_factors_forced or min(k_pa, MAX_FACTORS)
    pd.DataFrame({"component": np.arange(1, len(obs) + 1), "eigenvalue": obs, "parallel_95th": thr}).to_csv(ANALYSIS_DIR / "scree.csv", index=False)
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        fig, ax = plt.subplots(figsize=(7, 4))
        ax.plot(np.arange(1, len(obs) + 1), obs, "o-", label="observed eigenvalue")
        ax.plot(np.arange(1, len(thr) + 1), thr, "s--", label="parallel analysis (95th pct, 100 draws)")
        ax.axhline(1, color="grey", lw=0.8); ax.axvline(k + 0.5, color="red", lw=0.8, label=f"retained = {k}")
        ax.set_xlabel("component"); ax.set_ylabel("eigenvalue"); ax.set_title(f"Scree: {len(feats)} features, {len(cells)} creator x genre x month cells")
        ax.legend(); fig.tight_layout(); fig.savefig(ANALYSIS_DIR / "scree.png", dpi=130); plt.close(fig)
    except Exception as e:  # plotting must never break the stage
        print("scree plot failed:", e)

    fa = FactorAnalyzer(n_factors=k, rotation="oblimin", method="minres")
    fa.fit(X)
    sign = orient(fa.loadings_)
    load = pd.DataFrame(fa.loadings_ * sign, index=feats, columns=[f"F{j + 1}" for j in range(k)])
    fav = FactorAnalyzer(n_factors=k, rotation="varimax", method="minres").fit(X)
    loadv = pd.DataFrame(fav.loadings_ * orient(fav.loadings_), index=feats, columns=[f"F{j + 1}_varimax" for j in range(k)])
    comm = pd.Series(fa.get_communalities(), index=feats, name="communality")
    pd.concat([load, comm, loadv], axis=1).round(4).rename_axis("feature").to_csv(ANALYSIS_DIR / "factor_loadings.csv")
    var, prop, cum = fa.get_factor_variance()
    phi = getattr(fa, "phi_", None)
    names = {f"F{j + 1}": {"auto": auto_name(load[f"F{j + 1}"]), "name": ""} for j in range(k)}
    if FACTOR_NAMES_JSON.exists():
        old = json.loads(FACTOR_NAMES_JSON.read_text())
        for f in names:
            if f in old and old[f].get("name") and old[f].get("auto") == names[f]["auto"]:
                names[f]["name"] = old[f]["name"]
    FACTOR_NAMES_JSON.write_text(json.dumps(names, indent=2))
    summary = {
        "n_cells": int(len(cells)), "min_cell": MIN_CELL, "n_features": len(feats), "features": feats, "dropped": dropped,
        "kmo_total": round(float(kmo_total), 4), "bartlett_chi2": round(float(chi2), 1), "bartlett_p": float(bart_p),
        "parallel_analysis_factors": k_pa, "kaiser_factors": k_kaiser, "retained": k, "forced": n_factors_forced,
        "variance_explained": [round(float(v), 4) for v in prop], "cumulative_variance": round(float(cum[-1]), 4),
        "factor_correlations": (np.round(phi, 3).tolist() if phi is not None else None),
        "rotation": "oblimin", "method": "minres",
    }
    (ANALYSIS_DIR / "efa_summary.json").write_text(json.dumps(summary, indent=2))
    info.update(n_cells=len(cells), n_features=len(feats), retained=k, parallel=k_pa, kmo=round(float(kmo_total), 3))
    print(f"EFA: {len(feats)} features, {len(cells)} cells, KMO {kmo_total:.3f}, PA suggests {k_pa} (Kaiser {k_kaiser}); retained {k}; cum var {cum[-1]:.3f}")

    # ---- scores: cells, titles ----
    fcols = list(load.columns)
    cell_scores = pd.DataFrame(fa.transform(X) * sign, columns=fcols)
    cells_out = pd.concat([cells[["creator", "genre", "month", "n_titles", "group"]].reset_index(drop=True), cell_scores], axis=1)

    tf = pd.read_parquet(FEATURES_TITLE)
    tf = tf[~tf["is_dup"]].reset_index(drop=True)
    base = [c.replace("_p100", "").replace("_mean", "") for c in feats]
    Xt = tf[base].to_numpy(dtype=float)
    scale = np.array([100.0 if b in BINARY_OR_COUNT else 1.0 for b in base])
    Xt = Xt * scale
    Xt = np.where(np.isnan(Xt), fa.mean_, Xt)
    title_scores = pd.DataFrame(fa.transform(Xt) * sign, columns=fcols)
    titles = pd.concat([tf[["row_id", "creator", "genre", "month"]].reset_index(drop=True), title_scores], axis=1)
    prepared = load_prepared()[["row_id", "in_balanced", "low_n", "n_unique"]]
    topics = pd.read_csv(TOPICS_CSV, usecols=["row_id", "topic_id", "political"])
    titles = titles.merge(prepared, on="row_id").merge(topics, on="row_id", how="left")

    # ---- topic control ----
    bal = titles[titles["in_balanced"]]
    ctrl_rows = []
    for f in fcols:
        tmean = bal.groupby("topic_id")[f].mean()
        titles[f + "_resid"] = titles[f] - titles["topic_id"].map(tmean).fillna(bal[f].mean())
        r2_title = 1 - bal[f + "_resid"].var() / bal[f].var() if f + "_resid" in bal else np.nan
        ctrl_rows.append({"factor": f, "n_topics": int(tmean.notna().sum()), "title_level_r2_topic": round(float(1 - titles.loc[titles["in_balanced"], f + "_resid"].var() / bal[f].var()), 4)})
    titles.to_parquet(DIMENSIONS_TITLE, index=False)

    creators = load_creators()[["creator", "group", "organisation", "clipper", "platform"]]
    agg = {f: (f, "mean") for f in fcols} | {f + "_resid": (f + "_resid", "mean") for f in fcols}
    cg = titles.groupby(["creator", "genre"]).agg(n_unique=("row_id", "size"), **agg).reset_index()
    cg["low_n"] = cg["n_unique"] < LOW_N
    for f in fcols:
        cg[f + "_raw"] = cg[f]
        cg[f + "_controlled"] = cg[f + "_resid"]
        cg[f + "_topic_component"] = cg[f] - cg[f + "_resid"]
        cg = cg.drop(columns=[f, f + "_resid"])
    cg = cg.merge(creators, on="creator", how="left")
    for f in fcols:
        for kind in ("raw", "controlled"):
            col = f"{f}_{kind}"
            cg[f"{f}_pct_{kind}"] = np.nan
            for g, sub in cg[~cg["low_n"]].groupby("genre"):
                cg.loc[sub.index, f"{f}_pct_{kind}"] = sub[col].rank(pct=True) * 100
        med = cg[~cg["low_n"]].groupby(["group", "genre"])[f"{f}_controlled"].median().rename(f"{f}_group_median")
        cg = cg.join(med, on=["group", "genre"])
    cg.to_csv(DIMENSIONS_CSV, index=False)
    for r, f in zip(ctrl_rows, fcols):
        ok = cg[~cg["low_n"]]
        r["creator_level_r2_topic"] = round(float(1 - ok[f"{f}_controlled"].var() / ok[f"{f}_raw"].var()), 4)
        r["creator_level_corr_raw_controlled"] = round(float(ok[f"{f}_raw"].corr(ok[f"{f}_controlled"])), 4)
        r["auto_name"] = names[f]["auto"]
    pd.DataFrame(ctrl_rows).to_csv(ANALYSIS_DIR / "topic_control_summary.csv", index=False)

    # monthly cells: controlled = mean residual over the cell's titles
    mres = titles.groupby(["creator", "genre", "month"])[[f + "_resid" for f in fcols]].mean().reset_index()
    mres.columns = ["creator", "genre", "month"] + [f + "_controlled" for f in fcols]
    cells_out = cells_out.merge(mres, on=["creator", "genre", "month"], how="left")
    cells_out.to_csv(ANALYSIS_DIR / "dimensions_monthly.csv.gz", index=False)

    # within the 5 largest shared topics (by number of creators with >= 10 titles in them)
    tl = pd.read_csv(ANALYSIS_DIR / "topic_labels.csv")[["topic_id", "label"]]
    cnt = titles.groupby(["topic_id", "creator", "genre"]).size().reset_index(name="n")
    big = cnt[cnt["n"] >= 10].groupby("topic_id")["creator"].nunique().nlargest(5).index.tolist()
    within = titles[titles["topic_id"].isin(big)].groupby(["topic_id", "creator", "genre"]).agg(n=("row_id", "size"), **{f: (f, "mean") for f in fcols}).reset_index()
    within = within[within["n"] >= 10].merge(tl, on="topic_id").merge(creators[["creator", "group"]], on="creator", how="left")
    within.to_csv(ANALYSIS_DIR / "dimensions_by_topic.csv", index=False)
    print("factors:", {f: names[f]["auto"] for f in fcols})


def main(argv: Optional[Sequence[str]] = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--n-factors", type=int, default=None, help="force the number of factors (default: parallel analysis)")
    a = ap.parse_args(argv)
    with stage_timer("stage2b_factors", n_factors_forced=a.n_factors) as info:
        run(a.n_factors, info)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
