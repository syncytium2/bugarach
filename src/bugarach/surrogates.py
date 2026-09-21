"""Surrogate generators for the surrogate screen — candidates, controls, and the Elephant adapter.

A **surrogate** is a resampled copy of a recording that keeps each ROI's own timing
and destroys the timing *between* ROIs. The screen
(``docs/proposals/2026-09-10-surrogate-evaluation-overnight.md``) measures twelve
candidate generators and six known-bad controls on the same data, and this module
is the one place all eighteen are built, to one interface.

The interface
-------------
- A **train** is a sorted ``int64`` array of frame indices for one ROI; a stream of a
  recording is a list of trains, one per ROI. A frame index is the nearest whole
  number to ``t / dt``, ``dt`` being that recording's own frame interval.
- A **window** is ``(start_frame, end_frame)``, half-open. Onsets outside it are not
  part of the surrogate; how many were left out is ``info["outside_window"]``.
- **Every parameter is in frames** — ``J``, ``f``, ``sigma``, ``bandwidth``,
  ``analysis_window``. The caller converts seconds with the recording's own ``dt``.
- ``generate(name, trains, window, key, **params)`` returns a :class:`SurrogateResult`.
  ``key`` is ``(recording_id, stream, cell_id, draw)`` and becomes a seed through
  ``zlib.crc32`` of its ``repr`` (:func:`seed_of`). Generators that treat ROIs
  independently seed each ROI from ``key + (name, roi)``, so one ROI's surrogate
  does not depend on how many ROIs precede it. The circular shift, the per-window
  circular shift and the shipped dither use one generator for all ROIs, because
  that is how the code they reproduce draws.

Elephant, and what the adapter corrects
----------------------------------------
Seven candidates and four controls come from Elephant 1.2.1 (the optional extra
``surrogates``). Running it at this project's timescale found defects that fail
silently; each is handled here and each has a test in ``tests/test_surrogates.py``:

- **Floating-point time.** ``bin_shuffling`` floor-divides seconds and puts on-grid
  onsets a frame early; ``jitter_spikes`` counts a window's start twice and crashes
  or misplaces onsets whenever the start is not zero. So **every Elephant call runs
  in frame units on a window starting at zero**: an onset in frame ``k`` of the
  window is handed over at ``k + 0.5``, the centre of its frame, and whatever comes
  back maps to frame ``floor(x)``. Frame ``k`` owns ``[k, k + 1)``, so the window
  ``[0, L)`` maps onto frames ``0 .. L-1`` exactly, with no rounding edge case at
  either end, and a whole-frame dead time survives the mapping unchanged.
- **JointISI fails silently three ways**: fewer than three onsets come back
  unchanged; an interval pair beyond its truncation, or a bin wider than the
  dither, falls back to plain uniform dither; a small smoothing width runs and
  moves nothing. All three are counted per ROI, and an ROI that hits any of them is
  ``not_estimable``. Its memory grows with the square of its bin count, so an ROI
  whose histogram would exceed ``max_bytes`` is declared *intractable* rather than
  run.
- **ISI dither smooths an integer histogram** (found while building this adapter,
  2026-09-11; not in the plan's list). With ``isi_dithering=True`` and no square
  root, ``JointISI`` builds the histogram as an integer outer product and writes the
  Gaussian-smoothed values back into it, truncating them to whole counts. Sparse
  regions become exactly zero, and the draw falls back to uniform dither there —
  on dense synthetic trains, most ROIs. The adapter hands ``JointISI`` a float
  histogram smoothed by the same rule (:func:`_float_smoothed_histogram`); the
  joint path already builds floats and is left to Elephant.
- **``dither_spikes``' dead time is capped** at each train's own shortest interval,
  and a zero dead time silently runs plain uniform dither. The dead time in effect
  is reported per ROI, and zero is refused.
- **``bin_shuffling`` drops edge onsets**: its last window is permuted as if it were
  full, so onsets there can land past the window's end. The last partial window is
  handled here instead, with the same permutation rule.
- **No seed.** Elephant draws from numpy's and Python's global generators. Both are
  seeded from the key immediately before each call, and restored afterwards, so
  nothing outside this module sees its state change.
- **Millisecond defaults** (2 ms smoothing, 15 ms dither, 4 ms dead time). Every
  Elephant call goes through :func:`_call_explicit`, which refuses a call that
  leaves any keyword parameter to its default.

Our own randomness uses ``np.random.RandomState`` — sapper SAP002 blocks the newer
generator in ``src/``, because the MATLAB parity fixtures depend on the twister.
"""

from __future__ import annotations

import inspect
import math
import random
import zlib
from collections import OrderedDict
from contextlib import contextmanager
from dataclasses import dataclass, field

import numpy as np

from bugarach.assess import circular_shift_trains
from bugarach.graph import jitter_trains

#: JointISI returns any train with fewer onsets than this unchanged. Mirrors
#: ``elephant.spike_train_surrogates.JointISI.MIN_SPIKES``; a test holds them equal.
JISI_MIN_ONSETS = 3

#: The memory a single ROI's joint-ISI histogram may take before the ROI is
#: declared intractable (the plan's 4 GB).
JISI_MAX_BYTES = 4e9

