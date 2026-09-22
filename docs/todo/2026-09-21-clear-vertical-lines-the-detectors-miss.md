---
status: open
filed: 2026-09-21
---

# Clear vertical lines in the raster that CoactDetect and chorus_gain_norm miss

## What Tony saw

On the DI · TTX · fast raster from 2026-09-21
(`<darkroom>/bugarach/2026-09-21-full-cohort-default/rasters/DI_TTX_fast.png`), Tony flagged
two misses: *"chorus misses a clear vertical line in _301 and both miss a clear vertical line in
_309 (both around 20 minutes)"*. He said to note them for the next run rather than chase them
now.

The run: CoactDetect at the weekend's sliding settings (`weekend_settings.csv` in that folder),
and chorus_gain_norm fit fold 0, training seed 2 from the replicate run (the median of 20 fits
by held-out F1, `docs/learned/tuned_vs_coact/replicate1/chosen/gated/outer0/`). Both ran on
the default dataset, `2026-09-17_revised_2v_long_STEPS_AND_PINS_EXCLUDED`.

## What was measured before stopping

- **Neither detector calls outside a scored window**: 0 of 3,540 CoactDetect calls and 0 of
  3,490 chorus_gain_norm calls across the 84 recordings. So nothing between the end of
  baseline and the start of the scored TTX window (the 2-minute wash-in), and nothing past a
  window's 20-minute cap, is ever looked at. A line there is missed by construction, not by
  the detector. "Around 20 minutes" of recording time is where baseline ends in both
  recordings, so the lines may sit in that wash-in gap.
- **In 20260303_301** the strongest synchrony within 3 minutes after baseline ends is 7 of 24
  cells within 0.5 s, at +159 s into TTX. Both detectors called it, CoactDetect at +159.2 s and
  chorus_gain_norm at +159.0 s.
- **In 20260629_309** the strongest in the same stretch is only 3 of 21 cells within 0.5 s,
  and neither detector called anything there. So the line Tony saw is not the tightest 0.5 s
  coincidence. It may be looser in time, or elsewhere near 20 minutes.

## For the next run

1. Pin the two lines to exact times on the raster (zoom the HTML page) before measuring
   anything, so the question is about a known moment.
2. For each, ask three things: was it inside a scored window; how many cells, over what spread
   of onsets; and what each detector's statistic did there.
3. If the wash-in gap is the cause, the question goes to the producer, not to the detectors.
   Windows are theirs (FOUNDATIONS; fireflies' scope stop of 2026-09-14 says the same).
