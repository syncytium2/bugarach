---
status: open
filed: 2026-08-18
---

# SPIKE-synch's sensitivity knob does nothing on a sparse recording

`bench.OPERATING_POINTS["sync"]` sweeps `C_threshold` from 0.005 to 0.12 to trace
the detector's sensitivity curve. On the browser tuning step's default simulation
— 33 ROIs, 15 planted events, 45 minutes, 10 mHz background — **every value on
that grid returns the identical result**: four detections, four hits, eleven
misses, F1 0.42, at all six settings. The browser was checked against the Python
at each point and they agree exactly, so this is the detector's behaviour and not
a port defect.

The reason looks like the other two parameters. `C_min` is held at 0.1 while
`C_threshold` sweeps below it, so the bin that *opens* an event is cheaper to
find while every bin that *sustains* one still has to clear 0.1; and `min_n = 3`
requires three events inside the span, which a single low-C bin cannot supply. So
the swept parameter is not the binding constraint, and the sweep measures `C_min`
while reporting `C_threshold`.

The project's own bench does separate the grid — `sweep("sync", "baseline_busy")`
moves F1 from 0.58 down to 0.48 — but only across the **upper** half, with the
bottom three values tied. That is the same effect showing at a different density:
with 30 ROIs the coincidence quantum is 1/29, and thresholds below it are all the
same threshold.

**Worth deciding, and it is a calibration question rather than a code one:**

- Is `C_threshold` the right sensitivity axis for this detector at all, or is the
  pair `(C_threshold, C_min)` the thing that has to move together? A grid whose
  bottom half is degenerate cannot bracket an optimum in the sense
  `pick_operating_point` requires — it returns the first interior tie, which is a
  boundary answer wearing a plateau's clothes.
- The quantum argument says the useful grid depends on ROI count, since C can
  only take values `k/(n-1)`. A fixed grid in absolute C means something
  different for a 20-ROI field than for a 150-ROI one.

The browser says so rather than hiding it: a sweep whose every row is identical
reports that the knob is not what is deciding the answer, instead of naming a
value off a flat curve. That is a decent stopgap and not a resolution.

**Do not fix this by widening the grid until something moves.** FOUNDATIONS §9
and `bench`'s own docstring are explicit that operating points come from baseline
recordings and from measured coordination properties, not from whatever makes a
curve look like a curve.
