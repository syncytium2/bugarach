"""Smoke tests for the Panel viewer: builds headlessly against the canonical
two-stream fixture AND a foreign single-stream region-less slice, and the
compute plumbing produces signal rows for every enabled detector.

Plus the three things the viewer is not allowed to decide for itself, each of
which it got wrong once:

* the sidebar opens at the **calibrated** operating points, read from
  ``bench.OPERATING_POINTS`` rather than retyped;
* the sampling interval comes from the **recording**, is shown on screen, and
  a recording without one is refused rather than run at an assumed 10 Hz;
* what is on screen can be **taken away**, in the project's own output
  contract, written by ``bugarach.emit`` and nothing else.

Several of these assert on the STRING THE SIDEBAR DISPLAYS rather than on the
value behind it. That is deliberate: a window-provenance bug shipped here
because every test read the data structure and none read the sentence beside
it.
"""

from pathlib import Path

import numpy as np
import pytest

pn = pytest.importorskip("panel")
pytest.importorskip("holoviews")

from bugarach import emit  # noqa: E402
from bugarach.bench import OPERATING_POINTS  # noqa: E402
from bugarach.detectors.rate import recording_extent  # noqa: E402
from bugarach.io import load_folder, slice_from_events  # noqa: E402
from bugarach.store import load_slice  # noqa: E402
from bugarach.ui.app import (  # noqa: E402
    CALIBRATED,
    DT_DERIVED,
    NO_REGION,
    PARAM_SPECS,
    FrameIntervalMissing,
    _compute,
    _dt_derived,
    _resolve_specs,
    _SPECS,
    build_viewer,
    detection_bundle,
    detections_for,
    frame_interval_sec,
)

FIXTURE = Path(__file__).parent / "fixtures" / "synth_fastcal_s1.mat"

# Stated by the test, not defaulted by the code — which is the whole rule.
TEST_DT = 0.1


def _foreign_slice():
    rng = np.random.RandomState(4)
    events = [np.sort(rng.uniform(0, 120, 15)) for _ in range(5)]
    return slice_from_events(events, dt=0.1, slice_id="foreign")


def _walk(obj):
    """Every widget and pane in a built template, sidebar and main alike."""
    seen = []
    stack = list(getattr(obj, "sidebar", [])) + list(getattr(obj, "main", []))
    while stack:
        o = stack.pop()
        seen.append(o)
        stack.extend(list(getattr(o, "objects", []) or []))
    return seen


def _sidebar_text(app) -> str:
    """What the sidebar actually says, widget labels and prose together."""
    bits = []
    for o in _walk(app):
        text = getattr(o, "object", None)
        if isinstance(text, str):
            bits.append(text)
        name = getattr(o, "name", None)
        value = getattr(o, "value", "__none__")
        if isinstance(name, str) and value != "__none__":
            bits.append(f"{name} = {value}")
    return "\n".join(bits)


def _find(app, kind):
    for o in _walk(app):
        if isinstance(o, kind):
            return o
    raise AssertionError(f"no {kind.__name__} in the built viewer")


def _folder(tmp_path, *, dt="0.05", rows="1,10.0\n1,10.4\n2,10.2\n3,10.3\n"):
    """A minimal conforming export folder, so the dt on screen has a source."""
    d = tmp_path / "export"
    d.mkdir()
    (d / "s1.csv").write_text("roi,time_sec\n" + rows)
    if dt is None:
        (d / "slices.csv").write_text("slice_id,group_id\ns1,MALE\n")
    else:
        (d / "slices.csv").write_text(
            f"slice_id,frame_interval_sec,group_id\ns1,{dt},MALE\n")
    (d / "regions.csv").write_text(
        "slice_id,region_idx,label,start_sec,end_sec\n"
        "s1,1,baseline,0,20\ns1,2,TTX,20,40\n")
    return d


def test_viewer_builds_on_two_stream_store():
    s = load_slice(FIXTURE, dt=0.1)
    app = build_viewer({s.slice_id: s})
    assert app is not None  # FastListTemplate assembled without serving


def test_viewer_builds_on_single_stream_slice():
    s = _foreign_slice()
    app = build_viewer({"foreign": s})
    assert app is not None


@pytest.mark.parametrize("det", list(PARAM_SPECS))
def test_compute_runs_every_detector_generically(det):
    s = _foreign_slice()
    ext = recording_extent(s)
    params = {p: default for p, _, default, _, _ in PARAM_SPECS[det]}
    # shrink the expensive surrogate counts for the smoke test
    for key in ("n_surrogates",):
        if key in params:
            params[key] = 10
    out = _compute(det, s, ext, params, dt=TEST_DT)
    assert set(out) == {"events"}
    t, y, (onsets, widths), extra, result = out["events"]
    assert t.size == y.size and t.size > 0
    assert np.size(onsets) == np.size(widths)
    assert result is not None            # the row emit will write comes from here


