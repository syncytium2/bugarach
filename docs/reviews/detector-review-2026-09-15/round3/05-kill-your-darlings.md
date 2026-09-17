> **Public copy.** Lines that concern real treatment recordings are removed (22 here), per FOUNDATIONS §5, and machine paths are shortened to `<scratchpad>`, `<worktree>`, `<darkroom>` or `<home>` (sapper SAP004). Everything else is verbatim.

GRANT 5 ok — Read, Grep, Glob

# Role 5 (Kill Your Darlings): line edit, round 3, blind pass

**Artifact read:** `scratchpad/review/detector_review_plain.txt`, the text version of the built `detector_review.html`. I checked two points against `detector_review_textview.html`. All line numbers below are lines of the plain-text file. I have left out the full local path because this report goes into a public repo.

**Conventions applied:** `docs/writing_conventions.md`, `docs/GLOSSARY.md`, the role-5 banned list in `docs/doc_review_process.md` (lines 567–570, the house list as shipped, not edited), and the user's brief: no jargon, every term defined, US 6th-grade reading level, Strunk and White, American English.

## Run notes: what did not run

- **`murderboard_prose.sh` was NOT run.** My grant has no shell, so I cannot execute it. By the role's own rule this counts as a failure, not a clean result. The main thread should run it and paste its table next to this report. As a stand-in I ran the same searches with Grep; that output is pasted below. Word and sentence counts in the passage table were **counted by hand, give or take about 15%**, not measured by the tool.
- **Reading levels are my estimates, not a formula score.** No readability tool was available. Treat the grades as judgments.
- Lines 3 and 5 repeat the title. That is the page title and the H1 both landing in the text export, not a defect in the document.

### Search results (Grep in place of the tool, whole text file)

| search | result |
|---|---|
| `delve, leverage, robust, seamless, crucial, landscape, tapestry, worth noting, not just, in today's, it's not about` | **0 hits** |
| em dashes (`—`) | 11 hits, all empty table cells (lines 325–330, 408–416). **No em-dash pivots in the prose.** |
| three-item lists (checked by hand) | Lines 85, 287 and 297 each list three things that really are three. **No lists built for rhythm.** |
| `modality` / `detection` (glossary bans) | "detection" appears only inside cited paper titles (lines 458, 460). Clean. |
| passive (`is/are/was/were/be/been + -ed`) | 51 hits. Most are fine. The ones where active voice reads better are under m1. |
| hedges (`may, might, could, possibly, perhaps, about, nearly, almost, roughly, likely, somewhat`) | 53 hits. Most are the "about" in front of a rounded number, which is fine. The hedges that hide a claim are M14, M19 and m2. |

## Reading level by section (estimates)

| section | estimated US grade | what drives it |
|---|---|---|
| In short (11–21) | 10–11 | about 10 undefined terms (B1) |
| 1. The problem | 8–9 | closest to the brief |
| 2. Surrogates | 11 | line 77 (190 words), line 81 |
| 3. Hand-written detectors | 10 (3.2 and 3.6: 12) | nested asides, the word "spread" used two ways |
| 4. Learned detectors | 11 | lines 195, 203, 211 |
| 5. Simulator | **12–13** | lines 243, 245, 253 |
| 6. Grading | 12 | lines 273, 285, 289 |
| 7. Results | **13, the worst** | lines 297, 307, 311, 334; Table 3 |
| [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder] |
| 10. Conclusions | 12 | items packed with facts |
| 11. Sources | college (acceptable for citations) | — |
| Figure captions 2, 10, 14 | 13+ | 150–180 words each |

---

## BLOCKING

**B1. "In short" (lines 13–21) uses about ten terms before they are defined.** This is the first thing an outside reviewer reads, and it breaks "all terms defined."
- Undefined at first use:
  - *events* and *calls* (line 13; defined at 55 and 57)
  - [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder]
  - *locust* and *CoactDetect*, with nothing saying they are detectors
  - *frames* (line 13; defined at 109)
  - *quiet level* (line 15; defined at 245)
  - *chance lineups* (line 15)
  - *busy stretch* (line 17)
  - *mid-sized events* (line 17; defined at **418**)
  - *small events* (line 19)
  - *the setting it ships with* (line 19)
  - *bake-off* and *fitted* (line 21)
