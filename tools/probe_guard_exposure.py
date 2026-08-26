#!/usr/bin/env python3
"""The guard's empty-stratum rise has a closed form, and it is an exposure factor.

    python tools/probe_guard_exposure.py --selftest
    python tools/probe_guard_exposure.py

`docs/reviews/guard_where_it_lands_2026-08-25.md` reports that a guard interval
**raises** these detectors' bars where the excised band held no events, and gives the
reason as *"the retained span is compacted onto one shorter line, so the same events sit
at higher density"*. That reason is right, and it is stronger than it was stated: the
rise is not merely in that direction, it is **exactly** the ratio of the two line
lengths, with no free parameter.

CoactDetect's bar is the mean over surrogates of the number of ROIs with at least one
shifted event landing in one bin width. For an ROI whose retained events occupy a set
whose bin-width neighbourhood has measure ``m`` on a line of length ``L``, a uniform
circular shift lands it in the test window with probability ``m / L``. So

    nullmean  =  sum_over_ROIs m_i / L        — a DENSITY, not a count

and excising a band that holds **no events** leaves every ``m_i`` alone while cutting
``L`` from ``C`` to ``C - guard``. The bar therefore rises by

    C / (C - guard)   —   9.09% at C = 60 s, guard = 5 s;   50.00% at guard = 20 s

which is what that document measured (+8.78%, +49.91%) and read as an argument about
wide guards. It is not about wide guards. It is a **normalization**, and it is applied
to every bin in the recording — including the occupied ones, where it sits on top of
the masking relief and cancels part of it.

**The fix is a keyword.** ``coact_detect(..., guard_norm="exposure")`` drops the excised
events and keeps the full window length, so the guard removes counts and not exposure.
Then an empty band changes nothing — ratio 1 — and what is left in the occupied stratum
is masking relief with no normalization term mixed into it.

This probe measures the ratio, both ways, against the closed form. `--selftest` runs
guard 0 against guard 0 under both normalizations and demands every delta be exactly
zero; without that, everything below is RNG drift with a formula attached.

**What this does not do.** It does not touch LoCo, whose bar is a percentile of an
integer-valued pool and so responds to the same density change through a quantizer —
its rise is real but smaller than C / (C - guard) predicts and no closed form is
claimed for it here. It reports LoCo's number beside the prediction and stops.
"""

from __future__ import annotations

import argparse
import sys

import numpy as np

from bugarach.bench import make_crowded_recording, make_recording
from bugarach.detectors.coact import coact_detect
from bugarach.detectors.loco import loco_detect
from bugarach.detectors.rate import recording_extent, stream_trains

SEEDS = (1, 2, 3, 4)
GUARDS = (5.0, 20.0)
STREAM = "events"
REGIME = "baseline_quiet"
COACT_CTX = 60.0
COACT_BIN = 2.0
LOCO_CTX = 120.0          # halves of 60 s — the length a LoCo guard shortens
LOCO_STEP = 15.0


def _events(sl):
    ext = recording_extent(sl)
    trains = stream_trains(sl.streams[STREAM], ext)
    ev = [np.asarray(t, float) for t in trains if np.size(t)]
    pooled = np.sort(np.concatenate(ev)) if ev else np.empty(0)
    return pooled, ext, trains


def coact_bar(sl, guard, norm, n_sur):
    """Bin centres and the surrogate null mean. min_rois=0 for profiling only —
    a candidate bin always holds its own events, so with the shipped setting the
    empty stratum would be empty. No detection number comes out of this run."""
    _, ext, trains = _events(sl)
    d = coact_detect(trains, ext, rng_seed=7, int_win_sec=COACT_BIN,
                     context_win_sec=COACT_CTX, alpha=1e-4, n_surrogates=n_sur,
                     min_rois=0, guard_sec=guard, guard_norm=norm)
    return np.asarray(d.ctr, float), np.asarray(d.nullmean_prof, float)


def loco_bar(sl, guard, n_sur):
    st = loco_detect(sl, rng_seed=7, bin_width_sec=1.0, context_win_sec=LOCO_CTX,
                     thr_step_sec=LOCO_STEP, merge_gap_sec=2.0, threshold_pctile=99.9,
                     n_surrogates=n_sur, guard_sec=guard).streams[STREAM]
    return np.asarray(st.signal.t, float), np.asarray(st.signal.threshold, float)


