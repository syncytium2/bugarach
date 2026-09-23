#!/usr/bin/env python3
"""Re-measure every value the bench claims to have measured, on the declared folder.

    python tools/remeasure_bench.py                 # measure, write the record, verdict
    python tools/remeasure_bench.py --no-write      # measure and print only
    python tools/remeasure_bench.py --jobs 12       # assess recordings in parallel

**Why this exists.** On 2026-09-17 Tony ruled that the current program reads one
folder — then the steps-excluded export, now whatever ``dataset.default()`` names —
and the same day it turned out the bench did not: its background shapes had been fitted by
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
- ``n_roi``, ``participation``: from ``assess_coactivity`` at K = 4, the MATLAB
  summary's own headline K. ``participation`` is median participants over median
  ROI count, as ``BENCH_RECORDING``'s docstring derives it.
- ``jitter_sec``: **not** from ``assess_coactivity``. Its within-cluster onset spread
  (``jit_obs``) tracks the coincidence bin ÷ √12 on both streams rather than the
  recordings' own timing, so it measured the instrument. The checked value is the
  cross-ROI correlogram's calibrated half-width from
  ``tools/measure_jitter_correlogram.py``, read from :data:`JITTER_RECORD` with that
  tool's own bootstrap interval. ``jit_obs``'s median is still recorded, as
  ``jitter_sec_clustering``, as provenance rather than as a checked value.

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

JITTER_RECORD = Path("docs/learned/runs/2026-09-22-jitter-correlogram/jitter_correlogram.json")
"""Where ``jitter_sec`` and its interval are read from, repo-relative.

