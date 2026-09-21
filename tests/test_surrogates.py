"""The surrogate screen's generators and controls — synthetic trains only.

Each generator is held to what the plan's Table 1 says it preserves, each Elephant
defect the adapter corrects has a test that fails if the correction is removed, and
the seeding and default-parameter rules are checked directly. Plan:
``docs/proposals/2026-09-10-surrogate-evaluation-overnight.md``.

Nothing here is derived from a recording (FOUNDATIONS §5): every train is drawn
from a seeded ``RandomState`` or written out by hand.
"""

from __future__ import annotations

import functools
import importlib.util
import inspect
import math
import random

import numpy as np
import pytest

pytest.importorskip("elephant")

import elephant.spike_train_surrogates as ss  # noqa: E402
import quantities as pq  # noqa: E402

from bugarach import surrogates as S  # noqa: E402

KEY = ("synthetic", "fast", "cell-a", 0)
WIN = (1000, 7000)          # deliberately not starting at zero
L = WIN[1] - WIN[0]


def _renewal(rng, n, s, e, floor, mean_gap=40, lead=5):
    """A train with a hard floor: gaps of ``floor`` plus a geometric excess."""
    g = floor + rng.geometric(1.0 / mean_gap, n)
    t = s + lead + np.cumsum(g)
    return t[t < e].astype(np.int64)


def _stream(seed=1, n_roi=10, floor=4):
    rng = np.random.RandomState(seed)
    out = [_renewal(rng, rng.randint(20, 120), *WIN, floor) for _ in range(n_roi)]
    out.append(np.array([1500, 1600], np.int64))    # two onsets
    out.append(np.array([], np.int64))              # silent
    return out


def _sparse(rng, n, s, e, gap):
    """Onsets at least ``gap`` apart and at least ``gap`` from both edges."""
    t = s + gap + np.cumsum(gap + rng.randint(0, gap, n))
    return t[t < e - gap].astype(np.int64)


PARAMS = {
    "uniform_dither": dict(J=8),
    "shipped_dither": dict(J=8),
    "dead_time_dither": dict(J=8, f=4),
    "circular_shift": {},
    "rigid_shift": dict(J=8),
    "trial_shift": dict(J=8, f=4),
    "joint_isi": dict(J=8, f=4, sigma=4, use_sqrt=True),
    "isi_dither": dict(J=8, f=4, sigma=8, use_sqrt=False),
    "interval_jitter": dict(J=8),
    "window_shuffle": dict(J=8),
    "pattern_jitter": dict(J=8, f=4),
    "operational_time": dict(J=8, bandwidth=3000),
    "do_nothing": {},
    "interval_shuffle": {},
    "homogeneous_resample": {},
    "edge_thinning": dict(J=8, analysis_window=600),
    "edge_piling": dict(J=8, analysis_window=600),
    "window_circular_shift": dict(analysis_window=600),
}

_ELSEWHERE = {"pattern_jitter": "bugarach.pattern_jitter",
              "operational_time": "bugarach.operational_time"}


def _available(name):
    mod = _ELSEWHERE.get(name)
    if mod is not None and importlib.util.find_spec(mod) is None:
        pytest.skip(f"{mod} is written by another agent and is not here yet")


def _gen(name, trains, window=WIN, key=KEY, **params):
    p = dict(PARAMS[name]); p.update(params)
    return S.generate(name, trains, window, key, **p)


# ---------------------------------------------------------------- the registry

def test_registry_is_the_plans_twelve_and_six():
    assert set(S.CANDIDATES) == {
        "uniform_dither", "shipped_dither", "dead_time_dither", "circular_shift",
        "rigid_shift", "trial_shift", "joint_isi", "isi_dither", "interval_jitter",
        "window_shuffle", "pattern_jitter", "operational_time"}
    assert set(S.CONTROLS) == {
        "do_nothing", "interval_shuffle", "homogeneous_resample", "edge_thinning",
        "edge_piling", "window_circular_shift"}
    assert set(PARAMS) == set(S.CANDIDATES) | set(S.CONTROLS)


