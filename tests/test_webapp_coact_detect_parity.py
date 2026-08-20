"""The browser's CoactDetect against `bugarach.detectors.coact`.

The second sampling detector, tested on the pattern LoCo established: the
coactivity is exact, the null is sampled, and the episodes are exact once
significance is fixed — so p-values are injected into both implementations and
the events compared at 1e-9.

Two things are specific to this detector and get their own checks.

**`erfc` is the whole decision.** CoactDetect turns each bin into a z-score and
keeps it if `0.5*erfc(z/√2)` clears alpha. The browser has no `erfc`, so one is
carried, and it is compared to Python's `math.erfc` directly rather than through
the detector — an erfc that is merely close lands the same verdict on almost every
bin and differs exactly where alpha is, which is the only place it matters.

**Its grid is NOT the two-ended MATLAB colon.** CoactDetect builds `t0 + k*bw` and
bins by `clip(floor((t-t0)/bw), 0, nb-1)`, so the last bin swallows the endpoint.
LoCo and SPIKE-synch use the colon and `discretize`. Both are ported as they are,
because matching each original is the product, and a test asserts the difference so
nobody unifies them for tidiness.

⚠ **CI does not run this** — it needs a chromium CI does not install.
"""

from __future__ import annotations

import math
from pathlib import Path

import numpy as np
import pytest

from bugarach.detectors.coact import coact_detect
from bugarach.simulate import simulate_coordination

ROOT = Path(__file__).resolve().parents[1]
VIEWER = ROOT / "docs" / "site" / "raster_viewer.html"

DURATION = 900.0
# the operating point the bench ships — explore_sce's FAST viewer point
PARAMS = dict(int_win_sec=2.0, context_win_sec=60.0, alpha=1e-4,
              n_surrogates=100, min_rois=3, merge_gap_sec=3.0)

JS = """(cfg) => {
  const opts = {intWinSec: cfg.bw, contextWinSec: cfg.ctx, alpha: cfg.alpha,
                nSurrogates: cfg.nsur, minRois: cfg.minRois,
                mergeGapSec: cfg.mgap, seed: 5};
  const own = coactDetect(cfg.trains, cfg.tRange, opts);
  const given = coactDetect(cfg.trains, cfg.tRange, {...opts, pvals: cfg.pyP});
  const pick = d => ({starts: d.starts, ends: d.ends, widths: d.widths,
                      nrois: d.nrois, nEvents: d.nEvents});
  return {obs: Array.from(own.obs), ctr: Array.from(own.ctr),
          own: pick(own), given: pick(given),
          ownP: Array.from(own.pvalProf),
          nullmean: Array.from(own.nullmean)};
}"""

ERFC_JS = "(v) => v.map(x => erfc(x))"


@pytest.fixture(scope="module")
def trains():
    s, _ = simulate_coordination(duration_sec=DURATION, n_roi=35,
                                 bg_rate_hz=0.02, n_per_level=(4, 4, 4),
                                 min_sep_sec=60.0, seed=13)
    return [np.asarray(v, dtype=float) for v in s.streams["events"].locs]


@pytest.fixture(scope="module")
def py(trains):
    return coact_detect(trains, (0.0, DURATION), rng_seed=9, **PARAMS)


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
        "tRange": [0.0, DURATION], "bw": PARAMS["int_win_sec"],
        "ctx": PARAMS["context_win_sec"], "alpha": PARAMS["alpha"],
        "nsur": PARAMS["n_surrogates"], "minRois": PARAMS["min_rois"],
        "mgap": PARAMS["merge_gap_sec"],
        # NaN does not survive JSON; the browser reads a missing p as
        # not-significant exactly as Python reads NaN, so they agree
        "pyP": [None if np.isnan(x) else float(x) for x in py.pval_prof]})
    assert not errs, errs
    return out


# --------------------------------------------------- the deterministic pieces

def test_erfc_matches_pythons_to_1e12_across_the_range_that_decides(viewer_page):
    """The p-value is `0.5*erfc(z/√2)` and it is compared to alpha, so the tail is
    where accuracy has to hold — an erfc good to 1e-7 agrees on every ordinary bin
    and disagrees exactly at the threshold, which is the only place the answer
    changes."""
    page, _ = viewer_page
    xs = [-6.0, -3.0, -1.0, -0.25, 0.0, 0.25, 1.0, 2.0, 3.0, 4.0,
          5.0, 6.0, 8.0, 10.0, 0.7071067811865476, 2.5758293035489004]
    got = page.evaluate(ERFC_JS, xs)
    for x, g in zip(xs, got):
        ref = math.erfc(x)
        assert abs(g - ref) <= 1e-12 * max(1.0, abs(ref)), (
            f"erfc({x}): browser {g!r}, python {ref!r}")
    # and the tail must not have collapsed to zero, which would pass an
    # absolute-difference check while destroying every significance decision
    assert got[xs.index(6.0)] > 0, "erfc underflowed in the tail"


