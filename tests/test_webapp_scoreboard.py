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

And one about where it lives. The wording has not been through the review this
repo requires of anything an outside reader sees, so the panel is gated on
`window.__lab` exactly as the training panel is: present in the file, inert and
hidden on the published page, visible under `bugarach lab`. The test that the
gate holds is the load-bearing one here — a draft that ships is not a draft.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

from conftest import locust_suppressed_in_the_browser

SUPPRESSED = (
    "locust is suppressed in this build; the behaviour below is still implemented and these come back with it (conftest.locust_suppressed_in_the_browser)")


ROOT = Path(__file__).resolve().parents[1]
VIEWER = ROOT / "docs/site/raster_viewer.html"


# ---------------------------------------------------------------- the gate

def test_the_panel_is_in_the_file_rather_than_added_by_a_build():
    """Inert by absence of a capability, not by a build step that strips it —
    the same reasoning as ADR-0001. Nothing can fail to be stripped."""
    html = VIEWER.read_text(encoding="utf-8")
    assert 'id="accScore"' in html
    assert re.search(r'<details[^>]*id="accScore"[^>]*\shidden', html), (
        "the scoreboard is not hidden by default, so it would appear on the "
        "published page with copy that has not been reviewed")


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


def test_the_published_page_never_shows_the_scoreboard(page):
    """The file as anyone on the internet opens it."""
    pg, errs = page
    assert not errs, errs
    assert pg.locator("#accScore").count() == 1
    assert pg.locator("#accScore").is_hidden(), (
        "unreviewed copy is visible on the page as published")
    assert pg.evaluate("() => window.__lab === undefined")


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

@pytest.mark.skipif(locust_suppressed_in_the_browser(), reason=SUPPRESSED)

def test_a_detector_that_cannot_run_says_so_instead_of_scoring_zero(scored):
    """CICADA on a folder with no peak is the case that exists today. A zero
    would read as a poor detector rather than an unanswerable question."""
    cic = next(r for r in scored["board"]["rows"] if r["which"] == "cicada")
    if cic.get("refused"):
        assert cic["f1"] is None or "f1" not in cic
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
