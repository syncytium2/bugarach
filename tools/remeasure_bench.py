#!/usr/bin/env python3
"""Re-measure every value the bench claims to have measured, on the declared folder.

    python tools/remeasure_bench.py                 # measure, write the record, verdict
    python tools/remeasure_bench.py --no-write      # measure and print only
    python tools/remeasure_bench.py --jobs 12       # assess recordings in parallel

**Why this exists.** On 2026-09-17 Tony ruled that the current program reads one
folder, ``dataset.current("steps_excluded")``, and the same day it turned out the
bench did not: its background shapes had been fitted by
``tools/fit_background_shape.py`` on a closed ``.mat`` archive, and its structural
values (ROI count, onset jitter, participation) came from a MATLAB summary. Nothing
had flagged it, because every one of those origins was written down as prose. Tony:
*"not sure how to keep an eye on that."* This tool is the eye, and
``tests/test_bench_is_measured_on_the_declared_folder.py`` is what makes it blink.

**What it measures.** Exactly :func:`bugarach.bench.measured_constants`, on
:data:`~bugarach.bench.MEASURED_STREAM`, over each recording's **baseline analysis
window**: the window ``regions.csv`` says to score, chosen by
:func:`bugarach.assess_folder.generation_window`, the same rule ``bugarach assess``
reads. Baseline only (FOUNDATIONS §9).

- ``rate_shape`` and ``burst_shape_*``: the maximum-likelihood fits of
  ``tools/fit_background_shape.py``, with its own usability floors.
- ``regime_quiet_hz`` / ``regime_busy_hz``: the 25th and 75th percentiles of
  per-recording mean ROI rate, over the same windows.
- ``n_roi``, ``jitter_sec``, ``participation``: from ``assess_coactivity`` at K = 4,
  the MATLAB summary's own headline K. ``participation`` is median participants
  over median ROI count, as ``BENCH_RECORDING``'s docstring derives it.

**The verdict is an interval, not a tolerance.** Recordings are resampled with
replacement and every value refitted per draw. A constant inside its 95% interval
agrees with the folder; one outside it does not, and the tool exits 1. A fixed
percentage would call the 300 s burst shape "drifted" on estimator noise alone:
with windows of at most 1,200 s that fit sees four bins per window.

**It never edits** ``bench.py``. A value outside its interval moves the bench, which
moves every number measured on it, and that is Tony's call first.
"""

from __future__ import annotations

import argparse
import datetime as _dt
import json
import subprocess
import sys
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np

REPO = Path(__file__).resolve().parents[1]
if str(REPO / "src") not in sys.path:
    sys.path.insert(0, str(REPO / "src"))
if str(REPO / "tools") not in sys.path:
    sys.path.insert(0, str(REPO / "tools"))

K = 4
"""The coactivity floor for jitter and participation: the MATLAB summary's headline K
(``bench.MEASURED_PROVENANCE``)."""

WINDOW_RULE = ("longest baseline region; the folder's analysis window inside it "
               "(assess_folder.generation_window)")


def _measure_recording(args):
    """One recording's raw material. Top-level, so Windows can spawn it."""
    folder, index, stream, n_surrogates = args
    import fit_background_shape as fb
    from bugarach.assess import assess_coactivity
    from bugarach.assess_folder import NoBaselineRegion, generation_window
    from bugarach.io import load_folder

    s = load_folder(Path(folder))[index]
    out = {"slice_id": s.slice_id, "skipped": None}
    if stream not in s.streams:
        out["skipped"] = f"no {stream!r} stream"
        return out
    try:
        window, source = generation_window(s)
    except NoBaselineRegion as e:
        out["skipped"] = str(e)
        return out
    if window is None:
        out["skipped"] = "no regions declared, so no baseline window"
        return out
    lo, hi = window
    out.update(window=[lo, hi], window_source=source)

    st = s.streams[stream]
    trains = []
    for v in (st.t50rise or st.locs):
        v = np.asarray(v, dtype=float)
        v = v[np.isfinite(v)]
        trains.append((np.sort(v[(v >= lo) & (v < hi)]) - lo).tolist())
    counts = [len(t) for t in trains]
    dur = hi - lo
    # fit_background_shape's own floors decide which windows the shapes see.
    out["shape_usable"] = bool(dur >= fb.MIN_DURATION_SEC and sum(counts) >= fb.MIN_EVENTS
                               and len(counts) >= fb.MIN_ROIS)
    out.update(trains=trains, dur=dur)

    res = assess_coactivity(s, stream=stream, window=window, n_surrogates=n_surrogates,
                            min_rois=(K,))
    a = next(r for r in res if r.min_rois == K)
    out.update(n_roi=int(a.n_roi), part_n_obs=float(a.part_n_obs), jit_obs=float(a.jit_obs))
    return out


