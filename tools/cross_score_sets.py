#!/usr/bin/env python3
"""Score the settings tuned on one bench set on every other set of the same stream.

    python tools/cross_score_sets.py --searches <folder> --out <folder> --jobs 10

``<folder>`` holds one search per set, as ``<set>/search.json`` (``tools/search_all_settings.py
--bench <set> --out <folder>/<set>``).

**The question (Tony, 2026-11-12).** One synthetic set holds both groups of the default folder
and one holds each. Each is tuned on its own. Does one setting serve both groups, or does a
group need its own? For every stream and detector this takes three settings (the proposal of the
search on ``all``, on ``di`` and on ``male``) plus the shipped one, and scores each on
recordings of each set that no search saw.

**The proposal** of a search is ``tools/score_bench_candidates.py``'s: the held-out candidate
with the highest mean F1 whose gain over the shipped setting has an interval above zero, else
the shipped setting. Nothing here is adopted; that is Tony's.

**What is scored**, on fresh seeds (:data:`SEEDS`), both backgrounds, realistic spacing:

* F1, recall and precision on the set's planted recordings (``bench.evaluate``);
* false calls per hour on the set's recording with nothing planted;
* the share of pairs 1 s apart that are split, and of isolated events called twice
  (``bugarach.close_events``), on the set's recording with half the gaps set to 1 s.

The benches are simulated, so there is no dataset; each row names the sets it used.
"""
from __future__ import annotations

import argparse
import json
import multiprocessing as mp
import sys
import time
from pathlib import Path

import numpy as np

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))
sys.path.insert(0, str(REPO / "tools"))

REGIMES = ("baseline_quiet", "baseline_busy")
SEEDS = tuple(range(7000, 7024))
NULLS = tuple(range(7000, 7012))
CLOSE_SEC = 1.0
SHIPPED = "shipped"


