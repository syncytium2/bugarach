#!/usr/bin/env python3
"""How much of the crowded recording's recall collapse is crowding, and how much
is a background it was never meant to have?

    python tools/probe_crowded_background.py

`docs/forks.md` §4a measured the guard on `loco` and `coact` and flagged something
larger it could not explain: both detectors lose most of their recall on
``CROWDED_RECORDING`` — 0.70–0.83 down to 0.25–0.29 — and a guard recovers only a
slice. Three candidates were named and none separated: masking the guard does not
reach, the detectors' own episode merging, or the scorer's greedy one-to-one
matching on closely spaced events.

This separates them, and finds a fourth that dominates all three.

**The scorer and the merging are innocent.** An oracle emitting the exact planted
times scores F1 1.000 on the crowded recording, and no emitted span ever covers two
planted events — detection spans are 2.0 s and 0.70 s against a 19.4 s median gap.
Precision *rises* to 0.98–0.99 while the detection count falls below the planted
count: the detectors are not firing wrongly, they are silent, which is a bar that
went up.

**Most of what raised it is the background.** ``BENCH_RECORDING`` carries no
``bg_rate_hz`` — the rate always arrives from ``REGIMES[regime]``, which
:func:`~bugarach.bench.make_recording` merges in. :func:`make_crowded_recording`
merges no regime, so ``bg_rate_hz`` falls through to
:func:`~bugarach.simulate.simulate_coordination`'s own default of **0.05 Hz**, the
pre-2026-08-13 invented value ``BENCH_RECORDING``'s docstring names as "5× too
busy". Re-running the same recording at the quiet endpoint splits the collapse
roughly two-thirds background, one-third crowding.

See ``docs/todo/2026-08-23-the-crowded-recording-runs-off-the-difficulty-axis.md``.
"""

from __future__ import annotations

import numpy as np

from bugarach.bench import BENCH_RECORDING, CROWDED_RECORDING, REGIMES
from bugarach.detectors.coact import coact_detect
from bugarach.detectors.loco import loco_detect
from bugarach.detectors.rate import recording_extent, stream_trains
from bugarach.score import score_detections, score_stream
from bugarach.simulate import simulate_coordination

SEEDS = (1, 2, 3, 4)
TOL = 1.5
QUIET = REGIMES["baseline_quiet"]
STREAM = "events"


def coact(sl, guard=0.0):
    ext = recording_extent(sl)
    trains = stream_trains(sl.streams[STREAM], ext)
    return coact_detect(trains, ext, rng_seed=7, int_win_sec=2.0,
                        context_win_sec=60.0, alpha=1e-4, n_surrogates=100,
                        guard_sec=guard)


def loco(sl, guard=0.0):
    return loco_detect(sl, rng_seed=7, bin_width_sec=1.0, context_win_sec=120.0,
                       thr_step_sec=15.0, merge_gap_sec=2.0, threshold_pctile=99.9,
                       n_surrogates=100, guard_sec=guard).streams[STREAM]


DETECTORS = {"coact": coact, "loco ": loco}


def spans(r):
    """(lo, hi) for either field convention — see score_stream."""
    for onset, width in (("onset_sec", "width_sec"), ("locs", "widths")):
        if hasattr(r, onset):
            lo = np.asarray(getattr(r, onset), dtype=float)
            w = getattr(r, width, None)
            hi = lo + (np.zeros_like(lo) if w is None else np.asarray(w, float))
            return lo, hi
    raise TypeError(f"{type(r).__name__} carries no detection times")


def _gap(t, lo, hi):
    return np.maximum(0.0, np.maximum(lo - t, t - hi))


def background_hz(sl, cfg):
    """Realised per-ROI rate, including planted events — the honest comparison."""
    trains = stream_trains(sl.streams[STREAM], recording_extent(sl))
    return sum(len(t) for t in trains) / (cfg["duration_sec"] * cfg["n_roi"])


def measure(cfg, det, guard=0.0):
    tot, hit = {}, {}
    n_det = n_hit = n_plant = covered = multi = 0
    rates = []
    for seed in SEEDS:
        sl, gt = simulate_coordination(seed=seed, **cfg)
        rates.append(background_hz(sl, cfg))
        r = det(sl, guard)
        sc = score_stream(gt, r, tol_sec=TOL)
        n_det += sc.n_detected
        n_hit += sc.n_hit
        n_plant += len(gt.times)
        for frac, (n, h) in sc.by_frac.items():
            tot[frac] = tot.get(frac, 0) + n
            hit[frac] = hit.get(frac, 0) + h
        lo, hi = spans(r)
        t = np.asarray(gt.times, float)
        if t.size and lo.size:
            g = _gap(t[:, None], lo[None, :], hi[None, :])
            covered += int((g.min(axis=1) <= TOL).sum())
            multi += int(((g <= TOL).sum(axis=0) >= 2).sum())
    return dict(bg=float(np.mean(rates)), planted=n_plant, detected=n_det,
                recall=n_hit / n_plant, covered=covered / n_plant, multi=multi,
                precision=n_hit / n_det if n_det else float("nan"),
                by_frac={f: hit[f] / tot[f] for f in tot})


def show(label, m):
    per = "  ".join(f"{f:.2f}: {m['by_frac'][f]:.2f}"
                    for f in sorted(m["by_frac"], reverse=True))
    print(f"{label:38s} bg {m['bg']:.4f} Hz/ROI  planted {m['planted']:4d}  "
          f"det {m['detected']:4d}  recall {m['recall']:5.3f}  "
          f"precision {m['precision']:5.3f}  |  by participation  {per}")


def oracle():
    """Can the scorer score a perfect detector on 120 events at a 14 s floor?"""
    for name, cfg in (("bench, quiet", dict(BENCH_RECORDING, **QUIET)),
                      ("crowded, as shipped", CROWDED_RECORDING)):
        f1 = [score_detections(gt, np.asarray(gt.times, float), tol_sec=TOL).f1
              for gt in (simulate_coordination(seed=s, **cfg)[1] for s in SEEDS)]
        print(f"  oracle (exact planted times) on {name:22s} F1 {np.mean(f1):.3f}")


def main():
    print("== is the scorer the ceiling? ==")
    oracle()

    crowded_quiet = dict(CROWDED_RECORDING, **QUIET)
    for name, det in DETECTORS.items():
        print(f"\n== {name.strip()} ==")
        for label, cfg, guard in (
                ("bench, quiet (as scored)", dict(BENCH_RECORDING, **QUIET), 0.0),
                ("crowded, at quiet", crowded_quiet, 0.0),
                ("crowded, at quiet, guard 10 s", crowded_quiet, 10.0),
                ("crowded, AS SHIPPED (no regime)", CROWDED_RECORDING, 0.0),
                ("crowded, as shipped, guard 10 s", CROWDED_RECORDING, 10.0)):
            m = measure(cfg, det, guard)
            show(f"  {label}", m)
            if m["multi"]:
                print(f"      {m['multi']} spans covered >=2 planted events "
                      f"(one-to-one matching cost "
                      f"{m['covered'] - m['recall']:+.3f} recall)")


if __name__ == "__main__":
    main()
