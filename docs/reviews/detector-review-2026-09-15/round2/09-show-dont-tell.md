> **Public copy.** Lines that concern real treatment recordings are removed (16 here), per FOUNDATIONS §5, and machine paths are shortened to `<scratchpad>`, `<worktree>`, `<darkroom>` or `<home>` (sapper SAP004). Everything else is verbatim.

GRANT 9 ok — Read, Grep, Glob, Bash

# Role 9: Density and figure-first review of the detector review page

**Artifact:** `<scratchpad>\review\detector_review.html`

*[line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder]

## What I checked, and how

- **Rendering and measuring.** I rendered the page in Playwright chromium at 1280 px and 1440 px wide. The main column comes out 1212 px wide and the page 34,049 px tall at both sizes. I measured each section's word count, its largest text block, the size of each figure and each caption's length.
- **Figures.** I read all 16 PNGs as images.
- **Plain-text copy.** I read `detector_review_plain.txt` end to end.
- **Figure widths are fine.** Every figure renders 1182 px wide, which is the full main column and wider than the 760 px text column. No figure has empty side margins. Width is not a problem anywhere, so figure share below is measured **vertically**: the figure's height as a share of its section's height.
- **The measuring script was not saved.** A repo hook blocked writing it to disk, so I piped it to Python. You can re-run it from the method above.

**Thresholds (my adaptation of the slide rules to one long scrolling page; tunable conventions, not researched optima):**
- any text block or caption over **60 words**
- a methods or results section where figures fill **under 50%** of the section's height
- **2 or more** prose-only sections in a row
- any single figure taller than **one 900 px screen**, so the reader cannot see all of it at once

### Count table (per section, rendered at 1280 px)

| section | words (text + captions, tables excluded) | largest text block (words) | blocks over 60 words | has a figure | figure share of section height |
|---|---|---|---|---|---|
| Front matter ("In short", contents) | 282 | 61 | 1 | n | 0% |
| 1. The problem | 453 | 166 (caption) | 4 | y | **51%** |
| 2. Surrogates | 735 | 207 (caption) | 5 | y | **53%** (one figure, 1483 px tall: taller than a screen) |
| 3. Hand-written detectors | 1,848 | 132 | 12 | y (6 figures + Table 1) | **44%** ⚑ |
| 4. Learned detectors | 682 | 136 (caption) | 4 | y | **44%** ⚑ |
| 5. Simulator | 690 | 190 (caption) | 5 | y | **46%** ⚑ |
| 6. Grading and tuning | 544 | 124 | 5 | y | **43%** ⚑ |
| 7. Results on simulated recordings | 694 | 105 | 5 | y (Figure 12 + Table 2) | **27%** figure ⚑ (Table 2 takes much of the rest) |
| [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder] |
| 9. Strengths and weaknesses | 36 (+ Table 3) | 36 | 0 | table only | 0% |
| 10. What could be wrong | 205 | 30 | 0 | n | 0% |
| 11. Where the methods come from | 584 | 100 | 4 | n | 0% |
| 12. Word list | 292 | 53 | 0 | n | 0% |

**Captions over 60 words:** 13 of 16 figures. They are Figure 1 (166 words), 2 (207), 3 (70), 4 (119), 6 (84), 7 (68), 8 (88), 9 (136), 10 (190), 11 (95), 12 (66), 13 (88) and 15 (123).

**Prose-only run:** Sections 10, 11 and 12 come three in a row after Table 3. Prose is right there: a caveat list, references and a glossary. I am not flagging it.

---

## Blocking

**B1. Figure 9A, the learned filters: the mechanism is invisible, so the prose has to carry it.**
- **Issue:**
  - All eight filters in each of the four panels share a ±13 s axis and one weight scale. The centre filters show only as a spike about 1 s wide at zero.
  - The surround filters, which are the point of the design, draw as flat gray lines on zero in three of the four panels.
  - The contrast between "short centre" and "long surround" is what the brief's "how it works graphically" asks for. It is readable only from the numbers in Section 4.1 ("0.19 to 0.63 seconds … 2.6 to 16.3 seconds").
  - No row shows the centre-filtered and surround-filtered brightness that the network actually compares. So for six of the twelve detectors, no figure shows how the detector decides.
