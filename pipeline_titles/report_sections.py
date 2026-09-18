"""Sectioned write-up: one document per question, each with the finding explained
in prose, the few tables that carry it, and its caveats. Written by
pipeline_titles.report alongside the reference dump (all_tables.md).

    reports/README.md                    index and how to read the set
    reports/01_corpus.md                 what the corpus is, what was normalised, the creator table
    reports/02_topics.md                 what they talk about
    reports/04_formats_and_hooks.md      question / LIVE / episode formats; outrage, curiosity, humour
    reports/05_landscape.md              who titles like whom; channel groups vs style; who gets named; shared titles
    reports/06_drift.md                  month-by-month change
    reports/07_views.md         Zipf's law (words and views) and views over time, by channel group,
                                         title label and capitalisation style
    reports/08_null_results_and_caveats.md   what did not show up, and what to distrust
    reports/09..14                       the question documents (report_leaning.py renders 14)

The only grouping of channels anywhere in the set is the left / neutral / right channel
group from the leaning stage (document 14): each channel's score over its sampled
titles, thresholds +-0.05. Titles are grouped two ways: by the judge's left / neither /
right label (the sampled titles) and by capitalisation style (every title).

The interpretive prose reflects the 2026-09-14 run; every number in it is read from
the tables at render time, so a re-run keeps the numbers current but the wording
should be re-checked.
"""

from __future__ import annotations

import json
import re

import numpy as np
import pandas as pd

from pipeline_titles.common import ANALYSIS_DIR as A, GENRES, GROUPS, GROUP_LABEL, REPORTS_DIR, read_jsonl, RUNTIMES

HOOKS = ["curiosity_gap", "outrage", "humor"]
FORMATS = ["question", "breaking_live", "episode_show", "interview_guest", "reaction", "confrontation", "listicle", "howto_explainer"]
CAPS_LABEL = {"all_caps": "ALL CAPS", "selective_caps": "selective CAPS", "title_case": "Title Case", "sentence_case": "Sentence case",
              "mixed_other": "mixed / other", "short_other": "short / other", "caps_any": "ALL + selective"}
CAPS_ORDER = ["all_caps", "selective_caps", "title_case", "sentence_case", "mixed_other", "short_other"]
TITLE_LABELS = ["left", "neither", "right"]


def group(g: str) -> str:
    return GROUP_LABEL.get(g, g)


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


def _groups_only(df: pd.DataFrame, col: str = "group") -> pd.DataFrame:
    """Rows of the three scored groups, in left / neutral / right order."""
    d = df[df[col].isin(GROUPS)].copy()
    d["_o"] = d[col].map({g: i for i, g in enumerate(GROUPS)})
    return d.sort_values("_o").drop(columns="_o")


def _lg(df: pd.DataFrame, col: str = "group") -> pd.DataFrame:
    d = _groups_only(df, col).copy(); d[col] = d[col].map(group)
    return d


GROUP_NOTE = ("Channel groups are the left / neutral / right groups of document 14: each channel's score = (right − left) / titles over its "
              "sampled titles as labelled by the judge, sorted at ±0.05. A channel's group says how its *titles* read, not what its host believes.")


# --------------------------------------------------------------------------- #
def doc_corpus() -> str:
    summ = rd("creator_genre_summary.csv"); cr = rd("creators.csv"); sp = rd("stripped_patterns.csv"); z = rd("zipf_check.csv")
    lb = rd("leaning_by_creator.csv")[["creator", "group", "score", "n_titles"]]
    cr = cr.merge(lb, on="creator", how="left").fillna({"group": "unscored"})
    n_rows, n_uniq = int(summ.n_rows.sum()), int(summ.n_unique.sum())
    top4 = summ[summ.creator.isin(["@Firstpost", "@ANINewsIndia", "@TimesNowWorld", "@timesofindia"])].n_rows.sum()
    g = summ.groupby("genre").agg(groups=("creator", "size"), rows=("n_rows", "sum"), unique=("n_unique", "sum"), balanced=("n_balanced", "sum"),
                                  low_n=("low_n", "sum"), median_size=("n_unique", "median"), max_size=("n_unique", "max")).reset_index()
    zc = z[z.level == "creator_level_mean"].set_index("text").zipf_exponent
    gc = summ.merge(cr[["creator", "group"]], on="creator").groupby("group").agg(channels=("creator", "nunique"), unique_titles=("n_unique", "sum")).reindex(list(GROUPS)).reset_index()
    gc["group"] = gc.group.map(group)
    n_orgs = int((cr.groupby("organisation").size() > 1).sum()); n_clip = int(cr.clipper.astype(str).str.lower().eq("true").sum())
    out = f"""# 1. The corpus, what was normalised, and the creator table

**The question.** What exactly is being analysed, and what had to be done to it before any style measure means anything?

## The finding in one paragraph

The corpus is {n_rows:,} titles from {summ.creator.nunique()} creators, but it is wildly uneven: four Indian news channels (Firstpost, ANI, Times Now, Times of India) hold {top4:,} of them, the median creator x genre has {int(summ.n_unique.median())} titles and the largest has {int(summ.n_unique.max()):,}. {n_rows - n_uniq:,} rows ({pct((n_rows - n_uniq) / n_rows, 1)}) are verbatim repeats within a creator x genre, almost all live-broadcast loops on news stream tabs. So three rules run through everything downstream: edited uploads (`videos`) and live VODs (`streams`) are never pooled; a creator x genre with fewer than 50 unique titles is reported but never ranked ({int(summ.low_n.sum())} of {len(summ)} groups); and any statistic that pools titles uses a creator-balanced subset capped at 2,500 titles per creator x genre ({int(summ.n_balanced.sum()):,} titles), while corpus- and group-level figures are means of creator-level values.

## Size by genre

{table(g, fmt="{:.0f}")}

The `streams` genre is small and thin: {int(g.loc[g.genre == 'streams', 'low_n'].iloc[0])} of its {int(g.loc[g.genre == 'streams', 'groups'].iloc[0])} groups are low-n, so stream-level results in the later documents rest on roughly {int(g.loc[g.genre == 'streams', 'groups'].iloc[0]) - int(g.loc[g.genre == 'streams', 'low_n'].iloc[0])} creators.

![Creator x genre group sizes on a log scale, with the low-n line (50) and the balanced cap (2,500).](figures/01_group_sizes.png)
*Creator x genre group sizes on a log scale, with the low-n line (50) and the balanced cap (2,500).*

## What was stripped from titles, and why it matters

Titles carry brand furniture that would otherwise dominate any vocabulary-based measure: "| BBC News" on {int(sp[(sp.creator == '@BBCNews') & (sp.kind == 'suffix')]['count'].max()):,} BBC titles, "Ep. 1837"-style episode numbers on the Daily Wire shows, date stamps on RSBN and Newsmax streams, "N18G" on Firstpost. The rule was mechanical and per creator: any delimited leading or trailing segment (or colon label, bracket tag, hashtag) that occurs in more than 20 % of that creator's titles is a brand pattern and is removed; episode numbers and date stamps are removed from the edges regardless. Generic format labels (LIVE, BREAKING, WATCH) are never stripped because they are themselves a style choice measured later. {len(sp)} patterns were stripped across {sp.groupby(['creator', 'genre']).ngroups} creator x genre groups; {int((rd('creator_genre_summary.csv').n_norm_fallback).sum())} titles consisted of nothing but brand text and were kept as they were. The full list is `stripped_patterns.csv`; the fifteen most frequent:

{table(sp.sort_values('count', ascending=False).head(15), ['creator', 'genre', 'kind', 'pattern', 'count', 'share', 'example'], fmt='{:.2f}')}

**Check that it worked.** If stripping removed the show-brand head of each creator's vocabulary, the creator-level Zipf exponent should fall (the most frequent tokens were the brand) and the top-token share should drop most for show-branded channels. Both happened: the mean creator-level Zipf exponent went from {zc['raw']:.3f} (raw) to {zc['normalised']:.3f} (normalised), and the share of the single most frequent token fell most for Joe Rogan (from 14 % to 4 %: "Joe Rogan Experience #"), Denims, The Economist and the Hasan fan channels. The pooled corpus exponent barely moves (the brand tokens are a small share of a 189k-title pool), which is exactly why the report uses creator-level figures. Document 7 takes Zipf's law further.

## The creator table, and the one grouping used everywhere

`creators.csv` holds one row per creator: channel name, platform, `organisation` and `clipper`, subscribers, title counts and a short note. `organisation` groups sister channels of one outlet (Fox News / Fox News Clips, Timcast x3, NYT x4 incl. Ezra Klein, TYT / The Damage Report / Rebel HQ, MeidasTouch / Legal AF / Katie Phang / Michael Cohen, Daily Wire x4, Blaze Media x2, and so on: {n_orgs} organisations with more than one channel); same-organisation cross-posts (TYT and The Damage Report share 913 titles verbatim) are removed from every similarity calculation. `clipper` marks the {n_clip} channels whose titles are written by fans or an editing team (the Hasan, Destiny and Vaush clip channels, Fox News Clips, Lauren Chen Clips, Candace Clips, Denims, Asmongold TV, the Hasan VOD channel); they are kept as their own group so a fan editor's style is never attributed to the creator.

No channel is assigned a category by hand. The one between-channel grouping in this report is the **channel group** of document 14: a frontier model labelled a sample of each channel's titles left / right / neither from the title text alone, each channel's score is (right − left) / titles, and the score sorts the channels into left (below −0.05), neutral and right (above +0.05):

![Unique titles and channels per channel group.](figures/01_corpus_by_group.png)
*Unique titles and channels per channel group.*

{table(gc, fmt='{:.0f}')}

The group is a description of how a channel's titles read, produced by the same measurement as everything else here; it is not an editorial judgement about the channel, and document 14 gives its reliability (split-half Spearman of the score {float(rd('leaning_split_half.csv').split_half_spearman_mean.iloc[0]):.2f}) and its limits. Every "by group" table in documents 2-13 is a mean or median over the ranked channels of a group, never a pool of their titles.

Files: `creator_genre_summary.csv`, `stripped_patterns.csv`, `zipf_check.csv`, `zipf_check_creators.csv`, `creators.csv`, `leaning_by_creator.csv`.
"""
    return out


