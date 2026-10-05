<!-- Verbatim role report, except that this machine's absolute paths are written as %USERPROFILE% and <darkroom> (the repository is public). The unedited original is in <darkroom>/bugarach/2026-09-18-fair-comparison-run/report/review-roles/. -->

GRANT 10 ok — Read, Grep, Glob, Bash

# Role 10 (Ship It): build and craft gate for fair_comparison_2026_09_18/report.html (hash 76c3270)

I rendered the page myself with Playwright chromium: 1100 px viewport, plus a second pass at 400 px wide. Output is in `%USERPROFILE%\AppData\Local\Temp\claude\c--Users-<user>-bugarach-bugarach\0c979457-501e-4b3d-9c4b-21e394823cf5\scratchpad\mb\role-10\`:
- Whole-figure, table and page renders are in `r\`.
- Zoom crops are the `z_*.png` files.
- Table-in-context crops are `ctx_table*.png`.

I measured element geometry, font sizes, text-box overlaps and text outside the viewBox from the DOM, and counted the SVG elements against the generator's loops.

**Page geometry at 1100 px:** the text column is 980 px wide and the page is 11,128 px tall. Every figure renders at its intrinsic 900 px width: 91.8% of the column, 81.8% of the viewport. No text sits outside any SVG's viewBox. The smallest font in every figure is 11 px or larger.

## Table

| Item | Render checked | Rendered box (px; % of 980 px column) | Overlap / off-page | Everything drawn is present | Axes: name + unit | Marks identified | Result |
|---|---|---|---|---|---|---|---|
| Build currency | file mtimes + git | — | — | — | — | — | **PASS for 76c3270, but now STALE against the working tree (finding F1)** |
| Figure 1, one simulated recording | r\fig1.png | 900x520 at (60, 746); 91.8% | none | yes: 33 raster rows, 3 down-triangles (1 planted, 2 distractor), hatch | x "time in the recording", ticks 16m…26m (minutes-friendly); y "33 ROIs, busiest on top" | lane labels plus caption; raster left clean; triangles point DOWN | pass, with F11 and F8 |
| Figure 2, the four nets | r\fig2.png, z_fig2_chorusgain.png | 900x470 at (60, 2603); 91.8% | "chorus_gain_norm" ends 0.8 px from the raster box stroke (F4) | yes: 4 rows x (raster + 3 boxes + arrows) | n/a (diagram) | in-figure note says "shaded first box", but the shaded box is the 2nd box drawn (F4) | minor defects; the working tree deletes this figure (F1) |
| Figure 3, the nested layout | r\fig3.png | 900x400 at (60, 3543); 91.8% | none; about 60 px of empty band at the bottom of the SVG | yes | n/a; folds labelled "fold k: 12 seeds" | cell text labels every fill | pass (A and B lettered) |
| Figure 4, the fitting draws | r\fig4.png | 900x420 at (60, 4279); 91.8% | none | yes: 389 rects = 2 panels x 4 x 48 + 4 legend + 1 background | fold ticks sit under the legend, not under the strips (F12) | legend covers all 4 fills; red/green verdict text is also stated in words | pass, with F12 (A and B lettered) |
| Figure 5, the two selections | r\fig5.png, z_fig5_ref.png, z_fig5_top.png | 900x380 at (60, 5295); 91.8% | "reference CoactDetect" label crosses the dashed budget line; orange square overlaps a grey dot (F3) | yes | y "F1 on the training folds"; x "false alarms per hour (…)"; schematic, no ticks (stated on the figure) | every glyph labelled on the figure | fails the overlap check (F3) |
| Figure 6, the two draws | r\fig6.png | 900x300 at (60, 6076); 91.8% | none | yes: 96 cells + background | n/a | row labels; the fold shading is explained only in the caption | caption uses "Top/Bottom" (F8) |
| Figure 7, held-out F1 | r\fig7.png, z_fig7_nets.png, z_fig7_sce_gated.png, z_fig7_coded.png | 900x520 at (60, 6559); 91.8% | **marks overplot: 4 fold dots render as 3 blobs; in binned SCE under the budget, a hollow dot is hidden under a filled one (F2)** | in the DOM yes (82 circles, 24 hollow, all correct); **not all visible** | x "held-out F1" on both panels; shared limits 0.2–0.85 | legend: dot, bar, hollow | fails the "visibly present" check (F2); panels not lettered (F8) |
| Table 2 (the headline table) | r\table2.png, ctx_table2.png | 856x360 at y 7181 | none | yes | F1 is unitless; *t* is given | — | no visible "Table 2." label (F7) |
| Figure 8, net minus CoactDetect | r\fig8.png, z_fig8_zero.png | 900x330 at (60, 8012); 91.8% | none | yes: 32 dots | x "net minus CoactDetect, held-out F1 (right of 0: …)" | **no on-figure legend for dot, bar or dashed zero line (F9)** | **the caption's claim is false against the render (F0)** |
| Table 1 | r\table1.png, ctx_table1.png | 980x576 at y 2009 | none | yes | — | — | no visible "Table 1." label (F7) |
| Table 3 | r\table3.png | 980x594 at y 8917 | none | yes | "— s" printed as a unit on a missing value (F5) | — | fails the craft check (F5, F6, F7) |
| HTML title / metadata | DOM | — | — | — | — | — | title is specific; no `lang`; no author or description meta (F14) |
| Provenance line | page_full_1100px.png | — | — | — | — | — | stamp reads "0.1.0+gbdbd77b.dirty" (F15) |
| Phone width, 400 px | r\page_full_400px.png, p400_b.png | scrollWidth = 400 | no sideways scroll at page level | — | — | — | PASS. Figures scroll inside their containers, showing 368 of 900 px (41%). Table 1 cuts off at the edge ("configurat") with no visible scroll cue. This is the known cost the CSS comment records. |
| Figure numbering and references | DOM grep | — | — | — | — | — | PASS: "Figure N." captions 1–8, and every in-text reference gives number and name |

## Findings (location · issue · severity · suggested fix · verified against a source?)

**F0. Figure 8 caption, "no dot is to the right of it" · major.**
- **Issue:** the caption says no fold is right of zero, but two folds are.
  - chorus_gain_norm on F1 alone, folds 1 and 2, sit at +0.00006 and +0.0004 F1.
  - In the render their centres are at x 787.2 and 787.8; the zero line is at x 787.1.
  - Recomputed with the generator's own `Run.cmp`: per-fold values [6e-05, 0.0004, -0.15282, -0.02898].
  - The mean-level claim ("no net is ahead") still holds. The per-fold claim in the caption does not.
- **Fix:** state it, e.g. "two folds of chorus_gain_norm on F1 alone sit at zero (+0.0001, +0.0004)". Or compute the sentence from `per_fold` instead of typing it.
- **Verified:** yes (results.json via `Run`).

**F1. Build currency · major.**
- **Issue:**
  - For artifact 76c3270 the build was current:
    - report.html was written at 08:16:20.
    - The generator's mtime is 08:15:16.
    - The newest embedded input is fold_draws.json at 08:04:26; crowded_check.json is 08:02:52.
    - results, meta, ran and progress are all 07:58–07:59, and so are configs/, selections/, the page kit build_surrogate_report.py, bench.py and provenance.py.
  - **The working tree has moved since.** `tools/build_fair_comparison_report.py` was modified at 08:23:54 and is uncommitted, as is its test.
    - The edit deletes `fig_nets` (Figure 2) and rewrites the section 3 paragraph.
    - So the built file is older than its generator, and this table describes a page that will not ship if that edit lands.
    - Figures 3–8 would renumber, so every figure reference needs re-checking.
- **Fix:** rebuild after the edit is committed, then re-run role 10 on the new build.
- **Verified:** yes (mtimes, `git diff`).

**F2. Figure 7, overplotting · moderate.**
- **Issue:** the 4.2 px fold dots are spaced about 523 px per unit of F1, so folds less than 0.016 F1 apart fuse.
  - chorus_norm on F1 alone shows 3 marks for 4 folds.
  - binned SCE under the budget shows 3 marks. Fold 3 (0.7664, hollow, not admissible) is covered by fold 4 (0.7648, filled, admissible).
  - So the "3 of 4 folds not admissible" in Table 2 cannot be read off the figure, on the very row the section 7 argument rests on.
- **Fix:** offset each fold vertically within its row (e.g. y + (k − 1.5)·4), or draw hollow dots last with a heavier stroke.
- **Verified:** yes (zoom crop, and circle cx values against the recomputed F1).

**F3. Figure 5 · minor-moderate.**
- **Issue:** the "reference CoactDetect" label runs across the dashed budget boundary into the shaded "outside the budget" region. The orange reference square overlaps a grey candidate dot. The "chosen under the budget" ring touches the dashed line.
- **Fix:** move the label left or below so it stays within budget; nudge the square off the dot.
- **Verified:** yes (z_fig5_ref.png).

**F4. Figure 2 · minor.** Moot if the working-tree deletion lands.
- **Issue:**
  - The "chorus_gain_norm" label's right edge is at 131.2 px; the raster box starts at 132.0 px. That touches in Chromium/Segoe UI, and will overlap with a wider system-ui font such as the Mac's.
  - The note "Shaded first box" is wrong against the render: the first box is the unshaded raster, and the shaded one is second.
  - "loudest 4" has no unit.
- **Fix:** widen the label gutter or shrink the label; say "shaded box"; write "loudest 4 ROIs".
- **Verified:** yes (DOM measurement).

**F5. Table 3, "merge gap chosen" · minor.**
- **Issue:** locust and SPIKE-synch show "— s". The code appends " s" to the "—" placeholder (`esc(", ".join(gaps)) + " s"`).
- **Fix:** append the unit only when a value exists; otherwise print "none".
- **Verified:** yes.

**F6. Table 3 · minor.**
- **Issue:** degenerate ranges: "0.834–0.834", "0.771–0.771", "0.851–0.851", "0.666–0.666", "0.253–0.253".
- **Fix:** print a single value when min equals max.
- **Verified:** yes.

**F7. Tables 1–3 · moderate.**
- **Issue:** "Table N" appears only in the scroll container's aria-label. No visible caption or number is rendered, while the prose says "Table 2 gives the means…" and "Table 3 gives the outcome".
- **Fix:** add a visible `<caption>Table N. name</caption>`, as the figures have.
- **Verified:** yes (ctx_table*.png, DOM).

**F8. Panel lettering · minor.**
- **Issue:** panels are referred to by position rather than letter:
  - Figure 1 caption: "Raster (bottom) … Lane (top)".
  - Figure 6 caption: "Top: … Bottom: …".
  - Figure 7 has two unlettered panels, identified only by their titles.
- **Fix:** letter them A/B, and refer to the letters.
- **Verified:** yes.

**F9. Figure 8 · minor.**
- **Issue:** there is no on-figure legend for the fold dot, the mean bar or the dashed zero line; only the caption explains them. Figure 7's legend does not carry over.
- **Fix:** add the same 3-glyph legend row as Figure 7, plus "dashed: 0, tie with CoactDetect".
- **Verified:** yes.

**F10. Colour reuse across figures · minor.**
- **Issue:** blue and orange mean different things in each figure.
  - Blue: planted event (Fig 1), fitted (Fig 4), chosen under the budget (Fig 5), this run (Fig 6), nets (Figs 7–8).
  - Orange: distractor (Fig 1), picks the threshold (Fig 4), reference CoactDetect (Fig 5), replicate (Fig 6).
  - The reference CoactDetect is an orange square in Figure 5 but black in Figures 7–8.
- **Fix:** at minimum, give CoactDetect one glyph and colour across Figures 5, 7 and 8.
- **Verified:** yes.

**F11. Figure 1 caption · minor.**
- **Issue:** times are given in raw seconds (940 s to 1,560 s, 993 s, 1,200 s) beside an axis ticked in minutes (16m…26m). A reader cannot place 993 s on the axis without arithmetic. The house rule is minutes-friendly times.
- **Fix:** 15m40s to 26m, the event at 16m33s, the probe from 20m.
- **Verified:** yes.

**F12. Figure 4 · minor.**
- **Issue:** the fold range labels ("fold 1: seeds 1000–1011" …) sit below the legend, about 90 px from the panel B strips, and panel A has none.
- **Fix:** put the fold labels directly under each panel's strips, or thin fold dividers in the strips.
- **Verified:** yes.

**F13. Figure 3 · cosmetic.**
- **Issue:** about 60 px of empty band at the bottom of the SVG, below the in-figure note.
- **Fix:** trim the SVG height to about 345.
- **Verified:** yes.

**F14. HTML metadata · minor.**
- **Issue:** `<html>` has no `lang`, and there is no author or description meta. The title "Tuned nets against tuned coded detectors" is specific to this file.
- **Fix:** add `lang="en"`, and an author and description meta.
- **Verified:** yes.

**F15. Provenance line · moderate.**
- **Issue:** "Built 2026-09-19 08:16 -0400 … at 0.1.0+gbdbd77b.dirty". The page was built from an uncommitted tree before commit 805fee9, so the stamp names no commit that reproduces it.
- **Fix:** rebuild from the clean committed tree; this falls out of F1.
- **Verified:** yes.

**Residual (not a new finding).** At 400 px the page has no sideways scroll. Each figure shows 41% of its width inside a scrolling container, and Table 1 cuts off at "configurat" with no scroll cue. This is the known cost the CSS comment records; it belongs in the residual flags.

## Checked clean
- Every figure's text is 11 px or larger (Figures 5 and 6 are 12 px or larger).
- The only text-box overlap is "raster" against "33 ROIs x time" inside the Figure 2 boxes: 2 px of ascender/descender, invisible at zoom.
- Figure 7 shares x-limits across its panels.
- Nothing is drawn on the raster in Figure 1; the lane sits above it with down-pointing triangles, and triangle colour carries the identity.
- All 8 figures are numbered, and every reference gives the number and the name.
- Every figure's element count matches the generator's loops: Fig 1 has 33 rows and 3 triangles; Fig 4 has 389 rects; Fig 6 has 97; Fig 7 has 82 circles, 24 hollow; Fig 8 has 32 circles.
- The darkroom copy was not re-hashed by me. The caller states it is byte-identical.
