#!/usr/bin/env python3
"""How close can two planted events sit before each detector stops telling them apart?

    python tools/measure_close_events.py --also docs/learned/runs/2026-10-08-stack-ceiling
    python tools/measure_close_events.py --out <folder> --seeds 2      # smoke

Tony, 2026-10-08, after every tuned detector landed within a few hundredths of F1 on the fast
bench: *"i suspect we need the revised bench with short intervals."* The realistic bench draws
its planted gaps from gaps measured in real baselines, and that measurement found events as
peaks of a count in a 2 s window, so no gap under 2 s exists in it (the shortest fast gap is
2.1 s). A bench with shorter intervals needs the gaps measured again in a narrower window, on
real recordings, and the default folder is stopped (#858).

**This is the part that needs no real recording: a controlled test, not a bench.** On the fast
bench's own recording, half the gaps between neighbouring planted events are set to one chosen
value, from 0.3 s to 10 s, and the rest keep the old spacing. So planted events come in close
pairs and short chains at a known separation. Nothing here is measured from data, and the gap
values are a sweep axis, in the way ``bench.CROWDED_RECORDING`` is a diagnostic.

**What is reported, per gap and detector:** F1 by the bench's scorer and each recording's
floor; recall; and merged calls, the calls whose span holds two or more scored planted events
(``Score.n_merged_calls``, ADR-0010 part 3).

**Detectors.** The four references at their shipped fast points, and four settings of the
sliding count in a 0.5 s window, each named by what it is: with a 1.5 s merge gap (the best
cost-off setting of ``tools/search_stack_ceiling.py``) and with a 0.2 s one, each with the
stack ceiling's rebuild cost off and on (threshold 10 s, period 480 s, the searched setting).

Fast stream only: it is where the question was raised, and the searched settings are per stream.
"""

from __future__ import annotations

import argparse
import json
import multiprocessing as mp
import os
import shutil
import sys
import time
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import measure_stack as ms  # noqa: E402
import measure_stack_ceiling as mc  # noqa: E402

STREAM = "fast"
GAPS_SEC = (0.3, 0.5, 1.0, 1.5, 2.0, 3.0, 5.0, 10.0)
CLOSE_SHARE = 0.5
"""The share of gaps set to the chosen value; the simulator's ``gap_mix`` is one minus this."""
WINDOW_SEC, PERIOD_SEC, THRESHOLD_SEC = 0.5, 480.0, 10.0
CEILING = {                       # name: (merge gap, threshold)
    "count_0.5_gap1.5": (1.5, 0.0),
    "count_0.5_gap0.2": (0.2, 0.0),
    "ceiling_gap1.5": (1.5, THRESHOLD_SEC),
    "ceiling_gap0.2": (0.2, THRESHOLD_SEC),
}
NAME = dict(mc.NAME, **{
    "count_sliding": "count (sliding), shipped: 2 s window, 3 s merge gap",
    "count_0.5_gap1.5": "count, 0.5 s window, 1.5 s merge gap",
    "count_0.5_gap0.2": "count, 0.5 s window, 0.2 s merge gap",
    "ceiling_gap1.5": "stack ceiling, 0.5 s window, 1.5 s merge gap",
    "ceiling_gap0.2": "stack ceiling, 0.5 s window, 0.2 s merge gap"})
INK = dict(mc.INK, **{"count_0.5_gap1.5": "#1a7f37", "count_0.5_gap0.2": "#1a7f37",
                      "ceiling_gap1.5": "#111111", "ceiling_gap0.2": "#111111"})
DASHED = ("count_0.5_gap0.2", "ceiling_gap0.2")
ORDER = list(mc.REFERENCES) + list(CEILING)
FIELDS = ("n_planted", "n_detected", "n_hit", "hot_fa", "n_merged_calls")


def task(args):
    gap, regime, seed = args
    from bugarach import bench, real_intervals as ri
    from bugarach.detectors import stack_ceiling as sc
    from bugarach.detectors.rate import recording_extent, stream_trains
    from bugarach.score import score_stream

    mod = ms.bench_module(STREAM)
    s, gt = mod.make_recording(regime, seed, gap_source=ri.as_gap_distribution([gap]),
                               gap_mix=1.0 - CLOSE_SHARE)
    times = np.sort([e.time for e in gt.events])
    out = dict(gap=gap, regime=regime, seed=seed, n_events=int(times.size),
               n_close_gaps=int((np.abs(np.diff(times) - gap) < 1e-6).sum()), det={})

    def record(name, det):
        c = score_stream(gt, det, tol_sec=mod.TOL_SEC)
        out["det"][name] = [int(c.n_planted), int(c.n_detected), int(c.n_hit), int(c.hot_fa),
                            int(c.n_merged_calls)]

    for name in mc.REFERENCES:
        record(name, ms.run(STREAM, name, s))
    op = mod.OPERATING_POINTS["count_sliding"].params
    floor = bench.floored_params("count_sliding", s, op, {}, mod.STREAM, None)["min_rois"]
    ext = recording_extent(s)
    r = sc.stack_ceiling(stream_trains(s.streams[mod.STREAM], ext),
                         sc.frame_centres(ext, s.require_dt()), width_sec=WINDOW_SEC,
                         period_sec=PERIOD_SEC)
    cost = sc.rebuild_cost(r)
    for name, (merge_gap, threshold) in CEILING.items():
        record(name, sc.detection_from(r, cost, threshold_sec=threshold, min_rois=floor,
                                       merge_gap_sec=merge_gap))
    out["floor"] = int(floor)
    return out


