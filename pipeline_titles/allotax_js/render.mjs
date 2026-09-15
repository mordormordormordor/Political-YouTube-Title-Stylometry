// Render one allotaxonograph (Dodds, Minot, Arnold, Alshaabi, Adams, Dewhurst, Gray, Frank, Reagan and Danforth,
// "Allotaxonometry and rank-turbulence divergence: a universal instrument for comparing complex systems",
// EPJ Data Science 2023) with the Computational Story Lab's own renderer, allotaxonometer-ui (Svelte, server-side),
// and print it to PNG through Puppeteer. Called by pipeline_titles/allotax.py.
//
//   node render.mjs spec.json
//
// spec: { data1, data2: [{types, counts, totalunique, probs}], alpha, alpha_label, title1, title2, short1, short2,
//         top_n, out_png, out_html, out_json, json_top, scale, viewport_width }
import fs from 'fs';
import puppeteer from 'puppeteer';
import * as d3 from 'd3';
import { combElems, rank_turbulence_divergence, diamond_count, wordShift_dat, balanceDat } from 'allotaxonometer-ui';
import { Dashboard } from 'allotaxonometer-ui/ssr';
import { render } from 'svelte/server';

const spec = JSON.parse(fs.readFileSync(process.argv[2], 'utf8'));
const { data1, data2, alpha, title1, title2 } = spec;
const topN = spec.top_n || 40;

const me = combElems(data1, data2);                       // union of types, tied ranks per system (absent types share the last rank)
const rtd = rank_turbulence_divergence(me, alpha);        // per-type contributions, normalised so disjoint systems give D = 1
const dat = diamond_count(me, rtd);                       // diamond cells at 1/15-decade resolution; re-orders me[*] by contribution
const D = rtd.divergence_elements.reduce((a, b) => a + b, 0);
const maxlog10 = Math.ceil(Math.max(Math.log10(Math.max(...me[0].ranks)), Math.log10(Math.max(...me[1].ranks))));
const max_count_log = Math.ceil(Math.log10(d3.max(dat.counts, d => d.value))) + 1;
const barData = wordShift_dat(me, dat).slice(0, topN);
const max_shift = d3.max(barData, d => Math.abs(d.metric));
const balanceData = balanceDat(data1, data2);
const W = spec.width || 4200, H = spec.height || 2970;

const result = render(Dashboard, { props: { dat, alpha, divnorm: rtd.normalization, barData, balanceData, title: [title1, title2], maxlog10, max_count_log,
  width: W, height: H, DashboardWidth: W, DashboardHeight: H, marginInner: 160, marginDiamond: 40, xDomain: [-max_shift * 1.5, max_shift * 1.5],
  showDiamond: true, showWordshift: true, showDivergingBar: true, showLegend: true } });
let body = result.body;
if (spec.alpha_label) {   // alpha as written (1/3) and the divergence value under the instrument name, as in the paper's figures
  body = body.replace(`<div>α = ${alpha}</div>`, `<div>α = ${spec.alpha_label}</div><div style="margin-top: 0.6em;">D<sup>R</sup><sub>${spec.alpha_label}</sub> = ${D.toFixed(3)}</div>`);
}
if (spec.short1 && spec.short2) {   // name the systems in the wordshift header
  body = body.replace('← System 1 · Divergence contribution · System 2 →', `← ${spec.short1} · Divergence contribution · ${spec.short2} →`);
}
const html = `<!DOCTYPE html><html><head><meta charset="utf-8"><title>${title1} vs ${title2}</title><style>body{margin:0;padding:24px;font-family:system-ui,sans-serif;background:white}</style>${result.head || ''}</head><body>${body}</body></html>`;
if (spec.out_html) fs.writeFileSync(spec.out_html, html);

if (spec.out_json) {
  // diamond_count() re-orders me[*] by descending delta and returns the deltas in that order (dat.deltas)
  const contrib = dat.deltas.map((delta, i) => ({ type: me[0].types[i], rank1: me[0].ranks[i], rank2: me[1].ranks[i], count1: me[0].counts[i], count2: me[1].counts[i],
    contribution: (me[0].ranks[i] > me[1].ranks[i] ? 1 : -1) * delta }));   // positive = more prominent in system 2 (bars to the right)
  const pkgVersion = (name) => { try { return JSON.parse(fs.readFileSync(new URL(`./node_modules/${name}/package.json`, import.meta.url), 'utf8')).version; } catch { return null; } };
  const versions = { 'allotaxonometer-ui': pkgVersion('allotaxonometer-ui'), puppeteer: pkgVersion('puppeteer'), node: process.version };
  fs.writeFileSync(spec.out_json, JSON.stringify({ alpha, alpha_label: spec.alpha_label || String(alpha), divergence: D, normalization: rtd.normalization,
    n_types_union: me[0].types.length, n_types_1: data1.length, n_types_2: data2.length, top: contrib.slice(0, spec.json_top || 100), balance: balanceData, versions }, null, 1));
}

if (spec.out_png) {
  const browser = await puppeteer.launch({ headless: true, args: ['--no-sandbox', '--disable-setuid-sandbox'] });
  const page = await browser.newPage();
  await page.setViewport({ width: spec.viewport_width || 1500, height: 1400, deviceScaleFactor: spec.scale || 2 });   // narrow enough that the wordshift packs beside the diamond
  await page.setContent(html, { waitUntil: 'networkidle0', timeout: 60000 });
  const box = await page.evaluate(() => {
    let x0 = Infinity, y0 = Infinity, x1 = 0, y1 = 0;
    for (const el of document.querySelectorAll('svg, svg *, div')) {
      const r = el.getBoundingClientRect();
      if (r.width === 0 && r.height === 0) continue;
      x0 = Math.min(x0, r.left); y0 = Math.min(y0, r.top); x1 = Math.max(x1, r.right); y1 = Math.max(y1, r.bottom);
    }
    return { x0, y0, x1, y1 };
  });
  const pad = 16;
  const clip = { x: Math.max(0, box.x0 - pad), y: Math.max(0, box.y0 - pad), width: box.x1 - box.x0 + 2 * pad, height: box.y1 - box.y0 + 2 * pad };
  await page.setViewport({ width: Math.ceil(clip.x + clip.width) + 10, height: Math.ceil(clip.y + clip.height) + 10, deviceScaleFactor: spec.scale || 2 });
  await page.screenshot({ path: spec.out_png, clip });
  await browser.close();
}
console.log(`D=${D.toFixed(4)} types=${me[0].types.length} bars=${barData.length}${spec.out_png ? ' png=' + spec.out_png : ''}`);
