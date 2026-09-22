"""The correlogram jitter measure recovers a spread it was given, and reads no bins.

Synthetic trains only: a set of shared times, each ROI firing around them with Gaussian scatter
σ on a 0.1 s grid, plus independent background. The half-width must grow with σ, and match the
half-width of the pairwise-lag distribution (σ√2 · √(2 ln 2)) once σ is well above one frame.
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pytest

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "tools"))

import measure_jitter_correlogram as mjc  # noqa: E402

L = 60_000      # frames: 100 minutes at 0.1 s


def trains_with_jitter(sigma_sec, n_roi=30, n_events=400, bg_per_roi=300, seed=0):
    rng = np.random.RandomState(seed)
    times = rng.uniform(200, L - 200, n_events)
    out = []
    for _ in range(n_roi):
        on = times[rng.rand(n_events) < 0.4]
        on = on + rng.randn(on.size) * sigma_sec / mjc.DT
        bg = rng.uniform(0, L, bg_per_roi)
        t = np.round(np.concatenate([on, bg])).astype(int)
        out.append(t[(t >= 0) & (t < L)])
    return out


def test_the_half_width_grows_with_the_planted_spread():
    widths = [mjc.hwhm(*mjc.pairs(trains_with_jitter(s), L)) for s in (0.1, 0.2, 0.4, 0.8)]
    assert all(a < b for a, b in zip(widths, widths[1:])), widths


@pytest.mark.parametrize("sigma", [0.4, 0.8])
def test_the_half_width_matches_the_pairwise_lag_distribution(sigma):
    expected = sigma * np.sqrt(2) * np.sqrt(2 * np.log(2))
    got = mjc.hwhm(*mjc.pairs(trains_with_jitter(sigma, seed=1), L))
    assert got == pytest.approx(expected, rel=0.15)


def test_independent_trains_have_no_peak_to_measure():
    rng = np.random.RandomState(2)
    trains = [np.sort(rng.randint(0, L, 400)) for _ in range(30)]
    o, e = mjc.pairs(trains, L)
    assert abs(mjc.excess(o, e)[0]) < 0.2


# --- the per-group split (--by-group) -------------------------------------------------------

SHORT = 20_000      # frames: 2000 s, enough peak for a width and fast enough for a test


def records(spec, seed0=10):
    """``(info, obs, exp)`` records from ``{group: {mouse: [sigma_sec, ...]}}``."""
    out, seed = [], seed0
    for group, mice in spec.items():
        for mouse, sigmas in mice.items():
            for k, s in enumerate(sigmas):
                seed += 1
                trains = trains_with_jitter(s, n_roi=20, n_events=200, bg_per_roi=120, seed=seed)
                trains = [t[t < SHORT] for t in trains]
                o, e = mjc.pairs(trains, SHORT)
                out.append(({"slice_id": f"{group}_{mouse}_{k}", "group": group, "mouse": mouse,
                             "rois": len(trains), "onsets": int(sum(t.size for t in trains)),
                             "window_sec": SHORT * mjc.DT}, o, e))
    return out


def test_a_mouse_is_one_cluster_however_many_recordings_it_gave():
    r = records({"A": {"m1": [0.2, 0.2, 0.2], "m2": [0.2]}})
    assert len(r) == 4
    assert sorted(len(v) for v in mjc.mice_of(r).values()) == [1, 3]


def test_a_recording_with_no_group_is_left_out_of_the_split():
    r = records({"A": {"m1": [0.2]}, "B": {"m2": [0.2]}})
    r.append(({"slice_id": "x", "group": None, "mouse": "m9", "rois": 1, "onsets": 0,
               "window_sec": 1.0}, np.zeros(mjc.MAX_LAG + 1), np.zeros(mjc.MAX_LAG + 1)))
    assert sorted(mjc.by_group(r)) == ["A", "B"]
    assert sum(len(v) for v in mjc.by_group(r).values()) == 2


def test_the_permutation_test_finds_a_planted_difference():
    r = records({"A": {f"a{i}": [0.1, 0.1] for i in range(5)},
                 "B": {f"b{i}": [0.8, 0.8] for i in range(5)}})
    obs = mjc.spread([mjc.hwhm(*mjc.pooled(v)) for v in mjc.by_group(r).values()])
    null, dropped = mjc.label_permutation(r, mjc.hwhm, 200, np.random.RandomState(0))
    assert dropped == 0
    assert obs > np.percentile(null, 95), (obs, np.percentile(null, 95))


def test_the_permutation_test_does_not_invent_one():
    r = records({"A": {f"a{i}": [0.3, 0.3] for i in range(5)},
                 "B": {f"b{i}": [0.3, 0.3] for i in range(5)}}, seed0=200)
    obs = mjc.spread([mjc.hwhm(*mjc.pooled(v)) for v in mjc.by_group(r).values()])
    null, _ = mjc.label_permutation(r, mjc.hwhm, 200, np.random.RandomState(0))
    p = (null >= obs).sum() / null.size
    assert p > 0.05, (obs, p, np.percentile(null, 95))


def test_the_bootstrap_resamples_mice_and_brackets_the_width():
    r = records({"A": {f"a{i}": [0.4, 0.4] for i in range(6)}})
    recs = mjc.by_group(r)["A"]
    w = mjc.hwhm(*mjc.pooled(recs))
    wb = mjc.group_boot(recs, mjc.hwhm, 100, np.random.RandomState(3))
    lo, hi = np.nanpercentile(wb, [2.5, 97.5])
    assert lo <= w <= hi, (lo, w, hi)
