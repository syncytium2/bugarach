"""rate+context coordination detector — port of interface2's ``RateDetect`` /
``computeEventRateContext`` / ``computeEventRate`` (RateViewer copies; the
production path uses the RateViewer 0.1 s grid, not SpikyViewer's 0.05 s).

Pipeline (matching explore_sce's wiring):

1. Trains are per-ROI onset times (explore_sce feeds ``t50rise``), clipped to
   the recording extent = union span of region bounds and both streams'
   ``locs`` (generate_sce's ``local_recording_extent``).
2. Pooled population rate on a 0.1 s grid: centered sliding-window count /
   effective (edge-truncated) window width, at rate_win (1 s) and context_win
   (60 s; clipped to 0.9 x recording duration when longer).
3. excess = rate - context. THRESHOLD mode: supra-threshold grid times merged
   when <= merge_gap_s apart; zero-duration events dropped. PEAK mode: peak
   gating of the excess trace (prominence + min-distance); half-prominence
   extent is the event window; zero-duration events kept.
4. Event windows padded +-0.5 s for characterization; widths include the pad.

The cSPIKE synchrony characterization of the MATLAB original (mean_C) is the
"light element" path here: detection never uses it, and it stays NaN until
the SPIKE-synchronization port lands.
"""

from __future__ import annotations

import warnings
from dataclasses import dataclass, field

import numpy as np

from bugarach.detectors.peaks import peak_gate
from bugarach.store import Slice, Stream

# Fallback rate-trace grid (s), used only when grid_dt is not given. 0.1 s
# matches the MATLAB original (RateViewer copy), which hardcodes the MLspike
# output resolution of 10 Hz imaging. grid_dt SHOULD be the mean acquired
# frame interval of the underlying recording — the onset stores don't carry
# it yet (filed with the pipeline team), so relying on this fallback raises
# GridDtNotSetWarning to keep the assumption visible.
GRID_DT_FALLBACK = 0.1
CHARACTERIZATION_PAD_S = 0.5


class GridDtNotSetWarning(UserWarning):
    """grid_dt was not specified and fell back to the nominal 0.1 s grid."""


def _resolve_grid_dt(grid_dt: float | None, stacklevel: int) -> float:
    if grid_dt is not None:
        return grid_dt
    warnings.warn(
        f"grid_dt not set — falling back to {GRID_DT_FALLBACK} s (the MATLAB "
        "original's hardcoded 10 Hz MLspike grid). Set grid_dt to the sampling "
        "interval of the underlying recording (mean acquired frame interval); "
        "the onset stores do not carry it, so it must be supplied by the caller.",
        GridDtNotSetWarning,
        stacklevel=stacklevel,
    )
    return GRID_DT_FALLBACK


@dataclass
class DetectorSignal:
    """Plot-ready statistic trace a detector actually thresholded
    (detector_output_spec.md emit_signal contract)."""

    t: np.ndarray
    y: np.ndarray              # primary rate (Hz)
    ref: np.ndarray            # context rate (Hz)
    threshold: None            # threshold lives on the excess scale -> hilite instead
    hilite: np.ndarray         # (K, 2) time spans where excess >= threshold, pre-merge
    name: str = "pop rate (Hz)"
    kind: str = "rate_context"


@dataclass
class RateDetection:
    """Detected events + settings + analyzed signal (mirrors detect_out)."""

    locs: np.ndarray                   # event onsets (s), pad included
    amps: np.ndarray                   # = intra_event_freq_mean
    widths: np.ndarray                 # event widths (s), pad included
    intra_event_freq_max: np.ndarray
    intra_event_freq_mean: np.ndarray
    mean_C_nonadaptive: np.ndarray     # NaN until the SPIKE-synch port lands
    signal: DetectorSignal
    settings: dict = field(default_factory=dict)

    @property
    def n_events(self) -> int:
        return self.locs.size


def recording_extent(s: Slice) -> tuple[float, float]:
    """[t_lo, t_hi] seconds = union span of regions + both streams' locs."""
    lo, hi = np.inf, -np.inf
    for r in s.regions:
        for v in (r.start_sec, r.end_sec):
            if np.isfinite(v):
                lo, hi = min(lo, v), max(hi, v)
    for stream in (s.fast, s.slow):
        for v in stream.locs:
            if v.size:
                lo, hi = min(lo, v.min()), max(hi, v.max())
    if not (np.isfinite(lo) and np.isfinite(hi) and hi > lo):
        raise ValueError("could not derive a positive recording extent from the slice")
    return float(lo), float(hi)