def doc_topics() -> str:
    tl = rd("topic_labels.csv"); bl = rd("topic_by_group.csv"); spk = rd("topic_spikes.csv"); pol = rd("creator_political_share.csv"); cc = rd("cluster_comparison.csv")
    bl = bl[bl.group.isin(GROUPS)]
    t1 = {}
    for r in read_jsonl(RUNTIMES):
        if r["stage"] == "stage1_topics":
            t1.update(r)
    share = bl.groupby("topic_id")["mean_creator_share"].mean().rename("balanced_share")
    tl2 = tl.merge(share, on="topic_id").sort_values("balanced_share", ascending=False)
    big = tl2.head(12)
    pv = pol[(pol.n_unique >= 50) & (pol.genre == "videos")]
    pl = _lg(pv.groupby("group").political_share.agg(["mean", "median", "size"]).reset_index())
    v = bl[bl.genre == "videos"].sort_values("mean_creator_share", ascending=False).groupby("group").head(4)
    v = _lg(v)
    sp3 = spk.sort_values(["month", "z_vs_own_months"], ascending=[True, False]).groupby("month").head(2)
    ari = cc[(cc.genre == "videos") & (cc.titles == "all")].iloc[0]
    n_big12 = int((big.n_creators >= 100).sum())
    top_of = {g: v[v.group == group(g)].iloc[0].label for g in GROUPS}
    war = tl.loc[tl.topic_id == 0, "label"].iloc[0]
    lead = ("The war story leads in all three groups." if all(t == war for t in top_of.values()) else
            "The war story leads in the " + " and ".join(group(g) for g in GROUPS if top_of[g] == war) + "; the " + " and ".join(f"{group(g)} put \"{top_of[g]}\" first" for g in GROUPS if top_of[g] != war) + ", with the war second.")
    out = f"""# 2. Topics: what they talk about

**The question.** What stories fill the titles, who covers what, and how much of the corpus is politics at all? The topic assignment is also the control variable for every style result, so it has to be sound.

## The finding in one paragraph

A BERTopic model fitted on a {t1.get('fit_n', 0):,}-title creator-stratified sample found {t1.get('hdbscan_topics', '?')} topics; every title was then assigned to its nearest topic centroid ({t1.get('centroid_hdbscan_agreement', 0):.0%} agreement with HDBSCAN's own labels on cluster members, {t1.get('weak_share', 0):.0%} weak assignments). One story dominates 2026: the Iran war and the Strait of Hormuz, {int(tl.loc[tl.topic_id == 0, 'n_unique_all'].iloc[0]):,} unique titles across {int(tl.loc[tl.topic_id == 0, 'n_creators'].iloc[0])} of 274 creators, with a second energy-markets topic on the same war. {n_big12} of the twelve largest topics are each shared by 100 or more of the 274 creators. That is the central fact for everything after this document: the whole landscape covered the same stories, so raw vocabulary similarity between two channels mostly measures the news cycle, not their style. It also shows in the clustering: creators grouped by topic mix do not line up with the left / neutral / right channel groups (adjusted Rand index {ari.ari_topic_vs_group:.3f} for edited uploads).

## The largest topics (creator-balanced share)

![The fifteen largest topics by creator-balanced share; blue = political, yellow = non-political.](figures/02_top_topics.png)
*The fifteen largest topics by creator-balanced share; blue = political, yellow = non-political.*

{table(big, ['topic_id', 'label', 'political', 'balanced_share', 'n_unique_all', 'n_creators', 'top_terms'], fmt='{:.3f}')}

`balanced_share` is the mean over the six channel group x genre cells of the mean creator share, so a topic that four Indian channels post 8,000 times does not outrank one that 200 channels each post a few times (a topic that is large in the thin stream cells can rank above its upload count, as topic 59 does). The "Shocking Events and Reactions" topic is not a story: it is the cluster of content-free exclamations ("HOLY SH*T", "THIS IS INSANE..") that streamers and commentators use as titles, and it is the seed of the shared-title finding in document 5.

## Political or not

![Political share of a creator's titles, by channel group.](figures/02_political_share_by_group.png)
*Political share of a creator's titles, by channel group (dots = creators, bar = median).*

{int(tl.political.sum())} of {len(tl)} topics were tagged political by the labelling model (politics, government, elections, war, courts, political figures, the culture war); the {int((~tl.political).sum())} non-political topics are crime trials (Nancy Guthrie, Lindsay Clancy, the Brown University shooting), weather and disasters, sport (World Cup, MMA), tech and business, and a few channel-specific series. The tagging is generous, and the political share of a creator's unique titles is therefore high everywhere. The neutral channels, whose titles the judge mostly read as "neither", are also the ones with the most non-political subjects (crime, weather, sport, tech: the news outlets); the left and right groups are political almost throughout:

{table(pl, fmt='{:.2f}', rename={'size': 'n_creators', 'mean': 'mean political share', 'median': 'median political share'})}

Document 5 repeats the whole landscape analysis on political titles only; the conclusions do not change.

## Topic share by channel group (top 4 per group, edited uploads)

{table(v, ['group', 'label', 'mean_creator_share', 'n_creators'], fmt='{:.3f}')}

{lead} Beyond it the groups' attention differs at the margin rather than in kind: what separates them in document 14 is the wording about the shared subjects, not the subjects.

## The month-by-month story

![Monthly creator-balanced share of the eight largest topics; the hollow marker is the half month of September.](figures/02_topic_timeline.png)
*Monthly creator-balanced share of the eight largest topics; the hollow marker is the half month of September.*

For each month the topics that rose most against their own nine-month mean (creator-balanced), with the entities named in that month's titles:

{table(sp3, ['month', 'label', 'z_vs_own_months', 'share_month', 'top_entities'], fmt='{:.3f}')}

Read left to right and 2026 tells itself: the Bondi Beach attack and a Trump Christmas in January; the Don Lemon arrest and the Alex Pretti shooting in February; the State of the Union and the tariff case in March; the Joe Kent resignation, the Artemis II mission and the No Kings protests in April; the Correspondents' Dinner shooting in May; the Massie primary and the Karmelo Anthony verdict in June; the 250th anniversary in July; the Fauci testimony and the Blanche confirmation in August; 9/11 at 25 and Nepal's floods in September (a half month). The full list with three example titles each is `topic_spikes.csv`.

## Caveats

- The topic labels and the political flag come from a local 14B model reading the top terms and eight example titles; the labels are readable but a few are odd ("Hasanabi Reacts to Hasan" is a fan-channel formula, not a subject) and the political flag errs towards "political". Both live in `topic_labels.csv` and can be edited; the political-only analyses re-run from `landscape`.
- {t1.get('outlier_share', 0):.0%} of the fit sample were HDBSCAN outliers; nearest-centroid assignment gives them a topic anyway, and {t1.get('weak_share', 0):.0%} of all titles sit below the 10th-percentile similarity of genuine members. Those weak assignments are flagged per title in `topics.csv`.
- {GROUP_NOTE}

Files: `topics.csv` (title -> topic), `topic_labels.csv`, `creator_topic_mix.csv`, `topic_by_group.csv`, `topic_timeline.csv`, `topic_spikes.csv`, `creator_political_share.csv`.
"""
    return out


def doc_formats() -> str:
    hk = json.loads((A / "hook_classifier.json").read_text()); sh = rd("format_hook_shares.csv"); ag = rd("format_agreement.csv"); ex = rd("format_examples.csv")
    lv = _lg(sh[(sh.level == "group_mean_of_creators") & (sh.genre == "videos")])
    ls = _lg(sh[(sh.level == "group_mean_of_creators") & (sh.genre == "streams")])
    cr = sh[(sh.level == "creator") & (~sh.low_n.astype(str).str.lower().eq("true")) & (sh.genre == "videos") & sh.group.isin(GROUPS)]
    spread = _lg(cr.groupby("group").outrage.agg(["median", lambda s: s.quantile(.25), lambda s: s.quantile(.75), "min", "max", "size"]).reset_index())
    spread.columns = ["group", "median", "q25", "q75", "min", "max", "n_creators"]
    m = hk["hooks"]
    lab = rd("labels.csv")
    o = lv.set_index("group").outrage
    out = f"""# 4. Formats and hooks

**The question.** Which structural formats do creators use (questions, LIVE labels, episode numbering, guests, reactions, confrontations, listicles, explainers), and which semantic hooks (curiosity gap, outrage frame, humour)?

## The finding in one paragraph

The outrage frame is the landscape's default hook, not a niche device. The rating model flagged {pct(lab.outrage.mean())} of a 3,000-title creator-stratified sample as framing their subject as outrageous, scandalous or threatening, and a classifier trained on those labels reproduces the judgement well on held-out titles (accuracy {m['outrage']['holdout_accuracy']:.2f}, AUC {m['outrage']['holdout_auc']:.2f}, kappa {m['outrage']['holdout_kappa']:.2f}). Applied to every title, it covers {pct(o['left channels'])} of the average left channel's edited uploads, {pct(o['right channels'])} of the average right channel's and {pct(o['neutral channels'])} of the average neutral channel's: the frame belongs to partisan titling on both sides, and the neutral group, which is mostly news outlets, uses it least. The two other hooks could not be measured: the rater found a curiosity gap in {pct(lab.curiosity_gap.mean(), 1)} of titles and humour in {pct(lab.humor.mean(), 1)}, far too few positives to learn from (held-out F1 {m['curiosity_gap']['holdout_f1']:.2f} and {m['humor']['holdout_f1']:.2f}). Treat both as *unmeasured*, not absent (see document 8).

## Formats by channel group (share of a creator's titles, mean over creators; edited uploads)

![Structural formats by channel group, edited uploads.](figures/04_formats_heatmap.png)
*Structural formats by channel group, edited uploads.*

{table(lv, ['group', 'n_creators'] + FORMATS, fmt='{:.2f}')}

Questions run at the same rate in all three groups; episode numbering and how-to / explainer wording are a little more common on the right, guest formats a little more in the neutral and left groups ({pct(float(lv.loc[lv.group == 'neutral channels', 'interview_guest'].iloc[0]))}, {pct(float(lv.loc[lv.group == 'left channels', 'interview_guest'].iloc[0]))}, {pct(float(lv.loc[lv.group == 'right channels', 'interview_guest'].iloc[0]))} on the right), and none of the structural formats separates the groups the way the outrage hook does. Live VODs look different again: LIVE/BREAKING labels sit on {pct(float(ls.loc[ls.group == 'neutral channels', 'breaking_live'].iloc[0]))} of the neutral group's stream titles (the wires' rolling broadcasts), confrontation on {pct(float(ls.loc[ls.group == 'left channels', 'confrontation'].iloc[0]))} of the left group's (the debate streamers):

{table(ls, ['group', 'n_creators', 'question', 'breaking_live', 'episode_show', 'interview_guest', 'confrontation', 'outrage'], fmt='{:.2f}')}

## The outrage hook by channel group (edited uploads)

![Outrage-frame share by channel group, edited uploads (left) and live VODs (right).](figures/04_outrage_by_group.png)
*Outrage-frame share by channel group, edited uploads (left) and live VODs (right); dots are creators, the bar is the group median.*

{table(spread, ['group', 'n_creators', 'median', 'q25', 'q75', 'min', 'max'], fmt='{:.2f}')}

Within every group the creator-to-creator spread is wide (the quartiles above): the group is a weak predictor of any one channel. The gradient across groups is the same one the tone factor of the style model finds, measured a second way; the two measures are not independent (the classifier sees the same words the lexicon counts), but they were built from different sources, the tone factor from word lists and sentiment, the hook from a model reading whole titles.

## Examples (corpus-wide, three per category)

{table(ex[ex.scope == 'corpus'], ['category', 'creator', 'title'])}

## Do the rules agree with the model?

Formats are regexes on the raw title (the exact patterns are in `format_rules.csv`); the rater also gave each sampled title one format label. Where both apply:

{table(ag[ag.category.isin(FORMATS)], ['category', 'rule_positives', 'llm_positives', 'precision_rule_vs_llm', 'recall_rule_vs_llm', 'kappa'], fmt='{:.2f}')}

The rules fire far more often than the model's single label for interview_guest and howto_explainer (the rules count "with a name" and "why"; the model picks one dominant format per title), so the rule shares above are upper bounds for those two categories. Question, breaking/live and episode formats agree well.

{GROUP_NOTE}

Files: `formats.parquet` (per title), `format_hook_shares.csv`, `format_examples.csv`, `format_rules.csv`, `format_agreement.csv`, `hook_classifier.json`.
"""
    return out


