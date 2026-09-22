"""Stage 6c - the year in words (site article No. 3): what the titles say, month
by month and week by week, counted so that no channel's output outweighs
another's.

Every count here is over unique titles (repeats dropped) and, wherever a share
is averaged, channel-weighted: a word's share is the mean over channels of the
share of the channel's titles that contain it, so the ten largest channels,
which publish four titles in ten, weigh the same as any other. Content words
are textstats.vocab_tokens of the normalized title (brand tags, show names and
episode numbers stripped; stopwords dropped; possessives folded), except that a
pair of adjacent content words bound to each other (a name: "lindsey graham",
"dolly parton") is one term: a pair that appears in BIGRAM_MIN_TITLES titles
from BIGRAM_MIN_CHANNELS channels and accounts for at least BIGRAM_MIN_BOUND of
each of its words' own titles (year_bigrams.csv). In a title that carries the
pair, the pair replaces its two words; elsewhere each word counts on its own.
The shouted counts use the capitalization rule's own test on the raw title
(three or more letters written in capitals, neither a learned acronym, a
generic label nor one of the channel's own tag words), a word once per title;
a pair is shouted when both its words are.

Outputs (data/titles/analysis/):
    year_words.csv       the VOCAB most frequent content words by channel-weighted
                         share: channels using it, titles, share_mean, share_pooled,
                         and the shout numbers (shouted titles, mixed-case titles it
                         appears in, rate, channels shouting it; `exempt` marks a word
                         the rule never counts, a learned acronym or a generic label)
    year_months.csv      per month, the MONTH_TOP words that stand out against the
                         rest of the year by weighted log-odds (Monroe, Colaresi &
                         Quinn 2008, informative Dirichlet prior, alpha0 = 500) over
                         channel-months: a word's count for a month is how many
                         channels used it that month, so a super-uploader counts
                         once; each with the month's most-viewed title that carries
                         the word and the month's standout that travels with it most
                         (example_with), else the most-viewed title that carries the
                         word at all
    year_weeks_meta.csv  every week, Monday-keyed: titles, channels with WEEK_MIN or
                         more titles, partial (runs past the corpus window)
    year_weeks.csv       the vocabulary's channel-weighted share by week (over the
                         channels with WEEK_MIN or more titles that week)
    year_bigrams.csv     the pairs counted as one term: pair, titles, channels, and the
                         share of each word's titles the pair accounts for
    year_word_weeks.csv  every vocabulary word in every week it appears: share, channels,
                         titles, the week's most-viewed title carrying it (plain_*) and the
                         one carrying it with its companion (example_*, see the spikes)
    year_week_spikes.csv per week, the WEEK_TOP words furthest above their own average
                         that week (rank, share, baseline, delta, channels)
    year_spikes.csv      the SPIKES words whose weekly share departed furthest above
                         their own average over the full weeks, with the peak week,
                         the baseline, the departure, and that week's most-viewed
                         title that carries the word and the word spiking that week
                         (its share CO_SPIKE_MIN above its own average) that travels
                         with it most (example_with names it), else the most-viewed
                         title that carries the word at all: for a word as common
                         as "trump" the most-viewed title alone says nothing about
                         the spike

CLI:
    python -m pipeline_titles.year
"""

from __future__ import annotations

import argparse
import re
from collections import Counter
from datetime import date, timedelta
from typing import Optional, Sequence

import numpy as np
import pandas as pd

from pipeline_titles.annotate import build_case_lexicon
from pipeline_titles.common import ANALYSIS_DIR, WINDOW_FROM, WINDOW_TO, load_prepared, stage_timer
from pipeline_titles.profiles import tag_words
from pipeline_titles.textstats import _TOKEN_RE, CAPS_LABELS, VOCAB_STOP, shouted_words, weighted_log_odds

VOCAB = 400
BIGRAM_MIN_TITLES = 50
BIGRAM_MIN_CHANNELS = 10
BIGRAM_MIN_BOUND = 0.5
MONTH_TOP = 12
MONTH_MIN_CHANNELS = 5
WEEK_MIN = 5
SPIKES = 40
SPIKE_MIN_CHANNELS = 10
WEEK_TOP = 20
# A word is spiking in a week when its share is this far above its own average: the example title must carry one such word beside the spike's.
CO_SPIKE_MIN = 0.02
ALPHA0 = 500.0


