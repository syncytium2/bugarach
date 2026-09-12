"""The surrogate screen's measurements: statistics, yardsticks, destruction.

Everything here is **measurement** — the plan it serves
(``docs/proposals/2026-09-10-surrogate-evaluation-overnight.md``, "What is
measured") fixes what is computed and forbids choosing between yardsticks or
shortlisting candidates tonight. So this module reports numbers side by side and
decides nothing.

Conventions, all from the plan:

* **Frame indices.** Every statistic works on integer frame indices, the nearest
  whole number to ``t/dt`` on the recording's own frame interval. Two onsets of
  one ROI in one frame are a **zero interval**, counted like any other.
* **Surrogates only through** :func:`bugarach.surrogates.generate`. This module
  never moves an onset itself.
* **Not-estimable ROIs are never scored as preserving anything.** An ROI the
  adapter marks not estimable in any draw of a cell is dropped from that cell's
  real *and* surrogate statistics alike, and the drop is reported as coverage.
* **Seeds** are ``zlib.crc32`` of a key's ``repr`` feeding
  ``np.random.RandomState`` (sapper SAP002 bans ``default_rng`` in ``src/``).

The pieces:

1. :func:`summarize` reduces one recording's trains to additive counts, so a
   statistic over any set of recordings — a group, a mouse half — is a sum rather
   than a recomputation. :func:`set_stats` turns summed counts into Table 3's
   statistics.
2. The **three yardsticks**, all measured and none chosen: the mouse-split band
   (:func:`mouse_splits`, :func:`band`), the paired surrogate histogram
   (:func:`paired_p`, Amarasingham et al. 2012's rank P), and the
   exchangeable-negative flag rates (:func:`negative_rates_heldout`,
   :func:`negative_rates_synthetic`).
3. :func:`holm` adjusts each check's P within one grid cell.
4. **Destruction** (:func:`destruction`): planted synthetic twins with a hard
   floor, scored with the assessor's selection-corrected coactivity excess.
"""

from __future__ import annotations

import time
import tracemalloc
import zlib
from dataclasses import dataclass, field

import numpy as np

from bugarach.count_dispersion import burst_rows, fano

# ---------------------------------------------------------------------------
# Declared constants (Table 3 and Table 4 of the plan)
# ---------------------------------------------------------------------------

EDGE_BAND_SEC = 5.0
"""Edge bands at each end of a window (Table 3, edge-band density)."""

ANALYSIS_WINDOW_SEC = 60.0
"""⚠ Inherited from the earlier review, not justified (plan, Table 4)."""

RATE_BIN_SEC = 60.0
"""Counts for the rate-profile statistics are taken over 60-second bins."""

SERIAL_MIN_ONSETS = 5
"""Serial dependence is scored on ROIs with at least five onsets."""

SERIAL_N_SHUFFLES = 10
"""Within-ROI interval shuffles behind each ROI's serial-dependence null.

The null is what a lag-1 Spearman correlation reads when interval order carries
nothing; short sequences read below zero on their own, so the statistic is each
ROI's correlation **minus** the mean of its own shuffles."""

KS_MIN_INTERVALS = 2
"""An ROI needs this many real intervals for its interval distribution to be scored."""

DESTRUCTION_HALF_WINDOW_FRAMES = 2
"""Destruction's coincidence window is ±2 frames (Table 4). The assessor bins,
so the bin is ``2 * 2 + 1 = 5`` frames wide."""

DESTRUCTION_PARTICIPATION = (0.20, 0.50)
DESTRUCTION_JITTER_FRAMES = 1
"""The planted jitter is one frame (its standard deviation)."""

ALPHA = 0.05

#: Table 2: the statistic each control is built to move. A control that fails
#: to move its statistic is a measurement of that statistic's power, not a stop.
CONTROL_TARGETS = {
    "do_nothing": ("movement", "destruction"),
    "interval_shuffle": ("serial_dependence",),
    "homogeneous_resample": ("ks_intervals", "fano_60s", "count_ac1_60s"),
    "edge_thinning": ("edge_density", "edge_density_analysis"),
    "edge_piling": ("edge_density", "edge_density_analysis"),
    "window_circular_shift": ("subfloor",),
    # Uniform dither is a candidate and also the known-bad control for the two
    # floor statistics and the inside-the-previous-event statistic.
    "uniform_dither": ("subfloor", "band_f_2f", "inside_width"),
}


def seed_of(key) -> int:
    """The seed for a key: ``zlib.crc32`` of its ``repr``, as the adapter does."""
    return zlib.crc32(repr(key).encode("utf-8")) & 0xFFFFFFFF


def rng_of(key) -> np.random.RandomState:
    return np.random.RandomState(seed_of(key))


# ---------------------------------------------------------------------------
# Recordings on the frame grid
# ---------------------------------------------------------------------------

def to_frames(times_sec, dt: float) -> np.ndarray:
    """Nearest whole frame to ``t/dt``, halves away from zero (``matlab_round``'s
    rule, which ``simulate`` quantizes with), as sorted int64."""
    x = np.asarray(times_sec, dtype=float).ravel()
    x = x[np.isfinite(x)] / float(dt)
    f = np.sign(x) * np.floor(np.abs(x) + 0.5)
    return np.sort(f.astype(np.int64))


@dataclass
class RecordingTrains:
    """One stream of one recording, on its own frame grid, inside its window."""

    recording_id: str
    mouse: str
    group: str | None
    dt: float
    window: tuple[int, int]
    """Generation window in frames, half-open."""
    trains: list[np.ndarray]
    """Sorted int64 frame indices per ROI, all inside ``window``."""
    widths: list[np.ndarray] | None = None
    """Per-event width in whole frames, aligned with ``trains``; ``None`` when
    the stream carries no producer-defined width."""
    stream: str = ""
    window_source: str = ""

    @property
    def n_frames(self) -> int:
        return int(self.window[1] - self.window[0])


