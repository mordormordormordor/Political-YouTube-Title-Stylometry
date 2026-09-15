# 4. Formats and hooks

**The question.** Which structural formats do creators use (questions, LIVE labels, episode numbering, guests, reactions, confrontations, listicles, explainers), and which semantic hooks (curiosity gap, outrage frame, humour)?

## The finding in one paragraph

The outrage frame is the landscape's default hook, not a niche device. The rating model flagged 57 % of a 3,000-title creator-stratified sample as framing their subject as outrageous, scandalous or threatening, and a classifier trained on those labels reproduces the judgement well on held-out titles (accuracy 0.76, AUC 0.84, kappa 0.52). Applied to every title, it runs from three quarters of left-commentary and legal-commentary titles down to a quarter of US-press titles. The two other hooks could not be measured: the rater found a curiosity gap in 2.1 % of titles and humour in 0.4 %, far too few positives to learn from (held-out F1 0.18 and 0.00). Treat both as *unmeasured*, not absent (see document 8).

## Formats by lane (share of a creator's titles, mean over creators; edited uploads)

| lane | n_creators | question | breaking_live | episode_show | interview_guest | reaction | confrontation | listicle | howto_explainer |
|---|---|---|---|---|---|---|---|---|---|
| centrist / heterodox | 10.00 | 0.19 | 0.01 | 0.02 | 0.09 | 0.01 | 0.04 | 0.00 | 0.12 |
| explainers / geopolitics | 3.00 | 0.53 | 0.00 | 0.01 | 0.04 | 0.00 | 0.02 | 0.00 | 0.10 |
| humour / satire | 6.00 | 0.16 | 0.02 | 0.17 | 0.15 | 0.03 | 0.07 | 0.00 | 0.05 |
| independent digital news | 19.00 | 0.18 | 0.02 | 0.03 | 0.09 | 0.01 | 0.07 | 0.00 | 0.09 |
| interview podcasts | 19.00 | 0.19 | 0.01 | 0.11 | 0.18 | 0.01 | 0.09 | 0.00 | 0.12 |
| left commentary | 40.00 | 0.10 | 0.05 | 0.02 | 0.10 | 0.01 | 0.08 | 0.00 | 0.05 |
| legal commentary | 8.00 | 0.15 | 0.03 | 0.01 | 0.08 | 0.01 | 0.06 | 0.00 | 0.10 |
| right commentary | 69.00 | 0.15 | 0.01 | 0.08 | 0.08 | 0.03 | 0.08 | 0.00 | 0.09 |
| right TV networks | 4.00 | 0.06 | 0.18 | 0.26 | 0.10 | 0.02 | 0.07 | 0.00 | 0.05 |
| streamers | 23.00 | 0.09 | 0.00 | 0.05 | 0.08 | 0.10 | 0.14 | 0.00 | 0.04 |
| US legacy TV | 9.00 | 0.08 | 0.03 | 0.02 | 0.07 | 0.02 | 0.05 | 0.00 | 0.04 |
| US press | 18.00 | 0.26 | 0.01 | 0.02 | 0.09 | 0.01 | 0.04 | 0.00 | 0.15 |
| wires & international | 11.00 | 0.22 | 0.02 | 0.00 | 0.08 | 0.01 | 0.06 | 0.00 | 0.08 |


Questions are a press and explainer habit; episode numbering belongs to the talk shows (interview podcasts, humour) and to the right TV networks, whose stream titles are date-stamped replays; the reaction format is the streamers' own; confrontation wording ("vs", "destroys", "slams") is spread thinly across commentary and streamers and rare in news. Live VODs look different again, with LIVE/BREAKING labels on 71 % of wire streams and confrontation on 45 % of streamer streams (debates):

