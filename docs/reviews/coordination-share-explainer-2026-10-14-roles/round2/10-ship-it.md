GRANT 10 ok — Read, Grep, Glob, Bash

**Role 10 (Build & craft gate) — coordination-share explainer, round 2**

Everything below was checked against the PNGs themselves: full renders, zoom crops, and 880 px downscales in `C:\Users\defazio\AppData\Local\Temp\claude\c--Users-defazio-bugarach-bugarach\8f7e79d0-c19b-4389-819d-be7bbbbd9efc\scratchpad\mb-r2\ship\`. I edited nothing.

**Build and delivery checks (whole artifact)**
- **Build is current.** The PNGs were written 12:12:10–12:12:13 EDT and `numbers.json` at 12:12:13. That is newer than the generator `explain_coordination_share.py` (12:10:57) and newer than every input it imports (`src/bugarach/bench.py`, `src/bugarach/simulate.py`, `tools/measure_coordination_rates.py`, all about 11:12). The build is committed in b3a92814 (12:13:03) and the folder has no uncommitted changes.
- **The darkroom copy matches.** `<darkroom>/bugarach/2026-10-14-coordination-share-explainer/` holds the same 6 PNGs and README. MD5 checksums are identical for all 7 files.
- **README is written by hand.** The script does not generate it, so its timestamp (12:10:49) is not a staleness signal.
- **All six image links in the README resolve,** in both copies.
- **Document properties:** each PNG's Title names its own figure ("Figure N. …") and its Author is "bugarach, explain_coordination_share.py". There is no creation-time tag.
- **Figure numbers:** captions open "**Figure N.**" and every image's alt text is "Figure N". The PNGs carry no number of their own.
- **House raster rule:** Figure 1 B and D carry ticks only, and the planted cues sit in lane A above the raster as down-pointing ▼.

**Size as placed.** Every PNG is saved at 150 dpi with a tight bounding box. GitHub shows each one at the full 880 px width of the content column (100%). "Smallest font" is the em height in screen pixels after that downscale.

| Figure | Native size | Shown at 880 px | Scale | Smallest font as shown |
|---|---|---|---|---|
| 1 | 1471×1401 | 880×838 | 0.598 | "2 s pair", 9 pt → **11.2 px** |
| 2 | 1369×724 | 880×465 | 0.643 | legend, 10 pt → 13.4 px |
| 3 | 1352×734 | 880×478 | 0.651 | x-labels and legend, 10 pt → 13.6 px |
| 4 | 1394×745 | 880×470 | 0.631 | y-labels and legend, 10 pt → 13.1 px |
| 5 | 1445×728 | 880×443 | 0.609 | legends, 9 pt → **11.4 px** |
| 6 | 1397×655 | 880×413 | 0.630 | legend, 10 pt → 13.1 px |

**Per-panel table**

| Panel (render) | Overlap / clipping | Everything present | Axes named, with unit | Shared limits | Lettered | Lines, markers, colours, bands identified | Glyphs | Contrast |
|---|---|---|---|---|---|---|---|---|
| 1A lane (fig1 PNG, crop `f1_pair.png`) | The two close-pair ▼ merge into one "W" shape (F7) | Yes: 2 orange, 1 green, 2 blue | Labelled "planted" | x shared with B–D | A | Legend plus "2 s pair" text | ▼ points down | OK |
| 1B raster | None | Yes | "cell · 32 cells"; x shared | y matches D | B | Black ticks only | – | OK |
| 1C counts | None; no annotation lines | Yes | "onsets per 1 s window (X)" | – | C | Grey bars are the data | – | OK |
| 1D shifted raster | None | Yes | Name and unit; x axis 30m…35m in house format | y matches B | D | Ticks only | – | OK |
| 2A histogram (fig2 PNG) | None | Yes | x "onsets in one 1 s window (X)"; y "1 s windows (count, log scale; 2700 windows)" | – | A | Legend | Black = recording, green = shifted (matches B) | OK |
| 2B f₂/f₃ (crop `f2_arrow.png`) | Arrowhead touches the ◆ (intended) | Yes | **y is "per 1 s window": a unit with no quantity name** (F2) | – | B | **Grey line at 0 not identified** (F6) | ◆ = recording | OK |
| 3A–C (fig3 PNG) | None | Yes, 48 recordings per panel | y "recovered ÷ planted (1 s window)"; x is a percentage | y shared; **x limits differ** (F4) | A–C | Figure-level legend covers band, line, ● and ○ | ● fixed, ○ binomial, same in all panels | OK |
| 4A–C (fig4 PNG) | None; series are dodged | Yes, 5 series × 3 windows in each panel | y "quantity: recovered ÷ planted − 1" in %; x "window length (w)" with s ticks | Different quantities, so independent y is fine | A–C | Legend covers band and series; **0% line not identified** (F6) | Same marker and colour per series in all panels | Yellow #eda100 next to orange #eb6834 is weak, but marker shape also separates them |
| 5A (fig5 PNG, crop `f5_aleg.png`) | **Legend text sits on the grey band's peak** (F8) | Yes | x is stretch length with an onsets-per-second-per-cell unit; y is share, % | **Differs from 5B, which shows the same quantity** (F1) | A | Legend covers band, median and dotted "no stretch" line; **solid 0 line not identified** (F6) | – | OK |
| 5B | Clear of C's tick labels by about 10 px (crop `f5_bc.png`) | Yes | **No y label** (F1); x is a rate ratio | **Not shared with A; not marked** (F1) | B | Band and line rely on A's legend; **0 line not identified** | Same as A | OK |
| 5C (crop `f5_crow.png`) | **In the two quiet rows the open "before" markers are hidden under the filled "after" markers** (F3) | **Not visibly** (F3) | x "pairs beyond chance, f₂ (per 1 s window; nothing planted)"; y is labelled categories | – | C | Legend above the panel | ○ before, ● after | OK |
| 6 single panel (fig6 PNG) | None | Yes: 5 groups × 24, no recording without an answer (`numbers.json` `no_answer` = 0 everywhere) | y "share recovered ÷ planted (fixed model, 1 s window)"; x is groups | – | Single panel | Legend covers ○, ●, orange median bar and line | ○ own, ● pooled | OK |

**Findings** (location · issue · severity · suggested fix · checked against a source?)

**Moderate**

- **F1 · Figure 5, panels A and B · two panels show one quantity at different scales, and B has no label for it.** Both panels plot "share of events reported coordinated (nothing planted; 1 s window)". A runs 0–12%, B runs −0.3–3.5%. B has no y-axis label and nothing marks the different scale.
  - Fix: give B its own y label, plus "(scale differs from A)" or a short note in the caption. Alternatively share y between A and B.
  - Verified: yes (render, and `figure5` has no `set_ylabel` on `axB`).
- **F2 · Figure 2B, y axis · the label "per 1 s window" is a unit with no quantity name.** It also covers two different quantities: f₂ is pairs and f₃ is triples.
  - Fix: relabel as "beyond-chance pairs (f₂) or triples (f₃) per 1 s window".
  - Verified: yes (render).
- **F3 · Figure 5C, rows "steady, quiet" and "rising 3× over 45 min, quiet" · the "before" markers cannot be seen.** In `numbers.json`, raw f₂ is about 0.003–0.004 and the excess is about 0.0001–0.0014, on an axis running to 3. The open markers sit exactly under the filled ones. The README cites "Figure 5C, the steady rows" as showing that clumping is removed, but "steady, quiet" (52% removed) shows nothing at this scale. The README does admit the rising quiet row "shows nothing either way". An element the panel claims to show is invisible.
  - Fix: one of three options:
    - a symlog x axis;
    - an inset or separate scale for the quiet rows;
    - narrowing the README claim to the 13× rows.
  - Verified: yes (`numbers.json` figure 5 C, and the zoom crop).

**Low**

- **F4 · Figure 3, panels A–C, x axes · same measurement, three different ranges.** "Planted share of events" runs `xlim(0, None)` in each panel, ending at about 29%, 28% and 26%, so the 10% and 20% ticks fall in different places.
  - Fix: share x across the three panels (`sharex=True`, or one common `set_xlim`).
  - Verified: yes (render and code).
- **F5 · Figures 1–6 · the same colour or glyph means different things in different figures.**
  - Green means a single moment (Fig 1), a shifted copy (Fig 2) and "120 s only" (Fig 4).
  - Orange means a medium pair (Figs 1 and 4) and the median bar (Fig 6).
  - ● against ○ means fixed against binomial model (Fig 3), after against before (Fig 5C), and pooled against own (Fig 6).
  - Each figure has its own legend, so nothing is unidentified, but a reader moving between figures carries the wrong meaning across.
  - Fix: at minimum, give Fig 2's shifted copy a colour not used for a gap type, and draw Fig 6's median bar in a neutral ink.
  - Verified: yes (renders).
- **F6 · Figure 2B, Figure 4 A–C, Figure 5 A and B · the zero/reference line is drawn but not identified.** In Figure 4 the 0% line is the "right answer", and Figure 3 legends exactly that line.
  - Fix: add "right answer (0%)" to Figure 4's legend, and name the zero line in the Figure 2 and Figure 5 captions.
  - Verified: yes (renders and captions).
- **F7 · Figure 1A, the close pair · the two ▼ overlap into one "W" shape.** They are 2 s apart on a 300 s axis, about 5 px apart at 880 px wide.
  - The "2 s pair" text explains it, but a reader cannot count two markers.
  - Fix: a small zoom inset, or offset the second marker vertically.
  - Verified: yes (`f1_pair.png`).
- **F8 · Figure 5A, legend · the legend overlaps the grey 10th–90th percentile band at the 30s–1m peak.** The text stays legible.
  - Fix: move the legend above the panel, as in 5C, or put it at lower left.
  - Verified: yes (`f5_aleg.png`).
- **F9 · Figures 1 and 5 · the smallest text shows at about 11 px on GitHub.** Fig 1's "2 s pair" and Fig 5's 9 pt legends are below GitHub's 16 px body text. Everything else is at least 13 px.
  - Fix: raise both to 10–11 pt.
  - Verified: yes (computed from font size, dpi and 880 px scaling).
- **F10 · README line 188 · names a row of Figure 5C by position ("Figure 5C, bottom row").** The row has a label.
  - Fix: write "Figure 5C, the row 'rising 3× over 45 min, 13× quiet'".
  - Verified: yes.

**Main files**
- Artifact folder: `c:\Users\defazio\bugarach\bugarach-worktrees\coordination-share-explainer\docs\learned\coordination_share_explainer\` (README.md, six PNGs, numbers.json, explain_coordination_share.py)
- Darkroom copy: `<darkroom>\bugarach\2026-10-14-coordination-share-explainer\`
