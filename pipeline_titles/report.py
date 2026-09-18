"""Render the deliverables from the analysis tables:

    pipeline_titles/reports/README.md + 01..14_*.md      the sectioned write-up (one document per question)
    pipeline_titles/reports/all_tables.md                reference dump of every table in one file
    pipeline_titles/reports/methods_appendix.md          every preprocessing step, lists, loadings, validation, runtimes
    pipeline_titles/reports/cards/<creator>.md           one fixed-layout profile card per creator
    pipeline_titles/reports/title_stylometry.html        browsable page (creator selector, cards, landscape maps)

The headline findings are prose written from the numbers and kept in
pipeline_titles/reports/headlines.md; re-check them after a corpus refresh. Every
table in the report comes straight from data/titles/analysis/.

CLI:
    python -m pipeline_titles.report
"""

from __future__ import annotations

import argparse
import json
import re
from typing import Optional, Sequence

import numpy as np
import pandas as pd

from pipeline_titles import lexicons
from pipeline_titles.common import (
    ANALYSIS_DIR, GENRES, GROUPS, PROJECT_ROOT, REPORTS_DIR, RUNTIMES, STOPWORDS, creator_slug, load_creators, read_jsonl, stage_timer, utc_now,
)
from pipeline_titles.report_data import CARDS_JSON, FORMATS, HOOKS
from pipeline_titles.report_html import render_html

A = ANALYSIS_DIR


# --------------------------------------------------------------------------- #
def md_table(df: pd.DataFrame, cols: Optional[list] = None, floatfmt: str = "{:.3f}", max_rows: Optional[int] = None) -> str:
    if df is None or len(df) == 0:
        return "_(no rows)_\n"
    d = df if cols is None else df[[c for c in cols if c in df.columns]]
    if max_rows:
        d = d.head(max_rows)
    def fmt(v):
        if isinstance(v, (float, np.floating)):
            return "" if np.isnan(v) else floatfmt.format(v)
        if isinstance(v, (bool, np.bool_)):
            return "yes" if v else "no"
        s = str(v).replace("|", "\\|").replace("\n", " ")
        return s if len(s) <= 110 else s[:107] + "..."
    head = "| " + " | ".join(str(c) for c in d.columns) + " |\n|" + "|".join("---" for _ in d.columns) + "|\n"
    body = "".join("| " + " | ".join(fmt(v) for v in row) + " |\n" for row in d.itertuples(index=False))
    return head + body


def read(name: str) -> Optional[pd.DataFrame]:
    p = A / name
    if not p.exists() and (A / (name + ".gz")).exists():   # the large tables are stored gzipped
        p = A / (name + ".gz")
    return pd.read_csv(p) if p.exists() else None


def pct(x) -> str:
    return "" if x is None or (isinstance(x, float) and np.isnan(x)) else f"{100 * x:.1f}%"


