"""The SLOW-stream bench: the fast bench's machinery on recordings measured off the slow stream.

**A stopgap with a scheduled end.** Tony, 2026-09-21: *"we don't have time to rebuild
bench.py to handle more than one stream. this has to be a high priority todo after
tomorrows meeting."* So this module carries the slow constants **under the same names**
:mod:`bugarach.bench` uses, and **its own copies of every function that reads one**. The
rebuild that deletes it is ``docs/todo/2026-09-21-one-stream-aware-bench.md``. Until then a
fix to a copied function is owed in both files, and ``tests/test_bench_slow.py`` is what
notices when it is not.

**The trap this layout exists to avoid.** Re-exporting a :mod:`bugarach.bench` function that
reads a module constant scores FAST recordings under a slow label, silently:
``bench.evaluate`` reaches ``bench.BENCH_RECORDING`` through ``make_recording``,
``bench.run_detector`` reads ``bench.OPERATING_POINTS``, ``bench.pick_operating_point`` reads
``bench.MAX_PROBE_PER_MIN``. And one level further down, the simulator drew every event's
width from the fast table until 2026-09-21 — so the width table is passed explicitly here
(``simulate_coordination(width_quantiles=...)``), or locust would read fast widths on a slow
recording. ``tests/test_bench_slow.py`` fails if any copied name here **is** the ``bench``
object, and builds a slow recording to check its rates and its widths are slow ones.

**Shared, because they read no stream constant:** the result and error classes,
:func:`~bugarach.bench.pool_scores`, :func:`~bugarach.bench.fold_split`,
:func:`~bugarach.bench.nearest_neighbour_gaps`, the setting-validity rules, and the scoring
(:mod:`bugarach.score`). ``BenchResult.hot_fa_per_min`` reads the FAST bench's hot window;
the slow bench keeps the same window, and the test pins that.

**What is measured and what is chosen.** Measured on the default folder's slow baselines by
``tools/measure_slow_bench.py`` → :data:`MEASURED_RECORD`: the backgrounds, the rate and
300 s burst shapes, ROI count, participation and the width table. **Chosen**, every one
provisional and listed so it can be argued with:

- ``jitter_sec`` **0.135 s — measured, no longer chosen** (Tony, 2026-09-22: adopt it).
  ``tools/measure_jitter_correlogram.py`` gives 0.135 s [0.126, 0.149] for this stream on the
  default folder, from the width of the cross-ROI correlogram's peak calibrated against
  simulations of this bench. It replaces **0.30 s**, which rested on an analogy that did not
  hold: that number was bugarach's ``assess_coactivity`` at a 1 s bin, offered as "what the
  fast bench did", but the fast bench's 0.36 came from the MATLAB summary
  (``bench.MEASURED_PROVENANCE``), and that summary gives 0.46 s for slow at the same K. The
  analogy was moot in the end — on both streams that instrument tracks bin ÷ √12, so neither
  number identified a stream's own jitter, and the question of which of the two to copy had no
  right answer. The correlogram answers it directly instead. Slow is about a third looser than
  fast (0.135 against 0.106), where the old pair had slow *tighter* than fast (0.30 against
  0.36) — an ordering nothing ever justified. Record:
  ``docs/learned/runs/2026-09-22-jitter-correlogram/``; the superseded analogy and the 0.09 F1
  it was worth to locust and SPIKE-synch, ``docs/learned/runs/2026-09-21-slow-step-a/``.
- **No 60 s burst term** (Tony, 2026-09-21: *"disable the burst for slow"*). The slow
  stream's 60 s burst shape is unbounded above — no clumping at a minute that the fit can
  tell from chance — so only the 300 s scale is simulated.
- participation levels **(0.63, 0.38, 0.21)**: the fast bench's spread around its measured
  median (0.30 / 0.18 / 0.10), scaled to the slow median 0.38.
- the elevated-rate test at **0.032 Hz**, six times the slow stream's median per-ROI rate as
  the fast probe is six times its own; distractors at the middle participation, 0.38, as the
  fast ones sit at 0.18.
- event spacing, recording length, the close-events recordings and :data:`CROWDING_GAP_SEC`
  are the fast bench's. How crowded real slow recordings get is not measured yet —
  ``tools/probe_real_crowding.py`` runs CoactDetect at a fast setting, which is circular
  here — and a context wider than the 120 s spacing is refused by
  :func:`~bugarach.bench.context_fits_the_null` as it is on fast. **If the slow search
  presses against that, the spacing is the thing to move, not the rule.**
- :data:`OPERATING_POINTS`: **LoCo, CoactDetect and SPIKE-synch at slow settings** (adopted by
  Tony, 2026-09-21), the other three at the FAST settings, which is where the search started
  and what the false-alarm budgets were measured at (Tony: *"remeasure"*). Slow settings do
  **not** ship through ``bench.OPERATING_POINTS`` (``docs/handoffs/2026-09-21-slow-bench.md``).
"""