def doc_landscape() -> str:
    cc = rd("cluster_comparison.csv"); coh = rd("group_style_cohesion.csv"); dis = rd("disagreements_group_style.csv"); ent = rd("entities_top.csv")
    st = rd("shared_titles.csv"); tp = rd("shared_templates.csv"); nn = rd("neighbours_style.csv"); orgs = rd("org_style.csv")
    cross = st[~st.same_organisation_only]
    cv = _lg(coh[(coh.titles == "all") & (coh.genre == "videos")])
    dd = dis[(dis.genre == "videos") & (dis.titles == "all")]
    split = _lg(dd[dd.kind.str.startswith("channel group")])
    spans = dd[dd.kind.str.startswith("style")].sort_values("n_creators", ascending=False)
    nnv = nn[(nn.titles == "all") & (nn.genre == "videos")].set_index("creator")
    picks = ["@HasanAbi", "@BenShapiro", "@FoxNews", "@MeidasTouch", "@TuckerCarlson", "@joerogan", "@Reuters", "@destiny", "@bennyjohnson", "@CNN"]
    nrows = [{"creator": c, "group": nnv.loc[c, "group"], "five nearest in style": ", ".join(f"{nnv.loc[c, f'nn{i}']} [{nnv.loc[c, f'nn{i}_group']}]" for i in range(1, 6))} for c in picks if c in nnv.index]
    ccv = cc[["genre", "titles", "n_creators", "style_k", "style_silhouette", "topic_k", "topic_silhouette", "ari_style_vs_group", "ari_topic_vs_group", "ari_style_vs_topic"]]
    ep = ent[ent.kind == "person"].head(15); eo = ent[ent.kind == "organisation"].head(10)
    a_all = float(cc.loc[(cc.genre == 'videos') & (cc.titles == 'all'), 'ari_style_vs_group'].iloc[0]); a_pol = float(cc.loc[(cc.genre == 'videos') & (cc.titles == 'political'), 'ari_style_vs_group'].iloc[0])
    a_top = float(cc.loc[(cc.genre == 'videos') & (cc.titles == 'all'), 'ari_topic_vs_group'].iloc[0])
    tight = cv.sort_values("cohesion_ratio").iloc[0]
    gsz = rd("leaning_by_creator.csv").group.value_counts(normalize=True)
    chance_same = float((gsz ** 2).sum())        # a random pair of channels shares a group this often
    nlr = nn[(nn.titles == "all") & (nn.genre == "videos") & nn.group.isin(["left", "right"])]
    cross_nn1 = float((nlr.nn1_group != nlr.group).mean())
    cross_opp = float((sum(((nlr[f"nn{i}_group"] != nlr.group) & (nlr[f"nn{i}_group"] != "neutral")) for i in range(1, 6)) > 0).mean())
    def _ex(c):
        r = nnv.loc[c]; other = [f"{r[f'nn{i}']} ({r[f'nn{i}_group']})" for i in range(1, 6) if r[f"nn{i}_group"] not in (r.group, "neutral")]
        return f"{c} ({r.group}) has {', '.join(other)} among its five" if other else f"{c} ({r.group}) has none of the other side among its five"
    examples = "; ".join(_ex(c) for c in ("@HasanAbi", "@MeidasTouch", "@FoxNews") if c in nnv.index)
    out = f"""# 5. The landscape: who titles like whom

**The question.** Do channels whose titles read the same way politically (the left / neutral / right groups) share a *style*? Who are each creator's real neighbours in style, as opposed to in subject matter? Who gets named, and does the landscape converge on the same hooks?

## The finding in one paragraph

Political grouping predicts style almost not at all. Clustering creators in the twelve-dimensional, topic-controlled style space and comparing the clusters with the three channel groups gives an adjusted Rand index of {a_all:.3f} for edited uploads ({a_pol:.3f} on political titles only), and topic clusters do no better ({a_top:.3f}). No group holds together in style space: the tightest is {tight.group} at a cohesion ratio of {float(tight.cohesion_ratio):.2f} (members {1 - float(tight.cohesion_ratio):.0%} closer to each other than to everyone else), and the largest style cluster holds {int(spans.iloc[0].n_creators)} creators from all three groups. So the useful unit is not the group but the five nearest style neighbours on each creator's card, and those cut across politics: for {pct(cross_nn1)} of the left and right channels the single nearest neighbour is in another group, and {pct(cross_opp)} have a channel from the opposite side among their five ({examples}). The hooks converge too: {len(cross)} titles are used verbatim by creators from different organisations ("THIS IS INSANE.." by {int(cross.iloc[0].n_creators)} creators across {int(cross.iloc[0].n_groups)} groups), {pct(1 - cross.within_group.mean())} of them by channels in more than one group.

## Clusterings against the channel groups

![Style space: every ranked creator, coloured by channel group. The interactive version, with names on hover and each creator's five neighbours, is on the HTML page.](figures/05_style_map.png)
*Style space: every ranked creator, coloured by channel group. The interactive version, with names on hover and each creator's five neighbours, is on the HTML page.*

Style space: agglomerative (Ward) on z-scored topic-controlled factor scores. Topic space: average linkage on the Jensen-Shannon distance between creators' topic mixes. k chosen by silhouette; ARI = adjusted Rand index (1 = identical partitions, 0 = chance).

{table(ccv, fmt='{:.3f}')}

The low silhouettes say the same thing from the other side: neither space has well-separated groups, the creators form a continuum.

![Topic space map.](figures/05_topic_map.png)
*Topic space: MDS of the Jensen-Shannon distances between creators' topic mixes.*

![ARI and cohesion.](figures/05_groups_vs_style.png)
*Left: adjusted Rand index of the clusterings against the channel groups and against each other. Right: group cohesion in style space.*

## Do the groups cohere in style? (edited uploads)

Mean distance in style space between members of a group, over the mean distance from members to everyone else; below 1 means group-mates are closer than strangers.

{table(cv, ['group', 'n_creators', 'within_group_distance', 'between_group_distance', 'cohesion_ratio'], fmt='{:.2f}')}

## Where group and style disagree

Every group is split across style clusters; the share of a group in its own largest style cluster:

{table(split, ['group', 'n_creators', 'n_style_clusters', 'largest_cluster_share'], fmt='{:.2f}')}

Conversely, style clusters span groups: the two largest ({int(spans.iloc[0].n_creators)} and {int(spans.iloc[1].n_creators)} creators) each mix left, neutral and right channels. Full membership lists: `disagreements_group_style.csv`, `style_clusters.csv`, `topic_clusters.csv`.

## Nearest style neighbours, a sample

{table(pd.DataFrame(nrows))}

Neighbours are computed on titles with same-organisation cross-posts removed and low-n creators excluded; every creator's five style and five topic neighbours are on its card and in `neighbours_style.csv` / `neighbours_topic.csv`. The maps on the HTML page (PCA of the style space, MDS of the topic space) show the same picture: the group colours are scattered through both.

## Organisations

Sister channels do share a house style: the four MeidasTouch Network channels sit together at the outrage end of the tone factor (organisation score {float(orgs.loc[(orgs.organisation == 'MeidasTouch Network') & (orgs.genre == 'videos'), 'F1_controlled'].iloc[0]):.2f}) and high on capitals; the three Timcast channels are the most capitalised organisation ({float(orgs.loc[(orgs.organisation == 'Timcast') & (orgs.genre == 'videos'), 'F9_controlled'].iloc[0]):.2f} on F9); the four NYT channels and CBS sit at the positive/neutral end. Title-weighted organisation scores (clippers excluded) are in `org_style.csv`.

## Who gets named

![Outrage-frame ratio for the 25 most-named people: orange above the corpus baseline, blue below.](figures/05_entities_outrage.png)
*Outrage-frame ratio for the 25 most-named people: orange above the corpus baseline, blue below.*

Counted on the creator-balanced subset; people keyed by surname, so "Kirk" pools Charlie and Erika Kirk and "Trump" pools every Trump. `share_by_group` is the share of each channel group's balanced titles that names the entity; `outrage_ratio` is the outrage-frame share of titles naming the entity over the corpus share.

{table(ep, ['entity', 'n_titles_balanced', 'n_creators', 'share_by_group', 'outrage_share', 'outrage_ratio'], fmt='{:.2f}')}

{table(eo, ['entity', 'n_titles_balanced', 'n_creators', 'share_by_group', 'outrage_share', 'outrage_ratio'], fmt='{:.2f}')}

Trump is in {pct(float(ent.loc[(ent.kind == 'organisation') & (ent.entity == 'Trump'), 'share_of_balanced_titles'].iloc[0]), 1)} of balanced titles counting both tags, named by {int(ent.loc[(ent.kind == 'person') & (ent.entity == 'Trump'), 'n_creators'].iloc[0])} of 274 creators, and named most by the left group ({ent.loc[(ent.kind == 'person') & (ent.entity == 'Trump'), 'share_by_group'].iloc[0]}). Charlie Kirk and Mamdani are the right group's names, Hormuz, Putin and Netanyahu the neutral group's. The entities carrying the most outrage framing relative to baseline are the MAGA-era officials and the culture-war names; the least are the crime-story names (Nancy Guthrie, Lindsay Clancy) and institutions used as datelines (the Senate, the House, the White House). "Hormuz" is a spaCy mistake (a strait tagged as a person) left visible on purpose: entity counts from a small NER model on headline text are noisy at the margin.

## Convergent formulas

![The most shared verbatim titles across organisations.](figures/05_shared_titles.png)
*The most shared verbatim titles across organisations.*

Of {len(st):,} distinct titles (case-insensitive) used by two or more creators, {len(cross):,} cross organisations; the rest are same-outlet cross-posts (TYT / The Damage Report alone account for hundreds). The most shared:

{table(cross.head(15), ['example', 'n_creators', 'n_titles', 'n_groups', 'groups'], fmt='{:.0f}')}

These are content-free exclamations, the "Shocking Events and Reactions" topic of document 2: the same dozen phrases serve as titles on the left, the right and in between. With names and numbers masked, the shared templates are outrage frames and guest formulas:

{table(tp.head(15), ['template', 'n_creators', 'n_titles', 'n_groups', 'example'], fmt='{:.0f}')}

{pct(cross.within_group.mean())} of the shared verbatim titles are used within one channel group and {pct(tp.within_group.mean())} of the shared templates; with three groups of these sizes a random pair of channels shares a group {pct(chance_same)} of the time, so both run a little more within the camps than chance would give, the verbatim exclamations clearly and the masked templates barely. Either way the same dozen phrases and the same "<ENT> destroys <ENT>" frames serve left, neutral and right channels alike.

{GROUP_NOTE}

Files: `cluster_comparison.csv`, `group_style_cohesion.csv`, `disagreements_group_style.csv`, `style_clusters.csv`, `topic_clusters.csv`, `neighbours_style.csv`, `neighbours_topic.csv`, `map_style.csv`, `map_topic.csv`, `org_style.csv`, `entities_top.csv`, `shared_titles.csv`, `shared_templates.csv`.
"""
    return out


