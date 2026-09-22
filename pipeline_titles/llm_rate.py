"""Stage 2c - LLM ratings of a stratified 3,000-title sample (plus a 300-title retest).

Draws the sample from titles_prepared.parquet (unique titles only; every creator x
genre gets a base allocation - 8 titles for groups with >= 50 titles, 2 for low-n
groups - and the remainder is spread in proportion to log10(n), seed 20260914),
rates each RAW title with the rating model in batches of 20, and writes
data/titles/analysis/labels.csv with, per title:

    sensational, critical, analytical, educational, conversational   1-5
    humor, curiosity_gap, outrage                                    0/1
    format_llm     question | breaking_live | episode_show | interview_guest |
                   reaction | confrontation | listicle | howto_explainer | none
    retest_*       the same fields from a second pass over 300 titles, rated in
                   different, re-shuffled batches (test-retest reliability)
    model, prompt_id, prompt_sha256, temperature, rated_at, prompt (exact text)

Every model response is cached under data/titles/analysis/cache/llm/<sha1>.json,
so a re-run costs nothing; the run's call count, token counts and wall-clock go to
runtimes.jsonl (cost is 0: local model).

CLI:
    python -m pipeline_titles.llm_rate                     # full run (~1 h)
    python -m pipeline_titles.llm_rate --limit 60          # smoke test
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import time
import urllib.request
from typing import Optional, Sequence

import numpy as np
import pandas as pd

from pipeline_titles.common import (
    CACHE_DIR, LABELS_CSV, LOW_N, SEED, load_creators, load_prepared, stage_timer, utc_now,
)

OLLAMA_URL = "http://localhost:11434/api/generate"
DEFAULT_MODEL = "qwen3:14b"
TEMPERATURE = 0.0
BATCH_SIZE = 20
N_SAMPLE = 3000
N_RETEST = 300
PROMPT_ID = "title-style-v3"
FORMATS = ("question", "breaking_live", "episode_show", "interview_guest", "reaction",
           "confrontation", "listicle", "howto_explainer", "none")
DIMS = ("sensational", "critical", "analytical", "educational", "conversational")
FLAGS = ("humor", "curiosity_gap", "outrage")
LLM_CACHE = CACHE_DIR / "llm"

PROMPT_TEMPLATE = """You are annotating YouTube video titles from political-media channels. For each numbered title, rate five style dimensions on a 1-5 scale (1 = not at all, 3 = moderately, 5 = extremely), then give three yes/no flags (0 or 1) and one structural format label. Judge the title text only.

