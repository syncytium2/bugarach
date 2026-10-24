GRANT 10 MISMATCH — missing none; holds Edit, Write, PowerShell, Agent, Artifact, Skill, ToolSearch, Claude Docs MCP (batch/update), and NotebookEdit through deferred loading. These are forbidden editing and publishing tools and I used none of them. I was spawned through the inline fallback, so the run record's `roles:` line must say the review took a fallback path.

# Role 10 (Ship It): render table and findings

The build is current: all four figures rebuild from the current scripts to pixel-identical copies, so the table describes the files that ship. The page has one blocking defect: the link to the review's run record points to a file that does not exist. Six major findings are below the table.

**What I checked:**
- **Rebuild:** I rebuilt all four figures into `_scratch/r2-role-10/` with `--no-repo` and compared them pixel by pixel with the shipped PNGs.
- **Overlap pass:** I re-ran both generators with `savefig` patched to measure every text box against every other text box, every line and marker, and the canvas edge (`_scratch/r2-role-10/overlap.py`).
- **Zoom-crops:** `_scratch/r2-role-10/crop_*.png`.
- **Edge margins:** measured from the ink in each PNG.
- **Page render:** I rendered the goal page and `docs/GLOSSARY.md` with markdown-it (gfm-like) and resolved every image and relative link against `git ls-files`.
- **Names:** `artifact_name.py check` on all four file names.

For the one broken link I checked only whether the target exists, by path. I did not open it.

## Output table

