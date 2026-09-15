> **Public copy.** Lines that concern real treatment recordings are removed (19 here), per FOUNDATIONS §5, and machine paths are shortened to `<scratchpad>`, `<worktree>`, `<darkroom>` or `<home>` (sapper SAP004). Everything else is verbatim.

GRANT 5 ok — Read, Grep, Glob

# Role 5, line editor: blind review of `detector_review` (round 2)

**Run note: the prose tool did not run.** My checklist says to run `murderboard_prose.sh` and paste its output. My grant has no Bash, so I could not. By this role's own rule, a tool that did not run is a failure, not a clean result. Please record it in the run ledger. As a stand-in I searched the plain-text copy with Grep. The word counts, sentence counts and reading levels below are hand estimates from sampled passages, not tool output.

**Banned constructions.** I used the house list from `doc_review_process.md`, role 5 (the bugarach copy). I searched `detector_review_plain.txt` for each phrase and word on it, and read by eye for rhythm-built three-item lists, em-dash turns into an uplifting close, and "In today's ___" openers.

| construction | hits |
|---|---|
| not just X, but Y · it's not about A, it's about B · it's worth noting | 0 |
| delve, leverage, robust, seamless, crucial, landscape, tapestry | 0 |
| em-dash turn into an uplifting close | 0 (the only em-dashes are empty cells in Tables 2 and 3) |
| "In today's ___" opener | 0 |
| three-item list built for rhythm | 0 (the three-part subtitle on line 7 matches three real sections; Section 3's three-part opener on line 79 matches Table 1's three columns) |

## Reading level (hand estimate, Flesch-Kincaid)

Grade 6 means about 11–12 words per sentence and about 1.4 syllables per word. The document's own words (coordination, surrogate, percentile, CoactDetect) keep the syllable count near 1.55 however short the sentences get. **Grade 6 is realistic for In short, Section 1, Section 10 and the word list. For Sections 2–8, grade 8 is the realistic floor unless the text gives up precision.**

| section | words per sentence | syllables per word | grade (est.) | what drives it |
|---|---|---|---|---|
| In short | ~13 | ~1.55 | ~8 | undefined F1, "call"; line 15 is hard to parse |
| 1 The problem | ~14 | ~1.5 | ~7–8 | close to target |
| 2 Surrogates, "Why the shift" (l.71) | ~18 | ~1.5 | ~9, and harder than that suggests | a number every ~8 words |
| 3 Hand-written detectors (3.6 worst) | ~16 (3.6: ~22) | ~1.55 | ~9 (3.6: ~11) | 36-word definition of "close" |
| 4 Learned detectors | ~17 | ~1.6 | ~10 | 36-word network definition |
| 5 Simulator | ~19 | ~1.55 | ~10–11 | "median" sentence, mHz used before it is defined |
| 6 Grading | ~16 | ~1.55 | ~9 | |
| 7 Results | ~17 | ~1.5 | ~9 | number density |
| [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder] |
| Captions (Figures 1, 2, 10) | ~20 | ~1.6 | ~11–12 | |
| 11 Where the methods come from | ~25 (prose parts) | ~1.8 | **~15** | CFAR, spike trains, port, transliteration |

**Furthest above grade 6:** Section 11, then the Figure 2 and Figure 10 captions, Section 5, Section 4, Section 8 and Section 3.6. Rewrites for each are below.

---

## Blocking

**B1. "call" is the document's main noun, but the text never defines it.**
- **Location:** first used on l.11 ("false call") and l.15 ("call over and over"). Section 1 says "marks" (l.51, 55); from l.75 on the text says "calls". The only definition is in the word list (l.416).
- **Fix:** define it at l.51.
  - Before: "That question needs a program that marks coordinated events, which we call a detector."
  - After: "That question needs a program that marks coordinated events. We call such a program a detector, and each moment it marks a call."
- **Also fix:** In short (see B2) and Figure 1 ("198 marks" → "198 calls").
- **Verify:** yes (text only).