| lane | n_creators | question | breaking_live | episode_show | interview_guest | confrontation | outrage |
|---|---|---|---|---|---|---|---|
| centrist / heterodox | 2.00 | 0.08 | 0.23 | 0.00 | 0.41 | 0.04 | 0.40 |
| humour / satire | 1.00 | 0.06 | 0.00 | 0.31 | 0.79 | 0.02 | 0.42 |
| independent digital news | 6.00 | 0.09 | 0.31 | 0.01 | 0.10 | 0.07 | 0.63 |
| interview podcasts | 2.00 | 0.20 | 0.02 | 0.42 | 0.08 | 0.11 | 0.54 |
| left commentary | 18.00 | 0.10 | 0.13 | 0.04 | 0.21 | 0.12 | 0.77 |
| legal commentary | 3.00 | 0.21 | 0.07 | 0.25 | 0.11 | 0.09 | 0.64 |
| right commentary | 19.00 | 0.17 | 0.19 | 0.23 | 0.16 | 0.11 | 0.62 |
| right TV networks | 4.00 | 0.02 | 0.48 | 0.46 | 0.12 | 0.04 | 0.39 |
| streamers | 6.00 | 0.20 | 0.03 | 0.17 | 0.07 | 0.45 | 0.58 |
| US legacy TV | 7.00 | 0.04 | 0.39 | 0.00 | 0.11 | 0.04 | 0.12 |
| US press | 4.00 | 0.00 | 0.39 | 0.08 | 0.10 | 0.02 | 0.09 |
| wires & international | 7.00 | 0.05 | 0.71 | 0.00 | 0.09 | 0.08 | 0.36 |


## The outrage hook by lane (edited uploads)

| lane | n_creators | outrage | curiosity_gap | humor |
|---|---|---|---|---|
| left commentary | 40.00 | 0.76 | 0.03 | 0.00 |
| legal commentary | 8.00 | 0.76 | 0.02 | 0.00 |
| streamers | 23.00 | 0.65 | 0.04 | 0.00 |
| right commentary | 69.00 | 0.63 | 0.04 | 0.00 |
| independent digital news | 19.00 | 0.61 | 0.03 | 0.00 |
| centrist / heterodox | 10.00 | 0.54 | 0.04 | 0.00 |
| humour / satire | 6.00 | 0.45 | 0.02 | 0.00 |
| wires & international | 11.00 | 0.43 | 0.03 | 0.00 |
| right TV networks | 4.00 | 0.42 | 0.01 | 0.00 |
| interview podcasts | 19.00 | 0.41 | 0.01 | 0.00 |
| US legacy TV | 9.00 | 0.33 | 0.02 | 0.00 |
| US press | 18.00 | 0.28 | 0.02 | 0.00 |
| explainers / geopolitics | 3.00 | 0.26 | 0.04 | 0.00 |


The gradient is the same one the tone factor found in document 3, measured a second way: commentary lanes on the left and right, legal commentary and streamers above 60 %, the wires and the US press and TV below 45 %. The two measures are not independent (the classifier sees the same words the lexicon counts), but they were built from different sources: the tone factor from word lists and sentiment, the hook from a model reading whole titles.

## Examples (corpus-wide, three per category)

