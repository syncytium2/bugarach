# The surrogate screen, reevaluated — what the probe found and what to run next

> # ⚠ WITHDRAWN 2026-09-12, after its own murderboard. Do not act on anything below.
>
> Eleven roles reviewed this draft and each of its four load-bearing conclusions failed
> against the production run. It is kept, unedited below this notice, as the record of what
> was claimed — not as advice. Its replacement is re-derived from the 2026-09-11 run rather
> than from the probe, and lives at
> [`2026-09-12-surrogate-screen-reevaluated-v2.md`](2026-09-12-surrogate-screen-reevaluated-v2.md).
> The review is `docs/reviews/2026-09-12-surrogate-screen-reevaluated_2026-09-12.md`.
>
> **What failed, briefly.** "Delete the square-root axis" rests on a no-op claim that is false:
> 23 sqrt/nosqrt cell pairs in the production run differ on 5 of 13 statistics or more, and
> Elephant applies the square root before smoothing and before the cumulative is normalised,
> so normalisation cannot undo it. The cost argument is unsourced, reproduces only at 19 draws
> per cell (278,415 core-hours at the plan's 99), and rests on a probe ratio ~50× off the
> shipped scale. "The discriminator tier is usable" ignores a design effect of 5.14 — about
> 325 effective pairs against the 654 the same document demands — and leans on a `powered`
> flag computed from the data it judges, which reads True by construction under the null.
> Every destruction number comes from 20 assessor surrogates against a shipped 200, where the
> estimator is the median of that ensemble, and one quoted pair reproduces nowhere.
>
> **The root cause, stated once.** The probe was sized to test whether the instrument can
> answer. Its numbers were then used as evidence about cost, capability and destruction, which
> is not what a two-recording, three-draw, twentieth-of-an-ensemble run can support. The
> replacement takes every such number from the production run and keeps the probe for the one
> question it was built for.
>
> **Status (superseded): DRAFT, not yet reviewed.** This revises
> [the overnight plan](2026-09-10-surrogate-evaluation-overnight.md) from measurements taken
> 2026-09-12, after that plan's run and its
> [murderboard](../reviews/report_steps_excluded_2026-09-11.md). It goes through
> `/murderboard` before it is delivered.
>
> Tony, 2026-09-12: *"design a short probe run at each of the methods to ensure functional
> and usable output. then reevaluate the plan."* He chose the family-13 correction scope.
> This is the reevaluation.

## The problem, unchanged

The goal is a coordinated-event detector that needs **no labels**: train a model to tell a real
recording from a **surrogate** of itself, and whatever it learns is coordination. That works only
if the surrogate differs from real data in cross-ROI timing **and nothing else**. When something
else gives it away the surrogate **leaks**, and the model learns the giveaway. Uniform per-onset
dither leaks — it manufactures within-ROI intervals shorter than any real one — which killed the
first proposal and bought the screen.

The screen is instrumentation for that goal. Its job is to say which surrogate can be trusted, and
it shortlists nothing by design.

## What the night could not do, and why that was knowable in advance

The 2026-09-11 run measured 728 grid cells and **could not have flagged anything under
correction**. At 100 mouse splits, *K* ≤ 99 draws, and a Holm family of 65 checks per grid cell,
the smallest reachable adjusted *P* is 0.64 (band) and 1.00 (paired) against α = 0.05. No data is
needed to see it: it follows from the three numbers the plan itself declared. Two murderboard
rounds on that plan missed it, because no role computes forward from declared parameters to the
resolution they buy.

That is now a gate rather than a hope: `surrogate_stats.correction_reach()` does the arithmetic and
`build_surrogate_screen` refuses to start when no corrected flag is reachable, naming both remedies
with their numbers. `--allow-underpowered` exists for functional probes, which legitimately run at
three draws.

## What the probe established

Five stages, about an hour of compute against a night for the grid.

**The correction scope was the whole problem, and 13 is the family.** Correcting Holm *within* each
scope rather than across all five — FOUNDATIONS §9 requires the per-group numbers to be reported,
not jointly corrected — takes the family from 65 to 13 and the required sample from 1,300 splits and
2,600 draws to **260 and 520**.

**At 260/520 the screen fires, and at 259/519 it does not.** This is the keystone measurement.
Uniform dither, the known-bad control, is flagged 7 of 13 (band) and 11 of 13 (paired) **under
Holm** at 260/520, smallest adjusted *P* 0.0498 and 0.0499; do-nothing stays at 0 of 13. At 259/519
the same run flags 7 and 11 raw and **0 and 0** adjusted, because 13 × 2/520 = 0.05 exactly and a
check fires on *P* < α. One split and one draw are the entire difference.

**All 18 generators run, and three of them cannot be measured on the Cossart folder.** 146 probe
cells over three streams. Controls behave: do-nothing moves nothing with every ROI unchanged,
circular shift 0.999–1.000, homogeneous resample 0.999. Joint-ISI and ISI dither are killed at the
240-second cap at **every** *J* on Cossart, and on `steps_excluded` run only at the largest *J*, at
167–186 ms per ROI per draw — about six times uniform dither. Operational-time dither is 0 of 6 on
Cossart and fine on both `steps_excluded` streams. Interval jitter and pattern jitter return their
input unchanged at the smallest *J* — genuine no-op cells.

**The joint-ISI family is not merely expensive on this data; it is largely inapplicable to it.**
`jisi_too_few` fires on 35% (fast) and 48% (slow) of ROI-draws, with an identical count across every
sigma and square-root setting — a property of the corpus, not the parameters. On the fast stream
1,452 of 2,630 ROIs carry fewer than three onsets, which is the threshold below which no joint-ISI
histogram exists. Those ROIs are excluded from scoring, so a joint-ISI cell is scored on 803–954
ROIs where do-nothing is scored on all 2,630.

**Destruction works, at the radii where the arithmetic says it can.** At *J* = 0.8 and 2.5 s on the
fast stream: do-nothing keeps 1.000 at every floor, **homogeneous resample falls to 0.000**,
freeze-half lands between at 0.29–0.47, and uniform dither moves 0.63 → 0.05 across the scan. So
there is an honest zero-reader that is **not** the assessor's own null, which the circular shift is.
Saturation is a property of *J*: 3 of 6 fast radii cannot register removal at all, and every radius
on Cossart cannot.

**The discriminator tier is usable, and the report says otherwise for the wrong reason.** On 1,669
pairs per `steps_excluded` stream (power 0.992) and 1,375 on Cossart (0.980), the positive control is
detected everywhere — 0.762 fast, 0.747 slow, 0.992 Cossart, all *P* = 0.005. The negative control
passes on slow (*P* = 0.415) and Cossart (*P* = 0.165) and flags on fast at *P* = 0.035 — which
re-running at five seeds shows to be **1 in 5**, the α-level false-positive rate it is built to have.
The 2026-09-11 run voided the entire fast tier from a **single** such draw: its 248 fast candidate
rows carry one distinct void reason, naming accuracy 0.539, stamped onto 126 of them, because the
negative control is derived from the real features alone and is identical for every candidate in a
stream.

## Two traps found on the way

**Saturation was computed as a count that could exceed its own population.** `recruited × bin/(2J+1)`
with no cap reported 25.8 expected co-active ROIs from a twin recruiting 15.5, and 471.7 from one
recruiting 283. A probability cannot exceed 1. Capped; verdicts unchanged, printed counts were not.

**`coverage` runs opposite to the exclusion it is supposed to report.** It is 1.000 for the three
generators that exclude a third to a half of their ROIs and 0.505 for the fifteen that exclude none,
because `roi_mask` removes the excluded ROIs from numerator and denominator together. A verdict rule
reading coverage as completeness will prefer whichever generator discarded the most data. The
docstring that promised otherwise is corrected; the page still does not show `not_estimable_rois`.

## What to run next

**Do not rerun the dropped joint-ISI and ISI-dither cells at the old settings** (~53,500 core-hours
as previously estimated). They would faithfully reproduce three defects: the *J*/2 binning that makes
a 5-point lattice, the square-root axis that is a provable no-op and therefore duplicates half those
cells, and a method that excludes a third to a half of the ROIs it is scored on. That is compute
spent re-measuring known bugs.

**Run instead, in this order:**

1. **Fix the joint-ISI binning and delete the square-root axis** before any joint-ISI cell is
   believed. Then decide whether the family belongs in the screen at all on a corpus where most ROIs
   have fewer than three onsets.
2. **The cheap class at 260 splits and 520 draws**, corrected within scope. The gate now refuses
   anything less, so this cannot be got wrong by accident.
3. **Destruction only at the unsaturated radii**, with homogeneous resample as the must-pass control
   and the circular shift demoted to a self-consistency check.
4. **The discriminator with a multi-seed negative control.** A control whose failure voids a stream
   must be evaluated over several seeds before it is allowed to.

## Open decisions

1. **Does the joint-ISI family stay in the screen?** Tony ruled on 2026-09-10 that no candidate is
   pruned, and nothing here contradicts the reasoning — but the probe shows this data cannot support
   the method for most of its ROIs. Keeping it means accepting cells scored on a third of the
   population; dropping it revisits a standing ruling. This is his call, not a measurement.
2. **Should `coverage` be redefined, or a second column added?** Redefining changes what the
   2026-09-11 numbers mean. Adding a scored-share column over the full ROI population does not.
3. **Does the fast discriminator tier come back?** Its voiding was one α-level draw. Reinstating it
   means rebuilding the 2026-09-11 discriminator results with a multi-seed control.

## Residual ⚠

- Fractional *K* is **not** a universal fix for saturation: at 10% it rescues Cossart (57 against
  42.9 expected at *J* = 16 frames) and makes the fast stream worse (3 against 4.6 at *J* = 0.8 s),
  because a lower floor is easier to trip. The fast twin's 31 ROIs are the constraint there.
- The positive control is `powered: False` on both `steps_excluded` streams (87–89 mice required
  against 44) and `powered: True` on Cossart (18 against 32), so even the passing discriminator
  verdicts rest on an effect the mouse count cannot fully support.
- Role 6's three methods findings from the murderboard stand: the *J*/2 binning, the no-op square
  root, and "Stella's setting" being wrong in three of its four parameters.
- The page still does not surface `not_estimable_rois`, and the shipped report still tells the reader
  the fast discriminator tier is void.
- The probe ran at `--limit 2` recordings for Stage 1, so its cost figures are per-ROI rates, not
  whole-folder projections.
