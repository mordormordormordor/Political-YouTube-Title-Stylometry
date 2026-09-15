"""Stage 7 - political leaning from titles alone, judged by two models.

A creator-balanced sample (N_PER_CREATOR unique edited-upload titles per creator,
topped up from live VODs when a creator has fewer; seed 20260914) is labelled
left / right / neither by two local models of different families (Qwen3-14B and
Gemma-3-12B via Ollama, temperature 0, batches of 20, every response cached). The
label is the viewpoint the TITLE'S OWN WORDING signals, not the subject.

Outputs (data/titles/analysis/):
    leaning_labels.csv          one row per sampled title with both labels
    leaning_agreement.json      per-title agreement between the models (kappa, confusion)
    leaning_by_creator.csv      per creator: label shares and a score (right - left) / n
                                for each model, the consensus score (titles both models
                                label the same), and the side it implies
    leaning_lane_validation.csv how well each model's creator score separates the
                                left-commentary and right-commentary lanes (AUC, accuracy),
                                plus the creators whose title-leaning contradicts their lane
    leaning_by_lane.csv         lane means of the scores and of the 'neither' share
    leaning_words.csv           the words each model treats as right vs left: weighted
                                log-odds (alpha0 = 500) and rank-turbulence-divergence
                                contributions (alpha = 1/3), for each model and for the
                                titles both agree on

Backends. `--backend ollama` (default) calls a local model; `--backend claude-code`
runs each batch through the Claude Code CLI in print mode (`claude -p`), which is
covered by a Claude Pro/Max subscription (no API key must be set, or the CLI
switches to API billing). Usage-limit responses are waited out (5, 15, 30, 60 min).
Prompt v2 (`--prompt-version v2`) also asks for the title's TARGET (who is attacked
or featured), which separates "attacks Trump" from "speaks for the left".

Human check. analyse() writes a blind adjudication sheet
(leaning_human_sheet.csv: 200 titles, mostly ones the models disagree on, model
labels hidden) with its key (leaning_human_key.csv). Fill `human_label` and re-run
with `--human-labels data/titles/analysis/leaning_human_sheet.csv` to get every
model's agreement with a human (leaning_human_agreement.csv). That, not the lane
proposal, is the accuracy check.

CLI:
    python -m pipeline_titles.leaning                       # sample, label with both local models, analyse
    python -m pipeline_titles.leaning --backend claude-code --models opus   # add a frontier judge (subscription)
    python -m pipeline_titles.leaning --backend claude-code --models opus --prompt-version v2
    python -m pipeline_titles.leaning --analyse-only [--human-labels <filled sheet>]
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import time
from collections import Counter
from typing import Optional, Sequence

import numpy as np
import pandas as pd

from pipeline_titles.common import ANALYSIS_DIR, CACHE_DIR, SEED, load_lanes, load_prepared, stage_timer, utc_now
from pipeline_titles.llm_rate import OLLAMA_URL
from pipeline_titles.textstats import rank_turbulence_divergence, vocab_tokens, weighted_log_odds

MODELS = ["qwen3:14b", "gemma3:12b"]
N_PER_CREATOR = 16
BATCH = 20
PROMPT_ID = "leaning-v1"
LABELS = ("left", "right", "neither")
TARGETS = ("trump_administration", "democrats_left", "republicans_right", "media", "foreign", "other", "none")
CLAUDE_BIN = shutil.which("claude") or "/opt/homebrew/bin/claude"
LIMIT_WAITS = (300, 900, 1800, 3600, 3600, 3600)
LABELS_CSV = ANALYSIS_DIR / "leaning_labels.csv"
LLM_CACHE = CACHE_DIR / "llm_leaning"

PROMPT = """You are classifying YouTube video titles from political-media channels by the political viewpoint the TITLE ITSELF signals.
Labels:
- left = the framing, word choice or target of criticism signals a left-leaning / progressive stance.
- right = the framing, word choice or target of criticism signals a right-leaning / conservative stance.
- neither = a neutral news headline, a non-political title, or a political title whose stance cannot be told from its wording.
Judge the wording, not the subject: 'Trump signs order' is neither; 'Trump SLAMS radical left' is right; 'Trump's fascist crackdown' is left.
Output exactly one line per title, in order, as id,label with no other text.

