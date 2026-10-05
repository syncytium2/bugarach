GRANT 8 ok — Read, Grep, Glob (I also hold SubagentHandback, which is only for returning this report; I have no editing tools)

# Role 8, "You Lost Me": naive-reader review, blind round 3

**What I reviewed:** `<worktree>/docs/learned/runs/2026-09-25-final-parameters/README.md`, all 547 lines, and the four figure PNGs, which I opened and looked at. I did not open earlier review reports, ADRs or the glossary. The reader I assumed is Tony: he knows the biology and the project broadly, but he did not run this night.

**Overall:** most sections can be followed cold. Two things stop the reader:
- **Decision 1**, the section that matters most, uses three terms that are defined nowhere on the page before that point. It also has a table whose counts read as the wrong unit.
- **Decision 8** says the opposite of Table 1 about fast LoCo, and the page never reconciles the two.

Figure 2's colour draws the eye to the comparison its own caption says not to make.

## Per-section verdict

| section | terms/identifiers first used here | defined here, or in the page's Definitions | can a cold reader follow it? |
|---|---|---|---|
| Opening and the at-a-glance table (lines 1–37) | bench, coded detector, chorus, event floor, co-active ROI, chance null, planted event, busy background, budget, participation minimum, strict rule, decoy, bracketed, hard limit, close-events allowance, `alpha`, extension cap, context, guard, adoption set | ROI and floor are defined here. Most of the rest are in Definitions, but the pointer to Definitions only comes at line 22. "Strict rule" is defined in Decision 1. "Guard" is defined only in Decision 9. "Bench" is defined nowhere. | **no (major).** The table can only be read after the whole page has been read. |
| Decision 1 (lines 39–122) | selection / held-out / fresh seeds, paired resamples, "lowest / middle level", "elevated-rate recording", "the stretch", precision swing, close-events test, `score_bench_candidates.proposal()`, "gain interval" | The seed sets, precision swing and close-events test are in Definitions. **"Level", "elevated-rate recording" and "stretch" are not in Definitions and are not defined before this point.** Level is explained only in Table 3, line 434. The recording and the stretch are explained only in Figure 3's caption, line 187. | **BLOCKING, Decision 1.** Three undefined terms, in the section that asks for the adoption itself. |
| Decision 2 plus Figure 2 | 3 × 3, off-diagonal, "version", "tuned on" | Explained in the caption | yes, but the figure misleads (see F5) |
| Decision 3 plus Figure 3 | "gate", old/new bench layout, the elevated-rate stretch (defined here, after it was already used in Decision 1) | "Gate" is undefined (it is a synonym for budget). The rest are defined. | yes; what to do is incomplete (see F7) |
| Decision 4 plus Figure 4 | participation level, "planted recording", no-coordination recording | Planted recording is not in Definitions; the rest are covered | yes |
| Decision 5 | bin `dt`, "floor-set minimum", plateau | `dt` is not explained in plain words | yes (minor) |
| Decision 6 | none new | — | yes |
| Decision 7 | z-cutoff, "validity rule", "bracketing record" | Z-cutoff is explained. **Validity rule** and bracketing record are not. | mostly (minor) |
| Decision 8 | pair grid, context grid | Pair grid is in Definitions | **no (major).** It contradicts Table 1 (see F3). |
| Decision 9 | guard (defined here), round histories | Guard is defined here, eight sections after its first use | yes (minor) |
| Full tables 1–3 | `sce_min_distance_frames`, `sce_percentile`, `int_win_sec`, `max_gap`, `tau_max`, `null_context_mode` maxlt → symmetric, `C_min`, `dt` | none | **no for those rows (major).** Tony adopts settings he cannot name in words. |
| Real data | senktide_ttx, DI/OVX/MALE/ORX, "own floor − baseline floor" | Groups are expanded; Tony knows the treatments | yes, but there is nothing to decide (see F9) |
| Definitions | — | missing: bench, planted recording, elevated-rate recording, stretch, level, guard, strict rule, validity rule | — |
| What ran | PR A, PR B, workstations | defined inline | yes (audit material) |

## Findings

