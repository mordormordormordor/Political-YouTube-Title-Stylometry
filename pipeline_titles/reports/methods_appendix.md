# Title Stylometry: methods appendix

_Generated 2026-09-22T14:30:02+00:00._

## Pipeline stages (module docstrings, verbatim)

### `pipeline_titles.prepare`

```
Stage 0 - prepare the title corpus for every later stage.

Reads data/titles/videos.csv and writes, under data/titles/analysis/:

    titles_prepared.parquet   one row per video (all 309,596 kept) with
                              title_raw, title_norm (show-name prefixes/suffixes,
                              episode numbers, date stamps and channel-brand tags
                              removed), stripped (what was removed), title_key,
                              is_dup / dup_count (verbatim repeats within a
                              creator x genre; first occurrence by date is kept),
                              in_balanced (creator-balanced subset, <= 2,500 unique
                              titles per creator x genre, seed 20260914),
                              low_n (creator x genre with < 50 unique titles)
    stripped_patterns.csv     per creator x genre: every brand pattern that was
                              stripped, its kind, share of titles and an example
    creator_genre_summary.csv rows, unique titles, repeat share, low-n flag,
                              balanced n, subscribers, months active
    zipf_check.csv            corpus Zipf exponent (creator-balanced subset) on raw
                              vs normalized titles, plus the head of each rank list

Brand detection rule (per creator x genre, on unique titles): a delimited leading
or trailing segment (split on ' | ', ' - ', ' – ', ' — ', ' • ', ' ~ ', a 'LABEL: '
colon label, a [bracketed] / (parenthesised) tag or a trailing #hashtag), with
digits collapsed to '#', that occurs in more than 20 % of the group's titles (and
in at least 10 titles) is a brand pattern and is removed wherever it appears in
that position. Generic format labels (LIVE, BREAKING, WATCH, FULL SHOW, ...) are
never stripped because they are style markers used by Stages 2 and 3. Episode
numbers and date stamps are removed from the first and last segment regardless of
frequency (patterns in EPISODE_RES / DATE_RES).

CLI:
    python -m pipeline_titles.prepare
    python -m pipeline_titles.prepare --min-share 0.2 --min-count 10
```

### `pipeline_titles.creators`

```
Stage 0b - write the creator table (data/titles/analysis/creators.csv).

Columns: creator, channel_name, platform, organization, clipper, subscribers,
n_videos, n_streams, low_n_videos, low_n_streams, note.

The seed lives in pipeline_titles/creator_seed.py. This script refuses to overwrite an
existing creators.csv (which may carry hand corrections) unless --force is given;
every later stage reads creators.csv, so correct the CSV, not the seed. The channel
grouping used in every between-group comparison (left / neutral / right) is not in
this file: it is each channel's leaning group from the leaning stage, joined at load
time by common.load_creators().

CLI:
    python -m pipeline_titles.creators            # write if missing
    python -m pipeline_titles.creators --force    # rebuild from the seed
```

### `pipeline_titles.leaning`

```
Stage 0d - political leaning from titles alone, judged by a frontier model (the stage
runs third, after creators, because its channel groups are what every later stage reports
by; its runtime record keeps the historical name stage7_leaning).

A creator-balanced sample is labeled left / right / neither by Claude Opus through the
Claude Code CLI in print mode (a Claude Pro/Max subscription covers it; temperature 0;
twenty titles per call, sent in a seeded random order so that a call mixes channels and
the judge sees nothing but the title text; every response cached). The label is the
viewpoint the TITLE'S OWN WORDING signals, not the subject. Two levels of analysis follow: the
titles themselves, and the channels grouped as left / neutral / right by their scores.

Runs. The sample was labeled in three runs, all with the same prompt at temperature 0. Runs
1 and 2 (the base draw, then the top-up) sent the titles in sample order, so a call held one
or two channels' titles and a title was read beside its channel's other titles; run 3 sent
every title again in shuffled batches. Run 3 is the labeling of record
(leaning_labels.csv.gz). Runs 1 and 2 are kept as the first reading
(leaning_labels_channel_batched.csv.gz, column `run`), and two_readings() compares the two
readings title by title and channel by channel. The readings differ in their batches by
design, so their disagreement is the judge's own inconsistency and the effect of a title's
company together; neither is measured alone. `--repeat` reads every title of the sample a
third time with a fresh shuffle (run 4, leaning_labels_repeat.csv.gz): a clean repeat of the
method, whose disagreement with the labels of record is the judge's own inconsistency (plus
the luck of different batch-mates), so with three readings the batch-context effect and the
judge's noise can be told apart (repeat_check()).

Sample. Every creator gets a base draw of N_BASE (16) unique edited-upload titles
(seed 20260914; live VODs top up creators with fewer uploads). Creators with at least
--min-uploads (50) unique uploads are then topped up to --n-per-creator (N_PER_CREATOR,
50) with further uploads spread evenly across months (12,478 titles; 239 creators at
50, 35 at their base).

The channel groups written here (leaning_by_creator.csv, column `group`) are the only
between-channel grouping in the pipeline: common.load_creators() joins them to the
creator table, and every later stage reports by them. The stage therefore runs right
after prepare / creators in run_all.

Outputs (data/titles/analysis/):
    leaning_labels.csv.gz       one row per sampled title with the label, is_base (base draw vs
                                month-spread top-up) and month: the labels of record (run 3)
    leaning_labels_channel_batched.csv.gz
                                the first reading: the same titles labeled in runs 1 and 2, batched
                                by channel (column `run`); Claude Opus only
    leaning_runs.json           the three labeling runs from the run log: titles sent, batch order,
                                calls, minutes, output tokens, the CLI's reported cost
    leaning_two_readings.json   the first reading against the labels of record: agreement and kappa
                                (overall and per run), the confusion table, partisan shares, the
                                titles that changed side; the channel scores under the two readings
                                (Spearman, mean change, groups changed);
                                leaning_two_readings_channels.csv has the per-channel values and
                                leaning_two_readings_changed_titles.csv the titles whose label changed
    leaning_labels_repeat.csv.gz
                                the repeat: every title read again with a fresh shuffle (run 4)
    leaning_repeat.json         the repeat against the labels of record (a clean repeat: agreement, kappa,
                                the confusion table, channel scores) and against the first reading, plus the
                                three readings together (how many titles all three agree on);
                                leaning_repeat_channels.csv and leaning_repeat_changed_titles.csv as above
    leaning_label_shares.json   the labels' counts and shares
    leaning_by_creator.csv      per channel: label shares, score = (right - left) / n over its
                                sampled titles, and the group the score implies (left below
                                -0.05, right above +0.05, neutral between)
    leaning_groups.csv          the three groups: channels, titles, mean score and composition
    leaning_words.csv           right vs left vocabulary: weighted log-odds (alpha0 = 500) and
                                rank-turbulence-divergence contributions (alpha = 1/3)
    leaning_split_half.csv      split-half reliability of the channel scores
                                (channels with >= 32 labels, 20 random splits)
    leaning_stability.csv       the base 16-title score against the score from the disjoint
                                top-up titles and from all titles (Spearman, mean absolute
                                change, channels whose group changed);
                                leaning_stability_channels.csv has the per-channel values
    leaning_by_group_month.csv  partisan share and score per channel group x month
    plus the log-odds lexicon files of leaning_lexicon.py

Usage-limit replies from the CLI are waited out (5, 15, 30, 60 min). Prompt v2
(`--prompt-version v2`) also asks for the title's TARGET (who is attacked or featured),
which separates "attacks Trump" from "speaks for the left".

Human check. analyse() writes a blind adjudication sheet (leaning_human_sheet.csv: 200
titles, model labels hidden). Fill `human_label` and re-run with `--human-labels
data/titles/analysis/leaning_human_sheet.csv` to get the judge's agreement with a human
(leaning_human_agreement.csv). That is the accuracy check.

CLI:
    python -m pipeline_titles.leaning --n-per-creator 50            # sample, label, analyze
    python -m pipeline_titles.leaning --n-per-creator 50 --prompt-version v2
    python -m pipeline_titles.leaning --analyze-only [--human-labels <filled sheet>]
    python -m pipeline_titles.leaning --repeat [--shuffle-seed N]   # read every title again, fresh shuffle
```

### `pipeline_titles.annotate`

```
Stage 0c - spaCy annotation of every unique normalized title.

Runs en_core_web_sm (tagger, parser, NER) once over the unique `title_norm`
strings of titles_prepared.parquet and caches the result, so Stage 1 (entities per
topic), Stage 2 (POS-based style features, named-person / organization counts) and
Stage 4 (who gets named) never re-run the model.

ALL-CAPS titles ("TRUMP DESTROYS CNN") defeat the NER, so they are truecased first
with a lexicon learned from the corpus itself: a word is a proper noun if it is
capitalized in >= 80 % of its non-initial occurrences in mixed-case titles (>= 3
occurrences), and an acronym if it is ALL-CAPS in >= 80 % of them. The truecased
text is stored beside the annotations (`text_tc`); every feature that depends on
capitalization is computed from the original text, not from `text_tc`.

Output: data/titles/analysis/annotations.parquet, one row per unique title_norm:
    title_norm, text_tc, all_caps, tokens, lemmas (\x1f-joined), pos, tag, dep,
    ent_iob (space-joined, one item per token), ents ('text\x1elabel' \x1f-joined),
    n_tokens, n_person, n_org, n_gpe, n_ents

CLI:
    python -m pipeline_titles.annotate            # all unique titles
    python -m pipeline_titles.annotate --limit 5000 --processes 4
```

### `pipeline_titles.embed`

```
Stage 1a - sentence embeddings of every unique normalized title.

Encodes the unique `title_norm` strings of titles_prepared.parquet with a
sentence-transformers model (all-mpnet-base-v2, 768-d, L2-normalized) on the Mac
GPU and caches them, so the topic model (Stage 1), the hook classifier (Stage 3)
and the template analysis never re-encode.

Output (data/titles/analysis/cache/):
    embeddings.npy          float16 [n_unique, 768], rows in the order of
    embeddings_index.parquet  title_norm -> row (sorted unique strings)

CLI:
    python -m pipeline_titles.embed
    python -m pipeline_titles.embed --model sentence-transformers/all-MiniLM-L12-v2 --batch-size 512
```

### `pipeline_titles.topics`

```
Stage 1 - embedding-based topic model (BERTopic: sentence embeddings + UMAP +
HDBSCAN + class-based TF-IDF) fitted on a creator-stratified ~100k sample, then
every title assigned to its nearest topic centroid.

Reads titles_prepared.parquet, cache/embeddings.npy (Stage 1a), annotations.parquet
(Stage 0c, for the entities per topic) and creators.csv (with the channel groups of
the leaning stage). Writes, under
data/titles/analysis/:

    topics.csv                row_id, video_id, creator, genre, topic_id, topic_sim,
                              weak_assignment (all 309,596 rows; verbatim repeats get
                              the topic of their unique title)
    topic_labels.csv          topic_id, label (LLM), political, category, top_terms,
                              n_fit, n_unique_all, example_1..3, top_persons, top_orgs
    creator_topic_mix.csv     creator x genre x topic share (unique titles)
    topic_by_group.csv        channel group x genre x topic: mean of creator shares (+ raw pooled)
    topic_timeline.csv        month x topic: creator-balanced share and raw count
    topic_spikes.csv          per month, the topics that spike most vs. their own
                              mean, with the entities and example titles of that month
    creator_political_share.csv
    cache/topic_centroids.npy, cache/topic_fit_sample.parquet

Fit sample: from the creator-balanced subset, per creator x genre capped so that
the total is ~100,000 (cap found by bisection, seed 20260914). UMAP(15 neighbors,
5 dims, cosine, min_dist 0) -> HDBSCAN(min_cluster_size 80, min_samples 15, eom).
If HDBSCAN yields more than --max-topics topics they are merged to that number by
c-TF-IDF similarity. Outliers and all non-fit titles are assigned to the nearest
centroid (cosine); an assignment is 'weak' when its similarity is below the 10th
percentile of the similarities of HDBSCAN's own members.

CLI:
    python -m pipeline_titles.topics
    python -m pipeline_titles.topics --fit-size 100000 --min-cluster-size 80 --max-topics 250
    python -m pipeline_titles.topics --label-only        # re-run only the LLM labeling
```

### `pipeline_titles.llm_rate`

```
Stage 2c - LLM ratings of a stratified 3,000-title sample (plus a 300-title retest).

Draws the sample from titles_prepared.parquet (unique titles only; every creator x
genre gets a base allocation - 8 titles for groups with >= 50 titles, 2 for low-n
groups - and the remainder is spread in proportion to log10(n), seed 20260914),
rates each RAW title with the rating model in batches of 20, and writes
data/titles/analysis/labels.csv with, per title:

    sensational, critical, analytical, educational, conversational   1-5
    humor, curiosity_gap, outrage                                    0/1
    format_llm     question | breaking_live | episode_show | interview_guest |
                   reaction | confrontation | listicle | howto_explainer | none
    retest_*       the same fields from a second pass over 300 titles, rated in
                   different, re-shuffled batches (test-retest reliability)
    model, prompt_id, prompt_sha256, temperature, rated_at, prompt (exact text)

Every model response is cached under data/titles/analysis/cache/llm/<sha1>.json,
so a re-run costs nothing; the run's call count, token counts and wall-clock go to
runtimes.jsonl (cost is 0: local model).

CLI:
    python -m pipeline_titles.llm_rate                     # full run (~1 h)
    python -m pipeline_titles.llm_rate --limit 60          # smoke test
    python -m pipeline_titles.llm_rate --rekey             # after a re-prepare: re-key labels.csv, no model call
```

### `pipeline_titles.features`

```
Stage 2a - title-level style features, aggregated to creator x genre x month.

Reads titles_prepared.parquet, annotations.parquet and creators.csv. Writes:

    features_title.parquet     one row per video (all rows; repeats copy their unique
                               title's values): ~75 title-level features
    features.csv               creator x genre x month over UNIQUE titles: binary and
                               count features as rates per 100 titles (suffix _p100),
                               continuous features as means (suffix _mean), n_titles
    features_creator.csv       creator x genre over all months, plus repeat_share,
                               formulaicity, Heaps' exponent and Zipf slope at three
                               subsample sizes (20 repeats each, seed 20260914)
    lexical_diversity_sensitivity.csv   rank correlations of the Heaps'/Zipf values
                               across the three subsample sizes
    creator_templates.csv      the leading / trailing 3-gram templates each creator
                               re-uses most (entities and numbers masked)
    feature_definitions.csv    name, family, text it is computed on, definition, aggregation

Text used: lexical, pronoun, punctuation, syntax and entity features are computed on
the NORMALIZED title (brand prefixes/suffixes, episode numbers and dates removed);
the raw-structure family (lead_colon_label, lead_live, pipe_segments_raw, ...) on
the RAW title, because a 'LIVE:' label or a '| Show Name' suffix is itself a style
choice. Humor is never lexicon-scored.

CLI:
    python -m pipeline_titles.features
    python -m pipeline_titles.features --no-diversity     # skip the 20x subsampling
```

### `pipeline_titles.factors`

```
Stage 2b - exploratory factor analysis of the aggregated style features, factor
scores for every cell, creator and title, and topic control.

Reads features.csv (creator x genre x month), features_title.parquet, topics.csv
and creators.csv. Writes, under data/titles/analysis/:

    efa_summary.json         features used / dropped (and why), n cells, KMO,
                             Bartlett, parallel-analysis result, retained factors,
                             variance explained, factor correlations (oblimin)
    scree.csv, scree.png     eigenvalues of the correlation matrix vs the
                             parallel-analysis 95th percentile
    factor_loadings.csv      oblimin loadings (plus varimax for comparison)
    factor_names.json        auto-generated names from the loadings; edit the
                             "name" fields by hand - report.py reads this file
    dimensions_monthly.csv   cell scores (creator x genre x month), raw and
                             topic-controlled
    dimensions.csv           creator x genre: raw score, topic-expected component,
                             topic-controlled (residual) score, percentile ranks
                             within genre (non-low-n creators), channel-group medians
    dimensions_title.parquet row_id, topic_id, raw and residual title-level scores
    dimensions_by_topic.csv  creator scores within the 5 largest shared topics
    topic_control_summary.csv  per factor: share of title-level and creator-level
                             variance explained by topic

Method. Cells with >= 15 unique titles enter the EFA (each creator x genre
contributes at most 9 monthly rows, so the matrix is creator-balanced by
construction). Features are the _p100 / _mean columns minus artifacts (see
EXCLUDE) and minus features below 0.5 per 100 titles or with |r| > 0.95 to an
earlier feature. Number of factors: Horn's parallel analysis (100 random matrices,
95th percentile), capped at MAX_FACTORS. Extraction: minres, oblimin rotation
(varimax reported beside it). Factor scores: regression method; the same weights
are applied to title-level features (binary features x100 so the units match),
which gives cell scores exactly by linearity.

Topic control: for every factor the topic mean is estimated on the creator-
balanced subset; a title's residual is its score minus its topic's mean; a
creator's topic-controlled score is the mean residual of its unique titles, and
raw minus controlled is the part of its raw score that its topic mix predicts.

CLI:
    python -m pipeline_titles.factors
    python -m pipeline_titles.factors --n-factors 6     # force a solution (for comparison only)
```

### `pipeline_titles.formats`

```
Stage 3 - structural formats by rule and semantic hooks by LLM + classifier.

Formats (regex on the RAW title, case-insensitive unless noted; the exact patterns
are written to format_rules.csv): question, breaking_live, episode_show,
interview_guest, reaction, confrontation, listicle, howto_explainer.

Hooks (curiosity_gap, outrage, humor): the LLM labels of the 3,000-title sample
(labels.csv) train one logistic-regression classifier per hook on the title's
sentence embedding plus 12 style features; 5-fold cross-validation chooses C, a
stratified 20 % hold-out reports accuracy / balanced accuracy / F1 / AUC, and the
model refitted on the whole sample is applied to every unique title.

Outputs (data/titles/analysis/):
    formats.parquet          row_id + format flags + hook probabilities and labels
    format_rules.csv         the regexes
    format_hook_shares.csv   creator x genre shares (unique titles) and channel group x
                             genre means of creator shares (non-low-n creators)
    format_examples.csv      three examples per category per channel group and corpus-wide
    hook_classifier.json     CV and hold-out metrics per hook
    format_agreement.csv     rule vs LLM format label on the rated sample
                             (precision / recall / F1 / Cohen's kappa per category)

CLI:
    python -m pipeline_titles.formats
```

### `pipeline_titles.landscape`

```
Stage 4 - the landscape: creators clustered in style space and in topic space,
compared with the channel groups (left / neutral / right, from the leaning stage);
nearest neighbors; who gets named; convergent formulas.

Reads dimensions.csv / dimensions_title.parquet (Stage 2), topics.csv +
topic_labels.csv + creator_topic_mix.csv (Stage 1), formats.parquet (Stage 3),
annotations.parquet, titles_prepared.parquet and creators.csv (with the groups).

Every similarity is computed per genre over non-low-n creators, with cross-posted
titles removed (a title whose case-insensitive key also appears under another
creator of the same organization, e.g. TYT / The Damage Report). The whole
clustering block runs twice: on all titles and on political titles only.

Outputs (data/titles/analysis/):
    style_clusters.csv, topic_clusters.csv     cluster id per creator x genre (all / political)
    cluster_comparison.csv                     adjusted Rand index: style vs group, topic vs group, style vs topic
    group_style_cohesion.csv                   within-group vs between-group style distance per channel group
    disagreements_group_style.csv              group-mates in different style clusters, and style-mates across groups
    neighbours_style.csv, neighbours_topic.csv five nearest neighbors per creator x genre
    map_style.csv, map_topic.csv               2-D coordinates (PCA of style z-scores; MDS of topic JS distance)
    entities_top.csv                           top 25 people and organizations (creator-balanced counts), the
                                               channel groups naming them most, outrage-frame share vs overall
    shared_titles.csv, shared_templates.csv    verbatim titles / masked templates used by >= 2 creators
    org_style.csv                              organization-level style scores (title-weighted mean of members)

CLI:
    python -m pipeline_titles.landscape
```

### `pipeline_titles.timeline`

