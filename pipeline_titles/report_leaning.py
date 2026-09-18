"""Document 14: political leaning from titles, in two levels (rendered by report_sections.write_all).

Level 1, titles: a frontier judge labels each sampled title left / right / neither from the
title text alone; the labels and the vocabulary behind them are analysed.
Level 2, channels: each channel's score over its sampled titles sorts the channels into
left, neutral and right groups; the groups' reliability and whole output are analysed."""

from __future__ import annotations

import json

import numpy as np
import pandas as pd

from pipeline_titles.common import ANALYSIS_DIR as A, RUNTIMES, SEED, read_jsonl
from pipeline_titles.report_sections import pct, rd, table


def _mname(c: str) -> str:
    c = c.replace("label_", "").replace("_score", "")
    if c.startswith("claude_code_"):
        return "Claude " + c.replace("claude_code_", "").replace("_", " ").title()
    return c.replace("_", ":", 1).replace("_", ".")


def _opt(name: str) -> pd.DataFrame | None:
    return rd(name) if (A / name).exists() else None


def _json(name: str) -> dict | None:
    return json.loads((A / name).read_text()) if (A / name).exists() else None


def _allotax_titles(allo, allo_c, jname: str) -> str:
    if allo is None or allo_c is None or not (allo.comparison == "titles").any():
        return "_(allotaxonographs not rendered on this run: see the README for the Node step)_"
    r = allo[allo.comparison == "titles"].iloc[0]; c = allo_c[allo_c.comparison == "titles"]
    left = c[c.side == "system_1"].head(8).type.tolist(); right = c[c.side == "system_2"].head(8).type.tolist()
    return (f"How to read it. The two vocabularies overlap less than the label shares suggest: D<sup>R</sup><sub>1/3</sub> = {r.divergence:.3f}, with {pct(r.exclusive_share_1)} of the left-read words never appearing in a right-read title and {pct(r.exclusive_share_2)} the other way. "
            f"The apex is shared (the year's subjects), and the divergence is carried by the flanks: on the left {', '.join(left)}; on the right {', '.join(right)}. "
            f"The bottom edges of the diamond, where the dark cells run, are the words used once on one side and never on the other, which is where the labelled sample's smallness shows ({int(r.n_types_1):,} and {int(r.n_types_2):,} word types from {int(r.n_titles_1):,} and {int(r.n_titles_2):,} titles).")


def _allotax_channels(allo, allo_c) -> str:
    if allo is None or allo_c is None or not (allo.comparison == "channels").any():
        return "_(not rendered on this run)_"
    r = allo[allo.comparison == "channels"].iloc[0]; c = allo_c[allo_c.comparison == "channels"]
    left = c[c.side == "system_1"].head(10).type.tolist(); right = c[c.side == "system_2"].head(10).type.tolist()
    return (f"D<sup>R</sup><sub>1/3</sub> = {r.divergence:.3f}: the groups' whole outputs are closer to each other than the left-read and right-read titles are, as they should be, since most of what either group publishes is the shared news of the year. "
            f"The words that separate them are the words the labels found, now over every title the channels published rather than the labelled sample: the left channels' flank is {', '.join(left)}; the right channels' is {', '.join(right)}. "
            f"Show furniture shows up here too (segment names, hosts' first names, the words of a title template), which is the price of comparing channels rather than labelled titles; "
            f"{pct(r.exclusive_share_2)} of the right channels' words never appear in a left channel's title, against {pct(r.exclusive_share_1)} the other way.")


def _classes_sentence(t: pd.DataFrame) -> str:
    rows = {r.comparison: r for r in t.itertuples()}
    a = rows.get("left-read vs right-read titles"); b = rows.get("left vs right channels, every title")
    if a is None or b is None:
        return ""
    return (f"Over the labelled titles the two classes are close in size ({int(a.n_left)} left-class words, {int(a.n_right)} right-class, of {int(a.n_words):,} words with three or more occurrences). "
            f"Over the channels' whole output, with ten times the titles, {pct(b.share_classified)} of the vocabulary clears the cutoff and the right classifies far more words ({int(b.n_right):,} against {int(b.n_left):,} of {int(b.n_words):,}): "
            f"the right channels' vocabulary is the more varied one, and its stance words are spread over more distinct terms.")


