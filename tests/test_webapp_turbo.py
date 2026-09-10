"""Turbo's marks come from a moving window, and the button that opens turbo works.

Tony, 2026-09-06, tuning turbo on the TTX baselines: *"we lose coordinated events
because of the bin edges shifting. there's clearly events that are present at
1.2 s gone at 1.3 s and come back at 1.4. i think we need a moving bin instead
of bin steps."*

The first turbo counted co-active ROIs on a fixed bin grid — the shipped
assessment's rule, kept there because it is a parity contract with Python. In a
tool whose whole job is to let a person tune a width until the marks match what
they see, a grid is a defect: whether four onsets 0.3 s apart make one event
depended on where the edges fell, so the marks flickered as the width moved.

`turboMarks` asks the question directly — at every instant, how many ROIs have
an onset inside a window of the chosen width — with no step and no grid. These
tests pin what that buys, on hand-built trains where the right answer is known:

* the case Tony saw: an event found at 1.2 s, lost at 1.3 s, found at 1.4 s on
  the grid is found at all three by the window;
* widening never loses an event (a set of onsets that fits in w fits in w');
* K - 1 ROIs never make a mark, however tightly they fire;
* a window closed at both edges: two onsets exactly `width` apart count;
* a busy ROI counts once, however often it fires inside the window;
* the merge knob is in seconds and joins two stretches closer than it.

And one test that presses the real button, because turbo shipped (#484) with
no test pressing it, in a page whose handoff records seven controls that
existed, worked, and could not be reached.

The node half runs the page's own JavaScript — the functions are cut out of the
template by name, not re-implemented here, so a fork between what is tested and
what runs cannot open.
"""
from __future__ import annotations

import json
import re
import shutil
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
TEMPLATE = ROOT / "docs/site/viewer.template.html"
VIEWER = ROOT / "docs/site/raster_viewer.html"

NODE = shutil.which("node")
needs_node = pytest.mark.skipif(NODE is None, reason="turbo's marks are JavaScript; no node on PATH")


def _function_source(name: str) -> str:
    """The named top-level function, cut from the template by brace matching."""
    text = TEMPLATE.read_text(encoding="utf-8")
    m = re.search(rf"^function {re.escape(name)}\(", text, re.M)
    assert m, f"{name} is not in the template"
    i = text.index("{", m.end())
    depth = 0
    for j in range(i, len(text)):
        if text[j] == "{":
            depth += 1
        elif text[j] == "}":
            depth -= 1
            if depth == 0:
                return text[m.start():j + 1]
    raise AssertionError(f"unbalanced braces in {name}")


DRIVER = """
const req = JSON.parse(require('fs').readFileSync(0, 'utf8'));
%s
%s
const out = req.cases.map(c => {
  if (c.op === 'marks') return turboMarks(c.trains, c.width, c.K, c.merge);
  if (c.op === 'grid') {
    const nBins = Math.max(1, Math.ceil(c.dur / c.width));
    const counts = coactCount(c.trains, c.dur, c.width, nBins, null);
    return Array.from(counts).some(x => x >= c.K);
  }
  throw new Error('unknown op ' + c.op);
});
process.stdout.write(JSON.stringify(out));
"""


def _js(cases: list[dict]) -> list:
    driver = DRIVER % (_function_source("turboMarks"), _function_source("coactCount"))
    r = subprocess.run([NODE, "-e", driver], input=json.dumps({"cases": cases}),
                       capture_output=True, text=True)
    assert r.returncode == 0, f"node failed:\n{r.stderr}"
    return json.loads(r.stdout)


def _marks(trains, width, K=3, merge=2.0):
    return _js([{"op": "marks", "trains": trains, "width": width, "K": K, "merge": merge}])[0]


def _grid_finds(trains, width, K=3, dur=60.0):
    return _js([{"op": "grid", "trains": trains, "width": width, "K": K, "dur": dur}])[0]


