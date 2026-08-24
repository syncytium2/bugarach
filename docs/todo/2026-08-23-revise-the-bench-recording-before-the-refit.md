---
status: open
filed: 2026-08-23
---

# Revise the bench, and the thing most worth revising is not the background

> **Not murderboarded** — a recommendation for sessions in this tree, same standing as
> [`the revision plan`](2026-08-22-the-revision-plan-mechanism-before-calibration.md).
> Every number is quoted from a named file. **If any of it reaches an outside reader,
> murderboard that artifact first.**

Asked for a view rather than a survey, so this is a position with a recommendation in it.
Three parts: yes revise it, here is the part that matters more than the part everyone is
looking at, and here is the order that keeps the result checkable.

## First: there are three simulated data sets, and only one of them is the bench

Written down because the three get called by each other's names, and the whole argument
below is incoherent if they are one thing. Asked directly whether *"the bench is a
simulated data set with known coordinated events, used to optimize the six and train the
tube, derived from the assessment of the user's folder"* — that sentence is true of the
third row and of nothing else.

| | what it is | where it comes from | what runs on it |
|---|---|---|---|
| **the bench** | `bench.make_recording(regime, seed)` | `BENCH_RECORDING` + `REGIMES`, **hardcoded module constants**. `bench.py` opens no file, reads no assessment, loads no JSON | the probes and sweeps — tolerance curve, guard, multiplicative bar, flat-vs-fitted |
| **the bake-off data set** | `fair_bakeoff.py --spec` | `generator_spec.json`, which `derive_spec.py` built **from an assessment** — once, in 2026-08-16, off the `.mat` store, then committed | the published comparison: all seven rows, including the tube's 0.668 |
| **the user's simulated folder** | generated in the browser | the **user's own** `assess` run on the **folder they opened**, live | the webapp's tune step |

Three consequences worth keeping:

- **The bench is not folder-derived and never has been.** Its structural values — ~33 ROI,
  0.36 s jitter, 18% participation — were measured off real recordings **once**, in
  2026-08-13, and frozen into the file. That freezing is the point of a bench and is not
  the complaint; the complaint is that the field it runs on was never updated with them.
- **The tube was not trained on the bench.** It, and every hand-written detector in the
  bake-off, was fitted on the spec-derived set. What `fair_bakeoff.py` borrows from
  `bench.py` is plumbing — `fold_split`, `pool_scores`, `run_detector`, `OPERATING_POINTS`.
- **The six's shipped operating points came from neither.** Read the `source` fields: four
  of the six are inherited defaults — *"sce_detect defaults"*, *"explore_sce viewer FAST
  point"*, *"rate_detect defaults"*, *"viewer FAST defaults"* — and only `loco` and
  `cicada` cite a measured-regime optimum. This is the revision plan's item 10, and it is
  why the bake-off ranking partly tracks **calibration status** rather than detector
  quality.

`evaluate(..., gen=...)` is the seam between the first two: it holds the difficulty axis
fixed while swapping the recording underneath, *"the fitted background out of
`docs/learned/generator_spec.json`, say, instead of the bench's flat one."* That parameter
is where this whole change lands.

## The flat field is a coherence defect, and that is worse than an accuracy one

`BENCH_RECORDING` runs a flat background. `assess` fits the background's shape from the
recordings it was handed, and `derive_spec` prefers that measurement over the reference
constant and says loudly when it had to fall back. So **the tool and the bench that
chooses the tool's settings disagree about what a recording looks like**, and `bench.py`
says so about itself: *"every operating point and every score in this package is still
measured on the old background."*

### ⚠ Corrected 2026-08-24 — this section originally predicted the numbers would barely move

It said: when `REGIMES` moved to the folder-derived endpoints the effect was measured
rather than assumed — 12 seeds, nothing re-tuned — and no detector moved by more than its
own seed spread with the ranking identical, so *"expect the same here."*

