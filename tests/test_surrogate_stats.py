"""The surrogate screen's measurements — synthetic data only.

What these pin: each Table 3 statistic counts what the plan says on hand-built
frame-index trains (same-frame duplicates as zero intervals); the yardsticks'
arithmetic (rank P, band, Holm, mouse-grouped splits); the destruction measure's
two anchors (do-nothing keeps the planted excess, the whole-window circular
shift removes it); and the three extractions the build made — the
generation-window rule, the Fano helpers, and the simulator's opt-in floor.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import numpy as np
import pytest

from bugarach import surrogate_stats as ss
from bugarach.simulate import simulate_coordination

FS = {"a": 2, "b": 4}


def _summ(trains, window=(0, 1000), dt=0.1, fs=FS, **kw):
    return ss.set_stats(ss.summarize([np.asarray(t, np.int64) for t in trains],
                                     window, dt, fs, rng=ss.rng_of(0), **kw), fs)


# ---- the statistics ---------------------------------------------------------

def test_same_frame_duplicates_are_zero_intervals():
    """[5, 5, 9]: intervals 0 and 4. At f=2 one of two is sub-floor; at f=4,
    one of two is still sub-floor (0 < 4) and the other sits in [4, 8)."""
    st = _summ([[5, 5, 9]])
    assert st["subfloor@a"][0] == pytest.approx(0.5)
    assert st["subfloor@b"][0] == pytest.approx(0.5)
    assert st["band_f_2f@a"][0] == pytest.approx(0.0)
    assert st["band_f_2f@b"][0] == pytest.approx(0.5)


def test_interval_counts_pool_over_rois_and_coverage_counts_rois():
    # ROI 0: intervals 1, 3 (one sub-floor at f=2, one in [2,4)); ROI 1: one
    # onset, no interval; ROI 2: interval 10.
    st = _summ([[0, 1, 4], [7], [20, 30]])
    assert st["subfloor@a"][0] == pytest.approx(1 / 3)
    assert st["band_f_2f@a"][0] == pytest.approx(1 / 3)
    assert st["subfloor@a"][1] == pytest.approx(2 / 3)          # coverage


def test_inside_the_previous_event_uses_the_preceding_width():
    # intervals 3 and 10; preceding widths 5 and 5 -> the first is inside.
    st = _summ([[0, 3, 13]], widths=[np.array([5.0, 5.0, 5.0])])
    assert st["inside_width"][0] == pytest.approx(0.5)
    assert np.isnan(_summ([[0, 3, 13]])["inside_width"][0])     # no widths, no number


def test_edge_density_reads_one_when_flat_and_high_when_piled():
    dt = 0.1                                    # 5 s bands = 50 frames
    flat = [np.arange(0, 6000, 25)]
    piled = [np.concatenate([np.arange(0, 50, 5), np.arange(5950, 6000, 5),
                             np.arange(1000, 5000, 400)])]
    assert _summ(flat, (0, 6000), dt)["edge_density"][0] == pytest.approx(1.0, abs=0.05)
    assert _summ(piled, (0, 6000), dt)["edge_density"][0] > 5.0


def test_serial_dependence_sees_alternation_and_not_order_free_trains():
    """Alternating short/long intervals correlate negatively at lag 1, beyond
    what the same intervals shuffled read."""
    iv = np.tile([3, 30], 20)
    t = np.concatenate([[0], np.cumsum(iv)])
    alt = ss.serial_excess_batch([np.diff(t)], ss.rng_of(1))[0]
    assert alt < -0.5
    rng = np.random.RandomState(4)
    shuffled = np.diff(np.concatenate([[0], np.cumsum(rng.permutation(iv))]))
    assert abs(ss.serial_excess_batch([shuffled], ss.rng_of(1))[0]) < abs(alt)


def test_serial_dependence_needs_five_onsets():
    assert np.isnan(ss.serial_excess_batch([np.array([3, 4, 5])], ss.rng_of(0))[0])
    assert ss.serial_excess_batch([np.array([3, 40, 5, 60])], ss.rng_of(0))[0] == \
        pytest.approx(ss.serial_excess_batch([np.array([3, 40, 5, 60])],
                                             ss.rng_of(0))[0])


def test_rate_profile_is_the_shared_fano():
    """The Fano statistic is `count_dispersion.fano` on `burst_rows`, the same
    functions the background fitter uses."""
    from bugarach.count_dispersion import burst_rows, fano

    rng = np.random.RandomState(0)
    tr = [np.sort(rng.randint(0, 36000, size=40)) for _ in range(3)]
    st = _summ(tr, (0, 36000), 0.1)
    rows = burst_rows([([v * 0.1 for v in tr], 3600.0)], 60.0)
    assert st["fano_60s"][0] == pytest.approx(fano(rows))


def test_ks_distance_by_hand():
    assert ss.ks_distance([1, 2, 3], [1, 2, 3]) == 0.0
    assert ss.ks_distance([1, 1], [5, 5]) == 1.0
    assert ss.ks_distance([1, 2, 3, 4], [3, 4, 5, 6]) == pytest.approx(0.5)


def test_ks_paired_reads_zero_for_identical_draws():
    real = [np.array([0, 3, 9, 20]), np.array([1, 5, 30])]
    sums, n = ss.ks_paired(real, [real] * 4)
    assert n == 2
    assert np.allclose(sums, 0.0)


# ---- movement ---------------------------------------------------------------

def test_movement_do_nothing_reads_zero_and_a_shift_reads_its_size():
    real = [np.array([10, 20, 30]), np.array([5])]
    m0 = ss.movement(real, real)
    assert m0["share_moved"] == 0.0 and m0["rms_disp_frames"] == 0.0
    assert m0["share_rois_unchanged"] == 1.0
    m3 = ss.movement(real, [v + 3 for v in real])
    assert m3["share_moved"] == 1.0
    assert m3["rms_disp_frames"] == pytest.approx(3.0)
    assert m3["share_rois_unchanged"] == 0.0


# ---- yardsticks -------------------------------------------------------------

def test_paired_p_by_hand():
    assert ss.paired_p(1.0, [1.0] * 19) == 1.0          # do-nothing is never flagged
    assert ss.paired_p(100.0, np.arange(19)) == pytest.approx(2 / 20)
    assert ss.paired_p(-1.0, np.arange(19)) == pytest.approx(2 / 20)
    assert ss.paired_p(9.0, np.arange(19)) == pytest.approx(1.0)
    assert np.isnan(ss.paired_p(np.nan, [1, 2]))


def test_a_correction_that_cannot_reach_alpha_is_detected_before_the_run():
    """The arithmetic that was available on 2026-09-10 and computed on 2026-09-12.

    At 100 mouse splits, K = 99 and a family of 65 checks per grid cell — the settings
    the overnight screen actually ran — the Holm-corrected floors are 0.64 and 1.00, so
    no corrected flag was reachable for any candidate, the known-bad control included.
    """
    bad = ss.correction_reach(65, 100, 99)
    assert bad["band_floor"] == pytest.approx(1 / 101)
    assert bad["paired_floor"] == pytest.approx(2 / 100)
    assert bad["band_floor_holm"] == pytest.approx(65 / 101)
    assert bad["paired_floor_holm"] == pytest.approx(1.0)        # capped at 1
    assert not bad["band_reaches"] and not bad["paired_reaches"]
    assert bad["splits_needed"] == 1300 and bad["K_needed"] == 2600

    # Correcting within scope rather than across all five gives a family of 13. The
    # sample it needs is 260 and 520, NOT 259 and 519: at 259 splits the adjusted floor
    # is 13/260 = exactly alpha, and the flag test is strict, so nothing fires. Stage 2
    # of the probe ran at 259/519 and flagged the known-bad control 0 of 13 times under
    # Holm while flagging it 7 and 11 times raw — this is that lesson, as arithmetic.
    edge = ss.correction_reach(13, 259, 519)
    assert edge["band_floor_holm"] == pytest.approx(0.05)
    assert edge["paired_floor_holm"] == pytest.approx(0.05)
    assert not edge["band_reaches"] and not edge["paired_reaches"]

    ok = ss.correction_reach(13, 260, 520)
    assert ok["splits_needed"] == 260 and ok["K_needed"] == 520
    assert ok["band_reaches"] and ok["paired_reaches"]
    assert ok["band_floor_holm"] < 0.05 and ok["paired_floor_holm"] < 0.05

    # One short, in each direction independently, must fail.
    assert not ss.correction_reach(13, 259, 520)["band_reaches"]
    assert not ss.correction_reach(13, 260, 519)["paired_reaches"]
    # And the smallest-sample helper agrees with a brute-force search.
    for m in (1, 7, 8, 13, 20, 65):
        s = ss.correction_reach(m, 10_000, 10_000)
        assert s["splits_needed"] == next(n for n in range(1, 3000)
                                          if m / (n + 1) < ss.ALPHA)
        assert s["K_needed"] == next(n for n in range(1, 6000)
                                     if 2 * m / (n + 1) < ss.ALPHA)

    for args in ((0, 100, 99), (13, 0, 99), (13, 100, 0)):
        with pytest.raises(ValueError):
            ss.correction_reach(*args)


def test_holm_by_hand():
    adj = ss.holm([0.01, 0.04, np.nan, 0.03])
    # three tests: 0.01*3 = 0.03, 0.03*2 = 0.06, max(0.06, 0.04*1) = 0.06
    assert adj[0] == pytest.approx(0.03)
    assert adj[3] == pytest.approx(0.06)
    assert adj[1] == pytest.approx(0.06)
    assert np.isnan(adj[2])


def test_band_and_band_p():
    d = np.linspace(-1, 1, 101)
    b = ss.band(d)
    assert b["q025"] == pytest.approx(-0.95) and b["q975"] == pytest.approx(0.95)
    assert ss.band_p(5.0, d) == pytest.approx(1 / 102)
    assert ss.band_p(0.0, d) == pytest.approx(1.0)


def test_mouse_splits_are_grouped_stratified_and_seeded():
    mice = [f"m{i}" for i in range(10)]
    strata = {m: ("G1" if i < 6 else "G2") for i, m in enumerate(mice)}
    sp = ss.mouse_splits(mice, 20, key=("t",), strata=strata)
    assert sp == ss.mouse_splits(mice, 20, key=("t",), strata=strata)
    for a, b in sp:
        assert not (a & b) and (a | b) == set(mice)
        assert sum(strata[m] == "G1" for m in a) == 3
        assert sum(strata[m] == "G2" for m in a) == 2
    assert len({frozenset(a) for a, _ in sp}) > 1


def _synthetic_recs(n_mice=8, per_mouse=2, n_roi=12, n_frames=6000, seed=0):
    rng = np.random.RandomState(seed)
    recs = []
    for m in range(n_mice):
        for j in range(per_mouse):
            counts = rng.poisson(15, size=n_roi)
            tr = ss.floor_renewal_trains(counts, n_frames, 0.1, 4, rng)
            recs.append(ss.RecordingTrains(
                recording_id=f"r{m}_{j}", mouse=f"m{m}",
                group="G1" if m % 2 else "G2", dt=0.1, window=(0, n_frames),
                trains=tr, stream="events"))
    return recs


def test_exchangeable_negatives_report_rates():
    recs = _synthetic_recs()
    real = {r.recording_id: ss.summarize(r.trains, r.window, r.dt, FS,
                                         rng=ss.rng_of(r.recording_id)) for r in recs}
    splits = ss.mouse_splits({r.mouse for r in recs}, 30, key=("n",))
    diffs, halves = ss.split_diffs(real, recs, splits, FS)
    ho = ss.negative_rates_heldout(halves, FS)
    for nm in ss.stat_names(FS):
        assert ho[nm]["n"] == 30
        for k in ("band", "paired"):
            v = ho[nm][k]
            assert np.isnan(v) or 0.0 <= v <= 1.0
    sy = ss.negative_rates_synthetic(recs, diffs, FS, 4, n_rep=2, n_draws=5)
    assert set(sy) == set(ss.stat_names(FS)) | {"ks_intervals"}
    assert all(np.isnan(v["paired"]) or 0.0 <= v["paired"] <= 1.0 for v in sy.values())


def test_floor_renewal_trains_keep_counts_and_the_floor():
    rng = np.random.RandomState(3)
    tr = ss.floor_renewal_trains([0, 1, 5, 40], 2000, 0.1, 7, rng)
    assert [v.size for v in tr] == [0, 1, 5, 40]
    for v in tr:
        assert np.all(v >= 0) and np.all(v < 2000)
        if v.size > 1:
            assert np.diff(v).min() >= 7


# ---- destruction ------------------------------------------------------------

@pytest.fixture(scope="module")
def twins():
    rng = np.random.RandomState(1)
    counts = rng.poisson(12, size=20)
    pl, un, gt = ss.destruction_twins(20, 9000, 0.1, 4, counts, 0.5, seed=11)
    return pl, un, gt


def test_destruction_twins_hold_the_floor_and_plant_visibly(twins):
    pl, un, gt = twins
    for tr in (pl, un):
        for v in tr:
            if v.size > 1:
                assert np.diff(v).min() >= 4
            assert np.all((v >= 0) & (v < 9000))
    assert gt.params["n_bg_replaced"] > 0
    before = ss.coact_excess(pl, 9000, 0.1, min_rois=(3,), n_surrogates=50)[3]
    base = ss.coact_excess(un, 9000, 0.1, min_rois=(3,), n_surrogates=50)[3]
    assert before > base


def test_do_nothing_keeps_the_excess_and_circular_shift_removes_it(twins):
    pl, un, _ = twins
    kw = dict(n_draws=3, cell_id="t", n_assess_surrogates=50, min_rois=(3,))
    keep = ss.destruction("do_nothing", {}, {0.5: (pl, un)}, 9000, 0.1, **kw)
    gone = ss.destruction("circular_shift", {}, {0.5: (pl, un)}, 9000, 0.1, **kw)
    assert keep["0.5"]["3"]["planted_visible"]
    assert keep["0.5"]["3"]["retained"] == pytest.approx(1.0)
    assert gone["0.5"]["3"]["retained"] < 0.3


# ---- surrogates only through the adapter -------------------------------------

def test_draws_go_through_generate_and_are_reproducible():
    recs = _synthetic_recs(n_mice=2, per_mouse=1)
    a = ss.draw_surrogates("circular_shift", recs, 3, "c", {})
    b = ss.draw_surrogates("circular_shift", recs, 3, "c", {})
    for rid in a.trains:
        for k in range(3):
            for x, y in zip(a.trains[rid][k], b.trains[rid][k]):
                assert np.array_equal(x, y)
    assert a.K == 3 and a.peak_bytes > 0


def test_score_cell_do_nothing_is_never_flagged_by_the_paired_yardstick():
    recs = _synthetic_recs()
    d = ss.draw_surrogates("do_nothing", recs, 5, "dn", {})
    res = ss.score_cell(recs, d, FS, "dn", {"all": [r.recording_id for r in recs]}, {})
    for nm, row in res["scopes"]["all"].items():
        assert row["paired_p"] == pytest.approx(1.0) or np.isnan(row["paired_p"]), nm
        assert row["paired_p_holm"] == pytest.approx(1.0) or np.isnan(row["paired_p"])
    assert res["movement"]["share_moved"] == 0.0


def test_holm_corrects_within_each_scope_and_not_across_them():
    """Tony's call, 2026-09-12, and the arithmetic that forced it.

    FOUNDATIONS §9 wants each group's number reported beside the pooled one. That is a
    reporting requirement; it does not make the scopes one family. Correcting across them
    turned 13 statistics into 65 checks, and at 100 splits with K <= 99 that put the
    corrected floors at 0.64 and 1.00 — so nothing could flag, the known-bad control
    least of all, and a whole night's corrected rates were zero by construction.

    Uniform dither at J = 20 frames on floor-4 trains leaks sub-floor intervals, so some
    raw P are at the 2/(K+1) floor and the two family sizes give visibly different
    adjusted values. With 39 draws that floor is 0.05: eight statistics lift it to 0.4,
    twenty-four lift it past 1.
    """
    recs = _synthetic_recs(n_mice=6, per_mouse=2)
    d = ss.draw_surrogates("uniform_dither", recs, 39, "ud", {"J": 20})
    scopes = {"all": [r.recording_id for r in recs],
              "G1": [r.recording_id for r in recs if r.group == "G1"],
              "G2": [r.recording_id for r in recs if r.group == "G2"]}
    res = ss.score_cell(recs, d, FS, "ud", scopes, {})
    assert set(res["scopes"]) == set(scopes)

    # Each scope's adjustment is Holm over THAT scope's statistics and nothing else.
    for yard in ("paired_p", "band_p"):
        for sc in res["scopes"]:
            names_sc = list(res["scopes"][sc])
            want = ss.holm([res["scopes"][sc][nm][yard] for nm in names_sc])
            for nm, w in zip(names_sc, want):
                got = res["scopes"][sc][nm][yard + "_holm"]
                assert (np.isnan(got) and np.isnan(w)) or got == pytest.approx(w), (sc, nm)

    # And the rule this replaced would have been strictly harsher somewhere: if a reader
    # of this test ever flattens the scopes back into one family, that is the assertion
    # that fails. (Band P is NaN here — no split differences are supplied — so the
    # comparison is on the paired yardstick, which is the one with a sample-size floor.)
    keys = [(sc, nm) for sc in res["scopes"] for nm in res["scopes"][sc]]
    across = ss.holm([res["scopes"][sc][nm]["paired_p"] for sc, nm in keys])
    pairs = [(res["scopes"][sc][nm]["paired_p_holm"], float(a))
             for (sc, nm), a in zip(keys, across)
             if np.isfinite(res["scopes"][sc][nm]["paired_p_holm"]) and np.isfinite(a)]
    assert pairs, "no finite paired P to compare the two family sizes with"
    assert any(within < acr - 1e-12 for within, acr in pairs), (
        "within-scope correction is no looser than across-scope — has the family been "
        "flattened back to every statistic in every scope?")
    assert all(within <= acr + 1e-12 for within, acr in pairs)


def test_a_cell_that_cannot_reach_min_K_in_its_budget_says_so():
    """Below min_K an exhausted budget stops the cell and says it fell short —
    the caller records it intractable. No budget runs every draw."""
    recs = _synthetic_recs(n_mice=2, per_mouse=1)
    d = ss.draw_surrogates("circular_shift", recs, 50, "c", {}, min_K=4,
                           time_budget=0.0)
    assert d.K < 4 and "below the minimum" in d.stopped
    full = ss.draw_surrogates("circular_shift", recs, 6, "c", {}, min_K=4)
    assert full.K == 6 and full.stopped == ""


def test_the_serial_null_is_part_of_the_statistic():
    """Identical trains score identically whichever draw they are — the shuffle
    null is seeded per recording, not per draw."""
    rec = _synthetic_recs(n_mice=1, per_mouse=1)[0]
    a = ss.summarize(rec.trains, rec.window, rec.dt, FS, rng=ss.serial_rng(rec))
    b = ss.summarize(rec.trains, rec.window, rec.dt, FS, rng=ss.serial_rng(rec))
    assert a.serial_sum == b.serial_sum and a.n_roi_serial > 0


# ---- the extractions ----------------------------------------------------------

def test_generation_window_keeps_both_fallbacks():
    from bugarach.assess_folder import (NoBaselineRegion, WHOLE_RECORDING_SOURCE,
                                        generation_window)
    from bugarach.store import Region

    s, _ = simulate_coordination(duration_sec=120.0, n_roi=3, seed=1,
                                 n_per_level=(), participation=())
    assert generation_window(s) == (None, WHOLE_RECORDING_SOURCE)
    s.regions = [Region(name="senktide", slot="1", start_sec=0.0, end_sec=60.0)]
    with pytest.raises(NoBaselineRegion, match="senktide"):
        generation_window(s)
    s.regions = [Region(name="baseline", slot="1", start_sec=0.0, end_sec=60.0,
                        analysis_start_sec=10.0, analysis_end_sec=50.0)]
    w, src = generation_window(s)
    assert w == (10.0, 50.0) and "analysis window" in src


def test_the_fitter_imports_the_moved_fano_helpers():
    import bugarach.count_dispersion as cd

    tool = Path(__file__).resolve().parents[1] / "tools" / "fit_background_shape.py"
    spec = importlib.util.spec_from_file_location("_fbs_moved", tool)
    m = importlib.util.module_from_spec(spec)
    sys.modules["_fbs_moved"] = m
    spec.loader.exec_module(m)
    assert m.burst_rows is cd.burst_rows and m.fano is cd.fano
    assert m.MIN_EVENTS_PER_ROI == cd.MIN_EVENTS_PER_ROI


def test_the_floor_is_opt_in_and_existing_seeds_reproduce():
    kw = dict(duration_sec=300.0, n_roi=8, seed=5)
    a, ga = simulate_coordination(**kw)
    b, gb = simulate_coordination(bg_floor_sec=None, **kw)
    for x, y in zip(a.streams["events"].locs, b.streams["events"].locs):
        assert np.array_equal(x, y)
    assert "bg_floor_sec" not in ga.params


def test_the_floor_holds_with_planted_events_replacing_background():
    s, gt = simulate_coordination(duration_sec=1200.0, n_roi=20, bg_floor_sec=0.4,
                                  bg_roi_counts=np.full(20, 30),
                                  participation=(0.5,), n_per_level=(10,),
                                  jitter_sec=0.1, grid_sec=0.1, seed=2)
    for v in s.streams["events"].locs:
        fr = ss.to_frames(v, 0.1)
        if fr.size > 1:
            assert np.diff(fr).min() >= 4
    assert gt.params["n_bg_replaced"] > 0
    # replacing keeps each participant's count unless a neighbour had to go too
    total = sum(len(v) for v in s.streams["events"].locs)
    assert total == 20 * 30 - gt.params["n_bg_dropped"]


def test_the_floor_refuses_what_would_break_it():
    with pytest.raises(ValueError, match="bg_burst_shape"):
        simulate_coordination(bg_floor_sec=0.4, bg_burst_shape=1.0, seed=1)
    with pytest.raises(ValueError, match="hot_window"):
        simulate_coordination(bg_floor_sec=0.4, hot_window=(10, 20),
                              hot_rate_hz=1.0, seed=1)
