"""The combined stream, the combined bench, and the tools that take ``combined`` as a stream name.

The combined stream is the producer's (ADR-0023): every fast and every slow event of a ROI,
each row naming its source in ``source_stream``. bugarach reads it and does not build it.
No data needed: every recording here is built.
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pytest

from bugarach import bench, bench_combined, bench_slow
from bugarach import combined as combined_module
from bugarach.combined import (COMBINED, has_combined, near_coincident, only_combined,
                               stream_of, without_combined)
from bugarach.io import load_events_csv
from bugarach.store import Slice, Stream

# Pre-ADR-0008 by construction: these pin measurements taken before the floor, or exercise detector
# mechanics it has nothing to do with. The floor's own tests are tests/test_bench_floor.py.
pytestmark = pytest.mark.usefixtures("pre_adr_0008_bench")


REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "tools"))

HEADER = "roi,time_sec,stream,width_sec,width_def,peak_sec,amp,source_stream\n"
ROWS = (
    "1,10.0,fast,0.9,fwhm,10.4,1,fast\n"
    "1,50.0,fast,0.9,fwhm,50.4,1,fast\n"
    "2,20.0,fast,0.9,fwhm,20.4,1,fast\n"
    "1,11.0,slow,2.0,rise,13.0,1,slow\n"
    "1,30.0,slow,2.0,rise,32.0,1,slow\n"
    "2,NA,slow,NA,rise,NA,NA,slow\n"
    # the producer's pooled rows, deliberately out of time order
    "1,50.0,combined,0.9,per_event_by_source_stream,50.4,1,fast\n"
    "1,10.0,combined,0.9,per_event_by_source_stream,10.4,1,fast\n"
    "1,11.0,combined,2.0,per_event_by_source_stream,13.0,1,slow\n"
    "1,30.0,combined,2.0,per_event_by_source_stream,32.0,1,slow\n"
    "2,20.0,combined,0.9,per_event_by_source_stream,20.4,1,fast\n"
)


def _stream(onsets, width, wdef):
    t = [np.asarray(v, float) for v in onsets]
    return Stream(locs=[v.copy() for v in t], amp=[np.ones_like(v) for v in t],
                  width=[np.full_like(v, width) for v in t], t50rise=t, width_def=wdef)


def _slice():
    fast = _stream([[10.0, 50.0], [20.0]], 0.9, "fwhm")
    slow = _stream([[11.0, 30.0], []], 2.0, "rise")
    return Slice(slice_id="s1", streams={"fast": fast, "slow": slow}, dt=0.1)


def _shipped(tmp_path, rows=ROWS):
    path = tmp_path / "s1.csv"
    path.write_text(HEADER + rows, encoding="utf-8")
    return load_events_csv(path, dt=0.1)


def test_the_shipped_combined_stream_keeps_each_events_source_in_time_order(tmp_path):
    s = _shipped(tmp_path)
    c = s.streams[COMBINED]
    assert c.t50rise[0].tolist() == [10.0, 11.0, 30.0, 50.0]
    assert c.label[0].tolist() == ["fast", "slow", "slow", "fast"]
    # Each event keeps its own stream's width; the label travels with it through the sort.
    assert c.width[0].tolist() == [0.9, 2.0, 2.0, 0.9]
    assert c.width_def == "per_event_by_source_stream"
    assert c.t50rise[1].tolist() == [20.0] and c.label[1].tolist() == ["fast"]
    assert c.n_events == 5


def test_a_fast_or_slow_stream_gets_no_label(tmp_path):
    """Their rows repeat their own stream in ``source_stream``; nothing changes for them."""
    s = _shipped(tmp_path)
    assert s.streams["fast"].label is None and s.streams["slow"].label is None


def test_a_pooled_stream_that_names_only_some_sources_is_refused(tmp_path):
    rows = ROWS.replace("1,30.0,combined,2.0,per_event_by_source_stream,32.0,1,slow",
                        "1,30.0,combined,2.0,per_event_by_source_stream,32.0,1,")
    with pytest.raises(ValueError, match="source_stream"):
        _shipped(tmp_path, rows)


def test_check_reports_a_pooled_stream_that_is_not_its_sources(tmp_path):
    """Contract revision 10: a pooled stream holds every event of each stream it names."""
    from bugarach.conform import _pooled_stream_errors

    assert _pooled_stream_errors(_shipped(tmp_path)) == []
    short = ROWS.replace("1,30.0,combined,2.0,per_event_by_source_stream,32.0,1,slow\n", "")
    errors = _pooled_stream_errors(_shipped(tmp_path, short))
    assert len(errors) == 1 and "slow" in errors[0] and "1 of 2 ROI" in errors[0]


def test_bugarach_has_no_merge():
    """ADR-0023: the stream is the producer's. Nothing here makes one from fast and slow."""
    assert not hasattr(combined_module, "combine")


