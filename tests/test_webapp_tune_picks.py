"""One detector or six, and nothing between — in the two places it mattered.

Tony, 2026-08-21: *"tune panel should have a selector for which detectors to
tune. most users will have a favorite or two and wont even look at the weirdos
we created."*

**The timings argue for it harder than preference does.** Fit seconds over one
data set: SPIKE-synch 0.06, CoactDetect 0.08, RateDetect 0.10, SCE 0.17, **LoCo
2.69, CICADA 7.06** — two detectors are about 97% of the wall clock. Driven on
four simulated 45-minute recordings, served: **the cheap four sweep in 0.8 s and
all six in 6.2 s**, so unticking two is not a convenience, it is the difference
between a sweep that returns while you are looking at it and one you wait out.
And until this landed the panel showed one static "Sweeping…" over the whole of
it.

The second half is the same defect one panel down. ``analyseFolder`` ran
``Object.keys(DETECTORS)`` regardless of the Detect step's tick list, so the one
control on that panel governed the raster and not the ~minute-long folder run
that produces the file people keep. It reads ``chosenDetectors()`` now — the
same accessor the single-recording run uses, so the picture and the export
cannot disagree about what "all the ticked detectors" means.

Timings are quoted, never asserted: a CI box is not this laptop, and a test that
fails when a machine is busy teaches people to rerun it.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from conftest import locust_suppressed_in_the_browser

SUPPRESSED = (
    "locust is suppressed in this build; the behaviour below is still implemented and these come back with it (conftest.locust_suppressed_in_the_browser)")


VIEWER = Path(__file__).resolve().parents[1] / "docs/site/raster_viewer.html"

SIM = {"sRec": "2", "sMin": "22", "sRoi": "22", "sRate": "45", "sEv": "14",
       "sJit": "300", "sSeed": "5", "sWin": "0"}
# WHAT THE PAGE CAN RUN, which since 2026-08-24 is not the same as what it
# carries. A row with `unavailable` still draws, still reads an older settings
# file back, and its detector stays callable — but nothing on the page can tick
# it. These lists are the SELECTABLE set.
#
# `sync` came out on 2026-08-24. `cicada` (locust) came out on 2026-08-29, held
# back for the release: it is the only one of the six that consumes a per-event
# duration, this build scores it at a fixed one, and the generator plants no
# duration to vary. Four remain selectable. When either `unavailable` is deleted,
# put the key back here and the counts below move with it.
ALL = ["rate", "loco", "coact", "sce"]
CHEAP = ["rate", "coact", "sce"]


@pytest.fixture(scope="module")
def page():
    pytest.importorskip("playwright.sync_api",
                        reason="the tick list is a property of the running page")
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
                }""", SIM)
            yield pg, errs
        finally:
            browser.close()


def _tick(pg, prefix: str, on: list[str]):
    pg.evaluate(
        """([prefix, on]) => {
          for (const k of Object.keys(DETECTORS)) {
            const b = document.getElementById(prefix + k);
            if (!b) continue;
            const want = on.includes(k);
            if (b.checked !== want) { b.checked = want;
                                      b.dispatchEvent(new Event("change")); }
          }
        }""", [prefix, on])

@pytest.mark.skipif(locust_suppressed_in_the_browser(), reason=SUPPRESSED)

def test_the_tune_panel_has_a_tick_per_detector_and_marks_the_costly_two(page):
    pg, _ = page
    got = pg.evaluate("""() => ({
      boxes: [...document.querySelectorAll('#tPicks input[type=checkbox]')]
               .map(b => b.id),
      slow: [...document.querySelectorAll('#tPicks label')]
              .filter(l => l.querySelector('.cost'))
              .map(l => l.textContent.replace(/slow$/, '').trim()),
    })""")
    assert got["boxes"] == ["tPick_" + k for k in
                           pg.evaluate("() => Object.keys(DETECTORS)")]
    assert sorted(got["slow"]) == ["LoCo", "locust"], got["slow"]

@pytest.mark.skipif(locust_suppressed_in_the_browser(), reason=SUPPRESSED)

def test_it_says_which_before_the_click_and_names_the_slow_ones(page):
    pg, _ = page
    _tick(pg, "tPick_", CHEAP)
    cheap = pg.evaluate("() => document.getElementById('tuneWhat').textContent")
    _tick(pg, "tPick_", ALL)
    both = pg.evaluate("() => document.getElementById('tuneWhat').textContent")
    assert "costly" in cheap, cheap
    assert "LoCo and locust" in both, both
    assert "97%" in both, both


def test_no_tick_is_a_question_with_no_subject(page):
    pg, _ = page
    _tick(pg, "tPick_", [])
    got = pg.evaluate("""() => ({
      disabled: document.getElementById('runTune').disabled,
      chip: document.getElementById('cntTune').textContent,
      note: document.getElementById('tuneWhat').textContent})""")
    assert got["disabled"], "an empty sweep was offered"
    assert got["chip"] == "none ticked", got["chip"]
    assert "Tick at least one" in got["note"], got["note"]


