"""The complaint dies with the tab; the file outlives it.

Tony, 2026-08-22: *"compare is a step. that's my philosophy and it should force
the user to at minimium click through with grumpy comments."*

The step and the grumbling landed with the two-track rail: Compare has its own
panel, its own place in the rail, and a nag that repaints until somebody looks.
What
[`docs/todo/2026-08-22-compare-is-a-step-you-click-through.md`](../docs/todo/2026-08-22-compare-is-a-step-you-click-through.md)
left open was whether skipping it leaves a **persistent mark on the run** — and
the answer here is yes, in ``run.json``'s ``generator_checked`` and in the
settings file's ``fitted_generator_checked``.

**Why the mark rather than only the complaint.** The precedent is
``frame_interval_source``, two fields away: a sidecar that records only a value
cannot tell a measurement from a statement, so a 0.1 the page invented looked
exactly like a 0.1 the producer meant. ``generator_spec`` had the same hole. A
spec with nothing said about whether anybody compared it with the recording it
was aimed at reads as checked, because absent and fine are indistinguishable —
and every operating point downstream was fitted on that data.

**And it still refuses to judge.** No ``ok``, no threshold, no pass. It records
what happened — aimed at whom, at which K, compared or not — and where a
comparison exists it carries the ratios the panel already prints and already
introduces as "not a verdict and not a percentage error". That refusal is the
whole posture: insist the reader looks, then decline to decide for them, exactly
as the assessment refuses to pick K.
"""

from __future__ import annotations

from pathlib import Path

import pytest

VIEWER = Path(__file__).resolve().parents[1] / "docs/site/raster_viewer.html"

# 45 minutes split into baseline + drug, so the baseline clears the assessment's
# 15-minute floor and the accept step can aim the generator at it.
SIM = {"sRec": "2", "sMin": "45", "sRoi": "22", "sRate": "45", "sEv": "16",
       "sJit": "300", "sSeed": "5", "sWin": "2"}

# Anything that would make the record a ruling rather than a fact.
VERDICT_WORDS = ("ok", "pass", "fail", "acceptable", "good", "bad", "valid",
                 "verdict", "within_tolerance")


@pytest.fixture(scope="module")
def page():
    pytest.importorskip("playwright.sync_api",
                        reason="the mark is written by the running page")
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


ONE = """async () => {
  document.getElementById("dAll").checked = true;
  for (const k of Object.keys(DETECTORS))
    document.getElementById("dPick_" + k).checked = (k === "rate");
  paintDetectorChoice();
  await analyseFolder();
  return runJson(FOLDER_RUN).generator_checked;
}"""

AIM = """async () => {
  await show(RECORDINGS[0]);
  await runAssess();
  const b = [...document.querySelectorAll("#assessOut button")]
    .find(x => /Set the simulator/.test(x.textContent));
  b.click();
  await runSim();
  return SIM_TARGET ? SIM_TARGET.recId : null;
}"""


@pytest.fixture(scope="module")
def simulated(page):
    pg, errs = page
    pg.evaluate("""async (sim) => {
      for (const [k, v] of Object.entries(sim))
        document.getElementById(k).value = v;
      await runSim();
    }""", SIM)
    assert not errs, errs
    return pg


def test_a_data_set_nobody_aimed_says_there_was_nothing_to_check(simulated):
    got = simulated.evaluate(ONE)
    assert got["compared"] is False, got
    assert got["aimed_at"] is None, got
    assert "never aimed" in got["note"], got["note"]


def test_the_grumble_is_on_the_rail_before_any_of_this(page, simulated):
    """It must be impossible to skip Compare without noticing, and the rail is
    where noticing happens — the panel is one of nine and out of the column."""
    pg, _ = page
    aimed = pg.evaluate(AIM)
    assert aimed, "the accept step did not aim the generator"
    need = pg.eval_on_selector('#rail [data-step="accVerify"] .need',
                               "e => ({text: e.textContent, cls: e.className})")
    assert need["text"] == "not checked yet", need
    assert "nag" in need["cls"].split(), need
    assert "never compared with it" in pg.eval_on_selector(
        "#tuneUnchecked", "e => e.textContent")


def test_skipping_it_leaves_the_mark_and_the_mark_names_the_target(page):
    """The open question in the todo, answered. A `run.json` carrying a
    `generator_spec` and nothing about whether it was checked reads as checked,
    because absent and fine are indistinguishable — the same hole
    `frame_interval_source` was added to close."""
    pg, errs = page
    got = pg.evaluate(ONE)
    assert not errs, errs
    assert got["compared"] is False, got
    assert got["aimed_at"], got
    assert isinstance(got["at_k"], int), got
    assert "Compare step was not run" in got["note"], got["note"]


