"""Document 14: political leaning from titles, two models (rendered by report_sections.write_all)."""

from __future__ import annotations

import json

import numpy as np
import pandas as pd

from pipeline_titles.common import ANALYSIS_DIR as A
from pipeline_titles.report_sections import lane, pct, rd, table


def doc_leaning() -> str:
    ag = json.loads((A / "leaning_agreement.json").read_text()); bc = rd("leaning_by_creator.csv"); val = rd("leaning_lane_validation.csv")
    con = rd("leaning_lane_contradictions.csv"); bl = rd("leaning_by_lane.csv"); words = rd("leaning_words.csv"); labs = rd("leaning_labels.csv")
    cols = ag["models"]; names = {c: c.replace("label_", "").replace("_", ":", 1).replace("_", ".") for c in cols}
    shares = pd.DataFrame(ag["label_shares"]).T.reset_index().rename(columns={"index": "model"}); shares["model"] = shares.model.map(names)
    conf = pd.DataFrame(ag["confusion"]) if "confusion" in ag else None
    bl2 = bl.copy(); bl2["lane"] = bl2.lane.map(lane)
    ren = {f"{c}_score_mean": names[c] + " score" for c in cols} | {f"{c}_neither_mean": names[c] + " 'neither'" for c in cols}
    val2 = val.copy(); val2["score"] = val2.score.map(lambda s: names.get(s.replace("_score", ""), s))
    two = bc[bc.lane.isin(["left_commentary", "right_commentary"])]
    ext = bc.sort_values("mean_score"); ext["lane"] = ext.lane.map(lane)
    wcons = words[words.model == "consensus"] if (words.model == "consensus").any() else words[words.model == cols[0]]
    right_w = wcons.sort_values("z", ascending=False).head(20); left_w = wcons.sort_values("z").head(20)
    rtd_r = wcons.sort_values("rtd_contribution", ascending=False).head(15); rtd_l = wcons.sort_values("rtd_contribution").head(15)
    per_model = {c: (words[words.model == c].sort_values("z", ascending=False).head(12).word.tolist(), words[words.model == c].sort_values("z").head(12).word.tolist()) for c in cols}
    n_two = len(two); auc_mean = float(val.loc[val.score == "mean_score", "auc_right_vs_left_lane"].iloc[0]); acc_mean = float(val.loc[val.score == "mean_score", "accuracy_sign_vs_lane"].iloc[0])
    neither_share = {c: ag["label_shares"][c].get("neither", 0) for c in cols}
    con2 = con.copy(); con2["lane"] = con2.lane.map(lane) if len(con2) else con2.get("lane")
    return f"""# 14. Political leaning from titles alone

**The question.** Can a channel's political leaning be read off its titles? Two models of different families label each sampled title as left, right or neither; the channel's score is the balance of right over left labels; the lanes are the yardstick; and the words behind each side's labels show what the models are reacting to.

## The finding in one paragraph

Mostly yes at the channel level, mostly no at the title level. Both models call the majority of titles *neither* ({', '.join(f'{names[c]} {pct(neither_share[c])}' for c in cols)}): a ten-word title usually names a subject without betraying a stance. On the titles they do read as partisan the two models agree only moderately (Cohen's kappa {ag.get('kappa', float('nan')):.2f} over all three labels, exact agreement {pct(ag.get('exact_agreement', float('nan')))}). But averaged over {int(bc.n_titles.median())} titles per channel the noise cancels: the mean score separates the left-commentary and right-commentary lanes with an AUC of {auc_mean:.2f} and puts {pct(acc_mean)} of the {n_two} commentary channels on the side their lane says (the contradictions are listed below and are informative in themselves). The vocabulary the models treat as *right* is the anti-left culture-war lexicon ({', '.join(right_w.word.head(6))}); the vocabulary they treat as *left* is the anti-Trump / anti-administration lexicon ({', '.join(left_w.word.head(6))}). In other words the models read stance from the target of the attack, which is also how the lanes were drawn.

![Scores by model and by lane.](figures/14_leaning_scores.png)
*Left: each channel's score from the two models (−1 = every title read as left, +1 = every title read as right). Right: mean score by lane.*

## How the two models agree

{table(shares, fmt='{:.3f}')}

Per-title confusion (rows {names[cols[0]]}, columns {names[cols[1]]}):

{table(conf.reset_index().rename(columns={'index': names[cols[0]] + ' \\\\ ' + names[cols[1]]}), fmt='{:.0f}') if conf is not None else ''}

Kappa on the titles both models call partisan (left or right only): {ag.get('kappa_political_only', float('nan'))}.

## Channel scores against the lanes

{table(val2, ['score', 'n_creators', 'auc_right_vs_left_lane', 'accuracy_sign_vs_lane', 'n_nonzero', 'mean_score_left_lane', 'mean_score_right_lane'], fmt='{:.3f}')}

By lane (mean of channel scores; the 'neither' columns are the mean share of a channel's titles labelled neither):

{table(bl2, ['lane', 'n_creators', 'mean_score'] + [f'{c}_score_mean' for c in cols] + [f'{c}_neither_mean' for c in cols], fmt='{:.2f}', rename=ren)}

The most left-reading and most right-reading channels by mean score:

{table(ext.head(12), ['creator', 'lane', 'n_titles', 'mean_score', 'implied_side'], fmt='{:.2f}')}

{table(ext.tail(12).iloc[::-1], ['creator', 'lane', 'n_titles', 'mean_score', 'implied_side'], fmt='{:.2f}')}

Commentary channels whose title-leaning contradicts their lane ({len(con)}):

{table(con2, ['creator', 'lane', 'mean_score', 'implied_side', 'n_titles'], fmt='{:.2f}')}

Read these as diagnostics for the lane proposal as much as for the models: an anti-establishment left channel that spends its titles attacking Democrats reads as right; a never-Trump channel reads as left.

## What the models call right and what they call left

Titles both models labelled the same way, right vs left, scored two ways: weighted log-odds (which words are over-used on one side relative to the other) and rank-turbulence divergence (which words move most in the frequency ranking between the two sides).

![Words by side.](figures/14_leaning_words.png)
*Left: rank of each word among right-labelled titles against its rank among left-labelled titles (log axes); words far from the diagonal are one side's. Right: the largest rank-turbulence-divergence contributions, signed by side.*

Right-labelled vocabulary (weighted log-odds, top 20):

{table(right_w, ['word', 'log_odds_right_vs_left', 'z', 'count_right', 'count_left', 'rtd_contribution'], fmt='{:.2f}')}

Left-labelled vocabulary (top 20):

{table(left_w, ['word', 'log_odds_right_vs_left', 'z', 'count_right', 'count_left', 'rtd_contribution'], fmt='{:.2f}')}

Per model, the twelve most right-marked and left-marked words:

{table(pd.DataFrame([{'model': names[c], 'right': ', '.join(per_model[c][0]), 'left': ', '.join(per_model[c][1])} for c in cols]))}

## Method

1. **Sample.** For each of the 274 creators, 16 unique edited-upload titles (drawn at random with seed 20260914; creators with fewer than 16 uploads are topped up from their live VODs): {len(labs):,} titles.
2. **Labelling.** Two local models via Ollama, temperature 0, batches of 20, the same prompt (in `cache/leaning_prompt.txt`): label the viewpoint *the title's own wording* signals as left, right or neither, with three anchoring examples. {names[cols[0]]} and {names[cols[1]]} are different model families (Alibaba's Qwen3, Google's Gemma 3), so their errors are less correlated than two sizes of one family would be. Every response is cached.
3. **Scores.** Per channel and model: shares of left / right / neither and score = (right − left) / n. The consensus score uses only titles both models labelled the same way; the mean score averages the two models. A channel is called right if the mean score is above +0.05, left below −0.05, otherwise neither/unclear.
4. **Validation.** Against the lane proposal's `left_commentary` and `right_commentary` lanes only: AUC of the score for right vs left lane, and the accuracy of the score's sign (ties excluded).
5. **Words.** Titles labelled right vs left (consensus set, and per model): weighted log-odds with an informative Dirichlet prior (alpha0 = 500; Monroe, Colaresi and Quinn 2008) and rank-turbulence divergence (alpha = 1/3; Dodds et al. 2020) on the vocabulary tokens of document 11.

## Limitations

- **Ten words carry little stance.** Most titles are neither, so a channel's score rests on a minority of its titles; with 16 titles per channel the score moves in steps of 1/16 and small channels' scores are noisy.
- **The models read the target, not the politics.** Attacking Trump reads as left, attacking "the radical left" reads as right. A populist-left channel that attacks Democrats, or a never-Trump conservative, is misread by design; the contradictions table shows exactly those.
- **Two instruction-tuned LLMs are not independent judges**: both were trained on similar internet text and share conventions about which words signal which side. Their moderate agreement bounds how much either can be trusted per title.
- **The yardstick is the lane proposal**, itself hand-made from channel names and titles; agreement with it is not accuracy against ground truth.
- **The word lists describe the models' heuristics**, the words they associate with each label, not what left or right creators "really" say; the log-odds are computed over model-labelled titles, so a word the model over-reads as partisan looks partisan here.

Files: `leaning_labels.csv`, `leaning_agreement.json`, `leaning_by_creator.csv`, `leaning_lane_validation.csv`, `leaning_lane_contradictions.csv`, `leaning_by_lane.csv`, `leaning_words.csv`.
"""
