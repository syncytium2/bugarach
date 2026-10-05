GRANT 7 ok — Read, Grep, Glob, Bash

**Role 7 (Reuse auditor), blind round 3.** Branch run/final-parameters @ 0638de5 in <worktree> = bugarach-worktrees/floor-and-grids. I edited nothing. The only scripts I ran were throwaway read-only ones fed through stdin, using the tune-bench-comparison worktree's venv (the default python has no numpy), with `sys.path` pointed at <worktree>/src.

**Headline:** the report re-implements the admissibility and adoption rules rather than calling them. Where it does, I recomputed against the canonical code and the darkroom records, and **no divergence changes a verdict in the README**:
- **Strict adoption matches the canonical rule on all 14 proposals.** `adoptable_strict` equals `score_bench_candidates.adoptable_on_the_search(...)` AND every-budget. It also matches the recorded `proposal.adoptable` in candidates.json. The only row where the two differ is slow binned SCE, where the canonical rule says True and the report says False. That is the report's extra budget gate (held-out close-events loss 0.0207 against the 0.02 allowance), which is intended.
- **The search records have not moved since phase 3.** For every proposal, the held-out gain row and the bracketing record the report reads from search.json are identical to the ones candidates.json captured. Re-running `score_bench_candidates.proposal()` returns the same proposal name.
- **The selection-budget rows are consistent (32 of 32).** `all(checks) == admissible` holds on every row. Recomputing each check with `make_admissible`'s arithmetic from the recorded values gives the same booleans. The recorded limits equal the current `MAX_PROBE_PER_MIN`, `MAX_FALSE_POSITIVES_PER_HOUR`, `MAX_PRECISION_DROP` and `MAX_CROWDED_DROP` in bench / bench_slow / bench_combined.
- **The report's hand-picked records match `versions_from`.** Its hard-coded choice of record (fast chorus from 064/phase3; slow and combined from phase3-chorus-slow-combined) gives the same versions as `score_cross_stream.versions_from` on the 3×3's record order: 6 of 6 chorus picks, 0 of 32 coded parameter sets differ, and all equal `cross_stream.json["chosen"]`. The `any`→`all` change in `versions_from` does not change which record it picks for this night's inputs.
- **The review-check script reproduces the canonical numbers exactly.** Its `shipped_f1`/`proposal_f1` equal candidates.json `mean_f1` to the last digit for all 4 rows. Its fast CoactDetect proposal close-events F1 (0.9555179541302634) equals the search's held-out `crowded_mean_f1` exactly, so its `score()`, `pool_scores` use and the `make_tail_recording` seeds 49–60 match `search_all_settings._job`/`held_out`.
- **The floor table does not depend on which detector it reads.** Every coded row in a stream has an identical under-floor signature (floors and counts by level), so reading it from the first coded row is safe. The participant counts in `participants_per_level()` come from the simulator's `n_part`, and Table 3 agrees with them.
- **The per-budget formulas match the canonical code:** `fresh_budgets` (probe, null, elevated-outside-quiet, swing) and `held_out_budgets` (probe = `probe_*_per_hour`/60 = `probe_per_min`; close-events = `tail_f1(name)-tail_f1("shipped")` ≥ −0.02). They agree with `make_admissible` (<worktree>/tools/search_all_settings.py:401-434), and the fresh-seed values come from `score_bench_candidates`, whose calls-inside/calls-outside arithmetic is the same as `bench.probe_counts` (<worktree>/src/bugarach/bench.py:1418).
- **The guard-cap move is the canonical function, reused correctly.** bench_slow and bench_combined import `settings_are_valid` from bench, and `guard_fits_the_context` reads `context_win_sec`, falling back to `context_win`, so rate is covered. The new test runs it on all three bench modules.

## Findings

**1. The report re-implements `make_admissible` instead of calling it**
- **Location:** <worktree>/tools/make_final_parameters_report.py:58-90 (`fresh_budgets`, `held_out_budgets`) and :117-123 (`all_ok`).
- **Issue:**
  - It checks the budgets in three hand-written copies instead of building an `Evaluator.summary`-shaped dict and calling `make_admissible(reference)` (search_all_settings.py:401).
  - The formulas match today, but the copies do not hold `make_admissible`'s guards. Where the canonical code checks `math.isfinite` on F1 and swing, the report takes `max(q, b)` for the probe. Python's `max(x, nan)` returns `x`, so a NaN busy probe would pass silently, where the canonical per-background `<=` would fail it.
  - `all_ok` skips `ok=None`. So the held-out precision swing, which was never measured, counts as a pass inside `every_budget`, where `make_admissible` fails a non-finite swing.
  - No NaN appears in adoption.json's budgets today.
- **Severity:** minor. It is latent, and the report says "every budget that was checked".
- **Fix:** build summary dicts and call `make_admissible`. Put the "not recorded" labelling on top, rather than re-deriving each comparison.
- **Verified:** yes. I recomputed all 14 proposals and 32 selection rows, and no verdict changes.

**2. `held_out_budgets` can only guess at the held-out precision swing, because the search never writes it**
- **Location:** <worktree>/tools/search_all_settings.py:745-758 (`held_out` output schema); consumer at make_final_parameters_report.py:89.
- **Issue:**
  - `_job` returns `precision` for both backgrounds (:259), but `held_out()` drops it when writing its rows.
  - That is why the report needs its own schema translation and marks the swing "not recorded" in every held-out cell.
