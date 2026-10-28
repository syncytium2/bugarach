"""The coordination-rates prediction for any stationary event train.

Derivation: separation/real_intervals/derivation.md (the code there, `intervals.py`, is where
this was first written and checked; this module is its port for `theory.py`). `theory.py`'s
f2, f3 assume at most one event per window and shift surrogates independent of the event train.
Here the event train is described by its intensity lambda and pair correlation g_E(tau), and the
surrogate is the tool's own: cell x moved by d_x = (spacing) x, x = 0 .. N-1, with the spacing
read from `measure_coordination_rates` (SURR_SPACING windows). Then

    f2 = lam (k)_2 a2 + lam^2 k^2 b2
    f3 = lam (k)_3 a3 + 3 lam^2 k (k)_2 b3 + lam^3 k^3 c3

with every coefficient "recording minus surrogate", computed from w, sigma, N and g_E
(derivation sections 2-5). Triples use the renewal closure rho_3 = lam^3 g(u1) g(u2) (exact for
a renewal train). The tool averages N_SURR surrogates; that average has the same expectation as
one, so N_SURR does not enter.

    train = EventTrain.renewal(intervals=gaps)                 # stationary renewal train
    c = coefficients(w, sigma, n_cells, train)                 # dict a2, b2, a3, b3, c3
    f2, f3 = cumulants_from(c, k, lam)

Constructors: `poisson()`, `hard_core(d)`, `renewal(intervals | density, mean)`,
`palm(intervals, lam)` (real data, where lam is not 1 / mean gap) and `from_times(...)`
(empirical, circular lags); `.fixed_count(m)` conditions on the recording's event count.
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
from scipy import signal, stats

HERE = Path(__file__).resolve().parent
_TOOLS = str(HERE.parents[2] / "tools")
if _TOOLS not in sys.path:
    sys.path.insert(0, _TOOLS)
import measure_coordination_rates as mcr  # noqa: E402

R_MAX = 340.0     # s; longest lag tabulated (the surrogate spans 2w(N-1): 256 s at w = 4, N = 33)
DH = 0.01         # s; lag grid of the pair correlation
SIGMA_GRID = np.geomspace(0.005, 5.0, 46)   # s; the joint fit's log-sigma table
SURROGATES = ("tool", "independent")


class EventTrain:
    """g_E(|tau|) of a stationary event train on a fine lag grid, 1 beyond it.

    rho_2(tau) = lam^2 g_E(tau) is the density of ordered pairs of distinct events at lag tau.
    The intensity lam itself is not stored: it is a parameter of the prediction (and of the fit).
    Coefficients are cached on the object, so build a train once and reuse it."""

    def __init__(self, tau, g, name, lam_f=None, cv2=1.0, offset=0.0, kind="table"):
        self.tau, self.g, self.name = np.asarray(tau, float), np.asarray(g, float), name
        self.lam_f = lam_f      # 1 / mean interval, where an interval law made the train
        self.cv2 = cv2          # squared coefficient of variation of the intervals
        self.offset = offset    # uniform shift of g_E (the fixed-count deficit)
        self.kind = kind
        self._cache: dict = {}

    def __call__(self, t):
        return np.interp(np.abs(t), self.tau, self.g, right=1.0) + self.offset

    def __repr__(self):
        return f"EventTrain({self.name})"

    def fixed_count(self, m):
        """The same train given exactly m events in the recording (derivation A7).

        The tool's cumulants are sample moments over one recording, so their expectation is
        conditional on m. A stationary renewal train has int (g - 1) dtau = (CV^2 - 1) / lam over
        its correlation range; with the count fixed, the integral over the recording is -1 / lam.
        To first order the difference is a uniform deficit of CV^2 / m. It cancels in f2 and
        moves f3 by -3 lam^2 k (k)_2 w a2 CV^2 / m. The conditioned train is kept, so its
        coefficients are cached across calls."""
        key = ("fixed_count", float(m))
        if key not in self._cache:
            self._cache[key] = EventTrain(self.tau, self.g, self.name + f", m={m:g}", self.lam_f,
                                          self.cv2, self.offset - self.cv2 / m, self.kind)
        return self._cache[key]

    # constructors -----------------------------------------------------------------
    @classmethod
    def poisson(cls):
        return cls([0.0, R_MAX], [1.0, 1.0], "Poisson", kind="poisson")

    @classmethod
    def hard_core(cls, d=20.0):
        """No pair closer than d, uncorrelated beyond: `theory.py`'s assumption at d = 20 s."""
        eps = 1e-6
        return cls([0.0, d - eps, d, R_MAX], [0.0, 0.0, 1.0, 1.0], f"hard-core {d:g} s",
                   kind="hard_core")

    @classmethod
    def renewal(cls, intervals=None, density=None, mean=None, cv2=None, bw=0.05,
                name="renewal"):
        """A stationary renewal train from its interval law, g_E = h / lam_f (derivation 6).

        ``intervals``: samples (s), smoothed by a Gaussian kernel of ``bw`` s. Or ``density``: a
        callable on [0, inf) with its ``mean`` (and ``cv2``, default 1). h = sum_n f^{*n} is the
        renewal density, the density of other events at lag tau after a given event, built by
        repeated FFT convolution out to R_MAX; lam_f = 1 / mean interval."""
        tau, h, mean, cv2 = _renewal_density(intervals, density, mean, cv2, bw)
        lam_f = 1.0 / mean
        return cls(tau, _taper(tau, h / lam_f), name, lam_f=lam_f, cv2=cv2, kind="renewal")

    @classmethod
    def palm(cls, intervals, lam, bw=0.05, name="palm"):
        """Real data: an interval histogram whose mean does not match the event rate ``lam``.

        On real recordings the two disagree (fast stream: 9.7 events per hour, against 36 per hour
        implied by the mean gap of 101 s). This form keeps the density of neighbours seen from an
        event, which is what a gap histogram measures: g_E = 1 + (h - lam_f) / lam, tending to 1
        at long lags. With lam = 1 / mean interval it is `renewal`.

        UNTESTED ON REAL DATA. The derivation's simulations all had lam = 1 / mean gap, where the
        two forms coincide; `tests/test_synthetic_event_train.py` checks only that the joint fit
        recovers (sigma, k, lam) through this form on a simulated renewal train of known rate.
        Whether real gaps, which are measured within detected activity and merged below 2 s, give
        the right neighbour density is open (goal page, plan item 5)."""
        tau, h, mean, cv2 = _renewal_density(intervals, None, None, None, bw)
        lam_f = 1.0 / mean
        g = 1.0 + (h - lam_f) / lam
        return cls(tau, _taper(tau, g), name + f", lam={lam:.4g}", lam_f=lam_f, cv2=cv2,
                   kind="palm")

    @classmethod
    def from_times(cls, times, T, bin_sec=0.5, name="empirical"):
        """The empirical pair correlation of event trains on [0, T), with circular lags (the
        surrogate's shifts are circular).

        ``times``: one array of event times per recording. rho_2 at |lag| in a bin is the ordered
        pairs there over (n_rec T 2 bin), and g_E = rho_2 / lam^2 with lam = events / (n_rec T).
        Because each recording's count is what it is, the result is already conditional on the
        counts: do not apply `fixed_count` on top."""
        edges = np.arange(0.0, R_MAX + bin_sec, bin_sec)
        hist = np.zeros(edges.size - 1)
        n_ev = 0
        for tt in times:
            tt = np.asarray(tt, float)
            n_ev += tt.size
            d = (tt[None, :] - tt[:, None]) % T
            d = np.minimum(d, T - d)[~np.eye(tt.size, dtype=bool)]
            hist += np.histogram(d, edges)[0]
        lam = n_ev / (len(times) * T)
        g = hist / len(times) / (T * 2 * np.diff(edges)) / lam ** 2
        tau = 0.5 * (edges[1:] + edges[:-1])
        return cls(np.concatenate([[0.0], tau]), np.concatenate([[g[0]], g]), name,
                   kind="empirical")