# Four ROIs, one onset each, 0.1 s apart: one event by any reading, 0.3 s wide.
EVENT = [[10.95], [11.05], [11.15], [11.25]]


@needs_node
def test_the_grid_flickers_with_width_and_the_window_does_not():
    """The defect as reported, reproduced on the grid and absent from the window.

    On a grid the onsets at 10.95 and 11.05 sit either side of an edge at 11.0
    when the width divides 11 — so the event splits, and whether it splits is a
    property of the width's arithmetic, not of the data.
    """
    widths = [1.1, 1.2, 1.3, 1.4, 1.5]
    grid = [_grid_finds(EVENT, w, K=4) for w in widths]
    window = [len(_marks(EVENT, w, K=4)) for w in widths]
    assert window == [1] * len(widths), (widths, window)
    assert not all(grid), (
        "the grid found the event at every width in this range; the case this "
        "test reproduces has moved — pick widths that put an edge inside it")


@needs_node
def test_widening_never_loses_a_mark():
    """Monotone in the width: every mark at w lies inside a mark's span at w' > w."""
    trains = [[3.0, 20.1, 41.0], [3.2, 20.4, 41.3], [3.3, 20.6, 41.9], [8.0, 20.9], [30.0]]
    prev = None
    for w in (0.3, 0.5, 0.8, 1.2, 1.3, 1.4, 2.0, 3.0):
        marks = _marks(trains, w, K=3, merge=0.0)
        if prev is not None:
            for m in prev:
                assert any(x["from"] - 1e-9 <= m["t"] <= x["to"] + 1e-9 for x in marks), (
                    f"a mark at {m['t']:.2f} s found with a {pw} s window is gone at {w} s")
        prev, pw = marks, w


@needs_node
def test_k_minus_one_rois_never_mark():
    assert _marks([[5.0], [5.01], [5.02]], 1.0, K=4) == []
    assert len(_marks([[5.0], [5.01], [5.02]], 1.0, K=3)) == 1


@needs_node
def test_the_window_is_closed_at_both_edges():
    """Two onsets exactly `width` apart are co-active within `width`; a hair
    further apart they are not."""
    assert len(_marks([[5.0], [6.0], [5.5]], 1.0, K=3)) == 1
    assert _marks([[5.0], [6.001], [5.5]], 1.0, K=3) == []


@needs_node
def test_a_busy_roi_counts_once():
    """One ROI firing ten times inside the window is one ROI. GLOSSARY: a count
    of ROIs, never of spikes."""
    busy = [[5.0 + 0.05 * i for i in range(10)], [5.2], [5.3]]
    assert _marks(busy, 1.0, K=3)[0]["peak"] == 3
    assert _marks(busy, 1.0, K=4) == []


@needs_node
def test_the_merge_gap_is_in_seconds():
    """Two events 3 s apart: separate marks under a 2 s merge gap, one mark
    under 4 s. The knob used to be in bins, which meant nothing without the
    width beside it."""
    two = [[10.0, 13.0], [10.1, 13.1], [10.2, 13.2]]
    assert len(_marks(two, 0.5, K=3, merge=2.0)) == 2
    assert len(_marks(two, 0.5, K=3, merge=4.0)) == 1


@needs_node
def test_a_mark_sits_on_its_event():
    (m,) = _marks(EVENT, 1.0, K=4)
    assert 10.95 - 1e-9 <= m["t"] <= 11.25 + 1e-9, m
    assert m["peak"] == 4


# ---------------------------------------------------------------- the button

def test_the_page_says_the_window_moves():
    """The panel's own account of itself must not still say bins."""
    text = VIEWER.read_text(encoding="utf-8")
    assert "MOVING" in text and "no grid" in text
    turbo = text[text.index('id="turbo"'):text.index('id="turboScroll"')]
    assert "bins" not in turbo, "the merge knob still says bins"


