---
status: open
kind: new-rule-request
raised: 2026-08-26
about: SAP009's neighbour — "a marker above a raster points down"
---

# The down-triangle rule wants mechanizing and a line matcher cannot do it

CLAUDE.md's plot conventions gained a rule on 2026-08-26, hours after SAP009:
every marker in a lane above a raster points **down**, because it is an
annotation on the raster and an annotation points at its subject. Six call sites
were converted by hand, by two sessions that did not know about each other —
PR #334 took the benchmark cue lane, PR #335 the other five. Nothing stops the
seventh, and the near-simultaneous duplicate is itself the argument: a rule
carried in prose gets applied by whoever happens to read it.

The obvious rule — fire on `marker="triangle"` under `tools/**` and
`src/bugarach/ui/**` — is wrong, and here is the case that makes it wrong:

    tools/make_benchmark_figures.py, build_map()
        marker="triangle"      # a simulated recording, plotted as a point in a
                               # crowded-vs-rate scatter

That triangle is not above anything. It is a data point in an ordinary scatter
plot, where the shape distinguishes simulated recordings from real ones and
"down" would mean nothing at all. A blanket match blocks it, and a rule that
cries wolf on the only correct use in the tree is a rule somebody deletes.

## What separates the two cases, and why sapper cannot see it

The rule is about **where the mark sits relative to other data**, which is a
property of the figure's layout and not of the line. In the lane cases the y
value is a constant just past the top of the panel below —
`np.full(n, n_roi - 0.5)`, `np.zeros(n)` in a lane of its own,
`float(max(ks)) + 1.0`. In the scatter case the y value is the measurement.
Telling those apart needs to know what the y array *is*, which is a parser's
job, and sapper is a line matcher on purpose (SAP009 says so in its own
comment).

## What might work, and its cost

SAP009's answer to the same problem was **to work by naming**: hold a raster in
a variable called `raster` and the regex can see it. The equivalent here would
be a naming convention for lanes — a marker overlay assigned into something
matching `*lane*` or `*_marks`, and a rule that fires on `marker="triangle"`
only on such a line. Today two of the six sites would match (`planted_lane`,
`lane = lane * hv.Scatter(...)`) and four would not, so adopting it means
renaming at four call sites for the benefit of a check.

That may well be worth it — it is the same trade SAP009 already took — but it is
a convention change and belongs to whoever decides SAP009's family, not to the
session that noticed the gap. Filing it rather than guessing.

## In the meantime

The rule is written in CLAUDE.md directly under SAP009, which is where somebody
about to draw a lane is already reading, and every converted site carries a
one-line comment naming the convention. That is prose holding a rule, which is
what sapper exists to replace — so this is a real gap, not a closed one.
