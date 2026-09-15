# 8. Null results and caveats

Results that came out empty are results; and several numbers in this set should be read with their weaknesses in view.

## What did not show up

- **A Conversational dimension.** The LLM's conversational rating correlates with the factor closest to it (stream talk: chat, ellipsis, contractions) at only r = 0.18 at the creator level. The structural markers exist (document 3, F4) but they do not track what a reader calls conversational.
- **A Humour dimension, and a humour hook.** The rater flagged 11 of 3000 sampled titles as humorous; its test-retest kappa on the flag is 0.00; the classifier's held-out F1 is 0.00. Humour in titles is either genuinely rare in this landscape or invisible to a 14B model reading ten words. Nothing in the results should be cited as a measure of humour.
- **A curiosity-gap hook.** 62 positives of 3000 (2.1 %), classifier F1 0.18. The lexicon feature that approximates it (`curiosity_lex`: "here's why", "you won't believe", "this is insane") loads on the outrage pole of the tone factor, which suggests the device mostly *is* outrage in this corpus, but the hook as defined was not measured.
- **Style as a predictor of views** (beyond outrage). Twelve dimensions, length, curiosity: all median effects at or below 0.03 log views per SD with 50-70 % sign agreement across channels (document 7).
- **Power-law audiences.** 0 of 193 video channels (document 7).
- **Lane as a style predictor.** ARI 0.045 (document 5).
- **A landscape-wide drift.** Corpus-mean outrage share flat over the year (document 6).

## What to distrust, and how much

- **The rater.** All ratings and labels come from a local Qwen3-14B model at temperature 0. Weighted kappa on a 300-title retest: sensational 0.74, critical 0.58, analytical 0.56, conversational 0.66, educational 0.25; kappa on the outrage flag 0.50, on the format label 0.59. The validation of the tone factor stands on the reliable ratings; the rest is indicative. Re-rating with a stronger model is one cached command (`llm_rate --model ...`).
- **The lanes** are a proposal (document 1). Every lane-level table changes when they are corrected; the creator-level tables, neighbours and clusters do not.
- **The political flag** is broad (212 of 236 topics). The political-only landscape run reaches the same conclusions as the all-titles run, which limits how much this matters, but per-creator political shares should not be quoted without that caveat.
- **Entity counts** come from spaCy's small English model on truecased headline text; "Hormuz" as a person and fan-channel formulas as people show the noise. The top-25 lists are robust, the tail is not.
- **Views** are a fetch-time snapshot; Rumble has none; verbatim repeats are kept for view and concentration statistics and removed for everything else.
- **Group sizes.** Explainers/geopolitics has 3 ranked creators, right TV networks 4, humour 6; anything lane-level for those is a description of a handful of channels.
- **The corpus is one calendar window** dominated by one war. A landscape measured in a quieter year could show more topic separation between lanes and a smaller shared-title set.

## What would change the picture most

Correcting the lanes; re-rating the 3,000 titles with a more reliable model (or a human sample) to settle Educational and Conversational; and a second time window, so drift can be measured on more than nine points.
