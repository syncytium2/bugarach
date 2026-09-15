> **Public copy.** Lines that concern real treatment recordings are removed (12 here), per FOUNDATIONS §5, and machine paths are shortened to `<scratchpad>`, `<worktree>`, `<darkroom>` or `<home>` (sapper SAP004). Everything else is verbatim.

GRANT 9 ok — Read, Grep, Glob, Bash

**Role 9 (Show, Don't Tell): findings on `detector_review.html`**

I opened the built HTML in Playwright chromium at 1280 px and 400 px wide and measured it. I also looked at Figures 2, 8, 9, 10, 11, 12 and 15. I edited nothing.

**Thresholds I used.** These are conventions, not researched limits, adapted from slides to a scrolling page. The unit is one numbered section, plus each figure.
- Any text block over 60 words.
- A methods or results section with no figure.
- More than 1.5 screens (a 900 px viewport) with no figure. This stands in for "two or more prose-only slides in a row."
- A figure under 50% of the viewport width, or more than 20% empty margin on both sides.
- A caption over about 60 words, or taller than its image.
- I did not apply the 40-words-per-slide rule to whole sections of a long report. The counts are below for reference.

### Count table

"Body" and "caption" are word counts. "Fig height %" is the figures' share of the section's height at 1280 px.

| § | body | caption | table | largest block | figs | fig height % @1280 | fig height % @400 | width @1280 |
|---|---|---|---|---|---|---|---|---|
| 1 Problem | 189 | 117 | 0 | 117 (Fig 1 caption) | 1 | 42 | 13 | 89% vw |
| 2 Words | 418 | 0 | 0 | 45 | 0 | 0 | 0 | — |
| 3 Surrogates | 311 | 290 | 0 | **290 (Fig 2 caption)** | 1 | 55 | 18 | 89% |
| 4 Hand-written | 794 + ~340 in boxes | 507 | 227 | 112 (4.6 "What it does") | 6 | 43 | 11 | 89% |
| 5 Learned | 425 + 86 in box | 134 | 0 | 134 (Fig 9 caption) | 1 | 42 | 13 | 89% |
| 6 Simulator | 387 | 232 | 0 | **232 (Fig 10 caption)** | 1 | 49 | 14 | 89% |
| 7 Grading | 390 | 110 | 0 | 120 (7.2) | 1 | 44 | 13 | 89% |
| 8 Results | 607 | 118 + 81 | 176 | 118 (Fig 12 caption) | 1 | **23** | 6 | 89% |
| [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder] |
| 10 Side by side | 0 | 0 | **420** | table only | 0 | 0 | 0 | — |
| 11 Not covered | 150 | 0 | 0 | 51 | 0 | 0 | 0 | — |
| 12 Sources | 354 | 0 | 0 | 121 (one list item) | 0 | 0 | 0 | — |

**Figure width passes.** At 1280 px every image renders 1142 px wide: 89% of the viewport, 97% of the page column, with 70 px margins. Inside the PNGs the drawn content fills 87–90% of the width. So there is no fit-to-height shrink like the one in the incident.

**The prose column is the unused space.** Text runs 760 px wide, which leaves **450 px (35%) blank to its right** on every prose stretch. That gutter is room for small figures.

**Stretches with no figure** (at a 900 px screen height):
- [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder]
- Before Figure 2 (§2 glossary and the start of §3): **2.2 screens**.
- [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder]
- Before Figure 9: 1.5 screens.
- Before Figure 12: 1.4 screens.
- Before Figure 11: 1.2 screens.

**Captions.** 14 of 16 captions are over 60 words, and 7 are over 110. At 400 px, **9 of 16 captions are taller than their image**:

| Figure | image height | caption height |
|---|---|---|
| 1 | 149 px | 270 px |
| 2 | 421 px | 675 px |
| 4 | 147 px | 248 px |
| 10 | 336 px | 540 px |
| 12 | 207 px | 293 px |

Figures 3, 6, 7 and 8 also have captions taller than the image.

### Findings

Columns: location · issue · severity · suggested fix (the replacement figure is named) · could I verify it against a source.

1. **§4 comparison table (227 words) and the numbers repeated in 4.1–4.6 · High · verify: yes**
   - **Issue:** the key difference between detectors is time scale: how long a stretch each one counts over, and how long a stretch it judges chance against. That is written out in 18 table cells and repeated in the paragraphs.
   - **Replacement: a time-scale ladder.** One row per detector on a log time axis from 0.1 s to 45 min.
     - A dark bar for the counting window: 0.1 s for locust and SPIKE-synch, 1 s for rate+context and LoCo, 2 s for CoactDetect, 10 s for binned SCE.
     - A pale bar for the chance window: ±60 s, before and after 60 s, the whole period, the whole recording.
     - Add a tube row with its learned center (0.19–0.63 s) and surround (2.6–16.3 s) from §5.1.
   - The ladder shows at a glance why binned SCE and locust fire in the busy block and why binned SCE misses small events. Keep the table in an appendix. The paragraphs can then shrink to the one step each ladder row cannot show.

2. **§4, the 83-word paragraph "Each figure has the same layout…" · Medium · verify: yes**
   - **Replacement: a labeled key for Figure 3.** Callouts on the lane, raster, measure and bar rows, plus a glyph legend: ▼ green/red, ✕, ○.
   - The paragraph becomes one sentence pointing to it.

3. **4.6 and Figure 8 · Medium · verify: yes**
   - **Issue:** the caption makes the argument that a score "cannot exceed about 0.16." Meanwhile both score panels run 0–1 with every point below about 0.16, so about 85% of each panel's height is empty.
   - **Fix, in the figure:** draw a dashed line at 0.16 labeled "most a 6-of-33 event can score," and set the y-limits to about 0–0.3.
   - **Fix, in the text:** move the reasoning into the 4.6 body.
   - **Replacement for the 112-word "What it does":** a small schematic of two ROI rows. It shows the half-gap window, its 0.25 s cap, and a tight window for a busy cell next to a wide one for a quiet cell.

4. **4.2 and 4.5 mechanism text and captions · Low–Medium · verify: yes**
   - **4.5 locust (102 words):** replace the "switched on" description with a three-step inset: event ticks, then on-periods, then a count per frame.
   - **Relocate:** the 55-word CICADA provenance paragraph goes to §12. The Figure 4 caption sentence "We rebuilt the bar from its own numbers…" goes to notes.
   - **Figures 3, 6, 7:** move the counts ("crosses the bar 2 times," "19 bins," "15 times") into lane y-labels such as "rate+context · 2 false alarms." That is the repo's compact-labeling convention, and it takes each caption down to about 40 words.
   - **Figure 6:** move the mechanism sentence ("must compete with 10 seconds of background") to the 4.4 body.

5. **§3 and Figure 2 caption (290 words) · High · verify: yes**
   - **Issue:** the caption carries the section's whole argument: 0.35% against 0.58%, "a bar set from shuffles would therefore sit too low," "more cells line up than chance explains." Then a 97-word body paragraph ("Figure 2 makes two points") says it again.
   - **Fix, panel B:** draw a vertical guide at K = 6 in both the fast and slow panels, with the four percentages written where it crosses the curves.
   - **Fix, panel C:** put the counts in the lane labels: "bar from whole recording · 46 calls in block" and "bar from nearby 60 s · 0."
   - **Fix, caption:** cut it to panel labels plus one sentence. The interpretation lives in the body paragraph, which already exists.
   - **Consider:** splitting panel C into its own figure. It makes a different point: *where* the surrogate comes from, not *how* it is made.

6. **§5, 423 words of prose before Figure 9 (5.1 steps, variant bullets, 5.2 controls) · High · verify: yes**
   - **Replacement (a): a pipeline diagram.** Raster → widen (0.3 s) → brightness trace → four center/surround filter pairs → network → score → call level 0.972. Each box gets a thumbnail cut from Figure 9's window B.
   - **Replacement (b): a 2×2 design grid.** Rows: guard no/yes. Columns: subtract/divide. Add a controls row for trace and tiny. Each cell shows quiet F1 and busy-block calls per minute, taken from Table 1.
   - **Figure 9 caption (134 words):** move the false-alarm counts into lane labels ("tube · 3," "tube_guard · 7").

7. **§6 simulator bullets (176 words), the bench paragraph (86), and the Figure 10 caption (232) · High · verify: yes**
   - **Replacement for the four layers: a stacked build.** The same 5 minutes shown four times: background only, then + planted events, then + busy block, then + decoys. It could replace Figure 10A's first row.
   - **Replacement for "quiet and busy are the 25th and 75th percentiles of real baselines":** a histogram of the 84 real baseline rates with two labeled markers, quiet 5.2 mHz and busy 19 mHz.
   - [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder]
   - **Caption, in the figure:** write the D values on the line ends.
   - **Caption, relocate:** the verdict ("closer to real … but bunches more") goes to the "What the simulator does not copy" paragraph, which already says it. The matched-simulation method (84 recordings, 2,630 ROIs, flat against fitted) goes to notes.
   - **Keep on the page:** the "does not copy" caveat.

8. **§7, 390 words before Figure 11, which illustrates all three subsections · Medium–High · verify: yes**
   - **Reflow:** put 11A in 7.1 and 11B in 7.2, either inline or in the 450 px right gutter. Move 11C to §8, which is where "three flaws we can see in Figure 11C" is argued.
   - **Extend 11A** with the cases the text describes but the panel lacks:
     - a call on a decoy (▽), which counts as a false alarm;
     - a call inside the busy block, counted separately;
     - two calls near one event, paired closest-first.
   - **11B:** add three seed sub-rows for the learned detectors.
   - **7.3:** the six limits listed in prose are already the red dashes in Figure 12B. Replace the list with a pointer. Keep "set from its past measured behavior" on the page, because it is a rigor caveat.

9. **§8, figures are 23% of the section's height, and 526 words come before Figure 12 · High · verify: yes (Table 1)**
   - **Reflow:** move Figure 12 to the top of §8.
   - **Replacement (a) for "a busier background makes almost every detector worse":** a slope chart, one line per detector from quiet F1 to busy F1, replacing 12A's two separate panels. binned SCE's rise stands out.
   - **Replacement (b):** 12C shows recall at quiet only, yet the text quotes busy recall (CoactDetect 57% → 19%, tube 64% → 12%). Add busy as open markers.
   - **Replacement (c) for the 109-word "good scores come with calls where nothing was planted":** a scatter of F1 (x) against busy-block calls per minute (y, log scale), with each detector's limit as a tick. This is the trade-off in one panel.
   - **Replacement (d) for the 129-word flaws list:** label Figure 11C directly: "chosen at the end of the list" on binned SCE and LoCo, "F1 0.48–0.53 across the whole list" on SPIKE-synch, and a callout on rate+context's chosen ✕. Keep "a better value may lie past it" as a one-line caption note.
   - **Small fixes:** color the 12A dots by training seed. Move the speed sentence to a Table 1 footnote, since Table 1 already has a speed column.

10. [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder]
    - [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder]
    - **Fix:** put call counts in each lane's y-label ("locust · 266"), per the compact-labeling convention.
    - [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder]
    - [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder]
    - **Recording-choice paragraph (99 words):** replace with a strip plot of ROI counts per group, with the chosen median recording circled. It shows "picked by size."
    - **Run-setup paragraph (97 words):** move to notes and leave one sentence.
    - [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder]

11. **§10 table (420 words), no figure, part of the last 2.3 screens without a figure · Medium · verify: yes**
    - **Replacement: a report-card dot matrix.** One row per detector.
      - Measured columns, as sized or colored dots from Table 1: F1 quiet, F1 busy, recall at 10% of ROIs, busy-block calls ÷ limit, spread across training runs.
      - Mechanism columns, as ✓ marks: counts cells, bar follows nearby background, needs surrogates.
    - **Relocate:** the "good at / weak at" sentences go to an appendix. The §4–5 strengths and weaknesses boxes already hold most of them.

12. **§2 glossary (418 words, the longest stretch without a figure before Figure 2) · Medium · verify: yes**
    - Prose is right for definitions. The problem is placement: it is reference material sitting on the main reading path.
    - **Relocate:** to an appendix, a collapsible `<details>`, or the right gutter.
    - Point the hit / miss / false alarm and recall / precision entries at Figure 11A.

13. **§11 · No change · verify: yes**
    - Prose is right here. Statements of what is out of scope have no picture, and no block is over 51 words.

14. **§12 · Low · verify: yes**
    - Prose is right for citations. The one 121-word list item (CoactDetect and LoCo) should be split, one item per detector. That is a structure fix, not a figure.

15. **400 px layout, all figures · Medium · verify: yes (rendered)**
    - [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder]
    - **Layout fix:**
      - Link each image to its full-resolution PNG.
      - Or put figures in the same `.scroll` wrapper the tables use, with a minimum width of about 900 px.
      - Fold captions after their first sentence into `<details>` on narrow screens.
    - Boundary: measuring whether the text is still readable belongs to agent 10.

16. [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder]
    - The "In short" box is right as a short summary.
    - [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder]

### Things outside my role, for the main thread (not checked against sources)
- Figure 9A's x-axis runs ±8 s, but §5.1 gives tube's surround widths up to 16.3 s. The surround may be cut off (roles 1/10).
- Figure 12B's y-axis label is cut off ("…where nothing was plant") (agent 10).

### Files
- Measurements: `<scratchpad>\mb_scratch\role09\sections.json` and `...\role09\measure.json`
- Full-page render at 1280 px: `...\role09\full_1280.png`
