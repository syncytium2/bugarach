"""The COMBINED-stream bench: fast and slow onsets as one stream, simulated as one stream.

Tony, 2026-09-22: *"the pipeline fed the onsets of both fast and slow as a single stream …
run the same correlogram to derive jitter and all the same characterization for simulation as
if it were one stream. Then optimize the detectors creating a third param set."* The stream is
:func:`bugarach.combined.combine` — every onset of both, labelled, nothing deduplicated.

**Built the way** :mod:`bugarach.bench_slow` **was, and for the same reason**: the constants sit
under the names :mod:`bugarach.bench` uses, and every function that reads one is this module's
own copy, so nothing here can score a fast or slow recording under a combined label
(``tests/test_bench_combined.py``). It ends with the same rebuild,
``docs/todo/2026-09-21-one-stream-aware-bench.md``.

**The route, in order — each step is the fast/slow step with ``combined`` passed:**

1. ``tools/measure_jitter_correlogram.py --streams combined`` → jitter, calibrated on this bench.
2. ``tools/measure_slow_bench.py --stream combined --jitter-record <1>`` →
   :data:`MEASURED_RECORD`: backgrounds, rate and burst shapes, ROI count, participation and
   the width table (each event's own stream's width; ``combined.combine``'s ``width_def``).
3. ``tools/measure_coordination_rates.py`` → background quiet/busy and the 99th-percentile
   probe, on the background basis Tony ruled for fast and slow (2026-09-22, #748).
4. Transcribe 1–3 here; ``tools/measure_slow_budgets.py --bench combined`` → budgets.
5. ``tools/search_all_settings.py --bench combined --sliding`` → the third parameter set.

⚠ **Until step 4 lands, every constant below is PROVISIONAL**: fast + slow for the rates,
slow's shapes and widths, the fast settings as the search's starting point (where slow's
search started too), slow's budgets. :data:`PROVISIONAL` says so, and
``tests/test_bench_combined.py`` refuses a measured record that disagrees with a constant.
"""

from __future__ import annotations

import numpy as np

from bugarach import bench as _fast
from bugarach import bench_slow as _slow
from bugarach.bench import (  # noqa: F401  (shared: none reads a stream constant)
    FULL_GRID_PAIRS,
    MIN_BASELINE_SEC,
    NOT_SEARCHED,
    STREAM,
    BenchResult,
    DegenerateSweep,
    EdgeOfRange,
    OperatingPoint,
    TooPromiscuous,
    context_fits_the_null,
    fold_split,
    nearest_neighbour_gaps,
    pool_scores,
    setting_applies,
    settings_are_valid,
)
from bugarach.detectors.cicada import cicada_detect
from bugarach.detectors.coact import coact_detect
from bugarach.detectors.loco import loco_detect
from bugarach.detectors.rate import rate_detect, recording_extent, stream_trains
from bugarach.detectors.sce import sce_detect
from bugarach.detectors.sync import sync_detect
from bugarach.score import TOL_SEC, score_stream
from bugarach.simulate import simulate_coordination

MEASURED_STREAM = "combined"
MEASURED_ROLE = "default"
"""The pointer's default dataset, confirmed per session (``dataset.default()``)."""
MEASURED_RECORD = "docs/learned/bench_measured_combined.json"
"""Written by ``tools/measure_slow_bench.py --stream combined``. Never the fast or slow record."""

PROVISIONAL = False
"""Cleared 2026-09-23: every constant below is measured on the combined stream of the default
folder, by the route in the module docstring. Records:
``docs/learned/runs/2026-09-23-jitter-correlogram-combined/`` (jitter),
:data:`MEASURED_RECORD` (shapes, ROI count, participation, widths), and
``docs/learned/runs/2026-09-23-coordination-rates-combined/`` (backgrounds and the probe)."""

MEASURED_RATE_SHAPE = 0.3266
"""Gamma shape of the per-ROI combined background rate, ML fit over 81 baseline windows.

Between its parents (fast 0.275, slow 0.4152), which is what pooling two streams of one cell
should do: the union is less heterogeneous than either alone because a cell quiet in one stream
can be busy in the other."""

MEASURED_BURST_SHAPE = 2.0987
MEASURED_BURST_BINS = 300.0
"""One scale, as on slow. The 60 s fit is 2.0660 and sits inside the 300 s interval
[1.6215, 3.0440], so the combined stream gives no evidence of clumping at a minute that the
300 s term does not already carry; simulating both would multiply one signal by itself."""

