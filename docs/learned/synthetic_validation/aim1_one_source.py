"""Aim 1a: one source, random membership. Plant known parameters, measure blind, compare.

Goal page: docs/goals/synthetic-validation.md. Synthetic only; no recording is read.

Each grid cell is simulated with `simulate_coordination` at one participation level, then
measured by the two tools that run on arrays in memory, neither of which is told the truth:

* `measure_coordination_rates` (no K, no event definition): participants per shared moment
  (fixed model), the moments' rate, and the coordinated share of onsets, at windows 1, 2, 4 s.
* `assess_coactivity` at K = 3, 4, 6 cells: participants (`part_n_obs`), cluster rate,
  jitter (`jit_obs`) and onset span (`span_med`).

K = 4 is the compromise `tests/test_adapt.py` measured; K is not chosen from the truth.

    PYTHONPATH=src python docs/learned/synthetic_validation/aim1_one_source.py [--quick]
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
sys.path.insert(0, str(ROOT / "tools"))
sys.path.insert(0, str(ROOT / "src"))

N_ROI = 33
DURATION = 2700.0           # s, 45 min
JITTERS = (0.05, 0.2, 0.5, 1.0)        # s, SD of onset jitter
PARTS = (0.15, 0.3, 0.6)               # fraction of cells per event
N_EVENTS = (15, 45)                    # coordinated events per recording
BG_RATES = (0.01, 0.05)                # Hz, mean background rate per cell
SEEDS = (0, 1, 2, 3, 4)
KS = (3, 4, 6)
MIN_SEP = 20.0              # s; renewal spacing, mean gap well above the windows
HERE = Path(__file__).resolve().parent


def cell(args):
    idx, (jit, part, n_ev, bg, seed) = args
    from bugarach.assess import assess_coactivity
    from bugarach.simulate import simulate_coordination
    import measure_coordination_rates as mcr

    s, gt = simulate_coordination(
        duration_sec=DURATION, n_roi=N_ROI, bg_rate_hz=bg, participation=(part,),
        n_per_level=(n_ev,), jitter_sec=jit, min_sep_sec=MIN_SEP, grid_sec=0.1,
        seed=1000 + 100 * idx + seed)   # its own background per recording (see main)
    st = next(iter(s.streams.values()))
    L = int(round(DURATION / mcr.DT))
    trains = [np.minimum(mcr._frames(np.asarray(t), 0.0, DURATION), L - 1) for t in st.t50rise]
    rng = np.random.RandomState(7 + 100 * idx + seed)
    m = mcr.measure(trains, L, rng)
    cr = {w: mcr.solve(c["f2"], c["f3"], N_ROI, float(w), "fixed") for w, c in m["cum"].items()}

    recs = assess_coactivity(s, window=(0.0, DURATION), min_rois=KS, n_surrogates=120)
    asr = {r.min_rois: dict(part=r.part_n_obs, per_min=r.clusters_permin, jit=r.jit_obs,
                            jit_defined=bool(r.jit_defined), span=r.span_med) for r in recs}

    true = mcr.truth(gt, N_ROI, DURATION)
    true.update(jitter=jit, part_frac=part, n_events=n_ev, bg_rate=bg,
                per_min=60.0 * len(gt.events) / DURATION, n_onsets=int(sum(len(t) for t in trains)))
    # The raw excess cumulants are kept as well: solve() refuses (NaN) when f2 or f3 <= 0, and a
    # fit across windows should not inherit that screen (murderboard 2026-10-23, roles 6 and 7).
    cum = {w: dict(f2=float(c["f2"]), f3=float(c["f3"])) for w, c in m["cum"].items()}
    return dict(seed=seed, cell=idx, true=true, coord_rates=cr, cum=cum,
                assess={str(k): v for k, v in asr.items()})


def chance_cell(args):
    """Background only (no coordinated events): the assessor's cluster rate is all chance."""
    bg, seed = args
    from bugarach.assess import assess_coactivity
    from bugarach.simulate import simulate_coordination
    s, _ = simulate_coordination(duration_sec=DURATION, n_roi=N_ROI, bg_rate_hz=bg,
                                 participation=(0.3,), n_per_level=(0,), grid_sec=0.1,
                                 seed=900000 + 1000 * int(round(bg * 1000)) + seed)
    recs = assess_coactivity(s, window=(0.0, DURATION), min_rois=KS, n_surrogates=20)
    return dict(bg_rate=bg, seed=seed, per_min={str(r.min_rois): r.clusters_permin for r in recs})


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--quick", action="store_true", help="one seed, two jitters: a smoke run")
    ap.add_argument("--workers", type=int, default=12)
    ap.add_argument("--out", type=Path, default=None, help="figure folder (default: darkroom)")
    a = ap.parse_args()
    seeds, jits = (SEEDS[:1], JITTERS[::3]) if a.quick else (SEEDS, JITTERS)
    # Every recording gets its own seed. The first run (2026-10-23) seeded 1000 + seed in every
    # cell, and the generator draws the background first, so all cells at one background rate
    # shared five background draws and their errors were correlated across Figure 1. Both blind
    # theory passes found it independently (goal page, Aim 0).
    cells = list(itertools.product(jits, PARTS, N_EVENTS, BG_RATES))
    grid = [(i, (*c, s)) for i, c in enumerate(cells) for s in seeds]
    t0 = time.time()
    with ProcessPoolExecutor(a.workers) as ex:
        rows = list(ex.map(cell, grid))
        chance = list(ex.map(chance_cell, list(itertools.product(BG_RATES, range(100)))))
    print(f"{len(rows)} recordings + {len(chance)} background-only in {time.time() - t0:.0f} s",
          file=sys.stderr)
    rec = dict(what="Aim 1a: one source, random membership, blind recovery",
               seeding="per recording: 1000 + 100 * condition index + seed",
               assessor_settings="K = 3, 4, 6 cells (absolute counts), 1 s bins, merge_bins 2, "
                                 "120 surrogates (shipped default 1000; only observation-based "
                                 "outputs are used here)",
               n_roi=N_ROI, duration_sec=DURATION, min_sep_sec=MIN_SEP, ks=KS, quick=a.quick,
               rows=rows, chance_arm=chance)
    name = "aim1_one_source_quick.json" if a.quick else "aim1_one_source.json"
    (HERE / name).write_text(json.dumps(rec, indent=1, default=float))
    print(HERE / name, file=sys.stderr)


if __name__ == "__main__":
    main()