**B2. F1 and precision appear before Section 6.1 defines them.**
- **Location:** l.11 (In short: "F1 scores from 0.71 to 0.74 out of 1"); l.225 ("a precision of at most about 0.71"). The brief says "all terms defined".
- **Fix, l.11:**
  - Before: "No detector stands out on simulated recordings. On simulated recordings with a known answer, five detectors scored about the same: CoactDetect, LoCo, tube-guard, tube and rate+context, with F1 scores from 0.71 to 0.74 out of 1 (Section 7). Even the best made about one false call for every two correct ones."
  - After: "On simulated recordings, where we know the right answer, no detector stands out. Five scored about the same: CoactDetect, LoCo, tube-guard, tube and rate+context (Sections 3 and 4). Their F1 scores ran from 0.71 to 0.74 (Section 7). F1 is a grade from 0 to 1 that is high only when a detector finds most planted events and makes few false alarms. Even the best made about one false alarm for every two correct calls (a call is a moment a detector marks)."
  - This also removes "simulated recordings" said twice in two sentences.
- **Fix, l.225:**
  - Before: "…would score a precision of at most about 0.71."
  - After: "…could have at most about 71 correct calls in every 100 (its precision, Section 6.1)."
- **Verify:** yes.

**B3. "stream" is sent to the word list, and the word list does not define it.**
- [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder]
- **Fix, l.402:**
  - Before: "The lab's program sorts events into two groups by its own rule: the fast stream and the slow stream."
  - After: "The lab's program sorts events into two groups, the fast stream and the slow stream, by [the rule in one plain sentence, for example how quickly each brightening rises and fades]."
- **Verify:** no. I do not know the rule, so the author must fill it in.

---

## Major

**M1. In short, line 15 is hard to parse, and "matters most" never says most of what.**
- [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder]
- [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder]
- **Verify:** yes.

**M2. The summary and Section 7 describe busier cells differently.**
- **Location:** l.13 says "every useful detector less sensitive". l.286 says "almost every detector worse", then lists exceptions. "Useful" is undefined, and it quietly leaves out the exceptions.
- Before: "Busier cells make every useful detector less sensitive, most of all to small events."
- After: "When cells are busier, the best detectors miss more events, most of all small ones."
- **Verify:** no. Recall on busy backgrounds is not given in the text for every detector.

**M3. "Two exceptions" names three detectors.**
- **Location:** l.286.
- Before: "Two exceptions: tuned binned SCE rose (0.45 to 0.63), as did, slightly, the two failed controls."
- After: "Three detectors scored higher on the busy background: tuned binned SCE (0.45 to 0.63) and, by a little, the two failed controls."
- **Verify:** yes.

**M4. The same mistake has two names: "false call" and "false alarm".**
- **Location:** l.11 and l.282 say "false call". Everywhere else, including the word list, says "false alarm".
- l.282 before: "roughly one false call for every two correct ones"
- l.282 after: "roughly one false alarm for every two hits"
- **Verify:** yes.

**M5. "spread" carries five meanings.**
- **Where it is used:**
  - statistical deviation: Table 1 ("3.72 typical spreads")
  - how far planted cells' start times scatter: l.173, 221, 225 ("timing spread")
  - filter width: l.191 ("center filters spread about 0.19 to 0.63 seconds")
  - the range of results: l.253, 298 ("spread between runs", "spread more widely")
  - how rates vary across ROIs: Figure 10C ("the spread of rates")
- **Fix:** keep "spread" only for the scatter of start times.
  - Table 1 and 3.2: define the statistical meaning once as "standard deviation (how far surrogate counts usually stray from their average)" and use that phrase in both places.
  - l.191:
    - Before: "the center filters spread about 0.19 to 0.63 seconds and the surround filters about 2.6 to 16.3 seconds, cut off at 12.8 seconds either side."
    - After: "the center filters are about 0.19 to 0.63 seconds wide and the surround filters about 2.6 to 16.3 seconds wide. No filter reaches more than 12.8 seconds before or after the moment it scores."
    - This also clears up a filter "16.3 seconds" wide that is "cut off at 12.8".
  - l.253: "the spread between runs mixes the two" → "the differences between runs come partly from the random start and partly from the training recordings."
  - l.298: "spread more widely" → "vary more".
  - Figure 10C: "the spread of rates across ROIs" → "how rates vary across ROIs".
- **Verify:** yes for wording. Filter reach: no.

**M6. Section 3.6 and Section 11 disagree about SPIKE-synch's calling rule.**
- **Location:** l.171 describes one level: start above 0.1, continue above 0.1. l.388 calls the rule "an ordinary two-level threshold".
- **Fix:** if there is one level, l.388 becomes: "The rule that turns scores into calls is our own: a call starts when the average passes 0.1 and ends when it falls back below." If there are two levels, 3.6 must give the second one.
- **Verify:** no.

