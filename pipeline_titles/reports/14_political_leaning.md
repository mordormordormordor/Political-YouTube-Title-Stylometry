# 14. Political leaning from titles alone

**The question.** Can a channel's political leaning be read off its titles? Two local models of different families label each sampled title as left, right or neither; a channel's score is the balance of right over left labels; the lane proposal is the yardstick; and the vocabulary behind each side's labels shows what the models are actually reacting to.

## The finding in one paragraph

One model can, the other largely cannot, and both read the subject rather than the stance. gemma3:12b calls 48 % of titles neither and its channel score separates the left-commentary and right-commentary lanes with an AUC of 0.93, putting 88 % of the 123 commentary channels on their lane's side; it is the judge of record below. qwen3:14b calls 73 % of titles neither, leans right on the rest (it scores the *left*-commentary lane at +0.14 on average) and reaches an AUC of only 0.57. Per title the two agree only moderately (kappa 0.38; their channel scores correlate at Spearman 0.28). The instructive part is where the good judge fails: the channels it gets wrong are the ones whose every title attacks the other side in that side's own vocabulary. MeidasTouch ("Trump PANICS...", "MAGA Mike THROWN UNDER THE BUS") and Brian Shapiro's PTL Radio ("MAGA Caller CAN'T DEFEND...") read as *right* because MAGA, GOP and Trump-panic words are right-coded; Dave Smith's libertarian attacks on Bongino, Patel and Fauci read as *left*. The word lists confirm it: the models' "right" vocabulary is democrat, fraud, gop, maga, islam, liberal; their "left" vocabulary is black, racist, gaza, nazi, fascism, progressive. That is a map of who is being talked about, which tracks who is talking often enough to sort most channels, and fails exactly when it doesn't.

![Scores by model and by lane.](figures/14_leaning_scores.png)
*Left: each channel's score from the two models (−1 = every title read as left, +1 = every title read as right). Right: the judge-of-record score by lane, dots = channels.*

## How the two models label, and how much they agree

| model | neither | right | left |
|---|---|---|---|
| qwen3:14b | 0.726 | 0.197 | 0.077 |
| gemma3:12b | 0.479 | 0.281 | 0.240 |


Per-title confusion (rows qwen3:14b, columns gemma3:12b):

| qwen3:14b \\ gemma3:12b | left | neither | right |
|---|---|---|---|
| left | 237 | 17 | 77 |
| neither | 499 | 2010 | 625 |
| right | 300 | 41 | 511 |


Exact agreement 64 %; kappa 0.38 over the three labels, 0.32 on the titles both call partisan. Of the titles qwen3:14b calls right, gemma3:12b calls 35 % left: the smaller model treats a title *about* Trump as a right-leaning title.

Eight MeidasTouch titles with both labels, as an illustration of the target-versus-stance problem:

| title_raw | qwen3:14b | gemma3:12b |
|---|---|---|
| Trump & Blanche INSTANTLY COUNTERED as Blanche Takes Over DOJ!!! | right | right |
| Trump WANTS Fox OFF THE AIR after REPORT HE FEARED!! | right | right |
| Obama BREAKS HIS SILENCE and RIPS Trump’s AWFUL DEAL!!! | left | left |
| Fox News FINALLY TURNS AGAINST Trump OVER WAR DISASTER!! | right | left |
| MTG Gets REVENGE on Trump and LEADS BOYCOTT!!! | neither | right |
| Iran GIVES FINAL WARNING to Trump on CEASEFIRE VIOLATIONS!!! | neither | neither |
| THIS Trump Move SHOWS US His PLAN… | neither | right |
| Trump gives CATASTROPHIC SPEECH on IRAN WAR…in KENTUCKY?!!! | right | right |


## Channel scores against the lanes

| score | n_creators | auc_right_vs_left_lane | accuracy_sign_vs_lane | n_nonzero | mean_score_left_lane | mean_score_right_lane |
|---|---|---|---|---|---|---|
| qwen3:14b | 123 | 0.572 | 0.661 | 109 | 0.139 | 0.187 |
| gemma3:12b | 123 | 0.927 | 0.882 | 119 | -0.254 | 0.373 |
| consensus_score | 122 | 0.812 | 0.832 | 101 | -0.030 | 0.304 |
| mean_score | 123 | 0.897 | 0.817 | 120 | -0.058 | 0.280 |


The judge of record is the single model with the highest AUC (gemma3:12b); the mean and consensus scores are shown for transparency but are pulled down by the weaker model.

Where every channel lands under the judge of record (score above +0.05 = right, below −0.05 = left):

| lane | left | neither / unclear | right |
|---|---|---|---|
| centrist / heterodox | 5 | 0 | 7 |
| explainers / geopolitics | 4 | 1 | 2 |
| humour / satire | 5 | 0 | 3 |
| independent digital news | 15 | 1 | 4 |
| interview podcasts | 7 | 1 | 15 |
| left commentary | 38 | 2 | 8 |
| legal commentary | 6 | 0 | 3 |
| right commentary | 6 | 2 | 67 |
| right TV networks | 0 | 0 | 4 |
| streamers | 14 | 6 | 6 |
| US legacy TV | 2 | 0 | 7 |
| US press | 9 | 2 | 8 |
| wires & international | 3 | 5 | 6 |


