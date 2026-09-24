# Word association in political video titles: a research protocol

_Written 2026-09-23 for the 2026-01-01..2026-09-14 corpus. The first implementation is
`pipeline_titles/associations.py`; every number below comes from its run of that date
(`data/titles/analysis/assoc_*`)._

The question behind this protocol: when two words rise and fall together in the titles
(the motivating case is "Iran", "war" and "Epstein"), is that a relationship, or two
stories that happened to share a season? The protocol separates six things that all look
like "association" in a graph: co-movement over time, lead and lag, co-mention inside a
title, membership of one discourse cluster, change in a word's company over time, and
association that survives controls for the other stories and for the creators who tell
them. Each method is described the same way: the question it answers, its assumptions,
its limitations, what to save, and what it adds to the others. Section 10 turns the
Iran / war / Epstein hypothesis into a pre-specified test and reports what the first
pass found; section 11 describes the implementation.

## 0. The corpus, and the decisions it forces

| fact | value | consequence |
|---|---|---|
| titles in the window | 293,590 (274 channels) | large enough for title-level tests on words seen a few hundred times |
| after dropping verbatim repeats within a channel and genre | 284,906 | the pipeline's `is_dup` rule |
| after dropping a title an organization posts on two of its channels, or in two case / punctuation variants | 277,438 (7,468 dropped) | one document per editorial decision, matched on `title_key` within `organisation` |
| days with exact publish dates | 257 of 257 (21 titles still month-dated) | daily series are the workhorse; the Data API dates make that possible |
| full weeks | 36 (plus two part weeks) | weekly series are for display and robustness only: 36 points cannot carry a lag analysis |
| titles per day | median 1,232; weekends about half of weekdays | every daily model needs day-of-week terms |
| titles per channel | median 273, maximum 20,501; ten channels post 40 % of the corpus | pooled counts are the Indian news channels' counts; every statistic needs a channel-aware version |
| channel groups | left 122, neutral 42, right 110 (document 14) | the one between-channel grouping; used for the stratified checks |
| vocabulary at 100 titles from 10 channels | 3,665 terms, 274 of them phrases | 6.7 million candidate pairs |
| terms at 250 titles (about one a day) | 1,746 | the daily screen's vocabulary |

**Unit of observation.** A unique title. Presence of a term is binary: titles average
ten tokens and a word rarely repeats inside one, so counts add noise, not information.
Volume statistics (how many titles a day) use every title; association statistics use
the deduplicated set above. Cross-organization copies (a Reuters headline run by two
outlets, 1,264 rows) are kept: two outlets choosing the same headline is two decisions.

**Terms.** The pipeline's content-word rule on the normalized title (`title_norm`: show
names, episode numbers, date stamps and brand tags stripped; stopwords dropped;
possessives folded), plus phrases. A phrase is two content words adjacent or one stopword
apart that appear together in at least 50 titles from 10 channels with a title-level
normalized PMI of at least 0.5 ("press conference", "strait of hormuz", "epstein files";
`assoc_phrases.csv`, 511 of them, 11 with a stopword inside), and the year stage's bound
pairs (`year_bigrams.csv`) whatever their NPMI. The NPMI gate is what keeps a pair under
test from being fused: "iran war" is adjacent in thousands of titles but scores 0.2,
because each word has a large life of its own. A phrase is a term beside its words, not
instead of them: "epstein" counts whether or not the title says "epstein files", and a
word is never tested against the phrase that contains it or against the other word of
its own phrase, so "epstein" with "files" is not a pair in any table below (the
case-study concept tests, which work from indicator columns, still report it). The
tokenizer's one weakness shows in the phrase list: an accented name splits ("nicol s
maduro"), which a Unicode-aware token rule would fix.

**No stemming or lemmatization for names; a documented alias table for everything else.**
Political vocabulary is where stemmers do harm: "files" and "file" are different stories
("Epstein files" versus "file a lawsuit"), "strikes" is a noun and "strike" a verb in
these titles, and a name must never be conflated with a common word (Bondi, Gates, Kirk,
Graham, Homan, Rubio). The corpus has spaCy lemmas and part-of-speech tags for every
title (`annotations.parquet`), but ALL-CAPS titles defeat the tagger even after
truecasing. So: surface forms, lower-cased, possessives folded, and a hand-kept table of
merges (war / wars; strike / strikes) applied only where the analysis wants a concept
rather than a word. The table is data, versioned with the results.

**Named entities and concepts.** Multi-word names come from the bound-pair rule
(data-driven, transparent) rather than from the NER, whose labels on clickbait are noisy
("Hormuz" a person, "Trump PANICS" a person); the NER is useful as a source of candidate
names to check against the pair list. For hypothesis tests, a concept is a pre-registered
set of terms, and both the narrow and the broad reading are reported (section 10):
Iran = {iran} and {iran, iranian, iranians, tehran, khamenei, irgc, hormuz}; war = {war}
and {war, wars, strike(s), airstrike(s), bomb(s), bombing, missile(s), ceasefire};
Epstein = {epstein} and {epstein, maxwell, ghislaine, ghislaine maxwell}.

**Three ways to count a day.** For a term on a day: the pooled share (titles carrying
it over titles that day), the breadth (channels that used it over channels active that
day), and, at the week level, the year stage's channel-weighted share (the mean over
channels of the within-channel share). Breadth is the association workhorse: it cannot
be moved by one channel posting forty near-identical titles, and it answers directly
whether a word travelled across the landscape.

**Two time scales, and a warning.** Daily series (257 points) carry the lag analysis
and the regressions; weekly series are for the eye. The bigger limit is not points but
episodes: nine months of 2026 hold one Epstein-files season (late January to
mid-February), one Iran war (from February 28), and a handful of aftershocks. A lag
statistic is, in the end, a statement about how two or three episodes lined up. The
time-varying analysis of section 5 therefore compares months of 2026, not years.

## 1. Temporal association

