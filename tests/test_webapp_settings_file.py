"""A run can be specified, not just performed.

The page could run six detectors over a folder and hand back a table of times.
It could not hand back **what produced them**. Three linked gaps, all of them
about the same missing document:

  * it wrote `detections.csv` and `run.json` and no `detector_settings.csv`, so
    a result did not reproduce from the folder alone — which is the one job the
    output contract gives that file (`docs/export_folder_spec.md`);
  * `run.json`'s `thresholds` were keyed by detector with no stream, while
    `emit.detector_settings_rows` keys by `(detector, stream)` for the reason
    its docstring gives: *"a detector may run with different settings on the
    fast and slow streams, and a table that could not say so would make one of
    the two unreproducible"*;
  * a fitted setting lived in `TUNED`, a module variable deliberately kept alive
    across `open` so it could reach a second folder. A number with no file has
    no provenance, and the sequence that depended on it — tune on invented data,
    reopen your own recordings, detect — appeared nowhere on screen.

**Test the screen, not the function.** A bug shipped in this page because every
test read a data structure and none pressed a button; so everything below drives
the page, and the two files it writes are parsed by
`bugarach.emit.read_detector_settings` — the same reader a consumer downstream
uses — rather than by a second parser written to agree with the first.
"""

from __future__ import annotations

import random
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
VIEWER = ROOT / "docs/site/raster_viewer.html"


# ---------------------------------------------------------------- the folders

def _rows(rois, dur, rate_hz, seed):
    rng = random.Random(seed)
    out = []
    for r in rois:
        t = 0.0
        while True:
            t += rng.expovariate(rate_hz)
            if t >= dur:
                break
            out.append((r, round(t, 4)))
    return out


def _coordinated(rois, centres, jitter, spread, seed):
    rng = random.Random(seed)
    return [(r, round(c + rng.uniform(-jitter, jitter), 4))
            for c in centres for r in rois[:spread]]


def two_stream_csv(dur=1200.0, n_roi=20):
    """One recording, two streams, unequal coordination in each.

    Unequal on purpose: a page that analysed one stream and wrote the other's
    name would still produce a plausible table, and equal counts under the two
    choices would not catch it.
    """
    rois = [f"r{i:02d}" for i in range(1, n_roi + 1)]
    rows = []
    for roi, t in _coordinated(rois, [90.0, 200.0, 310.0, 420.0, 530.0, 640.0],
                               0.05, 14, 11):
        rows.append((roi, t, "fast"))
    for roi, t in _rows(rois, dur, 0.010, 12):
        rows.append((roi, t, "fast"))
    for roi, t in _coordinated(rois, [150.0, 480.0, 700.0], 0.30, 14, 21):
        rows.append((roi, t, "slow"))
    for roi, t in _rows(rois, dur, 0.008, 22):
        rows.append((roi, t, "slow"))
    rows.sort(key=lambda r: (r[2], r[0], r[1]))
    return "roi,time_sec,stream\n" + "".join(f"{r},{t},{s}\n" for r, t, s in rows)


def one_stream_csv(dur=1200.0, n_roi=20):
    rois = [f"r{i:02d}" for i in range(1, n_roi + 1)]
    rows = _coordinated(rois, [90.0, 200.0, 310.0, 420.0, 530.0], 0.05, 14, 11)
    rows += _rows(rois, dur, 0.010, 12)
    rows.sort()
    return "roi,time_sec\n" + "".join(f"{r},{t}\n" for r, t in rows)


def _folder(csv_text, sid="s1"):
    return [{"name": f"{sid}.csv", "text": csv_text},
            {"name": "slices.csv",
             "text": f"slice_id,frame_interval_sec\n{sid},0.1\n"}]


# ---------------------------------------------------------------- the browser

@pytest.fixture(scope="module")
def page():
    pytest.importorskip("playwright.sync_api",
                        reason="the settings file is written in the page")
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
            # The page simulates a folder on load, asynchronously; opening one
            # of ours before that settles races it.
            pg.wait_for_function(
                "() => document.getElementById('demoNote') && "
                "!document.getElementById('demoNote').hidden", timeout=120000)
            yield pg, errs
        finally:
            browser.close()


OPEN = """async (files) => {
  await open(files, {quiet: true});
  return {recs: RECORDINGS.length, stream: STREAM, seen: STREAMS_SEEN};
}"""

PICK = """async (name) => {
  const sel = document.getElementById("sStream");
  sel.value = name;
  sel.dispatchEvent(new Event("change", {bubbles: true}));
  await new Promise(r => setTimeout(r, 50));
  return STREAM;
}"""

