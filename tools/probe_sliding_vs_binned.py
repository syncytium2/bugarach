#!/usr/bin/env python3
"""LoCo and CoactDetect, binned vs sliding: does the call list survive a shift, and what does it cost.

    python tools/probe_sliding_vs_binned.py                  # shift check + timing
    python tools/probe_sliding_vs_binned.py --only timing

**Shift check** — ``tools/probe_shift_invariance.py``'s measurement, run in both window
modes: each detector on real baseline recordings, then on the same recordings with every
event moved by d = 0.1 … 0.9 s; the shift is undone on the calls, and "kept" is the fraction
of the unshifted calls with a shifted call within ``--tol`` seconds. A detector with no grid
keeps them all. Binned calls sit on bin edges, so at the default 0.05 s match they can only
fail; the September probe used 1 s for that reason (LoCo 64%, CoactDetect 70% kept).

**Timing** — each mode at the shipped settings, best of three, on two bench recordings and
the same real ones. Read the ratio, not the seconds: a busy machine slows both.

Measured 2026-09-16 on three TTX baselines: sliding keeps 100% at every shift for both
detectors, and runs in 0.25–0.75× the binned time.
"""
from __future__ import annotations

import argparse
import dataclasses
import time

import numpy as np

from bugarach import bench, dataset
from bugarach.detectors.coact import coact_detect
from bugarach.detectors.loco import loco_detect
from bugarach.detectors.rate import recording_extent, stream_trains
from bugarach.io import load_folder

SHIFTS = [round(0.1 * i, 1) for i in range(1, 10)]
MODES = ("binned", "sliding")


def _as_bench(s, stream):
    return dataclasses.replace(s, streams={bench.STREAM: s.streams[stream]})


def _shifted(s, d):
    st = s.streams[bench.STREAM]
    kw = {f: [np.asarray(a, float) + d for a in getattr(st, f)]
          for f in ("locs", "t50rise", "peak") if getattr(st, f, None) is not None}
    return dataclasses.replace(s, streams={bench.STREAM: dataclasses.replace(st, **kw)})


def _kept(ref, got, tol):
    if ref.size == 0:
        return float("nan"), got.size
    hit = sum(1 for t in ref if got.size and np.min(np.abs(got - t)) <= tol)
    return hit / ref.size, max(0, got.size - hit)


def shift_check(recordings, tol):
    for name in ("loco", "coact"):
        for mode in MODES:
            ks, extras, calls, lines = [], [], 0, []
            for s in recordings:
                base = _as_bench(s, "fast")
                ref = np.sort(bench.run_detector(name, base, window_mode=mode).onset_sec)
                calls += ref.size
                per = []
                for d in SHIFTS:
                    got = np.sort(bench.run_detector(name, _shifted(base, d),
                                                     window_mode=mode).onset_sec) - d
                    k, e = _kept(ref, got, tol)
                    per.append(k)
                    ks.append(k)
                    extras.append(e)
                lines.append(f"    {s.slice_id:14s} calls {ref.size:3d}  kept per shift "
                             + " ".join(f"{k:.2f}" for k in per))
            print(f"{name:6s} {mode:8s} calls {calls:4d}  kept: worst {np.nanmin(ks):.3f} "
                  f"mean {np.nanmean(ks):.3f}  extra calls, worst shift {max(extras)}", flush=True)
            print("\n".join(lines), flush=True)


def _best_of(fn, reps=3):
    best, out = np.inf, None
    for _ in range(reps):
        t0 = time.perf_counter()
        out = fn()
        best = min(best, time.perf_counter() - t0)
    return best, out


def timing(recordings):
    cp = {k: v for k, v in bench.OPERATING_POINTS["coact"].params.items() if k != "window_mode"}
    lp = {k: v for k, v in bench.OPERATING_POINTS["loco"].params.items() if k != "window_mode"}
    cases = [(f"bench {r}", bench.make_recording(r, 1)[0], bench.STREAM)
             for r in ("baseline_quiet", "baseline_busy")]
    cases += [(f"real {s.slice_id}", s, "fast") for s in recordings]
    for label, s, stream in cases:
        ext = recording_extent(s)
        trains = stream_trains(s.streams[stream], ext)
        out = []
        for mode in MODES:
            tc, c = _best_of(lambda: coact_detect(trains, ext, window_mode=mode, **cp))
            tl, lo = _best_of(lambda: loco_detect(s, window_mode=mode, **lp))
            out.append((tc, c.n_events, tl, lo.streams[stream].n_events))
        (bc, bcn, bl, bln), (sc, scn, sl_, sln) = out
        print(f"{label:24s} CoactDetect {bc:5.2f} s ({bcn:3d} calls) -> {sc:5.2f} s ({scn:3d}), "
              f"x{sc / bc:.2f}  |  LoCo, all streams {bl:5.2f} s -> {sl_:5.2f} s, x{sl_ / bl:.2f}",
              flush=True)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--role", default=bench.MEASURED_ROLE,
                    help="which current_export.toml role to read (default: the one the bench "
                         "is measured on). The 2026-09-17 program reads only this folder")
    ap.add_argument("--n", type=int, default=3, help="recordings to use")
    ap.add_argument("--tol", type=float, default=0.05, help="seconds within which a call is kept")
    ap.add_argument("--only", choices=("shift", "timing"), default=None)
    a = ap.parse_args(argv)
    # Was a folder NAME, and the name was the TTX subset: `..._STEPS_EXCLUDED_TTX`. Tony,
    # 2026-09-17: *"you should only work from the steps excluded folder"* — the subsets are
    # views of it and are not inputs. The parent holds the same recordings.
    recordings = load_folder(dataset.current(a.role))[:a.n]
    if a.only in (None, "shift"):
        shift_check(recordings, a.tol)
    if a.only in (None, "timing"):
        timing(recordings)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
