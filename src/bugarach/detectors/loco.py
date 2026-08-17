"""LoCo (Local Coincidence) — port of interface2's ``detect_loco``.

LoCo = binned distinct-ROI coactivity (SCE's statistic) thresholded against a
ROLLING, rate-local null pool at a high percentile. It shares CoactDetect's
core machinery (distinct-ROI counts, in-context circular-shift surrogates)
but differs in mechanism: instead of a per-bin z-test, a rolling threshold
envelope is built at anchors every thr_step_sec — the percentile of the
pooled shuffled coactivity over a half-context window, and with
null_context_mode="maxlt" (default) the per-anchor bar is the MAX of the
trailing and leading half-context thresholds, so a rate edge cannot lower it
and false-fire. The context clamps to the raw region so the null never
borrows across a region boundary. A bin fires iff S(t) > its local threshold
and S(t) >= min_rois; firing bins merge into episodes.

Runs BOTH streams per call (FAST then SLOW) off one seeded RNG stream, like
the MATLAB original — per-stream results are not independently reproducible,
the whole call is. Parity verified to 1e-9 against MATLAB reference output
(tests/fixtures/ref_loco_synth.json) and on a real slice, both modes, both
null-context modes, including the rolling threshold envelope (MATLAB's
prctile mid-point percentile definition is replicated in _shared.py).
"""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np

from bugarach.detectors._shared import (
    clip_sorted,
    distinct_coact,
    matlab_colon,
    matlab_prctile,
    matlab_round,
)
from bugarach.detectors.peaks import peak_gate
from bugarach.detectors.rate import DetectorSignal, recording_extent
from bugarach.store import Slice


@dataclass
class RegionWindow:
    """One region's raw bounds + stats window (if2_region_windows port)."""

    label: str
    slot: str
    raw_start: float
    raw_end: float
    win_start: float
    win_end: float
    win_dur: float
    meets_floor: bool
    is_baseline: bool
    is_hik: bool
    too_short: bool


@dataclass
class LocoStream:
    """Detected episodes for one stream (generate_sce output contract)."""

    onset_sec: np.ndarray       # first participating event (threshold) / t50rise (peak)
    magnitude: np.ndarray       # PEAK coactivity over the episode
    mag_total: np.ndarray       # distinct ROIs recruited anywhere in the episode
    width_sec: np.ndarray       # participant span (threshold) / half-prom (peak)
    strength: np.ndarray        # = magnitude
    threshold: np.ndarray       # local null threshold at the episode's peak bin
    region: list[str]
    in_stats_window: np.ndarray
    meets_floor: np.ndarray
    peak_sec: np.ndarray        # NaN in threshold mode
    t50rise: np.ndarray         # NaN in threshold mode
    t50fall: np.ndarray         # NaN in threshold mode
    width_kind: str             # "tightness" | "half_prominence"
    strength_kind: str = "local_coincidence_coactivity"
    signal: DetectorSignal | None = None

    @property
    def n_events(self) -> int:
        return self.onset_sec.size


@dataclass
class LocoDetection:
    slice_id: str
    streams: dict[str, LocoStream]     # name -> result, in slice stream order
    regions: list[RegionWindow]
    ext: tuple[float, float]
    params: dict = field(default_factory=dict)

    @property
    def fast(self) -> LocoStream:
        return self.streams["fast"]

    @property
    def slow(self) -> LocoStream:
        return self.streams["slow"]