# --------------------------------------------------------------------------- #
def corpus_report(cards: dict) -> str:
    out = [f"# Title Stylometry: all tables (reference dump), 2026-01-01 to 2026-09-14\n", f"_Generated {utc_now()} by `python -m pipeline_titles.report`. Every table below is read from `data/titles/analysis/`; the code is `pipeline_titles/`._\n"]
    summ = read("creator_genre_summary.csv")
    n_rows = int(summ["n_rows"].sum()); n_unique = int(summ["n_unique"].sum())
    out.append(f"Corpus: {n_rows:,} titles from {summ['creator'].nunique()} creators ({summ['n_unique'].sum():,} unique within creator x genre; "
               f"{int(summ.loc[summ.genre == 'videos', 'n_rows'].sum()):,} edited uploads, {int(summ.loc[summ.genre == 'streams', 'n_rows'].sum()):,} live-stream VODs; "
               f"{int(summ.loc[summ.platform == 'rumble', 'n_rows'].sum()):,} on Rumble). Genres are never pooled; a creator x genre with fewer than 50 unique titles is low-n and never ranked.\n")
    hl = REPORTS_DIR / "headlines.md"
    out.append("## Headline findings\n")
    out.append(hl.read_text(encoding="utf-8") if hl.exists() else "_headlines.md not written yet._\n")

    # ---- Stage 0 ----
    out.append("\n## Stage 0: corpus, normalisation, balance\n")
    g = summ.groupby("genre").agg(groups=("creator", "size"), rows=("n_rows", "sum"), unique=("n_unique", "sum"), balanced=("n_balanced", "sum"),
                                  low_n_groups=("low_n", "sum"), median_group_size=("n_unique", "median"), max_group_size=("n_unique", "max")).reset_index()
    out.append(md_table(g, floatfmt="{:.0f}"))
    out.append(f"\nVerbatim repeats within creator x genre: {n_rows - n_unique:,} rows ({(n_rows - n_unique) / n_rows:.1%}); they are collapsed for every style and topic computation and kept for volume, view and hit statistics. "
               f"Balanced subset (<= 2,500 unique titles per creator x genre, seed 20260914): {int(summ['n_balanced'].sum()):,} titles; it is used for every pooled fit (topic model, templates, corpus Zipf, LLM sample).\n")
    rep = summ.sort_values("repeat_share", ascending=False).head(8)
    out.append("\nHighest repeat shares (live-broadcast loops):\n\n" + md_table(rep, ["creator", "genre", "n_rows", "n_unique", "repeat_share"]))
    sp = read("stripped_patterns.csv")
    if sp is not None:
        out.append(f"\nBrand stripping: {sp.groupby(['creator', 'genre']).ngroups} creator x genre groups had at least one pattern above the 20 % rule ({len(sp)} patterns; full list in `stripped_patterns.csv`). The most frequent:\n\n")
        out.append(md_table(sp.sort_values("count", ascending=False).head(15), ["creator", "genre", "kind", "pattern", "count", "share", "example"]))
    z = read("zipf_check.csv")
    if z is not None:
        out.append("\nZipf check (does stripping remove the show-brand head?):\n\n" + md_table(z, ["level", "text", "max_rank", "zipf_exponent", "n_tokens", "n_types", "top_20"], floatfmt="{:.4f}"))
    creators = load_creators()
    gc = creators.groupby("group").agg(creators=("creator", "size"), clippers=("clipper", lambda s: int(s.astype(str).str.lower().eq("true").sum()))).reindex(list(GROUPS) + ["unscored"]).dropna().reset_index()
    out.append("\nChannel groups (left / neutral / right from each channel's title-leaning score, `leaning_by_creator.csv`; the only between-channel grouping in the report):\n\n" + md_table(gc, floatfmt="{:.0f}"))
    orgs = creators.groupby("organisation")["creator"].agg(list)
    orgs = orgs[orgs.map(len) > 1]
    out.append("\nOrganisations with more than one channel (`creators.csv`): " + "; ".join(f"**{o}** ({', '.join(c)})" for o, c in orgs.items()) + ".\n")
    out.append("\nClippers (titles written by fans or an editing team, kept as their own group): " + ", ".join(creators.loc[creators["clipper"].astype(str).str.lower().eq("true"), "creator"]) + ".\n")

    # ---- Stage 1 ----
    out.append("\n## Stage 1: topics\n")
    tl = read("topic_labels.csv")
    t1: dict = {}
    for r in read_jsonl(RUNTIMES):          # a --label-only re-run lacks the fit fields: keep them from the fit run
        if r["stage"] == "stage1_topics":
            t1.update(r)
    out.append(f"BERTopic on a {t1.get('fit_n', 0):,}-title creator-stratified sample (cap {t1.get('fit_cap', '?')} per creator x genre): HDBSCAN found {t1.get('hdbscan_topics', '?')} topics "
               f"({t1.get('outlier_share', float('nan')):.1%} outliers); every title was then assigned to its nearest topic centroid (agreement with HDBSCAN's own labels on cluster members {t1.get('centroid_hdbscan_agreement', float('nan')):.1%}; "
               f"{t1.get('weak_share', float('nan')):.1%} of titles are weak assignments below the 10th-percentile similarity). {int(tl['political'].sum())} of {len(tl)} topics are political; "
               f"{t1.get('political_share_of_unique_titles', float('nan')):.1%} of unique titles (raw pooled) fall in political topics.\n")
    pol = read("creator_political_share.csv")
    pl = pol[pol["n_unique"] >= 50].groupby(["group", "genre"]).agg(n_creators=("creator", "size"), mean_political_share=("political_share", "mean"), median_political_share=("political_share", "median")).reset_index()
    out.append("\nPolitical share by channel group (mean of creators, >= 50 unique titles):\n\n" + md_table(pl))
    bl = read("topic_by_group.csv"); bl = bl[bl["group"].isin(GROUPS)]
    tl2 = tl.copy()
    corpus_share = bl.groupby("topic_id")["mean_creator_share"].mean().rename("mean_group_share")
    tl2 = tl2.merge(corpus_share, on="topic_id").sort_values("mean_group_share", ascending=False)
    out.append("\nLargest topics (mean of group-level creator shares, i.e. creator-balanced):\n\n" + md_table(tl2.head(25), ["topic_id", "label", "political", "category", "mean_group_share", "n_unique_all", "n_creators", "top_terms", "example_1"], floatfmt="{:.4f}"))
    out.append("\nTopic share by channel group, top 5 per group (videos; mean of creator shares):\n\n")
    top_by_group = bl[bl["genre"] == "videos"].sort_values("mean_creator_share", ascending=False).groupby("group").head(5)
    out.append(md_table(top_by_group, ["group", "topic_id", "label", "political", "mean_creator_share", "raw_pooled_share", "n_creators"], floatfmt="{:.3f}"))
    spk = read("topic_spikes.csv")
    if spk is not None:
        out.append("\nMonthly spikes (creator-balanced share vs the topic's own nine-month mean; top 3 per month):\n\n")
        out.append(md_table(spk.sort_values(["month", "z_vs_own_months"], ascending=[True, False]).groupby("month").head(3), ["month", "label", "z_vs_own_months", "share_month", "share_mean_all_months", "top_entities", "example_1"], floatfmt="{:.3f}"))
    out.append("\nEntities most named per topic (top 15 topics): see `topic_labels.csv` columns `top_persons` / `top_orgs`.\n\n" + md_table(tl2.head(15), ["topic_id", "label", "top_persons", "top_orgs"]))

    # ---- Stage 2 ----
    out.append("\n## Stage 2: style dimensions\n")
    efa = json.loads((A / "efa_summary.json").read_text())
    names = json.loads((A / "factor_names.json").read_text())
    out.append(f"Exploratory factor analysis on {efa['n_cells']:,} creator x genre x month cells (>= {efa['min_cell']} unique titles) x {efa['n_features']} features "
               f"(dropped: {len(efa['dropped'])}, listed in the appendix). KMO = {efa['kmo_total']:.3f}; Bartlett chi2 = {efa['bartlett_chi2']:,.0f} (p = {efa['bartlett_p']:.2g}). "
               f"Parallel analysis retains {efa['parallel_analysis_factors']} factors (Kaiser: {efa['kaiser_factors']}); retained {efa['retained']} (minres, oblimin), "
               f"cumulative variance {efa['cumulative_variance']:.1%}. Scree data: `scree.csv` / `scree.png`.\n")
    load = pd.read_csv(A / "factor_loadings.csv").set_index("feature")
    fcols = [c for c in load.columns if re.fullmatch(r"F\d+", c)]
    out.append("\nRetained factors, named from their loadings (|loading| >= 0.4 shown; full table in the appendix):\n\n")
    rows = []
    for f in fcols:
        s = load[f].sort_values()
        hi = ", ".join(f"{k} ({v:+.2f})" for k, v in s[s >= 0.4].sort_values(ascending=False).items())
        lo = ", ".join(f"{k} ({v:+.2f})" for k, v in s[s <= -0.4].items())
        rows.append({"factor": f, "name": names[f].get("name") or names[f]["auto"], "variance": f"{efa['variance_explained'][fcols.index(f)]:.1%}", "positive loadings": hi, "negative loadings": lo})
    out.append(md_table(pd.DataFrame(rows)))
    if efa.get("factor_correlations"):
        fc = pd.DataFrame(efa["factor_correlations"], index=fcols, columns=fcols).reset_index().rename(columns={"index": "factor"})
        out.append("\nFactor correlations (oblimin):\n\n" + md_table(fc, floatfmt="{:.2f}"))
    cand = read("validation_candidates.csv")
    out.append("\nDo the factors map onto the candidate labels? (creator-level Spearman r between the LLM rating aggregated to creator x genre and the raw factor score; present >= 0.5, partial 0.3-0.5, absent < 0.3; 'merged' = two candidates land on the same factor):\n\n")
    out.append(md_table(cand, ["candidate", "best_factor", "factor_auto_name", "creator_level_r", "second_factor", "second_r", "verdict"]))
    vt = read("validation_title_level.csv"); vc = read("validation_creator_level.csv")
    piv = vc[vc["score"] == "raw"].pivot(index="llm", columns="factor", values="spearman_r").reset_index()
    out.append(f"\nLLM rating vs factor score, creator level (Spearman, n = {int(vc['n_groups'].iloc[0])} creator x genre groups with >= 5 rated titles):\n\n" + md_table(piv, floatfmt="{:.2f}"))
    piv = vt.pivot(index="llm", columns="factor", values="spearman_r").reset_index()
    out.append(f"\nLLM rating vs factor score, title level (Spearman, n = {int(vt['n'].iloc[0]):,} rated titles):\n\n" + md_table(piv, floatfmt="{:.2f}"))
    rt = read("validation_retest.csv")
    out.append(f"\nTest-retest reliability of the LLM rater (n = {int(rt['n'].iloc[0])} titles rated twice in re-shuffled batches, same model, temperature 0):\n\n" + md_table(rt))
    tc = read("topic_control_summary.csv")
    out.append("\nTopic control: share of variance in each factor score explained by topic (title level, balanced subset) and how much creator-level variance topic mix accounts for:\n\n" + md_table(tc))
    dims = read("dimensions.csv")
    ok = dims[~dims["low_n"]]
    for genre in GENRES:
        lm = ok[ok["genre"] == genre].groupby("group").agg(n=("creator", "size"), **{f: (f + "_controlled", "median") for f in fcols}).reset_index()
        out.append(f"\nChannel-group medians of topic-controlled scores, {genre} (non-low-n creators):\n\n" + md_table(lm, floatfmt="{:.2f}"))
    rows = []
    for f in fcols:
        sub = ok[ok["genre"] == "videos"].sort_values(f + "_controlled")
        rows.append({"factor": f, "name": names[f].get("name") or names[f]["auto"], "highest (videos)": ", ".join(sub.tail(5)["creator"][::-1]), "lowest (videos)": ", ".join(sub.head(5)["creator"])})
    out.append("\nCreators at the extremes of each topic-controlled dimension (videos):\n\n" + md_table(pd.DataFrame(rows)))
    sens = read("lexical_diversity_sensitivity.csv")
    if sens is not None:
        out.append("\nLexical diversity: Heaps' exponent and Zipf exponent on 20 subsamples per creator x genre; rank correlations across subsample sizes (sample-size sensitivity):\n\n" + md_table(sens))
        fcr = read("features_creator.csv")
        fq = fcr[(fcr["genre"] == "videos") & (~fcr["low_n"]) & fcr["heaps_beta_1500"].notna()].sort_values("heaps_beta_1500")
        out.append(f"\nHeaps' exponent at 1,500 tokens, videos (n = {len(fq)}): lowest (most repetitive vocabulary) {', '.join(fq.head(5)['creator'])}; highest {', '.join(fq.tail(5)['creator'][::-1])}. Mean {fq['heaps_beta_1500'].mean():.3f}, sd {fq['heaps_beta_1500'].std():.3f}.\n")

    # ---- Stage 3 ----
    out.append("\n## Stage 3: formats and hooks\n")
    hk = json.loads((A / "hook_classifier.json").read_text())
    rows = [{"hook": h, **{k: v for k, v in m.items() if k != "cv_f1_by_C"}} for h, m in hk["hooks"].items()]
    out.append(f"Hook classifier ({hk['model']}; features: {hk['features']}), trained on the LLM labels:\n\n" + md_table(pd.DataFrame(rows)))
    sh = read("format_hook_shares.csv")
    for genre in GENRES:
        ln = sh[(sh["level"] == "group_mean_of_creators") & (sh["genre"] == genre)]
        out.append(f"\nShare of titles per category, {genre} (mean of creator shares, non-low-n creators):\n\n" + md_table(ln, ["group", "n_creators"] + FORMATS + HOOKS, floatfmt="{:.2f}"))
    ag = read("format_agreement.csv")
    out.append("\nRule vs LLM format label on the rated sample (rule = regex on the raw title; LLM = single format label):\n\n" + md_table(ag[ag["category"].isin(FORMATS)], ["category", "n", "rule_positives", "llm_positives", "precision_rule_vs_llm", "recall_rule_vs_llm", "f1", "kappa", "agreement"]))
    ex = read("format_examples.csv")
    out.append("\nExamples (corpus-wide, three per category):\n\n" + md_table(ex[ex["scope"] == "corpus"], ["category", "creator", "title"]))

    # ---- Stage 4 ----
    out.append("\n## Stage 4: the landscape\n")
    cc = read("cluster_comparison.csv")
    out.append("Agglomerative clustering of creators in style space (topic-controlled factor scores, Ward) and topic space (Jensen-Shannon distance between topic mixes, average linkage), k by silhouette; adjusted Rand index against the channel groups and against each other. Run on all titles and on political titles only:\n\n")
    out.append(md_table(cc, ["genre", "titles", "n_creators", "n_groups", "style_k", "style_silhouette", "topic_k", "topic_silhouette", "ari_style_vs_group", "ari_topic_vs_group", "ari_style_vs_topic", "ari_style_vs_group_k_groups", "ari_topic_vs_group_k_groups", "ari_style_vs_topic_k_groups"]))
    coh = read("group_style_cohesion.csv")
    out.append("\nStyle cohesion per channel group (mean within-group vs between-group distance in z-scored style space; ratio < 1 = group-mates are closer than average):\n\n" + md_table(coh[(coh["titles"] == "all")].sort_values(["genre", "cohesion_ratio"]), ["genre", "group", "n_creators", "within_group_distance", "between_group_distance", "cohesion_ratio"]))
    dis = read("disagreements_group_style.csv")
    out.append("\nWhere channel group and style disagree (videos, all titles):\n\n" + md_table(dis[(dis["genre"] == "videos") & (dis["titles"] == "all")].sort_values(["kind", "largest_cluster_share"]), ["kind", "group", "n_creators", "n_style_clusters", "largest_cluster_share", "members"]))
    ent = read("entities_top.csv")
    out.append("\nWho gets named (creator-balanced titles; people keyed by surname, so 'Kirk' pools Charlie and Erika Kirk):\n\n" + md_table(ent[ent["kind"] == "person"], ["entity", "n_titles_balanced", "share_of_balanced_titles", "n_creators", "share_by_group", "outrage_share", "overall_outrage_share", "outrage_ratio"]))
    out.append("\n" + md_table(ent[ent["kind"] == "organisation"], ["entity", "n_titles_balanced", "share_of_balanced_titles", "n_creators", "share_by_group", "outrage_share", "overall_outrage_share", "outrage_ratio"]))
    st_all = read("shared_titles.csv"); tp = read("shared_templates.csv")
    st = st_all[~st_all["same_organisation_only"]]
    out.append(f"\nConvergent formulas: {len(st_all):,} distinct titles (case-insensitive) are used verbatim by two or more creators, {len(st):,} of them by creators from different organisations "
               f"(the rest are same-outlet cross-posts such as TYT / The Damage Report); of those {len(st):,}, {st['within_group'].mean():.1%} stay within one channel group. "
               f"{len(tp):,} masked templates (names and numbers replaced, at least one content word) are shared across organisations; {tp['within_group'].mean():.1%} within one channel group.\n\n")
    out.append(md_table(st.head(25), ["example", "n_creators", "n_titles", "groups", "creators"]))
    out.append("\n" + md_table(tp.head(25), ["template", "n_creators", "n_titles", "groups", "example"]))

    # ---- Stage 5 ----
    out.append("\n## Stage 5: time and engagement\n")
    tr = read("drift_trends.csv")
    strong = tr[(tr["level"] == "group") & (tr["p"] < 0.05) & (tr["spearman_trend"].abs() >= 0.6)].sort_values("spearman_trend")
    out.append(f"Monthly drift, January-September (September is 1-14 and never compared on volume). Channel-group trends with |Spearman| >= 0.6 and p < 0.05 over the nine months ({len(strong)} of {len(tr[tr['level'] == 'group'])} group x genre x measure series):\n\n")
    out.append(md_table(strong, ["group", "genre", "measure", "spearman_trend", "p", "first_month_value", "last_full_month_value"]))
    tcl = read("topic_change_group_monthly.csv")
    if tcl is not None:
        piv = tcl[tcl["genre"] == "videos"].pivot(index="group", columns="month_to", values="mean_js").reset_index()
        out.append("\nMonth-to-month topic change (mean Jensen-Shannon distance between a creator's consecutive monthly topic mixes; videos):\n\n" + md_table(piv, floatfmt="{:.2f}"))
    es = read("engagement_summary.csv")
    out.append("\nEngagement, within creator (OLS of log views on standardised title predictors with month and topic controls, HC3; views are a fetch-time snapshot that favours older videos):\n\n")
    out.append(md_table(es[es["group"] == "ALL"], ["genre", "predictor", "n_creators", "median_coef_per_sd", "q25", "q75", "share_positive", "share_sig_positive", "share_sig_negative", "share_same_sign_as_median", "median_r2"]))
    out.append("\nThe outrage effect by channel group (videos):\n\n" + md_table(es[(es["group"] != "ALL") & (es["genre"] == "videos") & (es["predictor"] == "outrage")], ["group", "n_creators", "median_coef_per_sd", "q25", "q75", "share_positive", "share_sig_positive", "share_sig_negative"]))
    hc = read("hit_concentration.csv")
    hs = hc.groupby("genre").agg(n_creators=("creator", "size"), median_gini=("gini", "median"), median_top10_share=("top10_share", "median"), median_top1_share=("top1_share", "median"), powerlaw_like=("powerlaw_like", "mean"), median_alpha=("alpha", "median")).reset_index()
    out.append("\nHit concentration (creator x genre with >= 100 videos carrying views):\n\n" + md_table(hs))
    hcc = read("hit_concentration_correlations.csv")
    pooled = hcc[hcc["scope"].str.startswith("pooled")]
    out.append("\nConcentration vs style, pooled within channel group (group-demeaned Spearman across creators):\n\n" + md_table(pooled.sort_values(["genre", "target", "predictor"]), ["genre", "target", "predictor", "n_creators", "spearman_r", "p"]))

    # ---- Stage 6b ----
    out.append("\n## Stage 6b: Zipf's law and views over time (document 7)\n")
    out.append("Zipf exponents per system (tokens with stopwords; OLS of log frequency on log rank; size-matched = 20 draws of 2,000 titles, top 200 ranks):\n\n" + md_table(read("zipf_words.csv"), ["grouping", "system", "n_titles", "n_tokens", "n_types", "tokens_per_title", "zipf_top100", "zipf_top1000", "zipf_top5000", "zipf_r2_top1000", "zipf_size_matched", "zipf_size_matched_sd", "top1_share", "top_10"], floatfmt="{:.4f}"))
    out.append("\nCreator-level Zipf / Heaps and the views rank-size slopes per channel group and per dominant capitalisation style:\n\n" + md_table(read("zipf_by_group.csv"), floatfmt="{:.3f}"))
    vm = read("views_by_month.csv")
    out.append("\nViews by publication month (edited uploads, YouTube, unique titles): median views, the median over channels of the channel's median, and log views relative to the same channel's mean that month:\n\n" + md_table(vm, ["grouping", "group", "month", "n_videos", "n_creators", "median_views", "creator_median_views", "mean_log_views", "relative_log_views", "relative_log_views_se"], floatfmt="{:.3f}"))
    out.append("\nCapitalisation style by channel group and by title label:\n\n" + md_table(read("caps_style_by_group.csv")))
    out.append("\nTitle label x capitalisation style (label shares within each style; relative log views per cell):\n\n" + md_table(read("label_by_caps_style.csv")))
    out.append("\n## Files\n\nMachine-readable interface tables: `features.csv`, `dimensions.csv`, `topics.csv`, `labels.csv`, `creators.csv`, `leaning_by_creator.csv` (all under `data/titles/analysis/`). Profile cards: `pipeline_titles/reports/cards/`. HTML: `pipeline_titles/reports/title_stylometry.html`. Methods: `methods_appendix.md`.\n")
    return "\n".join(out)


