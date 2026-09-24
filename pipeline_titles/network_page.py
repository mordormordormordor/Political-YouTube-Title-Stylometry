"""The word-association network as a page to explore (pipeline_titles/reports/word_network.html).

Nodes are the vocabulary terms of the associations stage; an edge is a pair that co-mentions
beyond chance within creator-weeks (Cochran-Mantel-Haenszel q < 0.01), replicated in both channel
halves, with lift >= 2 from >= 5 channels (assoc_edges.csv, assoc_nodes.csv); the month view uses
each month's own edges (assoc_monthly_neighbors.csv.gz); the timeline uses each node's titles and
channels per month (assoc_node_months.csv). The left, neutral and right channels' own networks
(assoc_edges_<group>.csv and companions) sit beside the whole; "left only", "right only" and "left
and right" are derived in the page from the edge sets. Every network is drawn on one shared layout
(ForceAtlas2 over the union of the networks' edges, seed fixed), so the same word is in the same
place in every network and two networks can be compared side by side.

Two views. Communities: one disc per community, sized by its words, joined by the pairs crossing
between communities; a card per community. Words: every node and edge; a click gives a word's
partners, a strip of its months, and, when two panels are open, a card comparing the word across
the networks. Degree and strength are recomputed from the edges on screen (month, lift threshold);
betweenness is the year's, precomputed per network; community detection is Louvain run in the
browser, with a resolution slider and a reshuffle. Self-contained: no network access, no libraries.

    python -m pipeline_titles.network_page                # everything
    python -m pipeline_titles.network_page --no-leaning   # word_network_site.html: nothing derived from the leaning labels
"""

from __future__ import annotations

import json
from pathlib import Path

import networkx as nx
import numpy as np
import pandas as pd

from pipeline_titles.common import ANALYSIS_DIR as A, REPORTS_DIR, SEED
from pipeline_titles.figures import CAT

OUT = REPORTS_DIR / "word_network.html"
GROUPS = ("left", "neutral", "right")
EXTRA_NETWORKS = GROUPS + ("title_left", "title_neither", "title_right")   # any assoc_edges_<name>.csv with its nodes and node months


def read_network(suffix: str) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    return pd.read_csv(A / f"assoc_nodes{suffix}.csv"), pd.read_csv(A / f"assoc_edges{suffix}.csv"), pd.read_csv(A / f"assoc_node_months{suffix}.csv").set_index("term")


def build_data(with_leaning: bool = True) -> dict:
    """The page's data. with_leaning=False leaves out everything derived from the leaning labels (the
    audience networks, the title-lean networks, the co-mentions by audience on each edge)."""
    nets = {"all": read_network("")}
    if with_leaning:
        for g in EXTRA_NETWORKS:
            if all((A / f"assoc_{k}_{g}.csv").exists() for k in ("edges", "nodes", "node_months")):
                nets[g] = read_network(f"_{g}")
    months = sorted(c[len("titles_"):] for c in nets["all"][2].columns if c.startswith("titles_"))
    # one layout for every network: ForceAtlas2 over the union of the edges, each pair at its heaviest weight
    G = nx.Graph()
    for key, (nodes, edges, _) in nets.items():
        for r in nodes.itertuples():
            G.add_node(r.term)
        for r in edges.itertuples():
            w = float(r.weight)
            if G.has_edge(r.term_a, r.term_b):
                G[r.term_a][r.term_b]["weight"] = max(G[r.term_a][r.term_b]["weight"], w)
            else:
                G.add_edge(r.term_a, r.term_b, weight=w)
    union = sorted(G.nodes())
    pos = nx.forceatlas2_layout(G, max_iter=400, weight="weight", seed=SEED, scaling_ratio=2.0, gravity=1.0)
    xy = np.array([pos[t] for t in union])
    xy = (xy - xy.mean(axis=0)) / xy.std(axis=0).max()
    idx = {t: i for i, t in enumerate(union)}
    data = {"terms": union, "x": [round(float(v), 4) for v in xy[:, 0]], "y": [round(float(v), 4) for v in xy[:, 1]], "networks": {}, "palette": CAT[:7],
            "meta": {"months": months}}
    aud = json.loads((A / "assoc_audience.json").read_text()) if (A / "assoc_audience.json").exists() and with_leaning else {"titles": {}}
    data["group_titles"] = aud["titles"]
    for key, (nodes, edges, nm) in nets.items():
        has_co = with_leaning and all(c in edges.columns for c in ("co_left", "co_neutral", "co_right"))
        n_rows = [[idx[r.term], int(r.n_titles), round(float(r.betweenness), 5), int(r.community),
                   [int(nm.loc[r.term, f"titles_{m}"]) for m in months], [int(nm.loc[r.term, f"channels_{m}"]) for m in months]] for r in nodes.itertuples()]
        e_rows = [[idx[r.term_a], idx[r.term_b], round(float(r.lift_strat), 2), round(float(r.z_cmh), 1), int(r.channels), int(r.observed)] + ([int(r.co_left), int(r.co_neutral), int(r.co_right)] if has_co else [])
                  for r in edges.itertuples()]
        net = {"nodes": n_rows, "edges": e_rows, "monthly": {}}
        if key == "all":
            nb = pd.read_csv(A / "assoc_monthly_neighbors.csv.gz")
            nb = nb[nb["term"].isin(idx) & nb["neighbor"].isin(idx)]
            for m, g in nb.groupby("month"):
                seen = {}
                for r in g.itertuples():
                    k2 = (min(idx[r.term], idx[r.neighbor]), max(idx[r.term], idx[r.neighbor]))
                    if k2 not in seen:
                        seen[k2] = [k2[0], k2[1], round(float(r.lift), 2), int(r.channels), int(r.observed)]
                net["monthly"][m] = list(seen.values())
        data["networks"][key] = net
        print(f"{key}: {len(n_rows)} nodes, {len(e_rows)} edges", flush=True)
    data["meta"]["nodes"] = len(nets["all"][0]); data["meta"]["edges"] = len(nets["all"][1])
    return data


