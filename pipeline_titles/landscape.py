"""Stage 4 - the landscape: creators clustered in style space and in topic space,
compared with the channel groups (left / neutral / right, from the leaning stage);
nearest neighbours; who gets named; convergent formulas.

Reads dimensions.csv / dimensions_title.parquet (Stage 2), topics.csv +
topic_labels.csv + creator_topic_mix.csv (Stage 1), formats.parquet (Stage 3),
annotations.parquet, titles_prepared.parquet and creators.csv (with the groups).

Every similarity is computed per genre over non-low-n creators, with cross-posted
titles removed (a title whose case-insensitive key also appears under another
creator of the same organisation, e.g. TYT / The Damage Report). The whole
clustering block runs twice: on all titles and on political titles only.

Outputs (data/titles/analysis/):
    style_clusters.csv, topic_clusters.csv     cluster id per creator x genre (all / political)
    cluster_comparison.csv                     adjusted Rand index: style vs group, topic vs group, style vs topic
    group_style_cohesion.csv                   within-group vs between-group style distance per channel group
    disagreements_group_style.csv              group-mates in different style clusters, and style-mates across groups
    neighbours_style.csv, neighbours_topic.csv five nearest neighbours per creator x genre
    map_style.csv, map_topic.csv               2-D coordinates (PCA of style z-scores; MDS of topic JS distance)
    entities_top.csv                           top 25 people and organisations (creator-balanced counts), the
                                               channel groups naming them most, outrage-frame share vs overall
    shared_titles.csv, shared_templates.csv    verbatim titles / masked templates used by >= 2 creators
    org_style.csv                              organisation-level style scores (title-weighted mean of members)

CLI:
    python -m pipeline_titles.landscape
"""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter, defaultdict
from typing import Optional, Sequence

import numpy as np
import pandas as pd

from pipeline_titles.common import (
    ANALYSIS_DIR, STOPWORDS, ANNOTATIONS, DIMENSIONS_CSV, DIMENSIONS_TITLE, FORMATS_PARQUET, LOW_N, SEED, TOPICS_CSV,
    load_creators, load_prepared, stage_timer,
)
from pipeline_titles.features import mask_tokens
from pipeline_titles.topics import normalise_entity

K_RANGE = range(3, 13)


# --------------------------------------------------------------------------- #
# Pure helpers
# --------------------------------------------------------------------------- #
def js_distance_matrix(P: np.ndarray) -> np.ndarray:
    """Pairwise Jensen-Shannon distance (sqrt of JS divergence, base 2) between rows of a stochastic matrix."""
    from scipy.spatial.distance import jensenshannon
    n = len(P)
    D = np.zeros((n, n))
    for i in range(n):
        for j in range(i + 1, n):
            D[i, j] = D[j, i] = jensenshannon(P[i], P[j], base=2)
    return np.nan_to_num(D)


def best_k_agglomerative(X: np.ndarray, metric: str, linkage: str, ks=K_RANGE, precomputed: bool = False, seed: int = SEED):
    from sklearn.cluster import AgglomerativeClustering
    from sklearn.metrics import silhouette_score
    best = (None, -1, None)
    scores = {}
    for k in ks:
        if k >= len(X):
            break
        model = AgglomerativeClustering(n_clusters=k, metric="precomputed" if precomputed else metric, linkage=linkage)
        lab = model.fit_predict(X)
        s = silhouette_score(X, lab, metric="precomputed" if precomputed else metric)
        scores[k] = round(float(s), 4)
        if s > best[1]:
            best = (k, s, lab)
    return best[0], best[1], best[2], scores


_NOT_NAME = {"live", "show", "podcast", "news", "report", "tv", "radio", "clips", "channel", "update", "updates", "hour", "daily"}


def surname_key(name: str) -> str:
    """Canonical key for a PERSON string: the last alphabetic token (Trump, Kirk...).
    Shouted verbs glued to a name ('Trump PANICS') and show words ('Kyle Kulinski
    Show') are dropped first; an all-caps name ('TRUMP') is kept."""
    toks = [t for t in re.split(r"[\s\-]+", name) if re.fullmatch(r"[A-Za-z][A-Za-z'’.]*", t)]
    if len(toks) > 1 and any(not t.isupper() for t in toks):
        toks = [t for t in toks if not (t.isupper() and len(t) >= 3)]
    toks = [t for t in toks if t.lower() not in _NOT_NAME] or toks
    if not toks:
        return name.lower()
    last = toks[-1].lower().rstrip(".")
    if last in {"jr", "sr", "ii", "iii"} and len(toks) > 1:
        last = toks[-2].lower()
    return last


