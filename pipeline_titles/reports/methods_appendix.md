# Title Stylometry: methods appendix

_Generated 2026-09-15T18:58:17+00:00._

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
                              vs normalised titles, plus the head of each rank list

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

### `pipeline_titles.annotate`

```
Stage 0c - spaCy annotation of every unique normalised title.

Runs en_core_web_sm (tagger, parser, NER) once over the unique `title_norm`
strings of titles_prepared.parquet and caches the result, so Stage 1 (entities per
topic), Stage 2 (POS-based style features, named-person / organisation counts) and
Stage 4 (who gets named) never re-run the model.

ALL-CAPS titles ("TRUMP DESTROYS CNN") defeat the NER, so they are truecased first
with a lexicon learned from the corpus itself: a word is a proper noun if it is
capitalised in >= 80 % of its non-initial occurrences in mixed-case titles (>= 3
occurrences), and an acronym if it is ALL-CAPS in >= 80 % of them. The truecased
text is stored beside the annotations (`text_tc`); every feature that depends on
capitalisation is computed from the original text, not from `text_tc`.

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
Stage 1a - sentence embeddings of every unique normalised title.

Encodes the unique `title_norm` strings of titles_prepared.parquet with a
sentence-transformers model (all-mpnet-base-v2, 768-d, L2-normalised) on the Mac
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
(Stage 0c, for the entities per topic) and lanes.csv. Writes, under
data/titles/analysis/:

    topics.csv                row_id, video_id, creator, genre, topic_id, topic_sim,
                              weak_assignment (all 309,596 rows; verbatim repeats get
                              the topic of their unique title)
    topic_labels.csv          topic_id, label (LLM), political, category, top_terms,
                              n_fit, n_unique_all, example_1..3, top_persons, top_orgs
    creator_topic_mix.csv     creator x genre x topic share (unique titles)
    topic_by_lane.csv         lane x genre x topic: mean of creator shares (+ raw pooled)
    topic_timeline.csv        month x topic: creator-balanced share and raw count
    topic_spikes.csv          per month, the topics that spike most vs. their own
                              mean, with the entities and example titles of that month
    creator_political_share.csv
    cache/topic_centroids.npy, cache/topic_fit_sample.parquet

Fit sample: from the creator-balanced subset, per creator x genre capped so that
the total is ~100,000 (cap found by bisection, seed 20260914). UMAP(15 neighbours,
5 dims, cosine, min_dist 0) -> HDBSCAN(min_cluster_size 80, min_samples 15, eom).
If HDBSCAN yields more than --max-topics topics they are merged to that number by
c-TF-IDF similarity. Outliers and all non-fit titles are assigned to the nearest
centroid (cosine); an assignment is 'weak' when its similarity is below the 10th
percentile of the similarities of HDBSCAN's own members.

CLI:
    python -m pipeline_titles.topics
    python -m pipeline_titles.topics --fit-size 100000 --min-cluster-size 80 --max-topics 250
    python -m pipeline_titles.topics --label-only        # re-run only the LLM labelling
```

### `pipeline_titles.llm_rate`

```
Stage 2c - LLM ratings of a stratified 3,000-title sample (plus a 300-title retest).

Draws the sample from titles_prepared.parquet (unique titles only; every creator x
genre gets a base allocation - 8 titles for groups with >= 50 titles, 2 for low-n
groups - and the remainder is spread in proportion to log10(n), seed 20260914),
rates each RAW title with a local Ollama model in batches of 20, and writes
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
    python -m pipeline_titles.llm_rate                     # full run (~1 h on qwen3:14b)
    python -m pipeline_titles.llm_rate --limit 60          # smoke test
    python -m pipeline_titles.llm_rate --model qwen3:30b --batch-size 20
```

### `pipeline_titles.features`

```
Stage 2a - title-level style features, aggregated to creator x genre x month.

Reads titles_prepared.parquet, annotations.parquet and lanes.csv. Writes:

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
the NORMALISED title (brand prefixes/suffixes, episode numbers and dates removed);
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
and lanes.csv. Writes, under data/titles/analysis/:

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
                             within genre (non-low-n creators), lane medians
    dimensions_title.parquet row_id, topic_id, raw and residual title-level scores
    dimensions_by_topic.csv  creator scores within the 5 largest shared topics
    topic_control_summary.csv  per factor: share of title-level and creator-level
                             variance explained by topic

Method. Cells with >= 15 unique titles enter the EFA (each creator x genre
contributes at most 9 monthly rows, so the matrix is creator-balanced by
construction). Features are the _p100 / _mean columns minus artefacts (see
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
    format_hook_shares.csv   creator x genre shares (unique titles) and lane x genre
                             means of creator shares (non-low-n creators)
    format_examples.csv      three examples per category per lane and corpus-wide
    hook_classifier.json     CV and hold-out metrics per hook
    format_agreement.csv     rule vs LLM format label on the rated sample
                             (precision / recall / F1 / Cohen's kappa per category)

CLI:
    python -m pipeline_titles.formats
```

### `pipeline_titles.landscape`

```
Stage 4 - the landscape: creators clustered in style space and in topic space,
compared with the lane assignment; nearest neighbours; who gets named; convergent
formulas.

Reads dimensions.csv / dimensions_title.parquet (Stage 2), topics.csv +
topic_labels.csv + creator_topic_mix.csv (Stage 1), formats.parquet (Stage 3),
annotations.parquet, titles_prepared.parquet and lanes.csv.

Every similarity is computed per genre over non-low-n creators, with cross-posted
titles removed (a title whose case-insensitive key also appears under another
creator of the same organisation, e.g. TYT / The Damage Report). The whole
clustering block runs twice: on all titles and on political titles only.

Outputs (data/titles/analysis/):
    style_clusters.csv, topic_clusters.csv     cluster id per creator x genre (all / political)
    cluster_comparison.csv                     adjusted Rand index: style vs lane, topic vs lane, style vs topic
    lane_style_cohesion.csv                    within-lane vs between-lane style distance per lane
    disagreements_lane_style.csv               lane-mates in different style clusters, and style-mates across lanes
    neighbours_style.csv, neighbours_topic.csv five nearest neighbours per creator x genre
    map_style.csv, map_topic.csv               2-D coordinates (PCA of style z-scores; MDS of topic JS distance)
    entities_top.csv                           top 25 people and organisations (creator-balanced counts), lanes
                                               naming them most, outrage-frame share vs overall
    shared_titles.csv, shared_templates.csv    verbatim titles / masked templates used by >= 2 creators
    org_style.csv                              organisation-level style scores (title-weighted mean of members)

CLI:
    python -m pipeline_titles.landscape
```

### `pipeline_titles.timeline`

