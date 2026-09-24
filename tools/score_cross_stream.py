#!/usr/bin/env python3
"""Each stream's version of each detector, scored on all three benches: the 3 x 3.

    python tools/score_cross_stream.py --models <phase2 folder> --out <folder> [--workers 24]

**Why.** Tony, 2026-09-23 and again 2026-09-24: *"Add to each table the performance across fast
slow and combined."* Every detector has three versions, one per stream (fast, slow, combined),
tuned or trained on that stream's bench. This scores every version on every bench, so each detector
gets a 3 x 3 of *tuned on* x *scored on*.

**The versions**, read from last night's two ``candidates.json`` run records:

* the six coded detectors at each bench's shipped operating point and, where the search had one,
  its proposal (``docs/learned/runs/2026-09-24-overnight-coact-chorus/`` for CoactDetect,
  ``.../2026-09-24-overnight-rest-of-suite/`` for the other five);
* ``chorus_norm`` and ``chorus_gain_norm`` at the seed each training run picked.

**How a version runs on another stream's bench.** A coded detector's version is its tuned-on bench's
operating point with the tuned settings over it, run through **the tuned-on bench's**
``run_detector`` on the scored-on bench's recording. Running it through the scored-on bench instead
would fill every setting the version leaves undeclared from the *other* stream's operating point
(slow CoactDetect's ``min_rois=6`` into a fast version), which is not the fast version. A chorus
checkpoint is run as saved. Every bench recording is the same shape, one ``events`` stream at 0.1 s,
32 ROIs, 2,700 s, and a checkpoint's input is a binary onset raster under one encoding contract,
so every cell runs as-is; a cell that raised would be recorded as "not runnable as-is" with its
error, never adapted.

**Scoring** is ``tools/score_bench_candidates.py``'s: seeds 6000–6023 per background, 56000–56011
for the no-coordination recording, F1 as scored and with decoy calls left out of precision
(ADR-0006). Each F1 carries a **bootstrap 95% interval over seeds**: each background's 24 seeds
resampled with replacement, scores pooled, the mean over the two backgrounds taken, 2,000 times.
The diagonal (a version scored on its own bench) must reproduce ``candidates.json`` exactly, and
``diagonal_check`` in the output says whether it does.

**Floor: pre-ADR-0008**, as the versions were tuned (``min_rois`` never below 3).
"""
from __future__ import annotations

import argparse
import importlib
import json
import multiprocessing as mp
import sys
from pathlib import Path

import numpy as np

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))
sys.path.insert(0, str(REPO / "tools"))

from score_bench_candidates import BENCHES, NULLS, REG, SEEDS  # noqa: E402

RUNS = REPO / "docs" / "learned" / "runs"
PHASE2 = RUNS / "2026-09-24-overnight-coact-chorus" / "candidates.json"
PHASE4 = RUNS / "2026-09-24-overnight-rest-of-suite" / "candidates.json"
STREAMS = tuple(BENCHES)
CODED = ("coact", "loco", "sce", "rate", "sync", "cicada")
CHORUS = ("chorus_norm", "chorus_gain_norm")
NAME = {"coact": "CoactDetect", "loco": "LoCo", "sce": "SCE", "rate": "rate+context",
        "sync": "SPIKE-synch", "cicada": "locust", "chorus_norm": "chorus_norm",
        "chorus_gain_norm": "chorus_gain_norm"}
N_BOOT = 2000
_MODELS: dict = {}


def versions(models: Path) -> list[dict]:
    """Every (detector, variant, tuned-on bench) version with what it needs to run, and the
    ``candidates.json`` row its diagonal must reproduce."""
    p2 = json.loads(PHASE2.read_text())
    p4 = json.loads(PHASE4.read_text())
    out = []
    for tuned in STREAMS:
        B2, B4 = p2["benches"][tuned], p4["benches"][tuned]
        coded = {"coact": dict(shipped=B2["coact_shipped"], proposal=B2["coact_proposal"])}
        for d, M in B4["detectors"].items():
            coded[d] = M
        for d in CODED:
            M = coded[d]
            src = p2 if d == "coact" else p4
            out.append(dict(det=d, variant="shipped", tuned=tuned, kind="coded",
                            spec=M["shipped"], reference=src["results"][tuned][f"{d}:shipped"]))
            if M["proposal"]["name"] != "shipped":
                out.append(dict(det=d, variant="proposal", tuned=tuned, kind="coded",
                                spec=M["proposal"]["params"],
                                reference=src["results"][tuned][f"{d}:proposal"]))
        for m in CHORUS:
            pick = B2["chorus"][m]["picked"]
            out.append(dict(det=m, variant=pick.split("_")[-1].replace(".json", ""), tuned=tuned,
                            kind="chorus", spec=str(models / f"models-{tuned}" / pick),
                            reference=p2["results"][tuned][f"chorus:{pick}"]))
    return out


def chosen(vs: list[dict], det: str, tuned: str) -> dict:
    """The version a detector's tuned-on bench settled on: the proposal where there is one."""
    c = [v for v in vs if v["det"] == det and v["tuned"] == tuned]
    return next((v for v in c if v["variant"] == "proposal"), c[0])