``tools/measure_jitter_correlogram.py`` measures both streams in one run — it pools
cross-ROI correlograms over the folder and reads the real peak's half-width off a
calibration curve built by simulating each bench at a grid of planted jitters — so it
is not a per-recording quantity this tool can resample. Its record carries the
calibrated point and its own bootstrap interval, and the folder it was measured on;
:func:`_jitter_from_record` refuses a record measured on a different folder."""

JITTER_STAT = "hwhm"
"""Half-width at half height: the correlogram tool's own primary statistic (its
``primary`` field). The RMS lag it also records weights the 0-3 s tail by lag squared,
so noise there moves it."""


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
    from bugarach.bench import MIN_BASELINE_SEC

    if hi - lo < MIN_BASELINE_SEC:
        out["skipped"] = (f"baseline window {hi - lo:.0f} s, under the "
                          f"{MIN_BASELINE_SEC:.0f} s floor (bench.MIN_BASELINE_SEC)")
        return out
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
    vals["participation"] = float(np.median(part[np.isfinite(part)]) / np.median(n_roi))
    # Provenance, not a checked value: this is the bin-bound instrument. jitter_sec
    # comes from the correlogram record instead (JITTER_RECORD).
    vals["jitter_sec_clustering"] = float(np.median(jit[np.isfinite(jit)]))
    return vals


def _repo_relative(path: Path) -> str:
    """``path`` as a repo-relative posix string, so the record never carries a
    machine-local absolute path into a tracked file (sapper SAP004)."""
    p = Path(path).resolve()
    try:
        return p.relative_to(REPO).as_posix()
    except ValueError:
        # Outside the repo: name it without the part that identifies the machine.
        return p.name


def _jitter_from_record(path: Path, stream: str, folder_name: str) -> dict:
    """The correlogram's calibrated jitter for ``stream``, checked against the folder.

    Refuses a record measured on a different folder: a jitter from one export and
    every other constant from another is exactly the split provenance this tool
    exists to catch.
    """
    if not path.exists():
        raise SystemExit(
            f"no jitter record at {path}. Produce one with\n"
            f"  python tools/measure_jitter_correlogram.py --jobs 12 --out {path.parent}\n"
            "and commit it, or pass --jitter-record.")
    rec = json.loads(path.read_text(encoding="utf-8"))
    measured_on = (rec.get("dataset") or {}).get("name")
    if measured_on != folder_name:
        raise SystemExit(
            f"{path} was measured on {measured_on!r}, but this run reads {folder_name!r}. "
            "Re-run tools/measure_jitter_correlogram.py on this folder; a jitter from one "
            "export with every other constant from another is not a measurement of either.")
    if stream not in rec.get("streams", {}):
        raise SystemExit(f"{path} carries no {stream!r} stream (has "
                         f"{sorted(rec.get('streams', {}))}).")
    s = rec["streams"][stream]
    stat = s.get("primary", JITTER_STAT)
    row = s[stat]
    if not row.get("calibration_monotone", False):
        raise SystemExit(
            f"{path}: the {stream} calibration is not monotone, so a real width cannot be "
            "read off it. The record refuses the method rather than reporting a number.")
    if row.get("jitter_interval") is None:
        raise SystemExit(f"{path}: the {stream} bootstrap produced no interval.")
    return {"point": float(row["jitter_sec"]), "interval": [float(x) for x in row["jitter_interval"]],
            "stat": stat, "record": _repo_relative(path),
            "recordings": int(s.get("recordings", 0))}


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
    p.add_argument("--jitter-record", type=Path, default=REPO / JITTER_RECORD,
                   help=f"the correlogram record jitter_sec is read from "
                        f"(default {JITTER_RECORD})")
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

    jitter = _jitter_from_record(a.jitter_record, bench.MEASURED_STREAM, name)
    print(f"jitter_sec from {jitter['record']} ({jitter['stat']}, "
          f"{jitter['recordings']} recordings): {jitter['point']:.4f} s")

    tree = bench.measured_constants()
    rows, all_inside = {}, True
    print(f"\n{'value':18s} {'in bench':>10s} {'measured':>10s} {'95% interval':>21s}  verdict")
    for k in tree:
        if k == "jitter_sec":
            measured, (lo, hi) = jitter["point"], jitter["interval"]
        else:
            measured = float(point[k])
            lo, hi = (float(x) for x in np.nanpercentile(draws[k], [2.5, 97.5]))
        inside = bool(lo <= tree[k] <= hi)
        all_inside &= inside
        rows[k] = {"bench": float(tree[k]), "measured": measured,
                   "lo": lo, "hi": hi, "inside": inside}
        if k == "jitter_sec":
            rows[k]["source"] = jitter["record"]
            rows[k]["statistic"] = jitter["stat"]
        print(f"{k:18s} {tree[k]:10.4f} {measured:10.4f} {lo:10.4f} - {hi:<8.4f}  "
              f"{'inside' if inside else 'OUTSIDE'}")

    # Kept OUT of `values`, which means "the constants that were checked" and is compared
    # key-for-key against bench.measured_constants(). This is provenance: the instrument
    # jitter_sec used to come from, recorded so the correction stays legible.
    jc = np.nanpercentile(draws["jitter_sec_clustering"], [2.5, 97.5])
    provenance = {"jitter_sec_clustering": {
        "measured": float(point["jitter_sec_clustering"]),
        "lo": float(jc[0]), "hi": float(jc[1]),
        "note": ("assess_coactivity's within-cluster onset spread at K = 4, the instrument "
                 "that tracks the coincidence bin / sqrt(12). Superseded as the source of "
                 "jitter_sec on 2026-09-22; kept so the size of the correction is visible."),
    }}
    print(f"{'jitter_sec_clustering':18s} {'-':>10s} "
          f"{point['jitter_sec_clustering']:10.4f} {jc[0]:10.4f} - {jc[1]:<8.4f}  provenance")

    record = {
        "role": role,
        "folder": name,
        "stream": bench.MEASURED_STREAM,
        "window": WINDOW_RULE,
        "min_baseline_sec": bench.MIN_BASELINE_SEC,
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
        "jitter_source": {
            "record": jitter["record"],
            "statistic": jitter["stat"],
            "recordings": jitter["recordings"],
            "tool": "tools/measure_jitter_correlogram.py",
        },
        "values": rows,
        "provenance": provenance,
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
