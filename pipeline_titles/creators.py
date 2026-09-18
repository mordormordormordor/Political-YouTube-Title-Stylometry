"""Stage 0b - write the creator table (data/titles/analysis/creators.csv).

Columns: creator, channel_name, platform, organisation, clipper, subscribers,
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
"""

from __future__ import annotations

import argparse
from typing import Optional, Sequence

import pandas as pd

from pipeline_titles.common import ANALYSIS_DIR, CREATORS_CSV, LOW_N, load_channels, load_prepared, stage_timer
from pipeline_titles.creator_seed import CREATORS


def build_creators(prepared: pd.DataFrame, channels: pd.DataFrame, seed: dict = CREATORS) -> pd.DataFrame:
    """One row per creator, joined with title counts and subscriber numbers."""
    counts = prepared[~prepared["is_dup"]].groupby(["creator", "genre"]).size().unstack(fill_value=0)
    ch = channels.sort_values("tab").drop_duplicates("creator").set_index("creator")
    rows = []
    for creator in sorted(set(prepared["creator"])):
        org, clipper, note = seed.get(creator, (creator, False, "not in seed"))
        nv = int(counts.loc[creator, "videos"]) if "videos" in counts.columns and creator in counts.index else 0
        ns = int(counts.loc[creator, "streams"]) if "streams" in counts.columns and creator in counts.index else 0
        rows.append({
            "creator": creator,
            "channel_name": str(ch.loc[creator, "channel_name"]).strip() if creator in ch.index else creator.rsplit("/", 1)[-1],
            "platform": prepared.loc[prepared["creator"] == creator, "platform"].iloc[0],
            "organisation": org, "clipper": bool(clipper),
            "subscribers": ch.loc[creator, "channel_follower_count"] if creator in ch.index else "",
            "n_videos": nv, "n_streams": ns, "low_n_videos": nv < LOW_N, "low_n_streams": ns < LOW_N,
            "note": note,
        })
    return pd.DataFrame(rows)


def main(argv: Optional[Sequence[str]] = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--force", action="store_true", help="overwrite an existing creators.csv")
    a = ap.parse_args(argv)
    if CREATORS_CSV.exists() and not a.force:
        print(f"{CREATORS_CSV} exists (may hold hand corrections); use --force to rebuild from the seed")
        return 0
    with stage_timer("stage0b_creators"):
        cr = build_creators(load_prepared(), load_channels())
        ANALYSIS_DIR.mkdir(parents=True, exist_ok=True)
        cr.to_csv(CREATORS_CSV, index=False)
        missing = cr[cr["note"] == "not in seed"]
        print(f"creators: {len(cr)}   clippers: {int(cr['clipper'].sum())}   organisations: {cr['organisation'].nunique()}   not in seed: {len(missing)}")
        if len(missing):
            print(missing["creator"].tolist())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
