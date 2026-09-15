"""Document 14: political leaning from titles, two models (rendered by report_sections.write_all)."""

from __future__ import annotations

import json

import numpy as np
import pandas as pd

from pipeline_titles.common import ANALYSIS_DIR as A
from pipeline_titles.report_sections import lane, pct, rd, table


def _mname(c: str) -> str:
    return c.replace("label_", "").replace("_score", "").replace("_", ":", 1).replace("_", ".")


def doc_leaning() -> str:
    ag = json.loads((A / "leaning_agreement.json").read_text()); summ = json.loads((A / "leaning_summary.json").read_text())
    bc = rd("leaning_by_creator.csv"); val = rd("leaning_lane_validation.csv"); con = rd("leaning_lane_contradictions.csv")
    bl = rd("leaning_by_lane.csv"); words = rd("leaning_words.csv"); labs = rd("leaning_labels.csv")
    cols = ag["models"]; names = {c: _mname(c) for c in cols}
    judge = summ["judge_of_record"]; jname = _mname(judge); other = [c for c in cols if c != judge][0]; oname = _mname(other)
    vj = val[val.score == judge + "_score"].iloc[0]; vo = val[val.score == other + "_score"].iloc[0]
    shares = pd.DataFrame(ag["label_shares"]).T.reset_index().rename(columns={"index": "model"}); shares["model"] = shares.model.map(names)
    conf = pd.DataFrame(ag["confusion"]).reset_index().rename(columns={"index": f"{names[cols[0]]} \\\\ {names[cols[1]]}"})
    side_by_lane = bc.groupby("lane").judge_side.value_counts().unstack(fill_value=0).reindex(columns=["left", "neither / unclear", "right"], fill_value=0).reset_index()
    side_by_lane["lane"] = side_by_lane.lane.map(lane)
    bl2 = bl.copy(); bl2["lane"] = bl2.lane.map(lane)
    ren = {f"{c}_score_mean": names[c] + " score" for c in cols} | {f"{c}_neither_mean": names[c] + " 'neither'" for c in cols}
    val2 = val.copy(); val2["score"] = val2.score.map(lambda s: names.get(s.replace("_score", ""), s))
    cj = con[con.score == judge + "_score"].copy(); cj["lane"] = cj.lane.map(lane)
    ext = bc.sort_values("judge_score"); ext["lane"] = ext.lane.map(lane)
    wcons = words[words.model == "consensus"]
    right_w = wcons.sort_values("z", ascending=False).head(20); left_w = wcons.sort_values("z").head(20)
    per_model = {c: (words[words.model == c].sort_values("z", ascending=False).head(12).word.tolist(), words[words.model == c].sort_values("z").head(12).word.tolist()) for c in cols}
    two = bc[bc.lane.isin(["left_commentary", "right_commentary"])]
    neither = {c: ag["label_shares"][c].get("neither", 0) for c in cols}
    rho = bc[cols[0] + "_score"].corr(bc[cols[1] + "_score"], method="spearman")
    ex = labs[labs.creator == "@MeidasTouch"][["title_raw", cols[0], cols[1]]].head(8).rename(columns={cols[0]: names[cols[0]], cols[1]: names[cols[1]]})
    return f"""# 14. Political leaning from titles alone

**The question.** Can a channel's political leaning be read off its titles? Two local models of different families label each sampled title as left, right or neither; a channel's score is the balance of right over left labels; the lane proposal is the yardstick; and the vocabulary behind each side's labels shows what the models are actually reacting to.

## The finding in one paragraph

One model can, the other largely cannot, and both read the subject rather than the stance. {jname} calls {pct(neither[judge])} of titles neither and its channel score separates the left-commentary and right-commentary lanes with an AUC of {vj.auc_right_vs_left_lane:.2f}, putting {pct(vj.accuracy_sign_vs_lane)} of the {int(vj.n_creators)} commentary channels on their lane's side; it is the judge of record below. {oname} calls {pct(neither[other])} of titles neither, leans right on the rest (it scores the *left*-commentary lane at {vo.mean_score_left_lane:+.2f} on average) and reaches an AUC of only {vo.auc_right_vs_left_lane:.2f}. Per title the two agree only moderately (kappa {ag['kappa']:.2f}; their channel scores correlate at Spearman {rho:.2f}). The instructive part is where the good judge fails: the channels it gets wrong are the ones whose every title attacks the other side in that side's own vocabulary. MeidasTouch ("Trump PANICS...", "MAGA Mike THROWN UNDER THE BUS") and Brian Shapiro's PTL Radio ("MAGA Caller CAN'T DEFEND...") read as *right* because MAGA, GOP and Trump-panic words are right-coded; Dave Smith's libertarian attacks on Bongino, Patel and Fauci read as *left*. The word lists confirm it: the models' "right" vocabulary is democrat, fraud, gop, maga, islam, liberal; their "left" vocabulary is black, racist, gaza, nazi, fascism, progressive. That is a map of who is being talked about, which tracks who is talking often enough to sort most channels, and fails exactly when it doesn't.

![Scores by model and by lane.](figures/14_leaning_scores.png)
*Left: each channel's score from the two models (−1 = every title read as left, +1 = every title read as right). Right: the judge-of-record score by lane, dots = channels.*

## How the two models label, and how much they agree

{table(shares, fmt='{:.3f}')}

Per-title confusion (rows {names[cols[0]]}, columns {names[cols[1]]}):

{table(conf, fmt='{:.0f}')}

Exact agreement {pct(ag['exact_agreement'])}; kappa {ag['kappa']:.2f} over the three labels, {ag.get('kappa_political_only', float('nan')):.2f} on the titles both call partisan. Of the titles {names[cols[0]]} calls right, {names[cols[1]]} calls {pct(ag['confusion'][cols[1]].get('left', 0) if False else conf.loc[conf.iloc[:, 0] == 'right', 'left'].iloc[0] / conf.loc[conf.iloc[:, 0] == 'right', ['left', 'neither', 'right']].sum(axis=1).iloc[0])} left: the smaller model treats a title *about* Trump as a right-leaning title.

Eight MeidasTouch titles with both labels, as an illustration of the target-versus-stance problem:

{table(ex)}

## Channel scores against the lanes

{table(val2, ['score', 'n_creators', 'auc_right_vs_left_lane', 'accuracy_sign_vs_lane', 'n_nonzero', 'mean_score_left_lane', 'mean_score_right_lane'], fmt='{:.3f}')}

The judge of record is the single model with the highest AUC ({jname}); the mean and consensus scores are shown for transparency but are pulled down by the weaker model.

Where every channel lands under the judge of record (score above +0.05 = right, below −0.05 = left):

{table(side_by_lane, fmt='{:.0f}')}

Lane means (both models; the 'neither' columns are the mean share of a channel's titles labelled neither):

{table(bl2, ['lane', 'n_creators'] + [f'{c}_score_mean' for c in cols] + [f'{c}_neither_mean' for c in cols], fmt='{:.2f}', rename=ren)}

The most left-reading and most right-reading channels under the judge of record:

{table(ext.head(12), ['creator', 'lane', 'n_titles', 'judge_score', 'judge_side'], fmt='{:.2f}')}

{table(ext.tail(12).iloc[::-1], ['creator', 'lane', 'n_titles', 'judge_score', 'judge_side'], fmt='{:.2f}')}

Commentary channels whose title-leaning contradicts their lane under the judge of record ({len(cj)} of {len(two)}):

{table(cj, ['creator', 'lane', 'value', 'implied_side', 'n_titles'], fmt='{:.2f}')}

Three kinds of channel are here: hostile coverage of the other side in its own vocabulary (MeidasTouch, PTL Radio, Tariq Nasheed read right); intra-right criticism (Dave Smith, Owen Shroyer, Xaviaer read left); and culture/gender channels whose titles the model reads as left when they mock women or streamers (Brittany Venti, Blaire White). None of these is a labelling accident; each is the method's definition showing through, and the first kind is also a lane question worth a look.

## What the models call right and what they call left

Titles both models labelled the same way ({int(wcons.n_right_titles.iloc[0])} right, {int(wcons.n_left_titles.iloc[0])} left), scored two ways: weighted log-odds (which words are over-used on one side relative to the other) and rank-turbulence divergence (which words move most in the frequency ranking between the two sides).

![Words by side.](figures/14_leaning_words.png)
*Left: rank of each word among right-labelled titles against its rank among left-labelled titles (log axes); words far from the diagonal belong to one side. Right: the largest rank-turbulence-divergence contributions, signed by side.*

Right-labelled vocabulary (weighted log-odds, top 20):

{table(right_w, ['word', 'log_odds_right_vs_left', 'z', 'count_right', 'count_left', 'rtd_contribution'], fmt='{:.2f}')}

Left-labelled vocabulary (top 20):

{table(left_w, ['word', 'log_odds_right_vs_left', 'z', 'count_right', 'count_left', 'rtd_contribution'], fmt='{:.2f}')}

Per model, the twelve most right-marked and left-marked words:

{table(pd.DataFrame([{'model': names[c], 'right': ', '.join(per_model[c][0]), 'left': ', '.join(per_model[c][1])} for c in cols]))}

## Method

1. **Sample.** For each of the 274 creators, 16 unique edited-upload titles drawn at random (seed 20260914; creators with fewer than 16 uploads topped up from live VODs): {len(labs):,} titles.
2. **Labelling.** Two local models via Ollama, temperature 0, batches of 20, one prompt (in `cache/leaning_prompt.txt`): label the viewpoint the title's own wording signals as left, right or neither, with three anchoring examples. Qwen3-14B (Alibaba) and Gemma-3-12B (Google) are different model families. Every response is cached.
3. **Scores.** Per channel and model: shares of left / right / neither and score = (right − left) / n; consensus score on titles both labelled the same way; mean of the two. The judge of record is the model whose score best separates the two commentary lanes (AUC); a channel is called right above +0.05, left below −0.05.
4. **Validation.** Against `left_commentary` and `right_commentary` only: AUC for right vs left lane and the accuracy of the score's sign (ties excluded), per score.
5. **Words.** Consensus right vs left titles (and per model): weighted log-odds with an informative Dirichlet prior (alpha0 = 500; Monroe, Colaresi and Quinn 2008) and rank-turbulence divergence (alpha = 1/3; Dodds et al. 2020) on the vocabulary tokens of document 11.

## Limitations

- **Ten words carry little stance.** Half to three quarters of titles are neither, so a channel's score rests on a minority of its titles; at 16 titles per channel the score moves in steps of 1/16 and small differences are noise. A 50-title pass for ranked channels, with a split-half reliability check, is the planned next step.
- **The models read the target, not the politics.** Vocabulary about MAGA, the GOP or Trump's troubles is right-coded; vocabulary about racism, Gaza or fascism is left-coded. That sorts most channels correctly because most channels talk about the other side, and misreads the ones that do so in the other side's own words.
- **Two instruction-tuned LLMs are not independent judges**; their moderate agreement bounds what either can be trusted for per title. The smaller model's right lean is a model property, not a corpus property.
- **The yardstick is the lane proposal**, itself hand-made; agreement with it is not accuracy against ground truth. A human-labelled sample of a few hundred titles would settle which judge to trust.
- **The word lists describe the models' cues**, not what left or right creators "really" say.

Files: `leaning_labels.csv`, `leaning_agreement.json`, `leaning_summary.json`, `leaning_by_creator.csv`, `leaning_lane_validation.csv`, `leaning_lane_contradictions.csv`, `leaning_by_lane.csv`, `leaning_words.csv`.
"""
