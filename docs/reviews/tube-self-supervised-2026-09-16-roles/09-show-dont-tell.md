GRANT 9 ok — Read, Grep, Glob, Bash

*(grant line repeated here as my first output line of the review proper; the opening line above was the same declaration.)*

## Conventions I used (tunable, stated so they can be argued with)

This artifact is **Markdown rendered on GitHub**, not slides, so the process doc's slide thresholds (40 words/slide, 60-word block) would flag every section and tell you nothing. Tuned for a report page, each `##` treated as a page:

- flag a **prose block over 80 words** that asserts something visual;
- flag a **section over 150 words with no figure** where the data beside the report support one;
- keep **two-or-more consecutive figure-free pages** as written;
- **figure share** measured against rendered page height, GitHub content column **890 CSS px**, body line box 24 px, table row 33 px. Figure height from the real PNG aspect ratio. The 890 px column is an assumption (I cannot render GitHub); everything else is measured.

## Count table

| page (`##`) | words | largest text block | figure | figure px (rendered) | page px | fig share | tables |
|---|---|---|---|---|---|---|---|
| title + standfirst | 68 | 54 | n | 0 | 136 | 0 % | 0 |
| The problem | 168 | 64 | n | 0 | 392 | 0 % | 0 |
| What holds | 142 | **98** | n | 0 | 304 | 0 % | 0 |
| Figure 1. What the two sensors buy | 537 | 79 | y | 369 | 1504 | 24.5 % | 2 |
| Figure 2. Learning from rigid shift alone | 368 | 55 | y | 309 | 1081 | 28.6 % | 2 |
| On real recordings | 239 | 66 | **n** | 0 | 552 | **0 %** | 1 |
| What this does not settle | 198 | **198** | n | 0 | 368 | 0 % | 0 |
| What waits on Tony | 135 | **135** | n | 0 | 272 | 0 % | 0 |
| How to reproduce | 125 | 49 | n | 0 | 511 | 0 % | 1 |
| **whole document** | **1980** | 198 | 2 figures | **678** | **5120** | **13.2 %** | 6 |

Geometry: `line_sensors_fig.png` 2025×840 px, authored 13.5×5.6 in at 150 dpi, rendered at **0.69×** authored linear size. `tube_ssl_fig.png` 2250×780 px, authored 15.0×5.2 in, rendered at **0.62×**.

Run of figure-free pages: **four consecutive**, 697 words, closing the report.

## Findings

