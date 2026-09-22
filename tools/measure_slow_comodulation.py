#!/usr/bin/env python3
"""Where shared structure between ROIs lives in time: the population cross-correlogram.

    python tools/measure_slow_comodulation.py                          # into the darkroom
    python tools/measure_slow_comodulation.py --out <folder> --limit 6 --draws 2   # smoke

The page this feeds is ``docs/learned/slow_comodulation/README.md``; what it found overturned
the hypotheses this tool was first written under, and the docstrings below say what each arm
was measured to do, not what it was expected to do.

**The statistic.** Count onset pairs at lag *k* frames between distinct ROIs, and divide by the
count expected if the two ROIs fired independently at their observed totals over the window —
the cross-correlogram normalised by its independence level (Perkel, Gerstein & Moore 1967):

    ratio(k) = sum_{i<j} [sum_t x_i(t) x_j(t+k) + x_j(t) x_i(t+k)]  /  sum_{i<j} 2 n_i n_j (L-k) / L**2

with the zero-lag term counted once per unordered pair. ``ratio - 1`` is the **excess
coincidence** at that lag: 0 means no more onset pairs than chance at this window's average
rates. Numerator and denominator are summed within lag bins and over recordings before dividing,
so a recording weighs in proportion to its onset pairs. ⚠ Because chance is set by whole-window
counts, the excess summed over **all** lags up to the window length is zero by construction — the
single-window case of Brody 1999, eq. 3.6, where the covariogram integrates to the count
covariance — so a positive shoulder at some lags is paid back at others.

**What a counting detector sees** is the variance of the number of onsets in a bin, summed over
ROIs. ``count_variance`` stores, per arm and bin width, the variance of that population count and
the same after a straight line across the window is removed; the count-variance ratio divides an
arm's pooled variance by the circular shift **of the same onsets** (``NULL_OF``), and says how much
more the population count varies than it would if ROIs were independent. It grows roughly as
1 + (ROIs − 1) × the mean pairwise count correlation, so ``checks`` also reports
(ratio − 1) / (ROIs − 1) per recording to compare folders with different ROI counts.

**Arms**, each on the same window trimmed by ``TRIM_SEC`` at both ends (the largest *J*, so rigid
shift's dropped onsets never enter):

* ``real`` — the recording.
* ``circular`` — :func:`bugarach.surrogates.circular_shift`, the assessor's null: each ROI's train
  moved by its own lag with wrap. Removes every relation between ROIs; keeps each ROI's own
  temporal structure. Reads zero by construction.
* ``block_120`` — :func:`bugarach.surrogates.window_circular_shift` with 2-minute windows: the
  same shift inside each block. Keeps every ROI's count per block, so **any** shared covariation
  of 2-minute counts survives it — slow drift, and events too, since a block holding a large
  event holds an extra onset from each member (argued; at the generator's sparse event density
  it reads zero, and on the lab slow stream removing CoactDetect's episodes first lowers it).
  It also keeps part of a 20 s modulation. ⚠ It is registered as a known-bad control: every
  block acquires a seam.
* ``rigid_<J>`` — one offset per ROI uniform in [−J, J), ``floor(k + 0.5 + u)``, onsets pushed past
  either end dropped: ``tools/tube_self_supervised.py``'s ``rigid_frames``, imported. Measured: it
  spreads an event's coincidences over about ±2*J* rather than deleting them, reduces modulation
  faster than about *J*, and leaves slower drift in place.
* ``minus_coact`` (lab folder and synthetic worlds) — every onset inside a CoactDetect episode
  removed, membership by CoactDetect's own half-open bins, CoactDetect at the project's
  calibrated point (``detect_folder.detector_params``). It fires only where at least three ROIs
  coincide, so two-ROI coincidences and events too weak for its test stay.
* ``circular_mask`` — the null for every removal arm: a circular shift run inside the stretches no
  episode covers, so the null keeps each ROI's onset count and carries the same shared,
  episode-shaped holes the removal cuts.
* ``circular_minus_coact`` — the circular shift of the already-removed trains. Kept only to show
  what the mask-matched null buys: it scatters each ROI's holes to its own phase, so the shared
  holes read as shared change and the ratio comes out too high.
* ``minus_coact_block_120`` — the block control applied after that removal.
* ``minus_coact_rigid_20`` — rigid shift at *J* = 20 s applied after that removal: what a rigid
  shift leaves once the detectable events are gone.
* ``circular_single`` — one circular draw scored against the 8-draw mean: the per-recording
  reference for how often a ratio exceeds 1 by chance.

**Synthetic worlds** (``--no-synthetic`` to skip):

* from the repository's own generator, ``docs/learned/generator_spec.json`` through
  :func:`bugarach.simulate.simulate_coordination` exactly as ``tools/fair_bakeoff.py`` builds
  benchmark recordings: ``benchmark`` (the whole spec), ``sim_background`` (per-ROI background
  only), ``sim_events`` (background plus planted events), ``sim_hot_window`` (background plus the
  spec's 300 s whole-field dense block, the promiscuity probe);
* illustrative, fitted to nothing: ``shared_20s``, ``drift_5min`` and ``shallow_1min``, every ROI's
  rate multiplied by one shared log-normal multiplier wandering on a 20 s, 5-minute or 1-minute
  timescale, no events; the last at a depth near the lab fast stream's shoulder.

Baseline windows only: the lab folder is refused anything but its declared baseline region. The
Cossart folder declares no regions and is read whole, from the first onset of any ROI (many of its
recordings open with tens of seconds in which no ROI has an onset). Every random key carries
``TAG``; CoactDetect's own surrogates use its default seed.
"""

from __future__ import annotations

import argparse
import json
import multiprocessing as mp
import os
import sys
import time
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from bugarach import surrogate_stats as ss  # noqa: E402
from bugarach import surrogates as sg  # noqa: E402
from tube_self_supervised import rigid_frames  # noqa: E402