def _logodds_section(lo_s, lo_ag, lex, judge: str, jname: str) -> str:
    if lo_s is None or lex is None or not (lo_s.comparison == "titles").any():
        return "_(not computed on this run)_"
    cut = float(lo_s.cutoff_z.iloc[0])
    cname = {"titles": "left-read vs right-read titles", "channels": "left vs right channels, every title"}
    t = lo_s[lo_s.comparison.isin(cname)].copy(); t["comparison"] = t.comparison.map(cname); t["share_classified"] = (t.n_left + t.n_right) / t.n_words
    ag = None
    if lo_ag is not None and len(lo_ag):
        m = lo_ag[((lo_ag.a == "titles") & (lo_ag.b == "channels")) | ((lo_ag.a == "channels") & (lo_ag.b == "titles"))]
        ag = m.iloc[0] if len(m) else None
    sw = [w.split(" (")[0] for w in str(ag.side_switchers).split(", ") if w and w != "nan"] if ag is not None else []
    lj = lex[lex.judge == judge].iloc[0]
    conf = json.loads(lj.confusion); n_neither = sum(conf["neither"].values())
    ag_txt = (f"The two lexicons agree: of the {int(ag.both_partisan)} words that both the labelled titles and the groups' whole output classify as partisan, {pct(ag.same_side_when_both_partisan)} point the same way (kappa {ag.kappa:.2f} over three classes, low only because the groups' output, with ten times the titles, classifies many more words). "
              f"The words that switch sides between the two are {', '.join(sw) if sw else 'none'}, topic and show-name words rather than stance words.") if ag is not None else ""
    return f"""The allotaxonograph ranks words by how far they move between the two rankings; weighted log-odds asks a different question, whether a word is over-used on one side *given how common it is overall*, and gives every word a z-score, so a cutoff turns the vocabulary into a three-way lexicon: right at z ≥ {cut:g}, left at z ≤ −{cut:g}, neither otherwise (the two-sided 5 % level; words with fewer than 3 occurrences are not classified).

![Log-odds, titles.](figures/14_logodds_titles.png)
*Weighted log-odds (Monroe, Colaresi and Quinn 2008). Left: every word by its z (vertical) and its frequency (horizontal, log scale) for the titles {jname} read as left against those it read as right; blue = left-class, orange = right-class, grey = neither. Right: the 25 words each side over-uses most, mirrored about the spine, the word beside the spine and its z at the bar's end; bars beyond the axis cap are cut, drawn paler, and keep their value.*

How many words clear the cutoff, for the labelled titles and for the channel groups' whole output (level 2):

![Words that clear the cutoff.](figures/14_logodds_classes.png)
*Left-class and right-class words as shares of each vocabulary, counts printed; the rest are neither.*

{_classes_sentence(t)}

{ag_txt}

**What a word list can do on its own.** The lexicon answers a specific question: how much of the judge's reading is vocabulary? If {jname} decided a title's leaning from the words in it, a plain word list built from its own labels should be able to reproduce those labels. So the list is built from the classes above (every word at |z| ≥ {cut:g} is a left-class or a right-class word); a title is called left when it holds more left-class than right-class words, right the other way, neither on a tie or with no classified word; and the list is built out of fold, on four fifths of the channels and applied to the remaining fifth, so no channel's titles help classify themselves.

![Lexicon against the judge.](figures/14_lexicon_vs_judge.png)
*Left: each channel's score from the word list's labels against its score from {jname}'s labels, coloured by the judge's group. Right: the word list's class against {jname}'s label, title by title, with the share of each row.*

Title by title (the right panel; rows are what {jname} said, columns what the word list said):

- The list agrees with {jname} on {pct(lj.accuracy)} of titles (kappa {lj.kappa:.2f}), which is weak. Where both call a title partisan they agree on the side {pct(lj.side_agreement_when_both_partisan)} of the time, so the direction is mostly right; the failure is in deciding whether a title is partisan at all.
- The list finds left-class words in {pct(conf['neither']['left'] / n_neither)} of the titles {jname} called neither and right-class words in another {pct(conf['neither']['right'] / n_neither)}: a plain headline that mentions MAGA, Epstein or Iran carries left-coded words without a left stance, and a list cannot tell the difference.
- It also misses partisan titles: it recovers {pct(lj.recall_left)} of the judge's left titles but only {pct(lj.recall_right)} of its right ones, because the right's stance words (woke, fraud, women) are rarer than the left's subject words.

Channel by channel (the left panel; each dot is a channel, its score from the judge's labels across and from the list's labels up), the list does much better: Spearman {lj.channel_spearman:.2f}, and {pct(lj.channel_group_agreement)} of channels land in the same group. Fifty titles average out the noise of single titles, so the ordering of channels is largely a matter of vocabulary even though the title-level call is not.

In one line: vocabulary says roughly where a channel sits, not how any single title reads. The judge reacts to framing, to how the words are put together, and that is the evidence that the labels measure stance rather than subject.

{table(lex[lex.judge == judge].assign(judge=jname), ['judge', 'n_titles', 'coverage', 'accuracy', 'kappa', 'partisan_titles_lexicon_neither', 'side_agreement_when_both_partisan', 'recall_left', 'recall_right', 'channel_spearman', 'channel_group_agreement'], fmt='{:.2f}')}
"""


