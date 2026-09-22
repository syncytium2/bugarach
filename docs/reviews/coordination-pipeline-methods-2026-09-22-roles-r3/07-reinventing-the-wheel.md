# Role 7 — Reinventing the Wheel (round 3, blind pass, verbatim as returned)

GRANT 7 ok — Read, Grep, Glob, Bash

Role 7 (Reinventing the Wheel), round 3 blind pass. Artifact: `docs\methods\coordination_pipeline_methods.md` at ee7bd62. I held no editing tools and edited nothing.

Every code defect in the cover memo that I could test holds up. I found one new code defect, in `measure_calls`. For the other memo defects, the fix already exists in tested production code, and the memo's proposed fixes point at it correctly. The new code in this worktree mostly reuses the canonical helpers.

To check numbers I read the run the methods describe: `<darkroom>/bugarach/2026-09-21-full-cohort-default/detect/` (`detections.csv`, `calls_measured.csv`, `detector_settings.csv`, `run.json`). I also loaded its input folder, `2026-09-17_revised_2v_long_STEPS_AND_PINS_EXCLUDED`, through `folder_analysis_windows`.

## Findings (location · issue · severity · suggested fix · verified)

**1. `tools/measure_calls.py:60` (with `src/bugarach/call_measure.py:70`) — NEW.** `out.append({**row, "center_sec": center, **m.row()})` overwrites the detector's own `n_roi` column. `CallMeasure` has a field with the same name (distinct cells anywhere in the search span). The tool's docstring says "every detections column unchanged", and that is false.
- Evidence, fast binned SCE: `n_roi` has min 3 in `detections.csv` but min 0 in `calls_measured.csv`, and 265 of 1,665 rows are below 3. Anyone reading `calls_measured.csv` gets the search-span count and takes it for the detector's participant count.
- The methods text is not affected: its "185 had a single cell" uses `core_n_roi`, and I reproduced 185.
- Severity: medium (a code defect that corrupts an output table). It belongs on the memo's defect list.
- Fix: rename the field (e.g. `span_n_roi`), or prefix the measured columns. Add a test that every detections column survives unchanged.
- Verified: yes.

**2. `tools/make_before_after_figure.py:96-107` with `src/bugarach/detect_folder.py:541-555` — memo defect 1, CONFIRMED and quantified.** Methods line 448 says "A call counts toward a window when its onset lies inside it."
- In the code, LoCo and locust calls are tagged by `_tag_region` (`detectors/loco.py:484`, `sce.py:352`, `cicada.py:422`) against the raw period (`raw_start <= onset < raw_end`). `_run_nested` then maps that label to the window's `region_idx`, and the figure counts by `region_idx`.
- Fast-stream counts of calls counted in a window whose onset lies outside it:
  - LoCo: 212 of 1,810 (TTX 84, senktide 76, SB222200 26, baseline 18, wash 8)
  - locust: 234 of 6,546 (TTX 124, senktide 61, baseline 24, SB222200 21, wash 4)
  - binned SCE, CoactDetect, SPIKE-synch: 0
- Reuse point: the detectors already compute the right test, `in_stats_window` (`loco.py:602/669`, `sce.py:426`, `cicada.py:492`), using the same half-open `[win_start, win_end)`. `emit.COLUMNS` (`emit.py:125`) drops it. The fix should export that flag, not add a fourth interval test.
- Side note: `_run_nested`'s fallback lookup (`detect_folder.py:543-544`) uses a closed `win_start <= onset <= win_end`, which disagrees with `_tag_region`'s half-open test. It is only reached when labels repeat.
- Severity: high (the methods state a rule the code does not follow).
- Fix: as in the memo. Carry `in_stats_window` into `detections.csv`, or filter on it in `_run_nested`, then regenerate.
- Verified: yes.

**3. `tools/make_before_after_figure.py` / `detectors/rate.py:366-369` — NEW, minor.** rate+context calls are widened by `CHARACTERIZATION_PAD_S = 0.5`, so their onset can sit up to 0.5 s before `win_start`. They still count toward that window through the `region_idx` of the per-window run: 14 fast calls, at −0.3 to −0.5 s. That contradicts "onset lies inside it" (line 448).
- Severity: low (14 calls).
- Fix: in the text, say "a call from a run inside a window counts toward it (rate+context's onset includes its 0.5 s widening)", or filter the calls.
- Verified: yes.

**4. `tools/measure_calls.py:54-59` — memo defect 2, CONFIRMED, and it is a reuse failure.** `measure_calls` works out a call's stretch as `[onset_sec, onset_sec + width_sec]`, which re-implements the rule `score.py` owns.
- Canonical version: `score.EXTENT_FIELD` / `score_stream` (`src/bugarach/score.py:281-322`) prefers `SceStream.extent_sec` (`detectors/sce.py:342-346`) over the width, for exactly this reason. `emit.py` does not export `extent_sec`.
- The copy does not match the reference for binned SCE: the width it uses is the event spread, not the bin. That gives the memo's numbers, both reproduced: 157 of 1,665 fast SCE calls with no events, and 347 with a core under 3 cells.
- Text-side mismatch: Scoring (line 226) says "binned SCE's interval is its bin". The width section (lines 460-461, "within the call") uses a different interval for the same detector without saying so.
- Severity: high for SCE width and amplitude.
- Fix: export `extent_sec` and have `measure_calls` take the call's stretch from the same rule as `score_stream`. Ideally make one shared `call_span()` that both call.
- Verified: yes.

