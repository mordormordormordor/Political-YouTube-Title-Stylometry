"""Stage 5c - hit concentration: how unequal are views within a channel, and
does title style go with a heavier tail?

For every creator x genre with >= 100 YouTube videos carrying a view count (all
rows, repeats included: a re-uploaded live loop is a separate video with its own
views): the Gini coefficient of views, the share of views held by the top 10 % of
videos, and a Clauset-Shalizi-Newman power-law fit of the tail (powerlaw.Fit,
discrete, xmin estimated by KS minimisation) with the log-likelihood-ratio test
against a lognormal (R > 0 favours the power law; p is the significance of R).
A tail is called power-law-like only when R > 0 and p < 0.05.

Then, within lane: Spearman correlations across creators between concentration
(Gini, top-10 % share) and the topic-controlled dimension scores and hook shares;
plus the same correlations with log(number of videos) and log(subscribers) as
the size-artefact check, and a pooled within-lane estimate (values demeaned by
lane x genre).

Outputs (data/titles/analysis/):
    hit_concentration.csv               per creator x genre
    hit_concentration_correlations.csv  within-lane and pooled-within-lane correlations

CLI:
    python -m pipeline_titles.hits
"""

from __future__ import annotations

import argparse
import contextlib
import io
import re
import warnings
from typing import Optional, Sequence

import numpy as np
import pandas as pd

from pipeline_titles.common import (
    ANALYSIS_DIR, DIMENSIONS_CSV, MIN_ENGAGEMENT_N, gini, load_lanes, load_prepared, stage_timer, top_share,
)

HOOKS = ["curiosity_gap", "outrage", "humor"]


def csn_fit(values: np.ndarray) -> dict:
    """Clauset-Shalizi-Newman fit and LR test vs lognormal (powerlaw package)."""
    import powerlaw
    x = values[values > 0].astype(float)
    if len(x) < 50:
        return {"alpha": np.nan, "xmin": np.nan, "n_tail": 0, "lr_vs_lognormal": np.nan, "lr_p": np.nan, "powerlaw_like": False}
    with warnings.catch_warnings(), contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
        warnings.simplefilter("ignore")
        fit = powerlaw.Fit(x, discrete=True, verbose=False)
        R, p = fit.distribution_compare("power_law", "lognormal", normalized_ratio=True)
    return {"alpha": float(fit.power_law.alpha), "xmin": float(fit.power_law.xmin), "n_tail": int((x >= fit.power_law.xmin).sum()),
            "lr_vs_lognormal": float(R), "lr_p": float(p), "powerlaw_like": bool(R > 0 and p < 0.05)}


def run(info: dict) -> None:
    from scipy.stats import spearmanr
    prepared = load_prepared()
    lanes = load_lanes()[["creator", "lane", "organisation", "clipper", "subscribers"]]
    df = prepared[prepared["has_views"] & (prepared["platform"] == "youtube")]
    rows = []
    for (c, g), grp in df.groupby(["creator", "genre"]):
        if len(grp) < MIN_ENGAGEMENT_N:
            continue
        v = grp["view_count"].to_numpy(float)
        rec = {"creator": c, "genre": g, "n_videos": len(grp), "median_views": float(np.median(v)), "mean_views": float(v.mean()),
               "gini": gini(v), "top10_share": top_share(v, 0.10), "top1_share": top_share(v, 0.01)}
        rec.update(csn_fit(v))
        rows.append(rec)
    hc = pd.DataFrame(rows).merge(lanes, on="creator", how="left")
    hc["subscribers"] = pd.to_numeric(hc["subscribers"], errors="coerce")
    dims = pd.read_csv(DIMENSIONS_CSV)
    fcols = [c[:-11] for c in dims.columns if re.fullmatch(r"F\d+_controlled", c)]
    hc = hc.merge(dims[["creator", "genre"] + [f + "_controlled" for f in fcols]], on=["creator", "genre"], how="left")
    shares = pd.read_csv(ANALYSIS_DIR / "format_hook_shares.csv")
    shares = shares[shares["level"] == "creator"][["creator", "genre"] + HOOKS]
    hc = hc.merge(shares, on=["creator", "genre"], how="left")
    hc.to_csv(ANALYSIS_DIR / "hit_concentration.csv", index=False)
    info.update(groups=len(hc), powerlaw_like=int(hc["powerlaw_like"].sum()))

    preds = [f + "_controlled" for f in fcols] + HOOKS + ["log_n_videos", "log_subscribers"]
    hc["log_n_videos"] = np.log(hc["n_videos"]); hc["log_subscribers"] = np.log(hc["subscribers"].clip(lower=1))
    crows = []
    for (lane, g), grp in hc.groupby(["lane", "genre"]):
        if len(grp) < 6:
            continue
        for target in ("gini", "top10_share"):
            for p in preds:
                sub = grp[[target, p]].dropna()
                if len(sub) < 6:
                    continue
                r, pv = spearmanr(sub[target], sub[p])
                crows.append({"scope": "within_lane", "lane": lane, "genre": g, "target": target, "predictor": p, "n_creators": len(sub), "spearman_r": round(float(r), 3), "p": round(float(pv), 4)})
    for g, grp in hc.groupby("genre"):
        dm = grp.copy()
        for col in ["gini", "top10_share"] + preds:
            dm[col] = dm[col] - dm.groupby("lane")[col].transform("mean")
        for target in ("gini", "top10_share"):
            for p in preds:
                sub = dm[[target, p]].dropna()
                if len(sub) < 10:
                    continue
                r, pv = spearmanr(sub[target], sub[p])
                crows.append({"scope": "pooled_within_lane (lane-demeaned)", "lane": "ALL", "genre": g, "target": target, "predictor": p, "n_creators": len(sub), "spearman_r": round(float(r), 3), "p": round(float(pv), 4)})
    pd.DataFrame(crows).to_csv(ANALYSIS_DIR / "hit_concentration_correlations.csv", index=False)
    print(hc.groupby("genre")[["gini", "top10_share", "powerlaw_like"]].agg(["median", "mean"]).round(3).to_string())


def main(argv: Optional[Sequence[str]] = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.parse_args(argv)
    with stage_timer("stage5c_hits") as info:
        run(info)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