def test_a_subset_sweeps_exactly_that_subset_and_says_so(page):
    """One block per ticked detector, in registry order, with the scope named at
    the top — a table whose scope the reader reconstructs from block headings is
    a table that gets quoted with the wrong scope."""
    pg, errs = page
    _tick(pg, "tPick_", CHEAP)
    got = pg.evaluate("""async () => {
      await runTune();
      const out = document.getElementById("tuneOut");
      return {heads: [...out.querySelectorAll("h5")].map(h =>
                        h.textContent.trim()),
              scope: out.querySelector("p.sub").textContent,
              tables: out.querySelectorAll("table").length,
              note: document.getElementById("tuneWhat").textContent};
    }""")
    assert not errs, errs
    # REGISTRY order, never tick order, so a rerun does not reshuffle the blocks
    labels = pg.evaluate(
        "([ks]) => Object.keys(DETECTORS).filter(k => ks.includes(k))"
        ".map(k => DETECTORS[k].label)", [CHEAP])
    assert got["heads"] == labels, got["heads"]
    assert got["tables"] == len(CHEAP)
    for lab in labels:
        assert lab in got["scope"], got["scope"]
    assert "The rest were not ticked and are not in this run." in got["scope"]
    # The off detector is named apart from the ones the reader declined: a sweep
    # that folded it into "not ticked" would look narrower by choice than it was.
    assert "off in this build and could not be swept" in got["scope"], got["scope"]
    assert got["note"].startswith(f"swept {len(CHEAP)} detectors"), got["note"]


def test_the_progress_line_moves_through_the_detectors(page):
    """The old panel put one static "Sweeping…" over the whole run, most of
    which is two detectors. This watches the node rather than the function: a
    message written and never painted is the failure being fixed."""
    pg, errs = page
    _tick(pg, "tPick_", CHEAP)
    seen = pg.evaluate("""async () => {
      const n = document.getElementById("tuneWhat");
      const seen = [];
      const w = new MutationObserver(() => {
        const t = n.textContent;
        if (t && seen[seen.length - 1] !== t) seen.push(t);
      });
      w.observe(n, {childList: true, characterData: true, subtree: true});
      await runTune();
      w.disconnect();
      return seen;
    }""")
    assert not errs, errs
    moving = [s for s in seen if s.startswith("sweeping: ")]
    assert moving, seen
    assert any(f"1/{len(CHEAP)}" in s for s in moving), moving[:4]
    assert any(f"{len(CHEAP)}/{len(CHEAP)}" in s for s in moving), moving[-4:]
    assert any("setting " in s for s in moving), moving[:4]


def test_the_two_tick_lists_are_independent(page):
    """Unticking a detector to get a sweep back in ten seconds must not silently
    drop it from the folder export an hour later. Tony's open question — "one
    preference, or two?" — answered two, because two cannot lose data."""
    pg, _ = page
    pg.evaluate("""() => { document.getElementById("dAll").checked = true;
                           paintDetectorChoice(); }""")
    _tick(pg, "dPick_", ALL)
    _tick(pg, "tPick_", ["rate"])
    assert pg.evaluate("() => chosenDetectors().length") == len(ALL)
    assert pg.evaluate("() => sweptDetectors()") == ["rate"]
    _tick(pg, "tPick_", ALL)
    _tick(pg, "dPick_", ["rate"])
    assert pg.evaluate("() => sweptDetectors().length") == len(ALL)
    assert pg.evaluate("() => chosenDetectors()") == ["rate"]


FOLDER = """async (on) => {
  document.getElementById("dAll").checked = true;
  for (const k of Object.keys(DETECTORS)) {
    const b = document.getElementById("dPick_" + k);
    b.checked = on.includes(k);
  }
  paintDetectorChoice();
  await analyseFolder();
  const out = document.getElementById("detectOut");
  return {
    ran: FOLDER_RUN ? FOLDER_RUN.detectors : null,
    rowDetectors: FOLDER_RUN
      ? [...new Set(FOLDER_RUN.rows.map(r => r.detector))].sort() : null,
    thresholds: FOLDER_RUN ? Object.keys(runJson(FOLDER_RUN).thresholds) : null,
    head: [...out.querySelectorAll("table tr:first-child th")]
            .map(t => t.textContent),
    text: out.innerText,
    note: document.getElementById("folderWhat").textContent,
  };
}"""


def test_the_folder_run_honours_the_tick_list(page):
    """It ran all six regardless until 2026-08-23, so the panel's one control
    governed the picture and not the file."""
    pg, errs = page
    got = pg.evaluate(FOLDER, ["rate", "sce"])
    assert not errs, errs
    assert got["ran"] == ["rate", "sce"], got["ran"]
    assert got["rowDetectors"] == ["rate", "sce"], got["rowDetectors"]
    assert got["thresholds"] == ["rate", "sce"], got["thresholds"]
    assert got["head"] == ["recording", "rows", "RateDetect", "SCE"], got["head"]
    assert "did not run and are not in the file" in got["text"], got["text"][:400]


def test_a_detector_that_did_not_run_gets_no_column_at_all(page):
    """Blank is a third answer beside "found nothing" and "could not run", and
    it is not one this page is entitled to give."""
    pg, _ = page
    got = pg.evaluate(FOLDER, ["rate", "sce"])
    for absent in ("LoCo", "locust", "CoactDetect", "SPIKE-synch"):
        assert absent not in got["head"], got["head"]


def test_an_empty_tick_list_is_refused_rather_than_written(page):
    """The same split `bugarach detect` makes: nothing scored is a refusal,
    nothing found is a result. A header-only file would blur them."""
    pg, errs = page
    got = pg.evaluate(FOLDER, [])
    assert not errs, errs
    assert got["ran"] is None
    assert "nothing to run over the folder" in got["note"], got["note"]