def _renewal_density(intervals, density, mean, cv2, bw):
    """h(tau) = sum_n f^{*n}(tau) on [0, R_MAX], step DH; returns (tau, h, mean, cv2)."""
    n = int(round(R_MAX / DH)) + 1
    tau = np.arange(n) * DH
    if intervals is not None:
        x = np.asarray(intervals, float)
        mean = float(x.mean()) if mean is None else mean
        cv2 = float(x.var() / x.mean() ** 2) if cv2 is None else cv2
        # sum of Gaussian kernels, binned: histogram then smooth (exact enough at DH << bw)
        hist = np.bincount(np.clip(np.round(x / DH).astype(int), 0, n - 1), minlength=n)[:n]
        hist[-1] = 0                     # mass beyond R_MAX does not reach the windows
        if bw > 0:
            ker = stats.norm.pdf(np.arange(-int(6 * bw / DH), int(6 * bw / DH) + 1) * DH, 0, bw)
            f = np.convolve(hist / x.size, ker * DH, mode="same") / DH
        else:
            f = hist / x.size / DH
    else:
        if density is None or mean is None:
            raise ValueError("give interval samples, or a density with its mean")
        f = np.asarray(density(tau), float)
        cv2 = 1.0 if cv2 is None else cv2
    h, cur = f.copy(), f.copy()
    nfft = 1 << int(np.ceil(np.log2(2 * n)))
    F = np.fft.rfft(f, nfft)
    for _ in range(2000):
        cur = np.fft.irfft(np.fft.rfft(cur, nfft) * F, nfft)[:n] * DH
        cur[cur < 0] = 0
        h += cur
        if cur.sum() * DH < 1e-10:
            break
    return tau, h, mean, cv2


