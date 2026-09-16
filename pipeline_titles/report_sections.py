"""Sectioned write-up: one document per question, each with the finding explained
in prose, the few tables that carry it, and its caveats. Written by
pipeline_titles.report alongside the reference dump (all_tables.md).

    reports/README.md                    index and how to read the set
    reports/01_corpus_and_lanes.md       what the corpus is, what was normalised, the lanes
    reports/02_topics.md                 what they talk about
    reports/03_style_dimensions.md       the twelve style dimensions and what they mean
    reports/04_formats_and_hooks.md      question / LIVE / episode formats; outrage, curiosity, humour
    reports/05_landscape.md              who titles like whom; lanes vs style; who gets named; shared titles
    reports/06_drift.md                  month-by-month change
    reports/07_views.md                  does style predict views; hit concentration
    reports/08_null_results_and_caveats.md   what did not show up, and what to distrust

The interpretive prose reflects the 2026-09-14 run; every number in it is read from
the tables at render time, so a re-run keeps the numbers current but the wording
should be re-checked.
"""

from __future__ import annotations

import json
import re

import numpy as np
import pandas as pd

from pipeline_titles.common import ANALYSIS_DIR as A, GENRES, REPORTS_DIR, read_jsonl, RUNTIMES

HOOKS = ["curiosity_gap", "outrage", "humor"]
FORMATS = ["question", "breaking_live", "episode_show", "interview_guest", "reaction", "confrontation", "listicle", "howto_explainer"]
LANE_LABEL = {
    "left_commentary": "left commentary", "right_commentary": "right commentary", "centrist_heterodox": "centrist / heterodox",
    "us_legacy_tv": "US legacy TV", "right_tv_network": "right TV networks", "wire_international": "wires & international",
    "us_press_print_digital": "US press", "independent_digital_news": "independent digital news", "streamer_reaction": "streamers",
    "interview_podcast": "interview podcasts", "legal_institutional": "legal commentary", "humour_satire": "humour / satire",
    "explainer_geopolitics": "explainers / geopolitics",
}


def lane(l: str) -> str:
    return LANE_LABEL.get(l, l)


def rd(name: str) -> pd.DataFrame:
    p = A / name
    return pd.read_csv(p if p.exists() or not (A / (name + ".gz")).exists() else A / (name + ".gz"))   # the large tables are stored gzipped


def table(df: pd.DataFrame, cols=None, fmt="{:.2f}", rename=None, max_rows=None) -> str:
    if df is None or len(df) == 0:
        return "_(no rows)_\n"
    d = df if cols is None else df[[c for c in cols if c in df.columns]]
    if max_rows:
        d = d.head(max_rows)
    if rename:
        d = d.rename(columns=rename)

    def f(v):
        if isinstance(v, (float, np.floating)):
            return "" if np.isnan(v) else fmt.format(v)
        if isinstance(v, (bool, np.bool_)):
            return "yes" if v else "no"
        s = str(v).replace("|", "\\|").replace("\n", " ")
        return s if len(s) <= 120 else s[:117] + "..."
    head = "| " + " | ".join(str(c) for c in d.columns) + " |\n|" + "|".join("---" for _ in d.columns) + "|\n"
    return head + "".join("| " + " | ".join(f(v) for v in row) + " |\n" for row in d.itertuples(index=False))


def pct(x, d=0) -> str:
    return f"{100 * x:.{d}f} %"


def names_of() -> dict:
    n = json.loads((A / "factor_names.json").read_text())
    return {k: (v.get("name") or v["auto"]) for k, v in n.items()}


def short_name(f: str, names: dict) -> str:
    return names[f].split(" (")[0]


# --------------------------------------------------------------------------- #
def doc_corpus() -> str:
    summ = rd("creator_genre_summary.csv"); lanes = rd("lanes.csv"); sp = rd("stripped_patterns.csv"); z = rd("zipf_check.csv")
    n_rows, n_uniq = int(summ.n_rows.sum()), int(summ.n_unique.sum())
    top4 = summ[summ.creator.isin(["@Firstpost", "@ANINewsIndia", "@TimesNowWorld", "@timesofindia"])].n_rows.sum()
    g = summ.groupby("genre").agg(groups=("creator", "size"), rows=("n_rows", "sum"), unique=("n_unique", "sum"), balanced=("n_balanced", "sum"),
                                  low_n=("low_n", "sum"), median_size=("n_unique", "median"), max_size=("n_unique", "max")).reset_index()
    zc = z[z.level == "creator_level_mean"].set_index("text").zipf_exponent
    lc = lanes.groupby("lane").agg(creators=("creator", "size"), clippers=("clipper", lambda s: int(s.astype(str).str.lower().eq("true").sum()))).reset_index()
    lc["lane"] = lc["lane"].map(lane)
    out = f"""# 1. The corpus, what was normalised, and the lanes

**The question.** What exactly is being analysed, and what had to be done to it before any style measure means anything?

## The finding in one paragraph

The corpus is {n_rows:,} titles from {summ.creator.nunique()} creators, but it is wildly uneven: four Indian news channels (Firstpost, ANI, Times Now, Times of India) hold {top4:,} of them, the median creator x genre has {int(summ.n_unique.median())} titles and the largest has {int(summ.n_unique.max()):,}. {n_rows - n_uniq:,} rows ({pct((n_rows - n_uniq) / n_rows, 1)}) are verbatim repeats within a creator x genre, almost all live-broadcast loops on news stream tabs. So three rules run through everything downstream: edited uploads (`videos`) and live VODs (`streams`) are never pooled; a creator x genre with fewer than 50 unique titles is reported but never ranked ({int(summ.low_n.sum())} of {len(summ)} groups); and any statistic that pools titles uses a creator-balanced subset capped at 2,500 titles per creator x genre ({int(summ.n_balanced.sum()):,} titles), while corpus- and lane-level figures are means of creator-level values.

## Size by genre

![Unique titles and creators per lane. A few news lanes hold most titles; commentary holds most creators.](figures/01_corpus_by_lane.png)
*Unique titles and creators per lane. A few news lanes hold most titles; commentary holds most creators.*

{table(g, fmt="{:.0f}")}

The `streams` genre is small and thin: {int(g.loc[g.genre == 'streams', 'low_n'].iloc[0])} of its {int(g.loc[g.genre == 'streams', 'groups'].iloc[0])} groups are low-n, so stream-level results in the later documents rest on roughly {int(g.loc[g.genre == 'streams', 'groups'].iloc[0]) - int(g.loc[g.genre == 'streams', 'low_n'].iloc[0])} creators.

![Creator x genre group sizes on a log scale, with the low-n line (50) and the balanced cap (2,500).](figures/01_group_sizes.png)
*Creator x genre group sizes on a log scale, with the low-n line (50) and the balanced cap (2,500).*

## What was stripped from titles, and why it matters

Titles carry brand furniture that would otherwise dominate any vocabulary-based measure: "| BBC News" on {int(sp[(sp.creator == '@BBCNews') & (sp.kind == 'suffix')]['count'].max()):,} BBC titles, "Ep. 1837"-style episode numbers on the Daily Wire shows, date stamps on RSBN and Newsmax streams, "N18G" on Firstpost. The rule was mechanical and per creator: any delimited leading or trailing segment (or colon label, bracket tag, hashtag) that occurs in more than 20 % of that creator's titles is a brand pattern and is removed; episode numbers and date stamps are removed from the edges regardless. Generic format labels (LIVE, BREAKING, WATCH) are never stripped because they are themselves a style choice measured later. {len(sp)} patterns were stripped across {sp.groupby(['creator', 'genre']).ngroups} creator x genre groups; {int((rd('creator_genre_summary.csv').n_norm_fallback).sum())} titles consisted of nothing but brand text and were kept as they were. The full list is `stripped_patterns.csv`; the fifteen most frequent:

{table(sp.sort_values('count', ascending=False).head(15), ['creator', 'genre', 'kind', 'pattern', 'count', 'share', 'example'], fmt='{:.2f}')}

**Check that it worked.** If stripping removed the show-brand head of each creator's vocabulary, the creator-level Zipf exponent should fall (the most frequent tokens were the brand) and the top-token share should drop most for show-branded channels. Both happened: the mean creator-level Zipf exponent went from {zc['raw']:.3f} (raw) to {zc['normalised']:.3f} (normalised), and the share of the single most frequent token fell most for Joe Rogan (from 14 % to 4 %: "Joe Rogan Experience #"), Denims, The Economist and the Hasan fan channels. The pooled corpus exponent barely moves (the brand tokens are a small share of a 189k-title pool), which is exactly why the report uses creator-level figures.

## Lanes: a proposal, not a fact

Every between-group comparison uses a lane assignment made from channel names, descriptions and a sample of titles. It is a proposal for correction (`lanes.csv`, column `status = proposed`): the nine lanes asked for plus four the corpus needed (right TV networks; US print/digital press as distinct from wires; centrist/heterodox; explainers/geopolitics).

{table(lc, fmt='{:.0f}')}

`organisation` groups sister channels of one outlet (Fox News / Fox News Clips, Timcast x3, NYT x4 incl. Ezra Klein, TYT / The Damage Report / Rebel HQ, MeidasTouch / Legal AF / Katie Phang / Michael Cohen, Daily Wire x4, Blaze Media x2, and so on: {int((lanes.groupby('organisation').size() > 1).sum())} organisations with more than one channel). `clipper` marks the {int(lanes.clipper.astype(str).str.lower().eq('true').sum())} channels whose titles are written by fans or an editing team (the Hasan, Destiny and Vaush clip channels, Fox News Clips, Lauren Chen Clips, Candace Clips, Denims, Asmongold TV, the Hasan VOD channel); they are kept as their own group so a fan editor's style is never attributed to the creator. Same-organisation cross-posts (TYT and The Damage Report share 913 titles verbatim) are removed from every similarity calculation.

**Lane-dependent results** (lane medians, lane cohesion, ARI against lanes, lane-level drift, within-lane correlations) will change when the CSV is corrected; re-run from `factors`.

Files: `creator_genre_summary.csv`, `stripped_patterns.csv`, `zipf_check.csv`, `zipf_check_creators.csv`, `lanes.csv`.
"""
    return out