- **Fix:** define each term inline the first time it appears. Rewrites:
  - [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder]
    [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder]
  - Line 13, before: "Where many cells start events within a few frames of each other, most detectors do call"
    After: "When many cells light up within a fraction of a second of each other, most detectors make a call"
  - Line 17, before: "found 8% of mid-sized events inside a busy stretch"
    After: "found 8% of the medium-sized events (those joined by 18% of the cells) inside a busy stretch"
  - Line 19, before: "At the setting it ships with"
    After: "At its default setting"
  - [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder]
    [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder]
- Could I verify it against a source: yes (line numbers above).

**B2. The 6th-grade target is not met in Sections 5–7, and meeting it would cost content.** No line edit can get Table 3 or the paragraph on timing spread (line 253) to grade 6 without removing numbers the reviewers need. This is a decision about the brief, not about wording.
- **Fix:** the main thread should tell the user this plainly. Aim for grade 6–8 in "In short," Section 1 and the Section 10 conclusions. Aim for grade 9–10 in Sections 2–8, using the rewrites below. Say which target applies where. Do not claim "6th grade" for the whole document.
- Could I verify it against a source: no (my judgment; no formula was run).

---

## MAJOR

**M1. "level" means two different things.** It means a background rate ("quiet level," "busy level," about 40 uses) and also a threshold ("call level," lines 193–225; "a fixed level (0.1)," lines 107, 179, 352, 438; "that level is passed," line 125). Line 408 reads "Finds small events well at the quiet level," while the call level sits in the next column. The document also says "quiet background" (lines 19, 334) and "quiet level" for the same idea.
- **Fix:** use "bar" for every threshold ("call bar" for the learned detectors, "SPIKE-synch's 0.1 bar"). Use "quiet background" and "busy background" everywhere, and retitle the word-list entry to match.
- Verified: yes.

**M2. "window" means five different things.**
- the lab's marked windows (line 61 and on)
- Window A and Window B in the figures (line 89)
- the 2.5-second scoring window (line 275)
- the "nearby window" of the detectors that judge chance locally (line 243)
- SPIKE-synch's closeness window (line 177) and the counting windows in the Figure 10 caption (line 247)
- **Fix:** keep "window" for the lab's windows only. Rename the others:
  - "View A" and "View B"
  - "the 2.5-second match distance"
  - "the nearby minute"
  - "SPIKE-synch's closeness limit"
  - "back-to-back stretches"
- Verified: yes (29 hits).

**M3. "spread" means three different things.** It means standard deviation ("typical spread," lines 99, 125, 521), the shape of a set of counts ("For a smooth bell-shaped spread," line 125), and timing jitter ("timing spread," lines 189, 253, 426). Line 125 uses the first two meanings in consecutive sentences.
- Before: "For a smooth bell-shaped spread, that level is passed once in 10,000 bins by chance."
- After: "If surrogate counts formed a smooth bell curve, chance alone would pass 3.72 typical spreads in about 1 bin in 10,000."
- Also rename "timing spread" to "timing scatter" throughout.
- Verified: yes.

**M4. "mark" and "cell" collide with words the document already uses.**
- Detectors "mark" moments (lines 113, 125, 205), and the lab "marks" windows (lines 97–107, 364–382). In Table 1, "each marked window" sits next to "the bin is marked."
  - **Fix:** detectors *flag*; the lab's windows become *analysis windows*.
- "Cell" means a neuron, but line 332 says "A red cell is a detector…" (a table cell) and line 209 says "Radar detectors do the same with 'guard cells'."
  - Before (line 332): "A red cell is a detector whose worst round broke its limit"
    After: "Red marks a detector whose worst round broke its limit"
  - Before (line 209): "Radar detectors do the same with 'guard cells'."
    After: "Radar engineers use the same trick and call the blanked zone a guard band."
- Verified: yes.

