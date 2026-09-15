"""Static figures for the sectioned write-up (pipeline_titles/reports/figures/*.png).

Every figure is drawn from the analysis tables at render time. Lanes are folded
into six families for colour (thirteen lanes cannot be told apart by hue) and
named in full in labels and legends. Palette: the validated reference palette of
the dataviz method (blue, orange, aqua, yellow, magenta, green; sequential blue;
diverging blue <-> red with a grey midpoint).

    python -m pipeline_titles.figures
"""

from __future__ import annotations

import json
import re

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker
import numpy as np
import pandas as pd
from matplotlib.colors import LinearSegmentedColormap, TwoSlopeNorm

from pipeline_titles.common import ANALYSIS_DIR as A, MONTHS, REPORTS_DIR, gini as gini_fn
from pipeline_titles.report_sections import LANE_LABEL, lane as lane_label

FIG = REPORTS_DIR / "figures"
CAT = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4", "#008300", "#4a3aa7", "#e34948"]
INK, INK2, MUTED, GRID, SURFACE = "#0b0b0b", "#52514e", "#8a8983", "#e6e5e1", "#fcfcfb"
FAMILY_OF = {
    "left_commentary": "left commentary", "right_commentary": "right commentary", "centrist_heterodox": "other commentary",
    "legal_institutional": "other commentary", "humour_satire": "other commentary", "explainer_geopolitics": "other commentary",
    "us_legacy_tv": "news outlets", "wire_international": "news outlets", "us_press_print_digital": "news outlets",
    "right_tv_network": "news outlets", "independent_digital_news": "independent news", "streamer_reaction": "streamers",
    "interview_podcast": "interview podcasts",
}
FAMILIES = ["left commentary", "right commentary", "news outlets", "independent news", "streamers", "interview podcasts", "other commentary"]
FAM_COLOR = dict(zip(FAMILIES, CAT[:7]))
DIV = LinearSegmentedColormap.from_list("div", ["#0d366b", "#3987e5", "#f0efec", "#e66767", "#8f1d1d"])
SEQ = LinearSegmentedColormap.from_list("seq", ["#f4f8fd", "#cde2fb", "#6da7ec", "#256abf", "#0d366b"])

plt.rcParams.update({"font.family": "sans-serif", "font.size": 9, "axes.edgecolor": GRID, "axes.labelcolor": INK2, "xtick.color": INK2,
                     "ytick.color": INK2, "axes.titlecolor": INK, "axes.titlesize": 10.5, "axes.titleweight": "bold", "axes.titlelocation": "left",
                     "axes.spines.top": False, "axes.spines.right": False, "axes.grid": True, "grid.color": GRID, "grid.linewidth": 0.6,
                     "axes.axisbelow": True, "figure.facecolor": SURFACE, "axes.facecolor": SURFACE, "savefig.dpi": 150, "legend.frameon": False,
                     "legend.fontsize": 8.5})


def rd(name):
    return pd.read_csv(A / name)


SHORT = {"F1": "tone: positive vs outrage", "F2": "clause headline", "F3": "LIVE / labelled", "F4": "stream talk", "F5": "question / explainer",
         "F6": "person-centred", "F7": "news prose", "F8": "numbers / dates", "F9": "ALL CAPS", "F10": "quoted speech", "F11": "long, upbeat", "F12": "modal / future"}


def names_of():
    """Short factor names for tick labels (hand-set; falls back to factor_names.json)."""
    n = json.loads((A / "factor_names.json").read_text())
    return {k: SHORT.get(k, (v.get("name") or v["auto"]).split(" (")[0]) for k, v in n.items()}


def save(fig, name, note=None):
    if note:
        fig.text(0.01, 0.005, note, fontsize=7.5, color=MUTED, ha="left", va="bottom")
    fig.savefig(FIG / name, bbox_inches="tight", facecolor=SURFACE)
    plt.close(fig)


def hbar(ax, labels, values, color, fmt="{:.2f}", direct=True):
    y = np.arange(len(labels))
    ax.barh(y, values, color=color, height=0.62)
    ax.set_yticks(y, labels)
    ax.invert_yaxis()
    ax.grid(axis="y", visible=False)
    if direct:
        for yi, v in zip(y, values):
            ax.text(v, yi, " " + fmt.format(v), va="center", ha="left", fontsize=8, color=INK2)


# --------------------------------------------------------------------------- #
def fig_corpus():
    lanes = rd("lanes.csv"); summ = rd("creator_genre_summary.csv")
    per = summ.merge(lanes[["creator", "lane"]], on="creator").groupby("lane").agg(creators=("creator", "nunique"), titles=("n_unique", "sum")).reset_index()
    per["label"] = per.lane.map(lane_label); per = per.sort_values("titles", ascending=False)
    fig, axes = plt.subplots(1, 2, figsize=(10, 4.2))
    hbar(axes[0], per.label, per.titles / 1000, CAT[0], fmt="{:.0f}k")
    axes[0].set_title("Unique titles per lane (thousands)"); axes[0].set_xlabel("")
    hbar(axes[1], per.label, per.creators, CAT[1], fmt="{:.0f}")
    axes[1].set_title("Creators per lane")
    fig.suptitle("The corpus is dominated by a few news lanes; commentary has the most creators", x=0.01, ha="left", fontsize=11, fontweight="bold", color=INK)
    fig.tight_layout(rect=(0, 0.02, 1, 0.95))
    save(fig, "01_corpus_by_lane.png", "Unique titles within creator x genre; every lane statistic later is a mean of creators, not a pool of titles.")

    fig, ax = plt.subplots(figsize=(8, 3.6))
    sizes = summ.n_unique.to_numpy()
    bins = np.logspace(0, np.log10(sizes.max() + 1), 30)
    ax.hist(sizes[summ.genre == "videos"], bins=bins, color=CAT[0], alpha=0.9, label="videos (edited uploads)")
    ax.hist(sizes[summ.genre == "streams"], bins=bins, color=CAT[1], alpha=0.8, label="streams (live VODs)")
    ax.set_xscale("log"); ax.axvline(50, color=INK, lw=1, ls="--"); ax.axvline(2500, color=INK, lw=1, ls=":")
    ax.text(50, ax.get_ylim()[1] * 0.95, " low-n below 50", va="top", fontsize=8, color=INK2); ax.text(2500, ax.get_ylim()[1] * 0.95, " balanced cap 2,500", va="top", fontsize=8, color=INK2)
    ax.set_xlabel("unique titles in the creator x genre group (log scale)"); ax.set_ylabel("groups"); ax.legend()
    ax.set_title("Group sizes span three orders of magnitude")
    fig.tight_layout(); save(fig, "01_group_sizes.png")


