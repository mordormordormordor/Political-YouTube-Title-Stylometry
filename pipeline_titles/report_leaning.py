"""Document 14: political leaning from titles, three models (rendered by report_sections.write_all)."""

from __future__ import annotations

import json

import numpy as np
import pandas as pd

from pipeline_titles.common import ANALYSIS_DIR as A, RUNTIMES, read_jsonl
from pipeline_titles.report_sections import lane, pct, rd, table


def _mname(c: str) -> str:
    c = c.replace("label_", "").replace("_score", "")
    if c.startswith("claude_code_"):
        return "Claude " + c.replace("claude_code_", "").replace("_", " ").title()
    return c.replace("_", ":", 1).replace("_", ".")


def _opt(name: str) -> pd.DataFrame | None:
    return rd(name) if (A / name).exists() else None


def _allotax_reading(allo: pd.DataFrame | None, allo_c: pd.DataFrame | None, jname: str) -> str:
    if allo is None or allo_c is None or not (allo.comparison == "opus").any():
        return "_(allotaxonographs not rendered on this run: see the README for the Node step)_"
    r = allo[allo.comparison == "opus"].iloc[0]; c = allo_c[allo_c.comparison == "opus"]
    left = c[c.side == "system_1"].head(8).type.tolist(); right = c[c.side == "system_2"].head(8).type.tolist()
    return (f"How to read it. The two vocabularies overlap less than the label shares suggest: D<sup>R</sup><sub>1/3</sub> = {r.divergence:.3f}, with {pct(r.exclusive_share_1)} of the left-read words never appearing in a right-read title and {pct(r.exclusive_share_2)} the other way. "
            f"The apex is shared (trump, iran, war: the year's subjects), and the divergence is carried by the flanks: on the left {', '.join(left)}; on the right {', '.join(right)}. "
            f"The bottom edges of the diamond, where the dark cells run, are the words used once on one side and never on the other, which is where the labelled sample's smallness shows ({int(r.n_types_1):,} and {int(r.n_types_2):,} word types from {int(r.n_titles_1):,} and {int(r.n_titles_2):,} titles).")


