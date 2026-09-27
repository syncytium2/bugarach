> Archived verbatim except machine-local paths, shown as `<darkroom>`, `<worktree>`, `<scratchpad>` and `<repo>` (SAP004).

GRANT 7 ok — Read, Grep, Glob, Bash

# Role 7, Reinventing the Wheel: findings on tools/make_briefing.py and tests/test_make_briefing.py

W = <worktree>. All line numbers refer to that worktree at 86cfffe2. No recording ids are quoted anywhere below.

## Findings

**1. HIGH: the example-caption time is wrong on the delivered page (4 of 9 captions)**
- **Where:** `make_briefing.py:769`, the caption built as `f"{t / 60:.0f}m{t % 60:02.0f}s"`.
- **Issue:** It rounds the minutes instead of flooring them, so the minute is one too high whenever the seconds are at 30 or more. It can also print "60s", and it writes "0m00s" where the house style is "0s".
- **Evidence:** I recomputed from `briefing.json`'s own `onset_sec`. In the built `index.html`, four captions show a minute one too high (fast agree, fast leader-only, slow leader-only, combined leader-only). One of them reads "20m60s".
- **The canonical code exists:** `W\src\bugarach\time_axis.py:74` `label()`. It is a Python port of `_time_axis_hook` (`W\src\bugarach\ui\app.py:75`) and is tested against the JavaScript original in `tests/test_time_axis.py`.
- **Fix:** `from bugarach.time_axis import label` and write `label(round(t))`. Add a test with an onset at 100 s, which must read "1m40s".
- **Verified:** yes.

**2. MEDIUM: budget names use retired vocabulary**
- **Where:** `make_briefing.py:106-109`, `BUDGET_WORDS`, and the page's Terms table.
- **Issue:** This re-implements the budget naming in `W\tools\make_final_parameters_report.py:392` `BUDGET_NAME`, which uses the glossary's names. The copy differs:
  - It says "calls in the dense block with nothing planted (the probe)" and "promiscuity probe".
  - `docs/GLOSSARY.md:366` retired "probe" and "promiscuity probe" on 2026-09-21 in favour of "elevated-rate test".
  - It says "recording with nothing planted" where the glossary says "no-coordination recording".
  - The built page prints "(the probe)" in its over-budget marks.
- **Fix:** Import `BUDGET_NAME` from make_final_parameters_report. Keep only the unit map locally.
- **Verified:** yes.

**3. MEDIUM: an unrecorded budget check disappears, and an unmeasured one would crash the build**
- **Where:** `make_briefing.py:125-126` together with `budget_words` at `:129-132`.
- **Issue:** The budgets themselves are computed by reusing `fresh_budgets` (good). But the handling of the result does not match the reference renderer `_bud` (`make_final_parameters_report.py:401`):
  - `_bud` names every check with `ok is None` as "not recorded". The briefing keeps only `ok is False`, so the close-events check (`crowded`, always `ok=None` on fresh seeds) vanishes without a word. The reference says "not run on the fresh seeds".
  - `fresh_budgets` returns `value=None, ok=False` for `elevated_out_quiet` when a row lacks `elevated_calls_per_hour_outside`. `budget_words` then runs `f"{None:.2f}"` and the build fails with a TypeError. I reproduced this with a minimal row. It is latent: 0 of 624 rows in tonight's files lack the field.
- **Fix:** Use `failed()` (`make_final_parameters_report.py:129`) for the list, and follow `_bud`'s rule: name unrecorded checks and print "not measured" when the value is None.
- **Verified:** yes (crash reproduced; the missing close-events line read from the code).

**4. MEDIUM: the viewer ignores the `&t=` in example links**
- **Where:** `make_briefing.py:671-675` `viewer_href(..., t)`, used for every example figure link.
- **Issue:** The viewer's deep-link contract (`W\docs\site\raster_viewer.html:4455-4467` `readDeepLink`) reads only `slice` and `stream`. Nothing in the viewer reads `t`. The link opens the recording at its start, but it is placed as if it goes to the call.
- **Fix:** Either drop `t`, or add `t` support to the viewer in its own change. Meanwhile the caption should give the time for the reader to navigate to.
- **Verified:** yes (searched the viewer for any `get("t")`; there is none).

