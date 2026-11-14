# Chapter 1 figure repairs (2026-10-29)

These are repairs to the figures the Chapter 1 (Aim 0) review found defective
(`docs/reviews/chapter-1-aim0-2026-10-29-round1-roles/`, roles 03, 04, 08 and 10). Every figure was
redrawn from its existing record, and no simulation was rerun. File names are unchanged, so links
from the chapter and from the goal page still work. Run all commands from the repository root
with `PYTHONPATH=src`. The `--out` flag points the darkroom copy somewhere else; without it, the
scripts also write to the darkroom folder (`2026-10-23-synthetic-validation`).

## Fig 1.1 / goal Figure 1: recovery against planted jitter (`aim1_figure.py`)

- **Panels D and H:** the four jitter series (assessor K = 3, 4, 6 and the joint fit) are now
  dodged symmetrically about the planted jitter. The factor is 1.15 per series, so the outermost
  series sits about 23 % off the planted value.
- **Markers:** they are smaller in these two panels (5 pt), with slight transparency. The K = 4
  series can now be picked out at every planted jitter.
- **Note:** each panel says "markers dodged horizontally for visibility". Panels A–C and E–G are
  unchanged.
- Command: `python docs/learned/synthetic_validation/aim1_figure.py`

## Fig 1.2 / goal Figure 2 (`aim0_figures.py`, `fig2`)

- **Off-scale note:** the "N off scale" annotation in panels E–G is now narrower and wraps one
  item per line. It sits in the empty lower-right corner and no longer covers data.
- **"grey":** the figure text never contained the word, so nothing changed here. The caption's
  "grey points" is in the chapter, which this pass does not edit.

## Fig 1.4 / goal Figure 4, panel C: order indicator with no order planted (`aim0_figures.py`, `fig4`)

- **Score sort is now derived, not fitted:**
  - Solid line: the exact finite-n̄ mean, computed with `kendall_w.F_exact` (the lattice
    convolution) over integer event counts E = 3–1000.
  - Dotted line: the derived asymptote c(N, k)/√n̄, with c(33, 10) = √(4(k+1)/(3πN)) = 0.376.
  - Both are labeled "derived". The "fitted 0.38/√n̄" line is gone.
- **Local search:** it keeps "fitted 0.50 / √n̄, local search".
- **Axis extended:** the n̄ axis now starts at 0.25.
  - The record `order_limit.json` starts at n̄ = 2.1.
  - The two points below that (n̄ = 0.43 and 0.85, i.e. E = 5 and 10) come from the separate
    200-recording check in `kendall_w/kendall_w_output.txt`, section C. The script parses that
    file.
  - They are drawn as open markers, with a legend entry "open: separate check, 200 recordings".
- **Color:** the closed-form lines are now the same blue in panels A, B and C.
- **Layout:** the legends moved below their panels, and the log axes show plain numbers.
- Command: `python docs/learned/synthetic_validation/aim0_figures.py` (this redraws Figs 1.2,
  1.3 and 1.4; Fig 1.3 itself is unchanged).

## Fig 1.5 / goal Figure 5: two-cluster split against separation (`separation/assessor_split/split.py`)

- **Re-export:** 12 in wide instead of 17 in (1800 × 1500 px). At 922 px the smallest text is
  about 11 px tall, against about 5 px before. The figure stays as one image, not split.
- **Panel titles:** now two lines (jitter SD; background).
- **Legend:** split into two columns, series and glyphs. The K values moved to a note below
  the legend.
- **Wording:**
  - "centre" → "center"
  - "+-1" → "±1"
  - ">= 20" → "≥ 20"
  - "2 x" → "2 ×"
  - "E-H" → "E–H"
  - "ADR-0008 floor" → "the event floor (the count chance first exceeds)"
- **Metadata:** the PNG now carries Title, Author and Creation Time.
- Command: `python docs/learned/synthetic_validation/separation/assessor_split/split.py --plot-only`

## Fig 1.6 / goal Figure 6: resolvable separation, any method (`separation/floor/bound.py`)

The `make_figure` function was rewritten.

- **Points that resolve at every Δ tested:** these entries ("any", a value of 0) are no longer
  clamped onto the curves.
  - Each is a downward triangle at the axis floor, in its series' color, with no line running to
    it. Filled means 80 % power and open means 50 %.
  - An open triangle is drawn only where 80 % is not also "any".
  - Series are dodged sideways so coincident triangles stay apart.
  - Legend entry: "resolves at every separation tested (shared cells alone), drawn at the axis
    floor".
- **Reference lines:** panels A–C now share y. The labels sit outside the plot area to the right
  of panel C, with thin leader lines, and each panel's 2σ line is labeled "2σ" in the gap after
  the panel. No data crosses a label.
- **Size:** 12 in wide (1800 × 1440 px). The smallest text is 10.5 pt, about 11 px tall at 922 px.
- **Assessor line:** it now sits at 2.5 s, labeled "assessor: half its split plateau at 2.5 s".
  Before, it was at 3 s and labeled "assessor floor 3 s".
- **Panel letters:** uppercase, A–D.
- **Spelling:** "centres" → "centers".
- **y-axis label:** now "resolvable separation Δ (s)". σ and 2σ moved into each panel's title.
- **Curve family renamed:** "within-cell floor g" is now "within-cell minimum interval" (0.1 s
  as stated in the model; measured values 0.4 s fast and 3.2 s slow). Panel D's legend uses the
  same term.
- **Size-inflated entries:** an entry whose test size exceeds 0.075 (the derivation's † rule;
  `size_pooled_max` or `size_identity_max` from the record) gets a † in the series' color above
  its 80 % point.
  - Legend: "test size above 7.5 % (mostly σ = 0.5 s, few cells): anti-conservative, value
    optimistic".
  - The record also flags one entry at σ = 0.105 s: cell identity at 0.1 s, k = 5, with a size of
    0.077. That matches † in derivation Table 2.
- **Metadata:** the PNG now carries Title, Author and Creation Time.
- Command: `python docs/learned/synthetic_validation/separation/floor/bound.py --figure`

## Not fixed here: text that now disagrees with the figures

The chapter and the goal page were outside this pass, so their captions still need these edits:

- **Fig 1.6:**
  - The caption still says "(a–c)", "Panel d", "within-cell floor g" and "assessor floor 3 s".
  - It should now describe the ▼ glyph and the †.
  - Panels A–C now share a y axis.
- **Fig 1.4:**
  - The caption should say what the lines in panel C are: the derived exact mean, the derived
    asymptote, and the fitted local search.
  - It should also note the open points from the separate check.
- **Fig 1.1:** the caption should mention the dodge in D and H.
- **Fig 1.5:** the caption could explain the sawtooth ripple (finding 08-12). That is not a
  figure change.
- **Figs 1.1–1.4:** the PNG Title metadata still reads "Figure 1"–"Figure 4" (the goal page's
  numbering).
- **Fig 1.3:** its on-figure note "M = 1 (rightmost)" was not asked for and is unchanged.
- **Darkroom copies:** they were not refreshed, because these runs wrote their darkroom copy to
  a scratch folder. Rerun without `--out` to refresh them.

## Round 2

The round-2 figure changes (Figures 1.4, 1.9, 1.10, 1.11 and 1.14 in the chapter's final
numbering, and three new figures: the mechanisms schematic, participant residuals on both records,
and the joint fit against the correlogram tool) are logged in
[`docs/dissertation/figures/round2_figure_changes.md`](../../dissertation/figures/round2_figure_changes.md).
The chapter's figure numbers changed when its sections were reordered; the README there keeps the
working numbers.
