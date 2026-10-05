<!-- Verbatim role report, except that this machine's absolute paths are written as %USERPROFILE% and <darkroom> (the repository is public). The unedited original is in <darkroom>/bugarach/2026-09-18-fair-comparison-run/report/review-roles-round2/. -->

GRANT 7 ok — Read, Grep, Glob, Bash

# Role 7, Reinventing the Wheel: reuse audit of the fair-comparison report (16ac704 / worktree HEAD c261f9c)

**Result:** Nothing in the new code gives a wrong number on this run's data. Every re-implementation I could check against its canonical version agrees on these data, and I confirmed that by running each pair where I could. The findings are about copies that will drift, three places where the rule differs from the canonical one and happens to agree today, and one typed claim about goal 1's reference rule that no committed file backs.

**Paths:**
- The four new files: `%USERPROFILE%\bugarach\bugarach-worktrees\fair-comparison-report\tools\{build_fair_comparison_report.py, fair_comparison_evidence.py, crowded_check_fair_comparison.py}` and `...\tests\test_build_fair_comparison_report.py`
- The run's code: `%USERPROFILE%\bugarach\bugarach-worktrees\tune-bench-comparison\tools\tune_learned_vs_coact.py`. The run declared commit e8764aa. There is no diff between e8764aa and that worktree's HEAD in this file, `src/bugarach/learn/` or `bench.py`.

## Findings (location · issue · severity · suggested fix · verified)

**1. Crowded-check reference differs from goal 1's rule, and the equivalence is typed, not computed.**
- **Location:** `crowded_check_fair_comparison.py:63`, and prose at `build_fair_comparison_report.py:981-983`.
- **Issue:** The reference is `{**OPERATING_POINTS, **coded_base}`. Goal 1's canonical rule is the shipped `OPERATING_POINTS` params (`tools/search_all_settings.py:884-889`, "what a candidate would REPLACE"). The report says so, then states "Scored against those, no verdict changes." `crowded_check.json` records only the coded_base reference. So that sentence is a typed claim, which the builder's own docstring (lines 10-12) forbids. The difference touches CoactDetect and LoCo only; for the other four detectors both references are `OPERATING_POINTS`.
- **Severity:** Medium.
- **Fix:** Have the crowded check also score goal 1's reference (`search_all_settings.py:884`) and write both verdicts. The builder should then generate the sentence from that comparison.
- **Verified:** Yes for the deviation (read both rules). No for the claim itself: it needs the shipped-point crowded scores, which nobody has computed.

**2. The fold split is derived a second time instead of using `bench.fold_split`.**
- **Location:** `fair_comparison_evidence.py:55-57` (`_seeds_of_fold`) and `:76` (`fold_of = i // spf`). The test copies it again at `test_build_fair_comparison_report.py:82`.
- **Issue:** The canonical version is `bugarach.bench.fold_split(...)`, with `.test(h)` and `.fold_of(s)` (`src/bugarach/bench.py:1198-1258`). Its docstring warns: "Derive it here and hand it around; deriving it twice invites two detectors to be scored on different held-out sets." The run uses it (`tune_learned_vs_coact.py:312`, `fold_seeds`). The copy matches today: contiguous blocks, read from `decl["recording_seeds"]`.
- **Severity:** Low-Medium.
- **Fix:** `split = bench.fold_split(n_folds=decl["folds"], seeds_per_fold=decl["seeds_per_fold"], base_seed=decl["recording_seeds"][0])`, then assert `list(split.seeds) == decl["recording_seeds"]`. Use `split.test(h)` and `split.fold_of(s)`.
- **Verified:** Yes.

**3. `_objective` copies the run's `objective()`, with a different grouping rule.**
- **Location:** `fair_comparison_evidence.py:122-130`.
- **Issue:** Canonical: `tune_learned_vs_coact.py:549-556` (`objective`, via `by_regime`, `pooled` and `f1_or_zero`). The copy always averages over both backgrounds (`for b in REGIMES`). The run averages only over the backgrounds actually present. The copy also pools `Score` objects directly, while the run pools them after a `score_row` JSON round trip. These are equivalent when both backgrounds are present, which they always are here. The committed `merge_gap.json` reproduces the coded scores to under 1e-9, and the test checks that.
- **Severity:** Low.
- **Fix:** The merge-gap subcommand already requires the tune-bench-comparison worktree on `PYTHONPATH`. Import `objective` and `score_row` from that tool instead of copying them. At minimum, group by the prefixes actually present.
- **Verified:** Yes.

