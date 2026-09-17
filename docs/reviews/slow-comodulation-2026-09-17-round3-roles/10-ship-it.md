GRANT 10 MISMATCH — missing Grep, Glob; holds no forbidden tools (Read and Bash only)

The missing tools didn't block anything: I did the searches with `grep` and `ls` through Bash. This is a note about the run, not the figures, and the run record should say the review took a fallback path.

# Build and craft table — slow co-modulation figures, commit 2f77de1

"Placed" means the size on an 880 px GitHub column: 0.489× for the 1800 px-wide figures and 0.469× for the 1875 px ones. At 150 dpi, 11 pt text lands at about 11 px and 12 pt at about 12 px. GitHub body text is 16 px.

## Build

| Unit | Render checked | Result |
|---|---|---|
| **Build current** | All seven PNGs in the repo, the darkroom and `<scratchpad>/review3/r10/` | **Pass.** The generator was saved at 13:21:55 and the measurement tool at 13:17:15. `results.json` was written at 13:25:36, then the PNGs at 13:25:37–38, then the commit at 13:26:25. `git status` is clean. I rebuilt everything from HEAD's generator and the darkroom `results.json` into r10: **all seven files are byte-identical** to the darkroom copies, with 0 pixels different. |
| **Repo copy = darkroom copy** | sha256 of each file | **Pass.** All 6 figures, `README.md` and `summary.json` match. The repo README is older by mtime (13:25:14 against 13:25:38) but has the same hash. |
| **Single-recording figure kept out of the repo** | `ls`, `git ls-files`, `git log --all` | **Pass.** `one_recording.png` is not in the tree or in the branch history. `summary.json` has no `raster` or `counts_per_minute` keys. The deleted `fig1_how_much_the_count_swings.png` (commit ab736cd, which is on origin) is pooled data only; I looked at it. |

## Figure 1, the two kinds (`fig1_two_kinds.png`, 1800×1980, placed 880×968)

| Unit | Box placed on the column | Overlap / clip | Elements present | Axes: name and units | Letter and caption | Legend, colour, glyph | Scales | Smallest text placed | Ticks, raster rule, titles | Verdict |
|---|---|---|---|---|---|---|---|---|---|---|
| **A–C** | each 236×77 px (27% × 8%) | **FAIL.** B's y-label ("shared modulation, 20 s") runs off the top edge: 22 ink pixels in the top 3 rows, columns 659–671. It also sits on A's "20m" tick label. C's y-label sits on B's "20m" tick label. Checked on crop `crops/f1_top_mid.png`. | step lines for all 3 worlds | "share lit per 10 s" plus "time (first 20 minutes)" | A, B, C used in the caption | the y-labels are coloured in the world colours | shared, 0–0.5 | 11 pt ≈ 11.2 px | 0s…20m, no titles | **fail** |
| **D–F** | each 236×152 px | no problems | 32-ROI rasters, synthetic | "1-minute zoom from 8m45s" plus "N ROIs" | D, E, F sit outside the frame and are used in the caption | the rasters are one black ink | fixed 1 minute wide | 11.2 px | 0s…1m. Nothing is drawn on the rasters. | pass |
| **G** | 776×200 px | no problems | 4 curves plus the zero line | "excess coincidence (observed ÷ chance − 1)" plus a lag label with log-scale note | G used | the legend covers all 4 | shared with H, −0.15 to 0.9 | ticks ≈ 12.2 px | 0.3s…5m | pass |
| **H** | 776×198 px | no problems | 4 curves | lag label that says the scale is linear | H used | **no legend of its own.** It relies on G's. The coloured labels in A–F cover 3 of the 4 lines; the gray dotted background line is keyed only in G. | shared | 12.2 px | 0s…2m | minor |

## Figure 2, the surrogates drawn (`fig2_the_surrogates.png`, 1800×1260, placed 880×616)

