# Role 7 — Reinventing the Wheel (round 1, verbatim as returned)

GRANT 7 ok — Read, Grep, Glob, Bash

**Role 7 (reuse auditor), round 1. Artifact:** docs\methods\coordination_pipeline_methods.md (worktree HEAD f6f0c26). Everything was read-only; I modified no files.

**Summary:** call_measure.py does not duplicate a tested equivalent. There is one close relative, assess._clusters, and I found no function that does the gap-split plus distinct-cell core. The methods text matches the code on the gap rule, core choice, width floor and NaN rule. However, two places re-derive something the project already computes canonically, and each produces wrong numbers:
- **F1:** the SCE call stretch that score.py already fixed.
- **F2:** the in-window flag that LoCo and locust already compute.

F3 is a text error in the same area. F4 is the reuse pointer for the revision the text says is under review.

**Finding list** (location · issue · severity · suggested fix · could I verify it against a source)

**F1**
- **Location:** text §"Width and amplitude", step 1 ("or within the call itself if it is longer"); tools/measure_calls.py:54-56; src/bugarach/call_measure.py:151-163.
- **Issue:** measure_calls rebuilds each call's stretch as `[onset_sec, onset_sec + width_sec]` from detections.csv. For binned SCE, `width_sec` is the onset spread inside the bin (`tlast - tfirst`, detectors/sce.py:341), and `onset_sec` is the bin start (sce.py:339). That stretch starts at the bin edge and can end seconds before the events. score.py already documents this as the wrong stretch and fixes it with `EXTENT_FIELD = "extent_sec"` (score.py:281-293; SceStream.extent_sec, sce.py:85-97; Tony's ruling 2026-09-16). measure_calls does not use it, and cannot, because emit.events_from (emit.py:228-253) does not write extent_sec to detections.csv. So for SCE:
  - the centre (onset + spread/2) is not the bin centre;
  - the widened aperture is not "the call itself";
  - late-bin clusters can still be missed.

  call_measure.py's docstring claims this widening fixed the 166-of-834 single-cell SCE calls. That is unverified and doubtful: I checked the logic, not a rerun.
- **Severity:** high. It is a wrong number for one of six detectors, and the text describes the rule as detector-independent.
- **Fix:** have emit carry extent_sec (or `call_start`/`call_end`) into detections.csv. Build measure_calls' window from the same field score.score_stream prefers, rather than from `onset + width`. Then rerun the SCE widths and amplitudes.
- **Verified against source:** yes, by reading the code. I did not rerun the pipeline.

**F2**
- **Location:** text §"Windows" ("LoCo, binned SCE and locust were run on the whole recording, and their calls were assigned to the window they fell in") and §"Rates"; tools/make_before_after_figure.py:80-108, 180-182; detect_folder._run_nested (detect_folder.py:533-555).
- **Issue:** for the whole-recording detectors, the region is assigned by `_tag_region` (loco.py:483-487; cicada.py:422-425). That function matches the **raw period** (`raw_start <= onset < raw_end`), not the analysis window. The same function returns `in_stats_window`, the MATLAB-parity flag (gen_ref_loco.m / gen_ref_cicada.m carry it), which says whether the call is in the window. Nothing downstream reads that flag: emit drops it, and grep finds no consumer in src/ outside detectors/ or in tools/.

  make_before_after_figure counts every call stamped with the period's region_idx, then divides by `w.win_dur`, the analysis window. So for LoCo and locust, the numerator includes calls from the first 2 min of treatment and from baseline before its last 20 min, while the denominator excludes that time. Their before/after rates are inflated relative to the other four detectors. The text's "assigned to the window they fell in" is false for these two.
- **Severity:** high. It biases a reported rate, and the bias differs between detectors.
- **Fix:** carry in_stats_window into detections.csv, or have _run_nested set region_idx=None when the call is outside win_start/win_end. Count only in-window calls in rates(). Then correct the sentence.
- **Verified against source:** yes, by reading the code. I did not count affected calls.

**F3**
- **Location:** text §"Windows", same sentence.
- **Issue:** binned SCE runs in `analysis_mode="regional"` by default (sce.py:123; detect_folder does not override it). That is an independent pass per trimmed window (sce.py:379-397), with calls inside the window by construction. The text groups SCE with the whole-recording detectors. That contradicts its own detector list ("thresholds each analysis window") and the code.
- **Severity:** medium.
- **Fix:** say that LoCo and locust scan the whole recording and tag calls by period, and that binned SCE detects within each window.
- **Verified against source:** yes.