**M7. The worst long sentence (3.6, l.171) is 36 words.**
- Before: "For each pair of events in two ROIs, "close" means nearer than half of the shortest of four gaps: the gaps before and after each of the two events, to the next event in the same ROI."
- After: "To decide whether two events in different ROIs are close, it looks at four gaps. For each event, it measures the time back to the previous event in the same ROI and forward to the next one. The two events are close if they are nearer than half the shortest of those four gaps."
- **Also, l.171:**
  - Before: "It continues while later bins stay above 0.1, skipping empty stretches shorter than 0.5 seconds, and it must include at least 3 events."
  - After: "It continues while later bins stay above 0.1. A gap shorter than 0.5 seconds does not end it. A call must include at least 3 events."
  - "Skipping empty stretches" is ambiguous: empty bins, or bins below 0.1? Verify: no.

**M8. Section 4, l.183: the network definition is 36 words, and "on 2 other" attaches to the wrong verb.**
- Before: "A learned detector is a small neural network: a chain of simple arithmetic steps whose numbers the computer adjusts, over many examples, until its output is high inside planted events and low elsewhere. That adjusting is training. Each network here saw 10 simulated recordings during training. It then chose the output level at which it makes a call (its call level) on 2 other simulated recordings."
- [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder]
- **Why:** as written, "each network here saw 10" contradicts "the same 18 recordings" on l.253.
- **Verify:** no. Which copy used which recordings needs checking.

**M9. Section 5, l.221: a 32-word aside about uncertainty sits in the middle of the simulator recipe.**
- [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder]
- After, in the recipe: "Each cell's start is moved by a random amount, typically 0.36 seconds."
- [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder]
- **Verify:** yes.

**M10. Terms used before they are defined: mHz, percentile, "four groups of mice".**
- **mHz:** "60 mHz" on l.223; defined on l.227.
  - l.223 before: "every ROI gets an extra 60 mHz of random events"
  - l.223 after: "every ROI gets an extra 60 mHz of random events (millihertz; 60 mHz is about one event every 17 seconds)"
  - Then shorten l.227's gloss to "(mHz: see above)".
- **Percentile:** first used in the Figure 2 caption (l.69); defined only in the word list.
  - l.69 before: "(the 99.9th percentile, 4 ROIs)"
  - l.69 after: "(the 99.9th percentile: a count higher than 999 in every 1,000 surrogate counts; here 4 ROIs)"
- **Four groups of mice:** l.71 and l.73; defined on l.306.
  - l.71 before: "in each of the four groups of mice"
  - l.71 after: "in each of the four groups of mice (Section 8)"
- **Verify:** yes (60 mHz → 16.7 seconds is arithmetic).

**M11. "Why the shift", l.71: the main point is sentence 7 of 10, and the decimals are more precise than the argument needs.**
- Before: "Real cells seldom have two events within a couple of seconds of each other. In the fast stream, an event lands in a 2-second bin its own cell already filled 24.5 times per 1,000 events. A circular shift keeps that (25.6 times). A shuffle scatters events at random, so it doubles them up 107.9 times per 1,000. Each doubled event is an event that adds nothing to any count, so a shuffle makes lineups look rarer than they are for these cells. In Figure 2B, the shuffle says 6 or more ROIs line up in 0.35% of fast-stream bins; the shift says 0.58%. A bar set from shuffles would sit too low and would fire more often by chance."
- After: "A bar built from shuffles sits too low, so it is passed by chance more often. Real cells seldom have two events within 2 seconds. In the fast stream, about 25 of every 1,000 events land in a 2-second bin where the same cell already has an event. A circular shift keeps that number (about 26). A shuffle scatters events at random and raises it to about 108. A second event in the same bin adds nothing, because each cell counts once. So a shuffle makes lineups look rarer than they are. In Figure 2B, the shuffle says 6 or more ROIs line up in 0.35% of fast-stream bins; the shift says 0.58%."
- **Verify:** yes.

**M12. Section 8, l.308 is an 11-sentence paragraph that should be a list, and its opening sentence says nothing.**
- Before: "The windows the lab marks for analysis shape the runs differently. rate+context, CoactDetect, SPIKE-synch and the learned detectors run separately inside each window. binned SCE also runs inside each window, with one bar per window. LoCo scans the whole recording, taking its surrogates within each recorded period. locust scans the whole recording with one bar for all of it."
- After: "Detectors differ in how much of each recording they look at:
  - rate+context, CoactDetect, SPIKE-synch and the learned detectors: each analysis window separately.
  - binned SCE: each analysis window, with one bar per window.
  - [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder]
  - locust: the whole recording, with one bar for all of it."
