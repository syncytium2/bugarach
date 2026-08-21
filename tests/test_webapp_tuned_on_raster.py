"""The sweep's answer reaches the detector, and the raster says it was tuned.

The tune step produced a number and a sentence containing it. To use that number
you read it off the screen and typed it into the Detect step — across a folder
change, because the sweep runs on a simulation (the only place with an answer
key) and the detector runs on your recordings (where there is none).

A transcribed number is a defect this project has already paid for:
`docs/todo/2026-08-14-generator-doc-numbers-are-transcribed.md`, and a commit
whose subject is *"stop transcribing the endpoints"*.

So the operating point now travels: a button applies it, `TUNED` remembers where
it came from, it survives `open`, and the raster lane says the setting was
**chosen** rather than merely current.

**Why the lane matters more than the panel.** A picture leaves the page — into a
slide, into a figure — and arrives without the panel that explained it. The one
thing it cannot afford to lose is whether the calls on it came from a tuned
instrument or from whatever happened to be in the boxes.

**And the claim has to be droppable.** Edit the control by hand and the
provenance is gone, from the chip and from the lane. A lane that says "tuned"
about a number somebody typed is worse than one that says nothing.
"""

from __future__ import annotations

from pathlib import Path

import pytest

VIEWER = Path(__file__).resolve().parents[1] / "docs/site/raster_viewer.html"

SIM = {"sRec": "4", "sMin": "25", "sRoi": "26", "sRate": "40", "sEv": "16",
       "sJit": "300", "sSeed": "5"}

# A plain folder with no planted truth — what "your own recordings" means here.
REAL = [{"name": "mine.csv",
         "text": "roi,time_sec\n" + "".join(
             f"r{r:02d},{round(60.0 * k + 0.03 * r, 3)}\n"
             for k in range(1, 12) for r in range(1, 15))},
        {"name": "slices.csv", "text": "slice_id,frame_interval_sec\nmine,0.1\n"}]


@pytest.fixture(scope="module")
def page():
    pytest.importorskip("playwright.sync_api",
                        reason="the loop is a property of the running page")
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


SWEEP = """async (sim) => {
  for (const [k, v] of Object.entries(sim)) document.getElementById(k).value = v;
  await runSim();
  document.getElementById("dDet").value = "rate";
  paintDetectorChoice();
  await show(RECORDINGS[0]);
  await runTune();
  const box = document.getElementById("tuneOut");
  const btn = [...box.querySelectorAll("button")]
    .find(b => /use this setting/i.test(b.textContent));
  return {hasButton: !!btn, before: document.getElementById("dThr").value};
}"""

APPLY = """async () => {
  const box = document.getElementById("tuneOut");
  const btn = [...box.querySelectorAll("button")]
    .find(b => /use this setting/i.test(b.textContent));
  btn.click();
  // runDetect is fired inside; wait for it to settle
  for (let i = 0; i < 200 && !(DETECT && DETECT.which === "rate"); i++)
    await new Promise(r => setTimeout(r, 25));
  return {
    control: document.getElementById("dThr").value,
    tuned: TUNED.rate || null,
    chip: document.getElementById("tunedWhat").textContent,
    detected: DETECT ? DETECT.starts.length : null,
    which: DETECT ? DETECT.which : null,
    open: document.getElementById("accDetect").open,
  };
}"""


@pytest.fixture(scope="module")
def applied(page):
    pg, errs = page
    swept = pg.evaluate(SWEEP, SIM)
    assert swept["hasButton"], (
        "the sweep result offers no way to use the setting it just chose")
    got = pg.evaluate(APPLY)
    assert not errs, errs
    got["before"] = swept["before"]
    return got


def test_the_setting_lands_in_the_detectors_own_control(applied):
    assert applied["tuned"], "nothing recorded that a setting was applied"
    assert float(applied["control"]) == pytest.approx(applied["tuned"]["value"]), (
        "the control does not hold the value the sweep chose")


