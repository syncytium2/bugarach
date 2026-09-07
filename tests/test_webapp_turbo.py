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
