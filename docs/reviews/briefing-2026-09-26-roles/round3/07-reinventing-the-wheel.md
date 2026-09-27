> Archived verbatim, except that the worktree's absolute path is replaced by `<worktree>` (SAP004). No
> recording ids appear.

GRANT 7 ok — Read, Grep, Glob, Bash

Role 7, Reinventing the Wheel. This was the blind pass: I did not open docs/reviews/briefing_2026-09-26-roles/ or the git history of either file. W = <worktree>.

**What I checked:** all 1695 lines of W\tools\make_briefing.py and the tests in W\tests\test_make_briefing.py, compared against the canonical code for each piece. I also checked behaviour on the night's own files under <darkroom>/bugarach/2026-09-26-full-panel/, reading them only and printing no recording ids. That covered the candidates.json bracketing records, windows.csv, calls.csv and the already-built briefing/briefing.json. I also compared the hand-rolled Spearman against scipy.stats.spearmanr on 2000 random inputs with ties. I wrote no files; the scratch folder <scratchpad>/mb3 is empty.

## Findings
Columns: location · issue · severity · fix, with the canonical path:line · verified against a source

**1. `limit_marks`, make_briefing.py:238-246, which feeds `flagged()` :491, `glance()` "top unflagged" :516-517, the headline and the choice of leader**
- **Issue:** it re-derives whether a setting is adoptable from `unbracketed_axes`, and treats every axis with `reason == "limit"` as a NOTE, which never counts as a flag. The canonical rule says the opposite:
  - W\tools\search_all_settings.py:434-436 says any of cap, limit or edge "makes the candidate not adoptable".
  - W\tools\score_bench_candidates.py:139-144, `adoptable_on_the_search`, requires `bracketed is True`.
  - W\tools\make_final_parameters_report.py:209-233 keeps both readings: strict, and `if_limit_counts`.
  - The briefing silently takes the loose reading, and it ignores the `adoptable` and `unbracketed` fields the scorer already wrote into the proposal. The `prop.get("unbracketed")` fallback at :256 never fires once the NOTE is in `out`.
  - No ADR says k_offset at 0 is fine "by design": a grep of docs/adr for k_offset, "by design" and only_at_limits finds nothing.
- **Effect on the built page:** the fast stream's "top unflagged row" is count (binned) · proposal. Its scorer record says `adoptable: False`, `unbracketed: True`, `bracketed: False`.
  - The slow stream's top unflagged row is count (sliding) at its starting point, which also has `bracketed: False`.
  - The combined stream's count_sliding proposal, also `adoptable: False`, is unflagged.
  - A row that is not adoptable can therefore head Table 1 and be chosen as the examples' leader.
- **Minor:** the NOTE text hard-codes "could not go lower" even when `side == "high"`.
- **Severity:** High.
- **Fix:** read the scorer's own verdict, `meta["detectors"][det]["proposal"]["adoptable"]` / `["bracketing"]["bracketed"]`, or call `score_bench_candidates.adoptable_on_the_search` (:139). If the loose reading is wanted, show both readings the way make_final_parameters_report.py:228-233 does, and get it ruled in an ADR first.
- **Verified:** yes, against the code and the night's candidates.json and briefing.json.

**2. The context-window notes in `limit_marks`, make_briefing.py:250-253**
- **Issue:** the search records `reason = "grid_floor"` / `"grid_ceiling"` (search_all_settings.py:452-453, with `CONTEXT_SETTINGS` at :184 and `CONTEXT_MIN_SEC` at :185). The briefing ignores the recorded reason and re-guesses it from the setting name plus the literals 20.0 and 120.0.
- It gives the right answer on tonight's data, but it will drift if the grid or the ceiling changes.
- **Severity:** Low.
- **Fix:** branch on `v["reason"]`, and import `CONTEXT_MIN_SEC` / `CONTEXT_SETTINGS` from search_all_settings.py:184-185.
- **Verified:** yes.

