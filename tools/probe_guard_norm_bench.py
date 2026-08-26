#!/usr/bin/env python3
"""Does the fixed guard normalization actually detect better? Swept, not asserted.

    python tools/probe_guard_norm_bench.py --selftest
    python tools/probe_guard_norm_bench.py

`docs/reviews/guard_prior_art_2026-08-26.md` proved the guard's empty-stratum rise is
an exposure factor and that removing it makes the masking relief 2.5x larger at a 5 s
guard. It then said, on its own face, that ``guard_norm="exposure"`` **had never been
benched** — no F1, no precision, no recall. This is that measurement.

**Comparing at fixed alpha would rig it.** `exposure` lowers the bar where `compact`
raised it, so at a frozen alpha it buys recall and pays precision — which is what any
threshold change does and is not evidence about a detector. The question a detector has
to answer is whether the whole operating curve moves out: sweep the knob the operating
point is chosen with (`bench.OPERATING_POINTS["coact"].grid`, alpha 1e-2 ... 1e-7) and
compare the best each configuration can reach.

The seed spread is reported beside every number, because the comparison lives or dies on
it: `docs/learned` records coact's sd(dF1) at **0.078** over 12 seeds, so a difference of
0.02 in F1 is not a difference.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

from bugarach.bench import (OPERATING_POINTS, make_crowded_recording,
                            make_recording, pool_scores, run_detector)
from bugarach.score import score_stream

SEEDS = tuple(range(1, 13))
ALPHAS = OPERATING_POINTS["coact"].grid
TOL_SEC = 1.5
CONFIGS = [(0.0, "compact", "no guard"),
           (5.0, "compact", "5s compact"),
           (5.0, "exposure", "5s exposure"),
           (20.0, "compact", "20s compact"),
           (20.0, "exposure", "20s exposure")]
REGIMES = ("baseline_quiet", "baseline_busy", "crowded")


def _recording(regime, seed):
    """`crowded` is the diagnostic recording, not a regime — it is built by its own
    maker at the quiet endpoint (`bench.py` says so in terms), so it cannot go
    through ``evaluate`` and is scored here the same way by hand."""
    if regime == "crowded":
        return make_crowded_recording("baseline_quiet", seed)
    return make_recording(regime, seed)


def one(regime, alpha, guard, norm):
    """Pooled score, plus the per-seed F1s the spread is computed from."""
    per_seed, scores = [], []
    for seed in SEEDS:
        sl, gt = _recording(regime, seed)
        det = run_detector("coact", sl, alpha=alpha, guard_sec=guard, guard_norm=norm)
        sc = score_stream(gt, det, tol_sec=TOL_SEC)
        scores.append(sc)
        per_seed.append(pool_scores([sc], detector="coact", regime=regime,
                                    seeds=(seed,)).f1)
    pooled = pool_scores(scores, detector="coact", regime=regime, seeds=SEEDS)
    return pooled, np.asarray(per_seed, float)


def collect():
    rows = []
    for regime in REGIMES:
        for guard, norm, label in CONFIGS:
            for alpha in ALPHAS:
                pooled, ps = one(regime, alpha, guard, norm)
                rows.append(dict(
                    regime=regime, label=label, guard=guard, norm=norm, alpha=alpha,
                    f1=pooled.f1, precision=pooled.precision, recall=pooled.recall,
                    seed_sd=float(np.nanstd(ps, ddof=1)),
                    n_hit=pooled.n_hit, n_detected=pooled.n_detected,
                    n_planted=pooled.n_planted))
    return rows


def selftest():
    """Can the alarm ring? With no guard neither branch is entered, so the two
    normalizations must produce the same detections down to the count."""
    bad = 0
    for regime in ("baseline_quiet", "crowded"):
        a, _ = one(regime, 1e-4, 0.0, "compact")
        b, _ = one(regime, 1e-4, 0.0, "exposure")
        same = (a.n_hit, a.n_detected, a.n_planted) == (b.n_hit, b.n_detected,
                                                        b.n_planted)
        bad += 0 if same else 1
        print(f"  guard 0, {regime:15s} compact {a.n_hit}/{a.n_detected} vs "
              f"exposure {b.n_hit}/{b.n_detected}   "
              + ("clean" if same else "NOT IDENTICAL — the tool is measuring itself"))
    return 1 if bad else 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--selftest", action="store_true",
                   help="guard 0 under both normalizations; detections must be identical")
    ap.add_argument("--json", type=Path, default=None, help="also dump the rows")
    a = ap.parse_args(argv)

    if a.selftest:
        return selftest()

    rows = collect()
    if a.json:
        a.json.write_text(json.dumps(rows, indent=1))

    print(f"coact, {len(SEEDS)} seeds, match tolerance {TOL_SEC} s, F1 pooled over seeds\n")
    for regime in REGIMES:
        print(f"{regime}")
        print(f"  {'config':14s} " + " ".join(f"{x:>8.0e}" for x in ALPHAS)
              + f" | {'best F1':>8s} {'at alpha':>9s} {'seed sd':>8s} {'P':>6s} {'R':>6s}")
        base = None
        for _, _, label in CONFIGS:
            rs = [r for r in rows if r["regime"] == regime and r["label"] == label]
            f1s = [r["f1"] for r in rs]
            i = int(np.nanargmax(f1s))
            if base is None:
                base = rs[i]
            print(f"  {label:14s} " + " ".join(f"{v:8.3f}" for v in f1s)
                  + f" | {rs[i]['f1']:8.3f} {rs[i]['alpha']:9.0e} "
                    f"{rs[i]['seed_sd']:8.3f} {rs[i]['precision']:6.3f} "
                    f"{rs[i]['recall']:6.3f}")
        print()

    print("READ IT LIKE THIS")
    print("  Compare each row's BEST F1, not its column at a shared alpha: exposure")
    print("  lowers a bar compact raised, so a frozen alpha scores two different")
    print("  operating points and calls it a detector comparison.")
    print("  Then compare the gaps against the seed sd in the same row. A gap smaller")
    print("  than that is not a result, whichever way it points.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
