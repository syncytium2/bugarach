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
    REGIMES,
    OPERATING_POINTS,
    BenchResult,
    CROWDED_RECORDING,
    CROWDING_GAP_SEC,
    MAX_PROBE_PER_MIN,
    DegenerateSweep,
    EdgeOfRange,
    TooPromiscuous,
    evaluate,
    false_positives_per_hour,
    make_crowded_recording,
    make_null_recording,
    make_recording,
    nearest_neighbour_gaps,
    pick_operating_point,
    run_detector,
    sweep,
)
from bugarach.detectors.rate import recording_extent, stream_trains

SEEDS = (1, 2)


@pytest.fixture(scope="module")
def bench():
    """Every detector on both regimes, computed once — each run is a 45-minute
    synthetic recording and there are twelve of them."""
    return {(name, regime): evaluate(name, regime, SEEDS)
            for name in DETECTORS for regime in ("baseline_quiet", "baseline_busy")}


# --- the regime-shift guard -------------------------------------------------
#
# Tuned where events are easy to see, deployed where they are not. Upstream
# measured precision falling 90 -> 45 (RateDetect) and 75 -> 30 (spike-sync)
# when dense-tuned settings met sparse data, and drew it as a figure.

MAX_PRECISION_DROP = {
    "loco": 0.10,      # measured: 0.01
    "coact": 0.10,     # measured: 0.01
    "rate": 0.10,      # measured: 0.01
    "sync": 0.10,      # measured: 0.01
    "cicada": 0.20,    # measured: 0.10
    "sce": 0.50,       # measured: 0.46 — a real degradation, recorded not excused
}


@pytest.mark.parametrize("name", DETECTORS)
def test_precision_survives_the_regime_shift(name, bench):
    quiet = bench[(name, "baseline_quiet")].precision
    normal = bench[(name, "baseline_busy")].precision
    drop = abs(normal - quiet)
    assert drop <= MAX_PRECISION_DROP[name], (
        f"{name}: precision {normal:.2f} (baseline) vs {quiet:.2f} (quiet), "
        f"a swing of {drop:.2f} against a budget of "
        f"{MAX_PRECISION_DROP[name]:.2f} — an operating point that only works "
        "at one background is not an operating point")


def test_sce_is_the_one_that_does_not_transfer():
    """Five of the six hold their precision across the background range; SCE
    does not, and the mechanism is visible in the no-planted-events test below.

    Its threshold is a *percentile over bins*, so it adapts to whatever it is
    given: on a quiet recording the top 1% of a mostly-empty histogram is still
    marked as events. Precision 0.91 at baseline, 0.33 at TTX-quiet, and the
    highest false-positive rate of the six on a recording with no coordination
    in it at all. Those are one fact seen twice.

    A threshold defined relative to the data cannot have a false-positive rate —
    it has a quantile, and the two are the same thing only when the data
    contains signal.
    """
    others = {k: v for k, v in MAX_PRECISION_DROP.items() if k != "sce"}
    assert max(others.values()) <= 0.20
    assert MAX_PRECISION_DROP["sce"] >= 0.5


# --- negative-class probes --------------------------------------------------
#
# The dense-but-random block has an elevated rate and no coordination in it, so
# every firing there is a detector keying on rate. The distractors are real
# cross-ROI coincidence that is not a coordinated event.

# The budgets moved into `bench.MAX_PROBE_PER_MIN` on 2026-08-22 and are imported
# rather than restated here. They had to move: while they lived only in this file
# the probe could fail a shipped setting but not the SWEEP that chooses one, and
# `pick_operating_point` selected on F1 alone.


@pytest.mark.parametrize("name", DETECTORS)
def test_promiscuity_probe_is_within_budget(name, bench):
    rate = bench[(name, "baseline_busy")].hot_fa_per_min
    assert rate <= MAX_PROBE_PER_MIN[name], (
        f"{name}: {rate:.1f} firings/min inside the dense-but-random block, "
        f"which contains no coordination by construction")


