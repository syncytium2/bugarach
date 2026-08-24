"""The browser's tuning step against `bugarach.score` and `bugarach.bench`.

Tuning is the step that makes the four a loop: measure a recording, simulate
from what you measured, detect, and then ask whether those settings were any
good. The last question only has an answer on a simulated folder, because only
there does anything know which moments were coordinated — which is why the page
keeps the events it plants and offers the sweep on nothing else.

Three things have to be true for a number on that screen to mean anything, and
each gets its own test here:

* **the truth the page kept is the truth it planted** — a sweep scored against a
  drifting answer key would look fine and be worthless;
* **the scorer matches the Python exactly** — it draws no random numbers, so 1e-9
  is the bar, the same one the two browser detectors hold;
* **the sweep the button runs is the sweep the table shows**, and the rule for
  choosing a setting off it is `bench.pick_operating_point`, refusal included: an
  optimum at the end of the grid is not an optimum.

The browser's generator is deliberately NOT the Python one — same model, a
different random source — so nothing here compares generated data. The trains and
the planted times are read back out of the page and handed to Python, which then
has to agree about what they mean.

⚠ **CI does not run this** — it needs a chromium CI does not install. Run it
locally when the browser tuning step changes.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pytest

from bugarach.bench import (BenchResult, DegenerateSweep, EdgeOfRange,
                            OPERATING_POINTS,
                            pick_operating_point)
from bugarach.detectors.rate import rate_detect
from bugarach.detectors.sync import sync_detect
from bugarach.score import score_detections
from bugarach.simulate import GroundTruth, PlantedEvent

ROOT = Path(__file__).resolve().parents[1]
VIEWER = ROOT / "docs" / "site" / "raster_viewer.html"

TOL = 1.5
# the simulator controls the page is driven with — one recording, enough minutes
# and events that a sweep has something to separate
SIM = {"sRec": "1", "sMin": "45", "sRoi": "33", "sRate": "10", "sEv": "15",
       "sJit": "360", "sSeed": "4"}

EXTRACT = """async (sim) => {
  for (const [id, v] of Object.entries(sim)) document.getElementById(id).value = v;
  await runSim();
  const rec = RECORDINGS[0];
  const data = await loadRecording(rec);
  const stream = [...data.streams.keys()].sort()[0];
  const byRoi = data.streams.get(stream);
  const trains = data.order.map(id => (byRoi.get(id) || []).slice());
  const truth = TRUTH.get(rec.id);
  const range = [data.t0, Math.max(data.t1, data.t0 + 1)];
  const dt = 0.1;
  const out = {id: rec.id, trains, range, dt,
               truth: {times: truth.times.slice(), fracs: truth.fracs.slice()},
               sweeps: {}};
  for (const which of ["rate", "sync"]) {
    document.getElementById("dDet").value = which;
    paintDetectorChoice();
    const base = DETECTORS[which].read(dt);
    const knob = DETECTORS[which].knob;
    out.sweeps[which] = {
      knob: knob.key, base,
      rows: knob.grid.map(v => {
        const r = sweepPoint(trains, range, which, base, knob, v, truth, %TOL%);
        return {knob: r.knob, nPlanted: r.nPlanted, nDetected: r.nDetected,
                nHit: r.nHit, nMiss: r.nMiss, nFa: r.nFa, nDup: r.nDup,
                precision: r.precision, recall: r.recall, f1: r.f1,
                byFrac: [...r.byFrac.entries()]};
      })};
  }
  return out;
}""".replace("%TOL%", str(TOL))


@pytest.fixture(scope="module")
def viewer():
    """One browser, one page, for every check in this file. Two `sync_playwright`
    contexts cannot be open at once in a thread, and each of these fixtures used
    to open its own."""
    pytest.importorskip("playwright.sync_api",
                        reason="the browser tuning step needs playwright")
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
def page_out(viewer):
    page, errs = viewer
    out = page.evaluate(EXTRACT, SIM)
    assert not errs, errs
    return out


@pytest.fixture(scope="module")
def trains(page_out):
    return [np.asarray(v, dtype=float) for v in page_out["trains"]]


@pytest.fixture(scope="module")
def gt(page_out):
    """The page's planted events, rebuilt as the ground truth Python scores
    against. Only `time` and `frac` are read by the scorer, and only those two
    cross the boundary — the participant lists stay in the browser."""
    t = page_out["truth"]
    return GroundTruth(events=[
        PlantedEvent(time=float(x), frac=float(f), n_part=0, rois=(),
                     jitter_sec=0.0)
        for x, f in zip(t["times"], t["fracs"])])


def _py_detect(which, trains, rng, base, knob_key, value):
    """The Python detector, given the browser's own settings for that run."""
    params = {**base, knob_key: value}
    if which == "rate":
        return rate_detect(trains, rng,
                           excess_threshold_hz=params["excessThresholdHz"],
                           rate_win=params["rateWin"],
                           context_win=params["contextWin"],
                           grid_dt=params["gridDt"])
    # `profileBinSec`, not `gridDt`. SPIKE-synch's bin is the resolution of the
    # DETECTOR rather than the acquisition interval — `sync.PROFILE_BIN_SEC` has
    # the argument — and the page stopped calling it a grid when it stopped
    # feeding it the recording's frame interval. The two names met the same 0.1
    # on this lab's folders, which is why the divergence survived so long.
    return sync_detect(trains, rng, tau_max=params["tauMax"],
                       max_gap=params["maxGap"],
                       C_threshold=params["CThreshold"],
                       C_min=params["CMin"], dt=params["profileBinSec"])