**Question.** Do the two words' daily shares rise and fall together, once the calendar
(weekends), the slow drift of the year, and the changing volume of titles are taken out?

**Method.** For each term, the log breadth share by day, log((channels + 0.5) / (active
channels + 1)); the residual after an ordinary-least-squares fit on an intercept, six
day-of-week dummies and a cubic B-spline trend with six knots (about one knot per seven
weeks); Pearson correlation between residual series. The share already removes the
volume of titles; the spline removes drift too slow to be a story; the day-of-week terms
remove the fact that weekend titles come from different channels. The correlation's
significance uses an effective sample size that discounts the autocorrelation both
series retain (Pyper & Peterman 1998: 1/n_eff = 1/n + (2/n) sum over lags of
r_x(k) r_y(k), k = 1..14), then a t-test on n_eff - 2 degrees of freedom and
Benjamini-Hochberg over all pairs.

**Assumptions.** Approximate stationarity of the residuals; a linear (Pearson) relation
on the log scale; the spline flexible enough to remove drift but not the episodes. The
last is the identification problem of this whole section: a news episode that lasts six
weeks is trend to a ten-knot spline and signal to a three-knot one. The first pass
reports the correlation at three, six and ten knots, and a result that changes sign
across them is reported as trend-dependent, not as a finding.

**Limitations.** Words seen fewer than about 250 times have daily series that are mostly
zero; their correlations are noise, so the screen uses 1,746 of the 3,665 terms. Weekly
series would admit more words but leave 36 points. The BH correction over 1.4 million
pairs is severe; for a focal word, correct over its 1,684 partners instead, which is the
question actually asked.

**What the first pass found.** 1,522,989 pairs tested; 352 pass at q < 0.01 and 660 at
q < 0.05, and 597 of those replicate in both channel halves. 95 % agree most at lag zero
and 94 % are positive. Nearly all are one story seen twice: "lebanon" and "hezbollah"
(0.64), "khamenei" and "supreme leader" (0.64), "iran" and "war" (0.63, with an effective
n of 78 of 257 days). The few negatives are displacement: "iran" and "winter" (the
Olympics) at -0.40. Epstein's only correlated partners are "jeffrey" and "ties". The
residual series of the case-study words keep a lag-one autocorrelation of 0.5 to 0.7 (the
median term: 0.12), which is why the effective n matters, and the shift null of section 8
shows it does not matter enough: at the q < 0.05 cutoff (|r| = 0.26) the empirical false
discovery rate is 0.23, at |r| = 0.4 it is 0.06, and at 0.5 it is 0.03. The nominal q is
a screen; the shift-calibrated threshold is the test, and at |r| >= 0.4 there are 182
pairs, 181 of them replicated.

**Save.** `assoc_daily.csv.gz` (day x term: titles, channels, both shares, the
residual), `assoc_days.csv` (titles and active channels per day), `assoc_series_terms.csv`
(per term: residual autocorrelation), `assoc_temporal_pairs.csv.gz` (pairs at q < 0.05:
r, n_eff, p, q, the best lag and the correlation there).

**Complements.** This is the graph the eye sees, made honest. It cannot say whether the
words share titles (section 3) or which leads (section 2), and a correlation that
survives here can still be the news cycle itself (section 6).

## 2. Lag and cross-correlation

**Question.** When one word spikes, does the other spike before, after, or at the same
time, and at what delay?

**Method.** Three estimators, because each has a failure mode the others do not.
(a) The cross-correlation function of the residual series at lags -14..+14 days, with a
circular-shift null: the target series is rotated by a random offset of at least 21 days
2,000 times and the largest absolute cross-correlation in the window recomputed each
time, which preserves both series' autocorrelation and corrects for searching 29 lags at
once. (b) Prewhitening (Box & Jenkins): an autoregressive model chosen by AIC is fitted
to the leading series and the same filter applied to both; the cross-correlation of the
filtered series has the textbook 1.96 / sqrt(n) band, and its peak lag is the lead.
(c) Granger tests in a bivariate VAR on the residual series, order by AIC, both
directions: does the past of x improve the forecast of y beyond y's own past?
A fourth, for the eye and for few big events: the superposed-epoch (event) study, which
takes the days where the source word's residual exceeds two standard deviations (local
maxima only, so one episode is one event), averages the target's residual at each lag
around them, and draws a null band from as many random days with the same day-of-week
mix.

**Assumptions.** Stationarity after residualization (the spike season is the
non-stationarity of interest, so this holds only loosely); the AR filter adequate for
the leading series; for Granger, linear dynamics and a lag window that contains the
delay. Granger precedence is prediction, not cause: a shared driver that reaches one
channel type a day earlier than another produces it.

**Limitations.** Few episodes (section 0). Lags longer than about two weeks are
unidentifiable in nine months; the window should be shortened rather than widened. The
event study with two events is a description, not a test, and is labeled as one.

**What the first pass found.** Iran and war: cross-correlation peaks at lag zero
(0.67 raw, 0.44 prewhitened), Iran Granger-causes war (p = 0.007) and not the reverse:
the war is the Iran story. Epstein and Iran: no contemporaneous relation (0.007
prewhitened at lag zero); the largest cross-correlation in the window is negative,
-0.35 at lags of 10 to 13 days with Iran leading (raw residuals; no shift of 2,000
reached that size), -0.18 after prewhitening (band 0.12); Granger p = 0.38 and 0.81;
and in the event study, the two Iran spike days (January 12, March 1) are followed by an
Epstein residual below the null band at 12 and 13 days. Epstein coverage did not rise
with Iran; it fell about two weeks after Iran rose.

**Save.** `assoc_case_ccf.csv` (every lag: raw and prewhitened cross-correlation, the
band), the shift-null p-values and Granger F and p in `assoc_case_timeseries.csv`,
`assoc_case_events.csv` (event days, the response at each lag, the null band).