MEASURED_WIDTH_QUANTILES = (
    0.1, 0.1, 0.4, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5,
    0.6, 0.6, 0.6, 0.6, 0.6, 0.6, 0.6, 0.6, 0.7, 0.7,
    0.7, 0.7, 0.7, 0.7, 0.7, 0.8, 0.8, 0.8, 0.8, 0.8,
    0.8, 0.8, 0.9, 0.9, 0.9, 0.9, 0.9, 0.9, 1.0, 1.0,
    1.0, 1.0, 1.0, 1.0, 1.1, 1.1, 1.1, 1.1, 1.2, 1.2,
    1.2, 1.2, 1.2, 1.3, 1.3, 1.3, 1.4, 1.4, 1.4, 1.5,
    1.5, 1.5, 1.6, 1.6, 1.6, 1.6, 1.7, 1.7, 1.7, 1.8,
    1.8, 1.8, 1.8, 1.9, 1.9, 1.9, 2.0, 2.0, 2.0, 2.0,
    2.1, 2.1, 2.1, 2.2, 2.2, 2.3, 2.3, 2.3, 2.4, 2.5,
    2.5, 2.6, 2.7, 2.8, 2.9, 3.1, 3.3, 3.6, 4.1, 4.7,
    5.1, 5.65, 12.06, 27.9,
)
"""Each event's own stream's width, over 70,543 events; median 1.2 s, interquartile 0.8–1.9 s.

⚠ **The one place combined is not between its parents.** Its maximum is 27.9 s against slow's
5.5 s and its 99th percentile 4.7 s, so the top of this table is a thin tail rather than a
typical width. The widths are inherited from each contributing stream rather than produced by
combining, so the tail is a property of the fast/slow width columns that pooling exposes. It has
not been chased; locust is the only detector that reads it."""

REGIMES: dict[str, dict] = {
    "baseline_quiet": dict(bg_rate_hz=0.0072),
    "baseline_busy": dict(bg_rate_hz=0.0268),
}
"""Per-ROI **background** rates: the 25th and 75th percentiles of per-recording mean combined
rate, minus the coordinated share.

Background and not raw, per Tony's ruling of 2026-09-22 (#748: *background, end to end*), on the
``shape_usable`` set with the fixed model at the 1 s window — the same basis as fast and slow.
Raw would be 0.0075 and 0.0341. The coordinated share is 1.5% of the combined rate, so the two
bases differ by less here than the ruling's stakes on slow suggested; the ruling matters for
consistency across the three streams rather than for the size of this particular move."""

NULL_RECORDING = dict(bg_rate_hz=REGIMES["baseline_quiet"]["bg_rate_hz"], n_per_level=(0, 0, 0),
                      hot_window=None, hot_rate_hz=0.0, ramp_sec=0.0, n_distractors=0)
"""The no-coordination test's recording, at the combined quiet background."""

BENCH_RECORDING = dict(
    _slow.BENCH_RECORDING,
    n_roi=32,
    participation=(0.40, 0.24, 0.13),
    jitter_sec=0.148,
    hot_rate_hz=0.1464,
    distractor_frac=0.24,
    bg_rate_shape=MEASURED_RATE_SHAPE,
    bg_burst_shape=MEASURED_BURST_SHAPE,
    bg_burst_bin_sec=MEASURED_BURST_BINS,
)
"""The recording the combined bench scores on. Measured 2026-09-23; hot window, spacing and
length remain the fast bench's, as on slow.

- ``n_roi`` **32**, the median over the folder (31.5, interval 27.0–33.5) — the same cells, so
  the same count as slow.
- ``participation`` **(0.40, 0.24, 0.13)**. The middle level is measured, 0.2381, and sits where
  a union should: between fast's 0.19 and slow's 0.38. The outer levels keep slow's ratios about
  the middle (×1.66 and ×0.55) rather than being measured, so recall still resolves a participant
  floor; the 0.13 level is about 4 cells.
- ``jitter_sec`` **0.148 s** [0.1336, 0.1602], the correlogram's calibrated half-width, monotone
  calibration with 0 of 200 bootstrap draws off the curve. Looser than either parent
  (fast 0.106, slow 0.135), which is what merging two differently-timed streams does to a
  cross-ROI peak.
- ``hot_rate_hz`` **0.1464**, the background 99th percentile of 5-minute baseline stretches, per
  the 2026-09-22 ruling. It is 5.5× the busy background, close to fast's ratio of 7.7×.
- ``distractor_frac`` **0.24**, the middle participation, as fast uses 0.18 and slow 0.38."""

