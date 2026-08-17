#!/usr/bin/env python3
"""Turn the corpus assessment into one generator spec, and say what it assumed.

    python tools/derive_spec.py --assessment docs/learned/assessment_real.json \
        --out docs/learned --k 3

The bridge in the per-lab loop: real recordings were measured without a detector,
and this turns that measurement into settings a simulator can run. Everything it
cannot ground it says so about, in `notes`, which travel with the spec.

**Which K is a human's call and this does not make it.** `assess.py` reports a
scan because K changes what counts as one event, and
`docs/todo/2026-08-16-assessment-needs-a-human-in-the-loop.md` says a human signs
off before an assessment parameterizes anything shipped. `--k` is required to be
passed explicitly for that reason; the scan is written into the spec beside the
choice so the reader sees what was not chosen.

**The background gets its measured shape and burstiness.** `bench.BENCH_RECORDING`
still runs a flat field, which the tree documents as easier than real data — real
recordings leave roughly a third of ROIs with no events in a baseline window
against a fiftieth here. Both fitted models are already in the tree
(`MEASURED_RATE_SHAPE`, `MEASURED_BURST_SHAPE`) and this turns them on, because a
detector calibrated on a flat field is calibrated for a recording nobody has.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np


def build(assessment: dict, k: int, *, events_per_level: int = 5,
          n_levels: int = 3) -> dict:
    from bugarach.adapt import generator_params
    from bugarach.assess import Assessment
    from bugarach.bench import (BENCH_RECORDING, MEASURED_BURST_BINS,
                                MEASURED_BURST_SHAPE, MEASURED_RATE_SHAPE)

    by_k = assessment["by_k"]
    if str(k) not in by_k:
        raise SystemExit(f"K={k} not in the scan ({sorted(by_k)})")
    v = by_k[str(k)]

    def med(field):
        m = v[field]["median"]
        return float("nan") if m is None else float(m)

    rows = [r for r in assessment["rows"] if r["K"] == k]
    n_roi = int(round(assessment["n_roi"]["median"]))
    win = float(np.median([r["window_sec"] for r in rows]))
    # Per-ROI rate, derived from the POPULATION event rate over the window
    # divided by the ROI count — the same construction the tree's own measured
    # regime endpoints came from.
    #
    # Not `roi_rate_med`. The median ROI's rate on this corpus is 0.00083 Hz with
    # an interquartile range starting at zero: in 38% of slices the median ROI
    # fires not once in baseline, which is FOUNDATIONS §9's "roughly 35% with no
    # events in a baseline window" reproduced on a store it was not measured on.
    # A median over a population that is a third silent is a statement about the
    # silence, not about the rate, and feeding it to the generator would build a
    # background an order of magnitude below anything recorded.
    rates = np.array([r["ev_rate_permin"] / 60.0 / max(r["n_roi"], 1)
                      for r in rows if np.isfinite(r["ev_rate_permin"])])
    rates = rates[np.isfinite(rates) & (rates > 0)]
    if rates.size == 0:
        raise SystemExit("no usable per-ROI rate in the assessment")
    roi_rate = float(np.median(rates))
    rate_iqr = [float(np.percentile(rates, 25)), float(np.percentile(rates, 75))]
    frac_median_silent = float(np.mean([r["roi_rate_med"] == 0 for r in rows]))

    a = Assessment(
        min_rois=k, meets_floor=True, win_dur=win, n_roi=n_roi,
        n_events_win=0,
        roi_rate_med=roi_rate, roi_rate_mean=roi_rate,
        part_n_obs=med("part_n_obs"),
        jit_obs=med("jit_obs"), jit_null=med("jit_null"),
        jit_excess=med("jit_excess"),
        jit_defined=v["n_jit_defined"] > 0,
        span_med=med("span_med"),
        clusters_permin=med("clusters_permin"),
        coact_excess=med("coact_excess"),
    )
    gp = generator_params(a, n_levels=n_levels,
                          events_per_level=events_per_level)
    kwargs = dict(gp.kwargs)
    notes = list(gp.notes)
    notes.append(
        f"bg_rate_hz derived from the population event rate / ROI count: median "
        f"{roi_rate:.5f} Hz, IQR {rate_iqr[0]:.5f}-{rate_iqr[1]:.5f}. The tree's "
        f"own measured regime endpoints are 0.0038 and 0.0175, so this store "
        f"independently reproduces the interquartile band the bench was built on. "
        f"The MEDIAN ROI rate is not used: {frac_median_silent:.0%} of slices have "
        f"a median ROI with no events in baseline")

    # --- the background the bench does not have -------------------------------
    kwargs["bg_rate_shape"] = MEASURED_RATE_SHAPE
    kwargs["bg_burst_shape"] = MEASURED_BURST_SHAPE
    kwargs["bg_burst_bin_sec"] = MEASURED_BURST_BINS
    notes.append(
        f"bg_rate_shape={MEASURED_RATE_SHAPE} and bg_burst_shape="
        f"{MEASURED_BURST_SHAPE} at bins {MEASURED_BURST_BINS} turn on the "
        "fitted per-ROI heterogeneity and burstiness. The bench's flat field is "
        "documented in the tree as easier than real data; leaving it flat would "
        "calibrate every detector for a recording nobody has")

    # --- the negatives, carried over from the bench ---------------------------
    for key in ("hot_window", "hot_rate_hz", "ramp_sec", "n_distractors",
                "distractor_frac", "distractor_window"):
        if key in BENCH_RECORDING:
            kwargs[key] = BENCH_RECORDING[key]
    notes.append(
        "the promiscuity probe and the correlated-burst distractors are carried "
        "over from BENCH_RECORDING unchanged: they are deliberate negatives, not "
        "properties of the recordings, so the assessment has nothing to say "
        "about them and they must not be fitted away")

    return {
        "generator": kwargs,
        "sweep": gp.sweep,
        "notes": notes,
        "k_chosen": k,
        "k_scan": {kk: {f: by_k[kk][f]["median"]
                        for f in ("part_n_obs", "jit_obs", "jit_null",
                                  "clusters_permin")}
                   | {"n_jit_defined": by_k[kk]["n_jit_defined"],
                      "n_slices": by_k[kk]["n_slices"]}
                   for kk in sorted(by_k, key=int)},
        "roi_rate": {"median": roi_rate, "iqr": rate_iqr,
                     "frac_slices_median_roi_silent": frac_median_silent},
        "provenance": {
            "store": assessment["store"],
            "n_slices_assessed": assessment["n_slices_assessed"],
            "n_surrogates": assessment["n_surrogates"],
            "regions": "baseline only",
            "region_labels_seen": assessment["region_labels_seen"],
        },
    }


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--assessment", type=Path, required=True)
    p.add_argument("--out", type=Path, required=True)
    p.add_argument("--k", type=int, required=True,
                   help="which K from the scan — a human's choice, not a default")
    a = p.parse_args(argv)

    spec = build(json.loads(a.assessment.read_text()), a.k)
    a.out.mkdir(parents=True, exist_ok=True)
    f = a.out / "generator_spec.json"
    f.write_text(json.dumps(spec, indent=1, sort_keys=True))
    print(f"wrote {f}\n")
    for kk, vv in spec["generator"].items():
        print(f"  {kk} = {vv}")
    print("\nassumptions:")
    for n in spec["notes"]:
        print(f"  - {n}")
    if spec["sweep"]:
        print(f"\n⚠ NOT grounded, sweep these: {spec['sweep']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