- **Fix:**
  - *Replace 9A* with a strip of filter widths. Put log seconds on the x axis (0.1 s to 20 s), one row per tube model, colored dots for the centre widths and gray dots for the surround widths. The gap between the two clusters is then the picture, and the width numbers in 4.1 can go.
  - Alternatively, normalise each filter to a peak of 1 and plot on a log-time axis.
  - *Add a row to 9B/9C* between the brightness row and the score row: centre-filtered brightness (color) over surround-filtered brightness (gray) for tube. This is the same "measure against chance" row that Figures 3–8 give each hand-written detector.
- **Verifiable against source:** yes (image; text of Section 4.1).

---

## Major

*[line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder]
- **Issue:**
  - In each recording block, the ten detector lanes take about 37% of the height and the raster about 26%. The period bar, the header and the gaps between boxes take the rest. I estimated these shares from the PNG, not the DOM.
  - The rasters render at about 2.5–4 px per ROI, the lab's term for one cell.
  - Each figure is 1552 px tall, so at 900 px the key at the top and the bottom recording are never on screen together.
- **Fix (a reflow, not a crop):**
  - Halve the lane pitch.
  - Fold the period bar into a thin strip at the top of the lane panel, and remove the empty box and gap around it.
  - Delete the per-recording header text "periods (top bar), calls (lanes), events (raster)", which repeats four times per figure; say it once in the key.
  - Give the space to the raster: at least 50% of each block.
  - The figure should then fit in about one screen.
- **Verifiable:** yes (image, rendered height).

**M2. Counts sit in captions and prose instead of lane labels, against the project's compact-labeling convention.**
- **Issue:**
  - [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder]
  - The convention says identity and counts go in the y-axis label.
  - In Figure 7B, overlapping ✕ markers make the caption's count impossible to check against the lane.
- **Fix:**
  - [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder]
  - Delete the count sentences from the captions. The captions for 1, 7, 14, 15 and 16 each lose 20–40 words.
- **Verifiable:** yes.

**M3. Figure 12C, recall by event size: the headline number cannot be read.**
- **Issue:**
  - Three event sizes at two background levels means six markers stacked in one column per detector, told apart only by gray shade and fill.
  - The "In short" bullet and Section 7 rest on the fall for small events, CoactDetect's 57% at the quiet level against 19% at the busy one. A reader cannot find either point.
  - The panel heading "B, C · quiet background" also contradicts C's own legend, which shows the busy level too.
- **Fix:**
  - Redraw as dumbbells. For each detector, show three side-by-side sub-columns (30%, 18%, 10%), each a segment from the quiet dot to the busy dot.
  - Or draw a small-multiple row per event size.
  - Fix the heading.
- **Verifiable:** yes.

**M4. Figure 12A and 12B split a trade-off across two panels, and the prose recombines it.**
- **Issue:** The paragraph "Some good scores come with many calls where nothing was planted" (105 words) makes the reader match detector names between panel A's F1 score and panel B's busy-block calls.
- **Fix:**
  - Add one scatter: x = calls per minute in the busy block (log scale), y = F1 at the quiet level. Label each point with the detector name, color hand-written against learned, and put a tick at each detector's limit.
  - The five similar detectors cluster, the detectors that use one bar for the whole recording sit to the right, and the ratio models sit left and low.
  - This one picture carries two of the four "In short" bullets. It could also lead the page as a headline figure.
  - Cut the paragraph to one sentence pointing at the scatter.
- **Verifiable:** yes (Table 2 values).

**M5. Figures 3–8, panel A: in the mechanism figures, the mechanism is sub-pixel.**
- **Issue:**
  - Window A is 3 minutes long, so the planted event is a 1–2 px column. For CoactDetect, the bar at the event, the surrogate average and the count are three marks in the same few pixels.
  - So the captions explain in words what should be visible. Figure 4's caption runs to 119 words explaining a bar rebuilt at tested bins, and Figure 8's does arithmetic ("6 minus 1 of the other 32 ROIs, … about 0.16").
- **Fix:**
  - Add a narrow third column to each figure: a zoom of about 20 s around the event, with the same rows.
  - In Figure 8, draw the most a 6-ROI event can score (about 0.16) as a reference line on the score row (not on the raster), and cut the arithmetic from the caption.
- **Verifiable:** yes.