@pytest.mark.parametrize("name", sorted(PARAMS))
def test_every_generator_honours_the_interface(name):
    _available(name)
    trains = _stream()
    trains[0] = np.concatenate([[WIN[0] - 50], trains[0], [WIN[1], WIN[1] + 9]])
    res = _gen(name, trains)
    assert isinstance(res, S.SurrogateResult)
    assert len(res.trains) == len(trains)
    assert res.unchanged.shape == res.not_estimable.shape == (len(trains),)
    assert res.unchanged.dtype == bool and res.not_estimable.dtype == bool
    for t in res.trains:
        assert t.dtype == np.int64
        assert np.all(np.diff(t) >= 0)
        assert t.size == 0 or (t.min() >= WIN[0] and t.max() < WIN[1])
    assert res.info["outside_window"] == 3          # half-open: WIN[1] is outside
    assert res.info["generator"] == name
    assert res.unchanged[-1]                         # the silent ROI stays silent


@pytest.mark.parametrize("name", sorted(PARAMS))
def test_same_key_agrees_and_another_draw_differs(name):
    _available(name)
    trains = _stream()
    a = _gen(name, trains)
    b = _gen(name, trains)
    for x, y in zip(a.trains, b.trains):
        np.testing.assert_array_equal(x, y)
    if name == "do_nothing":
        return
    c = _gen(name, trains, key=KEY[:3] + (1,))
    assert any(not np.array_equal(x, y) for x, y in zip(a.trains, c.trains))


@pytest.mark.parametrize("name", sorted(PARAMS))
def test_generators_leave_the_global_generators_as_they_found_them(name):
    _available(name)
    np.random.seed(123); random.seed(123)
    before_np, before_py = np.random.get_state(), random.getstate()
    _gen(name, _stream())
    after_np = np.random.get_state()
    assert before_np[0] == after_np[0]
    np.testing.assert_array_equal(before_np[1], after_np[1])
    assert before_np[2:] == after_np[2:]
    assert random.getstate() == before_py


def test_seed_is_crc32_of_the_keys_repr():
    import zlib
    assert S.seed_of(KEY) == zlib.crc32(repr(KEY).encode())


def test_an_unknown_parameter_is_refused_not_ignored():
    with pytest.raises(TypeError):
        S.generate("uniform_dither", _stream(), WIN, KEY, J=8, jitter=8)
    with pytest.raises(KeyError):
        S.generate("no_such_surrogate", _stream(), WIN, KEY)


# ---------------------------------------------------------------- frame mapping

def test_the_frame_mapping_round_trips_every_frame_of_the_window():
    t = np.arange(L, dtype=np.int64)
    back, n = S._back(S._centred(t), L, "drop")
    np.testing.assert_array_equal(back, t)
    assert n == 0


def test_a_whole_frame_dead_time_survives_the_mapping():
    rng = np.random.RandomState(0)
    a = rng.random_sample(10000) * 100
    for f in (1, 2, 4, 28):
        b = a + f + rng.random_sample(a.size) * 3
        fa, _ = S._back(a, 10**6, "clip")
        diff = np.floor(b).astype(np.int64) - np.floor(a).astype(np.int64)
        assert diff.min() >= f
        assert fa.size == a.size


# ---------------------------------------------------------------- Table 1

def test_uniform_dither_moves_within_J_and_drops_only_at_the_edges():
    rng = np.random.RandomState(2)
    J = 8
    trains = [_sparse(rng, 80, *WIN, gap=2 * J + 3) for _ in range(8)]
    trains.append(np.array([WIN[0], WIN[0] + 1, WIN[1] - 1], np.int64))
    dropped_any = False
    for d in range(30):
        res = _gen("uniform_dither", trains, key=KEY[:3] + (d,), J=J)
        for t, o in zip(trains[:-1], res.trains[:-1]):
            assert o.size == t.size                   # nothing near an edge
            assert np.abs(o - t).max() <= J
        dropped_any |= res.trains[-1].size < 3
    assert dropped_any


def test_shipped_dither_is_jitter_trains_with_inactive_rois_dropped():
    from bugarach.graph import jitter_trains
    rng = np.random.RandomState(3)
    a, b = _renewal(rng, 50, *WIN, 4), _renewal(rng, 50, *WIN, 4)
    with_gap = _gen("shipped_dither", [a, np.array([], np.int64), b], J=8)
    without = _gen("shipped_dither", [a, b], J=8)
    np.testing.assert_array_equal(with_gap.trains[0], without.trains[0])
    np.testing.assert_array_equal(with_gap.trains[2], without.trains[1])
    # and it is jitter_trains, drawn from one RandomState seeded by the key
    expect = jitter_trains([a.astype(float), b.astype(float)], 8, float(WIN[0]),
                           float(WIN[1]), np.random.RandomState(S.seed_of(KEY)))
    for got, x in zip(without.trains, expect):
        want = np.sort(WIN[0] + np.mod(np.floor(x - WIN[0] + 0.5).astype(np.int64), L))
        np.testing.assert_array_equal(got, want)
    assert all(o.size == t.size for o, t in zip(without.trains, [a, b]))  # wraps