def fig_topics():
    tl = rd("topic_labels.csv"); bl = rd("topic_by_lane.csv"); tt = rd("topic_timeline.csv"); pol = rd("creator_political_share.csv")
    share = bl.groupby("topic_id").mean_creator_share.mean().rename("share")
    top = tl.merge(share, on="topic_id").sort_values("share", ascending=False).head(15)
    fig, ax = plt.subplots(figsize=(9, 5))
    colors = [CAT[0] if p else CAT[3] for p in top.political]
    hbar(ax, top.label, top.share * 100, colors, fmt="{:.1f}%")
    ax.set_title("The fifteen largest topics (creator-balanced share of titles)")
    ax.plot([], [], "s", color=CAT[0], label="political"); ax.plot([], [], "s", color=CAT[3], label="non-political"); ax.legend(loc="lower right")
    ax.set_xlabel("mean over lanes of the mean creator share, %")
    fig.tight_layout(); save(fig, "02_top_topics.png", "One war story dominates; the 'Shocking Events and Reactions' topic is content-free exclamation titles.")

    ids = top.topic_id.head(8).tolist()
    fig, axes = plt.subplots(2, 4, figsize=(11, 4.6), sharex=True)
    for ax, t in zip(axes.flat, ids):
        s = tt[tt.topic_id == t].set_index("month").reindex(MONTHS).balanced_share * 100
        ax.plot(range(9), s.to_numpy(), color=CAT[0], lw=2); ax.plot(8, s.iloc[-1], "o", color=SURFACE, mec=CAT[0], mew=1.5, ms=7)
        ax.set_title(tl.set_index("topic_id").loc[t, "label"][:34], fontsize=8.5); ax.set_ylim(0, None)
        ax.set_xticks(range(9), [m[5:] for m in MONTHS], fontsize=7)
    fig.suptitle("Monthly share of the eight largest topics (creator-balanced, %; Sept = 1-14 only, hollow marker)", x=0.01, ha="left", fontsize=11, fontweight="bold", color=INK)
    fig.tight_layout(rect=(0, 0, 1, 0.94)); save(fig, "02_topic_timeline.png")

    pl = pol[pol.n_unique >= 50].groupby("lane").political_share.agg(["mean", "count"]).reset_index().sort_values("mean")
    fig, ax = plt.subplots(figsize=(7.5, 4))
    y = np.arange(len(pl)); ax.hlines(y, 0.7, pl["mean"], color=GRID, lw=2); ax.plot(pl["mean"], y, "o", color=CAT[0], ms=8)
    for yi, (m, c) in enumerate(zip(pl["mean"], pl["count"])):
        ax.text(m + 0.004, yi, f"{m:.0%}  (n={c})", va="center", fontsize=8, color=INK2)
    ax.set_yticks(y, [lane_label(l) for l in pl.lane]); ax.set_xlim(0.7, 1.03); ax.grid(axis="y", visible=False)
    ax.set_xlabel("mean share of a creator's unique titles in political topics"); ax.set_title("Political share by lane: high everywhere, lowest in news")
    fig.tight_layout(); save(fig, "02_political_share_by_lane.png", "The political tag is broad (212 of 236 topics); it separates lanes only at the bottom.")


