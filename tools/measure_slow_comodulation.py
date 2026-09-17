#!/usr/bin/env python3
"""Where shared structure between ROIs lives in time: the population cross-correlogram.

    python tools/measure_slow_comodulation.py --out <folder>                 # real + synthetic
    python tools/measure_slow_comodulation.py --out <folder> --limit 6 --draws 2   # smoke

**The question.** Two things make many ROIs active together. A *coordinated event* puts their
onsets within a fraction of a second of each other. *Slow shared modulation* raises and lowers
every ROI's rate together over tens of seconds, without aligning any onsets. A detector trained
to tell a recording from its rigid shift is paid for both, because rigid shift at 10–20 s removes
both. This measures how much of each the recordings carry, and what each displacement removes.

**The statistic.** For every ordered pair of distinct ROIs, count onset pairs at lag *k* frames and
divide by the count expected if the two ROIs were independent with their observed totals:

    ratio(k) = sum_{i != j} sum_t x_i(t) x_j(t + k)  /  sum_{i != j} n_i n_j (L - k) / L**2

``ratio - 1`` is the **excess coincidence** at that lag: 0 when ROIs are independent, 1 when
onset pairs at that lag are twice as common as chance. Numerator and denominator are summed within
log-spaced lag bins and over recordings before dividing, so a recording carries weight in
proportion to its onset pairs. A coordinated event makes a narrow peak at short lags; shared
modulation on a timescale *T* makes a shoulder out to roughly *T*.

**Arms**, each on the same trimmed window (``TRIM_SEC`` off both ends, the largest *J*, so rigid
shift's dropped onsets never enter any arm):

* ``real`` — the recording.
* ``circular`` — each ROI's train shifted by its own uniform lag with wrap: every cross-ROI
  relation removed at every timescale, each ROI's own temporal structure kept. The null.
* ``block_120`` — each ROI circularly shifted within each 2-minute block by its own lag. It keeps
  every ROI's count per block, so shared drift slower than 2 minutes survives it; the difference
  between ``real`` and this arm is the shared structure faster than 2 minutes.
* ``rigid_<J>`` — one offset per ROI uniform in [−J, J), ``floor(k + 0.5 + u)``, onsets pushed
  past either end of the baseline window dropped, then trimmed: exactly
  ``tools/tube_self_supervised.py``'s ``rigid_frames``, which is imported, not re-derived.
* ``minus_coact`` (lab folder only) — the recording with every onset inside a CoactDetect episode
  removed. ⚠ CoactDetect fires only where at least three ROIs coincide, so this removes neither
  two-ROI coincidences nor events too weak to pass its test, and it removes every onset in the
  episode's span, members or not.

**Synthetic worlds** (``--synthetic``, on by default) sized like the lab fast stream, so each
shape can be recognised: independent ROIs; planted sub-second events; shared slow modulation with
no events on a 20 s timescale; shared drift on a 5-minute timescale; per-ROI slow modulation (the kind `simulate.py` draws, one series per ROI); events plus
shared modulation. Their parameters are illustrative, chosen to be visible, and fitted to nothing.

Baseline windows only: the lab folder is refused anything but its declared baseline region.
Every random key carries ``TAG``.
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

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from bugarach import surrogate_stats as ss  # noqa: E402
from tube_self_supervised import rigid_frames  # noqa: E402

TAG = "slow-comodulation-2026-09-17"
J_SEC = (1.6, 10.0, 20.0)
TRIM_SEC = max(J_SEC)
BLOCK_SEC = 120.0
"""The block control keeps each ROI's count in every 2-minute block. What survives it is shared
change slower than 2 minutes — a drift across the recording — and what it removes is everything
faster, events and minute-scale modulation alike."""
MAX_LAG_SEC = 300.0
LAG_EDGES_SEC = tuple(float(x) for x in np.concatenate(
    [[0.0], np.geomspace(0.25, MAX_LAG_SEC, 22)]))
"""The first bin holds lags under 0.25 s — zero, one and two frames on the lab folder. The rest
are log-spaced to 300 s."""

COACT_PARAMS = {
    "fast": dict(int_win_sec=2.0, context_win_sec=60.0, alpha=1e-4, n_surrogates=100),
    "slow": dict(int_win_sec=1.0, context_win_sec=120.0, alpha=1e-6, n_surrogates=100),
}
"""Fast is ``bench.OPERATING_POINTS['coact']``. Slow is the explore_sce viewer's SLOW point, as
``coact_detect``'s docstring states it; no retuned slow point exists."""

