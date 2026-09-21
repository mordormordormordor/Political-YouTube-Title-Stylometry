"""Log-odds lexicons for document 14: which words are over-used on each side, a z cutoff
that sorts words into left / right / neither, how those classes compare across the judges
and against the channel groups, and what the word list can do on its own (a lexicon classifier of
titles, scored out of fold).

Weighted log-odds with an informative Dirichlet prior (Monroe, Colaresi and Quinn 2008;
textstats.weighted_log_odds, alpha0 = 500): for each word, log-odds of use in the right-side
titles against the left-side titles and its z-score. A word is `right` when z >= cutoff,
`left` when z <= -cutoff, otherwise `neither` (cutoff 1.96 = the two-sided 5 % level; words
with fewer than 3 occurrences in both sides together are not classified).

Comparisons (left side vs right side): titles (the titles the judge labeled left vs right)
and channels (everything the left channels published vs everything the right channels
published, channels grouped by their score), the same systems as the allotaxonographs.

The lexicon check. For each judge, its labeled titles are split into five folds by channel;
the lexicon is built on four folds and applied to the fifth, so no channel's titles help
classify themselves. A title is `left` when it holds more left-class words than right-class
words, `right` the other way round, `neither` when the counts tie (including no classified
word). Agreement with the judge's own labels says how much of the judge's reading is
vocabulary; the rest is wording the list cannot see.

Called from pipeline_titles.leaning.analyse(); also runnable alone once leaning_labels.csv exists:
    python -m pipeline_titles.leaning_lexicon [--cutoff 1.96]

Outputs (data/titles/analysis/):
    leaning_logodds.csv            per comparison and word: log-odds (right vs left), z, counts, class
    leaning_logodds_summary.csv    per comparison: words in each class at the cutoff, the top words each side
    leaning_logodds_agreement.csv  every pair of comparisons over their shared words: kappa of the classes,
                                   the counts of each class pair, the words that change side
    leaning_lexicon_validation.csv per judge: agreement of the out-of-fold lexicon classifier with the judge
                                   (coverage, accuracy, kappa, side agreement on partisan titles, per-class
                                   precision and recall, channel-level Spearman and group agreement)
    leaning_lexicon_channels.csv   per channel (judge of record): lexicon score vs judge score
"""

from __future__ import annotations

import argparse
import json
from collections import Counter
from typing import Optional, Sequence

import numpy as np
import pandas as pd

from pipeline_titles.common import ANALYSIS_DIR, SEED, stage_timer
from pipeline_titles.textstats import vocab_tokens, weighted_log_odds

CUTOFF = 1.96
MIN_COUNT = 3
N_FOLDS = 5
CLASSES = ("left", "neither", "right")


def word_classes(titles_left: Sequence[str], titles_right: Sequence[str], cutoff: float = CUTOFF, min_count: int = MIN_COUNT) -> pd.DataFrame:
    """Weighted log-odds of every word in right-side titles against left-side titles (z > 0 =
    over-used on the right) and its class at the cutoff. Words seen fewer than `min_count`
    times in both sides together are dropped."""
    cl, cr = Counter(), Counter()
    for t in titles_left:
        cl.update(vocab_tokens(t))
    for t in titles_right:
        cr.update(vocab_tokens(t))
    wlo = weighted_log_odds(cr, cl, alpha0=500.0)
    rows = [{"word": w, "log_odds_right_vs_left": round(d, 4), "z": round(z, 3), "count_right": yr, "count_left": yl}
            for w, (d, z, yr, yl) in wlo.items() if yr + yl >= min_count]
    df = pd.DataFrame(rows, columns=["word", "log_odds_right_vs_left", "z", "count_right", "count_left"])
    df["word_class"] = np.where(df["z"] >= cutoff, "right", np.where(df["z"] <= -cutoff, "left", "neither"))
    return df.sort_values("z", ascending=False).reset_index(drop=True)


def classify_title(title: str, lexicon: dict[str, str]) -> tuple[str, int, int]:
    """Majority of classified words: ('left' | 'right' | 'neither', n_left_words, n_right_words)."""
    n_l = n_r = 0
    for w in vocab_tokens(title):
        c = lexicon.get(w)
        if c == "left":
            n_l += 1
        elif c == "right":
            n_r += 1
    return ("left" if n_l > n_r else "right" if n_r > n_l else "neither"), n_l, n_r


def creator_folds(creators: Sequence[str], n_folds: int = N_FOLDS, seed: int = SEED) -> dict[str, int]:
    """Fold per channel (a channel's titles never build the lexicon that scores them)."""
    rng = np.random.RandomState(seed)
    uniq = sorted(set(creators))
    perm = rng.permutation(len(uniq))
    return {c: int(perm[i] % n_folds) for i, c in enumerate(uniq)}


