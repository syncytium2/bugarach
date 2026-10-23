"""Re-run Aim 1a's coordination-rates arm with INDEPENDENT backgrounds per cell (the record reuses
seeds 1000-1004 for every cell, so its 48 cells per background share 5 background realisations).
Stores raw excess (f2, f3) per window so the analytic model and an inverted estimator can be tested.
"""
from __future__ import annotations

import itertools
import json
import sys
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "tools"))
N, T = 33, 2700.0
JITS, PARTS, NEVS, BGS = (0.05, 0.2, 0.5, 1.0), (0.15, 0.3, 0.6), (15, 45), (0.01, 0.05)
WINDOWS = (0.5, 1.0, 2.0, 4.0, 8.0)
NSEED = 10


def one(args):
    idx, (jit, part, m, bg), s = args
    import measure_coordination_rates as mcr
    from bugarach.simulate import simulate_coordination
    seed = 50_000 + 100 * idx + s
    sl, gt = simulate_coordination(duration_sec=T, n_roi=N, bg_rate_hz=bg, participation=(part,),
                                   n_per_level=(m,), jitter_sec=jit, min_sep_sec=20.0, grid_sec=0.1,
                                   seed=seed)
    st = next(iter(sl.streams.values()))
    L = int(round(T / mcr.DT))
    tr = [np.minimum(mcr._frames(np.asarray(t), 0.0, T), L - 1) for t in st.t50rise]
    rng = np.random.RandomState(seed + 7)
    cum = {}
    for w in WINDOWS:
        f2, f3 = mcr.excess_cumulants(tr, L, int(round(w / mcr.DT)), mcr.N_SURR, rng)
        cum[str(w)] = (f2, f3)
    return dict(jit=jit, part=part, m=m, bg=bg, seed=seed, k=gt.events[0].n_part, cum=cum)


def main():
    cells = list(itertools.product(JITS, PARTS, NEVS, BGS))
    jobs = [(i, c, s) for i, c in enumerate(cells) for s in range(NSEED)]
    with ProcessPoolExecutor(40) as ex:
        rows = list(ex.map(one, jobs, chunksize=4))
    (HERE / "fresh_cr.json").write_text(json.dumps(rows))
    print(len(rows))


if __name__ == "__main__":
    main()
