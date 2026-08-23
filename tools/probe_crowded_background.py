#!/usr/bin/env python3
"""How much of the crowded recording's recall loss is crowding, and how much is
the background it is measured against?

    python tools/probe_crowded_background.py

`docs/forks.md` §4a measured the guard on `loco` and `coact` and flagged something
larger it could not explain: both detectors lose most of their recall on
``CROWDED_RECORDING`` and a guard recovers only a slice. Three candidates were
named and none separated — masking the guard does not reach, the detectors' own
episode merging, or the scorer's greedy one-to-one matching on closely spaced
events. This separates them, and found a fourth that dominated all three.

**The scorer and the merging are innocent.** An oracle emitting the exact planted
times scores F1 1.000 on the crowded recording, and no emitted span ever covers
two planted events — detection spans are 2.0 s and 0.70 s against a 19.4 s median
gap. Precision *rises* to 0.98–0.99 while the detection count falls below the
planted count: the detectors are not firing wrongly, they are silent, which is a
bar that went up.

**Most of what raised it was the background, and that was a bug.** Until
2026-08-23 :func:`~bugarach.bench.make_crowded_recording` merged no regime, so
``bg_rate_hz`` fell through to
:func:`~bugarach.simulate.simulate_coordination`'s default of 0.05 Hz — the
pre-2026-08-13 invented value, roughly 10× :data:`~bugarach.bench.REGIMES`' quiet
endpoint. It takes a regime now. The ``OFF-AXIS`` row below reconstructs the old
condition so the size of the error stays checkable, and so this tool keeps
answering the question it was written for: crowding and the background are
separate axes, and only one of them is what the recording is for.

**Read recall, not F1, across these rows.** The crowded recording plants eight
times as many events, so a detector firing at a similar rate hits far more often
and its precision rises — coact reads a *higher* F1 on the crowded recording than
on the bench while recalling a fifth less. Only the recall column compares.

The ``bg`` column subtracts planted coordinated spikes, not the promiscuity probe
block or the distractors, so the bench row reads above its nominal regime rate and
the crowded rows — which carry neither — read exactly at it.
"""

from __future__ import annotations

import numpy as np

from bugarach.bench import (BENCH_RECORDING, CROWDED_RECORDING, REGIMES,
                            make_crowded_recording, make_recording)
from bugarach.detectors.coact import coact_detect
from bugarach.detectors.loco import loco_detect
from bugarach.detectors.rate import recording_extent, stream_trains
from bugarach.score import score_detections, score_stream
from bugarach.simulate import simulate_coordination

SEEDS = (1, 2, 3, 4)
TOL = 1.5
STREAM = "events"

#: The pre-2026-08-23 crowded recording: no regime merged, so the simulator's own
#: ``bg_rate_hz`` default. A labelled control, never a call site.
OFF_AXIS = dict(CROWDED_RECORDING)


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


DETECTORS = {"coact": coact, "loco": loco}


def spans(r):
    """(lo, hi) for either field convention — see :func:`score_stream`."""
    for onset, width in (("onset_sec", "width_sec"), ("locs", "widths")):
        if hasattr(r, onset):
            lo = np.asarray(getattr(r, onset), dtype=float)
            w = getattr(r, width, None)
            hi = lo + (np.zeros_like(lo) if w is None else np.asarray(w, float))
            return lo, hi
    raise TypeError(f"{type(r).__name__} carries no detection times")


def _gap(t, lo, hi):
    return np.maximum(0.0, np.maximum(lo - t, t - hi))


def background_hz(sl, gt, cfg):
    """Realised per-ROI *background* rate — planted spikes removed."""
    trains = stream_trains(sl.streams[STREAM], recording_extent(sl))
    planted = sum(len(e.rois) for e in gt.events)
    return ((sum(len(t) for t in trains) - planted)
            / (cfg["duration_sec"] * cfg["n_roi"]))


def measure(recordings, det, guard=0.0):
    """``recordings`` maps a seed to ``(slice, ground_truth, config)``."""
    tot, hit = {}, {}
    n_det = n_hit = n_plant = covered = multi = 0
    rates = []
    for seed in SEEDS:
        sl, gt, cfg = recordings(seed)
        rates.append(background_hz(sl, gt, cfg))
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
    print(f"  {label:32s} bg {m['bg']:.4f} Hz/ROI  planted {m['planted']:4d}  "
          f"det {m['detected']:4d}  recall {m['recall']:5.3f}  "
          f"prec {m['precision']:5.3f}  |  by participation  {per}")
    if m["multi"]:
        print(f"      {m['multi']} span(s) covered >=2 planted events — "
              f"one-to-one matching cost {m['covered'] - m['recall']:+.3f} recall")


def bench_at(regime):
    def make(seed):
        sl, gt = make_recording(regime, seed)
        return sl, gt, dict(BENCH_RECORDING, **REGIMES[regime])
    return make


def crowded_at(regime):
    def make(seed):
        sl, gt = make_crowded_recording(regime, seed)
        return sl, gt, dict(CROWDED_RECORDING, **REGIMES[regime])
    return make


def crowded_off_axis(seed):
    return (*simulate_coordination(seed=seed, **OFF_AXIS), OFF_AXIS)


def oracle():
    """Can the scorer score a perfect detector on 120 events at a 14 s floor?"""
    for name, make in (("bench, quiet", bench_at("baseline_quiet")),
                       ("crowded, quiet", crowded_at("baseline_quiet"))):
        f1 = [score_detections(gt, np.asarray(gt.times, float), tol_sec=TOL).f1
              for gt in (make(s)[1] for s in SEEDS)]
        print(f"  oracle (exact planted times) on {name:16s} F1 {np.mean(f1):.3f}")


def main() -> int:
    print(f"{len(SEEDS)} seeds, shipped operating points, tol {TOL} s\n")
    print("== is the scorer the ceiling? ==")
    oracle()

    for name, det in DETECTORS.items():
        print(f"\n== {name} ==")
        for label, make, guard in (
                ("bench, quiet (as scored)", bench_at("baseline_quiet"), 0.0),
                ("crowded, quiet", crowded_at("baseline_quiet"), 0.0),
                ("crowded, quiet, guard 5 s", crowded_at("baseline_quiet"), 5.0),
                ("crowded, busy", crowded_at("baseline_busy"), 0.0),
                ("crowded, OFF-AXIS (pre-fix)", crowded_off_axis, 0.0)):
            show(label, measure(make, det, guard))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
