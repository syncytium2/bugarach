#!/usr/bin/env python3
"""The chance floor per recording: how many co-active ROIs coincidence alone reaches once an hour.

    python tools/measure_chance_floor.py --out <folder> [--draws 200] [--jobs 20]

**Why.** Link 1 of the scoring design, the event floor, is open with Tony. His ruling so far:
*"participation should have a floor and a fraction because the number of ROIs varies"*. The open
parts are whether the count floor comes from chance, where the fraction comes from, and whether each
stream gets its own. ADR-0006 defines a false alarm as a call on coincidence the ROIs' own event
rates explain, and names the per-ROI rigid shift as the negative on real recordings. This tool
measures that null's floor on every recording. **It decides nothing**; it is the evidence.

**What already existed.** ``tools/probe_field_size.py`` gives a closed-form floor: independent ROIs at
one homogeneous rate, one stream, from a corpus-level rate read off ``assessment_real.json``, which
comes from the closed ``.mat`` store. Its own header says heterogeneous rates and within-ROI dead time
(0.40 s fast, 3.20 s slow) both move the true floor and are not modelled. Its functions are imported
here, not copied, and it is run per recording on the export folder so the two can be compared.

**The empirical floor.** For each recording, on its baseline window only (FOUNDATIONS §9):

* the **co-active count** at each sliding-window position is the number of ROIs with at least one
  onset in ``[t, t + w)``, with ``w`` the coincidence window CoactDetect uses at each stream's
  operating point (``int_win_sec``, read from the bench modules at run time, 2 s on all three
  when this was written);
* the **null** is :func:`tube_self_supervised.rigid_frames` with ``shared=False`` — one offset per ROI,
  uniform in ±*J*, *J* = 20 s — the null ADR-0006 rests on. It keeps each ROI's own timing, its
  rate, its dead time and the minute-scale shared change, and destroys the alignment between ROIs;
* a **call** at count *K* is a maximal run of window positions whose co-active count is at least *K*;
* the **floor** is the smallest *K* ≥ 1 whose calls on the null, pooled over ``--draws`` surrogate
  draws, come to at most :data:`FA_PER_HOUR` per hour of analysed baseline.

Every arm is evaluated on the window trimmed by *J* at both ends, so no onset the shift pushed out
of the window enters, as ``measure_slow_comodulation`` does. The floor is also given with frames in
place of runs (window positions at or above *K* per hour), which is the budget the closed forms use.

**Stability** is part of the record: the floor from the first and second half of the draws, and
how many recordings agree.

**The closed forms, per recording, from the same ROIs' rates on the same trimmed window:**

* ``probe_homogeneous`` — ``probe_field_size.floor_k`` exactly as that probe runs it: per-frame
  probability ``rate × dt × WIDEN_FRAMES`` at the recording's mean per-ROI rate, one chance frame
  per hour;
* ``probe_poisson_binomial`` — the same with each ROI's own rate (a Poisson-binomial count);
* ``window_homogeneous`` / ``window_poisson_binomial`` — the same null at the bench's window: an ROI
  is co-active with probability ``1 − exp(−rate × w)``, budget one window position per hour.

**How the floor scales with ROI count** (:func:`scaling`): the slope of log floor against log ROI
count (0 is a fixed count, 1 a fixed fraction), the same regression with the recording's log mean
rate beside it, and how far each of three rules misses — a fixed count, a fixed fraction of the ROI
count, and count plus fraction (``a + b × ROIs``) — in ROIs.

**By group** (DI, OVX, MALE, ORX in ``bugarach.groups`` order, and pooled): each number with
leave-one-out and a mouse-clustered bootstrap from :mod:`bugarach.influence`.
"""
from __future__ import annotations

import argparse
import json
import math
import multiprocessing as mp
import os
import sys
import time
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import probe_field_size as probe  # noqa: E402

from bugarach import surrogate_stats as ss  # noqa: E402

TAG = "chance-floor-2026-09-23"
FOLDER = "2026-09-23-chance-floor-66"
J_SEC = 20.0
"""The rigid shift's half-width: #768 measured this *J* leaving the minute-scale shared change in
place (ADR-0006, decision 3)."""
FA_PER_HOUR = probe.FA_PER_HOUR
STREAMS = ("fast", "slow", "combined")
BENCH_OF = {"fast": "bugarach.bench", "slow": "bugarach.bench_slow",
            "combined": "bugarach.bench_combined"}


