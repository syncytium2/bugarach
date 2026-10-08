#!/usr/bin/env python3
"""Search every setting of the stack ceiling's call rule on the three benches.

    python tools/search_stack_ceiling.py --also docs/learned/runs/2026-10-08-stack-ceiling
    python tools/search_stack_ceiling.py --out <folder> --seeds 2      # smoke

Tony, 2026-10-08, on the first bench run: *"stack_ceiling was not optimized?"* It was not. That
run searched the threshold alone and borrowed the window, the merge gap and the period, while
every detector beside it ran at an operating point searched over all of its settings.

**What is searched:** the window, the period, the merge gap and the threshold, as a full grid
(:data:`WIDTHS_SEC` x :data:`PERIODS_SEC` x :data:`MERGE_GAPS_SEC` x :data:`THRESHOLDS_SEC`), per
stream. A threshold of 0 is the rule with the rebuild cost switched off: the sliding count at
that window against the floor.

**What is not:** the ROI minimum. As for every detector since ADR-0008, it is the recording's
floor, counted in a 2 s window whatever the rule's own window is (the bench's default).

**Picked on half the seeds, reported on the other half**, as ``tools/search_all_settings.py``
does. On the even seeds a setting is admissible when it is inside count (sliding)'s three
limits: calls per hour with nothing planted, calls per minute in the raised-rate stretch on
either background, and the precision difference between the backgrounds. The pick is the
admissible setting with the highest F1, averaged over the quiet and busy backgrounds. Every
number reported is from the odd seeds, and the gain over each reference detector there carries a
95% bootstrap interval over recordings. A picked value on the edge of its grid is reported as
unbracketed.

Reference detectors and seeds are ``tools/measure_stack_ceiling.py``'s. Simulated recordings
only; nothing here opens an export folder.
"""

from __future__ import annotations

import argparse
import itertools
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

WIDTHS_SEC = (0.3, 0.5, 1.0, 2.0, 3.0, 5.0)
PERIODS_SEC = (30.0, 60.0, 120.0, 240.0, 480.0)
MERGE_GAPS_SEC = (0.2, 0.5, 1.5, 3.0, 5.0, 8.0)
THRESHOLDS_SEC = (0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 8.0, 10.0, 12.0, 15.0, 20.0, 25.0, 30.0)
AXES = dict(width_sec=WIDTHS_SEC, period_sec=PERIODS_SEC, merge_gap_sec=MERGE_GAPS_SEC,
            threshold_sec=THRESHOLDS_SEC)
SETTINGS = list(itertools.product(WIDTHS_SEC, PERIODS_SEC, MERGE_GAPS_SEC, THRESHOLDS_SEC))
FIELDS = ("n_planted", "n_detected", "n_hit", "hot_fa", "decoy_calls")
REFERENCES = mc.REFERENCES
STREAMS = ms.STREAMS
BOOTSTRAP_DRAWS = 2000


def counts(sc) -> list[int]:
    """What ``bench.pool_scores`` sums from a score, in :data:`FIELDS` order."""
    return [int(sc.n_planted), int(sc.n_detected), int(sc.n_hit), int(sc.hot_fa),
            int(getattr(sc, "decoy_calls", 0))]


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
               hours=gt.params["duration_sec"] / 3600.0)
    if kind == "elevated":
        h0, h1 = gt.params["hot_window"]
        out["minutes_in"] = (h1 - h0) / 60.0
    out["refs"] = {n: counts(score_stream(gt, ms.run(stream, n, s), tol_sec=mod.TOL_SEC))
                   for n in REFERENCES}
    op = mod.OPERATING_POINTS["count_sliding"].params
    floor = bench.floored_params("count_sliding", s, op, {}, mod.STREAM, None)["min_rois"]
    ext = recording_extent(s)
    trains = stream_trains(s.streams[mod.STREAM], ext)
    centres = sc.frame_centres(ext, s.require_dt())
    grid = np.zeros((len(SETTINGS), len(FIELDS)), np.int32)
    k = 0
    for w in WIDTHS_SEC:
        for p in PERIODS_SEC:
            r = sc.stack_ceiling(trains, centres, width_sec=w, period_sec=p)
            cost = sc.rebuild_cost(r)
            for gap in MERGE_GAPS_SEC:
                for th in THRESHOLDS_SEC:
                    det = sc.detection_from(r, cost, threshold_sec=th, min_rois=floor,
                                            merge_gap_sec=gap)
                    grid[k] = counts(score_stream(gt, det, tol_sec=mod.TOL_SEC))
                    k += 1
    out.update(floor=int(floor), grid=grid)
    return out


