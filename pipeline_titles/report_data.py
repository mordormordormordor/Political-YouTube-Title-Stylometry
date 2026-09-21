"""Assemble every per-creator profile card and the landscape maps into one JSON
(pipeline_titles/reports/cards.json) that report.py renders as Markdown cards and
that the HTML page embeds.

Card layout (fixed): identity (channel group, organization, clipper, platform,
subscribers); per genre: n titles (rows / unique / repeat share / low-n), political
share, top-5 topics, dimension scores as percentile ranks with the group median, hook and format
shares, five nearest style neighbors (and topic neighbors), monthly drift
sparkline data, engagement coefficients (if n >= 100 with views), hit
concentration, lexical diversity.

CLI:
    python -m pipeline_titles.report_data
"""

from __future__ import annotations

import argparse
import json
import math
import re
from typing import Optional, Sequence

import numpy as np
import pandas as pd

from pipeline_titles.common import ANALYSIS_DIR, DIMENSIONS_CSV, GENRES, GROUPS, MONTHS, REPORTS_DIR, load_creators, stage_timer, utc_now

CARDS_JSON = REPORTS_DIR / "cards.json"
HOOKS = ["curiosity_gap", "outrage", "humor"]
FORMATS = ["question", "breaking_live", "episode_show", "interview_guest", "reaction", "confrontation", "listicle", "howto_explainer"]


def _num(x):
    if x is None:
        return None
    try:
        f = float(x)
    except (TypeError, ValueError):
        return x
    return None if (math.isnan(f) or math.isinf(f)) else round(f, 4)


def _rec(df: pd.DataFrame, **match) -> Optional[pd.Series]:
    m = np.ones(len(df), dtype=bool)
    for k, v in match.items():
        m &= (df[k] == v).to_numpy()
    sub = df[m]
    return sub.iloc[0] if len(sub) else None


