#!/usr/bin/env python3
"""Fit the per-ROI background heterogeneity from real baseline windows.

    python tools/fit_background_shape.py            # fit, compare, verdict
    python tools/fit_background_shape.py --tol 0.05 # how far the constant may drift

Prints the maximum-likelihood Gamma shape for `bugarach.bench.MEASURED_RATE_SHAPE`
and **exits 1 if the tree's constant no longer matches the data**, so the number
in the source cannot quietly rot the way a transcribed one does.

**The model.** Inside one baseline window, an ROI's rate is drawn from
``Gamma(shape, mean/shape)`` and its event count is Poisson over that rate;
marginally the count is Negative Binomial with dispersion ``shape``. One shape is
shared across all windows because it describes the *heterogeneity*, while each
window keeps its own mean, because untreated slices genuinely differ several-fold
(FOUNDATIONS §9) and pooling their levels would inflate the spread with a
between-slice difference that is not within-field structure.

``shape -> infinity`` is the flat field the generator has always produced.

**Fit the distribution, do not tune to a summary.** The CV, the silent fraction
and the maximum are *diagnostics reported below*, never targets — matching them
by search would reproduce the statistics without the mechanism, which is the
error `docs/todo/2026-08-14-generator-background-model-is-flat.md` names in
terms. Nothing here optimises against them; they are printed so a human can see
whether a fit obtained from the likelihood alone lands anywhere near the data.

**Baseline windows only** (FOUNDATIONS §9; Tony, 2026-08-14: *"do not use senk or
ttx as sources for the properties of coordination"*). A slice carrying a
treatment contributes only the events inside its ``baseline`` region.

Needs ``$BUGARACH_DATA_ROOT``; real stores are machine-local (FOUNDATIONS §5) and
this writes nothing anywhere.
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

import numpy as np

ARCHIVE = "processed_archive/event_store_onset_revised_2v"
STREAM = "fast"
MIN_DURATION_SEC = 300.0
MIN_EVENTS = 20
MIN_ROIS = 5


def baseline_counts(path: Path):
    """``(counts per ROI, window duration)`` for a slice's baseline region.

    Returns ``None`` for every reason a slice is unusable, so one bad file cannot
    end a survey of eighty.
    """
    from bugarach.store import load_slice

    try:
        sl = load_slice(path)
    except Exception:                                        # noqa: BLE001
        return None
    reg = next((r for r in sl.regions
                if (r.name or "").strip().lower() == "baseline"), None)
    if reg is None or STREAM not in sl.streams:
        return None
    lo, hi = float(reg.start_sec), float(reg.end_sec)
    dur = hi - lo
    if dur < MIN_DURATION_SEC:
        return None
    stream = sl.streams[STREAM]
    counts = []
    for v in (stream.t50rise or stream.locs):
        v = np.asarray(v, dtype=float)
        v = v[np.isfinite(v)]
        counts.append(int(((v >= lo) & (v < hi)).sum()))
    c = np.asarray(counts, dtype=float)
    if c.sum() < MIN_EVENTS or c.size < MIN_ROIS:
        return None
    return c, dur


def negative_log_likelihood(log_shape: float, windows) -> float:
    """Pooled negative-binomial NLL at a shared shape, per-window means profiled out."""
    from scipy.special import gammaln

    a = float(np.exp(log_shape))
    total = 0.0
    for c, _dur in windows:
        mu = c.mean()                       # MLE of the window's expected count
        if mu <= 0:
            continue
        p = a / (a + mu)
        total -= float(np.sum(
            gammaln(c + a) - gammaln(a) - gammaln(c + 1)
            + a * np.log(p) + c * np.log1p(-p)))
    return total


def fit(windows) -> float:
    from scipy.optimize import minimize_scalar

    res = minimize_scalar(negative_log_likelihood, args=(windows,),
                          bounds=(np.log(1e-3), np.log(1e3)), method="bounded")
    return float(np.exp(res.x))


def _diagnostics(windows, shape, seed=0):
    """Silent fraction, median and max — for a real, fitted and flat field."""
    rng = np.random.RandomState(seed)
    real_c = np.concatenate([c for c, _ in windows])
    real_r = np.concatenate([c / d for c, d in windows]) * 1000.0

    def draw(rates_of):
        cs, rs = [], []
        for c, d in windows:
            k = rng.poisson(rates_of(c))
            cs.append(k)
            rs.append(k / d * 1000.0)
        return np.concatenate(cs), np.concatenate(rs)

    fit_c, fit_r = draw(lambda c: rng.gamma(shape, c.mean() / shape, size=c.size))
    flat_c, flat_r = draw(lambda c: np.full(c.size, c.mean()))
    rows = [("real", real_c, real_r),
            ("fitted", fit_c, fit_r),
            ("flat (today)", flat_c, flat_r)]
    return [(name, float(np.mean(c == 0) * 100), float(np.median(r)), float(r.max()))
            for name, c, r in rows]


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--tol", type=float, default=0.05,
                   help="relative drift allowed against bench.MEASURED_RATE_SHAPE "
                        "before this exits 1 (default 0.05)")
    p.add_argument("--seed", type=int, default=0,
                   help="seed for the diagnostic draws (default 0)")
    args = p.parse_args(argv)

    root = os.environ.get("BUGARACH_DATA_ROOT", "").strip()
    if not root:
        print("BUGARACH_DATA_ROOT is not set — this fit needs the real archive, "
              "and real stores are machine-local. Nothing written.", file=sys.stderr)
        return 2
    arc = Path(root).expanduser() / ARCHIVE
    if not arc.is_dir():
        print(f"no archive at {arc}", file=sys.stderr)
        return 2

    windows = []
    for path in sorted(arc.glob("*.mat")):
        got = baseline_counts(path)
        if got is not None:
            windows.append(got)
    if not windows:
        print(f"no usable baseline windows under {arc}", file=sys.stderr)
        return 2

    n_roi = sum(len(c) for c, _ in windows)
    shape = fit(windows)

    from bugarach.bench import MEASURED_RATE_SHAPE

    print(f"{len(windows)} baseline windows · {n_roi} ROIs · stream {STREAM!r}\n")
    print(f"fitted Gamma shape      {shape:.3f}   (CV of per-ROI rate "
          f"{1 / np.sqrt(shape):.2f}; flat field is shape -> inf)")
    print(f"bench.MEASURED_RATE_SHAPE {MEASURED_RATE_SHAPE:.3f}\n")

    print(f"{'':14s} {'ROIs silent':>12s} {'median mHz':>11s} {'max mHz':>9s}")
    for name, silent, med, mx in _diagnostics(windows, shape, seed=args.seed):
        print(f"{name:14s} {silent:11.0f}% {med:11.1f} {mx:9.0f}")
    print("\nDiagnostics, not targets: the fit maximises the likelihood of the "
          "counts and\nis never searched against the three columns above.")

    drift = abs(shape - MEASURED_RATE_SHAPE) / MEASURED_RATE_SHAPE
    if drift > args.tol:
        print(f"\nDRIFT: fitted {shape:.3f} is {drift:.1%} from the tree's "
              f"{MEASURED_RATE_SHAPE:.3f} (tolerance {args.tol:.0%}). Update "
              f"bugarach.bench.MEASURED_RATE_SHAPE, and re-derive anything "
              f"calibrated on it.", file=sys.stderr)
        return 1
    print(f"\nOK: within {args.tol:.0%} of the tree's constant.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
