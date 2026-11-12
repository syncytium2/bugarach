#!/usr/bin/env python3
"""The separation axis: how close can two planted events sit before each detector joins them?

    python tools/measure_separation_axis.py --out <folder>
    python tools/measure_separation_axis.py --out <folder> --seeds 1 --jobs 4     # smoke

ADR-0022 (Tony, 2026-11-11): close events are a bench axis of set separations, below 2 s
included, because a person separates events closer than that. This is that axis on all three
streams, for the four detectors of the first capability map (ADR-0021), each at its stream's
shipped operating point and each recording's own floor.

**It is `tools/measure_close_events.py` generalised, not a second method.** That tool is the
fast stream with the stack-ceiling variants. The planting is the same: on the stream's own bench
recording, half the gaps between neighbouring planted events are set to one chosen separation
(`simulate_coordination(gap_source=, gap_mix=)`) and the rest keep the realistic spacing, so
planted events come in close pairs and short chains at a known separation.

**What differs:** the streams and their values come from `bugarach.stream_profile` (ADR-0020),
and the recordings carry no decoys (ADR-0019). Nothing is measured from data: no recording is
read, and the separations are a sweep axis.

**Reported per stream, separation and detector:** recall of scored planted events, F1 by the
bench's scorer, and merged calls, the calls whose span holds two or more scored planted events
(`Score.n_merged_calls`, ADR-0010 part 3).
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

SEPARATIONS_SEC = (0.5, 1.0, 2.0, 3.0, 5.0, 10.0)
"""ADR-0022's starting levels, and 10 s as the reference where pairs are easy."""
CLOSE_SHARE = 0.5
"""The share of gaps set to the separation; the simulator's ``gap_mix`` is one minus this."""
DETECTORS = ("coact", "loco", "sce", "count_sliding")
"""The first capability map's four (ADR-0021)."""
NAME = {"coact": "CoactDetect", "loco": "LoCo", "sce": "binned SCE",
        "count_sliding": "count (sliding)"}
FRESH_SEED = 6000
"""First of the fresh bench seeds, which no search and no training run saw."""
FIELDS = ("n_planted", "n_detected", "n_hit", "hot_fa", "n_merged_calls")


def task(args):
    stream, sep, regime, seed = args
    from bugarach import real_intervals as ri
    from bugarach import stream_profile as sp
    from bugarach.score import score_stream

    p = sp.profile(stream)
    s, gt = p.simulate(regime, seed, gap_source=ri.as_gap_distribution([sep]),
                       gap_mix=1.0 - CLOSE_SHARE, n_distractors=0)
    times = np.sort([e.time for e in gt.events])
    out = dict(stream=stream, sep=sep, regime=regime, seed=seed, n_events=int(times.size),
               n_close_gaps=int((np.abs(np.diff(times) - sep) < 1e-6).sum()), det={})
    for name in DETECTORS:
        c = score_stream(gt, p.module.run_detector(name, s), tol_sec=p.module.TOL_SEC)
        out["det"][name] = [int(getattr(c, f)) for f in FIELDS]
    return out


def summarise(rows) -> dict:
    from bugarach import stream_profile as sp

    R = dict(separations_sec=list(SEPARATIONS_SEC), detectors=list(DETECTORS), by_stream={})
    for stream in sp.STREAMS:
        R["by_stream"][stream] = {}
        for sep in SEPARATIONS_SEC:
            mine = [r for r in rows if r["stream"] == stream and r["sep"] == sep]
            entry = dict(n_recordings=len(mine), n_events=sum(r["n_events"] for r in mine),
                         n_close_gaps=sum(r["n_close_gaps"] for r in mine), det={})
            for name in DETECTORS:
                f1s, recalls, merged = [], [], 0
                for regime in sorted({r["regime"] for r in mine}):
                    c = np.sum([r["det"][name] for r in mine if r["regime"] == regime], axis=0)
                    rec = c[2] / c[0] if c[0] else float("nan")
                    kept = c[1] - c[3]
                    prec = c[2] / kept if kept else float("nan")
                    f1s.append(2 * rec * prec / (rec + prec) if rec + prec > 0 else 0.0)
                    recalls.append(rec)
                    merged += int(c[4])
                entry["det"][name] = dict(
                    mean_f1=float(np.mean(f1s)), mean_recall=float(np.mean(recalls)),
                    merged_calls_per_recording=merged / max(len(mine), 1))
            R["by_stream"][stream][f"{sep:g}"] = entry
    return R


def table(R) -> str:
    lines = []
    for stream, by_sep in R["by_stream"].items():
        for key, title in (("mean_recall", "recall"), ("mean_f1", "F1"),
                           ("merged_calls_per_recording", "merged calls per recording")):
            lines.append(f"\n{stream} · {title}, by separation (s)")
            lines.append(f"  {'':<18}" + "".join(f"{g:>7g}" for g in SEPARATIONS_SEC))
            for name in DETECTORS:
                lines.append(f"  {NAME[name]:<18}" + "".join(
                    f"{by_sep[f'{g:g}']['det'][name][key]:>7.2f}" for g in SEPARATIONS_SEC))
    return "\n".join(lines)