# ------------------------------------------------ the answer key itself

def test_the_page_kept_the_events_it_actually_planted(page_out, trains):
    """A sweep scored against a drifting answer key looks exactly like a sweep
    scored against a good one. So the truth is checked against the data it is
    supposed to describe: every planted time should have a crowd of onsets
    around it, far more than the background puts anywhere else."""
    times = np.asarray(page_out["truth"]["times"], dtype=float)
    fracs = np.asarray(page_out["truth"]["fracs"], dtype=float)
    assert times.size == int(SIM["sEv"]), (
        f"asked for {SIM['sEv']} events, kept {times.size}")
    assert times.size == fracs.size
    assert np.all(np.diff(np.sort(times)) > 0), "two events planted at one time"

    n_roi = len(trains)
    pooled = np.sort(np.concatenate([v for v in trains if v.size]))
    # participants are jittered around the planted time; 3 SD of the 360 ms
    # jitter this simulation uses catches essentially all of them
    win = 3 * float(SIM["sJit"]) / 1000.0
    for x, f in zip(times, fracs):
        near = np.sum((pooled >= x - win) & (pooled <= x + win))
        expect = max(1, round(f * n_roi))
        assert near >= 0.6 * expect, (
            f"planted event at {x:.1f}s claims {expect} participants but only "
            f"{near} onsets sit within {win:.1f}s of it — the kept truth does "
            f"not describe the data that was written")


def test_a_folder_read_from_disk_carries_no_truth_to_tune_against(viewer):
    """The page must not offer to tune somebody's real recordings against the
    last simulation's planted events. Opening any folder clears the truth, and
    the button goes with it."""
    page, _ = viewer
    state = page.evaluate("""async () => {
      await runSim();
      const before = {n: TRUTH.size,
                      enabled: !document.getElementById("runTune").disabled};
      // the same path a chosen folder takes, with one hand-made recording
      const csv = "roi,time_sec\\n1,1.0\\n1,2.0\\n2,1.1\\n";
      await open([new File([csv], "mine.csv", {type: "text/csv"})]);
      return {before, after: {n: TRUTH.size,
              enabled: !document.getElementById("runTune").disabled,
              chip: document.getElementById("cntTune").textContent}};
    }""")
    assert state["before"]["n"] > 0 and state["before"]["enabled"], (
        "the simulated folder did not arm the tuning step, so the check below "
        "would pass for the wrong reason")
    assert state["after"]["n"] == 0, "planted truth survived a real open"
    assert not state["after"]["enabled"], "tuning offered with no truth"
    assert "simulated" in state["after"]["chip"]


# ------------------------------------------------------- the scorer