def region_windows(
    s: Slice,
    t_hi_clamp: float,
    *,
    solution_delay_sec: float = 120.0,
    baseline_window_max_sec: float = 1200.0,
    treatment_window_sec: float = 1200.0,
    region_min_sec: float = 900.0,
) -> list[RegionWindow]:
    """aCa5z region-windowing convention (if2_region_windows port), applied to
    the slice's populated regions. Guards HALT: baseline must start at 0 and
    regions must be chronologically contiguous — a violation is a data bug."""
    regs = [r for r in s.regions if np.isfinite(r.start_sec)]
    if not regs:
        return []
    tol = 1e-6
    if abs(regs[0].start_sec) > tol:
        raise ValueError(
            f"slice {s.slice_id}: region 1 (baseline) start_sec = "
            f"{regs[0].start_sec:.6f}, expected 0")
    for k in range(1, len(regs)):
        if abs(regs[k].start_sec - regs[k - 1].end_sec) > tol:
            raise ValueError(
                f"slice {s.slice_id}: region {k + 1} start_sec = "
                f"{regs[k].start_sec:.6f} does not match region {k} end_sec = "
                f"{regs[k - 1].end_sec:.6f} (gap/overlap)")
    out = []
    for k, r in enumerate(regs):
        raw_start = r.start_sec
        raw_end = r.end_sec if np.isfinite(r.end_sec) else t_hi_clamp
        name = r.name or ""
        is_baseline = k == 0
        is_hik = (not is_baseline) and ("hi" in name.lower())
        if is_baseline:
            dur = min(raw_end - raw_start, baseline_window_max_sec)
            win_end = raw_end
            win_start = win_end - dur           # BACKWARD from baseline end
        elif is_hik:
            win_start, win_end = raw_start, raw_end   # no delay, no cap
        else:
            ts = raw_start + solution_delay_sec       # forward + wash-in delay
            te = raw_end
            if te - ts > treatment_window_sec:
                te = ts + treatment_window_sec
            win_start, win_end = ts, max(te, ts)
        win_dur = win_end - win_start
        label = name if name else (r.slot or "")
        out.append(RegionWindow(
            label=label, slot=r.slot or "",
            raw_start=raw_start, raw_end=raw_end,
            win_start=win_start, win_end=win_end, win_dur=win_dur,
            meets_floor=is_hik or win_dur >= region_min_sec,
            is_baseline=is_baseline, is_hik=is_hik,
            too_short=win_dur < 240.0,
        ))
    return out


def per_stream_param(x, names: list[str], param: str, calibrated=None) -> dict[str, float]:
    """Broadcast a per-stream parameter: scalar (all streams), sequence in
    stream order, or name-keyed dict. For the canonical two-stream stores a
    (FAST, SLOW) pair keeps its historical meaning.

    ``x=None`` means "use the calibrated default", which is where the stream
    count matters. The tuned optima were derived on the canonical two-stream
    store and are written as (FAST, SLOW) pairs; a store with one stream — the
    shape most outside labs have, and the viewer's default presentation
    (FOUNDATIONS §3) — has no SLOW to apply the second element to. So the pair
    is used verbatim for exactly two streams and its FAST element for any other
    count. FAST rather than SLOW because the SLOW optimum is the weakly
    determined one (see ``loco_detect``). Two-stream behaviour is unchanged.
    """
    if x is None:
        if calibrated is None:
            raise ValueError(f"{param} has no calibrated default")
        x = calibrated if len(names) == 2 else calibrated[0]
    if isinstance(x, dict):
        missing = [n for n in names if n not in x]
        if missing:
            raise ValueError(f"{param} missing streams: {missing}")
        return {n: float(x[n]) for n in names}
    a = np.atleast_1d(np.asarray(x, dtype=float))
    if a.size == 1:
        return {n: float(a[0]) for n in names}
    if a.size == len(names):
        return {n: float(v) for n, v in zip(names, a)}
    if a.size == 2 and len(names) == 1:
        raise ValueError(
            f"{param}: a (FAST, SLOW) pair is only meaningful for the canonical "
            f"two-stream store, and this slice has one stream ({names[0]!r}) — "
            f"pass a scalar, or omit the argument for the calibrated default")
    raise ValueError(
        f"{param} must be scalar, a {len(names)}-element sequence in stream "
        f"order, or a dict keyed by stream name {names}")


def supplied_region_windows(s: Slice, t_hi_clamp: float, *,
                            region_min_sec: float = 900.0,
                            **_ignored) -> list[RegionWindow] | None:
    """The producer's own analysis windows, where the folder carries them.

    A region can state both what happened (``start_sec``/``end_sec``) and what
    to score (``analysis_start_sec``/``analysis_end_sec``). Where it states the
    second, that decision is used as given: no wash-in delay, no cap, and no
    guard on where the baseline starts, because none of those are ours to apply
    to somebody else's protocol.

    All or nothing. A slice with windows for some regions and not others would
    be scored under two policies at once, which is worse than either — so that
    raises. Returns ``None`` when no region supplies one, and the caller then
    derives them.
    """
    regs = [r for r in s.regions if np.isfinite(r.start_sec)]
    if not regs:
        return None
    supplied = [r for r in regs if r.has_analysis_window]
    if not supplied:
        return None
    if len(supplied) != len(regs):
        missing = [str(r.slot or r.name or "?")
                   for r in regs if not r.has_analysis_window]
        raise ValueError(
            f"slice {s.slice_id}: {len(supplied)} of {len(regs)} regions carry "
            f"an analysis window; region(s) {', '.join(missing)} do not. Supply "
            f"one for every region or for none — half the producer's windows and "
            f"half ours is two policies inside one number")

    out = []
    for k, r in enumerate(regs):
        raw_end = r.end_sec if np.isfinite(r.end_sec) else t_hi_clamp
        win_start = float(r.analysis_start_sec)
        win_end = (float(r.analysis_end_sec)
                   if np.isfinite(r.analysis_end_sec) else t_hi_clamp)
        name = r.name or ""
        is_baseline = k == 0
        is_hik = (not is_baseline) and ("hi" in name.lower())
        win_dur = win_end - win_start
        out.append(RegionWindow(
            label=name if name else (r.slot or ""), slot=r.slot or "",
            raw_start=r.start_sec, raw_end=raw_end,
            win_start=win_start, win_end=win_end, win_dur=win_dur,
            # the floor and the too-short flag stay ours: they are what a
            # DETECTOR needs in order to refuse a window, not a windowing choice
            meets_floor=is_hik or win_dur >= region_min_sec,
            is_baseline=is_baseline, is_hik=is_hik,
            too_short=win_dur < 240.0))
    return out


