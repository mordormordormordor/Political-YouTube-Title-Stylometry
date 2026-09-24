# Political YouTube Title Stylometry

How 274 political-media creators (269 YouTube channels, 5 Rumble channels) title their
videos: every title they published between 2026-01-01 and 2026-09-14 (309,596 titles),
described along data-driven style dimensions, controlled for topic, clustered into a
landscape, tracked month by month, and tested against views.

There are no transcripts, descriptions, tags or thumbnails in this corpus: titles plus the
listing-level metadata that comes with them are the entire dataset.

## Results

Start at [`pipeline_titles/reports/README.md`](pipeline_titles/reports/README.md): the
write-up is split into twelve documents, one per question, each explaining its finding
with the tables that carry it and its caveats. No channel is categorized by hand: the one
grouping of channels used anywhere is the left / neutral / right channel group of document
14, how each channel's own titles read to a frontier model. Seven follow the pipeline's stages:

1. [The corpus](pipeline_titles/reports/01_corpus.md): what is analyzed, what was stripped, the creator table
2. [Topics](pipeline_titles/reports/02_topics.md)
4. [Formats and hooks](pipeline_titles/reports/04_formats_and_hooks.md)
5. [The landscape](pipeline_titles/reports/05_landscape.md)
6. [Drift](pipeline_titles/reports/06_drift.md)
7. [Zipf's law and views](pipeline_titles/reports/07_views.md): Zipf's law in title vocabulary
   and in views, and views over time, each cut by channel group, by title label (left / neither /
   right) and by capitalization style (ALL CAPS, selective CAPS, Title Case, Sentence case, mixed, short)
8. [Null results and caveats](pipeline_titles/reports/08_null_results_and_caveats.md)

Five answer a question of their own, each with its method and limitations:

9. [Stylistic twins](pipeline_titles/reports/09_stylistic_twins.md): which left and right
   channels title the same way
11. [Capitalization and vocabulary](pipeline_titles/reports/11_capitalization_and_vocabulary.md)
12. [Arousal index](pipeline_titles/reports/12_arousal_index.md): a 0-1 emotional-charge index
    per channel
13. [Signature keywords](pipeline_titles/reports/13_signature_keywords.md): the words each
    channel over-uses
14. [Political leaning from titles](pipeline_titles/reports/14_political_leaning.md): two
    levels. Titles: a frontier model labels 12,478 titles left / right / neither from the title
    text alone, and the vocabulary of each label is analyzed (allotaxonographs, log-odds, a
    lexicon check). Channels: each channel's score from its sampled titles sorts the 274
    channels into left, neutral and right groups, whose whole output is then compared

- `pipeline_titles/reports/all_tables.md`: the reference dump of every table in one file.
- `pipeline_titles/reports/methods_appendix.md`: preprocessing, stopwords, feature
  definitions, lexicons, factor loadings, validation numbers, sample sizes, prompts,
  runtimes.
- `pipeline_titles/reports/word_network.html`: the word-association network to explore (2,767
  words, 11,714 edges). It opens on the communities, one disc each, joined by the pairs that
  cross between them; a community opens into its words; a word gives its partners and a
  timeline of its months. Degree and strength follow the edges on screen (month, lift
  threshold), betweenness is the year's, and community detection is Louvain run in the page,
  with a resolution slider and a reshuffle. The left, neutral and right channels each have
  their own network (the same test on their titles alone), and the whole network's edges can
  be colored by which audience makes the pair. `--no-leaning` writes `word_network_site.html`,
  the build with nothing derived from the leaning labels, for the website. `python -m pipeline_titles.network_page` rebuilds
  it. Self-contained; open it directly in a browser.
- `pipeline_titles/reports/title_stylometry.html`: the interactive page. A creator selector
  renders each profile card, and the two landscape maps (style space, topic space) show
  every creator with names on hover and the selected creator's neighbors drawn in. It is
  self-contained; open it directly in a browser.
- `pipeline_titles/reports/figures/`: the static figures embedded in the documents
  (`python -m pipeline_titles.figures` redraws them from the tables).
- `pipeline_titles/reports/cards/<creator>.md`: one fixed-layout profile card per creator.
- `data/titles/analysis/`: machine-readable tables. The interface between stages is
  `features.csv` (creator x genre x month), `dimensions.csv` (creator scores, raw and
  topic-controlled), `topics.csv` (title -> topic), `labels.csv` (the 3,000 LLM-rated
  titles), `leaning_labels.csv.gz` (the 12,478 titles labeled left / right / neither by the
  judge), `leaning_by_creator.csv` (each channel's score and its left / neutral / right group),
  `creators.csv` (channel name / organization / clipper / subscribers per creator).

Headline findings from the 2026-09-14 run are in `pipeline_titles/reports/headlines.md`.

## Data

`data/titles/videos.csv.gz` is the corpus (gzipped; pandas reads it as is): one row per video with `creator`, `platform`,
`tab` (`videos` = edited uploads, `streams` = live-stream VODs), `video_id`, `title`,
`published` (month-accurate for YouTube, exact for Rumble), `duration`, `view_count`
(YouTube only, a snapshot at fetch time), `live_status`, `url`, `channel_name`,
`channel_id`. `data/titles/channels.jsonl` holds subscriber counts, descriptions and tags
per creator x tab. The creator list is `data/creator_lists/title_stylometry_creators.txt`.
The raw yt-dlp superset (`videos.jsonl`, 176 MB) is not versioned; the fetcher rebuilds it. The large analysis tables (`topics`, `labels`, `features`, `creator_topic_mix`, `dimensions_monthly`, `drift_creator_monthly`, the leaning labels) are stored as `.csv.gz` for the same reason; every reader takes either form.

Fetching (yt-dlp flat channel listings, no per-video requests):

```bash
.venv/bin/python -m pipeline_titles.ingest.fetch_video_metadata --since 2026-01-01 --tabs videos streams
```

See `docs/pipeline_notes.md` for the fetch notes (Rumble rate limits, resume behavior).

## Setup

Python 3.12+ (developed on 3.14.2, Apple M4 Pro, 24 GB).

```bash
python -m venv .venv
.venv/bin/pip install -r requirements-dev.txt
.venv/bin/python -m spacy download en_core_web_sm
```

Exact publish dates (optional; without them YouTube titles are dated to the month, which
is all yt-dlp's channel listing gives) come from the YouTube Data API v3, which is free:
in the [Google Cloud Console](https://console.cloud.google.com/) make a project, enable
*YouTube Data API v3* under APIs & Services, create an API key under Credentials (restrict
it to that API), and put it in `.env` at the repo root (`cp .env.example .env`). The
corpus is about 6,100 `videos.list` calls at one quota unit each against a daily quota of
10,000, so one run:

```bash
.venv/bin/python -m pipeline_titles.ingest.fetch_publish_dates --dry-run    # what would be fetched
.venv/bin/python -m pipeline_titles.ingest.fetch_publish_dates --limit 500  # a first look
.venv/bin/python -m pipeline_titles.ingest.fetch_publish_dates              # the rest; resumable
.venv/bin/python -m pipeline_titles.run_all                                 # then the pipeline over exact dates
```

The fetch writes `data/titles/publish_dates.csv.gz` (tracked) from an untracked ledger it
resumes from; if the day's quota runs out it stops and says how many ids remain. Once the
CSV exists, `prepare` dates every YouTube title to the day (`published`, `date_precision =
exact`, plus `published_at` to the second; a stream is dated by its actual start), keeps only
the titles published inside the corpus window (`WINDOW_FROM`..`WINDOW_TO` in `common.py`;
the listing's approximate dates had let about 16,000 December 2025 titles in as January),
and the site's import picks the dates up from the parquet.

The title ratings and topic labels are cached under `data/titles/analysis/cache/llm*/`, so
re-running over an unchanged corpus makes no model calls.

The leaning labels (document 14) come from a frontier model through the Claude Code CLI in
print mode, which a Claude Pro/Max subscription covers (`npm install -g @anthropic-ai/claude-code`,
then `claude` once to log in; do not set `ANTHROPIC_API_KEY`, or the CLI bills the API):

```bash
.venv/bin/python -m pipeline_titles.leaning --n-per-creator 50
```

Titles go to the judge in a seeded random order, twenty to a call, so a batch mixes channels
and a title is never read beside its channel's other titles (`--no-shuffle` batches in sample
order instead; `--relabel` starts afresh and keeps the old labels in an untracked file).
Usage-limit replies are waited out. The sample is a base draw of 16 titles per creator
plus a top-up to 50, spread evenly across months, for creators with at least 50 edited
uploads (`--n-per-creator`, `--min-uploads`); the base draw never changes, so earlier
labels are reused and only new titles are sent to a model. The labels of record come from
three runs (`leaning_runs.json`): the base draw and then the top-up were labeled in sample
order, then every title again in shuffled batches, which is the labeling used; the first
reading is kept (`leaning_labels_channel_batched.csv.gz`) and compared with it title by title
and channel by channel (`leaning_two_readings.json`: 88 % agreement, channels at Spearman
0.98). `--repeat` reads every title once more with a fresh shuffle seed into its own file
(`leaning_labels_repeat.csv.gz`, run 4; the labels of record are untouched) and compares the
three readings (`leaning_repeat.json`: the two shuffled readings agree on 91 % of titles,
channels at 0.99, so the judge's own noise is about one label in eleven and the channel
batching cost about two points more). `--analyze-only` recomputes every table (channel
scores, the split-half, base-vs-top-up and readings checks, words, group x month) from the
labels on disk without a model call.
`--prompt-version v2` also asks for the title's target (who it attacks), which separates
"attacks Trump" from "speaks for the left".
The stage writes a blind 200-title adjudication sheet
(`data/titles/analysis/leaning_human_sheet.csv`); fill `human_label` and re-run with
`--analyze-only --human-labels <that file>` to score every model against a human.

The allotaxonographs of document 14 (rank-turbulence divergence, Dodds et al. 2023) are
drawn by [allotaxonometer-ui](https://github.com/Vermont-Complex-Systems/allotaxonometer-ui),
the Computational Story Lab's own renderer (the code behind their web app and
[py-allotax](https://github.com/compstorylab/py-allotax)), through Node and Puppeteer. One-time
setup (Node 18+; Puppeteer fetches its own Chrome, about 170 MB, into `~/.cache/puppeteer`):

```bash
cd pipeline_titles/allotax_js && npm install
```

`python -m pipeline_titles.allotax` then renders the five comparisons in a few seconds (it
also runs inside `report`); without Node or that install the stage prints why it skipped and
the tracked figures stay as they are. The repo's own `rank_turbulence_divergence`
(`pipeline_titles/textstats.py`) reproduces the library's numbers, so the tables and the
figures agree.

## Running the pipeline

```bash
.venv/bin/python -m pipeline_titles.run_all            # everything, in order
.venv/bin/python -m pipeline_titles.run_all --from factors --skip llm_rate
```

Stages (each a `python -m pipeline_titles.<stage>` that reads the previous stage's files
from `data/titles/analysis/` and appends its runtime to `runtimes.jsonl`):

| stage | what it does |
|---|---|
| `prepare` | normalize titles (strip show names, episode numbers, dates, brand tags by a per-creator 20 % rule), mark verbatim repeats, low-n groups, the creator-balanced subset; Zipf check |
| `creators` | write the creator table (`creators.csv`: organization / clipper / subscribers; edit the CSV, not `creator_seed.py`) |
| `leaning` | document 14 and the channel groups every later stage reports by: left / right / neither labels from Claude Opus (title text only, shuffled batches, cached; every title was also read in channel-batched order and once more with a fresh shuffle, and the three readings are compared); channel scores and the left / neutral / right groups they define; split-half, base-vs-top-up and re-reading reliability; group x month; weighted log-odds and rank-turbulence words for the titles and for the groups' whole output; the log-odds lexicon and its out-of-fold check |
| `annotate` | spaCy tokens, POS, entities per unique title (ALL-CAPS titles truecased first) |
| `embed` | sentence embeddings (all-mpnet-base-v2), cached and incremental |
| `topics` | BERTopic on a ~100k creator-stratified sample, nearest-centroid assignment for all titles, LLM labels and political flag, per-creator mix, channel-group shares, monthly spikes |
| `llm_rate` | 3,000-title stratified sample rated 1-5 on five candidate dimensions plus hook flags and a format label, with a 300-title retest |
| `features` | ~75 title-level style features -> creator x genre x month; formulaicity; Heaps' and Zipf lexical diversity with sample-size sensitivity |
| `factors` | exploratory factor analysis (parallel analysis, minres, oblimin), factor scores per cell, creator and title, topic control |
| `validate` | LLM ratings vs factor scores, candidate-label mapping, test-retest reliability |
| `formats` | regex formats on raw titles; hook classifier trained on the LLM labels and applied to every title |
| `landscape` | style vs topic clusterings vs the channel groups (ARI), nearest neighbors, who gets named, shared titles and templates |
| `timeline` | monthly drift per channel group and creator; month-to-month topic change |
| `engagement` | within-creator regressions of log views on style with month and topic controls |
| `hits` | Gini, top-10 % share, Clauset-Shalizi-Newman tail fit vs lognormal |
| `profiles` | the question documents 9, 11, 12, 13: stylistic twins across the left / right groups, capitalization profiles and top words, the arousal index, signature keywords |
| `year` | the site's article No. 3, the year in words: the most frequent content words by channel-weighted share with their shout rates, each month's standout words by weighted log-odds over channel-months, the vocabulary's channel-weighted share by week, and the widest weekly spikes, each with the period's most-viewed title (`year_words.csv`, `year_months.csv`, `year_weeks_meta.csv`, `year_weeks.csv`, `year_spikes.csv`) |
| `associations` | word association in titles (`docs/word_association_protocol.md`): daily co-movement of every term with an autocorrelation-adjusted screen and an independent-shift null, title-level co-mention tested by Cochran-Mantel-Haenszel over creator x week strata with a curveball permutation null, both replicated across two channel halves; the association network and its communities, month-by-month neighborhoods and drift, and the Iran / war / Epstein case study (`assoc_*.csv`). `--battery spikes:N` runs the case-study tests over every pair of the N biggest spikes (80 words take 53 minutes; not part of a `run_all` run) |
| `zipf_views` | document 7: Zipf's law for words (per channel group, title label and capitalization style, with size-matched exponents) and for views (rank-size slopes), views by publication month, and views relative to each channel's monthly baseline by capitalization style and title label |
| `allotax` | allotaxonographs for document 14 (needs Node; see above) |
| `report_data`, `report` | cards JSON, Markdown report, methods appendix, cards, HTML page |

Hand-edited files that survive re-runs: `data/titles/analysis/creators.csv`,
`data/titles/analysis/factor_names.json`, `pipeline_titles/reports/headlines.md`.

Tests (pure helpers, no data or network): `.venv/bin/python -m pytest -q`.

## Layout

```
pipeline_titles/        the pipeline (see the table above); ingest/ holds the corpus fetcher; allotax_js/ the Node renderer for the allotaxonographs
pipeline_titles/reports/ report, appendix, cards, HTML
data/titles/            corpus + analysis/ outputs
data/creator_lists/     the creator list
docs/                   the analysis brief (ANALYSIS_PROMPT.md) and fetch notes
tests/                  pytest suite
```

This project was split out of the Political Quotes Project on 2026-09-14; the two Rumble /
YouTube listing helpers under `pipeline_titles/ingest/` are vendored from there.
