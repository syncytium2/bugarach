#!/usr/bin/env python3
"""Stage 2 of the tube plan: train every model in ``MODELS`` with rigid shift as the only negative,
then score them on the planted-truth bake-off beside supervised, untrained and zero-parameter
scorers. Exploratory.

    python tools/tube_self_supervised.py --out <folder>
    python tools/tube_self_supervised.py --out <folder> --quick --jobs 12

Runs only because Stage 1 (``tools/tube_aggregate_leak.py``) passed on the lab fast stream: a
classifier reading tube's cells-mean channel could not tell real from a shared offset, nor an
unplanted twin from its rigid shift, while real against rigid shift separated at event-width
kernel scales. That is the aggregate-channel test the tube foot-gun todo asks for first.
⚠ A murderboard (2026-09-17) found that licence narrower than it reads: the unplanted twin cannot
fail under rigid shift, and nothing in Stage 1 could tell sub-second coordination from slow shared
modulation. The small-J check and the modulation twins in ``paired_checks`` exist for that.

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
* ``baseline`` — the zero-parameter scorers in ``BASELINES``, one row per displacement, no seed:
  what a detector that fires with nothing learned scores under the same rules.

**Two thresholds** for every model on the held-out fold:

* *label-free* — per recording, found by scanning thresholds DOWN from the top of a quantile grid
  and stopping at the first at which any of three rigid shifts of **that recording** fires more
  than ``r`` events per 10 minutes; ``r`` in 0.5, 1, 2. A scan that never exceeds the rate falls
  to the grid's floor, and is recorded (``at_grid_floor``).
* *oracle* (the report's truth-reading threshold) — ``pick_threshold`` on the training folds'
  planted truth, the bake-off's own rule, with its edge report. It reads labels.

**Paired checks on every model** (``paired_checks``): held-out real crops against their rigid shift
at the training J and at ``J_SMALL_SEC``, against a shared offset at the same and at an independent
crop, and against a thinned copy; synthetic twins (stationary, shared-modulation,
independent-modulation) against their rigid shift. The docstring of ``paired_checks`` says what
each can and cannot fail on. Also stored per fit: fitted centre widths in seconds and every
parameter outside the head.
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
MODELS = ("tube", "tube_guard", "line", "line_length", "line_bound")
"""``line`` joined on 2026-09-15: it counts the lit ROIs before pooling, so it is the
architecture whose distinctness the tube models lack (``bugarach.learn.nets.line``).
``line_bound`` joined on 2026-09-16: ``line`` with its vote bounded in time as well as height,
so whether that bound matters is measured in the same run."""
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
        os.environ.setdefault("LOOK_ROLE", "steps_and_pins_excluded")
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
    """Per-frame LOGITS, not probabilities. A ranking loss fixes no scale, so a self-supervised
    model's logits grow until the sigmoid rounds them to exactly 1.0 and no probability grid can
    separate frames. Every threshold here is chosen in logit space, from quantiles of the scores
    the model actually produced; ``decode`` compares a score against a threshold and does not care
    which scale it is."""
    import torch
    with torch.no_grad():
        return model(torch.from_numpy(raster).unsqueeze(0)).squeeze(0).numpy().astype(float)


def quantile_grid(z_all):
    """Descending candidate thresholds: just above the maximum, then quantiles down to the
    minimum.

    ⚠ Until 2026-09-16 the grid stopped at the MEDIAN score, so the lowest threshold on offer
    let half of all frames fire, and the truth-reading search had no guard to say when it
    stopped there. The untrained arm's detections covering nearly a whole recording is what
    that floor looks like. The grid now reaches the minimum, and ``pick_threshold`` reports
    an optimum on either end."""
    z = np.concatenate([np.ravel(v) for v in z_all])
    qs = np.quantile(z, 1.0 - np.geomspace(1.0, 1e-6, 120))
    return np.unique(np.concatenate([[z.max() + 1e-6], qs]))[::-1]


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
    grid = quantile_grid(p_surs)
    chosen = float(grid[0])
    for thr in grid:
        if max(n_events(ps, thr) for ps in p_surs) > allowed:
            break
        chosen = float(thr)
    else:
        # No threshold on the grid ever exceeded the rate, so the scan fell through to the
        # grid's floor — the degenerate case the downward scan was written to avoid. Said
        # rather than returned silently.
        return chosen, True
    return chosen, False


def score_held_out(model, held, dt, J_sec, oracles, label):
    """Pooled bench scores on the held-out fold, at each label-free rate and each oracle."""
    from bugarach.bench import pool_scores
    from bugarach.learn.encode import decode, encode
    from bugarach.score import score_stream
    sp = split()
    te = list(sp.test(held))
    per = {f"label_free_{r:g}": [] for r in RATES_PER_10MIN}
    for k in oracles:
        per[k] = []
    thresholds = {k: [] for k in per}
    shape = {k: {"width_sec_median": [], "width_sec_max": [], "coverage_share": [],
                 "at_grid_floor": []} for k in per}

    def record(k, thr, det, enc, gt, L, floor=False):
        per[k].append(score_stream(gt, det.to_seconds(enc)))
        thresholds[k].append(thr)
        w = np.asarray(det.width_frame, float)
        shape[k]["width_sec_median"].append(float(np.median(w) * dt) if w.size else None)
        shape[k]["width_sec_max"].append(float(w.max() * dt) if w.size else None)
        shape[k]["coverage_share"].append(float(w.sum() / L))
        shape[k]["at_grid_floor"].append(bool(floor))

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
            thr, floor = label_free_threshold(p_surs, minutes, r)
            record(f"label_free_{r:g}", thr, decode(p, threshold=thr, merge_gap_frames=MERGE_GAP),
                   enc, gt, L, floor)
        for k, thr in oracles.items():
            if thr is None or not np.isfinite(thr):
                continue
            record(k, thr, decode(p, threshold=thr, merge_gap_frames=MERGE_GAP), enc, gt, L)
    out = {}
    for k, scs in per.items():
        if not scs:
            # Said, not skipped: an oracle that found no scoring threshold is a row with a
            # reason, where it used to be indistinguishable from an arm that had no oracle.
            out[k] = {"f1": None, "not_scored": "no threshold on the grid scored"}
            continue
        b = pool_scores(scs, detector=label, regime="heldout", seeds=te)
        out[k] = {"f1": b.f1, "recall": b.recall, "precision": b.precision,
                  "n_planted": b.n_planted, "n_hit": b.n_hit, "n_detected": b.n_detected,
                  "hot_fa": b.hot_fa, "thresholds": thresholds[k], **shape[k]}
    return out


def fit_and_val_seeds(held):
    """The training folds' recordings split as ``fold_maker`` splits them: (fit, validation)."""
    from bugarach.learn.train import fold_maker
    seeds = list(split().train(held))
    _, n_fit, n_val = fold_maker(sim_recording, seeds)
    return seeds[:n_fit], seeds[n_fit:], n_val


