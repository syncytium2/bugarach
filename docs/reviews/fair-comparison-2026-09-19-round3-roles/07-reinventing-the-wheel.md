<!-- Verbatim role report, except that this machine's absolute paths are written as %USERPROFILE% and <darkroom> (the repository is public). The unedited original is in <darkroom>/bugarach/2026-09-18-fair-comparison-run/report/review-roles-round3/. -->

GRANT 7 ok — Read, Grep, Glob, Bash (SubagentHandback is the channel back to you; I hold no editing tools)

**Role 7, Reuse auditor: round 3, blind pass.** I opened no review records and edited nothing.

**What I audited**
- Artifact: `report.html`. I confirmed its git hash-object is 5c0ccbb.
- Report worktree at HEAD 6eb9b29: `tools/build_fair_comparison_report.py`, `tools/fair_comparison_evidence.py`, `tools/crowded_check_fair_comparison.py` and `tests/test_build_fair_comparison_report.py`.
- The run's code at e8764aa. I read it with `git show` and extracted a copy to `<scratch>/mb/r3-role-7/tune_e8764aa.py`.
- The project's reference code: `bench.pool_scores`, `bench.context_fits_the_null`, `search_all_settings` (`_job`, `Evaluator.summary`, `make_admissible`, `choose_settings`, `valid`), `learn.train` (`fold_maker`, `train`, `pick_threshold`), `score.score_detections`, `ui.diagnostic.raster_panel`, the `Svg.time_axis` in `build_surrogate_report`, and `summarize_tube_self_supervised.paired`.
- I also used the run's unpacked `scores/` and `fits/` under `%USERPROFILE%/runs/fair-comparison-2026-09-18/`.

**Note for the main thread:** `tools/build_fair_comparison_report.py` has uncommitted edits in the worktree (+110/−57; the Figure 8/9 rework and `recall_at`). I reviewed HEAD. I re-ran the checks that depend on the builder against a HEAD copy (`<scratch>/.../bfcr_head.py`), and the results are the same. The evidence tool, the crowded-check tool and `src/` have no uncommitted changes.

---

## Findings

Each finding is given as: location · issue · severity · suggested fix · verified.

**F1. The Figure-9 sentence leaves out a detector whose starting point was over the budget**
- **Location:** `build_fair_comparison_report.py` L122–126 (`start_over_budget`), used at L1529 and L1551. The artifact's section 9 bullet reads *"the starting points of binned SCE, LoCo, SPIKE-synch and rate+context were themselves over it in every fold"*.
- **Issue:** The helper infers "the starting point was over the budget" only from `moves[0].rescued_from_inadmissible`. A search that never moved because every setting was refused has no moves, so it counts as not over.
  - That is locust (cicada) in all 4 folds: `n_scored` = `n_refused` = 16, 0 moves.
  - Its chosen setting *is* the starting point. The run's own rule, `within(budget, probe, quiet)` (`tune_learned_vs_coact.py:567` at e8764aa), applied to the selection file's `inner_probe_per_hour` / `inner_quiet_per_hour` against `meta.json budgets[h]`, gives OVER in all 4 folds.
  - So 5 of the 6 coded detectors started over the budget, not 4. The sentence is incomplete rather than false: locust appears later in the same bullet, but for a different reason.
- **Severity:** medium-low.
- **Suggested fix:** Count a start as over the budget when either `moves[0].rescued_from_inadmissible` is set, or there are no moves and `within()` fails on the chosen (= start) rates. Alternatively, apply the run's `within()` directly and cite it. Then the list comes out as five detectors, or the sentence can say "all but CoactDetect".
- **Verified:** yes. I ran the run's `within()` on all 24 coded selections under the budget.

**F2. `breakdown` pools score rows by hand instead of calling `bench.pool_scores`**
- **Location:** `fair_comparison_evidence.py` L248–266 (`breakdown.tally`).
- **Issue:** It re-sums `by_frac`, `distractor_hits`, `n_fa`, `n_detected` and `hot_fa` itself. `bench.pool_scores` (`src/bugarach/bench.py:1261–1281`) says in its docstring *"Anything scored against this bench pools through here … Pooling is six lines, so it was rewritten instead of imported, and the rule … forked in silence. Import this."* The run's own `pooled()` (`tune_learned_vs_coact.py:529`) goes through it.
  - The two agree exactly today: 48 CoactDetect and 96 chorus-net recall cells, the distractor hit rates, and CoactDetect's `f1_by_background` all differ by 0.
