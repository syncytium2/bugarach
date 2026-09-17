"""Differential cases for the rate+context step-by-step page (docs/detectors/rate_context_steps.md).

`rate_from_page.py` beside this file was written by an agent that saw ONLY that page, with its code links
removed. Every case here runs it and the real `bugarach.detectors.rate.rate_detect` on the same input and
settings; any difference in calls means the page is missing or misstating a rule.

Cases aim at the rules a reader could get wrong:
  * simulated bench recordings on both backgrounds (the path the page describes in the large);
  * recordings shorter than the context window, so the 90% clip applies;
  * lengths that are not a whole number of grid steps, so the last slot ends before t_hi;
  * events exactly on slot boundaries, and outside [t_lo, t_hi];
  * zero, one and two neurons; no events;
  * bursts spaced near the merge gap, and single-moment crossings;
  * other settings than the stored ones, so a rule cannot pass by matching one number.
"""
from __future__ import annotations

import numpy as np

STORED = dict(grid_dt=0.1, rate_win=1.0, context_win=60.0, excess_threshold=4.5, merge_gap=3.0, pad=0.5)
VARIANTS = (
    STORED,
    dict(STORED, excess_threshold=1.5, merge_gap=1.0),
    dict(STORED, rate_win=2.0, context_win=20.0, excess_threshold=3.0),
    dict(STORED, rate_win=0.5, context_win=45.3, merge_gap=0.0),
)


def real_calls(trains, t_lo, t_hi, p):
    """The program itself, called the way the page describes: events clipped to [t_lo, t_hi]."""
    from bugarach.detectors.rate import rate_detect
    clipped = []
    for v in trains:
        v = np.asarray(v, dtype=float).ravel()
        v = v[np.isfinite(v)]
        clipped.append(v[(v >= t_lo) & (v <= t_hi)])
    r = rate_detect(clipped, (t_lo, t_hi), grid_dt=p["grid_dt"], excess_threshold_hz=p["excess_threshold"],
                    merge_gap_s=p["merge_gap"], rate_win=p["rate_win"], context_win=p["context_win"])
    return np.asarray(r.locs, float), np.asarray(r.widths, float)


def bench_cases(seeds=(1, 2, 3)):
    from bugarach import bench
    from bugarach.detectors.rate import recording_extent
    for regime in ("baseline_quiet", "baseline_busy"):
        for seed in seeds:
            s, _ = bench.make_recording(regime, seed)
            t_lo, t_hi = recording_extent(s)
            trains = [np.asarray(v, float) for v in s.streams[bench.STREAM].t50rise]
            yield f"bench:{regime}:{seed}", trains, t_lo, t_hi


def random_cases(n=300, seed=20260916):
    rng = np.random.default_rng(seed)
    for i in range(n):
        n_neurons = int(rng.choice([0, 1, 2, 3, 5, 12, 30]))
        t_lo = float(rng.choice([0.0, 3.7, 12.345, 1000.05]))
        kind = rng.integers(4)
        if kind == 0:
            dur = float(rng.uniform(0.3, 15.0))                        # context clipped to 90%
        elif kind == 1:
            dur = float(rng.integers(5, 2000)) / 10.0                  # whole number of steps
        elif kind == 2:
            dur = float(rng.integers(5, 2000)) / 10.0 + float(rng.uniform(0.001, 0.099))
        else:
            dur = float(rng.uniform(60.0, 400.0))
        t_hi = t_lo + dur
        rate = float(rng.choice([0.02, 0.2, 1.0, 3.0]))
        trains = []
        for _ in range(n_neurons):
            k = rng.poisson(rate * dur)
            trains.append(rng.uniform(t_lo - 2.0, t_hi + 2.0, k))      # some fall outside the recording
        if n_neurons and dur > 2:
            # bursts: many neurons within a fraction of a second, some spaced near the merge gap
            n_b = int(rng.integers(0, 6))
            centres = t_lo + rng.uniform(1, dur - 1, n_b)
            if n_b >= 2 and rng.random() < 0.5:
                centres[1] = centres[0] + float(rng.choice([2.9, 3.0, 3.1, 1.0, 0.1]))
            for c in centres:
                for j in range(n_neurons):
                    if rng.random() < 0.7:
                        trains[j] = np.append(trains[j], c + rng.normal(0, 0.15))
        if n_neurons and rng.random() < 0.3:
            # events exactly on slot boundaries: t_lo + k*0.1 +- 0.05
            k = rng.integers(0, max(1, int(dur * 10)), 10)
            edges = t_lo + k * 0.1 + rng.choice([-0.05, 0.05], 10)
            j = int(rng.integers(n_neurons))
            trains[j] = np.append(trains[j], edges)
        yield f"random:{i}", [np.sort(v) for v in trains], t_lo, t_hi


def compare(impl, cases, variants=VARIANTS, atol=1e-9):
    """Run every case under every settings variant; return a list of mismatches (empty = agreement)."""
    bad = []
    n = 0
    for name, trains, t_lo, t_hi in cases:
        for vi, p in enumerate(variants):
            n += 1
            ro, rw = real_calls(trains, t_lo, t_hi, p)
            po, pw = impl([np.asarray(v, float) for v in trains], t_lo, t_hi, **p)
            po, pw = np.asarray(po, float), np.asarray(pw, float)
            if ro.shape != po.shape or not (np.allclose(ro, po, atol=atol, rtol=0)
                                            and np.allclose(rw, pw, atol=atol, rtol=0)):
                bad.append(dict(case=name, variant=vi, real=list(zip(ro.round(6), rw.round(6)))[:6],
                                page=list(zip(po.round(6), pw.round(6)))[:6], n_real=int(ro.size),
                                n_page=int(po.size)))
    return bad, n
