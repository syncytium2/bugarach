GRANT 10 ok — Read, Grep, Glob, Bash

# Role 10 (Ship It): blind review of the briefing page

I did not open anything under docs/reviews/briefing_2026-09-26-roles/, and I modified nothing outside the render folder.

**Renders:** `<scratchpad>/mb2/`
- full-page renders at 1200 px and 390 px wide, light and dark: `full_{1200,390}_{light,dark}.png`
- the same four renders cut into horizontal strips: `band_*.png` (9 strips at 1200 px, 21 at 390 px)
- Tables 2–4 with their collapsed section opened: `details_1200_{light,dark}.png`
- a close-up of the clipped Figure 1b label: `zoom_fig1b_label.png`
- 390 px dark, Figure 1a: `m390_fig1a_dark.png`
- the viewer opened from one of the page's links: `viewer_deeplink.png`
- measured values for every render: `metrics.json`

**Artifact checked:** `<darkroom>/bugarach/2026-09-26-full-panel/briefing/index.html`
**Generator:** `<worktree>/tools/make_briefing.py`

## Build is current: PASS, with one note
- index.html was built at 20:59:35 EDT. The generator's last commit (9e0ba401) is stamped 21:00:04, which is **after** the build. But the generator file was last written at 20:58:27, before the build, and the worktree is clean. So the build ran on the committed content. The page also shows that commit's changes: each stream's movement is stated separately, and the runner-up lane is orange.
- No file under 2026-09-26-full-panel/ is newer than index.html.
- The three inlined SVGs are byte-identical to figure1_{fast,slow,combined}.svg.
- `viewer.html` is byte-identical to the worktree's `docs/site/raster_viewer.html`. It **differs from origin/main**, so "a copy of the site's viewer" is really a copy of the branch's viewer.
- **Leftover files from an earlier build (20:29) sit beside the page and are not referenced by it:** `example_slow_leader_only.png` and `figure1_leaderboard.svg`. The PNG is a figure for a call the current page says does not exist ("no call of this kind lies at least 10 s inside…"). Anyone browsing the folder will find a stale figure. Fix: delete them, or have the generator clear old `example_*`/`figure1_*` files before writing.

