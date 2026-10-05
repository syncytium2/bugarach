> Archived verbatim. Paths are shown as placeholders (SAP004).

GRANT 10 ok — Read, Grep, Glob, Bash

(I also hold SubagentHandback, which is only for handing this report back. I have no Edit, Write or NotebookEdit. I modified nothing outside the scratchpad, and I did not open docs/reviews/briefing_2026-09-26-roles/.)

# Role 10, Ship It: blind review of the briefing page (index.html in the night's briefing folder)

**Result: the page is fine to ship once the four medium findings below are fixed.** Nothing failed outright:
- The build is current and there are no stale outputs beside it.
- All 271 links and images resolve.
- There is no page-level sideways scroll at 390, 1200 or 1920 px, in light or dark.
- Nothing measured below 14.67 px, the 11 pt house minimum.

## What I rendered
All renders are in `<scratchpad>/mb3/`. Chromium was driven through the repo venv, with every `<details>` opened, lazy images forced to load, and full-page shots:
- `full_{1200,390,1920}_{light,dark}.png`
- band crops `band_<viewport>_<scheme>_NN.png`: all 16 bands for 1200 light and 1200 dark, plus spot bands at 390 light and 1920 light
- `metrics.json`: page width, elements past the edge, text size per element, rendered box of every SVG and image, clipped elements, console errors
- `zoom_lanelabel.png`: a full-resolution crop of a lane label

"Box" in the table is the figure's rendered size in CSS px and as a share of the viewport width.

## Findings by section

