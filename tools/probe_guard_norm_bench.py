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

## Two axes, because the first version of this probe could not have found an effect

Tony asked whether the bench can show this at all. Twice over, it cannot, and the tree
says so about itself:

* **`BENCH_RECORDING` plants events 120 s apart** while CoactDetect's reference window
  spans ±30 s, so a second planted event can never enter the first one's context.
  `CROWDED_RECORDING`'s docstring puts it in terms: *"The failure mode every CFAR detector
  uses guard cells against ... is impossible by construction on the recording the
  detectors are scored on."* **Mutual masking cannot fire on `baseline_quiet` or
  `baseline_busy`**, so those two rows test the self-masking half alone. Only the
  `crowded` diagnostic — `min_sep_sec=14 s` — puts two planted events in one reference,
  and that recording is one *"nothing should be calibrated on."*
* **The field is flat.** Every ROI carries the same background rate. Adaptive
  thresholding exists for *heterogeneous* clutter; a flat field is the one place a
  CFAR-shaped detector has nothing to adapt to. `assess` fits a Gamma shape from real
  recordings — `MEASURED_RATE_SHAPE`, 0.275, which is strongly skewed — and
  `docs/learned/flat_vs_fitted.json` shows swapping the field **reorders the six**.

So the probe runs both fields. `flat` is the bench as shipped; `fitted` passes
`bg_rate_shape=MEASURED_RATE_SHAPE` through to the generator, the same seam
`tools/probe_flat_vs_fitted.py` uses. If the guard has a detection effect anywhere in
this tree, `crowded` × `fitted` is where it is.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

from bugarach.bench import (BENCH_RECORDING, CROWDED_RECORDING, CROWDING_GAP_SEC,
                            MEASURED_RATE_SHAPE, OPERATING_POINTS,
                            make_crowded_recording, make_recording,
                            nearest_neighbour_gaps, pool_scores, run_detector)
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
FIELDS = {"flat": {}, "fitted": {"bg_rate_shape": MEASURED_RATE_SHAPE}}


def _recording(regime, seed, field="flat"):
    """`crowded` is the diagnostic recording, not a regime — it is built by its own
    maker at the quiet endpoint (`bench.py` says so in terms), so it cannot go
    through ``evaluate`` and is scored here the same way by hand.

    ``field`` selects the background: flat as shipped, or the fitted Gamma shape
    `assess` measures off real recordings.
    """
    kw = FIELDS[field]
    if regime == "crowded":
        return make_crowded_recording("baseline_quiet", seed, **kw)
    return make_recording(regime, seed, **kw)


def crowding(regime, field="flat"):
    """Fraction of planted events with another inside their own reference window.

    This is the number that decides whether the guard's mutual-masking half can
    fire at all, and it is a property of the RECORDING, not of the detector.
    """
    frac = []
    for seed in SEEDS:
        _, gt = _recording(regime, seed, field)
        gaps = nearest_neighbour_gaps(gt)
        frac.append(float(np.mean(gaps < CROWDING_GAP_SEC)) if gaps.size else np.nan)
    return float(np.nanmean(frac))


def one(regime, alpha, guard, norm, field="flat"):
    """Pooled score, plus the per-seed F1s the spread is computed from."""
    per_seed, scores = [], []
    for seed in SEEDS:
        sl, gt = _recording(regime, seed, field)
        det = run_detector("coact", sl, alpha=alpha, guard_sec=guard, guard_norm=norm)
        sc = score_stream(gt, det, tol_sec=TOL_SEC)
        scores.append(sc)
        per_seed.append(pool_scores([sc], detector="coact", regime=regime,
                                    seeds=(seed,)).f1)
    pooled = pool_scores(scores, detector="coact", regime=regime, seeds=SEEDS)
    return pooled, np.asarray(per_seed, float)


def collect(fields=("flat", "fitted")):
    rows = []
    for field in fields:
        for regime in REGIMES:
            crowd = crowding(regime, field)
            for guard, norm, label in CONFIGS:
                for alpha in ALPHAS:
                    pooled, ps = one(regime, alpha, guard, norm, field)
                    rows.append(dict(
                        field=field, regime=regime, label=label, guard=guard,
                        norm=norm, alpha=alpha, crowded_frac=crowd,
                        f1=pooled.f1, precision=pooled.precision,
                        recall=pooled.recall,
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
    ap.add_argument("--flat-only", action="store_true",
                    help="skip the fitted field — halves the runtime and drops the "
                         "only condition where the guard's mechanism can fire")
    a = ap.parse_args(argv)

    if a.selftest:
        return selftest()

    rows = collect(("flat",) if a.flat_only else ("flat", "fitted"))
    if a.json:
        a.json.write_text(json.dumps(rows, indent=1))

    print(f"coact, {len(SEEDS)} seeds, match tolerance {TOL_SEC} s, F1 pooled over seeds")
    print(f"'crowded frac' = planted events with another inside their own "
          f"+-{CROWDING_GAP_SEC:.0f} s reference window.\n"
          f"Where it is 0, the guard's MUTUAL-masking half cannot fire at all and the "
          f"row tests self-masking alone.\n")
    for field in sorted({r["field"] for r in rows}):
        for regime in REGIMES:
            sub = [r for r in rows if r["field"] == field and r["regime"] == regime]
            print(f"{regime} · {field} field · crowded frac "
                  f"{sub[0]['crowded_frac']:.2f}")
            print(f"  {'config':14s} " + " ".join(f"{x:>8.0e}" for x in ALPHAS)
                  + f" | {'best F1':>8s} {'at alpha':>9s} {'seed sd':>8s} "
                    f"{'P':>6s} {'R':>6s}")
            for _, _, label in CONFIGS:
                rs = [r for r in sub if r["label"] == label]
                f1s = [r["f1"] for r in rs]
                i = int(np.nanargmax(f1s))
                print(f"  {label:14s} " + " ".join(f"{v:8.3f}" for v in f1s)
                      + f" | {rs[i]['f1']:8.3f} {rs[i]['alpha']:9.0e} "
                        f"{rs[i]['seed_sd']:8.3f} {rs[i]['precision']:6.3f} "
                        f"{rs[i]['recall']:6.3f}")
            print()

    print("READ IT LIKE THIS")
    print("  Look at 'crowded frac' BEFORE the F1s. A row at 0.00 cannot show the")
    print("  guard's main mechanism no matter what the numbers do, because no planted")
    print("  event is ever in another's reference window.")
    print("  Compare each row's BEST F1, not its column at a shared alpha: exposure")
    print("  lowers a bar compact raised, so a frozen alpha scores two different")
    print("  operating points and calls it a detector comparison.")
    print("  Then compare the gaps against the seed sd in the same row. A gap smaller")
    print("  than that is not a result, whichever way it points.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
