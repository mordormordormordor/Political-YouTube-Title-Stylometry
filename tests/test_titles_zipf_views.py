"""Pure-helper tests for pipeline_titles.zipf_views (no data files)."""

from collections import Counter

import numpy as np
import pandas as pd

from pipeline_titles.zipf_views import monthly_views_table, relative_log_views, size_matched_zipf, token_counter, zipf_fit_r2


def _zipf_titles(n_titles: int, seed: int = 0) -> list[str]:
    """Titles drawn from a vocabulary whose word probabilities follow 1 / rank."""
    rng = np.random.RandomState(seed)
    vocab = [f"w{i}" for i in range(1, 400)]
    p = 1 / np.arange(1, 400); p /= p.sum()
    return [" ".join(rng.choice(vocab, size=10, p=p)) for _ in range(n_titles)]


def test_token_counter_and_zipf_fit_recover_a_zipfian_vocabulary():
    ctr = token_counter(_zipf_titles(3000))
    assert isinstance(ctr, Counter) and ctr.most_common(1)[0][0] == "w1"
    assert zipf_fit_r2(ctr, 100) > 0.97                          # straight on log-log axes through the head
    assert zipf_fit_r2(Counter({"a": 1}), 100) != zipf_fit_r2(Counter({"a": 1}), 100)   # NaN when too few types


def test_size_matched_zipf_is_reproducible_and_nan_when_too_small():
    titles = _zipf_titles(2500)
    m1, s1 = size_matched_zipf(titles, n=500, repeats=5, max_rank=100)
    m2, _ = size_matched_zipf(titles, n=500, repeats=5, max_rank=100)
    assert m1 == m2 and 0.6 < m1 < 1.3 and s1 >= 0
    m, s = size_matched_zipf(titles[:100], n=500)
    assert np.isnan(m) and np.isnan(s)


def test_relative_log_views_centres_each_creator_month_on_zero():
    df = pd.DataFrame({"creator": ["a"] * 4 + ["b"] * 3, "month": ["2026-01", "2026-01", "2026-02", "2026-02", "2026-01", "2026-01", "2026-01"],
                       "view_count": [10, 1000, 5, 5, 100, 200, 400]})
    r = relative_log_views(df)
    assert np.allclose(r.groupby([df.creator, df.month]).mean(), 0)
    assert r.iloc[1] > 0 > r.iloc[0] and r.iloc[2] == 0 == r.iloc[3]


def test_monthly_views_table_reports_groups_months_and_an_all_row():
    rng = np.random.RandomState(1)
    rows = []
    for creator, style in (("a", "all_caps"), ("b", "title_case"), ("c", "all_caps")):
        for m in ("2026-01", "2026-02"):
            for i in range(25):
                rows.append({"creator": creator, "month": m, "caps_style": style if i % 2 else "title_case", "view_count": int(rng.lognormal(8, 1))})
    df = pd.DataFrame(rows); df["rel_log_views"] = relative_log_views(df)
    t = monthly_views_table(df, "caps_style", "caps_style", ["all_caps", "title_case", "sentence_case"])
    assert set(t.group) == {"all_caps", "title_case"}                  # sentence_case has no rows, and is skipped
    assert set(t.month) == {"2026-01", "2026-02", "all"}
    a = t[(t.group == "all_caps") & (t.month == "all")].iloc[0]
    assert a.n_videos == 48 and a.n_creators == 2 and a.relative_log_views_se > 0