def test_applying_it_runs_the_detector(applied):
    assert applied["which"] == "rate"
    assert applied["detected"] is not None and applied["detected"] >= 0


def test_it_opens_the_step_the_reader_now_has_to_look_at(applied):
    assert applied["open"], (
        "the setting was applied into a panel that is still closed")


def test_the_chip_says_where_the_setting_came_from(applied):
    chip = applied["chip"].lower()
    assert "sweep" in chip and "simulated" in chip, chip
    assert "f1" in chip, "the chip does not carry the score that justified it"


LANE = """() => {
  // the lane label is drawn onto the canvas, so read the string the drawing
  // code builds rather than pixels
  const tu = TUNED[DETECT.which];
  return DETECT.label + " · " + DETECT.starts.length + " called"
    + (tu ? " · " + tu.knobName + " " + fmtKnob(tu.value)
            + (tu.unit ? " " + tu.unit : "") + " tuned" : "");
}"""


def test_the_raster_lane_says_the_setting_was_tuned(page, applied):
    pg, _ = page
    assert "tuned" in pg.evaluate(LANE), (
        "the lane does not distinguish a tuned instrument from whatever was in "
        "the boxes, and a picture leaves the page without its panel")


SURVIVE = """async (files) => {
  await open(files, {quiet: true});
  await show(RECORDINGS[0]);
  const t = TUNED.rate;
  await runDetect();
  return {tuned: t || null, control: document.getElementById("dThr").value,
          truth: TRUTH.size, detected: DETECT ? DETECT.starts.length : null,
          chip: document.getElementById("tunedWhat").textContent};
}"""


def test_the_setting_survives_opening_your_own_folder(page, applied):
    """The whole point. Tune where the answer is known, then open the recordings
    where it is not — a different folder, which replaces the first."""
    pg, errs = page
    got = pg.evaluate(SURVIVE, REAL)
    assert not errs, errs
    assert got["truth"] == 0, "the fixture folder should carry no planted truth"
    assert got["tuned"], "the tuned setting did not survive the folder change"
    assert float(got["control"]) == pytest.approx(applied["tuned"]["value"])
    assert "sweep" in got["chip"].lower(), (
        "the provenance was lost when the folder changed, so the reader can no "
        "longer tell where the setting came from")


EDIT = """async () => {
  const n = document.getElementById("dThr");
  n.value = String(Number(n.value) + 1.5);
  n.dispatchEvent(new Event("input", {bubbles: true}));
  await new Promise(r => setTimeout(r, 50));
  const tu = TUNED[DETECT.which];
  return {tuned: TUNED.rate || null,
          chip: document.getElementById("tunedWhat").textContent,
          lane: DETECT.label + " · " + DETECT.starts.length + " called"
            + (tu ? " · tuned" : "")};
}"""


def test_editing_the_control_by_hand_drops_the_claim(page):
    """A lane that says 'tuned' about a number somebody typed is worse than one
    that says nothing."""
    pg, errs = page
    got = pg.evaluate(EDIT)
    assert not errs, errs
    assert got["tuned"] is None, "a hand-edited setting still claims to be tuned"
    assert got["chip"] == "", f"the chip still claims a sweep: {got['chip']!r}"
    assert "tuned" not in got["lane"], got["lane"]


def test_every_detector_knows_which_control_holds_its_knob():
    """Without this the sweep cannot reach the box it is choosing a value for,
    and a new detector would silently lose the button."""
    html = VIEWER.read_text(encoding="utf-8")
    import re

    knobs = re.findall(r"knob: \{ key: \"(\w+)\", input: \"(\w+)\"", html)
    assert len(knobs) == 6, f"only {len(knobs)} of six detectors name a control"
    for _key, input_id in knobs:
        assert f'id="{input_id}"' in html, f"{input_id} is not a control on the page"
