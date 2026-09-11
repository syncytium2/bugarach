"""Operational-time dither — Louis, Gerstein, Grün & Diesmann 2010, on frames.

Louis et al. (*Frontiers in Computational Neuroscience* 4:127, 2010) map a spike
train to **operational time**, τ(t) = ∫λ, in which the process runs at unit
rate; dither each spike uniformly there; and map back. Their eq. 8: a uniform
dither in operational time is, in real time, a dither whose density follows the
rate profile, so it keeps the estimated rate profile — onsets in a busy stretch
move a little, onsets in a quiet one move far.

Their rate estimate is a trial-averaged PSTH. This project has no trials: one
ROI's onsets are one realisation. So the rate is estimated from the ROI's **own**
train, and **leave-one-out** — onset *i* is dithered through the rate of the
other onsets, λ₋ᵢ. With its own kernel bump left in, each onset would sit on a
local peak of its own making, the real-time width would shrink around it, and
the surrogate would move everything less than asked.

What this module decides, each stated once:

* **Frames in, frames out.** A train is a sorted int64 array of frame indices;
  a window is ``(start, end)``, half-open. Frame *k* owns the cell
  ``[k - 1/2, k + 1/2)`` and its onset sits at the cell's centre. ``J`` and
  ``bandwidth`` are in **frames** (floats allowed) — the caller converts from
  seconds with the recording's own frame interval.
* **The rate is a Nadaraya–Watson estimate on the frame grid.** At frame *k*,
  λ₋ᵢ(k) = Σ_{j≠i} K(k − t_j) / Σ_{m in window} K(k − m), with K a Gaussian of
  σ = ``bandwidth`` frames. The denominator is the kernel mass that falls
  inside the window, which is :func:`bugarach.detectors.rate.event_rate`'s edge
  divisor correction carried over to a Gaussian: at a boundary the count is
  divided by the truncated kernel, so the rate does not dip there. Units are
  onsets per frame, so its sum over the window is an expected count.
  ``kernel="box"`` instead uses the detector's own estimator,
  :func:`bugarach.detectors.rate.train_rate`, with ``bandwidth`` as its full
  window width in frames.
* **A frame where the other onsets supply less than 10⁻¹² of the kernel sum
  there has no rate.** The leave-one-out sum is the full sum minus the onset's
  own kernel, and below that share the difference is rounding, not rate.
* **Operational time is the running sum of λ₋ᵢ over frames**, linear within a
  frame. A frame whose rate is zero has no operational-time extent and cannot
  be landed in.
* **Width.** Half-width in operational time w = J·N/T (N onsets, window of T
  frames): at the ROI's mean rate N/T, that is a real-time half-width of J.
  ⚠ The leave-one-out rate integrates to about N − 1, not N, so in a flat
  stretch the real-time half-width is J·N/(N − 1) — twice J for a two-onset
  ROI. The plan specifies J·N/T and this follows it; the realised displacement
  is what :func:`displacement_distribution` reports, and what any RMS matching
  should read.
* **Edges reflect.** A draw that leaves ``[0, U_i]`` (U_i the onset's total
  operational time) is folded back in. The process is unit-rate in operational
  time, and a symmetric dither with reflecting walls keeps a uniform density
  uniform, so the edges are neither thinned nor piled and no onset is dropped:
  **the count is exactly preserved.**
* **Not estimable**, returned unchanged: fewer than two onsets — the
  leave-one-out rate is zero everywhere. :func:`operational_time_dither_info`
  says so, and the adapter must not score such an ROI.
* **Degenerate onsets are counted, not hidden.** Where λ₋ᵢ is zero on the
  onset's own frame (a box kernel narrower than the gaps; every other onset
  more than about 7σ away) the onset has no operational-time position of its
  own and is carried to the nearest frame the other onsets do cover — it moves
  even at J = 0. ``info["flat_at_onset"]`` counts them.

Onsets are dithered independently ("in parallel", as Louis et al. do); two may
land in one frame, and the count stays exact. One uniform draw per onset, in
onset order, from the ``RandomState`` passed in.

**Cost.** One ROI's map — each onset's operational time at every frame edge — is
N × (T + 1) float64, built in O(N·T) in blocks of about 32 MB. It is cached per
(train, window, bandwidth, kernel) while it fits a 256 MB budget; then further
draws, and every J, cost O(N log T). A map too big to cache is recomputed on
every call, still in blocks, so memory stays bounded and time is O(N·T) per
draw. Loop draws and J *inside* the ROI and bandwidth, or the cache cannot help.
"""