```
Stage 5a - monthly drift, January to September 2026.

Reads dimensions_monthly.csv (Stage 2 cell scores), formats.parquet (Stage 3),
topics.csv, titles_prepared.parquet and lanes.csv. Months are the only safe time
unit (YouTube listing dates are month-accurate); September is 1-14 only and is
flagged partial_month = True everywhere - it is shown but its volume is never
compared with a full month.

Outputs (data/titles/analysis/):
    drift_lane_monthly.csv     lane x genre x month: mean of creator cell scores
                               (raw and topic-controlled), hook shares, n_creators
    drift_top30_monthly.csv    the 30 largest creators (unique titles): the same per
                               creator x genre x month (sparkline data for the cards)
    drift_creator_monthly.csv  every creator x genre x month (cards)
    topic_change_monthly.csv   month-to-month Jensen-Shannon distance between a
                               creator's consecutive monthly topic mixes; lane means
    drift_trends.csv           per lane x genre and per top-30 creator x genre: the
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
favours older videos; the month dummies absorb that within a creator, but
coefficients still describe views-to-date, not lifetime views.

Subscriber normalisation: log(views / subscribers) = log(views) - log(subscribers),
a constant within creator, so it leaves every slope unchanged; the standardised
coefficients are therefore already comparable across creators, and subscriber
count is reported beside them.

Rumble rows have no view count and are excluded here.

Outputs (data/titles/analysis/):
    engagement_coefficients.csv   creator x genre x predictor: coefficient, HC3 SE, p, n, R2
    engagement_summary.csv        across creators (per genre, and per lane): median,
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
discrete, xmin estimated by KS minimisation) with the log-likelihood-ratio test
against a lognormal (R > 0 favours the power law; p is the significance of R).
A tail is called power-law-like only when R > 0 and p < 0.05.

Then, within lane: Spearman correlations across creators between concentration
(Gini, top-10 % share) and the topic-controlled dimension scores and hook shares;
plus the same correlations with log(number of videos) and log(subscribers) as
the size-artefact check, and a pooled within-lane estimate (values demeaned by
lane x genre).

Outputs (data/titles/analysis/):
    hit_concentration.csv               per creator x genre (Gini, top shares, CSN fit, rank-size
                                        Zipf slope of views over all videos and over the top decile)
    hit_concentration_correlations.csv  within-lane and pooled-within-lane correlations

CLI:
    python -m pipeline_titles.hits
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

Cells: 2029 (>= 15 unique titles); features: 74; KMO 0.7254; Bartlett chi2 111975.4 p 0; parallel analysis 16, Kaiser 21, retained 12 (minres, oblimin); variance explained per factor [0.0534, 0.0478, 0.0472, 0.0456, 0.0448, 0.0428, 0.0424, 0.0371, 0.0336, 0.0319, 0.0245, 0.0233]; cumulative 0.4743.


Dropped features: `lowercase_start_p100` (prevalence 0.44 per 100 titles < 0.5); `percent_p100` (prevalence 0.31 per 100 titles < 0.5); `hashtag_p100` (prevalence 0.36 per 100 titles < 0.5); `at_mention_p100` (prevalence 0.14 per 100 titles < 0.5); `how_to_p100` (prevalence 0.39 per 100 titles < 0.5); `listicle_p100` (prevalence 0.03 per 100 titles < 0.5); `n_tokens_mean` (|r| = 0.983 with n_chars_mean)


Scree (eigenvalues vs parallel-analysis 95th percentile):

| component | eigenvalue | parallel_95th |
|---|---|---|
| 1 | 8.546 | 1.413 |
| 2 | 6.074 | 1.386 |
| 3 | 5.159 | 1.361 |
| 4 | 4.379 | 1.342 |
| 5 | 3.563 | 1.323 |
| 6 | 3.098 | 1.311 |
| 7 | 2.723 | 1.296 |
| 8 | 2.076 | 1.282 |
| 9 | 1.905 | 1.268 |
| 10 | 1.739 | 1.256 |
| 11 | 1.653 | 1.243 |
| 12 | 1.490 | 1.231 |
| 13 | 1.402 | 1.220 |
| 14 | 1.259 | 1.210 |
| 15 | 1.253 | 1.201 |
| 16 | 1.246 | 1.188 |
| 17 | 1.174 | 1.177 |
| 18 | 1.138 | 1.169 |
| 19 | 1.136 | 1.158 |
| 20 | 1.074 | 1.151 |


Full loadings (oblimin; varimax beside):

| feature | F1 | F2 | F3 | F4 | F5 | F6 | F7 | F8 | F9 | F10 | F11 | F12 | communality | F1_varimax | F2_varimax | F3_varimax | F4_varimax | F5_varimax | F6_varimax | F7_varimax | F8_varimax | F9_varimax | F10_varimax | F11_varimax | F12_varimax |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| n_chars_mean | -0.17 | 0.25 | 0.16 | 0.03 | -0.05 | 0.33 | 0.09 | 0.10 | -0.20 | 0.23 | 0.52 | 0.11 | 0.63 | -0.33 | 0.25 | -0.03 | 0.23 | 0.50 | 0.38 | 0.06 | 0.18 | 0.31 | -0.27 | 0.20 | 0.19 |
| mean_word_len_mean | -0.16 | -0.32 | -0.01 | -0.19 | -0.19 | 0.06 | 0.36 | -0.23 | -0.22 | -0.00 | 0.18 | -0.11 | 0.48 | -0.57 | 0.06 | -0.23 | 0.00 | 0.11 | 0.03 | -0.16 | -0.21 | 0.05 | -0.19 | -0.25 | 0.02 |
| allcaps_word_share_mean | -0.15 | -0.03 | 0.06 | -0.02 | -0.09 | 0.05 | 0.02 | 0.01 | 0.94 | -0.01 | 0.03 | -0.02 | 0.92 | 0.01 | 0.45 | -0.26 | 0.15 | -0.10 | -0.01 | -0.01 | -0.03 | -0.07 | 0.83 | -0.07 | -0.01 |
| has_allcaps_word_p100 | -0.33 | 0.01 | 0.29 | -0.01 | -0.20 | 0.04 | -0.15 | 0.00 | 0.44 | 0.03 | 0.19 | -0.15 | 0.51 | -0.04 | 0.58 | -0.31 | 0.34 | 0.08 | -0.07 | -0.03 | -0.00 | 0.03 | 0.34 | -0.12 | 0.01 |
| full_caps_title_p100 | 0.04 | 0.03 | -0.03 | -0.02 | -0.01 | 0.09 | 0.08 | 0.01 | 0.86 | -0.01 | -0.08 | 0.03 | 0.77 | 0.09 | 0.20 | -0.15 | 0.05 | -0.10 | 0.05 | -0.01 | -0.03 | -0.09 | 0.79 | -0.03 | -0.02 |
| cap_token_share_mean | -0.20 | -0.18 | -0.02 | -0.17 | -0.02 | 0.07 | -0.72 | -0.00 | 0.18 | -0.05 | -0.01 | 0.00 | 0.66 | 0.16 | 0.44 | 0.00 | -0.05 | 0.16 | -0.63 | -0.20 | 0.04 | -0.05 | 0.05 | 0.15 | -0.00 |
| q_mark_p100 | -0.01 | -0.00 | -0.02 | -0.04 | 0.46 | 0.09 | -0.10 | -0.01 | 0.04 | 0.08 | 0.05 | 0.10 | 0.25 | 0.05 | 0.01 | 0.45 | -0.04 | 0.07 | -0.02 | -0.03 | 0.01 | 0.08 | 0.00 | 0.18 | 0.06 |
| excl_p100 | -0.25 | -0.01 | -0.06 | 0.05 | -0.00 | -0.00 | -0.16 | -0.07 | 0.17 | -0.09 | 0.35 | -0.13 | 0.28 | -0.03 | 0.49 | -0.04 | -0.02 | 0.06 | -0.07 | 0.03 | -0.05 | -0.06 | 0.07 | -0.04 | 0.18 |
| multi_punct_p100 | -0.20 | 0.02 | -0.00 | 0.08 | 0.02 | -0.06 | -0.11 | -0.03 | 0.17 | -0.18 | 0.23 | -0.04 | 0.18 | 0.02 | 0.36 | -0.01 | 0.03 | -0.04 | -0.03 | 0.07 | -0.03 | -0.16 | 0.10 | 0.00 | 0.10 |
| colon_p100 | 0.01 | -0.04 | 0.79 | -0.11 | -0.02 | 0.01 | -0.01 | -0.02 | -0.04 | 0.17 | 0.02 | 0.10 | 0.68 | -0.16 | -0.10 | -0.07 | 0.78 | 0.09 | 0.04 | -0.05 | -0.00 | 0.18 | -0.04 | 0.05 | -0.02 |
| pipe_p100 | -0.05 | 0.13 | 0.16 | 0.00 | 0.04 | 0.29 | 0.12 | 0.23 | -0.00 | 0.05 | -0.03 | 0.20 | 0.24 | -0.17 | -0.07 | 0.01 | 0.18 | 0.26 | 0.19 | 0.02 | 0.24 | 0.08 | 0.01 | 0.14 | -0.16 |
| ellipsis_p100 | -0.07 | 0.08 | -0.03 | 0.71 | -0.08 | -0.02 | -0.03 | 0.02 | -0.03 | 0.12 | -0.10 | -0.20 | 0.59 | 0.30 | 0.09 | -0.09 | -0.05 | -0.04 | 0.00 | 0.65 | -0.01 | 0.11 | -0.02 | -0.18 | -0.08 |
| trailing_ellipsis_p100 | -0.01 | 0.04 | -0.05 | 0.82 | -0.06 | -0.02 | 0.04 | -0.01 | -0.07 | -0.02 | -0.08 | -0.16 | 0.73 | 0.28 | 0.01 | -0.06 | -0.07 | -0.08 | 0.02 | 0.76 | -0.04 | -0.03 | -0.04 | -0.19 | -0.07 |
| quotes_p100 | -0.00 | -0.02 | -0.01 | -0.08 | -0.02 | 0.01 | -0.00 | -0.00 | 0.01 | 0.91 | -0.02 | -0.07 | 0.84 | -0.04 | 0.01 | -0.01 | -0.02 | 0.14 | 0.10 | -0.03 | 0.04 | 0.87 | -0.04 | 0.04 | 0.05 |
| brackets_p100 | 0.14 | 0.14 | -0.05 | -0.01 | -0.09 | 0.11 | -0.17 | 0.08 | 0.00 | -0.04 | 0.09 | 0.04 | 0.11 | 0.11 | -0.01 | -0.03 | -0.02 | 0.14 | -0.01 | -0.03 | 0.11 | -0.04 | -0.03 | 0.12 | 0.11 |
| dash_p100 | 0.03 | 0.05 | -0.07 | -0.04 | 0.06 | 0.07 | -0.18 | 0.24 | 0.00 | 0.10 | 0.04 | -0.01 | 0.12 | 0.07 | 0.03 | 0.08 | -0.06 | 0.12 | -0.08 | -0.05 | 0.26 | 0.10 | -0.03 | 0.07 | 0.05 |
| emoji_p100 | -0.17 | 0.12 | 0.08 | 0.10 | -0.01 | 0.05 | -0.04 | 0.09 | 0.04 | 0.00 | 0.04 | -0.16 | 0.10 | 0.08 | 0.22 | -0.04 | 0.08 | 0.06 | 0.04 | 0.06 | 0.08 | 0.01 | 0.03 | -0.12 | -0.04 |
| digit_p100 | 0.05 | 0.02 | -0.01 | -0.02 | 0.04 | 0.00 | 0.02 | 0.85 | 0.01 | 0.09 | 0.05 | -0.00 | 0.73 | -0.13 | -0.12 | -0.00 | 0.03 | 0.04 | 0.03 | -0.01 | 0.84 | 0.10 | 0.00 | -0.03 | 0.02 |
| dollar_p100 | -0.02 | 0.06 | -0.09 | -0.03 | 0.03 | -0.02 | -0.01 | 0.17 | -0.04 | 0.08 | 0.07 | 0.02 | 0.06 | -0.02 | 0.02 | 0.04 | -0.08 | 0.01 | 0.06 | -0.02 | 0.18 | 0.09 | -0.05 | 0.05 | 0.04 |
| comma_p100 | 0.02 | 0.07 | -0.08 | 0.05 | -0.12 | 0.19 | 0.04 | 0.28 | 0.05 | 0.03 | 0.30 | 0.21 | 0.28 | -0.25 | 0.06 | -0.11 | 0.00 | 0.25 | 0.16 | 0.08 | 0.33 | 0.08 | -0.01 | 0.20 | 0.13 |
| period_end_p100 | 0.12 | 0.17 | -0.02 | 0.07 | -0.12 | -0.03 | -0.17 | -0.03 | -0.06 | 0.01 | -0.03 | -0.07 | 0.10 | 0.27 | -0.02 | -0.05 | -0.03 | 0.00 | -0.01 | 0.04 | -0.02 | -0.00 | -0.06 | 0.02 | 0.06 |
| year_mention_p100 | 0.07 | -0.01 | -0.01 | -0.02 | -0.02 | -0.02 | -0.01 | 0.68 | -0.03 | -0.09 | 0.04 | -0.04 | 0.48 | -0.08 | -0.12 | -0.04 | 0.02 | 0.01 | -0.04 | -0.03 | 0.66 | -0.08 | -0.03 | -0.08 | 0.04 |
| first_sg_p100 | 0.06 | 0.09 | 0.02 | 0.06 | 0.08 | -0.06 | -0.14 | -0.03 | 0.01 | 0.13 | -0.09 | -0.12 | 0.09 | 0.27 | -0.01 | 0.10 | -0.01 | -0.06 | -0.04 | 0.04 | -0.03 | 0.10 | 0.00 | -0.03 | 0.02 |
| first_pl_p100 | -0.13 | -0.11 | 0.01 | 0.53 | 0.00 | 0.03 | 0.13 | 0.02 | -0.05 | 0.16 | 0.00 | 0.42 | 0.53 | -0.20 | -0.05 | -0.00 | 0.01 | 0.03 | 0.11 | 0.60 | 0.04 | 0.20 | -0.04 | 0.29 | -0.16 |
| second_person_p100 | 0.14 | 0.06 | 0.03 | 0.00 | 0.11 | -0.18 | -0.27 | 0.08 | -0.01 | 0.29 | 0.17 | 0.09 | 0.27 | 0.17 | -0.01 | 0.17 | 0.04 | -0.05 | -0.04 | 0.04 | 0.13 | 0.27 | -0.08 | 0.23 | 0.25 |
| contraction_p100 | 0.09 | 0.15 | -0.09 | 0.65 | 0.06 | -0.04 | -0.25 | -0.05 | -0.04 | 0.13 | 0.05 | 0.15 | 0.57 | 0.38 | 0.01 | 0.14 | -0.09 | -0.01 | 0.01 | 0.64 | -0.02 | 0.12 | -0.07 | 0.26 | 0.09 |
| imperative_p100 | -0.01 | -0.24 | 0.28 | 0.55 | -0.04 | -0.00 | 0.07 | -0.05 | 0.07 | -0.10 | 0.11 | 0.12 | 0.48 | -0.14 | 0.00 | -0.10 | 0.30 | -0.02 | -0.07 | 0.57 | -0.04 | -0.08 | 0.06 | -0.01 | 0.02 |
| q_word_start_p100 | -0.02 | -0.08 | -0.02 | -0.06 | 0.95 | 0.01 | 0.09 | 0.01 | -0.00 | -0.02 | -0.05 | 0.05 | 0.93 | 0.05 | -0.17 | 0.90 | -0.08 | -0.11 | 0.02 | -0.06 | -0.01 | -0.03 | -0.00 | 0.10 | 0.02 |
| wh_any_p100 | -0.01 | 0.08 | -0.04 | 0.02 | 0.85 | 0.07 | -0.06 | 0.03 | -0.09 | -0.00 | 0.09 | -0.02 | 0.76 | 0.18 | -0.06 | 0.84 | -0.09 | 0.02 | 0.05 | -0.00 | 0.03 | -0.00 | -0.11 | 0.12 | 0.13 |
| intensifier_p100 | -0.02 | 0.33 | -0.08 | 0.13 | 0.17 | 0.00 | -0.18 | -0.04 | -0.02 | 0.03 | -0.05 | -0.20 | 0.24 | 0.45 | 0.12 | 0.21 | -0.11 | -0.01 | 0.07 | 0.05 | -0.06 | 0.01 | -0.03 | -0.03 | 0.02 |
| superlative_p100 | 0.10 | 0.09 | -0.10 | -0.02 | 0.14 | -0.10 | -0.02 | 0.03 | -0.05 | 0.16 | 0.15 | -0.17 | 0.14 | 0.12 | -0.01 | 0.17 | -0.09 | -0.04 | 0.09 | -0.04 | 0.05 | 0.14 | -0.07 | -0.06 | 0.22 |
| shock_word_p100 | -0.74 | 0.01 | 0.08 | 0.01 | 0.05 | -0.04 | -0.07 | -0.01 | 0.11 | 0.06 | 0.12 | 0.08 | 0.60 | -0.19 | 0.69 | -0.03 | 0.06 | 0.01 | 0.01 | 0.02 | -0.02 | 0.14 | 0.05 | 0.09 | -0.25 |
| pos_eval_p100 | 0.32 | -0.03 | -0.06 | -0.03 | 0.07 | -0.00 | -0.11 | -0.00 | 0.11 | 0.13 | 0.30 | -0.14 | 0.26 | 0.06 | -0.06 | 0.09 | 0.00 | 0.07 | -0.03 | -0.03 | 0.05 | 0.09 | 0.03 | -0.03 | 0.43 |
| neg_eval_p100 | -0.25 | 0.16 | -0.17 | -0.01 | -0.03 | 0.04 | -0.19 | -0.10 | 0.04 | 0.02 | 0.14 | -0.28 | 0.27 | 0.19 | 0.44 | -0.02 | -0.18 | 0.09 | -0.03 | -0.08 | -0.10 | 0.03 | -0.02 | -0.13 | 0.06 |
| negation_p100 | 0.12 | 0.33 | -0.11 | 0.06 | 0.01 | -0.10 | -0.41 | -0.02 | -0.06 | 0.17 | 0.10 | 0.20 | 0.39 | 0.40 | 0.05 | 0.15 | -0.11 | 0.01 | 0.03 | 0.07 | 0.03 | 0.16 | -0.12 | 0.41 | 0.16 |
| violence_verb_p100 | -0.64 | 0.09 | -0.12 | 0.03 | -0.11 | 0.09 | -0.08 | -0.04 | 0.04 | -0.07 | 0.16 | -0.13 | 0.51 | -0.10 | 0.71 | -0.15 | -0.13 | 0.14 | 0.00 | -0.01 | -0.05 | 0.01 | -0.01 | -0.07 | -0.18 |
| hedge_p100 | 0.00 | 0.15 | -0.06 | -0.08 | 0.02 | -0.01 | 0.11 | 0.10 | -0.07 | 0.15 | 0.07 | 0.25 | 0.15 | -0.10 | -0.08 | 0.05 | -0.05 | 0.03 | 0.25 | -0.03 | 0.12 | 0.18 | -0.06 | 0.25 | -0.00 |
| discourse_marker_p100 | -0.01 | -0.18 | -0.06 | 0.84 | -0.00 | -0.00 | 0.06 | -0.07 | 0.06 | -0.07 | 0.05 | 0.07 | 0.76 | 0.04 | 0.03 | -0.03 | -0.04 | -0.06 | -0.06 | 0.83 | -0.07 | -0.06 | 0.05 | -0.02 | 0.00 |
| nominalisation_p100 | 0.08 | -0.03 | 0.14 | -0.12 | -0.07 | 0.06 | 0.24 | -0.05 | -0.26 | 0.06 | 0.42 | 0.03 | 0.35 | -0.39 | -0.07 | -0.06 | 0.19 | 0.19 | 0.25 | -0.07 | 0.01 | 0.11 | -0.27 | 0.01 | 0.28 |
| n_person_p100 | 0.07 | 0.03 | -0.04 | 0.01 | 0.03 | 0.99 | -0.05 | -0.05 | 0.08 | 0.04 | 0.02 | -0.01 | 1.00 | -0.22 | 0.04 | -0.01 | 0.01 | 0.91 | -0.07 | -0.06 | 0.00 | 0.05 | 0.02 | 0.03 | -0.09 |
| n_org_p100 | -0.18 | -0.00 | 0.10 | 0.07 | -0.20 | 0.21 | 0.09 | 0.21 | -0.09 | -0.00 | 0.35 | 0.14 | 0.33 | -0.41 | 0.20 | -0.22 | 0.17 | 0.31 | 0.14 | 0.11 | 0.25 | 0.08 | -0.14 | 0.10 | 0.05 |
| n_gpe_p100 | -0.18 | 0.02 | 0.10 | -0.03 | -0.03 | 0.02 | 0.45 | 0.05 | -0.11 | 0.21 | 0.04 | 0.34 | 0.42 | -0.45 | -0.10 | -0.07 | 0.11 | 0.02 | 0.41 | 0.07 | 0.06 | 0.27 | -0.06 | 0.19 | -0.18 |
| has_person_p100 | 0.07 | -0.01 | -0.01 | -0.04 | 0.02 | 0.94 | -0.05 | -0.07 | 0.03 | 0.02 | -0.01 | -0.02 | 0.90 | -0.24 | 0.02 | -0.01 | 0.03 | 0.87 | -0.10 | -0.10 | -0.02 | 0.03 | -0.01 | 0.01 | -0.11 |
| entity_first_p100 | -0.18 | -0.05 | -0.59 | -0.18 | -0.29 | 0.28 | -0.01 | 0.09 | -0.14 | -0.11 | -0.05 | 0.12 | 0.63 | -0.25 | 0.14 | -0.24 | -0.58 | 0.28 | -0.10 | -0.19 | 0.11 | -0.05 | -0.13 | 0.10 | -0.20 |
| explainer_p100 | 0.01 | 0.07 | -0.07 | 0.03 | 0.37 | 0.15 | -0.08 | 0.00 | -0.09 | 0.02 | 0.12 | -0.11 | 0.22 | 0.09 | 0.03 | 0.38 | -0.08 | 0.16 | 0.01 | -0.01 | 0.02 | 0.02 | -0.12 | 0.01 | 0.13 |
| why_marker_p100 | -0.12 | -0.04 | 0.01 | -0.04 | 0.79 | 0.04 | 0.04 | 0.01 | -0.04 | -0.03 | -0.06 | -0.02 | 0.64 | 0.06 | -0.05 | 0.73 | -0.05 | -0.05 | -0.01 | -0.06 | -0.02 | -0.03 | -0.04 | 0.03 | -0.04 |
| curiosity_lex_p100 | -0.40 | 0.15 | -0.02 | 0.07 | 0.25 | 0.01 | -0.20 | -0.01 | 0.02 | -0.05 | 0.18 | -0.11 | 0.34 | 0.14 | 0.48 | 0.23 | -0.04 | 0.05 | -0.01 | 0.02 | -0.01 | -0.01 | -0.05 | 0.03 | -0.00 |
| fwd_ref_start_p100 | 0.19 | 0.18 | -0.12 | 0.08 | -0.05 | -0.26 | -0.24 | -0.06 | 0.14 | -0.07 | -0.18 | -0.09 | 0.29 | 0.52 | -0.06 | 0.01 | -0.14 | -0.30 | -0.09 | 0.05 | -0.08 | -0.13 | 0.15 | 0.00 | 0.04 |
| reaction_lex_p100 | 0.06 | 0.06 | -0.03 | 0.00 | -0.01 | 0.12 | -0.04 | -0.01 | -0.01 | 0.07 | 0.04 | -0.14 | 0.05 | 0.06 | 0.02 | -0.00 | -0.02 | 0.13 | 0.01 | -0.03 | 0.00 | 0.06 | -0.03 | -0.08 | 0.07 |
| interview_lex_p100 | 0.15 | -0.10 | 0.01 | 0.15 | 0.21 | 0.39 | 0.01 | -0.04 | -0.06 | -0.04 | 0.13 | 0.02 | 0.28 | -0.14 | -0.11 | 0.20 | 0.04 | 0.37 | -0.06 | 0.14 | -0.00 | -0.03 | -0.09 | 0.02 | 0.11 |
| confrontation_lex_p100 | 0.02 | -0.02 | -0.06 | -0.02 | 0.02 | 0.22 | -0.05 | -0.02 | 0.02 | 0.12 | 0.06 | -0.14 | 0.09 | -0.03 | 0.07 | 0.01 | -0.05 | 0.24 | -0.05 | -0.05 | 0.00 | 0.11 | -0.01 | -0.09 | 0.06 |
| lead_colon_label_p100 | -0.01 | -0.00 | 0.85 | -0.07 | -0.08 | -0.05 | -0.04 | -0.04 | 0.05 | -0.03 | 0.03 | -0.04 | 0.75 | -0.05 | -0.00 | -0.14 | 0.85 | 0.00 | -0.01 | -0.05 | -0.04 | -0.04 | 0.05 | -0.09 | 0.01 |
| lead_breaking_p100 | -0.22 | -0.03 | 0.26 | -0.03 | -0.00 | -0.12 | -0.02 | -0.04 | 0.02 | -0.01 | 0.08 | -0.02 | 0.14 | -0.07 | 0.20 | -0.04 | 0.25 | -0.07 | -0.01 | -0.02 | -0.05 | 0.01 | 0.00 | -0.03 | -0.03 |
| lead_live_p100 | 0.12 | 0.02 | 0.82 | -0.04 | -0.10 | 0.04 | 0.05 | -0.03 | -0.00 | -0.10 | -0.05 | -0.05 | 0.72 | -0.04 | -0.17 | -0.15 | 0.82 | 0.04 | 0.04 | -0.03 | -0.04 | -0.11 | 0.03 | -0.13 | -0.03 |
| episode_raw_p100 | 0.05 | -0.14 | 0.02 | 0.01 | 0.02 | -0.02 | -0.09 | -0.03 | 0.08 | -0.00 | -0.08 | -0.04 | 0.05 | 0.04 | -0.03 | 0.01 | 0.01 | -0.04 | -0.18 | 0.00 | -0.04 | -0.03 | 0.07 | -0.05 | -0.00 |
| date_raw_p100 | 0.18 | -0.15 | 0.16 | -0.03 | -0.06 | -0.07 | -0.13 | 0.23 | 0.09 | -0.12 | 0.22 | 0.03 | 0.23 | -0.11 | -0.04 | -0.07 | 0.22 | -0.00 | -0.15 | -0.00 | 0.26 | -0.12 | 0.04 | 0.01 | 0.25 |
| quoted_speech_p100 | -0.01 | -0.04 | 0.03 | 0.10 | -0.02 | 0.02 | 0.01 | -0.00 | 0.01 | 0.93 | -0.02 | 0.04 | 0.87 | -0.07 | -0.01 | -0.02 | 0.02 | 0.14 | 0.11 | 0.16 | 0.05 | 0.90 | -0.04 | 0.12 | 0.03 |
| has_finite_verb_p100 | -0.07 | 0.91 | -0.02 | -0.09 | 0.07 | 0.01 | 0.09 | -0.07 | 0.01 | 0.01 | 0.01 | 0.07 | 0.86 | 0.50 | 0.11 | 0.16 | -0.03 | -0.04 | 0.71 | -0.13 | -0.10 | 0.03 | 0.05 | 0.27 | -0.08 |
| past_tense_p100 | -0.12 | 0.54 | -0.19 | 0.09 | -0.04 | 0.01 | -0.12 | -0.01 | 0.04 | 0.12 | 0.03 | -0.08 | 0.39 | 0.43 | 0.26 | 0.02 | -0.19 | 0.02 | 0.30 | 0.04 | -0.02 | 0.13 | 0.02 | 0.12 | -0.02 |
| present_tense_p100 | -0.08 | 0.74 | 0.08 | -0.12 | 0.00 | 0.01 | 0.25 | -0.06 | -0.04 | -0.02 | 0.07 | 0.04 | 0.65 | 0.26 | 0.06 | 0.05 | 0.09 | -0.03 | 0.71 | -0.14 | -0.09 | 0.01 | 0.01 | 0.15 | -0.06 |
| modal_p100 | 0.10 | 0.25 | -0.12 | -0.09 | 0.19 | -0.08 | -0.24 | -0.08 | -0.02 | 0.07 | 0.03 | 0.53 | 0.48 | 0.18 | -0.10 | 0.31 | -0.13 | -0.04 | 0.12 | -0.02 | -0.03 | 0.08 | -0.05 | 0.64 | 0.04 |
| future_will_p100 | 0.03 | 0.13 | -0.06 | -0.12 | 0.04 | -0.03 | -0.13 | -0.07 | 0.00 | -0.01 | -0.03 | 0.54 | 0.35 | 0.01 | -0.10 | 0.12 | -0.06 | -0.02 | 0.08 | -0.04 | -0.03 | 0.02 | -0.00 | 0.55 | -0.07 |
| det_share_mean | 0.34 | 0.08 | -0.07 | 0.02 | 0.29 | -0.20 | -0.30 | -0.10 | -0.14 | -0.08 | 0.01 | -0.00 | 0.38 | 0.41 | -0.25 | 0.40 | -0.10 | -0.17 | -0.14 | 0.00 | -0.07 | -0.12 | -0.15 | 0.15 | 0.25 |
| stopword_share_mean | 0.25 | 0.38 | 0.22 | 0.15 | 0.28 | -0.23 | -0.26 | -0.17 | 0.01 | -0.12 | -0.07 | 0.01 | 0.51 | 0.64 | -0.15 | 0.36 | 0.18 | -0.26 | 0.09 | 0.12 | -0.18 | -0.17 | 0.02 | 0.17 | 0.13 |
| propn_share_mean | -0.18 | -0.48 | 0.04 | -0.22 | -0.11 | 0.33 | -0.37 | -0.05 | -0.25 | -0.02 | -0.04 | -0.01 | 0.63 | -0.35 | 0.15 | -0.10 | -0.00 | 0.44 | -0.62 | -0.23 | 0.01 | 0.02 | -0.29 | -0.02 | -0.11 |
| noun_share_mean | 0.08 | 0.14 | 0.02 | -0.06 | -0.05 | -0.09 | 0.81 | -0.01 | 0.16 | -0.01 | 0.01 | 0.02 | 0.73 | -0.30 | -0.26 | -0.15 | 0.08 | -0.24 | 0.65 | -0.01 | -0.07 | -0.01 | 0.26 | -0.19 | -0.05 |
| verb_share_mean | 0.09 | 0.51 | -0.19 | 0.17 | -0.03 | -0.26 | -0.01 | -0.20 | 0.15 | -0.12 | -0.19 | 0.17 | 0.55 | 0.57 | -0.04 | 0.06 | -0.21 | -0.37 | 0.33 | 0.16 | -0.24 | -0.15 | 0.20 | 0.24 | -0.10 |
| adj_share_mean | 0.16 | 0.12 | -0.08 | -0.08 | 0.01 | -0.25 | 0.52 | -0.09 | 0.27 | 0.10 | 0.03 | -0.07 | 0.48 | -0.04 | -0.17 | -0.05 | -0.04 | -0.35 | 0.46 | -0.04 | -0.14 | 0.06 | 0.31 | -0.16 | 0.11 |
| adv_share_mean | -0.01 | 0.46 | 0.39 | 0.14 | -0.03 | -0.01 | -0.09 | 0.05 | 0.06 | -0.12 | -0.26 | -0.16 | 0.51 | 0.51 | 0.01 | -0.03 | 0.35 | -0.09 | 0.17 | 0.06 | -0.01 | -0.15 | 0.12 | -0.10 | -0.20 |
| num_share_mean | 0.02 | -0.02 | -0.07 | -0.02 | 0.02 | -0.14 | -0.05 | 0.95 | 0.03 | -0.03 | -0.07 | -0.03 | 0.95 | -0.03 | -0.13 | -0.02 | -0.04 | -0.12 | -0.09 | -0.03 | 0.92 | -0.03 | 0.05 | -0.08 | -0.05 |
| vader_neg_mean | -0.76 | -0.04 | -0.20 | -0.02 | -0.02 | -0.21 | -0.07 | -0.13 | 0.17 | -0.01 | 0.04 | -0.06 | 0.72 | -0.06 | 0.76 | -0.09 | -0.24 | -0.19 | -0.07 | -0.03 | -0.17 | 0.05 | 0.13 | -0.04 | -0.25 |
| vader_pos_mean | 0.47 | -0.11 | -0.12 | -0.08 | 0.05 | -0.15 | -0.07 | -0.06 | 0.08 | 0.01 | 0.53 | -0.07 | 0.57 | -0.04 | -0.13 | 0.10 | -0.03 | -0.03 | -0.01 | -0.05 | 0.01 | -0.02 | -0.01 | 0.03 | 0.66 |
| vader_compound_mean | 0.91 | -0.05 | 0.06 | -0.02 | 0.00 | 0.03 | 0.03 | 0.05 | -0.05 | -0.06 | 0.12 | -0.01 | 0.86 | 0.11 | -0.74 | 0.09 | 0.13 | 0.03 | -0.00 | 0.00 | 0.09 | -0.14 | -0.04 | -0.00 | 0.50 |
| formulaic_p100 | -0.02 | -0.17 | 0.48 | 0.17 | -0.05 | 0.21 | 0.11 | 0.23 | 0.05 | -0.15 | 0.12 | 0.17 | 0.47 | -0.36 | -0.05 | -0.14 | 0.53 | 0.21 | -0.02 | 0.21 | 0.24 | -0.12 | 0.04 | 0.01 | -0.04 |


## Validation

| candidate | llm_column | best_factor | factor_auto_name | creator_level_r | second_factor | second_r | verdict | merged_with |
|---|---|---|---|---|---|---|---|---|
| Sensational | sensational | F1 | +vader_compound -vader_neg -shock_word -violence_verb | -0.711 | F5 | -0.329 | merged: Sensational, Critical, Analytical/Informational | Sensational, Critical, Analytical/Informational |
| Critical | critical | F1 | +vader_compound -vader_neg -shock_word -violence_verb | -0.489 | F5 | -0.182 | merged: Sensational, Critical, Analytical/Informational | Sensational, Critical, Analytical/Informational |
| Analytical/Informational | analytical | F1 | +vader_compound -vader_neg -shock_word -violence_verb | 0.433 | F5 | 0.425 | merged: Sensational, Critical, Analytical/Informational | Sensational, Critical, Analytical/Informational |
| Educational | educational | F5 | +q_word_start +wh_any +why_marker +q_mark | 0.392 | F1 | 0.320 | partial |  |
| Conversational | conversational | F4 | +discourse_marker +trailing_ellipsis +ellipsis +contraction | 0.177 | F1 | 0.170 | absent |  |
| Humor | humor | F2 | +has_finite_verb +present_tense +past_tense +verb_share | 0.082 | F4 | 0.063 | absent |  |

| dimension | n | exact_agreement | within_1 | spearman_r | weighted_kappa | kappa |
|---|---|---|---|---|---|---|
| sensational | 300 | 0.623 | 0.783 | 0.743 | 0.742 |  |
| critical | 300 | 0.713 | 0.753 | 0.580 | 0.581 |  |
| analytical | 300 | 0.583 | 0.773 | 0.600 | 0.561 |  |
| educational | 300 | 0.823 | 0.953 | 0.268 | 0.251 |  |
| conversational | 300 | 0.903 | 0.947 | 0.518 | 0.659 |  |
| humor | 300 | 0.993 |  |  |  | 0.000 |
| curiosity_gap | 300 | 0.980 |  |  |  | 0.490 |
| outrage | 300 | 0.757 |  |  |  | 0.497 |
| format_llm | 300 | 0.797 |  |  |  | 0.591 |

| llm | factor | factor_auto_name | score | spearman_r | pearson_r | p | n_groups |
|---|---|---|---|---|---|---|---|
| sensational | F1 | +vader_compound -vader_neg -shock_word -violence_verb | raw | -0.711 | -0.725 | 0.000 | 318 |
| sensational | F1 | +vader_compound -vader_neg -shock_word -violence_verb | controlled | -0.645 | -0.670 | 0.000 | 318 |
| sensational | F2 | +has_finite_verb +present_tense +past_tense +verb_share | raw | 0.109 | 0.154 | 0.053 | 318 |
| sensational | F2 | +has_finite_verb +present_tense +past_tense +verb_share | controlled | 0.073 | 0.101 | 0.197 | 318 |
| sensational | F3 | +lead_colon_label +lead_live +colon -entity_first | raw | -0.152 | -0.072 | 0.007 | 318 |
| sensational | F3 | +lead_colon_label +lead_live +colon -entity_first | controlled | -0.051 | -0.005 | 0.361 | 318 |
| sensational | F4 | +discourse_marker +trailing_ellipsis +ellipsis +contraction | raw | 0.152 | 0.047 | 0.007 | 318 |
| sensational | F4 | +discourse_marker +trailing_ellipsis +ellipsis +contraction | controlled | 0.010 | -0.021 | 0.856 | 318 |
| sensational | F5 | +q_word_start +wh_any +why_marker +q_mark | raw | -0.329 | -0.341 | 0.000 | 318 |
| sensational | F5 | +q_word_start +wh_any +why_marker +q_mark | controlled | -0.323 | -0.325 | 0.000 | 318 |
| sensational | F6 | +n_person +has_person | raw | 0.082 | 0.121 | 0.143 | 318 |
| sensational | F6 | +n_person +has_person | controlled | 0.072 | 0.114 | 0.201 | 318 |
| sensational | F7 | +noun_share -cap_token_share +adj_share +n_gpe | raw | -0.051 | -0.200 | 0.361 | 318 |
| sensational | F7 | +noun_share -cap_token_share +adj_share +n_gpe | controlled | -0.080 | -0.167 | 0.156 | 318 |
| sensational | F8 | +num_share +digit +year_mention | raw | -0.212 | -0.167 | 0.000 | 318 |
| sensational | F8 | +num_share +digit +year_mention | controlled | -0.013 | -0.039 | 0.825 | 318 |
| sensational | F9 | +allcaps_word_share +full_caps_title +has_allcaps_word | raw | 0.306 | 0.434 | 0.000 | 318 |
| sensational | F9 | +allcaps_word_share +full_caps_title +has_allcaps_word | controlled | 0.228 | 0.386 | 0.000 | 318 |
| sensational | F10 | +quoted_speech +quotes | raw | -0.043 | 0.009 | 0.449 | 318 |
| sensational | F10 | +quoted_speech +quotes | controlled | -0.019 | 0.025 | 0.737 | 318 |
| sensational | F11 | +vader_pos +n_chars +nominalisation | raw | 0.065 | 0.095 | 0.246 | 318 |
| sensational | F11 | +vader_pos +n_chars +nominalisation | controlled | 0.131 | 0.152 | 0.020 | 318 |
| sensational | F12 | +future_will +modal +first_pl | raw | -0.198 | -0.148 | 0.000 | 318 |
| sensational | F12 | +future_will +modal +first_pl | controlled | -0.206 | -0.192 | 0.000 | 318 |
| critical | F1 | +vader_compound -vader_neg -shock_word -violence_verb | raw | -0.489 | -0.508 | 0.000 | 318 |
| critical | F1 | +vader_compound -vader_neg -shock_word -violence_verb | controlled | -0.385 | -0.428 | 0.000 | 318 |
| critical | F2 | +has_finite_verb +present_tense +past_tense +verb_share | raw | 0.073 | 0.103 | 0.194 | 318 |
| critical | F2 | +has_finite_verb +present_tense +past_tense +verb_share | controlled | 0.047 | 0.068 | 0.404 | 318 |
| critical | F3 | +lead_colon_label +lead_live +colon -entity_first | raw | -0.176 | -0.172 | 0.002 | 318 |
| critical | F3 | +lead_colon_label +lead_live +colon -entity_first | controlled | -0.093 | -0.117 | 0.097 | 318 |
| critical | F4 | +discourse_marker +trailing_ellipsis +ellipsis +contraction | raw | 0.048 | -0.023 | 0.392 | 318 |
| critical | F4 | +discourse_marker +trailing_ellipsis +ellipsis +contraction | controlled | -0.046 | -0.058 | 0.408 | 318 |
| critical | F5 | +q_word_start +wh_any +why_marker +q_mark | raw | -0.182 | -0.211 | 0.001 | 318 |
| critical | F5 | +q_word_start +wh_any +why_marker +q_mark | controlled | -0.192 | -0.203 | 0.001 | 318 |
| critical | F6 | +n_person +has_person | raw | 0.094 | 0.151 | 0.093 | 318 |
| critical | F6 | +n_person +has_person | controlled | 0.111 | 0.167 | 0.049 | 318 |
| critical | F7 | +noun_share -cap_token_share +adj_share +n_gpe | raw | -0.092 | -0.156 | 0.103 | 318 |
| critical | F7 | +noun_share -cap_token_share +adj_share +n_gpe | controlled | -0.097 | -0.123 | 0.085 | 318 |
| critical | F8 | +num_share +digit +year_mention | raw | -0.144 | -0.123 | 0.010 | 318 |
| critical | F8 | +num_share +digit +year_mention | controlled | 0.022 | 0.013 | 0.691 | 318 |
| critical | F9 | +allcaps_word_share +full_caps_title +has_allcaps_word | raw | 0.071 | 0.120 | 0.205 | 318 |
| critical | F9 | +allcaps_word_share +full_caps_title +has_allcaps_word | controlled | -0.005 | 0.081 | 0.925 | 318 |
| critical | F10 | +quoted_speech +quotes | raw | 0.053 | 0.075 | 0.344 | 318 |
| critical | F10 | +quoted_speech +quotes | controlled | 0.022 | 0.074 | 0.696 | 318 |
| critical | F11 | +vader_pos +n_chars +nominalisation | raw | 0.058 | 0.095 | 0.299 | 318 |
| critical | F11 | +vader_pos +n_chars +nominalisation | controlled | 0.077 | 0.100 | 0.172 | 318 |
| critical | F12 | +future_will +modal +first_pl | raw | -0.134 | -0.076 | 0.017 | 318 |
| critical | F12 | +future_will +modal +first_pl | controlled | -0.141 | -0.099 | 0.012 | 318 |
| analytical | F1 | +vader_compound -vader_neg -shock_word -violence_verb | raw | 0.433 | 0.440 | 0.000 | 318 |
| analytical | F1 | +vader_compound -vader_neg -shock_word -violence_verb | controlled | 0.470 | 0.449 | 0.000 | 318 |
| analytical | F2 | +has_finite_verb +present_tense +past_tense +verb_share | raw | -0.002 | -0.010 | 0.977 | 318 |
| analytical | F2 | +has_finite_verb +present_tense +past_tense +verb_share | controlled | 0.018 | 0.012 | 0.745 | 318 |
| analytical | F3 | +lead_colon_label +lead_live +colon -entity_first | raw | 0.207 | 0.096 | 0.000 | 318 |
| analytical | F3 | +lead_colon_label +lead_live +colon -entity_first | controlled | 0.044 | 0.028 | 0.430 | 318 |
| analytical | F4 | +discourse_marker +trailing_ellipsis +ellipsis +contraction | raw | -0.134 | -0.034 | 0.017 | 318 |
| analytical | F4 | +discourse_marker +trailing_ellipsis +ellipsis +contraction | controlled | -0.034 | 0.028 | 0.541 | 318 |
| analytical | F5 | +q_word_start +wh_any +why_marker +q_mark | raw | 0.425 | 0.432 | 0.000 | 318 |
| analytical | F5 | +q_word_start +wh_any +why_marker +q_mark | controlled | 0.428 | 0.436 | 0.000 | 318 |
| analytical | F6 | +n_person +has_person | raw | 0.012 | -0.044 | 0.827 | 318 |
| analytical | F6 | +n_person +has_person | controlled | 0.034 | -0.020 | 0.548 | 318 |
| analytical | F7 | +noun_share -cap_token_share +adj_share +n_gpe | raw | 0.012 | 0.155 | 0.825 | 318 |
| analytical | F7 | +noun_share -cap_token_share +adj_share +n_gpe | controlled | -0.099 | 0.047 | 0.077 | 318 |
| analytical | F8 | +num_share +digit +year_mention | raw | 0.180 | 0.025 | 0.001 | 318 |
| analytical | F8 | +num_share +digit +year_mention | controlled | 0.004 | -0.052 | 0.945 | 318 |
| analytical | F9 | +allcaps_word_share +full_caps_title +has_allcaps_word | raw | -0.265 | -0.318 | 0.000 | 318 |
| analytical | F9 | +allcaps_word_share +full_caps_title +has_allcaps_word | controlled | -0.159 | -0.258 | 0.004 | 318 |
| analytical | F10 | +quoted_speech +quotes | raw | 0.230 | 0.146 | 0.000 | 318 |
| analytical | F10 | +quoted_speech +quotes | controlled | 0.092 | 0.065 | 0.103 | 318 |
| analytical | F11 | +vader_pos +n_chars +nominalisation | raw | 0.106 | 0.124 | 0.059 | 318 |
| analytical | F11 | +vader_pos +n_chars +nominalisation | controlled | 0.016 | 0.031 | 0.778 | 318 |
| analytical | F12 | +future_will +modal +first_pl | raw | 0.377 | 0.316 | 0.000 | 318 |
| analytical | F12 | +future_will +modal +first_pl | controlled | 0.268 | 0.244 | 0.000 | 318 |
| educational | F1 | +vader_compound -vader_neg -shock_word -violence_verb | raw | 0.320 | 0.344 | 0.000 | 318 |
| educational | F1 | +vader_compound -vader_neg -shock_word -violence_verb | controlled | 0.353 | 0.333 | 0.000 | 318 |
| educational | F2 | +has_finite_verb +present_tense +past_tense +verb_share | raw | 0.022 | -0.009 | 0.701 | 318 |
| educational | F2 | +has_finite_verb +present_tense +past_tense +verb_share | controlled | 0.023 | -0.003 | 0.684 | 318 |
| educational | F3 | +lead_colon_label +lead_live +colon -entity_first | raw | 0.033 | -0.033 | 0.555 | 318 |
| educational | F3 | +lead_colon_label +lead_live +colon -entity_first | controlled | -0.014 | -0.049 | 0.799 | 318 |
| educational | F4 | +discourse_marker +trailing_ellipsis +ellipsis +contraction | raw | 0.009 | 0.071 | 0.877 | 318 |
| educational | F4 | +discourse_marker +trailing_ellipsis +ellipsis +contraction | controlled | 0.069 | 0.110 | 0.219 | 318 |
| educational | F5 | +q_word_start +wh_any +why_marker +q_mark | raw | 0.392 | 0.422 | 0.000 | 318 |
| educational | F5 | +q_word_start +wh_any +why_marker +q_mark | controlled | 0.374 | 0.405 | 0.000 | 318 |
| educational | F6 | +n_person +has_person | raw | -0.110 | -0.118 | 0.050 | 318 |
| educational | F6 | +n_person +has_person | controlled | -0.073 | -0.084 | 0.194 | 318 |
| educational | F7 | +noun_share -cap_token_share +adj_share +n_gpe | raw | -0.049 | 0.061 | 0.389 | 318 |
| educational | F7 | +noun_share -cap_token_share +adj_share +n_gpe | controlled | -0.112 | 0.023 | 0.045 | 318 |
| educational | F8 | +num_share +digit +year_mention | raw | 0.056 | 0.040 | 0.316 | 318 |
| educational | F8 | +num_share +digit +year_mention | controlled | -0.045 | 0.015 | 0.422 | 318 |
| educational | F9 | +allcaps_word_share +full_caps_title +has_allcaps_word | raw | -0.062 | -0.125 | 0.273 | 318 |
| educational | F9 | +allcaps_word_share +full_caps_title +has_allcaps_word | controlled | -0.034 | -0.098 | 0.547 | 318 |
| educational | F10 | +quoted_speech +quotes | raw | 0.131 | 0.065 | 0.019 | 318 |
| educational | F10 | +quoted_speech +quotes | controlled | 0.062 | 0.038 | 0.270 | 318 |
| educational | F11 | +vader_pos +n_chars +nominalisation | raw | 0.053 | 0.070 | 0.347 | 318 |
| educational | F11 | +vader_pos +n_chars +nominalisation | controlled | -0.001 | 0.015 | 0.982 | 318 |
| educational | F12 | +future_will +modal +first_pl | raw | 0.166 | 0.132 | 0.003 | 318 |
| educational | F12 | +future_will +modal +first_pl | controlled | 0.118 | 0.107 | 0.036 | 318 |
| conversational | F1 | +vader_compound -vader_neg -shock_word -violence_verb | raw | 0.170 | 0.186 | 0.002 | 318 |
| conversational | F1 | +vader_compound -vader_neg -shock_word -violence_verb | controlled | 0.150 | 0.184 | 0.007 | 318 |
| conversational | F2 | +has_finite_verb +present_tense +past_tense +verb_share | raw | 0.072 | 0.029 | 0.200 | 318 |
| conversational | F2 | +has_finite_verb +present_tense +past_tense +verb_share | controlled | 0.043 | -0.026 | 0.441 | 318 |
| conversational | F3 | +lead_colon_label +lead_live +colon -entity_first | raw | -0.087 | -0.075 | 0.123 | 318 |
| conversational | F3 | +lead_colon_label +lead_live +colon -entity_first | controlled | 0.003 | -0.050 | 0.955 | 318 |
| conversational | F4 | +discourse_marker +trailing_ellipsis +ellipsis +contraction | raw | 0.177 | 0.623 | 0.002 | 318 |
| conversational | F4 | +discourse_marker +trailing_ellipsis +ellipsis +contraction | controlled | 0.175 | 0.612 | 0.002 | 318 |
| conversational | F5 | +q_word_start +wh_any +why_marker +q_mark | raw | 0.116 | 0.044 | 0.038 | 318 |
| conversational | F5 | +q_word_start +wh_any +why_marker +q_mark | controlled | 0.082 | 0.019 | 0.143 | 318 |
| conversational | F6 | +n_person +has_person | raw | -0.142 | -0.158 | 0.011 | 318 |
| conversational | F6 | +n_person +has_person | controlled | -0.120 | -0.122 | 0.032 | 318 |
| conversational | F7 | +noun_share -cap_token_share +adj_share +n_gpe | raw | 0.002 | 0.004 | 0.978 | 318 |
| conversational | F7 | +noun_share -cap_token_share +adj_share +n_gpe | controlled | 0.058 | 0.062 | 0.302 | 318 |
| conversational | F8 | +num_share +digit +year_mention | raw | -0.084 | 0.017 | 0.136 | 318 |
| conversational | F8 | +num_share +digit +year_mention | controlled | -0.049 | 0.001 | 0.381 | 318 |
| conversational | F9 | +allcaps_word_share +full_caps_title +has_allcaps_word | raw | 0.009 | -0.012 | 0.875 | 318 |
| conversational | F9 | +allcaps_word_share +full_caps_title +has_allcaps_word | controlled | -0.031 | -0.038 | 0.585 | 318 |
| conversational | F10 | +quoted_speech +quotes | raw | -0.021 | -0.033 | 0.704 | 318 |
| conversational | F10 | +quoted_speech +quotes | controlled | 0.015 | 0.004 | 0.792 | 318 |
| conversational | F11 | +vader_pos +n_chars +nominalisation | raw | -0.016 | 0.014 | 0.773 | 318 |
| conversational | F11 | +vader_pos +n_chars +nominalisation | controlled | 0.001 | 0.072 | 0.988 | 318 |
| conversational | F12 | +future_will +modal +first_pl | raw | -0.046 | 0.039 | 0.416 | 318 |
| conversational | F12 | +future_will +modal +first_pl | controlled | -0.011 | 0.109 | 0.852 | 318 |
| humor | F1 | +vader_compound -vader_neg -shock_word -violence_verb | raw | -0.021 | 0.005 | 0.716 | 318 |
| humor | F1 | +vader_compound -vader_neg -shock_word -violence_verb | controlled | -0.022 | 0.000 | 0.698 | 318 |
| humor | F2 | +has_finite_verb +present_tense +past_tense +verb_share | raw | 0.082 | 0.062 | 0.143 | 318 |
| humor | F2 | +has_finite_verb +present_tense +past_tense +verb_share | controlled | 0.063 | 0.057 | 0.260 | 318 |
| humor | F3 | +lead_colon_label +lead_live +colon -entity_first | raw | -0.057 | -0.043 | 0.313 | 318 |
| humor | F3 | +lead_colon_label +lead_live +colon -entity_first | controlled | -0.030 | -0.040 | 0.598 | 318 |
| humor | F4 | +discourse_marker +trailing_ellipsis +ellipsis +contraction | raw | 0.063 | 0.017 | 0.266 | 318 |
| humor | F4 | +discourse_marker +trailing_ellipsis +ellipsis +contraction | controlled | 0.039 | 0.015 | 0.487 | 318 |
| humor | F5 | +q_word_start +wh_any +why_marker +q_mark | raw | -0.035 | -0.004 | 0.528 | 318 |
| humor | F5 | +q_word_start +wh_any +why_marker +q_mark | controlled | -0.053 | -0.007 | 0.349 | 318 |
| humor | F6 | +n_person +has_person | raw | -0.017 | -0.023 | 0.767 | 318 |
| humor | F6 | +n_person +has_person | controlled | -0.009 | -0.026 | 0.869 | 318 |
| humor | F7 | +noun_share -cap_token_share +adj_share +n_gpe | raw | 0.048 | 0.073 | 0.393 | 318 |
| humor | F7 | +noun_share -cap_token_share +adj_share +n_gpe | controlled | 0.078 | 0.091 | 0.165 | 318 |
| humor | F8 | +num_share +digit +year_mention | raw | -0.029 | -0.015 | 0.603 | 318 |
| humor | F8 | +num_share +digit +year_mention | controlled | 0.001 | -0.002 | 0.982 | 318 |
| humor | F9 | +allcaps_word_share +full_caps_title +has_allcaps_word | raw | -0.020 | -0.019 | 0.727 | 318 |
| humor | F9 | +allcaps_word_share +full_caps_title +has_allcaps_word | controlled | -0.033 | -0.018 | 0.554 | 318 |
| humor | F10 | +quoted_speech +quotes | raw | 0.022 | 0.043 | 0.695 | 318 |
| humor | F10 | +quoted_speech +quotes | controlled | 0.024 | 0.044 | 0.668 | 318 |
| humor | F11 | +vader_pos +n_chars +nominalisation | raw | -0.013 | -0.001 | 0.824 | 318 |
| humor | F11 | +vader_pos +n_chars +nominalisation | controlled | 0.012 | 0.005 | 0.830 | 318 |
| humor | F12 | +future_will +modal +first_pl | raw | -0.049 | -0.033 | 0.384 | 318 |
| humor | F12 | +future_will +modal +first_pl | controlled | -0.002 | 0.000 | 0.970 | 318 |
| curiosity_gap | F1 | +vader_compound -vader_neg -shock_word -violence_verb | raw | -0.028 | -0.007 | 0.622 | 318 |
| curiosity_gap | F1 | +vader_compound -vader_neg -shock_word -violence_verb | controlled | -0.015 | 0.015 | 0.788 | 318 |
| curiosity_gap | F2 | +has_finite_verb +present_tense +past_tense +verb_share | raw | 0.107 | 0.084 | 0.057 | 318 |
| curiosity_gap | F2 | +has_finite_verb +present_tense +past_tense +verb_share | controlled | 0.077 | 0.049 | 0.172 | 318 |
| curiosity_gap | F3 | +lead_colon_label +lead_live +colon -entity_first | raw | -0.093 | -0.096 | 0.097 | 318 |
| curiosity_gap | F3 | +lead_colon_label +lead_live +colon -entity_first | controlled | -0.042 | -0.081 | 0.460 | 318 |
| curiosity_gap | F4 | +discourse_marker +trailing_ellipsis +ellipsis +contraction | raw | 0.174 | 0.111 | 0.002 | 318 |
| curiosity_gap | F4 | +discourse_marker +trailing_ellipsis +ellipsis +contraction | controlled | 0.155 | 0.081 | 0.006 | 318 |
| curiosity_gap | F5 | +q_word_start +wh_any +why_marker +q_mark | raw | 0.140 | 0.043 | 0.013 | 318 |
| curiosity_gap | F5 | +q_word_start +wh_any +why_marker +q_mark | controlled | 0.135 | 0.032 | 0.016 | 318 |
| curiosity_gap | F6 | +n_person +has_person | raw | -0.158 | -0.134 | 0.005 | 318 |
| curiosity_gap | F6 | +n_person +has_person | controlled | -0.184 | -0.151 | 0.001 | 318 |
| curiosity_gap | F7 | +noun_share -cap_token_share +adj_share +n_gpe | raw | -0.169 | -0.132 | 0.002 | 318 |
| curiosity_gap | F7 | +noun_share -cap_token_share +adj_share +n_gpe | controlled | -0.112 | -0.117 | 0.045 | 318 |
| curiosity_gap | F8 | +num_share +digit +year_mention | raw | -0.154 | -0.087 | 0.006 | 318 |
| curiosity_gap | F8 | +num_share +digit +year_mention | controlled | -0.068 | -0.065 | 0.230 | 318 |
| curiosity_gap | F9 | +allcaps_word_share +full_caps_title +has_allcaps_word | raw | 0.173 | 0.043 | 0.002 | 318 |
| curiosity_gap | F9 | +allcaps_word_share +full_caps_title +has_allcaps_word | controlled | 0.139 | 0.023 | 0.013 | 318 |
| curiosity_gap | F10 | +quoted_speech +quotes | raw | -0.081 | -0.065 | 0.152 | 318 |
| curiosity_gap | F10 | +quoted_speech +quotes | controlled | -0.073 | -0.071 | 0.195 | 318 |
| curiosity_gap | F11 | +vader_pos +n_chars +nominalisation | raw | -0.117 | -0.092 | 0.038 | 318 |
| curiosity_gap | F11 | +vader_pos +n_chars +nominalisation | controlled | -0.058 | -0.044 | 0.305 | 318 |
| curiosity_gap | F12 | +future_will +modal +first_pl | raw | -0.088 | -0.106 | 0.119 | 318 |
| curiosity_gap | F12 | +future_will +modal +first_pl | controlled | -0.087 | -0.108 | 0.121 | 318 |
| outrage | F1 | +vader_compound -vader_neg -shock_word -violence_verb | raw | -0.611 | -0.606 | 0.000 | 318 |
| outrage | F1 | +vader_compound -vader_neg -shock_word -violence_verb | controlled | -0.526 | -0.528 | 0.000 | 318 |
| outrage | F2 | +has_finite_verb +present_tense +past_tense +verb_share | raw | 0.097 | 0.144 | 0.084 | 318 |
| outrage | F2 | +has_finite_verb +present_tense +past_tense +verb_share | controlled | 0.057 | 0.086 | 0.315 | 318 |
| outrage | F3 | +lead_colon_label +lead_live +colon -entity_first | raw | -0.187 | -0.147 | 0.001 | 318 |
| outrage | F3 | +lead_colon_label +lead_live +colon -entity_first | controlled | -0.106 | -0.085 | 0.059 | 318 |
| outrage | F4 | +discourse_marker +trailing_ellipsis +ellipsis +contraction | raw | 0.090 | -0.016 | 0.109 | 318 |
| outrage | F4 | +discourse_marker +trailing_ellipsis +ellipsis +contraction | controlled | -0.038 | -0.071 | 0.499 | 318 |
| outrage | F5 | +q_word_start +wh_any +why_marker +q_mark | raw | -0.248 | -0.251 | 0.000 | 318 |
| outrage | F5 | +q_word_start +wh_any +why_marker +q_mark | controlled | -0.246 | -0.250 | 0.000 | 318 |
| outrage | F6 | +n_person +has_person | raw | -0.014 | 0.016 | 0.801 | 318 |
| outrage | F6 | +n_person +has_person | controlled | -0.008 | 0.023 | 0.882 | 318 |
| outrage | F7 | +noun_share -cap_token_share +adj_share +n_gpe | raw | -0.082 | -0.216 | 0.146 | 318 |
| outrage | F7 | +noun_share -cap_token_share +adj_share +n_gpe | controlled | -0.106 | -0.202 | 0.058 | 318 |
| outrage | F8 | +num_share +digit +year_mention | raw | -0.226 | -0.194 | 0.000 | 318 |
| outrage | F8 | +num_share +digit +year_mention | controlled | -0.037 | -0.074 | 0.510 | 318 |
| outrage | F9 | +allcaps_word_share +full_caps_title +has_allcaps_word | raw | 0.212 | 0.278 | 0.000 | 318 |
| outrage | F9 | +allcaps_word_share +full_caps_title +has_allcaps_word | controlled | 0.167 | 0.244 | 0.003 | 318 |
| outrage | F10 | +quoted_speech +quotes | raw | -0.056 | 0.001 | 0.317 | 318 |
| outrage | F10 | +quoted_speech +quotes | controlled | -0.070 | -0.009 | 0.214 | 318 |
| outrage | F11 | +vader_pos +n_chars +nominalisation | raw | 0.035 | 0.051 | 0.537 | 318 |
| outrage | F11 | +vader_pos +n_chars +nominalisation | controlled | 0.080 | 0.084 | 0.156 | 318 |
| outrage | F12 | +future_will +modal +first_pl | raw | -0.164 | -0.106 | 0.003 | 318 |
| outrage | F12 | +future_will +modal +first_pl | controlled | -0.184 | -0.142 | 0.001 | 318 |


## Hook classifier

```
{
  "features": "768-d sentence embedding + ['allcaps_word_share', 'excl', 'q_mark', 'trailing_ellipsis', 'violence_verb', 'shock_word', 'curiosity_lex', 'fwd_ref_start', 'discourse_marker', 'has_person', 'neg_eval', 'pos_eval']",
  "model": "StandardScaler + LogisticRegression(class_weight=balanced)",
  "hooks": {
    "curiosity_gap": {
      "n_train": 2400,
      "n_test": 600,
      "base_rate": 0.0207,
      "C": 0.3,
      "cv_f1_by_C": {
        "0.03": 0.1599,
        "0.1": 0.1702,
        "0.3": 0.182,
        "1.0": 0.1714
      },
      "holdout_accuracy": 0.9533,
      "holdout_balanced_accuracy": 0.6088,
      "holdout_f1": 0.1765,
      "holdout_auc": 0.7363,
      "holdout_kappa": 0.1546
    },
    "outrage": {
      "n_train": 2400,
      "n_test": 600,
      "base_rate": 0.572,
      "C": 0.03,
      "cv_f1_by_C": {
        "0.03": 0.7953,
        "0.1": 0.7731,
        "0.3": 0.7574,
        "1.0": 0.7461
      },
      "holdout_accuracy": 0.7617,
      "holdout_balanced_accuracy": 0.7603,
      "holdout_f1": 0.7869,
      "holdout_auc": 0.8431,
      "holdout_kappa": 0.5169
    },
    "humor": {
      "n_train": 2400,
      "n_test": 600,
      "base_rate": 0.0037,
      "C": 0.03,
      "cv_f1_by_C": {
        "0.03": 0.0,
        "0.1": 0.0,
        "0.3": 0.0,
        "1.0": 0.0
      },
      "holdout_accuracy": 0.9967,
      "holdout_balanced_accuracy": 0.5,
      "holdout_f1": 0.0,
      "holdout_auc": 0.7291,
      "holdout_kappa": 0.0
    }
  }
}
```


## LLM rating prompt (labels.csv; exact text)


Model `qwen3:14b`, temperature 0.0, prompt id `title-style-v3`, sha256 `03c5da1a9e41c1663e4e97797c79c74cf330976a57815c41ff7ee24f64ca61ad`, rated 2026-09-14T22:35:38+00:00.

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
You are labelling a topic found by clustering YouTube video titles from political-media channels.
Top terms (by class TF-IDF): {terms}
Example titles:
{examples}

Answer with one JSON object and nothing else:
{{"label": "<a short topic name, at most 6 words>", "political": true or false, "category": "<one of: {categories}>"}}
'political' is true when the topic concerns politics, government, elections, war, policy, courts, political figures or the culture war; false for sport, entertainment, weather, lifestyle, business/markets-only, science/health and similar.
```


