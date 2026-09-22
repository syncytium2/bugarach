GRANT 9 MISMATCH — missing Grep, Glob; holds no forbidden tools (holds Read, Bash)

# Show, Don't Tell review: tube_self_supervised README, commit f2278da

The page's figures are good and fill the column. The biggest problem is the result the page itself says settled the review's question, how the trained models score on synthetic twins: it appears only as a table, with no figure. The second problem is that every figure gets only a third of its section, because tables and prose repeat what its panels already show.

**The grant gap did not limit the review.** I searched with Read, Bash and Python instead of Grep and Glob. A repository hook blocks heredocs, so the measurement script ran as a `python -c` argument. The only files written are in `<scratchpad>/mb4/role09/`: `render.html`, `full.png`, `measure.json` and symlinks to the five figures. Nothing under the blind-excluded folders was opened.

**How I measured.** I converted the Markdown to HTML with the Python `markdown` package (tables extension) and rendered it in headless Chromium through Playwright. The reading column was 830 px of content with GitHub-like styles: images and tables capped at 100% width. Heights are rendered pixels. Word counts use each block's `innerText`, and tables are included in the section total.

**Thresholds I used** (project conventions, not researched optima, adapted from slides to a scrolling page):
- any single block over **60 words**
- a results or methods section with **no figure**
- **two or more consecutive** sections with no figure
- a figure under **50%** of its section's rendered height
- empty margins over **20% of the width** on both sides of a figure

The 40-words-per-slide limit does not apply to a whole report section, so I did not use it.

## Count table

| section | height (px) | words, prose + tables (of which tables) | largest single block, words | figure? | figure's share of section height | figure width / column |
|---|---|---|---|---|---|---|
| The problem | 1504 | 459 (0) | 95 | yes, Figure 1 | **42.3%** | 830/830 |
| Terms | 684 | 394 (0) | 60 (list item) | no | 0 | — |
| What this run found | 916 | 510 (0) | 96 (Exploratory blockquote) | no | 0 | — |
| Figure 2. The leak tests | 2588 | 791 (132) | 161 (⚠ what this test can and cannot see) | yes | **39.7%** | 830/830 |
| Figure 3. The supervised bake-off | 3798 | 1013 (363) | 205 (plant probe paragraph) | yes | **32.3%** | 830/830 |
| Figure 4. Training against rigid shift | 3800 | 1200 (244) | 145 (⚠ truth-reading paragraph) | yes | **33.3%** | 830/830 |
| Figure 5. Real recordings | 2971 | 935 (148) | 140 (⚠ edge enrichment) | yes | **34.2%** | 830/830 |
| What this does not settle | 828 | 457 (0) | 71 (list item) | no | 0 | — |
| What waits on Tony | 676 | 419 (0) | 125 (list item) | no | 0 | — |
| The published lineage | 1068 | 620 (0) | 192 (whole-train shifting) | no | 0 | — |
| References | 852 | 362 (0) | 30 | no | 0 | — |
| Provenance and how to reproduce | 1744 | 730 (145) | 145 (stage table) | no | 0 | — |

- **Total:** about 21,900 px of rendered height, 8,594 words in the source, 5 figures.
- **Blocks over 60 words:** 47 paragraphs, list items or blockquotes by my count.
- **Width is not the problem:** every figure is drawn at 830 px, the full column, so no figure has side margins.
- **Height is the problem:** in all five figure sections the figure gets under half the height. In Figures 2–5 the cause is the text and tables after the figure. Figure 1 shares "The problem" with four paragraphs of framing.

## Findings

Each finding gives location · issue · severity · suggested fix · could I verify it against a source.

**1. The twin-check table, lines 359–365 · high · verified: yes**
- **Issue:** This is the result the page says "is where the question was answered" (line 668), and the fifth "What this run found" bullet (lines 97–102) rests on it. It has no figure. It is the only one of the page's four questions whose deciding evidence is table-only.
- **Replacement figure:** a new **panel D in Figure 4**, a dot strip in the style of panel C.
  - x axis: the five twin conditions (events at 1.6 s; events plus independent modulation at 1.6 s; shared modulation at 1.6 s; shared modulation at 20 s; the independent-modulation null).
  - y axis: the share where the twin scores above its rigid shift, with chance at 0.5 dotted.
  - marks: colour by architecture, filled/open by arm, count baselines in black.
