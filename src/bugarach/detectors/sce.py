"""Binned SCE — port of interface2's ``generate_sce``: surrogate-thresholded
synchronous calcium event detection.

Detects time bins where an unusually large number of DISTINCT ROIs are
co-active, relative to a circular-shift null that preserves each ROI's own
event structure while destroying cross-ROI timing. Detection is TOTAL (whole
recording analyzed); min-length floors are recorded as TAGS, never used to
drop events here.

analysis_mode="regional" (default) runs an independent pass per TRIMMED
region window (aCa5z convention, shared with LoCo via region_windows), each
with its own null built from that window's events wrapped WITHIN the window —
a whole-extent wrap would dilute a high-rate window's events and over-detect
there (the promiscuity artifact). "whole" builds one global null and warns
when the recording has more than one populated region.

Episode merging (threshold mode) uses RateDetect's EVENT-TIME gap rule: a
supra-threshold bin joins the current episode iff its first event minus the
episode's last event is <= merge_gap_sec; NaN (default) disables merging
entirely (one episode per bin), 0 merges only events that literally touch.

Parity: one seeded RNG stream per call, FAST then SLOW; each surrogate draws
``rand(1, n_roi)`` — one offset per ROI including empty ones — matching
MATLAB's consumption exactly. Verified to 1e-9 against MATLAB reference
output (tests/fixtures/ref_sce_synth.json) and on a real slice.
"""

from __future__ import annotations

import warnings
from dataclasses import dataclass, field

import numpy as np

from bugarach.detectors._shared import matlab_prctile, matlab_round
from bugarach.detectors.loco import RegionWindow, region_windows
from bugarach.detectors.peaks import peak_gate
from bugarach.detectors.rate import recording_extent
from bugarach.store import Slice


@dataclass
class SceSignal:
    """Concatenated per-window binned-coactivity trace (NaN separators break
    the line across window gaps) + per-region thresholds (kind
    "sce_coactivity", detector_output_spec.md)."""

    t: np.ndarray
    y: np.ndarray
    thresholds: list[dict]      # {label, value, win_start, win_end} per window
    name: str = "distinct ROIs / bin"
    kind: str = "sce_coactivity"


@dataclass
class SceStream:
    """Column-aligned detected SCEs for one stream (generate_sce contract)."""

    onset_sec: np.ndarray       # episode start (first bin start) / t50rise (peak)
    magnitude: np.ndarray       # PEAK coactivity across the merged bins
    mag_total: np.ndarray       # distinct ROIs recruited anywhere in the episode
    width_sec: np.ndarray       # event span (threshold) / half-prominence (peak)
    threshold: np.ndarray       # surrogate threshold used (per event)
    region: list[str]
    in_stats_window: np.ndarray
    meets_floor: np.ndarray
    peak_sec: np.ndarray        # NaN in threshold mode
    t50rise: np.ndarray         # NaN in threshold mode
    t50fall: np.ndarray         # NaN in threshold mode
    width_kind: str             # "tightness" | "half_prominence"
    signal: SceSignal | None = None

    @property
    def n_events(self) -> int:
        return self.onset_sec.size


@dataclass
class SceDetection:
    slice_id: str
    fast: SceStream
    slow: SceStream
    regions: list[RegionWindow]
    ext: tuple[float, float]
    params: dict = field(default_factory=dict)


