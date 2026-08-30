#!/usr/bin/env python3
"""Calibrate the six and train the learned models on the SAME simulated data,
then score them on recordings none of them was allowed to see.

    python tools/fair_bakeoff.py --spec docs/learned/generator_spec.json \
        --out docs/learned [--folds 4] [--quick]

**One data set, unless you ask for two.** `--score-spec` generates the held-out
fold from a SECOND generator spec while everything stays fitted on the first —
the cross-corpus transfer test, and the only supported way to ask whether a
detector tuned on one preparation works on another. It is off by default and the
default path is unchanged.

Every complaint the 2026-08-16 murderboard made about the previous comparison was
a fairness complaint, and each one is answered by construction here rather than by
a caveat in the prose.

**One data set.** Every detector sees recordings generated from one spec at one set
of seeds. Nothing is tuned on one distribution and scored on another.

**One selection procedure.** Each detector — hand-written or learned — gets its
operating point chosen on a CALIBRATION fold and is scored on a HELD-OUT fold it
never touched. Previously the six were calibrated on the same three recordings
their "at home" number was reported on while the learned models used held-out
seeds, so one side of the comparison was an in-sample optimum and the other was
not. Ported from `optimize_detectors.m`, which keeps per-(config, seed) counts for
exactly this and calls it out in a comment as enabling leave-one-out.

**One scoring rule.** Everything pools through `bench.pool_scores`.

**Intervals, not rankings.** Every number is reported across folds with its spread.
The previous report ranked seven detectors over a total F1 spread of 0.011 on 45
events — about half of one event — and called it an ordering.

**The probe is reported, not hidden.** Firings in the dense-but-random block are
excluded from precision (they would otherwise measure how hard the probe was set)
and reported as their own rate, so promiscuity is visible instead of invisible.

**Cost is a result, not a footnote.** A model that is going to be retrained inside
an app on a lab's own data is chosen on time-to-train, time-to-detect and size as
much as on F1. All three are measured here on the same machine in the same run.
"""

from __future__ import annotations

import argparse
import json
import platform
import statistics
import sys
import time
from pathlib import Path

import numpy as np

LEARNED = ("tube", "tube_guard", "tube_ratio", "tube_ratio_guard", "trace", "tiny")
LR = {"tube": 1e-2, "trace": 1e-3, "tiny": 1e-3,
      # THE 2x2 RUNS AT THE CONTROL'S LEARNING RATE, DELIBERATELY. `tube`'s 1e-2 is
      # what every published tube number was fitted under, and the three variants
      # differ from it by a kernel change alone. Tuning lr per variant would confound
      # the mechanism with its optimisation -- the mistake `model_track.md` already
      # records against the per-cell architecture, which "trains at a tenth the
      # learning rate of the model that works, so the comparison is uncontrolled."
      "tube_guard": 1e-2, "tube_ratio": 1e-2, "tube_ratio_guard": 1e-2}


def _rows(r, *, folds_note=None) -> dict:
    return dict(f1=r.f1, recall=r.recall, precision=r.precision,
                n_planted=r.n_planted, n_hit=r.n_hit,
                n_detected=r.n_detected, n_scored=r.n_scored,
                hot_fa=r.hot_fa, distractor_hits=r.distractor_hits,
                by_frac={f"{f:g}": r.recall_at(f) for f in sorted(r.by_frac)})


def _spread(vals: list[float]) -> dict:
    v = [x for x in vals if x is not None and np.isfinite(x)]
    if not v:
        return dict(n=0, mean=None, sd=None, min=None, max=None)
    return dict(n=len(v), mean=float(np.mean(v)),
                sd=float(statistics.stdev(v)) if len(v) > 1 else 0.0,
                min=float(min(v)), max=float(max(v)))


def _make_recording(spec: dict, seed: int):
    from bugarach.simulate import simulate_coordination
    return simulate_coordination(seed=seed, **spec)


def _timed_detect(fn, slices) -> tuple[list, float]:
    """Run a detector over recordings and return (detections, wall seconds)."""
    out, t0 = [], time.perf_counter()
    for s in slices:
        out.append(fn(s))
    return out, time.perf_counter() - t0


