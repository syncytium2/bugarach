"""The pieces of ``tools/detect_with_floors.py`` that decide what a floored call is."""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
import detect_with_floors as d  # noqa: E402


def _one_recording(monkeypatch, windows):
    """A simulated slow recording standing in for the folder, with the given windows."""
    from types import SimpleNamespace

    import bugarach.detect_folder as df
    import bugarach.io as bio
    from bugarach import bench_slow

    s, _ = bench_slow.make_recording("baseline_quiet", 1)
    s.meta = {"group_id": "DI", "subject_id": "m1"}
    s.streams["slow"] = s.streams.pop(bench_slow.STREAM)
    wins = [SimpleNamespace(win_start=a, win_end=b, label=lab, slot=i + 1)
            for i, (a, b, lab) in enumerate(windows)]
    monkeypatch.setattr(bio, "load_folder", lambda folder: [s])
    monkeypatch.setattr(df, "folder_analysis_windows", lambda rec: (rec, wins))
    return bench_slow


def test_the_default_run_has_no_floor_plus_variant(monkeypatch):
    b = _one_recording(monkeypatch, [(0.0, 900.0, "baseline")])
    settings = {"slow": {"coact": dict(b.OPERATING_POINTS["coact"].params)}}
    out = d.recording_task((0, "unused", settings, {}, 20))
    assert out["ok"], out.get("error")
    assert {r["variant"] for r in out["rows"]} == {"own_floor", "baseline_floor"}
    assert d.plus_variant(0) is None


def test_floor_plus_one_runs_coact_one_roi_higher_and_never_keeps_more(monkeypatch):
    """Tony, 2026-09-25, weighing floor + 1: CoactDetect runs at min_rois = own + 1, and a
    stricter floor can only keep fewer calls in a window."""
    b = _one_recording(monkeypatch, [(0.0, 1300.0, "baseline"), (1300.0, 2600.0, "TTX")])
    settings = {"slow": {"coact": dict(b.OPERATING_POINTS["coact"].params)}}
    out = d.recording_task((0, "unused", settings, {}, 20, 1))
    assert out["ok"], out.get("error")
    rows = {(r["region_idx"], r["variant"]): r for r in out["rows"]}
    for idx in (1, 2):
        own, plus = rows[(idx, "own_floor")], rows[(idx, "own_plus_1")]
        assert plus["min_participants"] == own["min_participants"] + 1
        assert plus["n_calls"] <= own["n_calls"]
        assert plus["own_plus_1"] == own["own_floor"] + 1
    assert all(c["participants"] >= c["own_plus_1"] for c in out["calls"]
               if c["variant"] == "own_plus_1")


def test_chorus_is_counted_at_own_plus_one_by_its_calls_participants(monkeypatch):
    """Chorus has no participation parameter: a floor keeps the calls whose participants reach
    it, so floor + 1 counts the calls reaching own + 1. A stand-in model calls every onset
    time of the busiest ROI, so the participants vary from call to call."""
    from types import SimpleNamespace

    b = _one_recording(monkeypatch, [(0.0, 900.0, "baseline")])

    class Model:
        def predict(self, s, stream, extent):
            t = np.concatenate([np.asarray(x, float) for x in s.streams[stream].t50rise])
            t = np.sort(t[(t >= extent[0]) & (t < extent[1])])[:200]
            return SimpleNamespace(onset_sec=t, width_sec=np.zeros(t.size)), None

    monkeypatch.setitem(d._MODELS, "stand-in", Model())
    out = d.recording_task((0, "unused", {"slow": {}}, {"chorus_norm@slow": "stand-in"}, 20, 1))
    assert out["ok"], out.get("error")
    rows = {r["variant"]: r for r in out["rows"] if r["detector"] == "chorus_norm"}
    parts = [c["participants"] for c in out["calls"] if c["detector"] == "chorus_norm"]
    own = rows["own_floor"]["min_participants"]
    assert rows["own_plus_1"]["min_participants"] == own + 1
    assert rows["own_floor"]["n_calls"] == sum(p >= own for p in parts)
    assert rows["own_plus_1"]["n_calls"] == sum(p >= own + 1 for p in parts)
    assert rows["own_plus_1"]["n_calls"] <= rows["own_floor"]["n_calls"]


def test_participants_are_rois_with_an_onset_in_the_call_widened_to_two_seconds():
    trains = [np.array([10.0]), np.array([11.5]), np.array([13.0]), np.array([]),
              np.array([9.0, 10.2])]
    # A zero-width call at 10 s covers [10, 12]: ROIs 0, 1 and 4.
    assert d.participants(trains, 10.0, 0.0, 2.0) == 3
    # A 3.5 s call covers [10, 13.5]: ROI 2 joins.
    assert d.participants(trains, 10.0, 3.5, 2.0) == 4


def test_the_microscope_comes_from_the_recording_not_the_settings():
    from bugarach.detect_folder import with_microscope

    bench = {"excess_threshold_hz": 4.5, "grid_dt": 0.1}
    got = with_microscope("rate", bench, 0.25)
    assert got["grid_dt"] == 0.25 and bench["grid_dt"] == 0.1      # a new dict
    assert with_microscope("rate", {"excess_threshold_hz": 4.5}, 0.25)["grid_dt"] == 0.25
    assert with_microscope("cicada", {"imaging_rate_hz": 10.0}, 0.25)["imaging_rate_hz"] == 4.0
    assert with_microscope("coact", {"alpha": 1e-4}, 0.25) == {"alpha": 1e-4}