def doc_topics() -> str:
    tl = rd("topic_labels.csv"); bl = rd("topic_by_lane.csv"); spk = rd("topic_spikes.csv"); pol = rd("creator_political_share.csv"); cc = rd("cluster_comparison.csv")
    t1 = {}
    for r in read_jsonl(RUNTIMES):
        if r["stage"] == "stage1_topics":
            t1.update(r)
    share = bl.groupby("topic_id")["mean_creator_share"].mean().rename("balanced_share")
    tl2 = tl.merge(share, on="topic_id").sort_values("balanced_share", ascending=False)
    big = tl2.head(12)
    pl = pol[pol.n_unique >= 50].groupby("lane").political_share.mean().sort_values()
    v = bl[bl.genre == "videos"].sort_values("mean_creator_share", ascending=False).groupby("lane").head(3)
    v = v.assign(lane=v.lane.map(lane))
    sp3 = spk.sort_values(["month", "z_vs_own_months"], ascending=[True, False]).groupby("month").head(2)
    ari = cc[(cc.genre == "videos") & (cc.titles == "all")].iloc[0]
    out = f"""# 2. Topics: what they talk about

**The question.** What stories fill the titles, who covers what, and how much of the corpus is politics at all? The topic assignment is also the control variable for every style result, so it has to be sound.

## The finding in one paragraph

A BERTopic model fitted on a {t1.get('fit_n', 0):,}-title creator-stratified sample found {t1.get('hdbscan_topics', '?')} topics; every title was then assigned to its nearest topic centroid ({t1.get('centroid_hdbscan_agreement', 0):.0%} agreement with HDBSCAN's own labels on cluster members, {t1.get('weak_share', 0):.0%} weak assignments). One story dominates 2026: the Iran war and the Strait of Hormuz, {int(tl.loc[tl.topic_id == 0, 'n_unique_all'].iloc[0]):,} unique titles across {int(tl.loc[tl.topic_id == 0, 'n_creators'].iloc[0])} of 274 creators, with a second energy-markets topic on the same war. The twelve largest topics are each shared by 130 or more creators. That is the central fact for everything after this document: the whole landscape covered the same stories, so raw vocabulary similarity between two channels mostly measures the news cycle, not their style. It also shows in the clustering: creators grouped by topic mix do not line up with lanes at all (adjusted Rand index {ari.ari_topic_vs_lane:.3f} for edited uploads).

## The largest topics (creator-balanced share)

![The fifteen largest topics by creator-balanced share; blue = political, yellow = non-political.](figures/02_top_topics.png)
*The fifteen largest topics by creator-balanced share; blue = political, yellow = non-political.*

{table(big, ['topic_id', 'label', 'political', 'balanced_share', 'n_unique_all', 'n_creators', 'top_terms'], fmt='{:.3f}')}

`balanced_share` is the mean over lanes of the mean creator share, so a topic that four Indian channels post 8,000 times does not outrank one that 200 channels each post a few times. The "Shocking Events and Reactions" topic is not a story: it is the cluster of content-free exclamations ("HOLY SH*T", "THIS IS INSANE..") that streamers and commentators use as titles, and it is the seed of the shared-title finding in document 5.

## Political or not

![Mean political share of a creator's titles, by lane.](figures/02_political_share_by_lane.png)
*Mean political share of a creator's titles, by lane.*

{int(tl.political.sum())} of {len(tl)} topics were tagged political by the labelling model (politics, government, elections, war, courts, political figures, the culture war); the {int((~tl.political).sum())} non-political topics are crime trials (Nancy Guthrie, Lindsay Clancy, the Brown University shooting), weather and disasters, sport (World Cup, MMA), tech and business, and a few channel-specific series. The tagging is generous, and the political share of a creator's unique titles is therefore high everywhere; it separates the lanes only at the bottom:

{table(pl.rename('mean political share').reset_index().assign(lane=lambda d: d.lane.map(lane)), fmt='{:.2f}')}

Document 5 repeats the whole landscape analysis on political titles only; the conclusions do not change.

## Topic share by lane (top 3 per lane, edited uploads)

{table(v, ['lane', 'label', 'mean_creator_share', 'n_creators'], fmt='{:.3f}')}

Read this as "where each lane's attention goes beyond the shared war story": legal commentary on the Supreme Court and DOJ topic, streamers on reactions and streamer drama, the US press on tech and AI, explainers on Israel-Palestine, right commentary on the "modern women and feminism" culture-war topic.

## The month-by-month story

![Monthly creator-balanced share of the eight largest topics; the hollow marker is the half month of September.](figures/02_topic_timeline.png)
*Monthly creator-balanced share of the eight largest topics; the hollow marker is the half month of September.*

For each month the topics that rose most against their own nine-month mean (creator-balanced), with the entities named in that month's titles:

{table(sp3, ['month', 'label', 'z_vs_own_months', 'share_month', 'top_entities'], fmt='{:.3f}')}

Read left to right and 2026 tells itself: the Bondi Beach attack and a Trump Christmas in January; the Don Lemon arrest and the Alex Pretti shooting in February; the State of the Union and the tariff case in March; the Joe Kent resignation, the Artemis II mission and the No Kings protests in April; the Correspondents' Dinner shooting in May; the Massie primary and the Karmelo Anthony verdict in June; the 250th anniversary in July; the Fauci testimony and the Blanche confirmation in August; 9/11 at 25 and Nepal's floods in September (a half month). The full list with three example titles each is `topic_spikes.csv`.

## Caveats

- The topic labels and the political flag come from a local 14B model reading the top terms and eight example titles; the labels are readable but a few are odd ("Hasanabi Reacts to Hasan" is a fan-channel formula, not a subject) and the political flag errs towards "political". Both live in `topic_labels.csv` and can be edited; the political-only analyses re-run from `landscape`.
- {t1.get('outlier_share', 0):.0%} of the fit sample were HDBSCAN outliers; nearest-centroid assignment gives them a topic anyway, and {t1.get('weak_share', 0):.0%} of all titles sit below the 10th-percentile similarity of genuine members. Those weak assignments are flagged per title in `topics.csv`.

Files: `topics.csv` (title -> topic), `topic_labels.csv`, `creator_topic_mix.csv`, `topic_by_lane.csv`, `topic_timeline.csv`, `topic_spikes.csv`, `creator_political_share.csv`.
"""
    return out


