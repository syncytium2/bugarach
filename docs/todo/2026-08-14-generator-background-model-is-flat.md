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

## This is the rule, not one slice (surveyed 2026-08-15)

Tony, 2026-08-15: *"what is generally missing in the simulation is 1-3 highly
active ROIs as shown in the real data. it seems like most read data sets have at
least one."* Checked against the **baseline window of every archived slice** that
carries one — 81 windows, fast stream, ≥300 s and ≥20 events:

| | real baseline windows (n=81) | generator |
|---|---|---|
| share held by the **single busiest ROI** | median **30%** (IQR 18–53%) | 4.2% quiet / 3.8% busy |
| share held by the **top three** | median **61%** (IQR 40–89%) | ~12% |
| CV of per-ROI event counts | median **2.00** (IQR 1.31–3.29) | 0.24 |
| windows with ≥1 ROI firing ≥5× the median ROI | **73 of 81 (90%)** | 0 |

Reproduce with `python tools/make_roi_rate_distribution.py` (figure id
`roi_concentration`, written to `$BUGARACH_DARKROOM`; `--numbers-only` prints the
table and writes nothing). Needs `$BUGARACH_DATA_ROOT`; claim the figure id on
[`SESSIONS.md`](../SESSIONS.md) before running it, since the darkroom is mounted
on every machine.

So the observation holds, with one correction worth carrying: **"1–3" undercounts
the tail.** The median window has **4** such ROIs and the range runs 0–17; only
35% fall in the 1–3 band. The right statement is *"almost every baseline
recording has at least one dominant ROI, usually several."*

Two things follow that the single-slice version could not support:

- The example in `generator.md`, `20240813_39` (top-1 28.1%, CV 2.04), is within
  a couple of points of the **population median** on both. It is representative,
  not cherry-picked, and the document may say so.
- Cumulative-share curves for all 81 windows bow sharply away from the flat-field
  diagonal; **both generator regimes lie on it.** The generator is not a poor
  approximation of a real field's concentration — it is at the opposite extreme
  of the axis, and no setting of `bg_rate_hz` moves it, because that knob scales
  every ROI together.

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
   four gaps above. The survey above gives the target to fit *against* — 81
   windows of per-ROI counts — and the shape to beat: any candidate has to put
   a median 30% of events in one ROI without being tuned to do so.
2. **Bursty arrivals.** Replace the per-ROI homogeneous Poisson with a clustered
   process. More work, and worth measuring the real autocorrelation first.
3. **Re-derive the bench after either.** Both change every score, so this is a
   recalibration, not a tweak — see the transcription todo filed alongside.

## Do not fix this by matching the summary statistics

The CV numbers above are a *diagnostic*, not a target. Tuning the generator until
those four rows match would reproduce the statistics without reproducing the
mechanism, which is the same error as matching a marginal and calling it realism.
Fit the per-ROI rate distribution from data; do not tune to a CV.
