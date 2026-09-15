#!/usr/bin/env python3
"""Stage 2 of the tube plan: train `tube` and `tube_guard` with rigid shift as the only negative,
then score them on the planted-truth bake-off beside the supervised fit. Exploratory.

    python tools/tube_self_supervised.py --out <folder>
    python tools/tube_self_supervised.py --out <folder> --quick --jobs 12

Runs only because Stage 1 (``tools/tube_aggregate_leak.py``) passed on the lab fast stream: a
classifier reading tube's cells-mean channel could not tell real from a shared offset, nor an
unplanted twin from its rigid shift, while real against rigid shift separated at event-width
kernel scales. That is the aggregate-channel test the tube foot-gun todo asks for first.

**The objective.** A crop of a recording and the same crop of its rigid shift go through the
model; each crop's score is the mean of its top 1 % per-frame logits (events are sparse, so a
whole-crop mean would drown them); the loss is ``softplus(score_shift - score_real)``. No label
is read. Crops stay more than *J* from the recording's ends, where rigid shift drops onsets.

**Rigid shift here** is drawn in numpy: each ROI's frames move by ``floor(k + 0.5 + u)`` with
one ``u ~ U(-J, J)`` per ROI, onsets leaving the window dropped — the transform
:func:`bugarach.surrogates.rigid_shift` performs through Elephant (a murderboard reviewer checked
it is an exact integer shift per ROI), drawn without Elephant's per-ROI seeding so a bank of
draws is cheap.

**Arms**, each over the bake-off's four folds (``tools/fair_bakeoff.py``: the bench generator
spec, 4 folds of 2 recordings) and three torch seeds:

* ``ssl_sim``  — trained on the training folds' recordings, labels unread.
* ``ssl_real`` — trained on lab fast-stream baselines from three quarters of the mice; never
  sees a simulated recording until it is scored.
* ``supervised`` — ``bugarach.learn.train.train`` exactly as the bake-off runs it: the control,
  re-measured in this run.
* ``untrained`` — the architecture at initialisation: what the objective adds.

**Two thresholds** for every model on the held-out fold:

* *label-free* — per recording, the lowest threshold at which the model fires no more than
  ``r`` events per 10 minutes on three rigid shifts of **that recording**; ``r`` in 0.5, 1, 2.
* *oracle* — ``pick_threshold`` on the training folds' planted truth, the bake-off's own rule.
  For comparison with the supervised fit only; it reads labels.

**Checks on each self-supervised model:** paired score of held-out real crops against their
shared offset (must be ~0.5) and against their rigid shift; unplanted twins against their rigid
shift (must be ~0.5); the fitted centre widths in seconds.
"""

from __future__ import annotations

import argparse
import json
import multiprocessing as mp
import os
import sys
import time
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

TAG = "tube-ssl-2026-09-15"
MODELS = ("tube", "tube_guard")
J_SEC = (10.0, 20.0)
TRAIN_SEEDS = (0, 1, 2)
N_FOLDS, SEEDS_PER_FOLD = 4, 2
CROP, BATCH, STEPS = 4096, 3, 900
TOPK_FRAC = 0.01
N_BANK = 6
RATES_PER_10MIN = (0.5, 1.0, 2.0)
N_SURR_THRESHOLD = 3
MERGE_GAP = 20
SPEC_PATH = Path(__file__).resolve().parent.parent / "docs" / "learned" / "generator_spec.json"


def seed31(*key) -> int:
    from bugarach import surrogate_stats as ss
    return int(ss.seed_of((TAG,) + tuple(key)) & 0x7FFFFFFF)


# -- rasters and shifts -----------------------------------------------------------------------

def raster_of(trains, L) -> np.ndarray:
    x = np.zeros((len(trains), L), dtype=np.float32)
    for r, t in enumerate(trains):
        t = np.asarray(t, np.int64)
        t = t[(t >= 0) & (t < L)]
        x[r, t] = 1.0
    return x