Titles:
{titles}"""

PROMPT_V2 = """You are classifying YouTube video titles from political-media channels. For each title give two fields.
STANCE = the political viewpoint the TITLE'S OWN WORDING signals:
- left = the framing, word choice or target of criticism signals a left-leaning / progressive stance.
- right = signals a right-leaning / conservative stance.
- neither = a neutral news headline, a non-political title, or a political title whose stance cannot be told from its wording.
TARGET = who the title attacks, mocks or centres on: trump_administration | democrats_left | republicans_right | media | foreign | other | none.
Judge the wording, not the subject. A title that attacks Trump is left only if its wording is hostile from the left; a title that attacks Democrats is right only if its wording is hostile from the right; a title that attacks Republicans from the right (a libertarian criticising a Republican) is right with target republicans_right.
Examples: 'Trump signs order' -> neither,none. 'Trump SLAMS radical left' -> right,democrats_left. 'Trump's fascist crackdown on protesters' -> left,trump_administration. 'MAGA caller CAN'T defend ICE shooting' -> left,republicans_right. 'Kash Patel is pathetic' (from a libertarian) -> neither,trump_administration if the wording alone cannot tell.
Output exactly one line per title, in order, as id,stance,target with no other text.

Titles:
{titles}"""
PROMPTS = {"v1": PROMPT, "v2": PROMPT_V2}

_LINE_RE = re.compile(r"^\s*\**(\d+)\**\s*[.)]?\s*[,;:|\t\-]\s*\**([A-Za-z]+)\**(?:\s*[,;:|\t]\s*\**([A-Za-z_]+))?")


def model_col(model: str) -> str:
    return "label_" + re.sub(r"[^A-Za-z0-9]+", "_", model).strip("_")


def parse_labels(text: str, n: int) -> dict[int, str]:
    """{id: 'label'} or {id: 'label|target'} when the line carries a target."""
    out = {}
    for line in text.splitlines():
        m = _LINE_RE.match(line.strip().strip("`"))
        if not m:
            continue
        i, lab = int(m.group(1)), m.group(2).lower()
        tgt = (m.group(3) or "").lower()
        if 1 <= i <= n and i not in out and lab in LABELS:
            out[i] = lab + ("|" + tgt if tgt in TARGETS else "")
    return out


def ollama_generate(model: str, prompt: str, num_predict: int = 400) -> dict:
    import urllib.request
    body = {"model": model, "prompt": prompt, "stream": False, "options": {"temperature": 0.0, "num_predict": num_predict, "num_ctx": 4096, "seed": SEED}}
    if model.startswith("qwen3"):
        body["think"] = False
    req = urllib.request.Request(OLLAMA_URL, data=json.dumps(body).encode(), headers={"Content-Type": "application/json"})
    return json.loads(urllib.request.urlopen(req, timeout=900).read())


def claude_code_generate(model: str, prompt: str, timeout: int = 900) -> dict:
    """One batch through the Claude Code CLI in print mode (subscription billing).
    Returns a dict shaped like the Ollama one; waits out usage-limit replies."""
    env = os.environ.copy()
    for k in ("CLAUDECODE", "CLAUDE_CODE_ENTRYPOINT", "ANTHROPIC_API_KEY"):   # no nesting flags, no API billing
        env.pop(k, None)
    cmd = [CLAUDE_BIN, "-p", prompt, "--output-format", "json", "--model", model, "--max-turns", "1"]
    for attempt, wait in enumerate(LIMIT_WAITS + (0,)):
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, env=env)
        raw = proc.stdout.strip()
        try:
            data = json.loads(raw) if raw.startswith("{") else {}
        except json.JSONDecodeError:
            data = {}
        text = data.get("result", "") if isinstance(data, dict) else ""
        err_text = (text if data.get("is_error") else "") + " " + proc.stderr
        if proc.returncode == 0 and text and not data.get("is_error"):
            usage = data.get("usage", {}) or {}
            return {"response": text, "prompt_eval_count": usage.get("input_tokens"), "eval_count": usage.get("output_tokens"),
                    "cost_usd": data.get("total_cost_usd"), "duration_ms": data.get("duration_ms"), "session_id": data.get("session_id")}
        if "limit" in err_text.lower() and wait:
            print(f"  usage limit reported; waiting {wait // 60} min (attempt {attempt + 1})", flush=True)
            time.sleep(wait)
            continue
        raise RuntimeError(f"claude -p failed (code {proc.returncode}): {err_text.strip()[:400] or raw[:400]}")
    raise RuntimeError("claude -p: usage limit persisted")


def label_batch(titles: Sequence[str], model: str, info: dict, backend: str = "ollama", prompt_version: str = "v1") -> dict[int, str]:
    prompt = PROMPTS[prompt_version].format(titles="\n".join(f"{i + 1}. {t}" for i, t in enumerate(titles)))
    model_key = model if backend == "ollama" else f"claude-code:{model}"
    key = hashlib.sha1(f"{model_key}\n0\n{prompt}".encode()).hexdigest()
    path = LLM_CACHE / f"{key}.json"
    if path.exists():
        rec = json.loads(path.read_text(encoding="utf-8"))
        info["cache_hits"] = info.get("cache_hits", 0) + 1
    else:
        t0 = time.time()
        r = ollama_generate(model, prompt) if backend == "ollama" else claude_code_generate(model, prompt)
        rec = {"model": model_key, "backend": backend, "prompt_version": prompt_version, "prompt": prompt, "response": r.get("response", ""),
               "prompt_eval_count": r.get("prompt_eval_count"), "eval_count": r.get("eval_count"), "cost_usd": r.get("cost_usd"),
               "seconds": round(time.time() - t0, 2), "rated_at": utc_now()}
        LLM_CACHE.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(rec, ensure_ascii=False), encoding="utf-8")
        info["calls"] = info.get("calls", 0) + 1
        info["output_tokens"] = info.get("output_tokens", 0) + (rec["eval_count"] or 0)
        info["llm_seconds"] = round(info.get("llm_seconds", 0) + rec["seconds"], 1)
        if rec.get("cost_usd") is not None:
            info["reported_cost_usd"] = round(info.get("reported_cost_usd", 0) + (rec["cost_usd"] or 0), 4)
    return parse_labels(rec["response"], len(titles))


def label_titles(titles: Sequence[str], model: str, info: dict, backend: str = "ollama", prompt_version: str = "v1") -> list[Optional[str]]:
    results: list[Optional[str]] = [None] * len(titles)
    pending = list(range(len(titles)))
    for size in (BATCH, 5, 1):
        if not pending:
            break
        for start in range(0, len(pending), size):
            idx = pending[start:start + size]
            parsed = label_batch([titles[i] for i in idx], model, info, backend, prompt_version)
            for j, i in enumerate(idx):
                if (j + 1) in parsed:
                    results[i] = parsed[j + 1]
            if size == BATCH and (start // size) % 10 == 0:
                print(f"  [{model}] {sum(r is not None for r in results)}/{len(titles)} labelled, calls {info.get('calls', 0)}, cache hits {info.get('cache_hits', 0)}", flush=True)
        pending = [i for i in pending if results[i] is None]
    return results


def draw_sample(prepared: pd.DataFrame, n_per: int = N_PER_CREATOR, seed: int = SEED) -> pd.DataFrame:
    uniq = prepared[~prepared["is_dup"]]
    rng = np.random.RandomState(seed)
    parts = []
    for creator, g in uniq.groupby("creator", sort=True):
        vids = g[g["genre"] == "videos"]
        pool = vids if len(vids) >= n_per else pd.concat([vids, g[g["genre"] == "streams"]])
        k = min(n_per, len(pool))
        parts.append(pool.iloc[np.sort(rng.choice(len(pool), size=k, replace=False))])
    return pd.concat(parts).sort_values("row_id").reset_index(drop=True)


def analyse(df: pd.DataFrame, cols: list[str], info: dict) -> None:
    from sklearn.metrics import cohen_kappa_score, roc_auc_score
    lanes = load_lanes()[["creator", "lane", "organisation", "clipper"]]
    df = df.copy()
    for c in cols:                                   # 'left|democrats_left' -> label column + target column
        if df[c].astype(str).str.contains(r"\|").any():
            df[c.replace("label_", "target_")] = df[c].str.split("|").str[1]
            df[c] = df[c].str.split("|").str[0]
    ok = df.dropna(subset=cols)
    agree = {"n_labelled_by_all": int(len(ok)), "models": cols, "label_shares": {c: ok[c].value_counts(normalize=True).round(4).to_dict() for c in cols}}
    if len(cols) >= 2:
        a, b = ok[cols[0]], ok[cols[1]]
        agree["kappa"] = round(float(cohen_kappa_score(a, b)), 4)
        agree["exact_agreement"] = round(float((a == b).mean()), 4)
        agree["confusion"] = pd.crosstab(a, b).to_dict()
        agree["kappa_political_only"] = round(float(cohen_kappa_score(a[(a != "neither") & (b != "neither")], b[(a != "neither") & (b != "neither")])), 4) if ((a != "neither") & (b != "neither")).sum() > 10 else None
    (ANALYSIS_DIR / "leaning_agreement.json").write_text(json.dumps(agree, indent=2))
    info.update({k: v for k, v in agree.items() if k in ("kappa", "exact_agreement", "n_labelled_by_all")})

    # per creator
    rows = []
    for creator, g in df.groupby("creator"):
        rec = {"creator": creator, "n_titles": len(g)}
        scores = []
        for c in cols:
            v = g[c].dropna()
            rec[f"{c}_n"] = len(v)
            for l in LABELS:
                rec[f"{c}_{l}"] = float((v == l).mean()) if len(v) else np.nan
            rec[f"{c}_score"] = float(((v == "right").sum() - (v == "left").sum()) / len(v)) if len(v) else np.nan
            scores.append(rec[f"{c}_score"])
        if len(cols) >= 2:
            both = g.dropna(subset=cols[:2])
            cons = both[both[cols[0]] == both[cols[1]]]
            rec["consensus_n"] = len(cons)
            rec["consensus_score"] = float(((cons[cols[0]] == "right").sum() - (cons[cols[0]] == "left").sum()) / len(cons)) if len(cons) else np.nan
            rec["consensus_neither"] = float((cons[cols[0]] == "neither").mean()) if len(cons) else np.nan
        rec["mean_score"] = float(np.nanmean(scores))
        rec["implied_side"] = "right" if rec["mean_score"] > 0.05 else ("left" if rec["mean_score"] < -0.05 else "neither / unclear")
        rows.append(rec)
    bc = pd.DataFrame(rows).merge(lanes, on="creator", how="left").sort_values("mean_score")
    bc.to_csv(ANALYSIS_DIR / "leaning_by_creator.csv", index=False)

    # validation against the two commentary lanes
    val_rows, mis = [], []
    two = bc[bc["lane"].isin(["left_commentary", "right_commentary"])]
    y = (two["lane"] == "right_commentary").astype(int)
    for c in [f"{c}_score" for c in cols] + (["consensus_score", "mean_score"] if len(cols) >= 2 else ["mean_score"]):
        s = two[c]
        m = s.notna()
        auc = float(roc_auc_score(y[m], s[m])) if y[m].nunique() == 2 else np.nan
        nz = m & (s != 0)
        acc = float(((s[nz] > 0).astype(int) == y[nz]).mean()) if nz.sum() else np.nan
        val_rows.append({"score": c, "n_creators": int(m.sum()), "auc_right_vs_left_lane": round(auc, 4), "accuracy_sign_vs_lane": round(acc, 4), "n_nonzero": int(nz.sum()),
                         "mean_score_left_lane": round(float(s[m & (y == 0)].mean()), 4), "mean_score_right_lane": round(float(s[m & (y == 1)].mean()), 4)})
    score_cols = [f"{c}_score" for c in cols] + (["consensus_score", "mean_score"] if len(cols) >= 2 else ["mean_score"])
    for sc in score_cols:
        for r in two.itertuples():
            v = getattr(r, sc)
            if pd.isna(v):
                continue
            side = "right" if v > 0 else ("left" if v < 0 else "tie")
            expected = "right" if r.lane == "right_commentary" else "left"
            if side != expected:
                mis.append({"score": sc, "creator": r.creator, "lane": r.lane, "value": round(float(v), 3), "implied_side": side, "n_titles": r.n_titles, "clipper": r.clipper})
    pd.DataFrame(val_rows).to_csv(ANALYSIS_DIR / "leaning_lane_validation.csv", index=False)
    pd.DataFrame(mis).to_csv(ANALYSIS_DIR / "leaning_lane_contradictions.csv", index=False)
    info["lane_auc"] = {r["score"]: r["auc_right_vs_left_lane"] for r in val_rows}
    # judge of record: the single model whose channel score best separates the two commentary lanes
    per_model = [r for r in val_rows if r["score"].startswith("label_")]
    best = max(per_model, key=lambda r: (r["auc_right_vs_left_lane"] if not np.isnan(r["auc_right_vs_left_lane"]) else -1))
    judge = best["score"]
    bc["judge_of_record"] = judge.replace("_score", "")
    bc["judge_score"] = bc[judge]
    bc["judge_side"] = np.where(bc["judge_score"] > 0.05, "right", np.where(bc["judge_score"] < -0.05, "left", "neither / unclear"))
    bc.to_csv(ANALYSIS_DIR / "leaning_by_creator.csv", index=False)
    (ANALYSIS_DIR / "leaning_summary.json").write_text(json.dumps({"judge_of_record": judge.replace("_score", ""), "judge_auc": best["auc_right_vs_left_lane"],
                                                                     "judge_accuracy": best["accuracy_sign_vs_lane"], "per_model": val_rows}, indent=2))
    info["judge_of_record"] = judge

    bl = bc.groupby("lane").agg(n_creators=("creator", "size"), **{f"{c}_score_mean": (f"{c}_score", "mean") for c in cols},
                                **{f"{c}_neither_mean": (f"{c}_neither", "mean") for c in cols}, mean_score=("mean_score", "mean")).reset_index().sort_values("mean_score")
    bl.to_csv(ANALYSIS_DIR / "leaning_by_lane.csv", index=False)

    # words: right vs left per model and for the consensus set
    wrows = []
    sets = {c: (df[df[c] == "right"], df[df[c] == "left"]) for c in cols}
    if len(cols) >= 2:
        both = df.dropna(subset=cols[:2]); both = both[both[cols[0]] == both[cols[1]]]
        sets["consensus"] = (both[both[cols[0]] == "right"], both[both[cols[0]] == "left"])
    for name, (r, l) in sets.items():
        cr, cl = Counter(), Counter()
        for t in r["title_norm"]:
            cr.update(vocab_tokens(t))
        for t in l["title_norm"]:
            cl.update(vocab_tokens(t))
        wlo = weighted_log_odds(cr, cl, alpha0=500.0)
        rtd, contribs = rank_turbulence_divergence(cr, cl, alpha=1 / 3)
        rtd_map = {w: (c, ra, rb) for w, c, ra, rb in contribs}
        for w, (d, z, yr, yl) in wlo.items():
            if yr + yl < 3:
                continue
            c, ra, rb = rtd_map.get(w, (np.nan, np.nan, np.nan))
            wrows.append({"model": name, "word": w, "log_odds_right_vs_left": round(d, 3), "z": round(z, 2), "count_right": yr, "count_left": yl,
                          "rtd_contribution": round(c, 5), "rank_right": ra, "rank_left": rb, "n_right_titles": len(r), "n_left_titles": len(l), "rtd_total": round(rtd, 4)})
    pd.DataFrame(wrows).sort_values(["model", "z"], ascending=[True, False]).to_csv(ANALYSIS_DIR / "leaning_words.csv", index=False)

    # blind adjudication sheet: 200 titles, mostly disagreements, model labels kept in a separate key
    sheet_path = ANALYSIS_DIR / "leaning_human_sheet.csv"
    if not sheet_path.exists() and len(cols) >= 2:
        rng = np.random.RandomState(SEED + 7)
        lab_only = df[cols].apply(lambda c: c.str.split("|").str[0])
        dis = df[(lab_only.nunique(axis=1) > 1)]
        agr = df[(lab_only.nunique(axis=1) == 1)]
        pick = pd.concat([dis.sample(min(140, len(dis)), random_state=rng), agr.sample(min(60, len(agr)), random_state=rng)]).sample(frac=1, random_state=rng)
        pick[["row_id", "creator", "title_raw"]].assign(human_label="", human_target="", notes="").to_csv(sheet_path, index=False)
        pick[["row_id", "creator", "title_raw"] + cols].to_csv(ANALYSIS_DIR / "leaning_human_key.csv", index=False)
        print(f"blind adjudication sheet written: {sheet_path} ({len(pick)} titles; fill human_label with left / right / neither)", flush=True)


def human_agreement(df: pd.DataFrame, cols: list[str], human_path) -> None:
    """Every model's agreement with the filled human sheet (kappa, exact agreement, confusion)."""
    from sklearn.metrics import cohen_kappa_score
    h = pd.read_csv(human_path)
    h = h[h["human_label"].astype(str).str.lower().isin(LABELS)][["row_id", "human_label"]]
    h["human_label"] = h["human_label"].str.lower()
    m = df.merge(h, on="row_id")
    rows = []
    for c in cols:
        lab = m[c].dropna().str.split("|").str[0]
        hh = m.loc[lab.index, "human_label"]
        rows.append({"model": c, "n": len(lab), "kappa_vs_human": round(float(cohen_kappa_score(hh, lab)), 3), "exact_agreement": round(float((hh == lab).mean()), 3),
                     "confusion": json.dumps(pd.crosstab(hh, lab).to_dict())})
    pd.DataFrame(rows).to_csv(ANALYSIS_DIR / "leaning_human_agreement.csv", index=False)
    print(pd.DataFrame(rows)[["model", "n", "kappa_vs_human", "exact_agreement"]].to_string(index=False))


