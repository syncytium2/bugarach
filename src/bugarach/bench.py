"""Score all six detectors against planted truth, at declared operating points.

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
from bugarach.score import score_stream
from bugarach.simulate import simulate_coordination

STREAM = "events"
"""The single-stream slice the generator emits (FOUNDATIONS §3)."""

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
"""


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
OPERATING_POINTS: dict[str, OperatingPoint] = {
    "loco": OperatingPoint(
        params=dict(bin_width_sec=1.0, context_win_sec=120.0, thr_step_sec=15.0,
                    merge_gap_sec=2.0, threshold_pctile=99.9, n_surrogates=100),
        source="measured-regime F1 optimum, FAST (loco_detect docstring)",
        knob="threshold_pctile", grid=(99.0, 99.5, 99.9, 99.99, 99.999, 99.9999)),
    "cicada": OperatingPoint(
        params=dict(sce_percentile=99.99, active_duration_sec=1.0, n_surrogates=100),
        source="calibrated FAST pair (cicada_detect docstring)",
        knob="sce_percentile", grid=(90.0, 99.0, 99.9, 99.99, 99.999, 99.9999)),
    "sce": OperatingPoint(
        params=dict(bin_width_sec=10.0, threshold_pctile=99.0, n_surrogates=200),
        source="sce_detect defaults (generate_sce contract)",
        knob="threshold_pctile", grid=(90.0, 95.0, 98.0, 99.0, 99.5, 99.9)),
    "coact": OperatingPoint(
        params=dict(int_win_sec=2.0, context_win_sec=60.0, alpha=1e-4,
                    n_surrogates=100),
        source="explore_sce viewer FAST point — NOT the coact_detect signature "
               "default of alpha=0.01, which scores F1 0.72 here",
        knob="alpha", grid=(1e-2, 1e-3, 1e-4, 1e-5, 1e-6, 1e-7)),
    "rate": OperatingPoint(
        params=dict(excess_threshold_hz=5.0, context_win=60.0, rate_win=1.0,
                    grid_dt=0.1),
        source="rate_detect defaults; grid_dt is the generator's own 0.1 s grid",
        knob="excess_threshold_hz", grid=(0.5, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 8.0),
        takes_rng=False),
    "sync": OperatingPoint(
        params=dict(tau_max=0.25, max_gap=0.5, C_threshold=0.1, C_min=0.1),
        source="viewer FAST defaults (sync_detect docstring)",
        knob="C_threshold", grid=(0.005, 0.01, 0.02, 0.04, 0.08, 0.12),
        takes_rng=False),
}

DETECTORS = tuple(OPERATING_POINTS)


# The two regimes are the ones calibrate6.m separates, and they are the axis the
# regime-shift guard shifts along: an operating point tuned where events are easy
# to see must still work where they are not.
REGIMES: dict[str, dict] = {
    "baseline": dict(bg_rate_hz=0.0096),
    "senktide": dict(bg_rate_hz=0.0381),
}
"""The two regimes, and both numbers are **measured**, not chosen.

Per-ROI rate medians from `constellation/coordination_timescale_summary.csv`
(`roiRate_mean_med`, fast stream): `all-baseline` 0.0096 Hz, `all-senktide`
0.0381 Hz. The full range across flavours runs 0.0040 (ORX, TTX) to 0.0381
(senktide), so this pair brackets it about as widely as real data allows.

They replace an invented `sparse=0.05 / dense=0.15`, which sat **entirely above
the measured range** — every bench score before 2026-08-13 was taken on a
background 5–15× busier than any real recording.
"""

# Measured off 84 baseline slices — see MEASURED_PROVENANCE below. These are the
# numbers the review document was going to ask Tony for; they already existed.
BENCH_RECORDING = dict(
    duration_sec=2700.0,
    n_roi=33,
    participation=(0.30, 0.18, 0.10),
    n_per_level=(5, 5, 5),
    jitter_sec=0.36,
    min_sep_sec=120.0,
    hot_window=(1200.0, 1500.0),
    hot_rate_hz=0.06,
    ramp_sec=30.0,
    n_distractors=6,
    distractor_frac=0.5,
)
"""The recording every bench run is scored on.

Its structural values are **measured off real recordings**, not invented. Until
2026-08-13 they were guesses, and every one of them made coordination easier
than it is:

===================  ==========  =============================  ==============
knob                 was         measured                       effect
===================  ==========  =============================  ==============
``n_roi``            30          ~33                            (was right)
``bg_rate_hz``       0.05 Hz     0.0096 Hz/ROI                  5× too busy
``jitter_sec``       0.05 s      0.36 s                         7× too tight
``participation``    50–100%     6 of ~33 ROI = 18%             3–6× too many
===================  ==========  =============================  ==============

The consequence was not subtle. On the invented values every detector scored
F1 ≈ 0.9–1.0 and the bench could not tell them apart; on the measured ones they
range 0.20–0.75 and separate sharply, because a real coordinated event recruits
about **six ROIs with a third of a second of spread** — which sits just above
the ``min_rois`` floor the detectors ship with. That is the regime the
instruments were designed for, and it is where they differ.

``participation`` keeps a spread (30 / 18 / 10%) around the measured median
rather than collapsing to it, so recall still resolves a participant floor. The
10% level is ~3 ROIs, at the floor itself.

``hot_rate_hz`` moved with them. At 0.30 it was 6x the invented background and
**31x the measured one** — a probe that severe stops asking whether a detector
keys on rate and starts asking whether it survives an impossible surge. 0.06 is
6x measured baseline and 1.6x senktide: busier than any real condition in the
table, which is the point, without leaving the physical world.

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

The hot window is dense-but-random with no planted events (a rate-fooled
detector fires there) and the distractors are correlated bursts that are real
coincidence but not coordination. Both are negatives with no recall value; they
exist so the bench can fail a detector for firing on them.
"""


