---
status: waiting-on-tony
filed: 2026-09-15
---

# Binned SCE calls are scored over the wrong stretch

**What happens.** `sce_detect` reports each call with `onset_sec` = the start of its 10 s
bin and `width_sec` = `tlast - tfirst`, the spread of the events inside it
(`src/bugarach/detectors/sce.py`, the run loop at the end of `_window_detect`). That is
the MATLAB `generate_sce` contract and the parity tests lock it. `bugarach.score` reads
`[onset, onset + width]` as the call's stretch. The stretch therefore starts at the bin
edge and is only as long as the event spread, so it can end seconds before the events the
call was made on. A planted event late in its bin scores as a miss plus a false alarm.
LoCo does not have the problem: its onset is the first event.

**What it costs**, measured by `tools/make_detector_review.py --stages sce_rescore` on the
24 bench recordings and the same four held-out rounds as the bake-off (merging is off by
default, so each call is exactly one bin):

| background | scored as now: tuned F1 | scored over the full bin: tuned F1 | shipped (99th pct), as now → full bin |
|---|---|---|---|
| quiet | 0.446 (reproduces the bake-off) | 0.702 | 0.370 → 0.547 |
| busy  | 0.625 | 0.653 | 0.449 → 0.469 |

Scored over its own bin, binned SCE at its loosest setting sits inside the band of the
detectors the review calls "about the same", and the quiet-versus-busy anomaly ("binned SCE
scores higher on a busy background") disappears. It was produced by the scoring.

Found by the round-3 murderboard of the detector review (role 6), 2026-09-15.

**Decision needed (Tony).** Either

1. change what the scorer is given for binned SCE (the bin's own extent), leaving the
   detector's MATLAB contract and parity alone; or
2. change `sce_detect` to report the bin extent (or `onset = tfirst`) and re-baseline the
   parity fixtures;

then re-run the sweeps, the shipped scores and the bake-off. Until then, no ranking claim
about binned SCE from the bench should stand. The detector review states both scorings.
