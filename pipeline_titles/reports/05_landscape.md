# 5. The landscape: who titles like whom

**The question.** Do creators that share a lane share a style? Who are each creator's real neighbours in style, as opposed to in subject matter? Who gets named, and does the landscape converge on the same hooks?

## The finding in one paragraph

Lane predicts style almost not at all. Clustering creators in the twelve-dimensional, topic-controlled style space and comparing the clusters with the lanes gives an adjusted Rand index of 0.045 for edited uploads (0.061 on political titles only), and topic clusters do no better (0.004). Only one lane holds together, US legacy TV (its members are 33% closer to each other than to everyone else); every other lane is about as dispersed as the corpus. The largest style cluster holds 69 creators from eleven lanes. So the useful unit is not the lane but the five nearest style neighbours on each creator's card, and those cut across politics: Hasan Piker's are Vaush and two right-wing channels, Ben Shapiro's include Kim Iversen and Alex Stein, MeidasTouch's are Officer Tatum and Nick Fuentes. The hooks converge too: 474 titles are used verbatim by creators from different organisations ("THIS IS INSANE.." by 12 creators in 5 lanes), 62 % of them across lanes.

## Clusterings against the lanes

Style space: agglomerative (Ward) on z-scored topic-controlled factor scores. Topic space: average linkage on the Jensen-Shannon distance between creators' topic mixes. k chosen by silhouette; ARI = adjusted Rand index (1 = identical partitions, 0 = chance).

| genre | titles | n_creators | style_k | style_silhouette | topic_k | topic_silhouette | ari_style_vs_lane | ari_topic_vs_lane | ari_style_vs_topic |
|---|---|---|---|---|---|---|---|---|---|
| videos | all | 239 | 11 | 0.128 | 3 | 0.144 | 0.045 | 0.004 | 0.003 |
| videos | political | 234 | 10 | 0.136 | 3 | 0.110 | 0.061 | -0.013 | -0.004 |
| streams | all | 79 | 9 | 0.159 | 12 | 0.089 | 0.002 | 0.179 | 0.075 |
| streams | political | 77 | 3 | 0.150 | 3 | 0.088 | -0.034 | -0.017 | 0.143 |


The low silhouettes (0.09-0.16) say the same thing from the other side: neither space has well-separated groups, the creators form a continuum.

## Which lanes cohere (edited uploads)

Mean distance in style space between members of a lane, over the mean distance from members to everyone else; below 1 means lane-mates are closer than strangers.

| lane | n_creators | within_lane_distance | between_lane_distance | cohesion_ratio |
|---|---|---|---|---|
| US legacy TV | 9 | 3.30 | 4.93 | 0.67 |
| streamers | 23 | 3.74 | 4.33 | 0.86 |
| humour / satire | 6 | 3.79 | 4.31 | 0.88 |
| US press | 18 | 4.14 | 4.59 | 0.90 |
| centrist / heterodox | 10 | 3.98 | 4.40 | 0.91 |
| interview podcasts | 19 | 4.13 | 4.46 | 0.93 |
| right commentary | 69 | 4.24 | 4.47 | 0.95 |
| legal commentary | 8 | 4.19 | 4.30 | 0.97 |
| wires & international | 11 | 5.15 | 5.29 | 0.97 |
| independent digital news | 19 | 4.39 | 4.50 | 0.97 |
| left commentary | 40 | 4.59 | 4.64 | 0.99 |
| right TV networks | 4 | 5.69 | 5.31 | 1.07 |
| explainers / geopolitics | 3 | 6.04 | 5.45 | 1.11 |


## Where lane and style disagree

Every lane with three or more members is split across style clusters; the share of a lane in its own largest style cluster:

| group | n_creators | n_style_clusters | largest_cluster_share |
|---|---|---|---|
| centrist / heterodox | 10 | 4 | 0.40 |
| explainers / geopolitics | 3 | 3 | 0.33 |
| humour / satire | 6 | 3 | 0.50 |
| independent digital news | 19 | 8 | 0.32 |
| interview podcasts | 19 | 4 | 0.42 |
| left commentary | 40 | 6 | 0.38 |
| legal commentary | 8 | 5 | 0.38 |
| right commentary | 69 | 6 | 0.36 |
| right TV networks | 4 | 3 | 0.50 |
| streamers | 23 | 6 | 0.39 |
| US legacy TV | 9 | 2 | 0.89 |
| US press | 18 | 5 | 0.33 |
| wires & international | 11 | 6 | 0.55 |


