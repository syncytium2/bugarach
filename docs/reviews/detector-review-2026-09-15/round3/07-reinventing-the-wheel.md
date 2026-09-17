> **Public copy.** Lines that concern real treatment recordings are removed (6 here), per FOUNDATIONS §5, and machine paths are shortened to `<scratchpad>`, `<worktree>`, `<darkroom>` or `<home>` (sapper SAP004). Everything else is verbatim.

GRANT 7 ok — Read, Grep, Glob, Bash

# Role 7 — Reinventing the Wheel: blind pass, round 3

**What I reviewed:** commit `699de8e`. The code is `tools/make_detector_review.py` (1,962 lines at that commit) and `tools/make_mechanism_figure.py`, checked against `src/bugarach/` and the sibling tools. Line numbers below are for `699de8e`.

**The working copy moved while I was reviewing.** It now has about 270 uncommitted changed lines in `make_detector_review.py`, mostly in the block-recall stage. See the note at the end.

**Python path caveat.** On Windows, `PYTHONPATH` needs `;` as the separator. My first two runs used `:` and imported `bugarach` from the main checkout. I re-ran every comparison that decides a finding against the worktree's own `src`. `score.py`, `bench.py`, `performance.py` and `detectors/_shared.py` are the same in both commits; only `detectors/rate.py` differs.

## Major

**M1. The "precision, decoy calls set aside" column rebuilds a count that `performance.py` says it cannot be built from, and the result is wrong in both directions.**
- **Where:** `tools/make_detector_review.py:1521-1523`. Used in Table 3 and in the "Most false alarms outside the busy block are decoys" paragraph.
- **What it does:** computes `n_hit / (n_scored - distractor_hits)`, capped with `min(1.0, …)`.
- **Why that fails:** `distractor_hits` counts decoys that fall within reach of *any* call's span. It does not count calls, and it does not exclude matched calls. `performance.MAX_DISTRACTOR_RATE`'s docstring says exactly this ("span coverage rather than firing … not restricted to unmatched detections") and switches that gate off until the measure is repaired.
- **What I ran:** I re-ran all six hand-written detectors at each fold's chosen setting from the bakeoff, on the held-out seeds. The hit, scored and decoy counts matched the bakeoff JSON exactly in all 12 detector × level cases. I then counted unmatched calls outside the block within `TOL_SEC` of a decoy, using `score._spans` and `score._gap`.

  | level · detector | page | correct |
  |---|---|---|
  | quiet · SPIKE-synch | **1.00** (1.014 before the cap) | **0.96** |
  | quiet · CoactDetect | 0.92 | 0.88 |
  | quiet · LoCo | 0.96 | 0.93 |
  | quiet · rate+context | 0.75 | 0.72 |
  | quiet · binned SCE | 0.55 | 0.52 |
  | quiet · locust | **0.57** | **0.64** |
  | busy · binned SCE | 0.92 | 0.85 |
  | busy · locust | 0.70 | 0.75 |

- **Why it goes both ways:** decoys that sit within reach of a *matched* call get subtracted anyway (5 to 17 such calls per detector), so the page is too high. A decoy that draws several calls is subtracted only once (locust: 173 calls against 121 decoys reached), so there the page is too low.
- **The cap hides it:** `min(1.0, …)` turns an impossible 1.014 into a clean-looking 1.00. The "(about)" label does not cover errors that can go either way.
- **Fix:** add the count to the scorer. `Score` could carry unmatched calls within tolerance of a decoy (it already computes `fa_times`, `fa_ends` and the decoy gaps). `fair_bakeoff._rows` records it and `performance.FoldScore` reads it. That also closes `docs/todo/2026-08-30-distractor-hits-counts-coverage-not-firing.md`.
- **Until then:** drop the column, or compute it for the six hand-written detectors as above (seconds per detector). Learned models would need their predictions kept.
- **Verified against source:** yes.

