GRANT 9 MISMATCH — missing Grep, Glob; holds no forbidden tools (held: Read, Bash)

# Density and figure-first review (role 9, round 1): the slow co-modulation explainer

**Artifact:** `<worktree>/docs/learned/slow_comodulation/README.md` and its four PNGs.

**Grant mismatch (a finding about the run, not the page).** I was not given Grep or Glob. This review didn't need them, because I did all the searching with Read and Bash. The run record's `roles:` line should still say this reviewer took a fallback path.

**How I measured.**
- I counted words per section with a script.
- I measured figure pixel sizes and in-figure glyph heights with PIL, using the font's digit, ascender and descender heights to convert glyph height to font size.
- I rendered the page locally at an 880 px content column: python-markdown plus GitHub-like CSS, in headless Chromium. From that render I took each figure's width and height, where each section starts, and the table's height.
- This is an approximation of github.com, not github.com itself. GitHub's real column runs about 830–1012 px, so the text sizes below scale by up to 1.15×.
- Render and crops are in `<scratchpad>/review/r9/` (`page_full.png`, `crop_fig3_table.png`).

**Thresholds used.** These are conventions adapted from the slide rules for a web page, not researched optima:
- any single text block over 60 words;
- a results or methods section with no figure;
- two or more prose-only sections in a row;
- a figure taking under about 50% of its section's rendered height;
- text inside a figure under 11 CSS px at 880 px. GitHub body text is 16 px, so that is roughly 70% of it.

## Count table (rendered at an 880 px column)

| section | words | largest block (words) | figure? | section height (px) | figure share of section |
|---|---|---|---|---|---|
| title + opening summary | 64 | 64 (opening summary) | n | 240 | 0% |
| The problem | 170 | 93 | **n** | 374 | 0% |
| How to read the measurement | 366 | **166 (Figure 1 caption)** | y | 1,218 | 51% |
| What the surrogates remove | 351 | **165 (three bullets)**; caption 133 | y | 922 | **35%** |
| What the recordings hold | 645 | **189 (table, 45 cells, 135 numbers)**; dip paragraph 115; caption 103 | y | 1,780 | **28%** (table alone 491 px, as tall as Figure 3) |
| By group | 126 | 75 | y | 775 | 64% |
| What this changes | 392 | 105 (drift paragraph) | **n** | 662 | 0% |
| What this does not settle | 253 | 92 (CoactDetect bullet) | **n** | 462 | 0% |
| Reproduce | 88 | 36 | n (a table is right here) | 312 | 0% |
| **page** | **2,535** | | 4 figures | **6,746** | **29%** (1,931 px of figure) |

## Figure sizes and text size at page width

All four figures are wider than the column, so each fills 100% of its width. Nothing needs a margin reflow.

| figure | native size (px) | rendered size (CSS px) | tick labels | legend | panel titles |
|---|---|---|---|---|---|
| Figure 1, three kinds | 1875×1320 | 880×620 | 9.6 | 8.5 | 9.7 |
| Figure 2, surrogates | 1875×690 | 880×324 | 9.6 | 8.5 | ~9.7 |
| Figure 3, recordings | 1935×1080 | 880×491 | 9.3 | **6.9** | 9.0 |
| Figure 4, by group | 1860×1050 | 880×497 | 9.7 | 8.8 | ~9.7 |

Every figure uses 10 pt ticks at 150 dpi and gets scaled down to about 0.46×. The lab-fast shoulder in Figure 3's zoomed row (+0.05 to +0.09 on a ±0.7 axis) ends up **about 11 CSS px tall**. Cossart's shoulder (+0.01 to +0.02) ends up **about 3 CSS px**.

## Findings

