#!/usr/bin/env python3
"""Does the guard's gain concentrate where events crowd? Asked in the tail, with a control.

    python tools/probe_guard_in_the_tail.py --selftest
    python tools/probe_guard_in_the_tail.py --seeds 24

`docs/forks.md` §4a's instrument is the right one and it was pointed at a recording
that could not answer it. Its argument: a recall gain **flat across the
nearest-neighbour gap** is a threshold knob, and a gain **concentrated at small gaps**
is mutual-masking relief. It measured flat, on `CROWDED_RECORDING`, whose tightest gaps
sit at a **14 s floor** — so the bins where relief must be largest were barely there.

Two things have changed since.

* `docs/reviews/guard_prior_art_2026-08-26.md` established that **`compact`
  normalization cancels most of the relief**: an empty guard band raises the bar by
  `C / (C - guard)` at every bin, and removing that term made the occupied-anchor effect
  2.5x larger at a 5 s guard. §4a measured through that cancellation.
* Real recordings reach a crowding fraction of **0.57** with minimum gaps of **6 s**.
  :data:`bench.TAIL_RECORDING` is fitted to that and **populates the <10 s bin**, which
  is the bin §4a never had.

## The control, which is the whole reason this tool is not two paragraphs shorter

The tight bins start lower — recall 0.66 at <10 s against 0.82 at >60 s — so **any**
uniform loosening lifts them more in absolute terms. A tilt toward tight gaps is
therefore not evidence by itself; it is what headroom looks like.

So the guard is compared against a **no-guard run whose alpha is loosened until its
overall recall matches the guarded one**, chosen from a sweep rather than assumed.
Matching recall alone would still leave the two at different precisions, so the match
is reported with both. What is then read is `guard − control`, per bin:

* **flat at zero** — the tilt was headroom, and §4a's conclusion survives this recording.
* **positive and largest in the tightest bin** — mutual-masking relief, finally measured
  somewhere it can exist.

Alpha is otherwise held at the shipped 1e-4, because the question is the *shape* across
bins and re-picking alpha per configuration moves every bin together.

Everything is **paired**: same seeds, same recordings, so the spread reported is the
spread of the difference, and `agree` counts how many seeds individually show the same
sign. Eight seeds cannot support a p-value and none is offered.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

from bugarach.bench import (make_tail_recording, nearest_neighbour_gaps, run_detector)
from bugarach.score import score_stream

REGIME = "baseline_quiet"
TOL_SEC = 1.5
ALPHA = 1e-4                 # the shipped point; see the docstring on why it is fixed
CONTROL_GRID = (1e-3, 3e-3, 1e-2, 3e-2)
BINS = (0.0, 10.0, 20.0, 30.0, 60.0, np.inf)
CONFIGS = [(0.0, "compact", ALPHA, "no guard"),
           (5.0, "compact", ALPHA, "5s compact"),
           (5.0, "exposure", ALPHA, "5s exposure"),
           (20.0, "exposure", ALPHA, "20s exposure")]


def _label(lo, hi):
    return f"<{hi:.0f}s" if lo == 0 else (f">{lo:.0f}s" if np.isinf(hi)
                                          else f"{lo:.0f}-{hi:.0f}s")


LABELS = [_label(lo, hi) for lo, hi in zip(BINS[:-1], BINS[1:])]


def per_seed(seeds, guard, norm, alpha):
    """Per-bin recall, overall recall and precision, one row per seed."""
    rec, over, prec, planted = [], [], [], np.zeros(len(LABELS))
    for seed in seeds:
        sl, gt = make_tail_recording(REGIME, seed)
        det = run_detector("coact", sl, alpha=alpha, guard_sec=guard,
                           guard_norm=norm)
        sc = score_stream(gt, det, tol_sec=TOL_SEC)
        idx = np.digitize(nearest_neighbour_gaps(gt), BINS[1:-1], right=False)
        rec.append([sc.hits[idx == b].mean() if (idx == b).any() else np.nan
                    for b in range(len(LABELS))])
        planted += [int((idx == b).sum()) for b in range(len(LABELS))]
        over.append(sc.n_hit / sc.n_planted if sc.n_planted else np.nan)
        prec.append(sc.n_hit / sc.n_detected if sc.n_detected else np.nan)
    return dict(recall=np.array(rec, float), overall=np.array(over, float),
                precision=np.array(prec, float), planted=planted)


def _delta(a, b):
    """Paired difference, its spread across seeds, and how many seeds agree in sign."""
    d = a - b
    m = np.nanmean(d, axis=0)
    return dict(mean=m, sd=np.nanstd(d, axis=0, ddof=1),
                agree=[int(np.nansum(np.sign(d[:, i]) == np.sign(m[i])))
                       for i in range(d.shape[1])], n=d.shape[0])


def collect(seeds):
    runs = {label: per_seed(seeds, g, n, a) for g, n, a, label in CONFIGS}
    base = runs["no guard"]
    target = runs["20s exposure"]["overall"].mean()

    # the alpha-matched control: no guard, loosened until overall recall matches
    sweep = {}
    for alpha in CONTROL_GRID:
        sweep[alpha] = per_seed(seeds, 0.0, "compact", alpha)
    best = min(sweep, key=lambda a: abs(sweep[a]["overall"].mean() - target))
    control = sweep[best]

    return dict(runs=runs, base=base, control=control, control_alpha=best,
                control_sweep={a: dict(overall=float(v["overall"].mean()),
                                       precision=float(v["precision"].mean()))
                               for a, v in sweep.items()},
                residual=_delta(runs["20s exposure"]["recall"], control["recall"]),
                seeds=list(seeds))


def selftest(seeds=(1, 2)):
    """Can the alarm ring? With no guard neither branch is entered, so the two
    normalizations must return the same per-bin recall exactly."""
    a = per_seed(seeds, 0.0, "compact", ALPHA)
    b = per_seed(seeds, 0.0, "exposure", ALPHA)
    ok = np.array_equal(np.nan_to_num(a["recall"]), np.nan_to_num(b["recall"]))
    print(f"  guard 0, {len(seeds)} seeds: compact vs exposure per-bin recall "
          + ("identical — clean" if ok
             else "DIFFER — the tool is measuring itself"))
    return 0 if ok else 1


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--seeds", type=int, default=8)
    ap.add_argument("--json", type=Path, default=None)
    a = ap.parse_args(argv)

    if a.selftest:
        return selftest()

    seeds = tuple(range(1, a.seeds + 1))
    r = collect(seeds)
    base, ctrl = r["base"], r["control"]

    if a.json:
        def clean(o):
            if isinstance(o, np.ndarray):
                return o.tolist()
            if isinstance(o, dict):
                return {str(k): clean(v) for k, v in o.items()}
            if isinstance(o, (list, tuple)):
                return [clean(x) for x in o]
            return o
        a.json.write_text(json.dumps(clean(
            dict(labels=LABELS, seeds=list(seeds), alpha=ALPHA,
                 control_alpha=r["control_alpha"], control_sweep=r["control_sweep"],
                 planted=base["planted"],
                 recall={k: v["recall"] for k, v in r["runs"].items()},
                 control_recall=ctrl["recall"],
                 residual=r["residual"])), indent=1))

    print(f"TAIL_RECORDING, {len(seeds)} seeds, regime {REGIME!r}, tolerance {TOL_SEC} s")
    print("recall by each planted event's own nearest-neighbour gap — tightest first\n")
    hdr = f"  {'config':22s} " + " ".join(f"{l:>9s}" for l in LABELS) \
        + f" {'overall':>8s} {'precis':>7s}"
    print(hdr)
    print("  " + "-" * (len(hdr) - 2))
    print(f"  {'planted (n, pooled)':22s} "
          + " ".join(f"{int(n):9d}" for n in base["planted"]))
    for _, _, _, label in CONFIGS:
        v = r["runs"][label]
        print(f"  {label:22s} " + " ".join(f"{x:9.3f}" for x in np.nanmean(v['recall'], 0))
              + f" {np.nanmean(v['overall']):8.3f} {np.nanmean(v['precision']):7.3f}")
    ca = r["control_alpha"]
    print(f"  {f'no guard @ alpha {ca:.0e}':22s} "
          + " ".join(f"{x:9.3f}" for x in np.nanmean(ctrl['recall'], 0))
          + f" {np.nanmean(ctrl['overall']):8.3f} {np.nanmean(ctrl['precision']):7.3f}"
          + "   <- the control")

    print(f"\n  the control is picked from a sweep, matched on overall recall:")
    for alpha, v in r["control_sweep"].items():
        mark = "  <- matched" if alpha == ca else ""
        print(f"    alpha {alpha:8.0e}  recall {v['overall']:.3f}  "
              f"precision {v['precision']:.3f}{mark}")

    res = r["residual"]
    print(f"\n  GUARD MINUS CONTROL — paired, per bin, mean ± sd across seeds "
          f"(agree = seeds with the mean's sign, of {res['n']})")
    print(f"  {'':22s} " + " ".join(f"{l:>9s}" for l in LABELS))
    print(f"  {'20s exposure - ctrl':22s} "
          + " ".join(f"{m:+9.3f}" for m in res["mean"]))
    print(f"  {'sd':22s} " + " ".join(f"{s:9.3f}" for s in res["sd"]))
    print(f"  {'agree':22s} " + " ".join(f"{k:6d}/{res['n']:<2d}"
                                         for k in res["agree"]))

    print("\nREAD IT LIKE THIS")
    print("  The control has the same overall recall, so a uniform loosening is")
    print("  subtracted out and only a GAP-DEPENDENT component can survive.")
    print("  Flat at zero -> the tilt was headroom, and forks.md 4a survives here too.")
    print("  Positive and largest in <10s -> mutual-masking relief, in the one bin")
    print("  where events actually sit inside each other's reference window.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
