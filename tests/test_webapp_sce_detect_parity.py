"""The browser's SCE against `bugarach.detectors.sce`.

Third of the sampling detectors, on the pattern the other two established:
coactivity exact, threshold sampled, episodes exact once the threshold is fixed.
SCE makes that last step easy — its threshold is one scalar for the whole window
rather than a rolling vector, so the injection is a single number.

Two things are specific to this detector.

**It bins coarsely** — ten seconds by default, against LoCo's one and
CoactDetect's two — and reports the bin's LEFT EDGE as the onset. That is the
convention that once read 0.00 recall against a scorer treating detections as
points; the width it reports is what makes it scoreable, so the width is compared
here rather than assumed.

**Its merge is on event times, not bins.** Two significant bins join when the
first observed event of the second is within `merge_gap` of the last observed
event of the first — at ten-second bins a very different question from "are the
bins adjacent". The default gap is NaN, which merges nothing because every
comparison against NaN is false, and that is ported rather than tidied.

⚠ **CI does not run this** — it needs a chromium CI does not install.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pytest

from bugarach.detectors.sce import _window_detect
from bugarach.simulate import simulate_coordination

ROOT = Path(__file__).resolve().parents[1]
VIEWER = ROOT / "docs" / "site" / "raster_viewer.html"

DURATION = 3600.0
# the operating point the bench ships (generate_sce contract)
OPTS = dict(bin_width_sec=10.0, threshold_pctile=99.0, n_surrogates=200,
            min_rois=3, merge_gap_sec=np.nan, detection_mode="threshold",
            peak_prominence=0.0, peak_min_distance_sec=0.0)

JS = """(cfg) => {
  const opts = {binWidthSec: cfg.bw, thresholdPctile: cfg.pctile,
                nSurrogates: cfg.nsur, minRois: cfg.minRois,
                mergeGapSec: cfg.mgap === null ? undefined : cfg.mgap, seed: 4};
  const own = sceDetect(cfg.trains, cfg.tRange, opts);
  const given = sceDetect(cfg.trains, cfg.tRange, {...opts, threshold: cfg.pyThr});
  const pick = d => ({starts: d.starts, ends: d.ends, widths: d.widths,
                      magnitude: d.magnitude, magTotal: d.magTotal,
                      nEvents: d.nEvents});
  return {obs: Array.from(own.obs), bctr: Array.from(own.bctr),
          threshold: own.threshold, own: pick(own), given: pick(given)};
}"""


@pytest.fixture(scope="module")
def trains():
    s, _ = simulate_coordination(duration_sec=DURATION, n_roi=30,
                                 bg_rate_hz=0.015, n_per_level=(5, 5, 5),
                                 min_sep_sec=120.0, seed=17)
    return [np.asarray(v, dtype=float) for v in s.streams["events"].locs]


@pytest.fixture(scope="module")
def py(trains):
    """Python's SCE on one window, which is how the browser calls it."""
    rel = [v - 0.0 for v in trains]
    rng = np.random.RandomState(21)
    return _window_detect(rel, 0.0, DURATION, 0.0, DURATION, rng, OPTS)


@pytest.fixture(scope="module")
def viewer_page():
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


@pytest.fixture(scope="module")
def js(viewer_page, trains, py):
    page, errs = viewer_page
    out = page.evaluate(JS, {
        "trains": [list(map(float, v)) for v in trains],
        "tRange": [0.0, DURATION], "bw": OPTS["bin_width_sec"],
        "pctile": OPTS["threshold_pctile"], "nsur": OPTS["n_surrogates"],
        "minRois": OPTS["min_rois"], "mgap": None,   # NaN does not cross JSON
        "pyThr": float(py["thr"])})
    assert not errs, errs
    return out


def test_the_coactivity_and_its_grid_are_exact(js, py):
    got = np.asarray(js["obs"], dtype=float)
    ref = np.asarray(py["obs"], dtype=float)
    assert got.shape == ref.shape
    assert np.array_equal(got, ref), (
        f"coactivity differs in {int((got != ref).sum())} of {ref.size} bins")
    assert np.array_equal(np.asarray(js["bctr"], dtype=float),
                          np.asarray(py["bctr"], dtype=float))
    assert got.max() >= OPTS["min_rois"] + 2, f"peak only {got.max()}"


@pytest.mark.parametrize("field", ["starts", "widths", "magnitude", "magTotal"])
def test_given_the_same_threshold_the_episodes_match_to_1e9(js, py, field):
    got = np.asarray(js["given"][field], dtype=float)
    ref = {"starts": py["onset"], "widths": py["width"],
           "magnitude": py["mag"], "magTotal": py["mag_t"]}[field]
    ref = np.asarray(ref, dtype=float)
    assert js["given"]["nEvents"] == ref.size, (
        f"given Python's own threshold the browser called "
        f"{js['given']['nEvents']} episodes, Python called {ref.size}")
    assert got.shape == ref.shape
    if got.size:
        both_nan = np.isnan(got) & np.isnan(ref)
        d = np.where(both_nan, 0.0, np.abs(got - ref))
        assert np.nanmax(d) < 1e-9, f"{field}: worst |diff| {np.nanmax(d):.3e}"


