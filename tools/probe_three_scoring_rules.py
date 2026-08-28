"""Three scoring rules, one set of runs — does the GATE break the tie?

`docs/todo/2026-08-25-two-scorers-two-winners-and-nothing-decides.md` reports two
live rules that pick opposite winners for rate+context, and says the re-fit cannot
start until one is chosen. It lists a third form in its own decision list — *"a
separate gate that a candidate must pass rather than a term in F1, which is what
`hot_fa` already looks like"* — and does not measure it.

**It is not a hypothetical. It is in `bench.py` and it is already the default.**
`pick_operating_point(max_probe_per_min=-1.0)` looks the detector up in
`MAX_PROBE_PER_MIN` and raises `TooPromiscuous` rather than taking the runner-up
silently; the reasoning is in that dict's docstring, landed 2026-08-22 — three days
*before* the todo was filed:

    the probe stays OUT of F1. Folding it in makes the headline measure how hard
    the probe was set ... The fix for "the alarm cannot ring" is to give the probe
    a gate at selection time, not to corrupt the score.

So this asks the question that decides whether that answer is sufficient: **on the
sweep where the two rules disagree, does the gate agree with either of them?**

    rule 1  probe-blind   F1 from BenchResult.precision = n_hit / n_scored, argmax
    rule 2  probe-inclusive F1 from n_hit / n_detected,               argmax
    rule 3  gate          rule 1's F1, argmax over candidates whose
                          hot_fa_per_min <= MAX_PROBE_PER_MIN[detector]

**One set of detector runs feeds all three.** Every rule reads the same pooled
counts, so a difference here is the rule and nothing else — and the pooling goes
through `bench.pool_scores`, because hand-pooling is the specific defect the todo
is about (`probe_rate_mechanism.py` re-forked it four days after a review said
"import this").

`--selftest` runs the gate at an infinite ceiling and requires it to reproduce
rule 1 exactly, on every point. Without that this is three numbers with a story
attached, and the gate could differ for a reason that is not the gate.
"""
import argparse
import json
import math

import numpy as np

from bugarach.bench import (BACKGROUND_GRID, BENCH_RECORDING, MAX_PROBE_PER_MIN,
                            OPERATING_POINTS, REGIMES, make_recording,
                            pool_scores)
from bugarach.detectors.rate import recording_extent, rate_detect, stream_trains
from bugarach.score import score_stream

REGIME = "baseline_quiet"
SEEDS = (1, 2, 3)
TOL_SEC = 1.5
DETECTOR = "rate"

#: The two mechanisms forks §3 puts against each other, each swept over its OWN
#: knob so neither is credited a sweep the other did not get — the todo's rule.
ADDITIVE_GRID = OPERATING_POINTS["rate"].grid
MULTIPLICATIVE_GRID = (5.0, 10.0, 15.0, 20.0, 30.0, 40.0, 55.0, 70.0, 90.0, 120.0)


def _pooled(mode, knob, bg_rate):
    """One BenchResult for one (mechanism, knob, background) over the seeds.

    Pools through `bench.pool_scores` rather than by hand. That is not a style
    preference here: the fork this probe is about was created by a tool that
    pooled `n_hit / n_detected` inline while the six went through `evaluate`.
    """
    scores = []
    for s in SEEDS:
        sl, gt = make_recording(REGIME, s, bg_rate_hz=bg_rate)
        ext = recording_extent(sl)
        trains = stream_trains(sl.streams["events"], ext)
        kw = dict(context_win=60.0, rate_win=1.0, grid_dt=0.1)
        if mode == "multiplicative":
            kw.update(threshold_mode="multiplicative", threshold_alpha=knob)
        else:
            kw.update(excess_threshold_hz=knob)
        det = rate_detect(trains, ext, **kw)
        scores.append(score_stream(gt, det, tol_sec=TOL_SEC))
    return pool_scores(scores, detector=DETECTOR, regime=REGIME, seeds=SEEDS,
                       knob_value=knob)


def _inclusive_f1(r):
    """Rule 2: precision counts the probe's firings against the detector."""
    prec = r.n_hit / r.n_detected if r.n_detected else float("nan")
    rec = r.recall
    if not (np.isfinite(prec) and np.isfinite(rec)) or prec + rec == 0:
        return float("nan")
    return 2 * prec * rec / (prec + rec)


def _argmax(rows, key):
    live = [r for r in rows if np.isfinite(key(r))]
    return max(live, key=key) if live else None


def winners(rows, ceiling):
    """The three rules' picks over one mechanism's sweep at one background."""
    blind = _argmax(rows, lambda r: r.f1)
    incl = _argmax(rows, _inclusive_f1)
    eligible = [r for r in rows
                if not np.isfinite(r.hot_fa_per_min) or r.hot_fa_per_min <= ceiling]
    gated = _argmax(eligible, lambda r: r.f1)
    return blind, incl, gated


