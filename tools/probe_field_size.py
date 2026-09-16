#!/usr/bin/env python3
"""What changes about the detection problem when the field goes from 9 cells to 1050?

    python tools/probe_field_size.py [--out DIR] [--also DIR]

WHY THIS EXISTS. Tony, 2026-09-16: *"some recordings have 13 cells and some have 50
(500+ in another lab dataset)"*. Every architecture in `bugarach.learn.nets` reduces
the cell axis to one number and then thresholds it, and the reduction each one picks
is an answer to that sentence whether or not it was meant as one. This probe puts the
arithmetic beside the architectures so the answer can be read rather than assumed.

It computes three things, all closed-form, from statistics already measured and
committed in this tree — `docs/learned/assessment_real.json` (85 recordings of this
lab) and `docs/learned/assessment_cossart.json` (59 of DANDI:000219). **No detector
runs here and nothing is fitted**: this is the null model the detectors are supposed
to beat, not a measurement of any of them.

1. **The detection floor** — under an independent-cell null, the smallest number of
   co-active cells whose chance probability per frame is at or below a stated
   false-alarm budget. It is the number a detector cannot go below without firing on
   chance alignments, and it is a function of BOTH the field size and the per-cell
   rate.
2. **What a threshold fixed in one unit does elsewhere.** A count, a fraction of the
   field and a standardized excess are three different units; the first two move
   their own false-alarm rate when the field changes and the third does not. The
   table reports by how much.
3. **The contrast collapse** — the range of the exact scalar `tube` reads (the mean
   of the widened raster over cells) at background and at a typical event, in each
   corpus. A network head is a learned function of a numeric range, so a scalar whose
   range moves by two orders of magnitude between corpora is a transfer failure
   waiting in the arithmetic.

WHAT IT DOES NOT SETTLE. The null is independent cells at a single homogeneous rate,
which real recordings are not: per-cell rates are heterogeneous and onsets are not
independent within a cell (there is a dead-time floor — 0.40 s fast, 3.20 s slow on
the senktide baselines). Heterogeneity and dead time both move the true floor, in
opposite directions, and neither is modelled here. So the floors below are an
ORDERING and an order of magnitude, never an operating point. The within-recording
surrogate null that `assess` and CoactDetect already compute is the thing that gets
this right on real data; this probe exists to show why that matters, not to replace it.
"""
from __future__ import annotations

import argparse
import json
import math
import os
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent

# The lab's imaging grid. dt is required at load and never defaulted (FOUNDATIONS §6);
# this probe is not a loader, so it states the grid it is reasoning on instead.
DT_SEC = 0.1

# `tube` widens every onset to 2*kmin+1 frames before the mean over cells, where kmin
# is read from a fitted centre width. Fitted widths seen so far are ~4-7 samples
# (src/bugarach/learn/nets/tube.py), so 4 samples -> 9 frames is the middle of the
# observed range. It is a stated assumption, not a measurement.
WIDEN_FRAMES = 9

# One chance frame per hour of recording. A budget, chosen to be stated rather than
# argued: every number below scales with it and the ORDERING does not.
FA_PER_HOUR = 1.0


def binom_sf(k: int, n: int, p: float) -> float:
    """P(X >= k) for X ~ Binomial(n, p), summed exactly in log space.

    scipy is a dependency of this package, but its binomial survival function goes
    through a continued-fraction incomplete beta whose accuracy in the far tail is
    not what this probe needs — the quantities here reach 1e-169. An exact sum over
    at most 1050 terms costs nothing and is checkable by hand.
    """
    if k <= 0:
        return 1.0
    if k > n:
        return 0.0
    total = 0.0
    for i in range(int(k), n + 1):
        logp = (math.lgamma(n + 1) - math.lgamma(i + 1) - math.lgamma(n - i + 1)
                + i * math.log(p) + (n - i) * math.log1p(-p))
        total += math.exp(logp)
    return total


def floor_k(n: int, p: float, alpha: float) -> int:
    """Smallest co-active count whose chance probability per frame is <= alpha."""
    k = 1
    while k <= n and binom_sf(k, n, p) > alpha:
        k += 1
    return k


def _median(values):
    vals = sorted(v for v in values
                  if v is not None and not (isinstance(v, float) and math.isnan(v)))
    if not vals:
        return float("nan")
    mid = len(vals) // 2
    return float(vals[mid] if len(vals) % 2 else 0.5 * (vals[mid - 1] + vals[mid]))


