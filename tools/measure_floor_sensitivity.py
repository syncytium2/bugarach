#!/usr/bin/env python3
"""The ADR-0008 floor with each of its settings varied alone, and what count (sliding) calls at it.

    python tools/measure_floor_sensitivity.py --out <folder> [--workers 40] [--draws 1000]

**Why** (orchestrator's brief, 2026-09-28; Tony: "run the sensitivity check"). Tony is moving to a
one-statistic method: coordination is the number of ROIs with an onset in a sliding 2 s window, the
floor is set per window from that same count on rigid-shift shuffles, and a coordinated event is a
run at or above it (count (sliding), 2 s, k 0, merge 3 s). The bench cannot validate that, having
been built from the same statistic, so the floor's robustness is part of the evidence.

**What varies, one at a time, everything else at ADR-0008's value** (`bugarach.event_floor`):

* the false-alarm budget: 0.5, **1** and 2 chance calls per hour;
* the rigid shift's half-width J: 10, **20** and 40 s;
* the co-activity window the floor is counted in: 1, **2** and 3 s (the detector stays at 2 s; the
  floor-at-window experiment, #846, matched the two instead);
* the minimum: 2, **3** and 4 ROIs.

The null for the current setting is seeded exactly as ``tools/detect_with_floors.py`` seeds it, so
its floors reproduce that tool's. Varying J or the window changes the null itself (a new curve);
the budget and the minimum read the current curve differently. Every window the dataset declares,
baseline and treatment, on fast, slow and combined; baseline is reported first (FOUNDATIONS §9).

At each window's floor under each setting, count (sliding) runs and reports calls per hour and the
share of the current setting's calls it still makes (a call is kept when a call at the new setting
overlaps its span).

Writes ``windows.csv`` (one row per window, stream and setting), ``summary.json`` and
``fig1_floor_sensitivity.png``. Real treatment data: the darkroom, never the repo (FOUNDATIONS §5).
"""
from __future__ import annotations

import argparse
import csv
import json
import math
import multiprocessing as mp
import os
import sys
import warnings
from pathlib import Path

import numpy as np

REPO = Path(__file__).resolve().parents[1]
for _p in (REPO / "src", REPO / "tools"):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

STREAMS = ("fast", "slow", "combined")
DETECTOR = dict(win_sec=2.0, k_offset=0, merge_gap_sec=3.0)
#: (name, value, which null curve it reads, budget per hour, minimum)
SETTINGS = [
    ("current", "ADR-0008", (20.0, 2.0), 1.0, 3),
    ("fa_per_hour", 0.5, (20.0, 2.0), 0.5, 3),
    ("fa_per_hour", 2.0, (20.0, 2.0), 2.0, 3),
    ("j_sec", 10.0, (10.0, 2.0), 1.0, 3),
    ("j_sec", 40.0, (40.0, 2.0), 1.0, 3),
    ("window_sec", 1.0, (20.0, 1.0), 1.0, 3),
    ("window_sec", 3.0, (20.0, 3.0), 1.0, 3),
    ("minimum", 2, (20.0, 2.0), 1.0, 2),
    ("minimum", 4, (20.0, 2.0), 1.0, 4),
]
CURVES = sorted({s[2] for s in SETTINGS})


def floors_of(frames, n_frames, dt, key, draws):
    """Each setting's floor for one window: ``{(name, value): (floor, chance) or None}``."""
    from bugarach import event_floor as ef

    rates = {}
    for j, w in CURVES:
        try:
            runs, _, hours, _, _, _ = ef.null_curve(frames, n_frames, dt, key=key, draws=draws,
                                                    window_sec=w, j_sec=j)
        except ValueError:
            rates[(j, w)] = None
            continue
        rates[(j, w)] = runs.sum(axis=0) / (draws * hours)
    out = {}
    for name, val, curve, budget, minimum in SETTINGS:
        r = rates[curve]
        if r is None:
            out[(name, val)] = None
            continue
        chance = ef.floor_of(r, budget)
        out[(name, val)] = (max(minimum, chance), chance)
    return out


def calls_at(trains, span, floor):
    from bugarach.detectors.count import count_sliding_detect
    d = count_sliding_detect(trains, span, min_rois=int(floor), **DETECTOR)
    on, wd = np.asarray(d.onset_sec, float), np.asarray(d.width_sec, float)
    keep = (on >= span[0]) & (on < span[1])
    return on[keep], wd[keep]


