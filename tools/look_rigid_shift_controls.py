#!/usr/bin/env python3
"""The controls the rigid-shift look's murderboard asked for. Exploratory.

    python tools/look_rigid_shift_controls.py --role steps_excluded --out <folder>
    python tools/look_rigid_shift_controls.py --role cossart --out <folder>
    python tools/look_rigid_shift_controls.py --role cossart --out <folder> --limit 4 --quick

Review record: ``docs/reviews/rigid-shift-look-2026-09-15.md``. Three questions:

* **Is the large-displacement leak a leak?** Beside every rigid-shift leak cell, a **shared
  offset**: every ROI of a recording moved by the *same* uniform offset in ±*J*, mapped to frames
  exactly as :func:`bugarach.surrogates.rigid_shift` maps them (``floor(k + 0.5 + u)``, onsets
  pushed out dropped). Each ROI's train moves in time just as it does under rigid shift, so
  per-ROI drift is moved identically; cross-ROI alignment is kept. If the classifier separates
  rigid shift and not the shared offset, it is seeing cross-ROI structure removed, not drift.
  Both are scored on the same real windows with the look's features, folds and refitting
  bootstrap (:mod:`look_rigid_shift`), and the rigid-shift point is reproduced at the look's own
  seed as a check that nothing else changed.
* **Can the destruction measure register partial removal?** A graded control,
  ``freeze_half``: homogeneous resample, then a seeded half of the ROIs restored to their input,
  the same half in both twins — as :func:`bugarach.surrogate_stats.destruction` builds it. On
  Cossart, destruction is also run at the folder's **measured** participation (8.1 % of ROIs,
  ``docs/learned/cossart_transfer``) and at K near its measured K = 12, not the field-scaled K.
* **How many onsets does rigid shift drop?** Over each recording's whole generation window
  (the baseline region on the lab folder, the whole recording on Cossart), per *J*.

Every random key carries the tag ``look-2026-09-15-controls``; rigid-shift pairs are drawn with
the look's own keys so they are the draws the look scored.
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

import look_rigid_shift as lr                                # noqa: E402
from bugarach import assess                                  # noqa: E402
from bugarach import surrogate_discriminator as sd           # noqa: E402
from bugarach import surrogate_stats as ss                   # noqa: E402
from bugarach import surrogates as sg                        # noqa: E402

TAG = "look-2026-09-15-controls"
J_SEC = {"fast": (1.6, 2.5, 5.0, 10.0, 20.0, 40.0),
         "slow": (1.4, 2.8, 5.6, 11.2, 22.4, 44.8),
         "events": (1.6, 5.0, 10.0, 20.0, 40.0)}
FOLD_SEEDS = 10
COSSART_PARTICIPATION = 0.081
COSSART_K = (6, 9, 12, 18, 24)
VISIBILITY_FLOOR = 1.0
"""The signed rule's floor: a K whose planted excess before any surrogate is below it cannot
say how much survived (``bugarach.confirm.rule.VISIBILITY_FLOOR``)."""


def seed31(*key) -> int:
    return int(ss.seed_of((TAG,) + tuple(key)) & 0x7FFFFFFF)


# -- the shared offset ------------------------------------------------------------------------

def shared_shift(trains, window, key, J_frames):
    """Every ROI moved by one offset ``u ~ U(-J, J)``; frame ``k`` goes to ``floor(k + 0.5 + u)``
    as in ``rigid_shift``; onsets leaving the window are dropped. Returns (trains, n_in, n_out)."""
    s, e = int(window[0]), int(window[1])
    L = e - s
    u = np.random.RandomState(seed31("shared", *key)).uniform(-J_frames, J_frames)
    outs, n_in, n_out = [], 0, 0
    for t in trains:
        t = np.asarray(t, np.int64)
        t = t[(t >= s) & (t < e)] - s
        k = np.floor(t + 0.5 + u).astype(np.int64)
        k = np.sort(k[(k >= 0) & (k < L)])
        outs.append(k + s)
        n_in += t.size
        n_out += k.size
    return outs, n_in, n_out


# -- leak -------------------------------------------------------------------------------------

def group_intervals(correct, mice, groups, seed, n_boot):
    """Per-group accuracy with a mouse-resampled 95 % interval (fixed fits, no refit)."""
    rs = np.random.RandomState(seed)
    out = {}
    for g in sorted(set(groups)):
        m = groups == g
        c, mm = correct[m], mice[m]
        uniq, inv = np.unique(mm, return_inverse=True)
        s_ = np.bincount(inv, c)
        n_ = np.bincount(inv)
        pick = rs.randint(uniq.size, size=(n_boot, uniq.size))
        dist = s_[pick].sum(1) / n_[pick].sum(1)
        out[g] = {"accuracy": float(c.mean()), "p2_5": float(np.percentile(dist, 2.5)),
                  "p97_5": float(np.percentile(dist, 97.5)), "n_pairs": int(m.sum()),
                  "n_mice": int(uniq.size)}
    return out


def leak_task(args):
    stream, J_sec, n_boot, limit = args
    recs, _ = lr.load(stream, limit)
    keep, _ = lr.feature_mask()
    Xr, Xrig, Xsh, Xdi, mice, slices, groups = [], [], [], [], [], [], []
    drop = {"rigid_shift": [0, 0], "shared_shift": [0, 0], "uniform_dither": [0, 0]}
    per_rec_drop = {"rigid_shift": [], "shared_shift": [], "uniform_dither": []}
    for r in recs:
        Jf = round(J_sec / r.dt, 9)
        rig = sg.generate("rigid_shift", r.trains, r.window,
                          (lr.TAG, "leak", r.recording_id, stream, "rigid_shift", Jf), J=Jf)
        n_in = int(rig.info["n_in"].sum()); n_out = int(rig.info["n_out"].sum())
        drop["rigid_shift"][0] += n_in; drop["rigid_shift"][1] += n_in - n_out
        per_rec_drop["rigid_shift"].append((n_in - n_out) / max(1, n_in))
        sh, s_in, s_out = shared_shift(r.trains, r.window, ("leak", r.recording_id, stream, Jf), Jf)
        drop["shared_shift"][0] += s_in; drop["shared_shift"][1] += s_in - s_out
        per_rec_drop["shared_shift"].append((s_in - s_out) / max(1, s_in))
        # The POSITIVE control (added 2026-09-16): per-onset dither at the same J, the screen's
        # known-bad candidate. It breaks every ROI's interval floor, which these per-ROI features
        # can see, so a cell where the classifier reads chance for it too has no power there.
        di = sg.generate("uniform_dither", r.trains, r.window,
                         (TAG, "leak", r.recording_id, stream, "uniform_dither", Jf), J=Jf)
        d_in = int(di.info["n_in"].sum()); d_out = int(di.info["n_out"].sum())
        drop["uniform_dither"][0] += d_in; drop["uniform_dither"][1] += d_in - d_out
        per_rec_drop["uniform_dither"].append((d_in - d_out) / max(1, d_in))
        wins = lr.interior_windows(r)
        if not wins:
            continue
        band = max(1, int(np.floor(lr.EDGE_SEC / r.dt + 0.5)))
        a, b = sd.pair_features([r.trains] * len(wins), [rig.trains] * len(wins), wins, band)
        _, c = sd.pair_features([r.trains] * len(wins), [sh] * len(wins), wins, band)
        _, d = sd.pair_features([r.trains] * len(wins), [di.trains] * len(wins), wins, band)
        Xr.append(a[:, keep]); Xrig.append(b[:, keep]); Xsh.append(c[:, keep])
        Xdi.append(d[:, keep])
        mice += [r.mouse] * len(wins); slices += [r.recording_id] * len(wins)
        groups += [r.group or ""] * len(wins)
    Xr, Xrig, Xsh, Xdi = np.vstack(Xr), np.vstack(Xrig), np.vstack(Xsh), np.vstack(Xdi)
    mice, slices, groups = np.asarray(mice), np.asarray(slices), np.asarray(groups)

    res = {"stream": stream, "J_sec": J_sec, "n_pairs": int(len(mice)),
           "n_mice": int(np.unique(mice).size), "n_slices": int(np.unique(slices).size),
           "n_recordings": len(recs)}
    look_seed = lr.seed31("leak", stream, "rigid_shift", J_sec)
    res["rigid_shift_look_seed_accuracy"] = float(lr.cv_correct(Xr, Xrig, mice, look_seed).mean())
    for name, Xs in (("rigid_shift", Xrig), ("shared_shift", Xsh), ("uniform_dither", Xdi)):
        seeds = [seed31("folds", stream, J_sec, i) for i in range(FOLD_SEEDS)]
        accs = [float(lr.cv_correct(Xr, Xs, mice, s_).mean()) for s_ in seeds]
        seed = seed31("leak", stream, name, J_sec)
        p, dm = lr.refit_bootstrap(Xr, Xs, mice, mice, n_boot, seed)
        _, dsl = lr.refit_bootstrap(Xr, Xs, mice, slices, n_boot, seed + 1)
        correct = lr.cv_correct(Xr, Xs, mice, seed)
        res[name] = {"accuracy_fold_seed_mean": float(np.mean(accs)),
                     "accuracy_fold_seed_range": [float(min(accs)), float(max(accs))],
                     "by_mouse": lr.summarize(p, dm), "by_slice": lr.summarize(p, dsl),
                     "by_group": group_intervals(correct, mice, groups, seed + 2, n_boot),
                     "dropped_share": drop[name][1] / max(1, drop[name][0]),
                     "dropped_share_per_recording_max": float(max(per_rec_drop[name])),
                     "dropped_share_per_recording_median": float(np.median(per_rec_drop[name]))}
    return res


# -- destruction ------------------------------------------------------------------------------

def excess_k(trains, n_frames, dt, bin_sec, Ks, n_assess, seed):
    from bugarach.io import slice_from_events
    s = slice_from_events({"events": [np.asarray(v, float) * dt for v in trains]},
                          dt=dt, slice_id="twin")
    res = assess.assess_coactivity(s, stream="events", window=(0.0, n_frames * dt),
                                   min_rois=tuple(Ks), bin_width_sec=bin_sec,
                                   n_surrogates=n_assess, rng_seed=int(seed),
                                   region_min_sec=0.0)
    return {int(a.min_rois): float(a.coact_excess) for a in res}


_LOADED: dict = {}


def loaded(stream, limit):
    """One folder load per worker process, not one per twin."""
    if (stream, limit) not in _LOADED:
        _LOADED[(stream, limit)] = lr.load(stream, limit)
    return _LOADED[(stream, limit)]


def twin_pair(stream, limit, p, t):
    recs, _ = loaded(stream, limit)
    dt = float(np.median([r.dt for r in recs]))
    n_frames = int(np.median([r.window[1] - r.window[0] for r in recs]))
    n_roi = int(np.median([len(r.trains) for r in recs]))
    rates = np.concatenate([[v.size / max(1, r.window[1] - r.window[0]) for v in r.trains]
                            for r in recs])
    floor = ss.observed_floor(recs) or 1
    # The look's own twin keys, so at a participation the look ran these are its twins.
    g = np.random.RandomState(lr.seed31("twin-counts", stream, p, t))
    counts = g.poisson(g.choice(rates, size=n_roi, replace=True) * n_frames)
    pl, un, _ = ss.destruction_twins(n_roi, n_frames, dt, int(floor), counts, p,
                                     seed=lr.seed31("twin", stream, p, t))
    return pl, un, {"dt": dt, "n_frames": n_frames, "n_roi": n_roi, "floor_frames": int(floor)}


def before_task(args):
    """The planted-minus-unplanted excess of one twin pair before any surrogate."""
    stream, bin_sec, p, Ks, t, n_assess, limit = args
    pl, un, shape = twin_pair(stream, limit, p, t)
    base_seed = seed31("assess", stream, bin_sec, p)
    b_pl = excess_k(pl, shape["n_frames"], shape["dt"], bin_sec, Ks, n_assess, base_seed)
    b_un = excess_k(un, shape["n_frames"], shape["dt"], bin_sec, Ks, n_assess, base_seed)
    return {"cell": (stream, bin_sec, p), "twin": t, "shape": shape,
            "before": {K: b_pl[K] - b_un[K] for K in Ks}}


def draw_task(args):
    """One surrogate draw of one variant on one twin pair: planted and unplanted excess after.
    Split this finely because at Cossart's measured K one excess call takes about 37 s."""
    stream, bin_sec, p, Ks, t, name, J, k, n_assess, limit = args
    pl, un, shape = twin_pair(stream, limit, p, t)
    dt, n_frames = shape["dt"], shape["n_frames"]
    base_seed = seed31("assess", stream, bin_sec, p)
    gen = "homogeneous_resample" if name == "freeze_half" else name
    params = {"J": round(J / dt, 9)} if J else {}
    after_seed = base_seed + 7 if name == "do_nothing" else base_seed
    key = (TAG, "destroy", stream, bin_sec, p, t, name, J or 0, k)
    s_pl = [np.asarray(v, np.int64) for v in sg.generate(gen, pl, (0, n_frames), key, **params).trains]
    s_un = [np.asarray(v, np.int64) for v in sg.generate(gen, un, (0, n_frames), key, **params).trains]
    if name == "freeze_half":
        half = np.random.RandomState(seed31("freeze-half", stream, p, t, k)) \
            .permutation(len(pl))[: len(pl) // 2]
        for r_ in half:
            s_pl[r_] = np.asarray(pl[r_], np.int64)
            s_un[r_] = np.asarray(un[r_], np.int64)
    return {"cell": (stream, bin_sec, p), "twin": t, "variant": f"{name}@{J}" if J else name,
            "draw": k,
            "planted": excess_k(s_pl, n_frames, dt, bin_sec, Ks, n_assess, after_seed),
            "unplanted": excess_k(s_un, n_frames, dt, bin_sec, Ks, n_assess, after_seed)}


def destruction_tasks(stream, bin_sec, p, Ks, Js, n_twins, n_draws, n_assess, limit):
    variants = [("rigid_shift", J) for J in Js] + \
        [("homogeneous_resample", None), ("freeze_half", None), ("do_nothing", None)]
    out = []
    for t in range(n_twins):
        out.append(("before", (stream, bin_sec, p, Ks, t, n_assess, limit)))
        for name, J in variants:
            for k in range(n_draws if name != "do_nothing" else 1):
                out.append(("draw", (stream, bin_sec, p, Ks, t, name, J, k, n_assess, limit)))
    return out


def assemble(befores, draws, meta_of_cell):
    """Per cell, the look's structure: variants -> one row per twin with before and after."""
    cells = []
    for cell, info in meta_of_cell.items():
        stream, bin_sec, p = cell
        Ks = info["k_scan"]
        rows = {}
        for d in draws:
            if tuple(d["cell"]) != cell:
                continue
            rows.setdefault(d["variant"], {}).setdefault(d["twin"], []).append(d)
        variants = {}
        for v, by_twin in rows.items():
            variants[v] = []
            for t, ds in sorted(by_twin.items()):
                b = next(x for x in befores if tuple(x["cell"]) == cell and x["twin"] == t)
                variants[v].append({
                    "twin": t, "n_draws": len(ds),
                    "before": {K: b["before"][K] for K in Ks},
                    "after": {K: float(np.mean([x["planted"][K] for x in ds])
                                       - np.mean([x["unplanted"][K] for x in ds])) for K in Ks}})
        shape = next((x["shape"] for x in befores if tuple(x["cell"]) == cell), None)
        cells.append({"stream": stream, "bin_sec": bin_sec, "participation": p, "k_scan": list(Ks),
                      "twin_shape": shape, **{k: info[k] for k in ("n_twins", "n_draws",
                                                                   "n_assess_surrogates")},
                      "variants": variants})
    return cells


# -- main -------------------------------------------------------------------------------------

def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", required=True)
    ap.add_argument("--role", default="steps_excluded")
    ap.add_argument("--limit", type=int, default=None)
    ap.add_argument("--quick", action="store_true")
    ap.add_argument("--jobs", type=int, default=12)
    ap.add_argument("--leak-only", action="store_true",
                    help="run the leak cells only (shared offset, rigid shift, the dither "
                         "positive control); skip destruction")
    a = ap.parse_args(argv)
    import os
    os.environ[lr.ROLE_ENV] = a.role
    lab = a.role == "steps_excluded"
    streams = ("fast", "slow") if lab else ("events",)
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    n_boot = 40 if a.quick else 1000
    if a.quick:
        n_twins, n_draws, n_assess = 2, 2, 20
    elif lab:
        n_twins, n_draws, n_assess = 20, 20, 200
    else:
        n_twins, n_draws, n_assess = 10, 10, 200

    tasks, cells = [], {}
    for stream in streams:
        for J in J_SEC[stream]:
            tasks.append(("leak", (stream, J, n_boot, a.limit)))
        for bin_sec in ((() if a.leak_only else lr.BINS_SEC[stream])):
            if lab:
                # The graded control beside the look's own twins and K; rigid shift is in the look.
                specs = [(p, lr.K_SCAN, ()) for p in lr.PARTICIPATION]
            else:
                specs = [(COSSART_PARTICIPATION, COSSART_K, J_SEC[stream])]
            for p, Ks, Js in specs:
                cells[(stream, bin_sec, p)] = {"k_scan": tuple(Ks), "n_twins": n_twins,
                                               "n_draws": n_draws, "n_assess_surrogates": n_assess}
                tasks += destruction_tasks(stream, bin_sec, p, tuple(Ks), Js, n_twins, n_draws,
                                           n_assess, a.limit)
    meta = {"tag": TAG, "role": a.role, "started": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
            "limit": a.limit, "quick": a.quick, "n_boot": n_boot, "fold_seeds": FOLD_SEEDS,
            "n_twins": n_twins, "n_draws": n_draws, "n_assess_surrogates": n_assess,
            "J_sec": {s: J_SEC[s] for s in streams}, "window_sec": lr.WINDOW_SEC,
            "cossart_participation": COSSART_PARTICIPATION, "cossart_K": COSSART_K,
            "visibility_floor": VISIBILITY_FLOOR, "exploratory": True}
    for stream in streams:
        recs, skipped = lr.load(stream, a.limit)
        meta[f"{stream}_recordings"] = len(recs)
        meta[f"{stream}_skipped"] = skipped
        meta[f"{stream}_window_sources"] = sorted({r.window_source for r in recs})
    (out / "meta.json").write_text(json.dumps(meta, indent=2, default=str))

    fn = {"leak": leak_task, "before": before_task, "draw": draw_task}
    results = {"leak": [], "destruction": []}
    raw = {"before": [], "draw": []}
    t0 = time.time()
    done = 0
    with mp.get_context("spawn").Pool(a.jobs) as pool:
        futs = [(kind, pool.apply_async(fn[kind], (args,))) for kind, args in tasks]
        for kind, f in futs:
            r = f.get()
            done += 1
            if kind == "leak":
                results["leak"].append(r)
                (out / "results.json").write_text(json.dumps(results, indent=2, default=str))
                print(f"[{time.time() - t0:7.0f}s] leak {r['stream']} {r['J_sec']}", flush=True)
            else:
                raw[kind].append(r)
                with open(out / "destruction_raw.jsonl", "a") as fh:
                    fh.write(json.dumps({"kind": kind, **r}, default=str) + "\n")
                if done % 25 == 0 or done == len(tasks):
                    print(f"[{time.time() - t0:7.0f}s] {done}/{len(tasks)} tasks", flush=True)
    results["destruction"] = assemble(raw["before"], raw["draw"], cells)
    (out / "results.json").write_text(json.dumps(results, indent=2, default=str))
    meta["finished"] = time.strftime("%Y-%m-%dT%H:%M:%S%z")
    meta["seconds"] = time.time() - t0
    (out / "meta.json").write_text(json.dumps(meta, indent=2, default=str))
    print("done", out)


if __name__ == "__main__":
    main()