*[line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder]
- **Where:** `make_detector_review.py:594-627`.
- **What it builds:** its own binning (`counts_of`), a "whole-recording" bar (2 s bins, 200 shifts, 99.9th percentile) and a "nearby 60 s" bar (2 s bins, a 60 s window centred on the bin, 100 shifts, 99.9th percentile, recomputed at every bin).
- **Why that matches no detector:**
  - LoCo ships 1 s bins, a 120 s context, and the higher of the trailing and leading halves, re-anchored every 15 s (`detectors/loco.py:_detect_stream`, `OPERATING_POINTS["loco"]`).
  - CoactDetect ships a 2 s bin in a centred 60 s context, but decides by z at alpha = 1e-4, not a percentile.
  - binned SCE and locust, the whole-recording designs, use 10 s bins at the 99th percentile and frames at 99.999 respectively.
- [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder]
- **What already exists:**
  - `tools/make_clutter_edge_figure.py:bugarach_panel` draws this comparison with the real code: `sce_detect`'s stationary bar and `loco_detect`'s rolling envelope, on one statistic.
  - This builder already pulls each detector's own threshold trace through `ui.app._compute` for Figures 3-8 (`coded_results`, `_trace_loco`, `_trace_sce`).
- [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder]
- **Verified against source:** yes.

## Minor

**m1. `decoys_share` re-derives `performance.Row.distractor_rate`.**
- **Where:** `:1525-1527`.
- **Match check:** it matches exactly in all 24 rows (checked).
- **Problem:** it takes `n_distractors` from `BENCH_RECORDING`. `fold_scores_from_bakeoff` reads it from the bakeoff's own spec on purpose. The spec equals the bench today (no differences found).
- **Fix:** use `row.distractor_rate`.

**m2. The busy-block limit on the page is a different rule from `performance.Row.gate`.**
- **Where:** `:1511-1512` and `:1656`.
- **What differs:** the page flags a detector red when its worst round is over the limit (`p > ceiling`). `Row.gate` uses the average. At the quiet level, locust passes `Row.gate` (19.35 against a limit of 25) but shows red (34.7 in its worst round).
- **Mitigation:** the caption says so.
- **Fix:** add `row.gate` as its own column, so the project's verdict appears beside the worst-round detail.

**m3. `f1_ceiling` and `precision_ceiling` are derived twice.**
- **Where:** `:1547-1551` and `:1160-1161`.
- **Fix:** compute once and `put` once.

**m4. `_bench_survival` rewrites `detectors._shared.distinct_coact`.**
- **Where:** `:467-485`.
- **Match check:** identical on seeds 1000, 1007 and 1023 (0 of 4,050 bins differ).
- **Also:** it hard-codes `range(1000, 1024)` even though `_bakeoff_seeds()` exists in the same file. The realized-rate loop at `:1093` does the same.
- **Fix:** call `distinct_coact(trains, np.arange(0, dur + 2, 2))` and use `_bakeoff_seeds()`.

**m5. Block-recall chance line and constants.**
- **Where:** `:1214-1217` and `:1259-1264`.
- **Chance line:** the reach test is `score._gap(g, lo, hi) <= TOL_SEC` written out by hand. It matches, but it skips `_spans`' clean-up of non-finite and negative widths. Fix: import `_spans` and `_gap`.
- **Constants:** `BLOCK_SIZES` repeats `BENCH_RECORDING["participation"]` as a literal. `BLOCK_PLACE` hard-codes `hot_window` plus `ramp_sec`. Fix: derive both.
- **Checked clean:** `_block_events` goes through the simulator's decoy path, which builds events exactly the way planted events are built (`simulate.py:734-753` against `:775-797`). Recall outside the block comes from `score_stream(...).by_frac`. That reuse is correct.

*[line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder]
- **Where:** `:1774-1777`. The comment says "closed, as `detect_folder` counts".
- **Why it differs:** `detect_folder._run_nested` assigns a call to a window by its region label first, and already stores `region_idx`. `_detect_real` (`:1722`) throws that away.
- **Size:** in the cached real detections, 128 of 5,022 rows are assigned to a window by `detect_folder` but fall outside it on onset (locust 79, LoCo 46, rate+context 3).
- **Fix:** keep `e.region_idx` in `_detect_real` and choose one definition on purpose; or correct the comment.

