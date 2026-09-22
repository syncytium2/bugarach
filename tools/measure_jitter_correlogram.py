#!/usr/bin/env python3
"""Onset jitter without bins: the width of the cross-ROI correlogram's peak, calibrated on the simulator.

    python tools/measure_jitter_correlogram.py --jobs 12 --out docs/learned/runs/<dated-name>

**Why.** Both benches' ``jitter_sec`` came from a bin-bound instrument. ``assess_coactivity``'s
within-cluster onset spread tracks bin/√12 from 0.5 s to 5 s on both streams
(``tools/measure_slow_bench.py``, ``BINS``), and the MATLAB summary the fast bench's 0.36 s came
from (``bench.MEASURED_PROVENANCE``) is the same measure. Tony, 2026-09-22: *"we don't have our
own measure of jitter?"* — this is one.

**The statistic.** Onset pairs between distinct ROIs at each lag of one frame (0.1 s) out to
10 s, divided by the count expected if every pair fired independently at its observed totals —
``tools/measure_slow_comodulation.py``'s definition (Perkel, Gerstein & Moore 1967), not re-derived:
its ``raster`` and ``_autocorr_rows`` are imported, and zero lag is counted once per pair as there.
Numerator and denominator are pooled over recordings before dividing. If participants' onsets
scatter with SD σ around a shared time, the pairwise lag scatters with SD σ√2, so the excess
forms a peak at short lags whose width grows with σ.

**The width.** The mean excess at 5–10 s lag — the broad shoulder of slow shared modulation —
is subtracted, and the **half-width at half height** of what is left (:func:`hwhm`) is the
primary width. The RMS lag over 0–3 s (:func:`width`) is also recorded, and on real data it is
the wrong statistic: it weights the tail by lag squared, so noise there moves it.

**Why calibrate instead of dividing by √2.** Frames quantise onsets, distractors and the
elevated-rate stretch add their own pairs, participation sets the peak's height against the
background — so width is not exactly σ√2. The same measure is run on simulated recordings of
each bench (``bench`` for fast, ``bench_slow`` for slow; both backgrounds; seeds 1–24) at a
grid of planted ``jitter_sec``, and a real width is read off that curve. **The calibration is
the test**: a width that does not grow with planted jitter would refuse the method, and the
record says whether it grew.

**What it reads.** The default dataset (``dataset.default()``), each recording's baseline
analysis window (``assess_folder.generation_window``, 15-minute floor), ``t50rise`` onsets.
Baseline only (FOUNDATIONS §9).
"""
from __future__ import annotations

import argparse
import json
import sys
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np

REPO = Path(__file__).resolve().parents[1]
for _p in (REPO / "src", REPO / "tools"):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

DT = 0.1
MAX_LAG = 100            # frames: 10 s
PEAK = (0, 30)           # frames: 0-3 s
SHOULDER = (50, 100)     # frames: 5-10 s
JITTERS = (0.05, 0.1, 0.15, 0.2, 0.3, 0.36, 0.46, 0.6, 0.8, 1.0)
SIM_SEEDS = tuple(range(1, 25))
BENCHES = {"fast": "bugarach.bench", "slow": "bugarach.bench_slow"}


def pairs(trains, L: int, max_lag: int = MAX_LAG):
    """(observed, expected) cross-ROI onset pairs at each frame lag 0..max_lag, zero lag once."""
    import measure_slow_comodulation as msc

    max_lag = min(max_lag, L - 1)
    X = msc.raster(trains, L)
    n = X.sum(axis=1)
    obs = msc._autocorr_rows(X.sum(axis=0, keepdims=True), max_lag) - msc._autocorr_rows(X, max_lag)
    k = np.arange(max_lag + 1)
    exp = (n.sum() ** 2 - (n ** 2).sum()) * (L - k) / L ** 2
    obs[0] /= 2.0
    exp[0] /= 2.0
    out_o, out_e = np.zeros(MAX_LAG + 1), np.zeros(MAX_LAG + 1)
    out_o[:max_lag + 1], out_e[:max_lag + 1] = obs, exp
    return out_o, out_e


def excess(obs, exp):
    with np.errstate(invalid="ignore", divide="ignore"):
        return obs / exp - 1.0


def width(obs, exp) -> float:
    """RMS lag (s) of the shoulder-subtracted peak over 0-3 s."""
    x = excess(obs, exp)
    peak = x[PEAK[0]:PEAK[1] + 1] - np.nanmean(x[SHOULDER[0]:SHOULDER[1] + 1])
    w = np.clip(np.nan_to_num(peak), 0, None)
    w[0] *= 0.5
    k = np.arange(len(w)) * DT
    return float(np.sqrt((w * k ** 2).sum() / w.sum())) if w.sum() > 0 else float("nan")


def hwhm(obs, exp) -> float:
    """Half-width at half height (s) of the shoulder-subtracted peak, linearly interpolated.

    The primary width. The RMS lag (:func:`width`) is kept for the record, but it weights the
    0-3 s tail by lag squared, so noise there moves it: on the first run a real fast bump near 3 s
    read as jitter 0.48 s while the peak's own shape sat between 0.1 and 0.36 (Figure 1)."""
    x = excess(obs, exp)
    p = x[PEAK[0]:PEAK[1] + 1] - np.nanmean(x[SHOULDER[0]:SHOULDER[1] + 1])
    if not np.isfinite(p[0]) or p[0] <= 0:
        return float("nan")
    q = p / p[0]
    below = np.nonzero(q < 0.5)[0]
    if below.size == 0:
        return float("nan")
    i = int(below[0])
    return float(DT * (i - 1 + (q[i - 1] - 0.5) / (q[i - 1] - q[i])))


