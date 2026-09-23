"""Figures for the word-association protocol (docs/word_association_protocol.md), drawn from the
assoc_* tables into pipeline_titles/reports/figures/assoc_*.png. Same style and palette as figures.py.

    assoc_01_trajectories.png   the daily breadth share of Iran, war and Epstein (seven-day centered mean)
    assoc_01b_small_multiples.png  the same for the twenty biggest spikes, one panel each
    assoc_02_crosscorrelation.png  raw and prewhitened cross-correlation by lag for the three pairs, with the
                                band, and the event study around Iran and war spike days
    assoc_03_heatmap.png        the eighty battery words against each other: log2 of the co-mention lift within
                                creator-weeks, blank where the pair does not pass in both channel halves, ordered
                                by network community
    assoc_04_monthly_matrices.png  the twenty spike words month by month: log2 lift among the month's edges
    assoc_05_network.png        the association network's 150 strongest terms, colored by community
    assoc_05b_ego.png           Epstein's and Iran's neighborhoods
    assoc_06_network_by_month.png  the same 150 terms on the same layout, with each month's own edges
    assoc_07_emerging.png       the strongest associations that appear in a month without being there the month before

    python -m pipeline_titles.figures_associations
"""

from __future__ import annotations

import math

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
import pandas as pd
from matplotlib.colors import TwoSlopeNorm
from matplotlib.lines import Line2D

from pipeline_titles.associations import GENERIC
from pipeline_titles.common import ANALYSIS_DIR as A, SEED
from pipeline_titles.figures import CAT, DIV, FIG, GRID, INK, INK2, MUTED, SEQ, SURFACE, rd, save

FOCUS = ["iran", "war", "epstein"]
FCOL = {"iran": CAT[0], "war": CAT[1], "epstein": CAT[2]}
EPISODES = [("2026-02-02", "Epstein files\nseason"), ("2026-02-28", "Iran war\nbegins")]
NODES_SHOWN = 150
COMMUNITY_HUES = 7           # the seven largest communities get a hue; the rest are gray


def smooth(x: np.ndarray, k: int = 7) -> np.ndarray:
    return pd.Series(x).rolling(k, center=True, min_periods=1).mean().to_numpy()


def _episodes(ax, days, y=0.98):
    for d, label in EPISODES:
        x = pd.Timestamp(d)
        ax.axvline(x, color=MUTED, linewidth=0.8)
        ax.text(x, y, " " + label, transform=ax.get_xaxis_transform(), fontsize=7.5, color=MUTED, va="top", ha="left")


