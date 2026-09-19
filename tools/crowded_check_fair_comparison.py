#!/usr/bin/env python3
"""Apply goal 1's crowded-recording veto, after the fact, to every coded choice of the fair comparison.

    python tools/crowded_check_fair_comparison.py [--run DIR] [--workers 12]

**Why this exists.** Goal 2's per-fold search (``tools/tune_learned_vs_coact.py``, the 2026-09-18
fair comparison) applied the context rule but **not** goal 1's fourth budget,
``bench.MAX_CROWDED_DROP``: a setting may not lose more than that much mean F1 on the crowded
recordings (``bench.make_tail_recording``) against the setting it would replace. Goal 1 added the
veto after its first every-knob search gained 0.11 to 0.31 held-out F1 for four detectors by
running merge gaps out to about a minute, while losing 0.25 to 0.32 on crowded recordings. Merging
makes a detector call less, which looks cleaner on every false-alarm measure, so no other budget can
see it. WSMIP065 pointed out on 2026-09-19 that the goal-2 search chose the top of the merge-gap
grid in nearly every fold.

So this scores each coded choice the run made (every detector, outer fold and selection) on the
crowded recordings, exactly as goal 1 does: ``search_all_settings._job`` over ``TAIL`` at seeds
1 to ``N_TAIL``, mean of the two backgrounds' pooled F1. The reference is the setting the choice
replaces: goal 1's sliding values for CoactDetect and LoCo (the run's own base), and
``bench.OPERATING_POINTS`` for the other four. Goal 1's own search anchors every detector to the
shipped ``bench.OPERATING_POINTS`` instead, so that reference is scored too and each choice carries
both verdicts; the report says whether the choice of reference changes one from this file, not
from a sentence. **It changes nothing about the run**; it reports which choices the veto would
have refused. Output: ``crowded_check.json`` beside the run's summaries.

The recordings are goal 1's selection-stage crowded recordings, seeds 1 to ``N_TAIL``. Goal 1's
published held-out crowded numbers (0.818 for sliding CoactDetect, for one) come from its held-out
seeds, 49 to 60, so they differ from the ones here for the same setting.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from multiprocessing import Pool
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path[:0] = [str(REPO / "src"), str(REPO / "tools")]

DEFAULT_RUN = REPO / "docs" / "learned" / "tuned_vs_coact" / "fair_comparison_2026_09_18"


def _clean(params: dict) -> dict:
    """JSON writes NaN as NaN, and the run stored it that way; keep it a float NaN."""
    return {k: (float("nan") if v is None and k.startswith("merge_gap") else v)
            for k, v in params.items()}


def main(argv=None) -> int:
    from search_all_settings import N_TAIL, TAIL, _job, _key

    from bugarach import bench

    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--run", type=Path, default=DEFAULT_RUN,
                    help="the run's summary folder (results.json and meta.json)")
    ap.add_argument("--workers", type=int, default=12)
    a = ap.parse_args(argv)

    results = json.loads((a.run / "results.json").read_text())
    meta = json.loads((a.run / "meta.json").read_text())
    base = meta["declaration"]["coded_base"]["values"]
    seeds = list(range(1, N_TAIL + 1))

    reference = {d: _clean({**bench.OPERATING_POINTS[d].params, **base.get(d, {})})
                 for d in results["hand"]}
    shipped = {d: _clean(dict(bench.OPERATING_POINTS[d].params)) for d in results["hand"]}
    choices = []
    for d, rows in results["hand"].items():
        for row in rows:
            for w in ("ungated", "gated"):
                choices.append((d, row["outer_fold"], w, _clean(row[w]["chosen_params"])))

    distinct = {}
    for d, params in (list(reference.items()) + list(shipped.items())
                      + [(d, p) for d, _, _, p in choices]):
        distinct.setdefault(_key(d, params), (d, params))
    todo = [(d, k[1], tuple(sorted(p.items())), regime, seeds, False)
            for k, (d, p) in distinct.items() for regime in TAIL]
    print(f"{len(distinct)} distinct settings x {len(TAIL)} crowded backgrounds x "
          f"{len(seeds)} recordings")
    with Pool(a.workers) as pool:
        got = {key: val for key, val in pool.imap_unordered(_job, todo, chunksize=1)}

    def crowded(d, params):
        k = _key(d, params)
        vals = [got[(k[0], k[1], r)] for r in TAIL]
        if any(v.get("refused") for v in vals):
            return float("nan")
        return sum(v["f1"] for v in vals) / len(vals)

    ref_f1 = {d: crowded(d, p) for d, p in reference.items()}
    shipped_f1 = {d: crowded(d, p) for d, p in shipped.items()}

    def passes(f1, ref):
        return bool(math.isfinite(f1) and math.isfinite(ref)
                    and f1 >= ref - bench.MAX_CROWDED_DROP)
    out = dict(
        what="goal 1's crowded-recording veto applied after the fact to the fair comparison's "
             "coded choices; the run itself did not apply it",
        max_crowded_drop=bench.MAX_CROWDED_DROP, tail=list(TAIL), seeds=seeds,
        reference_rule="the setting a choice replaces: meta.json coded_base over "
                       "bench.OPERATING_POINTS",
        reference={d: dict(params=reference[d], crowded_mean_f1=ref_f1[d]) for d in reference},
        shipped_reference_rule="goal 1's own reference: bench.OPERATING_POINTS, what ships",
        shipped_reference={d: dict(params=shipped[d], crowded_mean_f1=shipped_f1[d])
                           for d in shipped},
        choices=[])
    for d, h, w, params in choices:
        f1 = crowded(d, params)
        ok = passes(f1, ref_f1[d])
        out["choices"].append(dict(detector=d, outer_fold=h, selection=w,
                                   crowded_mean_f1=f1, reference_crowded_mean_f1=ref_f1[d],
                                   passes_veto=ok,
                                   shipped_reference_crowded_mean_f1=shipped_f1[d],
                                   passes_veto_vs_shipped=passes(f1, shipped_f1[d])))
        print(f"{d:7s} fold {h} {w:8s} crowded {f1:.3f}  reference {ref_f1[d]:.3f}  "
              f"{'passes' if ok else 'REFUSED'}  shipped {shipped_f1[d]:.3f}")
    (a.run / "crowded_check.json").write_text(json.dumps(out, indent=1, default=float) + "\n")
    print(a.run / "crowded_check.json")
    return 0


if __name__ == "__main__":
    sys.exit(main())
