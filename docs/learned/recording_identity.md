# Is recording identity visible in our data? — declared before running

**Why.** The recombination-nulls deep dive found that negatives drawn across recordings taught recording
identity in every study that measured it
([reading log](recombination_nulls_reading_log.md), the negatives and identity answers). Tony,
2026-09-13: *"i think we need to measure this on our data."* This is the slice-identity stage of
[the ROI-swap plan](../todo/2026-09-12-evidence-before-more-effort-on-the-roi-swap.md), plus the
single-train lineup test the reading log proposed for it.

**This section was committed before any result existed.** Results go below the line, and nothing above it
changes after the run except to fix a typo.

## Data

`dataset.current("steps_excluded")` — `2026-09-03_revised_2v_long_STEPS_EXCLUDED`, 84 recordings, 44 mice,
four groups (ORX 25, MALE 22, OVX 20, DI 17). Every recording declares a baseline region with an analysis
window (17–20 min); **baseline only** (FOUNDATIONS §9). Frame interval 0.1 s throughout, so no donor ever
has to be re-quantised. Each stream, fast and slow, is measured separately. **Zero-event ROIs stay in**
(FOUNDATIONS §9) — empty-baseline composition is exactly the sort of signature this measures.

## What is measured

Both measurements use `surrogate_discriminator` unchanged, copied verbatim from
`origin/surrogate-screen-overnight`. Each ROI is reduced **alone** to a feature vector: onset count,
interval quantiles, shortest interval, edge-band counts. ROIs are pooled only by symmetric statistics.
**The classifier therefore cannot see coordination**: two windows whose trains differ only in cross-ROI
timing get identical features, and anything it detects is a per-ROI signature. It is a linear forced
choice on the feature difference, with folds grouped by mouse and a within-pair permutation null (199
permutations). Windows are the discriminator's 60 s, non-overlapping, inside the baseline window.

**The chimera test — can a swap be seen without coordination?** Each real window is paired with a
**chimera** of itself: a share *k* of its ROIs, chosen at random, is replaced by real one-minute trains
from donors, re-based onto the target window's frames. *k* is 0.5 or 1.0. Donors come from four tiers:

| tier | donor | what it holds constant |
|---|---|---|
| `self_other_time` | the **same recording**, a different baseline window, a random ROI | identity. Any accuracy here is within-recording nonstationarity, not identity |
| `same_mouse` | another recording of the same mouse (35 mice have one) | the animal; usually the imaging day |
| `same_group` | a recording of the same group, different mouse | the group |
| `other_group` | a recording of a different group | nothing |

Each replaced ROI takes its donor recording in rotation, so donors repeat only when the pool is smaller
than the number of ROIs replaced; the run records the largest number of ROIs taken from one donor recording.
**Identity cost** at a tier is its accuracy minus `self_other_time`'s at the same *k* and stream. It uses a
paired bootstrap over mice, which removes whatever a swap reveals for reasons other than where the donor
came from.

**The window-pair test — is a recording identifiable at population level?** This is the plan's stage,
built as a forced choice. Each anchor window is shown two candidates: another window of the **same
recording** starting at least 5 min away, and a window of a **different recording** at tier `same_mouse`,
`same_group` or `other_group`. The classifier must say which candidate shares the anchor's recording. The
features are the absolute differences of the pooled window features, so it sees distances, never times.

**Controls, both judged by interval and not by one P value.** The lesson of the 126 voided screen
candidates is that a control flagging at its nominal α on one seed voids nothing.
- **Negative control — real against real:** windows of one recording, orientation random. Must read chance:
  its 95% interval over mice contains 0.5.
- **Positive control — thinning:** each ROI loses a random 30% of its onsets. Must be detected: the lower
  95% bound is above 0.55.
If either fails for a stream, that stream's results are **void** and are not read.

## Declared gates