def doc_drift() -> str:
    names = names_of(); dl = rd("drift_group_monthly.csv"); tr = rd("drift_trends.csv"); tcl = rd("topic_change_group_monthly.csv")
    months = [m for m in dl.month.unique()]
    x = dl[(dl.genre == "videos")].copy(); x["group"] = x.group.map(lambda g: group(g) if g in GROUPS else "all channels (mean of creators)")
    order = ["all channels (mean of creators)"] + [group(g) for g in GROUPS]
    po = x.pivot(index="group", columns="month", values="outrage").reindex(order).reset_index()
    pf = x.pivot(index="group", columns="month", values="F1_controlled").reindex(order).reset_index()
    p9 = x.pivot(index="group", columns="month", values="F9_controlled").reindex(order).reset_index()
    strong = tr[(tr.level == "group") & (tr.p < 0.05) & (tr.spearman_trend.abs() >= 0.6)].copy()
    strong["group"] = strong.group.map(group); strong["measure"] = strong.measure.map(lambda m: (m.replace("_controlled", "") + ": " + short_name(m.replace("_controlled", ""), names)) if m.replace("_controlled", "") in names else m)
    js = _lg(tcl[(tcl.genre == "videos") & tcl.group.isin(GROUPS)].groupby("group").mean_js.mean().rename("mean month-to-month JS distance").reset_index())
    n_series = int((tr.level == "group").sum())
    allrow = po[po.group == order[0]].iloc[0]
    dims_ = rd("dimensions.csv"); n_neu_streams = int(((dims_.genre == "streams") & (~dims_.low_n) & (dims_.group == "neutral")).sum())
    out = f"""# 6. Drift: how titles changed from January to September

**The question.** Did the landscape's title style move over 2026, and did the three channel groups move differently? Months are the only safe unit: YouTube listing dates are month-accurate, and September covers the 1st to the 14th only (shown, never compared on volume).

## The finding in one paragraph

Not much, and not in one direction. Of {n_series} group x genre x measure series (twelve dimensions and three hooks, nine months), {len(strong)} show a monotone trend (|Spearman| >= 0.6, p < 0.05). Averaged over all creators the outrage share of edited uploads is flat ({pct(float(allrow[months[0]]))} in January, {pct(float(allrow[months[-2]]))} in August). Underneath, the left group cooled slightly (outrage {pct(float(po.loc[po.group == 'left channels', months[0]].iloc[0]))} to {pct(float(po.loc[po.group == 'left channels', months[-2]].iloc[0]))}), the right group's question framing fell over the year, and the neutral group moved on its stream titles rather than its uploads. Topic turnover is steadier than style: creators re-mix their subjects every month by a similar amount, most in the right group and least in the neutral one, whose news outlets follow the same news flow.

## Outrage share by month (edited uploads; mean of creators)

![Outrage-frame share by month, one panel per channel group, against the all-creator mean (grey dashed).](figures/06_drift_outrage.png)
*Outrage-frame share by month, one panel per channel group, against the all-creator mean (grey dashed).*

{table(po, fmt='{:.2f}')}

## Tone factor (F1, positive vs outrage; topic-controlled) by month

![The tone factor by month, per channel group.](figures/06_drift_tone.png)
*The tone factor by month, per channel group.*

{table(pf, fmt='{:.2f}')}

## ALL-CAPS factor (F9) by month

![The ALL-CAPS factor by month, per channel group.](figures/06_drift_caps.png)
*The ALL-CAPS factor by month, per channel group.*

{table(p9, fmt='{:.2f}')}

## The trends that are strong enough to report

{table(strong.sort_values(['group', 'genre']), ['group', 'genre', 'measure', 'spearman_trend', 'first_month_value', 'last_full_month_value'], fmt='{:.2f}')}

Read the stream rows with the group sizes in mind: the neutral group has {n_neu_streams} ranked stream channels, and fewer than that in any one month, so a "group trend" there can be one channel changing how it titles its streams. Per-creator trends for the thirty largest creators are in `drift_trends.csv` (level = creator) and every creator's monthly series is on its card as sparkline data (`drift_creator_monthly.csv`).

## Month-to-month topic change

Jensen-Shannon distance between a creator's topic mix in consecutive months (months with at least 15 titles), averaged per channel group over the year:

{table(js, fmt='{:.2f}')}

The ordering is the inverse of news dependence: the neutral group, which holds the wires and legacy TV, moves least because the news moves them all the same way. The monthly matrix is in `topic_change_group_monthly.csv`.

## Caveats

- Nine points per series is a short run; a trend that begins in March can look strong. The strong-trend table should be read as "worth a look", not as a finding on its own.
- September is a half month and appears in the tables for completeness; no volume comparison uses it.
- {GROUP_NOTE}

Files: `drift_group_monthly.csv`, `drift_creator_monthly.csv`, `drift_top30_monthly.csv`, `drift_trends.csv`, `topic_change_monthly.csv`, `topic_change_group_monthly.csv`.
"""
    return out


