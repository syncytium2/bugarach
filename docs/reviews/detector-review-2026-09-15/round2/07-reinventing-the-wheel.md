> **Public copy.** Lines that concern real treatment recordings are removed (4 here), per FOUNDATIONS §5, and machine paths are shortened to `<scratchpad>`, `<worktree>`, `<darkroom>` or `<home>` (sapper SAP004). Everything else is verbatim.

GRANT 7 ok — Read, Grep, Glob, Bash

# Role 7, Reinventing the Wheel: reuse audit of `tools/make_detector_review.py`

**Scope.** I read all of `tools/make_detector_review.py` (1,625 lines) and the `coact_bar` change to `tools/make_mechanism_figure.py`, and compared them with the project code they overlap. Where a check was cheap I ran it, using the worktree's `src` and the cached build in the scratchpad (`_work/`, `run/`).

**Overall.** Most of the builder already calls the project's own code, and I confirmed that much. The trouble is in three places: one sentence on the page, one figure's lanes, and a set of copied helpers that could drift apart later.

## Blocking

### B1. The page's warning that "the quiet level is busier than intended" comes from re-deriving the rate range a different way
- **Where:** `make_detector_review.py:926-955`, which produces `gen_real_rate_percentiles_mhz`. The sentence is at `tools/detector_review_template.html:210`.
- **What the builder does:** it computes the per-recording average event rate per ROI over every baseline window from `recordings_from_slices`. That is 84 windows, and the only thing dropped is a zero rate. Its 25th/50th/75th percentiles come out at **3.6 / 9.7 / 18.6 mHz**. The page compares these with the quiet and busy levels in `bench.REGIMES` (5.2 and 19.0 mHz) and flags a problem.
- **What the project already has:** `tools/make_roi_rate_distribution.py:76-105`, `baseline_rates()`. Its docstring says the range it reports "is quoted as the project's difficulty axis". It applies three floors (`MIN_DURATION_SEC=300`, `MIN_EVENTS=20`, `MIN_ROIS=8`). `tools/fit_background_shape.py:47-49,116` uses the same floors.
- **Evidence (run):**
  - `baseline_rates` on the `default` folder gives 80 windows and **5.17 / 10.21 / 19.04 mHz**. That reproduces `REGIMES` (0.0052 / 0.0190, median 0.0102) almost exactly.
  - On `steps_excluded` it gives **5.05 / 10.21 / 19.04 mHz**.
  - [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder]
  - The tree does hold a second definition. `docs/learned/generator_spec.json` `roi_rate.iqr` = 3.70 / 18.47 mHz, from `tools/derive_spec.py:147-150`, which has no floors. The builder's figure matches that one, not the one `REGIMES` was built from.
- **Fix:** the numbers compared with `REGIMES` should come from `make_roi_rate_distribution.baseline_rates`. Or report both, and say the difference is four near-silent baselines, not a mis-set level. Also remove or reword the ⚠. Keeping all 84 windows for Figure 10C/D is defensible under the export-folder rule, but the page must not compare them with a range defined on 80.
- **Verified against source:** yes.

## Major

