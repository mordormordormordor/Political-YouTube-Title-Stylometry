"""Stage 6c - the year in words (site article No. 3): what the titles say, month
by month and week by week, counted so that no channel's output outweighs
another's.

Every count here is over unique titles (repeats dropped) and, wherever a share
is averaged, channel-weighted: a word's share is the mean over channels of the
share of the channel's titles that contain it, so the ten largest channels,
which publish four titles in ten, weigh the same as any other. Content words
are textstats.vocab_tokens of the normalized title (brand tags, show names and
episode numbers stripped; stopwords dropped; possessives folded). The shouted
counts use the capitalization rule's own test on the raw title (three or more
letters written in capitals, neither a learned acronym, a generic label nor one
of the channel's own tag words), a word once per title.

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
                         once; each with the month's most-viewed title containing it
    year_weeks_meta.csv  every week, Monday-keyed: titles, channels with WEEK_MIN or
                         more titles, partial (runs past the corpus window)
    year_weeks.csv       the vocabulary's channel-weighted share by week (over the
                         channels with WEEK_MIN or more titles that week)
    year_spikes.csv      the SPIKES words whose weekly share departed furthest above
                         their own average over the full weeks, with the peak week,
                         the baseline, the departure, and that week's most-viewed
                         title containing the word

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
from pipeline_titles.textstats import CAPS_LABELS, shouted_words, vocab_tokens, weighted_log_odds

VOCAB = 400
MONTH_TOP = 12
MONTH_MIN_CHANNELS = 5
WEEK_MIN = 5
SPIKES = 40
SPIKE_MIN_CHANNELS = 10
ALPHA0 = 500.0


def week_of(published: str) -> str:
    """The Monday that starts the week of a YYYY-MM-DD date."""
    d = date.fromisoformat(published)
    return (d - timedelta(days=d.weekday())).isoformat()


def example_rows(uniq: pd.DataFrame, hits: pd.DataFrame, by: str) -> pd.DataFrame:
    """For every (by, word), the most-viewed title containing the word: one row with the title's fields.

    `hits` is (row_id, word) for every unique title; `by` is a column of `uniq` (month or week)."""
    h = hits.merge(uniq[["row_id", by, "creator", "title_raw", "video_id", "url", "view_count"]], on="row_id")
    h = h.sort_values(["view_count", "row_id"], ascending=[False, True], na_position="last")
    return h.drop_duplicates([by, "word"]).rename(columns={"creator": "example_creator", "title_raw": "example_title", "video_id": "example_video", "url": "example_url", "view_count": "example_views"})


def run(info: dict) -> None:
    prepared = load_prepared()
    uniq = prepared[~prepared["is_dup"]].copy()
    uniq["week"] = uniq["published"].map(week_of)
    n_channels = uniq["creator"].nunique()
    n_titles = len(uniq)
    channel_titles = uniq.groupby("creator").size()

    # ---- (row_id, word) for every content word of the normalized title, once per title ----
    hits = pd.DataFrame(
        [(rid, w) for rid, t in zip(uniq["row_id"], uniq["title_norm"]) for w in set(vocab_tokens(t))],
        columns=["row_id", "word"],
    )
    hits = hits.merge(uniq[["row_id", "creator", "month", "week"]], on="row_id")

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
    for creator, raw in zip(uniq["creator"], uniq["title_raw"]):
        s, m = shouted_words(raw, acronyms, own_tags.get(creator, ()))
        mentioned.update(m)
        shouted.update(s)
        for w in s:
            shouting_channels.setdefault(w, set()).add(creator)
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
    months = months.merge(example_rows(uniq, hits[["row_id", "word"]], "month")[["month", "word", "example_creator", "example_title", "example_video", "example_url", "example_views"]], on=["month", "word"], how="left")
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
    spikes = spikes.merge(example_rows(uniq, hits[["row_id", "word"]], "week")[["week", "word", "example_creator", "example_title", "example_video", "example_url", "example_views"]], on=["week", "word"], how="left")
    spikes.to_csv(ANALYSIS_DIR / "year_spikes.csv", index=False, float_format="%.6f")

    info.update({"unique_titles": int(n_titles), "channels": int(n_channels), "vocab": int(len(words)), "months": int(months["month"].nunique()), "weeks": int(len(weeks_meta)), "spikes": int(len(spikes))})
    print(f"{n_titles} unique titles, {n_channels} channels; vocabulary {len(words)}; {months['month'].nunique()} months, {len(weeks_meta)} weeks, {len(spikes)} spikes")


def main(argv: Optional[Sequence[str]] = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.parse_args(argv)
    with stage_timer("stage6c_year") as info:
        run(info)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
