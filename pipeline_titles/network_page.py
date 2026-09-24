"""The word-association network as a page to explore (pipeline_titles/reports/word_network.html).

Nodes are the vocabulary terms of the associations stage; an edge is a pair that co-mentions
beyond chance within creator-weeks (Cochran-Mantel-Haenszel q < 0.01), replicated in both channel
halves, with lift >= 2 from >= 5 channels (assoc_edges.csv, assoc_nodes.csv); the month view uses
each month's own edges (assoc_monthly_neighbors.csv.gz); the timeline uses each node's titles and
channels per month (assoc_node_months.csv). Positions come from ForceAtlas2 on the edge weights
(log2 lift), seed fixed.

The page has two views. Communities: one node per community, sized by its words, joined by the
pairs that cross between communities; a card per community lists its words and months. Words:
every node and edge; a click gives a word's partners and a timeline of its months. Degree and
strength are recomputed from the edges on screen (month, lift threshold); betweenness is the
year's, precomputed; community detection is Louvain run in the browser, with a resolution slider
and a reshuffle, so the stability of the groups is something to see rather than take on trust.
The page is self-contained: no network access, no libraries.

    python -m pipeline_titles.network_page
"""

from __future__ import annotations

import json

import networkx as nx
import numpy as np
import pandas as pd

from pipeline_titles.common import ANALYSIS_DIR as A, REPORTS_DIR, SEED
from pipeline_titles.figures import CAT

OUT = REPORTS_DIR / "word_network.html"


def layout_of(nodes: pd.DataFrame, edges: pd.DataFrame) -> np.ndarray:
    G = nx.Graph()
    for r in nodes.itertuples():
        G.add_node(r.term)
    for r in edges.itertuples():
        G.add_edge(r.term_a, r.term_b, weight=float(r.weight))
    pos = nx.forceatlas2_layout(G, max_iter=400, weight="weight", seed=SEED, scaling_ratio=2.0, gravity=1.0)
    xy = np.array([pos[t] for t in nodes["term"]])
    return (xy - xy.mean(axis=0)) / xy.std(axis=0).max()


def network_of(suffix: str, months: list[str], with_monthly: bool) -> dict:
    nodes = pd.read_csv(A / f"assoc_nodes{suffix}.csv")
    edges = pd.read_csv(A / f"assoc_edges{suffix}.csv")
    nm = pd.read_csv(A / f"assoc_node_months{suffix}.csv").set_index("term")
    xy = layout_of(nodes, edges)
    idx = {t: i for i, t in enumerate(nodes["term"])}
    data_nodes = [{"t": r.term, "x": round(float(xy[i, 0]), 4), "y": round(float(xy[i, 1]), 4), "c": int(r.community), "n": int(r.n_titles), "b": round(float(r.betweenness), 5),
                   "mt": [int(nm.loc[r.term, f"titles_{m}"]) for m in months], "mc": [int(nm.loc[r.term, f"channels_{m}"]) for m in months]} for i, r in enumerate(nodes.itertuples())]
    has_co = all(c in edges.columns for c in ("co_left", "co_neutral", "co_right"))
    data_edges = [[idx[r.term_a], idx[r.term_b], round(float(r.lift_strat), 2), round(float(r.z_cmh), 1), int(r.channels), int(r.observed)] + ([int(r.co_left), int(r.co_neutral), int(r.co_right)] if has_co else [])
                  for r in edges.itertuples()]
    out = {"nodes": data_nodes, "edges": data_edges, "monthly": {}}
    if with_monthly:
        nb = pd.read_csv(A / "assoc_monthly_neighbors.csv.gz")
        nb = nb[nb["term"].isin(idx) & nb["neighbor"].isin(idx)]
        for m, g in nb.groupby("month"):
            seen = {}
            for r in g.itertuples():
                key = (min(idx[r.term], idx[r.neighbor]), max(idx[r.term], idx[r.neighbor]))
                if key not in seen:
                    seen[key] = [key[0], key[1], round(float(r.lift), 2), int(r.channels), int(r.observed)]
            out["monthly"][m] = list(seen.values())
    return out