def trains_of(raster) -> list:
    return [np.flatnonzero(row) for row in raster]


def rigid_frames(trains, L, J_frames, rng, shared=False):
    u_all = rng.uniform(-J_frames, J_frames, size=1 if shared else len(trains))
    out = []
    for r, t in enumerate(trains):
        u = u_all[0] if shared else u_all[r]
        k = np.floor(np.asarray(t, float) + 0.5 + u).astype(np.int64)
        out.append(k[(k >= 0) & (k < L)])
    return out


# -- data -------------------------------------------------------------------------------------

_CACHE: dict = {}


def spec():
    if "spec" not in _CACHE:
        _CACHE["spec"] = json.loads(SPEC_PATH.read_text())["generator"]
    return _CACHE["spec"]


def sim_recording(seed):
    key = ("sim", seed)
    if key not in _CACHE:
        import fair_bakeoff as fb
        _CACHE[key] = fb._make_recording(spec(), seed)
    return _CACHE[key]


def split():
    from bugarach.bench import fold_split
    return fold_split(n_folds=N_FOLDS, seeds_per_fold=SEEDS_PER_FOLD)


def real_recordings():
    if "real" not in _CACHE:
        os.environ.setdefault("LOOK_ROLE", "steps_excluded")
        import look_rigid_shift as lr
        recs, _ = lr.load("fast", None)
        from bugarach import surrogate_discriminator as sd
        mice = [r.mouse for r in recs]
        folds = sd.mouse_folds(mice, N_FOLDS, seed31("mouse-folds"))
        rows = []
        for r, f in zip(recs, folds):
            s, e = r.window
            L = e - s
            tr = [np.asarray(t, np.int64)[(np.asarray(t) >= s) & (np.asarray(t) < e)] - s
                  for t in r.trains]
            rows.append({"id": r.recording_id, "mouse": r.mouse, "fold": int(f), "dt": r.dt,
                         "L": L, "trains": tr})
        _CACHE["real"] = rows
    return _CACHE["real"]


def bank_for(items, J_sec, seed_key):
    """(raster, [N_BANK rigid-shift rasters], margin frames) per recording, crops of CROP frames."""
    bank = []
    for it in items:
        L, dt = it["L"], it["dt"]
        Jf = J_sec / dt
        margin = int(np.ceil(Jf)) + 1
        if L - 2 * margin < CROP:
            continue
        rng = np.random.RandomState(seed31("bank", seed_key, it["id"], J_sec))
        real = raster_of(it["trains"], L)
        surs = [raster_of(rigid_frames(it["trains"], L, Jf, rng), L) for _ in range(N_BANK)]
        bank.append((real, surs, margin))
    return bank


def sim_items(seeds, dt):
    from bugarach.learn.encode import encode
    items = []
    for sd_ in seeds:
        sl, _ = sim_recording(sd_)
        enc = encode(sl, dt=dt)
        items.append({"id": f"sim{sd_}", "dt": dt, "L": enc.n_frame,
                      "trains": trains_of(enc.raster)})
    return items


# -- the objective ----------------------------------------------------------------------------

def crop_score(model, x):
    import torch
    z = model(torch.from_numpy(np.ascontiguousarray(x)).unsqueeze(0)).squeeze(0)
    k = max(1, int(TOPK_FRAC * z.numel()))
    return torch.topk(z, k).values.mean()


