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
    FLOOR_CACHE_ENV,
    FLOOR_LABEL,
    FLOOR_SWITCH_ENV,
    FLOORED_SETTING,
    FULL_GRID_PAIRS,
    MIN_BASELINE_SEC,
    NOT_SEARCHED,
    STREAM,
    BenchResult,
    DegenerateSweep,
    EdgeOfRange,
    ELEVATED_SEED_OFFSET,
    NULL_SEED_OFFSET,
    OperatingPoint,
    ProbeResult,
    TooPromiscuous,
    context_fits_the_null,
    floor_enabled,
    fold_split,
    nearest_neighbour_gaps,
    pool_scores,
    recording_floor,
    setting_applies,
    settings_are_valid,
    under_floor_report,
    with_floor,
)
# `cicada` is locust's key: the detector is called locust wherever a person sees it, and the
# key stays `cicada` because it is the detections.csv contract value (detectors/cicada.py).
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
``docs/learned/runs/2026-09-23-jitter-correlogram-combined-senktide-ttx/`` (jitter),
:data:`MEASURED_RECORD` (shapes, ROI count, participation, widths), and
``docs/learned/runs/2026-09-23-coordination-rates-senktide-ttx/`` (backgrounds and the probe),
all on the 66-recording default since the re-measure of 2026-09-23. The 84-recording records
were ``...-jitter-correlogram-combined/`` and ``...-coordination-rates-combined/``."""

MEASURED_RATE_SHAPE = 0.3579
"""Gamma shape of the per-ROI combined background rate, ML fit over 64 baseline windows.

Re-measured 2026-09-23 on the default folder's 66 recordings: 0.3579 [0.2858, 0.4812], from
0.3266 over 81 windows of the 84-recording folder. Every measured constant in this module moved
in that pass (``docs/learned/bench_measured_combined.json``).

Between its parents (fast 0.291, slow 0.469), which is what pooling two streams of one cell
should do: the union is less heterogeneous than either alone because a cell quiet in one stream
can be busy in the other."""

MEASURED_BURST_SHAPE = 2.1216
MEASURED_BURST_BINS = 300.0
"""One scale, as on slow. 2.1216 [1.6043, 2.9525] on the 66 recordings, from 2.0987. The 60 s
fit is 2.0696 and sits inside the 300 s interval, so the combined stream gives no evidence of
clumping at a minute that the 300 s term does not already carry; simulating both would multiply
one signal by itself."""

MEASURED_WIDTH_QUANTILES = (
    0.1, 0.1, 0.4, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5,
    0.6, 0.6, 0.6, 0.6, 0.6, 0.6, 0.6, 0.6, 0.7, 0.7,
    0.7, 0.7, 0.7, 0.7, 0.7, 0.8, 0.8, 0.8, 0.8, 0.8,
    0.8, 0.8, 0.9, 0.9, 0.9, 0.9, 0.9, 0.9, 1.0, 1.0,
    1.0, 1.0, 1.0, 1.1, 1.1, 1.1, 1.1, 1.1, 1.2, 1.2,
    1.2, 1.2, 1.3, 1.3, 1.3, 1.4, 1.4, 1.4, 1.4, 1.5,
    1.5, 1.5, 1.6, 1.6, 1.6, 1.7, 1.7, 1.7, 1.8, 1.8,
    1.8, 1.8, 1.9, 1.9, 1.9, 1.9, 2.0, 2.0, 2.0, 2.1,
    2.1, 2.1, 2.1, 2.2, 2.2, 2.3, 2.3, 2.3, 2.4, 2.4,
    2.5, 2.6, 2.7, 2.8, 2.9, 3.1, 3.3, 3.6, 4.0, 4.6,
    5.1, 5.5, 10.49, 17.6,
)
"""Each event's own stream's width, over 60,225 events in the default folder's 66 recordings;
median 1.2 s, interquartile 0.8–1.9 s. Re-measured 2026-09-23: on the 84-recording folder
(70,543 events) the body sat within 0.1 s of this and the tail was longer, 12.06 s at the
99.99th percentile and 27.9 s at the maximum, against 10.49 s and 17.6 s here.

