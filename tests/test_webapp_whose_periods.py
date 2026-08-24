"""Two places the page showed something true and did not say what it was.

**The region menu.** Tony, 2026-08-21: *"sb222200 should not be on this list.
why is it present and not ttx or senk?"* — and it was neither a bug nor a
missing entry. The menu lists the OPEN RECORDING's own periods, and the
recording open at the time declares baseline and SB222200 and nothing else. The
folder's tally is baseline 84, high K+ 60, TTX 38, senktide 35, SB222200 12,
wash 9, so which drugs appear changes with every file. Nothing said the list was
per recording, so a legitimate entry read as the app being wrong about the
folder — and the first four files in the export are among the twelve carrying
SB222200, which is what anybody sees on opening it.

Named rather than filtered, in two places: an `<optgroup>` carrying the
recording's id, and a sentence for the reader who never opens the dropdown.
Measuring a treatment stays legitimate — the guard that matters is on
`simulateFromMeasurement`, which refuses a non-baseline outright.

**The legend swatch.** Tony, 2026-08-21: the sentence names a bar AND a shading;
the swatch drew one of them. It draws both now, and — the half this file adds —
it draws the TRIM, or shows there is none. A rail and a field of the same width
say the period and the scored part are one extent; a field inset under a
full-width rail says time happened and is not counted. The lab's own export
sends 238 regions and not one analysis window, so the honest key over it shows
no distinction at all, and a swatch that always showed one would imply a
distinction the folder never made.
"""

from __future__ import annotations

from pathlib import Path

import pytest

VIEWER = Path(__file__).resolve().parents[1] / "docs/site/raster_viewer.html"

SIM = {"sRec": "1", "sMin": "40", "sRoi": "20", "sRate": "45", "sEv": "12",
       "sJit": "300", "sSeed": "4", "sWin": "2"}


@pytest.fixture(scope="module")
def page():
    pytest.importorskip("playwright.sync_api",
                        reason="both are properties of the running page")
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
            pg.evaluate("""async (sim) => {
              for (const [k, v] of Object.entries(sim))
                document.getElementById(k).value = v;
              await runSim();
              await show(RECORDINGS[0]);
            }""", SIM)
            yield pg, errs
        finally:
            browser.close()


MENU = """() => ({
  group: [...document.querySelectorAll("#aRegion optgroup")]
           .map(g => g.label),
  grouped: [...document.querySelectorAll("#aRegion optgroup option")]
             .map(o => o.textContent),
  loose: [...document.querySelectorAll("#aRegion > option")]
           .map(o => o.textContent),
  note: document.getElementById("aRegionWhat").textContent,
  id: current.id,
})"""


def test_the_menu_says_whose_periods_it_is_listing(page):
    pg, errs = page
    got = pg.evaluate(MENU)
    assert not errs, errs
    assert got["group"] == ["declared by " + got["id"]], got["group"]
    assert got["note"].startswith("The middle group is " + got["id"] + "'s own "
                                  "periods"), got["note"]


def test_the_recording_s_own_periods_are_inside_that_group(page):
    pg, _ = page
    got = pg.evaluate(MENU)
    assert "baseline" in got["grouped"], got["grouped"]
    assert any("drug" in o for o in got["grouped"]), got["grouped"]
    # the two entries that are not periods stay outside it
    assert "baseline (default)" in got["loose"], got["loose"]
    assert "whole recording" in got["loose"], got["loose"]


def test_nothing_was_filtered_out_of_it(page):
    """Measuring a treatment is legitimate and the code says so in terms; the
    rule FOUNDATIONS §9 states is about parameterising the generator, and that
    guard already exists on `simulateFromMeasurement`. Naming the list is the
    fix; shortening it would remove a thing somebody may want to look at."""
    pg, _ = page
    got = pg.evaluate(MENU)
    declared = pg.evaluate(
        "() => (REGIONS.get(current.id) || []).map(w => w.label)")
    for label in declared:
        assert any(o.startswith(label) for o in got["grouped"]), (label, got)
    assert "not for calibration" in " ".join(got["grouped"])
    assert "Only a baseline can set the simulator" in got["note"]


