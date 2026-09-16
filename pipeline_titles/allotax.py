"""Allotaxonographs (Dodds et al. 2023) for the leaning systems and the two commentary lanes.

Each figure is the Computational Story Lab's own instrument, rendered by allotaxonometer-ui
(the Svelte library behind the lab's web app and py-allotax) through Node and printed to
PNG by Puppeteer: the rank-rank histogram diamond with the words that sit far from the
diagonal named along the flanks, the rank-turbulence-divergence word shift, the balance
bars and the counts-per-cell legend. Rank-turbulence divergence with alpha = 1/3, the value
the paper recommends for text.

Comparisons (system 1 on the left flank and the grey bars, system 2 on the right flank and
the blue bars):
    opus  : titles the judge labelled left vs titles it labelled right
    lanes : left-commentary vs right-commentary channels, every unique edited upload in the
            creator-balanced subset
Types are the vocabulary tokens of document 11 (lower-cased words minus stopwords and
digits, possessives dropped), so the ranks agree with the tables of document 14, whose
rank-turbulence divergence (textstats.rank_turbulence_divergence) reproduces the
library's numbers.

Outputs:
    pipeline_titles/reports/figures/14_allotax_<name>.png
    data/titles/analysis/allotax_summary.csv         one row per comparison: D, sizes, exclusive shares
    data/titles/analysis/allotax_contributions.csv   the 100 largest contributions per comparison
    data/titles/analysis/cache/allotax/<name>.json   the spec sent to the renderer (input data; not tracked)

Needs `node` on the PATH and `npm install` run once in pipeline_titles/allotax_js (Puppeteer
fetches its own Chrome). Without them the stage prints why it skipped and leaves the
tracked figures as they are. Run by `report` through figures.main(), or alone:

    python -m pipeline_titles.allotax [--only opus lanes] [--alpha 0.3333] [--top-n 40]
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
from collections import Counter
from fractions import Fraction
from pathlib import Path
from typing import Iterable, Optional, Sequence

import pandas as pd

from pipeline_titles.common import ANALYSIS_DIR, CACHE_DIR, REPORTS_DIR, load_lanes, load_prepared, stage_timer
from pipeline_titles.textstats import vocab_tokens

JS_DIR = Path(__file__).resolve().parent / "allotax_js"
FIG_DIR = REPORTS_DIR / "figures"
SPEC_DIR = CACHE_DIR / "allotax"
ALPHA = 1 / 3
MODEL_NAMES = {"label_claude_code_opus": ("opus", "Claude Opus")}
UNAVAILABLE_MSG = ("needs `node` on the PATH and `npm install` in pipeline_titles/allotax_js "
                   "(Puppeteer downloads its Chrome once); the tracked figures are left as they are")


def available() -> bool:
    return shutil.which("node") is not None and (JS_DIR / "node_modules" / "allotaxonometer-ui").exists() and (JS_DIR / "node_modules" / "puppeteer").exists()


def system_records(titles: Iterable[str]) -> tuple[list[dict], int]:
    """allotaxonometer input for one system: [{types, counts, totalunique, probs}] sorted by
    count, plus the token total."""
    c = Counter()
    for t in titles:
        c.update(vocab_tokens(t))
    total = sum(c.values())
    recs = [{"types": w, "counts": int(n), "totalunique": len(c), "probs": round(n / total, 6) if total else 0.0} for w, n in c.most_common()]
    return recs, total


def alpha_label(alpha: float) -> str:
    f = Fraction(alpha).limit_denominator(12)
    return str(f) if abs(float(f) - alpha) < 1e-9 else f"{alpha:g}"


def comparisons(only: Optional[Sequence[str]] = None) -> list[dict]:
    """The systems to compare: name, titles (long, for the flanks), short names (for the word
    shift header) and the two title lists."""
    out = []
    labs_path = ANALYSIS_DIR / "leaning_labels.csv.gz"
    if labs_path.exists():
        labs = pd.read_csv(labs_path)
        cols = [c for c in labs.columns if c.startswith("label_") and c in MODEL_NAMES]
        for c in cols:
            name, model = MODEL_NAMES[c]
            out.append({"name": name, "title1": f"Titles {model} read as left", "title2": f"Titles {model} read as right", "short1": "left-read titles", "short2": "right-read titles",
                        "titles1": labs.loc[labs[c] == "left", "title_norm"].tolist(), "titles2": labs.loc[labs[c] == "right", "title_norm"].tolist()})
    prepared = load_prepared()
    lanes = load_lanes()[["creator", "lane"]]
    d = prepared[(~prepared["is_dup"]) & (prepared["genre"] == "videos") & (prepared["in_balanced"])].merge(lanes, on="creator", how="left")
    out.append({"name": "lanes", "title1": "Left-commentary channels", "title2": "Right-commentary channels", "short1": "left commentary", "short2": "right commentary",
                "titles1": d.loc[d["lane"] == "left_commentary", "title_norm"].tolist(), "titles2": d.loc[d["lane"] == "right_commentary", "title_norm"].tolist()})
    if only:
        out = [c for c in out if c["name"] in set(only)]
    return out


def render(spec: dict, spec_path: Path) -> dict:
    """Write the spec, run the Node renderer, return the JSON it wrote (D, balances, top contributions)."""
    spec_path.parent.mkdir(parents=True, exist_ok=True)
    spec_path.write_text(json.dumps(spec, ensure_ascii=False))
    proc = subprocess.run(["node", "render.mjs", str(spec_path)], cwd=JS_DIR, capture_output=True, text=True, timeout=1800)
    if proc.returncode != 0:
        raise RuntimeError(f"allotax render failed for {spec_path.name}: {proc.stderr.strip()[-800:] or proc.stdout[-800:]}")
    print("  " + proc.stdout.strip().splitlines()[-1], flush=True)
    return json.loads(Path(spec["out_json"]).read_text())


def main(argv: Optional[Sequence[str]] = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--only", nargs="*", default=None, help="comparison names to render (default: all)")
    ap.add_argument("--alpha", type=float, default=ALPHA)
    ap.add_argument("--top-n", type=int, default=40, help="bars in the word shift")
    ap.add_argument("--scale", type=float, default=2.0, help="device scale factor of the PNG")
    a = ap.parse_args(argv)
    if not available():
        print(f"allotaxonographs skipped: {UNAVAILABLE_MSG}")
        return 0
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    with stage_timer("allotax", alpha=round(a.alpha, 4), top_n=a.top_n) as info:
        rows, contribs = [], []
        for comp in comparisons(a.only):
            recs1, tok1 = system_records(comp["titles1"]); recs2, tok2 = system_records(comp["titles2"])
            if not recs1 or not recs2:
                print(f"  {comp['name']}: empty system, skipped"); continue
            png = FIG_DIR / f"14_allotax_{comp['name']}.png"
            spec = {"data1": recs1, "data2": recs2, "alpha": a.alpha, "alpha_label": alpha_label(a.alpha), "title1": comp["title1"], "title2": comp["title2"],
                    "short1": comp["short1"], "short2": comp["short2"], "top_n": a.top_n, "scale": a.scale, "out_png": str(png), "out_json": str(SPEC_DIR / f"{comp['name']}_result.json"), "json_top": 100}
            print(f"{comp['name']}: {len(comp['titles1']):,} vs {len(comp['titles2']):,} titles, {len(recs1):,} vs {len(recs2):,} types", flush=True)
            res = render(spec, SPEC_DIR / f"{comp['name']}.json")
            types1, types2 = {r["types"] for r in recs1}, {r["types"] for r in recs2}
            rows.append({"comparison": comp["name"], "system_1": comp["title1"], "system_2": comp["title2"], "alpha": a.alpha, "divergence": round(res["divergence"], 4),
                         "n_titles_1": len(comp["titles1"]), "n_titles_2": len(comp["titles2"]), "n_tokens_1": tok1, "n_tokens_2": tok2, "n_types_1": len(recs1), "n_types_2": len(recs2),
                         "n_types_union": res["n_types_union"], "exclusive_share_1": round(len(types1 - types2) / len(types1), 3), "exclusive_share_2": round(len(types2 - types1) / len(types2), 3),
                         "figure": png.name, "bars": a.top_n, "allotaxonometer_ui": res["versions"]["allotaxonometer-ui"], "node": res["versions"]["node"]})
            for i, t in enumerate(res["top"], 1):
                contribs.append({"comparison": comp["name"], "rank": i, "type": t["type"], "rank_1": t["rank1"], "rank_2": t["rank2"], "count_1": t["count1"], "count_2": t["count2"],
                                 "contribution": t["contribution"], "side": "system_2" if t["contribution"] > 0 else "system_1"})
            info["versions"] = res["versions"]
        if rows:
            done = {r["comparison"] for r in rows}
            for name, new in (("allotax_summary.csv", pd.DataFrame(rows)), ("allotax_contributions.csv", pd.DataFrame(contribs))):
                path = ANALYSIS_DIR / name
                if a.only and path.exists():   # a partial run replaces only its own comparisons
                    old = pd.read_csv(path); new = pd.concat([old[~old["comparison"].isin(done)], new])
                new.to_csv(path, index=False)
        info["figures"] = len(rows)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
