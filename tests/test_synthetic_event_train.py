"""The general event-train form of the coordination-rates prediction.

`docs/learned/synthetic_validation/event_train.py` and the ``train=`` options of `theory.py`,
derived in `docs/learned/synthetic_validation/separation/real_intervals/derivation.md`. These
check its two reductions to the page's forms, that the joint fit recovers known parameters
through it (including the Palm form), and that `theory.py` without ``train`` is unchanged.
No recording is simulated here; `theory.py --check-real` does that. Most of this file's time is
theory.py's own g_3 table, built once on first use (about 35 s on a laptop).
"""

import importlib.util
import json
from pathlib import Path

import numpy as np
import pytest

SV = Path(__file__).resolve().parents[1] / "docs" / "learned" / "synthetic_validation"


def _load():
    spec = importlib.util.spec_from_file_location("_sv_theory", SV / "theory.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


th = _load()
et = th.et                      # the event_train module theory.py imported, so classes match
EventTrain = et.EventTrain
N = 33
WINDOWS = th.WINDOWS


def test_poisson_train_reduces_to_poisson_cumulants():
    """g_E = 1: no between-event terms, and at small sigma no surrogate leakage either."""
    train = EventTrain.poisson()
    for w in WINDOWS:
        for k, s, lam in ((13, 0.105, 0.01), (7, 0.05, 0.02)):
            f2, f3 = th.predicted_excess_cumulants(k, s, w, lam, N, train=train)
            p2, p3 = th.poisson_cumulants(k, s, w, lam)
            assert f2 == pytest.approx(p2, rel=1e-4)
            assert f3 == pytest.approx(p3, rel=1e-4)


@pytest.mark.parametrize("sigma", [0.02, 0.105, 0.2])
def test_hard_core_with_independent_surrogate_is_the_page_form(sigma):
    """A 20 s hard core and theory.py's independent surrogate give predicted_excess_cumulants."""
    train = EventTrain.hard_core(20.0)
    for w in WINDOWS:
        c = et.coefficients(w, sigma, N, train, surrogate="independent")
        for k, lam in ((13, 0.01), (20, 45 / 2700)):
            f2, f3 = et.cumulants_from(c, k, lam)
            p2, p3 = th.predicted_excess_cumulants(k, sigma, w, lam, N)
            assert f2 == pytest.approx(p2, rel=1e-4)
            assert f3 == pytest.approx(p3, rel=1e-4)


@pytest.mark.parametrize("sigma", [0.5, 1.0])
def test_hard_core_coefficients_at_wide_jitter(sigma):
    """At sigma >= w / 2 each coefficient still matches the page's closed form to 1e-4, with g_3
    computed directly; theory.py's tabulated g_3 is itself up to 2e-4 off there, which is the
    whole of the difference in f3."""
    from scipy import integrate
    train = EventTrain.hard_core(20.0)
    for w in WINDOWS:
        c = et.coefficients(w, sigma, N, train, surrogate="independent")
        u = w / sigma
        g3 = integrate.quad(lambda r: th._range_cdf(3, r), 0, u, limit=200)[0] / u
        g2 = th.g(2, w, sigma)
        assert c["a2"] == pytest.approx(w * g2, rel=1e-4)
        assert c["a3"] == pytest.approx(w * g3, rel=1e-4)
        assert c["b2"] == pytest.approx(-(1 - 1 / N) * w * w, rel=1e-4)
        assert c["b3"] == pytest.approx(-w * w * g2, rel=1e-4)
        assert c["c3"] == pytest.approx(2 * w ** 3 * (1 - 1 / N ** 2), rel=1e-4)
        f3 = et.cumulants_from(c, 13, 0.01)[1]
        assert f3 == pytest.approx(th.predicted_excess_cumulants(13, sigma, w, 0.01, N)[1], rel=3e-4)


def test_tool_surrogate_adds_the_dependence_term():
    """With the tool's own surrogate the hard core lifts f2 by about 0.6 % at k = 13, sigma =
    0.105 s, 0.01 Hz (derivation section 5: +0.60, +0.59, +0.54 % at 1, 2, 4 s)."""
    train = EventTrain.hard_core(20.0)
    for w, want in zip(WINDOWS, (0.0060, 0.0059, 0.0054)):
        f2, _ = th.predicted_excess_cumulants(13, 0.105, w, 0.01, N, train=train)
        p2, _ = th.predicted_excess_cumulants(13, 0.105, w, 0.01, N)
        assert f2 / p2 - 1 == pytest.approx(want, abs=0.0003)


def _gaps():
    return th.load_gaps("fast")


def test_fit_joint_recovers_parameters_through_a_real_gap_renewal_train():
    """Exact general-form cumulants for a renewal train of real fast-stream gaps: fit_joint with
    the same train returns the planted (sigma, k, lambda); the page's fit does not."""
    gaps = _gaps()
    train = EventTrain.renewal(intervals=gaps)
    sigma, k, lam = 0.105, 13.0, 1.0 / gaps.mean()
    m = lam * 2690.0
    cum = {}
    for w in WINDOWS:
        f2, f3 = th.predicted_excess_cumulants(k, sigma, w, lam, N, train=train, n_events=m)
        cum[str(w)] = dict(f2=f2, f3=f3)
    # sigma on a node, so interpolation is exact there; the outer nodes are two of fit_joint's
    # starts (beyond the grid the coefficients are held, so a start there cannot move in sigma)
    grid = np.array([0.05, sigma, 0.2])
    fit = th.fit_joint(cum, N, train=train, n_events=m, sigma_grid=grid)
    assert fit["sigma"] == pytest.approx(sigma, rel=0.01)
    assert fit["k"] == pytest.approx(k, rel=0.005)
    assert fit["lam"] == pytest.approx(lam, rel=0.005)
    page = th.fit_joint(cum, N)
    assert page["sigma"] / sigma > 1.3              # the page's fit reads jitter high (derivation 7.4)


def test_palm_form_recovers_parameters_on_a_renewal_train_of_known_rate():
    """As on real data: the train is built from observed intervals and a separately known event
    rate. A renewal train of resampled real gaps at a known rate is drawn; palm() of its observed
    intervals, at that rate, fits the exact cumulants of the true train."""
    gaps = _gaps()
    rng = np.random.RandomState(3)
    T = 200_000.0
    times = np.cumsum(gaps[rng.randint(0, gaps.size, 4000)])
    times = times[times < T]
    lam = times.size / T                             # the known rate, from the count
    palm = EventTrain.palm(np.diff(times), lam)
    truth = EventTrain.renewal(intervals=gaps)
    n_cells, sigma, k = 12, 0.2, 7.0                 # fewer cells keeps the surrogate lattice small
    cum = {}
    for w in WINDOWS:
        f2, f3 = et.cumulants_from(et.coefficients(w, sigma, n_cells, truth), k, 1 / gaps.mean())
        cum[str(w)] = dict(f2=f2, f3=f3)
    grid = sigma * np.geomspace(0.5, 2.0, 5)
    fit = th.fit_joint(cum, n_cells, train=palm, sigma_grid=grid)
    assert fit["sigma"] == pytest.approx(sigma, rel=0.05)
    assert fit["k"] == pytest.approx(k, rel=0.03)
    assert fit["lam"] == pytest.approx(1 / gaps.mean(), rel=0.03)


def test_palm_at_the_interval_rate_is_the_renewal_train():
    gaps = _gaps()
    a = EventTrain.renewal(intervals=gaps)
    b = EventTrain.palm(gaps, 1.0 / gaps.mean())
    tau = np.linspace(0, 300, 601)
    np.testing.assert_allclose(a(tau), b(tau), rtol=0, atol=1e-9)


def test_from_times_of_a_poisson_train_is_flat():
    rng = np.random.RandomState(0)
    T = 2700.0
    draws = [np.sort(rng.uniform(0, T, 30)) for _ in range(3000)]
    g = EventTrain.from_times(draws, T)
    # at fixed count, g = (m - 1) / m everywhere (the binomial deficit fixed_count models)
    assert np.mean(g(np.linspace(5, 300, 100))) == pytest.approx(29 / 30, abs=0.01)


def test_fixed_count_shifts_g_by_cv2_over_m():
    gaps = _gaps()
    a = EventTrain.renewal(intervals=gaps)
    b = a.fixed_count(27)
    assert b is a.fixed_count(27)                    # cached, so its coefficients are too
    assert float(b(50.0) - a(50.0)) == pytest.approx(-a.cv2 / 27)


# ------------------------------------------------------------------ the default is unchanged

def test_default_calls_are_unchanged():
    """Values from theory.py before `train=` existed (git 4af0d53f)."""
    want = {(13, 0.105, 1.0, 0.01): (1.35878361364242, 13.578010619336698),
            (7, 0.5, 4.0, 45 / 2700): (2.193888841613618, 7.873686702871267),
            (20, 1.0, 2.0, 15 / 2700): (2.004387997476588, 19.304446293916545)}
    for (k, s, w, lam), v in want.items():
        assert th.predicted_excess_cumulants(k, s, w, lam, N) == pytest.approx(v, rel=1e-13)
        assert th.predicted_excess_cumulants(k, s, w, lam, N, train=None) == \
            th.predicted_excess_cumulants(k, s, w, lam, N)
    rec = json.loads((SV / "aim1_one_source.json").read_text())
    r = rec["rows"][-1]
    fit = th.fit_joint(r["cum"], N)
    assert fit["sigma"] == pytest.approx(0.9850004422248871, rel=1e-6)
    assert fit["k"] == pytest.approx(19.69654370939884, rel=1e-6)
    assert fit["lam"] == pytest.approx(0.017536027607245108, rel=1e-6)


def test_default_predictions_match_the_committed_record():
    """predict_solve without train reproduces theory_check.json's 'exact' values exactly."""
    out = json.loads((SV / "theory_check.json").read_text())
    rows = out["coord_rates"]
    lam_of = {15: 15 / 2700.0, 45: 45 / 2700.0}
    for r in rows[::37]:
        e = th.predict_solve(r["k"], r["sigma"], r["w"], lam_of[r["n_events"]], N)
        for q in ("k", "lam", "share"):
            if np.isfinite(r["exact"][q]):
                assert e[q] == r["exact"][q]