def doc_dimensions() -> str:
    efa = json.loads((A / "efa_summary.json").read_text()); names = names_of()
    load = rd("factor_loadings.csv").set_index("feature"); fcols = [c for c in load.columns if re.fullmatch(r"F\d+", c)]
    cand = rd("validation_candidates.csv"); rt = rd("validation_retest.csv"); tcs = rd("topic_control_summary.csv")
    dims = rd("dimensions.csv"); ok = dims[(~dims.low_n) & (dims.genre == "videos")]
    vc = rd("validation_creator_level.csv"); vcr = vc[vc.score == "raw"]
    rows = []
    for f in fcols:
        s = load[f]
        hi = ", ".join(f"{k.replace('_p100', '').replace('_mean', '')} ({v:+.2f})" for k, v in s[s >= 0.4].sort_values(ascending=False).head(5).items())
        lo = ", ".join(f"{k.replace('_p100', '').replace('_mean', '')} ({v:+.2f})" for k, v in s[s <= -0.4].sort_values().head(3).items())
        sub = ok.sort_values(f + "_controlled")
        rows.append({"factor": f, "name": names[f], "variance": f"{efa['variance_explained'][fcols.index(f)]:.1%}", "loads on": hi + (("; against: " + lo) if lo else ""),
                     "highest creators (videos)": ", ".join(sub.tail(4).creator[::-1]), "lowest": ", ".join(sub.head(4).creator)})
    lm = ok.groupby("lane").agg(n=("creator", "size"), **{f: (f + "_controlled", "median") for f in ["F1", "F2", "F3", "F4", "F5", "F6", "F7", "F9"] if f in fcols}).reset_index()
    lm["lane"] = lm.lane.map(lane)
    r1 = {r.candidate: r for r in cand.itertuples()}
    piv = vcr.pivot(index="llm", columns="factor", values="spearman_r")[fcols].reset_index()
    out = f"""# 3. The style dimensions: how they title

**The question.** Along which dimensions do titles actually vary, where does each creator sit, and do those dimensions match the labels people reach for (Sensational, Critical, Analytical, Educational, Conversational, Humour)?

## The finding in one paragraph

Exploratory factor analysis of {efa['n_features']} title-level style features, aggregated to {efa['n_cells']:,} creator x genre x month cells, retains {efa['retained']} factors (parallel analysis suggested {efa['parallel_analysis_factors']}, capped at 12 for interpretability; KMO {efa['kmo_total']:.2f}; {efa['cumulative_variance']:.0%} of variance). The factors are not the six candidate labels. One factor is *tone*: positive, upbeat wording at one end and outrage vocabulary (shock words, "slams / destroys / exposed", negative sentiment) at the other, and it absorbs three of the candidates at once: the LLM's Sensational, Critical and Analytical ratings all correlate with this single factor (creator-level Spearman {r1['Sensational'].creator_level_r:+.2f}, {r1['Critical'].creator_level_r:+.2f}, {r1['Analytical/Informational'].creator_level_r:+.2f}). Everything else the factors pick up is *structural*: whether a title is a clause or a noun phrase, whether it wears a LIVE/BREAKING label, whether it talks like a stream chat, asks a question, names a person, reads as news prose, carries numbers, shouts in capitals, or quotes someone. Educational maps only partly onto the question/explainer factor ({r1['Educational'].creator_level_r:+.2f}); Conversational ({r1['Conversational'].creator_level_r:+.2f}) and Humour ({r1['Humor'].creator_level_r:+.2f}) do not appear as dimensions at all.

## The twelve factors

![Factor loadings: which title features define each factor (only features loading at 0.35 or more are shown).](figures/03_loadings_heatmap.png)
*Factor loadings: which title features define each factor (only features loading at 0.35 or more are shown).*

Each factor is named from its loadings (name, share of variance, the features that load on it, and the creators at each extreme after topic control, edited uploads only):

{table(pd.DataFrame(rows))}

![Scree plot: eigenvalues against the parallel-analysis threshold.](figures/03_scree.png)
*Scree plot: observed eigenvalues against the parallel-analysis threshold; the vertical line marks the twelve retained factors.*

How to read a creator's position: the profile cards give each score as a percentile rank among ranked creators of the same genre, with the lane median beside it. A creator at the 95th percentile on F9 titles in ALL CAPS more than 95 % of comparable channels.

## Which lanes sit where (median topic-controlled score, edited uploads, selected factors)

![Lane medians of the topic-controlled scores, all twelve factors.](figures/03_lane_medians_heatmap.png)
*Lane medians of the topic-controlled scores, all twelve factors.*

{table(lm, fmt='{:.2f}')}

The tone factor (F1) already separates the landscape's temperaments: left commentary is the most outrage-toned lane, legacy TV and the US press the most positive/neutral; the legacy wires and TV score high on F2 (clause headlines with a finite verb: "Houthis claim major advance") and F7 (descriptive news prose in sentence case), commentary lanes low. Question framing (F5) belongs to the press and the explainers; person-centred titles (F6) to interview podcasts and right TV.

## Do the candidate labels survive?

![Creator-level correlation between each LLM rating and each factor score.](figures/03_candidate_correlations.png)
*Creator-level correlation between each LLM rating and each factor score.*

{table(cand, ['candidate', 'best_factor', 'creator_level_r', 'second_factor', 'second_r', 'verdict'], fmt='{:.2f}')}

Full creator-level correlation matrix (LLM rating aggregated to creator x genre, n = {int(vc.n_groups.iloc[0])} groups with at least five rated titles, against the raw factor score):

{table(piv, fmt='{:.2f}')}

Three things to take from it. Sensational and Critical are the same thing as far as titles are concerned: a title that attacks is a title that shouts. Analytical is the *absence* of that (the positive pole of F1 plus the question factor), not a dimension of its own. And the model that rated the titles agrees with itself only moderately: on 300 titles rated twice in different batches, quadratic-weighted kappa is {float(rt.loc[rt.dimension == 'sensational', 'weighted_kappa'].iloc[0]):.2f} for sensational, {float(rt.loc[rt.dimension == 'critical', 'weighted_kappa'].iloc[0]):.2f} critical, {float(rt.loc[rt.dimension == 'analytical', 'weighted_kappa'].iloc[0]):.2f} analytical, {float(rt.loc[rt.dimension == 'conversational', 'weighted_kappa'].iloc[0]):.2f} conversational and only {float(rt.loc[rt.dimension == 'educational', 'weighted_kappa'].iloc[0]):.2f} educational, so the validation is trustworthy for tone and weak for the rest.

## How much of a creator's style is just its topics?

![Left: share of each factor's variance explained by topic at the title and creator level. Right: the rater's test-retest reliability per dimension.](figures/03_topic_control_and_retest.png)
*Left: share of each factor's variance explained by topic at the title and creator level. Right: the rater's test-retest reliability per dimension.*

The scores above are topic-controlled: each title's score minus the mean score of its topic (estimated on the balanced subset), averaged per creator. Topic explains between {tcs.title_level_r2_topic.min():.0%} and {tcs.title_level_r2_topic.max():.0%} of the title-level variance of a factor, most for numbers/dates (F8) and person-centred titles (F6), least for questions (F5) and capitals (F9). At the creator level the raw and controlled scores correlate at {tcs.creator_level_corr_raw_controlled.min():.2f}-{tcs.creator_level_corr_raw_controlled.max():.2f}: what a channel covers moves its score a little, how it titles moves it a lot. `dimensions.csv` carries raw, controlled and the topic-expected component side by side, and `dimensions_by_topic.csv` gives each creator's scores inside the five largest shared topics.

{table(tcs, ['factor', 'auto_name', 'title_level_r2_topic', 'creator_level_r2_topic', 'creator_level_corr_raw_controlled'], fmt='{:.2f}')}

## Lexical diversity and formulaicity (creator-level, not in the factor model)

Heaps' exponent on 20 subsamples of 1,500 tokens ranks creators by how fast their vocabulary grows: lowest (most repetitive) are the daily left-commentary channels (Harry Sisson, Pondering Politics, Luke Beasley, Jack Cocchiarella, Brian Tyler Cohen, 0.71-0.73), highest are the news outlets and long-title commentators (NY Post, Reuters, Fox News Clips, 0.87-0.88). The ranking is stable across subsample sizes (rank correlation 0.90-0.98 between 1,000, 1,500 and 3,000 tokens; `lexical_diversity_sensitivity.csv`). Formulaicity, the share of a creator's titles whose leading or trailing three-word template recurs in three or more of its other titles, is near 100 % for Belle of the Ranch ("Let's talk about ...") and the Hasan VOD channel, and above 85 % for Steve Turley, Joe Rogan, Firstpost and RSBN.

## Caveats

- The factor model is fitted on monthly cells so that each creator contributes at most nine rows. The cell threshold (15 unique titles) and the cap of 12 factors are choices; the smaller factors (F10-F12 carry 2-3 % of variance each) are the ones most exposed to them, and the sensitivity has not been tested here.
- The candidate-label test depends on a local 14B rater with modest reliability; a stronger rater could raise the Educational and Conversational correlations. It cannot create a Humour dimension: the rater found humour in 0.4 % of titles, so there is nothing to correlate.

Files: `features.csv`, `features_creator.csv`, `feature_definitions.csv`, `factor_loadings.csv`, `scree.csv` / `scree.png`, `efa_summary.json`, `dimensions.csv`, `dimensions_monthly.csv`, `dimensions_by_topic.csv`, `topic_control_summary.csv`, `labels.csv`, `validation_*.csv`.
"""
    return out


def doc_formats() -> str:
    hk = json.loads((A / "hook_classifier.json").read_text()); sh = rd("format_hook_shares.csv"); ag = rd("format_agreement.csv"); ex = rd("format_examples.csv"); rules = rd("format_rules.csv")
    lv = sh[(sh.level == "lane_mean_of_creators") & (sh.genre == "videos")].copy(); lv["lane"] = lv.lane.map(lane)
    ls = sh[(sh.level == "lane_mean_of_creators") & (sh.genre == "streams")].copy(); ls["lane"] = ls.lane.map(lane)
    m = hk["hooks"]
    lab = rd("labels.csv")
    out = f"""# 4. Formats and hooks

**The question.** Which structural formats do creators use (questions, LIVE labels, episode numbering, guests, reactions, confrontations, listicles, explainers), and which semantic hooks (curiosity gap, outrage frame, humour)?

## The finding in one paragraph

The outrage frame is the landscape's default hook, not a niche device. The rating model flagged {pct(lab.outrage.mean())} of a 3,000-title creator-stratified sample as framing their subject as outrageous, scandalous or threatening, and a classifier trained on those labels reproduces the judgement well on held-out titles (accuracy {m['outrage']['holdout_accuracy']:.2f}, AUC {m['outrage']['holdout_auc']:.2f}, kappa {m['outrage']['holdout_kappa']:.2f}). Applied to every title, it runs from three quarters of left-commentary and legal-commentary titles down to a quarter of US-press titles. The two other hooks could not be measured: the rater found a curiosity gap in {pct(lab.curiosity_gap.mean(), 1)} of titles and humour in {pct(lab.humor.mean(), 1)}, far too few positives to learn from (held-out F1 {m['curiosity_gap']['holdout_f1']:.2f} and {m['humor']['holdout_f1']:.2f}). Treat both as *unmeasured*, not absent (see document 8).

## Formats by lane (share of a creator's titles, mean over creators; edited uploads)

![Structural formats by lane, edited uploads.](figures/04_formats_heatmap.png)
*Structural formats by lane, edited uploads.*

{table(lv, ['lane', 'n_creators'] + FORMATS, fmt='{:.2f}')}

Questions are a press and explainer habit; episode numbering belongs to the talk shows (interview podcasts, humour) and to the right TV networks, whose stream titles are date-stamped replays; the reaction format is the streamers' own; confrontation wording ("vs", "destroys", "slams") is spread thinly across commentary and streamers and rare in news. Live VODs look different again, with LIVE/BREAKING labels on {pct(float(ls.loc[ls.lane == 'wires & international', 'breaking_live'].iloc[0]))} of wire streams and confrontation on {pct(float(ls.loc[ls.lane == 'streamers', 'confrontation'].iloc[0]))} of streamer streams (debates):

{table(ls, ['lane', 'n_creators', 'question', 'breaking_live', 'episode_show', 'interview_guest', 'confrontation', 'outrage'], fmt='{:.2f}')}

## The outrage hook by lane (edited uploads)

![Outrage-frame share by lane, edited uploads (left) and live VODs (right).](figures/04_outrage_by_lane.png)
*Outrage-frame share by lane, edited uploads (left) and live VODs (right).*

{table(lv.sort_values('outrage', ascending=False), ['lane', 'n_creators', 'outrage', 'curiosity_gap', 'humor'], fmt='{:.2f}')}

The gradient is the same one the tone factor found in document 3, measured a second way: commentary lanes on the left and right, legal commentary and streamers above 60 %, the wires and the US press and TV below 45 %. The two measures are not independent (the classifier sees the same words the lexicon counts), but they were built from different sources: the tone factor from word lists and sentiment, the hook from a model reading whole titles.

## Examples (corpus-wide, three per category)

{table(ex[ex.scope == 'corpus'], ['category', 'creator', 'title'])}

## Do the rules agree with the model?

Formats are regexes on the raw title (the exact patterns are in `format_rules.csv`); the rater also gave each sampled title one format label. Where both apply:

{table(ag[ag.category.isin(FORMATS)], ['category', 'rule_positives', 'llm_positives', 'precision_rule_vs_llm', 'recall_rule_vs_llm', 'kappa'], fmt='{:.2f}')}

The rules fire far more often than the model's single label for interview_guest and howto_explainer (the rules count "with a name" and "why"; the model picks one dominant format per title), so the rule shares above are upper bounds for those two categories. Question, breaking/live and episode formats agree well.

Files: `formats.parquet` (per title), `format_hook_shares.csv`, `format_examples.csv`, `format_rules.csv`, `format_agreement.csv`, `hook_classifier.json`.
"""
    return out