**m7. Page layout.**
- **Where:** `_page_layout` at `:253-264`, and `:1788-1805`.
- **Monkeypatching:** `_page_layout` patches module globals in `make_group_raster_summary`. `build_page` already takes `lane_px=`; adding `names=` and `raster_px=` keyword arguments is the non-fragile route.
- **Duplicated layout logic:** `stage_real` calls `build_page` once per recording, then re-does `build_page`'s own "one x-axis per linked group" and height logic by hand.
- **Unit bypassed:** the lane label at `:1794` skips `_count_label`, so it prints a bare count ("LoCo · 12"). `:351` duplicates `_count_label` inline.

**m8. `tools/make_mechanism_figure.py` repeats the LoCo, CoactDetect and rate+context trace code from the builder's `_trace_*`, and keeps an older window filter.**
- **Where:** the filter is at line 116: `keep = (on >= win[0]) & (on <= win[1])`.
- **Problem:** `_overlapping`'s docstring (`:233-237`) explains why that filter is wrong: `lane_panel` re-scores its input, so dropping a call that starts just before the window can mark a found event as missed.
- **Only `coact_bar` is shared.** I checked its reconstruction against `coact.py:200-222` and it is correct, including the infinite-z bins.
- **Fix:** have one tool import the other's trace functions and `_overlapping`. Optionally, `CoactDetection` could expose the null standard deviation so no reconstruction is needed.

**m9. The regime percentiles are recomputed with a different estimator, and the prose calls them "matching".**
- **Where:** `:1083-1087`.
- **What differs:** `bench.REGIMES` comes from the population rate divided by a derived ROI count of 33.16, over 84 slices (`docs/generator.md` §"Where the numbers come from"). The builder uses the mean per-ROI rate over `fit_background_shape.baseline_trains` windows, skipping zero-rate ones (n = 80).
- **Result:** 25th percentile 5.0 mHz against 5.2; median 10.2 and 75th percentile 19.0 agree.
- **A second, related split:** Figure 2 calls 84 recordings (`recordings_from_slices`) "real baselines", while Figure 10 uses 80 windows.
- **Fix:** say "near", or name the estimator difference.

**m10. `stage_optimization` counts ties and picks by hand, where `bench.pick_operating_point` gives verdicts.**
- **Where:** `:1447-1463`.
- **Precedent:** `make_intro_figures._sweep_one` already reports the picker's verdict.
- **What the picker says on this build's `sweeps.json`:**
  - quiet: `EdgeOfRange` for binned SCE, `TooPromiscuous` for rate+context and SPIKE-synch;
  - busy: `TooPromiscuous` for SPIKE-synch;
  - it chooses LoCo's 99.5 at both levels.
- **Why it matters:** the prose says "a better value may lie past the end" for LoCo as well, but the picker finds an interior optimum for LoCo.
- **Fix:** put the picker's verdict next to the per-round picks.

**m11. `_real_members` copies `make_intro_figures.figure1`'s median-field picker, with an extra tie-break on `slice_id`.**
- **Where:** `:1685-1704`.
- [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder]
- **Fix:** move the picker into one shared function.

## Reuse I checked and found correct

- **Bench scoring:** `bench.evaluate`, `bench.sweep`, `fold_split` and the `pool_scores` route through `fair_bakeoff`.
- **Performance table:** `performance_table` supplies F1, its range, recall, precision and speed. Per-level recall averaged over folds equals pooled recall, because every fold has the same denominator.
- **Viewer vs bench:** `ui.app._compute` with `make_diagnostic._detector_params` gives the same onsets as `bench.run_detector` for all six detectors on seed 3.
- [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder]
- **Surrogates and statistics:** `surrogates.circular_shift` and `homogeneous_resample`; `assess.circular_shift_trains`; `count_dispersion.burst_rows` and `fano`. The rate strata inherit its 10-events-per-ROI floor, so "below 50 mHz" really starts at about 8 mHz in a 20-minute window.
- **Scoring helpers:** `score_detections` in `_window_counts`; `TOL_SEC` in `_overlapping`.

## Heads-up on the uncommitted working copy

The new `block_calls` counts calls that *start* inside `BLOCK_PLACE`. `Score.hot_fa` counts unmatched spans that *overlap* the window, and `score.py:259-265` explains why it chose overlap. If that number goes on the page, derive it with the scorer's rule. The hand-written `_wilson` interval is new too; if the project already has a proportion interval, use that.