- **Verify:** no. What "recorded period" means is my guess.

**M13. Section 8, l.306: a 32-word sentence, and "fire" for cells.**
- [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder]
- [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder]
- **Verify:** yes.

**M14. Section 11 reads at about grade 15 and leaves an abbreviation undefined.**
- **CFAR** (l.382) is never expanded.
  - Before: "radar's greatest-of rule"
  - After: "radar's greatest-of rule (radar papers call this family of detectors CFAR, for constant false-alarm rate)"
- **Other rewrites:**
  - l.380: "Shifting whole spike trains as surrogates:" → "Shifting each cell's whole row of events to make surrogates:"
  - l.384: "which reshuffled intervals and took a per-surrogate maximum" → "which shuffled the gaps between each cell's events and set the bar from the highest count in each surrogate"
  - l.386: "It is a partial, modified port." → "Our locust copies part of CICADA's code, with changes."
  - l.392: "matched its MATLAB predecessor to within 10⁻⁹ on test data" → "gave the same outputs as its MATLAB version, to within one billionth [of what: add the unit], on test data"
  - l.378: "Part II adds a moving window." Move it after the Part II citation: "…and II. Nonstationary data. 14(1):81–119, doi:…, which adds a moving window."
- **Verify:** no for the CFAR family claim and the unit.

**M15. The simulator is called "the lab's pipeline" once, and "the lab's program" everywhere else.**
- **Location:** l.217 says "the way the lab's pipeline does". l.49, l.308 and the word list say "program".
- After: "the way the lab's event-finding program does".
- **Verify:** yes.

---

## Minor

1. **Passive voice where the actor is known.**
   - l.107: "Calls less than 3 seconds apart are joined into one." → "It joins calls less than 3 seconds apart into one."
   - l.225: "Decoys are placed at random" → "The simulator places decoys at random"
   - l.227: "They were meant as the 25th and 75th percentiles" → "The project meant them to match the 25th and 75th percentiles"
   - l.249: "Each limit was set a little above" → "We set each limit a little above"
   - l.255: "That rule was not used here" → "We did not use that rule here"
2. **l.109, Figure 3:** "2 calls start in this window, all false alarms" → "2 calls start in this window, both false alarms".
3. **l.288:** "over its limit of 2 in 4 of 4 rounds" → "over its limit of 2 in all 4 rounds".
4. **l.225:** "6 times, 18% of ROIs have events together" → "Six times, 6 ROIs (18%) have events together". Strunk and White: do not start a sentence with a numeral.
5. [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder]
6. **l.119 and l.127:** the 1-in-10,000 warning appears in the text and again in the risks box. Cut the text version: "Real surrogate counts are lumpy and rarely bell-shaped, so the true chance rate is higher than that; the number sets the bar but is not a false-alarm rate." → "Real surrogate counts are rarely bell-shaped, so the true chance rate is higher."
7. **Figure 4 (l.121):** "so the count is one more than the planted ROIs" → "so the count is 7: the 6 planted ROIs plus one".
8. **Figure 8 (l.173):**
   - "each event can be close to at most 6 minus 1 of the other 32 ROIs, a score of about 0.16" → "each event can be close to at most the 5 other planted ROIs out of 32: a score of 5/32, about 0.16".
   - "With the planted spread, most scores are lower" → "Because planted cells do not start at exactly the same time, most scores are lower".
