GRANT 10 MISMATCH — missing none; holds Edit, Write, NotebookEdit (deferred), PowerShell, Agent, Artifact, Skill, ToolSearch, SendMessage (deferred), Claude Docs MCP update/batch tools

(Run note for the ledger: the review went through a fallback path, so I held tools beyond my grant. I used only Read, Grep, Glob and Bash. I edited nothing in the repository. Every scratch file is under <scratch>/mb2/role10/. I did not open docs/reviews/.)

# Role 10 — Build & craft gate ("Ship It"): Chapter 1, blob 0acfccbb

## What I built and checked against
- **Artifact:** `<repo>/docs/dissertation/chapter-1-aim0.md`. `git hash-object` gives 0acfccbbeab6…, which matches the brief. The working tree is clean apart from an untracked reviews folder and `uv.lock`.
- **docx:** built with pandoc 3.9 (pypandoc-binary 1.17) using `-f gfm -t docx --resource-path=.`, run from docs/dissertation/. It finished with no warnings, so all 19 images resolved. The file is `<scratch>/mb2/role10/ch1.docx`.
- **Render:** Word (COM) saved the docx as `ch1.pdf`: 59 pages, Letter size, 1 in margins. I rasterized every page at 110 dpi to `pages/pNN.png` and made contact sheets `sheet1-6.png`. I measured image boxes from the PDF with PyMuPDF.
- **Figures:** I opened every source PNG at full resolution. Zoom-crops of each suspected collision are saved as `c2a…c15a.png`.
- **docx contents:** 9 tables and 19 images, all present and in numeric order.
- **Leaked markup:** none in the rendered PDF text. I searched for `$`, backslashes, `<sup>`, `<br>`, `&lt;`, `**`, `__`, `[^`, `](` and U+FFFD.

## Build currency: PASS
Every figure is newer than both its generator and every data input it reads:
- **Fig 1.3:** `ch1_new_figures.py` was last saved 17:33:01 and the PNG at 17:33:07.
- **Figs 1.1, 1.2, 1.4:** built 16:50 to 17:16, after `ch1_intro_figures.py` (16:49:48).
- **Oct-29 builds (1.7, 1.9 to 1.14, 1.19):** the only generator changes since 2026-10-29 are in `_stack` (used only by `fig_data`, i.e. Fig 1.3) and a function rename in `fig_schematic` (Fig 1.5, rebuilt 15:35). These figures are not affected.
- **Inputs:** all `ch1_followups/*.json` and separation JSONs date from Oct 29 and are older than their PNGs. The figures in `learned/` (1.6, 1.8, 1.15 to 1.18) are newer than `aim0_figures.py`, `aim1_figure.py`, `bound.py` and `split.py`. `aim1_lab_regime.json` changed on Nov 13, but no figure reads it.

## Document properties: FAIL
- The docx core properties have `dc:title` and `dc:creator` empty. Created and modified are both the build time. Nothing names this chapter or its author.
- The embedded PNG "Title" metadata on six figures in `learned/` names a different document's numbering: "Figure 1, … (Aim 1a)", "Figure 2…", "Figure 3…", "Figure 4…", "Figure 5…" and "Figure 6…". In this chapter they are Figures 1.6, 1.8, 1.17, 1.18, 1.16 and 1.15.
- Two files carry a stale date in their name: `…data-and-what-each-tool-sees_20261029.png` and `…surrogate-nulls-and-order-schematic_20261029.png` were regenerated on 2026-11-13. The date is fixed in the generator's name call.

## Per-figure table
Every placed figure is 5.83 in wide, left-aligned at x = 1.00 in, on a 6.5 in text block and 8.5 in page. That is 69 % of page width and 90 % of the text block, with 0.67 in unused to the right. "Text pt" is the generator's base font size multiplied by the placement scale.

