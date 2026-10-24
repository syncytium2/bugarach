GRANT 10 MISMATCH — missing none; holds Edit, Write, NotebookEdit (deferred), plus Agent, Artifact, PowerShell, Skill, ToolSearch, Claude Docs batch, Claude Docs update, and deferred Dropbox and Gmail tools. (I held Read, Grep, Glob and Bash as granted. I used no editing tool on any tracked file. Every scratch file is under `_scratch/r4-role-10/`. `git status` is clean apart from `_scratch/`.)

## Build currency (applies to every figure row)
- I rebuilt Figure 1 with `aim1_figure.py --out _scratch/r4-role-10/ --no-repo`, and Figures 2–4 the same way with `aim0_figures.py`. Comparing RGBA arrays, **all four shipped PNGs match their rebuilds pixel for pixel** (same sizes: 1625×988, 1690×962, 1430×598, 1690×624).
- **Inputs:**
  - `aim1_one_source.json` and `membership_limit.json` were last committed in the same commit as their scripts (905c0eda).
  - `order_limit.json` was last committed with `order_limit.py` (320e6963).
  - `theory_check.json` is from 905c0eda, but `theory.py` changed later, in 320e6963. I read that diff. In the compute path it only renames `excess_cumulants` to `predicted_excess_cumulants`; everything else is docstring text, `summary()` prints and the new `aim1_summary()`. So the JSON that Figure 2 embeds is still current.
  - I did not rerun `theory.py` `check()`, because it writes into the repo. Verified from the diff only.
- **PNG metadata names each file:** Title "Figure N, …", Author "bugarach synthetic validation (docs/learned/synthetic_validation)", Creation Time 2026-10-24T00:47–00:49. That is before the 00:56 commit and after the last input change.
- **Ink against the page edge:** at least 14 px of clear margin on every side of all four figures. Nothing runs off.
- **Size at GitHub's ~880 px column:** every figure is wider than 880 px, so it renders at full column width. Rendered boxes: Fig 1 880×535 (scale 0.542), Fig 2 880×501 (0.521), Fig 3 880×368 (0.615), Fig 4 880×325 (0.521). Placed text sizes:
  - Fig 1: tick labels 11.7 px, legend 10.3 px, y-labels 10.8 px.
  - Fig 2: 11.3 px for 12 pt text, 10.3 px for 11 pt text (legend, off-scale notes, y-labels).
  - Fig 3: 12.2 to 13.3 px.
  - Fig 4: 10.3 px legends, 11.3 px axes.
  - All of these are about 0.65 to 0.83 of GitHub's 16 px body text. Readable, but small.
- **File names** (`artifact_name.py check`): all four PNGs return `ok`. The goal page `synthetic-validation.md` returns FAIL ("expected 8 fields"), but it follows the `docs/goals/` naming convention, not the artifact convention. I list it as not applicable, not a defect.

