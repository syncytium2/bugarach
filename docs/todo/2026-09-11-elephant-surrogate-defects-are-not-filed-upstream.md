---
status: open
filed: 2026-09-11
---

# Elephant's surrogate defects, found at our timescales, are not filed upstream

> **Outward-facing, so Tony's call**: filing an issue on NeuralEnsemble/elephant publishes.

Reproduced by the surrogate-screen review in a scratch install of Elephant 1.2.1, on synthetic trains
(2026-09-10). The screen's adapter works around every one, so nothing here blocks the screen.

- **`jitter_spikes` with a nonzero window start** adds the start to the bin edges twice and indexes
  bins from absolute time: it raises `IndexError`, or silently places onsets outside their own bins.
- **`JointISI` fails silently three ways**: a train of fewer than three spikes is returned unchanged
  (its docstring says a dithered train is returned); an interval pair beyond the truncation limit, or a
  bin wider than the dither, falls back to plain uniform dither; with a small smoothing width it runs and
  moves nothing.
- **`trial_shifting` in concatenated mode** selects each trial with `>=` and `<=`, so a spike exactly on
  a trial boundary is emitted twice; and it drops every spike after the last whole trial.
- **`bin_shuffling`** floor-divides times in floating point, so on-grid spikes land one bin early.
- **No seed argument**: the module draws from both numpy's and Python's global generators.

## Closes when

Filed, or decided against, with the issue links recorded here.
