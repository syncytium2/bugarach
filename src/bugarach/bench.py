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

MEASURED_RATE_SHAPE = 0.275
"""Gamma shape of the per-ROI background rate in real baseline windows.

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

⚠ **Not wired into the bench.** ``BENCH_RECORDING`` still runs a flat field, so
every operating point and every score in this package is still measured on the
old background. Switching it re-derives the whole bench and is not a default
change — see ``docs/todo/2026-08-14-generator-background-model-is-flat.md``.
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
        knob="sce_percentile", grid=(90.0, 99.0, 99.9, 99.99, 99.999, 99.9999, 99.99999)),
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


REGIMES: dict[str, dict] = {
    "baseline_quiet": dict(bg_rate_hz=0.0038),
    "baseline_busy": dict(bg_rate_hz=0.0175),
}
"""The difficulty axis, and **every value on it comes from untreated recordings.**

Both endpoints are the interquartile spread of the `all-baseline` flavour itself
(fast stream, `min_rois=4`): per-ROI rates of 0.0038 Hz at p25 and 0.0175 Hz at
p75, around a median of 0.0096. Untreated slices vary 4.6-fold among themselves,
and that variation is the axis an operating point has to survive.

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

The correction costs nothing, which is the part worth noticing: baseline's own
p25 (0.0038) lands within 5% of the TTX median (0.0040). The quiet end of the
range was reachable from untreated data the whole time, and reaching for a drug
to justify it added a confound in exchange for no information.

Senktide is absent entirely rather than held out. Holding it out still requires
generating a recording at senktide's rate, which is using a treatment as a source
of a coordination property. If a senktide evaluation is wanted it is a separate,
explicit decision, not a default of this module.
"""

NULL_RECORDING = dict(bg_rate_hz=0.0038, n_per_level=(0, 0, 0),
                      hot_window=None, hot_rate_hz=0.0, ramp_sec=0.0,
                      n_distractors=0)
"""A **synthetic** recording with no planted coordination — Poisson background at
the quiet end of baseline, and nothing else.

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
    n_roi=33,
    participation=(0.30, 0.18, 0.10),
    n_per_level=(5, 5, 5),
    jitter_sec=0.36,
    min_sep_sec=120.0,
    hot_window=(1200.0, 1500.0),
    hot_rate_hz=0.06,
    ramp_sec=30.0,
    n_distractors=6,
    distractor_frac=0.18,
    distractor_window=(120.0, 1100.0),
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
    """One bench recording. ``regime`` selects the background rate.

    Every regime here is derived from untreated recordings; there is no
    treatment regime to accept. See :data:`REGIMES`.
    """
    if regime not in REGIMES:
        raise ValueError(f"unknown regime {regime!r} — have {sorted(REGIMES)}")
    return simulate_coordination(
        seed=seed, **{**BENCH_RECORDING, **REGIMES[regime], **overrides})


def make_null_recording(seed: int, **overrides):
    """A recording with no planted coordination — background only.

    Returns the same ``(slice, ground_truth)`` pair as :func:`make_recording`,
    with ``gt.events`` empty. Nothing is scored against planted truth because
    there is none: every detection is a false positive *of this construction*.
    See :data:`NULL_RECORDING` for what that does and does not license.
    """
    return simulate_coordination(
        seed=seed, **{**BENCH_RECORDING, **NULL_RECORDING, **overrides})


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


MEASURED_BURST_SHAPE = (1.547, 1.388)
"""Gamma shapes of the per-bin rate multiplier, for `MEASURED_BURST_BINS`.

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

⚠ **Not wired into the bench**, exactly like `MEASURED_RATE_SHAPE`.
`BENCH_RECORDING` still runs a homogeneous background in both axes.
"""

MEASURED_BURST_BINS = (300.0, 60.0)
"""Bin widths (s) the shapes in `MEASURED_BURST_SHAPE` were fitted at."""
