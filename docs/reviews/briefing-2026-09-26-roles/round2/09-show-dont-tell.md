GRANT 9 ok — Read, Grep, Glob, Bash

(I also hold SubagentHandback, which is only the report channel. I hold no editing tool, and I modified nothing outside the scratchpad.)

**Role 9 (Show, Don't Tell), blind pass.** Artifact: `<darkroom>/bugarach/2026-09-26-full-panel/briefing/index.html`. I did not open anything under the reviews folder.

**How I measured.** I rendered the page with the repo venv's Python and Playwright chromium at 1200 and 1920 px viewports. Renders and measurement JSON are in `<scratchpad>/mb2/` (`full_1200.png`, `full_1920.png`, `crop1920_*.png`, `measure_*.json`). Figure share is the rendered bounding box of each figure element as a share of viewport width × section height, taken from the render and not from the source widths. Word counts come from the HTML with SVG text removed. The page layout does not change between the two widths: the text column is 1112 px wide (1080 px of content), so only the margins change.

**Thresholds** (project conventions, not optima): more than 40 words per page; any single block over 60 words; a results or methods page with no figure; two or more prose-only stretches in a row, which I read as more than one viewport (1080 px) of prose without a figure; figure share under 50%; empty margin over 20% of the width on both sides.

## Count table (each section treated as a page)

| Section | Words shown (prose / table) | Words collapsed | Largest block | Figure? | Figure share of page, 1200 px | Figure share of page, 1920 px | Longest prose-only stretch |
|---|---|---|---|---|---|---|---|
| Header | 60 (60 / 0) | 0 | 50 (byline) | n | 0% | 0% | 230 px |
| 1. Leaderboard | 1140 (952 / 188) | 2284 (Tables 2–4) | **180** ("What the new bench against the old bench shows" box) | y (Fig 1a–c) | **41%** | **26%** | **1948 px** after Fig 1c |
| 2. Examples | 1229 (974 / 255) | 0 | **168** (leader-rule paragraph); 99 ("Passed over") | y (Fig 2–9, 8 PNGs) | **47%** | **29%** | **1086 px** before Fig 2 |
| 3. Rasters with detection | 508 (58 / 450) | 0 | 54 (one Table 6 cell) | **n** | 0% | 0% | 1592 px (the whole section) |
| Terms | 463 (1 / 462) | 0 | 51 | n | 0% | 0% | 1323 px (reference, acceptable) |

At 1920 px the column leaves **21.0% empty margin on each side**. The example PNGs are 3540 px wide natively but are pinned at 1080 CSS px (`figure img.ex { width:1080px; max-width:none }`), and the Figure 1 SVGs are fixed at 1000 px. So the figures never use the canvas they could have.

**Inside each example PNG, the raster (the payload) is about 23% of the figure's area.** In Fig 2 the plot area is about 695 of 1080 px wide (64%) and the raster about 133 of 366 px tall. The rest goes to a roughly 355 px label gutter and three detection lanes.

## Findings (location · issue · severity · fix · verified)

1. **§1, box before Fig 1a** · Largest block on the page: 180 words of numbers comparing the new and old bench (rows above the reference, CoactDetect's shipped F1, median-F1 shifts, for each of three streams). It sits above the figure that shows the same thing, and Table 1 repeats it. · **Major** · Replace it with a small-multiple slope chart, one panel per stream: old → new F1 for CoactDetect shipped and for the median of the other rows, beside a stacked bar per bench counting rows above / spanning / below zero. Keep one sentence of assertion. Move the "proposals were chosen on the new bench, so they are favoured" caveat into Fig 1a's caption, and the rest into the collapsed details. · Verified: yes (render and source).

2. **§1, after Fig 1c** · 1948 px of prose-only content in a row (Table 1, then "How to read it" at about 400 words, then "What is compared", a 12-item glossary of about 200 words). That is nearly two viewports with no figure, at the end of the section Tony asked to see first. · **Major** · Relocate, don't delete. Put "How to read it" (interval method, budgets, scoring times, the ORX check) in a collapsed `<details>` beside Tables 2–4. Merge "What is compared" into Terms, or render it as a coded/learned marker on Fig 1's row labels. Table 1 stays as a table, or goes into the slope chart from finding 1. · Verified: yes.

3. **§1 and §2, whole page at 1920 px** · Figure share of the page is 26% (§1) and 29% (§2). Empty margin is 21% on each side while text and figures share one 1080 px column. The 3540 px PNGs are shown at 1080. Even at 1200 px the share is 41% and 47%, still under 50%. · **Major** · Reflow, not a crop. Let `figure` break out of `.wrap` to about min(96vw, 1800px) while the prose stays in its reading column. Or, at wide viewports, move the explanatory boxes into a narrow left column and give the figures the rest of the width. Drop `max-width:none` in favour of `width:100%` of the wider container. (Boundary: if the horizontal overflow below about 1112 px counts as a build bug, that is agent 10's; the layout policy is filed here.) · Verified: yes (measured bounding boxes at both widths).

4. **§2, before Fig 2** · 1086 px of prose before the first example. It holds the viewer-setup box, which serves §3's links more than §2; a 168-word paragraph giving the leader-selection rule; a 99-word "Passed over" list; and the kind × group count table. · **Major** · (a) The selection rule and passed-over list become a **selection matrix**: one row per candidate in Figure 1's order, columns for ran on real recordings / within budget / not on a search limit / disagrees each way, with ✓ or ✗ and the leader highlighted. Or annotate Fig 1's rows with the same marks. (b) The per-stream counts table (both call / only leader / only CoactDetect by DI, OVX, MALE, ORX) becomes **grouped bars of calls per baseline hour by group, coloured by kind**. (c) Move the viewer-setup box to §3, where the rasters are opened, and collapse it after first use. · Verified: yes.

5. **§2, example figures (Figs 2–9)** · The raster takes about 23% of each figure. Full-length detector names ("chorus_gain_norm_part · pick, training run 4 of 5") eat a gutter about 33% of the width, and a 19-ROI raster is drawn only about 130 px tall. · **Minor–Major** · Replace the lane labels with short names or a colour key shown once above the example block (the lanes already differ by colour), so the plot spans the full width. Give the raster about 60% of the figure's height. · Verified: yes (pixel measurement on the render).

6. **§3, Rasters with detection** · The section Tony asked to reach easily has **no figure**. It is a 24-link table plus a 450-word table of recording identifiers with 198 text links ("fast slow combined" repeated). Easy access is delivered as a wall of IDs. · **Major** · Replace Table 6 with a **thumbnail grid**: one small raster-plus-detection-lanes thumbnail per recording, rows in group order DI, OVX, MALE, ORX and split by first treatment, each clicking through to the zoomable viewer. Or at least do this for Table 5's 24 review pages (a group × treatment × stream contact sheet). Move the identifier list into a collapsed `<details>`. · Verified: yes.

7. **§1, Figures 1a–1c** · These are the right figures: paired ΔF1 with intervals, old and new bench joined per row, one shared x-range. But three stacked panels at 868, 748 and 808 px mean the streams cannot be compared without scrolling about 2.4 viewports. · **Minor** · At wide viewports, set the three panels side by side with one shared row-label column, or add a compact overview dot plot (new-bench ΔF1 only, all three streams) above them. · Verified: yes.

8. **Figure captions (Figs 2–9)** · About 50–59 words each, under the limit. They carry provenance ("one of N calls of its kind, M away from window edges", the shown-from/to range) beyond what the figure shows and why. · **Minor** · Keep the call, the time and the participant count. Move the selection bookkeeping to a hover title or the notes. · Verified: yes.

9. **Header and Terms** · Header: 60 words, 50-word byline. Terms: a 462-word glossary table. **Prose is right here**: this is reference material at the page's foot and should not become a figure. No flag beyond merging "What is compared" into Terms (finding 2). · Verified: yes.

## Not flagged, and why

Tony's requested order is present: leaderboard, then examples, then rasters. The new-vs-old comparison is shown graphically by Fig 1's filled and open paired marks. Only finding 1's prose duplicate is flagged, not missing content. Caveats should be relocated, not cut: every relocation above keeps the words in `<details>`, Terms or captions.
