> **Public copy.** Lines that concern real treatment recordings are removed (18 here), per FOUNDATIONS §5, and machine paths are shortened to `<scratchpad>`, `<worktree>`, `<darkroom>` or `<home>` (sapper SAP004). Everything else is verbatim.

GRANT 9 ok — Read, Grep, Glob, Bash

# Role 9: Density and figure-first review of the detector review page (round 3, blind)

**Summary:** the page does not suffer from undersized figures. Its problem is where the figures sit and what they leave out:
- The conclusions (Sections 9–10 and the "In short" box) have no figure at all.
- Several numbers the text relies on are not drawn in the figure it cites.
- About six stretches of 560–975 words of prose restate figures that sit right next to them.

Nothing here is blocking. There are 11 major findings and 13 minor ones.

**What I checked:**
- **Page:** the built page, `<scratchpad>\review\detector_review.html`. I rendered it in Playwright chromium with a 1280×900 viewport and measured the page from the rendered layout, not the source.
- **Text:** all of `detector_review_plain.txt`.
- **Figures:** all 18 PNGs, each opened as an image.
- **Conventions:** the plot conventions in CLAUDE.md, checked against every figure.
- I wrote no files; the measurement script ran from stdin.

**Thresholds I used.** These are adapted for one long HTML page rather than slides. They are conventions, not researched optima.
- Flag any stretch of more than about 400 words, or about one screen (900 px), with no figure.
- Flag any single paragraph over about 120 words.
- Flag any caption over about 100 words.
- Flag any methods or results section where figures take up less than half the section's height.
- Flag any figure narrower than half the column. None was.

## Count table (rendered)

| Section | Words | Longest block (words) | Figure? | Figure share of section height |
|---|---|---|---|---|
| Front matter ("In short", contents) | 417 | 72 | no | 0% |
| 1. The problem | 592 | 159 (caption), 111 (paragraph) | yes (1) | 40% |
| 2. Surrogates | 859 | **247 (caption)**, 185 (paragraph) | yes (1) | 54% |
| 3. Hand-written detectors | 1,606 | 134 | yes (6) + Table 1 | 44% |
| 4. Learned detectors | 650 | 117 | yes (1) | 41% |
| 5. Simulator | 809 | **190 (caption)**, 140 | yes (1) | 41% |
| 6. Grading and tuning | 620 | 132 | yes (1) | **21%** |
| 7. Results, simulated | 1,460 | 113, plus Table 3 (12 rows × 16 columns) | yes (3) | 42% |
| [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder] |
| 9. Strengths and weaknesses | 547 | table cells | **no** | 0% |
| 10. What this means | 434 | 90 | **no** | 0% |
| 11. Sources | 796 | 145 | no (prose is right here) | 0% |
| 12. Word list | 648 | — | no (prose is right here) | 0% |

**Figure size:** every figure renders 1182 px wide in a 1212 px column (98%). No figure has empty side margins, so no reflow is needed.

**Stretches with no figure:**

| Stretch | Words | Height |
|---|---|---|
| Top of page to Figure 1 | 850 | 2,233 px |
| Figure 2 to Figure 3 | 975 | 2,055 px |
| Figure 9 to Figure 10 | 560 | 1,612 px |
| Figure 10 to Figure 11 | 742 | 1,969 px |
| [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder] |
| [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder] |
| [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder] |

[line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder]

## Findings

"Verified" means I could check the finding against a source (the rendered figure, the page text or the measured layout).

### Major

