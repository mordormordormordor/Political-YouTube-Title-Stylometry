"""Document 14: political leaning from titles, in two levels (rendered by report_sections.write_all).

Level 1, titles: a frontier judge labels each sampled title left / right / neither from the
title text alone; the labels and the vocabulary behind them are analysed.
Level 2, channels: each channel's score over its sampled titles sorts the channels into
left, neutral and right groups; the groups' reliability and whole output are analysed."""

from __future__ import annotations

import json

import numpy as np
import pandas as pd

from pipeline_titles.common import ANALYSIS_DIR as A, RUNTIMES, SEED, read_jsonl
from pipeline_titles.report_sections import pct, rd, table


def _mname(c: str) -> str:
    c = c.replace("label_", "").replace("_score", "")
    if c.startswith("claude_code_"):
        return "Claude " + c.replace("claude_code_", "").replace("_", " ").title()
    return c.replace("_", ":", 1).replace("_", ".")


def _opt(name: str) -> pd.DataFrame | None:
    return rd(name) if (A / name).exists() else None


def _json(name: str) -> dict | None:
    return json.loads((A / name).read_text()) if (A / name).exists() else None


def _allotax_titles(allo, allo_c, jname: str) -> str:
    if allo is None or allo_c is None or not (allo.comparison == "titles").any():
        return "_(allotaxonographs not rendered on this run: see the README for the Node step)_"
    r = allo[allo.comparison == "titles"].iloc[0]; c = allo_c[allo_c.comparison == "titles"]
    left = c[c.side == "system_1"].head(8).type.tolist(); right = c[c.side == "system_2"].head(8).type.tolist()
    return (f"How to read it. The two vocabularies overlap less than the label shares suggest: D<sup>R</sup><sub>1/3</sub> = {r.divergence:.3f}, with {pct(r.exclusive_share_1)} of the left-read words never appearing in a right-read title and {pct(r.exclusive_share_2)} the other way. "
            f"The apex is shared (the year's subjects), and the divergence is carried by the flanks: on the left {', '.join(left)}; on the right {', '.join(right)}. "
            f"The bottom edges of the diamond, where the dark cells run, are the words used once on one side and never on the other, which is where the labelled sample's smallness shows ({int(r.n_types_1):,} and {int(r.n_types_2):,} word types from {int(r.n_titles_1):,} and {int(r.n_titles_2):,} titles).")


def _allotax_channels(allo, allo_c) -> str:
    if allo is None or allo_c is None or not (allo.comparison == "channels").any():
        return "_(not rendered on this run)_"
    r = allo[allo.comparison == "channels"].iloc[0]; c = allo_c[allo_c.comparison == "channels"]
    left = c[c.side == "system_1"].head(10).type.tolist(); right = c[c.side == "system_2"].head(10).type.tolist()
    return (f"D<sup>R</sup><sub>1/3</sub> = {r.divergence:.3f}: the groups' whole outputs are closer to each other than the left-read and right-read titles are, as they should be, since most of what either group publishes is the shared news of the year. "
            f"The words that separate them are the words the labels found, now over every title the channels published rather than the labelled sample: the left channels' flank is {', '.join(left)}; the right channels' is {', '.join(right)}. "
            f"Show furniture shows up here too (segment names, hosts' first names, the words of a title template), which is the price of comparing channels rather than labelled titles; "
            f"{pct(r.exclusive_share_2)} of the right channels' words never appear in a left channel's title, against {pct(r.exclusive_share_1)} the other way.")


def _classes_sentence(t: pd.DataFrame) -> str:
    rows = {r.comparison: r for r in t.itertuples()}
    a = rows.get("left-read vs right-read titles"); b = rows.get("left vs right channels, every title")
    if a is None or b is None:
        return ""
    return (f"Over the labelled titles the two classes are close in size ({int(a.n_left)} left-class words, {int(a.n_right)} right-class, of {int(a.n_words):,} words with three or more occurrences). "
            f"Over the channels' whole output, with ten times the titles, {pct(b.share_classified)} of the vocabulary clears the cutoff and the right classifies far more words ({int(b.n_right):,} against {int(b.n_left):,} of {int(b.n_words):,}): "
            f"the right channels' vocabulary is the more varied one, and its stance words are spread over more distinct terms.")


