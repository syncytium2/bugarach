"""Score all six detectors against planted truth, at declared operating points.

**One of the six is keyed ``cicada`` and named locust.** The key is the value in
``detections.csv``'s ``detector`` column — output contract — and *locust* is what
every screen, figure and report says. Same detector; ``bugarach.detectors.cicada``
carries the three-way split between the key, the name, and CICADA the upstream
tool.

Stage 3 of [`docs/simulation_plan.md`](../../docs/simulation_plan.md): the
sensitivity bench, and the regime-shift guard the plan calls the single
highest-value item on that page — *the precision-collapse figure is a test that
was drawn as a picture.* Here it is an assertion.

Two things this module refuses to do, both of them traps the project already
paid for.

**It will not run a detector at whatever its signature defaults to.** Those
defaults are not all calibrated operating points, and the difference is not
small: `coact_detect` defaults to the MATLAB function's `alpha=0.01`, where it
scores **F1 0.72** on the sparse regime, while explore_sce's FAST point
(`alpha=1e-4`, `int_win_sec=2.0`) scores **1.00**. A bench that read the
signature would have published the first number as CoactDetect's performance.
So every operating point is declared here with its provenance, and
:data:`OPERATING_POINTS` is the one place that changes when a calibration does.

**It will not report an optimum that sits on the edge of the grid it searched.**
An optimum at the boundary means the search was too narrow and the real one is
outside it; upstream published such a point once. :func:`pick_operating_point`
raises instead.

The scoring rule is interval-based (see :mod:`bugarach.score`) — binned
detectors report spans, and matching their bin edge against a planted onset
scores a correct detector at zero.
"""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np

from bugarach.detectors.cicada import cicada_detect
from bugarach.detectors.coact import coact_detect
from bugarach.detectors.loco import loco_detect
from bugarach.detectors.rate import (
    rate_detect,
    recording_extent,
    stream_trains,
)
from bugarach.detectors.sce import sce_detect
from bugarach.detectors.sync import sync_detect
from bugarach.score import TOL_SEC, score_stream
from bugarach.simulate import simulate_coordination

STREAM = "events"
"""The single-stream slice the generator emits (FOUNDATIONS §3)."""

FLOORED_SETTING = {"coact": "min_rois", "loco": "min_rois", "sce": "min_rois", "sync": "min_n"}
"""The setting each detector's participation minimum lives in, which ADR-0008 sets and no search
does (ADR-0008 decision 6; ADR-0009 decision 3 for SPIKE-synch's ``min_n``). rate+context and
locust have no participation minimum, so the floor reaches them only through the scorer."""

FLOOR_LABEL = "ADR-0008 per-window floor, bench per ADR-0009"
"""What every run record scored under this module's floor says about it."""

FLOOR_CACHE_ENV = "BUGARACH_FLOOR_CACHE"
"""A folder where :func:`recording_floor` keeps each recording's floor, keyed by its events. A
search sets it so its workers compute each floor once between them, not once each."""

FLOOR_SWITCH_ENV = "BUGARACH_BENCH_FLOOR"
"""Set to ``off`` to build and score this bench pre-ADR-0008: no floor recorded on a recording,
none injected into a detector. For tests that pin a measurement made before 2026-09-25 or that
exercise detector mechanics the floor has nothing to do with, and for reproducing earlier runs.
Anything run this way is pre-ADR-0008 and says so."""

_FLOORS: dict = {}


def floor_enabled() -> bool:
    """Is ADR-0008's floor on for this bench (the default)? Read at every call."""
    import os

    return os.environ.get(FLOOR_SWITCH_ENV, "on").strip().lower() not in ("off", "0", "false")


def _floor_key(s, stream: str):
    import hashlib

    ext = recording_extent(s)
    trains = stream_trains(s.streams[stream], ext)
    dt = s.require_dt()
    h = hashlib.sha256(repr((stream, float(dt), float(ext[0]), float(ext[1]))).encode())
    for t in trains:
        h.update(np.asarray(t, dtype=np.float64).tobytes())
        h.update(b"|")
    return h.hexdigest()[:32], trains, ext, dt


def recording_floor(s, stream: str = STREAM):
    """ADR-0008's floor for one simulated recording, from that recording's own events.

    ADR-0008 decision 5: every bench recording gets its floor from its own null, exactly as a real
    window does. ADR-0009 decision 1: nothing is left out of it, the elevated-rate stretch
    included. The null is seeded by a digest of the recording's events, so the same recording
    always gets the same floor, in any process. Returns a
    :class:`bugarach.event_floor.Floor`.
    """
    import json
    import os
    from pathlib import Path

    from bugarach import event_floor as ef

    key, trains, ext, dt = _floor_key(s, stream)
    if key in _FLOORS:
        return _FLOORS[key]
    cache = os.environ.get(FLOOR_CACHE_ENV)
    path = Path(cache) / f"{key}.json" if cache else None
    if path is not None and path.exists():
        try:
            f = ef.Floor(**{k: v for k, v in json.loads(path.read_text()).items()
                            if k != "stable"})
            _FLOORS[key] = f
            return f
        except (OSError, ValueError, TypeError):
            pass                              # a half-written file: compute it again
    frames = [np.unique(np.floor((np.asarray(t, float) - ext[0]) / dt + 1e-9).astype(np.int64))
              for t in trains]
    n_frames = int(round((ext[1] - ext[0]) / dt))
    f = ef.window_floor(frames, n_frames, dt, key=("bench", stream, key))
    _FLOORS[key] = f
    if path is not None:
        path.parent.mkdir(parents=True, exist_ok=True)
        tmp = path.with_suffix(f".{os.getpid()}.tmp")
        tmp.write_text(json.dumps(f.as_dict()))
        try:
            os.replace(tmp, path)
        except PermissionError:
            # Windows refuses a replace while another process holds the target — which happens
            # when two workers compute the same recording's floor at once. The floor is a
            # function of the recording, so the file already there holds the same number.
            # Seen in phase 3 of 2026-09-25 (score_bench_candidates.py, 44 workers).
            tmp.unlink(missing_ok=True)
            if not path.exists():
                raise
    return f


def with_floor(pair, stream: str = STREAM):
    """``(slice, ground_truth)`` with the recording's floor recorded in ``gt.params``, where
    :func:`bugarach.score.score_detections` reads it (ADR-0009 decision 2)."""
    s, gt = pair
    if not floor_enabled():
        return s, gt
    f = recording_floor(s, stream)
    gt.params["event_floor"] = f.floor
    gt.params["event_floor_detail"] = f.as_dict()
    return s, gt


def floored_params(name: str, s, op_params: dict, overrides: dict, stream: str,
                   floor: bool | None) -> dict:
    """The operating point's ``op_params`` with ``overrides`` applied and the detector's
    participation minimum set to the recording's floor.

    An override of that setting to anything but the operating point's own value is refused while
    the floor is on: ADR-0008 sets it, and a caller who wants the pre-ADR-0008 behaviour says so
    with ``floor=False``. Passing the operating point's parameters through unchanged, as the
    search's crowded reference does, is not an override and is allowed.
    """
    params = {**op_params, **overrides}
    setting = FLOORED_SETTING.get(name)
    if floor is None:
        floor = floor_enabled()
    if not floor or setting is None:
        return params
    if setting in overrides and overrides[setting] != op_params.get(setting):
        raise ValueError(f"{name}.{setting} is set by ADR-0008's per-recording floor, not by a "
                         f"caller; pass floor=False to run at {setting}={overrides[setting]!r}")
    return {**params, setting: int(recording_floor(s, stream).floor)}


MEASURED_PROVENANCE = (
    "constellation/coordination_timescale_summary.csv — flavour 'all-baseline', "
    "fast stream, min_rois=4 (the file's own headline_K). 84 slices. Produced by "
    "interface2 measure_coordination_timescale.m: roiRate = events/win_dur (Hz "
    "per ROI), jit_obs = median within-cluster onset SD (s), partN_obs = median "
    "participating ROIs per cluster."
)
"""Where the recording's structural values come from.

Recorded as a string rather than a comment because a bench whose settings have
no traceable origin cannot be re-derived when the measurement is revised, and
this one **is** revisable: `optim_history/README.md` marks the whole campaign
PROVISIONAL, and notes that the calibrated settings were adopted on 2026-08-05
*without* the real-data validation the deck named as the deciding step. These
numbers are measurements; the decision that rested on them was never checked.

**Re-measured 2026-09-17 on the one folder the current program allows**
(:data:`MEASURED_ROLE`), and none of the bench's measured values moved outside its
bootstrap interval. The string above still names where the values were *first*
taken from; :data:`MEASURED_RECORD` is where they were last *checked*, and
``tests/test_bench_is_measured_on_the_declared_folder.py`` fails when the two
stop agreeing.
"""

MEASURED_ROLE = "default"
"""The ``current_export.toml`` role every measured value in this module is checked
against — **the default dataset**, resolved through ``dataset.default_role()``.

Tony, 2026-09-17: *"you should only work from the steps excluded folder. it is
terrifying that you might use other data."* The same day it turned out that the
bench's background shapes had been fitted on a closed ``.mat`` archive and its
structural values taken from a MATLAB summary, and nothing had noticed, because a
provenance string is prose. A role name is not prose: ``tools/remeasure_bench.py``
resolves it, writes the folder it actually read into :data:`MEASURED_RECORD`, and
the test compares that folder with what the pointer declares today. A new export
under this role turns the suite red until the bench is re-measured on it.

**It was the literal ``"steps_excluded"`` until 2026-09-22**, which outlived the folder:
that role became an ``archive`` on 2026-09-21 and declares a contamination, so the bench
was pinned to a folder no analysis may read, and ``tools/check_scored_dataset.py`` flagged
it at every session start. Naming ``"default"`` puts the bench on the one folder the person
confirms each session, and leaves ``current_export.toml`` as the only place that choice is
written down — which is why the two entries this module and its tool held in
``ROLE_LITERAL_ALLOWED`` (``tests/test_where_the_data_are.py``) came out with the move.

A role, not a folder name, because folder names are declared in
``current_export.toml`` and nowhere else in code
(``tests/test_where_the_data_are.py``).
"""

MEASURED_STREAM = "fast"
"""The stream every measured value comes from. The slow stream gets its own bench
later (goals README, *The current program*, decision 4)."""

MEASURED_RECORD = "docs/learned/bench_measured.json"
"""Repo-relative path of the last re-measurement: the folder read, each value with
its 95% bootstrap interval, and whether the constant in this module sits inside it.
Written by ``tools/remeasure_bench.py``."""

MIN_BASELINE_SEC = 900.0
"""A baseline window shorter than **15 minutes** is not measured. Tony, 2026-09-17:
*"baselines shorter than 15 minutes should be ignored. they probably should not have been
exported."*

**It is a ruling, not a filter this repo derived**, and the distinction is the one CLAUDE.md
draws in terms: which recordings are analysable is the producer's call, and a consumer that
re-derives an exclusion has already made the error that once dropped a recording the lab had
not withdrawn. So this threshold is Tony's, recorded where the code can apply it, and the
place it really belongs is the exporter — *"they probably should not have been exported"*.
He also said not to dwell on it, so nothing here goes looking through the folder for more.

**Nothing in the current folder is affected.** Every baseline in the declared
``steps_excluded`` folder is at least 17.0 minutes, raw period and scored window alike, so
applying this changes no number measured before 2026-09-17. It is a guard against the next
folder, and a tool that drops a window under it says which and why rather than quietly
measuring fewer recordings.

Not to be confused with ``region_min_sec`` in the detectors' own signatures, which is the
MATLAB windowing rule for store input (FOUNDATIONS §4) and happens to carry the same 900 s.
"""

MEASURED_OUTSIDE_INTERVAL: dict[str, str] = {}
"""Measured constants knowingly left outside their interval, each with the reason and
who decides. The test fails for any constant outside its interval that is not listed
here, and for any entry here whose constant has come back inside.

Empty since 2026-09-22. It held ``participation`` from 2026-09-17, where the bench's
0.18 sat just under a 95% interval starting at 0.1818 — a rounding of 6/33 rather than a
moved measurement, but moving it moves every number the bench produces, so it waited for
Tony. The meeting approved 0.19 and it was adopted with the jitter in the same pass."""

MEASURED_RATE_SHAPE = 0.291
"""Gamma shape of the per-ROI background rate in real baseline windows.

**Re-measured 2026-09-23 on the default folder's 66 recordings**, over the
63 baseline windows that clear the shape fit's floors: 0.291 [0.226, 0.404], from
0.275 on the 84-recording folder. Every measured constant in this module moved in the
same pass, on Tony's instruction to retune the bench on the data set it scores
(`docs/learned/bench_measured.json`). The counts quoted below describe the
84-recording fit.

Fitted, not chosen: within a window the ROI rate is modelled as
``Gamma(shape, mean/shape)`` and the observed count as Poisson over that rate —
Negative Binomial marginally — and this is the maximum-likelihood shape over
**81 baseline windows / 2 643 ROIs**, each window keeping its own mean because
untreated slices genuinely differ several-fold. Re-derive with
``python tools/fit_background_shape.py`` (needs ``$BUGARACH_DATA_ROOT``); the
tool prints the fit and says whether the tree's value still matches the data.

The number worth looking at is not the shape but what it reproduces. Real
windows leave **35%** of ROIs with no event at all, at a median 1.7 mHz, and
reach 486 mHz. Drawing rates at this shape leaves **38%** silent at a median of
1.7. The silent ROIs are **not modelled** — there is no zero-inflation term
here. They are what a low rate drawn from the tail produces over a finite
window, which is the reason to believe the shape rather than merely accept it.
A flat field at the same mean leaves 2% silent at a median of 10.0 mHz.

⚠ The tail overshoots: the fit reaches ~847 mHz where the data reaches 486. A
Gamma is the simplest distribution that produces the silence and the skew
together; it is not the last word on the busiest ROIs.

**Wired into the bench 2026-08-28.** ``BENCH_RECORDING`` carries this shape, so
every score in this package is measured on a heterogeneous field. It was held
back for one reason — leaving it ``None`` kept the RNG stream identical, so old
seeds reproduced — and Tony spent that: *"all the benchmarks have changed because
the bench is changed."* Numbers published before that date were measured on a
flat field and are not comparable to numbers after it.
"""