from __future__ import annotations

import numpy as np

from bugarach import bench as _fast
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

MEASURED_STREAM = "slow"
MEASURED_ROLE = "default"
"""The pointer's default dataset, confirmed per session (``dataset.default()``)."""
MEASURED_RECORD = "docs/learned/bench_measured_slow.json"
"""Written by ``tools/measure_slow_bench.py``. Never the fast record."""

MEASURED_RATE_SHAPE = 0.415
"""How unevenly rates spread across ROIs (gamma shape; lower is more uneven). Fast 0.275."""
MEASURED_BURST_SHAPE = 3.47
"""How unevenly one ROI's events spread over 300 s bins. Fast (1.547, 1.388) at 300 and 60 s;
the slow 60 s term is off, see the module docstring."""
MEASURED_BURST_BINS = 300.0

MEASURED_WIDTH_QUANTILES = (
    0.1, 0.1, 0.1, 0.1, 0.9, 1.1, 1.1, 1.2, 1.3, 1.3,
    1.3, 1.4, 1.4, 1.5, 1.5, 1.5, 1.5, 1.6, 1.6, 1.6,
    1.6, 1.6, 1.6, 1.7, 1.7, 1.7, 1.7, 1.7, 1.7, 1.7,
    1.8, 1.8, 1.8, 1.8, 1.8, 1.8, 1.8, 1.9, 1.9, 1.9,
    1.9, 1.9, 1.9, 1.9, 1.9, 2.0, 2.0, 2.0, 2.0, 2.0,
    2.0, 2.0, 2.0, 2.1, 2.1, 2.1, 2.1, 2.1, 2.1, 2.1,
    2.2, 2.2, 2.2, 2.2, 2.2, 2.2, 2.3, 2.3, 2.3, 2.3,
    2.3, 2.4, 2.4, 2.4, 2.4, 2.5, 2.5, 2.5, 2.5, 2.6,
    2.6, 2.6, 2.7, 2.7, 2.8, 2.8, 2.9, 3.0, 3.0, 3.1,
    3.2, 3.3, 3.4, 3.6, 3.7, 3.9, 4.2, 4.4, 4.7, 5.1,
    5.3, 5.5, 5.5, 5.5)
"""Seconds: the producer's SLOW ``width`` column at ``simulate.MEASURED_WIDTH_QUANTILE_LEVELS``,
over 26,152 baseline events in 84 recordings (``width_def`` =
``rise_interval_peak_minus_t50rise``). Median 2.0 s, max 5.5 s. The bottom 4% sit at one
frame, 0.1 s. Taken as it comes: what the column means is the producer's (FOUNDATIONS §7)."""