FOLDERS = (("steps_excluded", "fast"), ("steps_excluded", "slow"), ("cossart", "events"))

SYN = dict(n_rec=24, n_roi=32, dur_sec=1200.0, dt=0.1, rate_hz=0.0097,
           n_events=32, event_rois=7, event_jitter_sec=0.3,
           mod_tau_sec=20.0, drift_tau_sec=300.0, mod_sigma=0.8)
"""Sized like the lab fast stream: its median ROI count (32), baseline length (1200 s), median
per-ROI rate (0.0097 Hz, `peek` of the export folder on 2026-09-17) and CoactDetect's 2.70 events
per 10 minutes on it. The event size, jitter and the modulation's timescale and depth are
illustrative."""


def seed31(*key) -> int:
    return int(ss.seed_of((TAG,) + tuple(str(k) for k in key)) & 0x7FFFFFFF)


# -- the statistic ----------------------------------------------------------------------------

def _autocorr_rows(X: np.ndarray, max_lag: int) -> np.ndarray:
    """Non-circular autocorrelation sum_t x(t) x(t+k), k = 0..max_lag, summed over rows."""
    L = X.shape[1]
    nfft = 1 << int(np.ceil(np.log2(2 * L)))
    out = np.zeros(max_lag + 1)
    for a in range(0, X.shape[0], 64):
        f = np.fft.rfft(X[a:a + 64], n=nfft, axis=1)
        ac = np.fft.irfft(f * np.conj(f), n=nfft, axis=1)[:, :max_lag + 1]
        out += ac.sum(axis=0)
    return out


def lag_bins(dt: float, max_lag: int) -> np.ndarray:
    """Bin index per lag frame; -1 past the last edge."""
    k_sec = np.arange(max_lag + 1) * dt
    idx = np.searchsorted(np.asarray(LAG_EDGES_SEC), k_sec, side="right") - 1
    idx[k_sec >= LAG_EDGES_SEC[-1]] = -1
    return idx


def pair_counts(trains, L: int, dt: float) -> tuple[np.ndarray, np.ndarray]:
    """(observed, expected) cross-ROI onset pairs per lag bin, for frame trains inside [0, L)."""
    max_lag = min(int(round(MAX_LAG_SEC / dt)), L - 1)
    X = np.zeros((len(trains), L))
    for r, t in enumerate(trains):
        t = np.asarray(t, np.int64)
        t = t[(t >= 0) & (t < L)]
        np.add.at(X[r], t, 1.0)
    n = X.sum(axis=1)
    obs = _autocorr_rows(X.sum(axis=0, keepdims=True), max_lag) - _autocorr_rows(X, max_lag)
    k = np.arange(max_lag + 1)
    exp = (n.sum() ** 2 - (n ** 2).sum()) * (L - k) / L ** 2
    idx = lag_bins(dt, max_lag)
    nb = len(LAG_EDGES_SEC) - 1
    ok = idx >= 0
    return (np.bincount(idx[ok], obs[ok], minlength=nb),
            np.bincount(idx[ok], exp[ok], minlength=nb))


# -- arms -------------------------------------------------------------------------------------

def trimmed(trains, L_full: int, trim: int):
    return [np.asarray(t, np.int64)[(np.asarray(t) >= trim) & (np.asarray(t) < L_full - trim)]
            - trim for t in trains], L_full - 2 * trim


def circular(trains, L: int, rng):
    lags = rng.randint(0, L, size=len(trains))
    return [np.sort((np.asarray(t, np.int64) + s) % L) for t, s in zip(trains, lags)]


