#!/usr/bin/env python3
"""Recompute a training run's calls/hour on the CURRENT no-coordination recording, and re-pick.

    python tools/rescore_null_on_bench.py --bench slow --run <dir>/models/chorus_gain_norm

**Why this exists rather than a retrain.** ``tools/train_learned_on_bench.py`` scores three things
per seed: F1 on held-out recordings, a threshold, and **calls/hour on**
``make_null_recording`` — and that last one decides which checkpoint becomes ``best.json``, because
the pick is the best mean F1 *among the seeds inside the null budget*.

On 2026-09-23 ``bench_slow.NULL_RECORDING`` was corrected: it had carried a stale literal
``0.0030`` Hz background while ``REGIMES`` quiet had moved to ``0.0024`` (#761). **The fits
themselves are unaffected** — models train on the main recordings, and nothing in training reads
the null recording. Only the calls/hour column and the pick depend on it.

So a run finished before that fix does not need retraining. It needs its null column recomputed on
the corrected recording and its ``best.json`` re-picked by the same rule. That is cheaper, and it
is also *exactly equivalent*: the checkpoints are byte-identical to what a retrain would produce.

**It reproduces the training tool's rule rather than inventing one**: the same ``NULLS`` seeds
offset by the same ``+50_000``, the same budget (``MAX_FALSE_POSITIVES_PER_HOUR["coact"]``), and
the same tie-break — best mean F1 among rows inside budget, or among all rows if none is.
"""
from __future__ import annotations

import argparse
import importlib
import json
import shutil
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
for _p in (REPO / "src", REPO / "tools"):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

BENCHES = {"fast": "bugarach.bench", "slow": "bugarach.bench_slow",
           "combined": "bugarach.bench_combined"}
NULLS = tuple(range(4000, 4012))
"""The training tool's own null seeds. Kept in step with it deliberately: a rescore that used a
different set would not be comparable with the column it replaces."""


def null_per_hour(b, run) -> float:
    from bugarach.score import score_stream

    n, h = 0, 0.0
    for s in NULLS:
        sl, gt = b.make_null_recording(s + 50_000)
        n += score_stream(gt, run(sl)).n_detected
        h += gt.params["duration_sec"] / 3600
    return n / h


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--bench", choices=sorted(BENCHES), required=True)
    p.add_argument("--run", type=Path, required=True, help="the folder holding summary.json")
    p.add_argument("--dry-run", action="store_true")
    a = p.parse_args(argv)

    from bugarach.learn import checkpoint

    b = importlib.import_module(BENCHES[a.bench])
    summary = json.loads((a.run / "summary.json").read_text(encoding="utf-8"))
    budget = b.MAX_FALSE_POSITIVES_PER_HOUR["coact"]

    print(f"{a.run.name}: null recording background is "
          f"{b.NULL_RECORDING['bg_rate_hz']} Hz, budget {budget:g} calls/h")
    print(f"{'seed':>4} {'was':>8} {'now':>8}  mean F1")
    for row in summary["rows"]:
        tr = checkpoint.load(a.run / row["path"])
        now = null_per_hour(b, lambda sl: tr.predict(sl)[0])
        print(f"{row['seed']:>4} {row['null_per_hour']:8.2f} {now:8.2f}  {row['mean']:.3f}"
              + ("  <- moved" if abs(now - row["null_per_hour"]) > 1e-9 else ""))
        row["null_per_hour_before_rescore"] = row["null_per_hour"]
        row["null_per_hour"] = now

    ok = [r for r in summary["rows"] if r["null_per_hour"] <= budget] or summary["rows"]
    best = max(ok, key=lambda r: r["mean"])
    moved = best["path"] != summary["best"]
    print(f"best: {summary['best']} -> {best['path']}" + ("  ** PICK MOVED **" if moved else
                                                          "  (unchanged)"))
    if a.dry_run:
        return 0

    summary["best_before_rescore"] = summary["best"]
    summary["best"] = best["path"]
    summary["best_within_budget"] = best["null_per_hour"] <= budget
    summary["rescored"] = (
        "calls/hour recomputed on the corrected no-coordination recording (#761: bench_slow's "
        "NULL_RECORDING had a stale 0.0030 Hz literal where REGIMES quiet is 0.0024). The fits "
        "are untouched -- training never reads that recording -- so this is equivalent to a "
        "retrain, and best.json was re-picked by the training tool's own rule.")
    (a.run / "summary.json").write_text(json.dumps(summary, indent=1) + "\n", encoding="utf-8")
    shutil.copyfile(a.run / best["path"], a.run / "best.json")
    print(f"wrote {a.run / 'summary.json'} and best.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
