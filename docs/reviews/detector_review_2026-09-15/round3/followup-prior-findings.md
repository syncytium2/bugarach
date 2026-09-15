> **Public copy.** Lines that concern real treatment recordings are removed (39 here), per FOUNDATIONS §5, and machine paths are shortened to `<scratchpad>`, `<worktree>`, `<darkroom>` or `<home>` (sapper SAP004). Everything else is verbatim.

# Round 3 follow-up: rulings on all blocking and major findings from rounds 1 and 2

I checked everything against the current build: the HTML (sha 5495e51e…), the plain-text copy, all 18 figure images, `numbers.json` and the generator at commit 699de8e. Nothing was written or edited. Round-1 findings marked high or medium count as major.

Rulings: F = FIXED, P = PARTLY FIXED, N = NOT FIXED, S = SUPERSEDED, D = DECLINED-ACCEPTABLE.

## Round 1

| Role | Finding | Ruling | Evidence in the current build |
|---|---|---|---|
| 1 | #1 The Figure 2C "three calls are planted" caption | F | §2: "3 calls: 1 on a planted event and 2 on decoys; the two planted events it misses there are small ones" |
| 1 | #2 Learned detectors "trained on 18" | F | §4: "trained on 10 … picked their call level on 2 more"; §6.3: "12 of those 18" |
| 1 | #3 locust event length and peak anchor | F | "switches its ROI on for 1 second"; "All six … place each event … when its brightening reached half its full rise" |
| 1 | #4 The 25th percentile does not reproduce | F | "Recomputed on the 80 baselines … 25th percentile at 5.0 mHz and its 75th at 19.0" |
| 1 | #5 Which detectors use which windows (LoCo, binned SCE, locust) | F | §8 bullet list: each marked window / one bar per window / surrogates within each period / one bar for all of it |
| [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder] |
| 1 | #7 Decoys placed "outside" planted events | F | §5: "Decoys follow no spacing rule and can sit close to a planted event" |
| 1 | #8 120-second spacing said to cover every detector | F | Now limited to "the nearby window of CoactDetect, LoCo and rate+context" |
| 1 | #9 "Each was trained once" | F | Replaced by "There are two sets of copies…" |
| 1 | #10 "The fastest detectors once trained" | F | Now "thousands of times faster than real time" |
| 1 | #11 locust per-round limit breaks hidden; flaw list incomplete | F | Table 3 marks the worst round in red; "locust broke its limit in 2 of 4 rounds"; flaw list names rate+context, locust and SPIKE-synch |
| 1 | #12 "Over minutes and over seconds" | F | Table 2: "5-minute and 1-minute stretches" |
| 1 | #13 "Steady intervals"; busiest recording not disclosed | F | Mechanism is now same-bin doubling (Figure 2C); caption: "We chose the baseline with the most events" |
| 1 | #14 "Every detector" / "one exception" | F | "almost every detector … The exceptions are tuned binned SCE … and … the two failed controls" |
| 1 | #15 Footer provenance | P | Footer now separates the rounds run. A few values are still typed into the template (the 0.42 s null, 0.64 s round trip), against "filled in from the same measurements" |
| 2 | #1 Amarasingham credited for shifting | F | Shifting is credited to Pipa, Bocchio and Dard; Amarasingham is cited for judging chance locally |
| [line removed from the public copy: it quotes page text beside a private-correspondence citation (check_quotes)] |
| 2 | #3 binned SCE lineage | F | "pooled-percentile bar like … Bocchio … Dard … goes back to Mao … Cossart 2003 … highest count in each surrogate" |
| 2 | #4 "All six first written in MATLAB in the same lab" | F | "Five … by this project's author; locust's MATLAB version transliterated CICADA's code" |
| 2 | #5 CICADA called "published, widely used" | F | "Close to openly released software from another lab" |
| 2 | #6 No prior art for the learned detectors | F | DOSED, cnn-ripple and Mölter cited; "first written in MATLAB" |
| 3 | 1 Trained once vs three times | F | Two sets of copies explained in §4 |
| 3 | 2 "Fastest" | F | As role 1, #10 |
| 3 | 3 Only rate+context named as breaking its limit | F | "let rate+context, locust and SPIKE-synch pick settings that break their limits" |
| 3 | 4 SPIKE-synch "few false alarms" strength | F | Strength now "Needs no surrogates. Its gap-based window…" |
| [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder] |
| 3 | 6 120-second spacing claim | F | As role 1, #8 |
| 3 | 7 18 vs 16 + 2 recordings | F | §6.3: 10 + 2 |
| 3 | 8 "The bench" used for two different recordings | F | "The simulator's recipe, which we call the bench"; test-recording paragraph in §3 |
| 3 | 9 "Fitted closer to real than flat" (Figure 10) | S | That claim is gone; the text now gives bunching split by cell rate |
| 3 | 10 A limit rule stated but never enforced | F | §6.3: "We did not use that rule here" |
| 3 | 11 MATLAB "same lab" | F | As role 2, #4 |
| 3 | 12 Symbol K in Figure 2B | F | Axis now uses "n" |
| 3 | 13 Reserved term "analysis window" | F | Not found anywhere; now "marked windows" |
| 3 | 14 Bare "settings" | D | Still used, but defined in the word list ("Setting, shipped setting") |
| 3 | 15 Table columns don't say which background | F | Table 3: "…busy block, quiet level"; "speed, quiet level" |
| 3 | 16 Busy-block rates at mixed precision | F | Two decimals in Table 3; Figure 13B floor labelled "fewer than 0.01 per minute" |
| 3 | 17 trace's rise missed; tube-guard 0.64 missed | F | Controls named as exceptions; "tube 0.64, tube-guard 0.64" |
| 3 | 18 End-of-list caveat missing for binned SCE | F | Table 4: "its best setting may lie past the end of the list" |
| 3 | 19 Figure 9 trace/tiny lanes empty | S | trace and tiny are no longer in Figure 9's lanes |
| [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder] |
| 3 | 21 Code names on Figure 11C axes | F | Figure 12 axes: "bar: events per second above the average", etc. |
| 3 | 22 New terms missing from `docs/GLOSSARY.md` | N | No decoy or busy block in GLOSSARY (a repo-side fix) |
| 4 | 1 Figure 2C caption false | F | As role 1, #1 |
| 4 | 2 Controls are an uncontrolled comparison | F | "Because their training differed, their failure does not show that tube's design is what makes it work" |
| 4 | 3 A detector that calls everything can't be flagged | F | Table 3 footnote ¹; trace and tiny left out of Figure 13B |
| 4 | 4 Table scores tuned, not shipped, settings | F | Shipped-setting columns in Tables 3 and 4 |
| 4 | 5 Decoy ceiling and scoring rule unexplained | F | F1 ceiling 0.83 stated; decoy purpose stated; decoys can sit close to planted events |
| 4 | 6 Training description wrong three ways | F | 10 + 2 split; seed confound disclosed; "trained once" gone |
| 4 | 7 SPIKE-synch score reported as an accuracy | F | "its score is not a tuned accuracy"; its precision explained |
| 4 | 8 "Fastest" | F | Fixed |
| 4 | 9 SPIKE-synch "few false alarms" | F | Fixed |
| 4 | 10 Limits certify each detector's own past; project's guards bypassed | F | §6.2: "flags a detector that has drifted … does not compare detectors"; §6.3 names the stricter rule and that it was not used |
| 4 | 11 Wrong variance behind "we do not rank" | D | "We did not run a statistical test, so we do not rank them"; also listed in §10 |
| 4 | 12 "Best detectors find most…" overreach | F | Sentence removed |
| 4 | 13 0.36 s spread is chance-level | F | "Its timing spread is not well measured … 0.42 … 0.64 … ⚠" |
| 4 | 14 Figure 2B "more than chance" | F | "more than a shift explains … slow changes … a shift … also breaks" |
| 4 | 15 Figure 2A extreme pick; bench can't test shift vs shuffle | P | Selection disclosed. The untestability on the bench is not stated |
| [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder] |
| [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder] |
| [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder] |
| [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder] |
| 4 | 20 "Obvious stripe" agreement is weak evidence | D | "could also come from a recording fault … We did not measure how often the detectors agree…" |
| 4 | 21 Two weaknesses never measured | P | LoCo: "not measured here"; §10 notes the crowded recording was not run. CoactDetect's "raises its own bar a little" is still not labelled unmeasured |
| 5 | H1 Trained once | F | Fixed |
| 5 | H2 Fastest | F | Fixed |
| 5 | H3 "May not exceed its limit" | F | Fixed |
| 5 | H4 "Three variations each change one thing" | F | "tube-ratio-guard makes both changes" |
| 5 | H5 "Every detector less sensitive" | F | "almost every" |
| [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder] |
| 5 | M1 "fire" | F | Not found anywhere |
| 5 | M2 "analysis window" undefined | F | Word list: "Marked windows are the stretches…" |
| 5 | M3 Stream undefined | F | "brief brightenings and much longer ones" |
| 5 | M4 KNDy not spelled out | F | "kisspeptin, neurokinin B and dynorphin" |
| 5 | M5 "Receptor" | F | "a sensor these cells carry" |
| 5 | M6 "Filter" undefined | F | "weighted averages over nearby moments" |
| 5 | M7 "Half-gap" | F | Four-gap sentence rewritten |
| 5 | M8 "Stops the bar from dropping" | F | "raises it as soon as a busy stretch begins" |
| 5 | M9 Shuffle "destroys bursts" contradiction | F | Rewritten |
| 5 | M10 §12 jargon | F | Radar averaging detector glossed; CFAR defined; "shuffled the gaps" |
| 5 | M11 Shuffle/shift order unclear | F | "the shuffle says … 0.35%; the shift says 0.58%" |
| 5 | M12 trace/tiny "almost nothing or everything" | F | "one call that covered all of it … 3 calls … 97%" |
| 5 | M13 Bench singular vs 24 recordings | F | "We made 24 bench recordings" |
| 5 | M14 Limit given without a reason | F | "Because busy-block calls are left out of precision, F1 cannot see them. So…" |
| 5 | M15 Numbers without units | F | "0.17 calls per minute"; "4 frames (0.4 seconds)" |
| 5 | M16 Four names for the call level | P | "call level" is consistent, but §4.1 tube-guard still says "raises its own bar less" |
| 5 | M17 "Not a confidence interval" | F | Now "it is not a statistical test" |
| 5 | M18 19 bins vs 18 | F | Lane reads 18 calls |
| 5 | M19 "More than" vs "about as much as" | S | Comparison removed |
| [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder] |
| 6 | 1 Benchmark doesn't test shipped settings | F | Shipped columns; SPIKE-synch at 0.1 is now measured |
| 6 | 2 Bell-curve p-value stated as a frequency | F | "true chance rate may differ; we have not measured it" |
| 6 | 3 "Steady intervals" mechanism | F | Same-bin doubling, Figure 2C |
| 6 | 4 locust duration from data file | F | Fixed 1 s |
| 6 | 5 Windows description | F | §8 list |
| 6 | 6 tiny scoring artifacts | F | Footnote ¹ |
| 6 | 7 SPIKE-synch pick is a tie | F | "identical results … by the tie rule" |
| 7 | 1 Speed uses median, not mean | F | Generator reads `row.detect_x_realtime`; slowest is now tube-ratio-guard |
| 7 | 2 Bunching not the project's definition | F | `count_dispersion.burst_rows`/`fano` |
| 7 | 3 Baseline-window rule copied | F | `recordings_from_slices` and `baseline_trains`; no `isfinite(analysis_start)` copies |
| 8 | 1 Figure 11C code identifiers | F | Figure 12 plain-language labels |
| 8 | 2 Figure 11C ticks, legend, ✕ reuse, missing shipped value | F | Legend added; markers without lines; limit break is now a red square; caption explains SPIKE-synch's missing diamond |
| 8 | 3 SPIKE-synch mechanism not drawn; "synchrony" labels | P | Labels now "event scores" / "frame score". No schematic |
| 8 | 4 Filter undefined; Figure 9A unreadable | F | Filters defined; 9A scaled to each peak, surrounds visible |
| 8 | 5 Underscore names | F | Hyphenated everywhere |
| [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder] |
| [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder] |
| [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder] |
| 8 | 9 Figure 10C/D units | F | "mHz, log scale"; "variance ÷ average count"; minute ticks |
| [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder] |
| 8 | 11 Trained once | F | Fixed |
| 8 | 12 "18 (Section 6)" pointer | F | Fixed |
| 8 | 13 Figure 2C colour code reversed | P | Count is now blue, but the nearby bar is still coloured (purple); blue means "shift" in 2B/2C and "count" in 2D |
| 8 | 14 Stream | F | Fixed |
| 8 | 15 CoactDetect units; bar of 2.3 ROIs; count of 7 for 6 cells | P | "typical spreads (standard deviations)"; "6 planted ROIs plus one". A bar between whole numbers is still unexplained |
| 8 | 16 Windows in seconds vs minute axes | F | "6 min 40 s to 9 min 40 s" |
| 8 | 17 Tables unnumbered; SCE and frame undefined | F | Tables 1–4 numbered; Table 1 caption defines both |
| [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder] |
| 9 | 1 Time-scale ladder figure | N | Still Table 1 only |
| 9 | 2 Layout paragraph instead of a key | F | In-figure keys; "Keys above each figure name the marks" |
| 9 | 3 Figure 8 axes, 0.16 line, schematic | P | Axes stop at 0.3. No 0.16 line; the arithmetic is still in the caption |
| 9 | 4 Counts in lane labels; CICADA provenance paragraph | P | Counts in lanes. Provenance paragraph still in §3.5 |
| 9 | 5 Figure 2 caption 290 words | P | n = 6 guide and a bar-chart panel added; caption still 247 words |
| 9 | 6 Pipeline diagram and design grid for §4 | P | Counts in Figure 9 lanes; no diagram or grid |
| 9 | 7 Simulator as a table; rate histogram; Figure 10B zoom | P | Table 2 added. No histogram; 10B still 8 s with no spread marked; caption 190 words |
| 9 | 8 Figure 11 reflow and extended 11A | P | Old 11C moved to §7 (now Figure 12). 11A still lacks the decoy and busy-block cases |
| [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder] |
| [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder] |
| 9 | 11 §10 table as a report card | N | Table 4 is still prose |
| 9 | 12 Glossary placement | F | Moved to §12 at the end |
| 9 | 15 Figures unreadable at 400 px | F | Images are links; "Tap or click any figure…" at the top |
| 10 | 1 Page head | F | DOCTYPE, lang, charset and viewport present |
| 10 | 2 Figure 12B label clipped | F | Figure 13B label is whole |
| 10 | 3 Figure 2B labels clipped | F | Whole |
| 10 | 4 Legend hides a data point | F | Legend is outside the plot |
| 10 | 5 "One line per detector" caption | F | Fixed |
| 10 | 6 Figures 3–9 keys only in prose | F | Glyph and line keys in each figure |
| [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder] |
| 10 | 8 Figure 9A y-ranges differ | F | All normalized to ±1 |
| 10 | 9 One green ▼ for six detectors | F | "found by any of the four" |
| 10 | 10 Figure 2C ▼ used for calls; colours change meaning | P | Calls are now ticks. Blue still means shift in 2B/2C and count in 2D |
| 10 | 11 Figure 11C axes, markers, text size | F | Figure 12 |
| [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder] |
| 11 | 2 Cost missing from the front | F | §1: "This matters for the lab's question…" |
| 11 | 3 "In short" states setup, not findings | F | Rewritten as findings |
| 11 | 4 Verdicts before evidence, contradicting it | F | Boxes are "What the design…"; Table 4 is "what Sections 7 and 8 measured" |
| 11 | 5 Glossary position | F | End of document |
| 11 | 6 Test recording used before it is described | F | "The test recording in Figures 3 to 9" paragraph |
| 11 | 12 Residual risk scattered | F | §10 "What could be wrong with the conclusions above" |
| [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder] |

