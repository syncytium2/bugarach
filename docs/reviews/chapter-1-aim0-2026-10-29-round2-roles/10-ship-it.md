GRANT 10 MISMATCH — missing none; holds forbidden Edit, Write, PowerShell, Agent, Artifact, Skill, Claude Docs MCP update/batch, and deferred NotebookEdit (on top of Read, Grep, Glob, Bash). I used only Read, Grep, Glob and Bash, edited nothing in the repository, and wrote only to my scratch folder. Record this as a fallback-path grant in the run's `roles:` line.

# Role 10 (Ship It): build and craft gate for `docs/dissertation/chapter-1-aim0.md`, blind verify round 2

**Artifact checked.** `docs/dissertation/chapter-1-aim0.md`. Its git hash-object is cdc8fbf6afea9df5c496b218e3e5c99fc2a8c881, which matches the run context.

**How it was rendered.**
- I sent the file through GitHub's own renderer (`gh api -X POST markdown`, gfm mode) and saved the result as scratch `work-r2-10/body.html`.
- I wrapped that HTML in a GitHub-like page: a 980 px article with 45 px padding, so the content column is 890 px wide. The page's base href was `docs/dissertation/`.
- I screenshotted it with Playwright (surrogate-screen venv) at a 1012 px viewport. Outputs: full page `work-r2-10/full.png`, one crop per figure `work-r2-10/fig1.png` … `fig11.png`.
- I opened every source PNG directly with Read.
- Renders are in my scratch folder, `…/scratchpad/mb/work-r2-10/`.

**Overall result.**
- **Build is current.** For all 11 figures, each PNG is newer than its generator and its input JSONs. The chapter (12:40:58) is newer than every PNG.
- **Images load.** All 11 images load in the render.
- **Links.** Of 22 relative links and images, 21 resolve. One does not (Finding 1).
- **Scripts and tools.** All 12 scripts listed under *Reproducing* exist, and so do the 5 tools.
- **Figures.** Figures 1.1–1.11 appear in order, and every in-text panel reference (1.1 A/D/E/H, 1.3 A/B, 1.4 D/H, 1.8 A/B) names a panel that exists.
- **Layout.** There is no horizontal page scroll at 390 px or 1012 px, and none of the 5 tables overflows.
- **Figure box.** Every figure renders 890 px wide: 100 % of the content column and 88 % of the 1012 px page.

## Findings