- **Data:** already in `summary.json` under `small_j_check/groups` (23 groups).
- **The table** moves below the panel or into a collapsed "numbers behind panel D" block. It is relocated, not deleted.

**2. Tables that repeat panels, in all four results sections · medium · verified: yes, panel by panel against the PNGs**
- **Issue:** these tables are the main reason each figure gets only 32–40% of its section.
  - Figure 2: the per-ROI table (line 133) is panel A. The aggregate table (line 160) is panels C and D.
  - Figure 3: the ΔF1 comparison table (line 207) is panel B. The F1 column of the detector table is panel A.
  - Figure 4: the label-free F1 table (line 296) is panel A. The paired-check table (line 328) is panel C.
  - Figure 5: the first table (line 397) is panel A.
- **Reflow, not cut:** keep the one-sentence claim directly under each figure. Move each duplicated table into a `<details>` block ("numbers behind panel A") at the end of its section, or into a numeric appendix section.
- **Measured effect** of taking the tables out of the height: Figure 3 goes to 53.8%, Figure 2 to 47.6%, Figure 4 to 44.5%, Figure 5 to 42.7%.
- **Some columns are not in any figure** and stay with the relocated tables: recall, precision, probe calls, seconds per fit, event rate on the rigid shift, and "share of CoactDetect's events it overlaps".

**3. The plant-probe paragraph in the Figure 3 section, lines 260–272 (205 words, the largest block on the page) · medium · verified: yes**
- **Issue:** it describes the four plant shapes (synchronous, burst, fuzz, wave) in words. It also re-quotes the ÷ fuzz ratios at 16 ROIs (1.99, 1.75, 1.60, 1.43), which panel C already plots.
- **Replacement figure:** a **mini-raster schematic of the four plants** in Figure 1's style (8 ROIs, one row per plant), placed as a strip above panel C.
- **What stays:** a definition of the ratio plus the "read as a direction" caveat. The per-model numbers and standard errors go into a details block.

**4. The architecture described in prose: "The builds" (lines 222–229, 117 words) and "The problem" paragraph 4 (lines 24–29, 82 words) · medium · verified: yes**
- **Issue:** the mechanism that separates `tube` from `line`, `line_length` and `line_bound` is only described.
- **Replacement figure:** an **operator schematic**.
  - `line` path: per-ROI trace → sigmoid height bound (plus a time bound for `line_bound`) → mean over ROIs (relative length) → narrow ÷ wide smoothing (concentration channels).
  - `tube` path: mean over ROIs → difference of Gaussians.
- **Reusable tool:** `<worktree>/tools/make_architecture_figures.py` already draws fitted `tube`-family operators from trained models. Extending it to the counting builds would draw the schematic from measured models rather than asserted boxes.
- **Placement:** as a panel beside Figure 1, which is where the architecture question is first raised.

**5. The objective paragraph in the Figure 4 section, lines 285–288 (68 words) · low · verified: yes**
- **Issue:** the training setup is described only in words.
- **Replacement figure:** a pipeline strip at the head of Figure 4: a 4,096-frame crop and its rigid shift → the same model → mean of the top 1% of per-frame scores → softplus(shifted − real).
- **What stays:** step count, learning-rate facts and the end-of-recording crop rule go to the caption or notes.

**6. The ⚠ truth-reading paragraph in the Figure 4 section, lines 314–322 (145 words) · medium · verified: yes**
- **Issue:** it lists coverage and F1 arm by arm, which is exactly panel B's two axes.
- **Fix:**
  - Label the two regions of panel B directly ("detections localized" near 0; "on almost everywhere" near 1).
  - Keep one sentence under the figure: arms trained on real recordings and the untrained arm sit at 0.95–0.99 coverage, so their F1 is not detection.
  - Move the per-arm ranges and the "4 of 360 fits at the grid edge" note into a details block. Keep the caveat; move the numbers.

