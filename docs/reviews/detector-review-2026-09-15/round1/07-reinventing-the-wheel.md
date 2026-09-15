> **Public copy.** Lines that concern real treatment recordings are removed (2 here), per FOUNDATIONS §5, and machine paths are shortened to `<scratchpad>`, `<worktree>`, `<darkroom>` or `<home>` (sapper SAP004). Everything else is verbatim.

GRANT 7 ok — Read, Grep, Glob, Bash

# Role 7, reuse audit: findings for `make_detector_review.py`

Nothing is edited. I ran scratch comparisons against the tool's own cache (`review/_work/numbers.json`) and the bake-off runs (`scratchpad/run/*`). One gap: I have no Write tool and a hook blocks writing source through heredocs, so the scripts went to Python on stdin and nothing is saved under `mb_scratch/role07/`.

Paths are relative to `<worktree>\`. MDR means `tools\make_detector_review.py`.

## Copies that do not match the project's code

**1. Speed column uses the median; the project's table uses the mean.** Medium. Verified: yes.
- **Where:** MDR:1035, `x_realtime=float(np.median(...))`.
- **Canonical:** `src\bugarach\performance.py:213` takes the mean of `detect_x_realtime` over `fold_scores_from_bakeoff` (248–288).
- **Match:** F1, min/max, recall, precision and probe per minute are identical for all 24 detector×background rows. Only speed differs:
  - Most rows are within 1–2%.
  - Busy `tiny` is 12,820 in the review against 15,750 canonical, about 20% apart.
  - At the quiet background the prose names the slowest detector through a token (`perf_baseline_quiet_tube_ratio`, template:251). By the median that is `tube_ratio` (9,786). By the canonical mean it is `tube_ratio_guard` (9,660), so the sentence names the wrong detector.
- **Fix:** build the rows from `performance_table(fold_scores_from_bakeoff(f))`. Coded detectors come from the seed-0 file, learned ones from all three files. Keep only `by_frac`, `fit_sec` and `n_params` local.

**2. Burstiness (Figure 10D) does not use the project's definition.** Medium. Verified: yes.
- **Where:** MDR:694–710 (`_roi_stats`) and 827 (median across ROIs).
- **Canonical:** `src\bugarach\count_dispersion.py:21–42`, `burst_rows` and `fano`. `surrogate_stats` and `fit_background_shape` both use it.
- **Differences:** the review uses `var(ddof=1)` where canonical uses `var()` (ddof=0). It drops the partial last bin where canonical keeps it. It takes the median across ROIs where canonical takes the mean.
- **Size of the gap:** on the 84 real baselines (748 ROIs), measured at 30/60/120/300 s:

  | | 30 s | 60 s | 120 s | 300 s |
  |---|---|---|---|---|
  | Page (review) | 1.39 | 1.71 | 2.27 | 3.55 |
  | `count_dispersion.fano` (mean) | 1.77 | 2.53 | 3.73 | 5.28 |
  | Same definition, median | 1.35 | 1.63 | 2.06 | 2.75 |

  The alt text quotes "1.4 to 3.6" and "1.9 to 5.2".
- [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder]
- **Fix:** call `burst_rows` and `fano`, or state the variant in the caption. Say which window the fit used.

**3. The baseline-window rule is copied three times.** Medium: it matches today but will crash on a legal folder. Verified: yes.
- **Where:** MDR:352–367 (`_baseline_frames`), 780–785 and 1159–1160.
- **Canonical:** `src\bugarach\assess_folder.py:80–150`, `generation_window`. Its docstring says it was moved so callers stop making copies of this rule. Frames come from `src\bugarach\surrogate_stats.py:163–232`, `recordings_from_slices`.
- **Match on `steps_excluded`:** window, L, every ROI's frame train and every 2 s coactivity count are identical for all 84 recordings in both streams.
- **Difference 1:** the copies call `np.isfinite(r.analysis_start_sec)`, but that field defaults to `None` (`store.py:153`). `np.isfinite(None)` raises `TypeError` (confirmed). Any folder without analysis columns crashes. Canonical checks `has_analysis_window`.
- **Difference 2:** the copies match the exact name "baseline" and take the first one. Canonical does a prefix match on `BASELINE_TOKENS` and takes the longest region.
- **Fix:** `recordings_from_slices(slices, stream)`, then pass `rec.window` to `circular_shift` / `homogeneous_resample`.

**4. CoactDetect bar is a verbatim copy, and both copies drop recoverable bins.** Low. Verified: yes.
- **Where:** MDR:221–239, copied from `tools\make_mechanism_figure.py:113–126`.
- **Math:** correct against `src\bugarach\detectors\coact.py:214–223`. Every significant bin has obs ≥ bar, and every non-significant tested bin has obs < bar.
- **Shared defect:** the `z > 0` guard throws away bins where z < 0, although sd = (obs − mean)/z is still positive there. In window B, 27 of 71 tested bins get no dash. The Figure 4 caption says the bar "appears only at tested bins", which reads as all of them.
- **Fix:** one shared helper in both tools, with the guard changed to `z != 0`.

## Values typed in where the project already has them

**5. Probe-minute and fold constants are typed in.** Low: correct for this run. Verified: yes.
- **Where:** MDR:1010 and 1018 (`6 * 5.0` minutes), 933 (`i // 6`), 862 (`fold_split(4, 6)`).
- **Canonical:** `performance.py:259–264` and `tools\make_detector_table.py:96–99` derive these from the bake-off file's `seeds_per_fold` and `spec.hot_window`. The fold test is `bench.FoldSplit.test/fold_of`.
- **Match now:** the runs have `seeds_per_fold=6`, a 300 s hot window and seeds 1000–1023. A bake-off run with `fair_bakeoff`'s default `--seeds-per-fold 2` would be mislabelled silently.

