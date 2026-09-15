"""Word lists for the title-level style features (Stage 2).

Every list is documented in the methods appendix verbatim from this file. Matching
is on lower-cased word tokens (multi-word entries are matched as phrases on the
lower-cased title). Humor is NOT lexicon-scored anywhere: it is an LLM flag only.
"""

FIRST_SG = {"i", "me", "my", "mine", "myself", "i'm", "i’m", "i've", "i’ve", "i'll", "i’ll", "i'd", "i’d", "im"}
FIRST_PL = {"we", "us", "our", "ours", "ourselves", "we're", "we’re", "we've", "we’ve", "we'll", "we’ll", "let's", "let’s", "lets"}
SECOND = {"you", "your", "yours", "yourself", "you're", "you’re", "you've", "you’ve", "you'll", "you’ll", "you'd", "you’d", "u", "ur", "ya", "y'all", "yall"}

QUESTION_START = {"who", "what", "when", "where", "why", "how", "which", "whose", "is", "are", "was", "were", "do", "does",
                  "did", "can", "could", "should", "will", "would", "has", "have", "had", "am", "isn't", "aren't", "doesn't",
                  "don't", "didn't", "can't", "couldn't", "shouldn't", "wouldn't"}
WH_WORDS = {"who", "what", "when", "where", "why", "how", "which", "whose"}

IMPERATIVE_START = {"watch", "listen", "look", "stop", "don't", "dont", "do", "let's", "lets", "let’s", "check", "imagine", "meet",
                    "try", "remember", "forget", "see", "read", "join", "tell", "get", "make", "take", "learn", "please",
                    "subscribe", "wake", "think", "leave", "help", "vote", "stand", "say", "never", "beware", "prepare",
                    "guess", "hear", "buckle", "call", "ask", "run", "give"}

INTENSIFIERS = {"very", "extremely", "totally", "absolutely", "literally", "completely", "utterly", "insanely", "incredibly",
                "massively", "seriously", "so", "really", "truly", "super", "hugely", "wildly", "deeply", "ridiculously",
                "shockingly", "brutally", "unbelievably", "perfectly", "entirely", "obviously", "actually", "genuinely",
                "officially", "finally", "completely", "fully", "purely", "way", "damn", "hella", "mega", "ultra", "100%"}
SUPERLATIVES = {"best", "worst", "most", "least", "biggest", "greatest", "largest", "smallest", "highest", "lowest", "ever",
                "all-time", "record", "unprecedented", "historic", "ultimate", "top", "#1", "first-ever", "strongest",
                "weakest", "craziest", "dumbest", "funniest", "scariest", "wildest", "hardest", "richest", "deadliest"}

SHOCK_WORDS = {"insane", "crazy", "shocking", "shock", "shocked", "unbelievable", "bombshell", "explosive", "massive", "huge",
               "epic", "wild", "brutal", "devastating", "terrifying", "horrifying", "disgusting", "outrageous", "unhinged",
               "bizarre", "chaos", "meltdown", "disaster", "nightmare", "catastrophe", "stunning", "jaw-dropping",
               "mind-blowing", "viral", "urgent", "emergency", "alert", "warning", "exposed", "secret", "hidden", "banned",
               "forbidden", "leaked", "caught", "scandal", "collapse", "panic", "horror", "madness", "insanity", "war",
               "attack", "crisis", "danger", "dangerous", "deadly", "rampage", "fury", "furious", "rage", "explodes",
               "erupts", "backlash", "revenge", "nuke", "nukes", "destroy", "destroyed", "wrecked", "humiliated"}

POS_EVAL = {"great", "amazing", "brilliant", "perfect", "incredible", "beautiful", "powerful", "genius", "hilarious", "heroic",
            "wonderful", "awesome", "fantastic", "excellent", "epic", "legendary", "inspiring", "smart", "honest", "brave",
            "based", "good", "best", "masterpiece", "masterclass", "iconic", "glorious", "elite", "goated"}