1. **Page as a whole: no at-a-glance figure, and the headline and the decision arrive late.**
   - **Issue:** The first figure appears only after 868 px and about 370 words of prose. The main result (the lab-fast shoulder is minutes-scale drift, holds 91% of the excess, and rigid shift leaves it alone) first shows up at about 2,750 px. Tony's decision question sits at about 5,800 px, in the second-to-last prose section.
   - **Severity:** high
   - **Fix:** Put a new summary figure directly under the opening summary, with the decision question under it. Two panels, lab fast stream only:
     - **Left, about 65% of the width:** the cross-correlogram. Show the recorded curve with its 95% band, rigid shift at *J* 20 s, the 2-minute block control and CoactDetect episodes removed. Use a symlog y-axis that is linear to about ±0.2, so the shoulder fills at least a third of the height. Label the "peak, under 1 s" and "shoulder, 1 s–5 min" ranges in a strip above the axes, not on the curves.
     - **Right, about 35%:** stacked horizontal bars of excess onset pairs under 1 s versus beyond 1 s, one bar per arm. Draw absolute counts, not 100% bars, so the reader sees the shoulder's mass stay put while the peak's mass collapses.
     - The data already exist in `summary.json` → `folders.steps_excluded/fast.peak_and_shoulder`. The under / beyond pairs are: as recorded 28,069 / 289,499; CoactDetect removed 9,020 / 262,238; rigid shift *J* 20 s 4,867 / 309,370; block control 3,697 / 301,349.
     - Proposed caption: *"Figure 1. On the lab fast stream, 91% of the excess coincident onset pairs lie beyond 1 s, and removing the sub-second peak (surrogates, CoactDetect) leaves them in place."*
     - Renumber the other figures.
   - **Verified against a source:** yes, for the layout positions and the `summary.json` fields. The unit of `under`/`beyond` (pooled pair counts?) needs the author to confirm.

2. **Figure 3, the recordings: the only legend is unreadable at page width.**
   - **Issue:** The legend renders at about 6.9 CSS px and sits in one lower-left panel, but all six panels need it to tell seven arms apart. Tick labels render at 9.3 px.
   - **Severity:** high
   - **Fix:**
     - Move the legend into a full-width row under the figure, as Figure 2 already does.
     - Size fonts so that font pt × dpi / 72 × 880 / figure width ≥ 11. At 150 dpi on a 1935 px figure, that means text of at least 12 pt.
     - Alternatively, split the figure: one row per stream, each at full width.
   - **Verified against a source:** yes (glyph measurement and render).

3. **Figures 1, 2 and 4: in-figure text is 8.5–9.7 CSS px.**
   - **Issue:** At that size the text is readable on a Retina screen but not at a glance. Figure 1's legend is the key to its panel D.
   - **Severity:** medium
   - **Fix:** Use the same font-size rule as in finding 2, or shrink the figure size in inches at the same dpi so text grows relative to the image. Boundary: agent 10 owns the mechanical label check; I'm only judging whether the text reads at page width.
   - **Verified against a source:** yes

4. **The results table in "What the recordings hold".**
   - **Issue:**
     - 9 rows × 5 lag bins, 135 numbers in all.
     - At 880 px every cell wraps its interval onto two lines, so the table is 491 px tall, the same height as Figure 3.
     - It repeats Figure 3 in text form, and a reader can't see a pattern in it.
   - **Severity:** medium–high
   - **Fix:**
     - Replace it with a dot-and-whisker (forest) plot: one small panel per stream, lag bins on the x-axis, arms as coloured dots with 95% whiskers.
     - Give it a shared linear y-axis for the four bins beyond 2.7 s. That puts shoulder values 0.05–0.16 and the slow-stream dip on a readable scale.
     - Show the 0–0.25 s bin as a separate strip, since its values (2.06, 21.94) would crush the scale.
     - Don't delete the table: move it into a collapsed `<details><summary>Numbers behind Figure N</summary>` block.
   - **Verified against a source:** yes

5. **Figure 3, bottom row: the ±0.7 zoom is too coarse for the claims the text makes.**
   - **Issue:**
     - The "flat and unchanged by rigid shift" shoulder on lab fast is about 11 CSS px tall. The arms differ by 1–5 px.
     - Cossart's shoulder (+0.01 to +0.02) is invisible in both rows, yet the text claims it "looks negligible and is not".
     - Cossart's two rows are near-duplicates, so one panel is wasted.
   - **Severity:** medium
   - **Fix:** Set the bottom row's y-limits per column: about −0.1…0.3 for lab fast, keep ±0.7 for lab slow (for the dip), and about −0.05…0.1 for Cossart. If the summary figure in finding 1 is adopted, the lab-fast column can drop back to supporting evidence.
   - **Verified against a source:** yes (measured the axis scaling on the image)

6. **The "shoulder holds most of the excess" bullet (0.91 / 0.71 / 0.86).**
   - **Issue:** A share across three folders is given as prose.
   - **Severity:** medium
   - **Fix:** Show one 100% stacked bar per folder (under versus beyond 1 s) from `peak_and_shoulder.real`. Put it in the summary figure's right panel as a second facet, or as a strip under Figure 3. Keep the sentence stating the 1 s cut and the 5-minute cap; that caveat stays.
   - **Verified against a source:** yes (the fields exist)

