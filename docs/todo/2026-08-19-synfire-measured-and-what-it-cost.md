---
status: open
filed: 2026-08-19
---

# Synfire order, measured — and the null that had to be replaced first

Ran SPIKE-order over the 84-recording baseline folder, both streams, via PySpike's
implementation (same authors as the method). Results in
`<darkroom>/bugarach/synfire_{fast,slow}_relabel.json`; tool is `tools/synfire_scan.py`.

## The headline

**There is leader–follower order in these recordings, well above chance.**

| stream | above its own null (p<0.05) | median indicator |
|---|---|---|
| fast | **23 of 80** (29%) | 0.036 |
| slow | **44 of 82** (54%) | 0.099 |
| generated control, no order planted | **3 of 40** (8%) | 0.101 |

The control is the load-bearing row: `simulate.py` places each event's onsets as
independent jitter around a common time, so there is no order to find, and the test finds
none. 29% and 54% against 8% is the result.

## The null had to be replaced, and the first one was catastrophically wrong

The first run used this project's standing surrogate — per-ROI circular shift. **On the
generated control that null called 60% of order-free recordings significant.** It was
measuring the wrong thing: a circular shift destroys the coordinated events themselves, so
any recording that *has* events beats it, whether or not its participants fire in a
consistent order. It answered "is there coordination", which was already settled.

The replacement keeps every spike time and permutes **which ROI owns each spike**,
preserving the pooled event structure and each ROI's own count, destroying only the
assignment of cells to latencies. Control false-positive rate: 8% (95% 2–19%).

This is the second time in two days the same error shape has appeared — the assembly work
made it first, with the same circular-shift null answering the same wrong question. **Any
new measure on this folder should be assumed to need an event-preserving null until shown
otherwise.**

## Two traps in PySpike worth knowing

1. **`optimal_spike_train_sorting` returns an unnormalized value and calls it the synfire
   indicator.** Its docstring says "(p, F) — optimal permutation and synfire indicator",
   but it computes the directionality matrix with `normalize=False`. On the first
   recording tried it returned 324 where the indicator is 0.021. The indicator is
   `spike_train_order` evaluated on the sorted trains. Both are recorded in the JSON, the
   raw one only so a cSPIKE cross-check has something to match.
2. **The sort is simulated annealing with no seed parameter.** interface2 hit the MATLAB
   equivalent of this (`SYNCHRO_PROGRESS.md`: different surrogate counts land on different
   local optima). The tool takes the best of `--restarts` optimisations and seeds numpy per
   recording so a rerun reproduces.

## The group question — different answer from the assembly case, and not yet settled

The **fast** group difference does **not** survive the corrected null (chi-square p=0.40).
The **slow** one does: DI 16/17, MALE 16/22, OVX 6/18, ORX 6/25, and — unlike the assembly
result — it **survives** permuting group within spike-count strata (**p=0.0004**).

Three reasons it is still not quotable:

- **The magnitude shows no group gradient.** Median indicator: DI 0.087, MALE 0.137,
  OVX 0.083, ORX 0.093. What differs by group is whether a recording beats *its own* null,
  not how ordered it is. That is a detectability statement wearing a biology costume until
  someone separates them properly.
- **The strata are coarse and the cells are small.** In the top spike tercile it is DI
  12/12, MALE 9/9, OVX 2/5, **ORX 2/2** — ORX at n=2 cuts against the intact-versus-GDX
  reading the direction otherwise suggests.
- **The indicator is strongly anti-correlated with spike count** (fast rho −0.75, slow
  −0.40), so raw values are not comparable across recordings of different richness. Only
  the per-recording verdict is.

**It does converge with the connectivity effort**, which found its group effect in slow and
treats fast as a negative control. Two independent measures agreeing on which stream
carries group structure is worth something. Neither is evidence about the other's mechanism.

## What would settle it

Give the slow group result what the connectivity work gave its own: rate-matching and
node-matching, not just coarse stratification — `darkroom/murmuration/connectivity_handoff.md`
documents both. And re-run on the penumbra-subtracted store, since optical crosstalk
between neighbouring ROIs produces apparent latency structure and the relabel null cannot
remove it.