def test_every_coded_detector_runs_on_a_recording_whose_settings_carry_no_microscope(monkeypatch):
    """The 2026-09-25 real-data run failed on all 66 recordings: rate+context's settings came
    from a search without ``grid_dt``, and this tool had only ever run CoactDetect."""
    from types import SimpleNamespace

    import bugarach.detect_folder as df
    import bugarach.io as bio
    from bugarach import bench_slow

    s, _ = bench_slow.make_recording("baseline_quiet", 1)
    s.meta = {"group_id": "DI", "subject_id": "m1"}
    win = SimpleNamespace(win_start=0.0, win_end=900.0, label="baseline", slot=1)
    monkeypatch.setattr(bio, "load_folder", lambda folder: [s])
    monkeypatch.setattr(df, "folder_analysis_windows", lambda rec: (rec, [win]))
    # A simulated recording names its one stream bench.STREAM ("events"); a folder names it.
    stream = "slow"
    s.streams[stream] = s.streams.pop(bench_slow.STREAM)
    settings = {stream: {}}
    for det, op in bench_slow.OPERATING_POINTS.items():
        p = {k: v for k, v in op.params.items() if k not in ("grid_dt", "imaging_rate_hz")}
        settings[stream][det] = p
    out = d.recording_task((0, "unused", settings, {}, 20))
    assert out["ok"], out.get("error")
    ran = {r["detector"] for r in out["rows"] if r["stream"] == stream}
    assert ran == set(bench_slow.OPERATING_POINTS)


def test_every_detector_that_draws_random_numbers_runs_seeded_on_real_data(monkeypatch):
    """Two real-data runs on 2026-09-25 differed in four locust verdicts: this tool never passed
    ``rng_seed``, so locust and SCE drew surrogate thresholds from an unseeded generator. A repeat
    run cannot catch that on a small recording, where the threshold rarely moves the calls, so
    this checks what each detector was handed."""
    from types import SimpleNamespace

    import bugarach.detect_folder as df
    import bugarach.detectors.cicada as mc
    import bugarach.detectors.coact as mco
    import bugarach.detectors.loco as ml
    import bugarach.detectors.sce as ms
    import bugarach.io as bio
    from bugarach import bench_slow
    from bugarach.detect_folder import RNG_SEED

    s, _ = bench_slow.make_recording("baseline_quiet", 1)
    s.meta = {"group_id": "DI", "subject_id": "m1"}
    s.streams["slow"] = s.streams.pop(bench_slow.STREAM)
    win = SimpleNamespace(win_start=0.0, win_end=900.0, label="baseline", slot=1)
    monkeypatch.setattr(bio, "load_folder", lambda folder: [s])
    monkeypatch.setattr(df, "folder_analysis_windows", lambda rec: (rec, [win]))
    seen = {}
    for mod, name in ((mc, "cicada_detect"), (mco, "coact_detect"), (ml, "loco_detect"),
                      (ms, "sce_detect")):
        real = getattr(mod, name)

        def spy(*a, _real=real, _name=name, **kw):
            seen[_name] = kw.get("rng_seed")
            return _real(*a, **kw)
        monkeypatch.setattr(mod, name, spy)
    settings = {"slow": {det: {k: v for k, v in op.params.items() if k != "rng_seed"}
                         for det, op in bench_slow.OPERATING_POINTS.items()}}
    out = d.recording_task((0, "unused", settings, {}, 20))
    assert out["ok"], out.get("error")
    assert seen == {n: RNG_SEED for n in ("cicada_detect", "coact_detect", "loco_detect",
                                          "sce_detect")}


def test_every_detector_that_draws_random_numbers_is_seeded_unless_the_settings_name_a_seed():
    from bugarach.bench import OPERATING_POINTS
    from bugarach.detect_folder import RNG_SEED

    for det, op in OPERATING_POINTS.items():
        got = d.seeded(det, {"x": 1})
        assert got.get("rng_seed") == (RNG_SEED if op.takes_rng else None), det
    assert d.seeded("cicada", {"rng_seed": 7})["rng_seed"] == 7


def test_baseline_is_read_from_the_label():
    assert d.is_baseline("baseline") and d.is_baseline(" Baseline 2")
    assert not d.is_baseline("senktide") and not d.is_baseline(None)


def test_the_summary_lists_groups_in_house_order_and_counts_recordings():
    rows = [dict(slice_id=f"r{i}", group=g, window_kind="baseline", stream="fast",
                 detector="coact", variant="own_floor", calls_per_hour=float(i), own_floor=5)
            for i, g in enumerate(["ORX", "DI", "DI", "MALE", "OVX"])]
    s = d.summarise(rows, ["DI", "OVX", "MALE", "ORX"])
    assert list(s) == ["DI", "OVX", "MALE", "ORX", "all"]
    cell = s["DI"]["baseline|fast|coact|own_floor"]
    assert cell["recordings"] == 2 and cell["median_calls_per_hour"] == 1.5
    assert s["all"]["baseline|fast|coact|own_floor"]["recordings"] == 5
