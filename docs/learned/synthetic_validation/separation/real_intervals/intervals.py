"""The coordination-rates tool's excess cumulants for any stationary event train.

Derivation: derivation.md (beside this file). Generalizes theory.py's f2, f3 from "at most one
event per window" to an event train of intensity lambda and pair correlation g_E(tau), and
includes the shift surrogates' own dependence on the train.

    f2 = lam (k)_2 a2 + lam^2 k^2 b2
    f3 = lam (k)_3 a3 + 3 lam^2 k (k)_2 b3 + lam^3 k^3 c3

with every coefficient a difference "real recording minus surrogate", computed here from the
window, the jitter, N and g_E. The surrogate is the tool's: each cell shifted by a distinct
multiple of 2w (all N multiples used once), so its expectation needs no sampling.

Run (repository root from BUGARACH_REPO, or this file's position if it sits in the repo):

    python intervals.py [--quick] [--n-rec 40] [--jobs 12]

writes intervals_output.txt, intervals_results.json and synth_recovery_plot_coordination-rates-on-real-intervals_20261025.png beside itself.
"""

from __future__ import annotations

import argparse
import functools
import importlib.util
import json
import os
import sys
import time
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np
from scipy import optimize, signal, stats

HERE = Path(__file__).resolve().parent


def _repo() -> Path:
    env = os.environ.get("BUGARACH_REPO")
    if env:
        return Path(env)
    for p in HERE.parents:
        if (p / "docs" / "learned" / "synthetic_validation" / "theory.py").exists():
            return p
    raise SystemExit("set BUGARACH_REPO to the repository root")


REPO = _repo()
for _p in (REPO / "src", REPO / "tools"):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))
import measure_coordination_rates as mcr  # noqa: E402


