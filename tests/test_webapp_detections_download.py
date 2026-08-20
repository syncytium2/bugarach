"""The browser writes `detections.csv`, and `bugarach.emit` has to be able to read it.

Until now nothing in this tree wrote a data file from the page: it detected, it
drew, and the reader left with a screenshot. The download is the step that turns
a screen into something a person keeps — which is also the step where a second
dialect of one table gets born, because the page cannot import `emit.py` and has
to carry its own copy of the contract.

So the bar here is not "the CSV looks right". It is that the file the browser
produced goes through `emit.read_detections` — the real reader, not a
reimplementation of it — and comes back with the values the page had on screen.
Anything the two spell differently shows up as a parse error or a changed number.

`docs/export_folder_spec.md` defines the shape; `src/bugarach/emit.py` implements
it; `tests/test_emit.py` fixes the round-trip rules these mirror:

  * a real zero survives as a zero, and only genuine absence becomes NA,
  * NaN is absence, because that is how the detectors spell "not applicable",
  * NA is spelled literally, so "no value" and "empty" cannot be confused,
  * line endings are newline only,
  * a detector that called nothing still writes a file with a header.

The mapping from a detector's own field names is the part most likely to be
wrong, and wrong quietly: RateDetect's strength is `amps`, which `rate.py`
defines as `freq_mean`, while the same returned object also carries `freqMax`.
Picking the wrong one produces a plausible column of numbers.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from bugarach.emit import COLUMNS, DETECTOR_FIELDS, NA, read_detections

VIEWER = Path(__file__).resolve().parents[1] / "docs/site/raster_viewer.html"

SIM = {"sRec": "1", "sMin": "20", "sRoi": "24", "sRate": "12", "sEv": "8",
       "sJit": "360", "sSeed": "7"}

# Detect, then hand back both the file the button would save and the numbers the
# page is holding, so the two can be compared without trusting either alone.
RUN = """async ({sim, which}) => {
  for (const [id, v] of Object.entries(sim)) document.getElementById(id).value = v;
  await runSim();
  document.getElementById("dDet").value = which;
  paintDetectorChoice();
  await runDetect();
  const btn = document.getElementById("saveDetections");
  return {
    csv: DETECT && DETECT.rows ? detectionsCsv(DETECT.rows) : null,
    rows: DETECT ? DETECT.rows.map(r => ({
      onset_sec: r.onset_sec, width_sec: r.width_sec,
      strength: r.strength, n_roi: r.n_roi,
      strength_unit: r.strength_unit, detector: r.detector, mode: r.mode,
    })) : [],
    buttonLabel: btn.textContent,
    buttonDisabled: btn.disabled,
    sliceId: DETECT ? DETECT.recId : null,
  };
}"""


@pytest.fixture(scope="module")
def viewer():
    pytest.importorskip("playwright.sync_api",
                        reason="writing the file needs the page that writes it")
    from playwright.sync_api import sync_playwright

    with sync_playwright() as p:
        try:
            browser = p.chromium.launch()
        except Exception as e:                        # noqa: BLE001
            pytest.skip(f"no chromium available: {type(e).__name__}")
        try:
            page = browser.new_page()
            errs: list[str] = []
            page.on("pageerror", lambda e: errs.append(str(e)))
            page.goto(VIEWER.as_uri())
            yield page, errs
        finally:
            browser.close()


def run(viewer, which: str) -> dict:
    page, errs = viewer
    out = page.evaluate(RUN, {"sim": SIM, "which": which})
    assert not errs, errs
    return out


@pytest.fixture(scope="module")
def rate(viewer):
    return run(viewer, "rate")


@pytest.fixture(scope="module")
def coact(viewer):
    return run(viewer, "coact")


def _read(tmp_path: Path, csv_text: str) -> list[dict]:
    """Through the library's own reader, never a second parser."""
    p = tmp_path / "detections.csv"
    p.write_text(csv_text, encoding="utf-8", newline="")
    return read_detections(p)


# ----------------------------------------------------- the file the library reads

def test_the_library_reads_what_the_browser_wrote(rate, tmp_path):
    assert rate["csv"], "the page produced no file at all"
    got = _read(tmp_path, rate["csv"])
    assert len(got) == len(rate["rows"]), (
        f"{len(rate['rows'])} rows on screen, {len(got)} read back")


def test_the_numbers_survive_the_trip(rate, tmp_path):
    got = _read(tmp_path, rate["csv"])
    for i, (a, b) in enumerate(zip(rate["rows"], got)):
        assert b["onset_sec"] == pytest.approx(a["onset_sec"]), f"row {i} onset"
        assert b["width_sec"] == pytest.approx(a["width_sec"]), f"row {i} width"
        assert b["strength"] == pytest.approx(a["strength"]), f"row {i} strength"