| # | Section / figure | Checked against | Result | Finding (severity) |
|---|---|---|---|---|
| 0a | Build is current | file times; `git log`; `find -newer` | PASS | index.html was written at 21:29:42 EDT. The generator file was last saved at 21:28:06 and is committed unchanged (f69f884, 21:29:43). The worktree has no changes to it; the only untracked item is the round-3 review folder. No file in the night folder is newer than index.html. The viewer copy is byte-identical to the worktree's `docs/site/raster_viewer.html`. **Not checked:** the time stamps on the export folder the examples read. |
| 0b | No stale outputs beside the page | directory listing | PASS | The folder holds only what this build writes (index, briefing.json, 3 SVGs, 9 example PNGs, the viewer copy) plus `detections.csv`, which is an input. `_clean()` deletes old example and Figure 1 files before each build. |
| 0c | Page head | index.html source | PASS | `<meta charset='utf-8'>`, `lang='en'`, a viewport meta tag, and the title "Full-panel night briefing". |
| 1 | Header, nav, summary box | band_1200_light_00, 390 bands | PASS | Build time is given in EDT. Counts carry units ("12 of the 21 other rows"). |
| 2 | Table 1 | band_1200_light_00/01; band_390_light_01 | FAIL at 390 (medium) | **The caption sits inside the sideways scroller**, so at 390 px every line is cut mid-word at the right edge. The reader has to scroll sideways and back for each line. There is no scroll cue for any table. The data cells pass: every count has a unit. Fix: move `<caption>` out of `.tablewrap` (a `<p>` above the scroller), and add a table scroll cue. |
| 3 | Table 2 | band_1200_light_01 | PASS | Units on events and calls. F1 and recall need no units. |
| 4 | "What each row is" details | band_1200_light_01, 1920_light_01 | PASS | Opens correctly and runs to its full length. |
| 5 | Figures 1a, 1b, 1c (inline SVG) | band_1200_light_01–03, band_1200_dark_02, band_390_light_03, band_1920_light_01; metrics | PASS, with 2 notes | Box at 1200: 1050×868 / 748 / 808 (88% of width). At 1920: 1700×1405 / 1211 / 1308 (89%). All text is 15 px at 1200 and 24.3 px at 1920. The x-axis is named with its quantity ("ΔF1 against CoactDetect at its shipped setting, 95% interval"). The x-range is the same in all three panels, as the caption says. Legend, † and zero line are on the figure; the gray join line is in the caption. Dark mode is correct. **Note A (low):** at 390 the figure is 1050 px in a 358 px scroller, so the first view shows labels only and no marks. A cue ("Scroll the figure sideways for the marks →") is shown. **Note B (low):** at 1920 the figure text is 1.4× body size, and the fast panel is taller than a 900 px viewport. |
| 6 | **Colour meaning: Figure 1 against Tables 3–5** | figure1_fast.svg style block; band_1200_light_04/05 | FAIL (medium) | **Orange means two different things.** In Figure 1, orange (`--warn`, #b35c00) means "over a budget or no pick". In Tables 3–5, which the page presents as "every number behind Figure 1", over budget is red (`--bad`) and orange marks a search-limit note. A reader moving from the figure to its table reads orange backwards. Fix: draw the Figure 1 over-budget marks in `--bad`, or recolour the table lines so each colour keeps one meaning. |
| 7 | "How to read it" details | band_1200_light_03/04 | PASS | Opens. Every count has a unit ("2,000 draws", "48 fast … seeds"). |
| 8 | Tables 3–5 | band_1200_light_04–08; metrics (scrollers 1080 of 1401 px) | FAIL (medium) | **At 1200 and 1920 the table is 1401 px wide in a 1080 px box, with no cue.** The cue CSS only shows below 1100 px, and it is written for figures anyway. The "old bench ΔF1" column and everything to its right are hidden. Its header is cut to "[9". The caption and long note lines are cut mid-word ("F1 poolec…", "(not bracketed…"). Fix: caption outside the scroller, a scroll cue on every scrolling table at every width, or let these three tables use the wide layout. |
| 9 | Section 2 viewer box and notes | band_1200_light_08 | PASS | — |
| 10 | Tables 6–8 | band_1200_light_09/10/12, band_1200_dark_09 | PASS, with 1 low note | Group columns run DI, OVX, MALE, ORX. Rates are in "calls per baseline hour". **Low:** group headers are left-aligned over right-aligned numbers, so each header sits well to the left of its figures. |
| 11 | Figures 2–10 (example PNGs) | band_1200_light_09–13, band_1200_dark_09; metrics; zoom_lanelabel.png; text heights measured in the PNGs | PASS, with 2 low notes | Box: 1080×391–435 at 1200 (90%), 1700×615–684 at 1920, and 1080 inside a 358 px scroller at 390 (cue shown). The PNGs are 3540 px wide at scale 3, from 14 pt text on an 1180 px page, so labels display at about 17 px; the tick-label height I measured in the image agrees. The time axis reads "time in recording (min:s)" with ticks like 14m15s. The raster is black and white with nothing drawn on it. The ▼ sits in its own "this call" lane above and points down. Lanes are named on the y-axis. No clipping: lane labels start about 4 px from the image edge. **Low:** the runner-up lane is orange (#E69F00) while Figure 1 uses orange for "over budget". The lanes are labelled, so this is not a defect, but it adds to row 6. **Low:** captions write distances as "972.0 s" and "22.7 s", while the call times in the same captions are minute-friendly (14m52s). |
| 12 | Section 3 thumbnails (8 review-page PNGs) | band_1200_light_13; metrics | FAIL (medium) | Box: 249×150 each (about 21% of width) at 1200 and 1920; 160×150 at 390. **(a) Not numbered.** The house rule is "number every figure on every page"; these are figures with captions and no "Figure 11–18" or a single numbered group caption. **(b) The text inside them is unreadable at the size shown:** the source PNGs are 4734 px wide shown at 249 px (scale 0.05). For a link-only thumbnail that is arguably fine, but it breaks the letter of the "type size includes text inside PNGs" rule. Fix: number them as one figure with lettered panels, and state in the caption that they are link previews. **Low:** some captions wrap with a line starting "· slow". |
| 13 | Table 9 (every recording) | band_1200_light_13/14 | PASS | Order is DI, OVX, MALE, ORX, each by first treatment. Counts read "11 recordings". |
| 14 | Terms (glossary table) | band_1200_light_14/15 | FAIL (low) | It is a `<table>` with no table number. Either number it or render it as a definition list (`<dl>`), which does not need one. |
| 15 | Every link and image resolves | script over all 271 href/src values | PASS | 271 checked, 0 broken. No external links. Every `#anchor` has a matching id. Every image has alt text and loads (0 broken, all six renders). |
| 16 | Viewer deep links | script plus headless click-through | PASS | 198 distinct `viewer.html#slice=…&stream=…` links (216 anchors) point at 66 recordings, one link per stream (fast, slow, combined). Every viewer anchor has `target='bugarach-viewer'`, and no other target appears. I set each of the 198 fragments on the copied viewer: `readDeepLink()` returned the expected recording and stream every time, and the hashchange handler reset `DEEP`. No page errors. Clicking a link opened one viewer tab; a second click reused it (2 pages, not 3) and changed its hash. |
| 17 | Page width at 390 / 1200 / 1920 | metrics | PASS | Page width equals window width at all three sizes. No element crosses the viewport outside a scroller, and no overflow-hidden element clips its text. |
| 18 | Dark mode | full_*_dark, band_1200_dark_02/09 | PASS | Background is dark (rgb 20,20,20). Figure 1 follows the page colours. Example PNGs keep a white background with a border, which is readable. |
| 19 | Type ≥ 14.67 px | metrics (every text node; SVG text scaled to display) | PASS | Nothing measured below 14.67 px outside SVG. SVG minimum is 15 px at 1200 and 24.3 px at 1920. Example PNG labels are about 17 px. The only exception is the thumbnails in row 12. |

## Medium findings, in fix order
1. **Row 6:** Figure 1 uses orange for over budget, while its own tables use red for over budget and orange for search limit.
2. **Row 8:** Tables 3–5 overflow at every width, with no cue and with cut captions.
3. **Row 2 (with 8):** every table caption sits inside its scroller, so captions are cut at 390 px.
4. **Row 12:** the Section 3 thumbnails are unnumbered, and their text is unreadable at the size shown.

## Low findings
Terms table unnumbered (row 14); Figure 1 on phones and at 1920 (row 5 notes A and B); orange reused for the runner-up lane (row 11); seconds written as "972.0 s" in captions (row 11); Tables 6–8 header alignment (row 10); thumbnail caption wrapping (row 12).

## Not checked
The time stamps on the export folder the examples read from the default dataset.

## Paths
- Artifact: `<darkroom>/bugarach/2026-09-26-full-panel/briefing/index.html`
- Generator: `<worktree>/tools/make_briefing.py`. Relevant code:
  - Figure 1 colours: `.badn` / `.bado` use `var(--warn)`, around line 931
  - CSS: `.tablewrap`, `.scrollcue` (only below 1100 px), around lines 976–1026
  - `TERMS`: around line 1546
  - thumbnail figcaptions: in `render`
- Renders and metrics: `<scratchpad>/mb3/`
