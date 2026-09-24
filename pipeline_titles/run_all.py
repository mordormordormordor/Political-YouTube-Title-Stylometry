"""Run the whole Title Stylometry pipeline in order (each stage is re-runnable on
its own; every stage reads the previous stage's files from disk).

    python -m pipeline_titles.run_all                 # everything
    python -m pipeline_titles.run_all --from factors  # resume from a stage
    python -m pipeline_titles.run_all --skip llm_rate embed   # skip cached long stages
    python -m pipeline_titles.run_all --incremental   # after channels were added: keep every sample of record

Stages, in order: prepare, creators, leaning, annotate, embed, topics, llm_rate,
features, factors, validate, formats, landscape, timeline, engagement, hits,
profiles, zipf_views, report_data, report.
The leaning stage runs early because its left / neutral / right channel groups are
the grouping every later stage reports by. The LLM stages (leaning, llm_rate,
topics' labeling) are fully cached, so a re-run with an unchanged corpus makes no
model calls.

--incremental is the run after channels are added to the corpus (pipeline_titles.add_channels
runs it): the stages that draw a sample keep their sample of record and only take the new
channels in. creators appends the new rows to creators.csv (hand corrections kept); leaning
labels the new channels' titles only (its default when a labels file exists); topics assigns
the new titles to the fitted topics (--label-only) instead of refitting; llm_rate re-keys
its rated sample to the new table (--rekey) instead of redrawing it, so the new channels are
not in the 3,000-title rating sample. Every other stage recomputes over the whole corpus.
"""

from __future__ import annotations

import argparse
import importlib
import sys
import time

# Per-stage arguments of an --incremental run (see the module docstring).
INCREMENTAL_ARGS = {"creators": ["--append"], "topics": ["--label-only"], "llm_rate": ["--rekey"]}

STAGES = ["prepare", "creators", "leaning", "annotate", "embed", "topics", "llm_rate", "features", "factors", "validate",
          "formats", "landscape", "timeline", "engagement", "hits", "profiles", "year", "associations", "zipf_views", "report_data", "report"]


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--from", dest="start", choices=STAGES, default=STAGES[0])
    ap.add_argument("--skip", nargs="*", choices=STAGES, default=[])
    ap.add_argument("--incremental", action="store_true", help="channels were added: keep every sample of record (creators --append, topics --label-only, llm_rate --rekey)")
    a = ap.parse_args(argv)
    t0 = time.time()
    for stage in STAGES[STAGES.index(a.start):]:
        if stage in a.skip:
            print(f"== skipping {stage}")
            continue
        args = INCREMENTAL_ARGS.get(stage, []) if a.incremental else []
        print(f"== {stage}" + (" " + " ".join(args) if args else ""), flush=True)
        mod = importlib.import_module(f"pipeline_titles.{stage}")
        rc = mod.main(list(args))
        if rc:
            print(f"stage {stage} failed with code {rc}", file=sys.stderr)
            return rc
    print(f"pipeline done in {(time.time() - t0) / 60:.1f} min")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
