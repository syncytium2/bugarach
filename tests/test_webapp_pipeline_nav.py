"""The rail, and what a stranger meets before touching anything.

The page has three readers and one of them has no data. A casual visitor should
see coordinated events being detected; a researcher should be able to open a
folder, skip the two optional stages, and get an answer; and neither should have
to discover by clicking that simulating THROWS AWAY the folder they opened.

These are properties of the running page, not of its source, so they are checked
in a browser. Every one of them was true only by inspection before this file
existed, and the two that are easiest to break silently are the ones about
things NOT happening: the demo must not run when it has been turned off, and the
note that admits the data is invented must not survive a real folder.
"""

from __future__ import annotations

from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
VIEWER = ROOT / "docs" / "site" / "raster_viewer.html"

# The demo simulates three recordings and then runs a detector on one of them.
# Generous, because CI machines are slower than this one and a flake here reads
# as a broken page.
SETTLE_MS = 25_000


def _page(pw, *, demo: bool = True):
    """A loaded viewer, optionally with the landing demo already turned off.

    The switch has to be in storage BEFORE the page's script runs, because the
    boot reads it and starts work immediately. `add_init_script` runs on document
    creation, ahead of any page script, which is early enough. Each `launch` gets
    its own profile, so one test's setting cannot reach another's.
    """
    browser = pw.chromium.launch()
    pg = browser.new_page()
    errs: list[str] = []
    pg.on("pageerror", lambda e: errs.append(str(e)))
    if not demo:
        pg.add_init_script(
            "try { localStorage.setItem('bugarach.demo', 'off'); } catch (e) {}")
    pg.goto(VIEWER.as_uri(), wait_until="load")
    return browser, pg, errs


@pytest.fixture(scope="module")
def pw():
    pytest.importorskip("playwright.sync_api",
                        reason="the rail is a property of the running page")
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        yield p


@pytest.fixture(scope="module")
def landed(pw):
    """The page as a first-time visitor gets it: demo on, nothing clicked."""
    try:
        browser, pg, errs = _page(pw)
    except Exception as e:                                    # noqa: BLE001
        pytest.skip(f"no chromium available: {type(e).__name__}")
    try:
        pg.wait_for_function("() => RECORDINGS.length > 0 && DETECT !== null",
                             timeout=SETTLE_MS)
        yield pg, errs
    finally:
        browser.close()


def test_the_page_detects_something_before_anyone_clicks(landed):
    pg, errs = landed
    assert not errs, errs
    got = pg.evaluate("() => ({recs: RECORDINGS.length, "
                      "rows: DETECT ? DETECT.rows.length : 0, sim: SIMULATED})")
    assert got["recs"] > 0, "a visitor with no folder still meets an empty page"
    assert got["sim"], "the landing data must be simulated, never a real folder"
    assert got["rows"] > 0, (
        "the raster arrived with no detections on it — a raster alone shows what "
        "data looks like, not what this page is for")


def test_the_page_says_the_landing_data_is_invented(landed):
    pg, _ = landed
    note = pg.text_content("#demoNote")
    assert "simulated" in note.lower()
    assert "not a recording" in note.lower() or "nothing here is a recording" in note.lower()


def test_the_note_says_how_many_were_planted_and_how_many_were_found(landed):
    """The claim is scored, not asserted. A landing line that said "found them"
    without counting would be the one unchecked number on the page."""
    pg, _ = landed
    note = pg.text_content("#demoNote")
    assert "planted" in note and "found" in note, note


def test_the_rail_draws_two_tracks_and_not_one_line(landed):
    """The shape is the point. Read the grid rows the steps actually landed on:
    a single row would pass every other test in this file and still be the
    ladder the two tracks replaced."""
    pg, _ = landed
    got = pg.evaluate("""() => {
        const row = el => {
            const box = el.closest('.railgroup') || el;
            return box.style.gridRow || '';
        };
        const steps = [...document.querySelectorAll('#rail .step')];
        return {
          rows: Object.fromEntries(steps.map(s => [s.dataset.step, row(s)])),
          joins: [...document.querySelectorAll('#rail .railjoin')].map(j => j.textContent),
          bypass: !!document.querySelector('#rail .railbypass'),
          merge: !!document.querySelector('#rail .railmerge'),
          groups: [...document.querySelectorAll('#rail .glabel')]
                    .map(g => g.textContent).filter(Boolean),
        };
    }""")
    assert got["rows"]["accOpen"] == "1", got["rows"]
    assert got["rows"]["accSim"] == "3", (
        "the simulate entry has to be on its own track — stacked under the "
        "folder entry, not beside it", got["rows"])
    # the top track's own steps, which the bottom track never reaches
    for k in ("accAssess", "simFrom", "accVerify"):
        assert got["rows"][k] == "1", (k, got["rows"])
    assert "or" in got["joins"], (
        "the two sources are exclusive — simulating clears the opened folder — "
        "and the rail has to say so, because that is the whole reason it exists")
    assert got["bypass"], "the simulate track has no route to the shared tail"
    assert got["merge"], "the two tracks never visibly converge"
    assert got["groups"][0] == "source"


