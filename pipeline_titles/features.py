"""Stage 2a - title-level style features, aggregated to creator x genre x month.

Reads titles_prepared.parquet, annotations.parquet and creators.csv. Writes:

    features_title.parquet     one row per video (all rows; repeats copy their unique
                               title's values): ~75 title-level features
    features.csv               creator x genre x month over UNIQUE titles: binary and
                               count features as rates per 100 titles (suffix _p100),
                               continuous features as means (suffix _mean), n_titles
    features_creator.csv       creator x genre over all months, plus repeat_share,
                               formulaicity, Heaps' exponent and Zipf slope at three
                               subsample sizes (20 repeats each, seed 20260914)
    lexical_diversity_sensitivity.csv   rank correlations of the Heaps'/Zipf values
                               across the three subsample sizes
    creator_templates.csv      the leading / trailing 3-gram templates each creator
                               re-uses most (entities and numbers masked)
    feature_definitions.csv    name, family, text it is computed on, definition, aggregation

Text used: lexical, pronoun, punctuation, syntax and entity features are computed on
the NORMALISED title (brand prefixes/suffixes, episode numbers and dates removed);
the raw-structure family (lead_colon_label, lead_live, pipe_segments_raw, ...) on
the RAW title, because a 'LIVE:' label or a '| Show Name' suffix is itself a style
choice. Humor is never lexicon-scored.

CLI:
    python -m pipeline_titles.features
    python -m pipeline_titles.features --no-diversity     # skip the 20x subsampling
"""

from __future__ import annotations

import argparse
import re
from collections import Counter
from statistics import mean
from typing import Optional, Sequence

import numpy as np
import pandas as pd

from pipeline_titles import lexicons as L
from pipeline_titles.common import (
    ANALYSIS_DIR, ANNOTATIONS, FEATURES_CREATOR, FEATURES_CSV, FEATURES_TITLE, LOW_N, SEED, STOPWORDS,
    load_creators, load_prepared, stage_timer,
)

WORD_RE = re.compile(r"[a-z0-9#@$%]+(?:['’][a-z]+)?")
ALPHA_RE = re.compile(r"[A-Za-z]+(?:['’][A-Za-z]+)?")
CONTRACTION_RE = re.compile(r"\b\w+(?:n['’]t|['’](?:re|ve|ll|d|m))\b|\b(?:it|that|what|he|she|there|here|who|let|where|how)['’]s\b", re.I)
NOMINAL_RE = re.compile(r"^[a-z]{3,}(?:tion|sion|ment|ness|ity|ance|ence|ism|ship|hood)s?$")
EMOJI_RE = re.compile("[\U0001F300-\U0001FAFF\U00002600-\U000027BF\U0001F1E6-\U0001F1FF\U00002B50\U00002B55\U0000203C\U00002049\U0000FE0F\U0001F900-\U0001F9FF\U0001F680-\U0001F6FF\U0001F004\U0001F0CF]")
LEAD_COLON_LABEL_RE = re.compile(r"^\s*[A-Z][A-Z0-9&'’.\- ]{1,28}:\s")
LEAD_BREAKING_RE = re.compile(r"^\s*[\W_]*(?:breaking|just in|developing|alert|urgent|bombshell|exclusive)\b", re.I)
LEAD_LIVE_RE = re.compile(r"^\s*[\W_]*(?:live|watch live|livestream|live stream|replay|live replay|watch)\b", re.I)
LEAD_WATCH_RE = re.compile(r"^\s*[\W_]*watch\b", re.I)
QUOTED_SPEECH_RE = re.compile(r"[\"“‘']([^\"”’']{3,}?\s[^\"”’']{2,}?)[\"”’']")
LISTICLE_RE = re.compile(L.LISTICLE_RE, re.I)
YEAR_RE = re.compile(r"\b(?:19|20)\d{2}\b")
DATE_RAW_RE = re.compile(r"\b\d{1,2}[/.]\d{1,2}[/.]\d{2,4}\b|\b20\d{2}-\d{2}-\d{2}\b|\b(?:jan|feb|mar|apr|may|jun|jul|aug|sep|sept|oct|nov|dec)[a-z]*\.?\s+\d{1,2}(?:st|nd|rd|th)?,?\s+20\d{2}\b", re.I)
EPISODE_RAW_RE = re.compile(r"\b(?:ep|episode)\.?\s*#?\s*\d+\b|#\d{2,5}\b", re.I)
FINITE_TAGS = {"VBZ", "VBD", "VBP", "MD"}
FIRST_TOKEN_IMPERATIVE_TAGS = {"VB"}