def summarise(rows) -> dict:
    R = dict(gaps_sec=list(GAPS_SEC), detectors=ORDER, by_gap={})
    for gap in GAPS_SEC:
        mine = [r for r in rows if r["gap"] == gap]
        entry = dict(n_recordings=len(mine), n_events=sum(r["n_events"] for r in mine),
                     n_close_gaps=sum(r["n_close_gaps"] for r in mine), det={})
        for name in ORDER:
            f1s, recalls, merged, hit, planted = [], [], 0, 0, 0
            for regime in sorted({r["regime"] for r in mine}):
                c = np.sum([r["det"][name] for r in mine if r["regime"] == regime], axis=0)
                rec = c[2] / c[0] if c[0] else np.nan
                kept = c[1] - c[3]
                prec = c[2] / kept if kept else np.nan
                f1s.append(2 * rec * prec / (rec + prec) if rec + prec > 0 else 0.0)
                recalls.append(rec)
                merged += int(c[4])
                hit += int(c[2])
                planted += int(c[0])
            entry["det"][name] = dict(
                mean_f1=float(np.mean(f1s)), mean_recall=float(np.mean(recalls)),
                merged_calls=merged, merged_calls_per_recording=merged / max(len(mine), 1),
                n_hit=hit, n_planted_scored=planted)
        R["by_gap"][f"{gap:g}"] = entry
    return R


def figure(R, out: Path) -> Path:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    panels = (("mean_f1", "F1, mean of the two backgrounds", (0, 1)),
              ("mean_recall", "recall of scored planted events", (0, 1)),
              ("merged_calls_per_recording",
               "merged calls per recording\n(a call spanning 2 or more planted events)", None))
    fig, axes = plt.subplots(1, 3, figsize=(12.5, 4.6))
    for ax, (key, label, ylim) in zip(axes, panels):
        for name in ORDER:
            ax.plot(GAPS_SEC, [R["by_gap"][f"{g:g}"]["det"][name][key] for g in GAPS_SEC],
                    color=INK[name], lw=1.4, marker="o", ms=3,
                    ls="--" if name in DASHED else "-", label=NAME[name])
        ax.set_xscale("log")
        ax.set_xticks(GAPS_SEC, [f"{g:g}" for g in GAPS_SEC], fontsize=8)
        ax.minorticks_off()
        ax.set_xlabel("gap between the close planted events (s)", fontsize=8)
        ax.set_ylabel(f"fast · {label}", fontsize=8)
        if ylim:
            ax.set_ylim(*ylim)
        else:
            ax.set_ylim(bottom=0)
        ax.tick_params(axis="y", labelsize=8)
        for side in ("top", "right"):
            ax.spines[side].set_visible(False)
    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="lower center", ncol=3, fontsize=7.5, frameon=False)
    fig.tight_layout(rect=(0, 0.14, 1, 1))
    path = out / "explainer_close-events_20261008.png"       # tools/naming/artifact_name.py
    fig.savefig(path, dpi=170)
    plt.close(fig)
    return path


def table(R) -> str:
    lines = []
    for key, title in (("mean_f1", "F1, mean of the two backgrounds"),
                       ("mean_recall", "recall"),
                       ("merged_calls_per_recording", "merged calls per recording")):
        lines.append(f"\n{title}, by gap (s)")
        lines.append(f"  {'':<50}" + "".join(f"{g:>7g}" for g in GAPS_SEC))
        for name in ORDER:
            lines.append(f"  {NAME[name]:<50}" + "".join(
                f"{R['by_gap'][f'{g:g}']['det'][name][key]:>7.2f}" for g in GAPS_SEC))
    return "\n".join(lines)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--out", type=Path, default=None,
                    help=f"output folder (default: <darkroom>/{mc.FOLDER})")
    ap.add_argument("--also", type=Path, default=None, help="a second folder for the outputs")
    ap.add_argument("--seeds", type=int, default=24, help="recordings per gap and background")
    ap.add_argument("--jobs", type=int, default=max(1, (os.cpu_count() or 2) - 2))
    a = ap.parse_args(argv)
    out = a.out
    if out is None:
        from bugarach.paths import darkroom
        out = darkroom(mc.FOLDER, create=True)
        if out is None:
            raise SystemExit("no darkroom found; pass --out")
    out.mkdir(parents=True, exist_ok=True)

    from bugarach import bench
    bench.use_spacing("realistic")
    regimes = ms.bench_module(STREAM).REGIMES
    tasks = [(g, regime, sd) for g in GAPS_SEC for regime in regimes
             for sd in range(ms.FRESH_SEED, ms.FRESH_SEED + a.seeds)]
    t0 = time.time()
    with mp.get_context("spawn").Pool(a.jobs) as pool:
        rows = pool.map(task, tasks, chunksize=2)
    R = summarise(rows)
    R["_"] = dict(stream=STREAM, close_share=CLOSE_SHARE, window_sec=WINDOW_SEC,
                  period_sec=PERIOD_SEC, threshold_sec=THRESHOLD_SEC, seeds=a.seeds,
                  n_recordings=len(rows), seconds=round(time.time() - t0, 1),
                  floors=sorted({r["floor"] for r in rows}))
    made = [out / "close_events_summary.json"]
    made[0].write_text(json.dumps(R, indent=1, default=float))
    made.append(figure(R, out))
    if a.also:
        a.also.mkdir(parents=True, exist_ok=True)
        for p in made:
            shutil.copy2(p, a.also / p.name)
    print(*made, sep="\n")
    print(table(R))
    print(f"\n{len(rows)} recordings in {R['_']['seconds']} s")


if __name__ == "__main__":
    main()
