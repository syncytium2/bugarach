<!-- Verbatim role report, except that this machine's absolute paths are written as %USERPROFILE% and <darkroom> (the repository is public). The unedited original is in <darkroom>/bugarach/2026-09-18-fair-comparison-run/report/review-roles-round3/. -->

GRANT 10 ok — Read, Grep, Glob, Bash

**Role 10 (Ship It), round 3, blind pass.** I reviewed the built artifact at hash `5c0ccbb` (the repo copy and the darkroom `index.html` have the same hash). I opened no review record and no run record.

The build is current, nothing runs off the page at either width, and every element the generator draws is present in the render. No finding is high severity. Three are medium: a glyph used two ways across figures 7, 8, 10 and 12; crossing leader lines in Figure 9B; and at phone width the data figures open on labels only, a limitation the page never states.

## Build currency — PASS
- **Rebuild matches:** I rebuilt from the worktree HEAD `6eb9b29` into the scratch folder. Apart from the build timestamp (10:07 against 10:03) and the version stamp (`0.1.0+g6eb9b29` against `+g69480a7`), the rebuild is identical to the shipped file. `6eb9b29` is the rebuild commit, so the stamp difference is expected.
- **Timestamps:** `report.html` was written at 10:03:36. That is later than everything it depends on:
  - the generator, 10:01:01
  - `tools/fair_comparison_evidence.py`, 10:00:57
  - the newest input, `replicate_summary.json`, 10:01:14
  - `build_surrogate_report.py`, 07:58
  - the `src/bugarach` modules it imports, 07:58
- **No input newer than the build:** `find -newer report.html` in the run folder returns nothing.
- **`comparison.svg`:** it is named in the text as living on PR #660 and is not embedded, so it is not an input.

## Render table
Renders are at 1100 px and 400 px viewports, with 3× zoom crops where noted. The column is 980 px wide at 1100 and the scroll container is 368 px wide at 400. Every figure is an intrinsic 900 px wide: 91.8% of the column at 1100, and 41% visible at 400 (it scrolls inside its container; the page itself never scrolls sideways, `scrollWidth` = viewport at both widths). The smallest rendered text is 11 px everywhere. "Text collisions" counts text boxes that overlap by more than a hairline; the measurement also flagged 1 px line-box touches between stacked caption lines in Figures 1 and 2, which I checked visually and do not count.

| Item | Checked against | Rendered box | Text collisions / off-edge | Axes (name + unit) | Marks identified | Result |
|---|---|---|---|---|---|---|
| Fig 1 | `fig01_1100.png`, `z1_tri.png` | 900×700 | 0 / 0 | time "0s…40m", "16m…26m" (minutes-friendly), ROI rows labeled | legend in A; lanes labeled in B; raster black only, cues in down-triangle lanes above | pass |
| Fig 2 | `fig02_1100.png` | 900×330 | 0 / 0 | schematic, "2.5 s" | legend covers triangle, bar, bracket, hatch | pass |
| Fig 3 | `fig03_1100.png` | 900×250 | 0 / 0 | n/a (layout) | cells self-labeled | pass |
| Fig 4 | `fig04_1100.png` | 900×450 | 0 / 0 | seed ranges labeled | legend covers all 4 fills | pass |
| Fig 5 | `fig05_1100.png`, `z5_bottom.png` | 900×330 | 0 / 1 (axis label 1 px past the bottom edge, visually intact) | "8s…12s" | row labels | minor (F7, F9) |
| Fig 6 | `fig06_1100.png` | 900×330 | 0 / 0 | both named; schematic, no ticks | square, rings and budget line labeled | pass (F11) |
| Fig 7 | `fig07_1100.png`, `z7_B.png`, `fig07_400.png` | 900×560 | 0 / 0 | "held-out F1", both panels 0.2–0.85, shared | legend covers dot, bar, hollow, × | F1, F6 |
| Fig 8 | `fig08_1100.png`, `z8_top.png` | 900×514 | 0 / 0 | named, "(right of 0: the net is ahead)" | legend covers all glyphs | pass (it is the reference convention for F1) |
| Fig 9 | `fig09_1100.png`, `z9_right.png` | 900×600 | 0 / 0 | "held-out F1"; gap in s, spacing noted as not to scale | direct labels plus ring legend | F2, F4 |
| Fig 10 | `fig10_1100.png` | 900×360 | 0 / 0 | named, panels share −0.20…+0.05 | no on-figure key | F1, F5 |
| Fig 11 | `fig11_1100.png` | 900×312 | 0 / 0 | named, panels share 0–1 | caption only | F5 |
| Fig 12 | `fig12_1100.png` | 900×330 | 0 / 0 | named, "(right of 0: tuning helped)" | caption only | F1, F5 |
| Table 1 | `tab1_1100.png`, `tab1_400.png` | 980 at 1100; 604 in 368 at 400 (scrolls) | none | n/a | n/a | pass |
| Table 2 | `tab2_1100.png` | 980 at 1100; 477 in 368 at 400 | none | F1 is unitless | n/a | pass; mean values match the Fig 7 bars |
| Table 3 | `tab3_1100.png` | 980 at 1100; 638 in 368 at 400 | none | n/a | n/a | pass |
| Page at 400 px | `full_400.png`, DOM overflow scan | page width = 400 | 0 elements outside the viewport except inside scroll containers | — | — | F3 |
| Metadata | `<meta>` tags | — | — | — | — | F10 |

Other checks, all clean:
- **Panel references:** panels are lettered, and no text refers to a panel by spatial words. "Upper/lower line" in the Figure 8 caption means sub-rows, and a legend backs it.
- **Figure references:** all 12 figures are numbered and each is referenced 4 or more times.
- **Shared scales:** multi-panel figures share their x-limits.
- **Histograms:** there are none, so there are no annotation bars on one.
- **Colours:** blue against black and blue against orange-red contrast clearly.
- **Accessibility:** every scroll container has `tabindex=0`, `role=region` and an `aria-label` ("Figure N, scrollable"), and every SVG has `role=img` and a label.