def coact_removed(trains, L_full: int, dt: float, stream: str):
    """Onsets inside any CoactDetect episode removed, and the share of onsets that was."""
    from bugarach.detectors.coact import coact_detect
    sec = [np.asarray(t, float) * dt for t in trains]
    det = coact_detect(sec, (0.0, L_full * dt), **COACT_PARAMS[stream])
    spans = np.c_[det.onset_sec, det.onset_sec + det.width_sec]
    out, n_in, n_out = [], 0, 0
    for t in trains:
        t = np.asarray(t, np.int64)
        ts = t * dt
        inside = np.zeros(t.size, bool)
        for a, b in spans:
            inside |= (ts >= a) & (ts <= b)
        out.append(t[~inside])
        n_in += t.size
        n_out += int(inside.sum())
    return out, dict(n_events=int(det.n_events), share_removed=n_out / max(n_in, 1),
                     events_per_10min=det.n_events / (L_full * dt / 600.0))


def block_circular(trains, L: int, block: int, rng):
    """Each ROI circularly shifted within each block by its own lag: every cross-ROI relation
    faster than the block is removed; each ROI's count in every block, so any shared change in
    rate slower than the block, is kept."""
    out = []
    for t in trains:
        t = np.asarray(t, np.int64)
        parts = []
        for a in range(0, L, block):
            b = min(a + block, L)
            s = t[(t >= a) & (t < b)] - a
            parts.append((s + rng.randint(0, b - a)) % (b - a) + a)
        out.append(np.sort(np.concatenate(parts)) if parts else t)
    return out


def arms_for(trains_full, L_full: int, dt: float, key, draws: int, stream: str | None):
    trim = int(np.ceil(TRIM_SEC / dt))
    tr, L = trimmed(trains_full, L_full, trim)
    res = {"real": pair_counts(tr, L, dt)}
    acc = np.zeros((2, len(LAG_EDGES_SEC) - 1))
    for d in range(draws):
        acc += np.array(pair_counts(circular(tr, L, np.random.RandomState(
            seed31(*key, "circular", d))), L, dt))
    res["circular"] = tuple(acc / draws)
    block = int(round(BLOCK_SEC / dt))
    acc[:] = 0
    for d in range(draws):
        acc += np.array(pair_counts(block_circular(tr, L, block, np.random.RandomState(
            seed31(*key, "block", d))), L, dt))
    res[f"block_{BLOCK_SEC:g}"] = tuple(acc / draws)
    for J in J_SEC:
        acc[:] = 0
        for d in range(draws):
            rng = np.random.RandomState(seed31(*key, "rigid", J, d))
            s = rigid_frames(trains_full, L_full, J / dt, rng)
            acc += np.array(pair_counts(trimmed(s, L_full, trim)[0], L, dt))
        res[f"rigid_{J:g}"] = tuple(acc / draws)
    extra = {}
    if stream in COACT_PARAMS:
        removed, extra = coact_removed(trains_full, L_full, dt, stream)
        res["minus_coact"] = pair_counts(trimmed(removed, L_full, trim)[0], L, dt)
    return {k: [list(map(float, v[0])), list(map(float, v[1]))] for k, v in res.items()}, extra, L * dt


# -- real recordings --------------------------------------------------------------------------

def load(role: str, stream: str, limit: int | None):
    from bugarach import dataset
    from bugarach.io import load_folder
    slices = load_folder(dataset.current(role))
    if limit:
        slices = slices[:limit]
    recs, skipped = ss.recordings_from_slices(slices, stream)
    if role == "steps_excluded":
        refused = [r.recording_id for r in recs
                   if not r.window_source.startswith("baseline region")]
        if refused:
            raise SystemExit(f"refusing non-baseline windows in {stream}: {refused}")
    return recs, skipped


def real_task(args):
    role, stream, rec, draws = args
    a, b = rec.window
    trains = [np.asarray(t, np.int64) - a for t in rec.trains]
    arms, extra, used_sec = arms_for(trains, b - a, rec.dt, (role, stream, rec.recording_id),
                                     draws, stream if role == "steps_excluded" else None)
    return dict(role=role, stream=stream, recording_id=rec.recording_id, mouse=rec.mouse,
                group=rec.group, dt=rec.dt, n_roi=len(rec.trains),
                n_onsets=int(sum(len(t) for t in rec.trains)), analysed_sec=used_sec,
                arms=arms, **extra)