MEASURED_BURST_SHAPE = (1.770, 1.439)
"""Gamma shapes of the per-bin rate multiplier, for `MEASURED_BURST_BINS`.

**Re-measured 2026-09-23 on the 66 recordings**: 1.770 [1.320, 2.282] at 300 s and
1.439 [1.062, 1.957] at 60 s, from (1.547, 1.388). The fit description below is the
original one.

The temporal partner of `MEASURED_RATE_SHAPE`, and the same estimator turned
ninety degrees. There, ROIs differed from one another. Here **one ROI is followed
across time bins**: under a constant rate its counts would be Poisson with
variance equal to mean, and a bursty ROI is over-dispersed. Fixing the ROI is
what makes the estimate clean — rate heterogeneity across ROIs is held constant
inside one of them, so the over-dispersion left over is temporal.

Maximum likelihood over the ROIs carrying at least 10 events in their baseline
window (784 of them, across 85 windows), each ROI keeping its own mean.
Re-derive with `python tools/fit_background_shape.py`.

**Two scales, because one cannot work.** A single bin width draws independent
bins, so its over-dispersion stops growing once the window exceeds the bin. Real
ROIs keep getting more over-dispersed the wider you look:

| variance/mean | 30 s | 60 s | 120 s | 300 s |
|---|---|---|---|---|
| real | 1.82 | 2.61 | 3.88 | 5.69 |
| flat background | 0.99 | 0.95 | 0.93 | 0.74 |
| these two scales | 1.87 | 2.76 | 3.04 | 4.44 |

Fine scales are reproduced; the coarse end is still short, so a busy stretch of
several minutes is shorter here than in real tissue.

⚠ The two shapes are fitted **per scale independently** and then multiplied. A
joint fit would not give these two numbers, and the agreement above is partly
that approximation being forgiving. It is an approximation on purpose — the
joint likelihood has no closed form — and it is why the coarse end is the half
that misses.

**Wired into the bench 2026-08-28**, with `MEASURED_RATE_SHAPE`. Both axes of
`BENCH_RECORDING`'s background are now the fitted ones; see that constant for
what switching them cost and who decided to spend it.
"""

MEASURED_BURST_BINS = (300.0, 60.0)
"""Bin widths (s) the shapes in `MEASURED_BURST_SHAPE` were fitted at."""

CONTEXT_GRID_SEC = (20.0, 30.0, 45.0, 60.0, 90.0, 120.0)
"""The context windows searched for CoactDetect, LoCo and rate+context (ADR-0009 decision 5): none
longer than 120 s, the bench's own cap (:func:`context_fits_the_null`), and short ones so a search
can find a short context where one works."""

GUARD_MAX_CONTEXT_FRACTION = 0.25
"""A guard may cover at most this fraction of the context it sits in (the final-parameters
runbook, 2026-09-24). It binds wherever a guard grid reaches past a quarter of a short
context: slow and combined's 8 s guard at 20 s and 30 s, fast LoCo's 2 and 4 s guards at 5 s;
:func:`settings_are_valid` enforces it."""

FULL_GRIDS: dict[str, dict[str, tuple]] = {
    "loco": {
        "threshold_pctile": (97.0, 98.0, 99.0, 99.5, 99.9, 99.99),
        "bin_width_sec": (0.5, 1.0, 2.0, 3.0, 5.0),
        "context_win_sec": CONTEXT_GRID_SEC,
        "merge_gap_sec": (0.5, 1.0, 2.0, 4.0, 8.0),
        "null_context_mode": ("maxlt", "symmetric"),
        "guard_sec": (0.0, 0.5, 1.0, 2.0, 4.0),
        "detection_mode": ("threshold", "peak"),
        "peak_prominence": (0.0, 0.25, 0.5, 1.0, 2.0),
        "peak_min_distance_sec": (0.0, 0.5, 1.0, 2.0, 5.0),
    },
    "sync": {
        "C_threshold": (0.02, 0.04, 0.06, 0.08, 0.1, 0.12, 0.16),
        "C_min": (0.02, 0.05, 0.1, 0.15, 0.2),
        "tau_max": (0.1, 0.25, 0.5, 1.0, 2.0),
        "max_gap": (0.1, 0.25, 0.5, 1.0, 2.0),
        "tau_mode": ("isi_adaptive", "fixed"),
        # The profile's own bin width, NOT the recording's frame interval (FOUNDATIONS §6).
        "dt": (0.05, 0.1, 0.2, 0.5),
        "detection_mode": ("threshold", "peak"),
        "peak_prominence": (0.0, 0.01, 0.02, 0.05, 0.1),
        "peak_min_distance_sec": (0.0, 0.5, 1.0, 2.0, 5.0),
    },
    "coact": {
        "alpha": (1e-2, 3e-3, 1e-3, 3e-4, 1e-4, 3e-5, 1e-5, 1e-6),
        "int_win_sec": (0.5, 1.0, 2.0, 3.0, 5.0),
        "context_win_sec": CONTEXT_GRID_SEC,
        "merge_gap_sec": (0.0, 1.0, 2.0, 3.0, 5.0, 8.0),
        "guard_sec": (0.0, 0.5, 1.0, 2.0, 4.0),
        "guard_norm": ("compact", "exposure"),
        "detection_mode": ("threshold", "peak"),
        "peak_prominence": (0.0, 0.25, 0.5, 1.0, 2.0),
        "peak_min_distance_sec": (0.0, 0.5, 1.0, 2.0, 5.0),
    },
    "rate": {
        "excess_threshold_hz": (3.0, 3.5, 4.0, 4.5, 5.0, 6.0, 8.0),
        "context_win": CONTEXT_GRID_SEC,
        "rate_win": (0.5, 1.0, 2.0, 3.0, 5.0),
        # ⚠ Starts at 0.1 s, not 0: at and below 0.001 s this detector returns NO calls at
        # all, which is a defect rather than a setting —
        # docs/todo/2026-09-17-rate-context-returns-nothing-at-a-zero-merge-gap.md.
        "merge_gap_s": (0.1, 0.5, 1.0, 2.0, 3.0, 5.0, 8.0),
        "guard_sec": (0.0, 0.5, 1.0, 2.0, 4.0),
        "threshold_mode": ("additive", "multiplicative"),
        "threshold_alpha": (1.5, 2.0, 3.0, 4.0),
        "detection_mode": ("threshold", "peak"),
        "peak_prominence": (0.0, 0.25, 0.5, 1.0, 2.0),
        "peak_min_distance_sec": (0.0, 0.5, 1.0, 2.0, 5.0),
    },
    "sce": {
        "threshold_pctile": (70.0, 75.0, 80.0, 85.0, 90.0, 95.0, 98.0, 99.0, 99.5),
        "bin_width_sec": (2.0, 5.0, 10.0, 15.0, 20.0, 30.0),
        # Shipped is NaN, which means "do not merge". NaN is not a grid value: the search
        # carries it as the starting state, and this grid is what it may move to.
        "merge_gap_sec": (0.0, 5.0, 10.0, 15.0, 20.0, 30.0),
        "detection_mode": ("threshold", "peak"),
        "peak_prominence": (0.0, 0.25, 0.5, 1.0, 2.0),
        "peak_min_distance_sec": (0.0, 1.0, 2.0, 5.0, 10.0),
    },
    "cicada": {
        "sce_percentile": (99.9, 99.95, 99.99, 99.995, 99.999, 99.9995, 99.9999),
        "n_synchronous_frames": (1, 2, 3, 5, 10),
        "sce_min_distance_frames": (1, 2, 4, 8, 16),
        "threshold_scope": ("global", "regional"),
    },
}
"""The values each detector's settings are searched over — **one declaration, both
machines**.

**Per axis, never a product.** The search that reads this
(``tools/search_all_settings.choose_settings``) moves one setting at a time with the rest
held at the current best, so what it visits is a **sum** over axes. A product of these
axes is not runnable, and no caller should build one: goal 2's nested cross-validation
calls the search inside each outer fold instead of enumerating a grid
(``docs/todo/2026-09-17-how-is-the-coded-side-searched-inside-nested-cross-validation.md``,
option A, decided 2026-09-17).

**Two consumers, one list, on purpose.** Goal 1 searches these for the values the
detectors ship at; goal 2 searches the same axes inside each of its outer folds, so the
comparison tunes the coded side over the space the shipped values came from. Two copies of
a grid is how the two machines came to tune different things on 2026-09-16.

**Every knob the bench can see, since 2026-09-17** (goal 1 step 3). Widened from the four
declared settings per detector to every parameter a detector takes bar the data's own —
the merge gaps, the guards, the peak-mode group and the categorical axes. ``min_rois`` was one
of them until 2026-09-25, when ADR-0008's floor took it (and SPIKE-synch's ``min_n``) out.
What is deliberately NOT here is in :data:`NOT_SEARCHED`, each with the reason, because a
parameter left out silently is a parameter nobody knows was left out.

**Each axis was probed before it was declared.** A parameter that cannot move this bench's
answer is not tunable here, and searching it anyway would report coverage nobody has. Three
of the probes found more than they were looking for: ``rate``'s merge gap returns no calls
at all at zero, ``sce``'s participation floor does nothing below about 8, and
``sync``'s ``synchrony_statistic`` is inert because the generator never puts two events on
the same timestamp. The first and third are filed as todos.

**Categorical and conditional axes.** Some axes are names rather than numbers
(``detection_mode``, ``tau_mode``, ``guard_norm``, …): a search must not extend them and an
"edge" means nothing on them. Others apply only under another setting — the peak-mode pair
under ``detection_mode="peak"``, ``guard_norm`` under a nonzero guard, ``threshold_alpha``
under multiplicative thresholding. :func:`setting_applies` is that rule, and a search that
varies an axis its parent has switched off is measuring nothing.
"""

NOT_SEARCHED: dict[str, dict[str, str]] = {
    "coact": {
        "window_mode": "a decision, not a score: sliding is chosen because calls should not "
                       "move with the grid (forks.md §14), which F1 on this bench cannot see",
        "min_rois": "set per recording by ADR-0008's floor (decision 6), in run_detector",
    },
    "loco": {
        "window_mode": "as coact",
        "min_rois": "as coact",
    },
    "sce": {
        "min_rois": "as coact",
        "analysis_mode": "measured inert: 'whole' and 'regional' give identical output on "
                         "bench recordings, which carry one implicit window",
        "surrogate_model": "only 'circular_shift' is implemented; 'jitter' raises",
    },
    "sync": {
        "min_n": "a participation minimum, so set by ADR-0008's floor (ADR-0009 decision 3)",
        "synchrony_statistic": "measured inert: it aggregates ROIs sharing an EXACT "
                               "timestamp, and the generator draws times continuously so "
                               "ties never happen. Live on real data, which is frame-"
                               "quantized — docs/todo/2026-09-17-the-bench-does-not-put-"
                               "events-on-the-frame-grid.md",
        "artifact_threshold": "measured inert on the bench at 0.7 and 0.95: the artifact "
                              "gate never engages on simulated recordings. It guards real "
                              "data",
        "artifact_threshold_fraction": "as artifact_threshold",
        "artifact_threshold_plat90": "as artifact_threshold",
    },
    "cicada": {
        "active_duration_mode": "settled by FOUNDATIONS §7: locust reads the event's own "
                                "width column. 'If you find yourself asking which duration "
                                "locust should use, the answer is the column'",
        "active_duration_sec": "as active_duration_mode",
    },
}
"""Parameters deliberately left out of :data:`FULL_GRIDS`, and why.

Three classes are excluded across every detector and are not repeated here: **the data's
own** (the events, the time range, the frame interval, column names, seeds, output
switches); **the region rules** (``solution_delay_sec``, ``baseline_window_max_sec``,
``treatment_window_sec``, ``region_min_sec``, ``clamp_context_to_region``), because an
export folder's ``regions.csv`` is used as delivered (FOUNDATIONS §4); and **surrogate
counts** (``n_surrogates``, ``thr_step_sec``), which trade compute for precision and are set
by checking that the calls stop changing, not by chasing an F1.

What is listed above is the rest: per detector, the parameter and the measured or decided
reason it is not searched. A reader who wants to know whether a setting was tuned should be
able to find it in one of the two places rather than in neither.
"""


def setting_applies(det: str, setting: str, params: dict) -> bool:
    """Does this setting do anything, given the rest of them?

    A conditional axis under a parent that is switched off is not a setting, it is dead
    weight: varying it costs a search real evaluations and returns identical answers, and a
    readout that lists it as searched is wrong. The three conditions here are the detectors'
    own, read off their code.
    """
    if setting in ("peak_prominence", "peak_min_distance_sec"):
        return params.get("detection_mode") == "peak"
    if setting == "guard_norm":
        return float(params.get("guard_sec", 0.0) or 0.0) > 0.0
    if setting == "threshold_alpha":
        return params.get("threshold_mode") == "multiplicative"
    return True

FULL_GRID_PAIRS: dict[str, tuple[str, str]] = {
    "sce": ("threshold_pctile", "bin_width_sec"),
    "loco": ("threshold_pctile", "context_win_sec"),
    "cicada": ("sce_percentile", "n_synchronous_frames"),
}
"""Pairs worth walking as a full two-setting grid, where one setting's best depends on
where the other sits. A coordinate search can miss a diagonal ridge, and these are the
ridges this project has met. Optional for a caller: goal 2 leaves them off inside a fold,
because a pair is a product and it pays for one per fold."""


def context_fits_the_null(p: dict, min_sep_sec: float) -> bool:
    """Is this setting's context window narrow enough for the null to be background only?

    A detector estimates its threshold over a context window. If planted events are spaced
    more tightly than that window, the window holds OTHER events, and the null the threshold
    comes from is contaminated with the very thing being detected — the trap that made the
    first upstream benchmark unusable and cost two weeks of tuning against it
    (:data:`BENCH_RECORDING`, ``min_sep_sec``).

    **It also flatters the setting that breaks it**, which is why a search needs this rule
    and not only a test. A contaminated null sits too high, so the detector calls less,
    precision rises and F1 with it. On 2026-09-17 the sliding search chose a 240 s context
    for both LoCo and CoactDetect on a bench that plants events 120 s apart, under all four
    budgets; ``tests/test_bench.py::test_the_bench_recording_keeps_the_null_clean`` refused
    the result. The guard worked and the run was already spent.

    ``min_sep_sec`` is the SCORED recordings' spacing, so a caller scoring something other
    than :data:`BENCH_RECORDING` passes its own — goal 2's home spec plants at 171 s, and its
    per-fold search binds this rule with that number.
    """
    context = p.get("context_win_sec", p.get("context_win"))
    return context is None or context <= min_sep_sec


def guard_fits_the_context(p: dict) -> bool:
    """A guard of at most :data:`GUARD_MAX_CONTEXT_FRACTION` of its context window."""
    context = p.get("context_win_sec", p.get("context_win"))
    guard = float(p.get("guard_sec", 0.0) or 0.0)
    return context is None or guard <= GUARD_MAX_CONTEXT_FRACTION * float(context)


