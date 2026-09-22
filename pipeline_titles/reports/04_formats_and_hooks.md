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
| right channels | 94.00 | 0.15 | 0.02 | 0.07 | 0.08 | 0.02 | 0.08 | 0.00 | 0.09 |


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
| right channels | 94 | 0.58 | 0.50 | 0.75 | 0.09 | 0.99 |


Within every group the creator-to-creator spread is wide (the quartiles above): the group is a weak predictor of any one channel. The gradient across groups is the same one the tone factor of the style model finds, measured a second way; the two measures are not independent (the classifier sees the same words the lexicon counts), but they were built from different sources, the tone factor from word lists and sentiment, the hook from a model reading whole titles.

## Examples (corpus-wide, three per category)

| category | creator | title |
|---|---|---|
| question | @CNN | Can Dems take the Senate even without Maine? |
| question | @FoxNewsChannelClips | Will Cain: Where will Gov. Walz go next with his analogies? |
| question | @bulwarkmedia | The Next Level LIVE: Texas Primary Results! Megyn Kelly Turns on Trump?! |
| breaking_live | @RealAmericasVoice | TRUMP'S IRAN DEAL BOMBSHELL, FED HOLDS RATES, SPLC NAZI SCANDAL EXPLODES \| LIVE FROM STUDIO 6B |
| breaking_live | @ANINewsIndia | WATCH: Sonam Wangchuk breaks 26-day fast amid CJP protest at Jantar Mantar against NEET Paper leak |
| breaking_live | @Firstpost | 🔴FIFA WORLD CUP LIVE \| Mexico Football Fans Hit Fever Pitch \| Mexico vs South Africa |
| episode_show | @RealDanBongino | They're Finding Out (Ep. 2549) |
| episode_show | @glennbeck | Remembering Charlie Kirk: Where Are We Now? \| Hour 1 \| 9/10/26 |
| episode_show | @RSBN | FULL EVENT: President Trump Creates U.S. Space Academy & Awards Space Medal of Honor - 08/28/26 |
| interview_guest | @ABCNews | The Obama Legacy: First Joint Interview Post-White House |
| interview_guest | @bulwarkmedia | Trump Promised Trillions in Cuts—And Delivered Nothing (w/ Jessica Riedl) \| Mona Charen Show |
| interview_guest | @timesofindia | 'ENOUGH IS ENOUGH': Tucker Carlson Joins Growing Revolt As Trump's Iran Gamble Backfires Inside MAGA |
| reaction | @DestinyDGGClips | Atrioc Responds After Getting Into MASSIVE Controversy |
| reaction | @SkyNews | Democrats react to Trump's citizenship defeat outside Supreme Court |
| reaction | @oann | WV Governor Praises National Guard Officers for Heroic Response to DC Attack |
| confrontation | @ANINewsIndia | ‘We'll destroy it as we get it’, Trump warns Iran after Khamenei’s 'defiance' over enriched Uranium |
| confrontation | @RealAmericasVoice | FAUCI TAKES THE FIFTH IN EXPLOSIVE SENATE HEARING, BERENSON DESTROYS COVID LIES \| CHARLIE KIRK SHOW |
| confrontation | @markets | US-Iran Clashes Hit Stocks as Oil Rises \| Bloomberg Brief 09/02/2026 |
| listicle | @RealAmericasVoice | FAUCI’S COVID CHAOS STEALS 2020, RNC CHAIR GRUTERS ON GOP FAITH \| AMERICA'S TOP 10 |
| listicle | @CNN | 4 ways Ukraine changed America’s wars forever |
| listicle | @nypost | Karoline Leavitt to Depart as White House Press Secretary — Top 5 Moments She Shut Down Reporters |
| howto_explainer | @SkyNews | Why Trump is fighting for the Arctic but losing in Antarctica |
| howto_explainer | @PhillipScottPodcast | Latina Explains Why They Didn't Vote For Jasmine Crockett Even Though She Was Pro-Immigration |
| howto_explainer | @oann | Why Rising Prices Could Trigger a Voter Backlash Before the Midterms |
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