def lexicon_check(df: pd.DataFrame, label_col: str, cutoff: float = CUTOFF, n_folds: int = N_FOLDS) -> tuple[pd.DataFrame, dict]:
    """Out-of-fold lexicon classes for every title with a label from `label_col`; returns the
    per-title frame (creator, title_norm, label, lexicon_class, n_left_words,
    n_right_words, fold) and the agreement summary."""
    from sklearn.metrics import cohen_kappa_score
    d = df.dropna(subset=[label_col]).copy()
    folds = creator_folds(d["creator"].tolist(), n_folds)
    d["fold"] = d["creator"].map(folds)
    out = []
    for k in range(n_folds):
        train, test = d[d["fold"] != k], d[d["fold"] == k]
        wc = word_classes(train.loc[train[label_col] == "left", "title_norm"], train.loc[train[label_col] == "right", "title_norm"], cutoff)
        lex = dict(zip(wc.loc[wc["word_class"] != "neither", "word"], wc.loc[wc["word_class"] != "neither", "word_class"]))
        for r in test.itertuples():
            c, n_l, n_r = classify_title(r.title_norm, lex)
            out.append({"row_id": r.row_id, "creator": r.creator, "title_norm": r.title_norm, "label": getattr(r, label_col), "lexicon_class": c, "n_left_words": n_l, "n_right_words": n_r, "fold": k})
    t = pd.DataFrame(out)
    y, p = t["label"], t["lexicon_class"]
    partisan = y.isin(["left", "right"])
    both = partisan & p.isin(["left", "right"])
    conf = pd.crosstab(y, p).reindex(index=CLASSES, columns=CLASSES, fill_value=0)
    summ = {"judge": label_col, "n_titles": int(len(t)), "coverage": round(float((t["n_left_words"] + t["n_right_words"] > 0).mean()), 4),
            "accuracy": round(float((y == p).mean()), 4), "kappa": round(float(cohen_kappa_score(y, p)), 4),
            "judge_partisan_share": round(float(partisan.mean()), 4), "lexicon_partisan_share": round(float(p.isin(["left", "right"]).mean()), 4),
            "partisan_titles_lexicon_neither": round(float((p[partisan] == "neither").mean()), 4),
            "side_agreement_when_both_partisan": round(float((y[both] == p[both]).mean()), 4) if both.any() else np.nan}
    for c in ("left", "right"):
        tp = int(((y == c) & (p == c)).sum()); fp = int(((y != c) & (p == c)).sum()); fn = int(((y == c) & (p != c)).sum())
        summ[f"precision_{c}"] = round(tp / (tp + fp), 4) if tp + fp else np.nan
        summ[f"recall_{c}"] = round(tp / (tp + fn), 4) if tp + fn else np.nan
    summ["confusion"] = json.dumps({r: {c: int(conf.loc[r, c]) for c in CLASSES} for r in CLASSES})
    # channel level
    ch = t.groupby("creator").agg(n_titles=("label", "size"),
                                  lexicon_score=("lexicon_class", lambda s: float(((s == "right").sum() - (s == "left").sum()) / len(s))),
                                  judge_score=("label", lambda s: float(((s == "right").sum() - (s == "left").sum()) / len(s)))).reset_index()
    side = lambda s: np.where(s > 0.05, "right", np.where(s < -0.05, "left", "neutral"))
    ch["lexicon_group"], ch["judge_group"] = side(ch["lexicon_score"]), side(ch["judge_score"])
    big = ch[ch["n_titles"] >= 16]
    summ["n_channels"] = int(len(big)); summ["channel_spearman"] = round(float(big["lexicon_score"].corr(big["judge_score"], method="spearman")), 4) if len(big) > 5 else np.nan
    summ["channel_group_agreement"] = round(float((big["lexicon_group"] == big["judge_group"]).mean()), 4) if len(big) else np.nan
    summ["channel_group_kappa"] = round(float(cohen_kappa_score(big["judge_group"], big["lexicon_group"])), 4) if len(big) > 5 else np.nan
    return t.merge(ch[["creator", "lexicon_score", "judge_score", "lexicon_group", "judge_group"]], on="creator", how="left"), summ