def f1_of(c) -> float:
    """F1 from summed counts, as ``bench.BenchResult`` defines it: recall is hits over planted,
    precision is hits over the calls outside the raised-rate stretch."""
    planted, detected, hit, hot = (float(c[..., i]) for i in range(4))
    recall = hit / planted if planted else np.nan
    precision = hit / (detected - hot) if detected - hot else np.nan
    return 2 * recall * precision / (recall + precision) if recall + precision > 0 else np.nan


def precision_of(c) -> float:
    return float(c[2]) / float(c[1] - c[3]) if c[1] - c[3] else np.nan


class Half:
    """One stream's recordings from one half of the seeds, stacked for pooling."""

    def __init__(self, rows, stream: str):
        self.regimes = list(ms.bench_module(stream).REGIMES)
        mine = [r for r in rows if r["stream"] == stream]
        self.planted = {g: [r for r in mine if r["kind"] == "planted" and r["regime"] == g]
                        for g in self.regimes}
        self.elevated = {g: [r for r in mine if r["kind"] == "elevated" and r["regime"] == g]
                         for g in self.regimes}
        self.nulls = [r for r in mine if r["kind"] == "null"]
        self.n = len(mine)

    def get(self, r, key):
        return r["refs"][key] if isinstance(key, str) else r["grid"][key]

    def measures(self, key) -> dict:
        """One detector (a reference's name, or a setting's index) pooled over this half."""
        out = {}
        for g in self.regimes:
            c = np.sum([self.get(r, key) for r in self.planted[g]], axis=0)
            out[g] = dict(f1=f1_of(c), recall=float(c[2]) / max(float(c[0]), 1.0),
                          precision=precision_of(c), n_calls=int(c[1]), n_hit=int(c[2]),
                          n_planted=int(c[0]), calls_on_decoys=int(c[4]),
                          n_recordings=len(self.planted[g]))
        stretch = [sum(self.get(r, key)[3] for r in self.elevated[g])
                   / max(sum(r["minutes_in"] for r in self.elevated[g]), 1e-9)
                   for g in self.regimes]
        hours = sum(r["hours"] for r in self.nulls)
        out["mean_f1"] = float(np.mean([out[g]["f1"] for g in self.regimes]))
        out["worst_stretch_calls_per_min"] = float(max(stretch))
        out["no_coordination_calls_per_hour"] = (
            sum(self.get(r, key)[1] for r in self.nulls) / max(hours, 1e-9))
        out["precision_difference"] = float(abs(out[self.regimes[0]]["precision"]
                                                - out[self.regimes[-1]]["precision"]))
        return out

    def mean_f1_all(self) -> np.ndarray:
        """Mean F1 over the backgrounds for every setting at once."""
        total = np.zeros(len(SETTINGS))
        for g in self.regimes:
            c = np.sum([r["grid"] for r in self.planted[g]], axis=0).astype(float)
            recall = c[:, 2] / np.maximum(c[:, 0], 1.0)
            kept = c[:, 1] - c[:, 3]
            precision = np.divide(c[:, 2], kept, out=np.zeros(len(SETTINGS)), where=kept > 0)
            total += np.divide(2 * recall * precision, recall + precision,
                               out=np.zeros(len(SETTINGS)), where=recall + precision > 0)
        return total / len(self.regimes)

    def gain(self, key, other, rng) -> dict:
        """Mean F1 of ``key`` minus that of ``other``, with a 95% interval from resampling
        recordings within each background."""
        def mean_f1(k, pick):
            return float(np.mean([f1_of(np.sum([self.get(self.planted[g][i], k)
                                                for i in pick[g]], axis=0))
                                  for g in self.regimes]))
        whole = {g: range(len(self.planted[g])) for g in self.regimes}
        point = mean_f1(key, whole) - mean_f1(other, whole)
        draws = []
        for _ in range(BOOTSTRAP_DRAWS):
            pick = {g: rng.integers(0, len(self.planted[g]), len(self.planted[g]))
                    for g in self.regimes}
            draws.append(mean_f1(key, pick) - mean_f1(other, pick))
        lo, hi = np.nanpercentile(draws, [2.5, 97.5])
        return dict(gain=point, low=float(lo), high=float(hi))