def fig_dimensions():
    names = names_of(); load = rd("factor_loadings.csv").set_index("feature"); fcols = [c for c in load.columns if re.fullmatch(r"F\d+", c)]
    L = load[fcols]
    keep = L.index[(L.abs() >= 0.35).any(axis=1)]
    L = L.loc[keep]
    order = []
    for f in fcols:
        order += [i for i in L[f].abs().sort_values(ascending=False).index if i not in order and abs(L.loc[i, f]) >= 0.35]
    L = L.loc[order]
    fig, ax = plt.subplots(figsize=(8, 0.22 * len(L) + 1.6))
    im = ax.imshow(L.to_numpy(), cmap=DIV, norm=TwoSlopeNorm(0, -1, 1), aspect="auto")
    ax.set_xticks(range(len(fcols)), [f"{f} {names[f]}" for f in fcols], fontsize=7, rotation=35, ha="right"); ax.set_yticks(range(len(L)), [i.replace("_p100", "").replace("_mean", "") for i in L.index], fontsize=7)
    ax.grid(False); ax.set_title("Factor loadings (oblimin; features with |loading| >= 0.35)")
    cb = fig.colorbar(im, ax=ax, fraction=0.03, pad=0.02); cb.set_label("loading")
    fig.tight_layout(); save(fig, "03_loadings_heatmap.png")

    dims = rd("dimensions.csv"); ok = dims[(~dims.low_n) & (dims.genre == "videos")]
    lm = ok.groupby("lane").agg(**{f: (f + "_controlled", "median") for f in fcols}); lm.index = [lane_label(l) for l in lm.index]
    fig, ax = plt.subplots(figsize=(9, 4.6))
    v = max(abs(lm.to_numpy()).max(), 0.5)
    im = ax.imshow(lm.to_numpy(), cmap=DIV, norm=TwoSlopeNorm(0, -v, v), aspect="auto")
    ax.set_xticks(range(len(fcols)), [f"{f} {names[f]}" for f in fcols], fontsize=7, rotation=35, ha="right"); ax.set_yticks(range(len(lm)), lm.index, fontsize=8)
    for i in range(lm.shape[0]):
        for j in range(lm.shape[1]):
            ax.text(j, i, f"{lm.iloc[i, j]:+.1f}", ha="center", va="center", fontsize=6.5, color=INK if abs(lm.iloc[i, j]) < v * 0.6 else "white")
    ax.grid(False); ax.set_title("Lane medians of topic-controlled scores (edited uploads)")
    fig.colorbar(im, ax=ax, fraction=0.03, pad=0.02).set_label("median score")
    fig.tight_layout(); save(fig, "03_lane_medians_heatmap.png", "Rows are lanes, columns the twelve factors; blue = low, red = high on that factor.")

    vc = rd("validation_creator_level.csv"); piv = vc[vc.score == "raw"].pivot(index="llm", columns="factor", values="spearman_r")[fcols]
    piv = piv.loc[["sensational", "critical", "analytical", "educational", "conversational", "humor", "curiosity_gap", "outrage"]]
    fig, ax = plt.subplots(figsize=(9, 3.6))
    im = ax.imshow(piv.to_numpy(), cmap=DIV, norm=TwoSlopeNorm(0, -0.8, 0.8), aspect="auto")
    ax.set_xticks(range(len(fcols)), [f"{f} {names[f]}" for f in fcols], fontsize=7, rotation=35, ha="right"); ax.set_yticks(range(len(piv)), piv.index, fontsize=8)
    for i in range(piv.shape[0]):
        for j in range(piv.shape[1]):
            ax.text(j, i, f"{piv.iloc[i, j]:+.2f}", ha="center", va="center", fontsize=6.5, color=INK if abs(piv.iloc[i, j]) < 0.5 else "white")
    ax.grid(False); ax.set_title("LLM ratings vs factor scores, creator level (Spearman r)")
    fig.colorbar(im, ax=ax, fraction=0.03, pad=0.02).set_label("r")
    fig.tight_layout(); save(fig, "03_candidate_correlations.png", "Sensational, critical and analytical all land on F1; conversational and humour on nothing.")

    tcs = rd("topic_control_summary.csv"); rt = rd("validation_retest.csv")
    fig, axes = plt.subplots(1, 2, figsize=(10, 3.8))
    x = np.arange(len(tcs)); w = 0.38
    axes[0].bar(x - w / 2, tcs.title_level_r2_topic, w, color=CAT[0], label="title level"); axes[0].bar(x + w / 2, tcs.creator_level_r2_topic, w, color=CAT[1], label="creator level")
    axes[0].set_xticks(x, tcs.factor); axes[0].set_ylabel("share of variance explained by topic"); axes[0].legend(); axes[0].grid(axis="x", visible=False)
    axes[0].set_title("How much of each factor is topic")
    r = rt[rt.dimension.isin(["sensational", "critical", "analytical", "educational", "conversational"])]
    hbar(axes[1], r.dimension, r.weighted_kappa, CAT[0]); axes[1].set_xlim(0, 1); axes[1].set_title("Rater test-retest (quadratic-weighted kappa, n = 300)")
    fig.tight_layout(); save(fig, "03_topic_control_and_retest.png")


def fig_formats():
    sh = rd("format_hook_shares.csv"); ln = sh[sh.level == "lane_mean_of_creators"]
    fmts = ["question", "breaking_live", "episode_show", "interview_guest", "reaction", "confrontation", "howto_explainer", "listicle"]
    fig, axes = plt.subplots(1, 2, figsize=(10, 4.2), sharey=False)
    for ax, g in zip(axes, ["videos", "streams"]):
        d = ln[ln.genre == g].sort_values("outrage")
        y = np.arange(len(d)); ax.hlines(y, 0, d.outrage, color=GRID, lw=2); ax.plot(d.outrage, y, "o", color=CAT[1], ms=8)
        for yi, (v, n) in enumerate(zip(d.outrage, d.n_creators)):
            ax.text(v + 0.012, yi, f"{v:.0%} (n={int(n)})", va="center", fontsize=7.5, color=INK2)
        ax.set_yticks(y, [lane_label(l) for l in d.lane], fontsize=8); ax.set_xlim(0, 1.02); ax.grid(axis="y", visible=False)
        ax.set_title(f"Outrage-frame share, {g}"); ax.set_xlabel("mean over creators of the share of titles the classifier flags")
    fig.tight_layout(); save(fig, "04_outrage_by_lane.png", "n = ranked creators in the lane.")

    d = ln[ln.genre == "videos"].set_index("lane")[fmts]; d.index = [lane_label(l) for l in d.index]
    fig, ax = plt.subplots(figsize=(8.5, 4.4))
    im = ax.imshow(d.to_numpy(), cmap=SEQ, vmin=0, vmax=0.6, aspect="auto")
    ax.set_xticks(range(len(fmts)), fmts, fontsize=8, rotation=20, ha="right"); ax.set_yticks(range(len(d)), d.index, fontsize=8)
    for i in range(d.shape[0]):
        for j in range(d.shape[1]):
            ax.text(j, i, f"{d.iloc[i, j]:.0%}", ha="center", va="center", fontsize=7, color=INK if d.iloc[i, j] < 0.35 else "white")
    ax.grid(False); ax.set_title("Structural formats by lane (share of titles, edited uploads)")
    fig.tight_layout(); save(fig, "04_formats_heatmap.png")


