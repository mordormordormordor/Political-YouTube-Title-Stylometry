"""Stage 3 - structural formats by rule and semantic hooks by LLM + classifier.

Formats (regex on the RAW title, case-insensitive unless noted; the exact patterns
are written to format_rules.csv): question, breaking_live, episode_show,
interview_guest, reaction, confrontation, listicle, howto_explainer.

Hooks (curiosity_gap, outrage, humor): the LLM labels of the 3,000-title sample
(labels.csv) train one logistic-regression classifier per hook on the title's
sentence embedding plus 12 style features; 5-fold cross-validation chooses C, a
stratified 20 % hold-out reports accuracy / balanced accuracy / F1 / AUC, and the
model refitted on the whole sample is applied to every unique title.

Outputs (data/titles/analysis/):
    formats.parquet          row_id + format flags + hook probabilities and labels
    format_rules.csv         the regexes
    format_hook_shares.csv   creator x genre shares (unique titles) and lane x genre
                             means of creator shares (non-low-n creators)
    format_examples.csv      three examples per category per lane and corpus-wide
    hook_classifier.json     CV and hold-out metrics per hook
    format_agreement.csv     rule vs LLM format label on the rated sample
                             (precision / recall / F1 / Cohen's kappa per category)

CLI:
    python -m pipeline_titles.formats
"""

from __future__ import annotations

import argparse
import json
import re
from typing import Optional, Sequence

import numpy as np
import pandas as pd

from pipeline_titles.common import (
    ANALYSIS_DIR, FEATURES_TITLE, FORMATS_PARQUET, LABELS_CSV, LOW_N, SEED, load_lanes, load_prepared, stage_timer,
)
from pipeline_titles.embed import load_embeddings

FORMAT_RULES = {
    "question": r"\?|^\W*(?:who|what|when|where|why|how|which|whose|is|are|was|were|do|does|did|can|could|should|will|would|has|have|had|isn't|aren't|doesn't|don't|didn't|can't|couldn't|shouldn't|wouldn't)\b(?![^|]*[.!]$)",
    "breaking_live": r"^\W*(?:breaking|just in|developing|live|watch live|livestream|live stream|replay|live replay|watch|alert|urgent|exclusive|bombshell)\b|\bbreaking news\b|\bLIVE\b\s*[:|\-–—]|[:|\-–—]\s*\bLIVE\b|\blive now\b",
    "episode_show": r"\b(?:ep|eps|episode)\.?\s*#?\s*\d+\b|#\d{2,5}\b|\bs\d{1,2}\s*e\d{1,3}\b|\bseason\s+\d+\b|\bhour\s+\d\b|\b\d{1,2}[/.]\d{1,2}[/.]\d{2,4}\b|\b20\d{2}-\d{2}-\d{2}\b|\b(?:jan|feb|mar|apr|may|jun|jul|aug|sep|sept|oct|nov|dec)[a-z]*\.?\s+\d{1,2}(?:st|nd|rd|th)?,?\s+20\d{2}\b",
    "interview_guest": r"\bwith\s+(?:[A-Z@][\w.'’-]+)|\bw/\s*\S|\bft\.?\s+\S|\bfeat\.?\s+\S|\bfeaturing\b|\bjoins\b|\binterview(?:s|ed|ing)?\b|\bin conversation with\b|\bsits down with\b|\btalks (?:to|with)\b|\bspeaks (?:to|with)\b|\bguest\b|\bQ&A\b",
    "reaction": r"\breact(?:s|ed|ing|ion|ions)?\b|\brespon(?:ds|se|ding)\b|\bresponds?\b|\bwatching\b|\bfirst time (?:watching|hearing|seeing)\b",
    "confrontation": r"\bvs\.?\b|\bversus\b|\bdebat(?:e|es|ed|ing)\b|\b(?:destroys?|destroyed|owns?|owned|shreds?|shredded|humiliat(?:es|ed)|dismantl(?:es|ed)|obliterat(?:es|ed)|schools?|schooled|clash(?:es)?|showdown|confront(?:s|ed)?|faces? off|takes? on|takes? down|eviscerat(?:es|ed)|roast(?:s|ed)|wreck(?:s|ed)|grill(?:s|ed)|crush(?:es|ed)|slams?|slammed|blasts?|blasted|rips?|ripped|torch(?:es|ed)|calls? out|called out|shuts? down|fires? back|hits? back|goes? off on|checks?|checked)\b",
    "listicle": r"^\W*(?:top\s+|the\s+)?\d{1,2}\s+(?:\w+\s+)?(?:things|reasons|ways|times|signs|facts|lessons|tips|moments|questions|mistakes|rules|takeaways|lies|truths|myths|predictions|best|worst|biggest|most|craziest|dumbest)\b|\btop\s+\d{1,2}\b|\b\d{1,2}\s+(?:things|reasons|ways|signs|facts|lessons|tips|mistakes|myths|questions|predictions)\b",
    "howto_explainer": r"\bhow\s+to\b|\bexplain(?:ed|er|s|ing)?\b|\bbreak(?:s|ing)?\s+down\b|\bbreakdown\b|\bwhat\s+(?:is|are|it\s+means|you\s+need|really\s+happened|happened)\b|\bwhy\b|\beverything\s+you\s+need\b|\b101\b|\bguide\b|\bdeep\s+dive\b|\bthe\s+(?:truth|real\s+reason|real\s+story|history)\b|\bunderstanding\b|\banalysis\b|\bexplainer\b",
}
FORMATS = list(FORMAT_RULES)
HOOKS = ["curiosity_gap", "outrage", "humor"]
STYLE_FOR_HOOKS = ["allcaps_word_share", "excl", "q_mark", "trailing_ellipsis", "violence_verb", "shock_word", "curiosity_lex",
                   "fwd_ref_start", "discourse_marker", "has_person", "neg_eval", "pos_eval"]