def effective_region_windows(s: Slice, ext: tuple[float, float], **kw) -> list[RegionWindow]:
    """Region windows, or — when the slice carries no region annotations
    (foreign data) — one implicit whole-recording window, so region-scoped
    detection analyzes the full extent instead of nothing.

    The producer's own analysis windows win wherever the folder states them;
    only otherwise is this project's convention applied."""
    rw = supplied_region_windows(s, ext[1], **kw)
    if rw:
        return rw
    rw = region_windows(s, ext[1], **kw)
    if rw:
        return rw
    dur = ext[1] - ext[0]
    region_min = kw.get("region_min_sec", 900.0)
    return [RegionWindow(
        label="recording", slot="", raw_start=ext[0], raw_end=ext[1],
        win_start=ext[0], win_end=ext[1], win_dur=dur,
        meets_floor=dur >= region_min, is_baseline=True, is_hik=False,
        too_short=dur < 240.0)]


def loco_detect(
    s: Slice,
    *,
    bin_width_sec=None,
    context_win_sec=None,
    threshold_pctile=99.9,
    min_rois: int = 3,
    n_surrogates: int = 200,
    thr_step_sec=None,
    merge_gap_sec=None,
    null_context_mode: str = "maxlt",
    onset_field: str = "t50rise",
    clamp_context_to_region: bool = True,
    solution_delay_sec: float = 120.0,
    baseline_window_max_sec: float = 1200.0,
    treatment_window_sec: float = 1200.0,
    region_min_sec: float = 900.0,
    rng_seed: int | None = 20260706,
    detection_mode: str = "threshold",
    peak_prominence: float = 0.0,
    peak_min_distance_sec: float = 0.0,
) -> LocoDetection:
    """Run LoCo on every stream of a slice (declaration order, one RNG stream).

    The five tuned knobs take a scalar (all streams), a sequence in stream
    order, or a name-keyed dict. Left unset they resolve to the measured-regime
    F1-optima (FAST bin 1 / ctx 120 / thr_step 15 / gap 2; SLOW bin 2 / ctx 60 /
    thr_step 30 / gap 4; pctile 99.9). Those are a (FAST, SLOW) pair, so they
    apply as a pair only to the canonical two-stream store; a single-stream
    slice gets the FAST element — see ``per_stream_param``. The SLOW optimum is
    weakly determined — treat as provisional.
    """
    if null_context_mode not in ("maxlt", "symmetric"):
        raise ValueError('null_context_mode must be "maxlt" or "symmetric"')
    if detection_mode not in ("threshold", "peak"):
        raise ValueError('detection_mode must be "threshold" or "peak"')

    names = list(s.streams)
    binw = per_stream_param(bin_width_sec, names, "bin_width_sec", (1.0, 2.0))
    mgap = per_stream_param(merge_gap_sec, names, "merge_gap_sec", (2.0, 4.0))
    ctxw = per_stream_param(context_win_sec, names, "context_win_sec", (120.0, 60.0))
    pcti = per_stream_param(threshold_pctile, names, "threshold_pctile", (99.9, 99.9))
    tstp = per_stream_param(thr_step_sec, names, "thr_step_sec", (15.0, 30.0))

    ext = recording_extent(s)
    rw = effective_region_windows(
        s, ext,
        solution_delay_sec=solution_delay_sec,
        baseline_window_max_sec=baseline_window_max_sec,
        treatment_window_sec=treatment_window_sec,
        region_min_sec=region_min_sec,
    )
    rng = np.random.RandomState(rng_seed) if rng_seed is not None \
        else np.random.RandomState()

    # streams processed in declaration order off ONE RNG stream (parity with
    # MATLAB's FAST-then-SLOW for the canonical stores)
    results = {}
    for name, stream in s.streams.items():
        trains = getattr(stream, onset_field) or stream.locs
        results[name] = _detect_stream(
            trains, rw, ext, rng,
            binw=binw[name], mgap=mgap[name], ctx=ctxw[name],
            pctile=pcti[name], tstep=tstp[name],
            min_rois=min_rois, n_surrogates=int(n_surrogates),
            null_context_mode=null_context_mode,
            clamp_context_to_region=clamp_context_to_region,
            detection_mode=detection_mode, peak_prominence=peak_prominence,
            peak_min_distance_sec=peak_min_distance_sec,
        )

    params = {
        "bin_width_sec": binw, "context_win_sec": ctxw,
        "threshold_pctile": pcti, "min_rois": min_rois,
        "n_surrogates": n_surrogates, "thr_step_sec": tstp,
        "merge_gap_sec": mgap, "null_context_mode": null_context_mode,
        "onset_field": onset_field,
        "clamp_context_to_region": clamp_context_to_region,
        "rng_seed": rng_seed, "detection_mode": detection_mode,
        "peak_prominence": peak_prominence,
        "peak_min_distance_sec": peak_min_distance_sec,
        "recording_extent": ext,
    }
    return LocoDetection(slice_id=s.slice_id, streams=results,
                         regions=rw, ext=ext, params=params)