| Row | Render checked against | Build current | Overlap / off-page | Elements present | Axes: name and units | Shared limits | Letters | Every mark identified | Colour | Placed text | Rendered box | Name check | Metadata |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Fig 1, A–H | shipped PNG 1950×962 px + scratch rebuild + crops `crop_fig1_B/H` | **yes**: rebuild identical; PNG 23:32 is newer than the script (23:22), `aim1_one_source.json` (23:05) and `theory.py` (23:16) | none. Down-triangle in B sits on the x-axis spine. Left ink margin 7 px (row labels) | all 7 series. Fit is absent from C/G and coordination rates from D/H by design, and the caption says so | yes: ratio panels and "planted jitter SD (s)" | y shared (0.05–30), x shared | A–H inside the panels, clear of data | dashed line in legend. IQR bars and ▼ are explained only in the caption, not on the figure | **fail**: orange (2 s window, #eb6834) vs red (K = 6, #e34948) is a low-contrast pair; blue (1 s window) vs violet (joint fit) is close; red IQR bars at alpha 0.7 render pink, like K = 4 | **fail**: 9–10 pt at 1950 px wide → about 8 px em at about 900 px column width (body is 16 px) | full column width; 8 panels of 268×286 px (@100 dpi), 18 % W × 39 % H each; gaps about 96 px | ok | Title and Author set; no creation date |
| Fig 2, A–C and E–G | shipped PNG 1950×988 + rebuild + `crop_fig2_EF_bottom` | **yes**: identical; newer than `aim0_figures.py` (23:26) and `theory_check.json` (23:18) | none. The off-scale counts (3/4/2) match the data: y only, no x off scale, none in the top row | yes | yes | 0.2–2.6 on both axes in all six panels | A–H outside the panels, top-left | **fail**: dashed diagonal (y = x) is in neither the legend nor the caption | grey vs amber/blue/green ok. Blue/amber/green carry different meanings here than in Fig 1 | **fail**: same scale as Fig 1; "N conditions off scale" is 8.5 pt → about 7 px | 18 % W × 34 % H per panel | ok | Title and Author set |
| Fig 2, D and H | same + `crop_fig2_D`, `crop_fig2_H` | yes | **fail (D)**: the diagonal runs through "K = 4" and through "K = 6: none predicted, none measured". In H, "K = 3" runs past the axes' right edge but stays on the page (24 px margin) | yes. K = 6 at 0.01 Hz is shown as text; its predicted value is 5.1e-5, not 0 | yes: "(per min)" | D and H shared (1e-3 to 20) | yes | violet points and their IQR bars are not in the legend (caption: "bars: interquartile range"); the diagonal is unlabeled | ok | same failure | same | ok | ok |
| Fig 3, A–B | shipped PNG 1430×572 + rebuild | **yes**: identical; newer than `membership_limit.json` (23:20) | none; margins ≥18 px | yes | yes ("E/M", "%") | **fail (x)**: same x quantity, but A spans 1e-4 to 1e2 and B about 3e-3 to 60. In A the model curve fills two decades that hold no data | A, B outside | yes: legend in A; "5 % by chance" on B | ok | 9–10 pt at 1430 px → about 11 px em, better | 43 % W × 76 % H per panel | ok | ok |
| Fig 4, A–C | shipped PNG 1950×598 + rebuild | **yes**: identical; newer than `order_limit.json` (23:19) | none; margins ≥17 px | yes. The predicted curve in B is a polyline through 7 values of M, with a visible kink at M = 2 and a long chord from 16 to 64 | yes (dimensionless) | **fail**: "order indicator F" on all three panels, but A is linear 0–1, B log about 0.035–0.9, C log about 0.04–0.35, and the difference is not marked | A–C outside | yes: legends in A, B, C; caption explains the dotted line | **fail (C)**: score sort orange #eb6834 vs local search red #e34948, the low-contrast pair again | **fail**: same as Fig 1 | 28 % W × 77 % H per panel | ok | ok |
| Goal page `docs/goals/synthetic-validation.md` | markdown-it render `_scratch/r2-role-10/goal.html` | n/a | n/a | 4/4 embedded images resolve to tracked files | n/a | n/a | the text refers to panels by letter only; no spatial words | n/a | the caption says "violet" for the fit, which matches the legend colour | n/a | 3 tables, column counts consistent (4/3/2) | n/a | **fail: 1 of 17 relative links is broken** |
| `docs/GLOSSARY.md` (new blocks) | markdown-it render of the full file | n/a | n/a | the new blocks render as list and paragraph, no stray code block; 2 links to the goal page, both tracked | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | ok |

## Findings
Columns: location · issue · severity · suggested fix · could I verify it against a source.

1. **Goal page, line 29** · The link `[run record](../reviews/synthetic-validation-aim0_2026-10-23.md)` points to a file that is neither tracked nor on disk. Only the `…-roles/` and `…-round2-roles/` folders exist under that prefix. · **Blocking** · Commit the run record at that path, or point the link at a file that exists. · yes (`git ls-files` and `test -e`)
2. **Fig 2, panel D** · The dashed diagonal crosses the "K = 4" label and the "K = 6: none predicted, none measured" note. · Major · Move the K labels to the upper-left side of the points, and move the K = 6 note to the upper left of the panel. · yes (overlap script and `crop_fig2_D.png`)
3. **Fig 2, all 8 panels** · The dashed y = x line is identified nowhere: not in the legend, not on the figure, not in the caption. The violet chance-cluster points and their IQR bars in D and H are not in the legend. · Major · Add "prediction = measurement" to the legend, and add a legend entry for the violet points (median, IQR). · yes
4. **Figs 1 and 4C, colour** · Orange #eb6834 and red #e34948 are a low-contrast pair:
   - In Fig 1 they are the 2 s window and the assessor at K = 6.
   - In Fig 4C they are the score sort and the local search.
   - In Fig 1 the red IQR bars at alpha 0.7 render pink and read as K = 4.
   - Blue #2a78d6 against violet #6250d6 is also close.

   · Major · Use a clearly separated hue, or vary marker shape as well; drop the alpha on the bars. · yes (render)
5. **Figs 1, 2 and 4, placed text size** · The PNGs are 1950 px wide and set 8.5–10 pt text. At page column width (about 900 px, an assumption) that is about 7–8 px per em, roughly half the body size. Fig 3 (1430 px wide) comes out at about 11 px. · Major · Shrink `figsize` toward about 7–10 in wide or raise the font sizes so placed text is near body size. · yes (pixel arithmetic; the column width is assumed)
6. **Fig 4, A–C** · The same measurement, order indicator F, is drawn on three different y scales (linear 0–1, then two different log ranges) without marking the difference. · Major · Share a log y-axis across A–C, or state the difference on the figure and in the caption. · yes
7. **Fig 3, A vs B** · The same x quantity (E/M) has different limits in the two panels. A shows about 1.5 decades of model curve with no data. · Minor · Share x-limits, from about 3e-3 to 100. · yes
8. **Fig 4, panel B** · The "predicted" curve is drawn only at the 7 simulated values of M, so it shows a kink at M = 2 and a long straight chord from 16 to 64. Both read as features. · Minor · Evaluate the closed form on a dense M grid. · yes
9. **Fig 1** · The IQR bars and the down-triangle are identified only in the caption, not on the figure. · Minor · Add a "median, IQR" legend entry and a ▼ entry. · yes
10. **Across figures** · Colour meanings change between figures:
    - Blue is the 1 s window in Fig 1, 10 cells per event in Fig 2, and "predicted" in Figs 3–4.
    - Violet is the joint fit in Fig 1, chance clusters in Fig 2, and detection in Fig 3B.

    Panel letters sit inside the panels in Fig 1 and outside in Figs 2–4. · Minor · Keep one meaning per colour across the page, and place panel letters the same way in every figure. · yes
11. **Fig 2, panel D note** · "none predicted" stands for a predicted 5.1e-5 per min. The note's own threshold is < 1e-3. · Minor · Write "< 0.001 predicted, none measured". · yes (`theory_check.json`)
12. **PNG metadata, all four** · Title and Author are set, but there is no creation or modification timestamp. Fig 4's metadata title ("The order indicator…") differs from its caption ("an order indicator…"). · Minor · Pass `"Creation Time"` in the `savefig` metadata, and align the title with the caption. · yes

**Passed:** build currency (all 4); naming (`ok` for all 4); every image resolves; panel letters on every panel; every axis carries a name and, where it has one, a unit; shared y-limits within Figs 1 and 2; no histogram annotations; no spatial panel references in the page text; table structure; the GLOSSARY renders cleanly.
