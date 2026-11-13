"""Aim 1a at the lab's own values: the joint fit on each stream's measured regime.

Goal page: docs/goals/synthetic-validation.md, plan item 1 ("add the lab's regime to the Aim 1a
grid and rerun the joint fit"). Synthetic only; no recording is read.

**The conditions are not typed here.** Cells, participants, jitter and both backgrounds come from
`bugarach.stream_profile` (ADR-0020), which reads the three benches, so this script and the
detector searches are centred on the same measured values and a re-measured bench moves both.

What is the same as `aim1_one_source.py`: one source, a fresh random set of cells per event, one
participation level per recording, a flat background, events at least 20 s apart, 45 min, the
coordination-rates tool at 1, 2 and 4 s, one seed per recording. What differs: the values, and
that the joint fit (`theory.fit_joint`, hard-core form) is run on every recording here and not
on condition medians.

    PYTHONPATH=src python docs/learned/synthetic_validation/aim1_lab_regime.py [--quick]
"""

from __future__ import annotations

import argparse
import itertools
import json
import sys
import time
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "tools"))
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(HERE))

N_EVENTS = (15, 45)         # coordinated events per recording, as in Aim 1a
SEEDS = (0, 1, 2, 3, 4)
MIN_SEP = 20.0              # s, as in Aim 1a: the hard-core form of the fit assumes it


def conditions():
    """(stream, regime, level, N, k, sigma, b, duration) for every stream profile."""
    from bugarach import stream_profile as sp

    out = []
    for stream, p in sp.profiles().items():
        for regime in p.regimes:
            src = p.source(regime)
            for level, k in enumerate(src.participants):
                out.append(dict(stream=stream, regime=regime, level=level, n_cells=src.n_cells,
                                k=k, sigma=src.jitter_sec, bg=src.bg_rate_hz,
                                duration=src.duration_sec))
    return out


def cell(args):
    idx, c, n_ev, seed = args
    import measure_coordination_rates as mcr
    import theory
    from bugarach.simulate import simulate_coordination

    N, T = c["n_cells"], c["duration"]
    s, gt = simulate_coordination(
        duration_sec=T, n_roi=N, bg_rate_hz=c["bg"], participation=(c["k"] / N,),
        n_per_level=(n_ev,), jitter_sec=c["sigma"], min_sep_sec=MIN_SEP, grid_sec=mcr.DT,
        seed=50000 + 100 * idx + seed)
    st = next(iter(s.streams.values()))
    L = int(round(T / mcr.DT))
    trains = [np.minimum(mcr._frames(np.asarray(t), 0.0, T), L - 1) for t in st.t50rise]
    m = mcr.measure(trains, L, np.random.RandomState(11 + 100 * idx + seed))
    cum = {str(w): dict(f2=float(v["f2"]), f3=float(v["f3"])) for w, v in m["cum"].items()}
    fit = theory.fit_joint(cum, N)
    return dict(cond=idx, n_events=n_ev, seed=seed, true=mcr.truth(gt, N, T), cum=cum, fit=fit)


def summarise(conds, rows):
    """Median recovered / planted per stream and participation level, over regime, E and seed."""
    out = []
    for stream, level in sorted({(c["stream"], c["level"]) for c in conds},
                                key=lambda x: (("fast", "slow", "combined").index(x[0]), x[1])):
        idxs = [i for i, c in enumerate(conds) if (c["stream"], c["level"]) == (stream, level)]
        c0 = conds[idxs[0]]
        got = [r for r in rows if r["cond"] in idxs]
        fits = [r for r in got if r["fit"] is not None]
        free = [r for r in fits if not r["fit"]["at_bound"]]

        def ratio(key, true_of):
            v = [r["fit"][key] / true_of(r) for r in free]
            return (None if not v else
                    [float(np.median(v)), float(np.percentile(v, 25)), float(np.percentile(v, 75))])

        out.append(dict(
            stream=stream, level=level, participants_planted=c0["k"], jitter_planted=c0["sigma"],
            recordings=len(got), no_fit=len(got) - len(fits), at_bound=len(fits) - len(free),
            jitter_ratio=ratio("sigma", lambda r: c0["sigma"]),
            participants_ratio=ratio("k", lambda r: r["true"]["k"]),
            rate_ratio=ratio("lam", lambda r: r["true"]["lam"])))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--quick", action="store_true", help="one seed, 15 events: a smoke run")
    ap.add_argument("--workers", type=int, default=12)
    a = ap.parse_args()
    from bugarach import stream_profile as sp

    conds = conditions()
    seeds, n_events = (SEEDS[:1], N_EVENTS[:1]) if a.quick else (SEEDS, N_EVENTS)
    grid = [(i, c, e, s) for (i, c), e, s in itertools.product(enumerate(conds), n_events, seeds)]
    t0 = time.time()
    with ProcessPoolExecutor(a.workers) as ex:
        rows = list(ex.map(cell, grid))
    print(f"{len(rows)} recordings in {time.time() - t0:.0f} s", file=sys.stderr)
    rec = dict(what="Aim 1a at each stream's measured regime: the joint fit, per recording",
               conditions_from="bugarach.stream_profile (the three benches); none typed here",
               profiles={s: p.summary() for s, p in sp.profiles().items()},
               generator="one source, random membership, one participation level per recording, "
                         "flat background, events >= 20 s apart",
               seeding="per recording: 50000 + 100 * condition index + seed",
               min_sep_sec=MIN_SEP, quick=a.quick, conditions=conds, rows=rows,
               summary=summarise(conds, rows))
    name = "aim1_lab_regime_quick.json" if a.quick else "aim1_lab_regime.json"
    (HERE / name).write_text(json.dumps(rec, indent=1, default=float), encoding="utf-8")
    for r in rec["summary"]:
        print(json.dumps(r), file=sys.stderr)
    print(HERE / name, file=sys.stderr)


if __name__ == "__main__":
    main()