def test_raster_only_viewer_builds_and_computes_nothing(monkeypatch):
    """The first look at a folder somebody just sent you: recordings, no
    claims about them. Nothing is computed, which is also why it opens."""
    import bugarach.ui.app as app_mod

    def boom(*a, **k):                      # any detector call is a failure
        raise AssertionError("raster-only must not run a detector")

    monkeypatch.setattr(app_mod, "_compute", boom)
    app = build_viewer({"a": _foreign_slice()}, raster_only=True)
    assert app is not None


def test_export_folder_is_read_as_one_thing_not_swept_for_files(tmp_path):
    """`slices.csv` and `regions.csv` are not recordings. Without this a
    folder of 2 recordings opens as 4, two of them nonsense."""
    from bugarach.cli import _is_export_folder

    d = tmp_path / "export"
    d.mkdir()
    (d / "s1.csv").write_text("roi,time_sec,stream\n1,1.0,fast\n2,NA,fast\n")
    (d / "s2.csv").write_text("roi,time_sec\n1,4.0\n")
    (d / "slices.csv").write_text("slice_id,frame_interval_sec\ns1,0.05\ns2,0.1\n")
    (d / "regions.csv").write_text(
        "slice_id,region_idx,label,start_sec,end_sec\ns1,1,baseline,0,60\n")

    assert _is_export_folder(d)
    assert not _is_export_folder(tmp_path)          # a bare dir is not one
    ids = [s.slice_id for s in load_folder(d)]
    assert ids == ["s1", "s2"]

    app = build_viewer({s.slice_id: s for s in load_folder(d)},
                       raster_only=True)
    assert app is not None


# ---------------------------------------------------------------- calibration

def test_every_viewer_default_is_the_calibrated_one():
    """No widget may open anywhere other than its declared operating point.

    This is the check that was missing: the sidebar carried its own copy of the
    numbers, and two of them fell behind ``bench.OPERATING_POINTS`` without
    anything noticing.
    """
    for det, rows in PARAM_SPECS.items():
        point = OPERATING_POINTS[det].params
        for pname, _label, default, _bounds, _step in rows:
            if pname in point:
                assert default == point[pname], (
                    f"{det}.{pname} opens at {default!r}, but the calibrated "
                    f"point is {point[pname]!r}")


def test_the_two_that_drifted_are_the_calibrated_values_now():
    """The specific regression, named so it cannot come back quietly.

    CICADA's FAST percentile was retuned to 99.999 on 2026-08-20 after the
    looser point fired 7.3 false events an hour against a ceiling of 6
    (FOUNDATIONS §9); CoactDetect's calibrated pair scores F1 1.00 against 0.72
    at the signature-ish one (``bench`` module docstring). The viewer shipped
    the rejected value in both cases.
    """
    got = {det: {p: v for p, _, v, _, _ in rows}
           for det, rows in PARAM_SPECS.items()}
    assert got["cicada"]["sce_percentile"] == 99.999
    assert got["cicada"]["n_surrogates"] == 100
    assert got["coact"]["int_win_sec"] == 2.0
    assert got["coact"]["alpha"] == 1e-4


def test_a_second_copy_of_a_calibrated_default_is_refused_at_import():
    """Writing the number here as well is the defect, so it cannot compile."""
    bad = {"coact": [("alpha", "alpha", 1e-3, (1e-6, 0.1), 1e-5)]}
    with pytest.raises(ValueError, match="bench.OPERATING_POINTS"):
        _resolve_specs(bad)


def test_calibrated_on_a_parameter_the_bench_does_not_declare_is_refused():
    bad = {"coact": [("min_rois", "min ROIs", CALIBRATED, (2, 15), 1)]}
    with pytest.raises(ValueError, match="does not declare it"):
        _resolve_specs(bad)


def test_a_default_outside_its_own_widget_range_is_refused():
    bad = {"sce": [("min_rois", "min ROIs", 99, (2, 15), 1)]}
    with pytest.raises(ValueError, match="outside its own"):
        _resolve_specs(bad)


def test_no_widget_offers_to_overrule_the_recording_about_its_own_dt():
    for det, names in DT_DERIVED.items():
        exposed = {p for p, _, _, _, _ in PARAM_SPECS[det]}
        assert not exposed & set(names), (
            f"{det} exposes {exposed & set(names)}, which the recording decides")
    bad = {"rate": [("grid_dt", "grid dt", 0.1, (0.001, 1.0), 0.001)]}
    with pytest.raises(ValueError, match="derived from the recording"):
        _resolve_specs(bad)