_PHRASE_CACHE: dict[str, re.Pattern] = {}


def _phrase_re(phrases: Sequence[str]) -> re.Pattern:
    key = "\x00".join(phrases)
    if key not in _PHRASE_CACHE:
        parts = []
        for p in phrases:
            p = p.strip()
            parts.append((r"\b" if p[0].isalnum() else "") + re.escape(p) + (r"\b" if p[-1].isalnum() else ""))
        _PHRASE_CACHE[key] = re.compile("|".join(parts), re.I)
    return _PHRASE_CACHE[key]


def _share(bools) -> float:
    b = list(bools)
    return float(np.mean(b)) if b else float("nan")


def parse_annotation(row) -> dict:
    """Annotation parquet row -> lists (tokens, pos, tag, dep, ent_iob, ents)."""
    toks = row["tokens"].split("\x1f") if row["tokens"] else []
    return {
        "tokens": toks, "pos": row["pos"].split() if row["pos"] else [], "tag": row["tag"].split() if row["tag"] else [],
        "dep": row["dep"].split() if row["dep"] else [], "ent_iob": row["ent_iob"].split() if row["ent_iob"] else [],
        "all_caps": bool(row["all_caps"]), "n_person": int(row["n_person"]), "n_org": int(row["n_org"]),
        "n_gpe": int(row["n_gpe"]), "n_ents": int(row["n_ents"]),
    }