Intervals are 95% bootstrap intervals **over mice** (2,000 resamples of mice with replacement, using the
cross-validated per-pair correctness).

- **Chimera test, per stream, at k = 1.0** (the plan's full-chimera bar):
  - **ADMISSIBLE** as a per-ROI-blind null at a tier if the upper bound of its accuracy is below **0.60**.
  - **NOT ADMISSIBLE** at a tier if its lower bound is above **0.60**.
  - Otherwise **UNDECIDED** at this sample size, and reported as such.
- **Identity cost:** reported with its interval at every tier. No gate; it is the measurement this was
  asked for.
- **Window-pair test, per stream** (the plan's slice-identity gate): **GO** if at least one tier has an
  upper bound below 0.60; **STOP** if every tier's lower bound is above 0.60. If even `other_group` reads
  chance, the instrument has failed, which is not a GO.

**Expectations, from the literature, stated so they can be wrong.** Population-level identity is near
ceiling wherever measured, so the window-pair test at `other_group` should be well above 0.60.
Single-unit identity was weak under a standard protocol (IBL 2025; CalM's per-neuron embeddings), so the
chimera test at `same_mouse` could plausibly be admissible. The chimera test at `other_group` is the open
question.

**Not measured here, and why.**
- **Coordination-sensitive models:** by construction.
- **The aggregate cells-mean leak** that `tube` would see: that is
  [its own todo](../todo/2026-09-12-tube-cannot-tell-a-count-leak-from-coordination.md).
- **Day versus group:** group is nested in imaging date on this export, so `other_group` is also a
  different day. The run reports each tier's share of donors imaged on the target's date.
- **Per-group breakdown:** reported descriptively, target group by target group, and not gated.

---

## Results — run 2026-09-13

`python tools/measure_recording_identity.py`: both streams, 1,669 windows from 84 recordings and 44 mice,
199 permutations, 2,000 bootstraps. Outputs are in `<darkroom>/bugarach/2026-09-13-recording-identity/`,
with repo copies in [`recording_identity/`](recording_identity/).

⚠ **Disclosure.** A 300-window, fast-stream smoke run (`--quick`) was seen **before** the declared section
was committed (681c39c). That section was not changed after it; the commit message says the same.

![Chimera accuracy by donor tier and window-pair accuracy, fast and slow streams](recording_identity/recording_identity.png)

**Read the left panels left to right.** The two squares are the controls. The dots are chimeras, with donors
from progressively further away: the same recording at another time, then the same mouse, the same group,
another group. The dashed line is the declared 0.60 gate. **Accuracy climbs with donor distance in both
streams.** The right panels ask whether a window pair comes from one recording, and every tier sits above the
gate.

### The instrument works

| stream | real vs real (must contain 0.5) | 30% thinning (lower bound must exceed 0.55) |
|---|---|---|
| fast | 0.523 [0.491, 0.556] — passes | 0.916 [0.878, 0.949] — passes |
| slow | 0.484 [0.448, 0.520] — passes | 0.870 [0.833, 0.901] — passes |

Neither stream is void.

### Chimera test — the declared gate is at swap share 1.0

| stream | donor tier | accuracy [95% over mice] | verdict | identity cost vs same recording |
|---|---|---|---|---|
| fast | same recording, other time | 0.547 [0.518, 0.575] | ADMISSIBLE | — |
| fast | same mouse | 0.572 [0.540, 0.608] | UNDECIDED | +0.022 [−0.017, 0.065] |
| fast | same group | 0.635 [0.567, 0.700] | UNDECIDED | +0.088 [0.008, 0.167] |
| fast | other group | 0.754 [0.703, 0.801] | **NOT ADMISSIBLE** | **+0.207 [0.148, 0.267]** |
| slow | same recording, other time | 0.636 [0.601, 0.675] | NOT ADMISSIBLE | — |
| slow | same mouse | 0.637 [0.602, 0.675] | NOT ADMISSIBLE | −0.012 [−0.044, 0.018] |
| slow | same group | 0.764 [0.701, 0.823] | **NOT ADMISSIBLE** | **+0.127 [0.052, 0.193]** |
| slow | other group | 0.858 [0.819, 0.896] | **NOT ADMISSIBLE** | **+0.221 [0.166, 0.276]** |

At share 0.5 the pattern is the same (full table in `results.json`). Fast reads 0.576, 0.541, 0.635 and
0.754; slow reads 0.614, 0.616, 0.738 and 0.812.

### Window-pair test — the plan's slice-identity stage

| stream | same mouse | same group | other group | verdict |
|---|---|---|---|---|
| fast | 0.715 [0.653, 0.779] | 0.762 [0.725, 0.798] | 0.776 [0.732, 0.815] | **STOP** |
| slow | 0.697 [0.644, 0.752] | 0.702 [0.663, 0.737] | 0.716 [0.673, 0.756] | **STOP** |

### What it says

- **Recording identity is visible in our data, without any access to coordination.** Pooled one-minute
  windows tell their own recording from another at 70–78%, at every tier, in both streams. The plan's
  slice-identity stage returns **STOP**, as the literature predicted.
- **For a swap, identity lives at the mouse or day level, not the slice.** Donors from the same mouse cost
  nothing measurable beyond moving the recording's own trains in time: +0.02 fast, −0.01 slow, both
  intervals spanning zero. Donors from another mouse in the same group cost +0.09 fast and +0.13 slow.
  Donors from another group cost about +0.21 in both streams. In the data these tiers are also imaging-day
  tiers: 100% of same-mouse donors were imaged on the target's date, against 1% of same-group donors and 0%
  of other-group donors. So "mouse" and "day" cannot be separated here, and neither can "group" and "day".
- **What gives a cross-group chimera away is rate composition, not timing.** The largest weights are the
  median and mean onset count per ROI, and in slow the share of ROIs with any onset. That is the group
  signature [the empty-baselines todo](../todo/2026-09-12-an-empty-baseline-is-a-group-feature-and-39-percent-of-every-surrogate-is-the-data.md)
  describes, seen by a classifier.
- **In slow, even the within-recording swap is visible** (0.636, NOT ADMISSIBLE). One-minute slow windows
  differ across a 20-minute baseline enough to tell a train moved in time. That is within-recording
  nonstationarity, and it applies to any null that moves trains in time — not only to the swap. The fast
  stream's version is small (0.547, admissible).
- **By group, descriptively:** DI's slow-stream within-recording chimeras read 0.73–0.76, against 0.54–0.65
  for the other groups, so DI baselines are the least stationary. ORX is the hardest group to spot a
  same-group donor in (0.54 fast, 0.59 slow) and the easiest to spot an other-group donor in (0.82 fast,
  0.92 slow).

### Consequences

- **The ROI swap as training negatives:** closed on evidence, not just on literature. A linear model that
  cannot see coordination already separates a cross-group swap at 75–86% and a within-group swap at
  64–76%. A model that can see coordination can learn at least this much instead.
- **The ROI swap as a significance null:** only **same-mouse** donors are plausible. They cost no measurable
  identity in either stream. But only 35 of 44 mice have a second slice, which is 180 of 1,669 windows
  without a donor. And same-mouse donors are also same-day donors, so a day-level shared state is exactly
  what they would fail to remove. The simulated-ground-truth stage should test same-mouse donors first, and
  the buildability counter should count that tier.
- **Any null that moves trains in time, in the slow stream,** has to reckon with the within-recording
  nonstationarity measured here, circular shift included, before its calls are read.

**Not settled here.** A coordination-sensitive model could find more. The cells-mean aggregate leak is
[its own todo](../todo/2026-09-12-tube-cannot-tell-a-count-leak-from-coordination.md). And day cannot be
separated from group or from mouse on this export.
