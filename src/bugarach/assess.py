"""Onset-coactivity assessment — measure coordination without picking a detector.

Port of interface2's ``measure_coordination_timescale.m``. **Not a seventh
detector**, which is why it does not live under ``detectors/``: it emits no event
times and has no operating point to tune. It answers *"how much coordination is
in this recording, and what does it look like"* with a rate-matched null, and
returns per-slice summary statistics.

Why bugarach needs it
---------------------
Three of the generator's knobs are coordination properties — how often events
happen, how many ROIs they recruit, and how tightly. Measuring those with the six
detectors would make every simulated recording a restatement of whichever
detector measured it, and then training on it would close the circle. The
assessment breaks that: it is a measurement convention, not a calibrated
instrument, so it can set the generator's priors without any detector's operating
point leaking in.

That is what makes a **per-lab** workflow possible at all: *measure your
recordings, parameterize the generator from them, train, detect.* Without this
port that loop needs MATLAB, which is the thing this project exists to remove
(FOUNDATIONS §1).

It is also the closest thing to a real-data check this project has.
``simulation_plan.md`` §6 calls the domain gap the honest blocker — nothing
measures it. This measures part of it: run the assessment on a real recording and
compare what it reports against what a detector or a model claims. Not ground
truth, but not a detector's opinion either.

The two statistics, both off ONE null
-------------------------------------
The null is a per-ROI circular shift **within the window** — each ROI's train
slides by its own random lag and wraps. That holds every ROI's own rate and
burstiness and destroys only cross-ROI phase, so what survives is coordination
beyond what the slice's rate explains. It is the same mechanism ``generate_sce``
uses, applied globally over a roughly stationary window.

1. **Coactivity excess** (headline) — ``sum over bins with obs >= K of
   (obs - null_mean)``, per minute. Excess co-active ROI·events/min. Defined at
   any rate, which is what makes it the headline.
2. **Onset jitter vs null** (secondary) — the SD of participating ROIs' onsets
   within a co-active cluster, against the same statistic computed on every
   surrogate, compared as medians and **never paired**. ⚠ **Undefined unless the
   observed and the surrogate ensemble each form at least one cluster**, so it
   goes missing on quiet recordings — exactly where a lab most needs it. The
   ``jit_defined`` flag is not decoration; a caller that ignores it will silently
   read NaN as zero.

Parity
------
Held to the same 1e-9 bar as the six detectors, and for the same reason: the
algorithm draws only ``rand``, which is bit-compatible with
``RandomState`` (FOUNDATIONS §2). One ``rand(1, n_roi)`` per surrogate, in
surrogate order. MATLAB semantics are preserved where they change the answer —
``matlab_prctile`` for the IQR, and ``std`` with ``ddof=1`` because MATLAB's
``std`` is the sample SD and numpy's default is not.
"""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np

from bugarach.detectors._shared import matlab_prctile
from bugarach.detectors.loco import effective_region_windows
from bugarach.detectors.rate import recording_extent

DEFAULT_MIN_ROIS = (3, 4, 6, 8)
"""The coactivity floors the assessment is reported at.

**Reported as a scan, not chosen.** K is the assessment's one real convention,
and sweeping it is how that convention stays visible instead of becoming a hidden
operating point. A caller quoting a single number must say which K produced it.
"""