def fig_landscape():
    ms = rd("map_style.csv"); mt = rd("map_topic.csv"); cc = rd("cluster_comparison.csv"); coh = rd("lane_style_cohesion.csv"); ent = rd("entities_top.csv"); st = rd("shared_titles.csv")
    label_set = {"@HasanAbi", "@BenShapiro", "@FoxNews", "@CNN", "@MeidasTouch", "@TuckerCarlson", "@joerogan", "@Reuters", "@destiny", "@TimcastIRL",
                 "@BBCNews", "@TheYoungTurks", "@LastWeekTonight", "@nytimes", "@RSBN", "@LegalEagle", "@CaspianReport", "@bennyjohnson", "@briantylercohen", "@PBDPodcast"}
    for df, name, title, note in ((ms, "05_style_map.png", "Style space: PCA of topic-controlled factor scores (edited uploads)", "Each point is a creator; colour is its lane family. Lanes are scattered through the space."),
                                  (mt, "05_topic_map.png", "Topic space: MDS of Jensen-Shannon distances between topic mixes (edited uploads)", "Distance = how different two creators' topic mixes are.")):
        d = df[df.genre == "videos"].copy(); d["family"] = d.lane.map(FAMILY_OF)
        fig, ax = plt.subplots(figsize=(9, 7))
        for fam in FAMILIES:
            s = d[d.family == fam]
            ax.scatter(s.x, s.y, s=34, color=FAM_COLOR[fam], edgecolor=SURFACE, linewidth=0.8, alpha=0.9, label=f"{fam} ({len(s)})")
        for r in d[d.creator.isin(label_set)].itertuples():
            ax.annotate(r.creator, (r.x, r.y), fontsize=7.5, color=INK, xytext=(4, 3), textcoords="offset points")
        ax.legend(loc="best", markerscale=1.1); ax.set_xticks([]); ax.set_yticks([]); ax.grid(False); ax.set_title(title)
        fig.tight_layout(); save(fig, name, note)

    fig, axes = plt.subplots(1, 2, figsize=(10, 4))
    c = cc.copy(); c["run"] = c.genre + ", " + c.titles
    x = np.arange(len(c)); w = 0.27
    axes[0].bar(x - w, c.ari_style_vs_lane, w, color=CAT[0], label="style vs lane"); axes[0].bar(x, c.ari_topic_vs_lane, w, color=CAT[1], label="topic vs lane"); axes[0].bar(x + w, c.ari_style_vs_topic, w, color=CAT[2], label="style vs topic")
    axes[0].set_xticks(x, c.run, fontsize=8); axes[0].axhline(0, color=INK, lw=0.8); axes[0].set_ylim(-0.1, 0.5); axes[0].set_ylabel("adjusted Rand index (1 = identical, 0 = chance)"); axes[0].legend(); axes[0].grid(axis="x", visible=False)
    axes[0].set_title("Clusterings barely agree with lanes or with each other")
    cv = coh[(coh.titles == "all") & (coh.genre == "videos")].sort_values("cohesion_ratio", ascending=False)
    hbar(axes[1], [lane_label(l) for l in cv.lane], cv.cohesion_ratio, [CAT[0] if v < 1 else CAT[1] for v in cv.cohesion_ratio])
    axes[1].axvline(1, color=INK, lw=1, ls="--"); axes[1].set_xlim(0, 1.25); axes[1].set_title("Lane cohesion in style space (within / between distance)")
    axes[1].set_xlabel("below 1 = lane-mates closer than strangers")
    fig.tight_layout(); save(fig, "05_lanes_vs_style.png")

    p = ent[ent.kind == "person"].head(25).sort_values("outrage_ratio")
    fig, ax = plt.subplots(figsize=(8, 6.5))
    colors = [CAT[1] if v >= 1 else CAT[0] for v in p.outrage_ratio]
    hbar(ax, p.entity, p.outrage_ratio, colors, fmt="{:.2f}x")
    ax.axvline(1, color=INK, lw=1, ls="--"); ax.set_xlim(0, 1.9); ax.set_xlabel("outrage-frame share of titles naming the person / corpus share")
    ax.set_title("Who gets the outrage frame: the 25 most-named people")
    fig.tight_layout(); save(fig, "05_entities_outrage.png", "Creator-balanced counts; people keyed by surname. Crime-story names get the least outrage framing, MAGA-era officials the most.")

    cross = st[~st.same_organisation_only].head(20)
    fig, ax = plt.subplots(figsize=(8, 5.5))
    hbar(ax, cross.example, cross.n_creators, CAT[0], fmt="{:.0f}")
    ax.set_xlabel("creators from different organisations using the title verbatim"); ax.set_title("The most shared verbatim titles")
    fig.tight_layout(); save(fig, "05_shared_titles.png")


def fig_drift():
    names = names_of(); dl = rd("drift_lane_monthly.csv")
    lanes_ = ["left_commentary", "right_commentary", "streamer_reaction", "independent_digital_news", "interview_podcast", "legal_institutional",
              "centrist_heterodox", "us_legacy_tv", "us_press_print_digital", "wire_international", "right_tv_network", "humour_satire"]
    for col, name, title in (("outrage", "06_drift_outrage.png", "Outrage-frame share by month (edited uploads; mean of creators)"),
                             ("F1_controlled", "06_drift_tone.png", "Tone factor F1 (positive vs outrage, topic-controlled) by month"),
                             ("F9_controlled", "06_drift_caps.png", "ALL-CAPS factor F9 by month")):
        allm = dl[(dl.genre == "videos") & (dl.lane == "ALL (mean of creators)")].set_index("month").reindex(MONTHS)[col]
        fig, axes = plt.subplots(3, 4, figsize=(11, 6.4), sharex=True, sharey=True)
        for ax, l in zip(axes.flat, lanes_):
            s = dl[(dl.genre == "videos") & (dl.lane == l)].set_index("month").reindex(MONTHS)[col]
            n = dl[(dl.genre == "videos") & (dl.lane == l)].n_creators.max()
            ax.plot(range(9), allm.to_numpy(), color=MUTED, lw=1.2, ls="--", label="all creators")
            ax.plot(range(9), s.to_numpy(), color=FAM_COLOR[FAMILY_OF[l]], lw=2, label=lane_label(l)); ax.plot(8, s.iloc[-1], "o", color=SURFACE, mec=FAM_COLOR[FAMILY_OF[l]], mew=1.5, ms=7)
            ax.set_title(f"{lane_label(l)} (n={int(n) if pd.notna(n) else '?'})", fontsize=8.5); ax.set_xticks(range(9), [m[5:] for m in MONTHS], fontsize=7)
        axes[0, 0].legend(loc="lower left", fontsize=7)
        fig.suptitle(title + "; grey dashed = all creators; hollow = Sept 1-14", x=0.01, ha="left", fontsize=11, fontweight="bold", color=INK)
        fig.tight_layout(rect=(0, 0, 1, 0.95)); save(fig, name)


