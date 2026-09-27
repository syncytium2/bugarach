#!/usr/bin/env python3
"""The ADR-0008 floor counted in a co-activity window of W = 0.5, 1 and 2 s, per stream.

    python tools/measure_floor_at_window.py --source bench --out <folder> [--jobs 40]
    python tools/measure_floor_at_window.py --source real  --out <folder> [--jobs 40]

**Why** (orchestrator's brief, 2026-09-27). Tony leans toward count (sliding) as the one primary
detector. Its threshold is the ADR-0008 floor, and that floor is always counted in a 2 s window
(``event_floor.WINDOW_SEC``), while the rule counts over its own window W. This measures what
matching them would change. **It changes nothing that ships**: ``WINDOW_SEC`` and ADR-0008 stay
as they are unless Tony rules otherwise.

**The method is event_floor's own**, called rather than copied: per-ROI rigid shift within
±20 s, 1,000 draws, at most 1 null call per hour, never below 3 ROIs
(:func:`bugarach.event_floor.window_floor`). Only ``window_sec`` changes.

- ``--source real``: the default dataset (``dataset.default()``, which refuses until the person
  has confirmed it this session), baseline windows only (FOUNDATIONS §9), all three streams. Each
  window's null is seeded exactly as ``tools/detect_with_floors.py`` seeds it, so the 2 s column
  reproduces the floors that tool already uses.
- ``--source bench``: the realistic bench's recordings, the ones a search selects on (both
  backgrounds, selection seeds, fast's doubled by ADR-0010 ruling 2), through
  ``bench.recording_floor``, the function that makes the bench's floors.

Writes ``floors_<source>.csv``, ``summary_<source>.json`` and ``fig1_floor_vs_window_<source>.png``.
"""
from __future__ import annotations

import argparse
import csv
import importlib
import json
import os
import sys
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np

REPO = Path(__file__).resolve().parents[1]
for p in (REPO / "src", REPO / "tools"):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

WINDOWS = (0.5, 1.0, 2.0)
STREAMS = ("fast", "slow", "combined")
BENCHES = {"fast": "bugarach.bench", "slow": "bugarach.bench_slow",
           "combined": "bugarach.bench_combined"}
REGIMES = ("baseline_quiet", "baseline_busy")
N_SELECTION = 48
"""The search's selection seeds per background before ADR-0010's doubling on fast."""


def _bench_task(args):
    stream, regime, seed = args
    from bugarach import bench as fast
    fast.use_spacing("realistic")
    b = importlib.import_module(BENCHES[stream])
    s, _ = b.make_recording(regime, seed)
    rows = []
    for w in WINDOWS:
        f = fast.recording_floor(s, b.STREAM, window_sec=w)
        rows.append(dict(source="bench", stream=stream, unit=f"{regime}:{seed}", window_sec=w,
                         floor=f.floor, chance_floor=f.chance_floor, stable=f.stable,
                         n_roi=f.n_roi))
    return rows


def _real_task(args):
    folder, i = args
    from bugarach import event_floor as ef
    from bugarach.combined import COMBINED, has_sources, stream_of
    from bugarach.detect_folder import _region_index, folder_analysis_windows
    from bugarach.detectors.rate import stream_trains
    from bugarach.io import load_folder
    from detect_with_floors import TAG, frames_in, is_baseline

    s = load_folder(Path(folder))[i]
    s, windows = folder_analysis_windows(s)
    if has_sources(s) and COMBINED not in s.streams:
        s.streams[COMBINED] = stream_of(s, COMBINED)
    dt = s.require_dt()
    rows = []
    for w in windows:
        lo, hi = float(w.win_start), float(w.win_end)
        label = (w.label or "").strip() or None
        if hi <= lo or not is_baseline(label):
            continue
        idx = _region_index(w)
        n_frames = int(round((hi - lo) / dt))
        for sname in STREAMS:
            if sname not in s.streams:
                continue
            tr = stream_trains(s.streams[sname], (lo, hi))
            for win in WINDOWS:
                try:
                    f = ef.window_floor(frames_in(tr, lo, dt), n_frames, dt,
                                        key=(TAG, s.slice_id, sname, idx), window_sec=win)
                except ValueError:
                    continue
                rows.append(dict(source="real", stream=sname, unit=f"{s.slice_id}:{idx}",
                                 window_sec=win, floor=f.floor, chance_floor=f.chance_floor,
                                 stable=f.stable, n_roi=f.n_roi))
    return rows


