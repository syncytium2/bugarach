#!/usr/bin/env python3
"""What do tube models trained against rigid shift call on real recordings? Exploratory.

    python tools/tube_ssl_real_compare.py --out <folder>
    python tools/tube_ssl_real_compare.py --out <folder> --quick

Option 1 after Stage 2 (``docs/handoffs/2026-09-15-rigid-shift-controls-and-tube-training.md``):
the models trained without labels learned to tell real lab recordings from their rigid shift, but
scored no better than an untrained tube on the simulator. The question here is whether what they
learned on real data is **coordination** or a **lab-specific artefact** — tight one- or two-frame
co-occurrence the simulator does not contain.

**Detections**, all on the lab folder's fast stream, baseline windows only (FOUNDATIONS §9):

* ``tube`` / ``tube_guard`` trained against rigid shift (J = 10 s, 20 s; 3 seeds), **fitted per
  mouse fold** so every recording is called by a model that never saw its mouse. Threshold:
  label-free, set per recording so the model fires at most 2 events per 10 minutes on three rigid
  shifts of that recording (:mod:`tube_self_supervised`).
* supervised ``tube`` fitted once on the bake-off's simulated corpus (as
  ``tools/run_learned_on_folder.py`` fits it), at the same label-free threshold and at its own
  bake-off threshold.
* ``coact`` (CoactDetect) and ``loco`` (LoCo) through :func:`bugarach.detect_folder.detect_slice`
  at their production operating points.

**What is measured per detector:**

* events per 10 minutes;
* **participation** — distinct ROIs with an onset inside each event (±2 frames), against the same
  intervals dropped at random times in the same recording;
* **pair recurrence** — for events carried by exactly two ROIs, how much of a recording's share
  the single most frequent pair takes; a crosstalk or duplicated-ROI artefact concentrates there;
* **agreement** — share of one detector's events overlapping the other's within ±1 s, against the
  same events circularly shifted within the window.

Nothing is planted in these recordings, so none of this is a score.
"""

from __future__ import annotations

import argparse
import json
import multiprocessing as mp
import os
import sys
import time
import warnings
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))
os.environ.setdefault("LOOK_ROLE", "steps_excluded")

import tube_self_supervised as ts                            # noqa: E402

TAG = "tube-ssl-real-2026-09-15"
RATE = 2.0
PAD_FRAMES = 2
TOL_SEC = 1.0
N_RANDOM = 20
MODELS = ("tube", "tube_guard", "line")
J_SEC = (10.0, 20.0)
SEEDS = (0, 1, 2)


def seed31(*key):
    from bugarach import surrogate_stats as ss
    return int(ss.seed_of((TAG,) + tuple(key)) & 0x7FFFFFFF)


def events_from_logits(z, thr, w0, dt):
    from bugarach.learn.encode import decode
    d = decode(z, threshold=thr, merge_gap_frames=ts.MERGE_GAP)
    return [((w0 + int(o)) * dt, int(w) * dt) for o, w in zip(d.onset_frame, d.width_frame)]


def call_recording(model, r, J_sec, label):
    """Label-free events on one real recording's baseline window."""
    L, dt = r["L"], r["dt"]
    z = ts.probs(model, ts.raster_of(r["trains"], L))
    rng = np.random.RandomState(seed31("thr", label, r["id"]))
    z_s = [ts.probs(model, ts.raster_of(ts.rigid_frames(r["trains"], L, J_sec / dt, rng), L))
           for _ in range(ts.N_SURR_THRESHOLD)]
    thr = ts.label_free_threshold(z_s, L * dt / 60.0, RATE)
    return thr, z


def ssl_task(args):
    name, J_sec, seed, fold, quick, ckpt_dir = args
    import fair_bakeoff as fb
    if quick:
        ts.STEPS = 60
    rows = ts.real_recordings()
    bank = ts.bank_for([r for r in rows if r["fold"] != fold], J_sec, ("ssl_real", fold))
    model, n_par, hist = ts.ssl_train(name, bank, seed, fb.LR[name])
    label = f"ssl-{name}-{J_sec}-{seed}-{fold}"
    out, thrs = {}, []
    for r in rows:
        if r["fold"] != fold:
            continue
        thr, z = call_recording(model, r, J_sec, label)
        thrs.append(thr)
        out[r["id"]] = events_from_logits(z, thr, r["w0"], r["dt"])
    if ckpt_dir:
        from bugarach.learn import checkpoint
        from bugarach.learn.train import Trained
        med = float(np.median(thrs))
        tr = Trained(name=name, model=model, threshold=float(1 / (1 + np.exp(-med))),
                     n_params=n_par, dt=0.1, merge_gap_frames=ts.MERGE_GAP)
        checkpoint.save(tr, Path(ckpt_dir) / f"{label}.json",
                        trained_on=f"lab fast baselines, mouse folds != {fold}",
                        train_seed=seed, steps=ts.STEPS, note=(
                            "trained against rigid shift with no labels "
                            "(tools/tube_self_supervised.py). NO FIXED OPERATING POINT: "
                            "thresholds are set per recording from its own rigid shift; the "
                            "threshold here is the sigmoid of the median of those, and may round "
                            "to 1.0."))
    return {"detector": f"ssl {name} J{J_sec:g}", "seed": seed, "fold": fold, "events": out,
            "thresholds": thrs, "history_last": hist[-1] if hist else None}