def doc_leaning() -> str:
    ls = _json("leaning_label_shares.json"); summ = _json("leaning_summary.json")
    bc = rd("leaning_by_creator.csv"); gs = rd("leaning_groups.csv"); words = rd("leaning_words.csv"); labs = rd("leaning_labels.csv.gz")
    shr = _opt("leaning_split_half.csv"); stab = _opt("leaning_stability.csv"); stab_ch = _opt("leaning_stability_channels.csv"); gm = _opt("leaning_by_group_month.csv")
    allo = _opt("allotax_summary.csv"); allo_c = _opt("allotax_contributions.csv")
    lo_s = _opt("leaning_logodds_summary.csv"); lo_ag = _opt("leaning_logodds_agreement.csv"); lex = _opt("leaning_lexicon_validation.csv")
    two = _json("leaning_two_readings.json"); two_ch = _opt("leaning_two_readings_channels.csv"); changed_t = _opt("leaning_two_readings_changed_titles.csv"); runs_t = _json("leaning_runs.json")
    rep = _json("leaning_repeat.json"); rep_ch = _opt("leaning_repeat_channels.csv")
    judge = summ["judge_of_record"]; jname = _mname(judge); eps = float(summ.get("threshold", 0.05))
    shares = ls["label_shares"]; counts = ls["label_counts"]
    n_l, n_n, n_r = (int(summ["groups"].get(g, 0)) for g in ("left", "neutral", "right"))
    gs2 = gs.copy(); gs2["group"] = gs2.group.map(lambda g: f"{g} channels")
    neutral = bc[bc.group == "neutral"].sort_values("score")
    wj = words[words.model == judge]
    right_w = wj.sort_values("z", ascending=False).head(20); left_w = wj.sort_values("z").head(20)
    rng = np.random.RandomState(SEED)
    ex = pd.concat([labs[labs[judge] == lab].sample(4, random_state=rng)[["creator", "title_raw", judge]] for lab in ("left", "right", "neither")]).rename(columns={judge: "label"})
    runs = [r for r in read_jsonl(RUNTIMES) if r["stage"] == "stage7_leaning" and r.get("calls")]
    cc_calls = sum(r.get("calls", 0) for r in runs); cc_min = sum(r.get("seconds", 0) for r in runs) / 60; cc_cost = sum(r.get("reported_cost_usd", 0) or 0 for r in runs)
    n50, nbase = int((bc.n_titles >= 50).sum()), int((bc.n_titles < 50).sum())
    sh_j = shr.iloc[0] if shr is not None and len(shr) else None
    st_j = stab.iloc[0] if stab is not None and len(stab) else None
    movers = stab_ch.reindex(stab_ch.change.abs().sort_values(ascending=False).index).head(6) if stab_ch is not None and len(stab_ch) else None
    near_txt, flip_txt = "", ""
    if stab_ch is not None and len(stab_ch) and st_j is not None:
        changed = stab_ch[stab_ch.group_base != stab_ch.group_all]
        near_txt = f"all of them with a final score between −{changed.score_all.abs().max():.2f} and +{changed.score_all.abs().max():.2f}" if len(changed) else "none"
        flip_txt = "none crosses from left to right or back" if int(st_j.sign_flipped) == 0 else f"{int(st_j.sign_flipped)} cross from one side to the other"
    rel = ""
    if sh_j is not None and st_j is not None:
        rel = (f" The score does not depend on which titles were drawn: two random halves of a channel's titles rank the {int(sh_j.n_channels)} channels with 50 titles the same way (Spearman {sh_j.split_half_spearman_mean:.2f}), "
               f"and so do the first 16 titles and the {int(stab_ch.n_topup.median())} drawn later ({st_j.spearman_base_vs_topup:.2f}).")
    gm_tab = None; gm_txt = ""
    if gm is not None and len(gm):
        piv = gm.pivot(index="group", columns="month", values="score").reindex(["left", "neutral", "right"])
        piv.insert(0, "titles / month", gm.groupby("group").n_titles.mean().round(0).astype(int).astype(str).reindex(piv.index))
        piv.index = piv.index.map(lambda g: f"{g} channels"); gm_tab = piv.reset_index()
        rng_txt = "; ".join(f"{g} {'ranges ' if i == 0 else ''}from {piv.loc[g].iloc[1:].astype(float).min():+.2f} to {piv.loc[g].iloc[1:].astype(float).max():+.2f}" for i, g in enumerate(piv.index))
        mp = gm.groupby("month").apply(lambda g: np.average(g.partisan_share, weights=g.n_titles), include_groups=False)
        gm_txt = f"It did not move: {rng_txt}; the share of all sampled titles read as partisan stays between {pct(mp.min())} and {pct(mp.max())} every month. Whatever the news did over the year, a channel's title stance is a fixed property of the channel, which is also what document 6 found for style."
    # the same titles read twice (Level 1: labels; Level 2: channel scores)
    two_intro, two_finding, two_l1, two_l2, two_lim, two_method = "", "", "", "", "", ""
    if two is not None:
        rr = rep["record_vs_repeat"] if rep else None
        if rr:
            two_intro = (" Every title was read three times by the judge: once in a batch of its channel's other titles, then twice in shuffled batches with different seeds. The first shuffled reading is the one used; "
                         "the other two are kept for comparison (Level 1, \"The same title read three times\"; Level 2, check 3).")
            two_finding = (f" Read again by the same judge in fresh shuffled batches, {pct(rr['exact_agreement'])} of titles kept their label (kappa {rr['kappa']:.2f}) and the channels came out in the same order (Spearman {rr['channel_spearman']:.2f}); "
                           f"an earlier reading with the titles batched by channel agreed at {pct(two['exact_agreement'])}.")
        else:
            two_intro = (" Every title was read twice by the judge, once in a batch of its channel's other titles and once in a shuffled batch; the shuffled reading is the one used, and the first is kept "
                         "for comparison (Level 1, \"The same title read twice\"; Level 2, check 3).")
            two_finding = f" Read a second time by the same judge, in shuffled batches, {pct(two['exact_agreement'])} of titles kept their label (kappa {two['kappa']:.2f}) and the channels came out in nearly the same order (Spearman {two['channel_spearman']:.2f})."
        conf = two["confusion_first_then_shuffled"]
        conf_tab = pd.DataFrame([{"first reading": a, "shuffled: left": conf[a]["left"], "shuffled: neither": conf[a]["neither"], "shuffled: right": conf[a]["right"]} for a in ("left", "neither", "right")])
        by_run = two.get("by_run", {})
        run_txt = f"; on the base draw {pct(by_run['1']['exact_agreement'])} (run 1 against run 3), on the top-up {pct(by_run['2']['exact_agreement'])} (run 2 against run 3)" if {"1", "2"} <= set(by_run) else ""
        ex_changed = ""
        if changed_t is not None and len(changed_t):
            pick = changed_t.sample(min(6, len(changed_t)), random_state=np.random.RandomState(SEED + 1))[["creator", "title_raw", "label_first", "label_shuffled"]]
            ex_changed = f"Titles whose label changed, six drawn at random from the {len(changed_t):,}:\n\n" + table(pick, rename={"creator": "channel", "title_raw": "title", "label_first": "first reading", "label_shuffled": "shuffled"})
        rep_l1, closing = "", ""
        if rr:
            three = rep["three_readings"]; fr = rep["first_vs_repeat"]
            conf2 = rr["confusion_record_then_repeat"]
            conf2_tab = pd.DataFrame([{"reading of record": a, "repeat: left": conf2[a]["left"], "repeat: neither": conf2[a]["neither"], "repeat: right": conf2[a]["right"]} for a in ("left", "neither", "right")])
            model_txt = ""
            if runs_t and any(r.get("model_ids") for r in runs_t):
                ids = sorted({m for r in runs_t for m in (r.get("model_ids") or [])})
                model_txt = f" The repeat, three days after the others, recorded the model the CLI's alias resolved to ({', '.join(ids)}); the earlier runs did not record it."
            rep_l1 = f"""
A clean repeat then settles how much of that is the judge. Run 4 sent every title again in shuffled batches with a fresh seed: the same method run twice.{model_txt} The two shuffled readings agree on {pct(rr['exact_agreement'], 1)} of titles (kappa {rr['kappa']:.2f}), so the judge on its own changes about one label in {round(1 / (1 - rr['exact_agreement']))} between two runs, nearly all between partisan and neither ({rr['side_flipped']} titles switched side; where both readings call a title partisan they agree on the side {pct(rr['same_side_when_both_partisan'])} of the time), and with no drift in the balance ({pct(rr['partisan_share_record'], 1)} of titles partisan in the reading of record, {pct(rr['partisan_share_repeat'], 1)} in the repeat). The channel-batched reading agrees with either shuffled reading at {pct(two['exact_agreement'], 1)} and {pct(fr['exact_agreement'], 1)}, so a title's company cost about {round(100 * (rr['exact_agreement'] - (two['exact_agreement'] + fr['exact_agreement']) / 2))} points more, and its effect had a direction that noise does not: {pct(two['partisan_share_first'], 1)} of titles read as partisan in company against {pct(rr['partisan_share_record'], 1)} and {pct(rr['partisan_share_repeat'], 1)} alone. All three readings agree on {pct(three['all_three_agree'], 1)} of titles; {three['no_majority']} titles got three different labels.

{table(conf2_tab)}"""
            closing = (f"So a single title's label is about one in {round(1 / (1 - rr['exact_agreement']))} fragile on the judge's own account, one in {round(1 / (1 - two['exact_agreement']))} once its batch-mates are allowed to vary too. "
                       "The channel scores, which average fifty of them, are steadier (Level 2, check 3).")
        else:
            closing = (f"The two readings differ in their batches by design, so the {pct(1 - two['exact_agreement'])} of labels that changed is the judge's own inconsistency and the effect of a title's company together; neither is measured on its own. "
                       "A single title's label is, to that extent, one reading among possible readings. The channel scores, which average fifty of them, are steadier (Level 2, check 3).")
        two_l1 = f"""### The same title read {'three times' if rr else 'twice'}

Every title went to the judge {'three times' if rr else 'twice'}, with the same prompt at temperature 0. The first reading (runs 1 and 2: the base draw, then the top-up) sent the titles in sample order, so a call held one or two channels' titles and a title was read in the company of its channel's other titles. The second reading (run 3) sent every title again in a seeded random order, so a call mixes channels and the judge sees nothing but the title. The second is the reading of record; the first is kept in `leaning_labels_channel_batched.csv.gz`.

The two readings agree on {pct(two['exact_agreement'])} of the {two['n_titles']:,} titles (kappa {two['kappa']:.2f}){run_txt}. Where both call a title partisan they agree on the side {pct(two['same_side_when_both_partisan'])} of the time: {two['side_flipped']} titles switched from left to right or back. The disagreement is almost all a title moving between partisan and neither, and it has a direction: {two['partisan_to_neither']} titles read as partisan in company and as neither alone, {two['neither_to_partisan']} the other way, so the shuffled reading calls {pct(two['partisan_share_shuffled'])} of titles partisan against {pct(two['partisan_share_first'])} the first time.

{table(conf_tab)}
{ex_changed}{rep_l1}
{closing}
"""
        flips = two_ch[(two_ch.n_titles >= two["min_titles_per_channel"]) & (((two_ch.group_first == "left") & (two_ch.group_shuffled == "right")) | ((two_ch.group_first == "right") & (two_ch.group_shuffled == "left")))] if two_ch is not None else None
        if flips is None or not len(flips):
            flip2 = "none crosses from left to right or back"
        else:
            flip2 = "; ".join(f"{r.creator} crosses from {r.group_first} to {r.group_shuffled} ({r.score_first:+.2f} to {r.score_shuffled:+.2f})".replace("-", "−") for r in flips.itertuples())
        two_l2 = (f"\n3. **Second reading.** The first reading of every title (Level 1) scores the channels too. The two readings rank the {two['n_channels']} channels with at least {two['min_titles_per_channel']} labelled titles at Spearman {two['channel_spearman']:.2f} "
                  f"and move a channel's score by {two['channel_mean_abs_change']:.2f} on average; {two['channel_group_changed']} channels change group, and {flip2}.")
        if rr:
            rflips = rep_ch[(rep_ch.n_titles >= rr["min_titles_per_channel"]) & (((rep_ch.group_record == "left") & (rep_ch.group_repeat == "right")) | ((rep_ch.group_record == "right") & (rep_ch.group_repeat == "left")))] if rep_ch is not None else None
            if rflips is None or not len(rflips):
                flip3 = "none crosses from left to right or back"
            else:
                flip3 = "; ".join(f"{r.creator} crosses from {r.group_record} to {r.group_repeat} ({r.score_record:+.2f} to {r.score_repeat:+.2f}, {int(r.n_titles)} titles)" for r in rflips.itertuples()).replace("-", "−")
            two_l2 = (f"\n3. **Second and third readings.** The other two readings of every title (Level 1) score the channels too. The clean repeat ranks the {rr['n_channels']} channels with at least {rr['min_titles_per_channel']} labelled titles at Spearman {rr['channel_spearman']:.2f} "
                      f"and moves a channel's score by {rr['channel_mean_abs_change']:.2f} on average; {rr['channel_group_changed']} channels change group, and {flip3}. The channel-batched reading ranks them at {two['channel_spearman']:.2f}, "
                      f"moves a score by {two['channel_mean_abs_change']:.2f} and changes {two['channel_group_changed']} groups, and {flip2}.")
        if rr:
            two_lim = (f" Its repeatability is measured: a clean repeat of the method agrees with the labels of record on {pct(rr['exact_agreement'])} of titles (kappa {rr['kappa']:.2f}) and ranks the channels at {rr['channel_spearman']:.2f}, "
                       f"so about one title label in {round(1 / (1 - rr['exact_agreement']))} is the judge's own noise, which the channel scores absorb.")
            two_method = (" Readings: the labels of record against the first reading (channel-batched) and against the repeat (the same method, a fresh shuffle seed, `--repeat`), title by title (exact agreement, Cohen's kappa, the confusion table) and channel by channel "
                          f"(channels with at least {rr['min_titles_per_channel']} labelled titles: Spearman between the two scores, mean absolute change, groups changed), and the three readings together (`leaning_repeat.json`).")
        else:
            two_lim = (f" The same model did read every title twice, but the second reading also changed the batches from channel-grouped to shuffled, so its {pct(two['exact_agreement'])} agreement mixes the judge's inconsistency with the effect of a title's company "
                       "and cannot be split into the two; a repeat with a fresh shuffle seed (`--repeat`) would put a number on the judge alone.")
            two_method = (" Two readings: the first reading's labels against the labels of record, title by title (exact agreement, Cohen's kappa, the confusion table, per run) and channel by channel "
                          f"(channels with at least {two['min_titles_per_channel']} labelled titles: Spearman between the two scores, mean absolute change, groups changed).")
    rel += two_finding
    runs_tab = ""
    if runs_t:
        rt = pd.DataFrame(runs_t)
        rt["batches"] = rt.batch_order.map({"sample order": "sample order (one or two channels a call)", "shuffled": "shuffled (a call mixes channels)"}).fillna(rt.batch_order)
        rt["titles"] = rt.titles.map(lambda v: f"{int(v):,}" if pd.notna(v) else "")
        rt["minutes"] = rt.minutes.round(0).astype(int); rt["reported cost"] = rt.reported_cost_usd.map(lambda v: f"${v:.2f}" if pd.notna(v) else "")
        rt["date (UTC)"] = rt.started.str.slice(0, 16).str.replace("T", " ")
        runs_tab = "\n\n" + "\n".join("   " + l for l in table(rt, ["run", "what", "titles", "batches", "calls", "minutes", "reported cost", "date (UTC)"]).strip().splitlines()) + "\n"
    return f"""# 14. Political leaning from titles alone

**The question and the design.** Can a channel's political leaning be read off its titles? The analysis has two levels, and everything in this document belongs to one of them.

1. **Titles.** A frontier model ({jname}, through the Claude Code CLI) reads each sampled title on its own, never the channel name, and labels it *left*, *right* or *neither* by the viewpoint the wording signals. Level 1 analyses those labels: how many titles read each way, and which words carry each reading.
2. **Channels.** Each channel's sampled titles give it a score, (titles read right − titles read left) / titles sampled, from −1 (every title read left) to +1 (every title read right). The score sorts the channels into three groups: **left** below −{eps:g}, **right** above +{eps:g}, **neutral** between. Level 2 analyses the groups: how many channels land in each, how reliable the score is, and what the groups' whole output looks like when their titles are compared as bodies of text.

Everything here is *model-perceived* leaning: how a careful, reader-like model reads the wording of a title. The sample is 16 titles per channel plus a top-up to 50, spread evenly across the months, for every channel with at least 50 edited uploads ({n50} of {len(bc)} channels; the other {nbase} stay at their base draw): {len(labs):,} titles in all.{two_intro}

## The finding in one paragraph

{jname} reads {pct(shares.get('neither', 0))} of titles as neither, {pct(shares.get('left', 0))} as left and {pct(shares.get('right', 0))} as right. Sorted by their scores, {n_l} channels are left, {n_r} right and {n_n} neutral.{rel} The words behind the labels are stance words rather than subjects: the *right* vocabulary is {', '.join(right_w.word.head(8))}; the *left* vocabulary is {', '.join(left_w.word.head(8))}. Applied to everything the left and right channels published, the same words separate the two groups' whole output, with the year's shared subjects (Trump, Iran, the war) at the top of both.

## Level 1: titles

### What the judge labelled

Over the {ls['n_labelled']:,} labelled titles:

{table(pd.DataFrame([{'label': k, 'titles': counts[k], 'share': shares[k]} for k in ('left', 'neither', 'right')]), fmt='{:.3f}')}

Four titles of each label, drawn at random:

{table(ex)}

Six in ten titles carry no readable stance: plain news headlines, non-political titles, or political titles whose wording does not tip either way. The labels live on the other four in ten, and the rest of this level asks what those titles have in their words.

{two_l1}
### The vocabulary of left-read and right-read titles

Titles {jname} labelled left ({int(wj.n_left_titles.iloc[0]):,}) vs right ({int(wj.n_right_titles.iloc[0]):,}), compared two ways: weighted log-odds (which words are over-used on one side, given how often they appear at all) and rank-turbulence divergence, read off an allotaxonograph (Dodds et al. 2023), the instrument built for exactly this comparison of two Zipfian systems.

![Allotaxonograph, titles.](figures/14_allotax_titles.png)
*Allotaxonograph of the titles {jname} read as left (system 1, left flank) against the titles it read as right (system 2, right flank); drawn by the Computational Story Lab's own renderer (allotaxonometer-ui), rank-turbulence divergence with α = 1/3. Diamond: every word placed by its rank in each system on log axes, the rank-rank plane rotated so that words used equally sit on the vertical centre line; colour = how many words share a cell; the words named along the flanks are the furthest from the centre line at each frequency, i.e. the most one-sided. Contour lines join equal contributions to the divergence. Right: the {int(allo.loc[allo.comparison == 'titles', 'bars'].iloc[0]) if allo is not None and 'bars' in allo.columns and (allo.comparison == 'titles').any() else 40} largest contributions, each with its two ranks (system 1 ⇋ system 2), grey bars pulling left, blue bars pulling right. Below the diamond: the balance of tokens, types and exclusive types between the two systems.*

{_allotax_titles(allo, allo_c, jname)}

The two instruments disagree about one word, and the disagreement is instructive: "trump" is the most over-used word on the left by log-odds ({int(wj.loc[wj.word == 'trump', 'count_left'].iloc[0]) if (wj.word == 'trump').any() else 0:,} occurrences in left-read titles against {int(wj.loc[wj.word == 'trump', 'count_right'].iloc[0]) if (wj.word == 'trump').any() else 0:,} in right-read ones), but it sits at the apex of the diamond, because it is the top-ranked word on both sides; rank turbulence measures who *changes* the ordering, not who wins the count.

For reference, the fifteen most one-sided words each way with their z and their occurrences on each side (the full table, with the raw log-odds, the ranks and each word's contribution to the divergence, is `leaning_words.csv`):

{table(right_w.head(15), ['word', 'z', 'count_right', 'count_left'], fmt='{:.1f}')}

{table(left_w.head(15), ['word', 'z', 'count_left', 'count_right'], fmt='{:.1f}')}

Read as a map of the two grammars of attack: the right's titles are about Democrats, fraud, women and trans issues, the woke, Charlie Kirk, California and Newsom, Islam and Mamdani; the left's are about Trump, MAGA, the wars (Iran, Israel, Gaza, Venezuela), Epstein, Vance and Noem, and they carry the outrage furniture (breaking, panics).

### A left / right / neither lexicon, and what a word list can and cannot do

{_logodds_section(lo_s, lo_ag, lex, judge, jname)}

## Level 2: channels

### From titles to channel groups

A channel's score is the balance of its sampled titles, and the groups follow from the score alone; no other information about the channel enters. The {len(bc)} channels sort as:

{table(gs2, ['group', 'n_channels', 'n_titles', 'mean_score', 'min_score', 'max_score', 'mean_left', 'mean_neither', 'mean_right'], fmt='{:.2f}')}

![Scores.](figures/14_leaning_scores.png)
*Left: each channel's score against the share of its titles read as neither; the dashed lines are the group thresholds at ±{eps:g}. Right: the distribution of scores, coloured by group.*

![Every channel.](figures/14_leaning_channels.png)
*Every channel's sampled titles: the share labelled left (blue), neither (grey) and right (orange), sorted by score, most left-reading first; the score at the right is coloured by group.*

![Group composition.](figures/14_leaning_group_composition.png)
*Mean composition of a channel's titles in each group.*

With 50 titles no channel scores ±1 ({int((bc.score.abs() >= 0.9).sum())} sit at or beyond ±0.90): even the most one-sided channels title one video in twenty as plain news. The {n_n} neutral channels, whose sampled titles balance or read mostly as neither: {', '.join(neutral.creator)}.

### Would a different draw of titles, or a second reading, give a different score?

A channel's score comes from 50 sampled titles out of the hundreds or thousands it published, so the first thing to check is whether the draw matters: had the sample been different, would the channel's score, and its group, be different? Two checks, both on the {int(sh_j.n_channels) if sh_j is not None else n50} channels with 50 labelled titles; then the second reading.

1. **Split-half.** Each channel's 50 titles are split at random into two halves of {int(sh_j.median_titles_per_half) if sh_j is not None else 25} and each half is scored on its own, so every channel gets two scores from disjoint sets of titles. The two sets of scores rank the channels at Spearman {sh_j.split_half_spearman_mean:.2f} (mean of 20 random splits, SD {sh_j.split_half_spearman_sd:.3f}): whichever half you look at, the channels come out in nearly the same order.
2. **First draw against second draw.** The sample was drawn in two steps, 16 titles per channel first and {int(stab_ch.n_topup.median()) if stab_ch is not None and len(stab_ch) else 34} more afterwards from other months, so the two draws are independent samples of the same channel. Scored separately they rank the channels at Spearman {st_j.spearman_base_vs_topup:.2f}. Going from the 16-title score to the 50-title score moves a channel by {st_j.mean_abs_change:.2f} on average; {int(st_j.group_changed)} of {int(st_j.n_channels)} channels change group, {near_txt}, and {flip_txt}.{two_l2}

![Stability.](figures/14_leaning_stability.png)
*Each channel's score from its first 16 titles against its score from the 34 drawn later, coloured by its final group. Points on the diagonal would mean identical scores; the labelled points are the channels that moved most.*

The channels that moved most between the two draws, for a sense of what "moved" means:

{table(movers.rename(columns={'creator': 'channel', 'score_base': 'score, first 16 titles', 'score_topup': 'score, next 34 titles', 'score_all': 'score, all 50', 'group_base': 'group at 16', 'group_all': 'group at 50'}), ['channel', 'score, first 16 titles', 'score, next 34 titles', 'score, all 50', 'group at 16', 'group at 50'], fmt='{:+.2f}') if movers is not None else '_(none)_'}

So the score is a property of the channel, not of the draw, and not of the reading either. With 50 titles it moves in steps of 0.02, and the only channels whose group is in doubt are the ones sitting within a few titles of a threshold.

### The groups' whole output

The groups were defined from 50 sampled titles per channel; the channels published far more. Comparing everything the {n_l} left channels published with everything the {n_r} right channels published (every unique edited upload in the creator-balanced subset{f", {int(allo.loc[allo.comparison == 'channels', 'n_titles_1'].iloc[0]):,} vs {int(allo.loc[allo.comparison == 'channels', 'n_titles_2'].iloc[0]):,} titles" if allo is not None and (allo.comparison == 'channels').any() else ''}) asks whether the vocabulary that separated the labelled titles separates the groups' bodies of work, with no label on any individual title.

![Allotaxonograph, channels.](figures/14_allotax_channels.png)
*Left channels (system 1) against right channels (system 2), every title; same instrument and α as above.*

{_allotax_channels(allo, allo_c)}

![Log-odds, channels.](figures/14_logodds_channels.png)
*Weighted log-odds of every word in the left channels' titles against the right channels', same construction as the titles figure.*

### Does perceived leaning move over the year?

The top-up titles were spread evenly across months, so the sample supports a group-level look at whether the balance of partisan titles moved between January and September (a channel contributes about five titles a month, so channel-level months are not readable):

{table(gm_tab, fmt='{:+.2f}') if gm_tab is not None else '_(not computed)_'}

{gm_txt}

## Method

1. **Sample.** Every creator gets a base draw of 16 unique edited-upload titles (seed 20260914; creators with fewer than 16 uploads topped up from live VODs). Creators with at least 50 unique uploads are then topped up to 50 with further uploads spread evenly across months (round-robin over the months, random within month, its own random stream), so the extra titles never depend on which month a creator posted most in: {len(labs):,} titles, {n50} creators at 50, {nbase} at their base.
2. **Labelling.** One prompt (in `leaning.py` and the methods appendix): label the viewpoint the title's own wording signals as left, right or neither, with three anchoring examples; temperature 0; the judge sees the title text only, numbered 1 to 20, never the channel name; every response cached. {jname} runs through the Claude Code CLI in print mode on a Claude Max subscription, in {'four' if rep else 'three'} runs: the base draw and the top-up with the titles in sample order (a call held one or two channels' titles), then every title again in a seeded random order (a call mixes channels), which is the labelling of record{', and once more with a fresh seed, the repeat kept for the reliability check' if rep else ''}.{runs_tab}
   {cc_calls:,} calls and {cc_min:.0f} minutes in all; the CLI reported an equivalent API cost of ${cc_cost:.2f}, not charged.
3. **Scores and groups.** Per channel: shares of left / right / neither and score = (right − left) / n over its sampled titles; left below −{eps:g}, right above +{eps:g}, neutral between.
4. **Reliability.** Split-half: channels with at least 32 labelled titles, two random halves, Spearman between the two channel rankings, 20 splits. Base vs top-up: the base-draw score against the top-up score per channel (disjoint titles), and the group at 16 titles against the group at 50.{two_method}
5. **Words.** Weighted log-odds with an informative Dirichlet prior (alpha0 = 500; Monroe, Colaresi and Quinn 2008) and rank-turbulence divergence (alpha = 1/3; Dodds et al. 2023) on the vocabulary tokens of document 11, for the left-read vs right-read titles and for the left vs right channels' whole output. The divergence follows the allotaxonometer's conventions exactly (tied ranks over the union of both vocabularies, absent words at the last tied rank, the sum normalised so that two vocabularies with no word in common give D = 1); `textstats.rank_turbulence_divergence` reproduces the library's per-word contributions to machine precision.
6. **Log-odds lexicon.** Every word with 3+ occurrences in the two systems together, right against left; right at z ≥ 1.96, left at z ≤ −1.96, neither otherwise; the same for the channel groups, and Cohen's kappa of the classes between the two over their shared words. The lexicon check: the labelled titles split into five folds by channel, the lexicon built on four folds and applied to the fifth (a title is left when it holds more left-class than right-class words, right the other way, neither on a tie or no classified word), then agreement with the judge's labels title by title and channel by channel (`leaning_lexicon.py`).
7. **Allotaxonographs.** Drawn by allotaxonometer-ui {allo.allotaxonometer_ui.iloc[0] if allo is not None else ''} (the Computational Story Lab's Svelte renderer, the same code behind the lab's web app and py-allotax) through Node and Puppeteer (`pipeline_titles/allotax.py`, `pipeline_titles/allotax_js/`), from the same word counts as the tables (`allotax_summary.csv`, top contributions in `allotax_contributions.csv`).
8. **Months.** The labels by channel group x month (`leaning_by_group_month.csv`): titles, creators, partisan share, left and right shares, score.

## Limitations

- **This is perceived leaning.** A model reads a title the way an attentive reader would, and readers disagree. No human panel was used, by choice: one reader cannot supply political ground truth, and a balanced panel is a study of its own. A blind 200-title sheet exists (`leaning_human_sheet.csv`, still unfilled) for anyone who wants a single-reader reliability check.
- **One judge{', and its second reading is not a clean repeat' if two is not None and rep is None else ''}.** Every number here is one model's reading, and a model reads a title the way it was trained to; a second frontier model of a different family would be the natural robustness check (`--models <alias>` takes any Claude Code model alias).{two_lim}
- **The groups are a cut on a continuous score.** ±{eps:g} is one title in twenty; a channel at −0.06 and one at −0.04 differ by one label. The score is the measurement, the group is a convenience for comparing bodies of text, and the neutral group mixes channels whose titles balance with channels whose titles are mostly plain news.
- **Ten words carry little stance.** Six in ten titles are neither, so a channel's score rests on a minority of its titles. At 50 titles the score moves in steps of 0.02 and the split-half reliability is {sh_j.split_half_spearman_mean:.2f}; the {nbase} channels with fewer than 50 uploads still sit at 16 titles or fewer and move in steps of 1/16.
- **Target and stance blur at the margin.** Hostile-to-Trump wording reads left even when it is a wire headline or an anti-war right channel's; the neutral group and the left tail hold both kinds. Prompt v2 (which also asks for the target) exists in `leaning.py` and was not run at scale.
- **Month-level reading is group-level only.** Five titles per channel-month is not a monthly channel score; the base 16 were drawn without regard to month, so the monthly table leans on the top-up.

Files: `leaning_labels.csv.gz`, `leaning_labels_channel_batched.csv.gz`, `leaning_runs.json`, `leaning_two_readings.json`, `leaning_two_readings_channels.csv`, `leaning_two_readings_changed_titles.csv`, `leaning_labels_repeat.csv.gz`, `leaning_repeat.json`, `leaning_repeat_channels.csv`, `leaning_repeat_changed_titles.csv`, `leaning_label_shares.json`, `leaning_summary.json`, `leaning_by_creator.csv`, `leaning_groups.csv`, `leaning_words.csv`, `leaning_split_half.csv`, `leaning_stability.csv`, `leaning_stability_channels.csv`, `leaning_by_group_month.csv`, `leaning_logodds.csv`, `leaning_logodds_summary.csv`, `leaning_logodds_agreement.csv`, `leaning_lexicon_validation.csv`, `leaning_lexicon_channels.csv`, `leaning_lexicon_titles.csv`, `allotax_summary.csv`, `allotax_contributions.csv`.
"""
