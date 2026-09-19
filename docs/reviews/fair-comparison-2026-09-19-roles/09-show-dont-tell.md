<!-- Verbatim role report, except that this machine's absolute paths are written as %USERPROFILE% and <darkroom> (the repository is public). The unedited original is in <darkroom>/bugarach/2026-09-18-fair-comparison-run/report/review-roles/. -->

GRANT 9 ok — Read, Grep, Glob, Bash (plus SubagentHandback; no Edit, Write or NotebookEdit)

# Role 9: Show, Don't Tell

**Artifact:** `%USERPROFILE%\bugarach\bugarach-worktrees\fair-comparison-report\docs\learned\tuned_vs_coact\fair_comparison_2026_09_18\report.html` (built, 76c3270). I did not edit anything.

**How I measured:** I loaded the built page in Playwright chromium at 1100 px and again at 1440 px. For each h2 and h3 section I measured its bounding box, word counts and each figure's SVG box. Separately I counted the text inside each SVG and opened all 8 figure renders in `renders_round1`. The scratch folder `...\scratchpad\mb\role-9\` holds only a stripped HTML copy. The measurement scripts ran from stdin: the repo's heredoc hook blocked writing them to disk, and this role has no Write tool.

**Thresholds** (conventions adapted for a web page, not researched optima):
- The 40-words-per-slide rule does not apply to a report: every section is over it, so it tells us nothing.
- Any single paragraph, list item or caption over **60 words** is flagged.
- A **methods or results section with over 150 words of prose and no figure** is flagged.
- **Two or more figureless h2/h3 sections in a row** are flagged.
- Figure share = total SVG box area ÷ section box area, where the section box is the 1012 px main column × the section's height. Anything under **50%** is flagged.
- Margins: flagged if a figure has more than 20% empty width on both sides while the text runs full width.

## Per-section table (1100 px viewport; 1440 px gives the same numbers because the column is fixed at 1012 px)

| unit | body prose words | caption words | table words | largest block (words) | figure | figure share of section |
|---|---|---|---|---|---|---|
| h1 + lede | 276 | 0 | 0 | 104 (The question) | n | 0% |
| 1 Problem | 169 | 116 | 0 | 163 (body paragraph) | y (Fig 1) | 52% |
| 2 Bench | 237 | 0 | 0 | 101 (two backgrounds) | **n** | **0%** |
| 3 Contestants | 85 | 82 | 216 | 82 | y (Fig 2) + Table 1 | **32%** (Table 1 takes 42%) |
| 4.1 Nested CV | 211 | 62 | 0 | 107 | y (Fig 3) | **46%** |
| 4.2 Fold defect | 184 | 101 | 0 | 169 | y (Fig 4) | 50% |
| 4.3 Sliding vs binned | 196 | 0 | 0 | **187** | **n** | **0%** |
| 4.4 Two selections | 128 | 50 | 0 | 119 | y (Fig 5) | 53% |
| 4.5 Size of run | 53 | 0 | 0 | 53 | n | 0% (prose is right here) |
| 5 Replicate | 116 | 30 | 0 | 109 | y (Fig 6) | **49%** |
| 6 Results | 364 | 166 | 101 | 83 | y (Fig 7, Fig 8) + Table 2 | **36%** |
| 7.1 Crowded veto | 212 | 0 | 114 | **168** | **n** (Table 3 only) | **0%** |
| 7.2 Not admissible | 99 | 0 | 0 | 55 | n | 0% |
| 7.3 Failed refits | 80 | 0 | 0 | 45 | n | 0% (prose is right here) |
| 8 Limits | 335 | 0 | 0 | 92 | n | 0% (prose is right here) |
| 9 Where | 114 | 0 | 0 | 42 | n | 0% (prose is right here) |

**Text inside the figures (not in the counts above):** Fig 1 has 26 words, Fig 2 177, Fig 3 152, Fig 4 82, Fig 5 93, Fig 6 90, Fig 7 60 and Fig 8 56.

**Blocks over 60 words:** 19 (listed in the finding rows).

