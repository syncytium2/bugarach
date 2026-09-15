GRANT 9 MISMATCH — missing Grep, Glob; holds no forbidden tools (holds Read, Bash)

The missing Grep and Glob did not limit this review: the artifact is one file plus six PNGs, and Read and Bash covered all of them. No file in the repo was edited, and nothing was written to the scratch folder.

**Artifact:** `<worktree>/docs/learned/rigid_shift_look/README.md`, its six figures, and the three JSON result files they were drawn from (`leak_count.json`, `larger-displacements/leak_count.json`, and the Cossart and destruction tables beside them).

**Thresholds** (project conventions, not researched optima):
- More than 40 words in a section.
- Any text block over 60 words.
- A results or methods section with no figure.
- Two or more prose-only sections in a row.
- Figure share under 50%.

A Markdown note is denser than a slide by nature, so I flag the word counts only where they hide a missing picture.

**How figure share was measured.** I did not render the page on GitHub. I assumed a content width of about 900 px, 16 px text on 24 px lines, about 15 words per line and 16 px between blocks. Every figure is at least 1600 px wide, so each one scales to the full 900 px, and their heights follow from the PNG sizes. The share figures are estimates, marked "no" under verification.

## Count table (one row per section)

| Section | Words | Largest block | Figure? | Figure share of rendered height |
|---|---|---|---|---|
| Title and provenance quote | 70 | 70 | n | 0% |
| The answer, short | 146 | 75 | n | 0% |
| What was measured | 288 | 112 (the Leak bullet) | n | 0% |
| The displacements first planned | 210 | 42 | y (Figures 1, 2) | about 73% (1412 px of figure against about 530 px of text) |
| Larger displacements, the follow-up | 131 | 31 | y (Figures 3, 4) | about 78% |
| The Cossart folder | 433 | 103 (the intro paragraph; the K-scaling paragraph is 95) | y (Figures 5, 6) | **about 39%** (585 px of figure against about 900 px of text) |
| What this cannot say | 152 | 57 | n | 0% |
| The decision this sets up for Tony | 48 | 29 | n | 0% |

**Measured inside the PNGs:**
- The destruction figures (Figures 2, 4 and 6) are 1840 px wide. Their legend strip, right of the last panel, takes **19.3% of the width but holds only 2.4–3.1% ink**.
- In the leak-and-count figures (Figures 1, 3 and 5), each column of count panels gets about 39% of the width, the same as the leak panels.

**Page-level flags:**
- The page opens with three prose-only sections in a row (about 500 words, roughly 1000 px) before the first figure.
- It closes with two more.

## Findings

**1. The note's answer has no figure of its own**
- **Location:** "The answer, short" (146 words, no figure) and "The decision this sets up for Tony".
- **Issue:** The finding is a trade-off: a shift must be large enough to remove planted coordination but small enough not to leak.
  - The two halves are in different figures. Leak is in Figures 1, 3 and 5; destruction is in Figures 2, 4 and 6.
  - They come from two runs with different displacement grids, plus a third dataset.
  - "Fast works at 10–20 s", "slow has a narrow window near 11 s" and "Cossart only near 5 s" can only be pieced together by reading six figures side by side. No figure shows why a shift of about 10 s is needed.
  - The project rule "Show the picture — don't describe it" fails at the headline.
- **Severity:** major.
- **Replacement figure:** a trade-off summary at the top of the note, a 2×3 grid.
  - **Columns:** lab fast, lab slow (2 s bin), Cossart.
  - **x-axis:** displacement *J* on a log scale, 1.4–45 s.
  - **Top row:** rigid-shift leak accuracy, with its range over mice and the dashed line at 0.55.
  - **Bottom row:** retained share for the hardest case, with the dashed line at 0.25. That case is K = 3 at 50% participation in the lab data, and K = 55 at 50% on Cossart.
  - **Shading:** the range of *J* where both criteria pass, shaded behind both rows. The shaded band is the answer.
  - The two paragraphs of "The answer, short" then become one assertion sentence each, pointing at a column.
- **Verified against a source:** yes. Every value needed is in `leak_count.json`, `larger-displacements/leak_count.json`, the three destruction-table JSON files and the Cossart JSON files.

