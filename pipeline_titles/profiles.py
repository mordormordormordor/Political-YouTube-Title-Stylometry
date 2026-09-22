"""Stage 6 - channel profiles behind the question documents (9, 11, 12, 13):

    caps_profile.csv        share of each creator x genre's unique titles by capitalization
                            style (all_caps, selective_caps, title_case, sentence_case,
                            mixed_other, short_other; rules in textstats.caps_style), read
                            with the channel's own tag words exempt from the shout test
                            (caps_tag_words.csv: the words of an edge segment the channel
                            repeats on at least CAPS_TAG_SHARE of its titles and CAPS_TAG_COUNT
                            times, "| REUTERS", "GRAPHIC WARNING:", detected with prepare's
                            brand patterns at that lower threshold), and
                            off the raw title as published: the normalized title strips a
                            channel's fixed show name and episode number along with its
                            brand tag, which left "Joe Rogan Experience #2551 - Daniel
                            Kokotajlo" as two words and "short / other"; a brand tag adds
                            capitalized words a Title Case rule does not mind, and one
                            always written in capitals is learned as an acronym;
                            caps_style_title.parquet carries the style of every unique
                            title (row_id, caps_style) for the Zipf / views stage
    top_words.csv           the most frequent non-stopwords: creator-balanced (mean over
                            ranked creators of the share of titles containing the word)
                            beside the raw pooled share
    arousal_index.csv       0-1 composite per creator x genre of five components: ALL-CAPS
                            word share, exclamation marks per title, power words per title
                            (shock words + violence verbs + intensifiers), emoji per title,
                            VADER intensity (positive + negative); each component winsorized
                            at the 2nd/98th percentile across ranked creators of the genre,
                            min-max scaled to 0-1, and averaged
    signature_keywords.csv  top 10 words per creator by weighted log-odds (informative
                            Dirichlet prior, alpha0 = 500) against all other creators' titles
    style_twins.csv         every (left channel, right channel) pair (the channel groups of
                            the leaning stage) with its distance in z-scored topic-controlled
                            style space; style_twins_nearest.csv gives each creator's nearest
                            cross-divide twin and how that distance ranks among all its
                            neighbors

CLI:
    python -m pipeline_titles.profiles
"""

from __future__ import annotations

import argparse
from collections import Counter
from typing import Optional, Sequence

import numpy as np
import pandas as pd

from pipeline_titles.annotate import build_case_lexicon
from pipeline_titles.common import ANALYSIS_DIR, CAPS_STYLE_TITLE, DIMENSIONS_CSV, FEATURES_TITLE, LOW_N, load_creators, load_prepared, stage_timer
from pipeline_titles.prepare import _WORD_RE_TAG, detect_brand_patterns
from pipeline_titles.textstats import CAPS_STYLES, caps_style, vocab_tokens, weighted_log_odds

EXCL_CAP = 3
# A channel's own tag: an edge segment (prefix, suffix, colon label, bracket, hashtag) it repeats on
# more than this share of its unique titles and at least this many times. Lower than prepare's brand
# threshold (20 %), because a tag used for one month ("| REUTERS" in January) is still the channel's.
CAPS_TAG_SHARE = 0.05
CAPS_TAG_COUNT = 20


def tag_words(titles, min_share: float = CAPS_TAG_SHARE, min_count: int = CAPS_TAG_COUNT) -> list[dict]:
    """The words (three or more letters, lower-cased) of one creator x genre's repeated edge segments, one row per word x pattern."""
    bp = detect_brand_patterns(list(titles), min_share, min_count)
    rows = []
    for r in bp.rows(len(titles)):
        for w in _WORD_RE_TAG.findall(r["pattern"]):
            if len(w) >= 3:
                rows.append({"word": w.lower(), "kind": r["kind"], "pattern": r["pattern"], "count": r["count"], "share": r["share"]})
    return rows
AROUSAL_COMPONENTS = ["caps_share", "exclamations", "power_words", "emoji", "vader_intensity"]


def arousal_index(df: pd.DataFrame, group_cols=("creator", "genre"), ranked: Optional[pd.Series] = None) -> pd.DataFrame:
    """Creator x genre means of the five components, winsorized (2nd/98th pct over the
    ranked creators of each genre), min-max scaled to 0-1 and averaged."""
    g = df.groupby(list(group_cols))[AROUSAL_COMPONENTS].mean().reset_index()
    g["n_titles"] = df.groupby(list(group_cols)).size().to_numpy()
    for comp in AROUSAL_COMPONENTS:
        g[comp + "_01"] = np.nan
    for genre, sub in g.groupby("genre"):
        ref = sub if ranked is None else sub[sub.set_index(["creator", "genre"]).index.map(ranked).fillna(False).to_numpy().astype(bool)]
        for comp in AROUSAL_COMPONENTS:
            lo, hi = np.nanpercentile(ref[comp], 2), np.nanpercentile(ref[comp], 98)
            x = sub[comp].clip(lo, hi)
            g.loc[sub.index, comp + "_01"] = (x - lo) / (hi - lo) if hi > lo else 0.0
    g["arousal_index"] = g[[c + "_01" for c in AROUSAL_COMPONENTS]].mean(axis=1)
    return g