def ssl_train(name, bank, seed, lr):
    import torch
    from bugarach.learn.nets import ARCHITECTURES, n_params
    from bugarach.learn.train import pin_threads
    torch.manual_seed(seed)
    pin_threads()
    model = ARCHITECTURES[name].make()
    opt = torch.optim.Adam(model.parameters(), lr=lr)
    rng = np.random.RandomState(seed)
    hist = []
    model.train()
    for step in range(STEPS):
        opt.zero_grad()
        tot = 0.0
        wins = 0
        for _ in range(BATCH):
            real, surs, margin = bank[rng.randint(len(bank))]
            a = rng.randint(margin, real.shape[1] - margin - CROP + 1)
            s = surs[rng.randint(len(surs))]
            sr = crop_score(model, real[:, a:a + CROP])
            ss_ = crop_score(model, s[:, a:a + CROP])
            loss = torch.nn.functional.softplus(ss_ - sr) / BATCH
            loss.backward()
            tot += float(loss.item())
            wins += int(float(sr) > float(ss_))
        opt.step()
        if step % 50 == 0 or step == STEPS - 1:
            hist.append((step, tot, wins / BATCH))
    model.eval()
    return model, n_params(model), hist


# -- scoring ----------------------------------------------------------------------------------

def probs(model, raster):
    import torch
    with torch.no_grad():
        return torch.sigmoid(model(torch.from_numpy(raster).unsqueeze(0))).squeeze(0).numpy()


def n_events(p, thr):
    from bugarach.learn.encode import decode
    return int(decode(p, threshold=thr, merge_gap_frames=MERGE_GAP).onset_frame.size)


def label_free_threshold(p_surs, minutes, rate_per_10min):
    """Lowest threshold, scanning DOWN from the top, before any surrogate fires more than ``rate``
    events per 10 minutes.

    Scanned downward and stopped at the first violation because the event count is not
    monotone in the threshold: low enough, every frame is above it and the whole recording
    merges into one detection, which a bare "lowest threshold that passes" would accept.
    """
    allowed = rate_per_10min * minutes / 10.0
    grid = np.unique(np.concatenate([np.geomspace(1e-4, 0.05, 12), np.arange(0.05, 0.95, 0.01),
                                     1.0 - np.geomspace(0.05, 1e-6, 16)]))[::-1]
    chosen = float(grid[0])
    for thr in grid:
        if max(n_events(ps, thr) for ps in p_surs) > allowed:
            break
        chosen = float(thr)
    return chosen


def score_held_out(model, held, dt, J_sec, oracle_thr, label):
    """Pooled bench scores on the held-out fold, at each label-free rate and the oracle."""
    from bugarach.bench import pool_scores
    from bugarach.learn.encode import decode, encode
    from bugarach.score import score_stream
    sp = split()
    te = list(sp.test(held))
    per = {f"label_free_{r:g}": [] for r in RATES_PER_10MIN}
    per["oracle"] = []
    thresholds = {k: [] for k in per}
    for sd_ in te:
        sl, gt = sim_recording(sd_)
        enc = encode(sl, dt=dt)
        p = probs(model, enc.raster)
        L = enc.n_frame
        rng = np.random.RandomState(seed31("thr-surr", label, sd_, J_sec))
        tr = trains_of(enc.raster)
        p_surs = [probs(model, raster_of(rigid_frames(tr, L, J_sec / dt, rng), L))
                  for _ in range(N_SURR_THRESHOLD)]
        minutes = L * dt / 60.0
        for r in RATES_PER_10MIN:
            thr = label_free_threshold(p_surs, minutes, r)
            det = decode(p, threshold=thr, merge_gap_frames=MERGE_GAP)
            per[f"label_free_{r:g}"].append(score_stream(gt, det.to_seconds(enc)))
            thresholds[f"label_free_{r:g}"].append(thr)
        if oracle_thr is not None:
            det = decode(p, threshold=oracle_thr, merge_gap_frames=MERGE_GAP)
            per["oracle"].append(score_stream(gt, det.to_seconds(enc)))
            thresholds["oracle"].append(oracle_thr)
    out = {}
    for k, scs in per.items():
        if not scs:
            continue
        b = pool_scores(scs, detector=label, regime="heldout", seeds=te)
        out[k] = {"f1": b.f1, "recall": b.recall, "precision": b.precision,
                  "n_planted": b.n_planted, "n_hit": b.n_hit, "n_detected": b.n_detected,
                  "hot_fa": b.hot_fa, "thresholds": thresholds[k]}
    return out