**That inference was wrong, and the measurement that refutes it was already in the tree
when this note was written.** `docs/learned/flat_vs_fitted.json` runs every detector on the
bench under both fields, 3 seeds, at the fitted shape 0.275:

| | flat F1 | fitted F1 | ΔF1 |
|---|---|---|---|
| sync | 0.367 | 0.500 | **+0.133** |
| rate | 0.636 | 0.547 | **−0.089** |
| sce | 0.155 | 0.107 | −0.047 |
| coact | 0.703 | 0.736 | +0.033 |
| cicada | 0.296 | 0.265 | −0.031 |
| loco | 0.674 | 0.703 | +0.029 |

**The ranking does not survive.** `rate` and `sync` are 0.269 apart on the flat field and
**0.047** apart on the fitted one — all but swapped, at 3 seeds. Changing the background's
**shape** is a much larger intervention than moving its **endpoints** was, and the two
should never have been reasoned about interchangeably. The probe records both fields: its
flat one gives every ROI 5.2 mHz with **none** silent, while the fitted one has a median of
1.06 mHz, a maximum of 112 mHz and **34.4%** of ROIs silent. That is a different recording,
not the same recording at a different level. (The revision plan's *"~35% against a flat
field's 2%"* is the same contrast measured elsewhere; the silent fraction of a flat field
depends on its rate, so quote one source or the other, not a blend.)

Two things follow. The `REGIMES` reassurance does **not** transfer, and nothing should
quote it about this change. And the argument below gets **stronger**, not weaker — if the
ordering of the six moves this much between two backgrounds, then standing on one point of
the difficulty axis and quoting a ranking off it is not a small sin.

⚠ Three seeds. The direction is clear and the magnitude is not; that is a reason to
re-measure it properly as the first step of the change, not a reason to discount it.

**The finding had no prose anywhere.** It landed as a JSON and a figure under a commit
message saying one of the two decisions *"is much bigger than the other"*, and no document
in the tree said which or how much. That is how a session ends up predicting the opposite
two days later.

The reason to fix it is that a user following the documented loop — measure my folder,
generate from that measurement, tune, detect — receives settings chosen on a field the
same tool has already told them does not exist. Real windows leave **~35% of ROIs silent**
against a flat field's 2%. Flat is not a live option that lost; it is settled against by
measurement, and the bench is the last place still using it.

Coherence defects are the expensive ones in this repo. The regime-shift incident took two
weeks, and it was not a wrong number — it was two parts of the system disagreeing about
what a reference window contained.

## The bigger error is that operating points are quoted off their own axis

This is the part I would actually spend the campaign on, and it is not on the plan.

`forks.md`'s open list records it in one line and then moves on: on the same 120 events,
CoactDetect recalls **0.817** at `baseline_quiet` and **0.560** at `baseline_busy`. That is
a 3.7-fold rate change — the **interquartile spread of untreated slices**, not an extreme
— costing **0.26** of recall, and **0.32** at the measured real participation.

Compare that with everything else currently being argued about. Crowding costs 0.144.
The multiplicative bar buys 0.050. The guard buys nothing. **Background sensitivity is
larger than all of them together, and operating points are chosen at one point on that
axis and reported as though they held across it.**

Making the background prettier does not touch this. A fitted shape at one rate is still
one rate. What touches it is **scoring across the axis instead of at a point** — and this
project has already solved exactly this problem once, in the same file.

## Do to the background what was already done to the tolerance

The matching tolerance used to be a constant that a score silently depended on. It is now
a curve: `TOLERANCE_GRID`, `evaluate_curve`, and `describe_curve`, which **refuses to hand
over a bare F1** for a detector still climbing at the widest tolerance scored — *"this
score depends on the matching tolerance"*. That change cost almost nothing and settled an
argument, because it turned a hidden constant into a visible axis and made one detector's
dependence on it impossible to quote away.

