#!/usr/bin/env python3
"""What CoactDetect's merge gap costs it on the crowded recordings, against no merging at all.

    python tools/coact_no_merge_crowded.py [--run DIR] [--workers 6] [--out FILE]

**Why this exists.** The merge-gap addendum reports, for every net, what the gap it chose costs on
the crowded recordings against that net's own 2 s. The same quantity has never been measured for
CoactDetect, which is the detector every net is compared against. Its review record names this as
the single cheapest check nobody has run, and the page says the comparison is missing rather than
asserting its outcome (``docs/reviews/net-merge-gap-2026-09-19.md``). Tony asked for it on
2026-09-21 as the descriptive half of option B.

**What it measures.** CoactDetect at the run's own base setting -- goal 1's sliding values, which is
what the fair comparison scored it at -- and the identical setting with **merging disabled**, on the
identical crowded recordings the nets were charged on (``bench.make_tail_recording``, both
backgrounds, seeds 1 to ``N_TAIL``). One parameter moves. Nothing is selected, nothing is retrained,
and no merge gap is re-decided: CoactDetect keeps the 8 s it ran with, and this reports what that 8 s
is worth there.

**"No merging at all" has two readings here, and only one of them is a baseline.** ``merge_gap_sec``
of NaN disables merging outright: every comparison against it is False, so nothing is combined.
``0.0`` still merges runs that touch. For a **sliding** detector those are very different things,
because its windows overlap by construction -- at NaN one planted event is reported once per
significant window, so on a crowded recording CoactDetect emits about six times as many calls at the
same recall and its precision collapses. That is a decoding artifact, not a detector operating
without a merge gap, and it is why the headline number here is measured against **0.0**, the
minimum coherent decoding. The NaN row is reported beside it with the call counts that show what it
is, because it is the row a reader would otherwise assume was the baseline.

This is the asymmetry the addendum's own limits section names -- the two sides' gaps "match by name,
not by operation" -- arriving as a number: a net merges runs of frames over its threshold, and
nothing forces it to merge anything, while a sliding detector's output is not interpretable until
overlapping windows are combined.

**This tool does not adjudicate, and the distinction is the point.** Saying CoactDetect's gap "would
have been refused", or that it "passes on the same terms" as the nets', applies the 0.02 F1 crowded
allowance -- which is unsigned, and is the decision this is evidence for. The output carries the
numbers and an explicit null where that verdict would go.

⚠ **A caution about `coact_crowded_no_merge`**, a field in the addendum's own output JSON: it is
**not** this measurement. It holds ``shipped_reference``, CoactDetect at ``bench.OPERATING_POINTS``,
which differs from the as-run setting in the window mode, the context window, alpha and the guard --
and which carries a **3 s** merge gap, the detector's own default, because the shipped point names no
gap at all. Reading it as a no-merge number attributes a five-parameter difference to the merge gap.

Run with branch ``tune-bench-comparison``'s ``src`` and ``tools`` first on ``PYTHONPATH``: the
scoring helpers live there, as they do for ``tools/tune_net_merge_gap.py``.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
import time
from multiprocessing import Pool
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path[:0] = [str(REPO / "src"), str(REPO / "tools")]

DEFAULT_RUN = REPO / "docs" / "learned" / "tuned_vs_coact" / "fair_comparison_2026_09_18"
DEFAULT_OUT = DEFAULT_RUN / "coact_no_merge_crowded.json"


def main(argv=None) -> int:
    from search_all_settings import N_TAIL, TAIL, _job, _key

    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--run", type=Path, default=DEFAULT_RUN,
                    help="the run's summary folder (meta.json, for the as-run coded base)")
    ap.add_argument("--workers", type=int, default=6)
    ap.add_argument("--out", type=Path, default=DEFAULT_OUT)
    a = ap.parse_args(argv)

    meta = json.loads((a.run / "meta.json").read_text())
    base = dict(meta["declaration"]["coded_base"]["values"]["coact"])
    as_run_gap = base.get("merge_gap_sec")
    seeds = list(range(1, N_TAIL + 1))

    variants = {
        "as_run": dict(base),
        "no_merge": {**base, "merge_gap_sec": float("nan")},
        "gap_zero": {**base, "merge_gap_sec": 0.0},
    }

    todo, keys = [], {}
    for name, params in variants.items():
        k = _key("coact", params)
        keys[name] = k
        for regime in TAIL:
            todo.append(("coact", k[1], tuple(sorted(params.items())), regime, seeds, False))

    from bugarach import bench
    from bugarach.score import score_stream

    DIAG_BACKGROUND, DIAG_SEED = sorted(TAIL)[0], seeds[0]
    DIAG_REC, DIAG_GT = bench.make_tail_recording("baseline_" + DIAG_BACKGROUND.split("_", 1)[1],
                                                  DIAG_SEED)

    print(f"{len(variants)} settings x {len(TAIL)} crowded backgrounds x {len(seeds)} recordings",
          flush=True)
    t0 = time.time()
    with Pool(a.workers) as pool:
        got = {key: val for key, val in pool.imap_unordered(_job, todo, chunksize=1)}

    def crowded(name):
        k = keys[name]
        vals = [got[(k[0], k[1], r)] for r in TAIL]
        if any(v.get("refused") for v in vals):
            return float("nan")
        return sum(v["f1"] for v in vals) / len(vals)

    f1 = {name: crowded(name) for name in variants}
    # Against 0.0, the minimum coherent decoding -- see the module docstring for why NaN is not the
    # baseline for a sliding detector.
    cost = f1["as_run"] - f1["gap_zero"]

    # The evidence for that call, on one crowded recording: what each setting actually emits.
    diagnostic = {}
    for name, params in variants.items():
        det = bench.run_detector("coact", DIAG_REC, **params)
        sc = score_stream(DIAG_GT, det)
        diagnostic[name] = dict(calls=int(det.n_events), f1=float(sc.f1),
                                recall=float(sc.recall), precision=float(sc.precision))

    doc = dict(
        what="CoactDetect's merge gap against no merging at all, on the crowded recordings the "
             "nets' merge-gap addendum charges its choices on",
        generator="tools/coact_no_merge_crowded.py",
        run=a.run.name,
        crowded_recordings=dict(builder="bench.make_tail_recording", backgrounds=list(TAIL),
                                seeds=seeds),
        setting=dict(detector="coact", base=base, as_run_merge_gap_sec=as_run_gap,
                     source="meta.json declaration.coded_base.values.coact (goal 1's sliding "
                            "values, what the fair comparison scored CoactDetect at)"),
        baseline="gap_zero. merge_gap_sec = 0.0 merges only runs that touch, which is the minimum "
                 "coherent decoding for a sliding detector. merge_gap_sec = NaN disables merging "
                 "outright and reports one call per significant window; its recall matches "
                 "gap_zero and its precision collapses, so it measures the decoding and not the "
                 "gap. The diagnostic block is the evidence",
        crowded_mean_f1={k: (None if math.isnan(v) else v) for k, v in f1.items()},
        diagnostic=dict(recording=dict(background=DIAG_BACKGROUND, seed=DIAG_SEED),
                        note="one crowded recording, to show what each setting emits",
                        per_setting=diagnostic),
        merge_gap_worth_on_crowded_recordings=None if math.isnan(cost) else cost,
        reading="as_run minus gap_zero. Positive means the 8 s gap SCORES HIGHER on the crowded "
                "recordings than the minimum decoding; negative means the gap costs it there",
        adjudication=None,
        adjudication_note="deliberately not decided here. Whether this margin passes or fails the "
                          "crowded check applies the 0.02 F1 allowance, which is unsigned; that is "
                          "the ruling this measurement is evidence for, not a conclusion it may "
                          "draw. See docs/todo/2026-09-20-why-the-merge-gap-page-would-not-"
                          "converge.md, option B.",
        seconds=round(time.time() - t0, 1),
    )
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps(doc, indent=1) + "\n", encoding="utf-8")

    d = diagnostic
    print(f"as run (merge gap {as_run_gap:g} s): {f1['as_run']:.4f} mean F1   "
          f"({d['as_run']['calls']} calls on the diagnostic recording)")
    print(f"gap 0.0 s, the baseline:            {f1['gap_zero']:.4f} mean F1   "
          f"({d['gap_zero']['calls']} calls)")
    print(f"no merging at all (NaN):            {f1['no_merge']:.4f} mean F1   "
          f"({d['no_merge']['calls']} calls, precision {d['no_merge']['precision']:.3f} "
          f"-- one call per significant window, not a baseline)")
    print(f"the {as_run_gap:g} s gap is worth {cost:+.4f} mean F1 there, against gap 0.0")
    print(a.out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
