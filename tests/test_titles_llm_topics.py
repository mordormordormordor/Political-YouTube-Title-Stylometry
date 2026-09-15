"""Pure-helper tests for pipeline_titles.llm_rate and pipeline_titles.topics."""

import numpy as np

from pipeline_titles.llm_rate import allocate_sample, build_prompt, parse_response
from pipeline_titles.topics import cap_for_target, nearest_centroid, normalise_entity, parse_label_json


def test_allocate_sample_hits_total_and_respects_group_sizes():
    sizes = {("a", "videos"): 5000, ("b", "videos"): 300, ("c", "streams"): 20, ("d", "videos"): 6}
    alloc = allocate_sample(sizes, total=100, base_full=8, base_low=2, low_n=50)
    assert sum(alloc.values()) == 100
    assert alloc[("c", "streams")] == 2 and alloc[("d", "videos")] == 2
    assert alloc[("a", "videos")] > alloc[("b", "videos")] >= 8


def test_parse_response_accepts_valid_lines_and_coerces_scale_flags():
    text = "1,5,3,1,1,2,0,1,1,confrontation\n2,1,1,4,3,1,0,0,5,howto_explainer\n**3**,2,2,2,2,2,1,0,0,Question\nnoise\n"
    out = parse_response(text, 3)
    assert out[1]["sensational"] == 5 and out[1]["format_llm"] == "confrontation"
    assert out[2]["outrage"] == 1                  # '5' on a 0/1 flag -> 1
    assert out[3]["format_llm"] == "question" and out[3]["humor"] == 1
    assert parse_response("garbage", 2) == {}


def test_build_prompt_lists_titles_in_order():
    p = build_prompt(["First title", "Second, with comma"])
    assert "1. First title\n2. Second, with comma" in p and "id,sensational" in p


def test_cap_for_target():
    assert cap_for_target([10, 10, 10], 100) == 10
    assert cap_for_target([100, 100, 5], 105) == 50
    assert cap_for_target([1000, 20], 60) == 40


def test_nearest_centroid():
    c = np.array([[1.0, 0.0], [0.0, 1.0]], dtype=np.float32)
    e = np.array([[0.9, 0.1], [0.2, 0.8], [-1, 0]], dtype=np.float32)
    e /= np.linalg.norm(e, axis=1, keepdims=True)
    best, sim = nearest_centroid(e, c, chunk=2)
    assert best.tolist() == [0, 1, 1] and sim[0] > 0.9


def test_normalise_entity_and_label_json():
    assert normalise_entity("President Trump's") == "Trump"
    assert normalise_entity("the FBI") == "FBI"
    assert parse_label_json('junk {"label": "Iran war", "political": "true", "category": "War / Conflict"} end') == \
        {"label": "Iran war", "political": True, "category": "other"}
    assert parse_label_json('{"label": "NFL season", "political": false, "category": "sport"}')["category"] == "sport"
    assert parse_label_json("no json") is None
