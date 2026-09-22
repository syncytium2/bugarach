# Onset jitter measured without bins: both streams are about three times tighter than their benches

Written 2026-09-22 on WSMIP064. Working material, not murderboarded. Tony, 2026-09-22: *"we don't
have our own measure of jitter?"* — until this, no: both benches' `jitter_sec` came from a
within-cluster spread that tracks bin/√12 (`tools/measure_slow_bench.py`, `BINS`), and so does the
MATLAB summary the fast bench's 0.36 s was taken from.

**Tool:** `tools/measure_jitter_correlogram.py` (tests: `tests/test_measure_jitter_correlogram.py`).
**Data:** the default dataset's 84 baseline analysis windows, `t50rise` onsets, per stream.
**Record:** `jitter_correlogram.json`. **Figure 1:** `jitter_correlogram.png`, and
`bugarach/2026-09-22-jitter-correlogram.png` in the darkroom.

## The measure

Onset pairs between distinct ROIs at each 0.1 s lag, over the count expected from each ROI's
total alone (`measure_slow_comodulation.py`'s statistic, imported). If participants scatter
with SD σ around a shared time, pair lags scatter with SD σ√2 and form a peak at short lags. Its
**half-width at half height**, after subtracting the 5–10 s level, is converted to σ two ways:

- **Calibrated on the simulator**: the same measure on each bench's recordings at ten planted
  jitters from 0.05 to 1.0 s, 48 recordings each. The half-width grows with planted jitter on
  both benches, so the method passes its own test.
- **From theory**: a Gaussian pair-lag peak has half-width σ√2·√(2 ln 2) ≈ 1.665 σ. The test
  confirms the measure recovers that within 15% on synthetic trains.

## The result

| stream | half-width, real (95% interval) | jitter, calibrated | jitter, from theory | bench today |
|---|---|---|---|---|
| fast | 0.183 s [0.160, 0.203] | **0.106 s** [0.091, 0.120] | 0.110 s | 0.36 s |
| slow | 0.230 s [0.215, 0.253] | **0.135 s** [0.126, 0.149] | 0.138 s | 0.30 s |

All 200 bootstrap draws land on each calibration curve. **Both streams' onsets are about three
times tighter than their benches assume, and slow is only slightly looser than fast.** Neither
0.30 nor 0.46 s is supported for slow, and fast's 0.36 s is not supported either.

## How it can be that tight on a 0.1 s frame grid (Figure 2)

Tony, 2026-09-22: *"how can it be so tight if sampling is 0.1s"*. **Figure 2**,
`explain_jitter.png` (script `explain_jitter.py`; darkroom `bugarach/2026-09-22-explain-jitter.png`).
The producer's `t50rise` onsets sit exactly on the 0.1 s grid (checked: every offset under
0.00001 frames), so every onset is rounded. Three things make the jitter measurable anyway:

- **Rounding is small against the spread.** Rounding to a frame adds a uniform error of
  ±0.05 s, whose standard deviation is 0.1/√12 = 0.029 s. A true σ of 0.11 s is recorded as
  √(0.11² + 0.029²) = 0.114 s, and the calibration's simulated onsets are rounded the same way.
- **σ = 0.11 s still spreads over several frames** (panel B): about 35% of a cell's onsets land
  in the event's own frame, 24% in each neighbour and 7% two frames out. σ = 0.36 s spreads
  over fifteen. The difference is visible frame by frame.
- **The width is read from many pairs across that shape** (panel C), not from any one onset:
  every pair of onsets from two different cells, over every event in 84 recordings, at each
  frame of lag. The calibration (panel D) shows the measure still tells 0.05 s from 0.1 s.

## What to be careful about

- **Shape (Figure 1, bottom).** Fast follows the simulated 0.1–0.15 s curves along its whole
  length. **Slow has a core like that and a longer tail** out to about 1.5 s: more like a mix of
  tight and looser events than one jitter. The half-width reports the core.
- **Anything that fires ROIs in the same frame sharpens the peak**: a motion, light or neuropil
  artefact shared across the field would read as tight coordination. This measure cannot tell
  that apart from coordination, and the slow stream's zero-lag excess (about 27 times chance)
  is large. It is a question for the producer if it matters.
- **The simulator's long-lag level is far above the real one** (Figure 1, top: excess ≈ 0.75 at
  5–10 s on the fast bench, about 0.1 in real data), from its elevated-rate stretch and burst
  shapes. The half-width subtracts it, so it does not move this result, but it is a mismatch
  between the benches and the data in its own right.
- **The RMS lag was tried first and rejected**: it reads fast as 0.48 s because tail noise
  moves it. Both are in the record.

## What it would change

A jitter change moves the bench, so every number scored on it — goal 1's tuned settings, goal 2's
comparison, and the slow work — would be re-checked. Tighter events make coordination easier to
detect, so scores would likely rise and the field compress further. This is Tony's call; no
bench constant is changed here.
