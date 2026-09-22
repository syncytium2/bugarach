"""The cumulant estimator behind ``tools/measure_coordination_rates.py``, on trains with known answers.

No data needed: every test builds its own onsets. The bench calibration itself runs inside the
tool, on the workstation, and is recorded with the result.
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
import measure_coordination_rates as m  # noqa: E402

DT = m.DT


def _toy(seed, N=30, T=1800.0, bg=0.01, rate=0.02, k=6, jitter=0.1):
    """Fixed-size shared moments (k of N cells each) on independent Poisson background, in frames."""
    rng = np.random.RandomState(seed)
    L = int(T / DT)
    trains = [list(rng.randint(0, L, rng.poisson(bg * T))) for _ in range(N)]
    times = rng.uniform(5, T - 5, rng.poisson(rate * T))
    for t in times:
        for c in rng.choice(N, k, replace=False):
            trains[c].append(int(round((t + jitter * rng.randn()) / DT)))
    return [np.unique(np.clip(np.array(x, int), 0, L - 1)) for x in trains], L, times.size / T


def test_independent_poisson_counts_have_no_factorial_cumulants():
    X = np.random.RandomState(0).poisson(3.0, 400_000)
    f2, f3 = m.factorial_cumulants(X)
    assert abs(f2) < 0.05 and abs(f3) < 0.2


def test_every_two_cells_are_shifted_at_least_the_spacing_apart():
    rng = np.random.RandomState(1)
    trains = [np.array([100]) for _ in range(20)]
    out = m.shifted(trains, 100_000, 20, rng)
    pos = np.sort(np.array([t[0] for t in out]))
    assert np.diff(pos).min() >= 20


def test_fixed_size_moments_are_recovered_on_a_toy_recording():
    ks, lams = [], []
    for seed in range(4):
        trains, L, lam_true = _toy(seed)
        f2, f3 = m.excess_cumulants(trains, L, int(1.0 / DT), 8, np.random.RandomState(seed))
        got = m.solve(f2, f3, len(trains), 1.0, "fixed")
        ks.append(got["k"])
        lams.append(got["lam"] / lam_true)
    assert np.median(ks) == pytest.approx(6, rel=0.15)
    assert np.median(lams) == pytest.approx(1, rel=0.2)


def test_background_alone_reports_no_shared_moments():
    trains, L, _ = _toy(7, rate=0.0)
    f2, f3 = m.excess_cumulants(trains, L, int(1.0 / DT), 8, np.random.RandomState(7))
    exp_pairs = 0.02 * 1.0 * 6 * 5          # what the toy's shared moments would have added
    assert abs(f2) < 0.1 * exp_pairs


def test_a_slow_onset_within_one_frame_of_a_fast_onset_counts_once():
    fast = [np.array([10, 50])]
    slow = [np.array([11, 30, 52])]
    assert m.merge_streams(fast, slow)[0].tolist() == [10, 30, 50, 52]


@pytest.mark.parametrize("bench_name", ["bugarach.bench", "bugarach.bench_slow"])
def test_the_bench_calibration_passes_at_the_primary_window(bench_name):
    """The check the tool records, on fewer seeds: planted share recovered at 1 s, fixed model.

    Found failing on 2026-09-22 twice before it passed — surrogate shifts that kept cells of one
    event together subtracted a third of the signal (``shifted``'s docstring)."""
    res = [m._sim((bench_name, g, s)) for g in ("baseline_quiet", "baseline_busy") for s in (1, 2, 3)]
    cal = m.calibrate(res, m.PRIMARY_W, "fixed")
    assert cal["passed"], cal
    summary = m.summarize([r for r, _ in res], m.PRIMARY_W, probe_now=0.06)
    for model in m.MODELS:
        assert np.isfinite(summary[model]["coordinated_share_hz"])
        assert summary[model]["quiet_background_hz"] < summary["quiet_raw_hz"]


def test_shape_usable_is_fit_background_shapes_own_floors():
    """Not a copy of the numbers — the floors are imported, so they cannot drift apart."""
    import fit_background_shape as fb

    assert m.shape_usable(fb.MIN_ROIS, fb.MIN_EVENTS, fb.MIN_DURATION_SEC)
    assert not m.shape_usable(fb.MIN_ROIS - 1, fb.MIN_EVENTS, fb.MIN_DURATION_SEC)
    assert not m.shape_usable(fb.MIN_ROIS, fb.MIN_EVENTS - 1, fb.MIN_DURATION_SEC)
    assert not m.shape_usable(fb.MIN_ROIS, fb.MIN_EVENTS, fb.MIN_DURATION_SEC - 1)


def test_quiet_and_busy_use_the_benchs_own_recording_set():
    """quiet/busy must be measured where ``remeasure_bench`` measured ``bench.REGIMES``.

    Its ``_values`` takes the 25th/75th percentile over ``[r for r in recs if
    r["shape_usable"]]``. Measuring here over ALL recordings and comparing against
    ``bench.REGIMES`` compares two recording SETS and reports the difference as a measurement —
    which is what the first run of 2026-09-22 did: quiet appeared to fall 30% while busy agreed
    to 2%, the signature of the cut rather than of coordination.

    Built so the two answers cannot coincide: every unusable recording is far quieter than every
    usable one, so including them must drag the 25th percentile down and leave the 75th alone.
    """
    def rec(rate, usable):
        return {"rate": rate, "N": 30, "T": 1800.0, "shape_usable": usable,
                "stretches": [rate],
                "cum": {str(m.PRIMARY_W): {"f2": 0.0, "f3": 0.0, "n_win": 100}}}

    usable = [rec(0.010 + 0.001 * i, True) for i in range(10)]       # 0.0100 … 0.0190
    unusable = [rec(0.001 + 0.0001 * i, False) for i in range(10)]   # 0.0010 … 0.0019
    out = m.summarize(usable + unusable, m.PRIMARY_W)

    assert out["recordings"] == 20
    assert out["recordings_shape_usable"] == 10

    only = np.array([r["rate"] for r in usable])
    every = np.array([r["rate"] for r in usable + unusable])
    assert out["quiet_raw_hz"] == pytest.approx(np.percentile(only, 25))
    assert out["busy_raw_hz"] == pytest.approx(np.percentile(only, 75))
    assert out["quiet_raw_hz_all_recordings"] == pytest.approx(np.percentile(every, 25))
    assert out["busy_raw_hz_all_recordings"] == pytest.approx(np.percentile(every, 75))

    # The whole point: the two differ, and the REPORTED one is the bench's set.
    assert out["quiet_raw_hz"] > out["quiet_raw_hz_all_recordings"] * 2
    for model in m.MODELS:
        assert (out[model]["quiet_background_hz"]
                > out[model]["quiet_background_hz_all_recordings"])


def test_stretch_rate_is_onsets_per_cell_per_second():
    L = int(600 / DT)
    trains = [np.arange(0, L, int(10 / DT)), np.arange(0, L, int(20 / DT))]   # 0.1 and 0.05 Hz
    r = m.stretch_rates(trains, L, int(300 / DT), int(30 / DT))
    assert r == pytest.approx(0.075, abs=0.004)