def test_the_probe_actually_separates_the_detectors(bench):
    """A probe everything passes is not a probe. The point of the block is that
    rate-keyed and coordination-keyed detectors answer it differently, so the
    spread across the six has to stay wide — if it narrows, the block stopped
    being dense enough to ask the question.

    **The "fooled" bound was 10.0/min and is 5.0 since 2026-08-20, because CICADA
    got stricter — not because the probe got weaker.** Retuning its FAST percentile
    99.99 -> 99.999 (the measurement is in `cicada.py`) cut its probe response from
    over 10/min to 6.9, and CICADA was most of what the old bound was measuring.

    **Raising `hot_rate_hz` instead was rejected**, though it would have restored the
    old number exactly — 0.08 puts the maximum back at 16.7/min.
    `bench.BENCH_RECORDING` justifies 0.06 as *6x measured baseline and 1.6x
    senktide: busier than any real condition in the table, which is the point,
    without leaving the physical world*, and warns in the same breath that a probe
    much more severe "stops asking whether a detector keys on rate and starts asking
    whether it survives an impossible surge". Turning the probe up until a
    better-tuned detector fails it again is that warning coming true.

    The spread is still asserted and still real: 0.0/min for LoCo and CoactDetect
    against 6.9 for CICADA. The bound now tracks the detectors instead of the
    detectors being held to a bound. If a later change pushes the top back above 10
    that is worth noticing, which is why this is lowered to what the probe actually
    separates rather than removed.
    """
    rates = [bench[(n, "baseline_quiet")].hot_fa_per_min for n in DETECTORS]
    assert min(rates) < 1.0, "no detector resists the probe — it is too severe"
    assert max(rates) > 5.0, "no detector is fooled by it — it is too mild"


def test_the_probe_stays_out_of_the_headline_numbers(bench):
    """Folding the probe into precision measures how hard the probe was set
    rather than how good the detector is: CICADA reads F1 0.09 that way, against
    0.68 in the upstream campaign, on 599 probe firings out of 601 false alarms.
    """
    cicada = bench[("cicada", "baseline_quiet")]
    assert cicada.hot_fa > 50, "the probe should be provoking CICADA"
    assert cicada.n_scored == cicada.n_detected - cicada.hot_fa
    assert cicada.f1 > 0.4, "the probe has leaked into the headline F1"


# --- the participant floor --------------------------------------------------

def test_recall_is_broken_down_by_participation(bench):
    """A detector that finds every all-ROI event and nothing at 50% is a
    different instrument from one that degrades gracefully, and the two share a
    headline recall."""
    for name in DETECTORS:
        by = bench[(name, "baseline_quiet")].by_frac
        assert set(by) == {0.30, 0.18, 0.10}, f"{name} lost a participation level"
        assert sum(n for n, _ in by.values()) == bench[(name, "baseline_busy")].n_planted


# --- the edge-of-range guard ------------------------------------------------

