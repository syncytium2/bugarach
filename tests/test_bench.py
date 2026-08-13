"""The coordination bench, and the guards that make it fail rather than plot.

`docs/simulation_plan.md` §8: *the precision-collapse figure is a test that was
drawn as a picture.* Had it been an assertion from the start, the dense
benchmark would have failed on day one instead of after two weeks of tuning
against it. These are the assertions.

The budgets below are **measured baselines, not aspirations**. They record what
each detector does today so that a change is visible; two of the six genuinely
collapse when the background triples, and pretending otherwise by setting a
tight budget everywhere would only mean deleting the test later. A detector that
improves past its budget should have the budget tightened in the same commit
that improves it.
"""

import numpy as np
import pytest

from bugarach.bench import (
    BENCH_RECORDING,
    DETECTORS,
    OPERATING_POINTS,
    BenchResult,
    EdgeOfRange,
    evaluate,
    make_recording,
    pick_operating_point,
    run_detector,
    sweep,
)

SEEDS = (1, 2)


@pytest.fixture(scope="module")
def bench():
    """Every detector on both regimes, computed once — each run is a 45-minute
    synthetic recording and there are twelve of them."""
    return {(name, regime): evaluate(name, regime, SEEDS)
            for name in DETECTORS for regime in ("baseline", "senktide")}


# --- the regime-shift guard -------------------------------------------------
#
# Tuned where events are easy to see, deployed where they are not. Upstream
# measured precision falling 90 -> 45 (RateDetect) and 75 -> 30 (spike-sync)
# when dense-tuned settings met sparse data, and drew it as a figure.

MAX_PRECISION_DROP = {
    "loco": 0.15,      # measured: 0.06 (0.92 -> 0.86)
    "coact": 0.10,     # measured: none, precision rises 0.72 -> 0.77
    "sce": 0.10,       # measured: none, 0.91 -> 1.00
    "cicada": 0.20,    # measured: 0.11
    "rate": 0.35,      # measured: 0.26 — the largest, and no longer a collapse
    "sync": 0.20,      # measured: 0.12
}


@pytest.mark.parametrize("name", DETECTORS)
def test_precision_survives_the_regime_shift(name, bench):
    sparse = bench[(name, "baseline")].precision
    dense = bench[(name, "senktide")].precision
    drop = sparse - dense
    assert drop <= MAX_PRECISION_DROP[name], (
        f"{name}: precision {sparse:.2f} -> {dense:.2f} when the background "
        f"triples, a drop of {drop:.2f} against a budget of "
        f"{MAX_PRECISION_DROP[name]:.2f}")


def test_nothing_collapses_on_measured_regimes():
    """The precision collapse was an artifact of invented regimes.

    On the old bench, RateDetect fell 0.68 -> 0.13 precision and spike-sync
    0.44 -> 0.03, which read as reproducing the upstream deploy-cost figure. But
    those regimes were bg 0.05 -> 0.15 Hz/ROI, and the measured range is
    0.0040-0.0381 — the whole shift happened above anything real. Re-run between
    measured baseline and senktide, the largest drop in the six is RateDetect's
    0.26 and nothing collapses.

    That does not retract the upstream finding, which was about settings *tuned*
    in one regime meeting the other; this bench holds settings fixed. It does
    mean the bench cannot claim to have reproduced it, and the budgets above are
    now tight enough that a real collapse would fail rather than fit.
    """
    assert max(MAX_PRECISION_DROP.values()) <= 0.35


# --- negative-class probes --------------------------------------------------
#
# The dense-but-random block has an elevated rate and no coordination in it, so
# every firing there is a detector keying on rate. The distractors are real
# cross-ROI coincidence that is not a coordinated event.

MAX_PROBE_PER_MIN = {
    "loco": 3.0,       # measured: 1.1
    "coact": 3.0,      # measured: 1.2
    "rate": 4.0,       # measured: 1.6
    "sync": 4.0,       # measured: 1.6
    "sce": 10.0,       # measured: 5.5
    "cicada": 20.0,    # measured: 13.3 — still the most rate-fooled of the six
}


@pytest.mark.parametrize("name", DETECTORS)
def test_promiscuity_probe_is_within_budget(name, bench):
    rate = bench[(name, "baseline")].hot_fa_per_min
    assert rate <= MAX_PROBE_PER_MIN[name], (
        f"{name}: {rate:.1f} firings/min inside the dense-but-random block, "
        f"which contains no coordination by construction")


