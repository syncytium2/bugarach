#!/usr/bin/env python3
"""Elevated-rate stretches in the real recordings, measured the way the bench's is built.

    python tools/measure_rate_stretches.py --out <folder> [--workers 20] [--draws 1000]

**Why.** Every bench recording carries a planted 300 s *elevated-rate test*: every ROI's rate raised
together, nothing planted inside. Under ADR-0008, computed over the whole recording, that stretch
lifts the bench's floor above every planted event (#793). Tony's ruling so far is that the floor must
not move because the stretch's position is known: detectors meet real stretches nobody marks for
them. Whether real stretches exist, how large and broad they are, and in which windows and groups,
decides what the bench's stretch should look like. This tool measures that, and decides nothing.

**Definitions (fixed; the run record states them the same way).**

* **Population rate**: onsets per ROI per second in a sliding window of ``width`` seconds stepped by
  10 s, inside one analysis window. The primary width is 60 s; 30 s and 120 s are the check.
* **Elevation**, two ways, never mixed:
  * **within-window**: the population rate divided by the same window's median population rate;
  * **against baseline**: divided by the same recording's baseline-window median, same stream and
    width.
* **Breadth**: at each position, the fraction of the window's ROIs whose own rate there is above
  their own median rate over the window's positions.
* **A stretch**: a contiguous run of positions where within-window elevation is at least *k*, lasting
  at least 120 s. Its duration is from the first position's start to the last position's end
  (``last start − first start + width``). *k* = 2, 3 and 5, side by side. Per stretch: start (s into
  the window and in recording time), duration, peak within-window elevation, peak elevation against
  baseline, median breadth.
* A window whose median population rate is zero has no within-window elevation; it is counted and
  reported, never given one.

**The bench's stretch** is measured with the same code on bench recordings (seeds 1–8, quiet and
busy, the whole recording as one window), so the two sit on the same scales.

**Floor, secondary**: per window and stream, the ADR-0008 floor (``bugarach.event_floor``) over the
whole window, and over the window with its *k* = 3, 60 s stretches cut out (the remaining pieces
joined end to end, as ``tools/probe_bench_floor.py`` does for the bench).

Reads ``dataset.default()`` (read-only), every analysis window it declares, fast, slow and combined.
Nothing is filtered.
"""
from __future__ import annotations

import argparse
import json
import multiprocessing as mp
import sys
import time
from pathlib import Path

import numpy as np

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))

TAG = "rate-stretches-2026-09-24"
STREAMS = ("fast", "slow", "combined")
WIDTHS = (30.0, 60.0, 120.0)
PRIMARY = 60.0
STEP = 10.0
KS = (2.0, 3.0, 5.0)
MIN_STRETCH_SEC = 120.0
BENCH_SEEDS = tuple(range(1, 9))
BENCHES = {"fast": "bugarach.bench", "slow": "bugarach.bench_slow",
           "combined": "bugarach.bench_combined"}


def window_type(label) -> str:
    """baseline / TTX / senktide / high K+ / wash / other, from the folder's own label."""
    lab = (label or "").strip().lower()
    for key, name in (("baseline", "baseline"), ("ttx", "TTX"), ("senktide", "senktide"),
                      ("high k", "high K+"), ("wash", "wash")):
        if lab.startswith(key):
            return name
    return "other"


def rates(trains_sec, lo: float, hi: float, width: float, step: float = STEP):
    """``(starts, population rate, per-ROI rate matrix)`` over positions ``[a, a + width)``."""
    starts = np.arange(lo, hi - width + 1e-9, step)
    N = len(trains_sec)
    per = np.zeros((N, starts.size))
    for i, t in enumerate(trains_sec):
        t = np.sort(np.asarray(t, float))
        per[i] = (np.searchsorted(t, starts + width, side="left")
                  - np.searchsorted(t, starts, side="left")) / width
    pop = per.mean(axis=0) if N else np.zeros(starts.size)
    return starts, pop, per


def breadth(per: np.ndarray) -> np.ndarray:
    """Fraction of ROIs above their own median rate, at each position."""
    if per.size == 0:
        return np.zeros(per.shape[1] if per.ndim == 2 else 0)
    med = np.median(per, axis=1, keepdims=True)
    return (per > med).mean(axis=0)