def _logodds_section(lo_s: pd.DataFrame | None, lo_ag: pd.DataFrame | None, lex: pd.DataFrame | None, judge: str, names: dict) -> str:
    if lo_s is None or lo_ag is None or lex is None or not (lo_s.comparison == "opus").any():
        return "_(not computed on this run)_"
    cut = float(lo_s.cutoff_z.iloc[0])
    cname = {"opus": names.get("label_claude_code_opus", "Claude Opus"), "gemma": names.get("label_gemma3_12b", "Gemma"), "qwen": names.get("label_qwen3_14b", "Qwen"), "consensus": "all three agree", "lanes": "the two lanes"}
    t = lo_s.copy(); t["comparison"] = t.comparison.map(cname); t["share_classified"] = (t.n_left + t.n_right) / t.n_words
    ag = lo_ag.copy(); ag["a"] = ag.a.map(cname); ag["b"] = ag.b.map(cname)
    pick = lambda a, b: lo_ag[((lo_ag.a == a) & (lo_ag.b == b)) | ((lo_ag.a == b) & (lo_ag.b == a))].iloc[0]
    oq, og, ol = pick("opus", "qwen"), pick("opus", "gemma"), pick("opus", "lanes")
    sw_oq = [w.split(" (")[0] for w in str(oq.side_switchers).split(", ") if w and w != "nan"]
    sw_ol = [w.split(" (")[0] for w in str(ol.side_switchers).split(", ") if w and w != "nan"]
    lj = lex[lex.judge == judge].iloc[0]; lex2 = lex.copy(); lex2["judge"] = lex2.judge.map(names)
    conf = json.loads(lj.confusion)
    n_neither = sum(conf["neither"].values()); n_left = sum(conf["left"].values()); n_right = sum(conf["right"].values())
    return f"""The allotaxonograph ranks words by how far they move between the two rankings; weighted log-odds asks a different question, whether a word is over-used on one side *given how common it is overall*, and gives every word a z-score, so a cutoff turns the vocabulary into a three-way lexicon: right at z ≥ {cut:g}, left at z ≤ −{cut:g}, neither otherwise (the two-sided 5 % level; words with fewer than 3 occurrences are not classified).

![Log-odds, judge of record.](figures/14_logodds_opus.png)
*Left: every word by its z (vertical) and its frequency (horizontal, log scale) for the titles {names[judge]} read as left against those it read as right; blue = left-class, orange = right-class, grey = neither. Right: the 25 most one-sided words each way. Words beyond the axis cap (one of them "trump") are drawn at the edge with their z.*

How many words clear the cutoff, per comparison (the same five systems as the allotaxonographs):

{table(t, ['comparison', 'n_words', 'n_left', 'n_right', 'n_neither', 'share_classified', 'top_left', 'top_right'], fmt='{:.2f}')}

Only a few per cent of words are one-sided at this level for the labelled samples; the lanes, with ten times the titles, classify {pct(float(t.loc[t.comparison == 'the two lanes', 'share_classified'].iloc[0]))} of their vocabulary. Comparing the classes between comparisons over the words both classify (kappa over three classes; `same side` restricts to words both call partisan):

{table(ag, ['a', 'b', 'n_shared_words', 'kappa', 'both_partisan', 'same_side_when_both_partisan', 'z_spearman'], fmt='{:.2f}')}

Three things stand out. {names[judge]} and the lanes agree on direction almost perfectly ({pct(ol.same_side_when_both_partisan)} of the {int(ol.both_partisan)} words both call partisan point the same way; the low kappa is only the lanes classifying many more words), so the judge's left and right vocabularies are the lanes' vocabularies. That is consistency, not validation: the lanes were assigned by a model of the same family (Claude, from channel names, descriptions and a sample of titles; `lane_seed.py`), so two readings by related models agree with each other, which is the least surprising outcome, and the lanes' own log-odds is only as independent of the judge as that assignment is. {names[judge]} and Gemma mostly agree too ({pct(og.same_side_when_both_partisan)} same side, kappa {og.kappa:.2f}). {names[judge]} and Qwen agree on the side of {pct(oq.same_side_when_both_partisan)} of the words both classify; the words that switch sides between them are {', '.join(sw_oq[:8])}{'...' if len(sw_oq) > 8 else ''}: Qwen's "right" is the vocabulary of talking *about* the right (trump, fox, gop, noem), which for the frontier model reads left. Between the judge and the lanes the switchers are {', '.join(sw_ol) if sw_ol else 'none'}, show-name and topic words rather than stance words.

**What a word list can do on its own.** If the judge's reading were vocabulary, a lexicon built from its own labels should reproduce them. It does not, quite: built out of fold (five folds by channel, so no channel's titles help classify themselves) and applied to titles by majority of classified words, the lexicon agrees with {names[judge]} on {pct(lj.accuracy)} of titles (kappa {lj.kappa:.2f}); it puts a word from the list into {pct(lj.coverage)} of titles; of the titles the judge called partisan it leaves {pct(lj.partisan_titles_lexicon_neither)} as neither, and where both call a title partisan they pick the same side {pct(lj.side_agreement_when_both_partisan)} of the time. The errors are the interesting part: the lexicon calls {pct(conf['neither']['left'] / n_neither)} of the judge's *neither* titles left and {pct(conf['neither']['right'] / n_neither)} right, because a plain news headline that mentions MAGA, Epstein or Iran carries left-class words without a left stance, and it recovers the judge's right titles worse ({pct(lj.recall_right)} recall) than its left ones ({pct(lj.recall_left)}), because the right's stance words (woke, fraud, women) are rarer than the left's subject words. At channel level the list does much better, Spearman {lj.channel_spearman:.2f} with the judge's channel score and lane AUC {lj.channel_lane_auc:.2f}: fifty titles average the noise out, and the ordering of channels is largely vocabulary; the title-level call is not.

![Lexicon against the judge.](figures/14_lexicon_vs_judge.png)
*Left: each channel's score from the out-of-fold lexicon classes against its score from the judge's labels. Right: the lexicon's class against the judge's label, title by title (row shares).*

The same check for every judge:

{table(lex2, ['judge', 'n_titles', 'coverage', 'accuracy', 'kappa', 'partisan_titles_lexicon_neither', 'side_agreement_when_both_partisan', 'recall_left', 'recall_right', 'channel_spearman', 'channel_lane_auc'], fmt='{:.2f}')}

The lanes' log-odds, for reference (the lexicon of what each lane publishes, no judge involved):

![Log-odds, lanes.](figures/14_logodds_lanes.png)
*Left-commentary against right-commentary channels, same construction. The left lane's list is Trump and the administration plus show furniture (let, talk, hour); the right lane's is Democrats, women, woke, fraud, Mamdani and America.*
"""


def _allotax_lanes_reading(allo: pd.DataFrame | None, allo_c: pd.DataFrame | None) -> str:
    if allo is None or allo_c is None or not (allo.comparison == "lanes").any():
        return "_(not rendered on this run)_"
    r = allo[allo.comparison == "lanes"].iloc[0]; c = allo_c[allo_c.comparison == "lanes"]
    left = c[c.side == "system_1"].head(10).type.tolist(); right = c[c.side == "system_2"].head(10).type.tolist()
    return (f"D<sup>R</sup><sub>1/3</sub> = {r.divergence:.3f}: the lanes' whole outputs are closer to each other than the judge's left-read and right-read titles are, as they should be, since most of what either lane publishes is the shared news of the year (the apex again: trump, iran, war, ice). "
            f"The words that separate them are the same words the judge found, now without any judge: the left lane's flank is {', '.join(left)}; the right lane's is {', '.join(right)}. "
            f"Show furniture shows up here too (tyt, hour, talk, let on the left: The Young Turks' and the talk shows' title templates; warroom and jlp on the right), which is the price of comparing channels rather than labelled titles; and the right lane, with 75 channels to the left's 48, brings the larger vocabulary: {pct(r.exclusive_share_2)} of its words never appear in a left-lane title, against {pct(r.exclusive_share_1)} the other way.")