@pytest.mark.parametrize("which", ["rate", "sync"])
def test_every_point_on_the_sweep_matches_python(page_out, trains, gt, which):
    """The whole path in one comparison: the browser's detector, its scorer and
    its bookkeeping against the Python's, on the same trains and the same
    planted events, for every setting the sweep tries. Counts compare exactly;
    the ratios at 1e-9."""
    sweep = page_out["sweeps"][which]
    rng = tuple(page_out["range"])
    assert len(sweep["rows"]) == len(OPERATING_POINTS[which].grid)
    for row in sweep["rows"]:
        det = _py_detect(which, trains, rng, sweep["base"], sweep["knob"],
                         row["knob"])
        s = score_detections(gt, det.locs, widths=det.widths, tol_sec=TOL)
        at = f"{which} @ {row['knob']:g}"
        assert row["nDetected"] == s.n_detected, at
        assert row["nHit"] == s.n_hit, at
        assert row["nMiss"] == s.n_miss, at
        assert row["nFa"] == s.n_fa, at
        assert row["nDup"] == s.n_duplicate, at
        for field, py in (("precision", s.precision), ("recall", s.recall),
                          ("f1", s.f1)):
            got = row[field]
            if not np.isfinite(py):
                assert got is None or not np.isfinite(got), f"{at}: {field}"
            else:
                assert abs(got - py) < 1e-9, (
                    f"{at}: {field} {got!r} vs {py!r}")
        for frac, (n, h) in row["byFrac"]:
            assert (n, h) == s.by_frac[frac], f"{at}: recall at {frac}"


def test_the_sweep_separates_settings_rather_than_returning_one_answer(page_out):
    """A sweep whose every row is identical proves nothing about the code that
    produced it, and every comparison above would pass on a detector that
    ignored its knob entirely. At least one detector has to move."""
    moved = {}
    for which, sweep in page_out["sweeps"].items():
        f1 = [r["f1"] for r in sweep["rows"]]
        moved[which] = len({round(v, 9) for v in f1}) > 1
    assert moved["rate"], (
        "RateDetect returned the same F1 at every threshold from "
        f"{OPERATING_POINTS['rate'].grid[0]} to "
        f"{OPERATING_POINTS['rate'].grid[-1]} — the knob is not reaching it")
    assert any(moved.values())


def test_the_table_on_screen_is_the_sweep_that_was_run(viewer, page_out):
    """A computation checked to 1e-9 and a table built from something else would
    pass every test above. So the button is pressed for real and the rendered
    rows are read back and compared to the numbers the same sweep returns."""
    page, errs = viewer
    rows = page.evaluate("""async (sim) => {
      for (const [id, v] of Object.entries(sim)) document.getElementById(id).value = v;
      await runSim();
      document.getElementById("dDet").value = "rate";
      paintDetectorChoice();
      document.getElementById("tTol").value = "1.5";
      await runTune();
      return [...document.querySelectorAll("#tuneOut table tr")].slice(1).map(
        tr => [...tr.querySelectorAll("td")].map(td => td.textContent));
    }""", SIM)
    assert not errs, errs

    want = page_out["sweeps"]["rate"]["rows"]
    assert len(rows) == len(want), f"{len(rows)} rows drawn, {len(want)} computed"
    for cells, r in zip(rows, want):
        where = f"row for knob {r['knob']:g}"
        assert float(cells[0]) == pytest.approx(r["knob"]), where
        assert int(cells[1]) == r["nDetected"], where
        assert int(cells[2]) == r["nHit"], where
        assert int(cells[3]) == r["nMiss"], where
        assert int(cells[4].split()[0]) == r["nFa"], where
        for col, val in ((5, r["precision"]), (6, r["recall"]), (7, r["f1"])):
            assert float(cells[col]) == pytest.approx(round(val, 2), abs=5e-3), (
                f"{where}, column {col}")

    # and the row the page bolded is the one the rule chooses
    best = page.evaluate(PICK, [{"knob": r["knob"], "f1": r["f1"]} for r in want])
    marked = page.evaluate(
        """() => [...document.querySelectorAll("#tuneOut tr.best td")]
                   .map(td => td.textContent)[0] ?? null""")
    if best["knob"] is None:
        assert marked is None, "a boundary value was marked as the best row"
    else:
        assert float(marked) == pytest.approx(best["knob"])


# --------------------------------------- the scorer, on cases it has to get right

SCORE = """(v) => {
  const s = scoreDetections(v.times, v.fracs, v.onsets, v.widths, v.tol);
  return {nPlanted: s.nPlanted, nDetected: s.nDetected, nHit: s.nHit,
          nMiss: s.nMiss, nFa: s.nFa, nDup: s.nDup,
          precision: s.precision, recall: s.recall, f1: s.f1,
          byFrac: [...s.byFrac.entries()]};
}"""


@pytest.fixture(scope="module")
def score_in_browser(viewer):
    page, _ = viewer
    return lambda **v: page.evaluate(SCORE, v)


