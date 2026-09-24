# 13. Signature title keywords per channel

**The question.** Which words does each channel use far more than everyone else?

## The finding in one paragraph

Each channel's signature is scored by weighted log-odds against all other channels' titles, with a prior that shrinks rare words, so the list is the vocabulary a channel *over-uses*, not merely uses. For most channels the top of the list is its own furniture (host names, show segments, a recurring guest), which is expected and is itself a style fact: ben, shapiro, movie, left, radical, tiktoks, majors, tucker, for Ben Shapiro, asmongold, abdul, fox, going, talking, cooked, ethan, hogs,  for Hasan Piker. Below that, the lists separate beats and registers: market, bid, fans, reuters, weekly, wall, talk, street, says, cup for Reuters, trump, panics, gets, loses, hell, loose, collapses, furious, disaster, for MeidasTouch. The top five per channel are below; the top ten with counts are in `signature_keywords.csv` and on each creator's card.

## Every channel's top five (alphabetical)

`z` is the log-odds z-score; larger = more distinctive. Words appear only if the channel used them at least three times. `group` is the channel group of document 14.

| creator | channel_name | group | top 5 (z) |
|---|---|---|---|
| @60minutes | 60 Minutes | neutral | minutes (63), episodes (33), sunday (29), laden (12), sasse (11) |
| @aaronparnas1 | Aaron Parnas | left | breaking (90), furious (29), republicans (29), major (28), trump (28) |
| @ABCNews | ABC News | neutral | abc (55), broadcast (52), good (49), know (43), need (43) |
| @ActualJusticeWarrior | Actual Justice Warrior | right | leftist (18), entitled (16), mamdani (16), black (16), mafia (15) |
| @adammockler | Adam Mockler | left | trump (36), maga (22), bomb (20), slip (20), lets (19) |
| @AfterPartyEmily | After Party with Emily Jashinsky | right | plus (21), truth (20), media (16), malice (16), culture (14) |
| @ajplus | AJ+ | left | gaza (9), cuba (5), africa (5), israeli (5), south (5) |
| @AlexStein99 | Alex Stein | right | stein (28), alex (24), dallas (12), prime (11), night (10) |
| @aljazeeraenglish | Al Jazeera English | left | gaza (52), israeli (44), lebanon (42), story (32), inside (31) |
| @AnaEscobarShow | Ana Escobar | right | charlie (19), kirk (15), candace (14), owens (13), tpusa (12) |
| @AndrewKlavan | Andrew Klavan | right | klavan (21), greatest (13), ranks (12), ranked (11), tiktoks (10) |
| @AndWeKnowOfficial-o9b | And We Know Official | right | pray (47), silver (20), comms (19), msm (13), gold (13) |
| @ANINewsIndia | ANI News | neutral | pm (86), india (79), modi (79), delhi (53), holds (51) |
| @AnthonyBrianLogan | Anthony Brian Logan | right | instagram (19), ask (18), spencer (9), mayor (9), pratt (9) |
| @AsmonTV | Asmongold TV | right | ck (34), game (32), i've (24), happening (21), genuinely (20) |
| @AssociatedPress | Associated Press | neutral | says (36), ap (29), xiv (28), shows (27), leo (22) |
| @axios | Axios | neutral | axios (39), view (17), fried (15), ai (14), brown (14) |
| @BadEmpanadaLive | BadEmpanada Live | left | zionist (16), cuba (12), palestine (12), signifier (12), anti-semitism (11) |
| @BadFaithPodcast | Bad Faith | left | left (11), unlocked (11), chomsky (11), briahna (10), zionist (9) |
| @BBCNews | BBC News | neutral | global (51), bbc (49), uk (37), story (30), andy (20) |
| @bbrettcooper | Brett Cooper | right | reacting (12), canceled (10), jelly (9), divorce (8), lively (8) |
| @BelleRanch | Belle of the Ranch | left | talk (119), let (115), trump (30), saying (15), wanting (12) |
| @bennyjohnson | Benny Johnson | right | libs (26), internet (25), panic (22), announces (18), on-air (18) |
| @BenShapiro | Ben Shapiro | right | ben (25), shapiro (16), movie (12), left (11), radical (11) |
| @BlackConservativePerspective | Black Conservative Perspective | right | woke (54), black (53), liberal (50), democrat (50), liberals (42) |
| @BlaireWhiteX | Blaire White | right | trans (7) |
| @BlazeTV | BlazeTV | right | beck (36), glenn (35), radical (16), far-left (15), rino (15) |
| @breakingpoints | Breaking Points | left | saagar (18), bibi (16), krystal (16), pape (16), aipac (15) |
| @BreakThroughNews | BreakThrough News | left | rania (15), khalek (15), cuba (15), lebanon (13), israel (11) |
| @briantylercohen | Brian Tyler Cohen | left | update (44), announcement (44), day (36), bombshell (33), trump (31) |
| @BrittanyVenti | Brittany Venti | neutral | thequartering (13), pearl (12), mayr (12), chrissie (11), simps (10) |
| @bulwarkmedia | The Bulwark | left | tim (28), command (28), level (26), sarah (26), shield (25) |
| @bushrakhanum | Bushra Khanum | neutral | raju (11), adeeb (10), parulekar (10), muslims (8), asia (6) |
| @cafedotcom | Stay Tuned with Preet Bharara | left | preet (17), bharara (17), joyce (14), elie (10), honig (8) |
| @CamHigby | Cam Higby | right | muslim (21), lib (20), anti-ice (19), islam (18), quran (17) |
| @CashJordan | Cash Jordan | right | mamdani (33), thought (28), nyc (27), mobs (18), marines (16) |
| @CaspianReport | CaspianReport | neutral | iran (3), america (2), war (2) |
| @CBSNews | CBS News | neutral | says (30), artemis (25), latest (24), ii (24), say (23) |
| @ChadPrather1 | Chad Prather | right | jesus (31), god (30), stories (17), faith (14), gospel (14) |
| @Channel5YouTube | Channel 5 with Andrew Callaghan | left | cast (13), interview (11), palestine (6), nick (5), inside (4) |
| @chicksonright | Chicks on the Right | right | candace (61), owens (48), tucker (30), megyn (24), carlson (21) |
| @chinainsights-r2w | China Insights | neutral | china (39), insights (36), xi (21), jinping (17), zhang (14) |
| @chriscuomo | The Chris Cuomo Project | left | cuomo (14), chris (10), midterms (9), wrong (9), mornings (9) |
| @clayandbuck | The Clay Travis & Buck Sexton Show | right | clay (38), buck (35), travis (30), stream (28), sexton (25) |
| @ClipsCandaceOwens | Candace Clips | neutral | erika (24), kirk (21), candace (21), charlie (19), owens (16) |
| @ClubRandomPodcast | Club Random Podcast | neutral | maher (60), club (36), random (32), classics (15), allen (13) |
| @CNN | CNN | left | roundup (28), cnn (25), fareed (24), enten (21), terms (20) |
| @ColeHastings | Cole Hastings | right | gen (17), epidemic (12), crisis (5), ai (2) |
| @ColemanHughesOfficial | Coleman Hughes | right | coleman (12), psychology (10), love (5), left (5), wrong (4) |
| @CoreyGilShusterAskProject | Corey Gil-Shuster | neutral | israelis (21), think (11), arab (9), solution (9), lgbtq (8) |
| @DailyDenims | Daily Denims | left | ethan (25), klein (21), asmongold (20), denims (19), unhinged (13) |
| @DannyHaiphongYT | Danny Haiphong | left | larry (28), marandi (27), iran (27), wilkerson (23), ritter (23) |
| @DarkHorsePod | Bret Weinstein | right | bret (36), heather (34), weinstein (34), lens (26), th (18) |
| @deanwithrs | Dean Withers | left | maga (57), man (34), argument (19), supporter (18), trump (15) |
| @DemocracyDocket | Democracy Docket | left | supreme (14), court (14), rig (11), voter (10), mail (10) |
| @DemocracyNow | Democracy Now! | left | headlines (56), world (27), ice (12), scholar (11), democracy (10) |
| @destiny | Destiny | left | destiny (32), debate (17), hutch (14), i've (10), boy (10) |
| @DestinyDGGClips | Destiny DGG Clips | right | destiny (36), hasan (28), asmongold (21), vaush (15), hutch (12) |
| @destinyhqclips | destinyhqclips | neutral | destiny (55), hasan (23), debate (17), snarker (16), snarkers (13) |
| @dineshdsouza | Dinesh D'Souza | right | fathers (12), founding (12), dinesh (11), series (10), d'souza (10) |
| @dollemore | Jesse Dollemore | left | donald (34), trump (31), fox (18), hegseth (16), markwayne (15) |
| @doomscrollpodcast | Joshua Citarella | left | socialism (7), politics (5), david (5) |
| @DoubleDownNews | Double Down News | left | lowkey (12), israel (10), want (9), think (9), mossad (8) |
| @DropSiteNews | Drop Site News | left | gaza (16), scahill (15), jeremy (14), lebanon (13), israel (11) |
| @DrSteveTurleyTV | Dr. Steve Turley | right | believe (31), happened (27), won't (25), muslims (15), democrats (11) |
| @DueDissidence | Due Dissidence | left | tucker (18), rex (15), massie (15), jose (14), vega (14) |
| @DylanBurnsLIVE | DylanBurnsLIVE | left | ukraine (19), debating (14), soypill (12), dsa (10), progressive (10) |
| @evanjmez | Evan James | left | ice (2), israel (2) |
| @EzraKleinShow | The Ezra Klein Show | left | klein (10), ezra (7), wants (4), america (2), war (1) |
| @FarronBalanced | Farron Balanced | left | trump (45), republicans (31), admits (16), total (16), staffers (16) |
| @fastpoliticspodcast | Fast Politics w/ Molly Jong-Fast | left | rick (32), wilson (30), sykes (19), acosta (18), wolfers (14) |
| @fightbackpodcast | Jake Shields' Fight Back Podcast | right | jake (52), shields (41), fight (27), bilzerian (22), owen (22) |
| @FinancialTimes | Financial Times | neutral | film (15), rethink (11), tech (7), energy (7), ai (6) |
| @Firstpost | Firstpost | neutral | africa (67), india (65), sharma (55), sports (53), iran (52) |
| @FleccasTalks | Fleccas Talks | right | stu (10), richard (9), cop (7), migrant (6), dropped (6) |
| @Forbes | Forbes | neutral | billionaire (35), billion (31), ai (28), startup (21), business (21) |
| @Forthepeoplepodcast305 | Niko House | left | pasta (17), drive (15), niko (9), jardula (9), time (9) |
| @FoxNews | Fox News | right | watters (32), gutfeld (32), breaking (32), iranian (29), details (28) |
| @FoxNewsChannelClips | Fox News Clips | right | laura (32), expert (31), ingraham (29), dems (24), says (22) |
| @franifio | The Bitchuation Room (with Francesca Fiorentini) | left | corner (17), feat (17), vigeland (14), emma (14), wajahat (13) |
| @FreshFitMiami | FreshandFit | right | myron (21), men (20), women (19), fit (19), girls (18) |
| @GeopoliticalEconomyReport | Geopolitical Economy Report | left | usa (14), dollar (9), corporations (9), china (7), reason (7) |
| @glennbeck | Glenn Beck | right | glenn (45), beck (31), reason (13), think (10), believe (10) |
| @GlennKirschner2 | Glenn Kirschner | left | doj (24), judge (16), court (14), blanche (12), todd (12) |
| @GrahamAllen | Graham Allen | right | candace (36), owens (31), kirk (15), erika (14), tucker (11) |
| @HangOutwithSeanHannity | Hang Out with Sean Hannity | right | carter (10), reveals (10), changed (10), nickal (9), siller (9) |
| @harryjsisson | Harry Sisson | left | omg (42), trump (36), posted (24), posts (22), leaked (20) |
| @HasanAbi | HasanAbi | left | asmongold (13), abdul (11), fox (11), going (11), talking (10) |
| @HasanabiClips | Hasanabi Clips | left | hasanabi (91), reacts (87), hasan (32), flame (17), asmongold (16) |
| @HasanAbiVODs3 | HasanAbi VODs | left | hasanabi (72), august (31), june (30), january (28), july (26) |
| @HasanReactionsfanTwo | Hasan Reactions | left | hasanabi (35), reacts (29), hasan (22), coffeezilla (11), abdul (11) |
| @hutch | Hutch | neutral | destiny (26), hasan (24), lib (21), pisco (17), learn (16) |
| @JackCocchiarellaShow | Jack Cocchiarella | left | trump (44), leaks (39), ends (32), finally (31), posts (30) |
| @JacksonHinkleOfficial | Jackson Hinkle Official | neutral | candace (25), owens (25), iran (22), erika (22), fuentes (17) |
| @JamarlThomas | Jamarl Thomas | left | garland (22), sleboda (21), nixon (20), chess (20), kiev (20) |
| @JesseKellyDC | Jesse Kelly | right | democrat (26), democrats (19), republicans (16), doj (15), red (14) |
| @JillianMichaels | Jillian Michaels | right | jillian (18), michaels (17), california (11), victor (10), wikipedia (10) |
| @jimacosta | Jim Acosta | left | acosta (29), jim (27), schmidt (21), molly (14), richardson (13) |
| @jlptalk | Jesse Lee Peterson | right | caller (25), mon (24), reacts (24), best (21), wed (18) |
| @joerogan | PowerfulJRE | neutral | mma (21), jre (13), daniel (7), protect (7), michael (6) |
| @johnnyharris | Johnny Harris | left | explained (5) |
| @judgingfreedom | Judge Napolitano - Judging Freedom | left | prof (48), col (39), johnson (34), larry (33), ritter (32) |
| @JustPearlyThings | Pearl | right | women (64), men (39), modern (25), pearl (24), obey (19) |
| @katiephangnews | Katie Phang | left | phang (23), shocking (23), epstein (21), panics (20), doj (18) |
| @katmabu | Kat Abughazaleh | left | kat (16), aipac (10), abughazaleh (10), ad (7), chicago (6) |
| @KimIversen | Kim Iversen | neutral | israel (15), epstein (12), israelis (9), massie (8), bilzerian (8) |
| @LastWeekTonight | LastWeekTonight | left | oliver (35), week (28), john (27), tonight (27), bonus (16) |
| @laurenchenclips | Lauren Chen Clips | right | odyssey (11), vigilante (9), elliot (9), christopher (9), supergirl (8) |
| @LeejaMiller | Leeja Miller | left | explainer (18), worse (4), don't (4), minnesota (3), ice (2) |
| @LegalAFMTN | Legal AF | left | trump (66), doj (54), court (51), judge (43), supreme (34) |
| @LegalEagle | LegalEagle | left | reckless (12), illegal (9), ben (8), lawyers (6), doj (6) |
| @LeverNews | The Lever | left | master (17), abdul (11), el-sayed (11), steyer (11), kingmakers (9) |
| @LiberalHivemind | Liberal Hivemind | right | holy (24), believe (22), crap (18), realized (17), happening (15) |
| @LIVESNEAKO | LIVE SNEAKO | neutral | sneako (56), tate (32), jiang (28), interviews (27), professor (26) |
| @lizwheeler | Liz Wheeler | right | plot (14), singham (12), spencer (12), pratt (12), roy (12) |
| @lonerboxlive | LonerBox Live | right | lonerbox (19), hasan (17), soypill (13), hutch (11), asmongold (11) |
| @lovettorleaveitpodcast | Lovett or Leave It | left | lovett (30), jon (23), rips (8), destroys (7), gay (6) |
| @LukeBeasley | Luke Beasley | left | sh (48), oh (42), omg (38), bonus (32), leaked (32) |
| @Lunaoi | Luna oi! | left | marxist (11), vietnam (11), theory (7) |
| @marclamonthillnetwork | Marc Lamont Hill Network | left | hill (60), marc (57), joe (37), budden (23), black (20) |
| @MarkDice | Mark Dice | right | they're (8), unloads (7), stopped (6), black (5), happened (5) |
| @markets | Bloomberg Television | neutral | stocks (54), trade (53), says (49), balance (47), ai (46) |
| @marklevinshow | The Mark Levin Show | right | levin (54), mark (46), best (24), unmasking (14), understanding (13) |
| @MattWalsh | Matt Walsh | right | trailer (11), dumbest (10), think (9), civil (9), teach (8) |
| @MegynKelly | Megyn Kelly | right | megyn (39), update (38), kelly (35), guthrie (31), nancy (27) |
| @MeidasTouch | MeidasTouch | left | trump (87), panics (53), gets (43), loses (41), hell (39) |
| @MichaelKnowles | Michael Knowles | right | knowles (36), michael (34), libs (15), mins (14), reacts (14) |
| @MichaelMaliceofficial | Michael Malice | right | malice (21), michael (14), welcome (14), punches (10), foster (8) |
| @MikeFromPA | Mike From PA | left | mike (26), hasan (22), ethan (16), jealous (15), klein (14) |
| @mikhaila | Mikhaila Peterson | right | carnivore (0) |
| @MLChristiansen | Matt Christiansen | right | guest (26), frank (16), frankly (15), quite (15), shooting (10) |
| @ModernDayDebate | Modern-Day Debate | left | debate (36), evolution (20), jake (19), feminism (18), wilson (18) |
| @morebridgetphetasy | Walk-Ins Welcome with Bridget Phetasy | right | welcome (23), generation (11), therapy (10), therapists (7), revolution (7) |
| @moreperfectunion | More Perfect Union | left | uncovered (18), investigated (14), skyrocketing (9), tracked (9), went (8) |
| @MrReaganUSA | Mr Reagan | right | black (3), maga-man (1) |
| @MrTariqNasheed | Tariq Radio | right | fba (31), fbas (29), black (24), refugee (21), african (21) |
| @msnow | MS NOW | left | dem (47), trump (43), ms (42), rep (40), fmr (37) |
| @MyronGainesX | MyronGainesX | right | myron (47), women (21), men (20), dating (19), modern (19) |
| @nationalreview | National Review | right | think (15), carlson (13), tucker (12), zohran (11), right (9) |
| @NBCNews | NBC News | neutral | morning (58), nbc (52), tom (41), headlines (37), meet (36) |
| @newdiscourses | New Discourses | right | nazi (18), experiment (17), myth (14), reads (12), milestones (11) |
| @NewsmaxTV | Newsmax | right | report (55), national (52), wake (51), rob (44), agenda (41) |
| @NewsNation | NewsNation | neutral | newsnation (79), morning (73), jesse (60), reports (56), tonight (53) |
| @newyorker | The New Yorker | neutral | yorker (22), mini (18), pack (15), essentials (14), cultural (13) |
| @NickCruseRBN | Nick Cruse | left | zionist (16), nick (15), joins (15), jamarl (14), kshama (13) |
| @NickShirley | Nick Shirley | right | irl (12), fraud (11), investigated (9), shirley (9), confronting (9) |
| @notsoErudite | notsoErudite | left | tilly (12), debate (8), liberal (7), christian (7), wilson (6) |
| @nousnetwork | nous | left | clips (39), muslims (24), muslim (14), india (13), hindutva (12) |
| @NovaraMedia | Novara Media | left | meets (23), aaron (22), labour (21), burnham (20), ash (18) |
| @NPR | NPR | left | newsmakers (14), methods (13), ilia (11), malinin (11), curious (10) |
| @nypost | New York Post | right | moment (43), ny (34), footage (28), car (24), shows (22) |
| @nytimes | The New York Times | left | anatomy (17), scene (16), broadway (10), images (6), congo (6) |
| @NYTOpinion | New York Times Opinion | left | opinion (16), nyt (14), op-docs (0), trump (-0) |
| @NYTPodcasts | New York Times Podcasts | left | serial (14), productions (12), opinions (11), guide (10), cease-fire (10) |
| @oann | One America News Network | right | president (28), gaetz (21), matt (20), oan (20), fraud (18) |
| @OfficialFlagrant | FLAGRANT | right | flagrant (13), stories (8), knicks (6), reaction (5), epstein (4) |
| @OfficialSaharTV | SaharTV | right | muslim (51), islam (38), muslims (31), tommy (30), islamist (27) |
| @OutKick | OutKick | right | travis (13), clay (13), fade (12), espn (9), football (9) |
| @OwenJonesTalks | Owen Jones | left | labour (17), farage (15), polanski (14), zack (13), israel (13) |
| @OwenReport | Owen Report | left | owen (27), shroyer (22), maga (17), israel (14), cult (13) |
| @PartOfTheProblem | Dave Smith | right | hawks (11), response (9), pathetic (7), term (5), massie (5) |
| @PBDPodcast | PBD Podcast | right | pbd (18), wire (8), opens (7), newsom (7), extends (6) |
| @PerunAU | Perun | left | economics (10), ukraine (8), arms (8), exports (7), ballistic (7) |
| @PhillipScottPodcast | Phillip Scott Podcast | right | black (28), fbas (21), woman (21), anti-black (20), folks (16) |
| @PiersMorganUncensored | Piers Morgan Uncensored | neutral | piers (28), morgan (26), plus (16), simon (13), feat (13) |
| @PiscoLitty | Pisco | left | debate (17), maga (8), lawyer (5), democratic (4), immigration (4) |
| @podsaveamerica | Pod Save America | left | trump (25), online (25), lovett (21), republicans (16), terminally (16) |
| @POLITICO | POLITICO | neutral | energy (16), conversation (10), pod (9), kemp (9), politico (8) |
| @Politicon | Politicon | left | politics (35), carville (34), room (33), james (29), hunt (23) |
| @PoliticsGirl | PoliticsGirl | left | conversation (24), kings (6), don't (6), save (5), we're (4) |
| @PoliticsJOE | PoliticsJOE | left | keir (32), pmqs (31), starmer (30), mps (24), interview (22) |
| @ponderingpolitics | Pondering Politics | left | trump (53), fox (51), sh (42), piers (36), morgan (35) |
| @PragerU | PragerU | right | parent (30), dennis (29), minute (29), videos (25), brief (25) |
| @PrisonPlanetLive | Paul Joseph Watson | right | cking (11), noticing (11), cked (8), got (6), king (6) |
| @PTLRadioShow | Pushing The Limits | left | maga (82), brian (78), shapiro (68), caller (51), supporter (30) |
| @RealAlexClark | Real Alex Clark | right | dr (14), md (12), skin (12), phd (10), kids (7) |
| @RealAmericasVoice | Real America's Voice | right | steve (52), room (49), bannon (48), stein (38), alex (36) |
| @RealDanBongino | Dan Bongino | right | bongino (12), simple (6), thing (6), dan (6), happened (6) |
| @RebelHQ | Rebel HQ | left | gets (30), fox (30), terrified (28), republicans (25), maga (24) |
| @RebelNewsOnline | Rebel News | right | canada (42), carney (40), toronto (35), ezra (33), roundtable (31) |
| @RedactedNews | Redacted | right | redacted (38), clayton (34), morris (28), col (15), coming (14) |
| @RekietaLaw | Rekieta Law | right | richins (22), kouri (22), trial (17), member (15), fitzsimmons (15) |
| @RestPoliticsUS | The Rest Is Politics US | left | trump (17), exclusive (13), members (13), panicking (10), hugely (9) |
| @Reuters | Reuters | neutral | market (34), bid (32), fans (27), reuters (27), weekly (25) |
| @revleftradio | Rev Left Radio | left | marxism (10), socialist (8), class (6), politics (4), fight (3) |
| @RileyGaines | Riley Gaines | right | riley (22), vlog (16), wnba (14), shirley (11), motherhood (11) |
| @RobertGouveiaEsq | Robert Gouveia Esq. | right | election (36), judge (30), fulton (28), appeal (27), crushed (26) |
| @rolandsmartin | Roland S. Martin | left | black (77), roland (34), voting (24), racist (21), rights (18) |
| @RonPlacone | Ron Placone | left | comedy (11), punk (10), lefty (8), amidst (8), rfk (7) |
| @RSBN | Right Side Broadcasting Network | right | president (75), event (47), delivers (37), matthew (35), speech (31) |
| @RubinReport | The Rubin Report | right | host (48), look (38), humiliated (28), zohran (26), rubin (25) |
| @RufoandLomez | Rufo & Lomez | right | left (9), right (8), splc (6), spencer (5), pratt (5) |
| @SabbySabs | Sabby Sabs | left | joins (21), mohammad (20), marandi (19), erika (19), kirk (18) |
| @SaltyCracker | Salty Cracker | right | lefty (21), man (19), antifa (16), woman (14), streamer (14) |
| @samharrisorg | Sam Harris | left | conversation (27), sam (18), harris (10), ai (8), end (5) |
| @SavSays | Sav Says | right | trial (4) |
| @SecretScholars | Warren Smith - Secret Scholar Society | right | leftist (22), wilson (17), confronts (14), exposes (13), andrew (12) |
| @SecularTalk | Secular Talk | left | kyle (48), kulinski (37), maga (30), completely (27), ck (24) |
| @Semafor | Semafor | neutral | ceo (30), economy (28), semafor (24), world (15), signal (13) |
| @Shoe0nHead | Shoe0nHead | right | cult (8) |
| @SkyNews | Sky News | left | uk (52), sky (50), starmer (48), burnham (39), mandelson (36) |
| @SMN | Some More News | left | early (23), release (17), access (9), patreon (9), normal (8) |
| @StatusCoup | Status Coup News | left | ice (48), protesters (31), breaking (19), accuser (18), delaney (18) |
| @StevenCrowder | StevenCrowder | right | crowder (10), dumbest (8), bullsh (8), islam (8), ck (8) |
| @StosselTV | John Stossel | right | classic (9), government (8), politicians (7), socialism (6), climate (6) |
| @Styxhexenhammer666 | Styxhexenhammer666 | right | food (12), lol (10), leftists (10), trumps (9), retarded (9) |
| @SydneyWatson | Sydney Watson | right | odyssey (10), supergirl (9), hollywood (7), gone (7), worse (7) |
| @TechCrunch | TechCrunch | neutral | build (31), mode (30), startup (17), ai (15), startups (13) |
| @The_Crucible | The Crucible | right | debate (21), tiktok (18), feminist (18), argument (16), owens (16) |
| @TheAdamCarollaShow1 | Adam Carolla | right | adam (48), carolla (36), drew (28), dr (16), vlog (16) |
| @TheAmalaEkpunobi | Amala Ekpunobi | right | woke (22), tiktoks (14), trans (14), leftist (12), clip (10) |
| @TheAtlantic | The Atlantic | left | atlantic (10), conversation (10), reads (9), ai (6), broke (6) |
| @TheBrianKilmeadeShow | Brian Kilmeade | right | kilmeade (20), iran (14), rove (13), karl (12), tyrus (12) |
| @TheDailyBeast | The Daily Beast | left | wolff (34), clip (29), beast (27), trump (27), know (25) |
| @TheDamageReport | The Damage Report | left | tyt (61), hour (60), rashad (42), richey (42), indisputable (42) |
| @thedavidpakmanshow | David Pakman Show | left | trump (51), they're (25), realize (20), dear (19), dementia (18) |
| @TheDonLemonShow | Don Lemon | left | donald (49), don (37), wells (35), nolan (35), lemon (25) |
| @TheEconomist | The Economist | left | ai (10), humans (7), winner (7), america (7), billionaires (6) |
| @thegrayzone7996 | The Grayzone | left | max (22), judging (14), blumenthal (12), israel (12), reed (11) |
| @theGuardian | The Guardian | left | feed (13), view (9), jimi (9), dating (9), documentary (7) |
| @thehill | The Hill | neutral | hill (48), sunrise (46), trending (42), newsnation (40), plus (37) |
| @TheHumanistReport | The Humanist Report | left | fascists (10), mafia (10), socialists (10), leftist (9), embarrassingly (9) |
| @theisabelbrown | Isabel Brown | right | baby (10), daughters (9), christian (9), kids (9), women (9) |
| @thejimmydoreshow | The Jimmy Dore Show | neutral | kirk (23), candace (22), blumenthal (22), max (20), tpusa (19) |
| @TheJoyReidShow | The Joy Reid Show | left | joy (34), reid (28), nationalism (14), countering (13), wells (13) |
| @TheLincolnProject | The Lincoln Project | left | cked (9), ck (8), epstein (7), lincoln (6), bondi (6) |
| @TheMajorityReport | The Majority Report w/ Sam Seder | left | corporate (17), dem (17), rubin (16), zohran (16), aipac (16) |
| @TheMichaelCohenShow | Michael Cohen | left | cohen (24), mea (23), culpa (17), trump (16), yikes (14) |
| @TheOfficerTatum | The Officer Tatum | right | nolan (40), wells (40), tatum (31), officer (25), clarity (24) |
| @ThePodcastoftheLotusEaters | The Podcast of the Lotus Eaters | right | breakfast (36), britain (29), restore (26), beau (23), makerfield (19) |
| @TheQuartering | TheQuartering | right | woke (31), karen (21), quartering (18), ice (17), fatigue (17) |
| @therationalnational | The Rational National | left | poilievre (19), pierre (18), ndp (17), avi (12), lewis (12) |
| @TheRealTabithaSpeaks | TabithaSpeaksPolitics | left | black (15), y'all (14), dear (11), kasparian (10), donald (10) |
| @TheSerfTimes | The Serf Times | left | hasan (20), tony (17), klein (17), rogan (17), hinchcliffe (16) |
| @TheVaushPit | The Vaush Pit | left | situation (13), wtf (13), crashing (10), lmao (10), they're (9) |
| @thewarningwithsteveschmidt | The Warning with Steve Schmidt | left | steve (46), schmidt (41), dean (33), donald (30), malcolm (17) |
| @TheYoungTurks | The Young Turks | left | tyt (69), hour (67), indisputable (46), rashad (46), richey (45) |
| @thomhartmann | Thom Hartmann Program | left | trump (17), thom (15), billionaires (13), america (11), democracy (10) |
| @Tim_Black | Tim Black TV | right | black (48), tim (20), roland (18), martin (17), fba (15) |
| @Timcast | Tim Pool | right | democrats (12), culture (8), cooked (8), leftists (7), begun (6) |
| @TimcastIRL | Timcast IRL | right | irl (32), timcast (20), leftists (17), they're (16), democrat (16) |
| @TimcastNews | Timcast | right | got (18), proves (16), democrat (13), actually (13), dude (11) |
| @TimDillonShow | The Tim Dillon Show | neutral | ray (25), dillon (17), tim (10), bonus (7), summer (6) |
| @TimesNowWorld | Times Now World | neutral | world (118), russia (89), times (82), ukraine (70), putin (60) |
| @timesofindia | Times Of India | left | big (54), putin (54), iran (48), cam (48), irgc (44) |
| @TomiLahrenIsFearless | Tomi Lahren Is Fearless | right | lahren (27), tomi (27), caitlyn (11), jenner (11), dana (11) |
| @triggerpod | Triggernometry | right | members (27), questions (27), konstantin (19), kisin (18), triggernometry (11) |
| @TuckerCarlson | Tucker Carlson | neutral | tucker (17), demons (9), israel (8), globalist (8), neocons (8) |
| @turningpointusa | Turning Point USA | right | kirk (31), charlie (30), shane (21), witt (19), abortion (18) |
| @underthedesknews | Under The Desk News | left | hot (27), geopolitical (25), fool (24), gossip (19), die (17) |
| @UnHerd | UnHerd | left | varoufakis (18), believes (9), germany (6), debate (6), europe (6) |
| @Unpacked | Unpacked | right | jews (12), jewish (12), mossad (9), reason (8), israel (8) |
| @USATODAY | USA TODAY | neutral | speech (25), conference (24), press (24), donald (22), white (18) |
| @usefulidiots | Useful Idiots | left | mat (23), aaron (21), halper (19), useful (16), israel (15) |
| @Vaush | Vaush | left | insane (11), hasan (11), actually (10), wtf (10), christ (10) |
| @VivaFrei | Viva Frei | right | viva (20), frei (20), pipe (18), jan (17), baker (16) |
| @Vox | Vox | left | actually (21), america (13), explained (12), today (11), dating (7) |
| @wethefifth | The Fifth Column - A Podcast | neutral | fifth (34), column (26), christie (11), rahm (9), chris (8) |
| @winston_marshall | Winston Marshall | right | britain (13), edition (13), portsmouth (10), members (10), elites (9) |
| @wsj | The Wall Street Journal | neutral | wsj (32), coveted (12), economics (11), pro (10), equipped (9) |
| @X22Report-y5y | X22Report | right | economic (23), ds (21), begun (18), leverage (17), gold (16) |
| @Xanderhal | Xanderhal | left | chud (21), asmongold (20), chuds (19), wing (18), slop (16) |
| @XAVIAER | Respectfully, Xaviaer | right | reacting (14), xaviaer (13), durousseau (10), nazarian (10), guess (10) |
| @ZeihanonGeopolitics | Zeihan on Geopolitics | neutral | energy (10), end (9), demographic (9), future (9), fleet (8) |
| @zeteo | Zeteo | left | mehdi (35), aipac (10), expert (9), hasan (8), genocidal (8) |
| @ZubyMusic | Zuby | right | marriage (12), wikipedia (11), zuby (10), destroying (7), modern (7) |
| https://rumble.com/c/BannonsWarRoom | BannonsWarRoom | right | bannon (59), battleground (29), sale (26), posobiec (25), going (24) |
| https://rumble.com/c/GGreenwald | GGreenwald | left | glenn (14), neocon (11), update (11), mearsheimer (9), deceitful (9) |
| https://rumble.com/c/nickjfuentes | nickjfuentes | right | imminent (18), fuentes (16), day (14), chickens (13), nick (13) |
| https://rumble.com/c/russellbrand | russellbrand | right | ss (13), coming (10), sunday (9), they're (9), really (9) |
| https://rumble.com/c/TheAlexJonesShowLive | TheAlexJonesShowLive | right | jones (55), alex (48), exclusive (19), report (17), must-watch (13) |


## Method

Tokens are lower-cased words from the normalized title (curly apostrophes normalized, possessive "'s" removed, the vocabulary stopword list of document 11 removed), pooled over a channel's unique titles in both genres. For each channel the weighted log-odds ratio of every word against all other channels' titles is computed with an informative Dirichlet prior proportional to the pooled corpus frequencies (Monroe, Colaresi and Quinn 2008, "Fightin' Words"), alpha0 = 500, and ranked by the z-score (log-odds divided by its approximate standard error). The top ten with at least three uses by the channel are kept.

## Limitations

- Show and host names survive when they were not stripped in Stage 0 (only patterns above the 20 % rule were), so some lists begin with the channel's own name; that is a real over-use, but not an interesting one.
- Small channels have few words that reach the count floor; their lists are short or dominated by one series.
- Unigrams only, and the prior's strength (alpha0) trades distinctiveness against rarity: a larger alpha0 would push common words up, a smaller one rare words.
- The comparison set is "all other channels", so a word every commentary channel uses (trump, maga) is not a signature for any of them, by design.

Files: `signature_keywords.csv`.