def test_the_onset_is_the_bins_left_edge_not_the_first_event(js, py):
    """SCE reports where the BIN started, which can be seconds before anything
    fired. It is the convention that once scored 0.00 recall against a
    point-matching scorer, and it is preserved rather than improved."""
    starts = np.asarray(js["given"]["starts"], dtype=float)
    assert starts.size, "no episodes to check"
    bw = OPTS["bin_width_sec"]
    assert np.allclose(starts % bw, 0.0), (
        "an onset does not sit on a bin edge — the port has started reporting "
        "first-event times instead")


def test_the_fixture_detects_enough_to_compare(py):
    assert np.asarray(py["onset"]).size >= 4, (
        f"only {np.asarray(py['onset']).size} episodes — comparisons are weak")


def test_the_sampled_threshold_lands_in_the_same_place(js, py):
    """One scalar per window, from a percentile of the shuffled pool. Different
    random sources, so not equal — but the statistic is a count of ROIs, so two
    correct estimators land on the same integer or one apart."""
    a, b = float(js["threshold"]), float(py["thr"])
    print(f"\n  threshold: browser {a:.3f}, python {b:.3f}")
    assert abs(a - b) <= 1.0, (
        f"threshold {a:.2f} vs {b:.2f} — that is a different null, not "
        f"sampling error")


def test_on_its_own_null_it_finds_about_what_python_finds(js, py):
    own, ref = js["own"]["nEvents"], np.asarray(py["onset"]).size
    assert abs(own - ref) <= max(2, 0.4 * ref), (
        f"browser found {own} episodes on its own null, Python found {ref}")


# ------------------------------- merging, against an answer derived by hand

VEC_JS = """(v) => {
  const d = sceDetect(v.trains, v.tRange, v.opts);
  return {nEvents: d.nEvents, starts: d.starts, widths: d.widths,
          magnitude: d.magnitude, magTotal: d.magTotal,
          obs: Array.from(d.obs)};
}"""


def test_a_merged_episode_reports_its_biggest_bin_and_only_qualifying_bins(
        viewer_page):
    """Two things the default settings cannot test, because the default merge gap
    is NaN and therefore merges nothing — every episode is one bin, so "biggest
    bin" and "last bin" are the same bin and the ROI floor never has to exclude
    anything that cleared the threshold.

    With a finite gap they separate. Seven ROIs fire in bin 0 and four of them
    again in bin 1, ten seconds later, which is inside a thirty-second gap — one
    episode, recruiting seven, whose magnitude is the SEVEN of its first bin and
    not the four of its last. Two further ROIs fire in bin 2; they clear a
    threshold of zero and are held out by the ROI floor alone, so if the floor
    stops working the episode grows to nine ROIs and twice the width."""
    page, _ = viewer_page
    trains = [[5.0, 15.0], [5.0, 15.0], [5.0, 15.0], [5.0, 15.0],
              [5.0], [5.0], [5.0],
              [25.0], [25.0]]
    out = page.evaluate(VEC_JS, {
        "trains": trains, "tRange": [0.0, 600.0],
        "opts": {"binWidthSec": 10.0, "minRois": 3, "mergeGapSec": 30.0,
                 "threshold": 0.0, "nSurrogates": 10}})
    assert out["obs"][:3] == [7, 4, 2], out["obs"][:3]
    assert out["nEvents"] == 1, f"expected one episode, got {out['nEvents']}"
    assert out["magnitude"][0] == 7, (
        f"episode magnitude {out['magnitude'][0]} — it is the biggest bin (7), "
        f"not the last (4)")
    assert out["magTotal"][0] == 7, (
        f"recruitment {out['magTotal'][0]} — the pair in bin 2 is under the ROI "
        f"floor and must not join the episode")
    assert out["widths"][0] == pytest.approx(10.0), (
        f"width {out['widths'][0]} — first to last event of the qualifying "
        f"bins is 5 s to 15 s; 20 s means bin 2 was swept in")
    assert out["starts"][0] == pytest.approx(0.0), "onset is bin 0's left edge"


def test_an_event_on_the_final_instant_joins_the_last_bin(viewer_page):
    """SCE clips its bin index into range rather than dropping what falls past
    the end, so an event at exactly the window's last instant belongs to the
    final bin. Each detector carries its own copy of this rule and each one is
    checked, because they do not all share it — LoCo uses `discretize`, which
    closes the last bin explicitly, and this one clips."""
    page, _ = viewer_page
    out = page.evaluate(VEC_JS, {
        "trains": [[600.0], [600.0], [600.0]], "tRange": [0.0, 600.0],
        "opts": {"binWidthSec": 10.0, "minRois": 3, "threshold": 0.0,
                 "nSurrogates": 10}})
    assert len(out["obs"]) == 60
    assert out["obs"][-1] == 3, (
        f"three events on the final instant should land in the last bin; it "
        f"holds {out['obs'][-1]}")