TAG = "slow-comodulation-2026-09-17"
FOLDER = "2026-09-17-slow-comodulation-pins-excluded"
J_SEC = (1.6, 10.0, 20.0)
TRIM_SEC = max(J_SEC)
BLOCK_SEC = 120.0
MAX_LAG_SEC = 300.0
LAG_EDGES_SEC = tuple(float(x) for x in np.concatenate(
    [[0.0, 0.3, 0.6], np.geomspace(1.0, MAX_LAG_SEC, 18)]))
"""Short bins 0.3 s wide so every recording's frame interval (at most 0.119 s) puts at least two
lag frames in each; an edge at exactly 1 s; log-spaced from there to 300 s."""
VAR_BIN_SEC = (1.0, 10.0, 60.0)
N_SINGLE = 3
"""Single circular draws per recording, each scored against the 8-draw circular mean: how often a
per-recording ratio from one surrogate realization exceeds 1 by chance. ``circular_ref8`` is a
second 8-draw mean, the matching reference for arms that are themselves means of 8 draws."""
from bugarach import dataset as _dataset  # noqa: E402

LAB_ROLE = _dataset.default_role()
"""The lab folder this analysis reads: the declared default (Tony, 2026-09-21), resolved to its
table name so the result keys (``<role>/<stream>``) record which folder was measured.

It moved on 2026-09-17, from ``steps_excluded`` to the producer's folder that also removes the
moco floor-pinned windows, and since 2026-09-21 it follows ``current_export.toml``'s ``default``
rather than naming a role here. The earlier folder declared a contamination nothing in the data
marked, and ``dataset.current`` refuses it outright.
The branches below test against this constant because the lab folder is the one with two streams,
baseline windows and a CoactDetect removal arm; the Dard et al. folder has none of those.
"""
FOLDERS = ((LAB_ROLE, "fast"), (LAB_ROLE, "slow"), ("cossart", "events"))

COACT_NOTE = ("CoactDetect runs at detect_folder.detector_params('coact', ...) on both streams: "
              "the project's calibrated point, as bugarach detect runs it.")

SPEC_PATH = ROOT / "docs" / "learned" / "generator_spec.json"
N_SYN = 24
OU = dict(dur_sec=1200.0, dt=0.1, shared_20s=(20.0, 0.8), drift_5min=(300.0, 0.8),
          shallow_1min=(60.0, 0.25))
"""The illustrative worlds take the generator spec's ROI count and mean background rate, a lab-like
1,200 s window, a flat rate for every ROI, and (timescale, log-rate depth): the 20 s and 5-minute
worlds at a depth chosen to be visible, and a 1-minute world at a depth near the lab fast
stream's shoulder."""


def rng(*key) -> np.random.RandomState:
    return ss.rng_of((TAG,) + tuple(str(k) for k in key))


# -- the statistic ----------------------------------------------------------------------------

def _autocorr_rows(X: np.ndarray, max_lag: int) -> np.ndarray:
    """Non-circular autocorrelation sum_t x(t) x(t+k), k = 0..max_lag, summed over rows."""
    L = X.shape[1]
    nfft = 1 << int(np.ceil(np.log2(2 * L)))
    out = np.zeros(max_lag + 1)
    for a in range(0, X.shape[0], 64):
        f = np.fft.rfft(X[a:a + 64], n=nfft, axis=1)
        out += np.fft.irfft(f * np.conj(f), n=nfft, axis=1)[:, :max_lag + 1].sum(axis=0)
    return out


def lag_bins(dt: float, max_lag: int) -> np.ndarray:
    """Bin index per lag frame; -1 at or past the last edge. A small tolerance keeps a lag of
    exactly 3 frames at 0.1 s in the bin that starts at 0.3 s."""
    k_sec = np.arange(max_lag + 1) * dt + 1e-9
    idx = np.searchsorted(np.asarray(LAG_EDGES_SEC), k_sec, side="right") - 1
    idx[k_sec >= LAG_EDGES_SEC[-1]] = -1
    return idx


def raster(trains, L: int) -> np.ndarray:
    X = np.zeros((len(trains), L))
    for r, t in enumerate(trains):
        t = np.asarray(t, np.int64)
        np.add.at(X[r], t[(t >= 0) & (t < L)], 1.0)
    return X


def pair_counts(trains, L: int, dt: float) -> tuple[np.ndarray, np.ndarray]:
    """(observed, expected) cross-ROI onset pairs per lag bin, zero lag counted once."""
    max_lag = min(int(round(MAX_LAG_SEC / dt)), L - 1)
    X = raster(trains, L)
    n = X.sum(axis=1)
    obs = _autocorr_rows(X.sum(axis=0, keepdims=True), max_lag) - _autocorr_rows(X, max_lag)
    k = np.arange(max_lag + 1)
    exp = (n.sum() ** 2 - (n ** 2).sum()) * (L - k) / L ** 2
    obs[0] /= 2.0
    exp[0] /= 2.0
    idx = lag_bins(dt, max_lag)
    nb = len(LAG_EDGES_SEC) - 1
    ok = idx >= 0
    return (np.bincount(idx[ok], obs[ok], minlength=nb),
            np.bincount(idx[ok], exp[ok], minlength=nb))


def count_variance(trains, L: int, dt: float) -> np.ndarray:
    """Variance of the population onset count in full bins of each width in ``VAR_BIN_SEC``, then
    the same after a straight line fitted to the bin counts is removed (residual sum of squares
    over n − 2). ⚠ The line also absorbs the linear part of any change slower than about half the
    window, so the detrended ratio is not a trend test: the trend-free 5-minute synthetic world
    loses about a third of its 1-minute excess to it."""
    pop = raster(trains, L).sum(axis=0)
    raw, detr = [], []
    for w in VAR_BIN_SEC:
        f = int(round(w / dt))
        nb = L // f
        c = pop[:nb * f].reshape(nb, f).sum(axis=1)
        raw.append(float(c.var(ddof=1)) if nb > 1 else np.nan)
        if nb > 2:
            x = np.arange(nb, dtype=float)
            resid = c - np.polyval(np.polyfit(x, c, 1), x)
            detr.append(float(np.sum(resid ** 2) / (nb - 2)))
        else:
            detr.append(np.nan)
    return np.asarray(raw + detr)


