GRANT 7 ok — Read, Grep, Glob, Bash

Role 7 (Reinventing the Wheel): blind review of `<worktree>/tools/make_briefing.py` and `<worktree>/tests/test_make_briefing.py`, where `<worktree>` is the briefing-page worktree. I did not open `docs/reviews/briefing_2026-09-26-roles/` or the git history of either file. I edited nothing and wrote no scratch files; every probe ran as an inline read-only Python call.

**Summary:** Most of the tool already calls the tested code. I found 3 medium and 6 low findings where it re-implements something with a canonical version, or diverges from one.

**Calls existing code as it should (checked, no finding):**
- `display_name` (it matches `LANE_NAMES` for locust)
- `GROUP_ORDER` / `group_key`
- `TOL_SEC`
- `time_axis.label`, which is used correctly: `round()` then the JavaScript-faithful label, and the test pins 7m59s and 20m
- the budget functions `fresh_budgets`, `failed` and `BUDGET_NAME` from `make_final_parameters_report`
- `BENCHES`
- `dataset.default()` and `dataset.stamp()`, which bring the confirmation gate and the contamination stop with them
- `ui.diagnostic.lane_panel` and `raster_panel`, `make_diagnostic._render_png`, `lane_color("coact")`
- `bugarach.combined` (`has_sources` / `stream_of`), with the same guard as `make_group_raster_summary.measure`
- `PARTICIPANTS_RULE` (it is already formatted, so the page reads "1 s" and not a template)

## Findings

**F1: Setting names and units are a second, divergent copy of the report's table.**
- **Location:** `tools/make_briefing.py:119-125` (`PARAM`) and `:165-172` (`_param_value`), used by `limit_marks`.
- **Issue:** `tools/make_final_parameters_report.py` already has `UNIT` (:412), `PLAIN` (:421), `_ordinal` (:436), `_v` (:373) and `_vu` (:443), and the briefing already imports from that module. The copy does not match it. Side by side (the briefing's output first, the report's second):
  - `threshold_pctile=92`: "at the 92th percentile" against "92nd percentile". The briefing always writes "th", so values ending in 1, 2 or 3 come out wrong.
  - `n_synchronous_frames=3`: "3 frames" against "3 frames (0.3 s at 0.1 s per frame)". The house rule wants the conversion.
  - `dt` / `alpha` at 1e-4: "0.0001" against "1e-4".
  - `merge_gap_sec=NaN`: "none" against "none (no merge)".
  - `int_win_sec`: "integration window" against "co-activity window". `dt`: "SPIKE-synch bin dt" against "bin width". `alpha`: "alpha" against "significance cutoff". `C_min`: the raw key against "minimum coincidence".
  - Keys the briefing lacks, and would print raw: `rate_win`, `tau_max`, `max_gap`, `excess_threshold_hz`, `sce_percentile`, `C_threshold`.
  - The two reports built from the same night will therefore name the same setting differently.
- **Severity:** Medium. The built page is not wrong today: its one percentile, 99.9922, is correctly "th". The divergence is latent, but it is certain to show on the next proposal whose value ends in 1, 2 or 3.
- **Fix:** `from make_final_parameters_report import PLAIN, _vu`, and write each setting as `f"{PLAIN.get(k, k)} {_vu(k, v)}"`. Keep only `k_offset` and `bin_sec` as local additions, or better, add them to `PLAIN`/`UNIT` at `make_final_parameters_report.py:412-431`. Update the test at `tests/test_make_briefing.py:148-151`: it pins "99.9922th", which is the diverging `:g` format; `_vu` gives "99.9921875th".
- **Verified:** Yes. I ran both functions on the same inputs.

**F2: The scored-dataset check is weaker than `check_scored_dataset`.**
- **Location:** `tools/make_briefing.py:610-614`.
- **Issue:** It reads `res["dataset"]["name"]` and refuses only when a name is present and differs. Three cases slip through: `results.json` missing (`_load(...) or {}`), a results file with no stamp, or one that records its data under `folder`/`store`. In all three the examples are drawn from `calls.csv` onto the default dataset with no check at all. The canonical reader, `tools/check_scored_dataset.py:58` (`scored_on`) with `classify` at :73, recognises all of those forms and classes a file with no stamp as "UNSTAMPED - cannot be checked", never as a pass.
- **Severity:** Medium. This is a guard clause that fails open.
- **Fix:** Import `scored_on` from `check_scored_dataset`. Refuse, or print a visible "cannot be checked" line on the page, whenever the kind is not `"dataset"` or the name is not `dataset.current_name("default")`. Also refuse when `RESULTS` is missing but `CALLS` exists.
- **Verified:** Yes, by reading the code. The night's own `results.json` is stamped, so tonight's page is not affected.