def title_features(raw: str, norm: str, stripped: str, ann: dict, vader=None) -> dict:
    """All title-level features for one title (see the module docstring)."""
    low = norm.lower()
    words = WORD_RE.findall(low)
    alpha = ALPHA_RE.findall(norm)
    alpha2 = [w for w in alpha if len(w) >= 2]
    padded = " " + low + " "
    f: dict = {}
    # --- length ---
    f["n_chars"] = len(norm)
    f["n_tokens"] = len(words)
    f["mean_word_len"] = mean(len(w) for w in words) if words else 0.0
    f["n_chars_raw"] = len(raw)
    # --- case ---
    f["allcaps_word_share"] = _share(w.isupper() for w in alpha2) if alpha2 else 0.0
    f["has_allcaps_word"] = int(any(w.isupper() and len(w) >= 3 for w in alpha2))
    f["full_caps_title"] = int(ann["all_caps"])
    f["cap_token_share"] = _share(w[0].isupper() for w in alpha[1:]) if len(alpha) > 1 else float("nan")
    f["lowercase_start"] = int(bool(alpha) and alpha[0][0].islower())
    # --- punctuation ---
    f["q_mark"] = int("?" in norm)
    f["excl"] = int("!" in norm)
    f["multi_punct"] = int(bool(re.search(r"[!?]{2,}", norm)))
    f["colon"] = int(":" in norm)
    f["pipe"] = int("|" in norm)
    f["ellipsis"] = int(bool(re.search(r"\.{2,}|…", norm)))
    f["trailing_ellipsis"] = int(bool(re.search(r"(?:\.{2,}|…)\s*$", norm)))
    f["quotes"] = int(bool(re.search(r"[\"“”]|(?:^|\s)[‘'][^'’]{2,}[’'](?:\s|$|[,.!?])", norm)))
    f["brackets"] = int(bool(re.search(r"[\[\]()]", norm)))
    f["dash"] = int(bool(re.search(r"\s[-–—]\s|—", norm)))
    f["emoji_count"] = len(EMOJI_RE.findall(norm))
    f["emoji"] = int(f["emoji_count"] > 0)
    f["digit"] = int(bool(re.search(r"\d", norm)))
    f["dollar"] = int("$" in norm)
    f["percent"] = int("%" in norm)
    f["hashtag"] = int(bool(re.search(r"(?:^|\s)#[A-Za-z]", raw)))
    f["at_mention"] = int(bool(re.search(r"(?:^|\s)@\w", raw)))
    f["comma"] = int("," in norm)
    f["period_end"] = int(norm.rstrip().endswith(".") and not f["trailing_ellipsis"])
    f["year_mention"] = int(bool(YEAR_RE.search(norm)))
    # --- pronouns, contractions, imperatives, questions ---
    f["first_sg"] = int(any(w in L.FIRST_SG for w in words))
    f["first_pl"] = int(any(w in L.FIRST_PL for w in words))
    f["second_person"] = int(any(w in L.SECOND for w in words))
    f["contraction"] = len(CONTRACTION_RE.findall(norm))
    first = words[0] if words else ""
    tag0 = ann["tag"][0] if ann["tag"] else ""
    pos0 = ann["pos"][0] if ann["pos"] else ""
    f["imperative"] = int(first in L.IMPERATIVE_START or (tag0 in FIRST_TOKEN_IMPERATIVE_TAGS and pos0 == "VERB"))
    f["q_word_start"] = int(first in L.QUESTION_START)
    f["wh_any"] = int(any(w in L.WH_WORDS for w in words))
    # --- lexicon families ---
    f["intensifier"] = sum(w in L.INTENSIFIERS for w in words)
    f["superlative"] = sum(w in L.SUPERLATIVES for w in words) + sum(t in ("JJS", "RBS") for t in ann["tag"])
    f["shock_word"] = sum(w in L.SHOCK_WORDS for w in words)
    f["pos_eval"] = sum(w in L.POS_EVAL for w in words)
    f["neg_eval"] = sum(w in L.NEG_EVAL for w in words)
    f["negation"] = int(any(w in L.NEGATION for w in words))
    f["violence_verb"] = sum(w in L.VIOLENCE_VERBS for w in words) + len(_phrase_re(L.VIOLENCE_PHRASES).findall(low))
    f["hedge"] = int(any(w in L.HEDGES for w in words))
    f["discourse_marker"] = int(any(w in L.DISCOURSE for w in words))
    f["nominalisation"] = sum(bool(NOMINAL_RE.match(w)) for w in words)
    # --- entities ---
    f["n_person"] = ann["n_person"]
    f["n_org"] = ann["n_org"]
    f["n_gpe"] = ann["n_gpe"]
    f["has_person"] = int(ann["n_person"] > 0)
    f["entity_first"] = int(bool(ann["ent_iob"]) and ann["ent_iob"][0].startswith("B"))
    # --- markers ---
    f["how_to"] = int(bool(_phrase_re(L.HOWTO_PHRASES).search(low)))
    f["explainer"] = int(bool(_phrase_re(L.EXPLAINER_PHRASES).search(low)))
    f["why_marker"] = int(first == "why" or " reason " in padded or "reason why" in low)
    f["curiosity_lex"] = int(bool(_phrase_re(L.CURIOSITY_PHRASES).search(low)))
    f["fwd_ref_start"] = int(first in L.FORWARD_REF_START and ann["n_ents"] == 0)
    f["listicle"] = int(bool(LISTICLE_RE.search(norm)))
    f["reaction_lex"] = int(bool(_phrase_re(L.REACTION_PHRASES).search(low)))
    f["interview_lex"] = int(bool(_phrase_re(L.INTERVIEW_PHRASES).search(padded)))
    f["confrontation_lex"] = int(bool(_phrase_re(L.CONFRONTATION_PHRASES).search(padded)))
    # --- raw structure ---
    f["lead_colon_label"] = int(bool(LEAD_COLON_LABEL_RE.match(raw)))
    f["lead_breaking"] = int(bool(LEAD_BREAKING_RE.match(raw)))
    f["lead_live"] = int(bool(LEAD_LIVE_RE.match(raw)))
    f["pipe_segments_raw"] = raw.count("|") + 1 if "|" in raw else 1
    f["colon_segments_raw"] = raw.count(":")
    f["brackets_raw"] = int(bool(re.search(r"[\[\]()]", raw)))
    f["brand_stripped"] = int(bool(stripped))
    f["episode_raw"] = int(bool(EPISODE_RAW_RE.search(raw)))
    f["date_raw"] = int(bool(DATE_RAW_RE.search(raw)))
    f["quoted_speech"] = int(bool(QUOTED_SPEECH_RE.search(norm)))
    # --- syntax (spaCy) ---
    tags, pos = ann["tag"], ann["pos"]
    n = max(len(pos), 1)
    f["has_finite_verb"] = int(any(t in FINITE_TAGS for t in tags))
    f["past_tense"] = int("VBD" in tags or "VBN" in tags)
    f["present_tense"] = int("VBZ" in tags or "VBP" in tags)
    f["modal"] = int("MD" in tags)
    f["future_will"] = int(any(w in ("will", "gonna", "'ll", "’ll") for w in words))
    f["det_share"] = sum(p == "DET" for p in pos) / n
    f["stopword_share"] = sum(w in STOPWORDS for w in words) / max(len(words), 1)
    f["propn_share"] = sum(p == "PROPN" for p in pos) / n
    f["noun_share"] = sum(p == "NOUN" for p in pos) / n
    f["verb_share"] = sum(p in ("VERB", "AUX") for p in pos) / n
    f["adj_share"] = sum(p == "ADJ" for p in pos) / n
    f["adv_share"] = sum(p == "ADV" for p in pos) / n
    f["num_share"] = sum(p == "NUM" for p in pos) / n
    # --- sentiment ---
    if vader is not None:
        s = vader.polarity_scores(norm)
        f["vader_neg"], f["vader_pos"], f["vader_compound"] = s["neg"], s["pos"], s["compound"]
    return f