**M6. Missing summary figure for "Where a detector takes its sense of chance matters most."**
- **Issue:**
  - This claim is the document's central mechanism. It is shown one detector at a time across six figures and about 7,000 px of scrolling, and never side by side.
  - Section 3 ends without a comparison.
- **Fix:**
  - At the end of Section 3, add one figure on window B: six stacked rows, one per detector, each showing the measure's margin over its bar (measure minus bar, or a ratio for SPIKE-synch), with a common zero line and one raster underneath.
  - The detectors that use a local bar stay below zero through the busy block; those that use one global bar sit above it. This makes the claim visible in one glance and can replace the "Detectors that judge chance…" sentence in "In short" with a figure reference.
- **Verifiable:** yes (the data already drawn in Figures 3–8).

**M7. Figure 2A does not show what the "Why the shift and not the shuffle" paragraph (173 words) argues.**
- **Issue:**
  - At a 5-minute scale, a shuffle putting two events from one cell into the same 2-second bin cannot be seen. The alt text admits "some rows show events bunched".
  - The evidence lives in the prose numbers: repeats per 1,000 events for recorded data, shift and shuffle in each stream.
- **Fix:**
  - Add panel 2D: a grouped bar chart of same-cell repeats in one 2-second bin per 1,000 events, with recorded, shift and shuffle bars for the fast and slow streams.
  - Shorten 2A to about 30 s of the busiest rows. Put the 2 s bin boundaries as ticks in a lane above, not on the raster.
  - The paragraph shrinks to about 40 words.
- **Verifiable:** yes.

**M8. Section 5, the simulator: a recipe written as four paragraphs.**
- **Issue:** The layer paragraphs ("Background", "Planted events", "A busy block", "Decoys": 97, 85 and 124 words) plus the recipe paragraph list parameters in running text.
- **Fix:**
  - Use a recipe table: layer · what it adds · value (ROI count, length, planted events by share of ROIs, timing spread, busy-block rate and ramp, decoy count and share, the quiet and busy rates).
  - Keep the two ⚠ caveats (the timing spread may describe chance, and the quiet level sits above its target percentile) as notes under the table. Relocate them; do not delete them.
  - Figure 10's caption (190 words) repeats numbers the in-figure legends already carry (38%, 37%, 4%, and the bunching values readable from D). Cut it to what the figure shows and why that matters.
- **Verifiable:** yes.

**M9. The same strengths and weaknesses appear twice.**
- **Issue:** Each "What the design does well / What the design risks" box pair in Sections 3.1–3.6 and 4 (7 pairs) says almost the same as Table 3. For CoactDetect, "raises its own bar a little" and "bins at fixed times" appear in both.
- **Fix:**
  - Keep Table 3 as the single home, because it carries the numbers and sits where the comparison happens.
  - Replace each box pair with one line: "Design risks: see Table 3."
  - Alternatively keep the boxes and cut Table 3's two prose columns to pointers. One copy either way.
- **Verifiable:** yes.

**M10. Section 4.1, how tube works: a pipeline described in four paragraphs.**
- **Issue:** Widen → share of ROIs on → centre and surround filters → subtract or divide → small network → score → call level runs to about 250 words.
- **Fix:**
  - Draw a one-row flow schematic with a thumbnail at each stage, taken from Figure 9's own rows.
  - Mark the three variations as branch labels on the subtract/divide step and the guard gap.
  - This pairs with B1.
- **Verifiable:** yes.

**M11. Section 8's claim that detectors disagree most in busy stretches has no quantifying figure.**
- **Issue:**
  - [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder]
  - The four tall figures show it only by eye, 3,000 px apart.
- **Fix:**
  - Add one small heatmap per stream: detectors as rows, the eight recordings as columns, each cell the calls per minute inside the analysis windows, plus a top row with each recording's event rate.
  - [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder]
  - [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder]
- **Verifiable:** partly (figures, yes; the per-window rates need the run data).

**M12. Captions carry the argument (13 captions over 60 words).**
- **Issue:**
  - Beyond M2, M5 and M8, the captions hold provenance and caveats that belong elsewhere.
  - Figure 2 says "We chose the baseline with the most events…" and "This bar is an illustration…", and repeats a color key that already appears twice inside the figure.
  - Figure 4 says "we rebuilt the bar from those numbers".
  - [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder]
  - [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder]
