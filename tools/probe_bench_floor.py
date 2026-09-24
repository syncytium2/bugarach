#!/usr/bin/env python3
"""ADR-0008's floor on the bench's own recordings, and what it leaves the bench to score.

    python tools/probe_bench_floor.py --out <folder> [--seeds 8] [--jobs 20]

**Why.** ADR-0008 decision 5: every bench recording gets its floor from its own null, so a detector
is tuned under the definition it is scored under. Computed that way on 2026-09-24, the fast bench
recording's floor came out at **17 co-active ROIs**, above every planted event (3, 6 and 10
participants), and it was the elevated-rate stretch that did it: 300 s in which every ROI's rate is
raised together is shared rate change, which ADR-0006 counts as chance and the rigid shift keeps.
Without that stretch the same recording's floor is 5. How the bench's floor should treat the
stretch is a decision the ADR does not make, and this probe measures the options for it:

* ``whole``: the recording as one window, the literal reading;
* ``without_stretch``: the same recording generated with no elevated-rate stretch
  (``hot_window=None``), which leaves the planted events, decoys and background unchanged;
* ``outside_stretch`` / ``inside_stretch``: the stretch as its own window and the rest as another
  (the part before the stretch and the part after it are joined end to end for the null, which
  adds one seam);
* the no-coordination recording's floor, which the empty-recording false-alarm budget runs on.

For each, the share of planted events whose participant count falls below the floor: under ADR-0008
those are not coordinated events, so a scorer that honours the floor stops counting them.

It measures and decides nothing. Floors use ``bugarach.event_floor.window_floor`` at ADR-0008's
settings (1,000 draws).
"""
from __future__ import annotations

import argparse
import json
import multiprocessing as mp
import os
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

BENCHES = ("bugarach.bench", "bugarach.bench_slow", "bugarach.bench_combined")
REGIMES = ("baseline_quiet", "baseline_busy")
STREAM_OF = {"bugarach.bench": "fast", "bugarach.bench_slow": "slow",
             "bugarach.bench_combined": "combined"}


def frames_of(s, stream_name, lo=None, hi=None):
    """Each ROI's onset frames on the recording's extent, and the extent's length in frames."""
    from bugarach.bench import recording_extent
    dt = s.require_dt()
    ext = recording_extent(s)
    a = ext[0] if lo is None else lo
    b = ext[1] if hi is None else hi
    L = int(round((b - a) / dt))
    out = []
    for v in s.streams[stream_name].t50rise:
        v = np.asarray(v, float)
        v = v[(v >= a) & (v < b)]
        out.append(np.unique(np.floor((v - a) / dt + 1e-9).astype(np.int64)))
    return out, L, dt


def job(args):
    import importlib

    from bugarach import event_floor as ef
    name, regime, seed = args
    b = importlib.import_module(name)
    key = ("bench-floor-probe", name, regime, seed)
    s, gt = b.make_recording(regime, seed)
    tr, L, dt = frames_of(s, b.STREAM)
    whole = ef.window_floor(tr, L, dt, key=(*key, "whole"))
    s2, _ = b.make_recording(regime, seed, hot_window=None, hot_rate_hz=0.0)
    tr2, L2, _ = frames_of(s2, b.STREAM)
    without = ef.window_floor(tr2, L2, dt, key=(*key, "without"))
    h0, h1 = gt.params["hot_window"]
    tin, Lin, _ = frames_of(s, b.STREAM, h0, h1)
    inside = ef.window_floor(tin, Lin, dt, key=(*key, "inside"))
    pre, Lpre, _ = frames_of(s, b.STREAM, None, h0)
    post, Lpost, _ = frames_of(s, b.STREAM, h1, None)
    joined = [np.concatenate([p, q + Lpre]) for p, q in zip(pre, post)]
    outside = ef.window_floor(joined, Lpre + Lpost, dt, key=(*key, "outside"))
    parts = np.array([e.n_part for e in gt.events])
    row = dict(bench=STREAM_OF[name], regime=regime, seed=seed, n_roi=len(tr),
               participants=sorted(set(parts.tolist())),
               floors={k: f.as_dict() for k, f in (("whole", whole),
                                                     ("without_stretch", without),
                                                     ("inside_stretch", inside),
                                                     ("outside_stretch", outside))})
    row["share_of_events_below_floor"] = {
        k: float(np.mean(parts < row["floors"][k]["floor"])) for k in row["floors"]}
    if regime == "baseline_quiet":
        n, _ = b.make_null_recording(seed)
        trn, Ln, _ = frames_of(n, b.STREAM)
        row["null_recording_floor"] = ef.window_floor(trn, Ln, dt,
                                                      key=(*key, "null")).as_dict()
    return row


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--seeds", type=int, default=8)
    ap.add_argument("--jobs", type=int, default=max(1, (os.cpu_count() or 2) - 2))
    a = ap.parse_args(argv)
    a.out.mkdir(parents=True, exist_ok=True)
    jobs = [(n, r, s) for n in BENCHES for r in REGIMES for s in range(1, a.seeds + 1)]
    with mp.Pool(a.jobs) as pool:
        rows = pool.map(job, jobs)
    summary = {}
    for bench in STREAM_OF.values():
        for regime in REGIMES:
            rs = [r for r in rows if r["bench"] == bench and r["regime"] == regime]
            summary[f"{bench}/{regime}"] = {
                k: dict(floor_range=[min(r["floors"][k]["floor"] for r in rs),
                                     max(r["floors"][k]["floor"] for r in rs)],
                        share_below_floor_mean=float(np.mean(
                            [r["share_of_events_below_floor"][k] for r in rs])))
                for k in rs[0]["floors"]}
            summary[f"{bench}/{regime}"]["participants"] = rs[0]["participants"]
            nulls = [r["null_recording_floor"]["floor"] for r in rs if "null_recording_floor" in r]
            if nulls:
                summary[f"{bench}/{regime}"]["null_recording_floor_range"] = [min(nulls),
                                                                              max(nulls)]
    (a.out / "bench_floor.json").write_text(json.dumps(dict(rows=rows, summary=summary),
                                                        indent=1))
    for k, v in summary.items():
        print(k, json.dumps(v))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