def sce_detect(
    s: Slice,
    *,
    analysis_mode: str = "regional",
    bin_width_sec: float = 10.0,
    threshold_pctile: float = 99.0,
    n_surrogates: int = 1000,
    surrogate_model: str = "circular_shift",
    solution_delay_sec: float = 120.0,
    baseline_window_max_sec: float = 1200.0,
    treatment_window_sec: float = 1200.0,
    region_min_sec: float = 900.0,
    min_rois: int = 3,
    merge_gap_sec: float = np.nan,
    onset_field: str = "t50rise",
    rng_seed: int | None = None,
    emit_signal: bool = False,
    detection_mode: str = "threshold",
    peak_prominence: float = 0.0,
    peak_min_distance_sec: float = 0.0,
) -> SceDetection:
    """Run the binned-SCE detector on both streams (FAST then SLOW, one RNG)."""
    if analysis_mode not in ("whole", "regional"):
        raise ValueError('analysis_mode must be "whole" or "regional"')
    if detection_mode not in ("threshold", "peak"):
        raise ValueError('detection_mode must be "threshold" or "peak"')
    if surrogate_model == "jitter":
        raise NotImplementedError('surrogate_model "jitter" is not implemented')
    if surrogate_model != "circular_shift":
        raise ValueError(f'unknown surrogate_model "{surrogate_model}"')

    ext = recording_extent(s)
    t_lo, t_hi = ext
    L = t_hi - t_lo
    rw = region_windows(
        s, t_hi,
        solution_delay_sec=solution_delay_sec,
        baseline_window_max_sec=baseline_window_max_sec,
        treatment_window_sec=treatment_window_sec,
        region_min_sec=region_min_sec,
    )
    n_pop = sum(1 for w in rw if w.win_dur > 0)
    if analysis_mode == "whole" and n_pop > 1:
        warnings.warn(
            f'analysis_mode="whole" over {n_pop} populated regions — the '
            "surrogate null/threshold is GLOBAL, not region-aware (high-rate "
            'windows get a diluted bar). Use analysis_mode="regional" unless '
            "you deliberately want a whole-recording null.")

    rng = np.random.RandomState(rng_seed) if rng_seed is not None \
        else np.random.RandomState()
    opts = dict(
        analysis_mode=analysis_mode, bin_width_sec=bin_width_sec,
        threshold_pctile=threshold_pctile, n_surrogates=int(n_surrogates),
        min_rois=min_rois, merge_gap_sec=merge_gap_sec,
        detection_mode=detection_mode, peak_prominence=peak_prominence,
        peak_min_distance_sec=peak_min_distance_sec, emit_signal=emit_signal,
    )

    results = []
    for stream in (s.fast, s.slow):
        trains = getattr(stream, onset_field) or stream.locs
        # per-ROI event times relative to the FULL-extent start (wrap math)
        rel = [np.asarray(v, dtype=float).ravel() - t_lo for v in trains]
        results.append(_detect_modality(rel, t_lo, L, rw, rng, opts))

    params = {
        **{k: v for k, v in opts.items() if k != "emit_signal"},
        "surrogate_model": surrogate_model, "onset_field": onset_field,
        "rng_seed": rng_seed, "recording_extent": ext,
        "n_roi": s.fast.n_rois,
    }
    return SceDetection(slice_id=s.slice_id, fast=results[0], slow=results[1],
                        regions=rw, ext=ext, params=params)


def _coactivity(rel, offsets, L, t_lo, w_lo, w_hi, bw, n_bins) -> np.ndarray:
    """Per-bin count of ROIs with >= 1 (shifted) event in [w_lo, w_hi] —
    population COACTIVITY, not a spike count. offsets 0 => observed."""
    counts = np.zeros(n_bins)
    for r, v in enumerate(rel):
        if v.size == 0:
            continue
        if offsets[r] != 0:
            v = np.mod(v + offsets[r], L)
        t_abs = t_lo + v
        t_in = t_abs[(t_abs >= w_lo) & (t_abs <= w_hi)]
        if t_in.size == 0:
            continue
        idx = np.clip(np.floor((t_in - w_lo) / bw).astype(int), 0, n_bins - 1)
        counts[np.unique(idx)] += 1
    return counts


def _bin_events(rel, t_lo, w_lo, w_hi, bw, n_bins):
    """All in-window observed event times with their bin indices (binning
    identical to _coactivity), plus each event's ROI index."""
    ts, bs, rois = [], [], []
    for r, v in enumerate(rel):
        if v.size == 0:
            continue
        t = t_lo + v
        t = t[(t >= w_lo) & (t <= w_hi)]
        if t.size == 0:
            continue
        idx = np.clip(np.floor((t - w_lo) / bw).astype(int), 0, n_bins - 1)
        ts.append(t)
        bs.append(idx)
        rois.append(np.full(t.size, r))
    if not ts:
        return np.empty(0), np.empty(0, int), np.empty(0, int)
    return np.concatenate(ts), np.concatenate(bs), np.concatenate(rois)


def _run_stats(ts, bs, rois, fb, lb):
    """Distinct-ROI recruitment and first/last event time over bins fb..lb."""
    sel = (bs >= fb) & (bs <= lb)
    if not sel.any():
        return 0, np.nan, np.nan
    return np.unique(rois[sel]).size, ts[sel].min(), ts[sel].max()