Lane means (both models; the 'neither' columns are the mean share of a channel's titles labelled neither):

| lane | n_creators | qwen3:14b score | gemma3:12b score | qwen3:14b 'neither' | gemma3:12b 'neither' |
|---|---|---|---|---|---|
| independent digital news | 20 | 0.04 | -0.18 | 0.70 | 0.47 |
| explainers / geopolitics | 7 | -0.01 | -0.12 | 0.99 | 0.79 |
| left commentary | 48 | 0.14 | -0.25 | 0.59 | 0.30 |
| humour / satire | 8 | 0.02 | -0.09 | 0.80 | 0.57 |
| streamers | 26 | 0.13 | -0.11 | 0.74 | 0.52 |
| legal commentary | 9 | 0.07 | -0.04 | 0.58 | 0.31 |
| US press | 19 | 0.07 | -0.03 | 0.89 | 0.71 |
| interview podcasts | 23 | 0.07 | 0.01 | 0.79 | 0.56 |
| centrist / heterodox | 12 | 0.13 | -0.05 | 0.73 | 0.49 |
| wires & international | 14 | 0.05 | 0.07 | 0.90 | 0.72 |
| US legacy TV | 9 | 0.10 | 0.13 | 0.80 | 0.63 |
| right commentary | 75 | 0.19 | 0.37 | 0.70 | 0.41 |
| right TV networks | 4 | 0.30 | 0.50 | 0.67 | 0.41 |


The most left-reading and most right-reading channels under the judge of record:

| creator | lane | n_titles | judge_score | judge_side |
|---|---|---|---|---|
| @TheDailyBeast | US press | 16 | -1.00 | left |
| @thewarningwithsteveschmidt | centrist / heterodox | 16 | -0.94 | left |
| @DemocracyDocket | legal commentary | 16 | -0.88 | left |
| @TheDonLemonShow | left commentary | 16 | -0.81 | left |
| @StatusCoup | independent digital news | 16 | -0.81 | left |
| @SecularTalk | left commentary | 16 | -0.81 | left |
| @katmabu | left commentary | 16 | -0.75 | left |
| @YaBoiHakim | left commentary | 16 | -0.75 | left |
| @BreakThroughNews | independent digital news | 16 | -0.75 | left |
| @TheJoyReidShow | left commentary | 16 | -0.69 | left |
| @revleftradio | interview podcasts | 16 | -0.69 | left |
| @BadFaithPodcast | interview podcasts | 16 | -0.69 | left |


| creator | lane | n_titles | judge_score | judge_side |
|---|---|---|---|---|
| @ActualJusticeWarrior | right commentary | 16 | 1.00 | right |
| @BlackConservativePerspective | right commentary | 16 | 0.88 | right |
| @BlazeTV | right commentary | 16 | 0.88 | right |
| @bennyjohnson | right commentary | 16 | 0.81 | right |
| @turningpointusa | right commentary | 16 | 0.81 | right |
| @TheOfficerTatum | right commentary | 16 | 0.81 | right |
| @CamHigby | right commentary | 16 | 0.81 | right |
| @NewsmaxTV | right TV networks | 16 | 0.81 | right |
| @X22Report-y5y | right commentary | 16 | 0.75 | right |
| @clayandbuck | right commentary | 16 | 0.75 | right |
| @DrSteveTurleyTV | right commentary | 16 | 0.75 | right |
| @VivaFrei | legal commentary | 16 | 0.75 | right |


Commentary channels whose title-leaning contradicts their lane under the judge of record (18 of 123):

| creator | lane | value | implied_side | n_titles |
|---|---|---|---|---|
| @BrittanyVenti | right commentary | -0.31 | left | 16 |
| @TheAmalaEkpunobi | right commentary | -0.06 | left | 16 |
| @PartOfTheProblem | right commentary | -0.31 | left | 16 |
| @PhillipScottPodcast | left commentary | 0.00 | tie | 16 |
| @SavSays | right commentary | 0.00 | tie | 16 |
| @ClipsCandaceOwens | right commentary | 0.00 | tie | 16 |
| @BlaireWhiteX | right commentary | -0.18 | left | 11 |
| @Tim_Black | left commentary | 0.12 | right | 16 |
| @TheRealTabithaSpeaks | left commentary | 0.12 | right | 16 |
| @OwenReport | right commentary | -0.06 | left | 16 |
| @thejimmydoreshow | left commentary | 0.06 | right | 16 |
| @ponderingpolitics | left commentary | 0.06 | right | 16 |
| @SabbySabs | left commentary | 0.12 | right | 16 |
| @XAVIAER | right commentary | -0.06 | left | 16 |
| @TheMichaelCohenShow | left commentary | 0.00 | tie | 16 |
| @MrTariqNasheed | left commentary | 0.38 | right | 16 |
| @MeidasTouch | left commentary | 0.44 | right | 16 |
| @PTLRadioShow | left commentary | 0.50 | right | 16 |


Three kinds of channel are here: hostile coverage of the other side in its own vocabulary (MeidasTouch, PTL Radio, Tariq Nasheed read right); intra-right criticism (Dave Smith, Owen Shroyer, Xaviaer read left); and culture/gender channels whose titles the model reads as left when they mock women or streamers (Brittany Venti, Blaire White). None of these is a labelling accident; each is the method's definition showing through, and the first kind is also a lane question worth a look.

## What the models call right and what they call left

Titles both models labelled the same way (511 right, 237 left), scored two ways: weighted log-odds (which words are over-used on one side relative to the other) and rank-turbulence divergence (which words move most in the frequency ranking between the two sides).

![Words by side.](figures/14_leaning_words.png)
*Left: rank of each word among right-labelled titles against its rank among left-labelled titles (log axes); words far from the diagonal belong to one side. Right: the largest rank-turbulence-divergence contributions, signed by side.*

Right-labelled vocabulary (weighted log-odds, top 20):

| word | log_odds_right_vs_left | z | count_right | count_left | rtd_contribution |
|---|---|---|---|---|---|
| democrat | 1.79 | 2.05 | 15 | 0 | 0.00 |
| fraud | 1.79 | 1.98 | 14 | 0 | 0.00 |
| gop | 1.79 | 1.75 | 11 | 0 | 0.00 |
| nick | 1.79 | 1.67 | 10 | 0 | 0.00 |
| candace | 1.79 | 1.67 | 10 | 0 | 0.00 |
| islam | 1.79 | 1.59 | 9 | 0 | 0.00 |
| owens | 1.79 | 1.59 | 9 | 0 | 0.00 |
| california | 1.08 | 1.46 | 11 | 1 | 0.00 |
| report | 1.79 | 1.40 | 7 | 0 | 0.00 |
| liberal | 1.79 | 1.40 | 7 | 0 | 0.00 |
| hegseth | 1.79 | 1.29 | 6 | 0 | 0.00 |
| alex | 1.79 | 1.29 | 6 | 0 | 0.00 |
| republican | 1.79 | 1.29 | 6 | 0 | 0.00 |
| attacks | 1.79 | 1.29 | 6 | 0 | 0.00 |
| maga | 0.43 | 1.28 | 31 | 8 | 0.00 |
| america | 0.48 | 1.26 | 25 | 6 | 0.00 |
| goes | 0.97 | 1.24 | 9 | 1 | 0.00 |
| fbi | 0.97 | 1.24 | 9 | 1 | 0.00 |
| finished | 1.79 | 1.18 | 5 | 0 | 0.00 |
| ds | 1.79 | 1.18 | 5 | 0 | 0.00 |


Left-labelled vocabulary (top 20):

| word | log_odds_right_vs_left | z | count_right | count_left | rtd_contribution |
|---|---|---|---|---|---|
| black | -1.24 | -2.75 | 6 | 12 | -0.00 |
| war | -0.70 | -2.67 | 24 | 25 | -0.00 |
| trump | -0.30 | -2.28 | 125 | 80 | -0.00 |
| gaza | -3.10 | -2.05 | 0 | 5 | -0.00 |
| racist | -3.10 | -2.05 | 0 | 5 | -0.00 |
| left | -0.85 | -1.96 | 8 | 10 | -0.00 |
| lies | -1.24 | -1.94 | 3 | 6 | -0.00 |
| donald | -1.24 | -1.94 | 3 | 6 | -0.00 |
| hasan | -1.41 | -1.90 | 2 | 5 | -0.00 |
| progressive | -1.41 | -1.90 | 2 | 5 | -0.00 |
| money | -1.77 | -1.86 | 1 | 4 | -0.00 |
| worse | -1.77 | -1.86 | 1 | 4 | -0.00 |
| nazi | -1.77 | -1.86 | 1 | 4 | -0.00 |
| israel | -0.66 | -1.69 | 11 | 11 | -0.00 |
| bombshell | -1.09 | -1.64 | 3 | 5 | -0.00 |
| fascism | -3.10 | -1.59 | 0 | 3 | -0.00 |
| fellow | -3.10 | -1.59 | 0 | 3 | -0.00 |
| resistance | -3.10 | -1.59 | 0 | 3 | -0.00 |
| detention | -3.10 | -1.59 | 0 | 3 | -0.00 |
| hasanabi | -3.10 | -1.59 | 0 | 3 | -0.00 |


Per model, the twelve most right-marked and left-marked words:

| model | right | left |
|---|---|---|
| qwen3:14b | gop, democrat, trump, maga, fox, nick, islam, candace, report, putin, owens, attacks | black, left, lies, money, gaza, worse, hasan, biden, progressive, piker, aoc, breaking |
| gemma3:12b | charlie, kirk, nick, fraud, candace, owens, democrat, fbi, america, myron, california, hegseth | trump, war, ice, hasanabi, hasan, breaking, racist, donald, gaza, democratic, israel, dsa |


## Method

1. **Sample.** For each of the 274 creators, 16 unique edited-upload titles drawn at random (seed 20260914; creators with fewer than 16 uploads topped up from live VODs): 4,352 titles.
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