def _real(args):
    folder, i, stream = args
    from bugarach.assess_folder import NoBaselineRegion, generation_window
    from bugarach.io import load_folder

    s = load_folder(Path(folder))[i]
    if stream not in s.streams:
        return None
    try:
        w, _ = generation_window(s)
    except NoBaselineRegion:
        return None
    if w is None or w[1] - w[0] < 900.0:
        return None
    dt = s.require_dt()
    assert abs(dt - DT) < 1e-9, f"{s.slice_id}: frame interval {dt}, this tool assumes {DT}"
    lo, hi = w
    L = int(round((hi - lo) / DT))
    st = s.streams[stream]
    trains = []
    for v in st.t50rise or st.locs:
        v = np.asarray(v, float)
        v = v[np.isfinite(v) & (v >= lo) & (v < hi)]
        trains.append(np.round((v - lo) / DT).astype(int))
    return pairs(trains, L)


def _sim(args):
    bench_name, regime, seed, jitter = args
    import importlib

    b = importlib.import_module(bench_name)
    s, gt = b.make_recording(regime, seed, jitter_sec=jitter)
    L = int(round(gt.params["duration_sec"] / DT))
    trains = [np.round(np.asarray(t, float) / DT).astype(int) for t in s.streams[b.STREAM].t50rise]
    return pairs(trains, L)


def pooled(results):
    o = sum(r[0] for r in results)
    e = sum(r[1] for r in results)
    return o, e


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--jobs", type=int, default=12)
    ap.add_argument("--boot", type=int, default=200)
    ap.add_argument("--out", type=Path, required=True)
    a = ap.parse_args(argv)
    a.out.mkdir(parents=True, exist_ok=True)

    from bugarach import dataset
    from bugarach.io import load_folder

    folder = dataset.default()
    n = len(load_folder(folder))
    rec = {"dataset": dataset.stamp(), "dt": DT, "peak_sec": [PEAK[0] * DT, PEAK[1] * DT],
           "shoulder_sec": [SHOULDER[0] * DT, SHOULDER[1] * DT], "jitters": list(JITTERS),
           "sim_seeds": [SIM_SEEDS[0], SIM_SEEDS[-1]], "streams": {}}
    with ProcessPoolExecutor(a.jobs) as ex:
        for stream, bench_name in BENCHES.items():
            real = [r for r in ex.map(_real, [(str(folder), i, stream) for i in range(n)]) if r]
            o, e = pooled(real)
            rng = np.random.RandomState(20260922)
            draws = [pooled([real[j] for j in rng.randint(0, len(real), len(real))])
                     for _ in range(a.boot)]

            sims, curves = {}, {}
            for j in JITTERS:
                jobs = [(bench_name, r, s, j) for r in ("baseline_quiet", "baseline_busy")
                        for s in SIM_SEEDS]
                sims[j] = pooled(list(ex.map(_sim, jobs)))
                curves[j] = excess(*sims[j]).tolist()

            out = dict(recordings=len(real), real_excess=excess(o, e).tolist(),
                       sim_excess={str(j): c for j, c in curves.items()},
                       bench_jitter_sec=__import__(bench_name, fromlist=["x"]).BENCH_RECORDING["jitter_sec"])
            print(f"{stream}: {len(real)} recordings (bench jitter now {out['bench_jitter_sec']} s)",
                  flush=True)
            for stat in (hwhm, width):
                ws = np.array([stat(*sims[j]) for j in JITTERS])
                monotone = bool(np.all(np.diff(ws) > 0))

                def to_jitter(w, ws=ws, monotone=monotone):
                    return (float(np.interp(w, ws, JITTERS, left=np.nan, right=np.nan))
                            if monotone else float("nan"))

                w_real = stat(o, e)
                wb = np.array([stat(*d) for d in draws])
                jb = np.array([to_jitter(w) for w in wb])
                row = dict(real_sec=w_real, real_interval=np.nanpercentile(wb, [2.5, 97.5]).tolist(),
                           calibration_sec={str(j): float(w) for j, w in zip(JITTERS, ws)},
                           calibration_monotone=monotone, jitter_sec=to_jitter(w_real),
                           jitter_interval=(np.nanpercentile(jb, [2.5, 97.5]).tolist()
                                            if np.isfinite(jb).any() else None),
                           boot_outside_calibration=int(np.isnan(jb).sum()))
                out[stat.__name__] = row
                ji = row["jitter_interval"]
                print(f"  {stat.__name__:5s} real {w_real:.3f} s "
                      f"[{row['real_interval'][0]:.3f}, {row['real_interval'][1]:.3f}]; calibration "
                      + ", ".join(f"{j:g}->{w:.3f}" for j, w in zip(JITTERS, ws))
                      + ("" if monotone else " NOT MONOTONE")
                      + f"; jitter {row['jitter_sec']:.3f} s "
                      + (f"[{ji[0]:.3f}, {ji[1]:.3f}]" if ji else "[none]")
                      + f" ({row['boot_outside_calibration']} of {a.boot} draws off the curve)",
                      flush=True)
            out["primary"] = "hwhm"
            rec["streams"][stream] = out
    (a.out / "jitter_correlogram.json").write_text(json.dumps(rec, indent=1) + "\n", encoding="utf-8")
    print(f"wrote {a.out / 'jitter_correlogram.json'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