NEG_EVAL = {"bad", "terrible", "horrible", "awful", "pathetic", "disgusting", "stupid", "dumb", "idiotic", "evil", "corrupt",
            "fake", "sick", "vile", "embarrassing", "humiliating", "insane", "crazy", "dangerous", "disgraceful", "ridiculous",
            "absurd", "delusional", "unhinged", "racist", "fascist", "cringe", "worst", "weak", "cowardly", "coward", "liar",
            "lies", "lying", "fraud", "grift", "grifter", "clown", "clueless", "shameful", "shameless", "hypocrite", "hypocrisy",
            "toxic", "creepy", "gross", "deranged", "psycho", "loser", "cult", "traitor", "treason", "criminal", "crooked",
            "moron", "idiot", "garbage", "trash", "scam", "scum", "nazi", "communist", "woke", "radical", "extremist"}

NEGATION = {"not", "no", "never", "nothing", "nobody", "none", "neither", "nor", "without", "cannot", "can't", "can’t", "won't",
            "won’t", "don't", "don’t", "doesn't", "doesn’t", "isn't", "isn’t", "aren't", "aren’t", "wasn't", "wasn’t", "didn't",
            "didn’t", "couldn't", "shouldn't", "wouldn't", "ain't", "ain’t", "n't", "nope", "nah", "stop", "fails", "failed", "refuses"}

VIOLENCE_VERBS = {"slams", "slam", "slammed", "destroys", "destroy", "destroyed", "exposes", "exposed", "expose", "shreds",
                  "shred", "shredded", "blasts", "blast", "blasted", "rips", "rip", "ripped", "obliterates", "obliterated",
                  "humiliates", "humiliated", "torches", "torched", "roasts", "roasted", "wrecks", "wrecked", "eviscerates",
                  "eviscerated", "crushes", "crushed", "owns", "owned", "dismantles", "dismantled", "demolishes", "demolished",
                  "annihilates", "annihilated", "attacks", "attacked", "erupts", "erupted", "explodes", "exploded", "rages",
                  "snaps", "snapped", "panics", "backfires", "busted", "nukes", "nuked", "drags", "dragged", "mocks", "mocked",
                  "trolls", "trolled", "schools", "schooled", "confronts", "confronted", "silences", "silenced", "scorches",
                  "dunks", "cooked", "ratioed", "smacks", "smacked", "wrecking", "destroying", "exposing", "slamming", "ripping",
                  "blasting", "grills", "grilled", "torpedoes", "hammers", "hammered", "bodies", "bodied", "flips", "unloads",
                  "ends", "ended", "fires", "fired", "sues", "sued", "threatens", "threatened", "melts", "loses", "lost",
                  "flames", "flamed", "rocks", "rocked", "stuns", "stunned", "shocks", "shocked", "clowns", "clowned", "gets",
                  "got"}
VIOLENCE_PHRASES = ["calls out", "called out", "melts down", "melted down", "loses it", "lost it", "freaks out", "freaked out",
                    "shuts down", "shut down", "blows up", "blew up", "goes off", "went off", "goes nuclear", "flips out",
                    "breaks down", "tears into", "tore into", "lays into", "goes after", "went after", "smacks down",
                    "takes down", "took down", "puts on blast", "in shambles", "gets wrecked", "gets destroyed",
                    "gets owned", "gets humiliated", "gets exposed", "gets caught", "gets busted"]
# 'gets'/'got'/'ends'/'fires'/'loses'/'lost' above are noisy on their own; they count only inside VIOLENCE_PHRASES
VIOLENCE_VERBS -= {"gets", "got", "ends", "ended", "fires", "fired", "sues", "sued", "loses", "lost", "melts"}