def settings_are_valid(det: str, p: dict) -> bool:
    """Do these settings make sense together?

    Rejects a context window shorter than what fills it, and a floor above its own
    threshold. It lives here rather than in the search so that a caller walking
    :data:`FULL_GRIDS` rejects the same combinations this project's own search does.
    """
    # Sliding supports threshold detection only, in both detectors that have the mode: a
    # sliding window has no bins to find a peak across (`loco.py`, `coact.py`). Encoded so a
    # search in sliding mode does not spend evaluations on a pair the detector will refuse.
    if p.get("window_mode") == "sliding" and p.get("detection_mode", "threshold") != "threshold":
        return False
    # Before any detector's own branch: until 2026-09-25 this sat after LoCo's early return, so
    # the guard cap never reached LoCo: on the final-parameters night fast LoCo's search, at a 5 s
    # context, could try guards of 2 and 4 s against a 1.25 s cap (murderboard roles 1 and 7).
    if not guard_fits_the_context(p):
        return False
    if det == "loco":
        # The detector's own refusal, encoded here so a search does not spend an evaluation
        # discovering it: a guard is supported only with the one-sided 'maxlt' null, because
        # under 'symmetric' the guard would hole the middle of the window and the wrap would
        # cross the hole (`loco.py`). Found by the 2026-09-17 every-knob search, the first
        # thing ever to cross those two axes.
        if p.get("guard_sec", 0.0) and p.get("null_context_mode", "maxlt") != "maxlt":
            return False
        return (p["bin_width_sec"] * 4 <= p["context_win_sec"]
                and p["merge_gap_sec"] < p["context_win_sec"])
    if det == "coact":
        return p["int_win_sec"] * 4 <= p["context_win_sec"]
    if det == "rate":
        return p["rate_win"] * 4 <= p["context_win"]
    if det == "sync":
        return p["C_min"] <= p["C_threshold"]
    return True


def measured_constants() -> dict[str, float]:
    """Every value in this module that claims to be measured off real recordings.

    One table, so ``tools/remeasure_bench.py`` measures exactly these and the test
    checks exactly these. A measured constant added to the bench and not added
    here is a constant nobody re-checks, so add it here in the same change.

    ``participation`` is the middle level of ``BENCH_RECORDING["participation"]``,
    which its docstring derives as median participants over median ROI count.
    """
    return {
        "rate_shape": MEASURED_RATE_SHAPE,
        **{f"burst_shape_{b:.0f}s": s
           for b, s in zip(MEASURED_BURST_BINS, MEASURED_BURST_SHAPE)},
        "regime_quiet_hz": REGIMES["baseline_quiet"]["bg_rate_hz"],
        "regime_busy_hz": REGIMES["baseline_busy"]["bg_rate_hz"],
        "n_roi": float(BENCH_RECORDING["n_roi"]),
        "jitter_sec": BENCH_RECORDING["jitter_sec"],
        "participation": BENCH_RECORDING["participation"][1],
    }


@dataclass(frozen=True)
class OperatingPoint:
    """One detector, the settings it is benched at, and where they came from.

    ``knob`` and ``grid`` define the sensitivity axis: the parameter swept to
    trace a detection curve, and the values swept over. The grid must bracket
    the operating point — if the F1-optimum lands on an end of it, the search
    was too narrow and :func:`pick_operating_point` says so rather than
    reporting the boundary as an answer.
    """

    params: dict
    source: str
    knob: str
    grid: tuple
    takes_rng: bool = True

    def with_knob(self, value) -> dict:
        return {**self.params, self.knob: value}


# Provenance matters more than the numbers: a bench whose settings have no
# recorded origin cannot be compared to constellation/'s MATLAB campaign, and
# cannot be re-derived when a calibration moves.
#
# **All six swept knobs were retuned together on 2026-09-16** by
# `tools/retune_operating_points.py` (RETUNE below): 48 bench recordings per point on
# both backgrounds and on the empty recording, grids widened until no optimum sat on
# an edge, candidates limited to values under BOTH false-alarm budgets
# (MAX_PROBE_PER_MIN on both backgrounds, MAX_FALSE_POSITIVES_PER_HOUR), the best by F1
# averaged over the two backgrounds — and a stored value moved ONLY where the gain's
# 95% bootstrap interval excludes zero. Three moved (sce, loco, rate); three were
# already best or within noise (coact, sync, cicada). Figure and numbers:
# <darkroom>/bugarach/2026-09-16-best-parameters/. Only the one swept knob per
# detector was searched; every other parameter below is as it was.
RETUNE = ("tools/retune_operating_points.py 2026-09-16 (48 recordings per point, both "
          "backgrounds, both false-alarm budgets, mean F1, moved only if the 95% "
          "bootstrap gain interval excludes zero)")
SLIDING_SEARCH = (
    "tools/search_all_settings.py --sliding, 2026-09-17 "
    "(<darkroom>/bugarach/2026-09-17-full-search/sliding5/): every parameter this bench can "
    "see, one at a time in rounds, chosen on 48 recordings per background and scored on 48 "
    "the search never saw, under FOUR budgets — the two false-alarm limits, the precision "
    "swing, and MAX_CROWDED_DROP against what the detector ships at today — and refusing any "
    "context window wider than the planted spacing (context_fits_the_null)")
OPERATING_POINTS: dict[str, OperatingPoint] = {
    "loco": OperatingPoint(
        # SLIDING since 2026-09-17, and calibrated IN that mode rather than inheriting the
        # binned values. A window that slides: a sub-second shift of a real recording keeps
        # 64% of the binned calls and 100% of the sliding ones
        # (`tools/probe_sliding_vs_binned.py`), and on the 84 real baseline windows sliding
        # is a superset of binned (`tools/compare_sliding_vs_binned.py`). `thr_step_sec` and
        # `n_surrogates` do not apply in this mode and are kept for the binned path, which
        # stays as the MATLAB port with its parity tests.
        # ⚠ STILL BINNED HERE. The sliding values below are measured and chosen; they are
        # NOT switched on in this change, because switching them moves the viewer's
        # calibrated defaults while the browser still runs both detectors binned, and moves
        # the calls a slow-comodulation analysis is pinned to. Both are consequences of
        # shipping sliding rather than defects in the values. The switch, with those two
        # handled, is on branch `opt-every-knob-run` and in HANDOFF-coded-detectors.md.
        params=dict(bin_width_sec=1.0, context_win_sec=120.0, thr_step_sec=15.0,
                    merge_gap_sec=2.0, threshold_pctile=99.5, n_surrogates=100),
        source=f"{RETUNE}: 99.9 -> 99.5, mean F1 0.669 -> 0.686, gain +0.017 "
               "(interval +0.005 to +0.029); 0.16 firings/min in the empty stretch on "
               "both backgrounds (limit 1), 1.7 calls/hour on the empty recording "
               "(limit 3). Was the measured-regime F1 optimum of 2026-08-13 "
               "(loco_detect docstring), found on an older bench. "
               f"⚠ NOT YET SWITCHED TO SLIDING. {SLIDING_SEARCH} chose, for the sliding "
               "mode: threshold 99.9, merge gap 8 s, symmetric null, context unchanged at "
               "120 s — held-out mean F1 0.737 against this point's 0.699, 1.7 calls/hour "
               "on the empty recording (limit 3) where sliding at THIS point fires 4.0 and "
               "is over, crowded-recording mean F1 0.827 against this point's 0.816. The "
               "switch waits on the browser port and one analysis; see the comment above.",
        knob="threshold_pctile", grid=(97.0, 98.0, 99.0, 99.5, 99.9, 99.99, 99.999,
                                       99.9999)),
    "cicada": OperatingPoint(
        # Each event held active for its own width, as the folder sent it
        # (FOUNDATIONS §7). Until 2026-09-16 this was `active_duration_sec=1.0`, so
        # every locust number — bench, bake-off and real recordings — came from a
        # fixed second that ignored the width column. The anchor is unchanged: the
        # default `locs`, which on a folder is the half-rise (export_folder_spec.md
        # revision 8 calls that deliberate; the browser anchors on the peak).
        params=dict(sce_percentile=99.999, active_duration_mode="per_event",
                    duration_field="width", n_surrogates=100),
        source="FAST percentile re-derived 2026-09-16 with per-event widths "
               "(MEASURED_WIDTH_QUANTILES): pick_operating_point over 24 bench "
               "recordings accepts 99.999 on baseline_quiet (F1 0.565, 7.9 firings/min "
               "in the empty block) and 99.99 on baseline_busy (F1 0.540, 9.5/min); "
               "mean F1 0.542 vs 0.548, a tie, so the setting that fires half as "
               "often on nothing stays. Previously retuned 99.99 -> 99.999 on "
               "2026-08-20 at the fixed 1 s (cicada.py). SLOW's percentile has no "
               f"bench evidence at either duration. Confirmed by {RETUNE}: 99.99 "
               "scores +0.010 mean F1 with an interval of -0.002 to +0.025, which "
               "includes zero, so 99.999 stays.",
        # Extended 2026-08-20 when REGIMES moved to the approved export folder: at the
        # corrected (busier) quiet endpoint the old top, 99.99999, was still the
        # peak and the search was still climbing. A busier background needs a
        # stricter percentile, so the grid needs room above the operating point
        # rather than ending at it.
        knob="sce_percentile", grid=(90.0, 99.0, 99.9, 99.95, 99.99, 99.995, 99.999,
                                     99.9995, 99.9999, 99.99999)),
    "sce": OperatingPoint(
        params=dict(bin_width_sec=10.0, threshold_pctile=98.0, n_surrogates=200),
        # ⚠ The F1 optimum is much looser — 75, mean F1 0.665 — and it is excluded by
        # the empty-recording budget, not by noise: 41.8 calls/hour there against a
        # limit of 6, where 98 makes 3.4. Whether that trade is worth it is Tony's call
        # (docs/todo/2026-09-16-binned-sce-trades-false-alarms-for-f1.md). In the
        # dense probe stretch this knob barely matters (about 5.7 firings/min at every
        # threshold); on the empty recording it decides nearly everything.
        source=f"{RETUNE}: 99 -> 98, mean F1 0.490 -> 0.525, gain +0.035 (interval "
               "+0.022 to +0.048); 3.4 calls/hour on the empty recording (limit 6), "
               "where 95 already makes 8.2. Was the sce_detect default (generate_sce "
               "contract), never tuned. Scored over each call's own bins "
               "(score.EXTENT_FIELD).",
        knob="threshold_pctile", grid=(10.0, 20.0, 30.0, 40.0, 50.0, 60.0, 70.0, 75.0,
                                       80.0, 85.0, 90.0, 95.0, 98.0, 99.0, 99.5, 99.9)),
    "coact": OperatingPoint(
        # ⚠ STILL BINNED HERE, for the reason on `loco` above: the sliding values are
        # measured and chosen and are not switched on in this change.
        params=dict(int_win_sec=2.0, context_win_sec=60.0, alpha=1e-4,
                    n_surrogates=100),
        source="explore_sce viewer FAST point — NOT the coact_detect signature "
               f"default of alpha=0.01, which scores F1 0.72 here. Confirmed by {RETUNE}: "
               "already the best value within both budgets (mean F1 0.700). "
               f"⚠ NOT YET SWITCHED TO SLIDING. {SLIDING_SEARCH} chose, for the sliding "
               "mode: alpha 1e-5, context 120 s, merge gap 8 s, guard 1 s — held-out mean "
               "F1 0.746 against this point's 0.702, 5.8 calls/hour on the empty recording "
               "(limit 7) where sliding at THIS point fires 7.7 and is over, "
               "crowded-recording mean F1 0.818 against this point's 0.808.",
        knob="alpha", grid=(1e-1, 3e-2, 1e-2, 3e-3, 1e-3, 3e-4, 1e-4, 3e-5, 1e-5, 1e-6,
                            1e-7)),
    "rate": OperatingPoint(
        params=dict(excess_threshold_hz=4.5, context_win=60.0, rate_win=1.0,
                    grid_dt=0.1),
        source=f"{RETUNE}: 5.0 -> 4.5 Hz, mean F1 0.606 -> 0.630, gain +0.024 "
               "(interval +0.012 to +0.037); 1.13 / 1.68 firings/min in the empty "
               "stretch (quiet / busy, limit 2), 0.1 calls/hour on the empty recording "
               "(limit 1). 4.0 scores about the same and is over the limit on busy. Was "
               "the rate_detect default, never tuned. grid_dt is the generator's own "
               "0.1 s grid.",
        knob="excess_threshold_hz", grid=(0.5, 1.0, 2.0, 3.0, 3.5, 4.0, 4.5, 5.0, 6.0,
                                          8.0),
        takes_rng=False),
    "sync": OperatingPoint(
        params=dict(tau_max=0.25, max_gap=0.5, C_threshold=0.1, C_min=0.1),
        source="viewer FAST defaults (sync_detect docstring). Confirmed by "
               f"{RETUNE}: every looser value fires over the limit of 1/min in the busy "
               "empty stretch, and 0.12 ties it (mean F1 0.449).",
        knob="C_threshold", grid=(0.005, 0.01, 0.02, 0.04, 0.06, 0.08, 0.1, 0.12, 0.16,
                                  0.2, 0.3),
        takes_rng=False),
}

DETECTORS = tuple(OPERATING_POINTS)


