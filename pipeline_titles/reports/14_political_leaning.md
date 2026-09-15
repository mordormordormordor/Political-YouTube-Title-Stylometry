# 14. Political leaning from titles alone

**The question.** Can a channel's political leaning be read off its titles, and what does a model actually react to when it reads one? Three models of different families label each sampled title as left, right or neither; a channel's score is the balance of right over left labels. Everything here is *model-perceived* leaning: how a careful, reader-like model reads the wording of a title, with the disagreement between models as the uncertainty.

## The finding in one paragraph

A frontier model reads stance; the small local models mostly read subject. Claude Opus labels 59 % of titles neither, 23 % left and 18 % right, and its channel score matches the channels' own words: of the 36 channels whose YouTube description declares a leaning ("conservative political commentator", "populist left perspective"), it puts 97 % on the declared side (the one miss is a tie). Against the lane proposal, a weaker yardstick because the lanes are themselves a model's assignment, it reaches an AUC of 0.99 and 97 % of the 123 commentary channels. Gemma-3-12B gets most channels right but misreads hostile coverage as the target's side; Qwen3-14B calls three quarters of titles neither and leans right on the rest. The three agree on 52 % of titles, almost all of them "neither". The words behind the frontier model's labels are stance words: its *right* vocabulary is women, woke, fraud, california, left, democrat, kirk, trans; its *left* vocabulary is trump, maga, iran, israel, war, epstein, breaking, donald, and "Trump PANICS" is left, as it should be, where the small models had it right.

![Scores by model and by lane.](figures/14_leaning_scores.png)
*Left: each channel's score from the two best models (−1 = every title read as left, +1 = every title read as right). Right: the judge-of-record score by lane, dots = channels.*

## What each model sees

Label shares over the 4,317 titles all three labelled:

| model | left | neither | right |
|---|---|---|---|
| qwen3:14b | 0.077 | 0.726 | 0.197 |
| gemma3:12b | 0.240 | 0.479 | 0.281 |
| Claude Opus | 0.233 | 0.588 | 0.179 |