def job(args):
    """One setting on one test set and background: planted, nothing planted, close pairs."""
    trained_on, test_set, det, params, regime, seeds, nulls = args
    from bugarach import bench as fast
    from bugarach import bench_sets, close_events as ce

    fast.use_spacing("realistic")
    m = bench_sets.load(test_set)
    stream_seeds = [s for s in seeds for _ in range(1)]
    r = m.evaluate(det, regime, seeds=tuple(stream_seeds), probe=False, **params)
    out = dict(trained_on=trained_on, test_set=test_set, detector=det, regime=regime,
               n_planted=int(r.n_planted), n_hit=int(r.n_hit), n_detected=int(r.n_detected),
               n_fa=int(r.n_fa), recall=float(r.recall), precision=float(r.precision),
               f1=float(r.f1))
    if regime == REGIMES[0]:
        out["null_per_hour"] = float(m.false_positives_per_hour(det, seeds=tuple(nulls), **params))
    pairs = dict(n_pairs=0, n_split=0, n_isolated=0, n_isolated_double=0)
    for seed in seeds:
        s, gt = ce.make(test_set, CLOSE_SEC, regime, seed)
        c = ce.pair_score(gt, m.run_detector(det, s, **params), CLOSE_SEC)
        for k in pairs:
            pairs[k] += int(c[k])
    out["close"] = pairs
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--searches", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--jobs", type=int, default=8)
    ap.add_argument("--seeds", type=int, default=len(SEEDS),
                    help="fresh recordings per background (doubled on fast)")
    a = ap.parse_args(argv)

    from score_bench_candidates import proposal

    from bugarach import bench as fast
    from bugarach import bench_sets

    by_stream: dict[str, list[str]] = {}
    # A set is scored, and scored on, only if this folder holds its search: sets measured on
    # another dataset (``fast_di_3x``) keep to their own folder of searches.
    without = [n for n in bench_sets.names() if not (a.searches / n / "search.json").exists()]
    for name in bench_sets.names():
        if name not in without:
            by_stream.setdefault(bench_sets.stream_of(name), []).append(name)

    tasks, settings, missing = [], {}, []
    for stream, sets in by_stream.items():
        k = fast.seed_factor(stream, "realistic")
        seeds = tuple(range(SEEDS[0], SEEDS[0] + a.seeds * k))
        nulls = tuple(range(NULLS[0], NULLS[0] + max(1, a.seeds // 2) * k))
        chosen = {}
        for name in sets:
            path = a.searches / name / "search.json"
            if not path.exists():
                missing.append(name)
                continue
            search = json.loads(path.read_text(encoding="utf-8"))
            for det in search["held_out"]:
                which, params, row = proposal(search, det)
                chosen.setdefault(det, {})[name] = dict(
                    candidate=which, params=params, search_mean_f1=row["mean_f1"])
                chosen[det].setdefault(SHIPPED, dict(
                    candidate=SHIPPED, params=dict(search["held_out"][det][SHIPPED]["params"]),
                    search_mean_f1=None))
        settings[stream] = chosen
        for det, by_set in chosen.items():
            for trained_on, c in by_set.items():
                for test_set in sets:
                    for regime in REGIMES:
                        tasks.append((trained_on, test_set, det, c["params"], regime, seeds, nulls))
    if without:
        print(f"no search here for: {', '.join(without)}; left out", file=sys.stderr)
    if not tasks:
        raise SystemExit(f"no <set>/search.json under {a.searches}")

    t0 = time.time()
    with mp.get_context("spawn").Pool(a.jobs) as pool:
        rows = pool.map(job, tasks, chunksize=1)

    table = {}
    for stream, sets in by_stream.items():
        for det, by_set in settings[stream].items():
            for trained_on in by_set:
                for test_set in sets:
                    mine = [r for r in rows if r["detector"] == det and r["test_set"] == test_set
                            and r["trained_on"] == trained_on]
                    if not mine:
                        continue
                    close = {k: sum(r["close"][k] for r in mine) for k in mine[0]["close"]}
                    table.setdefault(stream, {}).setdefault(det, {}).setdefault(trained_on, {})[
                        test_set] = dict(
                        mean_f1=float(np.mean([r["f1"] for r in mine])),
                        f1={r["regime"]: r["f1"] for r in mine},
                        recall={r["regime"]: r["recall"] for r in mine},
                        precision={r["regime"]: r["precision"] for r in mine},
                        null_per_hour=next((r["null_per_hour"] for r in mine
                                            if "null_per_hour" in r), None),
                        close_pairs=close["n_pairs"],
                        close_split_share=(close["n_split"] / close["n_pairs"]
                                           if close["n_pairs"] else None),
                        isolated=close["n_isolated"],
                        isolated_double_share=(close["n_isolated_double"] / close["n_isolated"]
                                               if close["n_isolated"] else None))

    a.out.mkdir(parents=True, exist_ok=True)
    record = dict(tool="tools/cross_score_sets.py", spacing="realistic", close_separation_sec=CLOSE_SEC,
                  seeds_per_background=a.seeds, sets_without_a_search=without,
                  sets={n: bench_sets.record(n)["recordings"] for ns in by_stream.values() for n in ns},
                  datasets={n: bench_sets.record(n)["dataset"] for ns in by_stream.values() for n in ns},
                  settings=settings, table=table, elapsed_min=round((time.time() - t0) / 60, 1))
    (a.out / "cross_score.json").write_text(json.dumps(record, indent=1) + "\n", encoding="utf-8")

    for stream, by_det in table.items():
        sets = by_stream[stream]
        print(f"\n{stream}: mean F1 (share of 1 s pairs split) — rows: where the setting was "
              f"tuned; columns: the set it is scored on")
        print(f"  {'detector':14s} {'tuned on':14s} " + " ".join(f"{s:>22s}" for s in sets))
        for det, by_train in by_det.items():
            for trained_on, by_test in by_train.items():
                cells = []
                for s in sets:
                    c = by_test.get(s)
                    split = "-" if c is None or c["close_split_share"] is None \
                        else f"{c['close_split_share']:.2f}"
                    cells.append(f"{'':>22s}" if c is None else f"{c['mean_f1']:14.3f} ({split:>4s})")
                print(f"  {det:14s} {trained_on:14s} " + " ".join(cells))
    print(f"\nwrote {a.out / 'cross_score.json'} in {record['elapsed_min']} min")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