**M5. "large," "mid-sized" and "small" events are used from line 17 on, but only defined in a table caption at line 418.** Line 273 introduces the 30%, 18% and 10% event sizes and never names them.
- **Fix:** at line 273, add "We call these large, mid-sized and small events." Add all three to the word list.
- Verified: yes.

**M6. Line 15 gives the wrong reason for the 0.83 cap.** The text says the cap exists "because some chance lineups look exactly like real events." Line 243 says the cause is the 6 decoys, which are built like planted events.
- Before: "The best any detector could score on these recordings is 0.83, because some chance lineups look exactly like real events."
- [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder]
- Verified: yes (lines 15 and 243).

**M7. Line 334 lists the numbers in the wrong order.** Before: "tuned binned SCE, which scored higher at the busy level (0.45 against 0.63)". The reader takes 0.45 as the busy score, but Table 3 has quiet 0.45 and busy 0.63.
- After: "tuned binned SCE, which scored higher on the busy background (0.63 against 0.45 on the quiet one)"
- The same paragraph opens "A busier background costs almost every detector," and "costs" has no object. After: "A busier background lowers almost every detector's score, most of all for small events."
- Verified: yes (Table 3, line 322).

**M8. Line 59, "How this document goes," previews the sections.** The house voice bans that. It repeats the Contents list, and it skips Sections 9 and 11. Only its first sentence carries a point.
- [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder]
- Verified: yes.

**M9. Line 163 defines when every event happens, but it sits inside the locust subsection.** Before: "All six hand-written detectors place each event at the same moment: when its brightening reached half its full rise." A reader looking for how event times are set will not look under locust.
- **Fix:** move it to line 55, after "writes down when each one happened": "Each event's time is the moment its brightening reaches half its full height."
- Verified: yes.

**M10. Line 243 packs three separate points into one 150-word block** (why the busy block exists, why decoys exist and the cap they cause, and why events are spaced out). It also contains a sentence that argues against itself. Before: "Decoys stand for lineups a careful person would not count". Two sentences later, no detector can tell a decoy from a real event, so the reader asks why a person could.
- **Fix:** make three short paragraphs. Decoy rewrite: "Decoys are lineups we leave off the answer key on purpose. They stand in for lineups that look real but are not true coordination. A detector that calls every lineup therefore loses points."
- Passage verdict: the busy-block point is buried as sentence 1 of 9.
- Verified: yes.

**M11. Line 245 has two dangling openers and a vague verb.**
- [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder]
  [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder]
- Before: "Recomputed on the 80 baselines the simulator was fitted to, a recording's average ROI rate has its 25th percentile at 5.0 mHz and its 75th at 19.0 mHz, matching the two levels."
  After: "We checked this on the 80 baselines the simulator copies. A quarter of them average below 5.0 mHz per ROI (region of interest, one cell), and a quarter average above 19.0 mHz. The two background rates sit at those two marks."
- Before: "Counting planted events and decoys too, the simulated recordings carry 6.1 and 17.2 mHz outside their busy block."
  After: "With planted events and decoys included, the simulated recordings average 6.1 mHz (quiet) and 17.2 mHz (busy) outside the busy block."
- Readers will also stop at 17.2 being lower than 19 after events were *added*. Give the reason in the same sentence.
- Verified: partly. The wording is checkable; the reason for 17.2 is not.

**M12. The timing-spread paragraph (line 253) is the hardest passage in the document.** Before: "Lineups under a circular shift, which are chance lineups, measured the same way give 0.42 seconds. And a recording built at 0.36 seconds measures back as about 0.64 seconds."
- [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder]
- Verified: yes.

**M13. Line 289 uses a double negative and an undefined term.** Before: "Those settings were not chosen on these 24 recordings, but they are not independent of the bench either. … CoactDetect's and SPIKE-synch's came from the project's viewer."
- "Viewer" is never defined, and "came from" hides who chose the settings and how.
- After: "We did not choose those settings on these 24 recordings, but some depend on the same recipe. locust's percentile was re-chosen on these two backgrounds. CoactDetect's and SPIKE-synch's were picked [by hand / by eye] in the project's viewing app."
- The author must fill the bracket; I cannot verify which is true.
- Verified: no.

