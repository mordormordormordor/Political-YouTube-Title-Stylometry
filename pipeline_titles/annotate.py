"""Stage 0c - spaCy annotation of every unique normalized title.

Runs en_core_web_sm (tagger, parser, NER) once over the unique `title_norm`
strings of titles_prepared.parquet and caches the result, so Stage 1 (entities per
topic), Stage 2 (POS-based style features, named-person / organization counts) and
Stage 4 (who gets named) never re-run the model.

ALL-CAPS titles ("TRUMP DESTROYS CNN") defeat the NER, so they are truecased first
with a lexicon learned from the corpus itself: a word is a proper noun if it is
capitalized in >= 80 % of its non-initial occurrences in mixed-case titles (>= 3
occurrences), and an acronym if it is ALL-CAPS in >= 80 % of them. The truecased
text is stored beside the annotations (`text_tc`); every feature that depends on
capitalization is computed from the original text, not from `text_tc`.

Output: data/titles/analysis/annotations.parquet, one row per unique title_norm:
    title_norm, text_tc, all_caps, tokens, lemmas (\\x1f-joined), pos, tag, dep,
    ent_iob (space-joined, one item per token), ents ('text\\x1elabel' \\x1f-joined),
    n_tokens, n_person, n_org, n_gpe, n_ents

CLI:
    python -m pipeline_titles.annotate            # all unique titles
    python -m pipeline_titles.annotate --limit 5000 --processes 4
"""

from __future__ import annotations

import argparse
import re
from collections import Counter
from typing import Iterable, Optional, Sequence

import pandas as pd

from pipeline_titles.common import ANNOTATIONS, PREPARED, stage_timer

SPACY_MODEL = "en_core_web_sm"
SEP = "\x1f"
ENT_SEP = "\x1e"
_WORD_RE = re.compile(r"[A-Za-z][A-Za-z'’]*")
_LETTERS_RE = re.compile(r"[A-Za-z]{2,}")


def is_all_caps(title: str, threshold: float = 0.6) -> bool:
    """True when more than `threshold` of the 2+-letter words are ALL-CAPS."""
    words = _LETTERS_RE.findall(title)
    return bool(words) and sum(w.isupper() for w in words) / len(words) > threshold


def build_case_lexicon(titles: Iterable[str], min_count: int = 3, min_share: float = 0.8) -> tuple[set, set]:
    """(proper_nouns, acronyms) learned from the non-initial words of mixed-case titles."""
    cap, low, acr = Counter(), Counter(), Counter()
    for t in titles:
        if is_all_caps(t):
            continue
        for i, w in enumerate(_WORD_RE.findall(t)):
            if i == 0 or len(w) < 2:
                continue
            k = w.lower()
            if w.isupper():
                acr[k] += 1
            elif w[0].isupper():
                cap[k] += 1
            else:
                low[k] += 1
    keys = set(cap) | set(low) | set(acr)
    proper = {k for k in keys if cap[k] >= min_count and cap[k] / (cap[k] + low[k] + acr[k]) >= min_share}
    acronyms = {k for k in keys if acr[k] >= min_count and acr[k] / (cap[k] + low[k] + acr[k]) >= min_share}
    return proper, acronyms


def truecase(title: str, proper: set, acronyms: set) -> str:
    """Lower-case an ALL-CAPS title, restoring learned proper nouns and acronyms
    and capitalizing the first word. Mixed-case titles are returned unchanged."""
    if not is_all_caps(title):
        return title

    def fix(m: re.Match) -> str:
        w = m.group(0)
        k = w.lower()
        if k in acronyms:
            return w.upper()
        if k in proper:
            return k[0].upper() + k[1:]
        return k

    t = _WORD_RE.sub(fix, title)
    m = _WORD_RE.search(t)
    if m:
        t = t[:m.start()] + t[m.start()].upper() + t[m.start() + 1:]
    return t


def annotate(texts: Sequence[str], originals: Sequence[str], all_caps: Sequence[bool],
             processes: int = 4, batch_size: int = 1000) -> pd.DataFrame:
    import spacy
    nlp = spacy.load(SPACY_MODEL)
    rows = []
    for i, doc in enumerate(nlp.pipe(texts, batch_size=batch_size, n_process=processes)):
        toks = [t.text for t in doc]
        ents = [(e.text, e.label_) for e in doc.ents]
        rows.append({
            "title_norm": originals[i], "text_tc": texts[i], "all_caps": bool(all_caps[i]),
            "tokens": SEP.join(toks), "lemmas": SEP.join(t.lemma_ for t in doc),
            "pos": " ".join(t.pos_ for t in doc), "tag": " ".join(t.tag_ for t in doc),
            "dep": " ".join(t.dep_ for t in doc), "ent_iob": " ".join((t.ent_iob_ + ("-" + t.ent_type_ if t.ent_type_ else "")) for t in doc),
            "ents": SEP.join(f"{e}{ENT_SEP}{l}" for e, l in ents),
            "n_tokens": len(toks), "n_person": sum(l == "PERSON" for _, l in ents),
            "n_org": sum(l == "ORG" for _, l in ents), "n_gpe": sum(l in ("GPE", "NORP", "LOC") for _, l in ents),
            "n_ents": len(ents),
        })
        if (i + 1) % 25000 == 0:
            print(f"  annotated {i + 1}/{len(texts)}", flush=True)
    return pd.DataFrame(rows)


def main(argv: Optional[Sequence[str]] = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--limit", type=int, default=None)
    ap.add_argument("--processes", type=int, default=4)
    ap.add_argument("--refresh", action="store_true", help="re-annotate everything instead of reusing the cache")
    a = ap.parse_args(argv)
    with stage_timer("stage0c_annotate", model=SPACY_MODEL) as info:
        prepared = pd.read_parquet(PREPARED, columns=["title_norm", "is_dup"])
        uniq = sorted(set(prepared.loc[~prepared["is_dup"], "title_norm"]))
        if a.limit:
            uniq = uniq[:a.limit]
        proper, acronyms = build_case_lexicon(uniq)
        old = pd.read_parquet(ANNOTATIONS) if ANNOTATIONS.exists() and not a.refresh else None
        done = set(old["title_norm"]) if old is not None else set()
        todo = [t for t in uniq if t not in done]
        caps = [is_all_caps(t) for t in todo]
        texts = [truecase(t, proper, acronyms) if c else t for t, c in zip(todo, caps)]
        print(f"unique titles {len(uniq)}, cached {len(uniq) - len(todo)}, annotating {len(todo)} "
              f"(all-caps {sum(caps)}, proper lexicon {len(proper)}, acronyms {len(acronyms)})", flush=True)
        df = annotate(texts, todo, caps, processes=a.processes) if todo else pd.DataFrame(columns=old.columns)
        if old is not None:
            df = pd.concat([old[old["title_norm"].isin(set(uniq))], df], ignore_index=True)
        df.to_parquet(ANNOTATIONS, index=False)
        info.update(titles=len(df), all_caps=int(sum(caps)), proper_lexicon=len(proper), acronyms=len(acronyms))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