def oracle_threshold(model, held, dt, seed):
    """F1-best logit threshold on the training folds' threshold-validation recordings, picked by
    ``bugarach.learn.train.pick_threshold`` itself over a quantile grid in logit space. Reads
    planted truth: comparison only. Returns ``(threshold, report)``.

    ⚠ This used to re-derive ``pick_threshold`` and dropped its edge-of-grid guard; it also
    asked for four validation seeds that ``fold_maker`` serves from two recordings. It now
    calls the function, with ``fold_maker``'s own ``n_val``, and the report says whether the
    choice sat on the grid's floor or ceiling."""
    import warnings
    from bugarach.learn.train import fold_maker, pick_threshold
    mk, _, n_val = fold_maker(sim_recording, list(split().train(held)))
    report: dict = {}
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", RuntimeWarning)   # recorded in `report` instead
        thr, _ = pick_threshold(model, mk, dt=dt, seed=seed, n_val=n_val,
                                merge_gap_frames=MERGE_GAP, grid=quantile_grid, logits=True,
                                report=report)
    return (float(thr) if np.isfinite(thr) else None), report


def thinned(trains, share, rng):
    """Each ROI keeps a random ``1 - share`` of its onsets, in place: counts fall, timing and
    cross-ROI alignment of what remains do not move."""
    return [np.asarray(t)[rng.random_sample(len(t)) >= share] for t in trains]


THIN_SHARE = 0.2
"""The positive control's size: a fifth of every ROI's onsets removed."""


J_SMALL_SEC = 1.6
"""The small displacement for the control that separates coordination from slow modulation. A
murderboard reviewer (2026-09-17) showed every earlier paired check passes for a scorer with no
events and only a slow rate change shared across ROIs. Such a change survives a 1.6 s shift almost
untouched; sub-second alignment between ROIs does not. So a model that learned modulation reads
chance against this shift, and one that learned coordination does not."""

