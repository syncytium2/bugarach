GRANT 10 ok — Read, Grep, Glob, Bash

# Role 10: build and craft gate, blind verify round 3

**Artifact:** `%USERPROFILE%\bugarach\bugarach-worktrees\replicate-report\docs\learned\tuned_vs_coact\replicate1\report.html`, git hash-object `9a99a7a4209b11b7bb285c260a43ea31aabda1d3`. This matches the hash in the brief. The copy in `scratchpad\build3\report.html` has the same hash.

**Renders:** I made my own with Playwright chromium, in light and dark at 1100 px and 390 px. They include per-figure and per-table element crops, 4× zoom crops of the dense regions, and the embedded raster PNG pulled out at native size (`raster_native.png`). The DOM measurements are in `measure.json`. Everything is under `<session-scratch>\scratchpad\mb3\role10\`. Crops are named like `light_1100_F06_fig-folds.png`, `light_390_T07.png` and `zoom_folds_panelC_low.png`. I did not open any earlier review folders.

## Build currency: PASS
- report.html was written at 09:49:10.85. The generator `tools/make_replicate_report.py` was last edited at 09:48:21.
- Every input the page embeds is older than the build:
  - second draw's `results/` (results.json at 07:48, fits.zip at 08:01, scores.zip at 08:00, merge_gap.json at 09:34:45)
  - first draw's `results/` (all 07:59–08:01)
  - `scratchpad\merge_gap_first.json` (09:19)
  - `scratchpad\shakedown_results.json` (08:52)
- One gap: the generator's default `--merge-gap-theirs` path (`docs/learned/tuned_vs_coact/fair_comparison_2026_09_18/merge_gap.json`) does not exist in this worktree. It exists only in commit 2ca264e. So this build was run with an explicit override. I can't prove from the file alone which merge_gap the first draw's data came from, but every candidate is older than the build.

## Page-wide results (all 4 renders: light and dark × 1100 and 390)
- Console errors and page errors: none. Failed requests: none.
- The page never scrolls sideways: scrollWidth equals clientWidth at both widths. No element outside a scroll wrapper crosses the viewport edge.
- Anchors: all 11 `href="#…"` links resolve. There are no duplicate ids. Each is a "Figure N, name" reference, and all 11 figures are referenced by number and name. Tables 1–7 are all numbered.
- Document properties: `<title>` is "Two draws of the comparison", `meta date` is 2026-09-19 and `meta author` is "bugarach, WSMIP065". All three name this file, not a template.
- SVG text: after dropping line-box grazes of 3 px or less, no text overlaps other text in any figure at either width, and no text runs outside its SVG. Where text sits on a shape, it is always a label inside its own box (Figures 3–5).

## Per-figure table
Boxes are measured off the render in CSS px. The percentage is of the 1000 px content column at 1100 px width. At 390 px the column is 358 px.

| Figure | Render checked | Rendered box at 1100 | At 390 | Result |
|---|---|---|---|---|
| Figure 1, raster (PNG) | light/dark_1100_F01, light_390_F01, zoom_raster_lane, raster_native.png | 1000×273 (100%). The plotted content is only about 84% of that (see finding 1). | 680 wide, scrolls, hint shown | FAIL on geometry and text size (finding 1). Clean on everything else: nothing is drawn on the raster (black ink only); the dense stretch is shaded in the lane only; lane markers point down; ticks read 10m/20m/30m/40m; the y label is "simulated · 33 ROI"; all 7 key rows render in their own colors at 14 px next to the figure. |
| Figure 2, placeholder | light_1100_F02 | Dashed box, 1000 wide | ok | Deliberate placeholder. Renders cleanly. |
| Figure 3, nested cross-validation | light/dark_1100_F03 | 980×440 (98%) | 820 wide, scrolls; smallest text 10.0 px | PASS. The three fills are keyed by swatches in the caption. |
| Figure 4, shared budget | light/dark_1100_F04 | 980×260 (98%) | 820, 10.0 px | FAIL, minor (finding 6) |
| Figure 5, two draws | light/dark_1100_F05 | 980×200 (98%) | 820, 10.0 px | PASS. Draw colors are keyed in the caption. |
| Figure 6, every held-out fold | light/dark_1100_F06, zoom_folds_panelC_low | 986×432 (98.6%) | 820, 10.0 px | FAIL, major (finding 2). Clean on everything else: panels lettered A/B/C; one shared x-range 0.55–0.85 across the three panels; ceiling line and mean tick explained. |
| Figure 7, the collapse | light/dark_1100_F07 | 930×272 (93%) | 820, 10.6 px | Minor (findings 7 and 12). Panels lettered; one y-axis; hatched bars and × explained. |
| Figure 8, between-draw moves | light_1100_F08 | 800×556 (80%) | 800, 12 px | PASS. Filled and hollow dots explained. About 200 px of the column is empty to the right; whether the figure should be wider is agent 9's call. |
| Figure 9, every net against CoactDetect | light_1100_F09, zoom_gaps_zero | 840×320 (84%) | 820, 11.7 px | Minor (findings 4 and 5). |
| Figure 10, matched merge | light/dark_1100_F10, zoom_matched_left | 840×546 (84%) | 820, 11.7 px | FAIL, major (finding 3), plus minor findings 4 and 5. |
| Figure 11, where the false alarms fall | light/dark_1100_F11 | 740×378 (74%) | 740, 12 px | Minor (finding 7). Axis named with units; both bar colors and draw dots keyed in the figure and the caption. |

| Table | Render checked | Width at 1100 / 390 | Result |
|---|---|---|---|
| Table 1 | light_1100_T01 | 571 / scrolls (571) | PASS |
| Table 2 | T02 | 354 / fits | Minor (findings 8 and 11) |
| Table 3 | T03 | 362 / fits | Minor (finding 8) |
| Table 4 | T04 | 582 / scrolls (383) | Minor (finding 11) |
| Table 5 | T05 | 646 / scrolls (560) | PASS |
| Table 6 | T06 | 498 / scrolls (498) | PASS |
| Table 7 | T07, light_390_T07 | 1000 / fits by wrapping (358) | Minor (finding 8) |

## Findings
Each finding gives the location, the issue, the severity, a suggested fix, and whether I could check it against a source.

1. **Figure 1, raster PNG.**
   - Issue, geometry: 16% of the embedded image is blank white on the right. Ink ends at column 2972 of 3540, so lane and raster fill only about 84% of the 1000 px box.
   - Issue, text size: the Bokeh text inside the PNG is small. Digit cap height is 23 native px. That puts the tick and row labels ("10m", "30", "planted", "CoactDetect") at about 9 px at 1100 and about 6 px on a 390 px phone, where the figure is shown at 680 px. The captions and key are 14 px.
   - Severity: **major** on a phone, minor on desktop.
   - Fix: crop the PNG to its ink bounding box before base64-encoding, which also enlarges everything by about 19%. Raise the Bokeh tick and label font sizes in `raster_png`, or render at the displayed width.
   - Checked against a source: yes (native PNG measured, and the crops).

2. **Figure 6, panel C: off-scale triangles.**
   - Issue: the triangles stack exactly on top of each other. Rate+context and SPIKE-synch each have 4 folds below 0.55 per draw (8 SVG paths each, confirmed by their `<title>`s), and locust has 3. But each draw shows **one** triangle, while the caption says "a triangle … is a fold".
   - Issue: those rows have no mean tick because the mean is off the scale, and nothing says so.
   - Issue: locust's first-draw fold 0 dot (the draw's one fold not below 0.55) is half covered by the triangle (zoom_folds_panelC_low).
   - Severity: **major**. The glyph misstates the count, so a reader looks for 3 missing folds.
   - Fix: print a count beside a stacked triangle ("×4") or change the caption to say a triangle marks all folds below 0.55. Say that the mean tick is absent when the mean is off the scale. Nudge the triangle clear of a dot at the edge.
   - Checked against a source: yes (SVG titles).

3. **Figure 10: unexplained off-scale glyphs.**
   - Issue: the triangles and arrowheads at the left edge are never explained. Line_length first draw fold 2 matched at −0.161, and tube first draw fold 1 at −0.205, draw as a line ending in an arrowhead. Tube under the budget, second draw, fold 0, is off the scale at both ends (−0.164 and −0.160). It becomes two identical triangles on top of each other with no line, next to "tube (1 left out)".
   - Issue: Figure 9's caption defines the triangle; Figure 10's does not. It also doesn't say that zero is CoactDetect.
   - Severity: **major**. The arrow reads as the direction of change, not as "off scale".
   - Fix: add "A triangle at the left edge is a value below −0.15; zero is CoactDetect" to the caption. Draw the fold that is off the scale at both ends differently, or state it.
   - Checked against a source: yes (SVG `<path>` titles).

4. **Figures 9 and 10: panels not lettered.**
   - Issue: "chosen on F1 alone" and "chosen under the budget" are two panels, but they are not lettered. Figures 6 and 7 are. The `fig_gaps` docstring even says "(panels A–C)".
   - Severity: minor.
   - Fix: label them A and B, and refer to them that way in the caption and text.
   - Checked against a source: yes (generator lines 728–752 and 845–889).

5. **Figures 9 and 10: different x-limits for the same measurement.**
   - Issue: both plot net minus CoactDetect held-out F1. Figure 9 runs −0.15 to +0.05 with a +0.05 tick; Figure 10 runs −0.15 to +0.04 with its last tick at 0.00.
   - Severity: minor.
   - Fix: use one `lo, hi` pair and one tick set in both.
   - Checked against a source: yes (generator).

6. **Figure 4: colors.**
   - Issue: the ceiling fill `--ceiling` (#e6eef9; dark #243a57) is almost the same as `--box` (#eef3fb; dark #20314a).
   - Issue: the caption swatch for "three ceilings" matches the three middle boxes (the inputs and the reference's calls) about as well.
   - Issue: the `--box` fill itself is never keyed.
   - Severity: minor.
   - Fix: give the ceilings a clearly different hue, or key `--box` and drop the ceiling swatch in favor of the column header.
   - Checked against a source: yes (CSS variables).

7. **Across figures: one concept, two looks.**
   - Issue: the dense stretch is a beige band in Figure 1 (`PROBE_BAND`) but gray in Figure 11 (`--c-dense`).
   - Issue: × means "a call that matched no planted event (a false alarm)" in Figure 1 but "no call at all, F1 0" in Figure 7.
   - Severity: minor.
   - Fix: use one color for the dense stretch everywhere, and give Figure 7's "called nothing" a different glyph.
   - Checked against a source: yes.

8. **390 px: needless scroll hints.**
   - Issue: "Scroll sideways to see the whole table." is shown above Tables 2, 3 and 7, which fit (scrollWidth = clientWidth = 358).
   - Severity: minor.
   - Fix: emit the hint only for tables whose natural width is over about 358 px, or drop it for those three.
   - Checked against a source: yes (measured).

9. **390 px: small SVG text.**
   - Issue: the smallest SVG text is 10.0 px (Figures 3–6), 10.6 px (Figure 7) and 11.7 px (Figures 9–10), next to 14 px captions.
   - Severity: minor.
   - Fix: a slightly larger `min-width` or a larger base font size for the SVGs.
   - Checked against a source: yes.

10. **Tooltips show "-0.000".**
   - Issue: four hover titles show a signed negative zero: Figure 8's two CoactDetect rows, Figure 9's chorus_norm fold 2, and Figure 10's chorus_norm fold 2 as run.
   - Severity: minor.
   - Fix: normalize −0 in the formatter (`x + 0.0`, or round then fix the sign).
   - Checked against a source: yes (grep).

11. **Tables 2 and 4: bare counts.**
   - Issue: Table 2's cells read "146 of 432" and Table 4's read "8 of 8" without a noun. House rule: every number carries its unit. Table 3 does it right ("4 of 20 refits").
   - Severity: minor.
   - Fix: "146 of 432 fits" and "8 of 8 folds".
   - Checked against a source: yes.

12. **Figure 7: bar color not keyed.**
   - Issue: the orange bars carry the second draw's color, but neither the figure nor the caption keys it.
   - Severity: minor.
   - Fix: add an orange swatch before "second draw's" in the caption.
   - Checked against a source: yes.

**Checked and clean:**
- Build is current.
- No console errors, no failed requests.
- No sideways page scroll or elements running off the page, light or dark, at either width.
- No broken anchors, no duplicate ids.
- Document properties name this file.
- All 11 figures and 7 tables are numbered; every figure is referenced by number and name.
- Nothing is drawn on the raster; lane markers point down.
- Time ticks are minutes-friendly.
- No titles above plots, apart from the group headers covered in finding 4.
- The draw colors (blue #2a78d6 against orange #eb6834) contrast clearly, in both themes.
- Figure 11's two stack colors contrast clearly.
- Figure 6 shares one x-range across its panels; Figure 7 uses one y-axis.
- Every figure's axes carry a name and units.
- Dark theme: all SVG marks and text stay legible. The raster keeps a deliberate white card.