REGIMES: dict[str, dict] = {
    "baseline_quiet": dict(bg_rate_hz=0.0049),
    "baseline_busy": dict(bg_rate_hz=0.0169),
}
"""The difficulty axis, and **every value on it comes from untreated recordings.**

**Re-measured 2026-09-23 on the default folder's 66 recordings**: quiet 0.0049 Hz
(0.004948) and busy 0.0169 Hz (0.016895), background rates by the same route as below,
over the 63 recordings that clear the shape floors;
`docs/learned/runs/2026-09-23-coordination-rates-senktide-ttx/`. They were 0.0042 and
0.0165 Hz on the 84-recording folder, which the rest of this docstring describes.

Both endpoints are the interquartile spread of slice-mean per-ROI rate across
baseline windows, fast stream, **with the coordinated share subtracted**: 0.0042 Hz
at p25 and 0.0165 Hz at p75. Untreated slices vary about 3.9-fold among themselves,
and that variation is the axis an operating point has to survive.

**These are BACKGROUND rates as of 2026-09-22, not total rates** (Tony, ~21:45 EDT:
*background, end to end*). A recording's total per-cell rate contains firing that
belongs to moments shared with other cells; what this axis wants is the rate the
*background* generator should produce, and planting coordinated events on top of a
total rate counts the shared part twice. The coordinated share is measured without
deciding which onsets form an event — factorial cumulants of the population count,
against per-cell circular-shift surrogates — by
`tools/measure_coordination_rates.py`, recorded in
`docs/learned/runs/2026-09-23-coordination-rates/`.

**The raw rates did not move; only the subtraction is new.** On the same recording
set the raw p25/p75 read 0.00505 and 0.01904, against the 0.0052 and 0.0190 that
stood here before — agreement within 3%, which is what makes the subtraction the
whole of the change. Quiet falls 16.5%, busy 13.6%.

**The recording set is `fit_background_shape`'s, not every recording.** 80 of the
default export's 84 baseline windows clear its floors (≥ 300 s, ≥ 20 events,
≥ 5 ROIs), and those are the ones `tools/remeasure_bench.py` has always used for
this axis. Measuring over all 84 instead makes quiet read 30% low while busy agrees
to 2% — the floors cut short, sparse and few-ROI windows, which are the quiet tail.
That mistake was made and caught on 2026-09-22, before anything adopted it.

⚠ **The estimator behind the subtraction is calibrated at the 1 s counting window
and, on the fast stream, at no other**: its error on the recovered coordinated share
runs +0.06 at 1 s, +0.46 at 2 s and +1.00 at 4 s. These values are the 1 s ones.
Slow's estimator clears every window; fast's does not, so a re-measure must keep the
window or re-check the calibration first.

**Re-derived 2026-08-20 from the export folder, which is what the lab
approved.** The previous endpoints — 0.0038 and 0.0175, a 4.6-fold span — were
fitted against the `.mat` store, which carries every recording ever processed
including the two the lab withdrew (SAP007, and
`docs/todo/2026-08-20-six-tools-still-read-stores.md`). The folder is smaller and
different, so the axis moved: both ends up, and the span narrower.

**Moving it changes no detector's score beyond seed noise, and reorders nothing.**
Measured before the change rather than assumed — every detector at its calibrated
operating point, nothing re-tuned, 12 seeds at the quiet endpoint:

===========  =========  =========  ==========  =======
detector     F1 old     F1 new     mean dF1    sd(dF1)
===========  =========  =========  ==========  =======
coact            0.743      0.688      -0.055    0.078
loco             0.731      0.649      -0.083    0.102
rate             0.601      0.625      +0.023    0.085
cicada           0.521      0.547      +0.026    0.076
sync             0.377      0.473      +0.095    0.128
sce              0.284      0.360      +0.075    0.095
===========  =========  =========  ==========  =======

**No detector moves by more than its own seed-to-seed spread**, and the ranking is
identical either way: coact > loco > rate > cicada > sync > sce. A first pass at
three seeds appeared to drop loco from first to third; that was noise, and it is
recorded because three seeds is the bench default and is not enough to support a
claim of this kind.

**No treatment appears here, as a source or as an endpoint.** Tony, 2026-08-14:
*"everything should be based on baseline recordings. do not use senk or ttx as
sources for the properties of coordination."* Two earlier versions of this module
got that wrong in opposite directions — the first ran baseline → senktide, which
made the drug response the thing operating points were checked against; the
second replaced it with a TTX-derived endpoint, which is still a treatment, and
which pooled 37 slices whose measured effects run in **opposite directions by
group** (ORX up, male unchanged, diestrus down). The global foundations doc
forbids exactly that pooling: *"a TTX result on one group does not generalise to
the arm."*

**The old justification for the quiet end is withdrawn, not restated.** It used to
read: "the correction costs nothing — baseline's own p25 (0.0038) lands within 5%
of the TTX median (0.0040)". On the approved recordings p25 is 0.0052, which is 30%
above that TTX median, so the coincidence is gone.

Losing it costs nothing, because the argument was never load-bearing and should not
have been offered as reassurance. The reason to take the quiet end from untreated
p25 is that treatments are not a source of coordination properties at all — Tony,
2026-08-14. That a drug-derived number happened to sit nearby was a curiosity, and
had the two disagreed from the start the untreated value would still have been
correct. An argument that only works when the numbers agree is not an argument.

Senktide is absent entirely rather than held out. Holding it out still requires
generating a recording at senktide's rate, which is using a treatment as a source
of a coordination property. If a senktide evaluation is wanted it is a separate,
explicit decision, not a default of this module.
"""

NULL_RECORDING = dict(bg_rate_hz=REGIMES["baseline_quiet"]["bg_rate_hz"],
                      n_per_level=(0, 0, 0), hot_window=None, hot_rate_hz=0.0,
                      ramp_sec=0.0, n_distractors=0)
"""A **synthetic** recording with no planted coordination — Poisson background at
the quiet end of baseline, and nothing else.

**The rate is read from** :data:`REGIMES` **rather than written here.** Until 2026-09-23 it was a
literal 0.0052 Hz, so when #756 moved the quiet background to 0.0042 Hz this recording stayed
behind, 24% busier than the quiet end it stands for, and the calls-per-hour budgets were measured
on it (Tony, 2026-09-23: *"fix the no coordination problem"*).

Its only claim is about construction: this generator planted no events, so a
detector reporting one is reporting structure that was not put there. That is a
useful false-positive floor precisely because it rests on the construction and on
nothing about biology.

**It is not a TTX recording, and TTX is not a silencing control.** An earlier
version asserted that under TTX action potentials are blocked so coordination
cannot happen, and treated a detector's TTX detections as false positives by
construction. That is false and the project forbids the premise: coordination
persists under TTX, the mechanism is open work, and a detector returning little
in a TTX window is **not** thereby validated. The rate here is baseline's own
p25, not a drug's median.

⚠ **This is measured at one rate only.** Reviewer 2's finding, 2026-08-14: the
false-positive ranking is not stable across the range — re-run at a busier
background it reorders, so a detector that reports zero here is not thereby
quiet. Report it with its rate attached, and do not read it as a ranking.
"""

# Measured off baseline slices only — see MEASURED_PROVENANCE.
BENCH_RECORDING = dict(
    duration_sec=2700.0,
    n_roi=32,
    participation=(0.30, 0.203, 0.10),
    n_per_level=(5, 5, 5),
    jitter_sec=0.105,
    min_sep_sec=120.0,
    # THE BACKGROUND IS NOT FLAT, and as of 2026-08-28 this bench stops pretending
    # it is. Both shapes are fitted, not chosen — see `MEASURED_RATE_SHAPE` (81
    # baseline windows, 2 643 ROIs) and `MEASURED_BURST_SHAPE` (the same estimator
    # turned on time). Wiring them in was held back for one reason and one only:
    # leaving them `None` keeps the RNG stream identical, so every seed reproduced
    # and every published number stayed comparable.
    #
    # Tony cut that knot, 2026-08-28: *"all the benchmarks have changed because the
    # bench is changed."* The comparability those `None`s were protecting had
    # already been spent by the bench revamp, so holding a measured background out
    # of the bench was buying nothing and costing realism — a flat field leaves 2%
    # of ROIs silent where real windows leave 35%.
    bg_rate_shape=MEASURED_RATE_SHAPE,
    bg_burst_shape=MEASURED_BURST_SHAPE,
    bg_burst_bin_sec=MEASURED_BURST_BINS,
    # ADR-0009 decision 1: no elevated-rate stretch on a recording with planted events. The span
    # 1200-1500 s carries ordinary background; the stretch lives in ELEVATED_RATE_RECORDING.
    hot_window=None,
    hot_rate_hz=0.0,
    ramp_sec=0.0,
    n_distractors=6,
    distractor_frac=0.18,
    distractor_window=(120.0, 1100.0),
)
"""The recording every bench run is scored on.

**Re-measured 2026-09-23 on the default folder's 66 recordings**, on Tony's instruction
to retune the bench on the data set it scores:

===================  ================  =========================================
knob                 84 recordings     66 recordings (95% interval)
===================  ================  =========================================
``n_roi``            33 ROIs           32 ROIs (27.5–34 ROIs)
``participation``    0.19              0.203 (0.182–0.233), the middle level
``jitter_sec``       0.106 s           0.105 s (0.090–0.124 s)
``hot_rate_hz``      0.1271 Hz         0.1334 Hz, background 99th percentile
===================  ================  =========================================

The outer participation levels (0.30, 0.10) and ``distractor_frac`` are chosen, not
measured, and did not move. Records: `docs/learned/bench_measured.json`,
`docs/learned/runs/2026-09-23-jitter-correlogram-senktide-ttx/` (jitter) and
`docs/learned/runs/2026-09-23-coordination-rates-senktide-ttx/` (the probe). The
history below is the 84-recording measurement's.

Its structural values are **measured off real recordings**, not invented. Until
2026-08-13 they were guesses, and every one of them made coordination easier
than it is:

===================  ==========  =============================  ==============
knob                 was         measured                       effect
===================  ==========  =============================  ==============
``n_roi``            30          ~33                            (was right)
``bg_rate_hz``       0.05 Hz     0.0096 Hz/ROI                  5× too busy
``jitter_sec``       0.05 s      0.106 s                        2× too tight
``participation``    50–100%     6 of ~33 ROI = 19%             3–5× too many
===================  ==========  =============================  ==============

The consequence was not subtle. On the invented values every detector scored
F1 ≈ 0.9–1.0 and the bench could not tell them apart; on the measured ones they
range 0.20–0.75 and separate sharply, because a real coordinated event recruits
about **six ROIs within about a tenth of a second** — which sits just above
the ``min_rois`` floor the detectors ship with. That is the regime the
instruments were designed for, and it is where they differ.

**``jitter_sec`` was 0.36 s until 2026-09-22, and that value measured the
instrument rather than the recordings.** It came from ``assess_coactivity``'s
within-cluster onset spread, which tracks the coincidence bin ÷ √12 from 0.5 s
to 5 s on both streams — so the 2026-09-17 re-measure "confirmed" it with the
same instrument at the same bin. ``tools/measure_jitter_correlogram.py`` measures
the width of the cross-ROI correlogram's peak instead, calibrated against
simulations of this bench at a grid of planted jitters, and gives **0.106 s
[0.091, 0.120]** on the default folder's fast stream. Tony ruled on 2026-09-22
to adopt it. The scale of the correction is the point: the bench was planting
events about **three times looser** than the recordings it is fitted to.

``participation`` keeps a spread (30 / 19 / 10%) around the measured median
rather than collapsing to it, so recall still resolves a participant floor. The
10% level is ~3 ROIs, at the floor itself. The middle level moved 0.18 → 0.19 on
2026-09-22, the meeting having approved it: 0.18 was this docstring's own
rounding of 6/33, and the folder measures 0.1905. Unlike the jitter, this
constant was **swept across five coincidence bins and held** (0.19 at every bin),
so the recruitment number survived the test the timing number failed.

``hot_rate_hz`` moved with them. At 0.30 it was 6x the invented background and
**31x the measured one** — a probe that severe stops asking whether a detector
keys on rate and starts asking whether it survives an impossible surge. 0.06
replaced it: 6x measured baseline and 1.6x senktide, busier than any real
condition in the table without leaving the physical world.

**Since 2026-09-22 it is 0.1271 Hz, and it is now measured rather than chosen**
(Tony, ~21:45 EDT). 0.06 was a multiple of the median picked to be plausible; this
is the **99th percentile of the per-cell background rate over every 300-second
stretch of every baseline window** — 2,582 stretches — so the methods section's
"99th percentile of the baseline frequency" is true of the bench rather than
approximately true of it. Same measurement, same recording set and same
coordinated-share subtraction as ``REGIMES`` above: background end to end, which is
what makes the probe comparable with the two endpoints instead of being a different
quantity at the top of the same axis.

**It roughly doubles, and the doubling is a change of definition, not a
correction.** The coordinated share at the probe is only 0.6% of the raw rate on
this stream — fast's busiest stretches are not its coordinated ones — so almost the
whole move from 0.06 to 0.1271 is the percentile replacing the multiple. For scale:
0.06 sat at the **96.2nd** percentile of the same distribution, so the old value
was not wild, and this is a deliberate step up the same curve rather than a
repudiation of it. ``tools/measure_coordination_rates.py``,
`docs/learned/runs/2026-09-23-coordination-rates/`.

``min_sep_sec`` is 120 s and not the generator's 15 s default on purpose. The
detectors estimate their null over context windows up to 120 s wide, so events
spaced more tightly than that put real coordination inside the null the
threshold is derived from — the **contaminated null**, the trap that made the
first upstream benchmark unusable and cost two weeks of tuning against it. One
event per context window is the condition for a background-only null.

That spacing is what sets ``duration_sec``, not the other way round: the
generator needs a mean interval above the floor, the hot window is excluded from
placement, and it refuses outright rather than quietly packing the events
closer. A 45-minute recording is the price of a null worth estimating against.

It is also long enough that the *realized* spacing stays irregular (CV ~0.8 at
these settings). At the shortest length that fits, every interval is pinned near
the floor and the schedule becomes near-metronomic — harmless for these six,
which use no timing prior, but the same configuration feeding a training set
would hand a model the clock as a shortcut (the plan's warning that regularity
is a cue). Shortening this recording is therefore not the free win it looks
like.

The distractors are correlated bursts that are real coincidence but not
coordination: negatives with no recall value, there so the bench can fail a
detector for calling on them.

**It carries no elevated-rate stretch since 2026-09-25** (ADR-0009 decision 1).
Until then 1200–1500 s held one — every ROI's rate raised together, nothing
planted — and under ADR-0008 that shared rate change lifted the whole
recording's floor above every planted event (16–20 co-active ROIs on fast,
`tools/probe_bench_floor.py`). The stretch moved to a recording of its own,
:data:`ELEVATED_RATE_RECORDING`, and the span here carries ordinary background.
Placement no longer skips it, so the realized spacing changes; the floor
``min_sep_sec`` and ``duration_sec`` do not. ``hot_rate_hz`` 0.1334 Hz and its
history above now describe that recording's stretch.
"""


def make_recording(regime: str, seed: int, **overrides):
    """One bench recording. ``regime`` selects the background rate.

    Every regime here is derived from untreated recordings; there is no
    treatment regime to accept. See :data:`REGIMES`. Like every simulated
    recording it carries per-event widths for locust — see
    :data:`bugarach.simulate.MEASURED_WIDTH_QUANTILES`.
    """
    if regime not in REGIMES:
        raise ValueError(f"unknown regime {regime!r} — have {sorted(REGIMES)}")
    return with_floor(simulate_coordination(
        seed=seed, **{**BENCH_RECORDING, **REGIMES[regime], **overrides}))


CROWDED_RECORDING = dict(BENCH_RECORDING, min_sep_sec=14.0, duration_sec=10800.0,
                         n_per_level=(40, 40, 40), hot_window=None,
                         hot_rate_hz=0.0, ramp_sec=0.0, n_distractors=0)