**5. LOW-MEDIUM: display names re-typed**
- **Where:** `make_briefing.py:64-66`, `NAME`.
- **Issue:** It duplicates `W\src\bugarach\detectors\__init__.py:39` `DISPLAY_NAMES` key for key and value for value today, including count and count_sliding. The next rename lands in one copy only. `tools/leaderboard.py:71` `shown()` already routes through `display_name`.
- **Fix:** `from bugarach.detectors import display_name` and replace every `NAME.get(x, x)`.
- **Verified:** yes.

**6. LOW: the detector list diverges from the scorer's**
- **Where:** `make_briefing.py:63`, `CODED`.
- **Issue:** It is a hand copy that already differs from the list the scorer writes from: `W\tools\score_bench_candidates.py:171` `CODED` includes count and count_sliding. Two consequences:
  - `ran_on_real` (`:252`) can never pick a count row as the examples' leader, even if the real run has its calls.
  - `model["budgets"]` (`:243`) leaves them out.
- **Fix:** Import it from score_bench_candidates, or state the exclusion on the page.
- **Verified:** yes.

**7. LOW: the agreement tolerance is re-typed**
- **Where:** `make_briefing.py:85`, `AGREE_TOL_SEC = 2.5`.
- **Issue:** The page says this is "the bench's scoring tolerance". That constant is `W\src\bugarach\score.py:60` `TOL_SEC`, but the value is copied rather than imported. The match rule also differs from `score_detections` (`score.py:241`): the briefing counts any span overlap, many-to-many, while the scorer matches one-to-one. The caption's claim that "agree means what a hit means there" is therefore approximate.
- **Fix:** `from bugarach.score import TOL_SEC`, and soften the caption to "the same tolerance".
- **Verified:** yes.

**8. LOW: first-treatment logic re-implemented, with different guards**
- **Where:** `make_briefing.py:272-289`, `recordings()`.
- **Issue:** It re-implements `W\tools\make_group_raster_summary.py:251` `treatment_one`, which decides which group page a recording sits on. The briefing takes the lowest `region_idx` whose `window_kind` is treatment; that kind comes from `detect_with_floors.is_baseline` (`W\tools\detect_with_floors.py:84`, "starts with baseline"). `treatment_one` takes the first label in time order that is not exactly "baseline". A label like "baseline 2" would be a treatment on the pages and not in the briefing, so Table 6 could disagree with Table 5.
- **Current data:** On tonight's windows the two agree on all 66 recordings.
- **Fix:** Call `treatment_one` on the loaded slices when examples load them. Otherwise add a comment stating that the rule is `detect_with_floors`' and why.
- **Verified:** yes (compared empirically).

**9. LOW: hover text re-implemented, and it has no effect in a PNG**
- **Where:** `make_briefing.py:347-352`, the lane build in `render_example`.
- **Issue:** It re-implements `make_group_raster_summary.py:493` `call_line` and `:501` `call_lanes`:
  - The hover string leaves out the baseline floor and has no guard for an empty value (`call_line` prints "—").
  - A PNG has no hover, so the text is invisible anyway.
  - The variant filter in `read_calls` (`:266-269`, own_floor plus unfloored) does match `call_lanes`' default.
- **Fix:** Build the lanes with `call_lanes(night/CALLS)[(slice, stream)]` filtered to `show`, or at least use `call_line`. The lane order (leader, runner, CoactDetect) differs from `call_lanes`' `DETECTORS` order; that is fine if it is deliberate.
- **Verified:** yes.

**10. LOW: the examples may not be drawn from the data the calls came from**
- **Where:** `make_briefing.py:374` and `:878`, the dataset handling.
- **Issue:** The examples draw rasters from `dataset.default()` over calls from `065/review/detect/results.json`, which carries its own `"dataset"` stamp. The two are never compared. The same goes for the Rasters box's "pick the export folder" instruction. `briefing.json` also carries no `"dataset": dataset.stamp()`, which CLAUDE.md requires of a result.
- **Canonical code:** `W\tools\check_scored_dataset.py:58` `scored_on` and `:73` `classify`; `W\src\bugarach\dataset.py:458` `stamp()`.
- **Current data:** The stamp's name matches the current default today. Its role field says a different role name, but the folder name is equal.
- **Fix:** Compare `scored_on(results.json)` with `current_name()` and refuse or flag a mismatch. Add a `dataset` stamp to `briefing.json`.
- **Verified:** yes.