**4. The draw rule is a third copy of the run's own.**
- **Location:** `fair_comparison_evidence.py:78-82` (`draw`).
- **Issue:** It is character-for-character the run's `Plan.fold_check.draws` (`tune_learned_vs_coact.py:398-401`): `TRAIN_SEED_BLOCK + seed*1000 + i` over `n_train`, and `VAL_SEED_BLOCK + seed*1000 + i` over 4. The "before the fix" order `[f"{b}:{s}" for s in sorted(train) for b in REGIMES]` matches the pre-fix `Plan.fold_recordings(training_folds(h))`; I checked it at 61d747a (lines 326-332 and 792). It matches `train.py:174` and `:269`. The literal `4` is `pick_threshold`'s default `n_val` (`train.py:244`), hard-coded in three places.
- **Severity:** Low.
- **Fix:** Import `Plan.fold_check`'s draw, or at least read `inspect.signature(pick_threshold).parameters["n_val"].default` rather than typing `4`.
- **Verified:** Yes.

**5. The test re-derives the draw and drops the `seed*1000` term.**
- **Location:** `test_build_fair_comparison_report.py:84-85`.
- **Issue:** The test uses `TRAIN_SEED_BLOCK + i` without `seed*1000`. That is correct only because `fold_draws.json` was made at seed 0, and the test never asserts `doc["seed"] == 0`. It is a fourth copy of the draw rule, and it is not the same as the other three.
- **Severity:** Low.
- **Fix:** Call `ev.fold_draws(RUN, ...)`'s inner draw on `doc["seed"]`, or add `+ doc["seed"] * 1000`.
- **Verified:** Yes.

**6. `GAP_KEY` is hand-kept and leaves out rate+context, which has a merge gap.**
- **Location:** `fair_comparison_evidence.py:50`. The builder has a second hand-kept key list at `build_fair_comparison_report.py:672`.
- **Issue:** Which detectors have a merge gap, and under what key, is declared in `bench.FULL_GRIDS` (`src/bugarach/bench.py:~216-277`): coact, loco and sce use `merge_gap_sec`, and rate uses `merge_gap_s` (grid top 8). `GAP_KEY` has only coact, sce and loco. So the merge-gap ablation never re-scores rate+context. Yet the report says every coded detector with a merge gap chose the top of its grid (Table 3, and the limits list at line 1144).
- **Severity:** Low-Medium.
- **Fix:** Derive it: `{d: k for d, g in bench.FULL_GRIDS.items() for k in g if k.startswith("merge_gap")}`. Rate+context is then re-scored, or its omission is explicit.
- **Verified:** Yes (read FULL_GRIDS and the declared `hand_axes`).

**7. The net re-decode hard-codes the run's gap instead of reading it from the checkpoint.**
- **Location:** `fair_comparison_evidence.py:206` and `:210`.
- **Issue:** The canonical decode is `decode_at` (`tune_learned_vs_coact.py:620-624`), which uses `trained.merge_gap_frames` as set by `pick_threshold` (`train.py:238-239`, `:338`). The evidence tool uses `int(round(g / tr.dt))`, and its reproduction check looks up the typed key `"2"`. The doc also types `net_gap_as_run_sec=2.0`. These match today (20 frames at dt 0.1), and reproduction is within 0.0015 F1.
- **Severity:** Low.
- **Fix:** Take the as-run gap from `tr.merge_gap_frames * tr.dt`, and assert it is in `NET_GAPS`.
- **Verified:** Yes.

**8. The threshold grid comes from live code, not from the run's declaration.**
- **Location:** `fair_comparison_evidence.py:174` (`grid = THRESHOLD_GRID`).
- **Issue:** The run declared its grid in `meta.json` (`declaration.threshold_grid`). The evidence tool reads the live `bugarach.learn.train.THRESHOLD_GRID` from whatever tree is on the path. They are identical now: 41 values.
- **Severity:** Low.
- **Fix:** Read `decl["threshold_grid"]`.
- **Verified:** Yes (ran the comparison).