def _values(recs) -> dict[str, float]:
    """Every measured constant from one set of per-recording records."""
    import fit_background_shape as fb
    from bugarach.bench import MEASURED_BURST_BINS

    usable = [r for r in recs if r["shape_usable"]]
    counts = [np.array([len(t) for t in r["trains"]], float) for r in usable]
    windows_t = [([np.asarray(t, float) for t in r["trains"]], r["dur"]) for r in usable]
    means = np.array([np.mean(c / r["dur"]) for c, r in zip(counts, usable)])

    vals = {"rate_shape": fb.fit(counts)}
    for b in MEASURED_BURST_BINS:
        vals[f"burst_shape_{b:.0f}s"] = fb.fit_burst(windows_t, b)
    vals["regime_quiet_hz"] = float(np.percentile(means, 25))
    vals["regime_busy_hz"] = float(np.percentile(means, 75))

    n_roi = np.array([r["n_roi"] for r in recs], float)
    part = np.array([r["part_n_obs"] for r in recs], float)
    jit = np.array([r["jit_obs"] for r in recs], float)
    vals["n_roi"] = float(np.median(n_roi))
    vals["jitter_sec"] = float(np.median(jit[np.isfinite(jit)]))
    vals["participation"] = float(np.median(part[np.isfinite(part)]) / np.median(n_roi))
    return vals


def _commit() -> str:
    r = subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=REPO,
                       capture_output=True, text=True)
    return r.stdout.strip() or "unknown"


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--boot", type=int, default=200,
                   help="bootstrap draws over recordings (default 200)")
    p.add_argument("--seed", type=int, default=20260917)
    p.add_argument("--surrogates", type=int, default=1000,
                   help="circular-shift surrogates per recording for the assessment "
                        "(default 1000, what the reference numbers used)")
    p.add_argument("--jobs", type=int, default=1)
    p.add_argument("--no-write", action="store_true",
                   help="print the table; do not write the record")
    a = p.parse_args(argv)

    from bugarach import bench, dataset
    from bugarach.io import load_folder

    role = bench.MEASURED_ROLE
    folder = dataset.current(role)
    name = dataset.current_name(role)
    n = len(load_folder(folder))
    print(f"role {role!r} -> {name} ({n} recordings), stream {bench.MEASURED_STREAM!r}, "
          f"baseline analysis windows, K = {K}")

    tasks = [(str(folder), i, bench.MEASURED_STREAM, a.surrogates) for i in range(n)]
    if a.jobs > 1:
        with ProcessPoolExecutor(max_workers=a.jobs) as ex:
            recs = list(ex.map(_measure_recording, tasks))
    else:
        recs = [_measure_recording(t) for t in tasks]
    skipped = {r["slice_id"]: r["skipped"] for r in recs if r["skipped"]}
    recs = [r for r in recs if not r["skipped"]]
    n_shape = sum(r["shape_usable"] for r in recs)
    print(f"{len(recs)} recordings measured ({n_shape} with enough baseline events for the "
          f"shape fits), {len(skipped)} skipped")

    point = _values(recs)
    rng = np.random.RandomState(a.seed)
    draws = {k: [] for k in point}
    for _ in range(a.boot):
        pick = [recs[i] for i in rng.randint(0, len(recs), len(recs))]
        for k, v in _values(pick).items():
            draws[k].append(v)

    tree = bench.measured_constants()
    rows, all_inside = {}, True
    print(f"\n{'value':18s} {'in bench':>10s} {'measured':>10s} {'95% interval':>21s}  verdict")
    for k in tree:
        lo, hi = (float(x) for x in np.nanpercentile(draws[k], [2.5, 97.5]))
        inside = bool(lo <= tree[k] <= hi)
        all_inside &= inside
        rows[k] = {"bench": float(tree[k]), "measured": float(point[k]),
                   "lo": lo, "hi": hi, "inside": inside}
        print(f"{k:18s} {tree[k]:10.4f} {point[k]:10.4f} {lo:10.4f} - {hi:<8.4f}  "
              f"{'inside' if inside else 'OUTSIDE'}")

    record = {
        "role": role,
        "folder": name,
        "stream": bench.MEASURED_STREAM,
        "window": WINDOW_RULE,
        "k": K,
        "recordings_measured": len(recs),
        "recordings_in_shape_fits": n_shape,
        "skipped": skipped,
        "bootstrap_draws": a.boot,
        "seed": a.seed,
        "surrogates": a.surrogates,
        "measured_on": _dt.date.today().isoformat(),
        "commit": _commit(),
        "tool": "tools/remeasure_bench.py",
        "values": rows,
        "all_inside": all_inside,
    }
    if not a.no_write:
        path = REPO / bench.MEASURED_RECORD
        path.write_text(json.dumps(record, indent=1, sort_keys=True) + "\n", encoding="utf-8")
        print(f"\nwrote {bench.MEASURED_RECORD}")

    if not all_inside:
        print("\nOUTSIDE: at least one bench constant disagrees with the folder beyond its "
              "bootstrap interval. The bench is not edited here; moving it moves every "
              "number measured on it, so Tony decides first.", file=sys.stderr)
        return 1
    print("\nOK: every measured constant in the bench sits inside its interval on this folder.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
