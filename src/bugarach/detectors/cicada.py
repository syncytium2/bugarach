"""CICADA sliding-window SCE detector — port of interface2's
``generate_sce_cicada``, itself a faithful port of the Cossart lab's CICADA
(``cossartlab/cicada`` sce_stats_utils: get_sce_threshold + detect_sce; MIT
license — see the repo README's Licensing & citations section).

1. Binary raster at imaging-frame resolution from the store's event times;
   each event marks its cell active for the transient DURATION (fixed scalar,
   or per-event durations the CALLER precomputed — e.g. rise interval =
   peak locs - t50rise; CICADA rasterizes what it is given).
2. Coactivity trace: distinct cells active within a sliding window of
   n_synchronous_frames consecutive frames.
3. Threshold: circular-shift each cell independently, sum active cells PER
   FRAME, pool across surrogates, take sce_percentile — an ABSOLUTE
   cell-count threshold (CICADA's exact rule: the null uses the single-frame
   sum even though detection uses the windowed sum).
4. SCEs = local maxima of the coactivity trace >= threshold, greedily thinned
   to >= sce_min_distance_frames apart (scipy find_peaks equivalent; NOT the
   shared half-prominence peak-gate — CICADA is natively peak-picking).

threshold_scope="global" (default) builds one threshold for the whole
recording; "regional" builds a per-region null and detects within each
trimmed window.

Parity: MATLAB ``randi(k)`` consumes one double and equals
``floor(rand*k)+1`` on the shared twister stream (verified empirically), so
the per-cell roll offsets reproduce exactly. Verified to 1e-9 against MATLAB
reference output (tests/fixtures/ref_cicada_synth.json) and on a real slice.
"""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np

from bugarach.detectors._shared import matlab_prctile, matlab_round
from bugarach.detectors.loco import (
    RegionWindow,
    effective_region_windows,
    per_stream_param,
)
from bugarach.detectors.rate import recording_extent
from bugarach.detectors.sce import SceSignal
from bugarach.store import Slice, Stream


@dataclass
class CicadaStream:
    """Column-aligned detected SCEs for one stream (event-list schema)."""

    onset_sec: np.ndarray       # peak window start, absolute seconds
    magnitude: np.ndarray       # distinct cells in the n_synchronous window
    mag_total: np.ndarray       # distinct cells in the +-1-frame member window
    width_sec: np.ndarray       # member-onset span, floored at the window duration
    threshold: np.ndarray       # cell-count threshold used (per event)
    region: list[str]
    in_stats_window: np.ndarray
    meets_floor: np.ndarray
    signal: SceSignal | None = None   # kind "cicada_coactivity"

    @property
    def n_events(self) -> int:
        return self.onset_sec.size


@dataclass
class CicadaDetection:
    slice_id: str
    streams: dict[str, CicadaStream]   # name -> result, in slice stream order
    regions: list[RegionWindow]
    ext: tuple[float, float]
    params: dict = field(default_factory=dict)

    @property
    def fast(self) -> CicadaStream:
        return self.streams["fast"]

    @property
    def slow(self) -> CicadaStream:
        return self.streams["slow"]


def rise_durations(stream: Stream) -> list[np.ndarray]:
    """Per-ROI rise intervals (peak locs - t50rise onset), the per_event
    duration explore_sce feeds CICADA to tame long SLOW transients."""
    return [np.asarray(pk, dtype=float) - np.asarray(on, dtype=float)
            for pk, on in zip(stream.locs, stream.t50rise)]