def measure(trains, L: int, dt: float) -> np.ndarray:
    o, e = pair_counts(trains, L, dt)
    return np.concatenate([o, e, count_variance(trains, L, dt)])


def unpack(v) -> dict:
    nb = len(LAG_EDGES_SEC) - 1
    nv = len(VAR_BIN_SEC)
    v = np.asarray(v, float)
    return dict(obs=v[:nb], exp=v[nb:2 * nb], var=v[2 * nb:2 * nb + nv],
                var_detrended=v[2 * nb + nv:2 * nb + 2 * nv])


NULL_OF = {"minus_coact": "circular_mask", "minus_coact_block_120": "circular_mask",
           "minus_coact_rigid_20": "circular_mask"}
"""Each count-variance ratio is divided by a surrogate of the same onsets (``null_of``), and for
the arms with CoactDetect's episodes removed that surrogate must carry the same holes. Deleting
every onset inside an episode cuts gaps that are **shared across ROIs**; a null that shifts each
ROI on its own and then deletes *its own* onsets scatters those gaps to separate phases, and the
shared gaps are then scored as shared change. So ``circular_mask`` shifts each ROI circularly
**within the frames no episode covers**: its onset count survives exactly, and the holes stay
where the arm has them. The mismatched version is kept as ``circular_minus_coact`` so the
difference can be read rather than asserted."""


def null_of(arm: str) -> str:
    return NULL_OF.get(arm, "circular")


# -- arms -------------------------------------------------------------------------------------

def trimmed(trains, L_full: int, trim: int):
    out = []
    for t in trains:
        t = np.asarray(t, np.int64)
        out.append(t[(t >= trim) & (t < L_full - trim)] - trim)
    return out, L_full - 2 * trim


def coact_removed(trains, L_full: int, dt: float, stream: str):
    """Onsets inside any CoactDetect episode removed, membership by its half-open bin span."""
    from bugarach.detect_folder import detector_params
    from bugarach.detectors.coact import coact_detect
    params = detector_params("coact", frame_interval_sec=dt, stream=stream)
    sec = [np.asarray(t, float) * dt for t in trains]
    det = coact_detect(sec, (0.0, L_full * dt), **params)
    episodes = list(zip(np.asarray(det.onset_sec, float), np.asarray(det.width_sec, float)))
    out, n_in, n_out = [], 0, 0
    for t, ts in zip(trains, sec):
        inside = np.zeros(t.size, bool)
        for a, w in zip(det.onset_sec, det.width_sec):
            inside |= (ts >= a) & (ts < a + w)
        out.append(np.asarray(t, np.int64)[~inside])
        n_in += t.size
        n_out += int(inside.sum())
    return out, episodes, dict(coact_events=int(det.n_events), share_removed=n_out / max(n_in, 1),
                     events_per_10min=det.n_events / (L_full * dt / 600.0),
                     episode_share_of_time=float(np.sum(det.width_sec)) / (L_full * dt))


def surviving_frames(episodes, L: int, dt: float, trim: int) -> np.ndarray:
    """The frames of the trimmed window that no CoactDetect episode covers, by the same half-open
    membership the removal uses."""
    keep = np.ones(L, bool)
    for a, w in episodes:
        i0 = int(np.ceil(a / dt - 1e-9)) - trim
        i1 = int(np.ceil((a + w) / dt - 1e-9)) - trim
        keep[max(i0, 0):max(i1, 0)] = False
    return keep


def masked_circular_shift(trains, keep: np.ndarray, r) -> list:
    """Circular shift run **inside the surviving stretches**: each ROI's onsets are mapped to
    their position among the frames no episode covers, shifted circularly there by that ROI's own
    offset, and mapped back.

    This is the null the removal arms need, and neither simpler construction is. Shifting the
    already-removed trains across the whole window scatters each ROI's episode-shaped holes to its
    own phase, so the holes — which the removal cuts in every ROI at once — read as shared change
    and the ratio comes out too high. Shifting the full trains and then cutting the same episodes
    keeps the holes but not the counts: the removal takes onsets where they are dense, the mask
    takes them in proportion to time, the null ends up with more onsets than the arm, and the ratio
    comes out too low. Shifting within the surviving frames keeps **both** — every ROI's onset
    count exactly, and not one onset inside an episode.
    """
    idx = np.flatnonzero(keep)
    if idx.size == 0:
        return [np.asarray(t, np.int64)[:0] for t in trains]
    pos = np.full(keep.size, -1, np.int64)
    pos[idx] = np.arange(idx.size)
    out = []
    for t in trains:
        p = pos[np.asarray(t, np.int64)]
        p = p[p >= 0]
        out.append(np.sort(idx[(p + r.randint(idx.size)) % idx.size]))
    return out