| Unit | Box placed on the column | Overlap / clip | Elements present | Axes: name and units | Letter and caption | Legend, colour, glyph | Scales | Smallest text placed | Ticks, raster rule, titles | Verdict |
|---|---|---|---|---|---|---|---|---|---|---|
| **A–D** | each 686×101 px. The row names take the left 20% of the width, with about 100 px of empty gap before the ROI ticks. | no problems. Crop `f2_tagB.png` shows the B letter clears A's ticks. | 4 trains × 4 rows. The dropped onset in B is counted (1 onset). | "ROI 1–4" plus "time (schematic)" | A–D used | black marks only | shared x | ROI ticks and the note are 11 pt ≈ 11.2 px | 0s…4m. The note "1 onset pushed past 4m is dropped" sits above B's frame: an annotation in title position, but not a title. | pass (the gap is minor) |
| **Lane above D** | same width as D | no problems | ▼ at 2m, matching D's 2m tick (x = 1062 px) | not applicable | the caption says "the lane above it" | purple, the same colour as the block control arm; labelled on the figure | shares x with D | 11.2 px | points down at D and is not drawn on the raster | pass |

## Figure 3, what the surrogates remove (`fig3_what_the_surrogates_remove.png`, 1875×2250, placed 880×1056)

| Unit | Box placed on the column | Overlap / clip | Elements present | Axes: name and units | Letter and caption | Legend, colour, glyph | Scales | Smallest text placed | Ticks, raster rule, titles | Verdict |
|---|---|---|---|---|---|---|---|---|---|---|
| **A–E** | each 302×169 px (34% × 16%) | no problems. D's two-line y-label is taller than its axes but collides with nothing. | all 7 arms in each panel | "excess coincidence, y to X" plus the world. D and E carry the lag label. | A–E used | the legend covers all 7 arms | differ per panel, and each limit is named in its label | 12 pt ≈ 11.7 px | 0.3s…5m | pass |
| **F** | 302×169 px | no problems | 4 arms × 6 worlds plus the "= 1" line | y: "count variance ÷ independent, 1-minute bins (log scale)". **The x axis has no name.** The category ticks read "20 s", "5 min", "shallow 1 min", not the "20s"/"5m" form used on every other time axis. | F used | the "F:" entries in the legend cover it | not applicable | the tick labels are 11 pt ≈ 10.8 px | not a time axis | minor |
| **Legend area** | 96 px (9%) blank below the legend | no problems | — | — | — | **Lists "curve above the view", but no curve leaves any panel.** Maxima are 0.53, 0.74, 0.48, 0.08 and 1.59 against tops of 0.9, 0.9, 0.9, 0.25 and 1.75. Its gray ▼ also sits next to F's navy ▼ for "rigid shift, J = 20 s". | — | 12 pt | — | minor |

## Figure 4, how much the count varies (`fig4_how_much_the_count_varies.png`, 1875×840, placed 880×394)

| Unit | Box placed on the column | Overlap / clip | Elements present | Axes: name and units | Letter and caption | Legend, colour, glyph | Scales | Smallest text placed | Ticks, raster rule, titles | Verdict |
|---|---|---|---|---|---|---|---|---|---|---|
| **A–C** | each 248×217 px (28% × 55%) | no problems. The y-label top clears the edge by about 10 px (crop `f4_ylabel_top.png`). | 4 arms × 3 bin widths, filled and hollow markers, whiskers. C has no episode-removal arm. | y-label with log-scale note; x: "bin width" plus dataset and counts | A–C used | the legend covers the filled markers, hollow markers, whiskers and the "= 1" line. "(lab only)" is marked. | shared y (`sharey`) | 12 pt ≈ 11.7 px | 1s, 10s, 1m | pass |
| **Legend** | — | no problems (crop `f4_legend.png`) | 7 entries | — | — | ▼ here means rigid shift, but means "curve above the view" in Figures 5 and 6 | — | 11.7 px | — | minor (glyph) |

## Figure 5, the recordings' correlograms (`fig5_recordings.png`, 1875×1875, placed 880×880)

