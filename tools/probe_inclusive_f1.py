#!/usr/bin/env python3
"""Rescore the bake-off with probe-block firings counted as false alarms.

    python tools/probe_inclusive_f1.py --bakeoff docs/learned/bakeoff.json \
        --out docs/learned/probe_inclusive.json

**Why this exists.** `bench.BenchResult.precision` is `n_hit / (n_detected - hot_fa)`:
firings inside the deliberate no-event block leave the denominator, so a detector is
not charged for them. That is a defensible rule — the block is a diagnostic, and
`docs/todo/2026-08-16-promiscuity-probe-cannot-fail.md` explains why it was built that
way — but it means the published F1 cannot see the one behaviour the block was planted
to expose, and the published ranking is a ranking under that rule.

A murderboard on the learned-detector page (2026-08-27) found the consequence: the page
led with a tie that the rule produces, disclosed three sections later that F1 could not
see the trap, and never said what F1 would have said. So this computes the other number
rather than leaving the reader to wonder.

**It is a derived store, not a new measurement.** Nothing retrains and nothing re-detects:
it reads the per-fold `n_hit`, `n_detected` and `n_planted` already in `bakeoff.json` and
recomputes precision without the forgiveness term. Both numbers describe the same runs.

⚠ **This rule is the subject of an open decision, and nothing here settles it.**
`docs/todo/2026-08-25-two-scorers-two-winners-and-nothing-decides.md` is
`waiting-on-tony` and **blocks the re-fit**: two precision rules are already live in the
tree — `bench.BenchResult.precision`'s `n_hit / n_scored` and
`tools/probe_rate_mechanism.py`'s `n_hit / n_detected` — they pick opposite winners for
the rate detector, and locust reads F1 0.09 one way against 0.68 the other. This file
computes the second rule and so is a **third** implementation of it.

That is the fork `bench.pool_scores`' own docstring was written to stop, which makes
adding one deliberate rather than careless. The justification, and its limit:

* it does **not** pick a winner. The page publishes both columns side by side and says
  in terms that the ordering is not stable between them, which is the honest position
  while the decision is open — and is strictly more informative than the page that
  published one column and mentioned the other three sections later;
* it does **not** feed calibration, fitting or any operating point. It reads a finished
  results file and writes a display store. Nothing downstream consumes it;
* it must **not** become the answer by attrition. When the open decision lands, this
  file either adopts the chosen rule or is deleted — and the todo names a third option
  neither rule implements (a gate rather than a term in F1), which would delete it.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def _f1(precision: float, recall: float) -> float:
    return 2 * precision * recall / (precision + recall) if precision + recall else 0.0


def rescore(fold: dict) -> dict:
    """One fold, with probe firings charged to precision.

    `n_detected` is every call the detector made; `n_hit` is the calls that matched a
    planted event. The published rule subtracts `hot_fa` from the denominator; this does
    not. Recall is untouched — a firing in an empty block cannot change what was found.
    """
    hit, detected, planted = fold["n_hit"], fold["n_detected"], fold["n_planted"]
    precision = hit / detected if detected else 0.0
    recall = hit / planted if planted else 0.0
    return {"precision": precision, "recall": recall, "f1": _f1(precision, recall)}


def _stats(values: list[float]) -> dict:
    n = len(values)
    mean = sum(values) / n
    # Sample standard deviation, matching bench.pool_scores' use of statistics.stdev,
    # so the two spreads on the page are the same kind of quantity.
    var = sum((v - mean) ** 2 for v in values) / (n - 1) if n > 1 else 0.0
    return {"mean": mean, "sd": var ** 0.5, "min": min(values),
            "max": max(values), "n": n}


def build(bakeoff: dict) -> dict:
    out: dict = {"folds": bakeoff.get("folds"), "detectors": {}}
    for group in ("hand_written", "learned"):
        for name, rec in bakeoff.get(group, {}).items():
            per_fold = [rescore(f) for f in rec["per_fold"]]
            published = rec["f1"]["mean"]
            inclusive = _stats([f["f1"] for f in per_fold])
            # The OTHER planted negative. The probe block is what the published rule
            # forgives; distractors are charged by both rules, and a detector that
            # reads zero in the probe column while hitting every distractor is telling
            # you something the probe column cannot. Carried here so the page can put
            # the two side by side, and so this store regenerates whole from this tool
            # — an earlier version had these fields written in by a separate script,
            # which meant re-running the tool silently dropped columns the page quotes.
            dh = [f["distractor_hits"] for f in rec["per_fold"]]
            out["detectors"][name] = {
                "group": group,
                "published_f1": published,
                "f1": inclusive,
                "precision": _stats([f["precision"] for f in per_fold]),
                "recall": _stats([f["recall"] for f in per_fold]),
                # How much the forgiveness term was worth to this detector. Positive
                # means the published number is the flattering one.
                "f1_drop": published - inclusive["mean"],
                "hot_fa": rec["hot_fa"],
                "distractor_hits_mean": sum(dh) / len(dh),
                "distractor_hits_per_fold": bakeoff["spec"]["n_distractors"]
                                            * bakeoff["seeds_per_fold"],
            }
    ranked = sorted(out["detectors"].items(), key=lambda kv: -kv[1]["f1"]["mean"])
    out["order_inclusive"] = [n for n, _ in ranked]
    out["order_published"] = [
        n for n, _ in sorted(out["detectors"].items(),
                             key=lambda kv: -kv[1]["published_f1"])]
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--bakeoff", default="docs/learned/bakeoff.json")
    ap.add_argument("--out", default="docs/learned/probe_inclusive.json")
    a = ap.parse_args(argv)

    bakeoff = json.loads(Path(a.bakeoff).read_text())
    result = build(bakeoff)
    Path(a.out).write_text(json.dumps(result, indent=1, sort_keys=True) + "\n")

    print(f"wrote {a.out}")
    print(f"{'detector':10s} {'published':>10s} {'inclusive':>10s} {'drop':>7s}  trap/fold")
    for name in result["order_published"]:
        d = result["detectors"][name]
        print(f"{name:10s} {d['published_f1']:10.3f} {d['f1']['mean']:10.3f} "
              f"{d['f1_drop']:7.3f}  {d['hot_fa']['mean']:.2f}")
    return 0


if __name__ == "__main__":                                      # pragma: no cover
    raise SystemExit(main())
