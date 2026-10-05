<!-- Verbatim role report, except that this machine's absolute paths are written as %USERPROFILE% and <darkroom> (the repository is public). The unedited original is in <darkroom>/bugarach/2026-09-18-fair-comparison-run/report/review-roles-round2/. -->

GRANT 10 ok — Read, Grep, Glob, Bash

# Role 10 (Ship It), round 2: fair_comparison_2026_09_18/report.html (hash 16ac704)

**Result: the build is current and clean, and no figure overlaps anything or runs off the page. Two new defects, both moderate, are in the figures added or changed this round:**
- **Figure 5, panel B:** the four blue net curves cannot be told apart reliably.
- **Figure 8:** the replicate diamond covers a fold dot in 6 of 8 rows.

The remaining findings are minor.

**What I rendered and measured:**
- I rendered the page myself with Playwright chromium at 1100 px (device scale 1 and 3) and at 400 px.
- Renders are in `%USERPROFILE%\AppData\Local\Temp\claude\c--Users-<user>-bugarach-bugarach\0c979457-501e-4b3d-9c4b-21e394823cf5\scratchpad\mb\r2-role-10\`:
  - `renders\` has the figures, tables and full-page shots.
  - `zoom\` has the 3x crops, the 400 px figure and table shots, and the page split into chunks.
- I read the SVG coordinates straight out of the HTML and counted each figure's elements against the generator's loops.

**Build currency: PASS.**
- The generator rebuilt into scratch (`rebuild\index.html`) gives the same bytes as the shipped file apart from 2 stamp lines: the build time (09:20 against 09:16) and the version (`+gc261f9c` against `+g2ca264e`).
- Commit `c261f9c` changes only `report.html` relative to `2ca264e`.
- File times line up:
  - `report.html` 09:16:55.
  - Generator 09:14:27.
  - The newest input, `merge_gap.json`, 09:11:38.
  - `replicate_summary.json` 09:03, `fold_draws.json` 08:51, `crowded_check.json` 08:02; `results`, `meta`, `ran` and `progress` 07:58–07:59.
  - Nothing under `configs/` or `selections/` is newer than the report.
- The git tree is clean.
- The darkroom `index.html` is byte-identical to the repo copy (238,260 bytes each, same mtime); I checked this myself.

**Page geometry at 1100 px:**
- The text column is 948 px (a 980 px `main` minus 16 px padding each side).
- Every figure renders at its intrinsic 900 px width: 94.9% of the column, 81.8% of the viewport.
- The smallest SVG text is 11 px, in every figure. Captions are 15 px and body text 16 px.

## Table

| Item | Render checked | Rendered box (px; % of 948 px column) | Overlap / off-page | Everything drawn is present | Axes: name + unit | Marks identified | Result |
|---|---|---|---|---|---|---|---|
| Build currency | rebuild diff + mtimes + git | — | — | — | — | — | **PASS** |
| Figure 1, one simulated recording | renders\fig1.png, zoom\page_0.png | 900×500 at x 60; 94.9% | none | yes: 33 raster rows; 3 lane triangles (1 filled blue, 2 hollow gray); probe hatch. 1,105 `line` elements, 3 `path` | x "time in the recording", ticks 16m…26m (minutes-friendly); y "33 ROIs, most active in this window on top" | lane labels on the figure; nothing on the raster; triangles point DOWN | pass |
| Figure 2, nested layout | renders\fig2.png | 900×300; 94.9% | none; about 50 px of empty band below panel A's fold labels | yes: 26 rects | n/a (diagram); column labels "fold k: 12 seeds" | each fill is named by the text inside it | pass; the "B A net" title reads run-on (F5) |
| Figure 3, fitting draws | renders\fig3.png | 900×450; 94.9% | none | yes: 389 rects (2 panels × 4 rows × 48 cells + 4 legend + 1 background) | fold labels now sit under each panel (round-1 F12 fixed) | legend swatches in colour; the red/green verdict line is stated in words | pass; "B As this run…" run-on (F5) |
| Figure 4, two selections (schematic) | renders\fig4.png | 900×330; 94.9% | none (round-1 F3 fixed: the label stays inside the budget region) | yes: 24 candidates + 2 rings + reference square | y "F1 on the training recordings"; x "false alarms per hour on the training recordings"; schematic, no ticks, stated as such | every glyph labelled on the figure; CoactDetect is now a black square (round-1 F10 partly fixed) | pass |
| Figure 5, merge gap, A + B | renders\fig5.png, zoom\f5_B.png | 900×560; 94.9% | **B: net labels pushed off their curves (F1); rings overlap at 2 s and 8 s (F3)** | coded curves at 0–30 s; **nets only at 2–16 s, but the caption says "at each gap" (F4)**; 24 circles = 16 net points + 4 net rings + 3 coded rings + 1 legend ring | B y "held-out F1"; x "merge gap: …", ticks "0 s…30 s" **evenly spaced, not to scale (F2)** | A: legend in colour. B: coded line styles named only in the caption; the ring has a legend | **fails the identification and overlap checks (F1–F4)** |
| Figure 6, two draws | renders\fig6.png | 900×150; 94.9% | none | yes: 97 rects | fold labels "fold 1: 1000–1011" **carry no unit (F6)** | row labels A/B; the alternating fold shading is explained only by the labels beneath it | pass, with F6 |
| Figure 7, held-out F1 per fold | renders\fig7.png, zoom\f7.png | 900×540; 94.9% | none: folds now offset vertically within each row (round-1 F2 fixed); 4 marks per row | yes: 78 circles = 76 data (80 − 4 locust ×) + 2 legend | x "held-out F1" on both panels; shared limits 0.2–0.85 | legend covers dot, bar, hollow and ×; nets are blue rows and coded black, both named in the caption; **the blue net mean bar is not in the legend (legend bar is black), F8** | pass, with F8 |
| Figure 8, net minus CoactDetect | renders\fig8.png, zoom\f8_rows.png | 900×360; 94.9% | **the replicate diamond covers a fold dot in 6 of 8 rows; 2 folds fuse into 1 dot in 2 rows (F0)** | yes in the DOM: 32 dots + 8 diamonds + legend | x "net minus CoactDetect, held-out F1 (right of 0: the net is ahead)" | on-figure legend present (round-1 F9 fixed); the caption now names the 2 right-of-zero folds (round-1 F0 fixed) | **fails the overlap check (F0)** |
| Table 1, contestants | renders\table1.png | 980 px wide at 1100 | none | 10 rows | "5 settings; 24 configurations" (units present) | — | pass; visible "Table 1." caption (round-1 F7 fixed) |
| Table 2, headline | renders\table2.png | 930 px | none | 10 rows | F1 is unitless; *t* is defined | — | pass |
| Table 3, crowded check | renders\table3.png | 980 px | none | 12 rows | "8 s (top of its grid)", "no merge setting" (round-1 F5 fixed); single values where min = max (round-1 F6 fixed) | — | pass |
| Cross-check, figures against tables | DOM + tables | — | — | Fig 7 hollow/filled pattern matches Table 3 "folds passing" in every row; Fig 7/8 means match Table 2 (e.g. chorus_norm −0.007 falls at x 775.4, where the bar is drawn) | — | — | pass |
| HTML metadata | DOM | — | — | — | — | — | `lang="en"`, charset, viewport, specific title; **no author, description or date meta (F7)** |
| Provenance line | zoom\page_5.png | — | — | — | — | — | clean stamp `0.1.0+g2ca264e`, built 09:16; **it names `docs/reviews/fair-comparison-2026-09-19.md`, which does not exist yet (F9)** |
| Phone width, 400 px | renders\page_full_400px.png, zoom\n_fig*.png, n_table*.png | scrollWidth = 400 | no page-level sideways scroll | — | — | — | Figures keep 900 px inside a 368 px container that scrolls (41% visible), and all 3 tables scroll inside `.wide`. This is the known cost the CSS comment records: a residual, not a new finding. |
| Figure numbering and references | DOM grep | — | — | — | — | — | PASS: captions "Figure 1."–"Figure 8." and "Table 1."–"Table 3."; every figure reference in prose carries number and name (e.g. "Figure 8, each net minus CoactDetect") |

## Findings (location · issue · severity · suggested fix · verified against a source?)

**F0. Figure 8: fold dots hidden under the replicate diamond or fused · moderate.**
- **Issue:** each row draws all 4 folds on one line (no vertical offset, unlike Figure 7), then draws the replicate diamond on top at 5 px half-width.
- Dot and diamond centres from the SVG:
  - chorus_gain_norm, F1 alone: dot 739.1 / diamond 739.1, exactly under it.
  - chorus_gain_norm, budget: 746.8 / 745.6.
  - line_length, F1 alone: 723.4 / 722.9.
  - line_length, budget: 702.1 / 699.8.
  - tube, F1 alone: 620.7 / 617.9.
  - tube, budget: 572.5 / 568.3.
- 2 rows also fuse folds:
  - chorus_gain_norm, F1 alone: 787.2 and 787.8, on the zero line.
  - chorus_norm, F1 alone: 784.0 and 786.6.
- So "chorus_gain_norm, F1 alone" reads as 2 dots plus a diamond. The caption points at 2 folds right of zero there, and they render as one mark.
- **Fix:** use Figure 7's per-fold vertical offset (e.g. y + (k − 1.5)·4), and draw the replicate diamond on its own sub-line (e.g. y + 9) or behind the dots.
- **Verified:** yes (SVG cx values; zoom\f8_rows.png).

**F1. Figure 5, panel B: net curves identified only by labels that do not sit at their curves · moderate.**
- **Issue:** all 4 nets are the same blue, so a label's position is their only identity, and the labels are misplaced in 2 ways.
  - **Wrong column:** every label goes at x1+10, the 30 s column, but the net curves end at 16 s. The labels float about 115 px from their curve ends, with no leader line.
  - **Pushed off their curves:** the de-collision loop (`y = max(y, last + 14)`, labels sorted top-down) pushes them downward.
    - "chorus_gain_norm" sits at about 0.752, while its curve ends at 0.736.
    - "binned SCE" is placed between two net labels.
    - Which blue line is chorus_norm and which is chorus_gain_norm has to be inferred.
- **Fix:** put each net's label at its own last point (x of 16 s + 8), or add short leader lines from label to curve end. Alternatively, vary the net line style (dash patterns) and add an in-figure legend.
- **Verified:** yes (zoom\f5_B.png; generator lines 437–462).

**F2. Figure 5, panel B: x-axis is categorical but drawn as continuous lines · moderate.**
- **Issue:** `X = x0 + gaps.index(g)/(len(gaps)-1)·(x1-x0)` spaces 0, 2, 4, 8, 16 and 30 s equally. The 0→2 s step and the 16→30 s step get the same width, so the slopes between points, including the "rise all the way to 30 s" the caption points at, are not proportional to seconds. Nothing on the figure says the axis is not to scale.
- **Fix:** plot on a true scale (e.g. linear, or symlog with a 0 s break), or mark the axis "gaps tried, evenly spaced" and draw markers without connecting slopes.
- **Verified:** yes (generator line 418; render).

**F3. Figure 5, panel B: rings collide · minor.**
- **Issue:**
  - At 2 s, the chorus_gain_norm ring (0.703) and the line_length ring (0.705) draw as one doubled ring.
  - At 8 s, the CoactDetect ring (black) and the LoCo ring (gray) intersect on top of the lines.
- **Fix:** draw the ring once per distinct point, offset the overlapping ones, or use a smaller ring with a white halo.
- **Verified:** yes (zoom\f5_B.png).

**F4. Figure 5 caption against what is drawn · minor-moderate.**
- **Issue:** the caption says "the nets, re-decoded at each gap", but `merge_gap.json` has `net_gaps_sec = [2, 4, 8, 16]`, while the coded gaps are 0–30 s.
  - The nets have no point at 0 s or 30 s, and the figure does not say why.
  - The missing 30 s point is the one where binned SCE ran.
  - Body text elsewhere says "at its best gap tried, 16 s", but the figure does not.
- **Fix:** have the caption say "re-decoded at 2 to 16 s, the gaps tried".
- **Verified:** yes (merge_gap.json; SVG point counts).

**F5. Panel letters run into titles · minor.**
- **Issue:** the source writes the letter and title with 2 spaces ("B  A net, …"), but SVG collapses whitespace. It renders as "B A net, inside held-out fold 1" (Figure 2B), "B As this run drew them" (Figure 3B), "A F1 alone" / "B F1 under the budget" (Figure 7), "A this run" (Figure 6). "B A net" reads as one token.
- **Fix:** "B. A net…" or "B: …", or `xml:space="preserve"` / a separate bold `<tspan>` with dx.
- **Verified:** yes (renders).

**F6. Figure 6: numbers without a unit · minor.**
- **Issue:** the fold labels read "fold 1: 1000–1011", where Figure 3 says "seeds 1000–1011". The house rule is that every number carries its unit.
- **Fix:** "fold 1: seeds 1000–1011".
- **Verified:** yes.

**F7. HTML document properties · minor.**
- **Issue:** `lang`, charset and title are correct and specific. There is no `<meta name="author">`, `description` or date. Build time and commit appear only in the Provenance line.
- **Fix:** add author, description and a `dcterms.created` (or similar) meta carrying the build stamp.
- **Verified:** yes (DOM).

**F8. Figure 7 legend: blue mean bar not keyed · minor.**
- **Issue:** the legend's "mean of 4 folds" bar is black, while net rows use a blue bar. The caption covers it ("nets in blue"); the legend does not.
- **Fix:** accept, or draw the legend bar half blue and half black.
- **Verified:** yes.

**F9. Provenance line names a review record that is not in the tree · minor, expected to close.**
- **Issue:** the page says "The review record for this page is docs/reviews/fair-comparison-2026-09-19.md". The tree has only `docs/reviews/fair-comparison-2026-09-19-roles/`.
- **Fix:** make sure the record lands with this round, or the link is dead.
- **Verified:** yes (`ls`).

**F10. Colour reuse across figures (carried from round 1, reduced) · minor.**
- **Issue:**
  - Blue (#1b5fa8) still means 4 things: planted event (Figure 1), "fitted" (Figure 3), "chosen under the budget" (Figure 4), and nets (Figures 5, 7, 8).
  - Orange (#c2410c) means "picks the threshold" in Figure 3 and "the replicate" in Figure 8.
  - The CoactDetect glyph is now consistent (black) across Figures 4, 5, 7 and 8.
- **Fix:** optional. Give "the replicate" (Figure 8) a colour not used elsewhere.
- **Verified:** yes.

## Round-1 findings confirmed fixed in this build
- Round 1's Figure 8 false caption (F0) and Figure 7 overplot (F2).
- Round 1's Figure 5 label-over-boundary (F3); it is Figure 4 now.
- Round 1's fold labels under the legend (F12); it is Figure 3 now.
- Table 3 "— s" (F5) and degenerate ranges (F6).
- Visible table numbers (F7).
- Panels lettered, no "top/bottom" (F8).
- Figure 8 legend (F9).
- Raw-seconds caption in Figure 1 (F11).
- `lang` attribute (F14).
- Dirty provenance stamp (F15).
- The stale build (F1) is resolved: the build is current.
- A grep of the prose outside SVGs finds no spatial panel references.

## Checked clean
- Nothing is drawn on Figure 1's raster; the cues sit in a lane above it, with down-pointing triangles.
- The planted-event ▼ glyph is identical in Figure 1 and Figure 5A.
- Figure 7 shares x-limits across panels A and B.
- No text runs outside any viewBox, and no text is under 11 px.
- Element counts match the generator's loops in all 8 figures.
- The page has no sideways scroll at 400 px.
