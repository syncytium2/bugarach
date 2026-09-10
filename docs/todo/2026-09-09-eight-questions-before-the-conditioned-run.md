---
status: waiting-on-tony
filed: 2026-09-09
---

# Eight questions that gate the conditioned run

waiting: Rule on the eight items in [`docs/conditioned_run.md`](../conditioned_run.md). None has a safe default, and the re-run of the senktide/TTX cohorts cannot start without them.

> **Not murderboarded** — working material for sessions in this tree.

Tony, 2026-09-09, on being handed the redesign: *"I don't think you can run this without my
feedback."* He is right, and this file exists so that judgement survives the session that
received it.

## Why there is anything to re-run

The 2026-09-09 full-cohort run is **withdrawn**. A K given as a percentage puts each
recording in the assessment once, at its own resolved count; the ROI summary the spec read
was filtered to one K, so the generator was fitted to the smallest 55 of 84 recordings.
Corrected, the simulated field and participation both move materially, so every F1, every
operating point and every detection in
`<darkroom>/bugarach/2026-09-09-full-cohort-senktide-ttx/` is void. The code is fixed; the
run is not redone. Both files in that folder open with the withdrawal.

## The questions

Each changes what gets built.

1. **Balance the assessor by weighting or by subsampling?** Weighting keeps all 67
   recordings and gives each group × arm cell equal influence; subsampling gives a strictly
   balanced 40 and discards 27. *Recommended: weight.*
2. **Which analysis windows?** The producer's shipped `long_window_20`, or windows
   recomputed to the stated definition — baseline 15–20 min back from baseline end,
   treatment 15–20 min starting 2 min after it. **Recomputing needs the three-delta
   interface, which exists in the browser and not in Python**, so this may be a build or a
   request to interface2.
3. **The two recordings under the 15-minute floor** — `20250912_227` (ORX, senktide, 14.9
   min) and `20241211_127` (MALE, TTX, 13.0 min). Keep, exclude, or ask the producer? The
   standing rule says which recordings are analysable is the producer's call.
4. **How finely to stratify?** Eight cells (group × arm) fits parameters on 5–11 recordings
   each. Four (group), two (arm), or eight? A judgement about how much structure the data
   supports.
5. **One operating point or several?** If detectors behave differently across field size,
   group or stream, does the run ship one setting chosen to hold across the range, or
   conditional settings? This changes what a calibration *is* and what the settings file
   must carry.
6. **Assess and bench the slow stream?** Roughly doubles the assessment and the bake-off.
   Slow carries the larger treatment effect and currently has neither.
7. **Is K the same percentage for both streams?** K is set by a person during MAHICE, and the
   assessor has run one stream to date.
8. **MAHICE — before or after?** It has never been run on an approved folder. Until it is,
   `RESET.md` §1 binds everything downstream.

## Defaults a session may take alone, flagged not hidden

`n_roi` drawn per recording from the empirical distribution rather than a fitted parametric
one · folds and seeds held at 6 × 12 unless a corrected pairwise winner is wanted, which
needs **eight folds at twelve seeds — 96 recordings, not a finer cut of 72** · the
rate-matched treatment-window surrogate specified but not run · no ranking published.

## Two decisions from the murderboard, separate from these

- **The TTX claim** — per-group with the zero-baseline denominators stated, or cut. Pooled
  across groups it is inadmissible under FOUNDATIONS §9, and the breakdown reverses it.
- **Authorship in the report.** A cold evaluator cannot tell what Tony built from what was
  automated.
