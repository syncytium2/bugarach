GRANT 7 ok — Read, Grep, Glob, Bash

Role 7 — Reinventing the Wheel: final-parameters report and its code (worktree `floor-and-grids`)

**Scope:** five `bench.py` functions, `bracketing`/`warm_floors` (`tools/search_all_settings.py`), `versions_from` (`tools/score_cross_stream.py`) and all of `tools/make_final_parameters_report.py`, each compared against the project's existing code: `event_floor.py`, `tools/detect_with_floors.py`, `tools/measure_rate_stretches.py`, `make_admissible`/`choose_settings`/`coordinate_rounds`, `bench.pick_operating_point`, `score_bench_candidates.adoptable_on_the_search`, and the detectors' own refusals in `loco.py`/`coact.py`. The night's `search.json` records in the darkroom were opened read-only to see whether any divergence changes a verdict.

**Summary:** 1 major (it repeats a defect the canonical gate already fixed), 5 minor (duplicates that currently match their reference).

## Findings

**1. The held-out close-events check compares against the wrong starting point.** · major · verified yes
- **Location:** `tools/search_all_settings.py:738` (`held_out`: `crowded_gain_vs_shipped = tail_f1(name) - tail_f1("shipped")`) → `tools/make_final_parameters_report.py:81-88` (`held_out_budgets`) → Table 2 and `every_budget`/`adoptable_*`.
- **Issue:** It measures the loss against `candidates["shipped"]`, the search's starting point, which `--sliding` forces into sliding form (`search_all_settings.py:979-986`). The canonical gate `make_admissible` (`search_all_settings.py:401-432`) was deliberately changed on 2026-09-17 to measure against `OPERATING_POINTS[d].params`, the point that actually ships; the comment at `search_all_settings.py:1044-1058` records that sliding-at-binned-values "ships NOWHERE" and cost a run. So the held-out check repeats a defect the canonical gate had fixed.
- **Consequence:** Table 2 shows **fail: close-events test** for fast CoactDetect's proposal, which the canonical reference would pass; the README's Decision 4 says a review re-run against the binned point gave a 0.0165 loss, inside the 0.02 allowance. Fast LoCo's held-out close-events "pass" is likewise against the sliding point and was never re-run against the canonical reference. No strict-adoption verdict changes, because both are unbracketed.
- **Fix:** In `held_out`, also score the `OPERATING_POINTS` params on the held-out close-events recordings (the `reference_points` already built in `main`) and compute `crowded_gain_vs_shipped` against that; have `held_out_budgets` read it instead of footnoting the mismatch.

**2. `bracketing()` uses a different edge rule from the project's canonical one.** · minor (no verdict on the page changes) · verified yes
- **Location:** `tools/search_all_settings.py:303-331`.
- **Issue:** The canonical rule is `bench.pick_operating_point` (`src/bugarach/bench.py:2229-2290`; `EdgeOfRange` at 1994): "a plateau that reaches the edge is not a boundary answer", so if any point tied for the best F1 is interior, the optimum is bracketed. `bracketing()` flags any chosen value at a grid end, ties or not.
- **Checked against the records:**
  - Fast LoCo pair: F1 climbs strictly to `threshold_pctile` 99.99 (0.7936 → 0.7996), so "cap" holds under either rule.
  - Slow LoCo's pair candidate sits at `threshold_pctile` = 1.0 on an exact plateau from 1 to 97 (mean F1 0.83269 at every value). `bracketing` calls it "limit"; the canonical rule calls it bracketed. It is not the slow LoCo proposal (the proposal is "rounds"), so nothing on the page changes, but "limit" misdescribes a plateau — which matters for Decision 2 ("does a limit count?").
  - Related: on ties, `pair_grids` (`:671-693`) keeps the first strictly-better value in grid order, which is how a plateau resolves to 1.0; `pick_operating_point` returns the first *interior* tied point.
- **Fix:** Reuse `pick_operating_point`'s plateau test (bracketed if any tied-best point on that axis is interior), or state in the `bracketing` docstring and in the README why the search is stricter than the bench's own rule.

