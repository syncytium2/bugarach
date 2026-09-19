"""Compare two ``fair_bakeoff.py`` results on the same folds, fold by fold.

    python tools/compare_bakeoff_runs.py <candidate/bakeoff.json> <reference/bakeoff.json> \
        [--learned-tol 0.02]

Written for Gate 1 of ``HANDOFF-workstation-tuning.md``: does another machine
reproduce the Mac's bake-off? The hand-written detectors are numpy with fixed
seeds, so they must match **exactly** on every per-fold field that is a result;
wall times are skipped. Learned models are compared on F1 within a tolerance, with
their threshold and training time beside it. Prints ``ALL MATCH`` or ``MISMATCH``
last. Record: ``docs/learned/tuned_vs_coact/gate1/README.md``.
"""
import argparse
import json
import math

TIMING = {"calibrate_sec", "detect_sec", "detect_x_realtime", "train_sec"}


def same(a, b):
    if isinstance(a, float) and isinstance(b, float) and math.isnan(a) and math.isnan(b):
        return True
    return a == b


def diff_fields(m, r):
    out = []
    for k in sorted(set(m) | set(r)):
        if k in TIMING:
            continue
        if not same(m.get(k), r.get(k)):
            out.append((k, m.get(k), r.get(k)))
    return out


def main():
    p = argparse.ArgumentParser()
    p.add_argument("mine")
    p.add_argument("mac")
    p.add_argument("--learned-tol", type=float, default=0.02)
    a = p.parse_args()
    mine, mac = json.load(open(a.mine)), json.load(open(a.mac))
    assert mine["seeds"] == mac["seeds"], "different recording seeds"
    ok = True

    for det, v in mine.get("hand_written", {}).items():
        ref = mac["hand_written"].get(det)
        if ref is None:
            print(f"{det:18} no Mac row")
            continue
        for fm, fr in zip(v["per_fold"], ref["per_fold"]):
            d = diff_fields(fm, fr)
            tag = "EXACT" if not d else "DIFFERS"
            ok &= not d
            print(f"{det:18} fold {fm['fold']}: {tag}  F1 {fm['f1']:.6f} vs {fr['f1']:.6f}"
                  f"  knob {fm['knob_value']:g} vs {fr['knob_value']:g}"
                  f"  cal {fm['calibrate_sec']:.1f}s vs {fr['calibrate_sec']:.1f}s")
            for k, x, y in d:
                print(f"{'':22}{k}: {x!r} vs {y!r}")

    for name, v in mine.get("learned", {}).items():
        ref = mac["learned"].get(name)
        if ref is None:
            print(f"{name:18} no Mac row")
            continue
        worst = 0.0
        for fm, fr in zip(v["per_fold"], ref["per_fold"]):
            dF = fm["f1"] - fr["f1"]
            worst = max(worst, abs(dF))
            d = [x for x in diff_fields(fm, fr) if x[0] != "f1"]
            print(f"{name:18} fold {fm['fold']}: F1 {fm['f1']:.4f} vs {fr['f1']:.4f}"
                  f" (diff {dF:+.4f})  threshold {fm['threshold']:.4g} vs {fr['threshold']:.4g}"
                  f"  train {fm['train_sec']:.1f}s vs {fr['train_sec']:.1f}s"
                  f"  other fields differing: {len(d)}")
        within = worst <= a.learned_tol
        ok &= within
        print(f"{name:18} largest |F1 diff| {worst:.4f} -> "
              f"{'within' if within else 'OUTSIDE'} {a.learned_tol}")

    print("ALL MATCH" if ok else "MISMATCH")


if __name__ == "__main__":
    main()