def test_the_two_simulate_steps_are_one_panel_said_two_ways(landed):
    """Calibrated from a measurement, or from defaults. Same controls, and the
    rail has to tell them apart — the label and the status both."""
    pg, _ = landed
    got = pg.evaluate("""() => {
        const of = k => document.querySelector(`#rail .step[data-step="${k}"]`);
        const a = of('simFrom'), b = of('accSim');
        return {
          samePanel: true,
          labels: [a.firstChild.textContent.trim(), b.firstChild.textContent.trim()],
          needs: [a.querySelector('.need').textContent,
                  b.querySelector('.need').textContent],
          calibratedOff: a.disabled, defaultsOff: b.disabled,
        };
    }""")
    assert got["labels"][0] != got["labels"][1], got["labels"]
    assert got["needs"][0] != got["needs"][1], (
        "both simulate steps read the same status off the one panel they share",
        got["needs"])
    assert got["calibratedOff"], (
        "simulating from a measurement offered itself with no measurement taken")
    assert not got["defaultsOff"]


def test_one_panel_is_in_the_column_and_the_rail_says_which(landed):
    pg, _ = landed
    got = pg.evaluate("""() => ({
        on: [...document.querySelectorAll('#side details.acc.on')].map(d => d.id),
        current: [...document.querySelectorAll('#rail .step[aria-current="true"]')]
                   .map(b => b.dataset.step),
    })""")
    assert len(got["on"]) == 1, got["on"]
    assert got["current"] == got["on"], (got["current"], got["on"])


def test_any_stage_can_be_reached_from_any_other(landed):
    """The point of the whole change: the reader is not walked down a ladder."""
    pg, _ = landed
    got = pg.evaluate("""() => {
        const order = ["accDetect", "accOpen", "accTune", "accSim", "accAssess"];
        const seen = [];
        for (const id of order) {
          document.querySelector(`#rail .step[data-step="${id}"]`).click();
          seen.push([...document.querySelectorAll('#side details.acc.on')]
                      .map(d => d.id).join(","));
        }
        return {order, seen};
    }""")
    assert got["seen"] == got["order"], got


def test_a_stage_that_cannot_run_yet_is_shown_and_says_what_it_wants(pw):
    """Tune scores against planted events, so on a folder read from disk it can
    never run. Hiding it is how the old page taught readers it did not exist."""
    try:
        browser, pg, errs = _page(pw, demo=False)
    except Exception as e:                                    # noqa: BLE001
        pytest.skip(f"no chromium available: {type(e).__name__}")
    try:
        got = pg.evaluate("""() => {
            const b = document.querySelector('#rail .step[data-step="accTune"]');
            return {there: !!b, off: b ? b.disabled : null,
                    need: b ? b.querySelector('.need').textContent : null};
        }""")
        assert not errs, errs
        assert got["there"], "Tune is not on the rail at all with no data open"
        assert got["off"], "Tune offers itself with nothing to score against"
        assert "simulated" in (got["need"] or ""), got["need"]
    finally:
        browser.close()


def test_turning_the_demo_off_leaves_the_page_empty(pw):
    """The switch is for the reader who opens this page daily to read their own
    folder. If it does not hold, it costs them a generator run and a screen of
    invented data every visit."""
    try:
        browser, pg, errs = _page(pw, demo=False)
    except Exception as e:                                    # noqa: BLE001
        pytest.skip(f"no chromium available: {type(e).__name__}")
    try:
        pg.wait_for_timeout(4000)
        got = pg.evaluate("() => ({recs: RECORDINGS.length, "
                          "note: document.getElementById('demoNote').hidden, "
                          "empty: !document.getElementById('empty').hidden})")
        assert not errs, errs
        assert got["recs"] == 0, "the demo ran with the switch off"
        assert got["note"], "the demo note is up with no demo behind it"
        # `hidden` alone is not enough: `#demoNote` sets `display: flex`, which
        # beats the UA rule for the attribute, and the note dismissed itself into
        # an empty bordered bar sitting above a real recording.
        assert not pg.locator("#demoNote").is_visible(), (
            "the note is hidden by attribute and still drawn")
        assert got["empty"], "nothing ran and the empty state is not showing"
    finally:
        browser.close()


def test_the_switch_is_reachable_after_the_note_is_gone(pw):
    """A reader who turned it off should not have to clear site data to undo."""
    try:
        browser, pg, errs = _page(pw, demo=False)
    except Exception as e:                                    # noqa: BLE001
        pytest.skip(f"no chromium available: {type(e).__name__}")
    try:
        pg.wait_for_timeout(1500)
        got = pg.evaluate("""() => {
            const box = document.getElementById("demoPref");
            const before = box.checked;
            box.checked = true; box.onchange();
            return {before, after: localStorage.getItem("bugarach.demo")};
        }""")
        assert not errs, errs
        assert got["before"] is False, "the panel switch does not show the setting"
        assert got["after"] is None, "ticking it back on did not clear the setting"
    finally:
        browser.close()


