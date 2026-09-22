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

* every model in ``tube_self_supervised.MODELS`` trained against rigid shift (J = 10 s, 20 s;
  3 seeds), **fitted per mouse fold** so every recording is called by a model that never saw its
  mouse. Threshold: label-free, set per recording so the model fires at most 2 events per
  10 minutes on three rigid shifts of that recording at the training J.
* the same models supervised, fitted once per seed on the bake-off's simulated recordings, at the
  label-free threshold (rigid shifts at ``SUP_THRESHOLD_J_SEC``) and at their own bake-off
  threshold.
* the zero-parameter scorers ``tube_self_supervised.BASELINES`` under the same label-free rule.
* ``coact`` (CoactDetect) and ``loco`` (LoCo) through :func:`bugarach.detect_folder.detect_slice`
  at their production operating points.
* for every label-free detector, its calls on a **fresh** rigid shift of each recording at the
  same *J* (``…, on its rigid shift``; see ``fresh_shift``), measured against the shifted trains.
  Not one of the shifts its threshold was set on, so its event rate is not capped by construction.

**What is measured per detector:**

* events per 10 minutes, and the share of events near a window edge;
* **participation** — distinct ROIs with an onset inside each event's extent ±2 frames, against the
  same extents dropped at uniformly random times, and at times drawn in proportion to the
  recording's population onset rate (the activity-matched chance), with a mouse-clustered interval
  on the excess over that chance, and per group;
* **localization** — the share of events whose span holds no onset, and the share within 1 s and
  3 s of a frame where at least three ROIs are active, against activity-matched random times;
* **pair recurrence** — for events carried by exactly two ROIs, how much of a recording's share
  the single most frequent pair takes; a crosstalk or duplicated-ROI artefact concentrates there;
* **agreement** — share of one detector's events overlapping the other's within ±1 s, against the
  same events circularly shifted within the window, pooled over every seed of both.

Nothing is planted in these recordings, so none of this is a score.
"""

from __future__ import annotations

import argparse
import json
import multiprocessing as mp
import sys
import time
import warnings
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import tube_self_supervised as ts                            # noqa: E402

TAG = "tube-ssl-real-2026-09-15"
RATE = 2.0
PAD_FRAMES = 2
AGREE_TOL_SEC = 1.0
"""Agreement tolerance. Named apart from `bugarach.score.TOL_SEC` (2.5 s) on purpose: agreement
is a many-to-one overlap share, not the scorer's one-to-one match, so it is not a recall."""
N_RANDOM = 20
MODELS = ts.MODELS
J_SEC = (10.0, 20.0)
SEEDS = (0, 1, 2)


def seed31(*key):
    from bugarach import surrogate_stats as ss
    return int(ss.seed_of((TAG,) + tuple(key)) & 0x7FFFFFFF)


def events_from_logits(z, thr, w0, dt):
    from bugarach.learn.encode import decode
    d = decode(z, threshold=thr, merge_gap_frames=ts.MERGE_GAP)
    return [((w0 + int(o)) * dt, int(w) * dt) for o, w in zip(d.onset_frame, d.width_frame)]


SUP_THRESHOLD_J_SEC = 10.0
"""The displacement of the rigid shifts a supervised or zero-parameter scorer's label-free threshold
is set on. 20 s until 2026-09-17, while the bench used 10 s for the same arms; now one value."""


def fresh_shift(r, J_sec):
    """The rigid shift a detector's calls "on its rigid shift" are made on and measured against.

    **Fresh**: seeded by recording and displacement only, never one of the shifts a threshold was
    set on, so its event rate is not guaranteed to sit under the cap by construction. **Shared**:
    every detector at the same *J* is called on the same shifted recording, and ``measure`` scores
    those calls against these shifted trains. Until 2026-09-17 the calls were made on the first
    threshold shift and scored against the unshifted recording's onsets, which reads any event as
    empty (the fourth blind review of the rigid-shift report)."""
    rng = np.random.RandomState(seed31("fresh-shift", r["id"], J_sec))
    return ts.rigid_frames(r["trains"], r["L"], J_sec / r["dt"], rng)


