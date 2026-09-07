#!/usr/bin/env python3
"""Does shifting a recording by a fraction of a second change a detector's calls?

Tony, 2026-09-07: "I suspect several of the detectors suffer this defect. Shifting
the data by a time step will change calls."

For each of the six detectors at its shipped operating point: run it on a real
baseline recording, then on the same recording with every onset moved by d for
d in 0.1 .. 0.9 s, shift the calls back by d, and compare to the unshifted calls.
A detector with no grid returns the same calls (to numerical noise); one that
bins returns different ones, and how different says how much of what it reports
is the grid rather than the data.

    python shift_invariance.py FOLDER [N_RECORDINGS] [TOL]
"""
import dataclasses
import sys
from pathlib import Path

import numpy as np

from bugarach import bench
from bugarach.dataset import preferred_stream
from bugarach.io import load_folder
from bugarach.score import _ONSET_FIELDS

folder = Path(sys.argv[1])
n_rec = int(sys.argv[2]) if len(sys.argv) > 2 else 3
TOL = float(sys.argv[3]) if len(sys.argv) > 3 else 0.05
SHIFTS = [round(0.1 * i, 1) for i in range(1, 10)]


def as_bench_slice(s, stream_name):
    """The bench addresses the stream as `events`; give it the real one under that name."""
    return dataclasses.replace(s, streams={bench.STREAM: s.streams[stream_name]})


def shifted(s, d):
    st = s.streams[bench.STREAM]
    kw = {}
    for f in ("locs", "t50rise", "peak"):
        v = getattr(st, f, None)
        if v is not None:
            kw[f] = [np.asarray(a, dtype=float) + d for a in v]
    return dataclasses.replace(s, streams={bench.STREAM: dataclasses.replace(st, **kw)})


def onsets_of(det):
    for f, _ in _ONSET_FIELDS:
        if hasattr(det, f):
            return np.sort(np.asarray(getattr(det, f), dtype=float).ravel())
    raise TypeError(type(det).__name__)


def preserved(ref, got):
    """Fraction of `ref` calls with a `got` call within TOL, and the surplus."""
    if ref.size == 0:
        return float("nan"), int(got.size)
    hit = 0
    for t in ref:
        if got.size and np.min(np.abs(got - t)) <= TOL:
            hit += 1
    return hit / ref.size, int(max(0, got.size - hit))


slices = load_folder(folder)
stream = preferred_stream([n for s in slices for n in s.streams] or ["fast"])
rows = {n: [] for n in bench.DETECTORS}
used = []
for s in slices[:n_rec]:
    base = as_bench_slice(s, stream)
    used.append(s.slice_id)
    for name in bench.DETECTORS:
        ref = onsets_of(bench.run_detector(name, base))
        per = []
        for d in SHIFTS:
            got = onsets_of(bench.run_detector(name, shifted(base, d))) - d
            per.append(preserved(ref, got))
        rows[name].append((s.slice_id, ref.size, per))

print(f"tolerance for 'the same call': {TOL} s; shifts: {SHIFTS}; recordings: {used}\n")
print(f"{'detector':8s} {'calls@0':>8s}  {'kept: min':>9s} {'mean':>6s}   {'extra: max':>10s} {'mean':>5s}   verdict")
for name in bench.DETECTORS:
    calls = sum(r[1] for r in rows[name])
    keeps = [k for r in rows[name] for k, _ in r[2] if np.isfinite(k)]
    extras = [e for r in rows[name] for _, e in r[2]]
    kmin, kmean = (min(keeps), float(np.mean(keeps))) if keeps else (float("nan"),) * 2
    verdict = ("shift-invariant" if kmin > 0.999 and max(extras) == 0
               else "grid-dependent" if kmin < 0.95 or max(extras) > 0.05 * max(calls, 1)
               else "nearly invariant")
    print(f"{name:8s} {calls:8d}  {kmin:9.3f} {kmean:6.3f}   {max(extras):10d} {np.mean(extras):5.1f}   {verdict}")
print("\nper recording, per shift — fraction of unshifted calls kept:")
for name in bench.DETECTORS:
    for sid, n, per in rows[name]:
        print(f"  {name:7s} {sid:14s} n={n:4d}  " + " ".join(f"{k:.2f}" for k, _ in per))
