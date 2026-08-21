---
status: done
filed: 2026-08-20
closed: 2026-08-21
---

# DONE — the rate now says which statistic it is, and the generator handles either

Closed by Tony's own proposal, 2026-08-21: *"can we flag the input to the
generator as median or mean so the generator can handle either?"* — which is this
repo's existing idiom rather than a new one. `strength_unit` travels with
`strength`; `width_def` travels with `width_sec`; both because a column that
means two things without saying which yields a plausible wrong answer rather than
an error. A bare per-ROI rate was that column.

## Two corrections to what this file originally said

**The generator was never wrong.** `simulate.py` documents `bg_rate_hz` as the
**mean** per-ROI rate, and `bench.REGIMES` states its endpoints as the
interquartile spread of slice-**mean** rate. The bench and the generator agreed
all along. The defect was one line in the calibration path handing them a median.
This file's option 1 claimed the bench states medians — **that was wrong**, and it
came from reading the webapp's own rate-box note, which was quoting `REGIMES`
endpoints that moved on 2026-08-20 and had not been updated. Both are fixed.

**The 0.45x figure was the fixture, not the calibration error.** It came from a
comparison whose "real" folder was a **flat** Poisson field, where the median and
the mean are one number. That conflated the knob mismatch with the two fields
having different shapes. The honest numbers:

- on a real, uneven field the median and mean differ by **4.8x**, consistently
  (0.209 / 0.209 / 0.211 measured at the bench's three regime points);
- feeding the median into a mean knob therefore under-produced the field's mean
  by that factor;
- through the real loop with a **heterogeneous** folder, the mean now lands at
  **0.98x** of the recording it was measured from, against ~5x too low before.

## What the flag is

Per-ROI rates are drawn `Gamma(k, rate/k)`, whose mean is exactly `rate`. The
median is the same scale times `median(Gamma(k,1))`, so the ratio depends on the
shape alone:

    median / mean = median(Gamma(k, 1)) / k

At the fitted `MEASURED_RATE_SHAPE` of 0.275 that is **0.209838** — the typical
ROI fires at about a fifth of the field's mean, which is what a field with a few
busy cells and a third of them silent looks like.

`simulate.median_over_mean(shape)` computes it without scipy, which is not a
dependency of this package; `tests/test_rate_statistic.py` checks it against
scipy across shapes and against the closed form `ln 2` at `k = 1`, and pins the
browser's constant by recomputing it from the shape the page itself declares, so
the two cannot drift.

`simulate.rate_as_mean(rate, stat, shape=…)` converts, and **refuses a rate that
does not say which statistic it is** rather than guessing.

## And the default moved to the mean, which is a separate claim

Not merely because the knob wants one. The median is a bad estimator of this
distribution at real ROI counts: at 33 ROIs the sample median spans **0.56 to
5.56 mHz** between its 5th and 95th percentiles around a population value of
2.14, and comes back exactly **zero about one run in a hundred**. The mean is
steady. Both the browser's calibration step and `adapt.py` now hand over the
mean; anyone holding a median can still pass one and say so.

`test_the_median_is_a_noisy_estimator_at_real_roi_counts` measures this rather
than asserting it.

## The Python half was latent, and is now impossible rather than documented

`adapt.py` mapped `roi_rate_med -> bg_rate_hz` and its own table already carried a
⚠ on that exact row for a **different** ambiguity — total rate versus background.
It was harmless only because nothing there sets `bg_rate_shape`, so Python runs a
flat field where the two statistics coincide. Wiring in `MEASURED_RATE_SHAPE`,
which that constant exists to allow, would have made it live at 4.8x with nothing
watching. The flag closes it before it opens.

## What is still open, and is not this

The **shape** of the generated field is only checked by the comparison screen's
second row, and that row is noisy at real ROI counts. Matching a mean says
nothing about matching a distribution —
[`the generator's background is flat`](2026-08-14-generator-background-model-is-flat.md)
is the file about that, and the browser's `fitted` background is its answer;
whether Python should get the same treatment is
`MEASURED_RATE_SHAPE`'s "⚠ not wired into the bench" note, still open.