def week_of(published: str) -> str:
    """The Monday that starts the week of a YYYY-MM-DD date."""
    d = date.fromisoformat(published)
    return (d - timedelta(days=d.weekday())).isoformat()


def content_tokens(text: str) -> list[tuple[str, bool]]:
    """The title's tokens in order, each with whether it is a content word (vocab_tokens's rule: two or more letters, not a stopword), possessives folded."""
    out = []
    for t in _TOKEN_RE.findall(str(text).lower().replace("\u2019", "'")):
        if t.endswith("'s"):
            t = t[:-2]
        out.append((t, len(t) >= 2 and t not in VOCAB_STOP))
    return out


def adjacent_pairs(tokens: list[tuple[str, bool]]) -> set[str]:
    """Every pair of adjacent content words in the title, as "a b"."""
    return {f"{a} {b}" for (a, ca), (b, cb) in zip(tokens, tokens[1:]) if ca and cb}


def find_collocations(token_lists: list[list[tuple[str, bool]]], creators: list[str],
                      min_titles: int = BIGRAM_MIN_TITLES, min_channels: int = BIGRAM_MIN_CHANNELS, min_bound: float = BIGRAM_MIN_BOUND) -> pd.DataFrame:
    """The adjacent pairs bound to each other: in `min_titles` titles from `min_channels` channels, and at least `min_bound` of each word's own titles."""
    word_titles: Counter = Counter()
    pair_titles: Counter = Counter()
    pair_channels: dict[str, set[str]] = {}
    for tokens, creator in zip(token_lists, creators):
        for w in {t for t, c in tokens if c}:
            word_titles[w] += 1
        for p in adjacent_pairs(tokens):
            pair_titles[p] += 1
            pair_channels.setdefault(p, set()).add(creator)
    rows = []
    for p, n in pair_titles.items():
        if n < min_titles or len(pair_channels[p]) < min_channels:
            continue
        a, b = p.split(" ")
        bound_a, bound_b = n / word_titles[a], n / word_titles[b]
        if bound_a >= min_bound and bound_b >= min_bound:
            rows.append({"pair": p, "titles": n, "channels": len(pair_channels[p]), "bound_first": round(bound_a, 4), "bound_second": round(bound_b, 4)})
    return pd.DataFrame(rows, columns=["pair", "titles", "channels", "bound_first", "bound_second"]).sort_values("titles", ascending=False).reset_index(drop=True)


def terms_of(tokens: list[tuple[str, bool]], collocations: set[str]) -> set[str]:
    """A title's terms: its content words, with each collocation it carries standing in for its two words."""
    words = {t for t, c in tokens if c}
    pairs = adjacent_pairs(tokens) & collocations
    for p in pairs:
        a, b = p.split(" ")
        words.discard(a)
        words.discard(b)
    return words | pairs


EXAMPLE_COLUMNS = ["example_creator", "example_title", "example_video", "example_url", "example_views", "example_with",
                   "plain_creator", "plain_title", "plain_video", "plain_url", "plain_views"]


def pick_examples(uniq: pd.DataFrame, hits: pd.DataFrame, by: str, wanted: list[tuple[str, str]], companions: dict[tuple[str, str], list[str]],
                  terms_by_row: dict[int, set[str]]) -> pd.DataFrame:
    """For each (period, word) in `wanted`, two titles. plain_*: the period's most-viewed title that carries the word. example_*: the most-viewed
    title that carries the word and its closest companion: of the `companions` (the other words standing out or spiking in that period,
    strongest first), the one that travels with the word most, in the most of the period's titles carrying the word (ties to the stronger);
    `example_with` names it. With no companion found, example_* is the plain title and example_with is empty."""
    h = hits.merge(uniq[["row_id", by, "creator", "title_raw", "video_id", "url", "view_count"]], on="row_id")
    h = h.sort_values(["view_count", "row_id"], ascending=[False, True], na_position="last")
    groups = {k: g for k, g in h.groupby([by, "word"], sort=False)}
    rows = []
    for period, word in wanted:
        g = groups.get((period, word))
        if g is None or g.empty:
            rows.append({by: period, "word": word, **{c: None for c in EXAMPLE_COLUMNS}})
            continue
        pick, matched = None, ""
        order = companions.get((period, word), [])
        together = Counter()
        for rid in g["row_id"]:
            together.update(terms_by_row.get(int(rid), set()).intersection(order))
        if together:
            matched = max(order, key=lambda w: (together.get(w, 0), -order.index(w)))
            pick = next(rid for rid in g["row_id"] if matched in terms_by_row.get(int(rid), set()))
        r = g[g["row_id"] == pick].iloc[0] if pick is not None else g.iloc[0]
        p0 = g.iloc[0]
        rows.append({by: period, "word": word, "example_creator": r["creator"], "example_title": r["title_raw"], "example_video": r["video_id"],
                     "example_url": r["url"], "example_views": r["view_count"], "example_with": matched,
                     "plain_creator": p0["creator"], "plain_title": p0["title_raw"], "plain_video": p0["video_id"], "plain_url": p0["url"], "plain_views": p0["view_count"]})
    return pd.DataFrame(rows, columns=[by, "word"] + EXAMPLE_COLUMNS)