**F1.** Decision 1, lines 75–83 and 91–96. **Blocking.**
- **Issue:** Three terms are used before any definition: "lowest / middle level" (a participation level), "the elevated-rate recording" and "the stretch". The under-floor table's cells read "22 → 5 of 120". "Of 120" reads as *events*, but the sentence after the table says the numbers are *calls*. So a reader sees "22 of 120 events" and gets the quantity wrong.
- **Fix:**
  - Add "participation level", "elevated-rate recording" and "stretch" to Definitions, or define them inline at first use: "levels: 10/20/30% of a recording's ROIs (fast)"; "a 45-min recording with nothing planted, where every ROI's rate is raised for 5 min (the stretch)".
  - Give the table's header its units and levels, for example "calls matched to under-floor planted events (shipped → proposal), of 120 planted events, 3-participant level on fast". Move the explanatory sentence above the table.

**F2.** Opening, lines 3–37. **Major.**
- **Issue:** About 20 specialist terms are used before the Definitions pointer (line 22), and the at-a-glance table relies on some that are defined only deep in the body: "strict rule" (Decision 1), "guard" (Decision 9), "close-events allowance". "Bench" is defined nowhere. In row 1, "—" in the "could change today's adoption set?" column reads as "no", when row 1 *is* the adoption set.
- **Fix:**
  - Move the Definitions pointer to line 3.
  - Add "bench", "guard" and "strict rule" to Definitions.
  - Put "this is the set" in row 1 instead of "—".

**F3.** Decision 8, lines 301–307, against Table 1, line 363. **Major (the reader is lost).**
- **Issue:** The text says every LoCo search lowered `threshold_pctile` to the 1st percentile, and fast LoCo's extensions "all six … went down, from the 94th percentile to the 1st". Table 1's fast LoCo proposal is `threshold_pctile` 99.5 → **99.99**, which is up. A cold reader cannot square "the search went down to 1" with "the proposal went up to 99.99".
- **Fix:** Say in one sentence why the proposal sits at 99.99 when the search walked down to 1. Say whether the proposal came from a different round or candidate, and why the "cap" flag attaches to the low end.

**F4.** Table 1 (lines 360–385), Decision 5, Decision 1's settings column. **Major.**
- **Issue:** Many settings appear only as code identifiers with no plain-language name. Examples: `sce_min_distance_frames`, `sce_percentile`, `int_win_sec`, `max_gap`, `tau_max`, `dt`, `null_context_mode` maxlt → symmetric (the values "maxlt" and "symmetric" are meaningless cold), `merge_gap_sec`, `bin_width_sec`, `excess_threshold_hz`. Tony is asked to adopt these changes. Some rows already do this right ("coincidence threshold `C_threshold`"; "minimum run of synchronous frames (`n_synchronous_frames`)").
- **Fix:** Give every changed setting a plain name before its identifier, for example "minimum spacing between calls (`sce_min_distance_frames`) 4 → 128 frames". Explain maxlt and symmetric in words.

**F5.** Figure 2 (`figure2_cross_stream.png`) and its caption, lines 137–146. **Major (the figure misleads).**
- **What a cold reader sees:** eight 3 × 3 blue heatmaps, each with a dark middle column and a bold diagonal.
- **Issue:** The colour scale is shared across columns, so the strongest visual pattern is "the slow column is darker". The caption says "levels do not compare between columns" and "compare down a column", so the most salient signal is the one to ignore. The two cells Decision 2 is actually about are not marked:
  - binned SCE, fast-tuned, scored on combined: 0.79 against 0.76;
  - rate+context, combined-tuned, scored on slow: 0.87 against 0.83.

  The layout also resembles a confusion matrix, where readers compare along rows. The caption heads that off, but only in the caption.
- **Fix:** Colour each cell by its difference from that column's diagonal (a diverging map centred on 0), keep the F1 as the text in the cell, and outline the two cells Decision 2 names.

**F6.** Figure 3 (`figure3_elevated_rate.png`). **Minor.**
- **What a cold reader sees:** for each detector, a black budget bar with coloured markers around it, some above the bar.
- **Issues:**
  - The legend draws "shipped point" and "quiet background (filled)" as the same filled circle, so shape and fill are hard to tell apart from the legend.
  - Colour repeats the x-axis category and adds nothing.
  - The x-axis says "SCE" where the text says "binned SCE".
  - Decision 1 cites Figure 3 and Figure 4 before either appears.
- **Fix:** Show the shape legend in hollow grey and the fill legend as a single shape. Drop the per-detector colour, or say it is redundant. Relabel "SCE" as "binned SCE".