```
Stage 5a - monthly drift, January to September 2026.

Reads dimensions_monthly.csv (Stage 2 cell scores), formats.parquet (Stage 3),
topics.csv, titles_prepared.parquet and creators.csv (with the channel groups). Months
are the only safe time
unit (YouTube listing dates are month-accurate); September is 1-14 only and is
flagged partial_month = True everywhere - it is shown but its volume is never
compared with a full month.

Outputs (data/titles/analysis/):
    drift_group_monthly.csv    channel group x genre x month: mean of creator cell scores
                               (raw and topic-controlled), hook shares, n_creators
    drift_top30_monthly.csv    the 30 largest creators (unique titles): the same per
                               creator x genre x month (sparkline data for the cards)
    drift_creator_monthly.csv  every creator x genre x month (cards)
    topic_change_monthly.csv   month-to-month Jensen-Shannon distance between a
                               creator's consecutive monthly topic mixes
    topic_change_group_monthly.csv   the same per channel group x genre x month (mean, median)
    drift_trends.csv           per channel group x genre and per top-30 creator x genre: the
                               Spearman trend of each controlled score and hook share
                               over the nine months

CLI:
    python -m pipeline_titles.timeline
```

### `pipeline_titles.engagement`

```
Stage 5b - does title style predict views, within creator?

For every creator x genre with >= 100 YouTube titles that carry a view count, an
OLS regression of log(1 + views) on the title's factor scores (Stage 2, raw
title-level), its hook labels (Stage 3), its length in tokens, with publish-month
dummies and topic dummies (topics with >= 5 titles for that creator, the rest
pooled) as controls; HC3 standard errors. Predictors are z-scored within the
creator, so a coefficient is the change in log views per one within-creator
standard deviation. Views are a snapshot taken at fetch time (2026-09-14), which
favors older videos; the month dummies absorb that within a creator, but
coefficients still describe views-to-date, not lifetime views.

Subscriber normalization: log(views / subscribers) = log(views) - log(subscribers),
a constant within creator, so it leaves every slope unchanged; the standardized
coefficients are therefore already comparable across creators, and subscriber
count is reported beside them.

Rumble rows have no view count and are excluded here.

Outputs (data/titles/analysis/):
    engagement_coefficients.csv   creator x genre x predictor: coefficient, HC3 SE, p, n, R2
    engagement_summary.csv        across creators (per genre, and per channel group): median,
                                  IQR, share positive, share significant (+/-), n_creators
    engagement_model.json         specification

CLI:
    python -m pipeline_titles.engagement
```

### `pipeline_titles.hits`

```
Stage 5c - hit concentration: how unequal are views within a channel, and
does title style go with a heavier tail?

For every creator x genre with >= 100 YouTube videos carrying a view count (all
rows, repeats included: a re-uploaded live loop is a separate video with its own
views): the Gini coefficient of views, the share of views held by the top 10 % of
videos, and a Clauset-Shalizi-Newman power-law fit of the tail (powerlaw.Fit,
discrete, xmin estimated by KS minimization) with the log-likelihood-ratio test
against a lognormal (R > 0 favors the power law; p is the significance of R).
A tail is called power-law-like only when R > 0 and p < 0.05.

Then, within channel group (left / neutral / right): Spearman correlations across
creators between concentration (Gini, top-10 % share) and the topic-controlled
dimension scores and hook shares; plus the same correlations with log(number of
videos) and log(subscribers) as the size-artifact check, and a pooled within-group
estimate (values demeaned by group x genre).

Outputs (data/titles/analysis/):
    hit_concentration.csv               per creator x genre (Gini, top shares, CSN fit, rank-size
                                        Zipf slope of views over all videos and over the top decile)
    hit_concentration_correlations.csv  within-group and pooled-within-group correlations

CLI:
    python -m pipeline_titles.hits
```

### `pipeline_titles.profiles`

```
Stage 6 - channel profiles behind the question documents (9, 11, 12, 13):

    caps_profile.csv        share of each creator x genre's unique titles by capitalization
                            style (all_caps, selective_caps, title_case, sentence_case,
                            mixed_other, short_other; rules in textstats.caps_style), read
                            off the raw title as published: the normalized title strips a
                            channel's fixed show name and episode number along with its
                            brand tag, which left "Joe Rogan Experience #2551 - Daniel
                            Kokotajlo" as two words and "short / other"; a brand tag adds
                            capitalized words a Title Case rule does not mind, and one
                            always written in capitals is learned as an acronym;
                            caps_style_title.parquet carries the style of every unique
                            title (row_id, caps_style) for the Zipf / views stage
    top_words.csv           the most frequent non-stopwords: creator-balanced (mean over
                            ranked creators of the share of titles containing the word)
                            beside the raw pooled share
    arousal_index.csv       0-1 composite per creator x genre of five components: ALL-CAPS
                            word share, exclamation marks per title, power words per title
                            (shock words + violence verbs + intensifiers), emoji per title,
                            VADER intensity (positive + negative); each component winsorized
                            at the 2nd/98th percentile across ranked creators of the genre,
                            min-max scaled to 0-1, and averaged
    signature_keywords.csv  top 10 words per creator by weighted log-odds (informative
                            Dirichlet prior, alpha0 = 500) against all other creators' titles
    style_twins.csv         every (left channel, right channel) pair (the channel groups of
                            the leaning stage) with its distance in z-scored topic-controlled
                            style space; style_twins_nearest.csv gives each creator's nearest
                            cross-divide twin and how that distance ranks among all its
                            neighbors

CLI:
    python -m pipeline_titles.profiles
```

### `pipeline_titles.zipf_views`

```
Stage 6b - Zipf's law and views over time, for document 7.

Three ways of cutting the corpus run through the whole stage:
    channel group   left / neutral / right channels (each channel's leaning group, Stage 0d)
    title label     left / neither / right titles (the judge's label of the sampled titles)
    caps style      ALL CAPS / selective CAPS / Title Case / Sentence case / mixed / short
                    (textstats.caps_style, written per title by the profiles stage)

Zipf's law for words. For every system (the corpus, each channel group, each title
label, each caps style) the rank-frequency table of its tokens and the OLS exponent of
log frequency on log rank over the top 100 / 1,000 / 5,000 types (prepare.zipf_slope,
the same tokenizer as the Stage 0 Zipf check, stopwords kept: Zipf's law is about the
whole vocabulary). Systems differ in size and the exponent depends on size, so a
size-matched exponent is reported beside it: SIZE_MATCH_N titles drawn SIZE_MATCH_REPEATS
times from the system, exponent over the top 200 ranks, averaged. Creator-level Zipf
exponents (Stage 0 check, Stage 2 subsampled Zipf / Heaps) are averaged per channel
group.

Zipf's law for views. Within a channel, videos ranked by views (hits.views_zipf_slope,
Stage 5c) give a rank-size slope; those slopes, the Gini and the top-10 % share are
summarized per channel group and per channel's dominant caps style.

Views over time. Views are a fetch-time snapshot (2026-09-14), so a January video has
had eight months to collect them and a September one two weeks: the raw curve falls
with publication month for everyone. Two measures per month:
    median views          over the videos of the group (and the median over channels of
                          each channel's median, so four Indian news channels cannot
                          carry a group)
    relative log views    mean over titles of log(1 + views) minus the mean log(1 + views)
                          of the same channel's videos in the same month: how a title
                          did against its own channel's average that month (0 = the
                          channel's average title; +0.1 = about 10 % more views); the
                          measure that makes caps styles and title labels comparable

Edited uploads and unique titles throughout. The word systems and the caps-style shares use
the creator-balanced subset on both platforms; the views block is YouTube only (Rumble has no
view counts); the views rank-size slopes, Gini and top-10 % share come from the hits stage,
which counts every video (repeats included).

Outputs (data/titles/analysis/):
    zipf_words.csv               one row per system: tokens, types, Zipf exponents, top words
    zipf_words_curves.csv        rank-frequency curves (ranks 1..5000) per system
    zipf_by_group.csv            creator-level Zipf / Heaps and the views rank-size slopes,
                                 Gini and top-10 % share, per channel group and per dominant
                                 caps style (n_creators_1500 = channels with enough tokens
                                 for the subsampled Zipf / Heaps exponents)
    views_by_month.csv           per grouping x group x month (and "all"): n videos, median
                                 views, creator-median views, relative log views
    caps_style_by_group.csv      caps-style shares per channel group and per title label
    label_by_caps_style.csv      title labels x caps style: share of each label within the
                                 style, and relative log views of the labeled titles per
                                 label x style

CLI:
    python -m pipeline_titles.zipf_views
```

## Stopword list

`a`, `about`, `amp`, `an`, `and`, `are`, `as`, `at`, `be`, `but`, `by`, `can`, `d`, `did`, `do`, `does`, `ep`, `episode`, `for`, `from`, `full`, `has`, `have`, `he`, `her`, `him`, `his`, `how`, `i`, `if`, `in`, `into`, `is`, `it`, `its`, `just`, `live`, `ll`, `m`, `me`, `my`, `n`, `new`, `news`, `no`, `not`, `of`, `on`, `or`, `our`, `out`, `over`, `re`, `s`, `she`, `show`, `so`, `t`, `than`, `that`, `the`, `their`, `them`, `then`, `there`, `these`, `they`, `this`, `those`, `to`, `up`, `ve`, `video`, `vs`, `was`, `watch`, `we`, `were`, `what`, `when`, `where`, `which`, `who`, `why`, `will`, `with`, `you`, `your`


## Feature definitions