| Fig | Checked against | Page / rendered box (in) / % page area | Text pt as printed | Result |
|---|---|---|---|---|
| 1.1 | source PNG + p02 render | p2, 5.83×6.16, 38 % | ~8 | Clean: axes named, panels A–C, legend lane labeled |
| 1.2 | PNG + crops c2a–c2d + p06 | p6, 5.83×7.57, 47 % | ~7–8 | 3 minor findings (rows 1–3) |
| 1.3 | PNG + p10 | p10, 5.83×7.67, 48 % (alone on page; caption spills to p11) | ~6 (12 pt × 0.56); bar numbers ~5.9 | 3 findings (rows 4–6) |
| 1.4 | PNG + crops c4a, c4b + p12 | p12, 5.83×7.37, 46 % | ~7.7 | **2 overlaps** (rows 7–8) |
| 1.5 | PNG + p16 | p16, 5.83×7.00, 44 % | ~6.4; key ~5.3 | 1 finding (row 9). Schematic arithmetic in B and C checks out |
| 1.6 | PNG + p19 | p19, 5.83×3.55, 22 % | **~5.6; "markers dodged" ~4.7** | Rows 10, 25 |
| 1.7 | PNG + crops c7a, c7b + p26 | p26, 5.83×2.97, 19 % | ~6.4 | **1 overlap** (row 11), row 12 |
| 1.8 | PNG + p27 | p27, 5.83×4.03, 25 % | ~6.4; off-scale notes ~5 | Row 13 |
| 1.9 | PNG + p28 | p28, 5.83×5.30, 33 % | ~6.4 | Rows 14–16 |
| 1.10 | PNG + crops c10a, c10b + p30 | p30, 5.83×6.11, 38 % | ~6.7 | **1 overlap** (row 17), rows 18–19 |
| 1.11 | PNG + crop c11a + p33 | p33, 5.83×5.51, 34 % | ~6.4 | Rows 20–21 |
| 1.12 | PNG + p35 | p35, 5.83×3.73, 23 % | ~7 | Clean: half-filled glyph legended, callouts colored |
| 1.13 | PNG + p37 | p37, 5.83×3.62, 23 % | ~7 | Row 22 |
| 1.14 | PNG + p40 | p40, 5.83×5.67, 35 % | ~6.7 | Clean: shared y across A–D, every line legended |
| 1.15 | PNG + crop c15a + p42 | p42, 5.83×4.67, 29 % | **~5.9; side labels ~5** | **1 overlap** (row 23), row 24 |
| 1.16 | PNG + p44 | p44, 5.83×4.86, 30 % | **~5.9** | Shared y. Blue vs violet near-pair, separated by solid/dashed and marker (minor) |
| 1.17 | PNG + p45 | p45, 5.83×2.44, 15 % | ~6.4 | "simulated (mean of 400)" has no unit; house rule is every count carries its unit (minor) |
| 1.18 | PNG + p47 | p47, 5.83×2.87, 18 % | **~5.4 (smallest in chapter)** | Clean geometry; text size only |
| 1.19 | PNG + p48 | p48, 5.83×2.78, 17 % | ~6.7 | Row 26 |

## Findings
Every row is verifiable against a source: yes.

