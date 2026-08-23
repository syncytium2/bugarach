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


def stream_name(sl):
    """Which stream to fit on, or ``None`` if it cannot be decided.

    This lab's stores carry ``fast`` and ``slow``; a foreign export folder with
    one unnamed stream is loaded as ``events`` (``io.load_folder``). Insisting on
    ``fast`` skipped every such recording **silently**, and then reported "too
    little baseline to fit a shape" — the wrong answer to give a lab whose data
    is fine, and precisely the lab this fit exists to serve.

    A folder with several named streams and no ``fast`` is ambiguous rather than
    broken, so it returns ``None`` and the caller says so.
    """
    if STREAM in sl.streams:
        return STREAM
    return next(iter(sl.streams)) if len(sl.streams) == 1 else None


def baseline_trains(sl):
    """``(per-ROI event times re-zeroed, window duration)`` for the baseline region.

    The temporal fit needs the times, not just the totals.
    """
    got = _baseline(sl)
    if got is None:
        return None
    trains, dur = got
    return trains, dur


def baseline_counts(sl):
    """``(counts per ROI, window duration)`` for a recording's baseline region.

    Returns ``None`` for every reason a recording is unusable, so one bad file
    cannot end a survey of eighty.

    Takes a loaded recording: the caller reads the export folder, which is the
    export folder the lab approved. The constants this file fits — ``MEASURED_RATE_SHAPE``
    and ``MEASURED_BURST_SHAPE`` — parameterise the generator every session uses,
    so fitting them on recordings the lab withdrew propagates further than any
    single figure.
    """
    reg = next((r for r in sl.regions
                if (r.name or "").strip().lower() == "baseline"), None)
    if reg is None:
        return None
    name = stream_name(sl)
    if name is None:
        return None
    lo, hi = float(reg.start_sec), float(reg.end_sec)
    dur = hi - lo
    if dur < MIN_DURATION_SEC:
        return None
    stream = sl.streams[name]
    counts = []
    for v in (stream.t50rise or stream.locs):
        v = np.asarray(v, dtype=float)
        v = v[np.isfinite(v)]
        counts.append(int(((v >= lo) & (v < hi)).sum()))
    c = np.asarray(counts, dtype=float)
    if c.sum() < MIN_EVENTS or c.size < MIN_ROIS:
        return None
    return c, dur


def _baseline(sl):
    """``(per-ROI times re-zeroed to the window, duration)`` or ``None``."""
    reg = next((r for r in sl.regions
                if (r.name or "").strip().lower() == "baseline"), None)
    if reg is None:
        return None
    name = stream_name(sl)
    if name is None:
        return None
    lo, hi = float(reg.start_sec), float(reg.end_sec)
    dur = hi - lo
    if dur < MIN_DURATION_SEC:
        return None
    stream = sl.streams[name]
    trains = []
    for v in (stream.t50rise or stream.locs):
        v = np.asarray(v, dtype=float)
        v = v[np.isfinite(v)]
        trains.append(np.sort(v[(v >= lo) & (v < hi)]) - lo)
    if sum(x.size for x in trains) < MIN_EVENTS or len(trains) < MIN_ROIS:
        return None
    return trains, dur


MIN_EVENTS_PER_ROI = 10
"""Below this a within-ROI temporal fit has nothing to say."""


def burst_rows(windows_t, bin_sec):
    """Per-ROI binned-count vectors, for ROIs carrying enough events."""
    rows = []
    for trains, dur in windows_t:
        edges = np.arange(0.0, dur + bin_sec, bin_sec)
        for v in trains:
            if v.size >= MIN_EVENTS_PER_ROI:
                rows.append(np.histogram(v, bins=edges)[0].astype(float))
    return rows


def fit_burst(windows_t, bin_sec) -> float:
    """ML Gamma shape of the per-bin rate multiplier, ROI means profiled out.

    Fixing the ROI is what isolates the temporal term: rate differences ACROSS
    ROIs are constant inside one of them, so the over-dispersion left is time.
    """
    rows = burst_rows(windows_t, bin_sec)
    if not rows:
        return float("nan")
    return fit(rows)


def fano(rows) -> float:
    """Mean variance/mean of per-bin counts — the diagnostic, never a target."""
    vals = [c.var() / c.mean() for c in rows if c.mean() > 0]
    return float(np.mean(vals)) if vals else float("nan")


def negative_log_likelihood(log_shape: float, rows) -> float:
    """Pooled negative-binomial NLL at a shared shape, per-row means profiled out."""
    from scipy.special import gammaln

    a = float(np.exp(log_shape))
    total = 0.0
    for c in rows:
        mu = c.mean()                       # MLE of the window's expected count
        if mu <= 0:
            continue
        p = a / (a + mu)
        total -= float(np.sum(
            gammaln(c + a) - gammaln(a) - gammaln(c + 1)
            + a * np.log(p) + c * np.log1p(-p)))
    return total


