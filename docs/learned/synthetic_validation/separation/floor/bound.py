"""Resolution floor for two coordinated events from onset times alone.

Companion to derivation.md.  Run:  python bound.py  [--quick]
Writes bound_output.txt, bound_results.json and synth_recovery_plot_separation-floor-any-method_20261025.png next to itself.

Model (see derivation.md section 1):
  two events, centres Delta apart, k cells each out of N = 33, memberships drawn at
  random (cells may be shared); each participant's onset = centre + N(0, sigma^2);
  onsets rounded to 0.1 s frames; independent Poisson background at b Hz per cell;
  within one cell, an onset closer than g to the previous one is not seen (g = one
  frame is the model as stated; 0.40 s / 3.20 s are the measured within-cell floors).
Null: one event whose membership is the union of the two, jitter sigma' free.

Tests (all calibrated by simulation under the null, 5 % false alarm):
  pooled   - likelihood ratio, one vs two Gaussian bursts on a Poisson background,
             cell labels discarded (the identity-free floor);
  identity - likelihood ratio of the per-cell model, which knows which onsets came
             from the same cell (Bernoulli membership, background, both free params);
  labelled - oracle that knows which event each onset belongs to (t test): the most
             that membership knowledge could ever add.
"""
from __future__ import annotations

import ctypes
import json
import math
import os
import sys
import time
from concurrent.futures import ProcessPoolExecutor

import numpy as np
from scipy import stats
from scipy.special import comb


def logsumexp(x, axis):
    mx = np.max(x, axis=axis, keepdims=True)
    mx = np.where(np.isfinite(mx), mx, 0.0)
    with np.errstate(divide="ignore"):
        return np.log(np.sum(np.exp(x - mx), axis=axis)) + np.squeeze(mx, axis)

HERE = os.path.dirname(os.path.abspath(__file__))
N_CELLS = 33
FRAME = 0.1          # s
WINDOW = 12.0        # s, analysis window centred on the pair
ALPHA = 0.05
POWERS = (0.5, 0.8)
SMIN = 0.05          # s, lower bound on a fitted jitter (keeps the likelihood bounded)
CAL_FACTOR = 2.0     # calibration neighbourhood in sigma' (see analyse)
MC = 4               # onsets kept per cell inside the window (cap; truncations counted)
LOG2PI = math.log(2 * math.pi)

SIGMAS = (0.105, 0.131, 0.5)
KS = (5, 7, 10, 13, 20)
BS = (0.0, 0.0096, 0.05)
GS = (0.1, 0.4, 3.2)   # within-cell floor: one frame (model as stated), fast, slow


class _PPTS(ctypes.Structure):
    _fields_ = [("Version", ctypes.c_ulong), ("ControlMask", ctypes.c_ulong), ("StateMask", ctypes.c_ulong)]


def unthrottle():
    """Windows: stop the OS from running pool workers as throttled background processes."""
    if os.name != "nt":
        return
    k = ctypes.windll.kernel32
    st = _PPTS(1, 1, 0)
    k.SetProcessInformation(k.GetCurrentProcess(), 4, ctypes.byref(st), ctypes.sizeof(st))


def lphi(t, mu, s):
    return -0.5 * ((t - mu) / s) ** 2 - np.log(s) - 0.5 * LOG2PI


# --------------------------------------------------------------------------- clean case
def em_mix(x, ncomp, init_mu, init_s, init_a, beta=0.0, L=1.0, n_iter=150, smin=1e-3,
           equal=False, w=None):
    """EM for a Poisson-process intensity beta + sum_j a_j N(mu_j, s^2) on rows of x.

    x (R, M) with mask w (R, M).  With beta = 0 and free a_j this is the ordinary
    mixture likelihood plus a Poisson count term that is identical under both
    hypotheses, so the likelihood ratio is the usual mixture one.
    Returns log-likelihood (R,), mu (R, C), s (R,), a (R, C).
    """
    if w is None:
        w = np.ones_like(x)
    mu, s, a = init_mu.copy(), init_s.copy(), init_a.copy()
    logb = math.log(beta) if beta > 0 else -np.inf
    xx = x[:, :, None]
    for it in range(n_iter + 1):
        comp = np.log(np.maximum(a, 1e-300))[:, None, :] + lphi(xx, mu[:, None, :], s[:, None, None])
        tot = logsumexp(np.concatenate([comp, np.full(comp.shape[:2] + (1,), logb)], axis=2), axis=2)
        if it == n_iter:
            break
        r = np.exp(comp - tot[:, :, None]) * w[:, :, None]
        araw = r.sum(1)
        a = np.full_like(araw, araw.sum(1, keepdims=True) / ncomp) if equal else araw
        den = np.maximum(araw, 1e-12)
        mu = np.where(araw > 1e-9, (r * xx).sum(1) / den, mu)
        s2 = (r * (xx - mu[:, None, :]) ** 2).sum((1, 2)) / np.maximum(araw.sum(1), 1e-12)
        s = np.maximum(np.sqrt(s2), smin)
    ll = (tot * w).sum(1) - beta * L - a.sum(1)
    return ll, mu, s, a


