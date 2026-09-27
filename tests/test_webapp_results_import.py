"""The viewer opens a results file beside the folder and draws its calls above the raster.

Tony, 2026-09-26: easy access to the zoomable rasters with the detections on — "point
the website at the cli results". The page could write ``detections.csv`` and could not
read one back, while two comments in it said an old file "still draws here".

What is pinned, each against a synthetic folder written here (never real data — the
repo is public):

* a ``detections.csv`` inside the folder is read as results, and neither it nor the
  other result files becomes a recording;
* the calls join the recording on ``slice_id``, one lane per detector × variant for the
  stream on screen, and every mark sits ABOVE the raster (nothing is drawn on it);
* every way the join can fail is said beside the raster, not in a console;
* a file in neither shape is refused with its missing columns named;
* ``#slice=<id>&stream=<name>`` goes to that recording once the folder is open;
* the file this page itself saves opens again.

The results file is written by ``bugarach.emit.write_detections`` — the library's own
writer — so the page is tested against the contract rather than against a copy of it.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from bugarach.emit import DetectedEvent, write_detections

VIEWER = Path(__file__).resolve().parents[1] / "docs/site/raster_viewer.html"

RECS = ("rec_a", "rec_b")
STREAMS = ("fast", "slow")

# (slice, stream, detector, variant, onset, width, n_roi) — rec_a carries three lanes on
# fast and one on slow; rec_b one lane on each.
CALLS = [
    ("rec_a", "fast", "coact", "own_floor", 40.0, 2.0, 5),
    ("rec_a", "fast", "coact", "own_floor", 140.0, 1.5, 4),
    ("rec_a", "fast", "coact", "baseline_floor", 40.0, 2.0, 5),
    ("rec_a", "fast", "chorus_norm", "unfloored", 200.0, 3.0, 6),
    ("rec_a", "slow", "rate", "unfloored", 60.0, 4.0, None),
    ("rec_b", "fast", "sync", "own_floor", 100.0, 1.0, 3),
    ("rec_b", "slow", "coact", "baseline_floor", 300.0, 2.5, 4),
]


def _recording(path: Path, shift: float) -> None:
    rows = ["roi,time_sec,stream"]
    for stream in STREAMS:
        for roi in range(1, 7):
            for k in range(1, 30):
                rows.append(f"{roi},{k * 20 + roi * 0.05 + shift:.2f},{stream}")
    path.write_text("\n".join(rows) + "\n", encoding="utf-8")


def _events(calls) -> list[DetectedEvent]:
    return [DetectedEvent(slice_id=s, stream=st, detector=d, mode="threshold",
                          onset_sec=on, width_sec=w, strength=None, strength_unit=None,
                          region_idx=0, region_label="baseline", n_roi=n,
                          identity={"variant": v, "own_floor": "3"})
            for s, st, d, v, on, w, n in calls]


def _folder(root: Path, name: str, *, results=True, extras=True) -> Path:
    d = root / name
    d.mkdir()
    for i, rec in enumerate(RECS):
        _recording(d / f"{rec}.csv", i * 0.3)
    (d / "slices.csv").write_text(
        "slice_id,frame_interval_sec\n" + "".join(f"{r},0.1\n" for r in RECS),
        encoding="utf-8")
    (d / "regions.csv").write_text(
        "slice_id,region_idx,label,start_sec,end_sec\n"
        + "".join(f"{r},0,baseline,0,600\n" for r in RECS), encoding="utf-8")
    if results:
        write_detections(_events(CALLS), d / "detections.csv")
    if extras:
        # the other result files a run leaves: none of them is a recording either
        (d / "calls.csv").write_text("slice_id,variant,participants,label,window_kind\n",
                                     encoding="utf-8")
        (d / "windows.csv").write_text("slice_id,variant\n", encoding="utf-8")
        (d / "detector_settings.csv").write_text("detector,stream,parameter,value\n",
                                                 encoding="utf-8")
    return d


@pytest.fixture(scope="module")
def browser():
    pytest.importorskip("playwright.sync_api", reason="the viewer needs a browser")
    from playwright.sync_api import sync_playwright

    with sync_playwright() as p:
        try:
            b = p.chromium.launch()
        except Exception as e:                        # noqa: BLE001
            pytest.skip(f"no chromium available: {type(e).__name__}")
        try:
            yield b
        finally:
            b.close()


def _page(browser, hash_: str = ""):
    pg = browser.new_page(viewport={"width": 1300, "height": 900})
    errs: list[str] = []
    pg.on("pageerror", lambda e: errs.append(str(e)))
    # no invented folder on load: the tests open their own
    pg.add_init_script("try { localStorage.setItem('bugarach.demo', 'off'); } catch (e) {}")
    pg.goto(VIEWER.as_uri() + hash_, wait_until="load")
    return pg, errs


def _open(pg, folder: Path) -> None:
    pg.set_input_files("#files", [str(q) for q in sorted(folder.iterdir())])
    pg.wait_for_function("() => RECORDINGS.length > 0 && current && current.loaded",
                         timeout=30000)


def _results(pg, path: Path) -> None:
    """Pick a results file, and wait until the note beside the raster is about it."""
    pg.set_input_files("#resultsFile", str(path))
    pg.wait_for_function(
        "name => !document.getElementById('importNote').hidden"
        " && document.getElementById('importNote').innerText.includes(name)",
        arg=path.name, timeout=30000)


STATE = """() => ({
  recordings: RECORDINGS.map(r => r.id),
  current: current && current.id,
  stream: STREAM,
  imported: IMPORTED && {name: IMPORTED.name, how: IMPORTED.how, rows: IMPORTED.rows.length},
  refusal: IMPORT_REFUSAL,
  lanes: current && current.loaded
    ? importLanes(current, shownStreams(current.loaded)).map(importLabel) : [],
  hits: IMPORT_HITS.map(h => ({y: h.y, top: h.panelTop, slice: h.row.slice,
                               stream: h.row.stream})),
  note: document.getElementById("importNote").hidden ? null
        : document.getElementById("importNote").innerText,
  noteErr: document.querySelectorAll("#importNote .err").length,
  resultsWhat: document.getElementById("resultsWhat").innerText,
  viewShown: !document.getElementById("view").hidden,
})"""


def test_a_results_file_in_the_folder_is_read_as_results_not_as_a_recording(browser, tmp_path):
    pg, errs = _page(browser)
    _open(pg, _folder(tmp_path, "export"))
    s = pg.evaluate(STATE)
    assert not errs, errs
    assert s["recordings"] == list(RECS), (
        f"a result file was read as a recording: {s['recordings']}")
    assert s["imported"] == {"name": "detections.csv", "how": "found in the folder",
                             "rows": len(CALLS)}
    # a folder holding results is opened for them: the single-recording view, not turbo
    assert s["viewShown"]


def test_calls_join_on_slice_id_one_lane_per_detector_and_variant_above_the_raster(
        browser, tmp_path):
    pg, errs = _page(browser)
    _open(pg, _folder(tmp_path, "export"))
    s = pg.evaluate(STATE)
    assert s["current"] == "rec_a" and s["stream"] == "fast"
    # three lanes for rec_a on fast, in registry order then variant order, counts in the label
    assert s["lanes"] == ["coact · own_floor · 2 calls", "coact · baseline_floor · 1 call",
                          "chorus_norm · unfloored · 1 call"], s["lanes"]
    assert len(s["hits"]) == 4
    assert {(h["slice"], h["stream"]) for h in s["hits"]} == {("rec_a", "fast")}
    for h in s["hits"]:
        assert h["y"] < h["top"], f"an imported mark at y={h['y']} is on the raster (top {h['top']})"
    assert s["noteErr"] == 0 and "Imported from detections.csv: 4 calls" in s["note"]

    # the other recording joins on its own id, and only on its own rows
    pg.evaluate("() => show(RECORDINGS.find(r => r.id === 'rec_b'))")
    s = pg.evaluate(STATE)
    assert s["current"] == "rec_b"
    assert s["lanes"] == ["sync · own_floor · 1 call"]
    assert [(h["slice"], h["stream"]) for h in s["hits"]] == [("rec_b", "fast")]

    # switching stream redraws that stream's lanes
    pg.evaluate("() => chooseStream('slow')")
    pg.wait_for_function("() => IMPORT_HITS.length === 1 && IMPORT_HITS[0].row.stream === 'slow'")
    assert not errs, errs


def test_the_hover_shows_what_the_row_carries(browser, tmp_path):
    pg, errs = _page(browser)
    _open(pg, _folder(tmp_path, "export"))
    tip = pg.evaluate("() => importTip(IMPORT_HITS[0])")
    assert "imported" in tip and "participants (n_roi) 5 ROIs" in tip
    assert "own_floor 3" in tip and "region_label baseline" in tip
    # and it appears under the pointer
    box = pg.locator("#cv").bounding_box()
    h = pg.evaluate("() => IMPORT_HITS[0]")
    pg.mouse.move(box["x"] + h["x"], box["y"] + h["y"])
    assert pg.locator("#impTip").is_visible()
    assert not errs, errs


def test_results_for_recordings_the_folder_does_not_hold_are_refused_visibly(browser, tmp_path):
    folder = _folder(tmp_path, "export", results=False)
    stranger = tmp_path / "stranger_detections.csv"
    write_detections(_events([("rec_z", "fast", "coact", "own_floor", 10.0, 1.0, 4)]), stranger)

    pg, errs = _page(browser)
    _open(pg, folder)
    _results(pg, stranger)
    s = pg.evaluate(STATE)
    assert s["hits"] == []
    assert s["noteErr"] >= 1 and "None of the 1 recording named in stranger_detections.csv" \
        in s["note"], s["note"]

    # partly matching: the stranger is named, and a recording with no rows says so
    mixed = tmp_path / "mixed.csv"
    write_detections(_events([("rec_a", "fast", "coact", "own_floor", 10.0, 1.0, 4),
                              ("rec_z", "fast", "coact", "own_floor", 10.0, 1.0, 4)]), mixed)
    _results(pg, mixed)
    s = pg.evaluate(STATE)
    assert "1 recording named in mixed.csv is not in this folder" in s["note"], s["note"]
    assert "rec_z" in s["note"]
    pg.evaluate("() => show(RECORDINGS.find(r => r.id === 'rec_b'))")
    s = pg.evaluate(STATE)
    assert "mixed.csv has no rows for rec_b" in s["note"], s["note"]
    assert s["noteErr"] >= 2
    assert pg.locator("#importNote").is_visible()

    # calls only on the stream that is not on screen
    slow_only = tmp_path / "slow_only.csv"
    write_detections(_events([("rec_a", "slow", "coact", "own_floor", 10.0, 1.0, 4)]),
                     slow_only)
    _results(pg, slow_only)
    pg.evaluate("() => show(RECORDINGS.find(r => r.id === 'rec_a'))")
    s = pg.evaluate(STATE)
    assert "none on fast, the stream on screen" in s["note"], s["note"]
    assert not errs, errs


def test_a_file_in_neither_shape_is_refused_naming_its_missing_columns(browser, tmp_path):
    folder = _folder(tmp_path, "export", results=False)
    calls = tmp_path / "calls.csv"
    calls.write_text(
        "slice_id,group,region_idx,label,window_kind,stream,detector,variant,onset_sec,"
        "width_sec,participants,own_floor,baseline_floor\n"
        "rec_a,DI,0,baseline,baseline,fast,coact,own_floor,40.0,2.0,5,3,3\n",
        encoding="utf-8")
    pg, errs = _page(browser)
    _open(pg, folder)
    _results(pg, calls)
    s = pg.evaluate(STATE)
    assert s["imported"] is None and s["hits"] == []
    for col in ("mode", "region_label", "width_def", "n_roi", "strength", "strength_unit"):
        assert col in s["refusal"], f"the refusal does not name {col}: {s['refusal']}"
    assert "--detections-from" in s["refusal"]
    # said in the panel and beside the raster, not only held in a variable
    assert "is not a detections.csv" in s["resultsWhat"]
    assert "is not a detections.csv" in (s["note"] or "")
    assert not errs, errs


def test_a_deep_link_goes_to_its_recording_and_stream_once_the_folder_is_open(browser, tmp_path):
    folder = _folder(tmp_path, "export")
    pg, errs = _page(browser, "#slice=rec_b&stream=slow")
    # before a folder is open, the page says what the link is waiting for
    assert "This link opens recording rec_b on stream slow" in pg.inner_text("#resultsWhat")
    _open(pg, folder)
    pg.wait_for_function("() => current && current.id === 'rec_b' && STREAM === 'slow'",
                         timeout=30000)
    s = pg.evaluate(STATE)
    assert s["viewShown"]
    assert [(h["slice"], h["stream"]) for h in s["hits"]] == [("rec_b", "slow")]

    # a link naming a recording the folder does not hold says so beside the raster
    pg.evaluate("() => { location.hash = 'slice=rec_nope'; }")
    pg.wait_for_function("() => DEEP && DEEP.slice === 'rec_nope' && DEEP.missing === true")
    s = pg.evaluate(STATE)
    assert "The link asks for recording rec_nope, which is not in this folder" in s["note"]
    assert not errs, errs


def test_the_file_this_page_saves_opens_again(browser):
    """Round trip through the page's own writer: detect on a simulated recording, save
    the rows the Save button would, read them back with the reader."""
    pg, errs = _page(browser)
    got = pg.evaluate("""async () => {
      await runSim();
      document.getElementById("dDet").value = "rate";
      paintDetectorChoice();
      await runDetect();
      const csv = detectionsCsv(DETECT.rows);
      const back = parseResults(csv, "detections.csv");
      return {saved: DETECT.rows.length, read: back.rows.length,
              slices: [...back.bySlice.keys()], id: DETECT.recId};
    }""")
    assert got["saved"] > 0 and got["read"] == got["saved"]
    assert got["slices"] == [got["id"]]
    assert not errs, errs