MOD_PERIOD_SEC = 40.0
MOD_DEPTH = 0.9
"""The modulation twins: each ROI of an unplanted twin keeps an onset at time *t* with probability
``(1 + depth * sin(2 pi t / period + phase)) / (1 + depth)``. One phase for every ROI makes the
SHARED-modulation twin (no events, only co-modulation); a phase per ROI makes the
INDEPENDENT-modulation twin (each ROI's rate moves, nothing moves together)."""


def modulated(trains, L, dt, rng, shared):
    phases = (np.full(len(trains), rng.uniform(0, 2 * np.pi)) if shared
              else rng.uniform(0, 2 * np.pi, len(trains)))
    out = []
    for r, t in enumerate(trains):
        t = np.asarray(t, np.int64)
        t = t[(t >= 0) & (t < L)]
        keep = (1 + MOD_DEPTH * np.sin(2 * np.pi * t * dt / MOD_PERIOD_SEC + phases[r])) \
            / (1 + MOD_DEPTH)
        out.append(t[rng.random_sample(t.size) < keep])
    return out


def crop_pairs(score, real, sur, starts, sur_starts=None):
    """(score of the real crop, score of the surrogate crop) at each start. ``score`` maps a
    (n_roi, CROP) raster to a float; ``sur_starts`` draws the surrogate crop elsewhere."""
    sur_starts = starts if sur_starts is None else sur_starts
    return [(score(real[:, a:a + CROP]), score(sur[:, b:b + CROP]))
            for a, b in zip(starts, sur_starts)]


def model_scorer(model):
    import torch

    def score(x):
        with torch.no_grad():
            return float(crop_score(model, x))
    return score


def paired_checks(score, held, J_sec, label):
    """Paired crop scores on held-out real recordings, plus synthetic twins. ``score`` maps a
    crop to a float (``model_scorer`` for a network).

    On the held-out real recordings:

    * ``real_vs_rigid_shift`` — what the objective paid for.
    * ``real_vs_rigid_shift_small_J`` — the same at 1.6 s. **The control that separates
      coordination from slow shared modulation**: see ``J_SMALL_SEC``.
    * ``real_vs_shared_offset`` — both crops at the same index. ⚠ Weak by construction: the
      two rasters differ by one global translation and every model here is convolutional, so
      the crops largely share frames and many pairs tie (reported as ``tie_share``, counted
      half). Kept so the change from the previous run is visible.
    * ``real_vs_shared_offset_independent_crop`` — the surrogate crop drawn at an index
      independent of the real one. ⚠ Two stretches of one recording are exchangeable, so this
      reads chance for ANY scorer; it shows ties are not what holds the same-crop check at 0.5,
      and nothing more.
    * ``real_vs_thinned`` — a fifth of every ROI's onsets removed, same crop. It moves for any
      scorer that rises with onset count; it shows the checks can register a count change, not
      that they can register a leak.

    On synthetic twins (``look_rigid_shift_controls.twin_pair``), each against its own rigid shift:

    * ``unplanted_twin_vs_rigid_shift`` — ⚠ stationary, independent ROIs, which rigid shift
      leaves invariant: it cannot fail for any leak. Kept for continuity only.
    * ``shared_modulation_twin_vs_rigid_shift`` — no events, one slow rate change shared by
      every ROI. **Separates for a model that learned modulation**; a model that learned only
      coordination has nothing here to find.
    * ``independent_modulation_twin_vs_rigid_shift`` — each ROI's rate moves on its own phase.
      Must read chance: nothing moves together.
    """
    import look_rigid_shift_controls as lc
    out = {}
    rows = [r for r in real_recordings() if r["fold"] == held]
    wins = {"real_vs_shared_offset": [], "real_vs_shared_offset_independent_crop": [],
            "real_vs_rigid_shift": [], "real_vs_thinned": [], "real_vs_rigid_shift_small_J": []}
    for r in rows:
        Jf = J_sec / r["dt"]
        margin = int(np.ceil(Jf)) + 1
        L = r["L"]
        rng = np.random.RandomState(seed31("check", label, r["id"], J_sec))
        real = raster_of(r["trains"], L)
        shared = raster_of(rigid_frames(r["trains"], L, Jf, rng, shared=True), L)
        rigid = raster_of(rigid_frames(r["trains"], L, Jf, rng), L)
        # Drawn from its own streams so the draws above match the previous runs'.
        rng_extra = np.random.RandomState(seed31("check-extra", label, r["id"], J_sec))
        thin = raster_of(thinned(r["trains"], THIN_SHARE, rng_extra), L)
        rng_small = np.random.RandomState(seed31("check-small", label, r["id"], J_sec))
        small = raster_of(rigid_frames(r["trains"], L, J_SMALL_SEC / r["dt"], rng_small), L)
        starts = list(range(margin, L - margin - CROP + 1, CROP))
        others = [int(rng_extra.randint(margin, L - margin - CROP + 1)) for _ in starts]
        wins["real_vs_shared_offset"] += crop_pairs(score, real, shared, starts)
        wins["real_vs_shared_offset_independent_crop"] += crop_pairs(score, real, shared, starts,
                                                                     others)
        wins["real_vs_rigid_shift"] += crop_pairs(score, real, rigid, starts)
        wins["real_vs_thinned"] += crop_pairs(score, real, thin, starts)
        wins["real_vs_rigid_shift_small_J"] += crop_pairs(score, real, small, starts)
    for k, v in wins.items():
        out[k] = paired_summary(v)
    tw = {"unplanted_twin_vs_rigid_shift": [], "shared_modulation_twin_vs_rigid_shift": [],
          "independent_modulation_twin_vs_rigid_shift": []}
    for t in range(10):
        _, un, shape = lc.twin_pair("fast", None, 0.2, t)
        L, dt = shape["n_frames"], shape["dt"]
        Jf = J_sec / dt
        margin = int(np.ceil(Jf)) + 1
        starts = list(range(margin, L - margin - CROP + 1, CROP))
        rng = np.random.RandomState(seed31("twin-check", label, t, J_sec))
        tw["unplanted_twin_vs_rigid_shift"] += crop_pairs(
            score, raster_of(un, L), raster_of(rigid_frames(un, L, Jf, rng), L), starts)
        rng_mod = np.random.RandomState(seed31("twin-mod", label, t, J_sec))
        for key, is_shared in (("shared_modulation_twin_vs_rigid_shift", True),
                               ("independent_modulation_twin_vs_rigid_shift", False)):
            mod = modulated(un, L, dt, rng_mod, is_shared)
            tw[key] += crop_pairs(score, raster_of(mod, L),
                                  raster_of(rigid_frames(mod, L, Jf, rng_mod), L), starts)
    for k, v in tw.items():
        out[k] = paired_summary(v)
    return out


