# 8. Null results and caveats

Results that came out empty are results; and several numbers in this set should be read with their weaknesses in view.

## What did not show up

- **A Conversational dimension.** The LLM's conversational rating correlates with the factor closest to it (stream talk: chat, ellipsis, contractions) at only r = 0.18 at the creator level. The structural markers exist (factor F4 of the style model, `factor_loadings.csv`) but they do not track what a reader calls conversational.
- **A Humour dimension, and a humour hook.** The rater flagged 11 of 3000 sampled titles as humorous; its test-retest kappa on the flag is 0.00; the classifier's held-out F1 is 0.00. Humour in titles is either genuinely rare in this landscape or invisible to a 14B model reading ten words. Nothing in the results should be cited as a measure of humour.
- **A curiosity-gap hook.** 62 positives of 3000 (2.1 %), classifier F1 0.18. The lexicon feature that approximates it (`curiosity_lex`: "here's why", "you won't believe", "this is insane") loads on the outrage pole of the tone factor, which suggests the device mostly *is* outrage in this corpus, but the hook as defined was not measured.
- **Style as a predictor of views** (beyond outrage and capitals). In the within-channel regression of log views on the twelve dimensions, the hooks and length (month and topic controls; `engagement_summary.csv`), every predictor other than the outrage frame has a median effect at or below 0.03 log views per SD and between 50 % and 70 % of channels on the median's side of zero. The capitals effect of document 7 is measured on the same titles without topic controls and is of the same small order.
- **Power-law audiences.** 0 of 193 video channels (document 7).
- **The channel groups as a style predictor.** ARI 0.036 (document 5): channels whose titles read left, neutral or right do not title in three styles.
- **A landscape-wide drift.** Corpus-mean outrage share flat over the year (document 6).

## What to distrust, and how much

- **The rater.** All ratings and labels behind the style model, the hooks and the formats come from a local Qwen3-14B model at temperature 0. Weighted kappa on a 300-title retest: sensational 0.74, critical 0.58, analytical 0.56, conversational 0.66, educational 0.25; kappa on the outrage flag 0.50, on the format label 0.59. The validation of the tone factor stands on the reliable ratings; the rest is indicative. Re-rating with a stronger model is one cached command (`llm_rate --model ...`).
- **The channel groups** come from a second model's reading of 50 sampled titles per channel (document 14). The score is reliable as a ranking (split-half Spearman 0.96), but the ±0.05 thresholds are a choice, 23 channels changed group between the first 16-title draw and the full sample, and a group says how a channel's titles *read*, not what it is. Every group-level table changes if the thresholds or the judge change; the creator-level tables, neighbours and clusters do not.
- **The political flag** is broad (212 of 236 topics). The political-only landscape run reaches the same conclusions as the all-titles run, which limits how much this matters, but per-creator political shares should not be quoted without that caveat.
- **Entity counts** come from spaCy's small English model on truecased headline text; "Hormuz" as a person and fan-channel formulas as people show the noise. The top-25 lists are robust, the tail is not.
- **Views** are a fetch-time snapshot; Rumble has none; verbatim repeats are kept for view and concentration statistics and removed for everything else; months are approximate listing dates.
- **Group sizes.** The neutral group has 42 channels and a handful of ranked stream channels; anything group-level on streams for it is a description of a few channels.
- **The corpus is one calendar window** dominated by one war. A landscape measured in a quieter year could show more topic separation between the groups and a smaller shared-title set.

## What would change the picture most

A human check of the leaning labels (the blind sheet is written: `leaning_human_sheet.csv`); re-rating the 3,000 titles with a more reliable model (or a human sample) to settle Educational and Conversational; and a second time window, so drift can be measured on more than nine points.