**F3: Which setting ran on the real recordings is re-derived instead of read from the run's record.**
- **Location:** `tools/make_briefing.py:452-464` (`ran_on_real`).
- **Issue:** The function infers the setting from the fresh-seed leaderboard: the proposal if the board has one, otherwise shipped, and any learned pick. `tools/detect_with_floors.py:446-457` records exactly this in `results.json["chosen"][stream]` (`detectors[det].which` plus `params`, and `chorus[family]` = the picked file). `examples()` already reads that record for CoactDetect's label (:621, :625) but not for the leader. The inference compares only the word "proposal", never the parameters. `detect_with_floors` picks from its own `--candidates` file, so the two can name different proposals, or different picks, whenever those files differ.
- **Severity:** Medium. It agrees tonight: I compared every coded and learned row on all three streams and found no mismatch.
- **Fix:** Take `chosen` from `results.json`. A coded row ran if `chosen[s]["detectors"][fam]["which"] == setting`, and ideally its `params` equal the board row's proposal params. A learned row ran if `chosen[s]["chorus"][fam]` equals the pick plus ".json".
- **Verified:** Yes. I checked the agreement tonight; the divergence is shown from the code.

**F4: The participants rule comes from the current code, not from the run that counted.**
- **Location:** `tools/make_briefing.py:1218-1223` (`_participants_rule`).
- **Issue:** It imports `detect_with_floors.PARTICIPANTS_RULE`. The night's `results.json` records `participants_rule` and `participant_pad_sec` as run. The pad width is an open question for Tony (ADR-0010 open point 3), so once the constant changes, a rebuilt page would describe a rule the counts were not made under. The bare-`except` fallback wording, "ROIs with an onset near the call", is a third version of the rule.
- **Severity:** Low.
- **Fix:** Use `res.get("participants_rule")`, falling back to the constant. Source of the record: `tools/detect_with_floors.py:495`.
- **Verified:** Yes. The key is present in the night's `results.json`.

**F5: The group columns of the examples table are case-sensitive; the house order is not.**
- **Location:** `tools/make_briefing.py:660-662`.
- **Issue:** `[g for g in GROUP_ORDER if (s, g) in hours]` and `c["group"] == g` are exact matches. `bugarach.groups.group_key` (`src/bugarach/groups.py:19-27`) is case-insensitive because "exports have spelled MALE both ways", and it keeps unknown labels. A "Male" recording, or one outside the four groups, would be counted in "all groups" but dropped from its column, so the columns would not add up to the total.
- **Severity:** Low. Latent: this night's groups are all upper-case.
- **Fix:** `groups = in_group_order(g for (st, g) in hours if st == s)` (`src/bugarach/groups.py:30`), and count by that same key.
- **Verified:** Yes. I checked the group values in `windows.csv` and `calls.csv`.

**F6: The first treatment uses a different rule from the review pages it links.**
- **Location:** `tools/make_briefing.py:495-513` (`recordings`).
- **Issue:** Table 6 groups recordings by the lowest treatment `region_idx` in `windows.csv`, whose baseline test is `detect_with_floors.is_baseline`, a `startswith("baseline")` match (:84). The pages linked in Table 5 are grouped by `make_group_raster_summary.treatment_one` (:251): the first non-"baseline" region in time order, with an exact-match baseline test. A region labelled like "baseline 2", or an index order that differs from time order, would put a recording under different headings in Tables 5 and 6.
- **Severity:** Low. It agrees tonight: indices and times order the same way in all 66 recordings, and the 8 group × treatment keys match the page stems.
- **Fix:** Order by `win_start`, not `region_idx`, and say in the docstring that the page groups use `treatment_one`. Alternatively, derive the grouping from the page stems.
- **Verified:** Yes. I checked both on the night's files.

