---
status: open
filed: 2026-08-27
---

# `problem_view.png` breaks the raster rule and nothing in the tree can re-render it

> Found while choosing figures for the learned-detector page. Two independent review
> roles reached the same verdict and one of them checked the harder half: there is no
> generator.

`docs/learned/problem_view.png` is a three-panel figure — ROI raster, cells-active
trace, center−surround response — and its top panel **draws on the raster twice**:
green up-pointing triangles for planted events, and a cream shaded span for the probe
block. CLAUDE.md is explicit that neither belongs there (*"Nothing is ever drawn on the
raster… Every detection, planted event, treatment window, anchor or other cue goes in a
lane above it"*), and a directional marker points **down**, at the raster it describes.

**The usual repair is not available.** `grep -rn problem_view tools/` returns nothing.
No script in the tree produces this file. Its only consumer is
`docs/learned/report.src.html`, which embeds it by name.

So this is not the `tube_view.png` case, where the tool exists, was half-fixed on
2026-08-26, and simply needs re-running (that one is
[`docs/sapper_feedback/2026-08-27-sap009-misses-an-overlay-through-a-named-variable.md`](../sapper_feedback/2026-08-27-sap009-misses-an-overlay-through-a-named-variable.md)).
Here the artifact is an **orphan**: a published figure that violates a standing
convention, with no path from the repository to a corrected version.

## Three options, and the middle one is probably right

- **Write the generator.** The figure is a raster, a coactivity trace and a DoG
  response over one bench recording — every ingredient is in `bugarach.bench`,
  `learn.encode` and `learn.nets`. Real work, and it produces a figure nothing
  currently asks for.
- **Retire it.** Drop the embed from `report.src.html`, rebuild that report, delete the
  PNG. That report is already superseded by the bake-off, so the cost is low and the
  convention violation leaves the tree.
- **Leave it and label it.** The pattern the repo uses elsewhere — *quote the picture,
  and say when the picture is behind*. Cheapest, and it leaves a rule-breaking raster
  on a published page indefinitely.

## The general point, worth keeping

**An artifact with no generator cannot be corrected, only deleted or excused.** Every
committed figure in `docs/learned/` should name the tool that makes it — most do,
in the report prose or the tool's own docstring. A sweep for the ones that do not is
half an hour and would catch the next orphan before it is published rather than after.