def methods_appendix() -> str:
    from pipeline_titles import annotate, creators, embed, engagement, factors, features, formats, hits, landscape, leaning, llm_rate, prepare, profiles, timeline, topics, zipf_views
    out = ["# Title Stylometry: methods appendix\n", f"_Generated {utc_now()}._\n"]
    out.append("## Pipeline stages (module docstrings, verbatim)\n")
    for mod in (prepare, creators, leaning, annotate, embed, topics, llm_rate, features, factors, formats, landscape, timeline, engagement, hits, profiles, zipf_views):
        out.append(f"### `{mod.__name__}`\n\n```\n{mod.__doc__.strip()}\n```\n")
    out.append("## Stopword list\n\n`" + "`, `".join(STOPWORDS) + "`\n")
    out.append("\n## Feature definitions\n\n" + md_table(read("feature_definitions.csv")))
    out.append("\n## Lexicons (pipeline_titles/lexicons.py)\n")
    for name in ["FIRST_SG", "FIRST_PL", "SECOND", "QUESTION_START", "IMPERATIVE_START", "INTENSIFIERS", "SUPERLATIVES", "SHOCK_WORDS", "POS_EVAL", "NEG_EVAL",
                 "NEGATION", "VIOLENCE_VERBS", "VIOLENCE_PHRASES", "HEDGES", "DISCOURSE", "HOWTO_PHRASES", "EXPLAINER_PHRASES", "CURIOSITY_PHRASES",
                 "FORWARD_REF_START", "REACTION_PHRASES", "INTERVIEW_PHRASES", "CONFRONTATION_PHRASES"]:
        vals = getattr(lexicons, name)
        out.append(f"- **{name}** ({len(vals)}): " + ", ".join(sorted(vals)) + "\n")
    out.append(f"- **LISTICLE_RE**: `{lexicons.LISTICLE_RE}`\n")
    out.append("\n## Format rules\n\n" + md_table(read("format_rules.csv")))
    efa = json.loads((A / "efa_summary.json").read_text())
    out.append("\n## Factor analysis\n\n" + f"Cells: {efa['n_cells']} (>= {efa['min_cell']} unique titles); features: {efa['n_features']}; KMO {efa['kmo_total']}; Bartlett chi2 {efa['bartlett_chi2']} p {efa['bartlett_p']:.3g}; parallel analysis {efa['parallel_analysis_factors']}, Kaiser {efa['kaiser_factors']}, retained {efa['retained']} ({efa['method']}, {efa['rotation']}); variance explained per factor {efa['variance_explained']}; cumulative {efa['cumulative_variance']}.\n")
    out.append("\nDropped features: " + "; ".join(f"`{k}` ({v})" for k, v in efa["dropped"].items()) + "\n")
    out.append("\nScree (eigenvalues vs parallel-analysis 95th percentile):\n\n" + md_table(read("scree.csv").head(20), floatfmt="{:.3f}"))
    out.append("\nFull loadings (oblimin; varimax beside):\n\n" + md_table(pd.read_csv(A / "factor_loadings.csv"), floatfmt="{:.2f}"))
    out.append("\n## Validation\n\n" + md_table(read("validation_candidates.csv")) + "\n" + md_table(read("validation_retest.csv")) + "\n" + md_table(read("validation_creator_level.csv"), floatfmt="{:.3f}"))
    out.append("\n## Hook classifier\n\n```\n" + (A / "hook_classifier.json").read_text() + "\n```\n")
    out.append("\n## LLM rating prompt (labels.csv; exact text)\n\n")
    lab = read("labels.csv").head(1)
    out.append(f"Model `{lab['model'].iloc[0]}`, temperature {lab['temperature'].iloc[0]}, prompt id `{lab['prompt_id'].iloc[0]}`, sha256 `{lab['prompt_sha256'].iloc[0]}`, rated {lab['rated_at'].iloc[0]}.\n\n```\n{lab['prompt'].iloc[0]}\n```\n")
    out.append("\n## Topic label prompt\n\n```\n" + topics.LABEL_PROMPT + "\n```\n")
    out.append("\n## Leaning label prompt (leaning_labels.csv; exact text, prompt id leaning-v1, temperature 0, batches of 20; the same prompt for every judge)\n\n```\n" + leaning.PROMPT + "\n```\n")
    out.append("\n## Zipf check\n\n" + md_table(read("zipf_check.csv"), floatfmt="{:.4f}"))
    out.append("\n## Sample sizes\n\n" + md_table(read("creator_genre_summary.csv"), ["creator", "genre", "n_rows", "n_unique", "n_balanced", "n_with_views", "repeat_share", "low_n"], floatfmt="{:.3f}"))
    runs = read_jsonl(RUNTIMES)
    last, longest = {}, {}
    for r in runs:
        last[r["stage"]] = r
        if r["stage"] not in longest or r["seconds"] >= longest[r["stage"]]["seconds"]:   # ties go to the newest run
            longest[r["stage"]] = r
    rows = [{"stage": k, "seconds_last_run": v["seconds"], "seconds_longest_run": longest[k]["seconds"], "finished": v["finished"],
             "llm_calls": v.get("calls", v.get("label_calls", "")), "output_tokens": v.get("output_tokens", v.get("label_output_tokens", "")),
             "api_cost_usd": v.get("api_cost_usd", 0 if "llm" in k or "topics" in k else ""),
             "notes": ", ".join(f"{a}={b}" for a, b in longest[k].items() if a not in ("stage", "seconds", "started", "finished", "calls", "output_tokens", "prompt_tokens", "api_cost_usd") and not isinstance(b, (list, dict)))} for k, v in last.items()]
    out.append("\n## Runtime and cost per stage (last run and longest run of each; a --label-only re-run of topics is seconds, the fit was minutes; local Ollama models cost $0)\n\n" + md_table(pd.DataFrame(rows), floatfmt="{:.1f}"))
    out.append("\n## Environment\n\n```\n" + (PROJECT_ROOT / "requirements.txt").read_text() + "\n```\n")
    return "\n".join(out)