def arms_for(trains_full, L_full: int, dt: float, key, draws: int, stream: str | None):
    trim = int(np.ceil(TRIM_SEC / dt))
    tr, L = trimmed(trains_full, L_full, trim)
    block = int(round(BLOCK_SEC / dt))
    res = {"real": measure(tr, L, dt)}

    def mean_over(fn, name):
        return np.mean([measure(fn(d), L, dt) for d in range(draws)], axis=0)

    res["circular"] = mean_over(
        lambda d: sg.circular_shift(tr, (0, L), (TAG, *key, "circular", d)).trains, "circular")
    for d in range(N_SINGLE):
        res[f"circular_single_{d}"] = measure(
            sg.circular_shift(tr, (0, L), (TAG, *key, "circular-single", d)).trains, L, dt)
    res["circular_ref8"] = mean_over(
        lambda d: sg.circular_shift(tr, (0, L), (TAG, *key, "circular-ref8", d)).trains, "ref8")
    res["block_120"] = mean_over(
        lambda d: sg.window_circular_shift(tr, (0, L), (TAG, *key, "block", d),
                                           analysis_window=block).trains, "block")
    for J in J_SEC:
        res[f"rigid_{J:g}"] = mean_over(
            lambda d, J=J: trimmed(rigid_frames(trains_full, L_full, J / dt,
                                                rng(*key, "rigid", J, d)), L_full, trim)[0],
            "rigid")
    extra = {}
    if stream in ("fast", "slow"):
        removed, episodes, extra = coact_removed(trains_full, L_full, dt, stream)
        rt = trimmed(removed, L_full, trim)[0]

        keep = surviving_frames(episodes, L, dt, trim)
        res["minus_coact"] = measure(rt, L, dt)
        res["circular_mask"] = mean_over(
            lambda d: masked_circular_shift(rt, keep, rng(*key, "mask-circular", d)), "mask")
        res["circular_minus_coact"] = mean_over(
            lambda d: sg.circular_shift(rt, (0, L), (TAG, *key, "coact-circular", d)).trains, "cc")
        res["minus_coact_block_120"] = mean_over(
            lambda d: sg.window_circular_shift(rt, (0, L), (TAG, *key, "coact-block", d),
                                               analysis_window=block).trains, "cb")
        res["minus_coact_rigid_20"] = mean_over(
            lambda d: trimmed(rigid_frames(removed, L_full, 20.0 / dt,
                                           rng(*key, "coact-rigid", d)), L_full, trim)[0],
            "cr")
    return {k: list(map(float, v)) for k, v in res.items()}, extra, L * dt


# -- real recordings --------------------------------------------------------------------------

def load(role: str, stream: str, limit: int | None):
    """Recordings, and whether this folder declares treatment regions.

    A folder that declares regions is refused anything but its declared baseline, as
    ``tools/look_rigid_shift.py`` refuses it.

    ⚠ **The guard asks the folder, not the role name.** It used to read
    ``role == "steps_excluded"``, which meant that renaming the role — which happened the day
    the producer shipped the de-pinned export — would have switched the guard off without a
    word, leaving treatment windows in a baseline-only analysis. The session next door hit
    exactly that: three name comparisons, two of which crashed loudly and one of which was this
    guard, failing silently. A property of the data cannot go stale the way a name can.
    """
    from bugarach import dataset
    from bugarach.io import load_folder
    slices = load_folder(dataset.current(role))
    if limit:
        slices = slices[:limit]
    recs, skipped = ss.recordings_from_slices(slices, stream)
    declares_regions = any(getattr(s, "regions", None) for s in slices)
    if declares_regions:
        refused = [r.recording_id for r in recs
                   if not r.window_source.startswith("baseline region")]
        if refused:
            raise SystemExit(f"refusing non-baseline windows in {stream}: {refused}")
    return recs, skipped, declares_regions


def active_and_correlation(trains_full, L_full: int, dt: float) -> dict:
    """ROIs with at least one onset in the trimmed window, and the mean correlation between two such
    ROIs' onset counts in full 1-minute bins (pairs where both counts vary). A denominator and a
    per-pair size only: no ROI is removed from any arm."""
    trim = int(np.ceil(TRIM_SEC / dt))
    tr, L = trimmed(trains_full, L_full, trim)
    f = int(round(60.0 / dt))
    nb = L // f
    X = raster(tr, L)[:, :nb * f].reshape(len(tr), nb, f).sum(axis=2)
    active = int(np.sum(X.sum(axis=1) > 0))
    varying = X[X.std(axis=1) > 0]
    corr = np.nan
    if varying.shape[0] > 1 and nb > 2:
        C = np.corrcoef(varying)
        corr = float(C[np.triu_indices_from(C, k=1)].mean())
    return dict(n_active_roi=active, pairwise_count_corr_1min=corr)


def minute_counts(trains_full, L_full: int, dt: float, key) -> dict:
    """The population onset count per full minute of the trimmed window: as recorded, one rigid
    shift at the largest J, one circular shift. Per recording; kept in results.json only, never in
    summary.json or the repository (FOUNDATIONS §5)."""
    trim = int(np.ceil(TRIM_SEC / dt))
    tr, L = trimmed(trains_full, L_full, trim)
    f = int(round(60.0 / dt))
    nb = L // f

    def per_min(ts):
        return raster(ts, L).sum(axis=0)[:nb * f].reshape(nb, f).sum(axis=1).tolist()

    rigid = trimmed(rigid_frames(trains_full, L_full, max(J_SEC) / dt,
                                 rng(*key, "trace-rigid")), L_full, trim)[0]
    return dict(real=per_min(tr), rigid=per_min(rigid),
                circular=per_min(sg.circular_shift(tr, (0, L), (TAG, *key, "trace-circ")).trains))


def real_task(args):
    role, stream, rec, draws, declares_regions = args
    a, b = rec.window
    lead_in = 0
    if not declares_regions:
        # No regions means the window is the whole recording, and several of those open with
        # tens of seconds in which no ROI fires; start at the first onset instead.
        firsts = [int(t[0]) for t in rec.trains if len(t)]
        if firsts:
            lead_in = min(firsts) - a
            a = min(firsts)
    trains = [np.asarray(t, np.int64) - a for t in rec.trains]
    # arms_for builds the CoactDetect removal arms only for a stream it has an operating point
    # for, so the stream goes through as it is rather than being gated on the folder's name.
    arms, extra, used_sec = arms_for(trains, b - a, rec.dt, (role, stream, rec.recording_id),
                                     draws, stream)
    extra["counts_per_minute"] = minute_counts(trains, b - a, rec.dt,
                                               (role, stream, rec.recording_id))
    extra.update(active_and_correlation(trains, b - a, rec.dt))
    return dict(role=role, stream=stream, recording_id=rec.recording_id, mouse=rec.mouse,
                group=rec.group, dt=rec.dt, n_roi=len(rec.trains),
                n_onsets=int(sum(len(t) for t in rec.trains)), analysed_sec=used_sec,
                lead_in_sec=lead_in * rec.dt, arms=arms, **extra)