def _window_detect(rel, t_lo, L, w_lo, w_hi, rng, opts):
    """One analysis window: in-window wrap null -> percentile threshold ->
    episodes (threshold mode) or peak gating (peak mode)."""
    empty = np.empty(0)
    if w_hi <= w_lo:
        return dict(onset=empty, mag=empty, mag_t=empty, thr=np.nan,
                    width=empty, obs=empty, bctr=empty, peak=empty)

    bw = opts["bin_width_sec"]
    n_sur = opts["n_surrogates"]
    n_roi = len(rel)
    n_bins = max(1, int(np.ceil((w_hi - w_lo) / bw)))
    bctr = w_lo + (np.arange(1, n_bins + 1) - 0.5) * bw

    obs = _coactivity(rel, np.zeros(n_roi), L, t_lo, w_lo, w_hi, bw, n_bins)

    # regional surrogate basis: in-window events wrapped WITHIN the window
    lw = w_hi - w_lo
    rel_win = []
    for v in rel:
        ta = t_lo + v
        ta = ta[(ta >= w_lo) & (ta <= w_hi)]
        rel_win.append(ta - w_lo)

    # one offset per ROI per surrogate — rand(1, n_roi), empty ROIs included
    draws = rng.random_sample((n_sur, n_roi)) * lw
    null_counts = np.zeros((n_sur, n_bins))
    for r, ce in enumerate(rel_win):
        if ce.size == 0:
            continue
        shifted = np.mod(ce[None, :] + draws[:, r:r + 1], lw)
        t_abs = w_lo + shifted
        idx = np.clip(np.floor((t_abs - w_lo) / bw).astype(int), 0, n_bins - 1)
        valid = (t_abs >= w_lo) & (t_abs <= w_hi)
        active = np.zeros((n_sur, n_bins), dtype=bool)
        rows = np.repeat(np.arange(n_sur)[:, None], ce.size, axis=1)
        active[rows[valid], idx[valid]] = True
        null_counts += active
    thr = matlab_prctile(null_counts.ravel(), opts["threshold_pctile"])

    ts, bs, rois = _bin_events(rel, t_lo, w_lo, w_hi, bw, n_bins)

    if opts["detection_mode"] == "peak":
        d_bins = max(1, matlab_round(opts["peak_min_distance_sec"] / bw))
        pk = peak_gate(obs, thr, prominence=opts["peak_prominence"],
                       min_distance=d_bins, floor=opts["min_rois"],
                       strict_above=True)
        n = pk.idx.size
        onset = w_lo + (pk.left_x + 0.5) * bw if n else empty
        peak_sec = w_lo + (pk.idx + 0.5) * bw if n else empty
        width = (pk.right_x - pk.left_x) * bw if n else empty
        mag_t = np.zeros(n)
        for i in range(n):
            fb = max(0, int(np.floor(pk.left_x[i])))
            lb = min(n_bins - 1, int(np.ceil(pk.right_x[i])))
            mag_t[i], _, _ = _run_stats(ts, bs, rois, fb, lb)
        width = np.where(np.isfinite(width), width, np.nan)
        return dict(onset=onset, mag=pk.val.copy(), mag_t=mag_t, thr=thr,
                    width=width, obs=obs, bctr=bctr, peak=peak_sec)

    bins = np.flatnonzero((obs > thr) & (obs >= opts["min_rois"]))
    if bins.size == 0:
        return dict(onset=empty, mag=empty, mag_t=empty, thr=thr, width=empty,
                    obs=obs, bctr=bctr, peak=empty)

    # per-bin first/last observed event time feeds the EVENT-TIME gap merge
    bin_first = np.full(n_bins, np.nan)
    bin_last = np.full(n_bins, np.nan)
    for b in np.unique(bs):
        sel = bs == b
        bin_first[b] = ts[sel].min()
        bin_last[b] = ts[sel].max()

    runs = []
    cs = ce = bins[0]
    run_last = bin_last[bins[0]]
    for b in bins[1:]:
        if bin_first[b] - run_last <= opts["merge_gap_sec"]:  # False for NaN gap
            ce = b
            run_last = bin_last[b]
        else:
            runs.append((cs, ce))
            cs = ce = b
            run_last = bin_last[b]
    runs.append((cs, ce))

    n = len(runs)
    onset = np.zeros(n)
    mag = np.zeros(n)
    mag_t = np.zeros(n)
    width = np.zeros(n)
    for i, (fb, lb) in enumerate(runs):
        onset[i] = w_lo + fb * bw            # episode start (first bin start)
        mag[i] = obs[fb:lb + 1].max()
        mag_t[i], tfirst, tlast = _run_stats(ts, bs, rois, fb, lb)
        width[i] = tlast - tfirst
    width = np.where(np.isfinite(width), width, np.nan)
    return dict(onset=onset, mag=mag, mag_t=mag_t, thr=thr, width=width,
                obs=obs, bctr=bctr, peak=np.full(n, np.nan))


