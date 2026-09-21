GRANT 10 MISMATCH — missing Grep, Glob; holds no forbidden tools (held: Read, Bash)

## Build & craft gate: rigid-shift look, first review round

I did not edit anything in the repo. The probe PNGs, rebuilds and zoom crops are under `<scratchpad>/mb_scratch/role10/`. Since I have no Write tool, the probe ran inline through `python -c`.

**The six PNGs match the current code and inputs.** Each is newer than `tools/make_rigid_shift_look_figure.py` and newer than its `results.json`. I rebuilt all three runs into scratch from the committed generator at 616f124 (the worktree is clean). All six PNGs match the rebuilds pixel for pixel, and so do all three `destruction_table.json` files. All six Markdown image links resolve to tracked files.

**How the checks were run:** I drew each figure again at 160 dpi and measured every visible text box: tick labels inside the axis limits, axis labels and legend text. I then viewed each full PNG and zoomed into the spots in question.

**No overlaps or clipping anywhere.** No text collides with other text, no legend covers a plot area, and nothing is within 8 px of an image edge. Ink starts at least 16 px from every edge.

**Assumed display width:** I took about 900 px for GitHub's Markdown column. That width is an assumption, not a measurement.

| Render checked | Panel (no letters exist, so named by content) | Plot box, px (% of image) | Overlap / clip | Axis name + units | Every mark identified on the figure | Shared y where comparable | Elements the generator draws are visible |
|---|---|---|---|---|---|---|---|
| `fig1_leak_count.png` 1600×1216 | fast leak | 616×425 (13.5 %) | clean | y ok; x "displacement J", unit only on ticks | **no**: dotted 0.5, dashed 0.55, the dot | **no**: 0.447–0.839 vs slow 0.467–0.785 | yes |
| same | fast count | 616×425 (13.5 %) | clean | y "(%)" ok; x as above | **no**: ±2 % band, dotted 0, grey control | near (−5.33 vs −5.41), not shared | yes; control has no slice bar |
| same | slow leak | 616×425 (13.5 %) | clean | as fast leak | **no** | **no** | yes |
| same | slow count | 616×425 (13.5 %) | clean | as fast count | **no** | near | yes |
| `fig2_destruction.png` 1840×1488 | fast 1 s bin, participation 0.2 and 0.5 | 643×394 each (9.3 %) | clean; column gap 32 px | ok (K in ROIs; fraction on y) | **no**: dashed 0.25 line, 95 % bars; legend 7 pt | yes (sharey) | yes |
| same | slow 1 s bin, both participations | 643×394 each (9.3 %) | clean | ok | **no** | yes | yes |
| same | slow 2 s bin, both participations | 643×394 each (9.3 %) | clean | ok | **no** | yes | yes |
| `larger-displacements/fig1_leak_count.png` 1600×1216 | fast leak / fast count / slow leak / slow count | 616×425 each (13.5 %) | clean | as `fig1` | **no** (same lines) | **no**: leak 0.435–0.860 vs 0.467–0.822; also differs from `fig1` | yes |
| `larger-displacements/fig2_destruction.png` 1840×1488 | three rows × two participations | 643×394 each (9.3 %) | clean | ok | **no**; 10 s and 40 s swatches cannot be told apart | yes | 20 s and 40 s lines hard to see near 0 |
| `cossart/fig1_leak_count.png` 1600×608 | events leak | 623×369 (23.7 %) | clean; "40 s" and "edge thinning" ticks 13 px apart | as `fig1` | **no** | single row | **dither range bars hidden behind the markers** |
| same | events count | 623×369 (23.7 %) | clean | as `fig1` | **no** | single row | yes |
| `cossart/fig2_destruction.png` 1840×496 | events 1 s bin, participation 0.2 | 632×378 (26.2 %) | clean; x-limits end on the 146 tick | ok | **no** | yes | **4 of 5 displacement lines hidden under the grey control; no mark at K = 146** |
| same | events 1 s bin, participation 0.5 | 632×378 (26.2 %) | clean; x-limits differ from the 0.2 panel | ok | **no** | yes | **4 of 5 displacement lines hidden under the grey control** |

## Findings

