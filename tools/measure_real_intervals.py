#!/usr/bin/env python3
"""The real inter-event intervals, measured without a detector (ADR-0010 part 2, step 1).

    python tools/measure_real_intervals.py --out <folder> [--also docs/learned/runs/<name>]
        [--workers 16] [--draws 1000]

**Why.** The bench plants coordinated events at least 120 s apart, and real ones are often seconds
apart. ADR-0010 (proposed) draws the bench's planted gaps from the real distribution instead. That
distribution is measured here **without any detector's calls**, because a detector's merging hides
the short gaps it is meant to reveal.

**How, for every recording of ``dataset.default()`` and each stream (fast, slow, combined), in
BASELINE windows only** (FOUNDATIONS §9):

1. **Co-activity count.** ``event_floor.coactive_counts``, the count ADR-0008's null uses: ROIs with
   an onset in a 2 s window, at every start position on the recording's own frame grid (its frame
   interval, not a fixed 0.1 s).
2. **Events.** Each maximal run of positions with count at or above the window's own floor
   (``event_floor.window_floor``, 1,000 draws) is one event. That is what the floor's null counts
   as one call. The event's time is the centre of its highest position, the first if tied.
   **Events whose times are less than 2 s apart (one co-activity window) are merged into one,
   keeping the higher.**
3. **Gaps.** The seconds between neighbouring events in the same window.

**What it writes.**
- ``gaps.csv``: one row per gap.
- ``events.csv``: one row per event.
- ``windows.csv``: one row per baseline window and stream, with its floor, hours and event count.
- ``intervals.json``: per stream, the pooled gaps and the gaps by group, for the generator to read.
- ``summary.json``: per stream and group, the percentiles, the shares under 10 s and 120 s, and
  the events per hour; plus each group against the rest by two-sample tests (Mann–Whitney U and
  Kolmogorov–Smirnov).

Every file carries ``dataset.stamp()``. It decides nothing: whether to pool the groups is Tony's
open point in ADR-0010.
"""
from __future__ import annotations

import argparse
import csv
import json
import multiprocessing as mp
import shutil
import sys
from pathlib import Path

import numpy as np

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))

STREAMS = ("fast", "slow", "combined")
TAG = "real-intervals-2026-09-25"
MERGE_SEC = 2.0


def events_of(counts: np.ndarray, floor: int, dt: float, wf: int, lo: float,
              merge_sec: float = MERGE_SEC) -> list[tuple[float, int]]:
    """``[(time_s, peak_count)]``: one per maximal run of ``counts >= floor``, at the run's highest
    position (the first if tied), timed at that window's centre; events closer than ``merge_sec``
    merged, keeping the higher (the earlier if equal)."""
    above = counts >= floor
    if not above.any():
        return []
    edges = np.flatnonzero(np.diff(np.concatenate([[0], above.astype(np.int8), [0]])))
    raw = []
    for a, b in zip(edges[::2], edges[1::2]):
        k = a + int(np.argmax(counts[a:b]))
        raw.append((lo + (k + wf / 2.0) * dt, int(counts[k])))
    merged = [raw[0]]
    for t, c in raw[1:]:
        if t - merged[-1][0] < merge_sec:
            if c > merged[-1][1]:
                merged[-1] = (t, c)
        else:
            merged.append((t, c))
    return merged


def task(args):
    i, folder, draws = args
    from bugarach import event_floor as ef
    from bugarach.combined import COMBINED, has_sources, stream_of
    from bugarach.detect_folder import _region_index, folder_analysis_windows
    from bugarach.detectors.rate import stream_trains
    from bugarach.io import load_folder

    s = load_folder(Path(folder))[i]
    meta = getattr(s, "meta", {}) or {}
    group = str(meta.get("group_id") or "").strip() or None
    s, windows = folder_analysis_windows(s)
    if has_sources(s) and COMBINED not in s.streams:
        s.streams[COMBINED] = stream_of(s, COMBINED)
    dt = s.require_dt()
    rows, evs, gaps = [], [], []
    for w in windows:
        label = (w.label or "").strip()
        if not label.lower().startswith("baseline"):
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
            wf = max(1, int(round(ef.WINDOW_SEC / dt)))
            base = dict(slice_id=s.slice_id, group=group, region_idx=idx, stream=sname,
                        dt=dt, hours=(hi - lo) / 3600.0, n_roi=len(tr))
            try:
                f = ef.window_floor(frames, n_frames, dt, key=(TAG, s.slice_id, sname, idx),
                                    draws=draws)
            except ValueError as e:
                rows.append(dict(base, floor=None, n_events=None, note=str(e)))
                continue
            e = events_of(ef.coactive_counts(frames, n_frames, wf), f.floor, dt, wf, lo)
            rows.append(dict(base, floor=f.floor, n_events=len(e), note=""))
            evs += [dict(base, time_sec=t, peak_count=c, floor=f.floor) for t, c in e]
            gaps += [dict(base, gap_sec=b[0] - a[0], floor=f.floor) for a, b in zip(e, e[1:])]
    return dict(slice_id=s.slice_id, group=group, rows=rows, events=evs, gaps=gaps)