def _region_of(a: float, rw: list[RegionWindow], ext, clamp: bool):
    """Raw-region bounds containing anchor a (extent if none / clamp off)."""
    if clamp:
        for w in rw:
            if w.raw_start <= a < w.raw_end:
                return w.raw_start, w.raw_end
    return ext[0], ext[1]


def _threshold_pool(ev, lo, hi, binw, n_sur, pctile, rng) -> float:
    """Percentile of the LOCAL null pool over [lo, hi]: circular-shift each
    ROI's in-window events, bin distinct-ROI coactivity, pool over all window
    bins x n_sur surrogates. One rand per non-empty ROI per surrogate,
    surrogate-major — identical stream consumption to MATLAB."""
    if hi <= lo:
        return np.inf
    ledges = matlab_colon(lo, binw, hi)
    if ledges.size < 2:
        ledges = np.array([lo, hi])
    m = ledges.size - 1
    lc = hi - lo
    cev = [v[(v >= lo) & (v <= hi)] for v in ev]
    nonempty = [v for v in cev if v.size]
    draws = rng.random_sample((n_sur, len(nonempty)))
    counts = np.zeros((n_sur, m))
    for j, ce in enumerate(nonempty):
        shifted = np.mod(ce[None, :] - lo + draws[:, j:j + 1] * lc, lc) + lo
        # discretize semantics: [ledges[0], ledges[-1]], last bin right-closed
        idx = np.searchsorted(ledges, shifted, side="right") - 1
        idx[shifted == ledges[-1]] = m - 1
        valid = (idx >= 0) & (idx < m) & (shifted >= ledges[0]) & (shifted <= ledges[-1])
        active = np.zeros((n_sur, m), dtype=bool)
        rows = np.repeat(np.arange(n_sur)[:, None], ce.size, axis=1)
        active[rows[valid], idx[valid]] = True
        counts += active
    return matlab_prctile(counts.ravel(), pctile)


def _span(ev, wlo, whi):
    """First/last participating event time and distinct-ROI recruitment
    across the episode's bin span [wlo, whi)."""
    tfirst, tlast, nrec = np.inf, -np.inf, 0
    for v in ev:
        sel = v[(v >= wlo) & (v < whi)]
        if sel.size:
            nrec += 1
            tfirst = min(tfirst, sel[0])
            tlast = max(tlast, sel[-1])
    if nrec == 0:
        tfirst = tlast = wlo
    return tfirst, tlast, nrec


def _tag_region(onset: float, rw: list[RegionWindow]):
    for w in rw:
        if w.raw_start <= onset < w.raw_end:
            return w.label, w.meets_floor, w.win_start <= onset < w.win_end
    return "none", False, False