def test_pressing_turbo_opens_it_and_a_knob_redraws():
    """The real control, through a real click, on a simulated folder.

    Turbo shipped with no test pressing its button. The handoff behind it lists
    seven defects in this page of the same shape — a thing that existed, worked,
    and could not be reached from where the reader was standing — and a test
    that calls the function is exactly what let them through.
    """
    pytest.importorskip("playwright.sync_api")
    from playwright.sync_api import sync_playwright
    # `sWin: 2` — baseline and drug. Turbo reads each recording's BASELINE window
    # and skips a recording without one, so a folder simulated with no windows
    # gives turbo nothing to show (FOUNDATIONS §9: baseline only).
    sim = {"sRec": "3", "sMin": "20", "sRoi": "24", "sRate": "60", "sEv": "12",
           "sJit": "300", "sSeed": "7", "sWin": "2"}
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
                }""", sim)
            assert pg.is_hidden("#turbo"), "turbo is open before anyone pressed it"
            pg.click("#turboBtn")
            # `TURBO` is a `let`, not a window property, so it is reached by name.
            pg.wait_for_function(
                "() => typeof TURBO !== 'undefined' && TURBO && TURBO.rows.length > 0",
                timeout=20000)
            assert pg.is_visible("#turbo")
            state = pg.evaluate(
                """() => ({rows: TURBO.rows.length,
                           marks: TURBO.rows.reduce((a, r) => a + r.marks.length, 0),
                           note: document.getElementById('turboWhat').textContent,
                           btn: document.getElementById('turboBtn').textContent})""")
            assert state["rows"] == 3, state
            assert state["marks"] > 0, "a simulated folder with planted events shows no marks"
            assert "MOVING" in state["note"], state["note"]
            assert state["btn"] == "Leave turbo"
            # A knob is live: raising K past every field's size empties the marks.
            pg.fill("#tFloor", "50")
            pg.dispatch_event("#tFloor", "input")
            pg.wait_for_function(
                "() => TURBO.rows.every(r => r.K === 50)", timeout=5000)
            assert pg.evaluate(
                "() => TURBO.rows.reduce((a, r) => a + r.marks.length, 0)") == 0
            assert errs == [], errs
        finally:
            browser.close()


# --------------------------------------------------------------------------
# TURBO IS THE FRONT DOOR
#
# Tony, 2026-09-10, opening this page to run MAHICE: the interface is painful
# and makes no sense to him. Turbo — the mode he asked for on 2026-09-06 and
# called the long-term solution — existed, worked, and was a ghost button in
# the fold bar, so the default way in to MAHICE was an eleven-panel rail.
#
# These press nothing. That is the whole point: what is under test is where a
# folder LANDS, and a test that clicks the button cannot see it.
# --------------------------------------------------------------------------

BASELINE_SEC = (0.0, 120.0)


def _folder(tmp: Path, n_rec: int = 3, *, regions: str = "baseline") -> Path:
    """A minimal export folder: onsets that co-fire, and a regions file or not.

    Six ROIs fire together every 20 s inside the baseline, so turbo finds marks
    at any sane K and the count does not depend on the knob defaults.

    `regions` is the case under test, and the three differ in what the PRODUCER
    said rather than in the data:
      "baseline" — a declared baseline window;
      "none"     — no regions.csv at all, so nobody has said anything;
      "treated"  — regions declared, none of them a baseline.
    """
    d = tmp / f"regions_{regions}"
    d.mkdir(parents=True, exist_ok=True)
    for i in range(n_rec):
        rows = ["roi,time_sec"]
        for roi in range(1, 7):
            for k in range(1, 6):
                # 0.05 s apart: one event by any reading, inside any bin width
                rows.append(f"{roi},{k * 20 + roi * 0.05:.2f}")
        (d / f"rec{i}.csv").write_text("\n".join(rows) + "\n", encoding="utf-8")
    (d / "slices.csv").write_text(
        "slice_id,frame_interval_sec\n"
        + "".join(f"rec{i},0.1\n" for i in range(n_rec)), encoding="utf-8")
    if regions == "baseline":
        s, e = BASELINE_SEC
        (d / "regions.csv").write_text(
            "slice_id,region_idx,label,start_sec,end_sec\n"
            + "".join(f"rec{i},0,baseline,{s},{e}\n" for i in range(n_rec)),
            encoding="utf-8")
    elif regions == "treated":
        (d / "regions.csv").write_text(
            "slice_id,region_idx,label,start_sec,end_sec\n"
            + "".join(f"rec{i},0,senktide,0,120\n" for i in range(n_rec)),
            encoding="utf-8")
    return d


def _open(pg, folder: Path):
    """Open a folder the way a person does — the file input, not a function."""
    pg.set_input_files("#files", [str(q) for q in sorted(folder.iterdir())])


def _page(p, tmp):
    try:
        browser = p.chromium.launch()
    except Exception as e:                            # noqa: BLE001
        pytest.skip(f"no chromium available: {type(e).__name__}")
    pg = browser.new_page()
    errs: list[str] = []
    pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.goto(VIEWER.as_uri(), wait_until="load")
    return browser, pg, errs


def test_opening_a_real_folder_lands_in_turbo(tmp_path):
    """No click. Open a folder and you are in turbo, because that is the job."""
    pytest.importorskip("playwright.sync_api")
    from playwright.sync_api import sync_playwright

    with sync_playwright() as p:
        browser, pg, errs = _page(p, tmp_path)
        try:
            _open(pg, _folder(tmp_path))
            pg.wait_for_selector("#turbo:not([hidden])", timeout=30000)
            assert pg.is_hidden("#view"), "the rail's view is still on top of turbo"
            state = pg.evaluate(
                """() => ({rows: TURBO.rows.length,
                           marks: TURBO.rows.reduce((a, r) => a + r.marks.length, 0),
                           btn: document.getElementById('turboBtn').textContent,
                           pressed: document.getElementById('turboBtn')
                                      .getAttribute('aria-pressed')})""")
            assert state["rows"] == 3, state
            assert state["marks"] > 0, "landed in turbo with nothing drawn"
            # The button is the way OUT now, and says so without being pressed.
            assert state["btn"] == "Leave turbo", state
            assert state["pressed"] == "true", state
            assert errs == [], errs
        finally:
            browser.close()


def test_no_regions_declared_uses_the_whole_trace_and_says_so(tmp_path):
    """Tony, 2026-09-10: no baseline defined means use the whole trace — and tell
    the user we did it.

    Before this, such a recording was silently dropped: `baselineWindow`
    returned null and `turboLoad` skipped it, so a folder that declared no
    periods produced an empty turbo and no explanation. The contract already
    said what to do — `export_folder_spec.md` §regions gives an unannotated
    recording one region spanning its own extent.

    The flag is asserted as hard as the behaviour, because a silent assumption
    is the failure this change exists to prevent: a K tuned on a recording that
    is secretly a treated preparation is wrong in a way nothing downstream
    would catch.
    """
    pytest.importorskip("playwright.sync_api")
    from playwright.sync_api import sync_playwright

    with sync_playwright() as p:
        browser, pg, errs = _page(p, tmp_path)
        try:
            _open(pg, _folder(tmp_path, regions="none"))
            pg.wait_for_selector("#turbo:not([hidden])", timeout=30000)
            state = pg.evaluate(
                """() => ({rows: TURBO.rows.length,
                           assumed: TURBO.rows.filter(r => r.assumed).length,
                           marks: TURBO.rows.reduce((a, r) => a + r.marks.length, 0),
                           dur: TURBO.rows[0].dur,
                           flagHidden: document.getElementById('turboFlag').hidden,
                           flag: document.getElementById('turboFlag').textContent})""")
            assert state["rows"] == 3, state
            assert state["assumed"] == 3, "the rows do not know they were assumed"
            assert state["marks"] > 0, "the whole trace produced no marks"
            # The extent is the recording's own last onset: events run to
            # 100 s + roi*0.05, so the span is ~100 s and emphatically not the
            # 120 s window the *other* fixtures declare.
            assert 100.0 <= state["dur"] <= 101.0, state["dur"]

            assert state["flagHidden"] is False, "we assumed and did not say so"
            flag = state["flag"]
            assert "WHOLE TRACE" in flag, flag
            # It has to name WHICH, or the reader cannot go and look.
            for i in range(3):
                assert f"rec{i}" in flag, flag

            # ...and no OTHER part of the page may claim the folder sent
            # windows. `paintWindowPanel` hid its panel and returned early
            # without clearing the chip, so the rail — which reads that node so
            # a step and its panel cannot disagree — kept the previously opened
            # folder's answer. Live on main; it shows up here because a folder
            # declaring nothing now lands in turbo, next to this very flag.
            assert pg.evaluate(
                "() => document.getElementById('cntWindows').textContent"
            ) == "none declared"
            assert errs == [], errs
        finally:
            browser.close()


def test_regions_declared_with_none_a_baseline_are_skipped_and_named(tmp_path):
    """The other half, and it must NOT be assumed.

    A producer who declared their periods and named none a baseline has said
    this recording is treated. Sweeping a senktide period into a baseline is
    FOUNDATIONS §9 in terms — coordination properties are not taken from
    treatments — and `folderAssessWindow` already refuses it. What changes here
    is that the refusal is now stated instead of being an empty column.
    """
    pytest.importorskip("playwright.sync_api")
    from playwright.sync_api import sync_playwright

    with sync_playwright() as p:
        browser, pg, errs = _page(p, tmp_path)
        try:
            _open(pg, _folder(tmp_path, regions="treated"))
            # No rows, so nothing to land in: the page stays on the rail.
            pg.wait_for_function(
                "() => typeof RECORDINGS !== 'undefined' && RECORDINGS.length === 3",
                timeout=30000)
            pg.click("#turboBtn")
            pg.wait_for_function(
                "() => typeof TURBO !== 'undefined' && TURBO !== null",
                timeout=30000)
            state = pg.evaluate(
                """() => ({rows: TURBO.rows.length,
                           skipped: (TURBO.skipped || []).length,
                           flag: document.getElementById('turboFlag').textContent})""")
            assert state["rows"] == 0, "a treated period was drawn as a baseline"
            assert state["skipped"] == 3, state
            assert "none as a baseline" in state["flag"], state["flag"]
            for i in range(3):
                assert f"rec{i}" in state["flag"], state["flag"]
            assert errs == [], errs
        finally:
            browser.close()


def test_leaving_turbo_is_remembered_across_a_reload(tmp_path):
    """Somebody who left turbo is working on the rail and wants it every time.

    The counterpart matters as much: arriving in turbo must NOT write the
    preference, or the first automatic entry would pin the choice forever.
    """
    pytest.importorskip("playwright.sync_api")
    from playwright.sync_api import sync_playwright

    folder = _folder(tmp_path)
    with sync_playwright() as p:
        browser, pg, errs = _page(p, tmp_path)
        try:
            _open(pg, folder)
            pg.wait_for_selector("#turbo:not([hidden])", timeout=30000)
            # Arriving is not a preference: nothing is stored yet.
            assert pg.evaluate(
                "() => localStorage.getItem('bugarach.turbofront')") is None

            pg.click("#turboBtn")                     # leave, deliberately
            pg.wait_for_selector("#view:not([hidden])", timeout=10000)
            assert pg.evaluate(
                "() => localStorage.getItem('bugarach.turbofront')") == "off"

            pg.reload(wait_until="load")
            _open(pg, folder)
            pg.wait_for_selector("#view:not([hidden])", timeout=30000)
            assert pg.is_hidden("#turbo"), "a declined front door reopened itself"

            # And going back in clears the departure rather than storing a second
            # flavour of it — the key records only a departure.
            pg.click("#turboBtn")
            pg.wait_for_selector("#turbo:not([hidden])", timeout=20000)
            assert pg.evaluate(
                "() => localStorage.getItem('bugarach.turbofront')") is None
            assert errs == [], errs
        finally:
            browser.close()


def test_a_second_folder_does_not_show_the_first_ones_rows(tmp_path):
    """`turboLoad` only ran when `TURBO` was null, and opening a folder never
    cleared it — so the second folder opened showing the FIRST one's baselines.

    Latent while turbo was a button somebody pressed once. A defect the moment
    opening a folder is what puts you there.
    """
    pytest.importorskip("playwright.sync_api")
    from playwright.sync_api import sync_playwright

    three = _folder(tmp_path / "a", n_rec=3)
    five = _folder(tmp_path / "b", n_rec=5)
    with sync_playwright() as p:
        browser, pg, errs = _page(p, tmp_path)
        try:
            _open(pg, three)
            pg.wait_for_selector("#turbo:not([hidden])", timeout=30000)
            assert pg.evaluate("() => TURBO.rows.length") == 3

            _open(pg, five)
            pg.wait_for_function(
                "() => TURBO && TURBO.rows.length === 5", timeout=30000)
            ids = pg.evaluate("() => TURBO.rows.map(r => r.id).sort()")
            assert ids == [f"rec{i}" for i in range(5)], ids
            assert errs == [], errs
        finally:
            browser.close()


# --------------------------------------------------------------------------
# DESIGNATION BEATS DETECTION
#
# Tony, 2026-09-10: "can we use whatever the user provides as baseline. maybe
# they call it control, or 'pre'". Both of those were already in
# BASELINE_TOKENS; a name that is not (`vehicle`, `naive`, `ctrl`) had no way
# in at all and the folder walk skipped the recording. His call was that
# designation wins and the token list is only the opening guess — which is also
# what this page already says about itself: the baseline is DESIGNATED, not
# detected, and a fourth guessing rule would be the worst of them.
# --------------------------------------------------------------------------


def _two_period_folder(tmp: Path, base_label: str, n_rec: int = 3) -> Path:
    """Two declared periods: an untreated one under `base_label`, then a drug.

    The events differ per period on purpose — co-firing in the first, quiet in
    the second — so a test can tell WHICH period was measured rather than only
    that something was.
    """
    d = tmp / f"two_period_{base_label}"
    d.mkdir(parents=True, exist_ok=True)
    for i in range(n_rec):
        rows = ["roi,time_sec"]
        for roi in range(1, 7):
            for k in range(1, 6):                      # co-fire inside 0..120
                rows.append(f"{roi},{k * 20 + roi * 0.05:.2f}")
            rows.append(f"{roi},{200 + roi * 9}")      # sparse inside 120..300
        (d / f"rec{i}.csv").write_text("\n".join(rows) + "\n", encoding="utf-8")
    (d / "slices.csv").write_text(
        "slice_id,frame_interval_sec\n"
        + "".join(f"rec{i},0.1\n" for i in range(n_rec)), encoding="utf-8")
    (d / "regions.csv").write_text(
        "slice_id,region_idx,label,start_sec,end_sec\n"
        + "".join(f"rec{i},1,{base_label},0,120\nrec{i},2,senktide,120,300\n"
                  for i in range(n_rec)), encoding="utf-8")
    return d


def test_a_label_off_the_list_is_refused_then_designated(tmp_path):
    """`vehicle` is untreated and no built-in token knows the word.

    Refused first — which is correct, because nothing has told the page that
    `vehicle` is not a drug — and then measured once the reader says so, on THE
    DESIGNATED PERIOD rather than on the whole recording. The window is the
    assertion that matters: sweeping in the senktide half would be the
    FOUNDATIONS §9 error wearing a fix's clothes.
    """
    pytest.importorskip("playwright.sync_api")
    from playwright.sync_api import sync_playwright

    with sync_playwright() as p:
        browser, pg, errs = _page(p, tmp_path)
        try:
            _open(pg, _two_period_folder(tmp_path, "vehicle"))
            pg.wait_for_function(
                "() => typeof RECORDINGS !== 'undefined' && RECORDINGS.length === 3",
                timeout=30000)
            pg.click("#turboBtn")
            pg.wait_for_function(
                "() => typeof TURBO !== 'undefined' && TURBO !== null",
                timeout=30000)
            assert pg.evaluate("() => TURBO.rows.length") == 0
            assert pg.evaluate("() => TURBO.skipped.length") == 3
            # The refusal offers what the folder actually calls its periods —
            # the reader cannot designate a name nobody has shown them.
            offered = pg.evaluate(
                "() => [...document.querySelectorAll('button.designate')]"
                ".map(b => b.textContent).sort()")
            assert offered == ["senktide", "vehicle"], offered
            # ...and the empty state does not print a settings sentence about
            # nothing: Math.min of no rows is Infinity.
            assert "Infinity" not in pg.evaluate(
                "() => document.getElementById('turboWhat').textContent")

            pg.click("button.designate:has-text('vehicle')")
            pg.wait_for_function("() => TURBO && TURBO.rows.length === 3",
                                 timeout=30000)
            state = pg.evaluate(
                """() => ({dur: TURBO.rows[0].dur,
                           marks: TURBO.rows.reduce((a, r) => a + r.marks.length, 0),
                           assumed: TURBO.rows.filter(r => r.assumed).length})""")
            # 0..120 — the vehicle period, NOT 0..300 and not the whole trace.
            assert 119.0 <= state["dur"] <= 121.0, state
            assert state["marks"] > 0, state
            assert state["assumed"] == 0, "a designated window is not an assumption"
            assert errs == [], errs
        finally:
            browser.close()


def test_designating_replaces_the_guess_rather_than_joining_it(tmp_path):
    """A folder with BOTH a designated name and one the built-in list knows.

    `pre-wash` matches the token `pre`. Designating `vehicle` has to mean
    vehicle — if the guess kept running alongside, the longest match would win
    and the page would measure the wrong period while reporting a designation.
    """
    pytest.importorskip("playwright.sync_api")
    from playwright.sync_api import sync_playwright

    d = tmp_path / "both"
    d.mkdir(parents=True, exist_ok=True)
    for i in range(2):
        rows = ["roi,time_sec"]
        for roi in range(1, 7):
            for k in range(1, 6):
                rows.append(f"{roi},{k * 20 + roi * 0.05:.2f}")   # in vehicle
            rows.append(f"{roi},{400 + roi * 9}")                 # in pre-wash
        (d / f"rec{i}.csv").write_text("\n".join(rows) + "\n", encoding="utf-8")
    (d / "slices.csv").write_text(
        "slice_id,frame_interval_sec\nrec0,0.1\nrec1,0.1\n", encoding="utf-8")
    # pre-wash is the LONGER period, so "longest baseline wins" would take it.
    (d / "regions.csv").write_text(
        "slice_id,region_idx,label,start_sec,end_sec\n"
        + "".join(f"rec{i},1,vehicle,0,120\nrec{i},2,pre-wash,120,600\n"
                  for i in range(2)), encoding="utf-8")

    with sync_playwright() as p:
        browser, pg, errs = _page(p, tmp_path)
        try:
            _open(pg, d)
            # `pre-wash` matches out of the box, so this folder is NOT refused —
            # it lands in turbo measuring the wrong period.
            pg.wait_for_selector("#turbo:not([hidden])", timeout=30000)
            assert 479.0 <= pg.evaluate("() => TURBO.rows[0].dur") <= 481.0

            pg.evaluate("() => designateBaseline(['vehicle'])")
            pg.wait_for_function(
                "() => TURBO && TURBO.rows.length === 2 && TURBO.rows[0].dur < 200",
                timeout=30000)
            assert 119.0 <= pg.evaluate("() => TURBO.rows[0].dur") <= 121.0
            assert errs == [], errs
        finally:
            browser.close()