**11. LOW: PNGs rendered at a lower scale than the reference default**
- **Where:** `make_briefing.py:366`, `_render_png(tmp, png, scale=2)`.
- **Issue:** The reference `W\tools\make_diagnostic.py:512` defaults to 3, and its docstring records that 2 goes soft (Tony, 2026-08-15). Mitigations: several other tools also use 2, and the example windows are short (90-240 s).
- **Fix:** Use the default of 3, or make it a `--scale` option as `make_real_detection_figure` and `make_group_raster_summary` do.
- **Verified:** yes.

**12. LOW: page styling hand-rolled**
- **Where:** `make_briefing.py:532-565`, `CSS`.
- **Issue:** The house stylesheet `W\docs\learned\report.css` (used by `md_to_page.py`, `build_site.py`, `build_assembly_report.py`) already has light and dark themes and the same `data-theme` switch, but under different variable names (`--ink` / `--paper` / `--rule` against `--fg` / `--bg` / `--line`). `tools/leaderboard.py` also hand-rolls, so this is not unprecedented.
- **Fix:** Inline `report.css` and add only the briefing-specific rules, renaming Figure 1's SVG variables to match.
- **Verified:** yes.

**13. LOW: fixed EDT offset (no canonical helper exists, so this is not reuse)**
- **Where:** `make_briefing.py:79` (`EDT`) and `:96-102` (`when_edt`).
- **Issue:** The offset is fixed at UTC−4, so every timestamp is labelled "EDT" and is an hour off after daylight time ends on 2026-11-01. I found no repo helper for the house clock.
- **Fix:** `zoneinfo.ZoneInfo("America/New_York")` with `%Z`. That also removes the Windows/POSIX `strftime` branch.
- **Verified:** yes (grep found no helper).

**14. LOW: group-page filenames parsed by hand**
- **Where:** `make_briefing.py:797`, `Path(p).stem.split("_", 2)`.
- **Issue:** It reverse-parses the naming at `make_group_raster_summary.py:873` (`{group}_{treatment without spaces}_{stream}`). A treatment with a space ("high K+") shows as "highK+" in Table 5 while Table 6 shows "high K+". No page exists for it today (the default treatments are TTX and senktide), so this is latent.
- **Fix:** Share a page-name helper, or parse with `rsplit("_", 1)` and map the treatment back through the known labels.
- **Verified:** yes.

## What is reused correctly (checked, no finding)
- **Group order:** `bugarach.groups.group_key` (`groups.py:20`), used for recordings and pages.
- **Budget computation:** `make_final_parameters_report.fresh_budgets`, with the same own-or-CoactDetect limit choice as the reference's `build`. Every detector the briefing can meet has keys in all three bench budget dicts.
- **Darkroom:** `bugarach.paths.darkroom` and `unresolved_message`.
- **Raster and lanes:** `ui.diagnostic.lane_panel` and `raster_panel` (both carry `_time_axis_hook`), `make_group_raster_summary.LANE_NAMES` and `lane_color`, and `make_diagnostic._render_png`.
- **Combined stream:** built exactly as `detect_with_floors.py:188-189` does.
- **Bench modules:** from `score_bench_candidates.BENCHES`.
- **Ruling-5 flag:** reads the `unbracketed` flag the scorer writes as `bracketed is not True` (`score_bench_candidates.py:259`), consistent with the reference's strict reading across 66 proposals.
- **Leaderboard:** `tools/leaderboard.py` reads a different source (per-fold runs), so there is nothing to reuse beyond display names.
- **Figure 1:** a hand-drawn SVG is justified. matplotlib is not in `pyproject.toml`, and I found no ΔF1 interval-plot helper in the repo.

## Test coverage
`tests/test_make_briefing.py` never runs the examples path, caption times or `ran_on_real` (it builds with `--no-examples`). That is how finding 1 shipped. A test of the caption formatter alone would have caught it.

Scratch: none written. Nothing modified.