## Findings

**F1. Figures 7, 8, 10, 12: one glyph means different things (medium, verified yes).**
- **Issue:** In Figure 8, a fold holding a refit below 0.2 F1 is drawn hollow at its counted value, and "filled" means that refit set aside. Figures 7, 10 and 12 draw the same folds filled at the counted value. Examples:
  - chorus_gain_norm, F1 alone, is at −0.153: hollow in Figure 8 but filled in Figure 10A.
  - The two −0.128 outliers in Figure 12 are the same two folds.
  - A reader carrying Figure 8's key reads them as the set-aside value.
- **Also:** a hollow circle means "fails the crowded-recording check" in Figure 7 but "counted with the failed refit" in Figure 8.
- **Evidence:** generator lines 618, 671–673, 813 and 872.
- **Fix:** mark failed-refit folds the same way in every figure (Figure 8's style or a separate glyph), and give the crowded-check failure a glyph that is not a hollow circle.

**F2. Figure 9B: leader lines cross (medium, verified yes).**
- **Issue:** chorus_norm's leader runs from its 16 s end (about 0.775) to the third label. On the way it crosses the CoactDetect and LoCo curves and passes through the ring at 30 s, and it then crosses binned SCE's leader. Which label belongs to which curve is ambiguous in exactly the cluster where they matter.
- **Cause:** lines 768–775 order the labels by their end y only, but the curves end at different x (16 s for the nets, 30 s for the coded detectors).
- **Fix:** end each leader at a common x, or order the labels by the y where each leader reaches the label column. Alternatively, label the net curves at their 16 s ends.

**F3. Phone width: data figures open on labels only, and the promised disclosure is missing (medium, verified yes).**
- **Issue:** at 400 px only 41% of each figure is visible. Figures 7, 8, 10, 11 and 12 open showing row labels and the start of the axis, with no data at all (see `fig07_400.png`).
- **Disclosure gap:** the CSS comment says this cost is "recorded in the report's residual flags". Section 11 (Limits) has no such entry, and the page never mentions scrolling.
- **Fix:** add the limit to section 11, or a visible "scroll →" cue. Alternatively, at narrow widths, stack panels vertically or move the row labels.

**F4. Figure 9B: ring markers not fully keyed (low, verified yes).**
- **Issue:** the rings come in two radii, 6 px and 10 px. The size only encodes that two rings were stacked at 8 s, but reads as a quantity. The rings take the detector's ink (black or gray), while the legend shows one black 6 px ring.
- **Fix:** use the same radius and offset stacked rings, or say in the legend that the ring colour follows the curve.

**F5. Figures 10, 11, 12: no on-figure key (low, verified yes).**
- **Issue:** the dot (one fold), the bar (mean of 4), the dashed zero line and the dotted group separator are explained only in the captions. Figures 7 and 8 carry legends.
- **Fix:** add the same legend line Figures 7 and 8 use.

**F6. Figure 7B, locust row (low, verified yes).**
- **Issue:** the four × marks pile into one tangle, so "four folds are always four marks" does not hold visually. A mean bar is also drawn for a row that Table 2 reports as "—", since the budget refused every setting.
- **Fix:** spread the × marks by fold, as the circles are, and drop the mean bar for refused rows.

**F7. Figure 5: counts without a unit (low, verified yes).**
- **Issue:** the bin counts "0 / 3 / 3 / 0" and "6", and the notes "most in a bin: 3" and "most in a window: 6", carry no unit. The house rule is that every number carries its unit.
- **Fix:** "3 firings", or a row label such as "firings per bin".

**F8. Figures 1, 4, 5, 9: panel headings are titles (low, verified yes; adjudicate).**
- **Issue:** examples are "A. The whole recording", "A. Before the fix: consecutive order", "A. As recorded", and in Figure 9 "B. Held-out F1 with only the merge gap changed (mean of 4 outer folds, choices on F1 alone)". CLAUDE.md asks for no titles above plots, and the brief says panel letters only.
- **Fix:** move the descriptive text into the caption and keep the letter, or shorten to a short tag. Figure 9B's heading most needs it.

**F9. Figure 5: axis label past the SVG edge (low, verified yes).**
- **Issue:** the text box of "time (a schematic)" ends 1 px below the SVG bottom, so the glyph descenders sit on the clip edge. It is visually intact in the 3× crop.
- **Fix:** add 4 px to the SVG height.

**F10. Metadata: no author (low, verified yes).**
- **Issue:** the title, description, date (2026-09-19) and generator all name this page, not the template it was built from. There is no author.
- **Fix:** add `<meta name="author">`.

**F11. Figure 6: caption and axis name the x quantity differently (low, verified yes).**
- **Issue:** the caption calls it "its firing rate on the training recordings"; the axis says "false alarms per hour on the training recordings".
- **Fix:** use one name for the quantity.

## Files
Everything is in `%USERPROFILE%\AppData\Local\Temp\claude\c--Users-<user>-bugarach-bugarach\0c979457-501e-4b3d-9c4b-21e394823cf5\scratchpad\mb\r3-role-10\`:
- renders `fig01–12_{1100,400}.png`, `tab1–3_{1100,400}.png`, `full_{1100,400}.png`
- zoom crops `z1_tri.png`, `z5_bottom.png`, `z7_B.png`, `z8_top.png`, `z9_right.png`
- geometry `geom_{1100,400}.json`
- the scratch rebuild `build\index.html`

I edited nothing.
