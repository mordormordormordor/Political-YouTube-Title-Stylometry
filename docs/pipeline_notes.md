# Title Stylometry

A second corpus, separate from the caption pipeline: **video titles** (plus the
light metadata that comes free with them) for a much wider set of creators, so
title style can be compared across the political-media landscape - lexicon,
capitalisation, punctuation, framing, length, clickbait devices, how titles
drift over time, and how a channel's titles relate to its transcripts where we
have them.

Creators: `data/creator_lists/title_stylometry_creators.txt` - 269 YouTube
channels + 5 Rumble channels. The 33 marked `# caption corpus` are the channels
whose captions live in `data/subtitles/`, so title-vs-transcript comparisons are
possible for them.

## Why this is fast

The caption pull needs three or four requests **per video** with polite sleeps
(about 10 s each). Titles do not: yt-dlp's flat channel listing returns 30 videos
per request with title, duration, view count, live status and an approximate
upload date, and it stops paging as soon as it is past the date floor. A channel
back to January costs seconds; the whole list is well under two hours. Rumble
channels are read from Rumble's own listing pages (25 per page, exact dates).

## Fetching

Agreed scope (2026-09-14): window 2026-01-01 → today, YouTube `videos` + `streams`
tabs, no thumbnail URLs. Start it detached (survives a closed terminal; `caffeinate`
keeps the Mac awake). Check it is not already running first (see below).

```bash
cd "/Users/sanji/Desktop/Visual Studio/Political Quotes Project" && nohup caffeinate -i .venv/bin/python -u -m pipeline_titles.ingest.fetch_video_metadata --since 2026-01-01 --tabs videos streams >> data/titles/fetch.log 2>&1 &
```

Progress (reads the ledger only, no network):

```bash
cd "/Users/sanji/Desktop/Visual Studio/Political Quotes Project" && pgrep -f fetch_video_metadata >/dev/null && echo RUNNING || echo "NOT RUNNING"; .venv/bin/python -m pipeline_titles.ingest.fetch_video_metadata --status --tabs videos streams; tail -2 data/titles/fetch.log
```

Stop: `pkill -f fetch_video_metadata`. Re-running the start command resumes where it stopped.

Rumble throttles per IP after roughly 150 listing pages in a short span and then
returns HTTP 429 for a long while (an hour or more). The fetcher backs off on 429
(30 s, 60 s, ... up to six tries), but a large channel such as Bannon's War Room (150+
pages for the 2026 window) needs a slow pace from the start: re-run only the Rumble
jobs with `--sleep 10`, and if it still 429s at page 5, wait an hour before trying again.
Only unsettled jobs run on a resume, so this never re-lists the YouTube channels.

Resume-safe: each (creator, tab) that finished is recorded in
`data/titles/fetch_log.jsonl` and skipped next time; `--refresh` re-fetches.
A failing handle is logged with its error and the run continues.

## Data (`data/titles/`)

| File | Tracked | One row per | Contents |
|------|---------|-------------|----------|
| `videos.csv` | no (~70 MB) | creator × tab × video | the analysis table (columns below); archive a dated copy off-repo if the snapshot matters |
| `channels.jsonl` | yes | creator × tab | channel name/id, follower count, description, tags, verified flag, videos listed |
| `videos.jsonl` | no | creator × tab × video | every flat field yt-dlp returned (superset of the CSV), rebuildable |
| `fetch_log.jsonl` | no | creator × tab | ok/error, listed/kept/undated counts, seconds, timestamp - the resume ledger |

`videos.csv` columns: `creator` (handle or Rumble URL as listed), `platform`,
`tab` (videos / streams / shorts), `video_id`, `title`, `published`
(YYYY-MM-DD), `date_precision` (`approx` for YouTube - listing dates are only
month-accurate; `exact` for Rumble), `duration` (s), `view_count` (at fetch
time; blank for Rumble), `live_status`, `url`, `channel_name`, `channel_id`.

Not collected (each would need one request per video): descriptions, tags,
like/comment counts, exact YouTube upload dates, chapters. If a subset ever
needs them, fetch that subset per video rather than the whole corpus.