def fig_trajectories():
    d = rd("assoc_case_daily.csv")
    days = pd.to_datetime(d["day"])
    fig, ax = plt.subplots(figsize=(10, 3.8))
    ends = {}
    for w in FOCUS:
        y = smooth(d[f"{w}_channels"].to_numpy() / d["active_channels"].to_numpy())
        ax.plot(days, y, color=FCOL[w], linewidth=2, label=w)
        ends[w] = float(y[-1])
    # end labels, pushed apart in log space when two series end together
    order = sorted(ends, key=lambda w: ends[w])
    ypos = [math.log10(ends[w]) for w in order]
    for i in range(1, len(ypos)):
        ypos[i] = max(ypos[i], ypos[i - 1] + 0.09)
    for w, yp in zip(order, ypos):
        ax.text(days.iloc[-1], 10 ** yp, "  " + w, color=FCOL[w], fontsize=8.5, va="center")
    ax.set_yscale("log")
    ax.yaxis.set_major_formatter(matplotlib.ticker.PercentFormatter(1.0, decimals=0))
    ax.yaxis.set_minor_formatter(matplotlib.ticker.NullFormatter())
    ax.set_yticks([0.02, 0.05, 0.1, 0.2, 0.5])
    ax.set_ylabel("share of active channels using the word (7-day mean)")
    ax.set_title("Iran, war and Epstein by day: two seasons, three to four weeks apart")
    _episodes(ax, days)
    ax.legend(loc="lower left", ncol=3)
    ax.margins(x=0.01)
    fig.tight_layout(); save(fig, "assoc_01_trajectories.png", "The share of channels active that day whose titles used the word. Log scale. 2026-01-01 to 2026-09-14.")

    words = rd("assoc_battery_words.csv")["word"].tolist()[:20]
    long = rd("assoc_daily.csv.gz")
    long = long[long["term"].isin(words)]
    days_all = pd.to_datetime(sorted(long["day"].unique()))
    fig, axes = plt.subplots(4, 5, figsize=(13, 7.2), sharex=True)
    for ax, w in zip(axes.ravel(), words):
        s = long[long["term"] == w].set_index(pd.to_datetime(long.loc[long["term"] == w, "day"]))["share_channels"].reindex(days_all).fillna(0).to_numpy()
        y = smooth(s)
        ax.fill_between(days_all, 0, y, color=CAT[0], alpha=0.18, linewidth=0)
        ax.plot(days_all, y, color=CAT[0], linewidth=1.4)
        peak = int(np.argmax(y))
        ax.plot(days_all[peak], y[peak], "o", color=CAT[0], markersize=4)
        ax.text(days_all[peak], y[peak], f" {y[peak]:.0%}", fontsize=7, color=INK2, va="bottom")
        ax.set_title(w, fontsize=9)
        ax.yaxis.set_major_formatter(matplotlib.ticker.PercentFormatter(1.0, decimals=0))
        ax.tick_params(labelsize=7)
        for d_, _ in EPISODES:
            ax.axvline(pd.Timestamp(d_), color=MUTED, linewidth=0.6)
    for ax in axes[-1]:
        ax.xaxis.set_major_locator(matplotlib.dates.MonthLocator(bymonth=[1, 4, 7]))
        ax.xaxis.set_major_formatter(matplotlib.dates.DateFormatter("%b"))
    fig.suptitle("The twenty biggest spikes of the year, by day", x=0.01, ha="left", fontsize=10.5, fontweight="bold")
    fig.tight_layout(); save(fig, "assoc_01b_small_multiples.png", "Share of active channels using the word, seven-day mean; the dot is the peak. Gray lines: the files season (Feb 2) and the war (Feb 28).")


def fig_crosscorrelation():
    cc = rd("assoc_case_ccf.csv"); ts = rd("assoc_case_timeseries.csv"); ev = rd("assoc_case_events.csv")
    pairs = [("epstein", "iran"), ("epstein", "war"), ("iran", "war")]
    fig, axes = plt.subplots(2, 3, figsize=(13, 6.4))
    for ax, (a, b) in zip(axes[0], pairs):
        g = cc[(cc["a"] == a) & (cc["b"] == b) & (cc["series"] == "pooled")].sort_values("lag_days")
        band = float(g["band"].iloc[0])
        ax.axhspan(-band, band, color=GRID, alpha=0.7, linewidth=0)
        ax.axhline(0, color=MUTED, linewidth=0.6)
        ax.axvline(0, color=MUTED, linewidth=0.6)
        ax.plot(g["lag_days"], g["ccf_residual"], color=CAT[0], linewidth=2, label="residual series")
        ax.plot(g["lag_days"], g["ccf_prewhitened"], color=CAT[1], linewidth=1.4, marker="o", markersize=3.5, label="prewhitened")
        t = ts[(ts["a"] == a) & (ts["b"] == b) & (ts["series"] == "pooled")].iloc[0]
        ax.set_title(f"{a} and {b}\npeak {t['max_abs_ccf_raw']:.2f}, shift p {'< 0.001' if t['p_max_ccf_shift'] < 0.001 else f'= {t['p_max_ccf_shift']:.2f}'}")
        ax.set_xlabel(f"lag in days  (left: {b} first;  right: {a} first)")
        ax.set_ylim(-0.5, 0.8)
        if ax is axes[0][0]:
            ax.set_ylabel("cross-correlation")
            ax.legend(loc="upper left")
    for ax, (src, tgt) in zip(axes[1], [("iran", "epstein"), ("war", "epstein"), ("iran", "war")]):
        g = ev[(ev["source"] == src) & (ev["target"] == tgt)].sort_values("lag_days")
        ax.fill_between(g["lag_days"], g["null_lo"], g["null_hi"], color=GRID, alpha=0.8, linewidth=0, label="95 % of random days")
        ax.axhline(0, color=MUTED, linewidth=0.6); ax.axvline(0, color=MUTED, linewidth=0.6)
        ax.plot(g["lag_days"], g["response"], color=FCOL[tgt], linewidth=2, label=f"{tgt} residual")
        out = g[g["outside"]]
        ax.plot(out["lag_days"], out["response"], "o", color=FCOL[tgt], markersize=5)
        n_ev = int(g["events"].iloc[0]); dates = g["event_days"].iloc[0]
        ax.set_title(f"{tgt} around {src} spike days\n({n_ev} days: {dates.replace(',', ', ')})")
        ax.set_xlabel(f"days after a {src} spike")
        if ax is axes[1][0]:
            ax.set_ylabel("mean residual log share")
            ax.legend(loc="lower left")
    fig.tight_layout(); save(fig, "assoc_02_crosscorrelation.png", "Top: cross-correlation of the detrended daily log shares at each lag; the gray band is +-1.96/sqrt(n) for the prewhitened series. Bottom: the event study, dots outside the band of 2,000 random day sets matched on weekday.")


