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


def doc_leaning() -> str:
    ag = json.loads((A / "leaning_agreement.json").read_text()); summ = json.loads((A / "leaning_summary.json").read_text())
    bc = rd("leaning_by_creator.csv"); val = rd("leaning_lane_validation.csv"); con = rd("leaning_lane_contradictions.csv")
    bl = rd("leaning_by_lane.csv"); words = rd("leaning_words.csv"); labs = rd("leaning_labels.csv")
    sd = rd("leaning_self_description.csv"); sdc = rd("leaning_self_description_channels.csv")
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
    ex = labs[labs.creator.isin(["@MeidasTouch", "@PTLRadioShow"])][["creator", "title_raw"] + cols].head(10).rename(columns=names)
    runs = [r for r in read_jsonl(RUNTIMES) if r["stage"] == "stage7_leaning" and r.get("backend") == "claude-code"]
    opus_run = runs[-1] if runs else {}
    gem = [c for c in cols if "gemma" in c]; gemma = gem[0] if gem else other[0]
    news = side_by_lane[side_by_lane.lane.isin(["wires & international", "US press", "US legacy TV"])]
    return f"""# 14. Political leaning from titles alone

**The question.** Can a channel's political leaning be read off its titles, and what does a model actually react to when it reads one? Three models of different families label each sampled title as left, right or neither; a channel's score is the balance of right over left labels. Everything here is *model-perceived* leaning: how a careful, reader-like model reads the wording of a title, with the disagreement between models as the uncertainty.

## The finding in one paragraph

A frontier model reads stance; the small local models mostly read subject. {jname} labels {pct(neither[judge])} of titles neither, {pct(ag['label_shares'][judge].get('left', 0))} left and {pct(ag['label_shares'][judge].get('right', 0))} right, and its channel score matches the channels' own words: of the {int(sd.n_self_declared.iloc[0])} channels whose YouTube description declares a leaning ("conservative political commentator", "populist left perspective"), it puts {pct(float(sd.loc[sd.score == judge + '_score', 'agreement_with_self_description'].iloc[0]))} on the declared side (the one miss is a tie). Against the lane proposal, a weaker yardstick because the lanes are themselves a model's assignment, it reaches an AUC of {vj.auc_right_vs_left_lane:.2f} and {pct(vj.accuracy_sign_vs_lane)} of the {int(vj.n_creators)} commentary channels. Gemma-3-12B gets most channels right but misreads hostile coverage as the target's side; Qwen3-14B calls three quarters of titles neither and leans right on the rest. The three agree on {pct(ag['all_models_agree_share'])} of titles, almost all of them "neither". The words behind the frontier model's labels are stance words: its *right* vocabulary is {', '.join(right_w.word.head(8))}; its *left* vocabulary is {', '.join(left_w.word.head(8))}, and "Trump PANICS" is left, as it should be, where the small models had it right.

![Scores by model and by lane.](figures/14_leaning_scores.png)
*Left: each channel's score from the two best models (−1 = every title read as left, +1 = every title read as right). Right: the judge-of-record score by lane, dots = channels.*

## What each model sees

Label shares over the {ag['n_labelled_by_all']:,} titles all three labelled:

{table(shares, fmt='{:.3f}')}

Agreement between models (Cohen's kappa; the last column restricts to titles both called partisan):

{table(pairs, fmt='{:.2f}')}

All three agree on {pct(ag['all_models_agree_share'])} of titles; of those, {pct(ag['consensus_label_shares'].get('neither', 0))} are neither. Channel scores: Spearman {', '.join(f'{rho[c]:.2f} with {names[c]}' for c in other)} against {jname}.

Ten MeidasTouch and PTL Radio titles with all three labels, the case that separated the judges:

{table(ex)}

## Channel scores against two yardsticks

**The channels' own descriptions** (lane-independent: {int(sd.n_self_declared.iloc[0])} channels with a leaning word in their YouTube description, {int(sd.n_right_declared.iloc[0])} right, {int(sd.n_left_declared.iloc[0])} left; rule and hand corrections in `leaning.py`):

{table(sd2, ['score', 'n_self_declared', 'agreement_with_self_description'], fmt='{:.3f}')}

Channels where the judge's sign differs from their self-description ({len(sd_dis)}):

{table(sd_dis, ['creator', 'lane', 'self_declared', 'judge_side_sign', 'judge_score'], fmt='{:.2f}') if len(sd_dis) else '_(none)_'}

**The lane proposal** (consistency check only: `left_commentary` vs `right_commentary`):

{table(val2, ['score', 'n_creators', 'auc_right_vs_left_lane', 'accuracy_sign_vs_lane', 'n_nonzero', 'mean_score_left_lane', 'mean_score_right_lane'], fmt='{:.3f}')}

The judge of record is the model with the highest lane AUC ({jname}); the mean and consensus scores are shown for transparency.

Where every channel lands under the judge of record (score above +0.05 = right, below −0.05 = left):

{table(side_by_lane, fmt='{:.0f}')}

Two things in that table deserve a look. The news lanes are mostly *neither*, as they should be, but their partisan-read titles tilt left ({int(news['left'].sum())} left vs {int(news['right'].sum())} right across the wires, the press and legacy TV): the judge reads a title hostile to the administration as left even in a news headline, so part of that tilt is the target-versus-stance ambiguity that no model fully escapes. And the interview podcasts lean right as a lane ({int(side_by_lane.loc[side_by_lane.lane == 'interview podcasts', 'right'].iloc[0])} right, {int(side_by_lane.loc[side_by_lane.lane == 'interview podcasts', 'left'].iloc[0])} left), which the lane proposal, built on format rather than politics, did not encode.

Lane means (all models; the 'neither' columns are the mean share of a channel's titles labelled neither):

{table(bl2, ['lane', 'n_creators'] + [f'{c}_score_mean' for c in cols] + [f'{c}_neither_mean' for c in cols], fmt='{:.2f}', rename=ren)}

The most left-reading and most right-reading channels under the judge of record:

{table(ext.head(12), ['creator', 'lane', 'n_titles', 'judge_score', 'judge_side'], fmt='{:.2f}')}

{table(ext.tail(12).iloc[::-1], ['creator', 'lane', 'n_titles', 'judge_score', 'judge_side'], fmt='{:.2f}')}

Commentary channels whose title-leaning contradicts their lane under the judge of record ({len(cj)} of {len(two)}):

{table(cj, ['creator', 'lane', 'value', 'implied_side', 'n_titles'], fmt='{:.2f}')}

These are not labelling accidents: Owen Shroyer's anti-war, anti-establishment titles read left; Tariq Nasheed's and Tim Black's read right on the titles that attack Democrats; Jimmy Dore's split evenly. They are the channels whose politics the left/right axis fits worst, and a reason to treat the lane proposal as provisional.

## What the frontier model calls right and what it calls left

Titles {jname} labelled right ({int(wj.n_right_titles.iloc[0])}) vs left ({int(wj.n_left_titles.iloc[0])}), scored by weighted log-odds (which words are over-used on one side) and rank-turbulence divergence (which words move most between the two frequency rankings).

![Words by side.](figures/14_leaning_words.png)
*Left: rank of each word among right-labelled titles against its rank among left-labelled titles (log axes); words far from the diagonal belong to one side. Right: the largest rank-turbulence-divergence contributions, signed by side.*

Right-labelled vocabulary (top 20):

{table(right_w, ['word', 'log_odds_right_vs_left', 'z', 'count_right', 'count_left', 'rtd_contribution'], fmt='{:.2f}')}

Left-labelled vocabulary (top 20):

{table(left_w, ['word', 'log_odds_right_vs_left', 'z', 'count_right', 'count_left', 'rtd_contribution'], fmt='{:.2f}')}

Read as a map of the two grammars of attack: the right's titles are about the left, the woke, women and trans issues, Islam, fraud, Newsom and Fauci; the left's are about Trump, MAGA, the war, Epstein, ICE and the DOJ, and they carry the outrage furniture (breaking, secret, panics, disaster). The same lists per model, and for the titles all three agree on (n = {int(wc.n_right_titles.iloc[0]) if len(wc) else 0} right, {int(wc.n_left_titles.iloc[0]) if len(wc) else 0} left):

{table(pd.DataFrame([{'model': names.get(c, c), 'right': ', '.join(per_model[c][0]), 'left': ', '.join(per_model[c][1])} for c in cols] + ([{'model': 'all three agree', 'right': ', '.join(wc.sort_values('z', ascending=False).head(12).word), 'left': ', '.join(wc.sort_values('z').head(12).word)}] if len(wc) else [])))}

The small models' lists are subject maps (MAGA, GOP and Trump-panic words on the "right", racism and Gaza on the "left"); the frontier model's list is closer to a stance map. That difference is the whole story of this document.

## Method

1. **Sample.** For each of the 274 creators, 16 unique edited-upload titles drawn at random (seed 20260914; creators with fewer than 16 uploads topped up from live VODs): {len(labs):,} titles.
2. **Labelling.** The same prompt for all three judges (`cache/leaning_prompt.txt`): label the viewpoint the title's own wording signals as left, right or neither, with three anchoring examples; temperature 0, batches of 20, every response cached. Qwen3-14B and Gemma-3-12B run locally through Ollama; {jname} runs through the Claude Code CLI in print mode on a Claude Max subscription ({opus_run.get('calls', '?')} calls, {opus_run.get('seconds', 0) / 60:.0f} minutes; the CLI reported an equivalent API cost of ${opus_run.get('reported_cost_usd', 0):.2f}, not charged).
3. **Scores.** Per channel and model: shares of left / right / neither and score = (right − left) / n; a consensus score on titles all models labelled the same way; the mean of the models. The judge of record is the model whose score best separates the two commentary lanes; a channel is called right above +0.05, left below −0.05.
4. **Yardsticks.** Self-description: a channel counts as self-declared right or left when its YouTube description contains leaning words (conservative, MAGA, libertarian, right-wing ... vs progressive, leftist, socialist, liberal ...), with nine hand corrections for phrases like "liberal democracy" or "former liberal"; agreement is the share of those channels whose score has the declared sign. Lanes: AUC and sign accuracy over the two commentary lanes only.
5. **Words.** Right vs left titles per model and for the all-agree set: weighted log-odds with an informative Dirichlet prior (alpha0 = 500; Monroe, Colaresi and Quinn 2008) and rank-turbulence divergence (alpha = 1/3; Dodds et al. 2020) on the vocabulary tokens of document 11.

## Limitations

- **This is perceived leaning.** A model reads a title the way an attentive reader would, and readers disagree; the three-way agreement figures are the honest width of that disagreement. No human panel was used, by choice: one reader cannot supply political ground truth, and a balanced panel is a study of its own. A blind 200-title sheet exists (`leaning_human_sheet.csv`) for anyone who wants a single-reader reliability check.
- **Ten words carry little stance.** Six in ten titles are neither even for the best judge, so a channel's score rests on a minority of its titles and, at 16 titles per channel, moves in steps of 1/16. Fifty titles per ranked channel is the natural next pass.
- **Target and stance still blur at the margin.** Hostile-to-Trump wording reads left even when it is a wire headline or an anti-establishment right channel; the news-lane tilt and the Owen Shroyer case are that residue.
- **The yardsticks are weak.** Self-descriptions cover 36 channels and say what a channel claims; the lane proposal is my own model-made assignment. Agreement with either is consistency, not accuracy.
- **The small models' failure is a model property, not a corpus property**; their word lists show what a 12-14B model uses as a partisan cue.

Files: `leaning_labels.csv`, `leaning_agreement.json`, `leaning_summary.json`, `leaning_by_creator.csv`, `leaning_lane_validation.csv`, `leaning_lane_contradictions.csv`, `leaning_by_lane.csv`, `leaning_self_description.csv`, `leaning_self_description_channels.csv`, `leaning_words.csv`.
"""