def test_a_slow_onset_one_frame_from_a_fast_one_is_counted_not_dropped():
    s = _slice()
    assert near_coincident(s.fast, s.slow, 0.1 + 1e-9) == (0, 2)
    assert near_coincident(s.fast, s.slow, 1.0) == (1, 2)


def test_detectors_see_the_combined_stream_alone(tmp_path):
    """Beside fast and slow it would move their shared-RNG surrogate draws."""
    s = _shipped(tmp_path)
    assert list(only_combined(s).streams) == [COMBINED]
    assert sorted(without_combined(s).streams) == ["fast", "slow"]
    assert sorted(s.streams) == ["combined", "fast", "slow"]      # the original is untouched
    assert stream_of(s, "fast") is s.streams["fast"]


def test_fast_and_slow_calls_do_not_depend_on_the_export_shipping_combined(tmp_path):
    from bugarach.detect_folder import detect_slice

    rng = np.random.default_rng(3)
    lines, pooled = [], []
    for roi in range(1, 9):
        for name, n, wdef in (("fast", 40, "fwhm"), ("slow", 25, "rise")):
            for t in np.sort(rng.uniform(5, 595, n)):
                row = f"{roi},{t:.1f},{name},1.0,{wdef},{t + 0.5:.1f},1"
                lines.append(f"{row},{name}")
                pooled.append(f"{roi},{t:.1f},combined,1.0,per_event_by_source_stream,"
                              f"{t + 0.5:.1f},1,{name}")
    (tmp_path / "two").mkdir()
    (tmp_path / "three").mkdir()
    two = _shipped(tmp_path / "two", "\n".join(lines) + "\n")
    three = _shipped(tmp_path / "three", "\n".join(lines + pooled) + "\n")

    def calls(s, stream=None):
        events, _ = detect_slice(s, detectors=("coact", "sce"), stream=stream)
        return sorted((e.detector, e.stream, round(e.onset_sec, 3)) for e in events)

    alone = calls(two)
    both = calls(three)
    assert [c for c in both if c[1] != COMBINED] == alone
    assert calls(three, "fast") == [c for c in alone if c[1] == "fast"]
    assert [c for c in both if c[1] == COMBINED] == calls(three, COMBINED)


def test_a_recording_whose_export_has_no_combined_stream_has_none():
    s = _slice()
    assert not has_combined(s)
    with pytest.raises(KeyError, match="ADR-0023"):
        stream_of(s, COMBINED)


COPIED = ("BENCH_RECORDING", "REGIMES", "NULL_RECORDING", "CROWDED_RECORDING",
          "TAIL_RECORDING", "OPERATING_POINTS", "FULL_GRIDS", "MAX_PROBE_PER_MIN",
          "MAX_FALSE_POSITIVES_PER_HOUR", "MAX_PRECISION_DROP", "MEASURED_RECORD",
          "make_recording", "make_crowded_recording", "make_tail_recording",
          "make_null_recording", "run_detector", "false_positives_per_hour", "evaluate",
          "sweep", "pick_operating_point",
          "ELEVATED_RATE_RECORDING", "make_elevated_rate_recording", "evaluate_elevated_rate")


@pytest.mark.parametrize("other", [bench, bench_slow], ids=["fast", "slow"])
@pytest.mark.parametrize("name", COPIED)
def test_a_stream_dependent_name_is_the_combined_modules_own(name, other):
    assert getattr(bench_combined, name) is not getattr(other, name), (
        f"bench_combined.{name} is {other.__name__}.{name}: a combined run would read its values")


def test_a_combined_recording_runs_at_the_combined_background():
    s, gt = bench_combined.make_null_recording(1)
    b = bench_combined.BENCH_RECORDING
    rate = sum(len(t) for t in s.streams[bench_combined.STREAM].locs) / b["duration_sec"] / b["n_roi"]
    want = bench_combined.NULL_RECORDING["bg_rate_hz"]
    assert abs(rate - want) < abs(rate - bench_slow.NULL_RECORDING["bg_rate_hz"])
    assert abs(rate - want) < abs(rate - bench.NULL_RECORDING["bg_rate_hz"])


def test_the_combined_bench_scores_a_detector():
    r = bench_combined.evaluate("coact", "baseline_busy", seeds=(1,))
    assert 0.0 <= r.f1 <= 1.0