BINARY_OR_COUNT = {
    "has_allcaps_word", "full_caps_title", "lowercase_start", "q_mark", "excl", "multi_punct", "colon", "pipe", "ellipsis",
    "trailing_ellipsis", "quotes", "brackets", "dash", "emoji_count", "emoji", "digit", "dollar", "percent", "hashtag",
    "at_mention", "comma", "period_end", "year_mention", "first_sg", "first_pl", "second_person", "contraction",
    "imperative", "q_word_start", "wh_any", "intensifier", "superlative", "shock_word", "pos_eval", "neg_eval", "negation",
    "violence_verb", "hedge", "discourse_marker", "nominalisation", "n_person", "n_org", "n_gpe", "has_person",
    "entity_first", "how_to", "explainer", "why_marker", "curiosity_lex", "fwd_ref_start", "listicle", "reaction_lex",
    "interview_lex", "confrontation_lex", "lead_colon_label", "lead_breaking", "lead_live", "brackets_raw",
    "brand_stripped", "episode_raw", "date_raw", "quoted_speech", "has_finite_verb", "past_tense", "present_tense",
    "modal", "future_will", "formulaic",
}
CONTINUOUS = {"n_chars", "n_tokens", "mean_word_len", "n_chars_raw", "allcaps_word_share", "cap_token_share",
              "pipe_segments_raw", "colon_segments_raw", "det_share", "stopword_share", "propn_share", "noun_share",
              "verb_share", "adj_share", "adv_share", "num_share", "vader_neg", "vader_pos", "vader_compound"}


# --------------------------------------------------------------------------- #
# Creator-level: formulaicity, Heaps' law, Zipf
# --------------------------------------------------------------------------- #
def mask_tokens(tokens: Sequence[str], ent_iob: Sequence[str]) -> list[str]:
    """Lower-case tokens with entities -> <ENT> (one per entity span) and numbers -> #."""
    out = []
    for i, t in enumerate(tokens):
        iob = ent_iob[i] if i < len(ent_iob) else "O"
        if iob.startswith("B"):
            out.append("<ENT>")
        elif iob.startswith("I"):
            continue
        elif re.fullmatch(r"[\d.,%$#]+", t):
            out.append("#")
        else:
            out.append(t.lower())
    return out


