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

PROVISIONAL = True
"""True until the measured values replace the placeholders below (module docstring, step 4)."""

MEASURED_RATE_SHAPE = _slow.MEASURED_RATE_SHAPE
MEASURED_BURST_SHAPE = _slow.MEASURED_BURST_SHAPE
MEASURED_BURST_BINS = _slow.MEASURED_BURST_BINS
MEASURED_WIDTH_QUANTILES = tuple(_slow.MEASURED_WIDTH_QUANTILES)

REGIMES: dict[str, dict] = {
    "baseline_quiet": dict(bg_rate_hz=round(_fast.REGIMES["baseline_quiet"]["bg_rate_hz"]
                                            + _slow.REGIMES["baseline_quiet"]["bg_rate_hz"], 4)),
    "baseline_busy": dict(bg_rate_hz=round(_fast.REGIMES["baseline_busy"]["bg_rate_hz"]
                                           + _slow.REGIMES["baseline_busy"]["bg_rate_hz"], 4)),
}
"""Per-ROI background rates. Provisional: fast + slow, since every onset of both is kept."""

NULL_RECORDING = dict(bg_rate_hz=REGIMES["baseline_quiet"]["bg_rate_hz"], n_per_level=(0, 0, 0),
                      hot_window=None, hot_rate_hz=0.0, ramp_sec=0.0, n_distractors=0)
"""The no-coordination test's recording, at the combined quiet background."""

BENCH_RECORDING = dict(
    _slow.BENCH_RECORDING,
    n_roi=33,
    participation=_slow.BENCH_RECORDING["participation"],
    jitter_sec=_slow.BENCH_RECORDING["jitter_sec"],
    hot_rate_hz=round(_fast.BENCH_RECORDING["hot_rate_hz"]
                      + _slow.BENCH_RECORDING["hot_rate_hz"], 4),
    bg_rate_shape=MEASURED_RATE_SHAPE,
    bg_burst_shape=MEASURED_BURST_SHAPE,
    bg_burst_bin_sec=MEASURED_BURST_BINS,
)
"""The recording the combined bench scores on. Provisional values from the slow bench, whose
event widths and 300 s-only burst term it shares until measured; hot window, spacing and length
are the fast bench's, as on slow."""

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

MAX_PROBE_PER_MIN: dict[str, float] = dict(_slow.MAX_PROBE_PER_MIN)
MAX_FALSE_POSITIVES_PER_HOUR: dict[str, float] = dict(_slow.MAX_FALSE_POSITIVES_PER_HOUR)
MAX_PRECISION_DROP: dict[str, float] = dict(_slow.MAX_PRECISION_DROP)
"""Provisional: slow's budgets, replaced by :data:`BUDGETS_RECORD`'s ceilings (step 4)."""


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