def run(info: dict) -> None:
    prepared = load_prepared()
    uniq = prepared[~prepared["is_dup"]].copy()
    uniq["week"] = uniq["published"].map(week_of)
    n_channels = uniq["creator"].nunique()
    n_titles = len(uniq)
    channel_titles = uniq.groupby("creator").size()

    # ---- (row_id, word) for every term of the normalized title, once per title; a bound pair is one term ----
    token_lists = [content_tokens(t) for t in uniq["title_norm"]]
    bigrams = find_collocations(token_lists, uniq["creator"].tolist())
    bigrams.to_csv(ANALYSIS_DIR / "year_bigrams.csv", index=False)
    collocations = set(bigrams["pair"])
    title_terms = [terms_of(tokens, collocations) for tokens in token_lists]
    hits = pd.DataFrame(
        [(rid, w) for rid, terms in zip(uniq["row_id"], title_terms) for w in terms],
        columns=["row_id", "word"],
    )
    hits = hits.merge(uniq[["row_id", "creator", "month", "week"]], on="row_id")
    terms_by_row = dict(zip((int(r) for r in uniq["row_id"]), title_terms))

    # ---- the vocabulary: channel-weighted share, pooled share, and the shout numbers from the raw title ----
    per_channel = hits.groupby(["word", "creator"]).size().rename("n").reset_index()
    per_channel["share"] = per_channel["n"] / per_channel["creator"].map(channel_titles)
    share_mean = per_channel.groupby("word")["share"].sum() / n_channels        # channels without the word contribute 0
    words = pd.DataFrame({
        "share_mean": share_mean,
        "channels": per_channel.groupby("word")["creator"].nunique(),
        "n_titles": hits.groupby("word").size(),
    })
    words["share_pooled"] = words["n_titles"] / n_titles
    words = words.sort_values(["share_mean", "n_titles"], ascending=False).head(VOCAB)
    words.index.name = "word"
    words = words.reset_index()
    words["rank"] = np.arange(1, len(words) + 1)

    _, acronyms = build_case_lexicon(uniq["title_raw"].drop_duplicates())
    own_tags: dict[str, set[str]] = {}
    for (creator, genre), g in uniq.groupby(["creator", "genre"]):
        own_tags.setdefault(creator, set()).update(w["word"] for w in tag_words(g["title_raw"].tolist()))
    shouted = Counter()
    mentioned = Counter()
    shouting_channels: dict[str, set[str]] = {}
    for creator, raw, terms in zip(uniq["creator"], uniq["title_raw"], title_terms):
        s, m = shouted_words(raw, acronyms, own_tags.get(creator, ()))
        mentioned.update(m)
        shouted.update(s)
        for w in s:
            shouting_channels.setdefault(w, set()).add(creator)
        # a bound pair is mentioned when both its words are, and shouted when both are shouted
        for term in terms:
            if " " in term:
                a, b = term.split(" ")
                if a in m and b in m:
                    mentioned[term] += 1
                if a in s and b in s:
                    shouted[term] += 1
                    shouting_channels.setdefault(term, set()).add(creator)
    words["shouted"] = words["word"].map(lambda w: shouted.get(w, 0))
    words["of"] = words["word"].map(lambda w: mentioned.get(w, 0))
    words["rate"] = np.where(words["of"] > 0, words["shouted"] / words["of"].replace(0, 1), 0.0)
    words["channels_shouting"] = words["word"].map(lambda w: len(shouting_channels.get(w, ())))
    # A word written in capitals by convention (a learned acronym, a generic label) is never a shout: its rate is not zero but undefined.
    words["exempt"] = words["word"].map(lambda w: w in acronyms or w in CAPS_LABELS)
    cols = ["rank", "word", "channels", "n_titles", "share_mean", "share_pooled", "shouted", "of", "rate", "channels_shouting", "exempt"]
    words[cols].to_csv(ANALYSIS_DIR / "year_words.csv", index=False, float_format="%.6f")
    vocab = set(words["word"])

    # ---- monthly standouts: weighted log-odds over channel-months ----
    cm = hits.drop_duplicates(["creator", "month", "word"])
    total = Counter(cm["word"])
    active = uniq.groupby("month")["creator"].nunique()
    month_rows = []
    for month, g in cm.groupby("month"):
        a = Counter(g["word"])
        b = Counter({w: total[w] - a.get(w, 0) for w in total})
        wlo = weighted_log_odds(a, b, alpha0=ALPHA0)
        top = sorted(((w, d, z, ya, yb) for w, (d, z, ya, yb) in wlo.items() if ya >= MONTH_MIN_CHANNELS), key=lambda x: -x[2])[:MONTH_TOP]
        for rank, (w, d, z, ya, yb) in enumerate(top, start=1):
            month_rows.append({"month": month, "rank": rank, "word": w, "z": round(z, 3), "log_odds": round(d, 4), "channels": ya, "channels_rest": yb, "channels_active": int(active[month])})
    months = pd.DataFrame(month_rows)
    # the example: the month's most-viewed title carrying the word and another of the month's standouts
    standouts = {m: g.sort_values("z", ascending=False)["word"].tolist() for m, g in months.groupby("month")}
    companions = {(r.month, r.word): [w for w in standouts[r.month] if w != r.word] for r in months.itertuples()}
    months = months.merge(pick_examples(uniq, hits[["row_id", "word"]], "month", list(zip(months["month"], months["word"])), companions, terms_by_row), on=["month", "word"], how="left")
    months.to_csv(ANALYSIS_DIR / "year_months.csv", index=False)

    # ---- weeks: the vocabulary's channel-weighted share, over channels with WEEK_MIN or more titles that week ----
    cw = uniq.groupby(["creator", "week"]).size().rename("n_week").reset_index()
    sized = cw[cw["n_week"] >= WEEK_MIN]
    weeks_meta = pd.DataFrame({
        "week": sorted(uniq["week"].unique()),
    })
    weeks_meta["titles"] = weeks_meta["week"].map(uniq.groupby("week").size())
    weeks_meta["channels"] = weeks_meta["week"].map(sized.groupby("week").size()).fillna(0).astype(int)
    weeks_meta["partial"] = [(w < WINDOW_FROM) or ((date.fromisoformat(w) + timedelta(days=6)).isoformat() > WINDOW_TO) for w in weeks_meta["week"]]
    weeks_meta.to_csv(ANALYSIS_DIR / "year_weeks_meta.csv", index=False)

    hv = hits[hits["word"].isin(vocab)]
    cwd = hv.groupby(["creator", "week", "word"]).size().rename("n").reset_index().merge(sized, on=["creator", "week"])
    cwd["share"] = cwd["n"] / cwd["n_week"]
    n_sized = sized.groupby("week").size()
    wk = cwd.groupby(["week", "word"]).agg(share_sum=("share", "sum"), channels=("creator", "nunique")).reset_index()
    wk["share"] = wk["share_sum"] / wk["week"].map(n_sized)
    titles_wk = hv.groupby(["week", "word"]).size().rename("titles").reset_index()
    wk = wk.merge(titles_wk, on=["week", "word"], how="left")
    wk[["week", "word", "share", "channels", "titles"]].sort_values(["word", "week"]).to_csv(ANALYSIS_DIR / "year_weeks.csv", index=False, float_format="%.6f")

    # ---- spikes: the furthest a word's weekly share rose above its own average over the full weeks ----
    full = set(weeks_meta.loc[~weeks_meta["partial"], "week"])
    grid = wk[wk["week"].isin(full)].pivot(index="word", columns="week", values="share").reindex(sorted(vocab)).fillna(0.0)
    grid = grid.reindex(columns=sorted(full), fill_value=0.0)
    baseline = grid.mean(axis=1)
    peak_week = grid.idxmax(axis=1)
    peak = grid.max(axis=1)
    ch = wk.set_index(["week", "word"])["channels"]
    spikes = pd.DataFrame({"word": grid.index, "week": peak_week.to_numpy(), "share": peak.to_numpy(), "baseline": baseline.to_numpy()})
    spikes["delta"] = spikes["share"] - spikes["baseline"]
    spikes["channels"] = [int(ch.get((w, k), 0)) for w, k in zip(spikes["week"], spikes["word"])]
    spikes = spikes[spikes["channels"] >= SPIKE_MIN_CHANNELS].sort_values("delta", ascending=False).head(SPIKES)
    # every week (the part-weeks too) against the full-week baseline: who is spiking in each week, strongest first
    all_grid = wk.pivot(index="word", columns="week", values="share").reindex(sorted(vocab)).reindex(columns=sorted(weeks_meta["week"]), fill_value=0.0).fillna(0.0)
    rise_all = all_grid.sub(baseline.reindex(all_grid.index).fillna(0.0), axis=0)
    spiking = {week: [w for w in rise_all[week].sort_values(ascending=False).index if rise_all.at[w, week] >= CO_SPIKE_MIN] for week in rise_all.columns}

    # the example: the week's most-viewed title carrying the word and another word spiking that week
    companions = {(r.week, r.word): [w for w in spiking[r.week] if w != r.word] for r in spikes.itertuples()}
    spikes = spikes.merge(pick_examples(uniq, hits[["row_id", "word"]], "week", list(zip(spikes["week"], spikes["word"])), companions, terms_by_row), on=["week", "word"], how="left")
    spikes.to_csv(ANALYSIS_DIR / "year_spikes.csv", index=False, float_format="%.6f")

    # ---- every vocabulary word in every week: its share and both titles, for the word search ----
    ww = wk[wk["word"].isin(vocab)][["word", "week", "share", "channels", "titles"]].copy()
    wanted = list(zip(ww["week"], ww["word"]))
    companions = {(week, word): [w for w in spiking[week] if w != word] for week, word in wanted}
    ww = ww.merge(pick_examples(uniq, hits[["row_id", "word"]], "week", wanted, companions, terms_by_row), on=["week", "word"], how="left")
    ww.sort_values(["word", "week"]).to_csv(ANALYSIS_DIR / "year_word_weeks.csv", index=False, float_format="%.6f")

    # ---- every week's own spikes: the words furthest above their average that week ----
    ch_all = wk.set_index(["week", "word"])["channels"]
    week_rows = []
    for week in rise_all.columns:
        col = rise_all[week].sort_values(ascending=False)
        rank = 0
        for w, delta in col.items():
            if delta <= 0 or rank >= WEEK_TOP:
                break
            if int(ch_all.get((week, w), 0)) < SPIKE_MIN_CHANNELS:
                continue
            rank += 1
            week_rows.append({"week": week, "rank": rank, "word": w, "share": all_grid.at[w, week], "baseline": baseline.get(w, 0.0), "delta": delta, "channels": int(ch_all.get((week, w), 0))})
    pd.DataFrame(week_rows, columns=["week", "rank", "word", "share", "baseline", "delta", "channels"]).to_csv(ANALYSIS_DIR / "year_week_spikes.csv", index=False, float_format="%.6f")

    info.update({"unique_titles": int(n_titles), "channels": int(n_channels), "vocab": int(len(words)), "bigrams": int(len(bigrams)), "months": int(months["month"].nunique()), "weeks": int(len(weeks_meta)), "spikes": int(len(spikes))})
    print(f"{n_titles} unique titles, {n_channels} channels; vocabulary {len(words)} with {len(bigrams)} bound pairs; {months['month'].nunique()} months, {len(weeks_meta)} weeks, {len(spikes)} spikes")


def main(argv: Optional[Sequence[str]] = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.parse_args(argv)
    with stage_timer("stage6c_year") as info:
        run(info)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