Conversely, style clusters span lanes: the two largest (69 and 54 creators) each mix left and right commentary, streamers, podcasts and independent news. Full membership lists: `disagreements_lane_style.csv`, `style_clusters.csv`, `topic_clusters.csv`.

## Nearest style neighbours, a sample

| creator | lane | five nearest in style |
|---|---|---|
| @HasanAbi | streamers | @Vaush [streamers], @TheVaushPit [streamers], @TimcastNews [right commentary], @JustPearlyThings [right commentary], ... |
| @BenShapiro | right commentary | @StevenCrowder [right commentary], @KimIversen [centrist / heterodox], @RealDanBongino [right commentary], @hutch [st... |
| @FoxNews | US legacy TV | @FoxNewsChannelClips [US legacy TV], @msnow [US legacy TV], @NBCNews [US legacy TV], @thedavidpakmanshow [left commen... |
| @MeidasTouch | left commentary | @TheOfficerTatum [right commentary], @LegalAFMTN [legal commentary], @deanwithrs [streamers], @adammockler [left comm... |
| @TuckerCarlson | interview podcasts | @MyronGainesX [right commentary], @RubinReport [right commentary], @TheAdamCarollaShow1 [interview podcasts], @thejim... |
| @joerogan | interview podcasts | @markets [US press], @ClubRandomPodcast [interview podcasts], @breakingpoints [independent digital news], @podsaveame... |
| @Reuters | wires & international | @aljazeeraenglish [wires & international], @CBSNews [US legacy TV], @AssociatedPress [wires & international], @ABCNew... |
| @destiny | streamers | @TheLincolnProject [centrist / heterodox], @hutch [streamers], @TheMajorityReport [left commentary], @LIVESNEAKO [str... |
| @bennyjohnson | right commentary | @OfficialSaharTV [right commentary], @BlazeTV [right commentary], @rolandsmartin [independent digital news], @Destiny... |
| @CNN | US legacy TV | @CBSNews [US legacy TV], @SkyNews [wires & international], @NBCNews [US legacy TV], @AssociatedPress [wires & interna... |


Neighbours are computed on titles with same-organisation cross-posts removed and low-n creators excluded; every creator's five style and five topic neighbours are on its card and in `neighbours_style.csv` / `neighbours_topic.csv`. The maps on the HTML page (PCA of the style space, MDS of the topic space) show the same picture: lane colours are scattered through both.

## Organisations

Sister channels do share a house style: the four MeidasTouch Network channels sit together at the outrage end of the tone factor (organisation score -0.99) and high on capitals; the three Timcast channels are the most capitalised organisation (2.35 on F9); the four NYT channels and CBS sit at the positive/neutral end. Title-weighted organisation scores (clippers excluded) are in `org_style.csv`.

## Who gets named

Counted on the creator-balanced subset; people keyed by surname, so "Kirk" pools Charlie and Erika Kirk and "Trump" pools every Trump. `outrage_ratio` is the outrage-frame share of titles naming the entity over the corpus share.

| entity | n_titles_balanced | n_creators | top_lanes_by_share | outrage_share | outrage_ratio |
|---|---|---|---|---|---|
| Trump | 7619 | 199 | legal_institutional (9.2%); left_commentary (6.2%); us_legacy_tv (4.9%) | 0.67 | 1.18 |
| Hormuz | 1065 | 86 | wire_international (1.5%); us_press_print_digital (0.9%); us_legacy_tv (0.8%) | 0.52 | 0.91 |
| Hegseth | 1062 | 106 | us_press_print_digital (1.1%); left_commentary (0.9%); us_legacy_tv (0.8%) | 0.53 | 0.94 |
| Putin | 992 | 67 | wire_international (1.9%); interview_podcast (0.6%); independent_digital_news (0.4%) | 0.69 | 1.21 |
| Charlie Kirk | 910 | 118 | right_tv_network (2.1%); right_commentary (0.8%); streamer_reaction (0.6%) | 0.53 | 0.94 |
| JD Vance | 886 | 120 | humour_satire (0.8%); left_commentary (0.8%); centrist_heterodox (0.7%) | 0.57 | 1.00 |
| Mamdani | 765 | 111 | right_commentary (0.8%); us_press_print_digital (0.7%); right_tv_network (0.6%) | 0.70 | 1.23 |
| Netanyahu | 726 | 113 | interview_podcast (1.2%); wire_international (0.6%); left_commentary (0.4%) | 0.70 | 1.23 |
| Epstein | 708 | 114 | us_legacy_tv (0.7%); left_commentary (0.5%); us_press_print_digital (0.4%) | 0.72 | 1.27 |
| Lindsey Graham | 628 | 123 | humour_satire (0.7%); right_tv_network (0.7%); us_legacy_tv (0.5%) | 0.48 | 0.84 |
| Brian Shapiro | 594 | 85 | left_commentary (1.0%); streamer_reaction (0.4%); humour_satire (0.3%) | 0.77 | 1.36 |
| Nancy Guthrie | 550 | 35 | us_legacy_tv (1.8%); us_press_print_digital (0.3%); right_tv_network (0.2%) | 0.17 | 0.29 |
| Kristi Noem | 543 | 103 | humour_satire (1.1%); left_commentary (0.6%); us_legacy_tv (0.3%) | 0.74 | 1.30 |
| Mike Johnson | 538 | 91 | interview_podcast (1.6%); right_tv_network (0.7%); left_commentary (0.5%) | 0.57 | 1.01 |
| Kash Patel | 479 | 89 | humour_satire (0.6%); centrist_heterodox (0.5%); legal_institutional (0.5%) | 0.77 | 1.35 |


| entity | n_titles_balanced | n_creators | top_lanes_by_share | outrage_share | outrage_ratio |
|---|---|---|---|---|---|
| Trump | 8817 | 193 | us_legacy_tv (8.2%); left_commentary (8.1%); legal_institutional (6.2%) | 0.67 | 1.18 |
| White House | 1565 | 120 | us_press_print_digital (1.7%); us_legacy_tv (1.5%); right_tv_network (1.1%) | 0.41 | 0.73 |
| GOP | 1509 | 106 | us_legacy_tv (1.8%); centrist_heterodox (1.3%); legal_institutional (1.2%) | 0.72 | 1.27 |
| MAGA | 1009 | 123 | left_commentary (1.7%); centrist_heterodox (1.2%); streamer_reaction (1.0%) | 0.93 | 1.63 |
| Senate | 976 | 97 | us_legacy_tv (1.4%); us_press_print_digital (1.1%); right_tv_network (0.8%) | 0.38 | 0.67 |
| FBI | 885 | 119 | us_legacy_tv (1.1%); legal_institutional (1.0%); right_tv_network (1.0%) | 0.74 | 1.30 |
| Supreme Court | 856 | 107 | legal_institutional (4.6%); us_legacy_tv (0.8%); us_press_print_digital (0.7%) | 0.52 | 0.92 |
| NATO | 822 | 86 | wire_international (1.3%); us_legacy_tv (0.4%); right_tv_network (0.4%) | 0.51 | 0.91 |
| House | 815 | 94 | us_legacy_tv (1.0%); us_press_print_digital (1.0%); right_tv_network (0.6%) | 0.41 | 0.72 |
| Congress | 773 | 113 | legal_institutional (0.9%); wire_international (0.6%); us_press_print_digital (0.5%) | 0.49 | 0.87 |


Trump is in 4.7 % of balanced titles counting both tags, named by 199 of 274 creators, most by legal commentary and left commentary. The entities carrying the most outrage framing relative to baseline are MAGA (1.6x), Pam Bondi, Kash Patel and Candace Owens (1.3-1.5x); the least are the crime-story names (Nancy Guthrie, Lindsay Clancy, 0.3x) and institutions used as datelines (the Senate, the House, the White House). "Hormuz" is a spaCy mistake (a strait tagged as a person) left visible on purpose: entity counts from a small NER model on headline text are noisy at the margin.

## Convergent formulas

Of 1,575 distinct titles (case-insensitive) used by two or more creators, 474 cross organisations; the rest are same-outlet cross-posts (TYT / The Damage Report alone account for hundreds). The most shared:

| example | n_creators | n_titles | n_lanes | lanes |
|---|---|---|---|---|
| THIS IS INSANE.. | 12 | 14 | 5 | centrist_heterodox; independent_digital_news; left_commentary; right_commentary; streamer_reaction |
| IT HAPPENED AGAIN?? | 7 | 10 | 4 | independent_digital_news; left_commentary; right_commentary; streamer_reaction |
| This changes everything.. | 7 | 7 | 4 | centrist_heterodox; independent_digital_news; right_commentary; streamer_reaction |
| IT'S HAPPENING | 6 | 10 | 4 | independent_digital_news; left_commentary; right_commentary; streamer_reaction |
| This Is Disgusting | 6 | 6 | 3 | left_commentary; right_commentary; streamer_reaction |
| it’s over. | 5 | 9 | 2 | right_commentary; streamer_reaction |
| It’s finally happening.. | 5 | 6 | 4 | independent_digital_news; left_commentary; right_commentary; streamer_reaction |
| Don Lemon ARRESTED! | 5 | 5 | 3 | left_commentary; legal_institutional; right_commentary |
| This can't be real.. | 5 | 5 | 4 | independent_digital_news; left_commentary; right_commentary; streamer_reaction |
| This is so embarrassing.. | 5 | 5 | 2 | left_commentary; streamer_reaction |
| This is terrifying... | 5 | 5 | 3 | left_commentary; right_commentary; streamer_reaction |
| Oh.. my.. god... | 4 | 8 | 3 | left_commentary; right_commentary; streamer_reaction |
| It finally happened | 4 | 6 | 2 | left_commentary; streamer_reaction |
| BREAKING: TRUMP FIRES PAM BONDI | 4 | 5 | 3 | centrist_heterodox; left_commentary; streamer_reaction |
| HOLY SH*T.. | 4 | 5 | 2 | right_commentary; streamer_reaction |


These are content-free exclamations, the "Shocking Events and Reactions" topic of document 2: the same dozen phrases serve as titles on the left, the right and the streaming platforms. With names and numbers masked, the shared templates are outrage frames and guest formulas:

| template | n_creators | n_titles | n_lanes | example |
|---|---|---|---|---|
| <ENT> 's <ENT> | 62 | 147 | 12 | Iran's Plan To Make You SIMP |
| <ENT> after <ENT> | 37 | 73 | 9 | Trump’s Envoys Get RUDE AWAKENING After Putin Meeting |
| <ENT> 's <ENT> <ENT> | 23 | 40 | 8 | California's Election Shakeup + Microsoft's AI Spy Badge \| PBD #811 |
| <ENT> ’s <ENT> | 18 | 28 | 8 | AIPAC’s "Elect Chicago Women" Super PAC Exposed |
| <ENT> exposes <ENT> | 14 | 19 | 5 | Elizabeth Warren Exposes Trump’s Fed Pick In Brutal Hearing |
| <ENT> <ENT> 's <ENT> | 13 | 19 | 8 | US Media's Hasan Piker Derangement Syndrome Is Ridiculous |
| <ENT> <ENT> after <ENT> | 13 | 15 | 6 | OMG: Trump RUSHES OFF after Going to HOSPITAL! |
| <ENT> after <ENT> <ENT> | 11 | 16 | 4 | Hakeem Jeffries In Full Panic Mode After Kushner Meeting Pisses Off Democrats |
| <ENT> vs. <ENT> | 11 | 11 | 7 | Ben Shapiro vs. Fortnite |
| <ENT> w/ <ENT> | 10 | 38 | 4 | Biblical Idolatry & The Role of Moses w/ Jordan B. Peterson |
| <ENT> <ENT> w/ <ENT> | 10 | 20 | 5 | "It Went Completely Viral" Brett Cooper Talks Internet Drama & Pendragon Cycle W/ Michael Knowles |
| <ENT> says <ENT> | 10 | 17 | 5 | Fox News Lunatic Says Americans Have Data Center Derangement Syndrome |
| <ENT> 's <ENT> in <ENT> | 10 | 13 | 7 | AOC's DISASTROUS Foreign Policy Debut In Munich |
| <ENT> <ENT> 's <ENT> <ENT> | 9 | 11 | 6 | Bill Kristol: MAGA's Grievance Culture \| The Bulwark Podcast |
| the truth about <ENT> | 9 | 9 | 6 | The truth about Blizzard |


26 % of shared templates stay within a lane, 38 % of shared verbatim titles: the conventions travel across the landscape rather than within its camps.

Files: `cluster_comparison.csv`, `lane_style_cohesion.csv`, `disagreements_lane_style.csv`, `style_clusters.csv`, `topic_clusters.csv`, `neighbours_style.csv`, `neighbours_topic.csv`, `map_style.csv`, `map_topic.csv`, `org_style.csv`, `entities_top.csv`, `shared_titles.csv`, `shared_templates.csv`.