def call_recording(model, r, J_sec, label):
    """Label-free threshold and scores on one real recording's baseline window, plus the scores on
    its fresh rigid shift at the same *J* (``fresh_shift``)."""
    L, dt = r["L"], r["dt"]
    z = ts.probs(model, ts.raster_of(r["trains"], L))
    rng = np.random.RandomState(seed31("thr", label, r["id"]))
    z_s = [ts.probs(model, ts.raster_of(ts.rigid_frames(r["trains"], L, J_sec / dt, rng), L))
           for _ in range(ts.N_SURR_THRESHOLD)]
    thr, _ = ts.label_free_threshold(z_s, L * dt / 60.0, RATE)
    z_fresh = ts.probs(model, ts.raster_of(fresh_shift(r, J_sec), L))
    return thr, z, z_fresh


def ssl_task(args):
    name, J_sec, seed, fold, quick, ckpt_dir = args
    import fair_bakeoff as fb
    if quick:
        ts.STEPS = 60
    rows = ts.real_recordings()
    bank = ts.bank_for([r for r in rows if r["fold"] != fold], J_sec, ("ssl_real", fold))
    model, n_par, hist = ts.ssl_train(name, bank, seed, fb.LR[name])
    label = f"ssl-{name}-{J_sec}-{seed}-{fold}"
    out, on_shift, thrs = {}, {}, []
    for r in rows:
        if r["fold"] != fold:
            continue
        thr, z, zs = call_recording(model, r, J_sec, label)
        thrs.append(thr)
        out[r["id"]] = events_from_logits(z, thr, r["w0"], r["dt"])
        on_shift[r["id"]] = events_from_logits(zs, thr, r["w0"], r["dt"])
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
    return [{"detector": f"ssl {name} J{J_sec:g}", "seed": seed, "fold": fold, "events": out,
             "thresholds": thrs, "history_last": hist[-1] if hist else None},
            {"detector": f"ssl {name} J{J_sec:g}, on its rigid shift", "seed": seed,
             "fold": fold, "events": on_shift, "surrogate": True, "J_sec": J_sec}]


def fit_supervised(name, seed, quick=False):
    """One supervised fit on every simulated recording of the bench split, as the bake-off fits."""
    import fair_bakeoff as fb
    from bugarach.bench import fold_split
    from bugarach.learn.train import fold_maker, train
    split = fold_split(n_folds=ts.N_FOLDS, seeds_per_fold=ts.SEEDS_PER_FOLD)
    mk, n_fit, _ = fold_maker(ts.sim_recording, list(split.seeds))
    return train(name, mk, n_train=min(10, n_fit), steps=60 if quick else 900, crop=ts.CROP,
                 batch=ts.BATCH, lr=fb.LR[name], seed=seed)


def sup_task(args):
    name, seed, quick = args
    tr = fit_supervised(name, seed, quick)
    p = min(max(float(tr.threshold), 1e-12), 1 - 1e-12)
    bake = float(np.log(p / (1 - p)))
    lf, bk, sh = {}, {}, {}
    for r in ts.real_recordings():
        thr, z, zs = call_recording(tr.model, r, SUP_THRESHOLD_J_SEC, f"sup-{name}-{seed}")
        lf[r["id"]] = events_from_logits(z, thr, r["w0"], r["dt"])
        bk[r["id"]] = events_from_logits(z, bake, r["w0"], r["dt"])
        sh[r["id"]] = events_from_logits(zs, thr, r["w0"], r["dt"])
    return [{"detector": f"supervised {name} label-free", "seed": seed, "events": lf},
            {"detector": f"supervised {name} bake-off threshold", "seed": seed, "events": bk},
            {"detector": f"supervised {name} label-free, on its rigid shift", "seed": seed,
             "events": sh, "surrogate": True, "J_sec": SUP_THRESHOLD_J_SEC}]


def baseline_task(args):
    """A zero-parameter scorer (``tube_self_supervised.BASELINES``) under the same label-free rule:
    the comparator a trained model's real-recording calls should be read against."""
    name, = args
    model = ts.baseline_model(name)
    lf, sh = {}, {}
    for r in ts.real_recordings():
        thr, z, zs = call_recording(model, r, SUP_THRESHOLD_J_SEC, f"baseline-{name}")
        lf[r["id"]] = events_from_logits(z, thr, r["w0"], r["dt"])
        sh[r["id"]] = events_from_logits(zs, thr, r["w0"], r["dt"])
    return [{"detector": f"baseline {name} label-free", "seed": 0, "events": lf},
            {"detector": f"baseline {name} label-free, on its rigid shift", "seed": 0,
             "events": sh, "surrogate": True, "J_sec": SUP_THRESHOLD_J_SEC}]


