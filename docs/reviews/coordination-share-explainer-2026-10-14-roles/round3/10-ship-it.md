GRANT 10 ok — Read, Grep, Glob, Bash

I found one high-severity defect: Figure 5C does not draw 14 of its 48 data points in the two high-background rows. The build is current, the darkroom copy matches the repo byte for byte, five of six README links resolve, and no figure has text colliding with text.

Renders checked: the six PNGs in `c:\Users\defazio\bugarach\bugarach-worktrees\coordination-share-explainer\docs\learned\coordination_share_explainer\`, each at full size, scaled to 880 px, and as zoom crops (crops are in scratchpad `mb-r3\r10\`).

**Build is current.**
- The PNGs were written 12:32:54–12:32:58 EDT. The generator `explain_coordination_share.py` was last saved at 12:29:57, the README at 12:32:24, and every input the script imports is older:
  - `measure_coordination_rates.py`, `bench.py`, `simulate.py`, `time_axis.py`, `_shared.py`, `artifact_name.py`: last commits run from 2026-08-10 to 2026-10-07, and their on-disk mtimes are 11:12 today.
- Commit fd252301 (12:33:32) holds them, and `git status` is clean.
- The darkroom folder `<darkroom>\bugarach\2026-10-14-coordination-share-explainer\` has the same md5 as the repo for all 8 files (README, 6 PNGs, `numbers.json`).

**Document properties.** Every PNG carries Title ("Figure N. …") and Author ("bugarach, explain_coordination_share.py"). None carries a creation or modified time.

**Font sizes.** Px-at-880 assumes GitHub scales each 150 dpi PNG to 880 px wide, so 1 pt ≈ 2.08 px × scale.

## Table

| Fig / panel | Render checked | Build current | Overlap / clipping (zoom-crop) | Everything present | Axes: name + unit | Shared limits | Lettered | Every mark identified | Glyph consistency | Colour contrast | Rendered box; smallest font as placed |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 A (lane) | fig1 PNG, 1471×1401; crop `f1_lane_right.png` | yes | none; the 2 s pair is drawn stacked on purpose and labelled "2 s pair" | close, medium and single all in view | y "planted"; x shared with D | x shared | A | ▼ colours are in the legend; the medium pair has no on-plot text, unlike the close pair | ▼ points down at the raster (house rule) | blue / orange / green distinct | 880×838 px (100% of column, tall); smallest "2 s pair" 10 pt ≈ 12.5 px |
| 1 B (raster) | fig1 PNG | yes | none | 32 rows | "cell · 32 cells"; x in minutes (m) | y same as D (0.3–32.7) | B | ink only, nothing drawn on the raster | — | black / white | ticks 11 pt ≈ 13.7 px |
| 1 C (count) | fig1 PNG | yes | none | yes | "onsets per 1 s window (X)" | — | C | gray bars, caption explains | — | ok | same |
| 1 D (shifted raster) | fig1 PNG; crop `f1_D_left.png` | yes | **one onset (row ~26, t = 30m00s) sits on the y-spine and is hidden by it** | yes | "cell, shifted copy · 32 cells"; x "time in the recording", 30m–35m | y same as B | D | yes | — | ok | same |
| 2 A | fig2 PNG, 1369×724 | yes | none | yes | x "onsets in one 1 s window (X)"; y count, log, 2700 windows | — | A | legend | — | **shifted copy #52514e vs recording #0b0b0b: dark gray against near-black, a low-contrast category pair** | 880×465; legend 10 pt ≈ 13.4 px |
| 2 B | fig2 PNG; crop `f2_tip.png` | yes | the f₃ arrowhead is drawn over the recording's diamond (cosmetic) | yes | y "pairs (f₂) or triples (f₃) beyond chance, per 1 s window" | — | B | legend has copies, recording and zero; **the "zero" legend swatch is #d9d8d4 and almost invisible at 880 px**; arrows labelled "excess" | ◆ = recording | see left | 11 pt ≈ 14.7 px |
| 3 A–C | fig3 PNG, 1473×732; crop `f3_C.png` | yes | none; in C, "-2%" sits just above the right-answer line without touching it | 48 points per panel per model; every point inside 0.4–1.6 (checked against `numbers.json` min/max) | y "recovered ÷ planted (1 s window)"; x planted share in % | sharey, sharex; 0.4–1.6, the same as Fig 6 | A B C | **the binomial median is a thin bar that is not in the legend; the legend shows only the thick (fixed) bar** | ● fixed / ○ binomial; **the median bars sit at x = 31.5–33.5% on a data axis and read as data points (in A they sit beside a real point at 28%)** | ok | 880×437; **smallest: median labels 9 pt ≈ 11.2 px**; legend 9.5 pt ≈ 11.8 px |
| 4 A–C | fig4 PNG, 1430×745 | yes | none | 5 sets × 3 windows × 3 panels | y "…: recovered ÷ planted − 1" in %; x "window length (w)" in s | y not shared on purpose (three different quantities) | A B C | legend; the band is only in A, and its legend entry says so | colour and shape per set, consistent with Fig 1 (blue close, orange medium, green 120 s / single); ▼ and ◆ reused here with meanings different from Figs 1–2 | orange #eb6834 and yellow #eda100 are adjacent hues, rescued by marker shape | 880×458; 10 pt ≈ 12.8 px |
| 5 A | fig5 PNG, 1484×810; crops `f5_Aleg.png`, `f5_Azero.png` | yes | **the dotted orange "no stretch" line (0.13%) sits on the solid zero line, about 2 px apart at 880 px, so the two cannot be told apart** | yes | y share reported coordinated (%); x stretch length (10s … 15m) | — | A | legend | — | ok | 880×480; 10 pt ≈ 12.4 px |
| 5 A, x-axis | same | — | — | — | **the categories 10s, 30s, 1m, 2m, 5m, 15m are evenly spaced and joined by a line, which implies a continuous, evenly spaced axis** | — | — | — | — | — | — |
| 5 B | fig5 PNG; crop `f5_BC.png` | yes | none, though C's row label "45 min, 13× quiet" ends within ~10 px of B's zero line | yes | y "share reported coordinated (scale differs from A)"; x rate ÷ background (log) | unshared y is flagged on the axis, which passes | B | band and line explained only by A's legend and the caption | — | ok | same |
| 5 C | fig5 PNG; crop `f5_Cleft.png`; values recomputed (see finding 1) | yes | **14 of 48 "after" points lie left of the x-limit −0.01 and are not drawn; one is half-clipped at the spine** | **no (see finding 1)** | x "pairs beyond chance, f₂ (per 1 s window; …; linear below 0.001)", symlog with ticks −0.01, 0, 0.01, 1; rows named on y | — | C | legend: ○ before, ● after | ○/● now means before/after, where Figs 3 and 6 use it for model and for own/pooled; each figure has its own legend | ok | same |
| 6 | fig6 PNG, 1365×714 | yes | none | 5 groups × 24 recordings × 2; every point inside 0.4–1.6 (`numbers.json`) | y "share recovered ÷ planted (fixed model, 1 s window)"; x groups with planted share | 0.4–1.6, the same as Fig 3 | single panel | legend covers ○, ●, whisker, median bar and right-answer line; the legend draws the 10th–90th whisker horizontal while the plot draws it vertical | the median is a thick **gray** bar here but a thick **black** bar in Fig 3 | ok | 880×460; legend 10 pt ≈ 13.4 px |
| README | README.md | yes | — | 6/6 image links resolve, plus 2 todos, the tool, the script and `numbers.json` | — | — | Figures 1–6 numbered | — | — | — | **the link `../../reviews/coordination_share_explainer_2026-10-14.md` is dead (only the `-roles` folder exists)** |

## Findings
"Verified" means I could check it against a source.

1. **Fig 5C, rows "constant, 13× quiet" and "rising 3× over 45 min, 13× quiet": data silently dropped.** HIGH. Verified: yes.
   - I re-ran `_measure` with the same seeds. The "after" excess f₂ runs from −0.128 to +0.092 (constant) and −0.082 to +0.147 (rising).
   - With `axC.set_xlim(-0.01, 5)`, 9 of 24 and 5 of 24 points are not drawn, and the one dot left at the spine is half-clipped.
   - As drawn, subtraction looks tight around zero. In fact the 13× "after" values spread about ±0.1 per recording, which is a quarter of the raw f₂ (~0.4). "Removes 99%" holds only for the median.
   - Fix: set the left limit from the data (e.g. −0.2, tick −0.1), or mark the out-of-range count on each row. The README should state the per-recording spread as well as the median.

2. **README "For developers": the murderboard-record link is dead.** MEDIUM. Verified: yes. It points to `docs/reviews/coordination_share_explainer_2026-10-14.md`, which does not exist. Fix: write the record before shipping, or point the link at the `-roles` folder.

3. **Fig 5A: the "no stretch (median)" dotted line cannot be told apart from the zero line.** MEDIUM. Verified: yes (crop). At 0.13% on a 0–12% axis the two lines are about 2 px apart. Fix: show it as a text value or point at the left edge (e.g. "no stretch: 0.1%"), or give it its own marker.

4. **Fig 3: the median glyphs sit inside the data x-range.** MEDIUM. Verified: yes.
   - The bars at planted share 31.5% and 33.5% read as data points.
   - The binomial median (thin bar) has no legend entry.
   - Fix: move the medians into a margin strip outside the data axis, or onto a separate tick labelled "median", and give the binomial median its own legend entry.

5. **Fig 2A: low-contrast category pair.** LOW–MEDIUM. Verified: yes. #52514e against #0b0b0b; at 880 px the two bar series separate mainly by position. Fix: use a light gray (e.g. #b5b4b0) for the shifted copy.

6. **Fig 5A: an uneven categorical x-axis is drawn as a continuous line.** LOW. Verified: yes. Fix: place the points at log(seconds), or drop the connecting line.

7. **Fig 2B: the "zero" legend swatch is the near-invisible #d9d8d4, and the f₃ arrowhead is hidden under the diamond.** LOW. Verified: yes. Fix: darken the zero line; set `shrinkA`/`shrinkB` on the annotate call.

8. **Fig 1D: an onset at exactly 30m00s is drawn under the y-spine.** LOW. Verified: yes. Fix: pad the x-limit by about 1 s, or set the spine zorder below the raster.

9. **Glyph and colour reuse across figures.** LOW. Verified: yes.
   - The median is a black bar in Fig 3 and a gray bar in Fig 6.
   - ○/● means model in Fig 3, before/after in Fig 5C, and own/pooled in Fig 6.
   - ▼ and ◆ change meaning between Figs 1, 2 and 4.
   - Each figure has its own legend, so this is identified; it is just not consistent. Fix: use one median glyph and colour throughout. Optionally keep ● for "what the tool reports" everywhere.

10. **Fig 3 median labels print an ASCII hyphen ("-18%") where the README uses "−".** LOW. Verified: yes (code `f"{…:+.0%}"`). Fix: replace "-" with "−".

11. **Fig 4: the legend title "intervals between moments" also heads the pass-band and right-answer entries.** LOW. Verified: yes. Fix: split the legend, or retitle it.

12. **Document properties: the PNGs have no creation or modified time.** LOW. Verified: yes. Fix: pass `"Creation Time"` in the `savefig` metadata in `save()`.

13. **Fig 3 has the smallest placed font: 9 pt median labels at about 11.2 px on GitHub.** LOW. Verified: yes (computed). Fix: use 10 pt or more.

No legend text collides with any other text in any figure.