def exposure_factor(centres, ext, guard, ctx):
    """C / (C - excised), per bin, with the clipping the detector itself applies.

    Near the recording edges the context window is short and the guard band can
    hang off the end, so the factor is not one number — it is computed per bin the
    same way ``coact.py`` computes ``c_lo``/``left``/``right``.
    """
    c_lo = np.maximum(ext[0], centres - ctx / 2)
    c_hi = np.minimum(ext[1], centres + ctx / 2)
    left = np.maximum(c_lo, np.minimum(centres - guard / 2, c_hi))
    right = np.minimum(c_hi, np.maximum(centres + guard / 2, c_lo))
    retained = (left - c_lo) + (c_hi - right)
    with np.errstate(divide="ignore", invalid="ignore"):
        return np.where(retained > 0, (c_hi - c_lo) / retained, np.nan)


def _split(t, b0, b1, events, guard):
    """Per-bin ratio bar(guard)/bar(0), split on whether the band held events."""
    lo = np.searchsorted(events, t - guard / 2, "left")
    hi = np.searchsorted(events, t + guard / 2, "right")
    occ = (hi - lo) > 0
    ok = np.isfinite(b0) & np.isfinite(b1) & (b0 > 0)
    ratio = np.where(ok, b1 / np.where(b0 > 0, b0, np.nan), np.nan)
    return ratio, occ, ok


def run_coact(maker, guard, norm, n_sur):
    r_empty, r_occ, pred, per_seed = [], [], [], []
    for seed in SEEDS:
        sl, _ = maker(seed)
        events, ext, _ = _events(sl)
        t, b0 = coact_bar(sl, 0.0, norm, n_sur)
        _, b1 = coact_bar(sl, guard, norm, n_sur)
        n = min(t.size, b1.size)
        t, b0, b1 = t[:n], b0[:n], b1[:n]
        ratio, occ, ok = _split(t, b0, b1, events, guard)
        f = exposure_factor(t, ext, guard, COACT_CTX)
        e, o = ok & ~occ, ok & occ
        r_empty.append(ratio[e]); r_occ.append(ratio[o]); pred.append(f[e])
        per_seed.append((np.nanmean(ratio[e]), np.nanmean(ratio[o])))
    return (np.concatenate(r_empty), np.concatenate(r_occ),
            np.concatenate(pred), np.array(per_seed))


def run_loco(maker, guard, n_sur):
    from bugarach.detectors._shared import matlab_colon
    r_empty, r_occ, pred = [], [], []
    for seed in SEEDS:
        sl, _ = maker(seed)
        events, ext, _ = _events(sl)
        t, b0 = loco_bar(sl, 0.0, n_sur)
        _, b1 = loco_bar(sl, guard, n_sur)
        n = min(t.size, b1.size)
        t, b0, b1 = t[:n], b0[:n], b1[:n]
        # score each ANCHOR once, at the anchor: LoCo excises around the anchor,
        # not the bin, and a bin sits up to thr_step/2 away from the one it
        # inherits its threshold from (probe_guard_where_it_lands.py says why).
        anchors = matlab_colon(ext[0], LOCO_STEP, ext[1])
        idx = np.argmin(np.abs(t[:, None] - anchors[None, :]), axis=1)
        _, first = np.unique(idx, return_index=True)
        t, b0, b1 = anchors[idx][first], b0[first], b1[first]
        ratio, occ, ok = _split(t, b0, b1, events, guard)
        # each half runs from the anchor outward, so the guard costs each half
        # guard/2 out of LOCO_CTX/2 — the same factor as a full window losing guard
        f = exposure_factor(t, ext, guard, LOCO_CTX)
        r_empty.append(ratio[ok & ~occ]); r_occ.append(ratio[ok & occ])
        pred.append(f[ok & ~occ])
    return np.concatenate(r_empty), np.concatenate(r_occ), np.concatenate(pred)


def _cell(x):
    if x.size == 0:
        return "        --  ", 0
    m = np.nanmean(x)
    sem = np.nanstd(x, ddof=1) / np.sqrt(np.isfinite(x).sum())
    return f"{m:7.4f}+-{sem:.4f}", x.size