# --------------------------------------------------------------------------- #
def cluster_block(vec_style: pd.DataFrame, mix: pd.DataFrame, creators_tbl: pd.DataFrame, tag: str, genre: str, out: dict) -> None:
    """One (genre, all/political) run: cluster in style and topic space, compare with the channel groups."""
    from sklearn.decomposition import PCA
    from sklearn.manifold import MDS
    from sklearn.metrics import adjusted_rand_score
    creators = sorted(set(vec_style.index) & set(mix.index))
    if len(creators) < 8:
        return
    S = vec_style.loc[creators]
    Z = (S - S.mean()) / S.std().replace(0, 1)
    k_s, sil_s, lab_s, scores_s = best_k_agglomerative(Z.to_numpy(), "euclidean", "ward")
    P = mix.loc[creators].to_numpy()
    P = P / P.sum(axis=1, keepdims=True)
    D = js_distance_matrix(P)
    k_t, sil_t, lab_t, scores_t = best_k_agglomerative(D, "precomputed", "average", precomputed=True)
    group_of = creators_tbl.set_index("creator")["group"]
    group_lab = pd.Series(creators).map(group_of).fillna("unscored").to_numpy()
    n_groups = len(set(group_lab))
    # also a group-count solution for a like-for-like ARI
    from sklearn.cluster import AgglomerativeClustering
    lab_s_G = AgglomerativeClustering(n_clusters=min(n_groups, len(creators) - 1), linkage="ward").fit_predict(Z.to_numpy())
    lab_t_G = AgglomerativeClustering(n_clusters=min(n_groups, len(creators) - 1), metric="precomputed", linkage="average").fit_predict(D)
    out["comparison"].append({"genre": genre, "titles": tag, "n_creators": len(creators), "n_groups": n_groups,
                              "style_k": k_s, "style_silhouette": round(sil_s, 3), "topic_k": k_t, "topic_silhouette": round(sil_t, 3),
                              "ari_style_vs_group": round(adjusted_rand_score(group_lab, lab_s), 3),
                              "ari_topic_vs_group": round(adjusted_rand_score(group_lab, lab_t), 3),
                              "ari_style_vs_topic": round(adjusted_rand_score(lab_s, lab_t), 3),
                              "ari_style_vs_group_k_groups": round(adjusted_rand_score(group_lab, lab_s_G), 3),
                              "ari_topic_vs_group_k_groups": round(adjusted_rand_score(group_lab, lab_t_G), 3),
                              "ari_style_vs_topic_k_groups": round(adjusted_rand_score(lab_s_G, lab_t_G), 3),
                              "style_silhouette_by_k": json.dumps(scores_s), "topic_silhouette_by_k": json.dumps(scores_t)})
    for c, ls, lt, gl in zip(creators, lab_s, lab_t, group_lab):
        out["style_clusters"].append({"genre": genre, "titles": tag, "creator": c, "group": gl, "style_cluster": int(ls), "style_cluster_k_groups": int(lab_s_G[creators.index(c)])})
        out["topic_clusters"].append({"genre": genre, "titles": tag, "creator": c, "group": gl, "topic_cluster": int(lt), "topic_cluster_k_groups": int(lab_t_G[creators.index(c)])})
    # style cohesion per channel group (z-space euclidean)
    from scipy.spatial.distance import cdist
    DS = cdist(Z.to_numpy(), Z.to_numpy())
    for group in sorted(set(group_lab)):
        idx = np.where(group_lab == group)[0]
        oth = np.where(group_lab != group)[0]
        if len(idx) < 2:
            continue
        within = DS[np.ix_(idx, idx)][np.triu_indices(len(idx), 1)].mean()
        between = DS[np.ix_(idx, oth)].mean()
        out["cohesion"].append({"genre": genre, "titles": tag, "group": group, "n_creators": len(idx), "within_group_distance": round(float(within), 3),
                                "between_group_distance": round(float(between), 3), "cohesion_ratio": round(float(within / between), 3)})
    # disagreements: group-mates split across style clusters; style-mates across groups
    df = pd.DataFrame({"creator": creators, "group": group_lab, "style_cluster": lab_s, "topic_cluster": lab_t})
    for group, g in df.groupby("group"):
        if len(g) >= 3:
            vc = g["style_cluster"].value_counts()
            out["disagree"].append({"genre": genre, "titles": tag, "kind": "channel group split across style clusters", "group": group, "n_creators": len(g),
                                    "n_style_clusters": int(len(vc)), "largest_cluster_share": round(float(vc.iloc[0] / len(g)), 3),
                                    "members": "; ".join(f"{r.creator} (S{r.style_cluster})" for r in g.sort_values("style_cluster").itertuples())})
    for cl, g in df.groupby("style_cluster"):
        if g["group"].nunique() >= 2:
            out["disagree"].append({"genre": genre, "titles": tag, "kind": "style cluster spanning channel groups", "group": f"S{cl}", "n_creators": len(g),
                                    "n_style_clusters": int(g["group"].nunique()), "largest_cluster_share": round(float(g["group"].value_counts().iloc[0] / len(g)), 3),
                                    "members": "; ".join(f"{r.creator} ({r.group})" for r in g.sort_values("group").itertuples())})
    # neighbours
    for i, c in enumerate(creators):
        ds = DS[i].copy(); ds[i] = np.inf
        nn = np.argsort(ds)[:5]
        out["nn_style"].append({"genre": genre, "titles": tag, "creator": c, "group": group_lab[i],
                                **{f"nn{j + 1}": creators[n] for j, n in enumerate(nn)}, **{f"nn{j + 1}_group": group_lab[n] for j, n in enumerate(nn)},
                                **{f"nn{j + 1}_dist": round(float(ds[n]), 3) for j, n in enumerate(nn)}})
        dt = D[i].copy(); dt[i] = np.inf
        nn = np.argsort(dt)[:5]
        out["nn_topic"].append({"genre": genre, "titles": tag, "creator": c, "group": group_lab[i],
                                **{f"nn{j + 1}": creators[n] for j, n in enumerate(nn)}, **{f"nn{j + 1}_group": group_lab[n] for j, n in enumerate(nn)},
                                **{f"nn{j + 1}_js": round(float(dt[n]), 3) for j, n in enumerate(nn)}})
    # maps
    if tag == "all":
        pca = PCA(n_components=2, random_state=SEED).fit(Z.to_numpy())
        xy = pca.transform(Z.to_numpy())
        for i, c in enumerate(creators):
            out["map_style"].append({"genre": genre, "creator": c, "group": group_lab[i], "x": round(float(xy[i, 0]), 4), "y": round(float(xy[i, 1]), 4),
                                     "style_cluster": int(lab_s[i]), "pc1_var": round(float(pca.explained_variance_ratio_[0]), 3), "pc2_var": round(float(pca.explained_variance_ratio_[1]), 3)})
        mds = MDS(n_components=2, dissimilarity="precomputed", random_state=SEED, n_init=4, normalized_stress="auto")
        xy = mds.fit_transform(D)
        for i, c in enumerate(creators):
            out["map_topic"].append({"genre": genre, "creator": c, "group": group_lab[i], "x": round(float(xy[i, 0]), 4), "y": round(float(xy[i, 1]), 4), "topic_cluster": int(lab_t[i])})


