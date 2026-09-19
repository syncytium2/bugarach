<!-- Verbatim role report, except that this machine's absolute paths are written as %USERPROFILE% and <darkroom> (the repository is public). The unedited original is in <darkroom>/bugarach/2026-09-18-fair-comparison-run/report/review-roles-round3/. -->

GRANT 9 ok — Read, Grep, Glob, Bash (SubagentHandback is the delivery channel; I hold no Edit, Write or NotebookEdit)

# Role 9: Show, Don't Tell. Round 3, blind pass

**Artifact:** `%USERPROFILE%\bugarach\bugarach-worktrees\fair-comparison-report\docs\learned\tuned_vs_coact\fair_comparison_2026_09_18\report.html`. I confirmed `git hash-object` = 5c0ccbb6… before reviewing. I did not open the review records or run records. I edited nothing.

## Method and thresholds
- I rendered the page myself at a 1100 px viewport with Playwright chromium (content column 1012 px, page 18,140 px tall). I also viewed the round-3 full-page render in 8 slices and opened fig6.png and fig8.png at full size.
- The page is one scrolling report, not slides, so I scored it one h2/h3 section at a time.
- **Figure share** = rendered figure area ÷ (column width × section height).
- **Thresholds.** These are conventions I chose for a scrolling report, not researched optima:
  - more than 400 words in a section with no figure
  - any single text block over 60 words, captions included
  - a results or methods section with no figure
  - two or more consecutive prose-only sections
  - figure share under 50%, read as too much text, since the figures are not undersized
- Measurement script output: `...\scratchpad\mb\r3-role-9\measure.json`.

## Count table (rendered)
| section | words | largest block | figure | fig share |
|---|---|---|---|---|
| Top (Terms / Question / Answer) | 469 | 192 (Terms) | n | 0% |
| 1 Problem | 384 | 157 (Fig 1 caption) | y (Fig 1, 900×700) | 51% |
| 2 Why a simulation | 373 | 120 | y (Fig 2) | 32% |
| 3 Contestants | 149 + Table 1 (594) | 56 | n (Table 1, 11 rows, 1570 px) | 0% |
| 4.1 Nested CV | 596 | 184 | y (Fig 3, 900×250) | 21% |
| 4.2 Fold defect | 287 | 96 | y (Fig 4) | 47% |
| 4.3 Better mode | 293 | 106 | y (Fig 5) | 40% |
| 4.4 Two selections | 320 | 108 | y (Fig 6) | 36% |
| 4.5 Crowded check | 222 | 139 | **n** | 0% |
| 5 Replicate | 127 | 120 | **n** | 0% |
| 6 Results | 578 + Table 2 (144) | 130 | y (Figs 7, 8) | 39% |
| 7 Merge gap | **727** | 148 | y (Figs 9, 10) | 44% |
| 8 Where they differ | 225 | 151 | y (Fig 11) | 42% |
| 9 Coded choices | 437 + Table 3 (278) | 142 | **n** | 0% |
| 10 Tuning, refits, overruns | 660 | 90 | y (Fig 12, 900×330) | 21% |
| 11 Limits | 622 | 125 | n | 0% |
| 12 Where everything is | 307 | 66 | n | 0% |

**Totals.** The body holds about 6,800 words of prose and captions, plus about 1,016 words in 3 tables. There are 12 figures and about 51 text blocks over 60 words.

**Geometry is clean.** Every figure renders 900 px wide in a 1012 px column, which is 89% of the width. Side margins are about 16 px and 96 px, so no figure has 20% empty margin on both sides. The low shares above come from text volume, not undersized figures.

## Findings (location · issue · severity · suggested fix · verified)

1. **Top matter (Question / Answer)** · The headline result arrives as a 161-word prose paragraph. The first figure starts about 700 px down, and it is a problem illustration, not the result. **Major.** Put a headline figure beside "The answer": a compact version of Figure 8, with net minus CoactDetect, fold dots and means, both draws, and F1-alone vs under-budget. Reflow the answer into a narrow left column with the figure on the right. The replicate and refit caveats in the answer move to section 6, which already carries them. · verified: yes (render)

2. **Section 9, Table 3 (13 rows) and 437 words of bullets** · This is a results section with no figure. Readers must compare "crowded F1 of the choices" against two reference columns by eye, row by row. **Major.** Replace it with a dot plot:
   - one row per detector × selection
   - the 4 fold choices as dots
   - ticks for the starting setting and the shipped setting
   - a 0.02 tolerance band below each tick
   - pass/fail as colour

   The plot also shows the bullet "which reference the check uses changes no verdicts" at a glance. Keep Table 3 as an appendix table for the exact values. · verified: yes

3. **Section 4.5 (222 words, 139-word block), followed by section 5 (127 words)** · This is a methods section with no figure, and together with section 5 it makes two consecutive prose-only sections. **Moderate.**
   - The merge-fuses-close-events concept is already drawn in Figure 9A's "close" row, but that figure sits in section 7, three sections after the check that depends on it.
   - Fix: move the merge schematic (Figure 9A) forward to where the merge gap is first needed (4.4 or 4.5).
   - Add a small panel showing the admissibility rule as a number line: the reference's crowded F1, the 0.02 band below it, and one passing and one failing choice.
   - That breaks the prose-only run. Section 5 can then stay prose (see "where prose is right").
   - Section order itself is role 11's; I raise only where the figure sits. · verified: yes