def test_dead_time_dither_never_drops_and_keeps_the_dead_time():
    trains = _stream(floor=6)
    trains.append(np.array([WIN[0], WIN[0] + 6, WIN[1] - 7, WIN[1] - 1], np.int64))
    for d in range(10):
        res = _gen("dead_time_dither", trains, key=KEY[:3] + (d,), J=8, f=4)
        for t, o in zip(trains, res.trains):
            assert o.size == t.size
            if t.size > 1:
                assert np.diff(o).min() >= 4
                assert np.abs(o - t).max() <= 8      # cannot jump a neighbour


def test_dead_time_in_effect_is_reported_where_elephant_caps_it():
    trains = [np.array([100, 102, 150, 300], np.int64) + WIN[0],
              np.array([100, 150, 300], np.int64) + WIN[0]]
    res = _gen("dead_time_dither", trains, J=8, f=4)
    np.testing.assert_array_equal(res.info["dead_time_in_effect"], [2.0, 4.0])
    np.testing.assert_array_equal(res.info["dead_time_capped"], [True, False])


@pytest.mark.parametrize("name", ["dead_time_dither", "trial_shift", "joint_isi",
                                  "isi_dither", "pattern_jitter"])
def test_zero_dead_time_is_refused(name):
    _available(name)
    with pytest.raises(ValueError, match="dead time"):
        _gen(name, _stream(), f=0)


def test_circular_shift_keeps_every_cyclic_interval():
    trains = _stream()
    res = _gen("circular_shift", trains)
    for t, o in zip(trains, res.trains):
        assert o.size == t.size
        if t.size > 1:
            def cyc(x):
                x = np.sort(x - WIN[0])
                return np.sort(np.diff(np.concatenate([x, [x[0] + L]])))
            np.testing.assert_array_equal(cyc(t), cyc(o))


def test_circular_shift_is_the_assessors_own_function(monkeypatch):
    from bugarach import assess
    calls = []
    real = assess.circular_shift_trains

    def spy(trains, win_dur, rng):
        calls.append(len(trains))
        return real(trains, win_dur, rng)

    monkeypatch.setattr(S, "circular_shift_trains", spy)
    _gen("circular_shift", _stream())
    assert calls == [len(_stream())]


def test_assess_coactivity_draws_its_null_through_the_extracted_function(monkeypatch):
    """The extraction must be load-bearing: the assessor calls it, once per surrogate."""
    from pathlib import Path
    from copy import deepcopy
    from bugarach import assess
    from bugarach.store import load_slice

    s = deepcopy(load_slice(Path(__file__).parent / "fixtures" / "synth_fastcal_s1.mat",
                            dt=0.1))
    for r in s.regions:
        r.name = "baseline"
    calls = []
    real = assess.circular_shift_trains

    def spy(trains, win_dur, rng):
        calls.append(len(trains))
        return real(trains, win_dur, rng)

    monkeypatch.setattr(assess, "circular_shift_trains", spy)
    assess.assess_coactivity(s, n_surrogates=4, min_rois=(3,))
    assert len(calls) == 4 and len(set(calls)) == 1 and calls[0] > 0


def test_rigid_shift_moves_the_whole_train_by_one_offset_and_drops_at_edges():
    trains = _stream()
    for d in range(10):
        res = _gen("rigid_shift", trains, key=KEY[:3] + (d,), J=8)
        for t, o in zip(trains, res.trains):
            if o.size == 0:
                continue
            # one offset c: o is exactly the in-window part of t + c
            cands = {int(o[0] - x) for x in t}
            ok = [c for c in cands if abs(c) <= 8 and np.array_equal(
                o, (t + c)[(t + c >= WIN[0]) & (t + c < WIN[1])])]
            assert ok


def test_pseudo_trials_are_cut_only_at_silences_longer_than_2J_plus_f():
    # J = 3, f = 4: the threshold is 10 frames. A gap of exactly 10 is not a cut.
    t = np.array([100, 110, 121, 125, 200], np.int64)
    np.testing.assert_array_equal(S.pseudo_trials(t, 3, 4), [0, 0, 1, 1, 2])