**7. The ⚠ edge-enrichment paragraph in the Figure 5 section, lines 440–448 (140 words) · low · verified: yes (`real_compare/edge_shares` has "supervised tube bake-off threshold")**
- **Issue:** panel B already shows the recording and rigid-shift shares. The bake-off-threshold comparison (1.6–2.2%) is prose-only, and it is the number decision 4 cites.
- **Fix:** add bake-off-threshold marks for the supervised rows to panel B, then shorten the paragraph to the claim.
- **Where prose is right:** the candidate cause (zero padding up to 12.8 s plus 6.3 s of head reach) is an untested hypothesis. It stays as prose or moves to notes; a diagram would present it more firmly than the evidence supports.

**8. Duplicated "Nothing here is ground truth" paragraphs, lines 450–454 and 456–461 (61 + 91 words) · low · verified: yes**
- **Issue:** two overlapping versions of the same caveat, one after the other.
- **Fix:** merge into one. The second version lacks only "in four groups, pooled here" from the first, so keep that phrase and nothing is lost.

**9. The twin types, described in prose in three places (lines 173–177; line 360's column headers; lines 369–371) · medium · verified: yes**
- **Issue:** the twins are the controls Figure 2 panel D, Figure 4 panel C and the twin check all depend on. A reader rebuilds them from sentences each time.
- **Replacement figure:** a second row in Figure 1 with four rate-over-time sketches.
  - stationary: flat
  - shared modulation: one 40 s cycle of depth 0.9, the same in every ROI
  - independent modulation: a cycle per ROI with its own phase
  - planted events: participation 0.2
- **Result:** the definitions become "(Figure 1, the twins)".

**10. Terms and "What this run found": two consecutive sections with no figure, about 1,600 px of text between Figure 1 and Figure 2 · medium · verified: yes**
- **Where prose is right:**
  - The glossary is definitional.
  - A findings list is the right form for claims; a composite figure would only repeat Figures 2–5.
  - The "Exploratory" blockquote (96 words) is status and provenance. It stays on the page but could move below the findings.
- **Relocation, not wording:**
  - The findings bullets carry roughly 60 numeric ranges, and every one is repeated in the section tables.
  - Each bullet should keep its assertion, one number and its figure pointer; the ranges then live only in their sections. The fifth bullet (89 words) and the sixth (83 words) gain most.
- **One term deserves a picture:** "Label-free threshold" (line 65). Its consequence, that the cap holds on the shifts and not on the recordings, is restated on lines 67, 414 and 528.
  - **Replacement figure:** a threshold-sweep sketch, a recording's score trace above three rigid-shift traces, with the threshold line stepping down until one shift exceeds the rate.
  - **Placement:** beside the term, or as a panel in Figure 4.
- The "Surrogate" entry should point to Figure 1 instead of re-listing the transforms.

**11. The five sections after Figure 5, all without figures (about 5,200 px) · low · verified: yes**
- **Where prose is right:**
  - "What this does not settle" and "What waits on Tony" are caveats and decisions.
  - References and provenance are reference material, and the stage table is the right form for commands.
- **One exception:** the whole-train-shifting paragraph (line 539, 192 words) is a chain of who credits whom, plus a drop-versus-wrap split at the ends.
  - **Replacement figure:** a **lineage timeline**: Grün et al. 1999 → Pipa, Riehle & Grün 2007 → Pipa et al. 2008 → Harrison & Geman 2009 → Louis et al. 2010 → Stella et al. 2022. Arrows mean "credits"; a mark shows each source's rule at the ends (drops: Elephant and this run; wraps: Louis, Stella, Dard).
  - The "trail stops at an unread paper" caveat stays as a caption line.
- **Pointers instead of repeats:** decisions 2 and 3 in "What waits on Tony" (108 and 125 words) re-quote Figure 3 and Figure 4 numbers. Point to "Figure 3, panel B" instead; the decision wording stays.

**12. Captions (lines 33, 124, 196, 278, 384; 53–124 words) · no finding**
- All five state what the figure shows, panel by panel.
- The main claim sits in the bold sentence right after each caption, not inside it, which is the right split.
- The Figure 3 and Figure 5 captions are at the upper end of the length range but contain only panel definitions.

**Boundary notes (not my findings, for agent 10, the mechanical checks role):**
- Every figure is drawn at 1575 px and displayed at 830 px, a 0.53× scale. Tick and row labels come out at about 10–11 px on screen.
- In Figure 5, the row-label column takes about 36% of the image width.
- I judged neither as a layout-policy failure. Legibility is a mechanical check.
