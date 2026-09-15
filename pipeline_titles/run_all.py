"""Run the whole Title Stylometry pipeline in order (each stage is re-runnable on
its own; every stage reads the previous stage's files from disk).

    python -m pipeline_titles.run_all                 # everything
    python -m pipeline_titles.run_all --from factors  # resume from a stage
    python -m pipeline_titles.run_all --skip llm_rate embed   # skip cached long stages

Stages, in order: prepare, lanes, annotate, embed, topics, llm_rate, features,
factors, validate, formats, landscape, timeline, engagement, hits, profiles,
leaning, report_data, report.
The LLM stages (llm_rate, topics' labelling) are fully cached, so a re-run with
an unchanged corpus makes no model calls.
"""

from __future__ import annotations

import argparse
import importlib
import sys
import time

STAGES = ["prepare", "lanes", "annotate", "embed", "topics", "llm_rate", "features", "factors", "validate",
          "formats", "landscape", "timeline", "engagement", "hits", "profiles", "leaning", "report_data", "report"]


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--from", dest="start", choices=STAGES, default=STAGES[0])
    ap.add_argument("--skip", nargs="*", choices=STAGES, default=[])
    a = ap.parse_args(argv)
    t0 = time.time()
    for stage in STAGES[STAGES.index(a.start):]:
        if stage in a.skip:
            print(f"== skipping {stage}")
            continue
        print(f"== {stage}", flush=True)
        mod = importlib.import_module(f"pipeline_titles.{stage}")
        rc = mod.main([])
        if rc:
            print(f"stage {stage} failed with code {rc}", file=sys.stderr)
            return rc
    print(f"pipeline done in {(time.time() - t0) / 60:.1f} min")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