9. **l.294:** "because no score between 0 and about 0.03 is possible with 33 ROIs" → "because with 33 ROIs the smallest score above 0 is 1 of 32 other ROIs, about 0.03". Also: "so its score here is not a tuned accuracy" → "so tuning did not really change it".
10. **l.131, LoCo:** "It takes the minute before and the minute after" → "It takes the minute before and the minute after that moment". Table 1 says "checkpoint" and the text never does; use one word.
11. **l.107, rate+context:** "for more than one time step". The length of a step is not given. Verify: no.
12. **l.155, locust:** "It calls the peaks of the count that reach the bar" → "It makes a call at each peak that reaches the bar". Also l.157: "the other five" → "the other five hand-written detectors".
13. **l.167:** "The on-period length is a fixed setting, and changes its results." → "The 1-second on-period is fixed by hand, and a different length gives different results."
14. **l.164 and l.334:** "Close to openly released software from another lab" → "Close to free, public software from another lab".
15. **l.159:** "some of its settings differ". GLOSSARY retires bare "settings". Name which ones. Verify: no.
16. **l.199:** "divides the center by the surround instead of subtracting". The text never says tube subtracts. On l.191: "It compares the brightness right now" → "It subtracts the surrounding brightness from the brightness right now".
17. **l.201:** "Its fitted surround puts most of its weight just outside the blanked part" → "Its learned surround filter counts the moments just outside the blanked part most heavily".
18. [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder]
19. **l.221:** "binned SCE and locust use the whole recording, so theirs always does." → "binned SCE and locust judge chance from the whole recording, so their window always holds all 15."
20. **l.231:** "the lab removed events near known ones" → "the lab removed events near known recording faults".
21. **l.255:** "a stricter rule that refuses a setting at the end of the list, a list where every value scores the same, or a setting that breaks the busy-block limit" → "a stricter rule. It refuses a setting at either end of the list, a setting from a list where every value scores the same, and a setting that breaks the busy-block limit."
22. **Figure 11 (l.257):** "Section 7 reads this figure." → "Section 7 discusses this figure." The diamond is never explained: add "a diamond marks the shipped setting". Verify: no.
23. **Table 2 caption (l.280):** "which one-to-one matching scores as one or two hits" → "and because each call can claim only one planted event, that scores as one or two hits".
24. **Table 2:** three different markers for "nothing here": "none set", "n/a" and "—". Use one, and say what it means in the caption.
25. [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder]
26. **l.320:**
    - Before: "where detectors with one bar for the whole recording, and SPIKE-synch, call far more often than those whose bar follows the nearby background."
    - After: "There, SPIKE-synch and the detectors with one bar for the whole recording call far more often than the detectors whose bar follows the nearby background."
27. [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder]
28. **l.360:** "The five that score alike may or may not." asserts nothing. → "So we cannot say whether the five that score alike are truly equal."
29. [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder]
30. **Footer (l.440):** "uncommitted changes of the project's own tools" → "uncommitted changes to the project's tools"; "bake-off tool" → "comparison tool".
31. **Word list:** it has no entries for raster, lineup, coordinated event, median, log scale, lane or seed, all of which appear in the text. It also has no entry for "call" beyond what B1 adds.
32. [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder]

---

## Passage test: the one sentence each long block exists to deliver

| block | point of the block | where it sits | what the other words buy | fix |
|---|---|---|---|---|
| In short ¶1 (l.11) | Five detectors tie, and we did not test the difference | first | proof (the range) | B2 rewrite |
| Section 2 "Why the shift" (l.71) | A bar built from shuffles sits too low | sentence 7 of 10 | evidence a skeptic needs (the rates for each stream and group) | move the point to the front (M11) |
| [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder] |
| 3.2 (l.119) | It calls at 3.72 standard deviations above the local surrogates | sentence 5 of 7 | the two bell-curve sentences repeat the risks box | cut one copy (Minor 6) |
| Section 4 intro (l.183) | A network trained on simulations decides when to call | spread across the block | a definition a reader needs | M8 |
| Section 5 planted events (l.221) | Planted cells start about 0.36 seconds apart | first, then buried by a 32-word aside | caveat, placed in the wrong block | move it (M9) |
| Section 5 recipe (l.227) | The quiet level is busier than intended | last | recipe details a skeptic needs | keep; already repeated in Section 10 |
| 6.3 ¶2 (l.255) | Section 7 includes settings the stricter rule would refuse | sentence 3 of 5 | needed context | keep |
| [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder] |
| Section 8 (l.308) | All detectors ran as the lab runs them, and only calls inside the windows count | split between the first and the eighth sentence | a per-detector list hidden in prose | make it a list (M12) |
| [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder] |

**What I checked:** every line of `detector_review_plain.txt` (the plain-text copy of the built HTML), plus the `10⁻⁹` superscript in `detector_review_textview.html`, against `docs/writing_conventions.md` and `docs/GLOSSARY.md` in the worktree. I did not open the figures: rendered checks belong to role 10, and the truth of the claims belongs to role 4.

**Files:**
- `<scratchpad>\review\detector_review_plain.txt`
- `<scratchpad>\review\detector_review_textview.html`
- `<worktree>\docs\writing_conventions.md`
- `<worktree>\docs\GLOSSARY.md`