⚠ **The one place combined is not between its parents.** Its maximum is 17.6 s against slow's
5.5 s and its 99th percentile 4.6 s, so the top of this table is a thin tail rather than a
typical width. The widths are inherited from each contributing stream rather than produced by
combining, so the tail is a property of the fast/slow width columns that pooling exposes. It has
not been chased; locust is the only detector that reads it."""

REGIMES: dict[str, dict] = {
    "baseline_quiet": dict(bg_rate_hz=0.0071),
    "baseline_busy": dict(bg_rate_hz=0.0292),
}
"""Per-ROI **background** rates: the 25th and 75th percentiles of per-recording mean combined
rate, minus the coordinated share.

**Re-measured 2026-09-23 on the default folder's 66 recordings**, 64 of which clear the shape
floors: quiet 0.0071 Hz (0.007080) and busy 0.0292 Hz (0.029164), from 0.0072 and 0.0268 Hz;
`docs/learned/runs/2026-09-23-coordination-rates-senktide-ttx/`. The paragraph below
describes the 84-recording measurement.

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
    participation=(0.40, 0.25, 0.13),
    jitter_sec=0.150,
    distractor_frac=0.24,
    bg_rate_shape=MEASURED_RATE_SHAPE,
    bg_burst_shape=MEASURED_BURST_SHAPE,
    bg_burst_bin_sec=MEASURED_BURST_BINS,
)
"""The recording the combined bench scores on. Measured 2026-09-23; spacing and length remain the
fast bench's, as on slow.

**No elevated-rate stretch since 2026-09-25** (ADR-0009 decision 1): it inherits slow's
``hot_window=None``, and the stretch rate, ``hot_rate_hz`` below, moved to
:data:`ELEVATED_RATE_RECORDING`.

**Re-measured the same day on the default folder's 66 recordings:** ``n_roi`` 32 ROIs
(27–34.5), unchanged; the middle ``participation`` 0.25 (0.209–0.367), from 0.24;
``jitter_sec`` 0.150 s (0.136–0.164 s), from 0.148 s
(`docs/learned/runs/2026-09-23-jitter-correlogram-combined-senktide-ttx/`); ``hot_rate_hz``
0.1529 Hz, from 0.1464 Hz (`docs/learned/runs/2026-09-23-coordination-rates-senktide-ttx/`).
The outer participation levels and ``distractor_frac`` are chosen and did not move. The list
below gives the 84-recording values.

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

_SEARCH_2026_09_23 = ("search pick, docs/learned/runs/2026-09-23-full-search-combined-coact; "
                      "Tony asked for the third set 2026-09-22; AWAITING HIS REVIEW")

def _pick(name: str, **params) -> OperatingPoint:
    base = _fast.OPERATING_POINTS[name]
    return OperatingPoint(**{**vars(base), "params": {**base.params, **params},
                             "source": _SEARCH_2026_09_23})


OPERATING_POINTS: dict[str, OperatingPoint] = dict(_fast.OPERATING_POINTS)
OPERATING_POINTS["coact"] = _pick(
    "coact", alpha=1e-05, context_win_sec=120.0, min_rois=4, merge_gap_sec=8.0,
    guard_sec=8.0, window_mode="sliding")
OPERATING_POINTS["loco"] = _pick(
    "loco", threshold_pctile=99.9, bin_width_sec=0.5, context_win_sec=120.0,
    merge_gap_sec=8.0, min_rois=3, null_context_mode="maxlt", window_mode="sliding")
OPERATING_POINTS["rate"] = _pick(
    "rate", merge_gap_s=8.0, guard_sec=4.0, threshold_mode="additive", threshold_alpha=2.0)
OPERATING_POINTS["cicada"] = _pick(
    "cicada", n_synchronous_frames=5, sce_min_distance_frames=128, threshold_scope="global")

OPERATING_POINTS["sync"] = _pick(
    "sync", C_threshold=0.08, C_min=0.02, tau_max=0.25, max_gap=8.0, min_n=2,
    tau_mode="isi_adaptive", dt=0.05, detection_mode="threshold")

"""**Nothing here is adopted.** Tony asked for a third parameter set and has not reviewed one;
these are search picks carrying that in their ``source``. A combined setting reaches a real
recording only through a settings file with ``stream=combined`` rows, as slow's do.

Held-out mean F1 against the fast settings each search started from, on seeds nothing was chosen
on (``2026-09-23-full-search-combined-coact`` and ``-rest``):

