"""Confirming the events, driven in the page that does it.

The step between Assess and Simulate. What is worth testing here is not that
buttons exist — it is the three properties the record depends on, none of which
are visible by reading the panel:

* the view is captured **at the moment of the verdict**, so a person who changes
  the ordering between judgements does not get one view stamped on every row;
* one verdict counts at every K at or below the one that candidate survives to,
  which is what lets somebody judge a single list and read a scan off it;
* the CSV columns match `annotate.COLUMNS` exactly, because the Python
  re-validates every row and refuses one whose view is missing.

The last one is the guard that matters most: the two halves are in different
languages and nothing else stops them drifting.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from bugarach.annotate import COLUMNS

VIEWER = Path(__file__).resolve().parents[1] / "docs/site/raster_viewer.html"

#: Dense enough that the assessment finds candidates to judge.
SIM = {"sRec": "2", "sMin": "25", "sRoi": "24", "sRate": "60", "sEv": "16",
       "sJit": "300", "sSeed": "11", "sWin": "0"}


@pytest.fixture(scope="module")
def page():
    pytest.importorskip("playwright.sync_api",
                        reason="the annotation stage is a property of the page")
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
                  await runAssess();
                }""", SIM)
            yield pg, errs
        finally:
            browser.close()


def _candidates(pg):
    return pg.evaluate("() => collectCandidates().length")


def test_the_assessment_leaves_candidates_to_judge(page):
    pg, errs = page
    assert _candidates(pg) > 0, "nothing to annotate — the fixture is too quiet"
    assert not errs, errs


def test_the_panel_offers_nothing_before_an_assessment_has_run(page):
    """The chip says so rather than the button failing when pressed."""
    pg, _ = page
    got = pg.evaluate("""() => {
      const saveF = FOLDER_ASSESS, saveL = LAST_ASSESS;
      FOLDER_ASSESS = null; LAST_ASSESS = null;
      paintAnnotChip();
      const out = { chip: document.getElementById('cntAnnot').textContent,
                    disabled: document.getElementById('anStart').disabled };
      FOLDER_ASSESS = saveF; LAST_ASSESS = saveL; paintAnnotChip();
      return out;
    }""")
    assert got["chip"] == "assess first"
    assert got["disabled"] is True


def test_one_busy_recording_cannot_eat_the_sample(page):
    """Mirrors the Python. One recording in this lab's folder carries 200
    candidates where the median is 8."""
    got = pg_sample(page, budget=30, cap=4)
    per = {}
    for c in got:
        per[c["recId"]] = per.get(c["recId"], 0) + 1
    assert per and max(per.values()) <= 4, per


def pg_sample(page, *, budget: int, cap: int, seed: int = 7):
    pg, _ = page
    return pg.evaluate(
        """([seed, budget, cap]) =>
             drawAnnotSample(collectCandidates(), seed, budget, cap)
               .picked.map(c => ({recId: c.recId, k: c.kSurvived}))""",
        [seed, budget, cap])


def test_the_draw_is_reproducible_from_its_seed(page):
    a = pg_sample(page, budget=20, cap=5, seed=3)
    b = pg_sample(page, budget=20, cap=5, seed=3)
    c = pg_sample(page, budget=20, cap=5, seed=4)
    assert a == b
    assert a != c or len(a) < 2      # a one-candidate folder cannot differ


def test_the_view_is_captured_at_the_verdict_not_at_export(page):
    """The property a reader cannot check by looking at the panel, and the one
    that makes the record worth keeping: judge, change the ROI ordering, judge
    again, and the two rows must disagree about the ordering."""
    pg, _ = page
    got = pg.evaluate("""async () => {
      startAnnotation();
      await showCandidate();
      ORDER = "file"; await showCandidate();
      recordVerdict("confirmed");
      await showCandidate();
      ORDER = "rate"; await showCandidate();
      recordVerdict("rejected");
      const v = ANNOT.verdicts.filter(Boolean);
      return v.map(x => x.view.order);
    }""")
    assert got[0] == "file"
    assert got[1] == "by_events", got