def recordings_from_slices(slices, stream: str, *, baseline_labels=None):
    """Every recording of ``slices`` as :class:`RecordingTrains` for ``stream``.

    The window comes from :func:`bugarach.assess_folder.generation_window` — the
    producer's baseline, or the whole recording where the folder declares no
    regions (labelled an assumption). A recording that declares regions and no
    baseline is skipped, as is one without ``stream`` or a frame interval.

    **The whole-recording window** runs from frame 0 to one frame past the last
    onset of any stream, since an export folder carries no duration of its own.
    Its end edge band therefore always holds that last onset; the source string
    says so, so an edge statistic on such a folder is read with that in mind.

    Returns ``(recordings, skipped)``, ``skipped`` a list of ``(id, reason)``.
    """
    from bugarach.assess_folder import NoBaselineRegion, generation_window

    out, skipped = [], []
    for s in slices:
        if stream not in s.streams:
            skipped.append((s.slice_id, f"no stream {stream!r}"))
            continue
        if not s.has_dt:
            skipped.append((s.slice_id, "no frame interval declared"))
            continue
        dt = float(s.dt)
        try:
            win, source = generation_window(s, baseline_labels=baseline_labels)
        except NoBaselineRegion as e:
            skipped.append((s.slice_id, str(e)))
            continue
        st = s.streams[stream]
        onsets = st.t50rise or st.locs
        if win is None:
            last = max((float(np.nanmax(v)) for stv in s.streams.values()
                        for v in (stv.t50rise or stv.locs)
                        if np.size(v) and np.any(np.isfinite(v))), default=0.0)
            w = (0, int(to_frames([last], dt)[0]) + 1)
            source = (f"{source}; frame 0 to one frame past the last onset, so the "
                      f"end edge band always holds that onset")
        else:
            w = (int(to_frames([win[0]], dt)[0]), int(to_frames([win[1]], dt)[0]))
        trains, widths = [], []
        has_w = bool(getattr(st, "has_width", False))
        for i, v in enumerate(onsets):
            v = np.asarray(v, dtype=float).ravel()
            ok = np.isfinite(v)
            fr = np.full(v.size, -1, dtype=np.int64)
            x = v[ok] / dt
            fr[ok] = (np.sign(x) * np.floor(np.abs(x) + 0.5)).astype(np.int64)
            keep = ok & (fr >= w[0]) & (fr < w[1])
            order = np.argsort(fr[keep], kind="stable")
            trains.append(fr[keep][order])
            if has_w:
                wv = np.asarray(st.width[i], dtype=float).ravel()
                if wv.size == v.size:
                    wf = np.floor(wv[keep] / dt + 0.5)
                    widths.append(np.where(np.isfinite(wf), wf, np.nan)[order])
                else:
                    widths.append(np.full(int(keep.sum()), np.nan))
        meta = getattr(s, "meta", {}) or {}
        out.append(RecordingTrains(
            recording_id=s.slice_id,
            mouse=str(meta.get("subject_id") or s.slice_id),
            group=(str(meta.get("group_id")).strip() or None)
            if meta.get("group_id") else None,
            dt=dt, window=w, trains=trains,
            widths=widths if has_w else None,
            stream=stream, window_source=source))
    return out, skipped


def observed_floor(recordings) -> int | None:
    """The shortest within-ROI interval in these windows, in frames."""
    best = None
    for rec in recordings:
        for v in rec.trains:
            if v.size >= 2:
                m = int(np.min(np.diff(v)))
                best = m if best is None else min(best, m)
    return best


# ---------------------------------------------------------------------------
# Per-recording summaries — additive, so any set is a sum
# ---------------------------------------------------------------------------

@dataclass
class Summary:
    """One recording (or one surrogate draw of it) reduced to additive counts."""

    n_roi: int = 0
    n_onsets: int = 0
    n_iv: int = 0
    n_roi_iv: int = 0
    sub: dict = field(default_factory=dict)       # f label -> count of intervals < f
    band: dict = field(default_factory=dict)      # f label -> count in [f, 2f)
    n_iv_width: int = 0
    inside_width: int = 0
    n_roi_width: int = 0
    serial_sum: float = 0.0
    n_roi_serial: int = 0
    fano_vals: list = field(default_factory=list)
    ac1_vals: list = field(default_factory=list)
    n_roi_rate: int = 0
    edge_count: int = 0
    edge_len: int = 0
    win_len: int = 0
    aw_edge_count: int = 0
    aw_edge_len: int = 0
    aw_count: int = 0
    aw_len: int = 0
    n_roi_active: int = 0
    pooled_iv: np.ndarray = field(default_factory=lambda: np.zeros(0, np.int64))

    def __add__(self, o: "Summary") -> "Summary":
        s = Summary()
        for k in ("n_roi", "n_onsets", "n_iv", "n_roi_iv", "n_iv_width",
                  "inside_width", "n_roi_width", "serial_sum", "n_roi_serial",
                  "n_roi_rate", "edge_count", "edge_len", "win_len",
                  "aw_edge_count", "aw_edge_len", "aw_count", "aw_len",
                  "n_roi_active"):
            setattr(s, k, getattr(self, k) + getattr(o, k))
        s.sub = {k: self.sub.get(k, 0) + o.sub.get(k, 0)
                 for k in set(self.sub) | set(o.sub)}
        s.band = {k: self.band.get(k, 0) + o.band.get(k, 0)
                  for k in set(self.band) | set(o.band)}
        s.fano_vals = self.fano_vals + o.fano_vals
        s.ac1_vals = self.ac1_vals + o.ac1_vals
        s.pooled_iv = np.concatenate([self.pooled_iv, o.pooled_iv])
        return s


def _spearman_rows(x: np.ndarray, y: np.ndarray) -> np.ndarray:
    """Row-wise Spearman correlation with average ranks; NaN where undefined."""
    from scipy.stats import rankdata

    rx = rankdata(x, axis=1)
    ry = rankdata(y, axis=1)
    rx = rx - rx.mean(axis=1, keepdims=True)
    ry = ry - ry.mean(axis=1, keepdims=True)
    den = np.sqrt((rx ** 2).sum(axis=1) * (ry ** 2).sum(axis=1))
    with np.errstate(invalid="ignore", divide="ignore"):
        return np.where(den > 0, (rx * ry).sum(axis=1) / den, np.nan)


def serial_excess(iv: np.ndarray, rng) -> float:
    """Lag-1 Spearman correlation of consecutive intervals, minus its mean over
    :data:`SERIAL_N_SHUFFLES` within-ROI shuffles. NaN where undefined."""
    iv = np.asarray(iv, dtype=float)
    if iv.size < SERIAL_MIN_ONSETS - 1:
        return float("nan")
    obs = _spearman_rows(iv[None, :-1], iv[None, 1:])[0]
    if not np.isfinite(obs):
        return float("nan")
    perm = np.argsort(rng.random_sample((SERIAL_N_SHUFFLES, iv.size)), axis=1)
    sh = iv[perm]
    null = _spearman_rows(sh[:, :-1], sh[:, 1:])
    null = null[np.isfinite(null)]
    if null.size == 0:
        return float("nan")
    return float(obs - null.mean())


def serial_excess_batch(ivs, rng) -> list[float]:
    """:func:`serial_excess` for many ROIs at once, grouped by interval count.

    Same statistic, same null, vectorized: ROIs with equally many intervals are
    ranked in one call. The shuffles are drawn group by group in ascending
    length, so the result is deterministic for a given ``rng`` state but not
    draw-for-draw identical to calling :func:`serial_excess` ROI by ROI.
    Returns one value per input, NaN where undefined.
    """
    out = [float("nan")] * len(ivs)
    by_n: dict[int, list[int]] = {}
    for i, iv in enumerate(ivs):
        if len(iv) >= SERIAL_MIN_ONSETS - 1:
            by_n.setdefault(len(iv), []).append(i)
    S = SERIAL_N_SHUFFLES
    for n in sorted(by_n):
        idx = by_n[n]
        X = np.asarray([ivs[i] for i in idx], dtype=float)          # (m, n)
        obs = _spearman_rows(X[:, :-1], X[:, 1:])
        perm = np.argsort(rng.random_sample((len(idx) * S, n)), axis=1)
        Xs = np.repeat(X, S, axis=0)
        sh = np.take_along_axis(Xs, perm, axis=1)
        null = _spearman_rows(sh[:, :-1], sh[:, 1:]).reshape(len(idx), S)
        with np.errstate(invalid="ignore"):
            cnt = np.isfinite(null).sum(axis=1)
            mean_null = np.where(cnt > 0, np.nansum(null, axis=1) / np.maximum(cnt, 1),
                                 np.nan)
        for j, i in enumerate(idx):
            if np.isfinite(obs[j]) and np.isfinite(mean_null[j]):
                out[i] = float(obs[j] - mean_null[j])
    return out