The background is the same shape of problem and deserves the same instrument. `REGIMES`
already holds the two endpoints and `evaluate_curve` already takes a `regime` argument —
it is fixed where the tolerance is swept. Swap which one is the axis:

- score each detector at **both endpoints and the median**, not at `baseline_quiet` alone;
- report the spread, the way fold spread is already reported;
- **refuse a bare F1 when the ranking changes across the axis**, exactly as
  `describe_curve` refuses one when the ranking depends on slack.

That last clause is the whole value. If the ordering of the seven is stable from quiet to
busy, the bake-off table is more defensible than it currently is and we can say so. If it
is not stable, then the published ranking is a fact about one background and every
sentence resting on it — including *"the tube ties CoactDetect"* — needs the axis attached.
**Nobody knows which**, and it is one bench run to find out.

I would land this **before** the fitted background, not after. It is smaller, it is
already-accepted in shape, and it tells you how much the fitted-background change is
allowed to matter.

## Move the recording, then measure, then re-fit — in three commits, not one

The `REGIMES` move is the pattern worth copying, and its virtue was the order: the axis
moved, the **existing** operating points were re-measured on the new axis with nothing
re-tuned, and only then was anything else touched. That is why "no detector moved beyond
its seed spread" can be said with a straight face — because a re-fit had not yet been
allowed to hide the movement.

So:

1. `BENCH_RECORDING` takes the measured shape, defaulting off, per fork #1.
2. Re-measure every existing operating point on it. **Nothing re-tuned.** Publish the
   old-versus-new table the way the `REGIMES` docstring does.
3. Only then re-derive grids and re-fit.

Doing 1 and 3 in one commit produces a set of numbers that moved for two reasons at once
and no way to separate them. That is the same error as measuring the guard between
recordings instead of within one, and it cost a published claim.

## What has to happen first is not code

`derive_spec` prefers a measured shape from the assessment. The assessment in the tree,
`assessment_real.json`, carries **`background: null`** and a `store` key — it predates the
fitter, and it was measured off the `.mat` store rather than the approved export folder. So
re-running `derive_spec` today falls back to the reference constant and correctly announces
that it did.

**The first step is a fresh `assess` over the approved folder, and a human's K call** —
`derive_spec` requires `--k` explicitly because an assessment does not get to parameterize
anything shipped without a person signing off on which K. Everything in this note queues
behind that, and it is Tony's, not a session's.

Land the sweep-subset control before the re-fit, too: LoCo and CICADA are **97%** of the
sweep's wall clock (fit seconds — sync 0.06, coact 0.08, rate 0.10, SCE 0.17, LoCo 2.69,
CICADA 7.06), and a campaign that has to be run twice at that price will not be.

## What I would not do

**Do not make the bench more realistic in several dimensions at once.** Fitted background,
crowding, treatment regimes, per-folder shapes — each addition makes the bench a better
imitation of a recording and a worse **instrument**, because a detector's score becomes a
function of more things nobody controlled. The bench's job is to discriminate between
detectors, not to be a recording. Crowding was handled correctly and is the precedent:
it went into a **separate** recording with its own control rather than into
`BENCH_RECORDING`.

**Do not regenerate `docs/learned/` a file at a time.** Everything in it was computed at
the old axis, and a half-regenerated folder mixes two calibrations with nothing saying
which is which — worse than a consistently stale one. One pass, old artifacts kept and
labelled, README table and the site's report last because they are what a stranger reads.

**Do not let the re-fit be the first thing that runs.** Three of the six detectors and the
learned model have defects that are not settings. Re-fitting a detector whose mechanism is
wrong bakes the defect into the new operating point at full price, and the campaign gets
run twice.

## In one line

Put the measured background in, because the bench should not contradict the tool. But the
change that would actually move what this project can honestly claim is **reporting the
difficulty axis instead of standing on one point of it** — the same fix the tolerance
already got, on the variable that costs five times as much.