def fig_views():
    names = names_of(); ec = rd("engagement_coefficients.csv"); es = rd("engagement_summary.csv"); hc = rd("hit_concentration.csv"); prep = None
    ev = ec[ec.genre == "videos"]
    order = es[(es.lane == "ALL") & (es.genre == "videos")].sort_values("median_coef_per_sd", ascending=False).predictor.tolist()
    fig, ax = plt.subplots(figsize=(10, 4.6))
    data = [ev[ev.predictor == p].coef_per_sd.clip(-0.3, 0.3).to_numpy() for p in order]
    bp = ax.boxplot(data, vert=True, widths=0.55, showfliers=False, patch_artist=True, medianprops=dict(color=INK, lw=1.5), boxprops=dict(facecolor="#cde2fb", edgecolor=CAT[0]), whiskerprops=dict(color=CAT[0]), capprops=dict(color=CAT[0]))
    rng = np.random.RandomState(0)
    for i, d in enumerate(data, start=1):
        ax.plot(i + rng.uniform(-0.18, 0.18, len(d)), d, ".", color=CAT[0], alpha=0.25, ms=4)
    ax.axhline(0, color=INK, lw=0.8); ax.set_xticks(range(1, len(order) + 1), [f"{p} {names[p]}" if p in names else p for p in order], fontsize=7, rotation=35, ha="right")
    ax.set_ylabel("log views per within-creator SD"); ax.set_title(f"Within-creator effect of each title feature on views ({ev.groupby('creator').ngroups} video channels; month + topic controls)")
    fig.tight_layout(); save(fig, "07_engagement_coefficients.png", "One point per channel (clipped at +-0.3). Only outrage sits clearly above zero.")

    byl = es[(es.lane != "ALL") & (es.genre == "videos") & (es.predictor == "outrage")].sort_values("median_coef_per_sd")
    fig, ax = plt.subplots(figsize=(7.5, 4))
    y = np.arange(len(byl)); ax.hlines(y, 0, byl.median_coef_per_sd, color=GRID, lw=2); ax.plot(byl.median_coef_per_sd, y, "o", color=CAT[1], ms=8)
    for yi, r in enumerate(byl.itertuples()):
        ax.text(r.median_coef_per_sd + 0.004, yi, f"{r.median_coef_per_sd:+.3f}  ({r.share_positive:.0%} positive, n={int(r.n_creators)})", va="center", fontsize=7.5, color=INK2)
    ax.set_yticks(y, [lane_label(l) for l in byl.lane], fontsize=8); ax.axvline(0, color=INK, lw=0.8); ax.set_xlim(-0.02, 0.3); ax.grid(axis="y", visible=False)
    ax.set_xlabel("median outrage coefficient (log views per SD)"); ax.set_title("The outrage effect is largest where outrage is rare")
    fig.tight_layout(); save(fig, "07_outrage_effect_by_lane.png")

    hv = hc[hc.genre == "videos"].copy(); hv["label"] = hv.lane.map(lane_label)
    order_l = hv.groupby("label").gini.median().sort_values().index.tolist()
    fig, ax = plt.subplots(figsize=(9, 4.6))
    rng = np.random.RandomState(1)
    for i, l in enumerate(order_l):
        s = hv[hv.label == l]
        ax.plot(s.gini, i + rng.uniform(-0.2, 0.2, len(s)), "o", color=FAM_COLOR[FAMILY_OF[s.lane.iloc[0]]], alpha=0.7, ms=5)
        ax.plot([s.gini.median()] * 2, [i - 0.3, i + 0.3], color=INK, lw=2)
    ax.set_yticks(range(len(order_l)), order_l, fontsize=8); ax.set_xlabel("Gini coefficient of views across the channel's videos (black bar = lane median)"); ax.grid(axis="y", visible=False)
    ax.set_title("Hit concentration by lane: streamers spread views evenly, news outlets live on hits")
    fig.tight_layout(); save(fig, "07_gini_by_lane.png")

    fig, axes = plt.subplots(1, 2, figsize=(10, 4.2))
    picks = ["@Vaush", "@BelleRanch", "@briantylercohen", "@BenShapiro", "@CNN", "@Reuters", "@wethefifth"]
    pre = pd.read_parquet(A / "titles_prepared.parquet", columns=["creator", "genre", "view_count", "has_views"])
    for i, c in enumerate(picks):
        v = np.sort(pre[(pre.creator == c) & (pre.genre == "videos") & pre.has_views].view_count.to_numpy())
        if len(v) < 100:
            continue
        cum = np.cumsum(v) / v.sum(); xs = np.arange(1, len(v) + 1) / len(v)
        axes[0].plot(xs, cum, lw=2, color=CAT[i % 8], label=f"{c} (Gini {gini_fn(v):.2f})")
    axes[0].plot([0, 1], [0, 1], color=MUTED, lw=1, ls="--"); axes[0].set_xlabel("share of videos (lowest views first)"); axes[0].set_ylabel("share of views"); axes[0].legend(fontsize=7.5)
    axes[0].set_title("Lorenz curves: how unequal a channel's views are")
    axes[1].hist(hv.lr_vs_lognormal.dropna(), bins=30, color=CAT[0]); axes[1].axvline(0, color=INK, lw=1)
    axes[1].set_xlabel("normalised log-likelihood ratio, power law vs lognormal (> 0 favours power law)"); axes[1].set_ylabel("channels")
    axes[1].set_title(f"Tails are lognormal, not power-law ({int(hv.powerlaw_like.sum())} of {len(hv)} channels pass)")
    fig.tight_layout(); save(fig, "07_lorenz_and_tails.png")