| feature | family | text | definition | aggregation |
|---|---|---|---|---|
| n_chars | length | norm | characters | mean (_mean) |
| n_tokens | length | norm | word tokens | mean (_mean) |
| mean_word_len | length | norm | mean characters per word token | mean (_mean) |
| n_chars_raw | length | raw | characters of the raw title | mean (_mean) |
| allcaps_word_share | case | norm | share of 2+-letter words in ALL CAPS | mean (_mean) |
| has_allcaps_word | case | norm | any 3+-letter ALL-CAPS word | rate per 100 titles (_p100) |
| full_caps_title | case | norm | >60% of words ALL CAPS | rate per 100 titles (_p100) |
| cap_token_share | case | norm | share of non-initial words starting upper-case (title-case tendency) | mean (_mean) |
| lowercase_start | case | norm | first letter lower-case | rate per 100 titles (_p100) |
| q_mark | punctuation | norm | contains ? | rate per 100 titles (_p100) |
| excl | punctuation | norm | contains ! | rate per 100 titles (_p100) |
| multi_punct | punctuation | norm | !! ?? ?! runs | rate per 100 titles (_p100) |
| colon | punctuation | norm | contains : | rate per 100 titles (_p100) |
| pipe | punctuation | norm | contains \| (after brand stripping) | rate per 100 titles (_p100) |
| ellipsis | punctuation | norm | .. ... or … | rate per 100 titles (_p100) |
| trailing_ellipsis | punctuation | norm | ends with an ellipsis | rate per 100 titles (_p100) |
| quotes | punctuation | norm | double or paired single quotes | rate per 100 titles (_p100) |
| brackets | punctuation | norm | ( ) [ ] | rate per 100 titles (_p100) |
| dash | punctuation | norm | spaced dash or em dash | rate per 100 titles (_p100) |
| emoji_count | punctuation | norm | emoji characters | rate per 100 titles (_p100) |
| emoji | punctuation | norm | any emoji | rate per 100 titles (_p100) |
| digit | punctuation | norm | any digit | rate per 100 titles (_p100) |
| dollar | punctuation | norm | $ | rate per 100 titles (_p100) |
| percent | punctuation | norm | % | rate per 100 titles (_p100) |
| comma | punctuation | norm | , | rate per 100 titles (_p100) |
| period_end | punctuation | norm | ends with a full stop | rate per 100 titles (_p100) |
| year_mention | punctuation | norm | a 19xx/20xx year | rate per 100 titles (_p100) |
| hashtag | punctuation | raw | #tag (raw) | rate per 100 titles (_p100) |
| at_mention | punctuation | raw | @handle (raw) | rate per 100 titles (_p100) |
| first_sg | address | norm | I / me / my ... | rate per 100 titles (_p100) |
| first_pl | address | norm | we / us / our / let's | rate per 100 titles (_p100) |
| second_person | address | norm | you / your ... | rate per 100 titles (_p100) |
| contraction | address | norm | count of n't / 're / 've / 'll / 'd / 'm / it's-type contractions | rate per 100 titles (_p100) |
| imperative | address | norm | first word in the imperative lexicon or a base-form verb | rate per 100 titles (_p100) |
| q_word_start | address | norm | starts with a question word or auxiliary | rate per 100 titles (_p100) |
| wh_any | address | norm | any wh-word | rate per 100 titles (_p100) |
| intensifier | lexicon | norm | count, lexicons.INTENSIFIERS | rate per 100 titles (_p100) |
| superlative | lexicon | norm | count, lexicons.SUPERLATIVES + JJS/RBS tags | rate per 100 titles (_p100) |
| shock_word | lexicon | norm | count, lexicons.SHOCK_WORDS | rate per 100 titles (_p100) |
| pos_eval | lexicon | norm | count, lexicons.POS_EVAL | rate per 100 titles (_p100) |
| neg_eval | lexicon | norm | count, lexicons.NEG_EVAL | rate per 100 titles (_p100) |
| negation | lexicon | norm | any word in lexicons.NEGATION | rate per 100 titles (_p100) |
| violence_verb | lexicon | norm | count, lexicons.VIOLENCE_VERBS + VIOLENCE_PHRASES (slams, destroys, exposed ...) | rate per 100 titles (_p100) |
| hedge | lexicon | norm | any word in lexicons.HEDGES | rate per 100 titles (_p100) |
| discourse_marker | lexicon | norm | any word in lexicons.DISCOURSE (let's, chat, okay, lol ...) | rate per 100 titles (_p100) |
| nominalisation | lexicon | norm | count of -tion/-sion/-ment/-ness/-ity/-ance/-ence/-ism/-ship/-hood words (7+ letters) | rate per 100 titles (_p100) |
| n_person | entities | norm (truecased for NER) | PERSON entities | rate per 100 titles (_p100) |
| n_org | entities | norm (truecased for NER) | ORG entities | rate per 100 titles (_p100) |
| n_gpe | entities | norm (truecased for NER) | GPE/NORP/LOC entities | rate per 100 titles (_p100) |
| has_person | entities | norm (truecased for NER) | any PERSON entity | rate per 100 titles (_p100) |
| entity_first | entities | norm (truecased for NER) | title starts with a named entity | rate per 100 titles (_p100) |
| how_to | markers | norm | 'how to' / 'how I/we/you' | rate per 100 titles (_p100) |
| explainer | markers | norm | explained / explainer / breakdown / what is / the truth about ... | rate per 100 titles (_p100) |
| why_marker | markers | norm | starts with why, or 'reason' | rate per 100 titles (_p100) |
| curiosity_lex | markers | norm | lexicons.CURIOSITY_PHRASES (here's why, you won't believe, this is insane ...) | rate per 100 titles (_p100) |
| fwd_ref_start | markers | norm | starts with this/he/they/... and names no entity | rate per 100 titles (_p100) |
| listicle | markers | norm | N things/reasons/ways ... | rate per 100 titles (_p100) |
| reaction_lex | markers | norm | reacts to / responds to / reaction | rate per 100 titles (_p100) |
| interview_lex | markers | norm | with / w/ / ft. / joins / interview | rate per 100 titles (_p100) |
| confrontation_lex | markers | norm | vs / debate / destroys / owns / clash ... | rate per 100 titles (_p100) |
| lead_colon_label | raw_structure | raw | leading ALL-CAPS label followed by a colon (BREAKING:, LIVE:) | rate per 100 titles (_p100) |
| lead_breaking | raw_structure | raw | starts with BREAKING / JUST IN / DEVELOPING / ALERT / URGENT / EXCLUSIVE | rate per 100 titles (_p100) |
| lead_live | raw_structure | raw | starts with LIVE / WATCH / REPLAY | rate per 100 titles (_p100) |
| pipe_segments_raw | raw_structure | raw | number of \|-separated segments of the raw title | mean (_mean) |
| colon_segments_raw | raw_structure | raw | colons in the raw title | mean (_mean) |
| brackets_raw | raw_structure | raw | brackets in the raw title | rate per 100 titles (_p100) |
| brand_stripped | raw_structure | raw | a brand/episode/date pattern was stripped from this title | rate per 100 titles (_p100) |
| episode_raw | raw_structure | raw | episode number in the raw title | rate per 100 titles (_p100) |
| date_raw | raw_structure | raw | date stamp in the raw title | rate per 100 titles (_p100) |
| quoted_speech | raw_structure | norm | a quoted span of 2+ words | rate per 100 titles (_p100) |
| has_finite_verb | syntax | norm (spaCy en_core_web_sm) | any VBZ/VBD/VBP/MD (clause vs. noun-phrase title) | rate per 100 titles (_p100) |
| past_tense | syntax | norm (spaCy en_core_web_sm) | VBD/VBN | rate per 100 titles (_p100) |
| present_tense | syntax | norm (spaCy en_core_web_sm) | VBZ/VBP | rate per 100 titles (_p100) |
| modal | syntax | norm (spaCy en_core_web_sm) | MD | rate per 100 titles (_p100) |
| future_will | syntax | norm (spaCy en_core_web_sm) | will / gonna / 'll | rate per 100 titles (_p100) |
| det_share | syntax | norm (spaCy en_core_web_sm) | share of DET tokens | mean (_mean) |
| stopword_share | syntax | norm (spaCy en_core_web_sm) | share of tokens in the stopword list | mean (_mean) |
| propn_share | syntax | norm (spaCy en_core_web_sm) | share PROPN | mean (_mean) |
| noun_share | syntax | norm (spaCy en_core_web_sm) | share NOUN | mean (_mean) |
| verb_share | syntax | norm (spaCy en_core_web_sm) | share VERB+AUX | mean (_mean) |
| adj_share | syntax | norm (spaCy en_core_web_sm) | share ADJ | mean (_mean) |
| adv_share | syntax | norm (spaCy en_core_web_sm) | share ADV | mean (_mean) |
| num_share | syntax | norm (spaCy en_core_web_sm) | share NUM | mean (_mean) |
| vader_neg | sentiment | norm (VADER) | VADER negative | mean (_mean) |
| vader_pos | sentiment | norm (VADER) | VADER positive | mean (_mean) |
| vader_compound | sentiment | norm (VADER) | VADER compound | mean (_mean) |
| formulaic | formulaicity | norm (entities/numbers masked) | leading or trailing 3-gram template shared with >= 3 other titles of the same creator x genre | rate per 100 titles (_p100) |


## Lexicons (pipeline_titles/lexicons.py)

- **FIRST_SG** (14): i, i'd, i'll, i'm, i've, im, i’d, i’ll, i’m, i’ve, me, mine, my, myself

- **FIRST_PL** (14): let's, lets, let’s, our, ours, ourselves, us, we, we'll, we're, we've, we’ll, we’re, we’ve

- **SECOND** (17): u, ur, y'all, ya, yall, you, you'd, you'll, you're, you've, your, yours, yourself, you’d, you’ll, you’re, you’ve

- **QUESTION_START** (33): am, are, aren't, can, can't, could, couldn't, did, didn't, do, does, doesn't, don't, had, has, have, how, is, isn't, should, shouldn't, was, were, what, when, where, which, who, whose, why, will, would, wouldn't

- **IMPERATIVE_START** (43): ask, beware, buckle, call, check, do, don't, dont, forget, get, give, guess, hear, help, imagine, join, learn, leave, let's, lets, let’s, listen, look, make, meet, never, please, prepare, read, remember, run, say, see, stand, stop, subscribe, take, tell, think, try, vote, wake, watch

- **INTENSIFIERS** (37): 100%, absolutely, actually, brutally, completely, damn, deeply, entirely, extremely, finally, fully, genuinely, hella, hugely, incredibly, insanely, literally, massively, mega, obviously, officially, perfectly, purely, really, ridiculously, seriously, shockingly, so, super, totally, truly, ultra, unbelievably, utterly, very, way, wildly

- **SUPERLATIVES** (29): #1, all-time, best, biggest, craziest, deadliest, dumbest, ever, first-ever, funniest, greatest, hardest, highest, historic, largest, least, lowest, most, record, richest, scariest, smallest, strongest, top, ultimate, unprecedented, weakest, wildest, worst

- **SHOCK_WORDS** (66): alert, attack, backlash, banned, bizarre, bombshell, brutal, catastrophe, caught, chaos, collapse, crazy, crisis, danger, dangerous, deadly, destroy, destroyed, devastating, disaster, disgusting, emergency, epic, erupts, explodes, explosive, exposed, forbidden, furious, fury, hidden, horrifying, horror, huge, humiliated, insane, insanity, jaw-dropping, leaked, madness, massive, meltdown, mind-blowing, nightmare, nuke, nukes, outrageous, panic, rage, rampage, revenge, scandal, secret, shock, shocked, shocking, stunning, terrifying, unbelievable, unhinged, urgent, viral, war, warning, wild, wrecked

- **POS_EVAL** (29): amazing, awesome, based, beautiful, best, brave, brilliant, elite, epic, excellent, fantastic, genius, glorious, goated, good, great, heroic, hilarious, honest, iconic, incredible, inspiring, legendary, masterclass, masterpiece, perfect, powerful, smart, wonderful

- **NEG_EVAL** (65): absurd, awful, bad, clown, clueless, communist, corrupt, coward, cowardly, crazy, creepy, criminal, cringe, crooked, cult, dangerous, delusional, deranged, disgraceful, disgusting, dumb, embarrassing, evil, extremist, fake, fascist, fraud, garbage, grift, grifter, gross, horrible, humiliating, hypocrisy, hypocrite, idiot, idiotic, insane, liar, lies, loser, lying, moron, nazi, pathetic, psycho, racist, radical, ridiculous, scam, scum, shameful, shameless, sick, stupid, terrible, toxic, traitor, trash, treason, unhinged, vile, weak, woke, worst

- **NEGATION** (38): ain't, ain’t, aren't, aren’t, can't, cannot, can’t, couldn't, didn't, didn’t, doesn't, doesn’t, don't, don’t, failed, fails, isn't, isn’t, n't, nah, neither, never, no, nobody, none, nope, nor, not, nothing, refuses, shouldn't, stop, wasn't, wasn’t, without, won't, won’t, wouldn't

- **VIOLENCE_VERBS** (99): annihilated, annihilates, attacked, attacks, backfires, blast, blasted, blasting, blasts, bodied, bodies, busted, clowned, clowns, confronted, confronts, cooked, crushed, crushes, demolished, demolishes, destroy, destroyed, destroying, destroys, dismantled, dismantles, dragged, drags, dunks, erupted, erupts, eviscerated, eviscerates, exploded, explodes, expose, exposed, exposes, exposing, flamed, flames, flips, grilled, grills, hammered, hammers, humiliated, humiliates, mocked, mocks, nuked, nukes, obliterated, obliterates, owned, owns, panics, rages, ratioed, rip, ripped, ripping, rips, roasted, roasts, rocked, rocks, schooled, schools, scorches, shocked, shocks, shred, shredded, shreds, silenced, silences, slam, slammed, slamming, slams, smacked, smacks, snapped, snaps, stunned, stuns, threatened, threatens, torched, torches, torpedoes, trolled, trolls, unloads, wrecked, wrecking, wrecks

- **VIOLENCE_PHRASES** (34): blew up, blows up, breaks down, called out, calls out, flips out, freaked out, freaks out, gets busted, gets caught, gets destroyed, gets exposed, gets humiliated, gets owned, gets wrecked, goes after, goes nuclear, goes off, in shambles, lays into, loses it, lost it, melted down, melts down, puts on blast, shut down, shuts down, smacks down, takes down, tears into, took down, tore into, went after, went off

- **HEDGES** (40): alleged, allegedly, apparently, appear, appears, claim, claimed, claims, considers, could, expected, eyes, hints, likely, may, maybe, might, mulls, perhaps, possibly, potentially, predicts, probably, purported, reported, reportedly, rumored, rumoured, seem, seems, signals, so-called, sources, suggest, suggests, supposedly, unlikely, warns, weighs, would

- **DISCOURSE** (57): ahh, ahhh, based, bro, bruh, chat, cooked, cringe, damn, dang, dude, everyone, folks, fr, friends, gg, goated, guys, haha, hahaha, hello, hey, hi, hmm, holy, let's, lets, let’s, lmao, lmfao, lol, nah, ngl, nope, oh, ok, okay, omg, oof, pog, ratio, rip, sooo, soooo, sus, tbh, ugh, uh, um, welp, wow, wtf, y'all, yeah, yep, yikes, yo

- **HOWTO_PHRASES** (4): how i, how to, how we, how you

- **EXPLAINER_PHRASES** (32): 101, a guide to, analysis, breakdown, breaks down, broken down, deep dive, everything you need to know, explained, explainer, explaining, explains, guide to, here is why, here's why, here’s why, history of, the case against, the case for, the history of, the real reason, the real story, the reason, the truth about, understanding, what are, what happened, what is, what it means, what really happened, what you need to know, why it matters

- **CURIOSITY_PHRASES** (43): everything changed, exposed, goes wrong, guess what, here's how, here's what, here's why, here’s how, here’s what, here’s why, it has begun, it's over, it’s over, need to see this, no one is talking, nobody is talking, nobody talks, secret, shocking, the real reason, the truth about, the untold, they don't want you, they don’t want you, this changes everything, this is bad, this is crazy, this is disgusting, this is huge, this is insane, this is it, this is why, this is wild, wait till, wait until, watch what, went wrong, what happened next, what no one, what nobody, you need to see, you won't believe, you won’t believe

- **FORWARD_REF_START** (19): a, everyone, he, her, him, his, it, nobody, she, somebody, someone, something, that, the, their, them, these, they, this

- **REACTION_PHRASES** (16): live reaction, my reaction, my response, my thoughts on, react to, reacting, reacting to, reaction, reaction to, reacts, reacts to, responding to, responds, responds to, response to, watching

- **INTERVIEW_PHRASES** (18):  and ,  feat ,  feat. ,  ft ,  ft. ,  in conversation with ,  interviews ,  joins ,  on the ,  sits down with ,  speaks to ,  speaks with ,  talks to ,  talks with ,  w/ ,  with ,  x , interview

- **CONFRONTATION_PHRASES** (29):  versus ,  vs ,  vs. , argues with, battle, battles, clash, clashes, confronted, confronts, debate, debates, debating, destroys, dismantles, face off, faces off, fight, fights, goes head to head, grills, head-to-head, owns, schools, showdown, shuts down, spars with, takes down, takes on

- **LISTICLE_RE**: `^(?:top|the)?\s*\d{1,2}\s+(?:\w+\s+)?(?:things|reasons|ways|times|signs|facts|lessons|tips|moments|questions|mistakes|rules|takeaways|lies|truths|myths|predictions|biggest|best|worst|craziest|most)`


## Format rules

| format | regex | flags |
|---|---|---|
| question | \?\|^\W*(?:who\|what\|when\|where\|why\|how\|which\|whose\|is\|are\|was\|were\|do\|does\|did\|can\|could\|s... | case-insensitive |
| breaking_live | ^\W*(?:breaking\|just in\|developing\|live\|watch live\|livestream\|live stream\|replay\|live replay\|watch... | case-insensitive (LIVE label case-sensitive) |
| episode_show | \b(?:ep\|eps\|episode)\.?\s*#?\s*\d+\b\|#\d{2,5}\b\|\bs\d{1,2}\s*e\d{1,3}\b\|\bseason\s+\d+\b\|\bhour\s+\d\... | case-insensitive |
| interview_guest | \bwith\s+(?:[A-Z@][\w.'’-]+)\|\bw/\s*\S\|\bft\.?\s+\S\|\bfeat\.?\s+\S\|\bfeaturing\b\|\bjoins\b\|\bintervie... | case-insensitive |
| reaction | \breact(?:s\|ed\|ing\|ion\|ions)?\b\|\brespon(?:ds\|se\|ding)\b\|\bresponds?\b\|\bwatching\b\|\bfirst time ... | case-insensitive |
| confrontation | \bvs\.?\b\|\bversus\b\|\bdebat(?:e\|es\|ed\|ing)\b\|\b(?:destroys?\|destroyed\|owns?\|owned\|shreds?\|shred... | case-insensitive |
| listicle | ^\W*(?:top\s+\|the\s+)?\d{1,2}\s+(?:\w+\s+)?(?:things\|reasons\|ways\|times\|signs\|facts\|lessons\|tips\|m... | case-insensitive |
| howto_explainer | \bhow\s+to\b\|\bexplain(?:ed\|er\|s\|ing)?\b\|\bbreak(?:s\|ing)?\s+down\b\|\bbreakdown\b\|\bwhat\s+(?:is\|a... | case-insensitive |


## Factor analysis

Cells: 1999 (>= 15 unique titles); features: 74; KMO 0.721; Bartlett chi2 109530.7 p 0; parallel analysis 16, Kaiser 21, retained 12 (minres, oblimin); variance explained per factor [0.0523, 0.049, 0.0467, 0.0453, 0.0438, 0.0423, 0.0407, 0.036, 0.0345, 0.032, 0.0262, 0.0229]; cumulative 0.4716.


Dropped features: `lowercase_start_p100` (prevalence 0.45 per 100 titles < 0.5); `percent_p100` (prevalence 0.31 per 100 titles < 0.5); `hashtag_p100` (prevalence 0.35 per 100 titles < 0.5); `at_mention_p100` (prevalence 0.14 per 100 titles < 0.5); `how_to_p100` (prevalence 0.38 per 100 titles < 0.5); `listicle_p100` (prevalence 0.03 per 100 titles < 0.5); `n_tokens_mean` (|r| = 0.983 with n_chars_mean)


Scree (eigenvalues vs parallel-analysis 95th percentile):

| component | eigenvalue | parallel_95th |
|---|---|---|
| 1 | 8.373 | 1.429 |
| 2 | 6.062 | 1.384 |
| 3 | 5.180 | 1.363 |
| 4 | 4.382 | 1.340 |
| 5 | 3.539 | 1.326 |
| 6 | 3.097 | 1.312 |
| 7 | 2.739 | 1.298 |
| 8 | 2.071 | 1.283 |
| 9 | 1.869 | 1.267 |
| 10 | 1.761 | 1.257 |
| 11 | 1.662 | 1.245 |
| 12 | 1.451 | 1.233 |
| 13 | 1.441 | 1.223 |
| 14 | 1.315 | 1.209 |
| 15 | 1.282 | 1.201 |
| 16 | 1.233 | 1.189 |
| 17 | 1.174 | 1.178 |
| 18 | 1.132 | 1.169 |
| 19 | 1.095 | 1.161 |
| 20 | 1.072 | 1.148 |


Full loadings (oblimin; varimax beside):

| feature | F1 | F2 | F3 | F4 | F5 | F6 | F7 | F8 | F9 | F10 | F11 | F12 | communality | F1_varimax | F2_varimax | F3_varimax | F4_varimax | F5_varimax | F6_varimax | F7_varimax | F8_varimax | F9_varimax | F10_varimax | F11_varimax | F12_varimax |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| n_chars_mean | -0.19 | 0.25 | 0.16 | 0.01 | -0.05 | 0.30 | 0.07 | 0.09 | -0.21 | 0.22 | 0.55 | 0.09 | 0.64 | -0.37 | 0.25 | 0.23 | -0.02 | 0.36 | 0.47 | 0.06 | 0.19 | 0.31 | -0.28 | 0.21 | 0.22 |
| mean_word_len_mean | -0.14 | -0.33 | -0.00 | -0.18 | -0.17 | 0.10 | 0.37 | -0.23 | -0.19 | 0.03 | 0.13 | -0.13 | 0.47 | -0.53 | 0.04 | 0.00 | -0.22 | 0.00 | 0.14 | -0.17 | -0.21 | 0.07 | -0.17 | -0.30 | -0.00 |
| allcaps_word_share_mean | -0.13 | -0.02 | 0.06 | -0.02 | -0.08 | 0.06 | 0.02 | 0.01 | 0.95 | -0.00 | 0.02 | -0.01 | 0.93 | 0.01 | 0.44 | 0.15 | -0.25 | 0.00 | -0.11 | -0.02 | -0.02 | -0.07 | 0.84 | -0.07 | -0.03 |
| has_allcaps_word_p100 | -0.31 | 0.00 | 0.28 | 0.00 | -0.19 | 0.08 | -0.12 | 0.02 | 0.47 | 0.03 | 0.15 | -0.17 | 0.51 | -0.04 | 0.56 | 0.34 | -0.30 | -0.06 | 0.08 | -0.02 | 0.01 | 0.02 | 0.37 | -0.12 | 0.01 |
| full_caps_title_p100 | 0.04 | 0.04 | -0.03 | -0.02 | -0.01 | 0.07 | 0.07 | 0.01 | 0.84 | -0.01 | -0.08 | 0.04 | 0.73 | 0.08 | 0.20 | 0.06 | -0.15 | 0.06 | -0.13 | -0.02 | -0.03 | -0.09 | 0.77 | -0.02 | -0.04 |
| cap_token_share_mean | -0.21 | -0.18 | -0.02 | -0.18 | -0.02 | 0.07 | -0.71 | -0.01 | 0.18 | -0.04 | -0.02 | -0.03 | 0.65 | 0.17 | 0.44 | -0.03 | 0.01 | -0.62 | 0.16 | -0.20 | 0.02 | -0.06 | 0.07 | 0.18 | 0.02 |
| q_mark_p100 | -0.05 | 0.01 | -0.02 | -0.05 | 0.48 | 0.09 | -0.10 | 0.03 | 0.03 | 0.07 | 0.06 | 0.07 | 0.27 | 0.03 | 0.02 | -0.04 | 0.47 | -0.02 | 0.07 | -0.04 | 0.04 | 0.07 | -0.01 | 0.17 | 0.05 |
| excl_p100 | -0.24 | -0.04 | -0.07 | 0.06 | 0.02 | 0.04 | -0.12 | -0.06 | 0.23 | -0.07 | 0.31 | -0.16 | 0.27 | -0.03 | 0.47 | -0.02 | -0.02 | -0.07 | 0.07 | 0.03 | -0.05 | -0.05 | 0.13 | -0.06 | 0.18 |
| multi_punct_p100 | -0.18 | 0.00 | -0.01 | 0.09 | 0.05 | -0.02 | -0.08 | -0.02 | 0.22 | -0.15 | 0.19 | -0.08 | 0.16 | 0.03 | 0.33 | 0.02 | 0.01 | -0.03 | -0.03 | 0.07 | -0.02 | -0.14 | 0.15 | -0.03 | 0.09 |
| colon_p100 | 0.00 | -0.03 | 0.80 | -0.12 | -0.02 | -0.01 | -0.01 | -0.02 | -0.04 | 0.18 | 0.02 | 0.10 | 0.69 | -0.18 | -0.10 | 0.78 | -0.06 | 0.04 | 0.07 | -0.06 | 0.00 | 0.18 | -0.05 | 0.04 | -0.02 |
| pipe_p100 | -0.05 | 0.16 | 0.15 | -0.01 | 0.04 | 0.31 | 0.10 | 0.23 | -0.00 | 0.03 | -0.01 | 0.22 | 0.26 | -0.20 | -0.06 | 0.17 | 0.01 | 0.18 | 0.26 | 0.03 | 0.24 | 0.05 | 0.01 | 0.17 | -0.15 |
| ellipsis_p100 | -0.06 | 0.05 | -0.02 | 0.73 | -0.08 | 0.01 | -0.01 | 0.04 | -0.02 | 0.14 | -0.13 | -0.19 | 0.62 | 0.32 | 0.10 | -0.04 | -0.09 | 0.02 | -0.02 | 0.64 | 0.00 | 0.13 | -0.01 | -0.19 | -0.12 |
| trailing_ellipsis_p100 | -0.02 | 0.02 | -0.04 | 0.84 | -0.05 | -0.01 | 0.06 | 0.01 | -0.07 | -0.02 | -0.09 | -0.15 | 0.76 | 0.30 | 0.02 | -0.06 | -0.06 | 0.03 | -0.07 | 0.76 | -0.03 | -0.02 | -0.04 | -0.21 | -0.09 |
| quotes_p100 | -0.00 | -0.03 | -0.00 | -0.06 | -0.02 | 0.01 | 0.01 | 0.01 | 0.01 | 0.91 | -0.03 | -0.07 | 0.84 | -0.06 | 0.02 | -0.02 | 0.00 | 0.09 | 0.14 | -0.02 | 0.05 | 0.87 | -0.04 | 0.05 | 0.01 |
| brackets_p100 | 0.13 | 0.16 | -0.05 | -0.02 | -0.09 | 0.07 | -0.18 | 0.07 | -0.02 | -0.06 | 0.13 | 0.02 | 0.12 | 0.11 | -0.00 | -0.02 | -0.03 | 0.01 | 0.12 | -0.03 | 0.10 | -0.05 | -0.04 | 0.13 | 0.15 |
| dash_p100 | 0.03 | 0.05 | -0.07 | -0.05 | 0.07 | 0.08 | -0.18 | 0.22 | -0.00 | 0.10 | 0.03 | -0.01 | 0.11 | 0.07 | 0.02 | -0.06 | 0.10 | -0.08 | 0.12 | -0.06 | 0.23 | 0.09 | -0.03 | 0.09 | 0.05 |
| emoji_p100 | -0.18 | 0.09 | 0.07 | 0.13 | -0.02 | 0.06 | -0.01 | 0.09 | 0.03 | -0.00 | 0.06 | -0.20 | 0.12 | 0.08 | 0.24 | 0.07 | -0.04 | 0.04 | 0.07 | 0.06 | 0.07 | 0.01 | 0.01 | -0.14 | -0.03 |
| digit_p100 | 0.06 | 0.01 | -0.02 | -0.02 | 0.02 | -0.01 | 0.02 | 0.83 | 0.01 | 0.09 | 0.07 | 0.01 | 0.70 | -0.13 | -0.11 | 0.02 | -0.01 | 0.02 | 0.03 | -0.01 | 0.83 | 0.11 | 0.01 | -0.02 | 0.02 |
| dollar_p100 | -0.00 | 0.06 | -0.11 | -0.04 | -0.02 | -0.02 | -0.02 | 0.17 | -0.03 | 0.09 | 0.07 | 0.03 | 0.06 | -0.03 | 0.01 | -0.10 | 0.01 | 0.05 | 0.02 | -0.02 | 0.18 | 0.10 | -0.04 | 0.07 | 0.05 |
| comma_p100 | -0.01 | 0.09 | -0.07 | 0.02 | -0.12 | 0.12 | 0.00 | 0.26 | 0.01 | -0.00 | 0.37 | 0.23 | 0.30 | -0.28 | 0.09 | 0.01 | -0.10 | 0.16 | 0.19 | 0.10 | 0.32 | 0.05 | -0.04 | 0.23 | 0.18 |
| period_end_p100 | 0.12 | 0.16 | -0.02 | 0.08 | -0.11 | -0.03 | -0.16 | -0.02 | -0.06 | 0.02 | -0.04 | -0.07 | 0.09 | 0.26 | -0.03 | -0.02 | -0.04 | 0.00 | 0.01 | 0.04 | -0.01 | 0.01 | -0.05 | 0.03 | 0.05 |
| year_mention_p100 | 0.05 | 0.01 | 0.01 | -0.02 | -0.02 | -0.04 | -0.03 | 0.66 | -0.05 | -0.09 | 0.04 | -0.01 | 0.45 | -0.06 | -0.10 | 0.04 | -0.03 | -0.04 | -0.01 | -0.03 | 0.65 | -0.07 | -0.04 | -0.04 | 0.01 |
| first_sg_p100 | 0.05 | 0.10 | 0.02 | 0.07 | 0.08 | -0.06 | -0.14 | -0.00 | -0.01 | 0.12 | -0.08 | -0.13 | 0.08 | 0.28 | 0.00 | -0.00 | 0.11 | -0.02 | -0.05 | 0.03 | -0.02 | 0.09 | -0.01 | -0.02 | 0.02 |
| first_pl_p100 | -0.12 | -0.07 | -0.01 | 0.49 | -0.01 | -0.01 | 0.08 | 0.00 | -0.06 | 0.14 | 0.06 | 0.47 | 0.52 | -0.22 | -0.03 | -0.00 | -0.02 | 0.10 | -0.01 | 0.60 | 0.04 | 0.18 | -0.06 | 0.32 | -0.11 |
| second_person_p100 | 0.13 | 0.04 | 0.03 | -0.01 | 0.11 | -0.17 | -0.26 | 0.06 | -0.01 | 0.30 | 0.16 | 0.04 | 0.25 | 0.15 | -0.03 | 0.04 | 0.17 | -0.04 | -0.05 | 0.04 | 0.11 | 0.29 | -0.07 | 0.20 | 0.24 |
| contraction_p100 | 0.11 | 0.17 | -0.11 | 0.64 | 0.06 | -0.02 | -0.25 | -0.06 | -0.02 | 0.15 | 0.05 | 0.15 | 0.58 | 0.37 | -0.01 | -0.10 | 0.14 | 0.03 | 0.00 | 0.65 | -0.03 | 0.14 | -0.05 | 0.25 | 0.09 |
| imperative_p100 | -0.00 | -0.23 | 0.26 | 0.54 | -0.03 | -0.00 | 0.05 | -0.04 | 0.08 | -0.10 | 0.14 | 0.16 | 0.48 | -0.14 | -0.00 | 0.29 | -0.09 | -0.07 | -0.03 | 0.58 | -0.03 | -0.08 | 0.06 | -0.02 | 0.04 |
| q_word_start_p100 | -0.02 | -0.07 | -0.02 | -0.06 | 0.96 | 0.01 | 0.08 | 0.02 | -0.01 | -0.03 | -0.05 | 0.04 | 0.94 | 0.06 | -0.18 | -0.08 | 0.90 | 0.02 | -0.10 | -0.06 | -0.02 | -0.04 | -0.02 | 0.08 | -0.00 |
| wh_any_p100 | -0.01 | 0.08 | -0.04 | 0.02 | 0.84 | 0.06 | -0.07 | 0.03 | -0.08 | 0.01 | 0.08 | -0.04 | 0.74 | 0.18 | -0.07 | -0.09 | 0.84 | 0.05 | 0.02 | -0.00 | 0.01 | 0.00 | -0.11 | 0.12 | 0.11 |
| intensifier_p100 | -0.01 | 0.31 | -0.07 | 0.14 | 0.15 | 0.00 | -0.16 | -0.04 | 0.00 | 0.02 | -0.04 | -0.21 | 0.22 | 0.44 | 0.12 | -0.10 | 0.20 | 0.09 | -0.01 | 0.06 | -0.07 | 0.00 | -0.01 | -0.00 | 0.03 |
| superlative_p100 | 0.07 | 0.08 | -0.07 | -0.01 | 0.09 | -0.11 | -0.01 | 0.01 | -0.09 | 0.16 | 0.09 | -0.17 | 0.11 | 0.13 | -0.02 | -0.08 | 0.13 | 0.09 | -0.05 | -0.03 | 0.02 | 0.16 | -0.10 | -0.06 | 0.15 |
| shock_word_p100 | -0.75 | 0.01 | 0.08 | 0.00 | 0.04 | -0.05 | -0.07 | -0.02 | 0.10 | 0.05 | 0.14 | 0.08 | 0.61 | -0.21 | 0.70 | 0.05 | -0.04 | 0.01 | -0.01 | 0.03 | -0.03 | 0.11 | 0.03 | 0.12 | -0.21 |
| pos_eval_p100 | 0.28 | -0.00 | -0.08 | -0.03 | 0.01 | -0.04 | -0.12 | -0.06 | 0.05 | 0.09 | 0.33 | -0.12 | 0.24 | 0.06 | -0.03 | -0.02 | 0.06 | -0.00 | 0.06 | -0.02 | -0.01 | 0.07 | -0.01 | 0.01 | 0.42 |
| neg_eval_p100 | -0.27 | 0.14 | -0.16 | -0.01 | -0.05 | 0.02 | -0.17 | -0.10 | 0.03 | 0.01 | 0.14 | -0.29 | 0.26 | 0.18 | 0.45 | -0.17 | -0.03 | -0.02 | 0.08 | -0.09 | -0.10 | 0.02 | -0.02 | -0.09 | 0.06 |
| negation_p100 | 0.13 | 0.33 | -0.12 | 0.04 | 0.02 | -0.06 | -0.40 | -0.02 | -0.03 | 0.18 | 0.10 | 0.17 | 0.38 | 0.35 | 0.02 | -0.11 | 0.15 | 0.05 | 0.04 | 0.07 | 0.03 | 0.17 | -0.08 | 0.43 | 0.17 |
| violence_verb_p100 | -0.64 | 0.08 | -0.11 | 0.04 | -0.12 | 0.10 | -0.07 | -0.03 | 0.04 | -0.06 | 0.16 | -0.18 | 0.52 | -0.09 | 0.72 | -0.12 | -0.16 | 0.00 | 0.14 | -0.01 | -0.04 | -0.00 | -0.02 | -0.08 | -0.14 |
| hedge_p100 | -0.03 | 0.18 | -0.05 | -0.09 | 0.01 | 0.01 | 0.07 | 0.19 | -0.09 | 0.14 | 0.04 | 0.21 | 0.15 | -0.10 | -0.07 | -0.05 | 0.04 | 0.21 | 0.03 | -0.04 | 0.21 | 0.16 | -0.08 | 0.22 | -0.04 |
| discourse_marker_p100 | -0.01 | -0.17 | -0.06 | 0.82 | -0.00 | -0.03 | 0.04 | -0.07 | 0.06 | -0.08 | 0.08 | 0.14 | 0.74 | 0.04 | 0.03 | -0.05 | -0.03 | -0.05 | -0.08 | 0.83 | -0.07 | -0.07 | 0.04 | -0.01 | 0.01 |
| nominalisation_p100 | 0.06 | -0.03 | 0.14 | -0.12 | -0.04 | 0.06 | 0.23 | -0.04 | -0.25 | 0.07 | 0.42 | 0.00 | 0.35 | -0.39 | -0.07 | 0.19 | -0.02 | 0.23 | 0.19 | -0.06 | 0.03 | 0.13 | -0.26 | -0.02 | 0.28 |
| n_person_p100 | 0.08 | 0.03 | -0.04 | 0.01 | 0.03 | 0.97 | -0.05 | -0.05 | 0.06 | 0.04 | 0.03 | -0.00 | 0.96 | -0.24 | 0.04 | 0.01 | 0.03 | -0.09 | 0.90 | -0.05 | -0.00 | 0.04 | 0.02 | 0.04 | -0.07 |
| n_org_p100 | -0.16 | -0.00 | 0.10 | 0.05 | -0.20 | 0.20 | 0.06 | 0.19 | -0.09 | -0.02 | 0.40 | 0.16 | 0.35 | -0.44 | 0.19 | 0.17 | -0.20 | 0.12 | 0.30 | 0.11 | 0.25 | 0.05 | -0.13 | 0.11 | 0.12 |
| n_gpe_p100 | -0.19 | 0.04 | 0.09 | -0.05 | -0.03 | -0.01 | 0.42 | 0.06 | -0.12 | 0.20 | 0.07 | 0.38 | 0.43 | -0.48 | -0.09 | 0.10 | -0.07 | 0.39 | -0.01 | 0.07 | 0.08 | 0.25 | -0.08 | 0.19 | -0.17 |
| has_person_p100 | 0.08 | -0.01 | -0.01 | -0.03 | 0.03 | 0.96 | -0.04 | -0.07 | 0.04 | 0.02 | -0.01 | -0.02 | 0.93 | -0.25 | 0.02 | 0.03 | 0.02 | -0.12 | 0.88 | -0.09 | -0.02 | 0.02 | 0.01 | 0.01 | -0.09 |
| entity_first_p100 | -0.16 | -0.03 | -0.60 | -0.18 | -0.26 | 0.30 | -0.02 | 0.09 | -0.13 | -0.10 | -0.06 | 0.12 | 0.64 | -0.24 | 0.13 | -0.59 | -0.21 | -0.12 | 0.30 | -0.19 | 0.11 | -0.05 | -0.12 | 0.11 | -0.17 |
| explainer_p100 | -0.01 | 0.06 | -0.05 | 0.03 | 0.36 | 0.13 | -0.08 | 0.03 | -0.10 | 0.07 | 0.11 | -0.15 | 0.21 | 0.11 | 0.04 | -0.07 | 0.38 | 0.01 | 0.15 | -0.01 | 0.03 | 0.07 | -0.13 | -0.01 | 0.11 |
| why_marker_p100 | -0.10 | -0.04 | 0.01 | -0.04 | 0.78 | 0.06 | 0.05 | -0.01 | -0.02 | -0.03 | -0.06 | -0.01 | 0.64 | 0.06 | -0.07 | -0.05 | 0.73 | 0.00 | -0.04 | -0.06 | -0.05 | -0.03 | -0.03 | 0.04 | -0.05 |
| curiosity_lex_p100 | -0.39 | 0.14 | -0.02 | 0.08 | 0.25 | 0.04 | -0.18 | -0.00 | 0.03 | -0.01 | 0.14 | -0.19 | 0.34 | 0.16 | 0.47 | -0.04 | 0.24 | -0.00 | 0.07 | 0.02 | -0.01 | 0.01 | -0.04 | 0.00 | -0.00 |
| fwd_ref_start_p100 | 0.17 | 0.19 | -0.11 | 0.09 | -0.07 | -0.29 | -0.23 | -0.06 | 0.11 | -0.08 | -0.18 | -0.10 | 0.29 | 0.53 | -0.05 | -0.13 | -0.01 | -0.05 | -0.32 | 0.05 | -0.09 | -0.13 | 0.12 | 0.02 | 0.03 |
| reaction_lex_p100 | 0.07 | 0.05 | -0.03 | 0.00 | -0.03 | 0.13 | -0.04 | -0.01 | -0.02 | 0.08 | 0.05 | -0.15 | 0.06 | 0.06 | 0.03 | -0.02 | -0.01 | -0.00 | 0.15 | -0.04 | -0.00 | 0.08 | -0.03 | -0.07 | 0.08 |
| interview_lex_p100 | 0.13 | -0.12 | 0.01 | 0.13 | 0.20 | 0.34 | -0.01 | -0.07 | -0.09 | -0.06 | 0.15 | 0.07 | 0.25 | -0.16 | -0.12 | 0.03 | 0.20 | -0.08 | 0.33 | 0.14 | -0.03 | -0.04 | -0.11 | 0.05 | 0.12 |
| confrontation_lex_p100 | -0.00 | -0.01 | -0.08 | -0.02 | -0.02 | 0.17 | -0.05 | -0.01 | -0.03 | 0.09 | 0.08 | -0.14 | 0.08 | -0.02 | 0.09 | -0.07 | -0.01 | -0.05 | 0.21 | -0.05 | 0.01 | 0.10 | -0.05 | -0.06 | 0.07 |
| lead_colon_label_p100 | -0.01 | -0.01 | 0.84 | -0.07 | -0.08 | -0.04 | -0.04 | -0.04 | 0.06 | -0.03 | 0.03 | -0.03 | 0.73 | -0.05 | 0.00 | 0.84 | -0.14 | -0.00 | 0.01 | -0.05 | -0.04 | -0.04 | 0.05 | -0.08 | 0.00 |
| lead_breaking_p100 | -0.22 | -0.04 | 0.25 | -0.04 | -0.01 | -0.11 | -0.02 | -0.05 | 0.04 | -0.01 | 0.07 | -0.02 | 0.13 | -0.07 | 0.21 | 0.24 | -0.05 | -0.01 | -0.08 | -0.02 | -0.05 | 0.01 | 0.02 | -0.03 | -0.02 |
| lead_live_p100 | 0.13 | 0.02 | 0.82 | -0.04 | -0.10 | 0.05 | 0.05 | -0.02 | 0.01 | -0.09 | -0.05 | -0.03 | 0.72 | -0.04 | -0.18 | 0.82 | -0.15 | 0.04 | 0.05 | -0.03 | -0.03 | -0.11 | 0.03 | -0.13 | -0.03 |
| episode_raw_p100 | 0.05 | -0.17 | 0.01 | -0.00 | 0.01 | -0.01 | -0.09 | -0.02 | 0.06 | -0.01 | -0.11 | -0.03 | 0.06 | 0.03 | -0.04 | -0.01 | -0.00 | -0.21 | -0.03 | -0.01 | -0.03 | -0.03 | 0.06 | -0.06 | -0.03 |
| date_raw_p100 | 0.19 | -0.15 | 0.15 | -0.03 | -0.06 | -0.08 | -0.13 | 0.22 | 0.11 | -0.11 | 0.26 | -0.00 | 0.25 | -0.10 | -0.05 | 0.22 | -0.07 | -0.14 | -0.01 | -0.00 | 0.26 | -0.11 | 0.06 | -0.02 | 0.29 |
| quoted_speech_p100 | 0.00 | -0.04 | 0.03 | 0.10 | -0.01 | 0.02 | 0.00 | -0.00 | 0.02 | 0.93 | -0.01 | 0.05 | 0.88 | -0.09 | -0.01 | 0.02 | -0.00 | 0.11 | 0.14 | 0.16 | 0.05 | 0.90 | -0.03 | 0.14 | 0.00 |
| has_finite_verb_p100 | -0.07 | 0.91 | -0.02 | -0.09 | 0.08 | 0.01 | 0.09 | -0.06 | 0.01 | 0.02 | 0.01 | 0.03 | 0.87 | 0.46 | 0.10 | -0.03 | 0.16 | 0.73 | -0.03 | -0.12 | -0.09 | 0.03 | 0.04 | 0.29 | -0.07 |
| past_tense_p100 | -0.14 | 0.53 | -0.17 | 0.10 | -0.02 | -0.01 | -0.12 | 0.01 | 0.04 | 0.13 | 0.03 | -0.11 | 0.39 | 0.41 | 0.28 | -0.18 | 0.04 | 0.32 | 0.01 | 0.04 | -0.00 | 0.14 | 0.03 | 0.14 | -0.02 |
| present_tense_p100 | -0.07 | 0.73 | 0.07 | -0.12 | -0.01 | -0.00 | 0.25 | -0.06 | -0.05 | -0.03 | 0.09 | 0.03 | 0.64 | 0.21 | 0.05 | 0.08 | 0.04 | 0.72 | -0.03 | -0.13 | -0.08 | 0.00 | -0.01 | 0.17 | -0.04 |
| modal_p100 | 0.11 | 0.31 | -0.13 | -0.11 | 0.18 | -0.04 | -0.26 | -0.05 | -0.02 | 0.13 | -0.00 | 0.41 | 0.43 | 0.19 | -0.12 | -0.13 | 0.28 | 0.13 | -0.02 | -0.02 | -0.01 | 0.13 | -0.04 | 0.57 | 0.03 |
| future_will_p100 | 0.03 | 0.19 | -0.06 | -0.14 | 0.07 | -0.02 | -0.16 | -0.04 | 0.00 | 0.03 | -0.03 | 0.44 | 0.29 | 0.02 | -0.10 | -0.06 | 0.13 | 0.08 | -0.02 | -0.04 | -0.01 | 0.03 | -0.00 | 0.49 | -0.05 |
| det_share_mean | 0.32 | 0.08 | -0.07 | -0.00 | 0.26 | -0.26 | -0.32 | -0.12 | -0.18 | -0.08 | 0.06 | -0.03 | 0.41 | 0.42 | -0.24 | -0.10 | 0.38 | -0.12 | -0.19 | -0.01 | -0.10 | -0.10 | -0.18 | 0.15 | 0.29 |
| stopword_share_mean | 0.22 | 0.39 | 0.21 | 0.14 | 0.26 | -0.26 | -0.27 | -0.18 | -0.01 | -0.13 | -0.04 | -0.01 | 0.52 | 0.63 | -0.14 | 0.18 | 0.34 | 0.13 | -0.27 | 0.12 | -0.19 | -0.16 | -0.00 | 0.19 | 0.14 |
| propn_share_mean | -0.17 | -0.48 | 0.04 | -0.22 | -0.12 | 0.33 | -0.37 | -0.04 | -0.25 | -0.03 | -0.04 | 0.01 | 0.63 | -0.34 | 0.14 | 0.01 | -0.09 | -0.64 | 0.44 | -0.22 | 0.01 | -0.01 | -0.28 | 0.00 | -0.08 |
| noun_share_mean | 0.09 | 0.14 | 0.02 | -0.06 | -0.05 | -0.08 | 0.80 | -0.00 | 0.17 | -0.01 | 0.01 | 0.06 | 0.71 | -0.31 | -0.26 | 0.06 | -0.16 | 0.64 | -0.24 | -0.02 | -0.05 | -0.00 | 0.25 | -0.21 | -0.08 |
| verb_share_mean | 0.08 | 0.54 | -0.19 | 0.16 | -0.02 | -0.26 | -0.03 | -0.19 | 0.15 | -0.11 | -0.19 | 0.14 | 0.56 | 0.56 | -0.04 | -0.21 | 0.05 | 0.36 | -0.36 | 0.15 | -0.24 | -0.14 | 0.19 | 0.25 | -0.09 |
| adj_share_mean | 0.15 | 0.14 | -0.08 | -0.07 | -0.00 | -0.24 | 0.53 | -0.09 | 0.27 | 0.11 | 0.02 | -0.06 | 0.49 | -0.03 | -0.17 | -0.04 | -0.07 | 0.49 | -0.35 | -0.05 | -0.12 | 0.08 | 0.30 | -0.17 | 0.06 |
| adv_share_mean | -0.02 | 0.46 | 0.40 | 0.16 | -0.04 | 0.01 | -0.07 | 0.06 | 0.05 | -0.14 | -0.27 | -0.16 | 0.53 | 0.50 | 0.02 | 0.36 | -0.04 | 0.20 | -0.06 | 0.07 | -0.01 | -0.17 | 0.10 | -0.07 | -0.22 |
| num_share_mean | 0.03 | -0.03 | -0.07 | -0.01 | 0.03 | -0.13 | -0.04 | 0.95 | 0.04 | -0.02 | -0.07 | -0.04 | 0.94 | -0.01 | -0.12 | -0.05 | -0.01 | -0.10 | -0.12 | -0.03 | 0.92 | -0.02 | 0.05 | -0.09 | -0.05 |
| vader_neg_mean | -0.76 | -0.04 | -0.19 | -0.03 | -0.03 | -0.22 | -0.07 | -0.14 | 0.18 | -0.02 | 0.02 | -0.04 | 0.73 | -0.06 | 0.76 | -0.23 | -0.10 | -0.06 | -0.21 | -0.04 | -0.17 | 0.02 | 0.12 | 0.01 | -0.24 |
| vader_pos_mean | 0.45 | -0.10 | -0.13 | -0.09 | 0.03 | -0.16 | -0.06 | -0.06 | 0.09 | 0.00 | 0.53 | -0.10 | 0.57 | -0.03 | -0.14 | -0.03 | 0.09 | 0.01 | -0.04 | -0.05 | 0.02 | -0.01 | 0.01 | -0.01 | 0.65 |
| vader_compound_mean | 0.91 | -0.05 | 0.05 | -0.01 | 0.01 | 0.04 | 0.03 | 0.05 | -0.04 | -0.05 | 0.13 | -0.04 | 0.87 | 0.13 | -0.76 | 0.12 | 0.09 | 0.00 | 0.05 | 0.00 | 0.10 | -0.10 | -0.01 | -0.06 | 0.48 |
| formulaic_p100 | 0.01 | -0.18 | 0.47 | 0.16 | -0.04 | 0.21 | 0.09 | 0.22 | 0.07 | -0.14 | 0.13 | 0.20 | 0.46 | -0.37 | -0.07 | 0.52 | -0.13 | -0.04 | 0.20 | 0.21 | 0.24 | -0.12 | 0.06 | -0.00 | -0.01 |


## Validation

| candidate | llm_column | best_factor | factor_auto_name | creator_level_r | second_factor | second_r | verdict | merged_with |
|---|---|---|---|---|---|---|---|---|
| Sensational | sensational | F1 | +vader_compound -vader_neg -shock_word -violence_verb | -0.709 | F5 | -0.322 | merged: Sensational, Critical, Analytical/Informational | Sensational, Critical, Analytical/Informational |
| Critical | critical | F1 | +vader_compound -vader_neg -shock_word -violence_verb | -0.494 | F5 | -0.167 | merged: Sensational, Critical, Analytical/Informational | Sensational, Critical, Analytical/Informational |
| Analytical/Informational | analytical | F1 | +vader_compound -vader_neg -shock_word -violence_verb | 0.422 | F5 | 0.419 | merged: Sensational, Critical, Analytical/Informational | Sensational, Critical, Analytical/Informational |
| Educational | educational | F5 | +q_word_start +wh_any +why_marker +q_mark | 0.384 | F1 | 0.312 | partial |  |
| Conversational | conversational | F4 | +trailing_ellipsis +discourse_marker +ellipsis +contraction | 0.174 | F1 | 0.166 | absent |  |
| Humor | humor | F2 | +has_finite_verb +present_tense +verb_share +past_tense | 0.077 | F4 | 0.067 | absent |  |

| dimension | n | exact_agreement | within_1 | spearman_r | weighted_kappa | kappa |
|---|---|---|---|---|---|---|
| sensational | 289 | 0.616 | 0.782 | 0.740 | 0.737 |  |
| critical | 289 | 0.709 | 0.751 | 0.582 | 0.585 |  |
| analytical | 289 | 0.581 | 0.768 | 0.598 | 0.552 |  |
| educational | 289 | 0.824 | 0.952 | 0.251 | 0.236 |  |
| conversational | 289 | 0.900 | 0.945 | 0.496 | 0.632 |  |
| humor | 289 | 0.993 |  |  |  | 0.000 |
| curiosity_gap | 289 | 0.979 |  |  |  | 0.390 |
| outrage | 289 | 0.754 |  |  |  | 0.492 |
| format_llm | 289 | 0.796 |  |  |  | 0.590 |

| llm | factor | factor_auto_name | score | spearman_r | pearson_r | p | n_groups |
|---|---|---|---|---|---|---|---|
| sensational | F1 | +vader_compound -vader_neg -shock_word -violence_verb | raw | -0.709 | -0.720 | 0.000 | 318 |
| sensational | F1 | +vader_compound -vader_neg -shock_word -violence_verb | controlled | -0.634 | -0.650 | 0.000 | 318 |
| sensational | F2 | +has_finite_verb +present_tense +verb_share +past_tense | raw | 0.099 | 0.143 | 0.078 | 318 |
| sensational | F2 | +has_finite_verb +present_tense +verb_share +past_tense | controlled | 0.068 | 0.091 | 0.225 | 318 |
| sensational | F3 | +lead_colon_label +lead_live +colon -entity_first | raw | -0.146 | -0.078 | 0.009 | 318 |
| sensational | F3 | +lead_colon_label +lead_live +colon -entity_first | controlled | -0.042 | -0.009 | 0.454 | 318 |
| sensational | F4 | +trailing_ellipsis +discourse_marker +ellipsis +contraction | raw | 0.167 | 0.059 | 0.003 | 318 |
| sensational | F4 | +trailing_ellipsis +discourse_marker +ellipsis +contraction | controlled | 0.027 | 0.017 | 0.636 | 318 |
| sensational | F5 | +q_word_start +wh_any +why_marker +q_mark | raw | -0.322 | -0.334 | 0.000 | 318 |
| sensational | F5 | +q_word_start +wh_any +why_marker +q_mark | controlled | -0.317 | -0.316 | 0.000 | 318 |
| sensational | F6 | +n_person +has_person | raw | 0.099 | 0.127 | 0.077 | 318 |
| sensational | F6 | +n_person +has_person | controlled | 0.101 | 0.133 | 0.071 | 318 |
| sensational | F7 | +noun_share -cap_token_share +adj_share +n_gpe | raw | -0.030 | -0.179 | 0.597 | 318 |
| sensational | F7 | +noun_share -cap_token_share +adj_share +n_gpe | controlled | -0.067 | -0.155 | 0.230 | 318 |
| sensational | F8 | +num_share +digit +year_mention | raw | -0.183 | -0.150 | 0.001 | 318 |
| sensational | F8 | +num_share +digit +year_mention | controlled | -0.043 | -0.074 | 0.449 | 318 |
| sensational | F9 | +allcaps_word_share +full_caps_title +has_allcaps_word | raw | 0.300 | 0.438 | 0.000 | 318 |
| sensational | F9 | +allcaps_word_share +full_caps_title +has_allcaps_word | controlled | 0.234 | 0.393 | 0.000 | 318 |
| sensational | F10 | +quoted_speech +quotes | raw | -0.050 | 0.009 | 0.378 | 318 |
| sensational | F10 | +quoted_speech +quotes | controlled | -0.036 | 0.020 | 0.520 | 318 |
| sensational | F11 | +n_chars +vader_pos +nominalisation +n_org | raw | 0.021 | 0.062 | 0.704 | 318 |
| sensational | F11 | +n_chars +vader_pos +nominalisation +n_org | controlled | 0.112 | 0.137 | 0.047 | 318 |
| sensational | F12 | +first_pl +future_will +modal | raw | -0.217 | -0.156 | 0.000 | 318 |
| sensational | F12 | +first_pl +future_will +modal | controlled | -0.257 | -0.227 | 0.000 | 318 |
| critical | F1 | +vader_compound -vader_neg -shock_word -violence_verb | raw | -0.494 | -0.508 | 0.000 | 318 |
| critical | F1 | +vader_compound -vader_neg -shock_word -violence_verb | controlled | -0.385 | -0.417 | 0.000 | 318 |
| critical | F2 | +has_finite_verb +present_tense +verb_share +past_tense | raw | 0.067 | 0.097 | 0.231 | 318 |
| critical | F2 | +has_finite_verb +present_tense +verb_share +past_tense | controlled | 0.048 | 0.068 | 0.390 | 318 |
| critical | F3 | +lead_colon_label +lead_live +colon -entity_first | raw | -0.166 | -0.174 | 0.003 | 318 |
| critical | F3 | +lead_colon_label +lead_live +colon -entity_first | controlled | -0.068 | -0.117 | 0.226 | 318 |
| critical | F4 | +trailing_ellipsis +discourse_marker +ellipsis +contraction | raw | 0.052 | -0.022 | 0.358 | 318 |
| critical | F4 | +trailing_ellipsis +discourse_marker +ellipsis +contraction | controlled | -0.043 | -0.046 | 0.442 | 318 |
| critical | F5 | +q_word_start +wh_any +why_marker +q_mark | raw | -0.167 | -0.195 | 0.003 | 318 |
| critical | F5 | +q_word_start +wh_any +why_marker +q_mark | controlled | -0.174 | -0.186 | 0.002 | 318 |
| critical | F6 | +n_person +has_person | raw | 0.102 | 0.153 | 0.068 | 318 |
| critical | F6 | +n_person +has_person | controlled | 0.121 | 0.173 | 0.031 | 318 |
| critical | F7 | +noun_share -cap_token_share +adj_share +n_gpe | raw | -0.072 | -0.141 | 0.201 | 318 |
| critical | F7 | +noun_share -cap_token_share +adj_share +n_gpe | controlled | -0.095 | -0.120 | 0.091 | 318 |
| critical | F8 | +num_share +digit +year_mention | raw | -0.146 | -0.120 | 0.009 | 318 |
| critical | F8 | +num_share +digit +year_mention | controlled | -0.021 | -0.027 | 0.704 | 318 |
| critical | F9 | +allcaps_word_share +full_caps_title +has_allcaps_word | raw | 0.045 | 0.105 | 0.419 | 318 |
| critical | F9 | +allcaps_word_share +full_caps_title +has_allcaps_word | controlled | -0.014 | 0.073 | 0.807 | 318 |
| critical | F10 | +quoted_speech +quotes | raw | 0.047 | 0.077 | 0.401 | 318 |
| critical | F10 | +quoted_speech +quotes | controlled | 0.013 | 0.071 | 0.818 | 318 |
| critical | F11 | +n_chars +vader_pos +nominalisation +n_org | raw | 0.038 | 0.075 | 0.499 | 318 |
| critical | F11 | +n_chars +vader_pos +nominalisation +n_org | controlled | 0.079 | 0.103 | 0.158 | 318 |
| critical | F12 | +first_pl +future_will +modal | raw | -0.150 | -0.084 | 0.007 | 318 |
| critical | F12 | +first_pl +future_will +modal | controlled | -0.168 | -0.119 | 0.003 | 318 |
| analytical | F1 | +vader_compound -vader_neg -shock_word -violence_verb | raw | 0.422 | 0.431 | 0.000 | 318 |
| analytical | F1 | +vader_compound -vader_neg -shock_word -violence_verb | controlled | 0.435 | 0.421 | 0.000 | 318 |
| analytical | F2 | +has_finite_verb +present_tense +verb_share +past_tense | raw | 0.017 | 0.001 | 0.761 | 318 |
| analytical | F2 | +has_finite_verb +present_tense +verb_share +past_tense | controlled | 0.031 | 0.022 | 0.583 | 318 |
| analytical | F3 | +lead_colon_label +lead_live +colon -entity_first | raw | 0.199 | 0.105 | 0.000 | 318 |
| analytical | F3 | +lead_colon_label +lead_live +colon -entity_first | controlled | 0.042 | 0.036 | 0.452 | 318 |
| analytical | F4 | +trailing_ellipsis +discourse_marker +ellipsis +contraction | raw | -0.165 | -0.052 | 0.003 | 318 |
| analytical | F4 | +trailing_ellipsis +discourse_marker +ellipsis +contraction | controlled | -0.047 | -0.005 | 0.402 | 318 |
| analytical | F5 | +q_word_start +wh_any +why_marker +q_mark | raw | 0.419 | 0.423 | 0.000 | 318 |
| analytical | F5 | +q_word_start +wh_any +why_marker +q_mark | controlled | 0.415 | 0.423 | 0.000 | 318 |
| analytical | F6 | +n_person +has_person | raw | -0.011 | -0.048 | 0.843 | 318 |
| analytical | F6 | +n_person +has_person | controlled | 0.005 | -0.025 | 0.933 | 318 |
| analytical | F7 | +noun_share -cap_token_share +adj_share +n_gpe | raw | -0.021 | 0.123 | 0.704 | 318 |
| analytical | F7 | +noun_share -cap_token_share +adj_share +n_gpe | controlled | -0.111 | 0.023 | 0.048 | 318 |
| analytical | F8 | +num_share +digit +year_mention | raw | 0.159 | 0.013 | 0.004 | 318 |
| analytical | F8 | +num_share +digit +year_mention | controlled | 0.031 | -0.040 | 0.583 | 318 |
| analytical | F9 | +allcaps_word_share +full_caps_title +has_allcaps_word | raw | -0.269 | -0.316 | 0.000 | 318 |
| analytical | F9 | +allcaps_word_share +full_caps_title +has_allcaps_word | controlled | -0.179 | -0.261 | 0.001 | 318 |
| analytical | F10 | +quoted_speech +quotes | raw | 0.245 | 0.154 | 0.000 | 318 |
| analytical | F10 | +quoted_speech +quotes | controlled | 0.114 | 0.081 | 0.043 | 318 |
| analytical | F11 | +n_chars +vader_pos +nominalisation +n_org | raw | 0.137 | 0.157 | 0.015 | 318 |
| analytical | F11 | +n_chars +vader_pos +nominalisation +n_org | controlled | 0.030 | 0.057 | 0.591 | 318 |
| analytical | F12 | +first_pl +future_will +modal | raw | 0.347 | 0.284 | 0.000 | 318 |
| analytical | F12 | +first_pl +future_will +modal | controlled | 0.269 | 0.232 | 0.000 | 318 |
| educational | F1 | +vader_compound -vader_neg -shock_word -violence_verb | raw | 0.312 | 0.342 | 0.000 | 318 |
| educational | F1 | +vader_compound -vader_neg -shock_word -violence_verb | controlled | 0.336 | 0.322 | 0.000 | 318 |
| educational | F2 | +has_finite_verb +present_tense +verb_share +past_tense | raw | 0.025 | -0.010 | 0.651 | 318 |
| educational | F2 | +has_finite_verb +present_tense +verb_share +past_tense | controlled | 0.026 | 0.007 | 0.640 | 318 |
| educational | F3 | +lead_colon_label +lead_live +colon -entity_first | raw | 0.012 | -0.028 | 0.835 | 318 |
| educational | F3 | +lead_colon_label +lead_live +colon -entity_first | controlled | -0.026 | -0.046 | 0.637 | 318 |
| educational | F4 | +trailing_ellipsis +discourse_marker +ellipsis +contraction | raw | -0.019 | 0.056 | 0.729 | 318 |
| educational | F4 | +trailing_ellipsis +discourse_marker +ellipsis +contraction | controlled | 0.042 | 0.083 | 0.459 | 318 |
| educational | F5 | +q_word_start +wh_any +why_marker +q_mark | raw | 0.384 | 0.413 | 0.000 | 318 |
| educational | F5 | +q_word_start +wh_any +why_marker +q_mark | controlled | 0.362 | 0.397 | 0.000 | 318 |
| educational | F6 | +n_person +has_person | raw | -0.140 | -0.131 | 0.013 | 318 |
| educational | F6 | +n_person +has_person | controlled | -0.107 | -0.097 | 0.056 | 318 |
| educational | F7 | +noun_share -cap_token_share +adj_share +n_gpe | raw | -0.062 | 0.048 | 0.271 | 318 |
| educational | F7 | +noun_share -cap_token_share +adj_share +n_gpe | controlled | -0.118 | 0.013 | 0.035 | 318 |
| educational | F8 | +num_share +digit +year_mention | raw | 0.035 | 0.030 | 0.539 | 318 |
| educational | F8 | +num_share +digit +year_mention | controlled | -0.040 | 0.004 | 0.476 | 318 |
| educational | F9 | +allcaps_word_share +full_caps_title +has_allcaps_word | raw | -0.071 | -0.126 | 0.206 | 318 |
| educational | F9 | +allcaps_word_share +full_caps_title +has_allcaps_word | controlled | -0.047 | -0.102 | 0.400 | 318 |
| educational | F10 | +quoted_speech +quotes | raw | 0.158 | 0.069 | 0.005 | 318 |
| educational | F10 | +quoted_speech +quotes | controlled | 0.082 | 0.044 | 0.145 | 318 |
| educational | F11 | +n_chars +vader_pos +nominalisation +n_org | raw | 0.058 | 0.088 | 0.307 | 318 |
| educational | F11 | +n_chars +vader_pos +nominalisation +n_org | controlled | -0.004 | 0.026 | 0.950 | 318 |
| educational | F12 | +first_pl +future_will +modal | raw | 0.138 | 0.115 | 0.014 | 318 |
| educational | F12 | +first_pl +future_will +modal | controlled | 0.102 | 0.091 | 0.069 | 318 |
| conversational | F1 | +vader_compound -vader_neg -shock_word -violence_verb | raw | 0.166 | 0.180 | 0.003 | 318 |
| conversational | F1 | +vader_compound -vader_neg -shock_word -violence_verb | controlled | 0.140 | 0.174 | 0.012 | 318 |
| conversational | F2 | +has_finite_verb +present_tense +verb_share +past_tense | raw | 0.052 | 0.016 | 0.352 | 318 |
| conversational | F2 | +has_finite_verb +present_tense +verb_share +past_tense | controlled | 0.030 | -0.009 | 0.597 | 318 |
| conversational | F3 | +lead_colon_label +lead_live +colon -entity_first | raw | -0.094 | -0.079 | 0.095 | 318 |
| conversational | F3 | +lead_colon_label +lead_live +colon -entity_first | controlled | -0.002 | -0.050 | 0.970 | 318 |
| conversational | F4 | +trailing_ellipsis +discourse_marker +ellipsis +contraction | raw | 0.174 | 0.620 | 0.002 | 318 |
| conversational | F4 | +trailing_ellipsis +discourse_marker +ellipsis +contraction | controlled | 0.161 | 0.592 | 0.004 | 318 |
| conversational | F5 | +q_word_start +wh_any +why_marker +q_mark | raw | 0.102 | 0.029 | 0.070 | 318 |
| conversational | F5 | +q_word_start +wh_any +why_marker +q_mark | controlled | 0.069 | 0.005 | 0.220 | 318 |
| conversational | F6 | +n_person +has_person | raw | -0.135 | -0.158 | 0.016 | 318 |
| conversational | F6 | +n_person +has_person | controlled | -0.127 | -0.124 | 0.024 | 318 |
| conversational | F7 | +noun_share -cap_token_share +adj_share +n_gpe | raw | -0.005 | 0.002 | 0.932 | 318 |
| conversational | F7 | +noun_share -cap_token_share +adj_share +n_gpe | controlled | 0.056 | 0.048 | 0.319 | 318 |
| conversational | F8 | +num_share +digit +year_mention | raw | -0.071 | 0.022 | 0.209 | 318 |
| conversational | F8 | +num_share +digit +year_mention | controlled | -0.018 | 0.018 | 0.747 | 318 |
| conversational | F9 | +allcaps_word_share +full_caps_title +has_allcaps_word | raw | 0.001 | -0.015 | 0.984 | 318 |
| conversational | F9 | +allcaps_word_share +full_caps_title +has_allcaps_word | controlled | -0.020 | -0.020 | 0.719 | 318 |
| conversational | F10 | +quoted_speech +quotes | raw | -0.028 | -0.036 | 0.624 | 318 |
| conversational | F10 | +quoted_speech +quotes | controlled | 0.003 | -0.008 | 0.952 | 318 |
| conversational | F11 | +n_chars +vader_pos +nominalisation +n_org | raw | -0.020 | 0.031 | 0.721 | 318 |
| conversational | F11 | +n_chars +vader_pos +nominalisation +n_org | controlled | -0.003 | 0.081 | 0.960 | 318 |
| conversational | F12 | +first_pl +future_will +modal | raw | -0.078 | 0.057 | 0.165 | 318 |
| conversational | F12 | +first_pl +future_will +modal | controlled | -0.032 | 0.102 | 0.572 | 318 |
| humor | F1 | +vader_compound -vader_neg -shock_word -violence_verb | raw | -0.020 | 0.006 | 0.724 | 318 |
| humor | F1 | +vader_compound -vader_neg -shock_word -violence_verb | controlled | -0.018 | 0.002 | 0.744 | 318 |
| humor | F2 | +has_finite_verb +present_tense +verb_share +past_tense | raw | 0.077 | 0.058 | 0.171 | 318 |
| humor | F2 | +has_finite_verb +present_tense +verb_share +past_tense | controlled | 0.060 | 0.052 | 0.288 | 318 |
| humor | F3 | +lead_colon_label +lead_live +colon -entity_first | raw | -0.055 | -0.041 | 0.325 | 318 |
| humor | F3 | +lead_colon_label +lead_live +colon -entity_first | controlled | -0.023 | -0.038 | 0.679 | 318 |
| humor | F4 | +trailing_ellipsis +discourse_marker +ellipsis +contraction | raw | 0.067 | 0.019 | 0.234 | 318 |
| humor | F4 | +trailing_ellipsis +discourse_marker +ellipsis +contraction | controlled | 0.032 | 0.021 | 0.568 | 318 |
| humor | F5 | +q_word_start +wh_any +why_marker +q_mark | raw | -0.039 | -0.008 | 0.493 | 318 |
| humor | F5 | +q_word_start +wh_any +why_marker +q_mark | controlled | -0.057 | -0.011 | 0.311 | 318 |
| humor | F6 | +n_person +has_person | raw | -0.021 | -0.024 | 0.709 | 318 |
| humor | F6 | +n_person +has_person | controlled | -0.014 | -0.028 | 0.798 | 318 |
| humor | F7 | +noun_share -cap_token_share +adj_share +n_gpe | raw | 0.060 | 0.077 | 0.289 | 318 |
| humor | F7 | +noun_share -cap_token_share +adj_share +n_gpe | controlled | 0.079 | 0.092 | 0.161 | 318 |
| humor | F8 | +num_share +digit +year_mention | raw | -0.026 | -0.015 | 0.646 | 318 |
| humor | F8 | +num_share +digit +year_mention | controlled | 0.002 | -0.001 | 0.975 | 318 |
| humor | F9 | +allcaps_word_share +full_caps_title +has_allcaps_word | raw | -0.018 | -0.018 | 0.749 | 318 |
| humor | F9 | +allcaps_word_share +full_caps_title +has_allcaps_word | controlled | -0.033 | -0.017 | 0.562 | 318 |
| humor | F10 | +quoted_speech +quotes | raw | 0.019 | 0.039 | 0.738 | 318 |
| humor | F10 | +quoted_speech +quotes | controlled | 0.020 | 0.040 | 0.719 | 318 |
| humor | F11 | +n_chars +vader_pos +nominalisation +n_org | raw | -0.015 | -0.002 | 0.787 | 318 |
| humor | F11 | +n_chars +vader_pos +nominalisation +n_org | controlled | 0.011 | 0.006 | 0.850 | 318 |
| humor | F12 | +first_pl +future_will +modal | raw | -0.055 | -0.038 | 0.328 | 318 |
| humor | F12 | +first_pl +future_will +modal | controlled | -0.007 | -0.008 | 0.902 | 318 |
| curiosity_gap | F1 | +vader_compound -vader_neg -shock_word -violence_verb | raw | -0.026 | -0.006 | 0.643 | 318 |
| curiosity_gap | F1 | +vader_compound -vader_neg -shock_word -violence_verb | controlled | -0.014 | 0.020 | 0.806 | 318 |
| curiosity_gap | F2 | +has_finite_verb +present_tense +verb_share +past_tense | raw | 0.104 | 0.082 | 0.064 | 318 |
| curiosity_gap | F2 | +has_finite_verb +present_tense +verb_share +past_tense | controlled | 0.062 | 0.039 | 0.268 | 318 |
| curiosity_gap | F3 | +lead_colon_label +lead_live +colon -entity_first | raw | -0.077 | -0.094 | 0.169 | 318 |
| curiosity_gap | F3 | +lead_colon_label +lead_live +colon -entity_first | controlled | -0.043 | -0.078 | 0.450 | 318 |
| curiosity_gap | F4 | +trailing_ellipsis +discourse_marker +ellipsis +contraction | raw | 0.173 | 0.124 | 0.002 | 318 |
| curiosity_gap | F4 | +trailing_ellipsis +discourse_marker +ellipsis +contraction | controlled | 0.146 | 0.113 | 0.009 | 318 |
| curiosity_gap | F5 | +q_word_start +wh_any +why_marker +q_mark | raw | 0.138 | 0.036 | 0.014 | 318 |
| curiosity_gap | F5 | +q_word_start +wh_any +why_marker +q_mark | controlled | 0.131 | 0.026 | 0.020 | 318 |
| curiosity_gap | F6 | +n_person +has_person | raw | -0.148 | -0.132 | 0.008 | 318 |
| curiosity_gap | F6 | +n_person +has_person | controlled | -0.164 | -0.144 | 0.003 | 318 |
| curiosity_gap | F7 | +noun_share -cap_token_share +adj_share +n_gpe | raw | -0.152 | -0.124 | 0.007 | 318 |
| curiosity_gap | F7 | +noun_share -cap_token_share +adj_share +n_gpe | controlled | -0.092 | -0.106 | 0.100 | 318 |
| curiosity_gap | F8 | +num_share +digit +year_mention | raw | -0.138 | -0.079 | 0.014 | 318 |
| curiosity_gap | F8 | +num_share +digit +year_mention | controlled | -0.082 | -0.072 | 0.147 | 318 |
| curiosity_gap | F9 | +allcaps_word_share +full_caps_title +has_allcaps_word | raw | 0.173 | 0.045 | 0.002 | 318 |
| curiosity_gap | F9 | +allcaps_word_share +full_caps_title +has_allcaps_word | controlled | 0.134 | 0.018 | 0.017 | 318 |
| curiosity_gap | F10 | +quoted_speech +quotes | raw | -0.063 | -0.054 | 0.260 | 318 |
| curiosity_gap | F10 | +quoted_speech +quotes | controlled | -0.058 | -0.059 | 0.303 | 318 |
| curiosity_gap | F11 | +n_chars +vader_pos +nominalisation +n_org | raw | -0.143 | -0.125 | 0.011 | 318 |
| curiosity_gap | F11 | +n_chars +vader_pos +nominalisation +n_org | controlled | -0.086 | -0.082 | 0.128 | 318 |
| curiosity_gap | F12 | +first_pl +future_will +modal | raw | -0.132 | -0.135 | 0.019 | 318 |
| curiosity_gap | F12 | +first_pl +future_will +modal | controlled | -0.147 | -0.152 | 0.009 | 318 |
| outrage | F1 | +vader_compound -vader_neg -shock_word -violence_verb | raw | -0.608 | -0.601 | 0.000 | 318 |
| outrage | F1 | +vader_compound -vader_neg -shock_word -violence_verb | controlled | -0.513 | -0.511 | 0.000 | 318 |
| outrage | F2 | +has_finite_verb +present_tense +verb_share +past_tense | raw | 0.097 | 0.141 | 0.085 | 318 |
| outrage | F2 | +has_finite_verb +present_tense +verb_share +past_tense | controlled | 0.058 | 0.084 | 0.303 | 318 |
| outrage | F3 | +lead_colon_label +lead_live +colon -entity_first | raw | -0.182 | -0.152 | 0.001 | 318 |
| outrage | F3 | +lead_colon_label +lead_live +colon -entity_first | controlled | -0.090 | -0.091 | 0.110 | 318 |
| outrage | F4 | +trailing_ellipsis +discourse_marker +ellipsis +contraction | raw | 0.098 | -0.011 | 0.080 | 318 |
| outrage | F4 | +trailing_ellipsis +discourse_marker +ellipsis +contraction | controlled | -0.032 | -0.051 | 0.575 | 318 |
| outrage | F5 | +q_word_start +wh_any +why_marker +q_mark | raw | -0.243 | -0.241 | 0.000 | 318 |
| outrage | F5 | +q_word_start +wh_any +why_marker +q_mark | controlled | -0.241 | -0.238 | 0.000 | 318 |
| outrage | F6 | +n_person +has_person | raw | -0.002 | 0.012 | 0.978 | 318 |
| outrage | F6 | +n_person +has_person | controlled | 0.006 | 0.024 | 0.912 | 318 |
| outrage | F7 | +noun_share -cap_token_share +adj_share +n_gpe | raw | -0.067 | -0.199 | 0.231 | 318 |
| outrage | F7 | +noun_share -cap_token_share +adj_share +n_gpe | controlled | -0.093 | -0.187 | 0.098 | 318 |
| outrage | F8 | +num_share +digit +year_mention | raw | -0.224 | -0.187 | 0.000 | 318 |
| outrage | F8 | +num_share +digit +year_mention | controlled | -0.101 | -0.131 | 0.074 | 318 |
| outrage | F9 | +allcaps_word_share +full_caps_title +has_allcaps_word | raw | 0.209 | 0.280 | 0.000 | 318 |
| outrage | F9 | +allcaps_word_share +full_caps_title +has_allcaps_word | controlled | 0.177 | 0.247 | 0.002 | 318 |
| outrage | F10 | +quoted_speech +quotes | raw | -0.069 | -0.003 | 0.223 | 318 |
| outrage | F10 | +quoted_speech +quotes | controlled | -0.087 | -0.016 | 0.122 | 318 |
| outrage | F11 | +n_chars +vader_pos +nominalisation +n_org | raw | -0.005 | 0.016 | 0.926 | 318 |
| outrage | F11 | +n_chars +vader_pos +nominalisation +n_org | controlled | 0.066 | 0.072 | 0.238 | 318 |
| outrage | F12 | +first_pl +future_will +modal | raw | -0.168 | -0.111 | 0.003 | 318 |
| outrage | F12 | +first_pl +future_will +modal | controlled | -0.201 | -0.160 | 0.000 | 318 |


## Hook classifier

```
{
  "features": "768-d sentence embedding + ['allcaps_word_share', 'excl', 'q_mark', 'trailing_ellipsis', 'violence_verb', 'shock_word', 'curiosity_lex', 'fwd_ref_start', 'discourse_marker', 'has_person', 'neg_eval', 'pos_eval']",
  "model": "StandardScaler + LogisticRegression(class_weight=balanced)",
  "hooks": {
    "curiosity_gap": {
      "n_train": 2283,
      "n_test": 571,
      "base_rate": 0.0214,
      "C": 0.03,
      "cv_f1_by_C": {
        "0.03": 0.2673,
        "0.1": 0.2445,
        "0.3": 0.1845,
        "1.0": 0.1622
      },
      "holdout_accuracy": 0.9562,
      "holdout_balanced_accuracy": 0.5699,
      "holdout_f1": 0.1379,
      "holdout_auc": 0.6942,
      "holdout_kappa": 0.1162
    },
    "outrage": {
      "n_train": 2283,
      "n_test": 571,
      "base_rate": 0.5739,
      "C": 0.03,
      "cv_f1_by_C": {
        "0.03": 0.7819,
        "0.1": 0.7674,
        "0.3": 0.7592,
        "1.0": 0.75
      },
      "holdout_accuracy": 0.7776,
      "holdout_balanced_accuracy": 0.7728,
      "holdout_f1": 0.8061,
      "holdout_auc": 0.8469,
      "holdout_kappa": 0.5453
    },
    "humor": {
      "n_train": 2283,
      "n_test": 571,
      "base_rate": 0.0039,
      "C": 0.03,
      "cv_f1_by_C": {
        "0.03": 0.0,
        "0.1": 0.0,
        "0.3": 0.0,
        "1.0": 0.0
      },
      "holdout_accuracy": 0.9982,
      "holdout_balanced_accuracy": 0.75,
      "holdout_f1": 0.6667,
      "holdout_auc": 0.9394,
      "holdout_kappa": 0.6659
    }
  }
}
```


## LLM rating prompt (labels.csv; exact text)


Temperature 0.0, prompt id `title-style-v3`, sha256 `03c5da1a9e41c1663e4e97797c79c74cf330976a57815c41ff7ee24f64ca61ad`, rated 2026-09-14T22:35:38+00:00.

```
You are annotating YouTube video titles from political-media channels. For each numbered title, rate five style dimensions on a 1-5 scale (1 = not at all, 3 = moderately, 5 = extremely), then give three yes/no flags (0 or 1) and one structural format label. Judge the title text only.

Dimensions:
- sensational: hype and emotional intensity - shock words, ALL-CAPS emphasis, exclamation marks, exaggeration, alarm. (1: 'Senate passes budget resolution'; 5: 'THIS CHANGES EVERYTHING!!! Trump's INSANE Move')
- critical: attacks, blames, mocks or condemns a person, group or institution. (1: 'How the Fed sets interest rates'; 5: 'Corrupt Coward Ted Cruz Humiliates Himself Again')
- analytical: informational or analytical framing - reports, explains or weighs a development in neutral, descriptive terms. (1: 'OMG..'; 5: 'Why the Iran ceasefire is fragile: three scenarios for the next month')
- educational: teaches - explains how something works, gives history or background, a how-to or explainer. (1: 'Trump SLAMS reporter'; 5: 'How tariffs actually work, explained')
- conversational: casual and chatty - addresses the audience directly, first or second person, slang, stream-of-consciousness. (1: 'Oil prices rise 3% as OPEC cuts output'; 5: 'chat, we need to talk about this..')
Use the whole 1-5 range: most titles are not 1 on every dimension.

Flags (answer 0 or 1 only, never a scale):
- humor: the title is meant to be funny or ironic (joke, pun, sarcasm, absurdity).
- curiosity_gap: key information is withheld to make you click (unnamed 'this' / 'he' / 'they', 'here's why', 'what happened next', trailing '...', a teaser).
- outrage: the subject is framed as outrageous, scandalous or threatening (slams, destroys, exposed, disaster, betrayal, meltdown).

Format (exactly one word): question | breaking_live | episode_show | interview_guest | reaction | confrontation | listicle | howto_explainer | none
question = phrased as a question; breaking_live = BREAKING / LIVE / WATCH label; episode_show = show name with an episode number or date; interview_guest = a named guest joins / interview / 'with' / 'ft.'; reaction = reacts to / responds to / reaction; confrontation = X vs Y, destroys, owns, debate, clash; listicle = a numbered list ('5 reasons', 'top 10'); howto_explainer = how to / explained / what is / why; none = none of these.

Output exactly one line per title, in order, with no other text:
id,sensational,critical,analytical,educational,conversational,humor_yn,curiosity_yn,outrage_yn,format
Example line for a title like 'Trump DESTROYS CNN reporter in heated exchange': 7,4,5,1,1,1,0,0,1,confrontation
Do not explain, do not add headers or commentary: only the CSV lines.

Titles:
{titles}
```


## Topic label prompt

```
You are labeling a topic found by clustering YouTube video titles from political-media channels.
Top terms (by class TF-IDF): {terms}
Example titles:
{examples}

Answer with one JSON object and nothing else:
{{"label": "<a short topic name, at most 6 words>", "political": true or false, "category": "<one of: {categories}>"}}
'political' is true when the topic concerns politics, government, elections, war, policy, courts, political figures or the culture war; false for sport, entertainment, weather, lifestyle, business/markets-only, science/health and similar.
```


## Leaning label prompt (leaning_labels.csv; exact text, prompt id leaning-v1, temperature 0, batches of 20; the same prompt in all three runs)

```
You are classifying YouTube video titles from political-media channels by the political viewpoint the TITLE ITSELF signals.
Labels:
- left = the framing, word choice or target of criticism signals a left-leaning / progressive stance.
- right = the framing, word choice or target of criticism signals a right-leaning / conservative stance.
- neither = a neutral news headline, a non-political title, or a political title whose stance cannot be told from its wording.
Judge the wording, not the subject: 'Trump signs order' is neither; 'Trump SLAMS radical left' is right; 'Trump's fascist crackdown' is left.
Output exactly one line per title, in order, as id,label with no other text.

Titles:
{titles}
```


## Zipf check

| level | text | max_rank | zipf_exponent | ranks_used | n_titles | n_tokens | n_types | top_20 |
|---|---|---|---|---|---|---|---|---|
| pooled_balanced | raw | 100 | 0.8573 | 100 | 183083 | 1999165 | 54552 | the trump to in on of iran s live is and as for a with us war after at news |
| pooled_balanced | raw | 1000 | 0.7813 | 1000 | 183083 | 1999165 | 54552 | the trump to in on of iran s live is and as for a with us war after at news |
| pooled_balanced | raw | 5000 | 1.0212 | 5000 | 183083 | 1999165 | 54552 | the trump to in on of iran s live is and as for a with us war after at news |
| pooled_balanced | normalised | 100 | 0.8636 | 100 | 183083 | 1943465 | 52809 | the trump to in on of iran s live is and as for a with us war after at over |
| pooled_balanced | normalised | 1000 | 0.7845 | 1000 | 183083 | 1943465 | 52809 | the trump to in on of iran s live is and as for a with us war after at over |
| pooled_balanced | normalised | 5000 | 1.0151 | 5000 | 183083 | 1943465 | 52809 | the trump to in on of iran s live is and as for a with us war after at over |
| creator_level_mean | raw | 200 | 0.7972 | 200 | 180878 | 1977690 | 483657 | median 0.7962 over 313 creator x genre groups (>= 50 titles) |
| creator_level_mean | normalised | 200 | 0.7806 | 200 | 180878 | 1923441 | 479933 | median 0.7826 over 313 creator x genre groups (>= 50 titles) |


## Sample sizes

| creator | genre | n_rows | n_unique | n_balanced | n_with_views | repeat_share | low_n |
|---|---|---|---|---|---|---|---|
| @60minutes | videos | 301 | 301 | 301 | 297 | 0.000 | no |
| @ABCNews | streams | 582 | 547 | 547 | 582 | 0.060 | no |
| @ABCNews | videos | 7549 | 7521 | 2500 | 7549 | 0.004 | no |
| @ANINewsIndia | streams | 7337 | 7202 | 2500 | 7337 | 0.018 | no |
| @ANINewsIndia | videos | 11635 | 11623 | 2500 | 11635 | 0.001 | no |
| @ActualJusticeWarrior | videos | 368 | 368 | 368 | 368 | 0.000 | no |
| @AfterPartyEmily | streams | 71 | 71 | 71 | 71 | 0.000 | no |
| @AfterPartyEmily | videos | 393 | 393 | 393 | 393 | 0.000 | no |
| @AlexStein99 | streams | 41 | 41 | 41 | 41 | 0.000 | yes |
| @AlexStein99 | videos | 82 | 82 | 82 | 82 | 0.000 | no |
| @AnaEscobarShow | streams | 31 | 31 | 31 | 31 | 0.000 | yes |
| @AnaEscobarShow | videos | 32 | 32 | 32 | 31 | 0.000 | yes |
| @AndWeKnowOfficial-o9b | videos | 184 | 184 | 184 | 184 | 0.000 | no |
| @AndrewKlavan | streams | 2 | 2 | 2 | 2 | 0.000 | yes |
| @AndrewKlavan | videos | 183 | 183 | 183 | 183 | 0.000 | no |
| @AnthonyBrianLogan | streams | 48 | 48 | 48 | 48 | 0.000 | yes |
| @AnthonyBrianLogan | videos | 233 | 233 | 233 | 233 | 0.000 | no |
| @AsmonTV | videos | 888 | 825 | 825 | 888 | 0.071 | no |
| @AssociatedPress | streams | 1267 | 1098 | 1098 | 1267 | 0.133 | no |
| @AssociatedPress | videos | 5263 | 5262 | 2500 | 5256 | 0.000 | no |
| @BBCNews | videos | 2356 | 2352 | 2352 | 2206 | 0.002 | no |
| @BadEmpanadaLive | streams | 1 | 1 | 1 | 1 | 0.000 | yes |
| @BadEmpanadaLive | videos | 274 | 274 | 274 | 273 | 0.000 | no |
| @BadFaithPodcast | streams | 1 | 1 | 1 | 1 | 0.000 | yes |
| @BadFaithPodcast | videos | 77 | 77 | 77 | 77 | 0.000 | no |
| @BelleRanch | videos | 770 | 770 | 770 | 770 | 0.000 | no |
| @BenShapiro | streams | 16 | 16 | 16 | 16 | 0.000 | yes |
| @BenShapiro | videos | 506 | 506 | 506 | 506 | 0.000 | no |
| @BlackConservativePerspective | streams | 1 | 1 | 1 | 1 | 0.000 | yes |
| @BlackConservativePerspective | videos | 1192 | 1192 | 1192 | 1192 | 0.000 | no |
| @BlaireWhiteX | videos | 10 | 10 | 10 | 10 | 0.000 | yes |
| @BlazeTV | streams | 14 | 14 | 14 | 14 | 0.000 | yes |
| @BlazeTV | videos | 829 | 829 | 829 | 829 | 0.000 | no |
| @BreakThroughNews | streams | 56 | 56 | 56 | 56 | 0.000 | no |
| @BreakThroughNews | videos | 234 | 234 | 234 | 234 | 0.000 | no |
| @BrittanyVenti | streams | 16 | 16 | 16 | 8 | 0.000 | yes |
| @BrittanyVenti | videos | 50 | 50 | 50 | 49 | 0.000 | no |
| @CBSNews | streams | 347 | 346 | 346 | 347 | 0.003 | no |
| @CBSNews | videos | 7956 | 7956 | 2500 | 7956 | 0.000 | no |
| @CNN | streams | 94 | 93 | 93 | 94 | 0.011 | no |
| @CNN | videos | 1638 | 1638 | 1638 | 1638 | 0.000 | no |
| @CamHigby | streams | 71 | 59 | 59 | 68 | 0.169 | no |
| @CamHigby | videos | 175 | 174 | 174 | 171 | 0.006 | no |
| @CashJordan | videos | 301 | 299 | 299 | 301 | 0.007 | no |
| @CaspianReport | videos | 25 | 25 | 25 | 25 | 0.000 | yes |
| @ChadPrather1 | streams | 191 | 190 | 190 | 191 | 0.005 | no |
| @ChadPrather1 | videos | 152 | 152 | 152 | 152 | 0.000 | no |
| @Channel5YouTube | videos | 42 | 42 | 42 | 42 | 0.000 | yes |
| @ClipsCandaceOwens | videos | 192 | 192 | 192 | 1 | 0.000 | no |
| @ClubRandomPodcast | videos | 185 | 185 | 185 | 185 | 0.000 | no |
| @ColeHastings | videos | 30 | 30 | 30 | 30 | 0.000 | yes |
| @ColemanHughesOfficial | videos | 52 | 52 | 52 | 52 | 0.000 | no |
| @CoreyGilShusterAskProject | streams | 2 | 2 | 2 | 2 | 0.000 | yes |
| @CoreyGilShusterAskProject | videos | 49 | 49 | 49 | 49 | 0.000 | yes |
| @DailyDenims | videos | 215 | 215 | 215 | 215 | 0.000 | no |
| @DannyHaiphongYT | streams | 220 | 220 | 220 | 219 | 0.000 | no |
| @DannyHaiphongYT | videos | 53 | 53 | 53 | 52 | 0.000 | no |
| @DarkHorsePod | streams | 35 | 35 | 35 | 35 | 0.000 | yes |
| @DarkHorsePod | videos | 65 | 65 | 65 | 65 | 0.000 | no |
| @DemocracyDocket | streams | 4 | 4 | 4 | 4 | 0.000 | yes |
| @DemocracyDocket | videos | 122 | 122 | 122 | 122 | 0.000 | no |
| @DemocracyNow | streams | 1 | 1 | 1 | 1 | 0.000 | yes |
| @DemocracyNow | videos | 770 | 767 | 767 | 770 | 0.004 | no |
| @DestinyDGGClips | videos | 191 | 191 | 191 | 191 | 0.000 | no |
| @DoubleDownNews | videos | 64 | 64 | 64 | 64 | 0.000 | no |
| @DrSteveTurleyTV | streams | 29 | 29 | 29 | 29 | 0.000 | yes |
| @DrSteveTurleyTV | videos | 419 | 417 | 417 | 419 | 0.005 | no |
| @DropSiteNews | streams | 42 | 42 | 42 | 42 | 0.000 | yes |
| @DropSiteNews | videos | 198 | 198 | 198 | 198 | 0.000 | no |
| @DueDissidence | streams | 105 | 105 | 105 | 105 | 0.000 | no |
| @DueDissidence | videos | 596 | 596 | 596 | 596 | 0.000 | no |
| @DylanBurnsLIVE | streams | 3 | 3 | 3 | 3 | 0.000 | yes |
| @DylanBurnsLIVE | videos | 175 | 175 | 175 | 175 | 0.000 | no |
| @EzraKleinShow | streams | 1 | 1 | 1 | 1 | 0.000 | yes |
| @EzraKleinShow | videos | 60 | 60 | 60 | 60 | 0.000 | no |
| @FarronBalanced | streams | 178 | 178 | 178 | 178 | 0.000 | no |
| @FarronBalanced | videos | 1707 | 1705 | 1705 | 1706 | 0.001 | no |
| @FinancialTimes | videos | 36 | 36 | 36 | 36 | 0.000 | yes |
| @Firstpost | streams | 9807 | 8485 | 2500 | 9807 | 0.135 | no |
| @Firstpost | videos | 9647 | 9637 | 2500 | 9647 | 0.001 | no |
| @FleccasTalks | videos | 288 | 288 | 288 | 66 | 0.000 | no |
| @Forbes | streams | 3 | 3 | 3 | 3 | 0.000 | yes |
| @Forbes | videos | 1208 | 1196 | 1196 | 1208 | 0.010 | no |
| @Forthepeoplepodcast305 | streams | 44 | 44 | 44 | 44 | 0.000 | yes |
| @Forthepeoplepodcast305 | videos | 111 | 111 | 111 | 111 | 0.000 | no |
| @FoxNews | streams | 607 | 597 | 597 | 607 | 0.017 | no |
| @FoxNews | videos | 7730 | 7727 | 2500 | 7675 | 0.000 | no |
| @FoxNewsChannelClips | videos | 5421 | 5421 | 2500 | 5421 | 0.000 | no |
| @FreshFitMiami | streams | 80 | 73 | 73 | 80 | 0.087 | no |
| @FreshFitMiami | videos | 98 | 98 | 98 | 98 | 0.000 | no |
| @GeopoliticalEconomyReport | videos | 67 | 67 | 67 | 67 | 0.000 | no |
| @GlennKirschner2 | videos | 246 | 244 | 244 | 246 | 0.008 | no |
| @GrahamAllen | videos | 247 | 247 | 247 | 247 | 0.000 | no |
| @HangOutwithSeanHannity | videos | 154 | 154 | 154 | 154 | 0.000 | no |
| @HasanAbi | streams | 7 | 7 | 7 | 7 | 0.000 | yes |
| @HasanAbi | videos | 597 | 591 | 591 | 597 | 0.010 | no |
| @HasanAbiVODs3 | videos | 163 | 163 | 163 | 163 | 0.000 | no |
| @HasanReactionsfanTwo | videos | 319 | 319 | 319 | 319 | 0.000 | no |
| @HasanabiClips | streams | 35 | 32 | 32 | 35 | 0.086 | yes |
| @HasanabiClips | videos | 474 | 474 | 474 | 474 | 0.000 | no |
| @JackCocchiarellaShow | streams | 21 | 21 | 21 | 21 | 0.000 | yes |
| @JackCocchiarellaShow | videos | 1524 | 1446 | 1446 | 1524 | 0.051 | no |
| @JacksonHinkleOfficial | streams | 78 | 76 | 76 | 1 | 0.026 | no |
| @JacksonHinkleOfficial | videos | 346 | 343 | 343 | 3 | 0.009 | no |
| @JamarlThomas | streams | 217 | 217 | 217 | 217 | 0.000 | no |
| @JamarlThomas | videos | 245 | 245 | 245 | 245 | 0.000 | no |
| @JesseKellyDC | streams | 1 | 1 | 1 | 1 | 0.000 | yes |
| @JesseKellyDC | videos | 479 | 478 | 478 | 479 | 0.002 | no |
| @JillianMichaels | videos | 437 | 437 | 437 | 437 | 0.000 | no |
| @JustPearlyThings | streams | 88 | 88 | 88 | 88 | 0.000 | no |
| @JustPearlyThings | videos | 631 | 631 | 631 | 631 | 0.000 | no |
| @KimIversen | streams | 1 | 1 | 1 | 1 | 0.000 | yes |
| @KimIversen | videos | 505 | 505 | 505 | 505 | 0.000 | no |
| @LIVESNEAKO | streams | 69 | 69 | 69 | 69 | 0.000 | no |
| @LIVESNEAKO | videos | 474 | 472 | 472 | 474 | 0.004 | no |
| @LastWeekTonight | videos | 35 | 35 | 35 | 35 | 0.000 | yes |
| @LeejaMiller | streams | 1 | 1 | 1 | 1 | 0.000 | yes |
| @LeejaMiller | videos | 56 | 56 | 56 | 56 | 0.000 | no |
| @LegalAFMTN | streams | 46 | 45 | 45 | 46 | 0.022 | yes |
| @LegalAFMTN | videos | 2598 | 2593 | 2500 | 2329 | 0.002 | no |
| @LegalEagle | videos | 97 | 97 | 97 | 97 | 0.000 | no |
| @LeverNews | streams | 9 | 9 | 9 | 9 | 0.000 | yes |
| @LeverNews | videos | 71 | 71 | 71 | 71 | 0.000 | no |
| @LiberalHivemind | videos | 807 | 800 | 800 | 807 | 0.009 | no |
| @LukeBeasley | streams | 247 | 246 | 246 | 155 | 0.004 | no |
| @LukeBeasley | videos | 1115 | 1109 | 1109 | 1028 | 0.005 | no |
| @Lunaoi | videos | 8 | 8 | 8 | 8 | 0.000 | yes |
| @MLChristiansen | streams | 73 | 73 | 73 | 73 | 0.000 | no |
| @MLChristiansen | videos | 116 | 116 | 116 | 116 | 0.000 | no |
| @MarkDice | videos | 89 | 89 | 89 | 89 | 0.000 | no |
| @MattBernstein1 | videos | 20 | 20 | 20 | 20 | 0.000 | yes |
| @MattWalsh | streams | 2 | 2 | 2 | 2 | 0.000 | yes |
| @MattWalsh | videos | 277 | 277 | 277 | 244 | 0.000 | no |
| @MegynKelly | streams | 13 | 13 | 13 | 11 | 0.000 | yes |
| @MegynKelly | videos | 1591 | 1591 | 1591 | 1587 | 0.000 | no |
| @MeidasTouch | streams | 590 | 586 | 586 | 590 | 0.007 | no |
| @MeidasTouch | videos | 3316 | 3315 | 2500 | 3196 | 0.000 | no |
| @MichaelKnowles | streams | 3 | 3 | 3 | 3 | 0.000 | yes |
| @MichaelKnowles | videos | 445 | 445 | 445 | 445 | 0.000 | no |
| @MichaelMaliceofficial | streams | 3 | 3 | 3 | 3 | 0.000 | yes |
| @MichaelMaliceofficial | videos | 51 | 51 | 51 | 51 | 0.000 | no |
| @MikeFromPA | videos | 125 | 125 | 125 | 125 | 0.000 | no |
| @ModernDayDebate | streams | 107 | 107 | 107 | 80 | 0.000 | no |
| @ModernDayDebate | videos | 46 | 45 | 45 | 41 | 0.022 | yes |
| @MrReaganUSA | videos | 24 | 24 | 24 | 24 | 0.000 | yes |
| @MrTariqNasheed | streams | 16 | 16 | 16 | 16 | 0.000 | yes |
| @MrTariqNasheed | videos | 354 | 354 | 354 | 354 | 0.000 | no |
| @MyronGainesX | streams | 242 | 240 | 240 | 242 | 0.008 | no |
| @MyronGainesX | videos | 365 | 365 | 365 | 365 | 0.000 | no |
| @NBCNews | streams | 386 | 350 | 350 | 386 | 0.093 | no |
| @NBCNews | videos | 6176 | 6161 | 2500 | 6176 | 0.002 | no |
| @NPR | streams | 1 | 1 | 1 | 1 | 0.000 | yes |
| @NPR | videos | 73 | 70 | 70 | 73 | 0.041 | no |
| @NYTOpinion | videos | 27 | 27 | 27 | 27 | 0.000 | yes |
| @NYTPodcasts | videos | 454 | 454 | 454 | 447 | 0.000 | no |
| @NewsNation | streams | 286 | 282 | 282 | 286 | 0.014 | no |
| @NewsNation | videos | 6898 | 6882 | 2500 | 6897 | 0.002 | no |
| @NewsmaxTV | streams | 388 | 383 | 383 | 388 | 0.013 | no |
| @NewsmaxTV | videos | 3745 | 3744 | 2500 | 3745 | 0.000 | no |
| @NickCruseRBN | streams | 99 | 99 | 99 | 99 | 0.000 | no |
| @NickCruseRBN | videos | 23 | 23 | 23 | 23 | 0.000 | yes |
| @NickShirley | streams | 12 | 12 | 12 | 9 | 0.000 | yes |
| @NickShirley | videos | 29 | 29 | 29 | 27 | 0.000 | yes |
| @NovaraMedia | streams | 4 | 4 | 4 | 4 | 0.000 | yes |
| @NovaraMedia | videos | 565 | 565 | 565 | 565 | 0.000 | no |
| @OfficialFlagrant | videos | 34 | 34 | 34 | 34 | 0.000 | yes |
| @OfficialSaharTV | streams | 2 | 2 | 2 | 2 | 0.000 | yes |
| @OfficialSaharTV | videos | 831 | 831 | 831 | 825 | 0.000 | no |
| @OutKick | videos | 47 | 47 | 47 | 47 | 0.000 | yes |
| @OwenJonesTalks | videos | 226 | 226 | 226 | 226 | 0.000 | no |
| @OwenReport | streams | 167 | 167 | 167 | 167 | 0.000 | no |
| @OwenReport | videos | 368 | 368 | 368 | 368 | 0.000 | no |
| @PBDPodcast | streams | 111 | 111 | 111 | 111 | 0.000 | no |
| @PBDPodcast | videos | 34 | 34 | 34 | 34 | 0.000 | yes |
| @POLITICO | videos | 286 | 286 | 286 | 286 | 0.000 | no |
| @PTLRadioShow | streams | 190 | 189 | 189 | 190 | 0.005 | no |
| @PTLRadioShow | videos | 1581 | 1580 | 1580 | 1581 | 0.001 | no |
| @PartOfTheProblem | videos | 97 | 97 | 97 | 97 | 0.000 | no |
| @PerunAU | videos | 35 | 35 | 35 | 35 | 0.000 | yes |
| @PhillipScottPodcast | streams | 147 | 147 | 147 | 147 | 0.000 | no |
| @PhillipScottPodcast | videos | 3 | 3 | 3 | 3 | 0.000 | yes |
| @PiersMorganUncensored | videos | 173 | 173 | 173 | 173 | 0.000 | no |
| @PiscoLitty | videos | 54 | 54 | 54 | 54 | 0.000 | no |
| @Politicon | streams | 1 | 1 | 1 | 1 | 0.000 | yes |
| @Politicon | videos | 480 | 480 | 480 | 480 | 0.000 | no |
| @PoliticsGirl | videos | 110 | 110 | 110 | 110 | 0.000 | no |
| @PoliticsJOE | videos | 325 | 325 | 325 | 325 | 0.000 | no |
| @PragerU | streams | 32 | 31 | 31 | 32 | 0.031 | yes |
| @PragerU | videos | 373 | 371 | 371 | 373 | 0.005 | no |
| @PrisonPlanetLive | videos | 54 | 44 | 44 | 54 | 0.185 | yes |
| @RSBN | streams | 315 | 315 | 315 | 315 | 0.000 | no |
| @RSBN | videos | 1555 | 1553 | 1553 | 1555 | 0.001 | no |
| @RealAlexClark | videos | 73 | 73 | 73 | 73 | 0.000 | no |
| @RealAmericasVoice | streams | 2944 | 1535 | 1535 | 2944 | 0.479 | no |
| @RealAmericasVoice | videos | 2344 | 2339 | 2339 | 2344 | 0.002 | no |
| @RealDanBongino | videos | 266 | 266 | 266 | 266 | 0.000 | no |
| @RebelHQ | videos | 1191 | 1190 | 1190 | 1191 | 0.001 | no |
| @RebelNewsOnline | streams | 189 | 187 | 187 | 189 | 0.011 | no |
| @RebelNewsOnline | videos | 1283 | 1273 | 1273 | 1075 | 0.008 | no |
| @RedactedNews | streams | 136 | 136 | 136 | 136 | 0.000 | no |
| @RedactedNews | videos | 424 | 424 | 424 | 424 | 0.000 | no |
| @RekietaLaw | streams | 103 | 103 | 103 | 79 | 0.000 | no |
| @RekietaLaw | videos | 18 | 18 | 18 | 18 | 0.000 | yes |
| @RestPoliticsUS | streams | 5 | 5 | 5 | 5 | 0.000 | yes |
| @RestPoliticsUS | videos | 208 | 208 | 208 | 99 | 0.000 | no |
| @Reuters | streams | 2176 | 1901 | 1901 | 2176 | 0.126 | no |
| @Reuters | videos | 7695 | 7680 | 2500 | 7695 | 0.002 | no |
| @RileyGaines | videos | 143 | 143 | 143 | 143 | 0.000 | no |
| @RobertGouveiaEsq | streams | 374 | 363 | 363 | 190 | 0.029 | no |
| @RobertGouveiaEsq | videos | 660 | 660 | 660 | 654 | 0.000 | no |
| @RonPlacone | streams | 28 | 28 | 28 | 28 | 0.000 | yes |
| @RonPlacone | videos | 63 | 63 | 63 | 63 | 0.000 | no |
| @RubinReport | streams | 113 | 112 | 112 | 113 | 0.009 | no |
| @RubinReport | videos | 1057 | 1011 | 1011 | 1057 | 0.043 | no |
| @RufoandLomez | videos | 74 | 74 | 74 | 74 | 0.000 | no |
| @SMN | streams | 8 | 8 | 8 | 7 | 0.000 | yes |
| @SMN | videos | 190 | 190 | 190 | 95 | 0.000 | no |
| @SNEAKO | videos | 3 | 3 | 3 | 3 | 0.000 | yes |
| @SabbySabs | streams | 98 | 98 | 98 | 98 | 0.000 | no |
| @SabbySabs | videos | 587 | 587 | 587 | 587 | 0.000 | no |
| @SaltyCracker | videos | 361 | 361 | 361 | 361 | 0.000 | no |
| @SavSays | streams | 1 | 1 | 1 | 0 | 0.000 | yes |
| @SavSays | videos | 16 | 16 | 16 | 16 | 0.000 | yes |
| @SecondThought | videos | 19 | 19 | 19 | 19 | 0.000 | yes |
| @SecularTalk | streams | 1 | 1 | 1 | 1 | 0.000 | yes |
| @SecularTalk | videos | 1375 | 1374 | 1374 | 1375 | 0.001 | no |
| @Semafor | streams | 30 | 30 | 30 | 30 | 0.000 | yes |
| @Semafor | videos | 149 | 149 | 149 | 149 | 0.000 | no |
| @Shoe0nHead | videos | 9 | 9 | 9 | 9 | 0.000 | yes |
| @SkyNews | streams | 1876 | 1868 | 1868 | 1830 | 0.004 | no |
| @SkyNews | videos | 3415 | 3412 | 2500 | 3415 | 0.001 | no |
| @StatusCoup | streams | 154 | 152 | 152 | 154 | 0.013 | no |
| @StatusCoup | videos | 489 | 489 | 489 | 470 | 0.000 | no |
| @StevenCrowder | streams | 8 | 8 | 8 | 8 | 0.000 | yes |
| @StevenCrowder | videos | 165 | 165 | 165 | 165 | 0.000 | no |
| @StosselTV | videos | 47 | 47 | 47 | 47 | 0.000 | yes |
| @Styxhexenhammer666 | streams | 16 | 16 | 16 | 16 | 0.000 | yes |
| @Styxhexenhammer666 | videos | 383 | 380 | 380 | 383 | 0.008 | no |
| @SydneyWatson | videos | 57 | 57 | 57 | 57 | 0.000 | no |
| @TechCrunch | videos | 140 | 139 | 139 | 140 | 0.007 | no |
| @TheAdamCarollaShow1 | videos | 372 | 372 | 372 | 372 | 0.000 | no |
| @TheAmalaEkpunobi | streams | 12 | 12 | 12 | 12 | 0.000 | yes |
| @TheAmalaEkpunobi | videos | 197 | 197 | 197 | 197 | 0.000 | no |
| @TheAtlantic | streams | 5 | 5 | 5 | 5 | 0.000 | yes |
| @TheAtlantic | videos | 157 | 157 | 157 | 157 | 0.000 | no |
| @TheBrianKilmeadeShow | streams | 2 | 2 | 2 | 2 | 0.000 | yes |
| @TheBrianKilmeadeShow | videos | 352 | 352 | 352 | 352 | 0.000 | no |
| @TheDailyBeast | streams | 34 | 34 | 34 | 3 | 0.000 | yes |
| @TheDailyBeast | videos | 294 | 294 | 294 | 293 | 0.000 | no |
| @TheDamageReport | streams | 262 | 259 | 259 | 84 | 0.011 | no |
| @TheDamageReport | videos | 3017 | 3015 | 2500 | 2097 | 0.001 | no |
| @TheDonLemonShow | streams | 377 | 377 | 377 | 348 | 0.000 | no |
| @TheDonLemonShow | videos | 348 | 348 | 348 | 348 | 0.000 | no |
| @TheEconomist | videos | 130 | 130 | 130 | 130 | 0.000 | no |
| @TheHumanistReport | streams | 34 | 34 | 34 | 34 | 0.000 | yes |
| @TheHumanistReport | videos | 146 | 146 | 146 | 146 | 0.000 | no |
| @TheJoyReidShow | streams | 139 | 135 | 135 | 131 | 0.029 | no |
| @TheJoyReidShow | videos | 234 | 234 | 234 | 233 | 0.000 | no |
| @TheLincolnProject | streams | 28 | 28 | 28 | 28 | 0.000 | yes |
| @TheLincolnProject | videos | 119 | 119 | 119 | 119 | 0.000 | no |
| @TheMajorityReport | streams | 183 | 183 | 183 | 183 | 0.000 | no |
| @TheMajorityReport | videos | 1523 | 1520 | 1520 | 1523 | 0.002 | no |
| @TheMichaelCohenShow | videos | 437 | 437 | 437 | 435 | 0.000 | no |
| @TheOfficerTatum | streams | 192 | 192 | 192 | 135 | 0.000 | no |
| @TheOfficerTatum | videos | 599 | 599 | 599 | 564 | 0.000 | no |
| @ThePodcastoftheLotusEaters | streams | 179 | 179 | 179 | 179 | 0.000 | no |
| @ThePodcastoftheLotusEaters | videos | 588 | 588 | 588 | 588 | 0.000 | no |
| @TheQuartering | videos | 653 | 637 | 637 | 653 | 0.025 | no |
| @TheRealTabithaSpeaks | streams | 3 | 3 | 3 | 3 | 0.000 | yes |
| @TheRealTabithaSpeaks | videos | 431 | 431 | 431 | 425 | 0.000 | no |
| @TheSerfTimes | streams | 101 | 98 | 98 | 1 | 0.030 | no |
| @TheSerfTimes | videos | 233 | 233 | 233 | 233 | 0.000 | no |
| @TheVaushPit | videos | 384 | 384 | 384 | 384 | 0.000 | no |
| @TheYoungTurks | streams | 423 | 403 | 403 | 227 | 0.047 | no |
| @TheYoungTurks | videos | 2710 | 2706 | 2500 | 1838 | 0.002 | no |
| @The_Crucible | streams | 5 | 5 | 5 | 5 | 0.000 | yes |
| @The_Crucible | videos | 218 | 218 | 218 | 218 | 0.000 | no |
| @TimDillonShow | videos | 66 | 66 | 66 | 36 | 0.000 | no |
| @Tim_Black | streams | 16 | 16 | 16 | 16 | 0.000 | yes |
| @Tim_Black | videos | 311 | 311 | 311 | 311 | 0.000 | no |
| @Timcast | streams | 5 | 5 | 5 | 5 | 0.000 | yes |
| @Timcast | videos | 177 | 174 | 174 | 177 | 0.017 | no |
| @TimcastIRL | streams | 149 | 149 | 149 | 149 | 0.000 | no |
| @TimcastIRL | videos | 872 | 824 | 824 | 872 | 0.055 | no |
| @TimcastNews | streams | 8 | 8 | 8 | 8 | 0.000 | yes |
| @TimcastNews | videos | 533 | 519 | 519 | 533 | 0.026 | no |
| @TimesNowWorld | streams | 4989 | 2827 | 2500 | 4989 | 0.433 | no |
| @TimesNowWorld | videos | 8496 | 8489 | 2500 | 8491 | 0.001 | no |
| @TomiLahrenIsFearless | videos | 113 | 113 | 113 | 113 | 0.000 | no |
| @TuckerCarlson | videos | 113 | 113 | 113 | 113 | 0.000 | no |
| @USATODAY | streams | 407 | 396 | 396 | 407 | 0.027 | no |
| @USATODAY | videos | 2138 | 2135 | 2135 | 2138 | 0.001 | no |
| @UnHerd | streams | 16 | 16 | 16 | 16 | 0.000 | yes |
| @UnHerd | videos | 76 | 76 | 76 | 76 | 0.000 | no |
| @Unpacked | videos | 38 | 38 | 38 | 38 | 0.000 | yes |
| @Vaush | streams | 1 | 1 | 1 | 1 | 0.000 | yes |
| @Vaush | videos | 431 | 431 | 431 | 431 | 0.000 | no |
| @VivaFrei | streams | 49 | 49 | 49 | 49 | 0.000 | yes |
| @VivaFrei | videos | 310 | 310 | 310 | 310 | 0.000 | no |
| @Vox | videos | 127 | 127 | 127 | 127 | 0.000 | no |
| @X22Report-y5y | videos | 380 | 379 | 379 | 380 | 0.003 | no |
| @XAVIAER | streams | 2 | 2 | 2 | 2 | 0.000 | yes |
| @XAVIAER | videos | 68 | 68 | 68 | 68 | 0.000 | no |
| @Xanderhal | streams | 101 | 101 | 101 | 1 | 0.000 | no |
| @Xanderhal | videos | 289 | 289 | 289 | 289 | 0.000 | no |
| @YaBoiHakim | videos | 15 | 15 | 15 | 15 | 0.000 | yes |
| @ZeihanonGeopolitics | videos | 202 | 202 | 202 | 202 | 0.000 | no |
| @ZubyMusic | videos | 130 | 130 | 130 | 130 | 0.000 | no |
| @aaronparnas1 | streams | 13 | 10 | 10 | 13 | 0.231 | yes |
| @aaronparnas1 | videos | 769 | 769 | 769 | 769 | 0.000 | no |
| @adammockler | streams | 2 | 2 | 2 | 2 | 0.000 | yes |
| @adammockler | videos | 1063 | 1055 | 1055 | 1059 | 0.007 | no |
| @ajplus | videos | 50 | 50 | 50 | 50 | 0.000 | no |
| @aljazeeraenglish | videos | 6649 | 6643 | 2500 | 6649 | 0.001 | no |
| @axios | streams | 8 | 7 | 7 | 8 | 0.125 | yes |
| @axios | videos | 138 | 137 | 137 | 138 | 0.007 | no |
| @bbrettcooper | videos | 139 | 139 | 139 | 139 | 0.000 | no |
| @bennyjohnson | streams | 162 | 162 | 162 | 162 | 0.000 | no |
| @bennyjohnson | videos | 1453 | 1453 | 1453 | 1453 | 0.000 | no |
| @breakingpoints | streams | 4 | 4 | 4 | 4 | 0.000 | yes |
| @breakingpoints | videos | 998 | 998 | 998 | 998 | 0.000 | no |
| @briantylercohen | streams | 10 | 10 | 10 | 10 | 0.000 | yes |
| @briantylercohen | videos | 1020 | 1019 | 1019 | 1020 | 0.001 | no |
| @bulwarkmedia | streams | 223 | 223 | 223 | 220 | 0.000 | no |
| @bulwarkmedia | videos | 2025 | 1730 | 1730 | 907 | 0.146 | no |
| @bushrakhanum | videos | 22 | 22 | 22 | 22 | 0.000 | yes |
| @cafedotcom | videos | 52 | 52 | 52 | 52 | 0.000 | no |
| @chicksonright | streams | 174 | 174 | 174 | 174 | 0.000 | no |
| @chicksonright | videos | 446 | 446 | 446 | 446 | 0.000 | no |
| @chinainsights-r2w | videos | 238 | 238 | 238 | 238 | 0.000 | no |
| @chriscuomo | streams | 9 | 8 | 8 | 8 | 0.111 | yes |
| @chriscuomo | videos | 203 | 203 | 203 | 122 | 0.000 | no |
| @clayandbuck | streams | 42 | 42 | 42 | 42 | 0.000 | yes |
| @clayandbuck | videos | 565 | 565 | 565 | 565 | 0.000 | no |
| @deanwithrs | streams | 253 | 251 | 251 | 253 | 0.008 | no |
| @deanwithrs | videos | 251 | 251 | 251 | 251 | 0.000 | no |
| @destiny | videos | 262 | 262 | 262 | 262 | 0.000 | no |
| @destinyhqclips | videos | 197 | 197 | 197 | 197 | 0.000 | no |
| @dineshdsouza | streams | 2 | 2 | 2 | 2 | 0.000 | yes |
| @dineshdsouza | videos | 62 | 62 | 62 | 62 | 0.000 | no |
| @dollemore | streams | 4 | 4 | 4 | 4 | 0.000 | yes |
| @dollemore | videos | 1376 | 1376 | 1376 | 1376 | 0.000 | no |
| @doomscrollpodcast | videos | 16 | 16 | 16 | 16 | 0.000 | yes |
| @evanjmez | videos | 22 | 22 | 22 | 22 | 0.000 | yes |
| @fastpoliticspodcast | videos | 138 | 138 | 138 | 128 | 0.000 | no |
| @fightbackpodcast | streams | 24 | 24 | 24 | 24 | 0.000 | yes |
| @fightbackpodcast | videos | 587 | 584 | 584 | 587 | 0.005 | no |
| @franifio | streams | 60 | 60 | 60 | 60 | 0.000 | no |
| @franifio | videos | 271 | 271 | 271 | 257 | 0.000 | no |
| @glennbeck | streams | 125 | 125 | 125 | 125 | 0.000 | no |
| @glennbeck | videos | 437 | 437 | 437 | 437 | 0.000 | no |
| @harryjsisson | streams | 3 | 3 | 3 | 3 | 0.000 | yes |
| @harryjsisson | videos | 639 | 632 | 632 | 639 | 0.011 | no |
| @hutch | streams | 50 | 50 | 50 | 1 | 0.000 | no |
| @hutch | videos | 160 | 160 | 160 | 160 | 0.000 | no |
| @jimacosta | streams | 157 | 156 | 156 | 157 | 0.006 | no |
| @jimacosta | videos | 302 | 301 | 301 | 300 | 0.003 | no |
| @jlptalk | streams | 180 | 180 | 180 | 180 | 0.000 | no |
| @jlptalk | videos | 293 | 293 | 293 | 277 | 0.000 | no |
| @joerogan | streams | 1 | 1 | 1 | 1 | 0.000 | yes |
| @joerogan | videos | 133 | 133 | 133 | 133 | 0.000 | no |
| @johnnyharris | videos | 11 | 11 | 11 | 11 | 0.000 | yes |
| @judgingfreedom | streams | 660 | 658 | 658 | 660 | 0.003 | no |
| @judgingfreedom | videos | 345 | 345 | 345 | 345 | 0.000 | no |
| @katiephangnews | streams | 45 | 44 | 44 | 45 | 0.022 | yes |
| @katiephangnews | videos | 381 | 381 | 381 | 381 | 0.000 | no |
| @katmabu | videos | 32 | 31 | 31 | 32 | 0.031 | yes |
| @laurenchenclips | videos | 109 | 109 | 109 | 109 | 0.000 | no |
| @lizwheeler | streams | 67 | 67 | 67 | 67 | 0.000 | no |
| @lizwheeler | videos | 77 | 77 | 77 | 77 | 0.000 | no |
| @lonerboxlive | videos | 82 | 82 | 82 | 82 | 0.000 | no |
| @lovettorleaveitpodcast | videos | 110 | 110 | 110 | 110 | 0.000 | no |
| @marclamonthillnetwork | streams | 145 | 145 | 145 | 145 | 0.000 | no |
| @marclamonthillnetwork | videos | 309 | 309 | 309 | 309 | 0.000 | no |
| @markets | streams | 55 | 55 | 55 | 55 | 0.000 | no |
| @markets | videos | 7698 | 7665 | 2500 | 7698 | 0.004 | no |
| @marklevinshow | videos | 486 | 486 | 486 | 486 | 0.000 | no |
| @mikhaila | videos | 26 | 26 | 26 | 26 | 0.000 | yes |
| @morebridgetphetasy | videos | 200 | 200 | 200 | 200 | 0.000 | no |
| @moreperfectunion | streams | 4 | 4 | 4 | 4 | 0.000 | yes |
| @moreperfectunion | videos | 68 | 68 | 68 | 68 | 0.000 | no |
| @msnow | streams | 318 | 308 | 308 | 318 | 0.031 | no |
| @msnow | videos | 9401 | 9398 | 2500 | 9401 | 0.000 | no |
| @nationalreview | streams | 2 | 2 | 2 | 2 | 0.000 | yes |
| @nationalreview | videos | 183 | 183 | 183 | 183 | 0.000 | no |
| @newdiscourses | videos | 95 | 95 | 95 | 82 | 0.000 | no |
| @newyorker | videos | 50 | 50 | 50 | 50 | 0.000 | no |
| @notsoErudite | streams | 20 | 20 | 20 | 0 | 0.000 | yes |
| @notsoErudite | videos | 42 | 42 | 42 | 42 | 0.000 | yes |
| @nousnetwork | videos | 152 | 152 | 152 | 152 | 0.000 | no |
| @nypost | streams | 102 | 98 | 98 | 102 | 0.039 | no |
| @nypost | videos | 6037 | 6036 | 2500 | 6037 | 0.000 | no |
| @nytimes | videos | 69 | 69 | 69 | 69 | 0.000 | no |
| @oann | streams | 338 | 304 | 304 | 338 | 0.101 | no |
| @oann | videos | 1737 | 1736 | 1736 | 1737 | 0.001 | no |
| @podsaveamerica | videos | 705 | 643 | 643 | 274 | 0.088 | no |
| @ponderingpolitics | streams | 2 | 2 | 2 | 2 | 0.000 | yes |
| @ponderingpolitics | videos | 1395 | 1392 | 1392 | 1263 | 0.002 | no |
| @revleftradio | streams | 3 | 3 | 3 | 3 | 0.000 | yes |
| @revleftradio | videos | 38 | 38 | 38 | 38 | 0.000 | yes |
| @rolandsmartin | streams | 1181 | 569 | 569 | 1181 | 0.518 | no |
| @rolandsmartin | videos | 698 | 698 | 698 | 698 | 0.000 | no |
| @samharrisorg | videos | 108 | 108 | 108 | 71 | 0.000 | no |
| @theGuardian | videos | 38 | 38 | 38 | 38 | 0.000 | yes |
| @thedavidpakmanshow | streams | 5 | 5 | 5 | 5 | 0.000 | yes |
| @thedavidpakmanshow | videos | 1558 | 1541 | 1541 | 1558 | 0.011 | no |
| @thegrayzone7996 | streams | 35 | 35 | 35 | 35 | 0.000 | yes |
| @thegrayzone7996 | videos | 144 | 144 | 144 | 144 | 0.000 | no |
| @thehill | streams | 494 | 490 | 490 | 494 | 0.008 | no |
| @thehill | videos | 4046 | 4045 | 2500 | 4046 | 0.000 | no |
| @theisabelbrown | videos | 134 | 134 | 134 | 134 | 0.000 | no |
| @thejimmydoreshow | streams | 109 | 108 | 108 | 109 | 0.009 | no |
| @thejimmydoreshow | videos | 1077 | 1077 | 1077 | 1077 | 0.000 | no |
| @therationalnational | streams | 7 | 7 | 7 | 7 | 0.000 | yes |
| @therationalnational | videos | 135 | 135 | 135 | 135 | 0.000 | no |
| @thewarningwithsteveschmidt | streams | 113 | 110 | 110 | 109 | 0.026 | no |
| @thewarningwithsteveschmidt | videos | 347 | 273 | 273 | 207 | 0.213 | no |
| @thomhartmann | videos | 760 | 760 | 760 | 760 | 0.000 | no |
| @timesofindia | streams | 3235 | 2094 | 2094 | 3235 | 0.353 | no |
| @timesofindia | videos | 9374 | 9372 | 2500 | 9374 | 0.000 | no |
| @triggerpod | streams | 6 | 6 | 6 | 6 | 0.000 | yes |
| @triggerpod | videos | 144 | 143 | 143 | 97 | 0.007 | no |
| @turningpointusa | streams | 14 | 13 | 13 | 14 | 0.071 | yes |
| @turningpointusa | videos | 152 | 152 | 152 | 152 | 0.000 | no |
| @underthedesknews | streams | 119 | 115 | 115 | 119 | 0.034 | no |
| @underthedesknews | videos | 74 | 74 | 74 | 74 | 0.000 | no |
| @usefulidiots | streams | 66 | 11 | 11 | 66 | 0.833 | yes |
| @usefulidiots | videos | 183 | 179 | 179 | 158 | 0.022 | no |
| @wethefifth | streams | 2 | 2 | 2 | 2 | 0.000 | yes |
| @wethefifth | videos | 107 | 107 | 107 | 107 | 0.000 | no |
| @winston_marshall | videos | 104 | 104 | 104 | 85 | 0.000 | no |
| @wsj | streams | 10 | 10 | 10 | 10 | 0.000 | yes |
| @wsj | videos | 104 | 104 | 104 | 104 | 0.000 | no |
| @zeteo | streams | 24 | 24 | 24 | 24 | 0.000 | yes |
| @zeteo | videos | 198 | 198 | 198 | 198 | 0.000 | no |
| https://rumble.com/c/BannonsWarRoom | videos | 4619 | 4506 | 2500 | 0 | 0.025 | no |
| https://rumble.com/c/GGreenwald | videos | 76 | 76 | 76 | 0 | 0.000 | no |
| https://rumble.com/c/TheAlexJonesShowLive | videos | 517 | 513 | 513 | 0 | 0.008 | no |
| https://rumble.com/c/nickjfuentes | videos | 309 | 305 | 305 | 0 | 0.013 | no |
| https://rumble.com/c/russellbrand | videos | 262 | 259 | 259 | 0 | 0.011 | no |


## Runtime and cost per stage (last run and longest run of each; a --label-only re-run of topics is seconds, the fit was minutes)

| stage | seconds_last_run | seconds_longest_run | finished | llm_calls | output_tokens | api_cost_usd | notes |
|---|---|---|---|---|---|---|---|
| stage0_prepare | 30.7 | 34.4 | 2026-09-22T14:11:00+00:00 |  |  |  | min_share=0.2, min_count=10, rows=309596, unique=300420, balanced=189240, low_n_groups=124 |
| stage0c_annotate | 11.4 | 108.8 | 2026-09-22T14:14:20+00:00 |  |  |  | titles=292688, all_caps=11192, proper_lexicon=11667, acronyms=956 |
| stage1a_embed | 6.0 | 289.2 | 2026-09-22T14:14:30+00:00 |  |  |  | device=mps, n=292688, dim=768 |
| stage2c_llm_rate | 6265.5 | 6265.5 | 2026-09-14T22:35:38+00:00 | 172 | 69430 | 0.0 | temperature=0.0, prompt_id=title-style-v3, cache_hits=2, llm_seconds=6264.3, n_rated=3000, flag_coercions=0... |
| stage2a_features | 66.8 | 353.2 | 2026-09-22T14:25:53+00:00 |  |  |  |  |
| stage1_topics | 616.5 | 6343.9 | 2026-09-22T14:24:46+00:00 | 224 | 5706 | 0.0 | fit_size=100000, min_cluster_size=80, min_samples=15, max_topics=250, fit_n=100041, fit_cap=561, hdbscan_to... |
| stage2b_factors | 2.2 | 2.5 | 2026-09-22T14:25:55+00:00 |  |  |  | n_factors_forced=None, n_cells=2029, n_features=74, retained=12, parallel=16, kmo=0.725 |
| stage2d_validate | 0.7 | 0.7 | 2026-09-22T14:27:26+00:00 |  |  |  | n_rated_matched=2854, n_creator_groups=318, n_retest=289 |
| stage3_formats | 13.5 | 13.5 | 2026-09-22T14:27:39+00:00 |  |  |  | curiosity_gap_holdout_f1=0.1379, outrage_holdout_f1=0.8061, humor_holdout_f1=0.6667 |
| stage4_landscape | 22.9 | 26.2 | 2026-09-22T14:28:02+00:00 |  |  |  | crossposted_titles=2237, cluster_runs=4, shared_titles_any=1575, shared_titles_cross_org=474, shared_titles... |
| stage5a_timeline | 1.0 | 1.4 | 2026-09-22T14:28:03+00:00 |  |  |  | group_month_rows=54, top30=30, topic_change_rows=1667 |
| stage5b_engagement | 5.7 | 9.4 | 2026-09-22T14:28:55+00:00 |  |  |  | creator_genre_models=252 |
| stage5c_hits | 25.8 | 28.9 | 2026-09-22T14:29:21+00:00 |  |  |  | groups=252, powerlaw_like=1 |
| report_data | 3.2 | 3.2 | 2026-09-22T14:29:47+00:00 |  |  |  | creators=274 |
| report | 15.1 | 24.6 | 2026-09-21T17:54:29+00:00 |  |  |  | cards=274 |
| stage6_profiles | 20.0 | 23.8 | 2026-09-22T14:29:41+00:00 |  |  |  | acronyms=961, twin_pairs=9200 |
| stage7_leaning | 5.8 | 8120.7 | 2026-09-22T14:13:55+00:00 |  |  | subscription (claude -p); see reported_cost_usd | backend=claude-code, prompt_id=leaning-v1, batch_order=shuffled, llm_seconds=8111.8, reported_cost_usd=56.5... |
| allotax | 7.0 | 11.9 | 2026-09-22T14:30:02+00:00 |  |  |  | alpha=0.3333, top_n=40, figures=5 |
| leaning_lexicon | 1.7 | 1.7 | 2026-09-15T18:52:59+00:00 |  |  |  | cutoff=1.96 |
| stage0b_creators | 0.3 | 0.3 | 2026-09-17T19:05:21+00:00 |  |  |  |  |
| stage6b_zipf_views | 2.3 | 2.7 | 2026-09-22T14:29:44+00:00 |  |  |  | zipf_systems=13, views_rows=244079 |


## Environment

```
# Political YouTube Title Stylometry - analysis stack (pipeline_titles/*.py).
#     python -m venv .venv && .venv/bin/pip install -r requirements.txt
#     .venv/bin/python -m spacy download en_core_web_sm    # 3.8.0 was used
# Pinned to the versions the 2026-09-14 run used (Python 3.14.2, Apple M4 Pro).
pandas==3.0.5
numpy==2.5.3
scipy==1.18.1
pyarrow==25.0.1
scikit-learn==1.9.1
statsmodels==0.15.0
matplotlib==3.11.2
torch==2.14.0
transformers==5.17.0
sentence-transformers==6.0.1
bertopic==0.17.4
umap-learn==0.5.12
hdbscan==0.8.44
factor_analyzer==0.5.1
spacy==3.8.16
vaderSentiment==3.3.2
powerlaw==2.0.0
# Corpus fetch (pipeline_titles/ingest): yt-dlp changes often, keep it recent.
yt-dlp>=2026.1.0
requests==2.34.2

```