def hand_task(args):
    ids, = args
    import look_rigid_shift as lr
    from bugarach import dataset
    from bugarach.detect_folder import detect_slice
    from bugarach.io import load_folder
    rows = {r["id"]: r for r in ts.real_recordings()}
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        # The role the rest of the run reads, not a second hard-coded folder: the two
        # disagreeing is how a comparison ends up spanning two exports.
        slices = {s.slice_id: s for s in load_folder(dataset.current(lr.role()))}
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


N_RANDOM_PER_EVENT = 10
"""Random times drawn per event, for each chance baseline. Two until 2026-09-17."""
ACTIVITY_SMOOTH_FRAMES = 101
"""The activity-matched chance draws random times in proportion to the recording's population onset
rate, smoothed over 10 s. A detector that fires where the population is busy is enriched against
uniform random times without detecting coordination; against this baseline it is not."""


def _activity_weights(r):
    pop = np.zeros(r["L"])
    for t in r["trains"]:
        np.add.at(pop, np.asarray(t, np.int64), 1.0)
    w = np.convolve(pop, np.ones(ACTIVITY_SMOOTH_FRAMES), mode="same") + 1e-9
    return w / w.sum()


COACTIVE_ROIS = 3
"""A frame is co-active when at least this many distinct ROIs have an onset within ±PAD_FRAMES of it:
the same count and pad the participation share uses, so the two measures describe one event."""
NEAR_SEC = (1.0, 3.0)
"""How far from a co-active frame an event may start or end and still count as beside it. Added
2026-09-17, when the fourth blind review measured the models trained against rigid shift firing in
quiet gaps next to co-activity, which the ±0.2 s participation share reads as chance."""
EDGE_SEC = (5.0, 12.8)
"""Window-edge bands. 12.8 s is the models' 128-frame difference-of-Gaussians half-support."""
N_BOOT = 1000


def shifted_row(r, J_sec):
    return {**r, "trains": fresh_shift(r, J_sec)}


def coactive_mask(r):
    """Frames with onsets in at least COACTIVE_ROIS distinct ROIs within ±PAD_FRAMES."""
    counts = np.zeros(r["L"], np.int32)
    for t in r["trains"]:
        lit = np.zeros(r["L"], bool)
        for k in np.asarray(t, np.int64):
            lit[max(0, k - PAD_FRAMES):k + PAD_FRAMES + 1] = True
        counts += lit
    return counts >= COACTIVE_ROIS


def near_coactive(mask_cum, r, on_sec, wd_sec, near_sec):
    """Whether any co-active frame lies within near_sec of the event's span."""
    dt = r["dt"]
    pad = int(round(near_sec / dt))
    a = max(0, int(round(on_sec / dt)) - r["w0"] - pad)
    b = min(r["L"], int(round((on_sec + wd_sec) / dt)) - r["w0"] + pad + 1)
    return b > a and mask_cum[b] - mask_cum[a] > 0