def card_md(card: dict, factors: dict) -> str:
    o = [f"# {card['channel_name']} ({card['creator']})\n",
         f"Channel group: **{card['group']}** (title-leaning score, document 14) · organisation: {card['organisation']} · clipper: {'yes' if card['clipper'] else 'no'} · platform: {card['platform']} · subscribers: {card['subscribers'] if card['subscribers'] is not None else 'n/a'}\n"]
    for genre, g in card["genres"].items():
        o.append(f"\n## {genre}\n")
        o.append(f"Titles: {g['n_rows']:,} rows, {g['n_unique']:,} unique (repeat share {pct(g['repeat_share'])}); {'LOW-N (not ranked)' if g['low_n'] else 'ranked'}; political share {pct(g.get('political_share'))}.\n")
        o.append("\nTop topics: " + "; ".join(f"{t['label']} ({pct(t['share'])})" for t in g["topics_top5"]) + "\n")
        if "dimensions" in g:
            rows = [{"dimension": f"{f}: {factors[f]['name']}", "percentile (topic-controlled)": d["pct_controlled"], "percentile (raw)": d["pct_raw"], "score": d["controlled"], "group median": d["group_median"]} for f, d in g["dimensions"].items()]
            o.append("\n" + md_table(pd.DataFrame(rows), floatfmt="{:.1f}"))
        if "hooks" in g:
            o.append("\nHooks / formats (share of titles; channel-group mean in brackets): " + "; ".join(f"{k} {pct(v['share'])} ({pct(v['group_mean'])})" for k, v in {**g['hooks'], **g['formats']}.items()) + "\n")
        if g.get("neighbours_style"):
            o.append("\nNearest style neighbours: " + "; ".join(f"{n['creator']} [{n['group']}]" for n in g["neighbours_style"]) + "\n")
        if g.get("neighbours_topic"):
            o.append("Nearest topic neighbours: " + "; ".join(f"{n['creator']} [{n['group']}]" for n in g["neighbours_topic"]) + "\n")
        if g.get("monthly"):
            fk = list(factors)
            rows = [{"month": m["month"] + ("*" if m["partial"] else ""), "n": m["n_titles"], **{f: m.get(f) for f in fk}, **{h: m.get(h) for h in HOOKS}} for m in g["monthly"]]
            o.append("\nMonthly drift (topic-controlled scores and hook shares; * = partial month):\n\n" + md_table(pd.DataFrame(rows), floatfmt="{:.2f}"))
        if g.get("engagement"):
            o.append(f"\nEngagement (n = {g['engagement_n']}, R2 = {g['engagement_r2']}; log views per within-creator SD, month + topic controls):\n\n" + md_table(pd.DataFrame(g["engagement"]), floatfmt="{:.3f}"))
        else:
            o.append("\nEngagement: n < 100 titles with views, not estimated.\n")
        if g.get("hits"):
            h = g["hits"]
            o.append(f"\nHit concentration: Gini {h['gini']}, top-10 % share {pct(h['top10_share'])}, power-law tail {'supported' if h['powerlaw_like'] else 'not supported'} vs lognormal (LR = {h['lr_vs_lognormal']}, p = {h['lr_p']}).\n")
        if g.get("diversity"):
            d = g["diversity"]
            o.append(f"\nLexical diversity: Heaps' beta (1,500 tokens) {d['heaps_beta_1500']}, Zipf {d['zipf_1500']}, formulaic titles {d['formulaic_p100']} per 100, mean length {d['n_tokens_mean']} tokens.\n")
    return "\n".join(o)


def main(argv: Optional[Sequence[str]] = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.parse_args(argv)
    with stage_timer("report") as info:
        cards = json.loads(CARDS_JSON.read_text())
        REPORTS_DIR.mkdir(parents=True, exist_ok=True)
        (REPORTS_DIR / "all_tables.md").write_text(corpus_report(cards), encoding="utf-8")
        from pipeline_titles.figures import main as figures_main
        figures_main()
        from pipeline_titles.report_sections import write_all
        write_all()
        (REPORTS_DIR / "methods_appendix.md").write_text(methods_appendix(), encoding="utf-8")
        cdir = REPORTS_DIR / "cards"
        cdir.mkdir(exist_ok=True)
        for creator, card in cards["creators"].items():
            (cdir / f"{creator_slug(creator)}.md").write_text(card_md(card, cards["factors"]), encoding="utf-8")
        html = render_html(cards, read("cluster_comparison.csv"), read("entities_top.csv"), read("validation_candidates.csv"))
        (REPORTS_DIR / "title_stylometry.html").write_text(html, encoding="utf-8")
        info["cards"] = len(cards["creators"])
        print(f"report written: {REPORTS_DIR}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
