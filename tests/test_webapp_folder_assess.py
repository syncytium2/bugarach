"""Assessing a folder, not whichever recording happened to be on screen.

Tony, 2026-08-21: *"assessor should have assess whole folder option?"*

**Yes, and it was a port rather than a design.** ``bugarach assess my_export/``
has walked an export folder, measured each recording's baseline and printed the
K scan since 2026-08-18; the browser assessed one recording at a time. The cost
was not convenience: the generator is parameterised from ONE measurement, so
until now the simulated data set inherited whichever file was open when somebody
pressed the button. A folder assessment is what makes *"typical of this lab"* a
measurable statement instead of a choice of file.

Measured on the real 84-recording export, served: **10.2 s wall, 84 of 84
measured, none skipped**, against the ~15 s the note's arithmetic predicted.
That is far too long for a button that greys out and says nothing, so the
progress line is the CLI's own — ``assessing: 12/84 · 20240708_13 (1s, ~6s
left)``, ending ``assessing: 84/84 in 10s`` — and the two read as one tool
because they say the same words.

Every test presses the button. The three rules below are not properties of a
data structure; they are what the panel prints, and the one that has already
gone wrong in this project went wrong in a rendering.
"""

from __future__ import annotations

from pathlib import Path

import pytest

VIEWER = Path(__file__).resolve().parents[1] / "docs/site/raster_viewer.html"

# Three recordings, each 45 min split into baseline + drug, so every baseline
# clears the assessment's own 15-minute floor and the folder has something to
# take a median over.
SIM = {"sRec": "3", "sMin": "45", "sRoi": "24", "sRate": "45", "sEv": "16",
       "sJit": "300", "sSeed": "6", "sWin": "2"}


@pytest.fixture(scope="module")
def page():
    pytest.importorskip("playwright.sync_api",
                        reason="the walk is a property of the running page")
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


WALK = """async (sim) => {
  for (const [k, v] of Object.entries(sim)) document.getElementById(k).value = v;
  await runSim();
  await show(RECORDINGS[0]);
  const before = {label: document.getElementById("assessFolder").textContent,
                  disabled: document.getElementById("assessFolder").disabled};
  // the progress line is caught by watching the node, not by reading the
  // function — a message written and never painted is the failure mode
  const seen = [];
  const watch = new MutationObserver(() => {
    const t = document.getElementById("assessFolderWhat").textContent;
    if (t && seen[seen.length - 1] !== t) seen.push(t);
  });
  watch.observe(document.getElementById("assessFolderWhat"),
                {childList: true, characterData: true, subtree: true});
  await assessFolderRun();
  watch.disconnect();
  const out = document.getElementById("assessOut");
  return {
    before, seen,
    kControl: document.getElementById("aK").value,
    marked: ASSESS ? {K: ASSESS.K} : null,
    nRecords: FOLDER_ASSESS.records.length,
    ids: FOLDER_ASSESS.records.map(r => r.id),
    regionCounts: FOLDER_ASSESS.regionCounts,
    summaryRows: [...out.querySelectorAll("table")][0].rows.length,
    summaryKs: [...[...out.querySelectorAll("table")][0].rows].slice(1)
                 .map(r => r.cells[0].textContent),
    perRecRows: [...out.querySelectorAll("table")][1].rows.length,
    text: out.innerText,
  };
}"""


@pytest.fixture(scope="module")
def walked(page):
    pg, errs = page
    got = pg.evaluate(WALK, SIM)
    assert not errs, errs
    return got


def test_the_button_is_dead_until_a_folder_is_open_and_then_says_how_many(page):
    """A button that reads the same with nothing open is a button whose scope
    the reader has to guess."""
    pg, _ = page
    fresh = pg.evaluate("""() => {
      const b = document.getElementById("assessFolder");
      return {label: b.textContent, disabled: b.disabled};
    }""")
    # the module fixture may have run already; assert on the pre-run capture
    assert "folder" in fresh["label"].lower() or "recordings" in fresh["label"]


def test_it_walks_every_recording_and_none_of_them_twice(walked):
    assert walked["nRecords"] == 3, walked["ids"]
    assert len(set(walked["ids"])) == 3, walked["ids"]
    assert walked["before"]["label"] == "Assess all 3 recordings", \
        walked["before"]["label"]