def _tag_region(onset, rw):
    for w in rw:
        if w.raw_start <= onset < w.raw_end:
            return w.label, w.meets_floor, w.win_start <= onset < w.win_end
    return "none", False, False


def _detect_modality(rel, t_lo, L, rw, rng, opts) -> SceStream:
    onset_l, mag_l, mag_t_l, thr_l, width_l, peak_l = [], [], [], [], [], []
    region, in_win, meets = [], [], []
    segments = []

    if opts["analysis_mode"] == "whole":
        b = _window_detect(rel, t_lo, L, t_lo, t_lo + L, rng, opts)
        n = b["onset"].size
        onset_l, mag_l, mag_t_l, width_l, peak_l = \
            [b["onset"]], [b["mag"]], [b["mag_t"]], [b["width"]], [b["peak"]]
        thr_l = [np.full(n, b["thr"])]
        for o in b["onset"]:
            lab, mf, iw = _tag_region(o, rw)
            region.append(lab)
            meets.append(mf)
            in_win.append(iw)
        if opts["emit_signal"]:
            segments.append(dict(t=b["bctr"], y=b["obs"], value=b["thr"],
                                 label="global", win_start=t_lo, win_end=t_lo + L))
    else:  # regional: independent pass per trimmed window, own null/threshold
        for w in rw:
            b = _window_detect(rel, t_lo, L, w.win_start, w.win_end, rng, opts)
            if opts["emit_signal"]:
                segments.append(dict(t=b["bctr"], y=b["obs"], value=b["thr"],
                                     label=w.label, win_start=w.win_start,
                                     win_end=w.win_end))
            n = b["onset"].size
            if n == 0:
                continue
            onset_l.append(b["onset"])
            mag_l.append(b["mag"])
            mag_t_l.append(b["mag_t"])
            thr_l.append(np.full(n, b["thr"]))
            width_l.append(b["width"])
            peak_l.append(b["peak"])
            region.extend([w.label] * n)
            in_win.extend([True] * n)          # within trimmed window by construction
            meets.extend([w.meets_floor] * n)

    cat = lambda parts: np.concatenate(parts) if parts else np.empty(0)  # noqa: E731
    onset = cat(onset_l)
    width = cat(width_l)
    peak_sec = cat(peak_l)
    n = onset.size
    is_peak = opts["detection_mode"] == "peak"

    signal = None
    if opts["emit_signal"]:
        t_parts, y_parts, thrs = [], [], []
        for k, seg in enumerate(segments):
            if k > 0:  # NaN separator breaks the line between windows
                t_parts.append([np.nan])
                y_parts.append([np.nan])
            t_parts.append(seg["t"])
            y_parts.append(seg["y"])
            thrs.append({k2: seg[k2] for k2 in ("label", "value",
                                                "win_start", "win_end")})
        signal = SceSignal(
            t=np.concatenate(t_parts) if t_parts else np.empty(0),
            y=np.concatenate(y_parts) if y_parts else np.empty(0),
            thresholds=thrs)

    return SceStream(
        onset_sec=onset, magnitude=cat(mag_l), mag_total=cat(mag_t_l),
        width_sec=width, threshold=cat(thr_l), region=region,
        in_stats_window=np.array(in_win, dtype=bool),
        meets_floor=np.array(meets, dtype=bool),
        peak_sec=peak_sec,
        t50rise=onset.copy() if is_peak else np.full(n, np.nan),
        t50fall=onset + width if is_peak else np.full(n, np.nan),
        width_kind="half_prominence" if is_peak else "tightness",
        signal=signal,
    )