| category | creator | title |
|---|---|---|
| question | @ABCNews | How Sysco acquiring Restaurant Depot could shake up the food industry |
| question | @nytimes | How Americans Are Struggling With Rising Healthcare Costs |
| question | @SkyNews | Is Trump about to bring down NATO? \| Trump100 |
| breaking_live | @StatusCoup | BREAKING: LIVE ICE Protests as Lawsuit Filed to SHUT DOWN Delaney Hall ICE Prison |
| breaking_live | @TimesNowWorld | FRANCE WILDFIRE LIVE \| Mega-Fire 4x Size Of Paris Out Of Control Near Bordeaux \| TIMES NOW WORLD |
| breaking_live | @Firstpost | LIVE: 'US Aims For $1.5 Trillion Defence Budget,' Says Hegseth at NATO Defence Ministers' Meet |
| episode_show | @markets | Micron Earnings Spark Global Tech Rebound \| Daybreak Europe 6/25/2026 |
| episode_show | @TheDamageReport | The Damage Report: April 20, 2026 |
| episode_show | @ABCNews | Vance Warns Pope To "Be Careful" On Theology - What You Need To Know - April 15th, 2026 |
| interview_guest | @underthedesknews | FULL TOP STORY: Sen. Graham Conspired w/ Israel to DESTROY the International Criminal Court |
| interview_guest | @NBCNews | Father reunites with five daughters after months overseas |
| interview_guest | @timesofindia | ‘Taco Welcome’: Barred From US, Iran Football Boss Joins Emotional Mexico Crowd \| FIFA World Cup |
| reaction | @Firstpost | US-Iran War Ceasefire LIVE: Iranians and Americans Reacts to Trump's Ceasefire Announcement \| N18G |
| reaction | @wethefifth | Media Insiders React to the Scott Pelley 60 Minutes Drama - The Fifth Column |
| reaction | @msnow | 'This is about Trump': Elections expert reacts to Virginia redistricting measure passing |
| confrontation | @Firstpost | Red Fort Attack LIVE: Pakistan's Terror Lies Busted As JeM’s Hand Emerge in Lal Qila Blast |
| confrontation | @timesofindia | '5th Time You Blinked': Reporter Grills Trump On Iran U-Turn; Shock 'I Don't Know' Reply Follows |
| confrontation | @PTLRadioShow | MAGA Callers Accuse Brian Shapiro Of Lying… Then Get Fact-Checked |
| listicle | @Firstpost | US-Iran War Top 5 Developments: Tehran Claims Drone Attack Amid Hormuz Tensions \| Firstpost Live |
| listicle | @TheMajorityReport | 39 Times Trump Claimed An Iran Deal Was Imminent |
| listicle | @NewsNation | An MLB opening day preview, plus March Madness Sweet 16 predictions \| Morning in America |
| howto_explainer | @JackCocchiarellaShow | Fox Host Suffers Emotional Breakdown As Trump Loses Senate |
| howto_explainer | @AssociatedPress | AP reporter breaks down Supreme Court ruling striking down Trump’s tariffs |
| howto_explainer | @RealAmericasVoice | 9/11 Widow Terry Strada REVEALS What Happened After Her Husband’s FINAL Call |
| curiosity_gap | @LukeBeasley | Actually, what the f*** just happened?! |
| curiosity_gap | https://rumble.com/c/russellbrand | They don't want you knowing this... |
| curiosity_gap | @AsmonTV | Holy sh*t.. How is this real? |
| outrage | @timesofindia | ‘Humiliated’ Trump Fires EXPLOSIVE WARNING To Canada In Extreme Meltdown \| ‘NO MORE BENEFITS!’ |
| outrage | @LukeBeasley | SHOCK BREAKING: TRUMP S*X BOMBSHELL ERUPTS, PUBLIC MELTDOWN BACKFIRES! |
| outrage | @BlackConservativePerspective | Leftists PANIC As Wife EXPOSES Another HUMILIATING Scandal Against IMPLODING Communist Democrat! |
| humor | @TimcastIRL | THIS IS HILARIOUS |
| humor | @TimcastNews | THIS IS HILARIOUS |
| humor | @TheQuartering | THIS IS HILARIOUS |


## Do the rules agree with the model?

Formats are regexes on the raw title (the exact patterns are in `format_rules.csv`); the rater also gave each sampled title one format label. Where both apply:

| category | rule_positives | llm_positives | precision_rule_vs_llm | recall_rule_vs_llm | kappa |
|---|---|---|---|---|---|
| question | 424 | 58 | 0.10 | 0.74 | 0.15 |
| breaking_live | 251 | 268 | 0.81 | 0.76 | 0.77 |
| episode_show | 226 | 228 | 0.54 | 0.54 | 0.50 |
| interview_guest | 326 | 99 | 0.18 | 0.60 | 0.24 |
| reaction | 78 | 56 | 0.49 | 0.68 | 0.56 |
| confrontation | 239 | 98 | 0.20 | 0.50 | 0.26 |
| listicle | 3 | 4 | 0.67 | 0.50 | 0.57 |
| howto_explainer | 219 | 75 | 0.17 | 0.51 | 0.23 |


The rules fire far more often than the model's single label for interview_guest and howto_explainer (the rules count "with a name" and "why"; the model picks one dominant format per title), so the rule shares above are upper bounds for those two categories. Question, breaking/live and episode formats agree well.

Files: `formats.parquet` (per title), `format_hook_shares.csv`, `format_examples.csv`, `format_rules.csv`, `format_agreement.csv`, `hook_classifier.json`.
