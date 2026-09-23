#!/usr/bin/env python3
"""Measure the SLOW stream's structure, for a slow bench that does not exist yet.

    python tools/measure_slow_bench.py --jobs 12             # measure, write the record
    python tools/measure_slow_bench.py --jobs 12 --no-write  # measure and print only

**Why a separate tool.** ``tools/remeasure_bench.py`` measures the fast bench and writes
``docs/learned/bench_measured.json`` unconditionally. Tony, 2026-09-21: the slow bench is
a separate module because there was no time to make ``bench.py`` handle two streams, and
a stream flag threaded through the shared tool is that same expansion in a second file
(``docs/handoffs/2026-09-21-slow-bench.md``). So this tool **imports** ``remeasure_bench``'s per-recording
measurement and its summary rather than copying them, and writes its own record. It
cannot overwrite the fast one: :data:`RECORD` is a different path, and the test pins it.
The duplication ends with ``docs/todo/2026-09-21-one-stream-aware-bench.md``.

**What it measures**, on the slow stream of :func:`bugarach.dataset.default`, over each
recording's baseline analysis window (``assess_folder.generation_window``, the rule
``bugarach assess`` reads; baseline only, FOUNDATIONS §9):

- the values ``remeasure_bench._values`` measures for the fast bench — the background's
  rate and burst shapes, the quiet and busy backgrounds (25th and 75th percentiles of
  per-recording mean ROI rate), ROI count and participation;
- ``jitter_sec``, read from the cross-ROI correlogram record (``rb.JITTER_RECORD``,
  written by ``tools/measure_jitter_correlogram.py``) for this stream, with that tool's
  own bootstrap interval. It is **not** derived from the per-bin assessment below: that
  instrument's within-cluster spread tracks the bin ÷ √12 rather than the recordings'
  timing, which is the defect the correlogram was built to get around;
- **jitter and participation again at each coincidence bin in** ``--bins``. The
  assessment's 1.0 s bin is the MATLAB default *for the faster stream*
  (``assess_coactivity``'s docstring) and there is no slow-stream convention anywhere in
  this tree, so which bin the slow bench should take is a choice. This records how much
  the two values depend on it instead of making the choice silently;
- **the width table**: the producer's slow ``width`` column at
  ``simulate.MEASURED_WIDTH_QUANTILE_LEVELS``, the levels the fast table uses, so the
  slow bench can hand locust slow widths. The column is taken as it comes (FOUNDATIONS
  §7); what it means is the producer's.

Every value carries a 95% bootstrap interval over recordings, as ``remeasure_bench``
does. There is no verdict yet: the slow bench's constants are set from this record in
the next step, and the comparison against them arrives with that module.
"""

from __future__ import annotations

import argparse
import datetime as _dt
import json
import sys
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np

REPO = Path(__file__).resolve().parents[1]
for _p in (REPO / "src", REPO / "tools"):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

import remeasure_bench as rb  # noqa: E402  (the fast tool; its measurement is reused)

STREAM = "slow"
RECORD = "docs/learned/bench_measured_slow.json"
"""Never ``bench.MEASURED_RECORD``: a slow write there would replace the fast record."""
RECORDS = {"slow": RECORD, "combined": "docs/learned/bench_measured_combined.json"}
"""``--stream combined`` (Tony, 2026-09-22) measures every fast and slow onset as one stream
(``bugarach.combined``) into its own record, read by ``bugarach.bench_combined``."""

BINS = (0.5, 1.0, 2.0, 3.0, 5.0)
"""Coincidence bins (s) jitter and participation are measured at. 1.0 is the fast
default and what ``remeasure_bench`` uses; 5.0 is about the slow stream's 5th-percentile
within-ROI interval, the widest bin that does not routinely hold two onsets of one ROI.

⚠ **Measured 2026-09-21: the jitter this instrument reports is set by the bin, on both
streams.** It tracks bin/√12 — the SD of onsets spread uniformly inside one bin — from
0.5 s to 5 s (fast 0.17 → 2.03 s, slow 0.21 → 1.39 s), so it does not identify a stream's
own onset jitter. Participation does not move with the bin (fast 0.19 at every bin; slow
0.37–0.38 from 0.5 s to 3 s). Figure: ``<darkroom>/bugarach/2026-09-21-slow-bench-jitter-vs-bin.png``."""