#: Cumulative tables kept between draws of the same ROI and parameters. They do not
#: depend on the draw, and building them is the slow part of joint-ISI dither.
_JISI_CACHE_BYTES = 1e9


@dataclass
class SurrogateResult:
    """One surrogate of one stream of one recording, over one generation window."""

    trains: list
    """One sorted ``int64`` array of frame indices per ROI, inside the window."""
    unchanged: np.ndarray
    """Per ROI: the surrogate train is identical to the in-window input train."""
    not_estimable: np.ndarray
    """Per ROI: the generator could not do what it claims (JointISI's silent
    failures, an intractable histogram). Never score such an ROI as preserving
    anything — it preserves by not having been touched."""
    info: dict = field(default_factory=dict)
    """Generator name, parameters, seed, per-ROI counters (dropped, clipped,
    dead time in effect, fallbacks …). Array-valued entries are one per ROI."""


# ---------------------------------------------------------------- seeding, calls

def seed_of(key) -> int:
    """The seed a key stands for: ``zlib.crc32`` of its ``repr``, a 32-bit int."""
    return zlib.crc32(repr(key).encode("utf-8"))


def _roi_seed(key, name: str, roi: int, *extra) -> int:
    return seed_of((*tuple(key), name, int(roi), *extra))


@contextmanager
def _seeded_globals(seed: int):
    """Seed numpy's and Python's global generators, restoring both afterwards."""
    np_state = np.random.get_state()
    py_state = random.getstate()
    np.random.seed(int(seed))
    random.seed(int(seed))
    try:
        yield
    finally:
        np.random.set_state(np_state)
        random.setstate(py_state)


def _call_explicit(fn, *args, **kwargs):
    """Call an Elephant function only if every one of its parameters is given.

    Elephant's defaults are in milliseconds and would be wrong here by three
    orders of magnitude; one reached silently is a surrogate that looks fine and is
    not. Positional or keyword both count as given.
    """
    sig = inspect.signature(fn)
    bound = sig.bind(*args, **kwargs)
    missing = [p for p in sig.parameters if p != "self" and p not in bound.arguments]
    if missing:
        raise TypeError(f"{getattr(fn, '__qualname__', fn)}: parameters left to "
                        f"Elephant's defaults: {missing}")
    return fn(*args, **kwargs)


def _elephant():
    try:
        import elephant.spike_train_surrogates as ss
        import neo
        import quantities as pq
    except ImportError as exc:  # pragma: no cover - exercised only without the extra
        raise ImportError("this surrogate needs Elephant: "
                          "pip install -e '.[surrogates]'") from exc
    return ss, neo, pq


def _spiketrain(pos, t_stop, t_start=0.0):
    """A neo train in frame units (Elephant's ``s`` stands for one frame here)."""
    _, neo, pq = _elephant()
    return neo.SpikeTrain(np.asarray(pos, dtype=float) * pq.s,
                          t_start=float(t_start) * pq.s, t_stop=float(t_stop) * pq.s)


def _frames(pq_value):
    _, _, pq = _elephant()
    return float(pq_value) * pq.s


# ---------------------------------------------------------------- frame mapping

def _window(window) -> tuple[int, int]:
    s, e = int(window[0]), int(window[1])
    if e <= s:
        raise ValueError(f"empty window {window!r}")
    return s, e


def _in_window(train, s: int, e: int) -> np.ndarray:
    t = np.asarray(train, dtype=np.int64).ravel()
    return np.sort(t[(t >= s) & (t < e)])


def _centred(rel: np.ndarray) -> np.ndarray:
    """Frame ``k`` handed to Elephant at the centre of its frame, ``k + 0.5``."""
    return rel.astype(float) + 0.5


def _back(x, L: int, edge: str) -> tuple[np.ndarray, int]:
    """Continuous frame-unit positions back to frames ``0 .. L-1``.

    ``edge`` says what happens to a position outside ``[0, L)``: ``drop`` removes
    it, ``clip`` moves it to the nearest end frame, ``wrap`` takes it modulo ``L``.
    Returns the frames and how many positions were dropped or clipped.
    """
    k = np.floor(np.asarray(x, dtype=float)).astype(np.int64)
    out = (k < 0) | (k >= L)
    n = int(out.sum())
    if edge == "drop":
        k = k[~out]
    elif edge == "clip":
        k = np.clip(k, 0, L - 1)
    elif edge == "wrap":
        k = np.mod(k, L)
    else:  # pragma: no cover
        raise ValueError(edge)
    return np.sort(k), n


def _positive(name: str, v) -> float:
    v = float(v)
    if not (np.isfinite(v) and v > 0):
        raise ValueError(f"{name} must be a positive number of frames, got {v!r}")
    return v


def _dead_time(f) -> int:
    """The provisional dead time *f*: whole frames, and never zero.

    Zero is refused because Elephant's ``dither_spikes`` tests the dead time for
    truth, so a zero silently runs plain uniform dither under UDD's name.
    """
    v = float(f)
    if not np.isfinite(v) or v <= 0:
        raise ValueError(f"dead time f must be a positive whole number of frames; "
                         f"got {f!r} (zero would silently run plain uniform dither)")
    if v != round(v):
        raise ValueError(f"dead time f must be whole frames, got {f!r}")
    return int(round(v))