def _detect_stream(trains, rw, ext, rng, *, binw, mgap, ctx, pctile, tstep,
                   min_rois, n_surrogates, null_context_mode,
                   clamp_context_to_region, detection_mode,
                   peak_prominence, peak_min_distance_sec) -> LocoStream:
    t_lo, t_hi = ext
    half_ctx = ctx / 2
    ev = clip_sorted(trains, t_lo, t_hi)

    edges = matlab_colon(t_lo, binw, t_hi)
    if edges.size < 2:
        edges = np.array([t_lo, t_hi])
    nb = edges.size - 1
    bc = edges[:-1] + binw / 2
    s_obs = distinct_coact(ev, edges)

    # rolling local threshold at anchors (maxlt: max of trailing & leading)
    anchors = matlab_colon(t_lo, tstep, t_hi)
    thr_a = np.zeros(anchors.size)
    for ai, a in enumerate(anchors):
        rs, re = _region_of(a, rw, ext, clamp_context_to_region)
        if null_context_mode == "maxlt":
            tl = _threshold_pool(ev, max(a - half_ctx, rs), a, binw,
                                 n_surrogates, pctile, rng)
            tr = _threshold_pool(ev, a, min(a + half_ctx, re), binw,
                                 n_surrogates, pctile, rng)
            thr_a[ai] = max(tl, tr)
        else:
            thr_a[ai] = _threshold_pool(ev, max(a - half_ctx, rs),
                                        min(a + half_ctx, re), binw,
                                        n_surrogates, pctile, rng)
    thr_bin = thr_a[np.argmin(np.abs(bc[:, None] - anchors[None, :]), axis=1)]

    if detection_mode == "peak":
        # peak-gate S(t) against the ROLLING per-bin threshold — the
        # per-sample theta(t) case the peak-gate kernel is built for
        d_bins = max(1, matlab_round(peak_min_distance_sec / binw))
        pk = peak_gate(s_obs, thr_bin, prominence=peak_prominence,
                       min_distance=d_bins, floor=min_rois, strict_above=True)
        n = pk.idx.size
        onset = bc[0] + pk.left_x * binw if n else np.empty(0)
        peak_sec = bc[0] + pk.idx * binw if n else np.empty(0)
        width = (pk.right_x - pk.left_x) * binw if n else np.empty(0)
        mag = pk.val.copy()
        thr = thr_bin[pk.idx] if n else np.empty(0)
        mag_t = np.zeros(n)
        region, meets, in_win = [], np.zeros(n, bool), np.zeros(n, bool)
        for k in range(n):
            b0 = max(0, int(np.floor(pk.left_x[k])))
            b1 = min(nb - 1, int(np.ceil(pk.right_x[k])))
            _, _, nrec = _span(ev, edges[b0], edges[b1 + 1])
            mag_t[k] = nrec
            lab, mf, iw = _tag_region(onset[k], rw)
            region.append(lab)
            meets[k], in_win[k] = mf, iw
        t50rise, t50fall = onset.copy(), onset + width
        width_kind = "half_prominence"
    else:
        fire = (s_obs > thr_bin) & (s_obs >= min_rois)
        fb = np.flatnonzero(fire)
        runs = []
        if fb.size:
            gap_b = max(1, matlab_round(mgap / binw))
            cur = [fb[0]]
            for b in fb[1:]:
                if b - cur[-1] <= gap_b:
                    cur.append(b)
                else:
                    runs.append(cur)
                    cur = [b]
            runs.append(cur)
        n = len(runs)
        onset = np.zeros(n)
        mag = np.zeros(n)
        mag_t = np.zeros(n)
        width = np.zeros(n)
        thr = np.zeros(n)
        peak_sec = np.full(n, np.nan)
        region, meets, in_win = [], np.zeros(n, bool), np.zeros(n, bool)
        for k, gi in enumerate(runs):
            b0, b1 = gi[0], gi[-1]
            tfirst, tlast, nrec = _span(ev, edges[b0], edges[b1 + 1])
            vals = s_obs[gi]
            pk_i = int(np.argmax(vals))     # first max, like MATLAB
            onset[k] = tfirst
            mag[k] = vals[pk_i]
            mag_t[k] = nrec
            width[k] = tlast - tfirst
            thr[k] = thr_bin[gi[pk_i]]
            lab, mf, iw = _tag_region(tfirst, rw)
            region.append(lab)
            meets[k], in_win[k] = mf, iw
        t50rise = np.full(n, np.nan)
        t50fall = np.full(n, np.nan)
        width_kind = "tightness"

    return LocoStream(
        onset_sec=onset, magnitude=mag, mag_total=mag_t, width_sec=width,
        strength=mag.copy(), threshold=thr, region=region,
        in_stats_window=in_win, meets_floor=meets,
        peak_sec=peak_sec, t50rise=t50rise, t50fall=t50fall,
        width_kind=width_kind,
        signal=DetectorSignal(t=bc, y=s_obs, ref=np.full(nb, np.nan),
                              threshold=thr_bin, hilite=np.empty((0, 2)),
                              name="distinct ROIs / bin (local)",
                              kind="local_coincidence"),
    )