## Output table
| Deliverable / panel | Render checked against | Axis name + units | Shared limits | Every mark identified | Overlap / clipping (zoom crops) | Colour contrast | Result |
|---|---|---|---|---|---|---|---|
| Fig 1 A–C, E–G | shipped PNG + scratch rebuild (identical) | x "planted jitter SD (s)"; y "<quantity> recovered ÷ planted" | yes, YLIM 0.05–30 on all six | **no**: legend entry "range continues below the axis" (▼) has no instance. An instrumented rerun shows zero ▼ drawn. Horizontal dodge (×0.77–×1.30 of the planted value) is not stated on the figure or in the caption | none | two greens (#1baf7a, #008300) and orange/amber (#eb6834, #eda100) are close pairs. Marker and line style separate them | FAIL (minor) |
| Fig 1 D, H | same | y "jitter SD recovered (s)" | yes, JLIM, a separate measurement | dotted identity line is in the legend; the dodge issue applies here too | none | as above | FAIL (minor) |
| Fig 2 A–C | shipped + rebuild | x "predicted ÷ planted"; y quantity "measured ÷ planted" | yes, 0.2–2.6 | yes | none | 5-cell light-blue ▼ (#86b6ef) and grey Poisson points (#9a9a9a) are a low-contrast pair at s=14–30; shape differs | pass (minor) |
| Fig 2 E | same | same | yes | yes; "3 off scale" note | none | as above | pass |
| Fig 2 F | same, crop `c2f.png` | same | yes | yes | **the off-scale note overlaps data**: "below" sits on a ▼ and "(5-cell events)" touches a grey point. The ▼ at 0.182 is counted "below" yet still drawn half-clipped on the bottom spine | as above | FAIL (minor) |
| Fig 2 G | same, crop `c2g.png` | same | yes | yes | ▼ at 0.222 (in range) is drawn half-clipped by the bottom spine | as above | minor |
| Fig 2 D | same, crop `c2d.png` | x "predicted (per min)"; y "chance clusters, background only measured (per min)" | D and H share 1e-3–20 | K=6 is given in a text note | none | violet on white is fine | K=4 interval cap sticks out of the marker: 95 % CI 0.0157–0.0241 is about ±6.7 px against a 6.3 px marker radius. The legend says "within the marker" and the caption says "smaller than the markers". Minor |
| Fig 2 H | same, crop `c2h.png` | same | yes | yes | "K = 4" label ends 21 px from the edge; not clipped | fine | pass |
| Fig 3 A | shipped + rebuild | x "reuse: events per assembly, E/M"; y "pair-count variance ÷ random" (a ratio) | n/a (different measures) | yes, legend | none | blue/orange fine | pass |
| Fig 3 B | same, crop `c3b.png` | y "recordings flagged (%, of 60)" | n/a | yes. The dotted line is labelled in text; the arrow annotates M=1 | **overlaps**: the "M = 1: only the uniform null rejects (one assembly…" annotation is crossed by both the dashed and solid lines and sits on the open-square marker at E/M = 0.045. "both reject under random participation: 2 %" is crossed by both lines at its left end, sits on the markers at E/M = 0.0045, and the arrow shaft grazes "2 %" | single violet, distinguished by fill and dash | FAIL (major: the text is hard to read and covers a data point) |
| Fig 4 A | shipped + rebuild, crop `c4a.png` | x "r = template spread ÷ jitter"; y "order indicator F" | yes, 0.04–1.1 on A–C | yes | **the lower-right legend overlaps the solid signal curve**: the curve's start runs through the "signal" handle | blue/orange fine | FAIL (minor) |
| Fig 4 B | same | x "latency templates M (r = 2.5, 2000 events)" | yes | yes. The M=1 diamond sits under the simulated point by design | the solid line runs out the bottom of the axis, clipped (expected) | fine | pass |
| Fig 4 C | same | x "events a pair of cells shares, n̄" (count); y "order indicator F, no order" | yes | yes | none | orange and dark grey fine | pass |
| Goal page `docs/goals/synthetic-validation.md` | markdown-it 4.2.0 (commonmark plus tables) render, `_scratch/r4-role-10/synthetic-validation.html` | n/a | n/a | n/a | 5 tables render (lines 40, 212, 325, 360, 544) with consistent column counts. No pipe rows are left unrendered and no stray `**`, `` ` `` or `[](…)` remains. The 4 images and 27 links/images all resolve to tracked files, including the run record `../reviews/synthetic-validation-aim0_2026-10-23.md` (existence checked only). No anchors are broken. Panels are referred to by letter only; there are no left/right/top/bottom references | n/a | pass. The empty cells in the symbols table are intentional |
| `docs/GLOSSARY.md`: jitter entry and "## Synthetic-validation vocabulary" | same render, `GLOSSARY.html` | n/a | n/a | n/a | renders as h2 plus a paragraph plus a list. All 15 links resolve to tracked files | n/a | pass |

## Findings (location · issue · severity · fix · verifiable against a source)
1. **Fig 3 B** · the M=1 annotation and the 2 % baseline label are crossed by both data lines and sit on markers; the arrow grazes "2 %" · major · move the annotation into the empty upper-left area (E/M 0.002–0.03, 40–70 %) or below the curves on the right, and put the baseline label right of E/M = 1 · yes (crop `C:\Users\defazio\bugarach\bugarach-worktrees\synth-mb-aim0\_scratch\r4-role-10\c3b.png`).
2. **Fig 1 legend** · the "range continues below the axis" ▼ entry identifies no mark: an instrumented rerun drew none · minor · draw that legend entry only when `off` is non-empty · yes (`_scratch/r4-role-10/inst1.py`).
3. **Fig 1** · series are dodged horizontally by 1.09^(i−3) (×0.77 to ×1.30), so points do not sit at their planted x, and neither the figure nor the caption says so · minor · add one caption clause ("points are offset sideways for legibility") · yes (`aim1_figure.py` line 122).
4. **Fig 2 F** · the off-scale note overlaps a ▼ and a grey point; the 0.182 point is counted "below" and also drawn half-clipped · minor · move the note to the lower right (that area is empty), and set `clip_on` or drop points outside the limits so off-scale points are not drawn · yes (`c2f.png`).
5. **Fig 2 G** · the in-range ▼ at 0.222 is half-clipped by the bottom spine · minor · lower ylim to 0.15, or set `clip_on=False` · yes (`c2g.png`).
6. **Fig 2 D, legend and caption** · "interval within the marker" / "smaller than the markers" is marginally false for K=4 at 0.01 Hz: the CI cap sticks out about 0.4 px at native size and is visible in the crop · minor · say "about the marker's size", or draw the caps · yes (`theory_check.json` chance row 0.01/4).
7. **Fig 4 A** · the legend box overlaps the start of the solid signal curve · minor · move the legend to "upper left", which is empty above 0.4 at r < 0.5, or start the curve at r = 0.15 · yes (`c4a.png`).
8. **All figures, text size** · at the 880 px column, placed text is 10.3 to 13.3 px, against 16 px body text · minor · raise to 13–14 pt, or narrow `figsize` so less downscaling occurs · yes (arithmetic above).
9. **Fig 1 and Fig 2 colour pairs** · Fig 1 has two greens and orange/amber; Fig 2 has light-blue 5-cell markers against grey · minor · already backed by marker and dash, so this is optional; darken #86b6ef or lighten the grey · yes.
10. **Run (not artifact)** · spawned through a fallback holding editing tools (GRANT MISMATCH above); the run record's `roles:` line must say fallback · n/a.

Clean: build currency (pixel-identical rebuilds, inputs current), document properties, panel lettering, axis names and units, shared y-limits, no histograms, edge margins, Markdown tables, embedded images, and every relative link and anchor in both files.