def _result(name, ins, outs, s, e, *, params, seed, per_roi=None,
            not_estimable=None, n_outside=0, extra=None) -> SurrogateResult:
    trains = [np.asarray(o, dtype=np.int64) + s for o in outs]
    unchanged = np.array([np.array_equal(a, b) for a, b in zip(ins, outs)], dtype=bool)
    n = len(ins)
    ne = (np.zeros(n, dtype=bool) if not_estimable is None
          else np.asarray(not_estimable, dtype=bool))
    info = {"generator": name, "params": dict(params), "window": (s, e),
            "seed": seed, "outside_window": int(n_outside),
            "n_in": np.array([a.size for a in ins], dtype=np.int64),
            "n_out": np.array([o.size for o in outs], dtype=np.int64)}
    for k, v in (per_roi or {}).items():
        info[k] = np.asarray(v)
    info.update(extra or {})
    return SurrogateResult(trains=trains, unchanged=unchanged, not_estimable=ne, info=info)


def _prepare(trains, window):
    s, e = _window(window)
    raw = [np.asarray(t, dtype=np.int64).ravel() for t in trains]
    ins = [_in_window(t, s, e) - s for t in raw]
    n_outside = sum(r.size for r in raw) - sum(i.size for i in ins)
    return s, e, e - s, ins, n_outside


def _tiles(L: int, width) -> list[tuple[int, int]]:
    """Consecutive analysis windows of ``width`` frames from the window start; the
    last, shorter one is its own window."""
    w = int(round(_positive("analysis_window", width)))
    return [(a, min(a + w, L)) for a in range(0, L, w)]


# ---------------------------------------------------------------- candidates

def uniform_dither(trains, window, key, *, J):
    """UD: each onset moved uniformly within ±J; onsets pushed out are dropped."""
    name = "uniform_dither"
    J = _positive("J", J)
    ss, _, _ = _elephant()
    s, e, L, ins, n_out = _prepare(trains, window)
    outs, dropped = [], []
    for r, t in enumerate(ins):
        if t.size == 0:
            outs.append(t.copy()); dropped.append(0); continue
        with _seeded_globals(_roi_seed(key, name, r)):
            sur = _call_explicit(ss.dither_spikes, _spiketrain(_centred(t), L),
                                 dither=_frames(J), n_surrogates=1, decimals=None,
                                 edges=True, refractory_period=None)[0]
        k, n = _back(sur.magnitude, L, "drop")
        outs.append(k); dropped.append(n + (t.size - sur.magnitude.size))
    return _result(name, ins, outs, s, e, params={"J": J}, seed=seed_of(key),
                   per_roi={"dropped": dropped}, n_outside=n_out)


def shipped_dither(trains, window, key, *, J):
    """The shipped dither, generated exactly as ``modularity_vs_null`` generates it.

    Inactive ROIs (no onset in the half-open window) are dropped before the draw;
    ``graph.jitter_trains`` moves each onset uniformly in ±J and wraps inside the
    window, drawing from one ``RandomState`` across the active ROIs in order. The
    wrap maps to frames modulo the window, so an onset rounded onto the end frame
    comes back at the start — the seam this generator is known for.
    """
    name = "shipped_dither"
    J = _positive("J", J)
    s, e, L, ins, n_out = _prepare(trains, window)
    rng = np.random.RandomState(seed_of(key))
    active = [r for r, t in enumerate(ins) if t.size > 0]
    moved = jitter_trains([ins[r].astype(float) + s for r in active], J,
                          float(s), float(e), rng)
    outs = [t.copy() for t in ins]
    for r, x in zip(active, moved):
        outs[r] = np.sort(np.mod(np.floor(np.asarray(x) - s + 0.5).astype(np.int64), L))
    return _result(name, ins, outs, s, e, params={"J": J}, seed=seed_of(key),
                   n_outside=n_out, extra={"n_active": len(active)})


def dead_time_dither(trains, window, key, *, J, f):
    """UDD: as UD, keeping each onset at least the dead time from its neighbours.

    Elephant caps the dead time at the ROI's own shortest interval, so the dead
    time *in effect* is reported per ROI, and ``dead_time_capped`` marks the ROIs
    where it is below *f*. Never drops an onset.
    """
    name = "dead_time_dither"
    J = _positive("J", J)
    f = _dead_time(f)
    ss, _, _ = _elephant()
    s, e, L, ins, n_out = _prepare(trains, window)
    outs, in_effect, clipped = [], [], []
    for r, t in enumerate(ins):
        eff = float(np.min(np.diff(t), initial=f)) if t.size else float(f)
        in_effect.append(eff)
        if t.size == 0:
            outs.append(t.copy()); clipped.append(0); continue
        with _seeded_globals(_roi_seed(key, name, r)):
            sur = _call_explicit(ss.dither_spikes, _spiketrain(_centred(t), L),
                                 dither=_frames(J), n_surrogates=1, decimals=None,
                                 edges=True, refractory_period=_frames(f))[0]
        k, n = _back(sur.magnitude, L, "clip")
        outs.append(k); clipped.append(n)
    in_effect = np.array(in_effect)
    return _result(name, ins, outs, s, e, params={"J": J, "f": f}, seed=seed_of(key),
                   per_roi={"dead_time_in_effect": in_effect,
                            "dead_time_capped": in_effect < f, "clipped": clipped},
                   n_outside=n_out)