def coincidence_window_sec(stream: str) -> float:
    """CoactDetect's ``int_win_sec`` at the stream's bench operating point, read, never retyped."""
    import importlib
    return float(importlib.import_module(BENCH_OF[stream]).OPERATING_POINTS["coact"]
                 .params["int_win_sec"])


# -- the count, its exceedances and the null ----------------------------------------------------
# One copy of the method, in the package since ADR-0008 (`bugarach.event_floor`). The names stay
# importable from here so the tests and the #790 run record that cite them still resolve.
from bugarach.event_floor import coactive_counts, exceedances, floor_of, null_curve  # noqa: E402,F401


# -- closed forms -----------------------------------------------------------------------------

def poisson_binomial_sf(ps) -> np.ndarray:
    """``P(X >= k)`` for ``k = 0 .. N``, X the number of successes among independent trials with
    probabilities ``ps``. Exact dynamic programme; N here is at most a few hundred."""
    pmf = np.zeros(len(ps) + 1)
    pmf[0] = 1.0
    for i, p in enumerate(ps):
        pmf[1:i + 2] = pmf[1:i + 2] * (1 - p) + pmf[:i + 1] * p
        pmf[0] *= 1 - p
    return np.cumsum(pmf[::-1])[::-1]


def pb_floor(ps, alpha: float) -> int:
    sf = poisson_binomial_sf(ps)
    ok = np.flatnonzero(sf[1:] <= alpha)
    return int(ok[0] + 1) if ok.size else len(ps) + 1


def closed_forms(rates_hz, dt: float, w_sec: float, fa_per_hour: float = FA_PER_HOUR) -> dict:
    """The four closed-form floors for one recording's per-ROI rates (see the module docstring).
    One chance frame, or one chance window position, per hour is the budget throughout."""
    r = np.asarray(rates_hz, float)
    N = r.size
    alpha = fa_per_hour / (3600.0 / dt)
    rbar = float(r.mean()) if N else 0.0
    p_probe = np.minimum(r * dt * probe.WIDEN_FRAMES, 1.0)
    p_win = 1.0 - np.exp(-r * w_sec)
    return dict(
        probe_homogeneous=(probe.floor_k(N, min(rbar * dt * probe.WIDEN_FRAMES, 1.0), alpha)
                           if rbar > 0 else 1),
        probe_poisson_binomial=pb_floor(p_probe, alpha),
        window_homogeneous=(probe.floor_k(N, float(1 - math.exp(-rbar * w_sec)), alpha)
                            if rbar > 0 else 1),
        window_poisson_binomial=pb_floor(p_win, alpha))


# -- one recording ----------------------------------------------------------------------------

