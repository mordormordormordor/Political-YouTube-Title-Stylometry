"""Pure-helper tests for pipeline_titles.textstats."""

from collections import Counter

import numpy as np

from pipeline_titles.textstats import caps_style, shouted_words, rank_turbulence_divergence, tied_ranks, vocab_tokens, weighted_log_odds


def test_vocab_tokens_strips_possessives_and_stopwords():
    assert vocab_tokens("Trump’s LIVE reaction to the Fed's rates!") == ["trump", "reaction", "fed", "rates"]


def test_caps_style_rules():
    acr = {"fbi", "ice", "gop"}
    assert caps_style("THIS IS INSANE", acr) == "all_caps"
    assert caps_style("Trump SLAMS Judge in Ballroom Appeal", acr) == "selective_caps"
    assert caps_style("FBI raids ICE office in Chicago", acr) == "sentence_case"          # acronyms exempt
    assert caps_style("Gazans wary as US names board | REUTERS", acr) == "selective_caps"
    assert caps_style("Gazans wary as US names board | REUTERS", acr, {"reuters"}) == "sentence_case"   # the channel's own tag exempt
    assert caps_style("Trump SLAMS judge | REUTERS", acr, {"reuters"}) == "selective_caps"
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


def test_tag_words_finds_a_repeated_edge_segment_at_the_low_threshold():
    from pipeline_titles.profiles import tag_words
    letters = "abcdefghijklmnopqrstuvwxy"
    titles = [f"{letters[i]} story about {letters[i] * 3} | REUTERS" for i in range(25)] + [f"{letters[i % 25]} other {letters[(i * 7) % 25] * 2} story {i}" for i in range(300)]
    rows = tag_words(titles)
    assert [(r["word"], r["kind"]) for r in rows] == [("reuters", "suffix")]
    assert rows[0]["count"] == 25
    assert tag_words(titles[:10] + titles[25:]) == []      # ten uses is under the count floor


def test_shouted_words_follow_the_caps_rule_and_fold_possessives():
    acr = {"fbi", "ice"}
    assert shouted_words("Trump SLAMS Judge in Ballroom Appeal", acr) == ({"slams"}, {"trump", "slams", "judge", "in", "ballroom", "appeal"})
    assert shouted_words("FBI raids ICE office | REUTERS", acr, {"reuters"})[0] == set()
    assert shouted_words("TRUMP'S plan EXPOSED: the end", acr)[0] == {"trump", "exposed"}
    assert shouted_words("THIS IS INSANE", acr) == (set(), set())
    assert shouted_words("Ep. 41", acr) == (set(), set())


def test_week_of_is_the_monday():
    from pipeline_titles.year import week_of
    assert week_of("2026-01-01") == "2025-12-29"
    assert week_of("2026-09-14") == "2026-09-14"
    assert week_of("2026-03-08") == "2026-03-02"


def test_collocations_bind_names_and_replace_their_words_in_the_titles_that_carry_them():
    from pipeline_titles.year import content_tokens, find_collocations, terms_of
    letters = "abcdefghijklmnopqrstuvwxy"
    # the filler titles repeat no pair: each word beside "trump" is its own
    titles = [f"Lindsey Graham on the war, take {i}" for i in range(60)] + [f"Graham cracker recipe {i}" for i in range(10)] + [f"Donald Trump again {i}" for i in range(200)] + [f"Trump {letters[i % 25]}{letters[(i * 7) % 25]}{letters[(i * 11) % 25]}x {i}" for i in range(400)]
    creators = [f"@c{i % 12}" for i in range(len(titles))]
    tokens = [content_tokens(t) for t in titles]
    found = find_collocations(tokens, creators, min_titles=50, min_channels=10)
    assert found["pair"].tolist() == ["lindsey graham"]          # "donald trump" is not bound: trump is mostly on its own
    assert terms_of(tokens[0], {"lindsey graham"}) == {"lindsey graham", "war"}   # "take" is a stopword
    assert "graham" in terms_of(tokens[60], {"lindsey graham"})   # alone, the word counts on its own
    assert content_tokens("Trump's letter to Greenland")[0] == ("trump", True)
    assert content_tokens("the end")[0] == ("the", False)


def test_pick_examples_prefers_a_title_that_also_carries_a_companion():
    import pandas as pd
    from pipeline_titles.year import pick_examples
    uniq = pd.DataFrame({"row_id": [0, 1, 2], "week": ["w"] * 3, "creator": ["@a", "@b", "@c"], "title_raw": ["Trump talks golf", "Trump and the ceasefire", "Trump again"],
                         "video_id": ["v0", "v1", "v2"], "url": [None] * 3, "view_count": [900.0, 500.0, 100.0]})
    hits = pd.DataFrame({"row_id": [0, 1, 2, 1], "word": ["trump", "trump", "trump", "ceasefire"]})
    terms = {0: {"trump", "golf"}, 1: {"trump", "ceasefire"}, 2: {"trump"}}
    got = pick_examples(uniq, hits, "week", [("w", "trump")], {("w", "trump"): ["ceasefire", "golf"]}, terms)
    assert got.iloc[0]["example_title"] == "Trump and the ceasefire" and got.iloc[0]["example_with"] == "ceasefire"   # a tie in co-occurrence goes to the stronger companion
    assert got.iloc[0]["plain_title"] == "Trump talks golf"   # the plain most-viewed title comes too
    terms2 = {0: {"trump", "golf"}, 1: {"trump", "ceasefire"}, 2: {"trump", "golf"}}
    got = pick_examples(uniq, hits, "week", [("w", "trump")], {("w", "trump"): ["ceasefire", "golf"]}, terms2)
    assert got.iloc[0]["example_with"] == "golf" and got.iloc[0]["example_title"] == "Trump talks golf"   # golf travels with trump in more titles
    got = pick_examples(uniq, hits, "week", [("w", "trump")], {("w", "trump"): ["iran"]}, terms)
    assert got.iloc[0]["example_title"] == "Trump talks golf" and got.iloc[0]["example_with"] == ""