def template_keys(masked: Sequence[str], n: int = 3) -> tuple[Optional[str], Optional[str]]:
    """(leading n-gram, trailing n-gram) of a masked token list, or None when shorter than n."""
    if len(masked) < n:
        return None, None
    return " ".join(masked[:n]), " ".join(masked[-n:])


def formulaic_flags(lead: Sequence[Optional[str]], trail: Sequence[Optional[str]], min_others: int = 3) -> list[int]:
    """1 when a title's leading or trailing template is used by >= min_others other titles of the group."""
    cl, ct = Counter(k for k in lead if k), Counter(k for k in trail if k)
    return [int((l is not None and cl[l] - 1 >= min_others) or (t is not None and ct[t] - 1 >= min_others))
            for l, t in zip(lead, trail)]


def heaps_zipf(token_lists: Sequence[Sequence[str]], n_tokens: int, repeats: int = 20,
               seed: int = SEED) -> tuple[float, float, float, float]:
    """Heaps' exponent and Zipf exponent on `repeats` random subsamples of exactly
    n_tokens tokens (titles drawn without replacement, in random order, truncated).
    Returns (heaps_mean, heaps_sd, zipf_mean, zipf_sd); NaNs when the group holds
    fewer than n_tokens tokens."""
    total = sum(len(t) for t in token_lists)
    if total < n_tokens or n_tokens < 200:
        return (float("nan"),) * 4
    rng = np.random.RandomState(seed)
    checkpoints = np.unique(np.geomspace(50, n_tokens, 20).astype(int))
    betas, zipfs = [], []
    for _ in range(repeats):
        seq: list[str] = []
        for i in rng.permutation(len(token_lists)):
            seq.extend(token_lists[i])
            if len(seq) >= n_tokens:
                break
        seq = seq[:n_tokens]
        seen, growth, ci = set(), [], 0
        for k, tok in enumerate(seq, start=1):
            seen.add(tok)
            if ci < len(checkpoints) and k == checkpoints[ci]:
                growth.append(len(seen)); ci += 1
        betas.append(np.polyfit(np.log(checkpoints[:len(growth)]), np.log(growth), 1)[0])
        freqs = np.array(sorted(Counter(seq).values(), reverse=True), dtype=float)
        freqs = freqs[freqs >= 2]
        if len(freqs) >= 10:
            zipfs.append(-np.polyfit(np.log(np.arange(1, len(freqs) + 1)), np.log(freqs), 1)[0])
    return (float(np.mean(betas)), float(np.std(betas)),
            float(np.mean(zipfs)) if zipfs else float("nan"), float(np.std(zipfs)) if zipfs else float("nan"))


def diversity_tokens(norm: str) -> list[str]:
    return re.findall(r"[a-z0-9']+", norm.lower())


# --------------------------------------------------------------------------- #
def aggregate(tf: pd.DataFrame, keys: list[str]) -> pd.DataFrame:
    cols = [c for c in tf.columns if c in BINARY_OR_COUNT or c in CONTINUOUS]
    g = tf.groupby(keys, sort=True)
    out = g[cols].mean()
    for c in cols:
        if c in BINARY_OR_COUNT:
            out[c] = out[c] * 100.0
    out.columns = [c + ("_p100" if c in BINARY_OR_COUNT else "_mean") for c in cols]
    out.insert(0, "n_titles", g.size())
    return out.reset_index()