def doc_landscape() -> str:
    cc = rd("cluster_comparison.csv"); coh = rd("lane_style_cohesion.csv"); dis = rd("disagreements_lane_style.csv"); ent = rd("entities_top.csv")
    st = rd("shared_titles.csv"); tp = rd("shared_templates.csv"); nn = rd("neighbours_style.csv"); orgs = rd("org_style.csv")
    cross = st[~st.same_organisation_only]
    cv = coh[(coh.titles == "all") & (coh.genre == "videos")].sort_values("cohesion_ratio").copy(); cv["lane"] = cv.lane.map(lane)
    dd = dis[(dis.genre == "videos") & (dis.titles == "all")]
    split = dd[dd.kind.str.startswith("lane")].copy(); split["group"] = split.group.map(lane)
    nnv = nn[(nn.titles == "all") & (nn.genre == "videos")].set_index("creator")
    picks = ["@HasanAbi", "@BenShapiro", "@FoxNews", "@MeidasTouch", "@TuckerCarlson", "@joerogan", "@Reuters", "@destiny", "@bennyjohnson", "@CNN"]
    nrows = [{"creator": c, "lane": lane(nnv.loc[c, "lane"]), "five nearest in style": ", ".join(f"{nnv.loc[c, f'nn{i}']} [{lane(nnv.loc[c, f'nn{i}_lane'])}]" for i in range(1, 6))} for c in picks if c in nnv.index]
    ccv = cc.copy(); ccv = ccv[["genre", "titles", "n_creators", "style_k", "style_silhouette", "topic_k", "topic_silhouette", "ari_style_vs_lane", "ari_topic_vs_lane", "ari_style_vs_topic"]]
    ep = ent[ent.kind == "person"].head(15); eo = ent[ent.kind == "organisation"].head(10)
    out = f"""# 5. The landscape: who titles like whom

**The question.** Do creators that share a lane share a style? Who are each creator's real neighbours in style, as opposed to in subject matter? Who gets named, and does the landscape converge on the same hooks?

## The finding in one paragraph

Lane predicts style almost not at all. Clustering creators in the twelve-dimensional, topic-controlled style space and comparing the clusters with the lanes gives an adjusted Rand index of {float(cc.loc[(cc.genre == 'videos') & (cc.titles == 'all'), 'ari_style_vs_lane'].iloc[0]):.3f} for edited uploads ({float(cc.loc[(cc.genre == 'videos') & (cc.titles == 'political'), 'ari_style_vs_lane'].iloc[0]):.3f} on political titles only), and topic clusters do no better ({float(cc.loc[(cc.genre == 'videos') & (cc.titles == 'all'), 'ari_topic_vs_lane'].iloc[0]):.3f}). Only one lane holds together, US legacy TV (its members are {1 - float(cv.iloc[0].cohesion_ratio):.0%} closer to each other than to everyone else); every other lane is about as dispersed as the corpus. The largest style cluster holds 69 creators from eleven lanes. So the useful unit is not the lane but the five nearest style neighbours on each creator's card, and those cut across politics: Hasan Piker's are Vaush and two right-wing channels, Ben Shapiro's include Kim Iversen and Alex Stein, MeidasTouch's are Officer Tatum and Nick Fuentes. The hooks converge too: {len(cross)} titles are used verbatim by creators from different organisations ("THIS IS INSANE.." by {int(cross.iloc[0].n_creators)} creators in {int(cross.iloc[0].n_lanes)} lanes), {pct(1 - cross.within_lane.mean())} of them across lanes.

## Clusterings against the lanes

![Style space: every ranked creator, coloured by lane family. The interactive version, with names on hover and each creator's five neighbours, is on the HTML page.](figures/05_style_map.png)
*Style space: every ranked creator, coloured by lane family. The interactive version, with names on hover and each creator's five neighbours, is on the HTML page.*

Style space: agglomerative (Ward) on z-scored topic-controlled factor scores. Topic space: average linkage on the Jensen-Shannon distance between creators' topic mixes. k chosen by silhouette; ARI = adjusted Rand index (1 = identical partitions, 0 = chance).

{table(ccv, fmt='{:.3f}')}

The low silhouettes (0.09-0.16) say the same thing from the other side: neither space has well-separated groups, the creators form a continuum.

![Topic space map.](figures/05_topic_map.png)
*Topic space: MDS of the Jensen-Shannon distances between creators' topic mixes.*

![ARI and cohesion.](figures/05_lanes_vs_style.png)
*Left: adjusted Rand index of the clusterings against the lanes and against each other. Right: lane cohesion in style space.*

## Which lanes cohere (edited uploads)

Mean distance in style space between members of a lane, over the mean distance from members to everyone else; below 1 means lane-mates are closer than strangers.

{table(cv, ['lane', 'n_creators', 'within_lane_distance', 'between_lane_distance', 'cohesion_ratio'], fmt='{:.2f}')}

## Where lane and style disagree

Every lane with three or more members is split across style clusters; the share of a lane in its own largest style cluster:

{table(split, ['group', 'n_creators', 'n_style_clusters', 'largest_cluster_share'], fmt='{:.2f}')}

Conversely, style clusters span lanes: the two largest ({int(dd[dd.kind.str.startswith('style')].n_creators.max())} and {int(dd[dd.kind.str.startswith('style')].n_creators.nlargest(2).iloc[1])} creators) each mix left and right commentary, streamers, podcasts and independent news. Full membership lists: `disagreements_lane_style.csv`, `style_clusters.csv`, `topic_clusters.csv`.

## Nearest style neighbours, a sample

{table(pd.DataFrame(nrows))}

Neighbours are computed on titles with same-organisation cross-posts removed and low-n creators excluded; every creator's five style and five topic neighbours are on its card and in `neighbours_style.csv` / `neighbours_topic.csv`. The maps on the HTML page (PCA of the style space, MDS of the topic space) show the same picture: lane colours are scattered through both.

## Organisations

Sister channels do share a house style: the four MeidasTouch Network channels sit together at the outrage end of the tone factor (organisation score {float(orgs.loc[(orgs.organisation == 'MeidasTouch Network') & (orgs.genre == 'videos'), 'F1_controlled'].iloc[0]):.2f}) and high on capitals; the three Timcast channels are the most capitalised organisation ({float(orgs.loc[(orgs.organisation == 'Timcast') & (orgs.genre == 'videos'), 'F9_controlled'].iloc[0]):.2f} on F9); the four NYT channels and CBS sit at the positive/neutral end. Title-weighted organisation scores (clippers excluded) are in `org_style.csv`.

## Who gets named

![Outrage-frame ratio for the 25 most-named people: orange above the corpus baseline, blue below.](figures/05_entities_outrage.png)
*Outrage-frame ratio for the 25 most-named people: orange above the corpus baseline, blue below.*

Counted on the creator-balanced subset; people keyed by surname, so "Kirk" pools Charlie and Erika Kirk and "Trump" pools every Trump. `outrage_ratio` is the outrage-frame share of titles naming the entity over the corpus share.

{table(ep, ['entity', 'n_titles_balanced', 'n_creators', 'top_lanes_by_share', 'outrage_share', 'outrage_ratio'], fmt='{:.2f}')}

{table(eo, ['entity', 'n_titles_balanced', 'n_creators', 'top_lanes_by_share', 'outrage_share', 'outrage_ratio'], fmt='{:.2f}')}

Trump is in {pct(float(ent.loc[(ent.kind == 'organisation') & (ent.entity == 'Trump'), 'share_of_balanced_titles'].iloc[0]), 1)} of balanced titles counting both tags, named by {int(ent.loc[(ent.kind == 'person') & (ent.entity == 'Trump'), 'n_creators'].iloc[0])} of 274 creators, most by legal commentary and left commentary. The entities carrying the most outrage framing relative to baseline are MAGA (1.6x), Pam Bondi, Kash Patel and Candace Owens (1.3-1.5x); the least are the crime-story names (Nancy Guthrie, Lindsay Clancy, 0.3x) and institutions used as datelines (the Senate, the House, the White House). "Hormuz" is a spaCy mistake (a strait tagged as a person) left visible on purpose: entity counts from a small NER model on headline text are noisy at the margin.

## Convergent formulas

![The most shared verbatim titles across organisations.](figures/05_shared_titles.png)
*The most shared verbatim titles across organisations.*

Of {len(st):,} distinct titles (case-insensitive) used by two or more creators, {len(cross):,} cross organisations; the rest are same-outlet cross-posts (TYT / The Damage Report alone account for hundreds). The most shared:

{table(cross.head(15), ['example', 'n_creators', 'n_titles', 'n_lanes', 'lanes'], fmt='{:.0f}')}

These are content-free exclamations, the "Shocking Events and Reactions" topic of document 2: the same dozen phrases serve as titles on the left, the right and the streaming platforms. With names and numbers masked, the shared templates are outrage frames and guest formulas:

{table(tp.head(15), ['template', 'n_creators', 'n_titles', 'n_lanes', 'example'], fmt='{:.0f}')}

{pct(tp.within_lane.mean())} of shared templates stay within a lane, {pct(cross.within_lane.mean())} of shared verbatim titles: the conventions travel across the landscape rather than within its camps.

Files: `cluster_comparison.csv`, `lane_style_cohesion.csv`, `disagreements_lane_style.csv`, `style_clusters.csv`, `topic_clusters.csv`, `neighbours_style.csv`, `neighbours_topic.csv`, `map_style.csv`, `map_topic.csv`, `org_style.csv`, `entities_top.csv`, `shared_titles.csv`, `shared_templates.csv`.
"""
    return out


