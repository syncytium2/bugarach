GRANT 7 ok — Read, Grep, Glob, Bash

**Role 7 (Reinventing the Wheel): chorus-collapse page and `tools/diagnose_chorus_collapse.py`**

Paths below are relative to a worktree root. `<worktrees>/chorus-collapse` is main plus this branch. `<worktrees>/weekend-runs` is branch `replicate-run`. I edited nothing and wrote no intermediate files. I read the darkroom run archives but did not write to them.

Findings, one per row: location · issue · severity · suggested fix · verified against a source (yes/no).

**R7-1** · `tools/diagnose_chorus_collapse.py:287-341` (`replay`)
- **Issue:** It copies the training loop of `train.train` instead of calling it. The canonical loop is `weekend-runs/src/bugarach/learn/train.py:219-284`.
- **Does it match?** Yes, line for line:
  - `deterministic_cuda`, then `manual_seed`, then `pin_threads` (lines 221-223).
  - `arch.make(**overrides)` (the tuning tool passes `**conf["overrides"]` at `tools/tune_learned_vs_coact.py:820`).
  - `fold_maker` with the default `n_val`, as in `_run_fit` (tune:807).
  - The same seed block (230), `pos_weight` (236-240), crop sampling (256-273) and device moves.
  - The only additions are the logging, GELU hooks that observe without changing anything, and the warm-up branch.
- **Proof it matches:** both as-run replay JSONs carry `max_abs_diff_vs_checkpoint` 0.0 (I checked them), and the page asserts it at :838.
- **Why copying is still a problem:**
  - `train()` has no per-step hook and no learning-rate schedule, so copying was the only route. As a result, the 200-step warm-up the page offers as a repair (§5) exists only in this copy.
  - The claim "the loop below is train.train's, line for line" (:312) is guarded only by rerunning on the GPU. The test rebuilds the page from committed JSON, so an edit to `train.py` would drift out of sync unnoticed.
- **Severity:** minor.
- **Fix:** add optional `on_step(step, loss, out)` and `lr_at(step)` (or `warmup_steps`) parameters to `train.train`, defaulting to no-ops, and have `replay` call `train()`. At the least, if goal 2 adopts warm-up, put it in `train.train` rather than lifting this loop a third time.
- **Verified:** yes.

**R7-2** · `:88-123` (`collapse_table`)
- **Issue:** It re-implements the report's Table 2 collapse rule and its filename regexes. The canonical code is `R.archive_facts` in `tools/make_replicate_report.py`: regexes at 224 and 257, rule at 264-266, counts at 277-282.
- **Inner fits match exactly:**
  - Keying by `(seed, recs)` instead of `(seed, pair)` makes no difference: each `(draw, net, cfg, seed, pair)` maps to exactly one `recs`.
  - Counts: chorus_norm 146 and 153 of 432 fits, chorus_gain_norm 75 and 75, overlaps 111 and 38. These are identical to the replicate report's Table 2.
- **Refits use a different rule on purpose:** the table applies the one-call rule, but the run's own flag is `failed_training_signature` (`tune_learned_vs_coact.py:1581-1582`, read through `R.seed_flags`, `make_replicate_report.py:146-156`).
  - I checked the four refits the table calls collapsed. They are exactly the four the run flagged: first draw chorus_gain_norm fold 2 seed 3; second draw chorus_norm fold 1 seeds 1 and 2; chorus_gain_norm fold 3 seed 1.
  - The page's "agrees for these four" (§5) is prose; nothing asserts it.
- **Severity:** minor.
- **Fix:** factor the per-fit one-call dict out of `R.archive_facts` into a function both tools call. Have `table` also read `R.seed_flags` for refits and assert that the two rules agree.
- **Verified:** yes.