def build_data() -> dict:
    nm = pd.read_csv(A / "assoc_node_months.csv")
    months = sorted(c[len("titles_"):] for c in nm.columns if c.startswith("titles_"))
    aud = json.loads((A / "assoc_audience.json").read_text()) if (A / "assoc_audience.json").exists() else {"titles": {}}
    networks = {"all": network_of("", months, True)}
    for g in ("left", "neutral", "right"):
        if (A / f"assoc_edges_{g}.csv").exists():
            networks[g] = network_of(f"_{g}", months, False)
            print(f"{g}: {len(networks[g]['nodes'])} nodes, {len(networks[g]['edges'])} edges", flush=True)
    return {"networks": networks, "palette": CAT[:7], "group_titles": aud["titles"],
            "meta": {"nodes": len(networks["all"]["nodes"]), "edges": len(networks["all"]["edges"]), "months": months}}


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
.tabs { display:inline-flex; gap:2px; vertical-align:middle; }
.tabs button { font:inherit; font-size:13px; padding:3px 10px; border:1px solid var(--grid); background:var(--panel); color:var(--ink2); cursor:pointer; border-radius:4px; }
.tabs button.on { background:var(--accent); color:#fff; border-color:var(--accent); }
.controls { display:flex; flex-wrap:wrap; gap:8px 16px; align-items:center; font-size:13px; }
.controls label { display:flex; align-items:center; gap:6px; color:var(--ink2); white-space:nowrap; }
input[type=search] { padding:4px 8px; border:1px solid var(--grid); border-radius:4px; font:inherit; width:180px; }
select, button.small { font:inherit; font-size:13px; padding:3px 6px; }
button.small { border:1px solid var(--grid); background:var(--panel); border-radius:4px; cursor:pointer; }
.legend { display:flex; flex-wrap:wrap; gap:6px 12px; }
.chip { display:inline-flex; align-items:center; gap:5px; cursor:pointer; user-select:none; color:var(--ink2); }
.chip.off { opacity:.35; }
.chip i { width:11px; height:11px; border-radius:50%; display:inline-block; }
main { display:flex; height:calc(100% - 128px); }
.stage { flex:1; display:flex; flex-direction:column; min-width:0; }
canvas { flex:1; display:block; cursor:grab; min-height:0; }
#timeline { height:0; overflow:hidden; border-top:1px solid var(--grid); background:var(--panel); transition:height .15s; }
#timeline.open { height:190px; overflow:auto; }
.tl { display:grid; grid-template-columns:repeat(9, 1fr); gap:6px; padding:8px 12px; font-size:12px; }
.tl .m { border-left:1px solid var(--grid); padding-left:6px; min-width:0; }
.tl .m h4 { margin:0 0 2px; font-size:12px; color:var(--ink); font-weight:600; }
.tl .bar { height:6px; background:var(--accent); border-radius:3px; margin:2px 0 4px; }
.tl .cnt { color:var(--muted); font-size:11px; margin-bottom:3px; }
.tl .p { color:var(--ink2); white-space:nowrap; overflow:hidden; text-overflow:ellipsis; cursor:pointer; }
.tl .p:hover { color:var(--accent); }
aside { width:360px; border-left:1px solid var(--grid); background:var(--panel); padding:12px 14px; overflow:auto; font-size:13px; }
aside h2 { font-size:15px; margin:0 0 4px; }
aside h3 { font-size:13px; margin:12px 0 4px; color:var(--ink2); }
aside .sub { color:var(--muted); margin-bottom:8px; }
table { border-collapse:collapse; width:100%; }
th, td { text-align:left; padding:3px 4px; border-bottom:1px solid var(--grid); font-variant-numeric:tabular-nums; }
th { color:var(--muted); font-weight:600; font-size:12px; }
td.num, th.num { text-align:right; }
tr.link { cursor:pointer; }
tr.link:hover { background:#ebeae6; }
.card { border:1px solid var(--grid); border-radius:6px; padding:8px 10px; margin-bottom:8px; background:var(--surface); cursor:pointer; }
.card:hover { border-color:var(--accent); }
.card.on { border-color:var(--ink); }
.card b { display:flex; align-items:center; gap:6px; }
.card i { width:10px; height:10px; border-radius:50%; display:inline-block; }
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
  <p id="intro">__NODES__ words, __EDGES__ edges. An edge joins two words that share titles beyond chance within the same channel and week, in both random halves of the channels (lift at least 2, from at least 5 channels). Start from the communities; open one to see its words.</p>
  <div class="controls">
    <label>Network <select id="net"><option value="all">all channels</option><option value="left">left channels</option><option value="neutral">neutral channels</option><option value="right">right channels</option></select></label>
    <label>Find <input type="search" id="q" list="terms" placeholder="a word"><datalist id="terms"></datalist></label>
    <label>Edges of <select id="month"><option value="all">the whole year</option></select></label>
    <label>Edge color <select id="edgecolor"><option value="strength">strength</option><option value="audience">audience</option></select></label>
    <button class="small" id="fit" title="fit the view to what is shown">fit</button>
    <label>Lift ≥ <input type="range" id="lift" min="1" max="6" step="0.25" value="1" style="width:90px"> <span id="liftv">2x</span></label>
    <label>Size by <select id="sizeby"><option value="strength">strength</option><option value="degree">degree</option><option value="betweenness">betweenness</option><option value="titles">titles</option></select></label>
    <label>Color by <select id="colorby"><option value="community">community</option><option value="betweenness">betweenness</option><option value="strength">strength</option></select></label>
    <label>Communities: resolution <input type="range" id="res" min="0.4" max="2.0" step="0.1" value="1.0" style="width:90px"> <span id="resv">1.0</span></label>
    <button class="small" id="reshuffle" title="run Louvain again with a new random order">reshuffle</button>
    <span id="modq" style="color:var(--muted)"></span>
    <label><input type="checkbox" id="labels" checked> labels</label>
  </div>
  <div class="legend" id="legend" style="margin-top:6px"></div>
</header>
<main>
  <div class="stage"><canvas id="c"></canvas><div id="timeline"></div></div>
  <aside id="panel"></aside>
</main>
<div class="tip" id="tip"></div>
<script id="data" type="application/json">__DATA__</script>
<script>
// ---------- pure functions: Louvain, modularity, measures ----------
function mulberry32(a) { return function() { a |= 0; a = a + 0x6D2B79F5 | 0; let t = Math.imul(a ^ a >>> 15, 1 | a); t = t + Math.imul(t ^ t >>> 7, 61 | t) ^ t; return ((t ^ t >>> 14) >>> 0) / 4294967296; }; }
function louvain(n, edges, resolution, seed) {
  // edges: [[i, j, w], ...]. Returns {comm: Int32Array (0..k-1), modularity}
  const rnd = mulberry32(seed);
  let nodes = n, E = edges.map(e => [e[0], e[1], e[2]]);
  let membership = Array.from({length: n}, (_, i) => i);   // original node -> current super-node
  for (let level = 0; level < 20; level++) {
    const adj = Array.from({length: nodes}, () => new Map());
    const k = new Float64Array(nodes); let m2 = 0;
    E.forEach(([i, j, w]) => { if (i === j) { k[i] += 2 * w; m2 += 2 * w; adj[i].set(i, (adj[i].get(i) || 0) + w); return; }
      adj[i].set(j, (adj[i].get(j) || 0) + w); adj[j].set(i, (adj[j].get(i) || 0) + w); k[i] += w; k[j] += w; m2 += 2 * w; });
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
    // renumber
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
  const tot = new Map(); for (let i = 0; i < n; i++) tot.set(comm[i], (tot.get(comm[i]) || 0) + k[i]);
  let inside = 0; edges.forEach(([i, j, w]) => { if (comm[i] === comm[j]) inside += 2 * w; });
  let s = 0; tot.forEach(t => s += t * t); return inside / m2 - s / (m2 * m2);
}
// ---------- data and state ----------
const D = JSON.parse(document.getElementById('data').textContent);
const MONTHS = D.meta.months, PAL = D.palette, GT = D.group_titles;
let NET = 'all', N = D.networks.all.nodes, E = D.networks.all.edges, MONTHLY = D.networks.all.monthly;
let byName = new Map(N.map((n, i) => [n.t, i]));
let edgeColor = 'strength';
const NETNAME = {all: 'all channels', left: 'left channels', neutral: 'neutral channels', right: 'right channels'};
function audienceBalance(e) {
  // rates per thousand titles of the left and the right channels; -1 = only the left makes the pair, +1 = only the right
  if (e.length < 9 || !GT.left) return null;
  const l = e[6] / GT.left * 1000, r = e[8] / GT.right * 1000; if (l + r === 0) return null; return (r - l) / (r + l);
}
function balanceColor(b) { const t = Math.abs(b); const base = b < 0 ? [42, 120, 214] : [235, 104, 52]; const g = [150, 149, 143]; return `rgba(${base.map((v, k) => Math.round(g[k] + (v - g[k]) * t)).join(',')},`; }
const canvas = document.getElementById('c'), ctx = canvas.getContext('2d');
const tip = document.getElementById('tip'), panel = document.getElementById('panel'), timeline = document.getElementById('timeline');
let view = {k: 1, tx: 0, ty: 0}, dragging = false, moved = false, last = null;
let mode = 'communities', selected = -1, selComm = -1, hover = -1, month = 'all', minLift = 2, showLabels = true, sizeBy = 'strength', colorBy = 'community';
let resolution = 1.0, seed = 1, comm, commInfo = [], hidden = new Set(), openComm = -1;
let edgesNow = E, adj = new Map(), deg = new Float64Array(N.length), str = new Float64Array(N.length);
function setNetwork(key) {
  NET = key; N = D.networks[key].nodes; E = D.networks[key].edges; MONTHLY = D.networks[key].monthly || {};
  byName = new Map(N.map((n, i) => [n.t, i])); deg = new Float64Array(N.length); str = new Float64Array(N.length);
  selected = -1; selComm = -1; openComm = -1; hover = -1; month = 'all'; document.getElementById('month').value = 'all';
  document.getElementById('month').disabled = key !== 'all'; document.getElementById('edgecolor').disabled = key !== 'all'; if (key !== 'all') { edgeColor = 'strength'; document.getElementById('edgecolor').value = 'strength'; }
  document.getElementById('intro').textContent = `${N.length.toLocaleString()} words, ${E.length.toLocaleString()} edges among the ${NETNAME[key]}` + (key === 'all' ? '. An edge joins two words that share titles beyond chance within the same channel and week, in both random halves of the channels (lift at least 2, from at least 5 channels). Start from the communities; open one to see its words.' : `: the same test run on the ${GT[key].toLocaleString()} titles of those channels alone, with its own channel halves, communities and layout. Fewer titles mean fewer pairs clear the gates, so this network is sparser than the whole.`);
  const dl = document.getElementById('terms'); dl.innerHTML = ''; N.slice().sort((a, b) => b.n - a.n).forEach(n => { const o = document.createElement('option'); o.value = n.t; dl.appendChild(o); });
  timeline.classList.remove('open'); timeline.innerHTML = '';
  buildEdges(); runCommunities(); view.init = false; resize(); showPanel();
}
let cNodes = [], cEdges = [];
const monthName = m => new Date(m + '-15').toLocaleString('en-US', {month: 'long'});
const monthShort = m => new Date(m + '-15').toLocaleString('en-US', {month: 'short'});

function buildEdges() {
  edgesNow = month === 'all' ? E : (MONTHLY[month] || []).map(e => [e[0], e[1], e[2], NaN, e[3], e[4]]);
  adj = new Map(); deg.fill(0); str.fill(0);
  edgesNow.forEach(e => {
    if (e[2] < minLift) return;
    const w = Math.log2(e[2]);
    if (!adj.has(e[0])) adj.set(e[0], []); if (!adj.has(e[1])) adj.set(e[1], []);
    adj.get(e[0]).push({j: e[1], lift: e[2], z: e[3], ch: e[4], obs: e[5], e}); adj.get(e[1]).push({j: e[0], lift: e[2], z: e[3], ch: e[4], obs: e[5], e});
    deg[e[0]]++; deg[e[1]]++; str[e[0]] += w; str[e[1]] += w;
  });
}
function runCommunities() {
  const r = louvain(N.length, E.map(e => [e[0], e[1], Math.log2(e[2])]), resolution, seed);
  comm = r.comm;
  const groups = new Map(); comm.forEach((c, i) => { if (!groups.has(c)) groups.set(c, []); groups.get(c).push(i); });
  commInfo = [...groups.entries()].map(([id, members]) => {
    const strength = i => E.reduce ? 0 : 0;   // placeholder (strength computed below from year edges)
    return {id, members};
  });
  // year strength per node for ranking words inside communities
  const ys = new Float64Array(N.length); E.forEach(e => { const w = Math.log2(e[2]); ys[e[0]] += w; ys[e[1]] += w; });
  commInfo.forEach(c => {
    c.members.sort((a, b) => ys[b] - ys[a]); c.size = c.members.length;
    c.top = c.members.slice(0, 10).map(i => N[i].t);
    c.x = c.members.reduce((s, i) => s + N[i].x, 0) / c.size; c.y = c.members.reduce((s, i) => s + N[i].y, 0) / c.size;
    const mt = MONTHS.map((_, k) => c.members.reduce((s, i) => s + N[i].mt[k], 0)); c.months = mt;
    c.titles = c.members.reduce((s, i) => s + N[i].n, 0);
  });
  commInfo.sort((a, b) => b.size - a.size);
  commInfo.forEach((c, rank) => { c.rank = rank; c.color = rank < PAL.length ? PAL[rank] : '#b3b2ad'; c.label = c.top.slice(0, 3).join(', '); });
  document.getElementById('modq').textContent = `${commInfo.length} communities, modularity ${r.modularity.toFixed(3)}`;
  hidden = new Set(); selComm = -1; if (openComm >= 0) openComm = -1;
  layoutCommunities(); buildLegend();
}
const commOf = i => commInfo.find(c => c.id === comm[i]);
function layoutCommunities() {
  // community nodes at their members' centroids, pushed apart so the discs do not overlap
  cNodes = commInfo.map(c => ({c, x: c.x, y: c.y, r: 0.03 + 0.11 * Math.sqrt(c.size / commInfo[0].size)}));
  for (let it = 0; it < 200; it++) {
    for (let a = 0; a < cNodes.length; a++) for (let b = a + 1; b < cNodes.length; b++) {
      const A = cNodes[a], B = cNodes[b]; const dx = B.x - A.x, dy = B.y - A.y; const d = Math.hypot(dx, dy) || 1e-6, min = A.r + B.r + 0.02;
      if (d < min) { const push = (min - d) / 2; A.x -= dx / d * push; A.y -= dy / d * push; B.x += dx / d * push; B.y += dy / d * push; }
    }
  }
  const agg = new Map();
  edgesNow.forEach(e => { if (e[2] < minLift) return; const a = comm[e[0]], b = comm[e[1]]; if (a === b) return; const key = a < b ? a + ':' + b : b + ':' + a;
    const v = agg.get(key) || {a: Math.min(a, b), b: Math.max(a, b), n: 0, w: 0, top: []}; v.n++; v.w += Math.log2(e[2]); v.top.push(e); agg.set(key, v); });
  cEdges = [...agg.values()]; cEdges.forEach(v => v.top.sort((p, q) => q[2] - p[2]));
}
// ---------- drawing ----------
function resize() {
  const r = canvas.getBoundingClientRect();
  canvas.width = r.width * devicePixelRatio; canvas.height = r.height * devicePixelRatio;
  ctx.setTransform(devicePixelRatio, 0, 0, devicePixelRatio, 0, 0);
  if (!view.init) { view.k = Math.min(r.width, r.height) * 0.42; view.tx = r.width / 2; view.ty = r.height / 2; view.init = true; }
  draw();
}
const sx = p => p.x * view.k + view.tx, sy = p => p.y * view.k + view.ty;
let sizeMax = 1;
function measure(i) { return sizeBy === 'strength' ? str[i] : sizeBy === 'degree' ? deg[i] : sizeBy === 'betweenness' ? N[i].b : N[i].n; }
function radius(i) { return 2 + 9 * Math.sqrt(Math.max(0, measure(i)) / sizeMax); }
const SEQ = ['#f4f8fd', '#cde2fb', '#6da7ec', '#256abf', '#0d366b'];
function ramp(v) { const t = Math.max(0, Math.min(1, v)); const p = t * (SEQ.length - 1), i = Math.floor(p), f = p - i; if (i >= SEQ.length - 1) return SEQ[SEQ.length - 1];
  const a = SEQ[i].match(/\w\w/g).map(h => parseInt(h, 16)), b = SEQ[i + 1].match(/\w\w/g).map(h => parseInt(h, 16)); return `rgb(${a.map((x, k) => Math.round(x + (b[k] - x) * f)).join(',')})`; }
let colorMax = 1;
function colorOfNode(i) {
  if (colorBy === 'community') return commOf(i).color;
  const v = colorBy === 'betweenness' ? N[i].b : str[i];
  return ramp(Math.sqrt(v / colorMax));
}
function visibleNode(i) { return !hidden.has(comm[i]); }
function inFocusComm(i) { return openComm < 0 || comm[i] === openComm; }
function draw() {
  const r = canvas.getBoundingClientRect();
  ctx.clearRect(0, 0, r.width, r.height);
  if (mode === 'communities') return drawCommunities(r);
  sizeMax = Math.max(1e-9, ...N.map((_, i) => visibleNode(i) && inFocusComm(i) ? measure(i) : 0));
  colorMax = Math.max(1e-9, ...N.map((_, i) => colorBy === 'betweenness' ? N[i].b : str[i]));
  const focus = selected >= 0 ? new Set([selected, ...(adj.get(selected) || []).map(a => a.j)]) : null;
  ctx.lineCap = 'round';
  edgesNow.forEach(e => {
    if (e[2] < minLift || !visibleNode(e[0]) || !visibleNode(e[1])) return;
    if (!inFocusComm(e[0]) || !inFocusComm(e[1])) return;
    const inFocus = focus && (e[0] === selected || e[1] === selected);
    if (focus && !inFocus) return;
    const w = Math.log2(e[2]);
    const bal = edgeColor === 'audience' ? audienceBalance(e) : null;
    if (bal !== null) ctx.strokeStyle = balanceColor(bal) + (inFocus ? '0.9)' : `${Math.min(0.75, 0.25 + 0.25 * Math.abs(bal) + 0.05 * w)})`);
    else ctx.strokeStyle = inFocus ? 'rgba(42,120,214,0.75)' : `rgba(82,81,78,${Math.min(0.45, 0.05 + 0.05 * w)})`;
    ctx.lineWidth = Math.max(0.4, Math.min(3, 0.3 + 0.35 * w)) * (inFocus ? 1.4 : 1);
    ctx.beginPath(); ctx.moveTo(sx(N[e[0]]), sy(N[e[0]])); ctx.lineTo(sx(N[e[1]]), sy(N[e[1]])); ctx.stroke();
  });
  const order = N.map((n, i) => i).filter(visibleNode).sort((a, b) => measure(a) - measure(b));
  order.forEach(i => {
    const n = N[i], dim = (focus && !focus.has(i)) || !inFocusComm(i);
    ctx.globalAlpha = dim ? 0.12 : 1;
    ctx.beginPath(); ctx.arc(sx(n), sy(n), radius(i), 0, Math.PI * 2);
    ctx.fillStyle = colorOfNode(i); ctx.fill();
    ctx.lineWidth = i === selected || i === hover ? 2 : 1; ctx.strokeStyle = i === selected ? '#0b0b0b' : '#fcfcfb'; ctx.stroke();
    ctx.globalAlpha = 1;
  });
  if (showLabels) {
    ctx.textAlign = 'center'; ctx.textBaseline = 'bottom';
    const budget = Math.round(40 * Math.max(1, view.k / (Math.min(r.width, r.height) * 0.42)) ** 1.6);
    const labeled = new Set(order.slice(-budget)); if (focus) focus.forEach(i => labeled.add(i));
    const placed = [];
    [...labeled].sort((a, b) => measure(b) - measure(a)).forEach(i => {
      const n = N[i]; if (!visibleNode(i) || !inFocusComm(i) || (focus && !focus.has(i))) return;
      ctx.font = (i === selected ? 'bold 12px' : '11px') + ' -apple-system, "Segoe UI", Helvetica, Arial, sans-serif';
      const x = sx(n), y = sy(n) - radius(i) - 2, w = ctx.measureText(n.t).width;
      if (x < -20 || y < -20 || x > r.width + 20 || y > r.height + 20) return;
      if (placed.some(p => Math.abs(p.x - x) < (p.w + w) / 2 + 4 && Math.abs(p.y - y) < 13)) return;
      placed.push({x, y, w});
      ctx.strokeStyle = 'rgba(252,252,251,0.9)'; ctx.lineWidth = 3; ctx.strokeText(n.t, x, y);
      ctx.fillStyle = i === selected ? '#0b0b0b' : '#52514e'; ctx.fillText(n.t, x, y);
    });
  }
}
function drawCommunities(r) {
  const maxN = Math.max(1, ...cEdges.map(v => v.n));
  ctx.lineCap = 'round';
  cEdges.forEach(v => {
    const A = cNodes.find(c => c.c.id === v.a), B = cNodes.find(c => c.c.id === v.b); if (!A || !B) return;
    if (hidden.has(v.a) || hidden.has(v.b)) return;
    const inFocus = selComm >= 0 && (v.a === selComm || v.b === selComm);
    if (selComm >= 0 && !inFocus) return;
    ctx.strokeStyle = inFocus ? 'rgba(42,120,214,0.7)' : 'rgba(82,81,78,0.35)';
    ctx.lineWidth = 0.6 + 9 * Math.sqrt(v.n / maxN);
    ctx.beginPath(); ctx.moveTo(sx(A), sy(A)); ctx.lineTo(sx(B), sy(B)); ctx.stroke();
  });
  cNodes.forEach(cn => {
    const c = cn.c; if (hidden.has(c.id)) return;
    const dim = selComm >= 0 && c.id !== selComm && !cEdges.some(v => (v.a === selComm && v.b === c.id) || (v.b === selComm && v.a === c.id));
    ctx.globalAlpha = dim ? 0.18 : 1;
    ctx.beginPath(); ctx.arc(sx(cn), sy(cn), cn.r * view.k, 0, Math.PI * 2);
    ctx.fillStyle = c.color; ctx.fill(); ctx.lineWidth = c.id === selComm ? 2.5 : 1.5; ctx.strokeStyle = c.id === selComm ? '#0b0b0b' : '#fcfcfb'; ctx.stroke();
    if (showLabels && (cn.r * view.k > 14 || c.id === selComm)) {
      ctx.font = 'bold 12px -apple-system, "Segoe UI", Helvetica, Arial, sans-serif'; ctx.textAlign = 'center'; ctx.textBaseline = 'middle';
      ctx.fillStyle = c.rank < PAL.length ? '#fff' : '#0b0b0b';
      const lines = c.top.slice(0, cn.r * view.k > 40 ? 3 : 1);
      lines.forEach((t, k) => ctx.fillText(t, sx(cn), sy(cn) + (k - (lines.length - 1) / 2) * 14));
      ctx.font = '11px -apple-system, "Segoe UI", Helvetica, Arial, sans-serif'; ctx.fillStyle = '#52514e'; ctx.textBaseline = 'top';
      ctx.fillText(`${c.size} words`, sx(cn), sy(cn) + cn.r * view.k + 3);
    }
    ctx.globalAlpha = 1;
  });
}
// ---------- hit testing ----------
function nodeAt(px, py) {
  if (mode === 'communities') { let best = -1; cNodes.forEach(cn => { if (hidden.has(cn.c.id)) return; if (Math.hypot(sx(cn) - px, sy(cn) - py) <= cn.r * view.k + 3) best = cn.c.id; }); return best; }
  let best = -1, bd = 1e9;
  N.forEach((n, i) => { if (!visibleNode(i) || !inFocusComm(i)) return; const d = Math.hypot(sx(n) - px, sy(n) - py); if (d < Math.max(radius(i) + 3, 8) && d < bd) { bd = d; best = i; } });
  return best;
}
// ---------- panels ----------
function buildLegend() {
  const legend = document.getElementById('legend'); legend.innerHTML = '';
  commInfo.slice(0, PAL.length).forEach(c => { const s = document.createElement('span'); s.className = 'chip' + (openComm >= 0 && openComm !== c.id ? ' off' : ''); s.title = mode === 'words' ? 'show only this community (click again for all)' : 'select this community';
    s.innerHTML = `<i style="background:${c.color}"></i>${c.label} (${c.size})`;
    s.addEventListener('click', () => { if (mode === 'communities') { selectCommunity(c.id); return; } openComm = openComm === c.id ? -1 : c.id; selected = -1; timeline.classList.remove('open'); timeline.innerHTML = ''; buildLegend(); showPanel(); setTimeout(resize, 160); }); legend.appendChild(s); });
  const others = document.createElement('span'); others.className = 'chip'; others.innerHTML = `<i style="background:#b3b2ad"></i>${Math.max(0, commInfo.length - PAL.length)} smaller communities`; legend.appendChild(others);
  if (colorBy !== 'community') { const s = document.createElement('span'); s.className = 'chip'; s.innerHTML = `<i style="background:linear-gradient(90deg,#cde2fb,#0d366b);border-radius:2px;width:40px"></i>${colorBy}, light to dark`; legend.appendChild(s); }
  if (edgeColor === 'audience' && NET === 'all') { const s = document.createElement('span'); s.className = 'chip'; s.innerHTML = `<i style="background:linear-gradient(90deg,#2a78d6,#96958f,#eb6834);border-radius:2px;width:60px"></i>edges: left channels make the pair · both · right channels`; legend.appendChild(s); }
}
function communityCards() {
  let h = `<h2>${commInfo.length} communities</h2><div class="sub">Louvain on the year's edges at resolution ${resolution.toFixed(1)}. Click a card or a disc; open it to see its words.</div>`;
  commInfo.forEach(c => {
    const active = c.months.map((v, k) => v > 0 ? monthShort(MONTHS[k]) : null).filter(Boolean);
    const peak = c.months.indexOf(Math.max(...c.months));
    const links = cEdges.filter(v => v.a === c.id || v.b === c.id).length;
    h += `<div class="card${c.id === selComm ? ' on' : ''}" data-c="${c.id}"><b><i style="background:${c.color}"></i>${c.top.slice(0, 3).join(', ')} <span style="color:var(--muted);font-weight:normal">· ${c.size} words</span></b>
      <div class="w">${c.top.slice(3, 10).join(', ')}</div><div class="mm">peak ${monthName(MONTHS[peak])} · ${c.titles.toLocaleString()} title mentions · linked to ${links} communities</div></div>`;
  });
  panel.innerHTML = h;
  panel.querySelectorAll('.card').forEach(el => el.addEventListener('click', () => selectCommunity(+el.dataset.c)));
}
function communityDetail(id) {
  const c = commInfo.find(x => x.id === id);
  const links = cEdges.filter(v => v.a === id || v.b === id).sort((p, q) => q.n - p.n);
  let h = `<h2><i style="display:inline-block;width:11px;height:11px;border-radius:50%;background:${c.color}"></i> ${c.top.slice(0, 3).join(', ')}</h2>
    <div class="sub">${c.size} words · ${c.titles.toLocaleString()} title mentions · <a class="x" id="open">open its words</a> · <a class="x" id="back">all communities</a></div>`;
  h += '<h3>Words, by strength</h3><div class="w" style="font-size:12px;color:var(--ink2)">' + c.members.slice(0, 30).map(i => `<a class="x" data-i="${i}">${N[i].t}</a>`).join(', ') + (c.size > 30 ? ` and ${c.size - 30} more` : '') + '</div>';
  h += '<h3>Titles by month</h3><div class="tl" style="grid-template-columns:repeat(9,1fr);padding:0">' + c.months.map((v, k) => `<div class="m"><h4>${monthShort(MONTHS[k])}</h4><div class="bar" style="width:${Math.round(100 * v / Math.max(...c.months))}%"></div><div class="cnt">${v.toLocaleString()}</div></div>`).join('') + '</div>';
  h += `<h3>Linked communities (pairs crossing between them)</h3><table><tr><th>community</th><th class="num">pairs</th><th>strongest pair</th></tr>`;
  links.forEach(v => { const o = commInfo.find(x => x.id === (v.a === id ? v.b : v.a)); const t = v.top[0]; h += `<tr class="link" data-c="${o.id}"><td><i style="display:inline-block;width:9px;height:9px;border-radius:50%;background:${o.color};margin-right:4px"></i>${o.top.slice(0, 2).join(', ')}</td><td class="num">${v.n}</td><td>${N[t[0]].t} + ${N[t[1]].t} (${t[2].toFixed(0)}x)</td></tr>`; });
  h += '</table><div class="note">Cross-community pairs are the places where two stories meet in the same titles.</div>';
  panel.innerHTML = h;
  panel.querySelector('#open').addEventListener('click', () => openCommunity(id));
  panel.querySelector('#back').addEventListener('click', () => selectCommunity(-1));
  panel.querySelectorAll('a.x[data-i]').forEach(a => a.addEventListener('click', () => { openCommunity(id); select(+a.dataset.i); }));
  panel.querySelectorAll('tr.link').forEach(tr => tr.addEventListener('click', () => selectCommunity(+tr.dataset.c)));
}
function rankingPanel() {
  const measures = [['strength', i => str[i], v => v.toFixed(1)], ['degree', i => deg[i], v => v], ['betweenness (year)', i => N[i].b, v => v.toFixed(3)]];
  let h = `<h2>${openComm >= 0 ? commInfo.find(c => c.id === openComm).top.slice(0, 3).join(', ') : 'All words'}</h2><div class="sub">${openComm >= 0 ? '<a class="x" id="back">all communities</a> · ' : ''}Click a word in the map or a name below. Degree and strength are for the edges on screen (${month === 'all' ? 'the whole year' : monthName(month)}, lift ≥ ${minLift}x).</div>`;
  measures.forEach(([name, f, fmt]) => {
    const top = N.map((_, i) => i).filter(i => visibleNode(i) && inFocusComm(i)).sort((a, b) => f(b) - f(a)).slice(0, 12);
    h += `<h3>Top by ${name}</h3><table>` + top.map(i => `<tr class="link" data-i="${i}"><td><i style="display:inline-block;width:9px;height:9px;border-radius:50%;background:${commOf(i).color};margin-right:4px"></i>${N[i].t}</td><td class="num">${fmt(f(i))}</td></tr>`).join('') + '</table>';
  });
  h += "<div class='note'>Degree: how many partners. Strength: the sum of the partners' log2 lifts. Betweenness: how often the word lies on the shortest path between two others, a bridge between stories.</div>";
  panel.innerHTML = h;
  panel.querySelectorAll('tr.link').forEach(tr => tr.addEventListener('click', () => select(+tr.dataset.i)));
  const b = panel.querySelector('#back'); if (b) b.addEventListener('click', () => { openComm = -1; setMode('communities'); buildLegend(); });
}
function wordPanel(i) {
  const n = N[i], nb = (adj.get(i) || []).slice().sort((a, b) => b.lift - a.lift), c = commOf(i);
  let h = `<h2>${n.t}</h2><div class="sub">${n.n.toLocaleString()} titles · degree ${deg[i]} · strength ${str[i].toFixed(1)} · betweenness ${n.b} · community <a class="x" id="cm"><i style="display:inline-block;width:9px;height:9px;border-radius:50%;background:${c.color}"></i> ${c.top.slice(0, 3).join(', ')}</a></div>`;
  h += `<div class="sub">${nb.length} partners ${month === 'all' ? 'over the year' : 'in ' + monthName(month)} at lift ≥ ${minLift}x</div>`;
  const showAud = NET === 'all' && month === 'all' && GT.left;
  h += '<table><tr><th>partner</th><th class="num">lift</th>' + (month === 'all' ? '<th class="num">z</th>' : '') + '<th class="num">titles</th><th class="num">channels</th>' + (showAud ? '<th title="co-mentions per thousand titles of the left and of the right channels">L / R per 1k</th>' : '') + '</tr>';
  nb.forEach(a => { let aud = '';
    if (showAud && a.e) { const b = audienceBalance(a.e); if (b !== null) aud = `<td><i style="display:inline-block;width:9px;height:9px;border-radius:2px;background:${balanceColor(b)}1)"></i> ${(a.e[6] / GT.left * 1000).toFixed(1)} / ${(a.e[8] / GT.right * 1000).toFixed(1)}</td>`; else aud = '<td></td>'; }
    h += `<tr class="link" data-i="${a.j}"><td><i style="display:inline-block;width:9px;height:9px;border-radius:50%;background:${commOf(a.j).color};margin-right:4px"></i>${N[a.j].t}</td><td class="num">${a.lift.toFixed(1)}</td>` + (month === 'all' ? `<td class="num">${a.z}</td>` : '') + `<td class="num">${a.obs}</td><td class="num">${a.ch}</td>${aud}</tr>`; });
  h += '</table>';
  if (showAud) h += '<div class="note">Audience: blue when the left channels make the pair more often per title, orange when the right do, gray when both do alike. Neutral channels count in titles and lift but not in the balance.</div>';
  panel.innerHTML = h;
  panel.querySelectorAll('tr.link').forEach(tr => tr.addEventListener('click', () => select(+tr.dataset.i)));
  panel.querySelector('#cm').addEventListener('click', () => { setMode('communities'); selectCommunity(comm[i]); });
}
function timelineFor(i) {
  const n = N[i]; const maxT = Math.max(1, ...n.mt);
  let h = '<div class="tl">';
  MONTHS.forEach((m, k) => {
    const partners = (MONTHLY[m] || []).filter(e => e[0] === i || e[1] === i).map(e => ({j: e[0] === i ? e[1] : e[0], lift: e[2]})).sort((a, b) => b.lift - a.lift).slice(0, 6);
    h += `<div class="m"><h4>${monthShort(m)}</h4><div class="bar" style="width:${Math.round(100 * n.mt[k] / maxT)}%"></div><div class="cnt">${n.mt[k].toLocaleString()} titles · ${n.mc[k]} ch</div>` +
      partners.map(p => `<div class="p" data-i="${p.j}" title="${N[p.j].t}, ${p.lift.toFixed(1)}x">${N[p.j].t} <span style="color:var(--muted)">${p.lift.toFixed(0)}x</span></div>`).join('') + '</div>';
  });
  h += '</div>';
  if (NET !== 'all') h += '<div class="note" style="padding:0 12px 8px">Partners by month are computed for the all-channel network only; the bars are this audience\'s titles.</div>';
  timeline.innerHTML = h; timeline.classList.add('open');
  timeline.querySelectorAll('.p').forEach(el => el.addEventListener('click', () => select(+el.dataset.i)));
  setTimeout(resize, 160);
}
function showPanel() {
  if (mode === 'communities') { if (selComm >= 0) communityDetail(selComm); else communityCards(); return; }
  if (selected >= 0) wordPanel(selected); else rankingPanel();
}
// ---------- actions ----------
function setMode(m) {
  mode = m; document.getElementById('tabC').classList.toggle('on', m === 'communities'); document.getElementById('tabW').classList.toggle('on', m === 'words');
  if (m === 'communities') { selected = -1; timeline.classList.remove('open'); timeline.innerHTML = ''; setTimeout(resize, 160); }
  showPanel(); draw();
}
function selectCommunity(id) { selComm = id; showPanel(); draw(); }
function openCommunity(id) { openComm = id; selComm = -1; selected = -1; setMode('words'); buildLegend(); }
function fitVisible() {
  const r = canvas.getBoundingClientRect(); const vis = N.filter((_, i) => visibleNode(i) && inFocusComm(i)); if (!vis.length) return;
  const xs = vis.map(n => n.x), ys = vis.map(n => n.y); const w = Math.max(...xs) - Math.min(...xs) || 1, h = Math.max(...ys) - Math.min(...ys) || 1;
  view.k = Math.min(r.width / w, r.height / h) * 0.8; view.tx = r.width / 2 - (Math.min(...xs) + w / 2) * view.k; view.ty = r.height / 2 - (Math.min(...ys) + h / 2) * view.k; draw();
}
function select(i) {
  if (mode !== 'words') { openComm = -1; setMode('words'); }
  if (i >= 0 && !visibleNode(i)) { openComm = -1; buildLegend(); }
  selected = i;
  if (i >= 0) { const n = N[i]; const r = canvas.getBoundingClientRect(); view.tx = r.width / 2 - n.x * view.k; view.ty = r.height / 2 - n.y * view.k; timelineFor(i); }
  else { timeline.classList.remove('open'); timeline.innerHTML = ''; setTimeout(resize, 160); }
  showPanel(); draw();
}
canvas.addEventListener('mousedown', e => { dragging = true; moved = false; last = [e.clientX, e.clientY]; canvas.style.cursor = 'grabbing'; });
window.addEventListener('mouseup', e => {
  if (dragging && !moved) { const r = canvas.getBoundingClientRect(); const i = nodeAt(e.clientX - r.left, e.clientY - r.top);
    if (mode === 'communities') { if (i >= 0 && i === selComm) openCommunity(i); else selectCommunity(i); } else select(i); }
  dragging = false; canvas.style.cursor = 'grab';
});
canvas.addEventListener('mousemove', e => {
  const r = canvas.getBoundingClientRect(), px = e.clientX - r.left, py = e.clientY - r.top;
  if (dragging) { const dx = e.clientX - last[0], dy = e.clientY - last[1]; if (Math.abs(dx) + Math.abs(dy) > 2) moved = true; view.tx += dx; view.ty += dy; last = [e.clientX, e.clientY]; draw(); return; }
  const i = nodeAt(px, py);
  if (i !== hover) { hover = i; draw(); }
  if (i >= 0) { tip.style.display = 'block'; tip.style.left = (e.clientX + 14) + 'px'; tip.style.top = (e.clientY + 14) + 'px';
    if (mode === 'communities') { const c = commInfo.find(x => x.id === i); tip.innerHTML = `<b>${c.top.slice(0, 5).join(', ')}</b><br>${c.size} words · click to see, click again to open`; }
    else { const n = N[i]; tip.innerHTML = `<b>${n.t}</b><br>${n.n.toLocaleString()} titles · degree ${deg[i]} · strength ${str[i].toFixed(1)} · betweenness ${n.b}`; } }
  else tip.style.display = 'none';
});
canvas.addEventListener('mouseleave', () => { tip.style.display = 'none'; hover = -1; draw(); });
canvas.addEventListener('wheel', e => { e.preventDefault(); const r = canvas.getBoundingClientRect(), px = e.clientX - r.left, py = e.clientY - r.top; const f = Math.exp(-e.deltaY * 0.0015); view.tx = px - (px - view.tx) * f; view.ty = py - (py - view.ty) * f; view.k *= f; draw(); }, {passive: false});
window.addEventListener('keydown', e => { if (e.key === 'Escape') { if (mode === 'words') select(-1); else selectCommunity(-1); } });
document.getElementById('tabC').addEventListener('click', () => { openComm = -1; setMode('communities'); buildLegend(); });
document.getElementById('tabW').addEventListener('click', () => { openComm = -1; setMode('words'); buildLegend(); });
const dl = document.getElementById('terms'); N.slice().sort((a, b) => b.n - a.n).forEach(n => { const o = document.createElement('option'); o.value = n.t; dl.appendChild(o); });
document.getElementById('q').addEventListener('change', e => { const i = byName.get(e.target.value.trim().toLowerCase()); if (i !== undefined) select(i); });
const ms = document.getElementById('month'); MONTHS.forEach(m => { const o = document.createElement('option'); o.value = m; o.textContent = monthName(m) + ' 2026'; ms.appendChild(o); });
ms.addEventListener('change', e => { month = e.target.value; buildEdges(); layoutCommunities(); showPanel(); draw(); });
document.getElementById('lift').addEventListener('input', e => { minLift = Math.pow(2, +e.target.value); document.getElementById('liftv').textContent = minLift.toFixed(minLift < 4 ? 1 : 0) + 'x'; buildEdges(); layoutCommunities(); showPanel(); draw(); });
document.getElementById('sizeby').addEventListener('change', e => { sizeBy = e.target.value; draw(); });
document.getElementById('colorby').addEventListener('change', e => { colorBy = e.target.value; buildLegend(); draw(); });
document.getElementById('res').addEventListener('change', e => { resolution = +e.target.value; document.getElementById('resv').textContent = resolution.toFixed(1); runCommunities(); showPanel(); draw(); });
document.getElementById('res').addEventListener('input', e => { document.getElementById('resv').textContent = (+e.target.value).toFixed(1); });
document.getElementById('reshuffle').addEventListener('click', () => { seed++; runCommunities(); showPanel(); draw(); });
document.getElementById('labels').addEventListener('change', e => { showLabels = e.target.checked; draw(); });
document.getElementById('net').addEventListener('change', e => setNetwork(e.target.value));
document.getElementById('edgecolor').addEventListener('change', e => { edgeColor = e.target.value; buildLegend(); draw(); });
document.getElementById('fit').addEventListener('click', fitVisible);
window.addEventListener('resize', resize);
buildEdges(); runCommunities(); showPanel(); resize();
</script>
</body>
</html>
"""


def main() -> int:
    data = build_data()
    html = TEMPLATE.replace("__DATA__", json.dumps(data, separators=(",", ":")).replace("</", "<\\/")).replace("__NODES__", f"{data['meta']['nodes']:,}").replace("__EDGES__", f"{data['meta']['edges']:,}")
    OUT.write_text(html, encoding="utf-8")
    print(f"{OUT} ({OUT.stat().st_size / 1e6:.1f} MB): {data['meta']['nodes']:,} nodes, {data['meta']['edges']:,} edges, {len(data['networks'])} networks")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