**Complements.** Section 1 says whether two series move together; this says in which
order, and the negative peak is the displacement that section 1's contemporaneous
correlation cannot see.

## 3. Title-level co-mention

**Question.** Do the two words appear in the same title more (or less) often than their
separate frequencies predict, and does that hold once the titles are compared only with
titles from the same channel in the same week?

**Method.** For every pair with at least 20 co-mentions, the 2 x 2 table (both, a only,
b only, neither) and three descriptive measures: the log-likelihood ratio G^2 (Dunning
1993), normalized PMI (Bouma 2009), and the log odds ratio with Haldane's correction.
The test of record is the Cochran-Mantel-Haenszel statistic over creator x week strata
(9,325 of them): within each stratum the observed co-mentions are compared with the
number expected if the two words were independent given their frequencies in that
channel's titles that week, and the stratum contributions are summed. Effect size: the
stratified lift, observed over expected, and for the case-study pairs the
Mantel-Haenszel odds ratio with the Robins-Breslow-Greenland interval. For all 5.9
million pairs this is three matrix products (observed = X'X on the title x term matrix;
expected and variance from the stratum x term count matrix), which is why it runs in
seconds. Pairs are also scored by breadth: the number of channels with at least one title
carrying both words.

**Which measure for short political titles.** Raw PMI is ranked by rarity: a pair seen
twice in two titles scores higher than "white house". NPMI bounds it but keeps the bias.
Chi-square misbehaves where expected counts are small, which is most cells here. G^2 is
the right screening statistic for sparse counts, and the log odds ratio is the right
effect size (it is what the stratified and per-channel analyses estimate too). But every
unstratified measure has two confounders built in: time (two words that peak in the same
week co-occur more than the global margins predict even if no title connects them), and
the creator (a channel that says both words in every title makes a pair). The CMH
stratification removes both at once, and the first pass shows the difference: 1,298
pairs pass a naive G^2 at p < 10^-6 and fail the stratified test at q < 0.01, while
3,520 pass only the stratified test (words that are both rare in most weeks and paired
in the week they appear). "Iran" and "war" co-occur 11,300 times against 2,442 expected
globally (odds ratio 14) but 4,971 expected within creator-weeks (Mantel-Haenszel odds
ratio 8.5): half the naive excess was timing.

**Assumptions.** Independence of titles within a stratum (near-duplicate titles inside a
channel-week break it, which is why the deduplication in section 0 matters and why a
permutation calibration is recommended in section 8); a common odds ratio across strata
for the Mantel-Haenszel estimate to be the quantity of interest (the CMH test is valid
without it; the Breslow-Day test or the per-channel meta-analysis of section 7 checks
it).

**Limitations.** Requiring 20 co-mentions selects positive associations; negative ones
(words that avoid each other) need a separate screen on pairs with high expected and low
observed counts, and the first pass tabulates 2,094 of them at q < 0.01 (761 replicated
in both channel halves), among them "iran" with "epstein". Title-level association is
dominated by syntax: with the fixed phrases removed as terms, the strongest remaining
pairs are still templates ("pm" and "modi" from nine channels, "warning" and "issues",
"kim" and "north korea"), which is useful for extending the phrase list and useless as
discourse.

**What the first pass found.** 31,420 pairs tabulated; 19,130 positive and 2,094 negative
at q < 0.01; 12,718 of the positive ones replicate in both channel halves (6,411 do not:
half-corpus power, and channel-specific pairs). Ten fixed-margins permutations put the
empirical false-discovery rate at the q < 0.01 cutoff (z = 2.71) at 0.012 for positive
and 0.023 for negative associations, at z >= 4 at 0.0006, and at z >= 5 at 0.0001: the
stratification leaves the nominal p-values honest here, unlike in the temporal screen.

**Save.** `assoc_pairs.csv.gz` (per pair: both words' counts, observed, global
expectation, G^2, NPMI, log odds ratio, stratified expectation, lift, CMH z, p and q,
channels, the z and q in each channel half, `replicated`), `assoc_pairs_calibration.csv`
(observed and null counts and the empirical FDR at each z), `assoc_phrases.csv`,
`assoc_vocab.csv`.

**Complements.** Sections 1 and 2 are about the calendar; this is about the sentence.
Two words can be temporally associated and avoid each other in titles (Iran and
Epstein, section 10), or share titles at a steady rate all year without ever co-spiking.

## 4. The word-association network

**Question.** What are the discourse clusters of the year, and are "Iran", "war" and
"Epstein" in one of them?

**Method.** Nodes are vocabulary terms; an edge is a pair that passes three gates at
once: q < 0.01 on the stratified test, lift of at least 2 (twice the expected
co-mentions), and at least 5 channels co-mentioning it. Weight is log2 of the lift.
Communities by Louvain (networkx, seeded), and, because Louvain's partition changes with
its seed, the co-membership of the focus words across 20 seeds. Node measures: degree
(how many partners), strength (weighted degree: how much association a word carries),
betweenness (how often a word lies on the shortest path between others: a bridge between
discourses), and community.

**Assumptions.** The three gates define an edge; the network is only as meaningful as
they are. Modularity-based communities assume the graph has block structure and are
resolution-limited (small clusters merge). Betweenness on an unweighted shortest path
treats every edge alike.

**Limitations.** A partition is one of many similar ones; membership near a boundary is
unstable, which is why the seed check exists and why a channel bootstrap (resample
channels, rebuild the graph, count co-membership) is the next step. Leiden (igraph)
would guarantee connected communities; it is not installed and Louvain suffices for a
first pass.

