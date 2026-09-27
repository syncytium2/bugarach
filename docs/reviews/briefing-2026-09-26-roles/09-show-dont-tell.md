> Archived verbatim except machine-local paths, shown as `<darkroom>`, `<worktree>`, `<scratchpad>` and `<repo>` (SAP004).

GRANT 9 ok — Read, Grep, Glob, Bash (I also hold SubagentHandback. I hold no Edit, Write or NotebookEdit.)

**Role 9: density and figure-first review of the full-panel briefing's `index.html`**

**Verdict:** The words are fine. The problem is that the page makes the reader scroll before any picture appears, and it tells more than it shows. Tony asked for the leaderboard first. The first 900 px screen is a 166-word box and a table, and Figure 1 starts at y=940 px. The examples start 8.3 screens down, because Tables 2-4 sit in front of them. The section called "Rasters with detection" contains no raster at all.

**How I measured it.** I rendered the page in chromium with the repo's `.venv` Playwright, at 1200 px and 1920 px wide. Word counts, block sizes and figure boxes come from the rendered page. The ink extents of the example PNGs come from their pixels. My files are in `<scratchpad>/mb/` only: `measure9_1200.json`, `measure9_1920.json`, `r9_full_1200.png`, `r9_full_1920.png`, and the crops `r9_top`, `r9_fig1a`, `r9_fig1b`, `r9_t2`, `r9_ex`, `r9_rast`, `r9_terms` (all `.png`). No script file was written: a hook blocks heredoc source files, so the scripts ran inline with `python -c`. Nothing else was modified.

**Thresholds I used.** These are conventions, not researched optima: more than 40 words per page; any single text block over 60 words; a results or methods page with no figure; two or more figure-free pages in a row; a figure under about 50% of its page's area; empty margin over 20% on both sides. On a web page, word counts for a table are mostly cell values, so I judged tables by height and by what they duplicate. For the example figures, "figure share" means the bounding box of the image. The share of that image that is actual data is given separately.

**Table: one row per page, at a 1200 px viewport (content column is 1112 px)**

| # | Page | Total words | Largest block (words) | Figure? | Figure share of the page area | Height |
|---|---|---|---|---|---|---|
| 1 | Header: h1, byline, nav | 33 | 26 | n | 0% | 190 px |
| 2 | How-to-read box | 175 (with h2) | **166** | n | 0% | 266 px |
| 3 | Table 1, at a glance | 123 | 36 | n | 0% | 354 px |
| 4 | Figure 1, the leaderboard | 362 (about 300 are axis labels; caption 58) | 58 | y (SVG, 1000×2122 px) | 89% of its element; 83% of viewport width. The data area alone (x 390-1030) is 53% of the width | **2214 px, about 2.4 screens** |
| 5 | Table 2, fast stream | 580 | 34 | n | 0% | 1605 px |
| 6 | Table 3, slow stream | 481 | 49 | n | 0% | 1222 px |
| 7 | Table 4, combined stream | 468 | 44 | n | 0% | 1292 px |
| 8 | Examples: intro and "passed over" note | 142 | **91** | n | 0% | 230 px |
| 9 | Examples: Figures 2-10 | 9 × 40 in captions, plus 3 subheads | 40 | y (9 PNGs, 1082×295-331 px displayed, 2360 px native) | Image box 82% of each figure element, 67% of the section. **The raster data area is about 20% of each image**, about 13% of the section | 3,800 px |
| 10 | Section 3: viewer setup box | 116 | **112** | n | 0% | 216 px |
| 11 | Table 5, group × first-treatment pages | 97 | 28 | n | 0% | 407 px |
| 12 | Table 6, every recording (66 rows) | 560 | 14 | n | 0% | **2727 px** |
| 13 | Terms | 225 | 47 | n | 0% (prose is right for a glossary) | 537 px |

- **Whole page:** about 3,700 words and 15,859 px tall. Figures take 30% of the page height and about 26% of its area.
- **Figure-free runs:** two runs of two or more pages in a row: pages 5-7 (Tables 2-4) and pages 10-13 (all of section 3 and Terms).
- **At 1920 px:** the column stays 1112 px wide, leaving 404 px of margin on each side (21% of the width). The example rasters, which have 2360 px of native width, are shown at 1082 px.

**Findings** (location · issue · severity · fix · verified against a source)

1. **Above the fold, pages 2-4** · There is no figure on the first screen: a 166-word box and Table 1 come before Figure 1, which starts at y=940. That goes against Tony's "leader board first". · **High** · Put Figure 1 (or the compact version in finding 2) straight under the h1. Figure 1's own legend and caption can do the box's job: filled = new bench, open = old bench, bar = 95% interval, vertical line = CoactDetect at its shipped setting. The reading-order question belongs to role 11. · Verified: yes (render, y offsets).

2. **Figure 1** · One 2122 px column holds all three streams, and the only x-axis is at the very bottom. Someone reading the fast-stream rows at the top has no tick labels on screen and must scroll about 2000 px to find them. Of the figure's 1000 px width, only 640 px is data; row labels take the rest. · **High** · Reflow it into **three side-by-side small multiples**, one per stream, each with its own x-axis and about 700 px tall, so the whole leaderboard fits on one screen. Within each panel, draw each row as a **dumbbell**: old (open) connected to new (filled) by a thin grey segment, so the shift between benches is read as a line rather than guessed from two offset dots. · Verified: yes (render).