def class_agreement(classes: dict[str, pd.DataFrame]) -> pd.DataFrame:
    """Pairwise agreement of the word classes between comparisons over their shared words."""
    from sklearn.metrics import cohen_kappa_score
    names = list(classes); rows = []
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            a, b = classes[names[i]], classes[names[j]]
            m = a[["word", "word_class", "z"]].merge(b[["word", "word_class", "z"]], on="word", suffixes=("_a", "_b"))
            if len(m) < 10:
                continue
            ct = pd.crosstab(m["word_class_a"], m["word_class_b"]).reindex(index=CLASSES, columns=CLASSES, fill_value=0)
            switch = m[((m.word_class_a == "left") & (m.word_class_b == "right")) | ((m.word_class_a == "right") & (m.word_class_b == "left"))]
            both_part = m[(m.word_class_a != "neither") & (m.word_class_b != "neither")]
            rows.append({"a": names[i], "b": names[j], "n_shared_words": int(len(m)), "kappa": round(float(cohen_kappa_score(m["word_class_a"], m["word_class_b"])), 4),
                         "exact_agreement": round(float((m["word_class_a"] == m["word_class_b"]).mean()), 4),
                         "both_partisan": int(len(both_part)), "same_side_when_both_partisan": round(float((both_part.word_class_a == both_part.word_class_b).mean()), 4) if len(both_part) else np.nan,
                         "z_spearman": round(float(m["z_a"].corr(m["z_b"], method="spearman")), 4),
                         **{f"{r}_{c}": int(ct.loc[r, c]) for r in CLASSES for c in CLASSES},
                         "side_switchers": ", ".join(f"{w} ({za:+.1f} / {zb:+.1f})" for w, za, zb in switch.sort_values("z_a")[["word", "z_a", "z_b"]].itertuples(index=False))})
    return pd.DataFrame(rows)


def run(df: pd.DataFrame, cols: list[str], judge: str, cutoff: float = CUTOFF, info: Optional[dict] = None) -> None:
    """All outputs. `df` is the labels frame (one row per title with the label columns), `judge`
    the judge-of-record column (e.g. label_claude_code_opus)."""
    from pipeline_titles.allotax import MODEL_NAMES, comparisons
    classes, summ_rows, all_rows = {}, [], []
    for comp in comparisons():
        wc = word_classes(comp["titles1"], comp["titles2"], cutoff)
        classes[comp["name"]] = wc
        all_rows.append(wc.assign(comparison=comp["name"]))
        vc = wc["word_class"].value_counts()
        summ_rows.append({"comparison": comp["name"], "system_left": comp["title1"], "system_right": comp["title2"], "cutoff_z": cutoff, "n_words": int(len(wc)),
                          "n_left": int(vc.get("left", 0)), "n_right": int(vc.get("right", 0)), "n_neither": int(vc.get("neither", 0)),
                          "top_right": ", ".join(wc.head(15)["word"]), "top_left": ", ".join(wc.sort_values("z").head(15)["word"])})
    pd.concat(all_rows)[["comparison", "word", "log_odds_right_vs_left", "z", "count_right", "count_left", "word_class"]].to_csv(ANALYSIS_DIR / "leaning_logodds.csv", index=False)
    pd.DataFrame(summ_rows).to_csv(ANALYSIS_DIR / "leaning_logodds_summary.csv", index=False)
    class_agreement(classes).to_csv(ANALYSIS_DIR / "leaning_logodds_agreement.csv", index=False)
    # the lexicon classifier, out of fold, for every judge
    val = []
    for c in cols:
        if c not in MODEL_NAMES:
            continue
        titles, s = lexicon_check(df, c, cutoff)
        val.append(s)
        if c == judge:
            titles.groupby("creator").agg(n_titles=("label", "size"), lexicon_score=("lexicon_score", "first"), judge_score=("judge_score", "first"), lexicon_group=("lexicon_group", "first"), judge_group=("judge_group", "first")).reset_index() \
                .sort_values("judge_score").to_csv(ANALYSIS_DIR / "leaning_lexicon_channels.csv", index=False)
            titles[["row_id", "creator", "label", "lexicon_class", "n_left_words", "n_right_words", "fold"]].to_csv(ANALYSIS_DIR / "leaning_lexicon_titles.csv", index=False)
    pd.DataFrame(val).to_csv(ANALYSIS_DIR / "leaning_lexicon_validation.csv", index=False)
    if info is not None and val:
        info["lexicon"] = {v["judge"]: {"accuracy": v["accuracy"], "kappa": v["kappa"], "channel_spearman": v["channel_spearman"]} for v in val}
    print(pd.DataFrame(summ_rows)[["comparison", "n_words", "n_left", "n_right", "n_neither"]].to_string(index=False), flush=True)
    if val:
        print(pd.DataFrame(val)[["judge", "coverage", "accuracy", "kappa", "side_agreement_when_both_partisan", "channel_spearman", "channel_group_agreement"]].to_string(index=False), flush=True)


def main(argv: Optional[Sequence[str]] = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--cutoff", type=float, default=CUTOFF)
    a = ap.parse_args(argv)
    with stage_timer("leaning_lexicon", cutoff=a.cutoff) as info:
        df = pd.read_csv(ANALYSIS_DIR / "leaning_labels.csv.gz")
        cols = [c for c in df.columns if c.startswith("label_")]
        judge = json.loads((ANALYSIS_DIR / "leaning_summary.json").read_text())["judge_of_record"]
        run(df, cols, judge, a.cutoff, info)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
