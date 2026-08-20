#!/usr/bin/env python3
"""Do the same cells fire in the same ORDER, event after event?

    python tools/synfire_scan.py --store <export folder> --out <dir> --stream fast

A different question from cell assemblies, and one nothing in this project had asked.
Assemblies are about *which* cells take part; this is about *which follows which* —
whether the recording resembles a synfire pattern, in which the same units repeatedly
fire from leader to follower. A field can have either without the other.

**Method** — SPIKE-order / Spike Train Order (Kreuz, Satuvuori, Pofahl & Mulansky 2017,
*New J. Phys.* 19:043028, doi:10.1088/1367-2630/aa68c3), via PySpike's implementation by
the same authors. Each recording's ROI onset trains are sorted from leader to follower by
simulated annealing over the spike-directionality matrix, and the **Synfire Indicator** is
read off that optimal sorting: 0 for no consistent order, 1 for a perfect synfire pattern.

**Two traps this tool exists to avoid, both hit while writing it.**

1. ``optimal_spike_train_sorting`` returns ``(permutation, F)`` and its docstring calls
   ``F`` the synfire indicator. It is **not normalized** — the function computes the
   directionality matrix with ``normalize=False``, so ``F`` is a raw sum that scales with
   spike count (324 on the first recording tried, where the indicator is 0.021). Quoting
   it as an indicator would produce numbers that are not in [0, 1] and cannot be compared
   across recordings. The indicator is ``spike_train_order`` evaluated on the *sorted*
   trains, which normalizes by default. Both are recorded below, the raw one only so a
   cSPIKE cross-check has something to match.
2. **The sorting is stochastic.** Simulated annealing has no seed parameter here, and
   interface2 already found the MATLAB equivalent lands on different local optima when the
   RNG path shifts (``SYNCHRO_PROGRESS.md``). Every optimisation below is therefore
   repeated ``--restarts`` times and the best F kept, and the numpy seed is fixed per
   recording so a rerun reproduces.

**The null.** Per-ROI circular shift inside the analysis window — this project's standing
surrogate (FOUNDATIONS §2), which preserves each ROI's own event count and destroys every
cross-ROI timing relation. The observed value is compared against surrogates put through
*the same* optimisation, because sorting maximises F and comparing an optimised value to
an unoptimised one would find order in noise.

Baseline windows only, and the producer's analysis window where it gives one. Reads an
export folder and nothing else.
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

import numpy as np

K_MIN_ACTIVE = 3
"""Fewer than three active ROIs cannot express a leader-follower order."""


def _trains(stream, window, n_rois, *, keep_silent: bool = False):
    """Per-ROI onset trains inside the window, as PySpike SpikeTrains.

    **ROIs with no events in the window are dropped, and that is load-bearing.**
    PySpike scores a pair of empty trains as ``(e=1, m=1)`` — a *perfectly ordered*
    pair — so every pair of silent ROIs adds a maximal-order term to the totals that
    ``spike_train_order`` averages. A recording with 21 silent ROIs of 24 contributes
    210 such pairs against a handful of real ones, and its indicator is then mostly a
    count of cells that never fired. Measured on this corpus: the top of the fast
    distribution is the emptiest recordings, and ``20240723_22`` (17 events, 21 of 24
    ROIs silent) scores 0.353 with them and 0.059 without.

    Silence is not order, and a cell that never fired has no latency to be ordered by.
    This matches `bugarach.graph.modularity_vs_null`, which drops zero-event cells for
    the same reason on the other instrument.

    ``keep_silent=True`` restores the padded behaviour, for reproducing pre-fix numbers.
    """
    import pyspike as spk
    out = []
    for i in range(n_rois):
        v = np.asarray(stream.locs[i], dtype=float)
        v = v[np.isfinite(v)]
        v = v[(v >= window[0]) & (v <= window[1])]
        if v.size == 0 and not keep_silent:
            continue
        out.append(spk.SpikeTrain(np.sort(v), edges=[window[0], window[1]]))
    return out


def _indicator(trains, restarts: int):
    """Synfire indicator at the best sorting found, plus the raw annealing score.

    ``restarts`` exists because the annealing is stochastic and unseeded; the best of
    several runs is a defensible summary where a single run is a coin toss.
    """
    import pyspike as spk
    best_f, best_raw = -np.inf, np.nan
    for _ in range(max(1, restarts)):
        order, raw = spk.optimal_spike_train_sorting(trains)
        f = spk.spike_train_order([trains[i] for i in order])
        if f > best_f:
            best_f, best_raw = float(f), float(raw)
    return best_f, best_raw


def _relabel(trains, rng, window):
    """Keep every spike time; permute which ROI each one belongs to.

    **This is the null the question needs, and the circular shift was not.** A
    circular shift moves each ROI's train independently, which destroys the
    coordinated events themselves — so any recording that *has* events beats it,
    whether or not the participants fire in a consistent order. Measured: on
    generated recordings containing no planted order at all, the shift null called
    60% of them significant. It was answering "is there coordination", a question
    already settled, rather than "is there order".

    Relabelling holds the pooled event structure exactly fixed — same times, same
    number of spikes per ROI — and destroys only the assignment of cells to
    latencies within it. That is the thing a synfire pattern is made of.
    """
    import pyspike as spk
    counts = [t.spikes.size for t in trains]
    pooled = np.concatenate([t.spikes for t in trains]) if any(counts) \
        else np.empty(0)
    labels = np.concatenate([np.full(c, i) for i, c in enumerate(counts)]) \
        if any(counts) else np.empty(0, dtype=int)
    labels = rng.permutation(labels)
    out = []
    for i in range(len(trains)):
        v = np.sort(pooled[labels == i]) if pooled.size else np.empty(0)
        out.append(spk.SpikeTrain(v, edges=[window[0], window[1]]))
    return out


def _shift(trains, rng, window):
    """Circular shift each ROI independently inside the window."""
    import pyspike as spk
    dur = window[1] - window[0]
    out = []
    for t in trains:
        v = t.spikes
        if v.size:
            v = np.sort(np.mod(v - window[0] + rng.rand() * dur, dur) + window[0])
        out.append(spk.SpikeTrain(v, edges=[window[0], window[1]]))
    return out


def scan(store: Path, *, stream: str, n_surrogates: int, restarts: int,
         null: str = "relabel", limit: int | None = None,
         keep_silent: bool = False) -> dict:
    from bugarach.io import load_folder

    slices = load_folder(store)
    if limit:
        slices = slices[:limit]
    rows, skipped = [], {"no_baseline": 0, "no_stream": 0, "too_few_active": 0}
    t0 = time.time()

    for n, s in enumerate(slices):
        base = [r for r in (s.regions or [])
                if (getattr(r, "name", "") or "").strip().lower().startswith("base")]
        if not base:
            skipped["no_baseline"] += 1
            continue
        r = max(base, key=lambda r: r.end_sec - r.start_sec)
        win = ((r.analysis_start_sec, r.analysis_end_sec)
               if getattr(r, "has_analysis_window", False)
               else (r.start_sec, r.end_sec))
        if stream not in s.streams:
            skipped["no_stream"] += 1
            continue
        st = s.streams[stream]
        trains = _trains(st, win, st.n_rois, keep_silent=keep_silent)
        active = sum(1 for t in trains if t.spikes.size)
        if active < K_MIN_ACTIVE:
            skipped["too_few_active"] += 1
            continue

        # Seeded per recording: the annealing is unseeded internally, so this is what
        # makes a rerun reproduce.
        np.random.seed(abs(hash(s.slice_id)) % (2 ** 31))
        rng = np.random.RandomState(abs(hash(s.slice_id)) % (2 ** 31))

        f_obs, raw_obs = _indicator(trains, restarts)
        surro = _relabel if null == "relabel" else _shift
        nulls = np.array([_indicator(surro(trains, rng, win), restarts)[0]
                          for _ in range(n_surrogates)], dtype=float)
        # Phipson & Smyth: never a zero p-value from a finite surrogate set.
        p = float((1 + int((nulls >= f_obs).sum())) / (1 + n_surrogates))
        z = float((f_obs - nulls.mean()) / nulls.std()) if nulls.std() > 0 \
            else float("nan")

        ident = {k: v for k, v in (getattr(s, "meta", None) or {}).items()
                 if k != "slice_id"}
        rows.append(dict(
            **ident, slice_id=s.slice_id, stream=stream,
            n_roi=int(st.n_rois), n_active=int(active),
            n_trains_scored=int(len(trains)),
            n_spikes=int(sum(t.spikes.size for t in trains)),
            window_sec=float(win[1] - win[0]),
            synfire=f_obs, synfire_raw_unnormalized=raw_obs,
            null_mean=float(nulls.mean()), null_sd=float(nulls.std()),
            p=p, z=z))
        # Flushed, and every recording rather than every twentieth. Redirected
        # stdout is block-buffered, so the old form emitted nothing at all until the
        # run ended — four silent minutes that read as a hang rather than as work.
        done, el = n + 1, time.time() - t0
        print(f"  {done}/{len(slices)}  {el:.0f}s elapsed, "
              f"~{el / max(1, len(rows)) * (len(slices) - done):.0f}s left "
              f"({s.slice_id}: {len(trains)} trains scored)", flush=True)

    return {"store": store.name, "stream": stream, "null": null,
            "silent_rois_kept": bool(keep_silent),
            "n_surrogates": n_surrogates,
            "restarts": restarts, "skipped": skipped,
            "n_recordings": len(rows), "elapsed_sec": round(time.time() - t0, 1),
            "rows": rows}


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--store", type=Path, required=True,
                   help="an export folder (data in, not a deliverable out)")
    p.add_argument("--out", type=Path, default=None,
                   help="destination; default $BUGARACH_DARKROOM")
    p.add_argument("--stream", default="fast")
    p.add_argument("--n-surrogates", type=int, default=200)
    p.add_argument("--null", choices=["relabel", "shift"],
                   default="relabel",
                   help="relabel keeps the events and permutes which ROI "
                        "owns each spike; shift is the old per-ROI circular "
                        "shift, kept only to reproduce its 60%% false-positive "
                        "rate")
    p.add_argument("--restarts", type=int, default=3,
                   help="annealing restarts per optimisation; the sort is stochastic")
    p.add_argument("--keep-silent-rois", action="store_true",
                   help="hand silent ROIs to the sorter, as this tool did before "
                        "2026-08-19. PySpike scores a pair of empty trains as a "
                        "perfectly ordered pair, so this inflates the indicator in "
                        "proportion to how many cells never fired. Kept only to "
                        "reproduce the pre-fix numbers.")
    p.add_argument("--limit", type=int, default=None)
    a = p.parse_args(argv)

    res = scan(a.store, stream=a.stream, n_surrogates=a.n_surrogates,
               restarts=a.restarts, null=a.null, limit=a.limit,
               keep_silent=a.keep_silent_rois)

    from bugarach.paths import darkroom, unresolved_message
    out = a.out or darkroom()
    if out is None:
        print(unresolved_message(), file=sys.stderr)
        return 1
    out.mkdir(parents=True, exist_ok=True)
    suffix = "_silentkept" if a.keep_silent_rois else ""
    dest = out / f"synfire_{a.stream}_{a.null}{suffix}.json"
    dest.write_text(json.dumps(res, indent=1))

    f = np.array([r["synfire"] for r in res["rows"]], dtype=float)
    pv = np.array([r["p"] for r in res["rows"]], dtype=float)
    print(f"\n{res['n_recordings']} recordings, {a.stream}, "
          f"{a.n_surrogates} surrogates x {a.restarts} restarts "
          f"({res['elapsed_sec']}s)")
    print(f"  skipped: {res['skipped']}")
    if f.size:
        print(f"  synfire indicator: median {np.median(f):.4f}  "
              f"IQR {np.percentile(f, 25):.4f}-{np.percentile(f, 75):.4f}  "
              f"max {f.max():.4f}")
        print(f"  above its own null at p<0.05: {int((pv < 0.05).sum())}/{pv.size}")
    print(f"wrote {dest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
