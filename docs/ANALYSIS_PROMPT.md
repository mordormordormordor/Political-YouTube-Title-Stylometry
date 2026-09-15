# Title Stylometry analysis prompt (v3, 2026-09-14)

Run once over the whole corpus; per-creator cards come out of the same pass.

---

Act as a computational linguist and media data scientist. I have every video title, with
listing-level metadata, that 274 political-media creators (269 YouTube channels, 5 Rumble
channels) published between 2026-01-01 and 2026-09-14: 309,596 titles (251,114 edited
uploads, 52,699 live-stream VODs, 5,783 Rumble videos; take the exact count from the CSV).
About 13,600 rows have no view count (every Rumble row plus a few YouTube ones). Titles
plus the metadata below are the entire dataset. There are no transcripts, descriptions, tags, likes, comments or
thumbnails; do not infer or fabricate them.

**Files**

- `data/titles/videos.csv` - one row per video: `creator` (@handle or Rumble URL),
  `platform`, `tab` (`videos` = edited uploads, `streams` = live-stream VODs), `video_id`,
  `title`, `published` (YYYY-MM-DD; `date_precision` is `approx` = month-level for YouTube,
  `exact` for Rumble), `duration` (s), `view_count` (YouTube only, snapshot at fetch time),
  `live_status`, `url`, `channel_name`, `channel_id`.
- `data/titles/channels.jsonl` - one row per creator × tab: `channel_follower_count`
  (subscribers), `channel_is_verified`, `description`, `tags`, `videos_listed`.
- `data/creator_lists/title_stylometry_creators.txt` - the creator list (comments are
  annotations, not data).

**Goal.** Describe the title style of the political-media landscape: what stylistic
dimensions titles vary along, where each creator sits on them, which creators cluster
together on style as opposed to subject matter, how style moved month by month across
2026, and whether style predicts views within a channel. Every style result must be
controlled for topic, because two channels covering the same stories look alike on raw
vocabulary and two channels with the same style on different beats look different.

## Stage 0 - Preparation