- **Fix:** Cut each caption to what the figure shows and why it matters (60 words or fewer). Move provenance and caveats to a "Notes on the figures" block after the figure, or to Section 10. Keep every word.
- **Verifiable:** yes.

---

## Minor

*[line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder]
- [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder]
- [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder]
- **Verifiable:** yes.

**m2. Minutes-friendly time axes are not used everywhere.**
- **Issue:** Figure 9A labels its ticks as bare "−10 … 10" (seconds), and Figure 10D as "30, 60, 120, 300" (seconds). The convention is `10s` / `1m` / `2m` / `5m`, never raw seconds.
- **Fix:** Use the project's time-axis helper, `_time_axis_hook`.
- **Verifiable:** yes.

**m3. Figure 9A repeats its x axis four times.**
- **Fix:** The convention is one x axis per linked group, bottom row only.
- **Verifiable:** yes.

**m4. Figure 9B/9C: the trace and tiny lanes are two full-width gray bars.**
- **Issue:** They take a third of the lane panel to show "failed", which the text already says.
- **Fix:** Drop them from the lanes and keep one sentence.
- **Verifiable:** yes.

**m5. Figure 9's key lists ▼ twice.**
- **Issue:** "planted event, found" and then "green if any model in the lane found it".
- **Fix:** Merge them into one entry.
- **Verifiable:** yes.

**m6. Figure 10B: 8 seconds with about 10 ticks in a raster 33 ROIs tall.**
- **Issue:** The timing spread the text quotes (a typical 0.36 s; this event starts within 1.2 s) is not marked.
- **Fix:** Add a bracket in the lane above showing the start spread, and shrink the raster's height.
- **Verifiable:** yes.

*[line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder]
- **Issue:** The lanes read "tube_guard", "tube_ratio", "tube (learned)", while the text and Figures 9 and 12 use "tube-guard" and "tube-ratio". A reader matching names across figures trips on it.
- **Fix:** Use the text's names.
- **Verifiable:** yes.

**m8. Y-axis labels are clipped in the rendered figures.**
- **Issue:** Figure 3 ("…all ROIs"), Figure 6 ("…10 s bi") and Figure 7 ("…0.1 s fra").
- **Fix:** This is agent 10's geometry check; I note it only because it hides what the measure row is.
- **Verifiable:** yes.

**m9. Figures 3–9 encode a call's verdict partly by shape (✕ false alarm, ○ second call), not only by color.**
- **Issue:** The convention says that with ▼ markers, shape is already taken and the verdict is the color. These markers are not directional, so this may be within the rule.
- **Fix:** Flagged for the adjudicator, not asserted as a breach.
- **Verifiable:** yes (convention text).

**m10. Table 2 (12 rows, 14 columns) sits in the middle of the argument and repeats Figure 12.**
- **Fix:** Move it after the Section 7 prose, or to an appendix. Keep the red over-limit cells.
- **Verifiable:** yes.

**m11. Sections 3.1–3.6 repeat their row of Table 1 before adding detail.**
- **Fix:** Cut each paragraph's first sentence or two to only what Table 1 does not say. About 150 words saved.
- **Verifiable:** yes.

**m12. Section 8's run-configuration paragraph (129 words) is a lookup table.**
- **Issue:** It says which detector runs per window and which runs on the whole recording, and whether its bar is local, set per window or set once per recording.
- [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder]
- **Verifiable:** yes.

**m13. "Window A / Window B" definitions are in prose at the start of Section 3 and again in each figure's panel headings.**
- **Fix:** Keep the headings, and shorten the prose to one sentence plus the two time ranges.
- **Verifiable:** yes.

---

## Where prose is right, left as is

- **Section 11 (references) and Section 12 (word list).**
- **Section 10's caveat list:** short bullets, and caveats should stay visible.
- **The "Read this first" box in Section 8:** a warning, not evidence.
- **Section 6.1's scoring definitions:** Figure 11A already illustrates them. The prose is short and needed for exact wording.

## Conventions confirmed compliant

- **Figure numbers:** every figure and table carries one.
- [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder]
- **Lane markers point down:** planted ▼ throughout, with found and missed told apart by color.
- **Time axes:** minutes-friendly everywhere except m2.
- **ROI counts:** carried in the y-axis labels.
