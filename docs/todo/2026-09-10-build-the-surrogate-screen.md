---
status: open
filed: 2026-09-10
---

# Build the surrogate screen — three tiers, cheapest first

> **Unblocked by Tony's rulings, 2026-09-10** — every candidate runs, and the tiers with a pooling
> operator run as a grid ([`which surrogates enter the screen`](2026-09-10-which-surrogates-enter-the-screen.md)).
> **Superseded in part by the overnight plan**,
> [`proposals/2026-09-10-surrogate-evaluation-overnight.md`](../proposals/2026-09-10-surrogate-evaluation-overnight.md),
> which builds this screen as a per-dataset tool, takes seven of its twelve candidates from
> Elephant, and measures every one against a known-bad control per leak statistic, a destruction test
> and three yardsticks — with no shortlist; the verdict rule is designed from those measurements.
> **Where the two disagree, the plan wins.** It launched 2026-09-11, stopping at 15:00; everything below is
> background.
>
> Two consequences of the full field entering. **The cost split is a build order, not a cut** —
> the cheap candidates can run while the ones that need real algorithms are still being written.
> And **the counting tier is the only tier that takes every candidate without the grid
> multiplying**, because it has no pooling operator; treat it as the workhorse rather than a
> pre-filter.

## Why a screen exists

A self-supervised coordination detector was proposed on 2026-09-10 and stopped by an eleven-role
review: its surrogate was separable one cell at a time. The full account, with the numbers, is
[`the run record`](../reviews/2026-09-10-coordination-without-labels_2026-09-10.md). The thesis
survived; the surrogate did not, and choosing its replacement is a measurement rather than an
argument.

## The three tiers

**Counting statistics — no model at all.** This is the tier that would have caught the failure, and
it runs in minutes. Per candidate surrogate, per stream, per *J*:

- sub-floor within-cell interval rate (the statistic that killed the dither: **0.0 %** of real
  60 s windows carry one, **29.5 %** of dithered ones do at *J* = 1.6 s, AUC **0.647** on that one
  count with no fitting)
- within-cell ISI divergence, real against surrogate
- edge-band onset density deficit, and boundary-frame pile-up — see
  [`the encoder clips`](2026-09-10-the-encoder-clips-onsets-onto-the-boundary-frames.md)
- binning collisions: two onsets displaced into one frame. `encode()` writes a binary raster
  (*"several onsets in one frame stay 1"*), so a collision silently loses an onset the positive kept
- **surrogate generation time** — see the cost note below

**A per-cell-only discriminator.** A model that structurally cannot see across cells. If it beats
chance on a candidate, that candidate leaks. This is the leak detector and the falsification test in
one object, and it is cheaper than the real model.

**The full model.** Survivors only.

## Two axes fixed before the grid runs

- ***J* is per-stream.** At *J* = 2.5 s, **50.4 %** of fast within-cell ISIs sit inside 2*J* against
  **0.00 %** of slow ones. One value cannot serve both.
- **τ, the dead-time floor, is declared not fitted** —
  [it is the producer's number](2026-09-10-the-dead-time-floor-is-the-producers-number.md).

## What it actually costs, and it is not compute

Pattern jitter is a dynamic program; joint-ISI dithering needs a per-cell 2-D ISI histogram;
operational-time dithering needs a per-cell rate estimate that is itself a parameter choice. **Each
needs its own support-violation tests**, because a subtly wrong surrogate produces a leak that looks
like a finding.

⚠ **Generation cost sits in the training inner loop.** The design draws fresh negatives every epoch,
so a surrogate that is free in the screen may bind at training time. Measure generation time as a
column of the counting tier, not afterwards.

## The figure this owes

The leak was found by counting and reported in prose. **Render it**: within-cell ISI distribution,
real against each surrogate, with the floor marked. CLAUDE.md's rule — if a finding is visual, draw
it before writing about it.

## Reuse, do not rebuild

- `graph.py` `jitter_trains` is an existing, tested, in-production per-onset dither. ⚠ **It wraps**
  (`np.mod`), so it is not splice-free and cannot be used unchanged as the no-wrap candidate.
- `bench.pick_operating_point` / `MAX_PROBE_PER_MIN` already select at a declared false-alarm budget.
- `tools/make_null_leak_figure.py` already ran a surrogate-as-positive control on the assessor — and
  it came out **non-flat**. Read it before designing this one's control.