RUN_FOLDER = """async () => {
  // Every detector, asked for rather than assumed: the folder run reads the
  // tick list now, and three of the six are unticked by default.
  document.getElementById("dAll").checked = true;
  for (const k of Object.keys(DETECTORS))
    document.getElementById("dPick_" + k).checked = true;
  paintDetectorChoice();
  await analyseFolder();
  return {settings: settingsCsv(runSettingsRows(FOLDER_RUN.thresholds)),
          // THE OTHER SETTINGS ROUTE — what the reader has typed, over the whole
          // registry, rather than what this run happened to execute. It is where
          // a detector the build withholds can still be checked for the shape of
          // its rows, which is why the SPIKE-synch grid guard below reads it.
          saved: settingsCsv(savedSettingsRows()),
          run: runJson(FOLDER_RUN),
          rows: FOLDER_RUN.rows.length,
          saveEnabled: !document.getElementById("saveSettingsCsv").disabled};
}"""


def _settings(text, tmp_path, name="detector_settings.csv"):
    from bugarach import emit

    p = tmp_path / name
    p.write_text(text, encoding="utf-8")
    return emit.read_detector_settings(p)


# --------------------------------------------- gap 1 and 2: the run's settings

@pytest.fixture(scope="module")
def ran(page):
    pg, errs = page
    pg.evaluate(OPEN, _folder(two_stream_csv()))
    pg.evaluate(PICK, "slow")
    got = pg.evaluate(RUN_FOLDER)
    assert not errs, errs
    return got


def test_the_folder_run_offers_a_detector_settings_file(ran):
    """The button, not the function. It writes `detections.csv` and `run.json`
    and now the third file the contract asks for."""
    assert ran["saveEnabled"], (
        "the folder run finished and the settings file could not be saved")


def test_the_settings_read_back_through_the_library_keyed_by_detector_and_stream(
        ran, tmp_path):
    """One dialect, not two. `emit.read_detector_settings` is what a consumer
    downstream uses; a file it cannot parse is a second dialect of one table."""
    got = _settings(ran["settings"], tmp_path)
    assert got, "read_detector_settings got nothing out of the browser's file"
    # FOUR, NOT SIX. `sync` (2026-08-24) and `cicada` (2026-08-29) both carry
    # `unavailable`, so nothing on
    # the page can tick it and no run produces settings rows for it. A row here
    # would say a detector ran when it did not — the settings file records what
    # this run executed, not what the registry holds.
    assert set(got) == {("rate", "slow"), ("sce", "slow"), ("coact", "slow"),
                        ("loco", "slow")}, (
        f"the keys are not (detector, stream) pairs for the run: {sorted(got)}")
    assert ("sync", "slow") not in got, (
        "SPIKE-synch is off in this build and must not appear in a settings "
        "file describing a run it could not take part in")


def test_every_detector_that_ran_records_the_parameters_it_ran_with(ran, tmp_path):
    got = _settings(ran["settings"], tmp_path)
    assert got[("rate", "slow")].keys() >= {
        "excessThresholdHz", "rateWin", "contextWin"}, got[("rate", "slow")]
    assert got[("coact", "slow")].keys() >= {
        "alpha", "intWinSec", "contextWinSec", "nSurrogates"}


def test_the_settings_do_not_carry_a_per_recording_frame_interval(ran, tmp_path):
    """`gridDt` varies per recording and `run.json` records it per slice, under
    `frame_interval_sec`, where it is correct. A single value in a run-wide row
    would read as a fact about the run and be a fact about the loop."""
    got = _settings(ran["settings"], tmp_path)
    for key, params in got.items():
        assert "gridDt" not in params, (
            f"{key} carries a frame interval in a run-wide settings row")


def test_spike_synch_records_the_grid_it_actually_used(ran, tmp_path):
    """The parameter that shapes the answer and was recorded nowhere.

    Five detectors take the acquisition frame interval and drop it from these
    rows because `frame_interval_sec` carries it per slice. SPIKE-synch's bin is
    not that quantity — `sync.py` names it `PROFILE_BIN_SEC` and argues that
    nothing upstream of the binning touches a grid, so it is the resolution of
    the detector and the width its hysteresis thresholds were calibrated at.
    Dropping it left SPIKE-synch the one detector whose settings rows named no
    grid at all.

    **Read off the saved-settings route rather than the run**, since 2026-08-24:
    the detector is off in this build, so no run produces rows for it, and the
    guard would otherwise vanish with the thing it guards — waiting to be
    rediscovered the day somebody turns it back on. `savedSettingsRows()` covers
    the whole registry, which is what makes it the right place for a fact about
    the shape of a detector's rows rather than about a particular run.
    """
    got = _settings(ran["saved"], tmp_path)
    sync = got[("sync", "slow")]
    assert "profileBinSec" in sync, (
        "SPIKE-synch's settings rows name no grid, and its grid is a parameter "
        f"of the detector rather than of the recording: {sync}")
    assert float(sync["profileBinSec"]) == pytest.approx(0.1)