def sup_task(args):
    name, seed, quick = args
    import fair_bakeoff as fb
    from bugarach.bench import fold_split
    from bugarach.learn.train import fold_maker, train
    split = fold_split(n_folds=ts.N_FOLDS, seeds_per_fold=ts.SEEDS_PER_FOLD)
    mk, n_fit, _ = fold_maker(ts.sim_recording, list(split.seeds))
    tr = train(name, mk, n_train=min(10, n_fit), steps=60 if quick else 900, crop=ts.CROP,
               batch=ts.BATCH, lr=fb.LR[name], seed=seed)
    p = min(max(float(tr.threshold), 1e-12), 1 - 1e-12)
    bake = float(np.log(p / (1 - p)))
    lf, bk = {}, {}
    for r in ts.real_recordings():
        thr, z = call_recording(tr.model, r, 20.0, f"sup-{name}-{seed}")
        lf[r["id"]] = events_from_logits(z, thr, r["w0"], r["dt"])
        bk[r["id"]] = events_from_logits(z, bake, r["w0"], r["dt"])
    return [{"detector": f"supervised {name} label-free", "seed": seed, "events": lf},
            {"detector": f"supervised {name} bake-off threshold", "seed": seed, "events": bk}]


def hand_task(args):
    ids, = args
    from bugarach import dataset
    from bugarach.detect_folder import detect_slice
    from bugarach.io import load_folder
    rows = {r["id"]: r for r in ts.real_recordings()}
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        slices = {s.slice_id: s for s in load_folder(dataset.current("steps_excluded"))}
    out = {"coact": {}, "loco": {}}
    for rid in ids:
        r = rows[rid]
        a, b = r["w0"] * r["dt"], (r["w0"] + r["L"]) * r["dt"]
        evs, _ = detect_slice(slices[rid], detectors=("coact", "loco"), stream="fast")
        for det in out:
            out[det][rid] = [(float(e.onset_sec), float(e.width_sec)) for e in evs
                             if e.detector == det and a <= e.onset_sec < b]
    return [{"detector": det, "seed": 0, "events": ev} for det, ev in out.items()]


# -- measures ---------------------------------------------------------------------------------

def participation(r, on_sec, wd_sec, pad=PAD_FRAMES):
    dt = r["dt"]
    a = int(round(on_sec / dt)) - r["w0"] - pad
    b = int(round((on_sec + wd_sec) / dt)) - r["w0"] + pad
    rois = [i for i, t in enumerate(r["trains"]) if np.any((t >= a) & (t <= b))]
    return rois