**Round 1 totals (150 findings):** FIXED 125 · PARTLY 16 · NOT FIXED 3 · SUPERSEDED 3 · DECLINED-ACCEPTABLE 3

## Round 2

| Role | Finding | Ruling | Evidence in the current build |
|---|---|---|---|
| [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder] |
| [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder] |
| 1 | M2 "Every useful detector" | F | Gone; "In short" now uses shipped CoactDetect 52% → 24% |
| [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder] |
| [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder] |
| 1 | M5 Bunching contradicts `bench.py` | P | "Almost twice" replaced by a split by cell rate. The conflict with `bench.py` `MEASURED_BURST_SHAPE` ("fine scales reproduced") is neither mentioned nor reconciled |
| 2 | B1 CICADA v1.0.3 lacks the SCE code | F | Concept DOI 10041433; "not in the Zenodo version 1.0.3 … main branch as read in August 2026" |
| 2 | B2 PySpike cap credited wrongly | F | "applied in our own code; PySpike has an option … no effect since its version 0.8.0" |
| 2 | M1 Stella 2022 not cited | F | Cited in §2 and §11 |
| 2 | M2 Local-surrogate literature missing | F | Harrison & Geman 2009 and Amarasingham 2012 cited |
| 2 | M3 Greatest-of origin | F | Hansen 1973 cited "(not read)" |
| 3 | B1 Held bake-off published | P | "These results are provisional … not yet released"; §10 repeats it. How this run relates to the held 24-seed run (including its different locust rate) is not explained, and no release is recorded in MILESTONES |
| 3 | B2 locust held out of the public build | N | Still an open decision for Tony. MILESTONES has not changed; its row already reads "in both viewers", which may settle the scope |
| 3 | M1 "One bar for the whole recording" class | F | §8: "locust, SPIKE-synch and sometimes rate+context call far more often…" |
| 3 | M2 SPIKE-synch zero from Figure 8 | F | Fixed |
| 3 | M3 "Every useful"; "in a quiet recording" | F | "on a quiet background … on a busy one" |
| 3 | M4 10 + 2 vs 18 | F | §4 and §6.3 agree |
| 3 | M5 Figure 2C counts cover minutes 15–30 only | F | Figure 2D caption "minutes 15–30"; prose "In the minutes shown" |
| 3 | M6 Underscore lane names | F | Fixed |
| [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder] |
| [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder] |
| 3 | M9 "Analysis window" | F | Not found anywhere |
| 3 | M10 "Silent" | F | Not found; legend "36% of ROIs with no event" |
| 3 | M11 Percentile basis | F | 80 fitter baselines match 5.0 / 19.0 mHz; ⚠ removed |
| 3 | M12 Figure 12C heading | F | "C1 at the quiet level, C2 at the busy level" |
| 3 | M13 GLOSSARY says locust gets producer durations | N | GLOSSARY still says `width_sec` from the producer; the page says a fixed 1 s |
| 3 | M14 "No detector stands out" vs MILESTONES "one winner" | F | "An earlier project run … found one detector ahead … this run does not. We have not worked out why" |
| [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder] |
| 4 | B2 Precision headline mostly measures decoys | F | Best F1 possible 0.83 (line in Figure 13A); precision with decoy calls set aside (Table 3); SPIKE-synch precision explained |
| 4 | M1 2.5 s window unexplained | F | "chosen where LoCo's and CoactDetect's F1 scores stop rising … generous … Read the order" |
| 4 | M2 Spacing built around local detectors | D | "avoids a known weakness … rather than testing it"; §10: crowded recording "not run here" |
| 4 | M3 Simulator lineups not validated | P | Bench curve added to Figure 2B1; 0.42 and 0.64 s disclosed; realized rates 6.1 and 17.2 mHz. Event sizes coming from detector-found clusters is still undisclosed |
| 4 | M4 No statistical test | D | "We did not run a statistical test … also untested"; "12 scores and … 4" |
| [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder] |
| 4 | M6 SPIKE-synch cap and level are this project's choices | F | "this project's choices, not the measure's authors'"; the hard limit is stated |
| 4 | M7 binned SCE anomaly | P | "One possible reason … not tested". §6.2 "F1 cannot see them" is still unqualified, and the misses at 30% of ROIs are unexplained |
| 4 | M8 Shipped settings provisional | F | "not independent of the bench … They are provisional"; slow stream in §10 |
| [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder] |
| [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder] |
| 4 | M11 Summary overreach | P | Five-way tie now "at the quiet level"; "every useful" gone. The "few false calls" wording remains (role 1, M1) |
| 4 | M12 §10 incomplete | P | Most items added. Missing: the busy block inside whole-recording surrogates, and recording faults |
| 5 | B1 "Call" undefined | P | Defined in §1, but "In short" uses "calls" before it |
| 5 | B2 F1 used before defined | F | "In short": "F1 is a grade from 0 to 1" |
| 5 | B3 Stream | F | Defined in §1 |
| 5 | M1 "Matters most" | F | Gone |
| 5 | M2 Summary vs §7 | F | Fixed |
| 5 | M3 "Two exceptions" names three | F | "The exceptions are…" |
| 5 | M4 "False call" vs "false alarm" | P | One "few false calls" remains in "In short" |
| 5 | M5 "Spread" with five meanings | P | Filter "wide" fixed. Still "spread of rates" (Figure 10) and "spread is narrower" (§7) |
| 5 | M6 §3.6 vs §11 calling rule | F | "starts and continues above 0.1" |
| 5 | M7 36-word sentence in §3.6 | F | Split |
| 5 | M8 Network definition | F | Rewritten |
| 5 | M9 0.36 s aside in the recipe | F | Moved to "What the simulator gets wrong" |
| 5 | M10 mHz, percentile, groups used early | F | Defined at first use or pointed to Section 8 |
| 5 | M11 Point buried in "Why the shift" | F | Leads with the conclusion |
| 5 | M12 §8 paragraph should be a list | F | List |
| 5 | M13 Long sentence with "fire" | F | Split |
| 5 | M14 §11 reading level | F | CFAR defined; plain rewrites. "10⁻⁹" still has no unit (minor) |
| 5 | M15 "Pipeline" | F | Not found anywhere |
| 6 | M1 locust anchor | F | Fixed |
| 6 | M2 Bunching comes from the busiest cells | F | "below 50 mHz … matches (1.73 against 1.79) … above 100 mHz … 9.81" |
| 7 | B1 Rate percentiles re-derived another way | F | 80 baselines through `baseline_trains`; page quotes 5.0 / 19.0 |
| 7 | M1 Lane calls clipped before scoring | F | `_overlapping` passes calls "UNCHANGED" |
| 8 | B1 Stream | F | Fixed |
| 8 | B2 "In short" F1, call, detector names | P | F1 defined. "Calls" undefined there; no pointer to §§3–4 for the names |
| [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder] |
| 8 | B4 Percentile and four groups | F | Inline definition; "(Section 8)" |
| 8 | B5 Figure 12C busy sizes unreadable | F | C1/C2 split; order note |
| 8 | M1 "Busy" has three meanings | F | "The busy block is not a third level…"; word list entries |
| 8 | M2 Code names in figures | F | Fixed |
| 8 | M3 Figure 8B crosses 0.1 but "0 calls" | F | "one frame passes 0.1, but it holds fewer than 3 events" |
| 8 | M4 Figure 2C missed ▼ unexplained | F | "misses … small ones, joined by 3 ROIs each"; "nothing planted inside it" |
| 8 | M5 Why decoys exist | F | "stand for lineups a careful person would not count" |
| 8 | M6 §4 vs §6.3 | F | Fixed |
| 8 | M7 Median and ⚠ undefined | F | Word list defines ⚠ and median |
| 8 | M8 Schematics for SPIKE-synch, LoCo, center/surround | N | None added |
| 8 | M9 Shift/shuffle chain | F | Leads with the conclusion |
| 8 | M10 Symbols change meaning | P | Limit break is now a red square. The green ○ "chosen" (Figure 12) still differs from ○ "second call" (Figures 3–9); markers still stack |
| 8 | M11 Table 3 packed score cell | F | Table 4 has separate columns |
| 8 | M12 Figure 12B vs table on trace/tiny and the floor | F | Omitted from B; floor labelled |
| 8 | M13 Sixth-grade reading level | P | Improved; Table 3 (17 columns) and §2 are still dense |
| 9 | B1 Figure 9A mechanism invisible | P | Surrounds now visible. No center/surround-filtered brightness row in B/C |
| [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder] |
| [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder] |
| 9 | M3 Figure 12C unreadable | F | C1/C2 |
| 9 | M4 F1 vs busy-block-calls scatter | N | Not added |
| 9 | M5 Sub-pixel mechanism; zoom column; 0.16 line | N | Not added |
| 9 | M6 Side-by-side figure for where chance comes from | P | Figures 13B and 14 now carry the claim side by side; the requested margin-over-bar figure is absent |
| 9 | M7 Figure 2A doesn't show doubling | F | New Figure 2C bar chart |
| 9 | M8 Simulator recipe as paragraphs | F | Table 2 (Figure 10 caption still 190 words) |
| 9 | M9 Strengths and weaknesses given twice | D | "Sections 3 and 4 listed what each design should do … Table 4 is what Sections 7 and 8 measured" |
| 9 | M10 tube flow schematic | N | Not added |
| [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder] |
| 9 | M12 Captions carry the argument | P | 12 of 18 captions are still over 60 words (Figure 2: 247, Figure 10: 190) |
| 10 | B1 Build currency | F | Every figure restaged 13:01–13:04, after the generator (12:52) and template (12:59); worktree clean at 699de8e. Cached inputs (sweeps, shipped, surrogate JSON) are older |
| 10 | M1 y-labels clipped in Figures 3, 6, 7 | F | "events per second", "ROIs per 10 s bin", "ROIs on, per frame" |
| 10 | M2 Figure 12C busy shades | F | Split, and shaded markers |
| 10 | M3 Figure 12 heading | F | Fixed |
| [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder] |
| 10 | M5 Lane names | F | Fixed |
| 10 | M6 Phone readability | F | "Tap or click any figure…" at the top; images are links |
| 11 | M1 §1 doesn't state the cost | F | Fixed |
| 11 | M2 No roadmap; Figure 1B has no job | F | "How this document goes … (Figure 1B)" |
| [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder] |
| [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder] |
| 11 | M5 Ending never answers §1 | F | §10 "What this means for the lab's question" |
| 11 | M6 Figure 11C result in methods | F | Moved to §7 as Figure 12 |

**Round 2 totals (107 findings):** FIXED 78 · PARTLY 19 · NOT FIXED 7 · SUPERSEDED 0 · DECLINED-ACCEPTABLE 3

## Cheap fixes still open
- **"In short" wording:** "make few false calls" should read "false alarms" and be qualified to shipped settings. "Calls" is also used there before §1 defines it.
- **Figure 13C pointer:** §7 quotes CoactDetect's *shipped* 52% and 24% "(Figure 13C…)", but Figure 13C plots *tuned* recall. The shipped values aren't in any figure.
- [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder]
- [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder]
- **Recording pick rule:** "middle number of ROIs" is undefined for groups with an even count.
- **ROI plural:** "33 ROI" in the raster labels of Figures 2D and 10 vs "ROIs" elsewhere.
- **Parity claim:** "to within 10−9" has no unit.
- **§4.1 tube-guard:** "raises its own bar" should be "its own surround".
- **Figure 12 ticks:** "99.9999999"-style percentile labels.
- **Repo side:** GLOSSARY aliases (decoy, busy block, …) and the locust duration entry; the `bench.py` `MEASURED_BURST_SHAPE` table disagrees with Figure 10D.
