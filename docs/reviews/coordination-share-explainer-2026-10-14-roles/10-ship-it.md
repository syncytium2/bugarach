GRANT 10 ok — Read, Grep, Glob, Bash

I checked all five figures against their PNGs. None of them is clean.

- **Most serious (moderate):** in Figure 1 the two triangles that mark a close pair merge into one W-shaped blob, so the figure's own point cannot be seen. Figure 1's three panels are also unlettered, and the caption refers to them by position ("Bottom").
- **Lines and bands not identified in the figure:** the diagonal in Figure 3, the ±25% band in Figure 4, and the line at 1.0 in Figure 5B are explained only in the README caption.
- **Text too small on GitHub:** Figures 4 and 5 are about twice as wide as GitHub's ~880 px column, so their smallest text shrinks to roughly 7–9 px.

**Build current: yes.** The five PNGs are dated 11:40:08–11:40:11 EDT. The script was last changed at 11:36:13. Its inputs are all older: `tools/measure_coordination_rates.py`, `src/bugarach/bench.py` and `tools/naming/artifact_name.py`, each dated 11:12 EDT. The worktree is clean and the files are committed in e3c2e5a.

**Darkroom copy:** `<darkroom>/bugarach/2026-10-14-coordination-share-explainer/` is byte-identical to the repo copy (`cmp`) for all five PNGs, README.md and numbers.json.

**Image links:** the README's five `![Figure n](...)` relative paths all point to files that exist in the same folder.

**How sizes were measured:** every PNG is rendered at 150 dpi. "Placed" means the width scaled to 880 px. Font size in px = pt × 150/72 × scale.

