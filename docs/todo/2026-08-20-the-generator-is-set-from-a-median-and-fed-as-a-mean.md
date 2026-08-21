---
status: open
filed: 2026-08-20
---

# The generator is set from a median and its rate knob behaves as a mean

Found by the stage-5 comparison screen the day it was built — the first thing it
was pointed at. That is the screen working, not failing.

## What happens

`simulateFromMeasurement` parameterises the generator from an assessment, and the
mapping it documents is:

    roi_rate_med -> the background rate

`roi_rate_med` is a **median** — `assessCoactivity` computes it as
`median(roiRate)` over ROIs. The generator's `rate` knob, on the **`fitted`
background that is the default**, sets something much closer to a **mean** over a
deliberately heterogeneous population. Under that skew the median comes out at a
fraction of what was asked for.

## The measurement

Generated three 25-minute recordings, 24 ROIs, and counted events straight out of
the emitted CSV — no assessor involved — at a knob of **15 mHz/ROI**:

| background | median per-ROI rate | mean per-ROI rate |
|---|---|---|
| `fitted` (**the default**) | **3.3 / 8.7 / 3.7 mHz** | 9.4 / 14.3 / 11.8 mHz |
| `flat` | 16.8 / 16.4 / 17.0 mHz | 17.1 / 16.5 / 16.7 mHz |

On `flat` the knob lands where it says, and median and mean agree because every
ROI is drawn at one rate. On `fitted` the mean tracks the knob and the median
falls to roughly a quarter to a half of it.

End to end, through the real path — assess a recording, accept a K, set the
simulator, generate, measure the corpus the same way — the comparison read
**14.7 mHz/ROI measured against 6.7 mHz/ROI generated, a ratio of 0.46**.

## Why it matters rather than being a rounding detail

Every operating point in the webapp's tuning step is fitted on this corpus. A
corpus whose typical ROI is two to four times quieter than the recording it was
measured from is a corpus where coordinated events stand out against less
background than they really have to — which makes the detectors look better than
they are, in the direction nobody would catch by looking.

It is also, specifically, a **regression risk introduced by a fix**.
[`the generator's background is flat`](2026-08-14-generator-background-model-is-flat.md)
correctly said real fields are heterogeneous and the generator's was not. The
`fitted` background answers that. What did not move with it is the quantity the
calibration path feeds in, which is still the median that was appropriate when
every ROI was drawn at one rate.

## Three ways to close it, and the choice is not the consumer's

1. **Feed the mean.** Have the assessor report `roi_rate_mean` alongside the
   median and parameterise from that. Cheapest, and it makes the knob's contract
   true — but the median is what the bench's own regime quartiles are stated in
   (`bench.REGIMES`), so the two would then be in different units.
2. **Make the knob mean what it is fed.** Rescale inside the generator so that a
   `fitted` background asked for a median of *x* produces a median of *x*. Keeps
   every existing number in the tree stated in medians.
3. **Report both and let the accept step choose**, which is the shape the K
   decision already has.

Option 2 looks right from here, but it changes what every previously generated
corpus meant, and that is a call for Tony rather than for the session that found
it. **Do not close this by adjusting the comparison screen's tolerance** — the
screen has no tolerance, deliberately, and adding one to make a discrepancy stop
showing is the failure mode `CLAUDE.md` names in its opening paragraphs.

## How to reproduce

`tests/test_webapp_verify_simulation.py::test_the_rate_knob_is_connected_on_a_flat_background`
pins the `flat` case, which is the half that behaves. The `fitted` case is
deliberately **not** pinned: a test asserting the current ratio would freeze the
discrepancy in place as though it were the specification.