def stretches(starts, elev, elev_base, brd, width: float, k: float) -> list[dict]:
    """Runs of positions with ``elev >= k`` lasting at least ``MIN_STRETCH_SEC``."""
    out = []
    hot = np.asarray(elev) >= k
    i, n = 0, hot.size
    while i < n:
        if not hot[i]:
            i += 1
            continue
        j = i
        while j + 1 < n and hot[j + 1]:
            j += 1
        dur = float(starts[j] - starts[i] + width)
        if dur >= MIN_STRETCH_SEC:
            sl = slice(i, j + 1)
            out.append(dict(start=float(starts[i]), end=float(starts[j] + width), duration=dur,
                            peak_elevation=float(np.max(elev[sl])),
                            peak_elevation_vs_baseline=(float(np.nanmax(elev_base[sl]))
                                                        if np.isfinite(elev_base[sl]).any()
                                                        else None),
                            median_breadth=float(np.median(brd[sl]))))
        i = j + 1
    return out


def measure_window(trains_sec, lo, hi, base_median: dict | None) -> dict:
    """Every width's curves and every k's stretches for one window and stream."""
    out = {}
    for width in WIDTHS:
        if hi - lo < width:
            out[str(width)] = dict(too_short=True)
            continue
        starts, pop, per = rates(trains_sec, lo, hi, width)
        med = float(np.median(pop))
        brd = breadth(per)
        with np.errstate(divide="ignore", invalid="ignore"):
            elev = pop / med if med > 0 else np.full(pop.shape, np.nan)
            b = (base_median or {}).get(str(width))
            elev_b = pop / b if b else np.full(pop.shape, np.nan)
        entry = dict(median_rate_hz=med, median_zero=med == 0, n_positions=int(starts.size),
                     peak_elevation=float(np.nanmax(elev)) if np.isfinite(elev).any() else None,
                     stretches={str(k): (stretches(starts, elev, elev_b, brd, width, k)
                                         if med > 0 else []) for k in KS})
        if width == PRIMARY:
            entry["curve"] = dict(starts=starts.tolist(), rate_hz=pop.tolist(),
                                  breadth=brd.tolist())
        out[str(width)] = entry
    return out


def cut_out(trains_sec, lo, hi, spans):
    """Onset frames of the window with ``spans`` removed and the pieces joined end to end."""
    keep, cursor = [], lo
    for a, b in sorted(spans):
        if a > cursor:
            keep.append((cursor, a))
        cursor = max(cursor, b)
    if cursor < hi:
        keep.append((cursor, hi))
    return keep


def floors(trains_sec, lo, hi, dt, spans, key, draws):
    from bugarach import event_floor as ef

    def frames(pieces):
        L, out = 0, [[] for _ in trains_sec]
        for a, b in pieces:
            n = int(round((b - a) / dt))
            for i, t in enumerate(trains_sec):
                t = np.asarray(t, float)
                t = t[(t >= a) & (t < b)]
                out[i].append(np.floor((t - a) / dt + 1e-9).astype(np.int64) + L)
            L += n
        return [np.unique(np.concatenate(x)) if x else np.zeros(0, np.int64) for x in out], L

    res = {}
    for name, pieces in (("whole", [(lo, hi)]), ("stretches_removed", cut_out(trains_sec, lo, hi,
                                                                             spans))):
        tr, L = frames(pieces)
        try:
            res[name] = ef.window_floor(tr, L, dt, key=(*key, name), draws=draws).as_dict()
        except ValueError as e:
            res[name] = dict(error=str(e))
    res["seconds_removed"] = float(sum(b - a for a, b in spans))
    return res


def recording_task(args):
    i, folder, draws = args
    from bugarach.combined import COMBINED, has_sources, stream_of
    from bugarach.detect_folder import folder_analysis_windows
    from bugarach.detectors.rate import stream_trains
    from bugarach.io import load_folder

    s = load_folder(Path(folder))[i]
    meta = getattr(s, "meta", {}) or {}
    head = dict(slice_id=s.slice_id, group=(str(meta.get("group_id")).strip() or None)
                if meta.get("group_id") else None,
                mouse=str(meta.get("subject_id") or s.slice_id))
    s, windows = folder_analysis_windows(s)
    if has_sources(s) and COMBINED not in s.streams:
        s.streams[COMBINED] = stream_of(s, COMBINED)
    dt = s.require_dt()
    wins = [(float(w.win_start), float(w.win_end), (w.label or "").strip()) for w in windows
            if float(w.win_end) > float(w.win_start)]
    kinds = [window_type(lab) for _, _, lab in wins]
    first = next((k for k in kinds if k not in ("baseline", "high K+", "wash")), None)
    head["first_treatment"] = first
    rows = []
    for sname in STREAMS:
        if sname not in s.streams:
            continue
        st = s.streams[sname]
        base = {}
        for (lo, hi, lab), kind in zip(wins, kinds):
            if kind == "baseline":
                for width in WIDTHS:
                    if hi - lo >= width:
                        base[str(width)] = float(np.median(
                            rates(stream_trains(st, (lo, hi)), lo, hi, width)[1]))
                break
        for idx, ((lo, hi, lab), kind) in enumerate(zip(wins, kinds)):
            tr = stream_trains(st, (lo, hi))
            m = measure_window(tr, lo, hi, base)
            spans = [(x["start"], x["end"]) for x in
                     m.get(str(PRIMARY), {}).get("stretches", {}).get(str(3.0), [])]
            rows.append(dict(head, stream=sname, window_index=idx, label=lab, window_type=kind,
                             win_start=lo, win_end=hi, hours=(hi - lo) / 3600.0,
                             n_roi=len(tr), measures=m,
                             floor=floors(tr, lo, hi, dt, spans,
                                          (TAG, s.slice_id, sname, idx), draws)))
    return rows