def _taper(tau, g):
    """Beyond the tabulated range the train is taken as uncorrelated; taper the last 20 s."""
    tap = np.clip((R_MAX - tau) / 20.0, 0, 1)
    return 1.0 + (g - 1.0) * tap


# ------------------------------------------------------------------ the coefficients

def _corr(a, b):
    """c[j] = sum_t a[t] b[t + j], lags j = -(len(a)-1) .. len(b)-1."""
    return signal.fftconvolve(a[::-1], b)


def coefficients(w: float, sigma: float, n_cells: int, train: EventTrain,
                 surrogate: str = "tool", parts: bool = False) -> dict:
    """Recording-minus-surrogate coefficients (a2, b2, a3, b3, c3) of f2, f3 at one window.

    Recording: every participant's onset at t_e + eps, eps ~ N(0, sigma^2). Surrogate
    ``"tool"``: cell x shifted by d_x = SURR_SPACING w x, x = 0 .. N-1 (the tool's permutation
    and common shift leave the expectation unchanged, by exchangeability of membership and
    stationarity); it carries the surrogate's dependence on the train and its leakage.
    ``"independent"``: the surrogate `theory.py` assumes, shifted copies uncorrelated with each
    other and no leakage; with ``hard_core(d >= w + 8 sigma)`` it reproduces
    `theory.predicted_excess_cumulants`. Cached on ``train``."""
    if surrogate not in SURROGATES:
        raise ValueError(surrogate)
    key = (float(w), float(sigma), int(n_cells), surrogate, parts)
    if key not in train._cache:
        train._cache[key] = _coefficients(float(w), float(sigma), int(n_cells), train,
                                          surrogate, parts)
    return dict(train._cache[key])