def test_trial_shift_never_duplicates_an_onset_on_a_trial_boundary():
    """Elephant's trial shifting duplicates an onset sitting on a trial boundary.
    Here the partition is of onsets, so the count is exact and no frame repeats."""
    J, f = 3, 4
    t = WIN[0] + np.array([100, 110, 121, 125, 200, 211, 222, 233], np.int64)
    for d in range(200):
        res = _gen("trial_shift", [t], key=KEY[:3] + (d,), J=J, f=f)
        o = res.trains[0]
        assert o.size == t.size
        assert np.unique(o).size == o.size
        lab = S.pseudo_trials(t, J, f)
        # within a trial the intervals are kept; between trials the gap stays > f
        for k in np.unique(lab):
            np.testing.assert_array_equal(np.diff(o[lab == k]), np.diff(t[lab == k]))
        assert np.diff(o).min() >= f
        assert np.abs(o - t).max() <= J


def test_trial_shift_drops_onsets_pushed_out_and_never_wraps():
    t = np.array([WIN[0], WIN[1] - 1], np.int64)
    sizes = {_gen("trial_shift", [t], key=KEY[:3] + (d,), J=8, f=4).trains[0].size
             for d in range(40)}
    assert min(sizes) < 2


# ---------------------------------------------------------------- joint-ISI

def test_jisi_min_onsets_mirrors_elephant():
    assert S.JISI_MIN_ONSETS == ss.JointISI.MIN_SPIKES


@pytest.mark.parametrize("name", ["joint_isi", "isi_dither"])
def test_joint_isi_keeps_ends_count_and_dead_time(name):
    trains = _stream(floor=4)[:-2]
    for d in range(3):
        res = _gen(name, trains, key=KEY[:3] + (d,), bin_width=4)
        for t, o, ne in zip(trains, res.trains, res.not_estimable):
            assert o.size == t.size
            assert o[0] == t[0] and o[-1] == t[-1]
            assert np.diff(o).min() >= 4
        assert (~res.not_estimable).any()
        assert (~res.unchanged).any()


def test_a_two_onset_train_through_jointisi_is_marked_not_estimable():
    """JointISI hands back a train of fewer than three onsets unchanged, silently."""
    t = [np.array([1500, 1600], np.int64)]
    res = _gen("joint_isi", t)
    assert res.unchanged[0] and res.not_estimable[0]
    assert res.info["jisi_too_few"][0]
    assert res.info["counts"]["too_few"] == 1


def test_a_fallback_to_uniform_dither_is_counted_and_marked():
    trains = _stream()[:3]
    # a truncation far below every interval pair: every step falls back
    res = _gen("joint_isi", trains, truncation=8.0)
    assert (res.info["jisi_fallback_steps"] > 0).all()
    assert res.not_estimable.all()
    # a bin wider than the dither: no window to draw from, every step falls back
    res = _gen("joint_isi", trains, bin_width=12.0)
    assert (res.info["jisi_fallback_steps"] > 0).all()
    assert res.not_estimable.all()


def test_a_smoothing_width_that_moves_nothing_is_marked():
    """With almost no smoothing the only mass near a pair is the pair itself, so
    JointISI runs, draws, and steps nowhere. Strictly increasing intervals put
    every pair on its own anti-diagonal of the histogram, so no pair lends another
    a place to go."""
    t = [WIN[0] + 100 + np.cumsum(60 + 10 * np.arange(10)).astype(np.int64)]
    res = _gen("joint_isi", t, sigma=0.01, use_sqrt=False)
    assert res.info["jisi_fallback_steps"][0] == 0
    assert res.unchanged[0]
    assert res.info["jisi_moved_nothing"][0]
    assert res.not_estimable[0]


def test_an_oversized_histogram_is_declared_intractable_not_run():
    trains = _stream()[:2]
    res = _gen("joint_isi", trains, max_bytes=1e3)
    assert res.info["jisi_intractable"].all()
    assert res.not_estimable.all() and res.unchanged.all()


def test_isi_dither_smooths_a_float_histogram():
    """Elephant 1.2.1 smooths ISI dither's histogram into an integer array. Without
    the adapter's float histogram, most of these ROIs fall back to uniform dither."""
    trains = _stream(floor=4)[:-2]
    st = S._spiketrain(S._centred(trains[0] - WIN[0]), L)
    u = pq.s                     # one frame, in the adapter's convention
    raw = ss.JointISI(st, dither=8.0 * u, truncation_limit=400.0 * u, n_bins=100,
                      sigma=8.0 * u, alternate=True, use_sqrt=False, method="window",
                      cutoff=True, refractory_period=4.0 * u, isi_dithering=True)
    assert raw.joint_isi_histogram().dtype.kind == "i"      # the defect, as shipped
    S.clear_cache()
    res = _gen("isi_dither", trains, bin_width=4, use_sqrt=False, sigma=8)
    assert res.info["counts"]["fallback"] == 0


