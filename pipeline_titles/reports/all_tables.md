# Title Stylometry: all tables (reference dump), 2026-01-01 to 2026-09-14

_Generated 2026-09-15T12:53:58+00:00 by `python -m pipeline_titles.report`. Every table below is read from `data/titles/analysis/`; the code is `pipeline_titles/`._

Corpus: 309,596 titles from 274 creators (300,420 unique within creator x genre; 256,897 edited uploads, 52,699 live-stream VODs; 5,783 on Rumble). Genres are never pooled; a creator x genre with fewer than 50 unique titles is low-n and never ranked.

## Headline findings

_One plain-language finding per stage, written from the tables below (2026-09-14 run). Re-check after a corpus refresh._

- **Stage 0, corpus.** The corpus is 309,596 titles from 274 creators, but four Indian news channels hold a fifth of it and 3.0 % of rows are verbatim live-loop repeats, so every corpus figure here is a mean of creator-level values or comes from the 189,240-title balanced subset. Brand stripping changed 34,394 titles; the creator-level Zipf exponent fell from 0.799 to 0.782 and the top-token share dropped most for show-branded channels (Rogan, Denims, Economist), which is the expected signature of removing the show-name head.
- **Stage 1, topics.** 236 topics; the Iran war / Strait of Hormuz story alone is 27,609 unique titles across 227 creators, and the ten largest topics are shared by 130+ creators each. Topic mix does not separate lanes (adjusted Rand index 0.004 for videos): in 2026 the whole landscape covered the same stories, which is exactly why style had to be measured within topic. 212 of 236 topics are political; the non-political mass (crime trials, weather, sport, tech) sits in the wire and legacy-TV lanes (political share 0.81-0.90 vs 0.93-0.98 for commentary).
- **Stage 2, style dimensions.** Twelve factors survive (parallel analysis suggested 16; 47 % of variance). The candidate labels do not hold up: Sensational, Critical and Analytical all collapse onto one tone factor (F1, positive tone vs outrage; creator-level r with the LLM ratings -0.71, -0.49, +0.43), Educational maps only partially onto the question/explainer factor (F5, r 0.39), and Conversational (r 0.18) and Humor (r 0.08; the LLM flagged 0.4 % of titles) do not appear. The other factors are structural: clause vs noun-phrase headlines, LIVE/BREAKING labelling, stream talk (chat, ellipsis), person-centred titles, news prose vs title case, numbers, ALL CAPS, quotes. Topic accounts for 5-18 % of title-level score variance, and creator scores barely move when controlled (raw vs controlled r 0.80-0.98): style is a channel trait, not a story trait. The LLM rater's test-retest weighted kappa is 0.74 for sensational but only 0.25 for educational, so the validation is trustworthy for tone and weak for the rest.
- **Stage 3, formats and hooks.** The outrage frame is the landscape's default hook: the LLM flagged 57 % of sampled titles, the classifier reproduces it well (hold-out AUC 0.84), and lane means run from 76 % (left commentary, legal commentary) and 63-65 % (right commentary, streamers) down to 43 % (wires), 33 % (US legacy TV) and 28 % (US press). Curiosity-gap (2 %) and humour (0.4 %) were flagged too rarely to learn (hold-out F1 0.18 and 0.00): treat both as unmeasured, not absent. Question titles are a press and explainer habit (26 % and 53 %), episode numbering a talk-show and right-TV habit.
- **Stage 4, landscape.** Lane predicts style almost not at all: style clusters vs lanes ARI 0.045 (videos, all titles) and 0.061 (political titles only); the largest style cluster holds 69 creators from 11 lanes, and every lane except US legacy TV (cohesion ratio 0.67) is about as spread out as the corpus. So the useful units are the style neighbours on each card, not the lanes. Of 1,575 titles used verbatim by two or more creators, 474 cross organisations (the rest are TYT/Damage Report-type cross-posts) and 62 % of those cross lanes: "THIS IS INSANE.." is used by 12 creators in 5 lanes, "IT HAPPENED AGAIN??" by 7, and the shared templates are outrage frames ("<ENT> exposes <ENT>", "<ENT> destroys <ENT>", "<ENT> under the bus"). Trump is named in 3-5 % of balanced titles by 199 creators; the entities that carry the most outrage framing relative to baseline are MAGA (1.6x), Pam Bondi (1.5x), Kash Patel and Candace Owens (1.3x), the least are the crime-story names (Nancy Guthrie 0.3x, Lindsay Clancy 0.3x).
- **Stage 5, time and engagement.** Drift is small and mostly lane-specific: 54 of 360 lane-month series show a monotone trend; left commentary's outrage share fell from 79 % to 74 % and its ALL-CAPS score fell over the year, while right-TV-network streams' outrage share doubled (21 % to 42 %). Within creator, the outrage frame is the only title feature that predicts views with a consistent sign (median +0.04 log views per SD; positive for 73 % of 193 video channels, significant-positive for 24 %, significant-negative for 1 %); every dimension score and length has a median effect at or below 0.03 with 50-70 % sign agreement, which is a null result. Views are concentrated (median Gini 0.51; the top 10 % of a channel's videos take 38 % of its views) but not power-law: the Clauset-Shalizi-Newman test prefers the lognormal in 193 of 193 video channels, and concentration tracks channel size (fewer subscribers, more concentration; rho -0.31) more than any style score.


## Stage 0: corpus, normalisation, balance

| genre | groups | rows | unique | balanced | low_n_groups | median_group_size | max_group_size |
|---|---|---|---|---|---|---|---|
| streams | 168 | 52699 | 44716 | 32656 | 89 | 42 | 8975 |
| videos | 274 | 256897 | 255704 | 156584 | 35 | 247 | 12279 |


Verbatim repeats within creator x genre: 9,176 rows (3.0%); they are collapsed for every style and topic computation and kept for volume, view and hit statistics. Balanced subset (<= 2,500 unique titles per creator x genre, seed 20260914): 189,240 titles; it is used for every pooled fit (topic model, templates, corpus Zipf, LLM sample).


Highest repeat shares (live-broadcast loops):

| creator | genre | n_rows | n_unique | repeat_share |
|---|---|---|---|---|
| @usefulidiots | streams | 69 | 12 | 0.826 |
| @rolandsmartin | streams | 1223 | 584 | 0.522 |
| @RealAmericasVoice | streams | 2958 | 1543 | 0.478 |
| @TimesNowWorld | streams | 5323 | 3006 | 0.435 |
| @timesofindia | streams | 3582 | 2295 | 0.359 |
| @aaronparnas1 | streams | 13 | 10 | 0.231 |
| @thewarningwithsteveschmidt | videos | 363 | 289 | 0.204 |
| @PrisonPlanetLive | videos | 56 | 46 | 0.179 |


Brand stripping: 85 creator x genre groups had at least one pattern above the 20 % rule (103 patterns; full list in `stripped_patterns.csv`). The most frequent:


| creator | genre | kind | pattern | count | share | example |
|---|---|---|---|---|---|---|
| @Firstpost | videos | suffix | n#g | 3523 | 0.348 | N18G |
| @Firstpost | streams | suffix | n#g | 1959 | 0.218 | N18G |
| @TimesNowWorld | videos | suffix | times now world | 1807 | 0.201 | Times Now World |
| @BBCNews | videos | suffix | bbc news | 1768 | 0.725 | BBC News |
| @thehill | videos | suffix | rising | 1669 | 0.393 | RISING |
| @SecularTalk | videos | suffix | the kyle kulinski show | 1065 | 0.731 | The Kyle Kulinski Show |
| @NewsmaxTV | streams | bracket | #/#/# | 291 | 0.729 | 9/11/2026 |
| @HasanReactionsfanTwo | videos | suffix | hasanabi reacts | 268 | 0.788 | Hasanabi Reacts |
| @deanwithrs | streams | suffix | debating maga | 258 | 0.970 | Debating MAGA. |
| @TheBrianKilmeadeShow | videos | suffix | brian kilmeade show | 253 | 0.719 | Brian Kilmeade Show |
| @NBCNews | streams | suffix | nbc news | 234 | 0.638 | NBC News |
| @ABCNews | streams | prefix | live: abc news live | 232 | 0.393 | LIVE: ABC News Live |
| @ABCNews | streams | suffix | abc news | 232 | 0.393 | ABC News |
| @TheJoyReidShow | videos | suffix | the joy reid show | 228 | 0.958 | The Joy Reid Show |
| @TheDonLemonShow | videos | prefix | lemon drop | 220 | 0.601 | LEMON DROP |


Zipf check (does stripping remove the show-brand head?):

| level | text | max_rank | zipf_exponent | n_tokens | n_types | top_20 |
|---|---|---|---|---|---|---|
| pooled_balanced | raw | 100 | 0.8563 | 2061945 | 55465 | the trump to in on of s iran live is and as for a with us war after at news |
| pooled_balanced | raw | 1000 | 0.7803 | 2061945 | 55465 | the trump to in on of s iran live is and as for a with us war after at news |
| pooled_balanced | raw | 5000 | 1.0204 | 2061945 | 55465 | the trump to in on of s iran live is and as for a with us war after at news |
| pooled_balanced | normalised | 100 | 0.8636 | 2002279 | 53660 | the trump to in on of s iran live is and as for a with us war after at over |
| pooled_balanced | normalised | 1000 | 0.7838 | 2002279 | 53660 | the trump to in on of s iran live is and as for a with us war after at over |
| pooled_balanced | normalised | 5000 | 1.0139 | 2002279 | 53660 | the trump to in on of s iran live is and as for a with us war after at over |
| creator_level_mean | raw | 200 | 0.7990 | 2042611 | 498266 | median 0.7991 over 318 creator x genre groups (>= 50 titles) |
| creator_level_mean | normalised | 200 | 0.7815 | 1984121 | 494374 | median 0.7829 over 318 creator x genre groups (>= 50 titles) |


Lane assignment (proposed, `lanes.csv`; correct the CSV and re-run from `factors`):

| lane | creators | clippers |
|---|---|---|
| centrist_heterodox | 12 | 0 |
| explainer_geopolitics | 7 | 0 |
| humour_satire | 8 | 0 |
| independent_digital_news | 20 | 0 |
| interview_podcast | 23 | 0 |
| left_commentary | 48 | 0 |
| legal_institutional | 9 | 0 |
| right_commentary | 75 | 2 |
| right_tv_network | 4 | 0 |
| streamer_reaction | 26 | 8 |
| us_legacy_tv | 9 | 1 |
| us_press_print_digital | 19 | 0 |
| wire_international | 14 | 0 |


Organisations with more than one channel: **Al Jazeera** (@ajplus, @aljazeeraenglish); **Blaze Media** (@BlazeTV, @glennbeck); **CBS News** (@60minutes, @CBSNews); **Crooked Media** (@lovettorleaveitpodcast, @podsaveamerica); **Daily Wire** (@AndrewKlavan, @BenShapiro, @MattWalsh, @MichaelKnowles); **Destiny** (@DestinyDGGClips, @destiny, @destinyhqclips); **Fox News** (@FoxNews, @FoxNewsChannelClips, @TheBrianKilmeadeShow); **HasanAbi** (@HasanAbi, @HasanAbiVODs3, @HasanReactionsfanTwo, @HasanabiClips); **MeidasTouch Network** (@LegalAFMTN, @MeidasTouch, @TheMichaelCohenShow, @katiephangnews); **Network18** (@Firstpost, @bushrakhanum); **New York Times** (@EzraKleinShow, @NYTOpinion, @NYTPodcasts, @nytimes); **PragerU** (@PragerU, @XAVIAER); **SNEAKO** (@LIVESNEAKO, @SNEAKO); **TYT Network** (@RebelHQ, @TheDamageReport, @TheYoungTurks); **Timcast** (@Timcast, @TimcastIRL, @TimcastNews); **Times Group** (@TimesNowWorld, @timesofindia); **Turning Point USA** (@RealAlexClark, @turningpointusa); **Vaush** (@TheVaushPit, @Vaush).


Clippers (titles written by fans or an editing team, kept as their own group): @AsmonTV, @ClipsCandaceOwens, @DailyDenims, @DestinyDGGClips, @FoxNewsChannelClips, @HasanAbiVODs3, @HasanReactionsfanTwo, @HasanabiClips, @TheVaushPit, @destinyhqclips, @laurenchenclips.


## Stage 1: topics

BERTopic on a 100,041-title creator-stratified sample (cap 561 per creator x genre): HDBSCAN found 236 topics (32.4% outliers); every title was then assigned to its nearest topic centroid (agreement with HDBSCAN's own labels on cluster members 85.5%; 13.4% of titles are weak assignments below the 10th-percentile similarity). 212 of 236 topics are political; 90.5% of unique titles (raw pooled) fall in political topics.


Political share by lane (mean of creators, >= 50 unique titles):

| lane | genre | n_creators | mean_political_share | median_political_share |
|---|---|---|---|---|
| centrist_heterodox | streams | 2 | 0.980 | 0.980 |
| centrist_heterodox | videos | 10 | 0.951 | 0.966 |
| explainer_geopolitics | videos | 3 | 0.967 | 0.962 |
| humour_satire | streams | 1 | 0.984 | 0.984 |
| humour_satire | videos | 6 | 0.934 | 0.933 |
| independent_digital_news | streams | 6 | 0.959 | 0.965 |
| independent_digital_news | videos | 19 | 0.963 | 0.975 |
| interview_podcast | streams | 2 | 0.979 | 0.979 |
| interview_podcast | videos | 19 | 0.931 | 0.940 |
| left_commentary | streams | 18 | 0.969 | 0.986 |
| left_commentary | videos | 40 | 0.973 | 0.980 |
| legal_institutional | streams | 3 | 0.888 | 0.904 |
| legal_institutional | videos | 8 | 0.950 | 0.974 |
| right_commentary | streams | 19 | 0.919 | 0.962 |
| right_commentary | videos | 69 | 0.927 | 0.949 |
| right_tv_network | streams | 4 | 0.947 | 0.947 |
| right_tv_network | videos | 4 | 0.944 | 0.942 |
| streamer_reaction | streams | 6 | 0.893 | 0.929 |
| streamer_reaction | videos | 23 | 0.847 | 0.898 |
| us_legacy_tv | streams | 7 | 0.806 | 0.838 |
| us_legacy_tv | videos | 9 | 0.846 | 0.865 |
| us_press_print_digital | streams | 4 | 0.886 | 0.883 |
| us_press_print_digital | videos | 18 | 0.837 | 0.857 |
| wire_international | streams | 7 | 0.866 | 0.884 |
| wire_international | videos | 11 | 0.902 | 0.913 |


Largest topics (mean of lane-level creator shares, i.e. creator-balanced):

| topic_id | label | political | category | mean_lane_share | n_unique_all | n_creators | top_terms | example_1 |
|---|---|---|---|---|---|---|---|---|
| 0 | Iran War and Strait of Hormuz Tensions | yes | war_conflict | 0.0616 | 27609 | 227 | strait hormuz, strait, hormuz, irans, iranian, iran iran, tehran, war iran, bases, iran strikes | IRAN WAR NEWS LIVE \| Iran’s Hidden Strength Shocks Experts — Is Trump Really Getting Nervous Now? |
| 2 | Israel-Palestine Conflict Media | yes | world_politics | 0.0317 | 6035 | 195 | gaza, palestine, palestinian, israeli, netanyahu, israels, west bank, jews, palestinians, jewish | Ian Carroll: How Israel MANIPULATES Our Media! |
| 3 | ICE Protests and Shootings | yes | us_politics | 0.0205 | 5189 | 210 | ice shooting, ice, ice agent, antiice, ice agents, minneapolis ice, minneapolis, agents, agent, protesters | Anti-ICE Protests LIVE From Washington DC: Charged Scenes After ICE Killing in Minneapolis \| US News |
| 59 | Iran Conflict and Political Updates | yes | world_politics | 0.0202 | 1358 | 124 | joins, renner, ac, fail, reveal, iran hits, sus, durk, jamm, larry johnson | IRAN NUCLEAR DEAL, DOLLY PARTON TRIBUTE, CORY BOOKER REVEAL, PENTAGON INFLUENCER, CNN HASAN SMEAR |
| 5 | Trump Supreme Court Legal Issues | yes | us_politics | 0.0167 | 3769 | 166 | supreme court, supreme, trump doj, court, scotus, doj, judges, ruling, judge, legal af | LIVE: Trump DOJ Indictment DOOMED + SCOTUS Ruling BACKFIRE?!?! \| Legal AF |
| 40 | Trump's speeches and events | yes | us_politics | 0.0164 | 1944 | 84 | trump delivers, delivers remarks, trump speaks, davos, remarks, world economic, economic forum, delivers, l... | LIVE: Trump delivers remarks at the World Economic Forum |
| 4 | Ukraine-Russia War and Political Figures | yes | war_conflict | 0.0156 | 9808 | 134 | ukraine, russia, putin, putins, zelensky, russian, ukraine war, zelenskyy, russias, moscow | Russia Ukraine War LIVE: Zelensky's Message to Putin: End the War or Face Russia's Wrath |
| 191 | Political Commentary and Interviews | yes | media_culture_war | 0.0144 | 548 | 124 | dean, schmidt, steve schmidt, michael malice, malice, kump, ray kump, steve, ft ray, welcome | Never Forget \| Steve Schmidt and Dean Blundell |
| 42 | War and Military Analysis | yes | war_conflict | 0.0137 | 2269 | 193 | hoh, matt hoh, col, macgregor, douglas macgregor, col douglas, douglas, world war, col lawrence, lawrence w... | The Truth About War |
| 1 | Shocking Events and Reactions | yes | media_culture_war | 0.0125 | 3996 | 171 | fing, holy, happening, theyre, holy sht, fck, im, fking, genuinely, fcked | WTF is happening.. |
| 7 | Trump vs Maduro Venezuela Conflict | yes | world_politics | 0.0117 | 3556 | 179 | maduro, venezuela, venezuelas, venezuelan, capture, trumps venezuela, nicolas, venezuela oil, captured, ven... | 'US Will Run Venezuela After Maduro’s Capture': Trump's Big Announcement On Caracas Action |
| 6 | Trump and China political relations | yes | world_politics | 0.0112 | 4790 | 165 | xi, china, chinas, taiwan, jiang, jinping, xi jinping, chinese, beijing, professor jiang | Trump in China: Why Xi Jinping Has the Upper Hand \| The Link \| 4K |
| 9 | AI and Political Concerns | yes | us_politics | 0.0102 | 3547 | 187 | ai, anthropic, bubble, artificial, researcher, models, humans, ai slop, sanders, bernie sanders | AI Is Coming for Your Job — and Even Tech CEOs Aren’t Safe \| NYNext |
| 16 | California Election Fraud Scandal | yes | us_politics | 0.0102 | 1667 | 156 | fulton, california, fulton county, voter, voter id, id, election fraud, steve hilton, county, californias | SCANDAL: How Election Fraud in California is Built INTO the System! |
| 8 | Epstein Files Political Connections | yes | us_politics | 0.0101 | 2002 | 196 | epstein files, epsteins, jeffrey epstein, files, epstein, files epstein, jeffrey, gates, connections, break... | The Dark Truth in the Epstein Files the Media WON'T TOUCH |
| 11 | Hollywood and Oscars Politics | yes | media_culture_war | 0.0099 | 1837 | 172 | odyssey, hollywood, oscars, movie, film, actors, christopher, sunday 60, grammys, red carpet | 'Idiots': Unpacking Oscars' most 'cringe, woke' nonsense \| Rob Schmitt Tonight |
| 12 | Canada-US Political Tensions | yes | us_politics | 0.0098 | 1899 | 127 | canada, carney, ezra levant, levant, canadian, canadas, ezra, poilievre, buffalo, carneys | ‘CAN’T SAVE CANADA...’: Mark Carney Faces New REVOLT Amid Trump Tariff War; ‘Only Half The Battle...’ |
| 17 | 2026 Midterm Election Predictions | yes | us_politics | 0.0094 | 3465 | 182 | midterm, midterms, midterms democrats, democratic party, republicans, democrats, win midterms, party, 2026 ... | 🚨Stunning New Polls Show Republican SURGE in Midterms \| Dems DOOM in Crisis After Voter Reversal... |
| 22 | Christian Nationalism and Politics | yes | us_politics | 0.0092 | 1518 | 171 | jesus, christian, god, nationalism, christ, christianity, faith, bible, pastor, gospel | HOT TOPICS \| Pastor EXPOSES the Truth About Donald Trump, MAGA & Christian Nationalism! |
| 98 | JLP Weekly Series | no | media_culture_war | 0.0091 | 1243 | 182 | jlp wed, jlp, wed, jlp thu, thu, jlp mon, mon, jlp tue, tue, jlp fri | Through Hell to Clarity \| JLP Fri 4-17-26 |
| 18 | Lindsay Clancy Murder Trial | no | crime_justice | 0.0089 | 2241 | 132 | clancy, lindsay clancy, lindsay, trial, jury, trial day, murder trial, closing arguments, murder, arguments | VERDICT WATCH: Lindsay Clancy Trial |
| 24 | Trump Meltdowns and Collapses | yes | us_politics | 0.0087 | 4108 | 136 | trump spirals, trump loses, speech trump, spirals, meltdown trump, trump meltdown, presser, trump melts, tr... | Trump STUNNED as IT ALL COLLAPSES |
| 156 | Kamala Harris 2028 Election Speculation | yes | us_politics | 0.0086 | 997 | 154 | kamala, kamala harris, harris, francesca, hong, candidate corner, kamalas, abughazaleh, kat abughazaleh, co... | Kamala Harris Is Back? Unpacking Her Big Announcement |
| 158 | India's Muslims and Political Parties | yes | world_politics | 0.0078 | 1610 | 57 | nous, nous clips, clips, muslims, indian, india, indias, parties, palki sharma, palki | Did Political Movements Fail India's Muslims I nous Clips |
| 51 | Minneapolis political unrest and federal response | yes | us_politics | 0.0078 | 1469 | 137 | insurrection act, minneapolis, insurrection, border patrol, patrol, bovino, minneapolis trump, minnesota, f... | LIVE: Scene in Minneapolis after Trump threatens to use Insurrection Act |


Topic share by lane, top 5 per lane (videos; mean of creator shares):


| lane | topic_id | label | political | mean_creator_share | raw_pooled_share | n_creators |
|---|---|---|---|---|---|---|
| explainer_geopolitics | 2 | Israel-Palestine Conflict Media | yes | 0.211 | 0.092 | 3 |
| explainer_geopolitics | 158 | India's Muslims and Political Parties | yes | 0.171 | 0.188 | 3 |
| legal_institutional | 5 | Trump Supreme Court Legal Issues | yes | 0.165 | 0.270 | 8 |
| wire_international | 0 | Iran War and Strait of Hormuz Tensions | yes | 0.139 | 0.158 | 11 |
| independent_digital_news | 2 | Israel-Palestine Conflict Media | yes | 0.096 | 0.063 | 19 |
| us_legacy_tv | 0 | Iran War and Strait of Hormuz Tensions | yes | 0.095 | 0.099 | 9 |
| independent_digital_news | 0 | Iran War and Strait of Hormuz Tensions | yes | 0.091 | 0.074 | 19 |
| explainer_geopolitics | 0 | Iran War and Strait of Hormuz Tensions | yes | 0.078 | 0.101 | 3 |
| us_press_print_digital | 95 | Tech Business and Startups | no | 0.077 | 0.033 | 18 |
| wire_international | 4 | Ukraine-Russia War and Political Figures | yes | 0.077 | 0.100 | 11 |
| streamer_reaction | 1 | Shocking Events and Reactions | yes | 0.075 | 0.129 | 23 |
| streamer_reaction | 48 | Hasanabi Reacts to Hasan | yes | 0.066 | 0.065 | 23 |
| centrist_heterodox | 0 | Iran War and Strait of Hormuz Tensions | yes | 0.063 | 0.061 | 10 |
| wire_international | 2 | Israel-Palestine Conflict Media | yes | 0.062 | 0.032 | 11 |
| us_press_print_digital | 9 | AI and Political Concerns | yes | 0.061 | 0.038 | 18 |
| interview_podcast | 102 | Political Media Figures | yes | 0.060 | 0.049 | 19 |
| left_commentary | 0 | Iran War and Strait of Hormuz Tensions | yes | 0.060 | 0.037 | 40 |
| streamer_reaction | 54 | Destiny and Ethan Klein debates | no | 0.059 | 0.040 | 23 |
| left_commentary | 24 | Trump Meltdowns and Collapses | yes | 0.055 | 0.077 | 40 |
| right_tv_network | 0 | Iran War and Strait of Hormuz Tensions | yes | 0.055 | 0.063 | 4 |
| interview_podcast | 2 | Israel-Palestine Conflict Media | yes | 0.054 | 0.045 | 19 |
| independent_digital_news | 6 | Trump and China political relations | yes | 0.050 | 0.035 | 19 |
| centrist_heterodox | 1 | Shocking Events and Reactions | yes | 0.050 | 0.032 | 10 |
| interview_podcast | 0 | Iran War and Strait of Hormuz Tensions | yes | 0.048 | 0.055 | 19 |
| right_commentary | 1 | Shocking Events and Reactions | yes | 0.046 | 0.047 | 69 |
| explainer_geopolitics | 4 | Ukraine-Russia War and Political Figures | yes | 0.046 | 0.070 | 3 |
| us_press_print_digital | 0 | Iran War and Strait of Hormuz Tensions | yes | 0.045 | 0.089 | 18 |
| streamer_reaction | 104 | MAGA Supporters and Arguments | yes | 0.042 | 0.033 | 23 |
| humour_satire | 191 | Political Commentary and Interviews | yes | 0.041 | 0.023 | 6 |
| right_commentary | 0 | Iran War and Strait of Hormuz Tensions | yes | 0.041 | 0.047 | 69 |
| explainer_geopolitics | 42 | War and Military Analysis | yes | 0.041 | 0.047 | 3 |
| streamer_reaction | 111 | HasanAbi 2026 Schedule | no | 0.041 | 0.024 | 23 |
| humour_satire | 11 | Hollywood and Oscars Politics | yes | 0.036 | 0.029 | 6 |
| us_press_print_digital | 11 | Hollywood and Oscars Politics | yes | 0.035 | 0.006 | 18 |
| legal_institutional | 3 | ICE Protests and Shootings | yes | 0.035 | 0.026 | 8 |
| centrist_heterodox | 217 | Trump's Unwise Actions and Mistakes | yes | 0.035 | 0.032 | 10 |
| legal_institutional | 16 | California Election Fraud Scandal | yes | 0.034 | 0.032 | 8 |
| wire_international | 20 | Indian Politics and Parliament | yes | 0.034 | 0.060 | 11 |
| independent_digital_news | 3 | ICE Protests and Shootings | yes | 0.032 | 0.042 | 19 |
| right_commentary | 13 | Modern Women and Feminism Debate | yes | 0.032 | 0.023 | 69 |
| centrist_heterodox | 2 | Israel-Palestine Conflict Media | yes | 0.032 | 0.032 | 10 |
| left_commentary | 62 | Trump Resignation and Leaks | yes | 0.032 | 0.041 | 40 |
| humour_satire | 3 | ICE Protests and Shootings | yes | 0.031 | 0.033 | 6 |
| legal_institutional | 43 | Trump slush fund scandal | yes | 0.030 | 0.032 | 8 |
| right_tv_network | 40 | Trump's speeches and events | yes | 0.030 | 0.021 | 4 |
| interview_podcast | 73 | Left Wing Political Violence | yes | 0.030 | 0.021 | 19 |
| left_commentary | 2 | Israel-Palestine Conflict Media | yes | 0.029 | 0.023 | 40 |
| wire_international | 38 | Israel-Lebanon Conflict and Ceasefire Talks | yes | 0.029 | 0.030 | 11 |
| interview_podcast | 9 | AI and Political Concerns | yes | 0.029 | 0.018 | 19 |
| centrist_heterodox | 24 | Trump Meltdowns and Collapses | yes | 0.028 | 0.026 | 10 |
| legal_institutional | 17 | 2026 Midterm Election Predictions | yes | 0.028 | 0.012 | 8 |
| independent_digital_news | 7 | Trump vs Maduro Venezuela Conflict | yes | 0.028 | 0.018 | 19 |
| humour_satire | 154 | Anti-Trump Protests and Riots | yes | 0.027 | 0.018 | 6 |
| left_commentary | 1 | Shocking Events and Reactions | yes | 0.025 | 0.024 | 40 |
| us_legacy_tv | 56 | Nancy Guthrie Disappearance Investigation | no | 0.025 | 0.029 | 9 |
| humour_satire | 98 | JLP Weekly Series | no | 0.025 | 0.017 | 6 |
| us_press_print_digital | 93 | Olympics and Team USA Politics | yes | 0.025 | 0.003 | 18 |
| right_commentary | 22 | Christian Nationalism and Politics | yes | 0.023 | 0.018 | 69 |
| right_tv_network | 25 | Immigration and Deportation Policies | yes | 0.022 | 0.024 | 4 |
| right_tv_network | 194 | Medal of Honor Ceremonies | yes | 0.021 | 0.015 | 4 |
| us_legacy_tv | 3 | ICE Protests and Shootings | yes | 0.021 | 0.024 | 9 |
| right_tv_network | 3 | ICE Protests and Shootings | yes | 0.021 | 0.023 | 4 |
| right_commentary | 2 | Israel-Palestine Conflict Media | yes | 0.020 | 0.021 | 69 |
| us_legacy_tv | 18 | Lindsay Clancy Murder Trial | no | 0.017 | 0.018 | 9 |
| us_legacy_tv | 9 | AI and Political Concerns | yes | 0.016 | 0.012 | 9 |


Monthly spikes (creator-balanced share vs the topic's own nine-month mean; top 3 per month):


| month | label | z_vs_own_months | share_month | share_mean_all_months | top_entities | example_1 |
|---|---|---|---|---|---|---|
| 2026-01 | Christmas and Trump | 2.660 | 0.016 | 0.002 | Trump (26); Bethlehem (17); US (17); Santa (15); America (15) | LIVE: Trump Participates in NORAD Santa Calls \| Christmas \| Trump on Christmas Eve |
| 2026-01 | Bondi Beach Terror Attack | 2.660 | 0.011 | 0.001 | Australia (155); Bondi Beach (150); Bondi (55); Sydney (39); REUTERS (35) | Bondi Beach Attack LIVE: PM Faces Antisemitism Row \| Father, Son ISIS Plot That Shocked Australia |
| 2026-01 | Dan Bongino's Political Outbursts | 2.660 | 0.007 | 0.002 | Dan Bongino (44); FBI (28); Bongino (5); Trump (4); New England Patriots (3) | Dan Bongino gets HUMILIATION he DESERVES \| Another Day |
| 2026-02 | Super Bowl Halftime Show Controversy | 2.660 | 0.011 | 0.002 | Bad Bunny (43); NFL (22); Kid Rock (9); Grammys (7); Patriots (6) | Super Bowl Halftime Show DISGRACE! - Cultural Insurrection Bad Bunny Backlash - Full Analysis |
| 2026-02 | Alex Pretti Shooting and Federal Agents | 2.660 | 0.011 | 0.002 | Alex Pretti (196); Minneapolis (60); Minnesota (16); DHS (13); Border Patrol (10) | Alex Pretti shooting: Debate continues over what videos show \| NewsNation Prime |
| 2026-02 | Don Lemon Arrested | 2.660 | 0.016 | 0.003 | Don Lemon (261); Minnesota (24); CNN (9); Don Lemon Arrest (7); Lemon (6) | Don Lemon Arrested: The Details Nobody is Talking About |
| 2026-03 | Prince Andrew Epstein Arrest | 2.650 | 0.007 | 0.001 | Prince Andrew (70); Andrew (68); UK (44); Andrew Mountbatten-Windsor (33); Epstein (15) | Prince Andrew Arrested — Is the Epstein Reckoning Finally Here? \| Gerry Callahan Show |
| 2026-03 | Supreme Court and Trump Tariffs | 2.650 | 0.013 | 0.003 | Trump (201); Supreme Court (150); US (36); US Supreme Court (16); Vantage (11) | SPECIAL REPORT: Supreme Court invalidates most of Trump's tariffs |
| 2026-03 | Trump State of the Union Address | 2.620 | 0.021 | 0.004 | Trump (138); State of the Union (63); Union Address (19); Trump's State of the Union (18); Trump’s State of... | LIVE: Trump’s State of the Union Address |
| 2026-04 | Joe Kent Resignation and Iran War Scandal | 2.660 | 0.011 | 0.001 | Joe Kent (93); Iran (31); Trump (17); Israel (11); FBI (10) | Joe Kent in HOT WATERS as Trump Exposes Real Reason He Flipped on America & Israel! |
| 2026-04 | No Kings Protests Movement | 2.650 | 0.010 | 0.002 | Trump (21); Kings (15); US (12); Donald Trump (7); New York (4) | WATCH: The "No Kings" Protests Released New Levels Of ABSURD |
| 2026-04 | Artemis II Moon Mission Updates | 2.620 | 0.014 | 0.003 | NASA (336); Artemis (118); Artemis II (67); Moon (43); America (20) | NASA news conference on Artemis II mission to the moon \| full video |
| 2026-05 | White House Correspondents Dinner Shooting | 2.660 | 0.020 | 0.004 | White House (167); Trump (133); White House Correspondents' Dinner (68); Cole Allen (26); US (20) | What we know about the White House Correspondents Dinner shooter |
| 2026-05 | King Charles III and Trump interactions | 2.660 | 0.007 | 0.001 | US (96); Trump (73); Charles III (66); King Charles (63); UK (63) | Donald Trump And King Charles III Viral Moments Amid King Charles' US Visit \| Firstpost |
| 2026-05 | Hantavirus outbreak on cruise ship | 2.650 | 0.009 | 0.001 | US (27); Nebraska (19); Tenerife (17); U.S (14); Spain (13) | Hantavirus is 'not a brand new virus.' Official outlines how disease spreads amid cruise outbreak |
| 2026-06 | Thomas Massie political defeat | 2.630 | 0.009 | 0.002 | Thomas Massie (76); Trump (37); Massie (35); Kentucky (32); Ed Gallrein (13) | Thomas Massie Gets Trumped, Loses His Representative Seat |
| 2026-06 | Karmelo Anthony Trial Verdict | 2.590 | 0.018 | 0.004 | Karmelo Anthony (114); Austin Metcalf (11); Karmelo (9); Luigi Mangione (9); Karmelo Anthony Trial (8) | Karmelo Anthony Verdict Courthouse Reactions - Here's What REALLY Happened! \| Brianna Morello |
| 2026-06 | Spencer Pratt LA Mayoral Campaign | 2.520 | 0.015 | 0.003 | Spencer Pratt (141); LA (43); Karen Bass (16); California (13); Los Angeles (12) | Spencer Pratt Is Turning LA Politics Upside Down |
| 2026-07 | America's 250th Anniversary and Founding History | 2.610 | 0.024 | 0.009 | America (184); US (36); Trump (22); U.S (13); New York (12) | US News Live: Trump's America-First Message Echoes At Salute To America \| 250th Independence Day |
| 2026-07 | JD Vance and Iran negotiations | 2.510 | 0.009 | 0.002 | Iran (219); US (88); JD Vance (87); Switzerland (52); Vance (32) | BOMBSHELL: JD Vance Turns On Israel After Iran Deal |
| 2026-07 | Trump Reflecting Pool Scandal | 2.500 | 0.007 | 0.002 | Trump (42); Reflecting Pool (8); David Hearn (8); Lincoln Memorial Reflecting Pool (7); US (7) | Trump goes FULL FREAKOUT over Reflecting Pool UPDATE \| Another Day |
| 2026-08 | Fauci Senate Testimony Controversy | 2.650 | 0.016 | 0.003 | Fauci (200); Senate (72); Rand Paul (50); Anthony Fauci (44); Congress (24) | 'The Five': Fauci's private diary entries EXPOSED ahead of Senate testimony |
| 2026-08 | Todd Blanche Attorney General Confirmation | 2.580 | 0.011 | 0.002 | Todd Blanche (153); Blanche (145); Trump (82); AG (59); Senate (56) | LIVE: Todd Blanche testifies at confirmation hearing to be attorney general |
| 2026-08 | Ceuta Migration Crisis | 2.570 | 0.006 | 0.002 | Spain (201); Morocco (36); Ceuta (29); EU (19); SPAIN (8) | Spain Migrant Crisis LIVE \| Spain Pushes Back Morocco Migrant Surge After Deadly Ceuta Border Crisis |
| 2026-09 | 9/11 Remembered 25 Years Later | 2.660 | 0.024 | 0.004 | Pentagon (38); America (22); Trump (21); Mamdani (19); New York (19) | 25 Years Later: Remembering the Heroes of 9/11 |
| 2026-09 | Nepal Floods and Rescue Efforts | 2.650 | 0.009 | 0.002 | Nepal (277); China (49); Nepal Floods (40); India (31); Nepal-Tibet (27) | Nepal floods: The race to find survivors \| Jesse Weber Live Full Show |
| 2026-09 | Dolly Parton Tribute and Legacy | 2.650 | 0.011 | 0.002 | Dolly Parton (77); Tennessee (7); Trump (4); US (4); National Report (3) | Dolly Parton Death LIVE \| ‘There Will Never Be Anyone Like Her’: Trump Mourns Dolly Parton |


Entities most named per topic (top 15 topics): see `topic_labels.csv` columns `top_persons` / `top_orgs`.

| topic_id | label | top_persons | top_orgs |
|---|---|---|---|
| 0 | Iran War and Strait of Hormuz Tensions | Hormuz (1783); Trump (1199); Khamenei (251); Netanyahu (210); Donald Trump (187); Firstpost Live (164); Moj... | Trump (2199); Vantage on Firstpost (295); Firstpost America (176); World News (144); Pentagon (142); Suprem... |
| 2 | Israel-Palestine Conflict Media | Netanyahu (433); Trump (82); Benjamin Netanyahu (47); Inside Story (40); Max Blumenthal (33); Ro Khanna (32... | Trump (134); Hamas (124); UN (77); REUTERS (30); Congress (24); Palestine Action (21); IDF (18); EU (18) |
| 3 | ICE Protests and Shootings | Tom Homan (42); Renee Good (42); Trump (39); JD Vance (19); Katie Pavlich (16); Homan (15); Kristi Noem (14... | Trump (214); DHS (84); REUTERS (39); ICE (35); TSA (34); FBI (28); White House (25); NewsNation Live (25) |
| 59 | Iran Conflict and Political Updates | Tom Llamas (186); Top Story (185); Michael Popok (19); Trump (18); Candace Owens (15); Erika Kirk (14); Tuc... | NBC News (185); Trump (85); GOP (18); FBI (13); Bloomberg (12); Candace (11); White House (10); MAGA (10) |
| 5 | Trump Supreme Court Legal Issues | Trump (131); Trump PANICS (25); Lisa Cook (23); Trump STUNNED (22); Trump DOJ (20); Obama (18); Legal AF (1... | Supreme Court (584); Trump (431); Court (52); GOP (42); Fed (40); Justice Department (33); DOJ (27); Congre... |
| 40 | Trump's speeches and events | Trump (370); Donald Trump (167); Trump Speaks (74); Trump Delivers Remarks (39); Trump Holds (36); Trump Pa... | White House (178); Trump (130); TRUMP (23); World Economic Forum (23); Oval Office (21); House (17); Cabine... |
| 4 | Ukraine-Russia War and Political Figures | Putin (1371); Zelensky (450); PUTIN (128); Trump (114); Vladimir Putin (52); Kyiv (51); Firstpost Live (47)... | NATO (347); EU (306); World News (298); Trump (159); CIA (66); Kremlin (66); REUTERS (55); Vantage on First... |
| 191 | Political Commentary and Interviews | Steve Schmidt (37); Gillian Joseph (32); Dean Blundell (18); Michael Malice (14); Steve Schmidt & Dean Blun... | Real America’s Music (5); Serial Productions (5); Official Music Video (3); Truth Bombers (3); JLP (3); AMA... |
| 42 | War and Military Analysis | Douglas Macgregor (34); Matt Hoh (17); Lawrence Wilkerson (16); John Mearsheimer (14); John Iadarola (12); ... | Pentagon (53); COL (39); Army (25); Navy (25); Operation Epic Fury (17); LtCOL (12); Ret (12); CIA (9) |
| 1 | Shocking Events and Reactions | McEnany (27); Jesse Watters (8); Keane (8); Watters (7); Peter Doocy (6); Gen Keane (5); Ben (4); Turley (4) | INSANE (9); NEVER (7); WTF (7); BRUTAL (4); WoW (3); MTG (3); LEAKED (3); DISGUSTING (3) |
| 7 | Trump vs Maduro Venezuela Conflict | Maduro (365); Trump (166); Nicolas Maduro (69); Nicolás Maduro (48); Donald Trump (23); Maduro Captured (14... | Maduro (345); Trump (265); REUTERS (76); CIA (33); UN (28); White House (26); Congress (26); NewsNation Liv... |
| 6 | Trump and China political relations | Xi (222); Trump (167); Xi Jinping (114); Putin (87); Kim Jong Un (47); Hormuz (40); Donald Trump (39); Jian... | Trump (283); Vantage on Firstpost (71); REUTERS (47); China MoFA (43); World News (32); CCP (30); Firstpost... |
| 9 | AI and Political Concerns | Sam Altman (36); Haslinda Amin (25); Joe Allen (23); Jensen Huang (21); Bernie Sanders (20); OpenAI (20); J... | AI (195); Pentagon (49); OpenAI (36); Vantage on Firstpost (35); Google (32); REUTERS (28); Trump (27); AI ... |
| 16 | California Election Fraud Scandal | Steve Hilton (35); Trump (13); Katie Pavlich (9); Xavier Becerra (8); Voter Fraud (6); Marc Elias (6); Favo... | FBI (51); Trump (50); GOP (28); USPS (16); Supreme Court (15); State (14); NJ (9); CA (8) |
| 8 | Epstein Files Political Connections | Epstein (217); Jeffrey Epstein (100); Epstein Files (43); Bill Gates (35); Ghislaine Maxwell (22); Howard L... | Congress (15); House (14); Blanche (11); Sky News (10); CIA (9); FBI (9); Maxwell (8); OMG (8) |


## Stage 2: style dimensions

Exploratory factor analysis on 2,029 creator x genre x month cells (>= 15 unique titles) x 74 features (dropped: 7, listed in the appendix). KMO = 0.725; Bartlett chi2 = 111,975 (p = 0). Parallel analysis retains 16 factors (Kaiser: 21); retained 12 (minres, oblimin), cumulative variance 47.4%. Scree data: `scree.csv` / `scree.png`.


Retained factors, named from their loadings (|loading| >= 0.4 shown; full table in the appendix):


| factor | name | variance | positive loadings | negative loadings |
|---|---|---|---|---|
| F1 | Positive tone vs outrage (shock words, violence verbs, negative sentiment) | 5.3% | vader_compound_mean (+0.91), vader_pos_mean (+0.47) | vader_neg_mean (-0.76), shock_word_p100 (-0.74), violence_verb_p100 (-0.64), curiosity_lex_p100 (-0.40) |
| F2 | Clause headline vs noun-phrase (finite verbs, tense) | 4.8% | has_finite_verb_p100 (+0.91), present_tense_p100 (+0.74), past_tense_p100 (+0.54), verb_share_mean (+0.51),... | propn_share_mean (-0.48) |
| F3 | Labelled live/formulaic headline (LIVE:, BREAKING:, colon labels) | 4.7% | lead_colon_label_p100 (+0.85), lead_live_p100 (+0.82), colon_p100 (+0.79), formulaic_p100 (+0.48) | entity_first_p100 (-0.59) |
| F4 | Conversational stream talk (chat, ellipsis, contractions, imperatives, we) | 4.6% | discourse_marker_p100 (+0.84), trailing_ellipsis_p100 (+0.82), ellipsis_p100 (+0.71), contraction_p100 (+0.... |  |
| F5 | Question and explainer framing (why, what, ?) | 4.5% | q_word_start_p100 (+0.95), wh_any_p100 (+0.85), why_marker_p100 (+0.79), q_mark_p100 (+0.46) |  |
| F6 | Person-centred (named people) | 4.3% | n_person_p100 (+0.99), has_person_p100 (+0.94) |  |
| F7 | Descriptive news prose vs title-case (nouns, adjectives, places) | 4.2% | noun_share_mean (+0.81), adj_share_mean (+0.52), n_gpe_p100 (+0.45) | cap_token_share_mean (-0.72), negation_p100 (-0.41) |
| F8 | Numeric and dated (digits, years) | 3.7% | num_share_mean (+0.95), digit_p100 (+0.85), year_mention_p100 (+0.68) |  |
| F9 | ALL-CAPS shouting | 3.4% | allcaps_word_share_mean (+0.94), full_caps_title_p100 (+0.86), has_allcaps_word_p100 (+0.44) |  |
| F10 | Quoted speech | 3.2% | quoted_speech_p100 (+0.93), quotes_p100 (+0.91) |  |
| F11 | Long, upbeat, abstract (length, positive words, nominalisations) | 2.5% | vader_pos_mean (+0.53), n_chars_mean (+0.52), nominalisation_p100 (+0.42) |  |
| F12 | Modal and future speculation (will, could, we) | 2.3% | future_will_p100 (+0.54), modal_p100 (+0.53), first_pl_p100 (+0.42) |  |


Factor correlations (oblimin):

| factor | F1 | F2 | F3 | F4 | F5 | F6 | F7 | F8 | F9 | F10 | F11 | F12 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| F1 | 1.00 | -0.07 | -0.03 | 0.09 | 0.11 | -0.06 | -0.17 | 0.25 | -0.27 | -0.07 | 0.13 | 0.10 |
| F2 | -0.07 | 1.00 | 0.06 | 0.08 | -0.04 | -0.08 | -0.07 | -0.29 | 0.22 | 0.09 | 0.20 | -0.04 |
| F3 | -0.03 | 0.06 | 1.00 | -0.07 | 0.05 | -0.16 | -0.06 | 0.18 | 0.03 | -0.04 | 0.01 | -0.11 |
| F4 | 0.09 | 0.08 | -0.07 | 1.00 | 0.04 | -0.01 | 0.07 | -0.01 | 0.15 | 0.23 | -0.16 | 0.21 |
| F5 | 0.11 | -0.04 | 0.05 | 0.04 | 1.00 | 0.01 | -0.05 | 0.02 | -0.18 | -0.07 | 0.06 | 0.05 |
| F6 | -0.06 | -0.08 | -0.16 | -0.01 | 0.01 | 1.00 | 0.07 | -0.15 | 0.11 | 0.12 | 0.07 | 0.01 |
| F7 | -0.17 | -0.07 | -0.06 | 0.07 | -0.05 | 0.07 | 1.00 | -0.09 | 0.12 | 0.08 | -0.09 | 0.08 |
| F8 | 0.25 | -0.29 | 0.18 | -0.01 | 0.02 | -0.15 | -0.09 | 1.00 | -0.21 | -0.06 | -0.18 | 0.12 |
| F9 | -0.27 | 0.22 | 0.03 | 0.15 | -0.18 | 0.11 | 0.12 | -0.21 | 1.00 | 0.26 | -0.22 | 0.10 |
| F10 | -0.07 | 0.09 | -0.04 | 0.23 | -0.07 | 0.12 | 0.08 | -0.06 | 0.26 | 1.00 | -0.08 | 0.09 |
| F11 | 0.13 | 0.20 | 0.01 | -0.16 | 0.06 | 0.07 | -0.09 | -0.18 | -0.22 | -0.08 | 1.00 | -0.17 |
| F12 | 0.10 | -0.04 | -0.11 | 0.21 | 0.05 | 0.01 | 0.08 | 0.12 | 0.10 | 0.09 | -0.17 | 1.00 |


Do the factors map onto the candidate labels? (creator-level Spearman r between the LLM rating aggregated to creator x genre and the raw factor score; present >= 0.5, partial 0.3-0.5, absent < 0.3; 'merged' = two candidates land on the same factor):


| candidate | best_factor | factor_auto_name | creator_level_r | second_factor | second_r | verdict |
|---|---|---|---|---|---|---|
| Sensational | F1 | +vader_compound -vader_neg -shock_word -violence_verb | -0.711 | F5 | -0.329 | merged: Sensational, Critical, Analytical/Informational |
| Critical | F1 | +vader_compound -vader_neg -shock_word -violence_verb | -0.489 | F5 | -0.182 | merged: Sensational, Critical, Analytical/Informational |
| Analytical/Informational | F1 | +vader_compound -vader_neg -shock_word -violence_verb | 0.433 | F5 | 0.425 | merged: Sensational, Critical, Analytical/Informational |
| Educational | F5 | +q_word_start +wh_any +why_marker +q_mark | 0.392 | F1 | 0.320 | partial |
| Conversational | F4 | +discourse_marker +trailing_ellipsis +ellipsis +contraction | 0.177 | F1 | 0.170 | absent |
| Humor | F2 | +has_finite_verb +present_tense +past_tense +verb_share | 0.082 | F4 | 0.063 | absent |


LLM rating vs factor score, creator level (Spearman, n = 318 creator x genre groups with >= 5 rated titles):

| llm | F1 | F10 | F11 | F12 | F2 | F3 | F4 | F5 | F6 | F7 | F8 | F9 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| analytical | 0.43 | 0.23 | 0.11 | 0.38 | -0.00 | 0.21 | -0.13 | 0.42 | 0.01 | 0.01 | 0.18 | -0.26 |
| conversational | 0.17 | -0.02 | -0.02 | -0.05 | 0.07 | -0.09 | 0.18 | 0.12 | -0.14 | 0.00 | -0.08 | 0.01 |
| critical | -0.49 | 0.05 | 0.06 | -0.13 | 0.07 | -0.18 | 0.05 | -0.18 | 0.09 | -0.09 | -0.14 | 0.07 |
| curiosity_gap | -0.03 | -0.08 | -0.12 | -0.09 | 0.11 | -0.09 | 0.17 | 0.14 | -0.16 | -0.17 | -0.15 | 0.17 |
| educational | 0.32 | 0.13 | 0.05 | 0.17 | 0.02 | 0.03 | 0.01 | 0.39 | -0.11 | -0.05 | 0.06 | -0.06 |
| humor | -0.02 | 0.02 | -0.01 | -0.05 | 0.08 | -0.06 | 0.06 | -0.04 | -0.02 | 0.05 | -0.03 | -0.02 |
| outrage | -0.61 | -0.06 | 0.03 | -0.16 | 0.10 | -0.19 | 0.09 | -0.25 | -0.01 | -0.08 | -0.23 | 0.21 |
| sensational | -0.71 | -0.04 | 0.07 | -0.20 | 0.11 | -0.15 | 0.15 | -0.33 | 0.08 | -0.05 | -0.21 | 0.31 |


LLM rating vs factor score, title level (Spearman, n = 3,000 rated titles):

| llm | F1 | F10 | F11 | F12 | F2 | F3 | F4 | F5 | F6 | F7 | F8 | F9 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| analytical | 0.19 | 0.11 | 0.06 | 0.10 | -0.04 | 0.09 | -0.02 | 0.22 | 0.02 | 0.04 | 0.09 | -0.11 |
| conversational | 0.15 | -0.02 | 0.03 | 0.01 | 0.03 | -0.03 | 0.14 | 0.07 | -0.08 | -0.04 | -0.03 | 0.06 |
| critical | -0.28 | 0.03 | 0.03 | -0.03 | 0.06 | -0.15 | -0.08 | -0.15 | 0.09 | -0.01 | -0.05 | -0.01 |
| curiosity_gap | 0.02 | 0.01 | -0.01 | -0.00 | 0.05 | -0.00 | 0.09 | 0.05 | -0.06 | -0.05 | -0.02 | 0.02 |
| educational | 0.15 | 0.08 | 0.06 | 0.02 | -0.01 | 0.04 | 0.04 | 0.20 | -0.02 | 0.02 | 0.05 | -0.03 |
| humor | 0.04 | 0.02 | 0.02 | -0.00 | -0.00 | -0.02 | -0.02 | -0.01 | -0.03 | -0.00 | -0.01 | -0.02 |
| outrage | -0.34 | 0.01 | 0.03 | -0.03 | 0.10 | -0.08 | -0.02 | -0.13 | -0.03 | -0.03 | -0.07 | 0.05 |
| sensational | -0.37 | 0.01 | 0.04 | -0.04 | 0.11 | -0.02 | 0.00 | -0.13 | 0.03 | -0.04 | -0.02 | 0.13 |


Test-retest reliability of the LLM rater (n = 300 titles rated twice in re-shuffled batches, same model, temperature 0):

| dimension | n | exact_agreement | within_1 | spearman_r | weighted_kappa | kappa |
|---|---|---|---|---|---|---|
| sensational | 300 | 0.623 | 0.783 | 0.743 | 0.742 |  |
| critical | 300 | 0.713 | 0.753 | 0.580 | 0.581 |  |
| analytical | 300 | 0.583 | 0.773 | 0.600 | 0.561 |  |
| educational | 300 | 0.823 | 0.953 | 0.268 | 0.251 |  |
| conversational | 300 | 0.903 | 0.947 | 0.518 | 0.659 |  |
| humor | 300 | 0.993 |  |  |  | 0.000 |
| curiosity_gap | 300 | 0.980 |  |  |  | 0.490 |
| outrage | 300 | 0.757 |  |  |  | 0.497 |
| format_llm | 300 | 0.797 |  |  |  | 0.591 |


Topic control: share of variance in each factor score explained by topic (title level, balanced subset) and how much creator-level variance topic mix accounts for:

| factor | n_topics | title_level_r2_topic | creator_level_r2_topic | creator_level_corr_raw_controlled | auto_name |
|---|---|---|---|---|---|
| F1 | 236 | 0.127 | 0.471 | 0.943 | +vader_compound -vader_neg -shock_word -violence_verb |
| F2 | 236 | 0.057 | 0.280 | 0.954 | +has_finite_verb +present_tense +past_tense +verb_share |
| F3 | 236 | 0.123 | 0.321 | 0.969 | +lead_colon_label +lead_live +colon -entity_first |
| F4 | 236 | 0.072 | 0.124 | 0.978 | +discourse_marker +trailing_ellipsis +ellipsis +contraction |
| F5 | 236 | 0.039 | 0.222 | 0.981 | +q_word_start +wh_any +why_marker +q_mark |
| F6 | 236 | 0.173 | 0.393 | 0.955 | +n_person +has_person |
| F7 | 236 | 0.111 | 0.274 | 0.957 | +noun_share -cap_token_share +adj_share +n_gpe |
| F8 | 236 | 0.176 | 0.681 | 0.801 | +num_share +digit +year_mention |
| F9 | 236 | 0.054 | 0.164 | 0.981 | +allcaps_word_share +full_caps_title +has_allcaps_word |
| F10 | 236 | 0.049 | 0.207 | 0.955 | +quoted_speech +quotes |
| F11 | 236 | 0.086 | 0.272 | 0.956 | +vader_pos +n_chars +nominalisation |
| F12 | 236 | 0.089 | 0.429 | 0.895 | +future_will +modal +first_pl |


Lane medians of topic-controlled scores, videos (non-low-n creators):

| lane | n | F1 | F2 | F3 | F4 | F5 | F6 | F7 | F8 | F9 | F10 | F11 | F12 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| centrist_heterodox | 10 | 0.40 | 0.42 | -0.35 | -0.08 | 0.59 | -0.38 | -0.85 | -0.09 | -0.44 | -0.49 | -0.77 | -0.01 |
| explainer_geopolitics | 3 | 1.14 | -0.36 | -0.17 | -0.26 | 2.12 | -0.99 | -0.31 | -0.21 | -0.08 | -0.99 | -0.37 | -0.05 |
| humour_satire | 6 | 0.55 | -0.29 | -0.44 | -0.03 | 0.05 | -0.25 | -0.80 | -0.35 | -0.59 | -0.58 | -0.04 | -0.17 |
| independent_digital_news | 19 | -0.12 | 0.15 | -0.21 | -0.10 | 0.41 | -0.09 | -0.71 | -0.14 | -0.32 | 0.03 | -0.19 | -0.16 |
| interview_podcast | 19 | 0.19 | -0.36 | -0.21 | -0.17 | 0.73 | 0.44 | -0.77 | -0.21 | -0.27 | -0.32 | -0.39 | -0.15 |
| left_commentary | 40 | -0.31 | -0.24 | -0.31 | -0.15 | -0.11 | -0.16 | -0.49 | -0.16 | -0.27 | -0.51 | -0.15 | -0.29 |
| legal_institutional | 8 | 0.16 | -0.09 | -0.24 | -0.29 | 0.04 | -0.22 | -0.70 | -0.02 | -0.56 | -0.35 | 0.05 | -0.15 |
| right_commentary | 69 | 0.16 | -0.03 | -0.28 | -0.14 | 0.18 | -0.30 | -0.69 | -0.17 | -0.33 | -0.46 | -0.16 | -0.23 |
| right_tv_network | 4 | 0.55 | -0.48 | 0.03 | -0.26 | -0.25 | 0.50 | -0.39 | -0.08 | -0.14 | 0.43 | 0.15 | -0.13 |
| streamer_reaction | 23 | 0.01 | -0.16 | -0.38 | -0.08 | -0.11 | -0.52 | -0.32 | -0.23 | -0.13 | -0.34 | -0.69 | -0.49 |
| us_legacy_tv | 9 | 0.69 | 0.39 | -0.31 | -0.11 | 0.07 | -0.44 | 1.16 | -0.20 | -0.32 | 0.15 | 0.00 | -0.04 |
| us_press_print_digital | 18 | 0.66 | -0.02 | -0.31 | -0.12 | 1.03 | -0.25 | -0.44 | -0.08 | -0.39 | -0.10 | -0.17 | -0.01 |
| wire_international | 11 | 0.34 | 0.53 | -0.43 | -0.08 | 0.08 | -0.41 | 0.85 | 0.01 | 0.02 | 0.19 | -0.13 | 0.37 |


Lane medians of topic-controlled scores, streams (non-low-n creators):

| lane | n | F1 | F2 | F3 | F4 | F5 | F6 | F7 | F8 | F9 | F10 | F11 | F12 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| centrist_heterodox | 2 | 0.22 | -0.84 | 0.41 | -0.12 | -0.13 | 1.60 | -0.61 | -0.19 | -0.62 | -0.59 | -0.33 | -0.04 |
| humour_satire | 1 | 0.27 | -1.17 | -0.24 | -0.10 | -0.29 | 0.67 | -0.53 | 0.01 | -0.31 | -0.66 | 0.12 | -0.39 |
| independent_digital_news | 6 | -0.38 | -0.70 | -0.04 | -0.13 | -0.37 | -0.01 | -0.26 | 0.20 | -0.73 | -0.53 | 0.31 | 0.08 |
| interview_podcast | 2 | 0.03 | -1.34 | -0.27 | -0.40 | -0.33 | 1.01 | -0.87 | 0.18 | -0.53 | -0.76 | -0.27 | -0.04 |
| left_commentary | 18 | -0.39 | -0.36 | -0.35 | -0.21 | -0.28 | 0.79 | -0.40 | 0.03 | -0.40 | -0.47 | 0.25 | 0.02 |
| legal_institutional | 3 | 0.20 | -0.33 | -0.34 | 0.22 | -0.23 | 1.05 | -0.40 | -0.16 | 0.25 | -0.28 | 1.47 | -0.58 |
| right_commentary | 19 | 0.16 | -0.32 | -0.30 | -0.06 | -0.21 | -0.09 | -0.63 | -0.01 | -0.44 | -0.52 | 0.10 | -0.08 |
| right_tv_network | 4 | 0.33 | -0.36 | 1.00 | -0.31 | -0.33 | 0.02 | -0.12 | 0.01 | 1.40 | -0.57 | 0.01 | -0.32 |
| streamer_reaction | 6 | 0.09 | -0.14 | -0.36 | -0.11 | -0.22 | 0.35 | 0.04 | 0.08 | 0.37 | -0.36 | -0.02 | -0.33 |
| us_legacy_tv | 7 | 0.29 | 0.48 | 0.88 | -0.26 | -0.35 | -0.11 | 1.01 | -0.13 | -0.50 | -0.67 | -0.55 | -0.30 |
| us_press_print_digital | 4 | 0.37 | -1.24 | 0.45 | -0.23 | -0.44 | 0.17 | 0.21 | 0.17 | -0.74 | -0.71 | -0.75 | -0.13 |
| wire_international | 7 | 0.03 | 0.02 | 1.48 | -0.04 | -0.31 | 0.61 | 0.25 | 0.31 | -0.12 | 0.01 | -0.12 | 0.16 |


Creators at the extremes of each topic-controlled dimension (videos):

| factor | name | highest (videos) | lowest (videos) |
|---|---|---|---|
| F1 | Positive tone vs outrage (shock words, violence verbs, negative sentiment) | @CoreyGilShusterAskProject, @NPR, @turningpointusa, @POLITICO, @RonPlacone | @DannyHaiphongYT, @BlackConservativePerspective, @katiephangnews, @DoubleDownNews, @bennyjohnson |
| F2 | Clause headline vs noun-phrase (finite verbs, tense) | @moreperfectunion, @Tim_Black, @CoreyGilShusterAskProject, @MattWalsh, @bbrettcooper | @joerogan, @FleccasTalks, @TimDillonShow, @BelleRanch, @newdiscourses |
| F3 | Labelled live/formulaic headline (LIVE:, BREAKING:, colon labels) | @RSBN, @aaronparnas1, @TimesNowWorld, @DailyDenims, @LukeBeasley | @DylanBurnsLIVE, @ANINewsIndia, @thewarningwithsteveschmidt, @lovettorleaveitpodcast, @thegrayzone7996 |
| F4 | Conversational stream talk (chat, ellipsis, contractions, imperatives, we) | @BelleRanch, @AsmonTV, @bennyjohnson, https://rumble.com/c/russellbrand, @harryjsisson | @thewarningwithsteveschmidt, @ActualJusticeWarrior, @FleccasTalks, @OutKick, @joerogan |
| F5 | Question and explainer framing (why, what, ?) | @TheEconomist, @wsj, @nationalreview, @TheDailyBeast, @CoreyGilShusterAskProject | @AndWeKnowOfficial-o9b, @CashJordan, @BlackConservativePerspective, @ActualJusticeWarrior, @Timcast |
| F6 | Person-centred (named people) | @BadFaithPodcast, @DannyHaiphongYT, @JamarlThomas, @fastpoliticspodcast, @Semafor | @CoreyGilShusterAskProject, @GeopoliticalEconomyReport, @moreperfectunion, @dineshdsouza, @thedavidpakmanshow |
| F7 | Descriptive news prose vs title-case (nouns, adjectives, places) | @aljazeeraenglish, @Reuters, @CBSNews, @USATODAY, @thegrayzone7996 | @moreperfectunion, @DrSteveTurleyTV, @jlptalk, @DoubleDownNews, @PiersMorganUncensored |
| F8 | Numeric and dated (digits, years) | @HasanAbiVODs3, @60minutes, @Firstpost, @Forbes, @jlptalk | @PoliticsGirl, @triggerpod, @TheEconomist, @UnHerd, @LukeBeasley |
| F9 | ALL-CAPS shouting | @JacksonHinkleOfficial, @FleccasTalks, @AndWeKnowOfficial-o9b, @katiephangnews, @TimcastNews | @joerogan, @JackCocchiarellaShow, @TheHumanistReport, @TheDailyBeast, @triggerpod |
| F10 | Quoted speech | @PiersMorganUncensored, @timesofindia, @jlptalk, @CashJordan, @msnow | @DrSteveTurleyTV, @ZeihanonGeopolitics, @PartOfTheProblem, @SabbySabs, @ThePodcastoftheLotusEaters |
| F11 | Long, upbeat, abstract (length, positive words, nominalisations) | @AndWeKnowOfficial-o9b, https://rumble.com/c/BannonsWarRoom, @BlackConservativePerspective, @DrSteveTurleyT... | @SydneyWatson, @thewarningwithsteveschmidt, @PartOfTheProblem, @joerogan, @AlexStein99 |
| F12 | Modal and future speculation (will, could, we) | @moreperfectunion, @thewarningwithsteveschmidt, @BelleRanch, @CoreyGilShusterAskProject, @TheEconomist | @AsmonTV, @destinyhqclips, @bennyjohnson, @SydneyWatson, @The_Crucible |


Lexical diversity: Heaps' exponent and Zipf exponent on 20 subsamples per creator x genre; rank correlations across subsample sizes (sample-size sensitivity):

| measure | n_a | n_b | n_groups | spearman | mean_a | mean_b |
|---|---|---|---|---|---|---|
| heaps_beta | 1000 | 1500 | 215 | 0.995 | 0.829 | 0.817 |
| zipf | 1000 | 1500 | 215 | 0.971 | 0.687 | 0.718 |
| heaps_beta | 1500 | 3000 | 143 | 0.991 | 0.820 | 0.798 |
| zipf | 1500 | 3000 | 143 | 0.919 | 0.719 | 0.770 |
| heaps_beta | 1000 | 3000 | 143 | 0.978 | 0.831 | 0.798 |
| zipf | 1000 | 3000 | 143 | 0.817 | 0.687 | 0.770 |


Heaps' exponent at 1,500 tokens, videos (n = 164): lowest (most repetitive vocabulary) @harryjsisson, @ponderingpolitics, @LukeBeasley, @JackCocchiarellaShow, @briantylercohen; highest @nypost, @MLChristiansen, @Reuters, @Styxhexenhammer666, @FoxNewsChannelClips. Mean 0.822, sd 0.035.


## Stage 3: formats and hooks

Hook classifier (StandardScaler + LogisticRegression(class_weight=balanced); features: 768-d sentence embedding + ['allcaps_word_share', 'excl', 'q_mark', 'trailing_ellipsis', 'violence_verb', 'shock_word', 'curiosity_lex', 'fwd_ref_start', 'discourse_marker', 'has_person', 'neg_eval', 'pos_eval']), trained on the LLM labels:

| hook | n_train | n_test | base_rate | C | holdout_accuracy | holdout_balanced_accuracy | holdout_f1 | holdout_auc | holdout_kappa |
|---|---|---|---|---|---|---|---|---|---|
| curiosity_gap | 2400 | 600 | 0.021 | 0.300 | 0.953 | 0.609 | 0.176 | 0.736 | 0.155 |
| outrage | 2400 | 600 | 0.572 | 0.030 | 0.762 | 0.760 | 0.787 | 0.843 | 0.517 |
| humor | 2400 | 600 | 0.004 | 0.030 | 0.997 | 0.500 | 0.000 | 0.729 | 0.000 |


Share of titles per category, videos (mean of creator shares, non-low-n creators):

| lane | n_creators | question | breaking_live | episode_show | interview_guest | reaction | confrontation | listicle | howto_explainer | curiosity_gap | outrage | humor |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| centrist_heterodox | 10.00 | 0.19 | 0.01 | 0.02 | 0.09 | 0.01 | 0.04 | 0.00 | 0.12 | 0.04 | 0.54 | 0.00 |
| explainer_geopolitics | 3.00 | 0.53 | 0.00 | 0.01 | 0.04 | 0.00 | 0.02 | 0.00 | 0.10 | 0.04 | 0.26 | 0.00 |
| humour_satire | 6.00 | 0.16 | 0.02 | 0.17 | 0.15 | 0.03 | 0.07 | 0.00 | 0.05 | 0.02 | 0.45 | 0.00 |
| independent_digital_news | 19.00 | 0.18 | 0.02 | 0.03 | 0.09 | 0.01 | 0.07 | 0.00 | 0.09 | 0.03 | 0.61 | 0.00 |
| interview_podcast | 19.00 | 0.19 | 0.01 | 0.11 | 0.18 | 0.01 | 0.09 | 0.00 | 0.12 | 0.01 | 0.41 | 0.00 |
| left_commentary | 40.00 | 0.10 | 0.05 | 0.02 | 0.10 | 0.01 | 0.08 | 0.00 | 0.05 | 0.03 | 0.76 | 0.00 |
| legal_institutional | 8.00 | 0.15 | 0.03 | 0.01 | 0.08 | 0.01 | 0.06 | 0.00 | 0.10 | 0.02 | 0.76 | 0.00 |
| right_commentary | 69.00 | 0.15 | 0.01 | 0.08 | 0.08 | 0.03 | 0.08 | 0.00 | 0.09 | 0.04 | 0.63 | 0.00 |
| right_tv_network | 4.00 | 0.06 | 0.18 | 0.26 | 0.10 | 0.02 | 0.07 | 0.00 | 0.05 | 0.01 | 0.42 | 0.00 |
| streamer_reaction | 23.00 | 0.09 | 0.00 | 0.05 | 0.08 | 0.10 | 0.14 | 0.00 | 0.04 | 0.04 | 0.65 | 0.00 |
| us_legacy_tv | 9.00 | 0.08 | 0.03 | 0.02 | 0.07 | 0.02 | 0.05 | 0.00 | 0.04 | 0.02 | 0.33 | 0.00 |
| us_press_print_digital | 18.00 | 0.26 | 0.01 | 0.02 | 0.09 | 0.01 | 0.04 | 0.00 | 0.15 | 0.02 | 0.28 | 0.00 |
| wire_international | 11.00 | 0.22 | 0.02 | 0.00 | 0.08 | 0.01 | 0.06 | 0.00 | 0.08 | 0.03 | 0.43 | 0.00 |


Share of titles per category, streams (mean of creator shares, non-low-n creators):

| lane | n_creators | question | breaking_live | episode_show | interview_guest | reaction | confrontation | listicle | howto_explainer | curiosity_gap | outrage | humor |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| centrist_heterodox | 2.00 | 0.08 | 0.23 | 0.00 | 0.41 | 0.01 | 0.04 | 0.00 | 0.02 | 0.00 | 0.40 | 0.00 |
| humour_satire | 1.00 | 0.06 | 0.00 | 0.31 | 0.79 | 0.00 | 0.02 | 0.00 | 0.02 | 0.00 | 0.42 | 0.02 |
| independent_digital_news | 6.00 | 0.09 | 0.31 | 0.01 | 0.10 | 0.01 | 0.07 | 0.00 | 0.03 | 0.02 | 0.63 | 0.00 |
| interview_podcast | 2.00 | 0.20 | 0.02 | 0.42 | 0.08 | 0.01 | 0.11 | 0.00 | 0.05 | 0.02 | 0.54 | 0.00 |
| left_commentary | 18.00 | 0.10 | 0.13 | 0.04 | 0.21 | 0.02 | 0.12 | 0.00 | 0.04 | 0.02 | 0.77 | 0.00 |
| legal_institutional | 3.00 | 0.21 | 0.07 | 0.25 | 0.11 | 0.01 | 0.09 | 0.00 | 0.04 | 0.01 | 0.64 | 0.00 |
| right_commentary | 19.00 | 0.17 | 0.19 | 0.23 | 0.16 | 0.03 | 0.11 | 0.00 | 0.07 | 0.04 | 0.62 | 0.00 |
| right_tv_network | 4.00 | 0.02 | 0.48 | 0.46 | 0.12 | 0.00 | 0.04 | 0.00 | 0.01 | 0.01 | 0.39 | 0.00 |
| streamer_reaction | 6.00 | 0.20 | 0.03 | 0.17 | 0.07 | 0.02 | 0.45 | 0.00 | 0.01 | 0.02 | 0.58 | 0.01 |
| us_legacy_tv | 7.00 | 0.04 | 0.39 | 0.00 | 0.11 | 0.01 | 0.04 | 0.00 | 0.01 | 0.01 | 0.12 | 0.00 |
| us_press_print_digital | 4.00 | 0.00 | 0.39 | 0.08 | 0.10 | 0.01 | 0.02 | 0.00 | 0.00 | 0.01 | 0.09 | 0.00 |
| wire_international | 7.00 | 0.05 | 0.71 | 0.00 | 0.09 | 0.02 | 0.08 | 0.00 | 0.01 | 0.04 | 0.36 | 0.00 |


Rule vs LLM format label on the rated sample (rule = regex on the raw title; LLM = single format label):

| category | n | rule_positives | llm_positives | precision_rule_vs_llm | recall_rule_vs_llm | f1 | kappa | agreement |
|---|---|---|---|---|---|---|---|---|
| question | 3000 | 424 | 58 | 0.101 | 0.741 | 0.178 | 0.149 | 0.868 |
| breaking_live | 3000 | 251 | 268 | 0.813 | 0.761 | 0.786 | 0.766 | 0.963 |
| episode_show | 3000 | 226 | 228 | 0.544 | 0.539 | 0.542 | 0.504 | 0.931 |
| interview_guest | 3000 | 326 | 99 | 0.181 | 0.596 | 0.278 | 0.239 | 0.898 |
| reaction | 3000 | 78 | 56 | 0.487 | 0.679 | 0.567 | 0.558 | 0.981 |
| confrontation | 3000 | 239 | 98 | 0.205 | 0.500 | 0.291 | 0.256 | 0.920 |
| listicle | 3000 | 3 | 4 | 0.667 | 0.500 | 0.571 | 0.571 | 0.999 |
| howto_explainer | 3000 | 219 | 75 | 0.174 | 0.507 | 0.259 | 0.230 | 0.927 |


Examples (corpus-wide, three per category):

| category | creator | title |
|---|---|---|
| question | @ABCNews | How Sysco acquiring Restaurant Depot could shake up the food industry |
| question | @nytimes | How Americans Are Struggling With Rising Healthcare Costs |
| question | @SkyNews | Is Trump about to bring down NATO? \| Trump100 |
| breaking_live | @StatusCoup | BREAKING: LIVE ICE Protests as Lawsuit Filed to SHUT DOWN Delaney Hall ICE Prison |
| breaking_live | @TimesNowWorld | FRANCE WILDFIRE LIVE \| Mega-Fire 4x Size Of Paris Out Of Control Near Bordeaux \| TIMES NOW WORLD |
| breaking_live | @Firstpost | LIVE: 'US Aims For $1.5 Trillion Defence Budget,' Says Hegseth at NATO Defence Ministers' Meet |
| episode_show | @markets | Micron Earnings Spark Global Tech Rebound \| Daybreak Europe 6/25/2026 |
| episode_show | @TheDamageReport | The Damage Report: April 20, 2026 |
| episode_show | @ABCNews | Vance Warns Pope To "Be Careful" On Theology - What You Need To Know - April 15th, 2026 |
| interview_guest | @underthedesknews | FULL TOP STORY: Sen. Graham Conspired w/ Israel to DESTROY the International Criminal Court |
| interview_guest | @NBCNews | Father reunites with five daughters after months overseas |
| interview_guest | @timesofindia | ‘Taco Welcome’: Barred From US, Iran Football Boss Joins Emotional Mexico Crowd \| FIFA World Cup |
| reaction | @Firstpost | US-Iran War Ceasefire LIVE: Iranians and Americans Reacts to Trump's Ceasefire Announcement \| N18G |
| reaction | @wethefifth | Media Insiders React to the Scott Pelley 60 Minutes Drama - The Fifth Column |
| reaction | @msnow | 'This is about Trump': Elections expert reacts to Virginia redistricting measure passing |
| confrontation | @Firstpost | Red Fort Attack LIVE: Pakistan's Terror Lies Busted As JeM’s Hand Emerge in Lal Qila Blast |
| confrontation | @timesofindia | '5th Time You Blinked': Reporter Grills Trump On Iran U-Turn; Shock 'I Don't Know' Reply Follows |
| confrontation | @PTLRadioShow | MAGA Callers Accuse Brian Shapiro Of Lying… Then Get Fact-Checked |
| listicle | @Firstpost | US-Iran War Top 5 Developments: Tehran Claims Drone Attack Amid Hormuz Tensions \| Firstpost Live |
| listicle | @TheMajorityReport | 39 Times Trump Claimed An Iran Deal Was Imminent |
| listicle | @NewsNation | An MLB opening day preview, plus March Madness Sweet 16 predictions \| Morning in America |
| howto_explainer | @JackCocchiarellaShow | Fox Host Suffers Emotional Breakdown As Trump Loses Senate |
| howto_explainer | @AssociatedPress | AP reporter breaks down Supreme Court ruling striking down Trump’s tariffs |
| howto_explainer | @RealAmericasVoice | 9/11 Widow Terry Strada REVEALS What Happened After Her Husband’s FINAL Call |
| curiosity_gap | @LukeBeasley | Actually, what the f*** just happened?! |
| curiosity_gap | https://rumble.com/c/russellbrand | They don't want you knowing this... |
| curiosity_gap | @AsmonTV | Holy sh*t.. How is this real? |
| outrage | @timesofindia | ‘Humiliated’ Trump Fires EXPLOSIVE WARNING To Canada In Extreme Meltdown \| ‘NO MORE BENEFITS!’ |
| outrage | @LukeBeasley | SHOCK BREAKING: TRUMP S*X BOMBSHELL ERUPTS, PUBLIC MELTDOWN BACKFIRES! |
| outrage | @BlackConservativePerspective | Leftists PANIC As Wife EXPOSES Another HUMILIATING Scandal Against IMPLODING Communist Democrat! |
| humor | @TimcastIRL | THIS IS HILARIOUS |
| humor | @TimcastNews | THIS IS HILARIOUS |
| humor | @TheQuartering | THIS IS HILARIOUS |


## Stage 4: the landscape

Agglomerative clustering of creators in style space (topic-controlled factor scores, Ward) and topic space (Jensen-Shannon distance between topic mixes, average linkage), k by silhouette; adjusted Rand index against the lanes and against each other. Run on all titles and on political titles only:


| genre | titles | n_creators | n_lanes | style_k | style_silhouette | topic_k | topic_silhouette | ari_style_vs_lane | ari_topic_vs_lane | ari_style_vs_topic | ari_style_vs_lane_k_lanes | ari_topic_vs_lane_k_lanes | ari_style_vs_topic_k_lanes |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| videos | all | 239 | 13 | 11 | 0.128 | 3 | 0.144 | 0.045 | 0.004 | 0.003 | 0.030 | -0.001 | 0.007 |
| videos | political | 234 | 13 | 10 | 0.136 | 3 | 0.110 | 0.061 | -0.013 | -0.004 | 0.064 | 0.004 | 0.010 |
| streams | all | 79 | 12 | 9 | 0.159 | 12 | 0.089 | 0.002 | 0.179 | 0.075 | 0.006 | 0.179 | 0.066 |
| streams | political | 77 | 12 | 3 | 0.150 | 3 | 0.088 | -0.034 | -0.017 | 0.143 | 0.013 | 0.183 | 0.085 |


Style cohesion per lane (mean within-lane vs between-lane distance in z-scored style space; ratio < 1 = lane-mates are closer than average):

| genre | lane | n_creators | within_lane_distance | between_lane_distance | cohesion_ratio |
|---|---|---|---|---|---|
| streams | legal_institutional | 3 | 3.285 | 4.549 | 0.722 |
| streams | us_press_print_digital | 4 | 3.205 | 4.374 | 0.733 |
| streams | centrist_heterodox | 2 | 3.000 | 4.000 | 0.750 |
| streams | us_legacy_tv | 7 | 3.654 | 4.853 | 0.753 |
| streams | wire_international | 7 | 4.410 | 4.736 | 0.931 |
| streams | independent_digital_news | 6 | 4.205 | 4.422 | 0.951 |
| streams | interview_podcast | 2 | 4.325 | 4.477 | 0.966 |
| streams | left_commentary | 18 | 4.683 | 4.707 | 0.995 |
| streams | streamer_reaction | 6 | 4.638 | 4.596 | 1.009 |
| streams | right_tv_network | 4 | 4.787 | 4.704 | 1.018 |
| streams | right_commentary | 19 | 5.254 | 4.947 | 1.062 |
| videos | us_legacy_tv | 9 | 3.302 | 4.926 | 0.670 |
| videos | streamer_reaction | 23 | 3.741 | 4.333 | 0.863 |
| videos | humour_satire | 6 | 3.785 | 4.307 | 0.879 |
| videos | us_press_print_digital | 18 | 4.138 | 4.588 | 0.902 |
| videos | centrist_heterodox | 10 | 3.981 | 4.398 | 0.905 |
| videos | interview_podcast | 19 | 4.135 | 4.459 | 0.927 |
| videos | right_commentary | 69 | 4.240 | 4.472 | 0.948 |
| videos | legal_institutional | 8 | 4.186 | 4.302 | 0.973 |
| videos | wire_international | 11 | 5.147 | 5.290 | 0.973 |
| videos | independent_digital_news | 19 | 4.387 | 4.502 | 0.975 |
| videos | left_commentary | 40 | 4.586 | 4.640 | 0.988 |
| videos | right_tv_network | 4 | 5.688 | 5.310 | 1.071 |
| videos | explainer_geopolitics | 3 | 6.035 | 5.450 | 1.107 |


Where lane and style disagree (videos, all titles):

| kind | group | n_creators | n_style_clusters | largest_cluster_share | members |
|---|---|---|---|---|---|
| lane split across style clusters | independent_digital_news | 19 | 8 | 0.316 | @BreakThroughNews (S0); @zeteo (S0); @RebelNewsOnline (S0); @GeopoliticalEconomyReport (S0); @RedactedNews ... |
| lane split across style clusters | explainer_geopolitics | 3 | 3 | 0.333 | @nousnetwork (S0); @ZeihanonGeopolitics (S2); @CoreyGilShusterAskProject (S3) |
| lane split across style clusters | us_press_print_digital | 18 | 5 | 0.333 | @wsj (S0); @nytimes (S0); @TheAtlantic (S0); @TheDailyBeast (S0); @nationalreview (S0); @Vox (S0); @NYTPodc... |
| lane split across style clusters | right_commentary | 69 | 6 | 0.362 | @RileyGaines (S0); @StevenCrowder (S0); @RufoandLomez (S0); @TheAmalaEkpunobi (S0); https://rumble.com/c/Th... |
| lane split across style clusters | left_commentary | 40 | 6 | 0.375 | @thomhartmann (S0); @thedavidpakmanshow (S0); @Tim_Black (S0); @MrTariqNasheed (S0); @jimacosta (S0); @TheH... |
| lane split across style clusters | legal_institutional | 8 | 5 | 0.375 | @LeejaMiller (S0); @LegalAFMTN (S1); @GlennKirschner2 (S2); @LegalEagle (S2); @RobertGouveiaEsq (S2); @Viva... |
| lane split across style clusters | streamer_reaction | 23 | 6 | 0.391 | @DestinyDGGClips (S0); @HasanAbi (S0); @Xanderhal (S0); @Vaush (S0); @MikeFromPA (S0); @hutch (S0); @TheVau... |
| lane split across style clusters | centrist_heterodox | 10 | 4 | 0.400 | @KimIversen (S0); @RestPoliticsUS (S0); @UnHerd (S0); @chriscuomo (S0); @TheLincolnProject (S2); https://ru... |
| lane split across style clusters | interview_podcast | 19 | 4 | 0.421 | @ColemanHughesOfficial (S0); @EzraKleinShow (S0); @samharrisorg (S0); @JillianMichaels (S0); @morebridgetph... |
| lane split across style clusters | humour_satire | 6 | 3 | 0.500 | @AlexStein99 (S0); @SMN (S0); @franifio (S0); @TimDillonShow (S2); @RonPlacone (S6); @lovettorleaveitpodcas... |
| lane split across style clusters | right_tv_network | 4 | 3 | 0.500 | @RealAmericasVoice (S6); @oann (S6); @RSBN (S7); @NewsmaxTV (S9) |
| lane split across style clusters | wire_international | 11 | 6 | 0.545 | @ajplus (S0); @TimesNowWorld (S1); @TheEconomist (S3); @timesofindia (S4); @ANINewsIndia (S9); @AssociatedP... |
| lane split across style clusters | us_legacy_tv | 9 | 2 | 0.889 | @ABCNews (S9); @CBSNews (S9); @CNN (S9); @FoxNews (S9); @FoxNewsChannelClips (S9); @NBCNews (S9); @NewsNati... |
| style cluster spanning lanes | S10 | 5 | 5 | 0.200 | @chinainsights-r2w (independent_digital_news); @HasanAbiVODs3 (streamer_reaction); @60minutes (us_legacy_tv... |
| style cluster spanning lanes | S3 | 4 | 4 | 0.250 | @thewarningwithsteveschmidt (centrist_heterodox); @CoreyGilShusterAskProject (explainer_geopolitics); @more... |
| style cluster spanning lanes | S6 | 54 | 10 | 0.259 | @DarkHorsePod (centrist_heterodox); @bulwarkmedia (centrist_heterodox); @wethefifth (centrist_heterodox); @... |
| style cluster spanning lanes | S2 | 51 | 10 | 0.294 | @TheLincolnProject (centrist_heterodox); https://rumble.com/c/russellbrand (centrist_heterodox); @ZeihanonG... |
| style cluster spanning lanes | S0 | 69 | 11 | 0.362 | @KimIversen (centrist_heterodox); @RestPoliticsUS (centrist_heterodox); @UnHerd (centrist_heterodox); @chri... |
| style cluster spanning lanes | S9 | 21 | 5 | 0.381 | @thegrayzone7996 (independent_digital_news); @NewsmaxTV (right_tv_network); @ABCNews (us_legacy_tv); @CBSNe... |
| style cluster spanning lanes | S4 | 10 | 6 | 0.400 | @DemocracyNow (independent_digital_news); @rolandsmartin (independent_digital_news); @PiersMorganUncensored... |
| style cluster spanning lanes | S1 | 20 | 6 | 0.450 | @DoubleDownNews (independent_digital_news); @StatusCoup (independent_digital_news); @LukeBeasley (left_comm... |
| style cluster spanning lanes | S7 | 2 | 2 | 0.500 | @aaronparnas1 (left_commentary); @RSBN (right_tv_network) |


Who gets named (creator-balanced titles; people keyed by surname, so 'Kirk' pools Charlie and Erika Kirk):

| entity | n_titles_balanced | share_of_balanced_titles | n_creators | top_lanes_by_share | outrage_share | overall_outrage_share | outrage_ratio |
|---|---|---|---|---|---|---|---|
| Trump | 7619 | 0.041 | 199 | legal_institutional (9.2%); left_commentary (6.2%); us_legacy_tv (4.9%) | 0.668 | 0.567 | 1.180 |
| Hormuz | 1065 | 0.006 | 86 | wire_international (1.5%); us_press_print_digital (0.9%); us_legacy_tv (0.8%) | 0.515 | 0.567 | 0.910 |
| Hegseth | 1062 | 0.006 | 106 | us_press_print_digital (1.1%); left_commentary (0.9%); us_legacy_tv (0.8%) | 0.533 | 0.567 | 0.940 |
| Putin | 992 | 0.005 | 67 | wire_international (1.9%); interview_podcast (0.6%); independent_digital_news (0.4%) | 0.689 | 0.567 | 1.210 |
| Charlie Kirk | 910 | 0.005 | 118 | right_tv_network (2.1%); right_commentary (0.8%); streamer_reaction (0.6%) | 0.534 | 0.567 | 0.940 |
| JD Vance | 886 | 0.005 | 120 | humour_satire (0.8%); left_commentary (0.8%); centrist_heterodox (0.7%) | 0.568 | 0.567 | 1.000 |
| Mamdani | 765 | 0.004 | 111 | right_commentary (0.8%); us_press_print_digital (0.7%); right_tv_network (0.6%) | 0.699 | 0.567 | 1.230 |
| Netanyahu | 726 | 0.004 | 113 | interview_podcast (1.2%); wire_international (0.6%); left_commentary (0.4%) | 0.696 | 0.567 | 1.230 |
| Epstein | 708 | 0.004 | 114 | us_legacy_tv (0.7%); left_commentary (0.5%); us_press_print_digital (0.4%) | 0.720 | 0.567 | 1.270 |
| Lindsey Graham | 628 | 0.003 | 123 | humour_satire (0.7%); right_tv_network (0.7%); us_legacy_tv (0.5%) | 0.478 | 0.567 | 0.840 |
| Brian Shapiro | 594 | 0.003 | 85 | left_commentary (1.0%); streamer_reaction (0.4%); humour_satire (0.3%) | 0.769 | 0.567 | 1.360 |
| Nancy Guthrie | 550 | 0.003 | 35 | us_legacy_tv (1.8%); us_press_print_digital (0.3%); right_tv_network (0.2%) | 0.165 | 0.567 | 0.290 |
| Kristi Noem | 543 | 0.003 | 103 | humour_satire (1.1%); left_commentary (0.6%); us_legacy_tv (0.3%) | 0.737 | 0.567 | 1.300 |
| Mike Johnson | 538 | 0.003 | 91 | interview_podcast (1.6%); right_tv_network (0.7%); left_commentary (0.5%) | 0.572 | 0.567 | 1.010 |
| Kash Patel | 479 | 0.003 | 89 | humour_satire (0.6%); centrist_heterodox (0.5%); legal_institutional (0.5%) | 0.766 | 0.567 | 1.350 |
| Karoline Leavitt | 473 | 0.003 | 55 | right_tv_network (0.7%); left_commentary (0.5%); us_press_print_digital (0.3%) | 0.526 | 0.567 | 0.930 |
| Jack Smith | 449 | 0.002 | 95 | legal_institutional (0.7%); independent_digital_news (0.4%); right_tv_network (0.3%) | 0.552 | 0.567 | 0.970 |
| Pam Bondi | 447 | 0.002 | 92 | left_commentary (0.4%); legal_institutional (0.4%); us_legacy_tv (0.4%) | 0.826 | 0.567 | 1.460 |
| Candace Owens | 416 | 0.002 | 71 | right_commentary (0.7%); streamer_reaction (0.6%); left_commentary (0.2%) | 0.743 | 0.567 | 1.310 |
| Keir Starmer | 397 | 0.002 | 43 | wire_international (0.8%); independent_digital_news (0.6%); right_commentary (0.1%) | 0.471 | 0.567 | 0.830 |
| Hillary Clinton | 396 | 0.002 | 88 | us_press_print_digital (0.4%); right_tv_network (0.4%); us_legacy_tv (0.3%) | 0.697 | 0.567 | 1.230 |
| Graham Platner | 393 | 0.002 | 102 | humour_satire (0.7%); streamer_reaction (0.6%); us_legacy_tv (0.4%) | 0.588 | 0.567 | 1.040 |
| Lindsay Clancy | 392 | 0.002 | 52 | us_legacy_tv (0.8%); us_press_print_digital (0.5%); wire_international (0.2%) | 0.184 | 0.567 | 0.320 |
| Marco Rubio | 388 | 0.002 | 85 | wire_international (0.4%); us_press_print_digital (0.3%); us_legacy_tv (0.3%) | 0.392 | 0.567 | 0.690 |
| Obama | 345 | 0.002 | 97 | legal_institutional (0.4%); humour_satire (0.3%); left_commentary (0.3%) | 0.603 | 0.567 | 1.060 |


| entity | n_titles_balanced | share_of_balanced_titles | n_creators | top_lanes_by_share | outrage_share | overall_outrage_share | outrage_ratio |
|---|---|---|---|---|---|---|---|
| Trump | 8817 | 0.047 | 193 | us_legacy_tv (8.2%); left_commentary (8.1%); legal_institutional (6.2%) | 0.667 | 0.567 | 1.180 |
| White House | 1565 | 0.008 | 120 | us_press_print_digital (1.7%); us_legacy_tv (1.5%); right_tv_network (1.1%) | 0.414 | 0.567 | 0.730 |
| GOP | 1509 | 0.008 | 106 | us_legacy_tv (1.8%); centrist_heterodox (1.3%); legal_institutional (1.2%) | 0.718 | 0.567 | 1.270 |
| MAGA | 1009 | 0.005 | 123 | left_commentary (1.7%); centrist_heterodox (1.2%); streamer_reaction (1.0%) | 0.926 | 0.567 | 1.630 |
| Senate | 976 | 0.005 | 97 | us_legacy_tv (1.4%); us_press_print_digital (1.1%); right_tv_network (0.8%) | 0.379 | 0.567 | 0.670 |
| FBI | 885 | 0.005 | 119 | us_legacy_tv (1.1%); legal_institutional (1.0%); right_tv_network (1.0%) | 0.739 | 0.567 | 1.300 |
| Supreme Court | 856 | 0.005 | 107 | legal_institutional (4.6%); us_legacy_tv (0.8%); us_press_print_digital (0.7%) | 0.522 | 0.567 | 0.920 |
| NATO | 822 | 0.004 | 86 | wire_international (1.3%); us_legacy_tv (0.4%); right_tv_network (0.4%) | 0.513 | 0.567 | 0.910 |
| House | 815 | 0.004 | 94 | us_legacy_tv (1.0%); us_press_print_digital (1.0%); right_tv_network (0.6%) | 0.406 | 0.567 | 0.720 |
| Congress | 773 | 0.004 | 113 | legal_institutional (0.9%); wire_international (0.6%); us_press_print_digital (0.5%) | 0.492 | 0.567 | 0.870 |
| CNN | 583 | 0.003 | 95 | right_commentary (0.7%); left_commentary (0.4%); us_legacy_tv (0.4%) | 0.798 | 0.567 | 1.410 |
| DHS | 515 | 0.003 | 68 | us_legacy_tv (1.0%); right_tv_network (0.7%); us_press_print_digital (0.6%) | 0.423 | 0.567 | 0.750 |
| EU | 447 | 0.002 | 41 | wire_international (1.0%); explainer_geopolitics (0.2%); interview_podcast (0.1%) | 0.443 | 0.567 | 0.780 |
| NASA | 430 | 0.002 | 44 | us_legacy_tv (0.7%); wire_international (0.5%); us_press_print_digital (0.4%) | 0.077 | 0.567 | 0.140 |
| Pentagon | 421 | 0.002 | 73 | us_legacy_tv (0.7%); us_press_print_digital (0.4%); wire_international (0.3%) | 0.428 | 0.567 | 0.750 |
| REUTERS | 402 | 0.002 | 3 | wire_international (1.1%); us_press_print_digital (0.0%) | 0.214 | 0.567 | 0.380 |
| CIA | 375 | 0.002 | 104 | interview_podcast (0.6%); independent_digital_news (0.4%); right_tv_network (0.3%) | 0.661 | 0.567 | 1.170 |
| World News | 375 | 0.002 | 2 | wire_international (1.0%) | 0.765 | 0.567 | 1.350 |
| HasanAbi | 365 | 0.002 | 5 | streamer_reaction (4.7%) | 0.433 | 0.567 | 0.760 |
| BJP | 342 | 0.002 | 5 | wire_international (0.9%); explainer_geopolitics (0.5%); us_press_print_digital (0.0%) | 0.295 | 0.567 | 0.520 |
| Fed | 333 | 0.002 | 57 | us_press_print_digital (0.5%); us_legacy_tv (0.3%); legal_institutional (0.2%) | 0.423 | 0.567 | 0.750 |
| Vantage on Firstpost | 315 | 0.002 | 1 | wire_international (0.8%) | 0.463 | 0.567 | 0.820 |
| ABC News Live | 314 | 0.002 | 1 | us_legacy_tv (1.4%) | 0.010 | 0.567 | 0.020 |
| Fox News | 313 | 0.002 | 60 | left_commentary (0.6%); streamer_reaction (0.2%); independent_digital_news (0.1%) | 0.917 | 0.567 | 1.620 |
| UN | 289 | 0.002 | 51 | wire_international (0.6%); explainer_geopolitics (0.2%); us_press_print_digital (0.1%) | 0.467 | 0.567 | 0.820 |


Convergent formulas: 1,575 distinct titles (case-insensitive) are used verbatim by two or more creators, 474 of them by creators from different organisations (the rest are same-outlet cross-posts such as TYT / The Damage Report); of those 474, 38.4% stay within one lane. 500 masked templates (names and numbers replaced, at least one content word) are shared across organisations; 26.0% within one lane.


| example | n_creators | n_titles | lanes | creators |
|---|---|---|---|---|
| THIS IS INSANE.. | 12 | 14 | centrist_heterodox; independent_digital_news; left_commentary; right_commentary; streamer_reaction | @AsmonTV; @BenShapiro; @JackCocchiarellaShow; @JacksonHinkleOfficial; @LukeBeasley; @RedactedNews; @TheMajo... |
| IT HAPPENED AGAIN?? | 7 | 10 | independent_digital_news; left_commentary; right_commentary; streamer_reaction | @HasanAbi; @JackCocchiarellaShow; @LiberalHivemind; @RebelNewsOnline; @TheQuartering; @TimcastNews; @adammo... |
| This changes everything.. | 7 | 7 | centrist_heterodox; independent_digital_news; right_commentary; streamer_reaction | @AsmonTV; @CashJordan; @DestinyDGGClips; @DoubleDownNews; @TheQuartering; @TimcastIRL; https://rumble.com/c... |
| IT'S HAPPENING | 6 | 10 | independent_digital_news; left_commentary; right_commentary; streamer_reaction | @JacksonHinkleOfficial; @LiberalHivemind; @RebelNewsOnline; @TimcastIRL; @Vaush; @adammockler |
| This Is Disgusting | 6 | 6 | left_commentary; right_commentary; streamer_reaction | @AsmonTV; @HasanAbi; @LukeBeasley; @TheMajorityReport; @TheQuartering; @TimcastIRL |
| it’s over. | 5 | 9 | right_commentary; streamer_reaction | @AsmonTV; @HasanAbi; @JacksonHinkleOfficial; @bennyjohnson; @destiny |
| It’s finally happening.. | 5 | 6 | independent_digital_news; left_commentary; right_commentary; streamer_reaction | @AsmonTV; @JackCocchiarellaShow; @RebelNewsOnline; @TimcastIRL; @bennyjohnson |
| Don Lemon ARRESTED! | 5 | 5 | left_commentary; legal_institutional; right_commentary | @BenShapiro; @GlennKirschner2; @TheYoungTurks; @TimcastNews; @marclamonthillnetwork |
| This can't be real.. | 5 | 5 | independent_digital_news; left_commentary; right_commentary; streamer_reaction | @AsmonTV; @RebelNewsOnline; @TimcastIRL; @Vaush; @adammockler |
| This is so embarrassing.. | 5 | 5 | left_commentary; streamer_reaction | @AsmonTV; @TheVaushPit; @TheYoungTurks; @destiny; @harryjsisson |
| This is terrifying... | 5 | 5 | left_commentary; right_commentary; streamer_reaction | @HasanAbi; @TheMajorityReport; @TheQuartering; @TheVaushPit; @TimcastNews |
| Oh.. my.. god... | 4 | 8 | left_commentary; right_commentary; streamer_reaction | @AsmonTV; @HasanAbi; @JackCocchiarellaShow; @TheQuartering |
| It finally happened | 4 | 6 | left_commentary; streamer_reaction | @HasanAbi; @JackCocchiarellaShow; @LukeBeasley; @adammockler |
| BREAKING: TRUMP FIRES PAM BONDI | 4 | 5 | centrist_heterodox; left_commentary; streamer_reaction | @Vaush; @aaronparnas1; @bulwarkmedia; @podsaveamerica |
| HOLY SH*T.. | 4 | 5 | right_commentary; streamer_reaction | @AsmonTV; @HasanAbi; @JacksonHinkleOfficial; @LiberalHivemind |
| THIS IS HILARIOUS | 4 | 5 | right_commentary; streamer_reaction | @MikeFromPA; @TheQuartering; @TimcastIRL; @TimcastNews |
| THIS IS REALLY BAD | 4 | 5 | left_commentary; right_commentary; streamer_reaction | @HasanAbi; @JackCocchiarellaShow; @bennyjohnson; @harryjsisson |
| He actually did it.. | 4 | 4 | left_commentary; right_commentary; streamer_reaction | @AsmonTV; @Timcast; @TimcastNews; @ponderingpolitics |
| It has begun | 4 | 4 | right_commentary; streamer_reaction | @HasanAbi; @Timcast; @TimcastIRL; @TimcastNews |
| It’s getting worse… | 4 | 4 | left_commentary; right_commentary | @TheQuartering; @TimcastIRL; @adammockler; @ponderingpolitics |
| 🚨They Actually Did It… | 4 | 4 | right_commentary | @TheQuartering; @TimcastIRL; @TimcastNews; @bennyjohnson |
| THIS COULD CHANGE EVERYTHING | 4 | 4 | centrist_heterodox; right_commentary; right_tv_network | @RealAmericasVoice; @TimcastIRL; @TimcastNews; https://rumble.com/c/russellbrand |
| THIS IS CRAZY | 4 | 4 | right_commentary; streamer_reaction | @HasanAbi; @TheQuartering; @TimcastIRL; @TimcastNews |
| TRUMP JUST LOST IT! | 4 | 4 | left_commentary | @FarronBalanced; @JackCocchiarellaShow; @LukeBeasley; @MeidasTouch |
| We need to talk about this.. | 4 | 4 | left_commentary; right_commentary; streamer_reaction | @AsmonTV; @TheQuartering; @TheVaushPit; @therationalnational |


| template | n_creators | n_titles | lanes | example |
|---|---|---|---|---|
| <ENT> 's <ENT> | 62 | 147 | centrist_heterodox; explainer_geopolitics; humour_satire; independent_digital_news; interview_podcast; left... | Iran's Plan To Make You SIMP |
| <ENT> after <ENT> | 37 | 73 | independent_digital_news; interview_podcast; left_commentary; legal_institutional; right_commentary; right_... | Trump’s Envoys Get RUDE AWAKENING After Putin Meeting |
| <ENT> 's <ENT> <ENT> | 23 | 40 | explainer_geopolitics; interview_podcast; left_commentary; legal_institutional; right_commentary; streamer_... | California's Election Shakeup + Microsoft's AI Spy Badge \| PBD #811 |
| <ENT> ’s <ENT> | 18 | 28 | explainer_geopolitics; humour_satire; independent_digital_news; left_commentary; right_commentary; streamer... | AIPAC’s "Elect Chicago Women" Super PAC Exposed |
| <ENT> exposes <ENT> | 14 | 19 | interview_podcast; left_commentary; legal_institutional; right_commentary; right_tv_network | Elizabeth Warren Exposes Trump’s Fed Pick In Brutal Hearing |
| <ENT> <ENT> 's <ENT> | 13 | 19 | explainer_geopolitics; interview_podcast; left_commentary; legal_institutional; right_commentary; us_legacy... | US Media's Hasan Piker Derangement Syndrome Is Ridiculous |
| <ENT> <ENT> after <ENT> | 13 | 15 | left_commentary; right_commentary; right_tv_network; streamer_reaction; us_press_print_digital; wire_intern... | OMG: Trump RUSHES OFF after Going to HOSPITAL! |
| <ENT> after <ENT> <ENT> | 11 | 16 | left_commentary; right_tv_network; us_press_print_digital; wire_international | Hakeem Jeffries In Full Panic Mode After Kushner Meeting Pisses Off Democrats |
| <ENT> vs. <ENT> | 11 | 11 | centrist_heterodox; interview_podcast; left_commentary; right_commentary; right_tv_network; streamer_reacti... | Ben Shapiro vs. Fortnite |
| <ENT> w/ <ENT> | 10 | 38 | centrist_heterodox; interview_podcast; left_commentary; right_commentary | Biblical Idolatry & The Role of Moses w/ Jordan B. Peterson |
| <ENT> <ENT> w/ <ENT> | 10 | 20 | centrist_heterodox; independent_digital_news; interview_podcast; left_commentary; right_commentary | "It Went Completely Viral" Brett Cooper Talks Internet Drama & Pendragon Cycle W/ Michael Knowles |
| <ENT> says <ENT> | 10 | 17 | interview_podcast; left_commentary; right_commentary; us_press_print_digital; wire_international | Fox News Lunatic Says Americans Have Data Center Derangement Syndrome |
| <ENT> 's <ENT> in <ENT> | 10 | 13 | explainer_geopolitics; independent_digital_news; interview_podcast; left_commentary; legal_institutional; r... | AOC's DISASTROUS Foreign Policy Debut In Munich |
| <ENT> <ENT> 's <ENT> <ENT> | 9 | 11 | centrist_heterodox; interview_podcast; left_commentary; right_commentary; us_press_print_digital; wire_inte... | Bill Kristol: MAGA's Grievance Culture \| The Bulwark Podcast |
| the truth about <ENT> | 9 | 9 | centrist_heterodox; interview_podcast; left_commentary; right_commentary; right_tv_network; streamer_reaction | The truth about Blizzard |
| <ENT> on <ENT> 's <ENT> | 8 | 10 | interview_podcast; left_commentary; right_commentary; us_press_print_digital | Aaron Rodgers Torched Fauci on ESPN's Own Air |
| <ENT> on live tv | 7 | 10 | left_commentary | Epstein Victim-Smearer Humiliated On Live TV |
| <ENT> destroys <ENT> | 7 | 8 | left_commentary; right_commentary; streamer_reaction | Candace Owens EXPOSES & DESTROYS Ben Shapiro! |
| <ENT> under the bus | 7 | 8 | humour_satire; left_commentary | Dems Throw Trans Folks Under The Bus |
| <ENT> is here | 7 | 7 | interview_podcast; left_commentary; right_commentary; streamer_reaction; us_legacy_tv | The Radical Left’s Hostile Takeover Is Here |
| <ENT> ft # <ENT> | 6 | 7 | humour_satire; independent_digital_news; left_commentary; right_commentary | Catholic & Protestant Debunk Islam & Atheist Arguments \| ft. Billy Hallowell |
| <ENT> against <ENT> | 6 | 6 | left_commentary; legal_institutional; us_press_print_digital | Ben Shapiro Lobs WILD Accusation Against Dave Smith |
| <ENT> off on <ENT> | 6 | 6 | humour_satire; left_commentary; right_commentary | Adam Conover GOES OFF on Tech Companies & A.I. |
| <ENT> senator <ENT> | 6 | 6 | centrist_heterodox; left_commentary; us_press_print_digital; wire_international | Republican Senator SLAMS Trump |
| <ENT> panic as <ENT> | 5 | 14 | left_commentary; right_commentary | Republicans PANIC as Reporters Fact-Check Them LIVE! |


## Stage 5: time and engagement

Monthly drift, January-September (September is 1-14 and never compared on volume). Lane-level trends with |Spearman| >= 0.6 and p < 0.05 over the nine months (54 of 360 lane x genre x measure series):


| group | genre | measure | spearman_trend | p | first_month_value | last_full_month_value |
|---|---|---|---|---|---|---|
| wire_international | streams | F7_controlled | -0.983 | 0.000 | 0.268 | 0.042 |
| legal_institutional | streams | F1_controlled | -0.933 | 0.000 | -0.884 | -1.933 |
| us_legacy_tv | streams | F3_controlled | -0.917 | 0.001 | 1.413 | 0.328 |
| right_tv_network | videos | F3_controlled | -0.883 | 0.002 | 0.766 | 0.618 |
| right_commentary | streams | F8_controlled | -0.883 | 0.002 | 1.595 | -0.268 |
| wire_international | videos | F7_controlled | -0.867 | 0.003 | 0.895 | 0.650 |
| us_legacy_tv | streams | outrage | -0.833 | 0.005 | 0.152 | 0.092 |
| left_commentary | videos | F9_controlled | -0.833 | 0.005 | 0.348 | -0.065 |
| right_tv_network | streams | F4_controlled | -0.800 | 0.010 | -0.251 | -0.397 |
| right_tv_network | videos | curiosity_gap | -0.783 | 0.013 | 0.016 | 0.009 |
| right_tv_network | videos | F5_controlled | -0.783 | 0.013 | -0.158 | -0.403 |
| right_commentary | videos | F5_controlled | -0.783 | 0.013 | 0.267 | 0.124 |
| us_legacy_tv | streams | F7_controlled | -0.783 | 0.013 | 1.301 | 1.073 |
| independent_digital_news | streams | outrage | -0.783 | 0.013 | 0.686 | 0.631 |
| left_commentary | videos | F11_controlled | -0.767 | 0.016 | -0.031 | -0.156 |
| independent_digital_news | streams | F2_controlled | -0.767 | 0.016 | -0.534 | -0.716 |
| left_commentary | videos | outrage | -0.750 | 0.020 | 0.791 | 0.736 |
| right_tv_network | videos | F10_controlled | -0.733 | 0.025 | 0.452 | -0.063 |
| left_commentary | videos | F5_controlled | -0.717 | 0.030 | 0.066 | 0.064 |
| interview_podcast | streams | F11_controlled | -0.717 | 0.030 | -0.690 | -0.842 |
| right_tv_network | streams | F5_controlled | -0.717 | 0.030 | 0.247 | -0.323 |
| right_tv_network | videos | F4_controlled | -0.667 | 0.050 | -0.255 | -0.333 |
| legal_institutional | videos | F4_controlled | 0.667 | 0.050 | -0.222 | -0.139 |
| explainer_geopolitics | videos | F2_controlled | 0.667 | 0.050 | -1.531 | -0.628 |
| us_press_print_digital | videos | F5_controlled | 0.667 | 0.050 | 0.869 | 1.802 |
| streamer_reaction | videos | F3_controlled | 0.683 | 0.042 | -0.437 | -0.339 |
| right_commentary | videos | F10_controlled | 0.683 | 0.042 | -0.365 | -0.241 |
| interview_podcast | videos | curiosity_gap | 0.700 | 0.036 | 0.000 | 0.015 |
| interview_podcast | videos | F11_controlled | 0.700 | 0.036 | -0.497 | -0.323 |
| us_legacy_tv | streams | F8_controlled | 0.700 | 0.036 | -0.489 | -0.298 |
| wire_international | streams | F10_controlled | 0.717 | 0.030 | -0.112 | 0.175 |
| left_commentary | videos | F8_controlled | 0.717 | 0.030 | -0.173 | -0.108 |
| us_legacy_tv | streams | F10_controlled | 0.733 | 0.025 | -0.824 | -0.681 |
| wire_international | videos | F8_controlled | 0.733 | 0.025 | 0.177 | 0.221 |
| right_tv_network | streams | F9_controlled | 0.733 | 0.025 | 0.577 | 1.683 |
| us_press_print_digital | streams | F9_controlled | 0.750 | 0.020 | -0.938 | -0.745 |
| wire_international | videos | curiosity_gap | 0.750 | 0.020 | 0.026 | 0.030 |
| right_tv_network | streams | F2_controlled | 0.750 | 0.020 | -1.150 | -0.312 |
| left_commentary | streams | F6_controlled | 0.750 | 0.020 | 0.630 | 0.994 |
| us_press_print_digital | streams | F2_controlled | 0.767 | 0.016 | -0.999 | 0.388 |
| wire_international | videos | F6_controlled | 0.767 | 0.016 | -0.257 | -0.201 |
| us_legacy_tv | streams | F6_controlled | 0.783 | 0.013 | -0.143 | 0.224 |
| centrist_heterodox | streams | F8_controlled | 0.786 | 0.036 | -0.610 | -0.171 |
| left_commentary | videos | F1_controlled | 0.817 | 0.007 | -0.380 | -0.169 |
| right_tv_network | streams | outrage | 0.833 | 0.005 | 0.206 | 0.416 |
| us_legacy_tv | streams | F5_controlled | 0.850 | 0.004 | -0.366 | 0.102 |
| wire_international | streams | F9_controlled | 0.850 | 0.004 | -0.449 | -0.244 |
| interview_podcast | videos | F2_controlled | 0.867 | 0.003 | -0.601 | -0.365 |
| wire_international | videos | F3_controlled | 0.867 | 0.003 | -0.351 | -0.224 |
| us_legacy_tv | streams | F9_controlled | 0.867 | 0.003 | -0.603 | -0.180 |
| us_press_print_digital | streams | F10_controlled | 0.883 | 0.002 | -1.112 | -0.380 |
| us_press_print_digital | streams | F7_controlled | 0.900 | 0.001 | -0.000 | 1.968 |
| right_commentary | streams | curiosity_gap | 0.900 | 0.001 | 0.000 | 0.044 |
| us_press_print_digital | streams | F8_controlled | 0.933 | 0.000 | -0.117 | 0.470 |


Month-to-month topic change (mean Jensen-Shannon distance between a creator's consecutive monthly topic mixes; videos):

| lane | 2026-02 | 2026-03 | 2026-04 | 2026-05 | 2026-06 | 2026-07 | 2026-08 | 2026-09 |
|---|---|---|---|---|---|---|---|---|
| centrist_heterodox | 0.76 | 0.73 | 0.64 | 0.71 | 0.70 | 0.68 | 0.71 | 0.77 |
| explainer_geopolitics | 0.74 | 0.80 | 0.66 | 0.77 | 0.68 | 0.58 | 0.62 | 0.58 |
| humour_satire | 0.91 | 0.93 | 0.84 | 0.87 | 0.91 | 0.85 | 0.92 | 0.86 |
| independent_digital_news | 0.67 | 0.66 | 0.64 | 0.61 | 0.64 | 0.60 | 0.65 | 0.67 |
| interview_podcast | 0.77 | 0.67 | 0.68 | 0.73 | 0.69 | 0.76 | 0.71 | 0.75 |
| left_commentary | 0.59 | 0.64 | 0.60 | 0.61 | 0.60 | 0.60 | 0.60 | 0.59 |
| legal_institutional | 0.57 | 0.63 | 0.63 | 0.61 | 0.61 | 0.61 | 0.57 | 0.61 |
| right_commentary | 0.71 | 0.72 | 0.68 | 0.67 | 0.69 | 0.70 | 0.69 | 0.67 |
| right_tv_network | 0.58 | 0.62 | 0.60 | 0.62 | 0.57 | 0.62 | 0.64 | 0.66 |
| streamer_reaction | 0.64 | 0.70 | 0.66 | 0.70 | 0.70 | 0.62 | 0.64 | 0.69 |
| us_legacy_tv | 0.59 | 0.61 | 0.52 | 0.53 | 0.51 | 0.49 | 0.47 | 0.56 |
| us_press_print_digital | 0.68 | 0.68 | 0.61 | 0.63 | 0.61 | 0.59 | 0.64 | 0.63 |
| wire_international | 0.50 | 0.55 | 0.42 | 0.45 | 0.44 | 0.40 | 0.41 | 0.45 |


Engagement, within creator (OLS of log views on standardised title predictors with month and topic controls, HC3; views are a fetch-time snapshot that favours older videos):


| genre | predictor | n_creators | median_coef_per_sd | q25 | q75 | share_positive | share_sig_positive | share_sig_negative | share_same_sign_as_median | median_r2 |
|---|---|---|---|---|---|---|---|---|---|---|
| streams | F1 | 59.000 | -0.013 | -0.061 | 0.023 | 0.339 | 0.034 | 0.085 | 0.661 | 0.405 |
| streams | F10 | 59.000 | 0.004 | -0.027 | 0.033 | 0.542 | 0.017 | 0.051 | 0.542 | 0.405 |
| streams | F11 | 59.000 | 0.002 | -0.031 | 0.034 | 0.525 | 0.085 | 0.051 | 0.525 | 0.405 |
| streams | F12 | 59.000 | 0.004 | -0.034 | 0.033 | 0.576 | 0.034 | 0.068 | 0.576 | 0.405 |
| streams | F2 | 59.000 | 0.019 | -0.020 | 0.054 | 0.576 | 0.051 | 0.017 | 0.576 | 0.405 |
| streams | F3 | 59.000 | 0.008 | -0.035 | 0.051 | 0.559 | 0.085 | 0.085 | 0.559 | 0.405 |
| streams | F4 | 59.000 | 0.014 | -0.012 | 0.057 | 0.661 | 0.169 | 0.051 | 0.661 | 0.405 |
| streams | F5 | 59.000 | 0.010 | -0.042 | 0.039 | 0.508 | 0.102 | 0.017 | 0.508 | 0.405 |
| streams | F6 | 59.000 | 0.021 | -0.028 | 0.073 | 0.593 | 0.085 | 0.051 | 0.593 | 0.405 |
| streams | F7 | 59.000 | -0.010 | -0.057 | 0.026 | 0.458 | 0.034 | 0.136 | 0.542 | 0.405 |
| streams | F8 | 59.000 | 0.006 | -0.027 | 0.063 | 0.525 | 0.085 | 0.051 | 0.525 | 0.405 |
| streams | F9 | 59.000 | 0.007 | -0.027 | 0.043 | 0.559 | 0.085 | 0.051 | 0.559 | 0.405 |
| streams | curiosity_gap | 54.000 | -0.001 | -0.020 | 0.021 | 0.481 | 0.019 | 0.111 | 0.519 | 0.405 |
| streams | humor | 13.000 | 0.011 | -0.006 | 0.021 | 0.692 | 0.077 | 0.000 | 0.692 | 0.376 |
| streams | n_tokens | 59.000 | -0.003 | -0.045 | 0.033 | 0.458 | 0.085 | 0.085 | 0.542 | 0.405 |
| streams | outrage | 59.000 | 0.044 | 0.000 | 0.096 | 0.746 | 0.203 | 0.000 | 0.746 | 0.405 |
| videos | F1 | 193.000 | -0.023 | -0.070 | 0.019 | 0.352 | 0.021 | 0.187 | 0.648 | 0.296 |
| videos | F10 | 193.000 | -0.006 | -0.050 | 0.023 | 0.425 | 0.036 | 0.124 | 0.575 | 0.296 |
| videos | F11 | 193.000 | -0.010 | -0.054 | 0.042 | 0.430 | 0.067 | 0.109 | 0.570 | 0.296 |
| videos | F12 | 193.000 | -0.031 | -0.081 | 0.005 | 0.295 | 0.026 | 0.145 | 0.705 | 0.296 |
| videos | F2 | 193.000 | 0.011 | -0.026 | 0.056 | 0.611 | 0.104 | 0.031 | 0.611 | 0.296 |
| videos | F3 | 193.000 | -0.008 | -0.061 | 0.034 | 0.435 | 0.104 | 0.078 | 0.565 | 0.296 |
| videos | F4 | 193.000 | 0.016 | -0.017 | 0.056 | 0.663 | 0.119 | 0.047 | 0.663 | 0.296 |
| videos | F5 | 193.000 | -0.022 | -0.052 | 0.015 | 0.368 | 0.062 | 0.104 | 0.632 | 0.296 |
| videos | F6 | 193.000 | 0.028 | -0.022 | 0.072 | 0.637 | 0.150 | 0.036 | 0.637 | 0.296 |
| videos | F7 | 193.000 | -0.023 | -0.075 | 0.012 | 0.347 | 0.073 | 0.119 | 0.653 | 0.296 |
| videos | F8 | 193.000 | -0.011 | -0.058 | 0.034 | 0.425 | 0.073 | 0.093 | 0.575 | 0.296 |
| videos | F9 | 193.000 | 0.014 | -0.020 | 0.055 | 0.596 | 0.088 | 0.036 | 0.596 | 0.296 |
| videos | curiosity_gap | 185.000 | 0.000 | -0.020 | 0.025 | 0.503 | 0.016 | 0.027 | 0.503 | 0.294 |
| videos | humor | 92.000 | 0.002 | -0.021 | 0.024 | 0.533 | 0.076 | 0.033 | 0.533 | 0.255 |
| videos | n_tokens | 193.000 | 0.011 | -0.041 | 0.065 | 0.549 | 0.140 | 0.088 | 0.549 | 0.296 |
| videos | outrage | 193.000 | 0.042 | -0.003 | 0.082 | 0.731 | 0.238 | 0.010 | 0.731 | 0.296 |


Hit concentration (creator x genre with >= 100 videos carrying views):

| genre | n_creators | median_gini | median_top10_share | median_top1_share | powerlaw_like | median_alpha |
|---|---|---|---|---|---|---|
| streams | 59 | 0.358 | 0.292 | 0.066 | 0.017 | 2.739 |
| videos | 193 | 0.512 | 0.382 | 0.094 | 0.000 | 2.748 |


Concentration vs style, pooled within lane (lane-demeaned Spearman across creators):

| genre | target | predictor | n_creators | spearman_r | p |
|---|---|---|---|---|---|
| streams | gini | F10_controlled | 59 | -0.338 | 0.009 |
| streams | gini | F11_controlled | 59 | -0.293 | 0.024 |
| streams | gini | F12_controlled | 59 | -0.185 | 0.161 |
| streams | gini | F1_controlled | 59 | 0.343 | 0.008 |
| streams | gini | F2_controlled | 59 | -0.081 | 0.542 |
| streams | gini | F3_controlled | 59 | 0.375 | 0.003 |
| streams | gini | F4_controlled | 59 | 0.253 | 0.053 |
| streams | gini | F5_controlled | 59 | 0.060 | 0.654 |
| streams | gini | F6_controlled | 59 | -0.179 | 0.176 |
| streams | gini | F7_controlled | 59 | -0.113 | 0.392 |
| streams | gini | F8_controlled | 59 | -0.159 | 0.228 |
| streams | gini | F9_controlled | 59 | -0.036 | 0.785 |
| streams | gini | curiosity_gap | 59 | 0.032 | 0.812 |
| streams | gini | humor | 59 | 0.021 | 0.875 |
| streams | gini | log_n_videos | 59 | 0.096 | 0.470 |
| streams | gini | log_subscribers | 59 | 0.083 | 0.532 |
| streams | gini | outrage | 59 | -0.236 | 0.072 |
| streams | top10_share | F10_controlled | 59 | -0.365 | 0.004 |
| streams | top10_share | F11_controlled | 59 | -0.307 | 0.018 |
| streams | top10_share | F12_controlled | 59 | -0.159 | 0.229 |
| streams | top10_share | F1_controlled | 59 | 0.380 | 0.003 |
| streams | top10_share | F2_controlled | 59 | -0.162 | 0.220 |
| streams | top10_share | F3_controlled | 59 | 0.334 | 0.010 |
| streams | top10_share | F4_controlled | 59 | 0.243 | 0.064 |
| streams | top10_share | F5_controlled | 59 | 0.108 | 0.416 |
| streams | top10_share | F6_controlled | 59 | -0.207 | 0.116 |
| streams | top10_share | F7_controlled | 59 | -0.104 | 0.434 |
| streams | top10_share | F8_controlled | 59 | -0.102 | 0.443 |
| streams | top10_share | F9_controlled | 59 | -0.102 | 0.440 |
| streams | top10_share | curiosity_gap | 59 | 0.017 | 0.897 |
| streams | top10_share | humor | 59 | 0.092 | 0.487 |
| streams | top10_share | log_n_videos | 59 | 0.003 | 0.982 |
| streams | top10_share | log_subscribers | 59 | 0.081 | 0.541 |
| streams | top10_share | outrage | 59 | -0.289 | 0.026 |
| videos | gini | F10_controlled | 193 | 0.122 | 0.090 |
| videos | gini | F11_controlled | 193 | 0.111 | 0.125 |
| videos | gini | F12_controlled | 193 | 0.046 | 0.523 |
| videos | gini | F1_controlled | 193 | 0.130 | 0.072 |
| videos | gini | F2_controlled | 193 | -0.010 | 0.886 |
| videos | gini | F3_controlled | 193 | -0.037 | 0.612 |
| videos | gini | F4_controlled | 193 | -0.046 | 0.528 |
| videos | gini | F5_controlled | 193 | 0.223 | 0.002 |
| videos | gini | F6_controlled | 193 | 0.182 | 0.011 |
| videos | gini | F7_controlled | 193 | -0.073 | 0.312 |
| videos | gini | F8_controlled | 193 | 0.148 | 0.040 |
| videos | gini | F9_controlled | 193 | -0.153 | 0.034 |
| videos | gini | curiosity_gap | 193 | -0.107 | 0.140 |
| videos | gini | humor | 193 | 0.042 | 0.564 |
| videos | gini | log_n_videos | 193 | 0.012 | 0.869 |
| videos | gini | log_subscribers | 193 | -0.305 | 0.000 |
| videos | gini | outrage | 193 | -0.274 | 0.000 |
| videos | top10_share | F10_controlled | 193 | 0.116 | 0.110 |
| videos | top10_share | F11_controlled | 193 | 0.097 | 0.179 |
| videos | top10_share | F12_controlled | 193 | 0.032 | 0.659 |
| videos | top10_share | F1_controlled | 193 | 0.154 | 0.033 |
| videos | top10_share | F2_controlled | 193 | -0.003 | 0.972 |
| videos | top10_share | F3_controlled | 193 | -0.071 | 0.327 |
| videos | top10_share | F4_controlled | 193 | -0.076 | 0.294 |
| videos | top10_share | F5_controlled | 193 | 0.199 | 0.006 |
| videos | top10_share | F6_controlled | 193 | 0.157 | 0.029 |
| videos | top10_share | F7_controlled | 193 | -0.081 | 0.261 |
| videos | top10_share | F8_controlled | 193 | 0.131 | 0.068 |
| videos | top10_share | F9_controlled | 193 | -0.159 | 0.027 |
| videos | top10_share | curiosity_gap | 193 | -0.114 | 0.116 |
| videos | top10_share | humor | 193 | 0.034 | 0.641 |
| videos | top10_share | log_n_videos | 193 | -0.003 | 0.966 |
| videos | top10_share | log_subscribers | 193 | -0.324 | 0.000 |
| videos | top10_share | outrage | 193 | -0.281 | 0.000 |


## Files

Machine-readable interface tables: `features.csv`, `dimensions.csv`, `topics.csv`, `labels.csv`, `lanes.csv` (all under `data/titles/analysis/`). Profile cards: `pipeline_titles/reports/cards/`. HTML: `pipeline_titles/reports/title_stylometry.html`. Methods: `methods_appendix.md`.