def _order_by_community(words: list[str]) -> tuple[list[str], dict[str, int]]:
    nodes = rd("assoc_nodes.csv").set_index("term")
    comm = {w: int(nodes.loc[w, "community"]) if w in nodes.index else 10 ** 6 for w in words}
    strength = {w: float(nodes.loc[w, "strength"]) if w in nodes.index else 0.0 for w in words}
    order = sorted(words, key=lambda w: (comm[w], -strength[w], w))
    return order, comm


def fig_heatmap():
    b = rd("assoc_battery_pairs.csv"); words = rd("assoc_battery_words.csv")["word"].tolist()
    order, comm = _order_by_community(words)
    idx = {w: i for i, w in enumerate(order)}
    n = len(order)
    M = np.full((n, n), np.nan)
    for r in b.itertuples():
        if r.title_kind in ("none", "phrase") or not r.title_replicated:
            continue
        v = math.log2(r.week_lift) if r.week_lift > 0 else np.nan
        M[idx[r.a], idx[r.b]] = v; M[idx[r.b], idx[r.a]] = v
    fig, ax = plt.subplots(figsize=(13.5, 12.5))
    lim = 3.0
    im = ax.imshow(np.clip(M, -lim, lim), cmap=DIV, norm=TwoSlopeNorm(vmin=-lim, vcenter=0, vmax=lim), interpolation="nearest")
    ax.set_xticks(range(n), order, rotation=90, fontsize=7); ax.set_yticks(range(n), order, fontsize=7)
    ax.grid(False)
    # community boundaries
    bounds = [i for i in range(1, n) if comm[order[i]] != comm[order[i - 1]]]
    for bnd in bounds:
        ax.axhline(bnd - 0.5, color=SURFACE, linewidth=1.5); ax.axvline(bnd - 0.5, color=SURFACE, linewidth=1.5)
    for w in FOCUS:
        if w in idx:
            ax.get_xticklabels()[idx[w]].set_color(FCOL[w]); ax.get_yticklabels()[idx[w]].set_color(FCOL[w])
            ax.get_xticklabels()[idx[w]].set_fontweight("bold"); ax.get_yticklabels()[idx[w]].set_fontweight("bold")
    cb = fig.colorbar(im, ax=ax, fraction=0.025, pad=0.01)
    cb.set_label("log2 of co-mentions over those expected within creator-weeks  (2 = four times, -2 = a quarter)")
    ax.set_title("Eighty words against each other: co-mention (red) and avoidance (blue) within the same channel and week, ordered by network community")
    fig.tight_layout(); save(fig, "assoc_03_heatmap.png", "Blank: the pair does not pass the stratified test in both channel halves, or is a word with its own phrase. Thin white lines separate the year's communities.")


