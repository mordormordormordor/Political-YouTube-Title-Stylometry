"""Stage 0d - political leaning from titles alone, judged by a frontier model (the stage
runs third, after creators, because its channel groups are what every later stage reports
by; its runtime record keeps the historical name stage7_leaning).

A creator-balanced sample is labelled left / right / neither by Claude Opus through the
Claude Code CLI in print mode (a Claude Pro/Max subscription covers it; temperature 0;
twenty titles per call, sent in a seeded random order so that a call mixes channels and
the judge sees nothing but the title text; every response cached). The label is the
viewpoint the TITLE'S OWN WORDING signals, not the subject. Two levels of analysis follow: the
titles themselves, and the channels grouped as left / neutral / right by their scores.

Runs. The sample was labelled in three runs, all with the same prompt at temperature 0. Runs
1 and 2 (the base draw, then the top-up) sent the titles in sample order, so a call held one
or two channels' titles and a title was read beside its channel's other titles; run 3 sent
every title again in shuffled batches. Run 3 is the labelling of record
(leaning_labels.csv.gz). Runs 1 and 2 are kept as the first reading
(leaning_labels_channel_batched.csv.gz, column `run`), and two_readings() compares the two
readings title by title and channel by channel. The readings differ in their batches by
design, so their disagreement is the judge's own inconsistency and the effect of a title's
company together; neither is measured alone. `--repeat` reads every title of the sample a
third time with a fresh shuffle (run 4, leaning_labels_repeat.csv.gz): a clean repeat of the
method, whose disagreement with the labels of record is the judge's own inconsistency (plus
the luck of different batch-mates), so with three readings the batch-context effect and the
judge's noise can be told apart (repeat_check()).

Sample. Every creator gets a base draw of N_BASE (16) unique edited-upload titles
(seed 20260914; live VODs top up creators with fewer uploads). Creators with at least
--min-uploads (50) unique uploads are then topped up to --n-per-creator (N_PER_CREATOR,
50) with further uploads spread evenly across months (12,478 titles; 239 creators at
50, 35 at their base).

The channel groups written here (leaning_by_creator.csv, column `group`) are the only
between-channel grouping in the pipeline: common.load_creators() joins them to the
creator table, and every later stage reports by them. The stage therefore runs right
after prepare / creators in run_all.

Outputs (data/titles/analysis/):
    leaning_labels.csv.gz       one row per sampled title with the label, is_base (base draw vs
                                month-spread top-up) and month: the labels of record (run 3)
    leaning_labels_channel_batched.csv.gz
                                the first reading: the same titles labelled in runs 1 and 2, batched
                                by channel (column `run`); Claude Opus only
    leaning_runs.json           the three labelling runs from the run log: titles sent, batch order,
                                calls, minutes, output tokens, the CLI's reported cost
    leaning_two_readings.json   the first reading against the labels of record: agreement and kappa
                                (overall and per run), the confusion table, partisan shares, the
                                titles that changed side; the channel scores under the two readings
                                (Spearman, mean change, groups changed);
                                leaning_two_readings_channels.csv has the per-channel values and
                                leaning_two_readings_changed_titles.csv the titles whose label changed
    leaning_labels_repeat.csv.gz
                                the repeat: every title read again with a fresh shuffle (run 4)
    leaning_repeat.json         the repeat against the labels of record (a clean repeat: agreement, kappa,
                                the confusion table, channel scores) and against the first reading, plus the
                                three readings together (how many titles all three agree on);
                                leaning_repeat_channels.csv and leaning_repeat_changed_titles.csv as above
    leaning_label_shares.json   the labels' counts and shares
    leaning_by_creator.csv      per channel: label shares, score = (right - left) / n over its
                                sampled titles, and the group the score implies (left below
                                -0.05, right above +0.05, neutral between)
    leaning_groups.csv          the three groups: channels, titles, mean score and composition
    leaning_words.csv           right vs left vocabulary: weighted log-odds (alpha0 = 500) and
                                rank-turbulence-divergence contributions (alpha = 1/3)
    leaning_split_half.csv      split-half reliability of the channel scores
                                (channels with >= 32 labels, 20 random splits)
    leaning_stability.csv       the base 16-title score against the score from the disjoint
                                top-up titles and from all titles (Spearman, mean absolute
                                change, channels whose group changed);
                                leaning_stability_channels.csv has the per-channel values
    leaning_by_group_month.csv  partisan share and score per channel group x month
    plus the log-odds lexicon files of leaning_lexicon.py

Usage-limit replies from the CLI are waited out (5, 15, 30, 60 min). Prompt v2
(`--prompt-version v2`) also asks for the title's TARGET (who is attacked or featured),
which separates "attacks Trump" from "speaks for the left".

Human check. analyse() writes a blind adjudication sheet (leaning_human_sheet.csv: 200
titles, model labels hidden). Fill `human_label` and re-run with `--human-labels
data/titles/analysis/leaning_human_sheet.csv` to get the judge's agreement with a human
(leaning_human_agreement.csv). That is the accuracy check.

CLI:
    python -m pipeline_titles.leaning --n-per-creator 50            # sample, label, analyse
    python -m pipeline_titles.leaning --n-per-creator 50 --prompt-version v2
    python -m pipeline_titles.leaning --analyse-only [--human-labels <filled sheet>]
    python -m pipeline_titles.leaning --repeat [--shuffle-seed N]   # read every title again, fresh shuffle
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

from pipeline_titles.common import ANALYSIS_DIR, CACHE_DIR, RUNTIMES, SEED, load_prepared, read_jsonl, stage_timer, utc_now
from pipeline_titles.textstats import rank_turbulence_divergence, vocab_tokens, weighted_log_odds

N_BASE = 16              # the base draw every creator gets
N_PER_CREATOR = 50       # the target after the month-spread top-up
BATCH = 20
PROMPT_ID = "leaning-v1"
LABELS = ("left", "right", "neither")
TARGETS = ("trump_administration", "democrats_left", "republicans_right", "media", "foreign", "other", "none")
CLAUDE_BIN = shutil.which("claude") or "/opt/homebrew/bin/claude"
LIMIT_WAITS = (300, 900, 1800, 3600, 3600, 3600)
LABELS_CSV = ANALYSIS_DIR / "leaning_labels.csv.gz"
FIRST_READING_CSV = ANALYSIS_DIR / "leaning_labels_channel_batched.csv.gz"   # runs 1 and 2: the same titles, batched by channel
RUNS_JSON = ANALYSIS_DIR / "leaning_runs.json"
REPEAT_CSV = ANALYSIS_DIR / "leaning_labels_repeat.csv.gz"                    # run 4: every title again, a fresh shuffle
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


def claude_code_generate(model: str, prompt: str, timeout: int = 900) -> dict:
    """One batch through the Claude Code CLI in print mode (subscription billing);
    waits out usage-limit replies."""
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
                    "cost_usd": data.get("total_cost_usd"), "duration_ms": data.get("duration_ms"), "session_id": data.get("session_id"),
                    "model_id": next((k for k in sorted((data.get("modelUsage") or {}).keys()) if model in k), None)}   # what the alias resolved to (the CLI also lists its own helper model)
        if "limit" in err_text.lower() and wait:
            print(f"  usage limit reported; waiting {wait // 60} min (attempt {attempt + 1})", flush=True)
            time.sleep(wait)
            continue
        raise RuntimeError(f"claude -p failed (code {proc.returncode}): {err_text.strip()[:400] or raw[:400]}")
    raise RuntimeError("claude -p: usage limit persisted")


def label_batch(titles: Sequence[str], model: str, info: dict, prompt_version: str = "v1") -> dict[int, str]:
    prompt = PROMPTS[prompt_version].format(titles="\n".join(f"{i + 1}. {t}" for i, t in enumerate(titles)))
    model_key = f"claude-code:{model}"
    key = hashlib.sha1(f"{model_key}\n0\n{prompt}".encode()).hexdigest()
    path = LLM_CACHE / f"{key}.json"
    if path.exists():
        rec = json.loads(path.read_text(encoding="utf-8"))
        info["cache_hits"] = info.get("cache_hits", 0) + 1
    else:
        t0 = time.time()
        r = claude_code_generate(model, prompt)
        rec = {"model": model_key, "backend": "claude-code", "prompt_version": prompt_version, "prompt": prompt, "response": r.get("response", ""),
               "prompt_eval_count": r.get("prompt_eval_count"), "eval_count": r.get("eval_count"), "cost_usd": r.get("cost_usd"),
               "model_id": r.get("model_id"), "seconds": round(time.time() - t0, 2), "rated_at": utc_now()}
        LLM_CACHE.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(rec, ensure_ascii=False), encoding="utf-8")
        info["calls"] = info.get("calls", 0) + 1
        info["output_tokens"] = info.get("output_tokens", 0) + (rec["eval_count"] or 0)
        info["llm_seconds"] = round(info.get("llm_seconds", 0) + rec["seconds"], 1)
        if rec.get("cost_usd") is not None:
            info["reported_cost_usd"] = round(info.get("reported_cost_usd", 0) + (rec["cost_usd"] or 0), 4)
    if rec.get("model_id"):
        info.setdefault("model_ids", [])
        if rec["model_id"] not in info["model_ids"]:
            info["model_ids"].append(rec["model_id"])
    return parse_labels(rec["response"], len(titles))


def label_titles(titles: Sequence[str], model: str, info: dict, prompt_version: str = "v1", shuffle: bool = True, seed: int = SEED) -> list[Optional[str]]:
    """Label every title; `shuffle` (default) sends titles to the model in a seeded random
    order, so a batch of 20 mixes channels and a title is never judged in the company of
    its own channel's other titles (the sample is grouped by channel)."""
    results: list[Optional[str]] = [None] * len(titles)
    pending = list(np.random.RandomState(seed).permutation(len(titles))) if shuffle else list(range(len(titles)))
    for size in (BATCH, 5, 1):
        if not pending:
            break
        for start in range(0, len(pending), size):
            idx = pending[start:start + size]
            parsed = label_batch([titles[i] for i in idx], model, info, prompt_version)
            for j, i in enumerate(idx):
                if (j + 1) in parsed:
                    results[i] = parsed[j + 1]
            if size == BATCH and (start // size) % 10 == 0:
                print(f"  [{model}] {sum(r is not None for r in results)}/{len(titles)} labelled, calls {info.get('calls', 0)}, cache hits {info.get('cache_hits', 0)}", flush=True)
        pending = [i for i in pending if results[i] is None]
    return results


def draw_sample(prepared: pd.DataFrame, n_per: int = N_PER_CREATOR, seed: int = SEED, n_base: int = N_BASE,
                min_uploads: int = 50) -> pd.DataFrame:
    """Creator-balanced sample. Every creator gets `n_base` titles by the original
    draw (random, seed 20260914; live VODs top up creators with fewer uploads).
    Creators with at least `min_uploads` unique edited uploads are then topped up to
    `n_per` with further uploads spread evenly across months (round-robin over the
    months, random within month), so the extra titles never depend on which month a
    creator posted most in. The base draw is unchanged, so earlier labels are reused."""
    uniq = prepared[~prepared["is_dup"]]
    rng = np.random.RandomState(seed)          # base draw: identical to the original 16-title sample
    rng_top = np.random.RandomState(seed + 1)  # top-up: its own stream, so the base draw never shifts
    parts = []
    for creator, g in uniq.groupby("creator", sort=True):
        vids = g[g["genre"] == "videos"]
        pool = vids if len(vids) >= n_base else pd.concat([vids, g[g["genre"] == "streams"]])
        k = min(n_base, len(pool))
        base = pool.iloc[np.sort(rng.choice(len(pool), size=k, replace=False))].assign(is_base=True)
        parts.append(base)
        extra = n_per - len(base)
        if extra > 0 and len(vids) >= min_uploads:
            rest = vids[~vids["row_id"].isin(base["row_id"])]
            by_month = {m: grp.iloc[rng_top.permutation(len(grp))] for m, grp in rest.groupby("month")}
            months = sorted(by_month)
            picked, i = [], 0
            while len(picked) < extra and any(len(v) for v in by_month.values()):
                m = months[i % len(months)]; i += 1
                if len(by_month[m]):
                    picked.append(by_month[m].iloc[0]); by_month[m] = by_month[m].iloc[1:]
            if picked:
                parts.append(pd.DataFrame(picked).assign(is_base=False))
    return pd.concat(parts).sort_values("row_id").reset_index(drop=True)


def split_half_reliability(df: pd.DataFrame, cols: list[str], min_titles: int = 32, seed: int = SEED) -> pd.DataFrame:
    """Score each channel from two random halves of its titles; Spearman across channels
    per model (and the mean over 20 random splits)."""
    rng = np.random.RandomState(seed)
    rows = []
    big = [c for c, g in df.groupby("creator") if len(g) >= min_titles]
    half_sizes = [len(g) // 2 for c, g in df.groupby("creator") if c in set(big)]
    for c in cols:
        rs = []
        for _ in range(20):
            a_scores, b_scores = [], []
            for creator in big:
                g = df[(df["creator"] == creator)].dropna(subset=[c])
                if len(g) < min_titles:
                    continue
                idx = rng.permutation(len(g)); h = len(g) // 2
                for part, store in ((g.iloc[idx[:h]], a_scores), (g.iloc[idx[h:2 * h]], b_scores)):
                    v = part[c]
                    store.append(((v == "right").sum() - (v == "left").sum()) / len(v))
            if len(a_scores) > 5:
                rs.append(pd.Series(a_scores).corr(pd.Series(b_scores), method="spearman"))
        rows.append({"model": c, "n_channels": len(big), "min_titles_per_half": min_titles // 2, "median_titles_per_half": int(np.median(half_sizes)) if half_sizes else 0,
                     "split_half_spearman_mean": round(float(np.mean(rs)), 3) if rs else np.nan,
                     "split_half_spearman_sd": round(float(np.std(rs)), 3) if rs else np.nan})
    return pd.DataFrame(rows)


def _score(v: pd.Series) -> float:
    return float(((v == "right").sum() - (v == "left").sum()) / len(v)) if len(v) else np.nan


GROUP_EPS = 0.05
GROUPS = ("left", "neutral", "right")


def _side(s: pd.Series, eps: float = GROUP_EPS) -> np.ndarray:
    """A channel's group from its score: right above +eps, left below -eps, neutral between."""
    return np.where(s > eps, "right", np.where(s < -eps, "left", "neutral"))


def ensure_sample_columns(df: pd.DataFrame) -> pd.DataFrame:
    """`is_base` (base draw vs top-up) and `month` for a labels file that lacks them; both are
    recomputed from the prepared titles."""
    if "is_base" in df.columns and "month" in df.columns:
        return df
    prepared = load_prepared()
    if "month" not in df.columns:
        df = df.merge(prepared[["row_id", "month"]], on="row_id", how="left")
    if "is_base" not in df.columns:
        base_ids = set(draw_sample(prepared, N_BASE)["row_id"])   # n_per == n_base: the base draw alone
        df["is_base"] = df["row_id"].isin(base_ids)
    return df


def stability_check(df: pd.DataFrame, judge: str, min_topup: int = 10) -> tuple[pd.DataFrame, pd.DataFrame]:
    """For every topped-up channel, the score from the base draw against the score from its
    disjoint top-up titles and from all its titles: how much a channel's score and group
    depended on which titles were drawn. Returns (one-row summary, per-channel frame)."""
    recs = []
    for creator, g in df.dropna(subset=[judge]).groupby("creator"):
        b, t = g[g["is_base"].astype(bool)], g[~g["is_base"].astype(bool)]
        if len(t) < min_topup or not len(b):
            continue
        recs.append({"creator": creator, "n_base": len(b), "n_topup": len(t), "score_base": _score(b[judge]), "score_topup": _score(t[judge]), "score_all": _score(g[judge])})
    r = pd.DataFrame(recs)
    if len(r) < 5:
        return pd.DataFrame(), r
    r["group_base"], r["group_all"] = _side(r["score_base"]), _side(r["score_all"])
    r["change"] = r["score_all"] - r["score_base"]
    flipped = ((r["group_base"] == "left") & (r["group_all"] == "right")) | ((r["group_base"] == "right") & (r["group_all"] == "left"))
    summ = pd.DataFrame([{"n_channels": len(r), "spearman_base_vs_topup": round(float(r["score_base"].corr(r["score_topup"], method="spearman")), 3),
                          "pearson_base_vs_topup": round(float(r["score_base"].corr(r["score_topup"])), 3),
                          "spearman_base_vs_all": round(float(r["score_base"].corr(r["score_all"], method="spearman")), 3),
                          "mean_abs_change": round(float(r["change"].abs().mean()), 3), "median_abs_change": round(float(r["change"].abs().median()), 3),
                          "max_abs_change": round(float(r["change"].abs().max()), 3), "group_changed": int((r["group_base"] != r["group_all"]).sum()), "sign_flipped": int(flipped.sum())}])
    return summ, r.sort_values("change").reset_index(drop=True)


def group_month_check(df: pd.DataFrame, judge: str, groups: dict[str, str]) -> pd.DataFrame:
    """The labels by channel group x month over the month-spread sample: titles, channels,
    share read as partisan (left or right), left and right shares, score."""
    d = df.dropna(subset=[judge, "month"]).copy()
    d["group"] = d["creator"].map(groups)
    d["partisan"] = (d[judge] != "neither").astype(float)
    d["value"] = np.where(d[judge] == "right", 1.0, np.where(d[judge] == "left", -1.0, 0.0))
    d["is_left"] = (d[judge] == "left").astype(float); d["is_right"] = (d[judge] == "right").astype(float)
    out = d.groupby(["group", "month"]).agg(n_titles=("row_id", "size"), n_creators=("creator", "nunique"), partisan_share=("partisan", "mean"),
                                            left_share=("is_left", "mean"), right_share=("is_right", "mean"), score=("value", "mean")).reset_index()
    return out.round(4)


def _agree(a: pd.Series, b: pd.Series) -> dict:
    """Exact agreement and Cohen's kappa of two label series (kappa None when it is undefined: no titles, or one label only)."""
    from sklearn.metrics import cohen_kappa_score
    defined = len(a) > 0 and (a.nunique() > 1 or b.nunique() > 1)
    return {"n_titles": int(len(a)), "exact_agreement": round(float((a == b).mean()), 4) if len(a) else None,
            "kappa": round(float(cohen_kappa_score(a, b, labels=list(LABELS))), 4) if defined else None}


def compare_readings(m: pd.DataFrame, col_a: str, col_b: str, name_a: str, name_b: str, min_titles: int = N_BASE) -> tuple[dict, pd.DataFrame, pd.DataFrame]:
    """Two readings of the same titles, `col_a` (the earlier) against `col_b` (the later), title
    by title and channel by channel. `m` has row_id, creator, title_raw, the two label columns
    and, optionally, `run` (which run made reading A: agreement is then also given per run).
    Names the two readings `name_a` / `name_b` in the summary's keys ("first", "shuffled",
    "record", "repeat"). Returns (summary, per-channel frame, the titles whose label changed)."""
    m = m.dropna(subset=[col_a, col_b])
    a, b = m[col_a], m[col_b]
    part_a, part_b = a.isin(("left", "right")), b.isin(("left", "right"))
    both = part_a & part_b
    out = {**_agree(a, b),
           f"label_counts_{name_a}": {k: int(v) for k, v in a.value_counts().reindex(LABELS, fill_value=0).items()},
           f"label_counts_{name_b}": {k: int(v) for k, v in b.value_counts().reindex(LABELS, fill_value=0).items()},
           f"partisan_share_{name_a}": round(float(part_a.mean()), 4), f"partisan_share_{name_b}": round(float(part_b.mean()), 4),
           "partisan_to_neither": int((part_a & ~part_b).sum()), "neither_to_partisan": int((~part_a & part_b).sum()),
           "side_flipped": int(((b == "left") & (a == "right")).sum() + ((b == "right") & (a == "left")).sum()),
           "same_side_when_both_partisan": round(float((a[both] == b[both]).mean()), 4) if both.any() else None,
           f"confusion_{name_a}_then_{name_b}": {x: {y: int(((a == x) & (b == y)).sum()) for y in LABELS} for x in LABELS}}
    if "run" in m.columns:
        out["by_run"] = {int(r): _agree(g[col_a], g[col_b]) for r, g in m.groupby("run")}
    sa, sb = f"score_{name_a}", f"score_{name_b}"
    ch = m.groupby("creator").agg(n_titles=(col_b, "size"), **{sa: (col_a, _score), sb: (col_b, _score)}).reset_index()
    ch["change"] = ch[sb] - ch[sa]
    ch[f"group_{name_a}"], ch[f"group_{name_b}"] = _side(ch[sa]), _side(ch[sb])
    big = ch[ch["n_titles"] >= min_titles]
    ga, gb = big[f"group_{name_a}"], big[f"group_{name_b}"]
    flipped = ((ga == "left") & (gb == "right")) | ((ga == "right") & (gb == "left"))
    out.update({"n_channels": int(len(big)), "min_titles_per_channel": min_titles,
                "channel_spearman": round(float(big[sa].corr(big[sb], method="spearman")), 4) if len(big) > 2 else None,
                "channel_mean_abs_change": round(float(big["change"].abs().mean()), 4) if len(big) else None,
                "channel_max_abs_change": round(float(big["change"].abs().max()), 4) if len(big) else None,
                "channel_group_changed": int((ga != gb).sum()), "channel_sign_flipped": int(flipped.sum())})
    cols = ["row_id", "creator"] + (["run"] if "run" in m.columns else []) + ["title_raw", col_a, col_b]
    changed = m[a != b][cols].rename(columns={col_a: f"label_{name_a}", col_b: f"label_{name_b}"})
    return out, ch.sort_values("change").reset_index(drop=True), changed.reset_index(drop=True)


def two_readings(df: pd.DataFrame, first: pd.DataFrame, judge: str, min_titles: int = N_BASE) -> tuple[dict, pd.DataFrame, pd.DataFrame]:
    """The judge's two readings of the same titles: the labels of record (`df`, shuffled batches)
    against the first reading (`first`, batches in sample order, so a title was read beside its
    channel's other titles; column `run` says which run labelled it), title by title and channel
    by channel. The readings differ in their batches by design, so the disagreement is the judge's
    own inconsistency and the effect of a title's company together; neither is measured alone.
    Returns (summary, per-channel frame, the titles whose label changed)."""
    m = df[["row_id", "creator", "title_raw", judge]].merge(first[["row_id", "run", judge]].rename(columns={judge: "label_first"}), on="row_id")
    out, ch, changed = compare_readings(m, "label_first", judge, "first", "shuffled", min_titles)
    return {"judge": judge, "first_reading": "runs 1 and 2, batches in sample order", "reading_of_record": "run 3, shuffled batches", **out}, ch, changed


def repeat_check(df: pd.DataFrame, first: Optional[pd.DataFrame], repeat: pd.DataFrame, judge: str, min_titles: int = N_BASE) -> tuple[dict, pd.DataFrame, pd.DataFrame]:
    """The clean repeat (run 4: every title again, a fresh shuffle) against the labels of record,
    title by title and channel by channel: the same method twice, so the disagreement is the
    judge's own inconsistency (with the luck of different batch-mates). With the first reading
    too, all three pairs are given, so the batch-context effect can be read against the judge's
    noise: what the first reading loses beyond what the repeat loses is the company a title was
    read in. Returns (summary, per-channel frame, the titles the repeat changed)."""
    m = df[["row_id", "creator", "title_raw", judge]].merge(repeat[["row_id", judge]].rename(columns={judge: "label_repeat"}), on="row_id")
    out, ch, changed = compare_readings(m, judge, "label_repeat", "record", "repeat", min_titles)
    summ = {"judge": judge, "reading_of_record": "run 3, shuffled batches", "repeat": "run 4, shuffled batches, a fresh seed", "record_vs_repeat": out}
    if first is not None and judge in first.columns:
        m3 = m.merge(first[["row_id", "run", judge]].rename(columns={judge: "label_first"}), on="row_id").dropna(subset=[judge, "label_first", "label_repeat"])
        f_vs_rep, _, _ = compare_readings(m3, "label_first", "label_repeat", "first", "repeat", min_titles)
        f_vs_rec, _, _ = compare_readings(m3, "label_first", judge, "first", "record", min_titles)
        pair = lambda d: {k: d[k] for k in ("n_titles", "exact_agreement", "kappa", "channel_spearman")}
        rec, rep = m3[judge], m3["label_repeat"]
        all_three = (rec == rep) & (rec == m3["label_first"])
        summ["first_vs_repeat"] = pair(f_vs_rep)
        summ["first_vs_record"] = pair(f_vs_rec)
        summ["three_readings"] = {"n_titles": int(len(m3)), "all_three_agree": round(float(all_three.mean()), 4),
                                  "record_and_repeat_agree": round(float((rec == rep).mean()), 4),
                                  "first_agrees_with_both": round(float(all_three.sum() / max(1, int((rec == rep).sum()))), 4),
                                  "no_majority": int(((rec != rep) & (rec != m3["label_first"]) & (rep != m3["label_first"])).sum())}
    return summ, ch, changed


def runs_table(df: pd.DataFrame, first: Optional[pd.DataFrame], repeat: Optional[pd.DataFrame] = None) -> list[dict]:
    """The labelling runs, oldest first, from the run log (this stage's records that made calls)
    with the titles each sent: the sample-order runs are the first reading's runs in order; the
    first shuffled run is the labelling of record and sent every title; a later shuffled run is
    the repeat (every title again, a fresh seed). `titles` is None when the log and the label
    files disagree."""
    recs = sorted((r for r in read_jsonl(RUNTIMES) if r.get("stage") == "stage7_leaning" and r.get("calls")), key=lambda r: r["started"])
    sample_order = [int((first["run"] == r).sum()) for r in sorted(first["run"].unique())] if first is not None and "run" in first.columns else []
    out, k, shuffled_seen = [], 0, 0
    for i, r in enumerate(recs, 1):
        order = r.get("batch_order", "sample order")
        if order == "sample order":
            titles = sample_order[k] if k < len(sample_order) else None; k += 1
            what, labels = ("the base draw" if i == 1 else "the top-up"), "first reading"
        elif shuffled_seen == 0:
            titles, what, labels = len(df), "every title again", "of record"; shuffled_seen += 1
        else:
            titles, what, labels = (len(repeat) if repeat is not None else None), "every title again, a fresh shuffle", "repeat"; shuffled_seen += 1
        out.append({"run": i, "what": what, "batch_order": order, "titles": titles, "calls": int(r["calls"]), "minutes": round(float(r["seconds"]) / 60, 1),
                    "output_tokens": r.get("output_tokens"), "reported_cost_usd": r.get("reported_cost_usd"), "model_ids": r.get("model_ids"),
                    "shuffle_seed": r.get("shuffle_seed"), "started": r["started"], "finished": r["finished"], "labels": labels})
    return out


def analyse(df: pd.DataFrame, cols: list[str], info: dict) -> None:
    """Two levels. Titles: the judge's labels and their shares. Channels: score = (right - left) / n
    over a channel's sampled titles, the group it implies (left / neutral / right at +-GROUP_EPS),
    the groups' composition, reliability, the group x month table;
    then the vocabulary (leaning_words.csv) and the log-odds lexicon (leaning_lexicon.py)."""
    df = df.copy()
    for c in cols:                                   # 'left|democrats_left' -> label column + target column
        if df[c].astype(str).str.contains(r"\|").any():
            df[c.replace("label_", "target_")] = df[c].str.split("|").str[1]
            df[c] = df[c].str.split("|").str[0]
    judge = next((c for c in cols if "claude_code" in c), cols[0])
    ok = df.dropna(subset=[judge])
    counts = ok[judge].value_counts().reindex(LABELS, fill_value=0)
    (ANALYSIS_DIR / "leaning_label_shares.json").write_text(json.dumps({"judge": judge, "n_labelled": int(len(ok)), "label_counts": {k: int(v) for k, v in counts.items()},
                                                                          "label_shares": {k: round(float(v / len(ok)), 4) for k, v in counts.items()}}, indent=2))
    info.update({"n_labelled": int(len(ok)), "label_shares": {k: round(float(v / len(ok)), 4) for k, v in counts.items()}})

    # channels: score and group
    rows = []
    for creator, g in df.groupby("creator"):
        v = g[judge].dropna()
        rec = {"creator": creator, "n_titles": len(g), f"{judge}_n": len(v)}
        for l in LABELS:
            rec[f"{judge}_{l}"] = float((v == l).mean()) if len(v) else np.nan
        rec["score"] = _score(v)
        rec[f"{judge}_score"] = rec["score"]
        rows.append(rec)
    bc = pd.DataFrame(rows)
    bc["group"] = _side(bc["score"])
    bc["judge_of_record"] = judge; bc["judge_score"] = bc["score"]; bc["judge_side"] = bc["group"]; bc["mean_score"] = bc["score"]; bc["implied_side"] = bc["group"]   # read by the cards
    bc = bc.sort_values("score").reset_index(drop=True)
    bc.to_csv(ANALYSIS_DIR / "leaning_by_creator.csv", index=False)
    groups = dict(zip(bc["creator"], bc["group"]))
    gs = bc.groupby("group").agg(n_channels=("creator", "size"), n_titles=("n_titles", "sum"), mean_score=("score", "mean"), min_score=("score", "min"), max_score=("score", "max"),
                                 mean_left=(f"{judge}_left", "mean"), mean_neither=(f"{judge}_neither", "mean"), mean_right=(f"{judge}_right", "mean")).reindex(GROUPS).reset_index()
    gs.to_csv(ANALYSIS_DIR / "leaning_groups.csv", index=False)
    (ANALYSIS_DIR / "leaning_summary.json").write_text(json.dumps({"judge_of_record": judge, "threshold": GROUP_EPS, "n_channels": int(len(bc)),
                                                                     "groups": {g: int(n) for g, n in bc["group"].value_counts().reindex(GROUPS, fill_value=0).items()}}, indent=2))
    info["groups"] = {g: int(n) for g, n in bc["group"].value_counts().items()}

    # vocabulary of right-read vs left-read titles
    r, l = df[df[judge] == "right"], df[df[judge] == "left"]
    cr, cl = Counter(), Counter()
    for t in r["title_norm"]:
        cr.update(vocab_tokens(t))
    for t in l["title_norm"]:
        cl.update(vocab_tokens(t))
    wlo = weighted_log_odds(cr, cl, alpha0=500.0)
    rtd, contribs = rank_turbulence_divergence(cr, cl, alpha=1 / 3)
    rtd_map = {w: (c, ra, rb) for w, c, ra, rb in contribs}
    wrows = []
    for w, (d, z, yr, yl) in wlo.items():
        if yr + yl < 3:
            continue
        c, ra, rb = rtd_map.get(w, (np.nan, np.nan, np.nan))
        wrows.append({"model": judge, "word": w, "log_odds_right_vs_left": round(d, 3), "z": round(z, 2), "count_right": yr, "count_left": yl,
                      "rtd_contribution": round(c, 5), "rank_right": ra, "rank_left": rb, "n_right_titles": len(r), "n_left_titles": len(l), "rtd_total": round(rtd, 4)})
    pd.DataFrame(wrows).sort_values("z", ascending=False).to_csv(ANALYSIS_DIR / "leaning_words.csv", index=False)

    # reliability, months
    shr = split_half_reliability(df, [judge])
    shr.to_csv(ANALYSIS_DIR / "leaning_split_half.csv", index=False)
    if "is_base" in df.columns and "month" in df.columns:
        stab, stab_ch = stability_check(df, judge)
        stab_ch["group"] = stab_ch["creator"].map(groups)
        stab.to_csv(ANALYSIS_DIR / "leaning_stability.csv", index=False)
        stab_ch.to_csv(ANALYSIS_DIR / "leaning_stability_channels.csv", index=False)
        group_month_check(df, judge, groups).to_csv(ANALYSIS_DIR / "leaning_by_group_month.csv", index=False)
        if len(stab):
            print(stab[["n_channels", "spearman_base_vs_topup", "group_changed", "sign_flipped"]].to_string(index=False), flush=True)
    # the same titles read twice: the first reading (runs 1 and 2, batched by channel) against the labels of record
    first = pd.read_csv(FIRST_READING_CSV) if FIRST_READING_CSV.exists() else None
    if first is not None and judge in first.columns:
        two, two_ch, changed = two_readings(df, first, judge)
        two_ch["group"] = two_ch["creator"].map(groups)
        (ANALYSIS_DIR / "leaning_two_readings.json").write_text(json.dumps(two, indent=2))
        two_ch.to_csv(ANALYSIS_DIR / "leaning_two_readings_channels.csv", index=False)
        changed.to_csv(ANALYSIS_DIR / "leaning_two_readings_changed_titles.csv", index=False)
        info["two_readings"] = {k: two[k] for k in ("exact_agreement", "kappa", "channel_spearman")}
        print(f"two readings: exact agreement {two['exact_agreement']}, kappa {two['kappa']}, channel Spearman {two['channel_spearman']}, {len(changed)} titles changed label", flush=True)
    # the clean repeat (run 4), against the labels of record and the first reading
    repeat = pd.read_csv(REPEAT_CSV) if REPEAT_CSV.exists() else None
    if repeat is not None and judge in repeat.columns and repeat[judge].notna().sum() == len(repeat):
        rep, rep_ch, rep_changed = repeat_check(df, first, repeat, judge)
        rep_ch["group"] = rep_ch["creator"].map(groups)
        (ANALYSIS_DIR / "leaning_repeat.json").write_text(json.dumps(rep, indent=2))
        rep_ch.to_csv(ANALYSIS_DIR / "leaning_repeat_channels.csv", index=False)
        rep_changed.to_csv(ANALYSIS_DIR / "leaning_repeat_changed_titles.csv", index=False)
        r = rep["record_vs_repeat"]
        info["repeat"] = {k: r[k] for k in ("exact_agreement", "kappa", "channel_spearman")}
        print(f"repeat: exact agreement {r['exact_agreement']}, kappa {r['kappa']}, channel Spearman {r['channel_spearman']}, {len(rep_changed)} titles changed label", flush=True)
    RUNS_JSON.write_text(json.dumps(runs_table(df, first, repeat), indent=2))
    print(f"channels: {info['groups']}; split-half {shr.split_half_spearman_mean.iloc[0] if len(shr) else float('nan')}", flush=True)
    # log-odds lexicons (left / right / neither at a z cutoff) and the out-of-fold lexicon check
    from pipeline_titles.leaning_lexicon import run as lexicon_run
    lexicon_run(df, [judge], judge, info=info)

    # blind adjudication sheet: 200 titles, model labels kept out of the sheet
    sheet_path = ANALYSIS_DIR / "leaning_human_sheet.csv"
    if not sheet_path.exists():
        rng = np.random.RandomState(SEED + 7)
        part = df[df[judge].isin(["left", "right"])]; neu = df[df[judge] == "neither"]
        pick = pd.concat([part.sample(min(140, len(part)), random_state=rng), neu.sample(min(60, len(neu)), random_state=rng)]).sample(frac=1, random_state=rng)
        pick[["row_id", "creator", "title_raw"]].assign(human_label="", human_target="", notes="").to_csv(sheet_path, index=False)
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
    ap.add_argument("--models", nargs="+", default=["opus"], help="Claude Code model aliases (default: opus)")
    ap.add_argument("--relabel", action="store_true", help="start the labels file afresh (the old file is kept as leaning_labels_previous.csv.gz, untracked; the committed first reading is leaning_labels_channel_batched.csv.gz)")
    ap.add_argument("--no-shuffle", action="store_true", help="batch titles in sample order (one or two channels per batch) instead of a seeded random order")
    ap.add_argument("--prompt-version", choices=tuple(PROMPTS), default="v1")
    ap.add_argument("--human-labels", default=None, help="filled leaning_human_sheet.csv: report every model's agreement with the human labels")
    ap.add_argument("--n-per-creator", type=int, default=N_PER_CREATOR, help=f"titles per ranked creator (base {N_BASE} for everyone; top-up spread across months)")
    ap.add_argument("--min-uploads", type=int, default=50, help="creators with fewer unique edited uploads stay at the base 16")
    ap.add_argument("--repeat", action="store_true", help="read every title of the sample of record again with a fresh shuffle (run 4) into leaning_labels_repeat.csv.gz, then analyse; the labels of record are untouched")
    ap.add_argument("--shuffle-seed", type=int, default=None, help=f"seed of the batch order (default {SEED}; --repeat defaults to {SEED + 1})")
    ap.add_argument("--analyse-only", action="store_true")
    ap.add_argument("--limit", type=int, default=None)
    a = ap.parse_args(argv)
    seed = a.shuffle_seed if a.shuffle_seed is not None else (SEED + 1 if a.repeat else SEED)
    with stage_timer("stage7_leaning", models=a.models, backend="claude-code", prompt_id=f"leaning-{a.prompt_version}", batch_order="sample order" if a.no_shuffle else "shuffled",
                     shuffle_seed=seed, repeat=bool(a.repeat), api_cost_usd="subscription (claude -p); see reported_cost_usd") as info:
        keep_cols = ["row_id", "video_id", "creator", "genre", "month", "is_base", "title_raw", "title_norm"]
        if a.repeat:
            # run 4: the sample of record, every title again, a fresh batch order; its own file, the record untouched
            df = pd.read_csv(LABELS_CSV)
            rep = df[[c for c in keep_cols if c in df.columns]].copy()
            if REPEAT_CSV.exists():   # resume: keep the labels already on disk
                old = pd.read_csv(REPEAT_CSV)
                for c in [c for c in old.columns if c.startswith("label_")]:
                    rep = rep.merge(old[["row_id", c]], on="row_id", how="left")
            print(f"repeat: {len(rep)} titles from {rep['creator'].nunique()} creators, shuffle seed {seed}", flush=True)
            for model in a.models:
                col = model_col(f"claude_code_{model}") + ("" if a.prompt_version == "v1" else f"_{a.prompt_version}")
                todo = rep[col].isna() if col in rep.columns else pd.Series(True, index=rep.index)
                if todo.any():
                    rep.loc[todo, col] = label_titles(rep.loc[todo, "title_raw"].tolist(), model, info, a.prompt_version, shuffle=True, seed=seed)
                print(f"{model}: {rep[col].notna().sum()}/{len(rep)} labelled", flush=True)
            rep["run"] = 4; rep["prompt_id"] = f"leaning-{a.prompt_version}"; rep["prompt_sha256"] = hashlib.sha256(PROMPTS[a.prompt_version].encode()).hexdigest()
            rep["temperature"] = 0.0; rep["labelled_at"] = utc_now(); rep["batch_order"] = "shuffled"; rep["shuffle_seed"] = seed; rep["model_id"] = ", ".join(info.get("model_ids", [])) or None
            rep.to_csv(REPEAT_CSV, index=False)
            df = pd.read_csv(LABELS_CSV)
        elif a.analyse_only and LABELS_CSV.exists():
            df = pd.read_csv(LABELS_CSV)
            if "is_base" not in df.columns or "month" not in df.columns:   # older layouts of the labels file
                df = ensure_sample_columns(df)
                df[[c for c in keep_cols if c in df.columns] + [c for c in df.columns if c not in keep_cols]].to_csv(LABELS_CSV, index=False)
        else:
            prepared = load_prepared()
            df = draw_sample(prepared, a.n_per_creator, min_uploads=a.min_uploads)
            if a.limit:
                df = df.head(a.limit)
            if LABELS_CSV.exists() and not a.relabel:   # keep labels already on disk
                old = pd.read_csv(LABELS_CSV)
                for c in [c for c in old.columns if c.startswith("label_")]:
                    df = df.merge(old[["row_id", c]], on="row_id", how="left")
            elif LABELS_CSV.exists():
                archive = ANALYSIS_DIR / "leaning_labels_previous.csv.gz"
                shutil.copy(LABELS_CSV, archive)
                print(f"--relabel: previous labels kept at {archive.name}; labelling afresh with {a.models}", flush=True)
            print(f"sample: {len(df)} titles from {df['creator'].nunique()} creators", flush=True)
            for model in a.models:
                col = model_col(f"claude_code_{model}") + ("" if a.prompt_version == "v1" else f"_{a.prompt_version}")
                todo = df[col].isna() if col in df.columns else pd.Series(True, index=df.index)
                if todo.any():
                    labs = label_titles(df.loc[todo, "title_raw"].tolist(), model, info, a.prompt_version, shuffle=not a.no_shuffle, seed=seed)
                    df.loc[todo, col] = labs
                print(f"{model}: {df[col].notna().sum()}/{len(df)} labelled", flush=True)
            df["prompt_id"] = f"leaning-{a.prompt_version}"; df["prompt_sha256"] = hashlib.sha256(PROMPTS[a.prompt_version].encode()).hexdigest(); df["temperature"] = 0.0; df["labelled_at"] = utc_now()
            df["batch_order"] = "sample order" if a.no_shuffle else "shuffled"
            keep = keep_cols + [c for c in df.columns if c.startswith("label_")] + ["prompt_id", "prompt_sha256", "temperature", "labelled_at", "batch_order"]
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