| # | Location | Issue | Sev. | Suggested fix |
|---|---|---|---|---|
| 1 | Fig 1.2 D, 2m30s | The sliding-count trace peak runs to the top of the axes and flattens there. It looks clipped, while C's matching bar (14) sits below its top. | minor | Raise D's ylim above the maximum, or share C/D ylim with headroom |
| 2 | Fig 1.2 A, event 3 | The two planted ▼ (4 s apart) and the green/red verdict ▼ pairs touch and merge into a "W". | minor | Narrow the markers or widen the figure so the two triangles separate |
| 3 | Fig 1.2 bottom | The "time" x-label sits about 5 px above the legend row ("false alarm"). | minor | Add a legend top margin |
| 4 | Fig 1.3 E | The "±1.5 s gather" bracket is labeled at event 1 but repeated unlabeled at event 2. | minor | Label both, or say "both brackets" |
| 5 | Fig 1.3 E vs F | Both are "cells per bin" but with different y-tops (E ~17, F ~14). The deviation is not marked. | minor | Share ylim, or note it |
| 6 | Fig 1.3 B/C, 4 s row | The 4 s window bar runs past the right axis limit, and its "10" label sits on the clipped edge. C's 1 s row has an empty outlined window box that is not in the legend. The lighter/darker orange shade in B's 1 s row is explained only in the caption. | minor | Clip the bar inside the axes and add the shade to the legend |
| 7 | **Fig 1.4 C legend** | The legend text "independent cells" collides with the blue peak's data point at +0.1 lag (crop c4a). | **major** | Move the legend (e.g. right half below the HWHM labels) or frame it |
| 8 | **Fig 1.4 E legend** | The frameless legend line "background alone (0.0096 Hz per cell)" is struck through by the sharp-set curve and its markers at K = 9–11 (crop c4b). | **major** | Put the legend lower-left (empty region) or below the axes |
| 9 | Fig 1.5 B key | The color key says "orange: the swapped tiles…" in grey text at smaller size below the panels. This is the pattern the checklist names: a color key that is not set in its color. It also uses spatial words ("right:", "below:"). | minor | Set the word "orange" in orange or add a swatch; keep the key at body size |
| 10 | Fig 1.6 | Category pairs are close in hue: teal (4 s window) vs dark green (K = 6), and blue (1 s) vs violet (joint fit). Only marker and line style separate them. | minor | Swap one of each pair to a contrasting hue |
| 11 | **Fig 1.7 A** | The dotted vertical "window = full width" line runs through the annotation text "Gaussian and uniform differ by … (g₃)" (crop c7a). | **major** | Move the annotation left of x = 3.46 or give it a white background |
| 12 | Fig 1.7 A vs B | Mid-blue means "2 onsets (g₂)" in A and "10 cells per event" in B. One color carries two concepts in adjacent panels. | minor | Change one palette |
| 13 | Fig 1.8 | The light-blue ▼ is a data marker (5 cells per event). The house rule reserves ▼ to mean "look below" (planted event). Grey circles stand for all cell counts while the blue circle means 10 cells. | minor | Use a different shape for 5-cell |
| 14 | Fig 1.9 A vs B | Same measurement (participant residual), different y-limits (±0.13 vs −0.3 to +0.5). The difference is not marked on the figure. | minor | Share ylim, or mark it ("note: y-scale differs") |
| 15 | Fig 1.9 x-axis | Categorical groups are spaced evenly with numeric ticks (0.0125 … 1), so they read as a continuous axis. The grey vertical group separators are explained only in the caption (p29), not on the figure. | minor | Add a legend entry for the separators; consider a categorical tick style |
| 16 | Figs 1.9, 1.11, 1.15, 1.16 | Bold or plain titles sit above plots ("background 0.01 Hz per cell"). This conflicts with the CLAUDE.md "no titles above plots" rule. | minor | Move them into y-labels or panel headers |
| 17 | **Fig 1.10 row titles** | The row title "…53.6 (slow) events per recording" overprints panel letter **B** (crop c10a). The second title nearly touches **D** (c10b). | **major** | Move the row titles up or the letters down |
| 18 | Fig 1.10 A/C and B/D | Same quantities, different axis limits; the deviation is not marked. | minor | Mark it, or share limits |
| 19 | Fig 1.10 legend | The legend shows a grey "joins one measurement's two predictions" line, but the plot draws it in series color. The "small: 7" count has no unit. | minor | Match the legend line color; write "7 cells" |
| 20 | Fig 1.11 | Purple carries both "A, B: joint fit" and "C: joint fit, hard-core form". The grey vertical group separators in C are not legended. | minor | Relabel or recolor |
| 21 | Fig 1.11 B | The "2 below the curve" label sits ~5 px from the purple error bar at 0.2 s (near-miss, c11a). | minor | Nudge it |
| 22 | Fig 1.13 | A blue ▼ marks the "95 % upper bound" (value marker). That is a third meaning for ▼ in the chapter: planted event in 1.1–1.5, data series in 1.8, upper bound here, "resolves at every separation" in 1.15. | minor | Pick another glyph (e.g. bar-topped arrow ↓ or "⊤") for bounds |
| 23 | **Fig 1.15 C** | The "†††" test-size markers print over the dotted 7.1 s and 3.8 s reference lines, and the left dagger touches the y-axis spine (crop c15a). | minor–major | Offset the daggers or place them beside the points |
| 24 | Fig 1.15 A, B | The reference lines (7.1 s, 3.8 s, 2.5 s, frame 0.1 s) are labeled only to the right of C and repeated unlabeled in A and B. The checklist names this case. | minor | Add short labels inside A, or say "lines as in C" |
| 25 | Text size, all docx placements | At the pandoc placement, generator text prints at about 5.4–6.7 pt in 15 of 19 figures; Figs 1.6, 1.15, 1.16 and 1.18 are below 6 pt. Annotations print near 5 pt. | major | Regenerate at a native width near 6 in (the 12 pt fonts then print near 12 pt), or raise font sizes |
| 26 | Fig 1.19 A | The power 0.8 and test-size 0.05 reference lines are labeled only in B. | minor | Label in A, or note "as in B" |
| 27 | docx geometry | Every figure is placed at 5.83 in, left-aligned, leaving 0.67 in of the text block empty at right (whether to widen is agent 9's call). Captions split from their figure across pages for 1.2 (p6/7), 1.3 (p10/11), 1.4 (p12/13), 1.5 (p16/17), 1.9 (p28/29), 1.10 (p30/31) and 1.11 (p33/34). Pages 1 and 11 are about half and two-thirds blank because the following figure did not fit. | minor | Set image width to the text width; keep the image with its caption (keep-with-next) in the reference docx |
| 28 | docx, Reproducing block (p65–66) | Indented code lines up to 129 characters wrap mid-token in Word. For example `…order_rounding_cells.p` / `y`, and `# in-` / `sample checks`. The copied commands come out broken. | minor | Shorten lines (put comments on their own line), or use a smaller code font in the reference docx |
| 29 | docx links | 14 relative links (`../learned/…`, `../goals/…`, `theory.py`) are dead in a standalone docx sent to Dropbox. | minor | Point them at GitHub URLs, or drop the links and keep the paths as text |
| 30 | docx properties | The title and author are empty (see the Document properties section above). | minor | Pass `-M title="Chapter 1. …" -M author=…` to pandoc |
| 31 | PNG metadata | Six figures in `learned/` carry Titles numbered for another document; two filenames carry a stale date (see the Document properties section above). | minor | Re-stamp the titles; let the name builder take the build date |

## Clean on every figure
- **Axis names and units:** every axis has both. Time axes use the house s/m ticks.
- **Panel letters:** every multi-panel figure is lettered, and every panel letter the text cites exists (grep: 1.2 C/D, 1.3 D/E, 1.4 C–E, 1.5 A–C, 1.6 A/D/F/H, 1.7 A/B, 1.11 A/C).
- **Histograms:** none carries vertical marker lines.
- **Rasters:** in 1.1 to 1.5 they stay black ink, with cues in the lane above and ▼ pointing down.
- **Colormaps:** there are no colorbars or heatmaps in this chapter, so the colormap rule does not apply.

## Summary
- **Build:** current.
- **Overlaps:** five real collisions need regenerating: 1.4C, 1.4E, 1.7A, 1.10 B/D and 1.15C (rows 7, 8, 11, 17, 23).
- **Print size:** text in the docx is undersized across most figures (row 25). This is a regenerate-at-print-width fix, not a docx setting.
- **Document properties:** fail (row 30).
- **Everything else:** minor.
