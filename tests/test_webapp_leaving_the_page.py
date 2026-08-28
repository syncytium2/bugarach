"""What survives a tab switch, and what the page owes you before you close it.

Tony, 2026-08-27: *"can you change tabs while the sweep is running and not lose
anything?"*

Changing tabs is safe, and that was measured rather than assumed: the same sweep
run in front and backgrounded returns the same rows and the same settings. What
was NOT safe is closing the tab. A locust sweep is minutes of work — the panel
says so beside the tick list — and the page carried no ``beforeunload`` handler
at all, so a reload discarded the run, the simulated folder, and any fit not yet
written to a settings file, without a word.

The guard has two failure modes and this file pins both. Not arming is the
obvious one. **Arming too eagerly is the one that would actually get shipped**:
most people open this page to look at a raster, and a viewer that asks "leave
site?" every time would train the one reader it is for to click through it. So
the tests below spend more effort on when it must STAY QUIET.
"""

from __future__ import annotations

from pathlib import Path

import pytest

VIEWER = Path(__file__).resolve().parents[1] / "docs/site/raster_viewer.html"

SIM = {"sRec": "2", "sMin": "12", "sRoi": "20", "sRate": "45", "sEv": "10",
       "sJit": "300", "sSeed": "3", "sWin": "0"}


@pytest.fixture(scope="module")
def page():
    pytest.importorskip("playwright.sync_api",
                        reason="an unload guard is a property of a running page")
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
            assert not errs, errs
            yield pg
        finally:
            browser.close()


def _simulate(pg):
    pg.evaluate("""async (sim) => {
      for (const [k, v] of Object.entries(sim)) document.getElementById(k).value = v;
      await runSim();
      await show(RECORDINGS[0]);
    }""", SIM)


def _reset(pg):
    pg.evaluate("""() => {
      for (const k of Object.keys(TUNED)) delete TUNED[k];
      TUNED_SAVED = true;
      TUNE_RUNNING = false;
    }""")


# ---------------------------------------------------------------------------
# when it must stay quiet — the failure mode that would ship


def test_a_freshly_opened_page_does_not_ask(page):
    _reset(page)
    assert page.evaluate("() => unsavedWork()") is None


def test_opening_a_folder_is_not_a_reason_to_ask(page):
    """A simulated folder is regenerable from its own seed, and the seed is in
    the box. Guarding it would be guarding nothing."""
    _simulate(page)
    _reset(page)
    assert page.evaluate("() => RECORDINGS.length > 0") is True
    assert page.evaluate("() => unsavedWork()") is None


def test_a_hand_typed_threshold_is_not_a_reason_to_ask(page):
    """Typing a number is not work the page has to protect — the number is on
    screen, and nothing was computed to get it."""
    _simulate(page)
    _reset(page)
    page.evaluate("""() => {
      const n = document.getElementById("dThr");
      n.value = "3.5";
      n.dispatchEvent(new Event("input", { bubbles: true }));
    }""")
    assert page.evaluate("() => unsavedWork()") is None


def test_saving_the_settings_file_stops_it_asking(page):
    """The file is how a fit is meant to survive this page. Once it is written,
    there is nothing left to lose and the prompt has to go away."""
    _simulate(page)
    _reset(page)
    page.evaluate("""() => useTunedSetting("rate", 3, {
      knobName: "excess threshold", unit: "Hz", f1: 0.8, heldOut: true,
      nFolds: 3, dataSetN: 2, tolSec: 1.5 })""")
    assert page.evaluate("() => unsavedWork()") is not None
    page.evaluate("() => saveSettingsFile()")
    assert page.evaluate("() => unsavedWork()") is None, (
        "the settings file was written and the page still wants to warn about it")
    _reset(page)


def test_opening_another_folder_clears_the_debt(page):
    """`open` drops TUNED on purpose — a value fitted on one folder is not a
    claim about the next. The guard has to forget with it, or every folder
    change leaves a permanent warning behind."""
    _simulate(page)
    _reset(page)
    page.evaluate("""() => useTunedSetting("rate", 3, {
      knobName: "excess threshold", unit: "Hz", f1: 0.8, heldOut: true,
      nFolds: 3, dataSetN: 2, tolSec: 1.5 })""")
    assert page.evaluate("() => unsavedWork()") is not None
    _simulate(page)          # runSim() -> open() -> TUNED = {}
    assert page.evaluate("() => Object.keys(TUNED).length") == 0
    assert page.evaluate("() => unsavedWork()") is None
    _reset(page)