def oracle_threshold(model, held, dt, seed):
    from bugarach.learn.train import fold_maker, pick_threshold
    mk, _, _ = fold_maker(sim_recording, list(split().train(held)))
    thr, _ = pick_threshold(model, mk, dt=dt, seed=seed)
    return thr


def paired_checks(model, held, J_sec, label):
    """Paired crop scores: held-out real vs shared offset and vs rigid shift; unplanted twins."""
    import look_rigid_shift_controls as lc
    out = {}
    rows = [r for r in real_recordings() if r["fold"] == held]
    # Each entry is (real score, surrogate score). A shared offset only translates the crop and
    # tube is a convolution, so exact ties are common and are counted as half, not as losses.
    wins = {"real_vs_shared_offset": [], "real_vs_rigid_shift": []}
    for r in rows:
        Jf = J_sec / r["dt"]
        margin = int(np.ceil(Jf)) + 1
        L = r["L"]
        rng = np.random.RandomState(seed31("check", label, r["id"], J_sec))
        real = raster_of(r["trains"], L)
        shared = raster_of(rigid_frames(r["trains"], L, Jf, rng, shared=True), L)
        rigid = raster_of(rigid_frames(r["trains"], L, Jf, rng), L)
        import torch
        with torch.no_grad():
            for a in range(margin, L - margin - CROP + 1, CROP):
                s_r = float(crop_score(model, real[:, a:a + CROP]))
                wins["real_vs_shared_offset"].append(
                    (s_r, float(crop_score(model, shared[:, a:a + CROP]))))
                wins["real_vs_rigid_shift"].append(
                    (s_r, float(crop_score(model, rigid[:, a:a + CROP]))))
    for k, v in wins.items():
        out[k] = paired_summary(v)
    tw = []
    import torch
    for t in range(10):
        _, un, shape = lc.twin_pair("fast", None, 0.2, t)
        L = shape["n_frames"]
        Jf = J_sec / shape["dt"]
        margin = int(np.ceil(Jf)) + 1
        rng = np.random.RandomState(seed31("twin-check", label, t, J_sec))
        real = raster_of(un, L)
        rigid = raster_of(rigid_frames(un, L, Jf, rng), L)
        with torch.no_grad():
            for a in range(margin, L - margin - CROP + 1, CROP):
                tw.append((float(crop_score(model, real[:, a:a + CROP])),
                           float(crop_score(model, rigid[:, a:a + CROP]))))
    out["unplanted_twin_vs_rigid_shift"] = paired_summary(tw)
    return out


def paired_summary(pairs):
    """Share of pairs where real scores higher (ties count half), the tie share, the mean gap."""
    if not pairs:
        return {"share_real_higher": None, "n_crops": 0}
    a = np.asarray(pairs, float)
    tie = np.isclose(a[:, 0], a[:, 1], rtol=0, atol=1e-6)
    higher = (a[:, 0] > a[:, 1]) & ~tie
    return {"share_real_higher": float(np.mean(higher + 0.5 * tie)), "tie_share": float(tie.mean()),
            "mean_gap": float(np.mean(a[:, 0] - a[:, 1])), "n_crops": int(len(a))}


def widths_sec(model, dt):
    try:
        import torch
        return (torch.exp(model.log_center.detach()).numpy() * dt).tolist()
    except AttributeError:
        return None


# -- tasks ------------------------------------------------------------------------------------

