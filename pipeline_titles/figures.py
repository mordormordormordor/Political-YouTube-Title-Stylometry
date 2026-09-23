"""Static figures for the sectioned write-up (pipeline_titles/reports/figures/*.png).

Every figure is drawn from the analysis tables at render time. The only grouping of
channels is the left / neutral / right channel group of the leaning stage (blue /
gray / orange everywhere); title labels (left / neither / right) use the same hues;
capitalization styles have their own fixed palette. Palette: the validated reference
palette of the dataviz method (blue, orange, aqua, yellow, magenta, green; sequential
blue; diverging blue <-> red with a gray midpoint).

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

from pipeline_titles.common import ANALYSIS_DIR as A, GROUPS, GROUP_LABEL, MONTHS, REPORTS_DIR, gini as gini_fn

FIG = REPORTS_DIR / "figures"
CAT = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4", "#008300", "#4a3aa7", "#e34948"]
INK, INK2, MUTED, GRID, SURFACE = "#0b0b0b", "#52514e", "#8a8983", "#e6e5e1", "#fcfcfb"
GCOL = {"left": CAT[0], "neutral": "#9a9992", "right": CAT[1], "unscored": "#c9c8c3", "neither": "#9a9992"}
CAPS_ORDER = ["all_caps", "selective_caps", "title_case", "sentence_case", "mixed_other", "short_other"]
CAPS_LABEL = {"all_caps": "ALL CAPS", "selective_caps": "selective CAPS", "title_case": "Title Case", "sentence_case": "Sentence case", "mixed_other": "mixed / other", "short_other": "short / other"}
CAPS_COL = dict(zip(CAPS_ORDER, ["#e34948", "#eb6834", "#2a78d6", "#1baf7a", "#8a8983", "#d6d5d0"]))
DIV = LinearSegmentedColormap.from_list("div", ["#0d366b", "#3987e5", "#f0efec", "#e66767", "#8f1d1d"])
SEQ = LinearSegmentedColormap.from_list("seq", ["#f4f8fd", "#cde2fb", "#6da7ec", "#256abf", "#0d366b"])

plt.rcParams.update({"font.family": "sans-serif", "font.size": 9, "axes.edgecolor": GRID, "axes.labelcolor": INK2, "xtick.color": INK2,
                     "ytick.color": INK2, "axes.titlecolor": INK, "axes.titlesize": 10.5, "axes.titleweight": "bold", "axes.titlelocation": "left",
                     "axes.spines.top": False, "axes.spines.right": False, "axes.grid": True, "grid.color": GRID, "grid.linewidth": 0.6,
                     "axes.axisbelow": True, "figure.facecolor": SURFACE, "axes.facecolor": SURFACE, "savefig.dpi": 150, "legend.frameon": False,
                     "legend.fontsize": 8.5})


def rd(name):
    p = A / name
    return pd.read_csv(p if p.exists() or not (A / (name + ".gz")).exists() else A / (name + ".gz"))


def glabel(g: str) -> str:
    return GROUP_LABEL.get(g, g)


SHORT = {"F1": "tone: positive vs outrage", "F2": "clause headline", "F3": "LIVE / labeled", "F4": "stream talk", "F5": "question / explainer",
         "F6": "person-centered", "F7": "news prose", "F8": "numbers / dates", "F9": "ALL CAPS", "F10": "quoted speech", "F11": "long, upbeat", "F12": "modal / future"}


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


def strip_by_group(ax, df, value_col, group_col, order, xlabel, title, color_of=None, seed=1):
    """One row per group: the members as dots, the median as a black bar."""
    rng = np.random.RandomState(seed)
    rows = [g for g in order if (df[group_col] == g).any()]
    for i, g in enumerate(rows):
        s = df[df[group_col] == g]
        col = (color_of or GCOL).get(g, CAT[0])
        ax.plot(s[value_col], i + rng.uniform(-0.2, 0.2, len(s)), "o", color=col, alpha=0.7, ms=5)
        ax.plot([s[value_col].median()] * 2, [i - 0.3, i + 0.3], color=INK, lw=2)
        ax.text(ax.get_xlim()[1] if False else s[value_col].max(), i, f"  n={len(s)}, median {s[value_col].median():.2f}", va="center", fontsize=7.5, color=INK2)
    ax.set_yticks(range(len(rows)), [glabel(g) if color_of is None else CAPS_LABEL.get(g, g) for g in rows], fontsize=8)
    ax.invert_yaxis(); ax.grid(axis="y", visible=False); ax.set_xlabel(xlabel); ax.set_title(title)


# --------------------------------------------------------------------------- #
def fig_corpus():
    cr = rd("creators.csv"); summ = rd("creator_genre_summary.csv"); lb = rd("leaning_by_creator.csv")
    cr = cr.merge(lb[["creator", "group"]], on="creator", how="left").fillna({"group": "unscored"})
    per = summ.merge(cr[["creator", "group"]], on="creator").groupby("group").agg(creators=("creator", "nunique"), titles=("n_unique", "sum")).reindex([g for g in list(GROUPS) + ["unscored"]]).dropna().reset_index()
    per["label"] = per.group.map(glabel)
    fig, axes = plt.subplots(1, 2, figsize=(10, 3.2))
    hbar(axes[0], per.label, per.titles / 1000, [GCOL[g] for g in per.group], fmt="{:.0f}k")
    axes[0].set_title("Unique titles per channel group (thousands)"); axes[0].set_xlabel("")
    hbar(axes[1], per.label, per.creators, [GCOL[g] for g in per.group], fmt="{:.0f}")
    axes[1].set_title("Channels per group")
    fig.suptitle("The corpus by channel group (left / neutral / right from the title-leaning score, document 14)", x=0.01, ha="left", fontsize=11, fontweight="bold", color=INK)
    fig.tight_layout(rect=(0, 0.02, 1, 0.93))
    save(fig, "01_corpus_by_group.png", "Unique titles within creator x genre; every group statistic later is a mean of creators, not a pool of titles.")

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
    tl = rd("topic_labels.csv"); bl = rd("topic_by_group.csv"); tt = rd("topic_timeline.csv"); pol = rd("creator_political_share.csv")
    bl = bl[bl.group.isin(GROUPS)]
    share = bl.groupby("topic_id").mean_creator_share.mean().rename("share")
    top = tl.merge(share, on="topic_id").sort_values("share", ascending=False).head(15)
    fig, ax = plt.subplots(figsize=(9, 5))
    colors = [CAT[0] if p else CAT[3] for p in top.political]
    hbar(ax, top.label, top.share * 100, colors, fmt="{:.1f}%")
    ax.set_title("The fifteen largest topics (creator-balanced share of titles)")
    ax.plot([], [], "s", color=CAT[0], label="political"); ax.plot([], [], "s", color=CAT[3], label="non-political"); ax.legend(loc="lower right")
    ax.set_xlabel("mean over the six channel group x genre cells of the mean creator share, %")
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

    pv = pol[(pol.n_unique >= 50) & (pol.genre == "videos") & pol.group.isin(GROUPS)]
    fig, ax = plt.subplots(figsize=(8, 3))
    strip_by_group(ax, pv, "political_share", "group", list(GROUPS), "share of a creator's unique titles in political topics (edited uploads)", "Political share by channel group: high everywhere")
    ax.set_xlim(0.6, 1.12)
    fig.tight_layout(); save(fig, "02_political_share_by_group.png", "The political tag is broad (212 of 236 topics); dots are creators, the bar the group median.")


def fig_formats():
    sh = rd("format_hook_shares.csv"); ln = sh[(sh.level == "group_mean_of_creators") & sh.group.isin(GROUPS)]
    cr = sh[(sh.level == "creator") & (~sh.low_n.astype(str).str.lower().eq("true")) & sh.group.isin(GROUPS)]
    fmts = ["question", "breaking_live", "episode_show", "interview_guest", "reaction", "confrontation", "howto_explainer", "listicle"]
    fig, axes = plt.subplots(1, 2, figsize=(11, 3.4))
    for ax, g in zip(axes, ["videos", "streams"]):
        strip_by_group(ax, cr[cr.genre == g], "outrage", "group", list(GROUPS), "share of a creator's titles the classifier flags as outrage-framed", f"Outrage-frame share by channel group, {g}", seed=4)
        ax.set_xlim(0, 1.25)
    fig.tight_layout(); save(fig, "04_outrage_by_group.png", "Dots are ranked creators; the black bar is the group median.")

    d = ln[ln.genre == "videos"].set_index("group").reindex(list(GROUPS))[fmts]; d.index = [glabel(g) for g in d.index]
    fig, ax = plt.subplots(figsize=(8.5, 2.6))
    im = ax.imshow(d.to_numpy(), cmap=SEQ, vmin=0, vmax=0.6, aspect="auto")
    ax.set_xticks(range(len(fmts)), fmts, fontsize=8, rotation=20, ha="right"); ax.set_yticks(range(len(d)), d.index, fontsize=8)
    for i in range(d.shape[0]):
        for j in range(d.shape[1]):
            ax.text(j, i, f"{d.iloc[i, j]:.0%}", ha="center", va="center", fontsize=7, color=INK if d.iloc[i, j] < 0.35 else "white")
    ax.grid(False); ax.set_title("Structural formats by channel group (mean of creator shares, edited uploads)")
    fig.tight_layout(); save(fig, "04_formats_heatmap.png")


def fig_landscape():
    ms = rd("map_style.csv"); mt = rd("map_topic.csv"); cc = rd("cluster_comparison.csv"); coh = rd("group_style_cohesion.csv"); ent = rd("entities_top.csv"); st = rd("shared_titles.csv")
    label_set = {"@HasanAbi", "@BenShapiro", "@FoxNews", "@CNN", "@MeidasTouch", "@TuckerCarlson", "@joerogan", "@Reuters", "@destiny", "@TimcastIRL",
                 "@BBCNews", "@TheYoungTurks", "@LastWeekTonight", "@nytimes", "@RSBN", "@LegalEagle", "@CaspianReport", "@bennyjohnson", "@briantylercohen", "@PBDPodcast"}
    for df, name, title, note in ((ms, "05_style_map.png", "Style space: PCA of topic-controlled factor scores (edited uploads)", "Each point is a creator; color is its channel group. The groups are scattered through the space."),
                                  (mt, "05_topic_map.png", "Topic space: MDS of Jensen-Shannon distances between topic mixes (edited uploads)", "Distance = how different two creators' topic mixes are.")):
        d = df[df.genre == "videos"].copy()
        fig, ax = plt.subplots(figsize=(9, 7))
        for g in list(GROUPS) + ["unscored"]:
            s = d[d.group == g]
            if len(s):
                ax.scatter(s.x, s.y, s=34, color=GCOL[g], edgecolor=SURFACE, linewidth=0.8, alpha=0.9, label=f"{glabel(g)} ({len(s)})")
        for r in d[d.creator.isin(label_set)].itertuples():
            ax.annotate(r.creator, (r.x, r.y), fontsize=7.5, color=INK, xytext=(4, 3), textcoords="offset points")
        ax.legend(loc="best", markerscale=1.1); ax.set_xticks([]); ax.set_yticks([]); ax.grid(False); ax.set_title(title)
        fig.tight_layout(); save(fig, name, note)

    fig, axes = plt.subplots(1, 2, figsize=(10, 3.8))
    c = cc.copy(); c["run"] = c.genre + ", " + c.titles
    x = np.arange(len(c)); w = 0.27
    axes[0].bar(x - w, c.ari_style_vs_group, w, color=CAT[0], label="style vs channel group"); axes[0].bar(x, c.ari_topic_vs_group, w, color=CAT[1], label="topic vs channel group"); axes[0].bar(x + w, c.ari_style_vs_topic, w, color=CAT[2], label="style vs topic")
    axes[0].set_xticks(x, c.run, fontsize=8); axes[0].axhline(0, color=INK, lw=0.8); axes[0].set_ylim(-0.1, 0.5); axes[0].set_ylabel("adjusted Rand index (1 = identical, 0 = chance)"); axes[0].legend(); axes[0].grid(axis="x", visible=False)
    axes[0].set_title("Clusterings barely agree with the groups or with each other")
    cv = coh[(coh.titles == "all") & (coh.genre == "videos") & coh.group.isin(GROUPS)].set_index("group").reindex(list(GROUPS)).dropna().reset_index()
    hbar(axes[1], [glabel(g) for g in cv.group], cv.cohesion_ratio, [GCOL[g] for g in cv.group])
    axes[1].axvline(1, color=INK, lw=1, ls="--"); axes[1].set_xlim(0, 1.25); axes[1].set_title("Group cohesion in style space (within / between distance)")
    axes[1].set_xlabel("below 1 = group-mates closer than strangers")
    fig.tight_layout(); save(fig, "05_groups_vs_style.png")

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
    ax.set_xlabel("creators from different organizations using the title verbatim"); ax.set_title("The most shared verbatim titles")
    fig.tight_layout(); save(fig, "05_shared_titles.png")


def fig_drift():
    dl = rd("drift_group_monthly.csv")
    for col, name, title in (("outrage", "06_drift_outrage.png", "Outrage-frame share by month (edited uploads; mean of creators)"),
                             ("F1_controlled", "06_drift_tone.png", "Tone factor F1 (positive vs outrage, topic-controlled) by month"),
                             ("F9_controlled", "06_drift_caps.png", "ALL-CAPS factor F9 by month")):
        allm = dl[(dl.genre == "videos") & (dl.group == "ALL (mean of creators)")].set_index("month").reindex(MONTHS)[col]
        fig, axes = plt.subplots(1, 3, figsize=(11, 3.2), sharex=True, sharey=True)
        for ax, g in zip(axes, GROUPS):
            s = dl[(dl.genre == "videos") & (dl.group == g)].set_index("month").reindex(MONTHS)[col]
            n = dl[(dl.genre == "videos") & (dl.group == g)].n_creators.max()
            ax.plot(range(9), allm.to_numpy(), color=MUTED, lw=1.2, ls="--", label="all creators")
            ax.plot(range(9), s.to_numpy(), color=GCOL[g], lw=2, label=glabel(g)); ax.plot(8, s.iloc[-1], "o", color=SURFACE, mec=GCOL[g], mew=1.5, ms=7)
            ax.set_title(f"{glabel(g)} (n={int(n) if pd.notna(n) else '?'})", fontsize=9); ax.set_xticks(range(9), [m[5:] for m in MONTHS], fontsize=7)
        axes[0].legend(loc="lower left", fontsize=7)
        fig.suptitle(title + "; gray dashed = all creators; hollow = Sept 1-14", x=0.01, ha="left", fontsize=11, fontweight="bold", color=INK)
        fig.tight_layout(rect=(0, 0, 1, 0.92)); save(fig, name)


# --------------------------------------------------------------------------- #
# Document 7: Zipf's law and views over time
# --------------------------------------------------------------------------- #
def fig_zipf_words():
    z = rd("zipf_words.csv"); cv = rd("zipf_words_curves.csv")
    fig, axes = plt.subplots(1, 3, figsize=(13, 4.2), sharey=True)
    panels = (("channel_group", list(GROUPS), GCOL, glabel, "by channel group (balanced edited uploads)"),
              ("title_label", ["left", "neither", "right"], GCOL, lambda l: f"{l} titles", "by title label (the judge's sample)"),
              ("caps_style", CAPS_ORDER, CAPS_COL, lambda c: CAPS_LABEL[c], "by capitalization style"))
    ref = cv[cv.grouping == "corpus"]
    for ax, (kind, order, colors, lab, title) in zip(axes, panels):
        ax.plot(ref["rank"], ref["share"], color=INK, lw=1, ls=":", label="whole corpus")
        for g in order:
            s = cv[(cv.grouping == kind) & (cv.system == g)]
            if not len(s):
                continue
            row = z[(z.grouping == kind) & (z.system == g)].iloc[0]
            sm = f", size-matched {row.zipf_size_matched:.2f}" if pd.notna(row.zipf_size_matched) else ""
            ax.plot(s["rank"], s["share"], color=colors[g], lw=1.8, label=f"{lab(g)} (top-1000 exponent {row.zipf_top1000:.2f}{sm})")
        ax.set_xscale("log"); ax.set_yscale("log"); ax.set_xlabel("rank of the word (log)"); ax.legend(fontsize=6.8, loc="lower left"); ax.set_title(title, fontsize=9.5)
    axes[0].set_ylabel("share of all tokens (log)")
    fig.suptitle("Zipf's law in title vocabulary: word frequency against rank, three ways of cutting the corpus", x=0.01, ha="left", fontsize=11, fontweight="bold", color=INK)
    fig.tight_layout(rect=(0, 0.03, 1, 0.94))
    save(fig, "07_zipf_words.png", "Tokens are lower-cased words including stopwords; the exponent is the OLS slope of log frequency on log rank; size-matched = mean over 20 draws of 2,000 titles, top 200 ranks.")


def fig_zipf_views():
    hc = rd("hit_concentration.csv"); hv = hc[(hc.genre == "videos")].copy()
    cp = rd("caps_profile.csv"); cp = cp[cp.genre == "videos"].copy(); cp["dominant_caps_style"] = cp[CAPS_ORDER].idxmax(axis=1)
    hv = hv.merge(cp[["creator", "dominant_caps_style"]], on="creator", how="left")
    pre = pd.read_parquet(A / "titles_prepared.parquet", columns=["creator", "genre", "view_count", "has_views"])
    picks = ["@FoxNews", "@CNN", "@Reuters", "@BenShapiro", "@briantylercohen", "@HasanAbi", "@Vaush", "@BelleRanch"]
    fig, axes = plt.subplots(1, 3, figsize=(14, 4.6), gridspec_kw={"width_ratios": [1.3, 1, 1]})
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
    strip_by_group(axes[1], hv[hv.group.isin(GROUPS)], "zipf_views_all", "group", list(GROUPS), "Zipf slope of views (log views vs log rank, all videos)", "Slope by channel group", seed=2)
    strip_by_group(axes[2], hv[hv.dominant_caps_style.isin(CAPS_ORDER)], "zipf_views_all", "dominant_caps_style", CAPS_ORDER, "Zipf slope of views", "Slope by the channel's dominant capitalization style", color_of=CAPS_COL, seed=3)
    for ax in axes[1:]:
        ax.set_xlim(0, 3.2)
    fig.tight_layout(); save(fig, "07_zipf_views.png", "Curves bend down at the tail on log-log axes: lognormal rather than straight-line power-law behavior. Steeper slope = views fall off faster down the ranking; the black bar is the median.")


def fig_views_over_time():
    v = rd("views_by_month.csv"); v = v[v.month != "all"]
    fig, axes = plt.subplots(1, 3, figsize=(14, 4.2))
    ax = axes[0]
    allm = v[v.grouping == "all"].set_index("month").reindex(MONTHS)
    ax.plot(range(9), allm.creator_median_views / 1000, color=MUTED, lw=1.2, ls="--", label="all channels")
    for g in GROUPS:
        s = v[(v.grouping == "channel_group") & (v.group == g)].set_index("month").reindex(MONTHS)
        ax.plot(range(9), s.creator_median_views / 1000, color=GCOL[g], lw=2, label=f"{glabel(g)} (n={int(s.n_creators.max())})"); ax.plot(8, s.creator_median_views.iloc[-1] / 1000, "o", color=SURFACE, mec=GCOL[g], mew=1.5, ms=7)
    ax.set_xticks(range(9), [m[5:] for m in MONTHS], fontsize=7.5); ax.set_ylabel("median channel's median views per video (thousands)"); ax.legend(fontsize=7.5)
    ax.set_title("Views per video by publication month and channel group", fontsize=9.5); ax.set_ylim(0, None)
    for ax, kind, order, colors, lab, title in ((axes[1], "caps_style", CAPS_ORDER[:4], CAPS_COL, lambda c: CAPS_LABEL[c], "Relative views by capitalization style"),
                                                (axes[2], "title_label", ["left", "neither", "right"], GCOL, lambda l: f"{l} titles", "Relative views by title label (sampled titles)")):
        ax.axhline(0, color=INK, lw=0.8)
        for g in order:
            s = v[(v.grouping == kind) & (v.group == g)].set_index("month").reindex(MONTHS)
            if s.relative_log_views.notna().sum() < 5:
                continue
            ax.plot(range(9), s.relative_log_views, color=colors[g], lw=2, label=lab(g))
            ax.fill_between(range(9), s.relative_log_views - 1.96 * s.relative_log_views_se, s.relative_log_views + 1.96 * s.relative_log_views_se, color=colors[g], alpha=0.12, linewidth=0)
        ax.set_xticks(range(9), [m[5:] for m in MONTHS], fontsize=7.5); ax.legend(fontsize=7, ncol=2); ax.set_title(title, fontsize=9.5)
        ax.set_ylabel("relative log views (0 = channel's month average)")
    axes[1].set_ylim(-0.1, 0.16); axes[2].set_ylim(-0.25, 0.3)
    fig.suptitle("Views over time: the snapshot by month, and how capitals and leaning do against each channel's own baseline", x=0.01, ha="left", fontsize=11, fontweight="bold", color=INK)
    fig.tight_layout(rect=(0, 0.03, 1, 0.94))
    save(fig, "07_views_over_time.png", "Views are a 2026-09-14 snapshot; months are approximate listing dates; hollow marker = Sept 1-14. Relative views: log(1+views) minus the mean for the same channel and month (0 = the channel's average title); bands are +-1.96 SE; the two small styles (mixed, short) are in the table only.")


def fig_caps_by_group():
    cs = rd("caps_style_by_group.csv")
    rows = [("channel_group", g, glabel(g)) for g in GROUPS] + [("title_label", l, f"{l} titles") for l in ("left", "neither", "right")]
    d = pd.DataFrame([{**cs[(cs.grouping == k) & (cs.group == g)].iloc[0].to_dict(), "label": lab} for k, g, lab in rows if ((cs.grouping == k) & (cs.group == g)).any()])
    fig, ax = plt.subplots(figsize=(9.5, 3.4))
    left = np.zeros(len(d))
    for style in CAPS_ORDER:
        ax.barh(np.arange(len(d)), d[style], left=left, color=CAPS_COL[style], height=0.7, label=CAPS_LABEL[style], edgecolor=SURFACE, linewidth=0.6)
        for i, (v_, l_) in enumerate(zip(d[style], left)):
            if v_ >= 0.06:
                ax.text(l_ + v_ / 2, i, f"{v_:.0%}", ha="center", va="center", fontsize=7, color="white" if style in ("all_caps", "selective_caps", "title_case", "sentence_case") else INK)
        left += d[style].to_numpy()
    ax.set_yticks(np.arange(len(d)), [f"{l} (n={int(n):,})" for l, n in zip(d.label, d.n_titles)], fontsize=8); ax.invert_yaxis(); ax.set_xlim(0, 1); ax.grid(axis="y", visible=False)
    ax.axhline(2.5, color=INK, lw=0.8)
    ax.xaxis.set_major_formatter(matplotlib.ticker.PercentFormatter(1.0)); ax.legend(ncol=6, loc="upper center", bbox_to_anchor=(0.5, -0.1), fontsize=7.5)
    ax.set_title("Capitalization style by channel group (top; balanced edited uploads) and by title label (bottom; the judge's sample)")
    fig.tight_layout(); save(fig, "07_caps_by_group.png")


def fig_profiles():
    from pipeline_titles.textstats import CAPS_STYLES
    ar = rd("arousal_index.csv"); a = ar[(ar.genre == "videos") & (~ar.low_n)].sort_values("arousal_index", ascending=False).reset_index(drop=True)
    half = int(np.ceil(len(a) / 2))
    fig, axes = plt.subplots(1, 2, figsize=(12, 0.115 * half + 1.2))
    for ax, part in zip(axes, (a.iloc[:half], a.iloc[half:])):
        y = np.arange(len(part))
        ax.hlines(y, 0, part.arousal_index, color=GRID, lw=1.5)
        ax.scatter(part.arousal_index, y, s=18, color=[GCOL.get(g, GCOL["unscored"]) for g in part.group], zorder=3)
        ax.set_yticks(y, [f"{c}" for c in part.creator], fontsize=5.5); ax.invert_yaxis(); ax.set_xlim(0, 1); ax.grid(axis="y", visible=False)
        ax.tick_params(axis="x", labelsize=7)
    for g in GROUPS:
        axes[0].plot([], [], "o", color=GCOL[g], label=glabel(g))
    axes[0].legend(loc="lower right", fontsize=7)
    fig.suptitle(f"Arousal index, all {len(a)} ranked channels (edited uploads), highest first", x=0.01, ha="left", fontsize=11, fontweight="bold", color=INK)
    fig.tight_layout(rect=(0, 0, 1, 0.97)); save(fig, "12_arousal_ranked.png", "0-1 composite of ALL-CAPS share, exclamation marks, power words, emoji and VADER intensity; color = channel group.")

    fig, ax = plt.subplots(figsize=(9, 3))
    strip_by_group(ax, a[a.group.isin(GROUPS)], "arousal_index", "group", list(GROUPS), "arousal index (black bar = group median)", "Arousal index by channel group", seed=3)
    ax.set_xlim(0, 1.25)
    fig.tight_layout(); save(fig, "12_arousal_by_group.png")

    cp = rd("caps_profile.csv"); c = cp[(cp.genre == "videos") & (~cp.low_n)].sort_values("caps_any", ascending=False)
    labels = [CAPS_LABEL[s] for s in CAPS_STYLES]
    cols = [CAPS_COL[s] for s in CAPS_STYLES]
    for name, sub, title in (("11_caps_profile_top.png", c.head(45), "Capitalization profile: the 45 channels using most ALL-CAPS or selective CAPS (edited uploads)"),
                             ("11_caps_profile_bottom.png", c.tail(30), "Capitalization profile: the 30 channels using least capitals")):
        fig, ax = plt.subplots(figsize=(10, 0.2 * len(sub) + 1.5))
        left = np.zeros(len(sub))
        for lab, col_, style in zip(labels, cols, CAPS_STYLES):
            ax.barh(np.arange(len(sub)), sub[style], left=left, color=col_, height=0.72, label=lab, edgecolor=SURFACE, linewidth=0.6)
            left += sub[style].to_numpy()
        ax.set_yticks(np.arange(len(sub)), sub.creator, fontsize=7); ax.invert_yaxis(); ax.set_xlim(0, 1); ax.grid(axis="y", visible=False)
        ax.xaxis.set_major_formatter(matplotlib.ticker.PercentFormatter(1.0)); ax.legend(ncol=6, loc="upper center", bbox_to_anchor=(0.5, -0.04), fontsize=7.5)
        ax.set_title(title)
        fig.tight_layout(); save(fig, name)
    gm = c[c.group.isin(GROUPS)].groupby("group")[CAPS_STYLES].mean().reindex(list(GROUPS)); gm.index = [glabel(g) for g in gm.index]
    fig, ax = plt.subplots(figsize=(9, 2.6))
    left = np.zeros(len(gm))
    for lab, col_, style in zip(labels, cols, CAPS_STYLES):
        ax.barh(np.arange(len(gm)), gm[style], left=left, color=col_, height=0.7, label=lab, edgecolor=SURFACE, linewidth=0.6)
        left += gm[style].to_numpy()
    ax.set_yticks(np.arange(len(gm)), gm.index, fontsize=8); ax.invert_yaxis(); ax.set_xlim(0, 1); ax.grid(axis="y", visible=False)
    ax.xaxis.set_major_formatter(matplotlib.ticker.PercentFormatter(1.0)); ax.legend(ncol=6, loc="upper center", bbox_to_anchor=(0.5, -0.12), fontsize=7.5)
    ax.set_title("Capitalization profile by channel group (mean of creators, edited uploads)")
    fig.tight_layout(); save(fig, "11_caps_profile_by_group.png")

    tw = rd("top_words.csv").head(20)
    fig, axes = plt.subplots(1, 2, figsize=(10, 5))
    hbar(axes[0], tw.word, tw.balanced_share_of_titles * 100, CAT[0], fmt="{:.1f}%"); axes[0].set_title("Creator-balanced: mean share of a creator's titles containing the word")
    raw = rd("top_words.csv").sort_values("raw_titles", ascending=False).head(20)
    hbar(axes[1], raw.word, raw.raw_pooled_share_of_titles * 100, CAT[1], fmt="{:.1f}%"); axes[1].set_title("Raw pooled: share of all unique titles containing the word")
    fig.suptitle("The twenty most frequent non-stopwords in titles (edited uploads)", x=0.01, ha="left", fontsize=11, fontweight="bold", color=INK)
    fig.tight_layout(rect=(0, 0, 1, 0.95)); save(fig, "11_top_words.png")

    # twins: the closest cross-divide pairs, and how cross-divide distances compare with same-group ones
    pairs = rd("style_twins.csv").head(20); near = rd("style_twins_nearest.csv")
    fig, axes = plt.subplots(1, 2, figsize=(12, 5.6), gridspec_kw={"width_ratios": [1.35, 1]})
    ax = axes[0]; y = np.arange(len(pairs))
    ax.barh(y, pairs.distance, color=GRID, height=0.6)
    for yi, r in zip(y, pairs.itertuples()):
        ax.text(0.02, yi, r.left_creator, va="center", ha="left", fontsize=7.5, color=CAT[0], fontweight="bold")
        ax.text(r.distance + 0.03, yi, r.right_creator, va="center", ha="left", fontsize=7.5, color=CAT[1], fontweight="bold")
    ax.set_yticks([]); ax.invert_yaxis(); ax.set_xlim(0, pairs.distance.max() + 1.6); ax.grid(axis="y", visible=False)
    ax.set_xlabel(f"distance in z-scored 12-factor style space (median nearest-neighbor distance {np.nanmedian(near.nearest_same_group_distance):.1f})"); ax.set_title("The twenty closest left (blue) - right (orange) pairs")
    ax = axes[1]
    a_ = np.sort(near.twin_distance.to_numpy()); b_ = np.sort(near.nearest_same_group_distance.dropna().to_numpy())
    ax.plot(a_, np.arange(1, len(a_) + 1) / len(a_), color=CAT[2], lw=2, label="nearest creator across the divide")
    ax.plot(b_, np.arange(1, len(b_) + 1) / len(b_), color=INK, lw=2, ls="--", label="nearest creator in the same group")
    ax.set_xlabel("distance to nearest neighbor"); ax.set_ylabel("share of left and right channels"); ax.legend(loc="lower right")
    ax.set_title(f"For {near.twin_closer_than_any_same_group.mean():.0%} of channels the twin across the divide is closer than any group-mate")
    fig.tight_layout(); save(fig, "09_twins.png", "Left and right channel groups (the leaning score), edited uploads, clip channels excluded.")




def _judge_name(c):
    c = c.replace("label_", "").replace("_score", "")
    return ("Claude " + c.replace("claude_code_", "").replace("_", " ").title()) if c.startswith("claude_code_") else c.replace("_", ":", 1).replace("_", ".")


def fig_leaning():
    """Channel level: every channel's score against the share of its titles read as neither, and
    how the scores distribute across the three groups."""
    if not (A / "leaning_by_creator.csv").exists():
        return
    bc = rd("leaning_by_creator.csv"); summ = json.loads((A / "leaning_summary.json").read_text())
    judge = summ["judge_of_record"]; eps = float(summ.get("threshold", 0.05)); jname = _judge_name(judge)
    fig, axes = plt.subplots(1, 2, figsize=(12.5, 5.2), gridspec_kw={"width_ratios": [1.2, 1]})
    ax = axes[0]
    for g in ("neutral", "left", "right"):
        sub = bc[bc.group == g]
        ax.scatter(sub[f"{judge}_neither"], sub.score, s=26, color=GCOL[g], alpha=0.85, edgecolor=SURFACE, linewidth=0.6, label=f"{g} channels ({len(sub)})")
    for y in (eps, -eps):
        ax.axhline(y, color=INK2, lw=0.7, ls="--")
    ax.axhline(0, color=GRID, lw=1)
    offsets = [(5, 3), (5, -9), (5, 12), (5, -18)]
    for i, r in enumerate(pd.concat([bc.nsmallest(4, "score"), bc.nlargest(4, "score")]).itertuples()):
        ax.annotate(r.creator, (getattr(r, f"{judge}_neither"), r.score), fontsize=6.5, xytext=offsets[i % 4], textcoords="offset points")
    ax.set_xlim(-0.02, 1.02); ax.set_ylim(-1.05, 1.05)
    ax.set_xlabel("share of the channel's sampled titles labeled neither"); ax.set_ylabel(f"score = (right − left) / titles  ({jname})")
    ax.set_title("Every channel: how partisan its titles read, and which way"); ax.legend(fontsize=7.5, loc="upper right", title=f"group at ±{eps:g}", title_fontsize=7.5)
    ax = axes[1]
    bins = np.arange(-1, 1.0001, 0.1)
    ax.hist([bc[bc.group == g].score for g in ("left", "neutral", "right")], bins=bins, stacked=True, color=[GCOL[g] for g in ("left", "neutral", "right")], label=["left", "neutral", "right"], edgecolor=SURFACE, linewidth=0.5)
    for x in (eps, -eps):
        ax.axvline(x, color=INK2, lw=0.7, ls="--")
    ax.set_xlabel("channel score (−1 = every sampled title read left, +1 = every one read right)"); ax.set_ylabel("channels")
    ax.set_title(f"How the {len(bc)} channels distribute"); ax.legend(fontsize=8, loc="upper left")
    fig.tight_layout(); save(fig, "14_leaning_scores.png")


def fig_leaning_channels():
    """Per-channel breakdowns: stacked left / neither / right shares for every channel (two
    columns, sorted by score) and the mean composition of the three groups."""
    if not (A / "leaning_by_creator.csv").exists():
        return
    bc = rd("leaning_by_creator.csv"); summ = json.loads((A / "leaning_summary.json").read_text())
    judge = summ["judge_of_record"]; jname = _judge_name(judge)
    d = bc.sort_values("score").reset_index(drop=True)
    L, N, R = d[f"{judge}_left"], d[f"{judge}_neither"], d[f"{judge}_right"]
    half = int(np.ceil(len(d) / 2))
    fig, axes = plt.subplots(1, 2, figsize=(13, 0.135 * half + 1.6))
    for ax, sl in zip(axes, (slice(0, half), slice(half, len(d)))):
        y = np.arange(sl.stop - sl.start)
        ax.barh(y, L.iloc[sl], color=CAT[0], height=0.78, label="left")
        ax.barh(y, N.iloc[sl], left=L.iloc[sl], color="#d6d5d0", height=0.78, label="neither")
        ax.barh(y, R.iloc[sl], left=L.iloc[sl] + N.iloc[sl], color=CAT[1], height=0.78, label="right")
        ax.set_yticks(y, d.creator.iloc[sl], fontsize=5.6); ax.set_ylim(len(y) - 0.5, -0.5); ax.set_xlim(0, 1); ax.grid(axis="y", visible=False)
        ax.xaxis.set_major_formatter(matplotlib.ticker.PercentFormatter(1.0)); ax.tick_params(axis="x", labelsize=7, top=True, labeltop=True)
        for yi, sc, g in zip(y, d.score.iloc[sl], d.group.iloc[sl]):
            ax.text(1.005, yi, f"{sc:+.2f}", va="center", ha="left", fontsize=5.2, color=GCOL[g], fontweight="bold" if g != "neutral" else "normal")
    fig.legend(*axes[0].get_legend_handles_labels(), loc="upper right", fontsize=8, ncol=3, frameon=False, bbox_to_anchor=(0.99, 0.995))
    n50, nbase = int((bc.n_titles >= 50).sum()), int((bc.n_titles < 50).sum())
    fig.suptitle(f"Every channel's sampled titles as labeled by {jname}: share left / neither / right ({n50} channels at 50 titles, {nbase} at 16 or fewer; sorted by score, most left first; score at right, colored by group)", x=0.01, ha="left", fontsize=11, fontweight="bold", color=INK)
    fig.tight_layout(rect=(0, 0, 1, 0.975)); save(fig, "14_leaning_channels.png")

    comp = bc.groupby("group")[[f"{judge}_left", f"{judge}_neither", f"{judge}_right"]].mean().reindex(["right", "neutral", "left"])
    comp["n"] = bc.groupby("group").size().reindex(comp.index)
    fig, ax = plt.subplots(figsize=(9, 2.9)); y = np.arange(len(comp))
    ax.barh(y, comp[f"{judge}_left"], color=CAT[0], height=0.6, label="left titles")
    ax.barh(y, comp[f"{judge}_neither"], left=comp[f"{judge}_left"], color="#d6d5d0", height=0.6, label="neither")
    ax.barh(y, comp[f"{judge}_right"], left=comp[f"{judge}_left"] + comp[f"{judge}_neither"], color=CAT[1], height=0.6, label="right titles")
    for yi, r in zip(y, comp.itertuples()):
        ax.text(0.01, yi, f"{getattr(r, judge + '_left'):.0%}", va="center", fontsize=8, color="white", fontweight="bold")
        ax.text(getattr(r, judge + '_left') + getattr(r, judge + '_neither') / 2, yi, f"{getattr(r, judge + '_neither'):.0%}", va="center", ha="center", fontsize=8, color=INK)
        ax.text(0.99, yi, f"{getattr(r, judge + '_right'):.0%}", va="center", ha="right", fontsize=8, color="white", fontweight="bold")
    ax.set_yticks(y, [f"{g} channels (n={int(n)})" for g, n in zip(comp.index, comp.n)], fontsize=9); ax.set_xlim(0, 1); ax.grid(axis="y", visible=False)
    ax.xaxis.set_major_formatter(matplotlib.ticker.PercentFormatter(1.0)); ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.18), ncol=3, fontsize=8)
    ax.set_title(f"Mean composition of a channel's sampled titles, by group ({jname})")
    fig.tight_layout(); save(fig, "14_leaning_group_composition.png")


def fig_leaning_stability():
    """Does a channel's score depend on which titles were drawn? Left: the score from the
    original 16-title draw against the score from the disjoint, month-spread top-up titles.
    Right: split-half reliability and base-vs-top-up Spearman."""
    if not (A / "leaning_stability_channels.csv").exists() or not (A / "leaning_split_half.csv").exists():
        return
    ch = rd("leaning_stability_channels.csv"); st = rd("leaning_stability.csv"); sh = rd("leaning_split_half.csv")
    summ = json.loads((A / "leaning_summary.json").read_text()); judge = summ["judge_of_record"]; jname = _judge_name(judge)
    if not len(ch) or not len(st):
        return
    st_j, sh_j = st.iloc[0], sh.iloc[0]
    fig, ax = plt.subplots(figsize=(7.2, 6))
    ax.plot([-1, 1], [-1, 1], color=GRID, lw=1); ax.axhline(0, color=GRID, lw=1); ax.axvline(0, color=GRID, lw=1)
    for g in ("neutral", "left", "right"):
        sub = ch[ch.group == g]
        ax.scatter(sub.score_base, sub.score_topup, s=24, color=GCOL[g], alpha=0.85, edgecolor=SURFACE, linewidth=0.6, label=f"{g} channels (final group)")
    for i, r in enumerate(ch.reindex(ch.change.abs().sort_values(ascending=False).index).head(6).itertuples()):
        inward = r.score_base < 0.5     # labels point toward the middle of the plot, never past an edge
        ax.annotate(r.creator, (r.score_base, r.score_topup), fontsize=6.5, xytext=(5 if inward else -5, 4 if i % 2 else -10), textcoords="offset points", ha="left" if inward else "right")
    nb, nt = int(ch.n_base.median()), int(ch.n_topup.median())
    ax.set_xlabel(f"score from the first {nb} titles drawn"); ax.set_ylabel(f"score from the {nt} titles drawn later, from other months")
    ax.set_title(f"Same channel, two independent draws of titles (Spearman {float(st_j.spearman_base_vs_topup):.2f}, n = {len(ch)})"); ax.legend(fontsize=7.5, loc="upper left")
    ax.text(0.98, 0.03, f"split-half check: two random halves of {int(sh_j.median_titles_per_half)} titles\nrank the channels at Spearman {float(sh_j.split_half_spearman_mean):.2f} (20 splits)", transform=ax.transAxes, ha="right", va="bottom", fontsize=7.5, color=INK2)
    ax.set_xlim(-1.05, 1.05); ax.set_ylim(-1.05, 1.05)
    fig.tight_layout(); save(fig, "14_leaning_stability.png")


def _fightin_words(ax_sc, ax_bar, wc, cutoff, sys_left, sys_right, n_label=12, n_bars=25):
    """Monroe et al.'s plot: z of the weighted log-odds against total frequency, classes colored,
    the most one-sided words named; beside it the top words each side as diverging bars. The
    axes are capped at the 99.5th percentile of |z| (at least four cutoffs) and the few words
    beyond the cap are drawn at the edge and listed with their z, so that one word like
    "trump" cannot squash the rest of the plot."""
    wc = wc.copy(); wc["total"] = wc.count_left + wc.count_right
    col = {"left": CAT[0], "right": CAT[1], "neither": "#c9c8c3"}
    # cap: a whole number, the 6th largest |z| rounded up (so at most five words sit beyond the edge), never below 8
    cap = float(max(8, int(np.ceil(wc.z.abs().nlargest(6).iloc[-1]))))
    wc["zc"] = wc.z.clip(-cap, cap); off = wc[wc.z.abs() > cap].sort_values("z")
    for cls in ("neither", "left", "right"):
        sub = wc[(wc.word_class == cls) & (wc.z.abs() <= cap)]
        ax_sc.scatter(sub.total, sub.zc, s=9 if cls == "neither" else 16, color=col[cls], alpha=0.55 if cls == "neither" else 0.9, edgecolor="none", label=f"{cls} ({int((wc.word_class == cls).sum()):,})")
    for r in off.itertuples():
        ax_sc.scatter([r.total], [r.zc], marker="v" if r.z < 0 else "^", s=46, color=col[r.word_class], edgecolor=INK, linewidth=0.5, zorder=4)
    off_l = [f"{r.word} ({r.z:+.0f})" for r in off.itertuples() if r.z < 0]; off_r = [f"{r.word} ({r.z:+.0f})" for r in off[::-1].itertuples() if r.z > 0]
    # the low-frequency side of the plot is empty at large |z|, so the notes go there
    if off_l:
        ax_sc.text(0.02, 0.05, "beyond the lower edge:\n" + ", ".join(off_l), transform=ax_sc.transAxes, ha="left", va="bottom", fontsize=7.5, color=col["left"], fontweight="bold")
    if off_r:
        ax_sc.text(0.02, 0.78, "beyond the upper edge:\n" + ", ".join(off_r), transform=ax_sc.transAxes, ha="left", va="top", fontsize=7.5, color=col["right"], fontweight="bold")
    ax_sc.axhline(cutoff, color=INK2, lw=0.8, ls="--"); ax_sc.axhline(-cutoff, color=INK2, lw=0.8, ls="--"); ax_sc.axhline(0, color=GRID, lw=1)
    ax_sc.set_xscale("log"); ax_sc.set_ylim(-cap * 1.08, cap * 1.08)
    ax_sc.annotate(f"+{cutoff:g}", (0.995, cutoff), xycoords=ax_sc.get_yaxis_transform(), xytext=(0, 3), textcoords="offset points", ha="right", va="bottom", fontsize=7.5, color=INK2)
    ax_sc.annotate(f"−{cutoff:g}", (0.995, -cutoff), xycoords=ax_sc.get_yaxis_transform(), xytext=(0, -3), textcoords="offset points", ha="right", va="top", fontsize=7.5, color=INK2)
    on = wc[wc.z.abs() <= cap]
    lab = pd.concat([on.nlargest(n_label, "z"), on.nsmallest(n_label, "z"), on[on.word_class == "right"].nlargest(5, "total"), on[on.word_class == "left"].nlargest(5, "total")]).drop_duplicates("word")
    for i, r in enumerate(lab.itertuples()):
        ax_sc.annotate(r.word, (r.total, r.zc), fontsize=6.8, color=col[r.word_class], xytext=(4, 3 if i % 2 else -8), textcoords="offset points")
    ax_sc.set_xlabel("occurrences in both systems together (log scale)"); ax_sc.set_ylabel(f"z of the weighted log-odds:  ← over-used in {sys_left}   |   over-used in {sys_right} →")
    ax_sc.legend(loc="upper left", fontsize=7.5, title="class", title_fontsize=7.5)
    ax_sc.text(0.02, 0.005, f"triangles: words beyond ±{cap:g}, drawn at the edge", transform=ax_sc.transAxes, ha="left", va="bottom", fontsize=7, color=INK2)
    ax_sc.set_title("Every word: how one-sided (z) against how common")
    # the two lists side by side, mirrored about a central spine (the layout of wordsandpolitics.com's
    # "Who over-uses which words"): each side ranked from the top, the word beside the spine, the bar
    # growing outward, its z at the outer end; bars beyond the cap are cut, drawn paler and keep their z
    top_l = wc.nsmallest(n_bars, "z").reset_index(drop=True); top_r = wc.nlargest(n_bars, "z").reset_index(drop=True)
    gutter = 0.42 * cap
    for side, top, sign in (("left", top_l, -1), ("right", top_r, 1)):
        for i, r in top.iterrows():
            length = min(abs(r.z), cap); cut = abs(r.z) > cap
            ax_bar.barh(i, sign * length, left=sign * gutter, height=0.64, color=col[side], alpha=0.5 if cut else 0.9, edgecolor="none")
            ax_bar.text(sign * gutter * 0.08, i, r.word, ha="right" if sign < 0 else "left", va="center", fontsize=7.6, color=INK)
            own, other = (r.count_left, r.count_right) if sign < 0 else (r.count_right, r.count_left)
            counts = f"{own:,} vs {other:,}"
            if length >= 0.34 * cap:   # room inside the bar: counts in white at the inner end, z outside at the tip
                ax_bar.text(sign * (gutter + 0.02 * cap), i, counts, ha="left" if sign > 0 else "right", va="center", fontsize=6.2, color="white")
                ax_bar.text(sign * (gutter + length + 0.02 * cap), i, f"{r.z:+.1f}", ha="left" if sign > 0 else "right", va="center", fontsize=6.6, color=INK2, fontweight="bold" if cut else "normal")
            else:
                ax_bar.text(sign * (gutter + length + 0.02 * cap), i, f"{r.z:+.1f} ({counts})", ha="left" if sign > 0 else "right", va="center", fontsize=6.2, color=INK2)
    ax_bar.axvline(0, color=GRID, lw=1.2)
    ax_bar.text(-gutter, -1.15, f"MORE {sys_left.upper()}", ha="right", va="center", fontsize=8, color=col["left"], fontweight="bold")
    ax_bar.text(gutter, -1.15, f"MORE {sys_right.upper()}", ha="left", va="center", fontsize=8, color=col["right"], fontweight="bold")
    ax_bar.set_xlim(-(gutter + cap * 1.32), gutter + cap * 1.32); ax_bar.set_ylim(max(len(top_l), len(top_r)) - 0.4, -1.8)
    ax_bar.set_xticks([]); ax_bar.set_yticks([]); ax_bar.grid(False)
    for sp in ax_bar.spines.values():
        sp.set_visible(False)
    ax_bar.set_title(f"The {n_bars} words each side over-uses most")
    ax_bar.text(0.5, -0.005, f"bar length = z, printed at the tip  ·  inside the bar: occurrences on this side vs the other  ·  paler bars are cut at ±{cap:g} and keep their z",
                transform=ax_bar.transAxes, ha="center", va="top", fontsize=7.2, color=INK2)


def fig_leaning_logodds():
    """Weighted log-odds figures for document 14: the judge's left- vs right-read titles and the
    left vs right channel groups, plus the out-of-fold lexicon classifier against the judge."""
    if not (A / "leaning_logodds.csv").exists():
        return
    lo = rd("leaning_logodds.csv"); summ = rd("leaning_logodds_summary.csv"); cutoff = float(summ.cutoff_z.iloc[0])
    for name, sys_l, sys_r, fname in (("titles", "left-read titles", "right-read titles", "14_logodds_titles.png"), ("channels", "left channels", "right channels", "14_logodds_channels.png")):
        wc = lo[lo.comparison == name]
        if not len(wc):
            continue
        fig, axes = plt.subplots(1, 2, figsize=(14, 7.4), gridspec_kw={"width_ratios": [1.2, 1.1]})
        _fightin_words(axes[0], axes[1], wc, cutoff, sys_l, sys_r)
        r = summ[summ.comparison == name].iloc[0]
        groups = json.loads((A / "leaning_summary.json").read_text()).get("groups", {})
        jn = _judge_name(json.loads((A / "leaning_summary.json").read_text())["judge_of_record"])
        title = (f"Which words each side over-uses: titles labeled left vs right by {jn}" if name == "titles"
                 else f"Which words each side over-uses: left channels ({groups.get('left', '?')}) vs right channels ({groups.get('right', '?')}), every title they published")
        fig.suptitle(title, x=0.01, ha="left", fontsize=12, fontweight="bold", color=INK)
        fig.tight_layout(rect=(0, 0.035, 1, 0.965))
        save(fig, fname, note=f"Weighted log-odds with an informative Dirichlet prior (Monroe, Colaresi and Quinn 2008; α₀ = 500) over the {int(r.n_words):,} words with three or more occurrences in the two systems together; z = log-odds / its standard error, cutoff |z| ≥ {cutoff:g}.")
    # how many words clear the cutoff, per comparison: left and right classes as shares of the vocabulary, counts printed
    cl = summ[summ.comparison.isin(["titles", "channels"])].set_index("comparison").reindex(["titles", "channels"]).dropna(subset=["n_words"])
    if len(cl):
        names = {"titles": "left-read vs right-read titles", "channels": "left vs right channels, every title"}
        fig, ax = plt.subplots(figsize=(10, 2.6)); y = np.arange(len(cl))
        pl, pr = cl.n_left / cl.n_words, cl.n_right / cl.n_words
        ax.barh(y, -pl, color=CAT[0], height=0.55); ax.barh(y, pr, color=CAT[1], height=0.55)
        for yi, (a, b, r) in enumerate(zip(pl, pr, cl.itertuples())):
            ax.text(-a - 0.003, yi, f"{int(r.n_left):,} left-class ({a:.1%})", ha="right", va="center", fontsize=8, color=INK)
            ax.text(b + 0.003, yi, f"{int(r.n_right):,} right-class ({b:.1%})", ha="left", va="center", fontsize=8, color=INK)
            ax.text(0, yi - 0.42, f"{int(r.n_words):,} words with 3+ occurrences; {int(r.n_neither):,} neither ({1 - a - b:.0%})", ha="center", va="center", fontsize=7.2, color=INK2)
        ax.axvline(0, color=INK, lw=0.8); ax.set_yticks(y, [names[i] for i in cl.index], fontsize=9); ax.set_ylim(len(cl) - 0.4, -0.9); ax.grid(axis="y", visible=False)
        lim = max(pl.max(), pr.max()) * 1.9; ax.set_xlim(-lim, lim)
        ax.xaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda v, _: f"{abs(v):.0%}")); ax.set_xlabel(f"share of the vocabulary classified at |z| ≥ {cutoff:g}   (← left-class · right-class →)")
        ax.set_title("How many words clear the cutoff, and on which side")
        fig.tight_layout(); save(fig, "14_logodds_classes.png")
    if not (A / "leaning_lexicon_channels.csv").exists() or not (A / "leaning_lexicon_validation.csv").exists():
        return
    ch = rd("leaning_lexicon_channels.csv"); val = rd("leaning_lexicon_validation.csv")
    summj = json.loads((A / "leaning_summary.json").read_text()); judge = summj["judge_of_record"]
    v = val[val.judge == judge].iloc[0] if (val.judge == judge).any() else val.iloc[0]

    def _nm(c):
        c = c.replace("label_", "").replace("_score", "")
        return ("Claude " + c.replace("claude_code_", "").replace("_", " ").title()) if c.startswith("claude_code_") else c.replace("_", ":", 1).replace("_", ".")
    fig, axes = plt.subplots(1, 2, figsize=(12, 5.2), gridspec_kw={"width_ratios": [1.2, 1]})
    ax = axes[0]
    ax.plot([-1, 1], [-1, 1], color=GRID, lw=1); ax.axhline(0, color=GRID, lw=1); ax.axvline(0, color=GRID, lw=1)
    big = ch[ch.n_titles >= 16]
    for g in ("neutral", "left", "right"):
        sub = big[big.judge_group == g]
        ax.scatter(sub.judge_score, sub.lexicon_score, s=22, color=GCOL[g], alpha=0.85, edgecolor=SURFACE, linewidth=0.6, label=f"{g} channels (by the judge)")
    ax.set_xlabel(f"channel score from {_nm(judge)}'s labels (−1 left … +1 right)"); ax.set_ylabel("channel score from the lexicon classes of the same titles (out of fold)")
    ax.set_title(f"A word list against the judge, channel by channel (Spearman {v.channel_spearman:.2f}, n = {int(v.n_channels)})"); ax.legend(fontsize=7.5, loc="upper left")
    ax.set_xlim(-1.05, 1.05); ax.set_ylim(-1.05, 1.05)
    ax = axes[1]
    conf = json.loads(v.confusion); classes = ["left", "neither", "right"]
    m = np.array([[conf[r][c] for c in classes] for r in classes], dtype=float); share = m / m.sum(axis=1, keepdims=True)
    ax.imshow(share, cmap=SEQ, vmin=0, vmax=1, aspect="auto")
    for i in range(3):
        for j in range(3):
            ax.text(j, i, f"{int(m[i, j]):,}\n{share[i, j]:.0%}", ha="center", va="center", fontsize=8.5, color="white" if share[i, j] > 0.55 else INK)
    ax.set_xticks(range(3), [f"lexicon: {c}" for c in classes], fontsize=8); ax.set_yticks(range(3), [f"{_nm(judge)}: {c}" for c in classes], fontsize=8); ax.grid(False)
    ax.set_title(f"Title by title: accuracy {v.accuracy:.0%}, kappa {v.kappa:.2f}; same side on {v.side_agreement_when_both_partisan:.0%} of titles both call partisan")
    fig.tight_layout(); save(fig, "14_lexicon_vs_judge.png")


def fig_allotax():
    """Allotaxonographs for document 14 (Dodds et al. 2023), drawn by allotaxonometer-ui through
    Node (pipeline_titles.allotax); skipped with a message when Node or its packages are missing."""
    from pipeline_titles import allotax
    if not allotax.available():
        print(f"allotaxonographs skipped: {allotax.UNAVAILABLE_MSG}")
        return
    allotax.main([])


def main() -> int:
    FIG.mkdir(parents=True, exist_ok=True)
    for fn in (fig_corpus, fig_topics, fig_formats, fig_landscape, fig_drift, fig_zipf_words, fig_zipf_views, fig_views_over_time, fig_caps_by_group, fig_profiles,
               fig_leaning, fig_leaning_channels, fig_leaning_stability, fig_leaning_logodds, fig_allotax):
        fn(); print("done", fn.__name__, flush=True)
    if (A / "assoc_summary.json").exists():
        from pipeline_titles import figures_associations
        figures_associations.main()
    print(f"{len(list(FIG.glob('*.png')))} figures in {FIG}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
