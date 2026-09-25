GRANT 10 ok — Read, Grep, Glob, Bash

## Build & craft gate — round 3 (blind), final-parameters report

Artifact: `<worktree>/docs/learned/runs/2026-09-25-final-parameters/README.md` (worktree `floor-and-grids`, HEAD `0638de5`, tree clean apart from the untracked round3 review folder).

### Build currency and darkroom parity
- **The build is current.** The generator `tools/make_final_parameters_report.py` was modified at 03:47:02. Built from it: `figure1` at 03:52:46, `figure2` at 03:52:47, `adoption.json` and `adoption_table.md` at 03:52:46, and `README.md` at 03:53:18. The commit `0638de5` is at 03:53:29.
- **Figures 3 and 4 were supplied by WSMIP065.** They are byte-identical (md5) to their sources at `<darkroom>/bugarach/2026-09-25-final-parameters/065/report-inputs/`, and no newer copy exists anywhere under the night folder.
- **The darkroom copy matches the repo copy.** All 7 files in `<darkroom>/bugarach/2026-09-25-final-parameters/report/` (the README, `adoption.json`, `adoption_table.md` and the four PNGs) have the same md5 as the repo copies.

### Markdown render
| check | result |
|---|---|
| Tables well-formed | 10 tables at lines 27, 49, 75, 155, 208, 241, 360, 392, 438 and 522. Every row in each table has the same column count as its header (3, 6, 4, 5, 3, 4, 9, 6, 4, 4). The table nested in the list item at line 75 is indented 2 spaces, so it renders inside the bullet. |
| Generated-table markers filled | All three are filled: adoption-table (26 lines), budget-table (40) and floor-table (8). Each block appears verbatim in `adoption_table.md`. |
| Image links | All 4 `figureN_*.png` resolve. |
| Relative links | `../../../handoffs/2026-09-25-overnight-final-parameters.md`, ADR-0008 and ADR-0009 all resolve. The tools named in the text exist: `probe_bench_floor`, `final_parameters_review_checks`, `detect_with_floors`, `search_all_settings` and `train_learned_on_bench`. |
| PNG properties | All four carry only `Software: Matplotlib 3.11.2`, with no inherited author or date. DPI is 160 for Figures 1–2 and 150 for Figures 3–4. |

### Per-figure table (each row checked against the PNG named, viewed at full size)
| figure | render | size (px) | est. rendered width in a GitHub column (~1012 px) | overlaps / clipping | axes: name + units | legend / colour key | panel letters | shared limits |
|---|---|---|---|---|---|---|---|---|
| 1 | figure1_fresh_f1.png | 2080×736 | ~49%, so tick text ≈ 9 px | none | x: "<stream> · mean F1, fresh seeds" (F1 has no unit) | complete; all glyphs and lines are legended | none (streams named in the x labels) | x 0.60–0.90 on all three panels, shared |
| 2 | figure2_cross_stream.png | 2240×1056 | ~45%, cell text ≈ 10 px | none. The y-labels of columns 2–4 sit about 28 px from the neighbouring panel but do not touch it. | "scored on (bench)", "<det> · tuned on" | colorbar 0.6–0.9. The smallest rendered value is 0.67, so nothing falls outside the bar. | none | one colour scale |
| 3 | figure3_elevated_rate.png | 2250×1230 | ~45%, tick and legend text ≈ 6–7 px | none. Rotated x ticks are clear of each other. | calls per minute and calls per hour, symlog noted | complete (shape, fill, colour, budget line) | none; uses "top"/"bottom" | y shared along each row |
| 4 | figure4_bench_floors.png | 2100×840 | ~48%, bar count labels ≈ 5 px | none | left y "floor, co-active ROIs (range over 8 seeds)", **left x has no axis name**; right y "% of events at that level", x "participants per planted event" | complete; group headers are set in their own colours | none; caption says "Right:" | n/a |

Every number in the text that I could read off a figure agrees with it. In Figure 2: 0.87 against 0.83, and 0.79 against 0.76. In Figure 3: slow locust 7.2 / 4.35 against the limit of 4, and combined rate+context busy proposal ≈1.35 per hour against 1. In Figure 4: 25/40, 20/40, 15/40, the elevated-rate floors of 16–20, and the offsets of about +1 and +3 ROI. Nothing is drawn on a raster: there are no rasters on the page.

### Findings
| # | location | issue | severity | fix | verified against source |
|---|---|---|---|---|---|
| 1 | Figures 3 and 4 at page width | At GitHub's column width (~45–48% of native size) the small text drops to about 5–7 px: Figure 3's tick labels, legend and caption, and Figure 4's "40/40" bar labels. Cold readers will not be able to read them without clicking through. | major | Enlarge the fonts or reduce the canvas width. In Figure 4, set the n/N labels at body size. | yes (px measured) |
| 2 | Figure 3, detector chorus_norm on slow (top row) | Table 2 marks slow chorus_norm as **fail: elevated-rate, inside the stretch (CoactDetect's limits)**. The figure draws no budget line for chorus, and its caption says chorus "has no budget of its own". The failure is invisible in the figure: the markers sit at ≈1.4 and ≈1.1 with no line at 1. | major | Draw CoactDetect's limit on the chorus columns (dashed, legended "CoactDetect's limit"), or change the caption. | yes |
| 3 | Figure 3, legend and embedded caption; Figure 4 caption "Right:" | Spatial words ("top row / bottom row", "top", "bottom", "Right:") are used instead of panel letters. No figure on the page letters its panels. | minor | Letter the panels A/B (Figure 1: A–C) and refer to them by letter. | yes |
| 4 | Figure 3 x ticks | The detector is labelled "SCE", while Figures 1–2 and all tables say "binned SCE". | minor | Rename it "binned SCE". | yes |
| 5 | Figure 4, left panel | The x axis has no name (only the tick labels fast/slow/combined). | minor | Label the axis "stream". | yes |
| 6 | Figure 4, left panel, elevated-rate glyph | A dotted range capped with a ▼ reads as "the value is the triangle". It is not clear whether the triangle marks the top of the 8-seed range or a single value. | minor | Say so in the legend ("range over 8 seeds; ▼ marks the maximum"), or use the same bar glyph as the other recording kinds. | yes |
| 7 | Figures 1–2 compared with 3–4 | Figures 3 and 4 carry an embedded "Figure N." caption and Figures 1 and 2 do not. The resolutions also differ (160 dpi against 150 dpi). | minor | Make them consistent: add embedded captions to Figures 1 and 2, or strip them from 3 and 4. | yes |
| 8 | Figure 3, colour key | CoactDetect (dark blue) and SCE (sky blue) are a low-contrast pair. The legend markers for shipped/proposal are near-black, the same as the locust colour. | minor | Give the shape legend entries a neutral gray outline so they are not read as locust. The detector columns already tell CoactDetect and SCE apart by position, so that pair only needs checking, not necessarily changing. | yes |
| 9 | README line 383 (generated Table 1) | "5 frames → 1 frames". | minor | Singularize units in the generator. | yes |
| 10 | README lines 466–469 | "OVX +17; MALE +1; ORX +20" have no unit; only DI says "ROI". | minor | Write "+17 ROIs" and so on. | yes |
| 11 | README Decision 7 compared with Table 1 | The same values are written in two formats: "1e-4 → 1.4e-9" in the text against `0.0001 → 1.4e-09` in the table. | minor | Use one format. | yes |

No blocking findings: the build is current, the darkroom copy matches, the markdown renders, every link resolves, and no element the text refers to is missing from a render.
