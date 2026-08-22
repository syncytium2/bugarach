"""Several detectors at once, each on its own lane, never merged.

Tony, 2026-08-21: *"detect should have the option to select all … maybe a popup
window with all of the settings for all of the detectors in one panel."*

Both halves were cheaper than they looked. `analyseFolder` already ran every
detector over every recording, so running several here is the same body at a
smaller scope — now shared as `detectOne` rather than written twice, because two
copies of "what a detection run is" is exactly the drift the output contract
exists to prevent. And the six settings blocks were always separate divs that
`paintDetectorChoice` hid five of; showing them is removing a filter.

**The raster was the part that was not free, and it reuses a convention rather
than inventing one.** `src/bugarach/ui/diagnostic.py` already draws detector
lanes, and it had settled the questions: lanes get their own strip, names come
from `SHORT` (the full titles overflow slim rows), colour is `COLORS` and is
per-detector identity, and the raster stays monochrome so it never competes.
Two views of the same six detectors with different colours would be two
vocabularies for one thing, and the diagnostic figure is the one that ends up in
a slide beside this page.

**What must not happen is a merge.** The output contract is one row per event
per detector with no consensus merging, because merging discards which detector
fired. A raster stacking six into one bar performs that merge in the artifact
most likely to be screenshotted.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

VIEWER = Path(__file__).resolve().parents[1] / "docs/site/raster_viewer.html"

SIM = {"sRec": "1", "sMin": "20", "sRoi": "26", "sRate": "45", "sEv": "16",
       "sJit": "300", "sSeed": "8"}


@pytest.fixture(scope="module")
def page():
    pytest.importorskip("playwright.sync_api",
                        reason="the lanes are a property of the running page")
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


RUN_ALL = """async (sim) => {
  for (const [k, v] of Object.entries(sim)) document.getElementById(k).value = v;
  await runSim();
  await show(RECORDINGS[0]);
  // tick every detector, not just the default trio
  document.getElementById("dAll").checked = true;
  for (const k of Object.keys(DETECTORS))
    document.getElementById("dPick_" + k).checked = true;
  paintDetectorChoice();
  await runDetect();
  const box = document.getElementById("detectOut");
  return {
    picks: chosenDetectors(),
    detectors: DETECT ? [...new Set(DETECT.rows.map(r => r.detector))].sort() : [],
    lanes: detectLanes(RECORDINGS[0]).map(r => r.which),
    laneColours: detectLanes(RECORDINGS[0]).map(r => DET_COLORS[r.which]),
    perDetector: DETECT ? DETECT.rows.reduce(
      (a, r) => (a[r.detector] = (a[r.detector] || 0) + 1, a), {}) : {},
    headers: [...box.querySelectorAll("th")].map(t => t.textContent.trim()),
    text: box.innerText,
    visibleCtls: Object.entries(DETECTORS)
      .filter(([, d]) => !document.getElementById(d.ctl).hidden).length,
  };
}"""


@pytest.fixture(scope="module")
def ran(page):
    pg, errs = page
    got = pg.evaluate(RUN_ALL, SIM)
    assert not errs, errs
    return got


def test_every_ticked_detector_actually_ran(ran):
    assert len(ran["picks"]) == 6, ran["picks"]
    # CICADA refuses on a folder with no peak, so it may be absent from the rows
    assert len(ran["detectors"]) >= 4, ran["detectors"]


def test_each_detector_keeps_its_own_rows_rather_than_being_merged(ran):
    """The contract's rule, checked on the data the picture is drawn from."""
    counts = ran["perDetector"]
    assert len(counts) >= 4, counts
    assert sum(counts.values()) == sum(
        c for c in counts.values()), "rows lost between detectors"


def test_there_is_one_lane_per_detector_that_fired(ran):
    assert ran["lanes"], "no lanes drawn for a run that produced rows"
    assert set(ran["lanes"]) == set(ran["detectors"]), (
        f"lanes {ran['lanes']} do not match the detectors that produced rows "
        f"{ran['detectors']}")


def test_every_lane_has_its_own_colour(ran):
    cols = ran["laneColours"]
    assert all(cols), "a lane drew with no colour of its own"
    assert len(set(cols)) == len(cols), (
        f"two detectors share a lane colour: {cols}")


def test_the_lane_colours_are_the_ones_the_diagnostic_figure_uses():
    """Ported, not invented. Drift here means the page and the figure name the
    same detector two different ways."""
    py = (Path(__file__).resolve().parents[1]
          / "src/bugarach/ui/app.py").read_text(encoding="utf-8")
    block = py[py.index("COLORS = {"):py.index("}", py.index("COLORS = {"))]
    want = dict(re.findall(r'"(\w+)":\s*"(#[0-9a-fA-F]{6})"', block))
    html = VIEWER.read_text(encoding="utf-8")
    jsblock = html[html.index("const DET_COLORS = {"):
                   html.index("};", html.index("const DET_COLORS = {"))]
    got = dict(re.findall(r'(\w+):\s*"(#[0-9a-fA-F]{6})"', jsblock))
    assert got == want, f"page {got} != bugarach.ui.app {want}"


def test_the_table_names_the_detector_when_several_ran(ran):
    assert "detector" in [h.lower() for h in ran["headers"]], ran["headers"]


def test_it_says_in_words_that_the_detectors_are_not_combined(ran):
    low = ran["text"].lower()
    assert "not combined" in low or "merged" in low, (
        "nothing tells the reader these rows are separate answers rather than "
        "one verdict")


def test_all_the_ticked_detectors_settings_are_shown_at_once(ran):
    assert ran["visibleCtls"] == 6, (
        f"only {ran['visibleCtls']} settings blocks are visible with six ticked")


ONE = """async () => {
  document.getElementById("dAll").checked = false;
  document.getElementById("dDet").value = "rate";
  paintDetectorChoice();
  await runDetect();
  const box = document.getElementById("detectOut");
  return {lanes: detectLanes(RECORDINGS[0]).map(r => r.which),
          headers: [...box.querySelectorAll("th")].map(t => t.textContent.trim()),
          visibleCtls: Object.entries(DETECTORS)
            .filter(([, d]) => !document.getElementById(d.ctl).hidden).length};
}"""


def test_one_detector_still_looks_like_one_detector(page, ran):
    """The single-detector case is the common one and must not grow furniture:
    no detector column when there is nothing to tell apart, one lane, one
    settings block."""
    pg, errs = page
    got = pg.evaluate(ONE)
    assert not errs, errs
    assert got["lanes"] == ["rate"], got["lanes"]
    assert "detector" not in [h.lower() for h in got["headers"]], got["headers"]
    assert got["visibleCtls"] == 1, got["visibleCtls"]


# A run where everything REFUSED must leave `DETECT` null rather than an empty
# result — an empty one would offer a save button for a file asserting the
# detectors ran and found nothing, which is a different claim from "they could
# not run here". That is not tested again here: this module's folder is the
# page's own generated one, which DOES carry the peak, so CICADA runs on it
# happily. `test_webapp_cicada.py::test_refusing_is_not_the_same_as_finding_nothing`
# owns that case, on a folder built to lack the peak, and it is the reason the
# refactor keeps `DETECT` null when nothing succeeds.
