"""The browser's SPIKE-synch against `bugarach.detectors.sync`, exactly.

The second detector on this page that draws no random numbers, and the second
one it is therefore allowed to carry. Like RateDetect, it is a pure function of
the event times: the browser port is either bit-identical to the Python or it is
wrong, and there is no sampling error for a bug to hide in. Everything here is
compared at 1e-9, the same bar the Python port holds against cSPIKE.

It is the harder of the two to get right, so it is checked in pieces rather than
only on the event list. The profile, the binned trace and the detections each get
their own comparison, so a failure says which stage moved — an adaptive window
computed slightly differently changes C for a handful of spikes and may still
call the same events, and a test that only looked at the event list would call
that agreement.

**One simulated recording does not reach every branch**, and the way to find
out which is to break the browser copy on purpose and see whether this file
notices. Eight mutations were tried. Six died on the simulated fixture alone.
One survived and is the reason `STALE_GAP` exists below: the scan re-tests a gap
it has not recomputed, and nothing in a simulated recording arranges the bins so
that the quirk changes the answer. That vector is pinned to the value the Python
produces rather than only to browser-equals-Python, so a tidy-up on either side
is caught.

The eighth survivor is an **equivalent** mutant, not a hole: deleting the
exact-tie shortcut changes nothing, because tau is always positive and the
neighbour test then accepts a separation of zero on its own. It is recorded here
so the next reader does not spend the afternoon writing a vector for it.

**CI runs this**, since 2026-08-19 — the runner installs chromium and
sets `BUGARACH_REQUIRE_BROWSER=1`, so a browser that goes missing fails
`test_browser_available.py` loudly rather than letting this skip quietly.
Without a browser locally it still skips.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pytest

from bugarach.detectors.sync import (adaptive_profile, binned_synchrony,
                                     sync_detect)
from bugarach.simulate import simulate_coordination

ROOT = Path(__file__).resolve().parents[1]
VIEWER = ROOT / "docs" / "site" / "raster_viewer.html"

DURATION = 900.0
GRID_DT = 0.1
# the operating point the bench ships for this detector (bench.OPERATING_POINTS)
PARAMS = dict(tau_max=0.25, max_gap=0.5, C_threshold=0.1, C_min=0.1)

SCRIPT = """(cfg) => {
  const opts = {tauMax: cfg.tauMax, maxGap: cfg.maxGap,
                CThreshold: cfg.cThr, CMin: cfg.cMin, gridDt: cfg.dt};
  const d = syncDetect(cfg.trains, cfg.tRange, opts);
  const p = adaptiveProfile(cfg.trains, cfg.tRange, cfg.tauMax);
  const bMax = binnedSynchrony(p.x, p.y, cfg.dt, cfg.tRange, "max");
  return {starts: d.starts, ends: d.ends, amps: d.amps, widths: d.widths,
          peakC: d.peakC, plat90: d.plat90,
          nParticipatingRois: d.nParticipatingRois,
          isArtifact: d.isArtifact, nTotalRois: d.nTotalRois,
          nEvents: d.nEvents,
          profileX: Array.from(d.profileX), profileY: Array.from(d.profileY),
          cx: Array.from(d.cx), cy: Array.from(d.cy), cn: Array.from(d.cn),
          maxCy: Array.from(bMax.cy), maxCn: Array.from(bMax.cn)};
}"""


@pytest.fixture(scope="module")
def run_in_browser():
    """One page for the whole file; each vector is one evaluate() on it."""
    pytest.importorskip("playwright.sync_api",
                        reason="the browser detector needs playwright")
    from playwright.sync_api import sync_playwright

    with sync_playwright() as p:
        try:
            browser = p.chromium.launch()
        except Exception as e:                        # noqa: BLE001
            pytest.skip(f"no chromium available: {type(e).__name__}")
        try:
            page = browser.new_page()
            errs: list[str] = []
            page.on("pageerror", lambda e: errs.append(str(e)))
            page.goto(VIEWER.as_uri())

            def run(trains, t_range, params=PARAMS, dt=GRID_DT):
                out = page.evaluate(SCRIPT, {
                    "trains": [list(map(float, v)) for v in trains],
                    "tRange": list(t_range), "dt": dt,
                    "tauMax": params["tau_max"], "maxGap": params["max_gap"],
                    "cThr": params["C_threshold"], "cMin": params["C_min"]})
                assert not errs, errs
                return out

            yield run
        finally:
            browser.close()


# ---------------------------------------------------------------- the vectors

@pytest.fixture(scope="module")
def trains():
    """A simulated recording — the realistic case, and the one that exercises
    the profile over hundreds of spikes."""
    s, _ = simulate_coordination(duration_sec=DURATION, n_roi=30,
                                 bg_rate_hz=0.03, n_per_level=(4, 4, 4),
                                 min_sep_sec=45.0, seed=7)
    return [np.asarray(v, dtype=float) for v in s.streams["events"].locs]


TIED = [np.array(sorted(set(
    list(np.arange(0.0, 60.0, 7.0) + 0.05 * (i % 2)) + [20.0, 20.05, 20.10])))
    for i in range(12)]
"""Twelve ROIs firing on the same 0.05 s frame grid, in two interleaved cohorts
with a shared burst. Every event it produces reaches C = 1.0 with every ROI
participating, which is the corner the simulated recording never visits: there,
coincidence is partial and the artifact rule fires on a minority of events, and
here it fires on six of ten at full saturation. It is the artifact criterion's
own regime rather than a coincidence-window test."""

STALE_GAP = [np.array([18.95, 19.50, 19.80, 21.25]),
             np.array([18.75, 19.55, 20.70])] + \
            [np.array([5.0 + 5.0 * k]) for k in range(8)]
"""Two ROIs carry one event; eight sit far apart and only set the denominator C
is a fraction of. It leaves nonzero bins at 18.7, 18.9, 19.4 and 19.5 s, which
is the arrangement where the scan's un-recomputed gap decides the answer: the
event ends at 19.4 s, and a version that recomputed the gap would run it to
19.5 s."""


@pytest.fixture(scope="module")
def py_detection(trains):
    return sync_detect(trains, (0.0, DURATION), dt=GRID_DT, **PARAMS)


@pytest.fixture(scope="module")
def js(run_in_browser, trains):
    return run_in_browser(trains, (0.0, DURATION))


# ------------------------------------------------- the simulated recording

def test_the_fixture_actually_exercises_the_detector(py_detection):
    """Two empty lists compare equal without comparing anything. Every other
    test in this file is near-vacuous unless the fixture detects something and
    the profile has structure to get wrong, so that is asserted first."""
    assert py_detection.locs.size >= 5, (
        f"only {py_detection.locs.size} detections — the comparisons below "
        f"would prove almost nothing")
    nonzero = np.count_nonzero(py_detection.profile_y)
    assert nonzero >= 50, (
        f"only {nonzero} spikes have a nonzero coincidence value — the "
        f"adaptive window is barely being exercised")
    assert py_detection.is_artifact.any(), "no event reaches the artifact rule"
    assert not py_detection.is_artifact.all(), "every event is an artifact"


def test_the_coincidence_profile_matches_to_1e9(js, trains):
    """The stage a mistake is likeliest to reach: an adaptive window computed a
    little differently moves C for a few spikes without necessarily changing any
    event boundary, so the event list alone would not notice."""
    px, py = adaptive_profile(trains, (0.0, DURATION), PARAMS["tau_max"])
    jx = np.asarray(js["profileX"], dtype=float)
    jy = np.asarray(js["profileY"], dtype=float)
    assert jx.shape == px.shape, f"{jx.shape} spikes vs {px.shape}"
    assert np.max(np.abs(jx - px)) == 0.0, "spike times differ"
    assert np.max(np.abs(jy - py)) < 1e-9, (
        f"worst |diff| in C: {np.max(np.abs(jy - py)):.3e}")


@pytest.mark.parametrize("stat", ["mean", "max"])
def test_the_binned_trace_matches_including_its_overwrite_rule(js, trains, stat):
    """The binning is not a histogram: same-time spikes aggregate, the group
    writes to the first centre within dt, and a later group overwrites an
    earlier one rather than adding to it. Cn carries the last writer's group
    size. Both statistics are checked because the viewer offers both."""
    px, py = adaptive_profile(trains, (0.0, DURATION), PARAMS["tau_max"])
    _, cy, cn = binned_synchrony(px, py, GRID_DT, (0.0, DURATION), stat)
    got_y = np.asarray(js["cy" if stat == "mean" else "maxCy"], dtype=float)
    got_n = np.asarray(js["cn" if stat == "mean" else "maxCn"], dtype=float)
    assert got_y.shape == cy.shape
    assert np.max(np.abs(got_y - cy)) < 1e-9, "binned synchrony differs"
    assert np.array_equal(got_n, cn), "the per-bin event count differs"


def test_the_bin_grid_is_matlabs_colon(js, trains):
    px, py = adaptive_profile(trains, (0.0, DURATION), PARAMS["tau_max"])
    cx, _, _ = binned_synchrony(px, py, GRID_DT, (0.0, DURATION), "mean")
    got = np.asarray(js["cx"], dtype=float)
    assert got.shape == cx.shape
    assert np.array_equal(got, cx), "the browser grid is not MATLAB's colon"


def test_the_same_events_are_detected(js, py_detection):
    assert js["nEvents"] == py_detection.locs.size, (
        f"browser found {js['nEvents']}, python found {py_detection.locs.size}")
    assert js["nTotalRois"] == py_detection.n_total_rois


@pytest.mark.parametrize("field", ["starts", "ends", "widths", "amps",
                                   "peakC", "plat90", "nParticipatingRois"])
def test_every_event_field_matches_to_1e9(js, py_detection, field):
    det = py_detection
    py = {"starts": det.locs,
          "ends": det.ends,
          "widths": det.widths,
          "amps": det.amps,
          "peakC": det.peak_C,
          "plat90": det.plat90,
          "nParticipatingRois": det.n_participating_rois}[field]
    got = np.asarray(js[field], dtype=float)
    assert got.shape == np.shape(py), f"{field}: {got.shape} vs {np.shape(py)}"
    if got.size:
        assert np.max(np.abs(got - py)) < 1e-9, (
            f"{field}: worst |diff| {np.max(np.abs(got - py)):.3e}")


def test_the_artifact_verdict_agrees_event_for_event(js, py_detection):
    """Three criteria have to hold together, so a disagreement here is a
    disagreement about one of peak C, the participating fraction, or the
    plateau width — all of which are compared above and would say which."""
    got = np.asarray(js["isArtifact"], dtype=bool)
    assert got.shape == py_detection.is_artifact.shape
    assert np.array_equal(got, py_detection.is_artifact)


# ------------------------------------------------ the hand-built vectors

def test_a_saturated_recording_agrees_including_its_artifact_verdicts(run_in_browser):
    """Every ROI in one bin, C pinned at 1.0, and the artifact rule firing on
    most of what is found — the opposite corner from the simulated fixture,
    where coincidence is partial. Saturation is asserted before it is used to
    check anything, so the vector cannot quietly stop being saturated."""
    span = (0.0, 60.0)
    px, py = adaptive_profile(TIED, span, PARAMS["tau_max"])
    assert py.max() == pytest.approx(1.0), "no spike is fully coincident"

    js = run_in_browser(TIED, span)
    jy = np.asarray(js["profileY"], dtype=float)
    assert jy.shape == py.shape
    assert np.max(np.abs(jy - py)) < 1e-9, (
        f"tied spikes disagree: worst |diff| {np.max(np.abs(jy - py)):.3e}")

    det = sync_detect(TIED, span, dt=GRID_DT, **PARAMS)
    assert det.locs.size >= 3, "the vector detects too little to compare"
    assert det.is_artifact.sum() >= 3, "saturation stopped reaching the rule"
    assert not det.is_artifact.all(), "every event is an artifact — no contrast"
    assert js["nEvents"] == det.locs.size
    assert np.max(np.abs(np.asarray(js["starts"]) - det.locs)) < 1e-9
    assert np.max(np.abs(np.asarray(js["ends"]) - det.ends)) < 1e-9
    assert np.array_equal(np.asarray(js["isArtifact"], dtype=bool),
                          det.is_artifact)


def test_the_scan_leaves_its_gap_stale_in_both_implementations(run_in_browser):
    """SpikyDetect3 does not recompute the gap after it accepts a bin, so a
    later re-test measures from a bin the event has already moved past. This
    vector is arranged so that quirk decides the answer, and the end time is
    pinned: recomputing the gap on either side runs the event to 19.5 s."""
    span = (0.0, 60.0)
    det = sync_detect(STALE_GAP, span, dt=GRID_DT, **PARAMS)
    assert det.locs.size == 1, f"expected one event, got {det.locs.size}"
    assert det.locs[0] == pytest.approx(18.7, abs=1e-9)
    assert det.ends[0] == pytest.approx(19.4, abs=1e-9), (
        "the Python scan stopped recomputing this gap — if that was deliberate "
        "the browser port and this vector both need revisiting")

    js = run_in_browser(STALE_GAP, span)
    assert js["nEvents"] == 1, f"the browser called {js['nEvents']} events"
    assert js["starts"][0] == pytest.approx(det.locs[0], abs=1e-9)
    assert js["ends"][0] == pytest.approx(det.ends[0], abs=1e-9)
    assert js["amps"][0] == pytest.approx(det.amps[0], abs=1e-9)