4. **Section 10 (660 words), the failed-refit lists** · Five near-identical bullets of about 69 words each repeat "the failed-training signature: one long call per recording …" in full. The next paragraph lists the budget overruns as prose plus a 4-item list. **Moderate.**
   - (a) Replace the refit bullets with a strip plot of all refit F1s: one strip per net, both draws, a line at 0.2, and the failures labelled below it. That shows "about 1% of refits" directly. Say the signature once in a caption, and move the per-refit specifics to a compact table (draw, net, fold, seed, F1 alone, F1 under the budget).
   - (b) Replace the false-alarm paragraph with a dot plot of held-out false alarms per hour: one dot per refit, grouped by net, with the budget as a vertical line. That shows directly that the budget caps the rate rather than matching nets to one operating point. · verified: yes

5. **Section 4.1, the 184-word block "What four folds can and cannot show"** · A statistical caveat (Nadeau–Bengio correction, Bouckaert–Frank, Bengio–Grandvalet) sits in the middle of the methods and pushes Figure 3's share down to 21%. **Moderate.**
   - Relocate, don't delete: move the paragraph whole to section 11 (Limits), which already has a "Four outer folds" bullet, or to a collapsible appendix.
   - Leave one sentence here, for example: "t values use Nadeau and Bengio's correction; at 3 degrees of freedom a two-sided 5% test needs 3.18."
   - The 119-word paragraph listing each net's grid (learning rate, steps, settings) and each coded detector's context-window limit belongs in Table 1's "what was tuned" column. · verified: yes

6. **Section 8 (151-word block)** · The paragraph asserts a contrast: events joined by 30% and 18% of ROIs are nearly all found by both sides, and only the 10% events separate them. Figure 11 shows only the 10% level, so half the contrast is told, not shown. **Moderate.** Extend Figure 11 to recall by participation level (30 / 18 / 10%) × background. The divergence at 10% then stands out against two near-ceiling columns, and the numbers in the paragraph (0.59 vs 0.35, 0.81 vs 0.72) can move into the figure or its caption. · verified: yes

7. **Section 7 (727 words, the longest section)** · The 105-word paragraph reads values that Figure 9B already plots (CoactDetect 0.731 at 2 s → 0.748 at 8 s → 0.803 at 30 s; chorus_norm 0.741 → 0.775). The 132-word asymmetry paragraph (coded searched the gap, nets fixed at 2 s) describes something the figure could mark. **Minor.**
   - On Figure 9B, ring where each net actually ran (2 s), as it already rings each coded choice.
   - Cut the repeated values to a pointer.
   - Move the processor-vs-GPU re-scoring arithmetic to section 11, which already has that bullet. · verified: yes

8. **Captions (Figures 1, 3, 4, 5, 6, 7, 8, 9, 10, 11 are over 60 words: 157 / 88 / 96 / 86 / 71 / 105 / 120 / 115 / 77 / 68)** · Several captions carry the argument or a legend the figure should carry itself. **Minor to moderate.** Specific moves:
   - **Figure 1.** Put the onset SD of 0.36 s and "6 aligned ticks among 2,595 firings" in body text or an in-plot label. Label the probe span on the plot itself (e.g. "3× background, 30 s").
   - **Figure 8.** Replace the closing sentence listing the two marks right of zero with a direct annotation on those marks.
   - **Figure 7.** Its symbol explanations repeat the rendered legend; cut them.

   Target: what the figure shows and why it matters, in about 40–60 words. · verified: yes

9. **Section 3, Table 1 (594 words, 1570 px, the tallest block on the page)** · The "where it comes from" column is citation provenance. The "what was tuned" cell repeats "24 configurations, the untuned one and 23 drawn at random" four times. **Minor.**
   - Move the citations to a references list or footnote markers, which shortens the table by roughly 40%.
   - Merge the repeated net cells.
   - A two-lane concept strip (per-ROI → vote → pool, vs pool-first → compare) would show the one difference the prose calls the one that matters. That is a concept diagram, not the architecture drawings the brief sends to draughtsman, but it is the owner's call given the brief. · verified: yes

10. **Top matter, "Terms" (192 words)** · Nine definitions are set as one bold-term paragraph, the largest single block on the page. **Minor.** Prose is right for definitions, but the form is wrong: use a two-column definition list (term | one line). Point ROI / firing / call / event at Figure 1 and Figure 2, which define them visually. · verified: yes

11. **Figure 8, axis range** · The x-axis runs from −0.35 to +0.05 to include the two hollow failed-refit marks, which squeezes every other mark into about 45% of the plot width. **Minor.** Clip the hollow marks to an off-scale arrow at the left edge with their value printed, or break the axis. The payload comparison, within about ±0.17 of zero, then gets the full width. · verified: yes (fig8.png)

## Where prose is right (no finding)
- **Section 5 (replicate):** a short description of the design; once section 4.5 gains a figure it no longer sits in a prose-only run.
- **Section 11 (Limits):** caveats and decisions pending with the project lead. This is exactly what the review is meant to keep. Relocate nothing out of it; it should *receive* the material from findings 5 and 7.
- **Section 12 and Provenance:** file paths and pointers, where prose is the right form.
- **Sections 4.2–4.4:** the paragraphs point at Figures 4, 5 and 6 and each carries one idea.
- **Table 2:** exact means and t values belong in a table, and Figure 7 carries the picture.

## Checked and clean
- The rendered widths, left edges and side margins of all 12 figures, from the render and not the source.
- No figure has empty margin on both sides.
- All figures are numbered.
- The architecture drawings are absent as the brief intends, and section 12 points to them.