def feature_definitions() -> pd.DataFrame:
    fam = {}
    for c in ["n_chars", "n_tokens", "mean_word_len", "n_chars_raw"]: fam[c] = ("length", "norm" if c != "n_chars_raw" else "raw")
    for c in ["allcaps_word_share", "has_allcaps_word", "full_caps_title", "cap_token_share", "lowercase_start"]: fam[c] = ("case", "norm")
    for c in ["q_mark", "excl", "multi_punct", "colon", "pipe", "ellipsis", "trailing_ellipsis", "quotes", "brackets", "dash", "emoji_count", "emoji", "digit", "dollar", "percent", "comma", "period_end", "year_mention"]: fam[c] = ("punctuation", "norm")
    for c in ["hashtag", "at_mention"]: fam[c] = ("punctuation", "raw")
    for c in ["first_sg", "first_pl", "second_person", "contraction", "imperative", "q_word_start", "wh_any"]: fam[c] = ("address", "norm")
    for c in ["intensifier", "superlative", "shock_word", "pos_eval", "neg_eval", "negation", "violence_verb", "hedge", "discourse_marker", "nominalisation"]: fam[c] = ("lexicon", "norm")
    for c in ["n_person", "n_org", "n_gpe", "has_person", "entity_first"]: fam[c] = ("entities", "norm (truecased for NER)")
    for c in ["how_to", "explainer", "why_marker", "curiosity_lex", "fwd_ref_start", "listicle", "reaction_lex", "interview_lex", "confrontation_lex"]: fam[c] = ("markers", "norm")
    for c in ["lead_colon_label", "lead_breaking", "lead_live", "pipe_segments_raw", "colon_segments_raw", "brackets_raw", "brand_stripped", "episode_raw", "date_raw"]: fam[c] = ("raw_structure", "raw")
    fam["quoted_speech"] = ("raw_structure", "norm")
    for c in ["has_finite_verb", "past_tense", "present_tense", "modal", "future_will", "det_share", "stopword_share", "propn_share", "noun_share", "verb_share", "adj_share", "adv_share", "num_share"]: fam[c] = ("syntax", "norm (spaCy en_core_web_sm)")
    for c in ["vader_neg", "vader_pos", "vader_compound"]: fam[c] = ("sentiment", "norm (VADER)")
    fam["formulaic"] = ("formulaicity", "norm (entities/numbers masked)")
    defs = {
        "n_chars": "characters", "n_tokens": "word tokens", "mean_word_len": "mean characters per word token", "n_chars_raw": "characters of the raw title",
        "allcaps_word_share": "share of 2+-letter words in ALL CAPS", "has_allcaps_word": "any 3+-letter ALL-CAPS word", "full_caps_title": ">60% of words ALL CAPS",
        "cap_token_share": "share of non-initial words starting upper-case (title-case tendency)", "lowercase_start": "first letter lower-case",
        "q_mark": "contains ?", "excl": "contains !", "multi_punct": "!! ?? ?! runs", "colon": "contains :", "pipe": "contains | (after brand stripping)", "ellipsis": ".. ... or …", "trailing_ellipsis": "ends with an ellipsis",
        "quotes": "double or paired single quotes", "brackets": "( ) [ ]", "dash": "spaced dash or em dash", "emoji_count": "emoji characters", "emoji": "any emoji", "digit": "any digit", "dollar": "$", "percent": "%", "hashtag": "#tag (raw)", "at_mention": "@handle (raw)", "comma": ",", "period_end": "ends with a full stop", "year_mention": "a 19xx/20xx year",
        "first_sg": "I / me / my ...", "first_pl": "we / us / our / let's", "second_person": "you / your ...", "contraction": "count of n't / 're / 've / 'll / 'd / 'm / it's-type contractions",
        "imperative": "first word in the imperative lexicon or a base-form verb", "q_word_start": "starts with a question word or auxiliary", "wh_any": "any wh-word",
        "intensifier": "count, lexicons.INTENSIFIERS", "superlative": "count, lexicons.SUPERLATIVES + JJS/RBS tags", "shock_word": "count, lexicons.SHOCK_WORDS", "pos_eval": "count, lexicons.POS_EVAL", "neg_eval": "count, lexicons.NEG_EVAL", "negation": "any word in lexicons.NEGATION",
        "violence_verb": "count, lexicons.VIOLENCE_VERBS + VIOLENCE_PHRASES (slams, destroys, exposed ...)", "hedge": "any word in lexicons.HEDGES", "discourse_marker": "any word in lexicons.DISCOURSE (let's, chat, okay, lol ...)", "nominalisation": "count of -tion/-sion/-ment/-ness/-ity/-ance/-ence/-ism/-ship/-hood words (7+ letters)",
        "n_person": "PERSON entities", "n_org": "ORG entities", "n_gpe": "GPE/NORP/LOC entities", "has_person": "any PERSON entity", "entity_first": "title starts with a named entity",
        "how_to": "'how to' / 'how I/we/you'", "explainer": "explained / explainer / breakdown / what is / the truth about ...", "why_marker": "starts with why, or 'reason'", "curiosity_lex": "lexicons.CURIOSITY_PHRASES (here's why, you won't believe, this is insane ...)", "fwd_ref_start": "starts with this/he/they/... and names no entity", "listicle": "N things/reasons/ways ...", "reaction_lex": "reacts to / responds to / reaction", "interview_lex": "with / w/ / ft. / joins / interview", "confrontation_lex": "vs / debate / destroys / owns / clash ...",
        "lead_colon_label": "leading ALL-CAPS label followed by a colon (BREAKING:, LIVE:)", "lead_breaking": "starts with BREAKING / JUST IN / DEVELOPING / ALERT / URGENT / EXCLUSIVE", "lead_live": "starts with LIVE / WATCH / REPLAY", "pipe_segments_raw": "number of |-separated segments of the raw title", "colon_segments_raw": "colons in the raw title", "brackets_raw": "brackets in the raw title", "brand_stripped": "a brand/episode/date pattern was stripped from this title", "episode_raw": "episode number in the raw title", "date_raw": "date stamp in the raw title", "quoted_speech": "a quoted span of 2+ words",
        "has_finite_verb": "any VBZ/VBD/VBP/MD (clause vs. noun-phrase title)", "past_tense": "VBD/VBN", "present_tense": "VBZ/VBP", "modal": "MD", "future_will": "will / gonna / 'll", "det_share": "share of DET tokens", "stopword_share": "share of tokens in the stopword list", "propn_share": "share PROPN", "noun_share": "share NOUN", "verb_share": "share VERB+AUX", "adj_share": "share ADJ", "adv_share": "share ADV", "num_share": "share NUM",
        "vader_neg": "VADER negative", "vader_pos": "VADER positive", "vader_compound": "VADER compound", "formulaic": "leading or trailing 3-gram template shared with >= 3 other titles of the same creator x genre",
    }
    rows = []
    for c, (family, text) in fam.items():
        agg = "rate per 100 titles (_p100)" if c in BINARY_OR_COUNT else "mean (_mean)"
        rows.append({"feature": c, "family": family, "text": text, "definition": defs.get(c, ""), "aggregation": agg})
    return pd.DataFrame(rows)


