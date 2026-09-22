GRANT 10 MISMATCH — missing Grep, Glob; holds none forbidden (holds Read, Bash)

# Build and craft check: slow co-modulation figures, first review round

I checked four renders in `<worktree>/docs/learned/slow_comodulation/`:
- `fig1_three_kinds.png` (1875×1320 px)
- `fig2_what_the_surrogates_remove.png` (1875×690 px)
- `fig3_recordings.png` (1935×1080 px)
- `fig4_by_group.png` (1860×1050 px)

I viewed each one at full size and zoomed into crops of the edges, legends and busy regions. The crops are in `<scratchpad>/review/r10/crops/`. I measured panel boxes by re-running the generator's drawing functions and reading the axes positions. "@880" means the size on a GitHub column about 880 px wide. The README embeds each image with plain `![...]()`, so each figure fills the full column, scaled by 0.455 to 0.473.

## Build check (all four figures)

| Check | Result | Evidence |
|---|---|---|
| Built files newer than their inputs | **pass** | measure script 10:49:16 → `results.json` 10:51:19 → generator 10:52:03 → PNGs 10:53:32. Worktree is clean, committed at 8ba5f57. |
| Repo copy matches darkroom copy | **pass** | SHA-1 is identical for all 4 PNGs, `README.md` and `summary.json`. The run folder's `results.json` matches the darkroom copy. |
| Reproducible | **pass** | I re-ran the generator into `.../scratchpad/review/r10/`. All 4 PNGs came out byte-identical (same SHA-1, 0 pixels differ). |
| No real raster in the repo | **pass** | The Figure 1 rasters come from `synthetic_recording()` (`measure_slow_comodulation.py`, `raster` is set only for the first synthetic recording of each world). No recording row in the folder results has a `raster` key, and the repo's `summary.json` contains no "raster". |
| File properties | **pass, nothing to stamp** | The PNG text chunks hold only `Software: Matplotlib 3.11.1` and dpi. No template creation date or author was inherited. |

## Figure 1, the three kinds

| Panel | Box in PNG (% of figure) → @880 | Overlap / clip | Elements present | Axis name + units | Letter | Identified | Shared y | Smallest text @880 |
|---|---|---|---|---|---|---|---|---|
| A, B, C share-of-ROIs-lit lanes | 537×146 px (29%×11%) → 252×69 px each | none. **103 px of empty space below each lane**, more than the lane's own height | step line ✓ | y: "share of ROIs lit, 10 s bins" (a fraction, so no unit needed) ✓. No x axis; it is linked to the raster below ✓ | A/B/C, one letter covers lane and raster | the y label identifies the step line ✓ | 0–0.8 on all three ✓ | tick labels 10 pt → 9.8 px |
| A, B, C rasters | 537×366 px (29%×28%) → 252×171 px | none | 32 rows of black ticks ✓. Nothing is drawn on the raster; cues sit in the lane above ✓ | y: "32 ROIs, one recording" ✓. **x: no axis name**; ticks read 0s/5m/10m/15m. Ticks are minutes-friendly ✓ | shares its column's letter | n/a | 0–32 ✓ | 9.8 px |
| D, the cross-correlogram | 1697×457 px (90%×35%) → 796×214 px | none. The black curve peaks at 4.31 with the axis top at 4.52, so it is not clipped. The "5m" tick label ends 12 px from the image edge | 5 worlds ✓. The `events_shared` world is computed but not drawn anywhere, and the README never mentions it | x: "lag between onsets in two different ROIs"; units are in the tick labels (0.25s…5m) ✓. y: "excess coincidence (observed ÷ chance − 1)", unitless and defined ✓. **The symlog y axis has only 2 tick labels (0 and 10⁰)** | D | legend covers all 5 curves ✓. The light zero line is unlabelled (conventional) | single panel | legend 8.5 pt → **8.3 px** |

## Figure 2, what the surrogates remove