**R7-3** · `:244-246` (`trace`), and `:189` (`_head_probe`)
- **Issue:** It re-implements the scoring path: a CPU forward pass plus a float64 numpy sigmoid. The run scored with `T.probabilities` (`weekend-runs/src/bugarach/learn/train.py:101-114`: float32 torch sigmoid on the model's device, the GPU for these fits) and then `decode_at` (`tune_learned_vs_coact.py:625-637`).
- **Result on the recording shown:** the outcome matches. On quiet:2024 the archived `n_detected` at `own_index` is 1 call for the collapsed fit (fold 2, index 0) and 23 for the working fit (fold 2, index 29). `trace.json` has the same 1 and 23. Nothing checks this in code.
- **Severity:** minor.
- **Fix:** call `T.probabilities(model, enc.raster, logits=True)` (forward hooks still fire). Also assert that `len(calls)` equals the archived `n_detected`; `trace()` already opens that archive at :232.
- **Verified:** yes.

**R7-4** · `:366-372` (`_minutes`) and `:497` (ticks every 300 s)
- **Issue:** This re-implements the house time axis. The canonical code is `src/bugarach/time_axis.py`: `label` at 74-82 and `ticks` at 55-59. It is the Python port of `_time_axis_hook` and is tested against the viewer.
- **It does not match:**

| input | `_minutes` | `time_axis.label` |
|---|---|---|
| 0 | "0" | "0s" |
| 2.5 | "2s" | "2.5s" |
| 90.5 | "1m30s" | "1m31s" |
| 1234.5 | "20m34s" | "20m35s" |

  - Float seconds do reach `_minutes`: the planted-event tooltips pass float onsets (:463).
  - Ticks on the 2,693.8-s recording: the tool draws 9 ticks, one every 5 minutes. The house ticker gives 0, 10m, 20m, 30m, 40m.
- **Severity:** minor.
- **Fix:** `from bugarach.time_axis import label, ticks`, as `tools/make_slow_comodulation_figure.py:46-47` and `tools/build_surrogate_report.py:64` already do for SVG figures.
- **Verified:** yes (both run side by side).

**R7-5** · `:823-824` (`grid_floor`)
- **Issue:** The floor is taken as the smallest threshold seen in the census. The page then calls it "the lowest value on the threshold grid". The canonical sources are the run's declared grid (`meta.json` `declaration.threshold_grid`) and `THRESHOLD_GRID` (`weekend-runs/src/bugarach/learn/train.py:57-59`).
- **Value:** it matches. Both draws declare 41 thresholds with floor 0.0001, and the census minimum is 0.0001.
- **But the check is circular:** the assert "every collapsed fit at the floor" would pass even if no fit sat on the grid's floor.
- **Severity:** minor.
- **Fix:** have the `table` step record `R.load_run(folder)["decl"]["threshold_grid"][0]` in `collapse_table.json`, and have `page` assert against that.
- **Verified:** yes.

**R7-6** · `:159-166` (`_selectivity`), and page §3 plus the answer box ("It is not the failure found earlier in plain chorus (PR #596)… Here the encoder's output still does")
- **Issue:** The page contrasts this failure with PR #596's, but measures something different from what #596 measured.
  - #596's tool, `weekend-runs/tools/diagnose_chorus_training.py:46-65`, measured the raw (unstandardized) `pooled_mean_at_events_minus_elsewhere` on the mean-pool channels only, how far one onset moves a vote, and gradient norm per block.
  - The new tool measures a standardized d, taking the maximum over all 3 × width head-input channels: mean, spread and top-m (`weekend-runs/src/bugarach/learn/nets/chorus.py:118-131`).
  - So the new tool's d could be carried by the spread or top-m channels, which #596 never measured. A reader cannot put the two results side by side.
- **Severity:** major. It underpins a headline claim that this is a different failure.
- **Fix:** compute #596's `inspect()` quantities on the census recording for the chorus_norm fits and report them beside d. Otherwise, state plainly that the measures and channels differ.
- **Verified:** yes for the code paths. I did not compute #596's statistic on these fits.

**R7-7** · `:149-156` (`_bench`), `:281-285` (`planted`), `:54` (`REGIMES`)
- **Issue:** These re-implement pieces of `tune_learned_vs_coact.py`: `BENCH_REGIMES` (103), `seed_of` and `regime_of` (471-476), and the bench branch of `_planted` (595-604). They match exactly for ids like "quiet:2000".
- **Also:** `_bench` hard-codes dt 0.1 even though the loaded fit carries `fit.dt`. `replay` asserts dt 0.1; `census` and `trace` do not.
- **Severity:** minor.
- **Fix:** use `fit.dt`, or assert it. Optionally import the helpers from the tuning tool, which is present in the `--code` checkout.
- **Verified:** yes.

**R7-8** · `:724-728` (`CSS_EXTRA`) and `:426-428` (`_ypanel_label`)
- **Issue:** `--c1` and `--c2` repeat `R.CSS`'s `--draw-a` and `--draw-b` (`make_replicate_report.py:988-989` and both dark-mode blocks). The values are identical in light and dark. `_ypanel_label` repeats the inline code at `make_replicate_report.py:756-757`.
- **Severity:** minor (cosmetic).
- **Fix:** reuse the existing tokens, and lift the y-label helper into R.
- **Verified:** yes.

**R7-9** · `:458-463` (Figure 1's planted-event lane)
- **Issue:** The canonical lane (`src/bugarach/ui/diagnostic.py:265-285`, `lane_panel`) puts ▼ at `gt.times` and colours found versus missed through `score_detections`. This figure puts ▼ at the midpoint of `observed_span`, in one ink.
- **Impact:** the position shift cannot be seen at about 0.26 px/s. Found/missed colouring would show the working fit's hits directly.
- **Severity:** minor (optional).
- **Fix:** colour by `score_detections` against the working fit's calls.
- **Verified:** yes.

**R7-10** · `tests/test_diagnose_chorus_collapse.py`
- **Issue:** The test only rebuilds the page from committed JSON. Nothing guards the two copied rules (R7-1, the training loop; R7-2, the collapse rule) against drifting from their originals.
- **Severity:** minor.
- **Fix:** a test that needs no GPU and asserts the per-fit collapse function is the same object R uses (once R7-2 is factored out). For R7-1, the `train()` hook refactor removes the copy altogether.
- **Verified:** yes.

**Reuse that is already correct:**
- `R.Archive`, `R.Svg`, `R.x_axis`, `R.esc`, `R.CSS`.
- `checkpoint.load` via a temp file, which is necessary because `load` takes only a path (`checkpoint.py:184`).
- `T.fold_maker`, `T.deterministic_cuda`, `T.pin_threads`, `T.TRAIN_SEED_BLOCK`, `T._recording`.
- `encode.decode` with the fit's `merge_gap_frames`, `bench.make_recording`, `paths.darkroom`.
- Calls and events are both measured from `enc.t0`, so they sit on the same time base.

**Outside my role (for roles 3, 4 and 5):** both pages compute the same overlap, 111 chorus_norm fits collapsed in both draws, and read it in opposite ways.
- The replicate report says "the same fits largely fail in both (111 of chorus_norm's are the same fit)" and asserts "most failures recur" (`make_replicate_report.py:1188-1191`).
- This page says "Which fits collapse is not repeatable", with 111.5 expected by chance.
- The numbers agree; the readings contradict each other across two shipped pages.
