#!/usr/bin/env python3
"""The realistic bench's real-data inputs, extracted by one detector at its untuned defaults.

    python tools/extract_bench_inputs.py --out <folder> [--extractor count_sliding|coact_shipped]
        [--participation-from <folder>] [--no-calibration] [--workers N]

ADR-0012 (Tony, 2026-09-28): one function builds the bench and is the detector. count (sliding)
at one setting shared by every stream, a 2 s window, the window's own ADR-0008 floor as its
minimum (``min_rois`` = floor, ``k_offset`` 0) and a 3 s merge gap, is run on the real baseline
windows (FOUNDATIONS §9) and its calls give every input the generator takes:

* **spacing**: the gaps between neighbouring calls in a window, measured **call start to call
  start** (``onset_sec``, the first participating onset). Events per hour are calls per baseline
  hour.
* **participation**: each call's distinct ROIs with an onset in its 2 s window at the peak
  (``CountDetection.nrois``) as a share of the window's ROIs. The bench plants three levels: the
  middle is the median of that share, and the outer two keep their present ratios to the middle,
  which were chosen, not measured (``bench.py``, the note under ``BENCH_RECORDING``).
* **timing spread**: the standard deviation of the participating ROIs' first onsets within each
  call's span, its median over calls. That spread is not the generator's ``jitter_sec`` (the SD of
  each participant's offset from the event time): the 2 s window and the background shape it too,
  which is why the clustering spread was retired as the source of ``jitter_sec`` on 2026-09-22.
  So it is **calibrated**: the same extractor and statistic run on bench recordings planted at a
  grid of ``jitter_sec`` values, with this folder's spacing and participation in force, and the
  real value is read off that curve.

``--extractor coact_shipped`` runs CoactDetect at each stream's shipped setting (floor as its
minimum) instead, for ADR-0012's sensitivity check; with ``--participation-from`` it takes
participation and jitter from another folder, so only the spacing differs.

Writes into ``--out``: ``summary.json`` and ``gaps_for_generator.json`` in the shapes the bench
already reads (``bench.INTERVALS_RUN``), ``bench_inputs.json`` (participation levels and
``jitter_sec`` per stream), ``calls.csv``, ``windows.csv``, ``calibration.json`` and
``inputs.json`` (every number, with the dataset stamp). Point ``BUGARACH_BENCH_INPUTS`` at the
folder to build the bench from it (``bench.INPUTS_ENV``).
"""
from __future__ import annotations

import argparse
import csv
import importlib
import json
import multiprocessing as mp
import os
import sys
import warnings
from pathlib import Path

import numpy as np

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))

STREAMS = ("fast", "slow", "combined")
TAG = "real-intervals-2026-09-25"          # the real-intervals tool's floor seed, so floors match
BENCHES = {"fast": "bugarach.bench", "slow": "bugarach.bench_slow",
           "combined": "bugarach.bench_combined"}
#: count (sliding)'s untuned defaults, the extraction setting ADR-0012 fixes. The floor is
#: added per window. Changing any of these needs a new ADR.
EXTRACTION = dict(win_sec=2.0, k_offset=0, merge_gap_sec=3.0)
JITTER_GRID = (0.02, 0.05, 0.08, 0.12, 0.18, 0.25, 0.35, 0.5, 0.7)
CAL_SEEDS = tuple(range(9000, 9036))
DRAWS = 1000


def _shipped(stream: str) -> dict:
    return dict(importlib.import_module(BENCHES[stream]).OPERATING_POINTS["coact"].params)


def detect(extractor: str, stream: str, trains, t_range, floor: int):
    """``(onsets, widths, peak ROI counts or None)`` of the extractor on one window."""
    if extractor == "count_sliding":
        from bugarach.detectors.count import count_sliding_detect
        d = count_sliding_detect(trains, t_range, min_rois=int(floor), **EXTRACTION)
        return (np.asarray(d.onset_sec, float), np.asarray(d.width_sec, float),
                np.asarray(d.nrois, float))
    from bugarach.detectors.coact import coact_detect
    sys.path.insert(0, str(REPO / "tools"))
    from detect_with_floors import seeded       # the fixed seed `bugarach detect` gives it

    d = coact_detect(trains, t_range, **seeded("coact", dict(_shipped(stream), min_rois=int(floor))))
    return np.asarray(d.onset_sec, float), np.asarray(d.width_sec, float), None


