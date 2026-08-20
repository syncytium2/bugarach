#!/usr/bin/env python3
"""Are the coupled cells a module? Run it here, without MATLAB.

    python tools/modularity_null.py --store <onset store> --stream fast \
        --exclude-file docs/learned/lab_excluded_slices.txt --out docs/learned

Writes `modularity_null_<stream>.csv` with the same column names the interface2
pipeline used, so `tools/make_modularity_figure.py` reads either without change.

**Why this exists.** The modularity half of the assembly negative was computed by
`eval_modularity_null` in interface2. That project has no maintainer and its pipeline
does not run out of the box — its dead-ROI roster path resolves into a quarantined
export. See `docs/todo/2026-08-19-the-connectivity-pipeline-has-no-owner.md`.

**Two differences from the reference, both deliberate.**

- **`defined` is a column, and an untestable recording is not a zero.** The reference
  computed `above_null_Q` as `Q_obs > q_hi`, which is false for a missing value, so a
  recording too sparse to score was written out as `0` and read as tested-and-not-modular.
  That defect is in 13 verdict columns across 8 of its output files and it flatters every
  negative. Here such a recording gets `defined=0` and is excluded from any rate.
- **The window is bugarach's, not interface2's.** This uses the producer's analysis window
  where the export folder supplies one, and the baseline region otherwise — the same rule
  every other measurement in this repo uses. interface2 applies its own solution delay and
  floors. So per-recording numbers are **close but not identical** to the reference by
  construction, and the comparison that certifies the port is
  `tests/test_graph.py`, which holds the window fixed.
"""
from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

import numpy as np


def baseline_window(sl):
    """The window this repo scores: the producer's analysis window, else the region."""
    base = [r for r in (sl.regions or [])
            if (getattr(r, "name", "") or "").strip().lower().startswith("base")]
    if not base:
        return None
    r = max(base, key=lambda r: r.end_sec - r.start_sec)
    if getattr(r, "has_analysis_window", False):
        return float(r.analysis_start_sec), float(r.analysis_end_sec)
    return float(r.start_sec), float(r.end_sec)


def main(argv=None) -> int:
    p = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--store", type=Path, required=True)
    p.add_argument("--stream", default="fast")
    p.add_argument("--dt", type=float, default=2.0)
    p.add_argument("--jitter", type=float, default=20.0)
    p.add_argument("--surrogates", type=int, default=200)
    p.add_argument("--restarts", type=int, default=5)
    p.add_argument("--pctl", type=float, default=95.0)
    p.add_argument("--seed", type=int, default=7)
    p.add_argument("--limit", type=int, default=None)
    p.add_argument("--exclude-file", type=Path, default=None)
    p.add_argument("--out", type=Path, default=None,
                   help="destination directory; default $BUGARACH_DARKROOM")
    p.add_argument("--also", type=Path, default=None)
    a = p.parse_args(argv)

    from bugarach.assembly import load_excluded
    from bugarach.graph import modularity_vs_null
    from bugarach.store import load_slice

    excl = load_excluded(a.exclude_file)
    if excl:
        print(f"excluding {len(excl)} lab-withdrawn recording(s): {', '.join(sorted(excl))}")

    files = sorted(Path(a.store).glob("*.mat"))
    if a.limit:
        files = files[: a.limit]
    rows, skipped = [], {"excluded": 0, "no_baseline": 0, "no_stream": 0, "load_error": 0}

    for i, f in enumerate(files):
        if f.stem in excl:
            skipped["excluded"] += 1
            continue
        try:
            sl = load_slice(f)
        except Exception as e:                                   # noqa: BLE001
            skipped["load_error"] += 1
            print(f"  ~ {f.name}: {type(e).__name__}: {e}", file=sys.stderr)
            continue
        win = baseline_window(sl)
        if win is None:
            skipped["no_baseline"] += 1
            continue
        if a.stream not in sl.streams:
            skipped["no_stream"] += 1
            continue
        tr = sl.streams[a.stream]
        # **t50rise, not locs.** An event is located at its half-rise in this project
        # (`docs/export_folder_spec.md`; PRs #126/#127), `locs` is the peak, and the
        # MATLAB this ports reads `t50rise` too. Taking the peak would shift every
        # event by its own rise time and quietly change which cells look coincident.
        trains = [np.asarray(t, dtype=float) for t in tr.t50rise]
        trains = [t[np.isfinite(t)] for t in trains]
        res = modularity_vs_null(trains, dt=a.dt, t0=win[0], t1=win[1],
                                 n_surrogates=a.surrogates, n_restarts=a.restarts,
                                 jitter=a.jitter, pctl=a.pctl, seed=a.seed)
        rows.append({
            "slice": sl.slice_id, "n_active": res.n_active,
            "meanSTTC": res.mean_sttc, "Q_obs": res.q_obs,
            "Q_null_mu": res.q_null_mu, "Q_null_hi": res.q_null_hi,
            "z_Q": res.z,
            # `defined` FIRST in meaning: a reader must be able to tell "not tested"
            # from "tested, not modular", which the reference could not.
            "defined": int(res.defined),
            "above_null_Q": int(res.above_null),
        })
        if (i + 1) % 20 == 0:
            print(f"  ... {i + 1}/{len(files)}")

    scored = [r for r in rows if r["defined"] == 1]
    k = sum(1 for r in scored if r["above_null_Q"] == 1)
    print(f"\n{a.stream}: {len(rows)} recordings, {len(scored)} scored, "
          f"{len(rows) - len(scored)} undefined (NOT negative)")
    if scored:
        print(f"  above their own null: {k}/{len(scored)} = {k / len(scored) * 100:.1f}%"
              f"   (chance gives ~{100 - a.pctl:.0f}%)")
    print(f"  skipped: {skipped}")

    from bugarach.paths import darkroom, unresolved_message
    dest = Path(a.out) if a.out else darkroom()
    if dest is None:
        print(unresolved_message(), file=sys.stderr)
        return 1
    for d in [dest] + ([a.also] if a.also else []):
        d.mkdir(parents=True, exist_ok=True)
        out = d / f"modularity_null_{a.stream}.csv"
        with open(out, "w", newline="") as fh:
            w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()) if rows else
                               ["slice", "n_active", "meanSTTC", "Q_obs", "Q_null_mu",
                                "Q_null_hi", "z_Q", "defined", "above_null_Q"])
            w.writeheader()
            w.writerows(rows)
        print(f"wrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