def test_the_probe_actually_separates_the_detectors(bench):
    """A probe everything passes is not a probe. The point of the block is that
    rate-keyed and coordination-keyed detectors answer it differently, so the
    spread across the six has to stay wide — if it narrows, the block stopped
    being dense enough to ask the question."""
    rates = [bench[(n, "baseline")].hot_fa_per_min for n in DETECTORS]
    assert min(rates) < 2.0, "no detector resists the probe — it is too severe"
    assert max(rates) > 10.0, "no detector is fooled by it — it is too mild"


def test_the_probe_stays_out_of_the_headline_numbers(bench):
    """Folding the probe into precision measures how hard the probe was set
    rather than how good the detector is: CICADA reads F1 0.09 that way, against
    0.68 in the upstream campaign, on 599 probe firings out of 601 false alarms.
    """
    cicada = bench[("cicada", "baseline")]
    assert cicada.hot_fa > 100, "the probe should be provoking CICADA"
    assert cicada.n_scored == cicada.n_detected - cicada.hot_fa
    assert cicada.f1 > 0.5, "the probe has leaked into the headline F1"


# --- the participant floor --------------------------------------------------

def test_recall_is_broken_down_by_participation(bench):
    """A detector that finds every all-ROI event and nothing at 50% is a
    different instrument from one that degrades gracefully, and the two share a
    headline recall."""
    for name in DETECTORS:
        by = bench[(name, "baseline")].by_frac
        assert set(by) == {0.30, 0.18, 0.10}, f"{name} lost a participation level"
        assert sum(n for n, _ in by.values()) == bench[(name, "baseline")].n_planted


# --- the edge-of-range guard ------------------------------------------------

def _curve(f1s):
    out = []
    for i, f in enumerate(f1s):
        r = BenchResult(detector="loco", regime="baseline", knob_value=float(i),
                        n_planted=100, n_detected=100, n_hit=0)
        # F1 is derived, so drive it through the counts: hits set both halves
        r.n_hit = int(round(f * 100))
        out.append(r)
    return out


def test_an_optimum_inside_the_grid_is_returned():
    best = pick_operating_point(_curve([0.5, 0.8, 0.9, 0.7, 0.4]))
    assert best.f1 == pytest.approx(0.9)


def test_an_optimum_at_the_top_of_the_grid_is_refused():
    """An optimum on the boundary is the search saying it stopped too early.
    Upstream published one; this raises instead."""
    with pytest.raises(EdgeOfRange, match="high end"):
        pick_operating_point(_curve([0.4, 0.6, 0.7, 0.8, 0.9]))


def test_an_optimum_at_the_bottom_of_the_grid_is_refused():
    with pytest.raises(EdgeOfRange, match="low end"):
        pick_operating_point(_curve([0.9, 0.8, 0.7, 0.6, 0.4]))


def test_a_plateau_reaching_the_edge_is_not_an_edge_optimum():
    """LoCo saturates at F1 1.00 above threshold_pctile 99.99 — recall and
    precision both stay at 1.00, so the top of any grid is optimal and widening
    never produces an interior peak. What makes an optimum trustworthy is that
    some optimal point has neighbours on both sides."""
    best = pick_operating_point(_curve([0.4, 0.6, 0.9, 1.0, 1.0, 1.0]))
    assert best.knob_value == 3, "the first optimal point with both neighbours"


@pytest.mark.parametrize("name", DETECTORS)
def test_the_declared_grid_brackets_its_own_optimum(name):
    """The edge-of-range guard against the grids actually shipped, not a
    synthetic curve. This is the check that caught LoCo's original grid, whose
    top value was still the best one."""
    pick_operating_point(sweep(name, "baseline", seeds=(1,)))


def test_a_curve_with_no_defined_f1_says_so():
    with pytest.raises(ValueError, match="no point on the curve"):
        pick_operating_point([BenchResult(detector="loco", regime="baseline")])


# --- the operating points themselves ----------------------------------------

@pytest.mark.parametrize("name", DETECTORS)
def test_every_operating_point_records_where_it_came_from(name):
    """A bench whose settings have no recorded origin cannot be compared to the
    MATLAB campaign, and cannot be re-derived when a calibration moves."""
    assert OPERATING_POINTS[name].source.strip()


@pytest.mark.parametrize("name", DETECTORS)
def test_the_swept_knob_is_a_real_parameter(name):
    op = OPERATING_POINTS[name]
    s, _ = make_recording("baseline", 1)
    run_detector(name, s, **{op.knob: op.grid[0]})   # raises on an unknown kwarg