| # | Location | Issue | Severity | Suggested fix | Verified |
|---|---|---|---|---|---|
| 1 | `cossart/fig2_destruction.png`, both panels; generator line 128 (`zorder=4`) | The homogeneous-resample control is drawn on top of the rigid-shift lines, so the 5, 10, 20 and 40 s lines cannot be seen (zoom crop `c_cossart_fig2_zero_right.png`). The key result ("from 5 s every displacement removes all of it") appears only as missing lines. The Figure 6 caption says the reverse: the control "sits under the rigid-shift lines". | major | Offset the controls or draw them as hollow squares, or add an on-figure note ("5–40 s: 0 at every K"). Make the caption match the render. | yes |
| 2 | Legends in all three `fig2_destruction.png` files (generator lines 25 and 136) | Displacement J is shown only by dash pattern, in one colour with one marker, in a 7 pt legend. In the swatches, solid and dashed look nearly the same, and the 20 s (`-.`) and 40 s (`(5,1,1,1)`) patterns are identical (crops `c_cossart_fig2_legend.png`, `c_large_fig2_legend.png`). | major | Add a second channel: a light-to-dark ramp or distinct markers per J. Or label the line ends directly. Make the legend handles longer. | yes |
| 3 | Legend text in all `fig2_destruction.png` files | 7 pt at 160 dpi is a 15.6 px em. At about 900 px display width the 1840 px image shrinks to 0.49×, which gives about 7.6 px text. This legend is the only key to J. For comparison, fig1's 8 pt legend displays at about 10 px. | major | Legend at 9–10 pt; narrow the figure or move the legend above the panels as fig1 does. | yes for the pixel sizes; no for the display width, which is assumed |
| 4 | `fig2_destruction.png` ×3: dashed grey line at 0.25 | Not in the legend or on the figure. The Figure 2 caption does not mention it either; only the preamble lists "0.25". The same dashed style also marks the second J in the same panel, so one style stands for two things. | major | Label it on the figure ("0.25 threshold") in a style no J uses, e.g. a thin solid grey line. | yes |
| 5 | `fig1_leak_count.png` ×3: dotted 0.5, dashed 0.55, dotted 0, ±2 % shaded band, grey edge-thinning point, the dot marker | None of these appears in the figure legend. The legend covers the two colours and the two bar widths only. The chance line and the zero line share the dotted style, and what the dot means (point accuracy or change share) is never stated. | major | Add legend entries or short labels on the lines ("chance", "0.55", "±2 %"). Add "dot: point estimate". | yes |
| 6 | fig1 leak panels, `fig1` and `larger-displacements/fig1` | The same measurement uses different y-limits across rows (0.447–0.839 vs 0.467–0.785; 0.435–0.860 vs 0.467–0.822) and across the two figures, with no mark. The slow-stream leak rising toward 0.55 is read against a threshold line at a different height in each panel. Count panels differ slightly too (−5.33 vs −5.41). | major | `sharey` per column, and one fixed range for the lab leak panels in both runs. | yes |
| 7 | All six PNGs; README lines 54–58, 65–66 and 105–115 | No panel letters. The captions use position words ("Left panels", "Right panels", "fast above and slow below", "Rows", "Columns"). | major | Letter the panels (A–D, A–F) and name them in the captions by letter plus content. | yes |
| 8 | `cossart/fig1_leak_count.png`, uniform dither | Range bars are short (0.97–1.00) and hidden behind the 5 pt markers; only a sliver of the thin bar shows (`c_cossart_fig1_dither.png`). The legend promises thick and thin bars that the reader cannot see. | minor | Smaller or hollow markers, or say in the caption that the ranges are narrower than the marker. | yes |
| 9 | `cossart/fig2_destruction.png`, participation 0.2, K = 146 | No point for either the controls or the shifts. The empty slot looks like a dropped element; only the caption explains it. The two panels' x-limits also differ (52.25–146.00 vs 50.45–150.55). | minor | Put an "n/a: event < K" mark at K = 146 and share x. | yes |
| 10 | README line 115, "as in Figure 2" | Inherits "Bars are 95 % over the 20 twin pairs", but the Cossart run has 10 pairs per variant (`results.json`). | minor | Figure 6: "Bars are 95 % over the 10 twin pairs." | yes |
| 11 | README lines 4–5; generator docstring line 8 | Says "the dashed lines at 0.55, ±2 % and 0.25", but ±2 % is drawn as a shaded band, not a dashed line. | minor | "The dashed lines at 0.55 and 0.25 and the shaded ±2 % band…" | yes |
| 12 | fig1 x-axes, all three renders | "displacement J" has no unit in the label (only the ticks carry "s"). The count-panel x-axis also holds the edge-thinning control, which is not a J. Tick format "1.6 s" differs from the house `45s` style; whether the 60-base convention applies to a category axis is a judgement call for adjudication. | minor | "displacement J (s)"; set the control apart with a gap or a divider. | yes |
| 13 | fig2 x labels "participation 0.2 / 0.5" vs README "20 % / 50 %"; fig1 legend "1.67–98.33 %" | Participation is a fraction on the figure but a percent in the text. "%" in the legend reads as a percent, not a percentile. | minor | "participation 20 % of ROIs"; "1.67th–98.33rd percentile over mice". | yes |
| 14 | `cossart/fig1_leak_count.png` count panel ticks | "40 s" and "edge thinning" are 13 px apart (about 7 px at display width). | minor | Put a gap before the control category. | yes |
| 15 | Controls across figures | Grey circle for the edge-thinning control in fig1, grey square for the controls in fig2. The two greys (#7a7a7a and 0.45 grey) are nearly the same. | minor | One control glyph across both figures. | yes |

## Checked with nothing to report

- **Build currency:** the PNGs are newer than the generator and its inputs, and they reproduce exactly.
- **Image links:** all six resolve.
- **Edges and overlaps:** no text clipped or overlapping in any render.
- **Spacing:** fig2 columns are 32 px apart, not touching; no wide empty margins beside the figures.
- **Shared y in fig2:** all three `fig2_destruction.png` files use `sharey`, and the y-range is the same across the three figures.
- **House layout rules:** no titles above the plots; identity and counts sit in the y-axis labels.
- **Document properties:** not applicable. These are PNGs with no author or title fields; the dpi metadata reads 160.
