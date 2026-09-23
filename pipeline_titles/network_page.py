"""The word-association network as a page to explore (pipeline_titles/reports/word_network.html).

Nodes are the vocabulary terms of the associations stage; an edge is a pair that co-mentions
beyond chance within creator-weeks (Cochran-Mantel-Haenszel q < 0.01), replicated in both channel
halves, with lift >= 2 from >= 5 channels (assoc_edges.csv, assoc_nodes.csv); the month view uses
each month's own edges (assoc_monthly_neighbors.csv.gz). Positions come from ForceAtlas2 on the
edge weights (log2 lift), seed fixed. The page is self-contained: no network access, no libraries.

    python -m pipeline_titles.network_page
"""

from __future__ import annotations

import json
import math

import networkx as nx
import numpy as np
import pandas as pd

from pipeline_titles.common import ANALYSIS_DIR as A, REPORTS_DIR, SEED
from pipeline_titles.figures import CAT

OUT = REPORTS_DIR / "word_network.html"
HUES = 7


def build_data() -> dict:
    nodes = pd.read_csv(A / "assoc_nodes.csv")
    edges = pd.read_csv(A / "assoc_edges.csv")
    comms = pd.read_csv(A / "assoc_communities.csv")
    G = nx.Graph()
    for r in nodes.itertuples():
        G.add_node(r.term)
    for r in edges.itertuples():
        G.add_edge(r.term_a, r.term_b, weight=float(r.weight))
    pos = nx.forceatlas2_layout(G, max_iter=400, weight="weight", seed=SEED, scaling_ratio=2.0, gravity=1.0)
    xy = np.array([pos[t] for t in nodes["term"]])
    xy = (xy - xy.mean(axis=0)) / xy.std(axis=0).max()
    idx = {t: i for i, t in enumerate(nodes["term"])}
    sizes = nodes.groupby("community").size().sort_values(ascending=False)
    hue_rank = {int(c): i for i, c in enumerate(sizes.index)}
    top_terms = comms.set_index("community")["top_terms"].to_dict()
    data_nodes = [{"t": r.term, "x": round(float(xy[i, 0]), 4), "y": round(float(xy[i, 1]), 4), "c": int(r.community), "s": round(float(r.strength), 2),
                   "d": int(r.degree), "n": int(r.n_titles), "b": round(float(r.betweenness), 4)} for i, r in enumerate(nodes.itertuples())]
    data_edges = [[idx[r.term_a], idx[r.term_b], round(float(r.lift_strat), 2), round(float(r.z_cmh), 1), int(r.channels), int(r.observed)] for r in edges.itertuples()]
    nb = pd.read_csv(A / "assoc_monthly_neighbors.csv.gz")
    keep = set(idx)
    nb = nb[nb["term"].isin(keep) & nb["neighbor"].isin(keep)]
    monthly = {}
    for m, g in nb.groupby("month"):
        seen = {}
        for r in g.itertuples():
            key = (min(idx[r.term], idx[r.neighbor]), max(idx[r.term], idx[r.neighbor]))
            if key not in seen:
                seen[key] = [key[0], key[1], round(float(r.lift), 2), int(r.channels), int(r.observed)]
        monthly[m] = list(seen.values())
    communities = [{"id": int(c), "rank": hue_rank[int(c)], "size": int(sizes[c]), "color": CAT[hue_rank[int(c)]] if hue_rank[int(c)] < HUES else "#b3b2ad",
                    "top": str(top_terms.get(int(c), ""))} for c in sizes.index]
    return {"nodes": data_nodes, "edges": data_edges, "monthly": monthly, "communities": communities,
            "meta": {"nodes": len(data_nodes), "edges": len(data_edges), "months": sorted(monthly)}}


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
h1 { font-size:17px; margin:0 0 2px; }
header p { margin:0 0 8px; color:var(--ink2); font-size:13px; }
.controls { display:flex; flex-wrap:wrap; gap:10px 18px; align-items:center; font-size:13px; }
.controls label { display:flex; align-items:center; gap:6px; color:var(--ink2); }
input[type=search] { padding:4px 8px; border:1px solid var(--grid); border-radius:4px; font:inherit; width:200px; }
select { font:inherit; padding:3px 6px; }
.legend { display:flex; flex-wrap:wrap; gap:6px 12px; }
.chip { display:inline-flex; align-items:center; gap:5px; cursor:pointer; user-select:none; color:var(--ink2); }
.chip.off { opacity:.35; }
.chip i { width:11px; height:11px; border-radius:50%; display:inline-block; }
main { display:flex; height:calc(100% - 118px); }
canvas { flex:1; display:block; cursor:grab; }
aside { width:340px; border-left:1px solid var(--grid); background:var(--panel); padding:12px 14px; overflow:auto; font-size:13px; }
aside h2 { font-size:15px; margin:0 0 4px; }
aside .sub { color:var(--muted); margin-bottom:8px; }
table { border-collapse:collapse; width:100%; }
th, td { text-align:left; padding:3px 4px; border-bottom:1px solid var(--grid); font-variant-numeric:tabular-nums; }
th { color:var(--muted); font-weight:600; font-size:12px; }
td.num, th.num { text-align:right; }
tr.link { cursor:pointer; }
tr.link:hover { background:#ebeae6; }
.tip { position:fixed; pointer-events:none; background:#fff; border:1px solid var(--grid); border-radius:4px; padding:6px 8px; font-size:12px; color:var(--ink2); box-shadow:0 2px 8px rgba(0,0,0,.08); display:none; z-index:5; }
.tip b { color:var(--ink); }
.note { color:var(--muted); font-size:12px; margin-top:12px; }
@media (max-width: 800px) { main { flex-direction:column; } aside { width:auto; height:40%; border-left:0; border-top:1px solid var(--grid); } }
</style>
</head>
<body>
<header>
  <h1>Word association network: __NODES__ words, __EDGES__ edges</h1>
  <p>An edge joins two words that share titles beyond chance within the same channel and week, in both random halves of the channels (lift at least 2, from at least 5 channels). Node size is strength, color is the year's community. Click a word for its partners; drag to pan, scroll to zoom.</p>
  <div class="controls">
    <label>Find <input type="search" id="q" list="terms" placeholder="type a word"><datalist id="terms"></datalist></label>
    <label>Edges of <select id="month"><option value="all">the whole year</option></select></label>
    <label>Lift at least <input type="range" id="lift" min="1" max="6" step="0.25" value="1"> <span id="liftv">2x</span></label>
    <label><input type="checkbox" id="labels" checked> labels</label>
    <div class="legend" id="legend"></div>
  </div>
</header>
<main>
  <canvas id="c"></canvas>
  <aside id="panel"><h2>Nothing selected</h2><div class="sub">Click a word in the map, or type one above.</div><div class="note">Strength is the sum of a word's edges' log2 lifts. Lift is a pair's co-mentions over the number expected within creator-weeks. Channels: how many channels co-mention the pair.</div></aside>
</main>
<div class="tip" id="tip"></div>
<script id="data" type="application/json">__DATA__</script>
<script>
const D = JSON.parse(document.getElementById('data').textContent);
const N = D.nodes, E = D.edges, C = D.communities;
const colorOf = {}; C.forEach(c => colorOf[c.id] = c.color);
const hidden = new Set();
const canvas = document.getElementById('c'), ctx = canvas.getContext('2d');
const tip = document.getElementById('tip'), panel = document.getElementById('panel');
let view = {k: 1, tx: 0, ty: 0}, dragging = false, moved = false, last = null;
let selected = -1, hover = -1, month = 'all', minLift = 2, showLabels = true;
let edgesNow = E, adj = new Map();
const byName = new Map(N.map((n, i) => [n.t, i]));
const maxS = Math.max(...N.map(n => n.s));
const radius = n => 2.2 + 9 * Math.sqrt(n.s / maxS);

function buildAdj() {
  adj = new Map();
  edgesNow.forEach(e => {
    if (e[2] < minLift) return;
    if (!adj.has(e[0])) adj.set(e[0], []);
    if (!adj.has(e[1])) adj.set(e[1], []);
    adj.get(e[0]).push({j: e[1], lift: e[2], z: e[3], ch: e[4], obs: e[5]});
    adj.get(e[1]).push({j: e[0], lift: e[2], z: e[3], ch: e[4], obs: e[5]});
  });
}
function setMonth(m) {
  month = m;
  edgesNow = m === 'all' ? E : D.monthly[m].map(e => [e[0], e[1], e[2], NaN, e[3], e[4]]);
  buildAdj(); draw(); showPanel();
}
function resize() {
  const r = canvas.getBoundingClientRect();
  canvas.width = r.width * devicePixelRatio; canvas.height = r.height * devicePixelRatio;
  ctx.setTransform(devicePixelRatio, 0, 0, devicePixelRatio, 0, 0);
  if (!view.init) { view.k = Math.min(r.width, r.height) * 0.42; view.tx = r.width / 2; view.ty = r.height / 2; view.init = true; }
  draw();
}
const sx = n => n.x * view.k + view.tx, sy = n => n.y * view.k + view.ty;
function draw() {
  const r = canvas.getBoundingClientRect();
  ctx.clearRect(0, 0, r.width, r.height);
  const focus = selected >= 0 ? new Set([selected, ...(adj.get(selected) || []).map(a => a.j)]) : null;
  const vis = i => !hidden.has(N[i].c);
  // edges
  ctx.lineCap = 'round';
  edgesNow.forEach(e => {
    if (e[2] < minLift || !vis(e[0]) || !vis(e[1])) return;
    const inFocus = focus && (e[0] === selected || e[1] === selected);
    if (focus && !inFocus) return;
    const w = Math.log2(e[2]);
    ctx.strokeStyle = inFocus ? 'rgba(42,120,214,0.75)' : `rgba(82,81,78,${Math.min(0.45, 0.05 + 0.05 * w)})`;
    ctx.lineWidth = Math.max(0.4, Math.min(3, 0.3 + 0.35 * w)) * (inFocus ? 1.4 : 1);
    ctx.beginPath(); ctx.moveTo(sx(N[e[0]]), sy(N[e[0]])); ctx.lineTo(sx(N[e[1]]), sy(N[e[1]])); ctx.stroke();
  });
  // nodes
  const order = N.map((n, i) => i).sort((a, b) => N[a].s - N[b].s);
  order.forEach(i => {
    const n = N[i]; if (!vis(i)) return;
    const dim = focus && !focus.has(i);
    ctx.globalAlpha = dim ? 0.12 : 1;
    ctx.beginPath(); ctx.arc(sx(n), sy(n), radius(n), 0, Math.PI * 2);
    ctx.fillStyle = colorOf[n.c] || '#b3b2ad'; ctx.fill();
    ctx.lineWidth = i === selected || i === hover ? 2 : 1; ctx.strokeStyle = i === selected ? '#0b0b0b' : '#fcfcfb'; ctx.stroke();
    ctx.globalAlpha = 1;
  });
  // labels: the strongest at this zoom, plus the selection and its partners
  if (showLabels) {
    ctx.font = '11px -apple-system, "Segoe UI", Helvetica, Arial, sans-serif'; ctx.textAlign = 'center'; ctx.textBaseline = 'bottom';
    const budget = Math.round(40 * Math.max(1, view.k / (Math.min(r.width, r.height) * 0.42)) ** 1.6);
    const labeled = new Set(order.slice(-budget));
    if (focus) focus.forEach(i => labeled.add(i));
    const placed = [];
    [...labeled].sort((a, b) => N[b].s - N[a].s).forEach(i => {
      const n = N[i]; if (!vis(i)) return; if (focus && !focus.has(i)) return;
      const x = sx(n), y = sy(n) - radius(n) - 2, w = ctx.measureText(n.t).width;
      if (x < -20 || y < -20 || x > r.width + 20 || y > r.height + 20) return;
      if (placed.some(p => Math.abs(p.x - x) < (p.w + w) / 2 + 4 && Math.abs(p.y - y) < 13)) return;
      placed.push({x, y, w});
      ctx.strokeStyle = 'rgba(252,252,251,0.9)'; ctx.lineWidth = 3; ctx.strokeText(n.t, x, y);
      ctx.fillStyle = i === selected ? '#0b0b0b' : '#52514e'; ctx.font = (i === selected ? 'bold 12px' : '11px') + ' -apple-system, "Segoe UI", Helvetica, Arial, sans-serif';
      ctx.fillText(n.t, x, y);
    });
  }
}
function nodeAt(px, py) {
  let best = -1, bd = 1e9;
  N.forEach((n, i) => {
    if (hidden.has(n.c)) return;
    const d = Math.hypot(sx(n) - px, sy(n) - py);
    if (d < Math.max(radius(n) + 3, 8) && d < bd) { bd = d; best = i; }
  });
  return best;
}
function showPanel() {
  if (selected < 0) { panel.innerHTML = '<h2>Nothing selected</h2><div class="sub">Click a word in the map, or type one above.</div>'; return; }
  const n = N[selected], nb = (adj.get(selected) || []).slice().sort((a, b) => b.lift - a.lift);
  const comm = C.find(c => c.id === n.c);
  let h = `<h2>${n.t}</h2><div class="sub">${n.n.toLocaleString()} titles; degree ${n.d}, strength ${n.s}, betweenness ${n.b}; community: ${comm ? comm.top.split(', ').slice(0, 4).join(', ') : n.c}</div>`;
  h += `<div class="sub">${nb.length} partners ${month === 'all' ? 'over the year' : 'in ' + monthName(month)} at lift ≥ ${minLift}x</div>`;
  h += '<table><tr><th>partner</th><th class="num">lift</th>' + (month === 'all' ? '<th class="num">z</th>' : '') + '<th class="num">titles</th><th class="num">channels</th></tr>';
  nb.forEach(a => { h += `<tr class="link" data-i="${a.j}"><td>${N[a.j].t}</td><td class="num">${a.lift.toFixed(1)}</td>` + (month === 'all' ? `<td class="num">${a.z}</td>` : '') + `<td class="num">${a.obs}</td><td class="num">${a.ch}</td></tr>`; });
  h += '</table>';
  if (month === 'all') {
    const months = D.meta.months.filter(m => (D.monthly[m] || []).some(e => e[0] === selected || e[1] === selected));
    h += `<div class="note">Has edges in: ${months.map(monthName).join(', ') || 'no month on its own'}.</div>`;
  }
  panel.innerHTML = h;
  panel.querySelectorAll('tr.link').forEach(tr => tr.addEventListener('click', () => select(+tr.dataset.i)));
}
function monthName(m) { return new Date(m + '-15').toLocaleString('en-US', {month: 'long'}); }
function select(i) { selected = i; if (i >= 0) { const n = N[i]; const r = canvas.getBoundingClientRect(); view.tx = r.width / 2 - n.x * view.k; view.ty = r.height / 2 - n.y * view.k; } showPanel(); draw(); }
canvas.addEventListener('mousedown', e => { dragging = true; moved = false; last = [e.clientX, e.clientY]; canvas.style.cursor = 'grabbing'; });
window.addEventListener('mouseup', e => { if (dragging && !moved) { const r = canvas.getBoundingClientRect(); const i = nodeAt(e.clientX - r.left, e.clientY - r.top); select(i); } dragging = false; canvas.style.cursor = 'grab'; });
canvas.addEventListener('mousemove', e => {
  const r = canvas.getBoundingClientRect(), px = e.clientX - r.left, py = e.clientY - r.top;
  if (dragging) { const dx = e.clientX - last[0], dy = e.clientY - last[1]; if (Math.abs(dx) + Math.abs(dy) > 2) moved = true; view.tx += dx; view.ty += dy; last = [e.clientX, e.clientY]; draw(); return; }
  const i = nodeAt(px, py);
  if (i !== hover) { hover = i; draw(); }
  if (i >= 0) { const n = N[i]; tip.style.display = 'block'; tip.style.left = (e.clientX + 14) + 'px'; tip.style.top = (e.clientY + 14) + 'px';
    tip.innerHTML = `<b>${n.t}</b><br>${n.n.toLocaleString()} titles · ${(adj.get(i) || []).length} partners · strength ${n.s}`; }
  else tip.style.display = 'none';
});
canvas.addEventListener('mouseleave', () => { tip.style.display = 'none'; hover = -1; draw(); });
canvas.addEventListener('wheel', e => { e.preventDefault(); const r = canvas.getBoundingClientRect(), px = e.clientX - r.left, py = e.clientY - r.top; const f = Math.exp(-e.deltaY * 0.0015); view.tx = px - (px - view.tx) * f; view.ty = py - (py - view.ty) * f; view.k *= f; draw(); }, {passive: false});
window.addEventListener('keydown', e => { if (e.key === 'Escape') select(-1); });
// controls
const dl = document.getElementById('terms'); N.slice().sort((a, b) => b.s - a.s).forEach(n => { const o = document.createElement('option'); o.value = n.t; dl.appendChild(o); });
document.getElementById('q').addEventListener('change', e => { const i = byName.get(e.target.value.trim().toLowerCase()); if (i !== undefined) select(i); });
const ms = document.getElementById('month'); D.meta.months.forEach(m => { const o = document.createElement('option'); o.value = m; o.textContent = monthName(m) + ' 2026'; ms.appendChild(o); });
ms.addEventListener('change', e => setMonth(e.target.value));
document.getElementById('lift').addEventListener('input', e => { minLift = Math.pow(2, +e.target.value); document.getElementById('liftv').textContent = minLift.toFixed(minLift < 4 ? 1 : 0) + 'x'; buildAdj(); showPanel(); draw(); });
document.getElementById('labels').addEventListener('change', e => { showLabels = e.target.checked; draw(); });
const legend = document.getElementById('legend');
C.slice(0, 8).forEach(c => { const s = document.createElement('span'); s.className = 'chip'; s.innerHTML = `<i style="background:${c.color}"></i>${c.top.split(', ').slice(0, 3).join(', ')} (${c.size})`;
  s.addEventListener('click', () => { if (hidden.has(c.id)) hidden.delete(c.id); else hidden.add(c.id); s.classList.toggle('off'); draw(); }); legend.appendChild(s); });
const others = document.createElement('span'); others.className = 'chip'; others.innerHTML = `<i style="background:#b3b2ad"></i>${C.length - 7} smaller communities`; legend.appendChild(others);
window.addEventListener('resize', resize);
buildAdj(); resize();
</script>
</body>
</html>
"""


def main() -> int:
    data = build_data()
    html = TEMPLATE.replace("__DATA__", json.dumps(data, separators=(",", ":")).replace("</", "<\\/")).replace("__NODES__", f"{data['meta']['nodes']:,}").replace("__EDGES__", f"{data['meta']['edges']:,}")
    OUT.write_text(html, encoding="utf-8")
    print(f"{OUT} ({OUT.stat().st_size / 1e6:.1f} MB): {data['meta']['nodes']:,} nodes, {data['meta']['edges']:,} edges, {len(data['monthly'])} months")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