def _curve(f1s):
    out = []
    for i, f in enumerate(f1s):
        r = BenchResult(detector="loco", regime="baseline_quiet", knob_value=float(i),
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


def test_a_sweep_where_every_point_ties_is_refused():
    """The gap the plateau rule left open, and the one SPIKE-synch fell through.

    A totally flat curve passes the interior test — every point is "optimal", so
    interior points exist and the first is returned as a calibrated setting. But
    a knob that changes nothing has not been measured, and that is a different
    failure from a grid too narrow: widening produces more identical rows.
    `docs/todo/2026-08-18-spike-synch-knob-may-not-be-the-knob.md`."""
    with pytest.raises(DegenerateSweep, match="not what is deciding"):
        pick_operating_point(_curve([0.42, 0.42, 0.42, 0.42, 0.42, 0.42]))


def test_the_degenerate_refusal_says_to_sweep_something_else_not_to_widen():
    """The two refusals prescribe opposite remedies, so they must not be
    confused. EdgeOfRange says widen; this one says the range is irrelevant."""
    with pytest.raises(DegenerateSweep) as e:
        pick_operating_point(_curve([0.6] * 5))
    assert "widening this grid will not help" in str(e.value).lower(), str(e.value)
    assert "sweep the binding parameter" in str(e.value).lower(), str(e.value)


def test_a_partial_tie_is_still_an_answer():
    """Deliberately narrower than "flat within noise". Partial ties are real and
    carry information — the bench's own sync sweep on baseline_busy moves 0.58
    to 0.48 with its bottom three tied — so only a TOTAL tie is refused. Anything
    looser needs a noise model this project does not have."""
    best = pick_operating_point(_curve([0.48, 0.48, 0.48, 0.55, 0.58, 0.52]))
    assert best.f1 == pytest.approx(0.58), "the real peak, on a curve with ties"


def test_syncs_grid_is_mostly_degenerate_and_the_gate_does_not_catch_it():
    """Recorded as a measurement, because the gate above is narrower than the
    disease and that should be visible rather than implied.

    `DegenerateSweep` refuses a TOTAL tie, which cannot be a measurement of
    anything. SPIKE-synch's shipped grid on this regime is not a total tie — it
    is `[0.400, 0.400, 0.400, 0.400, 0.476, 0.316]`, so **four of six points are
    identical** and only the top two carry information. The gate stays silent and
    `pick_operating_point` returns a setting off a curve that is two-thirds flat.

    The cause is not the grid's width. `C_threshold` is swept from 0.005 while
    `C_min` sits pinned at 0.1, so below that every value opens events the
    sustain rule then throws away; and the synchrony profile is quantised at
    `k/(n-1)`, so on a 33-ROI field the low end is all one threshold.
    `docs/todo/2026-08-18-spike-synch-knob-may-not-be-the-knob.md`.

    **This test is expected to fail when that is fixed**, which is the point: the
    fix is to sweep `(C_threshold, C_min)` together on a grid scaled to ROI
    count, and when it lands, this assertion should be updated to record the new
    spread rather than deleted."""
    f1s = [r.f1 for r in sweep("sync", "baseline_quiet", seeds=(1,))]
    ties = max(sum(1 for x in f1s if abs(x - v) <= 1e-9) for v in f1s)
    assert ties >= 4, (
        f"sync's grid now has at most {ties} tied points, not the 4 recorded "
        f"here — if the grid was fixed, update this measurement: {f1s}")
    assert len({round(x, 9) for x in f1s}) > 1, (
        "a TOTAL tie would be caught by pick_operating_point; this records the "
        "partial case that is not")


@pytest.mark.parametrize("name", DETECTORS)
def test_the_declared_grid_brackets_its_own_optimum(name):
    """The edge-of-range guard against the grids actually shipped, not a
    synthetic curve. This is the check that caught LoCo's original grid, whose
    top value was still the best one.

    The promiscuity gate is disabled here on purpose: this test is about whether
    the grid BRACKETS its optimum, and `rate`'s optimum is separately known to be
    over its probe budget (see the test below). Leaving the gate on would make
    this fail for a reason it is not testing."""
    pick_operating_point(sweep(name, "baseline_quiet", seeds=(1,)),
                         max_probe_per_min=None)


# --- the probe can now fail a CALIBRATION, not just a shipped setting --------

def _probe_curve(f1s, probes):
    """A curve carrying a probe rate per point, for the selection gate.

    Probe firings are part of ``n_detected`` and are then excluded from the
    scored set (``n_scored = n_detected - hot_fa``), which is the whole shape of
    the defect: they leave both halves of precision. Building them as an extra on
    top instead pushes precision above 1."""
    out = []
    for i, (f, hot) in enumerate(zip(f1s, probes)):
        r = BenchResult(detector="rate", regime="baseline_quiet",
                        knob_value=float(i), n_planted=100,
                        n_detected=100 + hot, n_hit=int(round(f * 100)))
        r.hot_fa = hot
        out.append(r)
    return out


def test_a_promiscuous_winner_is_refused_rather_than_calibrated():
    """The hole this closes. A budget test catches a regression at the SHIPPED
    point; nothing watched the sweep that chooses one, so a calibration could
    select a setting that wins on F1 by firing where nothing was planted."""
    probe_min = BENCH_RECORDING["hot_window"]
    span = (probe_min[1] - probe_min[0]) / 60.0
    over = int((MAX_PROBE_PER_MIN["rate"] + 5) * span)
    with pytest.raises(TooPromiscuous, match="keying on rate"):
        pick_operating_point(
            _probe_curve([0.5, 0.9, 0.6], [0, over, 0]))


def test_the_gate_can_be_turned_off_for_a_check_that_is_not_about_it():
    """`None` restores the pre-2026-08-22 behaviour, so a test about bracketing
    can isolate bracketing."""
    probe_min = BENCH_RECORDING["hot_window"]
    span = (probe_min[1] - probe_min[0]) / 60.0
    over = int((MAX_PROBE_PER_MIN["rate"] + 5) * span)
    got = pick_operating_point(_probe_curve([0.5, 0.9, 0.6], [0, over, 0]),
                               max_probe_per_min=None)
    assert got.f1 == pytest.approx(0.9)


def test_a_clean_winner_still_passes():
    got = pick_operating_point(_probe_curve([0.5, 0.9, 0.6], [0, 0, 0]))
    assert got.f1 == pytest.approx(0.9)


def test_rates_own_f1_optimum_is_over_its_probe_budget():
    """Recorded as a measurement, because it is the case that proves the gate was
    needed rather than hypothetical.

    On `baseline_quiet`, `rate`'s best-F1 setting is `excess_threshold_hz=3`
    (F1 0.79), which fires ~3.6 times/min into a block containing no planted
    events, against its budget of 2.0. The SHIPPED value is 5.0 and is within
    budget — so nothing was broken in what ships, and a re-calibration would have
    chosen the promiscuous point and called it an operating point.

    **Expected to change when rate+context's threshold rule is fixed** (see
    `docs/forks.md` §3): a multiplicative bar drops its probe firings to zero. Update
    the measurement then rather than deleting the test."""
    curve = sweep("rate", "baseline_quiet", seeds=(1,))
    with pytest.raises(TooPromiscuous):
        pick_operating_point(curve)
    winner = pick_operating_point(curve, max_probe_per_min=None)
    assert winner.hot_fa_per_min > MAX_PROBE_PER_MIN["rate"]


# --- the bench can now exhibit reference-window contamination ---------------

def test_the_bench_recording_cannot_crowd_a_reference_window():
    """The gap, asserted so it cannot be forgotten again.

    `BENCH_RECORDING` plants events at least 120 s apart while a rolling
    detector's reference window spans ±30 s, so a second planted event can never
    land in the first one's context. The failure guard cells exist for is
    **impossible by construction** on the recording the six are scored on — which
    is why the regime-shift incident was found by hand and not by this suite."""
    assert BENCH_RECORDING["min_sep_sec"] > 2 * CROWDING_GAP_SEC, (
        "the bench recording can now crowd a reference window — if that is "
        "deliberate, every operating point derived on it needs re-deriving")


def test_the_crowded_recording_actually_crowds():
    """And the diagnostic that fills the gap. A floor on the spacing is not a
    target: at the bench's own event count, `min_sep_sec=14` still leaves a
    median gap near 70 s. The count is what crowds."""
    _, gt = make_crowded_recording("baseline_quiet", 1)
    t = np.sort([e.time for e in gt.events])
    gaps = np.diff(t)
    assert gaps.min() >= CROWDED_RECORDING["min_sep_sec"] - 1e-6
    crowded = nearest_neighbour_gaps(gt) < CROWDING_GAP_SEC
    assert crowded.mean() > 0.25, (
        f"only {crowded.sum()} of {crowded.size} events have a neighbour inside "
        "their own reference window — this recording cannot test masking")


def test_the_crowded_recording_contains_its_own_control():
    """The half of the design that was missing, and the reason it runs three hours.

    Crowding is a property of an **event**, not of a recording, so it is
    measurable within one — but only if the recording holds both populations. The
    first version planted the same 120 events in 45 minutes, which put every one
    of them inside a neighbour's reference window: no uncontaminated group
    anywhere in it, so the only available comparison was against a different
    recording, differing in event count and duration and therefore false-alarm
    opportunity all at once.

    Tony, 2026-08-23: *"shouldn't the two tests have the same number of events so
    F1 can be compared. who cares how long the recording has to be?"* Nobody does,
    and the length is what buys the control group.

    Both groups must stay large enough to compare — when the guard's recall gain
    turned out to be **flat across the gap**, which is the finding that killed the
    masking reading, the isolated group is what made it visible."""
    gaps = nearest_neighbour_gaps(make_crowded_recording("baseline_quiet", 1)[1])
    crowded = gaps < CROWDING_GAP_SEC
    isolated = gaps >= 2 * CROWDING_GAP_SEC
    assert crowded.mean() > 0.25 and isolated.mean() > 0.20, (
        f"{crowded.mean():.0%} crowded / {isolated.mean():.0%} isolated — this "
        "recording no longer carries its own control, and any crowding effect "
        "measured on it is confounded with whatever else differs from the bench")


def test_nearest_neighbour_gaps_are_column_aligned_with_the_score():
    """The one way to misuse it. `Score.hits` is in `gt.events` order and the
    planted times are not sorted, so sorting one without the other silently pairs
    each event's outcome with a different event's gap."""
    _, gt = make_crowded_recording("baseline_quiet", 1)
    gaps = nearest_neighbour_gaps(gt)
    assert gaps.shape == (len(gt.events),)
    t = np.asarray(gt.times)
    for i in (0, len(t) // 2, len(t) - 1):
        others = np.delete(t, i)
        assert gaps[i] == pytest.approx(np.abs(others - t[i]).min())


def test_the_crowded_recording_is_not_a_regime_anyone_can_calibrate_on():
    """It carries no promiscuity probe and no distractors on purpose: it asks one
    question. Keeping it out of REGIMES is what stops it being swept."""
    assert CROWDED_RECORDING["hot_window"] is None
    assert CROWDED_RECORDING["n_distractors"] == 0
    assert "crowded" not in REGIMES, (
        "the crowded recording is a diagnostic, not a difficulty axis — a corpus "
        "where every event has a neighbour is as unrepresentative as one where "
        "none does")


@pytest.mark.parametrize("regime", sorted(REGIMES))
def test_the_crowded_recording_stays_on_the_difficulty_axis(regime):
    """The door the docstring thought it had already shut.

    Every knob the author of `CROWDED_RECORDING` set deliberately is asserted
    above — the spacing, the absent hot window, the zero distractors. The one
    that came from a *default* was not, and it was the one that was wrong:
    `make_crowded_recording` merged no regime, so `bg_rate_hz` fell through to
    `simulate_coordination`'s 0.05 Hz — the pre-2026-08-13 invented value, ~10×
    `REGIMES`' quiet endpoint. Two thirds of the recall collapse the recording
    was said to demonstrate was that, not crowding
    (`docs/forks.md` §4b, and the todo it links).

    So this asserts the realised rate, not the keyword: a background that comes
    from anywhere other than the chosen regime fails here regardless of how it
    got in."""
    sl, gt = make_crowded_recording(regime, 1)
    trains = stream_trains(sl.streams["events"], recording_extent(sl))
    n_planted = sum(len(e.rois) for e in gt.events)
    realised = ((sum(len(t) for t in trains) - n_planted)
                / (CROWDED_RECORDING["duration_sec"] * CROWDED_RECORDING["n_roi"]))
    want = REGIMES[regime]["bg_rate_hz"]
    assert 0.6 * want < realised < 1.6 * want, (
        f"crowded recording at {regime!r} realises {realised:.4f} Hz/ROI of "
        f"background against the regime's {want:.4f} — it is off the difficulty "
        "axis, and any masking it appears to show is confounded with rate")


def test_a_curve_with_no_defined_f1_says_so():
    with pytest.raises(ValueError, match="no point on the curve"):
        pick_operating_point([BenchResult(detector="loco", regime="baseline_quiet")])


# --- the operating points themselves ----------------------------------------

@pytest.mark.parametrize("name", DETECTORS)
def test_every_operating_point_records_where_it_came_from(name):
    """A bench whose settings have no recorded origin cannot be compared to the
    MATLAB campaign, and cannot be re-derived when a calibration moves."""
    assert OPERATING_POINTS[name].source.strip()


@pytest.mark.parametrize("name", DETECTORS)
def test_the_swept_knob_is_a_real_parameter(name):
    op = OPERATING_POINTS[name]
    s, _ = make_recording("baseline_quiet", 1)
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

    _, gt = make_recording("baseline_quiet", 1)
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
    s, _ = make_recording("baseline_quiet", 1)
    assert not s.regions, (
        "the generator is annotating regions again — any named region triggers "
        "protocol windowing and silently shrinks what a region-scoped detector "
        "is allowed to look at")


def test_every_detector_sees_the_whole_recording():
    """The behavioural half of the test above: whatever the annotations say,
    no detector may be confined to a slice of the recording the others get."""
    s, _ = make_recording("baseline_quiet", 1)
    ext = (0.0, BENCH_RECORDING["duration_sec"])
    for name in DETECTORS:
        det = run_detector(name, s)
        onsets = getattr(det, "onset_sec", None)
        onsets = det.locs if onsets is None else onsets
        finite = np.asarray(onsets, dtype=float)
        finite = finite[np.isfinite(finite)]
        if finite.size < 5:
            continue          # too few detections to say anything about span
        span = finite.max() - finite.min()
        assert span > 0.45 * (ext[1] - ext[0]), (
            f"{name} only produced detections across {span:.0f}s of a "
            f"{ext[1] - ext[0]:.0f}s recording — check whether something is "
            "restricting its analysis window")


def test_the_schedule_is_not_metronomic():
    """Long recordings keep the null clean; they must not do it by pinning every
    interval to the floor. Regular spacing is a cue a training set would leak."""
    _, gt = make_recording("baseline_quiet", 1)
    intervals = np.diff(gt.times)
    assert intervals.std() / intervals.mean() > 0.3


# --- reproducibility --------------------------------------------------------

def test_the_bench_is_reproducible():
    """Same seeds, same numbers — on this machine and any other. A bench that
    drifts between runs cannot support a claim about a change."""
    a = evaluate("loco", "baseline_quiet", (1,))
    b = evaluate("loco", "baseline_quiet", (1,))
    assert (a.n_hit, a.n_fa, a.hot_fa) == (b.n_hit, b.n_fa, b.hot_fa)


# --- a recording with nothing planted in it ---------------------------------
#
# The claim is arithmetic, not biological: this generator planted no events, so
# a detector reporting one is reporting structure that was not put there. That
# makes it a useful false-positive floor and NOT a statement about any
# preparation. In particular it is not TTX — see bench.NULL_RECORDING, and
# foundations §15.1: coordination persists under TTX, and a detector returning
# little in a TTX window is not thereby validated.

MAX_FALSE_POSITIVES_PER_HOUR = {
    "rate": 1.0,       # measured: 0.0
    "sync": 1.0,       # measured: 0.0
    "loco": 3.0,       # measured: 1.3
    "cicada": 6.0,     # measured: 3.1
    "sce": 6.0,        # measured: 3.1
    "coact": 7.0,      # measured: 4.4
}


@pytest.mark.parametrize("name", DETECTORS)
def test_nothing_planted_means_little_reported(name):
    rate = false_positives_per_hour(name)
    assert rate <= MAX_FALSE_POSITIVES_PER_HOUR[name], (
        f"{name} reports {rate:.1f} coordinated events per hour in a recording "
        "where the generator planted none")


def test_the_null_recording_really_is_empty():
    """Guard the guard: if the null ever acquires planted events, every budget
    above silently becomes meaningless."""
    s, gt = make_null_recording(1)
    assert not gt.events and not gt.distractors
    assert gt.params.get("hot_window") is None


def test_no_treatment_is_a_source_for_any_coordination_property():
    """Tony, 2026-08-14: *"everything should be based on baseline recordings. do
    not use senk or ttx as sources for the properties of coordination."*

    Two earlier versions got this wrong in opposite directions — baseline ->
    senktide made the drug response the thing operating points were checked
    against, and the TTX-derived replacement was still a treatment, pooled
    across groups whose effects run in opposite directions. Both endpoints are
    now the interquartile spread of the untreated flavour itself.
    """
    assert set(REGIMES) == {"baseline_quiet", "baseline_busy"}
    for name, cfg in REGIMES.items():
        assert name.startswith("baseline_"), f"{name} is not a baseline regime"
    # the treatment medians, which must not appear as endpoints
    rates = {cfg["bg_rate_hz"] for cfg in REGIMES.values()}
    assert 0.0040 not in rates, "TTX median is being used as an endpoint"
    assert 0.0381 not in rates, "senktide median is being used as an endpoint"


def test_the_distractors_can_actually_discriminate():
    """A control every detector answers identically controls nothing.

    Until 2026-08-14 all six distractors were planted *inside* the promiscuity
    probe (``simulate_coordination`` falls back to ``hot_window`` when
    ``distractor_window`` is unset), and they recruited 50% of ROIs against a
    measured participation of 18% — so the negatives were stronger coincidence
    than any planted event, and every one of their firings was subtracted out of
    precision along with the probe. All six detectors hit 17-18 of 18 and no
    headline number moved.
    """
    hits = {n: evaluate(n, "baseline_quiet", SEEDS).distractor_hits
            for n in DETECTORS}
    assert max(hits.values()) - min(hits.values()) >= 5, (
        f"every detector answers the distractors the same way: {hits}")


def test_pool_scores_is_the_one_place_pooling_happens():
    """`evaluate` must be `pool_scores` plus a loop, and nothing else.

    A murderboard on 2026-08-16 found two tools pooling by hand as
    ``n_hit / n_detected`` while the six went through :func:`evaluate` and got
    the promiscuity probe excluded from their denominator. The two halves of a
    published comparison were on different metrics under a caption reading
    "scored by the same rule" — SCE reads precision 0.91 one way and 0.11 the
    other. Pooling is short enough to rewrite, which is exactly why it forked.
    This asserts the shared path still produces the shared answer.
    """
    from bugarach.bench import pool_scores
    from bugarach.score import score_stream

    for name in ("rate", "sce"):
        scores = []
        for seed in SEEDS:
            s, gt = make_recording("baseline_busy", seed)
            scores.append(score_stream(gt, run_detector(name, s)))
        pooled = pool_scores(scores, detector=name, regime="baseline_busy",
                             seeds=SEEDS)
        direct = evaluate(name, "baseline_busy", SEEDS)
        assert pooled.n_detected == direct.n_detected
        assert pooled.hot_fa == direct.hot_fa
        assert pooled.n_scored == direct.n_scored
        assert pooled.precision == pytest.approx(direct.precision)
        assert pooled.by_frac == direct.by_frac
        # and the probe really is being excluded, or this test proves nothing
        assert pooled.hot_fa > 0
        assert pooled.precision != pytest.approx(pooled.n_hit / pooled.n_detected)