def main(argv: Optional[Sequence[str]] = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--models", nargs="+", default=MODELS)
    ap.add_argument("--backend", choices=("ollama", "claude-code"), default="ollama")
    ap.add_argument("--prompt-version", choices=tuple(PROMPTS), default="v1")
    ap.add_argument("--human-labels", default=None, help="filled leaning_human_sheet.csv: report every model's agreement with the human labels")
    ap.add_argument("--n-per-creator", type=int, default=N_PER_CREATOR)
    ap.add_argument("--analyse-only", action="store_true")
    ap.add_argument("--limit", type=int, default=None)
    a = ap.parse_args(argv)
    with stage_timer("stage7_leaning", models=a.models, backend=a.backend, prompt_id=f"leaning-{a.prompt_version}",
                     api_cost_usd=0.0 if a.backend == "ollama" else "subscription (claude -p); see reported_cost_usd") as info:
        lanes = load_lanes()[["creator", "lane"]]
        if a.analyse_only and LABELS_CSV.exists():
            df = pd.read_csv(LABELS_CSV)
        else:
            prepared = load_prepared()
            df = draw_sample(prepared, a.n_per_creator).merge(lanes, on="creator", how="left")
            if a.limit:
                df = df.head(a.limit)
            if LABELS_CSV.exists():   # keep labels already on disk for other models
                old = pd.read_csv(LABELS_CSV)
                for c in [c for c in old.columns if c.startswith("label_")]:
                    df = df.merge(old[["row_id", c]], on="row_id", how="left")
            print(f"sample: {len(df)} titles from {df['creator'].nunique()} creators", flush=True)
            for model in a.models:
                col = model_col(model if a.backend == "ollama" else f"claude_code_{model}") + ("" if a.prompt_version == "v1" else f"_{a.prompt_version}")
                todo = df[col].isna() if col in df.columns else pd.Series(True, index=df.index)
                if todo.any():
                    labs = label_titles(df.loc[todo, "title_raw"].tolist(), model, info, a.backend, a.prompt_version)
                    df.loc[todo, col] = labs
                print(f"{model}: {df[col].notna().sum()}/{len(df)} labelled", flush=True)
            df["prompt_id"] = f"leaning-{a.prompt_version}"; df["prompt_sha256"] = hashlib.sha256(PROMPTS[a.prompt_version].encode()).hexdigest(); df["temperature"] = 0.0; df["labelled_at"] = utc_now()
            keep = ["row_id", "video_id", "creator", "genre", "lane", "title_raw", "title_norm"] + [c for c in df.columns if c.startswith("label_")] + ["prompt_id", "prompt_sha256", "temperature", "labelled_at"]
            df[keep].to_csv(LABELS_CSV, index=False)
            (CACHE_DIR / "leaning_prompt.txt").write_text(PROMPT, encoding="utf-8")
            (CACHE_DIR / "leaning_prompt_v2.txt").write_text(PROMPT_V2, encoding="utf-8")
        cols = [c for c in df.columns if c.startswith("label_")]
        analyse(df, cols, info)
        if a.human_labels:
            human_agreement(df, cols, a.human_labels)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