==============  ========  ======  ====================
detector        shipped   pick    gain [95%]
==============  ========  ======  ====================
SPIKE-synch     0.666     0.797   **+0.131** [+0.119, +0.141]
LoCo            0.732     0.807   **+0.074** [+0.067, +0.083]
CoactDetect     0.718     0.781   **+0.063** [+0.054, +0.073]
locust          0.602     0.653   +0.051 [+0.040, +0.061]
rate+context    0.673     0.690   +0.017 [+0.012, +0.022]
binned SCE      0.571     —       nothing beat the start
==============  ========  ======  ====================

**SPIKE-synch's is installed as of 2026-09-23, and the route to it is worth reading**, because
the first search returned it in a form that could not be used and the second showed why that did
not matter.

The first pick (#754) had ``min_n`` **0.25** — an integer floor the search reached by halving,
the defect filed from the slow search and fixed in #755 — and ``C_min`` **0.0025** and ``dt``
**0.00625**, each at exactly **one eighth of its declared grid floor**, which is
``MAX_EXTENSIONS`` exhausted. None of the three was bracketed. It was withheld.

The rerun on the fixed search returned ``min_n`` **2**, a clean count, **with the gain unchanged**
— so the sub-integer floor had never been load-bearing. ``C_min`` and ``dt`` still ran to their
extension caps, and ``C_min`` came back at 0.0025 again: **the same value the slow search
produced**, which that thread diagnosed as a *plateau* rather than a climb, every value from 0 to
0.03 giving identical calls because the profile steps by about 1/31.

That diagnosis was then tested here rather than assumed, on the search's own held-out seeds:

===================================  ========  ==========
variant                              mean F1   vs shipped
===================================  ========  ==========
shipped                              0.666     —
pick as searched                     0.797     +0.131
pick, ``dt`` → 0.05 (grid floor)     0.797     +0.131
pick, ``C_min`` → 0.02 (grid floor)  0.797     +0.131
**pick, both → grid floors**         **0.797** **+0.131**
pick, both → shipped values          0.720     +0.054
shipped + ``max_gap`` 8 only         0.671     +0.005
===================================  ========  ==========

**Pinning both extended values back to their declared grid floors costs nothing at all.** The
extensions were cosmetic — the search walked a plateau and the edge rule could not tell. So the
installed point uses ``C_min`` 0.02 and ``dt`` 0.05, **every value on its own grid**, and keeps
the whole +0.131.

The gain is also **not** ``max_gap`` alone: 8 s on the shipped point is worth +0.005. It comes
from the combination, and mostly from ``dt`` and ``C_min`` sitting at their grid floors rather
than at the fast values (+0.077 of it).

⚠ **locust's ``sce_min_distance_frames`` 128** (12.8 s) is the same climb the fast and slow
searches both saw, which the slow handoff tied to the unsettled anchor question — *"not a setting
to ship until the anchor is settled."* It is installed here because nothing on this bench ships,
but it carries that flag with it.

**Three more things the table does not show.**

1. ⚠ **``min_rois`` 4 for CoactDetect sits just under the smallest planted level.** Combined
   participation is (0.40, 0.24, 0.13) of 32 ROIs — about 13, 8 and 4 participants — so a floor
   of 4 is on the bottom rung. That is the warning ``min_rois`` always carries: it can learn the
   simulation's planted participation rather than anything about tissue, and the gain looks the
   same either way.
2. **Two context windows went to the null rule's cap and stopped there**, CoactDetect's and
   LoCo's, both at 120 s. That is the rule stopping them rather than an interior optimum — the
   same shape LoCo's context showed on the slow bench, where the handoff recorded it as giving no
   evidence either way about what the stream wants.
3. **The starting point broke a budget for two of the six.** Round 1 moved CoactDetect's alpha
   and LoCo's threshold for that reason, logged in both runs. The fast settings, carried over as
   the search's origin the way slow's search carried them, are **not a neutral default on this
   bench** — so any comparison treating "the fast settings on combined" as a baseline is
   measuring against something this bench already refuses.

Only ``sce`` is unchanged: nothing in its grid beat the point it started from."""
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
    # Every recording carries its own ADR-0008 floor (`bench.with_floor`; ADR-0009).
    return _fast.with_floor(simulate_coordination(
        seed=seed, width_quantiles=MEASURED_WIDTH_QUANTILES, **{**spec, **overrides}))


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


ELEVATED_RATE_RECORDING = dict(_fast.ELEVATED_RATE_RECORDING, hot_rate_hz=0.1529)
"""The combined elevated-rate recording: fast's, at combined's stretch rate (the combined background
99th percentile, measured; see :data:`BENCH_RECORDING`). What it is for:
``bench.ELEVATED_RATE_RECORDING``."""


def make_elevated_rate_recording(regime: str, seed: int, **overrides):
    """The combined elevated-rate recording, on ``seed + ELEVATED_SEED_OFFSET``. Copy of ``bench``'s."""
    if regime not in REGIMES:
        raise ValueError(f"unknown regime {regime!r} — have {sorted(REGIMES)}")
    return _simulate(seed + ELEVATED_SEED_OFFSET,
                     {**BENCH_RECORDING, **REGIMES[regime], **ELEVATED_RATE_RECORDING}, overrides)


def run_detector(name: str, s, *, rng_seed: int = 20260706, floor: bool | None = None,
                 **overrides):
    """One detector on a slice at THIS module's operating point. Copy of ``bench``'s."""
    if name not in OPERATING_POINTS:
        raise ValueError(f"unknown detector {name!r} — have {sorted(OPERATING_POINTS)}")
    op = OPERATING_POINTS[name]
    params = _fast.floored_params(name, s, op.params, overrides, STREAM,
                                  floor)
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


def evaluate_elevated_rate(name: str, regime: str, seeds=(1, 2, 3), *, tol_sec: float = TOL_SEC,
                           **overrides) -> ProbeResult:
    """Calls on the combined elevated-rate recording, inside and outside the stretch. Copy of
    ``bench``'s."""
    return _fast.probe_counts(make_elevated_rate_recording, run_detector, name, regime, seeds,
                              tol_sec=tol_sec, **overrides)


def evaluate(name: str, regime: str, seeds=(1, 2, 3), *, tol_sec: float = TOL_SEC,
             gen: dict | None = None, probe: bool = True, **overrides) -> BenchResult:
    """One detector over several combined recordings, pooled. Copy of ``bench``'s."""
    gen = gen or {}
    scores = []
    for seed in seeds:
        s, gt = make_recording(regime, seed, **gen)
        det = run_detector(name, s, **overrides)
        scores.append(score_stream(gt, det, tol_sec=tol_sec))
    pr = None
    if probe:
        g = {k: v for k, v in gen.items() if k not in ELEVATED_RATE_RECORDING}
        pr = _fast.probe_counts(lambda r, sd: make_elevated_rate_recording(r, sd, **g),
                                run_detector, name, regime, seeds, tol_sec=tol_sec, **overrides)
    return pool_scores(scores, detector=name, regime=regime, seeds=seeds,
                       knob_value=overrides.get(OPERATING_POINTS[name].knob), probe=pr)


BACKGROUND_GRID = (0.0028, 0.0045, 0.0071, 0.0114, 0.0182, 0.0292, 0.0440, 0.0660)
"""Per-ROI combined background rates to report a score across, built as ``bench.BACKGROUND_GRID``.

Quiet (0.0071 Hz) and busy (0.0292 Hz) are on it, two interior points step about 1.6x
between them, two points above busy step 1.5x, and below quiet it reaches **0.0028 Hz**.
Added 2026-09-23, when the group run on the 66 recordings showed the two regimes are the
spread *between* groups: ORX's combined background runs 0.0029–0.0116 Hz and DI's
0.0237–0.0380 Hz (interquartile; `docs/learned/runs/2026-09-23-groups-rates-comod-66/`).
The grid covers every group's interquartile range, which ``tests/test_background_curve.py``
checks against that record. A reporting axis only: operating points are still tuned at quiet
and busy."""


def evaluate_background_curve(name: str, regime: str, seeds=(1, 2, 3), *,
                              rates=BACKGROUND_GRID, tol_sec: float = TOL_SEC,
                              gen: dict | None = None, **overrides) -> dict[float, BenchResult]:
    """One :class:`BenchResult` per combined background rate; see ``bench.evaluate_background_curve``."""
    return _fast.background_curve(make_recording, run_detector, OPERATING_POINTS, name,
                                  regime, seeds, rates=rates, tol_sec=tol_sec, gen=gen,
                                  **overrides)


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