def doc_views() -> str:
    z = rd("zipf_words.csv"); zg = rd("zipf_by_group.csv"); vm = rd("views_by_month.csv"); cs = rd("caps_style_by_group.csv"); lc = rd("label_by_caps_style.csv")
    hc = rd("hit_concentration.csv"); hv = hc[hc.genre == "videos"]; zc = rd("zipf_check.csv")
    es = rd("engagement_summary.csv"); o = es[(es.group == "ALL") & (es.genre == "videos") & (es.predictor == "outrage")].iloc[0]
    f9 = es[(es.group == "ALL") & (es.genre == "videos") & (es.predictor == "F9")].iloc[0]
    zs = z.set_index(["grouping", "system"])
    n_lab = int(zs.loc[('title_label', 'left'), 'n_titles'] + zs.loc[('title_label', 'neither'), 'n_titles'] + zs.loc[('title_label', 'right'), 'n_titles'])
    n_lab_all = int(json.loads((A / "leaning_label_shares.json").read_text())["n_labelled"])
    csg = cs.set_index(["grouping", "group"])
    zw = z.copy(); zw["system"] = [group(s) if k == "channel_group" else (f"{s} titles" if k == "title_label" else CAPS_LABEL.get(s, s)) for k, s in zip(zw.grouping, zw.system)]
    zw_cols = ["grouping", "system", "n_titles", "n_tokens", "n_types", "tokens_per_title", "zipf_top100", "zipf_top1000", "zipf_top5000", "zipf_r2_top1000", "zipf_size_matched", "top1_share", "top_10"]
    zg2 = zg.copy(); zg2["group"] = [group(s) if k == "channel_group" else CAPS_LABEL.get(s, s) for k, s in zip(zg2.grouping, zg2.group)]
    zg_words = zg2[["grouping", "group", "n_creators", "zipf_words_top200_mean", "zipf_words_top200_median", "n_creators_1500", "zipf_words_1500_mean", "heaps_beta_1500_mean", "top1_word_share_mean"]]
    zg_views = zg2[["grouping", "group", "n_creators_with_views", "zipf_views_all_median", "zipf_views_head_median", "gini_median", "top10_share_median", "powerlaw_like_share", "caps_any_mean"]]
    va = vm[vm.month == "all"].copy(); va["group"] = [group(s) if k == "channel_group" else (f"{s} titles" if k == "title_label" else CAPS_LABEL.get(s, s)) for k, s in zip(va.grouping, va.group)]
    vg = vm[(vm.grouping.isin(["channel_group", "all"])) & (vm.month != "all")].copy(); vg["group"] = vg.group.map(lambda g: group(g) if g in GROUPS else g)
    p_cg = vg.pivot(index="group", columns="month", values="creator_median_views").reindex(["all channels"] + [group(g) for g in GROUPS]).reset_index()
    ratio = (p_cg.set_index("group").loc["left channels"] / p_cg.set_index("group").loc[["neutral channels", "right channels"]].max()).astype(float)
    vc = vm[(vm.grouping == "caps_style") & (vm.month != "all")].copy(); vc["group"] = vc.group.map(CAPS_LABEL)
    p_cs = vc.pivot(index="group", columns="month", values="relative_log_views").reindex([CAPS_LABEL[c] for c in CAPS_ORDER]).reset_index()
    vl = vm[(vm.grouping == "title_label") & (vm.month != "all")].copy(); vl["group"] = vl.group + " titles"
    p_tl = vl.pivot(index="group", columns="month", values="relative_log_views").reindex([f"{l} titles" for l in TITLE_LABELS]).reset_index()
    cs2 = cs.copy(); cs2["group"] = [group(s) if k == "channel_group" else f"{s} titles" for k, s in zip(cs2.grouping, cs2.group)]
    lc2 = lc.copy(); lc2["caps_style"] = lc2.caps_style.map(CAPS_LABEL)
    rel = va.set_index("group").relative_log_views
    med = va.set_index("group").creator_median_views
    cg_z = zg.set_index(["grouping", "group"])
    ca = cs.set_index(["grouping", "group"]).caps_any
    tight = va[va.grouping == "channel_group"].set_index("group")
    out = f"""# 7. Zipf's law, and views over time

**The question.** Does title vocabulary follow Zipf's law, and does the shape of the law differ between left, neutral and right channels, between titles the judge read as left, neither or right, and between capitalisation styles? Do views within a channel follow a Zipf (rank-size) law? And how do views run over the months of 2026, again cut by channel group, by title label and by capitalisation style?

Three groupings run through the whole document. **Channel group**: left / neutral / right channels, each channel's title-leaning score from document 14 (thresholds ±0.05). **Title label**: left / neither / right, the judge's label of each sampled title (document 14; {n_lab:,} of the {n_lab_all:,} sampled titles are edited uploads and are used here). **Capitalisation style**: ALL CAPS, selective CAPS, Title Case, Sentence case, mixed / other and short / other, one rule per title (document 11).

## The finding in one paragraph

Title vocabulary is Zipfian in the way short texts usually are: on log-log axes the rank-frequency curve is straight through the head (R² {float(zs.loc[('corpus', 'all edited uploads (balanced)'), 'zipf_r2_top1000']):.3f} over the top 1,000 words) with an exponent that depends on the cut-off ({float(zs.loc[('corpus', 'all edited uploads (balanced)'), 'zipf_top1000']):.2f} over the top 1,000 words, {float(zs.loc[('corpus', 'all edited uploads (balanced)'), 'zipf_top5000']):.2f} over the top 5,000), because ten-word titles have a flatter head than running prose. The three ways of cutting the corpus move the curve less than they move the words on it. Left channels have the steepest vocabulary (size-matched exponent {float(zs.loc[('channel_group', 'left'), 'zipf_size_matched']):.2f} against {float(zs.loc[('channel_group', 'right'), 'zipf_size_matched']):.2f} for the right group): "trump" is their most frequent word, ahead of "the". Among the labelled titles the left-read ones are again the most concentrated ({float(zs.loc[('title_label', 'left'), 'zipf_size_matched']):.2f}) and the right-read ones the least ({float(zs.loc[('title_label', 'right'), 'zipf_size_matched']):.2f}). ALL-CAPS titles are the shortest ({float(zs.loc[('caps_style', 'all_caps'), 'tokens_per_title']):.1f} tokens against {float(zs.loc[('caps_style', 'sentence_case'), 'tokens_per_title']):.1f} for sentence case) and their head is the flattest, with "this", "it" and "they" among the ten most frequent words: the shouted title is a reaction, not a headline. Views within a channel are *not* Zipfian: the rank-size curve bends down in the tail, the power-law fit is never significantly preferred to a lognormal ({int(hv.powerlaw_like.astype(bool).sum())} of {len(hv)} video channels; the lognormal is significantly preferred in {int(((hv.lr_vs_lognormal < 0) & (hv.lr_p < 0.05)).sum())} and the test is inconclusive in the rest), and the neutral group is the most hit-driven (median Gini {float(cg_z.loc[('channel_group', 'neutral'), 'gini_median']):.2f} against {float(cg_z.loc[('channel_group', 'left'), 'gini_median']):.2f} and {float(cg_z.loc[('channel_group', 'right'), 'gini_median']):.2f}). Over the months, views per video are a snapshot that favours older uploads, and the left group's channels sit far above the other two in every month (median channel {med['left channels'] / 1000:.0f}k views per video against about {med['right channels'] / 1000:.0f}k for the right group and {med['neutral channels'] / 1000:.0f}k for the neutral). Against each channel's own monthly baseline, capitals earn views in every month of the year (ALL CAPS {rel['ALL CAPS']:+.2f} and selective CAPS {rel['selective CAPS']:+.2f} log points, Title Case {rel['Title Case']:+.2f}, sentence case {rel['Sentence case']:+.2f}), and right-read titles do a little better than left-read ones, which do a little better than neither ({rel['right titles']:+.2f}, {rel['left titles']:+.2f}, {rel['neither titles']:+.2f}).

## Zipf's law in title vocabulary

![Rank-frequency curves by channel group, by title label and by capitalisation style.](figures/07_zipf_words.png)
*Word frequency against rank on log-log axes, three ways of cutting the corpus; the dotted black line is the whole corpus.*

Tokens are lower-cased words from the normalised title, stopwords included (Zipf's law is a statement about the whole vocabulary). Systems differ in size, and the OLS exponent depends on size, so two exponents are given: over the top 1,000 ranks of the whole system, and *size-matched* (the mean over 20 random draws of 2,000 titles, top 200 ranks), which is the one to compare across rows.

{table(zw, zw_cols, fmt='{:.3f}')}

Three things to read off the table. The corpus exponent over the top 100 words ({float(zs.loc[('corpus', 'all edited uploads (balanced)'), 'zipf_top100']):.2f}) is higher than over the top 1,000 ({float(zs.loc[('corpus', 'all edited uploads (balanced)'), 'zipf_top1000']):.2f}) and lower than over the top 5,000 ({float(zs.loc[('corpus', 'all edited uploads (balanced)'), 'zipf_top5000']):.2f}): the head of a title vocabulary is flat because titles ration function words, and the tail is steep because a {int(zs.loc[('corpus', 'all edited uploads (balanced)'), 'n_titles']) // 1000}k-title corpus has a long list of names used once (the Stage 0 check on the balanced subset with streams included, `zipf_check.csv`, gives the same three figures). The left group is the most concentrated of the three channel groups and the left-read titles the most concentrated of the three labels, and "trump" heads both lists ({float(zs.loc[('channel_group', 'left'), 'top1_share']):.1%} of the left group's tokens, {float(zs.loc[('title_label', 'left'), 'top1_share']):.1%} of the left-read titles'), whereas the neutral group and the neither-read titles start with "the" and "in"; the right-read titles are the flattest system in the corpus, their most frequent words being the function words of a headline ("the", "to", "is", "on") with "trump" fifth. The capitalisation styles differ in length more than in slope; the ALL-CAPS system is the exception, with the lowest top-100 exponent ({float(zs.loc[('caps_style', 'all_caps'), 'zipf_top100']):.2f}) and the highest top-1,000 exponent ({float(zs.loc[('caps_style', 'all_caps'), 'zipf_top1000']):.2f}): a small, repetitive vocabulary of reaction words with a very short tail.

Creator-level exponents (each channel's own vocabulary, top 200 ranks, from the Stage 0 check; and the subsampled Zipf and Heaps exponents of Stage 2, which exist only for the `n_creators_1500` channels with at least 1,500 tokens) averaged per group tell the same story from the channel side, with the ranked channels' dominant capitalisation style as a second cut:

{table(zg_words, fmt='{:.3f}')}

Channels whose titles are mostly sentence case (the news outlets) have the steepest own vocabularies and the fastest-growing ones (Heaps' β {float(cg_z.loc[('dominant_caps_style', 'sentence_case'), 'heaps_beta_1500_mean']):.2f}); channels that shout have the flattest.

## Zipf's law for views

![Rank-size curves of views and the slope by channel group and by dominant capitalisation style.](figures/07_zipf_views.png)
*Left: rank-size curves for eight channels, each normalised to its own top video. Middle and right: the all-video Zipf slope per channel, by channel group and by the channel's dominant capitalisation style.*

Within each channel, videos ranked by views on log-log axes: a straight line would be Zipf's law for views (views proportional to rank to a negative power). The curves instead bend downwards in the tail, which is what a lognormal looks like on these axes and what the formal test confirms: the `powerlaw` fit (discrete, xmin by KS minimisation) with the likelihood-ratio test against a lognormal supports a power-law tail in {int(hv.powerlaw_like.astype(bool).sum())} of {len(hv)} video channels. Hits are heavy-tailed but lognormal-shaped, so no channel here should be described as having a power-law audience. The slope of log views on log rank over all of a channel's videos still summarises how steeply views fall off down the ranking (per channel in `hit_concentration.csv`, `zipf_views_all` and `zipf_views_head`), and it lines up with the Gini coefficient and the top-10 % share:

{table(zg_views, fmt='{:.3f}')}

The neutral group is the hit-driven one: its channels' views fall off fastest down the ranking (median slope {float(cg_z.loc[('channel_group', 'neutral'), 'zipf_views_all_median']):.2f}; the top tenth of videos take {pct(float(cg_z.loc[('channel_group', 'neutral'), 'top10_share_median']))} of views). Left and right channels are nearly identical to each other ({float(cg_z.loc[('channel_group', 'left'), 'zipf_views_all_median']):.2f} and {float(cg_z.loc[('channel_group', 'right'), 'zipf_views_all_median']):.2f}) and much flatter: the daily commentary audience turns up for everything. The same ordering appears by capitalisation: channels that mostly shout spread views most evenly, sentence-case channels live on hits. Both patterns are the same fact seen twice, because the neutral group is where the sentence-case news outlets are.

## Views over time

![Views by publication month by channel group; relative views by capitalisation style and by title label.](figures/07_views_over_time.png)
*Left: the median over channels of the channel's median views per video, by publication month and channel group. Middle and right: log views relative to the same channel's average in the same month, by capitalisation style and by title label; bands are ±1.96 standard errors.*

Views are a snapshot taken at fetch time (2026-09-14) and months are YouTube's approximate listing dates, so the monthly curve mixes age with season: a January video has had eight months to accumulate views, and the last, half month holds the newest uploads still in their first weeks. That half month also shows the highest medians of the year, which says more about how fast a video collects its first views and about the approximate dating (anything listed as "weeks ago" lands at the start of September) than about September itself. Read the left panel as a comparison *between* groups within a month, not as growth over time. The median channel in the left group draws {ratio.min():.1f} to {ratio.max():.1f} times the views of the median channel in the next group in every month of the year:

{table(p_cg, fmt='{:,.0f}')}

Within a channel the age effect cancels: **relative log views** is log(1 + views) minus the mean log(1 + views) of the same channel's videos in the same month, so 0 is the channel's average title that month and +0.05 is roughly 5 % more views than that average. By construction the three channel groups average 0 on it; capitalisation styles and title labels do not.

**By capitalisation style.** Capitals beat a channel's own baseline in every month of the year, and the two lower-case styles fall below it in every month:

{table(p_cs, fmt='{:+.3f}')}

Over the year: ALL CAPS {rel['ALL CAPS']:+.3f}, selective CAPS {rel['selective CAPS']:+.3f}, Title Case {rel['Title Case']:+.3f}, Sentence case {rel['Sentence case']:+.3f} (standard errors {float(va.loc[va.group == 'ALL CAPS', 'relative_log_views_se'].iloc[0]):.3f} for ALL CAPS and at most {float(va.loc[va.group.isin(['selective CAPS', 'Title Case', 'Sentence case']), 'relative_log_views_se'].max()):.3f} for the three big styles). The effect is modest (a few per cent) but it is the most consistent title-level signal in the corpus, holding month after month and inside channels rather than between them; the twelve-factor regression with month *and topic* controls (all_tables.md, stage 5) gives the ALL-CAPS factor F9 a median coefficient of {f9.median_coef_per_sd:+.3f} log views per within-channel SD, positive for {pct(f9.share_positive)} of channels: the same sign, smaller once the subject is held fixed. "Short / other" titles ({int(va.loc[va.group == 'short / other', 'n_videos'].iloc[0]):,} videos, mostly numbered episodes and one-word titles) sit far above baseline, but that is a format effect, not a capitalisation one.

**By title label.** Over the {int(va.loc[va.grouping == 'title_label', 'n_videos'].sum()):,} sampled titles with view counts, right-read titles outperform their channel's monthly average, left-read titles sit at it and neither-read titles fall just below; the differences are small, only the right-read figure clears two standard errors, and the monthly series is noisy (a few hundred titles per label per month):

{table(p_tl, fmt='{:+.3f}')}

Over the year: right {rel['right titles']:+.3f} (SE {float(va.loc[va.group == 'right titles', 'relative_log_views_se'].iloc[0]):.3f}), left {rel['left titles']:+.3f}, neither {rel['neither titles']:+.3f}. Partisan wording, in other words, does about what capitals do, and the two overlap: {pct(ca[('title_label', 'left')])} of left-read and {pct(ca[('title_label', 'right')])} of right-read titles carry ALL or selective CAPS, against {pct(ca[('title_label', 'neither')])} of neither-read ones.

## How the three cuts overlap

![Capitalisation style by channel group and by title label.](figures/07_caps_by_group.png)
*Capitalisation style shares by channel group (balanced edited uploads) and by title label (the judge's sample).*

{table(cs2, ['grouping', 'group', 'n_titles'] + CAPS_ORDER + ['caps_any'], fmt='{:.2f}', rename=CAPS_LABEL)}

Left and right channels shout at the same rate ({pct(ca[('channel_group', 'left')])} and {pct(ca[('channel_group', 'right')])} of titles with capitals); the neutral group is sentence case ({pct(float(csg.loc[('channel_group', 'neutral'), 'sentence_case']))}). The left group leans to selective CAPS ({pct(float(csg.loc[('channel_group', 'left'), 'selective_caps']))} of titles), the right group splits between Title Case ({pct(float(csg.loc[('channel_group', 'right'), 'title_case']))}) and selective CAPS ({pct(float(csg.loc[('channel_group', 'right'), 'selective_caps']))}); sentence case is {pct(float(csg.loc[('channel_group', 'left'), 'sentence_case']))} and {pct(float(csg.loc[('channel_group', 'right'), 'sentence_case']))}. Crossing the labelled titles with their style shows where the judge's labels come from: selective CAPS is the partisan style ({pct(1 - float(lc.loc[lc.caps_style == 'selective_caps', 'share_neither'].iloc[0]))} of its labelled titles read left or right), while ALL CAPS, Title Case and sentence case read as "neither" {pct(float(lc.loc[lc.caps_style == 'all_caps', 'share_neither'].iloc[0]))}, {pct(float(lc.loc[lc.caps_style == 'title_case', 'share_neither'].iloc[0]))} and {pct(float(lc.loc[lc.caps_style == 'sentence_case', 'share_neither'].iloc[0]))} of the time (a fully shouted title is as often a reaction to an event as a stance on it), and within each style the right-read titles are the ones that draw the most views relative to their channel:

{table(lc2, ['caps_style', 'n_titles', 'share_left', 'share_neither', 'share_right', 'relative_log_views_left', 'relative_log_views_neither', 'relative_log_views_right'], fmt='{:.3f}')}

## What the numbers do and do not say

- Views are views-to-date at one fetch, not lifetime views, and Rumble channels have no view counts and are absent. The relative measure compares titles of the same channel in the same month, which removes both the channel's size and the age of its videos; it does not remove the subject of the video, and a shouted title about a shooting may draw views for the shooting.
- The outrage frame of document 4 is the other title-level signal that predicts views within a channel: in the twelve-factor regression with month and topic controls (all_tables.md, stage 5), the outrage coefficient is positive for {pct(o.share_positive)} of {int(o.n_creators)} video channels (median {o.median_coef_per_sd:+.3f} log views per within-channel standard deviation); the capitals effect above is measured without topic controls and is of the same order.
- Title labels are the judge's reading of {n_lab_all:,} sampled titles (50 per ranked channel, 16 for the smallest channels), so the label series are thin by month; the annual figures are the ones to quote.
- Zipf exponents from OLS on log-log axes are descriptive; the size-matched column is the only fair comparison across systems of different size, and the curves in the figure are the fuller statement.
- {GROUP_NOTE}

Files: `zipf_words.csv`, `zipf_words_curves.csv`, `zipf_by_group.csv`, `views_by_month.csv`, `caps_style_by_group.csv`, `label_by_caps_style.csv`, `hit_concentration.csv`, `zipf_check.csv`, `zipf_check_creators.csv`, `engagement_summary.csv`.
"""
    return out