REGIMES: dict[str, dict] = {
    "baseline_quiet": dict(bg_rate_hz=0.0024),
    "baseline_busy": dict(bg_rate_hz=0.0089),
}
"""25th and 75th percentiles of per-recording mean per-ROI **background** rate over the
slow stream's baseline windows. Fast 0.0042 and 0.0165.

**Background, not total, since 2026-09-22** (Tony, ~21:45 EDT: *background, end to end*)
— the coordinated share subtracted, so the background generator is not asked to produce
firing the planted events already account for. Measured by
`tools/measure_coordination_rates.py` on the 75 of 84 baseline windows that clear
`fit_background_shape`'s floors, fixed model, 1 s counting window;
`docs/learned/runs/2026-09-23-coordination-rates/`.

**The raw rates were right; the subtraction is the change.** Raw p25/p75 read 0.00302 and
0.01133 against the 0.0030 and 0.0113 that stood here — within 0.6% — so what moved is the
correction: quiet −19.0%, busy −21.8%. It is proportionally larger here than on fast
(−16.5% and −13.6%) because more of this stream's firing is shared.

⚠ **Slow's estimator clears its calibration at every counting window**, unlike fast's, which
clears only 1 s. But the two terms the `passed` flag does not inspect are weakest here — the
moment rate reads −27.4% and participants +14.2%, errors in opposite directions whose product
is the gated quantity. That bears on anything read off participants or moment rate; it bears
much less on these two values, where the correction is about a fifth of the rate."""

NULL_RECORDING = dict(bg_rate_hz=0.0030, n_per_level=(0, 0, 0),
                      hot_window=None, hot_rate_hz=0.0, ramp_sec=0.0,
                      n_distractors=0)
"""The no-coordination test's recording, at the slow quiet background."""

BENCH_RECORDING = dict(
    duration_sec=2700.0,
    n_roi=32,
    participation=(0.63, 0.38, 0.21),
    n_per_level=(5, 5, 5),
    jitter_sec=0.135,
    min_sep_sec=120.0,
    bg_rate_shape=MEASURED_RATE_SHAPE,
    bg_burst_shape=MEASURED_BURST_SHAPE,
    bg_burst_bin_sec=MEASURED_BURST_BINS,
    hot_window=(1200.0, 1500.0),
    hot_rate_hz=0.0291,
    ramp_sec=30.0,
    n_distractors=6,
    distractor_frac=0.38,
    distractor_window=(120.0, 1100.0),
)
"""The recording the slow bench scores on. ``n_roi`` 32 is the measured median 31.5 rounded;
the rest is in the module docstring.

``hot_rate_hz`` is **0.0291 Hz since 2026-09-22**, was 0.032 — the 99th percentile of the
per-cell background rate over every 300-second stretch of every baseline window, on the same
set and the same subtraction as ``REGIMES``. Background end to end (Tony, ~21:45 EDT), so the
probe is the same quantity as the two endpoints rather than a different one at the top of the
axis.

**Its small net move hides two large ones, and that is worth knowing before anyone re-derives
it.** The raw 99th percentile is 0.0453 Hz — well *above* the old 0.032 — and the coordinated
share at the probe is **35.9%** of it, which pulls the adopted value back under. Unlike fast,
whose probe correction is 0.6%, this stream's busiest stretches **are** its coordinated ones.
So "the probe barely moved" is true of the number and false of the reasoning: −9% is +42% and
−36% cancelling. ⚠ That 36% is the largest correction anywhere in the measurement, on the
stream whose ungated calibration terms are weakest, and it is the first thing to re-check if
the slow bench behaves oddly. `docs/learned/runs/2026-09-23-coordination-rates/`."""

CROWDED_RECORDING = dict(BENCH_RECORDING, min_sep_sec=14.0, duration_sec=10800.0,
                         n_per_level=(40, 40, 40), hot_window=None,
                         hot_rate_hz=0.0, ramp_sec=0.0, n_distractors=0)
TAIL_RECORDING = dict(CROWDED_RECORDING, n_per_level=(60, 60, 60),
                      min_sep_sec=6.0, interval_cv=1.0)
"""The close-events recordings: the fast bench's spacing on the slow background."""
CROWDING_GAP_SEC = 30.0

SLOW_SEARCH = ("tools/search_all_settings.py --bench slow --sliding, 2026-09-21: chosen on seeds "
               "1-48, held out on 49-96, under the slow budgets and the close-events check; "
               "docs/learned/runs/2026-09-21-full-search-slow/")