def test_the_spec_table_still_marks_what_it_should():
    """A benched parameter written as a literal would pass the equality test
    above while re-introducing the second copy. This is the half that catches
    it: the table must SAY calibrated, not merely agree today."""
    for det, rows in _SPECS.items():
        point = OPERATING_POINTS[det].params
        for pname, _label, default, _bounds, _step in rows:
            if pname in point:
                assert default is CALIBRATED, (
                    f"{det}.{pname} is benched — write CALIBRATED, not "
                    f"{default!r}")


# ------------------------------------------------------------------------ dt

def test_dt_comes_from_the_folder(tmp_path):
    s, = load_folder(_folder(tmp_path, dt="0.05"))
    assert frame_interval_sec(s) == 0.05
    assert _dt_derived("rate", 0.05) == {"grid_dt": 0.05}
    assert _dt_derived("cicada", 0.05) == {"imaging_rate_hz": 20.0}
    assert _dt_derived("loco", 0.05) == {}


@pytest.mark.parametrize("det", ["rate", "cicada"])
@pytest.mark.parametrize("dt", [0.05, 0.1])
def test_the_detectors_actually_run_on_the_folders_grid(tmp_path, det, dt):
    """Not "the viewer computed a number" — the number reached the detector.

    Both detectors lay their statistic on a grid of the sampling interval, so
    the spacing of the trace that comes back is the interval, observed rather
    than reported. CICADA is the one that states it upside down (a rate, not an
    interval), which is exactly where an inversion bug would hide.
    """
    s, = load_folder(_folder(tmp_path, dt=str(dt)))
    params = {p: v for p, _, v, _, _ in PARAM_SPECS[det]}
    if "n_surrogates" in params:
        params["n_surrogates"] = 10
    out = _compute(det, s, recording_extent(s), params,
                   dt=frame_interval_sec(s))
    step = np.diff(next(iter(out.values())).t)
    assert np.allclose(step, dt)


def test_a_recording_with_no_interval_is_refused_not_defaulted():
    s = _foreign_slice()                        # a bare CSV states nothing
    assert frame_interval_sec(s) is None
    with pytest.raises(FrameIntervalMissing, match="no sampling interval"):
        _compute("rate", s, recording_extent(s),
                 {p: v for p, _, v, _, _ in PARAM_SPECS["rate"]}, dt=None)


def test_an_unreadable_interval_is_an_error_not_an_absence(tmp_path):
    d = _folder(tmp_path, dt="every other frame")
    s, = load_folder(d)
    with pytest.raises(FrameIntervalMissing, match="not a number of seconds"):
        frame_interval_sec(s)


def test_the_screen_says_which_interval_it_used(tmp_path):
    """Read the sentence, not the variable."""
    s, = load_folder(_folder(tmp_path, dt="0.05"))
    app = build_viewer({s.slice_id: s})
    text = _sidebar_text(app)
    assert "0.05" in text
    assert "20 Hz" in text                       # stated as a rate too
    assert "frame_interval_sec" in text          # and where it came from


def test_the_screen_says_it_refused_when_there_is_no_interval(tmp_path):
    """The refusal is visible, and the rasters are still there."""
    s, = load_folder(_folder(tmp_path, dt=None))
    assert frame_interval_sec(s) is None
    app = build_viewer({s.slice_id: s})
    text = _sidebar_text(app)
    assert "does not state one" in text
    assert "cannot analyse" in text
    # refusing to interpret a recording is not refusing to show it
    assert any(type(o).__name__ == "HoloViews" for o in _walk(app))


def test_raster_only_names_the_interval_too(tmp_path):
    s, = load_folder(_folder(tmp_path, dt="0.05"))
    app = build_viewer({s.slice_id: s}, raster_only=True)
    assert "dt 0.05 s (20 Hz)" in _sidebar_text(app)


# ------------------------------------------------------------------ download

def _computed(tmp_path, dets=("rate", "loco")):
    s, = load_folder(_folder(
        tmp_path, dt="0.05",
        rows="".join(f"{r},{t}\n" for t in (5.0, 5.1, 5.2, 25.0, 25.1, 25.2)
             for r in (1, 2, 3, 4))))
    ext = recording_extent(s)
    results, settings = {}, {}
    for det in dets:
        params = {p: v for p, _, v, _, _ in PARAM_SPECS[det]}
        if "n_surrogates" in params:
            params["n_surrogates"] = 20
        results[det] = _compute(det, s, ext, params, dt=0.05)
        for name in results[det]:
            settings[(det, name)] = {**params, **_dt_derived(det, 0.05)}
    return s, results, settings


