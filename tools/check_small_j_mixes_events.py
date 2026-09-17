#!/usr/bin/env python3
"""What do trained models respond to: sub-second events, or slow shared modulation?

    python tools/check_small_j_mixes_events.py --out <folder> [--twins 50] [--draws 4] [--jobs 12]
        [--checkpoints <folder>] [--supervised-seeds 0] [--untrained-seeds 0]

The rigid-shift report's training checks put rigid shift at *J* = 1.6 s beside 10–20 s, on the
reasoning that slow shared modulation survives a 1.6 s shift and sub-second alignment does not. On
real crops the zero-parameter ``slow_modulation`` scorer, which averages the share of active ROIs
over 10 s and so cannot resolve a sub-second event, still separated real from a 1.6 s shift at
0.62–0.63. A reviewing session (2026-09-17) argued the reason: a sub-second event raises the peak
of a 10 s average, and a 1.6 s shift pushes some member onsets out of that peak. If so, the control
mixes events and modulation, and a model has to be asked directly.

This asks on synthetic twins, where each ingredient is known. Four twins per draw, all from
``look_rigid_shift_controls.twin_pair`` at the paired checks' participation (0.2):

* ``events`` — planted coordinated events, no modulation;
* ``independent_modulation_with_events`` — the same planted twin, each ROI's rate modulated on its
  own phase (so nothing moves together except the events);
* ``independent_modulation`` — no events, each ROI on its own phase (must read chance);
* ``shared_modulation`` — no events, one phase for every ROI.

Each twin is scored against its own rigid shift at 1.6, 10 and 20 s, with the same crops, crop score
(top 1 %) and tie rule as the paired checks, by:

* the three count baselines of ``tools/tube_self_supervised.py``;
* every checkpoint in ``--checkpoints`` (``tools/tube_ssl_real_compare.py`` writes one per model,
  displacement, seed and mouse fold trained against rigid shift on real recordings);
* supervised fits at ``--supervised-seeds``, fitted as the real-recordings stage fits them
  (``tube_ssl_real_compare.fit_supervised``): models that saw planted events and never modulation;
* untrained models at ``--untrained-seeds``: the architecture at its registered initial parameters.

A model that learned sub-second events separates ``events`` from its 1.6 s shift; one that learned
only slow shared modulation separates ``shared_modulation`` from its 20 s shift and reads chance on
``events`` at 1.6 s. Exploratory.
"""

from __future__ import annotations

import argparse
import json
import multiprocessing as mp
import sys
import time
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

J_SEC = (1.6, 10.0, 20.0)
PARTICIPATION = 0.2
TWINS = ("events", "independent_modulation_with_events", "independent_modulation",
         "shared_modulation")


def build_scorer(spec):
    """(group label, fit label, crop scorer) for one scorer spec."""
    import torch
    import tube_self_supervised as ts

    kind = spec[0]
    if kind == "baseline":
        name = spec[1]
        return name, name, ts.model_scorer(ts.baseline_model(name).eval())
    if kind == "checkpoint":
        from bugarach.learn import checkpoint
        path = Path(spec[1])
        _, name, J, seed, fold = path.stem.split("-")
        tr = checkpoint.load(path)
        tr.model.eval()
        return (f"trained on real, J {float(J):g} s, {name}", path.stem,
                ts.model_scorer(tr.model))
    if kind == "supervised":
        import tube_ssl_real_compare as rc
        name, seed = spec[1], spec[2]
        tr = rc.fit_supervised(name, seed)
        tr.model.eval()
        return f"supervised, {name}", f"supervised-{name}-{seed}", ts.model_scorer(tr.model)
    if kind == "untrained":
        from bugarach.learn.nets import ARCHITECTURES
        name, seed = spec[1], spec[2]
        torch.manual_seed(seed)
        return (f"untrained, {name}", f"untrained-{name}-{seed}",
                ts.model_scorer(ARCHITECTURES[name].make().eval()))
    raise ValueError(spec)


