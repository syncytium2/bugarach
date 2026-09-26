#!/usr/bin/env python3
"""Does ``call_measure``'s core count track the planted participants on the realistic bench?

    python tools/check_call_measure.py --out <folder> [--also docs/learned/runs/<name>]
        [--spacing realistic] [--seeds 24] [--workers 16]

**Why.** ADR-0010 ruling 3: the review tool is to show ``call_measure``'s core count
(``core_n_roi``) on each stream where it tracks the planted participants on the realistic bench,
and its own ±1 s window elsewhere; adoption is decided per stream in the morning. This measures the
tracking.

**How.** On each stream's bench under ``--spacing`` (default ``realistic``), for seeds 1 to
``--seeds`` on both backgrounds (doubled on fast, as ``bench.seed_factor`` doubles every realistic
count there), every planted event is measured with ``call_measure.measure_call``:
- centred on the event's time;
- at that stream's defaults (``call_measure.DEFAULTS``: gap and half-aperture);
- with the recording's frame interval as the minimum interval.

Its ``core_n_roi`` is compared with the event's true participant count (``n_part``), split by the
gap from the event to its nearest planted neighbour: under 10 s, 10 to 30 s, over 30 s. Decoys are
not planted events and are not measured.

**What it writes.** ``call_measure_check.csv`` (one row per planted event), ``summary.json`` (per
stream and gap bin: events, the median and mean error, the mean absolute error, and the shares
exact, within one cell, over and under), and Figure 1, ``figure1_call_measure_vs_planted.png``.
Descriptive; it adopts nothing.
"""
from __future__ import annotations

import argparse
import csv
import importlib
import json
import multiprocessing as mp
import os
import shutil
import sys
from pathlib import Path

import numpy as np

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))

BENCHES = {"fast": "bugarach.bench", "slow": "bugarach.bench_slow",
           "combined": "bugarach.bench_combined"}
REG = ("baseline_quiet", "baseline_busy")
BINS = (("under 10 s", 0.0, 10.0), ("10 to 30 s", 10.0, 30.0), ("over 30 s", 30.0, np.inf))


def gap_bin(gap: float) -> str:
    for name, lo, hi in BINS:
        if lo <= gap < hi:
            return name
    return BINS[-1][0]


def job(args):
    stream, regime, seed = args
    from bugarach.call_measure import defaults_for, measure_call

    b = importlib.import_module(BENCHES[stream])
    s, gt = b.make_recording(regime, seed)
    st = s.streams[b.STREAM]
    dt = s.require_dt()
    gap_sec, half = defaults_for(stream)
    times = np.array([e.time for e in gt.events], float)
    rows = []
    for i, e in enumerate(gt.events):
        others = np.delete(times, i)
        nearest = float(np.min(np.abs(others - e.time))) if others.size else float("inf")
        m = measure_call(st, float(e.time), gap_sec=gap_sec, half_aperture_sec=half,
                         min_interval_sec=dt)
        rows.append(dict(stream=stream, regime=regime, seed=seed, time_sec=float(e.time),
                         n_part=int(e.n_part), core_n_roi=int(m.core_n_roi),
                         error=int(m.core_n_roi) - int(e.n_part), nearest_gap_sec=nearest,
                         gap_bin=gap_bin(nearest), floor=gt.params.get("event_floor")))
    return rows


def summarise(rows) -> dict:
    out = {}
    for stream in BENCHES:
        for name, _, _ in (*BINS, ("all", 0, 0)):
            rs = [r for r in rows if r["stream"] == stream and (name == "all" or r["gap_bin"] == name)]
            if not rs:
                continue
            err = np.array([r["error"] for r in rs], float)
            out.setdefault(stream, {})[name] = dict(
                events=len(rs), median_error_rois=float(np.median(err)),
                mean_error_rois=float(err.mean()), mean_abs_error_rois=float(np.abs(err).mean()),
                share_exact=float(np.mean(err == 0)), share_within_1=float(np.mean(np.abs(err) <= 1)),
                share_over=float(np.mean(err > 0)), share_under=float(np.mean(err < 0)))
    return out


def figure(rows, out_png: Path) -> Path:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    plt.rcParams.update({"font.size": 12})
    fig, axes = plt.subplots(1, 3, figsize=(15, 5.2), sharey=True)
    for ax, stream, letter in zip(axes, BENCHES, "abc"):
        data, labels = [], []
        for name, _, _ in BINS:
            e = [r["error"] for r in rows if r["stream"] == stream and r["gap_bin"] == name]
            data.append(e)
            labels.append(f"{name}\n({len(e)} events)")
        ax.boxplot([d if d else [np.nan] for d in data], showfliers=True, whis=(5, 95))
        ax.set_xticks(range(1, len(labels) + 1))
        ax.set_xticklabels(labels)
        ax.axhline(0, color="0.4", lw=1)
        ax.set_xlabel(f"{stream} stream: gap to the nearest planted event")
        ax.grid(axis="y", color="0.92")
        ax.text(0.0, 1.02, letter, transform=ax.transAxes, fontsize=15, fontweight="bold")
    axes[0].set_ylabel("core_n_roi minus planted participants (cells)")
    fig.tight_layout()
    fig.savefig(out_png, dpi=150)
    plt.close(fig)
    return out_png


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--also", type=Path, default=None)
    ap.add_argument("--spacing", choices=("bench", "realistic", "orx"), default="realistic")
    ap.add_argument("--seeds", type=int, default=24)
    ap.add_argument("--workers", type=int, default=16)
    a = ap.parse_args(argv)
    a.out.mkdir(parents=True, exist_ok=True)
    from bugarach import bench as _b
    _b.use_spacing(a.spacing)                 # before the pool: every worker reads it
    jobs = [(s, r, k) for s in BENCHES for r in REG
            for k in range(1, a.seeds * _b.seed_factor(s) + 1)]
    with mp.Pool(a.workers) as pool:
        rows = [r for part in pool.map(job, jobs) for r in part]
    with (a.out / "call_measure_check.csv").open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    summ = summarise(rows)
    (a.out / "summary.json").write_text(json.dumps(dict(
        spacing=a.spacing, seeds_per_background={s: a.seeds * _b.seed_factor(s) for s in BENCHES},
        bins=[b[0] for b in BINS], centred_on="the planted event's time",
        defaults="call_measure.DEFAULTS per stream", summary=summ), indent=1) + "\n")
    png = figure(rows, a.out / "figure1_call_measure_vs_planted.png")
    for stream, v in summ.items():
        for name, d in v.items():
            print(f"{stream:8s} {name:11s} {d['events']:5d} events  median error "
                  f"{d['median_error_rois']:+.0f}  mean |error| {d['mean_abs_error_rois']:.2f}  "
                  f"exact {d['share_exact']:.0%}  within 1 {d['share_within_1']:.0%}  "
                  f"over {d['share_over']:.0%}  under {d['share_under']:.0%}")
    if a.also:
        a.also.mkdir(parents=True, exist_ok=True)
        for f in ("summary.json", png.name):
            shutil.copy2(a.out / f, a.also / f)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
