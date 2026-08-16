#!/usr/bin/env python3
"""Train in one background regime, deploy in the other. Report what it costs.

    python tools/regime_shift.py --out docs/learned

`simulation_plan.md` §8 calls this the single highest-value item on that page,
and says why: **the precision-collapse figure is a test that was drawn as a
picture.** Upstream tuned detectors on a dense benchmark, deployed them on a
sparse one, and precision fell from 90 to 45, 74 to 10, 58 to 10. That was a
figure in a deck. Here it is an assertion.

The two regimes are both **untreated** and both measured: the interquartile
spread of per-ROI rate across baseline slices, 0.0038 Hz at p25 and 0.0175 Hz at
p75 — a 4.6-fold change that real slices show among themselves. No drug is
involved, which matters, because a treatment regime would make the test a
question about pharmacology instead of about generalization.

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


def _score(tr, regime, make):
    from bugarach.score import score_stream
    hit = det = pl = 0
    for s in BENCH_SEEDS:
        sl, gt = make(regime, seed=s)
        d, _ = tr.predict(sl)
        sc = score_stream(gt, d)
        hit += sc.n_hit
        det += sc.n_detected
        pl += sc.n_planted
    rec = hit / pl if pl else float("nan")
    pre = hit / det if det else 0.0
    f1 = 0.0 if (rec + pre) == 0 else 2 * rec * pre / (rec + pre)
    return dict(f1=f1, recall=rec, precision=pre, n_detected=det)


def run() -> dict:
    from bugarach.bench import DETECTORS, evaluate, make_recording
    from bugarach.learn.train import train

    out: dict = {"learned": {}, "six": {}}

    # The six do not train, so they only need evaluating in each regime — but
    # their operating points WERE calibrated, in one regime, which is the same
    # exposure a trained model has.
    for d in DETECTORS:
        out["six"][d] = {}
        for r in REGIMES:
            e = evaluate(d, r, seeds=BENCH_SEEDS)
            out["six"][d][r] = dict(f1=e.f1, recall=e.recall,
                                    precision=e.precision,
                                    n_detected=e.n_detected)

    for name in ARCHES:
        out["learned"][name] = {}
        for train_on in REGIMES:
            mk = lambda seed, _r=train_on: make_recording(_r, seed=seed)  # noqa: E731
            tr = train(name, mk, n_train=10, steps=900, crop=4096, batch=3,
                       lr=LR[name])
            cell = {"threshold": float(tr.threshold),
                    "params": tr.n_params,
                    "train_seconds": tr.train_seconds}
            for test_on in REGIMES:
                # NOTE: threshold NOT re-picked. Carried from the training regime.
                cell[test_on] = _score(tr, test_on, make_recording)
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
    lines.append(f"  quiet = {q} (0.0038 Hz/ROI)   busy = {b} (0.0175 Hz/ROI)")
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
    for d, byreg in res["six"].items():
        lines.append(f"{d:>8} {'—':>6} | {byreg[q]['f1']:8.2f} {byreg[b]['f1']:9.2f} "
                     f"{byreg[b]['f1'] - byreg[q]['f1']:+7.2f} | "
                     f"{byreg[q]['precision']:10.2f} {byreg[b]['precision']:11.2f} "
                     f"{byreg[b]['precision'] - byreg[q]['precision']:+7.2f}")
    return "\n".join(lines)


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--out", type=Path, default=None)
    a = p.parse_args(argv)
    res = run()
    print(report(res))
    if a.out:
        a.out.mkdir(parents=True, exist_ok=True)
        f = a.out / "regime_shift.json"
        f.write_text(json.dumps(res, indent=1, sort_keys=True))
        print(f"\nwrote {f}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
