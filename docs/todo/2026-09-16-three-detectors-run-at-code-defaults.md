---
status: waiting-on-tony
filed: 2026-09-16
---

# Three of the six run at their code defaults, and two sweep grids do not bracket

**Found reading the plain-language detector review.** Tony, 2026-09-16, on Figure 15's caption:
*"do we need a sidequest to tune the whole batch so the figures are valid. this will be reviewed by
people judging the project. this looks like unfinished business"*

The short answer is that **the batch has already been tuned** — `stage_rounds` picks a setting per
round on held-out recordings, for all six — so the comparison figure is not at risk. What the tuning
exposed is narrower and worth deciding on.

## What `OPERATING_POINTS` actually holds

Half the table was calibrated and half is whatever the function signature came with:

| detector | stored setting | origin |
| --- | --- | --- |
| CoactDetect | `alpha=1e-4` | tuned — explore_sce FAST point, **not** the signature's `0.01` |
| LoCo | `threshold_pctile=99.9` | tuned — measured-regime F1 optimum |
| locust | `sce_percentile=99.999` | tuned — calibrated FAST pair, retuned 2026-08-20 |
| rate+context | `excess_threshold_hz=5.0` | `rate_detect` defaults |
| binned SCE | `threshold_pctile=99.0` | `sce_detect` defaults (generate_sce contract) |
| SPIKE-synch | `C_threshold=0.1` | viewer FAST defaults |

## What tuning is worth, measured

F1, stored setting against the round-selected setting (`measurements/shipped.json` and the
`perf_*` keys of `numbers.json`, 2026-09-15 review build):

| detector | origin | quiet stored → tuned | busy stored → tuned |
| --- | --- | --- | --- |
| CoactDetect | tuned | 0.74 → 0.74 | 0.67 → 0.65 |
| LoCo | tuned | 0.72 → 0.73 | 0.65 → 0.66 |
| locust | tuned | 0.57 → 0.57 | 0.56 → 0.55 |
| rate+context | code default | 0.63 → **0.71** | 0.63 → 0.63 |
| binned SCE | code default | 0.37 → **0.45** | 0.45 → **0.63** |
| SPIKE-synch | code default | 0.49 → 0.53 | 0.47 → 0.51 |

**The three calibrated ones gain nothing**, which is the check working: their stored setting already
sits where the sweep puts the optimum. Every gain belongs to a detector nobody calibrated.

**On the busy background the ranking changes.** binned SCE goes from last (0.45) to third (0.63),
passing locust and SPIKE-synch. Anyone reading the busy-background ordering as a fact about the
detectors is reading a fact about who got calibrated.

## The defect the project's own code already names

`OperatingPoint`'s docstring: *"The grid must bracket the operating point — if the F1-optimum lands on
an end of it, the search was too narrow and `pick_operating_point` says so rather than reporting the
boundary as an answer."* Two sweeps land on an end:

- **binned SCE, quiet** — optimum at `threshold_pctile=75.0`, the floor of its grid, still climbing.
- **SPIKE-synch, busy** — optimum at `C_threshold=0.005`, the floor of its grid.

So two of the tuned numbers above are **lower bounds**, not optima. Widening those two grids is a
small, self-contained job and should happen regardless of the calibration decision.

## The decision, which is Tony's

**Should `OPERATING_POINTS` move for rate+context, binned SCE and SPIKE-synch?**

Reasons to leave it until the review lands:
- It is not a document change. It moves the viewer, `detections.csv`, every real-recording call, the
  MILESTONES rows pinned to those numbers, and every figure in both review documents. Doing it
  mid-review invalidates the real-recording sections that took ~8 minutes a build to produce.
- **Tuning against the simulator inherits the simulator's known wrongness.** The review has a section
  on what the generator gets wrong; a setting chosen to maximise F1 against planted events is chosen
  against those same assumptions. Retuning would make the numbers prettier without making them truer
  about real recordings — and the honest version of that is a measurement reported, not a knob turned.
- What a reviewer can fairly ask is *"did you check?"*, and the table above is the answer.

Reasons to do it:
- 0.18 on the busy background is not a rounding error, and binned SCE is the detector the review
  already treats unkindly.
- "Half our operating points are library defaults" is a sentence nobody wants read aloud.

Recommendation: **widen the two grids now, hold the calibration until the review lands**, and say the
gap out loud in the document rather than closing it quietly.