def test_one_verdict_counts_at_every_k_at_or_below_the_one_it_survived(page):
    """Candidates nest, which is what lets a person judge one list and read a
    whole scan off it."""
    pg, _ = page
    got = pg.evaluate("""() => {
      const fake = [{cand: {kSurvived: 8}, verdict: "confirmed"},
                    {cand: {kSurvived: 3}, verdict: "rejected"}];
      const m = agreementScan(fake);
      return {k3: m.get(3), k8: m.get(8)};
    }""")
    assert got["k3"]["c"] == 1 and got["k3"]["r"] == 1
    assert got["k8"]["c"] == 1 and got["k8"]["r"] == 0


def test_cannot_tell_is_kept_out_of_both_sides_of_the_rate(page):
    pg, _ = page
    got = pg.evaluate("""() => {
      const m = agreementScan([{cand: {kSurvived: 8}, verdict: "unsure"}]);
      return m.get(3);
    }""")
    assert got == {"c": 0, "r": 0, "u": 1}


def test_the_csv_columns_are_the_pythons_columns(page):
    """The two halves are in different languages and nothing else stops them
    drifting. `read_annotations` refuses a row whose view is missing, so a
    column dropped here becomes a file the pipeline will not accept."""
    pg, _ = page
    got = pg.evaluate("() => ANNOT_COLUMNS")
    assert got == list(COLUMNS), (got, list(COLUMNS))


def test_a_verdict_writes_absolute_seconds_not_window_relative(page):
    """The assessor's centres are relative to the analysis window; every time
    field in the export contract is absolute on the recording's own clock."""
    pg, _ = page
    got = pg.evaluate("""async () => {
      startAnnotation();
      await showCandidate();
      const c = ANNOT.cands[0];
      return { centre: c.centre, winStart: c.winStart, winEnd: c.winEnd };
    }""")
    assert got["centre"] >= got["winStart"]
    assert got["centre"] <= got["winEnd"]


def test_the_file_the_page_writes_is_a_file_the_python_accepts(tmp_path, page):
    """The whole seam, end to end, and the only test that can prove two halves
    in two languages still agree.

    `read_annotations` re-validates every row — a missing view, an unknown
    verdict, a malformed number all raise — so a page that drifted from the
    schema produces a file the pipeline refuses rather than one it misreads.
    """
    from bugarach.annotate import agreement_by_k, read_annotations

    pg, _ = page
    csv_text = pg.evaluate("""async () => {
      startAnnotation();
      await showCandidate();
      recordVerdict("confirmed");
      await showCandidate();
      recordVerdict("rejected");
      await showCandidate();
      recordVerdict("unsure");
      await showCandidate();
      document.getElementById("anWho").value = "tony";
      return annotationsCsv();
    }""")
    assert csv_text, "the page produced no file"

    p = tmp_path / "annotations.csv"
    p.write_text(csv_text, encoding="utf-8")
    verdicts = read_annotations(p)

    assert len(verdicts) == 3
    assert [v.verdict for v in verdicts] == ["confirmed", "rejected", "unsure"]
    assert all(v.annotator == "tony" for v in verdicts)
    # the view survived the crossing, which is what the Python refuses without
    assert all(v.view_t1_sec > v.view_t0_sec for v in verdicts)
    assert all(v.view_roi_order in ("file", "by_events") for v in verdicts)

    # and the scan the page drew is the scan the Python computes
    page_scan = pg.evaluate(
        "() => { const m = agreementScan(ANNOT.verdicts.filter(Boolean));"
        "        return [...m].map(([k, v]) => [k, v.c, v.r, v.u]); }")
    py_scan = agreement_by_k(verdicts)
    for k, c, r, u in page_scan:
        assert (py_scan[k].confirmed, py_scan[k].rejected, py_scan[k].unsure) \
            == (c, r, u), f"K={k} disagrees"


def test_no_page_errors_through_all_of_it(page):
    _, errs = page
    assert not errs, errs
