GRANT 9 ok: Read, Grep, Glob, Bash

# Role 9: Density and figure-first ("Show, Don't Tell"), round 1

**Artifact:** `%USERPROFILE%\bugarach\bugarach-worktrees\replicate-report\docs\learned\tuned_vs_coact\replicate1\report.html`, built from `%USERPROFILE%\bugarach\bugarach-worktrees\replicate-report\tools\make_replicate_report.py`.

**How I measured.** I rendered the built page in Playwright chromium at 1100 px wide, which gives a 1000 px content column and a 638 px prose column. I also rendered it at 1600 px and 800 px to test the layout. For every p, li, figure, table and heading I took the box with `getBoundingClientRect`. A figure's graphic box is the union of the img and svg elements inside the figure, not counting the figcaption. A section's area is the section's rendered height times the 1000 px column. Word counts come from the rendered `innerText` and include figure captions and table cells. Text drawn inside SVG figures is counted separately. I read all 8 existing 1100 px slices. I edited no files. The only scratch files are two JSON dumps under `...\scratchpad\mb\role09\`.

**Thresholds used.** These are the role's conventions, adapted to a long web page. Where the page is prose I flag:
- any single text block over 60 words;
- a methods or results section with no figure;
- two or more prose-only sections in a row;
- a figure-bearing section where the figure takes under 50% of the section's area;
- a figure narrower than about 80% of the column.

The 40-words-per-slide cap is **not applied**. A report section is not a slide, and every numbered section except 11 would fail it trivially. I report section word totals so the reader can judge.

## Count table (one row per section, rendered at 1100 px)

| Section | Height (px) | Words | Largest block (words, which) | Figure? | Figure share of section |
|---|---|---|---|---|---|
| Lead + "The answer, first" | 568 | 170 | 48 (bullet 1) | n | 0% |
| 1. The problem | 897 | 296 | **142 (Fig 1 caption)** | y (Fig 1) | 30.5% |
| 2. Why a simulation | 510 | 212 | **133 (paragraph 2, the bench spec)** | **n** | 0% |
| 3. The contestants | 962 | 282 | **104 (Fig 2 caption)**; paragraph 101 | y (Fig 2) | 34.5% |
| 4. Nested cross-validation (CV) | 1273 | 398 | **113 (paragraph 2)**; callout 109 | y (Fig 3) | 36.2% |
| 5. Two selections, shared budget | 1040 | 341 | **153 (paragraph 2, "sliding")** | y (Fig 4) | 31.1% |
| 6. Why two runs | 775 | 155 | **118 (paragraph 1)** | y (Fig 5) | 41.7% |
| 7. Results | 2064 | 346 (incl. Table 1: 75) | 68 (Fig 6 caption) | y (Figs 6, 7; Table 1) | 44.0% |
| 8. Three things not the models | 1529 | **472** | **126 ("edge of grid")**; 123; 81 | y (Fig 8 only) | **11.0%** |
| 9. What the pair can claim | 571 | 242 | **101 (bullet 2)** | **n** | 0% |
| 10. Limits | 573 | 225 | **143 (bullet 2, the bench folder flaw)** | n | 0% |
| 11. Where everything is | 402 | 83 | 42 | n | 0% |

**Totals**
- About 3,120 words of prose, captions and table cells.
- About 750 more words drawn inside the SVG figures: Fig 2 about 165, Fig 3 about 173, Fig 4 about 138, Fig 5 about 93, Fig 7 about 146 (mostly row labels).
- **22 text blocks over 60 words.**

**Figure geometry**
- Figures 1–6 use 968–1002 px of the 1000 px column, so the column is filled; Fig 7 uses 880 px.
- Fig 8 is fixed at **630 px, 63% of the column, with 370 px empty on the right**, and stays 630 px at every viewport.
- At 1600 px the page is capped at 1000 px and centred: 300 px (19%) margin on each side. That is symmetric for text and figures alike, so it is not the "text runs full width, figure shrunk" defect.

