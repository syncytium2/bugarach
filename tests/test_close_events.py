"""Close-event test sets and the per-pair score (ADR-0022).

The score has to be able to say both things the run record says: that a detector joined a pair,
and that a detector split one without fragmenting its calls.
"""
from __future__ import annotations

import sys
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import pytest

from bugarach import bench
from bugarach import close_events as ce
from bugarach import stream_profile as sp

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))


@pytest.fixture(autouse=True)
def realistic_spacing(monkeypatch):
    monkeypatch.setenv(bench.SPACING_ENV, "realistic")


def _gt(times, n_part=10, floor=None):
    events = [SimpleNamespace(time=float(t), n_part=n_part, frac=0.3) for t in times]
    return SimpleNamespace(events=events, times=np.asarray(times, float), distractors=[],
                           params={} if floor is None else {"event_floor": floor})


def _det(onsets, widths=None):
    onsets = np.asarray(onsets, float)
    return SimpleNamespace(onset_sec=onsets,
                           width_sec=np.zeros_like(onsets) if widths is None
                           else np.asarray(widths, float))


def test_structure_sorts_events_into_pairs_isolated_and_the_rest():
    #        isolated  pair (1 s)     chain of three          near, not at 1 s
    times = [100.0, 200.0, 201.0, 300.0, 301.0, 302.0, 400.0, 403.0]
    st = ce.structure(_gt(times), 1.0)
    assert st.pairs == ((1, 2),)
    assert st.isolated == (0,)
    assert st.other == (3, 4, 5, 6, 7)


def test_structure_does_not_depend_on_the_order_events_are_listed_in():
    times = [201.0, 100.0, 200.0]
    st = ce.structure(_gt(times), 1.0)
    assert st.pairs == ((2, 0),) and st.isolated == (1,)


def test_one_call_over_a_pair_is_not_a_split_and_two_calls_are():
    gt = _gt([100.0, 200.0, 201.0])
    joined = ce.pair_score(gt, _det([99.9, 199.9], widths=[0.3, 1.4]), 1.0)
    assert (joined["n_pairs"], joined["n_split"], joined["n_pair_events_hit"]) == (1, 0, 1)
    split = ce.pair_score(gt, _det([99.9, 199.9, 200.9], widths=[0.3, 0.3, 0.3]), 1.0)
    assert (split["n_pairs"], split["n_split"], split["n_pair_events_hit"]) == (1, 1, 2)
    assert split["n_isolated"] == 1 and split["n_isolated_hit"] == 1
    assert split["n_isolated_double"] == 0


def test_a_fragmenting_detector_is_caught_on_the_isolated_events():
    """Two calls on every event split every pair; the control is what tells them apart."""
    gt = _gt([100.0, 200.0, 201.0])
    frag = ce.pair_score(gt, _det([99.8, 100.2, 199.8, 200.2, 200.8, 201.2]), 1.0)
    assert frag["n_split"] == 1
    assert frag["n_isolated_double"] == 1
    assert ce.rates(frag)["isolated_double_rate"] == 1.0


def test_an_event_under_the_floor_takes_its_pair_out_of_the_count():
    gt = _gt([100.0, 200.0, 201.0], floor=6)
    gt.events[1].n_part = 4                       # one event of the pair is "don't care"
    c = ce.pair_score(gt, _det([99.9, 199.9, 200.9]), 1.0)
    assert c["n_pairs"] == 0 and c["n_isolated"] == 1
    assert np.isnan(ce.rates(c)["split_rate"]), "no pairs is NaN, not a split rate of zero"


@pytest.mark.parametrize("stream", sp.STREAMS)
def test_a_set_is_rebuilt_from_its_four_names_and_holds_pairs_and_no_decoys(stream):
    s1, gt1 = ce.make(stream, 1.0, "baseline_quiet", 8000)
    s2, gt2 = ce.make(stream, 1.0, "baseline_quiet", 8000)
    assert [e.time for e in gt1.events] == [e.time for e in gt2.events]
    assert not list(gt1.distractors)
    gaps = np.diff(np.sort([e.time for e in gt1.events]))
    assert np.any(np.abs(gaps - 1.0) < 1e-6), "no gap was set to the separation"


def test_the_search_starts_from_the_shipped_setting_and_reaches_below_two_seconds():
    import search_close_events as sce

    for det in sce.DETECTORS:
        cands = sce.candidates(det)
        assert cands[0] == {}, "the first candidate is the shipped setting"
        assert len(cands) > 1
    assert min(c["win_sec"] for c in sce.candidates("count_sliding")[1:]) < 2.0
    assert min(sce.SELECT_SEPARATIONS_SEC) < 2.0
    assert sce.SELECT_SEED != sce.REPORT_SEED


def test_the_narrow_window_splits_a_pair_the_shipped_setting_joins():
    """The run record's headline, on one recording: count (sliding) on the slow bench at 2 s."""
    p = sp.profile("slow")
    tried = 0
    for seed in range(6000, 6006):
        s, gt = ce.make("slow", 2.0, "baseline_quiet", seed)
        shipped = ce.pair_score(gt, p.module.run_detector("count_sliding", s), 2.0)
        if shipped["n_pairs"] == 0:
            continue
        narrow = ce.pair_score(
            gt, p.module.run_detector("count_sliding", s, win_sec=0.5, merge_gap_sec=0.0), 2.0)
        tried += shipped["n_pairs"]
        assert shipped["n_split"] == 0
        assert narrow["n_split"] >= 1
        assert narrow["n_isolated_double"] == 0
    assert tried >= 1, "no recording here held a pair"