1. Normalise titles: strip recurring show-name prefixes/suffixes, episode numbers, date
   stamps and channel-brand tags (detect them per creator as strings occurring in more
   than 20% of that creator's titles; list what was stripped). Keep the raw title too.
1b. Collapse exact-duplicate titles within a creator × genre to one row for every style
   and topic computation (3% of rows; nearly all are live-broadcast loops on news
   `streams` such as Times Now, Real America's Voice and Firstpost). Keep the repeat
   count as a feature (share of a creator's titles that are verbatim repeats) and keep
   every row for volume, view and hit-concentration statistics.
2. Treat `videos` and `streams` as separate genres throughout. Never pool them silently.
3. Flag creators with fewer than 50 titles in a genre as low-n; report them but exclude
   them from any ranking.
3b. Balance the corpus. Volume is wildly uneven: the median creator × genre has ~150
   titles, but 19 groups exceed 5,000 and four Indian news channels alone (Firstpost,
   ANI, Times Now, Times of India) hold 68k of the 304k titles. So: (a) every
   corpus-level or lane-level statistic is the mean (or median) of creator-level values,
   never a pool of titles; (b) any step that must pool titles - the topic-model fit,
   n-gram formula mining, corpus Zipf, the LLM-rating sample - uses a creator-balanced
   subset capped at 2,500 titles per creator × genre (random sample, seed reported),
   which trims 29 groups and keeps ~189k titles; (c) where a raw-pooled figure is shown
   anyway, label it as raw and show the balanced figure beside it.
4. Propose a lane assignment for all 274 creators from the channel names, descriptions
   and titles, as a CSV for me to correct, and use it for every between-group comparison
   once confirmed. Lanes should at least separate: left commentary; right commentary;
   US legacy TV news (CNN, Fox, ABC, CBS, NBC, MSNBC, NewsNation); wire and international
   news (Reuters, AP, BBC, Sky, Al Jazeera, AJ+, Firstpost, ANI, Times Now, Times of
   India, Guardian, and similar); independent/digital news; streamer and reaction;
   interview podcast; legal/institutional commentary; humour/satire. Add two more
   columns to the same CSV: `organisation`, grouping sister channels that belong to one
   outlet (Fox News / Fox News Clips; Timcast / TimcastIRL / TimcastNews; NYT / NYT
   Opinion / NYT Podcasts; The Young Turks / The Damage Report, which cross-post 28% of
   their titles verbatim; SNEAKO / LIVESNEAKO; MeidasTouch / Legal AF), and a boolean
   `clipper` for channels whose titles are written by fans or an editing team rather
   than the creator (HasanAbi Clips, HasanReactionsfanTwo, DestinyDGGClips,
   destinyhqclips, TheVaushPit, Fox News Clips, Lauren Chen Clips, and any others you
   detect). Report Stage 4 results at both creator and organisation level, exclude
   cross-posted duplicates from similarity calculations, and keep clippers visible as
   their own group so a fan editor's style is never attributed to the creator.

## Stage 1 - Topics (what they talk about)

Fit an embedding-based topic model on the normalised titles (sentence embeddings +
UMAP + HDBSCAN + class-based TF-IDF, or an equivalent short-text method; classic LDA is
not acceptable on 10-token texts). Fit on a stratified sample of ~100k titles if the full
set is too heavy, then assign all titles. Deliver: topic labels with top terms and three
example titles each; per-creator topic mix; topic share by lane; a monthly topic timeline
naming the story behind each month's spike; and the entities most named per topic. Tag
every topic as political or non-political (sport, entertainment, weather, lifestyle,
markets-only and similar; these sit mostly in the wire and Indian outlets) and report
each creator's political share. Keep the topic assignment per title, it is the control
variable for everything after this, and run the Stage 4 landscape twice, on all titles
and on political titles only, reporting where the two disagree.

## Stage 2 - Style dimensions (how they title), via multi-dimensional analysis

1. Extract 40-60 title-level style features, chosen for 10-word texts: length in
   characters and tokens; capitalised-token share, all-caps words, full-caps titles;
   per-100-title rates of `?`, `!`, `:`, `|`, quotes, brackets, ellipses, emoji, digits,
   dollar signs, percentages; first-person and second-person pronouns; contractions;
   imperatives; question words; intensifiers and superlatives; evaluative adjectives;
   negation; violence/outrage verbs (slams, destroys, exposed); hedges; nominalisations;
   named-person count and organisation count; "how to"/"explained"/"why" markers;
   discourse markers (let's, chat, okay); leading colon-label (BREAKING:, LIVE:);
   pipe-segmented structure; a formulaicity score (share of a creator's titles that
   repeat an n-gram template used by that creator elsewhere); and lexical diversity
   per creator × genre, measured as the Heaps' law exponent (and Zipf slope) on titles
   subsampled to a common token count, repeated 20 times and averaged, with the
   sample-size sensitivity reported.
2. Aggregate features to creator × genre × month (rates per 100 titles) - titles are too
   short for per-title factor analysis.
3. Run exploratory factor analysis on the aggregated matrix. Report the scree plot,
   retained factors, loadings, and name each factor from its loadings. Do NOT force a
   preset list of dimensions; test afterwards whether the factors map onto the
   candidate labels Sensational, Critical, Analytical/Informational, Educational,
   Conversational and Humor, and say plainly which candidates merged or failed to appear.
4. Validate: have an LLM rate a stratified sample of 3,000 raw titles on each candidate
   dimension (1-5) plus a humor flag; report the correlation between LLM ratings
   (aggregated the same way) and the factor scores, and inter-rater reliability on 300
   titles rated twice. Humor is scored by the LLM only; do not claim a lexicon detects it.
5. Topic control: re-estimate each creator's dimension scores within topic (residualise
   on topic mix, or report scores for the 5 largest shared topics). State how much of
   each creator's raw score was topic.

## Stage 3 - Format and hook classification (hybrid)

Structural formats by rule, with the regexes shown: question; breaking/live label;
episode-numbered show; interview/guest ("with", "ft.", "joins"); reaction/response;
confrontation ("vs", "destroys", "owns"); listicle; how-to/explainer. Semantic hooks by
LLM on the same 3,000-title sample, then a classifier trained on that sample and applied
to the rest (report held-out accuracy): curiosity gap (information withheld: forward
references, "here's why", "what happened next"); outrage/negative frame; and humor/irony.
Deliver the share of titles per category per creator and per lane, with three examples
each, and the agreement between rule and LLM labels where both apply.

## Stage 4 - The landscape

1. Cluster creators in style-dimension space (Stage 2, topic-controlled) and separately
   in topic space (Stage 1). Compare both clusterings to the lane assignment (adjusted
   Rand index) and to each other. The findings are where they disagree: creators who
   share a lane but not a style, and creators who share a style across lanes.
2. For every creator, its five nearest style neighbours and five nearest topic
   neighbours.
3. Who gets named: the top 25 people and organisations across the corpus, the lanes that
   name each most, and each entity's share of outrage-frame titles versus its overall
   share.
4. Convergent formulas: 1,370 distinct titles are used verbatim by two or more different
   creators ("This Is Insane" by seven, "This Is Disgusting" by five, "It Has Begun" by
   four). List the most-shared verbatim titles and the most-shared normalised templates
   (after replacing names, numbers and entities with placeholders), which lanes use
   them, and whether sharing runs within or across lanes. This is the cheapest evidence
   of hook conventions spreading through the landscape.

## Stage 5 - Time and engagement

1. Monthly drift, January to September 2026, per lane and for the 30 largest creators:
   dimension scores, hook shares, and month-to-month topic change. YouTube dates are
   month-accurate, so do not go finer than months; September covers only the 1st to the
   14th, so show it but never compare its volume with a full month.
2. Engagement, within creator only: for each creator with 100+ titles in a genre,
   regress log views on the dimension scores, hook categories and length, with
   publish-month and topic as controls, and normalise by subscriber count when comparing
   coefficients across creators. Report medians and robust effect sizes across creators,
   and the share of creators for which each feature has a consistent sign. Treat
   `view_count` as a snapshot that favours older videos, and say so. Rumble rows have no
   view count: exclude them from items 2 and 3 and treat `platform` as a covariate
   everywhere else rather than comparing platforms directly on five channels.
3. Hit concentration. For each creator × genre with 100+ videos, report the Gini
   coefficient of views and the share of views from the top 10% of videos. Fit the tail
   with the Clauset-Shalizi-Newman method and report the likelihood-ratio test against a
   lognormal; do not call a distribution a power law without it. Correlate concentration
   with the Stage 2 dimension scores and Stage 3 hook shares, within lane.

## Deliverables

- A corpus report: one plain-language headline finding per stage at the top, then the
  tables. Report null results as results.
- One profile card per creator with a fixed layout: n titles by genre, lane, topic mix
  (top 5), dimension scores as percentile ranks with the lane median beside them, hook
  shares, five nearest style neighbours, monthly drift sparkline data, and the
  engagement coefficients if n allows.
- Machine-readable outputs: `features.csv` (creator × genre × month), `dimensions.csv`
  (creator scores raw and topic-controlled), `topics.csv` (title → topic),
  `labels.csv` (the 3,000 LLM-rated titles), `lanes.csv`.
- A methods appendix: every preprocessing step, stopword list, feature definitions,
  the factor loadings, validation numbers, and sample sizes beside every statistic;
  plus the corpus-level Zipf exponent on normalised titles before and after prefix
  stripping, as a check that stripping removed the show-brand head; plus the runtime
  and any API cost of each stage, so the whole pipeline can be re-run when the corpus
  is refreshed.
- A browsable HTML page with a creator selector that renders the profile cards and the
  landscape maps, in addition to the Markdown report.

**Where things go and how they are built**

- Code lives in `pipeline_titles/` as modules run with `python -m pipeline_titles.<name>`,
  matching the rest of the repository, with pure helpers unit-tested under `tests/`.
  Every stage is a separate, re-runnable script that reads the previous stage's output
  from disk; nothing is computed only inside a notebook or a chat.
- Outputs go under `data/titles/analysis/` (tables) and `pipeline_titles/reports/`
  (the report and the HTML page). The four machine-readable tables above are the
  interface between stages.
- Environment: the project `.venv` has only yt-dlp, requests and pytest. Install what
  you need (sentence-transformers, bertopic with umap-learn and hdbscan, scikit-learn,
  factor_analyzer, spacy with a small English model, vaderSentiment, powerlaw) and pin
  them in `requirements-titles.txt`. Embedding 300k short titles is a few minutes on
  this Mac; topic-model fitting on the 100k stratified sample is the heaviest step.
- LLM ratings and labels: use the model the project already has credentials for (the
  quote pipeline's OpenAI setup via `OPENAI_API_KEY`, or a local Ollama model). Record
  the model id, the exact rating prompt, temperature and date in `labels.csv`, and cache
  every response so a re-run costs nothing.

Where a result could be an artefact of channel size, posting volume, video age, live-loop
duplicates or cross-posting, test that explanation before reporting the result. Prefer
fewer validated findings over many unvalidated ones; when two methods disagree, report
both.
