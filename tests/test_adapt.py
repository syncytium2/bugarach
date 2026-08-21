"""The measure -> parameterize loop, tested as a round trip.

Plant known coordination, assess it, re-derive generator parameters, and check
they land near what was planted. This is the only test that can fail when the
loop is subtly wrong — the parity test proves the assessment matches MATLAB, and
a wrong *interpretation* of a correct measurement would pass it unmoved.

The tolerances below are wide on purpose, and they encode measured biases rather
than hopes: see `RECOVERY` for what the loop actually recovers and why each
number is not 1.00.
"""

from __future__ import annotations

import numpy as np
import pytest

from bugarach.adapt import CONTEXT_WIN_SEC, generator_params
from bugarach.assess import assess_coactivity
from bugarach.simulate import simulate_coordination

PLANTED = dict(duration_sec=2700.0, n_roi=33, bg_rate_hz=0.0096,
               participation=(0.18,), n_per_level=(15,), jitter_sec=0.36,
               min_sep_sec=120.0, grid_sec=0.1)

# Median recovery over 8 seeds, measured 2026-08-16. Reproduce by running this
# module's helper; these are the loop's fidelity, not targets to tune toward.
#
#   K   participants      jitter        frequency
#   3   +1%               +10%          +60%   <- background pairs clear K=3
#   4   +18%              +9%            -7%   <- the compromise
#   6   +18%              +8%           -77%   <- most events never reach K=6
RECOVERY_K = 4


def _assess_planted(seed, ks=(3, 4, 6), n_surr=120):
    s, gt = simulate_coordination(seed=seed, **PLANTED)
    recs = assess_coactivity(s, window=(0.0, PLANTED["duration_sec"]),
                             min_rois=ks, n_surrogates=n_surr)
    return {r.min_rois: r for r in recs}, gt


def test_round_trip_recovers_tightness():
    """Jitter is the parameter Tony required be learned rather than assumed, so
    it is the one the loop most has to recover. It comes back ~9% high at every
    K — the +/-Wm gather admits onsets that were not participants, which inflates
    the SD — and that bias is stable enough to be a known offset rather than
    noise."""
    got = []
    for seed in (1, 2, 3, 4):
        recs, _ = _assess_planted(seed)
        r = recs[RECOVERY_K]
        assert r.jit_defined
        got.append(r.jit_obs)
    med = float(np.median(got))
    assert 0.30 < med < 0.50, f"jitter recovered as {med:.3f} from a planted 0.36"


def test_round_trip_recovers_event_frequency_at_k4():
    """Frequency recovery depends sharply on K, which is why the assessment
    reports a scan and refuses to pick one."""
    freqs = []
    for seed in (1, 2, 3, 4):
        recs, gt = _assess_planted(seed)
        freqs.append(recs[RECOVERY_K].clusters_permin)
    planted_permin = len(gt.events) / (PLANTED["duration_sec"] / 60.0)
    med = float(np.median(freqs))
    assert 0.6 * planted_permin < med < 1.3 * planted_permin, (
        f"frequency recovered as {med:.3f}/min from a planted {planted_permin:.3f}")


def test_k3_overcounts_and_k6_undercounts():
    """The scan's two ends fail in opposite directions, and a caller picking K
    without seeing that is picking blind. Pins the reason the human-in-the-loop
    todo exists."""
    recs, gt = _assess_planted(1)
    planted = len(gt.events) / (PLANTED["duration_sec"] / 60.0)
    assert recs[3].clusters_permin > planted, "K=3 should over-count"
    assert recs[6].clusters_permin < planted, "K=6 should under-count"


def test_params_refuse_an_excluded_window():
    """An assessment that did not meet the floor carries NaN measures. Building a
    generator from it would invent a recording out of an exclusion."""
    s, _ = simulate_coordination(seed=1, **PLANTED)
    rec = assess_coactivity(s, window=(0.0, 100.0), min_rois=(3,),
                            n_surrogates=5)[0]
    assert not rec.meets_floor
    with pytest.raises(ValueError, match="window floor"):
        generator_params(rec)


def test_spacing_never_drops_inside_the_null_window():
    """The contaminated null, mechanized.

    A recording whose measured events are closer together than the detectors'
    context window must not be simulated at that spacing — that rebuilds the trap
    which made the first upstream benchmark unusable. The floor binds and says so.
    """
    recs, _ = _assess_planted(1)
    p = generator_params(recs[3])
    assert p.kwargs["min_sep_sec"] >= CONTEXT_WIN_SEC
    if recs[3].clusters_permin > 60.0 / CONTEXT_WIN_SEC:
        assert any("contaminated null" in n for n in p.notes)


def test_undefined_jitter_becomes_a_sweep_not_a_number():
    """When the assessment cannot measure tightness it must not be invented.

    `jit_defined=False` means no cluster formed in the observed or surrogate
    ensemble. The parameters then carry a sweep range and a note, and never a
    point estimate dressed as a measurement.
    """
    from bugarach.assess import Assessment
    a = Assessment(min_rois=4, meets_floor=True, win_dur=1800.0, n_roi=30,
                   n_events_win=100, roi_rate_med=0.01, part_n_obs=5.0,
                   clusters_permin=0.2, jit_obs=0.4, jit_defined=False)
    p = generator_params(a)
    assert "jitter_sec" in p.sweep
    assert not p.grounded
    assert any("NOT measured" in n for n in p.notes)


def test_generated_recording_actually_runs():
    """The parameters must be accepted by the generator they are for — the
    spacing floor lengthens the recording, and an off-by-one there makes the
    generator refuse rather than quietly pack events closer."""
    recs, _ = _assess_planted(1)
    p = generator_params(recs[RECOVERY_K])
    s, gt = simulate_coordination(seed=99, **p.kwargs)
    assert len(gt.events) == sum(p.kwargs["n_per_level"])
    gaps = np.diff(gt.times)
    assert gaps.min() >= p.kwargs["min_sep_sec"] - 1e-6
