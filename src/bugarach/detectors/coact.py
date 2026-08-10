"""CoactDetect — port of interface2's ``detect_local_coincidence`` (detector #5
prototype): distinct-ROI coincidence tested against a rate-LOCAL null.

Statistic: per int_win bin, the number of DISTINCT ROIs with >= 1 event (each
ROI capped at 1, so a lone bursty ROI cannot drive it).

Null: for each candidate bin (obs >= min_rois), circular-shift each ROI's
events WITHIN a rolling context window centred on the bin, recount. This
preserves each ROI's local rate/ISI structure and randomises only cross-ROI
phase, so a window that is dense-but-unsynchronised (e.g. drug onset) gets a
null matched to the local density and is not flagged.

Significance is a one-sided Gaussian-tail p from the null's mean/sd
(p = 0.5*erfc(z/sqrt(2))), continuous so alpha can go below 1/(N+1).

Parity: the surrogate stream reproduces MATLAB exactly — MATLAB's default
``rng(seed)`` twister and numpy's ``RandomState(seed)`` generate identical
doubles, and draws are consumed in the same order (candidate bins ascending,
surrogate-major / ROI-minor within a bin). Verified against MATLAB reference
output in tests/fixtures/ref_coact_synth.json and on a real slice.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from math import erfc, sqrt

import numpy as np

from bugarach.detectors.peaks import peak_gate
from bugarach.detectors.rate import DetectorSignal


@dataclass
class CoactDetection:
    """Detected episodes + per-bin profiles (mirrors detect_local_coincidence's
    ``out``). Event fields are parallel arrays of length n_events; width_kind
    is "episode_span" (threshold mode) or "half_prominence" (peak mode)."""

    onset_sec: np.ndarray
    width_sec: np.ndarray
    strength: np.ndarray            # = z
    nrois: np.ndarray               # peak/episode-max distinct-ROI coactivity
    z: np.ndarray
    p: np.ndarray
    peak_sec: np.ndarray            # NaN in threshold mode
    t50rise: np.ndarray             # NaN in threshold mode
    t50fall: np.ndarray             # NaN in threshold mode
    width_kind: str
    ctr: np.ndarray                 # bin centres (s)
    obs: np.ndarray                 # distinct-ROI coactivity per bin
    z_prof: np.ndarray              # NaN except candidate bins
    pval_prof: np.ndarray
    nullmean_prof: np.ndarray
    signal: DetectorSignal
    ext: tuple[float, float] = (0.0, 0.0)
    opts: dict = field(default_factory=dict)

    @property
    def n_events(self) -> int:
        return self.onset_sec.size


def coact_detect(
    trains: list[np.ndarray],
    t_range: tuple[float, float],
    *,
    int_win_sec: float = 0.5,
    context_win_sec: float = 60.0,
    min_rois: int = 3,
    n_surrogates: int = 200,
    alpha: float = 0.01,
    merge_gap_sec: float = 3.0,
    rng_seed: int = 20260706,
    detection_mode: str = "threshold",
    peak_prominence: float = 0.0,
    peak_min_distance_sec: float = 0.0,
) -> CoactDetection:
    """Distinct-ROI coincidence vs a rolling rate-local circular-shift null.

    trains are per-ROI onset times (explore_sce feeds raw t50rise cells; they
    are clipped to t_range here). Defaults mirror the MATLAB function; the
    explore_sce viewer uses per-stream values (FAST: 2 s bins / 60 s context /
    alpha 1e-4; SLOW: 1 s / 120 s / 1e-6; n_surrogates 100).
    """
    if detection_mode not in ("threshold", "peak"):
        raise ValueError('detection_mode must be "threshold" or "peak"')
    rng = np.random.RandomState(rng_seed)
    t0, t1 = t_range
    bw = int_win_sec
    C = context_win_sec

    ev = []
    for v in trains:
        v = np.asarray(v, dtype=float).ravel()
        v = v[np.isfinite(v)]
        ev.append(np.sort(v[(v >= t0) & (v <= t1)]))

    nb = max(1, int(np.ceil((t1 - t0) / bw)))
    edges = t0 + np.arange(nb + 1) * bw
    ctr = t0 + (np.arange(1, nb + 1) - 0.5) * bw

    obs = np.zeros(nb)
    for e in ev:
        if e.size == 0:
            continue
        bi = np.clip(np.floor((e - t0) / bw).astype(int), 0, nb - 1)
        obs[np.unique(bi)] += 1  # distinct-ROI: 1 per ROI per bin

    cand = np.flatnonzero(obs >= min_rois)
    z = np.full(nb, np.nan)
    pval = np.full(nb, np.nan)
    nullmean = np.full(nb, np.nan)
    n_sur = int(n_surrogates)

    for b in cand:
        blo, bhi = edges[b], edges[b + 1]
        c_lo = max(t0, ctr[b] - C / 2)
        c_hi = min(t1, ctr[b] + C / 2)
        cw = c_hi - c_lo
        tlo, thi = blo - c_lo, bhi - c_lo
        ctx = []
        for e in ev:
            if e.size == 0:
                continue
            vv = e[(e >= c_lo) & (e <= c_hi)]
            if vv.size:
                ctx.append(vv - c_lo)
        # one uniform draw per (surrogate, context-ROI), surrogate-major order —
        # identical stream consumption to the MATLAB scalar-rand loops
        draws = rng.random_sample((n_sur, len(ctx)))
        counts = np.zeros(n_sur)
        for j, e in enumerate(ctx):
            shifted = np.mod(e[None, :] + draws[:, j:j + 1] * cw, cw)
            counts += ((shifted >= tlo) & (shifted < thi)).any(axis=1)
        mu = counts.mean()
        sd = counts.std(ddof=1)
        nullmean[b] = mu
        if sd > 0:
            z[b] = (obs[b] - mu) / sd
            pval[b] = 0.5 * erfc(z[b] / sqrt(2))
        elif obs[b] > mu:
            z[b], pval[b] = np.inf, 0.0
        else:
            z[b], pval[b] = 0.0, 1.0

    with np.errstate(invalid="ignore"):
        is_sig = (obs >= min_rois) & (pval <= alpha)  # NaN pval -> not significant

    if detection_mode == "peak":
        # peak-gate obs, admitting only peaks at significant bins: the
        # per-bin threshold (-Inf where significant, +Inf elsewhere) IS the
        # significance mask, and min-distance thins among significant peaks
        thrv = np.where(is_sig, -np.inf, np.inf)
        d_bins = max(1, int(np.floor(peak_min_distance_sec / bw + 0.5)))
        pk = peak_gate(obs, thrv, prominence=peak_prominence,
                       min_distance=d_bins, floor=min_rois, strict_above=True)
        onset = ctr[0] + pk.left_x * bw           # left half-prom edge, bin-centre space
        width = (pk.right_x - pk.left_x) * bw
        ev_nrois = obs[pk.idx]
        ev_z = z[pk.idx]
        ev_p = pval[pk.idx]
        peak_sec = ctr[0] + pk.idx * bw
        t50rise = onset.copy()
        t50fall = onset + width
        width_kind = "half_prominence"
    else:
        sig = cand[is_sig[cand]]
        starts_b, ends_b = [], []
        if sig.size:
            s_cur = prev = sig[0]
            for b in sig[1:]:
                if edges[b] - edges[prev + 1] <= merge_gap_sec:
                    prev = b
                else:
                    starts_b.append(s_cur)
                    ends_b.append(prev)
                    s_cur = prev = b
            starts_b.append(s_cur)
            ends_b.append(prev)
        n = len(starts_b)
        onset = np.array([edges[s] for s in starts_b])
        width = np.array([edges[e + 1] - edges[s] for s, e in zip(starts_b, ends_b)])
        ev_nrois = np.array([obs[s:e + 1].max() for s, e in zip(starts_b, ends_b)])
        # merged episodes span non-candidate bins whose z/p are NaN; MATLAB's
        # max/min ignore NaN, so aggregate with the nan-variants
        ev_z = np.array([np.nanmax(z[s:e + 1]) for s, e in zip(starts_b, ends_b)])
        ev_p = np.array([np.nanmin(pval[s:e + 1]) for s, e in zip(starts_b, ends_b)])
        peak_sec = np.full(n, np.nan)
        t50rise = np.full(n, np.nan)
        t50fall = np.full(n, np.nan)
        width_kind = "episode_span"

    opts = {
        "int_win_sec": int_win_sec, "context_win_sec": context_win_sec,
        "min_rois": min_rois, "n_surrogates": n_surrogates, "alpha": alpha,
        "merge_gap_sec": merge_gap_sec, "rng_seed": rng_seed,
        "detection_mode": detection_mode, "peak_prominence": peak_prominence,
        "peak_min_distance_sec": peak_min_distance_sec,
    }
    return CoactDetection(
        onset_sec=onset, width_sec=width, strength=ev_z.copy(), nrois=ev_nrois,
        z=ev_z, p=ev_p, peak_sec=peak_sec, t50rise=t50rise, t50fall=t50fall,
        width_kind=width_kind,
        ctr=ctr, obs=obs, z_prof=z, pval_prof=pval, nullmean_prof=nullmean,
        signal=DetectorSignal(t=ctr, y=obs, ref=nullmean, threshold=None,
                              hilite=np.empty((0, 2)),
                              name="coact / local null", kind="local_coincidence"),
        ext=t_range, opts=opts,
    )