**Figureless runs:**
- 7.1 through Provenance is 6 figureless sections in a row: 2,525 px, about 2.8 screens.
- 4.3 is a single figureless methods section between two figured ones.

**Margins:** there is no margin failure.
- At 1100 px, the 900 px figures sit in the 1012 px column with 56 px (5.5%) on each side, and the text shares that column.
- At 1440 px the whole column is centred, so text and figures stay symmetric.

**Page position:** the first results figure (Fig 7) starts at 6,559 px of an 11,128 px page, 59% of the way down and about 7 screens in.

## Findings

Each row: location · issue · severity · suggested fix (naming the replacement figure) · verified against a source (yes/no).

1. **§7.1, crowded-recording veto, and Table 3** · **Severity: high** · Verified: yes (page measured; per-fold data present in `crowded_check.json`).
   - **Issue:** This is the argument that overturns the top-ranked result (binned SCE), and it is made entirely in words: a 168-word paragraph plus an 11-row × 7-column table of numbers. The reader has to picture merge gaps against event spacing in their head.
   - **Fix: a new two-panel figure.**
     - **Panel A, schematic.** Two stacked timelines, each a lane of planted events above a lane of calls.
       - Bench: events at least 120 s apart. A 30 s merge bracket only swallows duplicate calls around one event, so precision goes up.
       - Crowded: events about 6 s apart (goal 1's spacing). The same bracket fuses three events into one call, so recall goes down.
     - **Panel B, data (replaces Table 3's numbers).** A dot-and-range chart with one row per detector × selection, labelled with the merge gap chosen (e.g. "binned SCE · F1 alone · 30 s").
       - x = crowded F1.
       - A tick marks the setting that was replaced; a shaded band shows the 0.02 veto tolerance below it.
       - Four dots per row, one per fold: filled if it passes, hollow if it fails.
       - Add a **"nets: not measured" row left empty**, so the warning box about the nets shows up as a visible gap rather than only as a sentence.
   - **Relocate, don't delete:** Table 3 moves in full to an appendix or a collapsible block under the figure. Its "also" column moves into the marker scheme of finding 6.

2. **§6, "Tuning barely moved the nets"** · **Severity: high** · Verified: partly. results.json contains untuned entries (string match only; I did not open the values), and I did not find the earlier comparison's numbers.
   - **Issue:** This is the causal explanation for the headline ("the earlier lead came from who got tuned"). It exists only as four sub-bullets of "tuned minus untuned" numbers and has no picture.
   - **Fix: a slope (dumbbell) chart.**
     - One row per net, with CoactDetect as the reference row.
     - Untuned F1 → tuned F1, per fold, drawn as arrows.
     - If the earlier comparison's numbers exist, add a second panel: each net's gap to CoactDetect in the earlier comparison → in this run. That slope *is* the sentence "with both sides tuned, it is gone."

3. **Lede, "The answer, in words"** · **Severity: high** · Verified: yes (offsets measured).
   - **Issue:** The answer is given in words at the top, but the first picture of it is about 7 screens down. The page is not figure-first.
   - **Fix:** Put a compact headline figure directly under the answer paragraph and renumber the figures. Either:
     - a means-only version of Fig 8 (each net minus CoactDetect, both selections, the zero line), or
     - Fig 7 reduced to means.
   - The full versions stay in §6. The lede's question paragraph is right as prose.

4. **§4.3, sliding vs binned (one 187-word block)** · **Severity: high** · Verified: yes (page measured; the goal 1 numbers are in `docs/goals/coded-detector-optimization.md` rows 78 and 81, and `tools/compare_sliding_vs_binned.py` exists; I did not open the darkroom figures).
   - **Issue:** This is a methods section whose central claim is visual by nature: sliding mode keeps its calls when a recording shifts by a fraction of a second, and binned mode can lose them. It has no figure.
   - **Fix, schematic.** A short raster of about 6 ROIs with a coordinated burst straddling a bin edge. **Nothing is drawn on the raster:**
     - In lanes above it, binned counts appear as steps per fixed bin (e.g. 3 | 3, under a threshold line) and the sliding count appears as a continuous trace peaking at 6.
     - A second column shows the same raster shifted by 0.5 s: the binned steps change, the sliding peak does not.
   - **Optional data panel:** goal 1's held-out F1, binned → sliding, as a dumbbell chart: LoCo 0.699 → 0.737, CoactDetect 0.702 → 0.746. Reuse the existing `2026-09-17-sliding-vs-binned` figures if they fit.
   - **Relocate:**
     - Why the shipped points are still binned (the viewer defaults) becomes a footnote.
     - The reference settings (alpha 1e-05, 120 s context window, 8 s merge gap, 1 s guard; LoCo at the 99.9th percentile, 8 s merge gap) become a small "reference settings" table or rows in Table 1.

5. **§2, bench description (237 words, two blocks of about 100 words, all numbers)** · **Severity: medium** · Verified: yes (page measured); **no** for the count question below.
   - **Issue:** This methods section has no figure. Fig 1 shows 10 of the 45 minutes, and only the busy background.
   - **Fix: an "anatomy of a bench recording" figure, or new panels added to Fig 1.**
     - **A.** The whole 45 minutes as a lane (not a raster): 15 planted events as down-triangles coded by participation level (30/18/10%), 6 distractors, the probe stretch hatched, and a bracket showing the at-least-120 s spacing.
     - **B.** Quiet and busy backgrounds side by side: short raster strips at 0.0052 Hz and 0.019 Hz per ROI.
     - **C.** Scoring inset: a ±2.5 s hit window around a planted event; a call inside the probe stretch counts as a false alarm per hour and is kept out of precision.
     - **D.** The design grid: 48 seeds × 2 backgrounds, plus the nothing-planted recordings.
   - **Side note, outside my role:** drawing panel D forces the recording count to be explicit. "96 recordings: 48 seeds at both backgrounds, plus one per seed with nothing planted at each background" reads to me as 96 + 96. I have not resolved it; the accuracy roles should check it.
   - The first paragraph ("no answer key") is right as prose.

6. **§6 Fig 7 hollow markers, §7.2 list, Table 3 "also" column** · **Severity: medium** · Verified: yes for the figure; the per-fold `probe_per_hour` and `quiet_per_hour` fields exist in results.json.
   - **Issue:** One hollow marker stands for two different failures: fails the crowded veto, or the budget refused every candidate. §7.2 and Table 3 then explain the difference in words.
   - **Fix, Fig 7 markers:** hollow circle = fails the veto; × = the budget refused every candidate and the search returned its starting point; a small tick = over the budget on the held-out fold. §7.2 then shrinks to a caption line.
   - **Optional new figure:** held-out firing rate ÷ budget, per contestant per fold, with a line at 1.0. This shows whether the budget held on new data for everyone, not only for the two cases §7.2 names.

7. **Figs 3, 5 and 6: body prose inside the SVG** · **Severity: medium** · Verified: yes (SVG text counted; the ink shares are my estimates from the renders).
   - **Issue:** These figures carry 152, 93 and 90 words of SVG text, and part of it is paragraphs rather than labels. It repeats the body text and the caption, and it takes canvas from the graphic:
     - Fig 5's plot uses about 60% of the SVG width; a text column fills the rest.
     - Fig 6's graphic is two strips in the top ~40% of its 300 px.
     - Fig 3's diagram fills the top ~55%, above a paragraph and empty space at the lower right.
   - As a result, §4.1 (46%) and §5 (49%) fall under 50% by box area, and lower still by ink.
   - **Fix, a reflow (not a crop):**
     - Fig 5: move the text column into the caption and give the scatter the full 900 px.
     - Fig 3: move the lower-left paragraph into the caption and close the gap.
     - Fig 6: move its two paragraphs into the §5 body (they repeat it), and either shrink the figure to about 120 px tall or merge it into Fig 3 as panel C ("the replicate's disjoint seeds, same folds").

8. **§6, Table 2 (and a 77-word t-value caveat)** · **Severity: medium** · Verified: yes.
   - **Issue:** Table 2's rows repeat Fig 7's means and Fig 8's differences, and its "(n of 4 not admissible)" notes repeat Fig 7's hollow dots. This is why §6's figure share is 36%.
   - **Fix:** Show the *t* values as right-margin labels on the rows of Fig 8. Move Table 2 to an appendix or a collapsible block for exact values.
   - **Keep the t-value caveat next to wherever the *t* values appear.** It is part of the result's rigor, not something to cut.

9. **§3, Table 1 and Fig 2** · **Severity: low–medium** · Verified: yes.
   - **Issue:** Only one side of the comparison is drawn. The nets get the Fig 2 schematic; the six coded detectors are described only in table text.
   - **Fix:**
     - A companion schematic for the coded six in Fig 2's style: raster → what is counted → null model (time-shifted, shuffled, percentile of neighbouring counts, per-ROI roll, adaptive window) → threshold → calls.
     - The "what was tuned" column becomes a bar chart of candidates evaluated per contestant per fold. That chart is the visual evidence for the thesis "tuned with the same care".
   - Names and kinds stay in a table; a table is right for identity.

10. **§4.4, Fig 5** · **Severity: low** · Verified: no (the `selections/` folders exist; I did not open them).
    - **Issue:** Fig 5 is labelled "a schematic, not data", but the candidates' F1 and false-alarm rates were recorded per fold.
    - **Fix:** Plot the real candidate cloud for one fold for CoactDetect and chorus_norm, with the budget line and both chosen points, and keep the schematic's annotations.

11. **§1, 163-word paragraph and 116-word Fig 1 caption** · **Severity: low** · Verified: yes.
    - **Issue:** The paragraph and the caption describe the same things. The difficulty ("about 6 ticks aligned among 2,595 onsets") is told, not shown: at 10 minutes across 900 px, the 0.36 s spread is not visible.
    - **Fix:** Add panel B to Fig 1, a ±5 s zoom of the raster around 993 s, with the planted marker in the lane above and nothing on the raster. The body paragraph can then shrink to the problem statement, and the caption carries the anatomy.
    - **Optional:** let Fig 1 and Fig 7 widen past the text column on wide screens (the column is 1012 px of a 1440 px viewport).

12. **§4.2, 169-word block** · **Severity: low** · Verified: yes.
    - The prose narrates Fig 4, which is acceptable.
    - **Relocate** the pre-launch check sentence (replayed the draws; `fold_check.distinct = true`) to the provenance section.
    - **Layout:** Fig 4's fold-range labels sit under the legend, away from the strips. Put them directly under panel B as its axis. Role 10 owns the geometry; the reflow is mine.

13. **§8, "values at the edge of their grid"** · **Severity: low** · Verified: yes (`edge_flags` exists per fold in results.json).
    - **Fix:** a grid-position strip chart. One row per coded detector × setting, showing where the chosen value sits in its grid across folds, with edge values highlighted. This supports "most chose the top of their merge-gap grid".

## Where prose is right, and why

- **Lede question and abbreviations:** the question and the definitions have nothing to plot.
- **§2's first paragraph:** the "no answer key" rationale is an argument, not a quantity.
- **§4.5:** the job counts are a few numbers, and 53 words is fine.
- **§5 body:** the replicate's numbers are deliberately not quoted, so there is nothing to plot beyond Fig 6.
- **§7.3:** the two failed refits already appear as Fig 8's two far-left dots, and the caption points to them.
- **§8 Limits:** these are caveats and they are the rigor. Every word stays on the page. A standalone web report has no speaker-notes pane, so relocating them would hide them. Finding 13 adds a figure beside one limit but removes nothing.
- **§9 and Provenance:** paths and build facts.

The owner asked for figures that explain what was done and why. They are missing in exactly four places: §2 (the bench), §4.3 (sliding vs binned), §7.1 (the crowded veto) and the tuning-moved-nothing claim in §6.