"""Some events sit inside one another's reference window and some do not — so the
recording is its own control.

**The bench cannot exhibit reference-window contamination, and that is why the
regime-shift incident was found by hand rather than by the suite.**
``BENCH_RECORDING`` plants events at least **120 s** apart while a rolling
detector's reference window spans **±30 s**, so a second planted event can never
land in the first one's context. The failure mode every CFAR detector uses guard
cells against — Finn & Johnson quantified it in 1968, and this project met it as
binned SCE's precision falling 74% → 10% — is *impossible by construction* on the
recording the detectors are scored on.

So it gets its own recording rather than a change to the shared one. Moving
``BENCH_RECORDING``'s spacing would re-derive every operating point and invalidate
every published number for a reason unrelated to why they were derived; this adds
a condition instead of moving the goalposts.

**14 s** is not arbitrary: it is the spacing of the dense benchmark whose settings
collapsed on sparse data, recorded in the README as the incident that cost two
weeks. The probe and distractors are off because this recording asks one question
— what happens when events crowd each other's context — and a dense-but-random
block would confound it with rate-keying.

⚠ **It carries no background rate, and that is deliberate — it takes a regime,
like every other recording here.** Until 2026-08-23 :func:`make_crowded_recording`
merged no regime at all, so ``bg_rate_hz`` fell through to
:func:`~bugarach.simulate.simulate_coordination`'s own default of **0.05 Hz** — the
pre-2026-08-13 invented value the correction table above names *"5× too busy"*,
roughly 10× :data:`REGIMES`' quiet endpoint. The recording built to isolate
crowding was running off the difficulty axis, and two thirds of the recall
collapse attributed to crowding was that instead: CoactDetect recalls **0.652**
at ``baseline_quiet`` against **0.254** as it had been shipped. The rate-keying
confound this docstring shuts the door on arrived through a keyword default.
``test_the_crowded_recording_stays_on_the_difficulty_axis`` is the door that
closes by itself.

**The count matters as much as the floor**, which is not obvious and cost a
measurement to find. ``min_sep_sec`` is a *floor* under a renewal process, not a
target: at the bench's own event count it changes almost nothing, because the
median gap stays near 70 s and only 5 of 35 gaps land inside a reference window.
**The count is what crowds.**

⚠ **It runs three hours, and the length is the design.** Tony, 2026-08-23:
*"shouldn't the two tests have the same number of events so F1 can be compared.
who cares how long the recording has to be?"* Both halves were right and the
second one is what fixed this.

The first version planted the same 120 events in 45 minutes, which put **every**
event inside a neighbour's reference window — 97 of 119 gaps under 30 s, none
over 60. So there was no uncontaminated group anywhere in it, and the only
available comparison was against ``BENCH_RECORDING``, which differs in event
count, duration and therefore false-alarm opportunity all at once. Two things
followed, both bad. F1 could not be compared across the pair at all, because
eight times the events raises precision on density alone — CoactDetect reads a
*higher* F1 crowded than on the bench while recalling a fifth less. And matching
the count by lengthening the sparse side cannot fix that, because false-alarm
opportunity scales with duration: the bench's own 15 events over 6 h hold recall
at 0.85 and drop precision from 0.633 to 0.250. **Crowding is events per unit
time, so no two recordings can differ in it and match on both count and
duration.**

Three hours dissolves the problem instead of balancing it. At the bench's own
``interval_cv`` the gap distribution spans both regimes in **one** recording:
about **38%** of events have a neighbour inside their own ±30 s reference window
and about **31%** have nothing within 60 s. Recall is per-event, so splitting it
by each event's own nearest-neighbour gap (:func:`nearest_neighbour_gaps`) holds
the count, the duration, the background *and* the false-alarm opportunity fixed
by construction — there is only one recording. See
``test_the_crowded_recording_contains_its_own_control``.

That contrast immediately paid for itself. Between recordings, a guard interval
looked like the masking fix §4a predicted. Within one, its recall gain is **flat
across the gap** — CoactDetect +0.045 at a 15–30 s gap and +0.046 at over 60 s,
where there is no neighbour to unmask — while precision falls 0.889 → 0.867. It
was lowering the bar everywhere, not relieving masking. `docs/forks.md` §4a.

Use it through :func:`make_crowded_recording`. It is a **diagnostic, not a
regime**: nothing should be calibrated on it, because a set assembled to hold
both populations in useful proportions is not one that anything resembles.
"""

TAIL_RECORDING = dict(CROWDED_RECORDING, n_per_level=(60, 60, 60),
                      min_sep_sec=6.0, interval_cv=1.0)
"""The crowded **tail** — fitted to real recordings, not invented.

:data:`CROWDED_RECORDING` plants a crowding fraction of **0.38**. Measured against the
export folder (``tools/probe_real_crowding.py``, 39 recordings with enough detections
to characterize), real recordings run **median 0.00, IQR 0.00–0.30, range 0.00–0.57**,
and **7 of 39 sit above 0.38**. So the region where reference-window contamination is
worst had no simulated counterpart at all;
``docs/reviews/guard_prior_art_2026-08-26.md`` records that as the gap this closes.

**The tail is not bursty, and that ruled out the obvious knob.** ``interval_cv`` buys
crowding by making the schedule clumpy — ``simulate_coordination`` calls ``>1`` *"long
quiet stretches broken by closely-spaced events"* — and reaching 0.5 that way needs
``interval_cv`` near 1.5, whose realized interval CV is 1.2–1.6. The seven real tail
recordings have an interval CV of **0.62–1.59, median 0.93**: Poisson-ish spacing, not
bursts. What they do have is a **small floor** — minimum gaps of **6–26 s, median 8** —
against this module's 14 s, and more events per hour.

So the tail is reached with ``interval_cv`` left at 1.0, the floor dropped onto the
real tail's own minimum gaps, and the count raised, holding the three-hour duration.
8 seeds, realized:

===============================  ========  ======  =========  =================
setting                           crowded      CV    min gap  matches real?
===============================  ========  ======  =========  =================
``CROWDED_RECORDING``                0.39    0.85       14.7  at the boundary
120 ev / 3 h / floor 6 s             0.48    0.94        6.8  **yes, mid-tail**
**TAIL_RECORDING** (180 / 3 h)       0.61    0.91        6.3  above in aggregate
===============================  ========  ======  =========  =================

**Its aggregate crowding is above anything observed, on purpose, and it is meant to be
used per-event rather than in aggregate.** This is the same trade
:data:`CROWDED_RECORDING` makes and states — *"a set assembled to hold both populations
in useful proportions is not one that anything resembles"* — for the same reason:
recall is per-event, so splitting by each event's own :func:`nearest_neighbour_gaps`
holds count, duration, background and false-alarm opportunity fixed inside one
recording. Raising the count is what populates the **tightest gap bins**, which are the
point and which :data:`CROWDED_RECORDING` barely reaches. Read the bins, not the
headline fraction.

⚠ **A diagnostic, exactly like its parent. Nothing may be calibrated on it**, and no
operating point in this module is derived from it.

One note against the parent's docstring: *"at the bench's own event count
[``min_sep_sec``] changes almost nothing"* is true, and is about
:data:`BENCH_RECORDING`'s 15 events. At the crowded count the floor moves crowding
0.39 → 0.51 by itself, which is why it is a knob here and not there.
"""


def make_tail_recording(regime: str, seed: int, **overrides):
    """A recording whose planted events reach the real crowded tail.

    Same ``(slice, ground_truth)`` pair as :func:`make_recording`, and ``regime`` is
    required for the same reason it is on :func:`make_crowded_recording`. See
    :data:`TAIL_RECORDING` for what it is fitted to and what it must not be used for.
    """
    if regime not in REGIMES:
        raise ValueError(f"unknown regime {regime!r} — have {sorted(REGIMES)}")
    return with_floor(simulate_coordination(
        seed=seed, **{**TAIL_RECORDING, **REGIMES[regime], **overrides}))


CROWDING_GAP_SEC = 30.0
"""Half the shipped 60 s context — a gap below this puts two planted events in
one another's reference window, which is what makes an event crowded.

Named rather than written as a literal because it is a *consequence* of
``context_win``: change the context and this moves with it.
"""


def nearest_neighbour_gaps(gt) -> "np.ndarray":
    """Seconds to each planted event's closest neighbour, in ``gt.times`` order.

    The companion to :data:`CROWDED_RECORDING`, and the reason that recording is
    three hours long. **Crowding is a property of an event, not of a recording**,
    so it is measurable within one: score as usual, then split recall by this.
    Everything a between-recording comparison cannot hold fixed — event count,
    duration, background rate, false-alarm opportunity — is fixed here because
    there is only one recording.

    A lone event gets ``inf``. Compare against :data:`CROWDING_GAP_SEC`::

        sl, gt = make_crowded_recording("baseline_quiet", 1)
        gaps = nearest_neighbour_gaps(gt)
        crowded = gaps < CROWDING_GAP_SEC        # has a neighbour in its context
        isolated = gaps >= 2 * CROWDING_GAP_SEC  # has none, and is the control

    The order is ``gt.events``' — ``gt.times`` is derived from it and
    :attr:`~bugarach.score.Score.hits` is in it — so ``gaps`` and ``score.hits``
    are column-aligned and ``score.hits[gaps < CROWDING_GAP_SEC].mean()`` is the
    crowded group's recall. Do not sort one without the other.
    """
    t = np.asarray(gt.times, dtype=float)
    order = np.argsort(t)
    gaps = np.full(t.size, np.inf)
    if t.size > 1:
        d = np.diff(t[order])
        by_time = np.full(t.size, np.inf)
        by_time[:-1] = np.minimum(by_time[:-1], d)
        by_time[1:] = np.minimum(by_time[1:], d)
        gaps[order] = by_time
    return gaps


def make_crowded_recording(regime: str, seed: int, **overrides):
    """A recording whose planted events crowd each other's reference window.

    Same signature and same ``(slice, ground_truth)`` pair as
    :func:`make_recording` — ``regime`` selects the background rate from
    :data:`REGIMES` and is **required**, because this function once defaulted it
    and the default was wrong for eight months of nobody noticing. See
    :data:`CROWDED_RECORDING` for what the recording is for, what it must not be
    used for, and what the missing regime cost.

    Crowding and the background are separate axes and both matter: at
    ``baseline_quiet`` crowding costs CoactDetect 0.181 of its recall, and moving
    the background off the axis cost another 0.398 on top.
    """
    if regime not in REGIMES:
        raise ValueError(f"unknown regime {regime!r} — have {sorted(REGIMES)}")
    return with_floor(simulate_coordination(
        seed=seed, **{**CROWDED_RECORDING, **REGIMES[regime], **overrides}))


def make_null_recording(seed: int, **overrides):
    """A recording with no planted coordination — background only.

    Returns the same ``(slice, ground_truth)`` pair as :func:`make_recording`,
    with ``gt.events`` empty. Nothing is scored against planted truth because
    there is none: every detection is a false positive *of this construction*.
    See :data:`NULL_RECORDING` for what that does and does not license.
    """
    return with_floor(simulate_coordination(
        seed=seed, **{**BENCH_RECORDING, **NULL_RECORDING, **overrides}))


def false_positives_per_hour(name: str, seeds=(1, 2, 3), **overrides) -> float:
    """How often a detector fires on a recording containing no coordination.

    Does not depend on the generator being realistic beyond its firing rate:
    there is no planted structure to get wrong, so a detector cannot be
    flattered by an easy benchmark or punished by a hard one.

    What it measures is a detector's response to Poisson background at a given
    rate. It is not a statement about any biological preparation, and it must
    not be read as one.
    """
    hours = 0.0
    total = 0
    for seed in seeds:
        s, _ = make_null_recording(seed)
        det = run_detector(name, s, **overrides)
        onsets = getattr(det, "onset_sec", None)
        onsets = det.locs if onsets is None else onsets
        onsets = np.asarray(onsets, dtype=float)
        total += int(np.isfinite(onsets).sum())
        hours += BENCH_RECORDING["duration_sec"] / 3600.0
    return total / hours if hours else float("nan")


NULL_SEED_OFFSET = 50_000
"""What the scoring tools add to a bench seed to draw the no-coordination recording, so it never
shares a simulator seed with a recording that has planted events (``tools/score_bench_candidates.py``:
fresh seeds 6000–6011 read the null on 56000–56011)."""

ELEVATED_SEED_OFFSET = 60_000
"""What :func:`make_elevated_rate_recording` adds to the seed it is given, beside
:data:`NULL_SEED_OFFSET`. Fixed on 2026-09-25 (the final-parameters night): a search on bench seeds
1–96 reads the elevated-rate recording on 60001–60096, and fresh-seed scoring on 6000–6011 reads it
on 66000–66011, clear of 1–96, 6000–6023 and the null's 56000–56011. The offset is applied inside
the maker rather than by each caller, so no caller can forget it."""

ELEVATED_RATE_RECORDING = dict(
    n_per_level=(0, 0, 0),
    n_distractors=0,
    hot_window=(1200.0, 1500.0),
    hot_rate_hz=0.1334,
    ramp_sec=30.0,
)
"""The elevated-rate test's recording (ADR-0009 decision 1): the stretch and nothing planted.

Laid over :data:`BENCH_RECORDING` and a regime, so its length, ROI count and background are the
bench's; only the stretch is added and the planted events and decoys are taken away. The stretch
is the one :data:`BENCH_RECORDING` carried until 2026-09-25: 1200–1500 s, every ROI at
``hot_rate_hz`` 0.1334 Hz (the background 99th percentile of 300 s baseline stretches, measured —
see :data:`BENCH_RECORDING`), with 30 s ramps.

**Scored only for calls**, against the budgets that already exist: calls per minute inside the
stretch against :data:`MAX_PROBE_PER_MIN`, and calls per hour outside it against
:data:`MAX_FALSE_POSITIVES_PER_HOUR`, where it is a recording with nothing planted. No decoys, so
that outside part is comparable with :data:`NULL_RECORDING`, which carries none either.

**Its floor is its own** (ADR-0008 decision 5, ADR-0009 decision 1): computed from its own null
over the whole recording, stretch included, with nothing left out. The stretch lifts it, as a real
stretch lifts a real window's floor, so a detector that honours the floor calls little there by
construction; the test still separates detectors by what they call above it.
"""