def doc_drift() -> str:
    names = names_of(); dl = rd("drift_lane_monthly.csv"); tr = rd("drift_trends.csv"); tcl = rd("topic_change_lane_monthly.csv")
    months = [m for m in dl.month.unique()]
    sel = ["ALL (mean of creators)", "left_commentary", "right_commentary", "streamer_reaction", "us_legacy_tv", "us_press_print_digital", "independent_digital_news"]
    x = dl[(dl.genre == "videos") & dl.lane.isin(sel)].copy(); x["lane"] = x.lane.map(lambda l: lane(l) if l in LANE_LABEL else "all lanes (mean of creators)")
    po = x.pivot(index="lane", columns="month", values="outrage").reset_index()
    pf = x.pivot(index="lane", columns="month", values="F1_controlled").reset_index()
    p9 = x.pivot(index="lane", columns="month", values="F9_controlled").reset_index()
    strong = tr[(tr.level == "lane") & (tr.p < 0.05) & (tr.spearman_trend.abs() >= 0.6)].copy()
    strong["group"] = strong.group.map(lane); strong["measure"] = strong.measure.map(lambda m: (m.replace("_controlled", "") + ": " + short_name(m.replace("_controlled", ""), names)) if m.replace("_controlled", "") in names else m)
    js = tcl[tcl.genre == "videos"].groupby("lane").mean_js.mean().sort_values().rename("mean month-to-month JS distance").reset_index(); js["lane"] = js.lane.map(lane)
    n_series = int((tr.level == "lane").sum())
    out = f"""# 6. Drift: how titles changed from January to September

**The question.** Did the landscape's title style move over 2026, and did different lanes move differently? Months are the only safe unit: YouTube listing dates are month-accurate, and September covers the 1st to the 14th only (shown, never compared on volume).

## The finding in one paragraph

Not much, and not in one direction. Of {n_series} lane x genre x measure series (twelve dimensions and three hooks, nine months), {len(strong)} show a monotone trend (|Spearman| >= 0.6, p < 0.05), and they point different ways for different lanes. Averaged over all creators the outrage share of edited uploads is flat ({pct(float(po.loc[po.lane == 'all lanes (mean of creators)', months[0]].iloc[0]))} in January, {pct(float(po.loc[po.lane == 'all lanes (mean of creators)', months[-2]].iloc[0]))} in August). Underneath, left commentary cooled slightly (outrage {pct(float(po.loc[po.lane == 'left commentary', months[0]].iloc[0]))} to {pct(float(po.loc[po.lane == 'left commentary', months[-2]].iloc[0]))}, ALL-CAPS score down, tone factor up), while the right TV networks' live streams went the other way (outrage share {pct(float(dl.loc[(dl.genre == 'streams') & (dl.lane == 'right_tv_network') & (dl.month == months[0]), 'outrage'].iloc[0]))} to {pct(float(dl.loc[(dl.genre == 'streams') & (dl.lane == 'right_tv_network') & (dl.month == months[-2]), 'outrage'].iloc[0]))}). Topic turnover is steadier than style: creators re-mix their subjects every month by a similar amount, most in humour and interview podcasts, least in the wires and TV that follow the same news flow.

## Outrage share by month (edited uploads; mean of creators)

![Outrage-frame share by month, one panel per lane, against the all-creator mean (grey dashed).](figures/06_drift_outrage.png)
*Outrage-frame share by month, one panel per lane, against the all-creator mean (grey dashed).*

{table(po, fmt='{:.2f}')}

## Tone factor (F1, positive vs outrage; topic-controlled) by month

![The tone factor by month, per lane.](figures/06_drift_tone.png)
*The tone factor by month, per lane.*

{table(pf, fmt='{:.2f}')}

## ALL-CAPS factor (F9) by month

![The ALL-CAPS factor by month, per lane.](figures/06_drift_caps.png)
*The ALL-CAPS factor by month, per lane.*

{table(p9, fmt='{:.2f}')}

## The trends that are strong enough to report

{table(strong.sort_values(['group', 'genre']), ['group', 'genre', 'measure', 'spearman_trend', 'first_month_value', 'last_full_month_value'], fmt='{:.2f}')}

Read these with the lane sizes in mind: right TV networks are four channels, legal commentary eight, so a "lane trend" there can be one channel changing its stream titling (RSBN's date stamps, for instance). Per-creator trends for the thirty largest creators are in `drift_trends.csv` (level = creator) and every creator's monthly series is on its card as sparkline data (`drift_creator_monthly.csv`).

## Month-to-month topic change

Jensen-Shannon distance between a creator's topic mix in consecutive months (months with at least 15 titles), averaged per lane over the year:

{table(js, fmt='{:.2f}')}

The ordering is the inverse of news dependence: the wires and legacy TV move least because the news moves them all the same way; humour and interview podcasts move most because each episode is its own subject. The monthly matrix is in `topic_change_lane_monthly.csv`.

## Caveats

- Nine points per series is a short run; a trend that begins in March can look strong. The strong-trend table should be read as "worth a look", not as a finding on its own.
- September is a half month and appears in the tables for completeness; no volume comparison uses it.

Files: `drift_lane_monthly.csv`, `drift_creator_monthly.csv`, `drift_top30_monthly.csv`, `drift_trends.csv`, `topic_change_monthly.csv`, `topic_change_lane_monthly.csv`.
"""
    return out


def doc_views() -> str:
    names = names_of(); es = rd("engagement_summary.csv"); hc = rd("hit_concentration.csv"); hcc = rd("hit_concentration_correlations.csv"); em = json.loads((A / "engagement_model.json").read_text())
    allv = es[(es.lane == "ALL") & (es.genre == "videos")].copy()
    allv["predictor"] = allv.predictor.map(lambda p: f"{p}: {short_name(p, names)}" if p in names else p)
    alls = es[(es.lane == "ALL") & (es.genre == "streams")].copy(); alls["predictor"] = alls.predictor.map(lambda p: f"{p}: {short_name(p, names)}" if p in names else p)
    byl = es[(es.lane != "ALL") & (es.genre == "videos") & (es.predictor == "outrage")].copy(); byl["lane"] = byl.lane.map(lane)
    hv = hc[hc.genre == "videos"]; hs = hc[hc.genre == "streams"]
    hl = hv.groupby("lane").agg(n=("creator", "size"), median_gini=("gini", "median"), median_top10_share=("top10_share", "median")).reset_index(); hl["lane"] = hl.lane.map(lane)
    pooled = hcc[hcc.scope.str.startswith("pooled") & (hcc.genre == "videos") & (hcc.p < 0.05)].copy()
    pooled["predictor"] = pooled.predictor.map(lambda p: f"{p[:-11]}: {short_name(p[:-11], names)}" if p.endswith("_controlled") else p)
    o = allv[allv.predictor == "outrage"].iloc[0]
    out = f"""# 7. Views: does title style predict engagement, and how concentrated are hits?

**The question.** Within a channel, do titles with more outrage, more capitals, a question, a name, a longer length get more views once the story and the month are held fixed? And how unequal are a channel's views across its videos?

## The finding in one paragraph

Within creator, the outrage frame is the only title feature that predicts views with a consistent sign. For each of the {int(o.n_creators)} channels with at least 100 edited uploads carrying a view count, log views were regressed on the title's twelve factor scores, its hook labels and its length, with publish-month and topic dummies as controls; predictors are standardised within the channel. The outrage coefficient is positive for {pct(o.share_positive)} of channels, significant and positive for {pct(o.share_sig_positive)}, significant and negative for {pct(o.share_sig_negative)}, median {o.median_coef_per_sd:+.3f} log views per standard deviation (a few per cent more views for a one-SD more outraged title). Every other predictor has a median effect at or below 0.03 in absolute value with sign agreement between 50 % and 70 % across channels, which is a null result at this sample size. Views are concentrated (median Gini {hv.gini.median():.2f}; the top 10 % of a channel's videos take {pct(hv.top10_share.median())} of its views) but the tail is not a power law: the Clauset-Shalizi-Newman likelihood-ratio test prefers a lognormal in {int((~hv.powerlaw_like).sum())} of {len(hv)} video channels. Concentration tracks channel size more than style.

## Within-creator effects, edited uploads (median over channels)

![Per-channel coefficients for every title feature; boxes show the spread across channels, the black line the median.](figures/07_engagement_coefficients.png)
*Per-channel coefficients for every title feature; boxes show the spread across channels, the black line the median.*

Coefficient = change in log(1 + views) per one within-channel standard deviation of the predictor; `share_positive` = share of channels with a positive coefficient; `share_sig_*` at p < 0.05 (HC3).

{table(allv, ['predictor', 'n_creators', 'median_coef_per_sd', 'q25', 'q75', 'share_positive', 'share_sig_positive', 'share_sig_negative', 'median_r2'], fmt='{:.3f}')}

Live VODs (n = {int(alls.n_creators.max())} channels) show the same picture, outrage {alls.loc[alls.predictor == 'outrage', 'median_coef_per_sd'].iloc[0]:+.3f} with {pct(float(alls.loc[alls.predictor == 'outrage', 'share_positive'].iloc[0]))} positive, everything else near zero.

## The outrage effect by lane (edited uploads)

![Median outrage coefficient per lane with the share of channels where it is positive.](figures/07_outrage_effect_by_lane.png)
*Median outrage coefficient per lane with the share of channels where it is positive.*

{table(byl.sort_values('median_coef_per_sd', ascending=False), ['lane', 'n_creators', 'median_coef_per_sd', 'share_positive', 'share_sig_positive'], fmt='{:.3f}')}

The effect is largest and most consistent where outrage is *rare*: the wires, legacy TV, the press, legal commentary and interview podcasts. In left commentary, where three quarters of titles already carry the frame, it is smaller; in right commentary and among streamers it is close to nothing. That is what a saturating device looks like: it lifts a title above a neutral baseline, and lifts nothing when every title has it.

## What the model does and does not say

- Views are a snapshot taken at fetch time (2026-09-14): a January video has had eight months to accumulate views, a September one two weeks. The month dummies absorb this within a channel, so the coefficients compare titles published in the same month, but they describe views-to-date, not lifetime views.
- Subscriber normalisation changes nothing here: log(views / subscribers) is log(views) minus a constant within a channel, so every slope is identical; subscriber counts are reported beside the coefficients instead.
- Median R2 is {allv.median_r2.iloc[0]:.2f}: month and topic explain a fair share of within-channel views; title style, on top of them, explains little.
- Rumble channels have no view counts and are absent; the platform therefore never enters the engagement or concentration results.

Specification: `engagement_model.json`; per-channel coefficients: `engagement_coefficients.csv`.

## Hit concentration

![Gini coefficient of views per channel, grouped by lane.](figures/07_gini_by_lane.png)
*Gini coefficient of views per channel, grouped by lane.*

Per channel x genre with at least 100 videos carrying views (all rows, repeats included: a re-uploaded live loop is a separate video with its own views).

{table(hl.sort_values('median_gini'), fmt='{:.2f}')}

Streamers and daily left commentators spread views most evenly (Gini 0.18-0.33 for Tariq Nasheed, Belle of the Ranch, Vaush, the Hasan VOD channel); the wires, legacy TV, the press and the right TV networks are the most hit-driven (median Gini 0.66-0.73; Real America's Voice, Politicon, Axios and The Fifth Column above 0.81, the top tenth of their videos taking three quarters of their views).

![Lorenz curves and the tail test.](figures/07_lorenz_and_tails.png)
*Left: Lorenz curves for seven channels. Right: the likelihood-ratio statistic of the power-law fit against a lognormal across all video channels.*

## Zipf's law for views

The rank-size view of the same distributions: within each channel, videos ranked by views, plotted on log-log axes. A straight line would be Zipf's law (views proportional to rank to a negative power); the curves instead bend downwards in the tail, which is what a lognormal looks like on these axes and what the formal test below confirms. The slope of log views on log rank over all of a channel's videos summarises how steeply views fall off down the ranking: the lane pattern follows the Gini ordering, shallow for streamers and daily left commentary, steep for the wires and legacy TV. Per-channel slopes (all videos, and the top decile only) are in `hit_concentration.csv` (`zipf_views_all`, `zipf_views_head`).

![Zipf rank-size curves of views and the slope by lane.](figures/07_zipf_views.png)
*Left: rank-size curves for eight channels, each normalised to its own top video. Right: the all-video Zipf slope per channel, grouped by lane.*

**Power law or not.** The `powerlaw` fit (discrete, xmin by KS minimisation) with the likelihood-ratio test against a lognormal supports a power-law tail in {int(hv.powerlaw_like.sum())} of {len(hv)} video channels and {int(hs.powerlaw_like.sum())} of {len(hs)} stream channels; the ratio even points towards the power law in only {pct(float((hv.lr_vs_lognormal > 0).mean()))} of video channels. Hits are heavy-tailed but lognormal-shaped, so no channel here should be described as having a power-law audience.

## Does style go with concentration?

Spearman correlations across channels, lane-demeaned (so a lane's overall level cannot drive them), edited uploads, p < 0.05 only:

{table(pooled.sort_values(['target', 'spearman_r']), ['target', 'predictor', 'n_creators', 'spearman_r', 'p'], fmt='{:.3f}')}

The strongest correlate is size: channels with more subscribers are *less* concentrated (rho about -0.3), and channels whose titles are more outrage-framed are less concentrated too, partly because those are the daily commentary channels whose audiences turn up for everything. Question framing and person-centred titles go with slightly more concentration. All of these are weak (|rho| <= 0.32) and observational.

Files: `engagement_coefficients.csv`, `engagement_summary.csv`, `engagement_model.json`, `hit_concentration.csv`, `hit_concentration_correlations.csv`.
"""
    return out


