"""Scratch: does slow jitter 0.30 vs 0.46 s (the MATLAB summary's slow K=4 value) move the slow bench?"""
from concurrent.futures import ProcessPoolExecutor

from bugarach import bench_slow as b

SEEDS = tuple(range(1, 49))
J = (0.30, 0.46)


def run(args):
    det, j = args
    f = [b.evaluate(det, r, SEEDS, gen=dict(jitter_sec=j)).f1 for r in b.REGIMES]
    return det, j, sum(f) / 2


if __name__ == "__main__":
    with ProcessPoolExecutor(12) as ex:
        res = {(d, j): v for d, j, v in ex.map(run, [(d, j) for d in b.DETECTORS for j in J])}
    for d in b.DETECTORS:
        print(f"{d:7s} jitter 0.30: {res[(d, 0.30)]:.3f}   0.46: {res[(d, 0.46)]:.3f}   "
              f"change {res[(d, 0.46)] - res[(d, 0.30)]:+.3f}")
