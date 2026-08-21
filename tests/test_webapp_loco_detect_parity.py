"""The browser's LoCo against `bugarach.detectors.loco` — exactly where it can be.

The first detector on this page that **guesses**. RateDetect and SPIKE-synch are
pure functions of the data, so their ports are compared bit for bit. LoCo
estimates its threshold by shuffling the data a hundred times and taking a high
percentile of the result, and this page's random source is not numpy's — so two
correct implementations disagree, by sampling error, permanently.

That is not a licence to test it loosely. The detector splits three ways and only
one of them is soft:

* **the observed statistic** — distinct ROIs per bin — depends on nothing but the
  data. Compared at **1e-9**, along with the bin grid it sits on.
* **the threshold** — sampled. Compared loosely and *reported*, never asserted
  tightly. A test that demanded agreement here would be testing the random
  number generators.
* **the detections** — deterministic *given* a threshold. So the same threshold
  vector is injected into both implementations and the events are compared at
  **1e-9**: onsets, ends, widths, magnitude, recruitment.

The injection is the part worth keeping. Without it the only comparison available
would be "both found roughly the same number of events", which would pass on a
port that merged runs wrongly, took the last maximum instead of the first, or
mis-set an episode's recruitment — every one of which is a real way to be wrong
that has nothing to do with sampling.

**Called one window at a time.** The browser runs LoCo per analysis segment, so
Python is called the same way — one region spanning the window — and the region
clamp is a no-op on both sides. That makes the comparison exact rather than
approximately-the-same-shape, and it is why the region-blind question does not
have to be settled before this port can be verified.

⚠ **CI does not run this** — it needs a chromium CI does not install. Run it
locally when the browser detector changes.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pytest

from bugarach.detectors._shared import (discretize, distinct_coact,
                                        matlab_colon, matlab_prctile)
from bugarach.detectors.loco import RegionWindow, _detect_stream
from bugarach.simulate import simulate_coordination

ROOT = Path(__file__).resolve().parents[1]
VIEWER = ROOT / "docs" / "site" / "raster_viewer.html"

DURATION = 1200.0
# the operating point the bench ships for this detector
PARAMS = dict(binw=1.0, ctx=120.0, tstep=15.0, mgap=2.0, pctile=99.9,
              n_surrogates=300, min_rois=3)

JS = """(cfg) => {
  const opts = {binWidthSec: cfg.binw, contextWinSec: cfg.ctx,
                thrStepSec: cfg.tstep, mergeGapSec: cfg.mgap,
                thresholdPctile: cfg.pctile, nSurrogates: cfg.nsur,
                minRois: cfg.minRois, seed: 7};
  const own = locoDetect(cfg.trains, cfg.tRange, opts);
  // the same run, but handed Python's threshold instead of its own — the only
  // way two different random sources can be compared on their detections
  const given = locoDetect(cfg.trains, cfg.tRange,
                           {...opts, thresholds: cfg.pyThr});
  const pick = d => ({starts: d.starts, ends: d.ends, widths: d.widths,
                      magnitude: d.magnitude, magTotal: d.magTotal,
                      threshold: d.threshold, nEvents: d.nEvents});
  return {bc: Array.from(own.bc), sObs: Array.from(own.sObs),
          thrBin: Array.from(own.thrBin), own: pick(own), given: pick(given)};
}"""


@pytest.fixture(scope="module")
def trains():
    s, _ = simulate_coordination(duration_sec=DURATION, n_roi=40,
                                 bg_rate_hz=0.02, n_per_level=(5, 5, 5),
                                 min_sep_sec=60.0, seed=11)
    return [np.asarray(v, dtype=float) for v in s.streams["events"].locs]


@pytest.fixture(scope="module")
def py(trains):
    """Python's LoCo on the same window, called the way the browser calls it:
    one region spanning the whole window, so the clamp is a no-op on both sides."""
    ext = (0.0, DURATION)
    rw = [RegionWindow(label="window", slot="", raw_start=ext[0], raw_end=ext[1],
                       win_start=ext[0], win_end=ext[1], win_dur=DURATION,
                       meets_floor=True, is_baseline=True, is_hik=False,
                       too_short=False)]
    rng = np.random.RandomState(3)
    return _detect_stream(
        trains, rw, ext, rng, binw=PARAMS["binw"], mgap=PARAMS["mgap"],
        ctx=PARAMS["ctx"], pctile=PARAMS["pctile"], tstep=PARAMS["tstep"],
        min_rois=PARAMS["min_rois"], n_surrogates=PARAMS["n_surrogates"],
        null_context_mode="maxlt", clamp_context_to_region=True,
        detection_mode="threshold", peak_prominence=0.0,
        peak_min_distance_sec=0.0)


@pytest.fixture(scope="module")
def viewer_page():
    """One browser for the whole file. Two `sync_playwright` contexts cannot be
    open at once in a thread, and three fixtures here want a page."""
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
            yield page, errs
        finally:
            browser.close()


def _payload(trains, py_thr, n_sur):
    return {"trains": [list(map(float, v)) for v in trains],
            "tRange": [0.0, DURATION], "binw": PARAMS["binw"],
            "ctx": PARAMS["ctx"], "tstep": PARAMS["tstep"],
            "mgap": PARAMS["mgap"], "pctile": PARAMS["pctile"],
            "nsur": n_sur, "minRois": PARAMS["min_rois"],
            "pyThr": [float(x) for x in py_thr]}


@pytest.fixture(scope="module")
def js(viewer_page, trains, py):
    page, errs = viewer_page
    out = page.evaluate(JS, _payload(trains, py.signal.threshold,
                                     PARAMS["n_surrogates"]))
    assert not errs, errs
    return out


# ------------------------------------------------ the half that must be exact

def test_the_bin_grid_is_matlabs_colon(js):
    py_bc = matlab_colon(0.0, PARAMS["binw"], DURATION)[:-1] + PARAMS["binw"] / 2
    got = np.asarray(js["bc"], dtype=float)
    assert got.shape == py_bc.shape
    assert np.array_equal(got, py_bc), "the browser bin centres are not MATLAB's"


def test_the_observed_statistic_matches_exactly(js, trains):
    """Distinct ROIs per bin. No randomness reaches this, so any difference is a
    bug in the binning or in the distinct-ROI rule — the two places a coactivity
    statistic is usually got wrong."""
    from bugarach.detectors._shared import clip_sorted
    edges = matlab_colon(0.0, PARAMS["binw"], DURATION)
    py_s = distinct_coact(clip_sorted(trains, 0.0, DURATION), edges)
    got = np.asarray(js["sObs"], dtype=float)
    assert got.shape == py_s.shape
    assert np.array_equal(got, py_s), (
        f"observed coactivity differs in {int((got != py_s).sum())} of "
        f"{py_s.size} bins")


def test_the_statistic_is_not_trivially_flat(js):
    """A statistic that is zero everywhere would pass the comparison above and
    prove nothing about the binning."""
    s = np.asarray(js["sObs"], dtype=float)
    assert s.max() >= PARAMS["min_rois"] + 1, f"peak coactivity only {s.max()}"
    assert np.count_nonzero(s) >= 50, "almost every bin is empty"


@pytest.mark.parametrize("field", ["starts", "ends", "widths", "magnitude",
                                   "magTotal", "threshold"])
def test_given_the_same_threshold_the_events_match_to_1e9(js, py, field):
    """The detection half is deterministic once the bar is fixed, so it gets the
    same 1e-9 bar as the two detectors that draw no random numbers at all."""
    got = np.asarray(js["given"][field], dtype=float)
    ref = {"starts": py.onset_sec,
           "ends": py.onset_sec + py.width_sec,
           "widths": py.width_sec,
           "magnitude": py.magnitude,
           "magTotal": py.mag_total,
           "threshold": py.threshold}[field]
    assert js["given"]["nEvents"] == py.onset_sec.size, (
        f"given Python's own threshold the browser called "
        f"{js['given']['nEvents']} events, Python called {py.onset_sec.size}")
    assert got.shape == ref.shape
    if got.size:
        assert np.max(np.abs(got - ref)) < 1e-9, (
            f"{field}: worst |diff| {np.max(np.abs(got - ref)):.3e}")


def test_the_fixture_detects_enough_to_compare(py):
    assert py.onset_sec.size >= 5, (
        f"only {py.onset_sec.size} episodes — every comparison above is nearly "
        f"vacuous")


# ---------------- the tie-breaks, against answers derived by hand

VECTOR = """(v) => {
  const d = locoDetect(v.trains, v.tRange, v.opts);
  return {nEvents: d.nEvents, starts: d.starts, ends: d.ends,
          magnitude: d.magnitude, threshold: d.threshold,
          sObs: Array.from(d.sObs),
          thrFinite: Array.from(d.thrBin, x => Number.isFinite(x))};
}"""

BASE = dict(binWidthSec=1.0, mergeGapSec=2.0, contextWinSec=120.0,
            thrStepSec=15.0, thresholdPctile=99.9, nSurrogates=20, minRois=3)


@pytest.fixture(scope="module")
def vector_in_browser(viewer_page):
    page, _ = viewer_page
    return lambda trains, t_range, **o: page.evaluate(
        VECTOR, {"trains": trains, "tRange": list(t_range),
                 "opts": {**BASE, **o}})


def test_a_gap_of_exactly_the_merge_gap_still_merges(vector_in_browser):
    """`merge_gap` is inclusive: bins exactly that far apart are one episode, not
    two. Off by one in the comparison splits every marginal episode in half, and
    a simulated recording almost never places two firing bins at exactly the
    limit — so it is placed here on purpose.

    Three ROIs fire in bin 0 and again in bin 2, nothing in bin 1. With
    `merge_gap` 2 s and 1 s bins the gap IS 2, so the answer is one episode.

    Two more ROIs fire together in bin 5, and they must be ignored. Every
    threshold here is zero, so that pair clears the bar — the only thing keeping
    it out is `min_rois`, which is the floor FOUNDATIONS §9 forbids raising to
    make false alarms disappear and which therefore has to be shown working."""
    trains = [[0.5, 2.5], [0.5, 2.5], [0.5, 2.5], [5.5], [5.5]]
    out = vector_in_browser(trains, [0.0, 60.0], thresholds=[0.0] * 60)
    assert out["sObs"][:6] == [3, 0, 3, 0, 0, 2], out["sObs"][:6]
    assert out["nEvents"] == 1, (
        f"expected one episode — a gap of exactly merge_gap merges, and the "
        f"pair in bin 5 is under the ROI floor — got {out['nEvents']}")
    assert out["starts"][0] == pytest.approx(0.5)
    assert out["ends"][0] == pytest.approx(2.5), "the episode lost its second bin"


def test_tied_maxima_report_the_first_bin_not_the_last(vector_in_browser):
    """MATLAB's `max` returns the FIRST maximum, and the port follows it. Which
    tied bin wins is invisible in the magnitude — they are equal, that is what a
    tie means — and shows only in the threshold the episode is recorded against.
    So the three bins are given three different thresholds and the first one is
    the answer."""
    trains = [[0.5, 1.5, 2.5], [0.5, 1.5, 2.5], [0.5, 1.5, 2.5]]
    thr = [0.0, 0.5, 0.9] + [0.0] * 57
    out = vector_in_browser(trains, [0.0, 60.0], thresholds=thr)
    assert out["sObs"][:3] == [3, 3, 3], "the vector stopped being a tie"
    assert out["nEvents"] == 1
    assert out["magnitude"][0] == 3
    assert out["threshold"][0] == pytest.approx(0.0), (
        f"the episode was recorded against threshold {out['threshold'][0]}, "
        f"which is a later tied bin — MATLAB's max takes the first")


def test_a_bin_equidistant_between_anchors_takes_the_earlier_one(
        vector_in_browser):
    """`np.argmin` takes the first minimum, so a bin exactly between two anchors
    belongs to the earlier one. The consequence here is not subtle: the first
    anchor has no trailing context at all, so its bar is infinite and nothing
    beneath it can fire. Taking the later anchor instead would hand that bin a
    finite bar and let it through.

    With 1 s bins and anchors every 15 s, bin 7 is centred at 7.5 — exactly
    between anchor 0 and anchor 15. No sampling reaches this: the infinity comes
    from an empty half-context, not from a draw."""
    trains = [[7.2, 7.4, 7.6], [7.3], [7.5], [7.7], [20.0], [21.0], [22.0]]
    out = vector_in_browser(trains, [0.0, 120.0])
    fin = out["thrFinite"]
    assert fin[7] is False, (
        "bin 7 is equidistant between anchors 0 and 15 and must take the "
        "earlier one, whose bar is infinite for want of a trailing context")
    assert fin[8] is True, (
        "bin 8 is nearer anchor 15 and should have a finite bar — if this is "
        "False the vector is not testing the tie it claims to")


# ------------------------- the pieces that are exact, tested exactly

HELPERS = """(v) => ({
  prctile: v.pcts.map(p => matlabPrctile(v.pool, p)),
  coact: Array.from(distinctCoact(v.trains, v.edges)),
  bins: v.probe.map(x => discretizeIdx(x, v.edges)),
})"""


@pytest.fixture(scope="module")
def helpers_in_browser(viewer_page):
    page, _ = viewer_page
    return lambda **v: page.evaluate(HELPERS, v)


def test_the_percentile_is_matlabs_not_numpys(helpers_in_browser):
    """`matlab_prctile` matches NO numpy interpolation mode, and the threshold it
    produces is the detector's whole bar. Reaching it only through the sampled
    null would leave the rule untested — a numpy-style percentile lands within
    sampling error of the right answer and passes every comparison above. So it
    is checked here directly, at 1e-9, on a pool shaped like a real one:
    small integers, heavily tied, which is where the two conventions differ most.
    """
    pool = ([0.0] * 40 + [1.0] * 25 + [2.0] * 15 + [3.0] * 10
            + [4.0] * 6 + [5.0] * 3 + [7.0])
    pcts = [0.0, 1.0, 25.0, 50.0, 90.0, 99.0, 99.9, 100.0]
    got = helpers_in_browser(pool=pool, pcts=pcts, trains=[[]],
                             edges=[0.0, 1.0], probe=[])["prctile"]
    ref = [matlab_prctile(np.asarray(pool), q) for q in pcts]
    assert np.max(np.abs(np.asarray(got) - np.asarray(ref))) < 1e-9, (
        f"browser {got}\npython   {ref}")

    # and it must actually differ from the obvious wrong answer, or the test
    # above proves only that two identical formulas agree
    naive = [float(np.percentile(pool, q)) for q in pcts]
    assert any(abs(a - b) > 1e-9 for a, b in zip(ref, naive)), (
        "MATLAB and numpy percentiles agree on this pool — pick a harder one")


def test_the_binning_rule_closes_the_last_bin_and_drops_the_outside(
        helpers_in_browser):
    """MATLAB's `discretize`: bin i is [edge_i, edge_i+1), the LAST bin closes on
    the right, and anything outside belongs to no bin. The right-closure is
    invisible in ordinary data — it fires only for an event landing exactly on
    the final edge, which is a real recording's last frame and never a
    simulation's."""
    edges = [0.0, 1.0, 2.0, 3.0]
    probe = [-0.5, 0.0, 0.999, 1.0, 2.5, 3.0, 3.0000001]
    got = helpers_in_browser(pool=[0.0], pcts=[50.0], trains=[[]],
                             edges=edges, probe=probe)["bins"]
    ref = discretize(np.asarray(probe), np.asarray(edges))
    assert got == list(ref), f"browser {got}, python {list(ref)}"
    assert got[5] == 2, "an event on the final edge must join the last bin"
    assert got[0] == -1 and got[6] == -1, "outside the edges is no bin at all"


