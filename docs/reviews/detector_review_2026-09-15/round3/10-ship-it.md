> **Public copy.** Lines that concern real treatment recordings are removed (11 here), per FOUNDATIONS §5, and machine paths are shortened to `<scratchpad>`, `<worktree>`, `<darkroom>` or `<home>` (sapper SAP004). Everything else is verbatim.

GRANT 10 ok — Read, Grep, Glob, Bash

# Role 10, Ship It: round 3 blind pass on `detector_review.html`

**Verdict:** nothing blocks, two major defects, fourteen minor. The build is current. I rendered the page in Playwright Chromium at 1280px and 400px and looked at every figure PNG at full size, cropping where detail mattered.

One note on the run, not the artifact: a project hook (`no-heredoc-source.sh`) blocked my first two render scripts. The first matched a `.py` redirect, the second matched `write_text`. I re-ran the same inspection as a Python script fed through stdin that only prints JSON and saves screenshots. No project file was touched.

All evidence is in `<scratchpad>\mb_scratch\role10_r3\`. File names below are relative to that folder: `page_1280.png`, `page_400.png`, `render.json`, `table*_{1280,400}*.png`, `figure{1,9,13}_{1280,400}.png`, `crop_*.png`.

## Build currency: pass
- **Generator:** `make_detector_review.py` last changed 12:52:27 and the template 12:59:46. Both are in commit 699de8e (13:06:33), and the worktree is clean.
- [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder]
- **Figures:** all 18 were rebuilt between 13:01:44 and 13:04:01, which matches `rebuild_r3.log`, every stage.
- **Page:** written 13:07:16, after every input and after the commit. The page's build line says "Built 2026-09-15 from commit 699de8e".
- **Caveat (minor):** the log's last entry is `stage page` at 13:04:02. The 13:07 restamp is not in any log, so nothing on disk shows that the restamp changed only the stamp.
- **Images:** the 18 images embedded in the page are byte-identical to `_work\fig*.png` and to the copies beside the page, in the same order (sha256 compared).

## Page-level checks
| check | 1280px | 400px |
|---|---|---|
| horizontal page scroll (scrollWidth vs clientWidth) | none (1280/1280) | none (400/400) |
| elements running off the page, outside scroll boxes | 0 | 0 |
| images loaded (complete, natural 2360px wide) | 18/18 | 18/18 |
| console / page errors | none | none |
| doctype, `lang="en"`, `<title>`, viewport meta (zoom allowed) | pass | pass |
| `alt` on every image | 18/18, 42–650 characters | same |
| `#` anchors resolve / duplicate IDs | 12/12 / none | same |
| unclosed or stray tags | none | none |
| unfilled `{{…}}` or `PROSE:` tokens | none | none |
| nan / None / null / undefined | none (the 3 hits for "none" are ordinary English) | none |
| mojibake | none | none |
| British spellings (colour, grey, analyse, centre, modell-, -ise…) | none ("analyze" and "analysis" are American) | none |
| thousands separators in numbers | consistent | consistent |
| text under 12px | none | none |
| caption-to-image gap | 8px on all 18 | 8px |
| [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder] |
| sticky first column | only Table 3; see M2 | see M2 |

## Per-figure table (rendered box measured off the render)
The page column is 1180 CSS px. At 1280px every figure renders **1182 px wide (92% of the viewport)**; at 400px every figure renders **370 px wide (92.5%)**. Heights are listed per figure.

