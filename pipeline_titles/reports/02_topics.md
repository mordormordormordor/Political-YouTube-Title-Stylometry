# 2. Topics: what they talk about

**The question.** What stories fill the titles, who covers what, and how much of the corpus is politics at all? The topic assignment is also the control variable for every style result, so it has to be sound.

## The finding in one paragraph

A BERTopic model fitted on a 100,078-title creator-stratified sample found 224 topics; every title was then assigned to its nearest topic centroid (86% agreement with HDBSCAN's own labels on cluster members, 13% weak assignments). One story dominates 2026: the Iran war and the Strait of Hormuz, 6,056 unique titles across 213 of 274 creators, with a second energy-markets topic on the same war. 10 of the twelve largest topics are each shared by 100 or more of the 274 creators. That is the central fact for everything after this document: the whole landscape covered the same stories, so raw vocabulary similarity between two channels mostly measures the news cycle, not their style. It also shows in the clustering: creators grouped by topic mix do not line up with the left / neutral / right channel groups (adjusted Rand index 0.004 for edited uploads).

## The largest topics (creator-balanced share)

![The fifteen largest topics by creator-balanced share; blue = political, yellow = non-political.](figures/02_top_topics.png)
*The fifteen largest topics by creator-balanced share; blue = political, yellow = non-political.*

| topic_id | label | political | balanced_share | n_unique_all | n_creators | top_terms |
|---|---|---|---|---|---|---|
| 3 | Trump and Iran War Negotiations | yes | 0.033 | 13816 | 190 | ceasefire, iran ceasefire, iran trump, trumps iran, deal iran, ceasefire iran, trump says, iran deal, usiran, says iran |
| 0 | ICE protests in Minneapolis | yes | 0.025 | 6056 | 213 | minneapolis, ice shooting, walz, ice agents, ice, antiice, tim walz, agents, alex pretti, ice agent |
| 2 | Israel and Palestine Conflict | yes | 0.024 | 5344 | 192 | gaza, palestine, palestinian, israels, israeli, netanyahu, jewish, israelis, jews, israel |
| 7 | Iran political unrest | yes | 0.021 | 6912 | 206 | khamenei, supreme leader, iranians, crown prince, irans, regime, iran iran, funeral, iranian, crown |
| 74 | Iran and Political Updates | yes | 0.019 | 1384 | 124 | joins, fail, brittany, reveal, sus, bye, ac, joins iran, jamm, iran hits |
| 1 | Shocking Events and Reactions | yes | 0.017 | 3828 | 170 | holy, holy sht, fing, theyre, sht, fking, fck, happening, genuinely, anymore |
| 60 | Trump delivering remarks | yes | 0.014 | 1703 | 59 | trump delivers, delivers remarks, trump speaks, remarks, delivers, speaks press, small business, replay president, pr... |
| 4 | Ukraine-Russia War and Political Figures | yes | 0.014 | 8146 | 128 | ukraine, russia, putins, putin, russian, zelensky, ukraine war, moscow, russias, lavrov |
| 15 | Christian Nationalism and Politics | yes | 0.014 | 1606 | 172 | pastor, christian, jesus, nationalism, prayer, god, faith, christianity, christ, christians |
| 20 | Feminism and Gender Roles Debate | yes | 0.013 | 1323 | 165 | feminism, dating, women, modern women, men, modern, marriage, divorce, men women, feminists |
| 5 | Trump and China Relations | yes | 0.012 | 4318 | 162 | xi, chinas, china, xi jinping, jinping, jiang, taiwan, beijing, chinese, professor jiang |
| 9 | Indian Politics and Delhi Riots | yes | 0.011 | 10330 | 90 | modi, pm modi, delhi, india, pm, nous, nous clips, singh, assembly, indias |


`balanced_share` is the mean over the six channel group x genre cells of the mean creator share, so a topic that four Indian channels post 8,000 times does not outrank one that 200 channels each post a few times (a topic that is large in the thin stream cells can rank above its upload count, as topic 59 does). The "Shocking Events and Reactions" topic is not a story: it is the cluster of content-free exclamations ("HOLY SH*T", "THIS IS INSANE..") that streamers and commentators use as titles, and it is the seed of the shared-title finding in document 5.

## Political or not

![Political share of a creator's titles, by channel group.](figures/02_political_share_by_group.png)
*Political share of a creator's titles, by channel group (dots = creators, bar = median).*

202 of 224 topics were tagged political by the labeling model (politics, government, elections, war, courts, political figures, the culture war); the 22 non-political topics are crime trials (Nancy Guthrie, Lindsay Clancy, the Brown University shooting), weather and disasters, sport (World Cup, MMA), tech and business, and a few channel-specific series. The tagging is generous, and the political share of a creator's unique titles is therefore high everywhere. The neutral channels, whose titles the judge mostly read as "neither", are also the ones with the most non-political subjects (crime, weather, sport, tech: the news outlets); the left and right groups are political almost throughout:

| group | mean political share | median political share | n_creators |
|---|---|---|---|
| left channels | 0.96 | 0.98 | 105 |
| neutral channels | 0.88 | 0.91 | 37 |
| right channels | 0.93 | 0.96 | 94 |


Document 5 repeats the whole landscape analysis on political titles only; the conclusions do not change.

## Topic share by channel group (top 4 per group, edited uploads)

| group | label | mean_creator_share | n_creators |
|---|---|---|---|
| left channels | Israel and Palestine Conflict | 0.045 | 105 |
| left channels | Trump and Iran War Negotiations | 0.036 | 105 |
| left channels | ICE protests in Minneapolis | 0.027 | 105 |
| left channels | Iran political unrest | 0.026 | 105 |
| neutral channels | Tech Business Founders and Industry | 0.040 | 37 |
| neutral channels | AI and Political Implications | 0.035 | 37 |
| neutral channels | Trump and Iran War Negotiations | 0.035 | 37 |
| neutral channels | Trump and China Relations | 0.033 | 37 |
| right channels | Shocking Events and Reactions | 0.044 | 94 |
| right channels | Feminism and Gender Roles Debate | 0.029 | 94 |
| right channels | Christian Nationalism and Politics | 0.024 | 94 |
| right channels | American History and Political Threats | 0.022 | 94 |


The war story leads in the ; the left channels put "Israel and Palestine Conflict" first and neutral channels put "Tech Business Founders and Industry" first and right channels put "Shocking Events and Reactions" first, with the war second. Beyond it the groups' attention differs at the margin rather than in kind: what separates them in document 14 is the wording about the shared subjects, not the subjects.

## The month-by-month story

![Monthly creator-balanced share of the eight largest topics; the hollow marker is the half month of September.](figures/02_topic_timeline.png)
*Monthly creator-balanced share of the eight largest topics; the hollow marker is the half month of September.*

For each month the topics that rose most against their own nine-month mean (creator-balanced), with the entities named in that month's titles:

| month | label | z_vs_own_months | share_month | top_entities |
|---|---|---|---|---|
| 2026-01 | Trump and Greenland politics | 2.660 | 0.031 | Greenland (877); Trump (428); US (234); NATO (165); Denmark (108) |
| 2026-01 | Trump at Davos and World Economic Forum | 2.660 | 0.007 | Davos (151); Trump (78); World Economic Forum (29); WEF (21); US (17) |
| 2026-02 | Prince Andrew Epstein Arrest Revelations | 2.660 | 0.008 | Andrew (89); Prince Andrew (80); UK (51); Andrew Mountbatten-Windsor (34); Epstein (25) |
| 2026-02 | Super Bowl Halftime Show Controversy | 2.660 | 0.013 | Bad Bunny (43); NFL (33); Patriots (15); Seahawks (10); Kid Rock (8) |
| 2026-03 | No Kings Protests Movement | 2.650 | 0.007 | Trump (24); US (13); Kings (12); Donald Trump (7); Bruce Springsteen (5) |
| 2026-03 | Joe Kent Resignation and Leaks | 2.650 | 0.010 | Joe Kent (88); Iran (28); Trump (17); FBI (10); Israel (10) |
| 2026-04 | King Charles III and Trump State Visit | 2.640 | 0.007 | US (91); Trump (76); Charles III (65); Congress (61); UK (56) |
| 2026-04 | Trump and Pope Leo Feud | 2.630 | 0.013 | Trump (139); Pope Leo (104); Leo XIV (53); Iran (48); Jesus (38) |
| 2026-05 | Thomas Massie and Trump political conflict | 2.640 | 0.011 | Thomas Massie (79); Trump (37); Massie (34); Kentucky (32); Ed Gallrein (13) |
| 2026-05 | Trump and China Relations | 2.600 | 0.029 | China (802); Trump (282); Beijing (169); US (166); Taiwan (162) |
| 2026-06 | NBA Championship Celebrations | 2.640 | 0.009 | Knicks (88); NBA (84); Trump (26); New York Knicks (24); New York (19) |
| 2026-06 | Karmelo Anthony Trial Verdict | 2.540 | 0.024 | Karmelo Anthony (137); Luigi Mangione (27); Austin Metcalf (13); Karmelo (13); Gilgo Beach (12) |
| 2026-07 | Lindsey Graham's Death and Legacy | 2.640 | 0.019 | Lindsey Graham (476); Graham (61); Senate (57); Trump (53); US (30) |
| 2026-07 | Mitch McConnell Health Mystery | 2.600 | 0.010 | Mitch McConnell (133); McConnell (50); Kentucky (15); Senate (8); GOP (6) |
| 2026-08 | Trump aide Natalie Harp and Jon Ossoff | 2.640 | 0.008 | Natalie Harp (89); Trump (44); Jon Ossoff (18); Ossoff (10); White House (6) |
| 2026-08 | WNBA and Sophie Cunningham controversy | 2.620 | 0.016 | WNBA (74); NBA (15); Sophie Cunningham (9); Royce White (4); National Report (4) |
| 2026-09 | 9/11 Remembrance 25 Years Later | 2.670 | 0.037 | Pentagon (37); America (23); Trump (19); New York (18); Mamdani (17) |
| 2026-09 | MAGA Mike Johnson political turmoil | 2.520 | 0.003 | Mike Johnson (8); MAGA Mike (2); House (2); Mike Johnson Warns (2); OMG (1) |


Read left to right and 2026 tells itself: the Bondi Beach attack and a Trump Christmas in January; the Don Lemon arrest and the Alex Pretti shooting in February; the State of the Union and the tariff case in March; the Joe Kent resignation, the Artemis II mission and the No Kings protests in April; the Correspondents' Dinner shooting in May; the Massie primary and the Karmelo Anthony verdict in June; the 250th anniversary in July; the Fauci testimony and the Blanche confirmation in August; 9/11 at 25 and Nepal's floods in September (a half month). The full list with three example titles each is `topic_spikes.csv`.

## Caveats

- The topic labels and the political flag come from a local 14B model reading the top terms and eight example titles; the labels are readable but a few are odd ("Hasanabi Reacts to Hasan" is a fan-channel formula, not a subject) and the political flag errs towards "political". Both live in `topic_labels.csv` and can be edited; the political-only analyses re-run from `landscape`.
- 35% of the fit sample were HDBSCAN outliers; nearest-centroid assignment gives them a topic anyway, and 13% of all titles sit below the 10th-percentile similarity of genuine members. Those weak assignments are flagged per title in `topics.csv`.
- Channel groups are the left / neutral / right groups of document 14: each channel's score = (right − left) / titles over its sampled titles as labeled by the judge, sorted at ±0.05. A channel's group says how its *titles* read, not what its host believes.

Files: `topics.csv` (title -> topic), `topic_labels.csv`, `creator_topic_mix.csv`, `topic_by_group.csv`, `topic_timeline.csv`, `topic_spikes.csv`, `creator_political_share.csv`.