# -- synthetic worlds -------------------------------------------------------------------------

def _ou_multiplier(n_frames: int, dt: float, rng, tau: float) -> np.ndarray:
    """Mean-one log-normal rate multiplier driven by an Ornstein-Uhlenbeck process."""
    sig = SYN["mod_sigma"]
    a = np.exp(-dt / tau)
    z = np.empty(n_frames)
    z[0] = rng.randn()
    e = rng.randn(n_frames) * np.sqrt(1 - a * a)
    for i in range(1, n_frames):
        z[i] = a * z[i - 1] + e[i]
    m = np.exp(sig * z - 0.5 * sig * sig)
    return m / m.mean()


def synthetic_recording(world: str, seed: int):
    rng = np.random.RandomState(seed)
    dt, nR = SYN["dt"], SYN["n_roi"]
    L = int(round(SYN["dur_sec"] / dt))
    p = SYN["rate_hz"] * dt
    shared = (_ou_multiplier(L, dt, rng, SYN["mod_tau_sec"]) if "shared" in world else
              _ou_multiplier(L, dt, rng, SYN["drift_tau_sec"]) if "drift" in world else None)
    trains = []
    for _ in range(nR):
        m = shared if shared is not None else (
            _ou_multiplier(L, dt, rng, SYN["mod_tau_sec"]) if "per_roi" in world else 1.0)
        trains.append(list(np.flatnonzero(rng.random_sample(L) < p * m)))
    if "events" in world:
        times = rng.uniform(TRIM_SEC + 5, SYN["dur_sec"] - TRIM_SEC - 5, SYN["n_events"])
        for t0 in times:
            for r in rng.choice(nR, SYN["event_rois"], replace=False):
                f = int(np.floor((t0 + SYN["event_jitter_sec"] * rng.randn()) / dt + 0.5))
                if 0 <= f < L:
                    trains[r].append(f)
    return [np.unique(np.asarray(t, np.int64)) for t in trains], L


SYN_WORLDS = ("independent", "events", "shared", "drift", "per_roi", "events_shared")


def syn_task(args):
    world, i, draws = args
    trains, L = synthetic_recording(world, seed31("syn", world, i))
    arms, _, used_sec = arms_for(trains, L, SYN["dt"], ("syn", world, i), draws, None)
    raster = None
    if i == 0:
        raster = [list(map(int, t)) for t in trains]
    return dict(world=world, i=i, dt=SYN["dt"], L=L, analysed_sec=used_sec, arms=arms,
                raster=raster)


# -- summary ----------------------------------------------------------------------------------

def pooled(rows, arm):
    o = np.sum([r["arms"][arm][0] for r in rows], axis=0)
    e = np.sum([r["arms"][arm][1] for r in rows], axis=0)
    with np.errstate(invalid="ignore", divide="ignore"):
        return o / e - 1.0


