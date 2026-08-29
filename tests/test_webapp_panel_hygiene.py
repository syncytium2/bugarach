"""Three ways a working page lied about what was on it.

None of these is an exception, a crash or a wrong number in isolation. Each is
the screen disagreeing with itself, which is worse than an error because it
reads as a result:

  * a **duplicate element id** — CoactDetect and CICADA both shipped a
    surrogate box called `cSur`, so CICADA's read CoactDetect's value. CICADA's
    own control moved nothing and turning CoactDetect's moved both detectors,
    silently, whenever "run several" was ticked.
  * a **window table that outlived its folder** — set windows on one folder,
    open another, and the table still reported the first one's periods and
    counts beside a chip saying the new folder sent its own.
  * a **folder table that dropped the caveats** the single-recording view has
    always printed, so its headline row count overstated what was found.

Every test presses the buttons. That is not a style preference: the surrogate
coupling survived a suite that read `DETECTORS.cicada.read(dt)` and got a
plausible number back, because the number came from the wrong box.
"""

from __future__ import annotations

from pathlib import Path

import pytest

VIEWER = Path(__file__).resolve().parents[1] / "docs/site/raster_viewer.html"

DUPES = """() => {
  const seen = new Set(), dup = [];
  for (const n of document.querySelectorAll('[id]'))
    if (seen.has(n.id)) dup.push(n.id); else seen.add(n.id);
  return dup;
}"""


def _go(pg, step: str):
    """Walk the pipeline rail, the way a reader does."""
    pg.click(f'#rail [data-step="{step}"]')


def _show_every_detector(pg):
    """Tick "run several" and every detector in it, which is what puts all six
    parameter blocks on the screen at once — and the only way the two surrogate
    boxes are both reachable.

    A DETECTOR THIS BUILD WITHHOLDS IS UNHIDDEN DIRECTLY rather than ticked. Its
    box is disabled, so ``pg.check`` waits for it to become checkable and times
    out — which is the disable working, and is asserted properly in
    ``test_webapp_sync_unavailable.py``. But hygiene is a property of the DOM
    rather than of what a reader may select: a duplicate id inside a block
    nobody can currently reach is still a duplicate id, and it becomes reachable
    again the day the field comes off the registry row. Dropping the block from
    the scan would retire that coverage silently, so it is shown the short way.
    """
    _go(pg, "accDetect")
    pg.check("#dAll")
    for k in ("rate", "sce", "coact", "loco", "cicada", "sync"):
        if pg.evaluate("k => !!offReason(k)", k):
            pg.evaluate(
                "k => { document.getElementById(DETECTORS[k].ctl).hidden = false; }",
                k)
            continue
        pg.check(f"#dPick_{k}")


@pytest.fixture(scope="module")
def page():
    pytest.importorskip("playwright.sync_api",
                        reason="these are properties of the running page")
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
            pg.wait_for_function(
                "() => document.getElementById('demoNote') && "
                "!document.getElementById('demoNote').hidden", timeout=60000)
            yield pg, errs
        finally:
            browser.close()


# --------------------------------------------------------------------------
# duplicate ids — the guard is worth more than the fix


def test_no_element_id_appears_twice_on_the_page(page):
    """The general guard, which is the point.

    The specific fix was renaming one input. This is what stops the next one:
    a second element answering to a live id makes `getElementById` return
    whichever came first, and the control that lost the coin toss goes inert
    with nothing failing anywhere.
    """
    pg, errs = page
    assert pg.evaluate(DUPES) == [], (
        f"duplicate element ids: {pg.evaluate(DUPES)}")
    assert not errs, errs


def test_still_no_duplicates_once_the_page_has_built_its_own_controls(page):
    """Half the page's ids are generated — one checkbox per detector, one row
    per period kind. A static scan of the file would never see them."""
    pg, errs = page
    _show_every_detector(pg)
    assert pg.evaluate(DUPES) == []
    assert not errs, errs


def test_cicadas_surrogate_control_moves_cicada_and_not_coactdetect(page):
    """Typed into the boxes, read out of what the detectors would run with."""
    pg, errs = page
    _show_every_detector(pg)
    pg.fill("#ciSur", "380")
    pg.fill("#cSur", "60")
    got = pg.evaluate("""() => ({
      cicada: DETECTORS.cicada.read(0.1).nSurrogates,
      coact: DETECTORS.coact.read(0.1).nSurrogates,
    })""")
    assert got == {"cicada": 380, "coact": 60}, (
        f"the two surrogate controls are still coupled: {got}")
    assert not errs, errs


# --------------------------------------------------------------------------
# the window table and the folder it describes

WINS_MINE = ("slice_id,region_idx,label,start_sec,end_sec\n"
             "one,1,baseline,0,1800\n"
             "one,2,drug,1800,3600\n")

WINS_SENT = ("slice_id,region_idx,label,start_sec,end_sec,"
             "analysis_start_sec,analysis_end_sec\n"
             "other,1,baseline,0,1800,600,1800\n"
             "other,2,drug,1800,3600,1920,3120\n")

TRAIN = "roi,time_sec\n" + "".join(
    f"r{r:02d},{t}.0\n" for r in range(1, 6) for t in range(10, 3600, 37))