def test_distinct_counts_an_roi_once_per_bin_however_often_it_fires(
        helpers_in_browser):
    """The statistic's whole content: one busy ROI is not coordination. A vector
    where one ROI fires six times in a bin and five others fire once each must
    count 6, not 11."""
    edges = [0.0, 10.0, 20.0]
    trains = [[1.0, 2.0, 3.0, 4.0, 5.0, 6.0], [1.5], [2.5], [3.5], [4.5], [5.5],
              [12.0, 13.0]]
    got = helpers_in_browser(pool=[0.0], pcts=[50.0], trains=trains,
                             edges=edges, probe=[])["coact"]
    ref = distinct_coact([np.asarray(v) for v in trains], np.asarray(edges))
    assert got == list(ref)
    assert got[0] == 6, f"first bin should count 6 distinct ROIs, got {got[0]}"
    assert got[1] == 1, f"second bin should count 1, got {got[1]}"


# ------------------------------------------- the half that can only be close

def test_the_sampled_threshold_agrees_within_sampling_error(js, py):
    """Reported, not asserted tightly. Both sides shuffle a hundred times and
    take the 99.9th percentile of the pool; they cannot agree exactly and a test
    that demanded it would be testing the random number generators.

    What IS asserted is that they are in the same place — a port that shuffled
    over the wrong window, or pooled the wrong axis, lands somewhere else
    entirely rather than a fraction of an ROI away."""
    a = np.asarray(js["thrBin"], dtype=float)
    b = np.asarray(py.signal.threshold, dtype=float)
    assert a.shape == b.shape
    finite = np.isfinite(a) & np.isfinite(b)
    assert finite.sum() >= 0.9 * a.size, "too many infinite thresholds to compare"
    diff = np.abs(a[finite] - b[finite])
    exact = float(np.mean(diff == 0))
    print(f"\n  threshold: {exact:.0%} of bins identical, median |diff| "
          f"{np.median(diff):.3f} ROI, worst {diff.max():.3f}, "
          f"python median {np.median(b[finite]):.2f}")
    # The bar is integer-valued — a count of ROIs — so two correct samplers land
    # on the SAME integer for most bins rather than merely nearby. That is what
    # gives a sampled quantity a usable assertion: not "close", but "identical
    # most of the time, and never far". A port that pooled the wrong axis, took
    # the lower of the two half-contexts, or counted events instead of ROIs
    # moves the bar systematically and fails both halves.
    assert exact >= 0.70, (
        f"only {exact:.0%} of bins got the same threshold — correct samplers "
        f"agree exactly on most of them; this is a structural disagreement")
    assert diff.max() <= 3.0, f"worst threshold gap {diff.max()} ROIs"