def circular_shift(trains, window, key):
    """The assessor's null: each ROI's whole train shifted by one random lag, wrapping.

    Calls :func:`bugarach.assess.circular_shift_trains` — the function
    ``assess_coactivity`` itself calls — with one ``RandomState`` and one uniform
    per ROI, empty ROIs included. The continuous lag maps to a whole-frame lag
    modulo the window.
    """
    name = "circular_shift"
    s, e, L, ins, n_out = _prepare(trains, window)
    rng = np.random.RandomState(seed_of(key))
    shifted = circular_shift_trains([t.astype(float) for t in ins], float(L), rng)
    outs = [np.sort(np.mod(np.floor(np.asarray(x) + 0.5).astype(np.int64), L))
            for x in shifted]
    return _result(name, ins, outs, s, e, params={}, seed=seed_of(key), n_outside=n_out)


def rigid_shift(trains, window, key, *, J):
    """Rigid shift, no wrap: the whole train moved by one offset in ±J; onsets
    pushed out are dropped (Elephant ``dither_spike_train``, ``edges=True``)."""
    name = "rigid_shift"
    J = _positive("J", J)
    ss, _, _ = _elephant()
    s, e, L, ins, n_out = _prepare(trains, window)
    outs, dropped = [], []
    for r, t in enumerate(ins):
        if t.size == 0:
            outs.append(t.copy()); dropped.append(0); continue
        with _seeded_globals(_roi_seed(key, name, r)):
            sur = _call_explicit(ss.dither_spike_train, _spiketrain(_centred(t), L),
                                 shift=_frames(J), n_surrogates=1, decimals=None,
                                 edges=True)[0]
        k, n = _back(sur.magnitude, L, "drop")
        outs.append(k); dropped.append(n + (t.size - sur.magnitude.size))
    return _result(name, ins, outs, s, e, params={"J": J}, seed=seed_of(key),
                   per_roi={"dropped": dropped}, n_outside=n_out)


def pseudo_trials(t: np.ndarray, J: float, f: int) -> np.ndarray:
    """Pseudo-trial label per onset: a new trial starts after any within-ROI
    silence **longer** than ``2J + f`` frames.

    That width is what keeps trials apart: two neighbours each shifted at most J
    towards each other still sit more than *f* apart. The partition is of onsets,
    not of time, so no onset can belong to two trials — Elephant's trial shifting
    duplicates onsets that sit on a trial boundary.
    """
    t = np.asarray(t)
    if t.size == 0:
        return np.zeros(0, dtype=np.int64)
    return np.concatenate([[0], np.cumsum(np.diff(t) > 2 * J + f)]).astype(np.int64)


def trial_shift(trains, window, key, *, J, f):
    """TR-SHIFT, written here: pseudo-trials cut at silences longer than 2J + f,
    each shifted rigidly within ±J, no wrap, onsets pushed out dropped."""
    name = "trial_shift"
    J = _positive("J", J)
    f = _dead_time(f)
    s, e, L, ins, n_out = _prepare(trains, window)
    outs, dropped, n_trials = [], [], []
    for r, t in enumerate(ins):
        if t.size == 0:
            outs.append(t.copy()); dropped.append(0); n_trials.append(0); continue
        lab = pseudo_trials(t, J, f)
        rng = np.random.RandomState(_roi_seed(key, name, r))
        u = rng.random_sample(int(lab[-1]) + 1) * 2 * J - J
        k, n = _back(_centred(t) + u[lab], L, "drop")
        outs.append(k); dropped.append(n); n_trials.append(int(lab[-1]) + 1)
    return _result(name, ins, outs, s, e, params={"J": J, "f": f}, seed=seed_of(key),
                   per_roi={"dropped": dropped, "n_pseudo_trials": n_trials},
                   n_outside=n_out)


# ---------------------------------------------------------------- joint-ISI

_jisi_cache: "OrderedDict[tuple, tuple[object, float]]" = OrderedDict()


def clear_cache() -> None:
    """Drop the joint-ISI tables kept between draws."""
    _jisi_cache.clear()


def jisi_bytes(n_bins: int, max_change_index: int) -> float:
    """Peak memory of one JointISI ``window`` table, in bytes: the cumulative
    table (``n_bins² × (2m+1)``), the padded diagonal cumulatives and the
    histogram's working copies."""
    n, m = int(n_bins), int(max_change_index)
    return 8.0 * (n * n * (2 * m + 1) + n * (n + 2 * m) + 3 * n * n)


def _float_smoothed_histogram(obj) -> np.ndarray:
    """JointISI's histogram as Elephant computes it, but smoothed in floats.

    Elephant's own method is called with smoothing switched off, so the binning,
    the outer product and the square root stay Elephant's; only the smoothing step
    is repeated here, on a float copy, with Elephant's cutoff rule. On the joint
    path, whose histogram is already float, this reproduces Elephant's result
    exactly — a test holds it to that.
    """
    from scipy.ndimage import gaussian_filter

    sigma = obj.sigma
    obj.sigma = 0
    try:
        h = type(obj).joint_isi_histogram(obj)
    finally:
        obj.sigma = sigma
    h = np.array(h, dtype=float)
    if sigma:
        if obj.cutoff:
            k = obj._isi_to_index(obj.refractory_period)
            h[k:, k:] = gaussian_filter(h[k:, k:], sigma=sigma / obj.bin_width)
            h[:k, :] = 0
            h[:, :k] = 0
        else:
            h = gaussian_filter(h, sigma=sigma / obj.bin_width)
    return h