def test_the_mark_never_judges(page):
    """`verifySimulation` refuses to rule on whether the gap is acceptable
    because that depends on what the data set is for. A sidecar that ruled would
    put the verdict back, in the artifact that outlives the screen."""
    pg, _ = page
    got = pg.evaluate(ONE)
    for k in got:
        assert k.lower() not in VERDICT_WORDS, f"{k} is a ruling, not a fact"
    assert not any(w in got["note"].lower().split()
                   for w in ("acceptable", "wrong", "bad", "unusable")), got


def test_comparing_turns_the_mark_over_and_carries_the_ratios(page):
    pg, errs = page
    got = pg.evaluate("""async () => {
      await verifySimulation();
      document.getElementById("dAll").checked = true;
      for (const k of Object.keys(DETECTORS))
        document.getElementById("dPick_" + k).checked = (k === "rate");
      paintDetectorChoice();
      await analyseFolder();
      return {mark: runJson(FOLDER_RUN).generator_checked,
              need: document.querySelector('#rail [data-step="accVerify"] .need')
                      .textContent,
              nagHidden: document.getElementById("tuneUnchecked").hidden};
    }""")
    assert not errs, errs
    mark = got["mark"]
    assert mark["compared"] is True, mark
    assert mark["n_recordings_measured"] >= 1, mark
    # keyed the way `bugarach.assess` spells them, not the way this file does
    assert set(mark["simulated_over_real"]) == {
        "roi_rate_mean", "roi_rate_med", "clusters_permin", "part_n_obs",
        "jit_obs"}, mark["simulated_over_real"]
    assert got["need"].startswith("checked against "), got["need"]
    assert got["nagHidden"], "the complaint outlived the thing it complained of"
    for k in mark:
        assert k.lower() not in VERDICT_WORDS, f"{k} is a ruling, not a fact"


def test_the_settings_file_carries_it_too_because_that_is_what_crosses(page):
    """The sweep runs on invented recordings and the detector runs on real ones.
    The settings file is the only thing that travels between them, and
    `fitted_on` said WHICH data set without saying whether it was ever checked
    against the recording it was aimed at."""
    pg, errs = page
    got = pg.evaluate("""async (sim) => {
      /* Regenerating leaves `SIM_TARGET` — the measurement the generator is
         aimed at — and drops `VERIFY`, which was about the data set just
         replaced. So this is exactly the state the row exists for: aimed,
         swept, and never compared. */
      for (const [k, v] of Object.entries(sim))
        document.getElementById(k).value = v;
      await runSim();
      await show(RECORDINGS[0]);
      for (const k of Object.keys(DETECTORS))
        document.getElementById("tPick_" + k).checked = (k === "rate");
      await runTune();
      const go = [...document.querySelectorAll("#tuneOut button")]
        .find(b => /Use this setting/.test(b.textContent));
      if (go) await go.onclick();
      const pick = rows => rows.filter(r =>
        r.parameter === "fitted_generator_checked").map(r => r.value);
      const before = savedSettingsRows();
      await verifySimulation();
      return {applied: !!go, aimed: !!SIM_TARGET,
              before: pick(before), after: pick(savedSettingsRows()),
              fittedOn: before.filter(r => r.parameter === "fitted_on")
                              .map(r => r.value)[0]};
    }""", SIM)
    assert not errs, errs
    assert got["aimed"], "the generator lost its target across the regenerate"
    assert got["applied"], "the sweep produced no operating point to apply"
    assert got["before"] == ["no"], got["before"]
    assert got["after"] == ["yes"], got["after"]
    assert "simulated" in got["fittedOn"], got["fittedOn"]
    assert "aimed at" in got["fittedOn"], got["fittedOn"]


def test_a_folder_off_disk_says_nothing_rather_than_no(page):
    """There was no generator, so there is nothing to have checked. Null on the
    same rule `generator_spec` follows — a `false` here would read as a folder
    somebody failed to verify."""
    pg, _ = page
    got = pg.evaluate("""() => runJson({
      slices: [], frameIntervals: {}, frameSources: {}, thresholds: {},
    })""")
    assert got["generator_spec"] is None
    assert got["generator_checked"] is None