def kept(cur, new) -> int:
    """Current calls that a call at the new setting overlaps."""
    (a_on, a_wd), (b_on, b_wd) = cur, new
    return int(sum(any((b0 <= a0 + aw) and (a0 <= b0 + bw) for b0, bw in zip(b_on, b_wd))
                   for a0, aw in zip(a_on, a_wd)))


def task(args):
    folder, i, draws = args
    from bugarach.combined import COMBINED, has_sources, stream_of
    from bugarach.detect_folder import _region_index, folder_analysis_windows
    from bugarach.detectors.rate import stream_trains
    from bugarach.io import load_folder
    from detect_with_floors import TAG, frames_in, is_baseline

    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        s = load_folder(Path(folder))[i]
        meta = getattr(s, "meta", {}) or {}
        s, windows = folder_analysis_windows(s)
    if has_sources(s) and COMBINED not in s.streams:
        s.streams[COMBINED] = stream_of(s, COMBINED)
    dt = s.require_dt()
    group = str(meta.get("group_id") or "").strip() or None
    rows = []
    for w in windows:
        lo, hi = float(w.win_start), float(w.win_end)
        if hi <= lo:
            continue
        idx = _region_index(w)
        label = (w.label or "").strip() or None
        for sname in STREAMS:
            if sname not in s.streams:
                continue
            tr = stream_trains(s.streams[sname], (lo, hi))
            n_frames = int(round((hi - lo) / dt))
            fl = floors_of(frames_in(tr, lo, dt), n_frames, dt, (TAG, s.slice_id, sname, idx),
                           draws)
            cache, base = {}, fl[("current", "ADR-0008")]
            cur = calls_at(tr, (lo, hi), base[0]) if base else None
            for (name, val), v in fl.items():
                row = dict(slice_id=s.slice_id, group=group, region_idx=idx, label=label,
                           window_kind="baseline" if is_baseline(label) else "treatment",
                           stream=sname, n_roi=len(tr), hours=(hi - lo) / 3600.0,
                           setting=name, value=val,
                           floor=None if v is None else v[0], chance_floor=None if v is None else v[1],
                           current_floor=None if base is None else base[0])
                if v is not None:
                    if v[0] not in cache:
                        cache[v[0]] = calls_at(tr, (lo, hi), v[0])
                    c = cache[v[0]]
                    row.update(n_calls=int(c[0].size),
                               current_calls=None if cur is None else int(cur[0].size),
                               kept=None if cur is None else kept(cur, c))
                rows.append(row)
    return rows


def summarise(rows, groups):
    """Per kind, stream, setting (and group): floor change in ROIs and %, calls per hour, share
    of current calls kept."""
    def block(R):
        R = [r for r in R if r["floor"] is not None and r["current_floor"] is not None]
        if not R:
            return None
        d = np.array([r["floor"] - r["current_floor"] for r in R], float)
        pct = np.array([100 * (r["floor"] - r["current_floor"]) / r["n_roi"] for r in R
                        if r["n_roi"]], float)
        h = sum(r["hours"] for r in R)
        calls, cur = sum(r["n_calls"] for r in R), sum(r["current_calls"] for r in R)
        kept_ = sum(r["kept"] for r in R)
        return dict(windows=len(R), moved=int(np.sum(d != 0)),
                    floor_change_median_rois=float(np.median(d)),
                    floor_change_min_rois=float(d.min()), floor_change_max_rois=float(d.max()),
                    floor_change_median_pct=float(np.median(pct)) if pct.size else None,
                    calls_per_hour=calls / h if h else None,
                    current_calls_per_hour=cur / h if h else None,
                    calls_ratio=calls / cur if cur else None,
                    share_of_current_kept=kept_ / cur if cur else None)

    out = {}
    for kind in ("baseline", "treatment"):
        for sname in STREAMS:
            for name, val, *_ in SETTINGS:
                R = [r for r in rows if r["window_kind"] == kind and r["stream"] == sname
                     and r["setting"] == name and r["value"] == val]
                key = f"{kind}|{sname}|{name}={val}"
                out[key] = dict(all=block(R),
                                groups={g: block([r for r in R if r["group"] == g])
                                        for g in groups})
    return out