TEMPLATE = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Word association network</title>
<style>
:root { --ink:#0b0b0b; --ink2:#52514e; --muted:#8a8983; --grid:#e6e5e1; --surface:#fcfcfb; --panel:#f4f3f0; --accent:#2a78d6; }
* { box-sizing:border-box; }
html, body { margin:0; height:100%; background:var(--surface); color:var(--ink); font:14px/1.45 -apple-system, "Segoe UI", Helvetica, Arial, sans-serif; }
header { padding:10px 16px 8px; border-bottom:1px solid var(--grid); }
h1 { font-size:17px; margin:0 0 2px; display:inline-block; margin-right:14px; }
header p { margin:4px 0 8px; color:var(--ink2); font-size:13px; }
.tabs { display:inline-flex; gap:2px; vertical-align:middle; margin-right:14px; }
.tabs button, button.small { font:inherit; font-size:13px; padding:3px 10px; border:1px solid var(--grid); background:var(--panel); color:var(--ink2); cursor:pointer; border-radius:4px; }
.tabs button.on, button.small.on { background:var(--accent); color:#fff; border-color:var(--accent); }
.controls { display:flex; flex-wrap:wrap; gap:8px 16px; align-items:center; font-size:13px; }
.controls label { display:flex; align-items:center; gap:6px; color:var(--ink2); white-space:nowrap; }
input[type=search] { padding:4px 8px; border:1px solid var(--grid); border-radius:4px; font:inherit; width:170px; }
select { font:inherit; font-size:13px; padding:3px 6px; }
.legend { display:flex; flex-wrap:wrap; gap:6px 12px; align-items:center; }
.legend .who { color:var(--muted); font-size:12px; }
.chip { display:inline-flex; align-items:center; gap:5px; cursor:pointer; user-select:none; color:var(--ink2); }
.chip.off { opacity:.35; }
.chip i { width:11px; height:11px; border-radius:50%; display:inline-block; }
main { display:flex; height:calc(100% - 150px); }
.stages { flex:1; display:flex; min-width:0; }
.stage { flex:1; position:relative; min-width:0; }
.stage + .stage { border-left:1px solid var(--grid); }
.stage canvas { position:absolute; inset:0; width:100%; height:100%; display:block; cursor:grab; }
.stage .head { position:absolute; left:8px; top:6px; z-index:2; display:flex; gap:6px; align-items:center; font-size:12px; color:var(--ink2); background:rgba(252,252,251,0.85); padding:3px 6px; border-radius:4px; }
#timeline { position:absolute; left:0; right:0; bottom:0; max-height:0; overflow:hidden; border-top:1px solid var(--grid); background:rgba(244,243,240,0.94); transition:max-height .15s; z-index:3; }
#timeline.open { max-height:190px; overflow:auto; }
#timeline .close { position:absolute; right:10px; top:6px; cursor:pointer; color:var(--muted); font-size:12px; }
.tl { display:grid; grid-template-columns:repeat(9, 1fr); gap:6px; padding:8px 12px; font-size:12px; }
.tl .m { border-left:1px solid var(--grid); padding-left:6px; min-width:0; }
.tl .m h4 { margin:0 0 2px; font-size:12px; color:var(--ink); font-weight:600; }
.tl .bar { height:6px; background:var(--accent); border-radius:3px; margin:2px 0 4px; }
.tl .cnt { color:var(--muted); font-size:11px; margin-bottom:3px; }
.tl .p { color:var(--ink2); white-space:nowrap; overflow:hidden; text-overflow:ellipsis; cursor:pointer; }
.tl .p:hover { color:var(--accent); }
aside { width:370px; border-left:1px solid var(--grid); background:var(--panel); padding:12px 14px; overflow:auto; font-size:13px; }
aside h2 { font-size:15px; margin:0 0 4px; }
aside h3 { font-size:13px; margin:12px 0 4px; color:var(--ink2); }
aside .sub { color:var(--muted); margin-bottom:8px; }
table { border-collapse:collapse; width:100%; }
th, td { text-align:left; padding:3px 4px; border-bottom:1px solid var(--grid); font-variant-numeric:tabular-nums; vertical-align:top; }
th { color:var(--muted); font-weight:600; font-size:12px; }
td.num, th.num { text-align:right; }
tr.link { cursor:pointer; }
tr.link:hover { background:#ebeae6; }
.card { border:1px solid var(--grid); border-radius:6px; padding:8px 10px; margin-bottom:8px; background:var(--surface); cursor:pointer; }
.card:hover { border-color:var(--accent); }
.card.on { border-color:var(--ink); }
.card b { display:flex; align-items:center; gap:6px; }
.card i, .dot { width:10px; height:10px; border-radius:50%; display:inline-block; }
.dot { width:9px; height:9px; margin-right:4px; }
.card .w { color:var(--ink2); font-size:12px; }
.card .mm { color:var(--muted); font-size:11px; margin-top:2px; }
.tip { position:fixed; pointer-events:none; background:#fff; border:1px solid var(--grid); border-radius:4px; padding:6px 8px; font-size:12px; color:var(--ink2); box-shadow:0 2px 8px rgba(0,0,0,.08); display:none; z-index:5; max-width:280px; }
.tip b { color:var(--ink); }
.note { color:var(--muted); font-size:12px; margin-top:12px; }
a.x { color:var(--accent); cursor:pointer; }
@media (max-width: 800px) { main { flex-direction:column; } aside { width:auto; height:40%; border-left:0; border-top:1px solid var(--grid); } .tl { grid-template-columns:repeat(3, 1fr); } }
</style>
</head>
<body>
<header>
  <h1>Word association network</h1>
  <span class="tabs"><button id="tabC" class="on">Communities</button><button id="tabW">Words</button></span>
  <button class="small" id="compare">compare right vs left</button>
  <p id="intro">__NODES__ words, __EDGES__ edges. An edge joins two words that share titles beyond chance within the same channel and week, in both random halves of the channels (lift at least 2, from at least 5 channels). Start from the communities; open one to see its words.</p>
  <div class="controls">
    <label>Find <input type="search" id="q" list="terms" placeholder="a word"><datalist id="terms"></datalist></label>
    <label>Edges of <select id="month"><option value="all">the whole year</option></select></label>
    <label>Lift ≥ <input type="range" id="lift" min="1" max="6" step="0.25" value="1" style="width:90px"> <span id="liftv">2x</span></label>
    <label>Size by <select id="sizeby"><option value="strength">strength</option><option value="degree">degree</option><option value="betweenness">betweenness</option><option value="titles">titles</option></select></label>
    <label>Color by <select id="colorby"><option value="community">community</option><option value="betweenness">betweenness</option><option value="strength">strength</option></select></label>
    <label>Edge color <select id="edgecolor"><option value="strength">strength</option><option value="audience">audience</option></select></label>
    <label>Communities: resolution <input type="range" id="res" min="0.4" max="2.0" step="0.1" value="1.0" style="width:90px"> <span id="resv">1.0</span></label>
    <button class="small" id="reshuffle" title="run Louvain again with a new random order">reshuffle</button>
    <button class="small" id="fit" title="fit the view to what is shown">fit</button>
    <label><input type="checkbox" id="labels" checked> labels</label>
  </div>
  <div class="legend" id="legend" style="margin-top:6px"></div>
</header>
<main>
  <div class="stages" id="stages"></div>
  <aside id="panel"></aside>
</main>
<div class="tip" id="tip"></div>
<script id="data" type="application/json">__DATA__</script>
<script>
// ---------- pure functions: Louvain, modularity ----------
function mulberry32(a) { return function() { a |= 0; a = a + 0x6D2B79F5 | 0; let t = Math.imul(a ^ a >>> 15, 1 | a); t = t + Math.imul(t ^ t >>> 7, 61 | t) ^ t; return ((t ^ t >>> 14) >>> 0) / 4294967296; }; }
function louvain(n, edges, resolution, seed) {
  const rnd = mulberry32(seed);
  let nodes = n, E = edges.map(e => [e[0], e[1], e[2]]);
  let membership = Array.from({length: n}, (_, i) => i);
  for (let level = 0; level < 20; level++) {
    const adj = Array.from({length: nodes}, () => new Map());
    const k = new Float64Array(nodes); let m2 = 0;
    E.forEach(([i, j, w]) => { if (i === j) { k[i] += 2 * w; m2 += 2 * w; adj[i].set(i, (adj[i].get(i) || 0) + w); return; }
      adj[i].set(j, (adj[i].get(j) || 0) + w); adj[j].set(i, (adj[j].get(i) || 0) + w); k[i] += w; k[j] += w; m2 += 2 * w; });
    if (m2 === 0) break;
    const comm = Int32Array.from({length: nodes}, (_, i) => i), tot = Float64Array.from(k);
    let improved = true, moves = 0, rounds = 0;
    while (improved && rounds++ < 50) {
      improved = false;
      const order = Array.from({length: nodes}, (_, i) => i); for (let i = order.length - 1; i > 0; i--) { const j = Math.floor(rnd() * (i + 1)); [order[i], order[j]] = [order[j], order[i]]; }
      for (const i of order) {
        const ci = comm[i]; const links = new Map();
        adj[i].forEach((w, j) => { if (j !== i) links.set(comm[j], (links.get(comm[j]) || 0) + w); });
        tot[ci] -= k[i];
        let best = ci, bestGain = (links.get(ci) || 0) - resolution * tot[ci] * k[i] / m2;
        links.forEach((w, c) => { const gain = w - resolution * tot[c] * k[i] / m2; if (gain > bestGain + 1e-12) { bestGain = gain; best = c; } });
        tot[best] += k[i];
        if (best !== ci) { comm[i] = best; improved = true; moves++; }
      }
    }
    const ids = new Map(); comm.forEach(c => { if (!ids.has(c)) ids.set(c, ids.size); });
    const newComm = Int32Array.from(comm, c => ids.get(c));
    membership = membership.map(s => newComm[s]);
    if (moves === 0 || ids.size === nodes) break;
    const agg = new Map();
    E.forEach(([i, j, w]) => { const a = newComm[i], b = newComm[j]; const key = a <= b ? a * ids.size + b : b * ids.size + a; agg.set(key, (agg.get(key) || 0) + w); });
    E = []; agg.forEach((w, key) => E.push([Math.floor(key / ids.size), key % ids.size, w])); nodes = ids.size;
  }
  return {comm: Int32Array.from(membership), modularity: modularity(n, edges, membership)};
}
function modularity(n, edges, comm) {
  const k = new Float64Array(n); let m2 = 0; edges.forEach(([i, j, w]) => { k[i] += w; k[j] += w; m2 += 2 * w; });
  if (m2 === 0) return 0;
  const tot = new Map(); for (let i = 0; i < n; i++) tot.set(comm[i], (tot.get(comm[i]) || 0) + k[i]);
  let inside = 0; edges.forEach(([i, j, w]) => { if (comm[i] === comm[j]) inside += 2 * w; });
  let s = 0; tot.forEach(t => s += t * t); return inside / m2 - s / (m2 * m2);
}
// ---------- data ----------
const D = JSON.parse(document.getElementById('data').textContent);
const T = D.terms, X = D.x, Y = D.y, U = T.length, MONTHS = D.meta.months, PAL = D.palette, GT = D.group_titles;
const byName = new Map(T.map((t, i) => [t, i]));
const NETNAME = {all: 'all channels', left: 'left channels', neutral: 'neutral channels', right: 'right channels', title_left: 'titles labeled left', title_neither: 'titles labeled neither', title_right: 'titles labeled right',
                 left_only: 'left only (edges the right channels lack)', right_only: 'right only (edges the left channels lack)', left_and_right: 'left and right (edges both make)'};
const NETS = {};   // key -> {nodes: Map(ui -> {n, b, c0, mt, mc}), edges}
Object.entries(D.networks).forEach(([k, v]) => { NETS[k] = {nodes: new Map(v.nodes.map(r => [r[0], {n: r[1], b: r[2], c0: r[3], mt: r[4], mc: r[5]}])), edges: v.edges, monthly: v.monthly || {}}; });
function deriveDiff(a, b, keep) {   // edges of a whose pair is (keep=false) absent from b, or (keep=true) present in b
  const key = e => e[0] < e[1] ? e[0] + ':' + e[1] : e[1] + ':' + e[0];
  const inB = new Set(NETS[b].edges.map(key));
  const edges = NETS[a].edges.filter(e => inB.has(key(e)) === keep);
  const nodes = new Map(); edges.forEach(e => [e[0], e[1]].forEach(i => { if (!nodes.has(i)) nodes.set(i, {n: NETS[a].nodes.get(i)?.n || 0, b: 0, c0: 0, mt: NETS[a].nodes.get(i)?.mt || MONTHS.map(() => 0), mc: NETS[a].nodes.get(i)?.mc || MONTHS.map(() => 0)}); }));
  return {nodes, edges, monthly: {}, derived: true};
}
if (NETS.left && NETS.right) { NETS.left_only = deriveDiff('left', 'right', false); NETS.right_only = deriveDiff('right', 'left', false); NETS.left_and_right = deriveDiff('left', 'right', true); }
function audienceBalance(e) { if (e.length < 9 || !GT.left) return null; const l = e[6] / GT.left * 1000, r = e[8] / GT.right * 1000; if (l + r === 0) return null; return (r - l) / (r + l); }
function balanceColor(b) { const t = Math.abs(b); const base = b < 0 ? [42, 120, 214] : [235, 104, 52]; const g = [150, 149, 143]; return `rgba(${base.map((v, k) => Math.round(g[k] + (v - g[k]) * t)).join(',')},`; }
const monthName = m => new Date(m + '-15').toLocaleString('en-US', {month: 'long'});
const monthShort = m => new Date(m + '-15').toLocaleString('en-US', {month: 'short'});
// ---------- shared state ----------
let view = {k: 1, tx: 0, ty: 0}, dragging = false, moved = false, last = null;
let mode = 'communities', selected = -1, hover = -1, hoverPanel = null, month = 'all', minLift = 2, showLabels = true, sizeBy = 'strength', colorBy = 'community', edgeColor = 'strength';
let resolution = 1.0, seed = 1, compare = false, active = null;
let selComm = -1, openComm = -1, hidden = new Set();      // shared across panels: the communities are the whole network's
const REF = {comm: new Map(), info: [], cNodes: [], modularity: 0};
const tip = document.getElementById('tip'), panelEl = document.getElementById('panel'), stages = document.getElementById('stages');
const SEQ = ['#f4f8fd', '#cde2fb', '#6da7ec', '#256abf', '#0d366b'];
function ramp(v) { const t = Math.max(0, Math.min(1, v)); const p = t * (SEQ.length - 1), i = Math.floor(p), f = p - i; if (i >= SEQ.length - 1) return SEQ[SEQ.length - 1];
  const a = SEQ[i].match(/\w\w/g).map(h => parseInt(h, 16)), b = SEQ[i + 1].match(/\w\w/g).map(h => parseInt(h, 16)); return `rgb(${a.map((x, k) => Math.round(x + (b[k] - x) * f)).join(',')})`; }
// ---------- the shared communities: Louvain on the all-channel network, applied to every panel ----------
function runCommunities() {
  const net = NETS.all; const ids = [...net.nodes.keys()]; const local = new Map(ids.map((u, i) => [u, i]));
  const r = louvain(ids.length, net.edges.map(e => [local.get(e[0]), local.get(e[1]), Math.log2(e[2])]), resolution, seed);
  REF.comm = new Map(ids.map((u, i) => [u, r.comm[i]])); REF.modularity = r.modularity;
  // a word with edges only in another network joins the community most of its partners belong to
  const extra = Math.max(-1, ...r.comm) + 1;
  for (let u = 0; u < U; u++) if (!REF.comm.has(u)) {
    const votes = new Map();
    Object.values(NETS).forEach(net => net.edges.forEach(e => { if (e[0] !== u && e[1] !== u) return; const o = e[0] === u ? e[1] : e[0]; const c = REF.comm.get(o); if (c !== undefined && c < extra) votes.set(c, (votes.get(c) || 0) + Math.log2(e[2])); }));
    let best = extra, bw = -1; votes.forEach((w, c) => { if (w > bw) { bw = w; best = c; } });
    REF.comm.set(u, best);
  }
  const ys = new Map(); net.edges.forEach(e => { const w = Math.log2(e[2]); ys.set(e[0], (ys.get(e[0]) || 0) + w); ys.set(e[1], (ys.get(e[1]) || 0) + w); });
  const groups = new Map(); REF.comm.forEach((c, u) => { if (!groups.has(c)) groups.set(c, []); groups.get(c).push(u); });
  REF.info = [...groups.entries()].map(([id, members]) => {
    members.sort((a, b) => (ys.get(b) || 0) - (ys.get(a) || 0));
    const st = u => net.nodes.get(u) || {mt: MONTHS.map(() => 0), n: 0};
    return {id, members, size: members.length, top: members.slice(0, 10).map(u => T[u]),
            x: members.reduce((s, u) => s + X[u], 0) / members.length, y: members.reduce((s, u) => s + Y[u], 0) / members.length,
            months: MONTHS.map((_, k) => members.reduce((s, u) => s + (st(u).mt[k] || 0), 0)), titles: members.reduce((s, u) => s + st(u).n, 0)};
  }).sort((a, b) => b.size - a.size);
  REF.info.forEach((c, rank) => { c.rank = rank; c.color = rank < PAL.length ? PAL[rank] : '#b3b2ad'; c.label = c.top.slice(0, 3).join(', '); });
  // one disc layout for every panel, from the reference sizes
  REF.cNodes = REF.info.map(c => ({c, x: c.x, y: c.y, r: 0.03 + 0.11 * Math.sqrt(c.size / REF.info[0].size)}));
  for (let it = 0; it < 200; it++) for (let a = 0; a < REF.cNodes.length; a++) for (let b = a + 1; b < REF.cNodes.length; b++) {
    const A = REF.cNodes[a], B = REF.cNodes[b]; const dx = B.x - A.x, dy = B.y - A.y; const d = Math.hypot(dx, dy) || 1e-6, min = A.r + B.r + 0.02;
    if (d < min) { const push = (min - d) / 2; A.x -= dx / d * push; A.y -= dy / d * push; B.x += dx / d * push; B.y += dy / d * push; }
  }
  hidden = new Set(); selComm = -1; openComm = -1;
  panels.forEach(p => p.layoutCommunities());
}
const commInfoOf = id => REF.info.find(c => c.id === id);
const commOf = u => commInfoOf(REF.comm.get(u));
// ---------- a panel: one network on one canvas ----------
class Panel {
  constructor(key, label) {
    this.key = key; this.label = label;
    this.el = document.createElement('div'); this.el.className = 'stage';
    this.el.innerHTML = `<canvas></canvas><div class="head"><b>${label}</b> <select class="netsel"></select></div>`;
    stages.appendChild(this.el);
    this.canvas = this.el.querySelector('canvas'); this.ctx = this.canvas.getContext('2d');
    const sel = this.el.querySelector('.netsel');
    Object.keys(NETS).forEach(k => { const o = document.createElement('option'); o.value = k; o.textContent = NETNAME[k] || k; sel.appendChild(o); });
    sel.value = key; sel.addEventListener('change', e => { this.setNetwork(e.target.value); });
    if (Object.keys(NETS).length < 2) sel.style.display = 'none';
    this.bind(); this.setNetwork(key);
  }
  setNetwork(key) {
    this.key = key; this.net = NETS[key];
    this.el.querySelector('.netsel').value = key;
    this.buildEdges(); if (REF.info.length) this.layoutCommunities(); this.resize();
    if (panels.length) { buildLegend(); showPanel(); }
  }
  has(u) { return this.net.nodes.has(u); }
  buildEdges() {
    const m = month === 'all' || !this.net.monthly[month] ? null : month;
    this.edgesNow = m ? this.net.monthly[m].map(e => [e[0], e[1], e[2], NaN, e[3], e[4]]) : this.net.edges;
    this.adj = new Map(); this.deg = new Map(); this.str = new Map();
    this.edgesNow.forEach(e => {
      if (e[2] < minLift) return;
      const w = Math.log2(e[2]);
      [[e[0], e[1]], [e[1], e[0]]].forEach(([a, b]) => { if (!this.adj.has(a)) this.adj.set(a, []); this.adj.get(a).push({j: b, lift: e[2], z: e[3], ch: e[4], obs: e[5], e}); this.deg.set(a, (this.deg.get(a) || 0) + 1); this.str.set(a, (this.str.get(a) || 0) + w); });
    });
  }
  layoutCommunities() {
    // the shared discs, with this panel's own member counts and crossing pairs
    this.present = new Map(); this.net.nodes.forEach((_, u) => { const c = REF.comm.get(u); this.present.set(c, (this.present.get(c) || 0) + 1); });
    const agg = new Map();
    this.edgesNow.forEach(e => { if (e[2] < minLift) return; const a = REF.comm.get(e[0]), b = REF.comm.get(e[1]); if (a === b) return; const key = a < b ? a + ':' + b : b + ':' + a;
      const v = agg.get(key) || {a: Math.min(a, b), b: Math.max(a, b), n: 0, w: 0, top: []}; v.n++; v.w += Math.log2(e[2]); v.top.push(e); agg.set(key, v); });
    this.cEdges = [...agg.values()]; this.cEdges.forEach(v => v.top.sort((p, q) => q[2] - p[2]));
  }
  resize() {
    const r = this.canvas.getBoundingClientRect(); if (!r.width) return;
    this.canvas.width = r.width * devicePixelRatio; this.canvas.height = r.height * devicePixelRatio;
    this.ctx.setTransform(devicePixelRatio, 0, 0, devicePixelRatio, 0, 0);
    if (!view.init) { view.k = Math.min(r.width, r.height) * 0.42; view.tx = r.width / 2; view.ty = r.height / 2; view.init = true; }
    this.draw();
  }
  sx(u) { return X[u] * view.k + view.tx; } sy(u) { return Y[u] * view.k + view.ty; }
  measure(u) { return sizeBy === 'strength' ? (this.str.get(u) || 0) : sizeBy === 'degree' ? (this.deg.get(u) || 0) : sizeBy === 'betweenness' ? this.net.nodes.get(u).b : this.net.nodes.get(u).n; }
  radius(u) { return 2 + 9 * Math.sqrt(Math.max(0, this.measure(u)) / this.sizeMax); }
  visible(u) { return this.has(u) && !hidden.has(REF.comm.get(u)); }
  inFocus(u) { return openComm < 0 || REF.comm.get(u) === openComm; }
  colorOf(u) { if (colorBy === 'community') return commOf(u).color; const v = colorBy === 'betweenness' ? this.net.nodes.get(u).b : (this.str.get(u) || 0); return ramp(Math.sqrt(v / this.colorMax)); }
  draw() {
    const ctx = this.ctx, r = this.canvas.getBoundingClientRect();
    ctx.clearRect(0, 0, r.width, r.height);
    if (!REF.info.length) return;
    if (mode === 'communities') return this.drawCommunities(r);
    const ids = [...this.net.nodes.keys()].filter(u => this.visible(u) && this.inFocus(u));
    this.sizeMax = Math.max(1e-9, ...ids.map(u => this.measure(u)));
    this.colorMax = Math.max(1e-9, ...[...this.net.nodes.keys()].map(u => colorBy === 'betweenness' ? this.net.nodes.get(u).b : (this.str.get(u) || 0)));
    const focus = selected >= 0 ? new Set([selected, ...(this.adj.get(selected) || []).map(a => a.j)]) : null;
    ctx.lineCap = 'round';
    this.edgesNow.forEach(e => {
      if (e[2] < minLift || !this.visible(e[0]) || !this.visible(e[1]) || !this.inFocus(e[0]) || !this.inFocus(e[1])) return;
      const inF = focus && (e[0] === selected || e[1] === selected); if (focus && !inF) return;
      const w = Math.log2(e[2]); const bal = edgeColor === 'audience' ? audienceBalance(e) : null;
      ctx.strokeStyle = bal !== null ? balanceColor(bal) + (inF ? '0.9)' : `${Math.min(0.75, 0.25 + 0.25 * Math.abs(bal) + 0.05 * w)})`) : (inF ? 'rgba(42,120,214,0.75)' : `rgba(82,81,78,${Math.min(0.45, 0.05 + 0.05 * w)})`);
      ctx.lineWidth = Math.max(0.4, Math.min(3, 0.3 + 0.35 * w)) * (inF ? 1.4 : 1);
      ctx.beginPath(); ctx.moveTo(this.sx(e[0]), this.sy(e[0])); ctx.lineTo(this.sx(e[1]), this.sy(e[1])); ctx.stroke();
    });
    const order = [...this.net.nodes.keys()].filter(u => this.visible(u)).sort((a, b) => this.measure(a) - this.measure(b));
    order.forEach(u => {
      const dim = (focus && !focus.has(u)) || !this.inFocus(u);
      ctx.globalAlpha = dim ? 0.12 : 1;
      ctx.beginPath(); ctx.arc(this.sx(u), this.sy(u), this.radius(u), 0, Math.PI * 2);
      ctx.fillStyle = this.colorOf(u); ctx.fill();
      ctx.lineWidth = u === selected || (u === hover && hoverPanel === this) ? 2 : 1; ctx.strokeStyle = u === selected ? '#0b0b0b' : '#fcfcfb'; ctx.stroke();
      ctx.globalAlpha = 1;
    });
    if (showLabels) {
      ctx.textAlign = 'center'; ctx.textBaseline = 'bottom';
      const budget = Math.round(40 * Math.max(1, view.k / (Math.min(r.width, r.height) * 0.42)) ** 1.6);
      const labeled = new Set(order.filter(u => this.inFocus(u)).slice(-budget)); if (focus) focus.forEach(u => { if (this.has(u)) labeled.add(u); });
      const placed = [];
      [...labeled].sort((a, b) => this.measure(b) - this.measure(a)).forEach(u => {
        if (!this.visible(u) || !this.inFocus(u) || (focus && !focus.has(u))) return;
        ctx.font = (u === selected ? 'bold 12px' : '11px') + ' -apple-system, "Segoe UI", Helvetica, Arial, sans-serif';
        const x = this.sx(u), y = this.sy(u) - this.radius(u) - 2, w = ctx.measureText(T[u]).width;
        if (x < -20 || y < -20 || x > r.width + 20 || y > r.height + 20) return;
        if (placed.some(p => Math.abs(p.x - x) < (p.w + w) / 2 + 4 && Math.abs(p.y - y) < 13)) return;
        placed.push({x, y, w});
        ctx.strokeStyle = 'rgba(252,252,251,0.9)'; ctx.lineWidth = 3; ctx.strokeText(T[u], x, y);
        ctx.fillStyle = u === selected ? '#0b0b0b' : '#52514e'; ctx.fillText(T[u], x, y);
      });
    }
  }
  discRadius(cn) { const n = this.present.get(cn.c.id) || 0; return cn.r * Math.sqrt(n / cn.c.size); }
  drawCommunities(r) {
    const ctx = this.ctx, maxN = Math.max(1, ...panels.map(p => Math.max(1, ...p.cEdges.map(v => v.n))));
    const px = c => c.x * view.k + view.tx, py = c => c.y * view.k + view.ty;
    this.cEdges.forEach(v => {
      const A = REF.cNodes.find(c => c.c.id === v.a), B = REF.cNodes.find(c => c.c.id === v.b); if (!A || !B || hidden.has(v.a) || hidden.has(v.b)) return;
      const inF = selComm >= 0 && (v.a === selComm || v.b === selComm); if (selComm >= 0 && !inF) return;
      ctx.strokeStyle = inF ? 'rgba(42,120,214,0.7)' : 'rgba(82,81,78,0.35)'; ctx.lineWidth = 0.6 + 9 * Math.sqrt(v.n / maxN);
      ctx.beginPath(); ctx.moveTo(px(A), py(A)); ctx.lineTo(px(B), py(B)); ctx.stroke();
    });
    REF.cNodes.forEach(cn => {
      const c = cn.c; if (hidden.has(c.id)) return; const n = this.present.get(c.id) || 0;
      const dim = n === 0 || (selComm >= 0 && c.id !== selComm && !this.cEdges.some(v => (v.a === selComm && v.b === c.id) || (v.b === selComm && v.a === c.id)));
      ctx.globalAlpha = dim ? 0.18 : 1;
      const rad = Math.max(3, this.discRadius(cn) * view.k);
      ctx.beginPath(); ctx.arc(px(cn), py(cn), rad, 0, Math.PI * 2);
      ctx.fillStyle = c.color; ctx.fill(); ctx.lineWidth = c.id === selComm ? 2.5 : 1.5; ctx.strokeStyle = c.id === selComm ? '#0b0b0b' : '#fcfcfb'; ctx.stroke();
      if (showLabels && n > 0 && (rad > 14 || c.id === selComm)) {
        ctx.font = 'bold 12px -apple-system, "Segoe UI", Helvetica, Arial, sans-serif'; ctx.textAlign = 'center'; ctx.textBaseline = 'middle'; ctx.fillStyle = c.rank < PAL.length ? '#fff' : '#0b0b0b';
        const lines = c.top.slice(0, rad > 40 ? 3 : 1); lines.forEach((t, k) => ctx.fillText(t, px(cn), py(cn) + (k - (lines.length - 1) / 2) * 14));
        ctx.font = '11px -apple-system, "Segoe UI", Helvetica, Arial, sans-serif'; ctx.fillStyle = '#52514e'; ctx.textBaseline = 'top'; ctx.fillText(`${n} words`, px(cn), py(cn) + rad + 3);
      }
      ctx.globalAlpha = 1;
    });
  }
  nodeAt(pxl, pyl) {
    if (mode === 'communities') { let best = -1; REF.cNodes.forEach(cn => { if (hidden.has(cn.c.id) || !(this.present.get(cn.c.id) || 0)) return; if (Math.hypot(cn.x * view.k + view.tx - pxl, cn.y * view.k + view.ty - pyl) <= Math.max(3, this.discRadius(cn) * view.k) + 3) best = cn.c.id; }); return best; }
    let best = -1, bd = 1e9;
    this.net.nodes.forEach((_, u) => { if (!this.visible(u) || !this.inFocus(u)) return; const d = Math.hypot(this.sx(u) - pxl, this.sy(u) - pyl); if (d < Math.max(this.radius(u) + 3, 8) && d < bd) { bd = d; best = u; } });
    return best;
  }
  bind() {
    const c = this.canvas;
    c.addEventListener('mousedown', e => { dragging = true; moved = false; last = [e.clientX, e.clientY]; c.style.cursor = 'grabbing'; active = this; });
    c.addEventListener('mouseup', e => {
      if (dragging && !moved) { const r = c.getBoundingClientRect(); const i = this.nodeAt(e.clientX - r.left, e.clientY - r.top); active = this;
        if (mode === 'communities') { if (i >= 0 && i === selComm) openCommunity(i); else { selComm = i; showPanel(); drawAll(); } } else select(i); }
      dragging = false; c.style.cursor = 'grab';
    });
    c.addEventListener('mousemove', e => {
      const r = c.getBoundingClientRect(), pxl = e.clientX - r.left, pyl = e.clientY - r.top;
      if (dragging) { const dx = e.clientX - last[0], dy = e.clientY - last[1]; if (Math.abs(dx) + Math.abs(dy) > 2) moved = true; view.tx += dx; view.ty += dy; last = [e.clientX, e.clientY]; drawAll(); return; }
      const i = this.nodeAt(pxl, pyl);
      if (i !== hover || hoverPanel !== this) { hover = i; hoverPanel = this; drawAll(); }
      if (i >= 0) { tip.style.display = 'block'; tip.style.left = (e.clientX + 14) + 'px'; tip.style.top = (e.clientY + 14) + 'px';
        if (mode === 'communities') { const cc = commInfoOf(i); tip.innerHTML = `<b>${cc.top.slice(0, 5).join(', ')}</b><br>${cc.size} words in all channels · ${this.present.get(i) || 0} with an edge here · click to see, click again to open`; }
        else tip.innerHTML = `<b>${T[i]}</b><br>${this.net.nodes.get(i).n.toLocaleString()} titles · degree ${this.deg.get(i) || 0} · strength ${(this.str.get(i) || 0).toFixed(1)} · betweenness ${this.net.nodes.get(i).b}`; }
      else tip.style.display = 'none';
    });
    c.addEventListener('mouseleave', () => { tip.style.display = 'none'; hover = -1; drawAll(); });
    c.addEventListener('wheel', e => { e.preventDefault(); const r = c.getBoundingClientRect(), pxl = e.clientX - r.left, pyl = e.clientY - r.top; const f = Math.exp(-e.deltaY * 0.0015); view.tx = pxl - (pxl - view.tx) * f; view.ty = pyl - (pyl - view.ty) * f; view.k *= f; drawAll(); }, {passive: false});
  }
}
// ---------- panels ----------
const panels = [];
panels.push(new Panel('all', 'A'));
active = panels[0];
const timeline = document.createElement('div'); timeline.id = 'timeline'; stages.appendChild(timeline);
function drawAll() { panels.forEach(p => p.draw()); }
function resizeAll() { panels.forEach(p => p.resize()); }
function setCompare(on) {
  compare = on; document.getElementById('compare').classList.toggle('on', on); document.getElementById('compare').textContent = on ? 'one network' : 'compare right vs left';
  if (on && panels.length === 1) { panels[0].setNetwork('left'); panels.push(new Panel('right', 'B')); }
  if (!on && panels.length === 2) { const p = panels.pop(); p.el.remove(); active = panels[0]; panels[0].setNetwork('all'); }
  stages.appendChild(timeline); resizeAll(); buildLegend(); showPanel();
}
// ---------- side panel ----------
function buildLegend() {
  const legend = document.getElementById('legend'); legend.innerHTML = '';
  const w = document.createElement('span'); w.className = 'who'; w.textContent = `communities of all channels (${REF.info.length}, modularity ${REF.modularity.toFixed(2)}):`; legend.appendChild(w);
  REF.info.slice(0, PAL.length).forEach(c => { const s = document.createElement('span'); s.className = 'chip' + (openComm >= 0 && openComm !== c.id ? ' off' : ''); s.title = mode === 'words' ? 'show only this community (click again for all)' : 'select this community';
    s.innerHTML = `<i style="background:${c.color}"></i>${c.label} (${c.size})`;
    s.addEventListener('click', () => { if (mode === 'communities') { selComm = c.id; showPanel(); drawAll(); return; } openComm = openComm === c.id ? -1 : c.id; selected = -1; timeline.classList.remove('open'); timeline.innerHTML = ''; buildLegend(); showPanel(); drawAll(); }); legend.appendChild(s); });
  const others = document.createElement('span'); others.className = 'chip'; others.innerHTML = `<i style="background:#b3b2ad"></i>${Math.max(0, REF.info.length - PAL.length)} smaller`; legend.appendChild(others);
  if (colorBy !== 'community') { const s = document.createElement('span'); s.className = 'chip'; s.innerHTML = `<i style="background:linear-gradient(90deg,#cde2fb,#0d366b);border-radius:2px;width:40px"></i>${colorBy}, light to dark`; legend.appendChild(s); }
  if (edgeColor === 'audience' && GT.left) { const s = document.createElement('span'); s.className = 'chip'; s.innerHTML = `<i style="background:linear-gradient(90deg,#2a78d6,#96958f,#eb6834);border-radius:2px;width:60px"></i>edges (all channels): left makes the pair · both · right`; legend.appendChild(s); }
}
const dot = c => `<i class="dot" style="background:${c}"></i>`;
function communityCards() {
  let h = `<h2>${REF.info.length} communities</h2><div class="sub">Louvain on the all-channel network at resolution ${resolution.toFixed(1)}, modularity ${REF.modularity.toFixed(2)}, the same groups in every panel. Click a card or a disc; open it to see its words.</div>`;
  REF.info.forEach(c => {
    const peak = c.months.indexOf(Math.max(...c.months));
    const counts = panels.length > 1 ? panels.map(p => `${p.label} ${p.present.get(c.id) || 0}`).join(' · ') + ' words with an edge' : `linked to ${panels[0].cEdges.filter(v => v.a === c.id || v.b === c.id).length} communities`;
    h += `<div class="card${c.id === selComm ? ' on' : ''}" data-c="${c.id}"><b><i style="background:${c.color}"></i>${c.top.slice(0, 3).join(', ')} <span style="color:var(--muted);font-weight:normal">· ${c.size} words</span></b>
      <div class="w">${c.top.slice(3, 10).join(', ')}</div><div class="mm">peak ${monthName(MONTHS[peak])} · ${c.titles.toLocaleString()} title mentions · ${counts}</div></div>`;
  });
  panelEl.innerHTML = h;
  panelEl.querySelectorAll('.card').forEach(el => el.addEventListener('click', () => { selComm = +el.dataset.c; showPanel(); drawAll(); }));
}
function communityDetail(id) {
  const c = commInfoOf(id);
  let h = `<h2>${dot(c.color)} ${c.top.slice(0, 3).join(', ')}</h2><div class="sub">${c.size} words in all channels · ${c.titles.toLocaleString()} title mentions · <a class="x" id="open">open its words</a> · <a class="x" id="back">all communities</a></div>`;
  h += '<h3>Words, by strength</h3><div class="w" style="font-size:12px;color:var(--ink2)">' + c.members.slice(0, 30).map(u => `<a class="x" data-i="${u}">${T[u]}</a>`).join(', ') + (c.size > 30 ? ` and ${c.size - 30} more` : '') + '</div>';
  h += '<h3>Titles by month (all channels)</h3><div class="tl" style="grid-template-columns:repeat(9,1fr);padding:0">' + c.months.map((v, k) => `<div class="m"><h4>${monthShort(MONTHS[k])}</h4><div class="bar" style="width:${Math.round(100 * v / Math.max(1, ...c.months))}%"></div><div class="cnt">${v.toLocaleString()}</div></div>`).join('') + '</div>';
  panels.forEach(p => {
    const links = p.cEdges.filter(v => v.a === id || v.b === id).sort((a, b) => b.n - a.n);
    h += `<h3>${panels.length > 1 ? p.label + ': ' : ''}${NETNAME[p.key] || p.key}: ${p.present.get(id) || 0} of its words with an edge, linked to ${links.length} communities</h3>`;
    if (links.length) {
      h += `<table><tr><th>community</th><th class="num">pairs</th><th>strongest pair</th></tr>`;
      links.slice(0, 12).forEach(v => { const o = commInfoOf(v.a === id ? v.b : v.a); const t = v.top[0]; h += `<tr class="link" data-c="${o.id}"><td>${dot(o.color)}${o.top.slice(0, 2).join(', ')}</td><td class="num">${v.n}</td><td>${T[t[0]]} + ${T[t[1]]} (${t[2].toFixed(0)}x)</td></tr>`; });
      h += '</table>';
    }
  });
  h += '<div class="note">Cross-community pairs are the places where two stories meet in the same titles.</div>';
  panelEl.innerHTML = h;
  panelEl.querySelector('#open').addEventListener('click', () => openCommunity(id));
  panelEl.querySelector('#back').addEventListener('click', () => { selComm = -1; showPanel(); drawAll(); });
  panelEl.querySelectorAll('a.x[data-i]').forEach(a => a.addEventListener('click', () => { openCommunity(id); select(+a.dataset.i); }));
  panelEl.querySelectorAll('tr.link').forEach(tr => tr.addEventListener('click', () => { selComm = +tr.dataset.c; showPanel(); drawAll(); }));
}
function rankingPanel(p) {
  const measures = [['strength', u => p.str.get(u) || 0, v => v.toFixed(1)], ['degree', u => p.deg.get(u) || 0, v => v], ['betweenness (year)', u => p.net.nodes.get(u).b, v => v.toFixed(3)]];
  let h = `<h2>${openComm >= 0 ? commInfoOf(openComm).top.slice(0, 3).join(', ') : (NETNAME[p.key] || p.key)}${panels.length > 1 ? ' (' + p.label + ')' : ''}</h2><div class="sub">${openComm >= 0 ? '<a class="x" id="back">all communities</a> · ' : ''}Click a word in the map or a name below. Degree and strength are for the edges on screen (${month === 'all' || !p.net.monthly[month] ? 'the whole year' : monthName(month)}, lift ≥ ${minLift}x).</div>`;
  measures.forEach(([name, f, fmt]) => {
    const top = [...p.net.nodes.keys()].filter(u => p.visible(u) && p.inFocus(u)).sort((a, b) => f(b) - f(a)).slice(0, 12);
    h += `<h3>Top by ${name}</h3><table>` + top.map(u => `<tr class="link" data-i="${u}"><td>${dot(commOf(u).color)}${T[u]}</td><td class="num">${fmt(f(u))}</td></tr>`).join('') + '</table>';
  });
  h += "<div class='note'>Degree: how many partners. Strength: the sum of the partners' log2 lifts. Betweenness: how often the word lies on the shortest path between two others, a bridge between stories.</div>";
  panelEl.innerHTML = h;
  panelEl.querySelectorAll('tr.link').forEach(tr => tr.addEventListener('click', () => select(+tr.dataset.i)));
  const b = panelEl.querySelector('#back'); if (b) b.addEventListener('click', () => { openComm = -1; setMode('communities'); });
}
function partnersTable(p, u) {
  const nb = (p.adj.get(u) || []).slice().sort((a, b) => b.lift - a.lift);
  if (!p.has(u)) return `<div class="sub">${T[u]} has no edge in ${NETNAME[p.key] || p.key}.</div>`;
  const yr = month === 'all' || !p.net.monthly[month];
  const showAud = p.key === 'all' && yr && GT.left && p.net.edges.length && p.net.edges[0].length >= 9;
  let h = `<div class="sub">${nb.length} partners ${yr ? 'over the year' : 'in ' + monthName(month)} at lift ≥ ${minLift}x · degree ${p.deg.get(u) || 0} · strength ${(p.str.get(u) || 0).toFixed(1)} · betweenness ${p.net.nodes.get(u).b}</div>`;
  h += '<table><tr><th>partner</th><th class="num">lift</th>' + (yr ? '<th class="num">z</th>' : '') + '<th class="num">titles</th><th class="num">ch</th>' + (showAud ? '<th title="co-mentions per thousand titles of the left and of the right channels">L / R per 1k</th>' : '') + '</tr>';
  nb.forEach(a => { let aud = '';
    if (showAud) { const b = audienceBalance(a.e); aud = b !== null ? `<td><i class="dot" style="border-radius:2px;background:${balanceColor(b)}1)"></i>${(a.e[6] / GT.left * 1000).toFixed(1)} / ${(a.e[8] / GT.right * 1000).toFixed(1)}</td>` : '<td></td>'; }
    h += `<tr class="link" data-i="${a.j}"><td>${dot(commOf(a.j).color)}${T[a.j]}</td><td class="num">${a.lift.toFixed(1)}</td>` + (yr ? `<td class="num">${a.z}</td>` : '') + `<td class="num">${a.obs}</td><td class="num">${a.ch}</td>${aud}</tr>`; });
  return h + '</table>';
}
function wordPanel(u) {
  let h = `<h2>${T[u]}</h2><div class="sub">community <a class="x" id="cm">${dot(commOf(u).color)}${commOf(u).top.slice(0, 3).join(', ')}</a></div>`;
  if (Object.keys(NETS).length > 1) {
    h += '<h3>Across the networks</h3><table><tr><th>network</th><th class="num">titles</th><th class="num">degree</th><th class="num">strength</th><th>top partners</th></tr>';
    Object.keys(NETS).forEach(k => {
      const net = NETS[k]; if (!net.nodes.has(u)) { h += `<tr><td>${NETNAME[k] || k}</td><td colspan="4" style="color:var(--muted)">no edge</td></tr>`; return; }
      const nb = net.edges.filter(e => (e[0] === u || e[1] === u) && e[2] >= minLift).map(e => ({j: e[0] === u ? e[1] : e[0], lift: e[2]})).sort((a, b) => b.lift - a.lift);
      const st = nb.reduce((s, a) => s + Math.log2(a.lift), 0);
      h += `<tr><td>${NETNAME[k] || k}</td><td class="num">${net.nodes.get(u).n.toLocaleString()}</td><td class="num">${nb.length}</td><td class="num">${st.toFixed(1)}</td><td>${nb.slice(0, 5).map(a => `<a class="x" data-i="${a.j}">${T[a.j]}</a>`).join(', ')}</td></tr>`;
    });
    h += '</table>';
  }
  panels.forEach(p => { h += `<h3>${panels.length > 1 ? p.label + ': ' : ''}${NETNAME[p.key] || p.key}</h3>` + partnersTable(p, u); });
  if (GT.left && panels.some(p => p.key === 'all')) h += '<div class="note">Audience: blue when the left channels make the pair more often per title, orange when the right do, gray when both do alike. Neutral channels count in titles and lift but not in the balance.</div>';
  panelEl.innerHTML = h;
  panelEl.querySelectorAll('tr.link, a.x[data-i]').forEach(el => el.addEventListener('click', () => select(+el.dataset.i)));
  panelEl.querySelector('#cm').addEventListener('click', () => { setMode('communities'); selComm = REF.comm.get(u); showPanel(); drawAll(); });
}
function timelineFor(u) {
  const p = panels.find(x => x.has(u)) || panels[0]; const st = p.net.nodes.get(u) || {mt: MONTHS.map(() => 0), mc: MONTHS.map(() => 0)}; const maxT = Math.max(1, ...st.mt);
  let h = '<div class="tl">';
  MONTHS.forEach((m, k) => {
    const partners = (NETS.all.monthly[m] || []).filter(e => e[0] === u || e[1] === u).map(e => ({j: e[0] === u ? e[1] : e[0], lift: e[2]})).sort((a, b) => b.lift - a.lift).slice(0, 6);
    h += `<div class="m"><h4>${monthShort(m)}</h4><div class="bar" style="width:${Math.round(100 * st.mt[k] / maxT)}%"></div><div class="cnt">${st.mt[k].toLocaleString()} titles · ${st.mc[k]} ch</div>` + partners.map(q => `<div class="p" data-i="${q.j}" title="${T[q.j]}, ${q.lift.toFixed(1)}x">${T[q.j]} <span style="color:var(--muted)">${q.lift.toFixed(0)}x</span></div>`).join('') + '</div>';
  });
  h += '</div>';
  if (p.key !== 'all') h += `<div class="note" style="padding:0 12px 8px">Bars: the word's titles among ${NETNAME[p.key] || p.key}; partners by month from the all-channel network.</div>`;
  timeline.innerHTML = '<span class="close" title="hide the months">hide ×</span>' + h; timeline.classList.add('open');
  timeline.querySelectorAll('.p').forEach(el => el.addEventListener('click', () => select(+el.dataset.i)));
  timeline.querySelector('.close').addEventListener('click', () => timeline.classList.remove('open'));
}
function showPanel() {
  const p = active || panels[0];
  if (mode === 'communities') { if (selComm >= 0) communityDetail(selComm); else communityCards(); return; }
  if (selected >= 0) wordPanel(selected); else rankingPanel(p);
}
// ---------- actions ----------
function setMode(m) {
  mode = m; document.getElementById('tabC').classList.toggle('on', m === 'communities'); document.getElementById('tabW').classList.toggle('on', m === 'words');
  if (m === 'communities') { selected = -1; timeline.classList.remove('open'); timeline.innerHTML = ''; }
  buildLegend(); showPanel(); drawAll();
}
function openCommunity(id) { openComm = id; selComm = -1; selected = -1; setMode('words'); }
function fitVisible() {
  const p = active || panels[0]; const r = p.canvas.getBoundingClientRect(); const vis = [...p.net.nodes.keys()].filter(u => p.visible(u) && p.inFocus(u)); if (!vis.length) return;
  const xs = vis.map(u => X[u]), ys = vis.map(u => Y[u]); const w = Math.max(...xs) - Math.min(...xs) || 1, h = Math.max(...ys) - Math.min(...ys) || 1;
  view.k = Math.min(r.width / w, r.height / h) * 0.8; view.tx = r.width / 2 - (Math.min(...xs) + w / 2) * view.k; view.ty = r.height / 2 - (Math.min(...ys) + h / 2) * view.k; drawAll();
}
function select(u, center) {
  if (mode !== 'words') { openComm = -1; setMode('words'); }
  if (u >= 0) { hidden.delete(REF.comm.get(u)); if (openComm >= 0 && REF.comm.get(u) !== openComm) openComm = -1; }
  selected = u;
  if (u >= 0) {
    const p = active || panels[0]; const r = p.canvas.getBoundingClientRect();
    const off = p.sx(u) < 20 || p.sy(u) < 20 || p.sx(u) > r.width - 20 || p.sy(u) > r.height - 20;
    if (center || off) { view.tx = r.width / 2 - X[u] * view.k; view.ty = r.height / 2 - Y[u] * view.k; }
    timelineFor(u);
  } else { timeline.classList.remove('open'); timeline.innerHTML = ''; }
  buildLegend(); showPanel(); drawAll();
}
window.addEventListener('keydown', e => { if (e.key === 'Escape') { if (mode === 'words') select(-1); else { selComm = -1; showPanel(); drawAll(); } } });
document.getElementById('tabC').addEventListener('click', () => { openComm = -1; setMode('communities'); });
document.getElementById('tabW').addEventListener('click', () => { openComm = -1; setMode('words'); });
document.getElementById('compare').addEventListener('click', () => setCompare(!compare));
if (!NETS.left || !NETS.right) document.getElementById('compare').style.display = 'none';
const dl = document.getElementById('terms'); [...NETS.all.nodes.entries()].sort((a, b) => b[1].n - a[1].n).forEach(([u]) => { const o = document.createElement('option'); o.value = T[u]; dl.appendChild(o); });
document.getElementById('q').addEventListener('change', e => { const u = byName.get(e.target.value.trim().toLowerCase()); if (u !== undefined) select(u, true); });
const ms = document.getElementById('month'); MONTHS.forEach(m => { const o = document.createElement('option'); o.value = m; o.textContent = monthName(m) + ' 2026 (all channels)'; ms.appendChild(o); });
ms.addEventListener('change', e => { month = e.target.value; panels.forEach(p => { p.buildEdges(); p.layoutCommunities(); }); showPanel(); drawAll(); });
document.getElementById('lift').addEventListener('input', e => { minLift = Math.pow(2, +e.target.value); document.getElementById('liftv').textContent = minLift.toFixed(minLift < 4 ? 1 : 0) + 'x'; panels.forEach(p => { p.buildEdges(); p.layoutCommunities(); }); showPanel(); drawAll(); });
document.getElementById('sizeby').addEventListener('change', e => { sizeBy = e.target.value; drawAll(); });
document.getElementById('colorby').addEventListener('change', e => { colorBy = e.target.value; buildLegend(); drawAll(); });
document.getElementById('edgecolor').addEventListener('change', e => { edgeColor = e.target.value; buildLegend(); drawAll(); });
if (!GT.left) document.getElementById('edgecolor').parentElement.style.display = 'none';
document.getElementById('res').addEventListener('change', e => { resolution = +e.target.value; document.getElementById('resv').textContent = resolution.toFixed(1); runCommunities(); buildLegend(); showPanel(); drawAll(); });
document.getElementById('res').addEventListener('input', e => { document.getElementById('resv').textContent = (+e.target.value).toFixed(1); });
document.getElementById('reshuffle').addEventListener('click', () => { seed++; runCommunities(); buildLegend(); showPanel(); drawAll(); });
document.getElementById('fit').addEventListener('click', fitVisible);
document.getElementById('labels').addEventListener('change', e => { showLabels = e.target.checked; drawAll(); });
window.addEventListener('resize', resizeAll);
runCommunities(); buildLegend(); showPanel(); resizeAll();
</script>
</body>
</html>
"""


def main(argv=None) -> int:
    import argparse
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--no-leaning", action="store_true", help="leave out everything derived from the leaning labels (audience networks, audience colors): the build for the website")
    ap.add_argument("--out", default=None, help="where to write (default: reports/word_network.html, or word_network_site.html with --no-leaning)")
    a = ap.parse_args(argv)
    out = Path(a.out) if a.out else (REPORTS_DIR / "word_network_site.html" if a.no_leaning else OUT)
    data = build_data(with_leaning=not a.no_leaning)
    html = TEMPLATE.replace("__DATA__", json.dumps(data, separators=(",", ":")).replace("</", "<\\/")).replace("__NODES__", f"{data['meta']['nodes']:,}").replace("__EDGES__", f"{data['meta']['edges']:,}")
    out.write_text(html, encoding="utf-8")
    print(f"{out} ({out.stat().st_size / 1e6:.1f} MB): {data['meta']['nodes']:,} nodes, {data['meta']['edges']:,} edges, {len(data['networks'])} networks")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