@dataclass(frozen=True)
class Assessment:
    """What the assessment measured, at one coactivity floor K."""

    min_rois: int
    meets_floor: bool
    """False when the window is shorter than ``region_min_sec``; every measure is
    NaN and the caller logs an exclusion rather than quoting a number."""
    win_dur: float
    n_roi: int
    n_events_win: int

    roi_rate: np.ndarray = field(default_factory=lambda: np.zeros(0))
    roi_rate_med: float = float("nan")
    roi_rate_mean: float = float("nan")
    ev_rate_permin: float = float("nan")
    width_med: float = float("nan")
    width_iqr: float = float("nan")

    coact_excess: float = float("nan")
    """The headline: excess co-active ROI·events per minute over the rate-matched
    null. Defined at every rate, which the jitter measure is not.

    **Selection-corrected since 2026-08-25** — ``excess_mode="corrected"``, the
    default. See :attr:`sur_excess_med` and ``docs/forks.md`` §13. The uncorrected
    quantity, which is what the MATLAB computes, is :attr:`coact_excess_raw`.
    """
    obs_mass: float = float("nan")
    null_mass: float = float("nan")
    n_coact_bins: int = 0

    coact_excess_raw: float = float("nan")
    """``obs_mass - null_mass``: the excess before the selection correction, and
    exactly what ``measure_coordination_timescale.m`` reports.

    Kept as a field rather than dropped. It is the baseline any claim of
    improvement is measured against (ADR-0003), and the parity fixtures still
    check it — which is why taking the correction needed no parity exemption."""
    sur_excess_med: float = float("nan")
    """The median surrogate's OWN selected-bin excess — what the correction
    subtracts, and the size of the selection bias at this K and this background.

    Every surrogate is scored exactly the way the observation is: take the bins
    where *that surrogate* reaches K, sum its counts there against the ensemble
    mean. A surrogate holds no coordination by construction, so whatever this
    reports is the selection rule rather than the data. Measured on independent
    Poisson ROIs at the busy endpoint it is ~6.15 of an 8.95 headline at K=3."""

    jit_obs: float = float("nan")
    jit_null: float = float("nan")
    jit_excess: float = float("nan")
    jit_defined: bool = False
    """⚠ Read this before reading ``jit_*``. False means no cluster formed in the
    observed data or in the surrogate ensemble, so the comparison does not exist."""

    part_n_obs: float = float("nan")
    """Median participants per cluster — the generator's ``participation``."""
    peak_med: float = float("nan")
    """Median peak coactivity (#ROIs) — a detector's amplitude descriptor."""
    span_med: float = float("nan")
    """Median participant onset span (s) — a detector's width/tightness
    descriptor, and the generator's ``jitter_sec`` axis."""

    n_clusters_obs: int = 0
    n_clusters_null: int = 0
    clusters_permin: float = float("nan")
    """Coordinated-event frequency — the generator's event count per unit time."""

    members: tuple[tuple[int, ...], ...] = ()
    """Which ROIs made up each observed cluster — the assembly question's input.

    Observed clusters only. The surrogates deliberately do not carry it: the
    circular shift is a null for *how much* coactivity there is, not for *who*
    takes part, and reading assembly structure off it would answer the wrong
    question (see ``bugarach.assembly``)."""


def _coact_count(trains, win_dur, bin_width, n_bins, offsets=None):
    """Per-bin distinct-ROI coactivity. An ROI contributes 1 to a bin if it has
    at least one onset there — a count of ROIs, never of spikes (GLOSSARY)."""
    counts = np.zeros(n_bins, dtype=np.float64)
    for r, v in enumerate(trains):
        if v.size == 0:
            continue
        if offsets is not None and offsets[r] != 0.0:
            v = np.mod(v + offsets[r], win_dur)
        idx = np.floor(v / bin_width).astype(np.int64)
        np.clip(idx, 0, n_bins - 1, out=idx)
        counts[np.unique(idx)] += 1.0
    return counts


def _clusters(trains, counts, K, bin_width, n_bins, merge_bins, wm,
              with_members: bool = False):
    """Per co-active cluster: onset SD, participant count, peak coactivity, span.

    With ``with_members``, a fifth value is returned: the ROI indices that made up
    each cluster, in the order they were gathered. It is off by default and the
    surrogate loop leaves it off — the four returned statistics, and every number
    computed from them, are identical either way. Added because *which* cells took
    part is the one thing this function knew and discarded, and the assembly
    question cannot be asked without it
    (``docs/todo/2026-08-18-do-real-slices-have-recurring-assemblies.md``).

    A cluster is a run of supra-K bins merged when no more than ``merge_bins``
    apart. Participants are each ROI's nearest onset within ±``wm`` of the cluster
    centre, kept only when at least K ROIs gather — so a bin can clear K on the
    binning and still produce no cluster once the onsets are actually gathered.

    Identical clustering runs on the observed data and on every surrogate, which
    is what makes the jitter comparison meaningful rather than a comparison of two
    different procedures.
    """
    sds: list[float] = []
    parts: list[int] = []
    peaks: list[float] = []
    spans: list[float] = []
    members: list[tuple[int, ...]] = []

    fire = np.flatnonzero(counts >= K)
    if fire.size == 0:
        return (sds, parts, peaks, spans, members) if with_members \
            else (sds, parts, peaks, spans)

    groups: list[list[int]] = []
    cur = [int(fire[0])]
    for q in range(1, fire.size):
        if fire[q] - fire[q - 1] <= merge_bins:
            cur.append(int(fire[q]))
        else:
            groups.append(cur)
            cur = [int(fire[q])]
    groups.append(cur)

    for g in groups:
        gi = np.asarray(g, dtype=np.float64)
        tc = float(np.mean((gi + 0.5) * bin_width))
        pk = float(np.max(counts[g]))
        gathered: list[float] = []
        who: list[int] = []
        for r, v in enumerate(trains):
            if v.size == 0:
                continue
            near = v[np.abs(v - tc) <= wm]
            if near.size == 0:
                continue
            # MATLAB min returns the first minimum on a tie; argmin does too.
            gathered.append(float(near[np.argmin(np.abs(near - tc))]))
            who.append(r)
        if len(gathered) >= K:
            oo = np.asarray(gathered, dtype=np.float64)
            # ddof=1: MATLAB std is the sample SD. numpy defaults to ddof=0, and
            # at the 3-8 participants this operates on the difference is large.
            sds.append(float(np.std(oo, ddof=1)))
            parts.append(int(oo.size))
            peaks.append(pk)
            spans.append(float(oo.max() - oo.min()))
            members.append(tuple(who))
    return (sds, parts, peaks, spans, members) if with_members \
        else (sds, parts, peaks, spans)