HEDGES = {"may", "might", "could", "reportedly", "allegedly", "appears", "appear", "seems", "seem", "possibly", "likely",
          "perhaps", "potentially", "suggests", "suggest", "claims", "claim", "claimed", "apparently", "expected", "would",
          "rumored", "rumoured", "maybe", "probably", "unlikely", "supposedly", "purported", "reported", "sources",
          "alleged", "so-called", "considers", "weighs", "mulls", "eyes", "signals", "hints", "warns", "predicts"}

DISCOURSE = {"let's", "lets", "let’s", "chat", "okay", "ok", "guys", "lol", "lmao", "lmfao", "bro", "dude", "yo", "wow", "omg",
             "holy", "wtf", "ngl", "fr", "tbh", "bruh", "cooked", "based", "cringe", "ratio", "yikes", "oof", "welp", "ugh",
             "hmm", "uh", "um", "oh", "yeah", "yep", "nope", "nah", "damn", "dang", "gg", "pog", "rip", "goated", "sus",
             "y'all", "folks", "friends", "everyone", "hey", "hi", "hello", "sooo", "soooo", "ahh", "ahhh", "haha", "hahaha"}

HOWTO_PHRASES = ["how to", "how i", "how we", "how you"]
EXPLAINER_PHRASES = ["explained", "explainer", "explains", "explaining", "breakdown", "broken down", "breaks down", "deep dive",
                     "what is", "what are", "what it means", "what you need to know", "everything you need to know", "analysis",
                     "a guide to", "guide to", "101", "the history of", "history of", "the case for", "the case against",
                     "understanding", "the truth about", "the real story", "the real reason", "the reason", "here's why",
                     "here’s why", "here is why", "why it matters", "what happened", "what really happened"]
WHY_PHRASES = ["why "]
CURIOSITY_PHRASES = ["here's why", "here’s why", "here's what", "here’s what", "here's how", "here’s how", "you won't believe",
                     "you won’t believe", "what happened next", "wait until", "wait till", "watch what", "guess what",
                     "nobody is talking", "no one is talking", "nobody talks", "they don't want you", "they don’t want you",
                     "the truth about", "the real reason", "this is why", "this changes everything", "everything changed",
                     "it's over", "it’s over", "it has begun", "this is it", "you need to see", "need to see this",
                     "this is bad", "this is insane", "this is crazy", "this is huge", "this is wild", "this is disgusting",
                     "goes wrong", "went wrong", "the untold", "what nobody", "what no one", "exposed", "secret", "shocking"]
FORWARD_REF_START = {"this", "these", "that", "he", "she", "they", "it", "his", "her", "their", "him", "them", "someone",
                     "something", "somebody", "everyone", "nobody", "the", "a"}  # 'the'/'a' only count with no entity present

REACTION_PHRASES = ["reacts to", "react to", "reaction to", "reacting to", "responds to", "response to", "responding to",
                    "reacts", "reaction", "responds", "reacting", "my reaction", "my response", "my thoughts on",
                    "watching", "live reaction"]
INTERVIEW_PHRASES = [" with ", " w/ ", " ft. ", " ft ", " feat. ", " feat ", " joins ", "interview", " interviews ", " talks to ",
                    " talks with ", " speaks to ", " speaks with ", " sits down with ", " on the ", " in conversation with ",
                    " and ", " x "]
CONFRONTATION_PHRASES = [" vs ", " vs. ", " versus ", "debate", "debates", "debating", "clash", "clashes", "showdown",
                        "confronts", "confronted", "faces off", "face off", "destroys", "owns", "dismantles", "shuts down",
                        "takes on", "takes down", "goes head to head", "head-to-head", "argues with", "fight", "fights",
                        "battle", "battles", "spars with", "grills", "schools"]
LISTICLE_RE = r"^(?:top|the)?\s*\d{1,2}\s+(?:\w+\s+)?(?:things|reasons|ways|times|signs|facts|lessons|tips|moments|questions|mistakes|rules|takeaways|lies|truths|myths|predictions|biggest|best|worst|craziest|most)"