def doc_nulls() -> str:
    rt = rd("validation_retest.csv"); lab = rd("labels.csv"); hk = json.loads((A / "hook_classifier.json").read_text())["hooks"]; cand = rd("validation_candidates.csv")
    out = f"""# 8. Null results and caveats

Results that came out empty are results; and several numbers in this set should be read with their weaknesses in view.

## What did not show up

- **A Conversational dimension.** The LLM's conversational rating correlates with the factor closest to it (stream talk: chat, ellipsis, contractions) at only r = {float(cand.loc[cand.candidate == 'Conversational', 'creator_level_r'].iloc[0]):.2f} at the creator level. The structural markers exist (document 3, F4) but they do not track what a reader calls conversational.
- **A Humour dimension, and a humour hook.** The rater flagged {int(lab.humor.sum())} of {len(lab)} sampled titles as humorous; its test-retest kappa on the flag is {float(rt.loc[rt.dimension == 'humor', 'kappa'].iloc[0]):.2f}; the classifier's held-out F1 is {hk['humor']['holdout_f1']:.2f}. Humour in titles is either genuinely rare in this landscape or invisible to a 14B model reading ten words. Nothing in the results should be cited as a measure of humour.
- **A curiosity-gap hook.** {int(lab.curiosity_gap.sum())} positives of {len(lab)} ({pct(lab.curiosity_gap.mean(), 1)}), classifier F1 {hk['curiosity_gap']['holdout_f1']:.2f}. The lexicon feature that approximates it (`curiosity_lex`: "here's why", "you won't believe", "this is insane") loads on the outrage pole of the tone factor, which suggests the device mostly *is* outrage in this corpus, but the hook as defined was not measured.
- **Style as a predictor of views** (beyond outrage). Twelve dimensions, length, curiosity: all median effects at or below 0.03 log views per SD with 50-70 % sign agreement across channels (document 7).
- **Power-law audiences.** 0 of 193 video channels (document 7).
- **Lane as a style predictor.** ARI 0.045 (document 5).
- **A landscape-wide drift.** Corpus-mean outrage share flat over the year (document 6).

## What to distrust, and how much

- **The rater.** All ratings and labels come from a local Qwen3-14B model at temperature 0. Weighted kappa on a 300-title retest: sensational {float(rt.loc[rt.dimension == 'sensational', 'weighted_kappa'].iloc[0]):.2f}, critical {float(rt.loc[rt.dimension == 'critical', 'weighted_kappa'].iloc[0]):.2f}, analytical {float(rt.loc[rt.dimension == 'analytical', 'weighted_kappa'].iloc[0]):.2f}, conversational {float(rt.loc[rt.dimension == 'conversational', 'weighted_kappa'].iloc[0]):.2f}, educational {float(rt.loc[rt.dimension == 'educational', 'weighted_kappa'].iloc[0]):.2f}; kappa on the outrage flag {float(rt.loc[rt.dimension == 'outrage', 'kappa'].iloc[0]):.2f}, on the format label {float(rt.loc[rt.dimension == 'format_llm', 'kappa'].iloc[0]):.2f}. The validation of the tone factor stands on the reliable ratings; the rest is indicative. Re-rating with a stronger model is one cached command (`llm_rate --model ...`).
- **The lanes** are a proposal (document 1). Every lane-level table changes when they are corrected; the creator-level tables, neighbours and clusters do not.
- **The political flag** is broad (212 of 236 topics). The political-only landscape run reaches the same conclusions as the all-titles run, which limits how much this matters, but per-creator political shares should not be quoted without that caveat.
- **Entity counts** come from spaCy's small English model on truecased headline text; "Hormuz" as a person and fan-channel formulas as people show the noise. The top-25 lists are robust, the tail is not.
- **Views** are a fetch-time snapshot; Rumble has none; verbatim repeats are kept for view and concentration statistics and removed for everything else.
- **Group sizes.** Explainers/geopolitics has 3 ranked creators, right TV networks 4, humour 6; anything lane-level for those is a description of a handful of channels.
- **The corpus is one calendar window** dominated by one war. A landscape measured in a quieter year could show more topic separation between lanes and a smaller shared-title set.

## What would change the picture most

Correcting the lanes; re-rating the 3,000 titles with a more reliable model (or a human sample) to settle Educational and Conversational; and a second time window, so drift can be measured on more than nine points.
"""
    return out




# --------------------------------------------------------------------------- #
# Question documents (09-14)
# --------------------------------------------------------------------------- #
def doc_twins() -> str:
    pairs = rd("style_twins.csv"); near = rd("style_twins_nearest.csv"); dims = rd("dimensions.csv")
    n_left = int((near.lane == "left_commentary").sum()); n_right = int((near.lane == "right_commentary").sum())
    top = pairs.head(20).copy(); top["distance_percentile_all_pairs"] = top.distance_percentile_all_pairs.round(2)
    hub = pairs.head(40).right_creator.value_counts().head(3)
    closer = near.twin_closer_than_any_same_lane.mean()
    nl = near[near.lane == "left_commentary"].head(12); nr = near[near.lane == "right_commentary"].head(12)
    return f"""# 9. Stylistic twins across the political divide

**The question.** Which left-commentary and right-commentary creators title their videos the same way?

## The finding in one paragraph

Style ignores the divide. Measured in the twelve-dimensional, topic-controlled style space of document 3, the nearest neighbour of a left-commentary creator is on the right side of the divide about as often as on its own side: for {closer:.0%} of the {len(near)} commentary creators the closest right (or left) creator is closer than *any* creator in their own lane, and the distributions of nearest-twin distance and nearest-lane-mate distance sit almost on top of each other. The closest pairs are not the big names but the mid-sized daily outrage channels on both sides: {top.iloc[0].left_creator} and {top.iloc[0].right_creator}, {top.iloc[2].left_creator} and {top.iloc[2].right_creator}, The Majority Report and Owen Shroyer, The Young Turks and Nick Fuentes. What they share is form: emphasis capitals on one or two words, a named target, a verb of attack or collapse, no question, no label, no numbers.

![The twenty closest pairs and the distance comparison.](figures/09_twins.png)
*Left: the twenty closest left-right pairs. Right: for every commentary creator, the distance to its nearest creator across the divide against the distance to its nearest lane-mate.*

## The twenty closest pairs

`distance` is Euclidean distance between z-scored topic-controlled factor scores (edited uploads); `distance_percentile_all_pairs` places the pair among all {len(dims[(dims.genre == 'videos') & (~dims.low_n)])} ranked creators' pairwise distances (0 = the closest pair in the whole landscape).

{table(top, ['left_creator', 'right_creator', 'distance', 'distance_percentile_all_pairs'], fmt='{:.2f}')}

A few right-side channels recur as everybody's twin ({', '.join(f'{k} x{v}' for k, v in hub.items())}): they sit near the centre of the commentary cloud, so they are close to many left creators at once. Hubness like this is a property of the space, not evidence of imitation.

## Every creator's twin across the divide

The full table is `style_twins_nearest.csv`; the twelve left and twelve right creators with the closest twins:

{table(nl, ['creator', 'twin_across_divide', 'twin_distance', 'twin_rank_among_all_neighbours', 'nearest_same_lane', 'nearest_same_lane_distance', 'twin_closer_than_any_same_lane'], fmt='{:.2f}')}

{table(nr, ['creator', 'twin_across_divide', 'twin_distance', 'twin_rank_among_all_neighbours', 'nearest_same_lane', 'nearest_same_lane_distance', 'twin_closer_than_any_same_lane'], fmt='{:.2f}')}

`twin_rank_among_all_neighbours` = 1 means the twin is the creator's single nearest neighbour in the whole landscape (any lane).

## Method

1. Style vectors: the twelve factor scores of document 3, topic-controlled (each title's score minus its topic's mean, averaged per creator), edited uploads only, creators with at least 50 unique titles, clip channels excluded ({n_left} left-commentary and {n_right} right-commentary creators).
2. Each factor z-scored across the ranked creators so that no factor dominates; distance = Euclidean over the twelve.
3. For every creator on one side, the nearest creator on the other side is its twin; the same distance is computed to the nearest creator on its own side; the pair distance is also expressed as a percentile of all ranked pairwise distances.
4. "Left" and "right" are the `left_commentary` and `right_commentary` lanes of the proposal in `lanes.csv`.

## Limitations

- The divide is the lane proposal, so a mislabelled creator becomes a spurious twin; centrist, legal, streamer and podcast lanes are not in the comparison at all.
- The space weights all twelve factors equally after z-scoring; two creators can be twins on capitals, questions and quotes while differing in tone, or the reverse. `dimensions.csv` has the per-factor scores if a narrower definition is wanted.
- Topic control removes the average effect of a topic on each score, not everything a subject does to a title.
- Distances shrink for creators near the centre of the cloud (hubness above) and grow for eccentric ones; the percentile column is the fairer comparison.
- Only edited uploads; live VODs are too thin for both lanes.

Files: `style_twins.csv`, `style_twins_nearest.csv`, `dimensions.csv`, `neighbours_style.csv`.
"""