**What the figure-share numbers mean here.** Every section with a figure falls below 50%, but except for Fig 8 the figures are not shrunk. The share is low because prose surrounds each figure and the prose often retells it. So the remedy in Sections 1–7 is to take text off the face, not to enlarge figures.

## Findings

Each row gives: location · issue · severity · suggested fix · could I verify it against a source.

**F1.** Section 9 and the lead's "The answer, first" box (the report's headline claims).
- **Issue:** Both are prose-only. The central claim is never drawn: CoactDetect minus the best budgeted net (0.030 and 0.025) and the untuned F1 gap (−0.012 and +0.006), each set against the between-draw movement (median 0.008 F1, most 0.027). The reader has to hold five numbers and two bands in their head. Section 9 is also the start of three prose-only sections in a row (9, 10, 11).
- **Severity:** **High.**
- **Fix:** Add a forest-style **"claims against the between-draw band"** figure.
  - One row per claim: budgeted gap, F1-alone gap, line_length tuning gain, chorus_norm tuning gain, and the rehearsal's +0.011.
  - x axis = F1 difference; one dot per draw in the two run colours; a zero line; a grey band at ±0.027 and a darker band at ±0.008.
  - Put it in Section 9 and a compact copy in the lead box.
  - The 101-word bullet's paired-statistic caveat moves to a note under the figure, not deleted.
  - Generator: new `fig_*` beside `fig_draw_vs_draw`.
- **Verified:** yes (render and numbers on the page).

**F2.** Section 7, Figure 7 ("draw against draw").
- **Issue:** The figure's payload is the typed column "second − first" on the right. The drawn dumbbells sit on a 0.2–0.8 axis, where moves of 0.002–0.006 are a pixel or two long and cannot be seen. The picture shows levels; the finding is differences, and those arrive as text.
- **Severity:** Medium.
- **Fix:** Plot the difference directly.
  - One dot per entry at (second − first), with a zero line and the ±0.027 band shaded.
  - Keep the defect rows bold or coloured.
  - Optionally facet by selection, like Fig 6, which would also shorten the 290 px label gutter.
  - This also gives F1 its noise band.
  - Generator: `fig_draw_vs_draw`.
- **Verified:** yes.

**F3.** Section 7, Table 1 (376 px, 48 numbers, 59-word caption).
- **Issue:** It prints the same 48 means that Figure 7 plots (24 rows × 2 draws) and that Fig 6 marks as ticks. It is a third telling of the results, on the face of the page.
- **Severity:** Medium.
- **Fix:** Relocate, don't delete. Move Table 1 to an appendix or a collapsed `<details>` at the end of Section 7. Carry its † and ‡ markers onto Fig 7's row labels, so the figure alone tells a reader which cells are not results.
- **Verified:** yes.