from __future__ import annotations

from collections import OrderedDict
from dataclasses import dataclass

import numpy as np

KERNELS = ("gaussian", "box")
EDGE_POLICY = "reflect"
NEGLIGIBLE = 1e-12

_CACHE_BYTES = 256 * 2**20   # all cached maps together, and the largest one kept
_CHUNK_BYTES = 32 * 2**20    # one block of rows while building or streaming
_cache: OrderedDict = OrderedDict()
_cache_bytes = 0


def clear_cache() -> None:
    """Drop every cached operational-time map."""
    global _cache_bytes
    _cache.clear()
    _cache_bytes = 0


# ---------------------------------------------------------------- validation


def _validate(train, window) -> tuple[np.ndarray, int, int]:
    a, b = int(window[0]), int(window[1])
    if (a, b) != (window[0], window[1]):
        raise ValueError(f"window must be whole frames, got {window!r}")
    if b <= a:
        raise ValueError(f"window {window!r} is empty: end must exceed start")
    raw = np.asarray(train).ravel()
    if raw.size and not np.all(np.isfinite(raw.astype(float))):
        raise ValueError("train holds a non-finite value")
    frames = raw.astype(np.int64)
    if raw.size and not np.array_equal(frames, raw):
        raise ValueError("train must hold whole frame indices")
    frames = np.sort(frames)
    if frames.size and (frames[0] < a or frames[-1] >= b):
        raise ValueError(
            f"train has onsets outside the window [{a}, {b}): first "
            f"{frames[0]}, last {frames[-1]}. Nothing is dropped silently here; "
            "cut the train to the window before calling.")
    return frames, a, b


def _check_scale(J: float, bandwidth: float) -> None:
    if not (np.isfinite(J) and J >= 0):
        raise ValueError(f"J must be a finite number of frames >= 0, got {J!r}")
    if not (np.isfinite(bandwidth) and bandwidth > 0):
        raise ValueError(
            f"bandwidth must be a finite number of frames > 0, got {bandwidth!r}")


def _check_kernel(kernel: str) -> None:
    if kernel not in KERNELS:
        raise ValueError(f"kernel must be one of {KERNELS}, got {kernel!r}")


def dither_width(n_onsets: int, n_frames: int, J: float) -> float:
    """Half-width of the dither in operational time: J·N/T expected onsets."""
    return float(J) * n_onsets / n_frames


# ---------------------------------------------------------------- the rate


