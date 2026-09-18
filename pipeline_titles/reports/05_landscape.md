# 5. The landscape: who titles like whom

**The question.** Do channels whose titles read the same way politically (the left / neutral / right groups) share a *style*? Who are each creator's real neighbours in style, as opposed to in subject matter? Who gets named, and does the landscape converge on the same hooks?

## The finding in one paragraph

Political grouping predicts style almost not at all. Clustering creators in the twelve-dimensional, topic-controlled style space and comparing the clusters with the three channel groups gives an adjusted Rand index of 0.036 for edited uploads (0.054 on political titles only), and topic clusters do no better (0.010). No group holds together in style space: the tightest is right channels at a cohesion ratio of 0.94 (members 6% closer to each other than to everyone else), and the largest style cluster holds 69 creators from all three groups. So the useful unit is not the group but the five nearest style neighbours on each creator's card, and those cut across politics: for 54 % of the left and right channels the single nearest neighbour is in another group, and 88 % have a channel from the opposite side among their five (@HasanAbi (left) has @TimcastNews (right), @JustPearlyThings (right), @dineshdsouza (right) among its five; @MeidasTouch (left) has @TheOfficerTatum (right), https://rumble.com/c/nickjfuentes (right) among its five; @FoxNews (right) has @msnow (left), @thedavidpakmanshow (left) among its five). The hooks converge too: 474 titles are used verbatim by creators from different organisations ("THIS IS INSANE.." by 12 creators across 3 groups), 38 % of them by channels in more than one group.

## Clusterings against the channel groups