def cicada_detect(
    s: Slice,
    *,
    threshold_scope: str = "global",
    active_duration_sec=(1.0, 2.0),
    n_synchronous_frames: int = 1,
    sce_percentile=(99.99, 99.9999),
    n_surrogates: int = 100,
    sce_min_distance_frames: int = 4,
    imaging_rate_hz: float = 10.0,
    solution_delay_sec: float = 120.0,
    baseline_window_max_sec: float = 1200.0,
    treatment_window_sec: float = 1200.0,
    region_min_sec: float = 900.0,
    rng_seed: int | None = None,
    emit_signal: bool = False,
    onset_field: str = "locs",
    active_duration_mode: str = "fixed",
    duration_field: str = "",
) -> CicadaDetection:
    """Run the CICADA detector on both streams (FAST then SLOW, one RNG).

    onset_field anchors the raster ("locs" peak = CICADA default; explore_sce
    uses "t50rise"). active_duration_mode="per_event" reads per-event
    durations from duration_field on each Stream ("width"), or "rise_dur"
    (computed here as locs - t50rise, matching explore_sce's prep).
    sce_percentile and active_duration_sec take a scalar or a (FAST, SLOW)
    pair — SLOW transients are wider and need a stricter percentile.
    """
    if threshold_scope not in ("global", "regional"):
        raise ValueError('threshold_scope must be "global" or "regional"')
    if active_duration_mode not in ("fixed", "per_event"):
        raise ValueError('active_duration_mode must be "fixed" or "per_event"')

    ext = recording_extent(s)
    t_lo, t_hi = ext
    L = t_hi - t_lo
    rw = effective_region_windows(
        s, ext,
        solution_delay_sec=solution_delay_sec,
        baseline_window_max_sec=baseline_window_max_sec,
        treatment_window_sec=treatment_window_sec,
        region_min_sec=region_min_sec,
    )
    rng = np.random.RandomState(rng_seed) if rng_seed is not None \
        else np.random.RandomState()

    names = list(s.streams)
    pcts = per_stream_param(sce_percentile, names, "sce_percentile")
    adurs = per_stream_param(active_duration_sec, names, "active_duration_sec")

    results = {}
    for name, stream in s.streams.items():
        trains = getattr(stream, onset_field) if onset_field != "t50rise" \
            else (stream.t50rise or stream.locs)
        if active_duration_mode == "per_event":
            if duration_field == "rise_dur":
                dur = rise_durations(stream)
            elif duration_field and hasattr(stream, duration_field):
                dur = getattr(stream, duration_field)
            else:
                raise ValueError(
                    'active_duration_mode="per_event" requires duration_field '
                    f'"{duration_field}" on the stream')
        else:
            dur = None
        results[name] = _detect_stream(
            trains, dur, t_lo, L, rw, rng,
            dt=1.0 / imaging_rate_hz,
            nsync=int(n_synchronous_frames),
            pct=pcts[name],
            adur=adurs[name],
            n_sur=int(n_surrogates),
            min_dist=int(sce_min_distance_frames),
            scope=threshold_scope, emit_signal=emit_signal,
        )

    params = {
        "method": "cicada_sliding", "threshold_scope": threshold_scope,
        "active_duration_sec": active_duration_sec,
        "active_duration_mode": active_duration_mode,
        "onset_field": onset_field, "duration_field": duration_field,
        "n_synchronous_frames": n_synchronous_frames,
        "sce_percentile": sce_percentile, "n_surrogates": n_surrogates,
        "sce_min_distance_frames": sce_min_distance_frames,
        "imaging_rate_hz": imaging_rate_hz, "rng_seed": rng_seed,
        "recording_extent": ext,
        "n_roi": next(iter(s.streams.values())).n_rois,
    }
    return CicadaDetection(slice_id=s.slice_id, streams=results,
                           regions=rw, ext=ext, params=params)


def _build_raster(trains, dur, t_lo, dt, nf, dframes) -> np.ndarray:
    """logical [nCells x nf]: each event marks its cell active from its onset
    frame for the transient duration (fixed dframes, or per-event runs)."""
    nc = len(trains)
    raster = np.zeros((nc, nf), dtype=bool)
    for c in range(nc):
        v = np.asarray(trains[c], dtype=float).ravel()
        keep = np.isfinite(v)
        v = v[keep]
        if v.size == 0:
            continue
        fr = np.floor((v - t_lo) / dt).astype(int)      # 0-based onset frames
        if dur is not None:
            dv = np.asarray(dur[c], dtype=float).ravel()[keep]
            df = np.maximum(1, np.floor(dv / dt + 0.5).astype(int))
        else:
            df = np.full(fr.size, dframes)
        for f, d in zip(fr, df):
            if f < 0 or f >= nf:                         # skipped, not clamped
                continue
            raster[c, f:min(nf, f + d)] = True
    return raster


def _slide_coact(raster: np.ndarray, nsync: int) -> np.ndarray:
    """Distinct cells active in each nsync-frame sliding window (nf-nsync)."""
    nf = raster.shape[1]
    m = nf - nsync
    if m < 1:
        return np.zeros(0)
    windowed = np.lib.stride_tricks.sliding_window_view(raster, nsync, axis=1)
    return windowed[:, :m, :].any(axis=2).sum(axis=0).astype(float)


def _sce_threshold(raster, n_sur, pct, rng) -> float:
    """CICADA get_sce_threshold: roll each cell by randi(nf-1), sum active
    cells PER FRAME, pool over surrogates, take the percentile."""
    nc, nf = raster.shape
    if nf < 2 or nc < 1:
        return 0.0
    pool = np.zeros((n_sur, nf))
    r_float = raster.astype(float)
    for s in range(n_sur):
        row = pool[s]
        for c in range(nc):
            k = int(rng.random_sample() * (nf - 1)) + 1   # MATLAB randi(nf-1)
            row += np.roll(r_float[c], k)
    return matlab_prctile(pool.ravel(), pct)