def make_elevated_rate_recording(regime: str, seed: int, **overrides):
    """The elevated-rate recording at ``regime``'s background, simulated on
    ``seed +`` :data:`ELEVATED_SEED_OFFSET`. See :data:`ELEVATED_RATE_RECORDING`."""
    if regime not in REGIMES:
        raise ValueError(f"unknown regime {regime!r} — have {sorted(REGIMES)}")
    # Its own ADR-0008 floor, over the whole recording, stretch included (ADR-0009 decision 1).
    return with_floor(simulate_coordination(
        seed=seed + ELEVATED_SEED_OFFSET,
        **{**BENCH_RECORDING, **REGIMES[regime], **ELEVATED_RATE_RECORDING, **overrides}))


@dataclass
class ProbeResult:
    """One detector's calls on the elevated-rate recording, pooled over seeds.

    Every call there is a false one, since nothing is planted, so the two counts are the whole
    score: calls inside the stretch (the *probe*) and calls outside it. A call overlapping the
    stretch counts inside, as :func:`bugarach.score.score_stream` counts ``hot_fa``.
    """

    calls_in: int = 0
    calls_out: int = 0
    minutes_in: float = 0.0
    hours_out: float = 0.0
    seeds: tuple = ()

    @property
    def per_min_in(self) -> float:
        """Calls per minute inside the stretch, the number :data:`MAX_PROBE_PER_MIN` gates."""
        return self.calls_in / self.minutes_in if self.minutes_in else float("nan")

    @property
    def per_hour_out(self) -> float:
        """Calls per hour outside the stretch, the number :data:`MAX_FALSE_POSITIVES_PER_HOUR` gates."""
        return self.calls_out / self.hours_out if self.hours_out else float("nan")


def probe_counts(make, run, name: str, regime: str, seeds, *, tol_sec: float = TOL_SEC,
                 **overrides) -> ProbeResult:
    """Pool one detector's calls over elevated-rate recordings built by ``make`` and run by ``run``.

    Takes the maker and the runner rather than reading them, so the slow and combined benches
    share it without scoring a fast recording under their own label (the trap
    :mod:`bugarach.bench_slow` is laid out to avoid)."""
    out = ProbeResult(seeds=tuple(seeds))
    for seed in seeds:
        s, gt = make(regime, seed)
        sc = score_stream(gt, run(name, s, **overrides), tol_sec=tol_sec)
        h0, h1 = gt.params["hot_window"]
        span = h1 - h0
        out.calls_in += sc.hot_fa
        out.calls_out += sc.n_detected - sc.hot_fa
        out.minutes_in += span / 60.0
        out.hours_out += (gt.params["duration_sec"] - span) / 3600.0
    return out


def evaluate_elevated_rate(name: str, regime: str, seeds=(1, 2, 3), *, tol_sec: float = TOL_SEC,
                           **overrides) -> ProbeResult:
    """One detector's calls on the elevated-rate recording, inside and outside the stretch."""
    return probe_counts(make_elevated_rate_recording, run_detector, name, regime, seeds,
                        tol_sec=tol_sec, **overrides)


def run_detector(name: str, s, *, rng_seed: int = 20260706, floor: bool | None = None,
                 **overrides):
    """Run one detector on a slice at its declared operating point.

    Absorbs the two call shapes — three detectors take a ``Slice`` and run every
    stream, three take one stream's trains plus the extent — so callers work in
    detector names rather than signatures.

    ``floor`` (on unless :data:`FLOOR_SWITCH_ENV` says ``off``): the detector's participation
    minimum (:data:`FLOORED_SETTING`) is the recording's own ADR-0008 floor
    (:func:`recording_floor`), whatever the operating point says. ``floor=False`` runs the
    operating point as declared, which is pre-ADR-0008 and is labelled so wherever it is used.
    """
    if name not in OPERATING_POINTS:
        raise ValueError(f"unknown detector {name!r} — have {sorted(OPERATING_POINTS)}")
    op = OPERATING_POINTS[name]
    params = floored_params(name, s, op.params, overrides, STREAM, floor)
    if op.takes_rng:
        params["rng_seed"] = rng_seed

    if name in ("loco", "cicada", "sce"):
        fn = {"loco": loco_detect, "cicada": cicada_detect, "sce": sce_detect}[name]
        return fn(s, **params).streams[STREAM]

    ext = recording_extent(s)
    trains = stream_trains(s.streams[STREAM], ext)
    fn = {"coact": coact_detect, "rate": rate_detect, "sync": sync_detect}[name]
    return fn(trains, ext, **params)


@dataclass
class BenchResult:
    """One detector on one regime, pooled over seeds.

    Pooled counts, not the mean of per-seed ratios: a seed that happens to plant
    fewer events should not carry the same weight as a fuller one, and a seed
    with no detections at all makes precision undefined rather than zero.
    """

    detector: str
    regime: str
    knob_value: float | None = None
    n_planted: int = 0
    n_detected: int = 0
    n_hit: int = 0
    n_fa: int = 0
    hot_fa: int = 0
    distractor_hits: int = 0
    decoy_calls: int = 0
    """Calls outside the probe that match no planted event and land on a decoy (ADR-0006)."""
    by_frac: dict = field(default_factory=dict)
    dont_care_by_frac: dict = field(default_factory=dict)
    """``{participation_fraction: (n_under_floor, n_calls_matched_to_them)}``, pooled: planted
    events under their recording's floor and the calls on them, both out of the score (ADR-0009
    decision 2) and reported beside it."""
    floors: tuple = ()
    """Each pooled recording's ADR-0008 floor, in pooling order; empty when none was applied."""
    seeds: tuple = ()
    probe: ProbeResult | None = None
    """The same detector's calls on the elevated-rate recording (ADR-0009 decision 1), on the same
    seeds shifted by :data:`ELEVATED_SEED_OFFSET`. ``None`` when it was not run, and then
    :attr:`hot_fa_per_min` is NaN rather than zero: a probe nobody ran has not been passed."""
    tol_sec: float | None = None
    """The match tolerance every pooled score was measured at.

    It travels with the number because it is the number's units. A hit is
    counted at a 1.5 s edge gap against a median realized event 0.80 s wide
    (``docs/learned/tolerance_sweep.png``), so this F1 cannot tell landing on an
    event from landing a second away from it. The *ranking* survives that and
    any comparison drawn from it is safe; a bare F1 implying timing accuracy is
    not. ``None`` where nothing was pooled — a result assembled by hand has no
    tolerance to claim.
    """

    @property
    def n_scored(self) -> int:
        """Detections the headline numbers are computed over — everything
        outside the promiscuity probe. The probe has no planted events, so it
        contributes no hits and its firings would otherwise land entirely in the
        precision denominator."""
        return self.n_detected - self.hot_fa

    @property
    def recall(self) -> float:
        return self.n_hit / self.n_planted if self.n_planted else float("nan")

    @property
    def precision(self) -> float:
        """Precision outside the probe.

        The probe is deliberately severe — a rate six times the background, no
        coordination in it — so its firings dominate any precision it is folded
        into. Fold them in and the headline stops measuring the detector and
        starts measuring how hard the probe was set: CICADA reads F1 0.09 here,
        against 0.68 in the upstream campaign, on 599 hot-window detections out
        of 601 false alarms. That is the project's own cautionary tale — *the
        benchmark, not the detectors, was the original problem* — reached by
        turning one knob too far.

        So the probe gets its own number (:attr:`hot_fa`, gated separately) and
        stays out of this one, which is also how ``score_coord_detection.m``
        reported it upstream.
        """
        return self.n_hit / self.n_scored if self.n_scored else float("nan")

    @property
    def f1(self) -> float:
        r, p = self.recall, self.precision
        if not np.isfinite(r) or not np.isfinite(p) or (r + p) == 0:
            return float("nan")
        return 2 * r * p / (r + p)

    @property
    def precision_without_decoys(self) -> float:
        """Precision with calls on decoys left out of the denominator (ADR-0006: a decoy is
        coordination by construction, so a call on one is not a false alarm). Reported beside
        :attr:`precision` until the objective's ADR decides what becomes of the decoys; nothing
        selects on it."""
        n = self.n_scored - self.decoy_calls
        return self.n_hit / n if n else float("nan")

    @property
    def f1_without_decoys(self) -> float:
        r, p = self.recall, self.precision_without_decoys
        if not np.isfinite(r) or not np.isfinite(p) or (r + p) == 0:
            return float("nan")
        return 2 * r * p / (r + p)

    def recall_at(self, frac: float) -> float:
        """Recall at one participation level — the participant-floor axis."""
        n, h = self.by_frac.get(frac, (0, 0))
        return h / n if n else float("nan")

    @property
    def hot_fa_per_min(self) -> float:
        """The promiscuity probe's own number: calls per minute inside the elevated-rate
        stretch, where by construction there is nothing to find.

        Read from :attr:`probe`, the elevated-rate recording, since 2026-09-25 (ADR-0009). It used
        to read ``BENCH_RECORDING["hot_window"]`` and divide :attr:`hot_fa`, when the stretch sat
        inside the scored recording; with the stretch gone from there that would read zero for
        every detector and pass every gate in silence."""
        return self.probe.per_min_in if self.probe is not None else float("nan")

    @property
    def elevated_out_per_hour(self) -> float:
        """Calls per hour on the elevated-rate recording outside its stretch, NaN if not run."""
        return self.probe.per_hour_out if self.probe is not None else float("nan")

    def summary(self) -> str:
        knob = "" if self.knob_value is None else f" @{self.knob_value:g}"
        by = " ".join(f"{int(f * 100)}%:{self.recall_at(f):.2f}"
                      for f in sorted(self.by_frac, reverse=True))
        # The tolerance rides beside F1, not in a footnote: it is what the F1
        # was measured with, and the two are only meaningful together.
        tol = "" if self.tol_sec is None else f"@{self.tol_sec:g}s"
        return (f"{self.detector:6}/{self.regime:6}{knob}  recall {self.recall:.2f}  "
                f"precision {self.precision:.2f}  F1 {self.f1:.2f}{tol}  "
                f"FA {self.n_fa - self.hot_fa}  |  probe {self.hot_fa_per_min:5.1f}/min  "
                f"distractor {self.distractor_hits}   [{by}]")


@dataclass(frozen=True)
class FoldSplit:
    """The simulated data set, divided once, so every detector is asked the same question.

    A fold split is only worth anything if it is the *same* split for everyone
    being compared. Derive it here and hand it around; deriving it twice invites
    two detectors to be scored on different held-out sets under one heading.

    It is fully determined by ``base_seed``, ``n_folds`` and ``seeds_per_fold``:
    recording seeds run consecutively from the base and are dealt out in
    contiguous blocks. There is no shuffle, so there is no random source for two
    languages to agree about — which is what lets the browser reproduce a split
    the command line made.
    """

    seeds: tuple[int, ...]
    n_folds: int
    seeds_per_fold: int
    base_seed: int

    def fold_of(self, seed: int) -> int:
        """Which fold a recording seed belongs to."""
        i = seed - self.base_seed
        if not 0 <= i < len(self.seeds):
            last = self.base_seed + len(self.seeds) - 1
            raise KeyError(f"seed {seed} is not in this simulated data set "
                           f"({self.base_seed}..{last})")
        return i // self.seeds_per_fold

    def train(self, held: int) -> tuple[int, ...]:
        """Everything outside the held-out fold — what a knob may be fitted on."""
        self._check(held)
        return tuple(s for s in self.seeds if self.fold_of(s) != held)

    def test(self, held: int) -> tuple[int, ...]:
        """The held-out fold — what the reported number is scored on, and the
        only recordings nothing was fitted on."""
        self._check(held)
        return tuple(s for s in self.seeds if self.fold_of(s) == held)

    def _check(self, held: int) -> None:
        if not 0 <= held < self.n_folds:
            raise IndexError(f"fold {held} is outside 0..{self.n_folds - 1}")


def fold_split(*, n_folds: int = 4, seeds_per_fold: int = 3,
               base_seed: int = 1000) -> FoldSplit:
    """Deal ``n_folds * seeds_per_fold`` recording seeds into contiguous folds.

    One fold is refused rather than allowed to degenerate: with a single fold
    there is nothing left to fit on, and what comes back is a held-out score with
    no training set behind it — the exact claim this split exists to make true.
    """
    if n_folds < 2:
        raise ValueError(
            f"n_folds={n_folds} leaves no training data — fitting on three and "
            "scoring on the fourth needs at least two folds")
    if seeds_per_fold < 1:
        raise ValueError(f"seeds_per_fold={seeds_per_fold} makes an empty fold")
    seeds = tuple(base_seed + i for i in range(n_folds * seeds_per_fold))
    return FoldSplit(seeds=seeds, n_folds=n_folds,
                     seeds_per_fold=seeds_per_fold, base_seed=base_seed)


def pool_scores(scores, *, detector: str, regime: str, seeds=(),
                knob_value=None, probe: ProbeResult | None = None) -> BenchResult:
    """Pool per-seed :class:`~bugarach.score.Score` objects into one result.

    **Anything scored against this bench pools through here** — including
    detectors that are not in :data:`OPERATING_POINTS`: a learned model, a
    candidate, a one-off. That is the point of it being a function.

    A review on 2026-08-16 found the learned models pooled by hand in two tools
    as ``n_hit / n_detected``, while the six went through :func:`evaluate` and
    got :attr:`BenchResult.precision`, which excludes the promiscuity probe. The
    two halves of that report's central comparison sat on different
    denominators under a caption reading *"scored by the same rule"*, and the
    gap is not small — SCE reads precision 0.91 one way and 0.11 the other.
    Pooling is six lines, so it was rewritten instead of imported, and the rule
    for what counts forked in silence. Import this.

    The pooled result carries the tolerance its inputs were scored at. Scores
    measured at different tolerances are not poolable and are refused here
    rather than summed into a number whose units are a mixture — the failure
    would be invisible, since counts add whatever they were counted against.
    """
    out = BenchResult(detector=detector, regime=regime, knob_value=knob_value,
                      seeds=tuple(seeds), probe=probe)
    tols = {float(sc.tol_sec) for sc in scores if sc.tol_sec is not None}
    if len(tols) > 1:
        raise ValueError(
            f"cannot pool scores measured at different tolerances: "
            f"{sorted(tols)} s. A pooled count is only meaningful against one "
            "matching rule.")
    out.tol_sec = tols.pop() if tols else None
    for sc in scores:
        out.n_planted += sc.n_planted
        out.n_detected += sc.n_detected
        out.n_hit += sc.n_hit
        out.n_fa += sc.n_fa
        out.hot_fa += sc.hot_fa
        out.distractor_hits += sc.distractor_hits
        out.decoy_calls += getattr(sc, "decoy_calls", 0)
        for frac, (n, h) in sc.by_frac.items():
            pn, ph = out.by_frac.get(frac, (0, 0))
            out.by_frac[frac] = (pn + n, ph + h)
        for frac, (n, c) in (getattr(sc, "dont_care_by_frac", None) or {}).items():
            pn, pc = out.dont_care_by_frac.get(frac, (0, 0))
            out.dont_care_by_frac[frac] = (pn + n, pc + c)
        if getattr(sc, "floor", None) is not None:
            out.floors += (int(sc.floor),)
    return out


