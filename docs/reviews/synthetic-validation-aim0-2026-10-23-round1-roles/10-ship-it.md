GRANT 10 MISMATCH — missing none; holds Edit, Write, NotebookEdit, PowerShell, Agent, Artifact, Skill and MCP tools (Dropbox, Gmail, Docs and others). This was a fallback general-purpose spawn, so the run record must say the review took a fallback path. I edited no tracked file; all my writes are under `_scratch/role-10/`.

**Build currency: PASS.** On disk every file in the checkout has the same timestamp, so I used git commit times instead. `aim1_figure.py` and `theory.py` were committed at 15:40:16, and `aim1_one_source.json` and the PNG together at 15:54:13. To confirm, I rebuilt the figure from a scratch copy of the script (`_scratch/role-10/aim1_figure_scratch.py`, which saves only to scratch). The result `_scratch/role-10/synth_recovery_plot_one-source-jitter_20261023.png` is byte-identical to the shipped PNG (same md5 431ec51d…, 0 pixels differ). The rows below therefore describe the file that ships.

**Naming:** `artifact_name.py check synth_recovery_plot_one-source-jitter_20261023.png` returns `ok`.

## Output table

| # | Unit | Checked against (render) | Rendered box | Axes: name + units | Shared limits | Every mark identified | Overlap / page edge | Result |
|---|---|---|---|---|---|---|---|---|
| F1-A | Fig 1, row 0.01 Hz × participants | shipped PNG 1950×910 px at 130 dpi (15×7 in); crops `z_placed_880.png`, `z_legend.png` | each panel ≈ 440×320 px, about 22 % × 35 % of canvas; ink spans px 20–1932 × 14–908 | x: "planted jitter, SD (s)" ✓; y: "recovered ÷ planted" (ratio) ✓ | y 0.08–30 shared across all 8 panels ✓; x shared per column ✓ | yes, legend | markers overlap at ratio ≈ 1 (4 % dodge) | FAIL (no panel letter; label sits above the panel) |
| F1-B | row 0.01 Hz × events per min | same + `z_toprow_mid.png` | as above | ✓ | ✓ | as-K dashed prediction covered by the "same colour, dashed" legend entry ✓ | green K = 6 IQR bars run below the 0.08 floor and are clipped, with no mark | FAIL (clipped bars, no letter) |
| F1-C | row 0.01 Hz × coordinated share | same | as above | ✓ | ✓ | assess series absent by design; legend and caption don't say so | lines stacked at ≈ 1 | minor |
| F1-D | row 0.01 Hz × jitter | same + `z_jitter_top.png` | as above | ✓ | ✓ | the fitted series (purple) is in the legend ✓; coordination-rates series absent by design | OK | FAIL (no letter) |
| F1-E | row 0.05 Hz × participants | same + `z_botleft.png` | as above | ✓ | ✓ | ✓ | K = 3 gold and K = 4 pink IQR bars coincide; K = 6 green (#008300) and 4 s teal (#1baf7a) sit together | low-contrast pair |
| F1-F | row 0.05 Hz × events per min | same | as above | ✓ | ✓ | ✓ | OK | low-contrast pair (two greens) |
| F1-G | row 0.05 Hz × share | same | as above | ✓ | ✓ | ✓ | stacked at ≈ 1 | minor |
| F1-H | row 0.05 Hz × jitter | same | as above | ✓ | ✓ | ✓ | OK | no letter |
| F1-cap | in-figure caption and legend | `z_caption_left.png`, `z_placed_880.png` | caption ink ends 2 px from the bottom edge | — | — | grey dashed "perfect recovery" line is explained only in grey 8.5 pt caption text, not in the legend | caption ≈ 15 px tall at native size, ≈ 7 px at 880 px placed width (illegible) | FAIL |
| F1-props | PNG metadata | PIL `.info` | — | — | — | — | only `Software: Matplotlib 3.11.2`; no Title, Author or creation time | minor |
| D-1 | goal doc lines 25–163 | markdown-it (commonmark + tables) → `_scratch/role-10/goal_render.html` | — | — | — | — | — | PASS |
| D-2 | "All three reached…" table | same render | — | — | — | — | — | PASS (7 rows × 4 cols) |
| D-3 | "Three properties" table | same render | — | — | — | — | — | PASS (4 × 3) |
| D-4 | order predictions table (√, π, τ², ≈) | same render | — | — | — | — | — | PASS (4 × 3) |
| D-5 | whole-file tables (Settled 8 × 3, plus one 3 × 2) | `goal_render_full.html` | — | — | — | — | — | PASS |
| D-6 | formulas (g_n, R_n, E[(1 − R_n/w)+], (1 − q)^2, k_hat, g_3/g_2) | same render | — | — | — | — | — | PASS: no stray emphasis; `_` and `^` show literally |
| D-7 | links (11 relative links) | file existence + `git ls-files` | — | — | — | — | — | PASS: all 11 exist and are tracked |
| D-8 | plan bullets, lines 234–255 | same render | — | — | — | — | — | PASS: the 8-item list renders |

## Findings
Columns: location · issue · severity · suggested fix · verified against source.

1. **Fig 1, all 8 panels** · No panel letters (A–H). · major (house rule) · Letter the panels, e.g. a column letter by row. · yes, render plus script lines 129–134.
2. **Fig 1, column headers** · The parameter names ("participants per event (cells)" and the rest) are titles drawn above the plots with `ax.text`, against the rule "no titles above plots (identity in y-axis labels)". The y-label says only "recovered ÷ planted / background … Hz per cell". · moderate · Move the parameter identity into the axis labels, or have the main thread rule that column headers are allowed. · yes.
3. **Fig 1, panels B and F** · Two greens, K = 6 (#008300) and the 4 s window (#1baf7a), plot together and are hard to tell apart (`z_botleft.png`, `z_toprow_mid.png`). · moderate · Replace one of them with a clearly contrasting hue. · yes.
4. **Fig 1, panel B** · The K = 6 IQR bars run past ylim 0.08 and are clipped without any mark, so the reader cannot see how far they extend. · minor · Add an arrow or other off-scale mark, or lower ylim. · yes, render.
5. **Fig 1, caption** · The grey dashed perfect-recovery line is identified only in grey 8.5 pt footer text, which is ≈ 7 px tall when the figure is viewed at about 880 px wide. · moderate · Add the line to the legend and enlarge the caption, or move the caption into the doc. · yes.
6. **Fig 1, page edge** · Caption ink reaches row 908 of 910 (2 px margin). · minor · Use `bbox_inches="tight", pad_inches` or raise the text's y. · yes.
7. **Fig 1, columns C, D, G, H** · Series are missing by design: assess has no share, coordination rates has no jitter. Nothing on the figure says so, so a reader may take them as dropped. · minor · Add a note to the caption. · yes, `PARAMS` None keys.
8. **Fig 1, PNG metadata** · No Title or Author. · minor · Pass `metadata={"Title":…, "Author":…}` to `savefig`. · yes.
9. **Doc lines 51 and 169–171** · Figure 1 is named only as a code-span filename. It is not embedded or linked, so it never renders where the doc is read, and "the darkroom folder below" is a spatial reference. · moderate · Embed it with `![Figure 1](../learned/synthetic_validation/synth_recovery_plot_one-source-jitter_20261023.png)`. · yes.
10. **Doc lines 257–260 (just past the plan range given)** · "1a. … *First experiment.* 1b. …" renders as one run-on paragraph, not a list. · minor · Use a list or separate paragraphs. · yes, render.

Not checked: the darkroom/Dropbox copy of the figure (no Dropbox access was allowed).

Files are in `C:\Users\defazio\bugarach\bugarach-worktrees\synth-mb-aim0\_scratch\role-10\`:
- renders and crops: `goal_render.html`, `goal_render_full.html`, `z_*.png`
- the rebuilt PNG
- the scratch script `aim1_figure_scratch.py`

The untracked folder `docs/reviews/synthetic-validation-aim0_2026-10-23-roles/` was not created by me.