def fit(rows) -> float:
    """ML shape for a set of count vectors, each keeping its own mean."""
    from scipy.optimize import minimize_scalar

    res = minimize_scalar(negative_log_likelihood, args=(rows,),
                          bounds=(np.log(1e-3), np.log(1e4)), method="bounded")
    return float(np.exp(res.x))


#: below this many usable baseline windows a shape is not worth reporting — the
#: constant in the tree rests on 81, and a handful of windows fits noise
MIN_WINDOWS_FOR_SHAPE = 8


def _this_labs_reference() -> float:
    """``bench.MEASURED_RATE_SHAPE`` — this lab's fit, for comparison only.

    Re-exported here so a caller that already has the fitter open does not also
    have to reach into ``bench`` for the number it is comparing against. It is
    **not** a default: the whole point of :func:`fit_shape_from_slices` is that a
    folder supplies its own.
    """
    from bugarach.bench import MEASURED_RATE_SHAPE
    return MEASURED_RATE_SHAPE


def fit_shape_from_slices(slices):
    """The per-ROI heterogeneity of whatever folder is handed in.

    ``MEASURED_RATE_SHAPE`` is a **measurement of this lab's recordings**, not a
    property of calcium imaging, and the difference bites as soon as a second lab
    points the tool at its own folder: applying our 0.275 to their field is the
    same category of error as applying a flat field to ours — a constant standing
    in for a measurement. Whether a field is flat is *their* empirical question,
    and this is what answers it for them.

    Returns ``(shape, n_windows, n_rois)``, or ``(None, n, r)`` when there is not
    enough baseline to fit. The caller decides what to do about that, because
    silently falling back to another folder's constant is the failure this
    function exists to prevent.
    """
    windows = [got for got in (baseline_counts(sl) for sl in slices)
               if got is not None]
    n_roi = int(sum(c.size for c, _ in windows))
    if len(windows) < MIN_WINDOWS_FOR_SHAPE:
        return None, len(windows), n_roi
    return fit([c for c, _ in windows]), len(windows), n_roi


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


DEAD_ROI_RATE = 0.030
"""66 of 2185 eligible ROIs rejected as dead — the rule's own rate.

Verified against this archive rather than assumed: the exporter applied its
2026-08-15 roster to `event_store_onset_revised_2v` by `(slice_id, ROI)`,
matching all 2185 keys with no disagreements, and rejected 66. The denominator
is the *eligible* population — 67 of 85 slices — not the store's 2738 ROIs.
See `docs/todo/2026-08-15-zero-event-rois-are-not-dead-rois.md`.
"""