def run(spec: dict, *, folds: int, seeds_per_fold: int, quick: bool,
        train_seed: int = 0, score_spec: dict | None = None) -> dict:
    from bugarach import provenance
    from bugarach.bench import (DETECTORS, OPERATING_POINTS, fold_split,
                                pool_scores, run_detector)
    from bugarach.learn.nets import ARCHITECTURES
    from bugarach.learn.train import fold_maker, train
    from bugarach.score import score_stream

    # ---- the data: two corpora, or the same one twice -----------------------
    # The split comes from bench so that the browser, which runs the same
    # comparison on its own generated data, divides it the same way.
    #
    # THE SECOND CORPUS IS THE WHOLE POINT OF `score_spec`. Every operating
    # point here -- the six detectors' knob, the learned models' weights AND
    # their threshold -- is chosen on `spec`; the held-out fold is generated
    # from `score_spec`. Left unset the two are the same object and this file
    # behaves exactly as it did before, which `test_fair_bakeoff_transfer.py`
    # checks rather than asserts.
    #
    # Why it is two generators and not two folders. Their corpus has no ground
    # truth and cannot supply one: it is binarised, `time_sec` is a rising edge
    # rather than a t50rise, and their own PROVENANCE.md says coincidence within
    # a tolerance is not recoverable from those files. So a cross-corpus number
    # is not an F1 on their recordings -- RESET section 10 reserves that word for
    # planted events -- it is an F1 on a simulation parameterised from THEIR
    # measured statistics. The `[cossart]` role in `current_export.toml` carries
    # the same warning, including that their K is not ours to transplant.
    n_folds = folds
    split = fold_split(n_folds=n_folds, seeds_per_fold=seeds_per_fold)
    all_seeds = list(split.seeds)
    transfer = score_spec is not None and score_spec != spec
    print(f"data set: {len(all_seeds)} recordings, {n_folds} folds "
          f"({seeds_per_fold} each)")
    if transfer:
        print("  TRANSFER: fitted on --spec, scored on --score-spec. "
              "The held-out fold is a different generator, not a different seed.")

    fit_cache: dict[int, tuple] = {}
    score_cache: dict[int, tuple] = {}

    def rec(seed):
        """The FITTING corpus. Calibration, training and threshold-picking only."""
        if seed not in fit_cache:
            fit_cache[seed] = _make_recording(spec, seed)
        return fit_cache[seed]

    def rec_scored(seed):
        """The SCORED corpus. Reached only from a held-out fold."""
        if not transfer:
            return rec(seed)
        if seed not in score_cache:
            score_cache[seed] = _make_recording(score_spec, seed)
        return score_cache[seed]

    for s in all_seeds:                       # generate once, up front
        rec(s)
        if transfer:
            rec_scored(s)
    total_sec = sum(r[1].params["duration_sec"] for r in fit_cache.values())
    print(f"  {total_sec / 60:.0f} recording-minutes total")
    if transfer:
        scored_sec = sum(r[1].params["duration_sec"]
                         for r in score_cache.values())
        print(f"  {scored_sec / 60:.0f} recording-minutes in the scored corpus")

    # WHAT PRODUCED THIS FILE, IN THE FILE. Until 2026-08-29 this artifact carried
    # `machine` and nothing else, so a reader holding only the JSON could not say
    # which library version, which commit, or which grids produced the numbers --
    # the answer lived in `docs/learned/bakeoff.md`'s prose, which is excellent and
    # is one rename away from leaving the data unattributable. Tony asked what
    # generated it and the file could not answer; this is that gap closed.
    #
    # `machine` is kept unchanged because older files carry it and readers key on
    # it. Everything new lands under `provenance`, so nothing that reads this file
    # today has to change.
    #
    # The grids are recorded as **swept on this run**, not as whatever `bench` says
    # when someone later reads it: a stale grid recorded here would be worse than
    # no grid at all, because it would look like evidence.
    out: dict = {
        "spec": spec, "folds": n_folds, "seeds_per_fold": seeds_per_fold,
        "train_seed": train_seed,
        "score_spec": score_spec if transfer else None,
        "transfer": transfer,
        "seeds": all_seeds,
        "machine": {"platform": platform.platform(),
                    "python": platform.python_version()},
        "provenance": provenance.stamp(
            produced_by="tools/fair_bakeoff.py",
            quick=quick,
            detectors_swept={
                det: {"knob": OPERATING_POINTS[det].knob,
                      "grid": list(OPERATING_POINTS[det].grid if not quick
                                   else OPERATING_POINTS[det].grid[::2])}
                for det in DETECTORS},
            # BOTH LISTS, BECAUSE THEY ARE DIFFERENT FACTS AND THEY DRIFT APART.
            # `registered` is read from the `@register` registry, so an
            # architecture added by one `@register` line appears here without
            # anybody editing this tool. `ran` is what this run actually swept.
            # Recording only `ran` would make an architecture that exists but was
            # skipped indistinguishable from one that does not exist — which is
            # the same "a finding and a bug must not look alike" rule `run.json`'s
            # roster is built on.
            learned_architectures={
                "registered": sorted(ARCHITECTURES),
                "ran": {name: {"lr": LR.get(name)} for name in LEARNED},
                "registered_but_not_run": sorted(set(ARCHITECTURES) - set(LEARNED)),
            },
        ),
        "hand_written": {}, "learned": {},
    }

    # ---- the six: calibrate on train folds, score on the held-out fold ------
    for det in DETECTORS:
        op = OPERATING_POINTS[det]
        grid = op.grid if not quick else op.grid[::2]
        per_fold = []
        cal_sec_total = 0.0
        for held in range(n_folds):
            tr_seeds = list(split.train(held))
            te_seeds = list(split.test(held))

            # calibrate: F1-optimal knob on the training folds only
            t0 = time.perf_counter()
            best_v, best_f1 = None, -1.0
            for v in grid:
                scs = []
                for sd in tr_seeds:
                    sl, gt = rec(sd)
                    scs.append(score_stream(
                        gt, run_detector(det, sl, **{op.knob: v})))
                p = pool_scores(scs, detector=det, regime="cal", seeds=tr_seeds)
                if np.isfinite(p.f1) and p.f1 > best_f1:
                    best_f1, best_v = p.f1, v
            cal_sec = time.perf_counter() - t0
            cal_sec_total += cal_sec

            # score: held-out fold, knob carried over unchanged. Under transfer
            # the knob crosses a corpus boundary as well as a fold boundary,
            # which is the quantity being measured -- `min_rois` fitted where
            # the median field is 34 cells, applied where it is 566.
            te_slices = [rec_scored(sd) for sd in te_seeds]
            dets, det_sec = _timed_detect(
                lambda sg: run_detector(det, sg[0], **{op.knob: best_v}),
                te_slices)
            scs = [score_stream(gt, d) for (sl, gt), d in zip(te_slices, dets)]
            p = pool_scores(scs, detector=det, regime="heldout", seeds=te_seeds)
            te_sec = sum(gt.params["duration_sec"] for _, gt in te_slices)
            per_fold.append(dict(_rows(p), fold=held, knob=op.knob,
                                 knob_value=best_v, calibrate_sec=cal_sec,
                                 detect_sec=det_sec,
                                 detect_x_realtime=te_sec / max(det_sec, 1e-9)))
            print(f"  {det:7} fold {held}: F1 {p.f1:.3f}  @{op.knob}={best_v:g}"
                  f"  cal {cal_sec:.1f}s  detect {det_sec:.2f}s")

        out["hand_written"][det] = {
            "per_fold": per_fold,
            "f1": _spread([f["f1"] for f in per_fold]),
            "recall": _spread([f["recall"] for f in per_fold]),
            "precision": _spread([f["precision"] for f in per_fold]),
            "calibrate_sec": _spread([f["calibrate_sec"] for f in per_fold]),
            "detect_sec": _spread([f["detect_sec"] for f in per_fold]),
            "detect_x_realtime": _spread([f["detect_x_realtime"]
                                          for f in per_fold]),
            "hot_fa": _spread([f["hot_fa"] for f in per_fold]),
            "n_params": 0,
            "grid_points": len(grid),
        }

    # ---- the learned models: train on train folds, score on the held-out ----
    for name in LEARNED:
        per_fold = []
        for held in range(n_folds):
            tr_seeds = list(split.train(held))
            te_seeds = list(split.test(held))

            # `fold_maker` splits the TRAINING folds again so the operating point
            # is picked on recordings the fit never saw. The maker here used to be
            # an index by seed-modulo-length, which handed `pick_threshold` the
            # very recordings it had just fitted on and silently defeated the
            # seed separation that function asserts. SAP010 blocks that shape.
            mk, n_fit, _ = fold_maker(rec, tr_seeds)
            t0 = time.perf_counter()
            # THE SEED AXIS. `train_seed` is the torch seed, and it is threaded here
            # so a caller can repeat the SAME fold with a different draw. Without it
            # every learned number in this repo is one training run per fold and the
            # only spread reported is across FOLDS -- which is a property of the data
            # split, not of the optimiser. The tube's headline is a 0.017 gap inside a
            # 0.061 fold spread, so a variant that moves F1 by less than that has
            # demonstrated nothing until this axis is populated.
            tr = train(name, mk, n_train=min(10, n_fit),
                       steps=300 if quick else 900, crop=4096, batch=3,
                       lr=LR[name], seed=train_seed)
            train_sec = time.perf_counter() - t0

            # `mk` above closes over `rec`, so BOTH the weights and the
            # threshold `pick_threshold` chooses come from the fitting corpus.
            # Nothing about the scored corpus is visible to the fit -- which is
            # what makes the number below a transfer penalty rather than a
            # domain adaptation.
            te_slices = [rec_scored(sd) for sd in te_seeds]
            dets, det_sec = _timed_detect(lambda sg: tr.predict(sg[0])[0],
                                          te_slices)
            scs = [score_stream(gt, d) for (sl, gt), d in zip(te_slices, dets)]
            p = pool_scores(scs, detector=name, regime="heldout",
                            seeds=te_seeds)
            te_sec = sum(gt.params["duration_sec"] for _, gt in te_slices)
            per_fold.append(dict(_rows(p), fold=held, threshold=float(tr.threshold),
                                 train_sec=train_sec, detect_sec=det_sec,
                                 detect_x_realtime=te_sec / max(det_sec, 1e-9),
                                 n_params=int(tr.n_params)))
            print(f"  {name:7} fold {held}: F1 {p.f1:.3f}  thr {tr.threshold:.4f}"
                  f"  train {train_sec:.1f}s  detect {det_sec:.2f}s")

        out["learned"][name] = {
            "per_fold": per_fold,
            "f1": _spread([f["f1"] for f in per_fold]),
            "recall": _spread([f["recall"] for f in per_fold]),
            "precision": _spread([f["precision"] for f in per_fold]),
            "train_sec": _spread([f["train_sec"] for f in per_fold]),
            "detect_sec": _spread([f["detect_sec"] for f in per_fold]),
            "detect_x_realtime": _spread([f["detect_x_realtime"]
                                          for f in per_fold]),
            "hot_fa": _spread([f["hot_fa"] for f in per_fold]),
            "n_params": per_fold[0]["n_params"],
            "grid_points": None,
        }
    return out


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--spec", type=Path, required=True,
                   help="generator kwargs JSON from tools/derive_spec.py. "
                        "EVERYTHING IS FITTED ON THIS: the six detectors' knob, "
                        "the learned models' weights, and their threshold.")
    p.add_argument("--score-spec", type=Path, default=None,
                   help="a SECOND generator spec to score the held-out fold on, "
                        "for the cross-corpus transfer test. Omit and the "
                        "held-out fold comes from --spec, which is the ordinary "
                        "bake-off and is bit-identical to it. Give a spec derived "
                        "from another lab's folder and the number that comes back "
                        "is the transfer penalty: nothing about this corpus is "
                        "visible to the fit.")
    p.add_argument("--out", type=Path, required=True)
    p.add_argument("--folds", type=int, default=4)
    p.add_argument("--seeds-per-fold", type=int, default=2)
    p.add_argument("--quick", action="store_true",
                   help="coarser grids and shorter training, for a smoke run")
    p.add_argument("--train-seed", type=int, default=0,
                   help="torch seed for the learned fits. Vary it across otherwise "
                        "identical runs to replicate each fold and get an error bar "
                        "on the OPTIMISER, not just on the data split.")
    a = p.parse_args(argv)

    spec = json.loads(a.spec.read_text())["generator"]
    score_spec = (json.loads(a.score_spec.read_text())["generator"]
                  if a.score_spec else None)
    a.out.mkdir(parents=True, exist_ok=True)
    res = run(spec, folds=a.folds, seeds_per_fold=a.seeds_per_fold,
              quick=a.quick, train_seed=a.train_seed, score_spec=score_spec)
    stem = "bakeoff_quick" if a.quick else "bakeoff"
    if res["transfer"]:
        # The file name has to carry BOTH corpora. A transfer result filed as
        # `bakeoff.json` is a number about somebody else's data wearing the name
        # of the home result, and this project has already paid once for a figure
        # that could not be told apart from the one it superseded.
        stem = f"{stem}_{a.spec.stem}_to_{a.score_spec.stem}"
    if a.train_seed:
        stem = f"{stem}_seed{a.train_seed}"
    f = a.out / f"{stem}.json"
    f.write_text(json.dumps(res, indent=1, sort_keys=True))
    print(f"\nwrote {f}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