def doc_nulls() -> str:
    rt = rd("validation_retest.csv"); lab = rd("labels.csv"); hk = json.loads((A / "hook_classifier.json").read_text())["hooks"]; cand = rd("validation_candidates.csv")
    cc = rd("cluster_comparison.csv"); hv = rd("hit_concentration.csv"); hv = hv[hv.genre == "videos"]
    es = rd("engagement_summary.csv"); allv = es[(es.group == "ALL") & (es.genre == "videos")]
    other = allv[allv.predictor != "outrage"]
    out = f"""# 8. Null results and caveats

Results that came out empty are results; and several numbers in this set should be read with their weaknesses in view.

## What did not show up

- **A Conversational dimension.** The LLM's conversational rating correlates with the factor closest to it (stream talk: chat, ellipsis, contractions) at only r = {float(cand.loc[cand.candidate == 'Conversational', 'creator_level_r'].iloc[0]):.2f} at the creator level. The structural markers exist (factor F4 of the style model, `factor_loadings.csv`) but they do not track what a reader calls conversational.
- **A Humour dimension, and a humour hook.** The rater flagged {int(lab.humor.sum())} of {len(lab)} sampled titles as humorous; its test-retest kappa on the flag is {float(rt.loc[rt.dimension == 'humor', 'kappa'].iloc[0]):.2f}; the classifier's held-out F1 is {hk['humor']['holdout_f1']:.2f}. Humour in titles is either genuinely rare in this landscape or invisible to a 14B model reading ten words. Nothing in the results should be cited as a measure of humour.
- **A curiosity-gap hook.** {int(lab.curiosity_gap.sum())} positives of {len(lab)} ({pct(lab.curiosity_gap.mean(), 1)}), classifier F1 {hk['curiosity_gap']['holdout_f1']:.2f}. The lexicon feature that approximates it (`curiosity_lex`: "here's why", "you won't believe", "this is insane") loads on the outrage pole of the tone factor, which suggests the device mostly *is* outrage in this corpus, but the hook as defined was not measured.
- **Style as a predictor of views** (beyond outrage and capitals). In the within-channel regression of log views on the twelve dimensions, the hooks and length (month and topic controls; `engagement_summary.csv`), every predictor other than the outrage frame has a median effect at or below {float(other.median_coef_per_sd.abs().max()):.2f} log views per SD and between {pct(float(other.share_same_sign_as_median.min()))} and {pct(float(other.share_same_sign_as_median.max()))} of channels on the median's side of zero. The capitals effect of document 7 is measured on the same titles without topic controls and is of the same small order.
- **Power-law audiences.** {int(hv.powerlaw_like.astype(bool).sum())} of {len(hv)} video channels (document 7).
- **The channel groups as a style predictor.** ARI {float(cc.loc[(cc.genre == 'videos') & (cc.titles == 'all'), 'ari_style_vs_group'].iloc[0]):.3f} (document 5): channels whose titles read left, neutral or right do not title in three styles.
- **A landscape-wide drift.** Corpus-mean outrage share flat over the year (document 6).

## What to distrust, and how much

- **The rater.** All ratings and labels behind the style model, the hooks and the formats come from a local Qwen3-14B model at temperature 0. Weighted kappa on a 300-title retest: sensational {float(rt.loc[rt.dimension == 'sensational', 'weighted_kappa'].iloc[0]):.2f}, critical {float(rt.loc[rt.dimension == 'critical', 'weighted_kappa'].iloc[0]):.2f}, analytical {float(rt.loc[rt.dimension == 'analytical', 'weighted_kappa'].iloc[0]):.2f}, conversational {float(rt.loc[rt.dimension == 'conversational', 'weighted_kappa'].iloc[0]):.2f}, educational {float(rt.loc[rt.dimension == 'educational', 'weighted_kappa'].iloc[0]):.2f}; kappa on the outrage flag {float(rt.loc[rt.dimension == 'outrage', 'kappa'].iloc[0]):.2f}, on the format label {float(rt.loc[rt.dimension == 'format_llm', 'kappa'].iloc[0]):.2f}. The validation of the tone factor stands on the reliable ratings; the rest is indicative. Re-rating with a stronger model is one cached command (`llm_rate --model ...`).
- **The channel groups** come from a second model's reading of 50 sampled titles per channel (document 14). The score is reliable as a ranking (split-half Spearman {float(rd('leaning_split_half.csv').split_half_spearman_mean.iloc[0]):.2f}), but the ±0.05 thresholds are a choice, {int(rd('leaning_stability.csv').group_changed.iloc[0])} channels changed group between the first 16-title draw and the full sample, and a group says how a channel's titles *read*, not what it is. Every group-level table changes if the thresholds or the judge change; the creator-level tables, neighbours and clusters do not.
- **The political flag** is broad (212 of 236 topics). The political-only landscape run reaches the same conclusions as the all-titles run, which limits how much this matters, but per-creator political shares should not be quoted without that caveat.
- **Entity counts** come from spaCy's small English model on truecased headline text; "Hormuz" as a person and fan-channel formulas as people show the noise. The top-25 lists are robust, the tail is not.
- **Views** are a fetch-time snapshot; Rumble has none; verbatim repeats are kept for view and concentration statistics and removed for everything else; months are approximate listing dates.
- **Group sizes.** The neutral group has {int(rd('leaning_groups.csv').set_index('group').loc['neutral', 'n_channels'])} channels and a handful of ranked stream channels; anything group-level on streams for it is a description of a few channels.
- **The corpus is one calendar window** dominated by one war. A landscape measured in a quieter year could show more topic separation between the groups and a smaller shared-title set.

## What would change the picture most

A human check of the leaning labels (the blind sheet is written: `leaning_human_sheet.csv`); re-rating the 3,000 titles with a more reliable model (or a human sample) to settle Educational and Conversational; and a second time window, so drift can be measured on more than nine points.
"""
    return out