def summarize(trains, window, dt: float, fs: dict, *, widths=None,
              rng=None, roi_mask=None) -> Summary:
    """Reduce one recording's trains (frame indices) to additive counts.

    ``fs`` maps a label to a provisional dead time *f* in frames; the sub-floor
    and ``[f, 2f)`` counts are taken for every one, so one set of draws serves
    all three *f* of the sweep. ``roi_mask`` drops ROIs (not-estimable ones)
    from every count. ``rng`` drives only the serial-dependence shuffles.
    """
    if rng is None:
        rng = np.random.RandomState(0)
    w0, w1 = int(window[0]), int(window[1])
    n_frames = w1 - w0
    e = max(1, int(np.floor(EDGE_BAND_SEC / dt + 0.5)))
    aw = max(1, int(np.floor(ANALYSIS_WINDOW_SEC / dt + 0.5)))
    n_aw = n_frames // aw
    s = Summary(sub={k: 0 for k in fs}, band={k: 0 for k in fs})
    s.win_len = n_frames
    s.edge_len = 2 * min(e, n_frames)
    s.aw_len = n_aw * aw
    s.aw_edge_len = n_aw * 2 * min(e, aw)
    ivs = []
    serial_in = []
    rate_windows = []
    for r, v in enumerate(trains):
        if roi_mask is not None and not roi_mask[r]:
            continue
        v = np.sort(np.asarray(v, dtype=np.int64))
        s.n_roi += 1
        s.n_onsets += int(v.size)
        if v.size:
            s.n_roi_active += 1
        # Edge bands at the generation window's two ends.
        s.edge_count += int(np.sum((v >= w0) & (v < w0 + e))
                            + np.sum((v >= w1 - e) & (v < w1)))
        if n_aw:
            rel = v - w0
            rel = rel[(rel >= 0) & (rel < n_aw * aw)]
            pos = rel % aw
            s.aw_count += int(rel.size)
            s.aw_edge_count += int(np.sum(pos < e) + np.sum(pos >= aw - e))
        rate_windows.append(((v - w0) * dt).astype(float))
        if v.size < 2:
            continue
        iv = np.diff(v)
        ivs.append(iv)
        s.n_iv += int(iv.size)
        s.n_roi_iv += 1
        for k, f in fs.items():
            s.sub[k] += int(np.sum(iv < f))
            s.band[k] += int(np.sum((iv >= f) & (iv < 2 * f)))
        if widths is not None and r < len(widths) and widths[r] is not None:
            wr = np.asarray(widths[r], dtype=float)
            if wr.size == v.size:
                prev = wr[:-1]
                ok = np.isfinite(prev)
                if ok.any():
                    s.n_roi_width += 1
                    s.n_iv_width += int(ok.sum())
                    s.inside_width += int(np.sum(iv[ok] < prev[ok]))
        if v.size >= SERIAL_MIN_ONSETS:
            serial_in.append(iv)
    for se in serial_excess_batch(serial_in, rng):
        if np.isfinite(se):
            s.serial_sum += se
            s.n_roi_serial += 1
    s.pooled_iv = np.concatenate(ivs) if ivs else np.zeros(0, np.int64)
    # Rate profile through the shared definition (`count_dispersion`).
    rows = burst_rows([(rate_windows, n_frames * dt)], RATE_BIN_SEC)
    s.n_roi_rate = len(rows)
    for c in rows:
        fv = fano([c])
        if np.isfinite(fv):
            s.fano_vals.append(fv)
        if c.size >= 3 and c[:-1].std() > 0 and c[1:].std() > 0:
            s.ac1_vals.append(float(np.corrcoef(c[:-1], c[1:])[0, 1]))
    return s


def _ratio(num, den):
    return float(num) / float(den) if den else float("nan")


STAT_NAMES_BASE = ("inside_width", "serial_dependence", "fano_60s",
                   "count_ac1_60s", "edge_density", "edge_density_analysis")


def stat_names(fs: dict) -> list[str]:
    """Every scalar statistic's name for this sweep of *f*."""
    names = []
    for k in fs:
        names += [f"subfloor@{k}", f"band_f_2f@{k}"]
    return names + list(STAT_NAMES_BASE)


def set_stats(s: Summary, fs: dict) -> dict:
    """Table 3's scalar statistics from summed counts, with each one's coverage.

    Returns ``{name: (value, coverage)}``; coverage is the share of ROIs the
    statistic could score. ``ks_intervals`` is two-sample and lives in
    :func:`ks_paired` / :func:`ks_pooled`.
    """
    out = {}
    cov_iv = _ratio(s.n_roi_iv, s.n_roi)
    for k in fs:
        out[f"subfloor@{k}"] = (_ratio(s.sub.get(k, 0), s.n_iv), cov_iv)
        out[f"band_f_2f@{k}"] = (_ratio(s.band.get(k, 0), s.n_iv), cov_iv)
    out["inside_width"] = (_ratio(s.inside_width, s.n_iv_width),
                           _ratio(s.n_roi_width, s.n_roi))
    out["serial_dependence"] = (_ratio(s.serial_sum, s.n_roi_serial),
                                _ratio(s.n_roi_serial, s.n_roi))
    cov_rate = _ratio(s.n_roi_rate, s.n_roi)
    out["fano_60s"] = (float(np.mean(s.fano_vals)) if s.fano_vals else float("nan"),
                       cov_rate)
    out["count_ac1_60s"] = (float(np.mean(s.ac1_vals)) if s.ac1_vals
                            else float("nan"), cov_rate)
    cov_act = _ratio(s.n_roi_active, s.n_roi)
    out["edge_density"] = (_ratio(_ratio(s.edge_count, s.edge_len),
                                  _ratio(s.n_onsets, s.win_len)), cov_act)
    out["edge_density_analysis"] = (_ratio(_ratio(s.aw_edge_count, s.aw_edge_len),
                                           _ratio(s.aw_count, s.aw_len)), cov_act)
    return out


# ---------------------------------------------------------------------------
# Interval distributions: two-sample Kolmogorov-Smirnov on integer intervals
# ---------------------------------------------------------------------------