def build() -> dict:
    creators_tbl = load_creators()
    summ = pd.read_csv(ANALYSIS_DIR / "creator_genre_summary.csv")
    pol = pd.read_csv(ANALYSIS_DIR / "creator_political_share.csv")
    mix = pd.read_csv(ANALYSIS_DIR / "creator_topic_mix.csv.gz")
    dims = pd.read_csv(DIMENSIONS_CSV)
    fcols = [c[:-4] for c in dims.columns if re.fullmatch(r"F\d+_raw", c)]
    names = json.loads((ANALYSIS_DIR / "factor_names.json").read_text())
    shares = pd.read_csv(ANALYSIS_DIR / "format_hook_shares.csv")
    shares_c = shares[shares["level"] == "creator"]
    shares_l = shares[shares["level"] == "group_mean_of_creators"]
    nn_s = pd.read_csv(ANALYSIS_DIR / "neighbours_style.csv")
    nn_s = nn_s[nn_s["titles"] == "all"]
    nn_t = pd.read_csv(ANALYSIS_DIR / "neighbours_topic.csv")
    nn_t = nn_t[nn_t["titles"] == "all"]
    monthly = pd.read_csv(ANALYSIS_DIR / "drift_creator_monthly.csv.gz")
    eng = pd.read_csv(ANALYSIS_DIR / "engagement_coefficients.csv")
    hits = pd.read_csv(ANALYSIS_DIR / "hit_concentration.csv")
    fc = pd.read_csv(ANALYSIS_DIR / "features_creator.csv")
    sc = pd.read_csv(ANALYSIS_DIR / "style_clusters.csv"); sc = sc[sc["titles"] == "all"]
    tc = pd.read_csv(ANALYSIS_DIR / "topic_clusters.csv"); tc = tc[tc["titles"] == "all"]
    map_s = pd.read_csv(ANALYSIS_DIR / "map_style.csv")
    map_t = pd.read_csv(ANALYSIS_DIR / "map_topic.csv")
    labels = pd.read_csv(ANALYSIS_DIR / "topic_labels.csv")
    extra = {}
    for name in ("arousal_index.csv", "caps_profile.csv", "signature_keywords.csv", "leaning_by_creator.csv"):
        extra[name] = pd.read_csv(ANALYSIS_DIR / name) if (ANALYSIS_DIR / name).exists() else None
    group_med = {}
    for (group, genre), g in dims[~dims["low_n"]].groupby(["group", "genre"]):
        group_med[f"{group}|{genre}"] = {f: _num(g[f + "_controlled"].median()) for f in fcols}

    creators = {}
    for r in creators_tbl.itertuples():
        card = {"creator": r.creator, "channel_name": r.channel_name, "platform": r.platform, "group": r.group,
                "organisation": r.organisation, "clipper": bool(r.clipper), "subscribers": _num(r.subscribers), "note": r.note, "genres": {}}
        for genre in GENRES:
            s = _rec(summ, creator=r.creator, genre=genre)
            if s is None:
                continue
            g = {"n_rows": int(s.n_rows), "n_unique": int(s.n_unique), "repeat_share": _num(s.repeat_share), "low_n": bool(s.low_n),
                 "n_with_views": int(s.n_with_views), "first_month": s.first_month, "last_month": s.last_month}
            p = _rec(pol, creator=r.creator, genre=genre)
            g["political_share"] = _num(p.political_share) if p is not None else None
            top = mix[(mix["creator"] == r.creator) & (mix["genre"] == genre)].nlargest(5, "share")
            g["topics_top5"] = [{"topic_id": int(t.topic_id), "label": t.label, "share": _num(t.share), "political": bool(t.political)} for t in top.itertuples()]
            d = _rec(dims, creator=r.creator, genre=genre)
            if d is not None:
                g["dimensions"] = {f: {"raw": _num(d[f + "_raw"]), "controlled": _num(d[f + "_controlled"]), "topic_component": _num(d[f + "_topic_component"]),
                                       "pct_raw": _num(d[f + "_pct_raw"]), "pct_controlled": _num(d[f + "_pct_controlled"]), "group_median": _num(d[f + "_group_median"])} for f in fcols}
            sh = _rec(shares_c, creator=r.creator, genre=genre)
            if sh is not None:
                lm = _rec(shares_l, group=r.group, genre=genre)
                g["hooks"] = {h: {"share": _num(sh[h]), "group_mean": _num(lm[h]) if lm is not None else None} for h in HOOKS}
                g["formats"] = {f: {"share": _num(sh[f]), "group_mean": _num(lm[f]) if lm is not None else None} for f in FORMATS}
            n = _rec(nn_s, creator=r.creator, genre=genre)
            if n is not None:
                g["neighbours_style"] = [{"creator": n[f"nn{i}"], "group": n[f"nn{i}_group"], "distance": _num(n[f"nn{i}_dist"])} for i in range(1, 6)]
            n = _rec(nn_t, creator=r.creator, genre=genre)
            if n is not None:
                g["neighbours_topic"] = [{"creator": n[f"nn{i}"], "group": n[f"nn{i}_group"], "js": _num(n[f"nn{i}_js"])} for i in range(1, 6)]
            c1 = _rec(sc, creator=r.creator, genre=genre); c2 = _rec(tc, creator=r.creator, genre=genre)
            g["style_cluster"] = int(c1.style_cluster) if c1 is not None else None
            g["topic_cluster"] = int(c2.topic_cluster) if c2 is not None else None
            mo = monthly[(monthly["creator"] == r.creator) & (monthly["genre"] == genre)].sort_values("month")
            g["monthly"] = [{"month": m.month, "n_titles": int(m.n_titles), "partial": bool(m.partial_month),
                             **{f: _num(getattr(m, f + "_controlled")) for f in fcols}, **{h: _num(getattr(m, h)) for h in HOOKS}} for m in mo.itertuples()]
            e = eng[(eng["creator"] == r.creator) & (eng["genre"] == genre)]
            g["engagement"] = [{"predictor": x.predictor, "coef_per_sd": _num(x.coef_per_sd), "se": _num(x.se_hc3), "p": _num(x.p)} for x in e.itertuples()] if len(e) else None
            g["engagement_n"] = int(e["n"].iloc[0]) if len(e) else None
            g["engagement_r2"] = _num(e["r2"].iloc[0]) if len(e) else None
            h = _rec(hits, creator=r.creator, genre=genre)
            g["hits"] = {"n_videos": int(h.n_videos), "gini": _num(h.gini), "top10_share": _num(h.top10_share), "top1_share": _num(h.top1_share),
                         "alpha": _num(h.alpha), "xmin": _num(h.xmin), "lr_vs_lognormal": _num(h.lr_vs_lognormal), "lr_p": _num(h.lr_p),
                         "powerlaw_like": bool(h.powerlaw_like)} if h is not None else None
            f = _rec(fc, creator=r.creator, genre=genre)
            if f is not None:
                g["diversity"] = {"heaps_beta_1500": _num(f.get("heaps_beta_1500")), "zipf_1500": _num(f.get("zipf_1500")),
                                  "formulaic_p100": _num(f.get("formulaic_p100")), "n_chars_mean": _num(f.get("n_chars_mean")),
                                  "n_tokens_mean": _num(f.get("n_tokens_mean"))}
            ar = extra["arousal_index.csv"]
            if ar is not None:
                a = _rec(ar, creator=r.creator, genre=genre)
                if a is not None:
                    g["arousal"] = {"index": _num(a.arousal_index), "rank": _num(a.get("rank_in_genre")), "percentile": _num(a.get("percentile_in_genre")),
                                    "caps_share": _num(a.caps_share), "exclamations": _num(a.exclamations), "power_words": _num(a.power_words), "emoji": _num(a.emoji), "vader_intensity": _num(a.vader_intensity)}
            cp = extra["caps_profile.csv"]
            if cp is not None:
                c_ = _rec(cp, creator=r.creator, genre=genre)
                if c_ is not None:
                    g["caps_profile"] = {k: _num(c_[k]) for k in ("all_caps", "selective_caps", "title_case", "sentence_case", "mixed_other", "short_other")}
            card["genres"][genre] = g
        kw = extra["signature_keywords.csv"]
        if kw is not None:
            k_ = kw[kw["creator"] == r.creator].sort_values("rank")
            card["signature_keywords"] = [{"word": x.word, "z": _num(x.z), "count": int(x.count_creator)} for x in k_.itertuples()]
        lb = extra["leaning_by_creator.csv"]
        if lb is not None:
            l_ = _rec(lb, creator=r.creator)
            if l_ is not None:
                cols = [c for c in lb.columns if c.startswith("label_") and c.endswith("_score")]
                def _nm(c):
                    c = c.replace("label_", "").replace("_score", "")
                    return ("Claude " + c.replace("claude_code_", "").replace("_", " ").title()) if c.startswith("claude_code_") else c.replace("_", ":", 1).replace("_", ".")
                composition = {_nm(c): {"left": _num(l_[c[:-6] + "_left"]), "neither": _num(l_[c[:-6] + "_neither"]), "right": _num(l_[c[:-6] + "_right"]), "score": _num(l_[c])} for c in cols}
                card["leaning"] = {"composition": composition, "judge": _nm(str(l_.get("judge_of_record", ""))),"mean_score": _num(l_.mean_score), "implied_side": l_.implied_side, "n_titles": int(l_.n_titles),
                                   "consensus_neither": _num(l_.get("consensus_neither")),
                                   "judge_score": _num(l_.get("judge_score")), "judge_side": l_.get("judge_side"),
                                   **{c.replace("label_", "").replace("_score", ""): _num(l_[c]) for c in cols}}
        creators[r.creator] = card
    data = {"generated": utc_now(), "factors": {f: {"name": names[f].get("name") or names[f]["auto"], "auto": names[f]["auto"]} for f in fcols},
            "groups": [g for g in list(GROUPS) + ["unscored"] if g in set(creators_tbl["group"])], "group_medians": group_med, "hooks": HOOKS, "formats": FORMATS, "months": MONTHS,
            "topic_labels": {int(t.topic_id): {"label": t.label, "political": bool(t.political)} for t in labels.itertuples()},
            "maps": {"style": {genre: [{"creator": m.creator, "group": m.group, "x": _num(m.x), "y": _num(m.y), "cluster": int(m.style_cluster)} for m in map_s[map_s["genre"] == genre].itertuples()] for genre in GENRES},
                     "topic": {genre: [{"creator": m.creator, "group": m.group, "x": _num(m.x), "y": _num(m.y), "cluster": int(m.topic_cluster)} for m in map_t[map_t["genre"] == genre].itertuples()] for genre in GENRES}},
            "creators": creators}
    return data


def main(argv: Optional[Sequence[str]] = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.parse_args(argv)
    with stage_timer("report_data") as info:
        data = build()
        REPORTS_DIR.mkdir(parents=True, exist_ok=True)
        CARDS_JSON.write_text(json.dumps(data, ensure_ascii=False))
        info["creators"] = len(data["creators"])
        print(f"cards.json: {len(data['creators'])} creators, {CARDS_JSON.stat().st_size / 1e6:.1f} MB")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
