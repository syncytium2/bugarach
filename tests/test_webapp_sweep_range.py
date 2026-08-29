"""The sweep told the reader to widen the range and the page had no range.

Tony, 2026-08-27, tuning locust: *"on the tune settings page, there's no way to
extend the sweep. i tried to optimize locust, the f1 plot says extend the sweep.
i don't see how. there's only match tolerance."*

He was right. ``pickOperatingPoint`` refuses a best value at the end of the grid
— that refusal exists because a boundary value once got published upstream as a
calibrated setting — and it ends "widen the range before calling any of these a
setting". The range was six array literals in the ``DETECTORS`` registry. The
Tune panel's only input was the match tolerance. The only reader who could act
on that sentence was one editing the page's source.

So these tests hold two things at once, and the second is the one that could go
wrong quietly:

* the range CAN be moved — from the boxes, and from the button the refusal now
  offers — and moving it reaches settings the shipped grid could not; and
* an untouched panel sweeps the grid this page has always swept, **the same
  array, not a regeneration of it**. The shipped grids are unevenly spaced on
  purpose (locust's 90/95/98/99/99.5/99.9 crowds the tail), so regenerating one
  from its own endpoints would silently move settings this project has already
  fitted and published against.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from conftest import locust_suppressed_in_the_browser

SUPPRESSED = (
    "locust is suppressed in this build; the behaviour below is still implemented and these come back with it (conftest.locust_suppressed_in_the_browser)")


VIEWER = Path(__file__).resolve().parents[1] / "docs/site/raster_viewer.html"

# The detectors the page can actually run, and so the ones with a range row.
# `sync` is in the registry carrying `unavailable`; nothing on the page ticks it.
RUNNABLE = ["rate", "loco", "coact", "sce", "cicada"]


@pytest.fixture(scope="module")
def page():
    pytest.importorskip("playwright.sync_api",
                        reason="the range boxes are a property of the running page")
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
            assert not errs, f"the page threw on load: {errs}"
            yield pg
        finally:
            browser.close()


def _reset(pg, tick=RUNNABLE):
    """Back to the shipped ranges, with `tick` ticked.

    locust is not ticked by default — it and LoCo are ~97% of a six-detector
    sweep's wall clock — so a test about locust's range has to ask for its row.
    """
    pg.evaluate("""(tick) => {
      for (const k of Object.keys(SWEEP_RANGE)) delete SWEEP_RANGE[k];
      for (const k of Object.keys(DETECTORS)) {
        const b = document.getElementById("tPick_" + k);
        if (b && !b.disabled) b.checked = tick.includes(k);
      }
      paintRanges();
    }""", list(tick))


# --------------------------------------------------------------------------
# the boxes exist, and start on the range the page ships with


def test_every_swept_detector_has_a_range_row(page):
    _reset(page)
    missing = page.evaluate(
        """(names) => names.filter(k =>
             !document.getElementById("tRange_" + k + "_from")
             || !document.getElementById("tRange_" + k + "_to")
             || !document.getElementById("tRange_" + k + "_n"))""",
        RUNNABLE)
    ticked = page.evaluate("() => sweptDetectors()")
    assert set(ticked) <= set(RUNNABLE)
    # Only ticked detectors get a row — the rows are built from the tick list.
    assert [k for k in ticked if k in missing] == [], (
        f"ticked detectors with no range boxes: {missing}. The panel offered "
        f"match tolerance and nothing else, which is the defect this file is "
        f"about.")


def test_the_boxes_start_on_the_grid_the_page_ships_with(page):
    _reset(page)
    got = page.evaluate(
        """() => sweptDetectors().map(k => {
             const g = DETECTORS[k].knob.grid;
             return { k,
               from: Number(document.getElementById("tRange_" + k + "_from").value),
               to: Number(document.getElementById("tRange_" + k + "_to").value),
               n: Number(document.getElementById("tRange_" + k + "_n").value),
               want: [g[0], g[g.length - 1], g.length] };
           })""")
    assert got, "no detector is ticked, so this checked nothing"
    for r in got:
        assert [r["from"], r["to"], r["n"]] == r["want"], r


def test_from_and_to_are_the_ends_of_the_sweep_not_the_smaller_and_larger(page):
    """CoactDetect's grid runs 1e-2 DOWN to 1e-7, loosest alpha first; every
    other detector's runs upward. A panel that sorted them would describe a
    sweep that detector has never run — and, worse, would count the shipped
    range as an edit the moment anything touched the row."""
    _reset(page)
    lo = page.evaluate(
        "() => Number(document.getElementById('tRange_coact_from').value)")
    hi = page.evaluate(
        "() => Number(document.getElementById('tRange_coact_to').value)")
    assert lo > hi, (lo, hi)
    assert page.evaluate("() => rangeEdited('coact')") is False
    # And a regenerated grid keeps that direction.
    _set_range(page, "coact", 1e-2, 1e-8, 4)
    grid = page.evaluate("() => sweepGrid('coact')")
    assert grid == sorted(grid, reverse=True), grid
    _reset(page)


def test_an_untouched_panel_sweeps_the_shipped_array_itself(page):
    """Not an equal-looking regeneration — the array.

    This is the test that protects every operating point already fitted on this
    page. The shipped grids are uneven; a range control that regenerated them
    from their endpoints would move the middle of every one of them, and the
    only symptom would be numbers that no longer reproduce.
    """
    _reset(page)
    same = page.evaluate(
        """(names) => names.map(k => ({
             k, identical: sweepGrid(k) === DETECTORS[k].knob.grid }))""",
        RUNNABLE)
    for r in same:
        assert r["identical"], (
            f"{r['k']}: an untouched panel handed the sweep a rebuilt grid "
            f"rather than the registry's own array")


# --------------------------------------------------------------------------
# moving them


def _set_range(pg, which, frm, to, n):
    pg.evaluate(
        """([k, frm, to, n]) => {
          const set = (part, v) => {
            const el = document.getElementById("tRange_" + k + "_" + part);
            el.value = String(v);
            el.dispatchEvent(new Event("input", { bubbles: true }));
          };
          set("from", frm); set("to", to); set("n", n);
        }""", [which, frm, to, n])

@pytest.mark.skipif(locust_suppressed_in_the_browser(), reason=SUPPRESSED)

def test_a_widened_range_reaches_settings_the_shipped_grid_could_not(page):
    _reset(page)
    # locust — the detector Tony was tuning. Its shipped grid stops at 99.9 and
    # its own control accepts 99.99.
    _set_range(page, "cicada", 90, 99.99, 9)
    grid = page.evaluate("() => sweepGrid('cicada')")
    assert len(grid) == 9, grid
    assert grid == sorted(grid), grid
    assert grid[-1] == pytest.approx(99.99), grid
    assert max(page.evaluate("() => DETECTORS.cicada.knob.grid")) == 99.9, (
        "the shipped grid moved; this test is about reaching past it")
    _reset(page)

@pytest.mark.skipif(locust_suppressed_in_the_browser(), reason=SUPPRESSED)

def test_the_range_boxes_mark_themselves_when_they_leave_the_default(page):
    _reset(page)
    assert page.evaluate("() => rangeEdited('cicada')") is False
    _set_range(page, "cicada", 90, 99.99, 9)
    assert page.evaluate("() => rangeEdited('cicada')") is True
    assert page.evaluate(
        "() => document.getElementById('tRange_cicada_to')"
        ".classList.contains('edited')") is True
    # Typing the shipped range back in is not an edit — the panel stops claiming
    # one, and `sweepGrid` goes back to the registry's own array.
    _set_range(page, "cicada", 90, 99.9, 6)
    assert page.evaluate("() => rangeEdited('cicada')") is False
    assert page.evaluate(
        "() => sweepGrid('cicada') === DETECTORS.cicada.knob.grid") is True
    _reset(page)

@pytest.mark.skipif(locust_suppressed_in_the_browser(), reason=SUPPRESSED)

def test_the_boxes_cannot_ask_for_a_setting_the_detector_will_not_hold(page):
    """A swept setting outside the control's own bounds is one the Detect step
    would silently clamp — so the sweep would score a value the reader could
    never apply. The bounds are read off the control rather than restated."""
    _reset(page)
    _set_range(page, "cicada", -50, 500, 8)
    grid = page.evaluate("() => sweepGrid('cicada')")
    lo, hi = page.evaluate(
        "() => { const b = knobBounds(DETECTORS.cicada.knob); return [b.lo, b.hi]; }")
    assert (lo, hi) == (80, 99.99), (lo, hi)
    assert min(grid) >= lo and max(grid) <= hi, grid
    _reset(page)


def test_the_bound_on_the_box_is_the_bound_the_detector_enforces(page):
    """`knobBounds` trusts the input's min/max. That is only safe while they are
    the same two numbers the detector's own `read` clamps to — so drive `read`
    past both ends and see where it lands."""
    _reset(page)
    got = page.evaluate(
        """(names) => names.map(k => {
             const knob = DETECTORS[k].knob;
             const node = document.getElementById(knob.input);
             const was = node.value;
             node.value = "-1e9";
             const low = DETECTORS[k].read(0.05)[knob.key];
             node.value = "1e9";
             const high = DETECTORS[k].read(0.05)[knob.key];
             node.value = was;
             return { k, low, high, min: Number(node.min), max: Number(node.max) };
           })""", RUNNABLE)
    for r in got:
        assert r["low"] == pytest.approx(r["min"]), (
            f"{r['k']}: the box says its floor is {r['min']} and the detector "
            f"clamps to {r['low']}. The sweep would offer settings the Detect "
            f"step cannot hold.")
        assert r["high"] == pytest.approx(r["max"]), r

@pytest.mark.skipif(locust_suppressed_in_the_browser(), reason=SUPPRESSED)

def test_a_range_of_one_setting_is_refused_rather_than_answered(page):
    """`pickOperatingPoint` hands back a single row as an operating point. With
    nothing on either side of it, that is exactly the un-bracketed answer this
    panel exists to refuse — so the sweep never gets there."""
    _reset(page)
    _set_range(page, "cicada", 99, 99, 4)
    assert len(page.evaluate("() => sweepGrid('cicada')")) == 1
    _reset(page)


# --------------------------------------------------------------------------
# spacing: a percentile grid is not a linear one


def test_a_percentile_range_is_spaced_by_its_tail(page):
    """Five settings from 99 to 99.9999 are one decade of tail apart.

    Interpolate a percentile linearly instead and four of the five land above
    99.75, where the surrogate distribution has almost nothing left to
    distinguish them with — the whole range that matters gets one point.
    """
    _reset(page)
    grid = page.evaluate(
        "() => makeGrid(DETECTORS.loco.knob, 99, 99.9999, 5)")
    assert grid == [99, 99.9, 99.99, 99.999, 99.9999], grid


def test_a_log_range_moves_by_factors(page):
    _reset(page)
    grid = page.evaluate("() => makeGrid(DETECTORS.coact.knob, 1e-6, 1e-2, 5)")
    assert [pytest.approx(v, rel=1e-6) for v in (1e-6, 1e-5, 1e-4, 1e-3, 1e-2)] \
        == grid, grid


def test_a_linear_range_stays_linear(page):
    _reset(page)
    grid = page.evaluate("() => makeGrid(DETECTORS.rate.knob, 1, 5, 5)")
    assert grid == [1, 2, 3, 4, 5], grid


# --------------------------------------------------------------------------
# the button on the refusal


def test_extending_goes_further_and_stops_where_the_detector_does(page):
    _reset(page)
    plan = page.evaluate(
        "() => extendPlan('cicada', DETECTORS.cicada.knob.grid, 'high')")
    assert plan["room"] is True, plan
    assert plan["to"] == pytest.approx(99.99), plan
    assert plan["from"] == 90 and plan["n"] > 6, plan


def test_extending_says_so_when_there_is_nowhere_left_to_go(page):
    """locust's control accepts 99.99 and no further. A grid already there
    cannot be widened, and saying "widen it" costs seven seconds a setting to
    find that out."""
    _reset(page)
    plan = page.evaluate("() => extendPlan('cicada', [99.0, 99.9, 99.99], 'high')")
    assert plan["room"] is False, plan
    assert plan["bound"] == pytest.approx(99.99), plan


def test_extending_downward_reaches_below_the_shipped_floor(page):
    _reset(page)
    plan = page.evaluate(
        "() => extendPlan('loco', DETECTORS.loco.knob.grid, 'low')")
    assert plan["room"] is True, plan
    assert plan["from"] < 99.0, plan
    assert plan["from"] >= 90, "LoCo's control accepts nothing below 90"
    assert plan["to"] == pytest.approx(99.9999), plan


def test_extending_a_descending_grid_goes_the_way_that_grid_goes(page):
    """CoactDetect again: the END of its grid is its SMALLEST alpha, so running
    out of range at the "high" end means the sweep wanted a tighter alpha, not a
    larger one. A plan that pushed toward the control's upper bound would widen
    in the direction the curve was already falling."""
    _reset(page)
    plan = page.evaluate(
        "() => extendPlan('coact', [1e-2, 1e-3, 1e-4], 'high')")
    assert plan["room"] is True, plan
    assert plan["up"] is False, plan
    assert plan["to"] < 1e-4, plan
    assert plan["to"] >= 1e-7, "1e-7 is the tightest alpha the box accepts"
    assert plan["from"] == pytest.approx(1e-2), plan
    # And the shipped grid already sits on that bound, so there is nothing left.
    at_bound = page.evaluate(
        "() => extendPlan('coact', DETECTORS.coact.knob.grid, 'high')")
    assert at_bound["room"] is False, at_bound


# A sweep that ran out of range, with only the fields `paintSweepBlock` reads.
# Built by hand rather than driven, because making a real sweep climb to the
# edge of the grid takes a contrived folder and this is a test about what the
# page OFFERS when it happens, not about when it happens.
_CLIMBING = """
([which, f1s]) => {
  const grid = DETECTORS[which].knob.grid;
  const rows = grid.map((v, i) => ({
    knob: v, nPlanted: 10, nDetected: 10, nHit: 8, nMiss: 2, nFa: 1, nDup: 0,
    precision: 0.8, recall: 0.8, f1: f1s[i], byFrac: new Map(),
  }));
  const out = { which, grid, rows, folds: [], split: null,
                edited: false, pick: pickOperatingPoint(rows) };
  const box = document.createElement("div");
  document.body.append(box);
  paintSweepBlock(box, out, [{ stream: "fast", nStreams: 1 }], 1.5, [], false);
  const text = box.textContent;
  const btns = [...box.querySelectorAll("button")].map(b => b.textContent);
  box.remove();
  return { text, btns, why: out.pick.why, end: out.pick.end };
}
"""


def test_a_sweep_that_ran_out_of_range_offers_to_extend_it(page):
    _reset(page)
    got = page.evaluate(_CLIMBING, ["cicada", [.1, .2, .3, .4, .5, .6]])
    assert got["end"] == "high", got
    assert "still climbing" in got["why"]
    extend = [b for b in got["btns"] if b.startswith("Extend")]
    assert extend, (
        f"the sweep said widen the range and offered no way to: {got['btns']}")
    assert "past 99.9" in extend[0], extend
    # And it says what it will search, before it costs anything.
    assert "99.99" in got["text"], got["text"]


def test_the_same_refusal_at_the_low_end_extends_downward(page):
    _reset(page)
    got = page.evaluate(_CLIMBING, ["cicada", [.6, .5, .4, .3, .2, .1]])
    assert got["end"] == "low", got
    extend = [b for b in got["btns"] if b.startswith("Extend")]
    assert extend and "past 90" in extend[0], (got["btns"], got["text"])


def test_a_degenerate_sweep_is_not_offered_a_wider_range(page):
    """Every setting scoring the same is the knob not deciding the answer.
    Widening is the one move that certainly will not help, and the page says so
    rather than handing over a button."""
    _reset(page)
    got = page.evaluate(_CLIMBING, ["cicada", [.4, .4, .4, .4, .4, .4]])
    assert [b for b in got["btns"] if b.startswith("Extend")] == [], got["btns"]
    assert "same result" in got["text"] or "not what decides" in got["text"], \
        got["text"]


def test_a_bracketed_peak_is_still_just_applied(page):
    """The ordinary case has to keep working: an interior optimum gets the
    apply button and no talk of ranges."""
    _reset(page)
    got = page.evaluate(_CLIMBING, ["cicada", [.1, .3, .9, .4, .2, .1]])
    assert [b for b in got["btns"] if b.startswith("Extend")] == [], got["btns"]
    assert any(b.startswith("Use this setting") for b in got["btns"]), got["btns"]


def test_the_block_names_the_range_it_was_measured_over(page):
    """A curve read a week later has to say what was searched. The count alone
    stopped identifying the run the moment the endpoints became editable."""
    _reset(page)
    got = page.evaluate(_CLIMBING, ["cicada", [.1, .3, .9, .4, .2, .1]])
    assert "6 settings tried" in got["text"], got["text"]
    assert "from 90 to 99.9" in got["text"], got["text"]
