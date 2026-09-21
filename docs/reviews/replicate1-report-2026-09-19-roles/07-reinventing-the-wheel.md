GRANT 7 ok, holding Read, Grep, Glob, Bash. SubagentHandback is only for delivering this report. I have no Edit, Write or NotebookEdit.

# Role 7, reuse auditor: blind verify round 3

**Summary: no blocking findings; one major and nine minor.** I checked every place where `tools/make_replicate_report.py` re-implements tested code against the data from both runs, and every computed number I checked matches exactly. The major finding: `prf` and `add` rebuild the pooling rule by hand. The pooling function's own docstring says not to do that, and the copy drops its tolerance guard. The minor findings are other copies that could drift from their source, two stated rules that differ from what the code checks, and three values typed by hand or taken from a hardcoded constant when the run's own files record them.

## Findings

Format: location · issue · severity · suggested fix · verified against a source.

**1. `make_replicate_report.py:235-243` (`add` inside `archive_facts`) and `:274-280` (`prf`)**
- **Issue:** This is a hand-built copy of `bench.pool_scores` and `BenchResult.recall/precision/f1` (`src/bugarach/bench.py:1102-1169` and `1261-1302`). The `pool_scores` docstring records that exactly this ("Pooling is six lines, so it was rewritten instead of imported, and the rule ... forked in silence. Import this.") caused a past incident. The tuner already has the adapter for stored rows: `pooled()` in `weekend-runs/tools/tune_learned_vs_coact.py:542-547`.
- **Does the copy match?**
  - The formula is identical: precision is hit / (detected − hot_fa), and the NaN rules for F1 are the same.
  - I pooled every held-out row through `pool_scores` and the tuner's `objective`. That reproduced `results.json` with a difference of 0 for all net refits and all 48 coded score files in each draw.
  - The report's `split` totals equal those rows exactly.
- **What the copy drops:**
  - `pool_scores` refuses scores measured at mixed tolerances, and its result carries `tol_sec`. The copy has neither.
  - `recall` divides by zero where `BenchResult` returns NaN.
  - `test_precision_leaves_the_dense_stretch_out...` checks `prf` against a hand-written formula, not against `BenchResult`.
- **Severity:** major.
- **Fix:** Collect the rows per key and pool them through `pool_scores`, using the tuner's `SimpleNamespace` adapter. Take recall and precision from the `BenchResult`, and compute the outside-the-dense-stretch count as `n_fa - hot_fa`. Change the test to compare against `BenchResult`.
- **Verified:** yes.

**2. `:1040-1044` (`paired_t`)**
- **Issue:** It recomputes the t statistic that the run already wrote in `comparisons[sel][...]["t"]` and `["df"]`, which come from the tuner's `_paired` at `tune_learned_vs_coact.py:1585-1591`.
  - The values are identical: t = −13.02 and −2.77 with df 3, matching the page's −13.0 (p = 0.001) and −2.8 (p = 0.07).
  - The prose hardcodes "on 3 degrees of freedom" instead of reading `df`.
  - The run's guard (t is None when sd = 0) becomes a ZeroDivisionError here.
- **Severity:** minor.
- **Fix:** Read `t` and `df` from the run and use scipy only for p.
- **Verified:** yes.

**3. `:442-445` and `:471-476` (`raster_png`)**
- **Issue, layout:** The lane-over-raster layout is a hand copy of `coordination_diagnostic(traces=None)` in `src/bugarach/ui/diagnostic.py:601-637`. The deviation has a reason and it is filed: `raster_panel` shades the dense stretch over the raster when given `gt` (`docs/todo/2026-09-19-raster-panel-shades-the-probe-band-on-the-raster.md`).
- **Issue, false-alarm split:** The ✕/○ split is a copy of `lane_panel`'s rule at `diagnostic.py:221-245`.
  - I rebuilt the `lane_panel` figure: it draws 6 ✕ and 0 ○.
  - I recounted independently: 20 calls, 14 hits, 6 false alarms, 4 of them on distractors. This matches the page, and the ○ key row is correctly absent.
  - Because it is a copy, it can drift. The function also imports private helpers: `_render_png`, `_gap`, `_spans` and `_key`.
- **Severity:** minor.
- **Fix:** Fix `raster_panel` as the todo describes, or give `coordination_diagnostic` an option to leave the raster unshaded, then call it. Move the false-alarm split into a helper in `diagnostic.py` (for example `split_false_alarms(sc, ext, width)`) that both callers use.
- **Verified:** yes.

**4. `:810-823` (`matched_gaps`)**
- **Issue:** The docstring says each re-decode must reproduce the run "to within 0.001". The code asserts `worst < 5e-3`.
  - The first draw's worst is 0.00147. It breaks the stated bound and passes the one the code enforces.
  - The page itself prints the true worst ("off by at most 0.0015"), so no false number reaches the reader.
- **Severity:** minor.
- **Fix:** Make the documented bound and the enforced bound the same value.
- **Verified:** yes (both merge-gap files).

**5. `:814` and `:1007` (`net_merge`)**
- **Issue:** The nets' as-run merge gap (2 s) is taken from `net_gap_as_run_sec`, which `fair_comparison_evidence.py:276` writes as a constant; nothing measures it. The authority is the checkpoint's `operating_point.merge_gap_frames × dt_sec`, which is what `checkpoint.load` and the tuner's `decode_at` use.
  - I checked every checkpoint in both archives: 20 frames × 0.1 s = 2.0 s, so the value is right.
  - The report already opens checkpoints in `untuned_param_counts`.
- **Severity:** minor.
- **Fix:** Read the gap from the checkpoints and assert it equals the file's constant.
- **Verified:** yes.