def summarise(rows) -> dict:
    rng = np.random.default_rng(20261008)
    R = {}
    for stream in STREAMS:
        mod = ms.bench_module(stream)
        limits = dict(
            no_coordination_calls_per_hour=float(mod.MAX_FALSE_POSITIVES_PER_HOUR["count_sliding"]),
            worst_stretch_calls_per_min=float(mod.MAX_PROBE_PER_MIN["count_sliding"]),
            precision_difference=float(mod.MAX_PRECISION_DROP["count_sliding"]))
        pick = Half([r for r in rows if r["seed"] % 2 == 0], stream)
        report = Half([r for r in rows if r["seed"] % 2 == 1], stream)
        order = np.argsort(-pick.mean_f1_all(), kind="stable")
        best, top, n_checked = None, [], 0
        for k in order:
            m = pick.measures(int(k))
            n_checked += 1
            if all(m[name] <= limit for name, limit in limits.items()):
                top.append(int(k))
                best = int(k) if best is None else best
                if len(top) == 5:
                    break
        setting = dict(zip(AXES, SETTINGS[best]))
        shipped = SETTINGS.index((2.0, 120.0, 3.0, 0.0))
        # The attribution: the best admissible setting with the rebuild cost switched off, which
        # is the sliding count at its best window and merge gap. What the searched rule gains
        # over this is what the cost adds; the rest is the window and the gap.
        cost_off = next(int(k) for k in order if SETTINGS[k][3] == 0.0 and all(
            pick.measures(int(k))[name] <= limit for name, limit in limits.items()))
        R[stream] = dict(
            limits=limits, picked=setting,
            unbracketed=[a for a, v in setting.items() if v in (AXES[a][0], AXES[a][-1])],
            settings_ranked_above_the_pick_and_refused=n_checked - len(top) if len(top) < 5
            else int(np.flatnonzero(order == best)[0]),
            top_five_on_the_pick_half=[
                dict(setting=dict(zip(AXES, SETTINGS[k])), mean_f1=pick.measures(k)["mean_f1"])
                for k in top],
            pick_half=dict(picked=pick.measures(best),
                           count_at_the_borrowed_settings=pick.measures(shipped)),
            report_half=dict(
                picked=report.measures(best),
                count_at_the_borrowed_settings=report.measures(shipped),
                references={n: report.measures(n) for n in REFERENCES},
                best_with_the_cost_off=dict(setting=dict(zip(AXES, SETTINGS[cost_off])),
                                            **report.measures(cost_off)),
                gain_over_the_best_with_the_cost_off=report.gain(best, cost_off, rng),
                gain_over={n: report.gain(best, n, rng) for n in REFERENCES}),
            floors=sorted({r["floor"] for r in rows if r["stream"] == stream}),
            n_recordings=dict(pick=pick.n, report=report.n))
    R["_"] = dict(axes={a: list(v) for a, v in AXES.items()}, n_settings=len(SETTINGS),
                  bootstrap_draws=BOOTSTRAP_DRAWS)
    return R