def lrt_mixture(x, w=None, beta=0.0, L=1.0, smin=1e-3, equal=False, n_iter=150):
    """2 x log LR of two Gaussian bursts against one, maximised over several starts.

    Returns (stat, H0 mu, H0 s, H1 mu (R,2), H1 s)."""
    R, M = x.shape
    if w is None:
        w = np.ones_like(x)
    n = w.sum(1)
    xm = np.where(w > 0, x, np.nan)
    med = np.nanmedian(xm, 1)
    # densest point: most neighbours within +-0.5 (in x units)
    mode2 = None
    if M <= 120:   # densest point: most neighbours within +-0.5 s
        d = np.abs(x[:, :, None] - x[:, None, :]) < 0.5
        cnt = (d * w[:, None, :]).sum(2) * w
        mode = x[np.arange(R), cnt.argmax(1)]
        # second-densest point at least 0.5 s from the first (a second burst the
        # one-burst fit may have handed to the background)
        far = np.abs(x - mode[:, None]) >= 0.5
        mode2 = x[np.arange(R), np.where(far, cnt, -1).argmax(1)]
    else:
        mode = med
    sd = np.sqrt(np.nanvar(xm, 1)) + smin
    best0 = None
    for m0, s0 in ((med, sd), (mode, np.maximum(sd / 3, smin)), (mode, np.maximum(sd / 8, smin))):
        ll, mu, s, a = em_mix(x, 1, m0[:, None], s0, (n / 2 + 0.5)[:, None], beta, L, n_iter, smin, w=w)
        if best0 is None:
            best0 = [ll, mu, s, a]
        else:
            better = ll > best0[0]
            for i, v in enumerate((ll, mu, s, a)):
                best0[i] = np.where(better.reshape((-1,) + (1,) * (v.ndim - 1)), v, best0[i])
    ll0, mu0, s0, a0 = best0
    mu0 = mu0[:, 0]
    best1 = None
    starts = []
    for dd in (0.6, 1.2, 2.0):
        for frac in (0.5, 0.3, 0.7):
            starts.append((dd, frac))
    inits = []
    for dd, frac in starts:
        if equal and frac != 0.5:
            continue
        inits.append((np.stack([mu0 - dd * s0 * (1 - frac) * 2, mu0 + dd * s0 * frac * 2], 1),
                      np.maximum(s0 * math.sqrt(max(0.15, 1 - dd ** 2 / 4)), smin),
                      np.stack([a0[:, 0] * frac, a0[:, 0] * (1 - frac)], 1)))
    if beta > 0 and mode2 is not None:
        for sc in (0.15, 0.4):
            inits.append((np.stack([mode, mode2], 1), np.full(R, max(sc, smin)),
                          np.stack([n / 3, n / 3], 1)))
    for mu_i, s_i, a_i in inits:
        ll, mu, s, a = em_mix(x, 2, mu_i, s_i, a_i, beta, L, n_iter, smin, equal=equal, w=w)
        if best1 is None:
            best1 = [ll, mu, s]
        else:
            better = ll > best1[0]
            best1 = [np.where(better, ll, best1[0]), np.where(better[:, None], mu, best1[1]),
                     np.where(better, s, best1[2])]
    stat = np.maximum(2 * (best1[0] - ll0), 0.0)
    return stat, mu0, s0, best1[1], best1[2]


def kurtosis_stat(x):
    """Minus the sample excess kurtosis (large = platykurtic = bimodal-looking)."""
    xc = x - x.mean(1, keepdims=True)
    m2 = (xc ** 2).mean(1)
    m4 = (xc ** 4).mean(1)
    return -(m4 / m2 ** 2 - 3.0)


def kurtosis_closed_form(n, power, alpha=ALPHA):
    """Delta/sigma at which the one-sided kurtosis test reaches `power` (null variance 24/n).

    Excess kurtosis of an equal two-Gaussian mixture, half-separation r = Delta/(2 sigma):
    gamma2 = -2 r^4 / (1 + r^2)^2.  Solve |gamma2| = (z_a + z_b) sqrt(24 / n)."""
    c = (stats.norm.ppf(1 - alpha) + stats.norm.ppf(power)) * math.sqrt(24.0 / n)
    if c >= 2:
        return float("inf")
    u = math.sqrt(c / 2)          # r^2/(1+r^2) = u
    r = math.sqrt(u / (1 - u))
    return 2 * r


def known_sigma_closed_form(n, power, alpha=ALPHA):
    """Delta/sigma for the variance test with sigma known (Gaussian approximation of the
    mixture): variance inflates by (1 + r^2), r = Delta / (2 sigma)."""
    lo, hi = 0.0, 20.0
    crit = stats.chi2.ppf(1 - alpha, n - 1)
    for _ in range(80):
        mid = (lo + hi) / 2
        pwr = stats.chi2.sf(crit / (1 + (mid / 2) ** 2), n - 1)
        lo, hi = (mid, hi) if pwr < power else (lo, mid)
    return hi


# --------------------------------------------------------------------------- full model
def simulate(rng, R, k, sigma, delta, b, g, null_sigma=None, disjoint=False):
    """Return per-cell onsets T (R, N, MC) NaN-padded and number truncated.

    null_sigma given -> null: one event, membership = union of two random k-sets."""
    N = N_CELLS
    order_a = rng.random((R, N)).argsort(1)
    inA = np.zeros((R, N), bool)
    np.put_along_axis(inA, order_a[:, :k], True, 1)
    if disjoint:
        inB = np.zeros((R, N), bool)
        np.put_along_axis(inB, order_a[:, k:2 * k], True, 1)
    else:
        order_b = rng.random((R, N)).argsort(1)
        inB = np.zeros((R, N), bool)
        np.put_along_axis(inB, order_b[:, :k], True, 1)
    u = rng.uniform(-FRAME / 2, FRAME / 2, (R, 1))
    if null_sigma is None:
        tA = np.where(inA, -delta / 2 + u + sigma * rng.standard_normal((R, N)), np.nan)
        tB = np.where(inB, delta / 2 + u + sigma * rng.standard_normal((R, N)), np.nan)
        ev = np.stack([tA, tB], 2)
    else:
        inU = inA | inB
        tE = np.where(inU, u + null_sigma * rng.standard_normal((R, N)), np.nan)
        ev = tE[:, :, None]
    nb = rng.poisson(b * WINDOW, (R, N)) if b > 0 else np.zeros((R, N), int)
    bmax = int(nb.max()) if nb.size else 0
    if bmax > 0:
        tb = rng.uniform(-WINDOW / 2, WINDOW / 2, (R, N, bmax))
        tb = np.where(np.arange(bmax)[None, None, :] < nb[:, :, None], tb, np.nan)
        allt = np.concatenate([ev, tb], 2)
    else:
        allt = ev
    allt = np.round(allt / FRAME) * FRAME                     # frames
    allt = np.where(np.abs(allt) <= WINDOW / 2, allt, np.nan)
    allt = np.sort(allt, 2)                                   # NaN last
    # within-cell floor g: an onset closer than g to the last seen one is not seen
    last = allt[:, :, 0].copy()
    for j in range(1, allt.shape[2]):
        tj = allt[:, :, j]
        keep = (tj - last >= g - 1e-9)
        allt[:, :, j] = np.where(keep, tj, np.nan)
        last = np.where(keep, tj, last)
    allt = np.sort(allt, 2)
    m = np.isfinite(allt).sum(2)
    trunc = int((m > MC).sum())
    if allt.shape[2] > MC:
        # keep the MC onsets nearest the window centre
        key = np.where(np.isfinite(allt), np.abs(allt), np.inf)
        idx = np.argsort(key, 2)[:, :, :MC]
        allt = np.sort(np.take_along_axis(allt, idx, 2), 2)
    if allt.shape[2] < MC:
        allt = np.concatenate([allt, np.full((R, N, MC - allt.shape[2]), np.nan)], 2)
    return allt, trunc