**6. `:1873-1887` (`untuned_param_counts`)**
- **Issue:** It repeats `checkpoint.peek`'s format check inline on bytes read from the archive, using `getattr(checkpoint, "FORMAT", None)`. That fallback skips the check without a word if the constant is ever renamed. `FORMAT` does exist, and both archives are `bugarach.learned-model` version 1.
- **Severity:** minor.
- **Fix:** Use `from bugarach.learn.checkpoint import FORMAT` so a rename fails loudly, or add a `peek_doc(doc)` to `checkpoint`.
- **Verified:** yes.

**7. `:118-124` (`fold_f1`)**
- **Issue:** The docstring says this is "the tuner's own rule". The tuner's `column()` (`tune:1670-1671`) turns an `f1_mean` of None into 0.0 (`or 0.0`); `float(None)` here raises instead. It cannot happen in these runs, because every entry has an `f1_mean`.
- **Severity:** minor.
- **Fix:** `float(entry.get("f1_mean") or 0.0)`.
- **Verified:** yes.

**8. `:144-154` (`seed_flags`), and the page wording "called nothing"**
- **Issue:** The run's `f1_was_nan` means the pooled F1 is not finite. That is also true for a refit that made calls but hit nothing, so it is not by definition "called nothing".
  - All 3 flagged refits made 0 calls on every held-out recording: tube (first draw, fold 0, seed 4) and chorus_norm (second draw, fold 1, seeds 1 and 2).
  - So the page is currently true, but only by coincidence of the data.
- **Severity:** minor.
- **Fix:** Assert `n_detected == 0` from the rows `archive_facts` already reads, or change the wording.
- **Verified:** yes.

**9. `:233-270` (the collapse count behind Table 2) against † in Table 1**
- **Issue:** The two use different rules, but the page describes both as "one call per recording".
  - Table 2 uses the report's own rule: exactly 1 call on every recording at the fit's own threshold.
  - † uses the run's `failed_training_signature` (`tune:1581-1582`): F1 within 0.01 of 0.125, at a threshold of 1e-4 or less.
  - On refits the two rules agree in every case (1 in the first draw, 3 in the second). Inner fits have no flag on the run's side, so the report's own rule is justified there.
- **Severity:** minor.
- **Fix:** Have the build assert that the two rules agree on refits, so any divergence stops it.
- **Verified:** yes.

**10. `:1350` (Table 7, "a 4,096-frame crop") and `:969` (`TOL_SEC`)**
- **Issue:** Two results come from outside the run's files.
  - The crop length is typed by hand, but the run records `training.crop_frames` in every config. It is 4096 in all 24 chorus configs in both draws.
  - `TOL_SEC` comes from the current tree, not from the rows' `tol_sec`. Both are 2.5 today.
- **Severity:** minor.
- **Fix:** Read both values from the run's files.
- **Verified:** yes.

## What I checked and found clean

- **Reading the archives** (`archive_facts`: pairing outer refits with their fits and picking the threshold index per selection). The per-refit F1 recomputed from the archives equals `results.json` exactly.
- **Figure 1's recording and detector.**
  - The recording is `make_recording("baseline_quiet", 2000)`, which matches the tuner's `_planted` / `BENCH_REGIMES`.
  - CoactDetect runs through `run_detector` at the declaration's reference parameters, which are the ones the budget was measured with, and is scored with `score_stream`.
  - CoactDetect has no `extent_sec`, so the lane's scoring and `score_stream` agree.
- **Reading the matched-merge files.**
  - The gap keys agree with the tool's `f"{g:g}"` format.
  - The guard that the as-run gap equals the run's `per_fold` holds to 1e-9 in both draws.
  - CoactDetect's `reproduces_run` is exactly 0, at a chosen gap of 8 s.
- **Budget figure and "× 1.6" text.** They read `meta.json` budgets. The tuner's minimum-ceiling floor (`max(..., 1/hours)`) never applies in any of the 8 folds, so the text is exact.
- **Table 4.** The edge flags, grid tops and moves are consistent with the chosen configs. Converting locust's setting from frames to seconds with dt 0.1 is correct, since no `imaging_rate_hz` override is set.
- **Values read from the run and not re-derived:** `held_out_compliance`, `refused_everything`, the flags, `declaration_difference`, and the held-out seeds in the two-draws figure.
- **`Archive`** is not a duplicate: nothing in `tools/` or `src/` already reads these archives.
- **Time axes.** The only one is in the raster figure, and it comes through `lane_panel`/`raster_panel` with `_time_axis_hook`.

## Files
- %USERPROFILE%\bugarach\bugarach-worktrees\replicate-report\tools\make_replicate_report.py
- %USERPROFILE%\bugarach\bugarach-worktrees\replicate-report\tests\test_make_replicate_report.py
- %USERPROFILE%\bugarach\bugarach-worktrees\replicate-report\src\bugarach\bench.py (1102-1169, 1261-1302)
- %USERPROFILE%\bugarach\bugarach-worktrees\replicate-report\src\bugarach\ui\diagnostic.py (221-245, 601-637)
- %USERPROFILE%\bugarach\bugarach-worktrees\replicate-report\src\bugarach\learn\checkpoint.py (48, 169-181)
- %USERPROFILE%\bugarach\bugarach-worktrees\weekend-runs\tools\tune_learned_vs_coact.py (542-569, 1561-1591, 1670-1671)
- %USERPROFILE%\bugarach\bugarach-worktrees\merge-gap-second-draw\tools\fair_comparison_evidence.py (122-130, 158, 210, 276)

I wrote nothing to any repository. The only scripts I ran were piped to the venv Python over stdin.