def stream_trains(
    stream: Stream, t_range: tuple[float, float], onset_field: str = "t50rise"
) -> list[np.ndarray]:
    """Per-ROI onset trains clipped to the extent (explore_sce's shimTrains)."""
    lo, hi = t_range
    out = []
    for v in getattr(stream, onset_field):
        v = np.asarray(v, dtype=float).ravel()
        v = v[np.isfinite(v)]
        out.append(v[(v >= lo) & (v <= hi)])
    return out


def _populated(trains: list[np.ndarray]) -> bool:
    # isPopulatedSlice: >= 2 ROI cells and at least one spike overall
    return len(trains) >= 2 and sum(v.size for v in trains) > 0


def _grid(t_range: tuple[float, float], dt: float) -> np.ndarray:
    """tmin:dt:tmax, MATLAB-colon style (endpoint included within roundoff)."""
    from bugarach.detectors._shared import matlab_colon

    return matlab_colon(t_range[0], dt, t_range[1])


def event_rate(
    trains: list[np.ndarray],
    t_range: tuple[float, float],
    window_sec: float,
    grid_dt: float | None = None,
) -> tuple[np.ndarray, np.ndarray]:
    """Pooled sliding-window population event rate (Hz) on a grid_dt grid,
    edge-corrected: at recording boundaries the divisor is the truncated
    window span, so rate does not artificially dip.

    grid_dt MUST be the sampling interval of the underlying recording (mean
    acquired frame interval). Omitting it falls back to the nominal 0.1 s
    grid and raises GridDtNotSetWarning."""
    dt = _resolve_grid_dt(grid_dt, stacklevel=3)
    if not _populated(trains):
        return np.empty(0), np.empty(0)
    tmin, tmax = t_range
    rate_x = _grid(t_range, dt)
    m = rate_x.size
    pooled = np.sort(np.concatenate(trains)) if trains else np.empty(0)
    if pooled.size == 0 or m == 0:
        return rate_x, np.zeros(m)

    edges = np.concatenate((rate_x - dt / 2, [rate_x[-1] + dt / 2]))
    counts, _ = np.histogram(pooled, bins=edges)

    half_bins = int(np.floor(window_sec / (2 * dt) + 0.5))  # MATLAB round
    cum = np.concatenate(([0], np.cumsum(counts)))
    k = np.arange(m)
    lo_i = np.maximum(0, k - half_bins)
    hi_i = np.minimum(m - 1, k + half_bins)
    spk = cum[hi_i + 1] - cum[lo_i]
    t_lo = np.maximum(tmin, rate_x - window_sec / 2)
    t_hi = np.minimum(tmax, rate_x + window_sec / 2)
    return rate_x, spk / (t_hi - t_lo)


def event_rate_context(
    trains: list[np.ndarray],
    t_range: tuple[float, float],
    window_sec: float = 1.0,
    context_sec: float = 60.0,
    grid_dt: float | None = None,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, float]:
    """Primary and contextual rates on the shared grid; context window is
    clipped to 0.9 x recording duration (the actual value used is returned).
    See event_rate for the grid_dt contract."""
    grid_dt = _resolve_grid_dt(grid_dt, stacklevel=3)
    duration = t_range[1] - t_range[0]
    max_ctx = 0.9 * duration
    ctx_actual = max_ctx if context_sec >= max_ctx else context_sec
    rate_x, rate_y = event_rate(trains, t_range, window_sec, grid_dt)
    _, ctx_y = event_rate(trains, t_range, ctx_actual, grid_dt)
    return rate_x, rate_y, ctx_y, ctx_actual