def spread_of(trains, onset: float, width: float) -> float | None:
    """SD of the participating ROIs' first onsets within ``[onset, onset + width]``."""
    w = width if np.isfinite(width) and width > 0 else 0.0
    firsts = []
    for t in trains:
        t = np.asarray(t, float)
        m = (t >= onset - 1e-9) & (t <= onset + w + 1e-9)
        if m.any():
            firsts.append(float(t[m][0]))
    return float(np.std(firsts)) if len(firsts) >= 2 else None


def task(args):
    i, folder, extractor = args
    from bugarach import event_floor as ef
    from bugarach.combined import COMBINED, has_sources, stream_of
    from bugarach.detect_folder import _region_index, folder_analysis_windows
    from bugarach.detectors.rate import stream_trains
    from bugarach.io import load_folder

    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        s = load_folder(Path(folder))[i]
        meta = getattr(s, "meta", {}) or {}
        group = str(meta.get("group_id") or "").strip() or None
        s, windows = folder_analysis_windows(s)
    if has_sources(s) and COMBINED not in s.streams:
        s.streams[COMBINED] = stream_of(s, COMBINED)
    dt = s.require_dt()
    rows, calls = [], []
    for w in windows:
        if not (w.label or "").strip().lower().startswith("baseline"):
            continue
        lo, hi = float(w.win_start), float(w.win_end)
        idx = _region_index(w)
        for sname in STREAMS:
            if sname not in s.streams:
                continue
            tr = stream_trains(s.streams[sname], (lo, hi))
            n_frames = int(round((hi - lo) / dt))
            frames = [np.unique(np.floor((np.asarray(t, float) - lo) / dt + 1e-9).astype(np.int64))
                      for t in tr]
            base = dict(slice_id=s.slice_id, group=group, region_idx=idx, stream=sname,
                        hours=(hi - lo) / 3600.0, n_roi=len(tr))
            try:
                f = ef.window_floor(frames, n_frames, dt, key=(TAG, s.slice_id, sname, idx),
                                    draws=DRAWS)
            except ValueError as e:
                rows.append(dict(base, floor=None, n_calls=None, note=str(e)))
                continue
            on, wd, peak = detect(extractor, sname, tr, (lo, hi), f.floor)
            keep = (on >= lo) & (on < hi)
            on, wd = on[keep], wd[keep]
            peak = peak[keep] if peak is not None else None
            rows.append(dict(base, floor=f.floor, n_calls=int(on.size), note=""))
            for k in range(on.size):
                calls.append(dict(base, floor=f.floor, onset_sec=float(on[k]),
                                  width_sec=float(wd[k]),
                                  peak_rois=None if peak is None else int(peak[k]),
                                  spread_sec=spread_of(tr, float(on[k]), float(wd[k]))))
    return dict(rows=rows, calls=calls)


def describe(g: np.ndarray, hours: float, n_events: int) -> dict:
    """The real-intervals summary's fields, so ``bench.realistic_counts`` reads this unchanged."""
    if not g.size:
        return dict(n_gaps=0, n_events=n_events, hours=hours,
                    events_per_hour=n_events / hours if hours else None)
    p = {f"p{q}": float(np.percentile(g, q)) for q in (5, 25, 50, 75, 95)}
    return dict(n_gaps=int(g.size), n_events=n_events, hours=hours,
                events_per_hour=n_events / hours if hours else None, **p,
                share_under_10_sec=float(np.mean(g < 10)),
                share_under_120_sec=float(np.mean(g < 120)))


def gaps_of(calls: list[dict]) -> list[dict]:
    """Neighbouring calls in the same window, start to start."""
    by = {}
    for c in calls:
        by.setdefault((c["slice_id"], c["region_idx"], c["stream"]), []).append(c)
    out = []
    for cs in by.values():
        cs.sort(key=lambda c: c["onset_sec"])
        out += [dict(a, gap_sec=b["onset_sec"] - a["onset_sec"]) for a, b in zip(cs, cs[1:])]
    return out


