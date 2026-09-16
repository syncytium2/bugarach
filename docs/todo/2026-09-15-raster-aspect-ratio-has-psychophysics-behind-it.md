---
status: open
filed: 2026-09-15
---

# The raster's height-to-width ratio has psychophysics behind it, and our figures cite none of it

> **Tony, 2026-09-15:** *"is there any psychophysics on evaluating rasters? the ratio of height to
> width seems to matter a lot to me"*.

`ui.diagnostic.raster_panel` already acts on that intuition. It says the raster is *"drawn short on
purpose"* because *"vertical alignment is a judgement human vision makes better the less distance it
has to carry it across"*, and the panel went from 560 px to about 200 px for thirty rows on
2026-08-26. **That sentence cites nothing.** There is a literature, and it says something sharper
than "shorter is better".

## What the literature says

**Nothing is about spike rasters.** A search on 2026-09-15 found no psychophysics of reading a
spike raster, or of how its aspect ratio changes what a person calls coordinated. The three strands
below are about dot patterns, and the mapping to a raster is ours.

- **Detecting a dotted line in dot noise — the closest paradigm.** Uttal hid dotted lines in random
  dot fields. **Dot spacing along the line is the most powerful parameter**: the closer the dots,
  the more detectable the line. Numerosity helps only to about five dots, and orientation made no
  difference, so "vertical" earns nothing by itself — what earns is that every dot shares one *x*.
  Denser masking noise reduces detectability monotonically.
  [Uttal 1973, *Vision Research*](https://www.sciencedirect.com/science/article/abs/pii/0042698973901934);
  [the millisecond-domain extension](https://link.springer.com/article/10.3758/BF03207029);
  [the masking paradigm](https://link.springer.com/article/10.3758/BF03212652).
- **Grouping by proximity — the aspect-ratio result.** Kubovy and Wagemans' dot lattices give the
  **pure distance law**: the strength of grouping along one direction falls off exponentially in the
  **ratio** of the competing inter-dot distances, and depends on nothing else — not the angle, not
  the global configuration. Changing a panel's height-to-width ratio changes exactly that ratio,
  which is why the same data read differently at different shapes.
  [Kubovy & Wagemans 1995, *Psychological Science* 6:225–234](https://journals.sagepub.com/doi/10.1111/j.1467-9280.1995.tb00597.x);
  [Kubovy, Holcombe & Wagemans 1998, *Cognitive Psychology* 35:71–98](https://www.sciencedirect.com/science/article/abs/pii/S0010028597906733).
- **Contour integration sets the wobble tolerance.** Aligned elements link into a path, and the
  tolerance to jitter is small. Our onsets carry 0.36–1.04 s of jitter, so whether an event reads as
  a line or a smear is decided by how many pixels a second occupies.
  [Field, Hayes & Hess 1993, *Vision Research* 33:173–193](https://pubmed.ncbi.nlm.nih.gov/8447091/).

**What does NOT apply, stated because it is the rule everyone reaches for.** *Banking to 45°* is
about comparing **slopes** in line charts, and
[Talbot, Gehrke & Heer 2012](http://vis.stanford.edu/files/2012-SlopeComparison-InfoVis.pdf) showed
that even there the 45° optimum was an artefact of the original design. It says nothing about
detecting an alignment.

## Our own geometry, at the settings we ship

Lab fast stream: 31 ROIs, 0.0097 Hz per ROI, about 7 participants per event, onset jitter
0.36–1.04 s. Two distances decide the reading: the **gap between participating rows** (the line's
own dot spacing) and the **distance to the nearest unrelated mark** (the mask).

| view | s per px | row pitch | gap between participants | jitter in px | nearest unrelated mark |
|---|---|---|---|---|---|
| whole baseline, 1000 px wide | 1.2 | 6.5 px | 29 px | 0.3–0.9 | ~19 px |
| 90 s zoom, 1000 px wide | 0.09 | 6.5 px | 29 px | 4–12 | ~259 px |
| group raster page, 3 px per ROI | 0.86 | 3 px | 13 px | 0.4–1.2 | ~27 px |

- **Whole baseline:** the event is narrower than a pixel — a clean column — but its participants sit
  29 px apart while unrelated marks sit about 19 px away, so by the pure distance law the mask is
  competing for the grouping.
- **The 90 s zoom:** the mask is far away, and the jitter spreads the column over 4–12 px, which is
  where it stops being a line.
- **The group raster page is the best of the three** on both distances, which is what Tony's
  intuition and the 2026-08-26 change both reached without the evidence.

## What to do

1. **Reorder rows so the line's dots are adjacent.** Spacing dominates detection, and `encode` sorts
   rows busiest-first, which scatters an event's participants across the field. A co-activity sort
   would turn a dotted column into a nearly solid one.
   [Rastermap](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC11706777/) is the neural-raster version
   of that sort. ⚠ Row order is a **coordinate** in this project (`encode`'s docstring), so changing
   it changes the model's input as well as the picture: the figure sort and the encoder sort are two
   decisions, not one.
2. **Replace the unsourced sentence in `raster_panel` with a rule and these citations**: keep the
   gap between participating rows below the distance to the nearest unrelated mark, and keep an
   event's jitter inside a pixel or two. Both are computable from the recording before the figure is
   drawn.
3. **Calibrate it on our own data.** Render planted synthetic events over a grid of aspect ratios and
   mark heights and measure detectability — by the pure distance law as a model, and by a person, so
   the number that lands in the conventions is measured here rather than transplanted from dot
   lattices.

## Closes when

`raster_panel` carries a stated, sourced rule for its height and mark size, and the figure tools
choose both from the recording rather than from a constant that was tuned once by eye.