def _med(x):
    a = np.asarray(x, dtype=float)
    return float(np.median(a)) if a.size else float("nan")


def _iqr(x):
    a = np.asarray(x, dtype=float)
    if a.size == 0:
        return float("nan")
    return float(matlab_prctile(a, 75.0) - matlab_prctile(a, 25.0))


def assess_coactivity(
    s,
    *,
    stream: str | None = None,
    window=None,
    region: str = "baseline",
    min_rois=DEFAULT_MIN_ROIS,
    bin_width_sec: float | None = None,
    wm_factor: float = 1.5,
    merge_bins: int = 2,
    n_surrogates: int = 1000,
    rng_seed: int = 20260722,
    region_min_sec: float = 900.0,
    onset_field: str = "t50rise",
    excess_mode: str = "corrected",
) -> list[Assessment]:
    """Assess one stream of one recording. Returns one record per K in ``min_rois``.

    stream: which stream to assess. ``None`` takes the first, which is the whole
      story for the single-stream recordings most labs have (FOUNDATIONS §3).
    window: ``(start, end)`` seconds to assess inside. ``None`` selects by
      ``region``; a recording with no region annotations gets one implicit
      whole-recording window (FOUNDATIONS §4), so foreign data assesses its full
      extent rather than nothing.
    bin_width_sec: coactivity bin. ``None`` uses 1.0 s, the MATLAB default for the
      faster stream. **This is a convention, and it interacts with what counts as
      one event** — say which was used when quoting a result.
    n_surrogates: circular-shift surrogates. 1000 is the MATLAB default and is
      what the reference numbers were produced at.
    excess_mode: how :attr:`Assessment.coact_excess` is computed.

      * ``"corrected"`` (default since 2026-08-25) — subtract the median
        surrogate's own selected-bin excess. **This is a fork from the MATLAB**;
        ``docs/forks.md`` §13 and the decision behind it.
      * ``"raw"`` — ``obs_mass - null_mass``, exactly what
        ``measure_coordination_timescale.m`` computes. The parity fixtures are
        checked against this, so the inherited arithmetic stays verified rather
        than exempted.

      Both are always computed and both are always returned
      (:attr:`Assessment.coact_excess_raw`, :attr:`Assessment.sur_excess_med`);
      this only chooses which one the headline field carries.

    Measurement only. Writes nothing, and returns NaN measures with
    ``meets_floor=False`` rather than a number when the window is too short.
    """
    if excess_mode not in ("corrected", "raw"):
        raise ValueError(
            f'excess_mode must be "corrected" or "raw", got {excess_mode!r}')
    name = stream if stream is not None else next(iter(s.streams))
    st = s.streams[name]
    ext = recording_extent(s)

    if window is None:
        rws = effective_region_windows(s, ext, region_min_sec=region_min_sec)
        want_baseline = region == "baseline"
        picked = None
        for rw in rws:
            if want_baseline and rw.is_baseline:
                picked = rw
                break
            if not want_baseline and not rw.is_baseline and not rw.is_hik:
                picked = rw
                break
        if picked is None:
            return [Assessment(min_rois=int(K), meets_floor=False,
                               win_dur=float("nan"), n_roi=st.n_rois,
                               n_events_win=0) for K in min_rois]
        win_start, win_end, win_dur = picked.win_start, picked.win_end, picked.win_dur
        meets = picked.meets_floor
    else:
        win_start, win_end = float(window[0]), float(window[1])
        win_dur = win_end - win_start
        meets = win_dur >= region_min_sec

    if not meets:
        return [Assessment(min_rois=int(K), meets_floor=False, win_dur=win_dur,
                           n_roi=st.n_rois, n_events_win=0) for K in min_rois]

    bin_width = 1.0 if bin_width_sec is None else float(bin_width_sec)
    wm = wm_factor * bin_width
    win_min = win_dur / 60.0

    # Clip everything to the window up front — the bins, the gather, the widths
    # and the per-ROI rate all derive from one in-window onset set, so no measure
    # can be computed over a different span than another.
    onsets = getattr(st, onset_field)
    trains, n_in_win, widths = [], [], []
    raw_w = getattr(st, "width", None)
    for r in range(st.n_rois):
        v = np.asarray(onsets[r], dtype=float).ravel()
        keep = np.isfinite(v) & (v >= win_start) & (v <= win_end)
        vv = v[keep] - win_start
        trains.append(vv)
        n_in_win.append(vv.size)
        if raw_w is not None:
            wv = np.asarray(raw_w[r], dtype=float).ravel()
            if wv.size == v.size:
                m = keep & np.isfinite(wv)
                widths.append(wv[m])
    widths = np.concatenate(widths) if widths else np.zeros(0)

    n_roi = st.n_rois
    n_bins = max(1, int(np.ceil(win_dur / bin_width)))
    roi_rate = np.asarray(n_in_win, dtype=float) / win_dur

    obs = _coact_count(trains, win_dur, bin_width, n_bins)

    # One RNG stream, one rand(1, n_roi) per surrogate, in surrogate order —
    # the draw order the MATLAB consumes, which is what the parity fixtures rest
    # on. Unchanged by the selection correction below: that reuses these same
    # draws and adds none of its own.
    rng = np.random.RandomState(rng_seed)
    null_sum = np.zeros(n_bins, dtype=np.float64)
    sds_null: dict[int, list[float]] = {int(K): [] for K in min_rois}
    # The per-surrogate counts are KEPT now, where they used to be summed and
    # dropped. The correction needs each surrogate scored the way the observation
    # is — its own bins at K, against the ensemble mean — and the ensemble mean is
    # not known until the loop ends, so one of the two has to be stored. float32
    # halves the footprint and the counts are small integers: at 1000 surrogates
    # over a 75-minute window at 1 s bins this is 18 MB rather than 36.
    sur_counts = np.empty((int(n_surrogates), n_bins), dtype=np.float32)
    for i in range(int(n_surrogates)):
        off = rng.random_sample(n_roi) * win_dur
        shifted = [np.mod(v + off[r], win_dur) if v.size else v
                   for r, v in enumerate(trains)]
        cn = _coact_count(shifted, win_dur, bin_width, n_bins)
        null_sum += cn
        sur_counts[i] = cn
        for K in min_rois:
            sd, _, _, _ = _clusters(shifted, cn, int(K), bin_width, n_bins,
                                    merge_bins, wm)
            if sd:
                sds_null[int(K)].extend(sd)
    null_mean = null_sum / float(n_surrogates)

    width_med, width_iqr = _med(widths), _iqr(widths)
    out: list[Assessment] = []
    for K in min_rois:
        K = int(K)
        bk = np.flatnonzero(obs >= K)
        obs_mass = float(obs[bk].sum()) / win_min
        null_mass = float(null_mean[bk].sum()) / win_min
        raw = obs_mass - null_mass

        # THE SELECTION CORRECTION. Every surrogate scored the way the
        # observation just was — its OWN bins at K, summed against the ensemble
        # mean — and the median of that is what the observation is measured
        # against. Vectorised over the whole ensemble at once because the
        # per-surrogate loop is already the expensive part of this function.
        sel = sur_counts >= K
        sur_ex = ((np.where(sel, sur_counts, 0.0).sum(axis=1)
                   - (sel * null_mean[None, :]).sum(axis=1)) / win_min)
        sur_med = float(np.median(sur_ex)) if sur_ex.size else 0.0

        sd_obs, prt, pk, span, memb = _clusters(trains, obs, K, bin_width, n_bins,
                                                merge_bins, wm, with_members=True)
        jit_obs, jit_null = _med(sd_obs), _med(sds_null[K])
        defined = bool(sd_obs) and bool(sds_null[K])
        out.append(Assessment(
            min_rois=K, meets_floor=True, win_dur=win_dur, n_roi=n_roi,
            n_events_win=int(sum(n_in_win)),
            roi_rate=roi_rate, roi_rate_med=_med(roi_rate),
            roi_rate_mean=float(np.mean(roi_rate)) if roi_rate.size else float("nan"),
            ev_rate_permin=float(sum(n_in_win)) / win_min,
            width_med=width_med, width_iqr=width_iqr,
            coact_excess=(raw - sur_med if excess_mode == "corrected" else raw),
            coact_excess_raw=raw, sur_excess_med=sur_med,
            obs_mass=obs_mass,
            null_mass=null_mass, n_coact_bins=int(bk.size),
            jit_obs=jit_obs, jit_null=jit_null, jit_excess=jit_obs - jit_null,
            jit_defined=defined,
            part_n_obs=_med(prt), peak_med=_med(pk), span_med=_med(span),
            n_clusters_obs=len(sd_obs), n_clusters_null=len(sds_null[K]),
            clusters_permin=len(sd_obs) / win_min,
            members=tuple(memb)))
    return out