# --------------------------------------------------------------------------- #
# Question documents (09-14)
# --------------------------------------------------------------------------- #
def doc_twins() -> str:
    pairs = rd("style_twins.csv"); near = rd("style_twins_nearest.csv"); dims = rd("dimensions.csv")
    n_left = int((near.group == "left").sum()); n_right = int((near.group == "right").sum())
    top = pairs.head(20).copy(); top["distance_percentile_all_pairs"] = top.distance_percentile_all_pairs.round(2)
    hub = pairs.head(20).right_creator.value_counts().head(3)
    closer = near.twin_closer_than_any_same_group.mean()
    nl = near[near.group == "left"].head(12); nr = near[near.group == "right"].head(12)
    return f"""# 9. Stylistic twins across the political divide

**The question.** Which left channels and right channels (the channel groups of document 14) title their videos the same way?

## The finding in one paragraph

Style ignores the divide. Measured in the twelve-dimensional, topic-controlled style space of the style model, the nearest neighbour of a left channel is on the right side of the divide about as often as on its own side: for {closer:.0%} of the {len(near)} left and right channels the closest channel across the divide is closer than *any* channel in their own group, and the distributions of nearest-twin distance and nearest-group-mate distance sit almost on top of each other. The closest pairs are not the big names but the mid-sized daily channels on both sides: {top.iloc[0].left_creator} and {top.iloc[0].right_creator}, {top.iloc[1].left_creator} and {top.iloc[1].right_creator}, {top.iloc[2].left_creator} and {top.iloc[2].right_creator}. What they share is form: emphasis capitals on one or two words, a named target, a verb of attack or collapse, no question, no label, no numbers.

![The twenty closest pairs and the distance comparison.](figures/09_twins.png)
*Left: the twenty closest left-right pairs. Right: for every left and right channel, the distance to its nearest channel across the divide against the distance to its nearest group-mate.*

## The twenty closest pairs

`distance` is Euclidean distance between z-scored topic-controlled factor scores (edited uploads); `distance_percentile_all_pairs` places the pair among all {len(dims[(dims.genre == 'videos') & (~dims.low_n)])} ranked creators' pairwise distances (0 = the closest pair in the whole landscape).

{table(top, ['left_creator', 'right_creator', 'distance', 'distance_percentile_all_pairs'], fmt='{:.2f}')}

A few right-side channels recur as everybody's twin in the table above ({', '.join(f'{k} x{v}' for k, v in hub.items())}): they sit near the centre of the commentary cloud, so they are close to many left channels at once. Hubness like this is a property of the space, not evidence of imitation.

## Every channel's twin across the divide

The full table is `style_twins_nearest.csv`; the twelve left and twelve right channels with the closest twins:

{table(nl, ['creator', 'twin_across_divide', 'twin_distance', 'twin_rank_among_all_neighbours', 'nearest_same_group', 'nearest_same_group_distance', 'twin_closer_than_any_same_group'], fmt='{:.2f}')}

{table(nr, ['creator', 'twin_across_divide', 'twin_distance', 'twin_rank_among_all_neighbours', 'nearest_same_group', 'nearest_same_group_distance', 'twin_closer_than_any_same_group'], fmt='{:.2f}')}

`twin_rank_among_all_neighbours` = 1 means the twin is the creator's single nearest neighbour in the whole landscape (any group).

## Method

1. Style vectors: the twelve factor scores of the style model (`factor_loadings.csv`, `dimensions.csv`), topic-controlled (each title's score minus its topic's mean, averaged per creator), edited uploads only, creators with at least 50 unique titles, clip channels excluded ({n_left} left and {n_right} right channels).
2. Each factor z-scored across the ranked creators so that no factor dominates; distance = Euclidean over the twelve.
3. For every channel on one side, the nearest channel on the other side is its twin; the same distance is computed to the nearest channel on its own side; the pair distance is also expressed as a percentile of all ranked pairwise distances.
4. "Left" and "right" are the channel groups of document 14: the channel's score over its sampled titles, below −0.05 and above +0.05. The neutral group is not in the comparison.

## Limitations

- The divide is the judge's reading of each channel's titles, so a channel whose titles read neutral although its host is partisan is left out, and a channel near a threshold can sit on either side; document 14 gives the reliability of the score.
- The space weights all twelve factors equally after z-scoring; two creators can be twins on capitals, questions and quotes while differing in tone, or the reverse. `dimensions.csv` has the per-factor scores if a narrower definition is wanted.
- Topic control removes the average effect of a topic on each score, not everything a subject does to a title.
- Distances shrink for creators near the centre of the cloud (hubness above) and grow for eccentric ones; the percentile column is the fairer comparison.
- Only edited uploads; live VODs are too thin for both groups.

Files: `style_twins.csv`, `style_twins_nearest.csv`, `dimensions.csv`, `neighbours_style.csv`.
"""


def doc_caps_words() -> str:
    from pipeline_titles.textstats import CAPS_STYLES
    cp = rd("caps_profile.csv"); tw = rd("top_words.csv"); acr = (A / "caps_acronyms.txt").read_text().split()
    v = cp[(cp.genre == "videos") & (~cp.low_n)].sort_values("caps_any", ascending=False).copy()
    means = v[CAPS_STYLES].mean()
    gm = _lg(v[v.group.isin(GROUPS)].groupby("group")[CAPS_STYLES + ["caps_any"]].mean().reset_index())
    full = v[["creator", "group", "n_titles", "caps_any"] + CAPS_STYLES].copy()
    t20 = tw.head(20).copy()
    return f"""# 11. Capitalisation profile, and the words titles are made of

## Capitalisation profile

**The question.** How does each channel capitalise its titles: shouting in ALL CAPS, emphasising single words, Title Case, or sentence case?

### The finding in one paragraph

Averaged over the {len(v)} ranked channels (edited uploads), {pct(means['title_case'])} of titles are Title Case, {pct(means['selective_caps'])} use selective CAPS (one or more shouted words inside a normally cased title: "Trump SLAMS Judge"), {pct(means['sentence_case'])} are sentence case, {pct(means['all_caps'])} are ALL CAPS, and the rest are too short to classify or mixed. Selective capitals are the signature of the daily commentary channels: {', '.join(v.head(5).creator)} put an emphasised word in more than {pct(v.iloc[4].caps_any)} of their titles. Full ALL-CAPS titles are rarer and concentrated in a handful of channels on both sides (Jackson Hinkle, TheQuartering, the three Timcast channels, Fleccas, and the streamers Hasan Piker and Vaush); the news outlets are sentence case or Title Case, and the selective capitals they do show are mostly quoted shouted words ('GAME CHANGER': ...) rather than emphasis. By channel group the left and right groups shout at the same rate ({pct(float(gm.loc[gm.group == 'left channels', 'caps_any'].iloc[0]))} and {pct(float(gm.loc[gm.group == 'right channels', 'caps_any'].iloc[0]))} of the average channel's titles) and the neutral group hardly at all ({pct(float(gm.loc[gm.group == 'neutral channels', 'caps_any'].iloc[0]))}); document 7 follows the styles into views.

![Top 45 channels by capitals.](figures/11_caps_profile_top.png)
*The 45 channels that use ALL CAPS or selective CAPS most; the bar is the whole channel's titles.*

![Bottom 30 channels by capitals.](figures/11_caps_profile_bottom.png)
*The 30 channels using capitals least.*

![By channel group.](figures/11_caps_profile_by_group.png)
*Channel-group means.*

### By channel group (mean of creators)

{table(gm, ['group'] + CAPS_STYLES + ['caps_any'], fmt='{:.2f}', rename=CAPS_LABEL)}

### Every ranked channel, sorted by ALL CAPS + selective CAPS

{table(full, ['creator', 'group', 'n_titles', 'caps_any'] + CAPS_STYLES, fmt='{:.2f}', rename=CAPS_LABEL)}

### Method

Each unique normalised title (brand suffixes such as "| Fox News" removed, so channel tags do not count) is classified by one rule in this order: **short / other** if it has fewer than three 2+-letter words; **ALL CAPS** if at least 90 % of its words are all-capitals; **selective CAPS** if it contains at least one all-capitals word of three or more letters that is neither a known acronym nor a generic label; **mixed / other** if it starts lower-case; **Title Case** if at least 80 % of the remaining content words (function words excluded) start with a capital; **sentence case** otherwise. Acronyms are learned from the corpus itself ({len(acr)} words that are all-capitals in at least 80 % of their non-initial occurrences in mixed-case titles, e.g. FBI, ICE, GOP, NATO, AI; the list is `caps_acronyms.txt`); the generic labels are LIVE, BREAKING, WATCH, NEW, FULL, EXCLUSIVE, UPDATE, REPLAY and the like. Shares are over a channel's unique titles per genre.

### Limitations

- Any single emphasised word makes a title "selective CAPS", so the category mixes light emphasis ("This Is INSANE") with heavy ("MAGA MELTDOWN as Trump LOSES IT").
- The acronym exemption is corpus-learned: a word that is usually shouted (e.g. a name a channel always capitalises) can be learned as an acronym and stop counting, and a genuine acronym rarely written in mixed case can count as emphasis.
- Title Case vs sentence case is a threshold (80 % of content words capitalised); headlines dense with proper nouns can tip over it.
- Computed on normalised titles; a channel whose only capitals were in a stripped show-name suffix scores lower than its raw titles look.
- {GROUP_NOTE}

## The twenty most frequent non-stopwords

**The question.** What words do titles actually use most?

{table(t20, ['rank_balanced', 'word', 'balanced_share_of_titles', 'creators_using', 'raw_pooled_share_of_titles', 'rank_raw'], fmt='{:.3f}')}

![Top words.](figures/11_top_words.png)

Trump is in one title in {round(1 / float(tw.loc[tw.word == 'trump', 'balanced_share_of_titles'].iloc[0]))} of the average creator's and in {pct(float(tw.loc[tw.word == 'trump', 'raw_pooled_share_of_titles'].iloc[0]))} of all titles; the war words (iran, war, israel) and the year's institutions (ice, epstein, maga, democrats) follow. The two columns disagree where the big news channels differ from everyone else: "says" is the {int(tw.loc[tw.word == 'says', 'rank_raw'].iloc[0])}th most frequent word in the raw pool (wire headlinese: "X says Y") but only {int(tw.loc[tw.word == 'says', 'rank_balanced'].iloc[0])}th when creators count equally; "debate", "black" and "truth" are commentary words that the pooled count buries.

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
    cols = ["rank_in_genre", "creator", "group", "arousal_index", "caps_share", "exclamations", "power_words", "emoji", "vader_intensity", "n_titles"]
    ren = {"rank_in_genre": "rank", "arousal_index": "index (0-1)", "caps_share": "ALL-CAPS word share", "exclamations": "! per title", "power_words": "power words per title", "emoji": "emoji per title", "vader_intensity": "VADER intensity"}
    gm = _lg(v[v.group.isin(GROUPS)].groupby("group").arousal_index.agg(["median", "mean", "min", "max", "size"]).reset_index())
    return f"""# 12. Arousal index by channel

