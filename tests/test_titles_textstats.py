"""Pure-helper tests for pipeline_titles.textstats."""

from collections import Counter

import numpy as np

from pipeline_titles.textstats import caps_style, rank_turbulence_divergence, tied_ranks, vocab_tokens, weighted_log_odds


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
    assert caps_style("iPhone Duo: Apple's First Foldable Costs More", acr) == "mixed_other"  # a lower-case first letter, whatever follows
    assert caps_style("8 dead after Air Force bomber crashes", acr) == "sentence_case"      # a number opens it: judged on what follows
    assert caps_style("U.S. strikes targets on Kharg Island", acr) == "sentence_case"      # "U.S." is skipped by the word pattern, not a lower-case start
    assert caps_style("'I was away': Trump justifies voting by mail", acr) == "sentence_case"
    assert caps_style("It's over.", acr) == "short_other"


def test_weighted_log_odds_direction_and_shrinkage():
    a = Counter({"insane": 30, "trump": 50, "policy": 2})
    b = Counter({"insane": 2, "trump": 50, "policy": 30})
    out = weighted_log_odds(a, b, alpha0=50.0)
    assert out["insane"][0] > 0 and out["policy"][0] < 0 and abs(out["trump"][0]) < 0.2
    assert out["insane"][1] > out["trump"][1]


def test_rank_turbulence_divergence_follows_the_allotaxonometer_conventions():
    a = Counter({"x": 10, "y": 5, "z": 1}); b = Counter({"x": 10, "y": 5, "z": 1})
    d, contribs = rank_turbulence_divergence(a, b)
    assert d == 0.0
    a = Counter({"x": 10, "y": 5}); b = Counter({"q": 10, "p": 5})          # disjoint systems: D is normalized to about 1
    d, _ = rank_turbulence_divergence(a, b, alpha=1 / 3)
    assert d > 0.9
    a = Counter({"x": 10, "y": 5}); b = Counter({"y": 10, "q": 5})
    d, contribs = rank_turbulence_divergence(a, b, alpha=1 / 3)
    d2, _ = rank_turbulence_divergence(b, a, alpha=1 / 3)
    assert 0 < d < 1 and abs(d - d2) < 1e-12                                 # symmetric
    assert abs(sum(abs(c) for _, c, _, _ in contribs) - d) < 1e-12          # contributions sum to D
    by = {w: (c, ra, rb) for w, c, ra, rb in contribs}
    assert by["x"][0] > 0 and by["q"][0] < 0                                 # positive = more prominent in A
    assert by["x"][2] == 3.0 and by["q"][1] == 3.0                           # an absent type takes the tied last rank of the union
    assert tied_ranks({"a": 5, "b": 5, "c": 1}, ["a", "b", "c", "d"]) == {"a": 1.5, "b": 1.5, "c": 3.0, "d": 4.0}