| fig | render checked | box @1280 (w×h) | box @400 | clipped / overlapping text | legend over data | marks on raster | up-pointing markers | shared y-limits | notes |
|---|---|---|---|---|---|---|---|---|---|
| 1 | fig01_problem.png, figure1_1280.png | 1182×721 | 370×226 | none | no | none | none | n/a | clean |
| 2 | fig02_surrogates.png, crop_fig02_B/Dright | 1182×1784 | 370×558 | none | no | none (busy-block shading stays in the lane) | none | B1 and B2 both 1e-6 to 1 | m1, m8 |
| 3 | fig03_rate.png, crop_fig03_Blane | 1182×535 | 370×168 | × glyph touches call tick | no | none | none | A and B both 0–14 | m2, m13 |
| 4 | fig04_coact.png | 1182×535 | 370×168 | surrogate dot sits on the histogram step in A | no | none | none | 0–14 | m12, m13 |
| 5 | fig05_loco.png | 1182×535 | 370×168 | none | no | none | none | 0–14 | m13 |
| 6 | fig06_sce.png | 1182×535 | 370×168 | × row touches call blocks in B | no | none | none | shared | m2, m13 |
| 7 | fig07_cicada.png | 1182×535 | 370×168 | × glyphs fuse in B (4 places) | no | none | none | 0–14 | m2 |
| 8 | fig08_sync.png | 1182×695 | 370×218 | none | no | none | none | shared | the bar-crossing frame in B with no call is explained in the caption |
| 9 | fig09_learned.png, crop_fig09_Clane | 1182×1223 | 370×383 | × sits between rows in C | no | none | none | A: all ±1; B/C shared | m2, m6 |
| 10 | fig10_generator.png, crop_fig10_C/D/A1lane | 1182×1105 | 370×346 | ▽ collides with ▼ in A1/A2 | **yes, panel C** | none | none | n/a | M1, m3, m8 |
| 11 | fig11_grading.png | 1182×398 | 370×125 | none | no | n/a | none | n/a | m4 |
| 12 | fig12_settings.png | 1182×523 | 370×164 | markers stack (by design) | no | n/a | n/a | all 0–1 | m5 |
| 13 | fig13_performance.png, figure13_400.png | 1182×1116 | 370×349 | none | no | n/a | n/a | A1/A2 and C1/C2 both 0–1 | m5 |
| 14 | fig14_blockrecall.png | 1182×762 | 370×239 | chance bars hidden under dots | no | n/a | n/a | A/B/C shared | m12 |
| [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder] |
| [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder] |
| [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder] |
| [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder] |

On the raster rule, all 18 pass: nothing is drawn on any raster, and every direction marker is a ▼ in a lane above its raster.

## Findings

### Blocking
None.

### Major
**M1. Figure 10, panel C: the legend box covers data.** The semi-transparent legend (top-left, reaching about 0.1–0.25 on y and 0.1–30 mHz on x) sits over the orange "flat" histogram: the step up from 0.13 to 0.20, the 0.20 plateau, and the start of the rise to the 0.24 peak are faded behind it. Those are the main feature of the "flat" curve.
- Evidence: `crop_fig10_C.png`.
- Fix: move the legend out of the plot area (above panel C, as panels B and D do elsewhere), or put it top-right, where only the flat tail runs, and make it opaque.

**M2. Table 3 at 400px: a sticky header cell lands over the detector column.** The rule `table.perf th:first-child{position:sticky;left:0}` also matches the first cell of the *second* header row ("average", under "F1 score, quiet level"). When the table is scrolled sideways, that cell slides left and pins above the detector names, so the detector column reads "detector / average", and the group header beside it is cut to "uiet level (0–1)". At 1280px there is no scroll, so this does not show.
- Evidence: `table3_400_scrolled.png`.
- Fix: make only the rowspan "detector" header cell and `tbody td:first-child` sticky. For example, put a class on those cells instead of using `th:first-child`.

### Minor
**m1. Figure 2, panel C heading says "(left pair fast stream, right pair slow)".** Each stream has three bars, not a pair, and the phrase uses spatial words. The category labels already say fast and slow.
- Fix: drop the parenthetical.

**m2. False-alarm × glyphs in the lanes are about 5 CSS px**, far smaller than the × in the legend.
- In Figures 3B and 6B they sit touching the tops of the call ticks.
- In Figure 7B, four pairs fuse into single blots, so the "15 calls" count cannot be checked by eye.
- In Figure 9C, the tube-guard × marks float halfway toward the tube row, so which row they belong to is unclear.
- Fix: a larger glyph with a fixed offset above its own row.
- Evidence: `crop_fig03_Blane.png`, `crop_fig09_Clane.png`.