def pooled_arrays(T):
    R = T.shape[0]
    flat = T.reshape(R, -1)
    order = np.argsort(~np.isfinite(flat), 1, kind="stable")
    flat = np.take_along_axis(flat, order, 1)
    M = max(int(np.isfinite(flat).sum(1).max()), 2)
    flat = flat[:, :M]
    w = np.isfinite(flat).astype(float)
    return np.nan_to_num(flat), w


# identity model patterns ------------------------------------------------------
# H1 roles per cell: none; A only (onset j); B only (onset j); in both, both onsets seen
# (i, j); in both but the two onsets closer than the within-cell floor g, so only one
# is seen (onset j, flag MER).
_P1 = ([(-1, -1, 0)] + [(j, -1, 0) for j in range(MC)] + [(-1, j, 0) for j in range(MC)]
       + [(i, j, 0) for i in range(MC) for j in range(MC) if i != j] + [(j, j, 1) for j in range(MC)])
IA = np.array([p[0] for p in _P1])
IB = np.array([p[1] for p in _P1])
MER = np.array([p[2] for p in _P1], bool)
NMEMB1 = (IA >= 0).astype(int) + (IB >= 0).astype(int)        # memberships (merged: 2)
NEV1 = np.where(MER, 1, NMEMB1)                               # onsets seen from events
MAX1 = np.maximum(IA, IB)
IE = np.arange(-1, MC)
NEV0 = (IE >= 0).astype(int)


def _logb_term(m, nev, logb):
    bg = m[:, :, None] - nev[None, None, :]
    with np.errstate(invalid="ignore"):
        return np.where(bg == 0, 0.0, bg * logb), bg >= 0


def em_identity(T, b, init, n_iter=60, two=True, g=FRAME):
    """EM for the per-cell likelihood.  Returns log-likelihood (R,) (may be -inf)."""
    R, N, S = T.shape
    fin = np.isfinite(T)
    m = fin.sum(2)
    T0 = np.nan_to_num(T)
    logb = math.log(b) if b > 0 else -np.inf
    if two:
        muA, muB, s, p = (v.copy() for v in init)
        ia, ib = np.clip(IA, 0, None), np.clip(IB, 0, None)
        mer = MER[None, None, :]
        hasA = ((IA >= 0) & ~MER)[None, None, :]
        hasB = ((IB >= 0) & ~MER)[None, None, :]
        nmemb = NMEMB1[None, None, :]
        lbt, okbg = _logb_term(m, NEV1, logb)
        valid = (MAX1[None, None, :] < m[:, :, None]) & okbg
        TA, TB = T0[:, :, ia], T0[:, :, ib]
        for it in range(n_iter + 1):
            lq, l1q = np.log(p)[:, None, None], np.log1p(-p)[:, None, None]
            memb = nmemb * lq + (2 - nmemb) * l1q
            fA = lphi(TA, muA[:, None, None], s[:, None, None])
            fB = lphi(TB, muB[:, None, None], s[:, None, None])
            dd = np.abs(muB - muA)
            sd = s * math.sqrt(2)
            pm = np.maximum(stats.norm.cdf((g - dd) / sd) - stats.norm.cdf((-g - dd) / sd), 1e-300)
            fM = np.logaddexp(fA, fB) - math.log(2) + np.log(pm)[:, None, None]
            on = np.where(mer, fM, np.where(hasA, fA, 0.0) + np.where(hasB, fB, 0.0))
            lw = np.where(valid, memb + on + lbt, -np.inf)
            cl = logsumexp(lw, 2)
            if it == n_iter:
                break
            okc = np.isfinite(cl)[:, :, None]
            wp = np.where(okc, np.exp(lw - np.where(okc, cl[:, :, None], 0.0)), 0.0)
            rA = np.exp(fA - np.logaddexp(fA, fB))
            wA = wp * hasA + wp * mer * rA
            wB = wp * hasB + wp * mer * (1 - rA)
            EA, EB = wA.sum((1, 2)), wB.sum((1, 2))
            muA = np.where(EA > 1e-9, (wA * TA).sum((1, 2)) / np.maximum(EA, 1e-12), muA)
            muB = np.where(EB > 1e-9, (wB * TB).sum((1, 2)) / np.maximum(EB, 1e-12), muB)
            s2 = ((wA * (TA - muA[:, None, None]) ** 2).sum((1, 2)) +
                  (wB * (TB - muB[:, None, None]) ** 2).sum((1, 2))) / np.maximum(EA + EB, 1e-12)
            s = np.maximum(np.sqrt(s2), SMIN)
            p = np.clip((wp * nmemb).sum((1, 2)) / (2 * N), 1e-4, 1 - 1e-4)
        return cl.sum(1)
    mu, s, q = (v.copy() for v in init)
    ie = np.clip(IE, 0, None)
    hasE = (IE >= 0)[None, None, :]
    lbt, okbg = _logb_term(m, NEV0, logb)
    valid = (IE[None, None, :] < m[:, :, None]) & okbg
    TE = T0[:, :, ie]
    for it in range(n_iter + 1):
        memb = np.where(hasE, np.log(q)[:, None, None], np.log1p(-q)[:, None, None])
        LE = np.where(hasE, lphi(TE, mu[:, None, None], s[:, None, None]), 0.0)
        lw = np.where(valid, memb + LE + lbt, -np.inf)
        cl = logsumexp(lw, 2)
        if it == n_iter:
            break
        okc = np.isfinite(cl)[:, :, None]
        wp = np.where(okc, np.exp(lw - np.where(okc, cl[:, :, None], 0.0)), 0.0) * hasE
        E = wp.sum((1, 2))
        mu = np.where(E > 1e-9, (wp * TE).sum((1, 2)) / np.maximum(E, 1e-12), mu)
        s = np.maximum(np.sqrt((wp * (TE - mu[:, None, None]) ** 2).sum((1, 2)) / np.maximum(E, 1e-12)), SMIN)
        q = np.clip(E / N, 1e-4, 1 - 1e-4)
    return cl.sum(1)


