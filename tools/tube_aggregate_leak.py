#!/usr/bin/env python3
"""Can a model that sees only what `tube` sees tell a recording from its rigid shift?

    python tools/tube_aggregate_leak.py --out <folder>
    python tools/tube_aggregate_leak.py --out <folder> --limit 6 --quick

Stage 1 of the tube plan, and the aggregate-channel leak test that
``docs/todo/2026-09-12-tube-cannot-tell-a-count-leak-from-coordination.md`` names as the
condition before any label-free objective is built on `tube`. Exploratory.

**What the classifier sees.** `tube` averages the onset raster over cells before its first
kernel (``src/bugarach/learn/nets/tube.py``), so its whole input is the cells-mean trace. Here
that trace is built the same way — binary raster, each onset widened ±1 frame, mean over ROIs —
over each recording's whole generation window, then passed through tube's own
difference-of-Gaussians kernels (area-normalised centre minus surround, surround ratio 8) at
centre widths of 1–128 frames. Per interior 60 s window and per scale: the response's spread,
its 1st and 99th percentiles and its maximum; plus the trace's mean, spread and 99th
percentile. A linear forced choice with mouse-grouped folds and a refitting bootstrap, exactly
as the rigid-shift look scores its leak test (:mod:`look_rigid_shift`).

**Contrasts**, at each displacement *J*:

1. **real vs shared offset** — every ROI moved by one offset (:mod:`look_rigid_shift_controls`).
   Keeps coordination and slow shared modulation, moves counts across window edges exactly as
   rigid shift does. Anything above chance is a count or edge leak on tube's channel.
2. **unplanted twin vs its rigid shift** — synthetic, no coordination and no shared modulation,
   so nothing legitimate to find. Anything above chance is a leak.
3. **real vs rigid shift**, pooled and **per kernel scale** — what tube could learn, and at
   which timescale.
4. **planted twin vs its rigid shift** — the positive control: must separate.
"""

from __future__ import annotations

import argparse
import json
import multiprocessing as mp
import sys
import time
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import look_rigid_shift as lr                                # noqa: E402
import look_rigid_shift_controls as lc                       # noqa: E402
from bugarach import surrogate_stats as ss                   # noqa: E402
from bugarach import surrogates as sg                        # noqa: E402

TAG = "tube-aggregate-2026-09-15"
J_SEC = {"fast": (5.0, 10.0, 20.0, 40.0), "slow": (5.6, 11.2, 22.4, 44.8)}
CENTRES = (1, 2, 4, 8, 16, 32, 64, 128)
SURROUND_RATIO = 8.0
WIDEN = 1
N_TWINS = 20
PER_SCALE = ("sd", "p1", "p99", "max")


def seed31(*key) -> int:
    return int(ss.seed_of((TAG,) + tuple(key)) & 0x7FFFFFFF)


def dog_kernel(c: float, ratio: float = SURROUND_RATIO) -> np.ndarray:
    s = c * ratio
    half = int(np.ceil(3 * s))
    t = np.arange(-half, half + 1, dtype=float)
    centre = np.exp(-0.5 * (t / c) ** 2)
    surround = np.exp(-0.5 * (t / s) ** 2)
    return centre / centre.sum() - surround / surround.sum()


KERNELS = {c: dog_kernel(float(c)) for c in CENTRES}


def bright_trace(trains, window) -> np.ndarray:
    """Cells-mean of the binary raster over ``window``, each onset widened ±WIDEN frames."""
    s, e = int(window[0]), int(window[1])
    L = e - s
    acc = np.zeros(L, dtype=float)
    for t in trains:
        t = np.asarray(t, np.int64)
        t = t[(t >= s) & (t < e)] - s
        if t.size == 0:
            continue
        row = np.zeros(L, dtype=bool)
        for d in range(-WIDEN, WIDEN + 1):
            k = t + d
            row[k[(k >= 0) & (k < L)]] = True
        acc += row
    return acc / max(1, len(trains))


def window_features(trains, window, wins):
    """One row per window: trace mean, sd, p99; then per centre width sd, p1, p99, max."""
    b = bright_trace(trains, window)
    resp = {c: np.convolve(b, KERNELS[c], mode="same") for c in CENTRES}
    s = int(window[0])
    rows = []
    for a, e in wins:
        seg = b[a - s:e - s]
        row = [seg.mean(), seg.std(), np.percentile(seg, 99)]
        for c in CENTRES:
            r = resp[c][a - s:e - s]
            row += [r.std(), np.percentile(r, 1), np.percentile(r, 99), r.max()]
        rows.append(row)
    return np.asarray(rows)


def feature_names():
    names = ["trace_mean", "trace_sd", "trace_p99"]
    for c in CENTRES:
        names += [f"c{c}_{k}" for k in PER_SCALE]
    return names


def columns_for(scale):
    names = feature_names()
    if scale == "all":
        return np.arange(len(names))
    if scale == "trace":
        return np.array([i for i, n in enumerate(names) if n.startswith("trace_")])
    return np.array([i for i, n in enumerate(names) if n.startswith(f"c{scale}_")])