def _jisi_object(ss, t, L, *, J, f, sigma, use_sqrt, bw, T, n_bins, isi_dithering):
    ck = (t.tobytes(), L, J, f, sigma, use_sqrt, bw, T, n_bins, isi_dithering)
    hit = _jisi_cache.get(ck)
    if hit is not None:
        _jisi_cache.move_to_end(ck)
        return hit[0]
    obj = _call_explicit(ss.JointISI, _spiketrain(_centred(t), L),
                         dither=_frames(J), truncation_limit=_frames(T), n_bins=int(n_bins),
                         sigma=_frames(sigma), alternate=True, use_sqrt=bool(use_sqrt),
                         method="window", cutoff=True, refractory_period=_frames(f),
                         isi_dithering=bool(isi_dithering))
    if isi_dithering:
        obj.joint_isi_histogram = lambda _o=obj: _float_smoothed_histogram(_o)
    size = jisi_bytes(n_bins, int(np.floor(J / (T / n_bins))))
    if size <= _JISI_CACHE_BYTES:
        _jisi_cache[ck] = (obj, size)
        while sum(v[1] for v in _jisi_cache.values()) > _JISI_CACHE_BYTES:
            _jisi_cache.popitem(last=False)
    return obj


def _joint_isi_family(name, trains, window, key, *, J, f, sigma, use_sqrt,
                      bin_width, truncation, max_bytes, isi_dithering):
    J = _positive("J", J)
    f = _dead_time(f)
    sigma = float(sigma)
    if not (np.isfinite(sigma) and sigma >= 0):
        raise ValueError(f"sigma must be >= 0 frames, got {sigma!r}")
    bw = J / 2.0 if bin_width is None else _positive("bin_width", bin_width)
    ss, _, _ = _elephant()
    s, e, L, ins, n_out = _prepare(trains, window)
    n = len(ins)
    too_few = np.zeros(n, bool); fallback = np.zeros(n, np.int64)
    moved_nothing = np.zeros(n, bool); intractable = np.zeros(n, bool)
    in_effect = np.full(n, float(f)); trunc = np.full(n, np.nan)
    nbins = np.zeros(n, np.int64); clipped = np.zeros(n, np.int64)
    outs = []
    for r, t in enumerate(ins):
        if t.size < JISI_MIN_ONSETS:
            too_few[r] = True
            outs.append(t.copy()); continue
        isis = np.diff(t).astype(float)
        in_effect[r] = min(float(f), float(isis.min()))
        if truncation is None:
            # At least the largest interval-pair sum, plus room for a pair to grow
            # by the dither twice over while its neighbours move: a pair beyond
            # the truncation falls back to uniform dither.
            T_req = float((isis[:-1] + isis[1:]).max()) + 2 * J + 2 * bw
        else:
            T_req = _positive("truncation", truncation)
        n_b = max(1, int(math.ceil(T_req / bw)))
        T = n_b * bw
        trunc[r], nbins[r] = T, n_b
        if jisi_bytes(n_b, int(np.floor(J / bw))) > max_bytes:
            intractable[r] = True
            outs.append(t.copy()); continue
        obj = _jisi_object(ss, t, L, J=J, f=f, sigma=sigma, use_sqrt=use_sqrt, bw=bw,
                           T=T, n_bins=n_b, isi_dithering=isi_dithering)
        count = [0]
        base = type(obj)._uniform_dither_not_jisi_movable_spikes

        def _counting(curr_isi, next_isi, _obj=obj, _base=base, _count=count):
            _count[0] += 1
            return _base(_obj, curr_isi, next_isi)

        obj._uniform_dither_not_jisi_movable_spikes = _counting
        try:
            with _seeded_globals(_roi_seed(key, name, r)):
                sur = _call_explicit(obj.dithering, n_surrogates=1)[0]
        finally:
            del obj._uniform_dither_not_jisi_movable_spikes
        fallback[r] = count[0]
        k, nc = _back(sur.magnitude, L, "clip")
        clipped[r] = nc
        if fallback[r] == 0 and np.array_equal(k, t):
            moved_nothing[r] = True
        outs.append(k)
    ne = too_few | (fallback > 0) | moved_nothing | intractable
    params = {"J": J, "f": f, "sigma": sigma, "use_sqrt": bool(use_sqrt),
              "bin_width": bw, "truncation": truncation, "max_bytes": float(max_bytes),
              "method": "window", "alternate": True, "cutoff": True,
              "isi_dithering": bool(isi_dithering)}
    return _result(name, ins, outs, s, e, params=params, seed=seed_of(key),
                   per_roi={"jisi_too_few": too_few, "jisi_fallback_steps": fallback,
                            "jisi_moved_nothing": moved_nothing,
                            "jisi_intractable": intractable,
                            "dead_time_in_effect": in_effect, "truncation": trunc,
                            "n_bins": nbins, "clipped": clipped},
                   not_estimable=ne, n_outside=n_out,
                   extra={"counts": {"too_few": int(too_few.sum()),
                                     "fallback": int((fallback > 0).sum()),
                                     "moved_nothing": int(moved_nothing.sum()),
                                     "intractable": int(intractable.sum())}})