def test_the_combined_elevated_rate_recording_keeps_the_shared_stretch_at_its_own_rate():
    _, gt = bench_combined.make_elevated_rate_recording("baseline_quiet", 1)
    assert gt.params["hot_window"] == bench.ELEVATED_RATE_RECORDING["hot_window"]
    assert gt.params["hot_rate_hz"] == bench_combined.ELEVATED_RATE_RECORDING["hot_rate_hz"]
    assert gt.params["hot_rate_hz"] not in (bench.ELEVATED_RATE_RECORDING["hot_rate_hz"],
                                            bench_slow.ELEVATED_RATE_RECORDING["hot_rate_hz"])


def test_the_measured_constants_agree_with_the_combined_record_once_there_is_one():
    """Provisional until measured; after that, the record and the module must agree."""
    import json

    path = REPO / bench_combined.MEASURED_RECORD
    if not path.exists():
        assert bench_combined.PROVISIONAL, "no combined record, so the module must say provisional"
        pytest.skip("the combined bench has not been measured yet (bench_combined's route, step 2)")
    rec = json.loads(path.read_text(encoding="utf-8"))
    assert rec["stream"] == bench_combined.MEASURED_STREAM == COMBINED
    assert not bench_combined.PROVISIONAL, "a record exists: transcribe it and clear PROVISIONAL"
    for k, v in bench_combined.measured_constants().items():
        row = rec["values"][k]
        assert row["lo"] <= v <= row["hi"], f"{k} = {v} outside {row['lo']:.4f}-{row['hi']:.4f}"
    assert list(bench_combined.MEASURED_WIDTH_QUANTILES) == rec["width_quantiles"]


@pytest.mark.parametrize("tool", ["measure_jitter_correlogram", "search_all_settings",
                                  "measure_coordination_rates", "settings_from_bench"])
def test_every_stage_offers_the_combined_bench(tool):
    mod = __import__(tool)
    assert mod.BENCHES["combined"] == "bugarach.bench_combined"


def test_the_combined_record_is_not_the_slow_record():
    import measure_slow_bench as msb

    assert msb.RECORDS["combined"] == bench_combined.MEASURED_RECORD
    assert len(set(msb.RECORDS.values()) | {bench.MEASURED_RECORD}) == 3


def test_the_settings_file_carries_the_combined_rows_and_detect_reads_it(tmp_path):
    import settings_from_bench as sfb

    from bugarach.detect_folder import load_settings

    out = tmp_path / "combined_settings.csv"
    assert sfb.main(["--bench", "combined", "--out", str(out)]) == 0
    params, prov = load_settings(out)
    assert {s for _, s in params} == {COMBINED}
    assert set(d for d, _ in params) == set(bench_combined.OPERATING_POINTS)
    assert all(v["fitted_on"] == "bugarach.bench_combined.OPERATING_POINTS" for v in prov.values())


def test_detect_runs_the_combined_stream_at_its_own_settings_and_labels_the_rows(tmp_path):
    """``bugarach detect --stream combined --settings <combined csv>``: the export fireflies reads."""
    import csv

    import settings_from_bench as sfb

    from bugarach.detect_folder import detect_folder

    folder = tmp_path / "folder"
    folder.mkdir()
    (folder / "slices.csv").write_text("slice_id,frame_interval_sec,group_id\ns1,0.1,MALE\n")
    (folder / "regions.csv").write_text(
        "slice_id,region_idx,label,start_sec,end_sec,analysis_start_sec,analysis_end_sec\n"
        "s1,1,baseline,0,900,0,900\n")
    rows = ["roi,time_sec,stream,source_stream"]
    for t in (150, 300, 450, 600, 750):
        for roi in range(1, 11):
            for when, name in ((t + roi * 0.05, "fast"), (t + 1.5 + roi * 0.1, "slow")):
                rows.append(f"{roi},{when:.2f},{name},{name}")
                rows.append(f"{roi},{when:.2f},combined,{name}")     # as the producer ships it
    (folder / "s1.csv").write_text("\n".join(rows) + "\n")

    settings = tmp_path / "combined_settings.csv"
    sfb.main(["--bench", "combined", "--out", str(settings)])
    out = tmp_path / "out"
    detect_folder(folder, out_dir=out, stream=COMBINED, settings=settings,
                  detectors=("coact", "loco"))
    with (out / "detections.csv").open(encoding="utf-8") as fh:
        got = list(csv.DictReader(fh))
    assert got, "five planted moments across ten ROIs, and nothing was called"
    assert {r["stream"] for r in got} == {COMBINED}
    with (out / "detector_settings.csv").open(encoding="utf-8") as fh:
        used = list(csv.DictReader(fh))
    assert {r["stream"] for r in used} == {COMBINED}


def test_the_combined_calls_take_the_slow_aperture():
    from bugarach.call_measure import DEFAULTS, defaults_for

    assert defaults_for(COMBINED) == DEFAULTS["slow"]
