#!/usr/bin/env python3
"""Recompute calls/hour on the CORRECTED no-coordination recording, and re-pick ``best.json``.

    python tools/rescore_null_after_fix.py --models <dir> --bench fast

**Why this exists rather than a retrain.** ``bench.NULL_RECORDING`` carried a stale literal
``bg_rate_hz`` of 0.0052 — the pre-#756 quiet endpoint — while ``REGIMES`` quiet had moved to
0.0042. #761 made the null follow the background it stands for. **Training is unaffected**: models
fit on ``make_recording``, not on the null. What the null decides is the ``null_per_hour`` column
in ``tools/train_learned_on_bench.py`` and therefore which seed becomes ``best.json``, because the
pick is *the highest mean held-out F1 among the fits at or under the anchor budget*. A fit that was
over the budget on a busier null may be under it on the corrected one.

So the fits stay; only the column they are filtered by is recomputed. **Re-running the training
instead would change the F1 numbers too** (different RNG draws), which would confuse a bench fix
with a model change and make these rows incomparable with the ones already published.

**It reproduces ``held_out``'s null arithmetic exactly** — ``make_null_recording(s + 50_000)`` over
``NULLS``, detections summed, divided by total hours — rather than re-deriving it, so a change to
that rule cannot silently diverge here. The F1 columns are copied from the existing summary
untouched.
"""
from __future__ import annotations

import argparse
import importlib
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
for _p in (REPO / "src", REPO / "tools"):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

BENCHES = {"fast": "bugarach.bench", "slow": "bugarach.bench_slow",
           "combined": "bugarach.bench_combined"}


def null_per_hour(b, run) -> float:
    """``train_learned_on_bench.held_out``'s null arithmetic, imported rather than restated."""
    from train_learned_on_bench import NULLS

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
    p.add_argument("--models", type=Path, required=True,
                   help="the directory holding the seed checkpoints and summary.json")
    p.add_argument("--bench", choices=sorted(BENCHES), required=True)
    p.add_argument("--dry-run", action="store_true", help="print; do not write")
    a = p.parse_args(argv)

    from bugarach.learn.checkpoint import load

    b = importlib.import_module(BENCHES[a.bench])
    summary = json.loads((a.models / "summary.json").read_text(encoding="utf-8"))
    budget = b.MAX_FALSE_POSITIVES_PER_HOUR["coact"]
    print(f"{BENCHES[a.bench]}: null bg_rate_hz now "
          f"{b.NULL_RECORDING['bg_rate_hz']}, quiet "
          f"{b.REGIMES['baseline_quiet']['bg_rate_hz']}, budget {budget:g}/h")

    rows = summary["rows"] if "rows" in summary else summary["seeds"]
    print(f"\n{'seed':>5} {'mean F1':>8} {'calls/h was':>12} {'now':>8}  {'eligible':>9}")
    for r in rows:
        m = load(a.models / r["path"])
        was = r["null_per_hour"]
        r["null_per_hour_before_761"] = was
        r["null_per_hour"] = null_per_hour(b, lambda sl: m.predict(sl)[0])
        ok = r["null_per_hour"] <= budget
        print(f"{r['seed']:>5} {r['mean']:8.3f} {was:12.2f} {r['null_per_hour']:8.2f}  "
              f"{'yes' if ok else 'NO':>9}")

    ok = [r for r in rows if r["null_per_hour"] <= budget] or rows
    best = max(ok, key=lambda r: r["mean"])
    was_best = summary.get("best")          # a file name, as train_learned_on_bench writes it
    moved = best["path"] != was_best
    print(f"\nbest: {best['path']} mean F1 {best['mean']:.3f}, "
          f"{best['null_per_hour']:.2f} calls/h — "
          f"{'CHANGED from ' + str(was_best) if moved else 'unchanged by the rescore'}")

    summary["rescored_on_corrected_null"] = {
        "why": "#761 made bench.NULL_RECORDING follow REGIMES quiet; the fits are untouched",
        "null_bg_rate_hz": b.NULL_RECORDING["bg_rate_hz"],
        "best_before": was_best,
        "best_changed": bool(moved),
    }
    summary["best"] = best["path"]
    summary["best_within_budget"] = best["null_per_hour"] <= budget
    if a.dry_run:
        print("\n--dry-run: nothing written")
        return 0
    (a.models / "summary.json").write_text(json.dumps(summary, indent=1) + "\n",
                                           encoding="utf-8")
    (a.models / "best.json").write_text(
        (a.models / best["path"]).read_text(encoding="utf-8"), encoding="utf-8")
    print(f"wrote {a.models / 'summary.json'} and best.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