# -- synthetic worlds -------------------------------------------------------------------------

def generator_spec() -> dict:
    return json.loads(SPEC_PATH.read_text())["generator"]


SIM_WORLDS = {
    "benchmark": {},
    # The probe is switched off the way bench.NULL_RECORDING switches it off: without
    # hot_window=None the generator still keeps planted events out of the probe's span.
    "sim_background": dict(hot_window=None, hot_rate_hz=0.0, ramp_sec=0.0, n_distractors=0,
                           n_per_level=(0, 0, 0)),
    "sim_events": dict(hot_window=None, hot_rate_hz=0.0, ramp_sec=0.0, n_distractors=0),
    "sim_hot_window": dict(n_distractors=0, n_per_level=(0, 0, 0)),
}
OU_WORLDS = ("shared_20s", "drift_5min", "shallow_1min")
SYN_WORLDS = tuple(SIM_WORLDS) + OU_WORLDS


def _ou_multiplier(n_frames: int, dt: float, r, tau: float, sigma: float) -> np.ndarray:
    """Mean-one log-normal multiplier driven by an Ornstein-Uhlenbeck process."""
    a = np.exp(-dt / tau)
    z = np.empty(n_frames)
    z[0] = r.randn()
    e = r.randn(n_frames) * np.sqrt(1 - a * a)
    for i in range(1, n_frames):
        z[i] = a * z[i - 1] + e[i]
    m = np.exp(sigma * z - 0.5 * sigma ** 2)
    return m / m.mean()


def synthetic_recording(world: str, i: int):
    """Frame trains and window length (frames) for one synthetic recording."""
    if world in SIM_WORLDS:
        from bugarach.simulate import simulate_coordination
        spec = {**generator_spec(), **SIM_WORLDS[world]}
        sl, _ = simulate_coordination(seed=int(ss.seed_of((TAG, world, i)) & 0x7FFFFFFF), **spec)
        dt = float(spec["grid_sec"])
        L = int(round(spec["duration_sec"] / dt))
        trains = [np.unique(ss.to_frames(np.asarray(v, float), dt)) for v in
                  sl.streams["events"].t50rise]
        return [t[(t >= 0) & (t < L)] for t in trains], L, dt
    r = rng("syn", world, i)
    dt = OU["dt"]
    L = int(round(OU["dur_sec"] / dt))
    p = generator_spec()["bg_rate_hz"] * dt
    tau, sigma = OU[world]
    m = _ou_multiplier(L, dt, r, tau, sigma)
    trains = [np.flatnonzero(r.random_sample(L) < p * m)
              for _ in range(int(generator_spec()["n_roi"]))]
    return trains, L, dt


def syn_task(args):
    world, i, draws = args
    trains, L, dt = synthetic_recording(world, i)
    # CoactDetect removal runs on the synthetic worlds too (fast settings), so the arm the lab
    # claims rest on is tested where the answer is known.
    arms, extra, used_sec = arms_for(trains, L, dt, ("syn", world, i), draws, "fast")
    return dict(world=world, i=i, mouse=f"syn{i}", dt=dt, L=L, analysed_sec=used_sec,
                n_roi=len(trains), n_onsets=int(sum(len(t) for t in trains)), arms=arms,
                share_removed=extra.get("share_removed"),
                raster=[list(map(int, t)) for t in trains] if i == 0 else None)


# -- summary ----------------------------------------------------------------------------------

def pooled(rows, arm, detrended=False, null=None):
    """(excess per lag bin, count-variance ratio per bin width). The ratio divides by the circular
    shift of the same onsets (``null_of``); ``detrended`` uses each bin count series after a
    straight line is removed, in the arm and in its null alike."""
    U = [unpack(r["arms"][arm]) for r in rows]
    C = [unpack(r["arms"][null or null_of(arm)]) for r in rows]
    key = "var_detrended" if detrended else "var"
    o = np.sum([u["obs"] for u in U], axis=0)
    e = np.sum([u["exp"] for u in U], axis=0)
    with np.errstate(invalid="ignore", divide="ignore"):
        return (o / e - 1.0,
                np.nansum([u[key] for u in U], axis=0) / np.nansum([c[key] for c in C], axis=0))