**3. `spearman` / `_ranks`, make_briefing.py:426-447**
- **Issue:** a hand-rolled average-rank Spearman. scipy is a core dependency (W\pyproject.toml:21), and the repo already ranks with `scipy.stats.rankdata` in W\src\bugarach\surrogate_stats.py:296-306.
- **Parity:** it matches `scipy.stats.spearmanr` to within 2.2e-16 on 2000 random tie-heavy inputs.
- **Guards:** a constant input gives None where scipy gives NaN, which is equivalent. With n < 3 it returns None where scipy returns ±1; that is stricter and defensible.
- The test at :191-193 covers only inputs without ties.
- **Severity:** Low.
- **Fix:** `scipy.stats.spearmanr(a, b).statistic`, keeping the n < 3 and NaN-to-None guard, and delete `_ranks`.
- **Verified:** yes, run.

**4. `_span` / `_near` / `nearest_gap` / `classify`, make_briefing.py:631-665 and :691-697**
- **Issue:** these re-implement the span-and-gap arithmetic in W\src\bugarach\score.py:211-238 (`_spans`, `_gap`).
  - The gap formula matches, and so does the `<=` tolerance test (score.py:297).
  - Widths match exactly: `_num` treats non-finite or negative widths as 0, the same as score.py:223-224.
  - Non-finite onsets are not dropped as score.py:226-227 drops them; none appear in tonight's calls.csv.
- **Different rule:** the matching itself is new. It is span-to-span and many-to-one, whereas both the bench (score.py:7-12) and the repo's only call-to-call matcher, `match_share` (W\tools\measure_chorus_context_span.py:191-206, tested in tests/test_measure_chorus_context_span.py:36), match greedily, closest first, one to one.
  - The page says "span to span, so one call can agree with several", but it also calls TOL_SEC "the bench's scoring tolerance". Its agree / only-one-side counts are not comparable to either canonical rule.
  - `_near` and `nearest_gap` are also two separate copies of one gap expression.
- **Severity:** Medium.
- **Fix:** either generalise `match_share` to spans, using score.py's `_spans`/`_gap`, and reuse it, or keep the rule and name it plainly as not the bench's. Either way, have `_near` and `nearest_gap` share one `_gap` helper.
- **Verified:** yes.

**5. `read_calls`, make_briefing.py:583-592**
- **Issue:** it duplicates the variant filter of `make_group_raster_summary.call_lanes` (W\tools\make_group_raster_summary.py:501-520).
  - It hard-codes the variant `own_floor`, whereas `call_lanes` takes it as a parameter (`--calls-variant`, :812).
  - If the review pages were built with another variant, the page's claim that it counts "the ones the review pages draw" is false.
- The filter logic matches (own_floor or unfloored), and the stream is normalised the same way.
- **Severity:** Low.
- **Fix:** take the variant from one shared constant, or from a `--calls-variant` flag passed through. `call_lanes` itself returns arrays without the row fields the briefing needs, so it cannot be called directly.
- **Verified:** yes.

**6. `recordings()` first treatment, make_briefing.py:611-628**
- **Issue:** this is a third copy of the "first treatment" rule.
  - Canonical copies: `make_group_raster_summary.treatment_one` (:251-257) sorts the slice's regions by start and takes the first name that is not "baseline"; `make_detect_floors_figure.load` (:40-50) takes the lowest `region_idx` among treatment windows.
  - The briefing takes the earliest `win_start` among treatment windows, and the docstring wrongly claims it is "the rule the review pages' treatment_one uses".
  - Known divergences:
    - windows.csv drops windows with hi <= lo (W\tools\detect_with_floors.py:205-206).
    - It classifies labels with `startswith("baseline")` (:84-85), where `treatment_one` requires an exact match.
- **Measured on tonight's data:** 0 of 66 recordings disagree between the win_start and region_idx rules, and every first treatment is TTX or senktide, matching the page names. So the defect is latent.
- **Severity:** Low.
- **Fix:** reuse the make_detect_floors_figure rule, or better, factor one `first_treatment(windows_rows)` next to `treatment_one` and call it from all three. At least correct the docstring.
- **Verified:** yes, measured.

