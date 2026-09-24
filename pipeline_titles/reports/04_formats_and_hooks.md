# 4. Formats and hooks

**The question.** Which structural formats do creators use (questions, LIVE labels, episode numbering, guests, reactions, confrontations, listicles, explainers), and which semantic hooks (curiosity gap, outrage frame, humor)?

## The finding in one paragraph

The outrage frame is the landscape's default hook, not a niche device. The rating model flagged 57 % of a 3,000-title creator-stratified sample as framing their subject as outrageous, scandalous or threatening, and a classifier trained on those labels reproduces the judgment well on held-out titles (accuracy 0.78, AUC 0.85, kappa 0.55). Applied to every title, it covers 64 % of the average left channel's edited uploads, 60 % of the average right channel's and 37 % of the average neutral channel's: the frame belongs to partisan titling on both sides, and the neutral group, which is mostly news outlets, uses it least. The two other hooks could not be measured: the rater found a curiosity gap in 2.1 % of titles and humor in 0.4 %, far too few positives to learn from (held-out F1 0.14 and 0.67). Treat both as *unmeasured*, not absent (see document 8).

## Formats by channel group (share of a creator's titles, mean over creators; edited uploads)

![Structural formats by channel group, edited uploads.](figures/04_formats_heatmap.png)
*Structural formats by channel group, edited uploads.*

| group | n_creators | question | breaking_live | episode_show | interview_guest | reaction | confrontation | listicle | howto_explainer |
|---|---|---|---|---|---|---|---|---|---|
| left channels | 105.00 | 0.16 | 0.03 | 0.03 | 0.10 | 0.03 | 0.08 | 0.00 | 0.08 |
| neutral channels | 37.00 | 0.14 | 0.01 | 0.07 | 0.12 | 0.02 | 0.08 | 0.00 | 0.07 |
| right channels | 95.00 | 0.15 | 0.02 | 0.07 | 0.08 | 0.02 | 0.08 | 0.00 | 0.09 |


Questions run at the same rate in all three groups; episode numbering and how-to / explainer wording are a little more common on the right, guest formats a little more in the neutral and left groups (12 %, 10 %, 8 % on the right), and none of the structural formats separates the groups the way the outrage hook does. Live VODs look different again: LIVE/BREAKING labels sit on 52 % of the neutral group's stream titles (the wires' rolling broadcasts), confrontation on 15 % of the left group's (the debate streamers):

| group | n_creators | question | breaking_live | episode_show | interview_guest | confrontation | outrage |
|---|---|---|---|---|---|---|---|
| left channels | 33.00 | 0.11 | 0.17 | 0.06 | 0.18 | 0.15 | 0.63 |
| neutral channels | 16.00 | 0.05 | 0.52 | 0.02 | 0.14 | 0.08 | 0.29 |
| right channels | 28.00 | 0.13 | 0.16 | 0.26 | 0.14 | 0.09 | 0.56 |


## The outrage hook by channel group (edited uploads)

![Outrage-frame share by channel group, edited uploads (left) and live VODs (right).](figures/04_outrage_by_group.png)
*Outrage-frame share by channel group, edited uploads (left) and live VODs (right); dots are creators, the bar is the group median.*

| group | n_creators | median | q25 | q75 | min | max |
|---|---|---|---|---|---|---|
| left channels | 105 | 0.67 | 0.46 | 0.84 | 0.06 | 1.00 |
| neutral channels | 37 | 0.31 | 0.22 | 0.47 | 0.05 | 0.88 |
| right channels | 95 | 0.59 | 0.50 | 0.76 | 0.09 | 0.99 |


Within every group the creator-to-creator spread is wide (the quartiles above): the group is a weak predictor of any one channel. The gradient across groups is the same one the tone factor of the style model finds, measured a second way; the two measures are not independent (the classifier sees the same words the lexicon counts), but they were built from different sources, the tone factor from word lists and sentiment, the hook from a model reading whole titles.

## Examples (corpus-wide, three per category)