def score(Xr, Xs, groups, n_boot, seed, per_scale=True):
    out = {}
    scales = ["all", "trace"] + list(CENTRES) if per_scale else ["all"]
    for sc in scales:
        cols = columns_for(sc)
        p, dist = lr.refit_bootstrap(Xr[:, cols], Xs[:, cols], groups, groups,
                                     n_boot if sc == "all" else max(40, n_boot // 5), seed)
        out[str(sc)] = lr.summarize(p, dist)
    return out


def real_task(args):
    stream, J_sec, n_boot, limit = args
    recs, _ = lr.load(stream, limit)
    Xr, Xrig, Xsh, mice = [], [], [], []
    count_change = {"rigid_shift": [0, 0], "shared_shift": [0, 0]}
    for r in recs:
        wins = lr.interior_windows(r)
        if not wins:
            continue
        Jf = round(J_sec / r.dt, 9)
        rig = sg.generate("rigid_shift", r.trains, r.window,
                          (lr.TAG, "leak", r.recording_id, stream, "rigid_shift", Jf), J=Jf).trains
        sh, _, _ = lc.shared_shift(r.trains, r.window, ("leak", r.recording_id, stream, Jf), Jf)
        Xr.append(window_features(r.trains, r.window, wins))
        Xrig.append(window_features(rig, r.window, wins))
        Xsh.append(window_features(sh, r.window, wins))
        mice += [r.mouse] * len(wins)
        for name, tr in (("rigid_shift", rig), ("shared_shift", sh)):
            for a, e in wins:
                n_real = sum(int(((t >= a) & (t < e)).sum()) for t in r.trains)
                n_sur = sum(int(((np.asarray(t) >= a) & (np.asarray(t) < e)).sum()) for t in tr)
                count_change[name][0] += abs(n_sur - n_real)
                count_change[name][1] += n_real
    Xr, Xrig, Xsh, mice = np.vstack(Xr), np.vstack(Xrig), np.vstack(Xsh), np.asarray(mice)
    seed = seed31("real", stream, J_sec)
    return {"kind": "real", "stream": stream, "J_sec": J_sec, "n_pairs": int(len(mice)),
            "n_mice": int(np.unique(mice).size),
            "real_vs_rigid_shift": score(Xr, Xrig, mice, n_boot, seed),
            "real_vs_shared_offset": score(Xr, Xsh, mice, n_boot, seed + 1),
            "window_count_abs_change_share": {k: v[0] / max(1, v[1])
                                              for k, v in count_change.items()}}


def twin_task(args):
    stream, J_sec, n_boot, limit = args
    X = {"planted": ([], []), "unplanted": ([], [])}
    groups = []
    shape = None
    for t in range(N_TWINS):
        pl, un, shape = lc.twin_pair(stream, limit, 0.2, t)
        n_frames, dt = shape["n_frames"], shape["dt"]
        w = int(np.floor(lr.WINDOW_SEC / dt + 0.5))
        wins = [(i * w, (i + 1) * w) for i in range(n_frames // w)][1:-1]
        Jf = round(J_sec / dt, 9)
        for kind, tr in (("planted", pl), ("unplanted", un)):
            rig = sg.generate("rigid_shift", tr, (0, n_frames),
                              (TAG, "twin", stream, kind, t, Jf), J=Jf).trains
            X[kind][0].append(window_features(tr, (0, n_frames), wins))
            X[kind][1].append(window_features(rig, (0, n_frames), wins))
        groups += [f"twin{t}"] * len(wins)
    groups = np.asarray(groups)
    seed = seed31("twin", stream, J_sec)
    return {"kind": "twin", "stream": stream, "J_sec": J_sec, "n_pairs": int(len(groups)),
            "n_twins": N_TWINS, "twin_shape": shape, "participation": 0.2,
            "unplanted_vs_rigid_shift": score(np.vstack(X["unplanted"][0]),
                                              np.vstack(X["unplanted"][1]), groups, n_boot, seed,
                                              per_scale=False),
            "planted_vs_rigid_shift": score(np.vstack(X["planted"][0]),
                                            np.vstack(X["planted"][1]), groups, n_boot, seed + 1,
                                            per_scale=False)}


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", required=True)
    ap.add_argument("--limit", type=int, default=None)
    ap.add_argument("--quick", action="store_true")
    ap.add_argument("--jobs", type=int, default=12)
    ap.add_argument("--streams", nargs="*", default=["fast", "slow"])
    a = ap.parse_args(argv)
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    n_boot = 40 if a.quick else 1000
    tasks = []
    for stream in a.streams:
        for J in J_SEC[stream]:
            tasks.append((real_task, (stream, J, n_boot, a.limit)))
            tasks.append((twin_task, (stream, J, n_boot, a.limit)))
    meta = {"tag": TAG, "started": time.strftime("%Y-%m-%dT%H:%M:%S%z"), "limit": a.limit,
            "n_boot": n_boot, "J_sec": {s: J_SEC[s] for s in a.streams}, "centres_frames": CENTRES,
            "surround_ratio": SURROUND_RATIO, "widen_frames": WIDEN, "n_twins": N_TWINS,
            "features": feature_names(), "exploratory": True}
    (out / "meta.json").write_text(json.dumps(meta, indent=2))
    results = []
    t0 = time.time()
    with mp.get_context("spawn").Pool(a.jobs) as pool:
        futs = [pool.apply_async(fn, (args,)) for fn, args in tasks]
        for f in futs:
            r = f.get()
            results.append(r)
            (out / "results.json").write_text(json.dumps(results, indent=2, default=str))
            print(f"[{time.time() - t0:6.0f}s] {r['kind']} {r['stream']} {r['J_sec']}", flush=True)
    meta["seconds"] = time.time() - t0
    (out / "meta.json").write_text(json.dumps(meta, indent=2))
    print("done", out)


if __name__ == "__main__":
    main()
