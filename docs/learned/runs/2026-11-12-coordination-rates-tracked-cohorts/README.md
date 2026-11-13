# Coordination rates and first calls on the tracked cohorts, fast and slow

> **Working material, not murderboarded.** Dataset: `tracked_cohorts`, the default since
> 2026-11-12 (12 recordings: 5 DI, 7 MALE; threshold 4 x sigma_est). Baseline analysis windows
> only. Fast and slow only: the export carries no combined stream, and bugarach does not build
> one (ADR-0023).

## Coordination rates (`coordination_rates.json`)

`tools/measure_coordination_rates.py --streams fast slow`. The statistic counts onsets in a
sliding window and does not define or merge events. At the 1 s window, fixed-size model:

| stream | per-ROI rate, 25th and 75th percentile over recordings | participants per shared moment | shared moments per minute | coordinated share of an ROI's rate |
|---|---|---|---|---|
| fast | 0.0079 and 0.0203 Hz | 11.9 ROIs | 0.49 | 13 % |
| slow | 0.0135 and 0.0254 Hz | 28.6 ROIs | 0.29 | 23 % |

The estimator passed its calibration on each bench's simulated recordings (48 recordings per
stream); there it reads the coordinated share 16 % low on fast and 19 % low on slow.

## Calls at the shipped settings and at a 0.5 s window

`bugarach detect` on the same folder, twice: the shipped operating points, and the settings the
close-events search picked on simulated recordings (CoactDetect: 0.5 s sliding window, no merge
gap; LoCo: 0.5 s bins, 0.5 s merge gap; binned SCE: 2 s bins, no merge gap). Outputs and the
raster pages with both sets of calls in lanes are in the darkroom,
`bugarach/2026-11-12-tracked-cohorts-calls-shipped-and-narrow/`.

| stream | detector | shipped calls in baseline | of those, holding 2 or more narrow calls | narrow calls in baseline | narrow calls under 2 s after the previous one |
|---|---|---|---|---|---|
| fast | CoactDetect | 194 | 32 (16 %) | 651 | 58 (9 %) |
| fast | LoCo | 298 | 12 (4 %) | 535 | 22 (4 %) |
| fast | binned SCE | 144 | 38 (26 %) | 382 | 0 |
| slow | CoactDetect | 302 | 52 (17 %) | 517 | 84 (16 %) |
| slow | LoCo | 320 | 9 (3 %) | 405 | 11 (3 %) |
| slow | binned SCE | 245 | 46 (19 %) | 454 | 0 |

## What this does not show

- Whether a narrow call is a real coordinated event. Nobody has looked at the pages yet, and
  the narrow settings were never tuned or scored on real recordings.
- Most of the extra narrow calls fall where the shipped setting made no call at all. That is
  a change in sensitivity as well as in separation, and the two are not pulled apart here.
- The shipped run uses the fast operating points on both streams, as `bugarach detect` does
  without a settings file.