def job(args):
    vi, v, scored, regime, seed = args
    from bugarach.score import score_stream
    sb = importlib.import_module(BENCHES[scored])
    try:
        if v["kind"] == "coded":
            tb = importlib.import_module(BENCHES[v["tuned"]])
            run = lambda sl: tb.run_detector(v["det"], sl, **v["spec"])  # noqa: E731
        else:
            if v["spec"] not in _MODELS:
                from bugarach.learn.checkpoint import load
                _MODELS[v["spec"]] = load(v["spec"])
            tr = _MODELS[v["spec"]]
            run = lambda sl: tr.predict(sl)[0]  # noqa: E731
        if regime == "null":
            sl, gt = sb.make_null_recording(seed + 50_000)
            return (vi, scored, regime, seed), dict(
                n=score_stream(gt, run(sl)).n_detected, hours=gt.params["duration_sec"] / 3600)
        sl, gt = sb.make_recording(regime, seed)
        return (vi, scored, regime, seed), score_stream(gt, run(sl))
    except Exception as e:  # noqa: BLE001 - recorded as not runnable, never adapted
        return (vi, scored, regime, seed), dict(error=f"{type(e).__name__}: {e}")


def cell(scores_by_regime, nulls, rng) -> dict:
    """Pooled F1 both ways per background, their mean, bootstrap intervals over seeds."""
    from bugarach.bench import pool_scores

    def mean_f1(idx_by_regime):
        f, g = [], []
        for reg, idx in zip(REG, idx_by_regime):
            r = pool_scores([scores_by_regime[reg][i] for i in idx], detector="x", regime=reg)
            f.append(r.f1)
            g.append(r.f1_without_decoys)
        return float(np.mean(f)), float(np.mean(g))

    n = len(SEEDS)
    full = [np.arange(n)] * len(REG)
    f1, f1_wd = mean_f1(full)
    boots = np.array([mean_f1([rng.randint(0, n, n) for _ in REG]) for _ in range(N_BOOT)])
    per_reg = {}
    for reg in REG:
        r = pool_scores(scores_by_regime[reg], detector="x", regime=reg)
        per_reg[reg] = dict(f1=r.f1, f1_without_decoys=r.f1_without_decoys, recall=r.recall,
                            precision=r.precision, decoy_calls=r.decoy_calls)
    return dict(mean_f1=f1, mean_f1_ci=np.nanpercentile(boots[:, 0], [2.5, 97.5]).tolist(),
                mean_f1_without_decoys=f1_wd,
                mean_f1_without_decoys_ci=np.nanpercentile(boots[:, 1], [2.5, 97.5]).tolist(),
                null_calls_per_hour=sum(x["n"] for x in nulls) / sum(x["hours"] for x in nulls),
                by_background=per_reg)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--models", type=Path, required=True,
                    help="last night's phase-2 folder, holding models-<bench>/")
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--workers", type=int, default=24)
    a = ap.parse_args(argv)
    a.out.mkdir(parents=True, exist_ok=True)
    vs = versions(a.models)
    jobs = [(i, v, s, reg, seed) for i, v in enumerate(vs) for s in STREAMS
            for reg in REG for seed in SEEDS]
    jobs += [(i, v, s, "null", seed) for i, v in enumerate(vs) for s in STREAMS for seed in NULLS]
    with mp.Pool(a.workers) as pool:
        got = dict(pool.map(job, jobs, chunksize=4))
    rng = np.random.RandomState(20260924)
    rows = []
    for i, v in enumerate(vs):
        for s in STREAMS:
            errs = sorted({g["error"] for k, g in got.items()
                           if k[0] == i and k[1] == s and isinstance(g, dict) and "error" in g})
            row = dict(det=v["det"], variant=v["variant"], tuned=v["tuned"], scored=s)
            if errs:
                row["not_runnable_as_is"] = errs
            else:
                sc = {reg: [got[(i, s, reg, seed)] for seed in SEEDS] for reg in REG}
                row.update(cell(sc, [got[(i, s, "null", seed)] for seed in NULLS], rng))
            rows.append(row)
    # The diagonal against last night's candidates.json, to the digit.
    diag = []
    for i, v in enumerate(vs):
        r = next(x for x in rows if x["det"] == v["det"] and x["variant"] == v["variant"]
                 and x["tuned"] == v["tuned"] and x["scored"] == v["tuned"])
        ref = v["reference"]
        ok = all(abs(r[k] - ref[k]) < 1e-12 for k in
                 ("mean_f1", "mean_f1_without_decoys", "null_calls_per_hour"))
        diag.append(dict(det=v["det"], variant=v["variant"], tuned=v["tuned"], reproduces=ok,
                         got=[r["mean_f1"], r["mean_f1_without_decoys"], r["null_calls_per_hour"]],
                         reference=[ref["mean_f1"], ref["mean_f1_without_decoys"],
                                    ref["null_calls_per_hour"]]))
    chosen_map = {d: {t: chosen(vs, d, t)["variant"] for t in STREAMS}
                  for d in (*CODED, *CHORUS)}
    rec = dict(seeds=[SEEDS[0], SEEDS[-1]], null_seeds=[NULLS[0] + 50_000, NULLS[-1] + 50_000],
               n_boot=N_BOOT, floor="pre-ADR-0008 (min_rois never below 3 when tuned)",
               chosen=chosen_map, diagonal_check=dict(all_reproduce=all(d["reproduces"]
                                                                          for d in diag),
                                                      rows=diag),
               rows=rows, names=NAME)
    (a.out / "cross_stream.json").write_text(json.dumps(rec, indent=1, default=float) + "\n")
    print(f"diagonal reproduces: {rec['diagonal_check']['all_reproduce']} "
          f"({sum(d['reproduces'] for d in diag)} of {len(diag)})")
    print(f"not runnable as-is: {sum('not_runnable_as_is' in r for r in rows)} of {len(rows)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
