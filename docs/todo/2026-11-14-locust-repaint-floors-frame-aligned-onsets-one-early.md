---
status: open
filed: 2026-11-14
---

# locust paints events that start exactly on a frame boundary one frame early

## What is wrong

`_build_raster` in [`detectors/cicada.py`](../../src/bugarach/detectors/cicada.py) finds an
event's onset frame as `floor((t - t_lo) / dt)`. When `t` sits exactly on a frame boundary,
`t = t_lo + k*dt`, floating-point error sometimes makes the quotient `k - ε`. The event is
then painted from frame `k - 1`, and its whole run moves one frame early.

Onsets produced from a binary raster always sit on frame boundaries.
[`tools/import_dandi.py`](../../tools/import_dandi.py) `runs()` returns `t0 + rise * dt`, so
every recording imported from DANDI:000219 is affected. This lab's own onsets are half-rise
times measured between frames, so they almost never land exactly on a boundary.

## How big it is (synthetic data only, 2026-11-14)

The test used 400 cells and 12,500 frames at 8.46 Hz. A binary raster went through `runs()`
and was repainted with `_build_raster` at the same `dt`:

| recording start `t0` | events painted one frame early | raster identical |
|---|---|---|
| 0 s | 268 of 11,412 events (2.3%) | no |
| 3.217 s | 297 of 11,412 events (2.6%) | no |
| 1234.5678 s | 3,812 of 11,412 events (33%) | no |

The error grows with `t0`, because a larger absolute time leaves less floating-point
precision for the fraction of a frame.

The repaint is bit-identical when onsets are placed at frame centres (`+ 0.5*dt`) and a
region spanning the whole movie is passed, so the grid has all `nf` frames. With that
workaround, locust run with Cossart's settings matches CICADA's "SCE description"
coactivity curve exactly, and its threshold too (14 cells in all three seeds). The calls
still differ slightly: 61 against CICADA's 62, 54 on the same frame and 59 within one. That
remainder is a separate, deliberate difference. locust's peak picker follows MATLAB
`findpeaks`, which takes a plateau's left edge; scipy, which CICADA uses, takes its middle.

## What it costs

- Every number locust has produced from the Cossart corpus was computed on a raster that
  was shifted in places. That includes the transfer rows in
  [`cossart_transfer/`](../learned/cossart_transfer/README.md) that used locust.
- A comparison of locust with CICADA on frame-aligned data cannot agree exactly until this
  is fixed.

## Done when

- `_build_raster` snaps an onset that lies within a small tolerance of a frame boundary
  onto that frame (for example by rounding `(t - t_lo)/dt` to 1e-9 before the floor). It
  must not start using `round` for every onset, which would change results on this lab's
  data.
- A test repaints a binary raster after a `runs()` round trip at several `t0` values and
  requires it to be bit-identical.
- Or `import_dandi.runs()` emits frame-centre onsets and says so in `width_def` and its
  docstring. Fixing the painter is better, since any frame-quantized producer has the same
  problem.

Related: [the movie-seam todo](2026-11-14-dandi-000219-import-respect-movie-seams-and-the-real-clock.md),
which concerns the same importer.