CROWDED_RECORDING = dict(BENCH_RECORDING, min_sep_sec=14.0, duration_sec=10800.0,
                         n_per_level=(40, 40, 40), hot_window=None,
                         hot_rate_hz=0.0, ramp_sec=0.0, n_distractors=0)
TAIL_RECORDING = dict(CROWDED_RECORDING, n_per_level=(60, 60, 60),
                      min_sep_sec=6.0, interval_cv=1.0)
CROWDING_GAP_SEC = _slow.CROWDING_GAP_SEC

OPERATING_POINTS: dict[str, OperatingPoint] = dict(_fast.OPERATING_POINTS)
"""Where the combined search starts: the fast settings, as the slow search did. **None of these
ships**; a combined setting reaches a real recording only through a settings file with
``stream=combined`` rows, as slow's do."""
DETECTORS = tuple(OPERATING_POINTS)

FULL_GRIDS: dict[str, dict[str, tuple]] = {d: dict(g) for d, g in _slow.FULL_GRIDS.items()}
"""The slow grids: the fast axes and every fast value, plus the slow extensions, because the
combined stream carries both timescales."""

MAX_CROWDED_DROP = _fast.MAX_CROWDED_DROP

BUDGETS_RECORD = "docs/learned/bench_combined_budgets.json"
"""Written by ``tools/measure_slow_budgets.py --bench combined``."""

MAX_PROBE_PER_MIN: dict[str, float] = {
    "loco": 1.0, "cicada": 68.0, "sce": 10.0, "coact": 1.0, "rate": 8.0, "sync": 16.0,
}
MAX_FALSE_POSITIVES_PER_HOUR: dict[str, float] = {
    "loco": 5.0, "cicada": 2.0, "sce": 7.0, "coact": 10.0, "rate": 1.0, "sync": 1.0,
}
MAX_PRECISION_DROP: dict[str, float] = {
    "loco": 0.1, "cicada": 0.1, "sce": 0.15, "coact": 0.1, "rate": 0.15, "sync": 0.1,
}
"""Measured ceilings from :data:`BUDGETS_RECORD`, seeds 1–48, at the settings this module
started from. **Budgets record what each detector does today so a change is visible** — they are
not targets, and the fast bench's docstring makes the same point.

⚠ **Two of them say the combined probe is a much harder test than fast's, and that is the thing
to look at before any of these is trusted.** The probe is a stretch at the background 99th
percentile, which on combined is 0.1464 Hz — 5.5× the busy background, and denser in absolute
terms than either parent's probe because every onset of both streams is in it.

- **locust fires 42 times a minute into it** (ceiling 68), against 7.8 on fast where its declared
  budget is 25. It is the detector that keys on a percentile of its own histogram, so a denser
  block moves its threshold with it rather than past it.
- **SPIKE-synch fires 9.4** (ceiling 16) against 0.6 on fast. Combining streams puts two onsets
  of the same cell close together far more often, which is what it counts.

Neither is evidence that those detectors are broken on combined; it is evidence that a probe
built this way asks them a different question than fast's does. Whether the combined probe should
be the background 99th percentile at all, given that, is worth Tony's eye — it follows the ruling
for fast and slow, and the ruling was not made with this stream's density in view."""


def measured_constants() -> dict[str, float]:
    """Every value here that claims to be measured, keyed as ``measure_slow_bench`` keys them."""
    return {
        "rate_shape": MEASURED_RATE_SHAPE,
        "burst_shape_300s": MEASURED_BURST_SHAPE,
        "regime_quiet_hz": REGIMES["baseline_quiet"]["bg_rate_hz"],
        "regime_busy_hz": REGIMES["baseline_busy"]["bg_rate_hz"],
        "n_roi": float(BENCH_RECORDING["n_roi"]),
        "participation": BENCH_RECORDING["participation"][1],
        "jitter_sec": BENCH_RECORDING["jitter_sec"],
    }


def _simulate(seed, spec, overrides):
    return simulate_coordination(seed=seed, width_quantiles=MEASURED_WIDTH_QUANTILES,
                                 **{**spec, **overrides})


