GRANT 10 MISMATCH: no tools missing; I hold Edit and Write, which no reviewer may have, plus PowerShell, Agent, Artifact, Skill, ToolSearch, mcp__claude_ai_Claude_Docs__batch/update/guide, and NotebookEdit as a deferred tool. **This is a finding about the run:** the role came in through a fallback path with editing tools. I did not use any editing tool on the repository. All scratch output is in <scratch>\mb\role10\.

# Role 10 (Ship It): Chapter 1, blob 14d63527

## Renders used
- **The docx.** pandoc 3.9 (pypandoc-binary, installed to scratch), `-f gfm -t docx --resource-path=.`, run from docs/dissertation, gave `...\role10\ch1.docx`. pandoc gave no warnings and all 19 images resolved.
- **The PDF.** Word COM exported the docx to `...\role10\ch1.pdf`: 57 pages, US Letter 612×792 pt, text block x 72–540 pt.
- **Figure crops.** Each placed figure was cropped from the PDF at 150 dpi to `...\role10\figs\fNN_pNN.png`, and zoom crops were taken from the source PNGs (`...\role10\z_*.png`).
- **Page geometry.** Measured from the PDF image boxes with PyMuPDF.
- **Page images.** 50 dpi pages are in `...\role10\pages\`, and the table pages are montaged in `tA.png`, `tB.png` and `tC.png`.

## Build-current gate

| item | result |
|---|---|
| **Shipped docx in Dropbox** (`darkroom/bugarach/dissertation/chapter-1/explainer_dissertation-chapter-1-analytical-baseline_20261113.docx`, 14:21:37) | **STALE: BLOCKER.** It is older than the md (15:48) and older than Figs 1.1–1.4 (15:32–15:35). It holds the earlier structure: its "Figure 1.1" is "What the first experiment found" and its "Figure 1.2" is "What one recording looks like". The Dropbox copy of chapter-1-aim0.md also differs from the blob. Every row below describes my fresh render of 14d63527, **not the file that is shipping**. Re-export before release. |
| Repo figures against their generators | **Current.** ch1_new_figures.py and ch1_intro_figures.py last changed at b1023ed4. The only change since fd1ace2d is to fig_schematic (Fig 1.4), and that figure was rebuilt at 15:35:53. The generators in learned/ (aim0_figures.py, aim1_figure.py, bound.py, split.py) are unchanged since their PNGs were committed. |

## Document properties

| check | result |
|---|---|
| core.xml (fresh render and shipped file alike) | **FAIL.** `dc:title` and `dc:creator` are empty. created/modified are stamped at the time of the conversion (OK). |
| app.xml | **FAIL.** It is inherited verbatim from pandoc's reference.docx: Words=83, Lines=12, Application "Microsoft Word 12.0.0", TotalTime 6. It describes the template, not this 57-page file. |
| PNG metadata | **FAIL (low).** Figs 1.1–1.3 give Author as `ch1_new_figures.py`, but ch1_intro_figures.py draws them (it reuses `save`/META). Fig 1.6 has Title "Figure 1, recovery against planted jitter (Aim 1a)", a stale number and aim. |
| File naming | **FAIL (low).** Fig 1.4's file name is dated `_20261029`, but the PNG was built 2026-11-13T15:35:53. The name misstates the build date. |

## Per-figure table
- **Placed box.** All figures are placed 420 pt (5.83 in) wide, left-aligned at x 72–492 pt. That is 90% of the 468 pt text block and 69% of the page width, with a 48 pt empty strip to the right of every figure.
- **"Text at placed size"** is the generator's smallest font × (5.83 in ÷ native width).
- **Shared-y** means: is the same measurement across panels on the same limits?

| Fig | render | page | rendered box (pt) / % page area | text at placed size | overlap / off-page | axes NAME+UNITS | shared-y | lettered | every mark identified | glyph / color | result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1.1 | f01_p2 | 2 | 420×389 / 34% | ≈5.3 pt (scale 0.53) | none | yes (time in m/s ticks; cell (of 33)) | yes | A–C | yes | ▼ planted | small text |
| 1.2 | f02_p6 | 6 | 420×504 / 44% | ≈5.3 pt | none | yes | C/D both 0–15 | A–D | Lane-A header "background … background 0.0096 Hz per cell" repeats the word and is pale gray, low contrast. The caption says "(top lane)", a spatial word for an unlettered lane. | ▼ found / missed / false call | minor |
| 1.3 | f03_p10 | 10 | 420×460 / 40% | ≈5.1 pt (0.507) | **FAIL.** In C the blue sharp curve crosses the legend text "half-width at half maximum". In C the "HWHM 0.80 s" label sits on the red dotted curve and markers. | yes | A/B yes | A–E | yes | | fix C |
| 1.4 | f04_p14 | 14 | 420×504 / 44% | **≈4.8 pt** (9 pt × 0.53) | none | yes | n/a | A–C (B's three matrices unlettered, named) | yes. Inside the figure, the key text uses spatial words ("right: … · below: …"). The caption says "row sums at right … column sums below". | | minor |
| 1.5 | f05_p16 | 16 | 420×552 / 48% | ≈5.6 pt | **FAIL.** The stacked labels "4" and "6" abut and read as "46" (D 1 s row and E). The "10" in C's 4 s row touches the right edge of the axes. | yes | D rows same scale | A–F (letters run A, B, C on the right column, then D–F) | yes | | fix labels |
| 1.6 | f06_p20 | 20 | 420×255 / 22% | **≈4.9 pt** (0.467) | none | yes | yes (checked zoomed) | A–H | yes | ▼ is "assessor K=…" style? No: squares and diamonds; consistent | small text |
| 1.7 | f07_p24 | 24 | 420×214 / 19% | ≈5.3 pt | none | yes | n/a | A–B | In B, the measured markers are colored light/mid/dark by cells per event, but the legend markers are black; the color key exists only through the line entries. | | minor |
| 1.8 | f08_p26 | 26 | 420×290 / 25% | ≈5.6 pt | none (the low points in E and F are inside the axes) | yes | yes | A–F | yes | ▼ = 5-cell measured (see the glyph row below) | ok |
| 1.9 | f09_p27 | 27 | 420×382 / 33% | ≈5.0 pt | none | yes | **FAIL.** A runs −0.13…0.10 and B runs −0.33…0.52 for the same quantity, and the difference is not marked. | A–B | Gray vertical category separators are not in the legend. | ● is used for both "10 cells" and "45 events" | fix y or mark it |
| 1.10 | f10_p28 | 28 (**caption on p29**) | 420×440 / 38% | ≈6.7 pt (larger; different style from the other 18) | none | yes | **FAIL.** A vs C (event rate) and B vs D (participants) are on different limits, unmarked. | A–D | **FAIL.** The legend uses the same thin gray line for "joins one measurement's two predictions" and for "measured = predicted". In the plot the joins are colored. A gray filled circle serves three meanings ("general-form (filled)", "fast stream", size key). Row headers sit above the plots, against the house "no titles" rule. | | fix legend; keep caption with figure |
| 1.11 | f11_p31 | 31 | 420×397 / 34% | ≈5.0 pt | In C the slow-stream at-bound points sit on the bottom spine and are half-clipped, while the fast-stream ones sit at the 0.05 tick. | yes | A/B yes | A–C | Panel titles sit above A and B. The purple circle means "A, B: joint fit" (large) and "C: hard-core form" (small): one color, two meanings. | | minor |
| 1.12 | f12_p33 | 33 | 420×269 / 23% | ≈5.8 pt | none | yes | n/a | single | yes | | ok |
| 1.13 | f13_p35 | 35 | 420×260 / 23% | ≈5.8 pt | none | yes | n/a | single | yes | ▼ = 95% upper bound (see the glyph row below) | ok |
| 1.14 | f14_p38 | 38 | 420×408 / 35% | ≈5.6 pt | none | yes | yes | A–D | yes | | ok |
| 1.15 | f15_p40 | 40 | 420×336 / 29% | ≈5.1 pt (0.486) | In A, the "2σ" label touches the end of the green line. B's "2σ" sits in the gutter between B and C, so its panel is ambiguous. In C the † daggers crowd together. | yes | A–C yes | A–D | **FAIL.** The 7.1 s, 3.8 s, 2.5 s and 0.1 s frame reference lines are labeled only at C's right margin and are repeated unlabeled in A and B. The open ▽ is not in the legend (the legend shows ▼ only). | ▼ = "resolves at every separation, axis floor" | fix labels |
| 1.16 | f16_p42 | 42 | 420×350 / 30% | ≈5.3 pt | none | yes | yes | A–H | yes. Two-line panel titles sit above each plot. | | small text |
| 1.17 | f17_p43 | 43 | 420×176 / 15% | ≈5.6 pt | none | yes | n/a (different quantities) | A–B | yes | | ok |
| 1.18 | f18_p45 | 45 | 420×207 / 18% | **≈4.7 pt** (0.449; native 13 in) | none | yes | yes | A–C | yes | | small text |
| 1.19 | f19_p46 | 46 | 420×200 / 17% | ≈5.8 pt | none | yes | yes | A–B | **FAIL (low).** The "power 0.8" and "test size 0.05" lines are labeled in B only and repeated unlabeled in A. The caption admits it. | r=1 and r=2.5 blues are close | minor |

## Cross-figure and whole-document checks

| check | result |
|---|---|
| **Placed text size** | **FAIL (major, all figures).** Generator fonts of 9–12 pt on canvases 10–13 in wide are scaled to 5.83 in, so text lands at about 4.7–5.8 pt against 11 pt body text. Worst are 1.18 (4.7 pt), 1.4 (4.8), 1.6 (4.9), 1.9 and 1.11 (5.0) and 1.15 (5.1). Fig 1.10 (about 6.7 pt) is the only one drawn at a near-print scale. |
| **Figure geometry** | All 19 figures are 90% of the text width and left-aligned, leaving 48 pt empty on the right. Whether the layout should give them the full block (or fewer, larger panels) is agent 9's call. |
| **One glyph per concept** (▼) | **FAIL (low/med).** ▼ carries five meanings across the chapter: planted event (1.1–1.5), detector verdict (1.2), "5 cells per event" (1.8), 95% upper bound (1.13), and "resolves at every separation tested" (1.15). |
| **Caption keep-with-figure** | **FAIL.** Fig 1.10 sits on p28 and its caption on p29. |
| **Tables** (9 rendered) | **FAIL (low).** All columns fit. Table 1.7 breaks after one row (p46→47) and Table 1.9 starts with one row at the bottom of p48. Header rows repeat. |
| **Hyperlinks** | **FAIL.** There are 10 relative links (`../learned/...`, `../goals/...`, `theory.py`) that are dead in a docx opened from Dropbox. |
| **Notation in the docx** | **FAIL (low/med).** The prose shows literal `g_n` (×6), `τ_min` (×6), `ν_c` (×5), `π_K` (×4), `λ_s` (×4) and `e^(−bw)` as raw text, and Table 1.2 mixes these with real subscripts (f₂, f₃). The figures set the same symbols as true subscripts (gₙ in Fig 1.7), so the text and figures disagree. |
| **Elements present** | All 19 images resolve and are placed, and each is followed by its caption. Every legend entry has a matching mark in the render. I spot-walked the legend entries against the renders; **I did not do a full walk of each generator's element list**, so this check is partial. |
| **Colorbars / overlay colors** | None in the chapter: not applicable. |
| **Histogram vertical-line rule** | Pass. Thresholds in 1.2 C/D and 1.5 E/F are horizontal; the σ markers in 1.5 B/C are horizontal arrows. |

## Findings list
Columns: location · issue · severity · suggested fix · could I verify it against a source.

1. **Dropbox docx.** The build is stale (pre-restructure, 14:21, older than md 15:48 and Figs 1.1–1.4). **Blocker.** Re-export from 14d63527 with pandoc and replace the file. Verified: yes.
2. **docx properties.** Title and creator are empty, and app.xml carries the template's stats (83 words, Word 12). Major. Set `title`/`author` metadata (`-M title=… -M author=…`) and use a reference.docx without stale app.xml, or stamp it after export. Verified: yes.
3. **All figures, placed text size.** Text is about 4.7–5.8 pt at placed size. Major. Redraw at a figure size near 6.5 in wide (or raise fonts so the placed size is at least 7 pt). Verified: yes (scale computed from px/dpi and placed EMU).
4. **Fig 1.3 C.** The curve crosses the legend text, and the "HWHM 0.80 s" label sits on the red curve. Major. Move the legend outside the peak and offset the label. Verified: yes.
5. **Fig 1.5 D/E.** The "4" and "6" labels abut and read as "46"; the "10" in C touches the axes edge. Major. Separate the labels or use "4 + 6". Verified: yes.
6. **Fig 1.9.** A and B use unmatched y-limits for the same measurement, with no marking. Minor/major. Share y, or mark the difference. Verified: yes.
7. **Fig 1.10.** Two identical gray-line legend entries; a gray circle with three meanings; the caption breaks onto the next page; the style differs from the rest; A/C and B/D are on unshared y-limits. Major. Give the join lines their own legend glyph (colored), split the key, and keep the caption with the figure. Verified: yes.
8. **Fig 1.15 A–C.** Reference lines are labeled only in C; open ▽ is not in the legend; "2σ" labels are placed ambiguously or touch lines. Minor. Label the lines per panel (or state that they apply to the row), add ▽ to the legend, and nudge the 2σ labels. Verified: yes.
9. **Fig 1.19 A.** The threshold lines are unlabeled (labeled only in B). Minor. Label them in A too. Verified: yes.
10. **Chapter-wide ▼.** One glyph for five concepts. Minor. Reserve ▼ for lane markers and use another glyph for the upper bound (1.13), the axis floor (1.15) and 5-cell (1.8). Verified: yes.
11. **Fig 1.11 C.** At-bound points are half-clipped on the bottom spine. Minor. Extend ylim, or draw the bound points with a distinct floor glyph. Verified: yes.
12. **Fig 1.2 and Fig 1.4.** Spatial words: "(top lane)"; "right: … below: …" inside the figure; "at right / below" in the caption. Minor. Name the lane and the sums instead. Verified: yes.
13. **Fig 1.2 lane-A header.** A duplicated, pale "background" label. Minor. Drop the left label or darken it. Verified: yes.
14. **docx hyperlinks.** 10 relative links are dead. Minor/major (they are visible to readers). Convert them to repository URLs, or unlink them to plain text. Verified: yes.
15. **docx notation.** Literal `_` and `^` subscripts in the prose and Table 1.2. Minor. Use Unicode subscripts or `~sub~` / TeX math in the source. Verified: yes.
16. **Tables 1.7 and 1.9.** Orphan rows at page breaks. Minor. Keep-with-next, or place a page break. Verified: yes.
17. **All figures, geometry.** 90% of the text width, left-aligned, 48 pt dead strip. Minor. Set width to 100% (`{width=100%}` is not available in gfm; use a reference doc or a Lua filter) and/or center. Verified: yes.
18. **PNG metadata and names.** Fig 1.1–1.3 Author names the wrong script; Fig 1.6 Title says "Figure 1 … (Aim 1a)"; Fig 1.4 file date 20261029 but built 11-13. Low. Pass META from ch1_intro_figures, retitle 1.6, rebuild the 1.4 name through `artifact_name.py build`. Verified: yes.
19. **Fig 1.7 B.** The marker color key exists only through the line entries. Low. Add colored marker swatches. Verified: yes.
