#!/usr/bin/env python3
"""The stack ceiling's call rule on the three benches, beside the detectors on record.

    python tools/measure_stack_ceiling.py --also docs/learned/runs/2026-10-08-stack-ceiling
    python tools/measure_stack_ceiling.py --out <folder> --seeds 2      # smoke

Tony, 2026-10-08: *"lets try it on the bench."* The rule is ``stack_ceiling``'s: a moment is
called when its tower would cost at least a threshold of shift per ROI to rebuild elsewhere in
its period, and at least the recording's floor of ROIs stand.

**What is fixed and where it comes from.** The window and the merge gap are count (sliding)'s
shipped operating point on each stream; the ROI minimum is the recording's ADR-0008 floor, as
the bench hands it to count (sliding); the period is 120 s, LoCo's context. None is searched.

**The threshold is the one setting, and it is picked on half the seeds and reported on the
other half.** Every threshold in :data:`THRESHOLDS_SEC` is run on every recording. On the
even seeds, the pick is the threshold with the highest F1 (mean of the two backgrounds) among
those inside count (sliding)'s two limits: calls per hour on the no-coordination recordings and
calls per minute in the raised-rate stretch. Every number reported for the rule, and for the
reference detectors beside it, is from the odd seeds.

**Reference detectors**, each at its shipped operating point and the same floor, through
``tools/measure_stack.py``'s runner: CoactDetect, LoCo, count (sliding) and ``stack_global``
(stack's first form). The learned ``chorus_norm`` is left out: it needs checkpoints from the
darkroom, and this run should work without them.

Seeds are the fresh ones (6000 onward) that no search and no training run saw. Simulated
recordings only; nothing here opens an export folder.
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

FOLDER = "2026-10-08-stack-ceiling"
PERIOD_SEC = 120.0
THRESHOLDS_SEC = (2.0, 3.0, 4.0, 5.0, 6.0, 8.0, 10.0, 12.0, 15.0, 20.0, 25.0)
REFERENCES = ("coact", "loco", "count_sliding", "stack")
NAME = {"coact": "CoactDetect", "loco": "LoCo", "count_sliding": "count (sliding)",
        "stack": "stack (global)", "ceiling": "stack ceiling"}
INK = {"coact": "#3b6fb6", "loco": "#7a4fa3", "count_sliding": "#555555", "stack": "#c8501e",
       "ceiling": "#111111"}
STREAMS = ms.STREAMS


def task(args):
    stream, kind, regime, seed = args
    from bugarach import bench
    from bugarach.detectors import stack_ceiling as sc
    from bugarach.detectors.rate import recording_extent, stream_trains
    from bugarach.score import score_stream

    mod = ms.bench_module(stream)
    if kind == "planted":
        s, gt = mod.make_recording(regime, seed)
    elif kind == "elevated":
        s, gt = mod.make_elevated_rate_recording(regime, seed)
    else:
        s, gt = mod.make_null_recording(seed + bench.NULL_SEED_OFFSET)
    out = dict(stream=stream, kind=kind, regime=regime, seed=seed,
               hours=gt.params["duration_sec"] / 3600.0, det={})

    def record(name, det):
        sc_ = score_stream(gt, det, tol_sec=mod.TOL_SEC)
        d = dict(score=sc_, n_calls=int(sc_.n_detected))
        if kind == "elevated":
            h0, h1 = gt.params["hot_window"]
            d.update(calls_in=int(sc_.hot_fa), minutes_in=(h1 - h0) / 60.0)
        out["det"][name] = d

    for name in REFERENCES:
        record(name, ms.run(stream, name, s))

    op = mod.OPERATING_POINTS["count_sliding"].params
    floor = bench.floored_params("count_sliding", s, op, {}, mod.STREAM, None)["min_rois"]
    ext = recording_extent(s)
    trains = stream_trains(s.streams[mod.STREAM], ext)
    t0 = time.time()
    r = sc.stack_ceiling(trains, sc.frame_centres(ext, s.require_dt()),
                         width_sec=float(op["win_sec"]), period_sec=PERIOD_SEC)
    cost = sc.rebuild_cost(r)
    out.update(floor=int(floor), seconds=time.time() - t0)
    for th in THRESHOLDS_SEC:
        record(f"ceiling@{th:g}", sc.detection_from(
            r, cost, threshold_sec=th, min_rois=floor, merge_gap_sec=float(op["merge_gap_sec"])))
    return out


def measures(rows, stream: str, name: str) -> dict:
    """One detector on one stream, pooled over the rows given."""
    from bugarach import bench

    mod = ms.bench_module(stream)
    mine = [r for r in rows if r["stream"] == stream]
    out = {}
    for regime in mod.REGIMES:
        planted = [r for r in mine if r["kind"] == "planted" and r["regime"] == regime]
        p = bench.pool_scores([r["det"][name]["score"] for r in planted], detector=name,
                              regime=regime, seeds=[r["seed"] for r in planted])
        el = [r for r in mine if r["kind"] == "elevated" and r["regime"] == regime]
        out[regime] = dict(
            f1=p.f1, recall=p.recall, precision=p.precision, n_scored=p.n_scored, n_hit=p.n_hit,
            n_false_alarm=p.n_fa, n_calls=p.n_detected, n_recordings=len(planted),
            calls_on_decoys=p.decoy_calls, f1_without_decoys=p.f1_without_decoys,
            recall_by_participation={f"{k:g}": [n, h] for k, (n, h) in sorted(p.by_frac.items())},
            stretch_calls_per_min=sum(r["det"][name]["calls_in"] for r in el)
            / max(sum(r["det"][name]["minutes_in"] for r in el), 1e-9))
    nulls = [r for r in mine if r["kind"] == "null"]
    hours = sum(r["hours"] for r in nulls)
    out["mean_f1"] = float(np.mean([out[g]["f1"] for g in mod.REGIMES]))
    out["worst_stretch_calls_per_min"] = max(out[g]["stretch_calls_per_min"] for g in mod.REGIMES)
    out["no_coordination_calls_per_hour"] = sum(r["det"][name]["n_calls"] for r in nulls) / hours
    out["no_coordination_hours"] = hours
    return out


def summarise(rows) -> dict:
    from bugarach import bench

    pick_rows = [r for r in rows if r["seed"] % 2 == 0]
    report_rows = [r for r in rows if r["seed"] % 2 == 1]
    R = {}
    for stream in STREAMS:
        mod = ms.bench_module(stream)
        limit_hour = float(mod.MAX_FALSE_POSITIVES_PER_HOUR["count_sliding"])
        limit_min = float(mod.MAX_PROBE_PER_MIN["count_sliding"])
        on_pick = {th: measures(pick_rows, stream, f"ceiling@{th:g}") for th in THRESHOLDS_SEC}
        inside = [th for th, m in on_pick.items()
                  if m["no_coordination_calls_per_hour"] <= limit_hour
                  and m["worst_stretch_calls_per_min"] <= limit_min]
        picked = max(inside, key=lambda th: on_pick[th]["mean_f1"]) if inside else None
        mine = [r for r in rows if r["stream"] == stream]
        R[stream] = dict(
            regimes=list(mod.REGIMES), limit_calls_per_hour=limit_hour,
            limit_stretch_calls_per_min=limit_min, picked_threshold_sec=picked,
            thresholds_inside_limits_sec=inside,
            window_sec=float(mod.OPERATING_POINTS["count_sliding"].params["win_sec"]),
            merge_gap_sec=float(mod.OPERATING_POINTS["count_sliding"].params["merge_gap_sec"]),
            floors=sorted({r["floor"] for r in mine}),
            median_seconds_per_recording=float(np.median([r["seconds"] for r in mine])),
            pick_half={f"{th:g}": on_pick[th] for th in THRESHOLDS_SEC},
            report_half=dict(
                ceiling={f"{th:g}": measures(report_rows, stream, f"ceiling@{th:g}")
                         for th in THRESHOLDS_SEC},
                references={n: measures(report_rows, stream, n) for n in REFERENCES}),
            n_recordings=dict(
                pick=len([r for r in pick_rows if r["stream"] == stream]),
                report=len([r for r in report_rows if r["stream"] == stream])))
    R["_"] = dict(period_sec=PERIOD_SEC, thresholds_sec=list(THRESHOLDS_SEC),
                  spacing=bench.spacing_name() if hasattr(bench, "spacing_name") else None)
    return R


def figure(R, out: Path) -> Path:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    rows = (("mean_f1", "F1, mean of the\ntwo backgrounds", None),
            ("no_coordination_calls_per_hour", "calls per hour,\nnothing planted",
             "limit_calls_per_hour"),
            ("worst_stretch_calls_per_min", "calls per minute in the\nraised-rate stretch",
             "limit_stretch_calls_per_min"))
    fig, axes = plt.subplots(3, 3, figsize=(11.5, 7.6), sharex=True)
    for j, stream in enumerate(STREAMS):
        S = R[stream]
        rep = S["report_half"]
        for i, (key, label, limit) in enumerate(rows):
            ax = axes[i, j]
            ax.plot(THRESHOLDS_SEC, [rep["ceiling"][f"{th:g}"][key] for th in THRESHOLDS_SEC],
                    color=INK["ceiling"], marker="o", ms=3.5, lw=1.4, label=NAME["ceiling"])
            for n in REFERENCES:
                ax.axhline(rep["references"][n][key], color=INK[n], lw=1.1, label=NAME[n])
            if limit:
                ax.axhline(S[limit], color="#c62828", lw=0.9, ls=":",
                           label="count (sliding)'s limit")
            if S["picked_threshold_sec"] is not None:
                ax.axvline(S["picked_threshold_sec"], color="#999999", lw=0.9, ls="--",
                           label="threshold picked on the other half")
            if i == 0:
                ax.set_ylim(0, 1)
            else:
                ax.set_yscale("symlog", linthresh=0.5)
                ax.set_ylim(bottom=0)
            ax.set_ylabel(f"{stream} · {label}" if j == 0 else stream, fontsize=8)
            ax.tick_params(labelsize=8)
            for side in ("top", "right"):
                ax.spines[side].set_visible(False)
            if i == 2 and j == 1:
                ax.set_xlabel("threshold: shift per ROI to rebuild the tower elsewhere (s)",
                              fontsize=8)
    handles, labels = axes[1, 0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="lower center", ncol=4, fontsize=8, frameon=False)
    fig.tight_layout(rect=(0, 0.06, 1, 1))
    path = out / "explainer_stack-ceiling-bench_20261008.png"   # tools/naming/artifact_name.py build
    fig.savefig(path, dpi=170)
    plt.close(fig)
    return path


def table(R) -> str:
    lines = []
    for stream in STREAMS:
        S = R[stream]
        th = S["picked_threshold_sec"]
        rep = S["report_half"]
        lines.append(f"\n{stream}: threshold picked on the even seeds = "
                     + (f"{th:g} s" if th is not None else "none inside the limits"))
        lines.append(f"  {'detector':<18} " + "  ".join(f"F1 {g[9:]:<6}" for g in S["regimes"])
                     + "  F1 without decoys (quiet, busy)"
                     + "  calls/h nothing planted  calls/min in stretch")
        entries = [(NAME[n], rep["references"][n]) for n in REFERENCES]
        if th is not None:
            entries.append((f"stack ceiling {th:g}s", rep["ceiling"][f"{th:g}"]))
        for label, m in entries:
            lines.append(f"  {label:<18} " + "  ".join(f"{m[g]['f1']:<9.3f}" for g in S["regimes"])
                         + "  " + ", ".join(f"{m[g]['f1_without_decoys']:.3f}"
                                         for g in S["regimes"]).ljust(31)
                         + f"  {m['no_coordination_calls_per_hour']:<23.2f}  "
                         f"{m['worst_stretch_calls_per_min']:.2f}")
    return "\n".join(lines)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--out", type=Path, default=None,
                    help=f"output folder (default: <darkroom>/{FOLDER})")
    ap.add_argument("--also", type=Path, default=None, help="a second folder for the outputs")
    ap.add_argument("--seeds", type=int, default=24,
                    help="bench recordings per background; half as many no-coordination and "
                         "raised-rate recordings. Half of each picks the threshold")
    ap.add_argument("--jobs", type=int, default=max(1, (os.cpu_count() or 2) - 2))
    ap.add_argument("--redraw", action="store_true",
                    help="redraw the figure from the folder's bench_summary.json; measures nothing")
    a = ap.parse_args(argv)
    out = a.out
    if out is None:
        from bugarach.paths import darkroom
        out = darkroom(FOLDER, create=True)
        if out is None:
            raise SystemExit("no darkroom found; pass --out")
    out.mkdir(parents=True, exist_ok=True)
    if a.redraw:
        R = json.loads((out / "bench_summary.json").read_text())
        made = [figure(R, out)]
        if a.also:
            shutil.copy2(made[0], a.also / made[0].name)
        print(*made, sep="\n")
        print(table(R))
        return

    from bugarach import bench
    bench.use_spacing("realistic")
    tasks = []
    for s in STREAMS:
        f = bench.seed_factor(s)
        seeds = range(ms.FRESH_SEED, ms.FRESH_SEED + a.seeds * f)
        fewer = range(ms.FRESH_SEED, ms.FRESH_SEED + max(2, a.seeds // 2) * f)
        regimes = ms.bench_module(s).REGIMES
        tasks += [(s, "planted", g, sd) for g in regimes for sd in seeds]
        tasks += [(s, "elevated", g, sd) for g in regimes for sd in fewer]
        tasks += [(s, "null", "baseline_quiet", sd) for sd in fewer]
    t0 = time.time()
    with mp.get_context("spawn").Pool(a.jobs) as pool:
        rows = pool.map(task, tasks, chunksize=2)
    R = summarise(rows)
    R["_"].update(seeds=a.seeds, n_recordings=len(rows), seconds=round(time.time() - t0, 1),
                  jobs=a.jobs)
    made = [out / "bench_summary.json"]
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