_COMPILED = {k: re.compile(v, re.I if k != "breaking_live" else 0) for k, v in FORMAT_RULES.items()}
_BREAKING_CI = re.compile(r"^\W*(?:breaking|just in|developing|live|watch live|livestream|live stream|replay|live replay|watch|alert|urgent|exclusive|bombshell)\b|\bbreaking news\b|\blive now\b", re.I)
_LIVE_CS = re.compile(r"\bLIVE\b\s*[:|\-–—]|[:|\-–—]\s*\bLIVE\b")


def rule_formats(title: str) -> dict[str, int]:
    """Format flags of one raw title (see FORMAT_RULES)."""
    out = {}
    for k, rx in _COMPILED.items():
        if k == "breaking_live":
            out[k] = int(bool(_BREAKING_CI.search(title) or _LIVE_CS.search(title)))
        else:
            out[k] = int(bool(rx.search(title)))
    return out


def cohen_kappa(a: np.ndarray, b: np.ndarray) -> float:
    a, b = np.asarray(a).astype(int), np.asarray(b).astype(int)
    po = np.mean(a == b)
    pe = np.mean(a) * np.mean(b) + (1 - np.mean(a)) * (1 - np.mean(b))
    return float((po - pe) / (1 - pe)) if pe < 1 else float("nan")


def train_hook_classifier(X: np.ndarray, y: np.ndarray, seed: int = SEED) -> tuple[object, dict]:
    from sklearn.linear_model import LogisticRegression
    from sklearn.metrics import balanced_accuracy_score, f1_score, roc_auc_score
    from sklearn.model_selection import StratifiedKFold, train_test_split
    from sklearn.pipeline import make_pipeline
    from sklearn.preprocessing import StandardScaler

    Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.2, stratify=y, random_state=seed)
    best_c, best_f1 = None, -1
    cv = StratifiedKFold(5, shuffle=True, random_state=seed)
    cv_scores = {}
    for C in (0.03, 0.1, 0.3, 1.0):
        f1s = []
        for tr, va in cv.split(Xtr, ytr):
            m = make_pipeline(StandardScaler(), LogisticRegression(C=C, class_weight="balanced", max_iter=2000))
            m.fit(Xtr[tr], ytr[tr])
            f1s.append(f1_score(ytr[va], m.predict(Xtr[va])))
        cv_scores[C] = round(float(np.mean(f1s)), 4)
        if np.mean(f1s) > best_f1:
            best_f1, best_c = float(np.mean(f1s)), C
    m = make_pipeline(StandardScaler(), LogisticRegression(C=best_c, class_weight="balanced", max_iter=2000))
    m.fit(Xtr, ytr)
    p = m.predict_proba(Xte)[:, 1]
    pred = (p >= 0.5).astype(int)
    metrics = {"n_train": int(len(ytr)), "n_test": int(len(yte)), "base_rate": round(float(y.mean()), 4), "C": best_c,
               "cv_f1_by_C": cv_scores, "holdout_accuracy": round(float(np.mean(pred == yte)), 4),
               "holdout_balanced_accuracy": round(float(balanced_accuracy_score(yte, pred)), 4),
               "holdout_f1": round(float(f1_score(yte, pred)), 4),
               "holdout_auc": round(float(roc_auc_score(yte, p)), 4) if len(set(yte)) > 1 else None,
               "holdout_kappa": round(cohen_kappa(yte, pred), 4)}
    final = make_pipeline(StandardScaler(), LogisticRegression(C=best_c, class_weight="balanced", max_iter=2000)).fit(X, y)
    return final, metrics