**9. The fallback in `Run.cmp` is a copy of `_paired` that nothing reaches.**
- **Location:** `build_fair_comparison_report.py:121-124`.
- **Issue:** It copies `_paired` (`tune_learned_vs_coact.py:1569-1575`) exactly, except that it drops the `len(d) < 2` guard and the run's None→0.0 substitution (`column`, `:1654-1655`). It is never reached: `results.json` has `"<net> - coact"` for all four nets in both selections, and `cmp` is only called with `"coact"`.
- **Severity:** Low.
- **Fix:** Delete it and raise if the run's comparison is missing, or import `_paired`.
- **Verified:** Yes.

**10. The Nadeau-Bengio correction now exists in a second tool.**
- **Location:** `build_fair_comparison_report.py:67-69` (`_nb_factor`).
- **Issue:** The same correction is already in `tools/summarize_tube_self_supervised.py:69-95` (`paired`, `t_nadeau_bengio`). The two agree algebraically: t_nb/t = sqrt((1/n)/(1/n + ratio)). Neither copy is in `src/`.
- **Severity:** Low.
- **Fix:** Move one implementation to `src/bugarach` (a stats helper) and call it from both tools. Whether the ratio should be 1/3 for nets that fit on 10 of 72 recordings is a question for the statistics role, not this one.
- **Verified:** Yes.