def joint_isi(trains, window, key, *, J, f, sigma, use_sqrt, bin_width=None,
              truncation=None, max_bytes=JISI_MAX_BYTES):
    """JISI-D: Elephant ``JointISI``, method ``window``, all ten parameters set.

    ``J`` is the maximum displacement; ``sigma`` the smoothing width (the grid
    sweeps J/2 and J); ``use_sqrt`` Gerstein's square root. ``bin_width`` defaults
    to J/2 (the grid asks for bins narrower than J); ``truncation`` defaults per
    ROI to the largest interval-pair sum plus 2J + 2 bins. First and last onsets
    stay fixed. ROIs that come back unchanged, fall back to uniform dither, move
    nothing or are intractable are ``not_estimable``.
    """
    return _joint_isi_family("joint_isi", trains, window, key, J=J, f=f, sigma=sigma,
                             use_sqrt=use_sqrt, bin_width=bin_width,
                             truncation=truncation, max_bytes=max_bytes,
                             isi_dithering=False)


def isi_dither(trains, window, key, *, J, f, sigma, use_sqrt, bin_width=None,
               truncation=None, max_bytes=JISI_MAX_BYTES):
    """ISI-D: as :func:`joint_isi` with ``isi_dithering=True`` — the joint
    histogram is the outer product of the interval histogram, ignoring order."""
    return _joint_isi_family("isi_dither", trains, window, key, J=J, f=f, sigma=sigma,
                             use_sqrt=use_sqrt, bin_width=bin_width,
                             truncation=truncation, max_bytes=max_bytes,
                             isi_dithering=True)


# ---------------------------------------------------------------- bin-based

def interval_jitter_bin(J: float) -> int:
    """Interval jitter's bin in whole frames: ``√2·J`` (the RMS rule), rounded.

    Whole frames because a bin edge inside a frame cannot be honoured once the
    surrogate is mapped back to frames: an onset re-placed just past a mid-frame
    edge lands in the frame the edge splits, and the frame belongs to the other
    bin. With whole-frame bins every bin's count is kept exactly. At J = 1 frame
    the bin is one frame and interval jitter moves nothing — the movement
    statistic reports that; it is not hidden here.
    """
    return max(1, int(round(math.sqrt(2.0) * _positive("J", J))))


def interval_jitter(trains, window, key, *, J):
    """Interval jitter (Date, Bienenstock & Geman 1998), Elephant ``jitter_spikes``.

    Each onset is re-placed uniformly within its fixed bin; bins of
    :func:`interval_jitter_bin` whole frames tile the window from its start (RMS
    displacement matched to UD's ``J/√3`` up to the rounding). Keeps every bin's
    count exactly.
    """
    name = "interval_jitter"
    J = _positive("J", J)
    b = float(interval_jitter_bin(J))
    ss, _, _ = _elephant()
    s, e, L, ins, n_out = _prepare(trains, window)
    outs, clipped = [], []
    for r, t in enumerate(ins):
        if t.size == 0:
            outs.append(t.copy()); clipped.append(0); continue
        with _seeded_globals(_roi_seed(key, name, r)):
            sur = _call_explicit(ss.jitter_spikes, _spiketrain(_centred(t), L),
                                 bin_size=_frames(b), n_surrogates=1)[0]
        k, n = _back(sur.magnitude, L, "clip")
        outs.append(k); clipped.append(n)
    return _result(name, ins, outs, s, e, params={"J": J, "bin": b}, seed=seed_of(key),
                   per_roi={"clipped": clipped}, n_outside=n_out)


def window_shuffle_width(J: float) -> int:
    """WIN-SHUFF's window in whole frames: ``√2·J`` (the RMS rule), as twice a
    whole-frame maximum displacement because that is the shape Elephant takes."""
    return 2 * max(1, int(round(_positive("J", J) / math.sqrt(2.0))))


