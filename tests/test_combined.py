"""The combined stream, the combined bench, and the tools that take ``combined`` as a stream name.

Tony, 2026-09-22: fast and slow onsets fed through the pipeline as one stream, labels kept for
plotting, a third parameter set. No data needed: every recording here is built.
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pytest

from bugarach import bench, bench_combined, bench_slow
from bugarach.combined import (COMBINED, combine, has_sources, near_coincident, only_combined,
                               stream_of)
from bugarach.store import Slice, Stream

# Pre-ADR-0008 by construction: these pin measurements taken before the floor, or exercise detector
# mechanics it has nothing to do with. The floor's own tests are tests/test_bench_floor.py.
pytestmark = pytest.mark.usefixtures("pre_adr_0008_bench")


REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "tools"))


def _stream(onsets, width, wdef):
    t = [np.asarray(v, float) for v in onsets]
    return Stream(locs=[v.copy() for v in t], amp=[np.ones_like(v) for v in t],
                  width=[np.full_like(v, width) for v in t], t50rise=t, width_def=wdef)


def _slice():
    fast = _stream([[10.0, 50.0], [20.0]], 0.9, "fwhm")
    slow = _stream([[11.0, 30.0], []], 2.0, "rise")
    return Slice(slice_id="s1", streams={"fast": fast, "slow": slow}, dt=0.1)


def test_every_onset_of_both_streams_is_kept_in_time_order_with_its_label():
    c = combine(_slice().fast, _slice().slow)
    assert c.t50rise[0].tolist() == [10.0, 11.0, 30.0, 50.0]
    assert c.label[0].tolist() == ["fast", "slow", "slow", "fast"]
    # Each event keeps its own stream's width, and the rule says so.
    assert c.width[0].tolist() == [0.9, 2.0, 2.0, 0.9]
    assert "fast=fwhm" in c.width_def and "slow=rise" in c.width_def
    assert c.t50rise[1].tolist() == [20.0] and c.label[1].tolist() == ["fast"]
    assert c.n_events == 5


def test_a_slow_onset_one_frame_from_a_fast_one_is_counted_not_dropped():
    s = _slice()
    assert near_coincident(s.fast, s.slow, 0.1 + 1e-9) == (0, 2)
    assert near_coincident(s.fast, s.slow, 1.0) == (1, 2)


def test_detectors_see_the_combined_stream_alone():
    """Adding it beside fast and slow would move their shared-RNG surrogate draws."""
    s = _slice()
    only = only_combined(s)
    assert list(only.streams) == [COMBINED]
    assert list(s.streams) == ["fast", "slow"]           # the original is untouched
    assert stream_of(s, COMBINED).n_events == 5
    assert stream_of(s, "fast") is s.fast


def test_a_recording_missing_a_source_stream_has_no_combined_stream():
    s = Slice(slice_id="s2", streams={"fast": _slice().fast}, dt=0.1)
    assert not has_sources(s)
    with pytest.raises(KeyError):
        stream_of(s, COMBINED)


def test_the_roi_counts_must_agree():
    s = _slice()
    short = _stream([[1.0]], 2.0, "rise")
    with pytest.raises(ValueError):
        combine(s.fast, short)


COPIED = ("BENCH_RECORDING", "REGIMES", "NULL_RECORDING", "CROWDED_RECORDING",
          "TAIL_RECORDING", "OPERATING_POINTS", "FULL_GRIDS", "MAX_PROBE_PER_MIN",
          "MAX_FALSE_POSITIVES_PER_HOUR", "MAX_PRECISION_DROP", "MEASURED_RECORD",
          "make_recording", "make_crowded_recording", "make_tail_recording",
          "make_null_recording", "run_detector", "false_positives_per_hour", "evaluate",
          "sweep", "pick_operating_point")


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


def test_the_combined_bench_keeps_the_shared_hot_window():
    assert bench_combined.BENCH_RECORDING["hot_window"] == bench.BENCH_RECORDING["hot_window"]


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
    rows = ["roi,time_sec,stream"]
    for t in (150, 300, 450, 600, 750):
        for roi in range(1, 11):
            rows.append(f"{roi},{t + roi * 0.05:.2f},fast")
            rows.append(f"{roi},{t + 1.5 + roi * 0.1:.2f},slow")
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