| # | location | issue | severity | suggested fix | verified against source |
|---|---|---|---|---|---|
| 1 | §1.9.3, "([run record](../reviews/chapter-1-aim0_2026-10-29.md))" | The link target does not exist, so on GitHub it is a 404. I only tested whether the file exists; I did not open anything under `docs/reviews/chapter-1-aim0_2026-10-29*`. | major (minor if the record is committed in the same commit) | Commit the record with the chapter, or drop the link until it exists. | yes (filesystem) |
| 2 | Fig 1.10, footnote "assessor 5 at 0.0096 Hz and 8 at 0.05 Hz (its one-per-hour chance K)" | This contradicts Fig 1.5's legend and §1.5, which both say the first K under one per hour at 0.0096 Hz is **4** cells (0.98 per hour). It comes from `separation/assessor_split/split.py` L43/L490 (`PLOT_K` hard-codes 5), which treats the 0.01 Hz value as if it applied at 0.0096 Hz. | major | Relabel the footnote ("K = 5, the one-per-hour K at 0.01 Hz"), or re-plot at K = 4. | yes (split.py, Fig 1.5 PNG, §1.5 text) |
| 3 | §1.2.2, "it is compared with this chapter's joint fit in *1.4.5*" | Wrong cross-reference. The correlogram comparison is in **1.4.6** ("The joint fit, and the correlogram tool"); 1.4.5 is the general event-train form. | minor | Change it to *1.4.6*. | yes (heading list) |
| 4 | Figs 1.2, 1.4, 1.5, 1.6, 1.7, 1.9, 1.10 | Never cited in the body text; they appear only in their own image line and caption (grep of "Figure 1.n"). | minor | Add a call-out where each result is discussed (e.g. "(Figure 1.5)" in §1.5, "(Figure 1.4)" in §1.4.4). | yes |
| 5 | Fig 1.9 (A–C vs D) and Fig 1.8 | The same line style means two things in one figure. In Fig 1.9, solid/dashed means 80 %/50 % power in A–C but fast/slow parameter set in D. In Fig 1.8, dashed means both "two templates" and the "power 0.8" reference line. | minor | Use a different encoding for one of each pair, e.g. a dash-dot reference line in 1.8 and different markers for the D series in 1.9. | yes (PNGs) |
| 6 | Figs 1.9, 1.10 on-figure labels, "fast-stream gap", "slow-stream gap", "fast stream", "real fast-stream gaps" | The figures say "stream" but the text everywhere says "fast type / slow type". | minor | Regenerate with "fast-type / slow-type intervals". | yes |
| 7 | Fig 1.9 A, k = 5 | The red † sits on top of the red square and blue circle; in C the daggers are placed above the markers. | minor | Offset the dagger above the marker, as in C. | yes (PNG) |
| 8 | Fig 1.2 D–F | The alternating light-gray bands (window and bin extents) are not identified by the legend or the caption. In C's "1 s windows" row, an empty window outline (a thin gray edge near −1.4 s) is also unexplained. The "1 s windows" label box covers the first bands. | minor | Add "gray bands: windows/bins" to the legend, and drop the empty-window outline. | yes (PNG) |
| 9 | Fig 1.3 A | The annotation "Gaussian and uniform differ by at most…" runs across the dotted reference line. In B, the gray dotted line at k̂/k = 1 is not labeled. | minor | Move the annotation left of x = 2√3; label the line or say in the caption that it marks 1. | yes (PNG) |
| 10 | Fig 1.3 caption, "for 5, 10 and 20 cells per event. Points are medians…" | Points exist only for 10- and 20-cell events (the on-figure note says so), but the caption reads as if all three have points. | minor | "Lines for 5, 10 and 20 cells; points for 10 and 20." | yes |
| 11 | Fig 1.5 legend, "95 % interval" | No interval is visible because each is smaller than its marker. The 0.01 Hz and 0.0096 Hz lines also run off the bottom of the axis at K ≥ 8 with no mark. | minor | Add "(intervals smaller than markers)", as Fig 1.4 does. | yes (PNG) |
| 12 | Fig 1.1 caption, "markers are dodged horizontally for visibility" | The caption attaches this to D and H only, but A–C and E–G are dodged too (assessor squares are offset from the window circles). | minor | Say "in all panels". | yes (PNG) |
| 13 | Fig 1.6, on-figure "M = 1 (rightmost):" | A spatial word inside a figure. It names a point, not a panel, so it is borderline under the rule. | minor | Label the point directly, e.g. "M = 1, E/M = 45". | yes |
| 14 | Six reused PNGs (Figs 1.1, 1.4, 1.6, 1.7, 1.9, 1.10) | Document properties name the goal-page record, not this chapter. Embedded PNG `Title` reads "Figure 1/2/3/4/5/6 … (Aim 0/1a)", which disagrees with chapter numbering 1.1/1.4/1.6/1.7/1.10/1.9. Filenames carry 20261023/20261025 although all were regenerated 2026-10-29. The five new figures carry chapter-specific titles. | minor | Re-save the chapter copies with chapter titles, or accept that they are shared files and note it in `docs/dissertation/figures/README.md`. | yes (PNG tEXt chunks) |
| 15 | §1.4.2 vs §1.4.1/1.4.3/1.5/1.6.1 equations | Display equations render inconsistently on GitHub. f₂/f₃ are 4-space indented and become gray monospace code blocks. g_n, g₂, k̂, q, 60q(1−q)² and 1+(E−1)/M are 2-space indented, which GitHub drops, so they become ordinary body paragraphs. | minor | Use one convention: all as code blocks, or GitHub `$$…$$` math. | yes (body.html) |
| 16 | The Synfire-comparison table (§1.6.2) and the old/new table (§1.9.1) | Unnumbered and uncaptioned, while Tables 1.1–1.3 are numbered. | minor | Number them 1.4 and 1.5 with captions. | yes |
| 17 | Figs 1.9, 1.10 (and 1.4, 1.7) at the rendered width | Scaled to 0.49 of native size (0.53 for 1.4 and 1.7), tick and legend text renders at about 8–9 px on a 1× display. It is legible but at the floor. Figs 1.5 and 1.11 give about 40 % of their width to the legend. | minor | Enlarge fonts for the chapter copies, or put legends below the plot. Whether more canvas is warranted is role 9's call. | yes (render) |
| 18 | Cross-figure color reuse | Violet means the joint fit in 1.1, chance clusters in 1.4, the 13-cell count detector in 1.10, and the slow bench level in 1.11. Orange-red (13-cell assessor) and the red 3.8 s dash-dot line in 1.10 are a low-contrast pair. | minor | Reserve violet for the joint fit across figures, and make the 3.8 s line dark gray. | yes |