# -- zero-parameter scorers ---------------------------------------------------------------------

BASELINES = ("count_share", "count_excess", "slow_modulation")
"""Scorers with no parameters, run through the same thresholds and checks as the trained models.

* ``count_share`` — the share of ROIs with an onset within ±2 frames (0.2 s). The detector every
  counting architecture here is built around, with nothing learned.
* ``count_excess`` — that share minus its own 30 s moving mean: a count judged against its local
  background, CoactDetect's idea with no statistics.
* ``slow_modulation`` — the share of ROIs active, averaged over 10 s. A scorer that can only see
  slow co-modulation, never a sub-second event: the probe a murderboard reviewer built
  (2026-09-17), kept as the check of the checks.

Measured beside the trained models so "training bought something" has a comparator that fires."""
BASELINE_WIDEN_FRAMES = 2
BASELINE_BACKGROUND_FRAMES = 301
BASELINE_SLOW_FRAMES = 101


def baseline_model(name):
    import torch
    F = torch.nn.functional

    class Baseline(torch.nn.Module):
        def forward(self, x):                                   # (B, n_roi, T) -> (B, T)
            b, n, t = x.shape
            if name == "slow_modulation":
                share = x.mean(dim=1, keepdim=True)
                k = BASELINE_SLOW_FRAMES
                return F.avg_pool1d(share, k, stride=1, padding=k // 2,
                                    count_include_pad=False).squeeze(1)
            w = BASELINE_WIDEN_FRAMES
            lit = F.max_pool1d(x.reshape(b * n, 1, t), 2 * w + 1, stride=1, padding=w)
            share = lit.reshape(b, n, t).mean(dim=1, keepdim=True)
            if name == "count_share":
                return share.squeeze(1)
            k = BASELINE_BACKGROUND_FRAMES
            bg = F.avg_pool1d(share, k, stride=1, padding=k // 2, count_include_pad=False)
            return (share - bg).squeeze(1)

    if name not in BASELINES:
        raise KeyError(name)
    return Baseline().eval()


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


def fitted_parameters(model):
    """Every parameter outside the dilated head, by name, as fitted — so a width, ratio, gain or
    vote setting quoted from this run is read from its row and not from a re-fit."""
    return {n: p.detach().numpy().astype(float).tolist()
            for n, p in model.named_parameters() if not n.startswith("head.")}


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
        model, n_par, hist = tr.model, tr.n_params, tr.history
        p = min(max(float(tr.threshold), 1e-12), 1 - 1e-12)
        thr, res["oracle_report"] = oracle_threshold(model, held, dt, seed)
        # The bake-off's own operating point, as a logit so it applies to logit scores.
        oracles = {"oracle": thr, "oracle_bakeoff_rule": float(np.log(p / (1 - p)))}
    elif arm == "untrained":
        import torch
        from bugarach.learn.nets import ARCHITECTURES, n_params
        torch.manual_seed(seed)
        model = ARCHITECTURES[name].make().eval()
        n_par, hist = n_params(model), []
        thr, res["oracle_report"] = oracle_threshold(model, held, dt, seed)
        oracles = {"oracle": thr}
    elif arm == "baseline":
        model = baseline_model(name)
        n_par, hist = 0, []
        thr, res["oracle_report"] = oracle_threshold(model, held, dt, seed)
        oracles = {"oracle": thr}
    else:
        if arm == "ssl_sim":
            # The fit block only. Until 2026-09-16 this arm trained on every training-fold
            # recording, the validation block included, so its truth-reading threshold was
            # picked on recordings it had trained on, where the supervised arm's was not.
            fit, _, _ = fit_and_val_seeds(held)
            items = sim_items(fit, dt)
        else:
            items = [r for r in real_recordings() if r["fold"] != held]
        bank = bank_for(items, J_sec, (arm, held))
        model, n_par, hist = ssl_train(name, bank, seed, fb.LR[name])
        res["n_train_recordings"] = len(bank)
        thr, res["oracle_report"] = oracle_threshold(model, held, dt, seed)
        oracles = {"oracle": thr}
    res["n_params"] = int(n_par)
    res["history"] = hist
    res["train_seconds"] = time.time() - t0
    res["centre_widths_sec"] = widths_sec(model, dt)
    res["fitted_parameters"] = fitted_parameters(model)
    res["scores"] = score_held_out(model, held, dt, J_sec, oracles, label)
    # Every arm now, supervised and baselines included: the checks mean something only beside
    # scorers whose answer is known (a count, a slow-modulation average) and models trained with
    # labels.
    res["checks"] = paired_checks(model_scorer(model), held, J_sec, label)
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
        # No seed: nothing is drawn. One row per displacement, because the label-free threshold
        # and the paired checks are drawn at J.
        for name in BASELINES:
            for J in J_SEC:
                tasks.append(("baseline", name, J, 0, held, a.quick))
    from bugarach import provenance
    from bugarach.learn.nets import ARCHITECTURES
    meta = {"tag": TAG, "started": time.strftime("%Y-%m-%dT%H:%M:%S%z"), "quick": a.quick,
            "models": MODELS, "registered": sorted(ARCHITECTURES),
            "registered_but_not_run": sorted(set(ARCHITECTURES) - set(MODELS)),
            "provenance": provenance.stamp(produced_by="tools/tube_self_supervised.py"),
            "thin_share": THIN_SHARE, "j_small_sec": J_SMALL_SEC,
            "modulation": {"period_sec": MOD_PERIOD_SEC, "depth": MOD_DEPTH},
            "baselines": BASELINES,
            "baseline_frames": {"widen": BASELINE_WIDEN_FRAMES,
                                "background": BASELINE_BACKGROUND_FRAMES,
                                "slow": BASELINE_SLOW_FRAMES},
            "n_surrogates_per_label_free_threshold": N_SURR_THRESHOLD,
            "J_sec": J_SEC, "train_seeds": seeds, "folds": folds,
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
            f1 = {k: (None if v["f1"] is None else round(v["f1"], 3))
                  for k, v in r["scores"].items()}
            print(f"[{time.time() - t0:6.0f}s] {i + 1}/{len(tasks)} {r['arm']} {r['model']} "
                  f"J{r['J_sec']:g} s{r['train_seed']} fold{r['held_fold']} {f1}", flush=True)
    meta["seconds"] = time.time() - t0
    (out / "meta.json").write_text(json.dumps(meta, indent=2))
    print("done", out)


if __name__ == "__main__":
    main()