- **Severity:** minor. The gap is disclosed in the README. The selection and fresh swings pass for all four strict proposals, so it does not change the adoption set.
- **Fix:** have `held_out()` write `precision_quiet` and `precision_busy`, ideally the full `Evaluator.summary` keys. Then finding 1's call to `make_admissible` works unchanged on held-out rows.
- **Verified:** yes, the schema. Whether the unmeasured swing would pass is not verifiable from the records.

**3. The fresh-seed budget set silently leaves out the close-events test**
- **Location:** make_final_parameters_report.py:58-71 (`fresh_budgets` has no `crowded` key); rendered in README Table 2's fresh column.
- **Issue:**
  - The held-out copy of the rule names its unmeasured budget ("precision swing not recorded"). The fresh copy just omits close-events, so `_bud` prints a bare "pass".
  - That contradicts Table 2's own caption ("A budget not recorded is named in the cell") and the reading guide (README:341).
  - Decision 1 does disclose it in prose (README:104).
- **Severity:** minor.
- **Fix:** add `crowded=dict(value=None, limit=-MAX_CROWDED_DROP, ok=None, note="not run on fresh seeds")` to `fresh_budgets`, including for chorus.
- **Verified:** yes.

**4. The adoption rule is re-derived rather than reusing `adoptable_on_the_search`**
- **Location:** make_final_parameters_report.py:207-230.
- **Issue:**
  - `adoptable_strict` re-derives gain lo > 0 AND bracketed. It should AND `score_bench_candidates.adoptable_on_the_search(p["name"], ho, br)`, or the recorded `proposal["adoptable"]`, with `every`.
  - The loose rule should be the only extension written in the report.
- **Severity:** minor. It is equivalent today on all 14 proposals.
- **Fix:** call the function. It keeps the report on the rule if the rule changes.
- **Verified:** yes.

**5. The review-check script hard-codes the adoptable set and uses its own bootstrap scheme**
- **Location:** <worktree>/tools/final_parameters_review_checks.py:37, 93-103.
- **Issue:**
  - (a) `ADOPTABLE` is typed by hand instead of being read from adoption.json's `adoptable_strict` rows. It matches today, but it becomes a second copy of the verdict.
  - (b) The paired bootstrap draws an independent index per background. The search's own held-out bootstrap uses one index per draw for both backgrounds (search_all_settings.py:722-741): 400 draws, gain taken as the bootstrap median.
  - So the two gain columns side by side in Decision 1's table are computed differently: joint vs per-background resampling, and median vs point estimate. The median vs point-estimate difference is disclosed; the resampling-scheme difference is not.
  - Combined binned SCE's paired interval has lo = +0.0012, close enough to zero that the scheme could matter.
- **Severity:** minor. It could become major if the choice of scheme flips combined SCE.
- **Fix:**
  - Read the set from adoption.json.
  - Resample with the search's joint index (or state why per-background), and report which estimate the gain is.
- **Verified:** partly. The code difference is verified. Whether combined SCE's lower bound stays above zero under joint resampling was not re-run, because it needs detector reruns.

**6. The Decision-1 table was copied from the record by hand**
- **Location:** README:49-54 (hand-maintained, outside the generator markers).
- **Issue:**
  - Tables 1–3 are written between markers by the generator; this table was copied by hand from review_checks.json.
  - It has already drifted: combined SPIKE-synch's paired upper bound reads +0.041, but the record holds 0.040499 → +0.040.
  - Figures in other hand-written paragraphs (e.g. the close-events loss 0.0165, the under-floor counts at README:75-80) are copied by hand in the same way.
- **Severity:** minor. It changes no verdict.
- **Fix:** have `make_final_parameters_report.py` read review_checks.json and write this table between markers too.
- **Verified:** yes.

**7. The selection-seed budgets come from a script that is not in the repository**
- **Location:** README:538-541; record 064/phase3-3x3/selection_budgets.json.
- **Issue:**
  - The README says the script reused `Evaluator` and `make_admissible`, but it is not in the repository, so that reuse cannot be checked from the tree.
  - I confirmed the arithmetic and limits, as the README says a reviewer did. I could not confirm the measured values, e.g. `crowded_reference` 0.978 for fast CoactDetect's sliding start.
- **Severity:** minor. It is disclosed, and the arithmetic is consistent.
- **Fix:** commit the script under tools/ and name it in the record, as review_checks.json does with its `tool` key.
- **Verified:** partly: the arithmetic and limits are verified; the values are not.

**8. `budget_table`'s "sliding starting point" note is hard-coded to fast CoactDetect and LoCo**
- **Location:** make_final_parameters_report.py:457-458.
- **Issue:**
  - The note fires for any proposal whose held-out anchor differs, and also, hard-coded, for fast CoactDetect and LoCo.
  - It should be derived for every row by comparing `search["shipped"][det].window_mode` with the shipped point, as `held_out_anchor` already does for proposals.
  - I checked all 18 searches: only fast CoactDetect and LoCo start sliding where the bench ships binned, so the output is right today.
  - The other differences between search start and shipped are all detector-signature defaults (`inspect.signature`, search_all_settings.py:164). That makes `changed_settings`' fill from `searched` correct.
- **Severity:** minor.
- **Fix:** derive the note per row from the search record.
- **Verified:** yes.

## No finding
- **bench.py's guard-cap move and its test** use the canonical `guard_fits_the_context` and are correct.
- **The `score_cross_stream.versions_from` change** leaves this night's outcome unchanged.
- **Existing tool, not in the diff:** `score_bench_candidates.job` re-implements `bench.false_positives_per_hour`, `evaluate_elevated_rate` and `probe_counts` by hand. Its formulas match `probe_counts`, but it counts `score_stream.n_detected` where `false_positives_per_hour` counts finite onsets. I did not check that the two are always equal.