def measure(detector_events, rows_by_id, surrogate_J=None):
    """detector -> list over runs of {recording: [(onset, width)]}; returns per-detector stats.

    A detector named in ``surrogate_J`` was called on its fresh rigid shift at that *J*, and every
    measure below reads the shifted trains, not the recording's.

    Per detector: the event rate; the share of events with onsets in at least COACTIVE_ROIS ROIs
    within their span ±PAD_FRAMES, against the same widths at uniformly random times and at times
    drawn in proportion to population activity; the share whose span holds no onset at all; the share
    starting or ending within NEAR_SEC of a co-active frame, against activity-weighted random times;
    the share of events near a window edge; a mouse-clustered bootstrap interval on the excess of the
    co-activity share over its activity-weighted chance; and the co-activity share per group."""
    surrogate_J = surrogate_J or {}
    rng = np.random.RandomState(seed31("measure"))
    cache: dict = {}

    def view(rid, J):
        key = (rid, J)
        if key not in cache:
            r = rows_by_id[rid] if J is None else shifted_row(rows_by_id[rid], J)
            mask = coactive_mask(r)
            cache[key] = (r, _activity_weights(r),
                          np.concatenate([[0], np.cumsum(mask.astype(np.int64))]))
        return cache[key]

    stats = {}
    for det, runs in detector_events.items():
        J = surrogate_J.get(det)
        n_ev, minutes, part, part_rand, top_pair = 0, 0.0, [], [], []
        wide, wide_rand, part_act, empty = [], [], [], []
        near = {s: [] for s in NEAR_SEC}
        near_act = {s: [] for s in NEAR_SEC}
        edge = {e: 0 for e in EDGE_SEC}
        edge_expect = {e: [] for e in EDGE_SEC}
        by_mouse: dict = {}
        by_group: dict = {}
        for run in runs:
            for rid, evs in run.items():
                r, weights, mask_cum = view(rid, J)
                minutes += r["L"] * r["dt"] / 60.0
                n_ev += len(evs)
                a_sec, b_sec = r["w0"] * r["dt"], (r["w0"] + r["L"]) * r["dt"]
                for e in EDGE_SEC:
                    edge_expect[e].append(min(1.0, 2 * e / (b_sec - a_sec)))
                m = by_mouse.setdefault(r["mouse"], [0, 0, 0, 0])
                g = by_group.setdefault(r.get("group"), [0, 0])
                pairs = {}
                for on, wd in evs:
                    rois = participation(r, on, wd)
                    part.append(len(rois))
                    empty.append(len(participation(r, on, wd, pad=0)) == 0)
                    one_s = int(round(AGREE_TOL_SEC / r["dt"]))
                    wide.append(len(participation(r, on, wd, pad=one_s)))
                    for s in NEAR_SEC:
                        near[s].append(near_coactive(mask_cum, r, on, wd, s))
                    for e in EDGE_SEC:
                        edge[e] += min(on - a_sec, b_sec - on) < e
                    if len(rois) == 2:
                        pairs[tuple(rois)] = pairs.get(tuple(rois), 0) + 1
                    span = max(1, r["L"] - int(wd / r["dt"]) - 1)
                    act_hits = 0
                    for _ in range(N_RANDOM_PER_EVENT):
                        t = (r["w0"] + rng.randint(0, span)) * r["dt"]
                        part_rand.append(len(participation(r, t, wd)))
                        wide_rand.append(len(participation(r, t, wd, pad=one_s)))
                        f = int(rng.choice(r["L"], p=weights))
                        ta = (r["w0"] + min(f, span - 1)) * r["dt"]
                        n_act = len(participation(r, ta, wd))
                        part_act.append(n_act)
                        act_hits += n_act >= COACTIVE_ROIS
                        for s in NEAR_SEC:
                            near_act[s].append(near_coactive(mask_cum, r, ta, wd, s))
                    m[0] += 1
                    m[1] += len(rois) >= COACTIVE_ROIS
                    m[2] += N_RANDOM_PER_EVENT
                    m[3] += act_hits
                    g[0] += 1
                    g[1] += len(rois) >= COACTIVE_ROIS
                if sum(pairs.values()) >= 3:
                    top_pair.append(max(pairs.values()) / sum(pairs.values()))
        part, part_rand = np.asarray(part), np.asarray(part_rand)
        wide, wide_rand = np.asarray(wide), np.asarray(wide_rand)
        part_act = np.asarray(part_act)
        runs_n = max(1, len(runs))
        excess_ci = None
        mice = [v for v in by_mouse.values() if v[0]]
        if mice:
            arr = np.asarray(mice, float)
            brng = np.random.RandomState(seed31("boot", det))
            draws = []
            for _ in range(N_BOOT):
                s = arr[brng.randint(0, len(arr), len(arr))].sum(axis=0)
                draws.append(s[1] / max(s[0], 1) - s[3] / max(s[2], 1))
            excess_ci = [float(np.percentile(draws, 2.5)), float(np.percentile(draws, 97.5))]
        stats[det] = {
            "on_rigid_shift_J_sec": J,
            "events_per_10min": 10.0 * n_ev / max(minutes, 1e-9),
            "n_events": n_ev, "n_runs": len(runs),
            "participation_median": float(np.median(part)) if part.size else None,
            "participation_share_ge3": float(np.mean(part >= 3)) if part.size else None,
            "participation_share_le2": float(np.mean(part <= 2)) if part.size else None,
            "random_participation_median": float(np.median(part_rand)) if part_rand.size else None,
            "random_share_ge3": float(np.mean(part_rand >= 3)) if part_rand.size else None,
            "activity_random_participation_median":
                float(np.median(part_act)) if part_act.size else None,
            "activity_random_share_ge3": float(np.mean(part_act >= 3)) if part_act.size else None,
            "share_ge3_minus_activity_chance_ci95_by_mouse": excess_ci,
            "n_mice": len(mice),
            "share_ge3_by_group": {str(k): v[1] / v[0] for k, v in by_group.items() if v[0]},
            "n_events_by_group": {str(k): v[0] for k, v in by_group.items()},
            "empty_span_share": float(np.mean(empty)) if empty else None,
            **{f"near_coactive_{s:g}s_share": float(np.mean(near[s])) if near[s] else None
               for s in NEAR_SEC},
            **{f"activity_random_near_coactive_{s:g}s_share":
               float(np.mean(near_act[s])) if near_act[s] else None for s in NEAR_SEC},
            **{f"edge_within_{e:g}s_share": edge[e] / max(n_ev, 1) for e in EDGE_SEC},
            **{f"edge_within_{e:g}s_uniform_expectation":
               float(np.mean(edge_expect[e])) if edge_expect[e] else None for e in EDGE_SEC},
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
    """Share of A's events within TOL of any of B's, and the same with A circularly shifted.

    Pooled over every run of B as well as of A. Until 2026-09-17 only B's first run was read, so
    "the share of CoactDetect's events a model overlaps" was the seed-0 fit's alone while every
    other column pooled three seeds."""
    hit = tot = hit_c = 0
    for run, b in ((a, b) for a in a_runs for b in b_runs):
        for rid, evs in run.items():
            r = rows_by_id[rid]
            w0, w1 = r["w0"] * r["dt"], (r["w0"] + r["L"]) * r["dt"]
            bo = np.asarray([o for o, _ in b.get(rid, [])])
            be = np.asarray([o + w for o, w in b.get(rid, [])])
            for on, wd in evs:
                tot += 1
                hit += bool(bo.size and np.any((bo - AGREE_TOL_SEC <= on + wd) & (be + AGREE_TOL_SEC >= on)))
                c = 0
                for _ in range(N_RANDOM):
                    s = w0 + (on - w0 + rng.uniform(0, w1 - w0)) % (w1 - w0)
                    c += bool(bo.size and np.any((bo - AGREE_TOL_SEC <= s + wd) & (be + AGREE_TOL_SEC >= s)))
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
    group = {r.recording_id: r.group or "" for r in recs}
    for r in rows:
        r["w0"] = w0[r["id"]]
        r["group"] = group[r["id"]]
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
    for name in ts.BASELINES:
        tasks.append((baseline_task, (name,)))
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
    surrogate_J = {}
    for item in raw:
        key = (item["detector"], item["seed"])
        merged.setdefault(key, {}).update(item["events"])
        if item.get("surrogate"):
            surrogate_J[item["detector"]] = item["J_sec"]
    for (det, seed), ev in merged.items():
        detector_events.setdefault(det, []).append(ev)
    stats = measure(detector_events, rows_by_id, surrogate_J)
    rng = np.random.RandomState(seed31("agree"))
    agree = {}
    for det in detector_events:
        if det.endswith("on its rigid shift"):
            continue  # measured for window-edge shares only; agreement is not defined on a surrogate
        for ref in ("coact", "loco"):
            if det != ref:
                agree[f"{det} -> {ref}"] = agreement(detector_events[det], detector_events[ref],
                                                    rows_by_id, rng)
        if not det.startswith(("coact", "loco")):
            for ref in ("coact", "loco"):
                agree[f"{ref} -> {det}"] = agreement(detector_events[ref], detector_events[det],
                                                    rows_by_id, rng)
    (out / "events.json").write_text(json.dumps(
        {det: runs for det, runs in detector_events.items()}, default=float))
    from bugarach import provenance
    (out / "summary.json").write_text(json.dumps({"stats": stats, "agreement": agree,
                                                  "provenance": provenance.stamp(
                                                      produced_by="tools/tube_ssl_real_compare.py"),
                                                  "sup_threshold_j_sec": SUP_THRESHOLD_J_SEC,
                                                  "n_random_per_event": N_RANDOM_PER_EVENT,
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