def corpus(path: Path, label: str, short: str) -> dict:
    """Field size, per-cell rate and participation, read off a committed assessment."""
    rows = json.loads(path.read_text())["rows"]
    sizes = sorted(r["n_roi"] for r in rows)
    rate = _median(r.get("roi_rate_med") for r in rows)
    return {
        "label": label,
        "short": short,
        "source": str(path.relative_to(REPO)),
        "n_rows": len(rows),
        "n_roi_min": sizes[0],
        "n_roi_p25": sizes[len(sizes) // 4],
        "n_roi_median": sizes[len(sizes) // 2],
        "n_roi_p75": sizes[(3 * len(sizes)) // 4],
        "n_roi_max": sizes[-1],
        "roi_rate_med_hz": rate,
        "participants_med": _median(r.get("part_n_obs") for r in rows),
        "p_frame": rate * DT_SEC * WIDEN_FRAMES,
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    # default=None, never required — a deliverable's destination falls back to the
    # darkroom (sapper SAP006).
    ap.add_argument("--out", default=None, help="where the JSON goes (default: darkroom)")
    ap.add_argument("--also", default=None, help="a second copy, usually the repo")
    ap.add_argument("--fa-per-hour", type=float, default=FA_PER_HOUR)
    args = ap.parse_args()

    alpha = args.fa_per_hour / (3600.0 / DT_SEC)

    corpora = [
        corpus(REPO / "docs/learned/assessment_real.json", "this lab", "this lab"),
        corpus(REPO / "docs/learned/assessment_cossart.json",
               "Cossart / DANDI:000219", "Cossart"),
    ]

    # The field sizes to report the floor at: the two corpora's own extremes, the
    # sizes Tony named, and enough in between to see the shape.
    grid = [9, 13, 20, 32, 50, 62, 117, 250, 566, 1050]
    curve = [9, 11, 13, 16, 20, 25, 32, 40, 50, 62, 80, 100, 117, 150, 200,
             250, 320, 400, 500, 566, 700, 850, 1050]

    floors = []
    for c in corpora:
        p = c["p_frame"]
        floors.append({
            "corpus": c["label"],
            "short": c["short"],
            "p_frame": p,
            "by_n_roi": [{"n_roi": n,
                          "k_floor_cells": floor_k(n, p, alpha),
                          "k_floor_fraction": floor_k(n, p, alpha) / n}
                         for n in grid],
            "curve": [{"n_roi": n, "k_floor_cells": floor_k(n, p, alpha)}
                      for n in curve],
        })

    # A threshold set on a 32-cell field, carried elsewhere in each of three units.
    carried = []
    for c in corpora:
        p, n0 = c["p_frame"], 32
        k0 = floor_k(n0, p, alpha)
        rows = []
        for n in grid:
            # as a COUNT: same k everywhere
            fa_count = binom_sf(k0, n, p)
            # as a FRACTION of the field: k scales with n
            k_frac = math.ceil(k0 / n0 * n)
            fa_frac = binom_sf(k_frac, n, p)
            # as a STANDARDIZED EXCESS: the count that holds the tail probability
            # fixed. This is the pivot, so its false-alarm rate is alpha by
            # construction; it is in the table to show what the other two are missing.
            k_piv = floor_k(n, p, alpha)
            rows.append({
                "n_roi": n,
                "count_rule_k": k0, "count_rule_fa_per_frame": fa_count,
                "count_rule_fa_ratio": fa_count / alpha,
                "fraction_rule_k": k_frac, "fraction_rule_fa_per_frame": fa_frac,
                "fraction_rule_fa_ratio": fa_frac / alpha,
                "pivot_rule_k": k_piv, "pivot_rule_fa_ratio": 1.0,
            })
        carried.append({"corpus": c["label"], "calibrated_at_n_roi": n0,
                        "calibrated_k": k0, "by_n_roi": rows})

    # The scalar `tube` reads, at background and at a typical event.
    contrast = []
    for c in corpora:
        n, k = c["n_roi_median"], c["participants_med"]
        bg, ev = c["p_frame"], k / n
        contrast.append({
            "corpus": c["label"], "n_roi_median": n, "participants_med": k,
            "bright_background": bg, "bright_at_event": ev,
            "contrast_ratio": ev / bg if bg else float("inf"),
        })

    result = {
        "produced_by": "tools/probe_field_size.py",
        "assumptions": {
            "dt_sec": DT_SEC,
            "widen_frames": WIDEN_FRAMES,
            "false_alarms_per_hour": args.fa_per_hour,
            "alpha_per_frame": alpha,
            "null": "independent cells, one homogeneous per-cell rate per corpus",
        },
        "corpora": corpora,
        "detection_floor": floors,
        "threshold_carried_from_32_cells": carried,
        "tube_input_contrast": contrast,
    }

    out_dir = args.out
    if out_dir is None:
        try:
            from bugarach.paths import darkroom
            out_dir = str(darkroom())
        except Exception:                                   # pragma: no cover
            out_dir = str(REPO / "docs" / "learned")
    written = []
    for d in [out_dir] + ([args.also] if args.also else []):
        Path(d).mkdir(parents=True, exist_ok=True)
        target = Path(d) / "field_size.json"
        target.write_text(json.dumps(result, indent=1, sort_keys=True) + "\n")
        written.append(str(target))
    for w in written:
        print(w)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