def test_the_run_sidecar_keys_its_thresholds_by_detector_and_stream(ran):
    """The gap a comment in the page used to admit to."""
    th = ran["run"]["thresholds"]
    assert set(th) >= {"rate", "coact", "loco", "sce"}, sorted(th)
    for name, by_stream in th.items():
        assert isinstance(by_stream, dict) and by_stream, name
        assert set(by_stream) == {"slow"}, (
            f"{name}'s thresholds are keyed {sorted(by_stream)} — the export "
            "contract keys settings by detector AND stream, and a sidecar that "
            "cannot say which stream makes one of the two unreproducible")


def test_the_run_sidecar_names_the_stream_the_whole_run_is_about(ran):
    assert ran["run"]["stream"] == "slow", ran["run"].get("stream")


# ----------------------------------- gap 3: a fast value cannot run on slow

def test_a_value_fitted_on_one_stream_stops_claiming_the_other(page):
    """The before and after, on screen.

    Apply a setting while `fast` is in play, then move the door to `slow`. The
    number stays in the box — silently rewriting somebody's choice would be
    worse — and every claim that a sweep chose it for what is being analysed
    now has to be gone, replaced by a sentence saying where it came from.
    """
    pg, errs = page
    pg.evaluate(OPEN, _folder(two_stream_csv()))
    pg.evaluate(PICK, "fast")
    before = pg.evaluate("""() => {
      useTunedSetting("rate", 2.5, {knobName: "excess threshold", unit: "Hz",
        f1: 0.81, nFolds: 3, dataSetN: 3, tolSec: 1.5, heldOut: true});
      return {chip: document.getElementById("tunedWhat").textContent,
              claims: !!tunedFor("rate"),
              box: document.getElementById("dThr").value};
    }""")
    assert before["claims"], "the setting was not recorded as chosen at all"
    assert "stream fast" in before["chip"], before["chip"]

    after = pg.evaluate("""async () => {
      const sel = document.getElementById("sStream");
      sel.value = "slow";
      sel.dispatchEvent(new Event("change", {bubbles: true}));
      await new Promise(r => setTimeout(r, 50));
      return {chip: document.getElementById("tunedWhat").textContent,
              claims: !!tunedFor("rate"),
              box: document.getElementById("dThr").value};
    }""")
    assert after["box"] == before["box"], (
        "the control was silently rewritten when the stream changed")
    assert not after["claims"], (
        "a value fitted on fast still claims to be the chosen setting for slow")
    chip = after["chip"]
    assert "fitted on fast" in chip and "analysing slow" in chip, (
        f"nothing on screen says the number came from the other stream: {chip!r}")
    assert not errs, errs


def test_a_settings_file_fitted_on_one_stream_is_refused_on_the_other(page):
    """The hard gate, and the reason it can exist at all.

    Because the stream is chosen at the door, a settings file knows which stream
    it belongs to and the page knows which is in play. FOUNDATIONS §9: the two
    move in opposite directions under the same drug, so applying one's threshold
    to the other is a different answer, not a rougher one — it is refused, with
    the way through named in the refusal.
    """
    pg, errs = page
    pg.evaluate(OPEN, _folder(two_stream_csv()))
    pg.evaluate(PICK, "fast")
    saved = pg.evaluate("() => settingsCsv(savedSettingsRows())")
    refused = pg.evaluate("""async (text) => {
      const sel = document.getElementById("sStream");
      sel.value = "slow";
      sel.dispatchEvent(new Event("change", {bubbles: true}));
      await new Promise(r => setTimeout(r, 50));
      return applySettings(parseSettingsCsv(text));
    }""", saved)
    assert refused.get("why"), (
        "a settings file fitted on fast was applied while slow was in play")
    assert "fast" in refused["why"] and "slow" in refused["why"], refused["why"]
    assert not errs, errs


# --------------------------------- gap 4: settings are a file, with provenance

def test_a_saved_settings_file_names_the_data_set_it_was_fitted_on(page,
                                                                   tmp_path):
    """A settings file that cannot say what it was fitted on is a number with no
    provenance. The provenance rides in the same four columns under a
    `fitted_` prefix, so one reader parses both files."""
    pg, errs = page
    pg.evaluate(OPEN, _folder(two_stream_csv()))
    pg.evaluate(PICK, "fast")
    pg.evaluate("""() => useTunedSetting("rate", 3.5,
      {knobName: "excess threshold", unit: "Hz", f1: 0.77, nFolds: 4,
       dataSetN: 6, tolSec: 1.5, heldOut: true})""")
    saved = pg.evaluate("() => settingsCsv(savedSettingsRows())")
    got = _settings(saved, tmp_path, "bugarach_settings.csv")
    rate = got[("rate", "fast")]
    assert rate["fitted_on"], "the file does not say what it was fitted on"
    assert rate["fitted_by"] == "sweep", rate
    assert float(rate["fitted_f1"]) == pytest.approx(0.77)
    assert float(rate["fitted_tolerance_sec"]) == pytest.approx(1.5)
    assert float(rate["excessThresholdHz"]) == pytest.approx(3.5)
    # A detector nobody swept says so rather than implying a fit
    assert got[("sce", "fast")]["fitted_by"] == "hand"
    assert not errs, errs


