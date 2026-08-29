"""Every detector on one data set and one fold split — and off the published page.

Phase 4 of `docs/webapp_completion_plan.md`: one row per detector, F1 with fold
spread, recall, precision, fit seconds, detect seconds, parameter count.

The tune panel already sweeps a detector properly — across the whole data set, fold split,
setting chosen on train and scored on held-out. What it cannot do is compare,
because two of its runs are two fold assignments. So the value here is not new
scoring, it is **one data set and one split for all of them**.

TWO THINGS THIS PANEL MUST NOT DO, both already recorded:

  * imply a detector is right about a **real** slice — everything measured is on
    simulated data, and no real slice has an answer key to be right against;
  * carry the phrase *"competes with state-of-the-art"*, because the comparison
    contains no published learned method and none of the assembly-detection
    family.

And one about where it lives. **It is published, since 2026-08-29** — its copy
went through `docs/doc_review_process.md` first and the run record is
`docs/reviews/scoreboard_copy_2026-08-29.md`. Before that it was gated beside the
training panel, and the training panel is still gated: it needs a local server,
so shipping it would offer a visitor a button that cannot work.

⚠ **The gate test that guarded this could not fail, for two years' worth of the
usual reason.** It asserted the `hidden` attribute in the markup and
`locator("#accScore").is_hidden()` on load. But `details.acc` is `display:none`
until the rail adds `.on`, and the rail shows one panel at a time — so **every**
accordion is `is_hidden()` on load, gated or not, and the assertion was true of
the whole sidebar. The real gate was `gated: true` in the rail registry, which no
test read. The replacement reads the registry, and reads `accLab` the same way so
that a green result demonstrates the check can go red.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
VIEWER = ROOT / "docs/site/raster_viewer.html"


# ---------------------------------------------------------------- the gate

def test_the_panel_is_in_the_file_rather_than_added_by_a_build():
    """Inert by absence of a capability, not by a build step that strips it —
    the same reasoning as ADR-0001. Nothing can fail to be stripped."""
    html = VIEWER.read_text(encoding="utf-8")
    assert 'id="accScore"' in html


def test_the_scoreboard_is_published_and_the_rail_offers_it():
    """The panel went out 2026-08-29, after its copy passed the murderboard —
    `docs/reviews/scoreboard_copy_2026-08-29.md`.

    **The assertion this replaces could not fail, and that is the finding worth
    keeping.** It required `<details id="accScore" … hidden>` in the markup and,
    in its Playwright half, `locator("#accScore").is_hidden()` on a freshly
    loaded page. Neither measured the gate:

    * `details.acc` is `display:none` until the rail adds `.on`, and the rail
      shows **one panel at a time**. Every accordion on this page is
      `is_hidden()` on load, gated or not. That assertion was true of the whole
      sidebar and said nothing about the scoreboard.
    * The real gate was `gated: true` on the panel's `TAIL` entry — one of the
      two publish edits the file's own `accLab` comment names — and no test
      read it.

    So a test whose module docstring called the gate "the load-bearing one here"
    would have stayed green through the exact change it existed to catch. This
    reads the gate itself, and reads `accLab` the same way so that a green
    result proves the check can go red.
    """
    html = VIEWER.read_text(encoding="utf-8")
    entry = re.search(r'\{\s*key:\s*"accScore".*?\}', html, re.S)
    assert entry, "the scoreboard has no step in the rail registry"
    assert "gated" not in entry.group(0), (
        "accScore is gated again — `gated` means 'not in this build at all', so "
        "the panel is off the published page. If that is deliberate, say why; "
        "if not, this is the publish edit reverted by accident")

    lab = re.search(r'\{\s*key:\s*"accLab".*?\}', html, re.S)
    assert lab and "gated: true" in lab.group(0), (
        "accLab is NOT gated — the training panel needs a local server, and "
        "shipping it to visitors offers a button that cannot work. This is also "
        "what proves the assertion above can fail: both entries are read the "
        "same way and they must disagree")


def test_the_draft_copy_is_collected_in_one_place_for_review():
    html = VIEWER.read_text(encoding="utf-8")
    assert "const SCORE_COPY" in html, (
        "the panel's sentences should sit in one object a reviewer can read "
        "without hunting them through the render code")


def test_no_banned_phrase_anywhere_in_the_page():
    """`competes with state-of-the-art`, in any spacing or casing."""
    html = VIEWER.read_text(encoding="utf-8").lower()
    flat = re.sub(r"\s+", " ", html)
    for banned in ("competes with state-of-the-art",
                   "competes with the state of the art",
                   "state-of-the-art performance"):
        assert banned not in flat, banned


@pytest.fixture(scope="module")
def page():
    pytest.importorskip("playwright.sync_api",
                        reason="the gate is a property of the running page")
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


def test_a_visitor_with_no_server_can_reach_the_scoreboard(page):
    """The page as anyone on the internet opens it, driven to the panel.

    `is_hidden()` on load is NOT the question and was the old test's mistake —
    the rail shows one accordion at a time, so every panel is hidden then. The
    question is whether a visitor with **no lab server** can navigate to this
    step and find a working control, which is what publishing it means.
    """
    pg, errs = page
    assert not errs, errs
    assert pg.evaluate("() => window.__lab === undefined"), (
        "this must be measured on the published page, not under `bugarach lab`")
    assert pg.locator("#accScore").count() == 1

    offered = pg.evaluate("() => !!ALL_STEPS.find(s => s.key === 'accScore') "
                          "&& !ALL_STEPS.find(s => s.key === 'accScore').gated")
    assert offered, "the rail does not offer the scoreboard step"

    pg.evaluate("""async () => {
      for (const [k, v] of Object.entries({sRec:"3", sMin:"45", sRoi:"33",
          sRate:"10", sEv:"15", sJit:"360", sSeed:"1"}))
        document.getElementById(k).value = v;
      await runSim();
      showSection("accScore");
    }""")
    assert pg.locator("#accScore").is_visible(), (
        "the step is offered but navigating to it shows nothing")
    assert pg.locator("#runScore").is_visible()
    assert pg.locator("#scoreWhat").inner_text().strip(), (
        "the panel says nothing before the button is pressed — a reader who "
        "opens it and does not click is told neither what it does nor what it "
        "needs")
    assert not errs, errs


def test_the_training_panel_is_still_gated(page):
    """The other half of the same registry, and the control for the test above.

    Training needs a local server. Publishing that panel would offer a visitor a
    button that cannot work — which is the ONE thing the lab gate is for, and it
    survives the scoreboard leaving it.
    """
    pg, errs = page
    assert not errs, errs
    assert pg.evaluate("() => !!ALL_STEPS.find(s => s.key === 'accLab').gated"), (
        "accLab is no longer gated")


# ---------------------------------------------------------------- the numbers

SIM = {"sRec": "6", "sMin": "25", "sRoi": "24", "sRate": "12", "sEv": "14",
       "sJit": "300", "sSeed": "4"}

SCORE = """async (sim) => {
  for (const [k, v] of Object.entries(sim)) document.getElementById(k).value = v;
  await runSim();
  document.getElementById("scTol").value = "1.5";
  await scoreAllDetectors();
  const box = document.getElementById("scoreOut");
  return {board: SCOREBOARD, text: box.innerText,
          headers: [...box.querySelectorAll("th")].map(t => t.textContent.trim())};
}"""


@pytest.fixture(scope="module")
def scored(page):
    pg, errs = page
    got = pg.evaluate(SCORE, SIM)
    assert not errs, errs
    assert got["board"], "the scoreboard produced nothing"
    return got


def test_every_detector_gets_a_row(scored):
    rows = scored["board"]["rows"]
    got = {r["which"] for r in rows}
    assert got == {"rate", "sce", "coact", "loco", "cicada", "sync"}, sorted(got)


def test_a_detector_that_cannot_run_says_so_instead_of_scoring_zero(scored):
    """A refused row carries its reason, never a zero.

    A zero would read as a poor detector rather than an unanswerable question,
    and the table's whole claim is that every row was offered the same folds.

    TWO REASONS a row is refused now, and both must produce the same shape. A
    detector can be unable to answer THIS folder — the peak-less case — or be
    withheld from the build entirely, which since 2026-08-29 covers `sync` and
    `cicada`. The second arrived after this test was written and would have
    slipped past it: the old version read `cic["f1"]` unguarded, so a withheld
    row raised KeyError instead of failing an assertion, which is a crash
    dressed as a test result.
    """
    refused = [r for r in scored["board"]["rows"] if r.get("refused")]
    assert refused, "no row was refused, so this checked nothing"
    for r in refused:
        assert r.get("f1") is None, (
            f"{r['which']} was refused and still carries an F1: {r.get('f1')}")
        assert str(r["refused"]).strip(), f"{r['which']} refused with no reason"
    assert "could not run" in scored["text"]


def test_the_columns_the_plan_asked_for_are_all_there(scored):
    heads = [h.lower() for h in scored["headers"]]
    for want in ("detector", "f1", "precision", "recall", "knobs", "fit",
                 "detect"):
        assert any(want in h for h in heads), (f"{want} missing from {heads}")


def test_f1_carries_a_fold_spread_rather_than_one_number(scored):
    scorable = [r for r in scored["board"]["rows"]
                if not r.get("refused") and r.get("f1") is not None]
    assert scorable, "nothing scored at all"
    assert any(r.get("sd") is not None for r in scorable), (
        "no detector reported a spread across folds; a single F1 with no spread "
        "is the number the plan says not to quote")


def test_every_detector_was_offered_the_same_folds(scored):
    """The reason this panel exists. Two runs of the tune step would each pick
    their own split; a comparison across those is not a comparison."""
    n = {r["nFolds"] for r in scored["board"]["rows"] if not r.get("refused")}
    assert len(n) == 1, f"detectors were offered different fold counts: {n}"


def test_a_detector_that_answered_fewer_folds_says_so(scored):
    """The silent cap this caught on its first run.

    `pickOperatingPoint` refuses a boundary answer, so a fold can yield no
    setting. Averaging the folds that worked and printing one F1 hides that a
    row rests on a third of the evidence — and, being a mean of one, it also
    loses its spread, which reads as agreement rather than as almost no data.
    """
    rows = [r for r in scored["board"]["rows"] if not r.get("refused")]
    assert all("nScored" in r for r in rows)
    for r in rows:
        assert r["nScored"] <= r["nFolds"]
    # every row states its denominator on screen, whether or not it is short
    for r in rows:
        assert f"{r['nScored']} of {r['nFolds']}" in scored["text"], (
            f"{r['which']} does not show how many folds it actually answered")
    if any(r["nScored"] < r["nFolds"] for r in rows):
        assert "end of the grid" in scored["text"], (
            "a detector answered fewer folds than it was offered and the panel "
            "does not say why")


def test_it_says_the_numbers_are_simulated_and_claims_nothing_about_real_slices(
        scored):
    low = scored["text"].lower()
    assert "simulated" in low
    for banned in ("on your recordings", "these are the events",
                   "correctly identifies", "accurate on real"):
        assert banned not in low, banned


def test_it_says_the_learned_detector_is_absent_rather_than_leaving_a_hole(
        scored):
    assert "learned" in scored["text"].lower()


def test_it_warns_that_the_gap_between_two_rows_is_not_the_reading(scored):
    """`docs/learned/tolerance_sweep.png`: the ranking is safe, a bare number
    implying timing accuracy is not."""
    low = scored["text"].lower()
    assert "ranking" in low or "order" in low