def doc_outrage() -> str:
    oc = rd("outrage_by_lane_ci.csv"); hk = json.loads((A / "hook_classifier.json").read_text())["hooks"]["outrage"]; rt = rd("validation_retest.csv"); lab = rd("labels.csv")
    v = oc[oc.genre == "videos"].copy(); v["lane"] = v.lane.map(lane); s_ = oc[oc.genre == "streams"].copy(); s_["lane"] = s_.lane.map(lane)
    top, bottom = v.iloc[0], v.iloc[-1]
    kap = float(rt.loc[rt.dimension == "outrage", "kappa"].iloc[0])
    return f"""# 10. How much of political YouTube is framed as outrage, lane by lane?

**The question.** What share of a creator's titles frames its subject as outrageous, scandalous or threatening, and how does that differ between lanes?

## The finding in one paragraph

Across the landscape the outrage frame is the majority style of commentary and the minority style of news. Averaging creators within a lane (edited uploads), {top.lane} sits at {pct(top['mean'])} (95 % CI {pct(top.ci95_low)}-{pct(top.ci95_high)}) and {bottom.lane} at {pct(bottom['mean'])} ({pct(bottom.ci95_low)}-{pct(bottom.ci95_high)}); the commentary lanes on both sides, legal commentary and streamers all exceed 60 %, the wires, legacy TV and the press all fall below 45 %. The confidence intervals of the commentary block and the news block do not overlap. Left commentary is higher than right commentary ({pct(float(v.loc[v.lane == 'left commentary', 'mean'].iloc[0]))} vs {pct(float(v.loc[v.lane == 'right commentary', 'mean'].iloc[0]))}), and the two intervals barely touch, so that gap is real but modest. Within every lane the creator-to-creator spread is wide (dots in the figure): lane is a weak predictor of any one channel.

![Outrage share by lane with confidence intervals.](figures/10_outrage_by_lane_ci.png)
*Each dot is a creator's share; the bar is the lane mean with a bootstrap 95 % interval.*

## Edited uploads

{table(v, ['lane', 'n_creators', 'mean', 'ci95_low', 'ci95_high', 'median', 'q25', 'q75', 'min', 'max'], fmt='{:.2f}')}

## Live VODs

{table(s_, ['lane', 'n_creators', 'mean', 'ci95_low', 'ci95_high', 'median', 'q25', 'q75', 'min', 'max'], fmt='{:.2f}')}

## Method

1. **Definition.** A local model (Qwen3-14B, temperature 0) rated a creator-stratified sample of {len(lab):,} raw titles; the outrage flag was defined in the prompt as "the subject is framed as outrageous, scandalous or threatening (slams, destroys, exposed, disaster, betrayal, meltdown)". {pct(lab.outrage.mean())} of the sample was flagged.
2. **Classifier.** A logistic regression on the title's sentence embedding plus twelve style features, trained on those labels (5-fold cross-validation for the regularisation strength, then a stratified 20 % hold-out: accuracy {hk['holdout_accuracy']:.2f}, balanced accuracy {hk['holdout_balanced_accuracy']:.2f}, AUC {hk['holdout_auc']:.2f}, kappa {hk['holdout_kappa']:.2f}), refitted on the whole sample and applied to every unique title.
3. **Aggregation.** Share of flagged titles per creator x genre (verbatim repeats collapsed); lane figure = mean of creators with at least 50 unique titles, with a bootstrap 95 % interval from 1,000 resamples of creators. Medians and quartiles describe the spread.

## Limitations

- **The rater.** The flag's test-retest kappa on 300 titles is {kap:.2f} (moderate); the definition is broad, and a title about a shooting or a flood can be flagged as "threatening" without any editorial outrage. That is why the wires and legacy TV land at 30-45 % rather than near zero: part of their share is event negativity. Document 3's tone factor, built from word lists rather than a model, gives the same lane ordering, which is the check that the pattern is not a rater artefact.
- **The classifier** is right about three titles in four on held-out data; errors are roughly symmetric, so lane means are less biased than individual titles, but a single creator's share carries an error of several points.
- **Lanes** are the proposal in `lanes.csv`; small lanes (right TV networks n = 4, explainers n = 3) have wide intervals and should be read as descriptions of a handful of channels.
- Titles only: an outraged thumbnail over a neutral title, or the reverse, is invisible.

Files: `outrage_by_lane_ci.csv`, `format_hook_shares.csv`, `formats.parquet`, `hook_classifier.json`, `labels.csv`.
"""


def doc_caps_words() -> str:
    from pipeline_titles.textstats import CAPS_STYLES
    cp = rd("caps_profile.csv"); tw = rd("top_words.csv"); acr = (A / "caps_acronyms.txt").read_text().split()
    v = cp[(cp.genre == "videos") & (~cp.low_n)].sort_values("caps_any", ascending=False).copy()
    means = v[CAPS_STYLES].mean()
    lanes_mean = v.groupby("lane")[CAPS_STYLES].mean().sort_values("all_caps", ascending=False).reset_index(); lanes_mean["lane"] = lanes_mean.lane.map(lane)
    ren = {"all_caps": "ALL CAPS", "selective_caps": "selective CAPS", "title_case": "Title Case", "sentence_case": "Sentence case", "mixed_other": "mixed / other", "short_other": "short / other", "caps_any": "ALL + selective"}
    full = v[["creator", "lane", "n_titles", "caps_any"] + CAPS_STYLES].copy(); full["lane"] = full.lane.map(lane)
    t20 = tw.head(20).copy()
    return f"""# 11. Capitalisation profile, and the words titles are made of

## Capitalisation profile

**The question.** How does each channel capitalise its titles: shouting in ALL CAPS, emphasising single words, Title Case, or sentence case?

### The finding in one paragraph

Averaged over the {len(v)} ranked channels (edited uploads), {pct(means['title_case'])} of titles are Title Case, {pct(means['selective_caps'])} use selective CAPS (one or more shouted words inside a normally cased title: "Trump SLAMS Judge"), {pct(means['sentence_case'])} are sentence case, {pct(means['all_caps'])} are ALL CAPS, and the rest are too short to classify or mixed. Selective capitals are the signature of the daily commentary channels: {', '.join(v.head(5).creator)} put an emphasised word in more than {pct(v.iloc[4].caps_any)} of their titles. Full ALL-CAPS titles are rarer and concentrated in a handful of channels on both sides (Jackson Hinkle, TheQuartering, the three Timcast channels, Fleccas, and the streamers Hasan Piker and Vaush); the news outlets are sentence case or Title Case, and the selective capitals they do show are mostly quoted shouted words ('GAME CHANGER': ...) rather than emphasis.

![Top 45 channels by capitals.](figures/11_caps_profile_top.png)
*The 45 channels that use ALL CAPS or selective CAPS most; the bar is the whole channel's titles.*

![Bottom 30 channels by capitals.](figures/11_caps_profile_bottom.png)
*The 30 channels using capitals least.*

![By lane.](figures/11_caps_profile_by_lane.png)
*Lane means.*

### By lane (mean of creators)

{table(lanes_mean, ['lane'] + CAPS_STYLES, fmt='{:.2f}', rename=ren)}

### Every ranked channel, sorted by ALL CAPS + selective CAPS

{table(full, ['creator', 'lane', 'n_titles', 'caps_any'] + CAPS_STYLES, fmt='{:.2f}', rename=ren)}

### Method

Each unique normalised title (brand suffixes such as "| Fox News" removed, so channel tags do not count) is classified by one rule in this order: **short / other** if it has fewer than three 2+-letter words; **ALL CAPS** if at least 90 % of its words are all-capitals; **selective CAPS** if it contains at least one all-capitals word of three or more letters that is neither a known acronym nor a generic label; **mixed / other** if it starts lower-case; **Title Case** if at least 80 % of the remaining content words (function words excluded) start with a capital; **sentence case** otherwise. Acronyms are learned from the corpus itself ({len(acr)} words that are all-capitals in at least 80 % of their non-initial occurrences in mixed-case titles, e.g. FBI, ICE, GOP, NATO, AI; the list is `caps_acronyms.txt`); the generic labels are LIVE, BREAKING, WATCH, NEW, FULL, EXCLUSIVE, UPDATE, REPLAY and the like. Shares are over a channel's unique titles per genre.

### Limitations

- Any single emphasised word makes a title "selective CAPS", so the category mixes light emphasis ("This Is INSANE") with heavy ("MAGA MELTDOWN as Trump LOSES IT").
- The acronym exemption is corpus-learned: a word that is usually shouted (e.g. a name a channel always capitalises) can be learned as an acronym and stop counting, and a genuine acronym rarely written in mixed case can count as emphasis.
- Title Case vs sentence case is a threshold (80 % of content words capitalised); headlines dense with proper nouns can tip over it.
- Computed on normalised titles; a channel whose only capitals were in a stripped show-name suffix scores lower than its raw titles look.

## The twenty most frequent non-stopwords

**The question.** What words do titles actually use most?

{table(t20, ['rank_balanced', 'word', 'balanced_share_of_titles', 'creators_using', 'raw_pooled_share_of_titles', 'rank_raw'], fmt='{:.3f}')}

![Top words.](figures/11_top_words.png)

Trump is in a seventh of the average creator's titles and in {pct(float(tw.loc[tw.word == 'trump', 'raw_pooled_share_of_titles'].iloc[0]))} of all titles; the war words (iran, war, israel) and the year's institutions (ice, epstein, maga, democrats) follow. The two columns disagree where the big news channels differ from everyone else: "says" is the 4th most frequent word in the raw pool (wire headlinese: "X says Y") but only 11th when creators count equally; "debate", "black" and "truth" are commentary words that the pooled count buries.

### Method

Tokens are lower-cased words from the normalised title with curly apostrophes normalised and possessive "'s" removed (so "Trump's" counts as "trump"); stopwords are the pipeline list plus scikit-learn's English list plus a few title-furniture words (live, new, news, video, full, show, watch, podcast, vs, ft, ep). The creator-balanced share is, for each ranked creator with edited uploads, the share of its unique titles containing the word, averaged over creators; the raw share pools all unique edited-upload titles. The top 400 words by raw count were scored; `top_words.csv` has all of them.

### Limitations

Unigrams only, so "white house" is "white" and "house"; hyphenated and censored words ("f***ing") are split by the tokeniser; the stopword list is a choice (it removes "says"-type words only when they are in the list, which "says" is not).

Files: `caps_profile.csv`, `caps_acronyms.txt`, `top_words.csv`.
"""