def test_the_file_name_says_which_data_set_too(page):
    """Tony: "tuned settings should be saved with a file name associated with
    the simulated folder or the user folder". Two of these on a disk are told
    apart by reading their names."""
    pg, errs = page
    pg.evaluate(OPEN, _folder(one_stream_csv()))
    loose = pg.evaluate("() => settingsFileName()")
    assert loose.startswith("bugarach_settings_") and loose.endswith(".csv"), loose
    # A directory pick knows the folder's own name; a loose-file pick does not,
    # and the sentence inside the file says so rather than inventing one.
    named = pg.evaluate("""() => {
      FOLDER_NAME = "2026-08-18_revised_2v_periods";
      return {file: settingsFileName(), where: dataSetName()};
    }""")
    assert "2026-08-18_revised_2v_periods" in named["file"], named
    assert "2026-08-18_revised_2v_periods" in named["where"], named
    assert not errs, errs


def test_settings_do_not_survive_a_folder_change_and_the_file_is_how_they_travel(
        page):
    """The replacement for `TUNED` outliving `open`.

    The old arrangement kept a fitted value alive across the folder swap, which
    is the one moment this page throws work away — so the step that made the
    whole loop work was invisible. Now nothing carries over, and the file does
    the carrying. Both halves are checked here, because only the second makes
    the first safe.
    """
    pg, errs = page
    pg.evaluate(OPEN, _folder(one_stream_csv()))
    pg.evaluate("""() => useTunedSetting("rate", 4.25,
      {knobName: "excess threshold", unit: "Hz", f1: 0.7, nFolds: 2,
       dataSetN: 3, tolSec: 1.5})""")
    saved = pg.evaluate("() => settingsCsv(savedSettingsRows())")

    gone = pg.evaluate(OPEN + "", _folder(one_stream_csv(), sid="s2"))
    assert gone["recs"] == 1
    after = pg.evaluate("""() => ({tuned: Object.keys(TUNED).length,
                                   box: document.getElementById("dThr").value,
                                   chip: document.getElementById("tunedWhat").textContent})""")
    assert after["tuned"] == 0, (
        "a fitted setting survived a folder change; nothing on screen said so, "
        "which is the failure the settings file replaces")

    loaded = pg.evaluate("""(text) => {
      const parsed = parseSettingsCsv(text);
      const got = applySettings(parsed);
      return {why: got.why || null, n: (got.set || []).length,
              fittedOn: got.fittedOn,
              box: document.getElementById("dThr").value};
    }""", saved)
    assert not loaded["why"], loaded
    assert float(loaded["box"]) == pytest.approx(4.25), (
        "loading the file did not put the value back in the control")
    assert loaded["fittedOn"], "the loaded file said nothing about its origin"
    assert not errs, errs


def test_a_folder_csv_picked_by_mistake_says_so(page):
    """Every wrong file this page can be handed has to answer in words. A
    recording opened as a settings file is the obvious slip."""
    pg, errs = page
    got = pg.evaluate("(t) => parseSettingsCsv(t)", one_stream_csv())
    assert got.get("why"), "a recording was accepted as a settings file"
    assert "detector" in got["why"], got["why"]
    assert not errs, errs


def test_every_detector_can_write_and_read_back_every_parameter_it_exposes(page):
    """Without this a setting can be saved and never loaded, which is a file
    that looks like provenance and is not. Derived from the registry, so a
    seventh detector is covered without being remembered."""
    pg, errs = page
    missing = pg.evaluate("""() => {
      const out = [];
      for (const [k, D] of Object.entries(DETECTORS)) {
        const cfg = D.read(0.1);
        for (const name of Object.keys(cfg)) {
          if (name === "gridDt") continue;
          const known = (D.params && D.params[name])
                     || (D.fixed || []).includes(name);
          if (!known) out.push(k + "." + name);
        }
        for (const name of Object.keys(D.params || {})) {
          const spec = D.params[name];
          const id = typeof spec === "string" ? spec : spec.input;
          if (!document.getElementById(id)) out.push(k + "." + name + " -> " + id);
        }
      }
      return out;
    }""")
    assert missing == [], (
        f"these settings can be written and never read back: {missing}")
    assert not errs, errs
