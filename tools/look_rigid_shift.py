#!/usr/bin/env python3
"""One exploratory look at rigid shift: does it hide from a coordination-blind classifier while
it removes planted coordination? Baseline windows only.

    python tools/look_rigid_shift.py --out <folder>            # the run
    python tools/look_rigid_shift.py --out <folder> --limit 6 --quick   # smoke

**Exploratory, not confirmatory.** Tony set aside the pre-registration machinery on
2026-09-14 in favour of one figure he reads himself. The thresholds drawn on that figure are
the ones he signed, used as reference lines, not as a decision rule.

What it measures, per stream (fast, slow) and per displacement *J* (1.6, 2.5, 5.0 s fast;
1.4, 2.8, 5.6 s slow):

* **Leak.** Each interior 60 s baseline window (whole windows from the baseline start, the
  trailing part dropped, the first and last excluded) is paired with the same window of one
  rigid-shift draw of its recording. A linear forced choice on per-ROI features pooled by
  symmetric statistics — **without the edge-band features**, which see coordination under a
  shift — is scored with mouse-grouped folds. Its accuracy is bootstrapped by resampling
  **mice** (refitting each time, fresh folds) and, beside it, by resampling **slices**. Uniform
  dither at the same *J* is drawn beside it as the reference a leak looks like.
* **Destruction.** Synthetic twins sized like the stream (20 of them per participation level; median ROIs and length, per-ROI
  rates resampled from its baseline windows, its observed floor) with and without planted
  events at participation 0.2 and 0.5. Both twins go through the surrogate with one key and are
  scored by the assessor's selection-corrected coactivity excess at a 1.0 s bin (and 2.0 s on
  slow). Retained = (planted − unplanted) after ÷ (planted − unplanted) before. Controls:
  homogeneous resample (should remove), do-nothing scored with a different assessor seed
  (should keep).
* **Count.** Occupied frames per ROI per interior window, surrogate minus real, as a share of
  the real count; ``edge_thinning`` at a fixed 5 s beside it as a change the measure must see.

Recordings come through :func:`bugarach.surrogate_stats.recordings_from_slices`; any whose
window is not the producer's baseline region is refused, and the run stops if that leaves the
folder short. Every random key carries the tag ``look-2026-09-15``.
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

from bugarach import assess                                 # noqa: E402
from bugarach import surrogate_discriminator as sd          # noqa: E402
from bugarach import surrogate_stats as ss                  # noqa: E402
from bugarach import surrogates as sg                       # noqa: E402

TAG = "look-2026-09-15"
J_SEC = {"fast": (1.6, 2.5, 5.0), "slow": (1.4, 2.8, 5.6)}
BINS_SEC = {"fast": (1.0,), "slow": (1.0, 2.0)}
WINDOW_SEC = 60.0
EDGE_SEC = 5.0
PARTICIPATION = (0.2, 0.5)
K_SCAN = (3, 4, 6, 8)
EDGE_THIN_SEC = 5.0


def seed31(*key) -> int:
    return int(ss.seed_of((TAG,) + tuple(key)) & 0x7FFFFFFF)


# -- data -------------------------------------------------------------------------------------

def load(stream: str, limit: int | None):
    from bugarach import dataset
    from bugarach.io import load_folder
    slices = load_folder(dataset.current("steps_excluded"))
    if limit:
        slices = slices[:limit]
    recs, skipped = ss.recordings_from_slices(slices, stream)
    refused = [r.recording_id for r in recs if not r.window_source.startswith("baseline region")]
    if refused:
        raise SystemExit(f"refusing non-baseline windows in {stream}: {refused}")
    return recs, skipped


def interior_windows(rec):
    w = int(np.floor(WINDOW_SEC / rec.dt + 0.5))
    a, b = rec.window
    n = (b - a) // w
    wins = [(a + i * w, a + (i + 1) * w) for i in range(n)]
    return wins[1:-1]


# -- leak -------------------------------------------------------------------------------------

def feature_mask():
    names = sd.feature_names()
    keep = np.array(["edge" not in n for n in names])
    return keep, [n for n, k in zip(names, keep) if k]


def pairs_for(recs, stream, name, J_frames_of):
    """Features of (real, surrogate) for every interior window of every recording."""
    Xr, Xs, mice, slices, groups = [], [], [], [], []
    keep, _ = feature_mask()
    for r in recs:
        wins = interior_windows(r)
        if not wins:
            continue
        params = {} if name in ("do_nothing", "homogeneous_resample") else {"J": J_frames_of(r)}
        sur = sg.generate(name, r.trains, r.window, (TAG, "leak", r.recording_id, stream, name,
                                                    params.get("J", 0.0)), **params).trains
        band = max(1, int(np.floor(EDGE_SEC / r.dt + 0.5)))
        a, b = sd.pair_features([r.trains] * len(wins), [sur] * len(wins), wins, band)
        Xr.append(a[:, keep]); Xs.append(b[:, keep])
        mice += [r.mouse] * len(wins); slices += [r.recording_id] * len(wins)
        groups += [r.group or ""] * len(wins)
    return (np.vstack(Xr), np.vstack(Xs), np.asarray(mice), np.asarray(slices),
            np.asarray(groups))


def cv_correct(Xr, Xs, folds_on, seed):
    folds = sd.mouse_folds(folds_on, 5, seed)
    scales = {int(f): sd._scale(np.vstack([Xr[folds != f], Xs[folds != f]]))
              for f in np.unique(folds)}
    correct, _ = sd._cv_correct(Xr - Xs, scales, folds, np.ones(len(folds_on)), 1.0)
    return correct


def refit_bootstrap(Xr, Xs, mice, unit, n_boot, seed):
    """Accuracy point estimate and a bootstrap distribution, resampling ``unit`` (mouse or slice)
    and refitting with fresh mouse-grouped folds each time."""
    point = float(cv_correct(Xr, Xs, mice, seed).mean())
    uniq, inv = np.unique(unit, return_inverse=True)
    idx_of = [np.flatnonzero(inv == u) for u in range(uniq.size)]
    rs = np.random.RandomState(seed)
    out = np.empty(n_boot)
    for b in range(n_boot):
        pick = rs.randint(uniq.size, size=uniq.size)
        idx = np.concatenate([idx_of[p] for p in pick])
        m = mice[idx]
        if np.unique(m).size < 2:
            out[b] = np.nan
            continue
        out[b] = cv_correct(Xr[idx], Xs[idx], m, int(rs.randint(2**31 - 1))).mean()
    return point, out


def summarize(point, dist):
    d = dist[np.isfinite(dist)]
    return {"accuracy": point, "p1_67": float(np.percentile(d, 100 / 60)),
            "p98_33": float(np.percentile(d, 100 - 100 / 60)),
            "p2_5": float(np.percentile(d, 2.5)), "p97_5": float(np.percentile(d, 97.5)),
            "n_boot": int(d.size)}


def leak_task(args):
    stream, name, J_sec, n_boot, limit = args
    recs, _ = load(stream, limit)
    Xr, Xs, mice, slices, groups = pairs_for(recs, stream, name,
                                             lambda r: round(J_sec / r.dt, 9))
    res = {"stream": stream, "generator": name, "J_sec": J_sec, "n_pairs": int(len(mice)),
           "n_mice": int(np.unique(mice).size), "n_slices": int(np.unique(slices).size)}
    seed = seed31("leak", stream, name, J_sec)
    p, dm = refit_bootstrap(Xr, Xs, mice, mice, n_boot, seed)
    res["by_mouse"] = summarize(p, dm)
    p, dsl = refit_bootstrap(Xr, Xs, mice, slices, n_boot, seed + 1)
    res["by_slice"] = summarize(p, dsl)
    correct = cv_correct(Xr, Xs, mice, seed)
    res["by_group"] = {g: {"accuracy": float(correct[groups == g].mean()),
                           "n_pairs": int((groups == g).sum())}
                       for g in sorted(set(groups))}
    return res


# -- count ------------------------------------------------------------------------------------

def count_task(args):
    stream, name, J_sec, n_boot, limit = args
    recs, _ = load(stream, limit)
    per_mouse_d, per_mouse_r, per_slice_d, per_slice_r, mice, slices = {}, {}, [], [], [], []
    for r in recs:
        wins = interior_windows(r)
        if not wins:
            continue
        if name == "edge_thinning":
            params = {"J": round(EDGE_THIN_SEC / r.dt, 9),
                      "analysis_window": int(np.floor(WINDOW_SEC / r.dt + 0.5))}
        else:
            params = {"J": round(J_sec / r.dt, 9)}
        sur = sg.generate(name, r.trains, r.window,
                          (TAG, "count", r.recording_id, stream, name, J_sec), **params).trains
        d = rr = 0
        for a, b in wins:
            for real, s in zip(r.trains, sur):
                rr += np.unique(real[(real >= a) & (real < b)]).size
                d += np.unique(s[(s >= a) & (s < b)]).size - np.unique(real[(real >= a) & (real < b)]).size
        per_slice_d.append(d); per_slice_r.append(rr); slices.append(r.recording_id)
        mice.append(r.mouse)
    per_slice_d = np.asarray(per_slice_d, float); per_slice_r = np.asarray(per_slice_r, float)
    mice = np.asarray(mice)
    point = float(per_slice_d.sum() / per_slice_r.sum())
    rs = np.random.RandomState(seed31("count", stream, name, J_sec))

    def boot(unit):
        uniq, inv = np.unique(unit, return_inverse=True)
        D = np.bincount(inv, per_slice_d); Rr = np.bincount(inv, per_slice_r)
        pick = rs.randint(uniq.size, size=(n_boot, uniq.size))
        return summarize(point, D[pick].sum(1) / Rr[pick].sum(1))

    return {"stream": stream, "generator": name, "J_sec": J_sec,
            "change_share": point, "by_mouse": boot(mice), "by_slice": boot(np.asarray(slices)),
            "n_slices": int(len(slices))}


# -- destruction ------------------------------------------------------------------------------

def excess(trains, n_frames, dt, bin_sec, n_assess, seed):
    from bugarach.io import slice_from_events
    s = slice_from_events({"events": [np.asarray(v, float) * dt for v in trains]},
                          dt=dt, slice_id="twin")
    res = assess.assess_coactivity(s, stream="events", window=(0.0, n_frames * dt),
                                   min_rois=K_SCAN, bin_width_sec=bin_sec,
                                   n_surrogates=n_assess, rng_seed=int(seed),
                                   region_min_sec=0.0)
    return {int(a.min_rois): float(a.coact_excess) for a in res}


def twins_for(stream, limit, n_twins):
    recs, _ = load(stream, limit)
    dt = float(np.median([r.dt for r in recs]))
    n_frames = int(np.median([r.window[1] - r.window[0] for r in recs]))
    n_roi = int(np.median([len(r.trains) for r in recs]))
    rates = np.concatenate([[v.size / max(1, r.window[1] - r.window[0]) for v in r.trains]
                            for r in recs])
    floor = ss.observed_floor(recs) or 1
    out = {}
    for p in PARTICIPATION:
        for t in range(n_twins):
            g = np.random.RandomState(seed31("twin-counts", stream, p, t))
            counts = g.poisson(g.choice(rates, size=n_roi, replace=True) * n_frames)
            pl, un, _ = ss.destruction_twins(n_roi, n_frames, dt, int(floor), counts, p,
                                             seed=seed31("twin", stream, p, t))
            out[(p, t)] = (pl, un)
    return {"dt": dt, "n_frames": n_frames, "n_roi": n_roi, "floor_frames": int(floor),
            "twins": out}


def destruction_task(args):
    stream, bin_sec, p, n_twins, n_draws, n_assess, limit = args
    tw = twins_for(stream, limit, n_twins)
    dt, n_frames = tw["dt"], tw["n_frames"]
    variants = [("rigid_shift", J) for J in J_SEC[stream]] + [("homogeneous_resample", None),
                                                               ("do_nothing", None)]
    base_seed = seed31("assess", stream, bin_sec, p)
    rows = {f"{n}@{J}" if J else n: [] for n, J in variants}
    for t in range(n_twins):
        pl, un = tw["twins"][(p, t)]
        b_pl = excess(pl, n_frames, dt, bin_sec, n_assess, base_seed)
        b_un = excess(un, n_frames, dt, bin_sec, n_assess, base_seed)
        for name, J in variants:
            params = {"J": round(J / dt, 9)} if J else {}
            after_seed = base_seed + 7 if name == "do_nothing" else base_seed
            a_pl = {K: [] for K in K_SCAN}; a_un = {K: [] for K in K_SCAN}
            for k in range(n_draws if name != "do_nothing" else 1):
                key = (TAG, "destroy", stream, bin_sec, p, t, name, J or 0, k)
                s_pl = sg.generate(name, pl, (0, n_frames), key, **params).trains
                s_un = sg.generate(name, un, (0, n_frames), key, **params).trains
                e_pl = excess(s_pl, n_frames, dt, bin_sec, n_assess, after_seed)
                e_un = excess(s_un, n_frames, dt, bin_sec, n_assess, after_seed)
                for K in K_SCAN:
                    a_pl[K].append(e_pl[K]); a_un[K].append(e_un[K])
            rows[f"{name}@{J}" if J else name].append({
                "twin": t,
                "before": {K: b_pl[K] - b_un[K] for K in K_SCAN},
                "after": {K: float(np.mean(a_pl[K]) - np.mean(a_un[K])) for K in K_SCAN}})
    return {"stream": stream, "bin_sec": bin_sec, "participation": p, "n_twins": n_twins,
            "n_draws": n_draws, "n_assess_surrogates": n_assess,
            "twin_shape": {k: tw[k] for k in ("dt", "n_frames", "n_roi", "floor_frames")},
            "variants": rows}


# -- main -------------------------------------------------------------------------------------

def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", required=True)
    ap.add_argument("--limit", type=int, default=None, help="first N recordings (smoke)")
    ap.add_argument("--quick", action="store_true", help="tiny counts for a smoke run")
    ap.add_argument("--jobs", type=int, default=12)
    a = ap.parse_args(argv)
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    n_boot = 40 if a.quick else 1000
    n_twins, n_draws, n_assess = (2, 2, 20) if a.quick else (20, 20, 200)

    tasks = []
    for stream in ("fast", "slow"):
        for J in J_SEC[stream]:
            tasks.append(("leak", (stream, "rigid_shift", J, n_boot, a.limit)))
            tasks.append(("leak", (stream, "uniform_dither", J, n_boot, a.limit)))
            tasks.append(("count", (stream, "rigid_shift", J, n_boot, a.limit)))
        tasks.append(("count", (stream, "edge_thinning", EDGE_THIN_SEC, n_boot, a.limit)))
        for bin_sec in BINS_SEC[stream]:
            for p in PARTICIPATION:
                tasks.append(("destruction", (stream, bin_sec, p, n_twins, n_draws, n_assess,
                                              a.limit)))
    fn = {"leak": leak_task, "count": count_task, "destruction": destruction_task}
    meta = {"tag": TAG, "started": time.strftime("%Y-%m-%dT%H:%M:%S%z"), "limit": a.limit,
            "quick": a.quick, "n_boot": n_boot, "n_twins": n_twins, "n_draws": n_draws,
            "n_assess_surrogates": n_assess, "J_sec": J_SEC, "bins_sec": BINS_SEC,
            "window_sec": WINDOW_SEC, "edge_thinning_sec": EDGE_THIN_SEC,
            "exploratory": True}
    for stream in ("fast", "slow"):
        recs, skipped = load(stream, a.limit)
        meta[f"{stream}_recordings"] = len(recs)
        meta[f"{stream}_skipped"] = skipped
        meta[f"{stream}_window_sources"] = sorted({r.window_source for r in recs})
    (out / "meta.json").write_text(json.dumps(meta, indent=2, default=str))

    results = {"leak": [], "count": [], "destruction": []}
    t0 = time.time()
    with mp.get_context("spawn").Pool(a.jobs) as pool:
        futs = [(kind, pool.apply_async(fn[kind], (args,))) for kind, args in tasks]
        for kind, f in futs:
            r = f.get()
            results[kind].append(r)
            (out / "results.json").write_text(json.dumps(results, indent=2, default=str))
            print(f"[{time.time() - t0:7.0f}s] {kind} {r.get('stream')} "
                  f"{r.get('generator', '')} {r.get('J_sec', r.get('bin_sec', ''))}", flush=True)
    meta["finished"] = time.strftime("%Y-%m-%dT%H:%M:%S%z")
    meta["seconds"] = time.time() - t0
    (out / "meta.json").write_text(json.dumps(meta, indent=2, default=str))
    print("done", out)


if __name__ == "__main__":
    main()