def test_the_float_histogram_reproduces_elephant_on_the_joint_path():
    trains = _stream(floor=4)
    u = pq.s
    for t in trains[:4]:
        st = S._spiketrain(S._centred(t - WIN[0]), L)
        o = ss.JointISI(st, dither=8.0 * u, truncation_limit=600.0 * u, n_bins=150,
                        sigma=6.0 * u, alternate=True, use_sqrt=True, method="window",
                        cutoff=True, refractory_period=4.0 * u, isi_dithering=False)
        np.testing.assert_allclose(S._float_smoothed_histogram(o),
                                   o.joint_isi_histogram(), rtol=0, atol=1e-12)


# ---------------------------------------------------------------- bin-based

def test_interval_jitter_keeps_every_bin_count_in_a_window_not_starting_at_zero():
    """``jitter_spikes`` counts a nonzero window start twice and misplaces onsets.
    The adapter hands it a window starting at zero, so bins stay put."""
    J = 8
    b = S.interval_jitter_bin(J)
    trains = _stream()
    moved = False
    for d in range(5):
        res = _gen("interval_jitter", trains, key=KEY[:3] + (d,), J=J)
        for t, o in zip(trains, res.trains):
            np.testing.assert_array_equal(np.bincount((t - WIN[0]) // b, minlength=L),
                                          np.bincount((o - WIN[0]) // b, minlength=L))
            moved |= not np.array_equal(t, o)
    assert moved


def test_interval_jitter_bin_is_root2_J_in_whole_frames():
    assert S.interval_jitter_bin(1) == 1
    assert S.interval_jitter_bin(8) == 11
    assert S.interval_jitter_bin(28) == 40


def test_window_shuffle_width_is_root2_J_in_whole_frames():
    assert S.window_shuffle_width(1) == 2
    assert S.window_shuffle_width(8) == 12
    assert S.window_shuffle_width(28) == 40


def test_window_shuffle_keeps_window_counts_on_grid_and_in_the_last_partial_window():
    """``bin_shuffling`` floor-divides seconds and puts on-grid onsets a frame early,
    and drops what its last, partial window pushes past the end. Onsets on every
    window's first frame, and in the last partial window, must stay where they are."""
    J = 8
    W = S.window_shuffle_width(J)
    win = (WIN[0], WIN[0] + 6005)
    L2 = win[1] - win[0]
    assert L2 % W != 0                               # there is a partial last window
    t = np.concatenate([np.arange(0, L2, W), [L2 - 1, L2 - 2]]).astype(np.int64) + win[0]
    t = np.unique(t)
    moved = False
    for d in range(10):
        res = _gen("window_shuffle", [t], window=win, key=KEY[:3] + (d,), J=J)
        o = res.trains[0]
        assert o.size == t.size
        np.testing.assert_array_equal(np.bincount((t - win[0]) // W),
                                      np.bincount((o - win[0]) // W,
                                                  minlength=(L2 - 1) // W + 1))
        assert res.info["dropped"][0] == 0
        assert res.info["last_partial_window"] == L2 % W
        moved |= not np.array_equal(t, o)
    assert moved


# ---------------------------------------------------------------- written elsewhere

@pytest.mark.parametrize("name", ["pattern_jitter", "operational_time"])
def test_the_lazily_imported_generators_keep_the_count(name):
    _available(name)
    trains = _stream()
    res = _gen(name, trains)
    for t, o in zip(trains, res.trains):
        assert o.size == t.size


def test_operational_time_marks_rois_it_cannot_estimate():
    """Fewer than two onsets leaves the leave-one-out rate at zero, so the method
    hands the train back unchanged. That ROI must be not estimable, never scored as
    preserving anything; about half the real baseline ROIs are like this."""
    _available("operational_time")
    trains = [np.array([], np.int64), np.array([WIN[0] + 700], np.int64)] + _stream()[:2]
    res = _gen("operational_time", trains)
    assert res.not_estimable[:2].all() and res.unchanged[:2].all()
    assert not res.not_estimable[2:].any()
    assert res.info["flat_at_onset"].shape == (len(trains),)
    assert np.isnan(res.info["width_op"][:2]).all()
    assert (res.info["width_op"][2:] > 0).all()


# ---------------------------------------------------------------- Table 2

def test_do_nothing_returns_its_input():
    trains = _stream()
    res = _gen("do_nothing", trains)
    for t, o in zip(trains, res.trains):
        np.testing.assert_array_equal(t, o)
    assert res.unchanged.all()


def test_interval_shuffle_permutes_within_train_intervals_only():
    """Elephant permutes the leading gap too, which would move the first onset."""
    trains = _stream()
    res = _gen("interval_shuffle", trains)
    for t, o in zip(trains, res.trains):
        assert o.size == t.size
        if t.size:
            assert o[0] == t[0] and o[-1] == t[-1]
            np.testing.assert_array_equal(np.sort(np.diff(t)), np.sort(np.diff(o)))
    assert (~res.unchanged[:-2]).all()


def test_homogeneous_resample_keeps_the_count():
    trains = _stream()
    res = _gen("homogeneous_resample", trains)
    assert [o.size for o in res.trains] == [t.size for t in trains]
    assert (~res.unchanged[:-2]).all()


def test_edge_thinning_drops_only_near_analysis_window_edges():
    J, A = 8, 600
    edges = np.arange(0, L + 1, A)
    trains = _stream()
    lost = 0
    for d in range(10):
        res = _gen("edge_thinning", trains, key=KEY[:3] + (d,), J=J, analysis_window=A)
        for t, o in zip(trains, res.trains):
            rel = t - WIN[0]
            far = np.min(np.abs(rel[:, None] - edges[None, :]), axis=1) > J + 1
            assert o.size >= int(far.sum())
            lost += t.size - o.size
    assert lost > 0


def test_edge_piling_keeps_the_count_and_piles_on_edge_frames():
    J, A = 8, 600
    t = (np.arange(0, L, A) + WIN[0]).astype(np.int64)     # one onset per window start
    piled = 0
    for d in range(20):
        res = _gen("edge_piling", [t], key=KEY[:3] + (d,), J=J, analysis_window=A)
        o = res.trains[0]
        assert o.size == t.size
        piled += int(np.isin(o - WIN[0], np.arange(0, L, A)).sum())
    assert piled > 20 * t.size * 0.4                         # about half clamp


def test_window_circular_shift_keeps_every_analysis_window_count():
    A = 600
    trains = _stream()
    res = _gen("window_circular_shift", trains, analysis_window=A)
    for t, o in zip(trains, res.trains):
        np.testing.assert_array_equal(np.bincount((t - WIN[0]) // A, minlength=L // A),
                                      np.bincount((o - WIN[0]) // A, minlength=L // A))


# ---------------------------------------------------------------- Elephant's defaults

_SPIED = ["dither_spikes", "dither_spike_train", "jitter_spikes", "bin_shuffling",
          "shuffle_isis", "randomise_spikes", "JointISI"]


def test_call_explicit_refuses_a_default():
    with pytest.raises(TypeError, match="defaults"):
        S._call_explicit(ss.dither_spikes, S._spiketrain([0.5, 3.5], 10),
                         dither=S._frames(2))


def test_no_elephant_default_is_ever_reached(monkeypatch):
    """Every Elephant callable the adapter touches is replaced by a spy that fails
    if any parameter was left to its (millisecond) default."""
    seen = set()

    def spy_of(name, fn):
        sig = inspect.signature(fn)

        @functools.wraps(fn)
        def spy(*args, **kwargs):
            bound = sig.bind(*args, **kwargs)
            missing = [p for p in sig.parameters
                       if p != "self" and p not in bound.arguments]
            assert not missing, f"{name} reached Elephant defaults for {missing}"
            seen.add(name)
            return fn(*args, **kwargs)
        return spy

    # the method first, on the real class, before the class name is replaced
    monkeypatch.setattr(ss.JointISI, "dithering",
                        spy_of("dithering", ss.JointISI.dithering))
    for name in _SPIED:
        monkeypatch.setattr(ss, name, spy_of(name, getattr(ss, name)))
    S.clear_cache()
    for name in PARAMS:
        if name in _ELSEWHERE and importlib.util.find_spec(_ELSEWHERE[name]) is None:
            continue
        _gen(name, _stream())
    assert seen == set(_SPIED) | {"dithering"}