**m3. Figure 10, A1 and A2 lanes: decoy ▽ collides with planted ▼**, near 2 min in A1 and at several points in A2. Two decoys also fuse near 4 min in A1.
- Fix: give decoys their own lane row.
- Evidence: `crop_fig10_A1lane.png`.

**m4. Figure 11, panel A: the green ±2.5 s bands are identified only in the caption.** Nothing on the figure explains them.
- Fix: add a swatch to the legend, e.g. "green: within 2.5 s of a planted event".

**m5. Figures 12 and 13, labeling and layout:**
- Figure 12's six panels have no letters; they are told apart by y-axis labels, and the caption says "its panel".
- In each row of Figure 12, the x-axis titles sit at different heights, because the rotated tick labels differ in length.
- Figure 12's legend glyphs (outlined square and circle) are about a third the size of the marks in the plots.
- [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder]
- Figure 13B keeps empty "trace" and "tiny" columns on its axis (the caption explains why). Drop them or mark them "n/a" on the figure.

**m6. Figure 9, panel A: labeling:**
- The y-axes are labeled with the model name only; the quantity ("filter weight, scaled to own peak") appears only in the legend line.
- The color key "colored: the four center filters…" is plain gray text, not set in the model colors.
- All four sub-panels carry the same letter A.

*[line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder]
- Ten lane rows at about 11 CSS px pitch with about 12px labels, so neighboring labels touch.
- The tube, tube-guard and SPIKE-synch reds are nearly indistinguishable at tick width, and tube-ratio-guard's pale yellow barely shows on white. Rows are labeled, so the colors are redundant, but they read as noise.
- The group panels are not lettered.
- Evidence: `crop_fig15_lanes.png`, `crop_fig16_lane_colors.png`.

**m8. Singular "ROI" in raster labels:** Figure 2D and Figure 10 A1/A2/B say "simulated · 33 ROI". Every other figure says "ROIs".

*[line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder]

**m10. At 400px, figure text shrinks to about 31% (roughly 3–4 CSS px).** The page says "Tap or click any figure to open it at full size". The tap links are relative (`fig01_problem.png`…), so they work only if the 18 PNGs ship beside the HTML. They do in the review folder. They will 404 if the self-contained 5.4 MB HTML is delivered alone.
- Fix: confirm the PNGs are copied wherever the page goes, or open the embedded image in a new tab instead.

**m11. Tables 1 and 4 at 400px scroll sideways without a sticky first column.** Table 4 renders about 3,300 px tall, with "weak at" off-screen.
- Evidence: `table1_400.png`, `table4_400.png`.

**m12. Marks hide each other:**
- [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder]
- Figure 4A: the surrogate-average dot sits on the teal histogram step.

**m13. The shared legend in Figures 3–8 lists glyphs a given figure never draws.** Examples: "second call on an event already found" in Figures 3–6 and 8; "planted event, found" in 6 and 8.

**m14. Table 3's caption says "A red cell".** The flagged cells are pale pink (#fbe3e1) and bold.
- Fix: say "pink", or use a stronger fill.

## Checked and clean
- No horizontal page scroll at either width.
- No figure text clipped at the canvas edges. The Figure 2D ▼ at 30 min sits inside the frame (`crop_fig02_Dright.png`).
- Every axis has a name, with units or a 0–1 range, except m6.
- Panels are lettered and prose references resolve, except the unlettered panels in m5 and m7.
- Shared y-limits hold in every multi-panel figure.
- No vertical annotation lines on histograms.
- Planted / found / missed glyphs are consistent across figures: black ▼ for planted with no verdict, green or red ▼ for the verdict.
- [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder]
- No colorbars are used.
- Document properties: the page title is set and the build line names the commit and date; there is no template metadata to inherit.
