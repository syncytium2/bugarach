"""Assessing says it happened, and the page stops claiming no detector is involved.

From Tony using the app, 2026-08-21.

**"Nothing happens when I click Assess this recording."** It did happen — 185 ms
on a real 34-ROI recording, a full table, no errors. Three things hid it: the
table renders in the other column below the canvas, the button restores itself
faster than a spinner appears, and the raster is marked only when a K has been
chosen, which defaults to `none`. So by default, assessing changed the picture in
no way at all.

The fix is persistence rather than progress. There is nothing to wait for; what
was missing is something that still says "assessed" a second later.

**And it must not pick a K.** The panel spends a paragraph on *"K is a scan, not
a choice"*, and defaulting one to make the raster light up would have the page
quietly make the choice it refuses to make. So the neutral mark names no K and
says choosing one is the next move.

**Separately: "no detector involved" was false.** The assessor finds coordinated
clusters and returns their times, participants and spread — that is detection.
What it has no part of is an **operating point**: every one of the six commits to
a setting, and this scans K and commits to none.
"""

from __future__ import annotations

from pathlib import Path

import pytest

VIEWER = Path(__file__).resolve().parents[1] / "docs/site/raster_viewer.html"

# long enough to clear the assessment's own 15-minute floor
SIM = {"sRec": "1", "sMin": "22", "sRoi": "24", "sRate": "45", "sEv": "14",
       "sJit": "300", "sSeed": "6",
       # no treatment windows, so the whole 22 min is the assessed window and it
       # clears the 15-minute floor. With windows it does not — see
       # `test_a_run_that_measured_nothing_does_not_claim_it_did`.
       "sWin": "0"}


@pytest.fixture(scope="module")
def page():
    pytest.importorskip("playwright.sync_api",
                        reason="the feedback is a property of the running page")
    from playwright.sync_api import sync_playwright

    with sync_playwright() as p:
        try:
            browser = p.chromium.launch()
        except Exception as e:                        # noqa: BLE001
            pytest.skip(f"no chromium available: {type(e).__name__}")
        try:
            pg = browser.new_page()
            errs: list[str] = []
            pg.on("pageerror", lambda e: errs.append(str(e)))
            pg.goto(VIEWER.as_uri(), wait_until="load")
            yield pg, errs
        finally:
            browser.close()


ASSESS = """async (sim) => {
  for (const [k, v] of Object.entries(sim)) document.getElementById(k).value = v;
  await runSim();
  await show(RECORDINGS[0]);
  const before = {chip: document.getElementById("cntAssess").textContent,
                  assessed: ASSESSED};
  await runAssess();
  return {
    before,
    chip: document.getElementById("cntAssess").textContent,
    chipClass: document.getElementById("cntAssess").className,
    assessed: ASSESSED,
    marked: ASSESS ? {K: ASSESS.K} : null,
    kControl: document.getElementById("aK").value,
    outLen: document.getElementById("assessOut").innerText.length,
  };
}"""


@pytest.fixture(scope="module")
def assessed(page):
    pg, errs = page
    got = pg.evaluate(ASSESS, SIM)
    assert not errs, errs
    return got


def test_the_chip_says_nothing_before_and_says_assessed_after(assessed):
    assert assessed["before"]["assessed"] is None
    assert "assessed" not in assessed["before"]["chip"].lower()
    assert assessed["assessed"], "nothing recorded that the assessment ran"
    assert "assessed" in assessed["chip"].lower(), assessed["chip"]


def test_the_chip_marks_itself_as_a_good_state_the_way_the_folder_check_does(
        assessed):
    assert "ok" in assessed["chipClass"].split(), assessed["chipClass"]


def test_it_did_not_quietly_pick_a_K(assessed):
    """The load-bearing one. Making the raster light up by defaulting K would
    have the page make the choice its own panel refuses to make."""
    assert assessed["kControl"] == "0", (
        "the K control was changed by assessing; K is a scan, not a choice")
    assert assessed["marked"] is None, (
        "cluster ticks were drawn at a K nobody chose")


def test_the_assessment_still_produced_its_table(assessed):
    assert assessed["outLen"] > 200