**M14. Line 297 hides a name.** Before: "An earlier project run … found one detector ahead at every rate; this run does not."
- Name the detector: "found [detector] ahead at every rate." Leaving it out makes the reader guess, and it reads like a hedge.
- Verified: no.

**M15. Line 424 promises something the list does not deliver.** It says "Each item names the conclusion it threatens." Most items name a section instead; line 446 (bake-off) names nothing.
- **Fix:** either open every item with the claim it threatens (for example, "*Threatens 'five score about the same':* no statistical test…") or cut the promise.
- Verified: yes.

**M16. Line 273 misleads on first reading.** Before: "An event joined by 10% of ROIs has 3 cells, exactly the minimum three of the detectors require." It first reads as "the minimum three."
- After: "An event joined by 10% of 33 ROIs has 3 cells. CoactDetect, LoCo and binned SCE need at least 3 cells to call, so these events sit right at their limit."
- The same vague "three of the others" appears at line 161. Name the detectors there too.
- Verified: yes (Table 1 and section 3 minimums).

**M17. "Bake-off" (lines 21, 446, 569) is never defined and is not in the word list.**
- **Fix:** say "the project's official scoring run" everywhere, or define "bake-off" once and add it to the word list.
- Verified: yes.

**M18. Line 125 nests an aside inside an aside.** Before: "It asks how far the real count sits above the surrogates' average, measured in typical spreads (standard deviations: how far surrogate counts usually stray from their average)." That is 27 words.
- After: "It asks how far the real count sits above the surrogates' average. It measures that distance in typical spreads: how far surrogate counts usually stray from their average (the standard deviation)."
- Verified: yes.

**M19. Line 275 says "Read the order of the scores, not their last decimal place."** Line 297 then says "we do not rank them." Reading the order *is* ranking.
- After: "Differences in the second decimal place mean little."
- Verified: yes.

**M20. Line 195 opens with "There are two sets of copies."** "Copies" of what? A 6th grader cannot parse it.
- [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder]
- The next sentence also says "Each tube model" before tube is introduced in 4.1. Move that sentence into 4.1.
- Verified: yes.

---

## MINOR

**m1. Passive voice where active is clearer.**
- Line 59: "is estimated" → "we estimate"
- Line 193: "the busy block and the decoys are marked as 'no event'" → "we label the busy block and the decoys 'no event'"
- Line 265: "Pairs of calls and planted events are matched closest first" → "We match calls to planted events, closest pairs first"
- Line 275: "The 2.5-second window was chosen where…" → "We set the 2.5-second match distance where…"
- Line 422: "no detector is shown to be best" → "no detector proved best"
- Line 476: "When they were ported" → "When we rewrote them in Python"

**m2. Hedges that weaken a claim.**
- Line 17 says calls in busy stretches "mean little"; line 402 says they "carry no information." Pick one strength.
- Line 410: "did not reliably cut its busy-block calls" hides what happened. Say whether it cut them in some training runs and not others. (Verified: no.)
- Line 376: "(typical values; unpublished lab data)". Give the source as "(unpublished lab data)" and state the numbers.

**m3. The overlong sentences not already rewritten above.**
- Line 81 (37 words). Before: "In the minutes shown outside the block, each bar makes 3 calls: 1 on a planted event and 2 on decoys; the two planted events it misses there are small ones, joined by 3 ROIs each."
  After: "Outside the block, each bar makes 3 calls: 1 on a planted event and 2 on decoys. Both bars miss the other two planted events, which are small (3 ROIs each)."
- Line 285 (32 words). Before: "In each round, each learned detector is trained three times from different random starting numbers, on 12 of those 18 recordings: 10 to train and 2 to pick its call level."
  After: "In each round, we train each learned detector three times, each from a different random start. Each run uses 12 of the 18 recordings: 10 to learn from and 2 to set its call bar."
- [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder]
  [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder]
- Line 61. Before: "We chose this recording because, of the eight in Section 8, it is where the six detectors' counts over these minutes differ most."
  After: "Of the eight recordings in Section 8, this one shows the biggest gap between the six detectors' counts."