def make_recording(regime: str, seed: int, **overrides):
    """One combined bench recording; ``regime`` selects the background. Copy of ``bench``'s."""
    if regime not in REGIMES:
        raise ValueError(f"unknown regime {regime!r} — have {sorted(REGIMES)}")
    return _simulate(seed, {**BENCH_RECORDING, **REGIMES[regime]}, overrides)


def make_crowded_recording(regime: str, seed: int, **overrides):
    if regime not in REGIMES:
        raise ValueError(f"unknown regime {regime!r} — have {sorted(REGIMES)}")
    return _simulate(seed, {**CROWDED_RECORDING, **REGIMES[regime]}, overrides)


def make_tail_recording(regime: str, seed: int, **overrides):
    if regime not in REGIMES:
        raise ValueError(f"unknown regime {regime!r} — have {sorted(REGIMES)}")
    return _simulate(seed, {**TAIL_RECORDING, **REGIMES[regime]}, overrides)


def make_null_recording(seed: int, **overrides):
    return _simulate(seed, {**BENCH_RECORDING, **NULL_RECORDING}, overrides)


def run_detector(name: str, s, *, rng_seed: int = 20260706, **overrides):
    """One detector on a slice at THIS module's operating point. Copy of ``bench``'s."""
    if name not in OPERATING_POINTS:
        raise ValueError(f"unknown detector {name!r} — have {sorted(OPERATING_POINTS)}")
    op = OPERATING_POINTS[name]
    params = {**op.params, **overrides}
    if op.takes_rng:
        params["rng_seed"] = rng_seed
    if name in ("loco", "cicada", "sce"):
        fn = {"loco": loco_detect, "cicada": cicada_detect, "sce": sce_detect}[name]
        return fn(s, **params).streams[STREAM]
    ext = recording_extent(s)
    trains = stream_trains(s.streams[STREAM], ext)
    fn = {"coact": coact_detect, "rate": rate_detect, "sync": sync_detect}[name]
    return fn(trains, ext, **params)


def false_positives_per_hour(name: str, seeds=(1, 2, 3), **overrides) -> float:
    """Calls per hour on the combined no-coordination recording. Copy of ``bench``'s."""
    hours, total = 0.0, 0
    for seed in seeds:
        s, _ = make_null_recording(seed)
        det = run_detector(name, s, **overrides)
        onsets = getattr(det, "onset_sec", None)
        onsets = np.asarray(det.locs if onsets is None else onsets, dtype=float)
        total += int(np.isfinite(onsets).sum())
        hours += BENCH_RECORDING["duration_sec"] / 3600.0
    return total / hours if hours else float("nan")


def evaluate(name: str, regime: str, seeds=(1, 2, 3), *, tol_sec: float = TOL_SEC,
             gen: dict | None = None, **overrides) -> BenchResult:
    """One detector over several combined recordings, pooled. Copy of ``bench``'s."""
    scores = []
    for seed in seeds:
        s, gt = make_recording(regime, seed, **(gen or {}))
        det = run_detector(name, s, **overrides)
        scores.append(score_stream(gt, det, tol_sec=tol_sec))
    return pool_scores(scores, detector=name, regime=regime, seeds=seeds,
                       knob_value=overrides.get(OPERATING_POINTS[name].knob))


def sweep(name: str, regime: str, seeds=(1, 2, 3), values=None, *,
          gen: dict | None = None) -> list[BenchResult]:
    op = OPERATING_POINTS[name]
    values = op.grid if values is None else values
    return [evaluate(name, regime, seeds, gen=gen, **{op.knob: v}) for v in values]


def pick_operating_point(curve: list[BenchResult], *,
                         max_probe_per_min: float | None = -1.0) -> BenchResult:
    """``bench.pick_operating_point`` with THIS module's elevated-rate budget; refuses a detector
    with no entry, as the slow bench does."""
    if max_probe_per_min == -1.0:
        name = next((r.detector for r in curve), None)
        if name not in MAX_PROBE_PER_MIN:
            raise ValueError(
                f"no combined elevated-rate budget for {name!r}: run "
                "tools/measure_slow_budgets.py --bench combined before choosing here")
        max_probe_per_min = MAX_PROBE_PER_MIN[name]
    return _fast.pick_operating_point(curve, max_probe_per_min=max_probe_per_min)
