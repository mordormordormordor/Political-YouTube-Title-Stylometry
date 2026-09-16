"""Stage 1 - embedding-based topic model (BERTopic: sentence embeddings + UMAP +
HDBSCAN + class-based TF-IDF) fitted on a creator-stratified ~100k sample, then
every title assigned to its nearest topic centroid.

Reads titles_prepared.parquet, cache/embeddings.npy (Stage 1a), annotations.parquet
(Stage 0c, for the entities per topic) and lanes.csv. Writes, under
data/titles/analysis/:

    topics.csv                row_id, video_id, creator, genre, topic_id, topic_sim,
                              weak_assignment (all 309,596 rows; verbatim repeats get
                              the topic of their unique title)
    topic_labels.csv          topic_id, label (LLM), political, category, top_terms,
                              n_fit, n_unique_all, example_1..3, top_persons, top_orgs
    creator_topic_mix.csv     creator x genre x topic share (unique titles)
    topic_by_lane.csv         lane x genre x topic: mean of creator shares (+ raw pooled)
    topic_timeline.csv        month x topic: creator-balanced share and raw count
    topic_spikes.csv          per month, the topics that spike most vs. their own
                              mean, with the entities and example titles of that month
    creator_political_share.csv
    cache/topic_centroids.npy, cache/topic_fit_sample.parquet

Fit sample: from the creator-balanced subset, per creator x genre capped so that
the total is ~100,000 (cap found by bisection, seed 20260914). UMAP(15 neighbours,
5 dims, cosine, min_dist 0) -> HDBSCAN(min_cluster_size 80, min_samples 15, eom).
If HDBSCAN yields more than --max-topics topics they are merged to that number by
c-TF-IDF similarity. Outliers and all non-fit titles are assigned to the nearest
centroid (cosine); an assignment is 'weak' when its similarity is below the 10th
percentile of the similarities of HDBSCAN's own members.

CLI:
    python -m pipeline_titles.topics
    python -m pipeline_titles.topics --fit-size 100000 --min-cluster-size 80 --max-topics 250
    python -m pipeline_titles.topics --label-only        # re-run only the LLM labelling
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from collections import Counter, defaultdict
from typing import Optional, Sequence

import numpy as np
import pandas as pd

from pipeline_titles.common import (
    ANALYSIS_DIR, ANNOTATIONS, CACHE_DIR, LOW_N, MONTHS, SEED, STOPWORDS, TOPIC_LABELS_CSV, TOPICS_CSV,
    balanced_mask, load_lanes, load_prepared, stage_timer, utc_now,
)
from pipeline_titles.embed import load_embeddings

FIT_SIZE = 100_000
MIN_CLUSTER_SIZE = 80
MIN_SAMPLES = 15
MAX_TOPICS = 250
LABEL_MODEL = "qwen3:14b"
CENTROIDS_NPY = CACHE_DIR / "topic_centroids.npy"
FIT_SAMPLE_PARQUET = CACHE_DIR / "topic_fit_sample.parquet"
TOPIC_CATEGORIES = ["us_politics", "world_politics", "war_conflict", "crime_justice", "economy_policy",
                    "media_culture_war", "tech_business", "markets_finance", "sport", "entertainment",
                    "weather_disaster", "health_science", "lifestyle", "religion", "other"]
POLITICAL_CATEGORIES = {"us_politics", "world_politics", "war_conflict", "crime_justice", "economy_policy",
                        "media_culture_war"}

LABEL_PROMPT = """You are labelling a topic found by clustering YouTube video titles from political-media channels.
Top terms (by class TF-IDF): {terms}
Example titles:
{examples}

