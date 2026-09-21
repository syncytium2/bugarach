---
status: open
filed: 2026-09-09
---

# An optimum at the edge of its grid refuses on the coded branch and only warns on the learned one

> **Not murderboarded** — working material for sessions in this tree. **If any of it
> reaches an outside reader, murderboard that artifact first.**

Found while running the full senktide + TTX cohorts through the loop, where it decided
what the best-performing learned model shipped at.

## The same condition, two verdicts

This project has a written position on an optimum that lands on the boundary of the
grid it was searched over. `bench.EdgeOfRange`'s own docstring states it:

> *"Not a warning. An optimum at the edge is not an optimum — it is the search telling
> you it stopped too early, and reporting it as a calibrated point is how a boundary
> value once got published upstream as one."*

`pick_operating_point` raises it, `tools/refit.py` reports it as an outcome, and
`tools/settings_from_bakeoff.py` will not emit such a value without `--allow-edge`,
which stamps the file to say so. That is the coded branch.

On the learned branch the same condition is a `RuntimeWarning` from
`learn/train.py`, the fit continues, the checkpoint is written, and the model runs on
real recordings. `learned_settings.csv` does record `threshold_at_grid_edge`, which is
the honest half — the value is knowable. Nothing acts on it.

## What it cost here, concretely

On this cohort's own generator spec, `tube` is the best learned model and second overall
on the bake-off (F1 0.678, fold range 0.665–0.716). Its fitted threshold is **0.9999,
the top of the searched grid `[0.0001, 0.9999]`**, flagged `threshold_at_grid_edge: yes`.
It was saved to a checkpoint and run on all 67 recordings.

So the best learned detector in this run is deployed at a threshold the coded branch
would have refused to publish, and the refusal that exists to catch exactly this never
fired because it is not wired to this branch.

`trace` and `tiny` are at the other edge (0.0001) and also flagged, but that is their
known degenerate-control behaviour rather than a search that stopped early — 78 calls
across 29 recordings, one span per analysis window. Two different problems wearing one
flag, which is its own reason to want a verdict rather than a boolean.

## Why this is a decision and not a patch

Making the learned branch refuse is a one-line change and it is **not obviously right**:

- The threshold grid is a probability in `(0, 1)`, so "widen it" means going to
  `1 - 1e-5` and further, and there is always another decimal place. The coded knobs have
  natural ranges; this one does not, so an edge here may mean *"the model separates
  cleanly and any high threshold works"* rather than *"the search stopped too early"*.
  Those two want opposite responses.
- `tube` at 0.9999 has a **probe rate of 1.37/min**, inside its own three-run history
  (0.75 pilot, 2.05 published). It is not behaving like a detector at a runaway operating
  point, which is what an edge-of-grid value would normally predict.
- A refusal would have blocked this run's learned half entirely, and the learned half is
  what `#508`/`#509` existed to make reachable.

So the question is not "should it refuse" but **which of the two meanings an edge has
for a probability threshold**, and that is answerable by measurement: sweep `tube`'s
threshold past 0.9999 on the bench and see whether F1 is flat (separates cleanly) or
still climbing (stopped too early). Nobody has.

## What to do

1. **Measure it.** Extend the threshold grid for the tube variants past 0.9999 and
   report whether F1 is flat or climbing there. One probe, and it settles the question.
2. **Then decide the verdict**, and make it the same kind of object on both branches —
   a refusal, or a stamped-and-allowed value like `--allow-edge`, not a warning nothing
   reads.
3. **Separate the two flags.** `threshold_at_grid_edge` currently means both "search
   stopped early" and "this control is degenerate". Those need different names.

Related: [`2026-09-08-the-ratio-tube-cannot-count-cells.md`](2026-09-08-the-ratio-tube-cannot-count-cells.md)
— the ratio arms read 0.00/min on the probe by arithmetic rather than by merit, which is
the other place a learned model's number means less than it looks like it means.