def bench_task(args):
    import importlib

    from bugarach.bench import recording_extent
    from bugarach.detectors.rate import stream_trains
    stream, regime, seed = args
    b = importlib.import_module(BENCHES[stream])
    # ADR-0009: the bench's stretch is on the elevated-rate recording, not the planted one.
    s, gt = b.make_elevated_rate_recording(regime, seed)
    lo, hi = recording_extent(s)
    tr = stream_trains(s.streams[b.STREAM], (lo, hi))
    m = measure_window(tr, lo, hi, None)
    h0, h1 = gt.params["hot_window"]
    return dict(stream=stream, regime=regime, seed=seed, hot_window=[h0, h1],
                measures={w: {k: v for k, v in e.items() if k != "curve"}
                          for w, e in m.items()})


def summarise(rows, groups):
    """Per stream × window type × group × k (primary width): recordings with a stretch, stretches
    per hour, median duration, median peak elevation, median breadth."""
    out = {}
    types = ("baseline", "TTX", "senktide", "high K+", "wash")
    for sname in STREAMS:
        for wt in types:
            for g in [*groups, "all"]:
                rs = [r for r in rows if r["stream"] == sname and r["window_type"] == wt
                      and (g == "all" or r["group"] == g)]
                if not rs:
                    continue
                for k in KS:
                    st = [x for r in rs for x in r["measures"][str(PRIMARY)]
                          .get("stretches", {}).get(str(k), [])]
                    with_st = {r["slice_id"] for r in rs if r["measures"][str(PRIMARY)]
                               .get("stretches", {}).get(str(k))}
                    hours = sum(r["hours"] for r in rs)
                    out.setdefault(sname, {}).setdefault(wt, {}).setdefault(g, {})[str(k)] = dict(
                        windows=len(rs), recordings=len({r["slice_id"] for r in rs}),
                        recordings_with_stretch=len(with_st), stretches=len(st),
                        stretches_per_hour=len(st) / hours if hours else None,
                        median_duration_sec=float(np.median([x["duration"] for x in st]))
                        if st else None,
                        median_peak_elevation=float(np.median([x["peak_elevation"] for x in st]))
                        if st else None,
                        median_breadth=float(np.median([x["median_breadth"] for x in st]))
                        if st else None,
                        windows_with_median_zero=sum(bool(r["measures"][str(PRIMARY)]
                                                          .get("median_zero")) for r in rs))
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--workers", type=int, default=20)
    ap.add_argument("--draws", type=int, default=1000)
    ap.add_argument("--limit", type=int, default=None)
    a = ap.parse_args(argv)
    a.out.mkdir(parents=True, exist_ok=True)
    from bugarach import dataset
    from bugarach.groups import in_group_order
    from bugarach.io import load_folder

    folder = dataset.default()
    n = len(load_folder(folder))
    if a.limit:
        n = min(n, a.limit)
    t0 = time.time()
    with mp.Pool(a.workers) as pool:
        rows = [r for rs in pool.map(recording_task, [(i, str(folder), a.draws)
                                                      for i in range(n)]) for r in rs]
        bench = pool.map(bench_task, [(s, reg, seed) for s in STREAMS
                                      for reg in ("baseline_quiet", "baseline_busy")
                                      for seed in BENCH_SEEDS])
    groups = in_group_order(r["group"] for r in rows if r.get("group"))
    res = dict(tag=TAG, dataset=dataset.stamp(), recordings=n, elapsed_sec=time.time() - t0,
               definitions=dict(widths_sec=list(WIDTHS), primary_width_sec=PRIMARY,
                                step_sec=STEP, ks=list(KS), min_stretch_sec=MIN_STRETCH_SEC,
                                floor_k=3.0, draws=a.draws),
               groups=groups, summary=summarise(rows, groups), bench=bench, rows=rows)
    (a.out / "results.json").write_text(json.dumps(res, default=float) + "\n")
    print(f"{n} recordings, {len(rows)} window-streams, {time.time() - t0:.0f} s")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