**What the first pass found.** 2,767 nodes, 11,714 edges (each replicated in both
channel halves), 31 communities, modularity 0.59. "Iran" and "war" sit in one community
(negotiations, deal, options, proposal, oman, centcom, war powers, ceasefire), beside a
military cluster (oil, hormuz, strikes, iranian, missile, israel, drone); "Epstein" in
the Washington-investigations cluster (senate, hearing, doj, fbi, testifies, blanche,
hegseth, files). Across 20 seeds Epstein never shares a community with Iran or with war
(0 of 20); Iran and war share one in 8 of 20. Epstein has the highest betweenness in the
graph (0.038, ahead of "senate" and "shooting"): it is a bridge between the DOJ /
hearings vocabulary and the Trump / Clinton vocabulary, not a member of the war
discourse. Its neighbors by lift: subpoena, howard (Lutnick), survivors, comer, jeffrey,
oversight, probe, suicide, note, clinton, deposition, testify, ties, hillary, gates.

**Save.** `assoc_nodes.csv` (measures and community per term), `assoc_edges.csv`,
`assoc_communities.csv` (size and top terms per community), `assoc_focus_neighbors.csv`;
and the page to explore it, `pipeline_titles/reports/word_network.html`
(`python -m pipeline_titles.network_page`): every node and edge on a ForceAtlas2 layout,
a word's partners with their lift, z, titles and channels on a click, each month's own
edges, a lift threshold, and the communities as a toggleable legend. Self-contained, no
libraries.

**Complements.** The network is section 3 read globally: it answers "same discourse?"
where section 3 answers "same sentence?". It is blind to time, which section 5 restores.

## 5. Time-varying networks

**Question.** Does a word's company change over the year, and which words changed most?

**Method.** The stratified co-mention analysis of section 3 rerun per month (strata are
creator x week inside the month; thresholds lowered to 10 co-mentions and 3 channels
because a month has a ninth of the titles), each term's top-20 neighbors by lift among
the month's edges, and drift as the Jaccard overlap of a term's neighbor set between
consecutive months (only where both months give it at least five neighbors). A term is
ranked by its mean Jaccard; low is churn.

**Assumptions.** Comparable power across months (the partial September is not), the
same gates in every month, a neighbor set of twenty large enough for Jaccard to be
stable.

**Limitations.** Jaccard of top-k lists is coarse and punishes words with sparse
neighborhoods; rank-turbulence divergence (already in `textstats.py`) between the two
months' full neighbor rankings, or the cosine between the term's rows of the two
months' lift matrices, are the finer versions. Nine months is a short panel, and a
year's vocabulary drifts for reasons (new names) that are not discourse change.

**What the first pass found.** Trump's neighborhood churns most of the five focus
words (mean Jaccard 0.09), then Iran's (0.11: carriers and warships in January, Oman and
Araghchi in February, Witkoff and proposals in March, Hormuz closure and seized vessels
in April, Doha and a resolution in June, reopening in August), then Israel (0.17),
Epstein (0.21) and war (0.24). Epstein's company is one story moving through its
institutions: Blanche and the Clintons' contempt in January, survivors and Lutnick in
February, depositions and the Oversight subpoena in March, Melania and denials in April,
Lutnick, a suicide note and Bondi in May, Gates and a leak in June, victims and Blanche
in July, the DOJ, Blanche and a lawsuit in August. The words associated with Epstein never
include Iran or war in any month.

**Save.** `assoc_monthly_neighbors.csv.gz` (month x term x rank: neighbor, lift, z,
co-mentions, channels), `assoc_drift.csv`, `assoc_focus_monthly.csv`.

**Complements.** Section 4 with a clock. A pair that is an edge in one month and not
another is the "emerging association" of section 9's rankings.

## 6. Conditional association

**Question.** Does the Epstein-Iran relation, if any, survive controls for the stories
that could drive both, and for the general intensity of political news?

**Method.** Two layers. At the day level, a negative-binomial regression of the
number of Epstein titles on an offset of log titles that day, day-of-week dummies, the
spline trend, and the standardized log-shares of the candidate driver (Iran, or war) and
the controls (Trump, Israel, the share of titles in political topics from
`topics.csv.gz`); Newey-West (HAC, 7 lags) standard errors; the coefficient reported as
an incidence-rate ratio per one standard deviation. A lagged specification replaces
today's Iran share with its mean over the previous seven days. At the title level, the
stratification of section 3 is the conditional model: comparing titles within the same
creator and week (or day) conditions on everything that varies between channels and
between weeks, including the news cycle, and asks only whether, among one channel's
titles of one week, the Iran titles are the Epstein titles. Partial correlations between
residual series, and a graphical lasso over the top few hundred series for a sparse
conditional-dependence network, are the extensions; both are one call in scikit-learn
and neither was needed for the case.

**What to control for, and what not to.** Controls are candidate common causes (Trump,
Israel, news intensity), not parts of the concept: conditioning on "files" when testing
Epstein is conditioning on the outcome. Write the control set down before running.

**Assumptions.** The count model's mean structure (log-linear in the covariates) and its
overdispersion parameter; HAC errors handle residual autocorrelation but not a misfit
trend. Collinearity among story shares (Iran and war correlate at 0.67) widens intervals
and makes single coefficients hard to read; report the joint and the one-at-a-time
models.

**Limitations.** Day-level regressions with 257 rows and a few big episodes are
fragile; the title-level stratified estimate is the robust one. Neither can turn
association into cause.

**What the first pass found.** Iran's incidence-rate ratio for Epstein titles is 1.21
(0.93 to 1.58, p = 0.15) with war in the model and 1.00 (0.80 to 1.25) without; war's is
0.72 (0.56 to 0.93, p = 0.013); Trump's is 0.84 (p < 0.001); the previous week's Iran
share gives 0.86 (0.64 to 1.15). Days heavy with war and Trump have fewer Epstein
titles, not more.

**Save.** `assoc_case_regression.csv` (every specification: covariate, IRR, interval,
HAC p), the stratified pair tests in `assoc_case_pairs.csv`.

**Complements.** Sections 1 to 3 establish that a relation exists; this asks whether it
is the relation claimed or a shared cause.

## 7. Creator-level analysis

**Question.** Is an association a property of the landscape, of one ideological group,
or of a few channels?