@pytest.mark.parametrize("name", DETECTORS)
def test_the_grid_brackets_the_operating_point(name):
    """A grid that does not span its own operating point cannot show whether
    that point is a peak or the edge of the search."""
    op = OPERATING_POINTS[name]
    if op.knob not in op.params:
        pytest.skip(f"{name}: {op.knob} is not pinned in the operating point")
    lo, hi = min(op.grid), max(op.grid)
    assert lo <= op.params[op.knob] <= hi


def test_the_signature_default_is_not_assumed_to_be_calibrated():
    """The trap the registry exists for. coact_detect defaults to the MATLAB
    function's alpha=0.01; explore_sce's FAST point is 1e-4, and the difference
    is F1 0.72 against 1.00. A bench that read the signature would have
    published the first number as CoactDetect's performance."""
    from bugarach.detectors.coact import coact_detect
    import inspect
    signature_default = inspect.signature(coact_detect).parameters["alpha"].default
    assert OPERATING_POINTS["coact"].params["alpha"] != signature_default


def test_the_bench_recording_keeps_the_null_clean():
    """The contaminated null, mechanized: events spaced more tightly than the
    widest context window put real coordination inside the null the threshold is
    estimated from. That is what made the first upstream benchmark unusable."""
    widest_context = max(
        op.params.get("context_win_sec", op.params.get("context_win", 0.0))
        for op in OPERATING_POINTS.values())
    assert BENCH_RECORDING["min_sep_sec"] >= widest_context

    _, gt = make_recording("baseline", 1)
    intervals = np.diff(gt.times)
    assert intervals.min() >= widest_context * 0.9, (
        f"realized spacing {intervals.min():.0f}s is inside the {widest_context:.0f}s "
        "context window — the null is contaminated")


def test_the_generator_does_not_impose_an_experimental_protocol():
    """The generator used to stamp every recording with a region named
    ``baseline`` spanning the whole duration. That reads as harmless metadata
    and is not: ``baseline`` is a wet-lab protocol label, and the region
    windowing rules trim such a region to its final 1200 s. SCE honours the
    trim, so it analysed 1500-2700 s of a 45-minute recording while being scored
    against the 15 events planted across all of it — a recall ceiling of 7/15,
    measured at 0.40, which read as a weak detector rather than as a detector
    shown 44% of the data. Removing it took SCE to 0.73-0.87 and moved LoCo and
    CICADA not at all.

    Every detector must see the same recording, or the bench is not comparing
    them. A synthetic recording has no baseline and no treatment period.
    """
    s, _ = make_recording("baseline", 1)
    assert not s.regions, (
        "the generator is annotating regions again — any named region triggers "
        "protocol windowing and silently shrinks what a region-scoped detector "
        "is allowed to look at")


def test_every_detector_sees_the_whole_recording():
    """The behavioural half of the test above: whatever the annotations say,
    no detector may be confined to a slice of the recording the others get."""
    s, _ = make_recording("baseline", 1)
    ext = (0.0, BENCH_RECORDING["duration_sec"])
    for name in DETECTORS:
        det = run_detector(name, s)
        onsets = getattr(det, "onset_sec", None)
        onsets = det.locs if onsets is None else onsets
        finite = np.asarray(onsets, dtype=float)
        finite = finite[np.isfinite(finite)]
        if finite.size < 2:
            continue
        span = finite.max() - finite.min()
        assert span > 0.5 * (ext[1] - ext[0]), (
            f"{name} only produced detections across {span:.0f}s of a "
            f"{ext[1] - ext[0]:.0f}s recording — check whether something is "
            "restricting its analysis window")


def test_the_schedule_is_not_metronomic():
    """Long recordings keep the null clean; they must not do it by pinning every
    interval to the floor. Regular spacing is a cue a training set would leak."""
    _, gt = make_recording("baseline", 1)
    intervals = np.diff(gt.times)
    assert intervals.std() / intervals.mean() > 0.3


# --- reproducibility --------------------------------------------------------

def test_the_bench_is_reproducible():
    """Same seeds, same numbers — on this machine and any other. A bench that
    drifts between runs cannot support a claim about a change."""
    a = evaluate("loco", "baseline", (1,))
    b = evaluate("loco", "baseline", (1,))
    assert (a.n_hit, a.n_fa, a.hot_fa) == (b.n_hit, b.n_fa, b.hot_fa)