### M1. Clipping calls to the window changes the scorer's verdicts in the lanes (Figure 9 controls)
- **Where:** `_overlapping` at `make_detector_review.py:225-234`, called from `_lane` (237-244) and used at lines 720 and 828.
- **The problem:** the builder moves each call's start and width to the window edges *before* passing them to `ui.diagnostic.lane_panel`. `lane_panel` then re-runs `score_detections` on those altered calls (`diagnostic.py:214-216, 271-273`). So the marks in the lane are verdicts on calls the detector never made.
- **Evidence (run on bench seed 3, full scoring vs. the lane's clipped scoring):**
  - All six hand-written detectors and the four tube models agree on hits, except that binned SCE in window B counts one more false alarm starting in the window (19 vs 18). That is only the clipped start moving inside the window; the verdict is the same.
  - **trace** and **tiny** do not agree. Their one call spans the whole recording.
    - Window A: the lane scores the planted event as found, but full scoring says not found.
    - Window B: the lane draws a false alarm (✕) that full scoring does not have.
  - So Figure 9 contradicts the `trace_winA` / `tiny_winA` counts that `_window_counts` computes with the real scorer.
- **Fix:** pass the calls to `lane_panel` unchanged. `_spans` (`diagnostic.py:100-131`) already clips the *drawing* to `ext`. If a span starting past the extent really draws wrong, fix that inside `_spans`, not by changing the scorer's input. Do not simply drop out-of-window calls either: a call just outside the window can still be the match for a planted event just inside it.
- **Verified against source:** yes.

## Minor

### m1. The scoring tolerance is hard-coded as 2.5 in three places instead of using `score.TOL_SEC`
- **Where:** lines 542 (`near_any`), 703 (`bench_seed_decoys_on_planted`) and 1117-1120 (the Figure 11A labels read "within 2.5 s").
- **Why it matters:** the values agree today (`TOL_SEC = 2.5`, `score.py:60`). But that constant's own docstring says it exists because "it was six bare 1.5s". The Figure 11A labels are drawn into the PNG, so the text-token check can never catch them.
- **Fix:** use `TOL_SEC`, and format the label strings from it.
- **Verified:** yes.

### m2. Figure 10C/D compare real baselines with a background fitted on a slightly different set of recordings
- **Where:** lines 922-948.
- **The problem:** `MEASURED_RATE_SHAPE` and `MEASURED_BURST_SHAPE` were fitted on the windows `fit_background_shape.baseline_trains` returns (80 windows). The "real" curve uses 84.
- **Evidence (run):**

| measure | builder (84 windows) | fitter's set (80 windows) |
|---|---|---|
| ROIs with no event | 37.9% | 35.8% |
| bunching (Fano) at 300 s | 5.28 | 5.64 |
| bunching (Fano) at 30 s | 1.77 | 1.79 |

  - On the fitter's set, its own `_diagnostics` puts the fitted field at 37.9% silent, above the real 35.8%. The page prints real 38% against fitted 37%, so the order flips.
- **Fix:** take the windows from `baseline_trains`, or say in the caption that the sets differ.
- **Verified:** yes.

### m3. Figure 2C re-implements LoCo's local surrogate pool
- **Where:** lines 505-535 (`counts_of` + `circular_shift_trains` + `matlab_prctile`).
- **Project equivalent:** `detectors/loco.py:434-460` `_threshold_pool`, with `_shared.distinct_coact` for the observed counts.
- **Evidence (run):** with the project functions, same bin, window and percentile, the numbers are identical:
  - bar from the whole recording: 4 ROIs
  - calls inside the busy block: 46 (whole-recording bar) vs 0 (nearby-60 s bar)
  - calls outside the block: 3 and 3
  - median of the nearby bar inside the block: 10 ROIs
- The caption already says the bar is an illustration. No change is needed; calling `_threshold_pool` would remove the copy.
- **Verified:** yes.

### m4. The Figure 2A rasters are hand-drawn instead of using `raster_panel`
- **Where:** lines 444-464.
- **The problem:** rows are sorted by event count over the *whole* baseline. `raster_panel` sorts by the drawn window, a fix recorded 2026-09-07 at `diagnostic.py` around lines 355-370. The marks also differ from every other raster on the page (Segments with `line_width=1.3` and ink `#2b2b2b`, vs. `RASTER_INK` dashes).
- Sharing one row order across A1-A3 is a real need.
- **Fix:** build a slice with `bugarach.io.slice_from_events` (already used at `surrogate_stats.py:1188`). Order the trains once, by the real version's counts inside the view. Then call `raster_panel(..., sort="store")`.
- **Verified:** yes, by reading the code.

### m5. Copies of `tools/make_intro_figures.py`
- [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder]
- `save_figure` (108-121) copies `_save` (`make_intro_figures.py:98-110`). The builder's version is stricter: it raises when no PNG is produced.
- `_sweep_one` (1020-1028) copies `make_intro_figures.py:69-85`.
- **Fix:** move these into one shared module.
- **Verified:** yes.

### m6. The tube internals are restated instead of read from the model registry
- `_kernels` (742-758) calls `_build_tube_variant(mode="subtract", guard_frames=0)` with the default arguments. It should pass `**ARCHITECTURES["tube"].cfg`. The defaults match today (`max_center_frames=128`, `max_ratio=40.0`).
- The brightness trace (779-783) restates the first stage of `tube.forward` (`tube.py:139-143`). The "center"/"surround" widths quoted in the text (792-794) restate the clamps in `tube.py:115-116` and `246-247`. Both match exactly.
- **Risk:** `tube.py:135-138` carries an open ⚠ about the two clamps disagreeing. If that ⚠ is resolved in `tube.py`, this copy will not follow.
- **Verified:** yes.

### m7. Table 2's "over the limit" highlight uses a different rule from the project's gate
- **Where:** lines 1351 and 1234.
- **The problem:** the table highlights a detector when its *worst round* exceeds the limit. `performance_table` gates on the *mean across rounds* (`performance.py:210-213`, `Row.gate`), and so does `bench._gate_on_probe`.
- **Evidence:** locust at the quiet level averages 19.35 calls/min against a 25 calls/min limit, so it passes the project gate. Its worst round is 34.7 calls/min, so the table highlights it.
- **Fix:** name the rule in the column header, or show `row.gate` beside it.
- **Verified:** yes.

[line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder]
- **Where:** line 1468 uses `on < w1`.
- **Project rule:** `detect_folder.py:493` uses `win_start <= onset <= win_end`, closed at both ends.
- The effect is negligible, but it is a second rule for the same question.
- **Verified:** yes, by reading the code.

### m9. The training recipe is copied from `fair_bakeoff.py`
- **Where:** `_train_one` (167-195) copies `fair_bakeoff.py:271-290`, and the split `(4 folds, 6 recordings per fold)` is hard-coded at lines 174 and 1017.
- Retraining is necessary because the bake-off saves no checkpoints.
- **Evidence (run):** all six retrained thresholds are bit-identical to the bake-off's fold-0 thresholds (e.g. tube 0.9715809801839131). The parameter counts also match.
- **Fix:** read `folds` and `seeds_per_fold` from `bakeoff.json`. At build time, assert that the thresholds equal the bake-off's fold 0, so any future drift fails the build.
- **Verified:** yes.

### m10. `coact_bar` rebuilds CoactDetect's bar instead of reading it from the detector
- **Evidence (run, seed 3):** 137 bins tested, a bar is defined for all 137, and `obs >= bar` agrees with `pval <= alpha` on 24 of 24 significant bins, with 0 disagreements. It matches the rule in `coact.py:214-226`.
- **Two gaps remain:**
  - Bins where z = 0 exactly (count equal to the null mean) get no bar.
  - The drawn bar leaves out the `min_rois = 3` floor that the detector also applies.
- **Fix (optional):** have `CoactResult` export the null standard deviation so nothing has to be rebuilt.
- **Verified:** yes.

## Checked and confirmed as reuse (no finding)
- **Scoring:** `score_detections` and `score_stream`. I also scored the Figure 11A demo with `score_detections`: hits at 12 s and 31 s, a duplicate at 33 s, a false alarm at 40 s, and a miss at 50 s. That matches the drawn labels.
- **Detector settings:** `make_diagnostic._detector_params` is exactly `bench.OPERATING_POINTS`.
- **Bake-off recordings:** both `spec_baseline_*.json` files match `{**BENCH_RECORDING, **REGIMES[r]}` with 0 differing keys. The bake-off's 24 recordings equal `fold_split(4, 6).seeds`.
- **Settings sweeps:** for all 10 detector/background pairs whose shipped setting is on the sweep grid, the `bench.sweep` row equals `bench.evaluate` at that setting (F1 and busy-block rate). SPIKE-synch's 0.1 is not on its grid.
- **Performance numbers:** `performance_table` and `fold_scores_from_bakeoff`. Recall by event size is averaged per round, which equals the pooled value here because every round has 30 events per level.
- [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder]
- **Figure 2B counting:** `_coact_frames` counts each ROI once per bin, the same as `assess._coact_count`, and works in whole frames, so no rounding error at bin edges.

## Files referenced
- <worktree>\tools\make_detector_review.py
- <worktree>\tools\detector_review_template.html
- <worktree>\tools\make_mechanism_figure.py
- <worktree>\tools\make_roi_rate_distribution.py
- <worktree>\tools\fit_background_shape.py
- <worktree>\tools\derive_spec.py
- <worktree>\tools\make_intro_figures.py
- <worktree>\tools\fair_bakeoff.py
- <worktree>\src\bugarach\ui\diagnostic.py
- <worktree>\src\bugarach\score.py
- <worktree>\src\bugarach\performance.py
- <worktree>\src\bugarach\bench.py
- <worktree>\src\bugarach\detectors\loco.py
- <worktree>\src\bugarach\detectors\coact.py
- <worktree>\src\bugarach\detect_folder.py
- <worktree>\src\bugarach\learn\nets\tube.py
- <worktree>\docs\learned\generator_spec.json
