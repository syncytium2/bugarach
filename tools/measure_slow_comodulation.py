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
counts, the excess summed over **all** lags up to the window length is zero by construction
(Brody 1999, rule of thumb 3): a positive shoulder at some lags is paid back at others.

**What a counting detector sees** is the variance of the number of onsets in a bin, summed over
ROIs. ``count_variance`` stores, per arm and bin width, the pooled variance of that population
count; divided by the circular-shift arm's, it says how much more the population count swings
than it would if ROIs were independent.

**Arms**, each on the same window trimmed by ``TRIM_SEC`` at both ends (the largest *J*, so rigid
shift's dropped onsets never enter):

* ``real`` — the recording.
* ``circular`` — :func:`bugarach.surrogates.circular_shift`, the assessor's null: each ROI's train
  moved by its own lag with wrap. Removes every relation between ROIs; keeps each ROI's own
  temporal structure. Reads zero by construction.
* ``block_120`` — :func:`bugarach.surrogates.window_circular_shift` with 2-minute windows: the
  same shift inside each block. Keeps every ROI's count per block, so **any** shared covariation
  of 2-minute counts survives it — slow drift, and events too, since a block holding a large
  event holds an extra onset from each member. Measured on synthetic recordings it keeps a flat
  residue of planted events and part of a 20 s modulation. ⚠ It is registered as a known-bad
  control: every block acquires a seam.
* ``rigid_<J>`` — one offset per ROI uniform in [−J, J), ``floor(k + 0.5 + u)``, onsets pushed past
  either end dropped: ``tools/tube_self_supervised.py``'s ``rigid_frames``, imported. Measured: it
  spreads an event's coincidences over about ±2*J* rather than deleting them, reduces modulation
  faster than about *J*, and leaves slower drift in place.
* ``minus_coact`` (lab folder only) — every onset inside a CoactDetect episode removed, membership
  by CoactDetect's own half-open bins. CoactDetect fires only where at least three ROIs coincide,
  so two-ROI coincidences and events too weak for its test stay.
* ``minus_coact_block_120`` (lab folder only) — the block control applied after that removal.

**Synthetic worlds** (``--no-synthetic`` to skip):

* from the repository's own generator, ``docs/learned/generator_spec.json`` through
  :func:`bugarach.simulate.simulate_coordination` exactly as ``tools/fair_bakeoff.py`` builds
  benchmark recordings: ``benchmark`` (the whole spec), ``sim_background`` (per-ROI background
  only), ``sim_events`` (background plus planted events), ``sim_hot_window`` (background plus the
  spec's 300 s whole-field dense block, the promiscuity probe);
* illustrative, fitted to nothing: ``shared_20s`` and ``drift_5min``, every ROI's rate multiplied
  by one shared log-normal multiplier wandering on a 20 s or 5-minute timescale, no events.

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
FOLDER = "2026-09-17-slow-comodulation"
J_SEC = (1.6, 10.0, 20.0)
TRIM_SEC = max(J_SEC)
BLOCK_SEC = 120.0
MAX_LAG_SEC = 300.0
LAG_EDGES_SEC = tuple(float(x) for x in np.concatenate(
    [[0.0, 0.3, 0.6], np.geomspace(1.0, MAX_LAG_SEC, 18)]))
"""Short bins 0.3 s wide so every recording's frame interval (at most 0.119 s) puts at least two
lag frames in each; an edge at exactly 1 s; log-spaced from there to 300 s."""
VAR_BIN_SEC = (1.0, 10.0, 60.0)
FOLDERS = (("steps_excluded", "fast"), ("steps_excluded", "slow"), ("cossart", "events"))

COACT_SLOW = dict(int_win_sec=1.0, context_win_sec=120.0, alpha=1e-6, n_surrogates=100)
"""The fast stream uses ``bench.OPERATING_POINTS['coact']``. No retuned slow operating point
exists; this is the slow-stream point ``coact_detect``'s docstring states (1 s bins, 120 s
context, alpha 1e-6)."""

SPEC_PATH = ROOT / "docs" / "learned" / "generator_spec.json"
N_SYN = 24
OU = dict(n_roi=32, dur_sec=1200.0, dt=0.1, sigma=0.8, shared_20s=20.0, drift_5min=300.0)
"""The illustrative worlds take the generator spec's ROI count and background rate, a lab-like
1,200 s window, and a multiplier depth chosen to be visible."""


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
    """Variance of the population onset count in full bins of each width in ``VAR_BIN_SEC``."""
    pop = raster(trains, L).sum(axis=0)
    out = []
    for w in VAR_BIN_SEC:
        f = int(round(w / dt))
        nb = L // f
        out.append(float(pop[:nb * f].reshape(nb, f).sum(axis=1).var(ddof=1)) if nb > 1
                   else np.nan)
    return np.asarray(out)


def measure(trains, L: int, dt: float) -> np.ndarray:
    o, e = pair_counts(trains, L, dt)
    return np.concatenate([o, e, count_variance(trains, L, dt)])


def unpack(v) -> dict:
    nb = len(LAG_EDGES_SEC) - 1
    v = np.asarray(v, float)
    return dict(obs=v[:nb], exp=v[nb:2 * nb], var=v[2 * nb:])


# -- arms -------------------------------------------------------------------------------------

def trimmed(trains, L_full: int, trim: int):
    out = []
    for t in trains:
        t = np.asarray(t, np.int64)
        out.append(t[(t >= trim) & (t < L_full - trim)] - trim)
    return out, L_full - 2 * trim


def coact_removed(trains, L_full: int, dt: float, stream: str):
    """Onsets inside any CoactDetect episode removed, membership by its half-open bin span."""
    from bugarach.bench import OPERATING_POINTS
    from bugarach.detectors.coact import coact_detect
    params = dict(OPERATING_POINTS["coact"].params) if stream == "fast" else dict(COACT_SLOW)
    sec = [np.asarray(t, float) * dt for t in trains]
    det = coact_detect(sec, (0.0, L_full * dt), **params)
    out, n_in, n_out = [], 0, 0
    for t, ts in zip(trains, sec):
        inside = np.zeros(t.size, bool)
        for a, w in zip(det.onset_sec, det.width_sec):
            inside |= (ts >= a) & (ts < a + w)
        out.append(np.asarray(t, np.int64)[~inside])
        n_in += t.size
        n_out += int(inside.sum())
    return out, dict(coact_events=int(det.n_events), share_removed=n_out / max(n_in, 1),
                     events_per_10min=det.n_events / (L_full * dt / 600.0),
                     episode_share_of_time=float(np.sum(det.width_sec)) / (L_full * dt))


def arms_for(trains_full, L_full: int, dt: float, key, draws: int, stream: str | None):
    trim = int(np.ceil(TRIM_SEC / dt))
    tr, L = trimmed(trains_full, L_full, trim)
    block = int(round(BLOCK_SEC / dt))
    res = {"real": measure(tr, L, dt)}

    def mean_over(fn, name):
        return np.mean([measure(fn(d), L, dt) for d in range(draws)], axis=0)

    res["circular"] = mean_over(
        lambda d: sg.circular_shift(tr, (0, L), (TAG, *key, "circular", d)).trains, "circular")
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
        removed, extra = coact_removed(trains_full, L_full, dt, stream)
        rt = trimmed(removed, L_full, trim)[0]
        res["minus_coact"] = measure(rt, L, dt)
        res["minus_coact_block_120"] = mean_over(
            lambda d: sg.window_circular_shift(rt, (0, L), (TAG, *key, "coact-block", d),
                                               analysis_window=block).trains, "cb")
    return {k: list(map(float, v)) for k, v in res.items()}, extra, L * dt


# -- real recordings --------------------------------------------------------------------------

def load(role: str, stream: str, limit: int | None):
    """The lab folder is refused anything but its declared baseline (as ``tools/look_rigid_shift.py``
    refuses it)."""
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
    lead_in = 0
    if role != "steps_excluded":
        firsts = [int(t[0]) for t in rec.trains if len(t)]
        if firsts:
            lead_in = min(firsts) - a
            a = min(firsts)
    trains = [np.asarray(t, np.int64) - a for t in rec.trains]
    arms, extra, used_sec = arms_for(trains, b - a, rec.dt, (role, stream, rec.recording_id),
                                     draws, stream if role == "steps_excluded" else None)
    return dict(role=role, stream=stream, recording_id=rec.recording_id, mouse=rec.mouse,
                group=rec.group, dt=rec.dt, n_roi=len(rec.trains),
                n_onsets=int(sum(len(t) for t in rec.trains)), analysed_sec=used_sec,
                lead_in_sec=lead_in * rec.dt, arms=arms, **extra)


# -- synthetic worlds -------------------------------------------------------------------------

def generator_spec() -> dict:
    return json.loads(SPEC_PATH.read_text())["generator"]


SIM_WORLDS = {
    "benchmark": {},
    "sim_background": dict(hot_rate_hz=0.0, n_distractors=0, n_per_level=(0, 0, 0)),
    "sim_events": dict(hot_rate_hz=0.0, n_distractors=0),
    "sim_hot_window": dict(n_distractors=0, n_per_level=(0, 0, 0)),
}
OU_WORLDS = ("shared_20s", "drift_5min")
SYN_WORLDS = tuple(SIM_WORLDS) + OU_WORLDS


def _ou_multiplier(n_frames: int, dt: float, r, tau: float) -> np.ndarray:
    """Mean-one log-normal multiplier driven by an Ornstein-Uhlenbeck process."""
    a = np.exp(-dt / tau)
    z = np.empty(n_frames)
    z[0] = r.randn()
    e = r.randn(n_frames) * np.sqrt(1 - a * a)
    for i in range(1, n_frames):
        z[i] = a * z[i - 1] + e[i]
    m = np.exp(OU["sigma"] * z - 0.5 * OU["sigma"] ** 2)
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
    m = _ou_multiplier(L, dt, r, OU[world])
    trains = [np.flatnonzero(r.random_sample(L) < p * m) for _ in range(OU["n_roi"])]
    return trains, L, dt


def syn_task(args):
    world, i, draws = args
    trains, L, dt = synthetic_recording(world, i)
    arms, _, used_sec = arms_for(trains, L, dt, ("syn", world, i), draws, None)
    return dict(world=world, i=i, mouse=f"syn{i}", dt=dt, L=L, analysed_sec=used_sec,
                n_roi=len(trains), n_onsets=int(sum(len(t) for t in trains)), arms=arms,
                raster=[list(map(int, t)) for t in trains] if i == 0 else None)


# -- summary ----------------------------------------------------------------------------------

def pooled(rows, arm):
    """(excess per lag bin, count-variance ratio to the circular arm per bin width)."""
    U = [unpack(r["arms"][arm]) for r in rows]
    C = [unpack(r["arms"]["circular"]) for r in rows]
    o = np.sum([u["obs"] for u in U], axis=0)
    e = np.sum([u["exp"] for u in U], axis=0)
    with np.errstate(invalid="ignore", divide="ignore"):
        return (o / e - 1.0,
                np.nansum([u["var"] for u in U], axis=0) / np.nansum([c["var"] for c in C], axis=0))


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
        with np.errstate(invalid="ignore"):
            out[arm] = dict(
                excess=ex.tolist(),
                lo=np.nanpercentile(bex, 2.5, axis=0).tolist(),
                hi=np.nanpercentile(bex, 97.5, axis=0).tolist(),
                excess_equal_mice=np.nanmean(per_mouse, axis=0).tolist(),
                excess_pairs=(o - e).tolist(),
                var_ratio=vr.tolist(),
                var_lo=np.nanpercentile(bvr, 2.5, axis=0).tolist(),
                var_hi=np.nanpercentile(bvr, 97.5, axis=0).tolist())
    exp_by_mouse = np.array([np.sum([unpack(r["arms"]["real"])["exp"][1:].sum()
                                     for r in by_mouse[m]]) for m in mice])
    top = float(exp_by_mouse.max() / exp_by_mouse.sum()) if exp_by_mouse.sum() else None
    return dict(n_recordings=len(rows), n_mice=len(mice), top_mouse_share_of_pairs=top, arms=out)


CONTRASTS = (("real", "rigid_20"), ("real", "block_120"), ("real", "minus_coact_block_120"),
             ("minus_coact", "minus_coact_block_120"))


def _var_ratio(rows, arm):
    return pooled(rows, arm)[1]


def checks(rows, n_boot: int, key) -> dict:
    """The comparisons the page rests on, each able to fail.

    * ``paired`` — pooled count-variance ratio of one arm minus another, per bin width, with a mouse
      bootstrap drawing the same mice for both arms.
    * ``per_recording`` — each recording's own count-variance ratio (arm ÷ its circular arm): the
      median, the quartiles and the share above 1, so a pooled number can be seen not to rest on a
      few recordings.
    * ``leave_heaviest_out`` — the pooled ratio with the five recordings carrying the most onset
      pairs dropped.
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
    for arm in ("real", "rigid_20", "block_120", "minus_coact_block_120"):
        if arm not in arms:
            continue
        with np.errstate(invalid="ignore", divide="ignore"):
            per = np.array([unpack(r["arms"][arm])["var"] / unpack(r["arms"]["circular"])["var"]
                            for r in rows])
        out["per_recording"][arm] = dict(
            median=np.nanmedian(per, axis=0).tolist(),
            q25=np.nanpercentile(per, 25, axis=0).tolist(),
            q75=np.nanpercentile(per, 75, axis=0).tolist(),
            share_above_1=np.nanmean(per > 1, axis=0).tolist())
    weight = np.array([unpack(r["arms"]["real"])["exp"][1:].sum() for r in rows])
    heavy = set(np.argsort(weight)[-5:].tolist())
    rest = [r for i, r in enumerate(rows) if i not in heavy]
    out["heaviest_five_share_of_pairs"] = float(np.sort(weight)[-5:].sum() / weight.sum())
    out["leave_heaviest_out"] = {arm: dict(var_ratio=_var_ratio(rest, arm).tolist(),
                                           excess=pooled(rest, arm)[0].tolist())
                                 for arm in ("real", "rigid_20", "block_120",
                                             "minus_coact_block_120") if arm in arms}
    if "share_removed" in rows[0]:
        sh = np.array([r["share_removed"] for r in rows])
        out["removal_share_pooled"] = float(np.sum(sh * weight) / weight.sum())
        out["removal_time_share_pooled"] = float(
            np.sum(np.array([r["episode_share_of_time"] for r in rows]) * weight) / weight.sum())
    return out


def summary_only(R) -> dict:
    """What the repo keeps: pooled curves and counts, no recording or mouse identifiers and no
    per-recording rows. ``results.json`` stays in the darkroom (FOUNDATIONS §5)."""
    keep = {k: v for k, v in R.items() if k not in ("folders", "synthetic")}
    keep["folders"] = {}
    for name, F in R["folders"].items():
        rows = F["rows"]
        entry = dict(summary=F["summary"], by_group=F["by_group"], checks=F.get("checks"),
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
    keep["synthetic"] = {w: dict(summary=D["summary"]) for w, D in R["synthetic"].items()}
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
        (a.out / "results.json").write_text(json.dumps(R))
        (a.out / "summary.json").write_text(json.dumps(summary_only(R), indent=1))
        print(f"resummarised {a.out}")
        return
    t0 = time.time()
    R = dict(tag=TAG, lag_edges_sec=list(LAG_EDGES_SEC), var_bin_sec=list(VAR_BIN_SEC),
             J_sec=list(J_SEC), trim_sec=TRIM_SEC, block_sec=BLOCK_SEC, coact_slow=COACT_SLOW,
             generator_spec=generator_spec(), ou_worlds=OU, draws=a.draws, folders={},
             synthetic={})
    with mp.Pool(a.jobs) as pool:
        if not a.no_real:
            for role, stream in FOLDERS:
                recs, skipped = load(role, stream, a.limit)
                rows = pool.map(real_task, [(role, stream, r, a.draws) for r in recs])
                name = f"{role}/{stream}"
                R["folders"][name] = dict(
                    rows=rows, skipped=skipped, summary=summarise(rows, a.boot, (role, stream)),
                    by_group={g: summarise([r for r in rows if r["group"] == g], a.boot,
                                           (role, stream, g))
                              for g in sorted({r["group"] for r in rows if r["group"]})})
                R["folders"][name]["checks"] = checks(rows, a.boot, (role, stream))
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
