---
status: open
filed: 2026-09-12
---

# An empty baseline is a group feature, and ~39% of every surrogate is bit-identical to the data

> **Tony's ruling, 2026-09-12**, on reading that the surrogate screen's per-ROI machinery drops
> quiet ROIs: *"empty baseline is a feature of some groups. that is as imporant as highly active
> rois."*

This is FOUNDATIONS §9's zero-event rule arriving in a new place. §9 already forbids dropping
zero-event ROIs to tidy a distribution, because `freq == 0` is a valid value and **conditioning on
having fired is group-dependent**. The surrogate screen conditions on it twice — once by
construction, once possibly by omission — and the second one may weaken every verdict it produces.

## The measurement

Read 2026-09-12 from the discriminator cells of the 2026-09-11 run,
`<darkroom>/bugarach/2026-09-11-surrogate-screen/discriminator/**/cells/*.json`. Reproduce before
building on it.

**Every generator leaves about 39% of `steps_excluded` ROIs bit-identical to the real recording.**
Median `unchanged_share` by generator: uniform dither 0.391, circular shift 0.390, trial shift 0.391,
dead-time dither 0.391, window shuffle 0.392, rigid shift 0.413, interval jitter 0.392.

**It is flat in displacement**, which is what identifies it as a population property rather than a
generator one — trial shift sits at 0.392 with J = 0.4 s and 0.383 with J = 1.6 s. Nothing moves
because there is nothing to move.

**The Cossart folder is 0.039–0.073.** The two folders differ by an order of magnitude in exactly
this quantity, which is the same effect as the group contrast, one level out.

FOUNDATIONS §9 independently puts roughly **35% of ROIs with no events in a baseline window**, against
3% rejected as dead. That is close enough to 39% to treat empty baselines as the cause, though the
per-ROI onset counts have not been computed directly here to prove it.

## What follows

**Roughly 39% of the negative class is the positive class.** For a self-supervised objective those
pairs are identical inputs with opposite labels: label noise at a floor set by the data rather than
by any surrogate's design. **No choice of surrogate removes it, and neither does mixing generators** —
every member inherits the same floor. It is a property of the approach on this folder.

**The noise is group-structured, so it is a §9 problem and not a nuisance.** Quiet baselines belong to
particular groups. A detector trained on this contrast is fitted where baselines are active, and §9
does not allow that to be averaged across groups. Any transfer claim between the two folders inherits
the same objection, since they differ tenfold in the share of untouchable ROIs.

**The leak gate is diluted by the same pairs, and the exclusion appears to be missing.**
`surrogate_stats.py` masks `not_estimable` ROIs when scoring preservation
(`roi_mask=~draws.not_estimable`). ⚠ **No corresponding exclusion of `unchanged` ROIs could be found
in `surrogate_discriminator.py`** on a read of 2026-09-12 — confirm against the code rather than
trusting this note. If identical pairs sit in the discriminator's pairs they are coin flips, and
against `min_effect` 0.55 a real effect on the movable 61% must be larger to clear the same bar. Then
*"no leak detected"* is systematically easier on the folder with more empty baselines, and the two
folders are not comparable on that axis.

**It also settles the vacuous-survivor question by measurement.** The `pattern_jitter` cells that
survive the leak detector at the smallest displacement carry `unchanged_share = 1.000`, accuracy 0.5,
*p* = 1.0 — the generator changed nothing. That is the concrete form of what
[the join](2026-09-12-join-the-leak-results-to-the-destruction-results.md) predicted and the strongest
argument for [a displacement floor](2026-09-12-the-verdict-rule-needs-a-displacement-floor.md) stated
in measured RMS displacement rather than in a parameter label.

## What to decide

The objective has to say what it does with ROIs no surrogate can touch, and the options are not
equivalent under §9:

- **Accept the noise**, and state the per-group share of untouchable ROIs beside every result.
- **Weight the contrast** so untouchable ROIs contribute nothing to the loss without being removed
  from the population.
- **Drop them** — the one option §9 rules out without a group-aware argument, because it conditions on
  having fired. It is also the option that happens by default if nobody chooses.

And the gate has a narrower version of the same question: whether the per-ROI discriminator should
exclude unchanged pairs, which raises its power but changes what its null means.

## Closes when

The screen's report states the share of untouchable ROIs per folder and per group, the discriminator's
handling of unchanged pairs is confirmed and stated, and the objective's treatment of them is chosen
rather than defaulted.