**11. `mmss` re-implements the viewer's time label.**
- **Location:** `build_fair_comparison_report.py:183-186`.
- **Issue:** The canonical Python version is `bugarach.time_axis.label` (`src/bugarach/time_axis.py:74-82`), which the imported `Svg.time_axis` already uses. They differ under 60 s (`mmss(45)` gives "0m45s"; the viewer gives "45s") and on exact halves (Python rounds to even; the viewer uses JavaScript's `Math.round`). All four times this page prints agree: 15m40s, 26m, 16m33s and 20m.
- **Severity:** Low.
- **Fix:** `from bugarach.time_axis import label as mmss`.
- **Verified:** Yes (ran both).

**12. The participant count is recomputed instead of read from the ground truth.**
- **Location:** `build_fair_comparison_report.py:217` (`n_part = int(round(frac * n_roi))`).
- **Issue:** The simulator records the actual count on each `PlantedEvent.n_part` (`src/bugarach/simulate.py:122`). It computes it as `max(1, matlab_round(f * nR))` (`:831`), rounding half away from zero on the recording's own ROI count. The builder rounds half to even on the declared `n_roi`. Both give 6 for the Figure 1 event.
- **Severity:** Low.
- **Fix:** Take the event from `gt.events` and use `e.n_part`.
- **Verified:** Yes (ran it: 6 = 6, 33 ROIs).

**13. `NAME` copies `TITLES` instead of extending it.**
- **Location:** `build_fair_comparison_report.py:54-56`.
- **Issue:** It is a literal copy of `bugarach.ui.app.TITLES` (`src/bugarach/ui/app.py:156`) with "locust" substituted. `tools/make_bakeoff_summary_figure.py:53` and `tools/make_detector_table.py:77` already use `{**TITLES, "cicada": "locust"}`. The values match today.
- **Severity:** Low.
- **Fix:** `NAME = {**TITLES, "cicada": "locust", **{m: m for m in NETS}}`.
- **Verified:** Yes.

**14. `provenance_line` is a copy of `provenance_block`, and the docstring says otherwise.**
- **Location:** `build_fair_comparison_report.py:1198-1208`, and docstring lines 22-23.
- **Issue:** It near-copies `build_surrogate_report.provenance_block` (`tools/build_surrogate_report.py:1960-1971`); only the tool name and the trailing citation differ. The docstring says `provenance_block` is "imported rather than copied", but it is not imported.
- **Severity:** Low.
- **Fix:** Add tool and source parameters to `provenance_block` and import it, or correct the docstring.
- **Verified:** Yes.

**15. The Figure 5 x-grid is a second copy of `CODED_GAPS`.**
- **Location:** `build_fair_comparison_report.py:417`.
- **Issue:** The `gaps` list is typed out again instead of read from `merge_gap.json`'s `coded_gaps_sec` (which comes from `fair_comparison_evidence.CODED_GAPS`). If the evidence grid changes, `if g in gaps` drops points silently.
- **Severity:** Low.
- **Fix:** `gaps = run.gap["coded_gaps_sec"]`.
- **Verified:** Yes.

**16. The "refused every setting" test is an inference, not the run's own budget rule.**
- **Location:** `build_fair_comparison_report.py:100-105` (`refused_all`: `n_refused >= n_scored`).
- **Issue:** The run's canonical rule is `within(budget, probes, quiet)` (`tune_learned_vs_coact.py:567-569`), applied to the selection's `inner_probe_per_hour` and `inner_quiet_per_hour` against `meta.json` budgets. The inference relies on every scored setting also having been checked for admissibility. I checked all 24 gated selections both ways, and they agree: only the locust detector's four folds (16 of 16 refused, chosen setting over budget).
- **Severity:** Low.
- **Fix:** Apply `within()` to the recorded inner rates.
- **Verified:** Yes (ran both).

**17. The Figure 1 raster reorders tied rows relative to the viewer.**
- **Location:** `build_fair_comparison_report.py:229-230`.
- **Issue:** The docstring says the raster follows `bugarach.ui.diagnostic`'s rules. The canonical sort is `np.argsort(counts, kind="stable")` with row 0 at the bottom (`src/bugarach/ui/diagnostic.py:377-384`). The builder uses `argsort(-counts)` with row 0 at the top. Busiest-on-top holds, but rows with equal counts come out in the opposite order. Re-drawing the raster rather than calling `raster_panel` is justified: `raster_panel` produces Bokeh output, and the page is inline SVG only.
- **Severity:** Low / informational.
- **Fix:** `order = np.argsort(counts, kind="stable")[::-1]`.
- **Verified:** Yes.

**18. The test's personal-path check is a second copy of sapper rule SAP004.**
- **Location:** `test_build_fair_comparison_report.py:42-53`.
- **Issue:** It widens SAP004's pattern (`tools/sapper.py:~92`, forward slashes only) to cover backslash and WSL forms, but only for this report. The gap it works around is repo-wide. CLAUDE.md says to prefer a sapper rule and to file requests in `docs/sapper_feedback/`.
- **Severity:** Low.
- **Fix:** File a sapper feedback note to widen SAP004 to `[\\/]`, then have this test call the sapper pattern.
- **Verified:** Yes.

**19. The crowded check treats a refused reference differently from goal 1.**
- **Location:** `crowded_check_fair_comparison.py:99-100`.
- **Issue:** It marks a choice as failing when the reference is refused (NaN). Goal 1's `make_admissible` (`search_all_settings.py:283-286`) passes the candidate when the reference is None. This cannot change anything here: all six references are finite (0.46 to 0.83).
- **Severity:** Low.
- **Fix:** Call the veto comparison from `make_admissible`, or match its None rule.
- **Verified:** Yes.

## What already reuses the project's code correctly
- **The crowded check** calls goal 1's `_job`, `_key`, `TAIL` and `N_TAIL` directly (seeds 1 to 12, as goal 1's `sel[:N_TAIL]`). Its reference expression equals the run's `base_params()` (`tune_learned_vs_coact.py:229-232`). It pools through `bench.pool_scores`.
- **The evidence tool:**
  - builds recordings with `bench.make_recording`, as the run's `_planted` does;
  - scores coded choices with `bench.run_detector` plus `score_stream`, as `_score_settings` does;
  - gets net probabilities from `train.probabilities` and decodes with `encode.decode`;
  - takes the "before fix" draws from `fold_maker`.
- **The builder:**
  - imports the page kit (`Svg`, `figure`, `page`, `table`, `num`, `esc`) rather than copying it;
  - takes bench constants and `score.TOL_SEC` from source, and asserts the live bench matches the run's declaration;
  - uses `bench.stream_trains` and `recording_extent` as `run_detector` does, and `bench.make_tail_recording` with the same background mapping as `_job`;
  - resolves its output through `paths.darkroom()`.

## Boundary notes (not filed as role-7 findings)
- `earlier = 0.103` (`build_fair_comparison_report.py:742`) is typed from `docs/goals/learned-model-family.md` rather than read from a file. That is for the citation and verification roles.
- The merge-gap tool runs the network forward pass again for each of the four gaps (it caches on `(ck, thr, g)`). That is an efficiency point, not a correctness one.
