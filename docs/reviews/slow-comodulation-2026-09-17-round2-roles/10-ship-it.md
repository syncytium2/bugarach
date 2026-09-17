GRANT 10 MISMATCH — missing Grep, Glob; holds none

I held Read and Bash only. I don't have Grep or Glob, and I hold no editing tool. I used `grep` and `find`-style listing through Bash instead, so no check was skipped. The run record's `roles:` line should still say this role took a fallback path.

The build is current and matches the source exactly. All six figures rebuild to the same bytes, and the repo and darkroom copies are identical. The problems are in how the figures are drawn: one clipped tick label, a legend that is wrong for half its panels, drawing and titles over rasters, scales that change between panels without a mark, and colours that mean different things in different figures.

**Renders checked.** The shipped PNGs are in `<worktree>/docs/learned/slow_comodulation/`. My rebuild is in `<scratchpad>/review2/r10/rebuild/`, a copy measured for panel sizes is in `<scratchpad>/review2/r10/geom/`, and the zoom crops are in `<scratchpad>/review2/r10/crops/`. I opened each crop.

## One row per figure

"Build current" compares file times against the generator (changed 12:56:54), the measuring tool (13:00:05) and `results.json` (13:02:11). "Text on the column" is the smallest text once the figure is shrunk to fit the 880 px column (×0.489; ×0.469 for Figure 5, the recordings).

| Figure (render checked) | Build current | Repo = darkroom (sha1) | Rebuild vs shipped | Size (smallest text on the column) | Titles above plots | Colour, one per concept across the six figures |
|---|---|---|---|---|---|---|
| Figure 1, the count variance (`fig1_how_much_the_count_swings.png`) | PNG 13:02:13, newer than all three | a097c1a1 both | identical bytes, 0 px differ | 1800×690 → 880×337; 9 pt → **9.2 px** ("no CoactDetect arm"); ticks 10.2 px | none | CoactDetect green #238b45 is close to DI's green #1b9e77 in Figure 6, by group |
| Figure 2, the three kinds (`fig2_three_kinds.png`) | 13:02:12 ok | 5d985b30 both | identical | 1800×1650 → 880×807; ticks 10.2 px | **coloured world names sit above rasters D–F** | 20 s world **#e7298a is the exact colour of OVX** in Figure 6; 5-minute drift #8c510a is close to ORX #a65628; planted events #d95f02 is close to MALE #e6ab02 |
| Figure 3, the surrogates (`fig3_the_surrogates.png`) | 13:02:13 ok | d8bc8ebe both | identical | 1800×1080 → 880×528; ROI labels 9 pt → **9.2 px** | **a sentence title above every panel, A–D** | block-edge purple #7b3294 matches the block control elsewhere (ok) |
| Figure 4, what the surrogates remove (`fig4_what_the_surrogates_remove.png`) | 13:02:13 ok | f203b4f9 both | identical | 1800×1230 → 880×601; ticks 10.2 px | none | matches the arm colours of Figures 1 and 5 (ok) |
| Figure 5, the recordings (`fig5_recordings.png`) | 13:02:13 ok | 84cc24e8 both | identical | 1875×1230 → 880×577; ticks **9.8 px** | none | where the grey and green bands overlap they make an olive that no legend names |
| Figure 6, by group (`fig6_by_group.png`) | 13:02:14 ok | 962c21e7 both | identical | 1800×1230 → 880×601; ticks and labels 10.2 px | none | group colours collide with Figures 1, 2 and 5 (see those rows) |
| Other files in the darkroom run folder | — | `summary.json` identical (c036fc68); **`README.md` differs** (12182c54 vs b7031680) and is the 10:53 round-0 page | — | — | — | — |

