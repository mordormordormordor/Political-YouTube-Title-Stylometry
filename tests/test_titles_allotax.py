"""Pure-helper tests for pipeline_titles.allotax (no Node, no data)."""

from pipeline_titles.allotax import alpha_label, system_records


def test_system_records_are_allotaxonometer_input_sorted_by_count():
    recs, total = system_records(["Trump SLAMS the radical left", "Trump signs order", "The left panics"])
    assert total == sum(r["counts"] for r in recs)
    assert recs[0]["types"] == "trump" and recs[0]["counts"] == 2 and recs[1]["types"] == "left"
    assert all(set(r) == {"types", "counts", "totalunique", "probs"} for r in recs)
    assert all(r["totalunique"] == len(recs) for r in recs) and abs(sum(r["probs"] for r in recs) - 1) < 1e-4
    assert system_records([]) == ([], 0)


def test_alpha_label_prefers_fractions():
    assert alpha_label(1 / 3) == "1/3" and alpha_label(0.5) == "1/2" and alpha_label(1.0) == "1" and alpha_label(0.58) == "0.58"
