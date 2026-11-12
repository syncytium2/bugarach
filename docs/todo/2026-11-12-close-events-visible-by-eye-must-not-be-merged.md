---
status: open
filed: 2026-11-12
---

# Coordinated events a person can see as separate must be called as separate

Tony, 2026-11-12, as the tracked cohorts became the default dataset: the whole issue with
the earlier bugarach work was that short coordinated event windows, detectable by eye, were
merged into one call. On 2026-11-11 he put the by-eye limit at under 2 s.

This is the test the work on the new default has to pass first. It applies to every step
that turns onsets into calls or counts calls:

- **Characterizing coordination on the baselines.** A count of coordinated events made with
  a window or merge gap that joins events 1 to 2 s apart undercounts them, and every bench
  value fitted from that count inherits the error.
- **The detectors' operating points.** At the shipped settings no detector splits a pair of
  planted events closer than 5 s. The first search for settings that do is on the branch
  `synth/close-events` (PR #926): count (sliding) at a 0.5 s window with no merge gap splits
  0.88 to 0.97 of pairs 1 s apart on simulated recordings. Nothing from it is adopted.
- **What is shown to Tony.** A page that draws calls should let him check, on the real
  rasters, that events he sees as separate got separate calls.

## Open

1. Does `tools/measure_coordination_rates.py` join close events on the new default? Not
   checked.
2. Which settings to run on the real baselines, and at which threshold (4 x or 3 x sigma_est).
3. How this sits with ADR-0022, which keeps the event definition's window at 2 s (PR #924).
