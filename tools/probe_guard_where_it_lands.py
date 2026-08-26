#!/usr/bin/env python3
"""Where does the guard move the bar — everywhere, or only where it excised something?

    python tools/probe_guard_where_it_lands.py

`docs/forks.md` §4a concludes the guard interval is **not** doing guard-cell work,
because its recall gain is *flat across the nearest-neighbour gap*: it helps events
with a close neighbour exactly as much as isolated ones, so there is nothing being
unmasked. That reading is sound for **mutual** masking and `probe_guard_on_surrogates`
measures it correctly.

**It cannot settle the question, because guard cells relieve two maskings and only
one of them is gap-dependent.** `docs/detector_history.md` §5.1 names both:

* **mutual masking** — a *neighbouring* event sits in the reference window. Gap-dependent.
  Relieving it raises recall for crowded events and does nothing for isolated ones.
* **self-masking** — the event's *own* energy sits in the reference that judges it.
  **Gap-independent by construction**: every event self-masks, crowded or alone.

So a gain that is flat across the gap is equally the signature of pure self-masking
relief and of a bar that simply dropped. Recall-by-gap cannot tell them apart, and
neither can the sparse bench: §4a calls it the place "where the effect can only be an
artifact" because a second planted event can never enter the context — but §5.1 says in
terms that *"the test bin's own events sit in the null pool that judges them"*, so
self-masking is present there too.

**This probe changes the question from HOW MUCH the bar moves to WHERE.** Both detectors
expose their own bar per bin — LoCo the rolling threshold envelope (``signal.threshold``,
a step function over anchors), CoactDetect the surrogate null mean (``nullmean_prof``).
Run each at guard 0 and guard G on the same recording and the same seed, and split the
bins by whether the excised band actually held any events:

* **occupied** — at least one event inside [t − G/2, t + G/2]. The guard removed something.
* **empty** — no event anywhere in that band. The guard removed nothing at all.

The two hypotheses separate cleanly, and they make opposite predictions about the
**empty** column:

* **A threshold knob.** Excising a span shrinks the reference, and a bar estimated from
  less data moves for reasons having nothing to do with what was excised. Then the bar
  falls at empty anchors too, where there was nothing to relieve. §4a stands.
* **Self-masking relief.** The bar falls only where the band held events, because that is
  the only place removing them changes the estimate. Then §4a's conclusion is measuring a
  real mechanism through an instrument that cannot see it, and needs amending.

Anything in between is a mixture, and the ratio of the two columns is its size.

**A note on why the empty column exists at all.** LoCo lays anchors every
``thr_step_sec`` across the whole recording whether or not anything happened there, so
its empty stratum is free. CoactDetect computes a null only at candidate bins
(``obs >= min_rois``), and a candidate bin always contains its own events — its band can
never be empty. So the CoactDetect run drops ``min_rois`` to 1 **for profiling only**:
it does not change the guard arithmetic, the surrogate draw, or the null at any bin that
was already a candidate. It only extends the profile to bins the shipped setting would
not have scored. No detection number is reported from this run and none should be.
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
LOCO_THR_STEP_SEC = 15.0   # must match the thr_step_sec passed in loco_bar


def _pooled_events(sl):
    ext = recording_extent(sl)
    trains = stream_trains(sl.streams[STREAM], ext)
    ev = [np.asarray(t, float) for t in trains if np.size(t)]
    return (np.sort(np.concatenate(ev)) if ev else np.empty(0)), ext, trains


def loco_bar(sl, guard):
    """Bin centres and the rolling threshold envelope, at shipped FAST settings."""
    st = loco_detect(sl, rng_seed=7, bin_width_sec=1.0, context_win_sec=120.0,
                     thr_step_sec=15.0, merge_gap_sec=2.0, threshold_pctile=99.9,
                     n_surrogates=100, guard_sec=guard).streams[STREAM]
    return np.asarray(st.signal.t, float), np.asarray(st.signal.threshold, float)


def coact_bar(sl, guard):
    """Bin centres and the surrogate null mean. min_rois=0 — see the module docstring.

    It has to be 0, not 1: a bin with no events has ``obs == 0`` and would still
    fail an ``obs >= 1`` candidacy test, so the empty stratum — the whole point of
    this probe — would come back with n = 0. It did, on the first run.
    """
    _, ext, trains = _pooled_events(sl)
    d = coact_detect(trains, ext, rng_seed=7, int_win_sec=2.0, context_win_sec=60.0,
                     alpha=1e-4, n_surrogates=100, min_rois=0, guard_sec=guard)
    return np.asarray(d.ctr, float), np.asarray(d.nullmean_prof, float)


def occupancy(centres, events, band):
    """How many events sit inside [t - band/2, t + band/2] for each bin centre."""
    if events.size == 0:
        return np.zeros(centres.size, int)
    lo = np.searchsorted(events, centres - band / 2.0, side="left")
    hi = np.searchsorted(events, centres + band / 2.0, side="right")
    return hi - lo


def _anchor_of(centres, ext):
    """Each bin's nearest threshold anchor — LoCo's own rule (``loco.py``).

    This matters and it is easy to get wrong. **LoCo excises its guard band around
    the ANCHOR, not around the bin under test**, and a bin can sit up to
    ``thr_step_sec / 2`` — 7.5 s at the shipped FAST setting — from the anchor whose
    threshold it inherits. Asking whether *the bin's* neighbourhood was occupied
    therefore asks about a stretch of time the guard never touched. The first run of
    this probe did exactly that and reported LoCo as showing no relief at all.
    """
    from bugarach.detectors._shared import matlab_colon
    anchors = matlab_colon(ext[0], LOCO_THR_STEP_SEC, ext[1])
    idx = np.argmin(np.abs(centres[:, None] - anchors[None, :]), axis=1)
    return anchors[idx], idx


def run(which, maker, guard):
    bar = loco_bar if which == "loco" else coact_bar
    d_empty, d_occ = [], []
    for seed in SEEDS:
        sl, _ = maker(seed)
        events, ext, _ = _pooled_events(sl)
        t0, b0 = bar(sl, 0.0)
        t1, b1 = bar(sl, guard)
        n = min(t0.size, t1.size)
        t, b0, b1 = t0[:n], b0[:n], b1[:n]
        if which == "loco":
            # score each ANCHOR once, at the anchor's own position
            t, keep = _anchor_of(t, ext)
            _, first = np.unique(keep, return_index=True)
            t, b0, b1 = t[first], b0[first], b1[first]
        # a bin counts only where BOTH runs produced a finite bar; loco returns inf
        # for an empty span and coact NaN where a guarded window left no reference
        ok = np.isfinite(b0) & np.isfinite(b1)
        occ = occupancy(t, events, guard) > 0
        delta = b1 - b0
        # carry the unguarded bar alongside its shift: a delta of +0.007 means
        # nothing until you know whether the bar it moved is 3 or 300
        d_empty.append(np.stack([delta[ok & ~occ], b0[ok & ~occ]]))
        d_occ.append(np.stack([delta[ok & occ], b0[ok & occ]]))
    per_seed = np.array([[e[0].mean() if e.size else np.nan,
                          o[0].mean() if o.size else np.nan]
                         for e, o in zip(d_empty, d_occ)])
    return (np.concatenate(d_empty, axis=1), np.concatenate(d_occ, axis=1), per_seed)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--crowded", action="store_true",
                    help="also run the crowded recording (slower)")
    ap.add_argument("--selftest", action="store_true",
                    help="guard 0 against guard 0 — every delta must be exactly zero")
    a = ap.parse_args(argv)

    if a.selftest:
        # Can this probe's alarm ring? A guard of zero excises nothing, so if the
        # two runs differ at all the difference is the RNG or the code path, and
        # every number this tool reports is that difference plus noise.
        bad = 0
        for which in ("loco", "coact"):
            e, o, _ = run(which, lambda s: make_recording(REGIME, s), 0.0)
            d = np.concatenate([e[0], o[0]])
            worst = np.abs(d).max() if d.size else 0.0
            ok = worst == 0.0
            bad += 0 if ok else 1
            print(f"  {which:8s} {d.size:7d} bins   max |delta| = {worst:.3e}   "
                  + ("clean" if ok else "NOT REPRODUCIBLE — the tool is measuring itself"))
        return 1 if bad else 0

    makers = [("bench", lambda s: make_recording(REGIME, s))]
    if a.crowded:
        makers.append(("crowded", lambda s: make_crowded_recording(REGIME, s)))

    print(f"{len(SEEDS)} seeds, regime {REGIME!r}, shipped operating points\n"
          "delta = bar(guard) - bar(no guard), per bin, pooled over seeds\n"
          "EMPTY = the excised band held no events at all — the guard removed nothing\n")
    hdr = (f"  {'recording':9s} {'detector':8s} {'guard':>5s} "
           f"{'n empty':>8s} {'d empty +-sd / bar':>24s} {'n occup':>8s} "
           f"{'d occupied +-sd / bar':>25s} {'flip':>5s}")
    print(hdr)
    print("  " + "-" * (len(hdr) - 2))
    for label, maker in makers:
        for which in ("loco", "coact"):
            for g in GUARDS:
                e, o, ps = run(which, maker, g)
                me, be = (e[0].mean(), e[1].mean()) if e.size else (np.nan, np.nan)
                mo, bo = (o[0].mean(), o[1].mean()) if o.size else (np.nan, np.nan)
                # spread across seeds, not across bins: bins within a seed are not
                # independent, so a bin-wise sd would flatter the result
                se, so = ps[:, 0].std(ddof=1), ps[:, 1].std(ddof=1)
                flip = "yes" if np.all(ps[:, 0] > 0) and np.all(ps[:, 1] < 0) else "no"
                print(f"  {label:9s} {which:8s} {g:5.1f} {e.shape[1]:8d} "
                      f"{me:+7.4f}+-{se:.4f} on {be:5.2f} {o.shape[1]:8d} "
                      f"{mo:+7.4f}+-{so:.4f} on {bo:5.2f}  {flip:>4s}")
        print()

    print("READ IT LIKE THIS")
    print("  delta empty ~ delta occupied  ->  the bar fell where nothing was excised.")
    print("                                    A threshold knob. forks.md 4a stands.")
    print("  delta empty ~ 0, occupied < 0 ->  the bar moved only where the guard")
    print("                                    removed events. Self-masking relief,")
    print("                                    and 4a's instrument cannot see it.")
    print("  ratio is delta empty / delta occupied: 1.0 is a pure knob, 0.0 is pure")
    print("  masking relief, and anything between is the mixture's size.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