def summarise(rows, n_boot: int, key):
    """Pooled curves with a mouse bootstrap (one resample of mice shared by every arm), an
    equal-weight-mice curve, and the heaviest mouse's share of the expected pairs."""
    arms = list(rows[0]["arms"])
    mice = sorted({r["mouse"] for r in rows})
    by_mouse = {m: [r for r in rows if r["mouse"] == m] for m in mice}
    picks = rng("boot", *key).randint(0, len(mice), (n_boot, len(mice)))
    out = {}
    for arm in arms:
        ex, vr = pooled(rows, arm)
        boots = [pooled([r for j in p for r in by_mouse[mice[j]]], arm) for p in picks]
        bex = np.array([b[0] for b in boots])
        bvr = np.array([b[1] for b in boots])
        per_mouse = np.array([pooled(by_mouse[m], arm)[0] for m in mice])
        U = [unpack(r["arms"][arm]) for r in rows]
        o = np.sum([u["obs"] for u in U], axis=0)
        e = np.sum([u["exp"] for u in U], axis=0)
        vd = pooled(rows, arm, detrended=True)[1]
        bvd = np.array([pooled([r for j in p for r in by_mouse[mice[j]]], arm, detrended=True)[1]
                        for p in picks])
        with np.errstate(invalid="ignore"):
            out[arm] = dict(
                excess=ex.tolist(),
                lo=np.nanpercentile(bex, 2.5, axis=0).tolist(),
                hi=np.nanpercentile(bex, 97.5, axis=0).tolist(),
                excess_equal_mice=np.nanmean(per_mouse, axis=0).tolist(),
                excess_pairs=(o - e).tolist(),
                var_ratio=vr.tolist(),
                var_lo=np.nanpercentile(bvr, 2.5, axis=0).tolist(),
                var_hi=np.nanpercentile(bvr, 97.5, axis=0).tolist(),
                var_ratio_detrended=vd.tolist(),
                var_detrended_lo=np.nanpercentile(bvd, 2.5, axis=0).tolist(),
                var_detrended_hi=np.nanpercentile(bvd, 97.5, axis=0).tolist())
    exp_by_mouse = np.array([np.sum([unpack(r["arms"]["real"])["exp"][1:].sum()
                                     for r in by_mouse[m]]) for m in mice])

    def kish(w):
        return float(w.sum() ** 2 / np.sum(w ** 2)) if np.sum(w ** 2) else None

    effective = {}
    for arm in ("real", "minus_coact_block_120"):
        if arm not in arms:
            continue
        pw = np.array([np.sum([unpack(r["arms"][arm])["exp"][1:].sum() for r in by_mouse[m]])
                       for m in mice])
        vw = np.array([np.sum([unpack(r["arms"][null_of(arm)])["var"][-1] for r in by_mouse[m]])
                       for m in mice])
        effective[arm] = dict(by_pairs=kish(pw), by_variance=kish(vw))
    top = float(exp_by_mouse.max() / exp_by_mouse.sum()) if exp_by_mouse.sum() else None
    return dict(n_recordings=len(rows), n_mice=len(mice), top_mouse_share_of_pairs=top,
                effective_mice=effective, arms=out)


CONTRASTS = (("real", "rigid_20"), ("real", "block_120"), ("real", "minus_coact_block_120"),
             ("minus_coact", "minus_coact_block_120"),
             ("minus_coact_block_120", "minus_coact_rigid_20"))


def _var_ratio(rows, arm):
    return pooled(rows, arm)[1]


def checks(rows, n_boot: int, key) -> dict:
    """The comparisons the page rests on, each able to fail.

    * ``paired`` — pooled count-variance ratio of one arm minus another, per bin width, with a mouse
      bootstrap drawing the same mice for both arms.
    * ``per_recording`` — each recording's own count-variance ratio (arm ÷ its circular arm): the
      median, the quartiles and the share above 1, so a pooled number can be seen not to rest on a
      few recordings.
    * ``leave_heaviest_out`` — the pooled ratio with the five heaviest recordings dropped, heaviest
      by each arm's own null variance for the ratio and by expected onset pairs for the excess.
    * ``null_single_draw`` / ``null_8_draw_mean`` — chance references for the share above 1.
    * ``pairwise_count_corr_1min`` — the mean correlation between two active ROIs' 1-minute counts,
      a per-pair size that does not grow with the number of ROIs.
    * ``removal_share_pooled`` — the share of onsets CoactDetect removal took, weighted as the
      pooled curves weight recordings (by expected onset pairs), beside the plain median.
    """
    mice = sorted({r["mouse"] for r in rows})
    by_mouse = {m: [r for r in rows if r["mouse"] == m] for m in mice}
    picks = rng("checks", *key).randint(0, len(mice), (n_boot, len(mice)))
    arms = set(rows[0]["arms"])
    out = {"paired": {}, "per_recording": {}}
    for a, b in CONTRASTS:
        if a not in arms or b not in arms:
            continue
        d = _var_ratio(rows, a) - _var_ratio(rows, b)
        boots = []
        for p in picks:
            rs = [r for j in p for r in by_mouse[mice[j]]]
            boots.append(_var_ratio(rs, a) - _var_ratio(rs, b))
        boots = np.array(boots)
        out["paired"][f"{a} - {b}"] = dict(
            diff=d.tolist(), lo=np.nanpercentile(boots, 2.5, axis=0).tolist(),
            hi=np.nanpercentile(boots, 97.5, axis=0).tolist())
    n_active = np.array([r.get("n_active_roi", r["n_roi"]) for r in rows], float)

    def per_rec(arm, null):
        with np.errstate(invalid="ignore", divide="ignore"):
            return (np.array([unpack(r["arms"][arm])["var"] / unpack(r["arms"][null])["var"]
                              for r in rows]),
                    np.array([unpack(r["arms"][arm])["var_detrended"]
                              / unpack(r["arms"][null])["var_detrended"] for r in rows]))

    for arm in ("real", "rigid_20", "block_120", "minus_coact", "minus_coact_block_120",
                "minus_coact_rigid_20"):
        if arm not in arms:
            continue
        per, per_d = per_rec(arm, null_of(arm))
        with np.errstate(invalid="ignore", divide="ignore"):
            per_pair = (per - 1.0) / np.maximum(n_active - 1, 1)[:, None]
        out["per_recording"][arm] = dict(
            median=np.nanmedian(per, axis=0).tolist(),
            q25=np.nanpercentile(per, 25, axis=0).tolist(),
            q75=np.nanpercentile(per, 75, axis=0).tolist(),
            share_above_1=np.nanmean(per > 1, axis=0).tolist(),
            detrended_median=np.nanmedian(per_d, axis=0).tolist(),
            per_active_pair_median=np.nanmedian(per_pair, axis=0).tolist())
    # Chance references for the per-recording share above 1: single draws against the 8-draw mean
    # (for the recording as it is and one-realization arms), and an 8-draw mean against another
    # (for arms that are themselves means of 8 draws).
    singles = [per_rec(f"circular_single_{d}", "circular")[0] for d in range(N_SINGLE)
               if f"circular_single_{d}" in arms]
    if singles:
        s = np.concatenate(singles)
        out["null_single_draw"] = dict(median=np.nanmedian(s, axis=0).tolist(),
                                       share_above_1=np.nanmean(s > 1, axis=0).tolist())
    if "circular_ref8" in arms:
        s = per_rec("circular_ref8", "circular")[0]
        out["null_8_draw_mean"] = dict(median=np.nanmedian(s, axis=0).tolist(),
                                       share_above_1=np.nanmean(s > 1, axis=0).tolist())
    if "circular_mask" in arms and "circular_minus_coact" in arms:
        out["removal_null_choice"] = {
            arm: dict(mask_matched=_var_ratio(rows, arm).tolist(),
                      mismatched=pooled(rows, arm, null="circular_minus_coact")[1].tolist(),
                      mask_matched_detrended=pooled(rows, arm, detrended=True)[1].tolist(),
                      mismatched_detrended=pooled(rows, arm, detrended=True,
                                                  null="circular_minus_coact")[1].tolist())
            for arm in ("minus_coact", "minus_coact_block_120") if arm in arms}
        out["removal_null_choice_note"] = (
            "mask_matched divides by the circular shift of the full trains with the recording's "
            "own episodes then cut out; mismatched divides by the circular shift of the already-"
            "removed trains, which scatters each ROI's holes to its own phase")
    corr = np.array([r.get("pairwise_count_corr_1min", np.nan) for r in rows], float)
    out["pairwise_count_corr_1min"] = dict(median=float(np.nanmedian(corr)),
                                           q25=float(np.nanpercentile(corr, 25)),
                                           q75=float(np.nanpercentile(corr, 75)))
    out["active_roi_share_median"] = float(np.median(
        n_active / np.array([r["n_roi"] for r in rows], float)))
    weight = np.array([unpack(r["arms"]["real"])["exp"][1:].sum() for r in rows])
    heavy = set(np.argsort(weight)[-5:].tolist())
    rest = [r for i, r in enumerate(rows) if i not in heavy]
    out["heaviest_five_share_of_pairs"] = float(np.sort(weight)[-5:].sum() / weight.sum())
    out["leave_heaviest_out"] = {}
    for arm in ("real", "rigid_20", "block_120", "minus_coact_block_120"):
        if arm not in arms:
            continue
        vweight = np.array([unpack(r["arms"][null_of(arm)])["var"][-1] for r in rows])
        vheavy = set(np.argsort(vweight)[-5:].tolist())
        vrest = [r for i, r in enumerate(rows) if i not in vheavy]
        out["leave_heaviest_out"][arm] = dict(
            var_ratio=_var_ratio(vrest, arm).tolist(), excess=pooled(rest, arm)[0].tolist(),
            heaviest_five_share_of_variance=float(np.sort(vweight)[-5:].sum() / vweight.sum()))
    out["leave_heaviest_out_note"] = ("var_ratio drops the five recordings with the largest "
                                      "1-minute variance under the arm's own null, which is the "
                                      "weight the count-variance figure gives them; excess drops "
                                      "the five with the most expected onset pairs, which is the "
                                      "weight the correlograms give them")
    if "share_removed" in rows[0]:
        sh = np.array([r["share_removed"] for r in rows])
        out["removal_share_pooled"] = float(np.sum(sh * weight) / weight.sum())
        out["removal_time_share_pooled"] = float(
            np.sum(np.array([r["episode_share_of_time"] for r in rows]) * weight) / weight.sum())
    return out