## Leaning label prompt (leaning_labels.csv; exact text, prompt id leaning-v1, temperature 0, batches of 20; the same prompt for every judge)

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
| pooled_balanced | raw | 100 | 0.8563 | 100 | 189240 | 2061945 | 55465 | the trump to in on of s iran live is and as for a with us war after at news |
| pooled_balanced | raw | 1000 | 0.7803 | 1000 | 189240 | 2061945 | 55465 | the trump to in on of s iran live is and as for a with us war after at news |
| pooled_balanced | raw | 5000 | 1.0204 | 5000 | 189240 | 2061945 | 55465 | the trump to in on of s iran live is and as for a with us war after at news |
| pooled_balanced | normalised | 100 | 0.8636 | 100 | 189240 | 2002279 | 53660 | the trump to in on of s iran live is and as for a with us war after at over |
| pooled_balanced | normalised | 1000 | 0.7838 | 1000 | 189240 | 2002279 | 53660 | the trump to in on of s iran live is and as for a with us war after at over |
| pooled_balanced | normalised | 5000 | 1.0139 | 5000 | 189240 | 2002279 | 53660 | the trump to in on of s iran live is and as for a with us war after at over |
| creator_level_mean | raw | 200 | 0.7990 | 200 | 187187 | 2042611 | 498266 | median 0.7991 over 318 creator x genre groups (>= 50 titles) |
| creator_level_mean | normalised | 200 | 0.7815 | 200 | 187187 | 1984121 | 494374 | median 0.7829 over 318 creator x genre groups (>= 50 titles) |