def measure(detector_events, rows_by_id):
    """detector -> list over seeds of {recording: [(onset, width)]}; returns per-detector stats."""
    rng = np.random.RandomState(seed31("measure"))
    stats = {}
    for det, runs in detector_events.items():
        n_ev, minutes, part, part_rand, top_pair = 0, 0.0, [], [], []
        wide, wide_rand = [], []
        for run in runs:
            for rid, evs in run.items():
                r = rows_by_id[rid]
                minutes += r["L"] * r["dt"] / 60.0
                n_ev += len(evs)
                pairs = {}
                for on, wd in evs:
                    rois = participation(r, on, wd)
                    part.append(len(rois))
                    one_s = int(round(TOL_SEC / r["dt"]))
                    wide.append(len(participation(r, on, wd, pad=one_s)))
                    if len(rois) == 2:
                        pairs[tuple(rois)] = pairs.get(tuple(rois), 0) + 1
                    for _ in range(N_RANDOM // 10):
                        t = (r["w0"] + rng.randint(0, max(1, r["L"] - int(wd / r["dt"]) - 1))) * r["dt"]
                        part_rand.append(len(participation(r, t, wd)))
                        wide_rand.append(len(participation(r, t, wd, pad=one_s)))
                if sum(pairs.values()) >= 3:
                    top_pair.append(max(pairs.values()) / sum(pairs.values()))
        part, part_rand = np.asarray(part), np.asarray(part_rand)
        wide, wide_rand = np.asarray(wide), np.asarray(wide_rand)
        runs_n = max(1, len(runs))
        stats[det] = {
            "events_per_10min": 10.0 * n_ev / max(minutes, 1e-9),
            "n_events": n_ev, "n_runs": len(runs),
            "participation_median": float(np.median(part)) if part.size else None,
            "participation_share_ge3": float(np.mean(part >= 3)) if part.size else None,
            "participation_share_le2": float(np.mean(part <= 2)) if part.size else None,
            "random_participation_median": float(np.median(part_rand)) if part_rand.size else None,
            "random_share_ge3": float(np.mean(part_rand >= 3)) if part_rand.size else None,
            "participation_1s_median": float(np.median(wide)) if wide.size else None,
            "participation_1s_share_ge3": float(np.mean(wide >= 3)) if wide.size else None,
            "random_participation_1s_median": float(np.median(wide_rand)) if wide_rand.size else None,
            "random_1s_share_ge3": float(np.mean(wide_rand >= 3)) if wide_rand.size else None,
            "top_pair_share_median": float(np.median(top_pair)) if top_pair else None,
            "n_recordings_with_pairs": len(top_pair),
            "events_per_run": n_ev / runs_n,
        }
    return stats


def agreement(a_runs, b_runs, rows_by_id, rng):
    """Share of A's events within TOL of any of B's, and the same with A circularly shifted."""
    hit = tot = hit_c = 0
    b = b_runs[0]
    for run in a_runs:
        for rid, evs in run.items():
            r = rows_by_id[rid]
            w0, w1 = r["w0"] * r["dt"], (r["w0"] + r["L"]) * r["dt"]
            bo = np.asarray([o for o, _ in b.get(rid, [])])
            be = np.asarray([o + w for o, w in b.get(rid, [])])
            for on, wd in evs:
                tot += 1
                hit += bool(bo.size and np.any((bo - TOL_SEC <= on + wd) & (be + TOL_SEC >= on)))
                c = 0
                for _ in range(N_RANDOM):
                    s = w0 + (on - w0 + rng.uniform(0, w1 - w0)) % (w1 - w0)
                    c += bool(bo.size and np.any((bo - TOL_SEC <= s + wd) & (be + TOL_SEC >= s)))
                hit_c += c / N_RANDOM
    return {"share": hit / max(tot, 1), "chance": hit_c / max(tot, 1), "n": tot}


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", required=True)
    ap.add_argument("--quick", action="store_true")
    ap.add_argument("--jobs", type=int, default=12)
    ap.add_argument("--checkpoints", default=None, help="save the self-supervised fits here")
    a = ap.parse_args(argv)
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    rows = ts.real_recordings()
    # The windows' start frame, which ts.real_recordings does not keep.
    import look_rigid_shift as lr
    recs, _ = lr.load("fast", None)
    w0 = {r.recording_id: int(r.window[0]) for r in recs}
    for r in rows:
        r["w0"] = w0[r["id"]]
    rows_by_id = {r["id"]: r for r in rows}

    seeds = (0,) if a.quick else SEEDS
    tasks = []
    ids = sorted(rows_by_id)
    for chunk in np.array_split(ids, a.jobs):
        tasks.append((hand_task, (list(chunk),)))
    for name in MODELS:
        for seed in seeds:
            tasks.append((sup_task, (name, seed, a.quick)))
            for J in J_SEC:
                for fold in range(ts.N_FOLDS):
                    tasks.append((ssl_task, (name, J, seed, fold, a.quick, a.checkpoints)))
    t0 = time.time()
    detector_events: dict = {}
    raw = []
    with mp.get_context("spawn").Pool(a.jobs, initializer=_init_rows, initargs=(w0,)) as pool:
        futs = [pool.apply_async(fn, (args,)) for fn, args in tasks]
        for i, f in enumerate(futs):
            res = f.get()
            for item in (res if isinstance(res, list) else [res]):
                raw.append(item)
            print(f"[{time.time() - t0:6.0f}s] {i + 1}/{len(tasks)}", flush=True)
    # SSL runs come per fold: merge each (detector, seed)'s folds into one run over all recordings.
    merged: dict = {}
    for item in raw:
        key = (item["detector"], item["seed"])
        merged.setdefault(key, {}).update(item["events"])
    for (det, seed), ev in merged.items():
        detector_events.setdefault(det, []).append(ev)
    stats = measure(detector_events, rows_by_id)
    rng = np.random.RandomState(seed31("agree"))
    agree = {}
    for det in detector_events:
        for ref in ("coact", "loco"):
            if det != ref:
                agree[f"{det} -> {ref}"] = agreement(detector_events[det], detector_events[ref],
                                                    rows_by_id, rng)
        if not det.startswith(("coact", "loco")):
            for ref in ("coact", "loco"):
                agree[f"{ref} -> {det}"] = agreement(detector_events[ref], detector_events[det][:1],
                                                    rows_by_id, rng)
    (out / "events.json").write_text(json.dumps(
        {det: runs for det, runs in detector_events.items()}, default=float))
    (out / "summary.json").write_text(json.dumps({"stats": stats, "agreement": agree,
                                                  "seconds": time.time() - t0,
                                                  "quick": a.quick}, indent=2, default=float))
    for det, s in sorted(stats.items()):
        print(f"{det:40s} {s['events_per_10min']:6.2f}/10min  part med {s['participation_median']} "
              f"(random {s['random_participation_median']})  >=3 {s['participation_share_ge3']}"
              f"  top pair {s['top_pair_share_median']}")
    for k, v in agree.items():
        print(f"{k:60s} {v['share']:.2f} (chance {v['chance']:.2f}, n {v['n']})")
    print("done", out)


def _init_rows(w0):
    rows = ts.real_recordings()
    for r in rows:
        r["w0"] = w0[r["id"]]


if __name__ == "__main__":
    main()