@functools.lru_cache(maxsize=1)
def theory():
    spec = importlib.util.spec_from_file_location(
        "theory", REPO / "docs" / "learned" / "synthetic_validation" / "theory.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


R_MAX = 340.0     # s; longest lag the pair correlation is tabulated to (surrogate span at w = 4 is 256 s)
DH = 0.01         # s; lag grid of the pair correlation


# ------------------------------------------------------------------ the event train

class PairCorrelation:
    """g_E(|tau|) of the event train on a fine lag grid, 1 beyond it.

    rho_2(tau) = lam^2 g_E(tau) is the density of ordered pairs of distinct events at lag tau.
    Triples use the renewal (Markov) closure rho_3 = lam^3 g(u1) g(u2) for ordered gaps u1, u2,
    exact for a renewal train."""

    def __init__(self, tau, g, name, lam_f=None, info=None, cv2=1.0):
        self.tau, self.g, self.name = np.asarray(tau, float), np.asarray(g, float), name
        self.lam_f = lam_f
        self.info = info or {}
        self.cv2 = cv2          # squared coefficient of variation of the intervals

    offset = 0.0

    def __call__(self, t):
        return np.interp(np.abs(t), self.tau, self.g, right=1.0) + self.offset

    def fixed_count(self, m):
        """The same train given exactly m events in the recording. The tool's cumulants are sample
        moments over one recording, so their expectation is conditional on m. A stationary renewal
        train has int (g - 1) dtau = (CV^2 - 1) / lam over its correlation range; with the count
        fixed the integral over the recording is -1 / lam. To first order the difference is a
        uniform deficit of CV^2 / m (1/m for Poisson intervals, as for a binomial process). It
        cancels in f2 and moves f3 by O(CV^2 w / T)."""
        new = PairCorrelation(self.tau, self.g, self.name + f", m={m:g}", self.lam_f, self.info,
                              self.cv2)
        new.offset = self.offset - self.cv2 / m
        return new

    # constructors -----------------------------------------------------------------
    @classmethod
    def poisson(cls):
        return cls([0.0, R_MAX], [1.0, 1.0], "Poisson")

    @classmethod
    def hard_core(cls, d=20.0):
        """theory.py's assumption: no pair closer than d, uncorrelated beyond."""
        eps = 1e-6
        return cls([0.0, d - eps, d, R_MAX], [0.0, 0.0, 1.0, 1.0], f"hard-core {d:g} s")

    @classmethod
    def from_intervals(cls, samples=None, density=None, lam=None, bw=0.05, name="intervals",
                       mean=None, cv2=None):
        """A renewal train from its interval law: samples (kernel-smoothed by ``bw`` s) or a
        density callable on [0, inf). h = sum_n f^{*n} is the renewal density (events per s at
        lag tau after an event), lam_f = 1 / mean interval.

        ``lam`` None: the stationary renewal, g_E = h / lam_f. ``lam`` given and different from
        lam_f (as on real recordings, where events per hour and gaps between neighbours disagree):
        the Palm-preserving form g_E = 1 + (h - lam_f) / lam, which keeps the density of
        neighbours seen from an event, the thing a gap histogram measures, and tends to 1 at long
        lags."""
        n = int(round(R_MAX / DH)) + 1
        tau = np.arange(n) * DH
        if samples is not None:
            x = np.asarray(samples, float)
            mean = float(x.mean()) if mean is None else mean
            cv2 = float(x.var() / x.mean() ** 2) if cv2 is None else cv2
            f = np.zeros(n)
            # sum of Gaussian kernels, binned: histogram then smooth (exact enough at DH << bw)
            hist = np.bincount(np.clip(np.round(x / DH).astype(int), 0, n - 1), minlength=n)[:n]
            hist[-1] = 0                     # mass beyond R_MAX does not reach the windows
            ker = stats.norm.pdf(np.arange(-int(6 * bw / DH), int(6 * bw / DH) + 1) * DH, 0, bw)
            f = np.convolve(hist / x.size, ker * DH, mode="same") / DH
        else:
            f = np.asarray(density(tau), float)
            if mean is None:
                raise ValueError("give the mean interval with a density")
            if cv2 is None:
                cv2 = 1.0
        lam_f = 1.0 / mean
        h = f.copy()
        cur = f.copy()
        nfft = 1 << int(np.ceil(np.log2(2 * n)))
        F = np.fft.rfft(f, nfft)
        for _ in range(2000):
            cur = np.fft.irfft(np.fft.rfft(cur, nfft) * F, nfft)[:n] * DH
            cur[cur < 0] = 0
            h += cur
            if cur.sum() * DH < 1e-10:
                break
        if lam is None or abs(lam - lam_f) < 1e-15:
            g = h / lam_f
        else:
            g = 1.0 + (h - lam_f) / lam
        # beyond the tabulated range the train is taken as uncorrelated; taper the last 20 s
        tap = np.clip((R_MAX - tau) / 20.0, 0, 1)
        g = 1.0 + (g - 1.0) * tap
        return cls(tau, g, name, lam_f=lam_f, info=dict(mean=mean), cv2=cv2)

    @classmethod
    def generator(cls, m, T=2700.0, margin=5.0, min_sep=20.0):
        """simulate._place_renewal's law at interval_cv = 1: min_sep + Exp(excess), with
        excess = (T - 2 margin) / (m + 1) - min_sep (the overrun rescaling is ignored)."""
        e = (T - 2 * margin) / (m + 1) - min_sep
        dens = lambda t: np.where(t >= min_sep, np.exp(-(t - min_sep) / e) / e, 0.0)  # noqa: E731
        return cls.from_intervals(density=dens, mean=min_sep + e, cv2=(e / (min_sep + e)) ** 2,
                                  name=f"generator m={m}", bw=0.0)


# ------------------------------------------------------------------ the coefficients

def _corr(a, b):
    """c[j] = sum_t a[t] b[t + j], lags j = -(len(a)-1) .. len(b)-1."""
    return signal.fftconvolve(a[::-1], b)


def coefficients(w: float, sigma: float, N: int, gE: PairCorrelation, parts=False):
    """Real-minus-surrogate coefficients (a2, b2, a3, b3, c3) of f2, f3 for one window.

    Real recording: every cell's onset at t_e + eps. Surrogate: cell x shifted by d_x = 2 w x,
    x = 0..N-1 (the tool's permutation and common shift do not change the expectation, by
    exchangeability of membership and stationarity)."""
    n_w = int(max(50, np.ceil(5 * w / sigma)))          # grid points per window
    dl = w / n_w
    sp = 2 * n_w                                        # surrogate spacing, grid steps
    pad = int(np.ceil((8 * sigma) / dl)) + 2
    # q(t): event at t, one onset lands in [0, w); support (-8 sigma, w + 8 sigma)
    j = np.arange(n_w + 2 * pad + 1)
    t = -pad * dl + j * dl
    q = stats.norm.cdf((w - t) / sigma) - stats.norm.cdf(-t / sigma)
    nq = q.size
    # surrogate sums S_r(t) = sum_x q(t + d_x)^r: q shifted left by sp*x
    L = nq + sp * (N - 1)
    S = np.zeros((4, L))
    for x in range(N):
        o = sp * (N - 1 - x)          # array index offset; common shift is immaterial
        for r in (1, 2, 3):
            S[r, o:o + nq] += q ** r
    mu1s = S[1] / N
    mu2s = (S[1] ** 2 - S[2]) / (N * (N - 1))
    mu3s = (S[1] ** 3 - 3 * S[1] * S[2] + 2 * S[3]) / (N * (N - 1) * (N - 2))
    A2r, A3r = q @ q * dl, np.sum(q ** 3) * dl
    A2s, A3s = mu2s.sum() * dl, mu3s.sum() * dl

    # lag integrals int (g - 1)(tau) M(tau) dtau on the pair-correlation grid
    taug = np.arange(-R_MAX, R_MAX + DH / 2, DH)
    gm1 = gE(taug) - 1.0

    def lagint(M, n_a):
        lags = (np.arange(M.size) - (n_a - 1)) * dl
        return float(np.sum(gm1 * np.interp(taug, lags, M, left=0.0, right=0.0)) * DH)

    Q = _corr(q, q) * dl
    B2r = lagint(Q, nq)
    B2s = lagint(_corr(mu1s, mu1s) * dl, L)
    B3r = lagint(_corr(q, q ** 2) * dl, nq)
    B3s = lagint(_corr(mu1s, mu2s) * dl, L)

    # triples: Q3(x, y) = int q(t) q(t+x) q(t+x+y) dt on a coarse 2-D grid
    s2 = max(1, int(round(((w + 6 * sigma) / 12) / dl)))
    d2 = s2 * dl
    nx = int(np.ceil((n_w + pad) / s2))
    xs = np.arange(-nx, nx + 1) * s2                    # grid steps
    xs = xs[np.abs(xs) < nq]
    Q3 = np.zeros((xs.size, xs.size))
    for ix, xstep in enumerate(xs):
        if xstep >= 0:
            prod = np.zeros(nq); prod[:nq - xstep] = q[:nq - xstep] * q[xstep:]
        else:
            prod = np.zeros(nq); prod[-xstep:] = q[-xstep:] * q[:nq + xstep]
        c = _corr(prod, q) * dl                         # lag z = x + y
        zl = xs[ix] + xs                                 # x + y in steps
        idx = zl + (nq - 1)
        ok = (idx >= 0) & (idx < c.size)
        Q3[ix, ok] = c[idx[ok]]
    X, Y = np.meshgrid(xs * dl, xs * dl, indexing="ij")
    wQ = Q3 * d2 * d2

    def K(t1, t2):
        p = np.stack([np.zeros_like(t1), t1, t1 + t2])
        p.sort(axis=0)
        u1, u2 = p[1] - p[0], p[2] - p[1]
        g1, g2, g12 = gE(u1), gE(u2), gE(u1 + u2)
        return g1 * g2 - g1 - g2 - g12 + 2.0

    Cr = float(np.sum(K(X, Y) * wQ))
    # surrogate lattice: (i, j, l) cells at indices x, x+m1, x+m1+m2; weight c(m1,m2)/N^3
    ms = np.arange(-(N - 1), N)
    M1, M2 = np.meshgrid(ms, ms, indexing="ij")
    x0 = np.arange(N)[:, None, None]
    cnt = np.sum((x0 + M1 >= 0) & (x0 + M1 < N) & (x0 + M1 + M2 >= 0) & (x0 + M1 + M2 < N), axis=0)
    sel = cnt > 0
    M1, M2, cnt = M1[sel], M2[sel], cnt[sel]
    Cs = 0.0
    Cs00 = 0.0
    for i0 in range(0, M1.size, 400):
        a = (2 * w * M1[i0:i0 + 400])[:, None, None]
        b = (2 * w * M2[i0:i0 + 400])[:, None, None]
        v = np.sum(K(X[None] - a, Y[None] - b) * wQ[None], axis=(1, 2))
        Cs += float(np.sum(cnt[i0:i0 + 400] * v)) / N ** 3
    Cs00 = Cr * N / N ** 3
    out = dict(a2=A2r - A2s, b2=B2r - B2s, a3=A3r - A3s, b3=B3r - B3s, c3=Cr - Cs)
    if parts:
        out.update(A2r=A2r, A2s=A2s, A3r=A3r, A3s=A3s, B2r=B2r, B2s=B2s, B3r=B3r, B3s=B3s,
                   Cr=Cr, Cs=Cs, Cs00=Cs00, Q3mass=float(wQ.sum()))
    return out


def cumulants_from(c, k, lam):
    f2 = lam * k * (k - 1) * c["a2"] + lam ** 2 * k ** 2 * c["b2"]
    f3 = (lam * k * (k - 1) * (k - 2) * c["a3"] + 3 * lam ** 2 * k * k * (k - 1) * c["b3"]
          + lam ** 3 * k ** 3 * c["c3"])
    return f2, f3


def decompose(w, sigma, N, gE, k, lam):
    """f2, f3 and their split against the page's hard-core form:
    page (theory.py), + interval (real recording's between-event pairs/triples beyond the hard
    core), + surrogate dependence (shifted copies of a correlated train), + surrogate leakage
    (the same event's onsets in two cells still sharing a window after the shift)."""
    p = coefficients(w, sigma, N, gE, parts=True)
    th = theory()
    g2, g3 = th.g(2, w, sigma), th.g(3, w, sigma)
    kk2, kk3 = k * (k - 1), k * (k - 1) * (k - 2)
    page2, page3 = th.predicted_excess_cumulants(k, sigma, w, lam, N)
    inter2 = lam ** 2 * k ** 2 * (1 - 1 / N) * (p["B2r"] + w ** 2)
    sdep2 = -lam ** 2 * k ** 2 * (p["B2s"] - p["B2r"] / N)
    leak2 = -lam * kk2 * p["A2s"]
    num2 = lam * kk2 * (p["A2r"] - w * g2)
    inter3 = (3 * lam ** 2 * k * kk2 * (p["B3r"] + w * w * g2)
              + lam ** 3 * k ** 3 * (1 - 1 / N ** 2) * (p["Cr"] - 2 * w ** 3))
    sdep3 = -3 * lam ** 2 * k * kk2 * p["B3s"] - lam ** 3 * k ** 3 * (p["Cs"] - p["Cs00"])
    leak3 = -lam * kk3 * p["A3s"]
    num3 = lam * kk3 * (p["A3r"] - w * g3)
    f2, f3 = cumulants_from(p, k, lam)
    return dict(f2=f2, f3=f3, page_f2=page2, page_f3=page3,
                f2_terms=dict(interval=inter2, surrogate=sdep2, leakage=leak2, numeric=num2),
                f3_terms=dict(interval=inter3, surrogate=sdep3, leakage=leak3, numeric=num3),
                parts=p)


def predict(intervals=None, *, k, sigma, N, w, lam, density=None, mean=None, gE=None,
            palm=True):
    """The interface: interval law (samples, or density + mean) plus k, sigma, N, w, lam ->
    predicted f2, f3 and the tool's solve() output, also as ratios to the planted values."""
    if gE is None:
        gE = PairCorrelation.from_intervals(samples=intervals, density=density, mean=mean,
                                            lam=lam if palm else None)
    c = coefficients(w, sigma, N, gE)
    f2, f3 = cumulants_from(c, k, lam)
    s = mcr.solve(f2, f3, N, w, "fixed")
    return dict(f2=f2, f3=f3, solve=s,
                ratio=dict(k=s["k"] / k, lam=s["lam"] / lam, share=s["share"] / (lam * k / N)))


def solve_ratio(f2, f3, k, lam, N, w):
    s = mcr.solve(f2, f3, N, w, "fixed")
    return dict(k=s["k"] / k, lam=s["lam"] / lam, share=s["share"] / (lam * k / N))


# ------------------------------------------------------------------ joint fit, general form

SIG_GRID = np.geomspace(0.005, 5.0, 46)


def _table(args):
    w, s, N, gE = args
    return coefficients(w, s, N, gE)


def coefficient_table(N, gE, windows=(1.0, 2.0, 4.0), jobs=1):
    jobs_l = [(w, s, N, gE) for w in windows for s in SIG_GRID]
    if jobs > 1:
        with ProcessPoolExecutor(jobs) as ex:
            res = list(ex.map(_table, jobs_l))
    else:
        res = [_table(a) for a in jobs_l]
    tab = {}
    for (w, s, _, _), r in zip(jobs_l, res):
        tab.setdefault(w, []).append([r[x] for x in ("a2", "b2", "a3", "b3", "c3")])
    return {w: np.array(v) for w, v in tab.items()}


def fit_joint_general(cum, n_cells, tab):
    """theory.fit_joint with the general form in place of the hard-core one (same residual
    scaling, starts and bounds); coefficients interpolated in log sigma from ``tab``."""
    th = theory()
    ws = np.array(sorted(float(w) for w in cum))
    get = lambda w, q: cum[str(w)][q] if str(w) in cum else cum[w][q]  # noqa: E731
    f2 = np.array([get(w, "f2") for w in ws]); f3 = np.array([get(w, "f3") for w in ws])
    if not np.any(f2 > 0):
        return None
    s2 = max(np.mean(np.abs(f2)), 1e-12); s3 = max(np.mean(np.abs(f3)), 1e-12)
    lg = np.log(SIG_GRID)

    def co(w, sig):
        T = tab[w]
        return [np.interp(np.log(sig), lg, T[:, i]) for i in range(5)]

    def resid(x):
        sig, k, lam = np.exp(x[0]), 2 + np.exp(x[1]), np.exp(x[2])
        p2, p3 = [], []
        for w in ws:
            a2, b2, a3, b3, c3 = co(w, sig)
            v = cumulants_from(dict(a2=a2, b2=b2, a3=a3, b3=b3, c3=c3), k, lam)
            p2.append(v[0]); p3.append(v[1])
        return np.concatenate([(np.array(p2) - f2) / s2, (np.array(p3) - f3) / s3])

    best = None
    lo = [np.log(th.SIGMA_BOUNDS[0]), np.log(1e-3), np.log(1e-6)]
    hi = [np.log(th.SIGMA_BOUNDS[1]), np.log(n_cells - 2), np.log(1.0)]
    for sig0 in (0.05, 0.2, 0.6, 1.5):
        for k0 in (4.0, 12.0):
            w0 = ws[-1]
            lam0 = max(f2[-1], 1e-6) / (w0 * k0 * (k0 - 1))
            x0 = [np.log(sig0), np.log(k0 - 2), np.log(min(max(lam0, 1e-5), 0.5))]
            try:
                r = optimize.least_squares(resid, x0, bounds=(lo, hi))
            except ValueError:
                continue
            if best is None or r.cost < best.cost:
                best = r
    if best is None:
        return None
    sig = float(np.exp(best.x[0]))
    return dict(sigma=sig, k=float(2 + np.exp(best.x[1])), lam=float(np.exp(best.x[2])),
                at_bound=bool(sig <= th.SIGMA_BOUNDS[0] * 1.02 or sig >= th.SIGMA_BOUNDS[1] / 1.02))


# ================================================================== experiments

N_ROI = 33
T_REC = 2700.0
LAB_SIGMA = {"fast": 0.105, "slow": 0.131}
LAB_K = (7, 13)
LAB_BG = 0.0096


def load_gaps(stream):
    import csv
    p = REPO / "docs" / "learned" / "runs" / "2026-09-25-real-intervals" / "gaps.csv"
    with open(p, newline="") as fh:
        return np.array([float(r["gap_sec"]) for r in csv.DictReader(fh) if r["stream"] == stream])


def _cum_parts(trains, L, wf, n_surr, rng):
    f = mcr.population_cumulants(trains, L, wf)
    s = np.array([mcr.population_cumulants(mcr.shifted(trains, L, 2 * wf, rng), L, wf)
                  for _ in range(n_surr)])
    return list(f), list(s.mean(axis=0))


def _mc_worker(args):
    """Aim 1a's generator with no background: real and surrogate cumulants kept apart."""
    sigma, part, ne, seed = args
    from bugarach.simulate import simulate_coordination
    s, gt = simulate_coordination(duration_sec=T_REC, n_roi=N_ROI, bg_rate_hz=0.0,
                                  participation=(part,), n_per_level=(ne,), jitter_sec=sigma,
                                  min_sep_sec=20.0, grid_sec=0.1, seed=500000 + seed)
    st = next(iter(s.streams.values()))
    L = int(round(T_REC / mcr.DT))
    trains = [np.minimum(mcr._frames(np.asarray(t), 0.0, T_REC), L - 1) for t in st.t50rise]
    rng = np.random.RandomState(seed)
    out = {}
    for w in mcr.WINDOWS:
        out[str(w)] = _cum_parts(trains, L, int(round(w / mcr.DT)), mcr.N_SURR, rng)
    return out


def _gen_times_worker(args):
    m, seed = args
    from bugarach import simulate as sim
    rng = np.random.RandomState(seed)
    tt = sim._place_renewal(rng, m, 5.0, T_REC - 5.0, 20.0, None, 1.0)
    return tt


def generator_pair_correlation(m, n_draw=20000, jobs=12):
    """The generator's own pair correlation, from _place_renewal draws (overrun rescaling
    included), as circular lags on the recording (the surrogate's shifts are circular)."""
    with ProcessPoolExecutor(jobs) as ex:
        draws = list(ex.map(_gen_times_worker, [(m, s) for s in range(n_draw)], chunksize=200))
    edges = np.arange(0, R_MAX + 1.0, 0.5)
    hist = np.zeros(edges.size - 1)
    for tt in draws:
        d = (tt[None, :] - tt[:, None]) % T_REC
        d = np.minimum(d, T_REC - d)[~np.eye(tt.size, dtype=bool)]
        hist += np.histogram(d, edges)[0]
    lam = m / T_REC
    # ordered pairs at |lag| in a bin: 2 * rho2 * T * width  (both signs folded)
    rho2 = hist / n_draw / (T_REC * 2 * np.diff(edges))
    g = rho2 / lam ** 2
    tau = 0.5 * (edges[1:] + edges[:-1])
    return PairCorrelation(np.concatenate([[0.0], tau]), np.concatenate([[g[0]], g]),
                           f"generator m={m} (empirical)")


def _realgap_worker(args):
    stream, sigma, k, seed, gaps = args
    from bugarach import simulate as sim
    rng_t = np.random.RandomState(700000 + seed)
    lo, hi = 5.0, T_REC - 5.0
    t, times = lo - 4000.0, []
    while t < hi:
        t += gaps[rng_t.randint(0, gaps.size)]
        if lo <= t < hi:
            times.append(t)
    times = np.array(times)
    orig = sim._place_renewal
    sim._place_renewal = lambda rng, m, lo_, hi_, ms, ex, cv: times.copy()  # noqa: E731
    try:
        s, gt = sim.simulate_coordination(
            duration_sec=T_REC, n_roi=N_ROI, bg_rate_hz=LAB_BG, participation=(k / N_ROI,),
            n_per_level=(times.size,), jitter_sec=sigma, min_sep_sec=0.0, grid_sec=0.1,
            seed=800000 + seed)
    finally:
        sim._place_renewal = orig
    st = next(iter(s.streams.values()))
    L = int(round(T_REC / mcr.DT))
    trains = [np.minimum(mcr._frames(np.asarray(tr), 0.0, T_REC), L - 1) for tr in st.t50rise]
    m = mcr.measure(trains, L, np.random.RandomState(900000 + seed))
    cum = {w: dict(f2=float(c["f2"]), f3=float(c["f3"])) for w, c in m["cum"].items()}
    cr = {w: mcr.solve(c["f2"], c["f3"], N_ROI, float(w), "fixed") for w, c in cum.items()}
    true = mcr.truth(gt, N_ROI, T_REC)
    ev = np.array(sorted(e.time for e in gt.events))
    return dict(stream=stream, sigma=sigma, k=k, seed=seed, true=true, cum=cum, coord_rates=cr,
                n_events=int(ev.size), gaps_lt_w={str(w): int(np.sum(np.diff(ev) < w + 1.0))
                                                  for w in mcr.WINDOWS})


# ================================================================== analysis

LOG: list[str] = []


def out(*a):
    s = " ".join(str(x) for x in a)
    print(s, flush=True)
    LOG.append(s)


def section_reductions():
    out("=" * 100)
    out("1. REDUCTIONS. k = 13, sigma = 0.105 s, N = 33, lambda = 0.01 Hz. General form against theory.py.")
    th = theory()
    k, s, lam, N = 13, 0.105, 0.01, N_ROI
    po, hc = PairCorrelation.poisson(), PairCorrelation.hard_core(20.0)
    rows = []
    for w in mcr.WINDOWS:
        dp = decompose(w, s, N, po, k, lam)
        pf2, pf3 = th.poisson_cumulants(k, s, w, lam)
        dh = decompose(w, s, N, hc, k, lam)
        t2, t3 = dh["f2_terms"], dh["f3_terms"]
        out(f"  w {w:g} s  Poisson train: general f2 {dp['f2']:.6f}, theory.poisson_cumulants {pf2:.6f}; "
            f"f3 {dp['f3']:.6f} vs {pf3:.6f} (difference = surrogate leakage, {dp['f2_terms']['leakage']:.1e})")
        out(f"         hard-core 20 s train: page f2 {dh['page_f2']:.6f}, f3 {dh['page_f3']:.6f}. General minus page: "
            f"f2 interval {t2['interval']:+.1e}, numeric {t2['numeric']:+.1e}, leakage {t2['leakage']:+.1e}, "
            f"surrogate {t2['surrogate']:+.2e} ({t2['surrogate'] / dh['page_f2']:+.4f} of f2); "
            f"f3 interval {t3['interval']:+.1e}, surrogate {t3['surrogate']:+.2e} ({t3['surrogate'] / dh['page_f3']:+.4f} of f3)")
        rows.append(dict(w=w, poisson=(dp["f2"], dp["f3"], pf2, pf3), hard=(dh["page_f2"], dh["page_f3"]),
                         t2=t2, t3=t3))
    return rows


def section_mc(n_rec, jobs, emp=None):
    out("=" * 100)
    out(f"2. MONTE CARLO CHECK OF THE SURROGATE TERM. Aim 1a's generator with no background, k = 20 (0.6 of 33), "
        f"sigma 0.2 s, {n_rec} recordings per event count. Surrogate = mean over the tool's 20 shift surrogates. "
        "Mean over recordings (SE).")
    res = {}
    for ne in (15, 45):
        args = [(0.2, 0.6, ne, 1000 * ne + i) for i in range(n_rec)]
        with ProcessPoolExecutor(jobs) as ex:
            rows = list(ex.map(_mc_worker, args))
        lam, k, N, s = ne / T_REC, 20, N_ROI, 0.2
        gE = PairCorrelation.generator(ne).fixed_count(ne)
        gEe = emp[ne] if emp else None
        res[ne] = {}
        for w in mcr.WINDOWS:
            real = np.array([r[str(w)][0] for r in rows]); sur = np.array([r[str(w)][1] for r in rows])
            p = coefficients(w, s, N, gE, parts=True)
            r2 = lam * k * (k - 1) * p["A2r"] + lam ** 2 * k * k * p["B2r"]
            r3 = (lam * k * (k - 1) * (k - 2) * p["A3r"] + 3 * lam ** 2 * k * k * (k - 1) * p["B3r"]
                  + lam ** 3 * k ** 3 * p["Cr"])
            s2 = lam * k * (k - 1) * p["A2s"] + lam ** 2 * k * k * p["B2s"]
            s3 = (lam * k * (k - 1) * (k - 2) * p["A3s"] + 3 * lam ** 2 * k * k * (k - 1) * p["B3s"]
                  + lam ** 3 * k ** 3 * p["Cs"])
            ind2 = -lam ** 2 * k * k * w * w / N
            ind3 = 2 * lam ** 3 * k ** 3 * w ** 3 / N ** 2
            if gEe is not None:
                pe = coefficients(w, s, N, gEe, parts=True)
                s2e = lam * k * (k - 1) * pe["A2s"] + lam ** 2 * k * k * pe["B2s"]
                s3e = (lam * k * (k - 1) * (k - 2) * pe["A3s"] + 3 * lam ** 2 * k * k * (k - 1) * pe["B3s"]
                       + lam ** 3 * k ** 3 * pe["Cs"])
            else:
                s2e = s3e = float("nan")
            se = lambda v: v.std(ddof=1) / np.sqrt(v.size)  # noqa: E731
            out(f"  {ne} events, w {w:g} s: surrogate f2 measured {sur[:, 0].mean():+.5f} ({se(sur[:, 0]):.5f}), "
                f"general {s2:+.5f} (empirical generator g_E {s2e:+.5f}), page's independent offsets {ind2:+.5f}; "
                f"surrogate f3 measured {sur[:, 1].mean():+.4f} ({se(sur[:, 1]):.4f}), general {s3:+.4f} "
                f"(empirical {s3e:+.4f}), page {ind3:+.4f}")
            out(f"       real f2 measured {real[:, 0].mean():.4f} ({se(real[:, 0]):.4f}), general {r2:.4f}; real f3 "
                f"{real[:, 1].mean():.3f} ({se(real[:, 1]):.3f}), general {r3:.3f}. Surrogate dependence, share of "
                f"excess f2: {-(s2 - ind2) / (r2 - s2):+.4f}")
            res[ne][str(w)] = dict(sur_f2=float(sur[:, 0].mean()), sur_f2_se=float(se(sur[:, 0])),
                                   sur_f3=float(sur[:, 1].mean()), sur_f3_se=float(se(sur[:, 1])),
                                   gen_sur_f2=s2, gen_sur_f3=s3, emp_sur_f2=s2e, emp_sur_f3=s3e, page_sur_f2=ind2, page_sur_f3=ind3,
                                   real_f2=float(real[:, 0].mean()), real_f2_se=float(se(real[:, 0])),
                                   gen_real_f2=r2, real_f3=float(real[:, 1].mean()), gen_real_f3=r3)
    return res


def _cond(rows):
    from collections import defaultdict
    c = defaultdict(list)
    for r in rows:
        t = r["true"]
        c[(t["bg_rate"], t["jitter"], int(round(t["k"])), t["n_events"])].append(r)
    return c


VARIANTS = ("page", "+interval", "+surrogate", "+leakage", "+finite count", "empirical g_E")
EMP = {}


def _variant_cumulants(w, s, N, k, ne, lam):
    """f2, f3 for the page form and for the general form built up one term at a time."""
    base = PairCorrelation.generator(ne)
    d = decompose(w, s, N, base, k, lam)
    dfc = decompose(w, s, N, base.fixed_count(ne), k, lam)
    f2, f3 = d["page_f2"], d["page_f3"]
    t2, t3 = d["f2_terms"], d["f3_terms"]
    res = {"page": (f2, f3)}
    f2 += t2["interval"] + t2["numeric"]; f3 += t3["interval"] + t3["numeric"]
    res["+interval"] = (f2, f3)
    f2 += t2["surrogate"]; f3 += t3["surrogate"]
    res["+surrogate"] = (f2, f3)
    f2 += t2["leakage"]; f3 += t3["leakage"]
    res["+leakage"] = (f2, f3)
    res["+finite count"] = (dfc["f2"], dfc["f3"])
    if ne in EMP:
        res["empirical g_E"] = cumulants_from(coefficients(w, s, N, EMP[ne]), k, lam)
    else:
        res["empirical g_E"] = res["+finite count"]
    return res, d


def section_aim1a():
    out("=" * 100)
    out("3. AIM 1A RECORD (aim1_one_source.json) with the generator's own interval law: 20 s + Exp(excess), "
        "excess = 2690/(m+1) - 20 s, m = 15 or 45. Terms added one at a time to the page's form.")
    rec = json.loads((REPO / "docs/learned/synthetic_validation/aim1_one_source.json").read_text())
    rows, N, T = rec["rows"], rec["n_roi"], rec["duration_sec"]
    cond = _cond(rows)
    cache, table = {}, []
    for (bg, s, k, ne), rs in sorted(cond.items()):
        lam = ne / T
        for w in mcr.WINDOWS:
            key = (w, s, k, ne)
            if key not in cache:
                cache[key] = _variant_cumulants(w, s, N, k, ne, lam)
            var, d = cache[key]
            pred = {v: solve_ratio(*var[v], k, lam, N, w) for v in VARIANTS}
            vals = {q: np.array([x["coord_rates"][str(w)][q] / x["true"][q] for x in rs]) for q in ("k", "lam", "share")}
            meas = {q: float(np.nanmedian(v)) if np.any(np.isfinite(v)) else float("nan") for q, v in vals.items()}
            f2m = np.mean([x["cum"][str(w)]["f2"] for x in rs]); f3m = np.mean([x["cum"][str(w)]["f3"] for x in rs])
            table.append(dict(bg=bg, sigma=s, k=k, n_events=ne, w=w, pred=pred, meas=meas,
                              pooled=solve_ratio(f2m, f3m, k, lam, N, w),
                              f2_terms={a: b / d["page_f2"] for a, b in d["f2_terms"].items()},
                              f3_terms={a: b / d["page_f3"] for a, b in d["f3_terms"].items()},
                              fc=(var["+finite count"][0] / var["+leakage"][0] - 1,
                                  var["+finite count"][1] / var["+leakage"][1] - 1)))
    it = [abs(r["f2_terms"]["interval"]) for r in table]
    out(f"  interval term / page f2: max |.| = {max(it):.1e} over all conditions (no two events share a window)")
    for bg in (0.01, 0.05):
        sel = [r for r in table if r["bg"] == bg and r["k"] >= 10]
        for nm, key in (("surrogate", "surrogate"), ("leakage", "leakage")):
            a2 = [r["f2_terms"][key] for r in sel]; a3 = [r["f3_terms"][key] for r in sel]
            out(f"  bg {bg}, k >= 10: {nm} term / page f2 median {np.median(a2):+.4f} ({min(a2):+.4f} to {max(a2):+.4f}); "
                f"/ page f3 median {np.median(a3):+.4f} ({min(a3):+.4f} to {max(a3):+.4f})")
        fc3 = [r["fc"][1] for r in sel]
        out(f"  bg {bg}, k >= 10: finite-count term moves f3 by median {np.median(fc3):+.4f} ({min(fc3):+.4f} to {max(fc3):+.4f}); f2 by 0")
    out("  k >= 10: 48 condition-windows per background. residual = condition median of measured/planted minus "
        "predicted/planted; sign p = two-sided sign test on measured > predicted.")
    out(f"  {'bg':>5} {'qty':>5} {'prediction':>14} {'median |res|':>12} {'median res':>11} {'meas > pred':>11} {'sign p':>7}"
        f" | pooled cumulants: {'median res':>10} {'above':>5}")
    summ = {}
    for bg in (0.01, 0.05):
        for q in ("lam", "k", "share"):
            for v in VARIANTS:
                sel = [r for r in table if r["bg"] == bg and r["k"] >= 10 and np.isfinite(r["meas"][q])]
                res = np.array([r["meas"][q] - r["pred"][v][q] for r in sel])
                pres = np.array([r["pooled"][q] - r["pred"][v][q] for r in sel if np.isfinite(r["pooled"][q])])
                above = int(np.sum(res > 0))
                pv = stats.binomtest(above, res.size).pvalue
                summ[f"{bg}|{q}|{v}"] = dict(abs_med=float(np.median(np.abs(res))), med=float(np.median(res)),
                                             above=above, n=int(res.size), p=float(pv),
                                             pooled_med=float(np.median(pres)), pooled_above=int(np.sum(pres > 0)))
                out(f"  {bg:>5} {q:>5} {v:>14} {np.median(np.abs(res)):12.4f} {np.median(res):+11.4f} "
                    f"{above:>5} of {res.size:<3} {pv:7.3f} | {np.median(pres):+10.4f} {int(np.sum(pres > 0)):>5}")
    return table, summ


def _law(stream, m_bar):
    g = load_gaps(stream)
    return PairCorrelation.from_intervals(samples=g, name=f"{stream} gaps").fixed_count(m_bar)


def section_realgaps(n_rec, jobs):
    out("=" * 100)
    out(f"4. REAL GAPS. Stationary renewal event trains, gaps resampled from gaps.csv per stream (fast with "
        f"sigma {LAB_SIGMA['fast']} s, slow with {LAB_SIGMA['slow']} s); b = {LAB_BG} Hz, N = 33, T = {T_REC:g} s, "
        f"k = 7 and 13, {n_rec} recordings per condition; lambda = 1 / mean gap.")
    th = theory()
    gaps = {st: load_gaps(st) for st in ("fast", "slow")}
    args = [(st, LAB_SIGMA[st], k, 100000 * (i_st + 1) + 1000 * k + i, gaps[st])
            for i_st, st in enumerate(("fast", "slow")) for k in LAB_K for i in range(n_rec)]
    with ProcessPoolExecutor(jobs) as ex:
        rows = list(ex.map(_realgap_worker, args))
    out(f"  simulated {len(rows)} recordings")
    table, fits, tabs, laws = [], [], {}, {}
    for st in ("fast", "slow"):
        g = gaps[st]
        lam_f = 1.0 / g.mean()
        law = _law(st, lam_f * (T_REC - 10.0))
        laws[st] = law
        s = LAB_SIGMA[st]
        out(f"  {st}: mean gap {g.mean():.1f} s (lambda {lam_f:.5f} Hz, {lam_f * (T_REC - 10):.1f} events per recording); "
            f"share of gaps under 2, 3, 4, 6 s: " + ", ".join(f"{np.mean(g < x):.3f}" for x in (2, 3, 4, 6))
            + "; pair correlation g_E at 3, 5, 10, 30, 100 s: " + ", ".join(f"{float(law(x)):.2f}" for x in (3, 5, 10, 30, 100)))
        tabs[st] = coefficient_table(N_ROI, law, jobs=jobs)
        for k in LAB_K:
            rs = [r for r in rows if r["stream"] == st and r["k"] == k]
            lam_i = np.array([r["true"]["lam"] for r in rs])
            for w in mcr.WINDOWS:
                d = decompose(w, s, N_ROI, law, k, lam_f)
                pred = dict(page=solve_ratio(d["page_f2"], d["page_f3"], k, lam_f, N_ROI, w),
                            poisson=solve_ratio(*th.poisson_cumulants(k, s, w, lam_f), k, lam_f, N_ROI, w),
                            general=solve_ratio(d["f2"], d["f3"], k, lam_f, N_ROI, w))
                vals = {q: np.array([r["coord_rates"][str(w)][q] / r["true"][q] for r in rs]) for q in ("k", "lam", "share")}
                meas = {q: float(np.nanmedian(v)) for q, v in vals.items()}
                iqr = {q: [float(np.nanpercentile(v, 25)), float(np.nanpercentile(v, 75))] for q, v in vals.items()}
                f2 = np.array([r["cum"][str(w)]["f2"] for r in rs]); f3 = np.array([r["cum"][str(w)]["f3"] for r in rs])
                pooled = solve_ratio(f2.mean(), f3.mean(), k, lam_i.mean(), N_ROI, w)
                bs = np.random.RandomState(1)
                boot = []
                for _ in range(400):
                    ii = bs.randint(0, len(rs), len(rs))
                    v_ = solve_ratio(f2[ii].mean(), f3[ii].mean(), k, lam_i[ii].mean(), N_ROI, w)
                    boot.append([v_[q] for q in ("k", "lam", "share")])
                boot = np.array(boot)
                pooled_se = {q: float(np.nanstd(boot[:, i])) for i, q in enumerate(("k", "lam", "share"))}
                table.append(dict(stream=st, sigma=s, k=k, w=w, lam=lam_f, pred=pred, meas=meas, iqr=iqr,
                                  pooled=pooled, pooled_se=pooled_se, n=len(rs),
                                  n_nan=int(np.sum(~np.isfinite(vals["k"]))),
                                  meas_f2=float(f2.mean()), meas_f2_se=float(f2.std(ddof=1) / np.sqrt(f2.size)),
                                  meas_f3=float(f3.mean()), meas_f3_se=float(f3.std(ddof=1) / np.sqrt(f3.size)),
                                  lam_mean=float(lam_i.mean()),
                                  pred_f2=dict(page=d["page_f2"], general=d["f2"],
                                               poisson=th.poisson_cumulants(k, s, w, lam_f)[0]),
                                  pred_f3=dict(page=d["page_f3"], general=d["f3"],
                                               poisson=th.poisson_cumulants(k, s, w, lam_f)[1]),
                                  f2_terms={a: b / d["page_f2"] for a, b in d["f2_terms"].items()},
                                  f3_terms={a: b / d["page_f3"] for a, b in d["f3_terms"].items()}))
            for r in rs:
                fp = th.fit_joint(r["cum"], N_ROI)
                fg = fit_joint_general(r["cum"], N_ROI, tabs[st])
                lt = r["true"]["lam"]
                fits.append(dict(stream=st, k=k, sigma=s, lam=lt,
                                 page=None if fp is None else dict(sigma=fp["sigma"] / s, k=fp["k"] / k,
                                                                     lam=fp["lam"] / lt, at_bound=fp["at_bound"]),
                                 general=None if fg is None else dict(sigma=fg["sigma"] / s, k=fg["k"] / k,
                                                                        lam=fg["lam"] / lt, at_bound=fg["at_bound"])))
    out("")
    out("  Mean excess cumulants over recordings (SE) against the predictions at lambda = 1/mean gap, and the "
        "general form's terms as shares of the page's f2, f3.")
    for r in table:
        out(f"  {r['stream']:4s} k {r['k']:2d} w {r['w']:g}: f2 meas {r['meas_f2']:.4f} ({r['meas_f2_se']:.4f}) "
            f"page {r['pred_f2']['page']:.4f} general {r['pred_f2']['general']:.4f} | f3 meas {r['meas_f3']:.3f} "
            f"({r['meas_f3_se']:.3f}) page {r['pred_f3']['page']:.3f} general {r['pred_f3']['general']:.3f} | "
            f"f2 terms: interval {r['f2_terms']['interval']:+.4f} surrogate {r['f2_terms']['surrogate']:+.4f}; "
            f"f3: interval {r['f3_terms']['interval']:+.4f} surrogate {r['f3_terms']['surrogate']:+.4f}")
    out("")
    out("  solve() output, ratio to planted. Predictions: page (hard-core 20 s), Poisson train, general (these "
        "gaps). meas = median over recordings [IQR]; pooled = solve() on the recordings' mean f2, f3 (bootstrap SE).")
    out(f"  {'condition':17s} {'qty':5s} {'page':>7} {'Poisson':>7} {'general':>7} {'meas median [IQR]':>24} {'pooled (SE)':>15}  NaN")
    for r in table:
        for q in ("k", "lam", "share"):
            out(f"  {r['stream']:4s} k {r['k']:2d} w {r['w']:g}  {q:5s} {r['pred']['page'][q]:7.3f} {r['pred']['poisson'][q]:7.3f} "
                f"{r['pred']['general'][q]:7.3f} {r['meas'][q]:8.3f} [{r['iqr'][q][0]:.3f}, {r['iqr'][q][1]:.3f}] "
                f"{r['pooled'][q]:8.3f} ({r['pooled_se'][q]:.3f})  {r['n_nan']}")
    out("")
    gof = {}
    for q in ("k", "lam", "share"):
        for v in ("page", "poisson", "general"):
            dd = np.array([r["pooled"][q] - r["pred"][v][q] for r in table])
            z = np.array([(r["pooled"][q] - r["pred"][v][q]) / r["pooled_se"][q] for r in table])
            gof[f"{q}|{v}"] = dict(med=float(np.median(dd)), worst=float(dd[np.argmax(np.abs(dd))]),
                                   n_z2=int(np.sum(np.abs(z) > 2)), chi2=float(np.sum(z ** 2)), n=int(z.size))
            out(f"  {q:5s} {v:8s}: pooled minus predicted, median {np.median(dd):+.4f}, worst {dd[np.argmax(np.abs(dd))]:+.4f}; "
                f"|z| > 2 in {int(np.sum(np.abs(z) > 2))} of {z.size}; chi2 {np.sum(z ** 2):.1f} on {z.size}")
    for q in ("f2", "f3"):
        for v in ("page", "poisson", "general"):
            z = np.array([(r[f"meas_{q}"] - r[f"pred_{q}"][v]) / r[f"meas_{q}_se"] for r in table])
            out(f"  {q} {v:8s}: (mean measured - predicted) / SE, median {np.median(z):+.2f}; chi2 {np.sum(z ** 2):.1f} on {z.size}")
            gof[f"{q}|{v}"] = dict(z_med=float(np.median(z)), chi2=float(np.sum(z ** 2)), n=int(z.size))
    out("")
    out("  Joint fit across 1, 2, 4 s (theory.fit_joint, and the same fit with the general form): median [IQR] of "
        "fitted / planted over recordings")
    for st in ("fast", "slow"):
        for k in LAB_K:
            fs = [f for f in fits if f["stream"] == st and f["k"] == k]
            for v in ("page", "general"):
                ok = [f[v] for f in fs if f[v] is not None]
                out(f"  {st:4s} k {k:2d} {v:8s}: " + "; ".join(
                    f"{q} {np.median([o[q] for o in ok]):.3f} [{np.percentile([o[q] for o in ok], 25):.2f}, "
                    f"{np.percentile([o[q] for o in ok], 75):.2f}]" for q in ("sigma", "k", "lam"))
                    + f"  (usable {len(ok)}/{len(fs)}, at the sigma bound {sum(o['at_bound'] for o in ok)})")
    out("  Noise-free: the general form's predicted cumulants fed to each fit (fitted / planted)")
    nf = []
    for st in ("fast", "slow"):
        lam_f = 1 / gaps[st].mean()
        for k in LAB_K:
            cum = {}
            for w in mcr.WINDOWS:
                f2, f3 = cumulants_from(coefficients(w, LAB_SIGMA[st], N_ROI, laws[st]), k, lam_f)
                cum[str(w)] = dict(f2=f2, f3=f3)
            fp = th.fit_joint(cum, N_ROI); fg = fit_joint_general(cum, N_ROI, tabs[st])
            nf.append(dict(stream=st, k=k,
                           page=dict(sigma=fp["sigma"] / LAB_SIGMA[st], k=fp["k"] / k, lam=fp["lam"] / lam_f),
                           general=dict(sigma=fg["sigma"] / LAB_SIGMA[st], k=fg["k"] / k, lam=fg["lam"] / lam_f)))
            out(f"  {st:4s} k {k:2d}: page fit sigma {nf[-1]['page']['sigma']:.3f} k {nf[-1]['page']['k']:.3f} "
                f"lam {nf[-1]['page']['lam']:.3f} | general fit sigma {nf[-1]['general']['sigma']:.3f} "
                f"k {nf[-1]['general']['k']:.3f} lam {nf[-1]['general']['lam']:.3f}")
    return rows, table, fits, nf, gof


def section_generator_check(jobs):
    out("=" * 100)
    out("5. THE GENERATOR'S PAIR CORRELATION, analytic renewal against 20 000 draws of _place_renewal (overrun "
        "rescaling included, circular lags), and what the difference does to the surrogate term.")
    res = {}
    for m in (15, 45):
        emp = generator_pair_correlation(m, jobs=jobs)
        ana = PairCorrelation.generator(m).fixed_count(m)
        k, s, lam = 20, 0.2, m / T_REC
        line = []
        for w in mcr.WINDOWS:
            ce = coefficients(w, s, N_ROI, emp); ca = coefficients(w, s, N_ROI, ana)
            fe = cumulants_from(ce, k, lam); fa = cumulants_from(ca, k, lam)
            line.append(f"w {w:g}: f2 {fe[0] / fa[0] - 1:+.5f}, f3 {fe[1] / fa[1] - 1:+.5f}")
        gl = [float(emp(x)) for x in (10, 21, 30, 60, 150)]
        ga = [float(ana(x)) for x in (10, 21, 30, 60, 150)]
        out(f"  m {m}: g_E at 10, 21, 30, 60, 150 s empirical " + ", ".join(f"{v:.3f}" for v in gl)
            + "; analytic " + ", ".join(f"{v:.3f}" for v in ga))
        out(f"        empirical / analytic - 1 (k 20, sigma 0.2 s): " + "; ".join(line))
        res[m] = dict(emp=gl, ana=ga)
        EMP[m] = emp
    return res


# ================================================================== figure

def figure(aim, real, fits, path):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    plt.rcParams.update({"font.size": 8.5, "axes.spines.top": False, "axes.spines.right": False})
    fig, ax = plt.subplots(2, 3, figsize=(12.5, 7.8))
    wcol = {1.0: "#1b9e77", 2.0: "#d95f02", 4.0: "#7570b3"}
    rng = np.random.RandomState(0)

    # A, B: Aim 1a residuals, page vs general, by background
    for a, q, lab in ((ax[0, 0], "lam", "event rate"), (ax[0, 1], "k", "participants")):
        pos = 0
        ticks, tl = [], []
        for bg in (0.01, 0.05):
            for v, mk in (("page", "o"), ("empirical g_E", "o")):
                sel = [r for r in aim if r["bg"] == bg and r["k"] >= 10 and np.isfinite(r["meas"][q])]
                res = np.array([r["meas"][q] - r["pred"][v][q] for r in sel])
                ws = np.array([r["w"] for r in sel])
                x = pos + rng.uniform(-0.18, 0.18, res.size)
                filled = v != "page"
                for w in mcr.WINDOWS:
                    m_ = ws == w
                    a.scatter(x[m_], res[m_], s=14, marker=mk, facecolors=wcol[w] if filled else "none",
                              edgecolors=wcol[w], linewidths=0.8)
                a.plot([pos - 0.3, pos + 0.3], [np.median(res)] * 2, "k-", lw=1.6)
                ticks.append(pos); tl.append(f"{'page' if v == 'page' else 'general'}\n{bg:g} Hz")
                pos += 1
            pos += 0.5
        a.axhline(0, color="0.5", lw=0.7, ls=":")
        lim = {"lam": 0.2, "k": 0.06}[q]
        allres = [r["meas"][q] - r["pred"][v][q] for r in aim if r["k"] >= 10 and np.isfinite(r["meas"][q])
                  for v in ("page", "empirical g_E")]
        n_out = int(np.sum(np.abs(allres) > lim))
        a.set_ylim(-lim, lim)
        a.set_xticks(ticks); a.set_xticklabels(tl)
        a.set_ylabel(f"{lab}: measured − predicted\n(ratio to planted, condition median)")
        a.set_title(f"Aim 1a, {lab}, events of 10+ cells\n({n_out} of {len(allres)} points beyond the axis)",
                    loc="left", fontsize=9)
    # C: median rate residual as the general form's terms are added
    a = ax[0, 2]
    labs = {"page": "page", "+interval": "+ interval", "+surrogate": "+ surrogate\ndependence",
            "+leakage": "+ leakage", "+finite count": "+ finite\ncount", "empirical g_E": "generator's\nempirical g_E"}
    vs = list(labs)
    for bg, col, dx in ((0.01, "k", -0.12), (0.05, "0.55", 0.12)):
        sel = [r for r in aim if r["bg"] == bg and r["k"] >= 10 and np.isfinite(r["meas"]["lam"])]
        med = [np.median([r["meas"]["lam"] - r["pred"][v]["lam"] for r in sel]) for v in vs]
        pol = [np.median([r["pooled"]["lam"] - r["pred"][v]["lam"] for r in sel if np.isfinite(r["pooled"]["lam"])])
               for v in vs]
        xx = np.arange(len(vs)) + dx
        a.plot(xx, med, "-o", color=col, ms=5, lw=1, label=f"{bg:g} Hz: median of condition medians")
        a.plot(xx, pol, "--o", color=col, ms=5, mfc="white", lw=1, label=f"{bg:g} Hz: solve() on pooled f2, f3")
    a.axhline(0, color="0.5", lw=0.7, ls=":")
    a.set_xticks(range(len(vs))); a.set_xticklabels([labs[v].replace(chr(10), " ") for v in vs], fontsize=7.5, rotation=30, ha="right")
    a.set_ylabel("event rate: measured − predicted\n(ratio to planted; median over 48 condition-windows)")
    a.set_title("Aim 1a, rate residual as terms are added", loc="left", fontsize=9)
    a.legend(fontsize=7, frameon=False, loc="upper right")

    # D, E: real gaps, pooled measured vs predicted
    smk = {"fast": "o", "slow": "s"}
    for a, q, lab in ((ax[1, 0], "lam", "event rate"), (ax[1, 1], "k", "participants")):
        for r in real:
            for v in ("page", "general"):
                filled = v == "general"
                a.errorbar(r["pred"][v][q], r["pooled"][q], yerr=r["pooled_se"][q], fmt=smk[r["stream"]],
                           ms=5 if r["k"] == 13 else 3.5, mfc=wcol[r["w"]] if filled else "white",
                           mec=wcol[r["w"]], ecolor=wcol[r["w"]], elinewidth=0.6, capsize=0, lw=0)
                if v == "general":
                    a.plot([r["pred"]["page"][q], r["pred"]["general"][q]], [r["pooled"][q]] * 2,
                           color=wcol[r["w"]], lw=0.5, alpha=0.6)
        lo = min(min(r["pred"][v][q] for r in real for v in ("page", "general")), min(r["pooled"][q] for r in real))
        hi = max(max(r["pred"][v][q] for r in real for v in ("page", "general")), max(r["pooled"][q] for r in real))
        pad = 0.05 * (hi - lo)
        a.plot([lo - pad, hi + pad], [lo - pad, hi + pad], color="0.4", lw=0.8)
        a.set_xlabel(f"predicted {lab}, ratio to planted")
        a.set_ylabel(f"measured {lab}, ratio to planted\n(solve() on pooled f2, f3; ±1 bootstrap SE)")
        a.set_title(f"Real gaps, {lab}", loc="left", fontsize=9)
    # F: joint fit
    a = ax[1, 2]
    xs = 0
    tick, tl = [], []
    for q in ("sigma", "k", "lam"):
        for v in ("page", "general"):
            for j, (st, k) in enumerate([(s_, k_) for s_ in ("fast", "slow") for k_ in LAB_K]):
                vals = [f[v][q] for f in fits if f["stream"] == st and f["k"] == k and f[v] is not None]
                med, lo_, hi_ = np.median(vals), np.percentile(vals, 25), np.percentile(vals, 75)
                x = xs + (j - 1.5) * 0.17
                a.errorbar(x, med, yerr=[[med - lo_], [hi_ - med]], fmt=smk[st], ms=5 if k == 13 else 3.5,
                           mfc="k" if v == "general" else "white", mec="k", ecolor="k", elinewidth=0.7, lw=0)
            tick.append(xs); tl.append(f"{ {'sigma': 'σ', 'k': 'k', 'lam': 'λ'}[q]}\n{'page' if v == 'page' else 'general'}")
            xs += 1
        xs += 0.4
    a.axhline(1, color="0.5", lw=0.7, ls=":")
    a.set_xticks(tick); a.set_xticklabels(tl)
    a.set_ylabel("joint fit, fitted ÷ planted\n(median, IQR over recordings)")
    a.set_title("Real gaps, joint fit across 1, 2, 4 s", loc="left", fontsize=9)

    for a, L in zip(ax.ravel(), "ABCDEF"):
        a.text(-0.16, 1.06, L, transform=a.transAxes, fontsize=12, fontweight="bold")
    from matplotlib.lines import Line2D
    hs = [Line2D([], [], marker="o", ls="", mfc=wcol[w], mec=wcol[w], label=f"window {w:g} s") for w in mcr.WINDOWS]
    hs += [Line2D([], [], marker="o", ls="", mfc="white", mec="k", label="page's hard-core form (open)"),
           Line2D([], [], marker="o", ls="", mfc="k", mec="k", label="general form (filled)"),
           Line2D([], [], color="k", lw=1.6, label="median (A, B)"),
           Line2D([], [], color="0.4", lw=0.8, label="identity (D, E)"),
           Line2D([], [], marker="o", ls="", mfc="0.6", mec="0.6", ms=5, label="D–F: fast gaps ●, slow gaps ■; large marker k 13, small k 7"),
           Line2D([], [], color="0.6", lw=0.5, label="D, E: line joins one measurement's two predictions")]
    fig.legend(handles=hs, loc="lower center", ncol=4, frameon=False, fontsize=8)
    fig.tight_layout(rect=(0, 0.06, 1, 1))
    fig.savefig(path, dpi=160)


# ================================================================== main

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n-rec", type=int, default=40)
    ap.add_argument("--n-mc", type=int, default=150)
    ap.add_argument("--jobs", type=int, default=12)
    a = ap.parse_args()
    t0 = time.time()
    red = section_reductions()
    gen = section_generator_check(a.jobs)
    mc = section_mc(a.n_mc, a.jobs, EMP)
    aim, summ = section_aim1a()
    rows, real, fits, nf, gof = section_realgaps(a.n_rec, a.jobs)
    out(f"\n[{time.time() - t0:.0f} s]")
    (HERE / "intervals_output.txt").write_text("\n".join(LOG) + "\n", encoding="utf-8")
    (HERE / "intervals_results.json").write_text(json.dumps(
        dict(mc=mc, generator=gen, aim1a=aim, aim1a_summary=summ, real=real, real_fits=fits,
             noise_free_fits=nf, goodness=gof, real_rows=rows), indent=1, default=float))
    figure(aim, real, fits, HERE / "synth_recovery_plot_coordination-rates-on-real-intervals_20261025.png")


def refigure():
    d = json.loads((HERE / "intervals_results.json").read_text())
    for r in d["aim1a"]:
        r["w"] = float(r["w"])
    for r in d["real"]:
        r["w"] = float(r["w"])
    figure(d["aim1a"], d["real"], d["real_fits"], HERE / "synth_recovery_plot_coordination-rates-on-real-intervals_20261025.png")


if __name__ == "__main__":
    if "--figure-only" in sys.argv:
        refigure()
    else:
        main()