## Sample sizes

| creator | genre | n_rows | n_unique | n_balanced | n_with_views | repeat_share | low_n |
|---|---|---|---|---|---|---|---|
| @60minutes | videos | 325 | 325 | 325 | 321 | 0.000 | no |
| @ABCNews | streams | 626 | 590 | 590 | 626 | 0.058 | no |
| @ABCNews | videos | 8002 | 7971 | 2500 | 8002 | 0.004 | no |
| @ANINewsIndia | streams | 7717 | 7579 | 2500 | 7717 | 0.018 | no |
| @ANINewsIndia | videos | 12296 | 12279 | 2500 | 12296 | 0.001 | no |
| @ActualJusticeWarrior | streams | 1 | 1 | 1 | 1 | 0.000 | yes |
| @ActualJusticeWarrior | videos | 392 | 392 | 392 | 392 | 0.000 | no |
| @AfterPartyEmily | streams | 74 | 74 | 74 | 74 | 0.000 | no |
| @AfterPartyEmily | videos | 410 | 410 | 410 | 410 | 0.000 | no |
| @AlexStein99 | streams | 41 | 41 | 41 | 41 | 0.000 | yes |
| @AlexStein99 | videos | 87 | 87 | 87 | 87 | 0.000 | no |
| @AnaEscobarShow | streams | 31 | 31 | 31 | 31 | 0.000 | yes |
| @AnaEscobarShow | videos | 32 | 32 | 32 | 31 | 0.000 | yes |
| @AndWeKnowOfficial-o9b | videos | 185 | 185 | 185 | 185 | 0.000 | no |
| @AndrewKlavan | streams | 3 | 3 | 3 | 3 | 0.000 | yes |
| @AndrewKlavan | videos | 196 | 196 | 196 | 196 | 0.000 | no |
| @AnthonyBrianLogan | streams | 52 | 52 | 52 | 52 | 0.000 | no |
| @AnthonyBrianLogan | videos | 248 | 248 | 248 | 248 | 0.000 | no |
| @AsmonTV | videos | 947 | 875 | 875 | 947 | 0.076 | no |
| @AssociatedPress | streams | 1332 | 1151 | 1151 | 1332 | 0.136 | no |
| @AssociatedPress | videos | 5574 | 5572 | 2500 | 5567 | 0.000 | no |
| @BBCNews | videos | 2445 | 2440 | 2440 | 2294 | 0.002 | no |
| @BadEmpanadaLive | streams | 1 | 1 | 1 | 1 | 0.000 | yes |
| @BadEmpanadaLive | videos | 298 | 298 | 298 | 290 | 0.000 | no |
| @BadFaithPodcast | streams | 1 | 1 | 1 | 1 | 0.000 | yes |
| @BadFaithPodcast | videos | 81 | 81 | 81 | 81 | 0.000 | no |
| @BelleRanch | videos | 822 | 822 | 822 | 822 | 0.000 | no |
| @BenShapiro | streams | 17 | 17 | 17 | 17 | 0.000 | yes |
| @BenShapiro | videos | 525 | 525 | 525 | 525 | 0.000 | no |
| @BlackConservativePerspective | streams | 1 | 1 | 1 | 1 | 0.000 | yes |
| @BlackConservativePerspective | videos | 1271 | 1271 | 1271 | 1271 | 0.000 | no |
| @BlaireWhiteX | videos | 11 | 11 | 11 | 11 | 0.000 | yes |
| @BlazeTV | streams | 14 | 14 | 14 | 14 | 0.000 | yes |
| @BlazeTV | videos | 868 | 868 | 868 | 868 | 0.000 | no |
| @BreakThroughNews | streams | 57 | 57 | 57 | 57 | 0.000 | no |
| @BreakThroughNews | videos | 242 | 242 | 242 | 242 | 0.000 | no |
| @BrittanyVenti | streams | 19 | 19 | 19 | 10 | 0.000 | yes |
| @BrittanyVenti | videos | 55 | 55 | 55 | 54 | 0.000 | no |
| @CBSNews | streams | 369 | 368 | 368 | 369 | 0.003 | no |
| @CBSNews | videos | 8322 | 8322 | 2500 | 8322 | 0.000 | no |
| @CNN | streams | 95 | 94 | 94 | 95 | 0.011 | no |
| @CNN | videos | 1758 | 1757 | 1757 | 1758 | 0.001 | no |
| @CamHigby | streams | 71 | 59 | 59 | 68 | 0.169 | no |
| @CamHigby | videos | 187 | 186 | 186 | 183 | 0.005 | no |
| @CashJordan | videos | 301 | 299 | 299 | 301 | 0.007 | no |
| @CaspianReport | videos | 25 | 25 | 25 | 25 | 0.000 | yes |
| @ChadPrather1 | streams | 202 | 201 | 201 | 202 | 0.005 | no |
| @ChadPrather1 | videos | 160 | 160 | 160 | 160 | 0.000 | no |
| @Channel5YouTube | videos | 43 | 43 | 43 | 43 | 0.000 | yes |
| @ClipsCandaceOwens | videos | 192 | 192 | 192 | 1 | 0.000 | no |
| @ClubRandomPodcast | videos | 197 | 197 | 197 | 197 | 0.000 | no |
| @ColeHastings | videos | 32 | 32 | 32 | 32 | 0.000 | yes |
| @ColemanHughesOfficial | videos | 54 | 54 | 54 | 54 | 0.000 | no |
| @CoreyGilShusterAskProject | streams | 2 | 2 | 2 | 2 | 0.000 | yes |
| @CoreyGilShusterAskProject | videos | 53 | 53 | 53 | 53 | 0.000 | no |
| @DailyDenims | videos | 215 | 215 | 215 | 215 | 0.000 | no |
| @DannyHaiphongYT | streams | 228 | 227 | 227 | 226 | 0.004 | no |
| @DannyHaiphongYT | videos | 64 | 64 | 64 | 63 | 0.000 | no |
| @DarkHorsePod | streams | 38 | 38 | 38 | 38 | 0.000 | yes |
| @DarkHorsePod | videos | 70 | 70 | 70 | 70 | 0.000 | no |
| @DemocracyDocket | streams | 4 | 4 | 4 | 4 | 0.000 | yes |
| @DemocracyDocket | videos | 129 | 129 | 129 | 129 | 0.000 | no |
| @DemocracyNow | streams | 1 | 1 | 1 | 1 | 0.000 | yes |
| @DemocracyNow | videos | 817 | 814 | 814 | 817 | 0.004 | no |
| @DestinyDGGClips | videos | 209 | 209 | 209 | 209 | 0.000 | no |
| @DoubleDownNews | videos | 66 | 66 | 66 | 66 | 0.000 | no |
| @DrSteveTurleyTV | streams | 31 | 31 | 31 | 31 | 0.000 | yes |
| @DrSteveTurleyTV | videos | 444 | 442 | 442 | 444 | 0.004 | no |
| @DropSiteNews | streams | 43 | 43 | 43 | 43 | 0.000 | yes |
| @DropSiteNews | videos | 204 | 204 | 204 | 204 | 0.000 | no |
| @DueDissidence | streams | 112 | 112 | 112 | 112 | 0.000 | no |
| @DueDissidence | videos | 643 | 643 | 643 | 643 | 0.000 | no |
| @DylanBurnsLIVE | streams | 3 | 3 | 3 | 3 | 0.000 | yes |
| @DylanBurnsLIVE | videos | 190 | 190 | 190 | 190 | 0.000 | no |
| @EzraKleinShow | streams | 1 | 1 | 1 | 1 | 0.000 | yes |
| @EzraKleinShow | videos | 65 | 65 | 65 | 65 | 0.000 | no |
| @FarronBalanced | streams | 188 | 188 | 188 | 188 | 0.000 | no |
| @FarronBalanced | videos | 1782 | 1780 | 1780 | 1781 | 0.001 | no |
| @FinancialTimes | videos | 40 | 40 | 40 | 40 | 0.000 | yes |
| @Firstpost | streams | 10365 | 8975 | 2500 | 10365 | 0.134 | no |
| @Firstpost | videos | 10136 | 10126 | 2500 | 10136 | 0.001 | no |
| @FleccasTalks | videos | 290 | 290 | 290 | 68 | 0.000 | no |
| @Forbes | streams | 3 | 3 | 3 | 3 | 0.000 | yes |
| @Forbes | videos | 1269 | 1256 | 1256 | 1269 | 0.010 | no |
| @Forthepeoplepodcast305 | streams | 45 | 45 | 45 | 45 | 0.000 | yes |
| @Forthepeoplepodcast305 | videos | 115 | 115 | 115 | 115 | 0.000 | no |
| @FoxNews | streams | 655 | 645 | 645 | 655 | 0.015 | no |
| @FoxNews | videos | 8213 | 8210 | 2500 | 8156 | 0.000 | no |
| @FoxNewsChannelClips | videos | 5748 | 5748 | 2500 | 5748 | 0.000 | no |
| @FreshFitMiami | streams | 82 | 75 | 75 | 82 | 0.085 | no |
| @FreshFitMiami | videos | 111 | 111 | 111 | 111 | 0.000 | no |
| @GeopoliticalEconomyReport | videos | 72 | 72 | 72 | 72 | 0.000 | no |
| @GlennKirschner2 | videos | 264 | 262 | 262 | 264 | 0.008 | no |
| @GrahamAllen | videos | 247 | 247 | 247 | 247 | 0.000 | no |
| @HangOutwithSeanHannity | videos | 154 | 154 | 154 | 154 | 0.000 | no |
| @HasanAbi | streams | 7 | 7 | 7 | 7 | 0.000 | yes |
| @HasanAbi | videos | 635 | 628 | 628 | 635 | 0.011 | no |
| @HasanAbiVODs3 | videos | 181 | 181 | 181 | 181 | 0.000 | no |
| @HasanReactionsfanTwo | videos | 340 | 340 | 340 | 340 | 0.000 | no |
| @HasanabiClips | streams | 35 | 32 | 32 | 35 | 0.086 | yes |
| @HasanabiClips | videos | 474 | 474 | 474 | 474 | 0.000 | no |
| @JackCocchiarellaShow | streams | 21 | 21 | 21 | 21 | 0.000 | yes |
| @JackCocchiarellaShow | videos | 1602 | 1524 | 1524 | 1602 | 0.049 | no |
| @JacksonHinkleOfficial | streams | 83 | 81 | 81 | 1 | 0.024 | no |
| @JacksonHinkleOfficial | videos | 391 | 388 | 388 | 4 | 0.008 | no |
| @JamarlThomas | streams | 223 | 223 | 223 | 223 | 0.000 | no |
| @JamarlThomas | videos | 274 | 274 | 274 | 274 | 0.000 | no |
| @JesseKellyDC | streams | 1 | 1 | 1 | 1 | 0.000 | yes |
| @JesseKellyDC | videos | 505 | 504 | 504 | 505 | 0.002 | no |
| @JillianMichaels | videos | 457 | 457 | 457 | 457 | 0.000 | no |
| @JustPearlyThings | streams | 96 | 96 | 96 | 96 | 0.000 | no |
| @JustPearlyThings | videos | 669 | 669 | 669 | 669 | 0.000 | no |
| @KimIversen | streams | 1 | 1 | 1 | 1 | 0.000 | yes |
| @KimIversen | videos | 534 | 534 | 534 | 534 | 0.000 | no |
| @LIVESNEAKO | streams | 69 | 69 | 69 | 69 | 0.000 | no |
| @LIVESNEAKO | videos | 481 | 479 | 479 | 481 | 0.004 | no |
| @LastWeekTonight | videos | 35 | 35 | 35 | 35 | 0.000 | yes |
| @LeejaMiller | streams | 1 | 1 | 1 | 1 | 0.000 | yes |
| @LeejaMiller | videos | 60 | 60 | 60 | 60 | 0.000 | no |
| @LegalAFMTN | streams | 46 | 45 | 45 | 46 | 0.022 | yes |
| @LegalAFMTN | videos | 2740 | 2735 | 2500 | 2470 | 0.002 | no |
| @LegalEagle | videos | 105 | 105 | 105 | 105 | 0.000 | no |
| @LeverNews | streams | 9 | 9 | 9 | 9 | 0.000 | yes |
| @LeverNews | videos | 73 | 73 | 73 | 73 | 0.000 | no |
| @LiberalHivemind | videos | 855 | 846 | 846 | 855 | 0.011 | no |
| @LukeBeasley | streams | 247 | 246 | 246 | 155 | 0.004 | no |
| @LukeBeasley | videos | 1168 | 1162 | 1162 | 1066 | 0.005 | no |
| @Lunaoi | videos | 9 | 9 | 9 | 9 | 0.000 | yes |
| @MLChristiansen | streams | 77 | 77 | 77 | 77 | 0.000 | no |
| @MLChristiansen | videos | 118 | 118 | 118 | 118 | 0.000 | no |
| @MarkDice | videos | 92 | 92 | 92 | 92 | 0.000 | no |
| @MattBernstein1 | videos | 21 | 21 | 21 | 21 | 0.000 | yes |
| @MattWalsh | streams | 2 | 2 | 2 | 2 | 0.000 | yes |
| @MattWalsh | videos | 297 | 297 | 297 | 263 | 0.000 | no |
| @MegynKelly | streams | 13 | 13 | 13 | 11 | 0.000 | yes |
| @MegynKelly | videos | 1651 | 1651 | 1651 | 1647 | 0.000 | no |
| @MeidasTouch | streams | 631 | 627 | 627 | 631 | 0.006 | no |
| @MeidasTouch | videos | 3533 | 3532 | 2500 | 3407 | 0.000 | no |
| @MichaelKnowles | streams | 4 | 4 | 4 | 4 | 0.000 | yes |
| @MichaelKnowles | videos | 472 | 472 | 472 | 472 | 0.000 | no |
| @MichaelMaliceofficial | streams | 3 | 3 | 3 | 3 | 0.000 | yes |
| @MichaelMaliceofficial | videos | 55 | 55 | 55 | 55 | 0.000 | no |
| @MikeFromPA | videos | 129 | 129 | 129 | 129 | 0.000 | no |
| @ModernDayDebate | streams | 109 | 109 | 109 | 81 | 0.000 | no |
| @ModernDayDebate | videos | 47 | 46 | 46 | 42 | 0.021 | yes |
| @MrReaganUSA | streams | 2 | 2 | 2 | 2 | 0.000 | yes |
| @MrReaganUSA | videos | 26 | 26 | 26 | 26 | 0.000 | yes |
| @MrTariqNasheed | streams | 19 | 19 | 19 | 19 | 0.000 | yes |
| @MrTariqNasheed | videos | 403 | 403 | 403 | 403 | 0.000 | no |
| @MyronGainesX | streams | 247 | 245 | 245 | 247 | 0.008 | no |
| @MyronGainesX | videos | 389 | 389 | 389 | 389 | 0.000 | no |
| @NBCNews | streams | 404 | 367 | 367 | 404 | 0.092 | no |
| @NBCNews | videos | 6516 | 6499 | 2500 | 6516 | 0.003 | no |
| @NPR | streams | 1 | 1 | 1 | 1 | 0.000 | yes |
| @NPR | videos | 73 | 70 | 70 | 73 | 0.041 | no |
| @NYTOpinion | videos | 29 | 29 | 29 | 29 | 0.000 | yes |
| @NYTPodcasts | videos | 481 | 481 | 481 | 473 | 0.000 | no |
| @NewsNation | streams | 306 | 302 | 302 | 306 | 0.013 | no |
| @NewsNation | videos | 7390 | 7372 | 2500 | 7389 | 0.002 | no |
| @NewsmaxTV | streams | 404 | 399 | 399 | 404 | 0.012 | no |
| @NewsmaxTV | videos | 3945 | 3944 | 2500 | 3945 | 0.000 | no |
| @NickCruseRBN | streams | 103 | 103 | 103 | 103 | 0.000 | no |
| @NickCruseRBN | videos | 23 | 23 | 23 | 23 | 0.000 | yes |
| @NickShirley | streams | 13 | 13 | 13 | 10 | 0.000 | yes |
| @NickShirley | videos | 32 | 32 | 32 | 29 | 0.000 | yes |
| @NovaraMedia | streams | 4 | 4 | 4 | 4 | 0.000 | yes |
| @NovaraMedia | videos | 585 | 585 | 585 | 585 | 0.000 | no |
| @OfficialFlagrant | videos | 35 | 35 | 35 | 35 | 0.000 | yes |
| @OfficialSaharTV | streams | 2 | 2 | 2 | 2 | 0.000 | yes |
| @OfficialSaharTV | videos | 893 | 893 | 893 | 887 | 0.000 | no |
| @OutKick | videos | 51 | 51 | 51 | 51 | 0.000 | no |
| @OwenJonesTalks | videos | 233 | 233 | 233 | 233 | 0.000 | no |
| @OwenReport | streams | 178 | 178 | 178 | 178 | 0.000 | no |
| @OwenReport | videos | 388 | 388 | 388 | 388 | 0.000 | no |
| @PBDPodcast | streams | 118 | 118 | 118 | 118 | 0.000 | no |
| @PBDPodcast | videos | 38 | 38 | 38 | 38 | 0.000 | yes |
| @POLITICO | videos | 295 | 295 | 295 | 295 | 0.000 | no |
| @PTLRadioShow | streams | 202 | 201 | 201 | 202 | 0.005 | no |
| @PTLRadioShow | videos | 1685 | 1684 | 1684 | 1685 | 0.001 | no |
| @PartOfTheProblem | videos | 103 | 103 | 103 | 103 | 0.000 | no |
| @PerunAU | videos | 37 | 37 | 37 | 37 | 0.000 | yes |
| @PhillipScottPodcast | streams | 153 | 153 | 153 | 153 | 0.000 | no |
| @PhillipScottPodcast | videos | 7 | 7 | 7 | 7 | 0.000 | yes |
| @PiersMorganUncensored | videos | 181 | 181 | 181 | 181 | 0.000 | no |
| @PiscoLitty | videos | 56 | 56 | 56 | 56 | 0.000 | no |
| @Politicon | streams | 1 | 1 | 1 | 1 | 0.000 | yes |
| @Politicon | videos | 496 | 496 | 496 | 496 | 0.000 | no |
| @PoliticsGirl | videos | 116 | 116 | 116 | 116 | 0.000 | no |
| @PoliticsJOE | videos | 339 | 339 | 339 | 339 | 0.000 | no |
| @PragerU | streams | 32 | 31 | 31 | 32 | 0.031 | yes |
| @PragerU | videos | 387 | 385 | 385 | 387 | 0.005 | no |
| @PrisonPlanetLive | videos | 56 | 46 | 46 | 56 | 0.179 | yes |
| @RSBN | streams | 337 | 337 | 337 | 337 | 0.000 | no |
| @RSBN | videos | 1642 | 1640 | 1640 | 1642 | 0.001 | no |
| @RealAlexClark | videos | 79 | 79 | 79 | 79 | 0.000 | no |
| @RealAmericasVoice | streams | 2958 | 1543 | 1543 | 2958 | 0.478 | no |
| @RealAmericasVoice | videos | 2659 | 2653 | 2500 | 2659 | 0.002 | no |
| @RealDanBongino | videos | 266 | 266 | 266 | 266 | 0.000 | no |
| @RebelHQ | videos | 1293 | 1292 | 1292 | 1293 | 0.001 | no |
| @RebelNewsOnline | streams | 197 | 195 | 195 | 197 | 0.010 | no |
| @RebelNewsOnline | videos | 1368 | 1358 | 1358 | 1147 | 0.007 | no |
| @RedactedNews | streams | 140 | 140 | 140 | 140 | 0.000 | no |
| @RedactedNews | videos | 452 | 452 | 452 | 452 | 0.000 | no |
| @RekietaLaw | streams | 106 | 106 | 106 | 80 | 0.000 | no |
| @RekietaLaw | videos | 18 | 18 | 18 | 18 | 0.000 | yes |
| @RestPoliticsUS | streams | 5 | 5 | 5 | 5 | 0.000 | yes |
| @RestPoliticsUS | videos | 220 | 220 | 220 | 103 | 0.000 | no |
| @Reuters | streams | 2294 | 2008 | 2008 | 2294 | 0.125 | no |
| @Reuters | videos | 8092 | 8076 | 2500 | 8092 | 0.002 | no |
| @RileyGaines | videos | 143 | 143 | 143 | 143 | 0.000 | no |
| @RobertGouveiaEsq | streams | 396 | 385 | 385 | 201 | 0.028 | no |
| @RobertGouveiaEsq | videos | 696 | 696 | 696 | 690 | 0.000 | no |
| @RonPlacone | streams | 28 | 28 | 28 | 28 | 0.000 | yes |
| @RonPlacone | videos | 66 | 66 | 66 | 66 | 0.000 | no |
| @RubinReport | streams | 115 | 114 | 114 | 115 | 0.009 | no |
| @RubinReport | videos | 1093 | 1047 | 1047 | 1093 | 0.042 | no |
| @RufoandLomez | videos | 80 | 80 | 80 | 80 | 0.000 | no |
| @SMN | streams | 8 | 8 | 8 | 7 | 0.000 | yes |
| @SMN | videos | 197 | 197 | 197 | 99 | 0.000 | no |
| @SNEAKO | videos | 5 | 5 | 5 | 5 | 0.000 | yes |
| @SabbySabs | streams | 103 | 103 | 103 | 103 | 0.000 | no |
| @SabbySabs | videos | 626 | 626 | 626 | 626 | 0.000 | no |
| @SaltyCracker | videos | 387 | 387 | 387 | 387 | 0.000 | no |
| @SavSays | streams | 1 | 1 | 1 | 0 | 0.000 | yes |
| @SavSays | videos | 16 | 16 | 16 | 16 | 0.000 | yes |
| @SecondThought | videos | 20 | 20 | 20 | 20 | 0.000 | yes |
| @SecularTalk | streams | 1 | 1 | 1 | 1 | 0.000 | yes |
| @SecularTalk | videos | 1459 | 1458 | 1458 | 1459 | 0.001 | no |
| @Semafor | streams | 30 | 30 | 30 | 30 | 0.000 | yes |
| @Semafor | videos | 153 | 153 | 153 | 153 | 0.000 | no |
| @Shoe0nHead | videos | 10 | 10 | 10 | 10 | 0.000 | yes |
| @SkyNews | streams | 1976 | 1968 | 1968 | 1930 | 0.004 | no |
| @SkyNews | videos | 3681 | 3677 | 2500 | 3681 | 0.001 | no |
| @StatusCoup | streams | 159 | 157 | 157 | 159 | 0.013 | no |
| @StatusCoup | videos | 517 | 517 | 517 | 498 | 0.000 | no |
| @StevenCrowder | streams | 8 | 8 | 8 | 8 | 0.000 | yes |
| @StevenCrowder | videos | 169 | 169 | 169 | 169 | 0.000 | no |
| @StosselTV | videos | 50 | 50 | 50 | 50 | 0.000 | no |
| @Styxhexenhammer666 | streams | 27 | 27 | 27 | 27 | 0.000 | yes |
| @Styxhexenhammer666 | videos | 449 | 446 | 446 | 449 | 0.007 | no |
| @SydneyWatson | videos | 61 | 61 | 61 | 61 | 0.000 | no |
| @TechCrunch | videos | 146 | 145 | 145 | 146 | 0.007 | no |
| @TheAdamCarollaShow1 | videos | 395 | 395 | 395 | 395 | 0.000 | no |
| @TheAmalaEkpunobi | streams | 12 | 12 | 12 | 12 | 0.000 | yes |
| @TheAmalaEkpunobi | videos | 211 | 211 | 211 | 211 | 0.000 | no |
| @TheAtlantic | streams | 5 | 5 | 5 | 5 | 0.000 | yes |
| @TheAtlantic | videos | 166 | 166 | 166 | 166 | 0.000 | no |
| @TheBrianKilmeadeShow | streams | 2 | 2 | 2 | 2 | 0.000 | yes |
| @TheBrianKilmeadeShow | videos | 352 | 352 | 352 | 352 | 0.000 | no |
| @TheDailyBeast | streams | 34 | 34 | 34 | 3 | 0.000 | yes |
| @TheDailyBeast | videos | 322 | 322 | 322 | 321 | 0.000 | no |
| @TheDamageReport | streams | 274 | 271 | 271 | 84 | 0.011 | no |
| @TheDamageReport | videos | 3206 | 3204 | 2500 | 2227 | 0.001 | no |
| @TheDonLemonShow | streams | 400 | 400 | 400 | 370 | 0.000 | no |
| @TheDonLemonShow | videos | 366 | 366 | 366 | 366 | 0.000 | no |
| @TheEconomist | videos | 137 | 137 | 137 | 137 | 0.000 | no |
| @TheHumanistReport | streams | 35 | 35 | 35 | 35 | 0.000 | yes |
| @TheHumanistReport | videos | 154 | 154 | 154 | 154 | 0.000 | no |
| @TheJoyReidShow | streams | 144 | 140 | 140 | 135 | 0.028 | no |
| @TheJoyReidShow | videos | 238 | 238 | 238 | 237 | 0.000 | no |
| @TheLincolnProject | streams | 28 | 28 | 28 | 28 | 0.000 | yes |
| @TheLincolnProject | videos | 123 | 123 | 123 | 123 | 0.000 | no |
| @TheMajorityReport | streams | 195 | 195 | 195 | 195 | 0.000 | no |
| @TheMajorityReport | videos | 1660 | 1657 | 1657 | 1660 | 0.002 | no |
| @TheMichaelCohenShow | videos | 479 | 479 | 479 | 477 | 0.000 | no |
| @TheOfficerTatum | streams | 194 | 194 | 194 | 137 | 0.000 | no |
| @TheOfficerTatum | videos | 617 | 617 | 617 | 582 | 0.000 | no |
| @ThePodcastoftheLotusEaters | streams | 179 | 179 | 179 | 179 | 0.000 | no |
| @ThePodcastoftheLotusEaters | videos | 622 | 622 | 622 | 622 | 0.000 | no |
| @TheQuartering | videos | 691 | 675 | 675 | 691 | 0.023 | no |
| @TheRealTabithaSpeaks | streams | 4 | 4 | 4 | 4 | 0.000 | yes |
| @TheRealTabithaSpeaks | videos | 452 | 452 | 452 | 446 | 0.000 | no |
| @TheSerfTimes | streams | 106 | 103 | 103 | 1 | 0.028 | no |
| @TheSerfTimes | videos | 247 | 247 | 247 | 247 | 0.000 | no |
| @TheVaushPit | videos | 403 | 403 | 403 | 403 | 0.000 | no |
| @TheYoungTurks | streams | 451 | 428 | 428 | 242 | 0.051 | no |
| @TheYoungTurks | videos | 2872 | 2868 | 2500 | 1941 | 0.001 | no |
| @The_Crucible | streams | 5 | 5 | 5 | 5 | 0.000 | yes |
| @The_Crucible | videos | 226 | 226 | 226 | 226 | 0.000 | no |
| @TimDillonShow | videos | 68 | 68 | 68 | 38 | 0.000 | no |
| @Tim_Black | streams | 16 | 16 | 16 | 16 | 0.000 | yes |
| @Tim_Black | videos | 329 | 329 | 329 | 329 | 0.000 | no |
| @Timcast | streams | 6 | 6 | 6 | 6 | 0.000 | yes |
| @Timcast | videos | 186 | 183 | 183 | 186 | 0.016 | no |
| @TimcastIRL | streams | 154 | 154 | 154 | 154 | 0.000 | no |
| @TimcastIRL | videos | 903 | 855 | 855 | 903 | 0.053 | no |
| @TimcastNews | streams | 8 | 8 | 8 | 8 | 0.000 | yes |
| @TimcastNews | videos | 548 | 534 | 534 | 548 | 0.025 | no |
| @TimesNowWorld | streams | 5323 | 3006 | 2500 | 5323 | 0.435 | no |
| @TimesNowWorld | videos | 9001 | 8994 | 2500 | 8996 | 0.001 | no |
| @TomiLahrenIsFearless | videos | 118 | 118 | 118 | 118 | 0.000 | no |
| @TuckerCarlson | videos | 119 | 119 | 119 | 119 | 0.000 | no |
| @USATODAY | streams | 430 | 417 | 417 | 430 | 0.030 | no |
| @USATODAY | videos | 2224 | 2221 | 2221 | 2224 | 0.001 | no |
| @UnHerd | streams | 17 | 17 | 17 | 17 | 0.000 | yes |
| @UnHerd | videos | 83 | 83 | 83 | 83 | 0.000 | no |
| @Unpacked | videos | 41 | 41 | 41 | 41 | 0.000 | yes |
| @Vaush | streams | 1 | 1 | 1 | 1 | 0.000 | yes |
| @Vaush | videos | 453 | 453 | 453 | 453 | 0.000 | no |
| @VivaFrei | streams | 52 | 52 | 52 | 52 | 0.000 | no |
| @VivaFrei | videos | 331 | 331 | 331 | 331 | 0.000 | no |
| @Vox | videos | 133 | 133 | 133 | 133 | 0.000 | no |
| @X22Report-y5y | videos | 396 | 395 | 395 | 396 | 0.003 | no |
| @XAVIAER | streams | 3 | 3 | 3 | 3 | 0.000 | yes |
| @XAVIAER | videos | 71 | 71 | 71 | 71 | 0.000 | no |
| @Xanderhal | streams | 108 | 108 | 108 | 1 | 0.000 | no |
| @Xanderhal | videos | 316 | 316 | 316 | 316 | 0.000 | no |
| @YaBoiHakim | videos | 16 | 16 | 16 | 16 | 0.000 | yes |
| @ZeihanonGeopolitics | videos | 217 | 217 | 217 | 217 | 0.000 | no |
| @ZubyMusic | videos | 139 | 139 | 139 | 139 | 0.000 | no |
| @aaronparnas1 | streams | 13 | 10 | 10 | 13 | 0.231 | yes |
| @aaronparnas1 | videos | 819 | 819 | 819 | 819 | 0.000 | no |
| @adammockler | streams | 2 | 2 | 2 | 2 | 0.000 | yes |
| @adammockler | videos | 1125 | 1117 | 1117 | 1121 | 0.007 | no |
| @ajplus | videos | 50 | 50 | 50 | 50 | 0.000 | no |
| @aljazeeraenglish | videos | 7006 | 7000 | 2500 | 7006 | 0.001 | no |
| @axios | streams | 8 | 7 | 7 | 8 | 0.125 | yes |
| @axios | videos | 138 | 137 | 137 | 138 | 0.007 | no |
| @bbrettcooper | videos | 143 | 143 | 143 | 143 | 0.000 | no |
| @bennyjohnson | streams | 168 | 168 | 168 | 168 | 0.000 | no |
| @bennyjohnson | videos | 1508 | 1508 | 1508 | 1508 | 0.000 | no |
| @breakingpoints | streams | 4 | 4 | 4 | 4 | 0.000 | yes |
| @breakingpoints | videos | 1037 | 1037 | 1037 | 1037 | 0.000 | no |
| @briantylercohen | streams | 10 | 10 | 10 | 10 | 0.000 | yes |
| @briantylercohen | videos | 1082 | 1081 | 1081 | 1082 | 0.001 | no |
| @bulwarkmedia | streams | 228 | 228 | 228 | 225 | 0.000 | no |
| @bulwarkmedia | videos | 2137 | 1826 | 1826 | 960 | 0.145 | no |
| @bushrakhanum | videos | 22 | 22 | 22 | 22 | 0.000 | yes |
| @cafedotcom | videos | 54 | 54 | 54 | 54 | 0.000 | no |
| @chicksonright | streams | 179 | 179 | 179 | 179 | 0.000 | no |
| @chicksonright | videos | 475 | 475 | 475 | 475 | 0.000 | no |
| @chinainsights-r2w | videos | 278 | 278 | 278 | 278 | 0.000 | no |
| @chriscuomo | streams | 9 | 8 | 8 | 8 | 0.111 | yes |
| @chriscuomo | videos | 208 | 208 | 208 | 127 | 0.000 | no |
| @clayandbuck | streams | 42 | 42 | 42 | 42 | 0.000 | yes |
| @clayandbuck | videos | 581 | 581 | 581 | 581 | 0.000 | no |
| @deanwithrs | streams | 268 | 266 | 266 | 268 | 0.007 | no |
| @deanwithrs | videos | 265 | 265 | 265 | 265 | 0.000 | no |
| @destiny | videos | 267 | 267 | 267 | 267 | 0.000 | no |
| @destinyhqclips | videos | 197 | 197 | 197 | 197 | 0.000 | no |
| @dineshdsouza | streams | 2 | 2 | 2 | 2 | 0.000 | yes |
| @dineshdsouza | videos | 92 | 92 | 92 | 92 | 0.000 | no |
| @dollemore | streams | 4 | 4 | 4 | 4 | 0.000 | yes |
| @dollemore | videos | 1439 | 1439 | 1439 | 1439 | 0.000 | no |
| @doomscrollpodcast | videos | 17 | 17 | 17 | 17 | 0.000 | yes |
| @evanjmez | videos | 22 | 22 | 22 | 22 | 0.000 | yes |
| @fastpoliticspodcast | videos | 145 | 145 | 145 | 135 | 0.000 | no |
| @fightbackpodcast | streams | 24 | 24 | 24 | 24 | 0.000 | yes |
| @fightbackpodcast | videos | 632 | 627 | 627 | 632 | 0.008 | no |
| @franifio | streams | 62 | 62 | 62 | 62 | 0.000 | no |
| @franifio | videos | 282 | 282 | 282 | 267 | 0.000 | no |
| @glennbeck | streams | 125 | 125 | 125 | 125 | 0.000 | no |
| @glennbeck | videos | 460 | 460 | 460 | 460 | 0.000 | no |
| @harryjsisson | streams | 3 | 3 | 3 | 3 | 0.000 | yes |
| @harryjsisson | videos | 688 | 681 | 681 | 688 | 0.010 | no |
| @hutch | streams | 50 | 50 | 50 | 1 | 0.000 | no |
| @hutch | videos | 162 | 162 | 162 | 162 | 0.000 | no |
| @jimacosta | streams | 161 | 160 | 160 | 161 | 0.006 | no |
| @jimacosta | videos | 314 | 313 | 313 | 312 | 0.003 | no |
| @jlptalk | streams | 187 | 187 | 187 | 187 | 0.000 | no |
| @jlptalk | videos | 304 | 304 | 304 | 288 | 0.000 | no |
| @joerogan | streams | 1 | 1 | 1 | 1 | 0.000 | yes |
| @joerogan | videos | 141 | 141 | 141 | 141 | 0.000 | no |
| @johnnyharris | videos | 13 | 13 | 13 | 13 | 0.000 | yes |
| @judgingfreedom | streams | 699 | 697 | 697 | 699 | 0.003 | no |
| @judgingfreedom | videos | 355 | 355 | 355 | 355 | 0.000 | no |
| @katiephangnews | streams | 45 | 44 | 44 | 45 | 0.022 | yes |
| @katiephangnews | videos | 403 | 403 | 403 | 403 | 0.000 | no |
| @katmabu | videos | 35 | 34 | 34 | 35 | 0.029 | yes |
| @laurenchenclips | videos | 109 | 109 | 109 | 109 | 0.000 | no |
| @lizwheeler | streams | 70 | 70 | 70 | 70 | 0.000 | no |
| @lizwheeler | videos | 86 | 86 | 86 | 86 | 0.000 | no |
| @lonerboxlive | videos | 88 | 88 | 88 | 88 | 0.000 | no |
| @lovettorleaveitpodcast | videos | 114 | 114 | 114 | 114 | 0.000 | no |
| @marclamonthillnetwork | streams | 151 | 151 | 151 | 151 | 0.000 | no |
| @marclamonthillnetwork | videos | 321 | 321 | 321 | 321 | 0.000 | no |
| @markets | streams | 56 | 56 | 56 | 56 | 0.000 | no |
| @markets | videos | 8008 | 7974 | 2500 | 8008 | 0.004 | no |
| @marklevinshow | videos | 505 | 505 | 505 | 505 | 0.000 | no |
| @mikhaila | videos | 27 | 27 | 27 | 27 | 0.000 | yes |
| @morebridgetphetasy | videos | 206 | 206 | 206 | 206 | 0.000 | no |
| @moreperfectunion | streams | 4 | 4 | 4 | 4 | 0.000 | yes |
| @moreperfectunion | videos | 71 | 71 | 71 | 71 | 0.000 | no |
| @msnow | streams | 335 | 325 | 325 | 335 | 0.030 | no |
| @msnow | videos | 9882 | 9879 | 2500 | 9882 | 0.000 | no |
| @nationalreview | streams | 2 | 2 | 2 | 2 | 0.000 | yes |
| @nationalreview | videos | 191 | 191 | 191 | 191 | 0.000 | no |
| @newdiscourses | videos | 98 | 98 | 98 | 84 | 0.000 | no |
| @newyorker | videos | 51 | 51 | 51 | 51 | 0.000 | no |
| @notsoErudite | streams | 20 | 20 | 20 | 0 | 0.000 | yes |
| @notsoErudite | videos | 43 | 43 | 43 | 43 | 0.000 | yes |
| @nousnetwork | videos | 156 | 156 | 156 | 156 | 0.000 | no |
| @nypost | streams | 114 | 110 | 110 | 114 | 0.035 | no |
| @nypost | videos | 6305 | 6304 | 2500 | 6305 | 0.000 | no |
| @nytimes | videos | 71 | 71 | 71 | 71 | 0.000 | no |
| @oann | streams | 344 | 309 | 309 | 344 | 0.102 | no |
| @oann | videos | 1804 | 1803 | 1803 | 1804 | 0.001 | no |
| @podsaveamerica | videos | 731 | 667 | 667 | 285 | 0.088 | no |
| @ponderingpolitics | streams | 2 | 2 | 2 | 2 | 0.000 | yes |
| @ponderingpolitics | videos | 1470 | 1467 | 1467 | 1338 | 0.002 | no |
| @revleftradio | streams | 3 | 3 | 3 | 3 | 0.000 | yes |
| @revleftradio | videos | 38 | 38 | 38 | 38 | 0.000 | yes |
| @rolandsmartin | streams | 1223 | 584 | 584 | 1223 | 0.522 | no |
| @rolandsmartin | videos | 742 | 742 | 742 | 742 | 0.000 | no |
| @samharrisorg | videos | 116 | 116 | 116 | 76 | 0.000 | no |
| @theGuardian | videos | 39 | 39 | 39 | 39 | 0.000 | yes |
| @thedavidpakmanshow | streams | 5 | 5 | 5 | 5 | 0.000 | yes |
| @thedavidpakmanshow | videos | 1659 | 1641 | 1641 | 1659 | 0.011 | no |
| @thegrayzone7996 | streams | 36 | 36 | 36 | 36 | 0.000 | yes |
| @thegrayzone7996 | videos | 155 | 155 | 155 | 155 | 0.000 | no |
| @thehill | streams | 509 | 505 | 505 | 509 | 0.008 | no |
| @thehill | videos | 4250 | 4249 | 2500 | 4250 | 0.000 | no |
| @theisabelbrown | videos | 141 | 141 | 141 | 141 | 0.000 | no |
| @thejimmydoreshow | streams | 116 | 115 | 115 | 116 | 0.009 | no |
| @thejimmydoreshow | videos | 1146 | 1146 | 1146 | 1146 | 0.000 | no |
| @therationalnational | streams | 7 | 7 | 7 | 7 | 0.000 | yes |
| @therationalnational | videos | 142 | 142 | 142 | 142 | 0.000 | no |
| @thewarningwithsteveschmidt | streams | 113 | 110 | 110 | 109 | 0.026 | no |
| @thewarningwithsteveschmidt | videos | 363 | 289 | 289 | 223 | 0.204 | no |
| @thomhartmann | videos | 784 | 784 | 784 | 784 | 0.000 | no |
| @timesofindia | streams | 3582 | 2295 | 2295 | 3582 | 0.359 | no |
| @timesofindia | videos | 9928 | 9926 | 2500 | 9928 | 0.000 | no |
| @triggerpod | streams | 6 | 6 | 6 | 6 | 0.000 | yes |
| @triggerpod | videos | 152 | 151 | 151 | 105 | 0.007 | no |
| @turningpointusa | streams | 14 | 13 | 13 | 14 | 0.071 | yes |
| @turningpointusa | videos | 183 | 183 | 183 | 183 | 0.000 | no |
| @underthedesknews | streams | 119 | 115 | 115 | 119 | 0.034 | no |
| @underthedesknews | videos | 79 | 79 | 79 | 79 | 0.000 | no |
| @usefulidiots | streams | 69 | 12 | 12 | 69 | 0.826 | yes |
| @usefulidiots | videos | 190 | 186 | 186 | 165 | 0.021 | no |
| @wethefifth | streams | 2 | 2 | 2 | 2 | 0.000 | yes |
| @wethefifth | videos | 112 | 112 | 112 | 112 | 0.000 | no |
| @winston_marshall | videos | 109 | 109 | 109 | 90 | 0.000 | no |
| @wsj | streams | 11 | 11 | 11 | 11 | 0.000 | yes |
| @wsj | videos | 119 | 119 | 119 | 119 | 0.000 | no |
| @zeteo | streams | 25 | 25 | 25 | 25 | 0.000 | yes |
| @zeteo | videos | 206 | 206 | 206 | 206 | 0.000 | no |
| https://rumble.com/c/BannonsWarRoom | videos | 4619 | 4506 | 2500 | 0 | 0.025 | no |
| https://rumble.com/c/GGreenwald | videos | 76 | 76 | 76 | 0 | 0.000 | no |
| https://rumble.com/c/TheAlexJonesShowLive | videos | 517 | 513 | 513 | 0 | 0.008 | no |
| https://rumble.com/c/nickjfuentes | videos | 309 | 305 | 305 | 0 | 0.013 | no |
| https://rumble.com/c/russellbrand | videos | 262 | 259 | 259 | 0 | 0.011 | no |