def summarise(rows, calls, gaps, groups) -> dict:
    out = {}
    for s in STREAMS:
        R = [r for r in rows if r["stream"] == s and r["floor"] is not None]
        C = [c for c in calls if c["stream"] == s]
        G = np.array([g["gap_sec"] for g in gaps if g["stream"] == s])
        share = np.array([c["peak_rois"] / c["n_roi"] for c in C
                          if c.get("peak_rois") is not None and c["n_roi"]])
        spread = np.array([c["spread_sec"] for c in C if c["spread_sec"] is not None])
        entry = dict(all=dict(describe(G, sum(r["hours"] for r in R), len(C)),
                              participation_median=float(np.median(share)) if share.size else None,
                              participation_q25=float(np.percentile(share, 25)) if share.size else None,
                              participation_q75=float(np.percentile(share, 75)) if share.size else None,
                              spread_median_sec=float(np.median(spread)) if spread.size else None,
                              windows=len(R)), groups={})
        for grp in groups:
            Rg = [r for r in R if r["group"] == grp]
            Cg = [c for c in C if c["group"] == grp]
            Gg = np.array([g["gap_sec"] for g in gaps if g["stream"] == s and g["group"] == grp])
            sh = [c["peak_rois"] / c["n_roi"] for c in Cg if c.get("peak_rois") is not None]
            entry["groups"][grp] = dict(describe(Gg, sum(r["hours"] for r in Rg), len(Cg)),
                                        participation_median=float(np.median(sh)) if sh else None,
                                        recordings=len({r["slice_id"] for r in Rg}))
        out[s] = entry
    return out


def generator_docs(gaps, groups, stamp, rules) -> list[dict]:
    """``gaps_for_generator.json``: one document per stream in ``real_intervals``' schema."""
    docs = []
    for s in STREAMS:
        G = [g for g in gaps if g["stream"] == s]
        docs.append(dict(stream=s, dataset=stamp, rules=rules,
                         pooled=dict(gaps_sec=[round(g["gap_sec"], 4) for g in G]),
                         by_group={grp: dict(gaps_sec=[round(g["gap_sec"], 4) for g in G
                                                       if g["group"] == grp]) for grp in groups}))
    return docs


