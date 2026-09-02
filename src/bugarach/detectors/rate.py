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

from dataclasses import dataclass, field

import numpy as np

from bugarach.detectors.peaks import peak_gate
from bugarach.store import Slice, Stream

# **There is no fallback grid, and there used to be one.** `GRID_DT_FALLBACK =
# 0.1` — the MATLAB original's hardcoded MLspike resolution for 10 Hz imaging —
# was reached whenever `grid_dt` was omitted, and announced itself with a
# `GridDtNotSetWarning`. Both are retired (FOUNDATIONS §6).
#
# The warning was right about the danger and useless as a gate. It fires AFTER
# the trace exists, so by the time anyone reads stderr the number is computed,
# the figure may be drawn and the export may be on disk. It is also the one
# warning in this repo that has never been a true alarm — 0.1 s genuinely is
# this lab's rate — which is the fastest way to train a team to filter one out.
# And it was outnumbered: two sibling detectors assumed the same interval and
# said nothing, so a lab imaging at 20 Hz got one warning and two silent wrong
# answers. `grid_dt` is required now, and the failure is a TypeError at the
# call site instead of a plausible number.
CHARACTERIZATION_PAD_S = 0.5


def _required_grid_dt(grid_dt: float | None) -> float:
    """The rate-trace grid, or a refusal. Never a number this module chose."""
    if grid_dt is None:
        raise ValueError(
            "grid_dt is required: it is the sampling interval of the recording "
            "the trains came from, it cannot be recovered from the times, and "
            "there is no default (FOUNDATIONS §6). A recording loaded by "
            "bugarach carries it — Slice.require_dt() — and a caller holding "
            "bare trains has to say.")
    return grid_dt


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
    """[t_lo, t_hi] seconds = union span of regions + every stream's locs."""
    lo, hi = np.inf, -np.inf
    for r in s.regions:
        for v in (r.start_sec, r.end_sec):
            if np.isfinite(v):
                lo, hi = min(lo, v), max(hi, v)
    for stream in s.streams.values():
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
    grid_dt: float,
) -> tuple[np.ndarray, np.ndarray]:
    """Pooled sliding-window population event rate (Hz) on a grid_dt grid,
    edge-corrected: at recording boundaries the divisor is the truncated
    window span, so rate does not artificially dip.

    grid_dt is **required** and MUST be the sampling interval of the underlying
    recording (mean acquired frame interval) — ``Slice.require_dt()`` is where
    a caller holding a recording gets it."""
    dt = grid_dt
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
    guard_sec: float = 0.0,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, float]:
    """Primary and contextual rates on the shared grid; context window is
    clipped to 0.9 x recording duration (the actual value used is returned).
    See event_rate for the grid_dt contract.

    ``grid_dt`` keeps its position in the signature and loses its fallback: it
    reads as optional and is not. Every caller passes it positionally, so the
    check is a raise rather than a signature change — the alternative reorders
    the arguments of a function two parity suites call by position.

    ``guard_sec`` excludes a band of that width, centred on each grid point,
    from the **context** — the guard cells of a CFAR detector. Without it the
    1 s primary window sits inside its own 60 s context, so an event raises the
    bar it must clear (self-masking) and a second event nearby raises it further
    (mutual masking). Finn & Johnson quantified the second in 1968 as a ~1 dB
    detectability loss; this project met it as the regime-shift incident, where
    four planted events inside every 60 s context drove binned SCE's precision
    from 74% to 10%. See ``docs/detector_history.md`` §5.1.

    **Defaults to 0.0, which is the MATLAB original and the shipped behaviour.**
    The zero case returns before any of the arithmetic below — parity by
    construction rather than by a subtraction happening to cancel, since a naive
    guard band of width 0 would still remove the centre bin.
    """
    grid_dt = _required_grid_dt(grid_dt)
    duration = t_range[1] - t_range[0]
    max_ctx = 0.9 * duration
    ctx_actual = max_ctx if context_sec >= max_ctx else context_sec
    rate_x, rate_y = event_rate(trains, t_range, window_sec, grid_dt)
    _, ctx_y = event_rate(trains, t_range, ctx_actual, grid_dt)
    if guard_sec <= 0:
        return rate_x, rate_y, ctx_y, ctx_actual
    if guard_sec >= ctx_actual:
        raise ValueError(
            f"guard_sec {guard_sec:g} is not smaller than the context window "
            f"{ctx_actual:g} — the guard would consume every reference cell and "
            "leave nothing to estimate the background from")
    # The guarded context is the full window minus the guard band, in COUNTS and
    # in SPAN. Both rates are already counts/span, so recover the counts,
    # subtract, and divide by what is left. Edge truncation carries through from
    # event_rate, so a guard at a recording boundary shrinks the span rather
    # than producing a negative one.
    _, guard_y = event_rate(trains, t_range, guard_sec, grid_dt)
    tmin, tmax = t_range
    ctx_span = (np.minimum(tmax, rate_x + ctx_actual / 2)
                - np.maximum(tmin, rate_x - ctx_actual / 2))
    guard_span = (np.minimum(tmax, rate_x + guard_sec / 2)
                  - np.maximum(tmin, rate_x - guard_sec / 2))
    left_span = ctx_span - guard_span
    with np.errstate(invalid="ignore", divide="ignore"):
        guarded = np.where(left_span > 0,
                           (ctx_y * ctx_span - guard_y * guard_span) / left_span,
                           ctx_y)
    return rate_x, rate_y, guarded, ctx_actual