No PNG has ink on any outer edge except Figure 2, at rows 184–186 on the right (panel C's "20m").

## One row per panel

Boxes are measured off the 150 dpi render, in PNG pixels and as a share of the figure's width and height.

| Panel | Box on the render | Overlap, clipping, off the page | Axis name and units | Letter present / used in the README text | Everything identified | Y-scale | Time ticks | Raster rules |
|---|---|---|---|---|---|---|---|---|
| Fig 1 A, lab fast | 386×421 px (21%W, 61%H) | **bars below 1 stand on an unlabeled floor at 0.41** (log axis, no tick under 1) | y: "variance ÷ that of independent ROIs (log scale)", a ratio; x: bin width | yes / **never used** | **hatch missing from its legend swatch** (crop f1_legend: plain green); swatches are drawn solid while bars are 85 % opacity, so they differ ((123,50,148) vs (143,81,164)) | shared, 0.41–22.6 | 1s/10s/1m ok | none |
| Fig 1 B, lab slow | same | same floor: green 1 s bar ≈0.65, lower whisker 0.49 (crop f1_B_bottom) | same | yes / never used | same | shared | ok | none |
| Fig 1 C, Dard et al. | same | **the 1m bar's whisker runs through the "no CoactDetect arm" text** (crop f1_C_topright) | same | yes / never used | ok | shared | ok | none |
| Fig 1 D, benchmark | same | ok | same | yes / never used | ok (the caption says there are no whiskers) | shared | ok | none |
| Fig 2 A, share lit | 512×132 px (28%, 8%) | 0.0/0s corner ok | "share of ROIs lit per 10 s" + time ✓ | yes / used | black step line (ok) | A–C shared at 0–0.5 | 10m steps ✓ | none |
| Fig 2 B | same | ok | tick labels hidden, shared ✓ | yes / used | ok | shared | 5m ✓ | none |
| Fig 2 C | same | **"20m" clipped at the right edge of the figure** (crop f2_rightedge_C) | ✓ | yes / used | ok | shared | 5m ✓ | none |
| Fig 2 D, planted-events raster | 512×263 px (28%, 16%) | title text above the panel; the letter's white box covers **no** events (checked from results.json) | "32 ROIs" + time ✓ | yes / used | — | 0–32 | 15s ✓, zoom from 8m45s | synthetic ✓; letter box sits inside the raster axes |
| Fig 2 E, 20 s raster | same | top-row events at 38 s and 41 s merge into the top spine (crop f2_E_tag_top) | ✓ | yes / used | — | same | ✓ | synthetic ✓; title above the raster |
| Fig 2 F, 5-minute raster | same | top-row event at 30 s merges into the spine; "1m" just fits | ✓ | yes / used | — | same | ✓ | synthetic ✓; title above the raster |
| Fig 2 G, log correlogram | 1638×386 px (91%, 23%) | legend clear of the data; "5m" fits | "excess coincidence (observed ÷ chance − 1)" + lag ✓ | yes / used | legend covers all 4 lines + dotted | G = H at −0.15–0.9 ✓ | 0.3s is off the 60-base ladder (below 1 s, low) | — |
| Fig 2 H, linear correlogram | same | ok | ✓ | yes / used | covered by G's legend | shared ✓ | 15s/30s/1m/1m30s/2m ✓ | — |
| Fig 3 A, as recorded | 1656×162 px (92%, 15%) | title above; letter box covers no events | ROI 1–4 + "time (schematic)" ✓ | yes / **not used** (caption uses B–D) | — | 0–4 | 30s ✓ | schematic, fixed numbers ✓ |
| Fig 3 B, rigid shift | same | ok; **the label says "what leaves the window is dropped", but no onset leaves** (all shifted times fall within 12–234 s) | ✓ | yes / used | — | same | ✓ | schematic |
| Fig 3 C, circular shift | same | **ROI 1 onset at exactly 0 s is half-clipped on the left spine** (crop f3_C_left) | ✓ | yes / used | — | same | ✓ | schematic |
| Fig 3 D, block control | same | **ROI 4 onset at exactly 2m sits under the dashed block-edge line** (crop f3_D_blockedge) | ✓ | yes / used | block edge in the legend, lower right | same | ✓ | **a line drawn on the raster** |
| Fig 4 A, planted events | 730×453 px (41%, 37%) | y-label reaches within 5 px of the top edge, not clipped | "excess coincidence" + world name; defined only in Figure 2 | yes / used | 6 arms in the legend ✓ | −0.15–0.9 | log lag ✓ | — |
| Fig 4 B, 20 s | same | ok | ✓ | yes / used | ✓ | −0.15–0.9 | ✓ | — |
| Fig 4 C, 5-minute | same | ok | ✓ | yes / used | ✓ | −0.15–0.9 | ✓ | — |
| Fig 4 D, benchmark | same | ok; about 100 px empty between the x-label and the legend | ✓ | yes / used | ✓ | **−0.15–1.75, unmarked** | ✓ | — |
| Fig 5 A, lab fast | 469×394 px (25%, 32%) | ok | "excess coincidence" + dataset ✓ | yes / used | 8 arms + 2 bands ✓; overlap colour not named | **autoscaled −0.26–3.29** | ✓ | — |
| Fig 5 B, lab slow | same | ok | ✓ | yes / used | ✓ | **−1.99–27.1** | ✓ | — |
| Fig 5 C, Dard et al. | same | "1.0" at the top is close to the edge, not clipped (crop f5_C_top) | ✓ | yes / used | ✓ | **−0.14–1.01** | ✓ | — |
| Fig 5 D, lab fast zoom | 469×512 px (25%, 42%) | real, 1.6 s rigid and CoactDetect-removed curves leave the zoom, with no mark on the figure; y-label 5 px from the left edge | "…, zoomed / 84 recordings, 44 mice" ✓ | yes / used | ✓ | −0.15–0.35 (the caption covers it) | ✓ | — |
| Fig 5 E, lab slow zoom | same | same 3 curves leave the zoom | ✓ | yes / used | ✓ | −0.8–0.8 | ✓ | — |
| Fig 5 F, Dard et al. zoom | same | real and 1.6 s rigid leave the zoom | ✓ | yes / used | ✓ | −0.12–0.12 | ✓ | — |
| Fig 6 A, fast as recorded | 730×453 px (41%, 37%) | curves reach 57.5 and are cut off at 0.8, with no mark | ✓ (label 10 pt) | yes / used | groups + solid/dashed ✓ | shared, −0.8–0.8 ✓ | ✓ | — |
| Fig 6 B, slow as recorded | same | curves reach 26.9 and are cut off at 0.8, with no mark | ✓ | yes / used | **legend's "heaviest mouse %" is the fast stream's number** | shared ✓ | ✓ | — |
| Fig 6 C, fast removed + block | same | C's y-label comes within about 10 px of A's "−0.8" (crop f6_C_ylabel_top) | ✓ | yes / used | ✓ | shared ✓ | ✓ | — |
| Fig 6 D, slow removed + block | same | ok | ✓ | yes / used | **same fast-stream percentages** | shared ✓ | ✓ | — |

**No real raster anywhere.** In `results.json`, only `synthetic/*` entries carry a non-null raster (6 of them). The three recording folders carry none, and Figure 3 is drawn from fixed numbers in the generator.

## Findings

Each finding gives where, what is wrong, severity, the suggested fix, and whether I checked it against a source.

1. **Figure 6 legend, panels B and D.** The "heaviest mouse N % of pairs" figures come only from the fast stream (`G0 = names[0]`), but the legend also serves the slow panels.
   - Fast stream: DI 43, MALE 48, ORX 46, OVX 37.
   - Slow stream: DI 52, MALE 56, ORX 64, OVX 64.
   - **Severity:** medium.
   - **Fix:** put both streams' shares in the legend, or scope the label ("fast stream").
   - **Checked:** yes, against `results.json`.

2. **Figure 2, panel C.** The "20m" tick label is cut off at the figure's right edge. Its ink touches the edge at rows 184–186 (crop f2_rightedge_C).
   - **Severity:** medium.
   - **Fix:** use `right=0.98`, or `ha="right"` on the last tick.
   - **Checked:** yes.

3. **Figure 3, panel D.** The dashed block-edge line is drawn on the schematic raster. ROI 4's onset lands exactly at 120 s and is hidden under the line, so a reader can't tell which block it belongs to. This breaks the CLAUDE.md "nothing is ever drawn on the raster" rule.
   - **Severity:** medium.
   - **Fix:** mark the block edge in a lane or tick above the panel, and move that onset off 120 s.
   - **Checked:** yes, from the generator's offsets: (190−120+50) mod 120 = 0.

4. **Figure 2 panels D–F and Figure 3 panels A–D.** Text titles sit above plots, which breaks CLAUDE.md's compact labelling rule. The generator's own docstring says "not in titles over the plots".
   - **Severity:** medium.
   - **Fix:** move world identity into Figure 2's y-labels or the G legend, and the surrogate descriptions into the caption or the y-labels.
   - **Checked:** yes.

5. **Figure 1, panel C.** The 1m bar's upper whisker runs through the "no CoactDetect arm" note.
   - **Severity:** medium.
   - **Fix:** move the note below the data, or raise the y-limit.
   - **Checked:** yes (crop f1_C_topright).

6. **Figure 1, all panels.** Bars on a log axis start at an unlabeled floor of 0.41, so values below 1 (panel B's green bars at 1 s ≈0.65 and 10 s) look like positive heights.
   - **Severity:** medium.
   - **Fix:** use `bottom=1` so bars grow up or down from 1, or points with whiskers instead of bars; add a tick at 0.5.
   - **Checked:** yes (ylim read from the rebuild).

7. **Figure 1 legend.** The swatch for "episodes removed, then block control" has no hatch, because `Patch(color=…)` paints the hatch in the fill colour. All swatches are also drawn solid while the bars are at 85 % opacity.
   - **Severity:** low.
   - **Fix:** `Patch(facecolor=c, edgecolor="white", hatch="///", alpha=.85)`.
   - **Checked:** yes (pixel sample and crop).

8. **Figure 5 panels A–C and Figure 4 panel D.** The same measurement is on a different y-scale per panel with nothing marking it: Figure 5's full-range row runs to 3.3, 27 and 1.0, and Figure 4 D runs to 1.75 against 0.9. The README caption only notes that the zoom differs, not the full-range row, and says nothing about Figure 4.
   - **Severity:** medium.
   - **Fix:** mark the panels on the figure ("y-scale differs") or state it in both captions.
   - **Checked:** yes.

9. **Across figures.** Colours are reused for different things:
   - #e7298a means both the 20 s world (Figure 2) and OVX (Figure 6).
   - Browns: 5-minute drift vs ORX.
   - Greens: CoactDetect removed vs DI.
   - Oranges: planted events vs MALE.

   - **Severity:** medium.
   - **Fix:** give the groups a palette used nowhere else, or use line styles for group.
   - **Checked:** yes (generator constants).

10. **Figure 1 in the README.** Neither the caption nor the "read off Figure 1" bullets use panel letters A–D. Figure 3's caption never cites A.
    - **Severity:** low.
    - **Fix:** cite the letters, e.g. "lab fast stream (A)".
    - **Checked:** yes.

11. **README, Figure 5 caption.** "Top row full range, bottom row zoomed" refers to panels by position, which the rules forbid.
    - **Severity:** low.
    - **Fix:** write "A–C full range, D–F zoomed".
    - **Checked:** yes.

12. **Figure 3, panel B.** The label says onsets that leave the window are dropped, but the schematic never drops one.
    - **Severity:** low.
    - **Fix:** use an offset that pushes one onset past 240 s, or cut that clause.
    - **Checked:** yes (all shifted onsets fall within 12–234 s).

13. **Figure 3 panel C, and Figure 2 panels E and F.**
    - Figure 3 C: ROI 1's onset at 0 s is half-clipped on the spine.
    - Figure 2 E–F: top-row onsets merge into the top spine.

    - **Severity:** low.
    - **Fix:** add a small x margin; set the y-limit to −0.2 to n+0.2.
    - **Checked:** yes (crops and results.json).

14. **Figures 5 and 6.** Curves leave the zoomed or shared range, with nothing on the figure saying so: Figure 5 D–F, and Figure 6 A and B, where values reach 57.5 and 26.9.
    - **Severity:** low.
    - **Fix:** add a small "off scale" marker at the top edge, or a note in the caption for Figure 6.
    - **Checked:** yes.

15. **All figures, text size.** On the 880 px column the smallest text is 9.2 px (Figure 1 note, Figure 3 ROI labels). Tick labels are 9.8–10.2 px against GitHub's 16 px body text.
    - **Severity:** medium.
    - **Fix:** raise the base font to 13–14 pt, or narrow the figure width so less scaling is needed.
    - **Checked:** yes (measured).

16. **Darkroom `README.md`.** It is the 10:53 round-0 page ("what it is, where it sits in time…"), sitting next to the round-1 PNGs. Someone opening the darkroom folder gets captions that don't match the figures.
    - **Severity:** medium.
    - **Fix:** copy the committed README into the darkroom, or have the builder write it there.
    - **Checked:** yes (sha1 and first line).

17. **Figure 5.** Where the grey and green bands overlap they make an olive colour that no legend names.
    - **Severity:** low.
    - **Fix:** outline the bands, or note the overlap in the legend.
    - **Checked:** yes (visual).

18. **Figure 2, panel G.** The "0.3s" tick is off the 60-base tick ladder CLAUDE.md asks for.
    - **Severity:** low.
    - **Fix:** use 0.2s or 0.5s, or accept it as a sub-second exception.
    - **Checked:** yes.