def fig_zipf_views():
    hc = rd("hit_concentration.csv"); hv = hc[hc.genre == "videos"].copy()
    pre = pd.read_parquet(A / "titles_prepared.parquet", columns=["creator", "genre", "view_count", "has_views"])
    picks = ["@FoxNews", "@CNN", "@Reuters", "@BenShapiro", "@briantylercohen", "@HasanAbi", "@Vaush", "@BelleRanch"]
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.6))
    ax = axes[0]
    for i, c in enumerate(picks):
        v = np.sort(pre[(pre.creator == c) & (pre.genre == "videos") & pre.has_views].view_count.to_numpy())[::-1]
        v = v[v > 0]
        if len(v) < 100:
            continue
        r = np.arange(1, len(v) + 1)
        ax.plot(r, v / v[0], lw=1.8, color=CAT[i % 8], label=f"{c} (n={len(v):,}, slope {float(hv.loc[hv.creator == c, 'zipf_views_all'].iloc[0]):.2f})")
    ax.set_xscale("log"); ax.set_yscale("log"); ax.set_xlabel("rank of the video within the channel (1 = most viewed)"); ax.set_ylabel("views / views of the channel's top video")
    ax.legend(fontsize=7.5); ax.set_title("Rank-size (Zipf) curves of views, eight channels")
    ax = axes[1]
    hv["label"] = hv.lane.map(lane_label); order = hv.groupby("label").zipf_views_all.median().sort_values().index.tolist()
    rng = np.random.RandomState(2)
    for i, l in enumerate(order):
        s = hv[hv.label == l]
        ax.plot(s.zipf_views_all, i + rng.uniform(-0.2, 0.2, len(s)), "o", color=FAM_COLOR[FAMILY_OF[s.lane.iloc[0]]], alpha=0.7, ms=5)
        ax.plot([s.zipf_views_all.median()] * 2, [i - 0.3, i + 0.3], color=INK, lw=2)
    ax.set_yticks(range(len(order)), order, fontsize=8); ax.grid(axis="y", visible=False)
    ax.set_xlabel("Zipf slope of views (log views vs log rank, all videos; black bar = lane median)")
    ax.set_title("Zipf slope by lane: steeper = views fall off faster down the ranking")
    fig.tight_layout(); save(fig, "07_zipf_views.png", "Curves bend down at the tail on log-log axes: lognormal rather than straight-line power-law behaviour.")


