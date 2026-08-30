"""CICADA in the browser: anchored on the peak, and refusing when there isn't one.

CICADA is the sixth detector and the only one that does not locate an event at
its half-rise. `src/bugarach/store.py` says so in terms — **do not "correct"
cicada to t50rise** — and records that two sentences claiming otherwise have
already been written in that file and misled two readers. The reason is not
deference to the original: a transient runs from half-rise to peak over ~0.3 s in
a fast stream and ~2 s in a slow one, and 2 s is wider than the tolerance a
detection is scored at, so onsets alone make almost any two events look
simultaneous.

That collides with the import contract, which sends `time_sec` as the half-rise
and leaves the peak optional. The peak is recoverable two ways and no others:

  * `peak_sec`, when the producer sends it;
  * `time_sec + width_sec`, but ONLY where `width_def` is `t50rise_to_peak` —
    that width is `locs - t50rise`, the quantity `cicada.py` calls `rise_dur`.

Under `fwhm` or `above_threshold` the sum is not a peak. Adding them anyway is
the export spec's own warning made real: "a column that means two things without
saying which yields a plausible wrong answer rather than an error". So the
refusals below are the load-bearing tests, not the happy path.

The detector reads the folder and nothing else — no store, no companion file.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pytest
from conftest import locust_suppressed_in_the_browser

#: Every test in this file drives the browser's locust, which is held out of the
#: build for this release (Tony, 2026-08-29). Nothing below is deleted and
#: nothing below is wrong: the refusals it covers are the load-bearing part of
#: that detector, and they are expensive to re-derive. Keyed to the page's own
#: flag, so the day the suppression is lifted this file wakes up with it.
pytestmark = pytest.mark.skipif(
    locust_suppressed_in_the_browser(),
    reason="locust is suppressed in this build; these return when it does")

VIEWER = Path(__file__).resolve().parents[1] / "docs/site/raster_viewer.html"

SIM = {"sRec": "1", "sMin": "12", "sRoi": "20", "sRate": "12", "sEv": "8",
       "sJit": "360", "sSeed": "7"}

SETUP = """async (sim) => {
  for (const [id, v] of Object.entries(sim)) document.getElementById(id).value = v;
  await runSim();
  /* IT DOES NOT SELECT THE DETECTOR, and that is deliberate. Selecting it means
     lifting the `unavailable` field the page now carries on it, and doing that
     here would leave it lifted for the whole test — including the two tests that
     assert the option IS disabled, which would then be measuring this harness
     rather than the page. `DETECT` lifts it around the run and puts it back. */
  paintDetectorChoice();
}"""

DETECT = """async () => {
  /* LIFT THE WITHHOLDING FOR THE LENGTH OF THE RUN, then put it back.
     Since 2026-08-29 this detector carries `unavailable` — withheld from the
     public build while how it should be named and credited is settled — and the
     page enforces that in THREE places, not one: the option is drawn disabled,
     `whichDetector()` falls back to `rate` for any unavailable key, and
     `offReason` gates the run. Enabling the option alone is not enough; the
     fallback silently ran RateDetect and every assertion below then compared
     RateDetect's output while reading as this detector's test.

     So the field comes off, the run happens, the field goes back. What that
     buys: this file keeps testing the DETECTOR — its raster, its refusals, its
     parity — while the page withholds it, which is the state it will be restored
     from. Whether a VISITOR can reach it is a different question owned by
     `test_webapp_tune_picks` and `test_webapp_scoreboard`, which assert the
     opposite and would fail if this leaked. */
  const held = DETECTORS.cicada.unavailable;
  delete DETECTORS.cicada.unavailable;
  try {
    paintDetectorChoice();        // rebuilds the options; must follow the lift
    document.getElementById("dDet").value = "cicada";
    if (whichDetector() !== "cicada")
      throw new Error("could not select the detector under test");
    await runDetect();
  } finally {
    if (held !== undefined) DETECTORS.cicada.unavailable = held;
  }
  const box = document.getElementById("detectOut");
  return {text: box.innerText,
          bad: [...box.querySelectorAll("p.verdict.bad")].map(p => p.textContent),
          rows: DETECT ? DETECT.rows.length : null,
          units: DETECT ? [...new Set(DETECT.rows.map(r => r.strength_unit))] : []};
}"""


@pytest.fixture(scope="module")
def viewer():
    pytest.importorskip("playwright.sync_api",
                        reason="CICADA runs in the page; checking it needs the page")
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


@pytest.fixture
def page(viewer):
    p, errs = viewer
    errs.clear()
    p.evaluate(SETUP, SIM)
    assert not errs, errs
    return p


def spoil(page, *, width_def=None, drop_peaks=False):
    """Rewrite the loaded folder's width story, the way a different producer
    would have sent it."""
    return page.evaluate("""([wd, drop]) => {
      for (const rec of RECORDINGS) {
        if (!rec.loaded) continue;
        if (drop)
          for (const [, byRoi] of rec.loaded.peaks)
            for (const id of byRoi.keys())
              byRoi.set(id, byRoi.get(id).map(() => NaN));
        if (wd !== null)
          rec.loaded.widthDefs.set("events", new Set(wd));
      }
    }""", [width_def, drop_peaks])


# ------------------------------------------------------------------ it is there

def test_it_is_in_the_chooser_and_the_visitor_cannot_pick_it(page):
    """Both halves, because either one alone describes the wrong page.

    PRESENT, because a detector deleted from the registry takes its refusals, its
    parity harness, and an older detections file's ability to draw with it.
    DISABLED, because it is withheld from this build while how it should be named
    and credited is settled — and an enabled control that `whichDetector()` then
    refuses is a button that does nothing.
    """
    got = page.evaluate(
        """() => {
             const o = [...document.getElementById("dDet").options]
                         .find(x => x.value === "cicada");
             return o ? {present: true, disabled: o.disabled} : {present: false};
           }""")
    assert got["present"], "the row was deleted rather than withheld"
    assert got["disabled"], "a withheld detector is offered to visitors"


def test_the_six_detectors_are_all_present(page):
    """All six are in the file. Two of them carry `unavailable` and cannot be
    started from this page, which is a different statement — asserted above, and
    from the other side in `test_webapp_tune_picks`."""
    opts = page.evaluate(
        """() => [...document.getElementById("dDet").options].map(o => o.value)""")
    assert set(opts) == {"rate", "sce", "coact", "loco", "sync", "cicada"}, opts
    withheld = page.evaluate(
        "() => Object.keys(DETECTORS).filter(k => DETECTORS[k].unavailable)")
    assert sorted(withheld) == ["cicada", "sync"], withheld


# ------------------------------------------------------- it runs on a good folder

def test_it_runs_when_the_folder_carries_t50rise_to_peak(page):
    out = page.evaluate(DETECT)
    assert not out["bad"], out["bad"]
    assert out["rows"], "no detections at all"


def test_its_rows_declare_the_unit_emit_declares(page):
    from bugarach.emit import DETECTOR_FIELDS
    out = page.evaluate(DETECT)
    assert out["units"] == [DETECTOR_FIELDS["cicada"].strength_unit]


def test_the_anchor_is_the_peak_and_not_the_half_rise(page):
    """The whole point. `peaks` must be `time_sec + width_sec`, event by event,
    and must NOT equal the times themselves."""
    same, shifted, n = page.evaluate("""() => {
      const d = RECORDINGS[0].loaded;
      const times = d.streams.get("events"), pk = d.peaks.get("events"),
            w = d.rise.get("events");
      let same = 0, shifted = 0, n = 0;
      for (const [id, ts] of times) {
        const p = pk.get(id), ws = w.get(id);
        for (let i = 0; i < ts.length; i++) {
          n++;
          if (p[i] === ts[i]) same++;
          if (Math.abs(p[i] - (ts[i] + ws[i])) < 1e-9) shifted++;
        }
      }
      return [same, shifted, n];
    }""")
    assert n, "the folder carried no events"
    assert shifted == n, f"only {shifted}/{n} peaks are time_sec + width_sec"
    assert same == 0, f"{same} peaks equal the half-rise — the anchor did not move"


# ------------------------------------------------------------------ the refusals

def test_it_refuses_a_width_that_does_not_reach_the_peak(page):
    """`fwhm` is a real width and a wrong summand. This is the case Tony named
    as the source of the chaos."""
    spoil(page, width_def=["fwhm"], drop_peaks=True)
    out = page.evaluate(DETECT)
    assert out["bad"], "it ran anyway"
    why = out["bad"][0]
    assert "fwhm" in why, why
    # names the two real routes: the column every current export sends, and the
    # width_def interface2 actually emits -- not the spec's illustration, which
    # would read as "rename your correct column"
    assert "peak_sec" in why, why
    assert "rise_interval_peak_minus_t50rise" in why, why


def test_the_refusal_survives_on_screen(page):
    """It is appended to a box that `clearDetect` empties, so the order of those
    two calls decides whether the reader sees an explanation or a blank panel."""
    spoil(page, width_def=["fwhm"], drop_peaks=True)
    out = page.evaluate(DETECT)
    assert "did not run" in out["text"], repr(out["text"])
    assert len(out["text"].strip()) > 80, repr(out["text"])


def test_it_refuses_a_folder_with_no_width_at_all(page):
    spoil(page, width_def=[], drop_peaks=True)
    out = page.evaluate(DETECT)
    assert out["bad"], "it ran without a peak"


def test_it_refuses_two_width_definitions_in_one_stream(page):
    """The contract asks for one rule per stream. Two means the column cannot be
    read at all, let alone added to an onset."""
    spoil(page, width_def=["fwhm", "t50rise_to_peak"])
    out = page.evaluate(DETECT)
    assert out["bad"], "it picked one of two definitions"
    assert "width_def" in out["bad"][0], out["bad"][0]


def test_refusing_is_not_the_same_as_finding_nothing(page):
    """An empty result would read as 'nothing was coordinated'. The refusal has
    to be a sentence, and no rows may be left behind for the download button."""
    spoil(page, width_def=["fwhm"], drop_peaks=True)
    out = page.evaluate(DETECT)
    assert out["rows"] is None, "a refusal left detections behind"
    assert page.evaluate(
        """() => document.getElementById("saveDetections").disabled""") is True


def test_it_does_not_quietly_fall_back_to_the_onsets(page):
    """The failure that would be invisible: run on `time_sec`, return a confident
    answer to a different question."""
    spoil(page, width_def=["fwhm"], drop_peaks=True)
    out = page.evaluate(DETECT)
    assert out["rows"] is None
    assert "onsets" in out["bad"][0], out["bad"][0]


# ------------------------------------- the producer's vocabulary, not the spec's

# `export_folder_spec.md` offers `t50rise_to_peak` as an ILLUSTRATION, and says the
# string is the producer's, carried and never parsed. These are the names really in
# use, audited across 164,527 events in
# `docs/reviews/pensub_export_validation_2026-08-20.md`:
#
#   slow  rise_interval_peak_minus_t50rise   peak_sec - time_sec == width_sec for
#                                            55,168 of 55,174 events
#   fast  halfprom_width_findpeaks_w         holds for 21 of 109,353 — coincidence
#
# The first version of this matched only the spec's example, so an export sending
# the slow width and no `peak_sec` would have been refused for carrying exactly
# the right column.
REAL_WIDTH_DEFS = [
    ("rise_interval_peak_minus_t50rise", True),
    ("halfprom_width_findpeaks_w", False),
    ("t50rise_to_peak", True),          # the spec's illustration still works
    ("fwhm", False),
    ("above_threshold", False),
    ("", False),
]


@pytest.mark.parametrize("width_def,reaches", REAL_WIDTH_DEFS)
def test_only_a_width_that_reaches_the_peak_may_stand_in_for_one(
        viewer, width_def, reaches):
    page, errs = viewer
    errs.clear()
    got = page.evaluate("(wd) => WIDTH_REACHES_PEAK.has(wd)", width_def)
    assert not errs, errs
    assert got is reaches, f"{width_def!r} classified wrong"


def test_the_name_interface2_actually_sends_is_recognised(viewer):
    """The one that matters: this is the string in every export on disk."""
    page, _ = viewer
    assert page.evaluate(
        """() => WIDTH_REACHES_PEAK.has("rise_interval_peak_minus_t50rise")""")


def test_the_refusal_names_a_string_a_producer_would_recognise(page):
    """Telling a producer to send `t50rise_to_peak` when their exporter already
    emits `rise_interval_peak_minus_t50rise` invites them to rename a correct
    column."""
    spoil(page, width_def=["fwhm"], drop_peaks=True)
    why = page.evaluate(DETECT)["bad"][0]
    assert "peak_sec" in why, why
    assert "rise_interval_peak_minus_t50rise" in why, why


# ------------------------------------------------- the port agrees with the Python

def test_the_coactivity_trace_is_the_pythons(viewer):
    """The threshold draws random numbers and the two languages never will agree
    on those, so it is supplied from outside and everything downstream of it is
    compared: the raster and the sliding count, both deterministic.
    """
    from bugarach.detectors.cicada import _build_raster, _slide_coact

    page, errs = viewer
    errs.clear()
    rng = np.random.RandomState(7)
    nc, T, dt = 12, 200.0, 0.1
    peaks, durs = [], []
    for _ in range(nc):
        n = rng.randint(3, 15)
        peaks.append(np.sort(rng.uniform(0, T, n)))
        durs.append(rng.uniform(0.2, 1.5, n))
    # a moment where many cells fire together, so there is something to find
    for c in range(8):
        peaks[c] = np.sort(np.append(peaks[c], 100.0 + rng.uniform(-0.05, 0.05)))
        durs[c] = np.append(durs[c], 0.8)

    nf = int(np.floor(T / dt))
    want = _slide_coact(_build_raster(peaks, durs, 0.0, dt, nf, 1), 1)

    got = page.evaluate("""([peaks, durs, T, dt]) => Array.from(cicadaDetect(
        peaks, durs, [0, T],
        {gridDt: dt, nSynchronousFrames: 1, sceMinDistanceFrames: 4,
         perEventDuration: true, nSurrogates: 0}).obs)""",
        [[list(map(float, v)) for v in peaks],
         [list(map(float, v)) for v in durs], T, dt])
    assert not errs, errs
    assert len(got) == want.size, f"{len(got)} frames vs {want.size}"
    assert np.array_equal(np.asarray(got, dtype=float), want), (
        "the browser's coactivity trace differs from the Python's")


# ------------------------------------------------- it says when it is degenerate

def test_a_sparse_folder_is_told_it_is_sparse(page):
    """On a sparse recording the surrogate threshold lands at one active cell and
    every isolated transient clears it. That is faithful — the Python does the
    same — and it is not coordination, so the page counts those rows and says so
    rather than raising a floor until they disappear."""
    out = page.evaluate(DETECT)
    assert "one cell only" in out["text"], out["text"][:400]
    if "single-cell moments" in out["text"]:
        assert "too sparse" in out["text"]
