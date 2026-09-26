---
status: open
filed: 2026-09-17
---

# How the detectors use analysis windows does not match the intended design

**Intent (Tony, 2026-09-17):** local detectors run on the whole trace; the analysis regions only split
events into baseline and treatment. Global detectors (one bar from copies of a long stretch) are applied
region by region. What happens outside the analysis windows does not matter for results.

**What `src/bugarach/detect_folder.py` does now** (module docstring, "Two detector families"):

| detector | now | intended |
|---|---|---|
| rate+context, CoactDetect, SPIKE-synch (`FLAT`) | run once per declared window, so their context stops at the window edges | whole trace, events assigned to regions afterwards |
| LoCo | whole recording, but its before/after context is clamped to the region: at an anchor on a region boundary the "before" pool is empty, `_threshold_pool` returns `inf` and `max()` keeps it (`loco.py` ~439-440, 514-518). LoCo cannot call within ~7.5 s of a drug's arrival | whole trace, context not clamped |
| binned SCE | one bar per analysis window | regional, as intended |
| locust | one bar for the whole recording | one bar per region |

Found by the 2026-09-17 murderboard of the plain detector review (round 2, role 6, LoCo measured on slice
20260303_301: bar `inf` for every bin 1193.5-1207.5 s around TTX arrival at 1200 s; 4 of LoCo's 6 misses
among 195 clear stripes sit 0.5-4.7 s after a period boundary). Not fixed for the manuscript: no time.

## Also found in that review, for follow-up (not pipeline)

- **FOUNDATIONS §9 TTX numbers do not reproduce** from `constellation/oxc_ttx_persistence.csv`: FAST median
  0.35 (n=26 defined), SLOW median 1.31 with 61% at or above baseline (17/28). "44%" divides by all 39 rows
  including undefined zero-baseline ones. The CSV holds 39 slices; `20250731_149` is not in the current export
  (withdrawn), and two rows lack a group. `current_export.toml` repeats the same figures.
- **Locust's "measured duration"** is the export's `width` column: half-prominence width for brief events,
  half-rise-to-peak for long events (`PROVENANCE.md`), so on long events a neuron is "on" only while rising.
- **Settings were searched and scored on simulated brief events only**; the same values run on long events.
- `bench.py` docstrings at ~762 and ~963 still say a 1.5 s match gap; `score.TOL_SEC` is 2.5.
- `tools/svgfig.py` time ticks differ from the tested `bugarach.time_axis` in 7 of 29 axes.
- Ask: does Nunemaker, DeFazio et al. 2001 (J Neurophysiol 86:86-93, Moenter lab) already use a chance test
  on coincident firing or episodes in summed firing rate? If so, credit rate+context / CoactDetect / LoCo.

Review records: `<darkroom>/bugarach/archive/2026-09/2026-09-15-detector-review-plain/reviews/`.