INK = {"coact": "#1f77b4", "loco": "#d62728", "sce": "#7f7f7f", "count_sliding": "#1a7f37"}


def figure_name() -> str:
    """The figure's file name, from the estate's naming tool (never typed by hand)."""
    import subprocess
    from datetime import date

    r = subprocess.run(
        [sys.executable, str(ROOT / "tools" / "naming" / "artifact_name.py"), "build",
         "--type", "recovery", "--ext", "png", "--source", "synth", "--form", "plot",
         "--topic", "separation-axis-recall", "--date", date.today().strftime("%Y%m%d")],
        capture_output=True, text=True, check=True)
    return r.stdout.strip().splitlines()[-1]


def figure(R, out: Path) -> Path:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    rows = (("mean_recall", "recall of planted events", (0, 1.02)),
            ("merged_calls_per_recording",
             "merged calls per recording\n(one call spanning 2 or more planted events)", None))
    streams = list(R["by_stream"])
    fig, axes = plt.subplots(len(rows), len(streams), figsize=(11.5, 6.4), sharex=True)
    top = max(R["by_stream"][s][f"{g:g}"]["det"][d]["merged_calls_per_recording"]
              for s in streams for g in SEPARATIONS_SEC for d in DETECTORS)
    for i, (key, label, ylim) in enumerate(rows):
        for j, stream in enumerate(streams):
            ax = axes[i][j]
            for name in DETECTORS:
                ax.plot(SEPARATIONS_SEC,
                        [R["by_stream"][stream][f"{g:g}"]["det"][name][key]
                         for g in SEPARATIONS_SEC],
                        color=INK[name], lw=1.5, marker="o", ms=3.5, label=NAME[name])
            ax.set_xscale("log")
            ax.set_xticks(SEPARATIONS_SEC, [f"{g:g}" for g in SEPARATIONS_SEC], fontsize=8)
            ax.minorticks_off()
            ax.set_ylim(*(ylim or (0, top * 1.08)))
            ax.set_ylabel(f"{stream} · {label}", fontsize=8)
            ax.tick_params(axis="y", labelsize=8)
            for side in ("top", "right"):
                ax.spines[side].set_visible(False)
            if i == len(rows) - 1:
                ax.set_xlabel("separation of the close planted events (s)", fontsize=8)
    handles, labels = axes[0][0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="lower center", ncol=4, fontsize=8, frameon=False)
    fig.tight_layout(rect=(0, 0.05, 1, 1))
    path = out / figure_name()
    fig.savefig(path, dpi=170)
    plt.close(fig)
    return path


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--out", type=Path, required=True, help="folder for the summary JSON")
    ap.add_argument("--seeds", type=int, default=12,
                    help="recordings per stream, separation and background")
    ap.add_argument("--jobs", type=int, default=max(1, (os.cpu_count() or 2) - 2))
    ap.add_argument("--figure", type=Path, default=None,
                    help="also draw the figure into this folder (the claimed darkroom folder)")
    ap.add_argument("--from-summary", action="store_true",
                    help="draw from the summary already in --out; simulate nothing")
    a = ap.parse_args(argv)
    a.out.mkdir(parents=True, exist_ok=True)
    if a.from_summary:
        R = json.loads((a.out / "separation_axis_summary.json").read_text(encoding="utf-8"))
        if a.figure is None:
            raise SystemExit("--from-summary draws a figure; pass --figure <folder>")
        a.figure.mkdir(parents=True, exist_ok=True)
        print(figure(R, a.figure))
        return

    from bugarach import bench
    from bugarach import stream_profile as sp

    bench.use_spacing("realistic")
    tasks = [(stream, sep, regime, sd) for stream, p in sp.profiles().items()
             for sep in SEPARATIONS_SEC for regime in p.regimes
             for sd in range(FRESH_SEED, FRESH_SEED + a.seeds)]
    t0 = time.time()
    with mp.get_context("spawn").Pool(a.jobs) as pool:
        rows = pool.map(task, tasks, chunksize=2)
    R = summarise(rows)
    R["_"] = dict(what="the separation axis of ADR-0022 on the three stream benches",
                  close_share=CLOSE_SHARE, seeds=a.seeds, first_seed=FRESH_SEED,
                  n_recordings=len(rows), decoys_per_recording=0, spacing="realistic",
                  settings="each stream's shipped operating point, each recording's own floor",
                  profiles={s: p.summary() for s, p in sp.profiles().items()},
                  seconds=round(time.time() - t0, 1))
    path = a.out / "separation_axis_summary.json"
    path.write_text(json.dumps(R, indent=1, default=float), encoding="utf-8")
    print(path)
    if a.figure is not None:
        a.figure.mkdir(parents=True, exist_ok=True)
        print(figure(R, a.figure))
    print(table(R))
    print(f"\n{len(rows)} recordings in {R['_']['seconds']} s")


if __name__ == "__main__":
    main()
