# 9. Stylistic twins across the political divide

**The question.** Which left-commentary and right-commentary creators title their videos the same way?

## The finding in one paragraph

Style ignores the divide. Measured in the twelve-dimensional, topic-controlled style space of document 3, the nearest neighbour of a left-commentary creator is on the right side of the divide about as often as on its own side: for 35% of the 107 commentary creators the closest right (or left) creator is closer than *any* creator in their own lane, and the distributions of nearest-twin distance and nearest-lane-mate distance sit almost on top of each other. The closest pairs are not the big names but the mid-sized daily outrage channels on both sides: @PTLRadioShow and @chicksonright, @FarronBalanced and @JesseKellyDC, The Majority Report and Owen Shroyer, The Young Turks and Nick Fuentes. What they share is form: emphasis capitals on one or two words, a named target, a verb of attack or collapse, no question, no label, no numbers.

![The twenty closest pairs and the distance comparison.](figures/09_twins.png)
*Left: the twenty closest left-right pairs. Right: for every commentary creator, the distance to its nearest creator across the divide against the distance to its nearest lane-mate.*

## The twenty closest pairs

`distance` is Euclidean distance between z-scored topic-controlled factor scores (edited uploads); `distance_percentile_all_pairs` places the pair among all 239 ranked creators' pairwise distances (0 = the closest pair in the whole landscape).

| left_creator | right_creator | distance | distance_percentile_all_pairs |
|---|---|---|---|
| @PTLRadioShow | @chicksonright | 0.92 | 0.00 |
| @Forthepeoplepodcast305 | @chicksonright | 0.94 | 0.01 |
| @FarronBalanced | @JesseKellyDC | 0.99 | 0.01 |
| @RebelHQ | @chicksonright | 1.09 | 0.03 |
| @TheDonLemonShow | @OwenReport | 1.09 | 0.03 |
| @thomhartmann | @theisabelbrown | 1.10 | 0.04 |
| @thejimmydoreshow | @fightbackpodcast | 1.20 | 0.08 |
| @TheMajorityReport | @OwenReport | 1.21 | 0.09 |
| @FarronBalanced | @chicksonright | 1.29 | 0.16 |
| @JackCocchiarellaShow | @chicksonright | 1.34 | 0.19 |
| @Forthepeoplepodcast305 | @AnthonyBrianLogan | 1.34 | 0.20 |
| @thejimmydoreshow | @MyronGainesX | 1.34 | 0.20 |
| @FarronBalanced | @OwenReport | 1.36 | 0.22 |
| @Forthepeoplepodcast305 | @GrahamAllen | 1.41 | 0.27 |
| @TheYoungTurks | https://rumble.com/c/nickjfuentes | 1.42 | 0.29 |
| @TheMajorityReport | @JesseKellyDC | 1.45 | 0.36 |
| @TheDonLemonShow | @clayandbuck | 1.46 | 0.37 |
| @MrTariqNasheed | @theisabelbrown | 1.53 | 0.47 |
| @Forthepeoplepodcast305 | @MyronGainesX | 1.57 | 0.57 |
| @MrTariqNasheed | @RileyGaines | 1.60 | 0.66 |


A few right-side channels recur as everybody's twin (@chicksonright x6, @XAVIAER x5, @MyronGainesX x4): they sit near the centre of the commentary cloud, so they are close to many left creators at once. Hubness like this is a property of the space, not evidence of imitation.

## Every creator's twin across the divide

The full table is `style_twins_nearest.csv`; the twelve left and twelve right creators with the closest twins:

| creator | twin_across_divide | twin_distance | twin_rank_among_all_neighbours | nearest_same_lane | nearest_same_lane_distance | twin_closer_than_any_same_lane |
|---|---|---|---|---|---|---|
| @PTLRadioShow | @chicksonright | 0.92 | 1 | @Forthepeoplepodcast305 | 1.28 | yes |
| @Forthepeoplepodcast305 | @chicksonright | 0.94 | 1 | @podsaveamerica | 1.28 | yes |
| @FarronBalanced | @JesseKellyDC | 0.99 | 2 | @JackCocchiarellaShow | 1.17 | yes |
| @RebelHQ | @chicksonright | 1.09 | 1 | @FarronBalanced | 1.37 | yes |
| @TheDonLemonShow | @OwenReport | 1.09 | 1 | @TheJoyReidShow | 1.42 | yes |
| @thomhartmann | @theisabelbrown | 1.10 | 1 | @MrTariqNasheed | 1.28 | yes |
| @thejimmydoreshow | @fightbackpodcast | 1.20 | 1 | @podsaveamerica | 1.59 | yes |
| @TheMajorityReport | @OwenReport | 1.21 | 3 | @FarronBalanced | 1.34 | yes |
| @JackCocchiarellaShow | @chicksonright | 1.34 | 3 | @FarronBalanced | 1.17 | no |
| @TheYoungTurks | https://rumble.com/c/nickjfuentes | 1.42 | 1 | @Forthepeoplepodcast305 | 2.10 | yes |
| @MrTariqNasheed | @theisabelbrown | 1.53 | 2 | @thomhartmann | 1.28 | no |
| @TheHumanistReport | @ChadPrather1 | 1.60 | 1 | @therationalnational | 2.18 | yes |


| creator | twin_across_divide | twin_distance | twin_rank_among_all_neighbours | nearest_same_lane | nearest_same_lane_distance | twin_closer_than_any_same_lane |
|---|---|---|---|---|---|---|
| @chicksonright | @PTLRadioShow | 0.92 | 1 | @GrahamAllen | 1.38 | yes |
| @JesseKellyDC | @FarronBalanced | 0.99 | 1 | @OwenReport | 1.10 | yes |
| @OwenReport | @TheDonLemonShow | 1.09 | 1 | @JesseKellyDC | 1.10 | yes |
| @theisabelbrown | @thomhartmann | 1.10 | 1 | @AndrewKlavan | 1.27 | yes |
| @fightbackpodcast | @thejimmydoreshow | 1.20 | 1 | @MyronGainesX | 1.68 | yes |
| @AnthonyBrianLogan | @Forthepeoplepodcast305 | 1.34 | 1 | @chicksonright | 1.81 | yes |
| @MyronGainesX | @thejimmydoreshow | 1.34 | 1 | @chicksonright | 1.53 | yes |
| @GrahamAllen | @Forthepeoplepodcast305 | 1.41 | 3 | @chicksonright | 1.38 | no |
| https://rumble.com/c/nickjfuentes | @TheYoungTurks | 1.42 | 1 | @AnthonyBrianLogan | 2.26 | yes |
| @clayandbuck | @TheDonLemonShow | 1.46 | 1 | @TomiLahrenIsFearless | 1.68 | yes |
| @RileyGaines | @MrTariqNasheed | 1.60 | 3 | @RealDanBongino | 1.60 | yes |
| @ChadPrather1 | @TheHumanistReport | 1.60 | 2 | @FreshFitMiami | 1.68 | yes |


`twin_rank_among_all_neighbours` = 1 means the twin is the creator's single nearest neighbour in the whole landscape (any lane).

## Method

1. Style vectors: the twelve factor scores of document 3, topic-controlled (each title's score minus its topic's mean, averaged per creator), edited uploads only, creators with at least 50 unique titles, clip channels excluded (40 left-commentary and 67 right-commentary creators).
2. Each factor z-scored across the ranked creators so that no factor dominates; distance = Euclidean over the twelve.
3. For every creator on one side, the nearest creator on the other side is its twin; the same distance is computed to the nearest creator on its own side; the pair distance is also expressed as a percentile of all ranked pairwise distances.
4. "Left" and "right" are the `left_commentary` and `right_commentary` lanes of the proposal in `lanes.csv`.

## Limitations

- The divide is the lane proposal, so a mislabelled creator becomes a spurious twin; centrist, legal, streamer and podcast lanes are not in the comparison at all.
- The space weights all twelve factors equally after z-scoring; two creators can be twins on capitals, questions and quotes while differing in tone, or the reverse. `dimensions.csv` has the per-factor scores if a narrower definition is wanted.
- Topic control removes the average effect of a topic on each score, not everything a subject does to a title.
- Distances shrink for creators near the centre of the cloud (hubness above) and grow for eccentric ones; the percentile column is the fairer comparison.
- Only edited uploads; live VODs are too thin for both lanes.

Files: `style_twins.csv`, `style_twins_nearest.csv`, `dimensions.csv`, `neighbours_style.csv`.