def summarise(rows, n_boot: int, key):
    arms = list(rows[0]["arms"])
    mice = sorted({r["mouse"] for r in rows})
    by_mouse = {m: [r for r in rows if r["mouse"] == m] for m in mice}
    rng = np.random.RandomState(seed31("boot", *key))
    out = {}
    for arm in arms:
        boots = []
        for _ in range(n_boot):
            pick = rng.randint(0, len(mice), len(mice))
            boots.append(pooled([r for j in pick for r in by_mouse[mice[j]]], arm))
        boots = np.array(boots)
        o = np.sum([r["arms"][arm][0] for r in rows], axis=0)
        e = np.sum([r["arms"][arm][1] for r in rows], axis=0)
        out[arm] = dict(excess=list(map(float, pooled(rows, arm))),
                        lo=list(map(float, np.nanpercentile(boots, 2.5, axis=0))),
                        hi=list(map(float, np.nanpercentile(boots, 97.5, axis=0))),
                        excess_pairs=list(map(float, o - e)))
    return dict(n_recordings=len(rows), n_mice=len(mice), arms=out)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--out", required=True, type=Path,
                    help="folder for results.json; the figure tool reads it from there")
    ap.add_argument("--limit", type=int, default=None, help="first N slices of each folder")
    ap.add_argument("--draws", type=int, default=8, help="surrogate draws per recording and arm")
    ap.add_argument("--boot", type=int, default=1000, help="mouse bootstrap resamples")
    ap.add_argument("--jobs", type=int, default=max(1, (os.cpu_count() or 2) - 2))
    ap.add_argument("--no-real", action="store_true")
    ap.add_argument("--no-synthetic", action="store_true")
    a = ap.parse_args(argv)
    a.out.mkdir(parents=True, exist_ok=True)
    t0 = time.time()
    R = dict(tag=TAG, lag_edges_sec=list(LAG_EDGES_SEC), J_sec=list(J_SEC), trim_sec=TRIM_SEC,
             coact_params=COACT_PARAMS, synthetic_spec=SYN, draws=a.draws, folders={},
             synthetic={})
    with mp.Pool(a.jobs) as pool:
        if not a.no_real:
            for role, stream in FOLDERS:
                recs, skipped = load(role, stream, a.limit)
                rows = pool.map(real_task, [(role, stream, r, a.draws) for r in recs])
                name = f"{role}/{stream}"
                R["folders"][name] = dict(rows=rows, skipped=skipped,
                                          summary=summarise(rows, a.boot, (role, stream)))
                groups = sorted({r["group"] for r in rows if r["group"]})
                R["folders"][name]["by_group"] = {
                    g: summarise([r for r in rows if r["group"] == g], a.boot, (role, stream, g))
                    for g in groups}
                print(f"{name}: {len(rows)} recordings, {time.time() - t0:.0f} s", flush=True)
        if not a.no_synthetic:
            for world in SYN_WORLDS:
                rows = pool.map(syn_task, [(world, i, a.draws) for i in range(SYN["n_rec"])])
                for r in rows:
                    r["mouse"] = f"syn{r['i']}"
                R["synthetic"][world] = dict(rows=rows, summary=summarise(rows, a.boot,
                                                                           ("syn", world)))
                print(f"synthetic/{world}: {time.time() - t0:.0f} s", flush=True)
    R["elapsed_sec"] = time.time() - t0
    (a.out / "results.json").write_text(json.dumps(R))
    (a.out / "summary.json").write_text(json.dumps(summary_only(R), indent=1))
    print(f"wrote {a.out / 'results.json'} and summary.json")


def peak_and_shoulder(S, cut_sec: float = 1.0) -> dict:
    """Excess onset pairs at lags under ``cut_sec`` and from there to the longest lag, per arm."""
    lo = np.asarray(LAG_EDGES_SEC[:-1])
    out = {}
    for arm, v in S["arms"].items():
        p = np.asarray(v["excess_pairs"])
        a, b = float(p[lo < cut_sec].sum()), float(p[lo >= cut_sec].sum())
        out[arm] = dict(under=a, beyond=b, share_beyond=b / (a + b) if a + b else None)
    return out


def summary_only(R) -> dict:
    """What the repo keeps: pooled curves and counts, no recording or mouse identifiers and no
    per-recording rows (FOUNDATIONS §5). ``results.json`` stays in the darkroom."""
    keep = {k: v for k, v in R.items() if k not in ("folders", "synthetic")}
    keep["folders"] = {}
    for name, F in R["folders"].items():
        rows = F["rows"]
        entry = dict(summary=F["summary"], by_group=F["by_group"],
                     peak_and_shoulder=peak_and_shoulder(F["summary"]),
                     analysed_hours=sum(r["analysed_sec"] for r in rows) / 3600.0,
                     median_rois=float(np.median([r["n_roi"] for r in rows])),
                     n_skipped=len(F["skipped"]))
        if "share_removed" in rows[0]:
            sh = [r["share_removed"] for r in rows]
            ev = [r["events_per_10min"] for r in rows]
            entry["coact"] = dict(share_onsets_removed_median=float(np.median(sh)),
                                  share_onsets_removed_mean=float(np.mean(sh)),
                                  events_per_10min_median=float(np.median(ev)))
        keep["folders"][name] = entry
    keep["synthetic"] = {w: dict(summary=D["summary"]) for w, D in R["synthetic"].items()}
    return keep


if __name__ == "__main__":
    main()