def run(do_diversity: bool = True) -> None:
    from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
    vader = SentimentIntensityAnalyzer()
    prepared = load_prepared()
    creators = load_creators()[["creator", "group", "organisation", "clipper"]]
    ann_df = pd.read_parquet(ANNOTATIONS).set_index("title_norm")
    uniq = prepared[~prepared["is_dup"]].copy()
    print(f"extracting features for {len(uniq)} unique titles", flush=True)

    # title-level features on unique (creator, genre, title) rows
    ann_cache: dict[str, dict] = {}
    feats = []
    for i, r in enumerate(uniq.itertuples(index=False)):
        a = ann_cache.get(r.title_norm)
        if a is None:
            a = parse_annotation(ann_df.loc[r.title_norm]) if r.title_norm in ann_df.index else \
                {"tokens": [], "pos": [], "tag": [], "dep": [], "ent_iob": [], "all_caps": False, "n_person": 0, "n_org": 0, "n_gpe": 0, "n_ents": 0}
            ann_cache[r.title_norm] = a
        f = title_features(r.title_raw, r.title_norm, r.stripped, a, vader)
        masked = mask_tokens(a["tokens"], a["ent_iob"])
        f["_lead"], f["_trail"] = template_keys(masked)
        f["row_id"] = r.row_id
        feats.append(f)
        if (i + 1) % 50000 == 0:
            print(f"  {i + 1}/{len(uniq)}", flush=True)
    tf = pd.DataFrame(feats)
    tf = uniq[["row_id", "creator", "platform", "genre", "month", "title_norm"]].merge(tf, on="row_id")

    # formulaicity within creator x genre
    tf["formulaic"] = 0
    template_rows = []
    for (creator, genre), g in tf.groupby(["creator", "genre"], sort=True):
        flags = formulaic_flags(g["_lead"].tolist(), g["_trail"].tolist())
        tf.loc[g.index, "formulaic"] = flags
        for kind, col in (("leading", "_lead"), ("trailing", "_trail")):
            for key, n in Counter(k for k in g[col] if k).most_common(5):
                if n >= 4:
                    template_rows.append({"creator": creator, "genre": genre, "kind": kind, "template": key, "n_titles": n,
                                          "share": round(n / len(g), 4)})
    pd.DataFrame(template_rows).to_csv(ANALYSIS_DIR / "creator_templates.csv", index=False)
    tf = tf.drop(columns=["_lead", "_trail"])

    # propagate to duplicates and save title-level table
    key_cols = ["creator", "genre", "title_norm"]
    feat_cols = [c for c in tf.columns if c not in key_cols + ["row_id", "platform", "month"]]
    all_rows = prepared[["row_id", "creator", "genre", "title_norm", "is_dup", "month", "platform"]].merge(
        tf[key_cols + feat_cols].drop_duplicates(key_cols), on=key_cols, how="left")
    all_rows.to_parquet(FEATURES_TITLE, index=False)

    # aggregation over unique titles
    monthly = aggregate(tf, ["creator", "genre", "month"])
    monthly = monthly.merge(creators, on="creator", how="left")
    monthly.to_csv(FEATURES_CSV, index=False)
    creator = aggregate(tf, ["creator", "genre"])
    summ = pd.read_csv(ANALYSIS_DIR / "creator_genre_summary.csv")[["creator", "genre", "n_rows", "n_unique", "repeat_share", "low_n"]]
    creator = creator.merge(summ, on=["creator", "genre"], how="left").merge(creators, on="creator", how="left")

    # lexical diversity
    if do_diversity:
        rows = []
        for (c, g), grp in tf.groupby(["creator", "genre"], sort=True):
            toks = [diversity_tokens(t) for t in grp["title_norm"]]
            rec = {"creator": c, "genre": g, "n_tokens_total": sum(len(t) for t in toks)}
            for n in (1000, 1500, 3000):
                hb, hs, zb, zs = heaps_zipf(toks, n)
                rec.update({f"heaps_beta_{n}": hb, f"heaps_sd_{n}": hs, f"zipf_{n}": zb, f"zipf_sd_{n}": zs})
            rows.append(rec)
        div = pd.DataFrame(rows)
        creator = creator.merge(div, on=["creator", "genre"], how="left")
        sens = []
        for a_, b_ in ((1000, 1500), (1500, 3000), (1000, 3000)):
            for m in ("heaps_beta", "zipf"):
                sub = div[[f"{m}_{a_}", f"{m}_{b_}"]].dropna()
                sens.append({"measure": m, "n_a": a_, "n_b": b_, "n_groups": len(sub),
                             "spearman": round(sub.iloc[:, 0].corr(sub.iloc[:, 1], method="spearman"), 4),
                             "mean_a": round(sub.iloc[:, 0].mean(), 4), "mean_b": round(sub.iloc[:, 1].mean(), 4)})
        pd.DataFrame(sens).to_csv(ANALYSIS_DIR / "lexical_diversity_sensitivity.csv", index=False)
    creator.to_csv(FEATURES_CREATOR, index=False)
    feature_definitions().to_csv(ANALYSIS_DIR / "feature_definitions.csv", index=False)
    print(f"features: {len(feat_cols)} title-level columns; monthly cells {len(monthly)}; creator x genre rows {len(creator)}")


def main(argv: Optional[Sequence[str]] = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--no-diversity", action="store_true")
    a = ap.parse_args(argv)
    with stage_timer("stage2a_features"):
        run(do_diversity=not a.no_diversity)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