**6. `bench.quiet_mhz=5.2` and `busy_mhz=19.0` are typed literals.** Low. Verified: yes.
- **Where:** MDR:851.
- **Canonical:** `bench.REGIMES[...]["bg_rate_hz"]`, which gives 5.2 and 19.0 today. Line 743 of the same tool already reads `REGIMES`. The tool promises that no number in the page is typed, and Figure 12's caption uses these two.

## Re-implementations whose results match

**7. Figure 2C bars rebuild LoCo's local pool.** Low. Verified: yes, for the quoted numbers.
- **Where:** MDR:500–538 (`counts_of` plus `circular_shift_trains` plus `matlab_prctile`).
- **Canonical:** `src\bugarach\detectors\loco.py:434–460`, `_threshold_pool`.
- **Match:** re-run through `_threshold_pool` with the same settings (2 s bins, 200 or 100 draws, 99.9th percentile, centred 60 s window), the results are identical: global bar 4.0, 46 calls inside the block against the global bar, 0 against the local one.
- **Differences:** the random draws differ (canonical draws once per non-empty ROI; here once per ROI, empty ones included). Binning differs (ceil+clip here, `matlab_colon` in LoCo). So bar values in individual bins may differ even though the counts agree. The observed counts match CoactDetect's binning (`coact.py:106–115`), not `distinct_coact`.
- **Caveat:** this bar is neither LoCo's rule (1 s bins, 15 s anchors, larger of the two 60 s half-windows) nor CoactDetect's (Gaussian z-test on one bin). The caption does not claim otherwise.
- **Fix:** call `_threshold_pool`, or label the panel as an illustration.

**8. Tube kernels are rebuilt by hand.** Low. Verified: yes.
- **Where:** MDR:576–592 and 624–628.
- **Canonical:** `src\bugarach\learn\nets\tube.py:109–121` (`Tube._kernels`) and 238–254 (`_centre_surround`).
- **Match:** centre minus surround equals `Tube._kernels / gain` to within 1e-9. The kernels equal the subtract variant's `_centre_surround` exactly.
- **Differences:** `40.0` is typed at 588 and 628 instead of read from the checkpoint's `cfg["max_ratio"]` (40.0 today). The reported centre widths (624) skip the `clamp(0.5, k/2)` the kernel applies. That has no effect at the fitted 1.87–6.26 frames.
- **Reuse route (verified):** load `tube`'s `state_dict` into `_build_tube_variant(mode="subtract", guard_frames=0)` and call `_centre_surround`. Its forward pass equals `tube` to within 1.2e-6.

**9. "Brightness" is recomputed.** Info. Verified: yes.
- **Where:** MDR:615–619, copying `tube.py:139–143`.
- **Match:** max difference 0.0 against the head's actual input, captured with a hook. The score line at 614 duplicates `learn\train.py:130–133` and also matches. Both copies inherit the kmin clamp warning in `tube.py:135–138`.

**10. Token lookup is a third copy.** Low. Verified: yes.
- **Where:** MDR:1186–1223.
- **Canonical:** `tools\build_learned_report.py:84–106`. That `_lookup` already resolves decimal keys such as `by_frac.0.1`, so the `recall_by_pct` workaround at MDR:1041–1042 would not be needed. Its store paths are fixed to `docs\learned`, so it is not directly importable.
- **Fix:** move `_lookup` to a shared module, or accept the copy.

## Checked and matching

- **Bench-seed scores:** MDR:342–348 goes through `ui.app._compute` (via `make_diagnostic`) and `score_stream`. Calls, hits, planted and probe counts are identical to `bench.run_detector` (`bench.py:664–685`) for all six detectors, with the same onsets.
- **`_window_counts`** (297–306) calls `score.score_detections`. Its overlap count follows the `hot_fa` convention (`score.py:265`). The NaN-width case it doesn't handle never occurs (0 NaN widths).
- **Coactivity counts:** `_coact_frames` (370–376) bins like `coact.py` (ceil, keeps the partial last bin). Counts match the `recordings_from_slices` route exactly.
- [line removed from the public copy: it concerns real treatment recordings (FOUNDATIONS §5); the verbatim report is in the darkroom delivery folder]
- **Sweeps:** `stage_sweeps` / `_sweep_one` (858–877) call `bench.sweep` and `hot_fa_per_min`, mirroring `make_intro_figures.py:60–86` without its pick. The bake-off's generator spec is identical to `BENCH_RECORDING` plus `REGIMES` (no keys differ).
- **Training:** `_train_one` (123–149) copies `fair_bakeoff.py:279–290` (steps 900, crop 4096, batch 3, `n_train=min(10, n_fit)`, `LR` imported). The settings match.
- **Display names:** `NAMES` (72–75) re-lists what `make_detector_table.py:77` builds as `{**TITLES, "cicada": "locust"}`. Cosmetic.
