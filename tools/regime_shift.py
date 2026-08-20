#!/usr/bin/env python3
"""Train in one background regime, deploy in the other. Report what it costs.

    python tools/regime_shift.py --out docs/learned

`simulation_plan.md` §8 calls this the single highest-value item on that page,
and says why: **the precision-collapse figure is a test that was drawn as a
picture.** Upstream tuned detectors on a dense benchmark, deployed them on a
sparse one, and precision fell from 90 to 45, 74 to 10, 58 to 10. That was a
figure in a deck. Here it is an assertion.

The two regimes are both **untreated** and both measured: 0.0052 Hz and 0.0190
Hz per ROI, a 3.7-fold change real slices show among themselves. No drug is
involved, which matters, because a treatment regime would make the test a
question about pharmacology instead of about generalization.

⚠ **Those endpoints are p25/p75 of the SLICE-POPULATION rate, divided by a
derived ROI count.** As per-ROI rates they sit at roughly the **60th and 83rd
percentiles** — a 23-percentile band, not an interquartile spread. See
`docs/reviews/roi_rate_distribution_2026-08-15.md`. This is the concrete reason
a null result on this axis is weak: the axis is provably narrower than the
sentence that used to describe it.

**The threshold is chosen on the training regime and carried over unchanged.**
Re-picking it on the target is the whole failure being tested for: it hides the
collapse by re-tuning at the moment of deployment, which is exactly what a lab
deploying a model cannot do.

What the test is *for*: the centre-surround model claims rate invariance is
structural rather than learned — the surround subtracts the local level, so a
uniform change in background cancels. That claim predicts it should barely move
across this shift while a model that had to discover the invariant should. This
is the experiment that can falsify it.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REGIMES = ("baseline_quiet", "baseline_busy")
ARCHES = ("tube", "trace", "tiny")
LR = {"tube": 1e-2, "trace": 1e-3, "tiny": 1e-3}
BENCH_SEEDS = (1, 2, 3)
# Held out from BENCH_SEEDS, so the six's knob is chosen off the recordings it is
# then graded on — matching what `learn.train.pick_threshold` already does for
# the learned models.
CALIBRATION_SEEDS = (901, 902, 903, 904)


def _row(r) -> dict:
    return dict(f1=r.f1, recall=r.recall, precision=r.precision,
                n_detected=r.n_detected, n_scored=r.n_scored, hot_fa=r.hot_fa,
                by_frac={f"{f:g}": r.recall_at(f) for f in sorted(r.by_frac)})


def _score(tr, regime, make):
    """Score a trained model, pooled by the bench's own rule.

    This used to compute `n_hit / n_detected` by hand while the six went through
    `evaluate` and got the promiscuity probe excluded from their denominator —
    so the two halves of the comparison this file exists to make were on
    different metrics.
    """
    from bugarach.bench import pool_scores
    from bugarach.score import score_stream
    scores = []
    for s in BENCH_SEEDS:
        sl, gt = make(regime, seed=s)
        d, _ = tr.predict(sl)
        scores.append(score_stream(gt, d))
    return _row(pool_scores(scores, detector="learned", regime=regime,
                            seeds=BENCH_SEEDS))


def load_spec(path: Path) -> tuple[dict, dict]:
    """The fitted generator settings, minus the one this test varies.

    ``bg_rate_hz`` IS the difficulty axis here, so the spec's fitted value (the
    median, 0.0097 Hz) is dropped and ``REGIMES`` supplies p25 and p75 instead.
    Everything else the fit measured — the heterogeneous background shape, the
    burst structure, participation, jitter — is carried, because the question is
    whether a rate change breaks a detector on the background real recordings
    actually have, not on a flat one.
    """
    doc = json.loads(path.read_text())
    gen = {k: v for k, v in doc["generator"].items() if k != "bg_rate_hz"}
    prov = {"spec": str(path), "k_chosen": doc.get("k_chosen"),
            "provenance": doc.get("provenance"),
            "dropped": {"bg_rate_hz": doc["generator"].get("bg_rate_hz")}}
    return gen, prov


def run(gen: dict | None = None) -> dict:
    from bugarach.bench import (DETECTORS, EdgeOfRange, OPERATING_POINTS,
                                evaluate, make_recording, pick_operating_point,
                                sweep)
    from bugarach.learn.train import train

    out: dict = {"learned": {}, "six": {}, "six_transfer": {}}
    gen = gen or {}

    # The six at their shipped operating points, evaluated in each regime.
    for d in DETECTORS:
        out["six"][d] = {}
        for r in REGIMES:
            out["six"][d][r] = _row(evaluate(d, r, seeds=BENCH_SEEDS, gen=gen))

    # --- the six under the SAME experiment the learned models get -------------
    # Evaluating a fixed detector twice is not a transfer test: a detector with
    # no fitted state cannot exhibit a transfer collapse, so its flatness is no
    # evidence that the axis is mild. The matched test is to calibrate on one
    # regime and carry the knob over unchanged — which is what the learned models
    # do with their threshold, and what the historical failure this file cites
    # actually was.
    #
    # **Calibrated on held-out seeds, scored on the bench seeds.** The learned
    # models pick their threshold on four recordings drawn from a disjoint seed
    # block and are never scored on them (`learn.train.pick_threshold`). Choosing
    # the six's knob on BENCH_SEEDS and then reporting their "at home" number on
    # those same three recordings would give one side of this comparison a knob
    # fitted to the exact recordings it is graded on, and the other side a
    # genuinely held-out one — which is not the same experiment, whichever way
    # the bias happened to run.
    for d in DETECTORS:
        out["six_transfer"][d] = {}
        for train_on in REGIMES:
            try:
                best = pick_operating_point(
                    sweep(d, train_on, seeds=CALIBRATION_SEEDS, gen=gen))
            except EdgeOfRange as e:
                out["six_transfer"][d][train_on] = {"edge_of_range": str(e)}
                continue
            knob = OPERATING_POINTS[d].knob
            cell = {"knob": knob, "knob_value": best.knob_value,
                    "calibration_seeds": list(CALIBRATION_SEEDS)}
            for test_on in REGIMES:
                # knob NOT re-picked on the target — the point of the test
                cell[test_on] = _row(evaluate(d, test_on, seeds=BENCH_SEEDS,
                                              gen=gen, **{knob: best.knob_value}))
            out["six_transfer"][d][train_on] = cell

    for name in ARCHES:
        out["learned"][name] = {}
        for train_on in REGIMES:
            mk = lambda seed, _r=train_on: make_recording(_r, seed=seed, **gen)  # noqa: E731
            tr = train(name, mk, n_train=10, steps=900, crop=4096, batch=3,
                       lr=LR[name])
            cell = {"threshold": float(tr.threshold),
                    "params": tr.n_params,
                    "train_seconds": tr.train_seconds}
            for test_on in REGIMES:
                # NOTE: threshold NOT re-picked. Carried from the training regime.
                cell[test_on] = _score(tr, test_on,
                                       lambda r, seed: make_recording(r, seed=seed, **gen))
            if hasattr(tr.model, "log_center"):
                import math
                cell["centres"] = [math.exp(v)
                                   for v in tr.model.log_center.tolist()]
            out["learned"][name][train_on] = cell
    return out


def report(res) -> str:
    lines = []
    q, b = REGIMES
    lines.append("REGIME SHIFT — threshold carried over, never re-picked")
    # Read off bench.REGIMES rather than transcribed: these were literals until
    # 2026-08-20, when the axis was re-derived from the export folder.
    from bugarach.bench import REGIMES as _R
    lines.append(f"  quiet = {q} ({_R[q]['bg_rate_hz']:g} Hz/ROI)   "
                 f"busy = {b} ({_R[b]['bg_rate_hz']:g} Hz/ROI)")
    lines.append("")
    lines.append(f"{'model':>8} {'trained':>6} | {'F1 same':>8} {'F1 shift':>9}"
                 f" {'dF1':>7} | {'prec same':>10} {'prec shift':>11} {'dprec':>7}")
    for name, byreg in res["learned"].items():
        for train_on, cell in byreg.items():
            other = b if train_on == q else q
            same, shift = cell[train_on], cell[other]
            lines.append(
                f"{name:>8} {('quiet' if train_on == q else 'busy'):>6} | "
                f"{same['f1']:8.2f} {shift['f1']:9.2f} "
                f"{shift['f1'] - same['f1']:+7.2f} | "
                f"{same['precision']:10.2f} {shift['precision']:11.2f} "
                f"{shift['precision'] - same['precision']:+7.2f}")
    lines.append("")
    lines.append("the six, at their fixed operating points (calibrated once, not here)")
    lines.append("  -- NOT a transfer test: nothing is carried over, so nothing can collapse")
    for d, byreg in res["six"].items():
        lines.append(f"{d:>8} {'—':>6} | {byreg[q]['f1']:8.2f} {byreg[b]['f1']:9.2f} "
                     f"{byreg[b]['f1'] - byreg[q]['f1']:+7.2f} | "
                     f"{byreg[q]['precision']:10.2f} {byreg[b]['precision']:11.2f} "
                     f"{byreg[b]['precision'] - byreg[q]['precision']:+7.2f}")
    lines.append("")
    lines.append("the six, CALIBRATED on one regime and carried over — the matched test")
    for d, byreg in res.get("six_transfer", {}).items():
        for train_on, cell in byreg.items():
            if "edge_of_range" in cell:
                lines.append(f"{d:>8} {('quiet' if train_on == q else 'busy'):>6} |"
                             f"  grid edge — no operating point")
                continue
            other = b if train_on == q else q
            same, shift = cell[train_on], cell[other]
            lines.append(
                f"{d:>8} {('quiet' if train_on == q else 'busy'):>6} | "
                f"{same['f1']:8.2f} {shift['f1']:9.2f} "
                f"{shift['f1'] - same['f1']:+7.2f} | "
                f"{same['precision']:10.2f} {shift['precision']:11.2f} "
                f"{shift['precision'] - same['precision']:+7.2f}"
                f"   @{cell['knob']}={cell['knob_value']:g}")
    return "\n".join(lines)


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--out", type=Path, default=None)
    p.add_argument("--spec", type=Path, default=None,
                   help="generator_spec.json — run the shift on the background "
                        "fitted from real recordings instead of the bench's flat "
                        "one. Without it, the corpus is the flat bench and the "
                        "result does not sit on the same footing as the bake-off.")
    a = p.parse_args(argv)
    gen, prov = load_spec(a.spec) if a.spec else ({}, {"spec": None})
    res = run(gen)
    res["corpus"] = prov
    print(report(res))
    if a.out:
        a.out.mkdir(parents=True, exist_ok=True)
        f = a.out / "regime_shift.json"
        f.write_text(json.dumps(res, indent=1, sort_keys=True))
        print(f"\nwrote {f}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