# ---------------------------------------------------------------------------
# Compare is a step, and it grumbles
#
# Tony, 2026-08-22: "compare is a step. that's my philosophy and it should force
# the user to at minimum click through with grumpy comments."
#
# Two halves, and both are tested because either alone is quiet enough to rot:
# the step says it has not been checked, and the panel that would spend the
# unchecked result says what that costs. Neither blocks — the comparison has no
# verdict to enforce, which is the whole reason it can only nag.
# ---------------------------------------------------------------------------

AIM = """async () => {
  // THE PANEL'S OWN DEFAULTS, not something smaller. Shrinking this to make the
  // test quick made the assessment find nothing above the participant floor, so
  // no K was offered, so no button existed to aim the generator with — and the
  // fixture skipped rather than failed, which is a test that says "passed" while
  // running none of what follows.
  await runSim();
  await show(RECORDINGS[0]);
  await runAssess();
  const b = [...document.querySelectorAll('#assessOut button')]
    .find(x => /set the simulator/i.test(x.textContent));
  if (!b) return {aimed: false};
  b.click();
  await runSim();
  return {aimed: !!SIM_TARGET, verified: !!VERIFY};
}"""


@pytest.fixture(scope="module")
def aimed(pw):
    """A simulated data set aimed at a measured recording and NOT yet compared."""
    try:
        browser, pg, errs = _page(pw, demo=False)
    except Exception as e:                                    # noqa: BLE001
        pytest.skip(f"no chromium available: {type(e).__name__}")
    try:
        pg.wait_for_timeout(600)
        got = pg.evaluate(AIM)
        if not got["aimed"]:
            pytest.skip("the assessment found no baseline to aim the generator at")
        assert not got["verified"], "nothing should have compared anything yet"
        yield pg, errs
    finally:
        browser.close()


def test_compare_is_its_own_step_and_its_own_panel(aimed):
    pg, _ = aimed
    got = pg.evaluate("""() => {
        const s = document.querySelector('#rail .step[data-step="accVerify"]');
        s.click();
        return {
          onRail: !!s,
          panel: [...document.querySelectorAll('#side details.acc.on')].map(d => d.id),
          button: !!document.querySelector('#accVerify #verifySim'),
          enabled: !document.querySelector('#accVerify #verifySim').disabled,
        };
    }""")
    assert got["onRail"]
    assert got["panel"] == ["accVerify"], got["panel"]
    assert got["button"], (
        "Compare is still a button inside another panel — it was moved out "
        "precisely so it stops being two panels deep")
    assert got["enabled"], "aimed at a measurement and still refusing to compare"


def test_the_step_says_it_has_not_been_checked(aimed):
    pg, _ = aimed
    got = pg.evaluate("""() => {
        const n = document.querySelector('#rail .step[data-step="accVerify"] .need');
        return {text: n.textContent, nagging: n.classList.contains('nag')};
    }""")
    assert "not checked" in got["text"].lower(), got["text"]
    assert got["nagging"], (
        "the unchecked state reads like every other status line, so nothing "
        "distinguishes 'you have not done this' from 'here is where you are'")


def test_tune_says_what_skipping_the_check_costs(aimed):
    """The grumble has to land where the cost does. A setting fitted on a data
    set nobody compared is a setting fitted on an unchecked generator."""
    pg, _ = aimed
    got = pg.evaluate("""() => {
        showSection('accTune');
        const n = document.getElementById('tuneUnchecked');
        return {hidden: n.hidden, text: n.textContent,
                sweepBlocked: document.getElementById('runTune').disabled};
    }""")
    assert not got["hidden"], "Tune spends an unchecked generator without saying so"
    assert "never compared" in got["text"], got["text"]
    assert not got["sweepBlocked"], (
        "the sweep must stay reachable — the comparison has no verdict, so "
        "there is nothing for it to enforce")


def test_the_grumble_stops_once_the_comparison_is_made(aimed):
    pg, errs = aimed
    got = pg.evaluate("""async () => {
        await verifySimulation();
        showSection('accTune');
        const n = document.querySelector('#rail .step[data-step="accVerify"] .need');
        return {
          verified: !!VERIFY,
          need: n.textContent, nagging: n.classList.contains('nag'),
          tick: !!document.querySelector(
            '#rail .step[data-step="accVerify"] .tick'),
          tuneNag: document.getElementById('tuneUnchecked').hidden,
        };
    }""")
    assert not errs, errs
    assert got["verified"]
    assert not got["nagging"], got["need"]
    assert got["tick"], "a comparison that was made leaves no mark on the step"
    assert got["tuneNag"], "Tune goes on complaining after the check was done"