**F7.** Decision 3's decide line, lines 199–202. **Major (the reader cannot act).**
- **Issue:** Tony is asked whether to re-measure the ceilings, but the page never says what happens to the four shipped points that fail a budget today if he says no. Do they stay shipped while failing? Are they withdrawn? The line also uses "gate" (line 169), a new word for budget.
- **Fix:**
  - State the default: "if not re-measured, these four stay shipped and failing" (or whatever is true).
  - Replace "gate" with "budget".

**F8.** Figure 4 (`figure4_bench_floors.png`). **Minor.**
- **What a cold reader sees:**
  - Left panel: short coloured vertical bars (each floor's range over 8 seeds) inside grey expected-range boxes. Down-triangles on dotted stems sit well above them.
  - Right panel: a bar chart of the share of events under the floor, by participant count. It reads clearly.
- **Issue:** On the left, the down-triangle and its dotted stem read as a marker "pointing at" something below. In this repo a down-triangle conventionally means "look below". Here it is really the top of the elevated-rate recording's range. "Planted recording" is used but is not in Definitions.
- **Fix:** Draw the elevated-rate range as a bar or whisker like the others, or use a non-directional mark. Add "planted recording" to Definitions.

**F9.** Real data, lines 465–474. **Major (the reader cannot act).**
- **Issue:** The page reports that under senktide the per-window floor rises by a median of +17 on OVX and +20 on ORX, and says it "can absorb the treatment-window co-activity the project studies". Neither this section nor the nine decisions asks Tony anything about it, so he reaches a finding that looks decision-relevant and does not know whether he is being asked something.
- **Also:** "+17" and "+20" carry no unit. Only "+1 ROI" does.
- **Fix:** Either add a decision (which floor the real-data analyses use) or say explicitly that nothing is asked yet. Write "+17 ROIs" and "+20 ROIs".

**F10.** Decision 7, lines 285–291. **Minor.**
- **Issue:** "Validity rule" and "bracketing record" are undefined. The text says Table 2 "shows the search's verdict (a loss of 0.044)", but Table 2 shows only "fail: close-events test". The reader goes looking for 0.044 and does not find it. The decide line asks for "a stated z-cutoff" but offers no candidate value.
- **Fix:** Define both terms. Either put 0.044 in the Table 2 cell or drop the table reference. Propose a cutoff, for example 5 SD.

**F11.** Table 2, lines 394–431. **Minor.**
- **Issue:** Cells stack parentheticals, for example "pass (precision swing not recorded) (close-events against the sliding starting point)", and are hard to parse.
- **Fix:** Put "precision swing not recorded" once, as a note on the held-out column header, and keep one qualifier per cell.

**F12.** Figure 1 (`figure1_fresh_f1.png`). **Minor.**
- **What a cold reader sees:** a forest plot per stream. Circles are shipped points and diamonds are proposals, each with an interval, and blue marks the adoptable ones. The forest-plot conventions hold, so a reader who knows the idiom will not misread it.
- **Issue:** Chorus uses the same diamond as "proposal" even though chorus has no shipped point and is not a proposal. The blue adoptable diamond for combined SPIKE-synch carries no mark that adopting it changes what the detector measures (Decision 1's first caveat).
- **Fix:** Give chorus a different shape. Footnote or mark the SPIKE-synch diamond.

**F13.** Decision 2's decide line, lines 148–149. **Minor.**
- **Issue:** "Keep one setting per stream?" does not name the alternative, or what to do with the one cell whose intervals do not overlap (rate+context, combined-tuned, scored on slow).
- **Fix:** Name the options, for example "(a) keep per-stream settings; (b) ship fast's binned SCE setting on combined as well".

**F14.** Decision 9, line 324. **Minor.**
- **Issue:** "Fixed in the same PR as this page" does not name the PR.
- **Fix:** Give the PR number.

**F15.** Tone. **Minor.**
- **Issue:** Sentence case is consistent and lists are formatted as lists. Two small problems: "1 frames" in Table 1, line 383; and "decoy" and "distractor" used for the same thing (Definitions, line 506).
- **Fix:** Write "1 frame" and use one term throughout.

**Could I verify these against a source?** Yes for F3 (lines 306 and 363 of the page), F9's units, F10 (Table 2 has no 0.044) and F5 (the figure's colour scale). The rest are judgments made as a cold reader, with nothing to check them against.
