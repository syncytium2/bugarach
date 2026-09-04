"""Setting K in the page that MAHICE happens in, and the file it writes.

The verdicts were already recorded here; what was not was **the thing the person
is there to decide**. Tony, 2026-09-03: *"K is set by the user during review of
the data with MAHICE"* — and *"the human might want different K for a session,
but it is not fair to change K for each slice. We do need K expressed as a
percentage."*

Three properties, and none is visible by reading the panel:

* the page resolves a percentage **the same way the generator does** — a second
  rounding convention would put a spec derived at 10% out of step with a
  simulation planted at 10%, and nothing downstream compares the two;
* `mahice.json` written here satisfies `annotate.MahiceSession`, which is the
  only thing stopping two halves in two languages drifting apart;
* the cross-check **reports and never overrides**, because the person looked at
  the recordings and the arithmetic did not.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from bugarach.annotate import MAHICE, MahiceSession, read_session
from bugarach.assess import k_from_fraction

VIEWER = Path(__file__).resolve().parents[1] / "docs/site/raster_viewer.html"

#: Dense enough that the assessment finds candidates to judge.
SIM = {"sRec": "2", "sMin": "25", "sRoi": "24", "sRate": "60", "sEv": "16",
       "sJit": "300", "sSeed": "11", "sWin": "0"}


@pytest.fixture(scope="module")
def page():
    pytest.importorskip("playwright.sync_api",
                        reason="setting K is a property of the page")
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
            pg.evaluate(
                """async (sim) => {
                  for (const [k, v] of Object.entries(sim))
                    document.getElementById(k).value = v;
                  await runSim();
                  await show(RECORDINGS[0]);
                  await runAssess();
                }""", SIM)
            yield pg, errs
        finally:
            browser.close()


def _judge(pg, n=60):
    """Start a review and cast alternating verdicts, so both sides are stocked.

    The per-recording cap is lifted first: it defaults to 8 and exists so one
    busy slice cannot speak for a folder, but this fixture has a single
    recording and 8 verdicts is below the floor the cross-check needs.
    """
    return pg.evaluate(
        """(n) => {
          document.getElementById("anWho").value = "tony";
          document.getElementById("anCap").value = "50";
          document.getElementById("anBudget").value = "400";
          startAnnotation();
          for (let i = 0; i < n && ANNOT.i < ANNOT.cands.length; i++)
            recordVerdict(i % 3 === 0 ? "rejected" : "confirmed");
          return ANNOT.verdicts.filter(Boolean).length;
        }""", n)


# ---------------------------------------------------------------------------
# the conversion agrees with the generator's
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("frac", [0.05, 0.1, 0.15, 0.2, 0.25, 0.33, 1.0])
@pytest.mark.parametrize("n_roi", [1, 7, 10, 12, 24, 34, 51, 405])
def test_the_page_resolves_a_percentage_the_way_the_generator_does(
        page, frac, n_roi):
    """`simulate.py` plants participation with `max(1, matlab_round(f*n))` and
    `assess.k_from_fraction` reuses it. If the page rounds differently, a spec
    derived at 10% stops describing a simulation planted at 10%."""
    pg, _ = page
    got = pg.evaluate("([f, n]) => kFromFraction(f, n)", [frac, n_roi])
    assert got == k_from_fraction(frac, n_roi)


def test_the_same_percentage_is_a_different_count_per_recording(page):
    """The whole reason K is a percentage."""
    pg, _ = page
    got = pg.evaluate("(n) => n.map(x => kFromFraction(0.10, x))",
                      [10, 34, 51, 405])
    assert got == [1, 3, 5, 41]


# ---------------------------------------------------------------------------
# the file the Python has to read
# ---------------------------------------------------------------------------

def test_the_page_writes_a_session_the_python_accepts(page, tmp_path):
    """The guard that matters most: two halves, two languages, one record."""
    pg, errs = page
    assert _judge(pg) >= 20
    text = pg.evaluate(
        """() => {
          document.getElementById("anKPct").value = "15";
          document.getElementById("anKNote").value = "read off the 15% row";
          setK();
          return mahiceJson();
        }""")
    assert text, "the page produced no mahice.json"
    p = tmp_path / "mahice.json"
    p.write_text(text)

    s = read_session(p)                       # the Python's own reader
    assert isinstance(s, MahiceSession)
    assert s.k_percent == pytest.approx(0.15)
    assert s.annotator == "tony"
    assert s.decided_at.endswith("Z")
    assert s.note == "read off the 15% row"
    assert s.k_absolute and s.n_roi
    # and every resolved count agrees with the Python's own conversion
    for sid, n in s.n_roi.items():
        assert s.k_absolute[sid] == k_from_fraction(0.15, n)
    assert json.loads(text)["mahice"] == MAHICE
    assert not errs, errs


def test_a_percentage_out_of_range_is_refused_before_it_reaches_the_file(page):
    """The dataclass refuses `k_percent=20`; the page must not get that far —
    a whole number would set K to a fifth of nothing or to the whole field."""
    pg, _ = page
    for bad in ("0", "-5", "101"):
        state = pg.evaluate(
            """(v) => {
              MAHICE = null;
              document.getElementById("anKPct").value = v;
              setK();
              return {set: MAHICE !== null,
                      said: document.getElementById("anKOut").textContent};
            }""", bad)
        assert not state["set"], f"{bad} was accepted"
        assert "percentage" in state["said"]


def test_no_k_set_means_no_file(page):
    pg, _ = page
    assert pg.evaluate("() => { MAHICE = null; return mahiceJson(); }") == ""


# ---------------------------------------------------------------------------
# the cross-check reports and never overrides
# ---------------------------------------------------------------------------

def test_the_setting_stands_when_the_labels_disagree(page):
    """The person looked at the recordings; this arithmetic did not."""
    pg, _ = page
    _judge(pg)
    out = pg.evaluate(
        """() => {
          document.getElementById("anKPct").value = "90";
          setK();
          return {pct: MAHICE.kPercent,
                  said: document.getElementById("anKOut").textContent,
                  json: JSON.parse(mahiceJson()).k_percent};
        }""")
    assert out["pct"] == pytest.approx(0.90)
    assert out["json"] == pytest.approx(0.90), "the cross-check rewrote K"
    assert ("NOTHING HAS BEEN CHANGED" in out["said"]
            or "Not cross-checked" in out["said"])


def test_a_censored_proposal_list_is_named_rather_than_answered(page):
    """The trap. The page proposes at K>=3, so its own labels cannot speak about
    a smaller K — and it says so instead of returning the floor as the answer."""
    pg, _ = page
    _judge(pg)
    sep = pg.evaluate(
        "() => labelSeparation(ANNOT.verdicts.filter(Boolean))")
    if not sep["ok"]:
        assert any(w in sep["why"] for w in
                   ("proposed at", "judged", "each side", "separates"))
    else:
        assert sep["band"][0] <= sep["k"] <= sep["band"][1]


def test_setting_k_needs_an_assessment_to_resolve_against(page):
    """A percentage with no ROI population is not a floor, and the page says so
    rather than writing a file with an empty map in it."""
    pg, _ = page
    said = pg.evaluate(
        """() => {
          const fa = FOLDER_ASSESS, la = LAST_ASSESS;
          FOLDER_ASSESS = null; LAST_ASSESS = null; MAHICE = null;
          document.getElementById("anKPct").value = "10";
          setK();
          const out = document.getElementById("anKOut").textContent;
          FOLDER_ASSESS = fa; LAST_ASSESS = la;
          return {said: out, set: MAHICE !== null};
        }""")
    assert not said["set"]
    assert "ROI population" in said["said"]


# ---------------------------------------------------------------------------
# the seam between the two halves
# ---------------------------------------------------------------------------

def test_the_judging_step_opens_once_an_assessment_lands(page):
    """MAHICE shipped with both halves working and nothing joining them.

    `assessRun` and `assessFolderRun` each left their candidates in a global and
    then never told the judging step they had arrived, so `#cntAnnot` stayed at
    "assess first" and **`#anStart` stayed `disabled` for the whole session**.
    Clicking "Draw a sample and start" did nothing, silently: a disabled button
    fires no event, raises nothing, and logs nothing.

    Every other test in this file reaches past that button and calls
    `startAnnotation()` in JS, which is why the suite was green while the step
    was unreachable. Tony hit it on the real folder on 2026-09-04 and reported
    it as "clicked. nothing happened", three separate controls over.

    So this asserts **what a person actually has**: an enabled control.
    """
    pg, _ = page
    assert pg.evaluate("collectCandidates().length") > 0, (
        "the fixture must leave candidates or this test proves nothing")
    assert "assess first" not in pg.inner_text("#cntAnnot")
    assert pg.is_enabled("#anStart"), (
        "the assessment ran and left candidates, and the judging step is still "
        "shut — this is the defect, not a flake")


def test_clicking_the_button_actually_starts_a_review(page):
    """One step past enablement: the click has to reach the loop.

    Enabled-but-inert is the same experience as disabled, and only pressing the
    control the way a person does can tell those two apart.
    """
    pg, _ = page
    state = pg.evaluate(
        """() => {
          const keep = ANNOT;
          ANNOT = null;
          document.getElementById("anWho").value = "tony";
          document.getElementById("anStart").click();
          const started = !!(ANNOT && ANNOT.cands && ANNOT.cands.length);
          ANNOT = keep;
          return {started, shown: !!document.getElementById("anCv")};
        }""")
    assert state["started"], "the button is enabled but the click reaches nothing"
    assert state["shown"], "a review started with no canvas to judge in"


# ---------------------------------------------------------------------------
# the judging lane on the raster
# ---------------------------------------------------------------------------

def test_candidates_are_marked_above_the_raster_and_never_on_it(page):
    """Tony asked for the assessor to flag candidates in the raster and for the
    marks to be selectable. Nothing is ever drawn ON the raster, so they go in a
    lane ABOVE it, pointing down at it.

    That rule is the measurement, not decoration: in a raster a vertical mark
    reads as many ROIs firing at once, which is the exact claim being judged. A
    candidate marker through the rows would put a synthetic coordinated event
    into the picture used to decide whether the real one is there.

    So this asserts geometry — every hit box sits ABOVE the top of the frame it
    describes.
    """
    pg, _ = page
    geom = pg.evaluate(
        """() => {
          document.getElementById("anWho").value = "tony";
          document.getElementById("anCap").value = "50";
          document.getElementById("anBudget").value = "400";
          startAnnotation();
          draw(current, current.loaded);
          return {hits: CAND_HITS.map(h => ({y: h.y, top: h.panelTop,
                                             stream: h.stream})),
                  n: CAND_HITS.length,
                  streams: [...new Set(CAND_HITS.map(h => h.stream))]};
        }""")
    assert geom["n"] > 0, "a sample was drawn and nothing was marked"
    # each mark against ITS OWN frame: with two streams there are two panels,
    # and a mark above the first frame can still be sitting on the second.
    for h in geom["hits"]:
        assert h["y"] < h["top"], (
            f"a candidate mark on {h['stream']} landed at y={h['y']}, at or "
            f"below its frame top {h['top']} — that is drawing on the raster")


def test_clicking_a_mark_selects_that_candidate(page):
    """The interaction Tony described: pick a mark, then say yes or no.

    A click selects; it never votes. And a click that hits nothing must do
    nothing — an accidental jump silently re-points every following keystroke at
    a different candidate.
    """
    pg, _ = page
    out = pg.evaluate(
        """() => {
          document.getElementById("anWho").value = "tony";
          document.getElementById("anCap").value = "50";
          document.getElementById("anBudget").value = "400";
          startAnnotation();
          draw(current, current.loaded);
          if (CAND_HITS.length < 2) return {skip: true};
          const cv = document.getElementById("cv");
          const r = cv.getBoundingClientRect();
          const target = CAND_HITS[CAND_HITS.length - 1];
          const before = ANNOT.i;
          cv.dispatchEvent(new MouseEvent("click", {
            clientX: r.left + target.x, clientY: r.top + target.y,
            bubbles: true}));
          const afterHit = ANNOT.i;
          const votesAfterHit = ANNOT.verdicts.filter(Boolean).length;
          cv.dispatchEvent(new MouseEvent("click", {
            clientX: r.left + target.x, clientY: r.top + target.y + 400,
            bubbles: true}));
          return {skip: false, before, afterHit, wanted: target.i,
                  afterMiss: ANNOT.i, votesAfterHit};
        }""")
    if out.get("skip"):
        pytest.skip("fixture drew fewer than two candidates")
    assert out["afterHit"] == out["wanted"], "the click selected the wrong candidate"
    assert out["votesAfterHit"] == 0, "selecting a mark cast a verdict"
    assert out["afterMiss"] == out["afterHit"], "a click on empty canvas moved the review"


def test_the_verdict_is_the_colour_not_the_shape(page):
    """Down is already spoken for, so shape cannot also encode what a mark is.

    Confirmed and rejected are the same triangle and differ only in ink, which
    means the lane has to report a state per mark that the painter turns into a
    colour. This checks the state actually changes when a verdict lands.
    """
    pg, _ = page
    states = pg.evaluate(
        """() => {
          document.getElementById("anWho").value = "tony";
          document.getElementById("anCap").value = "50";
          document.getElementById("anBudget").value = "400";
          startAnnotation();
          const stream = ANNOT.cands[0].stream, rec = ANNOT.cands[0].recId;
          const before = candidatesOnPanel(rec, stream).map(m => m.state);
          recordVerdict("confirmed");
          recordVerdict("rejected");
          const after = candidatesOnPanel(rec, stream).map(m => m.state);
          return {before, after, inks: Object.keys(CAND_INK)};
        }""")
    assert set(states["before"]) == {"unjudged"}
    assert "confirmed" in states["after"] and "rejected" in states["after"]
    for state in ("unjudged", "confirmed", "rejected", "unsure"):
        assert state in states["inks"], f"no ink defined for {state}"
