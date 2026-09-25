"""ADR-0010 (Proposed) parts 2 and 3, preparation only: empirical planted gaps and the merge count.

Part 2: ``simulate_coordination(gap_source=..., gap_mix=...)`` draws the gaps between planted
events from intervals measured in the real data, read by ``bugarach.real_intervals``. Part 3:
every score carries ``n_merged_calls``, the calls whose span contains two or more scored events.
That the new options change nothing when unset is ``test_real_intervals_off_by_default.py``.
"""
from __future__ import annotations

import json

import numpy as np
import pytest

from bugarach import bench, bench_combined, bench_slow, real_intervals as ri
from bugarach.groups import GROUP_ORDER
from bugarach.score import score_detections
from bugarach.simulate import GroundTruth, PlantedEvent, simulate_coordination

# A measured-looking distribution: mostly seconds apart, a long tail.
GAPS = (3.0, 4.0, 5.0, 6.0, 8.0, 12.0, 20.0, 34.0, 60.0, 150.0)


@pytest.fixture(autouse=True)
def _no_floor(monkeypatch):
    # The floor is computed from a finished recording and plays no part here; off keeps it fast.
    monkeypatch.setenv(bench.FLOOR_SWITCH_ENV, "off")


def _doc(stream="fast", key="gaps_sec"):
    return {"stream": stream, "pooled": {key: list(GAPS)},
            "by_group": {g.lower() if g == "MALE" else g: {key: [float(i + 2)] * 3}
                         for i, g in enumerate(GROUP_ORDER)},
            "provenance": "ignored"}


def _trains(s):
    return [np.asarray(v) for st in s.streams.values() for v in st.locs]


def _same_recording(a, b):
    (sa, ga), (sb, gb) = a, b
    assert len(ga.events) == len(gb.events)
    for x, y in zip(ga.events, gb.events):
        assert (x.time, x.rois, x.onsets) == (y.time, y.rois, y.onsets)
    for x, y in zip(_trains(sa), _trains(sb)):
        np.testing.assert_array_equal(x, y)


# ---- the loader -----------------------------------------------------------------------------

def test_the_loader_reads_the_schema_pooled_and_by_group(tmp_path):
    (tmp_path / "fast.json").write_text(json.dumps(_doc("fast")))
    (tmp_path / "slow.json").write_text(json.dumps(_doc("slow", key="gaps")))   # the alias
    d = ri.load_gaps("fast", path=tmp_path)
    assert (d.stream, d.pool, d.gaps_sec, d.source) == ("fast", "pooled", GAPS, "fast.json")
    assert ri.load_gaps("slow", path=tmp_path / "slow.json").gaps_sec == GAPS
    # Groups by name in any case; MALE was written lower-case above.
    assert ri.load_gaps("fast", pool="MALE", path=tmp_path).gaps_sec == (4.0,) * 3
    assert ri.load_gaps("fast", pool="ovx", path=tmp_path).pool == "OVX"


def test_the_loader_refuses_what_it_cannot_read(tmp_path):
    (tmp_path / "a.json").write_text(json.dumps([_doc("fast"), _doc("slow")]))   # a list is fine
    assert ri.load_gaps("slow", path=tmp_path).stream == "slow"
    with pytest.raises(FileNotFoundError):
        ri.load_gaps("combined", path=tmp_path)
    with pytest.raises(ValueError, match="pool must be"):
        ri.load_gaps("fast", pool="TTX", path=tmp_path)
    (tmp_path / "b.json").write_text(json.dumps(_doc("fast")))
    with pytest.raises(ValueError, match="2 documents"):
        ri.load_gaps("fast", path=tmp_path)
    with pytest.raises(ValueError, match="finite and positive"):
        ri.GapDistribution("fast", "pooled", (3.0, -1.0))


# ---- the generator --------------------------------------------------------------------------