VECTORS = {
    # In-order greedy gives BOTH events a hit here; closest-pair gives one. The
    # detection at 10.9 is a much better match for the second planted event than
    # for the first, and walking the events in time lets the first consume it.
    # Nothing a detector produced on the simulated fixture was ever this tight,
    # so without this vector the matching rule could be rewritten unnoticed.
    "greedy order decides the count": dict(
        times=[10.0, 11.0], fracs=[0.3, 0.3],
        onsets=[10.9, 12.4], widths=[0.0, 0.0], tol=1.5),
    # One event, two detections on it: a detector that fragmented rather than
    # one that fired at nothing. The second is a false alarm either way, but it
    # is a DUPLICATE, and the two failures want different repairs — a merge gap
    # and a threshold.
    "a fragmented event is a duplicate, not noise": dict(
        times=[10.0], fracs=[0.3],
        onsets=[9.9, 10.1, 30.0], widths=[0.0, 0.0, 0.0], tol=1.5),
    # A binned detector reports a left edge and a span. Scored as a point it
    # misses by most of a bin; scored as the interval it claims, it is a hit.
    # This is the failure that once read 0.00 recall on detections that were all
    # correct.
    "a wide detection is an interval, not a point": dict(
        times=[26.0], fracs=[1.0],
        onsets=[20.0], widths=[10.0], tol=1.5),
    # Onsets arriving out of order, one non-finite, one negative width. Sorting
    # and cleaning happen before any matching, and widths are PER DETECTION —
    # the widest span here belongs to the earliest onset, so an implementation
    # that sorted the onsets and left the widths where they were would give this
    # vector a different hit count rather than merely a different pairing. The
    # negative width is arranged to matter too: unclamped it inverts the span at
    # 100 s into [100, 97], which pushes the event at 99 s out of tolerance.
    "unsorted, non-finite, and widths that must ride the sort": dict(
        times=[12.0, 40.0, 99.0], fracs=[0.3, 0.1, 0.3],
        onsets=[40.2, None, 4.0, 100.0], widths=[0.0, 1.0, 10.0, -3.0], tol=1.5),
    # Two detections contain the same event, so both sit at distance zero and the
    # gap alone cannot separate them. The one CENTRED on the event takes it,
    # which leaves the wide one free for the second event; without that
    # tiebreak the wide one is consumed first and the second event is missed.
    "two spans over one event, and the centred one takes it": dict(
        times=[10.0, 25.0], fracs=[1.0, 0.3],
        onsets=[0.0, 9.0], widths=[30.0, 2.0], tol=1.5),
}


@pytest.mark.parametrize("name", list(VECTORS))
def test_the_scorer_agrees_on_the_cases_that_decide_the_rule(
        score_in_browser, name):
    v = VECTORS[name]
    onsets = np.array([np.nan if x is None else x for x in v["onsets"]],
                      dtype=float)
    gt = GroundTruth(events=[
        PlantedEvent(time=float(x), frac=float(f), n_part=0, rois=(),
                     jitter_sec=0.0)
        for x, f in zip(v["times"], v["fracs"])])
    py = score_detections(gt, onsets, widths=np.array(v["widths"], dtype=float),
                          tol_sec=v["tol"])
    got = score_in_browser(**v)

    assert got["nDetected"] == py.n_detected, name
    assert got["nHit"] == py.n_hit, name
    assert got["nMiss"] == py.n_miss, name
    assert got["nFa"] == py.n_fa, name
    assert got["nDup"] == py.n_duplicate, name
    for field, val in (("precision", py.precision), ("recall", py.recall),
                       ("f1", py.f1)):
        if np.isfinite(val):
            assert abs(got[field] - val) < 1e-9, f"{name}: {field}"
        else:
            assert got[field] is None or not np.isfinite(got[field]), name
    assert {f: tuple(c) for f, c in got["byFrac"]} == py.by_frac, name


def test_those_vectors_are_the_ones_that_separate_the_rules():
    """Each vector above exists to kill a specific wrong implementation. If the
    Python's own answer stops having the property the vector was built for, the
    vector has quietly become decoration and this says so."""
    def sc(v):
        gt = GroundTruth(events=[
            PlantedEvent(time=float(x), frac=float(f), n_part=0, rois=(),
                         jitter_sec=0.0)
            for x, f in zip(v["times"], v["fracs"])])
        onsets = np.array([np.nan if x is None else x for x in v["onsets"]],
                          dtype=float)
        return score_detections(gt, onsets,
                                widths=np.array(v["widths"], dtype=float),
                                tol_sec=v["tol"])

    assert sc(VECTORS["greedy order decides the count"]).n_hit == 1, (
        "closest-pair matching no longer costs this vector a hit — in-order "
        "matching would now score it the same and the vector proves nothing")
    assert sc(VECTORS["a fragmented event is a duplicate, not noise"]
              ).n_duplicate == 1, "no duplicate in the duplicate vector"
    assert sc(VECTORS["a wide detection is an interval, not a point"]
              ).n_hit == 1, "the wide detection stopped covering its event"
    assert sc(VECTORS["unsorted, non-finite, and widths that must ride the sort"]
              ).n_hit == 3, (
        "the widths vector stopped depending on widths riding the sort, or on "
        "the negative width being clamped — it needs all three hits")
    assert sc(VECTORS["two spans over one event, and the centred one takes it"]
              ).n_hit == 2, (
        "the tiebreak vector no longer costs a hit when the centred span loses, "
        "so dropping the tiebreak would score it the same")


