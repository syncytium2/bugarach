GRANT 10 ok — Read, Grep, Glob, Bash

## Role 10: build and craft checks, chorus-collapse page, round 1

I found 2 major problems and several minor ones. The build is current, and nothing clips, overlaps or causes page-level sideways scrolling in any of the four renders. The two majors are in the data marks, not the layout: Figure 2 silently squeezes its lowest values onto the bottom tick, and Figure 1 draws dots on top of each other so configurations disappear.

**Artifact:** `<worktrees>/chorus-collapse/docs/learned/chorus_collapse/index.html`, hash-object `5cafecea…` (matches the hash you gave me). It was committed in `259898f` and the tree is clean.

**Renders**, all under `<scratch>/mb-cc/10/`:
- **Full-page slices** at scale 1: `light_1100_00..04`, `dark_1100_00..04`, `light_390_00..06`, `dark_390_00..06`.
- **Element crops** at 2x: `crop_{light,dark}_{1100,390}_{0..5}.png`, in page order: Figure 1, Table 1, Figure 2, Figure 3, Figure 4, Table 2.

No console errors in any render. A DOM script checked every SVG `<text>` box against its SVG edge and against every other text box: nothing is clipped and nothing overlaps, in all four renders.

### Mechanical table

| Element | Render checked | Box on the render (px, % of page width) | Overlap or clipping | Axis names and units | Key and identification | Shared axes | 390 px | Dark | Result |
|---|---|---|---|---|---|---|---|---|---|
| Whole page | all 24 slices | 1100 → page 1100×6128; 390 → page 390×9029 | none; page scrollWidth equals the viewport at both widths, so no page-level sideways scroll | – | – | – | pass | pass: every figure colour is a `var()` token (the 3 hard-coded `#fff` are CSS rules for classes this page does not use) | pass |
| Build is current | test run and timestamps | page 12:08:55, newer than builder 12:08:26, `make_replicate_report.py` 11:21 and data 12:05:04; no replay file is newer than the page | – | – | – | – | – | – | pass: `pytest tests/test_diagnose_chorus_collapse.py` passes 3 of 3, including the byte-for-byte rebuild |
| `<title>` | source | "Why chorus_norm collapses" | – | – | – | – | – | – | pass: short. There is no author or date `<meta>` (see finding 9) |
| Top box and sections 1, 3, 5, 6, 7 (prose) | `light_1100_00/03/04`, `dark_1100_*`, `light_390_*` | text column about 690 px | none | – | – | – | wraps cleanly | pass | pass |
| Figure 1 (`fig-rates`) | `crop_light_1100_0`, `crop_dark_1100_0`, `light_390_01` | SVG 930×194 = 84.5% of page width; at 390, 820 px inside a 358 px scroller with its "scroll sideways" hint | text none; **dots stacked on each other** | x: "share of the configuration's 36 inner fits that collapsed" (a share from 0 to 1, acceptable). y has no name, only row labels "lr 0.003 / 0.01 / 0.03" | single colour; the darker dots come from 0.75 opacity overlap and are not explained; the grey band behind the lr 0.01 row is not explained | A and B both run 0 to 1, rows aligned | pass | pass | **FAIL (finding 2)** |
| Table 1 | `crop_light_1100_1`, `crop_light_390_1` | 1100: fits; 390: 644 px table inside a 358 px scroller | none | – | – | – | cells wrap onto 3 lines ("6 of / 252 / fits") although the table already scrolls; no scroll hint | pass | minor (finding 7) |
| Figure 2 (`fig-census`) | `crop_light_1100_2`, `crop_dark_1100_2`, `crop_light_390_2` | SVG 920×380 = 83.6%; at 390, 820 px inside the scroller | text none; **values below 10⁻³ drawn on the bottom tick** | y: "spread of the output logit (log scale)" names neither the statistic nor a unit; x acceptable | the legend dots are in colour, next to the plot, and match the caption's square swatches (a small glyph mismatch). The sideways scatter (jitter) is not stated | y shared: same range and gridlines, B has no tick labels. x shared, 0 to 1 | pass | pass | **FAIL (finding 1), minor (findings 3, 5)** |
| Figure 3 (`fig-curves`) | `crop_light_1100_3`, `crop_dark_1100_3`, `light_390_*` | SVG 810×460 = 73.6%; at 390, 810 px inside the scroller | none; the green 50-step warm-up line hides under orange by design, and the caption says so | x "training step" (acceptable); y "training loss (mean of 5 logged steps)" does not say which loss | 6 lines, each with a line swatch in colour right under the plot; slots 1 to 6 in order: blue working, orange as run, aqua lr 0.01, yellow lr 0.003, magenta dashed warm-up 200, green dashed warm-up 50 | step axis matches Figure 4 (left edge 70, width 720, 0 to 1799, ticks every 300) | pass | pass | pass, minor (findings 4, 6) |
| Figure 4 (`fig-dead`) | `crop_light_1100_4`, `crop_dark_1100_4` | SVG 810×266 = 73.6% | none; the blue line at 0 sits on the 0 gridline and is still visible | y "dead head layers" (the unit, layers, is in the name); x "training step" | blue working and orange as-run, the same colours as in Figure 3 | step axis matches Figure 3 | pass | pass | pass |
| Table 2 | `crop_light_1100_5`, `crop_dark_390_5` | fits at both widths | none | column "final loss" has no unit (same point as finding 6) | – | – | pass | pass | pass |
| Figure and table numbering | source plus test | Figures 1 to 4 and Tables 1 and 2 appear in page order; each figure is cited by number and name before it appears | – | – | – | – | – | – | pass; Table 1 is never cited in the text (finding 8) |
| Spatial words for panels | source grep | no "left/right/top/bottom panel" anywhere | – | – | – | – | – | – | pass |
| Palette | CSS | light slots are `#2a78d6 #eb6834 #1baf7a #eda100 #e87ba4 #008300`, in order | – | – | – | – | – | dark steps are `#3987e5 #d95926 #199e70 #c98500 #d55181`, but **green `#008300` is the same in dark** | pass for light; dark green not checked against the reference (finding 10) |
| Loss capped at 2.0 (Figure 3) | source (`sy` clamps to [0, 2]) plus the replay data | – | the cap never takes effect: the highest smoothed loss among the 6 plotted lines is 1.70. The raw logged loss reaches 2.495, but only the smoothed value is drawn | – | – | – | – | – | pass: nothing is hidden, but the caption's "Loss is clipped at 2.0" describes a clamp that never fires (finding 4) |