OPERATING_POINTS: dict[str, OperatingPoint] = {
    **_fast.OPERATING_POINTS,
    "loco": OperatingPoint(
        params=dict(bin_width_sec=1.0, context_win_sec=120.0, thr_step_sec=15.0,
                    merge_gap_sec=4.0, threshold_pctile=99.995, n_surrogates=100, min_rois=3,
                    null_context_mode="maxlt", guard_sec=0.0, detection_mode="threshold",
                    peak_prominence=0.0, peak_min_distance_sec=0.0, window_mode="sliding"),
        source=("SLOW, adopted by Tony 2026-09-21. " + SLOW_SEARCH + ". Sliding; threshold "
                "99.5 -> 99.995 (bracketed: 99.9975 scored lower), merge gap 2 -> 4 s. Held out: "
                "mean F1 0.846 against 0.802 at the fast settings, gain +0.044 [+0.038, +0.051]; "
                "0 elevated-rate calls/hour on either background; 0.03 calls/hour on the "
                "no-coordination test; close-events F1 0.982 (-0.003). The context sits at the "
                "null rule's 120 s cap and did not move."),
        knob=_fast.OPERATING_POINTS["loco"].knob,
        grid=tuple(sorted(set(_fast.OPERATING_POINTS["loco"].grid) | {99.995, 99.9975})),
        takes_rng=_fast.OPERATING_POINTS["loco"].takes_rng),
    "coact": OperatingPoint(
        params=dict(int_win_sec=2.0, context_win_sec=60.0, alpha=1e-4, n_surrogates=100,
                    min_rois=6, merge_gap_sec=8.0, guard_sec=0.0, guard_norm="compact",
                    detection_mode="threshold", peak_prominence=0.0,
                    peak_min_distance_sec=0.0, window_mode="sliding"),
        source=("SLOW, adopted by Tony 2026-09-21. " + SLOW_SEARCH + ". Sliding; min_rois "
                "3 -> 6, merge gap 3 -> 8 s. Held out: mean F1 0.861 against 0.780, gain +0.081 "
                "[+0.072, +0.089]; 0 calls/hour on the no-coordination test, where min_rois 3 "
                "makes about 4 (chance triples: nothing is planted there) against a slow budget "
                "of 2; close-events F1 0.964 (-0.006). min_rois 6 sits under the smallest "
                "planted event (about 7 of 32 ROIs) and excludes none of them, but it is the "
                "setting that can learn the simulation's participation, which rests on the slow "
                "measurement of 0.38. The anchor for goal 2's shared false-alarm budget on slow."),
        knob=_fast.OPERATING_POINTS["coact"].knob,
        grid=_fast.OPERATING_POINTS["coact"].grid,
        takes_rng=_fast.OPERATING_POINTS["coact"].takes_rng),
    "sync": OperatingPoint(
        params=dict(C_threshold=0.1, C_min=0.0, tau_max=0.5, max_gap=4.0, min_n=3,
                    tau_mode="isi_adaptive", dt=0.1, detection_mode="threshold",
                    peak_prominence=0.0, peak_min_distance_sec=0.0),
        source=("SLOW, adopted by Tony 2026-09-21 at max_gap 4 s. Started from the slow search's "
                "pick (" + SLOW_SEARCH + ": C_min 0.0025, tau_max 0.5, max_gap 16) and corrected "
                "on two counts. C_min: every value from 0 to 0.03 gives identical calls on seeds "
                "1-48 (the profile moves in steps of about 1/31), so the search's unbracketed edge "
                "was a flat stretch and the setting is off, 0. max_gap: 16 s fails the close-events "
                "check held out (0.854 against a floor of 0.856), the merge-gap artifact; on seeds "
                "49-96, 4 s scores mean F1 0.845 and close-events 0.993, 8 s 0.856 and 0.963. "
                "4 s chosen over 8 s as the cautious one, a window-shaped setting the bench can "
                "flatter. Confirmed on fresh seeds 97-144: mean F1 0.845 against 0.728 at the "
                "fast settings, close-events 0.994 (+0.117), 0.55 elevated-rate calls/min, "
                "0 calls/hour on the no-coordination test."),
        knob=_fast.OPERATING_POINTS["sync"].knob,
        grid=_fast.OPERATING_POINTS["sync"].grid,
        takes_rng=_fast.OPERATING_POINTS["sync"].takes_rng),
}
"""LoCo, CoactDetect and SPIKE-synch: adopted as the slow reference (Tony, 2026-09-21). The
other three: the FAST settings, which is where the search started and what the budgets below
were measured at, held until the fast questions on them are settled (binned SCE 98 or 75,
locust's anchor); rate+context's slow gain was +0.005, nothing to adopt. **None of these
ships**: real-data detection reads ``bench.OPERATING_POINTS``, and a slow setting reaches a
real recording only through a settings file with ``stream=slow`` rows (``docs/handoffs/2026-09-21-slow-bench.md``)."""
DETECTORS = tuple(OPERATING_POINTS)

