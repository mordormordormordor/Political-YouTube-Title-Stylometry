"""Pure-helper tests for pipeline_titles.leaning (no data, no model calls)."""

import numpy as np
import pandas as pd

import json

from pipeline_titles import leaning
from pipeline_titles.leaning import N_BASE, draw_sample, group_month_check, parse_labels, repeat_check, runs_table, stability_check, two_readings


def test_parse_labels_reads_plain_and_decorated_lines_and_targets():
    text = "1,left\n**2**, right\n3: neither\n4,right,democrats_left\n5,maybe\nnoise\n"
    out = parse_labels(text, 5)
    assert out == {1: "left", 2: "right", 3: "neither", 4: "right|democrats_left"}
    assert parse_labels("7,left", 5) == {}                  # out of range


def _prepared(n_uploads: dict[str, int]) -> pd.DataFrame:
    rows, rid = [], 0
    for creator, n in n_uploads.items():
        for i in range(n):
            rows.append({"row_id": rid, "creator": creator, "genre": "videos", "month": f"2026-0{1 + i % 9}", "is_dup": False, "title_raw": f"t{rid}"})
            rid += 1
    return pd.DataFrame(rows)


def test_draw_sample_marks_base_rows_and_spreads_topup_across_months():
    prep = _prepared({"@big": 200, "@small": 20})
    base_only = draw_sample(prep, N_BASE)
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


def test_two_readings_compares_the_first_reading_with_the_labels_of_record():
    rows, first = [], []
    for creator, labels in (("@r", ["right"] * 14 + ["neither"] * 6), ("@l", ["left"] * 12 + ["neither"] * 8), ("@n", ["neither"] * 20)):
        for i, lab in enumerate(labels):
            rid = len(rows)
            rows.append({"row_id": rid, "creator": creator, "title_raw": f"t{rid}", "label_m": lab})
            first.append({"row_id": rid, "run": 1 if i < 16 else 2, "label_m": lab})
    df, fr = pd.DataFrame(rows), pd.DataFrame(first)
    fr.loc[0, "label_m"] = "neither"          # @r: one right title read as neither the first time (neither -> partisan in the second reading)
    fr.loc[20, "label_m"] = "right"           # @l: one left title read as right the first time (a side flip)
    fr.loc[59, "label_m"] = "left"            # @n: one neither title read as left the first time
    summ, ch, changed = two_readings(df, fr, "label_m", min_titles=16)
    assert summ["n_titles"] == 60 and summ["exact_agreement"] == round(57 / 60, 4) and 0 < summ["kappa"] < 1
    assert summ["side_flipped"] == 1 and summ["neither_to_partisan"] == 1 and summ["partisan_to_neither"] == 1
    assert summ["confusion_first_then_shuffled"]["right"]["left"] == 1 and summ["confusion_first_then_shuffled"]["neither"]["neither"] == 33
    assert summ["by_run"][1] == {"n_titles": 48, "exact_agreement": round(46 / 48, 4), "kappa": summ["by_run"][1]["kappa"]} and summ["by_run"][2]["exact_agreement"] == round(11 / 12, 4)
    assert summ["n_channels"] == 3 and summ["channel_group_changed"] == 0 and summ["channel_sign_flipped"] == 0
    assert len(changed) == 3 and set(changed.columns) == {"row_id", "creator", "run", "title_raw", "label_first", "label_shuffled"}
    assert ch.loc[ch.creator == "@r", "score_first"].iloc[0] == 0.65 and ch.loc[ch.creator == "@r", "score_shuffled"].iloc[0] == 0.7


def test_runs_table_numbers_the_runs_and_counts_the_titles_each_sent(tmp_path, monkeypatch):
    log = tmp_path / "runtimes.jsonl"
    recs = [{"stage": "stage7_leaning", "started": "2026-09-15T23:53:57+00:00", "finished": "2026-09-16T02:09:17+00:00", "seconds": 8120.7, "calls": 624, "batch_order": "shuffled", "reported_cost_usd": 56.5},
            {"stage": "stage7_leaning", "started": "2026-09-15T14:13:56+00:00", "finished": "2026-09-15T15:05:29+00:00", "seconds": 3093.1, "calls": 218, "batch_order": "sample order", "reported_cost_usd": 18.9},
            {"stage": "stage7_leaning", "started": "2026-09-16T12:11:30+00:00", "finished": "2026-09-16T12:11:35+00:00", "seconds": 5.7},          # analyze-only: no calls
            {"stage": "report", "started": "2026-09-15T15:09:23+00:00", "finished": "2026-09-15T15:10:00+00:00", "seconds": 37.0},
            {"stage": "stage7_leaning", "started": "2026-09-15T16:32:42+00:00", "finished": "2026-09-15T17:54:05+00:00", "seconds": 4883.0, "calls": 407, "batch_order": "sample order", "reported_cost_usd": 36.4}]
    log.write_text("\n".join(json.dumps(r) for r in recs) + "\n")
    monkeypatch.setattr(leaning, "RUNTIMES", log)
    df = pd.DataFrame({"row_id": range(60)})
    first = pd.DataFrame({"row_id": range(60), "run": [1] * 48 + [2] * 12})
    runs = runs_table(df, first)
    assert [(r["run"], r["what"], r["titles"], r["calls"], r["labels"]) for r in runs] == [
        (1, "the base draw", 48, 218, "first reading"), (2, "the top-up", 12, 407, "first reading"), (3, "every title again", 60, 624, "of record")]
    assert runs[0]["minutes"] == 51.6 and runs[2]["reported_cost_usd"] == 56.5
    assert [r["titles"] for r in runs_table(df, None)] == [None, None, 60]