def flagged_contaminant_ids() -> list[str]:
    """The recordings the producer's own note says carry the motion-correction contaminant, read
    from ``current_export.toml`` rather than retyped. A view, never a filter: the export folder
    is the input, and the analysis keeps every recording in it."""
    import re
    import tomllib
    cfg = tomllib.loads((ROOT / "current_export.toml").read_text())
    for section in cfg.values():
        note = " ".join(section.get("note", "").split()) if isinstance(section, dict) else ""
        if "pinned" in note and "frame floor" in note:
            return sorted(set(re.findall(r"`(\d{8}_\d+)`", note)))
    return []


def flagged_sensitivity(rows, ids) -> dict:
    """The pooled 1-minute count-variance ratio with and without the producer-flagged recordings,
    overall and for each group that holds one, and the share of the pooled excess variance (arm
    variance minus its null's, summed over recordings) they carry. No identifiers kept."""
    flagged = [r for r in rows if r["recording_id"] in ids]
    if not flagged:
        return dict(n_flagged=0)
    rest = [r for r in rows if r["recording_id"] not in ids]
    arms = [a for a in ("real", "minus_coact_block_120") if a in rows[0]["arms"]]

    def excess_var(rs, arm):
        return sum(unpack(r["arms"][arm])["var"][-1] - unpack(r["arms"][null_of(arm)])["var"][-1]
                   for r in rs)

    groups = sorted({r["group"] for r in flagged if r.get("group")})

    def ratios(rs):
        return {arm: _var_ratio(rs, arm).tolist() for arm in arms}

    return dict(
        n_flagged=len(flagged),
        flagged_groups={g: sum(r.get("group") == g for r in flagged) for g in groups},
        all=ratios(rows), without=ratios(rest),
        share_of_excess_variance_1min={arm: float(excess_var(flagged, arm) / excess_var(rows, arm))
                                       for arm in arms},
        by_group={g: dict(all=ratios([r for r in rows if r.get("group") == g]),
                          without=ratios([r for r in rest if r.get("group") == g]))
                  for g in groups})


