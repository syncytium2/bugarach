---
status: open
filed: 2026-08-14
---

# The generator's background is flat; real fields are not

Putting a real baseline recording beside the generator's imitation — same ROI
count, same duration, same per-ROI rate, events planted at the measured
participation and jitter — shows they do not look alike, and the difference is
not in any parameter.

| | real slice `20240813_39` | generated |
|---|---|---|
| spread of per-ROI rates (CV) | **2.04** | 0.24 |
| quietest → busiest ROI | 0 → 99 mHz | 7 → 18 mHz |
| share of all events in the busiest ROI | **28.1%** | 4.4% |
| clumping in time (CV of per-minute counts) | **0.78** | 0.25 |

`simulate_coordination` draws a **homogeneous Poisson process at one rate for
every ROI**. A real field has a few ROIs carrying most of the activity, many
carrying almost none, and arrivals that come in bursts.

## Why it matters here specifically

Every one of the six detectors counts **distinct ROIs coactive**. Two
consequences follow:

- A population where most ROIs are near-silent has a far smaller *effective*
  size than its ROI count. Planting an event in 18% of 37 ROIs is not the same
  problem when 10 of those ROIs never fire otherwise.
- The circular-shift null is built from the background. A flat background gives a
  null that a clumpy one does not, so the threshold every detector derives is
  calibrated against the wrong distribution.

Measured symptom: LoCo finds 5 coordinated events in the real recording and 10 in
the generated one at matched marginals. **The synthetic recording is the easier
problem**, which is the direction that inflates every bench score.

## What it would take

1. **Per-ROI rate heterogeneity.** Draw each ROI's rate from a distribution fit
   to the real per-ROI rates (log-normal or gamma is the obvious first try)
   rather than giving every ROI the mean. Cheap, and it fixes the largest of the
   four gaps above.
2. **Bursty arrivals.** Replace the per-ROI homogeneous Poisson with a clustered
   process. More work, and worth measuring the real autocorrelation first.
3. **Re-derive the bench after either.** Both change every score, so this is a
   recalibration, not a tweak — see the transcription todo filed alongside.

## Do not fix this by matching the summary statistics

The CV numbers above are a *diagnostic*, not a target. Tuning the generator until
those four rows match would reproduce the statistics without reproducing the
mechanism, which is the same error as matching a marginal and calling it realism.
Fit the per-ROI rate distribution from data; do not tune to a CV.
