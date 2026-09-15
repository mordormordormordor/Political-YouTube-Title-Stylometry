# 13. Signature title keywords per channel

**The question.** Which words does each channel use far more than everyone else?

## The finding in one paragraph

Each channel's signature is scored by weighted log-odds against all other channels' titles, with a prior that shrinks rare words, so the list is the vocabulary a channel *over-uses*, not merely uses. For most channels the top of the list is its own furniture (host names, show segments, a recurring guest), which is expected and is itself a style fact: ben, shapiro, movie, tiktoks, radical, left, majors, tucker, for Ben Shapiro, asmongold, going, talking, abdul, fox, cooked, hogs, ethan,  for Hasan Piker. Below that, the lists separate beats and registers: market, bid, reuters, fans, weekly, wall, talk, street, says, graphic for Reuters, trump, panics, gets, loses, hell, loose, collapses, furious, disaster, for MeidasTouch. The top five per channel are below; the top ten with counts are in `signature_keywords.csv` and on each creator's card.

## Every channel's top five (alphabetical)

`z` is the log-odds z-score; larger = more distinctive. Words appear only if the channel used them at least three times.

| creator | channel_name | lane | top 5 (z) |
|---|---|---|---|
| @60minutes | 60 Minutes | US legacy TV | minutes (65), episodes (35), sunday (29), laden (12), sasse (11) |
| @aaronparnas1 | Aaron Parnas | left commentary | breaking (94), furious (30), republicans (30), major (29), trump (29) |
| @ABCNews | ABC News | US legacy TV | abc (56), broadcast (53), good (50), know (43), need (43) |
| @ActualJusticeWarrior | Actual Justice Warrior | right commentary | leftist (18), black (17), entitled (17), mamdani (16), chicago (15) |
| @adammockler | Adam Mockler | left commentary | trump (37), maga (24), bomb (22), slip (21), lets (20) |
| @AfterPartyEmily | After Party with Emily Jashinsky | right commentary | plus (21), truth (21), media (17), malice (16), culture (14) |
| @ajplus | AJ+ | wires & international | gaza (9), cuba (5), africa (5), israeli (5), south (5) |
| @AlexStein99 | Alex Stein | humour / satire | stein (28), alex (24), dallas (14), prime (11), booty (10) |
| @aljazeeraenglish | Al Jazeera English | wires & international | gaza (53), israeli (44), lebanon (42), story (33), inside (32) |
| @AnaEscobarShow | Ana Escobar | right commentary | charlie (19), kirk (15), candace (14), owens (12), intel (12) |
| @AndrewKlavan | Andrew Klavan | right commentary | klavan (22), greatest (13), ranks (12), tiktoks (12), ranked (11) |
| @AndWeKnowOfficial-o9b | And We Know Official | right commentary | pray (47), silver (19), comms (19), msm (13), gold (13) |
| @ANINewsIndia | ANI News | wires & international | pm (89), modi (81), india (80), delhi (55), holds (52) |
| @AnthonyBrianLogan | Anthony Brian Logan | right commentary | instagram (19), ask (17), waymo (9), spencer (9), pratt (9) |
| @AsmonTV | Asmongold TV | streamers | ck (34), game (33), i've (24), happening (22), genuinely (20) |
| @AssociatedPress | Associated Press | wires & international | says (36), ap (31), xiv (29), shows (27), leo (24) |
| @axios | Axios | US press | axios (40), view (17), fried (15), ai (14), conversation (14) |
| @BadEmpanadaLive | BadEmpanada Live | streamers | zionist (18), palestine (13), cuba (12), signifier (12), milei (11) |
| @BadFaithPodcast | Bad Faith | interview podcasts | chomsky (12), left (12), unlocked (11), briahna (10), gabriel (9) |
| @BBCNews | BBC News | wires & international | bbc (53), global (52), uk (38), story (30), donald (20) |
| @bbrettcooper | Brett Cooper | right commentary | reacting (12), canceled (10), jelly (9), divorce (8), lively (8) |
| @BelleRanch | Belle of the Ranch | left commentary | talk (123), let (119), trump (31), saying (15), wanting (12) |
| @bennyjohnson | Benny Johnson | right commentary | internet (27), libs (27), panic (22), somali (20), fraud (19) |
| @BenShapiro | Ben Shapiro | right commentary | ben (27), shapiro (19), movie (12), tiktoks (12), radical (12) |
| @BlackConservativePerspective | Black Conservative Perspective | right commentary | woke (56), black (53), democrat (51), liberal (51), liberals (44) |
| @BlaireWhiteX | Blaire White | right commentary | trans (7) |
| @BlazeTV | BlazeTV | right commentary | beck (37), glenn (36), rino (15), radical (15), far-left (15) |
| @breakingpoints | Breaking Points | independent digital news | saagar (19), bibi (16), krystal (16), pape (16), aipac (16) |
| @BreakThroughNews | BreakThrough News | independent digital news | rania (15), khalek (15), cuba (15), lebanon (13), israel (11) |
| @briantylercohen | Brian Tyler Cohen | left commentary | announcement (44), update (44), day (37), bombshell (34), trump (32) |
| @BrittanyVenti | Brittany Venti | right commentary | thequartering (13), pearl (12), mayr (12), chrissie (11), simps (10) |
| @bulwarkmedia | The Bulwark | centrist / heterodox | tim (28), command (28), level (27), sarah (26), shield (26) |
| @bushrakhanum | Bushra Khanum | wires & international | raju (11), adeeb (10), parulekar (10), muslims (8), asia (6) |
| @cafedotcom | Stay Tuned with Preet Bharara | legal commentary | preet (19), bharara (19), joyce (14), elie (10), honig (8) |
| @CamHigby | Cam Higby | right commentary | muslim (21), lib (20), anti-ice (20), islam (18), quran (17) |
| @CashJordan | Cash Jordan | right commentary | mamdani (33), thought (28), nyc (28), mobs (18), marines (16) |
| @CaspianReport | CaspianReport | explainers / geopolitics | iran (3), america (2), war (2) |
| @CBSNews | CBS News | US legacy TV | says (31), artemis (25), latest (25), ii (24), say (24) |
| @ChadPrather1 | Chad Prather | right commentary | god (32), jesus (31), stories (18), faith (14), gospel (14) |
| @Channel5YouTube | Channel 5 with Andrew Callaghan | independent digital news | cast (13), interview (11), palestine (6), inside (5), nick (5) |
| @chicksonright | Chicks on the Right | right commentary | candace (62), owens (49), tucker (31), megyn (26), carlson (21) |
| @chinainsights-r2w | China Insights | independent digital news | china (41), insights (36), xi (21), jinping (17), beijing (14) |
| @chriscuomo | The Chris Cuomo Project | centrist / heterodox | cuomo (13), wrong (10), chris (10), midterms (9), mornings (9) |
| @clayandbuck | The Clay Travis & Buck Sexton Show | right commentary | clay (38), buck (36), travis (30), stream (28), sexton (26) |
| @ClipsCandaceOwens | Candace Clips | right commentary | erika (23), kirk (21), candace (21), charlie (18), owens (16) |
| @ClubRandomPodcast | Club Random Podcast | interview podcasts | maher (51), random (18), classics (15), club (14), allen (14) |
| @CNN | CNN | US legacy TV | roundup (28), cnn (28), fareed (23), actors (21), enten (21) |
| @ColeHastings | Cole Hastings | centrist / heterodox | gen (17), epidemic (13), crisis (5), ai (3) |
| @ColemanHughesOfficial | Coleman Hughes | interview podcasts | coleman (14), hughes (12), psychology (10), love (5), left (5) |
| @CoreyGilShusterAskProject | Corey Gil-Shuster | explainers / geopolitics | israelis (21), think (13), arab (11), solution (9), jews (9) |
| @DailyDenims | Daily Denims | streamers | ethan (25), klein (21), asmongold (20), denims (19), unhinged (13) |
| @DannyHaiphongYT | Danny Haiphong | left commentary | larry (30), marandi (28), iran (27), wilkerson (24), mohammad (23) |
| @DarkHorsePod | Bret Weinstein | centrist / heterodox | bret (37), heather (35), weinstein (35), lens (27), th (20) |
| @deanwithrs | Dean Withers | streamers | maga (59), man (33), argument (19), supporter (18), trump (15) |
| @DemocracyDocket | Democracy Docket | legal commentary | supreme (15), court (15), democracy (12), rig (11), voter (10) |
| @DemocracyNow | Democracy Now! | independent digital news | headlines (57), world (30), ice (12), gaza (11), scholar (11) |
| @destiny | Destiny | streamers | destiny (33), debate (18), hutch (14), confronts (11), i've (10) |
| @DestinyDGGClips | Destiny DGG Clips | streamers | destiny (38), hasan (29), asmongold (23), vaush (15), pisco (13) |
| @destinyhqclips | destinyhqclips | streamers | destiny (56), hasan (23), debate (17), snarker (16), snarkers (14) |
| @dineshdsouza | Dinesh D'Souza | right commentary | dinesh (22), d'souza (20), fathers (12), founding (11), series (10) |
| @dollemore | Jesse Dollemore | left commentary | donald (37), trump (32), fox (18), hegseth (16), markwayne (15) |
| @doomscrollpodcast | Joshua Citarella | interview podcasts | socialism (7), politics (5), david (5) |
| @DoubleDownNews | Double Down News | independent digital news | lowkey (13), israel (10), want (10), think (9), mossad (8) |
| @DropSiteNews | Drop Site News | independent digital news | scahill (17), gaza (16), jeremy (15), lebanon (13), israel (12) |
| @DrSteveTurleyTV | Dr. Steve Turley | right commentary | believe (32), happened (28), won't (26), muslims (15), democrats (12) |
| @DueDissidence | Due Dissidence | left commentary | tucker (18), massie (15), rex (15), jose (14), vega (14) |
| @DylanBurnsLIVE | DylanBurnsLIVE | streamers | ukraine (19), debating (13), soypill (12), dsa (10), progressive (10) |
| @evanjmez | Evan James | left commentary | ice (2), israel (2) |
| @EzraKleinShow | The Ezra Klein Show | interview podcasts | klein (10), ezra (7), wants (4), america (2), war (1) |
| @FarronBalanced | Farron Balanced | left commentary | trump (46), republicans (33), admits (16), staffers (16), completely (16) |
| @fastpoliticspodcast | Fast Politics w/ Molly Jong-Fast | left commentary | rick (33), wilson (31), sykes (19), acosta (18), trump (14) |
| @fightbackpodcast | Jake Shields' Fight Back Podcast | right commentary | jake (53), shields (42), fight (29), owen (22), bilzerian (22) |
| @FinancialTimes | Financial Times | wires & international | rethink (11), energy (8), source (8), tech (7), ai (6) |
| @Firstpost | Firstpost | wires & international | africa (69), india (68), sharma (59), sports (55), iran (52) |
| @FleccasTalks | Fleccas Talks | right commentary | stu (10), richard (9), cop (7), migrant (6), dumb (6) |
| @Forbes | Forbes | US press | billionaire (35), billion (32), ai (29), forbes (23), business (22) |
| @Forthepeoplepodcast305 | Niko House | left commentary | pasta (17), drive (15), niko (9), jardula (9), time (9) |
| @FoxNews | Fox News | US legacy TV | watters (33), gutfeld (33), breaking (32), details (31), iranian (28) |
| @FoxNewsChannelClips | Fox News Clips | US legacy TV | expert (33), laura (32), ingraham (29), dems (24), says (23) |
| @franifio | The Bitchuation Room (with Francesca Fiorentini) | humour / satire | corner (17), feat (17), vigeland (14), emma (14), wajahat (13) |
| @FreshFitMiami | FreshandFit | right commentary | myron (22), men (21), women (19), fit (19), girls (19) |
| @GeopoliticalEconomyReport | Geopolitical Economy Report | independent digital news | usa (15), dollar (9), corporations (9), china (8), reason (7) |
| @glennbeck | Glenn Beck | right commentary | glenn (46), beck (31), reason (13), think (10), believe (10) |
| @GlennKirschner2 | Glenn Kirschner | legal commentary | doj (24), judge (17), court (14), pirro (12), blanche (12) |
| @GrahamAllen | Graham Allen | right commentary | candace (35), owens (30), kirk (14), erika (13), tucker (10) |
| @HangOutwithSeanHannity | Hang Out with Sean Hannity | interview podcasts | carter (11), reveals (10), changed (10), nickal (9), siller (9) |
| @harryjsisson | Harry Sisson | left commentary | omg (42), trump (37), posted (24), leaked (22), posts (22) |
| @HasanAbi | HasanAbi | streamers | asmongold (13), going (11), talking (11), abdul (11), fox (11) |
| @HasanabiClips | Hasanabi Clips | streamers | hasanabi (93), reacts (87), hasan (32), flame (18), asmongold (16) |
| @HasanAbiVODs3 | HasanAbi VODs | streamers | hasanabi (76), august (31), june (30), january (28), july (26) |
| @HasanReactionsfanTwo | Hasan Reactions | streamers | hasanabi (37), reacts (31), hasan (22), coffeezilla (11), abdul (11) |
| @hutch | Hutch | streamers | destiny (27), hasan (25), lib (22), pisco (18), learn (16) |
| @JackCocchiarellaShow | Jack Cocchiarella | left commentary | trump (46), leaks (41), ends (34), posts (31), finally (31) |
| @JacksonHinkleOfficial | Jackson Hinkle Official | right commentary | candace (30), owens (30), erika (24), iran (22), kirk (21) |
| @JamarlThomas | Jamarl Thomas | left commentary | garland (22), sleboda (22), nixon (20), chess (20), kiev (20) |
| @JesseKellyDC | Jesse Kelly | right commentary | democrat (27), democrats (19), republicans (16), red (15), state (15) |
| @JillianMichaels | Jillian Michaels | interview podcasts | jillian (19), michaels (17), macdonald (12), california (10), victor (10) |
| @jimacosta | Jim Acosta | left commentary | acosta (29), jim (28), schmidt (21), molly (14), richardson (14) |
| @jlptalk | Jesse Lee Peterson | right commentary | reacts (26), caller (25), mon (25), best (21), wed (18) |
| @joerogan | PowerfulJRE | interview podcasts | mma (22), jre (13), michael (7), daniel (7), protect (7) |
| @johnnyharris | Johnny Harris | explainers / geopolitics | explained (6) |
| @judgingfreedom | Judge Napolitano - Judging Freedom | interview podcasts | prof (49), col (41), johnson (35), larry (34), ritter (33) |
| @JustPearlyThings | Pearl | right commentary | women (66), men (40), modern (28), pearl (25), dating (20) |
| @katiephangnews | Katie Phang | left commentary | phang (24), shocking (23), panics (21), epstein (20), doj (20) |
| @katmabu | Kat Abughazaleh | left commentary | kat (16), abughazaleh (10), aipac (10), ad (7), chicago (6) |
| @KimIversen | Kim Iversen | centrist / heterodox | israel (15), epstein (12), israelis (9), infiltrated (8), bilzerian (8) |
| @LastWeekTonight | LastWeekTonight | humour / satire | oliver (35), week (28), john (27), tonight (27), bonus (16) |
| @laurenchenclips | Lauren Chen Clips | right commentary | odyssey (11), vigilante (9), elliot (9), christopher (9), supergirl (8) |
| @LeejaMiller | Leeja Miller | legal commentary | explainer (18), worse (5), think (5), explained (5), minnesota (4) |
| @LegalAFMTN | Legal AF | legal commentary | trump (68), doj (56), court (51), judge (45), supreme (34) |
| @LegalEagle | LegalEagle | legal commentary | reckless (12), illegal (9), ben (7), legal (7), lawyer (7) |
| @LeverNews | The Lever | independent digital news | master (17), abdul (11), el-sayed (11), steyer (11), kingmakers (9) |
| @LiberalHivemind | Liberal Hivemind | right commentary | holy (25), believe (22), crap (20), realized (17), entire (16) |
| @LIVESNEAKO | LIVE SNEAKO | streamers | sneako (56), tate (32), jiang (28), interviews (27), professor (26) |
| @lizwheeler | Liz Wheeler | right commentary | plot (13), singham (12), spencer (12), pratt (12), roy (12) |
| @lonerboxlive | LonerBox Live | streamers | lonerbox (19), hasan (17), soypill (13), hutch (11), asmongold (11) |
| @lovettorleaveitpodcast | Lovett or Leave It | humour / satire | lovett (31), jon (24), rips (8), destroys (7), tig (7) |
| @LukeBeasley | Luke Beasley | left commentary | sh (48), oh (43), omg (38), members (35), bonus (34) |
| @Lunaoi | Luna oi! | left commentary | marxist (11), vietnam (11), theory (7), war (1) |
| @marclamonthillnetwork | Marc Lamont Hill Network | left commentary | hill (62), marc (59), joe (38), lamont (24), budden (23) |
| @MarkDice | Mark Dice | right commentary | fragility (10), they're (8), unloads (6), stopped (6), black (5) |
| @markets | Bloomberg Television | US press | stocks (56), trade (54), says (50), balance (48), ai (47) |
| @marklevinshow | The Mark Levin Show | right commentary | levin (55), mark (47), best (24), unmasking (14), understanding (13) |
| @MattWalsh | Matt Walsh | right commentary | trailer (12), dumbest (11), think (10), history (9), civil (9) |
| @MegynKelly | Megyn Kelly | right commentary | megyn (40), update (39), kelly (35), guthrie (31), nancy (27) |
| @MeidasTouch | MeidasTouch | left commentary | trump (90), panics (53), gets (45), loses (43), hell (39) |
| @MichaelKnowles | Michael Knowles | right commentary | knowles (38), michael (36), libs (15), mins (14), reacts (14) |
| @MichaelMaliceofficial | Michael Malice | interview podcasts | malice (23), michael (17), welcome (17), punches (9), halperin (9) |
| @MikeFromPA | Mike From PA | streamers | mike (26), hasan (22), ethan (16), jealous (15), klein (14) |
| @mikhaila | Mikhaila Peterson | interview podcasts | carnivore (0) |
| @MLChristiansen | Matt Christiansen | right commentary | guest (27), frank (16), frankly (15), quite (14), seattle (10) |
| @ModernDayDebate | Modern-Day Debate | streamers | debate (37), evolution (20), feminism (19), jake (19), wilson (18) |
| @morebridgetphetasy | Walk-Ins Welcome with Bridget Phetasy | interview podcasts | welcome (23), generation (11), therapy (10), therapists (8), works (7) |
| @moreperfectunion | More Perfect Union | independent digital news | uncovered (18), investigated (16), went (10), shock (9), skyrocketing (9) |
| @MrReaganUSA | Mr Reagan | right commentary | black (3), maga-man (1) |
| @MrTariqNasheed | Tariq Radio | left commentary | fba (31), fbas (30), black (26), african (22), caller (21) |
| @msnow | MS NOW | US legacy TV | dem (48), trump (43), ms (42), rep (41), fmr (38) |
| @MyronGainesX | MyronGainesX | right commentary | myron (49), women (22), men (20), dating (20), modern (19) |
| @nationalreview | National Review | US press | think (15), carlson (13), tucker (12), zohran (11), right (8) |
| @NBCNews | NBC News | US legacy TV | morning (60), nbc (53), tom (42), headlines (38), meet (37) |
| @newdiscourses | New Discourses | right commentary | nazi (19), experiment (17), myth (14), vol (13), woke (13) |
| @NewsmaxTV | Newsmax | right TV networks | report (56), national (52), wake (52), rob (48), agenda (42) |
| @NewsNation | NewsNation | US legacy TV | newsnation (83), morning (78), jesse (59), reports (59), tonight (53) |
| @newyorker | The New Yorker | US press | yorker (22), mini (18), pack (15), essentials (14), cultural (13) |
| @NickCruseRBN | Nick Cruse | left commentary | nick (16), zionist (16), joins (15), jamarl (14), kshama (13) |
| @NickShirley | Nick Shirley | right commentary | irl (14), fraud (11), investigated (11), confronting (11), shirley (9) |
| @notsoErudite | notsoErudite | streamers | tilly (12), debate (9), nationalism (8), christian (8), liberal (7) |
| @nousnetwork | nous | explainers / geopolitics | clips (39), muslims (24), muslim (14), india (13), hindutva (12) |
| @NovaraMedia | Novara Media | independent digital news | aaron (23), meets (23), labour (22), burnham (20), ash (19) |
| @NPR | NPR | US press | newsmakers (14), methods (13), ilia (11), malinin (11), curious (10) |
| @nypost | New York Post | US press | moment (44), ny (36), footage (28), car (25), shows (22) |
| @nytimes | The New York Times | US press | anatomy (18), scene (17), broadway (10), images (6), congo (6) |
| @NYTOpinion | New York Times Opinion | US press | opinion (16), nyt (14), op-docs (1), trump (-0) |
| @NYTPodcasts | New York Times Podcasts | US press | serial (14), productions (12), guide (11), opinions (11), books (11) |
| @oann | One America News Network | right TV networks | president (29), gaetz (23), matt (21), oan (21), fraud (18) |
| @OfficialFlagrant | FLAGRANT | humour / satire | flagrant (14), stories (8), knicks (6), reaction (5), epstein (3) |
| @OfficialSaharTV | SaharTV | right commentary | muslim (53), islam (40), muslims (32), tommy (31), islamist (30) |
| @OutKick | OutKick | right commentary | clay (14), travis (13), gaines (13), fade (12), espn (9) |
| @OwenJonesTalks | Owen Jones | left commentary | labour (17), farage (15), israel (14), polanski (14), zack (13) |
| @OwenReport | Owen Report | right commentary | owen (29), shroyer (23), maga (18), israel (15), cult (13) |
| @PartOfTheProblem | Dave Smith | right commentary | hawks (12), horton (10), response (9), pathetic (7), massie (5) |
| @PBDPodcast | PBD Podcast | interview podcasts | pbd (22), wire (8), opens (7), newsom (7), tucker (6) |
| @PerunAU | Perun | explainers / geopolitics | economics (10), ukraine (9), arms (8), exports (7), ballistic (7) |
| @PhillipScottPodcast | Phillip Scott Podcast | left commentary | black (29), woman (22), fbas (21), anti-black (20), folks (20) |
| @PiersMorganUncensored | Piers Morgan Uncensored | interview podcasts | piers (28), morgan (27), plus (16), feat (14), simon (13) |
| @PiscoLitty | Pisco | streamers | debate (18), maga (8), lawyer (5), democratic (4), immigration (4) |
| @podsaveamerica | Pod Save America | left commentary | online (26), trump (26), lovett (22), republicans (17), terminally (16) |
| @POLITICO | POLITICO | US press | energy (16), conversation (11), pod (9), kemp (9), politico (8) |
| @Politicon | Politicon | interview podcasts | politics (36), carville (36), room (34), james (31), hunt (23) |
| @PoliticsGirl | PoliticsGirl | left commentary | conversation (24), don't (7), kings (6), save (5), we're (4) |
| @PoliticsJOE | PoliticsJOE | independent digital news | keir (32), pmqs (32), starmer (31), mps (24), labour (22) |
| @ponderingpolitics | Pondering Politics | left commentary | trump (55), fox (52), sh (42), piers (37), morgan (36) |
| @PragerU | PragerU | right commentary | parent (30), dennis (30), minute (29), brief (26), videos (25) |
| @PrisonPlanetLive | Paul Joseph Watson | right commentary | cking (11), noticing (11), cked (8), sick (7), got (6) |
| @PTLRadioShow | Pushing The Limits | left commentary | maga (85), brian (81), shapiro (72), caller (52), supporter (31) |
| @RealAlexClark | Real Alex Clark | right commentary | dr (15), md (12), skin (12), phd (10), tricks (9) |
| @RealAmericasVoice | Real America's Voice | right TV networks | steve (52), room (48), bannon (48), stein (38), charlie (38) |
| @RealDanBongino | Dan Bongino | right commentary | bongino (12), simple (6), thing (6), happened (6), i've (6) |
| @RebelHQ | Rebel HQ | left commentary | fox (32), gets (31), terrified (28), republicans (26), host (26) |
| @RebelNewsOnline | Rebel News | independent digital news | canada (44), carney (40), toronto (36), ezra (34), rebel (33) |
| @RedactedNews | Redacted | independent digital news | redacted (45), clayton (36), morris (29), coming (16), col (15) |
| @RekietaLaw | Rekieta Law | legal commentary | richins (22), kouri (22), trial (17), fitzsimmons (15), member (15) |
| @RestPoliticsUS | The Rest Is Politics US | centrist / heterodox | trump (18), exclusive (13), members (13), panicking (10), hugely (9) |
| @Reuters | Reuters | wires & international | market (35), bid (32), reuters (28), fans (27), weekly (26) |
| @revleftradio | Rev Left Radio | interview podcasts | marxism (10), socialist (8), class (6), politics (4), fight (3) |
| @RileyGaines | Riley Gaines | right commentary | riley (22), vlog (16), wnba (14), shirley (11), motherhood (11) |
| @RobertGouveiaEsq | Robert Gouveia Esq. | legal commentary | election (37), judge (33), fulton (29), appeal (27), crushed (26) |
| @rolandsmartin | Roland S. Martin | independent digital news | black (79), roland (34), voting (24), racist (22), crockett (19) |
| @RonPlacone | Ron Placone | humour / satire | comedy (11), punk (10), lefty (8), amidst (8), fascism (7) |
| @RSBN | Right Side Broadcasting Network | right TV networks | president (78), event (46), replay (38), delivers (37), matthew (36) |
| @RubinReport | The Rubin Report | right commentary | host (49), look (38), humiliated (29), rubin (26), zohran (26) |
| @RufoandLomez | Rufo & Lomez | right commentary | left (8), right (8), dei (7), splc (6), decline (6) |
| @SabbySabs | Sabby Sabs | left commentary | joins (21), mohammad (20), erika (20), marandi (19), kirk (19) |
| @SaltyCracker | Salty Cracker | streamers | lefty (22), man (19), antifa (17), woman (15), streamer (14) |
| @samharrisorg | Sam Harris | interview podcasts | conversation (27), sam (20), harris (11), ai (8), end (5) |
| @SavSays | Sav Says | right commentary | trial (4) |
| @SecularTalk | Secular Talk | left commentary | kyle (48), kulinski (38), maga (31), completely (27), ck (26) |
| @Semafor | Semafor | US press | ceo (30), economy (28), semafor (24), world (17), signal (13) |
| @Shoe0nHead | Shoe0nHead | centrist / heterodox | cult (8) |
| @SkyNews | Sky News | wires & international | uk (53), sky (52), starmer (49), burnham (39), analysis (36) |
| @SMN | Some More News | humour / satire | early (23), release (16), access (9), patreon (9), normal (8) |
| @StatusCoup | Status Coup News | independent digital news | ice (51), protesters (30), breaking (18), accuser (18), delaney (18) |
| @StevenCrowder | StevenCrowder | right commentary | crowder (12), dumbest (8), bullsh (8), ck (8), islam (8) |
| @StosselTV | John Stossel | right commentary | classic (9), government (9), capitalism (8), socialism (7), politicians (7) |
| @Styxhexenhammer666 | Styxhexenhammer666 | right commentary | occult (14), food (11), junior (10), wednesday (10), leftists (10) |
| @SydneyWatson | Sydney Watson | right commentary | odyssey (10), supergirl (9), mad (7), hollywood (7), gone (7) |
| @TechCrunch | TechCrunch | US press | build (32), mode (31), startup (18), ai (16), startups (14) |
| @The_Crucible | The Crucible | streamers | debate (22), tiktok (18), feminist (18), argument (16), candace (16) |
| @TheAdamCarollaShow1 | Adam Carolla | interview podcasts | adam (50), carolla (37), drew (29), dr (17), vlog (16) |
| @TheAmalaEkpunobi | Amala Ekpunobi | right commentary | woke (23), trans (15), tiktoks (14), leftist (13), clip (12) |
| @TheAtlantic | The Atlantic | US press | atlantic (10), conversation (10), reads (9), ai (6), broke (5) |
| @TheBrianKilmeadeShow | Brian Kilmeade | right commentary | kilmeade (21), iran (15), rove (13), karl (12), tyrus (12) |
| @TheDailyBeast | The Daily Beast | US press | wolff (35), clip (34), beast (29), trump (29), know (25) |
| @TheDamageReport | The Damage Report | left commentary | tyt (63), hour (62), rashad (43), richey (43), indisputable (43) |
| @thedavidpakmanshow | David Pakman Show | left commentary | trump (53), they're (25), realize (20), dementia (19), dear (18) |
| @TheDonLemonShow | Don Lemon | left commentary | donald (50), don (39), wells (35), nolan (35), lemon (28) |
| @TheEconomist | The Economist | wires & international | ai (10), humans (7), winner (7), america (6), billionaires (6) |
| @thegrayzone7996 | The Grayzone | independent digital news | max (22), judging (14), blumenthal (12), israel (12), reed (11) |
| @theGuardian | The Guardian | wires & international | feed (13), view (9), jimi (9), dating (9), documentary (7) |
| @thehill | The Hill | US press | hill (49), sunrise (47), trending (43), newsnation (40), plus (37) |
| @TheHumanistReport | The Humanist Report | left commentary | fascists (10), mafia (10), right-wing (10), socialists (10), leftist (9) |
| @theisabelbrown | Isabel Brown | right commentary | baby (11), christian (10), kids (10), daughters (9), women (8) |
| @thejimmydoreshow | The Jimmy Dore Show | left commentary | kirk (26), candace (25), erika (22), blumenthal (21), massie (20) |
| @TheJoyReidShow | The Joy Reid Show | left commentary | joy (35), reid (29), nationalism (16), countering (14), wells (13) |
| @TheLincolnProject | The Lincoln Project | centrist / heterodox | cked (9), ck (8), epstein (7), lincoln (6), era (5) |
| @TheMajorityReport | The Majority Report w/ Sam Seder | left commentary | dem (17), corporate (17), rubin (17), zohran (16), aipac (15) |
| @TheMichaelCohenShow | Michael Cohen | left commentary | mea (25), cohen (24), culpa (22), trump (18), yikes (14) |
| @TheOfficerTatum | The Officer Tatum | right commentary | nolan (40), wells (40), tatum (32), officer (26), clarity (24) |
| @ThePodcastoftheLotusEaters | The Podcast of the Lotus Eaters | right commentary | breakfast (36), britain (29), restore (26), beau (23), makerfield (19) |
| @TheQuartering | TheQuartering | right commentary | woke (32), karen (20), fatigue (18), quartering (17), ice (17) |
| @therationalnational | The Rational National | left commentary | poilievre (19), pierre (18), ndp (17), lewis (12), avi (12) |
| @TheRealTabithaSpeaks | TabithaSpeaksPolitics | left commentary | black (16), y'all (14), dear (12), donald (10), kasparian (10) |
| @TheSerfTimes | The Serf Times | streamers | hasan (20), tony (17), klein (17), rogan (16), hinchcliffe (16) |
| @TheVaushPit | The Vaush Pit | streamers | situation (15), wtf (14), insane (11), crashing (10), lmao (10) |
| @thewarningwithsteveschmidt | The Warning with Steve Schmidt | centrist / heterodox | steve (47), schmidt (41), dean (33), donald (30), malcolm (17) |
| @TheYoungTurks | The Young Turks | left commentary | tyt (71), hour (69), indisputable (47), rashad (47), richey (47) |
| @thomhartmann | Thom Hartmann Program | left commentary | trump (18), thom (15), billionaires (13), democracy (11), america (11) |
| @Tim_Black | Tim Black TV | left commentary | black (50), tim (20), roland (18), martin (17), crockett (15) |
| @Timcast | Tim Pool | right commentary | democrats (12), culture (10), pool (8), cooked (8), leftists (7) |
| @TimcastIRL | Timcast IRL | right commentary | irl (32), timcast (20), leftists (16), democrat (16), they're (15) |
| @TimcastNews | Timcast | right commentary | got (17), proves (16), actually (13), democrat (13), dude (12) |
| @TimDillonShow | The Tim Dillon Show | humour / satire | ray (25), dillon (17), tim (10), bonus (7), summer (6) |
| @TimesNowWorld | Times Now World | wires & international | russia (92), world (78), ukraine (73), putin (65), nato (56) |
| @timesofindia | Times Of India | wires & international | putin (58), big (56), cam (49), iran (47), irgc (44) |
| @TomiLahrenIsFearless | Tomi Lahren Is Fearless | right commentary | lahren (28), tomi (27), caitlyn (11), jenner (11), dana (11) |
| @triggerpod | Triggernometry | interview podcasts | members (27), questions (27), konstantin (17), kisin (14), triggernometry (11) |
| @TuckerCarlson | Tucker Carlson | interview podcasts | tucker (17), demons (9), globalist (8), israel (8), neocons (8) |
| @turningpointusa | Turning Point USA | right commentary | kirk (34), charlie (34), amfest (24), shane (20), abortion (19) |
| @underthedesknews | Under The Desk News | independent digital news | hot (27), geopolitical (25), fool (24), gossip (19), die (17) |
| @UnHerd | UnHerd | centrist / heterodox | varoufakis (19), believes (9), germany (7), europe (7), debate (6) |
| @Unpacked | Unpacked | explainers / geopolitics | jews (12), jewish (11), mossad (9), israel (8), reason (8) |
| @USATODAY | USA TODAY | US press | speech (25), conference (24), press (24), donald (22), white (18) |
| @usefulidiots | Useful Idiots | interview podcasts | mat (24), aaron (22), idiots (19), useful (19), halper (19) |
| @Vaush | Vaush | streamers | hasan (11), insane (11), christ (11), wtf (11), actually (10) |
| @VivaFrei | Viva Frei | legal commentary | viva (21), frei (21), jan (18), pipe (18), baker (16) |
| @Vox | Vox | US press | actually (21), america (13), explained (12), today (11), dating (6) |
| @wethefifth | The Fifth Column - A Podcast | centrist / heterodox | fifth (34), column (27), christie (11), moynihan (10), rahm (9) |
| @winston_marshall | Winston Marshall | interview podcasts | britain (15), edition (13), portsmouth (10), members (9), elites (9) |
| @wsj | The Wall Street Journal | US press | wsj (32), coveted (12), economics (11), equipped (11), pro (10) |
| @X22Report-y5y | X22Report | right commentary | economic (25), ds (21), begun (18), leverage (17), narrative (17) |
| @Xanderhal | Xanderhal | streamers | chud (21), asmongold (21), chuds (19), wing (18), right (16) |
| @XAVIAER | Respectfully, Xaviaer | right commentary | reacting (14), xaviaer (13), durousseau (10), nazarian (10), guess (10) |
| @ZeihanonGeopolitics | Zeihan on Geopolitics | explainers / geopolitics | energy (10), end (10), shadow (9), fleet (9), demographic (9) |
| @zeteo | Zeteo | independent digital news | mehdi (37), aipac (10), prem (9), expert (8), hasan (8) |
| @ZubyMusic | Zuby | interview podcasts | zuby (12), marriage (11), wikipedia (11), bitcoin (8), destroying (7) |
| https://rumble.com/c/BannonsWarRoom | BannonsWarRoom | right commentary | bannon (60), battleground (29), sale (26), going (25), posobiec (25) |
| https://rumble.com/c/GGreenwald | GGreenwald | independent digital news | glenn (14), neocon (11), update (11), mearsheimer (9), deceitful (9) |
| https://rumble.com/c/nickjfuentes | nickjfuentes | right commentary | imminent (18), fuentes (16), day (14), chickens (14), nick (13) |
| https://rumble.com/c/russellbrand | russellbrand | centrist / heterodox | ss (13), coming (10), sunday (9), they're (9), really (9) |
| https://rumble.com/c/TheAlexJonesShowLive | TheAlexJonesShowLive | right commentary | jones (56), alex (49), exclusive (20), report (17), must-watch (15) |


## Method

Tokens are lower-cased words from the normalised title (curly apostrophes normalised, possessive "'s" removed, the vocabulary stopword list of document 11 removed), pooled over a channel's unique titles in both genres. For each channel the weighted log-odds ratio of every word against all other channels' titles is computed with an informative Dirichlet prior proportional to the pooled corpus frequencies (Monroe, Colaresi and Quinn 2008, "Fightin' Words"), alpha0 = 500, and ranked by the z-score (log-odds divided by its approximate standard error). The top ten with at least three uses by the channel are kept.

## Limitations

- Show and host names survive when they were not stripped in Stage 0 (only patterns above the 20 % rule were), so some lists begin with the channel's own name; that is a real over-use, but not an interesting one.
- Small channels have few words that reach the count floor; their lists are short or dominated by one series.
- Unigrams only, and the prior's strength (alpha0) trades distinctiveness against rarity: a larger alpha0 would push common words up, a smaller one rare words.
- The comparison set is "all other channels", so a word every commentary channel uses (trump, maga) is not a signature for any of them, by design.

Files: `signature_keywords.csv`.