def fig_profiles():
    from pipeline_titles.textstats import CAPS_STYLES
    ar = rd("arousal_index.csv"); a = ar[(ar.genre == "videos") & (~ar.low_n)].sort_values("arousal_index", ascending=False).reset_index(drop=True)
    half = int(np.ceil(len(a) / 2))
    fig, axes = plt.subplots(1, 2, figsize=(12, 0.115 * half + 1.2))
    for ax, part in zip(axes, (a.iloc[:half], a.iloc[half:])):
        y = np.arange(len(part))
        ax.hlines(y, 0, part.arousal_index, color=GRID, lw=1.5)
        ax.scatter(part.arousal_index, y, s=18, color=[FAM_COLOR[FAMILY_OF[l]] for l in part.lane], zorder=3)
        ax.set_yticks(y, [f"{c}" for c in part.creator], fontsize=5.5); ax.invert_yaxis(); ax.set_xlim(0, 1); ax.grid(axis="y", visible=False)
        ax.tick_params(axis="x", labelsize=7)
    for fam in FAMILIES:
        axes[0].plot([], [], "o", color=FAM_COLOR[fam], label=fam)
    axes[0].legend(loc="lower right", fontsize=7)
    fig.suptitle(f"Arousal index, all {len(a)} ranked channels (edited uploads), highest first", x=0.01, ha="left", fontsize=11, fontweight="bold", color=INK)
    fig.tight_layout(rect=(0, 0, 1, 0.97)); save(fig, "12_arousal_ranked.png", "0-1 composite of ALL-CAPS share, exclamation marks, power words, emoji and VADER intensity; colour = lane family.")

    fig, ax = plt.subplots(figsize=(9, 4.6))
    a["label"] = a.lane.map(lane_label); order = a.groupby("label").arousal_index.median().sort_values().index.tolist()
    rng = np.random.RandomState(3)
    for i, l in enumerate(order):
        sub = a[a.label == l]
        ax.plot(sub.arousal_index, i + rng.uniform(-0.2, 0.2, len(sub)), "o", color=FAM_COLOR[FAMILY_OF[sub.lane.iloc[0]]], alpha=0.7, ms=5)
        ax.plot([sub.arousal_index.median()] * 2, [i - 0.3, i + 0.3], color=INK, lw=2)
    ax.set_yticks(range(len(order)), order, fontsize=8); ax.set_xlim(0, 1); ax.grid(axis="y", visible=False); ax.set_xlabel("arousal index (black bar = lane median)")
    ax.set_title("Arousal index by lane")
    fig.tight_layout(); save(fig, "12_arousal_by_lane.png")

    cp = rd("caps_profile.csv"); c = cp[(cp.genre == "videos") & (~cp.low_n)].sort_values("caps_any", ascending=False)
    labels = ["ALL CAPS", "selective CAPS", "Title Case", "Sentence case", "mixed / other", "short / other"]
    cols = ["#e34948", "#eb6834", "#2a78d6", "#1baf7a", "#8a8983", "#d6d5d0"]
    for name, sub, title in (("11_caps_profile_top.png", c.head(45), "Capitalisation profile: the 45 channels using most ALL-CAPS or selective CAPS (edited uploads)"),
                             ("11_caps_profile_bottom.png", c.tail(30), "Capitalisation profile: the 30 channels using least capitals")):
        fig, ax = plt.subplots(figsize=(10, 0.2 * len(sub) + 1.5))
        left = np.zeros(len(sub))
        for lab, col_, style in zip(labels, cols, CAPS_STYLES):
            ax.barh(np.arange(len(sub)), sub[style], left=left, color=col_, height=0.72, label=lab, edgecolor=SURFACE, linewidth=0.6)
            left += sub[style].to_numpy()
        ax.set_yticks(np.arange(len(sub)), sub.creator, fontsize=7); ax.invert_yaxis(); ax.set_xlim(0, 1); ax.grid(axis="y", visible=False)
        ax.xaxis.set_major_formatter(matplotlib.ticker.PercentFormatter(1.0)); ax.legend(ncol=6, loc="upper center", bbox_to_anchor=(0.5, -0.04), fontsize=7.5)
        ax.set_title(title)
        fig.tight_layout(); save(fig, name)
    lm = c.merge(pd.DataFrame(), how="left") if False else c
    lanes_mean = lm.groupby("lane")[CAPS_STYLES].mean().sort_values("all_caps", ascending=False); lanes_mean.index = [lane_label(l) for l in lanes_mean.index]
    fig, ax = plt.subplots(figsize=(9, 4.4))
    left = np.zeros(len(lanes_mean))
    for lab, col_, style in zip(labels, cols, CAPS_STYLES):
        ax.barh(np.arange(len(lanes_mean)), lanes_mean[style], left=left, color=col_, height=0.7, label=lab, edgecolor=SURFACE, linewidth=0.6)
        left += lanes_mean[style].to_numpy()
    ax.set_yticks(np.arange(len(lanes_mean)), lanes_mean.index, fontsize=8); ax.invert_yaxis(); ax.set_xlim(0, 1); ax.grid(axis="y", visible=False)
    ax.xaxis.set_major_formatter(matplotlib.ticker.PercentFormatter(1.0)); ax.legend(ncol=6, loc="upper center", bbox_to_anchor=(0.5, -0.06), fontsize=7.5)
    ax.set_title("Capitalisation profile by lane (mean of creators, edited uploads)")
    fig.tight_layout(); save(fig, "11_caps_profile_by_lane.png")

    tw = rd("top_words.csv").head(20)
    fig, axes = plt.subplots(1, 2, figsize=(10, 5))
    hbar(axes[0], tw.word, tw.balanced_share_of_titles * 100, CAT[0], fmt="{:.1f}%"); axes[0].set_title("Creator-balanced: mean share of a creator's titles containing the word")
    raw = rd("top_words.csv").sort_values("raw_titles", ascending=False).head(20)
    hbar(axes[1], raw.word, raw.raw_pooled_share_of_titles * 100, CAT[1], fmt="{:.1f}%"); axes[1].set_title("Raw pooled: share of all unique titles containing the word")
    fig.suptitle("The twenty most frequent non-stopwords in titles (edited uploads)", x=0.01, ha="left", fontsize=11, fontweight="bold", color=INK)
    fig.tight_layout(rect=(0, 0, 1, 0.95)); save(fig, "11_top_words.png")

    # twins: the closest cross-divide pairs, and how cross-divide distances compare with same-lane ones
    pairs = rd("style_twins.csv").head(20); near = rd("style_twins_nearest.csv")
    fig, axes = plt.subplots(1, 2, figsize=(12, 5.6), gridspec_kw={"width_ratios": [1.35, 1]})
    ax = axes[0]; y = np.arange(len(pairs))
    ax.barh(y, pairs.distance, color=GRID, height=0.6)
    for yi, r in zip(y, pairs.itertuples()):
        ax.text(0.02, yi, r.left_creator, va="center", ha="left", fontsize=7.5, color=CAT[0], fontweight="bold")
        ax.text(r.distance + 0.03, yi, r.right_creator, va="center", ha="left", fontsize=7.5, color=CAT[1], fontweight="bold")
    ax.set_yticks([]); ax.invert_yaxis(); ax.set_xlim(0, pairs.distance.max() + 1.6); ax.grid(axis="y", visible=False)
    ax.set_xlabel(f"distance in z-scored 12-factor style space (median nearest-neighbour distance {np.nanmedian(near.nearest_same_lane_distance):.1f})"); ax.set_title("The twenty closest left (blue) - right (orange) pairs")
    ax = axes[1]
    a_ = np.sort(near.twin_distance.to_numpy()); b_ = np.sort(near.nearest_same_lane_distance.dropna().to_numpy())
    ax.plot(a_, np.arange(1, len(a_) + 1) / len(a_), color=CAT[2], lw=2, label="nearest creator across the divide")
    ax.plot(b_, np.arange(1, len(b_) + 1) / len(b_), color=INK, lw=2, ls="--", label="nearest creator in the same lane")
    ax.set_xlabel("distance to nearest neighbour"); ax.set_ylabel("share of commentary creators"); ax.legend(loc="lower right")
    ax.set_title(f"For {near.twin_closer_than_any_same_lane.mean():.0%} of commentary creators the twin across the divide is closer than any lane-mate")
    fig.tight_layout(); save(fig, "09_twins.png", "Left and right commentary creators only, edited uploads, clip channels excluded.")

    # outrage by lane with CI (strip + CI)
    oc = rd("outrage_by_lane_ci.csv"); sh = rd("format_hook_shares.csv"); cr = sh[(sh.level == "creator") & (~sh.low_n.astype(str).str.lower().eq("true"))]
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.6))
    for ax, g in zip(axes, ("videos", "streams")):
        o = oc[oc.genre == g].sort_values("mean"); y = np.arange(len(o)); rng = np.random.RandomState(4)
        for i, r in enumerate(o.itertuples()):
            v = cr[(cr.lane == r.lane) & (cr.genre == g)].outrage
            ax.plot(v, i + rng.uniform(-0.18, 0.18, len(v)), "o", color=FAM_COLOR[FAMILY_OF[r.lane]], alpha=0.45, ms=4)
            ax.plot([r.ci95_low, r.ci95_high], [i, i], color=INK, lw=2); ax.plot(r.mean, i, "|", color=INK, ms=12, mew=2)
        ax.set_yticks(y, [f"{lane_label(l)} (n={int(n)})" for l, n in zip(o.lane, o.n_creators)], fontsize=8); ax.set_xlim(0, 1); ax.grid(axis="y", visible=False)
        ax.set_title(f"Outrage-frame share by lane, {g}"); ax.set_xlabel("share of a creator's titles (dots = creators; bar = mean with bootstrap 95 % CI)")
    fig.tight_layout(); save(fig, "10_outrage_by_lane_ci.png")