def _find_peaks(x, minh, mindist) -> np.ndarray:
    """Local maxima >= minh (plateau left edge: > left, >= right), greedily
    thinned tallest-first (stable: earlier wins ties) to >= mindist apart."""
    n = x.size
    if n < 3:
        return np.empty(0, dtype=int)
    interior = np.arange(1, n - 1)
    cand = interior[(x[1:-1] >= minh) & (x[1:-1] > x[:-2]) & (x[1:-1] >= x[2:])]
    if cand.size == 0:
        return np.empty(0, dtype=int)
    order = np.argsort(-x[cand], kind="stable")
    chosen: list[int] = []
    for o in order:
        c = cand[o]
        if not chosen or all(abs(k - c) >= mindist for k in chosen):
            chosen.append(c)
    return np.sort(np.array(chosen, dtype=int))


def _peak_stats(p, coact, raster, trains, t_lo, dt, nsync, nf):
    """Per-SCE onset / peak coactivity / member recruitment / span (0-based p).

    Width = span of member ONSETS in the +-1-frame window, FLOORED at the
    coincidence-window duration — the detector cannot resolve tighter than
    one window, so a duration-overlap peak reports that scale, not 0."""
    onset = t_lo + p * dt
    mag = coact[p]
    f_lo = max(0, p - 1)
    f_hi = min(nf - 1, p + nsync)                 # inclusive, 0-based
    members = np.flatnonzero(raster[:, f_lo:f_hi + 1].any(axis=1))
    tw_lo = t_lo + f_lo * dt
    tw_hi = t_lo + (f_hi + 1) * dt
    tmin, tmax = np.inf, -np.inf
    for c in members:
        v = np.asarray(trains[c], dtype=float).ravel()
        v = v[(v >= tw_lo) & (v < tw_hi)]
        if v.size:
            tmin = min(tmin, v.min())
            tmax = max(tmax, v.max())
    win_dur = tw_hi - tw_lo
    width = max(tmax - tmin, win_dur) if np.isfinite(tmin) else win_dur
    return onset, mag, members.size, width


def _tag_region(onset, rw):
    for w in rw:
        if w.raw_start <= onset < w.raw_end:
            return w.label, w.meets_floor, w.win_start <= onset < w.win_end
    return "none", False, False


def _detect_stream(trains, dur, t_lo, L, rw, rng, *, dt, nsync, pct, adur,
                   n_sur, min_dist, scope, emit_signal) -> CicadaStream:
    nf = max(1, matlab_round(L / dt))
    dframes = max(1, matlab_round(adur / dt))
    raster = _build_raster(trains, dur, t_lo, dt, nf, dframes)
    coact = _slide_coact(raster, nsync)

    onset_l, mag_l, mag_t_l, width_l, thr_l = [], [], [], [], []
    region, in_win, meets = [], [], []
    thr_segs = []

    if scope == "global":
        thr = _sce_threshold(raster, n_sur, pct, rng)
        for p in _find_peaks(coact, thr, min_dist):
            o, m1, m2, w = _peak_stats(p, coact, raster, trains, t_lo, dt, nsync, nf)
            lab, mf, iw = _tag_region(o, rw)
            onset_l.append(o)
            mag_l.append(m1)
            mag_t_l.append(m2)
            width_l.append(w)
            thr_l.append(thr)
            region.append(lab)
            in_win.append(iw)
            meets.append(mf)
        thr_segs.append(dict(label="global", value=thr,
                             win_start=t_lo, win_end=t_lo + L))
    else:  # regional: per-region null + detection within the trimmed window
        ncoact = coact.size
        for w_reg in rw:
            # 1-based frame arithmetic mirrored exactly, then shifted
            f0 = max(1, int(np.floor((w_reg.win_start - t_lo) / dt)) + 1)
            f1 = min(ncoact, int(np.floor((w_reg.win_end - t_lo) / dt)))
            if f1 <= f0:
                continue
            thr = _sce_threshold(raster[:, f0 - 1:min(nf, f1 + nsync - 1)],
                                 n_sur, pct, rng)
            for p_sub in _find_peaks(coact[f0 - 1:f1], thr, min_dist):
                p = p_sub + (f0 - 1)
                o, m1, m2, w = _peak_stats(p, coact, raster, trains, t_lo, dt,
                                           nsync, nf)
                onset_l.append(o)
                mag_l.append(m1)
                mag_t_l.append(m2)
                width_l.append(w)
                thr_l.append(thr)
                region.append(w_reg.label)
                in_win.append(True)
                meets.append(w_reg.meets_floor)
            thr_segs.append(dict(label=w_reg.label, value=thr,
                                 win_start=w_reg.win_start,
                                 win_end=w_reg.win_end))

    signal = None
    if emit_signal:
        signal = SceSignal(
            t=t_lo + np.arange(coact.size) * dt,   # window START times
            y=coact.copy(), thresholds=thr_segs,
            name="distinct cells / sync window", kind="cicada_coactivity")

    return CicadaStream(
        onset_sec=np.array(onset_l), magnitude=np.array(mag_l),
        mag_total=np.array(mag_t_l), width_sec=np.array(width_l),
        threshold=np.array(thr_l), region=region,
        in_stats_window=np.array(in_win, dtype=bool),
        meets_floor=np.array(meets, dtype=bool),
        signal=signal,
    )