def selftest(n_sur):
    """Can the alarm ring? A guard of zero excises nothing, under either
    normalization, so any nonzero delta is the RNG or the code path and every
    number this tool prints is that delta plus noise."""
    bad = 0
    sl, _ = make_recording(REGIME, 1)
    _, b_ref = coact_bar(sl, 0.0, "compact", n_sur)
    for norm in ("compact", "exposure"):
        _, b = coact_bar(sl, 0.0, norm, n_sur)
        d = np.abs(np.nan_to_num(b - b_ref, nan=0.0))
        worst = d.max() if d.size else 0.0
        ok = worst == 0.0
        bad += 0 if ok else 1
        print(f"  coact guard 0, guard_norm={norm:8s} {b.size:6d} bins   "
              f"max |delta| = {worst:.3e}   "
              + ("clean" if ok else "NOT REPRODUCIBLE — the tool is measuring itself"))
    # the two normalizations must also be indistinguishable at guard 0, since
    # neither takes the guarded branch at all
    return 1 if bad else 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--selftest", action="store_true",
                    help="guard 0 against guard 0, both normalizations; deltas must be 0")
    ap.add_argument("--crowded", action="store_true", help="also the crowded recording")
    ap.add_argument("--surrogates", type=int, default=500,
                    help="surrogates per bin (default 500; the closed form is a mean, "
                         "so this sets how tightly it can be resolved)")
    ap.add_argument("--loco", action="store_true",
                    help="also report LoCo beside the prediction (no fix is offered)")
    a = ap.parse_args(argv)

    if a.selftest:
        return selftest(a.surrogates)

    makers = [("bench", lambda s: make_recording(REGIME, s))]
    if a.crowded:
        makers.append(("crowded", lambda s: make_crowded_recording(REGIME, s)))

    print(f"{len(SEEDS)} seeds, regime {REGIME!r}, {a.surrogates} surrogates per bin\n"
          "ratio = bar(guard) / bar(no guard), per bin, pooled over seeds\n"
          "EMPTY = the excised band held no events — the guard removed nothing\n"
          "predicted = C / (C - excised), per bin, edge clipping included\n")
    hdr = (f"  {'rec':8s} {'detector':8s} {'norm':9s} {'guard':>5s} {'n empty':>8s} "
           f"{'ratio empty':>16s} {'predicted':>10s} {'n occup':>8s} {'ratio occupied':>16s}"
           f" {'seeds<1':>7s}")
    print(hdr)
    print("  " + "-" * (len(hdr) - 2))
    for label, maker in makers:
        for g in GUARDS:
            for norm in ("compact", "exposure"):
                e, o, p, ps = run_coact(maker, g, norm, a.surrogates)
                ce, ne = _cell(e)
                co, no = _cell(o)
                pm = np.nanmean(p) if norm == "compact" else 1.0
                # the strength test is agreement across seeds, not a p-value:
                # how many of them individually put the occupied bar below 1
                agree = int(np.sum(ps[:, 1] < 1.0))
                print(f"  {label:8s} {'coact':8s} {norm:9s} {g:5.1f} {ne:8d} "
                      f"{ce:>16s} {pm:10.4f} {no:8d} {co:>16s} "
                      f"{agree:d}/{len(SEEDS):d}".rjust(0))
            if a.loco:
                e, o, p = run_loco(maker, g, a.surrogates)
                ce, ne = _cell(e)
                co, no = _cell(o)
                print(f"  {label:8s} {'loco':8s} {'compact':9s} {g:5.1f} {ne:8d} "
                      f"{ce:>16s} {np.nanmean(p):10.4f} {no:8d} {co:>16s}")
        print()

    print("READ IT LIKE THIS")
    print("  compact  ratio empty ~= predicted  ->  the rise IS the exposure factor.")
    print("                                        Nothing about the neural data is in it.")
    print("  exposure ratio empty ~= 1.0000     ->  removing the span, not the events,")
    print("                                        was the whole of it.")
    print("  exposure ratio occupied < 1        ->  what is left is masking relief, with")
    print("                                        no normalization term mixed in.")
    print("  LoCo's bar is an integer-valued percentile, so it moves less than the")
    print("  prediction; that gap is a quantizer, not a second mechanism.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
