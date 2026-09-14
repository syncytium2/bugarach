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

## Results

*Not yet run.*