**5. `detectors/cicada.py:175` — memo defect 3, CONFIRMED in code.** The default is `threshold_scope="global"`. The settings file does not override it, so locust ran with one threshold per recording, as Table 4 and line 447 say. The "regional" option exists (`cicada.py:224`).
- I did not recount the memo's 998 → 2,763 locust calls.
- Severity: as the memo says.
- Verified: code yes, counts no.

**6. `src/bugarach/bench.py:523-613` — memo defect 4, CONFIRMED.** `OPERATING_POINTS` still holds the binned points for loco and coact, marked "NOT YET SWITCHED TO SLIDING".
- The run's own `detector_settings.csv` is byte-for-byte the same set of rows as the committed `docs/methods/recorded_data_detector_settings.csv` (sorted diff empty). Citing that file is therefore accurate.
- Verified: yes.

**7. Table 4, LoCo "threshold update step – 15 s".** `thr_step_sec` does nothing in sliding mode. `bench.py:529-531` says so, and `_detect_stream_sliding` (`loco.py:622`) never reads it. Listing it as a value used on the recorded data suggests a knob that had no effect.
- Severity: low.
- Fix: write "– (binned mode only)", or drop the row.
- Verified: yes.

**8. `tools/make_methods_bench_figure.py:48-73` — builds its own planted-event lane instead of `ui.diagnostic.lane_panel`.** This is justified: `lane_panel` (`diagnostic.py:153`) draws one "planted" row, and Figure 1 needs one row per participation level. The cell counts in the labels, `matlab_round(f * n_roi)`, match the generator's `max(1, matlab_round(frac * nR))` (`simulate.py:811`) for every level used (10, 6, 3; distractor 6).
- Severity: none / informational.
- Optional: read the counts from `gt.events[*].n_part` rather than recomputing them.
- Verified: yes.

## Parts that reuse, or match the reference exactly (verified)

- **Before/after windows:** `make_before_after_figure.windows()` calls `detect_folder.folder_analysis_windows` and `_region_index`, not its own copy. `win_dur` is the scored window, so the denominator is right. The only fault is the numerator (finding 2).
- **Search span:** `call_measure` matches the text's steps 1–3. The union of centre ± 1 s with `[onset, onset + width]` is exactly "within 1 s of the centre, or anywhere within the call if longer than 2 s", because the call is contained in centre ± 1 s whenever width ≤ 2 s.
- **Grouping, core and outputs:** events are split when the gap is > 0.5 s. Core ties are broken by distinct cells, then events, then nearness to the centre. Width = last minus first onset in the core. Amplitude = cells / max(width, `sl.dt`), with `dt` = 0.1 s. Amplitude is NaN for one cell; width and amplitude are NaN when the span is empty. `locs` is the t50rise on the folder path.
- **Width numbers in the text (lines 475-476):** all reproduced from `calls_measured.csv`: widths over 10 s for rate+context 25, LoCo 23, CoactDetect 10; widest 64.8 s (rate+context, 37 cells, 1,046 events); 308 zero-width calls; 185 single-cell calls.
- **Scoring text vs `score.py` and `bench.py`:**
  - Interval matching, gap 0 inside the interval, one-to-one, closest pair first, `TOL_SEC = 2.5`.
  - SCE scored on `extent_sec`; rate+context width includes the 0.5 s pad.
  - Precision = hits / (detected − block false alarms) (`BenchResult.n_scored`, `bench.py:1134`).
  - Pooling sums counts (`pool_scores`).
  - 15/21 → F1 0.83.
- **Table 4 against the detector signatures and the settings file:** every value I checked matches.
  - rate+context: merge 3 s, guard 0, additive, "more than one grid point" (`keep = ends - starts > 0`).
  - binned SCE: regional mode, min 3, merge NaN.
  - locust: synchronous frames 1, minimum distance 4, 100 surrogates.
  - SPIKE-synch: `min_n` 3, `isi_adaptive`, cap 0.25.
  - CoactDetect: min 3, `guard_norm` compact.
  - LoCo: context clamped to the raw period (`loco.py:430-436`), as line 183 says.
- **Numbers in the detector and learned-detector text:** z at α = 1e-5 is 4.2649. `learn/train.THRESHOLD_GRID` has 41 values from 1e-4 to 0.9999, matching line 383.
- **Figure 1 tool:** reuses `bench.make_recording`, `BENCH_RECORDING`, `ui.diagnostic.raster_panel`, `ui.app._time_axis_hook` and `make_generator_figures._write`. Nothing is drawn on the raster.
- **`call_measure`:** its re-implementation of interface2's `characterize_coord_window.m` is a sanctioned fresh build (module docstring, Tony 2026-09-21). I found nothing in bugarach that already does call-membership grouping. `assembly.py` and `assess.py` clusters answer a different question.

## Relevant paths

- `tools\measure_calls.py` (line 60)
- `src\bugarach\call_measure.py`
- `src\bugarach\detect_folder.py` (lines 522-557)
- `src\bugarach\emit.py` (lines 125, 208-256)
- `src\bugarach\score.py` (lines 281-322)
- `src\bugarach\detectors\sce.py` (lines 342-354, 426-433)
- `src\bugarach\detectors\loco.py` (lines 430-486, 602-669)
- `src\bugarach\bench.py` (lines 523-613)
- `tools\make_before_after_figure.py`
- `tools\make_methods_bench_figure.py`
- Run checked: `<darkroom>\2026-09-21-full-cohort-default\detect\`

---
*Transcription note: personal absolute paths were replaced with placeholders (sapper SAP004); nothing else was altered.*