def run(info: dict) -> None:
    prepared = load_prepared()
    creators = load_creators()[["creator", "group", "organisation", "clipper"]]
    uniq = prepared[~prepared["is_dup"]].copy()
    ranked = (~uniq.groupby(["creator", "genre"])["low_n"].first())
    uniq = uniq.merge(creators, on="creator", how="left")

    # ---- capitalization profile (on the raw title: the normalization strips show names and episode numbers, not just brand tags) ----
    _, acronyms = build_case_lexicon(uniq["title_raw"].drop_duplicates())
    tag_rows, styles = [], {}
    for (creator, genre), g in uniq.groupby(["creator", "genre"], sort=True):
        words = tag_words(g["title_raw"].tolist())
        tag_rows.extend({"creator": creator, "genre": genre, **w} for w in words)
        own = {w["word"] for w in words}
        for rid, t in zip(g["row_id"], g["title_raw"]):
            styles[rid] = caps_style(t, acronyms, own)
    uniq["caps_style"] = uniq["row_id"].map(styles)
    uniq[["row_id", "caps_style"]].to_parquet(CAPS_STYLE_TITLE, index=False)
    pd.DataFrame(tag_rows, columns=["creator", "genre", "word", "kind", "pattern", "count", "share"]).to_csv(ANALYSIS_DIR / "caps_tag_words.csv", index=False)
    cp = uniq.groupby(["creator", "genre"])["caps_style"].value_counts(normalize=True).unstack(fill_value=0.0).reindex(columns=CAPS_STYLES, fill_value=0.0).reset_index()
    cp["n_titles"] = uniq.groupby(["creator", "genre"]).size().to_numpy()
    cp["caps_any"] = cp["all_caps"] + cp["selective_caps"]
    cp["low_n"] = cp["n_titles"] < LOW_N
    cp = cp.merge(creators, on="creator", how="left").sort_values(["genre", "caps_any"], ascending=[True, False])
    cp.to_csv(ANALYSIS_DIR / "caps_profile.csv", index=False)
    (ANALYSIS_DIR / "caps_acronyms.txt").write_text("\n".join(sorted(acronyms)), encoding="utf-8")
    info["acronyms"] = len(acronyms)

    # ---- top words ----
    uniq["toks"] = uniq["title_norm"].map(lambda t: set(vocab_tokens(t)))
    vid = uniq[(uniq["genre"] == "videos")]
    vid_r = vid[vid.set_index(["creator", "genre"]).index.map(ranked).fillna(False).to_numpy().astype(bool)]
    raw = Counter()
    for s in vid["toks"]:
        raw.update(s)
    per_creator = {}
    for c, g in vid_r.groupby("creator"):
        cnt = Counter()
        for s in g["toks"]:
            cnt.update(s)
        per_creator[c] = {w: v / len(g) for w, v in cnt.items()}
    words = [w for w, _ in raw.most_common(400)]
    rows = []
    for w in words:
        shares = [d.get(w, 0.0) for d in per_creator.values()]
        rows.append({"word": w, "balanced_share_of_titles": float(np.mean(shares)), "creators_using": int(sum(s > 0 for s in shares)),
                     "raw_pooled_share_of_titles": raw[w] / len(vid), "raw_titles": raw[w]})
    tw = pd.DataFrame(rows).sort_values("balanced_share_of_titles", ascending=False)
    tw["rank_balanced"] = np.arange(1, len(tw) + 1)
    tw["rank_raw"] = tw["raw_titles"].rank(ascending=False).astype(int)
    tw.to_csv(ANALYSIS_DIR / "top_words.csv", index=False)

    # ---- arousal index ----
    ft = pd.read_parquet(FEATURES_TITLE, columns=["row_id", "allcaps_word_share", "shock_word", "violence_verb", "intensifier", "emoji_count", "vader_neg", "vader_pos"])
    a = uniq[["row_id", "creator", "genre", "title_norm"]].merge(ft, on="row_id")
    a["caps_share"] = a["allcaps_word_share"].fillna(0.0)
    a["exclamations"] = a["title_norm"].str.count("!").clip(upper=EXCL_CAP)
    a["power_words"] = a["shock_word"] + a["violence_verb"] + a["intensifier"]
    a["emoji"] = a["emoji_count"]
    a["vader_intensity"] = a["vader_neg"] + a["vader_pos"]
    ar = arousal_index(a, ranked=ranked)
    ar["low_n"] = ar["n_titles"] < LOW_N
    ar = ar.merge(creators, on="creator", how="left")
    for genre, sub in ar.groupby("genre"):
        ok = sub[~sub["low_n"]]
        ar.loc[ok.index, "rank_in_genre"] = ok["arousal_index"].rank(ascending=False).astype(int)
        ar.loc[ok.index, "percentile_in_genre"] = ok["arousal_index"].rank(pct=True) * 100
    ar.sort_values(["genre", "arousal_index"], ascending=[True, False]).to_csv(ANALYSIS_DIR / "arousal_index.csv", index=False)

    # ---- signature keywords (per creator, genres pooled) ----
    counts = {}
    for c, g in uniq.groupby("creator"):
        cnt = Counter()
        for t in g["title_norm"]:
            cnt.update(vocab_tokens(t))
        counts[c] = cnt
    total = Counter()
    for cnt in counts.values():
        total.update(cnt)
    krows = []
    for c, cnt in counts.items():
        rest = total - cnt
        wlo = weighted_log_odds(cnt, rest, alpha0=500.0)
        top = sorted(((w, d, z, ya, yb) for w, (d, z, ya, yb) in wlo.items() if ya >= 3), key=lambda x: -x[2])[:10]
        for rank, (w, d, z, ya, yb) in enumerate(top, start=1):
            krows.append({"creator": c, "rank": rank, "word": w, "z": round(z, 2), "log_odds": round(d, 3), "count_creator": ya, "count_rest": yb, "n_titles_creator": int(len(uniq[uniq['creator'] == c]))})
    kw = pd.DataFrame(krows).merge(creators[["creator", "group"]], on="creator", how="left")
    kw.to_csv(ANALYSIS_DIR / "signature_keywords.csv", index=False)

    # ---- stylistic twins across the divide (videos, ranked, non-clipper; left vs right channel groups) ----
    dims = pd.read_csv(DIMENSIONS_CSV)
    fcols = [c[:-11] for c in dims.columns if c.endswith("_controlled") and c[:-11].startswith("F") and c[1:-11].isdigit()]
    d = dims[(dims["genre"] == "videos") & (~dims["low_n"]) & (~dims["clipper"].astype(str).str.lower().eq("true"))].copy()
    Z = d[[f + "_controlled" for f in fcols]]
    Z = (Z - Z.mean()) / Z.std().replace(0, 1)
    X = Z.to_numpy(); names = d["creator"].tolist(); group_of = dict(zip(d["creator"], d["group"]))
    D = np.sqrt(((X[:, None, :] - X[None, :, :]) ** 2).sum(axis=2))
    all_pairs = D[np.triu_indices(len(names), 1)]
    left = [i for i, c in enumerate(names) if group_of[c] == "left"]
    right = [i for i, c in enumerate(names) if group_of[c] == "right"]
    prow = []
    for i in left:
        for j in right:
            prow.append({"left_creator": names[i], "right_creator": names[j], "distance": float(D[i, j]),
                         "distance_percentile_all_pairs": float((all_pairs < D[i, j]).mean() * 100)})
    pairs = pd.DataFrame(prow).sort_values("distance")
    pairs.to_csv(ANALYSIS_DIR / "style_twins.csv", index=False)
    nrow = []
    for i in left + right:
        other = right if i in left else left
        j = min(other, key=lambda k: D[i, k])
        order = np.argsort(D[i]); order = order[order != i]
        rank = int(np.where(order == j)[0][0]) + 1
        same = [k for k in (left if i in left else right) if k != i]
        nearest_same = min(same, key=lambda k: D[i, k]) if same else None
        nrow.append({"creator": names[i], "group": group_of[names[i]], "twin_across_divide": names[j], "twin_distance": float(D[i, j]),
                     "twin_rank_among_all_neighbours": rank, "nearest_same_group": names[nearest_same] if nearest_same is not None else "",
                     "nearest_same_group_distance": float(D[i, nearest_same]) if nearest_same is not None else np.nan,
                     "twin_closer_than_any_same_group": bool(nearest_same is not None and D[i, j] < D[i, nearest_same])})
    pd.DataFrame(nrow).sort_values("twin_distance").to_csv(ANALYSIS_DIR / "style_twins_nearest.csv", index=False)
    info["twin_pairs"] = len(pairs)


def main(argv: Optional[Sequence[str]] = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.parse_args(argv)
    with stage_timer("stage6_profiles") as info:
        run(info)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
