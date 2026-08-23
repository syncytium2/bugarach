"""The sweep now fits on some recordings and reports on others. On screen.

`docs/site/scoring.js` landed with `foldSplit` and `poolScores` and no callers,
which meant held-out scoring existed in the tree and nowhere a reader could see
it. The sweep fitted a knob on one recording and scored it on that same
recording, and nothing beside the number said so — an upper bound printed in the
place a measurement goes.

These drive the button and read what the page actually rendered, because that is
the only thing that goes in a slide. The lesson is written down in
`docs/todo/2026-08-20-webapp-session-status.md`: a window-provenance bug shipped
once because every test read the page's state directly and none pressed the
button, so the numbers were right while the sentence beside them was false.

Two claims are checked here and they are different claims:

  * the page SPLITS — folds appear, every recording is used, and the reported
    number comes from folds the knob was not chosen on;
  * the page SAYS WHICH — a one-recording folder cannot hold anything out, and
    has to admit that rather than print the same F1 in the same place.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

VIEWER = Path(__file__).resolve().parents[1] / "docs/site/raster_viewer.html"

# Four recordings, kept small: the sweep runs the detector over every recording
# at every setting on the grid, and this is a browser.
SIM_MANY = {"sRec": "4", "sMin": "12", "sRoi": "18", "sRate": "10",
            "sEv": "10", "sJit": "360", "sSeed": "4"}
SIM_ONE = dict(SIM_MANY, sRec="1")

RUN = """async (sim) => {
  for (const [id, v] of Object.entries(sim)) document.getElementById(id).value = v;
  await runSim();
  document.getElementById("dDet").value = "rate";
  paintDetectorChoice();
  document.getElementById("tTol").value = "1.5";
  await runTune();
  const box = document.getElementById("tuneOut");
  return {
    head: box.querySelector("h4")?.textContent ?? "",
    sub: box.querySelector("p.sub")?.textContent ?? "",
    verdicts: [...box.querySelectorAll("p.verdict")].map(p => p.textContent),
    bad: [...box.querySelectorAll("p.verdict.bad")].map(p => p.textContent),
    caveats: [...box.querySelectorAll("p.caveat")].map(p => p.textContent),
    nRows: box.querySelectorAll("table tr").length - 1,
    nRecordings: RECORDINGS.length,
  };
}"""


@pytest.fixture(scope="module")
def viewer():
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
def many(viewer):
    page, errs = viewer
    out = page.evaluate(RUN, SIM_MANY)
    assert not errs, errs
    return out


@pytest.fixture(scope="module")
def one(viewer):
    page, errs = viewer
    out = page.evaluate(RUN, SIM_ONE)
    assert not errs, errs
    return out


# --------------------------------------------------------------- it splits

def test_the_sweep_uses_the_whole_folder_not_the_recording_on_screen(many):
    assert many["nRecordings"] == 4
    assert "4 simulated recordings" in many["head"], many["head"]


def test_the_page_reports_how_many_folds_it_used(many):
    assert re.search(r"\b4 folds\b", many["sub"]), many["sub"]


def test_a_held_out_number_is_reported_and_named_as_such(many):
    held = [v for v in many["verdicts"] if v.startswith("Held out:")]
    assert held, many["verdicts"]
    assert re.search(r"F1 \d\.\d\d", held[0]), held[0]
    assert "never saw" in held[0], held[0]


def test_the_held_out_number_is_scored_on_data_it_was_not_fitted_on(many):
    """The arithmetic is `poolScores`', checked elsewhere at 1e-9. What this
    asserts is the claim on screen: each fold trained on 3 and scored on 1."""
    held = next(v for v in many["verdicts"] if v.startswith("Held out:"))
    assert "fitted on 3 recordings" in held, held
    assert "scored on 1" in held, held


def test_the_reader_is_told_the_table_is_not_the_result(many):
    held = next(v for v in many["verdicts"] if v.startswith("Held out:"))
    assert "the table above is not" in held, held


# ------------------------------------------------------ it says which is which

def test_one_recording_cannot_hold_anything_out_and_says_so(one):
    """The failure this whole change exists to prevent: the same F1, in the same
    place, with nothing marking it as in-sample."""
    assert one["nRecordings"] == 1
    assert not [v for v in one["verdicts"] if v.startswith("Held out:")], one["verdicts"]
    admits = [b for b in one["bad"] if "nothing to hold out" in b]
    assert admits, one["bad"]
    assert "upper bound" in admits[0], admits[0]


def test_the_one_recording_case_still_sweeps(one):
    """Refusing to hold out is not refusing to work — the table is still there,
    and the existing tune-parity test drives exactly this path."""
    assert one["nRows"] > 1, one


def test_the_single_recording_header_names_the_recording(one):
    assert "simulated_01" in one["head"], one["head"]


# ------------------------------------------------------------------ the gap

def test_the_in_sample_gap_is_shown_when_there_is_one(many):
    """Optional by construction — it appears only when the in-sample best beats
    the held-out mean, which is the usual direction but not guaranteed on a
    small simulated data set. When it is there it must be labelled."""
    gap = [c for c in many["caveats"] if "higher than the held-out mean" in c]
    if gap:
        assert "fitting and reporting on the same recordings" in gap[0], gap[0]