def statistics(T, b, g=FRAME):
    """Return pooled stat, identity stat, fitted null jitter, two-onset-cell count."""
    x, w = pooled_arrays(T)
    beta = N_CELLS * b
    sp, mu0, s0, mu1, s1 = lrt_mixture(x, w=w, beta=beta, L=WINDOW, smin=SMIN, n_iter=100)
    R = T.shape[0]
    p0 = np.full(R, 0.25)
    ll0 = em_identity(T, b, (mu0, s0, np.full(R, 0.4)), two=False)
    best = None
    for (ma, mb, ss) in ((mu1[:, 0], mu1[:, 1], s1), (mu0 - s0, mu0 + s0, np.maximum(s0 * 0.6, SMIN))):
        ll = em_identity(T, b, (ma, mb, ss, p0), two=True, g=g)
        best = ll if best is None else np.maximum(best, ll)
    with np.errstate(invalid="ignore"):
        # signed: the two-event per-cell model does not nest the one-event one
        si = np.where(np.isinf(ll0) & (ll0 < 0), np.inf, 2 * (best - ll0))
    two = (np.isfinite(T).sum(2) >= 2).sum(1)
    return sp, si, s0, two


# --------------------------------------------------------------------------- helpers
def delta_grid(sigma):
    a = sigma * np.concatenate([np.arange(0, 6.01, 0.5), np.arange(7, 16.01, 1.0)])
    b = np.arange(0.2, 4.01, 0.3)
    return np.unique(np.round(np.concatenate([a, b[b <= max(16 * sigma, 4.0)]]), 4))


def null_grid(sigma):
    top = math.sqrt(sigma ** 2 + (max(16 * sigma, 4.0) / 2) ** 2)
    return np.geomspace(sigma, top, 7)


def first_crossing(deltas, power, target):
    pw = np.maximum.accumulate(np.asarray(power))
    if pw[0] >= target:
        return 0.0
    idx = np.nonzero(pw >= target)[0]
    if len(idx) == 0:
        return float("inf")
    i = idx[0]
    d0, d1, p0, p1 = deltas[i - 1], deltas[i], pw[i - 1], pw[i]
    return float(d0 + (target - p0) / (p1 - p0) * (d1 - d0)) if p1 > p0 else float(d1)


def labelled_bound(k, sigma, power, alpha=ALPHA):
    """Two-sample t test with labels known; jitter inflated by frame rounding."""
    se = math.sqrt(sigma ** 2 + FRAME ** 2 / 12) * math.sqrt(2.0 / k)
    df = 2 * k - 2
    tc = stats.t.ppf(1 - alpha / 2, df)
    lo, hi = 0.0, 50 * se
    for _ in range(80):
        mid = (lo + hi) / 2
        nc = mid / se
        pwr = stats.nct.sf(tc, df, nc) + stats.nct.cdf(-tc, df, nc)
        lo, hi = (mid, hi) if pwr < power else (lo, mid)
    return hi


def p_share(k, N=N_CELLS):
    exact = 1 - comb(N - k, k, exact=True) / comb(N, k, exact=True)
    approx = 1 - (1 - k / N) ** k
    return exact, approx


def p_second_seen(delta, sigma, g):
    """P(a shared cell shows both onsets): its two onsets differ by D ~ N(delta, 2 sigma^2)
    and the second is seen only if |D| >= g (the within-cell floor)."""
    sd = sigma * math.sqrt(2)
    return stats.norm.sf((g - delta) / sd) + stats.norm.cdf((-g - delta) / sd)


def power_shared_only(delta, k, sigma, g, N=N_CELLS):
    """Zero background: any cell with two onsets rejects the one-event null outright.
    Power = 1 - E[(1 - P_seen)^S], S ~ hypergeometric(N, k, k) shared cells."""
    s = np.arange(k + 1)
    pmf = stats.hypergeom(N, k, k).pmf(s)
    return float(1 - np.sum(pmf * (1 - p_second_seen(delta, sigma, g)) ** s))


def solve_shared_only(k, sigma, g, target):
    if power_shared_only(1e3, k, sigma, g) < target:
        return float("inf")
    if power_shared_only(0.0, k, sigma, g) >= target:
        return 0.0
    lo, hi = 0.0, 1e3
    for _ in range(100):
        mid = (lo + hi) / 2
        lo, hi = (mid, hi) if power_shared_only(mid, k, sigma, g) < target else (lo, mid)
    return hi


def closed_form_section():
    out = ["", "=" * 96,
           "2b. CLOSED FORM, shared cells alone, b = 0 (no background): resolvable Delta (s) 50 % / 80 %",
           "    power = 1 - sum_s P(S = s) (1 - P_seen)^s, S hypergeometric; false alarm exactly 0",
           "    ceiling = P(S >= 1), the power as Delta -> infinity; 'any' = reached at Delta = 0",
           "=" * 96,
           f"{'sigma':>6} {'g':>5} | " + " | ".join(f"k={k:<2} 50%  80%" for k in KS)]
    for s, g in ((0.105, 0.1), (0.105, 0.4), (0.131, 0.1), (0.131, 3.2), (0.5, 0.1), (0.5, 0.4), (0.5, 3.2)):
        cells = [f"{fmt(solve_shared_only(k, s, g, 0.5))} {fmt(solve_shared_only(k, s, g, 0.8))}" for k in KS]
        out.append(f"{s:>6} {g:>5} | " + " | ".join(f"{c:>13}" for c in cells))
    out.append("    ceiling P(S >= 1): " + ", ".join(f"k={k}: {p_share(k)[0]:.4f}" for k in KS))
    return out


def clean_stats(x):
    return {"lrt_free": lrt_mixture(x)[0], "lrt_equal": lrt_mixture(x, equal=True)[0],
            "kurtosis": kurtosis_stat(x), "var_known_sigma": x.var(1) * x.shape[1]}


def clean_job(args):
    """sigma = 1, no background, no rounding, disjoint memberships, labels unknown."""
    k, D, R, seed = args
    rng = np.random.default_rng(seed)
    if D is None:
        x = rng.standard_normal((R, 2 * k))
    else:
        x = np.concatenate([rng.standard_normal((R, k)) - D / 2,
                            rng.standard_normal((R, k)) + D / 2], 1)
    return k, D, clean_stats(x)


def brentq_mix():
    from scipy.optimize import brentq
    f = lambda c: 0.5 * stats.chi2.sf(c, 1) + 0.5 * stats.chi2.sf(c, 2) - ALPHA
    return brentq(f, 0.5, 20)