**Method.** Four instruments, in order of strength. Breadth: how many channels co-mention
the pair at all (every pair table carries it). Group-stratified estimates: the
Mantel-Haenszel odds ratio within each of the left, neutral and right channel groups,
and a chi-square test of heterogeneity across the three log odds ratios. Leave one
organization out: the CMH estimate recomputed without each organization (sister
channels leave together), reporting the extremes. Per-channel meta-analysis: each
channel with at least five titles of each word gives a log odds ratio and standard error
(Haldane-corrected 2 x 2), pooled by DerSimonian-Laird random effects, which yields the
between-channel variance tau^2, the share of variance that is heterogeneity (I^2), and
the share of channels above and below one. The reading: (a) a general trend is many
channels on the same side with low heterogeneity; (b) a group trend is a significant
group heterogeneity with the groups themselves internally consistent; (c) a
creator-specific phenomenon is a few channels significant and the rest not, high
heterogeneity, and a leave-one-out that moves the estimate.

**Assumptions.** Channels are the exchangeable units (sister channels are handled by
organization); the per-channel odds ratios are estimable (rare pairs in small channels
are not, and those channels drop out); the random-effects model's normal distribution of
true effects.

**Limitations.** Per-channel time series are too sparse for lag analysis except in the
largest channels; creator-level lag questions are answered by group-level series
(left, neutral, right breadth series) instead. A mixed model with creator random
intercepts (statsmodels' `BinomialBayesMixedGLM`) is the formal version of the
stratified analysis and is slow on 277,000 rows; the CMH and the meta-analysis give the
same answer faster.

**What the first pass found.** Epstein and Iran within creator-weeks: odds ratio 0.22
(0.17 to 0.28) in left channels, 0.15 (0.11 to 0.21) in neutral, 0.40 (0.27 to 0.59) in
right (heterogeneity p = 0.001: the right avoids the pairing less, but every group avoids
it). Leaving out any one organization moves the estimate between 0.20 and 0.27. Over 109
channels the random-effects log odds ratio is -0.54 (odds ratio 0.58), I^2 = 0.69, and
35 % of channels have an odds ratio above one, 6 % significantly so (HasanAbi, Bad
Empanada, Marc Lamont Hill, with wide intervals for Candace Owens clips, RSBN, the
Lincoln Project and Fight Back), 22 % significantly below. The 156 co-mention titles come
from 65 channels and are of two kinds: news digests that list the day's stories ("Iran |
Ukraine | Epstein Files") and a frame, mostly on the anti-war left, that reads the war as
a distraction from the files ("Trump's WAR ON IRAN to HIDE PAST", "the Epstein regime
BEGGING Iran for mercy"). That frame is a creator-specific phenomenon (c), not a trend.

**Save.** `assoc_case_channels.csv` (per channel and pair: counts, log odds ratio,
standard error, group), the group, leave-one-out and meta columns of
`assoc_case_pairs.csv`.

**The audiences' own networks.** The pair test of section 3 also runs on each channel group
alone (its own creator x week strata, its own channel halves, the same gates), giving a left,
a neutral and a right network (`assoc_edges_<group>.csv`, `assoc_nodes_<group>.csv`, with
communities and node months), and every edge of the whole network carries the co-mentions
each group contributed (`co_left`, `co_neutral`, `co_right` in `assoc_edges.csv`;
`assoc_audience.json` has the groups' title counts). A third of the titles clears a third of
the gates: 1,564 edges on the left, 5,585 on the neutral channels, 1,525 on the right, against
11,714 for the whole. The page shows the four as separate networks, and colors the whole
network's edges by audience balance, the difference of the left and right co-mention rates per
thousand titles over their sum.

**Complements.** Every other section can be fooled by one channel's habits; this is the
check that none was.

## 8. Statistical significance across millions of pairs

**Minimum-frequency gates come first.** They are not a correction; they define the
population of tests. A term needs 100 titles from 10 channels (3,665 terms); a daily
series needs 250 titles; a pair is tabulated at 20 co-mentions and becomes an edge at 5
channels. Each gate is a parameter in `associations.py` and belongs in the write-up.

**Benjamini-Hochberg on the gated population.** Within a table, BH at q = 0.01 for
edges and q = 0.05 for the temporal screen. The p-values are positively dependent
(shared words, shared weeks), for which BH remains valid in the PRDS sense;
Benjamini-Yekutieli is the safe fallback where dependence is arbitrary, at a cost of
roughly log(m) in power. Correct within the question asked: for one focal word, over
its partners; for the whole graph, over all pairs.

**Calibrate with a permutation null that keeps the nuisance structure.** The nominal
CMH p-values assume independent titles inside a stratum; templated and near-duplicate
titles violate that and make them anti-conservative. The fix is a fixed-margins
permutation: shuffle term occurrences among the titles of each creator-week so that
every title keeps its number of terms and every term keeps its count in that stratum
(the curveball algorithm of Strona et al. 2014 on the binary matrix), recompute the
whole pair table, and estimate the empirical false-discovery rate at any threshold as
the null count above it over the observed count. For the time-series layer, the
circular-shift null of section 2 and a moving-block or stationary bootstrap (Politis &
Romano 1994) of the residual correlation are the equivalents. The first pass runs both.
Ten curveball permutations (about six seconds each) give the pair table an empirical FDR
of 0.012 at its q < 0.01 cutoff and 0.0006 at z >= 4, so the stratified p-values can be
used as they are. Two hundred independent shifts of every daily series give the temporal
screen an empirical FDR of 0.23 at its q < 0.05 cutoff and 0.17 at its q < 0.01 cutoff:
the effective-n correction is not enough, and the calibrated rule is |r| >= 0.4 (FDR
0.06) or 0.5 (0.03). The stationary bootstrap (mean block seven days, 1,000 draws) gives
the case-study correlations their intervals in `assoc_case_timeseries.csv`.

**Effect-size floors and replication.** A significant pair with lift 1.1 is a fact about
sample size. Edges need lift 2; the temporal screen should report r, not just q. And an
association is unusual, rather than lucky, when it replicates: across the two halves of
a random split of the channels (organizations kept together; every pair table carries the
statistic in each half and a `replicated` flag, and only replicated pairs become edges),
across the three channel groups, and across at least two episodes in time. The case-study words satisfy the last two tests in the negative
direction (every group, every episode: avoidance).

**The read.** A genuine association passes the gates, survives the stratified test at a
small q, has a lift or odds ratio worth reporting, replicates across channel halves and
groups, and is not moved by leaving out an organization. A chance association fails one
of these, usually the stratified test or the leave-one-out.

## 9. Visualization

The pipeline's figures stage (`python -m pipeline_titles.figures`) draws from tables; the
tables of section 11 are enough for every figure below. Rules that apply to all: shares
not counts; the channel-breadth series beside the pooled one; annotate the episodes on
the time axis (the files release, February 28); log scale for shares that span orders of
magnitude; the same term order and the same node positions across panels, so change is
visible as change.

- **Word-frequency time series and overlaid trajectories**: daily breadth share of the
  focus words with a seven-day centered mean, one panel per word plus one overlay
  (`assoc_case_daily.csv`); small multiples for many words.
- **Cross-correlation plots**: the raw and prewhitened cross-correlation by lag with the
  1.96 / sqrt(n) band and the shift-null maximum drawn as a horizontal line
  (`assoc_case_ccf.csv`); the event-study panel with its null band
  (`assoc_case_events.csv`).
- **Association heatmaps**: the top-k terms by strength, ordered by community, colored by
  log2 lift with the non-significant cells blank (`assoc_pairs.csv.gz` joined to
  `assoc_nodes.csv`); a second heatmap of residual correlations in the same order.
- **Temporal co-occurrence matrices**: one heatmap per month in a grid, same term order
  (`assoc_monthly_neighbors.csv.gz`).
- **Word networks**: a force layout of the edge table, nodes sized by strength and
  colored by community, the focus words labeled; then the ego networks of "epstein" and
  "iran" (`assoc_edges.csv`, `assoc_nodes.csv`).
- **Changing communities**: an alluvial (Sankey) diagram of community membership by
  month for the top terms, communities matched across months by overlap; or the network
  with fixed positions from the full-year layout redrawn per month.
- **Rankings of emerging associations**: a table of pairs whose lift rose most between
  two windows, with intervals and channel counts; and the drift ranking of
  `assoc_drift.csv`.

All of these are drawn by `python -m pipeline_titles.figures_associations` (also run by the
figures stage) into `pipeline_titles/reports/figures/`: `assoc_01_trajectories.png` and
`assoc_01b_small_multiples.png` (the three words by day, and the twenty biggest spikes),
`assoc_02_crosscorrelation.png` (raw and prewhitened cross-correlation with the band, and
the event study), `assoc_03_heatmap.png` (the eighty battery words against each other,
co-mention red and avoidance blue, ordered by community), `assoc_04_monthly_matrices.png`
(the twenty spike words month by month), `assoc_05_network.png` and `assoc_05b_ego.png`
(the 150 strongest terms by community; Epstein's and Iran's neighborhoods),
`assoc_06_network_by_month.png` (the same layout with each month's edges) and
`assoc_07_emerging.png` (the strongest associations between established words that are new
in a month: State of the Union in February, the NATO summit in July, oil and prices in
March, Andrew and arrest in February). What the figures show is what the tables said:
the Epstein and Iran seasons are weeks apart, Epstein sits in the investigations cluster
at the far side of the map from the war cluster, and the year's new associations are
events, not drift between stories.

## 10. The Iran / war / Epstein case study

**Hypothesis.** The appearance of "Epstein" in political video titles is temporally
associated with increased discussion of "Iran" and/or "war", beyond what their
individual frequencies and the general political-news cycle would produce.

**Data to construct.** (i) The daily table: titles and active channels per day; for each
concept (narrow and broad readings of section 0) the titles carrying it, the channels
carrying it, the pooled and breadth shares, and the residuals after day-of-week and
trend; the share of political titles as the news-intensity control. (ii) The title
table: one row per unique title with creator, organization, group, day, week, and the
concept indicators. Both are written by the stage (`assoc_case_daily.csv`; the title
table is built in memory from `titles_prepared.parquet`).

**Null hypotheses.** H0-time: after removing day-of-week and trend, the daily share of
Epstein titles is independent of the daily share of Iran (war) titles at every lag in
-14..+14 days. H0-title: within a creator's titles of one week (one day), whether a
title mentions Iran (war) is independent of whether it mentions Epstein.

**Tests, in order.** T1 contemporaneous correlation of residual series with the
circular-shift null and the three-knot sensitivity. T2 cross-correlation with the
shift-null maximum, prewhitened cross-correlation with its band, Granger both ways.
T3 event study around Iran spike days. T4 the negative-binomial day-level regression with
controls, contemporaneous and lagged. T5 CMH within creator x week and creator x day,
with the naive odds ratio beside it. T6 by channel group, leave one organization out,
and the per-channel random-effects meta-analysis. Every test is run for the narrow and
the broad concepts.

**Effect sizes to report.** r with its shift-null p and its range over spline
flexibility; the peak cross-correlation with its lag and band; Granger F and p; the
incidence-rate ratio per standard deviation with a HAC interval; the Mantel-Haenszel odds
ratio with its interval and the stratified lift; the group odds ratios and the
heterogeneity p; the leave-one-out range; tau^2, I^2 and the shares of channels above
and below one.

**What would count.** Convincing support: a positive residual correlation or a positive
peak cross-correlation with Iran leading that survives the shift null and does not
change sign across spline settings; a positive Iran effect in the regression with the
war, Trump and news-intensity controls in; a Mantel-Haenszel odds ratio above one within
creator-weeks (the titles themselves connect the stories) or, failing that, the same
positive lag in all three channel groups and in more than one episode; and a
leave-one-out range that stays above one with low heterogeneity. Weak evidence: a weekly
correlation that disappears under detrending or under the shift null; a sign that
depends on the spline; a result carried by one group or one organization; a positive
title-level odds ratio driven by a handful of channels with a random-effects pool near
one.

**Result of the first pass (2026-09-23).** The hypothesis is not supported on this
corpus, and the evidence against it is consistent across layers.

| test | Epstein x Iran | Epstein x war | Iran x war (reference) |
|---|---|---|---|
| T1 residual r (pooled; breadth) | -0.06; -0.03, shift p 0.62; 0.85 | -0.20; -0.13, p 0.07; 0.20 | 0.67; 0.63, p < 0.0005 |
| T1 r at 3 / 6 / 10 knots | -0.15 / -0.06 / +0.19 | -0.28 / -0.20 / +0.02 | 0.76 / 0.67 / 0.55 |
| T1 stationary-bootstrap 95 % interval for r (pooled) | -0.26 to 0.14 | -0.38 to 0.03 | 0.55 to 0.77 |
| T2 peak cross-correlation (raw) | -0.35 at Iran leading 10-13 days, shift p < 0.0005 | -0.24 at war leading 11 days, p = 0.26 | 0.67 at lag 0 |
| T2 prewhitened peak (band 0.12) | -0.18 at lag -13 | -0.16 at lag +8 | 0.44 at lag 0 |
| T2 Granger p (a to b; b to a) | 0.38; 0.81 | 0.50; 0.18 | 0.007; 0.50 |
| T3 event study | Epstein below the null band 12-13 days after the two Iran spike days | nothing outside the band that repeats | war above the band from -1 to +7 days |
| T4 IRR per SD (joint model) | Iran 1.21 (0.93-1.58), p = 0.15 | war 0.72 (0.56-0.93), p = 0.013 | (Trump 0.84, p < 0.001) |
| T5 odds ratio, naive; creator-week; creator-day | 0.21; 0.22 (0.18-0.26); 0.19 (0.16-0.23) | 0.23; 0.24 (0.19-0.30); 0.21 (0.16-0.27) | 14.1; 8.5 (8.2-8.9); 8.4 |
| T6 groups left / neutral / right | 0.22 / 0.15 / 0.40, heterogeneity p = 0.001 | 0.26 / 0.15 / 0.46, p = 0.02 | 6.5 / 11.2 / 6.4 |
| T6 leave one organization out | 0.20 to 0.27 | 0.23 to 0.29 | 7.8 to 11.3 |
| T6 meta over channels: pooled OR, I^2, share > 1 (significant) | 0.58, 0.69, 35 % (6 %) | 0.64, 0.43, 36 % (5 %) | 16.0, 0.94, 98 % (90 %) |

Read together: Epstein and Iran were two stories three to four weeks apart (Epstein's
files season peaked in the weeks of February 2 and 9 at about 10 % of titles; Iran rose
from the week of February 23 and peaked in the week of March 2 at 36 %), and the graph
that suggested they co-spiked was reading the same season. Within a channel and week
they avoid each other in titles (a title is about one thing), the day-level regression
finds war and Trump crowding Epstein out rather than pulling it in, and the only lagged
relation is displacement: Epstein coverage fell about two weeks after Iran spiked. The
one positive finding is small and creator-specific: seven channels, four of them on
the left, wrote titles that fuse the two ("Iran war as a distraction from the
Epstein files"), enough to make 6 % of channels significant on their own and none of the
pooled estimates. The broad concepts give the same answers as the narrow ones.

## 10b. The same battery over the year's twenty biggest spikes

The case-study tests also run over every pair of a word list (`--battery spikes:20`
takes the top twenty of `year_spikes.csv`, the words whose weekly share rose furthest
above their own average; `--battery a,b,c` takes a list). Per pair it reports the
detrended correlation with its bootstrap interval and shift p, the peak cross-correlation
with its shift null and its prewhitened confirmation, Granger both ways, the
Mantel-Haenszel odds ratio within creator-weeks and creator-days and in each channel half,
the group odds ratios and their heterogeneity, the leave-one-organization-out range, and
the per-channel meta-analysis; then two readings. The timing reading names a lag only when
the raw peak beats the shift null at p < 0.01, is at least 0.3 in size, and the prewhitened
peak agrees in sign and lag (within three days) above its band. The title reading is
"none" unless the stratified statistic passes in both channel halves, then "group" when the
channel groups disagree (heterogeneity p < 0.01 with one group at null), "channels" when
fewer than a tenth of channels carry it on their own or one organization can move it under
the threshold, and "landscape" otherwise. 190 pairs take two minutes
(`assoc_battery_words.csv`, `assoc_battery_pairs.csv`).

**Run of 2026-09-23** (iran, war, epstein, venezuela, ice, deal, maduro, greenland,
fauci, trump, state, platner, epstein files, ceasefire, china, shooting, minneapolis, alex,
lindsey graham, america; "alex" is Alex Pretti, "state" the State of the Union week).
Title level: 99 pairs show nothing, 32 are landscape-wide, 6 differ by group, 53 rest on a
few channels; among the 91 that pass, 68 are avoidance and 23 co-mention. The
co-mentions are the year's stories recovered from the pairs alone: Iran with war, Trump,
deal and ceasefire; ICE with shooting, Minneapolis and Alex Pretti; Venezuela with Maduro;
Greenland with Trump; Epstein with its files. The avoidances are the stories that do not
share a title: Iran with Epstein, ICE, shooting, Venezuela and Greenland, Trump with ICE,
Minneapolis and shooting. The six group pairs are readable: Iran with Venezuela and with
Greenland are avoided on the left (odds ratios 0.29 and 0.22) and not on the right (1.16
and 1.05, both including one), where the three make one "Trump's wars" frame; Minneapolis
with Alex Pretti co-mention on the left and neutral channels (3.8 and 6.7) and barely on
the right (1.3). Timing: twelve pairs earn a reading. Three co-move (Iran and war,
Epstein and its files, shooting and Minneapolis); the Iran-to-Epstein displacement of
section 10 is one; the rest are small (peaks of 0.31 to 0.36) and mostly involve the
generic "america", which is the June 29 "America 250" week meeting other stories. No pair
in the list shows a positive lead of one story into another beyond its own words.

**Run over eighty words (2026-09-23).** The list rule for a longer list: the spike
ranking recomputed for all 400 year-stage words (`spike_ranking`), a word on the generic
list skipped (GENERIC in the module: "america", "big", "says", "th", and so on), a fragment
replaced by its phrase when the phrase carries 60 % of its titles, a timing reading
requiring p < 0.001 against 1,000 shifts because 3,160 pairs at p < 0.01 would admit about
thirty by chance, and a word with its own phrase counted as "phrase" rather than as a pair.
The run took 53 minutes. Of 3,160 pairs, 877 pass the title-level test in both channel
halves: 621 avoidances and 256 co-mentions; 255 pairs are landscape-wide, 54 differ by
group, 568 rest on a few channels, 2,277 show nothing. The per-word table
(`assoc_battery_summary.csv`) reads as a map of the year: Trump and Iran are the hubs
(20 and 15 landscape co-mentions, 22 and 23 avoidances each), and every other word's
partners are its own story (oil with prices, Venezuela and Hormuz; Minnesota with fraud,
ICE and shooting; Charlie Kirk with hearing, case, trial and Candace Owens; Epstein with
DOJ, Melania, Andrew, hearing, the UK and arrests). The 54 group pairs are where the three
audiences frame differently: Iran with Netanyahu is a right-channel pairing (odds ratio
3.1 against 1.1 on the left), Iran with Venezuela and Greenland a right-channel one too,
Election with Texas a left one (5.5 against 1.4). Timing: 57 readings, forty of them
co-movement at lag zero inside one story (Iran and strikes, Israel and Lebanon, NYC and
Mamdani, UK and Starmer, oil and prices); the leads inside a story are one to three days
(Iranian leads Israel by a day, oil leads Iranian by three); and about ten readings of nine
to fourteen days between unrelated words at peaks of 0.31 to 0.34 are the residue the
threshold still admits, three of them expected by chance, and should be read as noise
unless a later corpus repeats them. Epstein's own row: six landscape co-mentions, all
its own story; two avoidances, Iran and Trump; no timing lead into any war word.

## 11. The first implementation

`pipeline_titles/associations.py` (about 1,050 lines; pandas, NumPy, SciPy sparse,
statsmodels, scikit-learn for the spline basis, networkx) runs the whole protocol,
including the ten permutations and two hundred shifts, in about two minutes on the M4
Pro and writes 27 files to `data/titles/analysis/assoc_*`. It reads
`titles_prepared.parquet`, `creators.csv`, `leaning_by_creator.csv`, `year_bigrams.csv`
and `topics.csv.gz`, reuses the year stage's tokenizer, and is not yet registered in
`run_all` (add `"associations"` after `"year"` in `STAGES` to make it a stage of record).
`--case-only` reruns section 10 in 45 seconds.

What it does not yet do, in the order worth building: a channel bootstrap of community
co-membership; rank-turbulence drift instead of Jaccard; a Unicode-aware token rule for
accented names; the negative-association screen of section 3 as its own table; and the
figures of section 9 in the figures stage. The battery's per-pair regression is the one case-study test it
skips, and `--battery-summary` rebuilds its readings and per-word table from the saved
pairs without recomputing.

## References

Benjamini, Y. & Hochberg, Y. (1995). Controlling the false discovery rate. _JRSS B_ 57.
Benjamini, Y. & Yekutieli, D. (2001). The control of the FDR under dependency. _Ann. Stat._ 29.
Blondel, V. et al. (2008). Fast unfolding of communities in large networks. _J. Stat. Mech._
Bouma, G. (2009). Normalized (pointwise) mutual information in collocation extraction. _GSCL_.
Box, G. & Jenkins, G. (1976). _Time Series Analysis: Forecasting and Control_.
Church, K. & Hanks, P. (1990). Word association norms, mutual information, and lexicography. _Comp. Ling._ 16.
DerSimonian, R. & Laird, N. (1986). Meta-analysis in clinical trials. _Controlled Clinical Trials_ 7.
Dodds, P. S. et al. (2023). Allotaxonometry and rank-turbulence divergence. _EPJ Data Science_ 12.
Dunning, T. (1993). Accurate methods for the statistics of surprise and coincidence. _Comp. Ling._ 19.
Granger, C. (1969). Investigating causal relations by econometric models and cross-spectral methods. _Econometrica_ 37.
Hamilton, W., Leskovec, J. & Jurafsky, D. (2016). Diachronic word embeddings reveal statistical laws of semantic change. _ACL_.
Mantel, N. & Haenszel, W. (1959). Statistical aspects of the analysis of data from retrospective studies. _JNCI_ 22.
Monroe, B., Colaresi, M. & Quinn, K. (2008). Fightin' words. _Political Analysis_ 16.
Politis, D. & Romano, J. (1994). The stationary bootstrap. _JASA_ 89.
Pyper, B. & Peterman, R. (1998). Comparison of methods to account for autocorrelation in correlation analyses of fish data. _Can. J. Fish. Aquat. Sci._ 55.
Robins, J., Breslow, N. & Greenland, S. (1986). Estimators of the Mantel-Haenszel variance consistent in both sparse data and large-strata limiting models. _Biometrics_ 42.
Strona, G. et al. (2014). A fast and unbiased procedure to randomize ecological binary matrices with fixed row and column totals. _Nature Communications_ 5.
Traag, V., Waltman, L. & van Eck, N. (2019). From Louvain to Leiden. _Scientific Reports_ 9.
