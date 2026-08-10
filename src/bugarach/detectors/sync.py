"""SPIKE-synchronization detector — port of interface2's sync stack:
cSPIKE ``AdaptiveSPIKESynchroProfile`` -> ``max/mean_synchrony`` binning ->
``SpikyDetect3`` hysteresis detection -> ``flagArtifactEvents``.

The tau-capped adaptive SPIKE-synchronization profile (Kreuz lab) assigns
each spike a coincidence value C in [0,1]: the fraction of other trains with
a spike within the adaptive coincidence window tau = min of the four
half-ISIs surrounding the spike pair, capped at tau_max (dense firing cannot
inflate C — the fixed-profile promiscuity fix). The implementation follows
PySpike's ``get_tau``/coincidence semantics per pair (strict ``<``; exact
cross-train ties always coincide; missing edge ISIs default to the cap) but
keeps one profile entry PER SPIKE like cSPIKE, rather than PySpike's
merged-sample DiscreteFunc — the ``max`` binning statistic can tell merged
same-time spikes apart, the merged form cannot. Cross-validated against BOTH:
PySpike's multivariate profile (summed-coincidence identity, unit test) and
cSPIKE reference output from MATLAB (tests/fixtures/ref_sync_synth.json and
a real slice, to 1e-9).

Detection (SpikyDetect3): bin the profile at dt (bin value = mean or max of
the per-spike C values at each event time — later event times in a bin
overwrite earlier ones, faithfully ported); threshold mode is a hysteresis
scan (C_threshold starts an event, C_min sustains it across gaps < max_gap,
zero bins skipped) with a min_n total-event floor; peak mode gates the
binned trace through the shared peak-gate kernel. Deterministic — no RNG.
"""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np

from bugarach.detectors._shared import clip_sorted, matlab_colon, matlab_round
from bugarach.detectors.peaks import peak_gate
from bugarach.detectors.rate import DetectorSignal


@dataclass
class SyncDetection:
    """Detected synchrony events + profile/binned traces for one stream."""

    locs: np.ndarray                # event begin times (s)
    ends: np.ndarray                # event end times (s)
    widths: np.ndarray
    amps: np.ndarray                # mean binned C over the event (threshold)
                                    # / peak C (peak mode)
    peak_C: np.ndarray              # artifact fields (flagArtifactEvents)
    plat90: np.ndarray
    n_participating_rois: np.ndarray
    n_total_rois: int
    is_artifact: np.ndarray
    profile_x: np.ndarray           # per-spike times (pooled, ascending)
    profile_y: np.ndarray           # per-spike C values in [0,1]
    Cx: np.ndarray                  # bin centres (dt grid)
    Cy: np.ndarray                  # binned synchrony
    Cn: np.ndarray                  # events per bin (as binned — see port note)
    signal: DetectorSignal | None = None
    settings: dict = field(default_factory=dict)

    @property
    def n_events(self) -> int:
        return self.locs.size


def adaptive_profile(
    trains: list[np.ndarray], t_range: tuple[float, float], tau_max: float
) -> tuple[np.ndarray, np.ndarray]:
    """Per-spike tau-capped SPIKE-synchronization profile (x, C), pooled over
    all trains and sorted ascending in time. C = coincident-pair count /
    (n_trains - 1)."""
    # cSPIKE's SpikeTrainSet drops duplicate spike times WITHIN a train
    ev = [np.unique(v) for v in clip_sorted(trains, t_range[0], t_range[1])]
    n = len(ev)
    span = t_range[1] - t_range[0]
    true_max = min(span, 2.0 * tau_max) if tau_max > 0 else span
    cap_half = true_max / 2.0

    counts = [np.zeros(v.size) for v in ev]
    for i in range(n):
        a = ev[i]
        if a.size == 0:
            continue
        # half-ISIs around each spike of a (edge neighbors default to the cap)
        a_prev = np.full(a.size, cap_half)
        a_next = np.full(a.size, cap_half)
        if a.size > 1:
            d = np.diff(a) / 2.0
            a_prev[1:] = d
            a_next[:-1] = d
        for j in range(i + 1, n):
            b = ev[j]
            if b.size == 0:
                continue
            b_prev = np.full(b.size, cap_half)
            b_next = np.full(b.size, cap_half)
            if b.size > 1:
                d = np.diff(b) / 2.0
                b_prev[1:] = d
                b_next[:-1] = d
            ca, cb = _pair_coincidence(a, a_prev, a_next, b, b_prev, b_next,
                                       cap_half)
            counts[i] += ca
            counts[j] += cb

    x = np.concatenate([v for v in ev]) if n else np.empty(0)
    denom = max(n - 1, 1)
    y = np.concatenate([c / denom for c in counts]) if n else np.empty(0)
    order = np.argsort(x, kind="stable")
    return x[order], y[order]