@pytest.mark.parametrize("mod", [bench, bench_slow, bench_combined])
def test_mix_one_is_the_old_recording(mod):
    old = mod.make_recording("baseline_busy", 3)
    new = mod.make_recording("baseline_busy", 3, gap_source=GAPS, gap_mix=1.0)
    _same_recording(old, new)
    assert "gap_mix" not in old[1].params and new[1].params["gap_mix"] == 1.0


def test_a_mix_without_a_source_or_outside_zero_to_one_is_refused():
    with pytest.raises(ValueError, match="needs a gap_source"):
        simulate_coordination(seed=1, gap_mix=0.5)
    with pytest.raises(ValueError, match="between 0 and 1"):
        simulate_coordination(seed=1, gap_source=GAPS, gap_mix=1.5)
    with pytest.raises(ValueError, match="renewal"):
        simulate_coordination(seed=1, gap_source=GAPS, gap_mix=0.0, spacing="uniform")


@pytest.mark.parametrize("mod", [bench, bench_slow, bench_combined])
def test_mix_zero_draws_every_gap_from_the_source_and_keeps_the_recording(mod):
    for seed in (1, 2, 3):
        s, gt = mod.make_recording("baseline_quiet", seed, gap_source=GAPS, gap_mix=0.0)
        old_s, old_gt = mod.make_recording("baseline_quiet", seed)
        t = np.sort([e.time for e in gt.events])
        gaps = np.diff(t)
        # Every gap is one of the supplied ones: none comes from the old rule.
        assert all(np.any(np.isclose(g, GAPS)) for g in gaps), gaps
        assert gt.params["n_gaps_measured"] == len(gt.events) - 1
        assert gt.params["n_gaps_old_rule"] == 0
        # Length, count and participation levels unchanged; every event inside the recording.
        assert gt.params["duration_sec"] == old_gt.params["duration_sec"]
        assert len(gt.events) == len(old_gt.events)
        assert sorted(e.frac for e in gt.events) == sorted(e.frac for e in old_gt.events)
        margin = gt.params["margin_sec"]
        assert t[0] >= margin and t[-1] <= gt.params["duration_sec"] - margin
        # Each event separately labelled with its own members and onsets.
        n_roi = gt.params["n_roi"]
        for e in gt.events:
            assert len(e.rois) == e.n_part == len(e.onsets) == len(set(e.rois))
            assert all(0 <= r < n_roi for r in e.rois)


def test_drawn_gaps_follow_the_supplied_distribution():
    # Loose: pooled over seeds, each supplied gap is drawn about as often as any other.
    drawn = []
    for seed in range(40):
        _, gt = simulate_coordination(seed=seed, **{**bench.BENCH_RECORDING, "n_distractors": 0},
                                      gap_source=GAPS, gap_mix=0.0)
        drawn += list(np.diff(np.sort([e.time for e in gt.events])))
    idx = [int(np.argmin(np.abs(np.asarray(GAPS) - g))) for g in drawn]
    counts = np.bincount(idx, minlength=len(GAPS))
    expected = len(drawn) / len(GAPS)
    assert counts.min() > 0.6 * expected and counts.max() < 1.4 * expected, counts
    assert abs(np.median(drawn) - np.median(GAPS)) < 3.0


def test_a_mix_keeps_about_that_share_at_the_old_spacing():
    old = new = 0
    for seed in range(40):
        _, gt = bench.make_recording("baseline_busy", seed, gap_source=GAPS, gap_mix=0.5)
        old += gt.params["n_gaps_old_rule"]
        new += gt.params["n_gaps_measured"]
        t = np.sort([e.time for e in gt.events])
        assert t[-1] <= gt.params["duration_sec"] - gt.params["margin_sec"]
        # An old-rule gap is at least the old floor; a measured one is one of the supplied values.
        for g in np.diff(t):
            assert g >= bench.BENCH_RECORDING["min_sep_sec"] - 1e-9 or np.any(np.isclose(g, GAPS))
    assert 0.4 < old / (old + new) < 0.6