# ------------------------------------------ choosing a setting off the sweep

def _curve(f1s):
    """A sweep shaped for `pickOperatingPoint`, with only the fields it reads."""
    return [{"knob": i, "f1": v} for i, v in enumerate(f1s)]


def _bench_curve(shape):
    """Real `BenchResult`s whose F1 traces a given shape.

    Built from counts rather than forged, so the actual
    `bench.pick_operating_point` runs against them — a restatement of its rule
    here would only prove that this file agrees with itself.
    """
    return [BenchResult(detector="rate", regime="baseline_quiet", knob_value=i,
                        n_planted=100, n_detected=d, n_hit=h)
            for i, (d, h) in enumerate(shape)]


PICK = """(rows) => {
  const p = pickOperatingPoint(rows);
  return {knob: p.row ? p.row.knob : null, why: p.why};
}"""


@pytest.fixture(scope="module")
def pick_in_browser(viewer):
    page, _ = viewer
    return lambda rows: page.evaluate(PICK, rows)


@pytest.mark.parametrize("shape,expect,why", [
    ([(20, 6), (40, 28), (60, 64), (20, 30), (20, 12)], 2, "a plain interior peak"),
    ([(20, 12), (100, 90), (100, 90), (100, 90), (20, 18)], 1,
     "a plateau — the first interior point on it wins"),
    ([(20, 6), (20, 18), (100, 90), (100, 90), (100, 90)], 2,
     "a plateau that REACHES the edge is still bracketed, and is allowed"),
])
def test_it_picks_the_point_python_picks(pick_in_browser, shape, expect, why):
    curve = _bench_curve(shape)
    assert pick_operating_point(curve).knob_value == expect, why
    assert pick_in_browser(_curve([r.f1 for r in curve]))["knob"] == expect, why


def test_the_real_python_rule_refuses_an_edge_and_so_does_the_browser(
        pick_in_browser):
    """The refusal is the reason this rule exists: an optimum at the end of the
    grid is the search saying it stopped too early, and a boundary value has
    been published upstream as a calibrated setting before. Python raises; the
    browser has no exception to raise at a reader, so it names no row and says
    why — and both have to agree that this curve has no answer on it."""
    curve = _bench_curve([(20, 10), (40, 25), (60, 45), (80, 70), (100, 95)])
    assert [round(r.f1, 2) for r in curve] == [0.17, 0.36, 0.56, 0.78, 0.95], (
        "the curve stopped climbing to the last point, which is the case here")
    with pytest.raises(EdgeOfRange):
        pick_operating_point(curve)

    got = pick_in_browser(_curve([r.f1 for r in curve]))
    assert got["knob"] is None, "the browser named a boundary value as best"
    assert "high end" in got["why"], got["why"]
    assert "widen" in got["why"].lower(), got["why"]


def test_a_knob_that_changes_nothing_is_refused_on_both_sides(pick_in_browser):
    """The other refusal, and it must not be confused with the edge one — the
    remedies are opposite. A grid whose every point ties has not measured the
    knob, so widening produces more identical rows; the answer is to sweep
    whatever is actually binding. SPIKE-synch fell through this gap and answered
    every fold on the scoreboard while measuring nothing.

    Both sides must refuse, and the browser must not tell a reader to widen."""
    curve = _bench_curve([(50, 30)] * 5)
    assert len({round(r.f1, 9) for r in curve}) == 1, "the curve must be flat"
    with pytest.raises(DegenerateSweep):
        pick_operating_point(curve)

    got = pick_in_browser(_curve([r.f1 for r in curve]))
    assert got["knob"] is None, "the browser named a setting on a flat sweep"
    assert "same f1" in got["why"].lower(), got["why"]
    assert "widening the range will not help" in got["why"].lower(), got["why"]