| # | location | issue | sev | fix (named replacement figure) | verified |
|---|---|---|---|---|---|
| 1 | `README.md` lines 88–110, "Figure 2. Learning from rigid shift alone" | **The figure cannot carry the section's claim.** `tools/make_tube_ssl_figure.py:29` hardcodes `MODELS = {"tube": (...), "tube_guard": (...)}`, so the embedded PNG plots only the two tube arms — while both tables and the headline sentence ("Both `line` builds keep their F1 as the threshold tightens") are about `line` and `line_length`. The reader's eye lands on a picture that structurally excludes the models being argued about. | **major** | Add the `line` and `line_length` series to all three panels. No re-run needed: all 288 rows of `training/results.jsonl` carry `model` in {tube, tube_guard, line, line_length}; the data are already on disk. | yes |
| 2 | lines 100–109, the four-threshold table | A **slope claim delivered as 16 numbers.** "Keep their F1 as the threshold tightens / lose a third of theirs" is a shape, and the reader must do four subtractions to see it. | **major** | *Figure: what the label-free threshold costs.* x = threshold tightness (≤ 0.5, ≤ 1, ≤ 2 events per 10 min, oracle), y = held-out planted-truth F1, one line per model, band = ±1 sd over 4 folds × 3 seeds. The line builds render near-flat, the tube builds descend. Keep the table below it as the lookup surface. Source: `training/results.jsonl`, `arm == "supervised"`, `scores[...]["f1"]`. | yes |
| 3 | lines 124–144, "On real recordings" | **The one section about real data has no figure**, and it is the payload of the whole night ("run the full test all the way to real data"). 239 words and a 6-row table carry the claim that the label-free models "break single bursts into several calls and are not locked in time to them" — a purely visual claim, asserted in 16 words. Worse, the figure form already exists and was rendered to the darkroom four hours earlier: `<darkroom>/bugarach/tube_real_lanes_20250827_199_baseline.png` and `..._zoom.png`. | **major** | *Figure: what each detector called on one real baseline* — lanes over the raster, whole baseline plus a zoom. `tools/make_tube_real_lanes.py:34` hardcodes `LANES` to the tube arms; `real_compare/events.json` already carries `supervised line label-free`, `ssl line J10`, `ssl line J20`, so swapping that list renders the line version this section is actually about. Number it in the README when embedded (the darkroom copy has no `Figure N.`). | yes |
| 4 | lines 128–135, the participation table | **A distribution compressed to two numbers.** "ROIs within ±1 s, median" and "share with ≥ 3 ROIs" are summaries of a per-event distribution that is on disk: `real_compare/events.json` stores every event as `[time, participation]` for all 18 detector arms across 84 recordings. The median of 2 for the *J* = 10 s arm hints at mass piling up at one and two ROIs; a reader cannot see it. | **moderate** | *Figure: how many ROIs each call actually involves* — overlaid participation ECDFs (or step histograms), one per detector, with the random-times baseline shaded. This is the figure that shows the label-free calls degenerating toward pairs, which is the report's real conclusion about them. | yes |
| 5 | lines 62–65, the ⚠ fold-spread paragraph | **The report's most important caveat is prose-only, and the paired data exist.** `line_bakeoff/bakeoff.json` carries `per_fold` for every model. Pairing by held-out fold, `line` − `line_length` = **+0.045, −0.009, +0.179, +0.017** — three wins of four, and the mean gain is almost entirely one fold. The ± notation and Panel A's fold-range bars both *unpair* the folds and therefore cannot show this. | **moderate** | *Figure: the gain, fold by fold* — a paired slopegraph, fold on x, held-out F1 on y, `line` and `line_length` connected per fold. It makes the caveat self-evident and is more honest than the ± numbers, because it shows the gain is one fold rather than four. | yes |
| 6 | lines 68–81, the probe table and Panel B | **Two-thirds of the probe's data are discarded.** `probe/line_vs_fuzz.json` has K = 4, 8, 16 ROIs; the table and Panel B report K = 16 only. The K axis is the mechanism: line ÷ wave runs 1.01 → 1.05 → **1.32** for `line` and 1.01 → 1.04 → **1.14** for `line_length`. The orientation channels only separate at large K — the strongest mechanistic evidence for the second sensor in the report, currently thrown away. | **moderate** | Replace Panel B's grouped bars with *Figure: the separation grows with the line's length* — x = K in ROIs, y = line ÷ other plant, one line per plant, one small multiple per model. Keep the K = 16 bars as an inset or drop them. | yes |
| 7 | lines 154–158, the ⚠ untrained-baselines bullet | **A contradiction between two of the report's own artifacts, stated in prose.** The bullet says untrained models scored 0.00 on every plant in the probe yet untrained `tube` scored F1 0.507 with an oracle threshold — and Figure 2's own Panel A shows the untrained column sitting at 0.44–0.51. The reader has no way to check the report's strongest warning except by trusting it. | **moderate** | *Figure: the untrained models respond to nothing and score half* — two panels, same models, same run: probe response to a planted line (all at zero) beside oracle-threshold F1 (0.44–0.51). Both numbers come from files beside the report (`probe/line_vs_fuzz.json`, `training/results.jsonl`). One picture retires the ⚠ or proves the threshold bug. | yes |
| 8 | both PNGs | **Layout policy, not a build bug.** The figures are authored ultra-wide (13.5 in and 15.0 in) and GitHub caps them at the 890 px column, so they render at 0.69× and 0.62× of authored linear size: 8 pt tick labels land near 5 pt, the 9 pt legend near 5.6 pt. Whole-document figure share is **13.2 %** of rendered height. The three-panel strip is the worse offender, and its panel C dotted "must be 0.5" reference is the first thing to become unreadable. | **moderate** | **Reflow, not crop, and not a `width=` attribute.** Cap an authored figure row at **two panels / ≈ 9.3 in** so it renders at 1:1 in the column; stack instead of widening. Split the three-panel strip into two numbered figures — threshold behaviour (panels A and B) and the leak checks (panel C) — which also gives the leak checks the room their reference line needs. Boundary note: agent 10 may file the same PNGs as an oversize/legibility defect; this row is the layout prescription, not the geometry report. | yes (pixels and `figsize` measured; 890 px column assumed) |
| 9 | lines 44–48, "Panel A, the bake-off." | **A caption carrying methods.** The block closes on registration provenance — "registered as `line_length` so it is measured in the same run by the same scorer rather than quoted from another one" — which is correct, valuable, and not a caption. | **minor** | **Relocate, do not delete.** Move that sentence to the `How to reproduce` table's bake-off row or a one-line methods note. The caption keeps what the panel shows and why it matters. | yes |
| 10 | lines 124–194 | **Four consecutive figure-free pages, 697 words, closing the report.** The run is a consequence of findings 3, 4 and 7 rather than a separate defect; fixing those breaks it. | **minor** | No separate remedy. Recorded so the run is visible if any of those three is declined. | yes |

## Where prose or a table is right, and why

- **"The problem"** (168 words) — a definition of rigid shift plus two questions. Prose is right. A before/after schematic of a rigid shift would help, but `../rigid_shift_look/controls/` already owns that figure and the section links it; drawing it again here would duplicate, not clarify.
- **The 8-row bake-off table** (lines 50–59) — right as a table. It is a lookup surface carrying precision, recall and parameter counts, and Panel A already carries the comparison graphically. Keep both; do not replace the table with the plot.
- **"How to reproduce"** — a stage/command/output table is exactly the correct form. Nothing here should be a picture.
- **"What waits on Tony"** — three decisions awaiting a person. A numbered list is right; a figure would be decoration.
- **"What this does not settle"**, apart from the untrained-baselines bullet — a list of open items is right as a list. Note that this section is the largest text block in the report (198 words) and the **relocate rule protects it**: do not trim it to hit a density number. If length becomes a problem, the caveats move to an appendix section with the full text intact, never to a shorter sentence.

## Files

- Artifact: `<worktree>/docs/learned/tube_self_supervised/README.md`
- Figure generators needing the model-list change: `<worktree>/tools/make_tube_ssl_figure.py` (line 29) and `<worktree>/tools/make_tube_real_lanes.py` (line 34)
- Existing lanes-over-raster renders: `<darkroom>/bugarach/tube_real_lanes_20250827_199_baseline.png` and `..._zoom.png`
- Data supporting every proposed figure, all already beside the report: `line_bakeoff/bakeoff.json` (`per_fold`), `training/results.jsonl` (288 rows, all four architectures), `real_compare/events.json` (per-event `[time, participation]`, 18 arms), `probe/line_vs_fuzz.json` (K = 4, 8, 16)

I edited nothing; scratch work ran in-memory under the session scratchpad.