# ---------------------------------------------------------------------------
# when it must speak up


def test_a_running_sweep_is_a_reason_to_ask(page):
    _simulate(page)
    _reset(page)
    page.evaluate("() => { TUNE_RUNNING = true; }")
    why = page.evaluate("() => unsavedWork()")
    assert why and "sweep" in why, why
    _reset(page)


def test_an_unsaved_fit_is_a_reason_to_ask(page):
    """The expensive case: the sweep is done, the number is in the box, and it
    exists nowhere else. This is what a stray reload used to throw away."""
    _simulate(page)
    _reset(page)
    page.evaluate("""() => useTunedSetting("rate", 3, {
      knobName: "excess threshold", unit: "Hz", f1: 0.8, heldOut: true,
      nFolds: 3, dataSetN: 2, tolSec: 1.5 })""")
    why = page.evaluate("() => unsavedWork()")
    assert why and "saved" in why, why
    _reset(page)


def test_the_guard_is_actually_wired_to_the_browser(page):
    """`unsavedWork()` being right is worth nothing if nothing calls it. Fire a
    real beforeunload and see whether the event comes back cancelled."""
    _simulate(page)
    _reset(page)
    quiet = page.evaluate(
        """() => { const e = new Event("beforeunload", { cancelable: true });
                   window.dispatchEvent(e); return e.defaultPrevented; }""")
    assert quiet is False, "the page asked to confirm with nothing to lose"
    page.evaluate("() => { TUNE_RUNNING = true; }")
    loud = page.evaluate(
        """() => { const e = new Event("beforeunload", { cancelable: true });
                   window.dispatchEvent(e); return e.defaultPrevented; }""")
    assert loud is True, (
        "a sweep was running and closing the tab would not have been questioned")
    _reset(page)


# ---------------------------------------------------------------------------
# the yield, which is what backgrounding actually costs


def test_the_long_loops_do_not_yield_through_a_throttled_timer(page):
    """Chrome clamps background-tab timers to >=1s, and to >=1min after about
    five minutes hidden. The yields are per grid setting, so that clamp
    multiplies by the size of the sweep — a 20-setting LoCo sweep performs 25 of
    them, which is ~25s backgrounded and ~25 MINUTES once intensive throttling
    starts. A MessageChannel message is an ordinary task, not a timer task.

    Asserted against the source rather than by timing, because Chromium under
    automation cannot be made to throttle: Playwright launches it with
    --disable-background-timer-throttling and two friends, and dropping them
    still will not hide a tab.
    """
    body = VIEWER.read_text(encoding="utf-8")
    assert "await new Promise(r => setTimeout(r, 0))" not in body, (
        "a long loop yields through setTimeout again — backgrounded, that costs "
        "a second per grid setting, then a minute per grid setting. Use "
        "`await yieldToUI()`.")
    assert body.count("await yieldToUI();") > 10, (
        "the yields stopped going through the shared helper")


def test_the_yield_still_yields(page):
    """A yield that does not reach the event loop would freeze the page instead
    of keeping it answerable — the opposite of what these calls are for."""
    ordered = page.evaluate("""async () => {
      const seen = [];
      const p = yieldToUI().then(() => seen.push("after-yield"));
      seen.push("sync");
      setTimeout(() => seen.push("timer"), 0);
      await p;
      return seen;
    }""")
    assert ordered[0] == "sync", ordered
    assert "after-yield" in ordered, ordered


def test_many_yields_all_resolve_and_in_order(page):
    """One MessageChannel serves every caller, so a queue bug would resolve the
    wrong promise — the kind of thing that shows up as a sweep hanging on point
    seven, once, on somebody else's machine."""
    got = page.evaluate("""async () => {
      const order = [];
      await Promise.all(Array.from({ length: 200 }, (_, i) =>
        yieldToUI().then(() => order.push(i))));
      return { n: order.length, sorted: order.every((v, i) => v === i) };
    }""")
    assert got["n"] == 200, got
    assert got["sorted"] is True, "yields resolved out of order"