def test_the_disagreement_shrinks_when_both_sides_sample_more(viewer_page, trains):
    """The test that tells sampling error apart from a bug, and the only one here
    that can.

    Any fixed bar on a sampled quantity is a guess: too tight and it flakes, too
    loose and it passes a port that pools the wrong axis. But sampling error has a
    property a structural error does not — **it shrinks when you sample more.**
    So both sides are run at 100 surrogates and again at 400, and the fraction of
    bins on which they agree *exactly* has to rise.

    A port whose null is genuinely wrong converges to a different answer, so its
    agreement stays flat or falls. Measured here: 73% at 100 surrogates, 81% at
    300, 87% at 600 — the signature of two correct estimators of one quantity.
    """
    ext = (0.0, DURATION)
    rw = [RegionWindow(label="window", slot="", raw_start=ext[0], raw_end=ext[1],
                       win_start=ext[0], win_end=ext[1], win_dur=DURATION,
                       meets_floor=True, is_baseline=True, is_hik=False,
                       too_short=False)]

    page, _ = viewer_page

    def agreement(n_sur):
        rng = np.random.RandomState(3)
        d = _detect_stream(
            trains, rw, ext, rng, binw=PARAMS["binw"], mgap=PARAMS["mgap"],
            ctx=PARAMS["ctx"], pctile=PARAMS["pctile"], tstep=PARAMS["tstep"],
            min_rois=PARAMS["min_rois"], n_surrogates=n_sur,
            null_context_mode="maxlt", clamp_context_to_region=True,
            detection_mode="threshold", peak_prominence=0.0,
            peak_min_distance_sec=0.0)
        out = page.evaluate(JS, _payload(trains, d.signal.threshold, n_sur))
        a = np.asarray(out["thrBin"], dtype=float)
        b = np.asarray(d.signal.threshold, dtype=float)
        f = np.isfinite(a) & np.isfinite(b)
        return float(np.mean(a[f] == b[f]))

    few, many = agreement(100), agreement(400)
    print(f"\n  exact agreement: {few:.0%} at 100 surrogates -> {many:.0%} at 400")
    assert many > few, (
        f"agreement did not improve with four times the sampling "
        f"({few:.0%} -> {many:.0%}). Sampling error shrinks; a wrong null does "
        f"not, so this is a disagreement about what is being estimated")


def test_the_two_thresholds_bracket_the_same_detections(js, py):
    """The end-to-end sanity check, and deliberately loose: run with its own
    sampled threshold, the browser should find about what Python finds. Tight
    comparison is the injected-threshold test above; this one only catches a
    port whose own null is wrong enough to change the answer."""
    own, ref = js["own"]["nEvents"], py.onset_sec.size
    assert abs(own - ref) <= max(2, 0.4 * ref), (
        f"browser found {own} episodes on its own null, Python found {ref} — "
        f"too far apart to be sampling error")