**7. Parsing the raster page filenames, make_briefing.py:1494-1499**
- **Issue:** it re-parses the stem format `{group}_{treatment.replace(' ', '')}_{stream}` that make_group_raster_summary.py:873 writes. Spaces are gone after the round trip, so "high K+" would show as "highK+" and would not match the recordings table's labels.
- **Severity:** Low.
- **Fix:** factor a `page_stem(group, treatment, stream)` in make_group_raster_summary and build the lookup from it instead of parsing.
- **Verified:** yes.

**8. `_setting_value` / `EXTRA_PLAIN` / `EXTRA_UNIT`, make_briefing.py:130-131 and :173-181**
- **Issue:** it forks the final-parameters report's canonical PLAIN/UNIT maps (make_final_parameters_report.py:412-433) locally for `k_offset` and `bin_sec`, so the two reports can drift apart. The local branch also prints no unit for a value of 1 in seconds: `"s".rstrip("s")` is empty.
- **Severity:** Low.
- **Fix:** add `k_offset` and `bin_sec` to PLAIN/UNIT in make_final_parameters_report.py and drop the fork; `_vu` (:443) then handles the units.
- **Verified:** yes.

**9. The viewer box's promise of detections.csv, make_briefing.py:1239-1254 and :1664**
- **Issue:** the page tells the reader to open "the detections.csv beside this page", but the builder never writes that file; it only checks whether it exists. The canonical producer is `detect_with_floors.write_detections(run, out)` (W\tools\detect_with_floors.py:372-407).
  - One is present in the built folder now, from a step outside this tool.
  - It is also a file derived from real recordings; that is outside my role, so I only note it.
- **Severity:** Low.
- **Fix:** call `write_detections(night / "065/review/detect", out=a.out)` inside the build, or state where the file comes from.
- **Verified:** yes.

**10. Figure 1, drawn by hand as SVG, make_briefing.py:869-973**
- **Issue:** a new SVG writer. The repo already has one that is themed with CSS custom properties: the `Svg` class in W\tools\make_replicate_report.py:341, plus another at W\tools\build_surrogate_report.py:690. Neither is in a shared module.
- The docstring's claim that matplotlib is not a declared dependency is true (pyproject.toml:19-34), although 24 tools import it.
- **Severity:** Low / optional.
- **Fix:** optionally lift make_replicate_report's `Svg` class into a shared module and use it here.
- **Verified:** yes.

**11. CSS :976-1027, `house_time` :147-157, `n_of` :160**
- **Issue:** none of these has a canonical copy. Every page builder carries its own CSS (build_site.py, make_replicate_report.py:990, and others), and no house-clock or plural-count helper exists in src or tools. So this is not a reuse violation.
- The "house clock", America/New_York, is a new convention defined only here.
- **Severity:** Info.
- **Fix:** if the house clock is meant to be a rule, put it in `bugarach.time_axis` beside `label`.
- **Verified:** yes, by grep.

## Reuse done right (checked, no finding)
- Budgets come through the final-parameters report's own functions (`fresh_budgets` and `failed`, make_final_parameters_report.py:58 and :129). Their limit owner is CoactDetect for learned models, the same as that report's :244.
- Other shared code is called rather than copied:
  - detector names: `display_name`
  - group order: `group_key` and `in_group_order`
  - tolerance: `TOL_SEC`
  - caption times: `time_axis.label`
  - lane colours: `lane_color`
  - drawing: `lane_panel`, `raster_panel` and `_render_png`
  - reading the stamp: `check_scored_dataset.scored_on`
- The stamp check compares against `dataset.current_name`, and it is stricter than `classify` at check_scored_dataset.py:73-86: it requires kind == "dataset".
- The combined stream is built with the repo's usual has_sources / stream_of pattern. Settling the slice (`with_folder_windows`) changes only the regions, so the raw slice's rasters line up with the calls.
- The link format `viewer.html#slice=…&stream=…` matches `readDeepLink` and the `hashchange` handler in W\docs\site\raster_viewer.html:4455-4491. The viewer is copied byte for byte, as build_site.py:838 describes.
- `darkroom()` resolves `<darkroom>/bugarach`, so the default night path is right.
- The seed counts from `seeds_by_bench` match `seeds_for`, which builds a contiguous range (score_bench_candidates.py:67 and :347).