def test_the_saved_file_is_the_projects_own_contract(tmp_path):
    """Round-tripped through ``emit.read_detections``, not a second parser."""
    import zipfile

    s, results, settings = _computed(tmp_path)
    buf = detection_bundle(s, results, settings, dt=0.05)
    with zipfile.ZipFile(buf) as z:
        assert set(z.namelist()) == {"detections.csv", "detector_settings.csv",
                                     "run.json"}
        z.extractall(tmp_path / "out")

    rows = emit.read_detections(tmp_path / "out" / "detections.csv")
    assert rows, "the fixture is supposed to produce detections"
    for col in emit.COLUMNS:
        assert col in rows[0]
    # identity carried through from slices.csv, unasked-for and unrenamed
    assert rows[0]["group_id"] == "MALE"
    assert rows[0]["frame_interval_sec"] == "0.05"
    # the interval is in the sidecar, where a reader looks for provenance
    import json
    run = json.loads((tmp_path / "out" / "run.json").read_text())
    assert run["frame_interval_sec"] == {s.slice_id: 0.05}
    assert run["slices"] == [s.slice_id]
    # settings say what each detector ran with, including the derived dt
    settings_rows = list(
        (tmp_path / "out" / "detector_settings.csv").read_text().splitlines())
    assert any("grid_dt,0.05" in r for r in settings_rows)


def test_a_windowed_detector_gets_the_producers_own_region_index(tmp_path):
    """``events_from`` takes ``region_idx`` from the caller and the detectors
    only ever report a label, so the join has to be made deliberately."""
    s, results, _ = _computed(tmp_path, dets=("loco",))
    rows = detections_for(s, results)
    labelled = [e for e in rows if e.region_label is not None]
    assert labelled, "the fixture plants events inside both declared windows"
    for e in labelled:
        assert e.region_idx == {"baseline": 1, "TTX": 2}[e.region_label]


def test_a_whole_recording_run_claims_no_window(tmp_path):
    """rate+context is run once over the full extent, so naming the window an
    onset happens to fall in would report an analysis that did not happen."""
    s, results, _ = _computed(tmp_path, dets=("rate",))
    rows = detections_for(s, results)
    assert rows
    assert all(e.region_idx is None and e.region_label is None for e in rows)


def test_the_no_region_sentinel_never_reaches_the_file(tmp_path):
    """LoCo says "none" for an onset in no declared window. That is a sentinel,
    not a period somebody named, and writing it would be a plausible wrong
    answer rather than an error."""
    s, results, settings = _computed(tmp_path)
    rows = detections_for(s, results)
    assert all(e.region_label != NO_REGION for e in rows)
    outside = [e for e in rows if e.region_label is None]
    assert all(e.region_idx is None for e in outside)


def test_a_recording_that_produced_nothing_still_writes_all_three_files(
        tmp_path):
    """An empty result is a finding; an absent file is a bug. The header is
    still there, so a reader sees a table with no rows rather than a truncated
    download, and ``run.json`` still names the recording that was looked at."""
    import json
    import zipfile

    s, = load_folder(_folder(tmp_path, dt="0.05"))
    buf = detection_bundle(s, {}, {}, dt=0.05)
    with zipfile.ZipFile(buf) as z:
        assert set(z.namelist()) == {"detections.csv", "detector_settings.csv",
                                     "run.json"}
        assert z.read("detections.csv").decode() == ",".join(emit.COLUMNS) + "\n"
        assert json.loads(z.read("run.json"))["slices"] == [s.slice_id]


def test_the_button_hands_over_the_same_bytes_the_screen_computed(tmp_path):
    """Press it. The download is wired to the last render, not to a stub."""
    import zipfile

    s, = load_folder(_folder(tmp_path, dt="0.05"))
    app = build_viewer({s.slice_id: s})
    save = _find(app, pn.widgets.FileDownload)
    assert not save.disabled, "there is a computed result to save"
    assert save.filename == f"{s.slice_id}_detections.zip"
    with zipfile.ZipFile(save.callback()) as z:
        names = set(z.namelist())
        settings = z.read("detector_settings.csv").decode()
    assert names == {"detections.csv", "detector_settings.csv", "run.json"}
    # the file records the CALIBRATED point that was on screen, not a default
    assert "coact,events,alpha,0.0001" in settings
    assert "coact,events,int_win_sec,2.0" in settings


def test_nothing_is_offered_for_download_when_nothing_could_be_computed(
        tmp_path):
    s, = load_folder(_folder(tmp_path, dt=None))
    app = build_viewer({s.slice_id: s})
    assert _find(app, pn.widgets.FileDownload).disabled