| category | creator | title |
|---|---|---|
| question | @timesofindia | Trump's Greenland Threat Backfires? EU Boss VDL Warns 'Tariffs A Mistake', Signals De-dollarisation |
| question | @judgingfreedom | Aaron Maté  :  Will Trump Sacrifice the Gulf States? |
| question | @theisabelbrown | Is Evie’s New Magazine A S*x “Issue?” I’m Here For It, TBH |
| breaking_live | @RealAmericasVoice | TRUMP'S IRAN DEAL BOMBSHELL, FED HOLDS RATES, SPLC NAZI SCANDAL EXPLODES \| LIVE FROM STUDIO 6B |
| breaking_live | @ANINewsIndia | WATCH: Sonam Wangchuk breaks 26-day fast amid CJP protest at Jantar Mantar against NEET Paper leak |
| breaking_live | @Firstpost | 🔴FIFA WORLD CUP LIVE \| Mexico Football Fans Hit Fever Pitch \| Mexico vs South Africa |
| episode_show | @RealDanBongino | They're Finding Out (Ep. 2549) |
| episode_show | @glennbeck | Remembering Charlie Kirk: Where Are We Now? \| Hour 1 \| 9/10/26 |
| episode_show | @RSBN | FULL EVENT: President Trump Creates U.S. Space Academy & Awards Space Medal of Honor - 08/28/26 |
| interview_guest | @deanwithrs | Cocky MAGA Man HUMILIATES Himself With His "Solution" To Poverty |
| interview_guest | @LegalAFMTN | Trump HIT with FIRST LAWSUIT to STOP SLUSH FUND!!! |
| interview_guest | @judgingfreedom | Poland's Secret Deal With Ukraine Has Washington Concerned |
| reaction | @TimesNowWorld | EXPLAINED: Olympic Village Condom Shortage Goes Viral As IOC Responds At Milan Cortina |
| reaction | @nypost | Trump Reacts to 'CATASTROPHE' in Spanish Enclave as Thousands of Illegal Migrants Enter Border |
| reaction | @RubinReport | Trump's Unexpected Ted Turner Reaction, Obama Faces Backlash, Massive LA Raid \| 5/7/26 FIRST LOOK |
| confrontation | @ANINewsIndia | IND vs PAK T20 World Cup: Wishes and good luck pour in from across India ahead of ultimate showdown |
| confrontation | @MyronGainesX | Senator BREAKS Marine’s Arm After He CALLS OUT Israel Over Iran War! |
| confrontation | @JackCocchiarellaShow | SCREAMING Hearing Shuts Down As Bessent CAUGHT In Crime |
| listicle | @ANINewsIndia | Gujarat's CSMCRI: 26 Scientists in Bhavnagar Ranked Among World's Top 5% Researchers |
| listicle | @thehill | Trump’s Lincoln Memorial Reflecting Pool work comes under scrutiny: 4 things to know |
| listicle | @Forbes | America’s Top 25 Philanthropists — And Why Musk, Page And Ellison Aren’t On The List |
| howto_explainer | @CBSNews | Why Tom Homan says ICE operation in Minnesota is ending |
| howto_explainer | @lovettorleaveitpodcast | John Stamos Ponders How To Turn Republicans Against Trump |
| howto_explainer | @wsj | Why Hyundai Is Betting $26B Going All-In on the U.S. \| WSJ |
| curiosity_gap | https://rumble.com/c/russellbrand | They don't want you knowing this... |
| curiosity_gap | @CoreyGilShusterAskProject | Palestinians: What happens at the endtimes? |
| curiosity_gap | @LukeBeasley | Actually, what the f*** just happened?! |
| outrage | @LukeBeasley | SHOCK BREAKING: TRUMP S*X BOMBSHELL ERUPTS, PUBLIC MELTDOWN BACKFIRES! |
| outrage | @timesofindia | ‘Humiliated’ Trump Fires EXPLOSIVE WARNING To Canada In Extreme Meltdown \| ‘NO MORE BENEFITS!’ |
| outrage | @BlackConservativePerspective | Leftists PANIC As Wife EXPOSES Another HUMILIATING Scandal Against IMPLODING Communist Democrat! |
| humor | @TimcastIRL | THIS IS HILARIOUS |
| humor | @TimcastNews | THIS IS HILARIOUS |
| humor | @TheQuartering | THIS IS HILARIOUS |


## Do the rules agree with the model?

Formats are regexes on the raw title (the exact patterns are in `format_rules.csv`); the rater also gave each sampled title one format label. Where both apply:

| category | rule_positives | llm_positives | precision_rule_vs_llm | recall_rule_vs_llm | kappa |
|---|---|---|---|---|---|
| question | 407 | 54 | 0.10 | 0.78 | 0.15 |
| breaking_live | 233 | 251 | 0.81 | 0.76 | 0.77 |
| episode_show | 213 | 211 | 0.53 | 0.53 | 0.49 |
| interview_guest | 306 | 93 | 0.18 | 0.59 | 0.24 |
| reaction | 74 | 53 | 0.47 | 0.66 | 0.54 |
| confrontation | 231 | 93 | 0.21 | 0.52 | 0.26 |
| listicle | 2 | 4 | 1.00 | 0.50 | 0.67 |
| howto_explainer | 207 | 71 | 0.17 | 0.49 | 0.22 |


The rules fire far more often than the model's single label for interview_guest and howto_explainer (the rules count "with a name" and "why"; the model picks one dominant format per title), so the rule shares above are upper bounds for those two categories. Question, breaking/live and episode formats agree well.

Channel groups are the left / neutral / right groups of document 14: each channel's score = (right − left) / titles over its sampled titles as labeled by the judge, sorted at ±0.05. A channel's group says how its *titles* read, not what its host believes.

Files: `formats.parquet` (per title), `format_hook_shares.csv`, `format_examples.csv`, `format_rules.csv`, `format_agreement.csv`, `hook_classifier.json`.
