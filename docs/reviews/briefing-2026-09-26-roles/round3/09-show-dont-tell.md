GRANT 9 ok — Read, Grep, Glob, Bash

(I also have SubagentHandback, which is only the report channel. I hold no Edit, Write or NotebookEdit.)

# Role 9: Show, Don't Tell. Blind review of the full-panel night briefing

**Artifact:** `<darkroom>/bugarach/2026-09-26-full-panel/briefing/index.html`, the built page. I rendered it in Playwright chromium at viewport widths 1200 and 1920 (1080 px tall). All renders and measurements are in `<scratchpad>/mb3/` (`r9_full_1200.png`, `r9_full_1920.png`, `r9_measure.json`, `r9_c*.png`, `r9_thumbs_loaded.png`). I did not open anything under `docs/reviews/briefing_2026-09-26-roles/`, and nothing outside `mb3/` was changed.

**Thresholds used:** these are project conventions I adapted to one long page, not researched values.
- "Page" means one section: h1, h2, and each h3 inside section 2.
- A section is flagged if its figure covers under 50% of its rendered area.
- Any single text block over 60 words is flagged.
- Any stretch of the page with no figure for more than about 1 screen (1080 px) is flagged.
- The 40-words-per-slide rule does not transfer to a scrolling page, so I measure runs of prose per screen instead.
- Figure share is the rendered bounding box of each img or svg, clipped to the viewport, divided by section height × viewport width.

## Count table

| Section | Visible words (incl. collapsed) | Largest block | Figure? | Figure share at 1200 / 1920 | Words before its first figure |
|---|---|---|---|---|---|
| h1 title + byline | 80 | 73 (byline paragraph) | n | 0 / 0 | – |
| 1. Leaderboard | 1,522 (4,375) | 119 (a bullet in the summary box) | y (Figures 1a–1c) | 44.2 / 55.4 | **~876 words, 2 tables; first figure at y = 2,309 px (screen 3)** |
| 2. Examples, intro | 432 | 110 (paragraph) | **n** | 0 / 0 | – |
| 2. Fast subsection | 607 | 103 (the "Passed over" paragraph) | y (Figures 2–4) | 44.9 / 55.4 | 423 words + Table 6 |
| 2. Slow subsection | 610 | 77 (Figure 7 caption) | y (Figures 5–7) | 45.1 / 55.7 | 410 words + Table 7 |
| 2. Combined subsection | 481 | 71 (Figures 9 and 10 captions) | y (Figures 8–10) | 48.3 / 58.8 | 286 words + Table 8 |
| 3. Rasters | 151 (480) | 41 | thumbnails only | 37.4 / 23.4 | 59 |
| Terms | 684 | 68 (a table cell) | n | 0 / 0 | – (glossary; prose is right here) |

**Stretches with no figure:**
- **y 0–2,309:** about 956 words, 2.1 screens.
- **y 5,120–6,785 at width 1200:** about 630 words, 1.5 screens. This is the section 2 intro plus the fast-stream preamble and Table 6.
- **Smaller stretches:** 880 px before Figure 5 and 714 px before Figure 8.
- **Terms:** 1.6 screens. Accepted, because it is reference material at the end.

## Findings
Columns: location · issue · severity · fix · verified against a source.

1. **Section 1, order of the leaderboard** · Tony asked for the leaderboard first. The leaderboard picture (Figures 1a–1c) only starts at screen 3, after a 385-word summary box, Table 1 (333 words) and Table 2 (128 words). A reader who opens the page sees no graphic for two full screens. · **major** · Put Figure 1a directly under the h2 heading. Cut the box to one assertion sentence per stream and move the rest into a collapsed `details` block below the figures. Nothing is deleted: the caveats about which bench the rows were tuned on and why the old bench is shown go to the notes. · yes (rendered y positions)