## Per-figure and per-section table

| row | checked against (render / file) | rendered box | build current | axes name+units | legend / every mark identified | panels lettered, shared y | figure ↔ text | result |
|---|---|---|---|---|---|---|---|---|
| Fig 1.1 | `fig1.png`; `docs/learned/synthetic_validation/synth_recovery_plot_one-source-jitter_20261023.png` (1625×988) | 890×541 px, 100 % col / 88 % page | PNG 12:10:15 > aim1_figure.py 12:08, aim1_one_source.json 08:57 | ✓ (ratios; jitter in s) | ✓ (dodging note incomplete, #12) | A–H ✓; A–C/E–G and D/H share y ✓ | Values in §1.1 for D and H (0.07–0.72; 0.43–0.68) and for A/E (0.34–0.42) match the plot | pass, minor |
| Fig 1.2 | `fig2.png`; `docs/dissertation/figures/synth_raster_plot_data-and-what-each-tool-sees_20261029.png` (1575×1980) | 890×1119 px, 100 % / 88 % | 12:37:18 > ch1_new_figures.py 12:36:43 | ✓ | gray bands and empty window not identified (#8) | A–F ✓ | 4/6 split, threshold 5 and σ 0.2 match the caption; not cited in body (#4) | pass, minor |
| Fig 1.3 | `fig3.png`; `docs/dissertation/figures/synth_recovery_plot_window-sharing-and-participant-bias_20261029.png` | 890×453 px | 12:37:52 ✓ | ✓ (dimensionless ratios labeled) | k̂/k = 1 line unlabeled; annotation overlap (#9) | A, B ✓ | 0.02/0.04 ✓; caption points wording (#10) | pass, minor |
| Fig 1.4 | `fig4.png`; `docs/learned/synthetic_validation/synth_recovery_plot_one-source-predicted-against-measured_20261023.png` | 890×507 px | 12:12:27 > aim0_figures.py 12:12:22, theory_check.json 11:52 | ✓ | ✓ (off-scale counts annotated) | A–H ✓; ratio panels share limits ✓ | D's K = 6 of 5×10⁻⁵/min matches the "0.2 in the arm" in §1.5; not cited (#4) | pass, minor |
| Fig 1.5 | `fig5.png`; `docs/dissertation/figures/synth_recovery_plot_chance-clusters-against-threshold_20261029.png` | 890×516 px (plot about 60 % of figure width) | 12:37:52 ✓ | ✓ | CIs invisible (#11) | single panel | 4/5/8 cells and 0.98/h match §1.5; conflicts with Fig 1.10 (#2); not cited (#4) | minor |
| Fig 1.6 | `fig6.png`; `docs/learned/synthetic_validation/synth_assembly-membership_plot_assemblies-converge-to-random_20261023.png` | 890×372 px | 12:12:28 > membership_limit.json ✓ | ✓ | ✓ | A, B ✓ | 72 %, 13 %, 100 % for E/M 1–15, and 1/60 and 3/60 ✓; "rightmost" (#13); not cited (#4) | pass, minor |
| Fig 1.7 | `fig7.png`; `docs/learned/synthetic_validation/synth_recovery_plot_order-indicator-closed-forms_20261023.png` | 890×438 px | 12:12:31 > order_limit.json ✓ | ✓ | ✓ | A–C ✓, shared log y ✓ | 0.503/0.753 and 0.376/√n̄ ✓; not cited (#4) | pass, minor |
| Fig 1.8 | `fig8.png`; `docs/dissertation/figures/synth_recovery_plot_order-power-against-event-count_20261029.png` | 890×475 px | 12:37:52 > order_power.json 12:20 ✓ | ✓ | dashed used for two concepts (#5) | A, B ✓, sharey ✓ | All 24 plotted values match Table 1.3 | pass, minor |
| Fig 1.9 | `fig9.png`; `docs/learned/synthetic_validation/separation/floor/synth_recovery_plot_separation-floor-any-method_20261025.png` (1800×1440) | 890×712 px, scale 0.49 | 12:19:57 > bound.py 12:19:47 ✓ | ✓ (Δ in s) | ✓, but style double-use (#5), dagger overlap (#7), "stream" (#6) | A–D ✓; A–C sharey ✓ | 0.44 s and 0.59 s, and the 0.26–0.76 s range, match the green 80 % points; not cited (#4) | minor |
| Fig 1.10 | `fig10.png`; `docs/learned/synthetic_validation/separation/assessor_split/synth_recovery_plot_assessor-split-against-separation_20261025.png` (1800×1500) | 890×742 px, scale 0.49 | 12:15:09 > split.py 12:15:05 ✓ | ✓ | ✓; red-on-orange contrast (#18) | A–H ✓, sharey ✓ | Assessor rise about 2.5 s and count detector about 5 s match §1.7; **K footnote contradicts Fig 1.5 (#2)**; not cited (#4) | **major** |
| Fig 1.11 | `fig11.png`; `docs/dissertation/figures/synth_recovery_plot_realistic-values-against-tested-grid_20261029.png` | 890×538 px (plot about 58 % of width) | 12:37:52 ✓ | ✓ | ✓ (box sizes nominal, per caption) | single panel | Ranges agree with §1.4.6 (0.88–1.13 for 10+ cells, σ ≥ 0.2) | pass |
| §1.1–1.10 headings and section refs | body.html heading list | — | chapter 12:40:58 is newest | — | — | — | 15 of 16 *x.y* refs resolve; *1.4.5* in §1.2.2 is wrong (#3) | minor |
| Tables 1.1–1.3 plus 2 unnumbered | body.html; Playwright (scrollWidth = clientWidth for all 5) | ≤ 890 px, no overflow | — | — | — | — | Table 1.3 matches Fig 1.8; 2 tables unnumbered (#16) | minor |
| Equations | body.html (`<pre>` vs `<p>`) | — | — | — | — | — | Mixed display (#15) | minor |
| Relative links and images (22) | Filesystem test from `docs/dissertation/` | — | — | — | — | — | 21 OK, 1 missing (#1) | **major** |
| *Reproducing* scripts and tools (17) | Filesystem test from the worktree root | — | — | — | — | — | All exist | pass |
| Phone width | Playwright at 390 px viewport | scrollWidth 390, no horizontal scroll | — | — | — | — | — | pass |

## What I checked
- **Render:** GitHub's markdown API, then Playwright screenshots of the full page and each figure, at 1012 px and 390 px.
- **Figures:** all 11 source PNGs (axes, units, legends, panel letters, shared limits, overlaps, clipping, colors) and their embedded PNG metadata.
- **Build currency:** mtimes of each PNG against its generator script and input JSONs.
- **Links and paths:** every relative link and image, every script and tool path, figure and table numbering, and section cross-references.
- **Figure numbers against text:** Fig 1.8 against Table 1.3; Figs 1.1, 1.5, 1.6, 1.7, 1.9 and 1.11 against the values quoted in the text.

I did not open `docs/reviews/chapter-1-aim0_2026-10-29*`. I only tested whether the linked path exists.

**Count:** two major findings (#1, #2) and sixteen minor.