### Findings

1. **Figure 2, both panels: 85 values are pinned to the 10⁻³ floor with no marker.**
   - **Issue:** `fig_census` draws `log10(max(logit_sd, 10**-3))`. Of the 432 inner fits in each net, 59 chorus_norm values and 26 chorus_gain_norm values are below 10⁻³, and some are exactly 0. They are drawn as an ordinary row of dots on the labelled "10⁻³" gridline, so they read as measured values of 0.001. There is no ceiling clamp, but nothing needs one: the largest value is 84.5, under the top tick of 10².
   - **Severity:** major.
   - **Fix:** draw floored points with a different glyph, such as an open circle, and label the floor "< 10⁻³ (59 fits)" / "(26 fits)". At minimum, state the floor in the caption.
   - **Verified:** yes (census.json and builder lines 303 and 320).

2. **Figure 1: stacked dots hide configurations, although the caption says "Each dot is one configuration".**
   - **Issue:**
     - chorus_norm, lr 0.003: 6 configurations, 2 visible positions (5 sit at 0).
     - chorus_norm, lr 0.01: 7 configurations, 3 positions.
     - chorus_norm, lr 0.03: 11 configurations, 8 positions.
     - chorus_gain_norm: 24 configurations, 17 positions.
     - A dot on a dot shows up only as a darker blue, which reads like a second colour and is not explained. Counting dots gives the wrong n.
   - **Severity:** major.
   - **Fix:** stack coincident dots vertically within the row (beeswarm), or size or annotate them by count ("×5").
   - **Verified:** yes (collapse_table.json, grouped the way `fig_rates` groups it).

3. **Figure 2 y-axis: no statistic named and no unit.**
   - **Issue:** "spread of the output logit (log scale)". The logit is a log-odds value with no physical unit, but the axis should still say that "spread" means the standard deviation over the recording's frames, and give the unit ("logits"). The page defines "spread" only in the section 3 prose.
   - **Severity:** major.
   - **Fix:** "SD of output logit over frames (logits, log scale)".
   - **Verified:** yes.