## Runtime and cost per stage (last run and longest run of each; a --label-only re-run of topics is seconds, the fit was minutes; local Ollama models cost $0)

| stage | seconds_last_run | seconds_longest_run | finished | llm_calls | output_tokens | api_cost_usd | notes |
|---|---|---|---|---|---|---|---|
| stage0_prepare | 34.4 | 34.4 | 2026-09-14T21:03:57+00:00 |  |  |  | min_share=0.2, min_count=10, rows=309596, unique=300420, balanced=189240, low_n_groups=124 |
| stage0c_annotate | 10.4 | 108.8 | 2026-09-14T21:05:00+00:00 |  |  |  | model=en_core_web_sm, titles=292688, all_caps=11192, proper_lexicon=11667, acronyms=956 |
| stage0b_lanes | 0.4 | 0.4 | 2026-09-14T20:41:31+00:00 |  |  |  |  |
| stage1a_embed | 5.3 | 289.2 | 2026-09-14T21:05:09+00:00 |  |  |  | model=sentence-transformers/all-mpnet-base-v2, device=mps, n=292688, dim=768 |
| stage2c_llm_rate | 6265.5 | 6265.5 | 2026-09-14T22:35:38+00:00 | 172 | 69430 | 0.0 | model=qwen3:14b, temperature=0.0, prompt_id=title-style-v3, cache_hits=2, llm_seconds=6264.3, n_rated=3000,... |
| stage2a_features | 68.9 | 69.6 | 2026-09-14T21:06:19+00:00 |  |  |  |  |
| stage1_topics | 11.5 | 6343.9 | 2026-09-14T23:08:54+00:00 | 3 | 72 | 0.0 | fit_size=100000, min_cluster_size=80, min_samples=15, max_topics=250, label_model=qwen3:14b, fit_n=100041, ... |
| stage2b_factors | 2.3 | 2.3 | 2026-09-14T23:10:34+00:00 |  |  |  | n_factors_forced=None, n_cells=2029, n_features=74, retained=12, parallel=16, kmo=0.725 |
| stage2d_validate | 0.7 | 0.7 | 2026-09-14T23:10:35+00:00 |  |  |  | n_rated_matched=3000, n_creator_groups=318, n_retest=300 |
| stage3_formats | 11.0 | 11.3 | 2026-09-14T23:10:16+00:00 |  |  |  | curiosity_gap_holdout_f1=0.1765, outrage_holdout_f1=0.7869, humor_holdout_f1=0.0 |
| stage4_landscape | 24.0 | 24.0 | 2026-09-14T23:15:32+00:00 |  |  |  | crossposted_titles=2237, cluster_runs=4, shared_titles_any=1575, shared_titles_cross_org=474, shared_titles... |
| stage5a_timeline | 1.4 | 1.4 | 2026-09-14T23:10:37+00:00 |  |  |  | lane_month_rows=215, top30=30, topic_change_rows=1667 |
| stage5b_engagement | 9.4 | 9.4 | 2026-09-14T23:10:47+00:00 |  |  |  | creator_genre_models=252 |
| stage5c_hits | 28.9 | 28.9 | 2026-09-15T01:01:53+00:00 |  |  |  | groups=252, powerlaw_like=1 |
| report_data | 3.1 | 3.1 | 2026-09-15T18:37:50+00:00 |  |  |  | creators=274 |
| report | 24.6 | 24.6 | 2026-09-15T18:56:47+00:00 |  |  |  | cards=274 |
| stage6_profiles | 21.1 | 22.3 | 2026-09-15T12:45:34+00:00 |  |  |  | acronyms=956, twin_pairs=2680 |
| stage7_leaning | 17.3 | 4883.0 | 2026-09-15T18:56:22+00:00 |  |  | 0.0 | backend=claude-code, prompt_id=leaning-v1, llm_seconds=4860.5, reported_cost_usd=36.4107, n_labelled_by_all... |
| allotax | 11.7 | 11.9 | 2026-09-15T18:58:17+00:00 |  |  |  | alpha=0.3333, top_n=40, figures=5 |
| leaning_lexicon | 1.7 | 1.7 | 2026-09-15T18:52:59+00:00 |  |  |  | cutoff=1.96 |


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