| Panel | Box → @880 | Overlap / clip | Elements | Axis name + units | Letter | Identified | Shared y | Smallest text @880 |
|---|---|---|---|---|---|---|---|---|
| A, planted events | 508×449 px (27%×65%) → 238×210 px | none. The "0" and "10⁻¹" tick labels are about 40 px apart and clear | 6 arms ✓ | x ✓ (units in ticks); y ✓, defined | A | figure-wide legend at the bottom, 6 entries ✓ | **symlog (linear within ±0.5), −0.23 to 4.5. The figure itself never says this; only the caption does** | legend 8.5 pt → 8.3 px |
| B, shared modulation 20 s | 508×449 px → 238×210 px | none | 6 arms ✓ | x ✓; **no y label on this panel** (it relies on A's) | B | legend ✓ | **linear, −0.08 to 0.91 (autoscaled)** | 8.3 px |
| C, shared drift 5 min | 508×449 px → 238×210 px | none. "5m" ends 3 px from the image edge (not cut off) | 6 arms ✓ | as B | C | legend ✓ | **linear, −0.06 to 0.69 (autoscaled)** | 8.3 px |

## Figure 3, the recordings

| Panel | Box → @880 | Overlap / clip | Elements | Axis name + units | Letter | Identified | Shared y | Smallest text @880 |
|---|---|---|---|---|---|---|---|---|
| A peak, lab fast | 518×398 px (27%×37%) → 235×181 px | none | 7 arms plus 2 shaded bands ✓ | y: "the peak: full range / excess coincidence". No definition (it is in Figures 1 and 2). x ticks have no labels (the axis is linked to the row below) ✓ | A covers the whole column | **bands not explained in this row** | **autoscaled, −0.3 to 3.6** | titles 9.5 pt → 9.0 px |
| B peak, lab slow | same | none | 7 arms plus 2 bands ✓ | no y label (uses A's) | B | as A | **autoscaled, −2 to 28.8** | 9.0 px |
| C peak, Cossart | same | none | 6 arms plus 1 band. **The green "CoactDetect episodes removed" curve is missing because the data have no such arm, and nothing on the figure says so** | as B | C | as A | **autoscaled, −0.14 to 1.1** | 9.0 px |
| A shoulder, lab fast | 518×498 px (27%×46%) → 235×226 px | **the legend does not cover any curve** (zoomed crop checked). Curves leave the top at +0.7 on purpose, and the y label says so | ✓ | **y label names no quantity**: "the shoulder: zoomed to ±0.7 / shaded: 95 % interval over mice". x ✓ | no letter of its own | legend lists 7 arms but sits inside this one panel; the bands are explained in the y label | ±0.7 on all three ✓ | **legend 7.5 pt → 7.1 px** |
| B shoulder, lab slow | same | none; the light-blue and black curves leave the top on purpose | ✓ | no y label | none | no legend of its own. Navy (rigid shift, J 20 s) and black (as recorded) cross in the dip and are hard to tell apart | ±0.7 ✓ | 9.0 px |
| C shoulder, Cossart | same. "5m" ends 4 px from the edge | none | green missing, as in C peak | no y label | none | as B | ±0.7 ✓ | 9.0 px |

## Figure 4, the lab streams by group

| Panel | Box → @880 | Overlap / clip | Elements | Axis name + units | Letter | Identified | Shared y | Smallest text @880 |
|---|---|---|---|---|---|---|---|---|
| A top, fast, as recorded | 776×435 px (42%×41%) → 367×206 px | the legend sits clear of the lines (zoomed crop checked); lines leave the top on purpose | 4 group lines plus 4 bands ✓ | y: "as recorded, zoomed to the shoulder / excess coincidence" ✓ (not defined). x ticks have no labels (linked) ✓ | A covers the column | legend for all 4 groups ✓. **Bands (alpha 0.08) explained nowhere on the figure** | −0.7 to 0.8 ✓ | **legend 8 pt → 7.9 px** |
| B top, slow, as recorded | same | none; bands run past +0.8 on purpose | ✓ | no y label | B | uses A's legend; bands not explained | ✓ | 9.8 px |
| A bottom, fast, block control | same | none | ✓ | y: "circular shift within 2-minute blocks / excess coincidence" ✓. x ✓ | none | bands not explained | ✓ | 9.8 px |
| B bottom, slow, block control | same. "5m" ends 3 px from the edge | none. Overlapping bands form a solid brown block past +0.8 | ✓ | no y label | none | bands not explained | ✓ | 9.8 px |

## Findings

Format: location · issue · severity · suggested fix · checked against a source (yes/no)

1. **Colours across all four figures** · The same colour means different things in different figures:
   - #111111 black is the planted-events world in Figure 1 but "as recorded" in Figures 2 and 3.
   - #c2502a is the 20 s shared-modulation world in Figure 1 but the 2-minute block control in Figures 2 and 3.
   - #9a9a9a grey is independent ROIs in Figure 1 but the circular-shift null in Figures 2 and 3.

   Figure 2's panels are titled with the world names, so a reader coming from Figure 1 sees the "shared modulation" colour in panel B of Figure 2 and it means something else there. Figure 4's MALE orange (#d95f02) is also close to the block-control orange, in the row that plots the block control. · **major** · Give the synthetic worlds a palette that no surrogate arm uses (for example, draw Figure 1's worlds in a set disjoint from `INK`), and move MALE off orange-red. · yes (`WORLD_INK` and `INK` in the generator, checked in the renders)

2. **Figures 2 and 3, rigid shift J 20 s against as recorded** · Navy #08306b and black #111111 have a luminance contrast of about 1.5:1. The navy line is 1.5 pt and about 1.5 px wide at 880. They sit close together in Figure 2 B and C and cross in Figure 3 B shoulder. Light blue #9ecae1 on white is about 1.75:1 and faint. · **major** · Draw as recorded as a heavier line in another hue or dashed, or pull the blue ramp away from near-black; make the lightest blue darker. · yes (colour arithmetic plus zoomed crop of Figure 3 B shoulder)

3. **README captions for Figures 1, 3 and 4 (and Figure 2's "events panel")** · Panels are named by position: "top row", "below it", "left column", "middle column", "right column", "bottom panel", "Top row / Bottom row". The rows of Figures 3 and 4 have no letters, so the text has nothing else to use. · **major** · Give every panel its own letter (Figure 1: seven, Figure 3: six, Figure 4: four) and have the captions use the letters. · yes (`README.md` lines 43–47, 70, 96, 145)

4. **Figure 2, y scales** · Same measurement on three different scales: A is symlog, B and C are linear with separate autoscaled limits (0.91 vs 0.69). The figure itself does not mark this; only the caption does. The README compares heights across these panels ("+0.75 … +0.35"). · **major** · Share linear limits between B and C. Mark A's symlog on the panel ("log beyond ±0.5"), or give A a broken or inset axis. · yes (measured y limits)

5. **Figure 4, shaded bands** · The 95 % interval bands appear in all four panels but the figure never identifies them (only the caption does). At alpha 0.08 they are nearly invisible at 880 px, except in B bottom, where they pile into a solid block. · **major** · Add "shaded: 95 % interval over mice" as a legend entry with a swatch, next to the figure. Raise alpha or show bands only where they carry the argument. · yes (render plus generator)

6. **Figure 3 shoulder row, y label** · "the shoulder: zoomed to ±0.7 / shaded: 95 % interval over mice" never names the quantity. The top row has only "excess coincidence", without the definition. · **minor** · "excess coincidence, zoomed to ±0.7". Put the band note in the legend. · yes

7. **Figure 3, legend placement and completeness** · The single 7-entry legend sits inside the A shoulder panel, so it reads as that panel's. The top-row bands are not explained in that row. Column C lists "CoactDetect episodes removed" in the shared legend but has no such curve, and the figure does not say so. · **minor** · Use a figure-level legend as in Figure 2, with band swatches and "(lab folders only)" on the green entry. · yes (the `cossart/events` arms in the results have no `minus_coact`)

8. **Legend text size at the placed size** · Figure 3's legend is 7.1 px at 880; Figure 4's is 7.9 px; Figures 1 and 2 are 8.3 px; panel titles in Figure 3 are 9.0 px. This is about half of GitHub's body text size. · **minor** · Raise legend and title sizes to about 11–12 pt at this figure width, or reduce the figure's inch size so matplotlib's defaults render larger. · yes (measured font sizes × dpi × scale)

9. **Figure 1 D, y axis** · The symlog axis shows only the "0" and "10⁰" tick labels. The README reads values off it ("starts at about +0.75"), and a reader cannot recover that from the render. · **minor** · Add ticks at 0.25, 0.5 and 0.75 and at 2 and 4, or use a linear axis with a broken top. · yes

10. **Figure 1 rasters, x axis** · No axis name; only tick labels. Also, "0s" is really 60 s into a 1,200 s recording (the window is `t0=60`, `t1=1140`), and neither figure nor caption says so. · **minor** · Label it "time from 1 min into the recording" (or plot the full 0–20m). · yes (generator)

11. **Figure 1 layout** · 103 px of empty space between the share lanes and the rasters, taller than the 146 px lanes themselves (69 px at 880). The uniform `hspace=0.32` makes room for titles where there are none. · **minor** · Use a separate gridspec gap for that row, or put the lane directly on top of its raster. Whether the lanes deserve more height is the layout reviewer's call. · yes (measured)

12. **Figure 3 top row, y limits** · Each folder is autoscaled (3.6 / 28.8 / 1.1), and only A's y label says "full range". · **minor** · Label every panel's own scale, or add "y scale differs per panel" to the row label. · yes

13. **Zoom range, Figure 3 vs Figure 4** · Figure 3 zooms the shoulder to ±0.7; Figure 4 zooms the same kind of curve to −0.7 to 0.8. · **nit** · Pick one range. · yes

14. **All four figures, titles above panels** · Every panel has a title above it ("A. lab, fast stream · 84 recordings, 44 mice"). The CLAUDE.md plot conventions say "no titles above plots; identity + counts live in y-axis labels". Panel letters are still required, so the letter could stay as a corner tag. I am recording this for the main thread to decide, not calling it a defect. · **minor** · Move identity and counts into y labels or a caption, and keep only a letter tag. · yes (CLAUDE.md, generator)

15. **Lag axis ticks** · The 0.25s tick is outside the 1/2/5/10/15/30 × 60^k family; the other ticks (1s/5s/15s/1m/5m) follow it. Nothing is in raw seconds. · **nit** · Acceptable, or drop to 1s as the first tick. · yes

16. **`events_shared` world** · Computed in the results (24 recordings, 6 arms) but drawn in no figure and never mentioned in the README. · **nit** (for the main thread) · Drop it from the run, or show and mention it. · yes

17. **Right-edge padding, Figures 2, 3, 4** · The last "5m" tick label ends 3–4 px from the PNG edge. It is not cut off (zoomed crops checked), but there is no margin. · **nit** · `right=0.98` or `bbox_inches="tight", pad_inches=0.05`. · yes

18. **Review run itself** · My grant was missing Grep and Glob; I used grep inside Bash instead. No editing tool was present. · run finding, not artifact · Record it in the ledger; the `roles:` line should say this reviewer ran on a fallback grant. · yes

Nothing overlaps or is cut off in any of the four renders, and nothing the generator draws is missing, apart from the Cossart column's CoactDetect curve, whose data do not exist. Findings 1 through 5 are the ones to fix before this ships.
