#!/usr/bin/env python3
"""Does one cell, one vote survive at the operating point? Ask several seeds.

    python tools/probe_one_vote.py --out docs/learned/one_vote.json

**The claim under test.** ``build_tube``'s docstring says each cell is capped at one
vote inside the centre window "so a single cell bursting cannot imitate a crowd", and
calls the cap exact. The cap *is* exact in amplitude — the raster is one-or-zero per
cell per frame, so a max-pool is an OR and two bursting cells reach 2/N brightness
however often they fire. The question is whether the conclusion follows.

**Why more than one seed.** A first version of this measurement used the single fit
that `probe_rate_invariance.py` trains, and reported that a two-cell burst outscores
four distinct cells. That is true of that fit. Across ten seeds it holds on five,
reverses on three and ties on two — because both scores are saturated sigmoids far
above the operating point and the gap between them is ~0.002. A blind review round
caught it, and it is the same defect this repository keeps finding: one training run
reported as a finding.

So this tool runs a grid of seeds and separates the two contrasts:

* **Fragile** — burst-of-two versus four-distinct. Reported with its seed-by-seed
  win/loss/tie count, and not as a result.
* **Robust** — the same two cells firing *many* times versus firing *once*. Identical
  amplitude, opposite verdict, decided purely by how long the run is. This is the one
  that carries the argument, and it is checked on every seed.

Runs ~4 s per seed on CPU.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

N_ROI = 32
"""Cells in the synthetic input, matching the benchmark's own recordings."""

T = 600
"""Frames. Long enough for the dilated stack's receptive field to sit inside it."""


def _fair_bakeoff():
    import importlib.util
    p = Path(__file__).with_name("fair_bakeoff.py")
    spec = importlib.util.spec_from_file_location("_fb", p)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _case(torch, *, n_cells: int, n_onsets: int, gap: int):
    """A raster with `n_cells` cells each firing `n_onsets` times, `gap` frames apart.

    Every case has the same total activity per cell and differs only in how it is
    distributed, which is the axis the claim is about.
    """
    x = torch.zeros(1, N_ROI, T)
    mid = T // 2
    for c in range(n_cells):
        for k in range(n_onsets):
            x[0, c, mid + (k - n_onsets // 2) * gap] = 1.0
    return x


def _peak(torch, model, x):
    with torch.no_grad():
        return float(torch.sigmoid(model(x)).max())


def _brightness(torch, model, x):
    """Peak pooled brightness — the quantity the cap actually bounds."""
    with torch.no_grad():
        b, n, t = x.shape
        kmin = int(torch.exp(model.log_center.detach()).min().clamp(1, model.k))
        pooled = torch.nn.functional.max_pool1d(
            x.reshape(b * n, 1, t), kernel_size=2 * kmin + 1,
            stride=1, padding=kmin).reshape(b, n, t)
        return float((pooled.sum(dim=1) / max(n, 1)).max())


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--bakeoff", default="docs/learned/bakeoff.json")
    ap.add_argument("--out", default="docs/learned/one_vote.json")
    ap.add_argument("--seeds", type=int, default=10)
    ap.add_argument("--steps", type=int, default=900)
    a = ap.parse_args(argv)

    import torch
    from bugarach.learn.train import train

    spec = json.loads(Path(a.bakeoff).read_text())["spec"]
    fb = _fair_bakeoff()
    dt = spec["grid_sec"]
    train_seeds = [1000 + i for i in range(6)]
    cache: dict[int, tuple] = {}

    def rec(seed):
        if seed not in cache:
            cache[seed] = fb._make_recording(spec, seed)
        return cache[seed]

    mk = lambda seed, _t=tuple(train_seeds): rec(_t[seed % len(_t)])   # noqa: E731

    per_seed = []
    for s in range(a.seeds):
        tr = train("tube", mk, dt=dt, n_train=6, steps=a.steps, crop=4096,
                   batch=3, lr=1e-2, seed=s)
        m, thr = tr.model, float(tr.threshold)
        burst = _case(torch, n_cells=2, n_onsets=5, gap=3)
        once2 = _case(torch, n_cells=2, n_onsets=1, gap=3)
        four = _case(torch, n_cells=4, n_onsets=1, gap=3)
        row = {
            "seed": s, "threshold": thr,
            "burst_two": _peak(torch, m, burst),
            "two_once": _peak(torch, m, once2),
            "four_distinct": _peak(torch, m, four),
            "brightness_two": _brightness(torch, m, burst),
            "brightness_four": _brightness(torch, m, four),
        }
        row["burst_beats_four"] = row["burst_two"] > row["four_distinct"]
        row["burst_fires"] = row["burst_two"] >= thr
        row["two_once_fires"] = row["two_once"] >= thr
        # The robust contrast: same two cells, same amplitude, different run length.
        row["duration_decides"] = row["burst_fires"] and not row["two_once_fires"]
        per_seed.append(row)
        print(f"  seed {s}: burst {row['burst_two']:.4f}  four "
              f"{row['four_distinct']:.4f}  two-once {row['two_once']:.4f}  "
              f"thr {thr:.4f}  duration-decides={row['duration_decides']}")

    n = len(per_seed)
    beats = sum(r["burst_beats_four"] for r in per_seed)
    out = {
        "n_seeds": n, "steps": a.steps, "n_roi": N_ROI,
        "cases": {
            "burst_two": "2 cells, 5 onsets each, 3 frames apart",
            "two_once": "the same 2 cells, 1 onset each",
            "four_distinct": "4 distinct cells, 1 onset each",
        },
        # The fragile comparison, reported as a tally rather than a value.
        "burst_beats_four_seeds": beats,
        "burst_beats_four_fraction": beats / n,
        # The robust one.
        "duration_decides_seeds": sum(r["duration_decides"] for r in per_seed),
        # The cap itself: brightness must be exactly 2/32 and 4/32 everywhere.
        "brightness_two_min": min(r["brightness_two"] for r in per_seed),
        "brightness_two_max": max(r["brightness_two"] for r in per_seed),
        "brightness_four_min": min(r["brightness_four"] for r in per_seed),
        "brightness_four_max": max(r["brightness_four"] for r in per_seed),
        "per_seed": per_seed,
    }
    Path(a.out).write_text(json.dumps(out, indent=1, sort_keys=True) + "\n")
    print(f"\nwrote {a.out}")
    print(f"  burst beats four distinct: {beats}/{n} seeds  <- fragile, not a result")
    print(f"  duration decides:          {out['duration_decides_seeds']}/{n} seeds")
    print(f"  pooled brightness two:  {out['brightness_two_min']:.4f}"
          f"-{out['brightness_two_max']:.4f}  (cap holds if constant)")
    print(f"  pooled brightness four: {out['brightness_four_min']:.4f}"
          f"-{out['brightness_four_max']:.4f}")
    return 0


if __name__ == "__main__":                                      # pragma: no cover
    raise SystemExit(main())