**The question.** On one 0-1 scale, how emotionally charged is each channel's titling: capitals, exclamation marks, power words, emoji and sentiment intensity together?

## The finding in one paragraph

The index runs from {v.iloc[0].creator} ({v.iloc[0].arousal_index:.2f}) at the top, followed by {', '.join(v.iloc[1:5].creator)}, to {', '.join(v.tail(4).creator[::-1])} at the bottom (all under 0.02). The top of the ranking is the daily outrage channels of both sides plus the MeidasTouch network; the bottom is magazines, wires and interview podcasts. By channel group, the left group has the highest median ({float(gm.loc[gm.group == 'left channels', 'median'].iloc[0]):.2f}), the right group is close behind ({float(gm.loc[gm.group == 'right channels', 'median'].iloc[0]):.2f}) and the neutral group sits far below ({float(gm.loc[gm.group == 'neutral channels', 'median'].iloc[0]):.2f}). The index agrees with the independent measures it should agree with: Spearman {r_sens:+.2f} with the LLM rater's *sensational* score aggregated per channel, {r_f1:+.2f} with the tone factor (positive = calm) and {r_f9:+.2f} with the ALL-CAPS factor of the style model.

![Arousal index, every ranked channel.](figures/12_arousal_ranked.png)
*All ranked channels with edited uploads, highest first; colour = channel group.*

![Arousal by channel group.](figures/12_arousal_by_group.png)

## By channel group

{table(gm, ['group', 'size', 'median', 'mean', 'min', 'max'], fmt='{:.2f}', rename={'size': 'n_creators'})}

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
- {GROUP_NOTE}

Files: `arousal_index.csv`.
"""


def doc_keywords() -> str:
    kw = rd("signature_keywords.csv"); cr = rd("creators.csv"); lb = rd("leaning_by_creator.csv")[["creator", "group"]]
    top5 = kw[kw["rank"] <= 5].groupby("creator").apply(lambda g: ", ".join(f"{w} ({z:.0f})" for w, z in zip(g.word, g.z)), include_groups=False).rename("top 5 (z)").reset_index()
    top5 = top5.merge(cr[["creator", "channel_name"]], on="creator").merge(lb, on="creator", how="left").fillna({"group": "unscored"}).sort_values("creator", key=lambda s: s.str.lower())
    ex = kw[kw.creator.isin(["@HasanAbi", "@BenShapiro", "@Reuters", "@MeidasTouch", "@CNN", "@joerogan"])].groupby("creator").apply(lambda g: ", ".join(g.word), include_groups=False)
    return f"""# 13. Signature title keywords per channel

**The question.** Which words does each channel use far more than everyone else?

## The finding in one paragraph

Each channel's signature is scored by weighted log-odds against all other channels' titles, with a prior that shrinks rare words, so the list is the vocabulary a channel *over-uses*, not merely uses. For most channels the top of the list is its own furniture (host names, show segments, a recurring guest), which is expected and is itself a style fact: {ex.get('@BenShapiro', '')[:60]} for Ben Shapiro, {ex.get('@HasanAbi', '')[:60]} for Hasan Piker. Below that, the lists separate beats and registers: {ex.get('@Reuters', '')[:70]} for Reuters, {ex.get('@MeidasTouch', '')[:70]} for MeidasTouch. The top five per channel are below; the top ten with counts are in `signature_keywords.csv` and on each creator's card.

## Every channel's top five (alphabetical)

`z` is the log-odds z-score; larger = more distinctive. Words appear only if the channel used them at least three times. `group` is the channel group of document 14.

{table(top5, ['creator', 'channel_name', 'group', 'top 5 (z)'])}

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

The one grouping of channels used throughout is the **channel group** of document 14: a frontier model labelled a sample of each channel's titles left / right / neither from the title text alone, and each channel's score over its titles sorts the channels into left, neutral and right. No channel is categorised by hand. Titles are grouped two further ways where a title-level cut is wanted: by that same **title label**, and by **capitalisation style** (document 11).

| document | the question it answers |
|---|---|
| [1. The corpus](01_corpus.md) | what is being analysed, what was stripped from titles, how the corpus was balanced, and the creator table |
| [2. Topics](02_topics.md) | what they talk about, month by month, and why topic has to be controlled |
| [4. Formats and hooks](04_formats_and_hooks.md) | questions, LIVE labels, episodes, guests, reactions, confrontations; the outrage frame; why curiosity and humour could not be measured |
| [5. The landscape](05_landscape.md) | who titles like whom, the channel groups vs style, nearest neighbours, organisations, who gets named, shared titles and templates |
| [6. Drift](06_drift.md) | how titles changed from January to September |
| [7. Zipf's law and views](07_views.md) | Zipf's law in title vocabulary and in views; views over time; all three cut by channel group, title label and capitalisation style |
| [8. Null results and caveats](08_null_results_and_caveats.md) | what did not show up, and what to distrust |

Question documents, each with its method and limitations:

| document | the question |
|---|---|
| [9. Stylistic twins](09_stylistic_twins.md) | which left and right channels title the same way |
| [11. Capitalisation and vocabulary](11_capitalisation_and_vocabulary.md) | each channel's capitalisation profile; the twenty most frequent words |
| [12. Arousal index](12_arousal_index.md) | a 0-1 emotional-charge index for every channel, with its components |
| [13. Signature keywords](13_signature_keywords.md) | the words each channel over-uses relative to all others |
| [14. Political leaning from titles](14_political_leaning.md) | two levels: a frontier model labels titles left / right / neither from the title text alone, and the vocabulary of each label is analysed; each channel's score then sorts the channels into left, neutral and right groups, whose whole output is compared |

The style model itself (twelve factors from an exploratory factor analysis of title features, their loadings, the validation against the rater's candidate labels and the topic control) is documented in [`methods_appendix.md`](methods_appendix.md) and its tables in [`all_tables.md`](all_tables.md); the documents above use its factor scores (`F1` tone ... `F12`) by name.

Alongside: [`title_stylometry.html`](title_stylometry.html) (the interactive page: creator selector, profile cards, and the two landscape maps with names on hover and each creator's neighbours drawn in; open it directly in a browser), [`figures/`](figures/) (the static figures used in the documents), [`cards/`](cards/) (one Markdown card per creator), [`methods_appendix.md`](methods_appendix.md) (every preprocessing step, lexicon, loading, validation number, prompt and runtime), and [`all_tables.md`](all_tables.md) (the reference dump of every table in one file).

## The findings, one paragraph per stage

{hl}
"""


def write_all() -> None:
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    docs = {"01_corpus.md": doc_corpus, "02_topics.md": doc_topics,
            "04_formats_and_hooks.md": doc_formats, "05_landscape.md": doc_landscape, "06_drift.md": doc_drift,
            "07_views.md": doc_views, "08_null_results_and_caveats.md": doc_nulls, "09_stylistic_twins.md": doc_twins,
            "11_capitalisation_and_vocabulary.md": doc_caps_words, "12_arousal_index.md": doc_arousal,
            "13_signature_keywords.md": doc_keywords, "README.md": doc_index}
    if (A / "leaning_by_creator.csv").exists():
        from pipeline_titles.report_leaning import doc_leaning
        docs["14_political_leaning.md"] = doc_leaning
    for name, fn in docs.items():
        (REPORTS_DIR / name).write_text(fn(), encoding="utf-8")