![Style space: every ranked creator, coloured by channel group. The interactive version, with names on hover and each creator's five neighbours, is on the HTML page.](figures/05_style_map.png)
*Style space: every ranked creator, coloured by channel group. The interactive version, with names on hover and each creator's five neighbours, is on the HTML page.*

Style space: agglomerative (Ward) on z-scored topic-controlled factor scores. Topic space: average linkage on the Jensen-Shannon distance between creators' topic mixes. k chosen by silhouette; ARI = adjusted Rand index (1 = identical partitions, 0 = chance).

| genre | titles | n_creators | style_k | style_silhouette | topic_k | topic_silhouette | ari_style_vs_group | ari_topic_vs_group | ari_style_vs_topic |
|---|---|---|---|---|---|---|---|---|---|
| videos | all | 239 | 11 | 0.128 | 3 | 0.144 | 0.036 | 0.010 | 0.003 |
| videos | political | 234 | 10 | 0.136 | 3 | 0.110 | 0.054 | 0.017 | -0.004 |
| streams | all | 79 | 9 | 0.159 | 12 | 0.089 | 0.025 | 0.117 | 0.075 |
| streams | political | 77 | 3 | 0.150 | 3 | 0.088 | -0.006 | 0.008 | 0.143 |


The low silhouettes say the same thing from the other side: neither space has well-separated groups, the creators form a continuum.

![Topic space map.](figures/05_topic_map.png)
*Topic space: MDS of the Jensen-Shannon distances between creators' topic mixes.*

![ARI and cohesion.](figures/05_groups_vs_style.png)
*Left: adjusted Rand index of the clusterings against the channel groups and against each other. Right: group cohesion in style space.*

## Do the groups cohere in style? (edited uploads)

Mean distance in style space between members of a group, over the mean distance from members to everyone else; below 1 means group-mates are closer than strangers.

| group | n_creators | within_group_distance | between_group_distance | cohesion_ratio |
|---|---|---|---|---|
| left channels | 105 | 4.61 | 4.55 | 1.01 |
| neutral channels | 38 | 4.75 | 4.75 | 1.00 |
| right channels | 96 | 4.23 | 4.51 | 0.94 |


## Where group and style disagree

Every group is split across style clusters; the share of a group in its own largest style cluster:

| group | n_creators | n_style_clusters | largest_cluster_share |
|---|---|---|---|
| left channels | 105 | 10 | 0.29 |
| neutral channels | 38 | 8 | 0.32 |
| right channels | 96 | 8 | 0.38 |


Conversely, style clusters span groups: the two largest (69 and 54 creators) each mix left, neutral and right channels. Full membership lists: `disagreements_group_style.csv`, `style_clusters.csv`, `topic_clusters.csv`.

## Nearest style neighbours, a sample

| creator | group | five nearest in style |
|---|---|---|
| @HasanAbi | left | @Vaush [left], @TheVaushPit [left], @TimcastNews [right], @JustPearlyThings [right], @dineshdsouza [right] |
| @BenShapiro | right | @StevenCrowder [right], @KimIversen [neutral], @RealDanBongino [right], @hutch [neutral], @AlexStein99 [right] |
| @FoxNews | right | @FoxNewsChannelClips [right], @msnow [left], @NBCNews [neutral], @thedavidpakmanshow [left], @RebelNewsOnline [right] |
| @MeidasTouch | left | @TheOfficerTatum [right], @LegalAFMTN [left], @deanwithrs [left], @adammockler [left], https://rumble.com/c/nickjfuen... |
| @TuckerCarlson | neutral | @MyronGainesX [right], @RubinReport [right], @TheAdamCarollaShow1 [right], @thejimmydoreshow [neutral], https://rumbl... |
| @joerogan | neutral | @markets [neutral], @ClubRandomPodcast [neutral], @breakingpoints [left], @podsaveamerica [left], @TheMajorityReport ... |
| @Reuters | neutral | @aljazeeraenglish [left], @CBSNews [neutral], @AssociatedPress [neutral], @ABCNews [neutral], @NBCNews [neutral] |
| @destiny | left | @TheLincolnProject [left], @hutch [neutral], @TheMajorityReport [left], @LIVESNEAKO [neutral], @BadEmpanadaLive [left] |
| @bennyjohnson | right | @OfficialSaharTV [right], @BlazeTV [right], @rolandsmartin [left], @DestinyDGGClips [right], @MyronGainesX [right] |
| @CNN | left | @CBSNews [neutral], @SkyNews [left], @NBCNews [neutral], @AssociatedPress [neutral], @BBCNews [neutral] |


Neighbours are computed on titles with same-organisation cross-posts removed and low-n creators excluded; every creator's five style and five topic neighbours are on its card and in `neighbours_style.csv` / `neighbours_topic.csv`. The maps on the HTML page (PCA of the style space, MDS of the topic space) show the same picture: the group colours are scattered through both.

## Organisations

Sister channels do share a house style: the four MeidasTouch Network channels sit together at the outrage end of the tone factor (organisation score -0.99) and high on capitals; the three Timcast channels are the most capitalised organisation (2.35 on F9); the four NYT channels and CBS sit at the positive/neutral end. Title-weighted organisation scores (clippers excluded) are in `org_style.csv`.

## Who gets named

![Outrage-frame ratio for the 25 most-named people: orange above the corpus baseline, blue below.](figures/05_entities_outrage.png)
*Outrage-frame ratio for the 25 most-named people: orange above the corpus baseline, blue below.*

Counted on the creator-balanced subset; people keyed by surname, so "Kirk" pools Charlie and Erika Kirk and "Trump" pools every Trump. `share_by_group` is the share of each channel group's balanced titles that names the entity; `outrage_ratio` is the outrage-frame share of titles naming the entity over the corpus share.

| entity | n_titles_balanced | n_creators | share_by_group | outrage_share | outrage_ratio |
|---|---|---|---|---|---|
| Trump | 7619 | 199 | left (5.6%); neutral (3.8%); right (2.3%) | 0.67 | 1.18 |
| Hormuz | 1065 | 86 | neutral (1.0%); left (0.5%); right (0.3%) | 0.52 | 0.91 |
| Hegseth | 1062 | 106 | left (0.8%); neutral (0.7%); right (0.2%) | 0.53 | 0.94 |
| Putin | 992 | 67 | neutral (1.0%); left (0.5%); right (0.1%) | 0.69 | 1.21 |
| Charlie Kirk | 910 | 118 | right (0.9%); neutral (0.4%); left (0.2%) | 0.53 | 0.94 |
| JD Vance | 886 | 120 | left (0.6%); neutral (0.5%); right (0.4%) | 0.57 | 1.00 |
| Mamdani | 765 | 111 | right (0.7%); neutral (0.4%); left (0.2%) | 0.70 | 1.23 |
| Netanyahu | 726 | 113 | neutral (0.5%); left (0.4%); right (0.2%) | 0.70 | 1.23 |
| Epstein | 708 | 114 | left (0.5%); neutral (0.4%); right (0.2%) | 0.72 | 1.27 |
| Lindsey Graham | 628 | 123 | left (0.4%); neutral (0.3%); right (0.3%) | 0.48 | 0.84 |
| Brian Shapiro | 594 | 85 | left (0.6%); right (0.2%); neutral (0.1%) | 0.77 | 1.36 |
| Nancy Guthrie | 550 | 35 | neutral (0.6%); right (0.4%); left (0.0%) | 0.17 | 0.29 |
| Kristi Noem | 543 | 103 | left (0.5%); neutral (0.2%); right (0.2%) | 0.74 | 1.30 |
| Mike Johnson | 538 | 91 | left (0.4%); right (0.2%); neutral (0.2%) | 0.57 | 1.01 |
| Kash Patel | 479 | 89 | left (0.4%); neutral (0.2%); right (0.1%) | 0.77 | 1.35 |


| entity | n_titles_balanced | n_creators | share_by_group | outrage_share | outrage_ratio |
|---|---|---|---|---|---|
| Trump | 8817 | 193 | left (7.0%); neutral (4.5%); right (1.9%) | 0.67 | 1.18 |
| White House | 1565 | 120 | neutral (1.3%); left (0.7%); right (0.7%) | 0.41 | 0.73 |
| GOP | 1509 | 106 | left (1.1%); right (0.7%); neutral (0.5%) | 0.72 | 1.27 |
| MAGA | 1009 | 123 | left (1.2%); right (0.1%); neutral (0.1%) | 0.93 | 1.63 |
| Senate | 976 | 97 | neutral (0.8%); right (0.4%); left (0.4%) | 0.38 | 0.67 |
| FBI | 885 | 119 | right (0.7%); neutral (0.4%); left (0.3%) | 0.74 | 1.30 |
| Supreme Court | 856 | 107 | neutral (0.5%); left (0.5%); right (0.4%) | 0.52 | 0.92 |
| NATO | 822 | 86 | neutral (0.9%); left (0.3%); right (0.2%) | 0.51 | 0.91 |
| House | 815 | 94 | neutral (0.7%); left (0.3%); right (0.3%) | 0.41 | 0.72 |
| Congress | 773 | 113 | neutral (0.6%); left (0.4%); right (0.3%) | 0.49 | 0.87 |


Trump is in 4.7 % of balanced titles counting both tags, named by 199 of 274 creators, and named most by the left group (left (5.6%); neutral (3.8%); right (2.3%)). Charlie Kirk and Mamdani are the right group's names, Hormuz, Putin and Netanyahu the neutral group's. The entities carrying the most outrage framing relative to baseline are the MAGA-era officials and the culture-war names; the least are the crime-story names (Nancy Guthrie, Lindsay Clancy) and institutions used as datelines (the Senate, the House, the White House). "Hormuz" is a spaCy mistake (a strait tagged as a person) left visible on purpose: entity counts from a small NER model on headline text are noisy at the margin.

## Convergent formulas

![The most shared verbatim titles across organisations.](figures/05_shared_titles.png)
*The most shared verbatim titles across organisations.*

Of 1,575 distinct titles (case-insensitive) used by two or more creators, 474 cross organisations; the rest are same-outlet cross-posts (TYT / The Damage Report alone account for hundreds). The most shared:

| example | n_creators | n_titles | n_groups | groups |
|---|---|---|---|---|
| THIS IS INSANE.. | 12 | 14 | 3 | left; neutral; right |
| IT HAPPENED AGAIN?? | 7 | 10 | 2 | left; right |
| This changes everything.. | 7 | 7 | 2 | left; right |
| IT'S HAPPENING | 6 | 10 | 3 | left; neutral; right |
| This Is Disgusting | 6 | 6 | 2 | left; right |
| it’s over. | 5 | 9 | 3 | left; neutral; right |
| It’s finally happening.. | 5 | 6 | 2 | left; right |
| Don Lemon ARRESTED! | 5 | 5 | 2 | left; right |
| This can't be real.. | 5 | 5 | 2 | left; right |
| This is so embarrassing.. | 5 | 5 | 2 | left; right |
| This is terrifying... | 5 | 5 | 2 | left; right |
| Oh.. my.. god... | 4 | 8 | 2 | left; right |
| It finally happened | 4 | 6 | 1 | left |
| BREAKING: TRUMP FIRES PAM BONDI | 4 | 5 | 1 | left |
| HOLY SH*T.. | 4 | 5 | 3 | left; neutral; right |


These are content-free exclamations, the "Shocking Events and Reactions" topic of document 2: the same dozen phrases serve as titles on the left, the right and in between. With names and numbers masked, the shared templates are outrage frames and guest formulas:

| template | n_creators | n_titles | n_groups | example |
|---|---|---|---|---|
| <ENT> 's <ENT> | 62 | 147 | 3 | Iran's Plan To Make You SIMP |
| <ENT> after <ENT> | 37 | 73 | 3 | Trump’s Envoys Get RUDE AWAKENING After Putin Meeting |
| <ENT> 's <ENT> <ENT> | 23 | 40 | 3 | California's Election Shakeup + Microsoft's AI Spy Badge \| PBD #811 |
| <ENT> ’s <ENT> | 18 | 28 | 3 | AIPAC’s "Elect Chicago Women" Super PAC Exposed |
| <ENT> exposes <ENT> | 14 | 19 | 2 | Elizabeth Warren Exposes Trump’s Fed Pick In Brutal Hearing |
| <ENT> <ENT> 's <ENT> | 13 | 19 | 3 | US Media's Hasan Piker Derangement Syndrome Is Ridiculous |
| <ENT> <ENT> after <ENT> | 13 | 15 | 3 | OMG: Trump RUSHES OFF after Going to HOSPITAL! |
| <ENT> after <ENT> <ENT> | 11 | 16 | 3 | Hakeem Jeffries In Full Panic Mode After Kushner Meeting Pisses Off Democrats |
| <ENT> vs. <ENT> | 11 | 11 | 3 | Ben Shapiro vs. Fortnite |
| <ENT> w/ <ENT> | 10 | 38 | 3 | Biblical Idolatry & The Role of Moses w/ Jordan B. Peterson |
| <ENT> <ENT> w/ <ENT> | 10 | 20 | 3 | "It Went Completely Viral" Brett Cooper Talks Internet Drama & Pendragon Cycle W/ Michael Knowles |
| <ENT> says <ENT> | 10 | 17 | 3 | Fox News Lunatic Says Americans Have Data Center Derangement Syndrome |
| <ENT> 's <ENT> in <ENT> | 10 | 13 | 3 | AOC's DISASTROUS Foreign Policy Debut In Munich |
| <ENT> <ENT> 's <ENT> <ENT> | 9 | 11 | 3 | Bill Kristol: MAGA's Grievance Culture \| The Bulwark Podcast |
| the truth about <ENT> | 9 | 9 | 2 | The truth about Blizzard |


62 % of the shared verbatim titles are used within one channel group and 45 % of the shared templates; with three groups of these sizes a random pair of channels shares a group 38 % of the time, so both run a little more within the camps than chance would give, the verbatim exclamations clearly and the masked templates barely. Either way the same dozen phrases and the same "<ENT> destroys <ENT>" frames serve left, neutral and right channels alike.

Channel groups are the left / neutral / right groups of document 14: each channel's score = (right − left) / titles over its sampled titles as labelled by the judge, sorted at ±0.05. A channel's group says how its *titles* read, not what its host believes.

Files: `cluster_comparison.csv`, `group_style_cohesion.csv`, `disagreements_group_style.csv`, `style_clusters.csv`, `topic_clusters.csv`, `neighbours_style.csv`, `neighbours_topic.csv`, `map_style.csv`, `map_topic.csv`, `org_style.csv`, `entities_top.csv`, `shared_titles.csv`, `shared_templates.csv`.