def test_the_coactivity_is_exact_and_not_flat(js, trains):
    """Distinct ROIs per bin, on this detector's own forward grid. No randomness
    touches it."""
    ref = coact_detect(trains, (0.0, DURATION), rng_seed=9, **PARAMS).obs
    got = np.asarray(js["obs"], dtype=float)
    assert got.shape == ref.shape
    assert np.array_equal(got, ref), (
        f"coactivity differs in {int((got != ref).sum())} of {ref.size} bins")
    assert got.max() >= PARAMS["min_rois"] + 2, f"peak only {got.max()}"


def test_its_grid_is_the_forward_one_not_matlabs_colon(js):
    """CoactDetect and LoCo disagree about how to build a bin grid, and the
    difference is in the originals rather than in the ports. Asserted so nobody
    unifies them for tidiness — that would silently move every bin edge in one
    of the two detectors."""
    from bugarach.detectors._shared import matlab_colon
    bw = PARAMS["int_win_sec"]
    nb = max(1, int(np.ceil(DURATION / bw)))
    forward = 0.0 + (np.arange(1, nb + 1) - 0.5) * bw
    got = np.asarray(js["ctr"], dtype=float)
    assert np.array_equal(got, forward), "the browser left this detector's grid"
    colon = matlab_colon(0.0, bw, DURATION)
    assert got.size != colon.size or not np.array_equal(got, colon[:got.size]), (
        "this detector's grid has become the colon grid — the two originals "
        "differ and the ports must keep differing")


STATS_JS = "(v) => coactStats(v.obs, v.counts)"
NULL_JS = """(v) => {
  const d = coactDetect(v.trains, v.tRange, v.opts);
  return {obs: Array.from(d.obs), nullmean: Array.from(d.nullmean)};
}"""

VEC_JS = """(v) => {
  const d = coactDetect(v.trains, v.tRange, {...v.opts, pvals: v.pvals});
  return {nEvents: d.nEvents, starts: d.starts, ends: d.ends,
          widths: d.widths, nrois: d.nrois, obs: Array.from(d.obs)};
}"""

VEC_OPTS = dict(intWinSec=1.0, contextWinSec=60.0, alpha=0.01, nSurrogates=20,
                minRois=3, mergeGapSec=3.0)


def test_the_z_and_p_arithmetic_matches_python_exactly(viewer_page):
    """Everything here is deterministic once the shuffles are counted, and it is
    the arithmetic most easily got slightly wrong: the spread is the SAMPLE
    standard deviation, and using the population one shifts every z by 0.5% at a
    hundred surrogates — far less than sampling error, so no comparison that goes
    through the shuffles can see it. This one does not go through them."""
    page, _ = viewer_page
    # Cases where p is of ORDER ONE matter as much as tail cases: a p that is
    # two-tailed instead of one is exactly twice the right answer, and at
    # p = 1e-16 that is invisible under any absolute tolerance. It is not
    # invisible at p = 0.02.
    cases = [
        (5.0, [3, 4, 5, 4, 3, 6, 4, 5, 3, 4]),        # p of order 0.1
        (6.0, [3, 4, 5, 4, 3, 6, 4, 5, 3, 4]),        # p of order 0.02
        (4.0, [3, 4, 5, 4, 3, 6, 4, 5, 3, 4]),        # p near a half
        (12.0, [3, 4, 5, 4, 3, 6, 4, 5, 3, 4]),       # deep tail
        (3.0, [3, 3, 3, 3, 3]),                       # no spread, obs == mu
        (9.0, [3, 3, 3, 3, 3]),                       # no spread, obs above
        (1.0, [3, 3, 3, 3, 3]),                       # no spread, obs below
    ]
    for obs, counts in cases:
        got = page.evaluate(STATS_JS, {"obs": obs, "counts": counts})
        c = np.asarray(counts, dtype=float)
        mu, sd = c.mean(), c.std(ddof=1)
        if sd > 0:
            z = (obs - mu) / sd
            pv = 0.5 * math.erfc(z / math.sqrt(2))
        elif obs > mu:
            z, pv = math.inf, 0.0
        else:
            z, pv = 0.0, 1.0
        assert got["mu"] == pytest.approx(mu, abs=1e-12), (obs, counts)
        if math.isinf(z):
            assert got["z"] is None or math.isinf(got["z"]), (obs, counts)
        else:
            assert got["z"] == pytest.approx(z, rel=1e-12), (obs, counts)
        # RELATIVE, so a factor-of-two error is caught wherever p sits. An
        # absolute tolerance passes anything once p is in the tail.
        assert got["p"] == pytest.approx(pv, rel=1e-10, abs=0.0), (
            f"obs={obs} counts={counts}: browser {got['p']!r}, python {pv!r}")
    orders = sorted(0.5 * math.erfc(((o - np.mean(c)) / np.std(c, ddof=1))
                                    / math.sqrt(2))
                    for o, c in cases if np.std(c, ddof=1) > 0)
    assert orders[-1] > 0.01, (
        "every case has a tail p — add one of order 1 or a doubled p goes "
        "unnoticed")