def recording_task(args) -> dict:
    stream, rec, draws, w_sec = args
    a, b = rec.window
    L_full = b - a
    dt = rec.dt
    trains_full = [np.asarray(t, np.int64) - a for t in rec.trains]
    N = len(trains_full)
    runs, frames, hours, real, L, wf = null_curve(
        trains_full, L_full, dt, key=(TAG, stream, rec.recording_id), draws=draws,
        window_sec=w_sec, j_sec=J_SEC)
    rates = np.array([t.size for t in real], float) / (L * dt)
    real_runs, real_frames = exceedances(coactive_counts(real, L, wf), N)

    def per_hour(x, n):
        return x / (n * hours)

    tot_runs, tot_frames = runs.sum(axis=0), frames.sum(axis=0)
    floor = floor_of(per_hour(tot_runs, draws), FA_PER_HOUR)
    half = [floor_of(per_hour(runs[h], (draws + 1 - h) // 2), FA_PER_HOUR) for h in (0, 1)]
    return dict(
        stream=stream, recording_id=rec.recording_id, mouse=rec.mouse, group=rec.group,
        n_roi=N, n_active_roi=int(np.sum(rates > 0)), dt=dt, window_sec=w_sec,
        analysed_hours=hours, mean_rate_hz=float(rates.mean()) if N else 0.0,
        roi_rates_hz=rates.tolist(), draws=draws,
        floor=floor, floor_fraction=floor / N if N else float("nan"),
        floor_frames=floor_of(per_hour(tot_frames, draws), FA_PER_HOUR),
        floor_first_half=half[0], floor_second_half=half[1],
        null_calls_per_hour=per_hour(tot_runs, draws).tolist(),
        null_frames_per_hour=per_hour(tot_frames, draws).tolist(),
        real_calls_per_hour=(real_runs / hours).tolist(),
        real_calls_per_hour_at_floor=float(real_runs[min(floor, N + 1)] / hours),
        null_calls_per_hour_at_floor=float(per_hour(tot_runs, draws)[min(floor, N + 1)]),
        closed_form=closed_forms(rates, dt, w_sec))


# -- how the floor scales ---------------------------------------------------------------------

def _ols(X, y):
    X = np.column_stack([np.ones(len(y))] + [np.asarray(x, float) for x in X])
    coef, *_ = np.linalg.lstsq(X, np.asarray(y, float), rcond=None)
    return coef


def scaling(rows) -> dict:
    """How the floor moves with ROI count across ``rows``: log–log slope (0 = a fixed count, 1 = a
    fixed fraction), the same with log mean rate beside it, and how far each of three rules misses
    (median absolute miss, in ROIs). Recordings with no onsets have no rate to take a log of and
    are left out of the rate regression only; they are counted in ``n_without_onsets``."""
    N = np.array([r["n_roi"] for r in rows], float)
    k = np.array([r["floor"] for r in rows], float)
    rate = np.array([r["mean_rate_hz"] for r in rows], float)
    nan = float("nan")
    if len(rows) < 3:
        return dict(n=len(rows), slope_log_floor_on_log_rois=nan)
    slope = float(_ols([np.log(N)], np.log(k))[1])
    ok = rate > 0
    both = (_ols([np.log(N[ok]), np.log(rate[ok])], np.log(k[ok]))
            if ok.sum() >= 4 else [nan, nan, nan])
    c = float(np.median(k))
    f = float(np.median(k / N))
    a, b = (float(x) for x in _ols([N], k))
    return dict(
        n=len(rows), n_without_onsets=int((~ok).sum()),
        slope_log_floor_on_log_rois=slope,
        slope_with_rate=dict(log_rois=float(both[1]), log_mean_rate=float(both[2])),
        count_rule=dict(count=c, median_miss_rois=float(np.median(np.abs(k - c)))),
        fraction_rule=dict(fraction=f, median_miss_rois=float(np.median(np.abs(k - f * N)))),
        count_and_fraction_rule=dict(count=a, fraction=b,
                                     median_miss_rois=float(np.median(np.abs(k - a - b * N)))))


GROUP_STATS = ("median_floor", "median_floor_fraction", "slope_log_floor_on_log_rois")


def group_stat(rows, name: str) -> float:
    if not rows:
        return float("nan")
    if name == "median_floor":
        return float(np.median([r["floor"] for r in rows]))
    if name == "median_floor_fraction":
        return float(np.median([r["floor_fraction"] for r in rows]))
    if name == "slope_log_floor_on_log_rois":
        return float(scaling(rows).get("slope_log_floor_on_log_rois", float("nan")))
    raise ValueError(name)


def by_group(rows, n_boot: int, seed_key) -> dict:
    """Per group and pooled: each :data:`GROUP_STATS` value with a mouse bootstrap and leave-one-out,
    the pair test, and :func:`scaling`."""
    from bugarach import influence
    from bugarach.groups import in_group_order

    groups = in_group_order(r["group"] for r in rows if r.get("group"))
    sets = {g: [r for r in rows if r.get("group") == g] for g in groups}
    sets_all = {**sets, "pooled": rows}

    def ident(r):
        return r["recording_id"]

    out = dict(groups=groups, recordings={g: len(v) for g, v in sets_all.items()},
               mice={g: len({r["mouse"] for r in v}) for g, v in sets_all.items()},
               scaling={g: scaling(v) for g, v in sets_all.items()}, stats={})
    for name in GROUP_STATS:
        def stat(rs, name=name):
            return group_stat(rs, name)

        loo = {g: influence.leave_one_out(v, stat, ident) for g, v in sets_all.items()}
        per, boots = {}, {}
        for g, v in sets_all.items():
            rs = ss.rng_of((TAG, *seed_key, name, g))
            b = np.array(influence.mouse_bootstrap(v, stat, lambda r: r["mouse"], n_boot, rs),
                         float)
            boots[g] = b
            per[g] = dict(value=stat(v), leave_one_out=loo[g],
                          interval=(np.nanpercentile(b, [2.5, 97.5]).tolist()
                                    if np.isfinite(b).any() else None))
        pairs = influence.pairwise(loo, groups)
        # A median of whole-ROI floors rarely moves when one recording goes, so a leave-one-out
        # range is often a single point and "outlives" is then nearly free. The bootstrap of the
        # difference, resampling each group's mice, is the test that binds; both go in the record.
        for pair, p in pairs.items():
            g, h = pair.split(" - ")
            d = boots[g] - boots[h]
            p["bootstrap_interval"] = (np.nanpercentile(d, [2.5, 97.5]).tolist()
                                       if np.isfinite(d).any() else None)
            p["robust"] = bool(p["outlives"] and p["bootstrap_interval"] is not None
                               and (p["bootstrap_interval"][0] > 0
                                    or p["bootstrap_interval"][1] < 0))
        out["stats"][name] = dict(groups=per, pairwise=pairs)
    return out


# -- run --------------------------------------------------------------------------------------

def summary_only(R: dict) -> dict:
    """What the repository keeps: per-recording floors and counts, no per-ROI rates and no curves
    over K (those stay in the darkroom's ``results.json``)."""
    drop = {"roi_rates_hz", "null_calls_per_hour", "null_frames_per_hour", "real_calls_per_hour"}
    keep = {k: v for k, v in R.items() if k != "streams"}
    keep["streams"] = {s: dict(S, rows=[{k: v for k, v in r.items() if k not in drop}
                                        for r in S["rows"]])
                       for s, S in R["streams"].items()}
    return keep


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--out", type=Path, default=None,
                    help=f"folder for results.json and summary.json; default <darkroom>/{FOLDER}")
    ap.add_argument("--draws", type=int, default=200, help="rigid-shift draws per recording")
    ap.add_argument("--boot", type=int, default=1000, help="mouse bootstrap resamples")
    ap.add_argument("--jobs", type=int, default=max(1, (os.cpu_count() or 2) - 2))
    ap.add_argument("--limit", type=int, default=None, help="first N recordings (smoke runs)")
    a = ap.parse_args(argv)
    if a.out is None:
        from bugarach.paths import darkroom, unresolved_message
        a.out = darkroom(FOLDER, create=True)
        if a.out is None:
            raise SystemExit(unresolved_message("--out"))
    a.out.mkdir(parents=True, exist_ok=True)

    import measure_slow_comodulation as msc  # its loader: baseline only, combined built the same way
    from bugarach import dataset

    t0 = time.time()
    R = dict(tag=TAG, dataset=dataset.stamp(), j_sec=J_SEC, fa_per_hour=FA_PER_HOUR,
             draws=a.draws, null="rigid_frames(shared=False), one offset per ROI in +-J",
             call="maximal run of sliding-window positions with at least K co-active ROIs",
             probe_widen_frames=probe.WIDEN_FRAMES, streams={})
    with mp.Pool(a.jobs) as pool:
        for stream in STREAMS:
            w = coincidence_window_sec(stream)
            recs, skipped, _ = msc.load(msc.LAB_ROLE, stream, a.limit)
            rows = pool.map(recording_task, [(stream, r, a.draws, w) for r in recs])
            agree = [r["floor_first_half"] == r["floor_second_half"] == r["floor"] for r in rows]
            R["streams"][stream] = dict(
                window_sec=w, rows=rows, skipped=skipped,
                stability=dict(halves_agree_with_full=int(sum(agree)), recordings=len(rows),
                               max_half_difference=int(max(
                                   abs(r["floor_first_half"] - r["floor_second_half"])
                                   for r in rows))),
                by_group=by_group(rows, a.boot, (stream,)))
            print(f"{stream}: {len(rows)} recordings, window {w:g} s, "
                  f"{sum(agree)} of {len(rows)} floors agree across halves of the draws, "
                  f"{time.time() - t0:.0f} s", flush=True)
            G = R["streams"][stream]["by_group"]
            for g in [*G["groups"], "pooled"]:
                S = G["scaling"][g]
                mf = G["stats"]["median_floor"]["groups"][g]
                print(f"  {g:6s} {G['recordings'][g]:2d} recordings: median floor "
                      f"{mf['value']:.1f} ROIs {mf['interval']}, slope on log ROIs "
                      f"{S['slope_log_floor_on_log_rois']:.2f}", flush=True)
    R["elapsed_sec"] = time.time() - t0
    (a.out / "results.json").write_text(json.dumps(R))
    (a.out / "summary.json").write_text(json.dumps(summary_only(R), indent=1))
    print(f"wrote {a.out / 'results.json'} and summary.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
