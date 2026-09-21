# 6. Drift: how titles changed from January to September

**The question.** Did the landscape's title style move over 2026, and did the three channel groups move differently? Months are the only safe unit: YouTube listing dates are month-accurate, and September covers the 1st to the 14th only (shown, never compared on volume).

## The finding in one paragraph

Not much, and not in one direction. Of 90 group x genre x measure series (twelve dimensions and three hooks, nine months), 9 show a monotone trend (|Spearman| >= 0.6, p < 0.05). Averaged over all creators the outrage share of edited uploads is flat (62 % in January, 60 % in August). Underneath, the left group cooled slightly (outrage 70 % to 65 %), the right group's question framing fell over the year, and the neutral group moved on its stream titles rather than its uploads. Topic turnover is steadier than style: creators re-mix their subjects every month by a similar amount, most in the right group and least in the neutral one, whose news outlets follow the same news flow.

## Outrage share by month (edited uploads; mean of creators)

![Outrage-frame share by month, one panel per channel group, against the all-creator mean (gray dashed).](figures/06_drift_outrage.png)
*Outrage-frame share by month, one panel per channel group, against the all-creator mean (gray dashed).*

| group | 2026-01 | 2026-02 | 2026-03 | 2026-04 | 2026-05 | 2026-06 | 2026-07 | 2026-08 | 2026-09 |
|---|---|---|---|---|---|---|---|---|---|
| all channels (mean of creators) | 0.62 | 0.62 | 0.65 | 0.62 | 0.62 | 0.62 | 0.61 | 0.60 | 0.60 |
| left channels | 0.70 | 0.69 | 0.70 | 0.71 | 0.67 | 0.70 | 0.67 | 0.65 | 0.67 |
| neutral channels | 0.37 | 0.38 | 0.44 | 0.39 | 0.37 | 0.36 | 0.35 | 0.41 | 0.35 |
| right channels | 0.62 | 0.63 | 0.67 | 0.64 | 0.66 | 0.64 | 0.63 | 0.63 | 0.61 |


## Tone factor (F1, positive vs outrage; topic-controlled) by month

![The tone factor by month, per channel group.](figures/06_drift_tone.png)
*The tone factor by month, per channel group.*

| group | 2026-01 | 2026-02 | 2026-03 | 2026-04 | 2026-05 | 2026-06 | 2026-07 | 2026-08 | 2026-09 |
|---|---|---|---|---|---|---|---|---|---|
| all channels (mean of creators) | 0.04 | 0.11 | -0.04 | -0.02 | 0.07 | 0.11 | 0.12 | 0.04 | 0.03 |
| left channels | -0.11 | 0.01 | -0.18 | -0.16 | 0.00 | -0.03 | -0.01 | -0.02 | -0.04 |
| neutral channels | 0.38 | 0.41 | 0.26 | 0.24 | 0.39 | 0.46 | 0.59 | 0.19 | 0.31 |
| right channels | 0.09 | 0.10 | 0.00 | 0.00 | 0.02 | 0.09 | 0.10 | 0.05 | 0.01 |


## ALL-CAPS factor (F9) by month

![The ALL-CAPS factor by month, per channel group.](figures/06_drift_caps.png)
*The ALL-CAPS factor by month, per channel group.*

| group | 2026-01 | 2026-02 | 2026-03 | 2026-04 | 2026-05 | 2026-06 | 2026-07 | 2026-08 | 2026-09 |
|---|---|---|---|---|---|---|---|---|---|
| all channels (mean of creators) | -0.01 | -0.05 | 0.00 | -0.05 | 0.02 | 0.01 | -0.07 | -0.10 | -0.04 |
| left channels | 0.15 | -0.03 | 0.01 | 0.02 | 0.12 | -0.01 | -0.04 | -0.10 | -0.03 |
| neutral channels | -0.15 | -0.15 | -0.13 | -0.22 | -0.18 | -0.18 | -0.31 | -0.31 | -0.16 |
| right channels | -0.13 | -0.04 | 0.04 | -0.04 | -0.01 | 0.11 | 0.00 | -0.01 | -0.01 |


## The trends that are strong enough to report

| group | genre | measure | spearman_trend | first_month_value | last_full_month_value |
|---|---|---|---|---|---|
| left channels | streams | F6: Person-centred | 0.70 | 0.58 | 0.96 |
| left channels | streams | F11: Long, upbeat, abstract | -0.87 | 0.14 | -0.09 |
| left channels | streams | curiosity_gap | 0.67 | 0.01 | 0.03 |
| left channels | videos | outrage | -0.78 | 0.70 | 0.65 |
| neutral channels | streams | F5: Question and explainer framing | 0.83 | -0.41 | -0.18 |
| neutral channels | streams | F6: Person-centred | 0.85 | 0.11 | 0.30 |
| neutral channels | streams | F8: Numeric and dated | 0.72 | -0.17 | 0.04 |
| neutral channels | streams | F10: Quoted speech | 0.87 | -0.76 | -0.50 |
| right channels | videos | F5: Question and explainer framing | -0.95 | 0.36 | 0.17 |


Read the stream rows with the group sizes in mind: the neutral group has 16 ranked stream channels, and fewer than that in any one month, so a "group trend" there can be one channel changing how it titles its streams. Per-creator trends for the thirty largest creators are in `drift_trends.csv` (level = creator) and every creator's monthly series is on its card as sparkline data (`drift_creator_monthly.csv`).

## Month-to-month topic change

Jensen-Shannon distance between a creator's topic mix in consecutive months (months with at least 15 titles), averaged per channel group over the year:

| group | mean month-to-month JS distance |
|---|---|
| left channels | 0.63 |
| neutral channels | 0.56 |
| right channels | 0.68 |


The ordering is the inverse of news dependence: the neutral group, which holds the wires and legacy TV, moves least because the news moves them all the same way. The monthly matrix is in `topic_change_group_monthly.csv`.

## Caveats

- Nine points per series is a short run; a trend that begins in March can look strong. The strong-trend table should be read as "worth a look", not as a finding on its own.
- September is a half month and appears in the tables for completeness; no volume comparison uses it.
- Channel groups are the left / neutral / right groups of document 14: each channel's score = (right − left) / titles over its sampled titles as labeled by the judge, sorted at ±0.05. A channel's group says how its *titles* read, not what its host believes.

Files: `drift_group_monthly.csv`, `drift_creator_monthly.csv`, `drift_top30_monthly.csv`, `drift_trends.csv`, `topic_change_monthly.csv`, `topic_change_group_monthly.csv`.