def summarise(rows):
    """Per stream and W: min, median, max of the floor; against the 2 s floor of the same unit,
    how many units move and by how much."""
    by = {}
    for r in rows:
        by.setdefault(r["stream"], {}).setdefault(r["unit"], {})[r["window_sec"]] = r["floor"]
    out = {}
    for stream, units in by.items():
        out[stream] = {}
        for w in WINDOWS:
            vals = [u[w] for u in units.values() if w in u]
            if not vals:
                continue
            d = [u[w] - u[2.0] for u in units.values() if w in u and 2.0 in u]
            moves = {str(k): int(v) for k, v in zip(*np.unique(d, return_counts=True))}
            out[stream][f"{w:g}"] = dict(
                n=len(vals), min=int(min(vals)), median=float(np.median(vals)),
                max=int(max(vals)), moved=int(sum(x != 0 for x in d)),
                change_vs_2s=moves, at_minimum_3=int(sum(v <= 3 for v in vals)))
    return out


def figure(rows, path, source):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, axes = plt.subplots(1, 3, figsize=(12, 3.6), sharey=False)
    colors = {0.5: "#0e7c86", 1.0: "#17becf", 2.0: "#444444"}
    for ax, stream in zip(axes, STREAMS):
        sub = [r for r in rows if r["stream"] == stream]
        if not sub:
            ax.set_visible(False)
            continue
        hi = max(r["floor"] for r in sub)
        bins = np.arange(2.5, hi + 1.5)
        unit = "recordings" if source == "bench" else "baseline windows"
        for w in WINDOWS:
            v = [r["floor"] for r in sub if r["window_sec"] == w]
            ax.hist(v, bins=bins, histtype="step", lw=1.8, color=colors[w],
                    label=f"W = {w:g} s ({len(v)} {unit})")
        n_units = len({r['unit'] for r in sub})
        ax.set_xlabel(f"{stream} · floor (ROIs) · {n_units} {unit}")
        ax.set_ylabel(unit)
        ax.legend(fontsize=8, frameon=False)
    fig.suptitle(f"Figure 1. The ADR-0008 floor counted in a W-second window, "
                 f"{'realistic bench' if source == 'bench' else '66 real recordings, baseline'}",
                 fontsize=10, x=0.01, ha="left")
    fig.tight_layout()
    fig.savefig(path, dpi=150)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--source", choices=("bench", "real"), required=True)
    ap.add_argument("--out", type=Path, default=None,
                    help="default: <darkroom>/2026-09-27-floor-at-window/")
    ap.add_argument("--jobs", type=int, default=max(1, (os.cpu_count() or 2) - 4))
    a = ap.parse_args(argv)
    if a.out is None:
        from bugarach.paths import darkroom
        a.out = darkroom() / "2026-09-27-floor-at-window"
    a.out.mkdir(parents=True, exist_ok=True)

    if a.source == "real":
        from bugarach import dataset
        folder = dataset.default()                 # refuses until the person has confirmed it
        from bugarach.io import load_folder
        n = len(load_folder(Path(folder)))
        tasks = [(str(folder), i) for i in range(n)]
        fn, stamp = _real_task, dataset.stamp()
    else:
        from bugarach import bench
        tasks = [(st, reg, seed) for st in STREAMS for reg in REGIMES
                 for seed in range(1, N_SELECTION * bench.seed_factor(st, "realistic") + 1)]
        fn, stamp = _bench_task, "realistic bench, selection seeds"
    with ProcessPoolExecutor(max_workers=a.jobs) as ex:
        rows = [r for part in ex.map(fn, tasks, chunksize=1) for r in part]

    with open(a.out / f"floors_{a.source}.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    summ = summarise(rows)
    (a.out / f"summary_{a.source}.json").write_text(
        json.dumps(dict(source=a.source, data=stamp, windows_sec=list(WINDOWS),
                        method="event_floor.window_floor: rigid shift ±20 s, 1000 draws, "
                               "<= 1 call/h, minimum 3", by_stream=summ), indent=1),
        encoding="utf-8")
    figure(rows, a.out / f"fig1_floor_vs_window_{a.source}.png", a.source)
    print(json.dumps(summ, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
