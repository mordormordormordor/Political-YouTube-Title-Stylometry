"""Pure-helper tests for pipeline_titles.formats and pipeline_titles.landscape."""

import numpy as np

from pipeline_titles.formats import cohen_kappa, rule_formats
from pipeline_titles.landscape import js_distance_matrix, surname_key
from pipeline_titles.factors import auto_name, orient, parallel_analysis, select_features
import pandas as pd


def test_rule_formats_examples():
    f = rule_formats("BREAKING: Trump vs Newsom debate goes off the rails")
    assert f["breaking_live"] == 1 and f["confrontation"] == 1 and f["question"] == 0
    assert rule_formats("Why the Fed can't cut rates | Explained")["howto_explainer"] == 1
    assert rule_formats("Is Trump Running Out of Steam?")["question"] == 1
    assert rule_formats("Joe Rogan Experience #2552 - Ehsan Ahmad")["episode_show"] == 1
    assert rule_formats("Hasan Reacts to the State of the Union")["reaction"] == 1
    assert rule_formats("5 Reasons The Left Is Losing")["listicle"] == 1
    assert rule_formats("A conversation with Sam Harris")["interview_guest"] == 1
    assert rule_formats("live from the studio")["breaking_live"] == 1          # leading 'live' (case-insensitive)
    assert rule_formats("Trump SLAMS Judge in Ballroom Appeal!")["confrontation"] == 1
    assert rule_formats("The border")["confrontation"] == 0 and rule_formats("The border")["episode_show"] == 0


def test_cohen_kappa():
    assert cohen_kappa([1, 1, 0, 0], [1, 1, 0, 0]) == 1.0
    assert abs(cohen_kappa([1, 0, 1, 0], [1, 1, 0, 0])) < 1e-9


def test_surname_key_and_js_distance():
    assert surname_key("Donald Trump") == "trump" and surname_key("Trump") == "trump"
    assert surname_key("Martin Luther King Jr.") == "king"
    P = np.array([[0.5, 0.5, 0.0], [0.5, 0.5, 0.0], [0.0, 0.0, 1.0]])
    D = js_distance_matrix(P)
    assert D[0, 1] == 0.0 and abs(D[0, 2] - 1.0) < 1e-9 and D[2, 0] == D[0, 2]


def test_factor_helpers():
    rng = np.random.RandomState(0)
    n = 300
    f1, f2 = rng.normal(size=n), rng.normal(size=n)
    X = np.column_stack([f1 + rng.normal(scale=.3, size=n), f1 + rng.normal(scale=.3, size=n), f2 + rng.normal(scale=.3, size=n),
                         f2 + rng.normal(scale=.3, size=n), rng.normal(size=n)])
    obs, thr, k = parallel_analysis(X, n_iter=20)
    assert k == 2 and obs[0] > thr[0]
    L = np.array([[0.8, 0.1], [-0.7, 0.0], [0.0, -0.9]])
    s = orient(L)
    assert s.tolist() == [1.0, -1.0]
    assert auto_name(pd.Series({"a_p100": 0.8, "b_mean": -0.5, "c_p100": 0.1})) == "+a -b"
    cells = pd.DataFrame({"x_p100": rng.uniform(1, 50, 100), "y_p100": rng.uniform(0, 0.2, 100), "z_mean": rng.normal(size=100), "n_chars_raw_mean": rng.normal(size=100)})
    cells["w_p100"] = cells["x_p100"] * 1.0001
    keep, dropped = select_features(cells)
    assert keep == ["x_p100", "z_mean"] and "y_p100" in dropped and "w_p100" in dropped and "n_chars_raw_mean" not in keep
