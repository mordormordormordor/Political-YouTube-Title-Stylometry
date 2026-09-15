# Political YouTube Title Stylometry

How 274 political-media creators (269 YouTube channels, 5 Rumble channels) title their
videos: every title they published between 2026-01-01 and 2026-09-14 (309,596 titles),
described along data-driven style dimensions, controlled for topic, clustered into a
landscape, tracked month by month, and tested against views.

There are no transcripts, descriptions, tags or thumbnails in this corpus: titles plus the
listing-level metadata that comes with them are the entire dataset.

## Results

Start at [`pipeline_titles/reports/README.md`](pipeline_titles/reports/README.md): the
write-up is split into fourteen documents, one per question, each explaining its finding
with the tables that carry it and its caveats. Eight follow the pipeline's stages:

1. [Corpus and lanes](pipeline_titles/reports/01_corpus_and_lanes.md)
2. [Topics](pipeline_titles/reports/02_topics.md)
3. [Style dimensions](pipeline_titles/reports/03_style_dimensions.md)
4. [Formats and hooks](pipeline_titles/reports/04_formats_and_hooks.md)
5. [The landscape](pipeline_titles/reports/05_landscape.md)
6. [Drift](pipeline_titles/reports/06_drift.md)
7. [Views](pipeline_titles/reports/07_views.md)
8. [Null results and caveats](pipeline_titles/reports/08_null_results_and_caveats.md)

Six answer a question of their own, each with its method and limitations:

9. [Stylistic twins](pipeline_titles/reports/09_stylistic_twins.md): which left and right
   commentary creators title the same way
10. [Outrage by lane](pipeline_titles/reports/10_outrage_by_lane.md): how much of political
    YouTube is framed as outrage, with confidence intervals
11. [Capitalisation and vocabulary](pipeline_titles/reports/11_capitalisation_and_vocabulary.md)
12. [Arousal index](pipeline_titles/reports/12_arousal_index.md): a 0-1 emotional-charge index
    per channel
13. [Signature keywords](pipeline_titles/reports/13_signature_keywords.md): the words each
    channel over-uses
14. [Political leaning from titles](pipeline_titles/reports/14_political_leaning.md): three
    models (two local, one frontier) label 12,478 titles left / right / neither, 50 per ranked
    channel; what each model sees, how reliable the channel score is, channel scores against
    the channels' own descriptions and the lanes, and the words behind each label

- `pipeline_titles/reports/all_tables.md`: the reference dump of every table in one file.
- `pipeline_titles/reports/methods_appendix.md`: preprocessing, stopwords, feature
  definitions, lexicons, factor loadings, validation numbers, sample sizes, prompts,
  runtimes.
- `pipeline_titles/reports/title_stylometry.html`: the interactive page. A creator selector
  renders each profile card, and the two landscape maps (style space, topic space) show
  every creator with names on hover and the selected creator's neighbours drawn in. It is
  self-contained; open it directly in a browser.
- `pipeline_titles/reports/figures/`: the static figures embedded in the documents
  (`python -m pipeline_titles.figures` redraws them from the tables).
- `pipeline_titles/reports/cards/<creator>.md`: one fixed-layout profile card per creator.
- `data/titles/analysis/`: machine-readable tables. The interface between stages is
  `features.csv` (creator x genre x month), `dimensions.csv` (creator scores, raw and
  topic-controlled), `topics.csv` (title -> topic), `labels.csv` (the 3,000 LLM-rated
  titles), `leaning_labels.csv` (the 12,478 titles labelled left / right / neither by three
  judges), `lanes.csv` (lane / organisation / clipper per creator; a proposal to correct).

Headline findings from the 2026-09-14 run are in `pipeline_titles/reports/headlines.md`.

## Data

`data/titles/videos.csv` is the corpus: one row per video with `creator`, `platform`,
`tab` (`videos` = edited uploads, `streams` = live-stream VODs), `video_id`, `title`,
`published` (month-accurate for YouTube, exact for Rumble), `duration`, `view_count`
(YouTube only, a snapshot at fetch time), `live_status`, `url`, `channel_name`,
`channel_id`. `data/titles/channels.jsonl` holds subscriber counts, descriptions and tags
per creator x tab. The creator list is `data/creator_lists/title_stylometry_creators.txt`.
The raw yt-dlp superset (`videos.jsonl`, 176 MB) is not versioned; the fetcher rebuilds it.