Dimensions:
- sensational: hype and emotional intensity - shock words, ALL-CAPS emphasis, exclamation marks, exaggeration, alarm. (1: 'Senate passes budget resolution'; 5: 'THIS CHANGES EVERYTHING!!! Trump's INSANE Move')
- critical: attacks, blames, mocks or condemns a person, group or institution. (1: 'How the Fed sets interest rates'; 5: 'Corrupt Coward Ted Cruz Humiliates Himself Again')
- analytical: informational or analytical framing - reports, explains or weighs a development in neutral, descriptive terms. (1: 'OMG..'; 5: 'Why the Iran ceasefire is fragile: three scenarios for the next month')
- educational: teaches - explains how something works, gives history or background, a how-to or explainer. (1: 'Trump SLAMS reporter'; 5: 'How tariffs actually work, explained')
- conversational: casual and chatty - addresses the audience directly, first or second person, slang, stream-of-consciousness. (1: 'Oil prices rise 3% as OPEC cuts output'; 5: 'chat, we need to talk about this..')
Use the whole 1-5 range: most titles are not 1 on every dimension.

Flags (answer 0 or 1 only, never a scale):
- humor: the title is meant to be funny or ironic (joke, pun, sarcasm, absurdity).
- curiosity_gap: key information is withheld to make you click (unnamed 'this' / 'he' / 'they', 'here's why', 'what happened next', trailing '...', a teaser).
- outrage: the subject is framed as outrageous, scandalous or threatening (slams, destroys, exposed, disaster, betrayal, meltdown).

Format (exactly one word): question | breaking_live | episode_show | interview_guest | reaction | confrontation | listicle | howto_explainer | none
question = phrased as a question; breaking_live = BREAKING / LIVE / WATCH label; episode_show = show name with an episode number or date; interview_guest = a named guest joins / interview / 'with' / 'ft.'; reaction = reacts to / responds to / reaction; confrontation = X vs Y, destroys, owns, debate, clash; listicle = a numbered list ('5 reasons', 'top 10'); howto_explainer = how to / explained / what is / why; none = none of these.

Output exactly one line per title, in order, with no other text:
id,sensational,critical,analytical,educational,conversational,humor_yn,curiosity_yn,outrage_yn,format
Example line for a title like 'Trump DESTROYS CNN reporter in heated exchange': 7,4,5,1,1,1,0,0,1,confrontation
Do not explain, do not add headers or commentary: only the CSV lines.

Titles:
{titles}"""

_LINE_RE = re.compile(
    r"^\s*\**(\d+)\**\s*[.)]?\s*[,;|\t]\s*(\d)\s*[,;|\t]\s*(\d)\s*[,;|\t]\s*(\d)\s*[,;|\t]\s*(\d)\s*[,;|\t]\s*(\d)"
    r"\s*[,;|\t]\s*(\d)\s*[,;|\t]\s*(\d)\s*[,;|\t]\s*(\d)\s*[,;|\t]\s*\**([A-Za-z_]+)")
FLAG_COERCIONS = {"n": 0}   # flags the model wrote on a 1-5 scale instead of 0/1 (>= 3 -> 1)


def _flag(v: int) -> int:
    if v in (0, 1):
        return v
    FLAG_COERCIONS["n"] += 1
    return 1 if v >= 3 else 0


# --------------------------------------------------------------------------- #
# Pure helpers (unit-tested)
# --------------------------------------------------------------------------- #
def allocate_sample(group_sizes: dict, total: int = N_SAMPLE, base_full: int = 8, base_low: int = 2,
                    low_n: int = LOW_N) -> dict:
    """Titles to draw per creator x genre: a base allocation for every group, the
    remainder in proportion to log10(n) over the non-low-n groups, never more than
    the group holds."""
    alloc = {g: min(n, base_full if n >= low_n else base_low) for g, n in group_sizes.items()}
    remainder = total - sum(alloc.values())
    if remainder > 0:
        full = {g: n for g, n in group_sizes.items() if n >= low_n}
        weights = {g: np.log10(max(n, 10)) for g, n in full.items()}
        wsum = sum(weights.values())
        extra = {g: int(round(remainder * w / wsum)) for g, w in weights.items()}
        for g, e in extra.items():
            alloc[g] = min(group_sizes[g], alloc[g] + e)
        # fix rounding to hit the total exactly (add/remove one at a time, largest groups first)
        order = sorted(full, key=lambda g: -group_sizes[g])
        i = 0
        while sum(alloc.values()) < total and i < 10 * len(order):
            g = order[i % len(order)]
            if alloc[g] < group_sizes[g]:
                alloc[g] += 1
            i += 1
        i = 0
        while sum(alloc.values()) > total and i < 10 * len(order):
            g = order[i % len(order)]
            if alloc[g] > (base_full if group_sizes[g] >= low_n else base_low):
                alloc[g] -= 1
            i += 1
    return alloc


def build_prompt(titles: Sequence[str]) -> str:
    lines = "\n".join(f"{i + 1}. {t}" for i, t in enumerate(titles))
    return PROMPT_TEMPLATE.format(titles=lines)


def parse_response(text: str, n: int) -> dict[int, dict]:
    """{id -> fields} for every well-formed output line with 1 <= id <= n."""
    out = {}
    for line in text.splitlines():
        m = _LINE_RE.match(line.strip().strip("`"))
        if not m:
            continue
        i = int(m.group(1))
        if not 1 <= i <= n or i in out:
            continue
        fmt = m.group(10)
        out[i] = {
            "sensational": int(m.group(2)), "critical": int(m.group(3)), "analytical": int(m.group(4)),
            "educational": int(m.group(5)), "conversational": int(m.group(6)),
            "humor": _flag(int(m.group(7))), "curiosity_gap": _flag(int(m.group(8))), "outrage": _flag(int(m.group(9))),
            "format_llm": fmt.lower() if fmt.lower() in FORMATS else "none",
        }
    return out


def cache_key(model: str, prompt: str, temperature: float) -> str:
    return hashlib.sha1(f"{model}\n{temperature}\n{prompt}".encode("utf-8")).hexdigest()


# --------------------------------------------------------------------------- #
def ollama_generate(model: str, prompt: str, temperature: float = TEMPERATURE, num_predict: int = 1200,
                    timeout: int = 900) -> dict:
    body = json.dumps({"model": model, "prompt": prompt, "stream": False, "think": False,
                       "options": {"temperature": temperature, "num_predict": num_predict, "num_ctx": 4096,
                                   "seed": SEED}}).encode()
    req = urllib.request.Request(OLLAMA_URL, data=body, headers={"Content-Type": "application/json"})
    return json.loads(urllib.request.urlopen(req, timeout=timeout).read())


def rate_batch(titles: Sequence[str], model: str, temperature: float, info: dict) -> dict[int, dict]:
    prompt = build_prompt(titles)
    key = cache_key(model, prompt, temperature)
    path = LLM_CACHE / f"{key}.json"
    if path.exists():
        rec = json.loads(path.read_text(encoding="utf-8"))
        info["cache_hits"] = info.get("cache_hits", 0) + 1
    else:
        t0 = time.time()
        r = ollama_generate(model, prompt, temperature)
        rec = {"model": model, "temperature": temperature, "prompt": prompt, "response": r.get("response", ""),
               "prompt_eval_count": r.get("prompt_eval_count"), "eval_count": r.get("eval_count"),
               "seconds": round(time.time() - t0, 2), "rated_at": utc_now()}
        LLM_CACHE.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(rec, ensure_ascii=False), encoding="utf-8")
        info["calls"] = info.get("calls", 0) + 1
        info["prompt_tokens"] = info.get("prompt_tokens", 0) + (rec["prompt_eval_count"] or 0)
        info["output_tokens"] = info.get("output_tokens", 0) + (rec["eval_count"] or 0)
        info["llm_seconds"] = round(info.get("llm_seconds", 0) + rec["seconds"], 1)
    return parse_response(rec["response"], len(titles))


def rate_titles(titles: Sequence[str], model: str, temperature: float, batch_size: int, info: dict,
                label: str = "") -> list[Optional[dict]]:
    """Rate every title; malformed / missing lines are retried in batches of 5, then 1."""
    results: list[Optional[dict]] = [None] * len(titles)
    pending = list(range(len(titles)))
    for size in (batch_size, 5, 1):
        if not pending:
            break
        for start in range(0, len(pending), size):
            idx = pending[start:start + size]
            parsed = rate_batch([titles[i] for i in idx], model, temperature, info)
            for j, i in enumerate(idx):
                if (j + 1) in parsed:
                    results[i] = parsed[j + 1]
            done = sum(r is not None for r in results)
            if size == batch_size and (start // size) % 10 == 0:
                print(f"  [{label}] {done}/{len(titles)} rated, calls {info.get('calls', 0)}, "
                      f"cache hits {info.get('cache_hits', 0)}, llm {info.get('llm_seconds', 0)} s", flush=True)
        pending = [i for i in pending if results[i] is None]
    return results


def draw_sample(prepared: pd.DataFrame, total: int = N_SAMPLE, seed: int = SEED) -> pd.DataFrame:
    uniq = prepared[~prepared["is_dup"]]
    sizes = uniq.groupby(["creator", "genre"]).size().to_dict()
    alloc = allocate_sample(sizes, total)
    rng = np.random.RandomState(seed)
    parts = []
    for (creator, genre), g in uniq.groupby(["creator", "genre"], sort=True):
        k = alloc[(creator, genre)]
        parts.append(g.iloc[np.sort(rng.choice(len(g), size=k, replace=False))])
    sample = pd.concat(parts).sort_values("row_id").reset_index(drop=True)
    return sample


def main(argv: Optional[Sequence[str]] = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--model", default=DEFAULT_MODEL)
    ap.add_argument("--batch-size", type=int, default=BATCH_SIZE)
    ap.add_argument("--limit", type=int, default=None, help="rate only the first N sampled titles (smoke test)")
    ap.add_argument("--no-retest", action="store_true")
    a = ap.parse_args(argv)
    with stage_timer("stage2c_llm_rate", model=a.model, temperature=TEMPERATURE, prompt_id=PROMPT_ID,
                     api_cost_usd=0.0) as info:
        prepared = load_prepared()
        creators = load_creators(with_group=False)[["creator", "organisation", "clipper"]]
        sample = draw_sample(prepared, N_SAMPLE).merge(creators, on="creator", how="left")
        if a.limit:
            sample = sample.head(a.limit)
        print(f"sample: {len(sample)} titles over {sample.groupby(['creator', 'genre']).ngroups} creator x genre groups", flush=True)
        titles = sample["title_raw"].tolist()
        ratings = rate_titles(titles, a.model, TEMPERATURE, a.batch_size, info, label="main")
        for col in DIMS + FLAGS + ("format_llm",):
            sample[col] = [r[col] if r else (np.nan if col != "format_llm" else "") for r in ratings]
        # retest: 300 titles re-rated in different, re-shuffled batches
        sample["retest"] = False
        if not a.no_retest:
            rng = np.random.RandomState(SEED + 1)
            n_re = min(N_RETEST, len(sample))
            re_idx = rng.choice(len(sample), size=n_re, replace=False)
            re_titles = [titles[i] for i in re_idx]
            re_ratings = rate_titles(re_titles, a.model, TEMPERATURE, a.batch_size, info, label="retest")
            sample.loc[re_idx, "retest"] = True
            for col in DIMS + FLAGS + ("format_llm",):
                vals = pd.Series([r[col] if r else np.nan for r in re_ratings], index=sample.index[re_idx])
                sample["retest_" + col] = vals.reindex(sample.index)
        prompt_text = PROMPT_TEMPLATE
        sample["model"] = a.model
        sample["prompt_id"] = PROMPT_ID
        sample["prompt_sha256"] = hashlib.sha256(prompt_text.encode("utf-8")).hexdigest()
        sample["temperature"] = TEMPERATURE
        sample["rated_at"] = utc_now()
        sample["prompt"] = prompt_text
        cols = ["row_id", "video_id", "creator", "genre", "organisation", "clipper", "platform", "month",
                "title_raw", "title_norm"] + list(DIMS + FLAGS) + ["format_llm", "retest"] + \
               [c for c in sample.columns if c.startswith("retest_")] + \
               ["model", "prompt_id", "prompt_sha256", "temperature", "rated_at", "prompt"]
        sample[cols].to_csv(LABELS_CSV, index=False)
        (CACHE_DIR / "labels_prompt.txt").write_text(prompt_text, encoding="utf-8")
        info["n_rated"] = int(sample["sensational"].notna().sum())
        info["flag_coercions"] = FLAG_COERCIONS["n"]
        info["n_sample"] = int(len(sample))
        info["n_retest"] = int(sample["retest"].sum())
        print(f"rated {info['n_rated']}/{len(sample)}; retest {info['n_retest']}; "
              f"calls {info.get('calls', 0)} prompt_tokens {info.get('prompt_tokens', 0)} output_tokens {info.get('output_tokens', 0)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