def _measure_recording(args):
    """One recording: ``remeasure_bench``'s record, plus the extra bins and the widths."""
    folder, index, n_surrogates, bins, stream = args
    rec = rb._measure_recording((folder, index, stream, n_surrogates))
    if rec["skipped"]:
        return rec
    from bugarach.assess import assess_coactivity
    from bugarach.combined import COMBINED, only_combined
    from bugarach.io import load_folder

    s = load_folder(Path(folder))[index]
    if stream == COMBINED:
        s = only_combined(s)
    lo, hi = rec["window"]
    st = s.streams[stream]
    widths = []
    for on, w in zip(st.t50rise or st.locs, st.width):
        on, w = np.asarray(on, float), np.asarray(w, float)
        keep = np.isfinite(on) & (on >= lo) & (on < hi) & np.isfinite(w)
        widths.extend(w[keep].tolist())
    rec["widths"] = widths

    rec["by_bin"] = {}
    for b in bins:
        a = next(r for r in assess_coactivity(s, stream=stream, window=(lo, hi),
                                              n_surrogates=n_surrogates, min_rois=(rb.K,),
                                              bin_width_sec=b)
                 if r.min_rois == rb.K)
        rec["by_bin"][f"{b:g}"] = {"part_n_obs": float(a.part_n_obs),
                                   "jit_obs": float(a.jit_obs)}
    return rec


def _bin_values(recs, bins) -> dict[str, float]:
    """Jitter and participation at each bin, derived exactly as ``rb._values`` does."""
    n_roi = np.median([r["n_roi"] for r in recs])
    out = {}
    for b in bins:
        k = f"{b:g}"
        part = np.array([r["by_bin"][k]["part_n_obs"] for r in recs], float)
        jit = np.array([r["by_bin"][k]["jit_obs"] for r in recs], float)
        out[f"jitter_sec@{k}s"] = float(np.median(jit[np.isfinite(jit)]))
        out[f"participation@{k}s"] = float(np.median(part[np.isfinite(part)]) / n_roi)
    return out


def _all_values(recs, bins) -> dict[str, float]:
    return {**rb._values(recs), **_bin_values(recs, bins)}


