# Rigid shift, one look — does it hide while it removes coordination?

> **Exploratory, run 2026-09-14 night.** Tony set the pre-registration machinery aside for one
> figure he reads himself. The dashed lines at 0.55, ±2 % and 0.25 are the thresholds he signed
> earlier, drawn for reference, not applied as a rule. Not murderboarded. Baseline windows of the
> lab folder only.
> Results: `<darkroom>/bugarach/2026-09-15-rigid-shift-look/`. Code: `tools/look_rigid_shift.py`
> and `tools/make_rigid_shift_look_figure.py` on branch `unsup/rule-as-code`.

## The answer, short

**On the fast stream, rigid shift at 10–20 s looks usable.** A classifier that cannot see
coordination cannot tell it from the real recording (accuracy 0.50, chance 0.50). Onset counts are
unchanged, and the shift removes 84–99 % of planted coordination in synthetic recordings. At the
displacements first planned (1.6–5 s) it hides just as well but removes too little: a large event
keeps up to 87 % of its coordination.

**On the slow stream, the window is narrow.** Up to about 11 s the shift hides (0.52), but large
events on the 2 s bin keep 29 % of their coordination. At 22 s and beyond it starts to give itself
away (0.55–0.56), almost entirely in the DI group (0.62–0.68). DI is the group whose slow baselines
the recording-identity run found least stationary, so the classifier is probably seeing slow drift
moved in time.

## What was measured

Every lab recording has a declared baseline region, and all 84 were read from it; none was
skipped. Each baseline was cut into whole 60 s windows, and the first and last were dropped as
edge windows. That gives 1,501 window pairs per stream, from 44 mice.

- **Leak.** Each window is paired with the same window of a rigid-shifted copy of its recording.
  The shift moves each ROI's whole train by one random offset within ±*J*. A linear classifier
  sees each ROI's own onset statistics, pooled over ROIs, so it cannot see cross-ROI timing, and
  it is asked to pick the real one. The edge-band features are left out, because the second review
  showed they see coordination under a shift. Accuracy is resampled over mice and, separately, over
  slices; the two intervals came out almost identical everywhere. Uniform dither, which moves every
  onset independently, is drawn beside it as what a leak looks like.
- **Destruction.** Synthetic twins are built with this stream's typical ROI count (31), length and
  per-ROI rates. One twin of each pair has events planted in 20 % or 50 % of ROIs, the other none;
  there are 20 pairs per level. Both go through the same shift. **Retained share** is how much of
  the planted coordination excess survives, where excess is what the assessor counts in a 1 s bin
  (and a 2 s bin on slow) above its circular-shift null. **K** is the number of ROIs that must fire
  together in one bin. Controls: homogeneous resample (should read 0) and do-nothing (should
  read 1).
- **Count.** Occupied frames per ROI per window, shifted against real. The edge-thinning control at
  5 s must show a change.

## Figures

### The displacements first planned

![Leak and count, declared displacements](fig1_leak_count.png)

**Figure 1. Leak and onset count at the planned displacements.**
- **Left panels:** forced-choice accuracy for rigid shift (blue) and uniform dither (red), fast
  above and slow below. Thick bars are the 1.67–98.33 % range over mice, thin bars the same over
  slices. The dotted line is chance, the dashed line 0.55.
- **Right panels:** occupied-frame change in percent, with the ±2 % band shaded and the
  edge-thinning control in grey.
- **What it shows:** rigid shift reads 0.49–0.52 at every displacement while dither reads
  0.63–0.77, and counts move by at most 0.14 % against the control's −4.6 %.

![Destruction, declared displacements](fig2_destruction.png)

**Figure 2. How much planted coordination survives at the planned displacements.**
- **Rows:** fast at a 1 s bin, slow at 1 s, slow at 2 s.
- **Columns:** 20 % and 50 % of ROIs in each planted event.
- **Axes:** x is K; each line is one displacement. Bars are 95 % over the 20 twin pairs. The grey
  squares are the two controls, which read 0 and 1 as they should.
- **What it shows:** removal is poor for large events at low K. At K = 3 with 50 % participation,
  1.6 s keeps 0.87, and 5 s still keeps 0.41 (fast, 1 s bin) and 0.60 (slow, 2 s bin).

### Larger displacements, the follow-up

Run the same night, because the first run showed no leak rising with displacement.

![Leak and count, larger displacements](larger-displacements/fig1_leak_count.png)

**Figure 3. Leak and onset count at 5–40 s (fast) and 5.6–44.8 s (slow).**
- **Panels:** as in Figure 1.
- **Fast:** stays at chance to 40 s (0.49–0.51).
- **Slow:** rises to 0.549 at 22.4 s and 0.563 at 44.8 s, with lower bounds 0.509 and 0.510. By
  group at 44.8 s: DI 0.675, MALE 0.593, ORX 0.506, OVX 0.507.
- **Counts:** stay within 0.4 %.

![Destruction, larger displacements](larger-displacements/fig2_destruction.png)

**Figure 4. How much planted coordination survives at 5–40 s (fast) and 5.6–44.8 s (slow).**
- **Panels:** as in Figure 2.
- **Fast, K = 3, 50 % participation:** retained falls 0.41 → 0.16 → 0.07 → 0.04 across 5, 10, 20
  and 40 s.
- **Slow, 2 s bin:** 0.60 → 0.29 → 0.13 → 0.07.

## What this cannot say

- **The destruction test uses synthetic events with one frame of jitter.** Real coordinated events
  are probably looser: an interface2 commit measured real fast onset jitter at about 1 s. Looser
  events are harder to remove, so these retained shares are a best case.
- **The leak classifier is linear and sees per-ROI statistics.** A trained model is a stronger
  learner. "Not detected here" is not "undetectable".
- **Shifting by 10–20 s removes all cross-ROI structure faster than that,** not only fast
  coordination: shared slow modulation within that range goes too. A model trained against these
  negatives learns "real = anything shared on timescales under about *J*". Whether that is what
  should count as coordination is a scientific call, not a statistical one.
- **Same recordings.** This uses the recordings the earlier screen explored, and it chose its
  follow-up displacements after seeing the first run. It is a look, not a confirmation.

## The decision this sets up for Tony

1. **Fast:** is rigid shift at 10–20 s a negative class worth training against, given the
   timescale caveat above?
2. **Slow:** accept a narrow window near 11 s, which hides but leaves some large-event
   coordination, or look for a slow-specific surrogate that respects the DI nonstationarity?