**F4.** Section 8, "Settings at the edge of their grid": the 126-word paragraph plus Table 2.
- **Issue:** Every row of Table 2 says "8 of 8". The table carries one bit of information. The actual argument is in prose: CoactDetect and LoCo stop at a top of 8 s, near the 6 s crowded spacing; SCE's top is 30 s; the bench spaces events at least 120 s apart.
- **Severity:** Medium.
- **Fix:** Replace Table 2 with a **grid-position strip**.
  - One row per detector; the fusing setting's grid values as ticks on a shared seconds axis (log scale); the chosen value marked, which is the top in all 8 folds.
  - Reference lines at 6 s (goal 1's crowded spacing) and 120 s (bench spacing).
  - The paragraph shrinks to the claim; Table 2 moves to an appendix.
  - Generator: around line 994.
- **Verified:** yes.

**F5.** Section 8, "Coded detectors with no admissible setting" (81 words).
- **Issue:** "Fires 449–527 times per hour … against a ceiling near 17" is a 30-fold gap given as numbers.
- **Severity:** Medium.
- **Fix:** Add a **false-alarm-rate vs F1 scatter** of every candidate a coded search scored, log x axis, with the budget ceiling as a vertical line. Locust's cloud lies entirely to the right of the line, and binned SCE's fold-2 cloud does too. The same figure also serves Section 5 (see F8).
- **Verified:** yes (the numbers are on the page; I did not check the candidate data exist in `results.json`).

**F6.** Section 8, Figure 8.
- **Issue:** The figure is fixed at 630 px, 63% of the column, with the right 370 px empty. Its figure share is 48% of its own block and 11% of the section, the lowest on the page. The prose says "the same signature appears at one refit seed of chorus_gain_norm in each run", which the figure does not show.
- **Severity:** Low–medium.
- **Fix:** A reflow, not a crop.
  - Widen `fig_collapse` to the full 1000 px column.
  - Use the width for the missing evidence: add the chorus_gain_norm panels (one per run) beside the chorus_norm panel, so the sentence points at bars instead of asserting them.
  - Alternatively, put the 123-word paragraph in a narrow left column beside the chart.
- **Verified:** yes (measured at 800, 1100 and 1600 px).

**F7.** Section 2 (a methods section with no figure; paragraph 2 is 133 words).
- **Issue:** The bench specification is typed out: 33 ROIs, 2700 s, 15 events at 10, 6 and 3 cells, 0.36 s jitter, at least 120 s spacing, quiet and busy rates, F1 with a 2.5 s match window. "Every seed is simulated twice" is never shown; Figure 1 shows only the quiet background.
- **Severity:** Medium.
- **Fix:**
  - Give Figure 1 a **second raster row with the same seed at the busy background**. It then shows the two backgrounds and the busy stretch together.
  - Put the numeric specification in a compact **parameter · value table** (about 8 rows) rather than a sentence chain.
  - F1's match rule is already visible in Fig 1's green and red triangles; point at it rather than re-deriving it.
- **Verified:** yes.

**F8.** Section 5, paragraph 2 (153 words, the largest block on the page) and Figure 4.
- **Issue 1:** The paragraph mixes three things: a mechanism (binned vs sliding counting, "lost 30–36% of calls"), a settings list (2 s, 120 s, α = 10⁻⁵, 8 s, 1 s), and code history ("the table of shipped settings in the code still names the binned versions…").
- **Issue 2:** Figure 4 draws the budget's arithmetic, but not what "the best F1 among admissible candidates" means.
- **Severity:** Medium.
- **Fix:**
  - Add a **binned vs sliding schematic**: one coordinated event straddling a fixed bin edge, split across two bins, next to a sliding window that catches it whole.
  - Fold the settings into Fig 4's CoactDetect box, which already carries α and context.
  - Move the code-history sentences to notes or Section 11.
  - Use the F5 scatter (false-alarm rate vs F1, ceiling line, chosen point circled) to show "chosen under the budget".
- **Verified:** yes.

**F9.** Figures 2, 3, 4 and 5 and the paragraphs around them: a pattern of telling each schematic three times.
- **Issue:** Each schematic is told three times: a paragraph, text drawn inside the SVG (about 90–175 words each), and a caption of 79–104 words that retells the rows or boxes.
  - Section 4 paragraph 2 (113 words: "432 inner fits … refit at 5 seeds … coordinate search") restates Fig 3. Fig 3 already prints "432 inner fits, then 4 × 5 refits" and "keep a move only if F1 rises by more than 0.002".
  - The Fig 2 caption restates the italic notes under each row.
  - Fig 4 has two in-figure notes that repeat its caption.
- **Severity:** Medium.
- **Fix:** One telling each. The figure annotates; the caption says what is shown and why it matters in at most 2 sentences; the prose makes the claim and points at the figure. Section 4 paragraph 2 shrinks to one sentence plus "Figure 3, the nested cross-validation". Captions for Figs 2, 3 and 4 shrink to about 30–40 words.
- **Verified:** yes.

**F10.** Section 1, Figure 1 caption (142 words, the longest caption).
- **Issue:** It is a legend in paragraph form (filled or hollow triangles, green or red, shaded bar, CoactDetect row) plus a forward pointer to Section 5. Readers have to decode the figure from a text block below it.
- **Severity:** Medium.
- **Fix:**
  - Move the legend into the figure: lane y-labels with counts ("planted · 15 events", "decoys · 6 bursts", "CoactDetect · 20 calls") and a small key strip in the lane for green/red/hollow and the shaded busy stretch.
  - Cut the caption to what it shows and why (about 35 words).
  - Put the "settings every budget is measured against" pointer in Section 5's prose.
- **Verified:** yes.

**F11.** Section 4, the callout "A defect was fixed before either run started" (109 words).
- **Issue:** This is provenance from the rehearsal run's fold bug and the `fold_check` fix. It is exactly what a review earns, but it sits in the method's main explanation, between the prose and Figure 3.
- **Severity:** Low.
- **Fix:** Relocate, don't delete. Move it to a "Run history" note in Section 10 or 11 (or a `<details>`), and leave a one-line pointer in Section 4.
- **Verified:** yes.

**F12.** Section 6, paragraph 1 (118 words).
- **Issue:** The half about how `--replicate 0` declares byte for byte what WSMIP064 declared, keeping that run resumable, is implementation provenance. The rehearsal's +0.011 is the fact a reader needs, and F1's figure would show it inside the band.
- **Severity:** Low.
- **Fix:** Keep the why-two-runs assertion and Figure 5. Move the declaration-diff and resumability detail to Section 11, next to the `--replicate` line already there.
- **Verified:** yes.

**F13.** Section 10, bullet 2 (143 words).
- **Issue:** The limit itself is one sentence. The rest is decision-tracking provenance: the HANDOFF filename, "item 3 of the decisions waiting on Tony", and the re-measurement date.
- **Severity:** Low.
- **Fix:** Prose is right for a limits section, so no figure. Shrink the bullet to the limit plus its size (12 ROIs, 4 recordings, about 0.03% of events; constants re-measured within their intervals, one borderline). Move the handoff path and decision number to Section 11.
  - Optional: a small forest plot of the 8 fitted constants with bootstrap intervals in both folders would show "one sat just outside". That is justified only if the caveat is expected to be challenged.
- **Verified:** yes (for density; the substance of the caveat is other roles' job).

**F14.** Section 3, coded-detectors paragraph (77 words).
- **Issue:** Six detectors are described in one chained sentence. The nets get Figure 2; the coded side gets nothing parallel.
- **Severity:** Low.
- **Fix:** Add a **6-row table**: detector · what it counts · over what window · compared against what null. A table is the right form for this, not a picture. Alternatively, add a coded-detector block to Fig 2 in the same row grammar.
- **Verified:** yes.

**F15.** Section 11 (83 words, prose-only).
- **Issue:** None. It is a location list, and prose (a list) is the right form.
- **Severity:** None.
- **Fix:** None.
- **Verified:** yes.

**F16.** Section 7, Figure 6 (968 × 432 px).
- **Issue:** None for density. The figure is full column width, the caption is 68 words (slightly over 60), and the one-sentence "lone low dots are defects named in section 8" pointer is caption-appropriate.
- **Severity:** None (only barely over the 60-word threshold).
- **Fix:** Optional: cut the caption's "Left/Middle/right" to the panel headers already drawn.
- **Verified:** yes.

## Summary for the adjudicator

The page's figures are large and mostly use the full column. The density problem here is not shrunk figures (except Fig 8). There are two problems:

1. **The two results that matter most are typed, not drawn:**
   - the headline claims against the between-draw band (F1): Section 9 and the lead box;
   - the per-entry draw-to-draw differences (F2): Figure 7's number column.
2. **The schematics are told three times** (F9, F10), which pushes figure share to 30–44% in every figure-bearing section.

Three sections in a row at the end are prose-only (9, 10, 11). Only Section 9's lack of a figure is a defect; for Sections 10 and 11 prose is right.

Every relocation above (F3, F8, F11, F12, F13) moves text to an appendix, a `<details>`, or Section 11. None deletes a caveat.