def width_quantiles(recs) -> list[float]:
    """The pooled slow widths at the fast table's levels, rounded as that table is."""
    from bugarach.simulate import MEASURED_WIDTH_QUANTILE_LEVELS

    w = np.concatenate([np.asarray(r["widths"], float) for r in recs])
    return [round(float(q), 2) for q in np.percentile(w, MEASURED_WIDTH_QUANTILE_LEVELS)]


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--boot", type=int, default=200,
                   help="bootstrap draws over recordings (default 200)")
    p.add_argument("--seed", type=int, default=20260921)
    p.add_argument("--surrogates", type=int, default=1000,
                   help="circular-shift surrogates per recording (default 1000)")
    p.add_argument("--bins", default=",".join(f"{b:g}" for b in BINS),
                   help="coincidence bins in seconds, comma-separated")
    p.add_argument("--jobs", type=int, default=1)
    p.add_argument("--no-write", action="store_true",
                   help="print the table; do not write the record")
    p.add_argument("--jitter-record", type=Path, default=REPO / rb.JITTER_RECORD,
                   help=f"the correlogram record jitter_sec is read from "
                        f"(default {rb.JITTER_RECORD})")
    p.add_argument("--rates-record", type=Path, default=REPO / rb.RATES_RECORD,
                   help=f"the coordination record each recording's coordinated share is "
                        f"read from, to make the regimes background rates "
                        f"(default {rb.RATES_RECORD})")
    p.add_argument("--stream", choices=sorted(RECORDS), default=STREAM,
                   help="slow (default) or combined; each writes its own record")
    a = p.parse_args(argv)
    bins = tuple(float(b) for b in a.bins.split(","))
    stream, record_path = a.stream, RECORDS[a.stream]

    from bugarach import dataset
    from bugarach.bench import MIN_BASELINE_SEC
    from bugarach.io import load_folder

    folder = dataset.default()
    stamp = dataset.stamp()
    n = len(load_folder(folder))
    print(f"{stamp['name']} ({n} recordings), stream {stream!r}, baseline analysis "
          f"windows, K = {rb.K}, bins {bins}")

    tasks = [(str(folder), i, a.surrogates, bins, stream) for i in range(n)]
    if a.jobs > 1:
        with ProcessPoolExecutor(max_workers=a.jobs) as ex:
            recs = list(ex.map(_measure_recording, tasks))
    else:
        recs = [_measure_recording(t) for t in tasks]
    skipped = {r["slice_id"]: r["skipped"] for r in recs if r["skipped"]}
    recs = [r for r in recs if not r["skipped"]]
    n_shape = sum(r["shape_usable"] for r in recs)
    print(f"{len(recs)} recordings measured ({n_shape} in the shape fits), "
          f"{len(skipped)} skipped")

    # Same background subtraction as the fast bench: `rb._values` takes each recording's
    # coordinated share off its total rate before the regime percentiles, so the slow
    # regimes are background rates too. Attached before the bootstrap, so a resampled draw
    # carries its own shares. See remeasure_bench.RATES_RECORD.
    shares = rb._shares_from_record(a.rates_record, stamp["name"], stream)
    for r in recs:
        r["share_hz"] = shares.get(r["slice_id"])
    have = sum(r["share_hz"] is not None for r in recs)
    print(f"coordinated share from {rb._repo_relative(a.rates_record)}: {have} of "
          f"{len(recs)} recordings; the regimes are background rates")

    point = _all_values(recs, bins)
    rng = np.random.RandomState(a.seed)
    draws = {k: [] for k in point}
    for _ in range(a.boot):
        pick = [recs[i] for i in rng.randint(0, len(recs), len(recs))]
        for k, v in _all_values(pick, bins).items():
            draws[k].append(v)

    jitter = rb._jitter_from_record(a.jitter_record, stream, stamp["name"])
    print(f"jitter_sec from {jitter['record']} ({jitter['stat']}, "
          f"{jitter['recordings']} recordings): {jitter['point']:.4f} s")

    rows, provenance = {}, {}
    print(f"\n{'value':20s} {'measured':>10s} {'95% interval':>21s}")
    for k in point:
        lo, hi = (float(x) for x in np.nanpercentile(draws[k], [2.5, 97.5]))
        row = {"measured": float(point[k]), "lo": lo, "hi": hi}
        # As in the fast tool: the superseded instrument is provenance, not a value.
        (provenance if k == "jitter_sec_clustering" else rows)[k] = row
        print(f"{k:20s} {point[k]:10.4f} {lo:10.4f} - {hi:<8.4f}"
              + ("  provenance" if k == "jitter_sec_clustering" else ""))
    rows["jitter_sec"] = {"measured": jitter["point"], "lo": jitter["interval"][0],
                          "hi": jitter["interval"][1], "source": jitter["record"],
                          "statistic": jitter["stat"]}
    print(f"{'jitter_sec':20s} {jitter['point']:10.4f} "
          f"{jitter['interval'][0]:10.4f} - {jitter['interval'][1]:<8.4f}")

    wq = width_quantiles(recs)
    n_w = sum(len(r["widths"]) for r in recs)
    print(f"\nwidths: {n_w} events; median {wq[50]} s, interquartile {wq[25]}-{wq[75]} s, "
          f"99th percentile {wq[99]} s, max {wq[-1]} s")

    record = {
        "dataset": stamp,
        "stream": stream,
        "window": rb.WINDOW_RULE,
        "min_baseline_sec": MIN_BASELINE_SEC,
        "k": rb.K,
        "bins_sec": list(bins),
        "recordings_measured": len(recs),
        "recordings_in_shape_fits": n_shape,
        "skipped": skipped,
        "bootstrap_draws": a.boot,
        "seed": a.seed,
        "surrogates": a.surrogates,
        "measured_on": _dt.date.today().isoformat(),
        "commit": rb._commit(),
        "tool": "tools/measure_slow_bench.py",
        "jitter_source": {
            "record": jitter["record"],
            "statistic": jitter["stat"],
            "recordings": jitter["recordings"],
            "tool": "tools/measure_jitter_correlogram.py",
        },
        "values": rows,
        "provenance": provenance,
        "width_events": n_w,
        "width_quantiles": wq,
    }
    if not a.no_write:
        (REPO / record_path).write_text(json.dumps(record, indent=1, sort_keys=True) + "\n",
                                   encoding="utf-8")
        print(f"\nwrote {record_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