def fig_monthly_matrices():
    nb = rd("assoc_monthly_neighbors.csv.gz"); words = rd("assoc_battery_words.csv")["word"].tolist()[:20]
    order, _ = _order_by_community(words)
    idx = {w: i for i, w in enumerate(order)}
    months = sorted(nb["month"].unique())
    fig, axes = plt.subplots(3, 3, figsize=(12.5, 12), sharex=True, sharey=True)
    vmax = 4.0
    for ax, m in zip(axes.ravel(), months):
        M = np.full((len(order), len(order)), np.nan)
        g = nb[(nb["month"] == m) & nb["term"].isin(order) & nb["neighbor"].isin(order)]
        for r in g.itertuples():
            v = math.log2(r.lift)
            M[idx[r.term], idx[r.neighbor]] = v; M[idx[r.neighbor], idx[r.term]] = v
        im = ax.imshow(np.clip(M, 0, vmax), cmap=SEQ, vmin=0, vmax=vmax, interpolation="nearest")
        ax.set_xticks(range(len(order)), order, rotation=90, fontsize=7); ax.set_yticks(range(len(order)), order, fontsize=7)
        ax.tick_params(labelbottom=True, labelleft=True)
        ax.grid(False)
        ax.set_title(pd.Timestamp(m + "-01").strftime("%B 2026") + (" (to the 14th)" if m == "2026-09" else ""), fontsize=9.5)
    fig.suptitle("The twenty spike words month by month: which pairs share titles beyond chance", x=0.01, ha="left", fontsize=10.5, fontweight="bold")
    fig.tight_layout(rect=[0, 0.02, 0.93, 0.97], h_pad=1.2)
    cax = fig.add_axes([0.945, 0.35, 0.012, 0.3])
    cb = fig.colorbar(im, cax=cax)
    cb.set_label("log2 lift within creator-weeks (edges only)", fontsize=8)
    save(fig, "assoc_04_monthly_matrices.png", "A cell is filled when the pair is one of either word's twenty strongest edges that month (q < 0.01 within creator-weeks, lift >= 2, >= 3 channels). Same order in every panel.")


def _graph_and_layout():
    nodes = rd("assoc_nodes.csv").sort_values("strength", ascending=False)
    top = nodes.head(NODES_SHOWN)
    keep = set(top["term"])
    edges = rd("assoc_edges.csv")
    edges = edges[edges["term_a"].isin(keep) & edges["term_b"].isin(keep)]
    G = nx.Graph()
    for r in top.itertuples():
        G.add_node(r.term, strength=float(r.strength), community=int(r.community))
    for r in edges.itertuples():
        G.add_edge(r.term_a, r.term_b, weight=float(r.weight), lift=float(r.lift_strat))
    pos = nx.spring_layout(G, weight="weight", k=0.9 / math.sqrt(max(G.number_of_nodes(), 1)), iterations=300, seed=SEED)
    sizes = nodes.groupby("community").size().sort_values(ascending=False)
    hue_of = {c: CAT[i] for i, c in enumerate(sizes.index[:COMMUNITY_HUES])}
    comm_terms = rd("assoc_communities.csv").set_index("community")["top_terms"]
    return G, pos, hue_of, comm_terms


def _draw(ax, G, pos, hue_of, edges=None, faint_nodes=(), label_top=40, edge_alpha=0.35):
    E = list(G.edges(data=True)) if edges is None else edges
    for u, v, d in E:
        ax.plot([pos[u][0], pos[v][0]], [pos[u][1], pos[v][1]], color=INK2, alpha=edge_alpha * min(1.0, 0.3 + d.get("weight", 1) / 4), linewidth=0.5 + 0.25 * d.get("weight", 1), zorder=1)
    for n_, d in G.nodes(data=True):
        col = hue_of.get(d["community"], "#b3b2ad")
        alpha = 0.25 if n_ in faint_nodes else 1.0
        ax.scatter(pos[n_][0], pos[n_][1], s=12 + 1.1 * d["strength"], color=col, alpha=alpha, edgecolors=SURFACE, linewidths=1.2, zorder=2)
    strong = sorted(G.nodes(data=True), key=lambda kv: -kv[1]["strength"])[:label_top]
    for n_, d in strong:
        if n_ in faint_nodes:
            continue
        ax.text(pos[n_][0], pos[n_][1], n_, fontsize=7 if n_ not in FOCUS else 9, fontweight="normal" if n_ not in FOCUS else "bold", color=INK, ha="center", va="center", zorder=3)
    for w in FOCUS:
        if w in G and w not in [n_ for n_, _ in strong]:
            ax.text(pos[w][0], pos[w][1], w, fontsize=9, fontweight="bold", color=INK, ha="center", va="center", zorder=3)
    ax.set_xticks([]); ax.set_yticks([]); ax.grid(False)
    for s in ax.spines.values():
        s.set_visible(False)


