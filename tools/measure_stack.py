#!/usr/bin/env python3
"""stack against count (sliding): the three benches, and recordings whose rates swell together.

    python tools/measure_stack.py                       # into the darkroom
    python tools/measure_stack.py --out <folder> --seeds 2 --swells 2   # smoke

**What is compared.** ``count_sliding`` at each bench's own operating point, and ``stack``
(:func:`bugarach.detectors.count.stack_detect`) with the same reference window, merge gap and
ADR-0008 floor, looking as well at windows 1/8, 1/4 and 1/2 as wide. ``stack`` at the reference
width alone *is* ``count_sliding`` (``tests/test_stack.py``), so every difference below is what
the narrower windows add. ``stack`` sets its own tail probability so that it calls no more often
than ``count_sliding`` on rigid shifts of the same recording.

**Two parts.**

* **The benches** (fast, slow, combined; both backgrounds): planted events scored by the bench's
  own scorer and pooled by ``bench.pool_scores``, the no-coordination recording, and the
  elevated-rate recording.
* **Swells** — the synthetic worlds of ``tools/measure_slow_comodulation.py``, which hold no
  planted event: a flat background, and every ROI's rate multiplied by one shared multiplier
  wandering on a 20 s, 1-minute or 5-minute timescale. Every call there is a call on shared rate
  change. The hypothesis: at the same rigid-shift false-alarm rate, ``stack`` makes fewer.

⚠ **The bench half is partly circular for stability.** The bench's planted jitter was copied
from the measured jitter (``8137da71``), so a detector that rewards onsets as tight as the bench
plants them is rewarded by construction. The swell half does not have that problem.

Simulated recordings only. Nothing here opens an export folder.
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
sys.path.insert(0, str(Path(__file__).resolve().parent))

FOLDER = "2026-10-07-stack"
TAG = "stack-2026-10-07"
FRESH_SEED = 6000
"""First of the fresh bench seeds (``tools/score_bench_candidates.py``'s ``SEEDS``)."""
FRACTIONS = (0.125, 0.25, 0.5, 1.0)
"""Window widths as fractions of the reference window: 0.25, 0.5, 1 and 2 s at a 2 s reference."""
STREAMS = ("fast", "slow", "combined")
WORLDS = ("sim_background", "shared_20s", "shallow_1min", "drift_5min")
WORLD_LABEL = {"sim_background": "flat background", "shared_20s": "shared swell, 20 s",
               "shallow_1min": "shared swell, 1 min (shallow)",
               "drift_5min": "shared swell, 5 min"}
PAIR = ("count_sliding", "stack")
"""The ablation: ``stack`` at one width is ``count_sliding``."""
BEST = ("coact", "loco", "chorus_norm")
"""The detectors the record puts at or near the top on every stream, for comparison: CoactDetect
(the reference every table is paired against), LoCo, and the learned ``chorus_norm`` at its
picked training seed. From ``<darkroom>/2026-09-28-detector-table/README.md`` and
``docs/learned/runs/2026-09-24-cross-stream-3x3/``."""
DETECTORS = BEST + PAIR
CHORUS_PICK = {"fast": 3, "slow": 4, "combined": 1}
"""``chorus_norm``'s picked training seed per stream (``2026-09-26-full-panel/064/README.md``,
section B: best held-out F1 within CoactDetect's no-coordination budget)."""
PICKS = {"chorus_norm": CHORUS_PICK,
         "chorus_norm_part": {"fast": 3, "slow": 2, "combined": 0}}
"""Picked training seed per learned model and stream, from the same section B.
``chorus_norm_part`` is the chorus variant with the best fresh-seed F1 that also has a valid
pick on all three streams (0.650, 0.818 and 0.822 in the 2026-09-28 detector table;
``chorus_gain_norm_part`` is 0.007 higher on combined and has no pick on slow)."""
BEST_CHORUS = "chorus_norm_part"
_MODELS: dict = {}


def chorus_path(stream: str, arch: str = "chorus_norm") -> Path:
    """The picked checkpoint of ``arch`` for ``stream``. It lives in the darkroom, where the
    full-panel night left it; nothing here trains one."""
    from bugarach.paths import darkroom

    root = darkroom("2026-09-26-full-panel", "064", f"models-{stream}")
    p = None if root is None else root / f"{arch}_{stream}_seed{PICKS[arch][stream]}.json"
    if p is None or not p.exists():
        raise SystemExit(f"{arch}'s picked checkpoint for {stream} is not in the darkroom "
                         f"({p}); the comparison needs it")
    return p


def chorus(stream: str, arch: str = "chorus_norm"):
    if (stream, arch) not in _MODELS:
        from bugarach.learn.checkpoint import load
        _MODELS[stream, arch] = load(chorus_path(stream, arch))
    return _MODELS[stream, arch]


def bench_module(stream: str):
    from bugarach import bench, bench_combined, bench_slow
    return {"fast": bench, "slow": bench_slow, "combined": bench_combined}[stream]


def stack_params(op: dict) -> dict:
    """``stack``'s settings from a ``count_sliding`` operating point."""
    if op.get("split_dip") is not None:
        raise SystemExit("count_sliding runs with split_dip here; stack has no such setting, "
                         "so the two would not be the same rule at one width")
    w = float(op["win_sec"])
    return dict(widths_sec=tuple(w * f for f in FRACTIONS), ref_win_sec=w,
                k_offset=int(op.get("k_offset", 0)), merge_gap_sec=float(op["merge_gap_sec"]))


def run(stream: str, name: str, s):
    """One detector on a bench slice. The coded ones run at the bench's shipped operating point
    and the recording's own floor; ``chorus_norm`` runs as saved; ``stack`` takes
    ``count_sliding``'s point and is tuned on nothing."""
    from bugarach import bench
    from bugarach.detectors.count import stack_detect
    from bugarach.detectors.rate import recording_extent, stream_trains

    mod = bench_module(stream)
    if name == "chorus_norm":
        return chorus(stream).predict(s)[0]
    if name != "stack":
        return mod.run_detector(name, s)
    op = mod.OPERATING_POINTS["count_sliding"].params
    floored = bench.floored_params("count_sliding", s, op, {}, mod.STREAM, None)
    ext = recording_extent(s)
    return stack_detect(stream_trains(s.streams[mod.STREAM], ext), ext,
                        min_rois=floored["min_rois"], frame_interval_sec=s.require_dt(),
                        **stack_params(op))


def _stability(det, sc) -> dict:
    """Each ``stack`` call's winning width, split by what the scorer made of the call."""
    onset = np.asarray(det.onset_sec, float)
    hit = np.isin(onset, sc.matched[np.isfinite(sc.matched)])
    fa = np.isin(onset, sc.fa_times)
    return dict(hit=det.stability_sec[hit].tolist(), false_alarm=det.stability_sec[fa].tolist())


def bench_task(args):
    stream, kind, regime, seed = args
    from bugarach import bench
    from bugarach.score import score_stream

    mod = bench_module(stream)
    if kind == "planted":
        s, gt = mod.make_recording(regime, seed)
    elif kind == "elevated":
        s, gt = mod.make_elevated_rate_recording(regime, seed)
    else:
        s, gt = mod.make_null_recording(seed + bench.NULL_SEED_OFFSET)
    out = dict(stream=stream, kind=kind, regime=regime, seed=seed,
               floor=gt.params.get("event_floor"), dt=float(s.require_dt()),
               hours=gt.params["duration_sec"] / 3600.0, det={})
    for name in DETECTORS:
        det = run(stream, name, s)
        sc = score_stream(gt, det, tol_sec=mod.TOL_SEC)
        d = dict(score=sc, n_calls=int(sc.n_detected))
        if kind == "elevated":
            h0, h1 = gt.params["hot_window"]
            d.update(calls_in=int(sc.hot_fa), minutes_in=(h1 - h0) / 60.0)
        if name == "stack":
            d.update(alpha=det.alpha, thresholds={f"{w:g}": k for w, k in det.thresholds.items()},
                     null=det.null, stability=_stability(det, sc))
        out["det"][name] = d
    return out


def swell_task(args):
    world, i = args
    import measure_slow_comodulation as msc

    from bugarach import bench, event_floor as ef
    from bugarach.detectors import sliding as sl
    from bugarach.detectors.count import count_sliding_detect, stack_detect

    frames, L, dt = msc.synthetic_recording(world, i)
    floor = ef.window_floor(frames, L, dt, key=(TAG, world, i))
    trains = [np.asarray(t, float) * dt for t in frames]
    ext = (0.0, L * dt)
    op = bench.OPERATING_POINTS["count_sliding"].params
    a = count_sliding_detect(trains, ext, min_rois=floor.floor, **op)
    b = stack_detect(trains, ext, min_rois=floor.floor, frame_interval_sec=dt,
                     **stack_params(op))
    out = dict(world=world, i=i, hours=L * dt / 3600.0, floor=floor.floor, dt=dt,
               n_roi=len(frames), calls={"count_sliding": int(a.n_events),
                                         "stack": int(b.n_events)},
               alpha=b.alpha, thresholds={f"{w:g}": k for w, k in b.thresholds.items()},
               null=b.null, stability=b.stability_sec.tolist())
    if i == 0:
        starts, ends, S = sl.pieces(trains, float(op["win_sec"]), *ext)
        out["example"] = dict(
            t=np.c_[starts, ends].ravel().tolist(), count=np.c_[S, S].ravel().tolist(),
            onsets={"count_sliding": a.onset_sec.tolist(), "stack": b.onset_sec.tolist()},
            stability=b.stability_sec.tolist(), duration_sec=L * dt,
            win_sec=float(op["win_sec"]))
    return out


def summarise(bench_rows, swell_rows) -> dict:
    from bugarach import bench

    R = dict(bench={}, swells={})
    for stream in STREAMS:
        mod = bench_module(stream)
        R["bench"][stream] = {}
        for regime in mod.REGIMES:
            pick = [r for r in bench_rows if r["stream"] == stream and r["regime"] == regime]
            entry = {}
            for name in DETECTORS:
                planted = [r for r in pick if r["kind"] == "planted"]
                p = bench.pool_scores([r["det"][name]["score"] for r in planted],
                                      detector=name, regime=regime,
                                      seeds=[r["seed"] for r in planted])
                el = [r for r in pick if r["kind"] == "elevated"]
                d = dict(f1=p.f1, recall=p.recall, precision=p.precision,
                         n_planted_scored=p.n_scored, n_hit=p.n_hit, n_false_alarm=p.n_fa,
                         n_calls=p.n_detected, n_recordings=len(planted),
                         # A decoy is planted coordination labelled negative (ADR-0006), so a
                         # call on one counts against precision above and not against these.
                         calls_on_decoys=p.decoy_calls,
                         f1_without_decoys=p.f1_without_decoys,
                         precision_without_decoys=p.precision_without_decoys,
                         under_floor=bench.under_floor_report(p)["by_participation"],
                         recall_by_participation={f"{k:g}": [n, h] for k, (n, h)
                                                  in sorted(p.by_frac.items())},
                         elevated_calls_per_min=(
                             sum(r["det"][name]["calls_in"] for r in el)
                             / max(sum(r["det"][name]["minutes_in"] for r in el), 1e-9)))
                if name == "stack":
                    d["stability_sec"] = {
                        k: sorted(sum((r["det"][name]["stability"][k] for r in planted), []))
                        for k in ("hit", "false_alarm")}
                    d["median_alpha"] = float(np.median(
                        [r["det"][name]["alpha"] for r in planted]))
                    nul = [r["det"][name]["null"] for r in planted]
                    hrs = sum(n["hours"] for n in nul)
                    d["rigid_shift_calls_per_hour"] = dict(
                        count_sliding=sum(n["ref_calls"] for n in nul) / hrs,
                        stack=sum(n["stack_calls"] for n in nul) / hrs)
                entry[name] = d
            entry["floors"] = sorted(r["floor"] for r in pick if r["kind"] == "planted")
            # Per recording, what a raster page is picked on (tools/make_stack_rasters.py).
            entry["per_recording"] = [
                dict(kind=r["kind"], seed=r["seed"], floor=r["floor"],
                     **{n: dict(calls=r["det"][n]["n_calls"],
                                decoy_calls=int(r["det"][n]["score"].decoy_calls),
                                under_floor_calls=int(sum(
                                    c for _, c in (r["det"][n]["score"].dont_care_by_frac
                                                   or {}).values())),
                                calls_in_stretch=r["det"][n].get("calls_in"))
                        for n in DETECTORS})
                for r in pick]
            R["bench"][stream][regime] = entry
        nulls = [r for r in bench_rows if r["stream"] == stream and r["kind"] == "null"]
        hours = sum(r["hours"] for r in nulls)
        R["bench"][stream]["no_coordination"] = dict(
            n_recordings=len(nulls), hours=hours,
            calls_per_hour={n: sum(r["det"][n]["n_calls"] for r in nulls) / hours
                            for n in DETECTORS})
    for world in WORLDS:
        rows = [r for r in swell_rows if r["world"] == world]
        hours = sum(r["hours"] for r in rows)
        null_hours = sum(r["null"]["hours"] for r in rows)
        per = {n: [r["calls"][n] / r["hours"] for r in rows] for n in PAIR}
        R["swells"][world] = dict(
            n_recordings=len(rows), hours=hours,
            calls={n: sum(r["calls"][n] for r in rows) for n in PAIR},
            calls_per_hour={n: sum(r["calls"][n] for r in rows) / hours for n in PAIR},
            calls_per_hour_by_recording=per,
            # stack lands at or under count (sliding)'s rigid-shift rate, never exactly on it
            # (counts are whole numbers), so the fair reading is each rule against its own.
            times_its_rigid_shift_rate={
                n: (sum(r["calls"][n] for r in rows) / hours)
                / max(sum(r["null"]["ref_calls" if n == "count_sliding" else "stack_calls"]
                          for r in rows) / null_hours, 1e-12) for n in PAIR},
            recordings_where_stack_calls_fewer=sum(
                r["calls"]["stack"] < r["calls"]["count_sliding"] for r in rows),
            recordings_where_stack_calls_more=sum(
                r["calls"]["stack"] > r["calls"]["count_sliding"] for r in rows),
            rigid_shift_calls_per_hour=dict(
                count_sliding=sum(r["null"]["ref_calls"] for r in rows) / null_hours,
                stack=sum(r["null"]["stack_calls"] for r in rows) / null_hours),
            floors=sorted(r["floor"] for r in rows),
            stability_sec=sorted(sum((r["stability"] for r in rows), [])),
            example=next((r["example"] for r in rows if "example" in r), None))
    return R


# -- figures ----------------------------------------------------------------------------------

INK = {"coact": "#3b6fb6", "loco": "#7a4fa3", "chorus_norm": "#2a8f7a",
       "count_sliding": "#555555", "stack": "#c8501e"}
NAME = {"coact": "CoactDetect", "loco": "LoCo", "chorus_norm": "chorus_norm (learned)",
        "count_sliding": "count (sliding)", "stack": "stack"}
BAR = 0.8 / len(DETECTORS)
BG = {"baseline_quiet": "quiet", "baseline_busy": "busy"}


def figures(R, out: Path) -> list[Path]:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    from bugarach.time_axis import label as tlabel
    from bugarach.time_axis import ticks as tticks

    made = []
    groups = [(s, g) for s in STREAMS for g in BG]
    x = np.arange(len(groups))
    labels = [f"{s}\n{BG[g]}" for s, g in groups]

    # Figure 1: the benches.
    fig, axes = plt.subplots(1, 5, figsize=(21, 3.8))
    panels = (("f1", "F1 (harmonic mean of recall and precision)"),
              ("precision", "precision (share of calls on a planted event)"),
              ("precision_without_decoys", "precision, calls on decoys left out"),
              ("elevated_calls_per_min", "elevated-rate stretch (calls per minute)"))
    for ax, (key, lab) in zip(axes, panels):
        for j, name in enumerate(DETECTORS):
            v = [R["bench"][s][g][name][key] for s, g in groups]
            ax.bar(x + (j - (len(DETECTORS) - 1) / 2) * BAR, v, BAR, color=INK[name],
                   label=NAME[name])
        ax.set_xticks(x, labels, fontsize=8)
        ax.set_ylabel(lab, fontsize=8)
    ax = axes[4]
    xs = np.arange(len(STREAMS))
    for j, name in enumerate(DETECTORS):
        v = [R["bench"][s]["no_coordination"]["calls_per_hour"][name] for s in STREAMS]
        ax.bar(xs + (j - (len(DETECTORS) - 1) / 2) * BAR, v, BAR, color=INK[name])
    ax.set_xticks(xs, STREAMS, fontsize=8)
    ax.set_ylabel("no-coordination recording (calls per hour)", fontsize=8)
    for ax in axes[:3]:
        ax.set_ylim(0, 1)
    for ax in axes[:4]:
        ax.tick_params(axis="x", labelsize=6.5)
    handles, names = axes[0].get_legend_handles_labels()
    fig.legend(handles, names, frameon=False, fontsize=8, ncol=len(DETECTORS),
               loc="upper center")
    fig.tight_layout(rect=(0, 0, 1, 0.94))
    made.append(out / "fig1_bench.png")
    fig.savefig(made[-1], dpi=150)
    plt.close(fig)

    # Figure 2: which width wins.
    fig, axes = plt.subplots(1, len(STREAMS), figsize=(12, 3.4), sharey=True)
    for ax, s in zip(axes, STREAMS):
        widths = sorted({w for g in BG for k in ("hit", "false_alarm")
                         for w in R["bench"][s][g]["stack"]["stability_sec"][k]})
        xs = np.arange(len(widths))
        for j, (k, col, lab) in enumerate((("hit", "#2a7d3f", "calls on a planted event"),
                                           ("false_alarm", "#b03030", "false alarms"))):
            vals = sum((R["bench"][s][g]["stack"]["stability_sec"][k] for g in BG), [])
            share = [np.mean(np.isclose(vals, w)) if vals else 0.0 for w in widths]
            ax.bar(xs + (j - 0.5) * 0.38, share, 0.38, color=col,
                   label=f"{lab} ({len(vals)} calls)")
        ax.set_xticks(xs, [f"{w:g} s" for w in widths])
        ax.set_xlabel(f"winning window width · {s} bench", fontsize=9)
        ax.legend(frameon=False, fontsize=7, loc="upper right")
        ax.set_ylim(0, 1)
    axes[0].set_ylabel("share of stack's calls", fontsize=9)
    fig.tight_layout()
    made.append(out / "fig2_winning_width.png")
    fig.savefig(made[-1], dpi=150)
    plt.close(fig)

    # Figure 3: swells.
    fig, axes = plt.subplots(1, 3, figsize=(17, 3.8))
    xs = np.arange(len(WORLDS))
    short = {"sim_background": "flat", "shared_20s": "swell 20 s",
             "shallow_1min": "swell 1 min\n(shallow)", "drift_5min": "swell 5 min"}
    for ax, key, lab in ((axes[0], "calls_per_hour", "calls per hour on the recording"),
                         (axes[1], "rigid_shift_calls_per_hour",
                          "calls per hour on the recording's rigid shifts"),
                         (axes[2], "times_its_rigid_shift_rate",
                          "calls on the recording ÷ calls on its rigid shifts")):
        for j, name in enumerate(PAIR):
            v = [R["swells"][w][key][name] for w in WORLDS]
            ax.bar(xs + (j - 0.5) * 0.38, v, 0.38, color=INK[name], label=NAME[name])
            if key == "calls_per_hour":
                for xi, w in zip(xs, WORLDS):
                    ax.text(xi + (j - 0.5) * 0.38, v[list(WORLDS).index(w)],
                            f"{R['swells'][w]['calls'][name]}\ncalls", ha="center",
                            va="bottom", fontsize=6)
        if key == "times_its_rigid_shift_rate":
            ax.axhline(1.0, color="k", lw=0.6, ls=":")
        ax.set_xticks(xs, [f"{short[w]}\n{R['swells'][w]['hours']:.0f} h" for w in WORLDS],
                      fontsize=7)
        ax.set_ylabel(lab, fontsize=8)
    axes[0].legend(frameon=False, fontsize=8)
    fig.tight_layout()
    made.append(out / "fig3_swells.png")
    fig.savefig(made[-1], dpi=150)
    plt.close(fig)

    # Figure 4: one recording per swell world, calls in lanes above the count.
    shown = [w for w in WORLDS if R["swells"][w]["example"]]
    fig = plt.figure(figsize=(12, 2.6 * len(shown)))
    gs = fig.add_gridspec(2 * len(shown), 1, height_ratios=(0.5, 1.6) * len(shown), hspace=0.5)
    for r, w in enumerate(shown):
        ex = R["swells"][w]["example"]
        lane = fig.add_subplot(gs[2 * r])
        trace = fig.add_subplot(gs[2 * r + 1], sharex=lane)
        for j, name in enumerate(PAIR):
            on = ex["onsets"][name]
            lane.plot(on, np.full(len(on), j), "v", color=INK[name], ms=6)
        lane.set_yticks([0, 1], [f"{NAME[n]} ({len(ex['onsets'][n])} calls)"
                                 for n in PAIR], fontsize=7)
        lane.set_ylim(-0.6, 1.6)
        lane.tick_params(labelbottom=False, length=0)
        for side in ("top", "right", "bottom"):
            lane.spines[side].set_visible(False)
        trace.plot(ex["t"], ex["count"], color="k", lw=0.6)
        trace.axhline(R["swells"][w]["floors"][0], color="#888888", lw=0.5, ls=":")
        trace.set_ylabel(f"{WORLD_LABEL[w]}\nROIs with an onset\nin {ex['win_sec']:g} s",
                         fontsize=7)
        tk = tticks(0.0, ex["duration_sec"])
        # every panel is its own recording (the flat one is longer), so each keeps its axis
        trace.set_xticks(tk, [tlabel(t) for t in tk])
        trace.set_xlim(0, ex["duration_sec"])
    made.append(out / "fig4_swell_examples.png")
    fig.savefig(made[-1], dpi=150, bbox_inches="tight")
    plt.close(fig)
    return made


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--out", type=Path, default=None,
                    help=f"output folder (default: <darkroom>/{FOLDER})")
    ap.add_argument("--also", type=Path, default=None,
                    help="a second folder for the summary and figures, e.g. the run record")
    ap.add_argument("--seeds", type=int, default=24,
                    help="bench recordings per background (doubled on fast when realistic); "
                         "half as many no-coordination and elevated-rate recordings")
    ap.add_argument("--spacing", default="realistic", choices=("realistic", "bench"),
                    help="planted-event spacing: realistic is the reference since ADR-0010")
    ap.add_argument("--swells", type=int, default=192, help="recordings per swell world")
    ap.add_argument("--jobs", type=int, default=max(1, (os.cpu_count() or 2) - 2))
    ap.add_argument("--redraw", action="store_true",
                    help="redraw the figures from the folder's summary.json; measures nothing")
    a = ap.parse_args(argv)

    out = a.out
    if out is None:
        from bugarach.paths import darkroom
        out = darkroom(FOLDER, create=True)
        if out is None:
            raise SystemExit("no darkroom found; pass --out")
    out.mkdir(parents=True, exist_ok=True)
    if a.redraw:
        made = figures(json.loads((out / "summary.json").read_text()), out)
        if a.also:
            import shutil
            for p in made:
                shutil.copy2(p, a.also / p.name)
        print(*made, sep="\n")
        return

    # The spacing travels to every worker in the environment (bench.use_spacing). Seeds are the
    # fresh ones of tools/score_bench_candidates.py, which no search and no training run saw,
    # doubled on fast under a realistic spacing (bench.seed_factor; ADR-0010 ruling 2).
    from bugarach import bench
    bench.use_spacing(a.spacing)
    for s in STREAMS:
        chorus_path(s)                      # fail before the pool starts, not inside it
    tasks = []
    for s in STREAMS:
        f = bench.seed_factor(s)
        seeds = range(FRESH_SEED, FRESH_SEED + a.seeds * f)
        nulls = range(FRESH_SEED, FRESH_SEED + max(1, a.seeds // 2) * f)
        tasks += [(s, "planted", g, sd) for g in bench_module(s).REGIMES for sd in seeds]
        tasks += [(s, "elevated", g, sd) for g in bench_module(s).REGIMES for sd in nulls]
        tasks += [(s, "null", "baseline_quiet", sd) for sd in nulls]
    swells = [(w, i) for w in WORLDS for i in range(a.swells)]
    t0 = time.time()
    with mp.get_context("spawn").Pool(a.jobs) as pool:
        bench_rows = pool.map(bench_task, tasks, chunksize=2)
        swell_rows = pool.map(swell_task, swells, chunksize=2)
    R = summarise(bench_rows, swell_rows)
    R["settings"] = dict(
        tag=TAG, seeds=a.seeds, swells=a.swells, fractions=list(FRACTIONS),
        spacing=a.spacing, first_seed=FRESH_SEED,
        chorus_norm_checkpoints={s: chorus_path(s).name for s in STREAMS},
        shipped_points={s: {n: bench_module(s).OPERATING_POINTS[n].params
                            for n in ("coact", "loco")} for s in STREAMS},
        operating_points={s: bench_module(s).OPERATING_POINTS["count_sliding"].params
                          for s in STREAMS},
        frame_interval_sec=sorted({r["dt"] for r in bench_rows} | {r["dt"] for r in swell_rows}),
        tol_sec={s: bench_module(s).TOL_SEC for s in STREAMS},
        wall_sec=round(time.time() - t0, 1))
    made = figures(R, out)
    (out / "summary.json").write_text(json.dumps(R, indent=1))
    if a.also:
        import shutil
        a.also.mkdir(parents=True, exist_ok=True)
        for p in made + [out / "summary.json"]:
            shutil.copy2(p, a.also / p.name)

    for s in STREAMS:
        for g in BG:
            e = R["bench"][s][g]
            print(f"{s:9s} {BG[g]:5s} " + "  ".join(
                f"{NAME[n]}: F1 {e[n]['f1']:.3f} R {e[n]['recall']:.3f} P {e[n]['precision']:.3f} "
                f"hot {e[n]['elevated_calls_per_min']:.2f}/min" for n in DETECTORS))
        print(f"{s:9s} no-coordination calls/h", R["bench"][s]["no_coordination"]["calls_per_hour"])
    for w in WORLDS:
        e = R["swells"][w]
        print(f"{w:15s} calls {e['calls']} in {e['hours']:.0f} h; times own rigid-shift rate "
              f"{ {n: round(v, 2) for n, v in e['times_its_rigid_shift_rate'].items()} }  "
              f"fewer/more "
              f"{e['recordings_where_stack_calls_fewer']}/{e['recordings_where_stack_calls_more']}")
    for p in made:
        print(p)


if __name__ == "__main__":
    main()
