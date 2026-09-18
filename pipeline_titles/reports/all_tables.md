# Title Stylometry: all tables (reference dump), 2026-01-01 to 2026-09-14

_Generated 2026-09-17T20:49:09+00:00 by `python -m pipeline_titles.report`. Every table below is read from `data/titles/analysis/`; the code is `pipeline_titles/`._

Corpus: 309,596 titles from 274 creators (300,420 unique within creator x genre; 256,897 edited uploads, 52,699 live-stream VODs; 5,783 on Rumble). Genres are never pooled; a creator x genre with fewer than 50 unique titles is low-n and never ranked.

## Headline findings

_One plain-language finding per stage, written from the tables below (2026-09-14 run; channel groups from the 2026-09-15 leaning run, regrouped 2026-09-17). Re-check after a corpus refresh._

- **Stage 0, corpus.** The corpus is 309,596 titles from 274 creators, but four Indian news channels hold a fifth of it and 3.0 % of rows are verbatim live-loop repeats, so every corpus figure here is a mean of creator-level values or comes from the 189,240-title balanced subset. Brand stripping changed 34,394 titles; the creator-level Zipf exponent fell from 0.799 to 0.782 and the top-token share dropped most for show-branded channels (Rogan, Denims, Economist), which is the expected signature of removing the show-name head. No channel is categorised by hand: the one grouping of channels used anywhere in the report is the left / neutral / right channel group of the leaning stage (122 / 42 / 110 channels), which is how each channel's own titles read to a frontier model.
- **Stage 1, topics.** 236 topics; the Iran war / Strait of Hormuz story alone is 27,609 unique titles across 227 creators, and eleven of the twelve largest topics are shared by 100+ creators each. Topic mix does not separate the channel groups (adjusted Rand index 0.010 for videos): in 2026 the whole landscape covered the same stories, which is exactly why style had to be measured within topic. 212 of 236 topics are political; the non-political mass (crime trials, weather, sport, tech) sits with the neutral channels, the news outlets (mean political share 0.87 vs 0.95 for the left group and 0.92 for the right).
- **Stage 2, style dimensions.** Twelve factors survive (parallel analysis suggested 16; 47 % of variance). The candidate labels do not hold up: Sensational, Critical and Analytical all collapse onto one tone factor (F1, positive tone vs outrage; creator-level r with the LLM ratings -0.71, -0.49, +0.43), Educational maps only partially onto the question/explainer factor (F5, r 0.39), and Conversational (r 0.18) and Humor (r 0.08; the LLM flagged 0.4 % of titles) do not appear. The other factors are structural: clause vs noun-phrase headlines, LIVE/BREAKING labelling, stream talk (chat, ellipsis), person-centred titles, news prose vs title case, numbers, ALL CAPS, quotes. Topic accounts for 5-18 % of title-level score variance, and creator scores barely move when controlled (raw vs controlled r 0.80-0.98): style is a channel trait, not a story trait. The LLM rater's test-retest weighted kappa is 0.74 for sensational but only 0.25 for educational, so the validation is trustworthy for tone and weak for the rest. The model's loadings, validation and topic control are in the methods appendix and all_tables.md.
- **Stage 3, formats and hooks.** The outrage frame is the landscape's default hook: the LLM flagged 57 % of sampled titles, the classifier reproduces it well (hold-out AUC 0.84), and it covers 64 % of the average left channel's edited uploads, 60 % of the average right channel's and 36 % of the average neutral channel's, with a wide spread of channels inside every group. Curiosity-gap (2 %) and humour (0.4 %) were flagged too rarely to learn (hold-out F1 0.18 and 0.00): treat both as unmeasured, not absent. Question titles run at 16 % in all three groups; none of the structural formats separates the groups the way the outrage hook does.
- **Stage 4, landscape.** The channel groups predict style almost not at all: style clusters vs groups ARI 0.036 (videos, all titles) and 0.054 (political titles only); no group coheres in style space (cohesion ratios 1.01, 1.00 and 0.94 for left, neutral and right), and the largest style cluster holds 69 creators from all three groups. So the useful units are the style neighbours on each card, not the groups. Of 1,575 titles used verbatim by two or more creators, 474 cross organisations (the rest are TYT/Damage Report-type cross-posts) and 38 % of those are used in more than one channel group (a random pair of channels shares a group 38 % of the time, so verbatim sharing runs a little more within the camps than chance, the masked templates across them): "THIS IS INSANE.." is used by 12 creators across all three groups, "IT HAPPENED AGAIN??" by 7, and the shared templates are outrage frames ("<ENT> exposes <ENT>", "<ENT> destroys <ENT>", "<ENT> under the bus"). Trump is named in 3-5 % of balanced titles by 199 creators, most by the left group; the entities that carry the most outrage framing relative to baseline are MAGA (1.6x), Pam Bondi (1.5x), Kash Patel and Candace Owens (1.3x), the least are the crime-story names (Nancy Guthrie 0.3x, Lindsay Clancy 0.3x).
- **Stage 5, time and engagement.** Drift is small: 9 of 90 group-month series show a monotone trend; the left group's outrage share eased from 70 % to 65 % over the year and the right group's question framing fell, while the corpus mean stayed flat. Within creator, the outrage frame is the only title feature that predicts views with a consistent sign in the topic-controlled regression (median +0.04 log views per SD; positive for 73 % of 193 video channels, significant-positive for 24 %, significant-negative for 1 %); every dimension score and length has a median effect at or below 0.03 with 50-70 % sign agreement, which is a null result. Views are concentrated (median Gini 0.51; the top 10 % of a channel's videos take 38 % of its views) but not power-law: the Clauset-Shalizi-Newman test never significantly prefers the power law (0 of 193 video channels; the lognormal wins significantly in 79, the rest are inconclusive); within groups, concentration falls with the outrage share (rho -0.44), and every other correlate (quoted speech, modal / future wording, question framing, tone, the number of videos) is weak (|rho| <= 0.26).
- **Stage 6b, Zipf's law and views over time.** Title vocabulary is Zipfian with a flat head (exponent 0.86 over the top 100 words, 0.78 over the top 1,000, 1.01 over the top 5,000; R² 0.995). The three cuts move the words more than the curve: the left group (size-matched exponent 0.82) and the left-read titles (0.85) are the most concentrated systems, with "trump" ahead of "the"; the right-read titles are the flattest (0.77); ALL-CAPS titles are 6 tokens long against 11 for sentence case, with "this", "it" and "they" among their ten most frequent words. Views within a channel are not Zipfian (lognormal tails), and the neutral group is the hit-driven one (median Gini 0.67 vs 0.49 for left and right). Over the months the median left channel draws one and a half to two and a half times the views per video of the median right or neutral channel. Against each channel's own monthly baseline, capitals earn views in every month of the year (ALL CAPS +0.04 and selective CAPS +0.05 log points; Title Case -0.03, sentence case -0.03), and right-read titles do a little better than left-read ones, which do a little better than neither-read ones (+0.04, +0.01, -0.02); left and right channels shout at the same rate (48 % and 45 % of titles with capitals), the neutral group is sentence case (54 %).
- **Stage 0d, political leaning (2026-09-15; runs third in the pipeline, recorded as stage7_leaning).** Two levels. Titles: Claude Opus, through the Claude Code CLI, labelled 12,478 titles (50 per ranked channel, 16 for the 35 channels with fewer than 50 uploads) as left, right or neither from the title text alone, twenty titles to a call in a random order so that no title was judged beside its channel's other titles; it reads 55 % of titles as neither, 24 % as left and 20 % as right, and the words behind the labels are stance words (fraud, women, Democrats, woke, Kirk, California on the right; Trump, MAGA, war, Israel, breaking, Iran, Epstein on the left). Channels: each channel's score, (right − left) / titles sampled, sorts the 274 channels into 122 left, 110 right and 42 neutral (thresholds ±0.05); the score is reliable (split-half Spearman 0.96; the original 16-title draw and the 34 month-spread top-up titles rank the 239 ranked channels at 0.96). Everything the left channels published against everything the right channels published separates on the same words as the labelled titles, with the year's shared subjects at the apex; nothing moved month to month. A left / right / neither lexicon cut from the judge's own labels at |z| ≥ 1.96 recovers the ordering of channels (Spearman 0.69, out of fold) but not the title-level call (agreement 53 %, kappa 0.26): the judge reads framing, and a word list reads subjects.


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


Channel groups (left / neutral / right from each channel's title-leaning score, `leaning_by_creator.csv`; the only between-channel grouping in the report):

| group | creators | clippers |
|---|---|---|
| left | 122 | 5 |
| neutral | 42 | 2 |
| right | 110 | 4 |


Organisations with more than one channel (`creators.csv`): **Al Jazeera** (@ajplus, @aljazeeraenglish); **Blaze Media** (@BlazeTV, @glennbeck); **CBS News** (@60minutes, @CBSNews); **Crooked Media** (@lovettorleaveitpodcast, @podsaveamerica); **Daily Wire** (@AndrewKlavan, @BenShapiro, @MattWalsh, @MichaelKnowles); **Destiny** (@DestinyDGGClips, @destiny, @destinyhqclips); **Fox News** (@FoxNews, @FoxNewsChannelClips, @TheBrianKilmeadeShow); **HasanAbi** (@HasanAbi, @HasanAbiVODs3, @HasanReactionsfanTwo, @HasanabiClips); **MeidasTouch Network** (@LegalAFMTN, @MeidasTouch, @TheMichaelCohenShow, @katiephangnews); **Network18** (@Firstpost, @bushrakhanum); **New York Times** (@EzraKleinShow, @NYTOpinion, @NYTPodcasts, @nytimes); **PragerU** (@PragerU, @XAVIAER); **SNEAKO** (@LIVESNEAKO, @SNEAKO); **TYT Network** (@RebelHQ, @TheDamageReport, @TheYoungTurks); **Timcast** (@Timcast, @TimcastIRL, @TimcastNews); **Times Group** (@TimesNowWorld, @timesofindia); **Turning Point USA** (@RealAlexClark, @turningpointusa); **Vaush** (@TheVaushPit, @Vaush).


Clippers (titles written by fans or an editing team, kept as their own group): @AsmonTV, @ClipsCandaceOwens, @DailyDenims, @DestinyDGGClips, @FoxNewsChannelClips, @HasanAbiVODs3, @HasanReactionsfanTwo, @HasanabiClips, @TheVaushPit, @destinyhqclips, @laurenchenclips.


## Stage 1: topics

BERTopic on a 100,041-title creator-stratified sample (cap 561 per creator x genre): HDBSCAN found 236 topics (32.4% outliers); every title was then assigned to its nearest topic centroid (agreement with HDBSCAN's own labels on cluster members 85.5%; 13.4% of titles are weak assignments below the 10th-percentile similarity). 212 of 236 topics are political; 90.5% of unique titles (raw pooled) fall in political topics.


Political share by channel group (mean of creators, >= 50 unique titles):

| group | genre | n_creators | mean_political_share | median_political_share |
|---|---|---|---|---|
| left | streams | 33 | 0.955 | 0.977 |
| left | videos | 105 | 0.946 | 0.972 |
| neutral | streams | 16 | 0.849 | 0.861 |
| neutral | videos | 38 | 0.866 | 0.908 |
| right | streams | 30 | 0.918 | 0.958 |
| right | videos | 96 | 0.918 | 0.937 |


Largest topics (mean of group-level creator shares, i.e. creator-balanced):

| topic_id | label | political | category | mean_group_share | n_unique_all | n_creators | top_terms | example_1 |
|---|---|---|---|---|---|---|---|---|
| 0 | Iran War and Strait of Hormuz Tensions | yes | war_conflict | 0.0643 | 27609 | 227 | strait hormuz, strait, hormuz, irans, iranian, iran iran, tehran, war iran, bases, iran strikes | IRAN WAR NEWS LIVE \| Iran’s Hidden Strength Shocks Experts — Is Trump Really Getting Nervous Now? |
| 2 | Israel-Palestine Conflict Media | yes | world_politics | 0.0266 | 6035 | 195 | gaza, palestine, palestinian, israeli, netanyahu, israels, west bank, jews, palestinians, jewish | Ian Carroll: How Israel MANIPULATES Our Media! |
| 59 | Iran Conflict and Political Updates | yes | world_politics | 0.0236 | 1358 | 124 | joins, renner, ac, fail, reveal, iran hits, sus, durk, jamm, larry johnson | IRAN NUCLEAR DEAL, DOLLY PARTON TRIBUTE, CORY BOOKER REVEAL, PENTAGON INFLUENCER, CNN HASAN SMEAR |
| 3 | ICE Protests and Shootings | yes | us_politics | 0.0191 | 5189 | 210 | ice shooting, ice, ice agent, antiice, ice agents, minneapolis ice, minneapolis, agents, agent, protesters | Anti-ICE Protests LIVE From Washington DC: Charged Scenes After ICE Killing in Minneapolis \| US News |
| 1 | Shocking Events and Reactions | yes | media_culture_war | 0.0172 | 3996 | 171 | fing, holy, happening, theyre, holy sht, fck, im, fking, genuinely, fcked | WTF is happening.. |
| 4 | Ukraine-Russia War and Political Figures | yes | war_conflict | 0.0154 | 9808 | 134 | ukraine, russia, putin, putins, zelensky, russian, ukraine war, zelenskyy, russias, moscow | Russia Ukraine War LIVE: Zelensky's Message to Putin: End the War or Face Russia's Wrath |
| 40 | Trump's speeches and events | yes | us_politics | 0.0146 | 1944 | 84 | trump delivers, delivers remarks, trump speaks, davos, remarks, world economic, economic forum, delivers, l... | LIVE: Trump delivers remarks at the World Economic Forum |
| 13 | Modern Women and Feminism Debate | yes | media_culture_war | 0.0124 | 1346 | 170 | dating, women, feminism, modern women, men, modern, marriage, men women, divorce, pill | The Consequences of Modern Women's Actions |
| 22 | Christian Nationalism and Politics | yes | us_politics | 0.0123 | 1518 | 171 | jesus, christian, god, nationalism, christ, christianity, faith, bible, pastor, gospel | HOT TOPICS \| Pastor EXPOSES the Truth About Donald Trump, MAGA & Christian Nationalism! |
| 6 | Trump and China political relations | yes | world_politics | 0.0121 | 4790 | 165 | xi, china, chinas, taiwan, jiang, jinping, xi jinping, chinese, beijing, professor jiang | Trump in China: Why Xi Jinping Has the Upper Hand \| The Link \| 4K |
| 98 | JLP Weekly Series | no | media_culture_war | 0.0110 | 1243 | 182 | jlp wed, jlp, wed, jlp thu, thu, jlp mon, mon, jlp tue, tue, jlp fri | Through Hell to Clarity \| JLP Fri 4-17-26 |
| 9 | AI and Political Concerns | yes | us_politics | 0.0109 | 3547 | 187 | ai, anthropic, bubble, artificial, researcher, models, humans, ai slop, sanders, bernie sanders | AI Is Coming for Your Job — and Even Tech CEOs Aren’t Safe \| NYNext |
| 7 | Trump vs Maduro Venezuela Conflict | yes | world_politics | 0.0106 | 3556 | 179 | maduro, venezuela, venezuelas, venezuelan, capture, trumps venezuela, nicolas, venezuela oil, captured, ven... | 'US Will Run Venezuela After Maduro’s Capture': Trump's Big Announcement On Caracas Action |
| 5 | Trump Supreme Court Legal Issues | yes | us_politics | 0.0104 | 3769 | 166 | supreme court, supreme, trump doj, court, scotus, doj, judges, ruling, judge, legal af | LIVE: Trump DOJ Indictment DOOMED + SCOTUS Ruling BACKFIRE?!?! \| Legal AF |
| 24 | Trump Meltdowns and Collapses | yes | us_politics | 0.0102 | 4108 | 136 | trump spirals, trump loses, speech trump, spirals, meltdown trump, trump meltdown, presser, trump melts, tr... | Trump STUNNED as IT ALL COLLAPSES |
| 8 | Epstein Files Political Connections | yes | us_politics | 0.0102 | 2002 | 196 | epstein files, epsteins, jeffrey epstein, files, epstein, files epstein, jeffrey, gates, connections, break... | The Dark Truth in the Epstein Files the Media WON'T TOUCH |
| 17 | 2026 Midterm Election Predictions | yes | us_politics | 0.0100 | 3465 | 182 | midterm, midterms, midterms democrats, democratic party, republicans, democrats, win midterms, party, 2026 ... | 🚨Stunning New Polls Show Republican SURGE in Midterms \| Dems DOOM in Crisis After Voter Reversal... |
| 49 | Race and Politics in Media | yes | media_culture_war | 0.0098 | 1303 | 156 | white men, black men, roland martin, black america, white people, roland, black americans, black people, bl... | The Argument Black Progressive Leaders Are Too Afraid to Make |
| 11 | Hollywood and Oscars Politics | yes | media_culture_war | 0.0097 | 1837 | 172 | odyssey, hollywood, oscars, movie, film, actors, christopher, sunday 60, grammys, red carpet | 'Idiots': Unpacking Oscars' most 'cringe, woke' nonsense \| Rob Schmitt Tonight |
| 20 | Indian Politics and Parliament | yes | world_politics | 0.0090 | 8886 | 66 | delhi, modi, assembly, singh, pm modi, session, shah, parliament, ram, sir | LIVE: BJP Press Conference by Sudhanshu Trivedi I Nishu Azad Case \| Swatantra Bhardwaj I CJP |
| 224 | Political Media Broadcasters | yes | media_culture_war | 0.0089 | 1834 | 67 | buck sexton, sexton, clay travis, travis, buck, clay, stream, broadcast, abc, christine | LIVE: ABC News Live |
| 95 | Tech Business and Startups | no | tech_business | 0.0086 | 1782 | 139 | mode, build, startup, tech, apple, founder, business, waymo, big tech, silicon | The Bold Plan to Make Tech Serve the Nation—And the Founders Who Are All In \| NYNext |
| 18 | Lindsay Clancy Murder Trial | no | crime_justice | 0.0086 | 2241 | 132 | clancy, lindsay clancy, lindsay, trial, jury, trial day, murder trial, closing arguments, murder, arguments | VERDICT WATCH: Lindsay Clancy Trial |
| 42 | War and Military Analysis | yes | war_conflict | 0.0084 | 2269 | 193 | hoh, matt hoh, col, macgregor, douglas macgregor, col douglas, douglas, world war, col lawrence, lawrence w... | The Truth About War |
| 12 | Canada-US Political Tensions | yes | us_politics | 0.0081 | 1899 | 127 | canada, carney, ezra levant, levant, canadian, canadas, ezra, poilievre, buffalo, carneys | ‘CAN’T SAVE CANADA...’: Mark Carney Faces New REVOLT Amid Trump Tariff War; ‘Only Half The Battle...’ |


Topic share by channel group, top 5 per group (videos; mean of creator shares):


| group | topic_id | label | political | mean_creator_share | raw_pooled_share | n_creators |
|---|---|---|---|---|---|---|
| neutral | 0 | Iran War and Strait of Hormuz Tensions | yes | 0.069 | 0.103 | 38 |
| left | 0 | Iran War and Strait of Hormuz Tensions | yes | 0.065 | 0.094 | 105 |
| left | 2 | Israel-Palestine Conflict Media | yes | 0.046 | 0.033 | 105 |
| neutral | 2 | Israel-Palestine Conflict Media | yes | 0.044 | 0.016 | 38 |
| right | 1 | Shocking Events and Reactions | yes | 0.044 | 0.034 | 96 |
| neutral | 95 | Tech Business and Startups | no | 0.038 | 0.013 | 38 |
| right | 0 | Iran War and Strait of Hormuz Tensions | yes | 0.037 | 0.069 | 96 |
| neutral | 9 | AI and Political Concerns | yes | 0.033 | 0.021 | 38 |
| neutral | 6 | Trump and China political relations | yes | 0.032 | 0.025 | 38 |
| left | 24 | Trump Meltdowns and Collapses | yes | 0.029 | 0.041 | 105 |
| right | 13 | Modern Women and Feminism Debate | yes | 0.027 | 0.013 | 96 |
| left | 3 | ICE Protests and Shootings | yes | 0.024 | 0.023 | 105 |
| left | 1 | Shocking Events and Reactions | yes | 0.022 | 0.015 | 105 |
| right | 22 | Christian Nationalism and Politics | yes | 0.021 | 0.013 | 96 |
| right | 49 | Race and Politics in Media | yes | 0.020 | 0.010 | 96 |


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
| 59 | Iran Conflict and Political Updates | Tom Llamas (186); Top Story (185); Michael Popok (19); Trump (18); Candace Owens (15); Erika Kirk (14); Tuc... | NBC News (185); Trump (85); GOP (18); FBI (13); Bloomberg (12); Candace (11); White House (10); MAGA (10) |
| 3 | ICE Protests and Shootings | Tom Homan (42); Renee Good (42); Trump (39); JD Vance (19); Katie Pavlich (16); Homan (15); Kristi Noem (14... | Trump (214); DHS (84); REUTERS (39); ICE (35); TSA (34); FBI (28); White House (25); NewsNation Live (25) |
| 1 | Shocking Events and Reactions | McEnany (27); Jesse Watters (8); Keane (8); Watters (7); Peter Doocy (6); Gen Keane (5); Ben (4); Turley (4) | INSANE (9); NEVER (7); WTF (7); BRUTAL (4); WoW (3); MTG (3); LEAKED (3); DISGUSTING (3) |
| 4 | Ukraine-Russia War and Political Figures | Putin (1371); Zelensky (450); PUTIN (128); Trump (114); Vladimir Putin (52); Kyiv (51); Firstpost Live (47)... | NATO (347); EU (306); World News (298); Trump (159); CIA (66); Kremlin (66); REUTERS (55); Vantage on First... |
| 40 | Trump's speeches and events | Trump (370); Donald Trump (167); Trump Speaks (74); Trump Delivers Remarks (39); Trump Holds (36); Trump Pa... | White House (178); Trump (130); TRUMP (23); World Economic Forum (23); Oval Office (21); House (17); Cabine... |
| 13 | Modern Women and Feminism Debate | Debra Soh (9); Adam Carolla (4); Dating Apps (4); Bret Weinstein (4); Heather Heying (4); Pearl (4); Graham... | JLP (7); Modern Women (6); Excerpt (5); Global Dating Crisis (3); NHS (3); New York Times (2); Post Show Cl... |
| 22 | Christian Nationalism and Politics | Jesus (70); Charlie Kirk (14); Trump (13); JENNY HOLLAND (12); James Talarico (11); Jesus Christ (11); Chri... | Trump (35); MLB (14); Church (14); JLP (10); HARNWELL (8); GOP (7); Catholic Church (6); MAGA Pastor (5) |
| 6 | Trump and China political relations | Xi (222); Trump (167); Xi Jinping (114); Putin (87); Kim Jong Un (47); Hormuz (40); Donald Trump (39); Jian... | Trump (283); Vantage on Firstpost (71); REUTERS (47); China MoFA (43); World News (32); CCP (30); Firstpost... |
| 98 | JLP Weekly Series | Harris Faulkner (28); Bret Weinstein (7); Heather Heying (7); JLP Thu (7); Arthur Brooks (6); Gad Saad (5);... | JLP (38); Chasing Life (11); Velshi Banned Book Club (8); Excerpt (4); DarkHorse (3); DEI (3); LOT (3); Nex... |
| 9 | AI and Political Concerns | Sam Altman (36); Haslinda Amin (25); Joe Allen (23); Jensen Huang (21); Bernie Sanders (20); OpenAI (20); J... | AI (195); Pentagon (49); OpenAI (36); Vantage on Firstpost (35); Google (32); REUTERS (28); Trump (27); AI ... |
| 7 | Trump vs Maduro Venezuela Conflict | Maduro (365); Trump (166); Nicolas Maduro (69); Nicolás Maduro (48); Donald Trump (23); Maduro Captured (14... | Maduro (345); Trump (265); REUTERS (76); CIA (33); UN (28); White House (26); Congress (26); NewsNation Liv... |
| 5 | Trump Supreme Court Legal Issues | Trump (131); Trump PANICS (25); Lisa Cook (23); Trump STUNNED (22); Trump DOJ (20); Obama (18); Legal AF (1... | Supreme Court (584); Trump (431); Court (52); GOP (42); Fed (40); Justice Department (33); DOJ (27); Congre... |
| 24 | Trump Meltdowns and Collapses | Trump PANICS (155); Trump (109); Donald Trump (60); Trump CRASHES (21); Trump Posts (21); Trump SPIRALS (18... | Trump (532); White House (72); GOP (62); OMG (33); MAGA (18); TRUMP (16); WH (16); Congress (16) |


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


Channel-group medians of topic-controlled scores, videos (non-low-n creators):

| group | n | F1 | F2 | F3 | F4 | F5 | F6 | F7 | F8 | F9 | F10 | F11 | F12 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| left | 105 | 0.13 | -0.08 | -0.31 | -0.13 | 0.14 | -0.25 | -0.53 | -0.19 | -0.27 | -0.44 | -0.30 | -0.11 |
| neutral | 38 | 0.52 | -0.14 | -0.33 | -0.12 | 0.07 | -0.21 | -0.12 | 0.01 | -0.38 | -0.10 | -0.10 | -0.03 |
| right | 96 | 0.19 | 0.12 | -0.28 | -0.09 | 0.22 | -0.24 | -0.67 | -0.17 | -0.28 | -0.45 | -0.11 | -0.20 |


Channel-group medians of topic-controlled scores, streams (non-low-n creators):

| group | n | F1 | F2 | F3 | F4 | F5 | F6 | F7 | F8 | F9 | F10 | F11 | F12 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| left | 33 | -0.16 | -0.41 | -0.24 | -0.21 | -0.28 | 0.61 | -0.37 | -0.01 | -0.45 | -0.54 | 0.12 | -0.06 |
| neutral | 16 | 0.28 | 0.15 | 0.84 | -0.10 | -0.34 | 0.17 | 0.44 | 0.17 | -0.42 | -0.68 | -0.60 | -0.20 |
| right | 30 | 0.16 | -0.37 | -0.26 | -0.10 | -0.28 | 0.02 | -0.59 | -0.02 | -0.42 | -0.44 | 0.18 | -0.12 |


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

| group | n_creators | question | breaking_live | episode_show | interview_guest | reaction | confrontation | listicle | howto_explainer | curiosity_gap | outrage | humor |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| left | 105.00 | 0.16 | 0.03 | 0.03 | 0.10 | 0.03 | 0.08 | 0.00 | 0.08 | 0.03 | 0.64 | 0.00 |
| neutral | 38.00 | 0.16 | 0.01 | 0.07 | 0.12 | 0.02 | 0.07 | 0.00 | 0.07 | 0.02 | 0.36 | 0.00 |
| right | 96.00 | 0.16 | 0.02 | 0.08 | 0.08 | 0.02 | 0.08 | 0.00 | 0.09 | 0.04 | 0.60 | 0.00 |


Share of titles per category, streams (mean of creator shares, non-low-n creators):

| group | n_creators | question | breaking_live | episode_show | interview_guest | reaction | confrontation | listicle | howto_explainer | curiosity_gap | outrage | humor |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| left | 33.00 | 0.11 | 0.17 | 0.06 | 0.18 | 0.01 | 0.15 | 0.00 | 0.03 | 0.02 | 0.63 | 0.00 |
| neutral | 16.00 | 0.05 | 0.52 | 0.02 | 0.13 | 0.01 | 0.07 | 0.00 | 0.01 | 0.02 | 0.30 | 0.00 |
| right | 30.00 | 0.14 | 0.19 | 0.26 | 0.14 | 0.02 | 0.09 | 0.00 | 0.05 | 0.03 | 0.56 | 0.00 |


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

Agglomerative clustering of creators in style space (topic-controlled factor scores, Ward) and topic space (Jensen-Shannon distance between topic mixes, average linkage), k by silhouette; adjusted Rand index against the channel groups and against each other. Run on all titles and on political titles only:


| genre | titles | n_creators | n_groups | style_k | style_silhouette | topic_k | topic_silhouette | ari_style_vs_group | ari_topic_vs_group | ari_style_vs_topic | ari_style_vs_group_k_groups | ari_topic_vs_group_k_groups | ari_style_vs_topic_k_groups |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| videos | all | 239 | 3 | 11 | 0.128 | 3 | 0.144 | 0.036 | 0.010 | 0.003 | -0.003 | 0.010 | -0.009 |
| videos | political | 234 | 3 | 10 | 0.136 | 3 | 0.110 | 0.054 | 0.017 | -0.004 | 0.009 | 0.017 | -0.008 |
| streams | all | 79 | 3 | 9 | 0.159 | 12 | 0.089 | 0.025 | 0.117 | 0.075 | 0.007 | -0.009 | 0.024 |
| streams | political | 77 | 3 | 3 | 0.150 | 3 | 0.088 | -0.006 | 0.008 | 0.143 | -0.006 | 0.008 | 0.143 |


Style cohesion per channel group (mean within-group vs between-group distance in z-scored style space; ratio < 1 = group-mates are closer than average):

| genre | group | n_creators | within_group_distance | between_group_distance | cohesion_ratio |
|---|---|---|---|---|---|
| streams | neutral | 16 | 4.163 | 4.654 | 0.895 |
| streams | left | 33 | 4.483 | 4.667 | 0.961 |
| streams | right | 30 | 5.003 | 4.789 | 1.045 |
| videos | right | 96 | 4.231 | 4.506 | 0.939 |
| videos | neutral | 38 | 4.751 | 4.750 | 1.000 |
| videos | left | 105 | 4.608 | 4.549 | 1.013 |


Where channel group and style disagree (videos, all titles):

| kind | group | n_creators | n_style_clusters | largest_cluster_share | members |
|---|---|---|---|---|---|
| channel group split across style clusters | left | 105 | 10 | 0.286 | https://rumble.com/c/GGreenwald (S0); @LeejaMiller (S0); @TheAtlantic (S0); @ajplus (S0); @MikeFromPA (S0);... |
| channel group split across style clusters | neutral | 38 | 8 | 0.316 | @wsj (S0); @hutch (S0); @KimIversen (S0); @TimesNowWorld (S1); @JacksonHinkleOfficial (S1); @joerogan (S2);... |
| channel group split across style clusters | right | 96 | 8 | 0.375 | @LiberalHivemind (S0); @JillianMichaels (S0); @JustPearlyThings (S0); @StevenCrowder (S0); @MarkDice (S0); ... |
| style cluster spanning channel groups | S6 | 54 | 3 | 0.426 | @BadFaithPodcast (left); @DannyHaiphongYT (left); @DemocracyDocket (left); @DropSiteNews (left); @HasanReac... |
| style cluster spanning channel groups | S1 | 20 | 3 | 0.500 | @DailyDenims (left); @DoubleDownNews (left); @LegalAFMTN (left); @LukeBeasley (left); @MeidasTouch (left); ... |
| style cluster spanning channel groups | S7 | 2 | 2 | 0.500 | @aaronparnas1 (left); @RSBN (right) |
| style cluster spanning channel groups | S0 | 69 | 3 | 0.522 | @BreakThroughNews (left); @EzraKleinShow (left); @GeopoliticalEconomyReport (left); @HasanAbi (left); @Leej... |
| style cluster spanning channel groups | S2 | 51 | 3 | 0.529 | @BadEmpanadaLive (left); @DueDissidence (left); @DylanBurnsLIVE (left); @FarronBalanced (left); @Forthepeop... |
| style cluster spanning channel groups | S9 | 21 | 3 | 0.571 | @CNN (left); @NPR (left); @SkyNews (left); @aljazeeraenglish (left); @msnow (left); @thegrayzone7996 (left)... |
| style cluster spanning channel groups | S4 | 10 | 3 | 0.600 | @DemocracyNow (left); @rolandsmartin (left); @timesofindia (left); @PiersMorganUncensored (neutral); @Blaze... |
| style cluster spanning channel groups | S3 | 4 | 2 | 0.750 | @TheEconomist (left); @moreperfectunion (left); @thewarningwithsteveschmidt (left); @CoreyGilShusterAskProj... |
| style cluster spanning channel groups | S10 | 5 | 2 | 0.800 | @HasanAbiVODs3 (left); @60minutes (neutral); @Firstpost (neutral); @Forbes (neutral); @chinainsights-r2w (n... |


Who gets named (creator-balanced titles; people keyed by surname, so 'Kirk' pools Charlie and Erika Kirk):

| entity | n_titles_balanced | share_of_balanced_titles | n_creators | share_by_group | outrage_share | overall_outrage_share | outrage_ratio |
|---|---|---|---|---|---|---|---|
| Trump | 7619 | 0.041 | 199 | left (5.6%); neutral (3.8%); right (2.3%) | 0.668 | 0.567 | 1.180 |
| Hormuz | 1065 | 0.006 | 86 | neutral (1.0%); left (0.5%); right (0.3%) | 0.515 | 0.567 | 0.910 |
| Hegseth | 1062 | 0.006 | 106 | left (0.8%); neutral (0.7%); right (0.2%) | 0.533 | 0.567 | 0.940 |
| Putin | 992 | 0.005 | 67 | neutral (1.0%); left (0.5%); right (0.1%) | 0.689 | 0.567 | 1.210 |
| Charlie Kirk | 910 | 0.005 | 118 | right (0.9%); neutral (0.4%); left (0.2%) | 0.534 | 0.567 | 0.940 |
| JD Vance | 886 | 0.005 | 120 | left (0.6%); neutral (0.5%); right (0.4%) | 0.568 | 0.567 | 1.000 |
| Mamdani | 765 | 0.004 | 111 | right (0.7%); neutral (0.4%); left (0.2%) | 0.699 | 0.567 | 1.230 |
| Netanyahu | 726 | 0.004 | 113 | neutral (0.5%); left (0.4%); right (0.2%) | 0.696 | 0.567 | 1.230 |
| Epstein | 708 | 0.004 | 114 | left (0.5%); neutral (0.4%); right (0.2%) | 0.720 | 0.567 | 1.270 |
| Lindsey Graham | 628 | 0.003 | 123 | left (0.4%); neutral (0.3%); right (0.3%) | 0.478 | 0.567 | 0.840 |
| Brian Shapiro | 594 | 0.003 | 85 | left (0.6%); right (0.2%); neutral (0.1%) | 0.769 | 0.567 | 1.360 |
| Nancy Guthrie | 550 | 0.003 | 35 | neutral (0.6%); right (0.4%); left (0.0%) | 0.165 | 0.567 | 0.290 |
| Kristi Noem | 543 | 0.003 | 103 | left (0.5%); neutral (0.2%); right (0.2%) | 0.737 | 0.567 | 1.300 |
| Mike Johnson | 538 | 0.003 | 91 | left (0.4%); right (0.2%); neutral (0.2%) | 0.572 | 0.567 | 1.010 |
| Kash Patel | 479 | 0.003 | 89 | left (0.4%); neutral (0.2%); right (0.1%) | 0.766 | 0.567 | 1.350 |
| Karoline Leavitt | 473 | 0.003 | 55 | left (0.3%); right (0.2%); neutral (0.2%) | 0.526 | 0.567 | 0.930 |
| Jack Smith | 449 | 0.002 | 95 | right (0.3%); left (0.2%); neutral (0.2%) | 0.552 | 0.567 | 0.970 |
| Pam Bondi | 447 | 0.002 | 92 | left (0.4%); neutral (0.2%); right (0.1%) | 0.826 | 0.567 | 1.460 |
| Candace Owens | 416 | 0.002 | 71 | right (0.3%); neutral (0.2%); left (0.2%) | 0.743 | 0.567 | 1.310 |
| Keir Starmer | 397 | 0.002 | 43 | left (0.3%); neutral (0.3%); right (0.1%) | 0.471 | 0.567 | 0.830 |
| Hillary Clinton | 396 | 0.002 | 88 | neutral (0.3%); right (0.2%); left (0.2%) | 0.697 | 0.567 | 1.230 |
| Graham Platner | 393 | 0.002 | 102 | left (0.2%); right (0.2%); neutral (0.2%) | 0.588 | 0.567 | 1.040 |
| Lindsay Clancy | 392 | 0.002 | 52 | neutral (0.5%); right (0.2%); left (0.0%) | 0.184 | 0.567 | 0.320 |
| Marco Rubio | 388 | 0.002 | 85 | neutral (0.4%); left (0.1%); right (0.1%) | 0.392 | 0.567 | 0.690 |
| Obama | 345 | 0.002 | 97 | right (0.2%); left (0.2%); neutral (0.1%) | 0.603 | 0.567 | 1.060 |


| entity | n_titles_balanced | share_of_balanced_titles | n_creators | share_by_group | outrage_share | overall_outrage_share | outrage_ratio |
|---|---|---|---|---|---|---|---|
| Trump | 8817 | 0.047 | 193 | left (7.0%); neutral (4.5%); right (1.9%) | 0.667 | 0.567 | 1.180 |
| White House | 1565 | 0.008 | 120 | neutral (1.3%); left (0.7%); right (0.7%) | 0.414 | 0.567 | 0.730 |
| GOP | 1509 | 0.008 | 106 | left (1.1%); right (0.7%); neutral (0.5%) | 0.718 | 0.567 | 1.270 |
| MAGA | 1009 | 0.005 | 123 | left (1.2%); right (0.1%); neutral (0.1%) | 0.926 | 0.567 | 1.630 |
| Senate | 976 | 0.005 | 97 | neutral (0.8%); right (0.4%); left (0.4%) | 0.379 | 0.567 | 0.670 |
| FBI | 885 | 0.005 | 119 | right (0.7%); neutral (0.4%); left (0.3%) | 0.739 | 0.567 | 1.300 |
| Supreme Court | 856 | 0.005 | 107 | neutral (0.5%); left (0.5%); right (0.4%) | 0.522 | 0.567 | 0.920 |
| NATO | 822 | 0.004 | 86 | neutral (0.9%); left (0.3%); right (0.2%) | 0.513 | 0.567 | 0.910 |
| House | 815 | 0.004 | 94 | neutral (0.7%); left (0.3%); right (0.3%) | 0.406 | 0.567 | 0.720 |
| Congress | 773 | 0.004 | 113 | neutral (0.6%); left (0.4%); right (0.3%) | 0.492 | 0.567 | 0.870 |
| CNN | 583 | 0.003 | 95 | right (0.4%); left (0.4%); neutral (0.1%) | 0.798 | 0.567 | 1.410 |
| DHS | 515 | 0.003 | 68 | neutral (0.4%); right (0.3%); left (0.2%) | 0.423 | 0.567 | 0.750 |
| EU | 447 | 0.002 | 41 | neutral (0.6%); left (0.1%); right (0.1%) | 0.443 | 0.567 | 0.780 |
| NASA | 430 | 0.002 | 44 | neutral (0.6%); right (0.1%); left (0.1%) | 0.077 | 0.567 | 0.140 |
| Pentagon | 421 | 0.002 | 73 | neutral (0.4%); left (0.2%); right (0.1%) | 0.428 | 0.567 | 0.750 |
| REUTERS | 402 | 0.002 | 3 | neutral (0.8%) | 0.214 | 0.567 | 0.380 |
| CIA | 375 | 0.002 | 104 | right (0.3%); left (0.2%); neutral (0.2%) | 0.661 | 0.567 | 1.170 |
| World News | 375 | 0.002 | 2 | neutral (0.7%) | 0.765 | 0.567 | 1.350 |
| HasanAbi | 365 | 0.002 | 5 | left (0.5%); right (0.0%) | 0.433 | 0.567 | 0.760 |
| BJP | 342 | 0.002 | 5 | neutral (0.6%); left (0.0%) | 0.295 | 0.567 | 0.520 |
| Fed | 333 | 0.002 | 57 | neutral (0.3%); left (0.1%); right (0.1%) | 0.423 | 0.567 | 0.750 |
| Vantage on Firstpost | 315 | 0.002 | 1 | neutral (0.6%) | 0.463 | 0.567 | 0.820 |
| ABC News Live | 314 | 0.002 | 1 | neutral (0.6%) | 0.010 | 0.567 | 0.020 |
| Fox News | 313 | 0.002 | 60 | left (0.4%); right (0.0%); neutral (0.0%) | 0.917 | 0.567 | 1.620 |
| UN | 289 | 0.002 | 51 | neutral (0.3%); left (0.1%); right (0.0%) | 0.467 | 0.567 | 0.820 |


Convergent formulas: 1,575 distinct titles (case-insensitive) are used verbatim by two or more creators, 474 of them by creators from different organisations (the rest are same-outlet cross-posts such as TYT / The Damage Report); of those 474, 61.8% stay within one channel group. 500 masked templates (names and numbers replaced, at least one content word) are shared across organisations; 45.4% within one channel group.


| example | n_creators | n_titles | groups | creators |
|---|---|---|---|---|
| THIS IS INSANE.. | 12 | 14 | left; neutral; right | @AsmonTV; @BenShapiro; @JackCocchiarellaShow; @JacksonHinkleOfficial; @LukeBeasley; @RedactedNews; @TheMajo... |
| IT HAPPENED AGAIN?? | 7 | 10 | left; right | @HasanAbi; @JackCocchiarellaShow; @LiberalHivemind; @RebelNewsOnline; @TheQuartering; @TimcastNews; @adammo... |
| This changes everything.. | 7 | 7 | left; right | @AsmonTV; @CashJordan; @DestinyDGGClips; @DoubleDownNews; @TheQuartering; @TimcastIRL; https://rumble.com/c... |
| IT'S HAPPENING | 6 | 10 | left; neutral; right | @JacksonHinkleOfficial; @LiberalHivemind; @RebelNewsOnline; @TimcastIRL; @Vaush; @adammockler |
| This Is Disgusting | 6 | 6 | left; right | @AsmonTV; @HasanAbi; @LukeBeasley; @TheMajorityReport; @TheQuartering; @TimcastIRL |
| it’s over. | 5 | 9 | left; neutral; right | @AsmonTV; @HasanAbi; @JacksonHinkleOfficial; @bennyjohnson; @destiny |
| It’s finally happening.. | 5 | 6 | left; right | @AsmonTV; @JackCocchiarellaShow; @RebelNewsOnline; @TimcastIRL; @bennyjohnson |
| Don Lemon ARRESTED! | 5 | 5 | left; right | @BenShapiro; @GlennKirschner2; @TheYoungTurks; @TimcastNews; @marclamonthillnetwork |
| This can't be real.. | 5 | 5 | left; right | @AsmonTV; @RebelNewsOnline; @TimcastIRL; @Vaush; @adammockler |
| This is so embarrassing.. | 5 | 5 | left; right | @AsmonTV; @TheVaushPit; @TheYoungTurks; @destiny; @harryjsisson |
| This is terrifying... | 5 | 5 | left; right | @HasanAbi; @TheMajorityReport; @TheQuartering; @TheVaushPit; @TimcastNews |
| Oh.. my.. god... | 4 | 8 | left; right | @AsmonTV; @HasanAbi; @JackCocchiarellaShow; @TheQuartering |
| It finally happened | 4 | 6 | left | @HasanAbi; @JackCocchiarellaShow; @LukeBeasley; @adammockler |
| BREAKING: TRUMP FIRES PAM BONDI | 4 | 5 | left | @Vaush; @aaronparnas1; @bulwarkmedia; @podsaveamerica |
| HOLY SH*T.. | 4 | 5 | left; neutral; right | @AsmonTV; @HasanAbi; @JacksonHinkleOfficial; @LiberalHivemind |
| THIS IS HILARIOUS | 4 | 5 | left; right | @MikeFromPA; @TheQuartering; @TimcastIRL; @TimcastNews |
| THIS IS REALLY BAD | 4 | 5 | left; right | @HasanAbi; @JackCocchiarellaShow; @bennyjohnson; @harryjsisson |
| He actually did it.. | 4 | 4 | left; right | @AsmonTV; @Timcast; @TimcastNews; @ponderingpolitics |
| It has begun | 4 | 4 | left; right | @HasanAbi; @Timcast; @TimcastIRL; @TimcastNews |
| It’s getting worse… | 4 | 4 | left; right | @TheQuartering; @TimcastIRL; @adammockler; @ponderingpolitics |
| 🚨They Actually Did It… | 4 | 4 | right | @TheQuartering; @TimcastIRL; @TimcastNews; @bennyjohnson |
| THIS COULD CHANGE EVERYTHING | 4 | 4 | right | @RealAmericasVoice; @TimcastIRL; @TimcastNews; https://rumble.com/c/russellbrand |
| THIS IS CRAZY | 4 | 4 | left; right | @HasanAbi; @TheQuartering; @TimcastIRL; @TimcastNews |
| TRUMP JUST LOST IT! | 4 | 4 | left | @FarronBalanced; @JackCocchiarellaShow; @LukeBeasley; @MeidasTouch |
| We need to talk about this.. | 4 | 4 | left; right | @AsmonTV; @TheQuartering; @TheVaushPit; @therationalnational |


| template | n_creators | n_titles | groups | example |
|---|---|---|---|---|
| <ENT> 's <ENT> | 62 | 147 | left; neutral; right | Iran's Plan To Make You SIMP |
| <ENT> after <ENT> | 37 | 73 | left; neutral; right | Trump’s Envoys Get RUDE AWAKENING After Putin Meeting |
| <ENT> 's <ENT> <ENT> | 23 | 40 | left; neutral; right | California's Election Shakeup + Microsoft's AI Spy Badge \| PBD #811 |
| <ENT> ’s <ENT> | 18 | 28 | left; neutral; right | AIPAC’s "Elect Chicago Women" Super PAC Exposed |
| <ENT> exposes <ENT> | 14 | 19 | left; right | Elizabeth Warren Exposes Trump’s Fed Pick In Brutal Hearing |
| <ENT> <ENT> 's <ENT> | 13 | 19 | left; neutral; right | US Media's Hasan Piker Derangement Syndrome Is Ridiculous |
| <ENT> <ENT> after <ENT> | 13 | 15 | left; neutral; right | OMG: Trump RUSHES OFF after Going to HOSPITAL! |
| <ENT> after <ENT> <ENT> | 11 | 16 | left; neutral; right | Hakeem Jeffries In Full Panic Mode After Kushner Meeting Pisses Off Democrats |
| <ENT> vs. <ENT> | 11 | 11 | left; neutral; right | Ben Shapiro vs. Fortnite |
| <ENT> w/ <ENT> | 10 | 38 | left; neutral; right | Biblical Idolatry & The Role of Moses w/ Jordan B. Peterson |
| <ENT> <ENT> w/ <ENT> | 10 | 20 | left; neutral; right | "It Went Completely Viral" Brett Cooper Talks Internet Drama & Pendragon Cycle W/ Michael Knowles |
| <ENT> says <ENT> | 10 | 17 | left; neutral; right | Fox News Lunatic Says Americans Have Data Center Derangement Syndrome |
| <ENT> 's <ENT> in <ENT> | 10 | 13 | left; neutral; right | AOC's DISASTROUS Foreign Policy Debut In Munich |
| <ENT> <ENT> 's <ENT> <ENT> | 9 | 11 | left; neutral; right | Bill Kristol: MAGA's Grievance Culture \| The Bulwark Podcast |
| the truth about <ENT> | 9 | 9 | left; right | The truth about Blizzard |
| <ENT> on <ENT> 's <ENT> | 8 | 10 | left; neutral; right | Aaron Rodgers Torched Fauci on ESPN's Own Air |
| <ENT> on live tv | 7 | 10 | left | Epstein Victim-Smearer Humiliated On Live TV |
| <ENT> destroys <ENT> | 7 | 8 | left; neutral; right | Candace Owens EXPOSES & DESTROYS Ben Shapiro! |
| <ENT> under the bus | 7 | 8 | left | Dems Throw Trans Folks Under The Bus |
| <ENT> is here | 7 | 7 | left; neutral; right | The Radical Left’s Hostile Takeover Is Here |
| <ENT> ft # <ENT> | 6 | 7 | left; neutral; right | Catholic & Protestant Debunk Islam & Atheist Arguments \| ft. Billy Hallowell |
| <ENT> against <ENT> | 6 | 6 | left; neutral; right | Ben Shapiro Lobs WILD Accusation Against Dave Smith |
| <ENT> off on <ENT> | 6 | 6 | left; right | Adam Conover GOES OFF on Tech Companies & A.I. |
| <ENT> senator <ENT> | 6 | 6 | left; neutral; right | Republican Senator SLAMS Trump |
| <ENT> panic as <ENT> | 5 | 14 | left; right | Republicans PANIC as Reporters Fact-Check Them LIVE! |


## Stage 5: time and engagement

Monthly drift, January-September (September is 1-14 and never compared on volume). Channel-group trends with |Spearman| >= 0.6 and p < 0.05 over the nine months (9 of 90 group x genre x measure series):


| group | genre | measure | spearman_trend | p | first_month_value | last_full_month_value |
|---|---|---|---|---|---|---|
| right | videos | F5_controlled | -0.950 | 0.000 | 0.358 | 0.170 |
| left | streams | F11_controlled | -0.867 | 0.003 | 0.145 | -0.094 |
| left | videos | outrage | -0.783 | 0.013 | 0.702 | 0.651 |
| left | streams | curiosity_gap | 0.667 | 0.050 | 0.013 | 0.027 |
| left | streams | F6_controlled | 0.700 | 0.036 | 0.579 | 0.956 |
| neutral | streams | F8_controlled | 0.717 | 0.030 | -0.172 | 0.043 |
| neutral | streams | F5_controlled | 0.833 | 0.005 | -0.406 | -0.178 |
| neutral | streams | F6_controlled | 0.850 | 0.004 | 0.110 | 0.297 |
| neutral | streams | F10_controlled | 0.867 | 0.003 | -0.761 | -0.500 |


Month-to-month topic change (mean Jensen-Shannon distance between a creator's consecutive monthly topic mixes; videos):

| group | 2026-02 | 2026-03 | 2026-04 | 2026-05 | 2026-06 | 2026-07 | 2026-08 | 2026-09 |
|---|---|---|---|---|---|---|---|---|
| left | 0.64 | 0.67 | 0.62 | 0.63 | 0.64 | 0.61 | 0.63 | 0.63 |
| neutral | 0.57 | 0.60 | 0.52 | 0.56 | 0.56 | 0.54 | 0.54 | 0.57 |
| right | 0.70 | 0.71 | 0.67 | 0.68 | 0.68 | 0.68 | 0.68 | 0.67 |


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


The outrage effect by channel group (videos):

| group | n_creators | median_coef_per_sd | q25 | q75 | share_positive | share_sig_positive | share_sig_negative |
|---|---|---|---|---|---|---|---|
| left | 86.000 | 0.037 | -0.001 | 0.082 | 0.744 | 0.209 | 0.023 |
| neutral | 32.000 | 0.070 | 0.022 | 0.103 | 0.781 | 0.406 | 0.000 |
| right | 75.000 | 0.039 | -0.005 | 0.077 | 0.693 | 0.200 | 0.000 |


Hit concentration (creator x genre with >= 100 videos carrying views):

| genre | n_creators | median_gini | median_top10_share | median_top1_share | powerlaw_like | median_alpha |
|---|---|---|---|---|---|---|
| streams | 59 | 0.358 | 0.292 | 0.066 | 0.017 | 2.739 |
| videos | 193 | 0.512 | 0.382 | 0.094 | 0.000 | 2.748 |


Concentration vs style, pooled within channel group (group-demeaned Spearman across creators):

| genre | target | predictor | n_creators | spearman_r | p |
|---|---|---|---|---|---|
| streams | gini | F10_controlled | 59 | -0.077 | 0.562 |
| streams | gini | F11_controlled | 59 | -0.214 | 0.103 |
| streams | gini | F12_controlled | 59 | -0.041 | 0.759 |
| streams | gini | F1_controlled | 59 | 0.368 | 0.004 |
| streams | gini | F2_controlled | 59 | -0.055 | 0.680 |
| streams | gini | F3_controlled | 59 | 0.470 | 0.000 |
| streams | gini | F4_controlled | 59 | -0.015 | 0.909 |
| streams | gini | F5_controlled | 59 | -0.175 | 0.185 |
| streams | gini | F6_controlled | 59 | -0.162 | 0.220 |
| streams | gini | F7_controlled | 59 | 0.228 | 0.082 |
| streams | gini | F8_controlled | 59 | -0.060 | 0.651 |
| streams | gini | F9_controlled | 59 | 0.042 | 0.752 |
| streams | gini | curiosity_gap | 59 | -0.178 | 0.177 |
| streams | gini | humor | 59 | 0.037 | 0.778 |
| streams | gini | log_n_videos | 59 | 0.352 | 0.006 |
| streams | gini | log_subscribers | 59 | 0.368 | 0.004 |
| streams | gini | outrage | 59 | -0.465 | 0.000 |
| streams | top10_share | F10_controlled | 59 | -0.088 | 0.506 |
| streams | top10_share | F11_controlled | 59 | -0.254 | 0.052 |
| streams | top10_share | F12_controlled | 59 | -0.028 | 0.832 |
| streams | top10_share | F1_controlled | 59 | 0.394 | 0.002 |
| streams | top10_share | F2_controlled | 59 | -0.079 | 0.552 |
| streams | top10_share | F3_controlled | 59 | 0.434 | 0.001 |
| streams | top10_share | F4_controlled | 59 | -0.001 | 0.996 |
| streams | top10_share | F5_controlled | 59 | -0.147 | 0.268 |
| streams | top10_share | F6_controlled | 59 | -0.182 | 0.169 |
| streams | top10_share | F7_controlled | 59 | 0.244 | 0.062 |
| streams | top10_share | F8_controlled | 59 | -0.031 | 0.814 |
| streams | top10_share | F9_controlled | 59 | 0.006 | 0.962 |
| streams | top10_share | curiosity_gap | 59 | -0.155 | 0.240 |
| streams | top10_share | humor | 59 | 0.069 | 0.606 |
| streams | top10_share | log_n_videos | 59 | 0.338 | 0.009 |
| streams | top10_share | log_subscribers | 59 | 0.353 | 0.006 |
| streams | top10_share | outrage | 59 | -0.467 | 0.000 |
| videos | gini | F10_controlled | 193 | 0.262 | 0.000 |
| videos | gini | F11_controlled | 193 | 0.185 | 0.010 |
| videos | gini | F12_controlled | 193 | 0.257 | 0.000 |
| videos | gini | F1_controlled | 193 | 0.209 | 0.004 |
| videos | gini | F2_controlled | 193 | 0.059 | 0.412 |
| videos | gini | F3_controlled | 193 | 0.029 | 0.684 |
| videos | gini | F4_controlled | 193 | -0.041 | 0.572 |
| videos | gini | F5_controlled | 193 | 0.246 | 0.001 |
| videos | gini | F6_controlled | 193 | 0.186 | 0.010 |
| videos | gini | F7_controlled | 193 | 0.079 | 0.276 |
| videos | gini | F8_controlled | 193 | 0.195 | 0.006 |
| videos | gini | F9_controlled | 193 | -0.118 | 0.102 |
| videos | gini | curiosity_gap | 193 | -0.159 | 0.027 |
| videos | gini | humor | 193 | -0.027 | 0.706 |
| videos | gini | log_n_videos | 193 | 0.203 | 0.005 |
| videos | gini | log_subscribers | 193 | 0.004 | 0.954 |
| videos | gini | outrage | 193 | -0.436 | 0.000 |
| videos | top10_share | F10_controlled | 193 | 0.263 | 0.000 |
| videos | top10_share | F11_controlled | 193 | 0.186 | 0.010 |
| videos | top10_share | F12_controlled | 193 | 0.225 | 0.002 |
| videos | top10_share | F1_controlled | 193 | 0.224 | 0.002 |
| videos | top10_share | F2_controlled | 193 | 0.059 | 0.418 |
| videos | top10_share | F3_controlled | 193 | -0.002 | 0.976 |
| videos | top10_share | F4_controlled | 193 | -0.068 | 0.350 |
| videos | top10_share | F5_controlled | 193 | 0.230 | 0.001 |
| videos | top10_share | F6_controlled | 193 | 0.176 | 0.015 |
| videos | top10_share | F7_controlled | 193 | 0.078 | 0.282 |
| videos | top10_share | F8_controlled | 193 | 0.179 | 0.013 |
| videos | top10_share | F9_controlled | 193 | -0.126 | 0.082 |
| videos | top10_share | curiosity_gap | 193 | -0.159 | 0.027 |
| videos | top10_share | humor | 193 | -0.019 | 0.792 |
| videos | top10_share | log_n_videos | 193 | 0.179 | 0.013 |
| videos | top10_share | log_subscribers | 193 | -0.026 | 0.723 |
| videos | top10_share | outrage | 193 | -0.428 | 0.000 |


## Stage 6b: Zipf's law and views over time (document 7)

Zipf exponents per system (tokens with stopwords; OLS of log frequency on log rank; size-matched = 20 draws of 2,000 titles, top 200 ranks):

| grouping | system | n_titles | n_tokens | n_types | tokens_per_title | zipf_top100 | zipf_top1000 | zipf_top5000 | zipf_r2_top1000 | zipf_size_matched | zipf_size_matched_sd | top1_share | top_10 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| corpus | all edited uploads (balanced) | 155636 | 1612982 | 48959 | 10.3600 | 0.8592 | 0.7847 | 1.0143 | 0.9954 | 0.8129 | 0.0097 | 0.0245 | the trump to in on of s is iran and |
| channel_group | left | 64947 | 618335 | 26834 | 9.5200 | 0.8572 | 0.8244 | 1.0867 | 0.9963 | 0.8180 | 0.0083 | 0.0383 | trump the to in as on s is of iran |
| channel_group | neutral | 39161 | 442699 | 28903 | 11.3000 | 0.8481 | 0.7922 | 1.0063 | 0.9945 | 0.8009 | 0.0108 | 0.0197 | in to the of trump on iran s for us |
| channel_group | right | 51528 | 551948 | 27779 | 10.7100 | 0.8282 | 0.7863 | 1.0233 | 0.9959 | 0.7865 | 0.0079 | 0.0336 | the to in is of trump on and a s |
| title_label | left | 3031 | 29617 | 6005 | 9.7700 | 0.8587 | 0.8180 | 0.9967 | 0.9954 | 0.8471 | 0.0070 | 0.0380 | trump the to is s in on of and as |
| title_label | right | 2550 | 26617 | 6104 | 10.4400 | 0.7689 | 0.7750 | 0.9654 | 0.9960 | 0.7730 | 0.0037 | 0.0408 | the to is on trump in of and for s |
| title_label | neither | 6881 | 62974 | 11081 | 9.1500 | 0.8643 | 0.8113 | 0.9644 | 0.9964 | 0.8147 | 0.0058 | 0.0404 | the to in is of a on s and trump |
| caps_style | all_caps | 4163 | 25992 | 4936 | 6.2400 | 0.7642 | 0.8745 | 0.9904 | 0.9940 | 0.7951 | 0.0081 | 0.0247 | the is trump this to it in they iran s |
| caps_style | selective_caps | 56805 | 592182 | 26654 | 10.4200 | 0.8079 | 0.7939 | 1.0675 | 0.9966 | 0.7823 | 0.0079 | 0.0321 | trump the to in as on s is of iran |
| caps_style | title_case | 52644 | 543500 | 30226 | 10.3200 | 0.8517 | 0.7950 | 1.0153 | 0.9959 | 0.8243 | 0.0079 | 0.0341 | the trump to s in on of is and a |
| caps_style | sentence_case | 38729 | 431875 | 28270 | 11.1500 | 0.8634 | 0.7959 | 1.0123 | 0.9952 | 0.8117 | 0.0082 | 0.0218 | to in the of trump on iran and for s |
| caps_style | mixed_other | 1334 | 14193 | 4133 | 10.6400 | 0.8308 | 0.8321 | 0.8167 | 0.9879 |  |  | 0.0237 | in a the to s i of u this is |
| caps_style | short_other | 1961 | 5240 | 1123 | 2.6700 | 1.2563 | 0.8266 | 0.7757 | 0.8644 |  |  | 0.1168 | tyt hour episode 1 2 bonus 26 full hasanabi 2026 |


Creator-level Zipf / Heaps and the views rank-size slopes per channel group and per dominant capitalisation style:

| grouping | group | n_creators | zipf_words_top200_mean | zipf_words_top200_median | n_creators_1500 | zipf_words_1500_mean | heaps_beta_1500_mean | top1_word_share_mean | n_creators_with_views | zipf_views_all_median | zipf_views_head_median | gini_median | top10_share_median | powerlaw_like_share | caps_any_mean |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| channel_group | left | 105 | 0.797 | 0.791 | 72 | 0.724 | 0.810 | 0.050 | 86 | 0.876 | 0.425 | 0.494 | 0.373 | 0.000 | 0.375 |
| channel_group | neutral | 38 | 0.789 | 0.809 | 25 | 0.712 | 0.843 | 0.043 | 32 | 1.244 | 0.603 | 0.670 | 0.538 | 0.000 | 0.181 |
| channel_group | right | 96 | 0.750 | 0.757 | 67 | 0.690 | 0.827 | 0.046 | 75 | 0.898 | 0.419 | 0.495 | 0.361 | 0.000 | 0.403 |
| dominant_caps_style | all_caps | 7 | 0.735 | 0.740 | 5 | 0.692 | 0.814 | 0.036 | 5 | 0.583 | 0.312 | 0.347 | 0.263 | 0.000 | 0.774 |
| dominant_caps_style | selective_caps | 74 | 0.784 | 0.791 | 63 | 0.701 | 0.809 | 0.046 | 64 | 0.797 | 0.383 | 0.459 | 0.346 | 0.000 | 0.748 |
| dominant_caps_style | title_case | 126 | 0.763 | 0.761 | 75 | 0.713 | 0.828 | 0.050 | 97 | 0.951 | 0.468 | 0.536 | 0.404 | 0.000 | 0.173 |
| dominant_caps_style | sentence_case | 30 | 0.830 | 0.835 | 21 | 0.718 | 0.843 | 0.042 | 25 | 1.236 | 0.634 | 0.681 | 0.557 | 0.000 | 0.070 |


Views by publication month (edited uploads, YouTube, unique titles): median views, the median over channels of the channel's median, and log views relative to the same channel's mean that month:

| grouping | group | month | n_videos | n_creators | median_views | creator_median_views | mean_log_views | relative_log_views | relative_log_views_se |
|---|---|---|---|---|---|---|---|---|---|
| channel_group | left | 2026-01 | 8344 | 102 | 59000.000 | 55500.000 | 10.845 | 0.000 | 0.012 |
| channel_group | left | 2026-02 | 9528 | 101 | 59000.000 | 59000.000 | 10.831 | -0.000 | 0.011 |
| channel_group | left | 2026-03 | 8713 | 100 | 69000.000 | 59000.000 | 10.949 | 0.000 | 0.012 |
| channel_group | left | 2026-04 | 9805 | 102 | 71000.000 | 54750.000 | 11.032 | -0.000 | 0.011 |
| channel_group | left | 2026-05 | 9327 | 103 | 47000.000 | 41000.000 | 10.628 | 0.000 | 0.011 |
| channel_group | left | 2026-06 | 9285 | 104 | 41000.000 | 40500.000 | 10.491 | 0.000 | 0.011 |
| channel_group | left | 2026-07 | 9235 | 103 | 43000.000 | 47000.000 | 10.505 | -0.000 | 0.012 |
| channel_group | left | 2026-08 | 12492 | 104 | 44000.000 | 45500.000 | 10.557 | -0.000 | 0.010 |
| channel_group | left | 2026-09 | 6461 | 101 | 70000.000 | 79000.000 | 11.022 | 0.000 | 0.013 |
| channel_group | left | all | 83190 | 104 | 54000.000 | 49500.000 | 10.745 | 0.000 | 0.004 |
| channel_group | neutral | 2026-01 | 9577 | 36 | 9700.000 | 15000.000 | 9.274 | -0.000 | 0.015 |
| channel_group | neutral | 2026-02 | 11510 | 36 | 9900.000 | 19500.000 | 9.296 | -0.000 | 0.014 |
| channel_group | neutral | 2026-03 | 10728 | 35 | 11000.000 | 23000.000 | 9.434 | 0.000 | 0.015 |
| channel_group | neutral | 2026-04 | 11245 | 36 | 9900.000 | 14250.000 | 9.349 | 0.000 | 0.014 |
| channel_group | neutral | 2026-05 | 11060 | 36 | 7700.000 | 13500.000 | 9.085 | -0.000 | 0.014 |
| channel_group | neutral | 2026-06 | 11249 | 36 | 7600.000 | 14175.000 | 9.022 | -0.000 | 0.013 |
| channel_group | neutral | 2026-07 | 10836 | 36 | 6800.000 | 18500.000 | 8.943 | 0.000 | 0.014 |
| channel_group | neutral | 2026-08 | 14402 | 36 | 7200.000 | 19500.000 | 8.967 | -0.000 | 0.011 |
| channel_group | neutral | 2026-09 | 7714 | 37 | 11000.000 | 25000.000 | 9.529 | -0.000 | 0.015 |
| channel_group | neutral | all | 98321 | 38 | 8800.000 | 20000.000 | 9.191 | -0.000 | 0.005 |
| channel_group | right | 2026-01 | 6259 | 88 | 32000.000 | 26500.000 | 10.111 | -0.000 | 0.014 |
| channel_group | right | 2026-02 | 7323 | 90 | 32000.000 | 28500.000 | 10.098 | 0.000 | 0.013 |
| channel_group | right | 2026-03 | 6908 | 90 | 32000.000 | 29000.000 | 10.075 | -0.000 | 0.014 |
| channel_group | right | 2026-04 | 7092 | 90 | 35000.000 | 35500.000 | 10.194 | 0.000 | 0.013 |
| channel_group | right | 2026-05 | 6905 | 92 | 33000.000 | 22000.000 | 10.254 | 0.000 | 0.013 |
| channel_group | right | 2026-06 | 6913 | 92 | 28000.000 | 20500.000 | 10.115 | 0.000 | 0.014 |
| channel_group | right | 2026-07 | 6449 | 92 | 28000.000 | 17250.000 | 10.137 | -0.000 | 0.014 |
| channel_group | right | 2026-08 | 9011 | 92 | 28000.000 | 19250.000 | 10.155 | 0.000 | 0.012 |
| channel_group | right | 2026-09 | 4769 | 90 | 44000.000 | 39500.000 | 10.602 | -0.000 | 0.016 |
| channel_group | right | all | 61629 | 92 | 32000.000 | 20500.000 | 10.178 | 0.000 | 0.004 |
| title_label | left | 2026-01 | 319 | 120 | 57000.000 | 52750.000 | 10.814 | 0.035 | 0.054 |
| title_label | left | 2026-02 | 357 | 129 | 60000.000 | 64000.000 | 10.749 | -0.047 | 0.047 |
| title_label | left | 2026-03 | 338 | 123 | 67000.000 | 54000.000 | 10.814 | 0.031 | 0.048 |
| title_label | left | 2026-04 | 316 | 125 | 51000.000 | 55000.000 | 10.563 | -0.084 | 0.052 |
| title_label | left | 2026-05 | 340 | 125 | 39500.000 | 36000.000 | 10.367 | -0.018 | 0.048 |
| title_label | left | 2026-06 | 358 | 130 | 54000.000 | 50750.000 | 10.550 | 0.063 | 0.048 |
| title_label | left | 2026-07 | 311 | 120 | 43000.000 | 47000.000 | 10.470 | 0.056 | 0.056 |
| title_label | left | 2026-08 | 295 | 127 | 49000.000 | 47350.000 | 10.496 | 0.014 | 0.050 |
| title_label | left | 2026-09 | 246 | 106 | 86500.000 | 87000.000 | 11.182 | 0.041 | 0.051 |
| title_label | left | all | 2880 | 214 | 55000.000 | 43500.000 | 10.654 | 0.009 | 0.017 |
| title_label | right | 2026-01 | 276 | 108 | 40500.000 | 33775.000 | 10.444 | 0.050 | 0.054 |
| title_label | right | 2026-02 | 290 | 112 | 27000.000 | 33250.000 | 10.230 | -0.024 | 0.050 |
| title_label | right | 2026-03 | 274 | 109 | 26500.000 | 37000.000 | 10.159 | -0.021 | 0.056 |
| title_label | right | 2026-04 | 275 | 106 | 45000.000 | 44500.000 | 10.464 | 0.131 | 0.055 |
| title_label | right | 2026-05 | 279 | 116 | 30000.000 | 41750.000 | 10.302 | -0.001 | 0.051 |
| title_label | right | 2026-06 | 301 | 110 | 29000.000 | 32500.000 | 10.192 | 0.110 | 0.049 |
| title_label | right | 2026-07 | 262 | 109 | 26500.000 | 30000.000 | 10.196 | 0.018 | 0.058 |
| title_label | right | 2026-08 | 291 | 114 | 29000.000 | 25500.000 | 10.297 | 0.019 | 0.051 |
| title_label | right | 2026-09 | 184 | 92 | 54500.000 | 48750.000 | 10.785 | 0.064 | 0.068 |
| title_label | right | all | 2432 | 190 | 32000.000 | 37000.000 | 10.323 | 0.038 | 0.018 |
| title_label | neither | 2026-01 | 684 | 217 | 28000.000 | 37000.000 | 10.209 | 0.005 | 0.039 |
| title_label | neither | 2026-02 | 721 | 225 | 38000.000 | 49400.000 | 10.294 | 0.009 | 0.040 |
| title_label | neither | 2026-03 | 718 | 228 | 42500.000 | 45500.000 | 10.387 | 0.011 | 0.039 |
| title_label | neither | 2026-04 | 745 | 232 | 29000.000 | 36500.000 | 10.235 | -0.023 | 0.039 |
| title_label | neither | 2026-05 | 807 | 237 | 31000.000 | 35000.000 | 10.332 | 0.053 | 0.038 |
| title_label | neither | 2026-06 | 738 | 227 | 21000.000 | 24000.000 | 9.930 | -0.091 | 0.036 |
| title_label | neither | 2026-07 | 760 | 221 | 25000.000 | 28000.000 | 9.969 | -0.080 | 0.038 |
| title_label | neither | 2026-08 | 728 | 227 | 28500.000 | 37000.000 | 10.146 | 0.028 | 0.038 |
| title_label | neither | 2026-09 | 577 | 211 | 39000.000 | 41000.000 | 10.521 | -0.065 | 0.039 |
| title_label | neither | all | 6478 | 267 | 30000.000 | 34000.000 | 10.217 | -0.016 | 0.013 |
| caps_style | all_caps | 2026-01 | 284 | 33 | 97500.000 | 100000.000 | 10.268 | 0.101 | 0.052 |
| caps_style | all_caps | 2026-02 | 411 | 38 | 113000.000 | 62500.000 | 10.749 | 0.029 | 0.042 |
| caps_style | all_caps | 2026-03 | 366 | 41 | 101000.000 | 114500.000 | 11.201 | 0.030 | 0.037 |
| caps_style | all_caps | 2026-04 | 598 | 39 | 36500.000 | 70000.000 | 9.227 | 0.025 | 0.039 |
| caps_style | all_caps | 2026-05 | 429 | 33 | 62000.000 | 90000.000 | 10.081 | 0.045 | 0.048 |
| caps_style | all_caps | 2026-06 | 412 | 34 | 43000.000 | 78750.000 | 9.928 | 0.038 | 0.048 |
| caps_style | all_caps | 2026-07 | 329 | 34 | 87000.000 | 86500.000 | 11.039 | 0.079 | 0.037 |
| caps_style | all_caps | 2026-08 | 473 | 34 | 76000.000 | 82000.000 | 10.937 | 0.020 | 0.028 |
| caps_style | all_caps | 2026-09 | 192 | 30 | 153500.000 | 114000.000 | 11.471 | 0.017 | 0.050 |
| caps_style | all_caps | all | 3494 | 76 | 76000.000 | 51000.000 | 10.410 | 0.040 | 0.014 |
| caps_style | selective_caps | 2026-01 | 7631 | 181 | 54000.000 | 41000.000 | 10.651 | 0.053 | 0.012 |
| caps_style | selective_caps | 2026-02 | 8660 | 192 | 54000.000 | 49000.000 | 10.640 | 0.047 | 0.011 |
| caps_style | selective_caps | 2026-03 | 7934 | 184 | 61000.000 | 44750.000 | 10.713 | 0.084 | 0.013 |
| caps_style | selective_caps | 2026-04 | 8930 | 195 | 56000.000 | 45800.000 | 10.734 | 0.059 | 0.011 |
| caps_style | selective_caps | 2026-05 | 8777 | 194 | 44000.000 | 33250.000 | 10.529 | 0.058 | 0.012 |
| caps_style | selective_caps | 2026-06 | 8845 | 197 | 39000.000 | 32000.000 | 10.353 | 0.055 | 0.012 |
| caps_style | selective_caps | 2026-07 | 8448 | 191 | 37000.000 | 33000.000 | 10.292 | 0.025 | 0.012 |
| caps_style | selective_caps | 2026-08 | 11997 | 207 | 39000.000 | 33000.000 | 10.327 | 0.042 | 0.010 |
| caps_style | selective_caps | 2026-09 | 6305 | 177 | 60000.000 | 59000.000 | 10.755 | 0.054 | 0.013 |
| caps_style | selective_caps | all | 77527 | 244 | 48000.000 | 37000.000 | 10.537 | 0.052 | 0.004 |
| caps_style | title_case | 2026-01 | 6841 | 224 | 19000.000 | 39000.000 | 9.760 | -0.017 | 0.016 |
| caps_style | title_case | 2026-02 | 8201 | 227 | 18000.000 | 40000.000 | 9.704 | -0.028 | 0.014 |
| caps_style | title_case | 2026-03 | 7764 | 226 | 18000.000 | 38750.000 | 9.699 | -0.055 | 0.015 |
| caps_style | title_case | 2026-04 | 7891 | 234 | 20000.000 | 36500.000 | 9.904 | -0.039 | 0.015 |
| caps_style | title_case | 2026-05 | 8150 | 230 | 15000.000 | 33250.000 | 9.656 | -0.023 | 0.014 |
| caps_style | title_case | 2026-06 | 8634 | 230 | 12000.000 | 28750.000 | 9.511 | -0.032 | 0.014 |
| caps_style | title_case | 2026-07 | 8460 | 233 | 12000.000 | 27000.000 | 9.514 | -0.001 | 0.014 |
| caps_style | title_case | 2026-08 | 11403 | 240 | 12000.000 | 28000.000 | 9.537 | -0.018 | 0.011 |
| caps_style | title_case | 2026-09 | 5998 | 218 | 23000.000 | 52500.000 | 10.082 | -0.020 | 0.016 |
| caps_style | title_case | all | 73342 | 259 | 16000.000 | 34500.000 | 9.685 | -0.026 | 0.005 |
| caps_style | sentence_case | 2026-01 | 9135 | 92 | 16000.000 | 23500.000 | 9.723 | -0.037 | 0.014 |
| caps_style | sentence_case | 2026-02 | 10856 | 91 | 16000.000 | 35000.000 | 9.726 | -0.022 | 0.013 |
| caps_style | sentence_case | 2026-03 | 10013 | 89 | 19000.000 | 29000.000 | 9.893 | -0.027 | 0.014 |
| caps_style | sentence_case | 2026-04 | 10408 | 100 | 18000.000 | 40750.000 | 9.882 | -0.022 | 0.014 |
| caps_style | sentence_case | 2026-05 | 9669 | 93 | 13000.000 | 23500.000 | 9.554 | -0.041 | 0.014 |
| caps_style | sentence_case | 2026-06 | 9215 | 92 | 12000.000 | 25500.000 | 9.512 | -0.029 | 0.014 |
| caps_style | sentence_case | 2026-07 | 8976 | 90 | 12000.000 | 27750.000 | 9.498 | -0.029 | 0.014 |
| caps_style | sentence_case | 2026-08 | 11662 | 98 | 12000.000 | 27000.000 | 9.534 | -0.033 | 0.012 |
| caps_style | sentence_case | 2026-09 | 6230 | 85 | 19000.000 | 62000.000 | 10.056 | -0.035 | 0.017 |
| caps_style | sentence_case | all | 86164 | 181 | 15000.000 | 26000.000 | 9.696 | -0.030 | 0.005 |
| caps_style | mixed_other | 2026-01 | 271 | 29 | 23000.000 | 28000.000 | 10.030 | 0.031 | 0.084 |
| caps_style | mixed_other | 2026-02 | 245 | 43 | 40000.000 | 37000.000 | 10.292 | 0.157 | 0.091 |
| caps_style | mixed_other | 2026-03 | 274 | 42 | 30000.000 | 30500.000 | 10.252 | -0.008 | 0.082 |
| caps_style | mixed_other | 2026-04 | 322 | 49 | 42500.000 | 36500.000 | 10.363 | -0.065 | 0.065 |
| caps_style | mixed_other | 2026-05 | 273 | 36 | 22000.000 | 22250.000 | 9.887 | 0.010 | 0.080 |
| caps_style | mixed_other | 2026-06 | 320 | 47 | 23500.000 | 29000.000 | 10.020 | 0.035 | 0.074 |
| caps_style | mixed_other | 2026-07 | 296 | 49 | 23000.000 | 19500.000 | 9.953 | 0.008 | 0.074 |
| caps_style | mixed_other | 2026-08 | 359 | 52 | 23000.000 | 36500.000 | 9.944 | 0.107 | 0.066 |
| caps_style | mixed_other | 2026-09 | 226 | 33 | 25500.000 | 39000.000 | 10.139 | -0.052 | 0.098 |
| caps_style | mixed_other | all | 2586 | 108 | 26500.000 | 33250.000 | 10.092 | 0.026 | 0.026 |
| caps_style | short_other | 2026-01 | 101 | 32 | 31000.000 | 56500.000 | 10.443 | 0.134 | 0.098 |
| caps_style | short_other | 2026-02 | 101 | 32 | 88000.000 | 107250.000 | 11.127 | 0.157 | 0.082 |
| caps_style | short_other | 2026-03 | 97 | 28 | 78000.000 | 101775.000 | 11.196 | 0.266 | 0.083 |
| caps_style | short_other | 2026-04 | 103 | 31 | 64000.000 | 85500.000 | 10.758 | 0.149 | 0.092 |
| caps_style | short_other | 2026-05 | 102 | 30 | 94500.000 | 112000.000 | 11.267 | 0.458 | 0.075 |
| caps_style | short_other | 2026-06 | 130 | 23 | 55500.000 | 60000.000 | 10.602 | 0.230 | 0.064 |
| caps_style | short_other | 2026-07 | 111 | 22 | 24000.000 | 88500.000 | 10.107 | 0.182 | 0.074 |
| caps_style | short_other | 2026-08 | 157 | 34 | 25000.000 | 48750.000 | 10.248 | 0.238 | 0.063 |
| caps_style | short_other | 2026-09 | 64 | 23 | 25500.000 | 88000.000 | 10.564 | 0.066 | 0.090 |
| caps_style | short_other | all | 966 | 75 | 44000.000 | 47500.000 | 10.670 | 0.216 | 0.026 |
| all | all channels | 2026-01 | 24180 | 226 | 25000.000 | 34000.000 | 10.033 |  |  |
| all | all channels | 2026-02 | 28361 | 227 | 25000.000 | 43000.000 | 10.019 |  |  |
| all | all channels | 2026-03 | 26349 | 225 | 27000.000 | 39000.000 | 10.103 |  |  |
| all | all channels | 2026-04 | 28142 | 228 | 28000.000 | 42000.000 | 10.148 |  |  |
| all | all channels | 2026-05 | 27292 | 231 | 21000.000 | 33000.000 | 9.908 |  |  |
| all | all channels | 2026-06 | 27447 | 232 | 18000.000 | 28750.000 | 9.794 |  |  |
| all | all channels | 2026-07 | 26520 | 231 | 18000.000 | 29000.000 | 9.777 |  |  |
| all | all channels | 2026-08 | 35905 | 232 | 18000.000 | 28750.000 | 9.818 |  |  |
| all | all channels | 2026-09 | 18944 | 228 | 30000.000 | 52000.000 | 10.308 |  |  |


Capitalisation style by channel group and by title label:

| grouping | group | n_titles | all_caps | selective_caps | title_case | sentence_case | mixed_other | short_other | caps_any |
|---|---|---|---|---|---|---|---|---|---|
| channel_group | left | 64947 | 0.020 | 0.461 | 0.318 | 0.173 | 0.008 | 0.020 | 0.481 |
| channel_group | neutral | 39161 | 0.008 | 0.157 | 0.272 | 0.541 | 0.015 | 0.007 | 0.165 |
| channel_group | right | 51528 | 0.049 | 0.403 | 0.414 | 0.122 | 0.005 | 0.007 | 0.452 |
| title_label | left | 3031 | 0.013 | 0.448 | 0.457 | 0.076 | 0.004 | 0.002 | 0.461 |
| title_label | right | 2550 | 0.023 | 0.455 | 0.473 | 0.044 | 0.002 | 0.003 | 0.478 |
| title_label | neither | 6881 | 0.034 | 0.214 | 0.528 | 0.189 | 0.009 | 0.026 | 0.248 |


Title label x capitalisation style (label shares within each style; relative log views per cell):

| caps_style | n_titles | share_left | share_right | share_neither | relative_log_views_left | n_left | relative_log_views_right | n_right | relative_log_views_neither | n_neither |
|---|---|---|---|---|---|---|---|---|---|---|
| all_caps | 332 | 0.115 | 0.175 | 0.711 | -0.010 | 32 | 0.069 | 49 | -0.004 | 185 |
| selective_caps | 3988 | 0.341 | 0.291 | 0.369 | 0.006 | 1296 | 0.066 | 1096 | 0.033 | 1397 |
| title_case | 6227 | 0.223 | 0.194 | 0.584 | 0.002 | 1303 | 0.006 | 1168 | -0.038 | 3422 |
| sentence_case | 1643 | 0.141 | 0.068 | 0.791 | 0.069 | 232 | 0.118 | 105 | -0.026 | 1268 |
| mixed_other | 80 | 0.138 | 0.075 | 0.787 |  | 11 |  | 6 | -0.132 | 62 |
| short_other | 192 | 0.031 | 0.042 | 0.927 |  | 6 |  | 8 | 0.174 | 144 |


## Files

Machine-readable interface tables: `features.csv`, `dimensions.csv`, `topics.csv`, `labels.csv`, `creators.csv`, `leaning_by_creator.csv` (all under `data/titles/analysis/`). Profile cards: `pipeline_titles/reports/cards/`. HTML: `pipeline_titles/reports/title_stylometry.html`. Methods: `methods_appendix.md`.
