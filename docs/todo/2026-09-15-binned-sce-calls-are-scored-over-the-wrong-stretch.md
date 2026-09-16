---
status: done
filed: 2026-09-15
closed: 2026-09-16
---

# Binned SCE calls are scored over the wrong stretch

**Ruling (Tony, 2026-09-16): option 1** — the scorer is given the bin's own extent; the
detector's outputs and its parity fixtures stay as they are.

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

| background | scored as now: tuned F1 (dimensionless) | scored over the full bin: tuned F1 (dimensionless) | shipped (99th percentile), as now → full bin (F1) |
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

## Resolution

**The seam.** `SceStream` gained `extent_sec`: how far past `onset_sec` each call reaches,
which is the first bin's start to the last bin's end, clipped to the analysis window where a
partial last bin ends there. A merged episode covers every bin from its first to its last.
In peak mode it equals `width_sec`, because the half-prominence width already is the call's
stretch. `onset_sec`, `width_sec` and every other array are unchanged, and so are the parity
fixtures. `bugarach.score.score_stream` prefers `extent_sec` (named in `score.EXTENT_FIELD`)
over the width whenever a result carries one. It is not keyed on the detector's name, so
every other detector is scored exactly as before. Everything that scores through
`score_stream` picks it up: `bench.evaluate`, `sweep`, the tolerance and background curves,
and `lab`/`learn`. So do the viewer's lanes, whose tuple for SCE is now
`(onset_sec, extent_sec)`; its own key already said SCE's bars are ten seconds wide. So does
the browser's tune sweep: `sceDetect` returns `extents`, `sweepPoint` prefers them, and the
browser parity test pins them to Python's to 1e-9.

**Deliberately unchanged:** `detections.csv` still writes `width_sec` as the event spread
under `width_def = "tightness"`, which is what the column claims. The browser's one-line
demo score, and its detection lane, still read that width for SCE. They are display only,
and nothing is chosen from them.

**Before and after, measured on `bugarach.bench`** (the three default seeds, pooled; no
held-out folds, which is why these are not the table above). F1 is dimensionless; the
probe is firings per minute inside the dense-but-random block where nothing is planted.

| background | `threshold_pctile` (percentile) | F1 before | F1 after | hits of 45 planted events, before → after | probe before → after (firings/min) |
|---|---|---|---|---|---|
| quiet | 75 (grid floor) | 0.536 | 0.701 | 26 → 34 | 5.87 → 5.87 |
| quiet | 99 (shipped) | 0.418 | 0.567 | 14 → 19 | 5.67 → 5.67 |
| busy | 75 (grid floor) | 0.600 | 0.620 | 30 → 31 | 6.00 → 6.00 |
| busy | 99 (shipped) | 0.419 | 0.452 | 13 → 14 | 5.80 → 5.80 |

The number of calls is identical at every grid point. Rescoring moves calls from false
alarm to hit and never adds or drops one. The probe is unchanged on every point of both
sweeps and stays well under its ceiling of 9.0 firings/min.

It agrees with the review's measurement in direction and roughly in size. Quiet gains
most (+0.15 F1 at the shipped point here, +0.18 there); busy gains little (+0.03 here,
+0.02 there). The quiet-versus-busy inversion goes the same way too: at the grid floor,
quiet was below busy before (0.536 against 0.600) and is above it after (0.701 against
0.620). The absolute values differ because the recordings and the pooling differ.

**The gated picker refuses before and after, for the same reason.** On both backgrounds
F1 peaks at the grid floor of 75, so `pick_operating_point` raises `EdgeOfRange`. The probe
gate is never reached. The ruling did not ask for a retune, and `OPERATING_POINTS` and
`MAX_PROBE_PER_MIN` are unchanged. As an informational run only, a grid widened to 30–99.9
picks 70 on both backgrounds before and after. Quiet goes from F1 0.536 to 0.701 and busy
from 0.608 to 0.627, with the probe at 5.87 and 6.00 firings/min. On quiet, 70 and 75 tie
after the change. Widening the committed grid is the retuning step, and it is still open.

**Still owed:** the detector review's `sce_rescore` stage, the bake-off and any ranking of
binned SCE need re-running on this scoring before a claim from them stands.
Tests: `tests/test_sce_scored_extent.py` (a coordinated event 8 s into its bin, a miss plus
a false alarm over the spread and a hit over the bin; merged runs; a partial last bin; peak
mode; the fallback for results without an extent).
