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
    rule 3  gate          whatever `bench.pick_operating_point` RETURNS — which on
                          a promiscuous winner is a refusal, not the runner-up

**Rule 3 is called, not reimplemented, and that is a correction made 2026-09-02.**
Until then this file modelled the gate as *filter to eligible candidates, take the
argmax of those*. That is taking the runner-up, which is the one move the shipped
refusal forbids in terms:

    Tighten the detector or raise the ceiling deliberately — do not take the
    runner-up silently

So the column labelled "the gate, shipped" was not the shipped gate. What it
reported as additive *moving* on the two quietest backgrounds — F1 0.827 at knob 2
down to 0.689 at knob 4 — is under the real rule a `TooPromiscuous` refusal with no
operating point at all, which is exactly what `tools/refit.py` returns today for
`rate/baseline_quiet`. A mechanism that is refused cannot win a comparison, so the
mechanism tally moved too.

That is the third instance of the fork this probe is about. `probe_rate_mechanism.py`
re-pooled by hand four days after a review said *import this*; this file
re-implemented the gate six days after the gate landed, while quoting the sentence
that describes it correctly. **Rule 3 now calls the function**, so it cannot drift
from what ships without `--selftest` noticing.

**One set of detector runs feeds all three.** Every rule reads the same pooled
counts, so a difference here is the rule and nothing else — and the pooling goes
through `bench.pool_scores`, because hand-pooling is the specific defect the todo
is about.