SLOW_EXTRA: dict[str, dict[str, tuple]] = {
    "loco": {"bin_width_sec": (8.0, 10.0), "merge_gap_sec": (16.0,),
             "guard_sec": (8.0,), "peak_min_distance_sec": (10.0,)},
    "sync": {"tau_max": (4.0, 8.0), "max_gap": (4.0, 8.0), "dt": (1.0,),
             "peak_min_distance_sec": (10.0,)},
    "coact": {"int_win_sec": (8.0, 10.0), "merge_gap_sec": (16.0,),
              "guard_sec": (8.0,), "peak_min_distance_sec": (10.0,)},
    "rate": {"rate_win": (8.0, 10.0), "merge_gap_s": (16.0,),
             "guard_sec": (8.0,), "peak_min_distance_sec": (10.0,)},
    "sce": {"bin_width_sec": (45.0, 60.0), "merge_gap_sec": (45.0, 60.0),
            "peak_min_distance_sec": (20.0,)},
    "cicada": {"n_synchronous_frames": (20, 40), "sce_min_distance_frames": (32, 64)},
}
"""Values added past the fast grids' top on every time-valued axis — about double each top
value, the SPIKE-synch windows four to five times — because slow timing runs two to four times
fast's: within-ROI intervals 5.7 s against 1.5 s at the 5th percentile, widths 2.0 s
against 0.9 s at the median (``tools/measure_slow_bench.py``). The search still extends an
edge past these and refuses an optimum that stays on one. **Context windows are not
widened**: :func:`~bugarach.bench.context_fits_the_null` caps them at the 120 s event spacing,
on slow as on fast, and a slow search pressing on that cap is a reason to move the spacing."""

FULL_GRIDS: dict[str, dict[str, tuple]] = {
    d: {k: tuple(sorted(set(v) | set(SLOW_EXTRA.get(d, {}).get(k, ())),
                        key=lambda x: (isinstance(x, str), x)))
        for k, v in g.items()}
    for d, g in _fast.FULL_GRIDS.items()}
"""The fast grids plus :data:`SLOW_EXTRA`. Same axes, so goal 2 and the search walk the same
settings on either stream."""

MAX_CROWDED_DROP = _fast.MAX_CROWDED_DROP
"""The close-events allowance is a judgement about noise, not a stream measurement, and it is
still unsigned on fast (the crowded-allowance sweep is its input). Same number, same status."""

BUDGETS_RECORD = "docs/learned/bench_slow_budgets.json"
"""Written by ``tools/measure_slow_budgets.py``: each detector at the FAST settings (measured before
LoCo and CoactDetect were adopted, and kept as measured) on
seeds 1–48 of this bench, and the same on the fast bench for comparison."""

