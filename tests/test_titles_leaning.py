"""Pure-helper tests for pipeline_titles.leaning (no data, no model calls)."""

import numpy as np
import pandas as pd

from pipeline_titles.leaning import N_PER_CREATOR, draw_sample, group_month_check, parse_labels, self_declared_leaning, stability_check


def test_parse_labels_reads_plain_and_decorated_lines_and_targets():
    text = "1,left\n**2**, right\n3: neither\n4,right,democrats_left\n5,maybe\nnoise\n"
    out = parse_labels(text, 5)
    assert out == {1: "left", 2: "right", 3: "neither", 4: "right|democrats_left"}
    assert parse_labels("7,left", 5) == {}                  # out of range


def test_self_declared_leaning_counts_words_on_each_side():
    assert self_declared_leaning("A conservative commentator") == "right"
    assert self_declared_leaning("Progressive news from the populist left") == "left"
    assert self_declared_leaning("Just the news") == "none"
    assert self_declared_leaning("liberal vs conservative debates") == "none"   # one each


def _prepared(n_uploads: dict[str, int]) -> pd.DataFrame:
    rows, rid = [], 0
    for creator, n in n_uploads.items():
        for i in range(n):
            rows.append({"row_id": rid, "creator": creator, "genre": "videos", "month": f"2026-0{1 + i % 9}", "is_dup": False, "title_raw": f"t{rid}"})
            rid += 1
    return pd.DataFrame(rows)


def test_draw_sample_marks_base_rows_and_spreads_topup_across_months():
    prep = _prepared({"@big": 200, "@small": 20})
    base_only = draw_sample(prep, N_PER_CREATOR)
    assert base_only.is_base.all() and base_only.groupby("creator").size().to_dict() == {"@big": 16, "@small": 16}
    full = draw_sample(prep, 50, min_uploads=50)
    assert full.groupby("creator").size().to_dict() == {"@big": 50, "@small": 16}       # @small has < 50 uploads: base only
    big = full[full.creator == "@big"]
    assert set(big[big.is_base].row_id) == set(base_only[base_only.creator == "@big"].row_id)   # the base draw never shifts
    assert big[~big.is_base].month.value_counts().max() - big[~big.is_base].month.value_counts().min() <= 1   # round-robin over months
    assert not full.row_id.duplicated().any()


def test_stability_and_group_month_checks_on_a_synthetic_sample():
    rng = np.random.RandomState(0)
    rows = []
    for creator, p_right in (("@r1", 0.8), ("@r2", 0.6), ("@l1", 0.1), ("@l2", 0.2), ("@r3", 0.7), ("@l3", 0.15)):
        for i in range(50):
            rows.append({"row_id": len(rows), "creator": creator, "month": f"2026-0{1 + i % 9}", "is_base": i < 16,
                         "label_m": "right" if rng.rand() < p_right else ("left" if rng.rand() < 0.6 else "neither")})
    df = pd.DataFrame(rows)
    summ, ch = stability_check(df, "label_m")
    assert len(summ) == 1 and summ.n_channels.iloc[0] == 6 and summ.spearman_base_vs_topup.iloc[0] > 0.5
    assert set(ch.columns) >= {"creator", "score_base", "score_topup", "score_all", "group_base", "group_all", "change"} and len(ch) == 6
    groups = {"@r1": "right", "@r2": "right", "@r3": "right", "@l1": "left", "@l2": "left", "@l3": "left"}
    gm = group_month_check(df, "label_m", groups)
    assert set(gm.group) == {"right", "left"} and gm.n_titles.sum() == 300
    assert (gm.partisan_share >= gm.left_share).all() and gm.score.between(-1, 1).all()