def window_shuffle(trains, window, key, *, J):
    """WIN-SHUFF: Elephant ``bin_shuffling`` with 1-frame bins, shuffled within
    windows of ``√2·J`` whole frames tiling the generation window.

    The last partial window is permuted here with the same rule (bin ``i`` goes to
    ``perm[i]``), because Elephant permutes it as if it were full and drops what
    lands past the end.
    """
    name = "window_shuffle"
    W = window_shuffle_width(J)
    md = W // 2
    ss, _, _ = _elephant()
    s, e, L, ins, n_out = _prepare(trains, window)
    Lp = (L // W) * W
    outs, dropped = [], []
    for r, t in enumerate(ins):
        head, tail = t[t < Lp], t[t >= Lp]
        parts = []
        n_drop = 0
        if head.size:
            with _seeded_globals(_roi_seed(key, name, r)):
                sur = _call_explicit(ss.bin_shuffling, _spiketrain(_centred(head), Lp),
                                     max_displacement=md, bin_size=_frames(1.0),
                                     n_surrogates=1, sliding=False)[0]
            k, n = _back(sur.magnitude, Lp, "drop")
            n_drop += n + (head.size - sur.magnitude.size)
            parts.append(k)
        if tail.size:
            rng = np.random.RandomState(_roi_seed(key, name, r, "tail"))
            perm = rng.permutation(L - Lp)
            parts.append(Lp + perm[tail - Lp])
        outs.append(np.sort(np.concatenate(parts)).astype(np.int64) if parts
                    else t.copy())
        dropped.append(n_drop)
    return _result(name, ins, outs, s, e, params={"J": float(J), "window": W},
                   seed=seed_of(key), per_roi={"dropped": dropped}, n_outside=n_out,
                   extra={"last_partial_window": L - Lp})


# ---------------------------------------------------------------- written elsewhere

def pattern_jitter(trains, window, key, *, J, f):
    """Pattern jitter (Harrison & Geman 2009), clean-room in
    :mod:`bugarach.pattern_jitter`: windows of ``√2·J`` whole frames, R = f − 1."""
    name = "pattern_jitter"
    from bugarach import pattern_jitter as _pj  # lazy: written by another agent

    J = _positive("J", J)
    f = _dead_time(f)
    Lw = max(1, int(round(math.sqrt(2.0) * J)))
    R = f - 1
    s, e, L, ins, n_out = _prepare(trains, window)
    outs = []
    for r, t in enumerate(ins):
        if t.size == 0:
            outs.append(t.copy()); continue
        rng = np.random.RandomState(_roi_seed(key, name, r))
        k = np.asarray(_pj.pattern_jitter(t + s, (s, e), Lw, R, rng), dtype=np.int64)
        outs.append(np.sort(k) - s)
    return _result(name, ins, outs, s, e, params={"J": J, "f": f, "L": Lw, "R": R},
                   seed=seed_of(key), n_outside=n_out)


def operational_time(trains, window, key, *, J, bandwidth):
    """Operational-time dither (Louis, Gerstein, Grün & Diesmann 2010), in
    :mod:`bugarach.operational_time`; ``bandwidth`` is the kernel σ in frames."""
    name = "operational_time"
    from bugarach import operational_time as _ot  # lazy: written by another agent

    J = _positive("J", J)
    bandwidth = _positive("bandwidth", bandwidth)
    s, e, L, ins, n_out = _prepare(trains, window)
    outs, ne, flat, width_op = [], [], [], []
    for r, t in enumerate(ins):
        if t.size < 2:
            # fewer than two onsets: the leave-one-out rate is zero, so the method
            # returns the train unchanged. Marked, never scored as preserving it.
            outs.append(t.copy()); ne.append(True); flat.append(0)
            width_op.append(np.nan); continue
        rng = np.random.RandomState(_roi_seed(key, name, r))
        k, oi = _ot.operational_time_dither_info(t + s, (s, e), J, bandwidth, rng)
        outs.append(np.sort(np.asarray(k, dtype=np.int64)) - s)
        ne.append(not oi["estimable"]); flat.append(int(oi["flat_at_onset"]))
        width_op.append(float(oi["width_op"]))
    return _result(name, ins, outs, s, e, params={"J": J, "bandwidth": bandwidth},
                   seed=seed_of(key), not_estimable=ne, n_outside=n_out,
                   per_roi={"flat_at_onset": flat, "width_op": width_op})


# ---------------------------------------------------------------- controls

def do_nothing(trains, window, key):
    """Returns its input. Must read zero on movement and keep destruction's excess."""
    s, e, L, ins, n_out = _prepare(trains, window)
    return _result("do_nothing", ins, [t.copy() for t in ins], s, e, params={},
                   seed=seed_of(key), n_outside=n_out)


def interval_shuffle(trains, window, key):
    """Within-train intervals permuted (Elephant ``shuffle_isis``); first and last
    onsets fixed.

    Elephant also permutes the gap from the window start to the first onset, which
    would move the whole train and change its span. The train is handed over with
    its first onset at zero and the rest as a train starting there, so the only
    intervals in play are the ones between onsets. Built to move serial dependence.
    """
    name = "interval_shuffle"
    ss, _, _ = _elephant()
    s, e, L, ins, n_out = _prepare(trains, window)
    outs = []
    for r, t in enumerate(ins):
        if t.size < 3:
            outs.append(t.copy()); continue
        rel = (t[1:] - t[0]).astype(float)
        with _seeded_globals(_roi_seed(key, name, r)):
            sur = _call_explicit(ss.shuffle_isis, _spiketrain(rel, float(L - t[0])),
                                 n_surrogates=1, decimals=None)[0]
        k = np.rint(sur.magnitude).astype(np.int64) + t[0]
        outs.append(np.sort(np.concatenate([[t[0]], k])).astype(np.int64))
    return _result(name, ins, outs, s, e, params={}, seed=seed_of(key), n_outside=n_out)


def homogeneous_resample(trains, window, key):
    """Each ROI's onsets re-placed uniformly over the window (Elephant
    ``randomise_spikes``): count kept, intervals and rate profile destroyed."""
    name = "homogeneous_resample"
    ss, _, _ = _elephant()
    s, e, L, ins, n_out = _prepare(trains, window)
    outs, clipped = [], []
    for r, t in enumerate(ins):
        if t.size == 0:
            outs.append(t.copy()); clipped.append(0); continue
        with _seeded_globals(_roi_seed(key, name, r)):
            sur = _call_explicit(ss.randomise_spikes, _spiketrain(_centred(t), L),
                                 n_surrogates=1, decimals=None)[0]
        k, n = _back(sur.magnitude, L, "clip")
        outs.append(k); clipped.append(n)
    return _result(name, ins, outs, s, e, params={}, seed=seed_of(key),
                   per_roi={"clipped": clipped}, n_outside=n_out)


def _edge_dither(name, trains, window, key, J, analysis_window, edges):
    J = _positive("J", J)
    ss, _, _ = _elephant()
    s, e, L, ins, n_out = _prepare(trains, window)
    tiles = _tiles(L, analysis_window)
    outs, dropped = [], []
    for r, t in enumerate(ins):
        parts, n_drop = [], 0
        for i, (a, b) in enumerate(tiles):
            sub = t[(t >= a) & (t < b)] - a
            if sub.size == 0:
                continue
            A = b - a
            with _seeded_globals(_roi_seed(key, name, r, i)):
                sur = _call_explicit(ss.dither_spikes, _spiketrain(_centred(sub), A),
                                     dither=_frames(J), n_surrogates=1, decimals=None,
                                     edges=edges, refractory_period=None)[0]
            k, n = _back(sur.magnitude, A, "drop" if edges else "clip")
            if edges:
                n_drop += n + (sub.size - sur.magnitude.size)
            parts.append(k + a)
        outs.append(np.sort(np.concatenate(parts)).astype(np.int64) if parts
                    else t.copy())
        dropped.append(n_drop)
    return _result(name, ins, outs, s, e,
                   params={"J": J, "analysis_window": int(round(analysis_window))},
                   seed=seed_of(key), per_roi={"dropped": dropped}, n_outside=n_out,
                   extra={"analysis_windows": tiles})


def edge_thinning(trains, window, key, *, J, analysis_window):
    """UD generated per analysis window, dropping what leaves it (Elephant
    ``dither_spikes(edges=True)``): thins onsets within J of every analysis-window
    edge. Built to move edge-band density low."""
    return _edge_dither("edge_thinning", trains, window, key, J, analysis_window, True)


def edge_piling(trains, window, key, *, J, analysis_window):
    """UD generated per analysis window, clamping what leaves it to the window's
    end frames (Elephant ``dither_spikes(edges=False)``): piles onsets on the edges.
    Built to move edge-band density high."""
    return _edge_dither("edge_piling", trains, window, key, J, analysis_window, False)


def window_circular_shift(trains, window, key, *, analysis_window):
    """The circular shift generated per analysis window, each with its own lags:
    the seam every window acquires is what it is built to move (sub-floor rate)."""
    name = "window_circular_shift"
    s, e, L, ins, n_out = _prepare(trains, window)
    tiles = _tiles(L, analysis_window)
    parts = [[] for _ in ins]
    for i, (a, b) in enumerate(tiles):
        A = b - a
        subs = [(t[(t >= a) & (t < b)] - a).astype(float) for t in ins]
        rng = np.random.RandomState(seed_of((*tuple(key), name, i)))
        for r, x in enumerate(circular_shift_trains(subs, float(A), rng)):
            parts[r].append(np.mod(np.floor(np.asarray(x) + 0.5).astype(np.int64), A) + a)
    outs = [np.sort(np.concatenate(p)).astype(np.int64) if p else ins[r].copy()
            for r, p in enumerate(parts)]
    return _result(name, ins, outs, s, e,
                   params={"analysis_window": int(round(analysis_window))},
                   seed=seed_of(key), n_outside=n_out, extra={"analysis_windows": tiles})


# ---------------------------------------------------------------- registry

CANDIDATES = {
    "uniform_dither": uniform_dither,
    "shipped_dither": shipped_dither,
    "dead_time_dither": dead_time_dither,
    "circular_shift": circular_shift,
    "rigid_shift": rigid_shift,
    "trial_shift": trial_shift,
    "joint_isi": joint_isi,
    "isi_dither": isi_dither,
    "interval_jitter": interval_jitter,
    "window_shuffle": window_shuffle,
    "pattern_jitter": pattern_jitter,
    "operational_time": operational_time,
}
"""The twelve candidates (the plan's Table 1), by name."""

CONTROLS = {
    "do_nothing": do_nothing,
    "interval_shuffle": interval_shuffle,
    "homogeneous_resample": homogeneous_resample,
    "edge_thinning": edge_thinning,
    "edge_piling": edge_piling,
    "window_circular_shift": window_circular_shift,
}
"""The six known-bad controls (the plan's Table 2), by name."""


def generate(name: str, trains, window, key, **params) -> SurrogateResult:
    """One surrogate of one stream: ``name`` from :data:`CANDIDATES` or
    :data:`CONTROLS`, every parameter in frames. An unknown parameter is a
    ``TypeError``, never ignored."""
    fn = CANDIDATES.get(name) or CONTROLS.get(name)
    if fn is None:
        raise KeyError(f"unknown surrogate {name!r}")
    return fn(trains, window, tuple(key), **params)
