"""HTML page for the Title Stylometry deliverables: a creator selector that
renders the profile cards, plus the two landscape maps (style space: PCA of the
topic-controlled factor scores; topic space: MDS of the Jensen-Shannon distances
between topic mixes). Self-contained: cards.json is embedded, no external files.
"""

from __future__ import annotations

import json

import pandas as pd

CSS = """
:root{--bg:#fafaf8;--fg:#1c1c1a;--muted:#6b6b66;--line:#dcdcd6;--card:#ffffff;--accent:#b5462b;--bar:#d8d3c6;--bar-fill:#b5462b;--hl:#fff3e0}
@media (prefers-color-scheme: dark){:root{--bg:#161615;--fg:#ececea;--muted:#a3a39c;--line:#3a3a36;--card:#1f1f1d;--accent:#e8825f;--bar:#3a3a36;--bar-fill:#e8825f;--hl:#3a2a1c}}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--fg);font:14px/1.45 system-ui,-apple-system,Segoe UI,Roboto,sans-serif;padding:16px}
h1{font-size:22px;margin:0 0 4px}h2{font-size:17px;margin:18px 0 8px}h3{font-size:14px;margin:12px 0 6px;color:var(--muted);text-transform:uppercase;letter-spacing:.04em}
.muted{color:var(--muted)}.row{display:flex;gap:16px;flex-wrap:wrap}.col{flex:1 1 420px;min-width:0}
.card{background:var(--card);border:1px solid var(--line);border-radius:8px;padding:14px 16px;margin-bottom:16px}
table{border-collapse:collapse;width:100%;font-size:13px}th,td{border-bottom:1px solid var(--line);padding:4px 6px;text-align:left;vertical-align:top}th{color:var(--muted);font-weight:600}
td.num,th.num{text-align:right;font-variant-numeric:tabular-nums}
.bar{position:relative;height:10px;background:var(--bar);border-radius:5px;min-width:120px}.bar>i{position:absolute;left:0;top:0;bottom:0;background:var(--bar-fill);border-radius:5px}
.bar>b{position:absolute;top:-3px;width:2px;height:16px;background:var(--fg);opacity:.7}
select,input{font:inherit;padding:6px 8px;border:1px solid var(--line);border-radius:6px;background:var(--card);color:var(--fg)}
.controls{display:flex;gap:10px;flex-wrap:wrap;align-items:center;margin:10px 0 14px}
.legend span{display:inline-flex;align-items:center;gap:4px;margin:0 8px 4px 0;font-size:12px}.legend i{width:10px;height:10px;border-radius:50%;display:inline-block}
svg.map{width:100%;height:auto;background:var(--card);border:1px solid var(--line);border-radius:8px}
svg.map circle{cursor:pointer}svg.map text.lbl{font-size:10px;fill:var(--fg);pointer-events:none}
.tip{position:fixed;pointer-events:none;background:var(--card);border:1px solid var(--line);padding:4px 8px;border-radius:6px;font-size:12px;display:none;z-index:9}
.chip{display:inline-block;padding:1px 7px;border:1px solid var(--line);border-radius:10px;font-size:12px;margin:0 4px 4px 0;cursor:pointer}.chip:hover{background:var(--hl)}
svg.spark{width:100%;height:46px}.sparkrow{display:grid;grid-template-columns:170px 1fr 60px;gap:8px;align-items:center;border-bottom:1px solid var(--line);padding:2px 0}
.small{font-size:12px}details summary{cursor:pointer;color:var(--muted)}
.allwrap{overflow-x:auto}table.all{font-size:12px;white-space:nowrap}table.all th{cursor:pointer;user-select:none;position:sticky;top:0;background:var(--card)}table.all th.sorted{color:var(--accent)}
table.all td.pc{text-align:center;min-width:34px;font-variant-numeric:tabular-nums}table.all td.name{cursor:pointer;font-weight:600}table.all td.name:hover{text-decoration:underline}
table.all tr.sel td{background:var(--hl)}
"""

