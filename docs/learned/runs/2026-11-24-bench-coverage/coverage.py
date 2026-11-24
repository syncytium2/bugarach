"""Per-recording features of the tracked cohorts, beside the bench sets built from them.

Run from the repository root:  python docs/learned/runs/2026-11-24-bench-coverage/coverage.py

Writes ``coverage.csv`` beside this file (one row per recording, stream and threshold) and prints,
per stream and group, the range the recordings span next to the values the bench set plants.

Every quantity is read from a record the route already wrote, or measured with the route's own
function; nothing is measured a new way:

* ROIs, coordinated events per hour and participation (each event's peak count of ROIs with an
  onset in the 2 s window, as a share of the recording's ROIs, median over its events): the
  stage 1 intervals record (``tools/measure_real_intervals.py``), 4x only;
* background (mean onset rate per ROI minus the recording's coordinated share, the bench's own
  definition in ``tools/remeasure_bench.py``): the stage 1 coordination-rates record of each
  threshold;
* excess: Review A's statistic (``tools/make_review_a_pages.py``, which imports
  ``tools/measure_jitter_correlogram.py``), observed over chance cross-ROI onset pairs at lag
  0 to 0.3 s, minus 1, on the baseline analysis window.

Display and description only. The split by group describes what a synthetic set has to reproduce;
it compares nothing between groups (ADR-0017).
"""
from __future__ import annotations

import csv
import json
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parent
sys.path[:0] = [str(ROOT / "src"), str(ROOT / "tools")]

import make_review_a_pages as ra  # noqa: E402
from bugarach import bench_sets, dataset  # noqa: E402
from bugarach.groups import in_group_order  # noqa: E402
from bugarach.io import load_folder  # noqa: E402

K = 3  # lag bins of 0.1 s: 0 to 0.3 s
RUNS = ROOT / "docs" / "learned" / "runs"
RATES = {"4x": RUNS / "2026-11-12-stage1-tracked-cohorts-three-streams" / "rates"
         / "coordination_rates.json",
         "3x": RUNS / "2026-11-13-stage1-tracked-cohorts-3x" / "rates" / "coordination_rates.json"}
INTERVALS = RUNS / "2026-11-12-stage1-tracked-cohorts-three-streams" / "intervals"
ROLES = {"4x": "tracked_cohorts", "3x": "tracked_cohorts_3x"}


def backgrounds(stamps):
    out = {}
    for thr, p in RATES.items():
        d = json.loads(p.read_text(encoding="utf-8"))
        if d["dataset"]["name"] != stamps[thr]:
            raise SystemExit(f"{p} was measured on {d['dataset']['name']}, not {stamps[thr]}")
        for stream, v in d["streams"].items():
            for r in v["per_recording"]:
                share = r.get("share_hz") or 0.0
                out[(thr, stream, r["slice_id"])] = max(r["rate_hz"] - share, 0.0) * 60.0
    return out


def coordination(stamp4):
    summ = json.loads((INTERVALS / "summary.json").read_text(encoding="utf-8"))
    if summ["dataset"]["name"] != stamp4:
        raise SystemExit(f"the intervals record was measured on {summ['dataset']['name']}")
    win = {}
    with (INTERVALS / "windows.csv").open(encoding="utf-8", newline="") as fh:
        for r in csv.DictReader(fh):
            win[(r["stream"], r["slice_id"])] = (int(r["n_roi"]), float(r["hours"]),
                                                 int(r["n_events"]))
    peaks = defaultdict(list)
    with (INTERVALS / "events.csv").open(encoding="utf-8", newline="") as fh:
        for r in csv.DictReader(fh):
            peaks[(r["stream"], r["slice_id"])].append(int(r["peak_count"]))
    out = {}
    for key, (n_roi, hours, n_events) in win.items():
        p = peaks.get(key, [])
        out[key] = dict(events_per_hour=n_events / hours if hours else float("nan"),
                        participation=float(np.median(p)) / n_roi if p else float("nan"))
    return out


def main():
    stamps = {t: dataset.stamp(r)["name"] for t, r in ROLES.items()}
    for t, n in stamps.items():
        print(f"dataset {t}: {n}", file=sys.stderr)
    s4 = load_folder(dataset.current(ROLES["4x"]))
    s3 = load_folder(dataset.current(ROLES["3x"]))
    bg = backgrounds(stamps)
    co = coordination(stamps["4x"])
    rows = []
    for a, b in zip(s4, s3):
        g = str(a.meta.get("group_id") or "").strip().upper()
        for stream in ra.STREAMS:
            r = ra.real_trains(a, b, stream)
            for thr, key in (("4x", "t4"), ("3x", "t3")):
                o, e = ra.correlogram(r[key], r["hi"] - r["lo"])
                o, e = np.asarray(o, float), np.asarray(e, float)
                c = co.get((stream, a.slice_id), {}) if thr == "4x" else {}
                rows.append(dict(
                    slice_id=a.slice_id, group=g, stream=stream, threshold=thr, rois=len(r[key]),
                    background_per_min=round(bg[(thr, stream, a.slice_id)], 4),
                    events_per_hour=round(c.get("events_per_hour", float("nan")), 2),
                    participation=round(c.get("participation", float("nan")), 3),
                    excess_0_to_0p3s=round(float(o[:K].sum() / e[:K].sum() - 1.0), 3)))
    with (HERE / "coverage.csv").open("w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)

    groups = in_group_order(sorted({r["group"] for r in rows}))
    feats = ("rois", "background_per_min", "events_per_hour", "participation", "excess_0_to_0p3s")
    for stream in ra.STREAMS:
        for g in groups:
            sel = [r for r in rows if r["stream"] == stream and r["group"] == g
                   and r["threshold"] == "4x"]
            rng = {f: (min(r[f] for r in sel), max(r[f] for r in sel)) for f in feats}
            v = bench_sets.load(f"{stream}_{g.lower()}")
            rec = json.loads((ROOT / "docs" / "learned" / "bench_sets"
                              / f"{stream}_{g.lower()}.json").read_text(encoding="utf-8"))
            vals = rec["values"]
            print(f"{stream:9} {g:5} {len(sel)} recordings | "
                  + " | ".join(f"{f} {lo:g} to {hi:g}" for f, (lo, hi) in rng.items()))
            print(f"{'':15} bench set {v.__name__ if hasattr(v, '__name__') else stream}: "
                  f"ROIs {vals['n_roi']['measured']:g}, background "
                  f"{60 * vals['regime_quiet_hz']['measured']:.3g} and "
                  f"{60 * vals['regime_busy_hz']['measured']:.3g} per min, participation "
                  f"{vals['participation']['measured']:.3g}, "
                  f"{rec['events']['events_per_hour']:.3g} events per hour")
    print(f"wrote {HERE / 'coverage.csv'} ({len(rows)} rows)", file=sys.stderr)


if __name__ == "__main__":
    main()
