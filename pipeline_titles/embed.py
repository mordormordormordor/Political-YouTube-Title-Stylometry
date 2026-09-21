"""Stage 1a - sentence embeddings of every unique normalized title.

Encodes the unique `title_norm` strings of titles_prepared.parquet with a
sentence-transformers model (all-mpnet-base-v2, 768-d, L2-normalized) on the Mac
GPU and caches them, so the topic model (Stage 1), the hook classifier (Stage 3)
and the template analysis never re-encode.

Output (data/titles/analysis/cache/):
    embeddings.npy          float16 [n_unique, 768], rows in the order of
    embeddings_index.parquet  title_norm -> row (sorted unique strings)

CLI:
    python -m pipeline_titles.embed
    python -m pipeline_titles.embed --model sentence-transformers/all-MiniLM-L12-v2 --batch-size 512
"""

from __future__ import annotations

import argparse
import json
from typing import Optional, Sequence

import numpy as np
import pandas as pd

from pipeline_titles.common import CACHE_DIR, PREPARED, stage_timer

DEFAULT_MODEL = "sentence-transformers/all-mpnet-base-v2"
EMB_NPY = CACHE_DIR / "embeddings.npy"
EMB_INDEX = CACHE_DIR / "embeddings_index.parquet"
EMB_META = CACHE_DIR / "embeddings_meta.json"


def load_embeddings() -> tuple[np.ndarray, pd.Series]:
    """(embeddings float32 [n, d], Series title_norm -> row)."""
    emb = np.load(EMB_NPY).astype(np.float32)
    idx = pd.read_parquet(EMB_INDEX)
    return emb, pd.Series(idx["row"].to_numpy(), index=idx["title_norm"])


def main(argv: Optional[Sequence[str]] = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--model", default=DEFAULT_MODEL)
    ap.add_argument("--batch-size", type=int, default=256)
    ap.add_argument("--device", default=None, help="mps / cpu (default: auto)")
    ap.add_argument("--refresh", action="store_true", help="re-encode everything instead of reusing the cache")
    a = ap.parse_args(argv)
    import torch
    from sentence_transformers import SentenceTransformer
    device = a.device or ("mps" if torch.backends.mps.is_available() else "cpu")
    with stage_timer("stage1a_embed", model=a.model, device=device) as info:
        prepared = pd.read_parquet(PREPARED, columns=["title_norm", "is_dup"])
        uniq = sorted(set(prepared.loc[~prepared["is_dup"], "title_norm"]))
        cached: dict[str, np.ndarray] = {}
        if EMB_NPY.exists() and EMB_INDEX.exists() and EMB_META.exists() and not a.refresh \
                and json.loads(EMB_META.read_text()).get("model") == a.model:
            old_emb, old_idx = load_embeddings()
            cached = {t: old_emb[r] for t, r in old_idx.items()}
        todo = [t for t in uniq if t not in cached]
        print(f"{len(uniq)} unique titles; {len(uniq) - len(todo)} cached, encoding {len(todo)} with {a.model} on {device}", flush=True)
        new: dict[str, np.ndarray] = {}
        if todo:
            model = SentenceTransformer(a.model, device=device)
            step = 20000
            for i in range(0, len(todo), step):
                vecs = model.encode(todo[i:i + step], batch_size=a.batch_size, normalize_embeddings=True,
                                    convert_to_numpy=True, show_progress_bar=False)
                new.update(zip(todo[i:i + step], vecs))
                print(f"  encoded {min(i + step, len(todo))}/{len(todo)}", flush=True)
        emb = np.vstack([np.asarray(cached[t] if t in cached else new[t], dtype=np.float32) for t in uniq]).astype(np.float16)
        CACHE_DIR.mkdir(parents=True, exist_ok=True)
        np.save(EMB_NPY, emb)
        pd.DataFrame({"title_norm": uniq, "row": np.arange(len(uniq))}).to_parquet(EMB_INDEX, index=False)
        EMB_META.write_text(json.dumps({"model": a.model, "dim": int(emb.shape[1]), "n": int(emb.shape[0]),
                                        "normalized": True, "dtype": "float16"}, indent=2))
        info.update(n=int(emb.shape[0]), dim=int(emb.shape[1]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
