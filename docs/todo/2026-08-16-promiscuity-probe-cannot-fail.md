---
status: open
filed: 2026-08-16
---

# The promiscuity probe is a test that cannot fail

`BenchResult.precision` is `n_hit / (n_detected - hot_fa)`, and the probe window
contains no planted events. So every firing inside it leaves the numerator *and*
the denominator, and **no reported metric can be reduced by probe firings at all**.

Constructed during the learned-detector murderboard (2026-08-16, role 4): a detector
that emits the 45 planted times plus **500 spurious firings inside the probe** scores
recall 1.00, precision 1.00, F1 1.00 — identical to the same detector firing there
zero times. The alarm cannot ring.

## Why it is this way, and why that part is right

The exclusion is deliberate and well argued in `bench.py`'s own docstring: fold the
probe in and the headline "stops measuring the detector and starts measuring how hard
the probe was set" — CICADA once read F1 0.09 against a true 0.68 on 599 hot-window
detections out of 601 false alarms. That reasoning stands. **The defect is not the
exclusion; it is that nothing replaces it.**

`hot_fa` and `hot_fa_per_min` are computed and, until this review, appeared in no
figure, no table and no page. The probe is currently a diagnostic that nobody reads,
described everywhere as though it were a control.

The spread is large enough to matter: at declared operating points, **81 of binned
SCE's 92 detections and 80 of CICADA's 135** are probe firings, against 0 for LoCo
and 1 for CoactDetect.

## What to do

Not "fold them back in". Give the probe its own gate, so a detector can fail it:

1. Report `hot_fa_per_min` beside precision wherever the six are compared — the
   learned-detector report now does this in prose, which is the minimum, not the fix.
2. Add a **budget assertion** to `tests/test_bench.py` in the style of the existing
   measured baselines: each detector's probe rate has a recorded ceiling, and a change
   that makes a detector fire more in a block containing nothing fails the suite.
3. Consider a composite the bench can rank on, so promiscuity costs something in the
   headline rather than only in a column.

Until (2) exists, no claim of the form "this detector does not fire on dense random
activity" is supported by anything in this repo.