def test_a_recording_with_no_periods_says_that_instead(page):
    pg, errs = page
    got = pg.evaluate("""async () => {
      const spec = {sRec: "1", sMin: "40", sRoi: "20", sRate: "45", sEv: "12",
                    sJit: "300", sSeed: "4", sWin: "0"};
      for (const [k, v] of Object.entries(spec))
        document.getElementById(k).value = v;
      await runSim();
      await show(RECORDINGS[0]);
      return {note: document.getElementById("aRegionWhat").textContent,
              groups: document.querySelectorAll("#aRegion optgroup").length};
    }""")
    assert not errs, errs
    assert got["groups"] == 0, "an empty group was drawn"
    assert "declares no periods" in got["note"], got["note"]


# Measured off the drawn boxes rather than off the inline style, because the
# claim is about the picture: `inset` is how much narrower the shading is than
# the bar above it, in pixels, and zero is the two channels agreeing.
LEGEND = """() => {
  const sw = [...document.querySelectorAll("#wins .win")].map(w => {
    const f = w.querySelector(".sw .field").getBoundingClientRect();
    const r = w.querySelector(".sw .rail").getBoundingClientRect();
    return {inset: Math.round((f.left - r.left) + (r.right - f.right)),
            rail: r.width > 0, field: f.width > 0};
  });
  return {sw, chan: document.querySelector("#wins .chan").textContent};
}"""


def test_the_swatch_carries_both_channels(page):
    pg, errs = page
    got = pg.evaluate("""async () => {
      const spec = {sRec: "1", sMin: "40", sRoi: "20", sRate: "45", sEv: "12",
                    sJit: "300", sSeed: "4", sWin: "2"};
      for (const [k, v] of Object.entries(spec))
        document.getElementById(k).value = v;
      await runSim();
      await show(RECORDINGS[0]);
      return null;
    }""")
    got = pg.evaluate(LEGEND)
    assert not errs, errs
    assert got["sw"], "no swatches drawn"
    assert all(s["rail"] and s["field"] for s in got["sw"]), got["sw"]


def test_it_shows_no_trim_where_the_folder_declared_none(page):
    """The watch-out in the note, and the case the lab's own export is: 238
    regions, no analysis window among them. A swatch implying a distinction the
    folder never made is worse than no key at all."""
    pg, _ = page
    # exactly the shape `regions.csv` has in this lab's export: bounds and
    # nothing else. The page's own generator sends analysis windows, so they are
    # stripped here rather than the folder being the one that never had them.
    pg.evaluate("""() => {
      for (const w of REGIONS.get(current.id) || []) {
        delete w.aStart; delete w.aEnd;
      }
      show(current);
    }""")
    pg.wait_for_timeout(200)
    got = pg.evaluate(LEGEND)
    assert all(s["inset"] == 0 for s in got["sw"]), got["sw"]
    assert "no analysis window was sent" in got["chan"], got["chan"]


def test_it_draws_the_trim_once_there_is_one(page):
    """Deriving windows in the page applies a wash-in delay, so the scored part
    of every treatment becomes a strict subset of its period — and the key has
    to be able to show that, or the sentence beside it is unsupported."""
    pg, errs = page
    got = pg.evaluate("""async () => {
      document.getElementById("runWindows").click();
      await new Promise(r => setTimeout(r, 60));
      await show(current);
      return null;
    }""")
    got = pg.evaluate(LEGEND)
    assert not errs, errs
    bounds = pg.evaluate("() => (REGIONS.get(current.id) || []).map(w => "
                         "[w.start, w.end, w.aStart, w.aEnd])")
    trimmed = [i for i, (s, e, a, b) in enumerate(bounds)
               if a is not None and (a != s or b != e)]
    assert trimmed, bounds
    for i in trimmed:
        assert got["sw"][i]["inset"] > 0, (i, got["sw"][i], bounds[i])
    assert "the part scored" in got["chan"], got["chan"]


def test_a_window_that_was_sent_and_trims_nothing_is_its_own_sentence(page):
    """Three states, because there are three. "No analysis window was sent" and
    "one was sent and trims nothing" are different facts about the folder and
    used to share a sentence — and the swatches beside them now differ, so a key
    that could not tell them apart would be contradicted by its own picture."""
    pg, _ = page
    got = pg.evaluate("""() => {
      for (const w of REGIONS.get(current.id) || []) {
        w.aStart = w.start; w.aEnd = w.end;
      }
      show(current);
      return null;
    }""")
    pg.wait_for_timeout(200)
    got = pg.evaluate(LEGEND)
    assert "which here is all of it" in got["chan"], got["chan"]
    assert all(s["inset"] == 0 for s in got["sw"]), got["sw"]