def test_the_context_at_the_recording_start_is_clipped_to_it(viewer_page):
    """The null is built by shifting events around inside the context window, so
    the window's WIDTH sets how often a shifted event lands in the target bin —
    and a bin near the start has a context clipped to the recording rather than a
    full one hanging off the front.

    Here the answer is arithmetic rather than a comparison. Five ROIs each fire
    once, in bin 0. Its context runs 0 to 31 s, so each ROI's single event lands
    back in that 2 s bin with probability 2/31, and the null mean is 5x that =
    0.32. Unclipped the window would be 60 s wide and the answer would be 0.17 —
    half, and in the direction that makes everything look significant.

    The fixture comparison cannot see this: every candidate bin in it sits more
    than half a context from either end, where clipping does nothing."""
    page, _ = viewer_page
    trains = [[1.0]] * 5
    opts = {**VEC_OPTS, "intWinSec": 2.0, "contextWinSec": 60.0,
            "nSurrogates": 3000}
    out = page.evaluate(NULL_JS, {"trains": trains, "tRange": [0.0, 900.0],
                                  "opts": opts})
    assert out["obs"][0] == 5, out["obs"][:3]
    clipped = 5 * 2.0 / 31.0            # context [0, 31]
    unclipped = 5 * 2.0 / 60.0          # what a full window would give
    got = out["nullmean"][0]
    assert got == pytest.approx(clipped, rel=0.12), (
        f"null mean {got:.3f} — clipped context predicts {clipped:.3f}, an "
        f"unclipped one {unclipped:.3f}")
    assert abs(got - clipped) < abs(got - unclipped), (
        "the null is nearer the unclipped prediction than the clipped one")


def test_a_merged_episode_measures_its_gap_from_the_previous_bins_end(
        viewer_page):
    """Two significant bins with one quiet bin between them. With 1 s bins and a
    3 s merge gap the distance from the END of the first to the START of the
    second is 1 s, so they are one episode. Measuring from the first bin's START
    instead gives 2 s, which also merges — so the vector puts the second bin far
    enough out that only the correct rule merges it: bins 0 and 4, which is 3 s
    end-to-start and 4 s start-to-start."""
    page, _ = viewer_page
    trains = [[0.5, 4.5], [0.5, 4.5], [0.5, 4.5]]
    pv = [None] * 60
    pv[0] = 0.0
    pv[4] = 0.0
    out = page.evaluate(VEC_JS, {"trains": trains, "tRange": [0.0, 60.0],
                                 "opts": VEC_OPTS, "pvals": pv})
    assert out["obs"][0] == 3 and out["obs"][4] == 3, out["obs"][:6]
    assert out["nEvents"] == 1, (
        f"bins 3 s apart end-to-start must merge under a 3 s gap; got "
        f"{out['nEvents']} episodes")
    assert out["ends"][0] == pytest.approx(5.0), "the episode lost its second bin"


def test_a_p_exactly_at_alpha_is_significant(viewer_page):
    """`p <= alpha`, not `<`. A bin landing exactly on the threshold is in."""
    page, _ = viewer_page
    trains = [[0.5], [0.5], [0.5]]
    pv = [None] * 60
    pv[0] = VEC_OPTS["alpha"]
    out = page.evaluate(VEC_JS, {"trains": trains, "tRange": [0.0, 60.0],
                                 "opts": VEC_OPTS, "pvals": pv})
    assert out["nEvents"] == 1, "a p exactly at alpha was rejected"


def test_an_episode_reports_its_biggest_bin_not_its_last(viewer_page):
    """Recruitment for a merged episode is the maximum across it. Reporting the
    last bin instead understates every episode that peaks early, which is most
    of them."""
    page, _ = viewer_page
    trains = ([[0.5, 1.5]] * 3) + ([[0.5]] * 4)
    pv = [None] * 60
    pv[0] = 0.0
    pv[1] = 0.0
    out = page.evaluate(VEC_JS, {"trains": trains, "tRange": [0.0, 60.0],
                                 "opts": VEC_OPTS, "pvals": pv})
    assert out["obs"][0] == 7 and out["obs"][1] == 3, out["obs"][:3]
    assert out["nEvents"] == 1
    assert out["nrois"][0] == 7, (
        f"episode recruitment {out['nrois'][0]} — it should be the biggest bin "
        f"(7), not the last (3)")


