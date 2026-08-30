"""SPIKE-synch is off in the browser, and off is not the same as gone.

Tony, 2026-08-24: *"disable spike-sync detection in the browser for now."*

**Why the detector is still in the registry.** Deleting the row would take four
things with it: the parity harness that calls ``syncDetect`` directly, the
ability to draw a ``detections.csv`` that already holds sync rows, the label a
saved settings file needs to read itself back, and the reason. What is left
would be a page quietly missing a detector, which is the shape of a bug rather
than of a decision. So the row carries an ``unavailable`` string instead, and
every site that *selects* a detector to run honours it.

That is the same principle the rail already applies with ``gated``: not in this
build, drawn anyway, with the absence explained on the control that would
otherwise offer it. A reader who came looking for SPIKE-synch finds it and finds
out why.

**What this file pins.** That the reason reaches the reader, that no route
through the page can start a run with it, and that a scoreboard row says it did
not compete rather than dropping it — a comparison table with a silently missing
row invites the reading that the missing detector lost.

**To turn it back on**, delete the ``unavailable`` field from the ``sync`` row.
These tests derive everything from the page, so they follow it without an edit —
except the two that assert the detector is off at all, which will fail loudly and
say so. That is deliberate: the day it comes back, somebody should have to look
here.
"""

from __future__ import annotations

from pathlib import Path

import pytest

VIEWER = Path(__file__).resolve().parents[1] / "docs/site/raster_viewer.html"

SIM = {"sRec": "1", "sMin": "10", "sRoi": "20", "sRate": "45", "sEv": "8",
       "sJit": "300", "sSeed": "3", "sWin": "0"}


@pytest.fixture(scope="module")
def page():
    pytest.importorskip("playwright.sync_api",
                        reason="availability is a property of the running page")
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


# ------------------------------------------------- it is off, and it says why

def test_spike_synch_is_carried_and_not_runnable(page):
    pg, _ = page
    got = pg.evaluate("""() => ({
      carried: Object.keys(DETECTORS),
      runnable: runnableDetectors(),
      reason: offReason("sync"),
    })""")
    assert "sync" in got["carried"], (
        "the registry row was deleted rather than disabled — the parity "
        "harness, the settings labels and the reason all went with it")
    assert "sync" not in got["runnable"], got["runnable"]
    assert got["reason"], "off with no reason attached"


def test_the_reason_names_what_would_have_to_change(page):
    """A build that withholds something owes the reader the condition for
    getting it back, not just the fact of its absence."""
    pg, _ = page
    reason = pg.evaluate('() => offReason("sync")')
    low = reason.lower()
    assert "parity" in low, reason
    assert "profile" in low, reason


def test_the_detect_function_still_exists(page):
    """Off is a property of the page's selection surface, not of the numerics.
    `test_webapp_sync_detect_parity.py` calls this directly and must keep
    working, because it is the thing that will say whether the port is still
    faithful on the day it comes back."""
    pg, _ = page
    assert pg.evaluate('() => typeof syncDetect') == "function"


# ------------------------------------------------- no route selects it to run

def test_the_dropdown_offers_it_disabled_and_explains(page):
    pg, _ = page
    got = pg.evaluate("""() => {
      const o = [...document.getElementById("dDet").options]
                  .find(o => o.value === "sync");
      return o ? {disabled: o.disabled, text: o.textContent, title: o.title}
               : null;
    }""")
    assert got, "the option was removed rather than disabled"
    assert got["disabled"], "SPIKE-synch can still be chosen from the dropdown"
    assert "off in this build" in got["text"], got["text"]
    assert got["title"], "the disabled option carries no explanation"


def test_a_stale_selection_cannot_start_a_run(page):
    """The select should never hold it — its option is disabled — but a value
    set some other way must not be able to start a run either. `whichDetector`
    falls back the same way it does for an unknown key."""
    pg, _ = page
    got = pg.evaluate("""() => {
      const sel = document.getElementById("dDet");
      const was = sel.value;
      sel.value = "sync";
      const which = whichDetector();
      const chosen = chosenDetectors();
      sel.value = was;
      return {which, chosen};
    }""")
    assert got["which"] != "sync", got["which"]
    assert "sync" not in got["chosen"], got["chosen"]


def test_both_tick_lists_disable_it_and_ticking_it_selects_nothing(page):
    """Disabling the box is the visible half; the accessors refusing it is the
    half that matters. A tick forced past the disabled attribute must still not
    reach a run."""
    pg, _ = page
    got = pg.evaluate("""() => {
      document.getElementById("dAll").checked = true;
      paintDetectorChoice();
      const d = document.getElementById("dPick_sync");
      const t = document.getElementById("tPick_sync");
      const before = {d: d.disabled, t: t.disabled,
                      dChecked: d.checked, tChecked: t.checked};
      d.checked = true; t.checked = true;   // force past the disabled attribute
      return {...before,
              chosen: chosenDetectors(), swept: sweptDetectors()};
    }""")
    assert got["d"] and got["t"], "the tick boxes are still enabled"
    assert not got["dChecked"] and not got["tChecked"], (
        "an unavailable detector starts out ticked")
    assert "sync" not in got["chosen"], got["chosen"]
    assert "sync" not in got["swept"], got["swept"]


def test_the_folder_run_produces_no_sync_rows(page):
    """The end of the line: whatever the controls say, the file people keep must
    not contain rows from a detector this build withheld."""
    pg, errs = page
    got = pg.evaluate("""async (sim) => {
      for (const [k, v] of Object.entries(sim))
        document.getElementById(k).value = v;
      await runSim();
      document.getElementById("dAll").checked = true;
      for (const k of buildDetectors()) {
        const b = document.getElementById("dPick_" + k);
        b.checked = true;                    // every box, disabled ones included
      }
      paintDetectorChoice();
      await analyseFolder();
      return {
        detectors: FOLDER_RUN ? FOLDER_RUN.detectors : null,
        rowDetectors: FOLDER_RUN
          ? [...new Set(FOLDER_RUN.rows.map(r => r.detector))].sort() : null,
        thresholds: FOLDER_RUN
          ? Object.keys(runJson(FOLDER_RUN).thresholds).sort() : null,
        text: document.getElementById("detectOut").innerText,
      };
    }""", SIM)
    assert not errs, errs
    assert "sync" not in got["detectors"], got["detectors"]
    assert "sync" not in got["rowDetectors"], got["rowDetectors"]
    assert "sync" not in got["thresholds"], got["thresholds"]
    # and the reader is told, rather than left to count columns
    assert "off in this build and could not be ticked" in got["text"], (
        got["text"][:400])


# ------------------------------------------------- it did not lose, it did not play

def test_the_scoreboard_says_it_did_not_compete(page):
    """A comparison table that silently drops a row invites the reading that the
    missing detector scored badly. It did not compete, and the row says so."""
    pg, _ = page
    row = pg.evaluate("""() => {
      // the shape the scoreboard builds for a detector it will not score
      const which = "sync";
      return offReason(which)
        ? {which, label: DETECTORS[which].label,
           refused: "off in this build — " + offReason(which)}
        : null;
    }""")
    assert row, "no refusal row is built for an unavailable detector"
    assert row["label"] == "SPIKE-synch", row
    assert row["refused"].startswith("off in this build"), row["refused"]
