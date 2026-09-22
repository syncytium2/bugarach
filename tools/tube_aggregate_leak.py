#!/usr/bin/env python3
"""Can a model that sees only what `tube` sees tell a recording from its rigid shift?

    python tools/tube_aggregate_leak.py --out <folder>
    python tools/tube_aggregate_leak.py --out <folder> --limit 6 --quick
    python tools/tube_aggregate_leak.py --out <folder> --banks fitted --jobs 12

Stage 1 of the tube plan, and the aggregate-channel leak test that
``docs/todo/2026-09-12-tube-cannot-tell-a-count-leak-from-coordination.md`` names as the
condition before any label-free objective is built on `tube`. Exploratory.

**Two banks of channels**, and the second exists because the first was wrong about what it
claimed to be:

* ``init`` — `tube` at **initialisation**. `tube` averages the onset raster over cells before
  its first kernel (``src/bugarach/learn/nets/tube.py``), so its whole input is the cells-mean
  trace. Here that trace is built the same way — binary raster, each onset widened ±1 frame,
  mean over ROIs — over each recording's whole generation window, then passed through
  difference-of-Gaussians kernels (area-normalised centre minus surround, surround ratio 8) at
  centre widths of 1–128 frames. ⚠ **These are tube's starting values, not a fitted tube.** A
  reviewer fitted one the bake-off's way (2026-09-16) and found onsets widened ±2 frames,
  surround ratios of 9.7–21.1 and centre widths of 2.3–5.3 frames; 128 frames lies outside the
  model's own clamp of [0.5, 64]. This bank licensed the label-free run, so it is kept and
  re-run unchanged, beside the bank that should have been used.
* ``fitted`` — **the channels a fitted model's head actually receives.** `tube` and `line` are
  each fitted with labels the way the bake-off fits them, one fit per held-out fold, and a
  forward pre-hook on ``model.head`` captures its input on every real and surrogate recording:
  for `tube` the widened cells-mean trace and its four fitted centre-surround responses; for
  `line` its four shares-of-field-lit, their four responses and three concentration ratios.
  No kernel is re-derived, so nothing can drift from the model. Lab fast stream only, the
  stream the models were fitted and trained for.

Per interior 60 s window and per channel: the channel's spread, its 1st and 99th percentiles
and its maximum; plus the raw cells-mean trace's mean, spread and 99th percentile. A linear
forced choice with mouse-grouped folds and a refitting bootstrap, exactly as the rigid-shift
look scores its leak test (:mod:`look_rigid_shift`).

**Contrasts**, at each displacement *J*:

1. **real vs shared offset** — every ROI moved by one offset (:mod:`look_rigid_shift_controls`).
   Keeps coordination and slow shared modulation, moves counts across window edges exactly as
   rigid shift does. Anything above chance is a count or edge leak on the channel.
2. **unplanted twin vs its rigid shift** — synthetic, stationary, independent ROIs. ⚠ Rigid shift
   leaves such a process invariant, so this contrast cannot fail for any leak (a murderboard
   finding, 2026-09-17). Kept for continuity only.
3. **real vs rigid shift**, pooled and **per channel** — what the model could learn, and where.
   At the smallest *J* (1.6 s fast, 1.4 s slow) slow co-modulation survives the shift, so
   separation there is not modulation.
4. **planted twin vs its rigid shift** — must separate: the channels can see planted events.
5. **shared-modulation twin vs its rigid shift** — no events, one slow rate change shared by every
   ROI. Must separate on any channel that sees co-modulation, which is what makes a large-*J*
   separation on real recordings ambiguous.
6. **independent-modulation twin vs its rigid shift** — each ROI's rate moves on its own. Must
   read chance.
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
import look_rigid_shift_controls as lc                       # noqa: E402
from bugarach import surrogate_stats as ss                   # noqa: E402
from bugarach import surrogates as sg                        # noqa: E402

TAG = "tube-aggregate-2026-09-15"
J_SEC = {"fast": (1.6, 5.0, 10.0, 20.0, 40.0), "slow": (1.4, 5.6, 11.2, 22.4, 44.8)}
"""1.6 s (fast) and 1.4 s (slow) added 2026-09-17: a shift too small to move slow co-modulation, so a
channel that separates real from rigid shift only at large J is seeing modulation, not coordination."""
CENTRES = (1, 2, 4, 8, 16, 32, 64, 128)
SURROUND_RATIO = 8.0
WIDEN = 1
N_TWINS = 20
PER_SCALE = ("sd", "p1", "p99", "max")
FITTED_MODELS = ("tube", "line")
FITTED_STREAM = "fast"


def seed31(*key) -> int:
    return int(ss.seed_of((TAG,) + tuple(key)) & 0x7FFFFFFF)


def dog_kernel(c: float, ratio: float = SURROUND_RATIO) -> np.ndarray:
    s = c * ratio
    half = int(np.ceil(3 * s))
    t = np.arange(-half, half + 1, dtype=float)
    centre = np.exp(-0.5 * (t / c) ** 2)
    surround = np.exp(-0.5 * (t / s) ** 2)
    return centre / centre.sum() - surround / surround.sum()


KERNELS = {c: dog_kernel(float(c)) for c in CENTRES}


def bright_trace(trains, window) -> np.ndarray:
    """Cells-mean of the binary raster over ``window``, each onset widened ±WIDEN frames."""
    s, e = int(window[0]), int(window[1])
    L = e - s
    acc = np.zeros(L, dtype=float)
    for t in trains:
        t = np.asarray(t, np.int64)
        t = t[(t >= s) & (t < e)] - s
        if t.size == 0:
            continue
        row = np.zeros(L, dtype=bool)
        for d in range(-WIDEN, WIDEN + 1):
            k = t + d
            row[k[(k >= 0) & (k < L)]] = True
        acc += row
    return acc / max(1, len(trains))


def raster(trains, window) -> np.ndarray:
    s, e = int(window[0]), int(window[1])
    x = np.zeros((len(trains), e - s), dtype=np.float32)
    for r, t in enumerate(trains):
        t = np.asarray(t, np.int64)
        x[r, t[(t >= s) & (t < e)] - s] = 1.0
    return x


# -- the two banks ----------------------------------------------------------------------------

def init_channels(trains, window):
    """(trace, channels): the widened cells-mean and its response at each initial centre width."""
    b = bright_trace(trains, window)
    return b, np.stack([np.convolve(b, KERNELS[c], mode="same") for c in CENTRES])


def head_input(model, x) -> np.ndarray:
    """What ``model.head`` receives for raster ``x`` (n_roi, T), captured, not re-derived."""
    import torch
    got = {}
    hook = model.head.register_forward_pre_hook(lambda _m, inp: got.setdefault("x", inp[0]))
    try:
        with torch.no_grad():
            model(torch.from_numpy(np.ascontiguousarray(x)).unsqueeze(0))
    finally:
        hook.remove()
    return got["x"].squeeze(0).numpy().astype(float)


def fitted_channels(model):
    def channels(trains, window):
        x = raster(trains, window)
        return x.mean(axis=0).astype(float), head_input(model, x)
    return channels


def window_features(trains, window, wins, channels=init_channels):
    """One row per window: trace mean, sd, p99; then per channel sd, p1, p99, max."""
    b, resp = channels(trains, window)
    s = int(window[0])
    rows = []
    for a, e in wins:
        seg = b[a - s:e - s]
        row = [seg.mean(), seg.std(), np.percentile(seg, 99)]
        for r in resp[:, a - s:e - s]:
            row += [r.std(), np.percentile(r, 1), np.percentile(r, 99), r.max()]
        rows.append(row)
    return np.asarray(rows)


def feature_names(channel_labels=CENTRES):
    names = ["trace_mean", "trace_sd", "trace_p99"]
    for c in channel_labels:
        names += [f"c{c}_{k}" for k in PER_SCALE]
    return names


def columns_for(scale, names):
    if scale == "all":
        return np.arange(len(names))
    if scale == "trace":
        return np.array([i for i, n in enumerate(names) if n.startswith("trace_")])
    return np.array([i for i, n in enumerate(names) if n.startswith(f"c{scale}_")])


def score(Xr, Xs, groups, n_boot, seed, labels=CENTRES, per_scale=True):
    names = feature_names(labels)
    out = {}
    scales = ["all", "trace"] + list(labels) if per_scale else ["all"]
    for sc in scales:
        cols = columns_for(sc, names)
        p, dist = lr.refit_bootstrap(Xr[:, cols], Xs[:, cols], groups, groups,
                                     n_boot if sc == "all" else max(40, n_boot // 5), seed)
        out[str(sc)] = lr.summarize(p, dist)
    return out


# -- contrasts --------------------------------------------------------------------------------

def real_contrasts(stream, J_sec, n_boot, limit, channels, labels, seed_key):
    recs, _ = lr.load(stream, limit)
    Xr, Xrig, Xsh, mice = [], [], [], []
    count_change = {"rigid_shift": [0, 0], "shared_shift": [0, 0]}
    for r in recs:
        wins = lr.interior_windows(r)
        if not wins:
            continue
        Jf = round(J_sec / r.dt, 9)
        rig = sg.generate("rigid_shift", r.trains, r.window,
                          (lr.TAG, "leak", r.recording_id, stream, "rigid_shift", Jf), J=Jf).trains
        sh, _, _ = lc.shared_shift(r.trains, r.window, ("leak", r.recording_id, stream, Jf), Jf)
        Xr.append(window_features(r.trains, r.window, wins, channels))
        Xrig.append(window_features(rig, r.window, wins, channels))
        Xsh.append(window_features(sh, r.window, wins, channels))
        mice += [r.mouse] * len(wins)
        for name, tr in (("rigid_shift", rig), ("shared_shift", sh)):
            for a, e in wins:
                n_real = sum(int(((t >= a) & (t < e)).sum()) for t in r.trains)
                n_sur = sum(int(((np.asarray(t) >= a) & (np.asarray(t) < e)).sum()) for t in tr)
                count_change[name][0] += abs(n_sur - n_real)
                count_change[name][1] += n_real
    Xr, Xrig, Xsh, mice = np.vstack(Xr), np.vstack(Xrig), np.vstack(Xsh), np.asarray(mice)
    seed = seed31(*seed_key)
    return {"kind": "real", "stream": stream, "J_sec": J_sec, "n_pairs": int(len(mice)),
            "n_mice": int(np.unique(mice).size),
            "real_vs_rigid_shift": score(Xr, Xrig, mice, n_boot, seed, labels),
            "real_vs_shared_offset": score(Xr, Xsh, mice, n_boot, seed + 1, labels),
            "window_count_abs_change_share": {k: v[0] / max(1, v[1])
                                              for k, v in count_change.items()}}


def twin_contrasts(stream, J_sec, n_boot, limit, channels, labels, seed_key):
    """Synthetic twins against their rigid shift. ``planted`` must separate. ``unplanted`` is
    stationary with independent ROIs, which rigid shift leaves invariant, so it cannot fail (kept
    for continuity). The two modulation twins (``tools/tube_self_supervised.modulated``, added
    2026-09-17) carry no events: ``shared_modulation`` must separate on any channel that sees
    co-modulation, and ``independent_modulation`` must read chance."""
    import tube_self_supervised as ts
    X = {"planted": ([], []), "unplanted": ([], []), "shared_modulation": ([], []),
         "independent_modulation": ([], [])}
    groups = []
    shape = None
    for t in range(N_TWINS):
        pl, un, shape = lc.twin_pair(stream, limit, 0.2, t)
        n_frames, dt = shape["n_frames"], shape["dt"]
        w = int(np.floor(lr.WINDOW_SEC / dt + 0.5))
        wins = [(i * w, (i + 1) * w) for i in range(n_frames // w)][1:-1]
        Jf = round(J_sec / dt, 9)
        rng_mod = np.random.RandomState(seed31("twin-mod", stream, t))
        mods = {k: ts.modulated(un, n_frames, dt, rng_mod, k == "shared_modulation")
                for k in ("shared_modulation", "independent_modulation")}
        for kind, tr in (("planted", pl), ("unplanted", un), *mods.items()):
            rig = sg.generate("rigid_shift", tr, (0, n_frames),
                              (TAG, "twin", stream, kind, t, Jf), J=Jf).trains
            X[kind][0].append(window_features(tr, (0, n_frames), wins, channels))
            X[kind][1].append(window_features(rig, (0, n_frames), wins, channels))
        groups += [f"twin{t}"] * len(wins)
    groups = np.asarray(groups)
    seed = seed31(*seed_key)
    return {"kind": "twin", "stream": stream, "J_sec": J_sec, "n_pairs": int(len(groups)),
            "n_twins": N_TWINS, "twin_shape": shape, "participation": 0.2,
            "unplanted_vs_rigid_shift": score(np.vstack(X["unplanted"][0]),
                                              np.vstack(X["unplanted"][1]), groups, n_boot, seed,
                                              labels, per_scale=False),
            "planted_vs_rigid_shift": score(np.vstack(X["planted"][0]),
                                            np.vstack(X["planted"][1]), groups, n_boot, seed + 1,
                                            labels, per_scale=False),
            "shared_modulation_vs_rigid_shift": score(
                np.vstack(X["shared_modulation"][0]), np.vstack(X["shared_modulation"][1]),
                groups, n_boot, seed + 2, labels, per_scale=False),
            "independent_modulation_vs_rigid_shift": score(
                np.vstack(X["independent_modulation"][0]),
                np.vstack(X["independent_modulation"][1]), groups, n_boot, seed + 3, labels,
                per_scale=False),
            "modulation": {"period_sec": ts.MOD_PERIOD_SEC, "depth": ts.MOD_DEPTH}}


def real_task(args):
    stream, J_sec, n_boot, limit = args
    r = real_contrasts(stream, J_sec, n_boot, limit, init_channels, CENTRES,
                       ("real", stream, J_sec))
    return {"bank": "init", **r}


def twin_task(args):
    stream, J_sec, n_boot, limit = args
    r = twin_contrasts(stream, J_sec, n_boot, limit, init_channels, CENTRES,
                       ("twin", stream, J_sec))
    return {"bank": "init", **r}


def fitted_task(args):
    """Fit one model with labels as the bake-off does, then run every contrast on its head input."""
    name, held, n_boot, limit, quick = args
    import fair_bakeoff as fb
    import tube_self_supervised as ts
    from bugarach.learn.train import fold_maker, train
    t0 = time.time()
    mk, n_fit, _ = fold_maker(ts.sim_recording, list(ts.split().train(held)))
    tr = train(name, mk, n_train=min(10, n_fit), steps=60 if quick else ts.STEPS, crop=ts.CROP,
               batch=ts.BATCH, lr=fb.LR[name], seed=0)
    model = tr.model.eval()
    channels = fitted_channels(model)
    probe = raster([np.array([10])], (0, 400))
    labels = tuple(range(head_input(model, probe).shape[0]))
    bank = {"bank": "fitted", "model": name, "held_fold": held, "train_seed": 0,
            "channels": len(labels), "fitted_parameters": ts.fitted_parameters(model)}
    out = []
    for J_sec in J_SEC[FITTED_STREAM]:
        out.append({**bank, **real_contrasts(FITTED_STREAM, J_sec, n_boot, limit, channels, labels,
                                            ("fitted-real", name, held, J_sec))})
        out.append({**bank, **twin_contrasts(FITTED_STREAM, J_sec, n_boot, limit, channels, labels,
                                            ("fitted-twin", name, held, J_sec))})
    for r in out:
        r["seconds"] = time.time() - t0
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", required=True)
    ap.add_argument("--limit", type=int, default=None)
    ap.add_argument("--quick", action="store_true")
    ap.add_argument("--jobs", type=int, default=12)
    ap.add_argument("--streams", nargs="*", default=["fast", "slow"])
    ap.add_argument("--banks", nargs="*", default=["init", "fitted"], choices=["init", "fitted"])
    a = ap.parse_args(argv)
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    n_boot = 40 if a.quick else 1000
    tasks = []
    if "init" in a.banks:
        for stream in a.streams:
            for J in J_SEC[stream]:
                tasks.append((real_task, (stream, J, n_boot, a.limit)))
                tasks.append((twin_task, (stream, J, n_boot, a.limit)))
    if "fitted" in a.banks:
        import tube_self_supervised as ts
        for name in FITTED_MODELS:
            for held in ((0,) if a.quick else range(ts.N_FOLDS)):
                tasks.append((fitted_task, (name, held, n_boot, a.limit, a.quick)))
    from bugarach import provenance
    meta = {"tag": TAG, "started": time.strftime("%Y-%m-%dT%H:%M:%S%z"), "limit": a.limit,
            "n_boot": n_boot, "banks": a.banks,
            "J_sec": {s: J_SEC[s] for s in a.streams}, "centres_frames": CENTRES,
            "surround_ratio": SURROUND_RATIO, "widen_frames": WIDEN, "n_twins": N_TWINS,
            "features": feature_names(), "fitted_models": FITTED_MODELS,
            "fitted_stream": FITTED_STREAM,
            "provenance": provenance.stamp(produced_by="tools/tube_aggregate_leak.py"),
            "exploratory": True}
    (out / "meta.json").write_text(json.dumps(meta, indent=2))
    results = []
    t0 = time.time()
    with mp.get_context("spawn").Pool(a.jobs) as pool:
        futs = [pool.apply_async(fn, (args,)) for fn, args in tasks]
        for f in futs:
            got = f.get()
            for r in (got if isinstance(got, list) else [got]):
                results.append(r)
                print(f"[{time.time() - t0:6.0f}s] {r['bank']} {r.get('model', '')} "
                      f"{r['kind']} {r['stream']} {r['J_sec']}", flush=True)
            (out / "results.json").write_text(json.dumps(results, indent=2, default=str))
    meta["seconds"] = time.time() - t0
    (out / "meta.json").write_text(json.dumps(meta, indent=2))
    print("done", out)


if __name__ == "__main__":
    main()
