"""Pure-helper tests for pipeline_titles.features."""

import numpy as np

from pipeline_titles.features import formulaic_flags, heaps_zipf, mask_tokens, template_keys, title_features


def _ann(tokens, tag=None, pos=None, ent_iob=None, **kw):
    n = len(tokens)
    a = {"tokens": tokens, "tag": tag or ["NN"] * n, "pos": pos or ["NOUN"] * n, "dep": ["dep"] * n,
         "ent_iob": ent_iob or ["O"] * n, "all_caps": False, "n_person": 0, "n_org": 0, "n_gpe": 0, "n_ents": 0}
    a.update(kw)
    return a


def test_title_features_sensational_title():
    raw = "BREAKING: Trump SLAMS CNN reporter in INSANE rant!! | Fox News"
    norm = "BREAKING: Trump SLAMS CNN reporter in INSANE rant!!"
    toks = ["BREAKING", ":", "Trump", "SLAMS", "CNN", "reporter", "in", "INSANE", "rant", "!", "!"]
    ann = _ann(toks, tag=["NN", ":", "NNP", "VBZ", "NNP", "NN", "IN", "JJ", "NN", ".", "."],
               pos=["NOUN", "PUNCT", "PROPN", "VERB", "PROPN", "NOUN", "ADP", "ADJ", "NOUN", "PUNCT", "PUNCT"],
               ent_iob=["O", "O", "B-PERSON", "O", "B-ORG", "O", "O", "O", "O", "O", "O"], n_person=1, n_org=1, n_ents=2)
    f = title_features(raw, norm, "Fox News", ann)
    assert f["lead_colon_label"] == 1 and f["lead_breaking"] == 1 and f["pipe_segments_raw"] == 2
    assert f["excl"] == 1 and f["multi_punct"] == 1 and f["has_allcaps_word"] == 1
    assert f["violence_verb"] == 1 and f["shock_word"] >= 1 and f["neg_eval"] >= 1
    assert f["n_person"] == 1 and f["has_finite_verb"] == 1 and f["present_tense"] == 1
    assert f["brand_stripped"] == 1 and f["pipe"] == 0


def test_title_features_conversational_and_explainer():
    norm = "chat, here's why we can't stop watching this.."
    toks = ["chat", ",", "here", "'s", "why", "we", "ca", "n't", "stop", "watching", "this", ".."]
    f = title_features(norm, norm, "", _ann(toks))
    assert f["discourse_marker"] == 1 and f["first_pl"] == 1 and f["negation"] == 1
    assert f["contraction"] >= 2 and f["trailing_ellipsis"] == 1 and f["curiosity_lex"] == 1
    assert f["lowercase_start"] == 1 and f["why_marker"] == 0   # 'why' not first, no 'reason'
    g = title_features("How tariffs actually work, explained", "How tariffs actually work, explained", "", _ann(["How", "tariffs", "actually", "work", ",", "explained"]))
    assert g["explainer"] == 1 and g["q_word_start"] == 1 and g["intensifier"] == 1


def test_mask_and_templates_and_formulaic_flags():
    toks = ["Trump", "SLAMS", "CNN", "over", "3", "reports"]
    masked = mask_tokens(toks, ["B-PERSON", "O", "B-ORG", "O", "O", "O"])
    assert masked == ["<ENT>", "slams", "<ENT>", "over", "#", "reports"]
    assert template_keys(masked) == ("<ENT> slams <ENT>", "over # reports")
    assert template_keys(["a", "b"]) == (None, None)
    lead = ["x y z"] * 4 + ["p q r", None]
    trail = ["m n o"] * 2 + [None] * 4
    assert formulaic_flags(lead, trail, min_others=3) == [1, 1, 1, 1, 0, 0]


def test_heaps_zipf_returns_nan_when_short_and_plausible_values_otherwise():
    assert all(np.isnan(v) for v in heaps_zipf([["a", "b"]] * 3, 1000))
    rng = np.random.RandomState(0)
    vocab = [f"w{i}" for i in range(2000)]
    probs = 1 / np.arange(1, 2001); probs /= probs.sum()
    titles = [list(rng.choice(vocab, size=8, p=probs)) for _ in range(600)]
    hb, hs, zb, zs = heaps_zipf(titles, 1500, repeats=5)
    assert 0.5 < hb < 1.0 and hs < 0.1 and 0.5 < zb < 1.5