def test_gaps_too_long_for_the_recording_are_redrawn_then_refused():
    # 14 gaps of 150 s (2100 s) overrun a 1500-s recording; a draw with enough 3-s gaps fits.
    _, gt = simulate_coordination(seed=5, duration_sec=1500.0, gap_source=(3.0, 150.0),
                                  gap_mix=0.0)
    t = np.sort([e.time for e in gt.events])
    assert t[-1] <= 1500.0 - gt.params["margin_sec"]
    assert gt.params["n_gap_redraws"] >= 0
    with pytest.raises(ValueError, match="could not fit"):
        simulate_coordination(seed=5, duration_sec=600.0, gap_source=(150.0,), gap_mix=0.0)


def test_the_same_seed_gives_the_same_mixed_recording():
    a = bench.make_recording("baseline_busy", 11, gap_source=GAPS, gap_mix=0.3)
    b = bench.make_recording("baseline_busy", 11, gap_source=GAPS, gap_mix=0.3)
    _same_recording(a, b)


def test_bench_overrides_wires_a_file_into_a_bench_maker(tmp_path):
    (tmp_path / "fast.json").write_text(json.dumps(_doc("fast")))
    over = ri.bench_overrides("fast", mix=0.0, path=tmp_path)
    _, gt = bench.make_recording("baseline_busy", 2, **over)
    assert gt.params["gap_source"]["source"] == "fast.json"
    assert gt.params["gap_source"]["n_gaps"] == len(GAPS)


# ---- the merge count ------------------------------------------------------------------------

def _gt(times, n_parts=None, floor=None):
    n_parts = n_parts or [10] * len(times)
    events = [PlantedEvent(time=float(t), frac=n / 30, n_part=n, rois=tuple(range(n)),
                           jitter_sec=0.1) for t, n in zip(times, n_parts)]
    params = {} if floor is None else {"event_floor": floor}
    return GroundTruth(events=events, distractors=[], params=params)


def test_a_call_spanning_two_scored_events_is_one_merge():
    gt = _gt([100.0, 104.0, 300.0])
    sc = score_detections(gt, [99.0, 299.0], widths=[6.0, 2.0])
    assert sc.n_merged_calls == 1
    assert "merged calls 1" in sc.summary()


def test_a_call_spanning_one_event_is_no_merge():
    gt = _gt([100.0, 104.0, 300.0])
    sc = score_detections(gt, [99.0, 103.5, 299.0], widths=[2.0, 2.0, 2.0])
    assert sc.n_merged_calls == 0


def test_a_call_spanning_a_scored_and_a_dont_care_event_is_no_merge():
    # Floor 6: the 3-ROI event is "don't care" (ADR-0009 decision 2).
    gt = _gt([100.0, 104.0], n_parts=[10, 3], floor=6)
    sc = score_detections(gt, [99.0], widths=[6.0])
    assert sc.n_merged_calls == 0
    # Without the floor both are scored, and the same call is a merge.
    assert score_detections(_gt([100.0, 104.0], n_parts=[10, 3]), [99.0],
                            widths=[6.0]).n_merged_calls == 1


def test_the_merge_count_changes_no_other_number():
    gt = _gt([100.0, 104.0, 300.0, 500.0])
    onsets, widths = [99.0, 299.0, 700.0], [6.0, 2.0, 1.0]
    sc = score_detections(gt, onsets, widths=widths)
    assert sc.n_merged_calls == 1
    # The one-to-one match: the merged call hits one of the two, the other is a miss.
    assert (sc.n_hit, sc.n_miss, sc.n_fa, sc.n_detected) == (2, 2, 1, 3)
    assert (sc.recall, sc.precision) == (0.5, 2 / 3)
    r = bench.pool_scores([sc, sc], detector="coact", regime="baseline_busy")
    assert r.n_merged_calls == 2
    assert (r.n_hit, r.n_planted, r.n_detected) == (4, 8, 6)
    assert "merged 2" in r.summary()