def task(args):
    spec, n_twins, draws = args
    import look_rigid_shift_controls as lc
    import tube_self_supervised as ts

    from bugarach.learn.train import pin_threads

    pin_threads()
    group, fit, score = build_scorer(spec)
    pairs = {(tw, J): [] for tw in TWINS for J in J_SEC}
    for t in range(n_twins):
        pl, un, shape = lc.twin_pair("fast", None, PARTICIPATION, t)
        L, dt = shape["n_frames"], shape["dt"]
        margin = int(np.ceil(max(J_SEC) / dt)) + 1   # one crop grid for every J
        starts = list(range(margin, L - margin - ts.CROP + 1, ts.CROP))
        for d in range(draws):
            # Keyed by twin and draw only, so every scorer sees the same recordings and shifts.
            rng_mod = np.random.RandomState(ts.seed31("small-j-mix-mod", t, d))
            twins = {"events": pl,
                     "independent_modulation_with_events": ts.modulated(pl, L, dt, rng_mod, False),
                     "independent_modulation": ts.modulated(un, L, dt, rng_mod, False),
                     "shared_modulation": ts.modulated(un, L, dt, rng_mod, True)}
            for tw, trains in twins.items():
                real = ts.raster_of(trains, L)
                for J in J_SEC:
                    rng = np.random.RandomState(ts.seed31("small-j-mix-shift", t, d, tw, J))
                    sur = ts.raster_of(ts.rigid_frames(trains, L, J / dt, rng), L)
                    pairs[(tw, J)] += ts.crop_pairs(score, real, sur, starts)
    return group, fit, {f"{tw}|{J:g}": v for (tw, J), v in pairs.items()}


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--out", required=True)
    ap.add_argument("--twins", type=int, default=50)
    ap.add_argument("--draws", type=int, default=4)
    ap.add_argument("--jobs", type=int, default=4)
    ap.add_argument("--checkpoints", default=None,
                    help="score every ssl-*.json checkpoint in this folder")
    ap.add_argument("--supervised-seeds", nargs="*", type=int, default=[])
    ap.add_argument("--untrained-seeds", nargs="*", type=int, default=[])
    a = ap.parse_args(argv)
    import tube_self_supervised as ts

    from bugarach import provenance

    specs = [("baseline", name) for name in ts.BASELINES]
    for name in ts.MODELS:
        specs += [("supervised", name, s) for s in a.supervised_seeds]
        specs += [("untrained", name, s) for s in a.untrained_seeds]
    if a.checkpoints:
        specs += [("checkpoint", str(p)) for p in sorted(Path(a.checkpoints).glob("ssl-*.json"))]
    # Slowest first, so the long fits are not the last to start.
    specs.sort(key=lambda s: (s[0] != "supervised", "line_bound" not in str(s)))
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    t0 = time.time()
    by_fit: dict = {}
    pooled: dict = {}
    with mp.get_context("spawn").Pool(a.jobs, maxtasksperchild=1) as pool:
        for i, (group, fit, cells) in enumerate(pool.imap_unordered(
                task, [(s, a.twins, a.draws) for s in specs])):
            by_fit[fit] = {"group": group, **{k: ts.paired_summary(v)["share_real_higher"]
                                              for k, v in cells.items()}}
            for k, v in cells.items():
                pooled.setdefault(group, {}).setdefault(k, []).extend(v)
            print(f"[{time.time() - t0:7.0f}s] {i + 1}/{len(specs)} {fit}", flush=True)
    groups = {}
    for group, cells in sorted(pooled.items()):
        fits = [f for f, v in by_fit.items() if v["group"] == group]
        groups[group] = {"n_fits": len(fits)}
        for k, v in sorted(cells.items()):
            per_fit = [by_fit[f][k] for f in fits]
            groups[group][k] = {"pooled": ts.paired_summary(v)["share_real_higher"],
                                "per_fit_min": float(min(per_fit)),
                                "per_fit_max": float(max(per_fit)),
                                "n_fits_above_half": int(sum(x > 0.5 for x in per_fit))}
    doc = {"meta": {"twins": a.twins, "draws_per_twin": a.draws, "participation": PARTICIPATION,
                    "J_sec": J_SEC, "crop_frames": ts.CROP, "baselines": ts.BASELINES,
                    "checkpoints": a.checkpoints and Path(a.checkpoints).name,
                    "supervised_seeds": a.supervised_seeds, "untrained_seeds": a.untrained_seeds,
                    "modulation": {"period_sec": ts.MOD_PERIOD_SEC, "depth": ts.MOD_DEPTH},
                    "seconds": time.time() - t0, "exploratory": True,
                    "provenance": provenance.stamp(
                        produced_by="tools/check_small_j_mixes_events.py")},
           "groups": groups, "by_fit": by_fit}
    (out / "results.json").write_text(json.dumps(doc, indent=1, default=float) + "\n")
    for group, cells in groups.items():
        print(group, f"({cells['n_fits']} fits)")
        for k, v in cells.items():
            if k != "n_fits":
                print(f"    {k:44s} {v['pooled']:.3f}  per fit {v['per_fit_min']:.2f}–"
                      f"{v['per_fit_max']:.2f}, above 0.5 in {v['n_fits_above_half']}")


if __name__ == "__main__":
    main()