def fig_network():
    G, pos, hue_of, comm_terms = _graph_and_layout()
    fig, ax = plt.subplots(figsize=(13, 11))
    _draw(ax, G, pos, hue_of)
    handles = [Line2D([0], [0], marker="o", color="none", markerfacecolor=hue_of[c], markersize=8, label=f"{', '.join(str(comm_terms[c]).split(', ')[:4])}") for c in hue_of]
    handles.append(Line2D([0], [0], marker="o", color="none", markerfacecolor="#b3b2ad", markersize=8, label="other communities"))
    ax.legend(handles=handles, loc="lower left", fontsize=8, title="community (its four strongest terms)", title_fontsize=8)
    ax.set_title(f"The association network: the {NODES_SHOWN} strongest terms, edges = co-mention beyond chance within creator-weeks, replicated in both channel halves")
    fig.tight_layout(); save(fig, "assoc_05_network.png", "Node size: strength (the sum of its edges' log2 lifts). Layout: force-directed, weighted by lift, seed fixed. Labels: the forty strongest terms and the three focus words.")
    return G, pos, hue_of

    
def fig_ego():
    nodes = rd("assoc_nodes.csv").set_index("term"); edges = rd("assoc_edges.csv")
    fig, axes = plt.subplots(1, 2, figsize=(14, 6.8))
    for ax, w in zip(axes, ["epstein", "iran"]):
        e = edges[(edges["term_a"] == w) | (edges["term_b"] == w)].copy()
        e["other"] = np.where(e["term_a"] == w, e["term_b"], e["term_a"])
        e = e.sort_values("lift_strat", ascending=False).head(28)
        others = e["other"].tolist()
        G = nx.Graph(); G.add_node(w)
        for r in e.itertuples():
            G.add_edge(w, r.other, weight=float(r.weight), lift=float(r.lift_strat))
        among = edges[edges["term_a"].isin(others) & edges["term_b"].isin(others)]
        for r in among.itertuples():
            G.add_edge(r.term_a, r.term_b, weight=float(r.weight), lift=float(r.lift_strat))
        pos = nx.spring_layout(G, weight="weight", k=0.45, iterations=400, seed=SEED)
        pos[w] = np.array([0.0, 0.0])
        for u, v, d in G.edges(data=True):
            is_hub = w in (u, v)
            ax.plot([pos[u][0], pos[v][0]], [pos[u][1], pos[v][1]], color=FCOL[w] if is_hub else INK2, alpha=0.55 if is_hub else 0.2, linewidth=0.6 + 0.35 * d["weight"], zorder=1)
        for n_ in G.nodes:
            c = int(nodes.loc[n_, "community"]) if n_ in nodes.index else -1
            ax.scatter(pos[n_][0], pos[n_][1], s=90 if n_ == w else 34, color=FCOL[w] if n_ == w else "#b3b2ad", edgecolors=SURFACE, linewidths=1.2, zorder=2)
            lift = G[w][n_]["lift"] if n_ != w and G.has_edge(w, n_) else None
            ax.text(pos[n_][0], pos[n_][1] + (0.06 if n_ != w else 0.09), n_ if n_ == w else f"{n_} ({lift:.0f}x)", fontsize=7.5 if n_ != w else 10, fontweight="normal" if n_ != w else "bold", color=INK, ha="center", va="bottom", zorder=3)
        ax.set_title(f"{w}: its {len(others)} strongest partners, and the edges among them")
        ax.set_xticks([]); ax.set_yticks([]); ax.grid(False)
        for s in ax.spines.values():
            s.set_visible(False)
        ax.margins(0.12)
    fig.tight_layout(); save(fig, "assoc_05b_ego.png", "Colored edges: the word's own edges, labeled with the lift (co-mentions over those expected within creator-weeks). Gray edges: partners that are also edges with each other.")


def fig_network_by_month(G, pos, hue_of):
    nb = rd("assoc_monthly_neighbors.csv.gz")
    keep = set(G.nodes)
    months = sorted(nb["month"].unique())
    fig, axes = plt.subplots(3, 3, figsize=(15, 14))
    for ax, m in zip(axes.ravel(), months):
        g = nb[(nb["month"] == m) & nb["term"].isin(keep) & nb["neighbor"].isin(keep)]
        seen = set(); E = []
        for r in g.itertuples():
            key = tuple(sorted((r.term, r.neighbor)))
            if key in seen:
                continue
            seen.add(key); E.append((key[0], key[1], {"weight": math.log2(r.lift)}))
        active = {u for u, v, _ in E} | {v for u, v, _ in E}
        _draw(ax, G, pos, hue_of, edges=E, faint_nodes=set(G.nodes) - active, label_top=22, edge_alpha=0.5)
        ax.set_title(f"{pd.Timestamp(m + '-01').strftime('%B')}: {len(E)} edges among the {len(active)} terms with an edge", fontsize=9.5)
    fig.suptitle("The same 150 terms on the same layout, month by month: each month's own edges", x=0.01, ha="left", fontsize=10.5, fontweight="bold")
    fig.tight_layout(rect=[0, 0.01, 1, 0.975]); save(fig, "assoc_06_network_by_month.png", "An edge: one word is among the other's twenty strongest partners that month (q < 0.01 within creator-weeks, lift >= 2, >= 3 channels). Colors: the full-year communities. Faint: no edge that month.")