- Line 177. Before: "The two events are close if they are nearer than half the shortest of those four gaps, and never more than 0.25 seconds apart."
  After: "The two events count as close only if they are less than half the shortest gap apart, and also less than 0.25 seconds apart."

**m4. Line 65, "sets its bar … high among the surrogate counts," is vague.**
- After: "A detector makes many surrogates, counts lineups in each, and sets its bar near the top of those counts. A real bin must pass the bar."
- "Bin" also appears here before it is defined. Line 65, first sentence, after: "Suppose 6 cells each have an event in the same 2-second bin (a fixed slice of time)."

**m5. Line 77, "A circular shift keeps that (26)," gives a number without its unit.** After: "A circular shift keeps it at 26 per 1,000."
- "Each doubled event adds nothing" → "A second event in the same bin adds nothing to the count"
- "the two lines sit closer" gives no number. Give the two percentages, or cut the clause.

*[line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder]

**m7. Line 145 says the second event hides the first.** Both events raise the bar for each other. After: "Two real events less than a minute apart can raise each other's bar and hide each other."

**m8. Line 183, "at most 6 minus 1 of the other 32 ROIs,"** → "at most 5 of the other 32 ROIs (5 ÷ 32, about 0.16)"

**m9. Line 193, "The network then picks its call level":** the network does not pick it. After: "We then set its call bar on recordings it did not train on."

**m10. Line 201, "(to 0.3 seconds here; the width is learned)," is self-contradicting.** After: "It stretches each event into a short on-period. Training set that to 0.3 seconds for tube."

**m11. Line 203, "No filter reaches more than 12.8 seconds before or after the moment it scores, so the widest surround is nearly flat":** the "so" does not follow for a lay reader. After: "Each filter is cut off 12.8 seconds before and after the moment it scores. The widest surround is wider than that, so what remains of it is nearly a plain average."

**m12. Line 211, "It is meant to make a background twice as busy need a flash twice as bright,"** → "The idea: if the background doubles, a flash must double too before it is called. The network also sees the raw brightness, so the ratio model need not follow that idea."

**m13. Line 217 repeats "whether tube's design is what makes it work" word for word.** The last sentence, after: "Because we trained them differently, their failure proves nothing about tube's design."

**m14. Line 229, "writes out event times the way the lab's event-finding program does," is ambiguous** (same file format, or same method?). After: "makes up lists of event times in the same form the lab's event-finding program produces."

**m15. Line 285, "the looser one wins":** "looser" is not defined. → "the one with the lower bar (more calls) wins." The same applies to "loosest" at lines 305 and 307.

**m16. Line 305, "binned SCE and LoCo each chose…":** the rounds chose, not the detectors. → "The rounds chose the lowest value on the list for binned SCE and LoCo…"

**m17. Line 307, "SPIKE-synch's list does not control it … its score is not a tuned accuracy,"** → "Changing SPIKE-synch's setting barely changes what it finds, so tuning did little for its score."

**m18. Line 311, "A learned range spans 12 scores and a hand-written one 4,"** → "Each learned range covers 12 scores (4 rounds × 3 training runs); each hand-written range covers 4. More scores make a wider range, so part of this gap comes from that alone."

**m19. Line 336, "in 4 of 4 rounds,"** → "in all 4 rounds"

**m20. Line 338, "planted-style events,"** is a new term for no reason. → "planted events"

*[line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder]

**m22. Line 344, "(56% and 65%)"** → "(CoactDetect 56%, LoCo 65%)"
- Line 350: "lost part of their recall" gives no number for outside the block. Add it.

**m23. Line 356, the speed paragraph, comes right after the section's conclusion (line 354) and deflates it.** Move it before "Few calls in a busy stretch…" or into the Table 3 caption.

**m24. Lines 366–372 repeat the last column of Table 1.** Replace them with "Table 1, last column, says how each detector uses the windows."

**m25. Line 382, "locust's many calls fit its single bar,"** → "locust's many calls are what its single whole-recording bar would predict."

**m26. Line 442, "some were tuned on this recipe":** only locust's was. → "locust's was re-chosen on this recipe"