def rate_detect(
    trains: list[np.ndarray],
    t_range: tuple[float, float],
    *,
    excess_threshold_hz: float = 5.0,
    merge_gap_s: float = 3.0,
    rate_win: float = 1.0,
    context_win: float = 60.0,
    detection_mode: str = "threshold",
    peak_prominence: float = 0.0,
    peak_min_distance_sec: float = 0.0,
    grid_dt: float | None = None,
) -> RateDetection:
    """Detect synchronous events from spike-rate excess (RateDetect port).

    grid_dt sets the rate-trace resolution and MUST be the sampling interval
    of the underlying recording (mean acquired frame interval). Omitting it
    falls back to the MATLAB original's nominal 0.1 s grid and raises
    GridDtNotSetWarning — silence it only when 10 Hz genuinely is the
    acquisition rate."""
    grid_dt = _resolve_grid_dt(grid_dt, stacklevel=2)
    rate_x, rate_y, ctx_y, ctx_actual = event_rate_context(
        trains, t_range, rate_win, context_win, grid_dt
    )
    excess = rate_y - ctx_y

    if detection_mode == "peak":
        # Each prominence-qualified local maximum of excess clearing the
        # threshold is one event; its half-prominence extent is the window.
        d_grid = np.median(np.diff(rate_x)) if rate_x.size > 1 else np.nan
        if not np.isfinite(d_grid) or d_grid <= 0:
            d_grid = 1.0
        d_bins = max(1, int(np.floor(peak_min_distance_sec / d_grid + 0.5)))
        pk = peak_gate(
            excess, excess_threshold_hz,
            prominence=peak_prominence, min_distance=d_bins,
            floor=-np.inf, strict_above=False,
        )
        t0 = rate_x[0] if rate_x.size else 0.0
        starts = t0 + pk.left_x * d_grid
        ends = t0 + pk.right_x * d_grid
        # no zero-duration drop: a sharp excess peak is a valid event
    else:
        # supra-threshold grid times, merged when <= merge_gap_s apart
        cand = rate_x[excess >= excess_threshold_hz] if rate_x.size else np.empty(0)
        if cand.size:
            brk = np.flatnonzero(np.diff(cand) > merge_gap_s)
            starts = cand[np.concatenate(([0], brk + 1))]
            ends = cand[np.concatenate((brk, [cand.size - 1]))]
            keep = (ends - starts) > 0  # single-bin crossings are likely noise
            starts, ends = starts[keep], ends[keep]
        else:
            starts = ends = np.empty(0)

    # pad for characterization: spike timing is 0.1 s-gridded and rate is
    # rate_win-smoothed, so give the stats a margin matching the kernel
    starts = starts - CHARACTERIZATION_PAD_S
    ends = ends + CHARACTERIZATION_PAD_S

    n = starts.size
    freq_max = np.zeros(n)
    freq_mean = np.zeros(n)
    for i in range(n):
        mask = (rate_x >= starts[i]) & (rate_x <= ends[i])
        if mask.any():
            freq_max[i] = rate_y[mask].max()
            freq_mean[i] = rate_y[mask].mean()
        elif rate_x.size:
            j = np.argmin(np.abs(rate_x - (starts[i] + ends[i]) / 2))
            freq_max[i] = freq_mean[i] = rate_y[j]

    sup = excess >= excess_threshold_hz
    edg = np.diff(np.concatenate(([False], sup, [False])).astype(int))
    hilite = np.column_stack(
        (rate_x[np.flatnonzero(edg == 1)], rate_x[np.flatnonzero(edg == -1) - 1])
    ) if rate_x.size else np.empty((0, 2))

    settings = {
        "dt_grid": grid_dt,
        "tmin": t_range[0], "tmax": t_range[1],
        "rate_win": rate_win, "context_win": context_win,
        "context_win_actual": ctx_actual,
        "excess_threshold_hz": excess_threshold_hz,
        "merge_gap_s": merge_gap_s,
        "detection_mode": detection_mode,
        "peak_prominence": peak_prominence,
        "peak_min_distance_sec": peak_min_distance_sec,
    }
    return RateDetection(
        locs=starts,
        amps=freq_mean.copy(),
        widths=ends - starts,
        intra_event_freq_max=freq_max,
        intra_event_freq_mean=freq_mean,
        mean_C_nonadaptive=np.full(n, np.nan),
        signal=DetectorSignal(t=rate_x, y=rate_y, ref=ctx_y,
                              threshold=None, hilite=hilite),
        settings=settings,
    )