Agreement between models (Cohen's kappa; the last column restricts to titles both called partisan):

| models | kappa (3 labels) | exact agreement | kappa (partisan titles only) |
|---|---|---|---|
| qwen3:14b vs gemma3:12b | 0.38 | 0.64 | 0.32 |
| qwen3:14b vs Claude Opus | 0.33 | 0.65 | 0.13 |
| gemma3:12b vs Claude Opus | 0.51 | 0.70 | 0.59 |


All three agree on 52 % of titles; of those, 80 % are neither. Channel scores: Spearman 0.13 with qwen3:14b, 0.78 with gemma3:12b against Claude Opus.

Ten MeidasTouch and PTL Radio titles with all three labels, the case that separated the judges:

| creator | title_raw | qwen3:14b | gemma3:12b | Claude Opus |
|---|---|---|---|---|
| @MeidasTouch | Trump & Blanche INSTANTLY COUNTERED as Blanche Takes Over DOJ!!! | right | right | left |
| @MeidasTouch | Trump WANTS Fox OFF THE AIR after REPORT HE FEARED!! | right | right | left |
| @MeidasTouch | Obama BREAKS HIS SILENCE and RIPS Trump’s AWFUL DEAL!!! | left | left | left |
| @MeidasTouch | Fox News FINALLY TURNS AGAINST Trump OVER WAR DISASTER!! | right | left | left |
| @MeidasTouch | MTG Gets REVENGE on Trump and LEADS BOYCOTT!!! | neither | right | left |
| @MeidasTouch | Iran GIVES FINAL WARNING to Trump on CEASEFIRE VIOLATIONS!!! | neither | neither | left |
| @MeidasTouch | THIS Trump Move SHOWS US His PLAN… | neither | right | neither |
| @MeidasTouch | Trump gives CATASTROPHIC SPEECH on IRAN WAR…in KENTUCKY?!!! | right | right | left |
| @MeidasTouch | 🚨SECRET Epstein INTERVIEWS SURFACE on Trump…IT’S BAD!! | neither | right | left |
| @MeidasTouch | 🚨Ivana HAUNTS Trump FROM GRAVE with EPSTEIN FILES!!! | neither | right | left |


## Channel scores against two yardsticks

**The channels' own descriptions** (lane-independent: 36 channels with a leaning word in their YouTube description, 19 right, 17 left; rule and hand corrections in `leaning.py`):

| score | n_self_declared | agreement_with_self_description |
|---|---|---|
| qwen3:14b | 36 | 0.500 |
| gemma3:12b | 36 | 0.861 |
| Claude Opus | 36 | 0.972 |
| mean_score | 36 | 0.917 |
| judge_score | 36 | 0.972 |


Channels where the judge's sign differs from their self-description (1):

| creator | lane | self_declared | judge_side_sign | judge_score |
|---|---|---|---|---|
| @thejimmydoreshow | left commentary | left | tie | 0.00 |


**The lane proposal** (consistency check only: `left_commentary` vs `right_commentary`):

| score | n_creators | auc_right_vs_left_lane | accuracy_sign_vs_lane | n_nonzero | mean_score_left_lane | mean_score_right_lane |
|---|---|---|---|---|---|---|
| qwen3:14b | 123 | 0.572 | 0.661 | 109 | 0.139 | 0.187 |
| gemma3:12b | 123 | 0.927 | 0.882 | 119 | -0.254 | 0.373 |
| Claude Opus | 123 | 0.991 | 0.967 | 122 | -0.556 | 0.434 |
| consensus_score | 122 | 0.957 | 0.969 | 97 | -0.296 | 0.331 |
| mean_score | 123 | 0.988 | 0.942 | 121 | -0.224 | 0.332 |


The judge of record is the model with the highest lane AUC (Claude Opus); the mean and consensus scores are shown for transparency.

Where every channel lands under the judge of record (score above +0.05 = right, below −0.05 = left):

| lane | left | neither / unclear | right |
|---|---|---|---|
| centrist / heterodox | 7 | 1 | 4 |
| explainers / geopolitics | 2 | 4 | 1 |
| humour / satire | 4 | 2 | 2 |
| independent digital news | 17 | 1 | 2 |
| interview podcasts | 7 | 2 | 14 |
| left commentary | 44 | 1 | 3 |
| legal commentary | 6 | 0 | 3 |
| right commentary | 1 | 0 | 74 |
| right TV networks | 0 | 0 | 4 |
| streamers | 19 | 3 | 4 |
| US legacy TV | 3 | 4 | 2 |
| US press | 7 | 10 | 2 |
| wires & international | 8 | 6 | 0 |


![Every channel's breakdown.](figures/14_leaning_channels.png)
*Every channel: the share of its sampled titles the judge of record labels left (blue), neither (grey) and right (orange), sorted from most left-reading to most right-reading, lane after the handle, score at the right.*

![Lane composition.](figures/14_leaning_lane_composition.png)
*Mean composition by lane.*

![Three models per channel.](figures/14_leaning_models_by_channel.png)
*The same channels with all three models' scores: circles = judge of record, squares = Gemma, triangles = Qwen. Where the small models' markers sit far from the circle is where they misread the channel.*

Two things in that table deserve a look. The news lanes are mostly *neither*, as they should be, but their partisan-read titles tilt left (18 left vs 4 right across the wires, the press and legacy TV): the judge reads a title hostile to the administration as left even in a news headline, so part of that tilt is the target-versus-stance ambiguity that no model fully escapes. And the interview podcasts lean right as a lane (14 right, 7 left), which the lane proposal, built on format rather than politics, did not encode.

Lane means (all models; the 'neither' columns are the mean share of a channel's titles labelled neither):

| lane | n_creators | qwen3:14b score | gemma3:12b score | Claude Opus score | qwen3:14b 'neither' | gemma3:12b 'neither' | Claude Opus 'neither' |
|---|---|---|---|---|---|---|---|
| left commentary | 48 | 0.14 | -0.25 | -0.56 | 0.59 | 0.30 | 0.38 |
| independent digital news | 20 | 0.04 | -0.18 | -0.38 | 0.70 | 0.47 | 0.50 |
| humour / satire | 8 | 0.02 | -0.09 | -0.20 | 0.80 | 0.57 | 0.65 |
| legal commentary | 9 | 0.07 | -0.04 | -0.27 | 0.58 | 0.31 | 0.41 |
| streamers | 26 | 0.13 | -0.11 | -0.24 | 0.74 | 0.52 | 0.64 |
| explainers / geopolitics | 7 | -0.01 | -0.12 | -0.07 | 0.99 | 0.79 | 0.91 |
| centrist / heterodox | 12 | 0.13 | -0.05 | -0.14 | 0.73 | 0.49 | 0.59 |
| US press | 19 | 0.07 | -0.03 | -0.03 | 0.89 | 0.71 | 0.84 |
| wires & international | 14 | 0.05 | 0.07 | -0.08 | 0.90 | 0.72 | 0.91 |
| interview podcasts | 23 | 0.07 | 0.01 | 0.01 | 0.79 | 0.56 | 0.68 |
| US legacy TV | 9 | 0.10 | 0.13 | -0.03 | 0.80 | 0.63 | 0.81 |
| right commentary | 75 | 0.19 | 0.37 | 0.43 | 0.70 | 0.41 | 0.52 |
| right TV networks | 4 | 0.30 | 0.50 | 0.36 | 0.67 | 0.41 | 0.64 |


The most left-reading and most right-reading channels under the judge of record:

| creator | lane | n_titles | judge_score | judge_side |
|---|---|---|---|---|
| @LegalAFMTN | legal commentary | 16 | -1.00 | left |
| @DannyHaiphongYT | left commentary | 16 | -1.00 | left |
| @deanwithrs | streamers | 16 | -1.00 | left |
| @TheDailyBeast | US press | 16 | -1.00 | left |
| @aaronparnas1 | left commentary | 16 | -0.94 | left |
| @JackCocchiarellaShow | left commentary | 16 | -0.94 | left |
| @briantylercohen | left commentary | 16 | -0.94 | left |
| @MeidasTouch | left commentary | 16 | -0.94 | left |
| @Lunaoi | left commentary | 9 | -0.89 | left |
| @dollemore | left commentary | 16 | -0.88 | left |
| @YaBoiHakim | left commentary | 16 | -0.88 | left |
| @thedavidpakmanshow | left commentary | 16 | -0.88 | left |


| creator | lane | n_titles | judge_score | judge_side |
|---|---|---|---|---|
| @BlackConservativePerspective | right commentary | 16 | 1.00 | right |
| @CamHigby | right commentary | 16 | 1.00 | right |
| @ActualJusticeWarrior | right commentary | 16 | 0.94 | right |
| @OfficialSaharTV | right commentary | 16 | 0.88 | right |
| @MLChristiansen | right commentary | 16 | 0.88 | right |
| @nationalreview | US press | 16 | 0.88 | right |
| @MrReaganUSA | right commentary | 16 | 0.88 | right |
| @TheOfficerTatum | right commentary | 16 | 0.88 | right |
| @MarkDice | right commentary | 16 | 0.81 | right |
| @AndWeKnowOfficial-o9b | right commentary | 16 | 0.81 | right |
| @X22Report-y5y | right commentary | 16 | 0.75 | right |
| @bennyjohnson | right commentary | 16 | 0.75 | right |


Commentary channels whose title-leaning contradicts their lane under the judge of record (5 of 123):

| creator | lane | value | implied_side | n_titles |
|---|---|---|---|---|
| @OwenReport | right commentary | -0.25 | left | 16 |
| @PhillipScottPodcast | left commentary | 0.06 | right | 16 |
| @thejimmydoreshow | left commentary | 0.00 | tie | 16 |
| @Tim_Black | left commentary | 0.19 | right | 16 |
| @MrTariqNasheed | left commentary | 0.19 | right | 16 |


These are not labelling accidents: Owen Shroyer's anti-war, anti-establishment titles read left; Tariq Nasheed's and Tim Black's read right on the titles that attack Democrats; Jimmy Dore's split evenly. They are the channels whose politics the left/right axis fits worst, and a reason to treat the lane proposal as provisional.

## What the frontier model calls right and what it calls left

Titles Claude Opus labelled right (783) vs left (1017), scored by weighted log-odds (which words are over-used on one side) and rank-turbulence divergence (which words move most between the two frequency rankings).

![Words by side.](figures/14_leaning_words.png)
*Left: rank of each word among right-labelled titles against its rank among left-labelled titles (log axes); words far from the diagonal belong to one side. Right: the largest rank-turbulence-divergence contributions, signed by side.*

Right-labelled vocabulary (top 20):

| word | log_odds_right_vs_left | z | count_right | count_left | rtd_contribution |
|---|---|---|---|---|---|
| women | 1.75 | 4.03 | 29 | 5 | 0.01 |
| woke | 2.32 | 3.88 | 25 | 2 | 0.01 |
| fraud | 1.71 | 3.49 | 22 | 4 | 0.00 |
| california | 2.13 | 3.37 | 19 | 2 | 0.00 |
| left | 1.49 | 3.24 | 21 | 5 | 0.00 |
| democrat | 2.51 | 3.17 | 17 | 1 | 0.00 |
| kirk | 2.39 | 2.89 | 14 | 1 | 0.00 |
| trans | 2.34 | 2.79 | 13 | 1 | 0.00 |
| people | 1.19 | 2.70 | 18 | 6 | 0.00 |
| islam | 2.29 | 2.68 | 12 | 1 | 0.00 |
| white | 0.91 | 2.63 | 24 | 11 | 0.00 |
| america | 0.72 | 2.57 | 32 | 18 | 0.00 |
| charlie | 3.41 | 2.56 | 14 | 0 | 0.00 |
| state | 0.99 | 2.47 | 19 | 8 | 0.00 |
| men | 2.16 | 2.45 | 10 | 1 | 0.00 |
| pray | 3.41 | 2.37 | 12 | 0 | 0.00 |
| biden | 1.26 | 2.36 | 13 | 4 | 0.00 |
| liberal | 1.63 | 2.31 | 10 | 2 | 0.00 |
| muslim | 1.63 | 2.31 | 10 | 2 | 0.00 |
| democrats | 0.73 | 2.28 | 25 | 14 | 0.00 |


Left-labelled vocabulary (top 20):

| word | log_odds_right_vs_left | z | count_right | count_left | rtd_contribution |
|---|---|---|---|---|---|
| trump | -1.35 | -12.23 | 79 | 426 | -0.00 |
| maga | -1.97 | -5.23 | 5 | 65 | -0.01 |
| iran | -1.12 | -4.93 | 20 | 86 | -0.00 |
| israel | -1.72 | -4.29 | 5 | 46 | -0.00 |
| war | -0.86 | -4.07 | 26 | 82 | -0.00 |
| epstein | -1.36 | -3.68 | 7 | 40 | -0.00 |
| breaking | -2.41 | -3.49 | 1 | 29 | -0.00 |
| donald | -2.30 | -3.12 | 1 | 23 | -0.00 |
| hasanabi | -2.13 | -2.68 | 1 | 17 | -0.00 |
| fox | -2.09 | -2.60 | 1 | 16 | -0.00 |
| files | -1.39 | -2.50 | 3 | 18 | -0.00 |
| doj | -1.20 | -2.40 | 4 | 19 | -0.00 |
| vance | -3.03 | -2.35 | 0 | 15 | -0.00 |
| republicans | -1.06 | -2.29 | 5 | 20 | -0.00 |
| secret | -1.30 | -2.28 | 3 | 16 | -0.00 |
| jd | -3.03 | -2.27 | 0 | 14 | -0.00 |
| gaza | -1.91 | -2.23 | 1 | 12 | -0.00 |
| finally | -1.46 | -2.16 | 2 | 13 | -0.00 |
| israeli | -1.85 | -2.13 | 1 | 11 | -0.00 |
| ice | -0.56 | -2.10 | 18 | 41 | -0.00 |


Read as a map of the two grammars of attack: the right's titles are about the left, the woke, women and trans issues, Islam, fraud, Newsom and Fauci; the left's are about Trump, MAGA, the war, Epstein, ICE and the DOJ, and they carry the outrage furniture (breaking, secret, panics, disaster). The same lists per model, and for the titles all three agree on (n = 285 right, 162 left):

| model | right | left |
|---|---|---|
| qwen3:14b | gop, democrat, trump, maga, fox, nick, islam, candace, report, putin, owens, attacks | black, left, lies, money, gaza, worse, hasan, biden, progressive, piker, aoc, breaking |
| gemma3:12b | charlie, kirk, nick, fraud, candace, owens, democrat, fbi, america, myron, california, hegseth | trump, war, ice, hasanabi, hasan, breaking, racist, donald, gaza, democratic, israel, dsa |
| Claude Opus | women, woke, fraud, california, left, democrat, kirk, trans, people, islam, white, america | trump, maga, iran, israel, war, epstein, breaking, donald, hasanabi, fox, files, doj |
| all three agree | democrat, woke, fraud, islam, california, fbi, liberal, report, election, brutal, jlp, ds | trump, war, iran, israel, donald, black, lies, maga, gaza, worse, breaking, money |


The small models' lists are subject maps (MAGA, GOP and Trump-panic words on the "right", racism and Gaza on the "left"); the frontier model's list is closer to a stance map. That difference is the whole story of this document.

## Method

1. **Sample.** For each of the 274 creators, 16 unique edited-upload titles drawn at random (seed 20260914; creators with fewer than 16 uploads topped up from live VODs): 4,352 titles.
2. **Labelling.** The same prompt for all three judges (`cache/leaning_prompt.txt`): label the viewpoint the title's own wording signals as left, right or neither, with three anchoring examples; temperature 0, batches of 20, every response cached. Qwen3-14B and Gemma-3-12B run locally through Ollama; Claude Opus runs through the Claude Code CLI in print mode on a Claude Max subscription (218 calls, 52 minutes; the CLI reported an equivalent API cost of $18.86, not charged).
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