def run(ceiling):
    out = []
    for bg in BACKGROUND_GRID:
        point = {"bg_rate_hz": bg, "mechanisms": {}}
        for mode, grid in (("additive", ADDITIVE_GRID),
                           ("multiplicative", MULTIPLICATIVE_GRID)):
            rows = [_pooled(mode, v, bg) for v in grid]
            blind, incl, gated = winners(rows, ceiling)
            point["mechanisms"][mode] = {
                "blind": _row(blind), "inclusive": _row(incl), "gated": _row(gated),
                "n_eligible": sum(1 for r in rows
                                  if not np.isfinite(r.hot_fa_per_min)
                                  or r.hot_fa_per_min <= ceiling),
                "n_grid": len(rows),
            }
        out.append(point)
    return out


def _row(r):
    if r is None:
        return None
    return {"knob": r.knob_value, "f1": r.f1, "inclusive_f1": _inclusive_f1(r),
            "precision": r.precision, "recall": r.recall,
            "hot_fa": r.hot_fa, "hot_fa_per_min": r.hot_fa_per_min}


def _mech_winner(point, rule):
    """Which MECHANISM a rule prefers at one background rate."""
    a = point["mechanisms"]["additive"][rule]
    m = point["mechanisms"]["multiplicative"][rule]
    key = "inclusive_f1" if rule == "inclusive" else "f1"
    if a is None and m is None:
        return "neither"
    if a is None:
        return "multiplicative"
    if m is None:
        return "additive"
    return "multiplicative" if m[key] > a[key] else "additive"


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--selftest", action="store_true",
                    help="gate at an infinite ceiling must reproduce rule 1 exactly")
    ap.add_argument("--json", metavar="PATH")
    args = ap.parse_args()

    ceiling = MAX_PROBE_PER_MIN[DETECTOR]

    if args.selftest:
        data = run(math.inf)
        bad = []
        for p in data:
            for mode, m in p["mechanisms"].items():
                if m["blind"] != m["gated"]:
                    bad.append((p["bg_rate_hz"], mode, m["blind"], m["gated"]))
                if m["n_eligible"] != m["n_grid"]:
                    bad.append((p["bg_rate_hz"], mode, "eligibility",
                                m["n_eligible"], m["n_grid"]))
        if bad:
            for b in bad:
                print("MISMATCH", b)
            raise SystemExit("selftest FAILED — an infinite ceiling changed the pick")
        print(f"selftest clean: {len(data)} background points x 2 mechanisms, "
              "an infinite ceiling reproduces the probe-blind pick exactly and "
              "excludes nothing")
        return

    data = run(ceiling)
    print(f"regime {REGIME}  seeds {SEEDS}  tol {TOL_SEC}s  "
          f"probe window {BENCH_RECORDING['hot_window']}")
    print(f"gate ceiling for {DETECTOR}: {ceiling} firings/min\n")

    hdr = (f"{'bg (Hz)':>8}  {'mechanism':>14}  {'blind F1':>9} {'knob':>6} "
           f"{'probe/min':>9}  {'gated F1':>9} {'knob':>6}  {'elig':>5}")
    print(hdr)
    for p in data:
        for mode in ("additive", "multiplicative"):
            m = p["mechanisms"][mode]
            b, g = m["blind"], m["gated"]
            print(f"{p['bg_rate_hz']:8.4f}  {mode:>14}  "
                  f"{b['f1']:9.3f} {b['knob']:6g} {b['hot_fa_per_min']:9.1f}  "
                  + (f"{g['f1']:9.3f} {g['knob']:6g}" if g else f"{'REFUSED':>16}")
                  + f"  {m['n_eligible']:2d}/{m['n_grid']:<2d}")

    print("\nwhich mechanism each rule picks, per background point:")
    print(f"{'bg (Hz)':>8}  {'rule 1 blind':>15}  {'rule 2 inclusive':>17}  "
          f"{'rule 3 gate':>15}")
    tally = {"blind": 0, "inclusive": 0, "gated": 0}
    for p in data:
        picks = {r: _mech_winner(p, r) for r in ("blind", "inclusive", "gated")}
        for r, v in picks.items():
            tally[r] += v == "multiplicative"
        print(f"{p['bg_rate_hz']:8.4f}  {picks['blind']:>15}  "
              f"{picks['inclusive']:>17}  {picks['gated']:>15}")
    n = len(data)
    print(f"\nmultiplicative wins:  blind {tally['blind']}/{n}   "
          f"inclusive {tally['inclusive']}/{n}   gate {tally['gated']}/{n}")
    print("\nThe gate agrees with whichever column it matches. If it matches the "
          "inclusive one\nwhile leaving F1 uncorrupted, the tie the todo reports "
          "is already broken in bench.py.")

    if args.json:
        with open(args.json, "w") as fh:
            json.dump({"regime": REGIME, "seeds": list(SEEDS), "tol_sec": TOL_SEC,
                       "ceiling_per_min": ceiling, "points": data}, fh, indent=1)
        print(f"\nwrote {args.json}")


if __name__ == "__main__":
    main()