def figure(rows, path):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    names = ["fa_per_hour", "j_sec", "window_sec", "minimum"]
    label = {"fa_per_hour": "false alarms per hour", "j_sec": "shift half-width J (s)",
             "window_sec": "co-activity window (s)", "minimum": "minimum (ROIs)"}
    fig, axes = plt.subplots(3, 4, figsize=(15, 11))
    colors = ["#0e7c86", "#d62728"]
    for i, sname in enumerate(STREAMS):
        for j, name in enumerate(names):
            ax = axes[i, j]
            vals = [v for n, v, *_ in SETTINGS if n == name]
            hi = 3
            for c, v in zip(colors, vals):
                R = [r for r in rows if r["stream"] == sname and r["setting"] == name
                     and r["value"] == v and r["floor"] is not None
                     and r["current_floor"] is not None]
                x = np.array([r["current_floor"] for r in R], float)
                y = np.array([r["floor"] for r in R], float)
                rs = np.random.default_rng(1)
                jx, jy = rs.uniform(-0.2, 0.2, x.size), rs.uniform(-0.2, 0.2, y.size)
                base = np.array([r["window_kind"] == "baseline" for r in R])
                ax.scatter(x[base] + jx[base], y[base] + jy[base], s=9, color=c, alpha=0.7,
                           label=f"{label[name]} = {v:g}, baseline windows")
                ax.scatter(x[~base] + jx[~base], y[~base] + jy[~base], s=9, facecolors="none",
                           edgecolors=c, alpha=0.6, label=f"{label[name]} = {v:g}, treatment windows")
                if x.size:
                    hi = max(hi, x.max(), y.max())
            ax.plot([0, hi + 1], [0, hi + 1], color="#888", lw=1, ls="--")
            ax.set_xlim(0, hi + 1)
            ax.set_ylim(0, hi + 1)
            ax.set_xlabel(f"{sname} · floor at the current setting (ROIs)")
            ax.set_ylabel(f"floor with {label[name]} varied (ROIs)")
            ax.legend(fontsize=6, frameon=False, loc="upper left")
    fig.suptitle("Figure 1. Each window's floor with one setting varied, against its floor at "
                 "ADR-0008's settings (1 per hour, J 20 s, 2 s window, minimum 3); dashed: identity. "
                 "Points jittered by ±0.2 ROI.", fontsize=10, x=0.01, ha="left")
    fig.tight_layout()
    fig.savefig(path, dpi=140)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--workers", type=int, default=max(1, (os.cpu_count() or 2) - 6))
    ap.add_argument("--draws", type=int, default=1000)
    ap.add_argument("--limit", type=int, default=None)
    a = ap.parse_args(argv)
    a.out.mkdir(parents=True, exist_ok=True)
    from bugarach import dataset
    from bugarach.groups import in_group_order
    from bugarach.io import load_folder

    folder = dataset.default()
    n = len(load_folder(Path(folder)))
    if a.limit:
        n = min(n, a.limit)
    with mp.Pool(a.workers) as pool:
        rows = [r for part in pool.map(task, [(str(folder), i, a.draws) for i in range(n)],
                                       chunksize=1) for r in part]
    with (a.out / "windows.csv").open("w", newline="", encoding="utf-8") as fh:
        wr = csv.DictWriter(fh, fieldnames=list(dict.fromkeys(k for r in rows for k in r)))
        wr.writeheader()
        wr.writerows(rows)
    groups = in_group_order({r["group"] for r in rows if r["group"]})
    summ = summarise(rows, groups)
    (a.out / "summary.json").write_text(json.dumps(dict(
        dataset=dataset.stamp(), draws=a.draws, detector=DETECTOR,
        settings=[dict(name=s[0], value=s[1], null=dict(j_sec=s[2][0], window_sec=s[2][1]),
                       fa_per_hour=s[3], minimum=s[4]) for s in SETTINGS],
        groups=groups, summary=summ), indent=1), encoding="utf-8")
    figure(rows, a.out / "fig1_floor_sensitivity.png")
    for k, v in summ.items():
        x = v["all"]
        if x:
            print(f"{k:45s} moved {x['moved']:3d}/{x['windows']:3d}  Δfloor median "
                  f"{x['floor_change_median_rois']:+.1f} ({x['floor_change_min_rois']:+.0f}.."
                  f"{x['floor_change_max_rois']:+.0f}) {x['floor_change_median_pct']:+.0f}%  "
                  f"calls/h {x['calls_per_hour']:.1f} vs {x['current_calls_per_hour']:.1f}  kept "
                  f"{x['share_of_current_kept'] if x['share_of_current_kept'] is None else round(x['share_of_current_kept'], 2)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