def rate_detect(
    trains: list[np.ndarray],
    t_range: tuple[float, float],
    *,
    grid_dt: float,
    excess_threshold_hz: float = 5.0,
    merge_gap_s: float = 3.0,
    rate_win: float = 1.0,
    context_win: float = 60.0,
    detection_mode: str = "threshold",
    peak_prominence: float = 0.0,
    peak_min_distance_sec: float = 0.0,
    guard_sec: float = 0.0,
    threshold_mode: str = "additive",
    threshold_alpha: float = 2.0,
) -> RateDetection:
    """Detect synchronous events from spike-rate excess (RateDetect port).

    grid_dt sets the rate-trace resolution, MUST be the sampling interval of
    the underlying recording (mean acquired frame interval), and is now
    **required** — it moved to the front of the keyword arguments to say so.
    A recording loaded by bugarach carries it (``Slice.require_dt()``); a
    caller holding bare trains states it. There is no fallback and no warning:
    FOUNDATIONS §6, and the comment at the top of this module for what the
    warning cost.

    Two options exist that the MATLAB original does not have, **both defaulting
    to the original's behaviour** so parity is unaffected (FOUNDATIONS §2).

    ``guard_sec`` excludes a band around each grid point from the context — see
    :func:`event_rate_context`.

    ``threshold_mode`` chooses how the bar relates to the context:

    * ``"additive"`` (default, the original): fire where
      ``rate - context >= excess_threshold_hz``. The bar is a fixed **offset**,
      so the ratio it represents is ``1 + excess/context`` — enormous when the
      tissue is quiet and approaching 1 when it is busy. That is a rolling
      reference window with **no constant-false-alarm property**, which is why
      this detector fires 34.8 times in a bench block containing nothing planted
      while its recall stays near the leaders'.
    * ``"multiplicative"``: fire where ``rate >= threshold_alpha * context``,
      which is how cell-averaging CFAR sets a threshold. Finn & Johnson make it
      *"proportional to the square root of this estimate of the output
      variance"*; Rohling's processor *"multiplies this estimation Z by a
      scaling factor T"*. Implemented as ``rate - alpha*context >= 0`` so the
      trace, the hilite spans and the peak path stay one code path.

    ``threshold_alpha`` is only read in multiplicative mode. Its default of 2.0
    is a placeholder, **not a calibrated value** — deriving it from a stated
    false-alarm probability is Phase 2 of the revision plan.

    **Measured 2026-09-02: that placeholder is the worst point on the curve, and
    the bench would refuse it.** At alpha 2.0 this fires **6.07/min** into a block
    with nothing planted on ``baseline_quiet`` and **5.47/min** on
    ``baseline_busy``, against ``MAX_PROBE_PER_MIN["rate"] = 2.0``, for an F1 of
    0.136 and 0.125. The alphas that win are an order up — 15 on quiet (F1 0.667),
    10 on busy (0.580) — and fire 0.0/min. The mechanism's reputation for never
    tripping the promiscuity probe belongs to its *calibrated* range, not to the
    value it ships with: flip ``threshold_mode`` without also setting
    ``threshold_alpha`` and you get the one setting
    :func:`~bugarach.bench.pick_operating_point` would have refused.
    ``docs/todo/2026-08-25-two-scorers-two-winners-and-nothing-decides.md``.
    """
    if threshold_mode not in ("additive", "multiplicative"):
        raise ValueError(
            'threshold_mode must be "additive" or "multiplicative", '
            f"got {threshold_mode!r}")
    grid_dt = _required_grid_dt(grid_dt)
    rate_x, rate_y, ctx_y, ctx_actual = event_rate_context(
        trains, t_range, rate_win, context_win, grid_dt, guard_sec=guard_sec
    )
    if threshold_mode == "multiplicative":
        excess = rate_y - threshold_alpha * ctx_y
        excess_threshold_hz = 0.0
    else:
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
        # recorded so a result carries which mechanism produced it — a detection
        # made with a guard is not the same instrument as one made without
        "guard_sec": guard_sec,
        "threshold_mode": threshold_mode,
        "threshold_alpha": threshold_alpha if threshold_mode == "multiplicative"
                           else None,
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