def make_recording(regime: str, seed: int, **overrides):
    """One bench recording. ``regime`` selects the background rate."""
    if regime not in REGIMES:
        raise ValueError(f"unknown regime {regime!r} — have {sorted(REGIMES)}")
    return simulate_coordination(
        seed=seed, **{**BENCH_RECORDING, **REGIMES[regime], **overrides})


def run_detector(name: str, s, *, rng_seed: int = 20260706, **overrides):
    """Run one detector on a slice at its declared operating point.

    Absorbs the two call shapes — three detectors take a ``Slice`` and run every
    stream, three take one stream's trains plus the extent — so callers work in
    detector names rather than signatures.
    """
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
    by_frac: dict = field(default_factory=dict)
    seeds: tuple = ()

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

    def recall_at(self, frac: float) -> float:
        """Recall at one participation level — the participant-floor axis."""
        n, h = self.by_frac.get(frac, (0, 0))
        return h / n if n else float("nan")

    @property
    def hot_fa_per_min(self) -> float:
        """The promiscuity probe's own number: firings per minute inside the
        dense-but-random block, where by construction there is nothing to find."""
        span = BENCH_RECORDING["hot_window"]
        minutes = (span[1] - span[0]) / 60.0 * max(1, len(self.seeds))
        return self.hot_fa / minutes if minutes else float("nan")

    def summary(self) -> str:
        knob = "" if self.knob_value is None else f" @{self.knob_value:g}"
        by = " ".join(f"{int(f * 100)}%:{self.recall_at(f):.2f}"
                      for f in sorted(self.by_frac, reverse=True))
        return (f"{self.detector:6}/{self.regime:6}{knob}  recall {self.recall:.2f}  "
                f"precision {self.precision:.2f}  F1 {self.f1:.2f}  "
                f"FA {self.n_fa - self.hot_fa}  |  probe {self.hot_fa_per_min:5.1f}/min  "
                f"distractor {self.distractor_hits}   [{by}]")


def evaluate(name: str, regime: str, seeds=(1, 2, 3), *, tol_sec: float = 1.5,
             **overrides) -> BenchResult:
    """Run one detector over several seeds and pool the outcome."""
    out = BenchResult(detector=name, regime=regime,
                      knob_value=overrides.get(OPERATING_POINTS[name].knob),
                      seeds=tuple(seeds))
    for seed in seeds:
        s, gt = make_recording(regime, seed)
        det = run_detector(name, s, **overrides)
        sc = score_stream(gt, det, tol_sec=tol_sec)
        out.n_planted += sc.n_planted
        out.n_detected += sc.n_detected
        out.n_hit += sc.n_hit
        out.n_fa += sc.n_fa
        out.hot_fa += sc.hot_fa
        out.distractor_hits += sc.distractor_hits
        for frac, (n, h) in sc.by_frac.items():
            pn, ph = out.by_frac.get(frac, (0, 0))
            out.by_frac[frac] = (pn + n, ph + h)
    return out


def sweep(name: str, regime: str, seeds=(1, 2, 3), values=None) -> list[BenchResult]:
    """The sensitivity curve: one :class:`BenchResult` per knob value."""
    op = OPERATING_POINTS[name]
    values = op.grid if values is None else values
    return [evaluate(name, regime, seeds, **{op.knob: v}) for v in values]


class EdgeOfRange(ValueError):
    """The best point found sits on the boundary of the grid that was searched.

    Not a warning. An optimum at the edge is not an optimum — it is the search
    telling you it stopped too early, and reporting it as a calibrated point is
    how a boundary value once got published upstream as one.
    """


def pick_operating_point(curve: list[BenchResult]) -> BenchResult:
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
    """
    scored = [r for r in curve if np.isfinite(r.f1)]
    if not scored:
        raise ValueError("no point on the curve has a defined F1")
    if len(scored) == 1:
        return scored[0]

    best_f1 = max(r.f1 for r in scored)
    optimal = [r for r in scored if r.f1 >= best_f1 - 1e-9]
    interior = [r for r in optimal if r is not scored[0] and r is not scored[-1]]
    if interior:
        return interior[0]

    end = "low" if optimal[0] is scored[0] else "high"
    best = optimal[0]
    raise EdgeOfRange(
        f"{best.detector}/{best.regime}: F1 peaks at the {end} end of the "
        f"{best.detector} {OPERATING_POINTS[best.detector].knob} grid "
        f"({best.knob_value:g}, F1 {best.f1:.2f}) — the search was still "
        "climbing when it stopped; widen the grid before calling this an "
        "operating point")
