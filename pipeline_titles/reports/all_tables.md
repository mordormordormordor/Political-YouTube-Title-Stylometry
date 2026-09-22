# Title Stylometry: all tables (reference dump), 2026-01-01 to 2026-09-14

_Generated 2026-09-22T14:35:37+00:00 by `python -m pipeline_titles.report`. Every table below is read from `data/titles/analysis/`; the code is `pipeline_titles/`._

Corpus: 293,590 titles from 274 creators (284,906 unique within creator x genre; 243,563 edited uploads, 50,027 live-stream VODs; 5,783 on Rumble). Genres are never pooled; a creator x genre with fewer than 50 unique titles is low-n and never ranked.

## Headline findings

_One plain-language finding per stage, written from the tables below (2026-09-14 run; channel groups from the 2026-09-15 leaning run, regrouped 2026-09-17). Re-check after a corpus refresh._

- **Stage 0, corpus.** The corpus is 309,596 titles from 274 creators, but four Indian news channels hold a fifth of it and 3.0 % of rows are verbatim live-loop repeats, so every corpus figure here is a mean of creator-level values or comes from the 189,240-title balanced subset. Brand stripping changed 34,394 titles; the creator-level Zipf exponent fell from 0.799 to 0.782 and the top-token share dropped most for show-branded channels (Rogan, Denims, Economist), which is the expected signature of removing the show-name head. No channel is categorized by hand: the one grouping of channels used anywhere in the report is the left / neutral / right channel group of the leaning stage (122 / 42 / 110 channels), which is how each channel's own titles read to a frontier model.
- **Stage 1, topics.** 236 topics; the Iran war / Strait of Hormuz story alone is 27,609 unique titles across 227 creators, and eleven of the twelve largest topics are shared by 100+ creators each. Topic mix does not separate the channel groups (adjusted Rand index 0.010 for videos): in 2026 the whole landscape covered the same stories, which is exactly why style had to be measured within topic. 212 of 236 topics are political; the non-political mass (crime trials, weather, sport, tech) sits with the neutral channels, the news outlets (mean political share 0.87 vs 0.95 for the left group and 0.92 for the right).
- **Stage 2, style dimensions.** Twelve factors survive (parallel analysis suggested 16; 47 % of variance). The candidate labels do not hold up: Sensational, Critical and Analytical all collapse onto one tone factor (F1, positive tone vs outrage; creator-level r with the LLM ratings -0.71, -0.49, +0.43), Educational maps only partially onto the question/explainer factor (F5, r 0.39), and Conversational (r 0.18) and Humor (r 0.08; the LLM flagged 0.4 % of titles) do not appear. The other factors are structural: clause vs noun-phrase headlines, LIVE/BREAKING labeling, stream talk (chat, ellipsis), person-centred titles, news prose vs title case, numbers, ALL CAPS, quotes. Topic accounts for 5-18 % of title-level score variance, and creator scores barely move when controlled (raw vs controlled r 0.80-0.98): style is a channel trait, not a story trait. The LLM rater's test-retest weighted kappa is 0.74 for sensational but only 0.25 for educational, so the validation is trustworthy for tone and weak for the rest. The model's loadings, validation and topic control are in the methods appendix and all_tables.md.
- **Stage 3, formats and hooks.** The outrage frame is the landscape's default hook: the LLM flagged 57 % of sampled titles, the classifier reproduces it well (hold-out AUC 0.84), and it covers 64 % of the average left channel's edited uploads, 60 % of the average right channel's and 36 % of the average neutral channel's, with a wide spread of channels inside every group. Curiosity-gap (2 %) and humor (0.4 %) were flagged too rarely to learn (hold-out F1 0.18 and 0.00): treat both as unmeasured, not absent. Question titles run at 16 % in all three groups; none of the structural formats separates the groups the way the outrage hook does.
- **Stage 4, landscape.** The channel groups predict style almost not at all: style clusters vs groups ARI 0.036 (videos, all titles) and 0.054 (political titles only); no group coheres in style space (cohesion ratios 1.01, 1.00 and 0.94 for left, neutral and right), and the largest style cluster holds 69 creators from all three groups. So the useful units are the style neighbors on each card, not the groups. Of 1,575 titles used verbatim by two or more creators, 474 cross organizations (the rest are TYT/Damage Report-type cross-posts) and 38 % of those are used in more than one channel group (a random pair of channels shares a group 38 % of the time, so verbatim sharing runs a little more within the camps than chance, the masked templates across them): "THIS IS INSANE.." is used by 12 creators across all three groups, "IT HAPPENED AGAIN??" by 7, and the shared templates are outrage frames ("<ENT> exposes <ENT>", "<ENT> destroys <ENT>", "<ENT> under the bus"). Trump is named in 3-5 % of balanced titles by 199 creators, most by the left group; the entities that carry the most outrage framing relative to baseline are MAGA (1.6x), Pam Bondi (1.5x), Kash Patel and Candace Owens (1.3x), the least are the crime-story names (Nancy Guthrie 0.3x, Lindsay Clancy 0.3x).
- **Stage 5, time and engagement.** Drift is small: 9 of 90 group-month series show a monotone trend; the left group's outrage share eased from 70 % to 65 % over the year and the right group's question framing fell, while the corpus mean stayed flat. Within creator, the outrage frame is the only title feature that predicts views with a consistent sign in the topic-controlled regression (median +0.04 log views per SD; positive for 73 % of 193 video channels, significant-positive for 24 %, significant-negative for 1 %); every dimension score and length has a median effect at or below 0.03 with 50-70 % sign agreement, which is a null result. Views are concentrated (median Gini 0.51; the top 10 % of a channel's videos take 38 % of its views) but not power-law: the Clauset-Shalizi-Newman test never significantly prefers the power law (0 of 193 video channels; the lognormal wins significantly in 79, the rest are inconclusive); within groups, concentration falls with the outrage share (rho -0.44), and every other correlate (quoted speech, modal / future wording, question framing, tone, the number of videos) is weak (|rho| <= 0.26).
- **Stage 6b, Zipf's law and views over time.** Title vocabulary is Zipfian with a flat head (exponent 0.86 over the top 100 words, 0.78 over the top 1,000, 1.01 over the top 5,000; R² 0.995). The three cuts move the words more than the curve: the left group (size-matched exponent 0.82) and the left-read titles (0.85) are the most concentrated systems, with "trump" ahead of "the"; the right-read titles are the flattest (0.77); ALL-CAPS titles are 6 tokens long against 11 for sentence case, with "this", "it" and "they" among their ten most frequent words. Views within a channel are not Zipfian (lognormal tails), and the neutral group is the hit-driven one (median Gini 0.67 vs 0.49 for left and right). Over the months the median left channel draws one and a half to two and a half times the views per video of the median right or neutral channel. Against each channel's own monthly baseline, capitals earn views in every month of the year (ALL CAPS +0.04 and selective CAPS +0.05 log points; Title Case -0.03, sentence case -0.03), and right-read titles do a little better than left-read ones, which do a little better than neither-read ones (+0.04, +0.01, -0.02); left and right channels shout at the same rate (48 % and 45 % of titles with capitals), the neutral group is sentence case (54 %).
- **Stage 0d, political leaning (2026-09-15; runs third in the pipeline, recorded as stage7_leaning).** Two levels. Titles: Claude Opus, through the Claude Code CLI, labeled 12,478 titles (50 per ranked channel, 16 for the 35 channels with fewer than 50 uploads) as left, right or neither from the title text alone, twenty titles to a call in a random order so that no title was judged beside its channel's other titles; it reads 55 % of titles as neither, 24 % as left and 20 % as right, and the words behind the labels are stance words (fraud, women, Democrats, woke, Kirk, California on the right; Trump, MAGA, war, Israel, breaking, Iran, Epstein on the left). Channels: each channel's score, (right − left) / titles sampled, sorts the 274 channels into 122 left, 110 right and 42 neutral (thresholds ±0.05); the score is reliable (split-half Spearman 0.96; the original 16-title draw and the 34 month-spread top-up titles rank the 239 ranked channels at 0.96), and it survives a re-reading: every title was labeled three times, first in channel-batched calls, then twice in shuffled ones with different seeds (the first shuffled reading is the one used). The two shuffled readings agree on 91 % of titles (kappa 0.84) and rank the channels at 0.99, so the judge's own noise is about one title label in eleven; the channel-batched reading agrees with either at 88–89 %, so a title's batch-mates cost about two points more and pushed labels toward neither. Everything the left channels published against everything the right channels published separates on the same words as the labeled titles, with the year's shared subjects at the apex; nothing moved month to month. A left / right / neither lexicon cut from the judge's own labels at |z| ≥ 1.96 recovers the ordering of channels (Spearman 0.69, out of fold) but not the title-level call (agreement 53 %, kappa 0.26): the judge reads framing, and a word list reads subjects.


## Stage 0: corpus, normalization, balance

| genre | groups | rows | unique | balanced | low_n_groups | median_group_size | max_group_size |
|---|---|---|---|---|---|---|---|
| streams | 166 | 50027 | 42483 | 31469 | 89 | 42 | 8485 |
| videos | 274 | 243563 | 242423 | 151614 | 38 | 234 | 11623 |


Verbatim repeats within creator x genre: 8,684 rows (3.0%); they are collapsed for every style and topic computation and kept for volume, view and hit statistics. Balanced subset (<= 2,500 unique titles per creator x genre, seed 20260914): 183,083 titles; it is used for every pooled fit (topic model, templates, corpus Zipf, LLM sample).


Highest repeat shares (live-broadcast loops):

| creator | genre | n_rows | n_unique | repeat_share |
|---|---|---|---|---|
| @usefulidiots | streams | 66 | 11 | 0.833 |
| @rolandsmartin | streams | 1181 | 569 | 0.518 |
| @RealAmericasVoice | streams | 2944 | 1535 | 0.479 |
| @TimesNowWorld | streams | 4989 | 2827 | 0.433 |
| @timesofindia | streams | 3235 | 2094 | 0.353 |
| @aaronparnas1 | streams | 13 | 10 | 0.231 |
| @thewarningwithsteveschmidt | videos | 347 | 273 | 0.213 |
| @PrisonPlanetLive | videos | 54 | 44 | 0.185 |


Brand stripping: 81 creator x genre groups had at least one pattern above the 20 % rule (99 patterns; full list in `stripped_patterns.csv`). The most frequent:


| creator | genre | kind | pattern | count | share | example |
|---|---|---|---|---|---|---|
| @Firstpost | videos | suffix | n#g | 3239 | 0.336 | N18G |
| @Firstpost | streams | suffix | n#g | 1757 | 0.207 | N18G |
| @BBCNews | videos | suffix | bbc news | 1698 | 0.722 | BBC News |
| @thehill | videos | suffix | rising | 1586 | 0.392 | RISING |
| @SecularTalk | videos | suffix | the kyle kulinski show | 990 | 0.721 | The Kyle Kulinski Show |
| @NewsmaxTV | streams | bracket | #/#/# | 281 | 0.734 | 9/11/2026 |
| @TheBrianKilmeadeShow | videos | suffix | brian kilmeade show | 253 | 0.719 | Brian Kilmeade Show |
| @HasanReactionsfanTwo | videos | suffix | hasanabi reacts | 253 | 0.793 | Hasanabi Reacts |
| @deanwithrs | streams | suffix | debating maga | 244 | 0.972 | Debating MAGA. |
| @NBCNews | streams | suffix | nbc news | 225 | 0.643 | NBC News |
| @TheJoyReidShow | videos | suffix | the joy reid show | 224 | 0.957 | The Joy Reid Show |
| @ABCNews | streams | prefix | live: abc news live | 216 | 0.395 | LIVE: ABC News Live |
| @ABCNews | streams | suffix | abc news | 216 | 0.395 | ABC News |
| @TheDonLemonShow | videos | prefix | lemon drop | 206 | 0.592 | LEMON DROP |
| @DailyDenims | videos | colon | denims | 200 | 0.930 | DENIMS |


Zipf check (does stripping remove the show-brand head?):

| level | text | max_rank | zipf_exponent | n_tokens | n_types | top_20 |
|---|---|---|---|---|---|---|
| pooled_balanced | raw | 100 | 0.8573 | 1999165 | 54552 | the trump to in on of iran s live is and as for a with us war after at news |
| pooled_balanced | raw | 1000 | 0.7813 | 1999165 | 54552 | the trump to in on of iran s live is and as for a with us war after at news |
| pooled_balanced | raw | 5000 | 1.0212 | 1999165 | 54552 | the trump to in on of iran s live is and as for a with us war after at news |
| pooled_balanced | normalised | 100 | 0.8636 | 1943465 | 52809 | the trump to in on of iran s live is and as for a with us war after at over |
| pooled_balanced | normalised | 1000 | 0.7845 | 1943465 | 52809 | the trump to in on of iran s live is and as for a with us war after at over |
| pooled_balanced | normalised | 5000 | 1.0151 | 1943465 | 52809 | the trump to in on of iran s live is and as for a with us war after at over |
| creator_level_mean | raw | 200 | 0.7972 | 1977690 | 483657 | median 0.7962 over 313 creator x genre groups (>= 50 titles) |
| creator_level_mean | normalised | 200 | 0.7806 | 1923441 | 479933 | median 0.7826 over 313 creator x genre groups (>= 50 titles) |


Channel groups (left / neutral / right from each channel's title-leaning score, `leaning_by_creator.csv`; the only between-channel grouping in the report):

| group | creators | clippers |
|---|---|---|
| left | 122 | 5 |
| neutral | 42 | 2 |
| right | 110 | 4 |


Organisations with more than one channel (`creators.csv`): **Al Jazeera** (@ajplus, @aljazeeraenglish); **Blaze Media** (@BlazeTV, @glennbeck); **CBS News** (@60minutes, @CBSNews); **Crooked Media** (@lovettorleaveitpodcast, @podsaveamerica); **Daily Wire** (@AndrewKlavan, @BenShapiro, @MattWalsh, @MichaelKnowles); **Destiny** (@DestinyDGGClips, @destiny, @destinyhqclips); **Fox News** (@FoxNews, @FoxNewsChannelClips, @TheBrianKilmeadeShow); **HasanAbi** (@HasanAbi, @HasanAbiVODs3, @HasanReactionsfanTwo, @HasanabiClips); **MeidasTouch Network** (@LegalAFMTN, @MeidasTouch, @TheMichaelCohenShow, @katiephangnews); **Network18** (@Firstpost, @bushrakhanum); **New York Times** (@EzraKleinShow, @NYTOpinion, @NYTPodcasts, @nytimes); **PragerU** (@PragerU, @XAVIAER); **SNEAKO** (@LIVESNEAKO, @SNEAKO); **TYT Network** (@RebelHQ, @TheDamageReport, @TheYoungTurks); **Timcast** (@Timcast, @TimcastIRL, @TimcastNews); **Times Group** (@TimesNowWorld, @timesofindia); **Turning Point USA** (@RealAlexClark, @turningpointusa); **Vaush** (@TheVaushPit, @Vaush).


Clippers (titles written by fans or an editing team, kept as their own group): @AsmonTV, @ClipsCandaceOwens, @DailyDenims, @DestinyDGGClips, @FoxNewsChannelClips, @HasanAbiVODs3, @HasanReactionsfanTwo, @HasanabiClips, @TheVaushPit, @destinyhqclips, @laurenchenclips.


## Stage 1: topics

BERTopic on a 100,078-title creator-stratified sample (cap 591 per creator x genre): HDBSCAN found 224 topics (35.3% outliers); every title was then assigned to its nearest topic centroid (agreement with HDBSCAN's own labels on cluster members 86.1%; 13.4% of titles are weak assignments below the 10th-percentile similarity). 202 of 224 topics are political; 92.8% of unique titles (raw pooled) fall in political topics.


Political share by channel group (mean of creators, >= 50 unique titles):

| group | genre | n_creators | mean_political_share | median_political_share |
|---|---|---|---|---|
| left | streams | 33 | 0.962 | 0.989 |
| left | videos | 105 | 0.963 | 0.980 |
| neutral | streams | 16 | 0.891 | 0.909 |
| neutral | videos | 37 | 0.882 | 0.909 |
| right | streams | 28 | 0.945 | 0.987 |
| right | videos | 94 | 0.932 | 0.955 |


Largest topics (mean of group-level creator shares, i.e. creator-balanced):

| topic_id | label | political | category | mean_group_share | n_unique_all | n_creators | top_terms | example_1 |
|---|---|---|---|---|---|---|---|---|
| 3 | Trump and Iran War Negotiations | yes | war_conflict | 0.0335 | 13816 | 190 | ceasefire, iran ceasefire, iran trump, trumps iran, deal iran, ceasefire iran, trump says, iran deal, usira... | US-Iran War Live \| 'War Will Continue Until...': Donald Trump Left Red-Faced? \| Iran's Ultimatum |
| 0 | ICE protests in Minneapolis | yes | us_politics | 0.0254 | 6056 | 213 | minneapolis, ice shooting, walz, ice agents, ice, antiice, tim walz, agents, alex pretti, ice agent | What we know in Minneapolis a day after fatal ICE shooting: Protests, agent details, more |
| 2 | Israel and Palestine Conflict | yes | world_politics | 0.0241 | 5344 | 192 | gaza, palestine, palestinian, israels, israeli, netanyahu, jewish, israelis, jews, israel | Ian Carroll: How Israel MANIPULATES Our Media! |
| 7 | Iran political unrest | yes | world_politics | 0.0214 | 6912 | 206 | khamenei, supreme leader, iranians, crown prince, irans, regime, iran iran, funeral, iranian, crown | IRAN’S FINAL CHAPTER |
| 74 | Iran and Political Updates | yes | world_politics | 0.0191 | 1384 | 124 | joins, fail, brittany, reveal, sus, bye, ac, joins iran, jamm, iran hits | IRAN NUCLEAR DEAL, DOLLY PARTON TRIBUTE, CORY BOOKER REVEAL, PENTAGON INFLUENCER, CNN HASAN SMEAR |
| 1 | Shocking Events and Reactions | yes | media_culture_war | 0.0174 | 3828 | 170 | holy, holy sht, fing, theyre, sht, fking, fck, happening, genuinely, anymore | THIS JUST F***ING HAPPENED... IT'S INSANE! |
| 60 | Trump delivering remarks | yes | us_politics | 0.0143 | 1703 | 59 | trump delivers, delivers remarks, trump speaks, remarks, delivers, speaks press, small business, replay pre... | LIVE: PRESIDENT TRUMP GIVES REMARKS |
| 4 | Ukraine-Russia War and Political Figures | yes | war_conflict | 0.0139 | 8146 | 128 | ukraine, russia, putins, putin, russian, zelensky, ukraine war, moscow, russias, lavrov | LIVE \| 'President Putin, Please...': Trump's 'UNBELIEVABLE' & TERRIFYING Ukraine War Update News |
| 15 | Christian Nationalism and Politics | yes | us_politics | 0.0135 | 1606 | 172 | pastor, christian, jesus, nationalism, prayer, god, faith, christianity, christ, christians | HOT TOPICS \| Pastor EXPOSES the Truth About Donald Trump, MAGA & Christian Nationalism! |
| 20 | Feminism and Gender Roles Debate | yes | media_culture_war | 0.0133 | 1323 | 165 | feminism, dating, women, modern women, men, modern, marriage, divorce, men women, feminists | The Harsh Reality About Modern Women Men Are Facing! |
| 5 | Trump and China Relations | yes | world_politics | 0.0120 | 4318 | 162 | xi, chinas, china, xi jinping, jinping, jiang, taiwan, beijing, chinese, professor jiang | Trump in China: Why Xi Jinping Has the Upper Hand \| The Link \| 4K |
| 9 | Indian Politics and Delhi Riots | yes | world_politics | 0.0114 | 10330 | 90 | modi, pm modi, delhi, india, pm, nous, nous clips, singh, assembly, indias | BJP PC LIVE \| Sudhanshu Trivedi, Shehzad Poonawalla\|Nehru\|Congress \|Somnath \|Umar Khalid \|Delhi Riot |
| 8 | AI and Political Implications | yes | media_culture_war | 0.0114 | 3550 | 183 | ai, anthropic, nvidia, humans, bubble, huang, rogue, researcher, tech, companies | AI Is Coming for Your Job — and Even Tech CEOs Aren’t Safe \| NYNext |
| 25 | American History and Political Threats | yes | us_politics | 0.0109 | 1848 | 217 | liberty, fascism, founders, founding, museum, 5minute videos, 5minute, road, cia, revolution | Conquering from Within: The Dangers Facing America |
| 34 | Black America and Racism Discussions | yes | us_politics | 0.0107 | 1397 | 154 | black, white people, black people, black america, white woman, black woman, black americans, month, racism,... | The Argument Black Progressive Leaders Are Too Afraid to Make |
| 46 | Iran-US military conflict in Gulf | yes | war_conflict | 0.0101 | 5406 | 116 | kuwait, fighter jet, fighter, pilot, bases, jet, rescue, dubai, rescued, aircraft | '200 U.S. PILOTS’ RESIDENCES BOMBED: Iranian Army Strikes Back In Biggest Gulf Revenge \| Watch |
| 6 | Trump vs Maduro in Venezuela | yes | world_politics | 0.0101 | 3197 | 175 | maduro, venezuela, venezuelas, venezuelan, capture, trumps venezuela, venezuela oil, captured, colombia, ve... | 'US Will Run Venezuela After Maduro’s Capture': Trump's Big Announcement On Caracas Action |
| 13 | Hormuz Strait Blockade Conflict | yes | war_conflict | 0.0095 | 5099 | 124 | strait hormuz, strait, hormuz, blockade, hormuz blockade, ships, closed, open, iran closes, tankers | STRAIT SHOWDOWN: Trump's battle with Iran over Hormuz ramps up |
| 18 | Epstein Files Revelations | yes | us_politics | 0.0093 | 1771 | 188 | epstein files, files, epsteins, jeffrey epstein, files epstein, epstein, jeffrey, wexner, names, michael tr... | The Dark Truth in the Epstein Files the Media WON'T TOUCH |
| 32 | Democratic Party and Midterm Elections | yes | us_politics | 0.0090 | 2743 | 175 | democratic party, midterms, 2026 midterms, midterm, democratic, democrats, party, democrats win, win midter... | ‘The Five’: Dems losing ground as midterms near... |
| 50 | Left-Wing Political Violence | yes | us_politics | 0.0087 | 1394 | 193 | political violence, violence, left, leftists, lefts, right wing, wing, red scare, conservatism, liberalism | Why the Left's Framework Is the Most Dangerous Threat Today |
| 173 | JLP Weekly Series | no | other | 0.0087 | 761 | 141 | jlp wed, wed, jlp, jlp thu, thu, jlp mon, mon, jlp fri, tue, jlp tue | Seeking for Happiness Destroys It \| JLP Fri 1-23-26 |
| 14 | Hasan Piker Controversy | yes | media_culture_war | 0.0085 | 936 | 134 | hasan, hasan piker, piker, hasanabi reacts, hasans, hasanabi, mehdi hasan, reacts hasanabi, reacts, mehdi | Hasan's Biggest Meltdown Yet \| Shoe0nHead Reacts |
| 121 | Tech Business Founders and Industry | no | tech_business | 0.0085 | 1662 | 138 | mode, build, startup, apple, apples, business, tech, cook, founder, ceo | Best of Build Mode: The Founder Mistakes That Cost Time, Money, and Growth |
| 33 | Candace Owens Controversies | yes | media_culture_war | 0.0084 | 844 | 141 | candace owens, owens, candace, andrew wilson, wilson, erika, erika kirk, candaces, kirk, andrew | EXPLOSIVE: What Did CANDACE OWENS Know?! |


Topic share by channel group, top 5 per group (videos; mean of creator shares):


| group | topic_id | label | political | mean_creator_share | raw_pooled_share | n_creators |
|---|---|---|---|---|---|---|
| left | 2 | Israel and Palestine Conflict | yes | 0.045 | 0.030 | 105 |
| right | 1 | Shocking Events and Reactions | yes | 0.044 | 0.034 | 94 |
| neutral | 121 | Tech Business Founders and Industry | no | 0.040 | 0.013 | 37 |
| left | 3 | Trump and Iran War Negotiations | yes | 0.036 | 0.051 | 105 |
| neutral | 8 | AI and Political Implications | yes | 0.035 | 0.023 | 37 |
| neutral | 3 | Trump and Iran War Negotiations | yes | 0.035 | 0.055 | 37 |
| neutral | 5 | Trump and China Relations | yes | 0.033 | 0.023 | 37 |
| neutral | 2 | Israel and Palestine Conflict | yes | 0.030 | 0.014 | 37 |
| right | 20 | Feminism and Gender Roles Debate | yes | 0.029 | 0.013 | 94 |
| left | 0 | ICE protests in Minneapolis | yes | 0.027 | 0.026 | 105 |
| left | 7 | Iran political unrest | yes | 0.026 | 0.022 | 105 |
| right | 15 | Christian Nationalism and Politics | yes | 0.024 | 0.015 | 94 |
| right | 25 | American History and Political Threats | yes | 0.022 | 0.014 | 94 |
| left | 1 | Shocking Events and Reactions | yes | 0.022 | 0.016 | 105 |
| right | 34 | Black America and Racism Discussions | yes | 0.022 | 0.011 | 94 |


Monthly spikes (creator-balanced share vs the topic's own nine-month mean; top 3 per month):


| month | label | z_vs_own_months | share_month | share_mean_all_months | top_entities | example_1 |
|---|---|---|---|---|---|---|
| 2026-01 | Trump and Greenland politics | 2.660 | 0.031 | 0.004 | Greenland (877); Trump (428); US (234); NATO (165); Denmark (108) | ‘Like it or not’: Trump threatens to take Greenland by force \| Morning in America |
| 2026-01 | Trump at Davos and World Economic Forum | 2.660 | 0.007 | 0.001 | Davos (151); Trump (78); World Economic Forum (29); WEF (21); US (17) | Davos 2026 LIVE: US President Donald Trump Addresses in Davos for World Economic Forum |
| 2026-01 | Trump vs Maduro in Venezuela | 2.650 | 0.059 | 0.009 | Venezuela (1046); Maduro (616); US (580); Trump (330); U.S (162) | 'US Will Run Venezuela After Maduro’s Capture': Trump's Big Announcement On Caracas Action |
| 2026-02 | Prince Andrew Epstein Arrest Revelations | 2.660 | 0.008 | 0.001 | Andrew (89); Prince Andrew (80); UK (51); Andrew Mountbatten-Windsor (34); Epstein (25) | Prince Andrew Arrested — Is the Epstein Reckoning Finally Here? \| Gerry Callahan Show |
| 2026-02 | Super Bowl Halftime Show Controversy | 2.660 | 0.013 | 0.002 | Bad Bunny (43); NFL (33); Patriots (15); Seahawks (10); Kid Rock (8) | Super Bowl Halftime Show DISGRACE! - Cultural Insurrection Bad Bunny Backlash - Full Analysis |
| 2026-02 | Nancy Guthrie Disappearance Case | 2.650 | 0.015 | 0.003 | Nancy Guthrie (678); Guthrie (261); FBI (199); Savannah Guthrie (177); America (42) | Nancy Guthrie Case: New Timeline, “Prime Suspect” Rumors, & Missing Camera Footage |
| 2026-03 | No Kings Protests Movement | 2.650 | 0.007 | 0.002 | Trump (24); US (13); Kings (12); Donald Trump (7); Bruce Springsteen (5) | WATCH LIVE: NO KINGS PROTESTS |
| 2026-03 | Joe Kent Resignation and Leaks | 2.650 | 0.010 | 0.002 | Joe Kent (88); Iran (28); Trump (17); FBI (10); Israel (10) | Joe Kent in HOT WATERS as Trump Exposes Real Reason He Flipped on America & Israel! |
| 2026-03 | Iran political unrest | 2.570 | 0.068 | 0.021 | Iran (1549); US (366); Khamenei (92); Israel (84); Tehran (81) | IRAN’S FINAL CHAPTER |
| 2026-04 | King Charles III and Trump State Visit | 2.640 | 0.007 | 0.001 | US (91); Trump (76); Charles III (65); Congress (61); UK (56) | WATCH : Britain’s King Charles addresses Joint session of U.S. Congress \|Trump \| State Visit \|UK |
| 2026-04 | Trump and Pope Leo Feud | 2.630 | 0.013 | 0.002 | Trump (139); Pope Leo (104); Leo XIV (53); Iran (48); Jesus (38) | Why Trump And Pope Leo Are at Odds — Inside The Feud And The 'Blasphemous' AI Jesus Photo |
| 2026-04 | Eric Swalwell Allegations and Resignation | 2.610 | 0.007 | 0.001 | Eric Swalwell (117); Swalwell (51); Congress (29); California (13); House (10) | Serious Allegations Against Rep. Eric Swalwell Have Surfaced |
| 2026-05 | Thomas Massie and Trump political conflict | 2.640 | 0.011 | 0.002 | Thomas Massie (79); Trump (37); Massie (34); Kentucky (32); Ed Gallrein (13) | Thomas Massie Gets Trumped, Loses His Representative Seat |
| 2026-05 | Trump and China Relations | 2.600 | 0.029 | 0.011 | China (802); Trump (282); Beijing (169); US (166); Taiwan (162) | Trump in China: Why Xi Jinping Has the Upper Hand \| The Link \| 4K |
| 2026-05 | Covid Vaccine Controversy | 2.390 | 0.013 | 0.005 | US (38); U.S (21); CDC (20); Nebraska (17); Congo (16) | Senator Just Announced How DEADLY Dr. Fauci’s COVID Vaccine REALLY Is... Horrifying |
| 2026-06 | NBA Championship Celebrations | 2.640 | 0.009 | 0.002 | Knicks (88); NBA (84); Trump (26); New York Knicks (24); New York (19) | Mayhem in New York City after Knicks win first NBA championship in 53 years |
| 2026-06 | Karmelo Anthony Trial Verdict | 2.540 | 0.024 | 0.007 | Karmelo Anthony (137); Luigi Mangione (27); Austin Metcalf (13); Karmelo (13); Gilgo Beach (12) | What Everybody Is Missing In The Karmelo Anthony Trial |
| 2026-06 | UFC at White House Event | 2.470 | 0.013 | 0.003 | UFC (109); White House (95); Trump (56); FBI (22); Dana White (18) | White House UFC Shocker On Cam: ‘OMG, This President Can’t...’: Trump’s Startling Act \| Watch |
| 2026-07 | Lindsey Graham's Death and Legacy | 2.640 | 0.019 | 0.003 | Lindsey Graham (476); Graham (61); Senate (57); Trump (53); US (30) | Lindsey Graham: The Aftermath |
| 2026-07 | Mitch McConnell Health Mystery | 2.600 | 0.010 | 0.002 | Mitch McConnell (133); McConnell (50); Kentucky (15); Senate (8); GOP (6) | SHOCKING Mitch McConnell UPDATE |
| 2026-07 | Christopher Nolan's Odyssey Reviews | 2.480 | 0.008 | 0.002 | Christopher Nolan (20); Odyssey (9); Hollywood (3); Ben Shapiro (3); Nolan (3) | Christopher Nolan's Odyssey: a true Hollywood disaster |
| 2026-08 | Trump aide Natalie Harp and Jon Ossoff | 2.640 | 0.008 | 0.001 | Natalie Harp (89); Trump (44); Jon Ossoff (18); Ossoff (10); White House (6) | TRENDING NOW! Who is Natalie Harp? Her Trump Connection explained as Jon Ossoff’s attack POTUS |
| 2026-08 | WNBA and Sophie Cunningham controversy | 2.620 | 0.016 | 0.003 | WNBA (74); NBA (15); Sophie Cunningham (9); Royce White (4); National Report (4) | ‘The Five’: WNBA dribbles up more drama |
| 2026-08 | Abdul El-Sayed vs AIPAC in Michigan Senate Primary | 2.580 | 0.016 | 0.003 | Abdul El-Sayed (144); Michigan (72); El-Sayed (60); Senate (24); Mike Rogers (22) | Abdul El-Sayed vs AIPAC: Michigan’s real primary \| The Listening Post |
| 2026-09 | 9/11 Remembrance 25 Years Later | 2.670 | 0.037 | 0.005 | Pentagon (37); America (23); Trump (19); New York (18); Mamdani (17) | 25 Years Later: Remembering the Heroes of 9/11 |
| 2026-09 | MAGA Mike Johnson political turmoil | 2.520 | 0.003 | 0.002 | Mike Johnson (8); MAGA Mike (2); House (2); Mike Johnson Warns (2); OMG (1) | Trump Keeps Making Mike Johnson's Life A Living Hell |
| 2026-09 | Lindsay Clancy Murder Trial | 2.500 | 0.046 | 0.009 | Lindsay Clancy (262); Clancy (19); Lindsay Clancy Jury (13); Kevin Reddington (10); Lindsay Clancy Trial (9) | VERDICT WATCH: Lindsay Clancy Trial |


Entities most named per topic (top 15 topics): see `topic_labels.csv` columns `top_persons` / `top_orgs`.

| topic_id | label | top_persons | top_orgs |
|---|---|---|---|
| 3 | Trump and Iran War Negotiations | Trump (1243); Donald Trump (232); Netanyahu (171); Hormuz (98); Putin (92); John Bolton (71); Khamenei (65)... | Trump (2257); White House (185); Vantage on Firstpost (135); TRUMP (111); GOP (83); Firstpost America (69);... |
| 0 | ICE protests in Minneapolis | Alex Pretti (65); Tim Walz (59); Trump (58); Renee Good (54); Border Patrol (30); Jacob Frey (22); JD Vance... | Trump (258); DHS (116); REUTERS (46); FBI (44); ICE (35); White House (33); NewsNation Live (33); TSA (32) |
| 2 | Israel and Palestine Conflict | Netanyahu (379); Trump (62); Benjamin Netanyahu (48); Inside Story (36); Ro Khanna (32); Max Blumenthal (31... | Trump (103); Hamas (86); UN (77); Congress (21); REUTERS (21); Palestine Action (20); Vantage on Firstpost ... |
| 7 | Iran political unrest | Khamenei (191); Mojtaba Khamenei (96); Trump (49); Ayatollah Ali Khamenei (46); Ali Khamenei (43); Inside S... | Supreme (92); supreme (68); Trump (55); CIA (52); UN (47); Vantage on Firstpost (40); NewsNation Live (26);... |
| 74 | Iran and Political Updates | Tom Llamas (176); Top Story (175); Trump (19); Michael Popok (13); Hormuz (12); Candace Owens (12); Erika K... | NBC News (175); Trump (92); GOP (17); Bloomberg (13); White House (11); MAGA (11); FBI (11); Candace (8) |
| 1 | Shocking Events and Reactions | McEnany (33); Peter Doocy (6); Keane (6); Ben (5); Bongino (5); Watters (5); Trump (3); Nick Shirley (3) | Old School (35); INSANE (7); NEVER (6); WTF (6); BRUTAL (4); PBD (4); MTG (3); LEAKED (3) |
| 60 | Trump delivering remarks | Trump (331); Donald Trump (159); Trump Speaks (75); Trump Delivers Remarks (40); Trump Holds (31); Trump Ho... | White House (173); Trump (97); House (29); Oval Office (19); GOP (17); Air Force One (14); Cabinet (12); NA... |
| 4 | Ukraine-Russia War and Political Figures | Putin (1091); Zelensky (376); PUTIN (101); Trump (68); Kyiv (47); Firstpost Live (40); Vladimir Putin (33);... | NATO (282); World News (242); Times Now World (207); EU (156); Trump (90); CIA (74); Kremlin (54); UN (48) |
| 15 | Christian Nationalism and Politics | Jesus (49); Charlie Kirk (16); JENNY HOLLAND (12); James Talarico (11); Pete Hegseth (9); Christian Nationa... | MLB (16); Trump (14); Church (13); HARNWELL (10); JLP (9); Catholic Church (7); Franklin (6); MAGA Pastor (5) |
| 20 | Feminism and Gender Roles Debate | Debra Soh (9); Pearl (5); Dating Apps (4); Adam Carolla (3); Rachel Wilson (3); Gloria Steinem (3); Heather... | Modern Women (7); Excerpt (5); JLP (4); Taliban (3); Global Dating Crisis (3); NHS (3); New York Times (2);... |
| 5 | Trump and China Relations | Xi (213); Trump (160); Xi Jinping (110); Putin (88); Kim Jong Un (47); Donald Trump (41); Firstpost Live (2... | Trump (256); Vantage on Firstpost (74); China MoFA (37); REUTERS (33); CCP (31); Firstpost America (27); Wo... |
| 9 | Indian Politics and Delhi Riots | Rahul Gandhi (276); Suvendu Adhikari (225); Lok Sabha (128); Yogi Adityanath (126); Tamil Nadu (109); Rajna... | BJP (1150); Congress (473); TMC (284); CJP (259); Parliament (135); TVK (114); PM Modi (112); DMK (93) |
| 8 | AI and Political Implications | Sam Altman (38); Haslinda Amin (27); Joe Allen (23); OpenAI (21); Jensen Huang (21); JOE ALLEN (19); Bernie... | AI (190); Pentagon (49); OpenAI (34); Vantage on Firstpost (33); Google (31); Trump (28); Meta (23); IPO (22) |
| 25 | American History and Political Threats | Victor Davis Hanson (17); Trump (16); Obama (9); Ken Burns (9); George Washington (8); Jeffrey Sachs (6); E... | CIA (29); Trump (22); White House Founders Museum (9); NEWSMAX Daily (7); Congress (6); Firstpost America (... |
| 34 | Black America and Racism Discussions | Jasmine Crockett (10); Roland Martin (10); Michelle Obama (7); James Talarico (6); Laura Loomer (6); Trump ... | Trump (15); JLP (15); Firstpost America (9); White Woman (7); Black America (6); MLK (6); Black Woman (6); ... |


## Stage 2: style dimensions

Exploratory factor analysis on 1,999 creator x genre x month cells (>= 15 unique titles) x 74 features (dropped: 7, listed in the appendix). KMO = 0.721; Bartlett chi2 = 109,531 (p = 0). Parallel analysis retains 16 factors (Kaiser: 21); retained 12 (minres, oblimin), cumulative variance 47.2%. Scree data: `scree.csv` / `scree.png`.


Retained factors, named from their loadings (|loading| >= 0.4 shown; full table in the appendix):


| factor | name | variance | positive loadings | negative loadings |
|---|---|---|---|---|
| F1 | Positive tone vs outrage (shock words, violence verbs, negative sentiment) | 5.2% | vader_compound_mean (+0.91), vader_pos_mean (+0.45) | vader_neg_mean (-0.76), shock_word_p100 (-0.75), violence_verb_p100 (-0.64) |
| F2 | +has_finite_verb +present_tense +verb_share +past_tense | 4.9% | has_finite_verb_p100 (+0.91), present_tense_p100 (+0.73), verb_share_mean (+0.54), past_tense_p100 (+0.53),... | propn_share_mean (-0.48) |
| F3 | Labelled live/formulaic headline (LIVE:, BREAKING:, colon labels) | 4.7% | lead_colon_label_p100 (+0.84), lead_live_p100 (+0.82), colon_p100 (+0.80), formulaic_p100 (+0.47), adv_shar... | entity_first_p100 (-0.60) |
| F4 | +trailing_ellipsis +discourse_marker +ellipsis +contraction | 4.5% | trailing_ellipsis_p100 (+0.84), discourse_marker_p100 (+0.82), ellipsis_p100 (+0.73), contraction_p100 (+0.... |  |
| F5 | Question and explainer framing (why, what, ?) | 4.4% | q_word_start_p100 (+0.96), wh_any_p100 (+0.84), why_marker_p100 (+0.78), q_mark_p100 (+0.48) |  |
| F6 | Person-centred (named people) | 4.2% | n_person_p100 (+0.97), has_person_p100 (+0.96) |  |
| F7 | Descriptive news prose vs title-case (nouns, adjectives, places) | 4.1% | noun_share_mean (+0.80), adj_share_mean (+0.53), n_gpe_p100 (+0.42) | cap_token_share_mean (-0.71), negation_p100 (-0.40) |
| F8 | Numeric and dated (digits, years) | 3.6% | num_share_mean (+0.95), digit_p100 (+0.83), year_mention_p100 (+0.66) |  |
| F9 | ALL-CAPS shouting | 3.5% | allcaps_word_share_mean (+0.95), full_caps_title_p100 (+0.84), has_allcaps_word_p100 (+0.47) |  |
| F10 | Quoted speech | 3.2% | quoted_speech_p100 (+0.93), quotes_p100 (+0.91) |  |
| F11 | +n_chars +vader_pos +nominalisation +n_org | 2.6% | n_chars_mean (+0.55), vader_pos_mean (+0.53), nominalisation_p100 (+0.42), n_org_p100 (+0.40) |  |
| F12 | +first_pl +future_will +modal | 2.3% | first_pl_p100 (+0.47), future_will_p100 (+0.44), modal_p100 (+0.41) |  |


Factor correlations (oblimin):

| factor | F1 | F2 | F3 | F4 | F5 | F6 | F7 | F8 | F9 | F10 | F11 | F12 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| F1 | 1.00 | -0.07 | -0.04 | 0.10 | 0.12 | -0.06 | -0.15 | 0.25 | -0.27 | -0.06 | 0.11 | 0.05 |
| F2 | -0.07 | 1.00 | 0.05 | 0.09 | -0.04 | -0.09 | -0.06 | -0.28 | 0.22 | 0.07 | 0.20 | -0.05 |
| F3 | -0.04 | 0.05 | 1.00 | -0.07 | 0.06 | -0.16 | -0.05 | 0.19 | 0.05 | -0.05 | -0.01 | -0.13 |
| F4 | 0.10 | 0.09 | -0.07 | 1.00 | 0.03 | -0.02 | 0.07 | -0.00 | 0.15 | 0.23 | -0.17 | 0.20 |
| F5 | 0.12 | -0.04 | 0.06 | 0.03 | 1.00 | 0.01 | -0.06 | 0.02 | -0.20 | -0.06 | 0.06 | 0.07 |
| F6 | -0.06 | -0.09 | -0.16 | -0.02 | 0.01 | 1.00 | 0.07 | -0.15 | 0.10 | 0.12 | 0.08 | 0.03 |
| F7 | -0.15 | -0.06 | -0.05 | 0.07 | -0.06 | 0.07 | 1.00 | -0.10 | 0.11 | 0.10 | -0.07 | 0.11 |
| F8 | 0.25 | -0.28 | 0.19 | -0.00 | 0.02 | -0.15 | -0.10 | 1.00 | -0.19 | -0.06 | -0.19 | 0.06 |
| F9 | -0.27 | 0.22 | 0.05 | 0.15 | -0.20 | 0.10 | 0.11 | -0.19 | 1.00 | 0.24 | -0.21 | 0.09 |
| F10 | -0.06 | 0.07 | -0.05 | 0.23 | -0.06 | 0.12 | 0.10 | -0.06 | 0.24 | 1.00 | -0.09 | 0.11 |
| F11 | 0.11 | 0.20 | -0.01 | -0.17 | 0.06 | 0.08 | -0.07 | -0.19 | -0.21 | -0.09 | 1.00 | -0.16 |
| F12 | 0.05 | -0.05 | -0.13 | 0.20 | 0.07 | 0.03 | 0.11 | 0.06 | 0.09 | 0.11 | -0.16 | 1.00 |


Do the factors map onto the candidate labels? (creator-level Spearman r between the LLM rating aggregated to creator x genre and the raw factor score; present >= 0.5, partial 0.3-0.5, absent < 0.3; 'merged' = two candidates land on the same factor):


| candidate | best_factor | factor_auto_name | creator_level_r | second_factor | second_r | verdict |
|---|---|---|---|---|---|---|
| Sensational | F1 | +vader_compound -vader_neg -shock_word -violence_verb | -0.709 | F5 | -0.322 | merged: Sensational, Critical, Analytical/Informational |
| Critical | F1 | +vader_compound -vader_neg -shock_word -violence_verb | -0.494 | F5 | -0.167 | merged: Sensational, Critical, Analytical/Informational |
| Analytical/Informational | F1 | +vader_compound -vader_neg -shock_word -violence_verb | 0.422 | F5 | 0.419 | merged: Sensational, Critical, Analytical/Informational |
| Educational | F5 | +q_word_start +wh_any +why_marker +q_mark | 0.384 | F1 | 0.312 | partial |
| Conversational | F4 | +trailing_ellipsis +discourse_marker +ellipsis +contraction | 0.174 | F1 | 0.166 | absent |
| Humor | F2 | +has_finite_verb +present_tense +verb_share +past_tense | 0.077 | F4 | 0.067 | absent |


LLM rating vs factor score, creator level (Spearman, n = 318 creator x genre groups with >= 5 rated titles):

| llm | F1 | F10 | F11 | F12 | F2 | F3 | F4 | F5 | F6 | F7 | F8 | F9 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| analytical | 0.42 | 0.25 | 0.14 | 0.35 | 0.02 | 0.20 | -0.17 | 0.42 | -0.01 | -0.02 | 0.16 | -0.27 |
| conversational | 0.17 | -0.03 | -0.02 | -0.08 | 0.05 | -0.09 | 0.17 | 0.10 | -0.13 | -0.00 | -0.07 | 0.00 |
| critical | -0.49 | 0.05 | 0.04 | -0.15 | 0.07 | -0.17 | 0.05 | -0.17 | 0.10 | -0.07 | -0.15 | 0.05 |
| curiosity_gap | -0.03 | -0.06 | -0.14 | -0.13 | 0.10 | -0.08 | 0.17 | 0.14 | -0.15 | -0.15 | -0.14 | 0.17 |
| educational | 0.31 | 0.16 | 0.06 | 0.14 | 0.03 | 0.01 | -0.02 | 0.38 | -0.14 | -0.06 | 0.03 | -0.07 |
| humor | -0.02 | 0.02 | -0.02 | -0.06 | 0.08 | -0.06 | 0.07 | -0.04 | -0.02 | 0.06 | -0.03 | -0.02 |
| outrage | -0.61 | -0.07 | -0.01 | -0.17 | 0.10 | -0.18 | 0.10 | -0.24 | -0.00 | -0.07 | -0.22 | 0.21 |
| sensational | -0.71 | -0.05 | 0.02 | -0.22 | 0.10 | -0.15 | 0.17 | -0.32 | 0.10 | -0.03 | -0.18 | 0.30 |


LLM rating vs factor score, title level (Spearman, n = 2,854 rated titles):

| llm | F1 | F10 | F11 | F12 | F2 | F3 | F4 | F5 | F6 | F7 | F8 | F9 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| analytical | 0.18 | 0.11 | 0.07 | 0.10 | -0.03 | 0.09 | -0.03 | 0.21 | 0.01 | 0.02 | 0.07 | -0.12 |
| conversational | 0.15 | -0.03 | 0.04 | 0.00 | 0.02 | -0.04 | 0.13 | 0.06 | -0.07 | -0.04 | -0.04 | 0.05 |
| critical | -0.28 | 0.03 | 0.02 | -0.03 | 0.06 | -0.15 | -0.08 | -0.15 | 0.10 | -0.00 | -0.03 | -0.02 |
| curiosity_gap | 0.02 | 0.02 | -0.01 | -0.01 | 0.05 | -0.00 | 0.09 | 0.05 | -0.06 | -0.05 | -0.01 | 0.01 |
| educational | 0.15 | 0.08 | 0.06 | 0.01 | -0.01 | 0.05 | 0.04 | 0.20 | -0.03 | 0.01 | 0.03 | -0.03 |
| humor | 0.04 | 0.02 | 0.03 | -0.01 | 0.00 | -0.01 | -0.01 | -0.01 | -0.02 | -0.01 | -0.02 | -0.01 |
| outrage | -0.33 | 0.01 | 0.02 | -0.03 | 0.10 | -0.08 | -0.02 | -0.13 | -0.03 | -0.02 | -0.07 | 0.05 |
| sensational | -0.36 | 0.02 | 0.03 | -0.04 | 0.10 | -0.02 | 0.01 | -0.13 | 0.04 | -0.03 | -0.00 | 0.13 |


Test-retest reliability of the LLM rater (n = 289 titles rated twice in re-shuffled batches, same model, temperature 0):

| dimension | n | exact_agreement | within_1 | spearman_r | weighted_kappa | kappa |
|---|---|---|---|---|---|---|
| sensational | 289 | 0.616 | 0.782 | 0.740 | 0.737 |  |
| critical | 289 | 0.709 | 0.751 | 0.582 | 0.585 |  |
| analytical | 289 | 0.581 | 0.768 | 0.598 | 0.552 |  |
| educational | 289 | 0.824 | 0.952 | 0.251 | 0.236 |  |
| conversational | 289 | 0.900 | 0.945 | 0.496 | 0.632 |  |
| humor | 289 | 0.993 |  |  |  | 0.000 |
| curiosity_gap | 289 | 0.979 |  |  |  | 0.390 |
| outrage | 289 | 0.754 |  |  |  | 0.492 |
| format_llm | 289 | 0.796 |  |  |  | 0.590 |


Topic control: share of variance in each factor score explained by topic (title level, balanced subset) and how much creator-level variance topic mix accounts for:

| factor | n_topics | title_level_r2_topic | creator_level_r2_topic | creator_level_corr_raw_controlled | auto_name |
|---|---|---|---|---|---|
| F1 | 224 | 0.127 | 0.480 | 0.940 | +vader_compound -vader_neg -shock_word -violence_verb |
| F2 | 224 | 0.060 | 0.274 | 0.960 | +has_finite_verb +present_tense +verb_share +past_tense |
| F3 | 224 | 0.121 | 0.316 | 0.968 | +lead_colon_label +lead_live +colon -entity_first |
| F4 | 224 | 0.150 | 0.438 | 0.972 | +trailing_ellipsis +discourse_marker +ellipsis +contraction |
| F5 | 224 | 0.037 | 0.216 | 0.982 | +q_word_start +wh_any +why_marker +q_mark |
| F6 | 224 | 0.183 | 0.385 | 0.950 | +n_person +has_person |
| F7 | 224 | 0.114 | 0.264 | 0.958 | +noun_share -cap_token_share +adj_share +n_gpe |
| F8 | 224 | 0.256 | 0.691 | 0.843 | +num_share +digit +year_mention |
| F9 | 224 | 0.061 | 0.142 | 0.983 | +allcaps_word_share +full_caps_title +has_allcaps_word |
| F10 | 224 | 0.048 | 0.208 | 0.959 | +quoted_speech +quotes |
| F11 | 224 | 0.086 | 0.279 | 0.961 | +n_chars +vader_pos +nominalisation +n_org |
| F12 | 224 | 0.116 | 0.506 | 0.880 | +first_pl +future_will +modal |


Channel-group medians of topic-controlled scores, videos (non-low-n creators):

| group | n | F1 | F2 | F3 | F4 | F5 | F6 | F7 | F8 | F9 | F10 | F11 | F12 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| left | 105 | 0.12 | -0.07 | -0.29 | -0.14 | 0.10 | -0.25 | -0.54 | -0.21 | -0.33 | -0.44 | -0.30 | -0.08 |
| neutral | 37 | 0.51 | -0.09 | -0.36 | -0.11 | 0.07 | -0.22 | -0.26 | 0.01 | -0.35 | -0.09 | -0.12 | -0.03 |
| right | 94 | 0.17 | 0.08 | -0.29 | -0.08 | 0.18 | -0.29 | -0.65 | -0.14 | -0.27 | -0.41 | -0.17 | -0.29 |


Channel-group medians of topic-controlled scores, streams (non-low-n creators):

| group | n | F1 | F2 | F3 | F4 | F5 | F6 | F7 | F8 | F9 | F10 | F11 | F12 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| left | 33 | -0.24 | -0.42 | -0.23 | -0.18 | -0.32 | 0.68 | -0.43 | -0.07 | -0.42 | -0.58 | 0.03 | -0.03 |
| neutral | 16 | 0.28 | 0.14 | 0.91 | -0.10 | -0.36 | 0.13 | 0.35 | 0.16 | -0.43 | -0.67 | -0.64 | 0.06 |
| right | 28 | 0.14 | -0.33 | -0.25 | -0.10 | -0.28 | -0.09 | -0.64 | 0.10 | -0.37 | -0.44 | 0.13 | -0.16 |


Creators at the extremes of each topic-controlled dimension (videos):

| factor | name | highest (videos) | lowest (videos) |
|---|---|---|---|
| F1 | Positive tone vs outrage (shock words, violence verbs, negative sentiment) | @NPR, @AndWeKnowOfficial-o9b, @turningpointusa, @MichaelMaliceofficial, @TimDillonShow | @DannyHaiphongYT, @BlackConservativePerspective, @katiephangnews, @DoubleDownNews, @TheDamageReport |
| F2 | +has_finite_verb +present_tense +verb_share +past_tense | @moreperfectunion, @Tim_Black, @UnHerd, @MattWalsh, @X22Report-y5y | @joerogan, @FleccasTalks, @TimDillonShow, @newdiscourses, @RobertGouveiaEsq |
| F3 | Labelled live/formulaic headline (LIVE:, BREAKING:, colon labels) | @RSBN, @aaronparnas1, @TimesNowWorld, @LukeBeasley, @DailyDenims | @ANINewsIndia, @DylanBurnsLIVE, @thewarningwithsteveschmidt, @lovettorleaveitpodcast, @thegrayzone7996 |
| F4 | +trailing_ellipsis +discourse_marker +ellipsis +contraction | @BelleRanch, @AsmonTV, @bennyjohnson, https://rumble.com/c/russellbrand, @harryjsisson | @thewarningwithsteveschmidt, @ActualJusticeWarrior, @FleccasTalks, @joerogan, @TimcastNews |
| F5 | Question and explainer framing (why, what, ?) | @TheEconomist, @wsj, @nationalreview, @TheDailyBeast, @nytimes | @CashJordan, @ActualJusticeWarrior, @BlackConservativePerspective, @SydneyWatson, @Timcast |
| F6 | Person-centred (named people) | @BadFaithPodcast, @DannyHaiphongYT, @JamarlThomas, @fastpoliticspodcast, @RealAlexClark | @moreperfectunion, @GeopoliticalEconomyReport, @dineshdsouza, @ajplus, @TheVaushPit |
| F7 | Descriptive news prose vs title-case (nouns, adjectives, places) | @aljazeeraenglish, @Reuters, @thegrayzone7996, @CBSNews, @USATODAY | @moreperfectunion, @jlptalk, @DrSteveTurleyTV, @MattWalsh, @DoubleDownNews |
| F8 | Numeric and dated (digits, years) | @HasanAbiVODs3, @60minutes, @Firstpost, @Forbes, @ponderingpolitics | @PoliticsGirl, @TheEconomist, @UnHerd, @triggerpod, @GeopoliticalEconomyReport |
| F9 | ALL-CAPS shouting | @JacksonHinkleOfficial, @AndWeKnowOfficial-o9b, @katiephangnews, @FleccasTalks, @TheQuartering | @TheDamageReport, @JackCocchiarellaShow, @joerogan, @TheDailyBeast, @TheHumanistReport |
| F10 | Quoted speech | @PiersMorganUncensored, @timesofindia, @jlptalk, @CashJordan, @msnow | @ZeihanonGeopolitics, @PartOfTheProblem, @DrSteveTurleyTV, @UnHerd, @SabbySabs |
| F11 | +n_chars +vader_pos +nominalisation +n_org | @AndWeKnowOfficial-o9b, https://rumble.com/c/BannonsWarRoom, @BlackConservativePerspective, @jlptalk, @RonP... | @SydneyWatson, @joerogan, @thewarningwithsteveschmidt, @PartOfTheProblem, @UnHerd |
| F12 | +first_pl +future_will +modal | @thewarningwithsteveschmidt, @BelleRanch, @moreperfectunion, @TheEconomist, https://rumble.com/c/BannonsWar... | @AsmonTV, @bennyjohnson, @The_Crucible, @destinyhqclips, @PiscoLitty |


Lexical diversity: Heaps' exponent and Zipf exponent on 20 subsamples per creator x genre; rank correlations across subsample sizes (sample-size sensitivity):

| measure | n_a | n_b | n_groups | spearman | mean_a | mean_b |
|---|---|---|---|---|---|---|
| heaps_beta | 1000 | 1500 | 212 | 0.996 | 0.828 | 0.817 |
| zipf | 1000 | 1500 | 212 | 0.971 | 0.688 | 0.719 |
| heaps_beta | 1500 | 3000 | 139 | 0.991 | 0.819 | 0.798 |
| zipf | 1500 | 3000 | 139 | 0.927 | 0.719 | 0.770 |
| heaps_beta | 1000 | 3000 | 139 | 0.979 | 0.830 | 0.798 |
| zipf | 1000 | 3000 | 139 | 0.828 | 0.687 | 0.770 |


Heaps' exponent at 1,500 tokens, videos (n = 165): lowest (most repetitive vocabulary) @harryjsisson, @LukeBeasley, @briantylercohen, @ponderingpolitics, @adammockler; highest @Reuters, @MLChristiansen, @ANINewsIndia, @FoxNewsChannelClips, @nypost. Mean 0.821, sd 0.036.


## Stage 3: formats and hooks

Hook classifier (StandardScaler + LogisticRegression(class_weight=balanced); features: 768-d sentence embedding + ['allcaps_word_share', 'excl', 'q_mark', 'trailing_ellipsis', 'violence_verb', 'shock_word', 'curiosity_lex', 'fwd_ref_start', 'discourse_marker', 'has_person', 'neg_eval', 'pos_eval']), trained on the LLM labels:

| hook | n_train | n_test | base_rate | C | holdout_accuracy | holdout_balanced_accuracy | holdout_f1 | holdout_auc | holdout_kappa |
|---|---|---|---|---|---|---|---|---|---|
| curiosity_gap | 2283 | 571 | 0.021 | 0.030 | 0.956 | 0.570 | 0.138 | 0.694 | 0.116 |
| outrage | 2283 | 571 | 0.574 | 0.030 | 0.778 | 0.773 | 0.806 | 0.847 | 0.545 |
| humor | 2283 | 571 | 0.004 | 0.030 | 0.998 | 0.750 | 0.667 | 0.939 | 0.666 |


Share of titles per category, videos (mean of creator shares, non-low-n creators):

| group | n_creators | question | breaking_live | episode_show | interview_guest | reaction | confrontation | listicle | howto_explainer | curiosity_gap | outrage | humor |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| left | 105.00 | 0.16 | 0.03 | 0.03 | 0.10 | 0.03 | 0.08 | 0.00 | 0.08 | 0.04 | 0.64 | 0.00 |
| neutral | 37.00 | 0.14 | 0.01 | 0.07 | 0.12 | 0.02 | 0.08 | 0.00 | 0.07 | 0.03 | 0.37 | 0.00 |
| right | 94.00 | 0.15 | 0.02 | 0.07 | 0.08 | 0.02 | 0.08 | 0.00 | 0.09 | 0.05 | 0.60 | 0.00 |


Share of titles per category, streams (mean of creator shares, non-low-n creators):

| group | n_creators | question | breaking_live | episode_show | interview_guest | reaction | confrontation | listicle | howto_explainer | curiosity_gap | outrage | humor |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| left | 33.00 | 0.11 | 0.17 | 0.06 | 0.18 | 0.01 | 0.15 | 0.00 | 0.03 | 0.03 | 0.63 | 0.00 |
| neutral | 16.00 | 0.05 | 0.52 | 0.02 | 0.14 | 0.01 | 0.08 | 0.00 | 0.01 | 0.03 | 0.29 | 0.00 |
| right | 28.00 | 0.13 | 0.16 | 0.26 | 0.14 | 0.02 | 0.09 | 0.00 | 0.05 | 0.04 | 0.56 | 0.00 |


Rule vs LLM format label on the rated sample (rule = regex on the raw title; LLM = single format label):

| category | n | rule_positives | llm_positives | precision_rule_vs_llm | recall_rule_vs_llm | f1 | kappa | agreement |
|---|---|---|---|---|---|---|---|---|
| question | 2854 | 407 | 54 | 0.103 | 0.778 | 0.182 | 0.154 | 0.868 |
| breaking_live | 2854 | 233 | 251 | 0.815 | 0.757 | 0.785 | 0.765 | 0.964 |
| episode_show | 2854 | 213 | 211 | 0.526 | 0.531 | 0.528 | 0.490 | 0.930 |
| interview_guest | 2854 | 306 | 93 | 0.180 | 0.591 | 0.276 | 0.238 | 0.899 |
| reaction | 2854 | 74 | 53 | 0.473 | 0.660 | 0.551 | 0.541 | 0.980 |
| confrontation | 2854 | 231 | 93 | 0.208 | 0.516 | 0.296 | 0.262 | 0.920 |
| listicle | 2854 | 2 | 4 | 1.000 | 0.500 | 0.667 | 0.666 | 0.999 |
| howto_explainer | 2854 | 207 | 71 | 0.169 | 0.493 | 0.252 | 0.223 | 0.927 |


Examples (corpus-wide, three per category):

| category | creator | title |
|---|---|---|
| question | @CNN | Can Dems take the Senate even without Maine? |
| question | @FoxNewsChannelClips | Will Cain: Where will Gov. Walz go next with his analogies? |
| question | @bulwarkmedia | The Next Level LIVE: Texas Primary Results! Megyn Kelly Turns on Trump?! |
| breaking_live | @RealAmericasVoice | TRUMP'S IRAN DEAL BOMBSHELL, FED HOLDS RATES, SPLC NAZI SCANDAL EXPLODES \| LIVE FROM STUDIO 6B |
| breaking_live | @ANINewsIndia | WATCH: Sonam Wangchuk breaks 26-day fast amid CJP protest at Jantar Mantar against NEET Paper leak |
| breaking_live | @Firstpost | 🔴FIFA WORLD CUP LIVE \| Mexico Football Fans Hit Fever Pitch \| Mexico vs South Africa |
| episode_show | @RealDanBongino | They're Finding Out (Ep. 2549) |
| episode_show | @glennbeck | Remembering Charlie Kirk: Where Are We Now? \| Hour 1 \| 9/10/26 |
| episode_show | @RSBN | FULL EVENT: President Trump Creates U.S. Space Academy & Awards Space Medal of Honor - 08/28/26 |
| interview_guest | @ABCNews | The Obama Legacy: First Joint Interview Post-White House |
| interview_guest | @bulwarkmedia | Trump Promised Trillions in Cuts—And Delivered Nothing (w/ Jessica Riedl) \| Mona Charen Show |
| interview_guest | @timesofindia | 'ENOUGH IS ENOUGH': Tucker Carlson Joins Growing Revolt As Trump's Iran Gamble Backfires Inside MAGA |
| reaction | @DestinyDGGClips | Atrioc Responds After Getting Into MASSIVE Controversy |
| reaction | @SkyNews | Democrats react to Trump's citizenship defeat outside Supreme Court |
| reaction | @oann | WV Governor Praises National Guard Officers for Heroic Response to DC Attack |
| confrontation | @ANINewsIndia | ‘We'll destroy it as we get it’, Trump warns Iran after Khamenei’s 'defiance' over enriched Uranium |
| confrontation | @RealAmericasVoice | FAUCI TAKES THE FIFTH IN EXPLOSIVE SENATE HEARING, BERENSON DESTROYS COVID LIES \| CHARLIE KIRK SHOW |
| confrontation | @markets | US-Iran Clashes Hit Stocks as Oil Rises \| Bloomberg Brief 09/02/2026 |
| listicle | @RealAmericasVoice | FAUCI’S COVID CHAOS STEALS 2020, RNC CHAIR GRUTERS ON GOP FAITH \| AMERICA'S TOP 10 |
| listicle | @CNN | 4 ways Ukraine changed America’s wars forever |
| listicle | @nypost | Karoline Leavitt to Depart as White House Press Secretary — Top 5 Moments She Shut Down Reporters |
| howto_explainer | @SkyNews | Why Trump is fighting for the Arctic but losing in Antarctica |
| howto_explainer | @PhillipScottPodcast | Latina Explains Why They Didn't Vote For Jasmine Crockett Even Though She Was Pro-Immigration |
| howto_explainer | @oann | Why Rising Prices Could Trigger a Voter Backlash Before the Midterms |
| curiosity_gap | https://rumble.com/c/russellbrand | They don't want you knowing this... |
| curiosity_gap | @CoreyGilShusterAskProject | Palestinians: What happens at the endtimes? |
| curiosity_gap | @LukeBeasley | Actually, what the f*** just happened?! |
| outrage | @LukeBeasley | SHOCK BREAKING: TRUMP S*X BOMBSHELL ERUPTS, PUBLIC MELTDOWN BACKFIRES! |
| outrage | @timesofindia | ‘Humiliated’ Trump Fires EXPLOSIVE WARNING To Canada In Extreme Meltdown \| ‘NO MORE BENEFITS!’ |
| outrage | @BlackConservativePerspective | Leftists PANIC As Wife EXPOSES Another HUMILIATING Scandal Against IMPLODING Communist Democrat! |
| humor | @TimcastIRL | THIS IS HILARIOUS |
| humor | @TimcastNews | THIS IS HILARIOUS |
| humor | @TheQuartering | THIS IS HILARIOUS |


## Stage 4: the landscape

Agglomerative clustering of creators in style space (topic-controlled factor scores, Ward) and topic space (Jensen-Shannon distance between topic mixes, average linkage), k by silhouette; adjusted Rand index against the channel groups and against each other. Run on all titles and on political titles only:


| genre | titles | n_creators | n_groups | style_k | style_silhouette | topic_k | topic_silhouette | ari_style_vs_group | ari_topic_vs_group | ari_style_vs_topic | ari_style_vs_group_k_groups | ari_topic_vs_group_k_groups | ari_style_vs_topic_k_groups |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| videos | all | 236 | 3 | 10 | 0.119 | 3 | 0.170 | 0.044 | 0.004 | 0.001 | -0.010 | 0.004 | -0.002 |
| videos | political | 229 | 3 | 10 | 0.131 | 3 | 0.180 | 0.046 | 0.005 | 0.001 | 0.035 | 0.005 | 0.002 |
| streams | all | 77 | 3 | 11 | 0.165 | 3 | 0.097 | 0.020 | 0.009 | 0.005 | 0.047 | 0.009 | -0.018 |
| streams | political | 76 | 3 | 9 | 0.162 | 4 | 0.069 | 0.043 | -0.014 | 0.027 | 0.026 | 0.000 | -0.024 |


Style cohesion per channel group (mean within-group vs between-group distance in z-scored style space; ratio < 1 = group-mates are closer than average):

| genre | group | n_creators | within_group_distance | between_group_distance | cohesion_ratio |
|---|---|---|---|---|---|
| streams | neutral | 16 | 4.071 | 4.631 | 0.879 |
| streams | left | 33 | 4.436 | 4.678 | 0.948 |
| streams | right | 28 | 5.117 | 4.826 | 1.060 |
| videos | right | 94 | 4.305 | 4.539 | 0.948 |
| videos | neutral | 37 | 4.647 | 4.721 | 0.984 |
| videos | left | 105 | 4.628 | 4.574 | 1.012 |


Where channel group and style disagree (videos, all titles):

| kind | group | n_creators | n_style_clusters | largest_cluster_share | members |
|---|---|---|---|---|---|
| channel group split across style clusters | neutral | 37 | 9 | 0.297 | @KimIversen (S0); @BrittanyVenti (S0); @destinyhqclips (S0); @ClipsCandaceOwens (S0); @JacksonHinkleOfficia... |
| channel group split across style clusters | left | 105 | 10 | 0.324 | https://rumble.com/c/GGreenwald (S0); @Vaush (S0); @TheHumanistReport (S0); @zeteo (S0); @Xanderhal (S0); @... |
| channel group split across style clusters | right | 94 | 8 | 0.340 | https://rumble.com/c/russellbrand (S0); @morebridgetphetasy (S0); @HangOutwithSeanHannity (S0); @RileyGaine... |
| style cluster spanning channel groups | S4 | 3 | 3 | 0.333 | @timesofindia (left); @PiersMorganUncensored (neutral); @jlptalk (right) |
| style cluster spanning channel groups | S7 | 3 | 3 | 0.333 | @aaronparnas1 (left); @TimesNowWorld (neutral); @RSBN (right) |
| style cluster spanning channel groups | S6 | 29 | 3 | 0.448 | @BadFaithPodcast (left); @DannyHaiphongYT (left); @DemocracyNow (left); @JamarlThomas (left); @LeverNews (l... |
| style cluster spanning channel groups | S1 | 26 | 3 | 0.500 | @DailyDenims (left); @DoubleDownNews (left); @LegalAFMTN (left); @LukeBeasley (left); @MeidasTouch (left); ... |
| style cluster spanning channel groups | S3 | 64 | 3 | 0.531 | @BadEmpanadaLive (left); @DropSiteNews (left); @DueDissidence (left); @DylanBurnsLIVE (left); @FarronBalanc... |
| style cluster spanning channel groups | S5 | 20 | 3 | 0.550 | @CNN (left); @NPR (left); @SkyNews (left); @aljazeeraenglish (left); @msnow (left); @thegrayzone7996 (left)... |
| style cluster spanning channel groups | S0 | 52 | 3 | 0.615 | @BreakThroughNews (left); @DemocracyDocket (left); @HasanAbi (left); @HasanabiClips (left); @SMN (left); @T... |
| style cluster spanning channel groups | S2 | 33 | 3 | 0.667 | @EzraKleinShow (left); @GeopoliticalEconomyReport (left); @LeejaMiller (left); @MikeFromPA (left); @NYTPodc... |
| style cluster spanning channel groups | S8 | 5 | 2 | 0.800 | @HasanAbiVODs3 (left); @60minutes (neutral); @Firstpost (neutral); @Forbes (neutral); @chinainsights-r2w (n... |


Who gets named (creator-balanced titles; people keyed by surname, so 'Kirk' pools Charlie and Erika Kirk):

| entity | n_titles_balanced | share_of_balanced_titles | n_creators | share_by_group | outrage_share | overall_outrage_share | outrage_ratio |
|---|---|---|---|---|---|---|---|
| Trump | 7277 | 0.040 | 197 | left (5.6%); neutral (3.7%); right (2.2%) | 0.666 | 0.563 | 1.180 |
| Hegseth | 1054 | 0.006 | 106 | left (0.8%); neutral (0.7%); right (0.2%) | 0.578 | 0.563 | 1.030 |
| Hormuz | 1041 | 0.006 | 85 | neutral (1.0%); left (0.5%); right (0.3%) | 0.492 | 0.563 | 0.870 |
| Putin | 888 | 0.005 | 62 | neutral (0.9%); left (0.5%); right (0.1%) | 0.685 | 0.563 | 1.220 |
| JD Vance | 858 | 0.005 | 120 | left (0.5%); neutral (0.5%); right (0.4%) | 0.570 | 0.563 | 1.010 |
| Charlie Kirk | 744 | 0.004 | 115 | right (0.8%); neutral (0.3%); left (0.2%) | 0.539 | 0.563 | 0.960 |
| Mamdani | 717 | 0.004 | 111 | right (0.7%); neutral (0.3%); left (0.2%) | 0.697 | 0.563 | 1.240 |
| Netanyahu | 708 | 0.004 | 109 | neutral (0.5%); left (0.5%); right (0.2%) | 0.733 | 0.563 | 1.300 |
| Lindsey Graham | 647 | 0.004 | 124 | left (0.4%); neutral (0.4%); right (0.4%) | 0.459 | 0.563 | 0.820 |
| Epstein | 624 | 0.003 | 108 | left (0.4%); neutral (0.4%); right (0.2%) | 0.726 | 0.563 | 1.290 |
| Nancy Guthrie | 579 | 0.003 | 33 | neutral (0.7%); right (0.4%); left (0.0%) | 0.171 | 0.563 | 0.300 |
| Kristi Noem | 536 | 0.003 | 103 | left (0.5%); neutral (0.2%); right (0.2%) | 0.743 | 0.563 | 1.320 |
| Brian Shapiro | 511 | 0.003 | 75 | left (0.5%); right (0.1%); neutral (0.1%) | 0.757 | 0.563 | 1.350 |
| Karoline Leavitt | 479 | 0.003 | 53 | left (0.3%); right (0.2%); neutral (0.2%) | 0.476 | 0.563 | 0.850 |
| Mike Johnson | 477 | 0.003 | 87 | left (0.3%); right (0.2%); neutral (0.2%) | 0.587 | 0.563 | 1.040 |
| Kash Patel | 440 | 0.002 | 86 | left (0.4%); neutral (0.2%); right (0.1%) | 0.775 | 0.563 | 1.380 |
| Jack Smith | 420 | 0.002 | 91 | right (0.3%); left (0.2%); neutral (0.2%) | 0.536 | 0.563 | 0.950 |
| Keir Starmer | 411 | 0.002 | 42 | neutral (0.3%); left (0.3%); right (0.1%) | 0.499 | 0.563 | 0.890 |
| Lindsay Clancy | 408 | 0.002 | 53 | neutral (0.5%); right (0.2%); left (0.0%) | 0.164 | 0.563 | 0.290 |
| Pam Bondi | 403 | 0.002 | 89 | left (0.3%); neutral (0.2%); right (0.1%) | 0.834 | 0.563 | 1.480 |
| Graham Platner | 398 | 0.002 | 100 | left (0.3%); neutral (0.2%); right (0.2%) | 0.595 | 0.563 | 1.060 |
| Marco Rubio | 370 | 0.002 | 84 | neutral (0.4%); left (0.1%); right (0.1%) | 0.403 | 0.563 | 0.720 |
| Hillary Clinton | 352 | 0.002 | 84 | neutral (0.2%); right (0.2%); left (0.1%) | 0.688 | 0.563 | 1.220 |
| Candace Owens | 343 | 0.002 | 64 | right (0.3%); neutral (0.2%); left (0.1%) | 0.703 | 0.563 | 1.250 |
| Stephen Miller | 335 | 0.002 | 75 | left (0.3%); right (0.1%); neutral (0.1%) | 0.672 | 0.563 | 1.190 |


| entity | n_titles_balanced | share_of_balanced_titles | n_creators | share_by_group | outrage_share | overall_outrage_share | outrage_ratio |
|---|---|---|---|---|---|---|---|
| Trump | 8617 | 0.048 | 192 | left (7.1%); neutral (4.5%); right (2.0%) | 0.660 | 0.563 | 1.170 |
| White House | 1502 | 0.008 | 114 | neutral (1.2%); left (0.7%); right (0.7%) | 0.410 | 0.563 | 0.730 |
| GOP | 1462 | 0.008 | 105 | left (1.1%); right (0.7%); neutral (0.5%) | 0.722 | 0.563 | 1.280 |
| MAGA | 973 | 0.005 | 122 | left (1.2%); right (0.1%); neutral (0.1%) | 0.921 | 0.563 | 1.640 |
| Senate | 958 | 0.005 | 97 | neutral (0.9%); right (0.4%); left (0.4%) | 0.364 | 0.563 | 0.650 |
| Supreme Court | 858 | 0.005 | 107 | neutral (0.5%); left (0.5%); right (0.4%) | 0.515 | 0.563 | 0.910 |
| NATO | 826 | 0.005 | 86 | neutral (0.8%); left (0.4%); right (0.2%) | 0.522 | 0.563 | 0.930 |
| FBI | 809 | 0.004 | 115 | right (0.6%); neutral (0.4%); left (0.3%) | 0.714 | 0.563 | 1.270 |
| House | 777 | 0.004 | 95 | neutral (0.7%); left (0.3%); right (0.3%) | 0.395 | 0.563 | 0.700 |
| Congress | 768 | 0.004 | 111 | neutral (0.6%); left (0.4%); right (0.3%) | 0.479 | 0.563 | 0.850 |
| CNN | 563 | 0.003 | 100 | right (0.4%); left (0.4%); neutral (0.1%) | 0.789 | 0.563 | 1.400 |
| DHS | 549 | 0.003 | 68 | neutral (0.5%); right (0.3%); left (0.2%) | 0.424 | 0.563 | 0.750 |
| NASA | 436 | 0.002 | 45 | neutral (0.6%); right (0.1%); left (0.1%) | 0.073 | 0.563 | 0.130 |
| Pentagon | 413 | 0.002 | 73 | neutral (0.4%); left (0.2%); right (0.1%) | 0.387 | 0.563 | 0.690 |
| EU | 392 | 0.002 | 40 | neutral (0.5%); left (0.1%); right (0.1%) | 0.454 | 0.563 | 0.810 |
| World News | 368 | 0.002 | 2 | neutral (0.7%) | 0.750 | 0.563 | 1.330 |
| CIA | 364 | 0.002 | 101 | right (0.3%); left (0.2%); neutral (0.2%) | 0.662 | 0.563 | 1.180 |
| HasanAbi | 347 | 0.002 | 5 | left (0.5%); right (0.0%) | 0.447 | 0.563 | 0.790 |
| BJP | 344 | 0.002 | 4 | neutral (0.7%); left (0.0%) | 0.326 | 0.563 | 0.580 |
| Fed | 315 | 0.002 | 57 | neutral (0.3%); left (0.1%); right (0.1%) | 0.435 | 0.563 | 0.770 |
| Vantage on Firstpost | 310 | 0.002 | 1 | neutral (0.6%) | 0.458 | 0.563 | 0.810 |
| ABC News Live | 305 | 0.002 | 1 | neutral (0.6%) | 0.000 | 0.563 | 0.000 |
| Fox News | 303 | 0.002 | 58 | left (0.4%); right (0.0%); neutral (0.0%) | 0.898 | 0.563 | 1.590 |
| REUTERS | 303 | 0.002 | 4 | neutral (0.6%); left (0.0%) | 0.208 | 0.563 | 0.370 |
| UN | 275 | 0.002 | 49 | neutral (0.3%); left (0.1%); right (0.0%) | 0.480 | 0.563 | 0.850 |


Convergent formulas: 1,477 distinct titles (case-insensitive) are used verbatim by two or more creators, 454 of them by creators from different organizations (the rest are same-outlet cross-posts such as TYT / The Damage Report); of those 454, 62.1% stay within one channel group. 500 masked templates (names and numbers replaced, at least one content word) are shared across organizations; 45.8% within one channel group.


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
| This is terrifying... | 5 | 5 | left; right | @HasanAbi; @TheMajorityReport; @TheQuartering; @TheVaushPit; @TimcastNews |
| Oh.. my.. GOD... | 4 | 8 | left; right | @AsmonTV; @HasanAbi; @JackCocchiarellaShow; @TheQuartering |
| It finally happened | 4 | 6 | left | @HasanAbi; @JackCocchiarellaShow; @LukeBeasley; @adammockler |
| BREAKING: TRUMP FIRES PAM BONDI | 4 | 5 | left | @Vaush; @aaronparnas1; @bulwarkmedia; @podsaveamerica |
| HOLY SH*T.. | 4 | 5 | left; neutral; right | @AsmonTV; @HasanAbi; @JacksonHinkleOfficial; @LiberalHivemind |
| THIS IS HILARIOUS | 4 | 5 | left; right | @MikeFromPA; @TheQuartering; @TimcastIRL; @TimcastNews |
| THIS IS REALLY BAD | 4 | 5 | left; right | @HasanAbi; @JackCocchiarellaShow; @bennyjohnson; @harryjsisson |
| He actually did it.. | 4 | 4 | left; right | @AsmonTV; @Timcast; @TimcastNews; @ponderingpolitics |
| It has begun | 4 | 4 | left; right | @HasanAbi; @Timcast; @TimcastIRL; @TimcastNews |
| It’s getting worse… | 4 | 4 | left; right | @TheQuartering; @TimcastIRL; @adammockler; @ponderingpolitics |
| 🚨They Actually Did It… | 4 | 4 | right | @TheQuartering; @TimcastIRL; @TimcastNews; @bennyjohnson |
| This can't be real.. | 4 | 4 | left; right | @AsmonTV; @RebelNewsOnline; @TimcastIRL; @adammockler |
| THIS COULD CHANGE EVERYTHING | 4 | 4 | right | @RealAmericasVoice; @TimcastIRL; @TimcastNews; https://rumble.com/c/russellbrand |
| THIS IS CRAZY | 4 | 4 | left; right | @HasanAbi; @TheQuartering; @TimcastIRL; @TimcastNews |
| This is so embarrassing.. | 4 | 4 | left; right | @AsmonTV; @TheYoungTurks; @destiny; @harryjsisson |
| TRUMP JUST LOST IT! | 4 | 4 | left | @FarronBalanced; @JackCocchiarellaShow; @LukeBeasley; @MeidasTouch |
| We need to talk about this.. | 4 | 4 | left; right | @AsmonTV; @TheQuartering; @TheVaushPit; @therationalnational |


| template | n_creators | n_titles | groups | example |
|---|---|---|---|---|
| <ENT> 's <ENT> | 61 | 142 | left; neutral; right | Iran's Plan To Make You SIMP |
| <ENT> after <ENT> | 35 | 67 | left; neutral; right | Trump’s Envoys Get RUDE AWAKENING After Putin Meeting |
| <ENT> 's <ENT> <ENT> | 23 | 39 | left; neutral; right | California's Election Shakeup + Microsoft's AI Spy Badge \| PBD #811 |
| <ENT> ’s <ENT> | 17 | 27 | left; neutral; right | AIPAC’s "Elect Chicago Women" Super PAC Exposed |
| <ENT> exposes <ENT> | 14 | 19 | left; right | Elizabeth Warren Exposes Trump’s Fed Pick In Brutal Hearing |
| <ENT> <ENT> 's <ENT> | 13 | 19 | left; neutral; right | US Media's Hasan Piker Derangement Syndrome Is Ridiculous |
| <ENT> <ENT> after <ENT> | 12 | 13 | left; neutral; right | OMG: Trump RUSHES OFF after Going to HOSPITAL! |
| <ENT> after <ENT> <ENT> | 11 | 16 | left; neutral; right | Hakeem Jeffries In Full Panic Mode After Kushner Meeting Pisses Off Democrats |
| <ENT> <ENT> w/ <ENT> | 10 | 20 | left; neutral; right | "It Went Completely Viral" Brett Cooper Talks Internet Drama & Pendragon Cycle W/ Michael Knowles |
| <ENT> says <ENT> | 10 | 16 | left; neutral; right | Fox News Lunatic Says Americans Have Data Center Derangement Syndrome |
| <ENT> 's <ENT> in <ENT> | 10 | 13 | left; neutral; right | AOC's DISASTROUS Foreign Policy Debut In Munich |
| <ENT> w/ <ENT> | 8 | 35 | left; neutral; right | Trump’s Ballroom Obsession Has Gone Totally Off the Rails (w/ Ben Terris) |
| <ENT> <ENT> 's <ENT> <ENT> | 8 | 10 | left; neutral; right | Bill Kristol: MAGA's Grievance Culture \| The Bulwark Podcast |
| <ENT> on <ENT> 's <ENT> | 8 | 10 | left; neutral; right | Aaron Rodgers Torched Fauci on ESPN's Own Air |
| <ENT> vs. <ENT> | 8 | 8 | left; right | Ben Shapiro vs. Fortnite |
| the truth about <ENT> | 8 | 8 | left; right | The truth about Blizzard |
| <ENT> on live tv | 7 | 10 | left | Epstein Victim-Smearer Humiliated On Live TV |
| <ENT> under the bus | 7 | 8 | left | Dems Throw Trans Folks Under The Bus |
| <ENT> is here | 7 | 7 | left; neutral; right | The Radical Left’s Hostile Takeover Is Here |
| <ENT> destroys <ENT> | 6 | 7 | left; right | Jesse Watters DESTROYS Abdul El-Sayed |
| <ENT> ft # <ENT> | 6 | 7 | left; neutral; right | Catholic & Protestant Debunk Islam & Atheist Arguments \| ft. Billy Hallowell |
| <ENT> against <ENT> | 6 | 6 | left; neutral; right | Ben Shapiro Lobs WILD Accusation Against Dave Smith |
| <ENT> off on <ENT> | 6 | 6 | left; right | Adam Conover GOES OFF on Tech Companies & A.I. |
| <ENT> senator <ENT> | 6 | 6 | left; neutral; right | Republican Senator SLAMS Trump |
| <ENT> panic as <ENT> | 5 | 13 | left; right | Republicans PANIC as Reporters Fact-Check Them LIVE! |


## Stage 5: time and engagement

Monthly drift, January-September (September is 1-14 and never compared on volume). Channel-group trends with |Spearman| >= 0.6 and p < 0.05 over the nine months (13 of 90 group x genre x measure series):


| group | genre | measure | spearman_trend | p | first_month_value | last_full_month_value |
|---|---|---|---|---|---|---|
| right | videos | humor | -0.883 | 0.002 | 0.003 | 0.002 |
| neutral | streams | F3_controlled | -0.767 | 0.016 | 1.634 | 1.288 |
| left | videos | outrage | -0.683 | 0.042 | 0.702 | 0.654 |
| left | videos | F2_controlled | 0.700 | 0.036 | -0.152 | -0.095 |
| left | streams | F10_controlled | 0.733 | 0.025 | -0.525 | -0.382 |
| left | videos | F4_controlled | 0.733 | 0.025 | 0.003 | 0.053 |
| left | streams | F4_controlled | 0.783 | 0.013 | -0.202 | -0.006 |
| left | videos | curiosity_gap | 0.783 | 0.013 | 0.035 | 0.041 |
| neutral | videos | F5_controlled | 0.833 | 0.005 | -0.086 | 0.271 |
| neutral | streams | F10_controlled | 0.850 | 0.004 | -0.670 | -0.453 |
| neutral | videos | F2_controlled | 0.900 | 0.001 | -0.270 | -0.058 |
| right | videos | F8_controlled | 0.900 | 0.001 | -0.129 | -0.071 |
| neutral | streams | F8_controlled | 0.917 | 0.001 | 0.011 | 0.390 |


Month-to-month topic change (mean Jensen-Shannon distance between a creator's consecutive monthly topic mixes; videos):

| group | 2026-02 | 2026-03 | 2026-04 | 2026-05 | 2026-06 | 2026-07 | 2026-08 | 2026-09 |
|---|---|---|---|---|---|---|---|---|
| left | 0.68 | 0.69 | 0.64 | 0.65 | 0.63 | 0.64 | 0.63 | 0.64 |
| neutral | 0.59 | 0.60 | 0.54 | 0.57 | 0.54 | 0.51 | 0.53 | 0.59 |
| right | 0.72 | 0.71 | 0.68 | 0.68 | 0.67 | 0.68 | 0.67 | 0.68 |


Engagement, within creator (OLS of log views on standardized title predictors with month and topic controls, HC3; views are a fetch-time snapshot that favors older videos):


| genre | predictor | n_creators | median_coef_per_sd | q25 | q75 | share_positive | share_sig_positive | share_sig_negative | share_same_sign_as_median | median_r2 |
|---|---|---|---|---|---|---|---|---|---|---|
| streams | F1 | 56.000 | -0.016 | -0.073 | 0.005 | 0.304 | 0.018 | 0.036 | 0.696 | 0.398 |
| streams | F10 | 56.000 | 0.014 | -0.022 | 0.042 | 0.554 | 0.018 | 0.071 | 0.554 | 0.398 |
| streams | F11 | 56.000 | 0.017 | -0.022 | 0.048 | 0.625 | 0.054 | 0.018 | 0.625 | 0.398 |
| streams | F12 | 56.000 | 0.001 | -0.028 | 0.030 | 0.500 | 0.036 | 0.054 | 0.500 | 0.398 |
| streams | F2 | 56.000 | 0.007 | -0.017 | 0.034 | 0.589 | 0.071 | 0.036 | 0.589 | 0.398 |
| streams | F3 | 56.000 | 0.003 | -0.032 | 0.053 | 0.554 | 0.089 | 0.107 | 0.554 | 0.398 |
| streams | F4 | 56.000 | 0.011 | -0.021 | 0.040 | 0.607 | 0.125 | 0.018 | 0.607 | 0.398 |
| streams | F5 | 56.000 | 0.003 | -0.047 | 0.048 | 0.554 | 0.071 | 0.054 | 0.554 | 0.398 |
| streams | F6 | 56.000 | 0.019 | -0.006 | 0.080 | 0.661 | 0.143 | 0.071 | 0.661 | 0.398 |
| streams | F7 | 56.000 | -0.005 | -0.051 | 0.020 | 0.464 | 0.018 | 0.125 | 0.536 | 0.398 |
| streams | F8 | 56.000 | 0.003 | -0.025 | 0.046 | 0.500 | 0.089 | 0.054 | 0.500 | 0.398 |
| streams | F9 | 56.000 | 0.011 | -0.029 | 0.041 | 0.571 | 0.036 | 0.018 | 0.571 | 0.398 |
| streams | curiosity_gap | 52.000 | 0.001 | -0.018 | 0.026 | 0.519 | 0.096 | 0.058 | 0.519 | 0.392 |
| streams | humor | 13.000 | 0.006 | -0.001 | 0.017 | 0.615 | 0.000 | 0.000 | 0.615 | 0.385 |
| streams | n_tokens | 56.000 | -0.006 | -0.049 | 0.048 | 0.446 | 0.089 | 0.071 | 0.554 | 0.398 |
| streams | outrage | 56.000 | 0.047 | 0.017 | 0.097 | 0.839 | 0.161 | 0.000 | 0.839 | 0.398 |
| videos | F1 | 188.000 | -0.022 | -0.065 | 0.021 | 0.356 | 0.043 | 0.149 | 0.644 | 0.285 |
| videos | F10 | 188.000 | -0.008 | -0.047 | 0.031 | 0.441 | 0.032 | 0.112 | 0.559 | 0.285 |
| videos | F11 | 188.000 | -0.007 | -0.056 | 0.041 | 0.468 | 0.064 | 0.117 | 0.532 | 0.285 |
| videos | F12 | 188.000 | -0.031 | -0.095 | 0.008 | 0.287 | 0.032 | 0.160 | 0.713 | 0.285 |
| videos | F2 | 188.000 | 0.014 | -0.025 | 0.066 | 0.606 | 0.096 | 0.048 | 0.606 | 0.285 |
| videos | F3 | 188.000 | -0.003 | -0.050 | 0.037 | 0.473 | 0.085 | 0.096 | 0.527 | 0.285 |
| videos | F4 | 188.000 | 0.018 | -0.011 | 0.056 | 0.681 | 0.128 | 0.032 | 0.681 | 0.285 |
| videos | F5 | 188.000 | -0.022 | -0.060 | 0.018 | 0.383 | 0.053 | 0.106 | 0.617 | 0.285 |
| videos | F6 | 188.000 | 0.025 | -0.015 | 0.077 | 0.628 | 0.154 | 0.027 | 0.628 | 0.285 |
| videos | F7 | 188.000 | -0.018 | -0.069 | 0.019 | 0.372 | 0.064 | 0.101 | 0.628 | 0.285 |
| videos | F8 | 188.000 | -0.007 | -0.053 | 0.034 | 0.447 | 0.059 | 0.106 | 0.553 | 0.285 |
| videos | F9 | 188.000 | 0.018 | -0.020 | 0.060 | 0.644 | 0.096 | 0.037 | 0.644 | 0.285 |
| videos | curiosity_gap | 185.000 | 0.008 | -0.022 | 0.038 | 0.578 | 0.054 | 0.011 | 0.578 | 0.281 |
| videos | humor | 89.000 | 0.008 | -0.025 | 0.025 | 0.528 | 0.101 | 0.045 | 0.528 | 0.254 |
| videos | n_tokens | 188.000 | 0.010 | -0.051 | 0.067 | 0.548 | 0.160 | 0.096 | 0.548 | 0.285 |
| videos | outrage | 188.000 | 0.038 | 0.003 | 0.094 | 0.755 | 0.229 | 0.005 | 0.755 | 0.285 |


The outrage effect by channel group (videos):

| group | n_creators | median_coef_per_sd | q25 | q75 | share_positive | share_sig_positive | share_sig_negative |
|---|---|---|---|---|---|---|---|
| left | 84.000 | 0.041 | 0.005 | 0.094 | 0.762 | 0.202 | 0.000 |
| neutral | 32.000 | 0.074 | 0.029 | 0.107 | 0.875 | 0.406 | 0.000 |
| right | 72.000 | 0.020 | -0.014 | 0.086 | 0.694 | 0.181 | 0.014 |


Hit concentration (creator x genre with >= 100 videos carrying views):

| genre | n_creators | median_gini | median_top10_share | median_top1_share | powerlaw_like | median_alpha |
|---|---|---|---|---|---|---|
| streams | 57 | 0.363 | 0.298 | 0.072 | 0.018 | 2.754 |
| videos | 188 | 0.515 | 0.394 | 0.095 | 0.000 | 2.702 |


Concentration vs style, pooled within channel group (group-demeaned Spearman across creators):

| genre | target | predictor | n_creators | spearman_r | p |
|---|---|---|---|---|---|
| streams | gini | F10_controlled | 57 | -0.038 | 0.778 |
| streams | gini | F11_controlled | 57 | -0.118 | 0.381 |
| streams | gini | F12_controlled | 57 | 0.025 | 0.851 |
| streams | gini | F1_controlled | 57 | 0.385 | 0.003 |
| streams | gini | F2_controlled | 57 | -0.045 | 0.742 |
| streams | gini | F3_controlled | 57 | 0.440 | 0.001 |
| streams | gini | F4_controlled | 57 | -0.007 | 0.957 |
| streams | gini | F5_controlled | 57 | -0.169 | 0.210 |
| streams | gini | F6_controlled | 57 | -0.090 | 0.504 |
| streams | gini | F7_controlled | 57 | 0.263 | 0.049 |
| streams | gini | F8_controlled | 57 | -0.050 | 0.711 |
| streams | gini | F9_controlled | 57 | 0.065 | 0.633 |
| streams | gini | curiosity_gap | 57 | -0.160 | 0.236 |
| streams | gini | humor | 57 | 0.026 | 0.850 |
| streams | gini | log_n_videos | 57 | 0.303 | 0.022 |
| streams | gini | log_subscribers | 57 | 0.336 | 0.011 |
| streams | gini | outrage | 57 | -0.447 | 0.001 |
| streams | top10_share | F10_controlled | 57 | -0.046 | 0.736 |
| streams | top10_share | F11_controlled | 57 | -0.146 | 0.279 |
| streams | top10_share | F12_controlled | 57 | 0.025 | 0.856 |
| streams | top10_share | F1_controlled | 57 | 0.419 | 0.001 |
| streams | top10_share | F2_controlled | 57 | -0.045 | 0.742 |
| streams | top10_share | F3_controlled | 57 | 0.395 | 0.002 |
| streams | top10_share | F4_controlled | 57 | 0.011 | 0.935 |
| streams | top10_share | F5_controlled | 57 | -0.117 | 0.387 |
| streams | top10_share | F6_controlled | 57 | -0.127 | 0.345 |
| streams | top10_share | F7_controlled | 57 | 0.278 | 0.036 |
| streams | top10_share | F8_controlled | 57 | -0.056 | 0.681 |
| streams | top10_share | F9_controlled | 57 | 0.010 | 0.939 |
| streams | top10_share | curiosity_gap | 57 | -0.124 | 0.358 |
| streams | top10_share | humor | 57 | 0.046 | 0.733 |
| streams | top10_share | log_n_videos | 57 | 0.258 | 0.052 |
| streams | top10_share | log_subscribers | 57 | 0.340 | 0.010 |
| streams | top10_share | outrage | 57 | -0.458 | 0.000 |
| videos | gini | F10_controlled | 188 | 0.267 | 0.000 |
| videos | gini | F11_controlled | 188 | 0.174 | 0.017 |
| videos | gini | F12_controlled | 188 | 0.234 | 0.001 |
| videos | gini | F1_controlled | 188 | 0.214 | 0.003 |
| videos | gini | F2_controlled | 188 | 0.035 | 0.629 |
| videos | gini | F3_controlled | 188 | -0.027 | 0.713 |
| videos | gini | F4_controlled | 188 | -0.085 | 0.248 |
| videos | gini | F5_controlled | 188 | 0.272 | 0.000 |
| videos | gini | F6_controlled | 188 | 0.149 | 0.041 |
| videos | gini | F7_controlled | 188 | 0.067 | 0.359 |
| videos | gini | F8_controlled | 188 | 0.204 | 0.005 |
| videos | gini | F9_controlled | 188 | -0.145 | 0.047 |
| videos | gini | curiosity_gap | 188 | -0.210 | 0.004 |
| videos | gini | humor | 188 | -0.041 | 0.580 |
| videos | gini | log_n_videos | 188 | 0.177 | 0.015 |
| videos | gini | log_subscribers | 188 | 0.008 | 0.910 |
| videos | gini | outrage | 188 | -0.467 | 0.000 |
| videos | top10_share | F10_controlled | 188 | 0.265 | 0.000 |
| videos | top10_share | F11_controlled | 188 | 0.177 | 0.015 |
| videos | top10_share | F12_controlled | 188 | 0.205 | 0.005 |
| videos | top10_share | F1_controlled | 188 | 0.230 | 0.002 |
| videos | top10_share | F2_controlled | 188 | 0.043 | 0.560 |
| videos | top10_share | F3_controlled | 188 | -0.054 | 0.463 |
| videos | top10_share | F4_controlled | 188 | -0.110 | 0.134 |
| videos | top10_share | F5_controlled | 188 | 0.258 | 0.000 |
| videos | top10_share | F6_controlled | 188 | 0.136 | 0.063 |
| videos | top10_share | F7_controlled | 188 | 0.068 | 0.351 |
| videos | top10_share | F8_controlled | 188 | 0.191 | 0.009 |
| videos | top10_share | F9_controlled | 188 | -0.149 | 0.041 |
| videos | top10_share | curiosity_gap | 188 | -0.204 | 0.005 |
| videos | top10_share | humor | 188 | -0.037 | 0.611 |
| videos | top10_share | log_n_videos | 188 | 0.158 | 0.031 |
| videos | top10_share | log_subscribers | 188 | -0.024 | 0.745 |
| videos | top10_share | outrage | 188 | -0.456 | 0.000 |


## Stage 6b: Zipf's law and views over time (document 7)

Zipf exponents per system (tokens with stopwords; OLS of log frequency on log rank; size-matched = 20 draws of 2,000 titles, top 200 ranks):

| grouping | system | n_titles | n_tokens | n_types | tokens_per_title | zipf_top100 | zipf_top1000 | zipf_top5000 | zipf_r2_top1000 | zipf_size_matched | zipf_size_matched_sd | top1_share | top_10 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| corpus | all edited uploads (balanced) | 150571 | 1566114 | 48201 | 10.4000 | 0.8585 | 0.7848 | 1.0155 | 0.9953 | 0.8188 | 0.0076 | 0.0244 | the trump to in on of s is iran as |
| channel_group | left | 62517 | 596492 | 26294 | 9.5400 | 0.8576 | 0.8246 | 1.0872 | 0.9959 | 0.8118 | 0.0087 | 0.0381 | trump the to in as on s is iran of |
| channel_group | neutral | 38562 | 438415 | 28428 | 11.3700 | 0.8491 | 0.7993 | 1.0080 | 0.9947 | 0.8061 | 0.0078 | 0.0199 | in to the of trump iran on s for us |
| channel_group | right | 49492 | 531207 | 27335 | 10.7300 | 0.8312 | 0.7869 | 1.0236 | 0.9959 | 0.7963 | 0.0065 | 0.0336 | the to in is of trump on and a s |
| title_label | left | 2585 | 28077 | 6598 | 10.8600 | 0.8529 | 0.7840 | 0.9616 | 0.9930 | 0.8164 | 0.0036 | 0.0261 | trump the to in s on of iran as for |
| title_label | right | 2149 | 22134 | 6218 | 10.3000 | 0.8312 | 0.7722 | 0.8875 | 0.9932 | 0.8183 | 0.0024 | 0.0244 | the to trump s in on is of iran a |
| title_label | neither | 5967 | 62982 | 10934 | 10.5600 | 0.8370 | 0.7846 | 0.9596 | 0.9954 | 0.8039 | 0.0067 | 0.0217 | the trump to in s on of iran is for |
| caps_style | all_caps | 3820 | 23184 | 4561 | 6.0700 | 0.7706 | 0.8769 | 0.9762 | 0.9944 | 0.8006 | 0.0086 | 0.0260 | the is trump this to it they in iran just |
| caps_style | selective_caps | 53681 | 560301 | 25997 | 10.4400 | 0.8096 | 0.7950 | 1.0695 | 0.9966 | 0.7880 | 0.0074 | 0.0324 | trump the to in as on s is of iran |
| caps_style | title_case | 52673 | 537961 | 29813 | 10.2100 | 0.8359 | 0.7999 | 1.0188 | 0.9960 | 0.8201 | 0.0082 | 0.0338 | the trump to s in on of is and a |
| caps_style | sentence_case | 39304 | 440474 | 28309 | 11.2100 | 0.8627 | 0.7989 | 1.0134 | 0.9951 | 0.8083 | 0.0088 | 0.0219 | to in the of trump on iran and s for |
| caps_style | mixed_other | 272 | 1906 | 810 | 7.0100 | 0.7595 | 0.6930 | 0.6930 | 0.9173 |  |  | 0.0472 | this is the to f i it a you just |
| caps_style | short_other | 821 | 2288 | 770 | 2.7900 | 0.9773 | 0.7576 | 0.7576 | 0.8697 |  |  | 0.0612 | 26 episode full 2026 hasanabi bloomberg surveillance 4 5 1 |


Creator-level Zipf / Heaps and the views rank-size slopes per channel group and per dominant capitalization style:

| grouping | group | n_creators | zipf_words_top200_mean | zipf_words_top200_median | n_creators_1500 | zipf_words_1500_mean | heaps_beta_1500_mean | top1_word_share_mean | n_creators_with_views | zipf_views_all_median | zipf_views_head_median | gini_median | top10_share_median | powerlaw_like_share | caps_any_mean |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| channel_group | left | 105 | 0.792 | 0.788 | 72 | 0.724 | 0.810 | 0.051 | 84 | 0.880 | 0.433 | 0.494 | 0.378 | 0.000 | 0.372 |
| channel_group | neutral | 37 | 0.792 | 0.807 | 26 | 0.713 | 0.838 | 0.043 | 32 | 1.257 | 0.597 | 0.671 | 0.537 | 0.000 | 0.179 |
| channel_group | right | 94 | 0.750 | 0.752 | 67 | 0.691 | 0.826 | 0.046 | 72 | 0.899 | 0.435 | 0.496 | 0.373 | 0.000 | 0.396 |
| dominant_caps_style | all_caps | 7 | 0.745 | 0.743 | 5 | 0.698 | 0.808 | 0.037 | 5 | 0.591 | 0.311 | 0.352 | 0.256 | 0.000 | 0.780 |
| dominant_caps_style | selective_caps | 72 | 0.786 | 0.794 | 62 | 0.704 | 0.807 | 0.045 | 62 | 0.764 | 0.387 | 0.459 | 0.343 | 0.000 | 0.748 |
| dominant_caps_style | title_case | 127 | 0.757 | 0.754 | 77 | 0.712 | 0.827 | 0.050 | 95 | 0.961 | 0.485 | 0.539 | 0.415 | 0.000 | 0.170 |
| dominant_caps_style | sentence_case | 29 | 0.830 | 0.838 | 21 | 0.716 | 0.842 | 0.041 | 25 | 1.245 | 0.635 | 0.682 | 0.557 | 0.000 | 0.064 |


Views by publication month (edited uploads, YouTube, unique titles): median views, the median over channels of the channel's median, and log views relative to the same channel's mean that month:

| grouping | group | month | n_videos | n_creators | median_views | creator_median_views | mean_log_views | relative_log_views | relative_log_views_se |
|---|---|---|---|---|---|---|---|---|---|
| channel_group | left | 2026-01 | 9111 | 102 | 62000.000 | 58000.000 | 10.896 | -0.000 | 0.011 |
| channel_group | left | 2026-02 | 8471 | 101 | 57000.000 | 52000.000 | 10.785 | 0.000 | 0.012 |
| channel_group | left | 2026-03 | 9849 | 100 | 75000.000 | 60750.000 | 11.065 | -0.000 | 0.011 |
| channel_group | left | 2026-04 | 9606 | 102 | 59000.000 | 49750.000 | 10.852 | 0.000 | 0.011 |
| channel_group | left | 2026-05 | 9159 | 103 | 41000.000 | 40000.000 | 10.509 | -0.000 | 0.011 |
| channel_group | left | 2026-06 | 9308 | 103 | 42000.000 | 43000.000 | 10.495 | 0.000 | 0.012 |
| channel_group | left | 2026-07 | 9641 | 103 | 42000.000 | 53000.000 | 10.512 | -0.000 | 0.011 |
| channel_group | left | 2026-08 | 9277 | 103 | 50000.000 | 50500.000 | 10.698 | 0.000 | 0.011 |
| channel_group | left | 2026-09 | 4098 | 101 | 69000.000 | 79000.000 | 11.017 | 0.000 | 0.017 |
| channel_group | left | all | 78520 | 104 | 54000.000 | 49500.000 | 10.743 | -0.000 | 0.004 |
| channel_group | neutral | 2026-01 | 10903 | 35 | 9900.000 | 21500.000 | 9.301 | -0.000 | 0.014 |
| channel_group | neutral | 2026-02 | 10362 | 35 | 10000.000 | 20000.000 | 9.338 | 0.000 | 0.015 |
| channel_group | neutral | 2026-03 | 11857 | 34 | 11000.000 | 20500.000 | 9.425 | -0.000 | 0.014 |
| channel_group | neutral | 2026-04 | 11136 | 35 | 8400.000 | 13000.000 | 9.188 | 0.000 | 0.014 |
| channel_group | neutral | 2026-05 | 10889 | 35 | 8100.000 | 21000.000 | 9.085 | 0.000 | 0.014 |
| channel_group | neutral | 2026-06 | 11144 | 35 | 7100.000 | 14000.000 | 8.971 | -0.000 | 0.014 |
| channel_group | neutral | 2026-07 | 11343 | 35 | 7000.000 | 17000.000 | 8.944 | -0.000 | 0.013 |
| channel_group | neutral | 2026-08 | 10471 | 35 | 8200.000 | 23000.000 | 9.095 | -0.000 | 0.013 |
| channel_group | neutral | 2026-09 | 5149 | 36 | 11000.000 | 24000.000 | 9.530 | 0.000 | 0.019 |
| channel_group | neutral | all | 93254 | 37 | 8800.000 | 22000.000 | 9.189 | -0.000 | 0.005 |
| channel_group | right | 2026-01 | 6994 | 88 | 34500.000 | 24500.000 | 10.170 | -0.000 | 0.013 |
| channel_group | right | 2026-02 | 6662 | 89 | 32000.000 | 23000.000 | 10.071 | -0.000 | 0.014 |
| channel_group | right | 2026-03 | 7510 | 88 | 32000.000 | 30500.000 | 10.107 | -0.000 | 0.013 |
| channel_group | right | 2026-04 | 6883 | 89 | 35000.000 | 24500.000 | 10.285 | 0.000 | 0.014 |
| channel_group | right | 2026-05 | 6816 | 89 | 29000.000 | 20000.000 | 10.154 | 0.000 | 0.013 |
| channel_group | right | 2026-06 | 6705 | 90 | 29000.000 | 17250.000 | 10.142 | 0.000 | 0.014 |
| channel_group | right | 2026-07 | 6882 | 89 | 28000.000 | 17000.000 | 10.163 | 0.000 | 0.013 |
| channel_group | right | 2026-08 | 6727 | 89 | 31000.000 | 25000.000 | 10.244 | 0.000 | 0.014 |
| channel_group | right | 2026-09 | 3000 | 87 | 45000.000 | 48000.000 | 10.620 | 0.000 | 0.019 |
| channel_group | right | all | 58179 | 90 | 32000.000 | 20750.000 | 10.190 | 0.000 | 0.005 |
| title_label | left | 2026-01 | 275 | 68 | 39000.000 | 66500.000 | 10.085 | -0.012 | 0.074 |
| title_label | left | 2026-02 | 343 | 73 | 22000.000 | 68000.000 | 9.834 | -0.008 | 0.058 |
| title_label | left | 2026-03 | 326 | 68 | 21000.000 | 76750.000 | 9.927 | 0.065 | 0.064 |
| title_label | left | 2026-04 | 330 | 70 | 32000.000 | 66500.000 | 10.163 | 0.031 | 0.065 |
| title_label | left | 2026-05 | 241 | 59 | 27000.000 | 38000.000 | 10.120 | 0.049 | 0.064 |
| title_label | left | 2026-06 | 273 | 71 | 31000.000 | 51000.000 | 10.201 | 0.019 | 0.064 |
| title_label | left | 2026-07 | 368 | 60 | 25000.000 | 38000.000 | 10.138 | 0.014 | 0.058 |
| title_label | left | 2026-08 | 209 | 59 | 60000.000 | 53000.000 | 10.759 | 0.034 | 0.061 |
| title_label | left | 2026-09 | 123 | 46 | 47000.000 | 46000.000 | 10.689 | -0.043 | 0.087 |
| title_label | left | all | 2488 | 139 | 31000.000 | 57500.000 | 10.150 | 0.020 | 0.022 |
| title_label | right | 2026-01 | 254 | 50 | 19500.000 | 45000.000 | 9.680 | 0.058 | 0.078 |
| title_label | right | 2026-02 | 186 | 50 | 30000.000 | 81000.000 | 9.963 | 0.066 | 0.096 |
| title_label | right | 2026-03 | 218 | 49 | 26500.000 | 49500.000 | 9.623 | 0.048 | 0.082 |
| title_label | right | 2026-04 | 240 | 49 | 33000.000 | 48900.000 | 10.023 | 0.008 | 0.077 |
| title_label | right | 2026-05 | 263 | 45 | 13000.000 | 37500.000 | 9.434 | 0.001 | 0.086 |
| title_label | right | 2026-06 | 251 | 58 | 12000.000 | 26500.000 | 9.575 | -0.147 | 0.075 |
| title_label | right | 2026-07 | 260 | 55 | 36000.000 | 43000.000 | 10.122 | 0.019 | 0.068 |
| title_label | right | 2026-08 | 209 | 58 | 37000.000 | 50250.000 | 10.221 | -0.004 | 0.071 |
| title_label | right | 2026-09 | 144 | 32 | 17000.000 | 87500.000 | 9.686 | -0.069 | 0.108 |
| title_label | right | all | 2025 | 122 | 24000.000 | 39000.000 | 9.809 | -0.002 | 0.027 |
| title_label | neither | 2026-01 | 645 | 105 | 27000.000 | 48500.000 | 10.002 | 0.081 | 0.051 |
| title_label | neither | 2026-02 | 670 | 109 | 30000.000 | 64000.000 | 9.954 | 0.034 | 0.045 |
| title_label | neither | 2026-03 | 613 | 111 | 21000.000 | 61000.000 | 9.834 | -0.010 | 0.049 |
| title_label | neither | 2026-04 | 791 | 93 | 20000.000 | 40500.000 | 9.713 | -0.050 | 0.043 |
| title_label | neither | 2026-05 | 626 | 114 | 19000.000 | 36500.000 | 9.711 | 0.007 | 0.049 |
| title_label | neither | 2026-06 | 622 | 114 | 39000.000 | 42500.000 | 10.331 | 0.013 | 0.042 |
| title_label | neither | 2026-07 | 733 | 107 | 27000.000 | 38500.000 | 10.071 | -0.029 | 0.041 |
| title_label | neither | 2026-08 | 589 | 110 | 30000.000 | 40250.000 | 10.185 | 0.040 | 0.047 |
| title_label | neither | 2026-09 | 339 | 82 | 24000.000 | 48000.000 | 10.057 | -0.030 | 0.069 |
| title_label | neither | all | 5628 | 204 | 26000.000 | 33000.000 | 9.973 | 0.006 | 0.016 |
| caps_style | all_caps | 2026-01 | 353 | 31 | 112000.000 | 109000.000 | 10.556 | 0.043 | 0.041 |
| caps_style | all_caps | 2026-02 | 326 | 36 | 108000.000 | 76000.000 | 11.285 | 0.040 | 0.044 |
| caps_style | all_caps | 2026-03 | 500 | 40 | 54500.000 | 96750.000 | 9.740 | 0.064 | 0.038 |
| caps_style | all_caps | 2026-04 | 492 | 37 | 57000.000 | 87000.000 | 9.733 | 0.013 | 0.048 |
| caps_style | all_caps | 2026-05 | 405 | 31 | 34000.000 | 56000.000 | 9.638 | 0.017 | 0.049 |
| caps_style | all_caps | 2026-06 | 340 | 29 | 73000.000 | 103000.000 | 10.679 | 0.046 | 0.043 |
| caps_style | all_caps | 2026-07 | 318 | 30 | 71000.000 | 103750.000 | 10.897 | 0.045 | 0.039 |
| caps_style | all_caps | 2026-08 | 321 | 28 | 83000.000 | 80500.000 | 11.010 | 0.033 | 0.038 |
| caps_style | all_caps | 2026-09 | 106 | 30 | 147000.000 | 121000.000 | 11.376 | 0.009 | 0.065 |
| caps_style | all_caps | all | 3161 | 72 | 72000.000 | 56250.000 | 10.378 | 0.036 | 0.015 |
| caps_style | selective_caps | 2026-01 | 8131 | 187 | 58000.000 | 42000.000 | 10.720 | 0.036 | 0.012 |
| caps_style | selective_caps | 2026-02 | 7728 | 185 | 51000.000 | 38000.000 | 10.565 | 0.053 | 0.012 |
| caps_style | selective_caps | 2026-03 | 8755 | 189 | 63000.000 | 46000.000 | 10.779 | 0.058 | 0.011 |
| caps_style | selective_caps | 2026-04 | 8515 | 193 | 55000.000 | 34000.000 | 10.726 | 0.064 | 0.012 |
| caps_style | selective_caps | 2026-05 | 8660 | 194 | 39000.000 | 31750.000 | 10.386 | 0.039 | 0.011 |
| caps_style | selective_caps | 2026-06 | 8466 | 193 | 40000.000 | 33000.000 | 10.365 | 0.034 | 0.012 |
| caps_style | selective_caps | 2026-07 | 8714 | 192 | 39000.000 | 30000.000 | 10.313 | 0.025 | 0.012 |
| caps_style | selective_caps | 2026-08 | 8881 | 190 | 45000.000 | 39500.000 | 10.473 | 0.040 | 0.011 |
| caps_style | selective_caps | 2026-09 | 3902 | 166 | 62000.000 | 61750.000 | 10.751 | 0.059 | 0.017 |
| caps_style | selective_caps | all | 71752 | 244 | 49000.000 | 33500.000 | 10.551 | 0.044 | 0.004 |
| caps_style | title_case | 2026-01 | 7841 | 223 | 20000.000 | 41000.000 | 9.786 | -0.002 | 0.014 |
| caps_style | title_case | 2026-02 | 7537 | 226 | 17000.000 | 40250.000 | 9.689 | -0.036 | 0.015 |
| caps_style | title_case | 2026-03 | 8561 | 230 | 20000.000 | 40000.000 | 9.835 | -0.032 | 0.014 |
| caps_style | title_case | 2026-04 | 8295 | 237 | 18000.000 | 36500.000 | 9.804 | -0.027 | 0.014 |
| caps_style | title_case | 2026-05 | 8317 | 229 | 14000.000 | 29000.000 | 9.604 | -0.013 | 0.014 |
| caps_style | title_case | 2026-06 | 8911 | 230 | 13000.000 | 26500.000 | 9.511 | -0.004 | 0.014 |
| caps_style | title_case | 2026-07 | 9165 | 235 | 12000.000 | 27000.000 | 9.511 | -0.004 | 0.013 |
| caps_style | title_case | 2026-08 | 8537 | 232 | 15000.000 | 35750.000 | 9.713 | -0.007 | 0.013 |
| caps_style | title_case | 2026-09 | 3999 | 208 | 23000.000 | 50750.000 | 10.086 | -0.018 | 0.019 |
| caps_style | title_case | all | 71163 | 260 | 16000.000 | 32500.000 | 9.701 | -0.015 | 0.005 |
| caps_style | sentence_case | 2026-01 | 10726 | 96 | 17000.000 | 31500.000 | 9.754 | -0.029 | 0.013 |
| caps_style | sentence_case | 2026-02 | 9923 | 90 | 17000.000 | 33750.000 | 9.788 | -0.017 | 0.014 |
| caps_style | sentence_case | 2026-03 | 11385 | 103 | 19000.000 | 43750.000 | 9.934 | -0.025 | 0.013 |
| caps_style | sentence_case | 2026-04 | 10316 | 93 | 15000.000 | 29000.000 | 9.681 | -0.035 | 0.014 |
| caps_style | sentence_case | 2026-05 | 9502 | 92 | 13000.000 | 26500.000 | 9.574 | -0.028 | 0.014 |
| caps_style | sentence_case | 2026-06 | 9415 | 91 | 12000.000 | 23000.000 | 9.492 | -0.030 | 0.014 |
| caps_style | sentence_case | 2026-07 | 9652 | 87 | 12000.000 | 26000.000 | 9.550 | -0.023 | 0.014 |
| caps_style | sentence_case | 2026-08 | 8750 | 86 | 13000.000 | 28925.000 | 9.624 | -0.035 | 0.014 |
| caps_style | sentence_case | 2026-09 | 4254 | 73 | 20000.000 | 70000.000 | 10.066 | -0.036 | 0.020 |
| caps_style | sentence_case | all | 83923 | 180 | 15000.000 | 26500.000 | 9.702 | -0.028 | 0.005 |
| caps_style | mixed_other | 2026-03 | 63 | 15 | 109000.000 | 103000.000 | 11.296 | -0.039 | 0.084 |
| caps_style | mixed_other | 2026-04 | 38 | 9 | 106500.000 | 106500.000 | 11.414 | -0.110 | 0.149 |
| caps_style | mixed_other | 2026-05 | 35 | 12 | 79000.000 | 68250.000 | 10.985 | -0.060 | 0.110 |
| caps_style | mixed_other | 2026-06 | 36 | 7 | 104000.000 | 112000.000 | 11.144 | -0.064 | 0.089 |
| caps_style | mixed_other | 2026-07 | 39 | 9 | 81000.000 | 108000.000 | 11.258 | 0.055 | 0.076 |
| caps_style | mixed_other | 2026-08 | 26 | 10 | 67000.000 | 82500.000 | 11.148 | 0.002 | 0.083 |
| caps_style | mixed_other | all | 276 | 39 | 93500.000 | 58000.000 | 11.160 | -0.086 | 0.048 |
| caps_style | short_other | 2026-01 | 75 | 25 | 29000.000 | 66000.000 | 10.438 | 0.235 | 0.081 |
| caps_style | short_other | 2026-02 | 70 | 23 | 55000.000 | 103000.000 | 10.926 | 0.203 | 0.090 |
| caps_style | short_other | 2026-03 | 81 | 30 | 24000.000 | 93500.000 | 10.218 | 0.228 | 0.110 |
| caps_style | short_other | 2026-04 | 90 | 30 | 66000.000 | 112000.000 | 10.892 | 0.347 | 0.084 |
| caps_style | short_other | 2026-05 | 76 | 20 | 24500.000 | 59500.000 | 10.017 | 0.330 | 0.086 |
| caps_style | short_other | 2026-06 | 104 | 18 | 36000.000 | 78250.000 | 9.895 | 0.156 | 0.070 |
| caps_style | short_other | 2026-07 | 103 | 25 | 18000.000 | 62000.000 | 9.646 | 0.227 | 0.075 |
| caps_style | short_other | 2026-08 | 85 | 27 | 18000.000 | 39000.000 | 9.671 | 0.103 | 0.081 |
| caps_style | short_other | 2026-09 | 29 | 14 | 18000.000 | 51500.000 | 9.851 | -0.028 | 0.153 |
| caps_style | short_other | all | 713 | 61 | 27000.000 | 46000.000 | 10.165 | 0.216 | 0.029 |
| all | all channels | 2026-01 | 27008 | 225 | 26000.000 | 40000.000 | 10.064 |  |  |
| all | all channels | 2026-02 | 25495 | 225 | 25000.000 | 37000.000 | 10.011 |  |  |
| all | all channels | 2026-03 | 29216 | 222 | 29000.000 | 46500.000 | 10.153 |  |  |
| all | all channels | 2026-04 | 27625 | 226 | 25000.000 | 35750.000 | 10.040 |  |  |
| all | all channels | 2026-05 | 26864 | 227 | 19000.000 | 30500.000 | 9.842 |  |  |
| all | all channels | 2026-06 | 27157 | 228 | 18000.000 | 27250.000 | 9.783 |  |  |
| all | all channels | 2026-07 | 27866 | 227 | 18000.000 | 28000.000 | 9.788 |  |  |
| all | all channels | 2026-08 | 26475 | 227 | 21000.000 | 37500.000 | 9.949 |  |  |
| all | all channels | 2026-09 | 12247 | 224 | 30000.000 | 56500.000 | 10.294 |  |  |


Capitalisation style by channel group and by title label:

| grouping | group | n_titles | all_caps | selective_caps | title_case | sentence_case | mixed_other | short_other | caps_any |
|---|---|---|---|---|---|---|---|---|---|
| channel_group | left | 62517 | 0.017 | 0.462 | 0.331 | 0.180 | 0.003 | 0.006 | 0.480 |
| channel_group | neutral | 38562 | 0.007 | 0.141 | 0.289 | 0.560 | 0.001 | 0.003 | 0.147 |
| channel_group | right | 49492 | 0.050 | 0.391 | 0.420 | 0.131 | 0.001 | 0.007 | 0.441 |
| title_label | left | 2585 | 0.014 | 0.416 | 0.290 | 0.272 | 0.002 | 0.006 | 0.430 |
| title_label | right | 2149 | 0.076 | 0.295 | 0.369 | 0.247 | 0.006 | 0.007 | 0.371 |
| title_label | neither | 5967 | 0.051 | 0.321 | 0.349 | 0.268 | 0.002 | 0.009 | 0.372 |


Title label x capitalization style (label shares within each style; relative log views per cell):

| caps_style | n_titles | share_left | share_right | share_neither | relative_log_views_left | n_left | relative_log_views_right | n_right | relative_log_views_neither | n_neither |
|---|---|---|---|---|---|---|---|---|---|---|
| all_caps | 506 | 0.073 | 0.324 | 0.603 | 0.219 | 36 | -0.007 | 138 | 0.005 | 281 |
| selective_caps | 3621 | 0.297 | 0.175 | 0.528 | 0.071 | 1052 | 0.116 | 616 | 0.082 | 1816 |
| title_case | 3627 | 0.207 | 0.219 | 0.574 | -0.051 | 683 | -0.044 | 730 | -0.048 | 1912 |
| sentence_case | 2834 | 0.248 | 0.187 | 0.565 | 0.001 | 703 | -0.065 | 518 | -0.011 | 1577 |
| mixed_other | 30 | 0.133 | 0.400 | 0.467 |  | 4 |  | 11 |  | 13 |
| short_other | 83 | 0.181 | 0.181 | 0.639 |  | 10 |  | 12 | -0.120 | 29 |


## Files

Machine-readable interface tables: `features.csv`, `dimensions.csv`, `topics.csv`, `labels.csv`, `creators.csv`, `leaning_by_creator.csv` (all under `data/titles/analysis/`). Profile cards: `pipeline_titles/reports/cards/`. HTML: `pipeline_titles/reports/title_stylometry.html`. Methods: `methods_appendix.md`.