def fig_emerging():
    nb = rd("assoc_monthly_neighbors.csv.gz")
    months = sorted(nb["month"].unique())
    present = {m: set(tuple(sorted(p)) for p in zip(g["term"], g["neighbor"])) for m, g in nb.groupby("month")}
    rows = []
    for m0, m1 in zip(months, months[1:]):
        g = nb[nb["month"] == m1]
        seen = set()
        for r in g.itertuples():
            key = tuple(sorted((r.term, r.neighbor)))
            if key in seen or key in present[m0]:
                continue
            seen.add(key)
            rows.append({"month": m1, "a": key[0], "b": key[1], "lift": r.lift, "z": r.z, "observed": r.observed, "channels": r.channels})
    em = pd.DataFrame(rows)
    # established words only: both used by >= 20 channels in the previous month
    daily = rd("assoc_daily.csv.gz")
    daily["month"] = daily["day"].str[:7]
    mc = daily.groupby(["month", "term"])["channels"].apply(lambda c: int((c > 0).sum()))
    prev = dict(zip(months[1:], months))
    def established(r):
        m0 = prev[r.month]
        return mc.get((m0, r.a), 0) >= 20 and mc.get((m0, r.b), 0) >= 20
    em = em[(em["channels"] >= 10) & (em["observed"] >= 30)]
    em = em[[established(r) for r in em.itertuples()]]
    # no pair whose terms share a word ("epic fury" with "operation epic"), and one row per story: a word appears once per month
    em = em[[not (set(r.a.split()) & set(r.b.split())) and not ({r.a, r.b} & GENERIC) for r in em.itertuples()]].sort_values("z", ascending=False)
    used, keep = set(), []
    for r in em.itertuples():
        words_ = {(r.month, w) for w in r.a.split() + r.b.split()}
        if words_ & used:
            continue
        used |= words_; keep.append(r.Index)
    em = em.loc[keep].head(30)
    fig, ax = plt.subplots(figsize=(10, 8.4))
    y = np.arange(len(em))
    ax.barh(y, np.log2(em["lift"]), color=CAT[0], height=0.62)
    ax.set_yticks(y, [f"{r.a} + {r.b}" for r in em.itertuples()])
    ax.invert_yaxis(); ax.grid(axis="y", visible=False)
    for yi, r in zip(y, em.itertuples()):
        ax.text(math.log2(r.lift), yi, f"  {r.lift:.0f}x, {int(r.observed)} titles, {int(r.channels)} ch, {pd.Timestamp(r.month + '-01').strftime('%b')}", va="center", fontsize=7.5, color=INK2)
    ax.set_xlabel("log2 lift within creator-weeks in the month the pair appears")
    ax.set_title("The strongest new associations between established words: an edge this month, not the month before")
    ax.margins(x=0.25)
    fig.tight_layout(); save(fig, "assoc_07_emerging.png", "Ranked by the stratified z of the month; pairs with at least 30 co-mentions from 10 channels, both words used by 20 channels the month before, terms sharing no word, one row per word and month.")


def main() -> int:
    FIG.mkdir(parents=True, exist_ok=True)
    fig_trajectories(); print("done trajectories", flush=True)
    fig_crosscorrelation(); print("done cross-correlation", flush=True)
    fig_heatmap(); print("done heatmap", flush=True)
    fig_monthly_matrices(); print("done monthly matrices", flush=True)
    G, pos, hue_of = fig_network(); print("done network", flush=True)
    fig_ego(); print("done ego", flush=True)
    fig_network_by_month(G, pos, hue_of); print("done network by month", flush=True)
    fig_emerging(); print("done emerging", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