def ks_distance(a, b) -> float:
    """Two-sample KS distance between two sets of intervals. NaN if either is empty."""
    a = np.sort(np.asarray(a, dtype=np.int64))
    b = np.sort(np.asarray(b, dtype=np.int64))
    if a.size == 0 or b.size == 0:
        return float("nan")
    u = np.union1d(a, b)
    fa = np.searchsorted(a, u, side="right") / a.size
    fb = np.searchsorted(b, u, side="right") / b.size
    return float(np.max(np.abs(fa - fb)))


def ks_paired(real_trains, draws_trains, *, roi_mask=None):
    """Per-ROI interval KS, as a paired statistic over ``K`` draws.

    Each object — the real recording and each draw — is compared with the pool of
    **all the other draws'** intervals of the same ROI, so the real recording and
    the draws are scored the same way and the real one is exchangeable with them
    exactly when the surrogate preserves the ROI's interval distribution. Averaged
    over ROIs with at least :data:`KS_MIN_INTERVALS` real intervals; a draw that
    leaves such an ROI with no interval scores 1.0 there, the largest distance.

    Returns ``(ks_sum, n_roi)``: ``ks_sum`` a length ``K + 1`` array, real first,
    so sets of recordings add.
    """
    K = len(draws_trains)
    sums = np.zeros(K + 1)
    n = 0
    for r, v in enumerate(real_trains):
        if roi_mask is not None and not roi_mask[r]:
            continue
        riv = np.diff(np.sort(np.asarray(v, dtype=np.int64)))
        if riv.size < KS_MIN_INTERVALS:
            continue
        div = [np.diff(np.sort(np.asarray(d[r], dtype=np.int64))) for d in draws_trains]
        allv = np.concatenate([riv] + div)
        u = np.unique(allv)
        # Per-object counts on the shared support, then CDFs by cumsum.
        H = np.zeros((K + 1, u.size))
        H[0] = np.bincount(np.searchsorted(u, riv), minlength=u.size)
        for k, d in enumerate(div):
            if d.size:
                H[k + 1] = np.bincount(np.searchsorted(u, d), minlength=u.size)
        C = np.cumsum(H, axis=1)
        tot = C[:, -1]
        pool_all = C[1:].sum(axis=0)
        pool_tot = tot[1:].sum()
        out = np.empty(K + 1)
        with np.errstate(invalid="ignore", divide="ignore"):
            # the real recording against every draw
            out[0] = (np.max(np.abs(C[0] / tot[0] - pool_all / pool_tot))
                      if pool_tot > 0 else np.nan)
            for k in range(1, K + 1):
                if tot[k] == 0:
                    out[k] = 1.0
                    continue
                pt = pool_tot - tot[k]
                if pt <= 0:
                    out[k] = np.nan
                    continue
                out[k] = np.max(np.abs(C[k] / tot[k] - (pool_all - C[k]) / pt))
        sums += np.nan_to_num(out, nan=0.0)
        n += 1
    return sums, n


def ks_pooled(a_summary: Summary, b_summary: Summary) -> float:
    """KS distance between two sets' pooled intervals (used by the band)."""
    return ks_distance(a_summary.pooled_iv, b_summary.pooled_iv)


# ---------------------------------------------------------------------------
# Movement
# ---------------------------------------------------------------------------

def movement(real_trains, sur_trains, unchanged=None) -> dict:
    """Share of onsets moved, median and RMS displacement (frames), share of
    ROIs unchanged.

    Onsets are paired by rank where the surrogate kept the ROI's count and by
    nearest surrogate onset where it did not; an ROI the surrogate emptied has
    every onset moved with no displacement to measure. Descriptive: a wrapped
    circular shift pairs by rank, which is not its offset.
    """
    disp, moved, total, same = [], 0, 0, 0
    for r, v in enumerate(real_trains):
        v = np.sort(np.asarray(v, dtype=np.int64))
        w = np.sort(np.asarray(sur_trains[r], dtype=np.int64))
        is_same = (v.size == w.size and np.array_equal(v, w))
        if unchanged is not None and r < len(unchanged):
            is_same = bool(unchanged[r]) or is_same
        same += int(is_same)
        if v.size == 0:
            continue
        total += v.size
        if w.size == v.size:
            d = np.abs(w - v)
        elif w.size == 0:
            moved += v.size
            continue
        else:
            idx = np.clip(np.searchsorted(w, v), 1, w.size - 1) if w.size > 1 else \
                np.zeros(v.size, dtype=int)
            if w.size > 1:
                d = np.minimum(np.abs(w[idx] - v), np.abs(w[idx - 1] - v))
            else:
                d = np.abs(w[0] - v)
        moved += int(np.sum(d != 0))
        disp.append(d)
    d = np.concatenate(disp) if disp else np.zeros(0)
    return {
        "share_moved": _ratio(moved, total),
        "median_disp_frames": float(np.median(d)) if d.size else float("nan"),
        "rms_disp_frames": float(np.sqrt(np.mean(d.astype(float) ** 2)))
        if d.size else float("nan"),
        "share_rois_unchanged": _ratio(same, len(real_trains)),
    }


# ---------------------------------------------------------------------------
# Yardsticks
# ---------------------------------------------------------------------------

def paired_p(real: float, draws) -> float:
    """Two-sided Monte Carlo P of ``real`` among ``K`` surrogate draws.

    ``2 * min((1 + #{S_k >= S_0}), (1 + #{S_k <= S_0})) / (K + 1)``, capped at 1
    — the rank P of Amarasingham et al. 2012, doubled for two sides. A draw equal
    to the real value counts on both sides, so a surrogate that returns its
    input reads P = 1. NaN draws are ignored; NaN if nothing is left.
    """
    d = np.asarray(draws, dtype=float)
    d = d[np.isfinite(d)]
    if not np.isfinite(real) or d.size == 0:
        return float("nan")
    k = d.size
    ge = (1 + np.sum(d >= real)) / (k + 1)
    le = (1 + np.sum(d <= real)) / (k + 1)
    return float(min(1.0, 2.0 * min(ge, le)))


def mouse_splits(mice, n_splits: int = 100, *, key=("splits",), strata=None):
    """``n_splits`` half splits of ``mice``, grouped by mouse.

    ``strata`` maps each mouse to its group, and each group is halved on its own
    so both halves carry every group; an odd group gives its extra mouse to the
    second half. Returns a list of ``(set_a, set_b)``. Seeded from ``key``.
    """
    mice = sorted(set(mice))
    rng = rng_of(key)
    by = {}
    for m in mice:
        by.setdefault(None if strata is None else strata.get(m), []).append(m)
    out = []
    for _ in range(int(n_splits)):
        a, b = set(), set()
        for g in sorted(by, key=lambda x: str(x)):
            ms = list(by[g])
            perm = rng.permutation(len(ms))
            half = len(ms) // 2
            a |= {ms[i] for i in perm[:half]}
            b |= {ms[i] for i in perm[half:]}
        out.append((a, b))
    return out