def _pair_coincidence(a, a_prev, a_next, b, b_prev, b_next, cap_half):
    """Coincidence indicators for each spike of a and b against the other
    train: nearest neighbor within tau = min of the four half-ISIs (each
    capped); exact ties always coincide (PySpike sweep semantics)."""
    ca = np.zeros(a.size)
    cb = np.zeros(b.size)
    for (s, s_prev, s_next, o, o_prev, o_next, cs) in (
        (a, a_prev, a_next, b, b_prev, b_next, ca),
        (b, b_prev, b_next, a, a_prev, a_next, cb),
    ):
        idx = np.searchsorted(o, s)                 # first o >= s
        for k in range(s.size):
            jn = idx[k]
            if jn < o.size and o[jn] == s[k]:       # exact tie -> coincident
                cs[k] = 1.0
                continue
            hit = False
            if jn < o.size:                         # next neighbor
                tau = min(min(s_prev[k], s_next[k]),
                          min(o_prev[jn], o_next[jn]), cap_half)
                hit = (o[jn] - s[k]) < tau
            if not hit and jn > 0:                  # previous neighbor
                jp = jn - 1
                tau = min(min(s_prev[k], s_next[k]),
                          min(o_prev[jp], o_next[jp]), cap_half)
                hit = (s[k] - o[jp]) < tau
            cs[k] = 1.0 if hit else 0.0
    return ca, cb


