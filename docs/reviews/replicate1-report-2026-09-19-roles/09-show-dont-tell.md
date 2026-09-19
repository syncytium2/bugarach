GRANT 9 ok — Read, Grep, Glob, Bash

# Role 9: Density and figure-first review. Blind verify round 3 of 3.

**Artifact:** `%USERPROFILE%\bugarach\bugarach-worktrees\replicate-report\docs\learned\tuned_vs_coact\replicate1\report.html`. I re-ran `git hash-object` on it and got 9a99a7a4209b11b7bb285c260a43ea31aabda1d3, which matches the hash I was given. I opened no earlier review reports.

**How I measured:**
- I rendered the page myself with Playwright chromium at 1100, 1440 and 390 px wide. All geometry below comes from bounding boxes in the rendered page, not from widths requested in the source.
- I read the supplied slices `shots3\light_1100_00`–`12`.
- I pulled the Figure 1 PNG out of the page and measured where its ink sits.
- Scratch files are in `...\scratchpad\mb3\role09\` (`stripped.html`, `raster.png`). I wrote nothing into any repository.

**Thresholds, adapted from slides to a scrolling report.** These are conventions, not researched optima.
- The "40 words per slide" rule does not transfer: every section of a report exceeds it. I report the counts but do not flag on them.
- I flag:
  - a results or methods section with no figure;
  - two or more prose-only sections in a row;
  - any text block over 60 words that a figure could carry;
  - any caption over 60 words;
  - any graphic under 50% of its figure block;
  - any graphic with more than 20% of its width empty on both sides.
- The column is 1000 px wide at both 1100 and 1440 px, and prose sits in a 653 px measure inside it.

## Count table, one row per section, at 1100 px

| section | prose words | caption + key words | table words | largest prose block | figure? | graphic's share of section height | graphic width as % of column |
|---|---|---|---|---|---|---|---|
| lede and answer box | 425 | 0 | 0 | 96 | n | 0% | – |
| 1 The problem | 142 | 188 | 0 | 74 | y (Figure 1) | 29% | 100% box; about 77% is plot (PNG has a blank right strip, see F1) |
| 2 Why a simulation | 442 | 0 | 0 | 129 | **n** | 0% | – |
| 3 The contestants | 682 | 38 | 0 | 154 | placeholder only (Figure 2) | 0% real | – |
| 4 Nested cross-validation | 281 | 43 | 0 | 146 | y (Figure 3) | 39% | 98% |
| 5 Selections and budget | 221 | 63 | 0 | 160 | y (Figure 4) | 29% | 98% |
| 6 Why two draws | 153 | 43 | 0 | 153 | y (Figure 5) | 32% | 98% |
| 7 Results of each draw | 98 | 92 | 110 | 98 | y (Figure 6), plus Table 1 | 31% | 99% |
| 8 What the runs carry | 434 | 77 | 262 | 160 | y (Figure 7), plus Tables 2–4 | **11%** | 93% |
| 9 What the pair can claim | 862 | 255 | 125 | 172 | y (Figures 8–11), plus Tables 5–6 | 34% | 80 / 84 / 84 / **74%** |
| 10 Limits | 356 | 0 | 139 | 125 | n, plus Table 7 | 0% | – |
| 11 Where everything is | 258 | 0 | 0 | 68 | n | 0% | – |
| References | 157 | 0 | 0 | 23 | n | – | – |

**Graphic as a share of its own figure block (the rest is key and caption):**

| Figure | share |
|---|---|
| 1 | **46%** |
| 3 | 83% |
| 4 | 70% |
| 5 | 70% |
| 6 | 76% |
| 7 | 67% |
| 8 | 70% |
| 9 | 67% |
| 10 | 71% |
| 11 | 58% |

- **Prose blocks over 60 words:** 32 across the page. Most are definitions, caveats or source pointers, where prose is the right form. The ones where a figure should replace prose are named in the findings below.
- **Captions over 60 words:**

| Figure | caption words |
|---|---|
| 1 | **130** (188 with its 7-entry key) |
| 6 | 86 |
| 7 | 71 |
| 10 | 68 |
| 11 | 64 |

## Findings

Each finding gives location · issue · severity · suggested fix · whether I verified it against a source.

**F1. Figure 1, section 1 · major**
- **Issue:** The figure that carries section 1's three claims gives its data the least space of any figure in the report.
  - The graphic is 273 px tall out of a 590 px figure block (46%).
  - The 7-entry, 3-column key (120 px) and the 130-word caption (179 px) together take more height than the picture.
  - The raster panel itself is about 135 px tall for 33 ROIs, about 4 px per ROI. At that size a 3-cell planted event, the point of "an event recruits only a few of the imaged cells", is hard to see.
  - The PNG has a blank strip of about 16% of its width baked in on the right: ink ends at x = 2971 of 3540 px. So the plot area uses about 77% of the column.
- **Suggested fix (a reflow, not a crop):**
  - Re-render the figure at the column's aspect with no right canvas, so the plot fills the full 1000 px.
  - Roughly double the raster's height, to about 10 px per ROI.
  - Collapse the key to one line under the lane. Most of its entries are already named by the lane's y-axis ("planted", "CoactDetect").
  - Cut the caption to what the figure shows. Move the draw-wide sentence ("across the second draw's held-out recordings CoactDetect averages 0.75 calls per recording there") into section 2's text, next to where the dense stretch is defined. It is a result about the whole draw, not about this picture.
- **Verified:** yes (rendered bounding boxes, and the PNG's inked extent).

**F2. Sections 2 and 3 in a row · major**
- **Issue:** Two methods sections run back to back with no real figure: about 1,120 prose words and about 2,700 px, three full screens at 1100×900.
- **Figure 2 is a deliberate placeholder,** and even when drawn it covers only the four nets. The coded half of section 3 and all of section 2 stay prose.
- **Named replacements:**
  - **Section 2, the "What one bench recording holds" list** becomes a recording-anatomy timeline. It is a 45-minute axis showing:
    - the 15 planted events at 120 s or more apart, sized or coloured by recruitment (10 / 6 / 3 cells);
    - the 6 distractors;
    - the 20–25 minute dense stretch, shaded;
    - the quiet and busy rates as a two-row label;
    - the empty twin at seed + 100,000 as a ghost row.

    Most of this ink already exists in Figure 1's lane, so an alternative is to label Figure 1 for this purpose and point the list at it.
  - **Section 3, the coded-detector bullets plus the 99-word origins paragraph,** becomes a detector table: detector · what it counts · null · window · merge grid top · origin and citation. This also absorbs the grid-top column now in Table 7's first row. Relocate the provenance into the table's origin column, not delete it.
  - **Section 3, the 154-word "The reference, sliding CoactDetect" paragraph,** becomes a schematic of the sliding window. It should show the 2 s count window, the 1 s guard on each side, the 120 s context, the z-threshold at α = 10⁻⁵, and the 8 s merge joining two calls. The binned-history sentence (30–36% of calls lost) moves to the section 11 sources or a footnote.
- **Verified:** yes (render, word counts).

**F3. Section 9, "At a matched merge": Table 5 plus the in-text list of eight gaps · major**
- **Issue:** The subsection's claim is how a gap changes as the merge changes.
  - That lives in a 16-row × 5-column number table.
  - The prose repeats eight of those numbers inline ("0.014, 0.015, 0.017, 0.017 … 0.011, 0.013, 0.015, 0.018").
  - Figure 10 shows only one merge (8 s), so no picture shows the trend.
- **Suggested fix:** A gap-versus-merge line chart.
  - x axis: as run, then 2, 4, 8 and 16 s.
  - y axis: net minus CoactDetect.
  - One line per net per draw, in the draw colours, with two panels: chosen on F1 alone, and chosen under the budget.
  - A zero line and the typical-move band (see F4).
- Keep Table 5 as an appendix or collapsible table, or in the companion JSON. Replace the inline number list with "Figure N: the gap narrows but stays below zero at every merge".
- **Verified:** yes.

**F4. Figures 8 and 9, the headline comparison · major**
- **Issue:** The report's central claim, that the closest net trails "by two to three times the typical move", compares two quantities that sit in two different figures on different x axes.
  - The typical move is in Figure 8; the gap is in Figure 9.
  - A reader has to carry 0.010 from one figure to the other.
- **Suggested fix:** Draw the between-draw move scale on Figure 9 (and Figure 10) as a shaded band of ±0.010 around zero, labelled "typical between-draw move (Figure 8)". Every dot outside the band then shows the claim.
- The same band on a small copy of Figure 9's budget panel, placed in or under the answer box, would give the lede a picture. At present the lede is 425 prose words with no figure.
- **Verified:** yes.

**F5. Section 8, Tables 2 and 3 · minor**
- **Issue:** The section's figure share of its height is 11%: three tables against one figure.
  - Table 2 ("146 of 432" and so on) is counts per net per draw that read as proportions.
  - Table 3 mixes two units in one column ("N of 20 refits" for nets, "N of 4 folds" for coded detectors).
- **Suggested fix:**
  - **Table 2** becomes grouped horizontal bars: percentage of inner fits that collapsed, by net, first and second draw side by side. Roughly 35%, 17%, 2% and 1.5%. The "a third / a sixth" in the text becomes visible.
  - **Table 3** becomes a dot strip: the share of held-out choices over the ceiling, nets and coded detectors in separate panels because their units differ.
  - **Table 4** is categorical (started at the top of the grid or moved there) and is right as a table.
  - **"Searches that found no admissible setting"** quotes 449–527 per hour against ceilings of 15–18. That would show at a glance as locust's rate marked on Figure 4's ceiling scale (log axis). If not drawn, the prose is acceptable.
- **Verified:** yes.

**F6. Section 9, "Where the as-run gap is": Table 6 · minor**
- **Issue:** The claim "comparable recall, lower precision, split by background" sits in a 2×2×2 number grid.
- **Suggested fix:** A precision–recall plane with iso-F1 curves.
  - One arrow per background per draw, from CoactDetect's point to chorus_gain_norm's point.
  - Arrows run left (lower precision) at both backgrounds, down at quiet and up at busy.
  - Keep the numbers as point labels or tooltips.
- **Verified:** yes.

**F7. Captions over 60 words: Figures 1, 6, 7, 10 and 11 · minor** (Figure 1 is covered in F1)
- **Figure 6 (86 words):** "The isolated low folds are the flagged ones of section 8" is worth keeping. The panel-by-panel list duplicates the panel labels printed under each panel and can go.
- **Figure 7 (71 words):** the threshold explanation ("whose threshold sits above everything those refits output") is argument. Move it to the section 8 text.
- **Figure 10 (68 words):** the leave-out rule is already stated in Table 5's note. Keep one copy.
- **Figure 11 (64 words):** "Counted from the runs' per-recording score files…" is provenance. Move it to section 11 or a footnote.
- **Verified:** yes (word counts from the render).

**F8. Figure widths in section 9 · minor**
- **Issue:** The graphics are left-aligned and do not fill the column.
  - Figure 8: 800 px, with 200 px empty on the right.
  - Figures 9 and 10: 840 px each, with 160 px empty.
  - Figure 11: 740 px, with 260 px (26%) empty on the right. Its graphic is 58% of its block.
  - None has more than 20% empty on both sides, so the incident pattern is absent. But the plots are narrower than the page offers, and Figure 9's x range beyond 0.00 is mostly unused.
- **Suggested fix:** Build these SVGs at the full 1000 px column width rather than a fixed internal width. For Figure 11, stretch the bar scale across the column. Layout policy only; any geometry bug is agent 10's to report.
- **Verified:** yes.

**F9. Section 4, the 146-word "inner fits" paragraph · minor**
- **Issue:** It restates what Figure 3 draws ("24 configurations × 3 training repeats × 6 fold pairs", "refit the winner at 5 training repeats").
- **Suggested fix:** Put the remaining numbers on Figure 3's labels (40–60 refits per net per draw, 10 recordings to train plus 2 to pick the threshold). Cut the paragraph to what the figure cannot show: the pooled-score rule and the refit mean.
- **Verified:** yes.

**F10. Section 6, a single 153-word paragraph · minor**
- **Issue:** It lists what differed between the rehearsal and this run: simulator, coded tuning, budget, fold defect and context cap. Section 9 relies on the same list ("four things changed at once").
- **Suggested fix:** A two-column table, rehearsal versus this replicate, one row per difference. Section 9 then points at it. Figure 5 (8 seed boxes) is low-information but cheap; I would not remove it.
- **Verified:** yes.

## Observation outside my scope (boundary with agent 10)

At 390 px wide every SVG figure scrolls sideways: 740–820 px of graphic in a 358 px viewport, so 44–48% is visible at once. The page says so ("Scroll sideways…"). Whether that is acceptable is a mechanical and responsive question for agent 10, not a density finding. I also saw that the swatches in Figure 3's caption render as near-empty pale boxes at 1100 px light theme. I am noting it for agent 10 only.

## Checked and found clean

- **Section 7** is the right mix: Figure 6 carries the fold-level result and Table 1 the means for lookup.
- **Figure 3 (nested cross-validation) and Figure 4 (budget)** are schematics where schematics belong, and they fill 98% of the column.
- **Figure 7** shows the collapse better than the text could.
- **Section 10 (limits) and Table 7** are right as prose and table. These are caveats, and the "relocate, don't delete" rule argues for keeping them on the page.
- **Section 11 and References** are pointers, where prose is right.
- **The "Tuning" subsection** is 4 numbers in about 60 words; prose is right.
- **No figure has more than 20% of its width empty on both sides.** The incident pattern of a narrow centred figure under full-width text is absent: the prose runs in a 653 px measure and the figures take the full 1000 px column.
- **Figure 2** is a declared placeholder and I did not flag it. It still leaves the coded half of section 3 without a picture (F2).