def run(info: dict) -> None:
    prepared = load_prepared()
    lanes = load_lanes()[["creator", "lane", "organisation", "clipper"]]
    uniq = prepared[~prepared["is_dup"]].reset_index(drop=True)
    # ---- rule formats on raw titles (unique rows; repeats copy) ----
    fm = pd.DataFrame([rule_formats(t) for t in uniq["title_raw"]])
    fm.insert(0, "row_id", uniq["row_id"].to_numpy())
    pd.DataFrame([{"format": k, "regex": v, "flags": "case-insensitive" + (" (LIVE label case-sensitive)" if k == "breaking_live" else "")}
                  for k, v in FORMAT_RULES.items()]).to_csv(ANALYSIS_DIR / "format_rules.csv", index=False)

    # ---- hook classifier ----
    labels = pd.read_csv(LABELS_CSV)
    labels = labels[labels["sensational"].notna()]
    emb, idx = load_embeddings()
    tf = pd.read_parquet(FEATURES_TITLE, columns=["row_id"] + STYLE_FOR_HOOKS).set_index("row_id")
    norm_of = uniq.set_index("row_id")["title_norm"]

    def design(row_ids: np.ndarray) -> np.ndarray:
        rows = norm_of.loc[row_ids].map(idx).to_numpy()
        e = emb[rows]
        s = tf.loc[row_ids, STYLE_FOR_HOOKS].to_numpy(dtype=float)
        s = np.where(np.isnan(s), 0.0, s)
        return np.hstack([e, s])

    Xl = design(labels["row_id"].to_numpy())
    metrics, probs = {}, {}
    X_all = design(uniq["row_id"].to_numpy())
    for h in HOOKS:
        y = labels[h].to_numpy().astype(int)
        model, m = train_hook_classifier(Xl, y)
        metrics[h] = m
        probs[h] = model.predict_proba(X_all)[:, 1]
        print(f"  {h}: base rate {m['base_rate']}, hold-out acc {m['holdout_accuracy']} bal-acc {m['holdout_balanced_accuracy']} F1 {m['holdout_f1']} AUC {m['holdout_auc']}", flush=True)
    (ANALYSIS_DIR / "hook_classifier.json").write_text(json.dumps({"features": f"{emb.shape[1]}-d sentence embedding + {STYLE_FOR_HOOKS}",
                                                                    "model": "StandardScaler + LogisticRegression(class_weight=balanced)", "hooks": metrics}, indent=2))
    for h in HOOKS:
        fm[f"p_{h}"] = probs[h].astype(np.float32)
        fm[h] = (probs[h] >= 0.5).astype(int)
    info.update({f"{h}_holdout_f1": metrics[h]["holdout_f1"] for h in HOOKS})

    # propagate to duplicates
    key = uniq[["row_id", "creator", "genre", "title_raw"]].merge(fm, on="row_id")
    all_rows = prepared[["row_id", "creator", "genre", "title_raw", "is_dup", "month"]].merge(
        key.drop(columns=["row_id"]).drop_duplicates(["creator", "genre", "title_raw"]), on=["creator", "genre", "title_raw"], how="left")
    all_rows.to_parquet(FORMATS_PARQUET, index=False)

    # ---- shares per creator x genre and per lane x genre ----
    cats = FORMATS + HOOKS
    u = all_rows[~all_rows["is_dup"]]
    cg = u.groupby(["creator", "genre"]).agg(n_unique=("row_id", "size"), **{c: (c, "mean") for c in cats}).reset_index()
    cg["low_n"] = cg["n_unique"] < LOW_N
    cg = cg.merge(lanes, on="creator", how="left")
    cg["level"] = "creator"
    ln = cg[~cg["low_n"]].groupby(["lane", "genre"]).agg(n_creators=("creator", "size"), **{c: (c, "mean") for c in cats}).reset_index()
    ln["level"] = "lane_mean_of_creators"
    raw = u.merge(lanes, on="creator", how="left").groupby(["lane", "genre"]).agg(n_unique=("row_id", "size"), **{c: (c, "mean") for c in cats}).reset_index()
    raw["level"] = "lane_raw_pooled"
    pd.concat([cg, ln, raw], ignore_index=True).to_csv(ANALYSIS_DIR / "format_hook_shares.csv", index=False)

    # ---- examples: per category, corpus-wide and per lane ----
    ex_rows = []
    rng = np.random.RandomState(SEED)
    ul = u.merge(lanes, on="creator", how="left")
    for c in cats:
        pool = ul[ul[c] == 1]
        pick = pool.sort_values(f"p_{c}", ascending=False) if c in HOOKS else pool.iloc[rng.permutation(len(pool))]
        for t in pick.drop_duplicates("creator").head(3).itertuples():
            ex_rows.append({"category": c, "scope": "corpus", "creator": t.creator, "title": t.title_raw})
        for lane, sub in pick.groupby("lane"):
            for t in sub.drop_duplicates("creator").head(3).itertuples():
                ex_rows.append({"category": c, "scope": lane, "creator": t.creator, "title": t.title_raw})
    pd.DataFrame(ex_rows).to_csv(ANALYSIS_DIR / "format_examples.csv", index=False)

    # ---- rule vs LLM format agreement on the rated sample ----
    lab = labels.merge(fm[["row_id"] + FORMATS + [f"p_{h}" for h in HOOKS]], on="row_id")
    rows = []
    for c in FORMATS:
        llm = (lab["format_llm"] == c).astype(int).to_numpy()
        rule = lab[c].to_numpy().astype(int)
        tp = int(((rule == 1) & (llm == 1)).sum())
        prec = tp / max(rule.sum(), 1); rec = tp / max(llm.sum(), 1)
        rows.append({"category": c, "n": len(lab), "rule_positives": int(rule.sum()), "llm_positives": int(llm.sum()),
                     "precision_rule_vs_llm": round(prec, 3), "recall_rule_vs_llm": round(rec, 3),
                     "f1": round(2 * prec * rec / max(prec + rec, 1e-9), 3), "kappa": round(cohen_kappa(rule, llm), 3),
                     "agreement": round(float(np.mean(rule == llm)), 3)})
    for h in HOOKS:  # classifier (refit on all labels, so in-sample) vs the LLM label, for reference only
        llm = lab[h].to_numpy().astype(int)
        pred = (lab[f"p_{h}"] >= 0.5).astype(int).to_numpy()
        tp = int(((pred == 1) & (llm == 1)).sum())
        prec = tp / max(pred.sum(), 1); rec = tp / max(llm.sum(), 1)
        rows.append({"category": h + " (classifier, in-sample)", "n": len(lab), "rule_positives": int(pred.sum()), "llm_positives": int(llm.sum()),
                     "precision_rule_vs_llm": round(prec, 3), "recall_rule_vs_llm": round(rec, 3),
                     "f1": round(2 * prec * rec / max(prec + rec, 1e-9), 3), "kappa": round(cohen_kappa(pred, llm), 3),
                     "agreement": round(float(np.mean(pred == llm)), 3)})
    pd.DataFrame(rows).to_csv(ANALYSIS_DIR / "format_agreement.csv", index=False)


def main(argv: Optional[Sequence[str]] = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.parse_args(argv)
    with stage_timer("stage3_formats") as info:
        run(info)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