**F4**
- **Location:** text §"Width and amplitude", ⚠ paragraph ("A revision that counts each cell once is under review").
- **Issue:** the project already has a tested, MATLAB-parity participant rule that counts each cell once: assess._clusters (assess.py:303-312) takes each ROI's single onset nearest the cluster centre within ±wm. The planned revision should reuse or mirror it, not re-derive a third variant. Its span (`oo.max() - oo.min()`, assess.py:334) is the same width concept.
- **Severity:** medium, as a reuse pointer for the pending change.
- **Fix:** base the revision on assess._clusters' gathering rule (nearest onset per ROI, tie to the first minimum, as MATLAB does). Cite it in the module docstring.
- **Verified against source:** yes.

**F5**
- **Location:** text §"Width and amplitude", step 1 and the lead-in ("by one rule for every detector"); call_measure.py:13-15 ("Nothing here reads the detector's width").
- **Issue:** the aperture's centre is `onset + width_sec/2` (call_center, call_measure.py:196-204), and its extent is widened to `[onset, onset + width_sec]`. Both use the detector's own width, so where and how widely events are collected depends on each detector's width rule. The text never says how "the call's centre" is defined, and the module docstring's claim is false.
- **Severity:** medium.
- **Fix:** state that the centre is the detector's onset plus half its reported width. Drop or qualify "nothing here reads the detector's width".
- **Verified against source:** yes.

**F6**
- **Location:** text §"Width and amplitude", step 3.
- **Issue:** the core tie-break is not stated. The code (call_measure.py:171-172) breaks ties by more events, then by the group whose mean onset is nearest the centre.
- **Severity:** low.
- **Fix:** add "ties go to the group with more events, then to the one nearest the centre".
- **Verified against source:** yes.

**F7**
- **Location:** text §"Width and amplitude", NaN rule.
- **Issue:** the text says only "a single cell has no amplitude". The code also returns NaN width and NaN amplitude when the aperture holds no events (call_measure.py:166-168). A reader of the width distribution needs to know those calls are excluded.
- **Severity:** low.
- **Fix:** add "a call with no events in the aperture has no width or amplitude".
- **Verified against source:** yes.

**Parts of the text that match the code exactly** (checked, no finding):
- aperture ±1.0 s and gap 0.5 s for the fast stream (DEFAULTS, call_measure.py:62);
- a gap splits only when strictly greater than 0.5 s (`np.diff > gap_sec`, call_measure.py:122);
- the core is the group with the most distinct cells;
- width = last minus first onset of the core;
- amplitude = core_n_roi / max(span, frame interval), with the floor at sl.dt (0.1 s on this dataset);
- NaN when core_n_roi < 2;
- onsets are t50rise (io.py:166-167 sets t50rise = locs);
- the window lengths described (baseline's last 20 min; treatment from +2 min, capped at 20 min) are the producer-supplied windows, and the fallback convention agrees (loco_detect `solution_delay_sec=120`, `baseline_window_max_sec=1200`, `treatment_window_sec=1200`);
- rate+context, CoactDetect and SPIKE-synch run per window (detect_folder._run_flat);
- the rate denominator is folder_analysis_windows' win_dur, reused rather than re-derived.

**Notes, not findings against the artifact:**
- tests/test_call_measure.py's module docstring still describes the superseded amplitude rule ("inversely proportional to the interval between their onsets"). The tests themselves check cells/width.
- call_measure's `peak_coactivity` (distinct cells inside any sliding gap window) shares its name with assess._clusters' `peaks` / peak coactivity (the maximum binned count), which is a different quantity. The methods text does not use it.
- The learned detector also runs per window (_run_learned), and the text does not say so.
- The 15-minute floor survives in code as `meets_floor` (`region_min_sec=900`) but nothing downstream reads it, which is consistent with the text's ⚠ note.

**What I could not verify:** interface2's characterize_coord_window.m. There is no interface2 checkout on this machine and BUGARACH_INTERFACE2 is unset. The module says it was deliberately built from the concept rather than ported, on Tony's instruction of 2026-09-21, so not reusing that code is sanctioned. I am not claiming a parity check.

**Files:**
- src\bugarach\call_measure.py
- tools\measure_calls.py
- tools\make_before_after_figure.py
- src\bugarach\detect_folder.py
- src\bugarach\score.py
- src\bugarach\emit.py
- src\bugarach\detectors\sce.py
- src\bugarach\detectors\loco.py
- src\bugarach\detectors\cicada.py
- src\bugarach\assess.py

---
*Transcription note: personal absolute paths were replaced with placeholders (sapper SAP004); nothing else was altered.*