- **Severity:** low. No number on the page moves, but the tool breaks a rule the project states.
- **Suggested fix:** Pool each background's rows through `bench.pool_scores`, wrapping them in `SimpleNamespace` as the run's `pooled()` does. Read `by_frac` and `distractor_hits` off the `BenchResult`. Keep only the per-recording `n_distractors` (it is not on `Score`, and I checked it is a constant 6) and `distractor_share_of_false_calls` local.
- **Verified:** yes (differential against the run's score files).

**F3. The context-rule sentence re-derives the rule and reads live grids instead of the declared ones**
- **Location:** `build_fair_comparison_report.py` L1198–1203 (`ctx_cut`).
- **Issue:**
  - It re-derives the rule as `v > min_sep` over the **live** `bench.FULL_GRIDS` and the live `BENCH_RECORDING["min_sep_sec"]`. The canonical rule is `bench.context_fits_the_null` (`bench.py:401`), which `search_all_settings.valid` (L110) also calls.
  - It does not read the run's **declared** grids (`decl["hand_axes"]`, which `contestants_table` already uses) or the declared spacing (`decl["hand_search"]["min_sep_sec"]` = 120).
  - The key handling differs slightly: the canonical rule reads `context_win_sec`, falling back to `context_win`, while the copy scans both.
  - `Run.__init__` asserts that the bench's recording keys still match the declaration, but not the grids. If `FULL_GRIDS` changes, this sentence would describe grids the run never walked, and `claim()` would not notice.
  - Today both routes give the same result: CoactDetect loses 240 s, LoCo 240 s and 480 s, rate+context 240 s, and the declared axes equal `FULL_GRIDS` for all six detectors.
- **Severity:** low (a drift risk).
- **Suggested fix:** Compute `[v for k in keys for v in dict(decl["hand_axes"][d]).get(k, []) if not bench.context_fits_the_null({k: v}, decl["hand_search"]["min_sep_sec"])]`.
- **Verified:** yes (both routes run).

**F4. "The budget refused every setting" is inferred from the search's internals**
- **Location:** `build_fair_comparison_report.py` L115–120 (`refused_all`), feeding `admissible()` at L134–136, Table 2, Table 3, the × marks in Figure 7, and section 9.
- **Issue:** It infers the outcome from `n_refused >= n_scored`, which depends on how `choose_settings` counts its caches. The run's own rule, `within()` on the selection's recorded inner rates, is available directly.
  - The two agree on all 24 coded selections under the budget: locust is refused in 4 of 4 folds and every other detector in 0.
- **Severity:** low.
- **Suggested fix:** Use `within()`, citing it as the run's rule, or assert that the two agree so a change inside the search fails loudly.
- **Verified:** yes.

**F5. The paired statistics are re-implemented, as a third copy in the tree**
- **Location:** `build_fair_comparison_report.py` L77–79 (`_nb_factor`) and L147–154 (`Run.stats`).
- **Issue:** These re-implement the run's `_paired` (`tune_learned_vs_coact.py:1569`). Importing it is not possible: the tool exists only on `tune-bench-comparison` and is absent from this worktree, so the copy is justified. The Nadeau–Bengio corrected *t* also already exists in `tools/summarize_tube_self_supervised.py:68–96` (`paired`, whose `TEST_TRAIN_RATIO` is also 1/3).
  - Against the run's stored comparisons, `stats` matches `_paired` to 0 over 112 values: mean, *t* and per-fold differences, for every net against every coded detector and tuned against untuned, both selections.
  - `tc` matches `summarize_tube_self_supervised.paired`'s `t_nadeau_bengio` to 3.6e-15 over 48 comparisons.
  - They differ at the edges only. When sd = 0 this copy gives NaN where the run gives None. A None F1 raises TypeError here, where the run's `column()` treats it as 0.0. Neither case occurs in this run.
- **Severity:** low / info.
- **Suggested fix:** None required. Optionally cite `summarize_tube_self_supervised.paired` as the in-tree reference for the correction, or move one paired helper into `src/bugarach/`.
- **Verified:** yes.

**F6. The crowded check re-implements goal 1's veto**
- **Location:** `crowded_check_fair_comparison.py` L89–101 (`crowded()`, `passes()`).
- **Issue:** It re-implements the veto instead of calling `Evaluator.summary` + `make_admissible` (`search_all_settings.py:241–293`). That is justified, because `make_admissible` also binds goal 1's other three budgets, which do not belong here.
  - It matches the reference: the mean of the two crowded backgrounds' F1; a refused setting is not admissible; NaN fails; `got >= ref - MAX_CROWDED_DROP`; seeds 1–12, the same as goal 1's `sel[:N_TAIL]`; recordings through `_job` / `make_tail_recording`. The reference parameters equal `meta.json declaration.reference` for CoactDetect.
  - One edge differs: goal 1 **passes** a candidate whose reference is None, while this copy **fails** one whose reference is NaN. It is not triggered: all 12 references and all 48 choices are finite.
  - `_clean` (L46–49) is dead code: there is no None or NaN in any chosen or `OPERATING_POINTS` parameters. Its docstring ("stored it as NaN") also contradicts what the code checks (None).
- **Severity:** low / info.
- **Suggested fix:** Factor the comparison into `search_all_settings`, for example a `crowded_veto(got, ref)`, and call it from both places. Drop `_clean` or correct its docstring.
- **Verified:** yes (read; the finite references and choices checked from `crowded_check.json`).

**F7. The fold-draw replay is copied in three places**
- **Location:** `fair_comparison_evidence.py` L83–87 (`fold_draws.draw`) and `tests/test_build_fair_comparison_report.py` L79–86.
- **Issue:** Both copy `Plan.fold_check`'s `draws()` (`tune_learned_vs_coact.py:397–400`), which is not importable from main.
  - The copy is identical, and it matches `train` (the `TRAIN_SEED_BLOCK` draw over `n_train`), `pick_threshold` (`VAL_SEED_BLOCK` with the default `n_val` of 4, served modulo `fold_maker`'s 2) and `fold_maker`, all at e8764aa.
  - The "before the fix" order matches e8764aa^'s `Plan.recordings`: sorted seeds, quiet then busy.
  - The test's docstring says *"not a copied rule"*, but the test copies the tool's draw. It proves the file can be regenerated, not that the rule matches `train()`.
- **Severity:** info.
- **Suggested fix:** Reword the test docstring, or add an assertion against `train`'s seed expression.
- **Verified:** yes (read against e8764aa and e8764aa^).

**F8. The merge-gap re-scoring follows the run's rules**
- **Location:** `fair_comparison_evidence.py` L127–135 (`_objective`) and L171–225 (`net_gaps`).
- **Issue:**
  - `_objective` duplicates the run's `objective` (`tune_learned_vs_coact.py:549`): it pools through `pool_scores`, counts a NaN F1 as 0, and averages the two backgrounds.
  - `net_gaps` decodes like the run's `decode_at`, except that it uses `merge_gap_frames = round(g/dt)` instead of `trained.merge_gap_frames`. The two are equal at 2 s.
  - Reproduction: the coded detectors reproduce the run exactly (max 0.0). The nets reproduce within 0.0015 F1 per refit and 0.0003 per fold mean, which is GPU-versus-CPU arithmetic, and the test pins it.
- **Severity:** info; no action.
- **Verified:** yes.

---

## Reuse that is correct (checked)

- **Figure 1:** it uses `bench.make_recording`, `bench.stream_trains` and `bench.recording_extent`, the same trains `run_detector` gets. Its row order is identical to `ui.diagnostic.raster_panel`'s frequency sort, busiest on top with the same stable tie order; I checked all 33 rows on seed 1000 in the busy background.
- **Time axes:** they go through `Svg.time_axis`, which calls `bugarach.time_axis.ticks` / `label`.
- **Figure 2:** it is drawn from `score.TOL_SEC`, and its rules match `score_detections`: the span is widened by the tolerance, matching is one to one, and probe calls are kept out of precision through `BenchResult.n_scored`.
- **`crowded_spacing`:** it uses `make_tail_recording` and `N_TAIL`, the same recordings as the crowded check.
- **`_refit_health` means:** they equal the run's `f1_mean` (max difference 0.0).
- **Page kit:** it is imported from `build_surrogate_report` rather than copied.

## Files referenced

- %USERPROFILE%\bugarach\bugarach-worktrees\fair-comparison-report\tools\build_fair_comparison_report.py
- %USERPROFILE%\bugarach\bugarach-worktrees\fair-comparison-report\tools\fair_comparison_evidence.py
- %USERPROFILE%\bugarach\bugarach-worktrees\fair-comparison-report\tools\crowded_check_fair_comparison.py
- %USERPROFILE%\bugarach\bugarach-worktrees\fair-comparison-report\tests\test_build_fair_comparison_report.py
- %USERPROFILE%\bugarach\bugarach-worktrees\fair-comparison-report\src\bugarach\bench.py (L401, L1261)
- %USERPROFILE%\bugarach\bugarach-worktrees\fair-comparison-report\tools\search_all_settings.py (L95, L110, L159, L241, L264)
- %USERPROFILE%\bugarach\bugarach-worktrees\fair-comparison-report\tools\summarize_tube_self_supervised.py (L68)
- %USERPROFILE%\bugarach\bugarach-worktrees\fair-comparison-report\src\bugarach\ui\diagnostic.py (L306)
- The run's code: %USERPROFILE%\AppData\Local\Temp\claude\c--Users-<user>-bugarach-bugarach\0c979457-501e-4b3d-9c4b-21e394823cf5\scratchpad\mb\r3-role-7\tune_e8764aa.py (extracted from e8764aa)