| Unit | Box placed on the column | Overlap / clip | Elements present | Axes: name and units | Letter and caption | Legend, colour, glyph | Scales | Smallest text placed | Ticks, raster rule, titles | Verdict |
|---|---|---|---|---|---|---|---|---|---|---|
| **A–C** | each 208×254 px (24% × 29%) | no problems. The letters clear the bands (crops `f5_A_tag.png`, `f5_C_tag.png`). | 8 arms, a gray band, a green hatched band. C has no removal arms. | "excess coincidence, full range" plus the dataset | A–C used | covered | differ per column, marked "full range" | 11.7 px | 0.3s…5m, no titles | pass |
| **D–F** | each 208×332 px | **FAIL.** F's x-label is cut off at the right edge ("(log sca…"): 40 ink pixels in the last 3 columns, rows 1452–1465. Checked on crop `f5_F_xlabel.png`. | all present; off-view marks at the top | "zoomed to X" plus counts | D–F used | covered | differ per column, named | 11.7 px; the ▼ off-view marks are about 6 px | 0.3s…5m | **fail** |
| **Legend** | 66 px (8%) blank below it | no problems | 13 entries | — | — | "CoactDetect episodes removed" and its hatched band don't say "(lab only)", though C and F have neither | — | 11.7 px | — | minor |

## Figure 6, by group (`fig6_by_group.png`, 1875×1725, placed 880×810)