**m27. Line 476, "to within 10⁻⁹," says within 10⁻⁹ of what, and in what unit?** → "matched to within one part in a billion" (or give the unit).
- "Transliterated" and "ported" are jargon. → "copied line by line", "rewritten in Python"

**m28. "Provisional" (lines 21, 289, 442, 446) is above a 6th-grade vocabulary.** → "not final"

**m29. Undefined or late terms.**
- [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder]
- [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder]
- "tuned" (line 313) is not in the word list.
- "matching" (line 332) → "the grading rule"

**m30. The word list has gaps and one unused entry.**
- "median" (line 518) is never used in the text. Cut it.
- Missing: large/mid-sized/small events, busy stretch, bake-off, tuned, on-period, chance line, busy-block limit, KNDy.
- The entry "Neural network, training…" (line 548) defines "learned detector," not a neural network. Retitle it.

**m31. The Figure 12 caption (line 301) mentions "no diamond" without saying what a diamond marks.** The alt text says it marks the shipped value. Add "(the purple diamond marks the shipped setting)".

*[line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder]

---

## Passage test (word counts are hand estimates, ±15%)

| block (line) | words / sentences | the one sentence it delivers | payload sits | what the other words buy | verdict |
|---|---|---|---|---|---|
| [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder] |
| 17 | ~75 / 4 | Every design trades false calls for missed events in busy stretches. | start | CoactDetect 8%/97% (evidence) | keep |
| [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder] |
| 59 | ~95 / 7 | We also build simulated recordings with known answers. | start | a roadmap that repeats Contents (the author's thoroughness) | cut the rest (M8) |
| 77 | ~190 / 13 | A shuffle makes chance lineups look rarer, so its bar sits too low. | start | the 24/26/108 numbers (evidence); slow stream and four groups (partly thoroughness) | cut the slow-stream and four-group sentences to one clause |
| 81 | ~135 / 7 | A bar built from nearby time ignores busy stretches but also misses real events there. | spread over sentences 2–3 | minute-by-minute call counts outside the block (thoroughness) | cut the "In the minutes shown outside…" sentence or move it to the Figure 2 caption |
| 125 | ~160 / 10 | CoactDetect calls a bin when its cell count sits 3.72 typical spreads above nearby surrogates. | middle | the chance-rate caveat (sceptic's evidence) | keep; split sentences (M3, M18) |
| 217 | ~110 / 5 | The controls failed, and because their training differed, the failure proves nothing. | **end** | the training differences (evidence) | promote the last sentence |
| 243 | ~150 / 9 | three separate points | buried | — | split into three paragraphs (M10) |
| 285 | ~135 / 7 | Settings are chosen on 18 recordings and scored on the 6 left out. | middle | the seed and split detail for learned detectors (thoroughness for most readers) | move the learned-detector training detail to Figure 11B |
| 297 | ~120 / 7 | Five detectors score about the same; we do not rank them. | start | the busy-level list (evidence); the earlier-run comparison (a hedge, M14) | keep; name the detector |
| 334 | ~105 / 5 | A busier background costs every detector the most on small events. | start | the binned SCE exception (evidence) | fix M7 |
| [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder] |
| 386 | ~150 / 7 | Detectors agree on sharp stripes and disagree in busy stretches, where neither kind can be trusted. | sentences 1 and 3 | the recording-fault caveat (sceptic's evidence); the eight-recordings caveat (needed) | keep; cut "anyway" |

## Summary for the main thread

- **Banned constructions: none.** That is from the Grep stand-in; the prose tool itself was not run (see run notes).
- **Blocking:** B1, the undefined terms in "In short." B2, 6th grade cannot be reached in Sections 5–7, and the user should be told.
- **Most costly for a young reader:** four words that each mean several things ("level," "window," "spread," "mark"/"cell"). Fixing M1–M4 throughout will lower the reading level more than any single sentence rewrite.
- **Two checkable errors in wording:** M6 (the 0.83 cap blamed on chance lineups instead of decoys) and M7 (binned SCE's two scores given in the wrong order).