def _logodds_section(lo_s, lo_ag, lex, judge: str, jname: str) -> str:
    if lo_s is None or lex is None or not (lo_s.comparison == "titles").any():
        return "_(not computed on this run)_"
    cut = float(lo_s.cutoff_z.iloc[0])
    cname = {"titles": "left-read vs right-read titles", "channels": "left vs right channels, every title"}
    t = lo_s[lo_s.comparison.isin(cname)].copy(); t["comparison"] = t.comparison.map(cname); t["share_classified"] = (t.n_left + t.n_right) / t.n_words
    ag = None
    if lo_ag is not None and len(lo_ag):
        m = lo_ag[((lo_ag.a == "titles") & (lo_ag.b == "channels")) | ((lo_ag.a == "channels") & (lo_ag.b == "titles"))]
        ag = m.iloc[0] if len(m) else None
    sw = [w.split(" (")[0] for w in str(ag.side_switchers).split(", ") if w and w != "nan"] if ag is not None else []
    lj = lex[lex.judge == judge].iloc[0]
    conf = json.loads(lj.confusion); n_neither = sum(conf["neither"].values())
    ag_txt = (f"The two lexicons agree: of the {int(ag.both_partisan)} words that both the labelled titles and the groups' whole output classify as partisan, {pct(ag.same_side_when_both_partisan)} point the same way (kappa {ag.kappa:.2f} over three classes, low only because the groups' output, with ten times the titles, classifies many more words). "
              f"The words that switch sides between the two are {', '.join(sw) if sw else 'none'}, topic and show-name words rather than stance words.") if ag is not None else ""
    return f"""The allotaxonograph ranks words by how far they move between the two rankings; weighted log-odds asks a different question, whether a word is over-used on one side *given how common it is overall*, and gives every word a z-score, so a cutoff turns the vocabulary into a three-way lexicon: right at z ≥ {cut:g}, left at z ≤ −{cut:g}, neither otherwise (the two-sided 5 % level; words with fewer than 3 occurrences are not classified).

![Log-odds, titles.](figures/14_logodds_titles.png)
*Left: every word by its z (vertical) and its frequency (horizontal, log scale) for the titles {jname} read as left against those it read as right; blue = left-class, orange = right-class, grey = neither. Right: the 25 words each side over-uses most, mirrored about the spine, the word beside the spine and its z at the bar's end; bars beyond the axis cap are cut, drawn paler, and keep their value.*

How many words clear the cutoff, for the labelled titles and for the channel groups' whole output (level 2):

![Words that clear the cutoff.](figures/14_logodds_classes.png)
*Left-class and right-class words as shares of each vocabulary, counts printed; the rest are neither.*

{_classes_sentence(t)}

{ag_txt}

**What a word list can do on its own.** The lexicon answers a specific question: how much of the judge's reading is vocabulary? If {jname} decided a title's leaning from the words in it, a plain word list built from its own labels should be able to reproduce those labels. So the list is built from the classes above (every word at |z| ≥ {cut:g} is a left-class or a right-class word); a title is called left when it holds more left-class than right-class words, right the other way, neither on a tie or with no classified word; and the list is built out of fold, on four fifths of the channels and applied to the remaining fifth, so no channel's titles help classify themselves.

![Lexicon against the judge.](figures/14_lexicon_vs_judge.png)
*Left: each channel's score from the word list's labels against its score from {jname}'s labels, coloured by the judge's group. Right: the word list's class against {jname}'s label, title by title, with the share of each row.*

Title by title (the right panel; rows are what {jname} said, columns what the word list said):

- The list agrees with {jname} on {pct(lj.accuracy)} of titles (kappa {lj.kappa:.2f}), which is weak. Where both call a title partisan they agree on the side {pct(lj.side_agreement_when_both_partisan)} of the time, so the direction is mostly right; the failure is in deciding whether a title is partisan at all.
- The list finds left-class words in {pct(conf['neither']['left'] / n_neither)} of the titles {jname} called neither and right-class words in another {pct(conf['neither']['right'] / n_neither)}: a plain headline that mentions MAGA, Epstein or Iran carries left-coded words without a left stance, and a list cannot tell the difference.
- It also misses partisan titles: it recovers {pct(lj.recall_left)} of the judge's left titles but only {pct(lj.recall_right)} of its right ones, because the right's stance words (woke, fraud, women) are rarer than the left's subject words.

Channel by channel (the left panel; each dot is a channel, its score from the judge's labels across and from the list's labels up), the list does much better: Spearman {lj.channel_spearman:.2f}, and {pct(lj.channel_group_agreement)} of channels land in the same group. Fifty titles average out the noise of single titles, so the ordering of channels is largely a matter of vocabulary even though the title-level call is not.

In one line: vocabulary says roughly where a channel sits, not how any single title reads. The judge reacts to framing, to how the words are put together, and that is the evidence that the labels measure stance rather than subject.

{table(lex[lex.judge == judge].assign(judge=jname), ['judge', 'n_titles', 'coverage', 'accuracy', 'kappa', 'partisan_titles_lexicon_neither', 'side_agreement_when_both_partisan', 'recall_left', 'recall_right', 'channel_spearman', 'channel_group_agreement'], fmt='{:.2f}')}
"""