def band(split_diffs) -> dict:
    """The mouse-split band: quantiles of real-against-real half differences."""
    d = np.asarray(split_diffs, dtype=float)
    d = d[np.isfinite(d)]
    if d.size == 0:
        return {"n": 0, "q025": float("nan"), "q975": float("nan"),
                "abs_q95": float("nan")}
    return {"n": int(d.size), "q025": float(np.quantile(d, 0.025)),
            "q975": float(np.quantile(d, 0.975)),
            "abs_q95": float(np.quantile(np.abs(d), 0.95))}


def band_p(delta: float, split_diffs) -> float:
    """``(1 + #{|d_j| >= |delta|}) / (n + 1)`` over the split differences."""
    d = np.asarray(split_diffs, dtype=float)
    d = d[np.isfinite(d)]
    if not np.isfinite(delta) or d.size == 0:
        return float("nan")
    return float((1 + np.sum(np.abs(d) >= abs(delta))) / (d.size + 1))


def correction_reach(m: int, n_splits: int, K: int, *, alpha: float = ALPHA) -> dict:
    """Can a CORRECTED test flag anything at these settings? Arithmetic, before compute.

    A rank test's smallest possible ``P`` is fixed by its sample: the mouse-split band's
    is ``1/(n_splits + 1)``, the paired surrogate histogram's ``2/(K + 1)``. Holm
    multiplies the smallest ``P`` in a family by the family size, so once that product
    passes ``alpha`` the corrected test cannot flag anything — for any candidate, the
    known-bad control included.

    **This is computable from a plan alone, and on 2026-09-11 nobody computed it.** A
    night ran at 100 splits, ``K <= 99`` and a family of 65 checks per grid cell, where
    the corrected floors are 0.64 and 1.00; every corrected rate was therefore zero by
    construction, and the screen's own positive control could not have fired. Two
    murderboard rounds on that plan missed it, because no role computes forward from
    declared parameters to the resolution they buy. Hence a function, so that the next
    design is refused rather than reviewed.

    Returns the floors, whether each yardstick reaches ``alpha``, and the smallest sample
    that would: ``splits >= ceil(m/alpha - 1)`` and ``draws >= ceil(2m/alpha - 1)``.
    """
    if m <= 0 or n_splits <= 0 or K <= 0:
        raise ValueError("family size, splits and draws must all be positive")
    band_floor = 1.0 / (n_splits + 1)
    paired_floor = 2.0 / (K + 1)
    return {
        "m": int(m), "alpha": float(alpha), "n_splits": int(n_splits), "K": int(K),
        "band_floor": band_floor, "paired_floor": paired_floor,
        "band_floor_holm": min(1.0, band_floor * m),
        "paired_floor_holm": min(1.0, paired_floor * m),
        # A relative tolerance, because the boundary is exactly representable in decimal
        # and not in binary: at m = 13 and 259 splits the product is 13/260 = 0.05, which
        # evaluates to 0.05000000000000001 and would demand a 260th split for nothing.
        "band_reaches": bool(band_floor * m <= alpha * (1 + 1e-9)),
        "paired_reaches": bool(paired_floor * m <= alpha * (1 + 1e-9)),
        "splits_needed": int(np.ceil(m / alpha - 1)),
        "K_needed": int(np.ceil(2 * m / alpha - 1)),
    }


def holm(pvals) -> np.ndarray:
    """Holm step-down adjustment; NaNs pass through and do not count as tests."""
    p = np.asarray(pvals, dtype=float)
    out = np.full(p.shape, np.nan)
    ok = np.flatnonzero(np.isfinite(p))
    m = ok.size
    if m == 0:
        return out
    order = ok[np.argsort(p[ok], kind="stable")]
    running = 0.0
    for i, idx in enumerate(order):
        running = max(running, min(1.0, (m - i) * p[idx]))
        out[idx] = running
    return out


def split_diffs(summaries_by_rec, recs, splits, fs):
    """Per statistic, ``S(A) - S(B)`` over the splits; KS as ``KS(A, B)``."""
    names = stat_names(fs)
    out = {n: [] for n in names}
    out["ks_intervals"] = []
    halves = []
    for a, b in splits:
        sa = _sum_where(summaries_by_rec, recs, a)
        sb = _sum_where(summaries_by_rec, recs, b)
        halves.append((sa, sb))
        va, vb = set_stats(sa, fs), set_stats(sb, fs)
        for n in names:
            out[n].append(va[n][0] - vb[n][0])
        out["ks_intervals"].append(ks_pooled(sa, sb))
    return out, halves


def _sum_where(summaries_by_rec, recs, mice):
    tot = Summary()
    for rec in recs:
        if rec.mouse in mice:
            tot = tot + summaries_by_rec[rec.recording_id]
    return tot


def negative_rates_heldout(halves, fs, *, alpha: float = ALPHA) -> dict:
    """Flag rates when a **real held-out half** is scored as if it were a candidate.

    Band: each split's ``|S(A) - S(B)|`` against the band of the other splits.
    Paired: each ``S(A_j)`` ranked among ``S`` of every other split's halves —
    all of them uniformly random mouse halves, so exchangeable with it. The KS
    statistic has no ROI correspondence across mice, so its paired rate is NaN.
    """
    names = stat_names(fs)
    vals = [(set_stats(a, fs), set_stats(b, fs)) for a, b in halves]
    out = {}
    n = len(halves)
    for nm in names:
        a = np.array([v[0][nm][0] for v in vals])
        b = np.array([v[1][nm][0] for v in vals])
        d = a - b
        band_flags, paired_flags = [], []
        for j in range(n):
            others = np.delete(d, j)
            others = others[np.isfinite(others)]
            if np.isfinite(d[j]) and others.size:
                band_flags.append(abs(d[j]) > np.quantile(np.abs(others), 0.95))
            pool = np.concatenate([np.delete(a, j), np.delete(b, j)])
            p = paired_p(a[j], pool)
            if np.isfinite(p):
                paired_flags.append(p < alpha)
        out[nm] = {"band": float(np.mean(band_flags)) if band_flags else float("nan"),
                   "paired": float(np.mean(paired_flags)) if paired_flags
                   else float("nan"), "n": n}
    ks = np.array([ks_pooled(a, b) for a, b in halves])
    flags = []
    for j in range(n):
        others = np.delete(ks, j)
        others = others[np.isfinite(others)]
        if np.isfinite(ks[j]) and others.size:
            flags.append(ks[j] > np.quantile(others, 0.95))
    out["ks_intervals"] = {"band": float(np.mean(flags)) if flags else float("nan"),
                           "paired": float("nan"), "n": n}
    return out


# ---------------------------------------------------------------------------
# Synthetic recordings with a floor (the exchangeable negative's fresh draws)
# ---------------------------------------------------------------------------