def under_floor_report(r: BenchResult) -> dict:
    """The counts ADR-0009 decision 2 says go with every score, by participation level: planted
    events scored, planted events under the floor, and calls on those, plus the floors."""
    levels = sorted(set(r.by_frac) | set(r.dont_care_by_frac), reverse=True)
    return dict(
        floor=FLOOR_LABEL if r.floors else "none",
        floors=dict(min=min(r.floors), median=float(np.median(r.floors)), max=max(r.floors))
        if r.floors else None,
        by_participation={f"{f:g}": dict(scored=r.by_frac.get(f, (0, 0))[0],
                                         under_floor=r.dont_care_by_frac.get(f, (0, 0))[0],
                                         calls_on_under_floor=r.dont_care_by_frac.get(f, (0, 0))[1])
                          for f in levels})


def evaluate(name: str, regime: str, seeds=(1, 2, 3), *, tol_sec: float = TOL_SEC,
             gen: dict | None = None, probe: bool = True, **overrides) -> BenchResult:
    """Run one detector over several seeds and pool the outcome.

    ``gen`` passes generator settings through to :func:`make_recording`, so a
    caller can hold the difficulty axis (``regime``) fixed while changing the
    recording it runs on — the fitted background out of
    ``docs/learned/generator_spec.json``, say, instead of the bench's flat one.
    Separate from ``**overrides``, which are the *detector's* knobs: the two used
    to be impossible to tell apart because only one of them existed.

    ``probe`` also runs the detector on the elevated-rate recording for the same seeds
    (:func:`evaluate_elevated_rate`), which is where :attr:`BenchResult.hot_fa_per_min` comes from
    since ADR-0009. It doubles the cost; ``probe=False`` leaves that number NaN, which the probe
    gates read as not passed.
    """
    gen = gen or {}
    scores = []
    for seed in seeds:
        s, gt = make_recording(regime, seed, **gen)
        det = run_detector(name, s, **overrides)
        scores.append(score_stream(gt, det, tol_sec=tol_sec))
    pr = None
    if probe:
        # The background settings travel; what makes it the elevated-rate recording does not.
        g = {k: v for k, v in gen.items() if k not in ELEVATED_RATE_RECORDING}
        pr = probe_counts(lambda r, sd: make_elevated_rate_recording(r, sd, **g), run_detector,
                          name, regime, seeds, tol_sec=tol_sec, **overrides)
    return pool_scores(scores, detector=name, regime=regime, seeds=seeds,
                       knob_value=overrides.get(OPERATING_POINTS[name].knob), probe=pr)


TOLERANCE_GRID = (0.1, 0.15, 0.25, 0.4, 0.5, 0.75, 1.0, 1.25, 1.5, 2.0, 2.5, 3.0)
"""Edge gaps to score at, spanning well under and well over the shipped 1.5 s.

**Reported as a curve rather than chosen as a constant** — the practice DOSED
uses (Chambon et al. 2019, on the coordination shelf, recorded there as
*"bugarach's open question, answered"*): report precision, recall and F1 across a
swept matching tolerance, so how much timing slack a score was granted is a
**visible axis** instead of a hidden constant.

Measured here, that costs almost nothing and settles an argument. Five of the six
detectors are flat from **0.75 s** upward and the ranking does not change between
0.4 s and 2.0 s, so the shipped 1.5 s sits deep in the plateau and no comparison
rests on it. The exception is **binned SCE**, still climbing at 1.5 s because its
10 s bins make its detections coarse and only a loose tolerance credits them —
which is exactly what a single number hides and a curve shows.

⚠ **Superseded 2026-09-16: the exception was the scorer's.** SCE had been scored
over ``[bin start, bin start + event spread]``, which ends before events late in
the bin, so extra tolerance kept reaching events its calls were made on. Scored
over its own bin (``SceStream.extent_sec``), its curve is flat from the narrowest
gap on this grid, and all six settle at or below the shipped tolerance —
``tests/test_tolerance_curve.py`` and
``docs/todo/2026-09-15-binned-sce-calls-are-scored-over-the-wrong-stretch.md``.

Same grid as ``docs/learned/tolerance_sweep.json``, so figures and bench runs
describe one sweep rather than two.
"""


def evaluate_curve(name: str, regime: str, seeds=(1, 2, 3), *,
                   tols=TOLERANCE_GRID, gen: dict | None = None,
                   **overrides) -> dict[float, BenchResult]:
    """One :class:`BenchResult` per matching tolerance — the curve, not a point.

    Detection runs **once per seed** and every tolerance scores those same
    detections, so the curve isolates the scoring rule. Re-detecting per
    tolerance would fold detector RNG into what is meant to be a property of the
    scorer.
    """
    per_tol: dict[float, list] = {float(t): [] for t in tols}
    for seed in seeds:
        s, gt = make_recording(regime, seed, **(gen or {}))
        det = run_detector(name, s, **overrides)
        for t in tols:
            per_tol[float(t)].append(score_stream(gt, det, tol_sec=float(t)))
    return {t: pool_scores(v, detector=name, regime=regime, seeds=seeds,
                           knob_value=overrides.get(OPERATING_POINTS[name].knob))
            for t, v in per_tol.items()}


def plateau_tol(curve: dict[float, BenchResult], *, eps: float = 1e-9):
    """The smallest tolerance whose F1 already equals the curve's best, or None.

    ``None`` means the detector was **still climbing at the widest tolerance
    scored**: its score depends on how much slack it was granted, so quoting one
    F1 for it asserts a timing accuracy it does not have. That is not a defect to
    fix by widening the grid — it is a fact about the detector, and the honest
    report names it rather than averaging it away.
    """
    tols = sorted(curve)
    best = max(curve[t].f1 for t in tols)
    if curve[tols[-1]].f1 < best - eps:
        return None                    # non-monotone: the widest is not the best
    if len(tols) > 1 and curve[tols[-1]].f1 - curve[tols[-2]].f1 > eps:
        return None                    # still rising where the grid stopped
    return next(t for t in tols if curve[t].f1 >= best - eps)


def describe_curve(curve: dict[float, BenchResult]) -> str:
    """An F1 that carries the tolerance it needed — for anything human-facing."""
    tols = sorted(curve)
    best = max(curve[t].f1 for t in tols)
    flat = plateau_tol(curve)
    if flat is None:
        return (f"F1 {curve[tols[-1]].f1:.3f} at {tols[-1]:g}s and STILL "
                "CLIMBING — this score depends on the matching tolerance")
    return f"F1 {best:.3f}, flat from {flat:g}s"


BACKGROUND_GRID = (0.0018, 0.0032, 0.0049, 0.0074, 0.0112, 0.0169, 0.0250, 0.0370)
"""Per-ROI background rates to score across — the SECOND hidden constant.

**Re-anchored 2026-09-23 on the 66 recordings, and widened to the groups.** Quiet
(0.0049 Hz) and busy (0.0169 Hz) are on it, two interior points step about 1.51x
between them, and two points above busy step about 1.48x. Below quiet it now reaches
**0.0018 Hz**, one point further than the old half-of-quiet, because the bench's two
regimes turned out to be the spread *between* groups rather than within one: ORX's
lower interquartile background is 0.00185 Hz and DI's upper is 0.0277 Hz
(`docs/learned/runs/2026-09-23-groups-rates-comod-66/`). The grid covers every group's
interquartile range, and ``tests/test_background_curve.py`` checks that against the
record. It was ``(0.0021, 0.0042, 0.0065, 0.0100, 0.0165, 0.0250, 0.0360)``. This is a
reporting axis only: operating points are still tuned at quiet and busy.

:data:`TOLERANCE_GRID` above dissolved the first one: how much timing slack a
score was granted became a visible axis instead of an inherited number. **The
background rate is the same defect and a larger one.** An operating point is
chosen at one point on this axis and quoted as though it held across it, and it
does not: on the same 120 events CoactDetect recalls **0.817** at the quiet
endpoint and **0.560** at the busy one — 0.26 of recall across a 3.7-fold rate
change that is only the interquartile spread of *untreated* slices
(``docs/RESET.md`` §6).

The grid brackets :data:`REGIMES` rather than reproducing it: p25 (0.0042) and
p75 (0.0165) are both on it, with a point below the quiet endpoint and two above
the busy one, because a curve that stops at the endpoints cannot show whether it
was about to fall off one. **``REGIMES`` is not changed by this** — moving the
axis is a recalibration; this reports across the axis that already exists.
``tests/test_background_curve.py`` enforces both endpoints being on the grid, so
the two cannot drift apart silently.

**It moved with ``REGIMES`` on 2026-09-22**, from
``(0.0026, 0.0052, 0.0080, 0.0120, 0.0190, 0.0280, 0.0400)``, when the endpoints
became background rates. The spacing is the old grid's, carried over: the point
below quiet is half of it, the two above busy step by about 1.5x, and the
interior keeps ratios near 1.55. Only the anchors moved; the shape of the axis
is unchanged, so curves either side of the change are comparable in form even
though they are measured at different rates.

**Why this matters more than the tolerance did.** Five of six detectors turned
out flat across the tolerance grid (six, once binned SCE was scored over its own
bin), so that constant was granting slack nobody
used and no comparison rested on it. Nothing is flat across this one. And the
treatment contrast the whole loop builds toward compares two windows at
*different* backgrounds, so a detector's sensitivity to this axis is confounded
with the effect being measured — and until now nothing reported it.
"""


def evaluate_background_curve(name: str, regime: str, seeds=(1, 2, 3), *,
                              rates=BACKGROUND_GRID, tol_sec: float = TOL_SEC,
                              gen: dict | None = None,
                              **overrides) -> dict[float, BenchResult]:
    """One :class:`BenchResult` per background rate — the curve, not a point.

    **Unlike :func:`evaluate_curve` this re-generates the recording at every
    point, and it has to.** The tolerance curve scores one set of detections
    several ways, so it isolates the scoring rule. The background is a property
    of the *recording*, so changing it means a different recording. The planted
    events are held fixed by the seed — same count, same times, same recruitment
    — so what moves across the curve is the field they sit in and nothing else.

    ``regime`` still selects the base recording and ``gen`` still passes generator
    settings through, so a caller can put a fitted background *shape* underneath
    and sweep its level. ``bg_rate_hz`` from either is overridden per point, which
    is the whole operation.
    """
    return background_curve(make_recording, run_detector, OPERATING_POINTS, name,
                            regime, seeds, rates=rates, tol_sec=tol_sec, gen=gen,
                            **overrides)


def background_curve(make, run, operating_points, name: str, regime: str,
                     seeds=(1, 2, 3), *, rates, tol_sec: float = TOL_SEC,
                     gen: dict | None = None, **overrides) -> dict[float, BenchResult]:
    """The loop behind every bench's ``evaluate_background_curve``.

    ``make`` and ``run`` are that bench's ``make_recording`` and ``run_detector``, so
    the slow and combined benches score across their own grids with this code rather
    than a copy of it.
    """
    out: dict[float, BenchResult] = {}
    for rate in rates:
        g = dict(gen or {})
        g["bg_rate_hz"] = float(rate)
        scores = []
        for seed in seeds:
            s, gt = make(regime, seed, **g)
            det = run(name, s, **overrides)
            scores.append(score_stream(gt, det, tol_sec=float(tol_sec)))
        out[float(rate)] = pool_scores(
            scores, detector=name, regime=regime, seeds=seeds,
            knob_value=overrides.get(operating_points[name].knob))
    return out


def background_spread(curve: dict[float, BenchResult]) -> float:
    """How much F1 moves across the axis — the number a bare F1 hides.

    Deliberately the full range rather than a slope or a fitted coefficient: the
    question a reader actually has is *"how wrong is this number if my slices are
    busier than the ones it was measured on"*, and the range answers it without
    assuming the curve has a shape.
    """
    f1s = [curve[r].f1 for r in sorted(curve)]
    return max(f1s) - min(f1s)


BACKGROUND_TOLERABLE_SPREAD = 0.05
"""Above this much movement across the grid, one F1 is not reportable alone.

Set at the scale of the differences the bake-off asks readers to believe: the top
two detectors there are **0.017** apart, so a score that swings several times that
with the background cannot be compared against its neighbour without naming where
on the axis both were measured.
"""


def describe_background(curve: dict[float, BenchResult]) -> str:
    """An F1 that carries the background it was measured at — human-facing.

    The counterpart of :func:`describe_curve`, refusing on the same principle:
    when the score still depends on the axis, say so rather than hand over a
    number that reads like a property of the detector.

    In practice this refuses for nearly every detector, and **that is the finding
    rather than a threshold set too tight** — the tolerance version usually
    settles, which is exactly the contrast worth seeing.
    """
    rates = sorted(curve)
    lo, hi = curve[rates[0]].f1, curve[rates[-1]].f1
    spread = background_spread(curve)
    if spread > BACKGROUND_TOLERABLE_SPREAD:
        return (f"F1 {lo:.3f} at {rates[0]*1000:g} mHz/ROI to {hi:.3f} at "
                f"{rates[-1]*1000:g} — spread {spread:.3f}, so this score "
                "depends on the background rate and is NOT one number")
    return (f"F1 {max(curve[r].f1 for r in rates):.3f}, flat across "
            f"{rates[0]*1000:g}–{rates[-1]*1000:g} mHz/ROI (spread {spread:.3f})")


def sweep(name: str, regime: str, seeds=(1, 2, 3), values=None, *,
          gen: dict | None = None) -> list[BenchResult]:
    """The sensitivity curve: one :class:`BenchResult` per knob value."""
    op = OPERATING_POINTS[name]
    values = op.grid if values is None else values
    return [evaluate(name, regime, seeds, gen=gen, **{op.knob: v})
            for v in values]


class EdgeOfRange(ValueError):
    """The best point found sits on the boundary of the grid that was searched.

    Not a warning. An optimum at the edge is not an optimum — it is the search
    telling you it stopped too early, and reporting it as a calibrated point is
    how a boundary value once got published upstream as one.
    """


