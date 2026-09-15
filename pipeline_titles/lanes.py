"""Stage 0b - write the proposed lane assignment (data/titles/analysis/lanes.csv).

Columns: creator, channel_name, platform, lane, organisation, clipper, subscribers,
n_videos, n_streams, low_n_videos, low_n_streams, note, status.

The seed lives in pipeline_titles/lane_seed.py. This script refuses to overwrite an
existing lanes.csv (which may carry hand corrections) unless --force is given;
every later stage reads lanes.csv, so correct the CSV, not the seed.

CLI:
    python -m pipeline_titles.lanes            # write if missing
    python -m pipeline_titles.lanes --force    # rebuild from the seed
"""

from __future__ import annotations

import argparse
from typing import Optional, Sequence

import pandas as pd

from pipeline_titles.common import ANALYSIS_DIR, LANES_CSV, LOW_N, load_channels, load_prepared, stage_timer
from pipeline_titles.lane_seed import LANES

VALID_LANES = {
    "left_commentary", "right_commentary", "centrist_heterodox", "us_legacy_tv", "right_tv_network",
    "wire_international", "us_press_print_digital", "independent_digital_news", "streamer_reaction",
    "interview_podcast", "legal_institutional", "humour_satire", "explainer_geopolitics",
}


def build_lanes(prepared: pd.DataFrame, channels: pd.DataFrame, seed: dict = LANES) -> pd.DataFrame:
    """One row per creator, joined with title counts and subscriber numbers."""
    counts = prepared[~prepared["is_dup"]].groupby(["creator", "genre"]).size().unstack(fill_value=0)
    ch = channels.sort_values("tab").drop_duplicates("creator").set_index("creator")
    rows = []
    for creator in sorted(set(prepared["creator"])):
        lane, org, clipper, note = seed.get(creator, ("UNASSIGNED", creator, False, "not in seed"))
        assert lane in VALID_LANES or lane == "UNASSIGNED", (creator, lane)
        nv = int(counts.loc[creator, "videos"]) if "videos" in counts.columns and creator in counts.index else 0
        ns = int(counts.loc[creator, "streams"]) if "streams" in counts.columns and creator in counts.index else 0
        rows.append({
            "creator": creator,
            "channel_name": str(ch.loc[creator, "channel_name"]).strip() if creator in ch.index else creator.rsplit("/", 1)[-1],
            "platform": prepared.loc[prepared["creator"] == creator, "platform"].iloc[0],
            "lane": lane, "organisation": org, "clipper": bool(clipper),
            "subscribers": ch.loc[creator, "channel_follower_count"] if creator in ch.index else "",
            "n_videos": nv, "n_streams": ns, "low_n_videos": nv < LOW_N, "low_n_streams": ns < LOW_N,
            "note": note, "status": "proposed",
        })
    return pd.DataFrame(rows)


def main(argv: Optional[Sequence[str]] = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--force", action="store_true", help="overwrite an existing lanes.csv")
    a = ap.parse_args(argv)
    if LANES_CSV.exists() and not a.force:
        print(f"{LANES_CSV} exists (may hold hand corrections); use --force to rebuild from the seed")
        return 0
    with stage_timer("stage0b_lanes"):
        lanes = build_lanes(load_prepared(), load_channels())
        ANALYSIS_DIR.mkdir(parents=True, exist_ok=True)
        lanes.to_csv(LANES_CSV, index=False)
        missing = lanes[lanes["lane"] == "UNASSIGNED"]
        print(lanes["lane"].value_counts().to_string())
        print(f"clippers: {int(lanes['clipper'].sum())}   organisations: {lanes['organisation'].nunique()}   unassigned: {len(missing)}")
        if len(missing):
            print(missing["creator"].tolist())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