def test_the_columns_are_the_contract_in_the_contract_order(rate):
    header = rate["csv"].splitlines()[0].split(",")
    assert header[:len(COLUMNS)] == list(COLUMNS), header


def test_line_endings_are_newline_only(rate):
    assert "\r" not in rate["csv"]
    assert rate["csv"].endswith("\n")


# --------------------------------------------------------- the per-detector map

def test_the_strength_unit_is_the_one_emit_declares(rate, coact):
    for out, name in ((rate, "rate"), (coact, "coact")):
        want = DETECTOR_FIELDS[name].strength_unit
        units = {r["strength_unit"] for r in out["rows"]}
        assert units <= {want}, f"{name}: {units} != {want}"


def test_rate_reports_no_participation_and_spells_it_NA(rate, tmp_path):
    """`n_roi` is None for RateDetect alone — a fact about the detector, not a
    gap. It has to reach the file as NA and come back as None."""
    assert DETECTOR_FIELDS["rate"].n_roi is None
    body = rate["csv"].splitlines()[1:]
    if not body:
        pytest.skip("this seed produced no rate detections to check")
    col = list(COLUMNS).index("n_roi")
    assert {ln.split(",")[col] for ln in body} == {NA}
    assert all(r["n_roi"] is None for r in _read(tmp_path, rate["csv"]))


def test_a_detector_that_reports_participation_writes_a_number(coact, tmp_path):
    assert DETECTOR_FIELDS["coact"].n_roi == "nrois"
    got = _read(tmp_path, coact["csv"])
    if not got:
        pytest.skip("this seed produced no coact detections to check")
    assert all(isinstance(r["n_roi"], int) for r in got), got[:2]


def test_the_mode_is_threshold_because_the_page_has_no_peak_branch(rate, coact):
    for out in (rate, coact):
        assert {r["mode"] for r in out["rows"]} <= {"threshold"}


# ------------------------------------------------------------------ the button

def test_the_button_is_dead_until_there_is_something_to_save(viewer):
    """It must not offer a file describing the previous detector."""
    page, _ = viewer
    state = page.evaluate("""() => {
      clearDetect();
      const b = document.getElementById("saveDetections");
      return {disabled: b.disabled, label: b.textContent};
    }""")
    assert state["disabled"] is True
    assert "(" not in state["label"], state["label"]


def test_the_button_counts_the_rows_it_would_write(rate):
    assert rate["buttonDisabled"] is False
    assert f"({len(rate['rows'])} row" in rate["buttonLabel"], rate["buttonLabel"]


def test_the_file_is_named_for_the_recording(rate):
    assert rate["sliceId"], "no recording id to name the file after"


# ------------------------------------------------- zero, absence, and quoting

QUIRKS = """() => {
  const rows = [{
    slice_id: 'a,b', stream: 'fast', detector: 'rate', mode: 'threshold',
    region_idx: null, region_label: 'he said "hi"',
    onset_sec: 0, width_sec: NaN, width_def: null,
    n_roi: null, strength: 0.0, strength_unit: 'u',
    identity: {note: ''},
  }];
  return detectionsCsv(rows);
}"""


def test_a_real_zero_stays_a_zero_and_a_nan_becomes_absence(viewer, tmp_path):
    """The two failure modes `emit._fmt` exists to keep apart, in one row."""
    page, errs = viewer
    csv_text = page.evaluate(QUIRKS)
    assert not errs, errs
    got = _read(tmp_path, csv_text)[0]
    assert got["onset_sec"] == 0.0, "a real zero was lost"
    assert got["strength"] == 0.0, "a real zero was lost"
    assert got["width_sec"] is None, "NaN should read back as absence"
    assert got["width_def"] is None
    assert got["region_idx"] is None


def test_an_empty_identity_value_is_absence_not_an_empty_string(viewer, tmp_path):
    page, _ = viewer
    got = _read(tmp_path, page.evaluate(QUIRKS))[0]
    assert got["note"] is None


def test_commas_and_quotes_survive_being_written(viewer, tmp_path):
    """If quoting is wrong the row silently gains a column, which a reader
    notices only as a shifted value somewhere else entirely."""
    page, _ = viewer
    got = _read(tmp_path, page.evaluate(QUIRKS))[0]
    assert got["slice_id"] == "a,b"
    assert got["region_label"] == 'he said "hi"'


def test_a_detector_that_called_nothing_still_writes_a_header(viewer):
    """An empty result is a finding; an absent one is a bug. They must not look
    alike, so the file exists with its header and no rows."""
    page, _ = viewer
    csv_text = page.evaluate("() => detectionsCsv([])")
    assert csv_text.splitlines() == [",".join(COLUMNS)]
    assert csv_text.endswith("\n")