MAX_PROBE_PER_MIN = {
    "coact": 1.0,      # measured: 0.08 — unmoved by the harder probe
    "loco": 1.0,       # measured: 0.21 — unmoved
    "sync": 9.0,       # measured: 5.54, was 0.2 at the old probe
    # HAND-SET from the separation window, not from the 1.6x rule, which would give 7.0
    # and disable the gate at the doubled probe: rate's F1-optimum fires 4.98/min and the
    # gate exists to refuse it. 4.5 is the midpoint of 3.83 (shipped, seeds 1-48) and 4.98
    # (that optimum), and it separates them on the test's own seed too (3.00 / 4.80).
    "rate": 4.5,       # measured: 3.83 shipped, 4.98 at the setting the gate refuses
    "sce": 9.0,        # measured: 5.92, was 5.6 — barely moved
    "cicada": 48.0,    # measured: 29.66, was 17.3 — still the most rate-fooled of the six
}
"""Firings per minute each detector may make inside a block containing nothing.

**Measured baselines, not aspirations** — the convention the regime-shift budgets
use. A detector that improves past its ceiling should have the ceiling tightened
in the commit that improves it.

⚠ **Three ceilings rose on 2026-09-22 because the PROBE rose, not because any
detector got worse.** ``hot_rate_hz`` went 0.06 → 0.1271 Hz when the probe became
the measured 99th percentile of baseline stretches, so the dense-but-random block
is twice as dense and a detector that keys on rate fires more inside it. Measured
at ``OPERATING_POINTS`` on seeds 1–48 by ``tools/measure_slow_budgets.py`` — the
same code path the search's admissibility test reads — and moved by that tool's own
``ceiling_rate``, ``max(1, ceil(1.6 x measured))``, **only where the old ceiling no
longer held**. ``coact``, ``loco`` and ``sce`` kept theirs.

**What the harder probe exposed, and the gentle one could not.** At 0.06 Hz five of
six looked quiet. At a realistic elevated stretch they separate:

=========  ==========  ==========  ========
detector   old probe   new probe   factor
=========  ==========  ==========  ========
coact         0.0         0.08     flat
loco          0.1         0.21     flat
sce           5.6         5.92     1.1x
rate          1.1         4.14     3.8x
cicada       17.3        29.66     1.7x
sync          0.2         5.54     **28x**
=========  ==========  ==========  ========

**CoactDetect and LoCo do not key on rate at all.** SPIKE-synch does, and was
passing a 1.0 ceiling only because the probe was too gentle to ask.

⚠ **``rate`` is hand-set because the rule collided with the gate, and that collision
is itself the finding.** ``ceiling_rate`` gives 1.6x headroom over the shipped rate;
at the doubled probe that is 7.0, and rate's own F1-optimum fires **4.98/min** — so
the rule would have put the ceiling *above* the setting
:func:`pick_operating_point` exists to refuse, and a re-calibration would have
selected it and called it an operating point (``test_rates_own_f1_optimum_is_over
_its_probe_budget`` is that case). **At this probe rate+context's shipped setting
sits within about 10% of the setting its gate refuses** — 3.83 against 4.98 — so
there is no longer room for 1.6x headroom. 4.5 is the midpoint, checked to separate
on seeds 1–48 *and* on the test's own seed. A budget's job is to sit between an
acceptable setting and a promiscuous one; where a headroom rule cannot, the window
wins.

⚠ It sits beside the other thing measured that day: SPIKE-synch is also the
detector that stays flat across the background axis and takes the top at its busy
end (``tests/test_background_curve.py``). Flatness that reads as robustness on one
axis and as rate-keying on the other is **one observation, not two**, and which it
is has not been decided here. Raising this ceiling records a measurement; it does
not bless the setting.

**These lived in `tests/test_bench.py` until 2026-08-22, and that was the defect.**
The test caught a regression at the *shipped* operating point, but
:func:`pick_operating_point` — the thing that *chooses* the shipped operating
point — had no notion of an acceptable probe rate. So a sweep could select a
promiscuous setting and nothing objected: the probe could fail a detector, but it
could not fail a **calibration**, which is where operating points come from.

What is deliberately still true: the probe stays **out of F1**. Folding it in makes
the headline measure how hard the probe was set rather than how good the detector
is — CICADA reads F1 0.09 that way against 0.68 upstream, on 599 hot-window
detections out of 601 false alarms. The fix for "the alarm cannot ring" is to give
the probe a gate at selection time, not to corrupt the score.
`docs/todo/2026-08-16-promiscuity-probe-cannot-fail.md`.
"""

MAX_PRECISION_DROP = {
    "loco": 0.10,      # measured: 0.01
    "coact": 0.10,     # measured: 0.01
    "rate": 0.10,      # measured: 0.01
    "sync": 0.10,      # measured: 0.01
    "cicada": 0.20,    # measured: 0.10
    "sce": 0.50,       # measured: 0.46 — a real degradation, recorded not excused
}
"""How far precision may differ between the quiet and busy backgrounds at one setting.

Tuned where events are easy to see, deployed where they are not: upstream measured
precision falling 90 -> 45 (RateDetect) and 75 -> 30 (spike-sync) when dense-tuned
settings met sparse data. **Moved here from ``tests/test_bench.py`` on 2026-09-16 for
the third time that day's reason** — a budget a test holds cannot gate a calibration.
Switching LoCo and CoactDetect to a sliding window broke it at their binned settings
(precision 0.53 busy against 0.67 quiet for LoCo), and ``tools/search_all_settings.py``
now refuses such a setting instead of proposing it.
"""

MAX_CROWDED_DROP = 0.02
"""How much mean F1 a candidate setting may lose on the CROWDED recordings, against the
setting it is proposed in place of.

**The fourth budget, and the first one a search could not have been stopped without.** On
2026-09-17 the every-knob search found large held-out gains for four of the six detectors —
binned SCE +0.305 mean F1, rate+context +0.134, CoactDetect +0.122, LoCo +0.113 — and every
one of them got there by running its **merge gap out to about a minute**. On a bench that
plants events at least 120 s apart, merging within 60 s costs nothing and tidies away
duplicate calls; on `make_tail_recording`, where planted events sit as little as 6 s apart,
it fuses real events. The same four settings lose **0.251 to 0.318** mean F1 there.

**The other three budgets cannot see it, and it is worth understanding why.** Merging makes
a detector call LESS, so a merge-happy setting looks *cleaner* on every false-alarm measure:
LoCo's empty-recording rate went 1.4 to 1.9 calls per hour against a limit of 3, well inside.
A budget counting false alarms cannot catch a setting whose flaw is that it answers a
different question — "was there coordination in the last minute" instead of "was there
coordination here".

**So the crowded recordings stop being only a report.** `bench.py` still forbids CALIBRATING
on them — nothing is chosen for scoring well there — but a candidate that scores worse there
than what it would replace is refused, in the search, before it can be proposed. Report and
veto are different powers, and this is the second.

⚠ **0.02 is a judgement, not a measurement.** It is meant to allow noise and refuse the
artifact, which on the numbers above is a gap of more than ten to one. Tony has not signed
it, and a detector genuinely better in both regimes will pass it easily.
"""

MAX_FALSE_POSITIVES_PER_HOUR = {
    "rate": 1.0,       # measured: 0.0
    "sync": 1.0,       # measured: 0.0
    "loco": 3.0,       # measured: 1.3
    "cicada": 6.0,     # measured: 3.1
    "sce": 6.0,        # measured: 3.1
    "coact": 7.0,      # measured: 4.4
}
"""Calls per hour each detector may report on :func:`make_null_recording`, where
nothing was planted at all (:func:`false_positives_per_hour`).

The **other** false-alarm budget, and not the same one as
:data:`MAX_PROBE_PER_MIN`: the probe is a dense stretch inside an ordinary bench
recording, this is a whole recording at the quiet background with nothing planted.
A detector can pass one and fail the other — binned SCE fires about 6 times a
minute in the probe at every threshold from 75 to 99.9, while on the empty
recording its threshold decides nearly everything.

**It lived in ``tests/test_bench.py`` until 2026-09-16 — the same defect the probe
budget above had until 2026-08-22.** A regression test at the shipped setting
cannot fail a calibration, so ``tools/retune_operating_points.py`` proposed a
binned-SCE setting reporting 32 calls an hour here against this budget of 6, and
found the budget only by failing it. Same convention as the probe: measured
baselines plus slack, tightened in the commit that improves on them.
"""


class TooPromiscuous(ValueError):
    """The best-scoring point on the sweep fires too often on nothing.

    Raised by :func:`pick_operating_point` when the F1-optimum exceeds that
    detector's :data:`MAX_PROBE_PER_MIN` ceiling. A third refusal for a third
    remedy: the grid is fine and the knob is binding, but the value that wins on
    F1 wins by firing into a block where nothing was planted.
    """


class DegenerateSweep(ValueError):
    """Every point on the grid scored identically — the knob did nothing.

    Distinct from :class:`EdgeOfRange` because the remedy is the opposite. There
    the grid was too narrow and the answer is to widen it; here the grid is
    irrelevant, because the parameter being swept is **not the one deciding the
    answer**, and widening it only produces more identical rows.

    The case this was written for is SPIKE-synch, recorded in
    ``docs/todo/2026-08-18-spike-synch-knob-may-not-be-the-knob.md``: the sweep
    moves ``C_threshold`` over ``(0.005 … 0.12)`` while ``C_min`` sits pinned at
    0.1 above most of that range, so the bin that *opens* an event gets cheaper
    while every bin that *sustains* one must still clear 0.1. The synchrony
    profile is also quantised at ``k/(n-1)``, so on a 30-ROI field every
    threshold below 1/29 is the same threshold. On a default simulation every
    value on the grid returned four detections and eleven misses.

    :func:`pick_operating_point` could not see it. Its plateau rule — an optimum
    is trustworthy if *some* optimal point has neighbours on both sides — is
    right for a **saturating** plateau (LoCo at F1 1.00 from 99.99 upward) and
    cannot distinguish that from a curve flat because nothing is happening: when
    every point ties, the whole grid is "optimal", interior points exist, and the
    first is returned as a calibrated setting. A boundary answer wearing a
    plateau's clothes. That is how SPIKE-synch answered 3 of 3 folds on the
    scoreboard while measuring nothing.

    **The test is a total tie, not "flat within noise"** — a stricter rule than
    first proposed, and deliberately. Partial ties are real and informative: the
    bench's own ``sweep("sync", "baseline_busy")`` moves F1 from 0.58 to 0.48
    across the upper half with the bottom three tied. Refusing "nearly flat"
    would need a noise model nobody has, and would refuse curves that carry
    information. An exact tie across every point cannot be a measurement of
    anything, so it is the case that can be refused without one.
    """


def _gate_on_probe(best: BenchResult, ceiling: float | None) -> BenchResult:
    """Refuse a winner that got there by firing where nothing was planted.

    ``-1.0`` is the sentinel for "look it up"; ``None`` disables the gate. The
    lookup is by detector name, so a curve for something not in
    :data:`MAX_PROBE_PER_MIN` passes rather than crashing — a new detector should
    not be un-calibratable until someone writes it a budget.
    """
    if ceiling is None:
        return best
    if ceiling == -1.0:
        ceiling = MAX_PROBE_PER_MIN.get(best.detector)
        if ceiling is None:
            return best
    rate = best.hot_fa_per_min
    if not np.isfinite(rate) or rate <= ceiling:
        return best
    raise TooPromiscuous(
        f"{best.detector}/{best.regime}: the best F1 on this sweep "
        f"({best.f1:.2f} at {best.knob_value:g}) fires {rate:.1f} times/min "
        f"inside a block containing no planted events, against a ceiling of "
        f"{ceiling:g}. That setting wins on F1 by keying on rate, so it is not "
        "an operating point. Tighten the detector or raise the ceiling "
        "deliberately — do not take the runner-up silently")


def pick_operating_point(curve: list[BenchResult], *,
                         max_probe_per_min: float | None = -1.0) -> BenchResult:
    """The F1-optimal point on a sweep, refusing a boundary answer.

    A *plateau* that reaches the edge is not a boundary answer. LoCo saturates
    at F1 1.00 from ``threshold_pctile`` 99.99 upward on this bench — recall and
    precision both stay at 1.00 — so the top of any grid is optimal and no
    amount of widening produces an interior peak. What makes an optimum
    trustworthy is that some optimal point has neighbours on both sides, not
    that the single argmax happens to sit inside. So the test is: if any point
    achieving the best F1 is interior, the grid bracketed the optimum and the
    first such point is returned; only when *every* optimal point is at an end
    is the search still climbing when it stopped.

    ``max_probe_per_min`` gates the choice on the **promiscuity probe**, which is
    what makes that probe able to fail a calibration rather than only a shipped
    setting. Default ``-1.0`` means *look the detector up in*
    :data:`MAX_PROBE_PER_MIN`; pass a number to override, or ``None`` to select on
    F1 alone the way this did before 2026-08-22.

    The gate is applied **after** the edge and degeneracy checks and **before**
    the answer is returned, so a sweep whose winner fires into a block containing
    nothing raises :class:`TooPromiscuous` instead of quietly becoming an
    operating point. It does not re-rank: a promiscuous winner is a refusal, not
    an invitation to take second place, because silently accepting a worse point
    is how a calibration stops being reproducible.
    """
    scored = [r for r in curve if np.isfinite(r.f1)]
    if not scored:
        raise ValueError("no point on the curve has a defined F1")
    if len(scored) == 1:
        return _gate_on_probe(scored[0], max_probe_per_min)

    best_f1 = max(r.f1 for r in scored)
    # Before asking WHERE the optimum sits, ask whether the sweep found one at
    # all. A grid whose every point ties has not measured the knob; see
    # DegenerateSweep. Checked first because such a curve also passes the
    # interior test below, which is exactly how it went unnoticed.
    if best_f1 - min(r.f1 for r in scored) <= 1e-9:
        d = scored[0]
        raise DegenerateSweep(
            f"{d.detector}/{d.regime}: every point on the "
            f"{OPERATING_POINTS[d.detector].knob} grid scores F1 {best_f1:.4f} "
            f"({len(scored)} values, {scored[0].knob_value:g}–"
            f"{scored[-1].knob_value:g}) — the swept parameter is not what is "
            "deciding the answer, so no value of it is an operating point. "
            "Widening this grid will not help; sweep the binding parameter "
            "instead, or sweep them together")
    optimal = [r for r in scored if r.f1 >= best_f1 - 1e-9]
    interior = [r for r in optimal if r is not scored[0] and r is not scored[-1]]
    if interior:
        return _gate_on_probe(interior[0], max_probe_per_min)

    end = "low" if optimal[0] is scored[0] else "high"
    best = optimal[0]
    raise EdgeOfRange(
        f"{best.detector}/{best.regime}: F1 peaks at the {end} end of the "
        f"{best.detector} {OPERATING_POINTS[best.detector].knob} grid "
        f"({best.knob_value:g}, F1 {best.f1:.2f}) — the search was still "
        "climbing when it stopped; widen the grid before calling this an "
        "operating point")