JS = r"""
const D = JSON.parse(document.getElementById('data').textContent);
// channel groups (left / neutral / right from the leaning stage): left blue, neutral grey, right orange
const GROUP_COLORS = {left:'#2a78d6', neutral:'#8a8983', right:'#eb6834', unscored:'#c9c8c3'};
const GROUP_LABEL = {left:'left channels', neutral:'neutral channels', right:'right channels', unscored:'unscored'};
const $ = s=>document.querySelector(s);
const creators = Object.keys(D.creators).sort((a,b)=>a.toLowerCase().localeCompare(b.toLowerCase()));
const fmtPct = v => v==null?'':(100*v).toFixed(1)+'%';
const fmt = (v,d=2) => v==null?'':(+v).toFixed(d);
let genre = 'videos', current = creators[0];
function esc(s){return String(s).replace(/[&<>"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));}
function groupChip(g){return `<span class="chip" style="border-color:${GROUP_COLORS[g]||'#999'}" title="channel group from the title-leaning score (document 14)">${esc(GROUP_LABEL[g]||g||'?')}</span>`;}
function bar(pct, grp){ const p=Math.max(0,Math.min(100,pct||0)); return `<div class="bar"><i style="width:${p}%"></i>${grp!=null?`<b style="left:${Math.max(0,Math.min(100,grp))}%" title="group median percentile"></b>`:''}</div>`; }
function spark(vals, months, color){
  const w=300,h=40,xs=vals.map((_,i)=>i*(w-6)/(Math.max(vals.length-1,1))+3);
  const good=vals.filter(v=>v!=null); if(!good.length) return '';
  const mn=Math.min(...good),mx=Math.max(...good),rng=(mx-mn)||1;
  const ys=vals.map(v=>v==null?null:h-4-(v-mn)/rng*(h-8));
  let path='',pts=''; vals.forEach((v,i)=>{ if(v==null)return; path+=(path?' L':'M')+xs[i].toFixed(1)+' '+ys[i].toFixed(1); pts+=`<circle cx="${xs[i].toFixed(1)}" cy="${ys[i].toFixed(1)}" r="2.2" fill="${color}"><title>${months[i]}: ${fmt(v,3)}</title></circle>`; });
  return `<svg class="spark" viewBox="0 0 ${w} ${h}" preserveAspectRatio="none"><path d="${path}" fill="none" stroke="${color}" stroke-width="1.5"/>${pts}</svg>`;
}
function renderCard(){
  const c = D.creators[current]; const g = c.genres[genre];
  const other = Object.keys(c.genres).filter(k=>k!==genre);
  let h = `<h2>${esc(c.channel_name)} <span class="muted">${esc(c.creator)}</span></h2>
  <div>${groupChip(c.group)} organisation: <b>${esc(c.organisation)}</b> · clipper: <b>${c.clipper?'yes':'no'}</b> · ${esc(c.platform)} · subscribers: <b>${c.subscribers!=null?c.subscribers.toLocaleString():'n/a'}</b>${c.note?` · <span class="muted">${esc(c.note)}</span>`:''}</div>`;
  if(!g){ h += `<p class="muted">No ${genre} titles for this creator${other.length?` (has ${other.join(', ')})`:''}.</p>`; $('#card').innerHTML=h; return; }
  h += `<h3>${genre}</h3><p>${g.n_rows.toLocaleString()} titles, ${g.n_unique.toLocaleString()} unique (repeat share ${fmtPct(g.repeat_share)}) · ${g.low_n?'<b>low-n: reported, not ranked</b>':'ranked'} · political share ${fmtPct(g.political_share)} · ${g.first_month} to ${g.last_month}</p>`;
  h += `<h3>Topic mix (top 5)</h3><table>${g.topics_top5.map(t=>`<tr><td>${esc(t.label)}${t.political?'':' <span class="muted">(non-political)</span>'}</td><td class="num">${fmtPct(t.share)}</td><td style="width:40%">${bar(100*t.share/Math.max(...g.topics_top5.map(x=>x.share)))}</td></tr>`).join('')}</table>`;
  if(g.dimensions){
    h += `<h3>Style dimensions (percentile rank within ${genre}, topic-controlled; tick = median of the channel's group)</h3><table><tr><th>dimension</th><th class="num">pct</th><th style="width:40%"></th><th class="num">raw pct</th><th class="num">score</th><th class="num">group median</th></tr>`;
    for(const [f,d] of Object.entries(g.dimensions)){
      const grpPct = groupMedianPct(f, c.group);
      h += `<tr><td><b>${f}</b> ${esc(D.factors[f].name)}</td><td class="num">${fmt(d.pct_controlled,0)}</td><td>${bar(d.pct_controlled, grpPct)}</td><td class="num">${fmt(d.pct_raw,0)}</td><td class="num">${fmt(d.controlled)}</td><td class="num">${fmt(d.group_median)}</td></tr>`;
    }
    h += `</table>`;
  }
  if(g.hooks){
    h += `<h3>Hooks and formats (share of titles; group mean in brackets)</h3><table>`;
    for(const [k,v] of Object.entries({...g.hooks, ...g.formats})) h += `<tr><td>${k}</td><td class="num">${fmtPct(v.share)}</td><td style="width:40%">${bar(100*v.share)}</td><td class="num muted">(${fmtPct(v.group_mean)})</td></tr>`;
    h += `</table>`;
  }
  if(g.neighbours_style) h += `<h3>Nearest style neighbours</h3><div>${g.neighbours_style.map(n=>`<span class="chip" data-c="${esc(n.creator)}" style="border-color:${GROUP_COLORS[n.group]||'#999'}">${esc(n.creator)} <span class="muted">${esc(n.group)} · ${fmt(n.distance)}</span></span>`).join('')}</div>`;
  if(g.neighbours_topic) h += `<h3>Nearest topic neighbours</h3><div>${g.neighbours_topic.map(n=>`<span class="chip" data-c="${esc(n.creator)}" style="border-color:${GROUP_COLORS[n.group]||'#999'}">${esc(n.creator)} <span class="muted">${esc(n.group)} · JS ${fmt(n.js)}</span></span>`).join('')}</div>`;
  if(g.monthly && g.monthly.length){
    const months = g.monthly.map(m=>m.month+(m.partial?'*':''));
    h += `<h3>Monthly drift (${months[0]} to ${months[months.length-1]}; * = 1-14 Sept only)</h3><div class="small muted">titles per month: ${g.monthly.map(m=>m.n_titles).join(' · ')}</div>`;
    for(const f of Object.keys(D.factors)) h += `<div class="sparkrow"><span><b>${f}</b> <span class="muted small">${esc(D.factors[f].name)}</span></span>${spark(g.monthly.map(m=>m[f]),months,GROUP_COLORS[c.group]||'#999')}<span class="num small">${fmt(g.monthly[g.monthly.length-1][f])}</span></div>`;
    for(const k of D.hooks) h += `<div class="sparkrow"><span>${k}</span>${spark(g.monthly.map(m=>m[k]),months,'#718096')}<span class="num small">${fmtPct(g.monthly[g.monthly.length-1][k])}</span></div>`;
  }
  if(g.engagement){
    h += `<h3>Engagement within creator (n = ${g.engagement_n}, R² = ${fmt(g.engagement_r2)}; log views per within-creator SD; month + topic controls, HC3)</h3><table><tr><th>predictor</th><th class="num">coef</th><th class="num">se</th><th class="num">p</th></tr>${g.engagement.map(e=>`<tr><td>${esc(e.predictor)}${D.factors[e.predictor]?' <span class="muted">'+esc(D.factors[e.predictor].name)+'</span>':''}</td><td class="num">${fmt(e.coef_per_sd,3)}</td><td class="num">${fmt(e.se,3)}</td><td class="num">${e.p==null?'':e.p<0.001?'<0.001':fmt(e.p,3)}</td></tr>`).join('')}</table>`;
  } else h += `<h3>Engagement</h3><p class="muted">fewer than 100 titles with view counts: not estimated (Rumble has no view counts).</p>`;
  if(g.hits) h += `<h3>Hit concentration</h3><p>Gini ${fmt(g.hits.gini)} · top-10% share ${fmtPct(g.hits.top10_share)} · top-1% share ${fmtPct(g.hits.top1_share)} · power-law tail ${g.hits.powerlaw_like?'<b>supported</b>':'not supported'} vs lognormal (LR ${fmt(g.hits.lr_vs_lognormal)}, p ${fmt(g.hits.lr_p,3)}; alpha ${fmt(g.hits.alpha)}, xmin ${g.hits.xmin})</p>`;
  if(g.arousal) h += `<h3>Arousal index</h3><p><b>${fmt(g.arousal.index)}</b> (rank ${g.arousal.rank!=null?Math.round(g.arousal.rank):'n/a'} in ${genre}; percentile ${fmt(g.arousal.percentile,0)}) · ALL-CAPS word share ${fmtPct(g.arousal.caps_share)} · ${fmt(g.arousal.exclamations)} ! per title · ${fmt(g.arousal.power_words)} power words per title · ${fmt(g.arousal.emoji)} emoji per title · VADER intensity ${fmt(g.arousal.vader_intensity)}</p>`;
  if(g.caps_profile) h += `<h3>Capitalisation profile</h3><table>${Object.entries({'ALL CAPS':g.caps_profile.all_caps,'selective CAPS':g.caps_profile.selective_caps,'Title Case':g.caps_profile.title_case,'Sentence case':g.caps_profile.sentence_case,'mixed / other':g.caps_profile.mixed_other,'short / other':g.caps_profile.short_other}).map(([k,v])=>`<tr><td>${k}</td><td class="num">${fmtPct(v)}</td><td style="width:40%">${bar(100*v)}</td></tr>`).join('')}</table>`;
  if(c.signature_keywords&&c.signature_keywords.length) h += `<h3>Signature keywords (weighted log-odds vs all other channels; both genres)</h3><div>${c.signature_keywords.map(k=>`<span class="chip" title="z ${fmt(k.z,1)}, used ${k.count} times">${esc(k.word)} <span class="muted">${fmt(k.z,0)}</span></span>`).join('')}</div>`;
  if(c.leaning&&c.leaning.composition) h += `<h3>Political leaning from titles (${c.leaning.n_titles} sampled titles)</h3><table>${Object.entries(c.leaning.composition).map(([m,v])=>`<tr><td>${esc(m)}${m===c.leaning.judge?' <span class="muted">(judge of record)</span>':''}</td><td style="width:55%"><div class="bar" style="background:transparent;display:flex;overflow:hidden;border-radius:5px"><i style="position:static;width:${100*v.left}%;background:#2a78d6;height:10px"></i><i style="position:static;width:${100*v.neither}%;background:#d6d5d0;height:10px"></i><i style="position:static;width:${100*v.right}%;background:#eb6834;height:10px"></i></div></td><td class="num small">${fmtPct(v.left)} L · ${fmtPct(v.neither)} N · ${fmtPct(v.right)} R · score ${v.score>0?'+':''}${fmt(v.score)}</td></tr>`).join('')}</table>`;
  else if(c.leaning) h += `<h3>Political leaning from titles (${c.leaning.n_titles} sampled titles, two models)</h3><p>judge of record ${esc(c.leaning.judge)}: score <b>${c.leaning.judge_score>0?'+':''}${fmt(c.leaning.judge_score)}</b> (−1 = every title reads left, +1 = every title reads right) → <b>${esc(c.leaning.judge_side)}</b> · ${Object.entries(c.leaning).filter(([k])=>!['mean_score','implied_side','n_titles','consensus_neither','judge','judge_score','judge_side'].includes(k)).map(([k,v])=>`${esc(k)} ${fmt(v)}`).join(' · ')} · mean of models ${fmt(c.leaning.mean_score)} · both say 'neither' on ${fmtPct(c.leaning.consensus_neither)} of agreed titles</p>`;
  if(g.diversity) h += `<h3>Lexical diversity</h3><p>Heaps' β (1,500 tokens) ${fmt(g.diversity.heaps_beta_1500,3)} · Zipf ${fmt(g.diversity.zipf_1500,3)} · formulaic titles ${fmt(g.diversity.formulaic_p100,1)} per 100 · mean length ${fmt(g.diversity.n_tokens_mean,1)} tokens / ${fmt(g.diversity.n_chars_mean,0)} chars</p>`;
  $('#card').innerHTML = h;
  document.querySelectorAll('#card .chip[data-c]').forEach(el=>el.onclick=()=>select(el.dataset.c));
}
function groupMedianPct(f, grp){
  // percentile of the channel group's median among ranked creators of this genre
  const vals = creators.map(c=>D.creators[c].genres[genre]).filter(g=>g&&g.dimensions&&!g.low_n).map(g=>g.dimensions[f].controlled).filter(v=>v!=null).sort((a,b)=>a-b);
  const med = (D.group_medians[grp+'|'+genre]||{})[f]; if(med==null||!vals.length) return null;
  let k=0; while(k<vals.length&&vals[k]<=med)k++; return 100*k/vals.length;
}
function renderMap(kind){
  const pts = (D.maps[kind][genre]||[]); const svg = $('#map-'+kind);
  if(!pts.length){ svg.innerHTML=''; return; }
  const W=560,H=420,pad=28; const xs=pts.map(p=>p.x),ys=pts.map(p=>p.y);
  const x0=Math.min(...xs),x1=Math.max(...xs),y0=Math.min(...ys),y1=Math.max(...ys);
  const sx=x=>pad+(x-x0)/((x1-x0)||1)*(W-2*pad), sy=y=>H-pad-(y-y0)/((y1-y0)||1)*(H-2*pad);
  const me = D.creators[current], g = me.genres[genre];
  const nn = new Set(kind==='style' ? (g&&g.neighbours_style||[]).map(n=>n.creator) : (g&&g.neighbours_topic||[]).map(n=>n.creator));
  let s = `<rect width="${W}" height="${H}" fill="transparent"/>`;
  const mine = pts.find(p=>p.creator===current);
  if(mine) pts.filter(p=>nn.has(p.creator)).forEach(p=>{ s+=`<line x1="${sx(mine.x)}" y1="${sy(mine.y)}" x2="${sx(p.x)}" y2="${sy(p.y)}" stroke="var(--fg)" stroke-opacity=".35"/>`; });
  pts.forEach(p=>{ const sel=p.creator===current; s+=`<circle cx="${sx(p.x).toFixed(1)}" cy="${sy(p.y).toFixed(1)}" r="${sel?7:(nn.has(p.creator)?5:3.5)}" fill="${GROUP_COLORS[p.group]||'#999'}" fill-opacity="${sel||nn.has(p.creator)?1:.6}" stroke="${sel?'var(--fg)':'none'}" stroke-width="2" data-c="${esc(p.creator)}" data-l="${esc(GROUP_LABEL[p.group]||p.group)}"/>`; });
  if(mine) s+=`<text class="lbl" x="${sx(mine.x)+9}" y="${sy(mine.y)+4}">${esc(current)}</text>`;
  pts.filter(p=>nn.has(p.creator)).forEach(p=>{ s+=`<text class="lbl" x="${sx(p.x)+7}" y="${sy(p.y)+3}" opacity=".8">${esc(p.creator)}</text>`; });
  svg.setAttribute('viewBox',`0 0 ${W} ${H}`); svg.innerHTML=s;
  svg.querySelectorAll('circle').forEach(el=>{ el.onclick=()=>select(el.dataset.c); el.onmousemove=e=>{const t=$('#tip'); t.style.display='block'; t.style.left=(e.clientX+12)+'px'; t.style.top=(e.clientY+12)+'px'; t.textContent=el.dataset.c+' · '+el.dataset.l;}; el.onmouseleave=()=>$('#tip').style.display='none'; });
}
function select(c){ if(!D.creators[c]) return; current=c; $('#creator').value=c; renderAll(); }
let sortKey='creator', sortDir=1, groupFilter='', textFilter='';
function pcColor(p){ // percentile 0-100 -> blue (low) .. grey .. red (high), text stays ink
  if(p==null) return 'transparent'; const t=(p-50)/50; const a=Math.min(1,Math.abs(t))*0.55;
  return t<0?`rgba(42,120,214,${a})`:`rgba(230,103,103,${a})`; }
function rowsAll(){
  const F=Object.keys(D.factors);
  return creators.map(c=>{ const k=D.creators[c], g=k.genres[genre]; if(!g) return null;
    const r={creator:c, name:k.channel_name, group:k.group, organisation:k.organisation, clipper:k.clipper, n_unique:g.n_unique, low_n:g.low_n, political:g.political_share,
      outrage:g.hooks?g.hooks.outrage.share:null, question:g.formats?g.formats.question.share:null, gini:g.hits?g.hits.gini:null, top10:g.hits?g.hits.top10_share:null, cluster:g.style_cluster,
      arousal:g.arousal?g.arousal.index:null, caps:g.caps_profile?(g.caps_profile.all_caps+g.caps_profile.selective_caps):null, leaning:k.leaning?(k.leaning.judge_score!=null?k.leaning.judge_score:k.leaning.mean_score):null};
    F.forEach(f=>r[f]=g.dimensions?g.dimensions[f].pct_controlled:null); return r; }).filter(Boolean);
}
function renderAllTable(){
  const F=Object.keys(D.factors); let rows=rowsAll();
  if(groupFilter) rows=rows.filter(r=>r.group===groupFilter);
  if(textFilter) rows=rows.filter(r=>(r.creator+' '+r.name+' '+r.organisation).toLowerCase().includes(textFilter));
  rows.sort((a,b)=>{ const x=a[sortKey],y=b[sortKey]; if(x==null&&y==null)return 0; if(x==null)return 1; if(y==null)return -1; return (typeof x==='string'? x.localeCompare(y) : x-y)*sortDir; });
  const cols=[['creator','creator'],['group','group'],['n_unique','titles'],['political','political'],['outrage','outrage'],['arousal','arousal'],['caps','CAPS'],['leaning','leaning'],['question','question'],['gini','Gini'],['top10','top 10%'],['cluster','style cl.']].concat(F.map(f=>[f,f]));
  let h=`<tr>${cols.map(([k,l])=>`<th data-k="${k}" class="${k===sortKey?'sorted':''}" title="${D.factors[k]?esc(D.factors[k].name):''}">${esc(l)}${k===sortKey?(sortDir>0?' ▲':' ▼'):''}</th>`).join('')}</tr>`;
  for(const r of rows){
    h+=`<tr class="${r.creator===current?'sel':''}"><td class="name" data-c="${esc(r.creator)}" title="${esc(r.name)}${r.clipper?' (clipper)':''}">${esc(r.creator)}${r.low_n?' <span class="muted" title="low-n: fewer than 50 titles, not ranked">·</span>':''}</td>`;
    h+=`<td><span style="color:${GROUP_COLORS[r.group]||'#999'}">●</span> ${esc(r.group)}</td><td class="num">${r.n_unique.toLocaleString()}</td><td class="num">${fmtPct(r.political)}</td><td class="num">${fmtPct(r.outrage)}</td><td class="num">${fmt(r.arousal)}</td><td class="num">${fmtPct(r.caps)}</td><td class="num">${r.leaning==null?'':(r.leaning>0?'+':'')+fmt(r.leaning)}</td><td class="num">${fmtPct(r.question)}</td><td class="num">${fmt(r.gini)}</td><td class="num">${fmtPct(r.top10)}</td><td class="num">${r.cluster==null?'':'S'+r.cluster}</td>`;
    h+=F.map(f=>`<td class="pc" style="background:${pcColor(r[f])}">${r[f]==null?'':Math.round(r[f])}</td>`).join('')+'</tr>';
  }
  $('#alltable').innerHTML=h; $('#allcount').textContent=`${rows.length} creators with ${genre} titles`;
  $('#alltable').querySelectorAll('th').forEach(th=>th.onclick=()=>{ const k=th.dataset.k; if(sortKey===k) sortDir=-sortDir; else { sortKey=k; sortDir=(k==='creator'||k==='group')?1:-1; } renderAllTable(); });
  $('#alltable').querySelectorAll('td.name').forEach(td=>td.onclick=()=>{ select(td.dataset.c); window.scrollTo({top:0,behavior:'smooth'}); });
}
function renderAll(){ renderCard(); renderMap('style'); renderMap('topic'); renderAllTable(); }
function init(){
  const sel=$('#creator'); creators.forEach(c=>{const o=document.createElement('option'); o.value=c; o.textContent=`${c} — ${D.creators[c].channel_name} [${D.creators[c].group}]`; sel.appendChild(o);});
  sel.value=current; sel.onchange=()=>select(sel.value);
  $('#search').oninput=e=>{ const q=e.target.value.toLowerCase(); const hit=creators.find(c=>c.toLowerCase().includes(q)||D.creators[c].channel_name.toLowerCase().includes(q)); if(hit) select(hit); };
  $('#genre').onchange=e=>{genre=e.target.value; renderAll();};
  $('#legend').innerHTML = D.groups.map(g=>`<span><i style="background:${GROUP_COLORS[g]}"></i>${esc(GROUP_LABEL[g]||g)}</span>`).join('') + ' <span class="muted small">(channel groups from the title-leaning score, document 14)</span>';
  const gf=$('#groupfilter'); D.groups.forEach(g=>{const o=document.createElement('option'); o.value=g; o.textContent=GROUP_LABEL[g]||g; gf.appendChild(o);});
  gf.onchange=e=>{groupFilter=e.target.value; renderAllTable();}; $('#allsearch').oninput=e=>{textFilter=e.target.value.toLowerCase(); renderAllTable();};
  $('#factors').innerHTML = Object.entries(D.factors).map(([f,v])=>`<tr><td><b>${f}</b></td><td>${esc(v.name)}</td><td class="muted small">${esc(v.auto)}</td></tr>`).join('');
  renderAll();
}
init();
"""