Answer with one JSON object and nothing else:
{{"label": "<a short topic name, at most 6 words>", "political": true or false, "category": "<one of: {categories}>"}}
'political' is true when the topic concerns politics, government, elections, war, policy, courts, political figures or the culture war; false for sport, entertainment, weather, lifestyle, business/markets-only, science/health and similar."""


# --------------------------------------------------------------------------- #
# Pure helpers
# --------------------------------------------------------------------------- #
def cap_for_target(sizes: Sequence[int], target: int) -> int:
    """Smallest per-group cap such that sum(min(n, cap)) >= target (or the max size)."""
    sizes = np.asarray(sizes)
    lo, hi = 1, int(sizes.max())
    if np.minimum(sizes, hi).sum() <= target:
        return hi
    while lo < hi:
        mid = (lo + hi) // 2
        if np.minimum(sizes, mid).sum() >= target:
            hi = mid
        else:
            lo = mid + 1
    return lo


def nearest_centroid(emb: np.ndarray, centroids: np.ndarray, chunk: int = 20000) -> tuple[np.ndarray, np.ndarray]:
    """(argmax cosine, max cosine) of L2-normalised rows against L2-normalised centroids."""
    best, sim = np.empty(len(emb), dtype=np.int32), np.empty(len(emb), dtype=np.float32)
    for i in range(0, len(emb), chunk):
        s = emb[i:i + chunk] @ centroids.T
        best[i:i + chunk] = s.argmax(axis=1)
        sim[i:i + chunk] = s.max(axis=1)
    return best, sim


def normalise_entity(text: str) -> str:
    t = re.sub(r"[’']s$", "", text.strip().strip("\"'“”‘’.,:;!?"))
    t = re.sub(r"^(the|president|sen\.|sen|rep\.|rep|gov\.|gov|dr\.|dr|mr\.|mr|ms\.|ms|judge)\s+", "", t, flags=re.I)
    return re.sub(r"\s+", " ", t).strip()


def parse_label_json(text: str) -> Optional[dict]:
    m = re.search(r"\{.*\}", text, flags=re.S)
    if not m:
        return None
    try:
        obj = json.loads(m.group(0))
    except json.JSONDecodeError:
        return None
    if not isinstance(obj, dict) or "label" not in obj:
        return None
    cat = str(obj.get("category", "other")).strip().lower().replace(" ", "_")
    if cat not in TOPIC_CATEGORIES:
        cat = "other"
    pol = obj.get("political")
    if isinstance(pol, str):
        pol = pol.strip().lower() in ("true", "yes", "1")
    return {"label": str(obj["label"]).strip()[:80], "political": bool(pol), "category": cat}


# --------------------------------------------------------------------------- #
def llm_label(terms: list[str], examples: list[str], model: str, info: dict) -> dict:
    from pipeline_titles.llm_rate import ollama_generate
    prompt = LABEL_PROMPT.format(terms=", ".join(terms), examples="\n".join(f"- {e}" for e in examples),
                                 categories=", ".join(TOPIC_CATEGORIES))
    key = hashlib.sha1(f"{model}\n0\n{prompt}".encode()).hexdigest()
    path = CACHE_DIR / "llm_topics" / f"{key}.json"
    if path.exists():
        rec = json.loads(path.read_text(encoding="utf-8"))
    else:
        r = ollama_generate(model, prompt, 0.0, num_predict=200)
        rec = {"model": model, "prompt": prompt, "response": r.get("response", ""), "rated_at": utc_now(),
               "prompt_eval_count": r.get("prompt_eval_count"), "eval_count": r.get("eval_count")}
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(rec, ensure_ascii=False), encoding="utf-8")
        info["label_calls"] = info.get("label_calls", 0) + 1
        info["label_output_tokens"] = info.get("label_output_tokens", 0) + (rec["eval_count"] or 0)
    parsed = parse_label_json(rec["response"])
    if parsed is None:
        parsed = {"label": " / ".join(terms[:3]), "political": True, "category": "other"}
        info["label_parse_failures"] = info.get("label_parse_failures", 0) + 1
    return parsed


def fit_topic_model(docs: list[str], emb: np.ndarray, min_cluster_size: int, min_samples: int,
                    max_topics: int, seed: int):
    from bertopic import BERTopic
    from bertopic.vectorizers import ClassTfidfTransformer
    from hdbscan import HDBSCAN
    from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS, CountVectorizer
    from umap import UMAP

    umap_model = UMAP(n_neighbors=15, n_components=5, min_dist=0.0, metric="cosine", random_state=seed, low_memory=True)
    hdbscan_model = HDBSCAN(min_cluster_size=min_cluster_size, min_samples=min_samples, metric="euclidean",
                            cluster_selection_method="eom", prediction_data=False, core_dist_n_jobs=8)
    vectorizer = CountVectorizer(stop_words=sorted(set(ENGLISH_STOP_WORDS) | set(STOPWORDS)), ngram_range=(1, 2), min_df=5)
    model = BERTopic(embedding_model=None, umap_model=umap_model, hdbscan_model=hdbscan_model,
                     vectorizer_model=vectorizer, ctfidf_model=ClassTfidfTransformer(reduce_frequent_words=True),
                     calculate_probabilities=False, verbose=True)
    topics, _ = model.fit_transform(docs, embeddings=emb)
    n_topics = len(set(topics)) - (1 if -1 in topics else 0)
    print(f"HDBSCAN found {n_topics} topics; outliers {np.mean(np.array(topics) == -1):.1%}", flush=True)
    if n_topics > max_topics:
        model.reduce_topics(docs, nr_topics=max_topics)
        topics = list(model.topics_)
        print(f"reduced to {len(set(topics)) - 1} topics", flush=True)
    return model, np.array(topics)


def run(fit_size: int, min_cluster_size: int, min_samples: int, max_topics: int, model_name: str,
        label_only: bool, info: dict) -> None:
    prepared = load_prepared()
    lanes = load_lanes()[["creator", "lane", "organisation", "clipper"]]
    uniq = prepared[~prepared["is_dup"]].copy()
    emb_all, emb_index = load_embeddings()
    uniq["emb_row"] = uniq["title_norm"].map(emb_index).astype(int)

    if not label_only:
        # --- fit sample ---
        bal = uniq[uniq["in_balanced"]]
        sizes = bal.groupby(["creator", "genre"]).size()
        cap = cap_for_target(sizes.to_numpy(), fit_size)
        fit_mask = balanced_mask(bal, cap=cap, seed=SEED)
        fit = bal[fit_mask].sort_values("row_id")
        print(f"fit sample: {len(fit)} titles (cap {cap} per creator x genre, {fit.groupby(['creator', 'genre']).ngroups} groups)", flush=True)
        docs = fit["title_norm"].tolist()
        emb_fit = emb_all[fit["emb_row"].to_numpy()]
        model, hdb_topics = fit_topic_model(docs, emb_fit, min_cluster_size, min_samples, max_topics, SEED)
        topic_ids = sorted(t for t in set(hdb_topics) if t != -1)
        # centroids = mean embedding of HDBSCAN members, L2-normalised
        centroids = np.vstack([emb_fit[hdb_topics == t].mean(axis=0) for t in topic_ids])
        centroids /= np.linalg.norm(centroids, axis=1, keepdims=True)
        np.save(CENTROIDS_NPY, centroids.astype(np.float32))
        terms = {t: [w for w, _ in model.get_topic(t)[:10]] for t in topic_ids}
        fit_out = fit[["row_id", "creator", "genre", "title_norm"]].copy()
        fit_out["hdbscan_topic"] = hdb_topics
        fit_out.to_parquet(FIT_SAMPLE_PARQUET, index=False)
        (CACHE_DIR / "topic_terms.json").write_text(json.dumps({int(t): v for t, v in terms.items()}, indent=1))
        info.update(fit_n=len(fit), fit_cap=cap, hdbscan_topics=len(topic_ids),
                    outlier_share=round(float(np.mean(hdb_topics == -1)), 4))
    else:
        centroids = np.load(CENTROIDS_NPY)
        fit_out = pd.read_parquet(FIT_SAMPLE_PARQUET)
        terms = {int(k): v for k, v in json.loads((CACHE_DIR / "topic_terms.json").read_text()).items()}
        topic_ids = sorted(terms)
        hdb_topics = fit_out["hdbscan_topic"].to_numpy()

    # --- assign every unique title to its nearest centroid ---
    idx_of = {t: i for i, t in enumerate(topic_ids)}
    best, sim = nearest_centroid(emb_all, centroids)
    uniq["topic_idx"] = best[uniq["emb_row"].to_numpy()]
    uniq["topic_sim"] = sim[uniq["emb_row"].to_numpy()]
    uniq["topic_id"] = uniq["topic_idx"].map(lambda i: topic_ids[i])
    # weak threshold: 10th percentile of members' similarity to their own HDBSCAN centroid
    fit_rows = uniq.set_index("row_id").loc[fit_out["row_id"]]
    member = hdb_topics != -1
    member_sims = np.array([
        float(emb_all[r] @ centroids[idx_of[t]]) for r, t in zip(fit_rows["emb_row"].to_numpy()[member], hdb_topics[member])
    ])
    weak_thr = float(np.percentile(member_sims, 10))
    uniq["weak_assignment"] = uniq["topic_sim"] < weak_thr
    agree = float(np.mean(fit_rows["topic_id"].to_numpy()[member] == hdb_topics[member]))
    print(f"nearest-centroid vs HDBSCAN label agreement on fit members: {agree:.3f}; weak threshold {weak_thr:.3f}; "
          f"weak share {uniq['weak_assignment'].mean():.1%}", flush=True)
    info.update(centroid_hdbscan_agreement=round(agree, 4), weak_threshold=round(weak_thr, 4),
                weak_share=round(float(uniq["weak_assignment"].mean()), 4), n_topics=len(topic_ids))

    # propagate to duplicates
    key_topic = uniq.set_index(["creator", "genre", "title_norm"])[["topic_id", "topic_sim", "weak_assignment"]]
    key_topic = key_topic[~key_topic.index.duplicated()]
    all_rows = prepared[["row_id", "video_id", "creator", "genre", "month", "title_norm", "is_dup", "in_balanced"]].copy()
    all_rows = all_rows.join(key_topic, on=["creator", "genre", "title_norm"])
    all_rows["topic_id"] = all_rows["topic_id"].astype(int)

    # --- topic labels: terms, examples, entities, LLM label ---
    ann = pd.read_parquet(ANNOTATIONS, columns=["title_norm", "ents"]).set_index("title_norm")["ents"]
    uniq["ents"] = uniq["title_norm"].map(ann)
    rows = []
    for t in topic_ids:
        members = uniq[uniq["topic_id"] == t]
        top = members.nlargest(60, "topic_sim")
        # examples from distinct creators, closest to the centroid
        ex, seen = [], set()
        for r in top.itertuples():
            if r.creator not in seen:
                ex.append(r.title_norm); seen.add(r.creator)
            if len(ex) >= 8:
                break
        persons, orgs = Counter(), Counter()
        for e in members["ents"].dropna():
            if not e:
                continue
            for item in e.split("\x1f"):
                text, _, label = item.partition("\x1e")
                norm = normalise_entity(text)
                if len(norm) < 2:
                    continue
                if label == "PERSON":
                    persons[norm] += 1
                elif label == "ORG":
                    orgs[norm] += 1
        lab = llm_label(terms[t], ex, model_name, info)
        rows.append({
            "topic_id": t, "label": lab["label"], "political": lab["political"], "category": lab["category"],
            "top_terms": ", ".join(terms[t]), "n_fit": int((hdb_topics == t).sum()), "n_unique_all": len(members),
            "n_creators": members["creator"].nunique(),
            "example_1": ex[0] if len(ex) > 0 else "", "example_2": ex[1] if len(ex) > 1 else "", "example_3": ex[2] if len(ex) > 2 else "",
            "top_persons": "; ".join(f"{k} ({v})" for k, v in persons.most_common(8)),
            "top_orgs": "; ".join(f"{k} ({v})" for k, v in orgs.most_common(8)),
        })
        if len(rows) % 25 == 0:
            print(f"  labelled {len(rows)}/{len(topic_ids)} topics", flush=True)
    labels = pd.DataFrame(rows)
    labels.to_csv(TOPIC_LABELS_CSV, index=False)
    political = set(labels.loc[labels["political"], "topic_id"])

    all_rows["political"] = all_rows["topic_id"].isin(political)
    all_rows[["row_id", "video_id", "creator", "genre", "topic_id", "topic_sim", "weak_assignment", "political"]] \
        .to_csv(TOPICS_CSV, index=False)

    # --- per-creator topic mix (unique titles), political share ---
    u = all_rows[~all_rows["is_dup"]]
    mix = u.groupby(["creator", "genre", "topic_id"]).size().rename("n").reset_index()
    mix["share"] = mix["n"] / mix.groupby(["creator", "genre"])["n"].transform("sum")
    mix = mix.merge(labels[["topic_id", "label", "political"]], on="topic_id")
    mix.to_csv(ANALYSIS_DIR / "creator_topic_mix.csv.gz", index=False)
    pol = u.groupby(["creator", "genre"]).agg(n_unique=("row_id", "size"), political_share=("political", "mean"),
                                              weak_share=("weak_assignment", "mean")).reset_index()
    pol.merge(lanes, on="creator", how="left").to_csv(ANALYSIS_DIR / "creator_political_share.csv", index=False)

    # --- topic share by lane: mean of creator shares (creator-level), raw pooled beside it ---
    ml = mix.merge(lanes, on="creator", how="left")
    ml = ml[ml["n"].groupby([ml["creator"], ml["genre"]]).transform("sum") >= LOW_N]
    full = (ml.groupby(["lane", "genre", "creator"])["share"].sum().index.to_frame(index=False))
    grid = full.merge(labels[["topic_id"]], how="cross")
    grid = grid.merge(ml[["lane", "genre", "creator", "topic_id", "share", "n"]], on=["lane", "genre", "creator", "topic_id"], how="left").fillna({"share": 0.0, "n": 0})
    by_lane = grid.groupby(["lane", "genre", "topic_id"]).agg(mean_creator_share=("share", "mean"), n_creators=("creator", "nunique"), raw_n=("n", "sum")).reset_index()
    by_lane["raw_pooled_share"] = by_lane["raw_n"] / by_lane.groupby(["lane", "genre"])["raw_n"].transform("sum")
    by_lane = by_lane.merge(labels[["topic_id", "label", "political"]], on="topic_id")
    by_lane.sort_values(["lane", "genre", "mean_creator_share"], ascending=[True, True, False]).to_csv(ANALYSIS_DIR / "topic_by_lane.csv", index=False)

    # --- monthly timeline (creator-balanced) and spikes ---
    um = u.groupby(["creator", "genre", "month"]).size().rename("n_month").reset_index()
    um = um[um["n_month"] >= 5]
    cm = u.groupby(["creator", "genre", "month", "topic_id"]).size().rename("n").reset_index().merge(um, on=["creator", "genre", "month"])
    cm["share"] = cm["n"] / cm["n_month"]
    grid = um[["creator", "genre", "month"]].merge(labels[["topic_id"]], how="cross")
    grid = grid.merge(cm[["creator", "genre", "month", "topic_id", "share", "n"]], on=["creator", "genre", "month", "topic_id"], how="left").fillna({"share": 0.0, "n": 0})
    tl = grid.groupby(["month", "topic_id"]).agg(balanced_share=("share", "mean"), raw_n=("n", "sum"), n_groups=("creator", "size")).reset_index()
    tl["raw_share"] = tl["raw_n"] / tl.groupby("month")["raw_n"].transform("sum")
    tl = tl.merge(labels[["topic_id", "label", "political"]], on="topic_id")
    tl.to_csv(ANALYSIS_DIR / "topic_timeline.csv", index=False)
    piv = tl.pivot(index="topic_id", columns="month", values="balanced_share").reindex(columns=MONTHS)
    z = piv.sub(piv.mean(axis=1), axis=0).div(piv.std(axis=1).replace(0, np.nan), axis=0)
    jump = piv.sub(piv.mean(axis=1), axis=0)
    spikes = []
    for m in MONTHS:
        cand = z[m].dropna()
        cand = cand[piv.loc[cand.index].mean(axis=1) >= 0.001]
        for t in cand.nlargest(6).index:
            mem = u[(u["topic_id"] == t) & (u["month"] == m)]
            ents = Counter()
            for e in uniq.loc[uniq["row_id"].isin(mem["row_id"]), "ents"].dropna():
                for item in (e.split("\x1f") if e else []):
                    text, _, label = item.partition("\x1e")
                    if label in ("PERSON", "ORG", "GPE"):
                        ents[normalise_entity(text)] += 1
            ex = mem.nlargest(40, "topic_sim").drop_duplicates("creator").head(3)["title_norm"].tolist()
            spikes.append({"month": m, "topic_id": t, "label": labels.set_index("topic_id").loc[t, "label"],
                           "z_vs_own_months": round(float(z.loc[t, m]), 2), "share_month": round(float(piv.loc[t, m]), 4),
                           "share_mean_all_months": round(float(piv.loc[t].mean()), 4), "jump": round(float(jump.loc[t, m]), 4),
                           "n_titles_month": int(len(mem)), "top_entities": "; ".join(f"{k} ({v})" for k, v in ents.most_common(5)),
                           "example_1": ex[0] if len(ex) > 0 else "", "example_2": ex[1] if len(ex) > 1 else "", "example_3": ex[2] if len(ex) > 2 else ""})
    pd.DataFrame(spikes).to_csv(ANALYSIS_DIR / "topic_spikes.csv", index=False)
    info["political_topics"] = int(labels["political"].sum())
    info["political_share_of_unique_titles"] = round(float(u["political"].mean()), 4)


def main(argv: Optional[Sequence[str]] = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--fit-size", type=int, default=FIT_SIZE)
    ap.add_argument("--min-cluster-size", type=int, default=MIN_CLUSTER_SIZE)
    ap.add_argument("--min-samples", type=int, default=MIN_SAMPLES)
    ap.add_argument("--max-topics", type=int, default=MAX_TOPICS)
    ap.add_argument("--label-model", default=LABEL_MODEL)
    ap.add_argument("--label-only", action="store_true", help="skip the fit; re-assign and re-label from the cached centroids")
    a = ap.parse_args(argv)
    with stage_timer("stage1_topics", fit_size=a.fit_size, min_cluster_size=a.min_cluster_size, min_samples=a.min_samples,
                     max_topics=a.max_topics, label_model=a.label_model, api_cost_usd=0.0) as info:
        run(a.fit_size, a.min_cluster_size, a.min_samples, a.max_topics, a.label_model, a.label_only, info)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