4. **Figure 3 caption: "Loss is clipped at 2.0" describes a clamp that never fires.**
   - **Issue:** the highest smoothed value drawn is 1.70. The sentence is not false, but a reader will look for clipped segments that are not there.
   - **Severity:** minor.
   - **Fix:** either "the axis stops at 2.0; no line reaches it", or drop the sentence. If the axis is ever re-scaled so the clamp fires, mark the clipped segments.
   - **Verified:** yes (all 6 plotted replay logs, smoothed the same way as `fig_curves`).

5. **Figure 2 x: undisclosed sideways scatter that is one-sided at the edges.**
   - **Issue:** the quantity only takes the values k/8, but each dot is shifted by ±0.02 and then clamped to [0, 1]. So the 153 chorus_norm fits and 63 chorus_gain_norm fits at x = 0 scatter only rightward, and the chorus_gain_norm fits at 1.0 only leftward. The caption does not mention the scatter.
   - **Severity:** minor.
   - **Fix:** add a caption clause ("x values are k/8, jittered ±0.02 for visibility").
   - **Verified:** yes (builder line 319).

6. **Figure 3 y-axis and Table 2 "final loss": the loss is not named.**
   - **Issue:** the axis says "training loss" without saying which loss or its unit.
   - **Severity:** minor.
   - **Fix:** name it, for example "training loss (binary cross-entropy, …; mean of 5 logged steps)", using whatever the chorus objective actually is.
   - **Verified:** no (I did not check the objective).

7. **Table 1 at 390 px: cells wrap onto 3 lines inside a container that already scrolls sideways, and there is no scroll hint.**
   - **Severity:** minor.
   - **Fix:** `white-space: nowrap` on this table's cells, plus the same "scroll sideways" hint the figures carry.
   - **Verified:** yes (`crop_light_390_1`).

8. **Table 1 is never cited in the body text**, while Table 2 is ("(Table 2)").
   - **Severity:** minor.
   - **Fix:** cite it in section 2.
   - **Verified:** yes (grep).

9. **Page metadata: no author or build date in `<head>`.**
   - **Issue:** only viewport and charset are set; the `<title>` itself is fine.
   - **Severity:** minor.
   - **Fix:** add `<meta name="author">` and a build date or commit stamp. It has to come from committed inputs, or the byte-for-byte rebuild test will break.
   - **Verified:** yes.

10. **Dark palette: slot 6 green `#008300` has no dark-mode step.** The other five slots do. It is legible on `#1a1a19` (about 3.5:1 by my arithmetic) and only carries the mostly hidden 50-step warm-up line.
    - **Severity:** minor.
    - **Fix:** confirm against the reference palette's dark value for slot 6.
    - **Verified:** no (I have no reference palette file).

11. **Figure 1: two unexplained marks.**
    - **Issue:** the grey band behind the lr 0.01 row, and the missing y-axis name. "lr" is the only name the rows have, and the figure does not spell it out.
    - **Severity:** minor.
    - **Fix:** add a y name ("learning rate") or say "rows: learning rate (lr)" in the caption. The band is ordinary zebra striping and can stay if it is mentioned or made lighter.
    - **Verified:** yes.

**Figure boxes, for role 9's layout judgement.** At 1100 px, Figures 3 and 4 fill 810 of the 1000 px column, leaving 190 px empty on the right; Figures 1 and 2 fill 930 and 920 px. At 390 px all four figures sit at 810–820 px inside their scrollers, so their 12 px SVG text shrinks to about 10.6 px in Figures 1 and 2.

**What I checked and found no problem with:** the build is current and reproduces byte-for-byte. There is no page-level sideways scroll at 390 px; wide content scrolls only inside the figure and table containers. No text is clipped or overlapping in any mode. Panels are lettered A and B, and no spatial words are used for them. The colour keys render in colour next to their figures in Figures 2, 3 and 4. Figure 2's A and B share the same axes. Figures 3 and 4 share the step axis. Figure and table numbering is in order. Figure 3 has the 6 slots in order with both warm-up lines dashed. Dark-mode colours all come from tokens.