def _coefficients(w, sigma, N, gE, surrogate, parts):
    n_w = int(max(50, np.ceil(5 * w / sigma)))          # grid points per window
    dl = w / n_w
    sp = mcr.SURR_SPACING * n_w                         # surrogate spacing, grid steps
    pad = int(np.ceil((8 * sigma) / dl)) + 2
    # q(t): event at t, one onset lands in [0, w); support (-8 sigma, w + 8 sigma)
    j = np.arange(n_w + 2 * pad + 1)
    t = -pad * dl + j * dl
    q = stats.norm.cdf((w - t) / sigma) - stats.norm.cdf(-t / sigma)
    nq = q.size
    A2r, A3r = q @ q * dl, np.sum(q ** 3) * dl

    # lag integrals int (g - 1)(tau) M(tau) dtau on the pair-correlation grid
    taug = np.arange(-R_MAX, R_MAX + DH / 2, DH)
    gm1 = gE(taug) - 1.0

    def lagint(M, n_a):
        lags = (np.arange(M.size) - (n_a - 1)) * dl
        return float(np.sum(gm1 * np.interp(taug, lags, M, left=0.0, right=0.0)) * DH)

    B2r = lagint(_corr(q, q) * dl, nq)
    B3r = lagint(_corr(q, q ** 2) * dl, nq)

    # triples: Q3(x, y) = int q(t) q(t+x) q(t+x+y) dt on a coarse 2-D grid
    s2 = max(1, int(round(((w + 6 * sigma) / 12) / dl)))
    d2 = s2 * dl
    nx = int(np.ceil((n_w + pad) / s2))
    xs = np.arange(-nx, nx + 1) * s2                    # grid steps
    xs = xs[np.abs(xs) < nq]
    Q3 = np.zeros((xs.size, xs.size))
    for ix, xstep in enumerate(xs):
        prod = np.zeros(nq)
        if xstep >= 0:
            prod[:nq - xstep] = q[:nq - xstep] * q[xstep:]
        else:
            prod[-xstep:] = q[-xstep:] * q[:nq + xstep]
        c = _corr(prod, q) * dl                         # lag z = x + y
        idx = xs[ix] + xs + (nq - 1)
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
    Cs00 = Cr / N ** 2          # the surrogate's same-cell triples, unshifted

    if surrogate == "independent":
        # theory.py's surrogate: only same-cell terms survive the shift, no leakage
        A2s = A3s = B3s = 0.0
        B2s, Cs = B2r / N, Cs00
    else:
        # surrogate sums S_r(t) = sum_x q(t + d_x)^r: q shifted left by sp * x
        L = nq + sp * (N - 1)
        S = np.zeros((4, L))
        for x in range(N):
            o = sp * (N - 1 - x)          # array index offset; the common shift is immaterial
            for r in (1, 2, 3):
                S[r, o:o + nq] += q ** r
        mu1s = S[1] / N
        mu2s = (S[1] ** 2 - S[2]) / (N * (N - 1))
        mu3s = (S[1] ** 3 - 3 * S[1] * S[2] + 2 * S[3]) / (N * (N - 1) * (N - 2))
        A2s, A3s = mu2s.sum() * dl, mu3s.sum() * dl
        B2s = lagint(_corr(mu1s, mu1s) * dl, L)
        B3s = lagint(_corr(mu1s, mu2s) * dl, L)
        if gE.kind == "poisson" and gE.offset == 0.0:
            Cs = 0.0                      # K = 0 everywhere
        else:
            # cells at lattice indices x, x+m1, x+m1+m2; weight c(m1, m2) / N^3
            ms = np.arange(-(N - 1), N)
            M1, M2 = np.meshgrid(ms, ms, indexing="ij")
            x0 = np.arange(N)[:, None, None]
            cnt = np.sum((x0 + M1 >= 0) & (x0 + M1 < N) & (x0 + M1 + M2 >= 0)
                         & (x0 + M1 + M2 < N), axis=0)
            sel = cnt > 0
            M1, M2, cnt = M1[sel], M2[sel], cnt[sel]
            Cs = 0.0
            step = mcr.SURR_SPACING * w
            for i0 in range(0, M1.size, 400):
                a = (step * M1[i0:i0 + 400])[:, None, None]
                b = (step * M2[i0:i0 + 400])[:, None, None]
                v = np.sum(K(X[None] - a, Y[None] - b) * wQ[None], axis=(1, 2))
                Cs += float(np.sum(cnt[i0:i0 + 400] * v)) / N ** 3
    out = dict(a2=A2r - A2s, b2=B2r - B2s, a3=A3r - A3s, b3=B3r - B3s, c3=Cr - Cs)
    if parts:
        out.update(A2r=A2r, A2s=A2s, A3r=A3r, A3s=A3s, B2r=B2r, B2s=B2s, B3r=B3r, B3s=B3s,
                   Cr=Cr, Cs=Cs, Cs00=Cs00)
    return out


def cumulants_from(c: dict, k: float, lam: float) -> tuple[float, float]:
    """f2, f3 from the coefficients: polynomials in k and lam."""
    f2 = lam * k * (k - 1) * c["a2"] + lam ** 2 * k ** 2 * c["b2"]
    f3 = (lam * k * (k - 1) * (k - 2) * c["a3"] + 3 * lam ** 2 * k * k * (k - 1) * c["b3"]
          + lam ** 3 * k ** 3 * c["c3"])
    return f2, f3


COEF = ("a2", "b2", "a3", "b3", "c3")


def coefficient_table(train: EventTrain, n_cells: int, windows, sigma_grid=SIGMA_GRID,
                      surrogate: str = "tool") -> dict:
    """{w: array (len(sigma_grid), 5)} of the coefficients, for interpolation in log sigma.
    Cached on ``train``, so a joint fit over many recordings tabulates once."""
    key = ("table", int(n_cells), tuple(float(w) for w in windows),
           tuple(np.round(np.log(sigma_grid), 12)), surrogate)
    if key not in train._cache:
        train._cache[key] = {float(w): np.array([[coefficients(w, s, n_cells, train, surrogate)[c]
                                                  for c in COEF] for s in sigma_grid])
                             for w in windows}
    return train._cache[key]


def interpolated(table: dict, w: float, sigma: float, sigma_grid=SIGMA_GRID) -> dict:
    """The coefficients at (w, sigma) from a `coefficient_table`, linear in log sigma."""
    T = table[float(w)]
    ls = np.log(sigma)
    lg = np.log(sigma_grid)
    return {c: float(np.interp(ls, lg, T[:, i])) for i, c in enumerate(COEF)}
