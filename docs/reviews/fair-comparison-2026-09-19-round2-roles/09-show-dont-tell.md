<!-- Verbatim role report, except that this machine's absolute paths are written as %USERPROFILE% and <darkroom> (the repository is public). The unedited original is in <darkroom>/bugarach/2026-09-18-fair-comparison-run/report/review-roles-round2/. -->

GRANT 9 ok — Read, Grep, Glob, Bash

# Role 9: Show, don't tell — fair-comparison report, round 2

**Artifact:** the built `%USERPROFILE%\bugarach\bugarach-worktrees\fair-comparison-report\docs\learned\tuned_vs_coact\fair_comparison_2026_09_18\report.html` at git hash 16ac704.

**How I measured:** I rendered the page in Playwright chromium at a 1100 px viewport, which gives a 980 px column. I counted words on the rendered text and took section extents from the heading positions. I read all 8 figure PNGs and the full-page render in `...\scratchpad\mb\renders_round2\`. My crops are in `...\scratchpad\mb\r2-role-9\`. I did not read round 1's role-9 record (`docs/reviews/fair-comparison-2026-09-19-roles/09-show-dont-tell.md`), so this pass is independent of it.

**Tooling note for the run record:** the no-heredoc hook blocked writing a measurement script to disk, and I hold no Write tool. The script was piped to Python on stdin instead, so no file was written.

**Thresholds (project conventions, adapted for a web page):**
- The 40-words-per-slide rule is **not applied**. Every section of a report exceeds it, so I report the counts instead.
- Applied:
  - any single text block over 60 words;
  - a methods or results section with no figure;
  - two or more consecutive figure-free sections;
  - figure share under 50%, measured as rendered SVG area ÷ (section height × 980 px column);
  - more than 20% empty margin on both sides.

## Per-section table

| Section | Prose words (not counting captions or tables) | Largest block | Figure | Figure share of section | Section height |
|---|---|---|---|---|---|
| Title and lede | 398 | **191** ("The answer") | n | 0% | 653 px |
| 1 Problem | 206 | **206** | Fig 1 (caption 120 words) | 48% | 951 |
| 2 Why a simulation | 255 | **62** | **n** | 0% | 474 |
| 3 Contestants | 197 (+ Table 1: 389 words, 750 px) | **61** | **n** | 0% | 1262 |
| 4.1 Nested cross-validation | 247 | **96** | Fig 2 (83) | **35%** | 792 |
| 4.2 Fold defect | 182 | **123** | Fig 3 (114) | **47%** | 873 |
| 4.3 Better mode | 167 | **105** | **n** | 0% | 385 |
| 4.4 Two selections | 183 | **77** | Fig 4 (74) | **41%** | 747 |
| 4.5 Merge gap | 407 | **144** | Fig 5 (99) | **41%** | 1250 |
| 5 Replicate | 107 | **107** | Fig 6 (28) | **32%** | 434 |
| 6 What came out | 657 (+ Tables 2 and 3: 373 words, 1019 px) | **440** (bullet list) | Figs 7, 8 (219) | **25%** | 3355 |
| 6 Refits below 0.2 | 118 | **81** | n | 0% | 229 |
| 6 Exceeded budget | 106 | 46 | n | 0% | 284 |
| 7 Limits | 530 | **530** | n | 0% | 898 |
| 8 Where everything is | 218 | **218** | n | 0% | 559 |
| Provenance | 16 | 16 | n | 0% | 182 |

**Whole page:** 6,109 rendered words and 13,419 px tall. Figures are 22% of the page area.

**Width is not the problem.** Every figure is 900 of the 980 px column (92%), so the margin rule never fires. Every figure-bearing section still fails the 50% share rule, because the prose around each figure narrates it again.

**Consecutive figure-free runs:**
- §2 → §3: about 450 words plus a 750 px table between Figure 1 and Figure 2.
- §6's two subsections → §7 → §8: here prose is right (see the end of this report).

**Against the owner's ask ("figures to explain conceptually what was done and why"):**
- **Drawn:** the problem (Fig 1), nested cross-validation (Fig 2), the fold defect (Fig 3), the two selections (Fig 4), merging (Fig 5A), the replicate draw (Fig 6, weak).
- **Not drawn:**
  - what a bench recording contains, and the hit rule (§2);
  - how the nets differ (§3);
  - binned vs sliding mode (§4.3);
  - the crowded-recording check (§4.5);
  - **the headline result itself**, the per-fold reversal at matched gaps;
  - what tuning did to each net.

## Findings

Each finding gives: location · issue · severity · fix, naming the replacement figure · whether I could verify it against a source.

1. **Lede, "The answer" (191 words) · major**
   - **Issue:** the headline has no picture. The reversal (−0.007 as run; +0.010 with both gaps at 2 s, 4 of 4 folds; +0.009 at 8 s, 3 of 4 folds) exists only in prose. No figure on the page shows the matched-gap comparison per fold: Fig 8 shows only the settings as chosen, and Fig 5B shows only fold means.
   - **Fix:** add a headline figure in Fig 8's style. Plot chorus_norm minus CoactDetect in three rows: *as run (2 s vs 8 s)*, *both at 2 s*, *both at 8 s*. Show fold dots, a mean bar, the replicate diamond on the as-run row, and a dashed zero line. Put it beside the lede: the question paragraph goes in a narrow left column (about 40%) and the figure takes the rest. Alternatively, add these rows to the top of Fig 8 and move it up.
   - **Relocate:** the binned SCE sentence moves to §6, which already says it.
   - **Verified:** yes. `merge_gap.json` holds per-fold `coded.coact[].f1_by_gap` and `nets.chorus_norm[].f1_mean_by_gap`.

2. **§3, Table 1 and its "drawings not here" note (61 words) · major**
   - **Issue:** the main concept, *where each net stops treating ROIs separately*, is carried by prose and a 389-word table whose "what it does" column is mechanism in words. The architecture drawings exist but are replaced by a production note.
   - **Fix:** a pooling-point schematic with four pipelines (ROI lanes → per-ROI filter → bounded vote → pool → threshold) and a marker where pooling happens:
     - tube pools at the input;
     - chorus_norm and chorus_gain_norm pool after the vote, three ways;
     - line_length takes the share of ROIs lit, then compares it with its own surroundings in time.

     For the coded detectors, one shared schematic: count coincident ROIs → compare with time-shifted copies → call. Each detector's variant can then be a short phrase in the table.
   - **Relocate:** move the note to §8.
   - **Verified:** partially. The drawings' existence (PR #660) is the page's own claim; I did not open the PR.

3. **§2, the bench (255 words, no figure; with §3 it makes the only figure-free run in the methods) · major**
   - **Issue:** what a bench recording contains is a sequence, and it is typed.
   - **Fix, part 1:** add a Figure 1 panel A showing the full 45 minutes of seed 1000 as a lane strip:
     - 15 filled ▼, shaded by participation (30, 18, 10%);
     - 6 hollow distractors;
     - the hatched probe;
     - a "≥120 s" spacing bracket;
     - an inset of the real baseline rate distribution with the 25th and 75th percentiles (0.0052 and 0.019 events/s/ROI) marked as the two backgrounds.

     The current raster becomes panel B, the zoom.
   - **Fix, part 2:** a hit-rule mini-schematic. A call span widened by ±2.5 s that contains a ▼ is a hit, and a long call that spans two ▼ hits both. The prose itself says this "matters later", because it is the mechanism behind §4.5. It could go here or as a top row of Fig 5A.
   - **Verified:** partially. Fig 1 was built from this seed, so the full-length data exist; I did not check the rate distribution source.

4. **§4.3, binned vs sliding (105-word block, no figure) · major**
   - **Issue:** a mechanism, and a shift-sensitivity result, explained in words. This is exactly a "why".
   - **Fix:** a two-row schematic. Six ticks spread over 0.36 s straddle a bin edge: binned counts 3 | 3 and misses, while the sliding window counts 6 and calls. The second row shifts the same ticks by 0.2 s: the binned result flips and sliding does not.
   - **Reuse:** goal 1 already rendered sliding-vs-binned figures, with `tools/compare_sliding_vs_binned.py` producing `<darkroom>/bugarach/2026-09-17-sliding-vs-binned/`, which `docs/goals/coded-detector-optimization.md` cites.
   - **Verified:** yes for the pointer; I did not open the darkroom figures.

5. **§6 bullet "Tuning moved some nets and not others" (16 per-fold numbers as a nested list) · major**
   - **Fix:** a tuned-minus-untuned figure, one row per net, with fold dots, a mean bar and a zero line (Fig 8's style). It could also be a second panel of Fig 8.
   - **Verified:** yes. `results.json` holds `learned[*][fold].untuned` beside `ungated` and `gated`.

6. **§6, the t-value caveat that opens the results (71 + 73 words) · moderate**
   - **Issue:** a statistical hedge comes before any result.
   - **Fix (relocate, don't delete):** keep one sentence on the page: "t is over 4 folds on 3 degrees of freedom and overstates the evidence; Table 2's corrected t ranks consistency and is not a test." Move the Nadeau–Bengio / Bouckaert–Frank / Bengio–Grandvalet discussion to §7, which already has the 3-degrees-of-freedom limit.
   - **Verified:** yes.

7. **§6 bullet list (440 words) with Fig 8 placed after it · moderate**
   - **Issue:** bullet 1 cites Fig 8, but the reader meets 440 words before the picture.
   - **Fix:** reflow so Fig 8 (extended per finding 1) comes right after Table 2. Each bullet then shrinks to its claim plus a pointer to its figure row.
   - **Verified:** yes, on the render.

8. **§4.5 paragraphs 3–4 (113 + 63 words) and Table 3 (12 rows × 7 columns, 681 px) · moderate**
   - **Issue:** the crowded-recording check is defined in words and reported in a table. The "also" column holds one entry.
   - **Fix:** a dot-and-range chart, one row per detector and selection, with crowded F1 on the x axis:
     - a tick for the setting the choice replaces;
     - a shaded pass zone from that value minus 0.02 upward;
     - a range bar for the choices across folds;
     - filled or hollow marks for pass or fail, labelled "n of 4 pass".

     Move Table 3 to a reference position.
   - **Relocate:** move the provenance to §8: "applied afterwards … by `tools/crowded_check_fair_comparison.py`" and "scored against the shipped defaults, no verdict changes". "0.02 not yet signed" goes to §7.
   - **Verified:** partially. `crowded_check.json` holds `max_crowded_drop` 0.02 and each reference's `crowded_mean_f1`. I did not open the per-choice rows.

9. **§4.5 paragraph 2 (144 words) · moderate**
   - **Issue:** it reads out Fig 5B's values (0.731 / 0.748 / 0.803 / 0.741 / 0.775) and the reproduction check.
   - **Fix:** keep "nothing re-chosen, so the curves bound what tuning the gap could do". Move the reproduction check to §8 or notes.
   - **Candidate addition:** a Fig 5 panel C with the same gap sweep on crowded recordings, which would *show* why the check exists.
   - **Verified:** no. `crowded_check.json` looks like it holds values per choice, not a sweep over gaps. The main thread must confirm the data exist before asking for panel C.

10. **§5, Figure 6 · moderate**
    - **Issue:** 150 px of 96 empty boxes whose only content, "the draws share no seed", is one sentence. §5's actual result (does the replicate agree?) is drawn only as diamonds in Fig 8, two sections later.
    - **Fix:** replace Fig 6 with a paired-dot or slope chart: for each net and selection, the mean difference from CoactDetect in this run vs the replicate, with a zero line. Alternatively, put the seed ranges into Fig 2A's fold labels and drop Fig 6.
    - **Relocate:** the darkroom path in §5 moves to §8.
    - **Verified:** yes. `replicate_summary.json` holds per-fold held-out F1.

11. **§1 (206-word block, figure share 48%) · minor**
    - **Issue:** the paragraph narrates Figure 1 and the 120-word caption narrates it again.
    - **Fix:** keep the five problem sentences and cut the walk-through to a pointer. Move the probe-rate comparison (0.06/s, 12× quiet, 3× busy) into the caption. The sentence "whether real coincidence should count against a detector is open" is a caveat and moves to §7.
    - **Verified:** yes.

12. **§4.1 (paragraphs of 79 and 96 words, figure share 35%) · minor**
    - **Issue:** the prose walks Fig 2 step by step.
    - **Fix:** Fig 2B leaves an empty fourth row under its three strips. Fill it with "coded detector: folds 2–4 pooled → scored once" and add "chosen configuration → refit at 5 training seeds → scored on fold 1". The asymmetry between the two sides is then drawn, and paragraph 2 shrinks to a sentence. The configuration-grid paragraph is fine as prose.
    - **Verified:** yes, on the Fig 2 render.

13. **§4.2 (123-word block) · minor**
    - **Issue:** the paragraph and the caption both say "folds 2–4 fit the same ten recordings".
    - **Fix:** the paragraph keeps only the consequence (four folds were fewer than four independent fits); the caption keeps the reading.
    - **Verified:** yes.

14. **§4.4, Figure 4 · minor, optional**
    - **Issue:** it is labelled "a schematic, not data", though `selections/` may hold real candidates.
    - **Fix:** use one fold's real candidate cloud (CoactDetect and chorus_norm) with the 1.6× budget line, which carries evidence as well as the concept.
    - **Verified:** no. I did not open the selection files.

15. **§6, "Choices that exceeded the budget" (16 counts as a list) · minor**
    - **Fix:** a heatmap with rows for the four nets plus CoactDetect, fold columns, and each cell the number of refits over budget out of 5 (out of 1 for CoactDetect). A compact table would also be acceptable.
    - **Verified:** partially, since the per-fold counts are on the page.

## Prose is right here (checked, no finding)

- **Terms paragraph:** it is a glossary.
- **"Refits below 0.2 F1":** two individual cases, and Fig 8 already shows the dots.
- **§7 Limits (530 words):** caveats are what this page should keep, and they are the target for the relocations above. Only the contamination item's provenance clauses (commit 2120516, the branch name, the handoff filenames) belong in §8.
- **§8:** paths and a developer note.
- **Provenance.**

**Boundary with agent 10 (Ship It):** figure widths are fine (92% of the column, no margin rule fired), so I found no geometry or build bug. The low figure share is a layout-policy failure from duplicated narration, and the prescriptions above are reflows.