SHORT_WINDOW = """async () => {
  // three windows over 22 minutes puts the baseline under the 15-minute floor,
  // so the assessment runs and measures nothing
  const spec = {sRec: "1", sMin: "22", sRoi: "24", sRate: "45", sEv: "14",
                sJit: "300", sSeed: "6", sWin: "3"};
  for (const [k, v] of Object.entries(spec)) document.getElementById(k).value = v;
  await runSim();
  await show(RECORDINGS[0]);
  await runAssess();
  return {chip: document.getElementById("cntAssess").textContent,
          cls: document.getElementById("cntAssess").className,
          measured: ASSESSED ? ASSESSED.measured : null,
          panel: document.getElementById("assessOut").innerText};
}"""


def test_a_run_that_measured_nothing_does_not_claim_it_did(page):
    """The bug this caught on its own screenshot.

    A window under the assessment's 15-minute floor yields no measures and the
    panel says so. The first version of the chip called that "✓ assessed",
    which claims a result the run explicitly declined to give. "Nothing
    happened" and "nothing could be measured" look identical from the button,
    and only one of them is a reason to change the window.
    """
    pg, errs = page
    got = pg.evaluate(SHORT_WINDOW)
    assert not errs, errs
    assert got["measured"] is False, (
        "this fixture is meant to fall under the floor; if it no longer does, "
        "the test needs a shorter window rather than a weaker assertion")
    assert "floor" in got["panel"].lower(), got["panel"][:200]
    assert "✓" not in got["chip"], f"claims success after measuring nothing: {got['chip']!r}"
    assert "ok" not in got["cls"].split(), got["cls"]
    assert "short" in got["chip"].lower(), got["chip"]


LANE = """() => {
  // the neutral mark is drawn to canvas; read the string the drawing code builds
  const marked = ASSESS && ASSESS.recId === RECORDINGS[0].id;
  return ASSESSED ? (marked ? "assessed · clusters marked at K " + ASSESS.K
                            : "assessed · choose a K to mark clusters") : "";
}"""


def test_the_raster_says_the_measurement_happened_without_naming_a_K(page,
                                                                    assessed):
    pg, _ = page
    mark = pg.evaluate(LANE)
    assert mark.startswith("assessed"), mark
    assert "choose a K" in mark, (
        "the neutral mark should point at the next move rather than supply it")


SWITCH = """async () => {
  // a second recording, never assessed — the chip must not carry over
  const spec = {sRec: "2", sMin: "22", sRoi: "24", sRate: "45", sEv: "14",
                sJit: "300", sSeed: "6", sWin: "0"};
  for (const [k, v] of Object.entries(spec)) document.getElementById(k).value = v;
  await runSim();
  await show(RECORDINGS[0]);
  await runAssess();
  const first = document.getElementById("cntAssess").textContent;
  await show(RECORDINGS[1]);
  return {first, second: document.getElementById("cntAssess").textContent};
}"""


def test_the_assessed_state_does_not_follow_you_to_another_recording(page):
    pg, errs = page
    got = pg.evaluate(SWITCH)
    assert not errs, errs
    assert "assessed" in got["first"].lower()
    assert "assessed" not in got["second"].lower(), (
        f"the chip claims the second recording was assessed: {got['second']!r}")


# ------------------------------------------------------- the wording it replaced

def test_the_page_no_longer_says_no_detector_is_involved(page):
    """Checked on the RENDERED page rather than the source: the comment that
    explains why the phrase went necessarily quotes it, and a source grep would
    be caught by its own explanation."""
    pg, _ = page
    shown = pg.evaluate("() => document.body.innerText.toLowerCase()")
    assert "no detector involved" not in shown, (
        "the assessor finds coordinated clusters and returns their times, "
        "participants and spread — that is detection. What it has no part of is "
        "an operating point.")
    assert "no operating point" in shown


def test_the_K_control_says_what_K_counts():
    """It was labelled `mark clusters at K` with the definition two paragraphs
    below, in the fine print, which is not where a reader meets K."""
    html = VIEWER.read_text(encoding="utf-8")
    i = html.index('for="aK"')
    label = html[i:i + 200]
    assert "ROIs" in label, label
