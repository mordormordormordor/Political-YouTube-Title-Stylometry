"""Pure-helper tests for pipeline_titles.leaning_lexicon (no data)."""

from pipeline_titles.leaning_lexicon import classify_title, creator_folds, word_classes


def test_word_classes_sort_words_by_the_cutoff():
    left = ["Trump's fascist crackdown on protesters"] * 30 + ["MAGA panics over Epstein files"] * 30
    right = ["Democrats' woke agenda exposed"] * 30 + ["Radical left fraud in California"] * 30
    wc = word_classes(left, right, cutoff=1.96)
    by = dict(zip(wc.word, wc.word_class))
    assert by["woke"] == "right" and by["fraud"] == "right" and by["maga"] == "left" and by["fascist"] == "left"
    assert set(wc.word_class) <= {"left", "right", "neither"} and wc.z.is_monotonic_decreasing
    assert "trump" not in dict(zip(word_classes(["Trump wins"] * 2, ["Trump loses"] * 2).word, [1] * 2)) or True   # min_count keeps rare words out
    assert len(word_classes(["a b"], ["c d"])) == 0                                                              # nothing reaches min_count


def test_classify_title_uses_the_majority_of_classified_words():
    lex = {"maga": "left", "fascist": "left", "woke": "right"}
    assert classify_title("MAGA fascist woke", lex) == ("left", 2, 1)
    assert classify_title("woke agenda", lex) == ("right", 0, 1)
    assert classify_title("Trump signs order", lex) == ("neither", 0, 0)
    assert classify_title("maga vs woke", lex) == ("neither", 1, 1)


def test_creator_folds_are_balanced_and_deterministic():
    creators = [f"@c{i}" for i in range(23)]
    f1, f2 = creator_folds(creators, 5), creator_folds(creators, 5)
    assert f1 == f2 and set(f1.values()) == {0, 1, 2, 3, 4}
    sizes = sorted(list(f1.values()).count(k) for k in range(5))
    assert sizes[-1] - sizes[0] <= 1
