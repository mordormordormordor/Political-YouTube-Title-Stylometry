"""Pure-helper tests for the Title Stylometry Stage 0 modules (no data files, no network)."""

import numpy as np
import pandas as pd

from pipeline_titles.annotate import build_case_lexicon, is_all_caps, truecase
from pipeline_titles.common import balanced_mask, creator_slug, gini, month_of, title_key, top_share
from pipeline_titles.prepare import (
    BrandPatterns, detect_brand_patterns, segment_key, segments_with_seps, strip_title, zipf_slope,
)


def test_creator_slug_and_month():
    assert creator_slug("@HasanAbi") == "HasanAbi"
    assert creator_slug("https://rumble.com/c/GGreenwald") == "rumble_GGreenwald"
    assert creator_slug("@X22Report-y5y") == "X22Report-y5y"
    assert month_of("2026-03-17") == "2026-03"


def test_title_key_is_case_and_punctuation_insensitive():
    assert title_key("This Is Insane") == title_key("THIS IS INSANE!!") == "this is insane"


def test_gini_and_top_share():
    assert gini([1, 1, 1, 1]) == 0.0
    assert abs(gini([0, 0, 0, 10]) - 0.75) < 1e-9
    assert np.isnan(gini([]))
    assert top_share([10, 1, 1, 1, 1, 1, 1, 1, 1, 1], 0.10) == 10 / 19


def test_balanced_mask_caps_each_group_and_is_seeded():
    df = pd.DataFrame({"creator": ["a"] * 10 + ["b"] * 3, "genre": "videos", "x": range(13)})
    m1 = balanced_mask(df, cap=4, seed=1)
    m2 = balanced_mask(df, cap=4, seed=1)
    assert m1.equals(m2)
    assert m1[df["creator"] == "a"].sum() == 4 and m1[df["creator"] == "b"].sum() == 3
    elig = df["x"] != 0
    assert not balanced_mask(df, cap=4, seed=1, eligible=elig)[0]


def test_segment_key_collapses_digits_and_case():
    assert segment_key("Ep. 1837") == "ep. #"
    assert segment_key("The Ben Shapiro Show ") == "the ben shapiro show"


def test_segments_with_seps_keeps_original_separators():
    segs = segments_with_seps("A - B | C")
    assert [s for s, _ in segs] == ["A", "B", "C"]
    assert segs[1][1] == " - " and segs[2][1] == " | "


def test_detect_brand_patterns_uses_20_percent_rule_and_keeps_generic_labels():
    titles = [f"Story number {i} | My Show" for i in range(30)] + [f"LIVE: Event {i}" for i in range(30)] + \
             [f"Plain title {i}" for i in range(40)]
    bp = detect_brand_patterns(titles, min_share=0.2, min_count=10)
    assert "my show" in bp.suffix                       # 30 % of titles
    assert "live" not in bp.colon                       # generic label exempt
    assert "story number #" in bp.prefix                # a digit-varying template at 30 % is a brand too
    bp2 = detect_brand_patterns([f"My Show | Story {i}" for i in range(30)] + [f"Plain {i}" for i in range(70)])
    assert "my show" in bp2.prefix


def test_strip_title_removes_brand_dates_episodes_and_hashtags():
    bp = BrandPatterns(suffix={"my show": (30, "My Show")}, prefix={"debating maga": (10, "Debating MAGA")})
    norm, removed, fb = strip_title("Trump did it again (Ep. 2593) | My Show #shorts", bp)
    assert norm == "Trump did it again" and not fb
    assert set(removed) == {"My Show", "#shorts", "Ep. 2593"}
    norm, removed, fb = strip_title("Debating MAGA. Ep. 533 - The border", bp)
    assert norm == "The border"
    norm, removed, fb = strip_title("Bloomberg Surveillance 9/14/2026", BrandPatterns())
    assert norm == "Bloomberg Surveillance" and "9/14/2026" in removed
    # a hashtag-looking rank is content, not a tag
    norm, _, _ = strip_title("Who Took His Place At #6", BrandPatterns())
    assert norm == "Who Took His Place At #6"
    # January 6 is content: not delimited, so it stays
    norm, _, _ = strip_title("January 6 hearings resume", BrandPatterns())
    assert norm == "January 6 hearings resume"
    # separators are preserved
    norm, _, _ = strip_title("NOT GUILTY - Closing argument - #defense #trial", BrandPatterns())
    assert norm == "NOT GUILTY - Closing argument"


def test_strip_title_falls_back_when_only_brand_remains():
    bp = BrandPatterns(prefix={"top u.s. & world headlines": (100, "Top U.S. & World Headlines")})
    norm, removed, fb = strip_title("Top U.S. & World Headlines — September 14, 2026", bp)
    assert norm == "Top U.S. & World Headlines" and "September 14, 2026" in removed
    norm, removed, fb = strip_title("Top U.S. & World Headlines", bp)
    assert norm == "Top U.S. & World Headlines" and fb          # exactly the show name: brand-only
    norm, removed, fb = strip_title("Top U.S. & World Headlines | Top U.S. & World Headlines", bp)
    assert norm == "Top U.S. & World Headlines | Top U.S. & World Headlines" and fb
    bp3 = BrandPatterns(prefix={"live: abc news live": (10, "")}, suffix={"abc news": (10, "")})
    norm, removed, fb = strip_title("LIVE: ABC News Live - Sunday, September 13 | ABC News", bp3)
    assert norm == "LIVE: ABC News Live | ABC News" and fb and "Sunday, September 13" in removed
    # generic labels are exempt at detection time; a cut-off trailing date is still a date
    bp4 = detect_brand_patterns([f"LIVE REPLAY: Event {i} - 9/{i % 28 + 1}/2026" for i in range(40)])
    assert "live replay" not in bp4.colon
    norm, _, _ = strip_title("LIVE REPLAY: Trump speaks - 12/19/2", bp4)
    assert norm == "LIVE REPLAY: Trump speaks"


def test_zipf_slope_on_power_law():
    from collections import Counter
    ctr = Counter({f"w{r}": int(1000 / r) for r in range(1, 200)})
    expo, used = zipf_slope(ctr, 100)
    assert used == 100 and abs(expo - 1.0) < 0.05


def test_truecase_uses_learned_lexicon():
    mixed = ["Trump slams CNN over report", "Why Trump attacked CNN again", "CNN and Trump clash", "The FBI raid on Trump"]
    proper, acronyms = build_case_lexicon(mixed, min_count=2)
    assert "trump" in proper and "cnn" in acronyms
    assert is_all_caps("TRUMP DESTROYS CNN") and not is_all_caps("Trump destroys CNN")
    assert truecase("TRUMP DESTROYS CNN", proper, acronyms) == "Trump destroys CNN"
    assert truecase("Already mixed", proper, acronyms) == "Already mixed"
