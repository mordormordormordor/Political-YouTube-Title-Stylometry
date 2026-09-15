"""Pure-helper tests for pipeline_titles.textstats."""

from collections import Counter

import numpy as np

from pipeline_titles.textstats import caps_style, rank_turbulence_divergence, vocab_tokens, weighted_log_odds


def test_vocab_tokens_strips_possessives_and_stopwords():
    assert vocab_tokens("Trump’s LIVE reaction to the Fed's rates!") == ["trump", "reaction", "fed", "rates"]


def test_caps_style_rules():
    acr = {"fbi", "ice", "gop"}
    assert caps_style("THIS IS INSANE", acr) == "all_caps"
    assert caps_style("Trump SLAMS Judge in Ballroom Appeal", acr) == "selective_caps"
    assert caps_style("FBI raids ICE office in Chicago", acr) == "sentence_case"          # acronyms exempt
    assert caps_style("BREAKING: Trump signs the order", acr) == "sentence_case"           # generic label exempt
    assert caps_style("The Truth About Tariffs And Trade", acr) == "title_case"
    assert caps_style("Why the Fed can't cut rates", acr) == "sentence_case"
    assert caps_style("chat, we are so back", acr) == "mixed_other"
    assert caps_style("It's over.", acr) == "short_other"


def test_weighted_log_odds_direction_and_shrinkage():
    a = Counter({"insane": 30, "trump": 50, "policy": 2})
    b = Counter({"insane": 2, "trump": 50, "policy": 30})
    out = weighted_log_odds(a, b, alpha0=50.0)
    assert out["insane"][0] > 0 and out["policy"][0] < 0 and abs(out["trump"][0]) < 0.2
    assert out["insane"][1] > out["trump"][1]


def test_rank_turbulence_divergence_symmetry_and_contributions():
    a = Counter({"x": 10, "y": 5, "z": 1}); b = Counter({"x": 10, "y": 5, "z": 1})
    d, contribs = rank_turbulence_divergence(a, b)
    assert d == 0.0
    a = Counter({"x": 10, "y": 5}); b = Counter({"y": 10, "q": 5})
    d, contribs = rank_turbulence_divergence(a, b, alpha=1 / 3)
    assert d > 0 and abs(sum(abs(c) for _, c, _, _ in contribs) - 1.0) < 1e-9
    top = contribs[0]
    assert top[0] in ("x", "q")
    assert next(c for w, c, _, _ in contribs if w == "x") > 0 and next(c for w, c, _, _ in contribs if w == "q") < 0