def run(info: dict) -> None:
    creators_tbl = load_creators()
    prepared = load_prepared()
    org_of = creators_tbl.set_index("creator")["organisation"]
    uniq = prepared[~prepared["is_dup"]].copy()
    uniq["organisation"] = uniq["creator"].map(org_of)
    # cross-posted titles: same organisation, another creator, same key
    key_cre = uniq.groupby(["organisation", "title_key_raw"])["creator"].nunique()
    uniq["crosspost"] = uniq.set_index(["organisation", "title_key_raw"]).index.map(key_cre).to_numpy() > 1
    info["crossposted_titles"] = int(uniq["crosspost"].sum())
    dt = pd.read_parquet(DIMENSIONS_TITLE)
    fcols = [c for c in dt.columns if c.startswith("F") and c[1:].isdigit()]
    dt = dt.merge(uniq[["row_id", "crosspost"]], on="row_id")
    dt = dt[~dt["crosspost"]]
    topics = pd.read_csv(TOPICS_CSV, usecols=["row_id", "topic_id", "political"])
    labels = pd.read_csv(ANALYSIS_DIR / "topic_labels.csv")
    all_topics = sorted(labels["topic_id"])
    out = defaultdict(list)
    for genre in ("videos", "streams"):
        for tag in ("all", "political"):
            sub = dt[(dt["genre"] == genre) & (~dt["low_n"])]
            if tag == "political":
                sub = sub[sub["political"]]
            n_ok = sub.groupby("creator").size()
            sub = sub[sub["creator"].isin(n_ok[n_ok >= LOW_N].index)]
            vec = sub.groupby("creator")[[f + "_resid" for f in fcols]].mean()
            vec.columns = fcols
            tmix = sub.groupby(["creator", "topic_id"]).size().unstack(fill_value=0).reindex(columns=all_topics, fill_value=0)
            cluster_block(vec, tmix, creators_tbl, tag, genre, out)
    for name in ("style_clusters", "topic_clusters", "comparison", "cohesion", "disagree", "nn_style", "nn_topic", "map_style", "map_topic"):
        fname = {"comparison": "cluster_comparison", "cohesion": "group_style_cohesion", "disagree": "disagreements_group_style",
                 "nn_style": "neighbours_style", "nn_topic": "neighbours_topic"}.get(name, name)
        pd.DataFrame(out[name]).to_csv(ANALYSIS_DIR / f"{fname}.csv", index=False)
    info["cluster_runs"] = len(out["comparison"])

    # organisation-level style (title-weighted mean of members' controlled scores, non-clipper members)
    dims = pd.read_csv(DIMENSIONS_CSV)
    d2 = dims[~dims["clipper"].astype(str).str.lower().eq("true")] if "clipper" in dims else dims
    rows = []
    for (org, genre), g in d2.groupby(["organisation", "genre"]):
        w = g["n_unique"].to_numpy(dtype=float)
        rec = {"organisation": org, "genre": genre, "n_channels": len(g), "channels": "; ".join(g["creator"]), "n_unique": int(w.sum())}
        for f in fcols:
            rec[f + "_controlled"] = float(np.average(g[f + "_controlled"], weights=w))
            rec[f + "_raw"] = float(np.average(g[f + "_raw"], weights=w))
        rows.append(rec)
    pd.DataFrame(rows).to_csv(ANALYSIS_DIR / "org_style.csv", index=False)

    # ---- who gets named (creator-balanced: in_balanced unique titles) ----
    ann = pd.read_parquet(ANNOTATIONS, columns=["title_norm", "ents"]).set_index("title_norm")["ents"]
    fm = pd.read_parquet(FORMATS_PARQUET, columns=["row_id", "outrage", "p_outrage"])
    bal = uniq[uniq["in_balanced"] & ~uniq["low_n"]].merge(fm, on="row_id").merge(creators_tbl[["creator", "group"]], on="creator")
    bal["ents"] = bal["title_norm"].map(ann)
    person_count, org_count = Counter(), Counter()
    person_forms, org_forms = defaultdict(Counter), defaultdict(Counter)
    person_rows, org_rows = defaultdict(list), defaultdict(list)
    for r in bal.itertuples():
        if not r.ents:
            continue
        seen_p, seen_o = set(), set()
        for item in r.ents.split("\x1f"):
            text, _, label = item.partition("\x1e")
            norm = normalise_entity(text)
            if len(norm) < 2:
                continue
            if label == "PERSON":
                k = surname_key(norm)
                if len(k) < 3 or k in seen_p:
                    continue
                seen_p.add(k); person_count[k] += 1; person_forms[k][norm] += 1; person_rows[k].append(r.Index)
            elif label == "ORG":
                k = norm.lower()
                if k in seen_o:
                    continue
                seen_o.add(k); org_count[k] += 1; org_forms[k][norm] += 1; org_rows[k].append(r.Index)
    overall_outrage = float(bal["outrage"].mean())
    group_n = bal.groupby("group").size()
    ent_rows = []
    for kind, counts, forms, rows_of in (("person", person_count, person_forms, person_rows), ("organisation", org_count, org_forms, org_rows)):
        for k, n in counts.most_common(25):
            sub = bal.loc[rows_of[k]]
            by_group = (sub.groupby("group").size() / group_n).dropna().sort_values(ascending=False)
            top_groups = "; ".join(f"{g_} ({v:.1%})" for g_, v in by_group.items())
            ent_rows.append({"kind": kind, "entity": forms[k].most_common(1)[0][0], "key": k, "n_titles_balanced": n,
                             "share_of_balanced_titles": round(n / len(bal), 4), "n_creators": sub["creator"].nunique(),
                             "share_by_group": top_groups, "outrage_share": round(float(sub["outrage"].mean()), 3),
                             "overall_outrage_share": round(overall_outrage, 3), "outrage_ratio": round(float(sub["outrage"].mean() / overall_outrage), 2) if overall_outrage else np.nan,
                             "surface_forms": "; ".join(f"{f} ({c})" for f, c in forms[k].most_common(4))})
    pd.DataFrame(ent_rows).to_csv(ANALYSIS_DIR / "entities_top.csv", index=False)

    # ---- convergent formulas ----
    group_of = creators_tbl.set_index("creator")["group"]
    u2 = uniq[["creator", "genre", "title_raw", "title_norm", "title_key_raw", "organisation"]].copy()
    u2["group"] = u2["creator"].map(group_of)
    grp = u2.groupby("title_key_raw")
    shared = grp.agg(n_creators=("creator", "nunique"), n_organisations=("organisation", "nunique"), n_titles=("creator", "size"),
                     example=("title_raw", "first"), creators=("creator", lambda s: "; ".join(sorted(set(s)))),
                     groups=("group", lambda s: "; ".join(sorted(set(s)))), n_groups=("group", "nunique")).reset_index()
    shared = shared[shared["n_creators"] >= 2].sort_values(["n_creators", "n_titles"], ascending=False)
    shared["within_group"] = shared["n_groups"] == 1
    shared["same_organisation_only"] = shared["n_organisations"] == 1     # e.g. TYT / Damage Report cross-posts
    shared.to_csv(ANALYSIS_DIR / "shared_titles.csv", index=False)
    info["shared_titles_any"] = int(len(shared))
    conv = shared[~shared["same_organisation_only"]]
    info["shared_titles_cross_org"] = int(len(conv)); info["shared_titles_within_group_share"] = round(float(conv["within_group"].mean()), 3)
    ann_tok = pd.read_parquet(ANNOTATIONS, columns=["title_norm", "tokens", "ent_iob"]).set_index("title_norm")
    masked = {}
    for t, row in ann_tok.iterrows():
        toks = row["tokens"].split("\x1f") if row["tokens"] else []
        m = mask_tokens(toks, row["ent_iob"].split() if row["ent_iob"] else [])
        masked[t] = " ".join(x for x in m if re.search(r"\w|<ENT>|#", x))
    u2["template"] = u2["title_norm"].map(masked)
    u2 = u2[u2["template"].str.count(" ") >= 2]
    _skip = set(STOPWORDS) | {"<ENT>", "#"}
    u2 = u2[u2["template"].map(lambda t: any(w not in _skip for w in t.split()))]   # at least one content word
    tg = u2.groupby("template").agg(n_creators=("creator", "nunique"), n_titles=("creator", "size"), example=("title_raw", "first"),
                                   creators=("creator", lambda s: "; ".join(sorted(set(s))[:12])), groups=("group", lambda s: "; ".join(sorted(set(s)))),
                                   n_groups=("group", "nunique")).reset_index()
    tg = tg.merge(u2.groupby("template")["organisation"].nunique().rename("n_organisations"), on="template")
    tg = tg[(tg["n_organisations"] >= 2) & tg["template"].str.contains("<ENT>|#")].sort_values(["n_creators", "n_titles"], ascending=False)
    tg["within_group"] = tg["n_groups"] == 1
    tg.head(500).to_csv(ANALYSIS_DIR / "shared_templates.csv", index=False)
    info["shared_templates"] = int(len(tg)); info["shared_templates_within_group_share"] = round(float(tg["within_group"].mean()), 3) if len(tg) else None


def main(argv: Optional[Sequence[str]] = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.parse_args(argv)
    with stage_timer("stage4_landscape") as info:
        run(info)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