## Layout

```
pipeline_titles/
  ingest/fetch_video_metadata.py   # creator list -> data/titles/ (this README's "Fetching")
  common.py        # paths, seed, genres, low-n / balancing rules, stage timer (runtimes.jsonl)
  prepare.py       # Stage 0: normalise titles (brand/episode/date stripping), repeats, balanced subset
  lane_seed.py     # Stage 0: proposed lane / organisation / clipper per creator (edit lanes.csv, not this)
  lanes.py         # Stage 0: writes data/titles/analysis/lanes.csv (refuses to overwrite without --force)
  annotate.py      # Stage 0c: spaCy tokens / POS / entities per unique title (truecases ALL-CAPS titles)
  embed.py         # Stage 1a: all-mpnet-base-v2 sentence embeddings (cached, incremental)
  topics.py        # Stage 1: BERTopic on a ~100k creator-stratified sample; nearest-centroid assignment;
                   #          LLM topic labels + political flag; per-creator mix, lane shares, monthly spikes
  llm_rate.py      # Stage 2c: 3,000-title stratified sample rated by a local Ollama model (+300 retest)
  lexicons.py      # word lists used by the style features (documented in the methods appendix)
  features.py      # Stage 2a: ~75 title-level style features -> creator x genre x month (features.csv),
                   #          formulaicity, Heaps' / Zipf lexical diversity with sample-size sensitivity
  factors.py       # Stage 2b: exploratory factor analysis (parallel analysis, minres + oblimin), scores,
                   #          topic control (dimensions.csv)
  validate.py      # Stage 2d: LLM ratings vs factor scores, candidate-label mapping, test-retest
  formats.py       # Stage 3: regex formats on raw titles; hook classifier trained on the LLM labels
  landscape.py     # Stage 4: style vs topic clusterings vs lanes (ARI), neighbours, entities, shared titles
  timeline.py      # Stage 5a: monthly drift per lane and per creator; month-to-month topic change
  engagement.py    # Stage 5b: within-creator regressions of log views on style (month + topic controls)
  hits.py          # Stage 5c: Gini / top-10 % share / Clauset-Shalizi-Newman tail fit vs lognormal
  report_data.py   # profile-card JSON (reports/cards.json)
  report.py, report_html.py   # Markdown report + methods appendix + cards + HTML page
  run_all.py       # runs every stage in order (--from <stage>, --skip <stages>)
  reports/         # title_stylometry_report.md, methods_appendix.md, headlines.md, cards/, title_stylometry.html
tests/test_titles_*.py             # pure-helper tests (no data files, no network)
```

## Analysis pipeline

Install the stack once (`pip install -r requirements-titles.txt`, then
`python -m spacy download en_core_web_sm`) and run

```bash
cd "/Users/sanji/Desktop/Visual Studio/Political Quotes Project" && .venv/bin/python -m pipeline_titles.run_all
```

Every stage is a separate `python -m pipeline_titles.<stage>` that reads the previous
stage's files under `data/titles/analysis/` and appends its wall-clock time (and LLM
call / token counts) to `data/titles/analysis/runtimes.jsonl`. The interface tables
are `features.csv`, `dimensions.csv`, `topics.csv`, `labels.csv` and `lanes.csv`.

LLM work (title ratings, topic labels) uses the local Ollama model `qwen3:14b`
(no `OPENAI_API_KEY` is configured on this machine); every response is cached under
`data/titles/analysis/cache/llm*/`, so a re-run over an unchanged corpus makes no
model calls. Ollama serves requests one at a time: run `llm_rate` before `topics`
if you re-fit the topic model, or the topic labelling crawls behind the rating batches.

Hand-edited files that survive re-runs: `data/titles/analysis/lanes.csv` (the lane
proposal; correct it, then re-run from `factors`), `data/titles/analysis/factor_names.json`
(names for the retained factors), `pipeline_titles/reports/headlines.md` (the prose
headline findings; re-check after a corpus refresh).
