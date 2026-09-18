---
status: open
filed: 2026-09-18
---

# `bugarach detect` refuses settings an every-knob search chooses

**Found** by WSMIP064 on 2026-09-18, merging `main` into `tune-bench-comparison` before goal 2's
fair-comparison run.

## What

`detect_folder.load_settings` reads a settings CSV and refuses any parameter that
`bench.OPERATING_POINTS` does not already ship for that detector (*"'coact' has no parameter
'detection_mode'. It takes alpha, context_win_sec, int_win_sec, n_surrogates"*). That check exists
to catch a typo. But `bench.FULL_GRIDS` now searches every knob a detector accepts — `detection_mode`,
`min_rois`, `guard_norm`, the peak settings — so a setting chosen by goal 1's search or by goal 2's
per-fold search writes parameters the loader then refuses. Such a setting cannot be applied with
`bugarach detect`.

The check is keyed on the wrong list. What a detector *takes* is its signature; what it *ships* is
`OPERATING_POINTS`, and the gap between them is exactly what an every-knob search explores.

## Where it bites

- **Goal 1 landing** (`HANDOFF-coded-detectors.md` §3 step 4): any shipped value for a knob that is
  not in today's `OPERATING_POINTS` entry. Adding it to the entry fixes the loader for that knob,
  which may be why it has not surfaced.
- **Goal 2's chosen settings** (`chosen/<selection>/outer<h>/<detector>/detector_settings.csv`):
  written correctly, unreadable by `bugarach detect`. The run itself never reads them back.
  `test_a_chosen_settings_file_round_trips_what_was_chosen` is marked `xfail(strict=True)` on
  `tune-bench-comparison` and points here, so fixing this turns that test red until the mark comes off.

## The likely fix

Accept a key the detector's signature takes (`inspect.signature`, as
`search_all_settings.shipped_value` already does), and coerce it by the signature default's type
when the shipped point has no value to coerce by. Keep refusing anything the signature does not take:
that is still the typo check.

## Closes when

`load_settings` accepts every parameter `bench.FULL_GRIDS` can choose, and the xfail mark is removed.