def dead_roi_sensitivity(n_win=81, n_roi=33, mean_count=8.0, reps=20,
                         dead=DEAD_ROI_RATE, seed=20260816):
    """How far do structural zeros bend the fitted shape?

    The fits in this tool were taken over a population that had not been through
    the dead-ROI rule, so it carried rows that are zero by construction rather
    than by biology — and a Gamma shape MLE is most sensitive in exactly that
    tail. The rule has since been applied at export, but the question stays
    live: it is what any fit over an unfiltered population is worth, and 18 of
    85 slices are ineligible for the verdict and so remain unfiltered.

    Answers it by simulation rather than argument: draw Gamma-Poisson counts at a
    known shape with the real fit's geometry, force `dead` of them to zero, and
    refit with :func:`fit` — the same estimator, so the comparison is of
    populations and not of methods.

    Needs no data root, which is the point: the question can be settled on any
    machine, including one that cannot open a store.
    """
    import numpy as np

    def sample(rng, a, dead_frac):
        rows = []
        for _ in range(n_win):
            c = rng.poisson(rng.gamma(a, mean_count / a, size=n_roi)).astype(float)
            if dead_frac:
                c[rng.random_sample(n_roi) < dead_frac] = 0.0
            rows.append(c)
        return rows

    out = []
    for a in (0.275, 0.450, 0.800):
        clean, dirty = [], []
        for rep in range(reps):
            rng = np.random.RandomState(seed + rep)
            clean.append(fit(sample(rng, a, 0.0)))
            rng = np.random.RandomState(seed + rep)
            dirty.append(fit(sample(rng, a, dead)))
        clean, dirty = np.array(clean), np.array(dirty)
        out.append((a, clean.mean(), clean.std(), dirty.mean(), dirty.std()))
    return out


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--dead-roi-sensitivity", action="store_true",
                   help="simulate how 3%% structural zeros bend the fit; needs no data root")
    p.add_argument("--tol", type=float, default=0.05,
                   help="relative drift allowed against bench.MEASURED_RATE_SHAPE "
                        "before this exits 1 (default 0.05)")
    p.add_argument("--folder", default=None,
                   help="export folder holding the real recordings "
                        "(docs/export_folder_spec.md)")
    p.add_argument("--seed", type=int, default=0,
                   help="seed for the diagnostic draws (default 0)")
    args = p.parse_args(argv)

    if args.dead_roi_sensitivity:
        print(f"dead-ROI contamination at {DEAD_ROI_RATE:.1%}, "
              "81 windows x 33 ROI, 20 replicates")
        print(f"{'true':>6s} {'clean':>16s} {'+dead':>16s} {'bias':>9s}")
        for a, cm, cs, dm, ds in dead_roi_sensitivity():
            print(f"{a:6.3f} {cm:8.3f}+/-{cs:5.3f} {dm:8.3f}+/-{ds:5.3f} {dm - cm:+9.3f}")
        print("\nContamination biases the shape DOWN and the bias grows with it,"
              "\nbut at the tree's 0.275 it is under 1% after inversion — so"
              "\napplying the dead-ROI rule should not strand any bench number.")
        return 0

    if not args.folder:
        print("--folder is required: this fit needs real recordings, and they "
              "arrive as an export folder (docs/export_folder_spec.md). It used "
              "to walk a .mat archive, which holds every recording ever "
              "processed rather than the ones the lab kept — and the constants "
              "fitted here parameterise the generator every session uses. "
              "Nothing written.", file=sys.stderr)
        return 2

    from bugarach.io import load_folder

    slices = load_folder(Path(args.folder).expanduser())
    windows = []
    for sl in slices:
        got = baseline_counts(sl)
        if got is not None:
            windows.append(got)
    if not windows:
        print(f"no usable baseline windows in {args.folder}", file=sys.stderr)
        return 2

    n_roi = sum(len(c) for c, _ in windows)
    shape = fit([c for c, _ in windows])

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

    # ---- the temporal axis ------------------------------------------------
    from bugarach.bench import MEASURED_BURST_BINS, MEASURED_BURST_SHAPE

    windows_t = []
    for sl in slices:
        got = baseline_trains(sl)
        if got is not None:
            windows_t.append(got)

    print("\n--- clumping in time, within an ROI ---")
    print("(one ROI followed across bins: rate differences BETWEEN ROIs are held "
          "constant\ninside one of them, so the over-dispersion left over is "
          "temporal)\n")
    n_rois = len(burst_rows(windows_t, MEASURED_BURST_BINS[-1]))
    print(f"{len(windows_t)} windows · {n_rois} ROIs with "
          f"{MIN_EVENTS_PER_ROI}+ events\n")
    print(f"{'bin':>7s} {'fitted shape':>13s} {'in tree':>9s} "
          f"{'real var/mean':>14s} {'constant rate':>14s}")
    burst_fits = {}
    for bin_sec in (30.0, 60.0, 120.0, 300.0):
        k = fit_burst(windows_t, bin_sec)
        burst_fits[bin_sec] = k
        in_tree = ""
        for b, s in zip(MEASURED_BURST_BINS, MEASURED_BURST_SHAPE):
            if abs(b - bin_sec) < 1e-9:
                in_tree = f"{s:.3f}"
        print(f"{bin_sec:6.0f}s {k:13.3f} {in_tree:>9s} "
              f"{fano(burst_rows(windows_t, bin_sec)):14.2f} {1.0:14.2f}")
    print("\nVariance/mean rises with the bin because busy stretches span several "
          "bins.\nOne scale cannot reproduce that at any shape, which is why the "
          "generator\ntakes a sequence.")

    burst_drift = max(
        abs(burst_fits[b] - s) / s
        for b, s in zip(MEASURED_BURST_BINS, MEASURED_BURST_SHAPE)
        if b in burst_fits)
    if burst_drift > args.tol:
        print(f"\nDRIFT: the temporal fit is {burst_drift:.1%} from "
              f"bench.MEASURED_BURST_SHAPE (tolerance {args.tol:.0%}). Update it, "
              f"and re-derive anything calibrated on it.", file=sys.stderr)
        return 1

    drift = abs(shape - MEASURED_RATE_SHAPE) / MEASURED_RATE_SHAPE
    if drift > args.tol:
        print(f"\nDRIFT: fitted {shape:.3f} is {drift:.1%} from the tree's "
              f"{MEASURED_RATE_SHAPE:.3f} (tolerance {args.tol:.0%}). Update "
              f"bugarach.bench.MEASURED_RATE_SHAPE, and re-derive anything "
              f"calibrated on it.", file=sys.stderr)
        return 1
    print(f"\nOK: both axes within {args.tol:.0%} of the tree's constants.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