def group_checks(rows, n_boot: int, key) -> dict:
    """Per group: the per-recording count-variance medians and the pooled ratios, so no pooled
    headline stands without its breakdown (FOUNDATIONS §9)."""
    out = {}
    for g in sorted({r["group"] for r in rows if r.get("group")}):
        rs = [r for r in rows if r["group"] == g]
        c = checks(rs, max(50, n_boot // 5), (*key, g))
        out[g] = dict(per_recording=c["per_recording"],
                      pooled_var_ratio={arm: _var_ratio(rs, arm).tolist()
                                        for arm in ("real", "minus_coact_block_120")
                                        if arm in rs[0]["arms"]})
    return out


def summary_only(R) -> dict:
    """What the repo keeps: pooled curves and counts, no recording or mouse identifiers and no
    per-recording rows. ``results.json`` stays in the darkroom (FOUNDATIONS §5)."""
    keep = {k: v for k, v in R.items() if k not in ("folders", "synthetic")}
    keep["folders"] = {}
    for name, F in R["folders"].items():
        rows = F["rows"]
        entry = dict(summary=F["summary"], by_group=F["by_group"], checks=F.get("checks"),
                     checks_by_group=F.get("checks_by_group"),
                     flagged_contaminant=F.get("flagged_contaminant"),
                     analysed_hours=sum(r["analysed_sec"] for r in rows) / 3600.0,
                     window_min_range=[min(r["analysed_sec"] + 2 * TRIM_SEC for r in rows) / 60,
                                       max(r["analysed_sec"] + 2 * TRIM_SEC for r in rows) / 60],
                     median_rois=float(np.median([r["n_roi"] for r in rows])),
                     lead_in_sec_median=float(np.median([r["lead_in_sec"] for r in rows])),
                     n_skipped=len(F["skipped"]))
        if "share_removed" in rows[0]:
            entry["coact"] = dict(
                share_onsets_removed_median=float(np.median([r["share_removed"] for r in rows])),
                share_onsets_removed_mean=float(np.mean([r["share_removed"] for r in rows])),
                events_per_10min_median=float(np.median([r["events_per_10min"] for r in rows])),
                events_per_10min_mean=float(np.mean([r["events_per_10min"] for r in rows])),
                episode_share_of_time_median=float(
                    np.median([r["episode_share_of_time"] for r in rows])))
        keep["folders"][name] = entry
    keep["synthetic"] = {w: dict(summary=D["summary"], share_removed_median=float(np.median(
        [r["share_removed"] for r in D["rows"] if r.get("share_removed") is not None] or [np.nan])))
        for w, D in R["synthetic"].items()}
    return keep


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--out", type=Path, default=None,
                    help=f"folder for results.json and summary.json; default <darkroom>/{FOLDER}")
    ap.add_argument("--limit", type=int, default=None, help="first N slices of each folder")
    ap.add_argument("--draws", type=int, default=8, help="surrogate draws per recording and arm")
    ap.add_argument("--boot", type=int, default=1000, help="mouse bootstrap resamples")
    ap.add_argument("--jobs", type=int, default=max(1, (os.cpu_count() or 2) - 2))
    ap.add_argument("--no-real", action="store_true")
    ap.add_argument("--no-synthetic", action="store_true")
    ap.add_argument("--resummarise", action="store_true",
                    help="recompute summaries and checks from an existing results.json in --out")
    a = ap.parse_args(argv)
    if a.out is None:
        from bugarach.paths import darkroom, unresolved_message
        a.out = darkroom(FOLDER, create=True)
        if a.out is None:
            raise SystemExit(unresolved_message("--out"))
    a.out.mkdir(parents=True, exist_ok=True)
    if a.resummarise:
        R = json.loads((a.out / "results.json").read_text())
        for name, F in R["folders"].items():
            role, stream = name.split("/")
            rows = F["rows"]
            F["summary"] = summarise(rows, a.boot, (role, stream))
            F["by_group"] = {g: summarise([r for r in rows if r["group"] == g], a.boot,
                                          (role, stream, g))
                             for g in sorted({r["group"] for r in rows if r["group"]})}
            F["checks"] = checks(rows, a.boot, (role, stream))
            F["checks_by_group"] = group_checks(rows, a.boot, (role, stream))
            F["flagged_contaminant"] = flagged_sensitivity(rows, flagged_contaminant_ids())
        (a.out / "results.json").write_text(json.dumps(R))
        (a.out / "summary.json").write_text(json.dumps(summary_only(R), indent=1))
        print(f"resummarised {a.out}")
        return
    t0 = time.time()
    R = dict(tag=TAG, lag_edges_sec=list(LAG_EDGES_SEC), var_bin_sec=list(VAR_BIN_SEC),
             J_sec=list(J_SEC), trim_sec=TRIM_SEC, block_sec=BLOCK_SEC, coact=COACT_NOTE,
             generator_spec=generator_spec(), ou_worlds=OU, draws=a.draws, jobs=a.jobs, folders={},
             synthetic={})
    with mp.Pool(a.jobs) as pool:
        if not a.no_real:
            for role, stream in FOLDERS:
                recs, skipped, declares_regions = load(role, stream, a.limit)
                rows = pool.map(real_task,
                                [(role, stream, r, a.draws, declares_regions) for r in recs])
                name = f"{role}/{stream}"
                R["folders"][name] = dict(
                    rows=rows, skipped=skipped, summary=summarise(rows, a.boot, (role, stream)),
                    by_group={g: summarise([r for r in rows if r["group"] == g], a.boot,
                                           (role, stream, g))
                              for g in sorted({r["group"] for r in rows if r["group"]})})
                R["folders"][name]["checks"] = checks(rows, a.boot, (role, stream))
                R["folders"][name]["checks_by_group"] = group_checks(rows, a.boot, (role, stream))
                R["folders"][name]["flagged_contaminant"] = flagged_sensitivity(
                    rows, flagged_contaminant_ids())
                print(f"{name}: {len(rows)} recordings, {time.time() - t0:.0f} s", flush=True)
        if not a.no_synthetic:
            for world in SYN_WORLDS:
                rows = pool.map(syn_task, [(world, i, a.draws) for i in range(N_SYN)])
                R["synthetic"][world] = dict(rows=rows,
                                             summary=summarise(rows, a.boot, ("syn", world)))
                print(f"synthetic/{world}: {time.time() - t0:.0f} s", flush=True)
    R["elapsed_sec"] = time.time() - t0
    (a.out / "results.json").write_text(json.dumps(R))
    (a.out / "summary.json").write_text(json.dumps(summary_only(R), indent=1))
    print(f"wrote {a.out / 'results.json'} and summary.json")


if __name__ == "__main__":
    main()