def doc_leaning() -> str:
    ls = _json("leaning_label_shares.json"); summ = _json("leaning_summary.json")
    bc = rd("leaning_by_creator.csv"); gs = rd("leaning_groups.csv"); words = rd("leaning_words.csv"); labs = rd("leaning_labels.csv.gz")
    sd = rd("leaning_self_description.csv"); sdc = rd("leaning_self_description_channels.csv")
    shr = _opt("leaning_split_half.csv"); stab = _opt("leaning_stability.csv"); stab_ch = _opt("leaning_stability_channels.csv"); gm = _opt("leaning_by_group_month.csv")
    allo = _opt("allotax_summary.csv"); allo_c = _opt("allotax_contributions.csv")
    lo_s = _opt("leaning_logodds_summary.csv"); lo_ag = _opt("leaning_logodds_agreement.csv"); lex = _opt("leaning_lexicon_validation.csv")
    judge = summ["judge_of_record"]; jname = _mname(judge); eps = float(summ.get("threshold", 0.05))
    shares = ls["label_shares"]; counts = ls["label_counts"]
    n_l, n_n, n_r = (int(summ["groups"].get(g, 0)) for g in ("left", "neutral", "right"))
    gs2 = gs.copy(); gs2["group"] = gs2.group.map(lambda g: f"{g} channels")
    sd_row = sd.iloc[0]; sd_dis = sdc[sdc.self_declared != sdc.judge_sign]
    miss_txt = ("" if len(sd_dis) == 0 else f" (the one miss is {sd_dis.creator.iloc[0]} at {sd_dis.score.iloc[0]:+.2f})" if len(sd_dis) == 1 else f" ({len(sd_dis)} misses: {', '.join(sd_dis.creator)})")
    ext = bc.sort_values("score")
    neutral = bc[bc.group == "neutral"].sort_values("score")
    wj = words[words.model == judge]
    right_w = wj.sort_values("z", ascending=False).head(20); left_w = wj.sort_values("z").head(20)
    rng = np.random.RandomState(SEED)
    ex = pd.concat([labs[labs[judge] == lab].sample(4, random_state=rng)[["creator", "title_raw", judge]] for lab in ("left", "right", "neither")]).rename(columns={judge: "label"})
    runs = [r for r in read_jsonl(RUNTIMES) if r["stage"] == "stage7_leaning" and r.get("calls")]
    cc_calls = sum(r.get("calls", 0) for r in runs); cc_min = sum(r.get("seconds", 0) for r in runs) / 60; cc_cost = sum(r.get("reported_cost_usd", 0) or 0 for r in runs)
    n50, nbase = int((bc.n_titles >= 50).sum()), int((bc.n_titles < 50).sum())
    sh_j = shr.iloc[0] if shr is not None and len(shr) else None
    st_j = stab.iloc[0] if stab is not None and len(stab) else None
    movers = stab_ch.reindex(stab_ch.change.abs().sort_values(ascending=False).index).head(8) if stab_ch is not None and len(stab_ch) else None
    rel = ""
    if sh_j is not None and st_j is not None:
        rel = (f" The channel score is reliable: two random halves of a channel's titles rank the {int(sh_j.n_channels)} channels with 50 titles the same way (split-half Spearman {sh_j.split_half_spearman_mean:.2f}), "
               f"and the original 16-title draw ranks them the same way as the {int(stab_ch.n_topup.median())} titles drawn later from other months (Spearman {st_j.spearman_base_vs_topup:.2f}).")
    gm_tab = None; gm_txt = ""
    if gm is not None and len(gm):
        piv = gm.pivot(index="group", columns="month", values="score").reindex(["left", "neutral", "right"])
        piv.insert(0, "titles / month", gm.groupby("group").n_titles.mean().round(0).astype(int).astype(str).reindex(piv.index))
        piv.index = piv.index.map(lambda g: f"{g} channels"); gm_tab = piv.reset_index()
        rng_txt = "; ".join(f"{g} {'ranges ' if i == 0 else ''}from {piv.loc[g].iloc[1:].astype(float).min():+.2f} to {piv.loc[g].iloc[1:].astype(float).max():+.2f}" for i, g in enumerate(piv.index))
        mp = gm.groupby("month").apply(lambda g: np.average(g.partisan_share, weights=g.n_titles), include_groups=False)
        gm_txt = f"It did not move: {rng_txt}; the share of all sampled titles read as partisan stays between {pct(mp.min())} and {pct(mp.max())} every month. Whatever the news did over the year, a channel's title stance is a fixed property of the channel, which is also what document 6 found for style."
    return f"""# 14. Political leaning from titles alone

**The question and the design.** Can a channel's political leaning be read off its titles? The analysis has two levels, and everything in this document belongs to one of them.

1. **Titles.** A frontier model ({jname}, through the Claude Code CLI) reads each sampled title on its own, never the channel name, and labels it *left*, *right* or *neither* by the viewpoint the wording signals. Level 1 analyses those labels: how many titles read each way, and which words carry each reading.
2. **Channels.** Each channel's sampled titles give it a score, (titles read right − titles read left) / titles sampled, from −1 (every title read left) to +1 (every title read right). The score sorts the channels into three groups: **left** below −{eps:g}, **right** above +{eps:g}, **neutral** between. Level 2 analyses the groups: how many channels land in each, how reliable the score is, and what the groups' whole output looks like when their titles are compared as bodies of text.

Everything here is *model-perceived* leaning: how a careful, reader-like model reads the wording of a title. The sample is 16 titles per channel plus a top-up to 50, spread evenly across the months, for every channel with at least 50 edited uploads ({n50} of {len(bc)} channels; the other {nbase} stay at their base draw): {len(labs):,} titles in all.

## The finding in one paragraph

{jname} reads {pct(shares.get('neither', 0))} of titles as neither, {pct(shares.get('left', 0))} as left and {pct(shares.get('right', 0))} as right. Sorted by their scores, {n_l} channels are left, {n_r} right and {n_n} neutral, and the score matches the one thing the channels say about themselves: all {int(sd_row.n_self_declared)} channels whose YouTube description declares a leaning land on the declared side{miss_txt}.{rel} The words behind the labels are stance words rather than subjects: the *right* vocabulary is {', '.join(right_w.word.head(8))}; the *left* vocabulary is {', '.join(left_w.word.head(8))}. Applied to everything the left and right channels published, the same words separate the two groups' whole output, with the year's shared subjects (Trump, Iran, the war) at the top of both.

## Level 1: titles

### What the judge labelled

Over the {ls['n_labelled']:,} labelled titles:

{table(pd.DataFrame([{'label': k, 'titles': counts[k], 'share': shares[k]} for k in ('left', 'neither', 'right')]), fmt='{:.3f}')}

Four titles of each label, drawn at random:

{table(ex)}

Six in ten titles carry no readable stance: plain news headlines, non-political titles, or political titles whose wording does not tip either way. The labels live on the other four in ten, and the rest of this level asks what those titles have in their words.

### The vocabulary of left-read and right-read titles

Titles {jname} labelled left ({int(wj.n_left_titles.iloc[0]):,}) vs right ({int(wj.n_right_titles.iloc[0]):,}), compared two ways: weighted log-odds (which words are over-used on one side, given how often they appear at all) and rank-turbulence divergence, read off an allotaxonograph (Dodds et al. 2023), the instrument built for exactly this comparison of two Zipfian systems.

![Allotaxonograph, titles.](figures/14_allotax_titles.png)
*Allotaxonograph of the titles {jname} read as left (system 1, left flank) against the titles it read as right (system 2, right flank); drawn by the Computational Story Lab's own renderer (allotaxonometer-ui), rank-turbulence divergence with α = 1/3. Diamond: every word placed by its rank in each system on log axes, the rank-rank plane rotated so that words used equally sit on the vertical centre line; colour = how many words share a cell; the words named along the flanks are the furthest from the centre line at each frequency, i.e. the most one-sided. Contour lines join equal contributions to the divergence. Right: the {int(allo.loc[allo.comparison == 'titles', 'bars'].iloc[0]) if allo is not None and 'bars' in allo.columns and (allo.comparison == 'titles').any() else 40} largest contributions, each with its two ranks (system 1 ⇋ system 2), grey bars pulling left, blue bars pulling right. Below the diamond: the balance of tokens, types and exclusive types between the two systems.*

{_allotax_titles(allo, allo_c, jname)}

The two instruments disagree about one word, and the disagreement is instructive: "trump" is the most over-used word on the left by log-odds ({int(wj.loc[wj.word == 'trump', 'count_left'].iloc[0]) if (wj.word == 'trump').any() else 0:,} occurrences in left-read titles against {int(wj.loc[wj.word == 'trump', 'count_right'].iloc[0]) if (wj.word == 'trump').any() else 0:,} in right-read ones), but it sits at the apex of the diamond, because it is the top-ranked word on both sides; rank turbulence measures who *changes* the ordering, not who wins the count.

For reference, the fifteen most one-sided words each way with their z and their occurrences on each side (the full table, with the raw log-odds, the ranks and each word's contribution to the divergence, is `leaning_words.csv`):

{table(right_w.head(15), ['word', 'z', 'count_right', 'count_left'], fmt='{:.1f}')}

{table(left_w.head(15), ['word', 'z', 'count_left', 'count_right'], fmt='{:.1f}')}

Read as a map of the two grammars of attack: the right's titles are about Democrats, fraud, women and trans issues, the woke, Charlie Kirk, California and Newsom, Islam and Mamdani; the left's are about Trump, MAGA, the wars (Iran, Israel, Gaza, Venezuela), Epstein, Vance and Noem, and they carry the outrage furniture (breaking, panics).

### A left / right / neither lexicon, and what a word list can and cannot do

{_logodds_section(lo_s, lo_ag, lex, judge, jname)}

## Level 2: channels

### From titles to channel groups

A channel's score is the balance of its sampled titles, and the groups follow from the score alone; no other information about the channel enters. The {len(bc)} channels sort as:

{table(gs2, ['group', 'n_channels', 'n_titles', 'mean_score', 'min_score', 'max_score', 'mean_left', 'mean_neither', 'mean_right'], fmt='{:.2f}')}

![Scores.](figures/14_leaning_scores.png)
*Left: each channel's score against the share of its titles read as neither; the dashed lines are the group thresholds at ±{eps:g}. Right: the distribution of scores, coloured by group.*

![Every channel.](figures/14_leaning_channels.png)
*Every channel's sampled titles: the share labelled left (blue), neither (grey) and right (orange), sorted by score, most left-reading first; the score at the right is coloured by group.*

![Group composition.](figures/14_leaning_group_composition.png)
*Mean composition of a channel's titles in each group.*

The most left-reading and most right-reading channels:

{table(ext.head(12), ['creator', 'n_titles', 'score', 'group'], fmt='{:.2f}')}

{table(ext.tail(12).iloc[::-1], ['creator', 'n_titles', 'score', 'group'], fmt='{:.2f}')}

With 50 titles no channel scores ±1 ({int((bc.score.abs() >= 0.9).sum())} sit at or beyond ±0.90): even the most one-sided channels title one video in twenty as plain news. The {n_n} neutral channels, whose sampled titles balance or read mostly as neither: {', '.join(neutral.creator)}.

### How much a channel's score depends on which titles were drawn

Two checks, both on the {int(sh_j.n_channels) if sh_j is not None else n50} channels with 50 labelled titles. Split-half: a channel's titles are split at random into two halves of {int(sh_j.median_titles_per_half) if sh_j is not None else 25}, each half scored, and the two channel rankings correlated (Spearman; mean and SD over 20 random splits). Base vs top-up: the score from the original 16-title draw against the score from the disjoint top-up titles, which were drawn from other months.

{table(shr.assign(judge=jname) if shr is not None else None, ['judge', 'n_channels', 'median_titles_per_half', 'split_half_spearman_mean', 'split_half_spearman_sd'], fmt='{:.3f}')}

{table(stab.assign(judge=jname) if stab is not None else None, ['judge', 'n_channels', 'spearman_base_vs_topup', 'spearman_base_vs_all', 'mean_abs_change', 'group_changed', 'sign_flipped'], fmt='{:.3f}')}

*`group_changed`: channels whose group differs between the 16-title and the 50-title score; `sign_flipped`: the subset that went from left to right or the reverse.*

![Stability of the channel score.](figures/14_leaning_stability.png)
*Left: every ranked channel's score from the original 16 titles against its score from the 34 top-up titles, coloured by its final group; the labelled points are the largest movers. Right: the two reliability figures.*

The largest movers between the 16-title and the 50-title score:

{table(movers, ['creator', 'group', 'score_base', 'score_topup', 'score_all', 'group_base', 'group_all'], fmt='{:.2f}') if movers is not None else '_(none)_'}

### A model-free anchor

Only {int(sd_row.n_self_declared)} channels put a leaning word in their own YouTube description ({int(sd_row.n_right_declared)} right, {int(sd_row.n_left_declared)} left; rule and hand corrections in `leaning.py`), nearly all of them channels that were never in doubt, so agreement here rules out one gross failure, a judge that reads self-declared conservatives as left, and says nothing about the rest of the landscape. {jname} puts {pct(float(sd_row.agreement_with_self_description))} of them on their declared side{miss_txt}.

{table(sd.assign(judge=jname), ['judge', 'n_self_declared', 'n_right_declared', 'n_left_declared', 'agreement_with_self_description'], fmt='{:.3f}')}

### The groups' whole output

The groups were defined from 50 sampled titles per channel; the channels published far more. Comparing everything the {n_l} left channels published with everything the {n_r} right channels published (every unique edited upload in the creator-balanced subset{f", {int(allo.loc[allo.comparison == 'channels', 'n_titles_1'].iloc[0]):,} vs {int(allo.loc[allo.comparison == 'channels', 'n_titles_2'].iloc[0]):,} titles" if allo is not None and (allo.comparison == 'channels').any() else ''}) asks whether the vocabulary that separated the labelled titles separates the groups' bodies of work, with no label on any individual title.

![Allotaxonograph, channels.](figures/14_allotax_channels.png)
*Left channels (system 1) against right channels (system 2), every title; same instrument and α as above.*

{_allotax_channels(allo, allo_c)}

![Log-odds, channels.](figures/14_logodds_channels.png)
*Weighted log-odds of every word in the left channels' titles against the right channels', same construction as the titles figure.*

### Does perceived leaning move over the year?

The top-up titles were spread evenly across months, so the sample supports a group-level look at whether the balance of partisan titles moved between January and September (a channel contributes about five titles a month, so channel-level months are not readable):

{table(gm_tab, fmt='{:+.2f}') if gm_tab is not None else '_(not computed)_'}

{gm_txt}

## Method

1. **Sample.** Every creator gets a base draw of 16 unique edited-upload titles (seed 20260914; creators with fewer than 16 uploads topped up from live VODs). Creators with at least 50 unique uploads are then topped up to 50 with further uploads spread evenly across months (round-robin over the months, random within month, its own random stream), so the extra titles never depend on which month a creator posted most in: {len(labs):,} titles, {n50} creators at 50, {nbase} at their base.
2. **Labelling.** One prompt (in `leaning.py` and the methods appendix): label the viewpoint the title's own wording signals as left, right or neither, with three anchoring examples; temperature 0; the judge sees the title text only, numbered 1 to 20, never the channel name; titles are sent in a seeded random order so that a batch mixes channels; every response cached. {jname} runs through the Claude Code CLI in print mode on a Claude Max subscription ({cc_calls:,} calls, {cc_min:.0f} minutes; the CLI reported an equivalent API cost of ${cc_cost:.2f}, not charged).
3. **Scores and groups.** Per channel: shares of left / right / neither and score = (right − left) / n over its sampled titles; left below −{eps:g}, right above +{eps:g}, neutral between.
4. **Reliability.** Split-half: channels with at least 32 labelled titles, two random halves, Spearman between the two channel rankings, 20 splits. Base vs top-up: the base-draw score against the top-up score per channel (disjoint titles), and the group at 16 titles against the group at 50.
5. **The anchor.** A channel counts as self-declared right or left when its YouTube description contains leaning words (conservative, MAGA, libertarian, right-wing ... vs progressive, leftist, socialist, liberal ...), with nine hand corrections for phrases like "liberal democracy" or "former liberal"; agreement is the share of those channels whose score has the declared sign.
6. **Words.** Weighted log-odds with an informative Dirichlet prior (alpha0 = 500; Monroe, Colaresi and Quinn 2008) and rank-turbulence divergence (alpha = 1/3; Dodds et al. 2023) on the vocabulary tokens of document 11, for the left-read vs right-read titles and for the left vs right channels' whole output. The divergence follows the allotaxonometer's conventions exactly (tied ranks over the union of both vocabularies, absent words at the last tied rank, the sum normalised so that two vocabularies with no word in common give D = 1); `textstats.rank_turbulence_divergence` reproduces the library's per-word contributions to machine precision.
7. **Log-odds lexicon.** Every word with 3+ occurrences in the two systems together, right against left; right at z ≥ 1.96, left at z ≤ −1.96, neither otherwise; the same for the channel groups, and Cohen's kappa of the classes between the two over their shared words. The lexicon check: the labelled titles split into five folds by channel, the lexicon built on four folds and applied to the fifth (a title is left when it holds more left-class than right-class words, right the other way, neither on a tie or no classified word), then agreement with the judge's labels title by title and channel by channel (`leaning_lexicon.py`).
8. **Allotaxonographs.** Drawn by allotaxonometer-ui {allo.allotaxonometer_ui.iloc[0] if allo is not None else ''} (the Computational Story Lab's Svelte renderer, the same code behind the lab's web app and py-allotax) through Node and Puppeteer (`pipeline_titles/allotax.py`, `pipeline_titles/allotax_js/`), from the same word counts as the tables (`allotax_summary.csv`, top contributions in `allotax_contributions.csv`).
9. **Months.** The labels by channel group x month (`leaning_by_group_month.csv`): titles, creators, partisan share, left and right shares, score.

## Limitations

- **This is perceived leaning.** A model reads a title the way an attentive reader would, and readers disagree. No human panel was used, by choice: one reader cannot supply political ground truth, and a balanced panel is a study of its own. A blind 200-title sheet exists (`leaning_human_sheet.csv`, still unfilled) for anyone who wants a single-reader reliability check.
- **One judge.** Every number here is one model's reading, and a model reads a title the way it was trained to; a second frontier model of a different family would be the natural robustness check (`--models <alias>` takes any Claude Code model alias).
- **The groups are a cut on a continuous score.** ±{eps:g} is one title in twenty; a channel at −0.06 and one at −0.04 differ by one label. The score is the measurement, the group is a convenience for comparing bodies of text, and the neutral group mixes channels whose titles balance with channels whose titles are mostly plain news.
- **Ten words carry little stance.** Six in ten titles are neither, so a channel's score rests on a minority of its titles. At 50 titles the score moves in steps of 0.02 and the split-half reliability is {sh_j.split_half_spearman_mean:.2f}; the {nbase} channels with fewer than 50 uploads still sit at 16 titles or fewer and move in steps of 1/16.
- **Target and stance blur at the margin.** Hostile-to-Trump wording reads left even when it is a wire headline or an anti-war right channel's; the neutral group and the left tail hold both kinds. Prompt v2 (which also asks for the target) exists in `leaning.py` and was not run at scale.
- **The anchor is small.** Self-descriptions cover {int(sd_row.n_self_declared)} channels and say what a channel claims; agreement with them is a sanity check, not accuracy.
- **Month-level reading is group-level only.** Five titles per channel-month is not a monthly channel score; the base 16 were drawn without regard to month, so the monthly table leans on the top-up.

Files: `leaning_labels.csv.gz`, `leaning_label_shares.json`, `leaning_summary.json`, `leaning_by_creator.csv`, `leaning_groups.csv`, `leaning_self_description.csv`, `leaning_self_description_channels.csv`, `leaning_words.csv`, `leaning_split_half.csv`, `leaning_stability.csv`, `leaning_stability_channels.csv`, `leaning_by_group_month.csv`, `leaning_logodds.csv`, `leaning_logodds_summary.csv`, `leaning_logodds_agreement.csv`, `leaning_lexicon_validation.csv`, `leaning_lexicon_channels.csv`, `leaning_lexicon_titles.csv`, `allotax_summary.csv`, `allotax_contributions.csv`.
"""
