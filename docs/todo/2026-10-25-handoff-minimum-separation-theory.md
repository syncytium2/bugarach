---
status: picked-up
filed: 2026-10-25
---

# Handoff: derive the minimum separation of events the tools can resolve

**Picked up 2026-10-25** by the session that wrote it (Tony: the theory stays here), branch `synth/minimum-separation`.

**For a new session.** Tony, 2026-10-25: *"Discuss whether or not our analytical approach can
determine the minimum separation of events we can detect"* and *"What parameters of the data
determine min detectable separation"*. The discussion is done (below). Building it is yours. Goal
page: [`goals/synthetic-validation.md`](../goals/synthetic-validation.md), *Aim 0*. Synthetic only.
Claim a block on the machine-local board before the first write, and name the branch `synth/<slug>`.
A sister handoff puts the same question to human raters:
[`2026-10-25-handoff-rater-sheet-separation.md`](2026-10-25-handoff-rater-sheet-separation.md).
The two curves are meant to go on one plot.

## Why it matters now

Aim 0's generator holds events at least 20 s apart, and the coordination-rates prediction relies on
it (the *at-most-one-event term*). Real intervals do not. In
[`learned/runs/2026-09-25-real-intervals/gaps.csv`](../learned/runs/2026-09-25-real-intervals/gaps.csv):

| stream | 5th percentile gap | gaps under 5 s | gaps under 20 s |
|---|---|---|---|
| fast | 3.8 s | 7.5 % | 28 % |
| slow | 7.1 s | 0.9 % | 38 % |

So a quarter to a third of real intervals break the prediction's assumption, and that probably
accounts for part of its leftover rate residual. The fast stream's shortest gaps also sit near the
assessor's merge floor.

## What sets the minimum separation Δ between two events

**From the data:**
- **Jitter σ.** Two equal Gaussian onset clouds are unimodal below Δ = 2σ, which is exact. At the
  lab's σ of 0.10–0.15 s that is 0.2–0.3 s.
- **Participants per event, k.** For the clouds not to interleave at all, Δ must exceed the
  expected range of k onsets: about 3σ at 5 cells and 4.5σ at 20. More onsets also give more power
  to tell two clouds apart.
- **Background rate × number of cells, against the threshold K.** Chance onsets bridge the gap.
- **Shared cells.** With random membership two events share about k²/N cells. A cell with an onset
  in both events is direct evidence of two, if Δ exceeds the cell's own minimum interval.

**From the tools,** which in practice dominate:
- **The assessor** (`bugarach.assess`) merges clusters within `merge_bins` (2) bins of 1 s and
  gathers onsets ±1.5 s. That is a floor of about 3 s whatever the data.
- **The coordination-rates tool** stops seeing two events once they share a window w (1, 2 or 4 s).

## What to build

1. **The assessor's split probability.** Derive P(two events read as two | Δ, σ, k, K, b, N): enough
   consecutive bins between them must fall below K. Use the same machinery as `theory.py`'s
   `chance_clusters_per_min` and window sharing, with each event's onsets as a Gaussian cloud
   spread over the bins.
2. **The coordination-rates prediction for any interval distribution.** Replace the at-most-one-event
   term with the event train's pair correlation (the probability two events fall in one window, for
   a given interval distribution). The prediction then covers Poisson trains, hard-core trains and
   intervals drawn from `gaps.csv`. Report how much of the 0.01 Hz rate residual it removes on the
   Aim 1a record, and what it predicts for real gaps.
3. **The limit for any method.** Bound the separation at which one event of 2k cells cannot be told
   from two of k: a likelihood or Fisher-information bound (plan item 6 on the goal page). A
   numerical bound is fine.
4. **Check by simulation.** Plant pairs at controlled Δ (the generator's `min_sep_sec` must be
   overridden, or plant pairs by hand), at the lab's σ and participation, at both backgrounds. Then
   compare the assessor's and the count detector's measured split rate with item 1.

## Where things are

- **Theory and records:** `docs/learned/synthetic_validation/`. `theory.py` has `g`, the predicted
  excess cumulants, `chance_clusters_per_min` and `--from-record`. `aim1_one_source.py` is the
  simulation pattern; its README lists everything else. Keep every number recomputable by a script
  beside its record. That is the goal page's rule.
- **Generator:** `bugarach.simulate.simulate_coordination` (`min_sep_sec`). **Assessor:**
  `bugarach.assess` (`_clusters`, `merge_bins`, `wm_factor`). **Event floor:** ADR-0008,
  `bugarach.event_floor`.
- **Prior art to check first:** radar's range resolution and two-target resolution (the cross-field
  survey in `learned/synthetic_validation/prior_art/cross_field_survey.md`), seismology's
  resolution of overlapping events, and the two-Gaussian bimodality result.

## Done when

The goal page has a short section on the minimum separation with its figure (the split probability
against Δ for the assessor, the count detector and the bound), the coordination-rates prediction
covers real interval distributions, and the PR lists what was derived, what was fitted and what was
only simulated.