Fetching (yt-dlp flat channel listings, no per-video requests):

```bash
.venv/bin/python -m pipeline_titles.ingest.fetch_video_metadata --since 2026-01-01 --tabs videos streams
```

See `docs/pipeline_notes.md` for the fetch notes (Rumble rate limits, resume behaviour).

## Setup

Python 3.12+ (developed on 3.14.2, Apple M4 Pro, 24 GB).

```bash
python -m venv .venv
.venv/bin/pip install -r requirements-dev.txt
.venv/bin/python -m spacy download en_core_web_sm
```

LLM steps (title ratings, topic labels, leaning labels) use local Ollama models
(`qwen3:14b`, `gemma3:12b`); every response is cached under
`data/titles/analysis/cache/llm*/`, so re-running over an unchanged corpus makes no
model calls. There is no paid API involved.

The leaning stage can also use a frontier model through the Claude Code CLI in print
mode, which a Claude Pro/Max subscription covers (`npm install -g @anthropic-ai/claude-code`,
then `claude` once to log in; do not set `ANTHROPIC_API_KEY`, or the CLI bills the API):

```bash
.venv/bin/python -m pipeline_titles.leaning --backend claude-code --models opus
```

Usage-limit replies are waited out. The sample is a base draw of 16 titles per creator
plus a top-up to 50, spread evenly across months, for creators with at least 50 edited
uploads (`--n-per-creator`, `--min-uploads`); the base draw never changes, so earlier
labels are reused and only new titles are sent to a model. `--analyse-only` recomputes
every table (agreement, channel scores, yardsticks, split-half and base-vs-top-up
reliability, words, lane x month) from the labels on disk without a model call.
`--prompt-version v2` also asks for the title's target (who it attacks), which separates
"attacks Trump" from "speaks for the left".
The stage writes a blind 200-title adjudication sheet
(`data/titles/analysis/leaning_human_sheet.csv`); fill `human_label` and re-run with
`--analyse-only --human-labels <that file>` to score every model against a human.

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
| `prepare` | normalise titles (strip show names, episode numbers, dates, brand tags by a per-creator 20 % rule), mark verbatim repeats, low-n groups, the creator-balanced subset; Zipf check |
| `lanes` | write the lane / organisation / clipper proposal (`lanes.csv`; edit the CSV, not `lane_seed.py`) |
| `annotate` | spaCy tokens, POS, entities per unique title (ALL-CAPS titles truecased first) |
| `embed` | sentence embeddings (all-mpnet-base-v2), cached and incremental |
| `topics` | BERTopic on a ~100k creator-stratified sample, nearest-centroid assignment for all titles, LLM labels and political flag, per-creator mix, lane shares, monthly spikes |
| `llm_rate` | 3,000-title stratified sample rated 1-5 on five candidate dimensions plus hook flags and a format label, with a 300-title retest |
| `features` | ~75 title-level style features -> creator x genre x month; formulaicity; Heaps' and Zipf lexical diversity with sample-size sensitivity |
| `factors` | exploratory factor analysis (parallel analysis, minres, oblimin), factor scores per cell, creator and title, topic control |
| `validate` | LLM ratings vs factor scores, candidate-label mapping, test-retest reliability |
| `formats` | regex formats on raw titles; hook classifier trained on the LLM labels and applied to every title |
| `landscape` | style vs topic clusterings vs lanes (ARI), nearest neighbours, who gets named, shared titles and templates |
| `timeline` | monthly drift per lane and creator; month-to-month topic change |
| `engagement` | within-creator regressions of log views on style with month and topic controls |
| `hits` | Gini, top-10 % share, Clauset-Shalizi-Newman tail fit vs lognormal |
| `allotax` | allotaxonographs for document 14 (needs Node; see above) |
| `report_data`, `report` | cards JSON, Markdown report, methods appendix, cards, HTML page |

Hand-edited files that survive re-runs: `data/titles/analysis/lanes.csv`,
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
