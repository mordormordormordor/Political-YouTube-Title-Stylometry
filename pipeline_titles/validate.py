"""Stage 2d - validate the factor solution against the LLM ratings.

Reads labels.csv (3,000 rated titles + 300 retest), dimensions_title.parquet and
dimensions.csv. Writes:

    validation_title_level.csv   Spearman r between every LLM dimension / flag and
                                 every factor score over the rated titles
    validation_creator_level.csv the same after aggregating both to creator x genre
                                 (mean over rated titles; groups with >= 5 rated titles)
    validation_candidates.csv    for each candidate label (Sensational, Critical,
                                 Analytical/Informational, Educational, Conversational,
                                 Humor): the best-matching factor, its r, the verdict
                                 (present / partial / merged / absent)
    validation_retest.csv        test-retest reliability on the 300 twice-rated titles
    validation_summary.json

CLI:
    python -m pipeline_titles.validate
"""

from __future__ import annotations

import argparse
import json
from typing import Optional, Sequence

import numpy as np
import pandas as pd

from pipeline_titles.common import ANALYSIS_DIR, DIMENSIONS_CSV, DIMENSIONS_TITLE, LABELS_CSV, stage_timer

CANDIDATES = {"Sensational": "sensational", "Critical": "critical", "Analytical/Informational": "analytical",
              "Educational": "educational", "Conversational": "conversational", "Humor": "humor"}
LLM_COLS = ["sensational", "critical", "analytical", "educational", "conversational", "humor", "curiosity_gap", "outrage"]


def verdict(r: float, strong: float = 0.5, partial: float = 0.3) -> str:
    if np.isnan(r):
        return "no data"
    return "present" if abs(r) >= strong else ("partial" if abs(r) >= partial else "absent")


def run(info: dict) -> None:
    from scipy.stats import spearmanr
    from sklearn.metrics import cohen_kappa_score
    labels = pd.read_csv(LABELS_CSV)
    rated = labels[labels["sensational"].notna()].copy()
    dt = pd.read_parquet(DIMENSIONS_TITLE)
    fcols = [c for c in dt.columns if c.startswith("F") and c[1:].isdigit()]
    names = json.loads((ANALYSIS_DIR / "factor_names.json").read_text())
    m = rated.merge(dt[["row_id"] + fcols + [f + "_resid" for f in fcols]], on="row_id", how="inner")
    info["n_rated_matched"] = int(len(m))

    # title level
    rows = []
    for l in LLM_COLS:
        for f in fcols:
            r, p = spearmanr(m[l], m[f])
            rows.append({"llm": l, "factor": f, "factor_auto_name": names[f]["auto"], "spearman_r": round(float(r), 4), "p": float(p), "n": len(m)})
    tl = pd.DataFrame(rows)
    tl.to_csv(ANALYSIS_DIR / "validation_title_level.csv", index=False)

    # creator level (same aggregation: means)
    agg = m.groupby(["creator", "genre"]).agg(n_rated=("row_id", "size"), **{l: (l, "mean") for l in LLM_COLS}).reset_index()
    agg = agg[agg["n_rated"] >= 5]
    dims = pd.read_csv(DIMENSIONS_CSV)
    cg = agg.merge(dims[["creator", "genre"] + [f"{f}_raw" for f in fcols] + [f"{f}_controlled" for f in fcols]], on=["creator", "genre"])
    rows = []
    for l in LLM_COLS:
        for f in fcols:
            for kind in ("raw", "controlled"):
                r, p = spearmanr(cg[l], cg[f"{f}_{kind}"])
                pr = cg[l].corr(cg[f"{f}_{kind}"])
                rows.append({"llm": l, "factor": f, "factor_auto_name": names[f]["auto"], "score": kind, "spearman_r": round(float(r), 4),
                             "pearson_r": round(float(pr), 4), "p": float(p), "n_groups": len(cg)})
    cl = pd.DataFrame(rows)
    cl.to_csv(ANALYSIS_DIR / "validation_creator_level.csv", index=False)
    info["n_creator_groups"] = int(len(cg))

    # candidate mapping (creator level, raw scores)
    best_by_cand = {}
    rows = []
    for cand, col in CANDIDATES.items():
        sub = cl[(cl["llm"] == col) & (cl["score"] == "raw")].set_index("factor")["spearman_r"]
        f = sub.abs().idxmax()
        best_by_cand[cand] = f
        rows.append({"candidate": cand, "llm_column": col, "best_factor": f, "factor_auto_name": names[f]["auto"],
                     "creator_level_r": round(float(sub[f]), 3), "second_factor": sub.abs().drop(f).idxmax(),
                     "second_r": round(float(sub[sub.abs().drop(f).idxmax()]), 3), "verdict": verdict(float(sub[f]))})
    cand = pd.DataFrame(rows)
    shared = cand.groupby("best_factor")["candidate"].apply(list)
    cand["merged_with"] = cand["best_factor"].map(lambda f: ", ".join(c for c in shared[f] if len(shared[f]) > 1))
    cand.loc[(cand["merged_with"] != "") & (cand["verdict"] != "absent"), "verdict"] = "merged: " + cand["merged_with"]
    cand.to_csv(ANALYSIS_DIR / "validation_candidates.csv", index=False)

    # test-retest
    re = rated[rated["retest"] & rated["retest_sensational"].notna()]
    rows = []
    for l in LLM_COLS:
        a, b = re[l].astype(int).to_numpy(), re["retest_" + l].astype(int).to_numpy()
        rec = {"dimension": l, "n": len(re), "exact_agreement": round(float(np.mean(a == b)), 3)}
        if l in ("humor", "curiosity_gap", "outrage"):
            rec["kappa"] = round(float(cohen_kappa_score(a, b)), 3) if len(set(a) | set(b)) > 1 else np.nan
            rec["spearman_r"] = np.nan; rec["within_1"] = np.nan; rec["weighted_kappa"] = np.nan
        else:
            rec["within_1"] = round(float(np.mean(np.abs(a - b) <= 1)), 3)
            rec["spearman_r"] = round(float(spearmanr(a, b)[0]), 3)
            rec["weighted_kappa"] = round(float(cohen_kappa_score(a, b, weights="quadratic")), 3)
            rec["kappa"] = np.nan
        rows.append(rec)
    a, b = re["format_llm"].fillna("none"), re["retest_format_llm"].fillna("none")
    rows.append({"dimension": "format_llm", "n": len(re), "exact_agreement": round(float(np.mean(a == b)), 3),
                 "kappa": round(float(cohen_kappa_score(a, b)), 3), "spearman_r": np.nan, "within_1": np.nan, "weighted_kappa": np.nan})
    rt = pd.DataFrame(rows)
    rt.to_csv(ANALYSIS_DIR / "validation_retest.csv", index=False)
    info["n_retest"] = int(len(re))
    summary = {"n_rated": int(len(rated)), "n_matched": int(len(m)), "n_creator_groups": int(len(cg)), "n_retest": int(len(re)),
               "candidates": cand.to_dict(orient="records"), "retest": rt.to_dict(orient="records"),
               "llm_means": {l: round(float(rated[l].mean()), 3) for l in LLM_COLS}}
    (ANALYSIS_DIR / "validation_summary.json").write_text(json.dumps(summary, indent=2, default=str))
    print(cand[["candidate", "best_factor", "creator_level_r", "verdict"]].to_string(index=False))
    print(rt[["dimension", "exact_agreement", "within_1", "weighted_kappa", "kappa"]].to_string(index=False))


def main(argv: Optional[Sequence[str]] = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.parse_args(argv)
    with stage_timer("stage2d_validate") as info:
        run(info)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