def binned_synchrony(
    x: np.ndarray, y: np.ndarray, dt: float,
    t_range: tuple[float, float], statistic: str = "max",
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """max/mean_synchrony port: (Cx, Cy, Cn) on the tmin:dt:tmax grid.

    Faithful to the MATLAB binning: events at the SAME time aggregate by
    max/mean; each event time writes to the FIRST bin centre within dt of it,
    OVERWRITING whatever an earlier event time put there; Cn is the same-time
    group size of the last writer, not the bin's event total."""
    t = matlab_colon(t_range[0], dt, t_range[1])
    cy = np.zeros(t.size)
    cn = np.zeros(t.size)
    if x.size:
        # groups of identical event times, ascending
        starts = np.concatenate(([0], np.flatnonzero(np.diff(x) != 0) + 1))
        ends = np.concatenate((starts[1:], [x.size]))
        for s, e in zip(starts, ends):
            val = y[s:e].max() if statistic == "max" else y[s:e].mean()
            xi = x[s]
            i0 = max(0, int(np.floor((xi - t_range[0]) / dt)) - 2)
            idx = None
            for i in range(i0, min(t.size, i0 + 5)):
                if abs(t[i] - xi) < dt:
                    idx = i
                    break
            if idx is not None:
                cy[idx] = val
                cn[idx] = e - s
    return t, cy, cn


def sync_detect(
    trains: list[np.ndarray],
    t_range: tuple[float, float],
    *,
    tau_max: float,
    max_gap: float,
    C_threshold: float = 0.1,
    C_min: float = 0.1,
    min_n: int = 3,
    dt: float = 0.1,
    synchrony_statistic: str = "mean",
    detection_mode: str = "threshold",
    peak_prominence: float = 0.0,
    peak_min_distance_sec: float = 0.0,
    artifact_threshold: float = 0.85,
    artifact_threshold_fraction: float = 0.70,
    artifact_threshold_plat90: float = 0.8,
) -> SyncDetection:
    """Detect synchrony events on the tau-capped SPIKE-synchronization
    profile (viewer defaults: tau FAST 0.25 / SLOW 0.5, max_gap 0.5 / 2,
    C_threshold = C_min = 0.1, min_n 3, statistic "mean")."""
    if detection_mode not in ("threshold", "peak"):
        raise ValueError('detection_mode must be "threshold" or "peak"')
    if synchrony_statistic not in ("max", "mean"):
        raise ValueError('synchrony_statistic must be "max" or "mean"')

    ev = clip_sorted(trains, t_range[0], t_range[1])
    px, py = adaptive_profile(trains, t_range, tau_max)
    cx, cy, cn = binned_synchrony(px, py, dt, t_range, synchrony_statistic)
    n2 = cy.size

    if detection_mode == "peak":
        d_bins = max(1, matlab_round(peak_min_distance_sec / dt))
        pk = peak_gate(cy, C_threshold, prominence=peak_prominence,
                       min_distance=d_bins, floor=-np.inf, strict_above=True)
        begins, ends_, amps = [], [], []
        for i in range(pk.idx.size):
            b0 = max(0, int(np.floor(pk.left_x[i])))
            b1 = min(n2 - 1, int(np.ceil(pk.right_x[i])))
            if cn[b0:b1 + 1].sum() >= min_n:
                tb = cx[0] + pk.left_x[i] * dt
                te = cx[0] + pk.right_x[i] * dt
                if tb == te:
                    te += dt
                begins.append(tb)
                ends_.append(te)
                amps.append(pk.val[i])
        begins, ends_, amps = map(np.array, (begins, ends_, amps))
    else:
        # SpikyDetect3 hysteresis scan, ported with its exact control flow
        # (including the stale-gap re-checks and skipped-bin quirks)
        begins_l, ends_l, amps_l = [], [], []
        i = -1
        while i < n2 - 1:
            i += 1
            if cy[i] > C_threshold:
                cmean = cy[i]
                ncmean = 1
                ev_begin = cx[i]
                ev_end = ev_begin
                ev_sum = cn[i]
                j = i + 1
                gap = cx[j] - cx[i] if j < n2 else np.inf
                while j < n2 - 1 and gap < max_gap:
                    while j < n2 - 2 and cy[j] == 0 and gap < max_gap:
                        j += 1                       # advance through zeros
                        gap = cx[j] - cx[i]
                    if gap <= max_gap and cy[j] > C_min:
                        cmean += cy[j]
                        ncmean += 1
                        ev_sum += cn[j]
                        ev_end = cx[j]
                        i = j
                        j += 1
                    else:
                        i = j
                        break
                if ev_begin == ev_end:
                    ev_end = ev_end + dt
                if ev_sum >= min_n:
                    begins_l.append(ev_begin)
                    ends_l.append(ev_end)
                    amps_l.append(cmean / ncmean)
        begins = np.array(begins_l)
        ends_ = np.array(ends_l)
        amps = np.array(amps_l)

    peak_c, plat90, n_part, is_art = _flag_artifacts(
        begins, ends_, amps, cy, cx, ev,
        artifact_threshold, artifact_threshold_fraction,
        artifact_threshold_plat90)

    settings = {
        "tau_max": tau_max, "max_gap": max_gap, "dt": dt,
        "C_threshold": C_threshold, "C_min": C_min, "min_n": min_n,
        "synchrony_statistic": synchrony_statistic,
        "detection_mode": detection_mode,
        "peak_prominence": peak_prominence,
        "peak_min_distance_sec": peak_min_distance_sec,
    }
    return SyncDetection(
        locs=begins, ends=ends_, widths=ends_ - begins, amps=amps,
        peak_C=peak_c, plat90=plat90, n_participating_rois=n_part,
        n_total_rois=len(trains), is_artifact=is_art,
        profile_x=px, profile_y=py, Cx=cx, Cy=cy, Cn=cn,
        signal=DetectorSignal(t=cx, y=cy, ref=np.full(n2, np.nan),
                              threshold=C_threshold, hilite=np.empty((0, 2)),
                              name="SPIKE-synch C (adaptive)",
                              kind="spike_sync"),
        settings=settings,
    )


def _flag_artifacts(begins, ends, amps, cy, cx, ev, athr, afthr, aplat90):
    """flagArtifactEvents port: peak_C / plat90 / participating-ROI fraction,
    compound AND artifact criterion (narrow near-total C spikes)."""
    n = begins.size
    n_total = len(ev)
    peak_c = np.zeros(n)
    plat90 = np.zeros(n)
    n_part = np.zeros(n)
    for ie in range(n):
        t0, t1 = begins[ie], ends[ie]
        mask = (cx >= t0) & (cx <= t1)
        if mask.any():
            bx = cx[mask]
            by = cy[mask]
            pk = by.max()
            peak_c[ie] = pk
            if bx.size >= 2:
                d = bx[1] - bx[0]
            elif cx.size >= 2:
                d = cx[1] - cx[0]
            else:
                d = 0.1
            above = bx[by >= 0.9 * pk]
            plat90[ie] = (above[-1] - above[0] + d) if above.size >= 2 else d
        elif not np.isnan(amps[ie]):
            peak_c[ie] = amps[ie]
            plat90[ie] = (cx[1] - cx[0]) if cx.size >= 2 else 0.1
        n_part[ie] = sum(
            1 for v in ev if v.size and ((v >= t0) & (v <= t1)).any())
    frac = n_part / max(n_total, 1)
    is_art = (peak_c >= athr) & (frac >= afthr) & (plat90 <= aplat90)
    return peak_c, plat90, n_part, is_art