**F7: The call readers and the overlap test drop the canonical guards.**
- **Location:** `tools/make_briefing.py:471-476` (`read_calls`), `:516-519` (`_overlaps`), `:542-547` (`_inside`).
- **Issue:**
  - `read_calls` re-implements the variant filter of `make_group_raster_summary.call_lanes` (:501-527), which it has to, because it needs `window_kind`, `region_idx`, `group` and `participants`. But it skips that function's stream normalisation, `str(r["stream"]).strip().lower()` (:520).
  - `_overlaps` builds spans with `float(width or 0)`. `bugarach.score._spans` (`src/bugarach/score.py:211-233`) sets non-finite and negative widths to 0 and drops non-finite onsets. A NaN width here makes every comparison false, so the call silently becomes "only the leader's".
- **Severity:** Low. Latent: the night's `calls.csv` has no non-finite values, negative widths or mixed-case streams.
- **Fix:** Normalise the stream as `call_lanes` does. Clamp widths as `_spans` does, `w = w if isfinite(w) and w > 0 else 0`, or build the spans through `score._spans`.
- **Verified:** Yes. I scanned the night's `calls.csv`.

**F8: The page's stylesheet is a new palette, not the house one.**
- **Location:** `tools/make_briefing.py:811-847` (`CSS`), and the SVG variables at :734-739.
- **Issue:** `docs/learned/report.css`, loaded by `tools/md_to_page.py:166` and `tools/build_assembly_report.py:58`, is the house look for pages meant to be read, including the light/dark `data-theme` handling. The briefing re-implements that theme machinery with different variable names (`--fg`/`--bg`/`--line` against `--ink`/`--paper`/`--rule`) and different colours.
- **Severity:** Low. This is a judgement call: a dashboard may justify its own look, but the theme mechanism is duplicated.
- **Fix:** Inline `report.css` the way `md_to_page` does, keep only the page-specific rules (`td.n`, `.bad`/`.warn`, `img.ex`), and rename the SVG `var()` references to the house names.
- **Verified:** Yes, by reading both files.

**F9: Constants hard-typed in the prose instead of read from their owners.**
- **Location:** `tools/make_briefing.py:1049` ("2,000 draws"), `:1101`, and `:600`.
- **Issue:**
  - The bootstrap count is `score_bench_candidates.BOOTSTRAP` (`tools/score_bench_candidates.py:59`), and the module is already imported for `BENCHES`.
  - The example lanes colour the leader and runner-up with fixed Okabe–Ito colours, `LEADER_COLOR`/`RUNNER_COLOR`, rather than `make_group_raster_summary.lane_color(det)` (:431). So on the review pages the reader clicks through to, the same detector's lane has a different colour. That may be deliberate, since two chorus-family leaders could share a ramp colour, but the page does not say so.
- **Severity:** Low.
- **Fix:** Write `f"{BOOTSTRAP:,} draws"`. Either use `lane_color` for the leader and runner-up, or state on the page why their colours differ.
- **Verified:** Yes, by reading the code.

## Out of my role, noted only (for roles 2 and 10)
- `house_time` (:139) is new, and I found nothing in `src` or `tools` for it to reuse. But the Terms table (:1273) hard-codes "EDT, UTC − 4 h" while `%Z` will print EST after early November.
- `has_results` (:1317) checks for a `detections.csv` beside the page that nothing in this tool writes.

## Files
- `<worktree>/tools/make_briefing.py`
- `<worktree>/tests/test_make_briefing.py`
- Canonical implementations referred to:
  - `<worktree>/tools/make_final_parameters_report.py`
  - `<worktree>/tools/check_scored_dataset.py`
  - `<worktree>/tools/detect_with_floors.py`
  - `<worktree>/tools/make_group_raster_summary.py`
  - `<worktree>/src/bugarach/score.py`
  - `<worktree>/src/bugarach/groups.py`
  - `<worktree>/tools/score_bench_candidates.py`
  - `<worktree>/tools/search_all_settings.py` (:429-477, the bracketing vocabulary; `limit_marks` handles all five reasons correctly)
  - `<worktree>/docs/learned/report.css`
  - `<worktree>/tools/md_to_page.py`
- Night data read, not modified: `<darkroom>/bugarach/2026-09-26-full-panel/065/review/detect/` and `.../briefing/index.html`.