| # | Location | Issue | Fix (with the replacement figure) | Verified |
|---|---|---|---|---|
| [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder] |
| M2 | "In short" bullet 4; Section 7, "A busier background costs…" | The headline number is not in the figure the text cites. The text quotes CoactDetect **at its shipped setting** (52% → 24% of small events) and points to Figure 13C. Figure 13C draws **tuned** values (about 0.57 → 0.19 by eye, which matches Table 3's tuned recall). The same applies to rate+context's shipped 2%. | Add purple shipped-setting diamonds to 13C1/13C2. Better: replace C1/C2 with a **slopegraph**, one line per detector from quiet to busy, for 10%-of-ROIs events, shipped setting solid and tuned faint. The claim "busier cells change what a detector reports" then becomes the slope itself. | yes |
| M3 | Figure 10D; "What the simulator gets wrong", bullet 1 | The text says the simulator's worst failure depends on ROI rate: bunching matches real cells below 50 mHz but reads about 9.8 against about 1.2 above 100 mHz. Figure 10D averages bunching over all ROIs against window length, so the failure the text calls important is not drawn. The panel even shows the simulation above the recordings at every window, which reads against "matches below 50 mHz". | Replace or add a panel: **bunching in 30 s windows against ROI rate** (log x), recorded vs fitted. The bullet then shrinks to one sentence. | figure yes; numbers no |
| [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder] |
| [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder] |
| [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder] |
| M7 | Figure 2 | This is two figures in one. Panels A–C show shift vs shuffle. Panel D shows where the surrogate is drawn from, an idea that returns in Figures 4, 5 and 14. It renders 1,784 px tall (two screens) with a 247-word caption. The 185-word "Why the shift" paragraph restates values from 2B and 2C. | Split: Figure 2 = A–C; a new figure = D, placed at "Where the surrogate comes from". Keep each caption under 80 words. Print the values at n = 6 (recorded, shift, shuffle) where the dashed line crosses 2B1. Cut the paragraph to the mechanism sentence, about 60 words. | yes |
| M8 | From Figure 2 to Figure 3 (Section 3 intro, Table 1, 3.1) | 975 words with no figure. Table 1 and the 3.1–3.6 mechanism paragraphs describe each detector twice. | Keep Table 1 as the summary. Cut each 3.x paragraph to what the table cannot hold (merge rules, minimum ROIs). Let the mechanism panels in M9 carry the rest. | yes |
| M9 | Figures 3–8 | The brief asks each detector's figure to show "how it works graphically". Each figure shows the measure against the bar over 3 minutes, which is the **outcome**. The **mechanism** the text spends 64–177 words on per detector is not drawn: bin width; the 60 s surrogate window; LoCo's two one-minute sides, taking the higher, stepping every 15 s; locust's 1 s "on" period; SPIKE-synch's four-gap window with the 0.25 s cap. SPIKE-synch has the longest mechanism text and nothing drawn. | Add a zoom panel C (about 20 s around the planted event) to each figure, drawing nothing on the raster. In a lane above the zoomed raster, show bins as alternating hatched spans and the surrogate window as a bracket with a scale bar (LoCo: two brackets, the higher side filled). locust: a panel under the raster showing each event's 1 s "on" bar. SPIKE-synch: each event's coincidence window as a short horizontal bar in a lane. Then cut each 3.x paragraph to 1–2 sentences. | yes |
| [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder] |
| [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder] |

### Minor

| # | Location | Issue | Fix | Verified |
|---|---|---|---|---|
| [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder] |
| m2 | Figure 12 | The key says "chosen in at least one round", which hides the "3 of 4 rounds" the bullets quote. Rotated tick labels push some x-axis titles lower than their neighbours'. | Label each circle with its round count ("×3"). Align the axis titles. | yes |
| m3 | Figures 12 and 14 | A full-sentence title above the plot repeats the caption (the conventions say no titles above plots). | Delete it; keep only the A/B/C panel headings. | yes |
| [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder] |
| [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder] |
| [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder] |
| m7 | Pro/con boxes in Sections 3–4, and Table 4 | Claims repeat: "counts cells, not events" appears in both places. | Once M1's map exists, cut each box to one line or remove the boxes. | yes |
| m8 | Figure 9; Section 4.2 | Panels B and C show only tube's traces, so the reason the ratio models make no false alarms is not shown. The failed controls get 117 words and no picture. | Add a tube-ratio score row to panel C. Add trace and tiny as two more lanes in B and C, each showing one call spanning the whole window. Move the learning-rate caveat to notes. | yes |
| m9 | Figure 10B; Figure 10A labels | The planted event's ticks fill the middle ~1.2 s of an 8 s window, and some ticks overlap. A1/A2 draw ▽ and ▼ in one row and overlap. The raster label says "33 ROI". | Zoom to about 3 s. Split planted and decoys into two labelled rows. Write "33 ROIs". | yes |
| m10 | Figure 10C | The key box covers the top edge of the flat-rate histogram near 10 mHz. | Move the key outside the plot area. | yes |
| m11 | Figure 9, key | Green ▼ here means "found by any of the four"; in Figures 3–8 it means found by that detector. | Mark found/missed per lane, or say so in the lane label. | yes |
| [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder] |
| m13 | Section 6.3 / Figure 11B | The learned detectors' 10 train / 2 pick / 6 scored split and the three training runs are in prose only (132 words). Section 6 has the lowest figure share on the page (21%). | Add one row to 11B showing the learned detectors' split for one round. | yes |

## Plot conventions: passed

- [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder]
- **Markers point down:** every directional marker (▼ planted, ▽ decoy) points down at its raster.
- **Minutes-friendly time axes:** every time axis uses 60-base labels ("7m30s", "30s–5m", "−12s…+12s"). None shows raw seconds.
- [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder]
- **Figure numbers:** every figure has a numbered caption ("Figure N.").
- **Prose is right here:** the source list (Section 11), the word list (Section 12) and the "what could be wrong" checklist in Section 10 should stay as text.