| Unit | Box placed on the column | Overlap / clip | Elements present | Axes: name and units | Letter and caption | Legend, colour, glyph | Scales | Smallest text placed | Ticks, raster rule, titles | Verdict |
|---|---|---|---|---|---|---|---|---|---|---|
| **A–B** | each 347×265 px (39% × 33%) | no problems | 4 groups × solid and dashed lines; ▼ marks | "excess coincidence, y to 0.8" plus stream and arm | A, B used | ORX and OVX are a low-contrast pastel pair | shared, −0.8 to 0.8 | the y-labels are 11 pt ≈ 10.8 px | 0.3s…5m | fail (colour) |
| **C–D** | each 347×265 px | **FAIL.** Dashed equal-weight lines leave the view with no mark. In D, MALE's dashed line is above 0.35 in 9 lag bins. In C, ORX's dashed line is above in 1 bin and OVX's is below −0.1 in 3 bins. There is no below-view mark at all. Checked numerically and on crops `f6_D.png` and `f6_C_bottom.png`. | the marks miss the dashed lines | "y to 0.35", named | C, D used | ORX (#c49c94) and OVX (#ff9896) can't be told apart as thin dashed lines. MALE (#bcbd22) dashed is faint on white. | shared, both 0.35 | 10.8 px | 0.3s…5m | **fail** |
| **Legend** | — | no problems | 7 entries | — | — | covers groups, solid and dashed, and ▼ | — | 11.7 px | — | pass |

## Single recording, darkroom only (`<darkroom>/…/one_recording.png`, 1800×690)

| Unit | Box | Overlap / clip | Elements present | Axes: name and units | Letter and caption | Legend, colour, glyph | Scales | Smallest text | Ticks, raster rule, titles | Verdict |
|---|---|---|---|---|---|---|---|---|---|---|
| **Single panel** | 1602×523 px at native size | no problems | 3 lines | "onsets per minute, all 21 ROIs" plus "time in the trimmed baseline window (1-minute bins)" | a single panel, so no letter | the legend covers all 3 lines. The arm colours match Figures 3–5. | not applicable | the gray footer is 10 pt (21 px native) | 0s…15m, no title, not a raster | pass |

**Colour across figures:** each arm keeps one colour and style through Figures 3, 4 and 5 and the single-recording figure. The world colours appear only in Figure 1, and the group colours only in Figure 6.

**Minutes-friendly ticks:** every time axis passes. The one exception is Figure 3 panel F's category labels.

---

# Findings

| # | Where | Issue | Severity | Suggested fix | Verified against the render |
|---|---|---|---|---|---|
| 0 | this run | Grant mismatch: Grep and Glob were not provided; Read and Bash were. No editing tools were held. | run finding | Note in the run record's `roles:` line that the review took a fallback path | yes |
| 1 | Figure 1, panels A–C | B's y-label runs off the top of the image and sits on A's "20m" tick label. C's y-label sits on B's "20m" tick label. | **major** | Give the top row its own gridspec with `wspace` ≥ 0.3. Or keep only "share lit per 10 s" on A–C and let the D–F labels carry the world names. | yes |
| 2 | Figure 5, panel F | The x-label is cut off at the right edge ("(log sca…"). | **major** | Put `right` at about 0.96, or draw one centred lag label for the row | yes |
| 3 | Figure 6, panels C and D | The off-view mark only checks the solid pooled lines. Dashed lines leave the view unmarked: in D, MALE's is above in 9 bins; in C, ORX's is above in 1 bin and OVX's is below in 3. There is no below-view mark, yet the legend and Figure 5's caption say every exit is marked. | **major** | Pass both the solid and dashed lines to `off_scale`, and add a bottom-edge mark. Or widen C and D so the dashed lines fit. | yes (numbers and crop) |
| 4 | Figure 6, group colours | ORX (#c49c94) and OVX (#ff9896) are a low-contrast pastel pair and blur together as thin dashed lines. MALE (#bcbd22) dashed is faint on white. | **major** | Pick four hues that differ in lightness, not used for any arm or world, and check the dashed lines at placed size. The pinks and browns of Figure 1's worlds are also worth avoiding. | yes |
| 5 | Figure 3 legend | "Curve above the view" is listed but never drawn, because no curve exceeds its panel's top. Its ▼ also sits beside F's ▼ for rigid shift. | minor | Add the legend entry only when a mark is actually drawn | yes |
| 6 | Figures 2–6 | ▼ carries three meanings: rigid shift (Figure 3 panel F, Figure 4), "curve above the view" (Figures 5 and 6) and the block edge (Figure 2's lane). | minor | Give rigid shift a non-directional marker (for example "X" or "P") and keep ▼ for marks that point at something | yes |
| 7 | Figure 1, panel H | It repeats G's four lines without a key. The gray dotted background line is identified only in G. | minor | Add "colours as in G" to H's y-label, or a compact legend | yes |
| 8 | Figure 3, panel F | The x axis has no name. The category ticks use "20 s" and "5 min" instead of "20s" and "5m". | minor | Add the x-label "synthetic world"; write the ticks as "20s", "5m", "shallow 1m" | yes |
| 9 | Figure 5 legend | The episode-removal arm and its hatched band lack "(lab only)", though C and F have neither. Figure 4 has the qualifier. | minor | Add "(lab only)" to both entries | yes |
| 10 | all six figures | At the 880 px column, the smallest text lands at 10.8–11.2 px: the 11 pt labels on the Figure 1 y-axes, Figure 2's ROI ticks, note and lane text, Figure 3 panel F's ticks, and Figure 6's y-labels. Ticks are 11.7–12.2 px, against 16 px body text, and the ▼ off-view marks are about 6 px. | minor | Raise the base font to 14–15 pt or make the figures narrower (about 10 in); make the marks `ms` ≥ 8 | yes (computed; assumes the 880 px column) |
| 11 | Figures 3, 5 and 2 | Wasted space: 9% of Figure 3's height and 8% of Figure 5's sit blank below the legend, and Figure 2's row names leave about 100 placed px of empty gap. Whether the layout should use that room is agent 9's call. | minor | Shrink the legend rows' height ratio; reduce `labelpad` on Figure 2's row names | yes |
| 12 | `<darkroom>/…/results.json` | I only confirmed it comes from HEAD's measurement tool by mtime. I did not re-run the measurement. | info | Re-run the measurement tool if provenance matters for sign-off | no |

To rerun the checks: the rebuild is in `<scratchpad>/review3/r10/` and the crops are in `<scratchpad>/review3/r10/crops/`. The generator is `<worktree>/tools/make_slow_comodulation_figure.py` and the shipped figures are in `<worktree>/docs/learned/slow_comodulation/`.