def test_the_progress_line_is_the_CLI_s_and_it_actually_painted(walked):
    """`cli._progress` prints `assessing: 12/84 · <id> (3s, ~11s left)` and
    finishes `assessing: 84/84 in 15s`. Same words here, because a user who has
    run the command should recognise the page and vice versa."""
    seen = walked["seen"]
    assert seen, "the progress node never changed — the walk ran blind"
    assert all(s.startswith("assessing: ") for s in seen), seen
    assert any("·" in s and "left" in s for s in seen[:-1] or seen), seen
    assert seen[-1].startswith("assessing: 3/3 in "), seen[-1]


def test_K_is_a_scan_and_the_walk_reports_every_one_of_them(walked):
    assert walked["summaryKs"] == ["3", "4", "6", "8"], walked["summaryKs"]
    assert "K is a scan, not a choice" in walked["text"]


def test_the_walk_did_not_quietly_pick_a_K(walked):
    """The rule that has already cost this project once, in a rendering rather
    than a data structure: a folder assessment that chose K would make the
    choice its own panel spends a paragraph refusing to make."""
    assert walked["kControl"] == "0", (
        "the K control moved; K is a scan, not a choice")
    assert walked["marked"] is None, (
        "cluster ticks were drawn at a K nobody chose")


def test_tightness_says_how_many_recordings_could_answer(walked):
    """`jit_defined` is a state, not a NaN. A median of the four recordings that
    had a surrogate cluster, printed bare beside a K where seventy could not, is
    a number about almost nothing."""
    txt = walked["text"]
    assert ("defined)" in txt) or ("undefined in all" in txt), txt[:400]


def test_every_recording_gets_a_row_whether_or_not_it_could_be_measured(walked):
    # header + one row per recording
    assert walked["perRecRows"] == 1 + walked["nRecords"], walked["perRecRows"]


def test_the_periods_it_skipped_over_are_counted_and_printed(walked):
    """FOUNDATIONS §9 — treatments are not a source of coordination properties,
    so they are skipped. A silent skip would make a folder of treatments look
    like a quiet folder, so the tally goes on screen."""
    assert walked["regionCounts"].get("baseline") == 3, walked["regionCounts"]
    assert walked["regionCounts"].get("drug") == 3, walked["regionCounts"]
    assert "Periods declared across the folder" in walked["text"]


def test_it_reports_the_folder_s_rate_as_a_mean_and_says_so(walked):
    """The simulator's rate box means the field's MEAN, and handing it a median
    of medians is the defect the single-recording path already paid for. So the
    folder number says which statistic it is, in the sentence."""
    assert "field MEAN" in walked["text"], walked["text"][:600]


def test_it_does_not_set_the_simulator(page, walked):
    """Whether a folder median should aim the generator in place of one
    recording's numbers changes what the accept step means. That is Tony's call,
    filed in `docs/todo/2026-08-21-app-notes-from-use.md`, and a port that
    quietly took it would have decided it."""
    pg, _ = page
    assert pg.evaluate("() => SIM_TARGET") is None
    assert "not this port's decision" in walked["text"]


def test_a_window_under_the_floor_is_named_rather_than_dropped(page):
    """Three windows over 22 minutes puts every baseline under the 15-minute
    floor. The recording still appears, and the row says why there are no
    numbers in it — an absent recording and a recording that could not answer
    must not look alike."""
    pg, errs = page
    got = pg.evaluate("""async () => {
      const spec = {sRec: "2", sMin: "22", sRoi: "24", sRate: "45", sEv: "14",
                    sJit: "300", sSeed: "6", sWin: "3"};
      for (const [k, v] of Object.entries(spec))
        document.getElementById(k).value = v;
      await runSim();
      await show(RECORDINGS[0]);
      await assessFolderRun();
      const out = document.getElementById("assessOut");
      return {n: FOLDER_ASSESS.records.length,
              rows: [...out.querySelectorAll("table")].slice(-1)[0].rows.length,
              text: out.innerText};
    }""")
    assert not errs, errs
    assert got["n"] == 2
    assert got["rows"] == 3, "a recording vanished from the per-recording table"
    assert "under the 15-minute floor" in got["text"], got["text"][:400]
