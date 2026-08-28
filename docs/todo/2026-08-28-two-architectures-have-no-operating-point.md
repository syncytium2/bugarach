---
status: open
filed: 2026-08-28
---

# Two of the three architectures pick a threshold at the floor, so two of the three rows are not operating points

> **Not murderboarded** — a measurement for sessions in this tree, reproducible
> from `tools/fair_bakeoff.py --spec docs/learned/generator_spec.json`. If any of
> it reaches an outside reader, murderboard that artifact first.

Found while fixing
[the thread-count binding](2026-08-27-the-bakeoff-reference-is-thread-count-bound.md)
and [the threshold picked on the fitting recordings](2026-08-27-the-threshold-is-picked-on-the-recordings-it-trained-on.md),
which landed together and are what exposed this.

## What changed, and why it made this visible

`pick_threshold`'s grid used to be `arange(0.05, 0.95, 0.05)` plus a dense tail
towards 1 — **open at the top, hard floor at 0.05**. That asymmetry was survivable
only while the threshold was being picked on the recordings the model had just
fitted: probabilities run high on training data and the optimum sat comfortably
inside the grid.

The moment `fold_maker` started handing `pick_threshold` recordings the fit had
never seen, the optimum went through the floor on the first architecture of the
first fold. The grid is now open at both ends (`geomspace(1e-4, 0.05, 12)` added
below), and this is what the three architectures do under it:

| architecture | held-out F1 | thresholds, per fold | operating point? |
|---|---|---|---|
| `tube` (centre−surround) | **0.681** | 0.9838, 0.9983, 0.9716, 0.9716 | **yes — interior** |
| `trace` (pooled) | 0.118 | 0.4, 0.0001, 0.0001, 0.0001 | **no — 3 of 4 on the floor** |
| `tiny` (per-cell bank) | 0.125 | 0.0001 ×4 | **no — 4 of 4 on the floor** |

A threshold at the floor means *"detect everything"* scored better than any
stricter setting the search could reach. By this project's own rule — the one
`bench.EdgeOfRange` enforces for the six, and the one `pick_threshold`'s existing
comment states — **a boundary answer is the search reporting that it stopped while
still climbing, and is not an operating point.**

## What is and is not new

**The per-cell bank was already known not to train.** `docs/learned/README_for_the_webapp.md`
says so in terms: *"its threshold lands on the edge of the searched grid. Its
number is not an operating point."* That is unchanged and this file does not
re-report it.

**The pooled trace joining it IS new**, and it matters more than it looks. The
trace is the *control* — the architecture that pools ROIs first and gives up
distinctness, present to answer whether distinctness matters. A control whose
number is not an operating point cannot do that job, so the comparison
*"centre−surround beats the pooled baseline"* currently rests on a row that means
"this architecture has no threshold at which it is better than answering yes to
everything."

The conclusion does not reverse — 0.681 against 0.118 is not a close call, and
the direction is what the architecture argument predicts. What is missing is that
the baseline is not being beaten *at its best*, because it has no best.

## What to do about it, cheapest first

1. **Say it, wherever the three are tabled together.** One row of a three-row
   comparison being a genuine operating point is a fact a reader needs at the
   table, not three sections later. This is the same defect shape the
   learned-detector murderboard found on 2026-08-27: the page led with a number
   the rule could not support and disclosed the caveat downstream.
2. **Ask whether the floor is real or whether the search is still wrong.** The
   grid now reaches 1e-4. If the optimum is still there, the architecture has no
   operating point on this data set and that is a finding. If widening again moves
   it, the grid is still the problem and the first widening was not enough.
3. **Check the learning rate before concluding anything about architecture.**
   `README_for_the_webapp.md` already flags that the per-cell bank trains at a
   tenth the rate of the model that works, *"so the architecture comparison is
   uncontrolled."* The same question now applies to the trace, whose rate
   (`LR["trace"] = 1e-3`) is also a tenth of the tube's `1e-2`. **Until the rates
   are controlled, "the pooled baseline is worse" is not separable from "the
   pooled baseline was trained differently."**

That third point is the one that would change a claim, and it is cheap: refit both
at the tube's rate and see whether either finds an interior threshold.

## What this does not touch

The centre−surround row is unaffected — interior on all four folds, comfortably
so. Every number in the comparison against **the six** stands: those are
calibrated rather than trained, they never enter `pick_threshold`, and they moved
by less than 0.0003 across this whole change.
