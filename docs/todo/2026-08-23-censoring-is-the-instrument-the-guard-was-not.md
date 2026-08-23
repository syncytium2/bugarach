---
status: open
filed: 2026-08-23
---

# Censoring is the instrument the guard was not, and there is now a control that can tell

The guard interval was added to `loco` and `coact` on the prediction that a
contaminated reference window masks events, and that excising the span next to
the anchor would recover them. Measured between recordings, it looked right.
Measured **within** one, it is not what is happening.

`docs/forks.md` §4a has the numbers. The short version:

- The guard's recall gain is **flat across nearest-neighbour gap**. CoactDetect
  gains +0.045 for events with a neighbour 15–30 s away and **+0.046** for events
  with nothing within 60 s, where there is no neighbour to unmask. LoCo's is
  inverted: +0.014 crowded against +0.025 isolated, and at a 20 s guard +0.025
  against **+0.064**.
- On the **sparse bench**, where a second planted event can never enter the
  context, the guard raises recall anyway — CoactDetect 0.833 → 0.875, LoCo
  0.683 → 0.733 across 8 seeds.
- Precision pays for all of it: CoactDetect 0.889 → 0.867, LoCo 0.992 → 0.985.

It is lowering the bar. Excising a span shrinks the null pool, and a fixed 99.9th
percentile of a smaller sample underestimates the tail, so every anchor gets an
easier threshold whether or not anything was masking it.

**The masking it was supposed to fix is real and unaddressed.** With an internal
control, a neighbour inside the reference window costs CoactDetect **0.144** of
recall and LoCo **0.104**.

## Why censoring, specifically

A guard removes a span *at a fixed position* — adjacent to the anchor. That is the
right shape when there is one interferer next to the cell under test, which is the
case Rohling 1983 and Finn & Johnson 1968 are written about. It is the wrong shape
here: at the spacings this preparation produces, interference is spread across the
whole ±30 s reference rather than concentrated beside the anchor, so a guard wide
enough to reach it destroys the reference.

Censoring removes the largest reference cells **wherever they sit**. That is the
multiple-target remedy, and this repo's own literature review already reaches for
it twice:

- [`detector_history.md`](../detector_history.md) §5.4 — greatest-of is
  edge-robust and target-blind, and the fix for the blind spot is *"censoring
  inside it"*, not replacing `maxlt`.
- §6.4 — same recommendation, as one of the three things to change about LoCo.
- §5.5 — an order statistic over the reference cells is *"essentially free"*
  against LoCo's surrogate pool, which is 17× the cost of the learned model. **An
  order statistic is one sort away from a trimmed mean**, so the censoring change
  and the cost change are the same change.

## What makes this runnable now, and was not before

`CROWDED_RECORDING` runs three hours and holds both populations — about 38% of its
events have a neighbour inside their own ±30 s reference window and about 31% have
nothing within 60 s. `bench.nearest_neighbour_gaps` splits recall between them
within one recording, so event count, duration, background rate and false-alarm
opportunity are fixed by construction.

**That gives the experiment a falsifiable signature it did not have.** Censoring
that relieves masking shows a gain **concentrated in the crowded band and near
zero in the control band**. A gain that is flat across the gap is another
threshold shift, and should be read as one — which is exactly the reading the
guard failed and nothing was in place to catch.

## The order of work

1. **Trimmed/censored reference on `coact` first.** Its window is centred and its
   null pool is built from events inside it, so the estimator is the whole
   mechanism and there is nothing else to disentangle. Behind a flag defaulting to
   current behaviour, per fork #1 — parity is the product.
2. **Check the signature, not the score.** Crowded-band gain minus control-band
   gain is the number that decides it. Report both.
3. **Then LoCo, as an estimator swap inside `maxlt`.** Fork #8 and §5.4 are
   explicit that the combination rule is right for this preparation and must not
   be replaced; only what each half computes changes. If the order statistic also
   removes the surrogate shuffle, §5.5's cost question gets answered in the same
   run.
4. **Then decide what `guard_sec` is.** It is a working threshold knob spelled in
   seconds. Either document it as that, or find why the shrunken pool biases the
   percentile and fix it, which would make the guard mean what its name says.
   Leaving it named for a mechanism it does not implement is the option to avoid.

## What must not happen

- **Do not tune the guard to make the crowded number look better.** It moves the
  number; that is the problem, not the solution.
- **Do not replace `maxlt`** (fork #8, §5.4, §6.4).
- **Do not read a flat gain as success.** The control band exists to catch exactly
  that, and it caught it once already.
