#!/usr/bin/env python3
"""Do real recordings crowd their own reference window? The bench assumes not.

    python tools/probe_real_crowding.py <export-folder> --json out.json

`BENCH_RECORDING` plants coordinated events **120 s** apart against a **±30 s**
reference window, so no planted event is ever inside another's context — the crowding
fraction is **0.00** by construction, and `CROWDED_RECORDING`'s docstring says in terms
that the masking failure guard cells exist for is *"impossible by construction on the
recording the detectors are scored on."* The `crowded` diagnostic plants at 0.38 and is
one *"nothing should be calibrated on."*

Neither number is an observation. This tool makes one: run CoactDetect at its shipped
FAST point over an export folder and ask of the **detected** events exactly what
`bench.nearest_neighbour_gaps` asks of planted ones — what fraction have another inside
their own ±`CROWDING_GAP_SEC` window.

**Detections are not ground truth**, and this does not pretend otherwise. It is a
statistic about the recordings, estimated with the only instrument available; a detector
that misses crowded events would understate the answer, which is the direction that
would make the bench look better than it is.

**The export folder is the input and nothing is filtered out of it** (FOUNDATIONS, and
the SAP007 incident). Recordings with fewer than three detections are reported as
uncharacterizable rather than dropped: a nearest-neighbour distribution needs three
points, and that is a limit of the statistic, not a judgement about the recording.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

from bugarach.bench import CROWDING_GAP_SEC, OPERATING_POINTS
from bugarach.detectors.coact import coact_detect
from bugarach.detectors.rate import recording_extent, stream_trains
from bugarach.io import load_folder

BENCH_PLANTED = 0.00       # BENCH_RECORDING, min_sep_sec=120 against a ±30 s window
CROWDED_PLANTED = 0.38     # CROWDED_RECORDING, measured, min_sep_sec=14


def nn_gaps(onsets):
    """Seconds to each event's nearest neighbour — the same quantity
    ``bench.nearest_neighbour_gaps`` computes for planted events."""
    on = np.sort(np.asarray(onsets, float))
    if on.size < 2:
        return np.empty(0)
    d = np.diff(on)
    return np.minimum(np.r_[d, np.inf], np.r_[np.inf, d])


def run(folder, stream="fast", verbose=True):
    params = dict(OPERATING_POINTS["coact"].params)
    rows, thin = [], []
    for s in load_folder(folder):
        if stream not in s.streams:
            thin.append(dict(slice_id=s.slice_id, why="stream absent"))
            continue
        ext = recording_extent(s)
        det = coact_detect(stream_trains(s.streams[stream], ext), ext,
                           rng_seed=20260706, **params)
        on = np.asarray(det.onset_sec, float)
        gaps = nn_gaps(on)
        if gaps.size < 3:
            thin.append(dict(slice_id=s.slice_id, why="fewer than 3 detections",
                             n_detected=int(on.size)))
            continue
        row = dict(slice_id=s.slice_id, minutes=(ext[1] - ext[0]) / 60.0,
                   n_detected=int(on.size), median_gap_sec=float(np.median(gaps)),
                   crowded_frac=float(np.mean(gaps < CROWDING_GAP_SEC)))
        rows.append(row)
        if verbose:
            print(f"  {row['slice_id']:22s} {row['minutes']:8.1f} min "
                  f"{row['n_detected']:5d} det  median gap "
                  f"{row['median_gap_sec']:7.1f} s  crowded {row['crowded_frac']:.2f}")
    return rows, thin


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("folder", type=Path, help="an export folder (docs/export_folder_spec.md)")
    p.add_argument("--stream", default="fast")
    p.add_argument("--json", type=Path, default=None)
    a = p.parse_args(argv)

    print(f"CoactDetect at its shipped point, stream {a.stream!r}, "
          f"crowding measured at ±{CROWDING_GAP_SEC:.0f} s\n")
    rows, thin = run(a.folder, a.stream)
    if not rows:
        print("no recording had enough detections to characterize")
        return 1

    fr = np.array([r["crowded_frac"] for r in rows])
    out = dict(folder=str(a.folder), stream=a.stream,
               gap_sec=CROWDING_GAP_SEC, recordings=rows, uncharacterized=thin,
               bench_planted=BENCH_PLANTED, crowded_planted=CROWDED_PLANTED)
    if a.json:
        a.json.write_text(json.dumps(out, indent=1))

    print(f"\n  {len(rows)} recordings characterized, {len(thin)} not "
          f"(fewer than 3 detections), {sum(r['n_detected'] for r in rows)} detections")
    print(f"  crowded fraction: median {np.median(fr):.2f}  mean {fr.mean():.2f}  "
          f"IQR {np.percentile(fr, 25):.2f}–{np.percentile(fr, 75):.2f}  "
          f"range {fr.min():.2f}–{fr.max():.2f}")
    print(f"  above the crowded diagnostic's {CROWDED_PLANTED:.2f}: "
          f"{int((fr > CROWDED_PLANTED).sum())}/{len(fr)}")
    print(f"\n  the bench plants {BENCH_PLANTED:.2f} — the median recording, and one end "
          f"of a range\n  the crowded diagnostic plants {CROWDED_PLANTED:.2f} — near the "
          f"top of the same range")
    return 0


if __name__ == "__main__":
    sys.exit(main())