def _chunks(n: int, T: int):
    step = max(1, _CHUNK_BYTES // (8 * (T + 1)))
    for s in range(0, n, step):
        yield np.arange(s, min(n, s + step))


def _kernel_block(rel: np.ndarray, T: int, sigma: float) -> np.ndarray:
    """(len(rel), T): unnormalised Gaussian of each onset at each frame. A
    Nadaraya–Watson ratio cancels the normalising constant."""
    k = np.arange(T, dtype=float)
    return np.exp(-0.5 * ((k[None, :] - rel[:, None]) / sigma) ** 2)


def _gaussian_totals(rel: np.ndarray, T: int, sigma: float):
    """S: every onset's kernel summed per frame. denom: the kernel mass inside
    the window at each frame, Σ_{m=0}^{T-1} K(k − m) — the edge divisor."""
    x = np.arange(-(T - 1), T, dtype=float)
    P = np.concatenate(([0.0], np.cumsum(np.exp(-0.5 * (x / sigma) ** 2))))
    k = np.arange(T)
    denom = P[k + T] - P[k]          # offsets k-(T-1) .. k
    # Row by row, in onset order: a block sum would round differently for each
    # block size, and a map too big to cache must reproduce a cached one.
    S = np.zeros(T)
    for idx in _chunks(rel.size, T):
        for row in _kernel_block(rel[idx], T, sigma):
            S += row
    return S, denom


def _mass_block(rel: np.ndarray, T: int, bandwidth: float, kernel: str,
                S, denom, idx: np.ndarray) -> np.ndarray:
    """(len(idx), T): onset i's leave-one-out rate at each frame, onsets/frame."""
    if kernel == "gaussian":
        W = _kernel_block(rel[idx].astype(float), T, bandwidth)
        loo = S[None, :] - W
        loo[loo <= NEGLIGIBLE * S[None, :]] = 0.0
        return loo / denom[None, :]
    from bugarach.detectors.rate import train_rate

    out = np.empty((idx.size, T))
    relf = rel.astype(float)
    for r, i in enumerate(idx):
        _, y = train_rate(np.delete(relf, i), (0.0, float(T - 1)), bandwidth, 1.0)
        out[r] = y
    return np.maximum(out, 0.0)


def _cum_block(masses: np.ndarray) -> np.ndarray:
    return np.concatenate((np.zeros((masses.shape[0], 1)),
                           np.cumsum(masses, axis=1)), axis=1)


def _loo_masses(rel, T: int, bandwidth: float, kernel: str = "gaussian"):
    """(N, T) leave-one-out rate for every onset — the whole matrix at once,
    for inspection and tests; the dither itself never holds it unless cached."""
    rel = np.asarray(rel, dtype=float)
    S = denom = None
    if kernel == "gaussian":
        S, denom = _gaussian_totals(rel, T, float(bandwidth))
    return _mass_block(rel, T, float(bandwidth), kernel, S, denom,
                       np.arange(rel.size))


@dataclass(frozen=True)
class _OpMap:
    rel: np.ndarray            # (N,) int64 onset frames relative to the window
    T: int
    bandwidth: float
    kernel: str
    S: np.ndarray | None       # gaussian: all onsets' kernels summed per frame
    denom: np.ndarray | None   # gaussian: in-window kernel mass per frame
    pos: np.ndarray            # (N,) each onset's own operational-time position
    total: np.ndarray          # (N,) U_i, each onset's total operational time
    flat: np.ndarray           # (N,) bool: zero rate on the onset's own frame
    cum: np.ndarray | None     # (N, T+1) cell-edge operational time, if cached

    @property
    def nbytes(self) -> int:
        n = self.pos.nbytes * 3 + self.rel.nbytes
        for a in (self.S, self.denom, self.cum):
            n += 0 if a is None else a.nbytes
        return n


def _rows(m: _OpMap, idx: np.ndarray) -> np.ndarray:
    """(len(idx), T+1): the onsets' operational time at every frame edge."""
    if m.cum is not None:
        return m.cum[idx]
    return _cum_block(_mass_block(m.rel, m.T, m.bandwidth, m.kernel,
                                  m.S, m.denom, idx))


def _op_map(frames: np.ndarray, a: int, b: int, bandwidth: float,
            kernel: str) -> _OpMap:
    global _cache_bytes
    _check_kernel(kernel)
    key = (frames.tobytes(), a, b, float(bandwidth), kernel)
    hit = _cache.get(key)
    if hit is not None:
        _cache.move_to_end(key)
        return hit
    T, N = b - a, frames.size
    rel = frames - a
    S = denom = None
    if kernel == "gaussian":
        S, denom = _gaussian_totals(rel.astype(float), T, float(bandwidth))
    keep = N * (T + 1) * 8 <= _CACHE_BYTES
    cum = np.empty((N, T + 1)) if keep else None
    pos, total = np.empty(N), np.empty(N)
    flat = np.zeros(N, dtype=bool)
    for idx in _chunks(N, T):
        masses = _mass_block(rel, T, float(bandwidth), kernel, S, denom, idx)
        rows = _cum_block(masses)
        r = np.arange(idx.size)
        own = masses[r, rel[idx]]
        pos[idx] = rows[r, rel[idx]] + own / 2.0
        total[idx] = rows[:, -1]
        flat[idx] = own <= 0.0
        if keep:
            cum[idx] = rows
    m = _OpMap(rel=rel, T=T, bandwidth=float(bandwidth), kernel=kernel, S=S,
               denom=denom, pos=pos, total=total, flat=flat, cum=cum)
    if m.nbytes <= _CACHE_BYTES:
        _cache[key] = m
        _cache_bytes += m.nbytes
        while _cache_bytes > _CACHE_BYTES and len(_cache) > 1:
            _, old = _cache.popitem(last=False)
            _cache_bytes -= old.nbytes
    return m


# ---------------------------------------------------------------- placing


def _fold(y: np.ndarray, U: np.ndarray) -> np.ndarray:
    """Reflect into [0, U]: period 2U, mirrored on the second half."""
    r = np.mod(y, 2.0 * U)
    return np.where(r > U, 2.0 * U - r, r)


def _cell(cum_row: np.ndarray, u: float) -> int:
    """The frame (window-relative) whose operational-time extent holds u.

    Half-open cells [cum[k], cum[k+1]); a zero-extent frame is never chosen.
    u == U (the far wall, reachable only through rounding) goes to the last
    frame with extent."""
    T = cum_row.size - 1
    k = int(np.searchsorted(cum_row, u, side="right")) - 1
    if 0 <= k < T and cum_row[k + 1] > cum_row[k]:
        return k
    pos = np.flatnonzero(np.diff(cum_row) > 0)
    if k < 0:
        return int(pos[0])
    before = pos[pos <= min(k, T - 1)]
    return int(before[-1]) if before.size else int(pos[0])


def _not_estimable(frames: np.ndarray) -> str:
    if frames.size < 2:
        return "fewer than two onsets: the leave-one-out rate is zero"
    return ""


def operational_time_dither_info(
    train, window, J: float, bandwidth: float, rng, *, kernel: str = "gaussian",
) -> tuple[np.ndarray, dict]:
    """:func:`operational_time_dither` plus what the adapter needs to report.

    Returns ``(frames, info)``. ``info`` carries ``estimable`` and its
    ``reason``; ``n``, ``T``, ``J``, ``bandwidth``, ``kernel``, ``edge``;
    ``width_op`` (w = J·N/T); ``flat_at_onset`` (onsets with no rate on their
    own frame, which move even at J = 0); and ``displacement`` — each onset's
    move in frames, in onset order, before the output is sorted."""
    _check_scale(J, bandwidth)
    _check_kernel(kernel)
    frames, a, b = _validate(train, window)
    T, N = b - a, frames.size
    w = dither_width(N, T, J)
    info = {"n": int(N), "T": T, "J": float(J), "bandwidth": float(bandwidth),
            "kernel": kernel, "edge": EDGE_POLICY, "width_op": w,
            "flat_at_onset": 0, "estimable": False, "reason": "",
            "displacement": np.zeros(N, dtype=np.int64)}
    why = _not_estimable(frames)
    if why:
        info["reason"] = why
        return frames.copy(), info
    m = _op_map(frames, a, b, bandwidth, kernel)
    info["flat_at_onset"] = int(m.flat.sum())
    xi = rng.uniform(-w, w, size=N)
    new = np.empty(N, dtype=np.int64)
    for idx in _chunks(N, T):
        rows = _rows(m, idx)
        u = _fold(m.pos[idx] + xi[idx], m.total[idx])
        for r, i in enumerate(idx):
            new[i] = _cell(rows[r], u[r])
    new += a
    info["estimable"] = True
    info["displacement"] = new - frames
    return np.sort(new), info


def operational_time_dither(
    train, window, J: float, bandwidth: float, rng, *, kernel: str = "gaussian",
) -> np.ndarray:
    """One operational-time surrogate of one ROI's train, as sorted int64 frames.

    ``train``: frame indices inside ``window = (start, end)``, half-open.
    ``J``: dither half-width in frames at the ROI's mean rate.
    ``bandwidth``: the rate kernel's σ in frames (``kernel="box"``: full width).
    ``rng``: a ``numpy.random.RandomState``; one uniform per onset.

    A train the method cannot estimate comes back unchanged — ask
    :func:`operational_time_dither_info` whether it was."""
    return operational_time_dither_info(train, window, J, bandwidth, rng,
                                        kernel=kernel)[0]


# ---------------------------------------------------------------- distribution


@dataclass
class DisplacementDistribution:
    """Exact distribution of one surrogate's per-onset moves, in frames.

    ``offsets`` and ``pmf`` are the pooled distribution: the probability that
    an onset, chosen uniformly among the train's onsets, moves by each offset.
    ``per_onset_rms`` is each onset's own RMS displacement; ``rms`` is the
    pooled one, sqrt(mean over onsets of E[d²]) — the number to hold against
    J when candidates are matched by RMS displacement. ``p_unmoved`` is the
    pooled probability of staying on the same frame."""

    offsets: np.ndarray
    pmf: np.ndarray
    per_onset_rms: np.ndarray
    rms: float
    mean_abs: float
    p_unmoved: float
    width_op: float
    estimable: bool
    reason: str = ""


def _cell_probabilities(cum: np.ndarray, pos: float, U: float,
                        w: float) -> np.ndarray:
    """(T,) probability that an onset at operational time ``pos`` lands on each
    window frame, given its row ``cum`` of cell-edge operational times.

    The dithered operational time is uniform on [pos - w, pos + w], folded into
    [0, U]. A frame's probability is the length of that interval whose fold
    falls in the frame's extent [c0, c1), over 2w; the fold's preimages of
    [c0, c1) are [2kU + c0, 2kU + c1] and [2kU - c1, 2kU - c0] for every
    integer k."""
    T = cum.size - 1
    if w <= 0:
        p = np.zeros(T)
        p[_cell(cum, pos)] = 1.0
        return p
    lo, hi = pos - w, pos + w
    c0, c1 = cum[:-1], cum[1:]
    acc = np.zeros(T)
    for k in range(int(np.floor((lo - U) / (2 * U))),
                   int(np.ceil((hi + U) / (2 * U))) + 1):
        base = 2.0 * k * U
        for s0, s1 in ((base + c0, base + c1), (base - c1, base - c0)):
            acc += np.clip(np.minimum(s1, hi) - np.maximum(s0, lo), 0.0, None)
    return acc / (2.0 * w)


def displacement_distribution(
    train, window, J: float, bandwidth: float, *, kernel: str = "gaussian",
) -> DisplacementDistribution:
    """The exact displacement distribution, in frames, of
    :func:`operational_time_dither` on this train — no sampling.

    It is what one draw is a sample of: the same rate, operational time, width,
    reflection and frame assignment. A train the method cannot estimate comes
    back ``estimable=False`` with a point mass at zero."""
    _check_scale(J, bandwidth)
    _check_kernel(kernel)
    frames, a, b = _validate(train, window)
    T, N = b - a, frames.size
    w = dither_width(N, T, J)
    why = _not_estimable(frames)
    if why:
        return DisplacementDistribution(
            offsets=np.zeros(1, dtype=np.int64), pmf=np.ones(1),
            per_onset_rms=np.zeros(N), rms=0.0, mean_abs=0.0, p_unmoved=1.0,
            width_op=w, estimable=False, reason=why)
    m = _op_map(frames, a, b, bandwidth, kernel)
    pooled = np.zeros(2 * T - 1)
    per_rms = np.empty(N)
    frame_d = np.arange(T)
    for idx in _chunks(N, T):
        rows = _rows(m, idx)
        for r, i in enumerate(idx):
            p = _cell_probabilities(rows[r], m.pos[i], m.total[i], w)
            p = p / p.sum()
            d = frame_d - m.rel[i]
            per_rms[i] = np.sqrt(np.sum(p * d.astype(float) ** 2))
            pooled[d + (T - 1)] += p
    pooled /= N
    offsets = np.arange(-(T - 1), T, dtype=np.int64)
    nz = np.flatnonzero(pooled > 0)
    offsets, pooled = offsets[nz[0]:nz[-1] + 1], pooled[nz[0]:nz[-1] + 1]
    return DisplacementDistribution(
        offsets=offsets, pmf=pooled, per_onset_rms=per_rms,
        rms=float(np.sqrt(np.mean(per_rms ** 2))),
        mean_abs=float(np.sum(pooled * np.abs(offsets))),
        p_unmoved=float(pooled[offsets == 0].sum()),
        width_op=w, estimable=True)