def floor_renewal_trains(counts, n_frames: int, dt: float, f_frames: int, rng):
    """Per-ROI onsets, each ROI's count exactly as given, with a hard floor.

    The hard-core transform: draw ``k`` frames uniformly on
    ``[0, n_frames - (k - 1) f)``, sort, and add ``i * f`` to the ``i``-th. Every
    interval is then at least ``f`` frames, the spacings are exchangeable, and no
    onset is pinned to either edge. Not ``simulate``'s ``_place_renewal``, whose
    overflow rescale lands the last onset exactly on the window's end in about a
    third of ROIs at baseline counts — harmless for the destruction twins, where
    both twins carry it, but an edge pile-up this negative would then measure.
    A count too large for the floor is capped. Used for the exchangeable
    negative's fresh synthetic draws.
    """
    f = max(0, int(f_frames))
    out = []
    for k in counts:
        k = int(k)
        if f > 0:
            k = min(k, max(0, (n_frames - 1) // f + 1))
        if k <= 0:
            out.append(np.zeros(0, np.int64))
            continue
        room = n_frames - (k - 1) * f
        u = np.sort(rng.randint(0, room, size=k)).astype(np.int64)
        out.append(u + f * np.arange(k, dtype=np.int64))
    return out


def negative_rates_synthetic(recs, splits_diff, fs, f_frames: int, *,
                             n_rep: int = 20, n_draws: int = 19,
                             key=("negative",), alpha: float = ALPHA) -> dict:
    """Flag rates when a **fresh synthetic draw** is scored as if it were a candidate.

    For each replicate a synthetic copy of ``recs`` is drawn — every recording's
    own ROI count, per-ROI onset counts and window length, background placed
    with a hard floor ``f_frames`` — and ``n_draws`` fresh copies with the same
    counts and new seeds stand in for a candidate's draws. The fresh copies are
    exchangeable with the base, so any flag is the yardstick's own false-alarm
    rate. Paired: ``paired_p`` below α. Band: the mean fresh-minus-base
    difference outside the **real** band (``splits_diff``), which is the band a
    candidate would be judged against.
    """
    names = stat_names(fs)
    flags = {n: {"band": [], "paired": []} for n in names + ["ks_intervals"]}

    def draw(rep, j):
        g = rng_of(tuple(key) + ("rep", rep, "draw", j))
        return [floor_renewal_trains([v.size for v in rec.trains], rec.n_frames,
                                     rec.dt, f_frames, g) for rec in recs]

    for rep in range(int(n_rep)):
        sets = [draw(rep, j) for j in range(int(n_draws) + 1)]
        sums = []
        for j, tr in enumerate(sets):
            tot = Summary()
            for rec, t in zip(recs, tr):
                # One shuffle seed per recording across the base and its fresh
                # draws, as the candidates get (`serial_rng`).
                tot = tot + summarize(t, (0, rec.n_frames), rec.dt, fs,
                                      rng=rng_of(tuple(key) + ("s", rep,
                                                               rec.recording_id)))
            sums.append(tot)
        vals = [set_stats(s, fs) for s in sums]
        for nm in names:
            base = vals[0][nm][0]
            dr = np.array([v[nm][0] for v in vals[1:]])
            p = paired_p(base, dr)
            if np.isfinite(p):
                flags[nm]["paired"].append(p < alpha)
            sd = np.asarray(splits_diff.get(nm, []), dtype=float)
            sd = sd[np.isfinite(sd)]
            delta = float(np.nanmean(dr) - base) if np.any(np.isfinite(dr)) else np.nan
            if sd.size and np.isfinite(delta):
                flags[nm]["band"].append(abs(delta) > np.quantile(np.abs(sd), 0.95))
        # KS: paired through the reference pool, band through pooled intervals.
        ks_sum = np.zeros(int(n_draws) + 1)
        ks_n = 0
        for i, rec in enumerate(recs):
            s_, n_ = ks_paired(sets[0][i], [sets[j][i] for j in range(1, len(sets))])
            ks_sum += s_
            ks_n += n_
        if ks_n:
            t = ks_sum / ks_n
            p = paired_p(t[0], t[1:])
            if np.isfinite(p):
                flags["ks_intervals"]["paired"].append(p < alpha)
        sd = np.asarray(splits_diff.get("ks_intervals", []), dtype=float)
        sd = sd[np.isfinite(sd)]
        dks = np.nanmean([ks_pooled(sums[0], s) for s in sums[1:]])
        if sd.size and np.isfinite(dks):
            flags["ks_intervals"]["band"].append(dks > np.quantile(sd, 0.95))
    return {nm: {"band": float(np.mean(v["band"])) if v["band"] else float("nan"),
                 "paired": float(np.mean(v["paired"])) if v["paired"] else float("nan"),
                 "n_rep": int(n_rep), "n_draws": int(n_draws)}
            for nm, v in flags.items()}


# ---------------------------------------------------------------------------
# Drawing surrogates — only through the adapter
# ---------------------------------------------------------------------------

@dataclass
class Draws:
    """``K`` surrogate draws of every recording of one stream, for one grid cell."""

    trains: dict                      # recording_id -> list over draws of list of trains
    not_estimable: dict               # recording_id -> bool array, any draw
    unchanged: dict                   # recording_id -> list over draws of bool arrays
    info: list                        # adapter info dicts, one per (recording, draw)
    seconds: float = 0.0
    peak_bytes: int = 0
    n_roi: int = 0
    K: int = 0
    stopped: str = ""


def draw_surrogates(name: str, recs, K: int, cell_id: str, params: dict, *,
                    min_K: int = 19, time_budget: float | None = None,
                    measure_memory: bool = True, progress=None) -> Draws:
    """``K`` draws of every recording through :func:`bugarach.surrogates.generate`.

    Draws are generated draw by draw across all recordings, so a cell that runs
    out of ``time_budget`` seconds keeps every draw it finished: once ``min_K``
    draws are in, the next draw is taken only if the projected time fits. A cell
    that cannot reach ``min_K`` inside the budget is marked ``stopped``. The
    peak traced memory is measured on the first draw (tracemalloc, which numpy
    reports to), because tracing every draw would cost more than the draws.
    """
    from bugarach import surrogates

    d = Draws(trains={r.recording_id: [] for r in recs},
              not_estimable={r.recording_id: np.zeros(len(r.trains), bool)
                             for r in recs},
              unchanged={r.recording_id: [] for r in recs}, info=[])
    d.n_roi = int(sum(len(r.trains) for r in recs))
    t0 = time.perf_counter()
    for k in range(int(K)):
        if time_budget is not None and k >= min_K:
            per = (time.perf_counter() - t0) / k
            if (time.perf_counter() - t0) + per > time_budget:
                d.stopped = f"time budget reached after {k} draws"
                break
        trace = measure_memory and k == 0
        if trace:
            tracemalloc.start()
        for rec in recs:
            # `params` may be a callable of the recording: J is converted to
            # frames with each recording's own frame interval.
            p = params(rec) if callable(params) else params
            res = surrogates.generate(
                name, [np.asarray(v, dtype=np.int64) for v in rec.trains],
                rec.window, (rec.recording_id, rec.stream, cell_id, k), **p)
            d.trains[rec.recording_id].append(
                [np.sort(np.asarray(v, dtype=np.int64)) for v in res.trains])
            d.not_estimable[rec.recording_id] |= np.asarray(res.not_estimable, bool)
            d.unchanged[rec.recording_id].append(np.asarray(res.unchanged, bool))
            d.info.append(dict(res.info or {}))
        if trace:
            _, peak = tracemalloc.get_traced_memory()
            tracemalloc.stop()
            d.peak_bytes = int(peak)
        d.K = k + 1
        if progress is not None:
            # So a caller that has to kill this cell can still say how far it got.
            progress({"draws_completed": d.K,
                      "seconds_generation": time.perf_counter() - t0,
                      "peak_bytes_first_draw": d.peak_bytes, "n_roi": d.n_roi})
        if (time_budget is not None and k + 1 < min_K
                and time.perf_counter() - t0 > time_budget):
            d.stopped = (f"time budget reached after {k + 1} draws, below the "
                         f"minimum {min_K}")
            break
    d.seconds = time.perf_counter() - t0
    return d


def summarize_draws(recs, draws: Draws, fs: dict, cell_id: str):
    """Real and per-draw summaries, with the not-estimable ROIs dropped from both.

    Returns ``(real_by_rec, draws_by_rec)``: dicts keyed by recording id, the
    second holding one :class:`Summary` per draw.
    """
    real, per = {}, {}
    for rec in recs:
        mask = ~draws.not_estimable[rec.recording_id]
        real[rec.recording_id] = summarize(
            rec.trains, rec.window, rec.dt, fs, widths=rec.widths,
            rng=serial_rng(rec), roi_mask=mask)
        per[rec.recording_id] = []
        for k, tr in enumerate(draws.trains[rec.recording_id]):
            wd = None
            if rec.widths is not None:
                # Widths follow onsets by rank where the count held; an ROI whose
                # count changed has no width to assign and is not scored for it.
                wd = [rec.widths[r] if len(tr[r]) == len(rec.trains[r]) else None
                      for r in range(len(tr))]
            per[rec.recording_id].append(summarize(
                tr, rec.window, rec.dt, fs, widths=wd, rng=serial_rng(rec),
                roi_mask=mask))
    return real, per


def serial_rng(rec) -> np.random.RandomState:
    """The serial-dependence shuffles' generator for one recording.

    **The same seed for the real recording and every draw of it** — common random
    numbers. The shuffle null is part of the statistic, so a statistic that
    re-drew its null per draw would score identical trains differently, and a
    surrogate that returns its input would stop reading P = 1."""
    return rng_of((rec.recording_id, rec.stream, "serial-null"))


def score_cell(recs, draws: Draws, fs: dict, cell_id: str, scopes: dict,
               split_info: dict, *, alpha: float = ALPHA) -> dict:
    """Every statistic, every scope, both P-bearing yardsticks, for one cell.

    ``scopes`` maps a scope name (``"all"`` or a group) to its recording ids;
    ``split_info[scope]`` holds that scope's split differences
    (:func:`split_diffs`). Holm is applied per cell, separately for each
    yardstick's family of checks (every statistic in every scope). Returns a
    JSON-ready dict.
    """
    real, per = summarize_draws(recs, draws, fs, cell_id)
    names = stat_names(fs) + ["ks_intervals"]
    K = draws.K
    by_id = {r.recording_id: r for r in recs}
    out = {"scopes": {}, "movement": None}

    # Movement, over every recording and draw.
    mv = [movement(by_id[rid].trains, draws.trains[rid][k], draws.unchanged[rid][k])
          for rid in draws.trains for k in range(len(draws.trains[rid]))]
    if mv:
        out["movement"] = {k: float(np.nanmean([m[k] for m in mv]))
                           for k in mv[0]}

    for scope, ids in scopes.items():
        ids = [i for i in ids if i in real]
        r_sum = Summary()
        for i in ids:
            r_sum = r_sum + real[i]
        d_sums = []
        for k in range(K):
            t = Summary()
            for i in ids:
                t = t + per[i][k]
            d_sums.append(t)
        rv = set_stats(r_sum, fs)
        dv = [set_stats(s, fs) for s in d_sums]
        rows = {}
        for nm in names[:-1]:
            dr = np.array([v[nm][0] for v in dv], dtype=float)
            delta = (float(np.nanmean(dr)) - rv[nm][0]) if np.any(np.isfinite(dr)) \
                else float("nan")
            sd = split_info.get(scope, {}).get(nm, [])
            bd = band(sd)
            rows[nm] = {
                "real": rv[nm][0], "coverage": rv[nm][1],
                "draws_mean": float(np.nanmean(dr)) if np.any(np.isfinite(dr)) else float("nan"),
                "draws_sd": float(np.nanstd(dr)) if np.any(np.isfinite(dr)) else float("nan"),
                "delta": delta,
                "paired_p": paired_p(rv[nm][0], dr),
                "band_p": band_p(delta, sd),
                "band_abs_q95": bd["abs_q95"],
                "band_flag": bool(np.isfinite(delta) and np.isfinite(bd["abs_q95"])
                                  and abs(delta) > bd["abs_q95"]),
            }
        # KS: paired through the reference pool, band through pooled intervals.
        ks_sum = np.zeros(K + 1)
        ks_n = 0
        for i in ids:
            rec = by_id[i]
            s_, n_ = ks_paired(rec.trains, draws.trains[i][:K],
                               roi_mask=~draws.not_estimable[i])
            ks_sum += s_
            ks_n += n_
        t = ks_sum / ks_n if ks_n else np.full(K + 1, np.nan)
        dks = [ks_pooled(r_sum, s) for s in d_sums]
        delta = float(np.nanmean(dks)) if dks and np.any(np.isfinite(dks)) else float("nan")
        sd = np.asarray(split_info.get(scope, {}).get("ks_intervals", []), dtype=float)
        # A half with no interval at all gives a NaN distance; it is not a split
        # difference, so it leaves the band rather than turning its quantile NaN.
        sd = sd[np.isfinite(sd)]
        n_roi_scope = sum(len(by_id[i].trains) for i in ids)
        rows["ks_intervals"] = {
            "real": float(t[0]), "coverage": _ratio(ks_n, n_roi_scope),
            "draws_mean": float(np.nanmean(t[1:])) if K else float("nan"),
            "draws_sd": float(np.nanstd(t[1:])) if K else float("nan"),
            "delta": delta,
            "paired_p": paired_p(float(t[0]), t[1:]),
            "band_p": float((1 + np.sum(np.asarray(sd) >= delta)) / (len(sd) + 1))
            if len(sd) and np.isfinite(delta) else float("nan"),
            "band_abs_q95": float(np.quantile(sd, 0.95)) if len(sd) else float("nan"),
            "band_flag": bool(len(sd) and np.isfinite(delta)
                              and delta > np.quantile(sd, 0.95)),
        }
        out["scopes"][scope] = rows

    for yard in ("paired_p", "band_p"):
        keys = [(sc, nm) for sc in out["scopes"] for nm in out["scopes"][sc]]
        adj = holm([out["scopes"][sc][nm][yard] for sc, nm in keys])
        for (sc, nm), a in zip(keys, adj):
            out["scopes"][sc][nm][yard + "_holm"] = float(a)
    out["K"] = K
    return out


# ---------------------------------------------------------------------------
# Destruction
# ---------------------------------------------------------------------------

def destruction_twins(n_roi: int, n_frames: int, dt: float, f_frames: int,
                      counts, participation: float, *, n_events: int | None = None,
                      seed: int = 0):
    """A planted recording and its unplanted twin, both with a hard floor.

    Built by :func:`bugarach.simulate.simulate_coordination` in its floor mode:
    the same seed with and without planted events, so the backgrounds agree
    except where a planted onset **replaced** a background one. Planted jitter
    is one frame. Returns ``(planted, unplanted, ground_truth)``, trains in
    frames.
    """
    from bugarach.simulate import simulate_coordination

    T = n_frames * dt
    if n_events is None:
        n_events = max(5, int(T // 60.0))
    common = dict(duration_sec=T, n_roi=int(n_roi), bg_floor_sec=f_frames * dt,
                  bg_roi_counts=np.asarray(counts, dtype=np.int64),
                  jitter_sec=DESTRUCTION_JITTER_FRAMES * dt, grid_sec=dt,
                  min_sep_sec=max(15.0, 4 * f_frames * dt), margin_sec=5.0,
                  seed=int(seed))
    sp, gt = simulate_coordination(participation=(float(participation),),
                                   n_per_level=(int(n_events),), **common)
    su, _ = simulate_coordination(participation=(float(participation),),
                                  n_per_level=(0,), **common)

    def fr(s):
        # Onsets at or past the window's end are dropped, not clipped:
        # `_place_renewal` lands some ROIs' last onset exactly on the end, and
        # clipping would stack them in the last frame — a coincidence neither
        # twin was meant to carry.
        st = s.streams["events"]
        out = []
        for v in st.locs:
            f_ = to_frames(v, dt)
            out.append(f_[(f_ >= 0) & (f_ < n_frames)])
        return out

    return fr(sp), fr(su), gt


def coact_excess(trains, n_frames: int, dt: float, *, min_rois=None,
                 n_surrogates: int = 200, seed: int = 20260722) -> dict:
    """The assessor's selection-corrected coactivity excess, ±2 frames, all ROIs.

    Runs :func:`bugarach.assess.assess_coactivity` itself on the trains, with
    the whole window, a bin of ``2 * DESTRUCTION_HALF_WINDOW_FRAMES + 1`` frames
    and every K of its default scan (K is a scan, never a choice). Unchanged
    ROIs are included — the assessor counts every ROI it is given.
    Returns ``{K: coact_excess}``.
    """
    from bugarach.assess import DEFAULT_MIN_ROIS, assess_coactivity
    from bugarach.io import slice_from_events

    s = slice_from_events({"events": [np.asarray(v, float) * dt for v in trains]},
                          dt=dt, slice_id="twin")
    res = assess_coactivity(
        s, stream="events", window=(0.0, n_frames * dt),
        min_rois=tuple(min_rois or DEFAULT_MIN_ROIS),
        bin_width_sec=(2 * DESTRUCTION_HALF_WINDOW_FRAMES + 1) * dt,
        n_surrogates=int(n_surrogates), rng_seed=int(seed), region_min_sec=0.0)
    return {int(a.min_rois): float(a.coact_excess) for a in res}


def destruction(name: str, params: dict, twins, n_frames: int, dt: float, *,
                n_draws: int, cell_id: str, stream: str = "",
                freeze_half: bool = False, n_assess_surrogates: int = 200,
                min_rois=None) -> dict:
    """Does the surrogate remove planted cross-ROI coordination?

    ``twins`` is ``{participation: (planted, unplanted)}``. For each draw both
    twins go through :func:`bugarach.surrogates.generate` with the **same key**,
    so the two differ only in what was planted, and each is scored with
    :func:`coact_excess`. ``freeze_half`` restores a seeded half of the ROIs to
    their input after the surrogate — the graded control.

    Per participation and K: the excess before any surrogate, the mean after it
    for each twin, the **retained** share ``(E_planted - E_unplanted) after /
    before``, and the share of draw pairs where the planted twin's excess tops
    the unplanted one's. ``before <= 0`` means the planted events are invisible
    to the measure at that K, and the row says so rather than dividing.
    """
    from bugarach import surrogates

    out = {}
    for p, (pl, un) in twins.items():
        b_pl = coact_excess(pl, n_frames, dt, min_rois=min_rois,
                            n_surrogates=n_assess_surrogates)
        b_un = coact_excess(un, n_frames, dt, min_rois=min_rois,
                            n_surrogates=n_assess_surrogates)
        e_pl = {K: [] for K in b_pl}
        e_un = {K: [] for K in b_pl}
        for k in range(int(n_draws)):
            key = (f"twin-{p}", stream, cell_id, k)
            got = []
            for tr in (pl, un):
                res = surrogates.generate(name, [np.asarray(v, np.int64) for v in tr],
                                          (0, n_frames), key, **params)
                st = [np.sort(np.asarray(v, np.int64)) for v in res.trains]
                if freeze_half:
                    keep = rng_of(("freeze-half", p, k)).permutation(len(tr))[: len(tr) // 2]
                    for r in keep:
                        st[r] = np.asarray(tr[r], np.int64)
                got.append(st)
            s_pl = coact_excess(got[0], n_frames, dt, min_rois=min_rois,
                                n_surrogates=n_assess_surrogates)
            s_un = coact_excess(got[1], n_frames, dt, min_rois=min_rois,
                                n_surrogates=n_assess_surrogates)
            for K in e_pl:
                e_pl[K].append(s_pl[K])
                e_un[K].append(s_un[K])
        rows = {}
        for K in e_pl:
            before = b_pl[K] - b_un[K]
            a, b = np.asarray(e_pl[K]), np.asarray(e_un[K])
            after = float(np.mean(a) - np.mean(b)) if a.size else float("nan")
            rows[str(K)] = {
                "before_planted": b_pl[K], "before_unplanted": b_un[K],
                "before": before,
                "after_planted_mean": float(np.mean(a)) if a.size else float("nan"),
                "after_unplanted_mean": float(np.mean(b)) if b.size else float("nan"),
                "after_planted_sd": float(np.std(a)) if a.size else float("nan"),
                "after_unplanted_sd": float(np.std(b)) if b.size else float("nan"),
                "after": after,
                "retained": (after / before) if before > 0 else float("nan"),
                "planted_visible": bool(before > 0),
                "pair_share_planted_above": float(np.mean(a[:, None] > b[None, :]))
                if a.size and b.size else float("nan"),
            }
        out[str(p)] = rows
    return out