def describe(g: np.ndarray, hours: float, n_events: int) -> dict:
    if not g.size:
        return dict(n_gaps=0, n_events=n_events, hours=hours,
                    events_per_hour=n_events / hours if hours else None)
    p = {f"p{q}": float(np.percentile(g, q)) for q in (5, 25, 50, 75, 95)}
    return dict(n_gaps=int(g.size), n_events=n_events, hours=hours,
                events_per_hour=n_events / hours if hours else None, **p,
                share_under_10_sec=float(np.mean(g < 10)),
                share_under_120_sec=float(np.mean(g < 120)))


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--also", type=Path, default=None)
    ap.add_argument("--workers", type=int, default=16)
    ap.add_argument("--draws", type=int, default=1000)
    a = ap.parse_args(argv)
    a.out.mkdir(parents=True, exist_ok=True)

    from scipy.stats import ks_2samp, mannwhitneyu

    from bugarach import dataset
    from bugarach.groups import in_group_order
    from bugarach.io import load_folder

    dataset.refuse_if_contaminated()
    folder = dataset.default()
    stamp = dataset.stamp()
    n = len(load_folder(folder))
    with mp.Pool(a.workers) as pool:
        recs = pool.map(task, [(i, str(folder), a.draws) for i in range(n)])
    rows = [r for rec in recs for r in rec["rows"]]
    events = [r for rec in recs for r in rec["events"]]
    gaps = [r for rec in recs for r in rec["gaps"]]
    groups = in_group_order({r["group"] for r in rows if r["group"]})

    def write(name, recs_, fields):
        with (a.out / name).open("w", newline="", encoding="utf-8") as fh:
            w = csv.DictWriter(fh, fieldnames=fields, extrasaction="ignore")
            w.writeheader()
            w.writerows(recs_)

    ident = ["slice_id", "group", "region_idx", "stream"]
    write("windows.csv", rows, ident + ["dt", "hours", "n_roi", "floor", "n_events", "note"])
    write("events.csv", events, ident + ["time_sec", "peak_count", "floor"])
    write("gaps.csv", gaps, ident + ["gap_sec", "floor"])

    summary, intervals = {}, {}
    for s in STREAMS:
        rs = [r for r in rows if r["stream"] == s and r["floor"] is not None]
        g_all = np.array([r["gap_sec"] for r in gaps if r["stream"] == s])
        summary[s] = dict(all=describe(g_all, sum(r["hours"] for r in rs),
                                       sum(r["n_events"] for r in rs)), groups={})
        intervals[s] = dict(pooled=sorted(g_all.tolist()), by_group={})
        for grp in groups:
            gi = np.array([r["gap_sec"] for r in gaps if r["stream"] == s and r["group"] == grp])
            rest = np.array([r["gap_sec"] for r in gaps if r["stream"] == s and r["group"] != grp])
            ri = [r for r in rs if r["group"] == grp]
            d = describe(gi, sum(r["hours"] for r in ri), sum(r["n_events"] for r in ri))
            d["recordings"] = len({r["slice_id"] for r in ri})
            if gi.size and rest.size:
                d["vs_rest"] = dict(
                    mann_whitney_p=float(mannwhitneyu(gi, rest, alternative="two-sided").pvalue),
                    ks_p=float(ks_2samp(gi, rest).pvalue),
                    median_rest_sec=float(np.median(rest)))
            summary[s]["groups"][grp] = d
            intervals[s]["by_group"][grp] = sorted(gi.tolist())
    rules = dict(grid="each recording's frame interval",
                 coactivity="event_floor.coactive_counts: ROIs with an onset in a 2 s window",
                 floor="event_floor.window_floor, the baseline window's own, "
                       f"{a.draws} draws", event="a maximal run of count >= floor, at its peak",
                 merge=f"events less than {MERGE_SEC} s apart merged, keeping the higher",
                 windows="baseline windows only (FOUNDATIONS section 9)",
                 caveat="gaps within one recording are not independent; the tests treat them as "
                        "if they were, so their p values are optimistic")
    (a.out / "summary.json").write_text(json.dumps(dict(dataset=stamp, groups=groups, rules=rules,
                                                        summary=summary), indent=1) + "\n")
    (a.out / "intervals.json").write_text(json.dumps(dict(
        dataset=stamp, rules=rules, units="seconds",
        streams=intervals), indent=1) + "\n")
    print(json.dumps({s: summary[s]["all"] for s in STREAMS}, indent=1))
    if a.also:
        a.also.mkdir(parents=True, exist_ok=True)
        for f in ("summary.json", "intervals.json", "windows.csv", "gaps.csv"):
            shutil.copy2(a.out / f, a.also / f)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