def fig_leaning():
    if not (A / "leaning_by_creator.csv").exists():
        return
    bc = rd("leaning_by_creator.csv"); words = rd("leaning_words.csv"); bl = rd("leaning_by_lane.csv")
    cols = [c for c in bc.columns if c.startswith("label_") and c.endswith("_score")]
    names = {c: c.replace("label_", "").replace("_score", "").replace("_", ":", 1).replace("_", ".") for c in cols}
    fig, axes = plt.subplots(1, 2, figsize=(12, 5.4), gridspec_kw={"width_ratios": [1.15, 1]})
    ax = axes[0]
    if len(cols) >= 2:
        ax.plot([-1, 1], [-1, 1], color=GRID, lw=1); ax.axhline(0, color=GRID, lw=1); ax.axvline(0, color=GRID, lw=1)
        for fam in FAMILIES:
            sub = bc[bc.lane.map(FAMILY_OF) == fam]
            ax.scatter(sub[cols[0]], sub[cols[1]], s=26, color=FAM_COLOR[fam], alpha=0.8, edgecolor=SURFACE, linewidth=0.6, label=fam)
        for r in bc.nlargest(4, "mean_score").itertuples():
            ax.annotate(r.creator, (getattr(r, cols[0]), getattr(r, cols[1])), fontsize=6.5, xytext=(3, 3), textcoords="offset points")
        for r in bc.nsmallest(4, "mean_score").itertuples():
            ax.annotate(r.creator, (getattr(r, cols[0]), getattr(r, cols[1])), fontsize=6.5, xytext=(3, 3), textcoords="offset points")
        ax.set_xlabel(f"{names[cols[0]]} score (right − left) / n"); ax.set_ylabel(f"{names[cols[1]]} score"); ax.legend(fontsize=7.5, loc="upper left")
        r_ = bc[cols[0]].corr(bc[cols[1]], method="spearman")
        ax.set_title(f"Channel scores from the two models (Spearman {r_:.2f})")
    ax = axes[1]
    sc = "judge_score" if "judge_score" in bc.columns else "mean_score"
    jname = bc["judge_of_record"].iloc[0].replace("label_", "").replace("_", ":", 1).replace("_", ".") if "judge_of_record" in bc.columns else "mean of models"
    lm = bc.groupby("lane").agg(v=(sc, "mean"), n=("creator", "size")).reset_index().sort_values("v"); y = np.arange(len(lm)); rng = np.random.RandomState(5)
    for i, r in enumerate(lm.itertuples()):
        sub = bc[bc.lane == r.lane]
        ax.plot(sub[sc], i + rng.uniform(-0.2, 0.2, len(sub)), "o", color=FAM_COLOR[FAMILY_OF[r.lane]], alpha=0.5, ms=4)
        ax.plot([r.v] * 2, [i - 0.3, i + 0.3], color=INK, lw=2)
    ax.set_yticks(y, [f"{lane_label(l)} (n={int(n)})" for l, n in zip(lm.lane, lm.n)], fontsize=8); ax.axvline(0, color=INK, lw=0.8); ax.grid(axis="y", visible=False)
    ax.set_xlabel(f"title-leaning score, judge of record {jname} (−1 left … +1 right); dots = channels, bar = lane mean"); ax.set_title("Title leaning by lane")
    fig.tight_layout(); save(fig, "14_leaning_scores.png")

    w = words[words.model == "consensus"] if (words.model == "consensus").any() else words[words.model == words.model.iloc[0]]
    w = w[(w.count_right + w.count_left) >= 5].copy()
    fig, axes = plt.subplots(1, 2, figsize=(12, 5.6), gridspec_kw={"width_ratios": [1.2, 1]})
    ax = axes[0]
    ax.scatter(w.rank_right, w.rank_left, s=8, color=GRID, alpha=0.8)
    ax.set_xscale("log"); ax.set_yscale("log"); mx = max(w.rank_right.max(), w.rank_left.max()); ax.plot([1, mx], [1, mx], color=INK, lw=0.8, ls="--")
    both = w[(w.count_right > 0) & (w.count_left > 0)]
    lab = pd.concat([both.nlargest(9, "rtd_contribution"), both.nsmallest(9, "rtd_contribution")])
    for r in lab.itertuples():
        col_ = CAT[1] if r.rtd_contribution > 0 else CAT[0]
        ax.scatter([r.rank_right], [r.rank_left], s=22, color=col_, zorder=3)
        ax.annotate(r.word, (r.rank_right, r.rank_left), fontsize=7, color=col_, xytext=(3, 2), textcoords="offset points")
    only_r = w[(w.count_left == 0)].nlargest(10, "rtd_contribution").word.tolist(); only_l = w[(w.count_right == 0)].nsmallest(10, "rtd_contribution").word.tolist()
    ax.text(0.02, 0.90, "right-only words (top row): " + ", ".join(only_r), transform=ax.transAxes, fontsize=7, color=CAT[1], va="top", wrap=True)
    ax.text(0.98, 0.10, "left-only words (right column): " + ", ".join(only_l), transform=ax.transAxes, fontsize=7, color=CAT[0], ha="right", va="bottom", wrap=True)
    ax.set_xlabel("rank among right-labelled titles (1 = most frequent)"); ax.set_ylabel("rank among left-labelled titles")
    ax.set_title("Where each word ranks on the two sides (titles both models agree on)")
    ax.text(0.02, 0.97, "above the line: more prominent on the right", transform=ax.transAxes, fontsize=7.5, color=CAT[1], va="top")
    ax.text(0.98, 0.03, "below the line: more prominent on the left", transform=ax.transAxes, fontsize=7.5, color=CAT[0], ha="right")
    ax = axes[1]
    top = pd.concat([w.nlargest(15, "rtd_contribution").sort_values("rtd_contribution"), w.nsmallest(15, "rtd_contribution").sort_values("rtd_contribution")]).sort_values("rtd_contribution")
    y = np.arange(len(top)); ax.barh(y, top.rtd_contribution, color=[CAT[1] if v > 0 else CAT[0] for v in top.rtd_contribution], height=0.7)
    ax.set_yticks(y, top.word, fontsize=7.5); ax.axvline(0, color=INK, lw=0.8); ax.grid(axis="y", visible=False)
    ax.set_xlabel("rank-turbulence divergence contribution (alpha = 1/3); orange = right-labelled, blue = left-labelled")
    ax.set_title("The words that most separate the two labels")
    fig.tight_layout(); save(fig, "14_leaning_words.png")


def main() -> int:
    FIG.mkdir(parents=True, exist_ok=True)
    for fn in (fig_corpus, fig_topics, fig_dimensions, fig_formats, fig_landscape, fig_drift, fig_views, fig_zipf_views, fig_profiles, fig_leaning):
        fn(); print("done", fn.__name__, flush=True)
    import shutil
    if (A / "scree.png").exists():
        shutil.copy(A / "scree.png", FIG / "03_scree.png")
    print(f"{len(list(FIG.glob('*.png')))} figures in {FIG}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