**3. `bracketing()` duplicates `choose_settings`' edge loop.** · minor · verified yes
- **Location:** `tools/search_all_settings.py:303-331` vs `choose_settings`'s `edges` loop at `:654-662`.
- **Issue:** Near-identical logic (numeric test, `setting_applies`, NaN skip, min/max); `bracketing` adds only a `None` skip. It also reconstructs the extension count as `len(grown) - len(declared)`, while `coordinate_rounds` keeps the real counter (`extensions`, `:457`) but does not return it; the two agree today only because each extension appends exactly one value. Neither loop filters the grid through `valid()`, so an axis whose usable end is set by `context_fits_the_null` (e.g. combined CoactDetect's 120 s context) is not flagged; the README discloses this gap for that one case.
- **Fix:** One `_edges(det, params, grids, is_valid)` helper used by both, with `coordinate_rounds` returning its `extensions` counter for `bracketing` to read.

**4. The report builder re-derives the adoption rule instead of reading it.** · minor · verified yes
- **Location:** `tools/make_final_parameters_report.py:207, 227-230`.
- **Issue:** It recomputes `bracketed is True and gain.lo > 0`. The canonical rule is `score_bench_candidates.adoptable_on_the_search` (`tools/score_bench_candidates.py:83-88`), whose result is already in `candidates.json` as `proposal.adoptable` (`:183`). The logic matches exactly today, but it is a second copy that can drift.
- **Fix:** Take `M["proposal"]["adoptable"]` (or call `adoptable_on_the_search`) and combine it with `every_budget`; assert the two agree.

**5. The report builder re-implements the budget checks from `make_admissible`.** · minor · verified yes
- **Location:** `tools/make_final_parameters_report.py:58-90` (`fresh_budgets`, `held_out_budgets`).
- **Issue:** It matches `make_admissible` (`search_all_settings.py:411-432`) on everything that matters: the elevated-rate test inside the stretch (worse background ≤ `MAX_PROBE_PER_MIN`), the no-coordination recording ≤ `MAX_FALSE_POSITIVES_PER_HOUR`, outside-the-stretch on quiet only against the same limit, and the absolute quiet−busy precision swing ≤ `MAX_PRECISION_DROP`. Differences: it drops the `isfinite(f1_quiet/busy)` guard; a missing outside-stretch value fails here where the canonical gate would raise a TypeError; and the fresh seeds have no close-events check (disclosed in the README). Separately, `selection_budgets.json` came from a script that is not in the repo (README L436-438), so its claim to reuse `Evaluator`/`make_admissible` cannot be checked from the repo.
- **Fix:** Split `make_admissible` into `budget_checks(det, summary) -> {check: (value, limit, ok)}` that it `all()`s, call it from the report and from the selection-budget script, and check that script in.

**6. The seconds→frames conversion for the floor now exists in three copies.** · minor · verified yes
- **Location:** `src/bugarach/bench.py:127-129` (`recording_floor`) is the third copy, alongside `tools/detect_with_floors.py:66-68` (`frames_in`) and `tools/measure_rate_stretches.py:163-172`.
- **Issue:** All three match exactly today (`floor((t - lo)/dt + 1e-9)`, `np.unique`, `n_frames = round((hi - lo)/dt)`, the same `stream_trains` with an inclusive upper bound). The README's real-data section puts bench floors and real-window floors side by side, so these two paths must not drift.
- **Fix:** One seconds-based entry point in `bugarach.event_floor` (e.g. `window_floor_sec(trains_sec, lo, hi, dt, key=...)`) called by all three.

## Checked, no reuse issue
- **`recording_floor`** calls `event_floor.window_floor` at ADR-0008's defaults (`bench.py:130`) rather than re-deriving the null, and passes recording-relative frames as `window_floor` requires.
- **`floored_params`** is single-sourced: `bench.run_detector:1459`, `bench_slow.py:438` and `bench_combined.py:408` all call it; `detect_with_floors` imports `FLOORED_SETTING`, and a test asserts it is the same object (`tests/test_bench_floor.py:107`).
- **`under_floor_report`** reads `score.py`'s `dont_care_by_frac` (pooled by `pool_scores`) rather than recounting.
- **`guard_fits_the_context` / `settings_are_valid`:** the LoCo guard/symmetric refusal and the sliding-needs-threshold refusal mirror `loco.py:358-376` and `coact.py:332`; the move that lets the guard cap reach LoCo is tested (`tests/test_bench_floor.py:184-200`).
- **`warm_floors`** only pre-computes through the bench's own `make_*`.
- **`versions_from`** mirrors the older `versions()` with the same reference rows; `cell()` pools through `bench.pool_scores`.
- **Outside my role, noticed in passing:** `versions_from` (`tools/score_cross_stream.py:86-88, 99-100`) picks `chorus_src` if *any* chorus model has a pick, then reads `["picked"]` for *every* model, so a record where only one model was picked would crash on `None.split`.