# Measured on THIS bench at OPERATING_POINTS (Tony, 2026-09-21: "remeasure"), then one rule
# turns a measurement into a ceiling: rates max(1, ceil(1.6 x measured)); precision swing
# max(0.10, measured + 0.05 up to a 0.05 step). ⚠ The rule is this session's, not Tony's, and
# it is TIGHTER than several fast ceilings: applied to the fast bench's own measurements it
# gives locust 13 probe calls/min where bench.py declares 25, and binned SCE a 0.10 swing
# where bench.py declares 0.50 — fast ceilings set at older settings and never tightened.
# tests/test_bench_slow.py holds these equal to the record's ceilings.
# ⚠ RE-MEASURED 2026-09-22, because this bench's own constants moved: `REGIMES` became
# background rates and `hot_rate_hz` went 0.032 -> 0.0291. These are the ceilings
# `tools/measure_slow_budgets.py` derives from that re-measurement, and
# `tests/test_bench_slow.py` asserts they EQUAL the record rather than merely contain it,
# so they are not chosen here — they are copied, and the comment is the measurement.
# Most TIGHTENED: the slow bench got a little easier to be quiet on.
MAX_PROBE_PER_MIN: dict[str, float] = {
    "loco": 1.0,      # measured: 0.01, was 1.0 at 0.14
    "cicada": 4.0,    # measured: 1.93, was 5.0 at 2.59 — tightened
    "sce": 7.0,       # measured: 4.30, was 8.0 at 4.67 — tightened
    "coact": 1.0,     # measured: 0.22, was 1.0 at 0.07
    "rate": 1.0,      # measured: 0.27, was 1.0 at 0.36
    "sync": 1.0,      # measured: 0.38, was 1.0 at 0.05
}
MAX_FALSE_POSITIVES_PER_HOUR: dict[str, float] = {
    "loco": 1.0,      # measured: 0.08, was 1.0 at 0.56
    "cicada": 1.0,    # measured: 0.61
    "sce": 5.0,       # measured: 3.08
    "coact": 1.0,     # measured: 0.00, was 2.0 at 1.25 — tightened
    "rate": 1.0,      # measured: 0.00
    "sync": 1.0,      # measured: 0.00
}
MAX_PRECISION_DROP: dict[str, float] = {
    "loco": 0.10,     # measured: 0.001, was 0.10 at 0.034
    "cicada": 0.15,   # measured: 0.067, was 0.10 at 0.011 — the one that loosened
    "sce": 0.10,      # measured: 0.025
    "coact": 0.10,    # measured: 0.003, was 0.15 at 0.070 — tightened
    "rate": 0.10,     # measured: 0.003
    "sync": 0.10,     # measured: 0.001
}


def measured_constants() -> dict[str, float]:
    """Every value here that claims to be measured, keyed as ``measure_slow_bench`` keys them."""
    return {
        "rate_shape": MEASURED_RATE_SHAPE,
        "burst_shape_300s": MEASURED_BURST_SHAPE,
        "regime_quiet_hz": REGIMES["baseline_quiet"]["bg_rate_hz"],
        "regime_busy_hz": REGIMES["baseline_busy"]["bg_rate_hz"],
        "n_roi": float(BENCH_RECORDING["n_roi"]),
        "participation": BENCH_RECORDING["participation"][1],
    }


def _simulate(seed, spec, overrides):
    return simulate_coordination(seed=seed, width_quantiles=MEASURED_WIDTH_QUANTILES,
                                 **{**spec, **overrides})


def make_recording(regime: str, seed: int, **overrides):
    """One slow bench recording; ``regime`` selects the background. Copy of ``bench``'s."""
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
    """Calls per hour on the slow no-coordination recording. Copy of ``bench``'s."""
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
    """One detector over several slow recordings, pooled. Copy of ``bench``'s."""
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
    """``bench.pick_operating_point`` with THIS module's elevated-rate budget.

    ``-1.0`` looks the detector up in :data:`MAX_PROBE_PER_MIN` and, unlike the fast bench,
    **refuses** a detector with no entry: an empty budget here means it has not been
    measured on the slow bench yet, not that the detector is new.
    """
    if max_probe_per_min == -1.0:
        name = next((r.detector for r in curve), None)
        if name not in MAX_PROBE_PER_MIN:
            raise ValueError(
                f"no slow elevated-rate budget for {name!r}: run "
                "tools/measure_slow_budgets.py before choosing on the slow bench")
        max_probe_per_min = MAX_PROBE_PER_MIN[name]
    return _fast.pick_operating_point(curve, max_probe_per_min=max_probe_per_min)