7. **Captions carry methods and inventory instead of the finding.**
   - **Issue:**
     - **Figure 1 (166 words):** simulation parameters, an axis-scale note, and an argument quoting the simulator's docstring.
     - **Figure 2 (133 words):** surrogate definitions and trimming.
     - **Figure 3 (103 words):** counts, hours and what the shading means, with no takeaway. The takeaway sits after the table ("Every folder has both a peak and a shoulder").
   - **Severity:** medium
   - **Fix:** Make each caption two lines: what the figure shows and why it matters. Move the rest, don't cut it: parameters, surrogate definitions, trimming and the axis-scale notes go into a `<details>` "How these were measured" block beside the figure, or a short Methods section above Reproduce. Suggested captions:
     - Figure 2: *"Rigid shift removes structure faster than J and spreads the event peak into a plateau; drift slower than J passes through."*
     - Figure 3: *"Every folder has a sub-second peak and a shoulder out to minutes; on the lab fast stream only the peak responds to the surrogates."*
   - **Verified against a source:** yes

8. **The opening: "The problem" and the first half of "How to read the measurement".**
   - **Issue:** Two prose-only stretches in a row (374 px and about 600 px) before any picture. The "How to read" section's three bullets (narrow peak, broad shoulder, nothing) repeat Figure 1D's legend.
   - **Severity:** medium
   - **Fix:** Put Figure 1's top two rows (the three worlds' activity traces and rasters) right under "The problem"; they are the picture of the two kinds of activity. Replace the three bullets with one sentence pointing at Figure 1D, the cross-correlogram panel. The definition of excess coincidence stays as prose, which is right for a definition.
   - **Verified against a source:** yes

9. **The last three sections are prose-only ("What this changes", "What this does not settle", "Reproduce"; 1,436 px, the final 21% of the page).**
   - **Issue:** This is two or more prose-only sections in a row. Prose is **right** for all three:
     - "What this changes" is argued reasoning with no model run behind it;
     - "What this does not settle" is caveats;
     - "Reproduce" is commands.
   - **Severity:** low
   - **Fix:**
     - **Relocate, don't delete.** Move the decision question ("does shared drift over minutes belong to coordination, to the background, or to the producer?") to the top with the summary figure. Put the caveat list in a `<details>` block, or leave it at the end.
     - The "small displacement is not a modulation control" bullet should point at Figure 2A and Figure 3A instead of repeating numbers.
     - Optional figure for the `count_excess` bullet: show the share of lit ROIs for the 5-minute world before and after subtracting a 30 s moving mean (two stacked lanes). It would show the drift cancelling. It is also a new measurement, so label it measured, not argued.
     - Order across sections is role 11's call.
   - **Verified against a source:** yes

10. **The paragraph about the lab slow stream's dip (115 words).**
    - **Issue:** The paragraph is over 60 words, and its numbers (−0.55, −0.53, +0.03, +0.10, +0.36 to +0.57) are all visible in Figure 3B's bottom panel.
    - **Severity:** low
    - **Fix:** Keep the argued refractory reading as prose, since it is a mechanism claim. Replace the numbers with "Figure 3B, lower panel". Optionally mark the 2.80–3.20 s refractory floor as a bracket in a strip above that panel, not as a band over the curves; the house rule is that marks over data are annotations on it.
    - **Verified against a source:** yes

11. **"By group" (Figure 4 plus a 75-word paragraph).**
    - **Issue:** The figure takes 64% of its section, which is fine. The section reports a null result with a confounding caveat.
    - **Severity:** low
    - **Fix:** Prose is right for the caveat that group can't be separated from imaging day. Optionally fold the whole section into a `<details>` block so it doesn't sit in the main results flow. Keep the ⚠ caveat as written.
    - **Verified against a source:** yes

12. **Empty space inside Figures 1 and 2.**
    - **Issue:** Figure 2 has a blank band of about 10% of its height between the x-axis labels and the legend. Figure 1 has a gap of about 7% between its activity-trace row and its raster row.
    - **Severity:** low
    - **Fix:** Tighten the layout (legend `bbox`, `hspace`). The gain is small; the page-width share is already 100%.
    - **Verified against a source:** yes

**Direct answer to the brief's question.** Yes, a single figure could carry the whole message for Tony: the two-panel lab-fast summary in finding 1, with the correlogram on the left and the stacked peak-versus-shoulder bars on the right. Everything it needs is already in `summary.json`, and it would let the table and most of the results bullets move into a collapsed block below.
