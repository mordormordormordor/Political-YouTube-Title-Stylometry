# 2. Topics: what they talk about

**The question.** What stories fill the titles, who covers what, and how much of the corpus is politics at all? The topic assignment is also the control variable for every style result, so it has to be sound.

## The finding in one paragraph

A BERTopic model fitted on a 100,041-title creator-stratified sample found 236 topics; every title was then assigned to its nearest topic centroid (85% agreement with HDBSCAN's own labels on cluster members, 13% weak assignments). One story dominates 2026: the Iran war and the Strait of Hormuz, 27,609 unique titles across 227 of 274 creators, with a second energy-markets topic on the same war. The twelve largest topics are each shared by 130 or more creators. That is the central fact for everything after this document: the whole landscape covered the same stories, so raw vocabulary similarity between two channels mostly measures the news cycle, not their style. It also shows in the clustering: creators grouped by topic mix do not line up with lanes at all (adjusted Rand index 0.004 for edited uploads).

## The largest topics (creator-balanced share)

| topic_id | label | political | balanced_share | n_unique_all | n_creators | top_terms |
|---|---|---|---|---|---|---|
| 0 | Iran War and Strait of Hormuz Tensions | yes | 0.062 | 27609 | 227 | strait hormuz, strait, hormuz, irans, iranian, iran iran, tehran, war iran, bases, iran strikes |
| 2 | Israel-Palestine Conflict Media | yes | 0.032 | 6035 | 195 | gaza, palestine, palestinian, israeli, netanyahu, israels, west bank, jews, palestinians, jewish |
| 3 | ICE Protests and Shootings | yes | 0.021 | 5189 | 210 | ice shooting, ice, ice agent, antiice, ice agents, minneapolis ice, minneapolis, agents, agent, protesters |
| 59 | Iran Conflict and Political Updates | yes | 0.020 | 1358 | 124 | joins, renner, ac, fail, reveal, iran hits, sus, durk, jamm, larry johnson |
| 5 | Trump Supreme Court Legal Issues | yes | 0.017 | 3769 | 166 | supreme court, supreme, trump doj, court, scotus, doj, judges, ruling, judge, legal af |
| 40 | Trump's speeches and events | yes | 0.016 | 1944 | 84 | trump delivers, delivers remarks, trump speaks, davos, remarks, world economic, economic forum, delivers, las vegas, ... |
| 4 | Ukraine-Russia War and Political Figures | yes | 0.016 | 9808 | 134 | ukraine, russia, putin, putins, zelensky, russian, ukraine war, zelenskyy, russias, moscow |
| 191 | Political Commentary and Interviews | yes | 0.014 | 548 | 124 | dean, schmidt, steve schmidt, michael malice, malice, kump, ray kump, steve, ft ray, welcome |
| 42 | War and Military Analysis | yes | 0.014 | 2269 | 193 | hoh, matt hoh, col, macgregor, douglas macgregor, col douglas, douglas, world war, col lawrence, lawrence wilkerson |
| 1 | Shocking Events and Reactions | yes | 0.012 | 3996 | 171 | fing, holy, happening, theyre, holy sht, fck, im, fking, genuinely, fcked |
| 7 | Trump vs Maduro Venezuela Conflict | yes | 0.012 | 3556 | 179 | maduro, venezuela, venezuelas, venezuelan, capture, trumps venezuela, nicolas, venezuela oil, captured, venezuelan oil |
| 6 | Trump and China political relations | yes | 0.011 | 4790 | 165 | xi, china, chinas, taiwan, jiang, jinping, xi jinping, chinese, beijing, professor jiang |


`balanced_share` is the mean over lanes of the mean creator share, so a topic that four Indian channels post 8,000 times does not outrank one that 200 channels each post a few times. The "Shocking Events and Reactions" topic is not a story: it is the cluster of content-free exclamations ("HOLY SH*T", "THIS IS INSANE..") that streamers and commentators use as titles, and it is the seed of the shared-title finding in document 5.

## Political or not

212 of 236 topics were tagged political by the labelling model (politics, government, elections, war, courts, political figures, the culture war); the 24 non-political topics are crime trials (Nancy Guthrie, Lindsay Clancy, the Brown University shooting), weather and disasters, sport (World Cup, MMA), tech and business, and a few channel-specific series. The tagging is generous, and the political share of a creator's unique titles is therefore high everywhere; it separates the lanes only at the bottom:

| lane | mean political share |
|---|---|
| US legacy TV | 0.83 |
| US press | 0.85 |
| streamers | 0.86 |
| wires & international | 0.89 |
| right commentary | 0.93 |
| legal commentary | 0.93 |
| interview podcasts | 0.94 |
| humour / satire | 0.94 |
| right TV networks | 0.95 |
| centrist / heterodox | 0.96 |
| independent digital news | 0.96 |
| explainers / geopolitics | 0.97 |
| left commentary | 0.97 |


Document 5 repeats the whole landscape analysis on political titles only; the conclusions do not change.

## Topic share by lane (top 3 per lane, edited uploads)

| lane | label | mean_creator_share | n_creators |
|---|---|---|---|
| explainers / geopolitics | Israel-Palestine Conflict Media | 0.211 | 3 |
| explainers / geopolitics | India's Muslims and Political Parties | 0.171 | 3 |
| legal commentary | Trump Supreme Court Legal Issues | 0.165 | 8 |
| wires & international | Iran War and Strait of Hormuz Tensions | 0.139 | 11 |
| independent digital news | Israel-Palestine Conflict Media | 0.096 | 19 |
| US legacy TV | Iran War and Strait of Hormuz Tensions | 0.095 | 9 |
| independent digital news | Iran War and Strait of Hormuz Tensions | 0.091 | 19 |
| explainers / geopolitics | Iran War and Strait of Hormuz Tensions | 0.078 | 3 |
| US press | Tech Business and Startups | 0.077 | 18 |
| wires & international | Ukraine-Russia War and Political Figures | 0.077 | 11 |
| streamers | Shocking Events and Reactions | 0.075 | 23 |
| streamers | Hasanabi Reacts to Hasan | 0.066 | 23 |
| centrist / heterodox | Iran War and Strait of Hormuz Tensions | 0.063 | 10 |
| wires & international | Israel-Palestine Conflict Media | 0.062 | 11 |
| US press | AI and Political Concerns | 0.061 | 18 |
| interview podcasts | Political Media Figures | 0.060 | 19 |
| left commentary | Iran War and Strait of Hormuz Tensions | 0.060 | 40 |
| streamers | Destiny and Ethan Klein debates | 0.059 | 23 |
| left commentary | Trump Meltdowns and Collapses | 0.055 | 40 |
| right TV networks | Iran War and Strait of Hormuz Tensions | 0.055 | 4 |
| interview podcasts | Israel-Palestine Conflict Media | 0.054 | 19 |
| independent digital news | Trump and China political relations | 0.050 | 19 |
| centrist / heterodox | Shocking Events and Reactions | 0.050 | 10 |
| interview podcasts | Iran War and Strait of Hormuz Tensions | 0.048 | 19 |
| right commentary | Shocking Events and Reactions | 0.046 | 69 |
| US press | Iran War and Strait of Hormuz Tensions | 0.045 | 18 |
| humour / satire | Political Commentary and Interviews | 0.041 | 6 |
| right commentary | Iran War and Strait of Hormuz Tensions | 0.041 | 69 |
| humour / satire | Hollywood and Oscars Politics | 0.036 | 6 |
| legal commentary | ICE Protests and Shootings | 0.035 | 8 |
| centrist / heterodox | Trump's Unwise Actions and Mistakes | 0.035 | 10 |
| legal commentary | California Election Fraud Scandal | 0.034 | 8 |
| right commentary | Modern Women and Feminism Debate | 0.032 | 69 |
| left commentary | Trump Resignation and Leaks | 0.032 | 40 |
| humour / satire | ICE Protests and Shootings | 0.031 | 6 |
| right TV networks | Trump's speeches and events | 0.030 | 4 |
| US legacy TV | Nancy Guthrie Disappearance Investigation | 0.025 | 9 |
| right TV networks | Immigration and Deportation Policies | 0.022 | 4 |
| US legacy TV | ICE Protests and Shootings | 0.021 | 9 |


Read this as "where each lane's attention goes beyond the shared war story": legal commentary on the Supreme Court and DOJ topic, streamers on reactions and streamer drama, the US press on tech and AI, explainers on Israel-Palestine, right commentary on the "modern women and feminism" culture-war topic.

## The month-by-month story

For each month the topics that rose most against their own nine-month mean (creator-balanced), with the entities named in that month's titles:

| month | label | z_vs_own_months | share_month | top_entities |
|---|---|---|---|---|
| 2026-01 | Christmas and Trump | 2.660 | 0.016 | Trump (26); Bethlehem (17); US (17); Santa (15); America (15) |
| 2026-01 | Bondi Beach Terror Attack | 2.660 | 0.011 | Australia (155); Bondi Beach (150); Bondi (55); Sydney (39); REUTERS (35) |
| 2026-02 | Super Bowl Halftime Show Controversy | 2.660 | 0.011 | Bad Bunny (43); NFL (22); Kid Rock (9); Grammys (7); Patriots (6) |
| 2026-02 | Alex Pretti Shooting and Federal Agents | 2.660 | 0.011 | Alex Pretti (196); Minneapolis (60); Minnesota (16); DHS (13); Border Patrol (10) |
| 2026-03 | Prince Andrew Epstein Arrest | 2.650 | 0.007 | Prince Andrew (70); Andrew (68); UK (44); Andrew Mountbatten-Windsor (33); Epstein (15) |
| 2026-03 | Supreme Court and Trump Tariffs | 2.650 | 0.013 | Trump (201); Supreme Court (150); US (36); US Supreme Court (16); Vantage (11) |
| 2026-04 | Joe Kent Resignation and Iran War Scandal | 2.660 | 0.011 | Joe Kent (93); Iran (31); Trump (17); Israel (11); FBI (10) |
| 2026-04 | No Kings Protests Movement | 2.650 | 0.010 | Trump (21); Kings (15); US (12); Donald Trump (7); New York (4) |
| 2026-05 | White House Correspondents Dinner Shooting | 2.660 | 0.020 | White House (167); Trump (133); White House Correspondents' Dinner (68); Cole Allen (26); US (20) |
| 2026-05 | King Charles III and Trump interactions | 2.660 | 0.007 | US (96); Trump (73); Charles III (66); King Charles (63); UK (63) |
| 2026-06 | Thomas Massie political defeat | 2.630 | 0.009 | Thomas Massie (76); Trump (37); Massie (35); Kentucky (32); Ed Gallrein (13) |
| 2026-06 | Karmelo Anthony Trial Verdict | 2.590 | 0.018 | Karmelo Anthony (114); Austin Metcalf (11); Karmelo (9); Luigi Mangione (9); Karmelo Anthony Trial (8) |
| 2026-07 | America's 250th Anniversary and Founding History | 2.610 | 0.024 | America (184); US (36); Trump (22); U.S (13); New York (12) |
| 2026-07 | JD Vance and Iran negotiations | 2.510 | 0.009 | Iran (219); US (88); JD Vance (87); Switzerland (52); Vance (32) |
| 2026-08 | Fauci Senate Testimony Controversy | 2.650 | 0.016 | Fauci (200); Senate (72); Rand Paul (50); Anthony Fauci (44); Congress (24) |
| 2026-08 | Todd Blanche Attorney General Confirmation | 2.580 | 0.011 | Todd Blanche (153); Blanche (145); Trump (82); AG (59); Senate (56) |
| 2026-09 | 9/11 Remembered 25 Years Later | 2.660 | 0.024 | Pentagon (38); America (22); Trump (21); Mamdani (19); New York (19) |
| 2026-09 | Nepal Floods and Rescue Efforts | 2.650 | 0.009 | Nepal (277); China (49); Nepal Floods (40); India (31); Nepal-Tibet (27) |


Read left to right and 2026 tells itself: the Bondi Beach attack and a Trump Christmas in January; the Don Lemon arrest and the Alex Pretti shooting in February; the State of the Union and the tariff case in March; the Joe Kent resignation, the Artemis II mission and the No Kings protests in April; the Correspondents' Dinner shooting in May; the Massie primary and the Karmelo Anthony verdict in June; the 250th anniversary in July; the Fauci testimony and the Blanche confirmation in August; 9/11 at 25 and Nepal's floods in September (a half month). The full list with three example titles each is `topic_spikes.csv`.

## Caveats

- The topic labels and the political flag come from a local 14B model reading the top terms and eight example titles; the labels are readable but a few are odd ("Hasanabi Reacts to Hasan" is a fan-channel formula, not a subject) and the political flag errs towards "political". Both live in `topic_labels.csv` and can be edited; the political-only analyses re-run from `landscape`.
- 32% of the fit sample were HDBSCAN outliers; nearest-centroid assignment gives them a topic anyway, and 13% of all titles sit below the 10th-percentile similarity of genuine members. Those weak assignments are flagged per title in `topics.csv`.

Files: `topics.csv` (title -> topic), `topic_labels.csv`, `creator_topic_mix.csv`, `topic_by_lane.csv`, `topic_timeline.csv`, `topic_spikes.csv`, `creator_political_share.csv`.