def _folder(name, regions, slices):
    return [{"name": f"{name}.csv", "text": TRAIN},
            {"name": "regions.csv", "text": regions},
            {"name": "slices.csv", "text": slices}]


def test_the_window_table_does_not_outlive_the_folder_it_describes(page):
    """Chip and table, on screen together, about two different folders.

    `open()` clears the planted truth, the simulator spec, the folder run, the
    verification, the recordings, the regions, the roster, the delay
    exemptions, the rail's ✓ marks and both check panels. `#windowOut` was the
    one piece of folder-shaped state it walked past, and `clearWindows()` had
    always known how to clear it.
    """
    pg, errs = page
    pg.evaluate("async (f) => { await open(f); }",
                _folder("one", WINS_MINE,
                        "slice_id,frame_interval_sec\none,0.1\n"))
    _go(pg, "accWindows")
    pg.click("#runWindows")
    pg.wait_for_timeout(400)
    before = pg.eval_on_selector("#windowOut", "e => e.innerText")
    assert "set here" in before, before
    assert pg.eval_on_selector("#cntWindows", "e => e.textContent") == "set here"

    pg.evaluate("async (f) => { await open(f); }",
                _folder("other", WINS_SENT,
                        "slice_id,frame_interval_sec\nother,0.1\n"))
    pg.wait_for_timeout(400)
    _go(pg, "accWindows")
    after = pg.eval_on_selector("#windowOut", "e => e.innerText").strip()
    chip = pg.eval_on_selector("#cntWindows", "e => e.textContent")
    assert after == "", (
        f"the new folder's chip says {chip!r} while the table below it still "
        f"reports the last one: {after[:160]!r}")
    assert chip == "sent by the folder", chip
    assert pg.evaluate("() => WINDOWS_ARE_MINE") is False
    assert not errs, errs


# --------------------------------------------------------------------------
# the folder table and the caveats it dropped

SIM = {"sRec": "2", "sMin": "10", "sRoi": "16", "sRate": "12", "sEv": "6",
       "sJit": "360", "sSeed": "4"}


def test_the_folder_table_carries_the_caveat_the_one_recording_view_does(page):
    """CICADA's single-cell moments, in the view that produces the file.

    Where the raster is sparse, the threshold rolled off it lands at one active
    cell and every isolated transient clears it. The detector is faithful; the
    operating point is degenerate, and the count is not about coordination. The
    single-recording panel has always said so and the folder table did not —
    which is backwards, because the folder table is the one attached to the
    download button. On the lab's own 84 recordings, analysed whole-period at
    the shipped settings, that silence covered 7,064 single-cell rows inside
    CICADA's 38,266 — itself 63% of the run's 60,417.

    Counted and said, never filtered: raising a floor until the awkward rows
    disappear is what FOUNDATIONS §9 forbids in terms.

    **The withholding is lifted for the length of this run and put back after.**
    Since 2026-08-29 that detector carries `unavailable` — off the public build
    while how it should be named and credited is settled — so a folder run
    produces no rows for it and this test had nothing to count. Lifting keeps the
    caveat's behaviour under test in the state it will be restored from; the
    tests that assert a visitor cannot reach it live in
    `test_webapp_cicada.py` and `test_webapp_tune_picks.py` and would fail if
    this leaked.
    """
    pg, errs = page
    pg.evaluate("""async (sim) => {
      for (const [k, v] of Object.entries(sim))
        document.getElementById(k).value = v;
      await runSim();
    }""", SIM)
    held = pg.evaluate("""() => {
      const h = DETECTORS.cicada.unavailable;
      delete DETECTORS.cicada.unavailable;
      paintDetectorChoice();
      const b = document.getElementById("dPick_cicada");
      if (b && !b.checked) { b.checked = true; b.dispatchEvent(new Event("change")); }
      return h === undefined ? null : h;
    }""")
    _go(pg, "accDetect")
    pg.click("#runFolder")
    pg.wait_for_function("() => !document.getElementById('runFolder').disabled",
                         timeout=600000)
    got = pg.evaluate("""() => ({
      extras: FOLDER_RUN.extras,
      single: FOLDER_RUN.rows.filter(
        r => r.detector === 'cicada' && r.n_roi === 1).length,
      text: document.getElementById('detectOut').innerText,
      brackets: [...document.querySelectorAll('#detectOut td .qual')]
        .map(n => n.textContent.trim()),
    })""")
    pg.evaluate("""(h) => {
      if (h !== null) DETECTORS.cicada.unavailable = h;
      paintDetectorChoice();
    }""", held)
    assert got["single"] > 0, (
        "this fixture no longer produces single-cell CICADA rows, so it can no "
        "longer show whether the caveat is printed — pick a sparser folder")
    assert got["extras"]["cicada"]["n"] == got["single"], (
        f"the folder run counted {got['extras']['cicada']['n']} single-cell "
        f"moments and the rows hold {got['single']}")
    assert "single-cell" in got["text"], (
        "the folder table prints a row count for CICADA and nothing about what "
        "that count contains:\n" + got["text"][-600:])
    assert got["brackets"], (
        "no cell in the table carries its qualified count, so the number a "
        "reader copies out is still the unqualified one")
    assert not errs, errs