**2. The per-group leak claim has no figure, and the data do not support its wording**
- **Location:** "The answer, short" ("almost entirely in the DI group (0.62–0.68)") and the Figure 3 caption ("By group at 44.8 s: DI 0.675, MALE 0.593…").
- **Issue:** Group accuracies are stated in prose and appear in no figure. Plotted, they would contradict "almost entirely". Computed from `by_group` in `larger-displacements/leak_count.json` (window pairs above chance, weighted by pairs):
  - **At 44.8 s:** DI accounts for about 56% of the leak and MALE about 38%. MALE alone reads 0.593, which is past the 0.55 line.
  - **At 22.4 s:** DI accounts for about 49%, MALE about 23% and OVX about 20%.
  - The `by_group` entries also hold only `accuracy` and `n_pairs`, with no interval. The DI numbers therefore carry no uncertainty, while every pooled number carries two.
- **Severity:** major. The wording itself belongs to the claims and rigor roles; this role owns the fact that the claim has no figure.
- **Replacement figure:** a small-multiples dot plot of leak accuracy against *J*.
  - One panel per group (DI, MALE, ORX, OVX).
  - Slow stream in the main panels, fast stream as a flat contrast.
  - Pooled accuracy as a grey reference line, and the dashed line at 0.55.
  - Group-level resampled intervals need computing before this is drawn.
- **Verified against a source:** yes (`larger-displacements/leak_count.json`, `by_group`).

**3. The K-scaling argument is arithmetic about a picture**
- **Location:** the Cossart section, the paragraph "The K scaling makes removal easy" (95 words) and the intro paragraph (103 words). The section's figure share is about 39%.
- **Issue:** "283 ROIs shifted ±5 s spread over 10 s, about 28 ROIs per 1 s bin, below K = 55" is a curve described in words. The consequence, that a small K would need a larger shift and the larger shift is where the leak starts, is exactly what the reader needs to see.
- **Severity:** major.
- **Replacement figure:** an analytic plot, exact for a uniform shift.
  - **x-axis:** *J*.
  - **y-axis:** expected co-active ROIs per 1 s bin, N/(2*J*).
  - **Curves:** N = 283 (50% of 566 ROIs) and N = 113 (20%).
  - **Horizontal lines:** K = 55, 73, 110 and 146, plus a band for the lab's K = 3–8 marked "not measured on Cossart".
  - **Shading:** the *J* range where the Cossart leak crosses 0.55 (from 10 s), taken from `cossart/leak_count.json`.
- **Relocate, don't delete:**
  - The recording geometry (12,634 frames at a 0.118 s frame interval, 566 ROIs, 59 recordings from 32 mice, 1,257 window pairs) goes into a one-row table or "What was measured".
  - The sentence saying the screen's review could not register removal goes into a methods note or a collapsed `<details>` block.
  - The "Reading" paragraph keeps only its assertion.
- **Verified against a source:** yes for the arithmetic (283/10 ≈ 28 ROIs per bin). The shaded leak range was not re-extracted.

**4. The displacement trend is split across two figure pairs**
- **Location:** "Larger displacements, the follow-up": Figures 3 and 4 against Figures 1 and 2.
- **Issue:**
  - The follow-up exists to show how leak and removal change as *J* grows. That trend is cut at *J* = 5 s, which appears in both runs, and spread over two leak figures and two destruction figures with different x grids.
  - No single axis shows slow-stream leak rising from 0.49 to 0.56, or retained share falling from 0.87 to 0.04.
  - The layout repeats a full subsection to make a point one axis would make.
- **Severity:** major.
- **Fix (a reflow):**
  - Merge the two runs into one leak-and-count figure, with *J* from 1.6–40 s (fast) and 1.4–44.8 s (slow) on a log x-axis.
  - Merge them into one destruction figure the same way.
  - The provenance ("run the same night after seeing the first run") goes into a one-line caption footnote. It is already a caveat under "What this cannot say".
- **Verified against a source:** yes (both JSON files and all four PNGs viewed).