def test_repeat_check_gives_all_three_pairs_and_the_three_way_agreement():
    rows, first, rep = [], [], []
    for creator, labels in (("@r", ["right"] * 14 + ["neither"] * 6), ("@l", ["left"] * 12 + ["neither"] * 8), ("@n", ["neither"] * 20)):
        for i, lab in enumerate(labels):
            rid = len(rows)
            rows.append({"row_id": rid, "creator": creator, "title_raw": f"t{rid}", "label_m": lab})
            first.append({"row_id": rid, "run": 1 if i < 16 else 2, "label_m": lab})
            rep.append({"row_id": rid, "label_m": lab})
    df, fr, rp = pd.DataFrame(rows), pd.DataFrame(first), pd.DataFrame(rep)
    fr.loc[0, "label_m"] = "neither"; fr.loc[20, "label_m"] = "right"      # the first reading differs on two titles
    rp.loc[0, "label_m"] = "neither"; rp.loc[41, "label_m"] = "left"       # the repeat differs on two: one shared with the first reading, one of its own
    summ, ch, changed = repeat_check(df, fr, rp, "label_m", min_titles=16)
    rr = summ["record_vs_repeat"]
    assert rr["n_titles"] == 60 and rr["exact_agreement"] == round(58 / 60, 4) and rr["partisan_to_neither"] == 1 and rr["neither_to_partisan"] == 1
    assert "confusion_record_then_repeat" in rr and rr["confusion_record_then_repeat"]["right"]["neither"] == 1
    assert rr["n_channels"] == 3 and rr["channel_group_changed"] == 0 and len(changed) == 2 and set(changed.columns) == {"row_id", "creator", "title_raw", "label_record", "label_repeat"}
    assert set(ch.columns) >= {"creator", "score_record", "score_repeat", "change", "group_record", "group_repeat"}
    assert summ["first_vs_record"]["exact_agreement"] == round(58 / 60, 4) and summ["first_vs_repeat"]["exact_agreement"] == round(58 / 60, 4)   # title 0 agrees between first and repeat; 20 and 41 differ
    t = summ["three_readings"]
    assert t["n_titles"] == 60 and t["all_three_agree"] == round(57 / 60, 4) and t["record_and_repeat_agree"] == round(58 / 60, 4) and t["no_majority"] == 0
    # without a first reading only the pair of record and repeat is given
    assert set(repeat_check(df, None, rp, "label_m", min_titles=16)[0]) == {"judge", "reading_of_record", "repeat", "record_vs_repeat"}


def test_draw_new_creators_is_fixed_by_the_creator_alone_and_leaves_the_record_untouched():
    from pipeline_titles.leaning import draw_new_creators
    prep = _prepared({"@a": 120, "@m": 120, "@z": 120})
    record = draw_sample(prep, 50)
    with_insert = draw_sample(_prepared({"@a": 120, "@m": 120, "@s": 120, "@z": 120}), 50)
    shifted = set(record[record.creator == "@z"].row_id) != set(with_insert[with_insert.creator == "@z"].row_id)
    assert shifted                                        # the shared stream: an inserted creator moves the later ones' draws
    prep2 = pd.concat([prep, _prepared({"@s": 120}).assign(row_id=lambda d: d.row_id + 1000)], ignore_index=True)
    alone = draw_new_creators(prep2, ["@s"], 50)
    assert alone.creator.eq("@s").all() and len(alone) == 50 and alone.is_base.sum() == N_BASE
    prep3 = pd.concat([prep2, _prepared({"@b": 80}).assign(row_id=lambda d: d.row_id + 2000)], ignore_index=True)
    both = draw_new_creators(prep3, ["@b", "@s"], 50)
    assert set(both[both.creator == "@s"].row_id) == set(alone.row_id)   # @s's draw does not depend on @b
    assert set(draw_new_creators(prep3, ["@s"], 50).row_id) == set(alone.row_id)
    assert draw_new_creators(prep3, [], 50).empty


def test_readings_are_matched_by_title_when_both_files_carry_it():
    rows, first = [], []
    for creator, labels in (("@r", ["right"] * 16 + ["neither"] * 4), ("@l", ["left"] * 16 + ["neither"] * 4)):
        for i, lab in enumerate(labels):
            rid = len(rows)
            rows.append({"row_id": rid, "creator": creator, "genre": "videos", "title_raw": f"t{rid}", "label_m": lab})
            first.append({"row_id": rid, "creator": creator, "genre": "videos", "title_raw": f"t{rid}", "run": 1, "label_m": lab})
    df, fr = pd.DataFrame(rows), pd.DataFrame(first)
    # a channel added later: its row_ids collide with the record's stale ones, and the first reading never saw it
    new = pd.DataFrame({"row_id": range(20), "creator": "@new", "genre": "videos", "title_raw": [f"n{i}" for i in range(20)], "label_m": ["right"] * 20})
    summ, ch, changed = two_readings(pd.concat([df, new], ignore_index=True), fr, "label_m", min_titles=16)
    assert summ["n_titles"] == 40 and summ["exact_agreement"] == 1.0 and set(ch.creator) == {"@r", "@l"} and changed.empty
    # the record's row_ids can move (a re-prepare) without breaking the match
    fr2 = fr.assign(row_id=fr.row_id + 5000)
    assert two_readings(df, fr2, "label_m", min_titles=16)[0]["n_titles"] == 40
    rep = fr2.drop(columns="run")
    assert repeat_check(df, fr2, rep, "label_m", min_titles=16)[0]["three_readings"]["n_titles"] == 40