2. **Section 1, Table 1** (6 rows × 8 count columns: above zero / includes zero / below / above CoactDetect's proposal …) · Tallies typed as text, and they largely restate what Figure 1 already shows. · major · **Replacement:** a small stacked-bar strip, one bar per stream × bench (6 bars). Segments are rows above / including / below zero, and new-bench bars sit next to old-bench bars. Keep the "top unflagged row" column as a footnote, and move the full table into the collapsed Tables 3–5 section. · yes

3. **Section 1, Table 2** (CoactDetect at its shipped setting, old vs new bench) · Before/after numbers typed as a table, when the point is a change (F1 drops, calls on decoys roughly double on the fast stream, merged calls appear). · minor · **Replacement:** a dumbbell (or slope) chart per stream, old to new, with panels for F1, recall, and calls on decoys. Or a two-bar pair per stream for calls on decoys and merged calls. · yes

4. **Section 1 box, the fast-stream bullet** (119 words) and the byline (73 words) · Text blocks over 60 words. · minor · Keep one sentence each ("12 of 21 rows beat the shipped setting on the new bench, against 3 of 21 on the old"). The explanation of why decoys double becomes an annotation on the figure from finding 3, and the rest goes to `details`. · yes

5. **Section 2 intro** (432 words, no figure; blocks of 151, 110 and 101 words) · A prose-only section that runs straight into another 423 words of prose before Figure 2. Together this is the second 1.5-screen stretch with no figure.
   · **major**
   · **Fixes:**
     - **Viewer instructions (151 words):** make them a 3-step numbered strip with one annotated screenshot of the viewer's left rail (the folder button, then the results button), inside a collapsed block.
     - **Leader-selection rule (101 words):** draw it as a small flow schematic: Figure 1 order, then ran on real recordings?, then within budget?, then not on a limit?, then leader.
     - **Agreement rule (110 words):** show it as a one-row timeline schematic, two calls with a ±2.5 s tolerance band.
     - **"Read this first" box:** stays; it is a true caveat.
   · yes

6. **Section 2 subsections, the "Passed over for the leader / runner-up" paragraphs** (103, 59 and 69 words) · Lists of reasons written as paragraphs. · minor · **Replacement:** show the reasons on the leaderboard figure itself, with a reason code on the right of each skipped row (for example "over budget", "not run on the real recordings", "on a limit"). Or use a compact table (row · reason) inside a collapsed block. That also connects Figure 1 to Figure 2 visually. · yes

7. **Section 2, Tables 6–8** (calls per baseline hour: 3 kinds × 4 groups, repeated for 3 streams) · A 3×4 grid of rates typed as text, three times. · major · **Replacement:** grouped bars, one small panel per stream. The x-axis is group in the order DI, OVX, MALE, ORX; bars are the three kinds (both call it / only the leader / only CoactDetect); y is calls per baseline hour. Keep the raw counts as hover text or in a collapsed table. · yes

8. **Section 2, figure share at width 1200** · The example subsections come out at 44.9%, 45.1% and 48.3%, below the 50% threshold, only because of the preambles in findings 6–7. At 1920 they are 55–59%. · minor · Fixing findings 6 and 7 brings them over 50% by reflow, not cropping. No change to the images is needed. · yes

9. **Figures 2–10, inside the image** · The lane-label column (long detector names) takes about 35% of each image's width, so the raster and lane data get about 60%. · minor · Label the lanes "leader", "runner-up" and "CoactDetect", and give their full names once in the subsection heading or a legend. The data area then widens by about a third. · yes (estimated from the render)

10. **Captions of Figures 7, 9 and 10** (77, 71 and 71 words) · Over 60 words. They carry provenance (one of N calls of its kind, from M recordings, K calls away from window edges; distance to the nearest other call) as well as what the figure shows. · minor · Keep what is shown and why: who called it, when, how many ROIs took part. Move the selection bookkeeping to `details` or the notes. · yes

11. **Section 3, Rasters: thumbnails** · The 8 thumbnails are 4,734-px-wide review pages shrunk to 249 px (about 5% scale). The rasters cannot be read, so they work as icons, not figures. At 1920 the grid sits in the 1,080-px column with 22% empty margin on each side (figure share 23%). They also load lazily, so a full-page capture shows them blank (`r9_full_1920.png`). Once scrolled into view they do load (`r9_thumbs_loaded.png`). · major · **Replacement:** a link matrix. Rows are groups in the order DI, OVX, MALE, ORX; columns are TTX fast / slow / combined and senktide fast / slow / combined. That is 24 cells, one click each. If a picture is wanted, use one legible crop per treatment (a single recording's lanes plus raster at native scale), widened to the full width at 1920, rather than 8 unreadable miniatures. · yes

12. **Terms** (684-word glossary table at the end) · No flag. It is reference material, reached by link, and prose is the right form here. · – · none · yes

**Checked, no flag:** Figures 1a–1c get 87.5% of the width at 1200 and 1,700 px (89%) at 1920. That is good use of the canvas, and the only problem is where they sit (finding 1). No figure-bearing section has text running full width over a narrow figure. It is the other way round: the text is held to 1,080 px and the figures run wider.

**Out of my scope, reported to agent 10 as geometry:** the thumbnails need scrolling before a static capture shows them, and the example images have a fixed width of 1,080 px with `max-width: none`.