## Page-wide checks
| Check | Render | Result |
|---|---|---|
| Charset declared | source | PASS (`<meta charset='utf-8'>`) |
| No page-level horizontal scroll at 390 px | full_390_light/dark | PASS: page width equals window width (390 = 390) |
| Dark mode | full_1200_dark, full_390_dark, details_1200_dark | PASS: variables switch, SVG legible, PNGs on white cards, red and orange marks legible |
| Console / page errors | all 4 renders | PASS: none |
| Type size ≥ 14.67 px (HTML and SVG, scaled by the SVG's transform) | metrics.json, all 4 | PASS: no text node below 14.6 px. SVG base size is 15 px. |
| Type size inside the PNGs, at displayed size | native 3540 px shown at 1080 px (×0.305) | PASS, narrowly. Tick-label ascender height is 37 px native, so about 51 px font, so **about 15.6 px displayed**. The x-axis label works out to about 15.3 px. The source asks for 13 pt on a 1180 px page shown at 1080 px. No margin: any shrink of the image box fails this. |
| Links: 24 review pages (`../065/review/pages/*.html`) | filesystem | PASS: all 24 exist |
| Links: viewer deep links | index.html, viewer.html, viewer_deeplink.png | PASS on keys. 214 links cover 198 distinct (recording, stream) pairs, and every link uses exactly `slice` and `stream`. `readDeepLink` reads exactly `slice` and `stream` (URLSearchParams), and a loaded link parses to `{slice, stream:"fast"}` with no errors. **Note:** 1 of 198 pairs (a fast-stream link) has no rows in detections.csv, while the same recording's slow and combined streams do. I could not check whether the export folder has that stream; if it does not, the viewer will flag the stream as missing. |
| Anchors (#leaderboard, #examples, #rasters, #terms, #viewer-setup) | source | PASS: all targets exist |
| Group order DI, OVX, MALE, ORX | band_1200_light_03/05/07 | PASS in all three examples tables, Table 5 and Table 6 |
| Times in EDT | band_1200_light_00/02 | PASS |
| Document title | source | PASS: "Full-panel night briefing". The build time is in the byline. There is no author meta tag (not required for HTML). |
| Table numbering | band_1200_light_03/05/06 | MINOR: the three per-stream "Calls on baseline windows…" tables and the Terms table have no number, so the sequence runs Table 1, 2–4, (three unnumbered), 5, 6. |

## One row per figure or section
Rendered boxes are measured off the render; the fixed 1080 px image box, the 1000 px SVGs and their inner scroll boxes are confirmed in the source CSS/markup.

| Section / figure | Render checked | Rendered box at 1200 px / at 390 px | Result |
|---|---|---|---|
| Header, nav, headline box | band_full_1200_{light,dark}_00, full_390_* | text | PASS |
| **Figure 1a** (fast) | band_full_1200_light_00, band_full_1200_dark_00, m390_fig1a_dark | 1000×868 px (83% of window width). At 390: 358 of 1000 px visible (36%) | PASS at 1200. Both axes named; one glyph per concept; orange keyed in the legend; the zero line and joining line explained; † explained; panel letter present; shared x-range stated and true. **FAIL at 390:** the visible part is the 320 px label column and nothing else. No data is on screen until the reader scrolls sideways inside the figure, and nothing hints that it scrolls. |
| **Figure 1b** (slow) | band_full_1200_light_01, zoom_fig1b_label | 1000×748 px / 36% visible at 390 | **FAIL, text clipped:** the row label "chorus_gain_norm_part · no pick, best training run 4 of 5" runs off the SVG's left edge and renders as "gain_norm_part · no pick, …". It is placed right-aligned at x=320 in a 1000-wide viewBox and is wider than 320 px. Fix: widen the label column when the longest label needs it (measure, or allow about 8.5 px per character at 15 px), or wrap or shorten the "no pick" label. Same 390 px problem as 1a. |
| **Figure 1c** (combined) | band_full_1200_light_01 | 1000×808 px / 36% visible at 390 | PASS at 1200: longest label fits, with about 60 px to spare. Same 390 px problem as 1a. |
| Table 1 | band_full_1200_light_02 | fits at 1200; needs sideways scroll at 390 (886 vs 358 px) | PASS: counts carry "rows". |
| **Tables 2–4** (collapsed section) | details_1200_{light,dark} | tables 1150 px wide in a 1080 px box | **FAIL (geometry):** even at 1200 px the tables overflow by 70 px. The last column, "merged calls, new bench", is cut off behind a sideways scroll, and the caption runs off the box. Meanwhile the "setting" column wraps to one or two words per line (a row about 7 lines tall). Fix: let the "setting" column take the width (a min-width), or move the "held-out F1…" note onto its own line under the row. |
| Viewer-setup box and leader-rule paragraph | band_full_1200_light_03 | text | PASS |
| Examples tables (×3) | band_full_1200_light_03/05 | fit at 1200; 549–596 px at 390 (sideways scroll) | PASS: counts carry "calls"; rates are "/h" under a caption that says "per baseline hour". Unnumbered (see above). |
| **Figures 2–4** (fast examples) | band_full_1200_light_03/04, full_390_* | 1080×366/428/366 px (90% of window width). At 390: 358 of 1080 px visible (33%) | PASS at 1200. The ▼ is in a lane above and points down. The raster carries no overlay (one ink). Each lane has its own row label. y-axis "fast · N ROI" has a unit; minutes-friendly ticks. The x label "time in recording" has no unit in the label itself, only in the ticks (m/s): MINOR. **FAIL at 390:** the visible third is the lane-label column; the call, lanes and raster are off screen. |
| **Figures 5–6** (slow examples) | band_full_1200_light_05 | 1080×366 px each / 33% visible at 390 | PASS at 1200 (same checks). The skipped "leader only" case is stated in text, not left silently out. Same 390 px problem. |
| **Figures 7–9** (combined examples) | band_full_1200_light_05/06 | 1080×428/406/366 px / 33% visible at 390 | PASS at 1200 (same checks). Same 390 px problem. |
| Section 3: Table 5 (24 review pages) | band_full_1200_light_07 | fits | PASS: 24 of 24 links resolve; group order correct. |
| Section 3: Table 6 (66 recordings × 3 streams) | band_full_1200_light_07 | fits at 1200; 403 vs 358 px at 390 | PASS: the count carries "recordings"; deep-link keys correct (1 link has no calls in the CSV, see above). |
| Terms | band_full_1200_light_07/08 | fits (not in a scroll box; causes no page overflow at 390) | PASS: ROI, EDT, ΔF1 and F1 defined. No number or caption (minor). |

## Findings
Each is listed as location · issue · severity · suggested fix · could I verify it against a source.

1. **Figure 1b row label** · clipped at the SVG's left edge ("gain_norm_part…") · **major** (an unreadable row name in the headline figure) · size the label column from the longest label, or wrap it · yes (the SVG `<text x='320' text-anchor='end'>` plus the render).
2. **Tables 2–4 at 1200 px** · 70 px overflow hides the last column; the "setting" column is crushed · moderate · give "setting" a min-width, or move the held-out note onto its own line · yes (scrollWidth 1150 vs clientWidth 1080).
3. **Figure 1a–c and Figures 2–9 at 390 px** · the first view shows only label columns; all data sits behind an unhinted sideways scroll (1000 or 1080 px content in a 358 px box). No page-level scroll, so the house rule passes, but the figures are unreadable on first view · moderate · at narrow widths scale the figure to fit (`max-width:100%`, accepting smaller type), or put a visible "scroll →" cue on the figure · yes (measured).
4. **Leftover files beside the page** (`example_slow_leader_only.png`, `figure1_leaderboard.svg`, both 20:29) · the delivery folder holds a figure the page says has no call to show · moderate · clear old outputs before writing · yes (mtimes, and no reference in index.html).
5. **viewer.html is the branch's viewer, not main's** · the copy differs from origin/main's `docs/site/raster_viewer.html`, so the "copy of the site's viewer" wording holds only once the branch lands · minor · note it, or land the viewer first · yes (cmp).
6. **One fast-stream viewer link** has no rows in detections.csv (its slow and combined streams do) · minor, cannot confirm · check that the export folder has that stream; drop the link if it does not · partly (CSV only; the export folder was not opened).
7. **Unnumbered tables** (3 examples tables, Terms) · minor · number them · yes.
8. **Example x-axis label "time in recording"** · the unit is only in the tick labels · minor · e.g. "time in recording (min:s)" · yes.
9. **PNG type size** · passes at about 15.3–15.6 px displayed, with no margin · note only · keep the 1080 px image box, or raise to 14 pt · yes (measured on the native PNG).

Nothing overlaps within any figure or between elements at 1200 px, light or dark. The only text running off an edge is finding 1.