def _table_html(df: pd.DataFrame, cols: list, floatfmt: str = "{:.3f}") -> str:
    if df is None or df.empty:
        return "<p class='muted'>no rows</p>"
    d = df[[c for c in cols if c in df.columns]]
    def f(v):
        if isinstance(v, float):
            return "" if pd.isna(v) else floatfmt.format(v)
        return str(v).replace("&", "&amp;").replace("<", "&lt;")
    head = "<tr>" + "".join(f"<th>{c}</th>" for c in d.columns) + "</tr>"
    body = "".join("<tr>" + "".join(f"<td>{f(v)}</td>" for v in r) + "</tr>" for r in d.itertuples(index=False))
    return f"<table>{head}{body}</table>"


def render_html(cards: dict, comparison: pd.DataFrame, entities: pd.DataFrame, candidates: pd.DataFrame) -> str:
    data = json.dumps(cards, ensure_ascii=False).replace("</", "<\\/")
    n = len(cards["creators"])
    comp = _table_html(comparison, ["genre", "titles", "n_creators", "style_k", "style_silhouette", "topic_k", "topic_silhouette", "ari_style_vs_group", "ari_topic_vs_group", "ari_style_vs_topic"]) if comparison is not None else ""
    ents = _table_html(entities[entities["kind"] == "person"].head(15), ["entity", "n_titles_balanced", "n_creators", "share_by_group", "outrage_ratio"], "{:.2f}") if entities is not None else ""
    cand = _table_html(candidates, ["candidate", "best_factor", "creator_level_r", "verdict"]) if candidates is not None else ""
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Title Stylometry</title><style>{CSS}</style></head><body>
<h1>Title Stylometry: the political-media landscape, 2026-01-01 to 2026-09-14</h1>
<div class="muted">{n} creators · generated {cards['generated']} · every number comes from <code>data/titles/analysis/</code>; the Markdown report and methods appendix sit beside this file.</div>
<div class="controls"><label>Creator <select id="creator"></select></label><input id="search" placeholder="search handle or channel name" size="28"><label>Genre <select id="genre"><option value="videos">videos (edited uploads)</option><option value="streams">streams (live VODs)</option></select></label></div>
<div class="legend" id="legend"></div>
<div class="row"><div class="col card" id="card"></div>
<div class="col"><div class="card"><h2>Style space</h2><div class="muted small">PCA of topic-controlled factor scores (z-scored across ranked creators of the genre). Lines join the selected creator to its five nearest style neighbours; click a point to select it.</div><svg class="map" id="map-style"></svg></div>
<div class="card"><h2>Topic space</h2><div class="muted small">MDS of Jensen-Shannon distances between creators' topic mixes; lines join the selected creator to its five nearest topic neighbours.</div><svg class="map" id="map-topic"></svg></div></div></div>
<div class="card"><h2>All creators</h2><div class="muted small">One row per creator for the selected genre. arousal = 0-1 arousal index; CAPS = share of titles in ALL CAPS or with selective CAPS; leaning = title-leaning score of the judge-of-record model (−1 left … +1 right; document 14). Dimension columns are percentile ranks of the topic-controlled score among ranked creators (blue = low, red = high; hover a column header for the factor's name). Click a header to sort, a creator to open its card. A dot after the handle marks a low-n group (under 50 titles, shown but not ranked).</div>
<div class="controls"><label>Group <select id="groupfilter"><option value="">all groups</option></select></label><input id="allsearch" placeholder="filter by handle, name or organisation" size="34"><span class="muted small" id="allcount"></span></div>
<div class="allwrap"><table class="all" id="alltable"></table></div></div>
<div class="row"><div class="col card"><h2>Dimensions</h2><table><tr><th>factor</th><th>name</th><th>from loadings</th></tr><tbody id="factors"></tbody></table><h3>Candidate labels</h3>{cand}</div>
<div class="col card"><h2>Clusterings vs the channel groups (adjusted Rand index)</h2>{comp}<h3>Most-named people (creator-balanced)</h3>{ents}</div></div>
<div class="tip" id="tip"></div>
<script id="data" type="application/json">{data}</script>
<script>{JS}</script></body></html>"""