`--selftest` runs the gate with `max_probe_per_min=None` — the gate off, every other
refusal still armed — and requires it to reproduce rule 1 exactly on every sweep.
Without that this is three numbers with a story attached, and rule 3 could differ
for a reason that is not the gate: `pick_operating_point` also refuses an optimum at
the edge of its grid and a knob that did nothing, and either would look like the
gate from outside.
"""
import argparse
import json
import math

import numpy as np

from bugarach.bench import (BACKGROUND_GRID, BENCH_RECORDING, MAX_PROBE_PER_MIN,
                            OPERATING_POINTS, REGIMES, DegenerateSweep,
                            EdgeOfRange, TooPromiscuous, make_recording,
                            pick_operating_point, pool_scores)
from bugarach.detectors.rate import recording_extent, rate_detect, stream_trains
from bugarach.score import score_stream

REGIME = "baseline_quiet"
SEEDS = (1, 2, 3)
TOL_SEC = 1.5
DETECTOR = "rate"

#: The two mechanisms forks §3 puts against each other, each swept over its OWN
#: knob so neither is credited a sweep the other did not get — the todo's rule.
ADDITIVE_GRID = OPERATING_POINTS["rate"].grid

#: **Refilled 2026-09-02, at both ends, and the old shape was hiding two things.**
#: It was `(5, 10, 15, 20, 30, 40, 55, 70, 90, 120)` — and calling the shipped
#: selector, instead of hand-rolling an argmax over it, immediately refused it:
#:
#: * **The bottom was the edge.** On the busiest backgrounds the best alpha WAS
#:   5.0, the grid's first value, with F1 still climbing as alpha fell.
#:   `pick_operating_point` calls that `EdgeOfRange` — the sweep stopped while it
#:   was still improving, so the value at the end is not an optimum, it is where
#:   the grid ran out.
#: * **The 5 -> 10 jump stepped over the peak.** At bg 0.028 the true optimum is
#:   **alpha 6, F1 0.667**; the old grid could only see 5.0 at **0.520** and
#:   reported that as multiplicative's best. The mechanism was being scored 0.147
#:   below its own peak at that background, in the comparison forks §3 rests on.
#:
#: The runner-up version of rule 3 could see neither, because it never called the
#: selector — it took the best eligible row and reported a winner. Alpha below 5
#: also lowers the bar far enough for multiplicative to fire in the probe at last
#: (4.87/min at alpha 2, bg 0.040), which is where its "never trips the probe"
#: reputation gets its first real test rather than a grid that excluded the range.
MULTIPLICATIVE_GRID = (2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0, 15.0, 20.0,
                       30.0, 40.0, 55.0, 70.0, 90.0, 120.0)


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
    """The three rules' picks over one mechanism's sweep at one background.

    Rules 1 and 2 are argmaxes because that is what a scoring rule is. Rule 3 is
    a **call**, because it is not a scoring rule at all — it is the selection
    procedure that ships, and its answer may be a refusal. Returns the gate's
    verdict alongside its pick: ``("chosen", result)`` or ``(<exception name>,
    None)``.
    """
    blind = _argmax(rows, lambda r: r.f1)
    incl = _argmax(rows, _inclusive_f1)
    try:
        gated, verdict = pick_operating_point(rows, max_probe_per_min=ceiling), "chosen"
    except (EdgeOfRange, DegenerateSweep, TooPromiscuous) as exc:
        gated, verdict = None, type(exc).__name__
    return blind, incl, gated, verdict


def run(ceiling):
    """Sweep both mechanisms across the background grid.

    ``ceiling`` goes straight to ``pick_operating_point``: a number overrides the
    per-detector budget, and ``None`` disables the gate while leaving the edge and
    degeneracy refusals armed — which is what ``--selftest`` needs, and why it is
    ``None`` here rather than ``math.inf``. An infinite ceiling would also pass the
    gate, but it would pass it by making the comparison vacuous rather than by
    turning the rule off, and the two are not the same claim.
    """
    out = []
    for bg in BACKGROUND_GRID:
        point = {"bg_rate_hz": bg, "mechanisms": {}}
        for mode, grid in (("additive", ADDITIVE_GRID),
                           ("multiplicative", MULTIPLICATIVE_GRID)):
            rows = [_pooled(mode, v, bg) for v in grid]
            blind, incl, gated, verdict = winners(rows, ceiling)
            # Eligibility is reported for the picture — how much of the grid the
            # budget puts out of reach — and is NOT how rule 3 chooses. Counting
            # it here and selecting with it is the confusion this file used to be.
            budget = math.inf if ceiling is None else ceiling
            point["mechanisms"][mode] = {
                "blind": _row(blind), "inclusive": _row(incl), "gated": _row(gated),
                "verdict": verdict,
                "n_eligible": sum(1 for r in rows
                                  if not np.isfinite(r.hot_fa_per_min)
                                  or r.hot_fa_per_min <= budget),
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
    """Which MECHANISM a rule prefers at one background rate.

    Under rule 3 a ``None`` is a **refusal**, not a missing number, and a
    mechanism the selector refuses cannot win: there is no operating point to
    quote. That is the whole difference between this and the runner-up version —
    there, a refused sweep silently re-entered the comparison one rung down.
    """
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
                    help="with the gate OFF, rule 3 must reproduce rule 1 exactly")
    ap.add_argument("--json", metavar="PATH")
    args = ap.parse_args()

    ceiling = MAX_PROBE_PER_MIN[DETECTOR]

    if args.selftest:
        data = run(None)
        bad = []
        for p in data:
            for mode, m in p["mechanisms"].items():
                if m["verdict"] != "chosen":
                    bad.append((p["bg_rate_hz"], mode, "verdict", m["verdict"]))
                if m["blind"] != m["gated"]:
                    bad.append((p["bg_rate_hz"], mode, m["blind"], m["gated"]))
                if m["n_eligible"] != m["n_grid"]:
                    bad.append((p["bg_rate_hz"], mode, "eligibility",
                                m["n_eligible"], m["n_grid"]))
        if bad:
            for b in bad:
                print("MISMATCH", b)
            raise SystemExit("selftest FAILED — with the gate off, rule 3 is not rule 1")
        print(f"selftest clean: {len(data)} background points x 2 mechanisms. With "
              "max_probe_per_min=None\nthe shipped selector reproduces the "
              "probe-blind pick exactly and refuses nothing, so\nevery difference "
              "in the run below is the gate and not the edge or degeneracy check.")
        return

    data = run(ceiling)
    print(f"regime {REGIME}  seeds {SEEDS}  tol {TOL_SEC}s  "
          f"probe window {BENCH_RECORDING['hot_window']}")
    print(f"gate ceiling for {DETECTOR}: {ceiling} firings/min\n")

    hdr = (f"{'bg (Hz)':>8}  {'mechanism':>14}  {'blind F1':>9} {'knob':>6} "
           f"{'probe/min':>9}  {'rule 3 — what ships':>19} {'knob':>6}  {'elig':>5}")
    print(hdr)
    for p in data:
        for mode in ("additive", "multiplicative"):
            m = p["mechanisms"][mode]
            b, g = m["blind"], m["gated"]
            got = (f"{g['f1']:19.3f} {g['knob']:6g}" if g
                   else f"{m['verdict']:>19} {'—':>6}")
            print(f"{p['bg_rate_hz']:8.4f}  {mode:>14}  "
                  f"{b['f1']:9.3f} {b['knob']:6g} {b['hot_fa_per_min']:9.1f}  "
                  f"{got}  {m['n_eligible']:2d}/{m['n_grid']:<2d}")

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

    refused = [(p["bg_rate_hz"], mode, m["verdict"])
               for p in data for mode, m in p["mechanisms"].items()
               if m["verdict"] != "chosen"]
    print(f"\nrule 3 refused {len(refused)} of {2 * n} sweeps outright — no operating "
          "point, not a lower one:")
    for bg, mode, why in refused:
        print(f"  {bg:8.4f}  {mode:>14}  {why}")
    if not refused:
        print("  (none)")
    print("\nA refused sweep is not a loss on points; it is the selector saying this\n"
          "detector has no operating point here until somebody tightens it or moves\n"
          "the budget deliberately. `tools/refit.py` reports the same thing for\n"
          "rate/baseline_quiet, which is BACKGROUND_GRID's 0.0052 row above.")

    if args.json:
        with open(args.json, "w") as fh:
            json.dump({"regime": REGIME, "seeds": list(SEEDS), "tol_sec": TOL_SEC,
                       "ceiling_per_min": ceiling, "points": data}, fh, indent=1)
        print(f"\nwrote {args.json}")


if __name__ == "__main__":
    main()