def test_an_event_on_the_final_edge_joins_the_last_bin(viewer_page):
    """This detector clips its bin index into range rather than dropping the
    outside, so an event at exactly the recording end belongs to the last bin.
    That is a real recording's final frame and never a simulation's."""
    page, _ = viewer_page
    trains = [[60.0], [60.0], [60.0]]
    out = page.evaluate(VEC_JS, {"trains": trains, "tRange": [0.0, 60.0],
                                 "opts": VEC_OPTS, "pvals": [None] * 60})
    assert out["obs"][-1] == 3, (
        f"three events at the recording end should land in the last bin; "
        f"the last bin holds {out['obs'][-1]}")


@pytest.mark.parametrize("field", ["starts", "ends", "widths", "nrois"])
def test_given_the_same_p_values_the_episodes_match_to_1e9(js, py, field):
    """Merging and episode aggregation are deterministic once significance is
    fixed, so they get the same bar as a detector that draws no random numbers."""
    got = np.asarray(js["given"][field], dtype=float)
    ref = {"starts": py.onset_sec,
           "ends": py.onset_sec + py.width_sec,
           "widths": py.width_sec,
           "nrois": py.nrois}[field]
    assert js["given"]["nEvents"] == py.onset_sec.size, (
        f"given Python's own p-values the browser called "
        f"{js['given']['nEvents']} episodes, Python called {py.onset_sec.size}")
    assert got.shape == ref.shape
    if got.size:
        assert np.max(np.abs(got - ref)) < 1e-9, (
            f"{field}: worst |diff| {np.max(np.abs(got - ref)):.3e}")


def test_the_fixture_detects_enough_to_compare(py):
    assert py.onset_sec.size >= 4, (
        f"only {py.onset_sec.size} episodes — the comparisons are near-vacuous")


# ----------------------------------------------------- the sampled piece

def test_the_sampled_significance_agrees_on_almost_every_bin(js, py):
    """Both sides estimate the null by shuffling and their random sources differ,
    so the p-values cannot match. What must match is the VERDICT: whether each
    bin cleared alpha. A z-score is a smooth function of the null, so sampling
    error moves a bin across the line only when it was sitting on it."""
    a = np.asarray(js["ownP"], dtype=float)
    b = np.asarray(py.pval_prof, dtype=float)
    assert a.shape == b.shape
    sa = np.nan_to_num(a, nan=1.0) <= PARAMS["alpha"]
    sb = np.nan_to_num(b, nan=1.0) <= PARAMS["alpha"]
    agree = float(np.mean(sa == sb))
    print(f"\n  significance: {agree:.1%} of bins get the same verdict "
          f"({int(sa.sum())} vs {int(sb.sum())} significant)")
    assert agree >= 0.98, (
        f"only {agree:.1%} of bins agree on significance — that is a "
        f"disagreement about the null, not sampling noise")


def test_the_null_mean_agrees_where_the_context_is_clipped(js, py):
    """The context window is clipped to the recording, so a bin near either end
    gets a narrower one — and the null is built by shifting within it, so the
    width is part of the answer. Unclipped, an edge bin's shuffles spread over
    twice the span and the null comes out roughly half as large.

    A mean converges far faster than a percentile, so this is comparable across
    two random sources even though the individual draws are not."""
    a = np.asarray(js["nullmean"], dtype=float)
    b = np.asarray(py.nullmean_prof, dtype=float)
    both = np.isfinite(a) & np.isfinite(b) & (b > 0)
    assert both.sum() >= 5, "too few candidate bins to compare the null"
    rel = np.abs(a[both] - b[both]) / b[both]
    print(f"\n  null mean: median relative difference {np.median(rel):.1%}, "
          f"worst {rel.max():.1%} over {int(both.sum())} bins")
    assert np.median(rel) <= 0.15, (
        f"null means differ by {np.median(rel):.0%} in the median — that is a "
        f"different null, not sampling error")
    # the earliest candidate bin is where clipping bites hardest
    first = int(np.flatnonzero(both)[0])
    assert abs(a[first] - b[first]) / b[first] <= 0.35, (
        f"the first candidate bin's null differs by "
        f"{abs(a[first] - b[first]) / b[first]:.0%} — that is where the context "
        f"is clipped, and where an unclipped one shows first")


def test_on_its_own_null_it_finds_about_what_python_finds(js, py):
    own, ref = js["own"]["nEvents"], py.onset_sec.size
    assert abs(own - ref) <= max(2, 0.4 * ref), (
        f"browser found {own} episodes on its own null, Python found {ref}")