def figure(R, out: Path) -> Path:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    names = list(REFERENCES) + ["ceiling"]
    fig, axes = plt.subplots(1, 3, figsize=(11.5, 3.6), sharey=True)
    for ax, stream in zip(axes, STREAMS):
        rep = R[stream]["report_half"]
        regimes = [g for g in rep["picked"] if g.startswith("baseline")]
        for i, n in enumerate(names):
            m = rep["picked"] if n == "ceiling" else rep["references"][n]
            for j, g in enumerate(regimes):
                x = i + (j - 0.5) * 0.38
                ax.bar(x, m[g]["f1"], width=0.36, color=mc.INK[n], alpha=1.0 if j == 0 else 0.55)
                ax.text(x, m[g]["f1"] + 0.012, f"{m[g]['f1']:.2f}", ha="center", fontsize=6.5)
        ax.set_xticks(range(len(names)),
                      [mc.NAME[n].replace(" (", "\n(") if n != "ceiling" else "stack ceiling\n(searched)"
                       for n in names], fontsize=7)
        ax.set_ylim(0, 1)
        ax.set_ylabel(f"{stream} · F1" if stream != STREAMS[0]
                      else f"{stream} · F1 (dark: quiet background, light: busy)", fontsize=8)
        ax.tick_params(axis="y", labelsize=8)
        for side in ("top", "right"):
            ax.spines[side].set_visible(False)
    fig.tight_layout()
    path = out / "explainer_stack-ceiling-search_20261008.png"   # tools/naming/artifact_name.py
    fig.savefig(path, dpi=170)
    plt.close(fig)
    return path


def table(R) -> str:
    lines = []
    for stream in STREAMS:
        S = R[stream]
        rep = S["report_half"]
        regimes = [g for g in rep["picked"] if g.startswith("baseline")]
        p = S["picked"]
        lines.append(f"\n{stream}: picked window {p['width_sec']:g} s, period {p['period_sec']:g} s, "
                     f"merge gap {p['merge_gap_sec']:g} s, threshold {p['threshold_sec']:g} s"
                     + (f"   UNBRACKETED: {', '.join(S['unbracketed'])}" if S["unbracketed"] else ""))
        lines.append(f"  {'detector':<28} " + "  ".join(f"F1 {g[9:]:<6}" for g in regimes)
                     + "  calls/h nothing planted  calls/min in stretch")
        rows = [(mc.NAME[n], rep["references"][n]) for n in REFERENCES]
        off = rep["best_with_the_cost_off"]
        rows += [("ceiling, borrowed, no cost", rep["count_at_the_borrowed_settings"]),
                 (f"best with cost off ({off['setting']['width_sec']:g}s/"
                  f"{off['setting']['merge_gap_sec']:g}s)", off),
                 ("stack ceiling, searched", rep["picked"])]
        for label, m in rows:
            lines.append(f"  {label:<28} " + "  ".join(f"{m[g]['f1']:<9.3f}" for g in regimes)
                         + f"  {m['no_coordination_calls_per_hour']:<23.2f}  "
                         f"{m['worst_stretch_calls_per_min']:.2f}")
        g = rep["gain_over_the_best_with_the_cost_off"]
        lines.append(f"  gain over best with cost off  {g['gain']:+.3f}  "
                     f"(95% {g['low']:+.3f} to {g['high']:+.3f})")
        for n in REFERENCES:
            g = rep["gain_over"][n]
            lines.append(f"  gain over {mc.NAME[n]:<18} {g['gain']:+.3f}  "
                         f"(95% {g['low']:+.3f} to {g['high']:+.3f})")
    return "\n".join(lines)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--out", type=Path, default=None,
                    help=f"output folder (default: <darkroom>/{mc.FOLDER})")
    ap.add_argument("--also", type=Path, default=None, help="a second folder for the outputs")
    ap.add_argument("--seeds", type=int, default=48,
                    help="bench recordings per background; half pick, half report")
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
        rows = pool.map(task, tasks, chunksize=1)
    R = summarise(rows)
    R["_"].update(seeds=a.seeds, n_recordings=len(rows), seconds=round(time.time() - t0, 1),
                  jobs=a.jobs)
    made = [out / "search_summary.json"]
    made[0].write_text(json.dumps(R, indent=1, default=float))
    made.append(figure(R, out))
    if a.also:
        a.also.mkdir(parents=True, exist_ok=True)
        for p in made:
            shutil.copy2(p, a.also / p.name)
    print(*made, sep="\n")
    print(table(R))
    print(f"\n{len(rows)} recordings, {len(SETTINGS)} settings each, in {R['_']['seconds']} s")


if __name__ == "__main__":
    main()