def levels(stream: str, middle: float) -> list[float]:
    """Three planted levels: the measured middle, the outer two at the bench's present ratios."""
    cur = importlib.import_module(BENCHES[stream]).BENCH_RECORDING["participation"]
    mid = cur[len(cur) // 2]
    return [round(min(0.95, middle * x / mid), 4) for x in cur]


def _cal_job(args):
    """Median within-call spread of the extractor on one planted bench recording."""
    stream, jitter, seed, regime, inputs = args
    os.environ["BUGARACH_BENCH_INPUTS"] = inputs
    os.environ["BUGARACH_BENCH_SPACING"] = "realistic"
    from bugarach import bench as B
    from bugarach.detectors.rate import stream_trains

    mod = importlib.import_module(BENCHES[stream])
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        s, gt = mod.make_recording(regime, seed, jitter_sec=jitter)
        ext = B.recording_extent(s)
        tr = stream_trains(s.streams[B.STREAM], ext)
        floor = gt.params["event_floor"]          # the recording's own ADR-0008 floor
        on, wd, _ = detect("count_sliding", stream, tr, ext, floor)
    sp = [spread_of(tr, float(a), float(b)) for a, b in zip(on, wd)]
    return stream, jitter, [x for x in sp if x is not None]


def calibrate(out: Path, real: dict, workers: int) -> dict:
    jobs = [(s, j, seed, reg, str(out)) for s in STREAMS for j in JITTER_GRID for seed in CAL_SEEDS
            for reg in ("baseline_quiet", "baseline_busy")]
    with mp.Pool(workers) as pool:
        got = pool.map(_cal_job, jobs)
    # Every call's spread pooled over seeds and both backgrounds, as on the real data, where the
    # statistic is the median over all calls. The curve is made non-decreasing (running maximum)
    # before it is inverted; where that changed a point, the record says so.
    cal = {}
    for s in STREAMS:
        curve = []
        for j in JITTER_GRID:
            v = [x for st, jj, xs in got if st == s and jj == j for x in xs]
            curve.append((j, float(np.median(v)) if v else None, len(v)))
        xs = np.array([j for j, m, _ in curve if m is not None])
        ys = np.array([m for j, m, _ in curve if m is not None])
        mono = np.maximum.accumulate(ys) if ys.size else ys
        target = real[s]
        inside = bool(ys.size and mono[0] <= target <= mono[-1])
        # Invert on the rising part only: a flat stretch has no single jitter.
        keep = np.concatenate([[True], np.diff(mono) > 0]) if mono.size else mono.astype(bool)
        est = float(np.interp(target, mono[keep], xs[keep])) if keep.sum() >= 2 else None
        cal[s] = dict(curve=[dict(jitter_sec=j, spread_median_sec=m, n_calls=n)
                             for j, m, n in curve],
                      real_spread_median_sec=target, jitter_sec=est, inside_grid=inside,
                      monotone=bool(np.all(np.diff(ys) > 0)) if ys.size > 1 else None,
                      points_raised_to_monotone=int(np.sum(mono != ys)),
                      floor_sec=float(mono[0]) if mono.size else None)
    return cal


def main(argv=None) -> int:
    from bugarach import dataset
    from bugarach.groups import in_group_order
    from bugarach.io import load_folder

    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--extractor", choices=("count_sliding", "coact_shipped"),
                    default="count_sliding")
    ap.add_argument("--participation-from", type=Path, default=None,
                    help="take bench_inputs.json (participation and jitter) from this folder")
    ap.add_argument("--no-calibration", action="store_true")
    ap.add_argument("--workers", type=int, default=16)
    a = ap.parse_args(argv)
    a.out.mkdir(parents=True, exist_ok=True)
    folder = dataset.default()
    stamp = dataset.stamp()
    n = len(load_folder(folder))
    with mp.Pool(a.workers) as pool:
        recs = pool.map(task, [(i, str(folder), a.extractor) for i in range(n)])
    rows = [r for rec in recs for r in rec["rows"]]
    calls = [c for rec in recs for c in rec["calls"]]
    groups = in_group_order({r["group"] for r in rows if r["group"]})
    gaps = gaps_of(calls)
    rules = dict(
        extractor=("count_sliding_detect at its untuned defaults, the same on every stream: "
                   f"win_sec {EXTRACTION['win_sec']:g}, min_rois = the window's own ADR-0008 floor, "
                   f"k_offset {EXTRACTION['k_offset']}, merge_gap_sec {EXTRACTION['merge_gap_sec']:g}")
        if a.extractor == "count_sliding" else
        "coact_detect at each stream's shipped setting, min_rois = the window's own ADR-0008 floor",
        floor="event_floor.window_floor, the baseline window's own, 1000 draws (the real-intervals "
              "tool's seed, so the floors match it)",
        windows="baseline windows only (FOUNDATIONS §9)",
        gap="between neighbouring calls in the same window, call start to call start (onset_sec)",
        participation="the call's peak distinct-ROI count in its 2 s window over the window's ROIs",
        spread="SD of the participating ROIs' first onsets within the call's span, median over calls")
    summ = summarise(rows, calls, gaps, groups)
    (a.out / "summary.json").write_text(json.dumps(dict(dataset=stamp, rules=rules, groups=groups,
                                                        summary=summ), indent=1), encoding="utf-8")
    (a.out / "gaps_for_generator.json").write_text(
        json.dumps(generator_docs(gaps, groups, stamp, rules), indent=1), encoding="utf-8")
    for name, rs in (("windows.csv", rows), ("calls.csv", calls)):
        cols = list(dict.fromkeys(k for r in rs for k in r))
        with (a.out / name).open("w", encoding="utf-8", newline="") as fh:
            w = csv.DictWriter(fh, fieldnames=cols)
            w.writeheader()
            w.writerows(rs)
    cal = None
    if a.participation_from is not None:
        inputs = json.loads((a.participation_from / "bench_inputs.json").read_text(encoding="utf-8"))
        inputs["note"] = (f"participation and jitter_sec taken from {a.participation_from.name}; "
                          f"only the spacing is this folder's own ({a.extractor})")
    else:
        inputs = dict(dataset=stamp, streams={s: dict(participation=levels(
            s, summ[s]["all"]["participation_median"])) for s in STREAMS})
        (a.out / "bench_inputs.json").write_text(json.dumps(inputs, indent=1), encoding="utf-8")
        if not a.no_calibration:
            cal = calibrate(a.out, {s: summ[s]["all"]["spread_median_sec"] for s in STREAMS},
                            a.workers)
            for s in STREAMS:
                inputs["streams"][s]["jitter_sec"] = round(cal[s]["jitter_sec"], 4)
            (a.out / "calibration.json").write_text(json.dumps(cal, indent=1), encoding="utf-8")
    (a.out / "bench_inputs.json").write_text(json.dumps(inputs, indent=1), encoding="utf-8")
    (a.out / "inputs.json").write_text(json.dumps(dict(
        dataset=stamp, extractor=a.extractor, extraction=EXTRACTION, rules=rules, summary=summ,
        bench_inputs=inputs, calibration=cal,
        failed=[r for r in rows if r["floor"] is None]), indent=1, default=str), encoding="utf-8")
    for s in STREAMS:
        al = summ[s]["all"]
        print(f"{s}: {al['n_events']} calls, {al.get('events_per_hour') or 0:.1f} per hour, "
              f"gap median {al.get('p50', float('nan')):.1f} s, participation "
              f"{al['participation_median']}, spread {al['spread_median_sec']}, inputs "
              f"{inputs['streams'][s]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