def task(args):
    arm, name, J_sec, seed, held, quick = args
    import fair_bakeoff as fb
    global STEPS
    if quick:
        STEPS = 60
    dt = float(spec()["grid_sec"])
    t0 = time.time()
    label = f"{arm}-{name}-{J_sec}-{seed}-{held}"
    res = {"arm": arm, "model": name, "J_sec": J_sec, "train_seed": seed, "held_fold": held}
    if arm == "supervised":
        from bugarach.learn.train import fold_maker, train
        mk, n_fit, _ = fold_maker(sim_recording, list(split().train(held)))
        tr = train(name, mk, n_train=min(10, n_fit), steps=STEPS, crop=CROP, batch=BATCH,
                   lr=fb.LR[name], seed=seed)
        model, n_par, hist, oracle = tr.model, tr.n_params, tr.history, tr.threshold
    elif arm == "untrained":
        import torch
        from bugarach.learn.nets import ARCHITECTURES, n_params
        torch.manual_seed(seed)
        model = ARCHITECTURES[name].make().eval()
        n_par, hist = n_params(model), []
        oracle = oracle_threshold(model, held, dt, seed)
    else:
        if arm == "ssl_sim":
            items = sim_items(list(split().train(held)), dt)
        else:
            items = [r for r in real_recordings() if r["fold"] != held]
        bank = bank_for(items, J_sec, (arm, held))
        model, n_par, hist = ssl_train(name, bank, seed, fb.LR[name])
        res["n_train_recordings"] = len(bank)
        oracle = oracle_threshold(model, held, dt, seed)
    res["n_params"] = int(n_par)
    res["history"] = hist
    res["train_seconds"] = time.time() - t0
    res["centre_widths_sec"] = widths_sec(model, dt)
    res["scores"] = score_held_out(model, held, dt, J_sec, oracle, label)
    if arm in ("ssl_sim", "ssl_real", "untrained"):
        res["checks"] = paired_checks(model, held, J_sec, label)
    res["seconds"] = time.time() - t0
    return res


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", required=True)
    ap.add_argument("--quick", action="store_true", help="one fold, one seed, 60 steps")
    ap.add_argument("--jobs", type=int, default=12)
    a = ap.parse_args(argv)
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    folds = (0,) if a.quick else tuple(range(N_FOLDS))
    seeds = (0,) if a.quick else TRAIN_SEEDS
    tasks = []
    for held in folds:
        for seed in seeds:
            for name in MODELS:
                tasks.append(("supervised", name, J_SEC[0], seed, held, a.quick))
                tasks.append(("untrained", name, J_SEC[0], seed, held, a.quick))
                for J in J_SEC:
                    for arm in ("ssl_sim", "ssl_real"):
                        tasks.append((arm, name, J, seed, held, a.quick))
    meta = {"tag": TAG, "started": time.strftime("%Y-%m-%dT%H:%M:%S%z"), "quick": a.quick,
            "models": MODELS, "J_sec": J_SEC, "train_seeds": seeds, "folds": folds,
            "crop": CROP, "batch": BATCH, "steps": 60 if a.quick else STEPS,
            "topk_frac": TOPK_FRAC, "n_bank": N_BANK, "rates_per_10min": RATES_PER_10MIN,
            "merge_gap_frames": MERGE_GAP, "spec": str(SPEC_PATH.name), "exploratory": True,
            "n_tasks": len(tasks)}
    (out / "meta.json").write_text(json.dumps(meta, indent=2))
    t0 = time.time()
    with mp.get_context("spawn").Pool(a.jobs, maxtasksperchild=4) as pool:
        for i, r in enumerate(pool.imap_unordered(task, tasks)):
            with open(out / "results.jsonl", "a") as fh:
                fh.write(json.dumps(r, default=float) + "\n")
            f1 = {k: round(v["f1"], 3) for k, v in r["scores"].items()}
            print(f"[{time.time() - t0:6.0f}s] {i + 1}/{len(tasks)} {r['arm']} {r['model']} "
                  f"J{r['J_sec']:g} s{r['train_seed']} fold{r['held_fold']} {f1}", flush=True)
    meta["seconds"] = time.time() - t0
    (out / "meta.json").write_text(json.dumps(meta, indent=2))
    print("done", out)


if __name__ == "__main__":
    main()