**Zoom crops** are in `C:\Users\defazio\AppData\Local\Temp\claude\c--Users-defazio-bugarach-bugarach\8f7e79d0-c19b-4389-819d-be7bbbbd9efc\scratchpad\mb-r1\`:
- `f1_lane.png`
- `f2_ticks.png`
- `f4_markers.png`
- `f5_legend.png`
- `gh_*.png` (Figures 1, 4 and 5 resampled to 880 px)

## Table (one row per figure/panel; each checked against the PNG named)

| Figure / panel (render) | Build current | Overlap / clipping (zoom-crop) | Everything present | Axes labeled (name AND unit) | Shared limits | Panels lettered | Every line/marker/colour/band identified | Glyph consistency | Colour contrast | Rendered size and smallest font as placed |
|---|---|---|---|---|---|---|---|---|---|---|
| Fig 1, cue lane (`...fig1-the-count_20261014.png`) | yes | **FAIL.** The two ▼ of each close pair, 2 s apart, overlap and merge into one W-shaped blob (`f1_lane.png`). The pair cannot be read as two moments, natively or at 880 px. | Partial. The legend has an aqua "single moment" entry, but there is no aqua ▼ anywhere in the 6 minutes shown. | Lane is labeled "planted" (no unit needed). | n/a | **FAIL.** The lane, raster and count panels have no letters, and the caption uses "lane above" and "Bottom". | Legend is in colour, beside the lane. OK. | ▼ points down at the raster. OK, as CLAUDE.md requires. | Blue/orange OK. Colour is the only identity, which CLAUDE.md allows in the lane (shape is already used for "look below"). | 1524×969 → 880×560 (100% of the column). Legend 9 pt → about 10.8 px. |
| Fig 1, raster | yes | No overlap. Nothing is drawn on the raster. | yes | "cell · 32 cells". OK. | Shares x with the lane and count. OK. | unlettered (as above) | Black ink only. OK. | n/a | n/a | Ticks 10 pt → about 12 px. |
| Fig 1, count panel | yes | none | yes | y: "onsets per 1 s window (X)". OK. x: "time in the recording" has no unit word, but the tick labels (35m30s…) carry it in the house minutes format. Minor. | x shared. OK. | unlettered | Grey bars are named by the y label. OK. | n/a | n/a | about 12 px |
| Fig 2A (`...fig2-wider-spread_20261014.png`) | yes | none | yes | x: "onsets in one 1 s window (X)". y: "1 s windows (count, of 2700 windows)", log scale. OK. | n/a | A. OK. | Legend: aqua = shifted copy, black = recording, both with means. OK. | Aqua = shifted and black = recording, the same in A and B. OK. | aqua/black ΔE about 80. OK. | 1505×645 → 880×377. Legend 9 pt → about 11 px. |
| Fig 2B | yes | The tick labels "f₂ (pairs beyond chance)" and "f₃ (triples beyond chance)" are about 10 px apart natively and about 6 px at 880 px. They nearly read as one string (`f2_ticks.png`). Minor. | yes | y: "factorial cumulant (per 1 s window)". OK. | n/a | B. OK. | Dots and ◆ are in the legend. Arrows are labeled "excess …" on the figure. The pale zero line is not identified (minor; it is a reference line). | ◆ = "the recording" here. Fig 5B uses ◇ for a different thing (see findings). | OK | Excess text 9 pt → about 11 px. |
| Fig 3 (`...fig3-planted-vs-recovered_20261014.png`) | yes | Filled and open markers overplot heavily between 3% and 10% planted, so the models cannot be told apart there. Minor. | yes | x: "planted share of events that are coordinated", in %. y: "recovered share of events", in % (the name is shorter than x's). OK. | x and y limits are equal. OK. | Single panel. OK. | **FAIL.** The grey diagonal (recovered = planted) is not in the legend or labeled on the figure; only the README caption names it. | Filled = fixed, open = binomial. OK. | Monochrome. OK. | 887×787 → 880×781. Legend 9 pt → about 18.6 px. **Geometry:** the axes run to 46% because of the 0.4 floor in `max(p.max(),0.4)*1.15`, but the data stop at 28%. About 40% of the axis span on each side is empty band. |
| Fig 4A (`...fig4-window-and-spacing_20261014.png`) | yes | Markers sit on top of each other at 1 s and 2 s (blue/aqua/orange/black), offset by only 0.06 (`f4_markers.png`). Minor. | yes | The shared y label "recovered ÷ planted − 1, fixed model (median over 48 recordings)" is unit-free and fine. The x label "window w · share of events coordinated" puts the panel's measured quantity in the x label, which reads as if it were the x quantity. Minor. | sharey across A–C, all the same ratio. OK. | A. OK. | **FAIL.** The ±25% grey band and the 0 line are not in the legend. | **FAIL.** The schedules are told apart by colour alone (all use the same ○ marker). Under simulated protanopia orange vs aqua is ΔE about 25. | Normal vision OK (ΔE ≥ 73). Protan orange/aqua is weak. | 1896×645 → 880×299 (scale 0.46). **Legend 9 pt → about 8.7 px; ticks and labels 10 pt → about 9.7 px.** Too small. |
| Fig 4B | yes | At 4 s, black and blue nearly coincide. Minor. | yes | as A | shared y. OK. | B. OK. | as A | as A | as A | as A |
| Fig 4C | yes | as B | yes | as A | shared y. OK. | C. OK. | as A | as A | as A | as A. The legend sits outside on the right and is not clipped. |
| Fig 5A (`...fig5-blind-spots_20261014.png`) | yes | The left spine at −0.3% and the axvline at 0% draw two parallel vertical lines about 25 px apart, which reads as a doubled axis. Minor. | yes | x: "share of events reported coordinated (fixed model, 1 s window)", in %. Rows are labeled. OK. | n/a | A. OK. | The 0% line is not identified (it is a reference line). "median 3.7%" is on the figure. OK. | Dots = one recording. OK. | Monochrome. OK. | 1955×698 → 880×314 (scale 0.45). Text 9 pt → about 8.4 px, ticks about 9.4 px. **Geometry:** the row labels take about 22% of the width and the data occupy only the 2–6% span. A wide gap separates A from B. |
| Fig 5B | yes | The legend's second line ends about 25 px below the 1.37 outlier. Close but no overlap (`f5_legend.png`). | yes | y: "answer ÷ planted share" (ratio). x: "shared moments planted in a 45-minute recording". OK. | n/a | B. OK. | **FAIL.** The horizontal line at 1.0 ("a perfect answer") is not identified on the figure. | ◇ = pooled median here, but ◆ = "the recording" in Fig 2B. Cross-figure conflict, minor. | Monochrome. OK. | **Legend 8 pt → about 7.5 px at 880 px.** Below legible. |

## Findings (location · issue · severity · suggested fix · verified against source)

1. **Fig 1, cue lane.** Each close pair's two ▼ (2 s apart over a 360 s span, about 8 px natively and about 4.6 px placed) overlap into one W-shaped glyph. The figure exists to show close pairs, and they read as one odd marker. **Moderate.** Fix: draw a small bracket or a "2 s" label above each pair, shrink the marker size, or add an inset zoom of the pair. Verified: yes (crop `f1_lane.png`; `s=60` at script line 236).
2. **Fig 1, all panels; README caption line 3 and body line 85.** The three stacked panels are unlettered. The caption says "lane above" and "Bottom", and the body says "the bottom row of Figure 1". **Moderate.** Fix: letter them A (planted), B (raster), C (count *X*), and refer to them by letter. Verified: yes.
3. **Fig 1 legend.** "single moment (120 s or more from the next)" is listed, but no aqua ▼ appears in the window shown, so the reader looks for an element that is not there. **Minor.** Fix: drop legend entries with zero points in view, or pick a window that contains a single moment. Verified: yes (render; the scatter at line 236 makes a legend entry even with zero points).
4. **Fig 3.** The recovered = planted diagonal is identified only in the README caption, not on the figure. **Moderate.** Fix: add `label="recovered = planted"` to `ax.plot(xs, xs, …)` (line 332). Verified: yes.
5. **Fig 3 geometry.** `lim = max(p.max(), 0.4) * 1.15` gives 46% axes for data that stop at 28%, so the points crowd into the lower-left of the plot and fixed and binomial overplot. **Minor.** Fix: use `lim = p.max() * 1.15`, or about 0.33. Verified: yes.
6. **Fig 4, A–C.** The ±25% band (`axhspan`) and the 0 line are not in the legend. **Moderate.** Fix: label the axhspan "±25% pass band" once so it joins the legend. Verified: yes (lines 363–364, no label).
7. **Fig 4.** The four gap schedules are distinguished by colour alone (all ○), against the house rule that colour is never the only identity. Orange vs aqua drops to ΔE about 25 under simulated protanopia (about 42 under deuteranopia). **Moderate.** Fix: give each schedule its own marker (○ □ △ ◇) or line style. Verified: yes (Machado simulation, ΔE in CIELAB).
8. **Fig 4 and Fig 5, placed size.** 1896 px and 1955 px wide PNGs shrink to scale about 0.45 at 880 px:
   - Fig 4: legend about 8.7 px, ticks and labels about 9.7 px.
   - Fig 5: B legend (`fontsize=8`) about 7.5 px, A text about 8.4 px.

   **Moderate.** Fix: render narrower (about 9 in wide), stack the panels in two rows, or raise the fonts to at least 12–13 pt. Fig 5A's 22%-wide row labels could become short letters or a two-line label. Verified: yes (pixel sizes measured; arithmetic as stated).
9. **Fig 5B.** The line at 1.0 ("a perfect answer") is not identified on the figure. **Moderate.** Fix: add a label or a short text "perfect answer" at the line's right end. Verified: yes (line 451).
10. **Fig 5A.** The 0% axvline sits about 25 px from the left spine at −0.3%, which reads as a double axis. **Minor.** Fix: set xlim to start at 0 and drop the axvline, or hide the left spine. Verified: yes.
11. **Cross-figure glyphs.** ◆ (filled diamond) = "the recording" in Fig 2B, while ◇ (open diamond) = "pooled median" in Fig 5B. **Minor.** Fix: use a different glyph for the pooled median, for example a horizontal bar. Verified: yes.
12. **Fig 2B tick labels.** The f₂ and f₃ category labels are about 6 px apart at the placed size and nearly run together. **Minor.** Fix: break them onto two lines ("f₂\npairs beyond chance"). Verified: yes (`f2_ticks.png`).
13. **README captions (Figs 1, 2 and 4).** The colour #1baf7a is called "aqua", but it renders as green-teal. A reader matching the caption to the figure looks for a light-blue mark. **Minor.** Fix: call it "green", or change the colour. Verified: yes (hex in script line 70; render).
14. **Fig 4 x labels.** "window w · share of events coordinated" puts the measured quantity (a y-side identity) in the x label. **Minor.** Fix: move the quantity to a per-panel heading beside the letter ("A · share of events"), or into each panel's y label. Verified: yes.
15. **Document properties.** The PNG metadata holds only `Software: Matplotlib 3.11.2`. There is no Title, Author or creation time naming this file. **Minor.** Fix: pass `metadata={"Title": …, "Author": …, "Creation Time": …}` to `savefig`. Verified: yes (PIL `info`).
16. **Run note.** `--also` copies `a.out.glob("*.png")`, which is every PNG in the darkroom folder, not only this run's five. Nothing stray is there now, but a leftover PNG would be copied into the repo silently. **Minor (build hygiene).** Fix: copy only the returned file names. Verified: yes (line 504).

Files:
- `c:\Users\defazio\bugarach\bugarach-worktrees\coordination-share-explainer\docs\learned\coordination_share_explainer\README.md`
- `c:\Users\defazio\bugarach\bugarach-worktrees\coordination-share-explainer\docs\learned\coordination_share_explainer\explain_coordination_share.py`
- the five PNGs in the same folder