def doc_arousal() -> str:
    ar = rd("arousal_index.csv"); lab = rd("labels.csv"); dims = rd("dimensions.csv")
    v = ar[(ar.genre == "videos") & (~ar.low_n)].sort_values("arousal_index", ascending=False).copy()
    # validation against the LLM 'sensational' rating and the tone / caps factors
    lm = lab[lab.genre == "videos"].groupby("creator").agg(n=("sensational", "size"), sensational=("sensational", "mean")).reset_index()
    lm = lm[lm.n >= 5].merge(v[["creator", "arousal_index"]], on="creator")
    r_sens = lm.sensational.corr(lm.arousal_index, method="spearman")
    dv = dims[(dims.genre == "videos")].merge(v[["creator", "arousal_index"]], on="creator")
    r_f1 = dv["F1_controlled"].corr(dv.arousal_index, method="spearman"); r_f9 = dv["F9_controlled"].corr(dv.arousal_index, method="spearman")
    v["lane"] = v.lane.map(lane)
    cols = ["rank_in_genre", "creator", "lane", "arousal_index", "caps_share", "exclamations", "power_words", "emoji", "vader_intensity", "n_titles"]
    ren = {"rank_in_genre": "rank", "arousal_index": "index (0-1)", "caps_share": "ALL-CAPS word share", "exclamations": "! per title", "power_words": "power words per title", "emoji": "emoji per title", "vader_intensity": "VADER intensity"}
    lanes_ = v.groupby("lane").arousal_index.agg(["median", "mean", "min", "max", "size"]).sort_values("median", ascending=False).reset_index()
    return f"""# 12. Arousal index by channel

**The question.** On one 0-1 scale, how emotionally charged is each channel's titling: capitals, exclamation marks, power words, emoji and sentiment intensity together?

## The finding in one paragraph

The index runs from {v.iloc[0].creator} ({v.iloc[0].arousal_index:.2f}) at the top, followed by {', '.join(v.iloc[1:5].creator)}, to {', '.join(v.tail(4).creator[::-1])} at the bottom (all under 0.02). The top of the ranking is the daily outrage channels of both sides plus the MeidasTouch network; the bottom is magazines, wires and interview podcasts. By lane, left commentary has the highest median, then legal commentary and streamers; the press and legacy TV the lowest. The index agrees with the independent measures it should agree with: Spearman {r_sens:+.2f} with the LLM rater's *sensational* score aggregated per channel, {r_f1:+.2f} with the tone factor (positive = calm) and {r_f9:+.2f} with the ALL-CAPS factor of document 3.

![Arousal index, every ranked channel.](figures/12_arousal_ranked.png)
*All ranked channels with edited uploads, highest first; colour = lane family.*

![Arousal by lane.](figures/12_arousal_by_lane.png)

## By lane

{table(lanes_, ['lane', 'size', 'median', 'mean', 'min', 'max'], fmt='{:.2f}', rename={'size': 'n_creators'})}

## Every ranked channel (edited uploads), with the raw components

{table(v, cols, fmt='{:.3f}', rename=ren)}

Live VODs and low-n channels are in `arousal_index.csv` (column `genre`, flag `low_n`).

## Method

For each unique title: (1) the share of 2+-letter words in ALL CAPS; (2) the number of exclamation marks, capped at three; (3) power words, the count of shock words, violence/outrage verbs and intensifiers from the pipeline lexicons ("insane", "slams", "exposed", "absolutely"); (4) emoji characters; (5) VADER intensity, the positive plus negative sentiment shares (arousal, not valence: "AMAZING" counts as much as "DISGUSTING"). Each component is averaged per channel x genre; across the ranked channels of a genre it is winsorised at the 2nd and 98th percentile and min-max scaled to 0-1; the index is the mean of the five scaled components. Ranks and percentiles are within genre.

## Limitations

- Equal weights are a choice; a channel that only shouts and a channel that only exclaims can tie.
- Emoji are rare (most channels average zero per title), so that component mostly separates a few emoji users (MeidasTouch, Benny Johnson, Pondering Politics) from everyone else.
- Min-max scaling depends on the extremes even after winsorising; the ranking is stable, the spacing between values is not meaningful beyond ordering.
- VADER is a general-purpose sentiment lexicon on ten-word texts; "war" or "shooting" raise intensity in a wire headline as they do in a rant.
- Computed on normalised titles (brand suffixes removed).

Files: `arousal_index.csv`.
"""


def doc_keywords() -> str:
    kw = rd("signature_keywords.csv"); lanes_ = rd("lanes.csv")
    top5 = kw[kw["rank"] <= 5].groupby("creator").apply(lambda g: ", ".join(f"{w} ({z:.0f})" for w, z in zip(g.word, g.z)), include_groups=False).rename("top 5 (z)").reset_index()
    top5 = top5.merge(lanes_[["creator", "lane", "channel_name"]], on="creator").sort_values("creator", key=lambda s: s.str.lower())
    top5["lane"] = top5.lane.map(lane)
    ex = kw[kw.creator.isin(["@HasanAbi", "@BenShapiro", "@Reuters", "@MeidasTouch", "@CNN", "@joerogan"])].groupby("creator").apply(lambda g: ", ".join(g.word), include_groups=False)
    return f"""# 13. Signature title keywords per channel

**The question.** Which words does each channel use far more than everyone else?

## The finding in one paragraph

Each channel's signature is scored by weighted log-odds against all other channels' titles, with a prior that shrinks rare words, so the list is the vocabulary a channel *over-uses*, not merely uses. For most channels the top of the list is its own furniture (host names, show segments, a recurring guest), which is expected and is itself a style fact: {ex.get('@BenShapiro', '')[:60]} for Ben Shapiro, {ex.get('@HasanAbi', '')[:60]} for Hasan Piker. Below that, the lists separate beats and registers: {ex.get('@Reuters', '')[:70]} for Reuters, {ex.get('@MeidasTouch', '')[:70]} for MeidasTouch. The top five per channel are below; the top ten with counts are in `signature_keywords.csv` and on each creator's card.

## Every channel's top five (alphabetical)

`z` is the log-odds z-score; larger = more distinctive. Words appear only if the channel used them at least three times.

{table(top5, ['creator', 'channel_name', 'lane', 'top 5 (z)'])}

## Method

Tokens are lower-cased words from the normalised title (curly apostrophes normalised, possessive "'s" removed, the vocabulary stopword list of document 11 removed), pooled over a channel's unique titles in both genres. For each channel the weighted log-odds ratio of every word against all other channels' titles is computed with an informative Dirichlet prior proportional to the pooled corpus frequencies (Monroe, Colaresi and Quinn 2008, "Fightin' Words"), alpha0 = 500, and ranked by the z-score (log-odds divided by its approximate standard error). The top ten with at least three uses by the channel are kept.

## Limitations

- Show and host names survive when they were not stripped in Stage 0 (only patterns above the 20 % rule were), so some lists begin with the channel's own name; that is a real over-use, but not an interesting one.
- Small channels have few words that reach the count floor; their lists are short or dominated by one series.
- Unigrams only, and the prior's strength (alpha0) trades distinctiveness against rarity: a larger alpha0 would push common words up, a smaller one rare words.
- The comparison set is "all other channels", so a word every commentary channel uses (trump, maga) is not a signature for any of them, by design.

Files: `signature_keywords.csv`.
"""


def doc_index() -> str:
    hl = (REPORTS_DIR / "headlines.md").read_text(encoding="utf-8") if (REPORTS_DIR / "headlines.md").exists() else ""
    return f"""# Political YouTube Title Stylometry: the results

Every video title that 274 political-media creators published between 2026-01-01 and 2026-09-14 (309,596 titles), described along data-driven style dimensions, controlled for topic, clustered into a landscape, tracked month by month and tested against views. The write-up is split by question; each document explains one finding, shows the tables that carry it and lists its caveats.

| document | the question it answers |
|---|---|
| [1. Corpus and lanes](01_corpus_and_lanes.md) | what is being analysed, what was stripped from titles, how the corpus was balanced, and the lane proposal |
| [2. Topics](02_topics.md) | what they talk about, month by month, and why topic has to be controlled |
| [3. Style dimensions](03_style_dimensions.md) | the twelve dimensions titles vary along, what each means, which lanes sit where, and whether "Sensational / Critical / Analytical / Educational / Conversational / Humour" survive |
| [4. Formats and hooks](04_formats_and_hooks.md) | questions, LIVE labels, episodes, guests, reactions, confrontations; the outrage frame; why curiosity and humour could not be measured |
| [5. The landscape](05_landscape.md) | who titles like whom, lanes vs style, nearest neighbours, organisations, who gets named, shared titles and templates |
| [6. Drift](06_drift.md) | how titles changed from January to September |
| [7. Views](07_views.md) | whether style predicts views within a channel; how concentrated hits are |
| [8. Null results and caveats](08_null_results_and_caveats.md) | what did not show up, and what to distrust |

Question documents, each with its method and limitations:

| document | the question |
|---|---|
| [9. Stylistic twins](09_stylistic_twins.md) | which left and right commentary creators title the same way |
| [10. Outrage by lane](10_outrage_by_lane.md) | how much of political YouTube is framed as outrage, lane by lane, with confidence intervals |
| [11. Capitalisation and vocabulary](11_capitalisation_and_vocabulary.md) | each channel's capitalisation profile; the twenty most frequent words |
| [12. Arousal index](12_arousal_index.md) | a 0-1 emotional-charge index for every channel, with its components |
| [13. Signature keywords](13_signature_keywords.md) | the words each channel over-uses relative to all others |
| [14. Political leaning from titles](14_political_leaning.md) | three models (two local, one frontier) label titles left / right / neither: what each sees, channel scores against the channels' own descriptions and the lanes, and the words behind each label |

Alongside: [`title_stylometry.html`](title_stylometry.html) (the interactive page: creator selector, profile cards, and the two landscape maps with names on hover and each creator's neighbours drawn in; open it directly in a browser), [`figures/`](figures/) (the static figures used in the documents), [`cards/`](cards/) (one Markdown card per creator), [`methods_appendix.md`](methods_appendix.md) (every preprocessing step, lexicon, loading, validation number, prompt and runtime), and [`all_tables.md`](all_tables.md) (the reference dump of every table in one file).

## The findings, one paragraph per stage

{hl}
"""


def write_all() -> None:
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    docs = {"01_corpus_and_lanes.md": doc_corpus, "02_topics.md": doc_topics, "03_style_dimensions.md": doc_dimensions,
            "04_formats_and_hooks.md": doc_formats, "05_landscape.md": doc_landscape, "06_drift.md": doc_drift,
            "07_views.md": doc_views, "08_null_results_and_caveats.md": doc_nulls, "09_stylistic_twins.md": doc_twins,
            "10_outrage_by_lane.md": doc_outrage, "11_capitalisation_and_vocabulary.md": doc_caps_words, "12_arousal_index.md": doc_arousal,
            "13_signature_keywords.md": doc_keywords, "README.md": doc_index}
    if (A / "leaning_by_creator.csv").exists():
        from pipeline_titles.report_leaning import doc_leaning
        docs["14_political_leaning.md"] = doc_leaning
    for name, fn in docs.items():
        (REPORTS_DIR / name).write_text(fn(), encoding="utf-8")