3. **Old vs new comparison (Tony's second ask): slope chart or dumbbell?** · A paired slope chart loses the confidence intervals. Its end labels would also collide: in the render, the slow stream's old-bench values for about 18 rows fall within about 0.015 of each other near −0.03, so a slope chart's left-hand labels would pile on top of each other. · **Medium** · **Use the dumbbell from finding 2.** Add a rank **bump chart** (old rank → new rank, one line per detector, per stream) only if the point to make is how much the order reshuffles. It works as a second small panel, not as the main view. · Verified: yes (read from the rendered Figure 1).

4. **Tables 2-4** · These are three figure-free pages in a row: 1,529 words and 4,119 px. They sit between the leaderboard and the examples and push the examples to 8.3 screens down. Their content repeats Figure 1 as numbers, plus notes on budgets and on ruling 5. **They are not a better figure; Figure 1 already is the figure. They are its lookup.** · **High** · Move them behind a collapsed `<details>` under Figure 1, or to an appendix after section 3. Keep every word: the budget and ruling-5 notes are hard-won caveats, so move them, don't delete them. The flags are already encoded in Figure 1 (red marks, §5 tags); if the numbers need a direct route, a hover tooltip on each Figure 1 row can show that row's table line. · Verified: yes (render).

5. **Table 1** · A 6-row count table as the headline. The message ("on the new bench most rows beat CoactDetect; on the old bench almost none do") is a proportion, and a proportion reads faster as a bar. · **Medium** · Replace it with **100% stacked horizontal bars**, one per stream×bench (6 bars, split above / straddles zero / below). Alternatively, fold the counts into each Figure 1 panel header, e.g. "fast · new: 13 above · 4 straddle · 5 below". Keep the "top row" column as a label on the bar. · Verified: yes.

6. **How-to-read box** · A single 166-word block, over the 60-word limit. Its last two lines (when each bench was scored, how many seeds) are provenance, not reading instructions. · **Medium** · Move the scoring times and seed counts to a footer line or to Terms. Reduce the reading key to Figure 1's legend and caption. Keep the caveat about which rows were chosen on which bench, but as a footnote under Figure 1 or in a notes block, not in front of the chart. · Verified: yes.

7. **Examples, Figures 2-10: geometry inside each image** · Each PNG leaves its right 16% empty (ink ends at 84% of the native width in all 9 files), and labels take about 18% on the left. The event lanes take about as much height as the raster, which gets about 90-110 px for 33-39 ROIs (about 3 px per ROI). The evidence, the raster, is about 20% of each image's area. · **Medium** · Reflow each image: plot frame to the right edge; lanes shrunk to about 12-15 px each; raster at least 60% of image height. At wide viewports, let the example figures break out of the 1112 px column to about 95 vw, since they have 2360 px of native width. Boundary: agent 10 owns the empty right 16% as a possible geometry or build bug; I own the layout policy. · Verified: yes (pixel scan of all 9 PNGs, plus render).

8. **Example captions** · Each 40-word caption repeats the same boilerplate: the lane list, the hover hint and the "N s either side" window. That is about 20 words × 9 = about 180 repeated words. · **Low** · State the boilerplate once per stream subhead, e.g. "Lanes: A, B, CoactDetect · ±45 s · hover in the viewer for participants". Each caption then says only what the figure shows (which detector called it, group, time, participant count). · Verified: yes.

9. **Examples intro** · A 91-word paragraph, over the limit, that describes a 3×3 structure (stream × {both, leader only, CoactDetect only}) the reader cannot see. · **Medium** · Make the structure visible: add column headers "both call it · only the leader · only CoactDetect" above each stream's three figures, or use a 3×3 thumbnail index at the top of section 2 linking to the full-size figures. Move the method (median-participant selection, the 2.5 s agreement tolerance, the source file) to Terms or a notes line. Keep the 46-word "passed over" note as a footnote: it is a real caveat. · Verified: yes.

10. **Section 3 as a whole (Tables 5, 6 and the setup box)** · Four figure-free pages in a row, about 3,550 px. The "Rasters with detection" section has no raster, and its main content is Table 6, a 2727 px list of links (66 rows). That does not give Tony the "easy access" he asked for. · **Medium-high** · Replace Table 5 with a **4×2 clickable thumbnail grid** of the stacked review pages (columns in group order DI, OVX, MALE, ORX; rows TTX and senktide), with the three stream links under each thumbnail. Replace Table 6 with **small multiples: one mini-raster per recording** with call ticks in a lane above it, grouped by group × treatment, each opening the viewer. At minimum, compact it into a group-column matrix of recording chips, which takes it from about 2700 px to about 500 px. · Verified: yes (render).

11. **Section 3 setup box** · A single 112-word block, over the limit, describing a two-click procedure in prose. · **Medium** · Replace it with a **two-step annotated screenshot** of the viewer toolbar (1: Choose folder, 2: Open results), with a one-line caption. Move the reopen and permission details to notes. Out of scope for me, but worth passing to roles 2 and 10: the box prints an absolute local path that contains a person's name. That matters if this page or its text ever reaches the public repo or site. · Verified: yes.

12. **Wide viewport, whole page** · At 1920 px the fixed 1112 px column leaves 21% margin on each side. The text is constrained too, so this is not the pattern of full-width text over a narrow figure, but the rasters and Figure 1 lose space they could use. · **Low** · Keep the prose column at about 70 characters; let `<figure>` elements break out of it (e.g. `width: min(95vw, 1800px)`). · Verified: yes (1920 px render).

13. **Terms** · 225 words; largest block 47. · **None** · Prose is right for a glossary. No flag. · Verified: yes.

14. **Header** · 33 words, no figure. · **None** · Fine as a header, once Figure 1 moves directly under it (finding 1). · Verified: yes.

I quote no recording or slice IDs anywhere in this report.