def fmt(v):
    return "  any" if v == 0 else (f"{v:5.2f}" if np.isfinite(v) else " >max")


def task(args):
    kind, sigma, k, b, g, val, R, seed, disjoint = args
    rng = np.random.default_rng(seed)
    if kind == "null":
        T, tr = simulate(rng, R, k, sigma, 0.0, b, g, null_sigma=val, disjoint=disjoint)
    else:
        T, tr = simulate(rng, R, k, sigma, val, b, g, disjoint=disjoint)
    sp, si, s0, two = statistics(T, b, g)
    return (kind, sigma, k, b, g, val, disjoint), sp, si, s0, two, tr


def main():
    quick = "--quick" in sys.argv
    t0 = time.time()
    lines = []

    def say(s=""):
        print(s, flush=True)
        lines.append(s)

    workers = min(24, os.cpu_count() or 4)
    ss = np.random.SeedSequence(20261025)
    say("bound.py - resolution floor for two coordinated events (see derivation.md)")
    say(f"N = {N_CELLS} cells, frame = {FRAME} s, window = {WINDOW} s, alpha = {ALPHA}, "
        f"seed = SeedSequence(20261025){'  [QUICK MODE]' if quick else ''}")

    # ---------------- 1. clean case
    k_clean = (5, 7, 10, 13, 20, 50, 100, 200)
    dgrid = np.round(np.arange(0, 16.01, 0.5), 3)
    Rn, Ra = (2000, 200) if quick else (10000, 1000)
    jobs = []
    for k in k_clean:
        rn, ra = (Rn, Ra) if k <= 20 else (Rn // 2, Ra // 2)
        jobs += [(k, None, rn // 5, None)] * 5
        jobs += [(k, float(D), ra, None) for D in dgrid]
    seeds = ss.spawn(len(jobs))
    jobs = [j[:3] + (seeds[i],) for i, j in enumerate(jobs)]
    nulls, alts = {}, {}
    with ProcessPoolExecutor(workers, initializer=unthrottle) as ex:
        for k, D, st in ex.map(clean_job, jobs, chunksize=1):
            if D is None:
                for n_, v in st.items():
                    nulls.setdefault(k, {}).setdefault(n_, []).append(v)
            else:
                alts[(k, D)] = st
    names = ("lrt_free", "lrt_equal", "kurtosis", "var_known_sigma")
    say()
    say("=" * 96)
    say("1. CLEAN CASE  (sigma = 1; no background, no rounding, disjoint memberships, labels unknown)")
    say("   resolvable Delta/sigma at 5 % false alarm, from the 2k pooled onsets")
    say("=" * 96)
    say("   classical: an equal two-Gaussian mixture is unimodal iff Delta <= 2 sigma")
    say(f"{'k':>4} {'n=2k':>5} | {'LRT free w':>11} | {'LRT equal w':>11} | {'kurtosis':>11} |"
        f" {'kurt closed':>11} || {'sig. known':>11} | {'s.kn closed':>11}")
    say(f"{'':>11}|  50%   80% |  50%   80% |  50%   80% |  50%   80% ||  50%   80% |  50%   80%")
    clean_rows, clean_curves, clean_crit = {}, {}, {}
    for k in k_clean:
        crit = {n_: float(np.quantile(np.concatenate(nulls[k][n_]), 1 - ALPHA)) for n_ in names}
        clean_crit[k] = crit
        curves = {n_: [float((alts[(k, float(D))][n_] > crit[n_]).mean()) for D in dgrid] for n_ in names}
        clean_curves[k] = curves
        r = {n_: [first_crossing(dgrid, curves[n_], p) for p in POWERS] for n_ in names}
        r["kurt_cf"] = [kurtosis_closed_form(2 * k, p) for p in POWERS]
        r["known_cf"] = [known_sigma_closed_form(2 * k, p) for p in POWERS]
        clean_rows[k] = r
        f = lambda v: " ".join(fmt(x) for x in v)
        say(f"{k:>4} {2 * k:>5} | {f(r['lrt_free'])} | {f(r['lrt_equal'])} | {f(r['kurtosis'])} |"
            f" {f(r['kurt_cf'])} || {f(r['var_known_sigma'])} | {f(r['known_cf'])}")
    say("   'sig. known' = variance test with the jitter known in advance (not the model's null;")
    say("   shown because it is the case the imaging/radar resolution results address)")
    say("   null 95th percentile of 2 log LR, free weights: " +
        ", ".join(f"n={2 * k}: {clean_crit[k]['lrt_free']:.2f}" for k in k_clean))
    say("   equal weights: " + ", ".join(f"n={2 * k}: {clean_crit[k]['lrt_equal']:.2f}" for k in k_clean))
    say(f"   reference: chi2_2 5.99; 50:50 chi2_1:chi2_2 {brentq_mix():.2f}; chi2_3 7.81")
    say("   rate check, Delta_80/sigma * n^(1/8) (constant if Delta ~ n^-1/8): " +
        ", ".join(f"{clean_rows[k]['lrt_free'][1] * (2 * k) ** 0.125:.2f}" for k in k_clean))
    say("   rate check, sigma known, Delta_80/sigma * n^(1/4): " +
        ", ".join(f"{clean_rows[k]['var_known_sigma'][1] * (2 * k) ** 0.25:.2f}" for k in k_clean))
    say("   power at Delta = 2 sigma (the unimodality boundary), LRT free: " +
        ", ".join(f"k={k}: {clean_curves[k]['lrt_free'][list(dgrid).index(2.0)]:.2f}" for k in k_clean))
    say(f"   elapsed {time.time() - t0:.0f} s")

    # ---------------- 2. sharing probability
    say()
    say("=" * 96)
    say("2. P(at least one cell in both events), N = 33, k cells per event")
    say("=" * 96)
    shares = {}
    for k in KS:
        e, a = p_share(k)
        shares[k] = e
        say(f"   k = {k:>2} cells: exact (hypergeometric) {e:.3f}   approx 1-(1-k/N)^k {a:.3f}   "
            f"expected shared cells k^2/N = {k * k / N_CELLS:.2f}")
    for line in closed_form_section():
        say(line)

    # ---------------- 3/4. full model
    R_alt, R_null, n_chunks = (60, 100, 2) if quick else (300, 300, 4)
    g_for = {0.105: (0.1, 0.4), 0.131: (0.1, 3.2), 0.5: GS}   # measured floor per stream
    conds = [(s, k, b, g, False) for s in SIGMAS for k in KS for b in BS for g in g_for[s]]
    if quick:
        conds = [(s, k, b, g, False) for s in (0.131,) for k in (7, 13) for b in (0.0, 0.0096) for g in (0.1, 3.2)]
    chk = (0.131, 7, 0.0096, 0.1, True)     # disjoint memberships: what is left without sharing
    conds_all = conds + [chk]
    jobs = []
    for c in conds_all:
        s, k, b, g, dj = c
        for v in null_grid(s):
            jobs += [("null", s, k, b, g, float(v), R_null, None, dj)] * n_chunks
        for d in delta_grid(s):
            jobs.append(("alt", s, k, b, g, float(d), R_alt, None, dj))
    # longest jobs first for load balance
    seeds = ss.spawn(len(jobs))
    jobs = [j[:7] + (seeds[i], j[8]) for i, j in enumerate(jobs)]
    jobs.sort(key=lambda j: -(j[6] * (1 + 20 * j[3])))
    say()
    say(f"   full model: {len(conds_all)} conditions, {len(jobs)} simulation jobs "
        f"({R_alt} alternatives per Delta, {R_null * n_chunks} nulls per sigma')")
    raw = {}
    trunc_total = 0
    done = 0
    with ProcessPoolExecutor(workers, initializer=unthrottle) as ex:
        for out in ex.map(task, jobs, chunksize=1):
            (kind, s, k, b, g, val, dj), sp, si, s0, two, tr = out
            trunc_total += tr
            raw.setdefault((s, k, b, g, dj), []).append((kind, val, sp, si, s0, two))
            done += 1
            if done % 500 == 0:
                print(f"   {done}/{len(jobs)} jobs, {time.time() - t0:.0f} s", flush=True)
    say(f"   elapsed {time.time() - t0:.0f} s; cells truncated to {MC} onsets: {trunc_total}")
    finish(raw, conds_all, chk, lines, say, clean_rows, clean_curves, dgrid, shares, t0, quick)


def analyse(rows):
    nul = [r for r in rows if r[0] == "null"]
    alt = [r for r in rows if r[0] == "alt"]
    sv = np.array(sorted({r[1] for r in nul}))
    cp, ci = [], []
    for v in sv:
        cp.append(np.quantile(np.concatenate([r[2] for r in nul if r[1] == v]), 1 - ALPHA))
        ci.append(np.quantile(np.concatenate([r[3] for r in nul if r[1] == v]), 1 - ALPHA))
    cp, ci = np.array(cp), np.array(ci)
    lsv = np.log(sv)

    def crit(c, s0):
        # Berger-Boos style: the largest null critical value over the sigma' grid points
        # within a factor CAL_FACTOR of the fitted one-event jitter (nearest always in)
        dist = np.abs(lsv[None, :] - np.log(np.clip(s0, sv[0], sv[-1]))[:, None])
        near = (dist <= math.log(CAL_FACTOR)) | (dist == dist.min(1, keepdims=True))
        return np.where(near, c[None, :], -np.inf).max(1)
    size_p, size_i = [], []
    for v in sv:
        rr = [r for r in nul if r[1] == v]
        sp = np.concatenate([r[2] for r in rr]); si = np.concatenate([r[3] for r in rr])
        s0 = np.concatenate([r[4] for r in rr])
        size_p.append(float((sp > crit(cp, s0)).mean())); size_i.append(float((si > crit(ci, s0)).mean()))
    deltas = np.array(sorted({r[1] for r in alt}))
    pp, pi = [], []
    for d in deltas:
        rr = [r for r in alt if r[1] == d]
        sp = np.concatenate([r[2] for r in rr]); si = np.concatenate([r[3] for r in rr])
        s0 = np.concatenate([r[4] for r in rr])
        pp.append(float((sp > crit(cp, s0)).mean()))
        pi.append(float((si > crit(ci, s0)).mean()))
    res = {"deltas": deltas.tolist(), "power_pooled": pp, "power_identity": pi,
           "size_pooled_max": max(size_p), "size_identity_max": max(size_i),
           "size_pooled": size_p, "size_identity": size_i,
           "crit_pooled": cp.tolist(), "crit_identity": ci.tolist(), "null_sigmas": sv.tolist()}
    for p in POWERS:
        res[f"pooled_{int(p * 100)}"] = first_crossing(deltas, pp, p)
        res[f"identity_{int(p * 100)}"] = first_crossing(deltas, pi, p)
    return res


def finish(raw, conds_all, chk, lines, say, clean_rows, clean_curves, dgrid, shares, t0, quick):
    results = {c: analyse(raw[c]) for c in conds_all}
    say()
    say("=" * 96)
    say("3/4. FULL MODEL: resolvable Delta (s), 5 % false alarm, 50 % / 80 % power")
    say("   pooled   = cell labels discarded (likelihood ratio, bursts on a Poisson background)")
    say("   id g=... = per-cell likelihood ratio, within-cell floor g (0.1 s = one frame = the model")
    say("              as stated; 0.4 s and 3.2 s = measured fast / slow within-cell floors)")
    say("   labelled = oracle that knows each onset's event (t test): the most membership can add")
    say("   'any' = the target power is reached already at Delta = 0 (shared cells alone);")
    say("   '>max' = not reached on the grid.  pooled column uses g = 0.1 s.")
    say("   size = worst realised false-alarm rate over the null sigma' grid (pooled / identity per g);")
    say("   critical value = largest null 95th percentile over sigma' within a factor 2 of the fit")
    say("=" * 96)
    for s in SIGMAS:
        for b in BS:
            if (s, KS[0], b, GS[0], False) not in results and (s, 7, b, GS[0], False) not in results:
                continue
            say(f"-- sigma = {s} s, b = {b} Hz per cell")
            say(f"{'k':>4} | {'pooled':>11} | {'id g=0.1':>11} | {'id g=0.4':>11} | {'id g=3.2':>11} |"
                f" {'labelled':>11} | {'P(share)':>8} | size p/i at g = 0.1, 0.4, 3.2")
            for k in KS:
                rp = results.get((s, k, b, GS[0], False))
                if rp is None:
                    continue
                cells = [f"{fmt(rp['pooled_50'])} {fmt(rp['pooled_80'])}"]
                sizes = []
                for g in GS:
                    r = results.get((s, k, b, g, False))
                    if r is None:
                        cells.append(f"{'-':>11}")
                        continue
                    cells.append(f"{fmt(r['identity_50'])} {fmt(r['identity_80'])}")
                    sizes.append(f"{r['size_pooled_max']:.3f}/{r['size_identity_max']:.3f}")
                lab = " ".join(fmt(labelled_bound(k, s, p)) for p in POWERS)
                say(f"{k:>4} | " + " | ".join(cells) + f" | {lab} | {shares[k]:8.3f} | " + " ".join(sizes))
    r = results[chk]
    rr = results.get(chk[:4] + (False,))
    say()
    say(f"   membership-only check (sigma {chk[0]} s, k {chk[1]} cells, b {chk[2]} Hz, g {chk[3]} s), "
        "memberships forced DISJOINT (no shared cells):")
    say(f"   pooled 50/80 = {fmt(r['pooled_50'])} {fmt(r['pooled_80'])} s; identity 50/80 = "
        f"{fmt(r['identity_50'])} {fmt(r['identity_80'])} s  (size {r['size_pooled_max']:.3f}/{r['size_identity_max']:.3f})")
    if rr is not None:
        say(f"   same condition, random (overlapping) memberships: pooled 50/80 = {fmt(rr['pooled_50'])} "
            f"{fmt(rr['pooled_80'])} s; identity 50/80 = {fmt(rr['identity_50'])} {fmt(rr['identity_80'])} s")
    say()
    say("   pooled power at Delta = 1, 2, 3 s (b = 0.0096 Hz, g = 0.1 s):")
    for s in SIGMAS:
        for k in KS:
            r = results.get((s, k, 0.0096, 0.1, False))
            if r is None:
                continue
            d = np.array(r["deltas"])
            pw = [np.interp(x, d, np.maximum.accumulate(r["power_pooled"])) for x in (1.0, 2.0, 3.0)]
            say(f"     sigma {s} s, k {k:>2} cells: " + ", ".join(f"{p:.2f}" for p in pw))
    say(f"   total elapsed {time.time() - t0:.0f} s")

    suffix = "_quick" if quick else ""
    with open(os.path.join(HERE, f"bound_output{suffix}.txt"), "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines) + "\n")
    js = {"clean": {str(k): v for k, v in clean_rows.items()},
          "clean_curves": {str(k): v for k, v in clean_curves.items()}, "clean_grid": dgrid.tolist(),
          "full": {f"{c[0]}|{c[1]}|{c[2]}|{c[3]}|{int(c[4])}": v for c, v in results.items()}}
    with open(os.path.join(HERE, f"bound_results{suffix}.json"), "w") as fh:
        json.dump(js, fh, indent=1, default=float)
    if not quick:
        make_figure(results)


def make_figure(results):
    """Figure 1.6 (goal page Figure 6). Sized for a ~922 px page column: 12 in wide, smallest text
    10.5 pt (about 11 px rendered). A-C share y; reference lines are labeled outside the plot
    area (right of C, and '2σ' in the gap after each panel) so no data crosses a label."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import matplotlib.ticker
    from matplotlib.lines import Line2D
    plt.rcParams.update({"font.size": 12})
    C = {"pooled": "#2a78d6", "id01": "#eb6834", "idg": "#1baf7a", "lab": "#555555"}
    floors = {0.105: (0.4, "fast"), 0.131: (3.2, "slow"), 0.5: (0.4, "fast")}
    b = 0.0096
    YFLOOR = 0.03          # bottom of the A-C y axis
    ANY_Y = 0.036          # where a 'resolves at every separation tested' point is drawn
    SIZE_MAX = 0.075       # test size above this is flagged † (derivation.md, Table 2)
    fig = plt.figure(figsize=(12, 9.6))
    w, gap, top_b, top_h = 0.205, 0.04, 0.585, 0.37
    axs = [fig.add_axes((0.075 + i * (w + gap), top_b, w, top_h)) for i in range(3)]
    axs.append(fig.add_axes((0.075, 0.075, 0.36, 0.36)))
    ks = np.array(KS)
    for ax, s, letter in zip(axs[:3], SIGMAS, "ABC"):
        g, gname = floors[s]

        def series(key, g_):
            return [results[(s, k, b, g_, False)][key] for k in KS]

        def size_flags(sizekey, g_):
            return [results[(s, k, b, g_, False)][sizekey] > SIZE_MAX for k in KS]

        daggers = {}     # k -> [(color, y of the 80 % point)] for size-inflated entries

        def plotpair(v50, v80, color, marker, flags, dodge=0.0):
            any80 = np.array(v80, float) == 0
            for v, lw, ls, ms, mfc, z, skip in ((v80, 2, "-", 7, color, 3, None),
                                                (v50, 1.2, "--", 5.5, "white", 2, any80)):
                v = np.array(v, float)
                pos = np.where(np.isfinite(v) & (v > 0), v, np.nan)
                ax.plot(ks, pos, color=color, marker=marker, lw=lw, ls=ls, ms=ms, mfc=mfc, zorder=z)
                # 'any': reached already at Δ = 0. A filled glyph (80 %) implies 50 % too, so the
                # open one is drawn only where 80 % is not 'any'; series are dodged sideways.
                isany = (v == 0) if skip is None else ((v == 0) & ~skip)
                anyk = ks[isany]
                if len(anyk):
                    ax.plot(anyk + dodge, [ANY_Y] * len(anyk), "v", color=color, ms=ms + 1,
                            mfc=mfc, mew=1.3, ls="none", zorder=z, clip_on=False)
            v80 = np.array(v80, float)
            for kk, f, y in zip(ks, flags, v80):
                if f:
                    daggers.setdefault(kk, []).append(
                        (color, y if (np.isfinite(y) and y > 0) else ANY_Y))

        plotpair(series("pooled_50", 0.1), series("pooled_80", 0.1), C["pooled"], "o",
                 size_flags("size_pooled_max", 0.1))
        plotpair(series("identity_50", 0.1), series("identity_80", 0.1), C["id01"], "s",
                 size_flags("size_identity_max", 0.1), dodge=-0.4)
        plotpair(series("identity_50", g), series("identity_80", g), C["idg"], "^",
                 size_flags("size_identity_max", g), dodge=0.4)
        plotpair([labelled_bound(k, s, 0.5) for k in KS], [labelled_bound(k, s, 0.8) for k in KS],
                 C["lab"], "D", [False] * len(KS))
        # one row of daggers per k, above the highest flagged point, each in its series' color
        for kk, lst in daggers.items():
            ytop = max(y for _, y in lst)
            for n_, (colr, _) in enumerate(lst):
                ax.annotate("†", (kk, ytop), textcoords="offset points",
                            xytext=(-3 * (len(lst) - 1) + 7 * n_, 6), fontsize=12, color=colr,
                            fontweight="bold", ha="center", va="bottom")
        for y, ls in ((7.1, ":"), (3.8, ":"), (2.5, "-"), (0.1, "-.")):
            ax.axhline(y, color="#9a9a9a", lw=1, ls=ls, zorder=0)
        ax.axhline(2 * s, color="#9a9a9a", lw=1.2, ls=(0, (6, 2, 1, 2)), zorder=0)
        ax.text(1.015, 2 * s, "2σ", transform=ax.get_yaxis_transform(), fontsize=10.5,
                va="center", ha="left", color="#444444")
        ax.set_yscale("log")
        ax.set_ylim(YFLOOR, 12)
        ax.set_xlim(4, 21)
        ax.set_xticks(KS)
        ax.set_xlabel("cells per event, k\n(of 33 cells)", fontsize=11)
        if letter == "A":
            ax.set_ylabel("resolvable separation Δ (s)")
            ax.yaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda v, _: f"{v:g}"))
        else:
            ax.tick_params(labelleft=False)
        ax.set_title(f"jitter SD σ = {s} s\n2σ = {2 * s:.2f} s", fontsize=11, loc="right")
        ax.text(-0.04, 1.02, letter, transform=ax.transAxes, fontsize=14, fontweight="bold",
                ha="right", va="bottom")
        ax.grid(True, which="major", color="#eeeeee", lw=0.6)
    # shared reference-line labels, outside to the right of panel C (7.1 and 3.8 nudged apart)
    ax = axs[2]
    for y, ty, lab in ((7.1, 8.6, "slow-stream gap,\n5th percentile 7.1 s"),
                       (3.8, 4.4, "fast-stream gap,\n5th percentile 3.8 s"),
                       (2.5, 2.05, "assessor: half its split\nplateau at 2.5 s"),
                       (0.1, 0.1, "frame 0.1 s")):
        ax.annotate(lab, xy=(1.0, y), xycoords=ax.get_yaxis_transform(),
                    xytext=(1.13, ty), textcoords=ax.get_yaxis_transform(), fontsize=10.5,
                    va="center", ha="left", color="#444444", linespacing=1.0,
                    arrowprops=dict(arrowstyle="-", color="#bbbbbb", lw=0.8))

    ax = axs[3]
    for (s, k, g, ls) in ((0.105, 7, 0.4, "-"), (0.131, 13, 3.2, "--")):
        r = results[(s, k, b, g, False)]
        d = np.array(r["deltas"])
        ax.plot(d, np.maximum.accumulate(r["power_pooled"]), color=C["pooled"], ls=ls, lw=2)
        ax.plot(d, np.maximum.accumulate(r["power_identity"]), color=C["idg"], ls=ls, lw=2)
    for y, t in ((0.05, "5 % false alarm"), (0.5, "50 % power"), (0.8, "80 % power")):
        ax.axhline(y, color="#9a9a9a", lw=1, ls=":", zorder=0)
        ax.text(1.47, y + 0.015, t, fontsize=10.5, ha="right", color="#444444")
    ax.set_xlim(0, 1.5)
    ax.set_ylim(0, 1.02)
    ax.set_xlabel("separation between event centers, Δ (s)", fontsize=11)
    ax.set_ylabel("power (fraction of\n300 pairs called two)", fontsize=11)
    ax.text(-0.04, 1.02, "D", transform=ax.transAxes, fontsize=14, fontweight="bold",
            ha="right", va="bottom")
    ax.grid(True, color="#eeeeee", lw=0.6)

    h = [Line2D([], [], color=C["pooled"], marker="o", lw=2, label="no cell identity"),
         Line2D([], [], color=C["id01"], marker="s", lw=2,
                label="cell identity, within-cell minimum interval\n0.1 s (model as stated)"),
         Line2D([], [], color=C["idg"], marker="^", lw=2,
                label="cell identity, measured within-cell minimum\ninterval (0.4 s fast, 3.2 s slow; 0.4 s in C)"),
         Line2D([], [], color=C["lab"], marker="D", lw=2, label="membership known (oracle t test)"),
         Line2D([], [], color="0.3", marker="o", lw=2, label="solid, filled: 80 % power"),
         Line2D([], [], color="0.3", marker="o", lw=1.2, ls="--", mfc="white", label="dashed, open: 50 % power"),
         Line2D([], [], color="0.3", marker="v", ls="none", ms=8,
                label="resolves at every separation tested\n(shared cells alone), drawn at the axis floor"),
         Line2D([], [], color="none", marker="$†$", ms=10, mec="0.3", mfc="0.3", ls="none",
                label="test size above 7.5 % (mostly σ = 0.5 s, few cells):\nanti-conservative, value optimistic"),
         Line2D([], [], color="0.3", lw=2, ls="-", label="D: fast stream (σ 0.105 s, 7 cells,\nminimum interval 0.4 s)"),
         Line2D([], [], color="0.3", lw=2, ls="--", label="D: slow stream (σ 0.131 s, 13 cells,\nminimum interval 3.2 s)")]
    fig.legend(handles=h, loc="upper left", fontsize=10.5, frameon=False,
               bbox_to_anchor=(0.475, 0.47), labelspacing=0.55)
    fig.savefig(os.path.join(HERE, "synth_recovery_plot_separation-floor-any-method_20261025.png"), dpi=150,
                metadata={"Title": "Figure 6, the separation any method can resolve (Aim 0)",
                          "Author": "bugarach synthetic validation (docs/learned/synthetic_validation)",
                          "Creation Time": __import__("datetime").datetime.now().isoformat(timespec="seconds")})


def figure_from_json():
    with open(os.path.join(HERE, "bound_results.json")) as fh:
        js = json.load(fh)
    results = {}
    for key, v in js["full"].items():
        s, k, b, g, dj = key.split("|")
        results[(float(s), int(k), float(b), float(g), bool(int(dj)))] = v
    make_figure(results)


if __name__ == "__main__":
    if "--figure" in sys.argv:      # redraw synth_recovery_plot_separation-floor-any-method_20261025.png from bound_results.json, no simulation
        figure_from_json()
    else:
        main()