**5. The destruction figures run along K while their captions read along J**
- **Location:** Figures 2, 4 and 6 and their "What it shows" lines.
- **Issue:**
  - The panels put K on the x-axis, with one line per displacement. Every caption claim runs across displacements instead, for example "0.41 → 0.16 → 0.07 → 0.04 across 5, 10, 20 and 40 s".
  - In Figure 4, the larger-displacement destruction figure, the 10, 20 and 40 s lines share one blue and differ only in dash pattern. They pile up between 0 and 0.07, so the stated sequence cannot be read off.
  - In Figure 6, the Cossart destruction figure, the 5–40 s lines lie exactly on the homogeneous-resample control at 0 and cannot be seen. The caption has to say so in words.
  - Also in Figure 6, K = 146 at 20% participation is a blank x position explained only in the caption.
- **Severity:** major.
- **Replacement figure:** retained share against *J* on a log x-axis, one line per K in an ordered colour ramp, panels by stream/bin × participation. Alternatively, a K × *J* heatmap with the 0.25 contour drawn. For the K = 146, 20% case, put an explicit "event smaller than K" marker in the plot instead of the caption sentence.
- **Verified against a source:** yes (PNGs viewed).

**6. The methods section has no schematic**
- **Location:** "What was measured" (288 words; the Leak bullet alone is 112 words).
- **Issue:** The difference between rigid shift, where each ROI's whole train slides by one offset, and uniform dither, where each onset moves on its own, is what the whole leak test rests on. The reader has to imagine it. The planted-event and K-threshold idea behind the destruction test is also prose only.
- **Severity:** major.
- **Replacement figure:** a schematic with three stacked black-and-white rasters of about 6 ROIs over one short window:
  - the real recording;
  - the same window after rigid shift, with visibly whole rows sliding;
  - the same window after uniform dither.

  Beside it, a destruction panel: a planted event's binned co-active count before and after the shift, against a K line.
  - Following the "nothing drawn on the raster" rule, labels go in the y-axis labels or a lane above, never on the marks.
  - `bugarach.ui.diagnostic.raster_panel` already draws the rasters.
- **Relocate:** the edge-band exclusion and its reason, resampling over mice and slices, and the control definitions go into a `<details>` block under the schematic.
- **Verified against a source:** no. This is a judgment call; no source to check.

**7. The legend strip wastes a fifth of each destruction figure**
- **Location:** Figures 2, 4 and 6.
- **Issue:**
  - The legend strip takes 19.3% of the width but holds 2.4–3.1% ink, and it is repeated three times per figure even though every row's legend is identical apart from the displacement values.
  - At about 900 px of content width, the 1840 px PNG shrinks to about 0.49×, so legend text renders around 9 px.
  - Agent 10 owns the legibility measurement. This role owns the layout fix.
- **Severity:** minor.
- **Fix (a reflow):** one shared legend in a single row above the panel grid, giving the panels the full width. Lab fast and lab slow use different displacement values, so each row keeps its own values in the row label.
- **Verified against a source:** yes (ink measured on the PNGs).

**8. The leak panels give the space to the reference, not the result**
- **Location:** Figures 1, 3 and 5.
- **Issue:**
  - The uniform-dither reference sets the y-range, so the result being tested, rigid shift and its crossing of the 0.55 line, sits in the bottom third of the axis. In Figure 5, the Cossart leak figure, dither at 0.98–0.99 pushes rigid shift's 0.49–0.60 into about a third of the panel height.
  - Meanwhile the count panels, whose result is a null (0.4% change or less), get as much width as the leak panels (about 39% each).
- **Severity:** minor.
- **Fix (a reflow):**
  - Give the leak panels about two-thirds of the width and shrink the count panels to a narrow strip. Alternatively, move counts to a caption row: "within ±0.4% at every displacement; control −4.5% to −4.8%".
  - Zoom the leak axis to about 0.45–0.65 and show dither with a broken axis or a labelled arrow at the top edge.
- **Verified against a source:** yes (PNGs viewed; widths measured).

**9. Places where prose is right**
- **Location:** the title's provenance quote, "What this cannot say", and "The decision this sets up for Tony".
- **Assessment:** these are provenance, caveats and questions to Tony, and prose is the right form. The caveat on real onset jitter of about 1 s could point to the interface2 measurement if a figure of it exists, but it needs no new figure here. The captions for Figures 1–4 stay at 42 words or fewer per bullet and state what each figure shows.
- **Severity:** none. Recorded so the pass is traceable.
- **Verified against a source:** no. Judgment only.

**Things this role did not check:** whether the numbers in the note match the JSON files, apart from the group split in item 2; the wording of claims; axis units and figure numbering. Those belong to the other roles.