def doc_leaning() -> str:
    ag = json.loads((A / "leaning_agreement.json").read_text()); summ = json.loads((A / "leaning_summary.json").read_text())
    bc = rd("leaning_by_creator.csv"); val = rd("leaning_lane_validation.csv"); con = rd("leaning_lane_contradictions.csv")
    bl = rd("leaning_by_lane.csv"); words = rd("leaning_words.csv"); labs = rd("leaning_labels.csv")
    sd = rd("leaning_self_description.csv"); sdc = rd("leaning_self_description_channels.csv")
    shr = _opt("leaning_split_half.csv"); stab = _opt("leaning_stability.csv"); stab_ch = _opt("leaning_stability_channels.csv"); lm = _opt("leaning_by_lane_month.csv")
    allo = _opt("allotax_summary.csv"); allo_c = _opt("allotax_contributions.csv")
    lo_s = _opt("leaning_logodds_summary.csv"); lo_ag = _opt("leaning_logodds_agreement.csv"); lex = _opt("leaning_lexicon_validation.csv")
    cols = ag["models"]; names = {c: _mname(c) for c in cols}
    judge = summ["judge_of_record"]; jname = names[judge]
    vj = val[val.score == judge + "_score"].iloc[0]
    shares = pd.DataFrame(ag["label_shares"]).T.reindex(columns=["left", "neither", "right"]).reset_index().rename(columns={"index": "model"}); shares["model"] = shares.model.map(names)
    pairs = pd.DataFrame([{"models": f"{names[p['a']]} vs {names[p['b']]}", "kappa (3 labels)": p["kappa"], "exact agreement": p["exact_agreement"], "kappa (partisan titles only)": p["kappa_political_only"]} for p in ag["pairs"]])
    side_by_lane = bc.groupby("lane").judge_side.value_counts().unstack(fill_value=0).reindex(columns=["left", "neither / unclear", "right"], fill_value=0).reset_index()
    side_by_lane["lane"] = side_by_lane.lane.map(lane)
    bl2 = bl.copy(); bl2["lane"] = bl2.lane.map(lane)
    ren = {f"{c}_score_mean": names[c] + " score" for c in cols} | {f"{c}_neither_mean": names[c] + " 'neither'" for c in cols}
    val2 = val.copy(); val2["score"] = val2.score.map(lambda s: names.get(s.replace("_score", ""), s))
    sd2 = sd.copy(); sd2["score"] = sd2.score.map(lambda s: names.get(s.replace("_score", ""), s))
    sd_dis = sdc[sdc.self_declared != sdc.judge_side_sign].copy(); sd_dis["lane"] = sd_dis.lane.map(lane)
    cj = con[con.score == judge + "_score"].copy(); cj["lane"] = cj.lane.map(lane)
    ext = bc.sort_values("judge_score"); ext["lane"] = ext.lane.map(lane)
    wj = words[words.model == judge]
    right_w = wj.sort_values("z", ascending=False).head(20); left_w = wj.sort_values("z").head(20)
    per_model = {c: (words[words.model == c].sort_values("z", ascending=False).head(12).word.tolist(), words[words.model == c].sort_values("z").head(12).word.tolist()) for c in cols}
    wc = words[words.model == "consensus"]
    two = bc[bc.lane.isin(["left_commentary", "right_commentary"])]
    neither = {c: ag["label_shares"][c].get("neither", 0) for c in cols}
    other = [c for c in cols if c != judge]
    rho = {c: bc[judge + "_score"].corr(bc[c + "_score"], method="spearman") for c in other}
    ex = pd.concat([labs[labs.creator == c].head(5) for c in ("@MeidasTouch", "@PTLRadioShow")])[["creator", "title_raw"] + cols].rename(columns=names)
    runs = [r for r in read_jsonl(RUNTIMES) if r["stage"] == "stage7_leaning"]
    cc_runs = [r for r in runs if r.get("backend") == "claude-code" and r.get("calls")]
    cc_calls = sum(r.get("calls", 0) for r in cc_runs); cc_min = sum(r.get("seconds", 0) for r in cc_runs) / 60; cc_cost = sum(r.get("reported_cost_usd", 0) or 0 for r in cc_runs)
    ol_runs = [r for r in runs if r.get("backend", "ollama") == "ollama" and r.get("calls")]
    ol_calls = sum(r.get("calls", 0) for r in ol_runs); ol_min = sum(r.get("seconds", 0) for r in ol_runs) / 60
    gem = [c for c in cols if "gemma" in c]; gemma = gem[0] if gem else other[0]
    news = side_by_lane[side_by_lane.lane.isin(["wires & international", "US press", "US legacy TV"])]
    n50, nbase = int((bc.n_titles >= 50).sum()), int((bc.n_titles < 50).sum())
    n_all = int(ag["n_labelled_by_all"])
    miss_txt = (f"the one miss is {sd_dis.creator.iloc[0]} at {sd_dis.judge_score.iloc[0]:+.2f}, one title's worth from zero" if len(sd_dis) == 1 else
                (f"{len(sd_dis)} misses, all within ±0.10" if len(sd_dis) and sd_dis.judge_score.abs().max() <= 0.1 else f"{len(sd_dis)} misses"))
    # reliability numbers
    sh_j = shr[shr.model == judge].iloc[0] if shr is not None and (shr.model == judge).any() else None
    st_j = stab[stab.model == judge].iloc[0] if stab is not None and (stab.model == judge).any() else None
    shr2 = shr.copy() if shr is not None else None
    if shr2 is not None:
        shr2["model"] = shr2.model.map(names)
    stab2 = stab.copy() if stab is not None else None
    if stab2 is not None:
        stab2["model"] = stab2.model.map(names)
    movers = stab_ch.reindex(stab_ch.change.abs().sort_values(ascending=False).index).head(8).copy() if stab_ch is not None and len(stab_ch) else None
    if movers is not None:
        movers["lane"] = movers.lane.map(lane)
    changed = stab_ch[stab_ch.side_base != stab_ch.side_all].copy() if stab_ch is not None and len(stab_ch) else None
    flips = changed[(changed.side_base.isin(["left", "right"])) & (changed.side_all.isin(["left", "right"]))] if changed is not None else None
    reliability_sentence = ""
    if sh_j is not None and st_j is not None:
        reliability_sentence = (f" With 50 titles per ranked channel the frontier model's channel score is reliable: two random halves of a channel's titles rank the "
                                f"{int(sh_j.n_channels)} channels with 50 titles the same way (split-half Spearman {sh_j.split_half_spearman_mean:.2f}), and the score from the original "
                                f"16-title draw ranks them the same way as the score from the {int(stab_ch.n_topup.median())} titles drawn afterwards from other months "
                                f"(Spearman {st_j.spearman_base_vs_topup:.2f}); the 16-title result of the first pass was already the right ordering, and the top-up bought resolution, not a different answer.")
    # lane x month table for the judge: lanes with at least 50 titles in every month
    lm_tab = None
    if lm is not None and len(lm):
        ok_lanes = lm.groupby("lane").n_titles.min(); ok_lanes = ok_lanes[ok_lanes >= 50].index
        piv = lm[lm.lane.isin(ok_lanes)].pivot(index="lane", columns="month", values="score")
        piv = piv.loc[piv.mean(axis=1).sort_values().index]
        piv.insert(0, "titles / month", lm[lm.lane.isin(ok_lanes)].groupby("lane").n_titles.mean().round(0).astype(int).astype(str).reindex(piv.index))
        piv.index = piv.index.map(lane); lm_tab = piv.reset_index()
        rng_txt = "; ".join(f"{l} {'ranges ' if i == 0 else ''}from {piv.loc[l].iloc[1:].astype(float).min():+.2f} to {piv.loc[l].iloc[1:].astype(float).max():+.2f}" for i, l in enumerate(piv.index[:2].tolist() + piv.index[-1:].tolist()))
        month_partisan = lm.groupby("month").apply(lambda g: np.average(g.partisan_share, weights=g.n_titles), include_groups=False)
    return f"""# 14. Political leaning from titles alone

**The question.** Can a channel's political leaning be read off its titles, and what does a model actually react to when it reads one? Three models of different families label each sampled title as left, right or neither; a channel's score is the balance of right over left labels. Everything here is *model-perceived* leaning: how a careful, reader-like model reads the wording of a title, with the disagreement between models as the uncertainty. This is the second pass: the first labelled 16 titles per channel; this one keeps those 16 and adds 34 more, spread evenly across the months, for every channel with at least 50 edited uploads ({n50} of {len(bc)} channels; the other {nbase} stay at their base draw).

## The finding in one paragraph

A frontier model reads stance; the small local models mostly read subject.{reliability_sentence} {jname} labels {pct(neither[judge])} of titles neither, {pct(ag['label_shares'][judge].get('left', 0))} left and {pct(ag['label_shares'][judge].get('right', 0))} right, and its channel score matches the channels' own words: of the {int(sd.n_self_declared.iloc[0])} channels whose YouTube description declares a leaning ("conservative political commentator", "populist left perspective"), it puts {pct(float(sd.loc[sd.score == judge + '_score', 'agreement_with_self_description'].iloc[0]))} on the declared side ({miss_txt}). Against the lane proposal, a weaker yardstick because the lanes are themselves a model's assignment, it reaches an AUC of {vj.auc_right_vs_left_lane:.3f} and {pct(vj.accuracy_sign_vs_lane)} of the {int(vj.n_creators)} commentary channels. Gemma-3-12B gets most channels right and gained the most from the extra titles, but still misreads hostile coverage as the target's side; Qwen3-14B calls seven in ten titles neither and leans right on the rest, and more titles did not help it. The three agree on {pct(ag['all_models_agree_share'])} of titles, almost all of them "neither". The words behind the frontier model's labels are stance words: its *right* vocabulary is {', '.join(right_w.word.head(8))}; its *left* vocabulary is {', '.join(left_w.word.head(8))}, and "Trump PANICS" is left, as it should be, where the small models had it right.

![Scores by model and by lane.](figures/14_leaning_scores.png)
*Left: each channel's score from the two best models (−1 = every title read as left, +1 = every title read as right). Right: the judge-of-record score by lane, dots = channels.*

## How much a channel's score depends on which titles were drawn

Two checks, both on the {int(sh_j.n_channels) if sh_j is not None else n50} channels with 50 labelled titles. Split-half: a channel's titles are split at random into two halves of {int(sh_j.median_titles_per_half) if sh_j is not None else 25}, each half scored, and the two channel rankings correlated (Spearman; mean and SD over 20 random splits). Base vs top-up: the score from the original 16-title draw against the score from the disjoint top-up titles, which were drawn from other months.

{table(shr2, ['model', 'n_channels', 'median_titles_per_half', 'split_half_spearman_mean', 'split_half_spearman_sd'], fmt='{:.3f}') if shr2 is not None else '_(not computed)_'}

{table(stab2, ['model', 'n_channels', 'spearman_base_vs_topup', 'spearman_base_vs_all', 'lane_auc_base', 'lane_auc_all', 'mean_abs_change', 'side_changed', 'sign_flipped'], fmt='{:.3f}') if stab2 is not None else '_(not computed)_'}

*`lane_auc_base` / `lane_auc_all`: how well the score separates the left- and right-commentary lanes (same {int(st_j.n_commentary) if st_j is not None else 0} channels) from the 16 base titles alone and from all 50. `side_changed`: channels whose call (right above +0.05, left below −0.05, else neither) differs between the 16-title and the 50-title score; `sign_flipped`: the subset that went from left to right or the reverse.*

![Stability of the channel score.](figures/14_leaning_stability.png)
*Left: every ranked channel's score from the original 16 titles against its score from the 34 top-up titles ({jname}); the labelled points are the largest movers. Right: the two reliability figures per model.*

The three models fail the same test differently. For {jname}, the rankings from the two disjoint title sets agree at {st_j.spearman_base_vs_topup:.2f} and the split halves at {sh_j.split_half_spearman_mean:.2f}: {int(st_j.side_changed)} of {int(st_j.n_channels)} channels changed their call between 16 and 50 titles, {'all' if flips is not None and len(flips) and (flips.score_all.abs() <= 0.2).all() else 'most'} of them channels near zero crossing the ±0.05 line, and {int(st_j.sign_flipped)} went from one side to the other. For {names[gemma]} the extra titles mattered: its lane AUC on the same channels rose from {float(stab.loc[stab.model == gemma, 'lane_auc_base'].iloc[0]):.2f} to {float(stab.loc[stab.model == gemma, 'lane_auc_all'].iloc[0]):.2f}, so part of what looked like misreading at 16 titles was sampling noise on a noisy judge; its split-half reliability ({float(shr.loc[shr.model == gemma, 'split_half_spearman_mean'].iloc[0]):.2f}) is still well below the frontier model's, and its systematic error (below) did not go away. Qwen3-14B's score is close to unrepeatable (split-half {float(shr.loc[shr.model == 'label_qwen3_14b', 'split_half_spearman_mean'].iloc[0]) if shr is not None and (shr.model == 'label_qwen3_14b').any() else float('nan'):.2f}): its problem is not too few titles but what it reads in them.

The largest movers under {jname} between the 16-title and the 50-title score:

{table(movers, ['creator', 'lane', 'score_base', 'score_topup', 'score_all', 'side_base', 'side_all'], fmt='{:.2f}') if movers is not None else '_(none)_'}

Nothing moved by more than {float(st_j.max_abs_change):.2f}, and the movers are the channels whose 16 titles happened to be their loudest or quietest: Officer Tatum's base draw was almost all attack titles, Jackson Hinkle's base draw missed the anti-war titles that dominate his month-spread top-up.

## What each model sees

Label shares over the {n_all:,} titles all three labelled:

{table(shares, fmt='{:.3f}')}

Agreement between models (Cohen's kappa; the last column restricts to titles both called partisan):

{table(pairs, fmt='{:.2f}')}

All three agree on {pct(ag['all_models_agree_share'])} of titles; of those, {pct(ag['consensus_label_shares'].get('neither', 0))} are neither. Channel scores: Spearman {', '.join(f'{rho[c]:.2f} with {names[c]}' for c in other)} against {jname}.

Five MeidasTouch and five PTL Radio titles with all three labels, the case that separates the judges (both are left channels whose titles attack Trump; {jname} reads the wording, Gemma reads the name):

{table(ex)}

## Channel scores against two yardsticks

**The channels' own descriptions** (lane-independent: {int(sd.n_self_declared.iloc[0])} channels with a leaning word in their YouTube description, {int(sd.n_right_declared.iloc[0])} right, {int(sd.n_left_declared.iloc[0])} left; rule and hand corrections in `leaning.py`):

{table(sd2, ['score', 'n_self_declared', 'agreement_with_self_description'], fmt='{:.3f}')}

Channels where the judge's sign differs from their self-description ({len(sd_dis)}):

{table(sd_dis, ['creator', 'lane', 'self_declared', 'judge_side_sign', 'judge_score'], fmt='{:.2f}') if len(sd_dis) else '_(none)_'}

**The lane proposal** (consistency check only: `left_commentary` vs `right_commentary`):

{table(val2, ['score', 'n_creators', 'auc_right_vs_left_lane', 'accuracy_sign_vs_lane', 'n_nonzero', 'mean_score_left_lane', 'mean_score_right_lane'], fmt='{:.3f}')}

The judge of record is the model with the highest lane AUC ({jname}); the mean and consensus scores are shown for transparency. The mean of the three models now matches the judge on both yardsticks, which is what averaging a good judge with two noisy ones should do; it is not evidence that the small models add information.

Where every channel lands under the judge of record (score above +0.05 = right, below −0.05 = left):

{table(side_by_lane, fmt='{:.0f}')}

![Every channel's breakdown.](figures/14_leaning_channels.png)
*Every channel: the share of its sampled titles the judge of record labels left (blue), neither (grey) and right (orange), sorted from most left-reading to most right-reading, lane after the handle, score at the right.*

![Lane composition.](figures/14_leaning_lane_composition.png)
*Mean composition by lane.*

![Three models per channel.](figures/14_leaning_models_by_channel.png)
*The same channels with all three models' scores: circles = judge of record, squares = Gemma, triangles = Qwen. Where the small models' markers sit far from the circle is where they misread the channel.*

Two things in that table deserve a look. The news lanes are mostly *neither*, as they should be, but their partisan-read titles tilt left ({int(news['left'].sum())} channels left vs {int(news['right'].sum())} right across the wires, the press and legacy TV): the judge reads a title hostile to the administration as left even in a news headline, so part of that tilt is the target-versus-stance ambiguity that no model fully escapes. And the interview podcasts lean right as a lane ({int(side_by_lane.loc[side_by_lane.lane == 'interview podcasts', 'right'].iloc[0])} right, {int(side_by_lane.loc[side_by_lane.lane == 'interview podcasts', 'left'].iloc[0])} left), which the lane proposal, built on format rather than politics, did not encode; Rogan sits at exactly {float(bc.loc[bc.creator == '@joerogan', 'judge_score'].iloc[0]):+.2f} over 50 titles.

Lane means (all models; the 'neither' columns are the mean share of a channel's titles labelled neither):

{table(bl2, ['lane', 'n_creators'] + [f'{c}_score_mean' for c in cols] + [f'{c}_neither_mean' for c in cols], fmt='{:.2f}', rename=ren)}

The most left-reading and most right-reading channels under the judge of record:

{table(ext.head(12), ['creator', 'lane', 'n_titles', 'judge_score', 'judge_side'], fmt='{:.2f}')}

{table(ext.tail(12).iloc[::-1], ['creator', 'lane', 'n_titles', 'judge_score', 'judge_side'], fmt='{:.2f}')}

With 50 titles no channel scores ±1 any more ({int((bc.judge_score.abs() >= 0.9).sum())} sit at or beyond ±0.90): even the most one-sided channels title one video in twenty as plain news.

Commentary channels whose title-leaning contradicts their lane under the judge of record ({len(cj)} of {len(two)}):

{table(cj, ['creator', 'lane', 'value', 'implied_side', 'n_titles'], fmt='{:.2f}')}

These are not labelling accidents. The right-lane channels that read left or tie are the anti-war, anti-establishment right: Owen Shroyer, Jackson Hinkle and Dave Smith's Part of the Problem, whose titles attack the administration's wars and the Republican establishment in the vocabulary the left uses. Tariq Nasheed's and Phillip Scott's read right on the titles that attack Democrats. Tim Black and Jimmy Dore, contradictions at 16 titles, sit at {float(bc.loc[bc.creator == '@Tim_Black', 'judge_score'].iloc[0]):+.2f} and {float(bc.loc[bc.creator == '@thejimmydoreshow', 'judge_score'].iloc[0]):+.2f} with 50: split evenly, which is what their politics looks like on a left/right axis. They are the channels the axis fits worst, and a reason to treat the lane proposal as provisional.

## Does perceived leaning move over the year?

The top-up titles were spread evenly across months, so the sample supports a lane-level look at whether the balance of partisan titles moved between January and September ({jname} score, lanes with at least 50 sampled titles in every month; a channel contributes about five titles a month, so channel-level months are not readable):

{table(lm_tab, fmt='{:+.2f}') if lm_tab is not None else '_(not computed)_'}

It did not move: {rng_txt if lm_tab is not None else ''}; the share of all sampled titles read as partisan stays between {pct(month_partisan.min()) if lm_tab is not None else ''} and {pct(month_partisan.max()) if lm_tab is not None else ''} every month. Whatever the news did over the year, the channels' title stance is a fixed property of the channel, which is also what document 6 found for style.

## What the frontier model calls right and what it calls left

Titles {jname} labelled left ({int(wj.n_left_titles.iloc[0]):,}) vs right ({int(wj.n_right_titles.iloc[0]):,}), compared two ways: weighted log-odds (which words are over-used on one side, given how often they appear at all) and rank-turbulence divergence, read off an allotaxonograph (Dodds et al. 2023), the instrument built for exactly this comparison of two Zipfian systems.

![Allotaxonograph, judge of record.](figures/14_allotax_opus.png)
*Allotaxonograph of the titles {jname} read as left (system 1, left flank) against the titles it read as right (system 2, right flank); drawn by the Computational Story Lab's own renderer (allotaxonometer-ui), rank-turbulence divergence with α = 1/3. Diamond: every word placed by its rank in each system on log axes, the rank-rank plane rotated so that words used equally sit on the vertical centre line; colour = how many words share a cell; the words named along the flanks are the furthest from the centre line at each frequency, i.e. the most one-sided. Contour lines join equal contributions to the divergence. Right: the {int(allo.loc[allo.comparison == 'opus', 'bars'].iloc[0]) if allo is not None and 'bars' in allo.columns else 40} largest contributions, each with its two ranks (system 1 ⇋ system 2), grey bars pulling left, blue bars pulling right. Below the diamond: the balance of tokens, types and exclusive types between the two systems.*

{_allotax_reading(allo, allo_c, jname)}

The two instruments disagree about one word, and the disagreement is instructive: "trump" is the most over-used word on the left by log-odds ({int(wj.loc[wj.word == 'trump', 'count_left'].iloc[0]) if (wj.word == 'trump').any() else 0:,} occurrences in left-read titles against {int(wj.loc[wj.word == 'trump', 'count_right'].iloc[0]) if (wj.word == 'trump').any() else 0:,} in right-read ones), but it sits at the apex of the diamond, because it is the top-ranked word on both sides; rank turbulence measures who *changes* the ordering, not who wins the count, and on that reading the left's signature is maga, breaking, fox and donald, the right's is women, fraud, democrats and woke.

Right-labelled vocabulary (top 20 by weighted log-odds; `rtd_contribution` is the word's share of D, in per cent, signed positive when the word is more prominent in right-labelled titles; ranks are tied ranks over the union of both vocabularies, so a word absent from one side takes that side's last tied rank):

{table(right_w.assign(rtd_contribution=right_w.rtd_contribution * 100, rank_right=right_w.rank_right.map('{:g}'.format), rank_left=right_w.rank_left.map('{:g}'.format)), ['word', 'log_odds_right_vs_left', 'z', 'count_right', 'count_left', 'rank_right', 'rank_left', 'rtd_contribution'], fmt='{:.3f}')}

Left-labelled vocabulary (top 20 by weighted log-odds):

{table(left_w.assign(rtd_contribution=left_w.rtd_contribution * 100, rank_right=left_w.rank_right.map('{:g}'.format), rank_left=left_w.rank_left.map('{:g}'.format)), ['word', 'log_odds_right_vs_left', 'z', 'count_right', 'count_left', 'rank_right', 'rank_left', 'rtd_contribution'], fmt='{:.3f}')}

Read as a map of the two grammars of attack: the right's titles are about Democrats, fraud, women and trans issues, the woke, Charlie Kirk, California and Newsom, Islam and Mamdani; the left's are about Trump, MAGA, the wars (Iran, Israel, Gaza, Venezuela), Epstein, Vance and Noem, and they carry the outrage furniture (breaking, panics). With three times the titles of the first pass the lists are the same lists with steadier counts: every word in the first pass's top eight is still in the top twenty on its side. The same lists per model, and for the titles all three agree on (n = {int(wc.n_right_titles.iloc[0]) if len(wc) else 0} right, {int(wc.n_left_titles.iloc[0]) if len(wc) else 0} left):

{table(pd.DataFrame([{'model': names.get(c, c), 'right': ', '.join(per_model[c][0]), 'left': ', '.join(per_model[c][1])} for c in cols] + ([{'model': 'all three agree', 'right': ', '.join(wc.sort_values('z', ascending=False).head(12).word), 'left': ', '.join(wc.sort_values('z').head(12).word)}] if len(wc) else [])))}

The small models' lists are subject maps (Trump, GOP and Fox on Qwen's "right"; Hasan, Gaza and racism on its "left"; the named right personalities on Gemma's "right"); the frontier model's list is closer to a stance map. That difference is the whole story of this document. The same allotaxonograph for each of the other judges and for the all-agree set: [Gemma-3-12B](figures/14_allotax_gemma.png), [Qwen3-14B](figures/14_allotax_qwen.png), [all three agree](figures/14_allotax_consensus.png).

## Log-odds: a left / right / neither lexicon, and what a word list can and cannot do

{_logodds_section(lo_s, lo_ag, lex, judge, names)}

## The same instrument on the lanes

The allotaxonograph does not need a judge: applied to what the two commentary lanes actually published (every unique edited upload of the 48 left-commentary and 75 right-commentary channels in the creator-balanced subset, {int(allo.loc[allo.comparison == 'lanes', 'n_titles_1'].iloc[0]):,} vs {int(allo.loc[allo.comparison == 'lanes', 'n_titles_2'].iloc[0]):,} titles), it shows the two lanes' vocabularies directly, with no labelling in between.

![Allotaxonograph, lanes.](figures/14_allotax_lanes.png)
*Left-commentary channels (system 1) against right-commentary channels (system 2), same instrument and α.*

{_allotax_lanes_reading(allo, allo_c)}

## Method

1. **Sample.** Every creator gets a base draw of 16 unique edited-upload titles (seed 20260914; creators with fewer than 16 uploads topped up from live VODs). Creators with at least 50 unique uploads are then topped up to 50 with further uploads spread evenly across months (round-robin over the months, random within month, its own random stream), so the extra titles never depend on which month a creator posted most in: {len(labs):,} titles, {n50} creators at 50, {nbase} at their base. The base draw is unchanged from the first pass, so its labels were reused; only the top-up was labelled.
2. **Labelling.** The same prompt for all three judges (in `leaning.py` and the methods appendix): label the viewpoint the title's own wording signals as left, right or neither, with three anchoring examples; temperature 0, batches of 20, every response cached. The judges saw the title text only, numbered 1 to 20, never the channel name; but the batches follow the sample's order, so a batch holds 20 titles from one or two channels (base pass: 182 of 218 batches span two channels; top-up pass: 192 of 407 batches are a single channel), which gives the judge a channel's other titles as context for each call. Qwen3-14B and Gemma-3-12B run locally through Ollama ({ol_calls:,} calls over both passes, {ol_min:.0f} minutes, no cost); {jname} runs through the Claude Code CLI in print mode on a Claude Max subscription ({cc_calls:,} calls over both passes, {cc_min:.0f} minutes; the CLI reported an equivalent API cost of ${cc_cost:.2f}, not charged). Qwen returned no parseable label for {int(labs['label_qwen3_14b'].isna().sum()) if 'label_qwen3_14b' in labs.columns else 0} titles after three batch sizes; those rows are excluded from the three-way agreement figures only.
3. **Scores.** Per channel and model: shares of left / right / neither and score = (right − left) / n; a consensus score on titles all models labelled the same way; the mean of the models. The judge of record is the model whose score best separates the two commentary lanes; a channel is called right above +0.05, left below −0.05.
4. **Yardsticks.** Self-description: a channel counts as self-declared right or left when its YouTube description contains leaning words (conservative, MAGA, libertarian, right-wing ... vs progressive, leftist, socialist, liberal ...), with nine hand corrections for phrases like "liberal democracy" or "former liberal"; agreement is the share of those channels whose score has the declared sign. Lanes: AUC and sign accuracy over the two commentary lanes only.
5. **Reliability.** Split-half: channels with at least 32 labelled titles, two random halves, Spearman between the two channel rankings, 20 splits. Base vs top-up: the base-draw score against the top-up score per channel (disjoint titles), plus the lane AUC from each; `leaning_stability.csv`, per-channel values for the judge in `leaning_stability_channels.csv`.
6. **Words.** Right vs left titles per model and for the all-agree set: weighted log-odds with an informative Dirichlet prior (alpha0 = 500; Monroe, Colaresi and Quinn 2008) and rank-turbulence divergence (alpha = 1/3; Dodds et al. 2023) on the vocabulary tokens of document 11. The divergence follows the allotaxonometer's conventions exactly (tied ranks over the union of both vocabularies, absent words at the last tied rank, the sum normalised so that two vocabularies with no word in common give D = 1); `textstats.rank_turbulence_divergence` reproduces the library's per-word contributions to machine precision.
7. **Log-odds lexicon.** Weighted log-odds (as above) of every word with 3+ occurrences in the two systems together, right against left; a word is right at z ≥ 1.96, left at z ≤ −1.96, neither otherwise; the same for each judge, the all-agree set and the two lanes, and Cohen's kappa of the classes between comparisons over their shared words. The lexicon check: each judge's labelled titles split into five folds by channel, the lexicon built on four folds and applied to the fifth (a title is left when it holds more left-class than right-class words, right the other way, neither on a tie or no classified word), then agreement with the judge's labels title by title and channel by channel (`leaning_lexicon.py`).
8. **Allotaxonographs.** Drawn by allotaxonometer-ui {allo.allotaxonometer_ui.iloc[0] if allo is not None else ''} (the Computational Story Lab's Svelte renderer, the same code behind the lab's web app and py-allotax) through Node and Puppeteer (`pipeline_titles/allotax.py`, `pipeline_titles/allotax_js/`), from the same word counts as the tables; five comparisons (`allotax_summary.csv`, top contributions in `allotax_contributions.csv`).
9. **Months.** The judge's labels by lane x month (`leaning_by_lane_month.csv`): titles, creators, partisan share, left and right shares, score.

## Limitations

- **This is perceived leaning.** A model reads a title the way an attentive reader would, and readers disagree; the three-way agreement figures are the honest width of that disagreement. No human panel was used, by choice: one reader cannot supply political ground truth, and a balanced panel is a study of its own. A blind 200-title sheet exists (`leaning_human_sheet.csv`, still unfilled) for anyone who wants a single-reader reliability check.
- **Ten words carry little stance.** Six in ten titles are neither even for the best judge, so a channel's score rests on a minority of its titles. At 50 titles the score moves in steps of 0.02 and the split-half reliability is {sh_j.split_half_spearman_mean:.2f}, so the ranking is settled; the {nbase} channels with fewer than 50 uploads still sit at 16 titles or fewer and move in steps of 1/16.
- **The judge had batch context.** A title was never labelled alone: its batch-mates were mostly the same channel's other titles, so an ambiguous title ("Trump's plan for Iran") could be read by the company it kept. That inflates within-channel consistency, and with it the split-half figures, by an amount this run cannot measure. The clean test is to re-label a shuffled subsample (titles from random channels mixed in each batch) and compare; a few thousand titles would settle it.
- **Target and stance still blur at the margin.** Hostile-to-Trump wording reads left even when it is a wire headline or an anti-war right channel; the news-lane tilt and the Shroyer / Hinkle cases are that residue. Prompt v2 (which also asks for the target) exists in `leaning.py` and was not run at scale.
- **The yardsticks are weak.** Self-descriptions cover {int(sd.n_self_declared.iloc[0])} channels and say what a channel claims; the lane proposal is my own model-made assignment. Agreement with either is consistency, not accuracy.
- **The small models' failure is a model property, not a corpus property**, and it comes in two kinds: Gemma's is partly noise (more titles helped) and partly a systematic target-for-stance error (more titles did not help); Qwen's is systematic. Their word lists show what a 12-14B model uses as a partisan cue.
- **Month-level reading is lane-level only.** Five titles per channel-month is not a monthly channel score; the base 16 were drawn without regard to month, so the monthly table leans on the top-up.

Files: `leaning_labels.csv`, `leaning_agreement.json`, `leaning_summary.json`, `leaning_by_creator.csv`, `leaning_lane_validation.csv`, `leaning_lane_contradictions.csv`, `leaning_by_lane.csv`, `leaning_self_description.csv`, `leaning_self_description_channels.csv`, `leaning_words.csv`, `leaning_split_half.csv`, `leaning_stability.csv`, `leaning_stability_channels.csv`, `leaning_by_lane_month.csv`, `leaning_logodds.csv`, `leaning_logodds_summary.csv`, `leaning_logodds_agreement.csv`, `leaning_lexicon_validation.csv`, `leaning_lexicon_channels.csv`, `leaning_lexicon_titles.csv`, `allotax_summary.csv`, `allotax_contributions.csv`.
"""
