#!/usr/bin/env python3
"""The detector review for a reader with no background: pictures first, short words.

    python tools/make_plain_detector_review.py --from-review <old review dir> --stages all

Tony, 2026-09-15, on the first detector review (`make_detector_review.py`): he asked for
figures and sixth-grade text, for a reader who knows nothing about the field. What came
back was 11,500 words, figures that showed each algorithm's output but not its steps, a
neural network drawn only as its learned bell curves, a surrogate figure whose two main
panels needed a statistics course, and citations with no links. It also never looked
closely at the thing he found most troubling: on real recordings, some calls look like
nothing and some clear stripes are missed by most of the tools.

This builder answers that. It **reuses the first review's measurements** (its ``_work``
folder, copied to the darkroom as ``measurements/``) and its real-recording figures, and
adds what was missing:

* ``sim``    — every algorithm's steps on one simulated recording, including the chance
  copies each one draws, redrawn for the picture the way the algorithm draws them.
* ``toys``   — the shift-versus-shuffle demonstration, on simulated cells and on the lab's
  own evenly firing cells (the first review's Figure 2 numbers).
* ``tube``   — the neural network's stages, as signals, from one trained copy.
* ``real``   — close-ups of real recordings where the eye and the detectors disagree,
  and a count of how often that happens in the eight recordings shown.
* ``figures``— every figure as SVG, flattened to PNG beside it.
* ``page``   — the HTML page.

**Real treatment data goes to the darkroom only** (FOUNDATIONS §5): the close-ups, the
counts and every sentence describing them. The template carries ``{{PROSE:key}}`` for
those sentences; they live in ``real_prose.json`` next to the page.

Figures are drawn as SVG by hand rather than through Bokeh, because most of them are
diagrams with data inside — numbered steps, arrows, a chance histogram beside the count it
judges — and a plotting library fights that layout. The rules in CLAUDE.md still hold:
nothing is drawn on a raster, markers above a raster point down, time axes are
minutes-friendly, every figure is numbered and every count carries its unit.
"""
from __future__ import annotations

import argparse
import html as _html
import json
import math
import re
import shutil
import sys
import tempfile
import warnings
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))

FOLDER_NAME = "2026-09-15-detector-review-plain"
TEMPLATE = Path(__file__).resolve().parent / "plain_detector_review_template.html"
LEARNED_TEMPLATE = Path(__file__).resolve().parent / "plain_learned_template.html"

SEED, REGIME = 3, "baseline_quiet"
EVENT_T = 491.9                      # the planted event in the first review's view A
ZOOM_A = (EVENT_T - 30.0, EVENT_T + 30.0)
ZOOM_B = (1350.0, 1410.0)            # inside the busy stretch, nothing planted
CODED = ("rate", "coact", "loco", "sce", "cicada", "sync")
NAMES = {"rate": "rate+context", "coact": "CoactDetect", "loco": "LoCo",
         "sce": "binned SCE", "cicada": "locust", "sync": "SPIKE-synch",
         "tube": "tube", "tube_guard": "tube-guard", "tube_ratio": "tube-ratio",
         "tube_ratio_guard": "tube-ratio-guard"}
COLORS = {"rate": "#0B5FFF", "coact": "#00A396", "loco": "#7A00E6", "sce": "#1E9E1E",
          "cicada": "#E6008E", "sync": "#FF5A1F", "tube": "#8B1A1A", "tube_guard": "#D0453A",
          "tube_ratio": "#E88A1A", "tube_ratio_guard": "#E8B83A"}
LEARNED4 = ("tube", "tube_guard", "tube_ratio", "tube_ratio_guard")


def put(work: Path, key: str, value) -> None:
    f = work / "plain.json"
    d = json.loads(f.read_text()) if f.exists() else {}
    d[key] = value
    f.write_text(json.dumps(d, default=_jsonable))


def _jsonable(o):
    if isinstance(o, np.ndarray):
        return [None if (isinstance(v, float) and not math.isfinite(v)) else v
                for v in o.tolist()]
    if isinstance(o, (np.floating,)):
        return float(o) if np.isfinite(o) else None
    if isinstance(o, (np.integer,)):
        return int(o)
    raise TypeError(type(o))


def _clip(t, y, win, pad=0.0):
    t, y = np.asarray(t, float), np.asarray(y, float)
    k = (t >= win[0] - pad) & (t <= win[1] + pad)
    return np.round(t[k], 3), np.where(np.isfinite(y[k]), np.round(y[k], 4), np.nan)


def _trains_in(trains, win):
    return [np.round(v[(v >= win[0]) & (v <= win[1])], 3) for v in trains]


def _calls_in(on, wd, win, pad=3.0):
    on, wd = np.asarray(on, float), np.asarray(wd, float)
    wd = np.where(np.isfinite(wd), wd, 0.0)
    k = (on + wd >= win[0] - pad) & (on <= win[1] + pad)
    return [[round(float(a), 2), round(float(b), 2)] for a, b in zip(on[k], wd[k])]


def _shift(v, lo, hi, rng):
    """Slide one cell's events by a random amount inside [lo, hi), wrapping at the end."""
    L = hi - lo
    return lo + np.mod(v - lo + rng.uniform(0, L), L)


# ----------------------------------------------------------------------- stage: sim
def stage_sim(work: Path) -> None:
    """Every algorithm's steps on the first review's simulated recording (seed 3)."""
    from make_detector_review import _bench, coded_results
    from make_mechanism_figure import coact_bar

    s, gt, ext = _bench(SEED)
    trains = [np.asarray(v, float) for v in s.streams["events"].t50rise]
    n = len(trains)
    res, params = coded_results(s, ext)
    ev = min(gt.events, key=lambda e: abs(e.time - EVENT_T))
    hot = gt.params.get("hot_window")
    out = dict(n_roi=n, ext=list(ext), event=dict(time=ev.time, n_part=ev.n_part, rois=list(ev.rois),
                                                  frac=ev.frac),
               hot=list(hot) if hot else None,
               planted=[[e.time, e.n_part] for e in gt.events],
               decoys=[[e.time, e.n_part] for e in gt.distractors],
               settings={d: dict(params[d]) for d in CODED})
    out["full_trains"] = [np.round(v, 2) for v in trains]
    rng = np.random.RandomState(20260915)
    for key, win in (("A", ZOOM_A), ("B", ZOOM_B)):
        W = dict(win=list(win), trains=_trains_in(trains, win))
        for d in CODED:
            r = res[d]
            W[f"{d}_calls"] = _calls_in(*[np.asarray(a, float) for a in r.events[:2]], win)
        # rate+context: summed rate, the 60 s average, the bar
        r = res["rate"]
        t, y = _clip(r.t, r.y, win)
        _, ref = _clip(r.t, r.extra["ref"], win)
        W["rate"] = dict(t=t, y=y, ref=ref, bar=ref + params["rate"]["excess_threshold_hz"])
        # CoactDetect: count per 2 s bin, the chance average, the bar (where tested)
        ctr, obs, nm, bar = coact_bar(res["coact"].result)
        c_t, c_obs = _clip(ctr, obs, win, pad=1.0)
        _, c_nm = _clip(ctr, nm, win, pad=1.0)
        _, c_bar = _clip(ctr, bar, win, pad=1.0)
        W["coact"] = dict(t=c_t, y=c_obs, mean=c_nm, bar=c_bar)
        # LoCo: count per 1 s bin and its stepped bar
        r = res["loco"]
        t, y = _clip(r.t, r.y, win, pad=1.0)
        _, thr = _clip(r.t, r.extra["threshold"], win, pad=1.0)
        W["loco"] = dict(t=t, y=y, bar=thr)
        # binned SCE: count per 10 s bin, one bar
        r = res["sce"]
        t, y = _clip(r.t, r.y, win, pad=10.0)
        _, thr = _clip(r.t, r.extra["threshold"], win, pad=10.0)
        W["sce"] = dict(t=t, y=y, bar=thr)
        # locust: cells switched on per frame, one bar
        r = res["cicada"]
        t, y = _clip(r.t, r.y, win)
        _, thr = _clip(r.t, r.extra["threshold"], win)
        W["cicada"] = dict(t=t, y=y, bar=thr)
        # SPIKE-synch: each event's score and the frame score
        raw = res["sync"].result
        px, py = _clip(raw.profile_x, raw.profile_y, win)
        cx, cy = _clip(raw.Cx, raw.Cy, win)
        W["sync"] = dict(px=px, py=py, cx=cx, cy=cy, bar=float(params["sync"]["C_threshold"]))
        out[key] = W

    # ---- the chance copies, redrawn for the picture ---------------------------------
    # Each algorithm draws its own copies inside its own code, with its own random numbers,
    # and does not hand them back. These are drawn the same way for the picture; the bar
    # drawn beside them is the algorithm's own, read from its output.
    A = out["A"]
    # CoactDetect: the 2 s bin holding the event, 100 copies of the 60 s around it
    k = int(np.nanargmax(np.where(np.abs(np.asarray(A["coact"]["t"]) - EVENT_T) < 3,
                                  np.asarray(A["coact"]["y"], float), -1)))
    c0 = float(A["coact"]["t"][k])
    lo, hi = c0 - 30.0, c0 + 30.0
    # THE EVENTS ARE NUMBERED, not drawn as bare ticks (Tony, 2026-09-16: "humans can't see
    # the pattern shift without cues"; the lab's older MATLAB teaching slide numbered them).
    # Each event carries its position in its own cell's sequence, so a slid row can be read as
    # the same row — including where it wrapped, which is exactly what a bare tick hides.
    # Only cells with an event in this minute are drawn, so the numbers stay readable; the
    # counts, the bar and the histogram are over every cell, as the detector computes them.
    ctx = [np.round(v[(v >= lo) & (v < hi)], 2) for v in trains]
    rows = [i for i, v in enumerate(ctx) if v.size]
    counts, examples = [], []
    for i in range(100):
        offs = [rng.uniform(0, hi - lo) for _ in trains]
        cp = [lo + np.mod(v - lo + o, hi - lo) for v, o in zip(ctx, offs)]
        counts.append(sum(1 for w in cp if np.any(np.abs(w - c0) < 1.0)))
        if i < 3:
            examples.append(dict(
                count=counts[-1], shifts=[round(float(offs[j]), 1) for j in rows],
                numbered=[[[round(float(t), 2), n + 1] for n, t in enumerate(cp[j])] for j in rows]))
    out["chance_coact"] = dict(bin_center=c0, observed=A["coact"]["y"][k], counts=counts,
                               mean=A["coact"]["mean"][k], bar=A["coact"]["bar"][k],
                               context=[lo, hi], examples=examples, n_rows_drawn=len(rows),
                               observed_numbered=[[[round(float(t), 2), n + 1]
                                                   for n, t in enumerate(ctx[j])] for j in rows],
                               observed_trains=[ctx[j] for j in rows])
    # a busy-stretch bin for CoactDetect too
    B = out["B"]
    yb = np.asarray(B["coact"]["y"], float)
    kb = int(np.nanargmax(np.where(np.isfinite(np.asarray(B["coact"]["bar"], float)), yb, -1)))
    cb = float(B["coact"]["t"][kb])
    lo, hi = cb - 30.0, cb + 30.0
    counts = []
    for _ in range(100):
        counts.append(sum(1 for v in trains
                          if np.any(np.abs(_shift(v[(v >= lo) & (v < hi)], lo, hi, rng) - cb) < 1.0)))
    out["chance_coact_B"] = dict(bin_center=cb, observed=float(yb[kb]), counts=counts,
                                 mean=B["coact"]["mean"][kb], bar=B["coact"]["bar"][kb])

    # LoCo: 1 s bins in the minute before and the minute after, 100 copies each
    def loco_side(lo, hi):
        edges = np.arange(lo, hi + 1e-9, 1.0)
        pooled = []
        for _ in range(100):
            occ = np.zeros(len(edges) - 1)
            for v in trains:
                w = _shift(v[(v >= lo) & (v < hi)], lo, hi, rng)
                if w.size:
                    occ += np.histogram(w, edges)[0] > 0
            pooled.append(occ)
        return np.concatenate(pooled)
    before, after = loco_side(EVENT_T - 60, EVENT_T), loco_side(EVENT_T, EVENT_T + 60)
    ia = int(np.argmin(np.abs(np.asarray(A["loco"]["t"]) - EVENT_T)))
    lo_obs = float(np.nanmax(np.asarray(A["loco"]["y"], float)[max(0, ia - 2):ia + 3]))
    out["chance_loco"] = dict(observed=lo_obs,
                              before=np.bincount(before.astype(int), minlength=12).tolist(),
                              after=np.bincount(after.astype(int), minlength=12).tolist(),
                              p999_before=float(np.percentile(before, 99.9)),
                              p999_after=float(np.percentile(after, 99.9)),
                              bar=float(np.nanmax(np.asarray(A["loco"]["bar"], float)[max(0, ia - 2):ia + 3])))
    # binned SCE: 10 s bins over the whole recording, 200 copies pooled
    edges = np.arange(ext[0], ext[1] + 1e-9, 10.0)
    hist = np.zeros(40, int)
    for _ in range(200):
        occ = np.zeros(len(edges) - 1)
        for v in trains:
            occ += np.histogram(_shift(v, ext[0], ext[1], rng), edges)[0] > 0
        hist += np.bincount(occ.astype(int), minlength=40)[:40]
    si = int(np.argmin(np.abs(np.asarray(A["sce"]["t"]) - EVENT_T)))
    out["chance_sce"] = dict(hist=hist.tolist(), n_bins=int(hist.sum()),
                             observed=float(np.asarray(A["sce"]["y"], float)[si]),
                             bar=float(np.nanmax(np.asarray(A["sce"]["bar"], float))))
    # locust: frames of 0.1 s, each event on for 1 s, 100 copies pooled
    fr = 0.1
    nf = int(round((ext[1] - ext[0]) / fr))
    hist = np.zeros(40, np.int64)
    for _ in range(100):
        on = np.zeros(nf, int)
        for v in trains:
            m = np.zeros(nf + 10, bool)
            idx = np.floor((_shift(v, ext[0], ext[1], rng) - ext[0]) / fr).astype(int)
            for j in range(10):
                m[np.clip(idx + j, 0, nf + 9)] = True
            on += m[:nf]
        hist += np.bincount(on, minlength=40)[:40]
    ci = int(np.argmin(np.abs(np.asarray(A["cicada"]["t"]) - EVENT_T)))
    out["chance_cicada"] = dict(hist=hist.tolist(), n_frames=int(hist.sum()),
                                observed=float(np.nanmax(np.asarray(A["cicada"]["y"], float)[max(0, ci - 20):ci + 20])),
                                bar=float(np.nanmax(np.asarray(A["cicada"]["bar"], float))))
    put(work, "sim", out)
    print("  sim: ok", {k: out[k]["observed"] for k in out if k.startswith("chance")})


# ----------------------------------------------------------------------- stage: toys
def stage_toys(work: Path) -> None:
    """Shift against shuffle on six simulated cells, in the two ways a shuffle goes wrong."""
    rng = np.random.RandomState(11)
    L = 20.0

    def counter(b):
        return lambda trs: sum(1 for v in trs if np.any((v >= b[0]) & (v < b[1])))

    # Bursty cells: every event comes in a tight burst of four. 4 cells burst together.
    starts = [9.3, 9.2, 9.4, 9.25, 3.5, 15.6]
    bursty = [np.round(a + np.arange(4) * 0.22, 2) for a in starts]
    # Evenly firing cells: one event every 2.5 s, each cell on its own random beat, so
    # nothing is coordinated. The 2 s bin where most of them happen to fall is tested.
    phases = np.random.RandomState(5).uniform(0, 2.5, 6)
    even = [np.round(np.mod(p + np.arange(8) * 2.5, L), 2) for p in phases]
    grid = np.arange(0.0, L - 2.0 + 1e-9, 0.1)
    best = max(grid, key=lambda b: (counter((b, b + 2.0))(even), -abs(b - 9.0)))
    bins = {"bursty": (9.0, 11.0), "even": (round(float(best), 1), round(float(best) + 2.0, 1))}
    out = {}
    for name, trs in (("bursty", bursty), ("even", even)):
        count = counter(bins[name])
        n = sum(len(v) for v in trs)
        sh, sc = [], []
        ex_shift = ex_shuffle = None
        for i in range(5000):
            a = [np.sort(np.mod(v + rng.uniform(0, L), L)) for v in trs]
            b = [np.sort(rng.uniform(0, L, len(v))) for v in trs]
            if i == 0:
                ex_shift, ex_shuffle = a, b
            sh.append(count(a))
            sc.append(count(b))
        obs = count(trs)
        out[name] = dict(observed=obs, trains=trs, shift_example=ex_shift,
                         shuffle_example=ex_shuffle,
                         shift_hist=np.bincount(sh, minlength=7)[:7].tolist(),
                         shuffle_hist=np.bincount(sc, minlength=7)[:7].tolist(),
                         p_shift=float(np.mean(np.asarray(sh) >= obs)),
                         p_shuffle=float(np.mean(np.asarray(sc) >= obs)),
                         mean_shift=float(np.mean(sh)), mean_shuffle=float(np.mean(sc)),
                         n_events=n, bin=list(bins[name]))
    out["length"] = L
    # ---- the numbered teaching example for the shifted-copy steps --------------------
    # Quiet cells will not do here: over one minute of the bench recording almost every cell
    # has a single event, so every number is "1" and nothing can be followed when a row
    # slides. Six busier simulated cells, numbered in their own firing order, is the form the
    # lab's older MATLAB slide used, and the form Tony asked for back (2026-09-16).
    SL, PIECE = 60.0, (29.0, 31.0)
    r2 = np.random.RandomState(7)
    cells = []
    for i in range(6):
        v = np.sort(r2.uniform(0, SL, 4))
        while np.min(np.diff(v)) < 3.0:
            v = np.sort(r2.uniform(0, SL, 4))
        cells.append(v)
    for i in range(4):                       # four of the six act together in the test bin
        cells[i][int(np.argmin(np.abs(cells[i] - 30.0)))] = 30.0 + r2.uniform(-0.3, 0.3)
        cells[i] = np.sort(np.round(cells[i], 2))
    cells = [np.round(v, 2) for v in cells]

    def in_bin(trs):
        return sum(1 for v in trs if np.any((np.asarray(v) >= PIECE[0]) & (np.asarray(v) < PIECE[1])))

    counts, examples = [], []
    for i in range(200):
        offs = [r2.uniform(0, SL) for _ in cells]
        cp = [np.mod(v + o, SL) for v, o in zip(cells, offs)]
        counts.append(in_bin(cp))
        if i < 3:
            examples.append(dict(
                count=counts[-1], shifts=[round(float(o), 1) for o in offs],
                numbered=[[[round(float(t), 2), n + 1] for n, t in enumerate(v)] for v in cp]))
    obs = in_bin(cells)
    out["steps"] = dict(
        length=SL, bin=list(PIECE), observed=obs, n_copies=len(counts),
        numbered=[[[round(float(t), 2), n + 1] for n, t in enumerate(v)] for v in cells],
        examples=examples, hist=np.bincount(counts, minlength=7)[:7].tolist(),
        bar=float(np.percentile(counts, 99)),
        share_at_least=float(np.mean(np.asarray(counts) >= obs)))
    put(work, "toys", out)
    print("  toys:", {k: (v["p_shift"], v["p_shuffle"]) for k, v in out.items()
                      if isinstance(v, dict) and "p_shift" in v},
          "| steps:", out["steps"]["observed"], "of 6 observed,",
          f"{out['steps']['share_at_least']:.1%} of copies reach it")


# ----------------------------------------------------------------------- stage: tube
def stage_tube(work: Path) -> None:
    """One trained tube network, and the signal after each of its stages."""
    import torch
    from make_detector_review import _bench, _train_one
    from bugarach.learn.checkpoint import load
    from bugarach.learn.encode import encode

    mdir = work / "models"
    mdir.mkdir(exist_ok=True)
    if not (mdir / "tube.json").exists():
        _, meta = _train_one(("tube", str(mdir)))
        (mdir / "tube_meta.json").write_text(json.dumps(meta))
    trained = load(mdir / "tube.json")
    net = trained.model
    s, gt, ext = _bench(SEED)
    dt = float(s.require_dt("the network figure"))
    enc = encode(s, dt=dt)
    x = torch.from_numpy(enc.raster).unsqueeze(0)
    t = enc.t0 + np.arange(enc.n_frame) * dt
    with torch.no_grad():
        kmin = int(torch.exp(net.log_center.detach()).min().clamp(1, net.k))
        pooled = torch.nn.functional.max_pool1d(
            x.reshape(-1, 1, enc.n_frame), kernel_size=2 * kmin + 1, stride=1,
            padding=kmin).reshape(1, -1, enc.n_frame)
        bright = pooled.sum(dim=1, keepdim=True) / enc.n_roi
        resp = torch.nn.functional.conv1d(bright, net._kernels("cpu"), padding=net.k)
        score = torch.sigmoid(net(x)).squeeze(0).numpy()
        c = torch.exp(net.log_center.detach()).clamp(0.5, net.k / 2).numpy()
        ck = net._kernels("cpu").squeeze(1).numpy()
    calls = trained.predict(s)[0]
    n_params = sum(p.numel() for p in net.parameters())
    head = sum(p.numel() for p in net.head.parameters())
    out = dict(threshold=float(trained.threshold), widen_s=round((2 * kmin + 1) * dt, 2),
               n_params=int(n_params), n_head=int(head), dt=dt,
               centre_s=[round(float(v * dt), 2) for v in c],
               kernel_example=dict(lag_s=np.round(np.arange(-net.k, net.k + 1) * dt, 2),
                                   w=np.round(ck[int(np.argmin(c))], 5)))
    for key, win in (("A", ZOOM_A), ("B", ZOOM_B)):
        m = (t >= win[0]) & (t <= win[1])
        rows = np.flatnonzero(enc.raster[:, m].any(axis=1))
        out[key] = dict(win=list(win), t=np.round(t[m], 2),
                        onsets=[np.round(t[m][np.flatnonzero(enc.raster[i, m])], 2) for i in range(enc.n_roi)],
                        widened=[np.round(t[m][np.flatnonzero(pooled[0, i, m].numpy())], 2) for i in range(enc.n_roi)],
                        bright=np.round(bright[0, 0, m].numpy() * 100, 2),
                        resp=[np.round(resp[0, j, m].numpy() * 100, 3) for j in range(resp.shape[1])],
                        score=np.round(score[m], 4),
                        calls=_calls_in(calls.onset_sec, calls.width_sec, win))
    put(work, "tube", out)
    print("  tube: threshold", out["threshold"], "params", n_params, "head", head)


# ----------------------------------------------------------------------- stage: real
#: A stripe is what a person sees on a raster: at least this share of a recording's cells
#: starting an event within STRIPE_S seconds of each other (and never fewer than MIN_CELLS).
STRIPE_FRAC, STRIPE_S, MIN_CELLS = 0.25, 1.0, 5
#: A call "has no stripe under it" when no STRIPE_S-second stretch inside it, or within
#: STRIPE_S of its edges, holds more than WEAK_CELLS cells starting an event.
WEAK_CELLS = 3
ALL10 = CODED + LEARNED4


def _peak_cells(trains, t0, t1, w=STRIPE_S):
    rows = [(float(a), i) for i, v in enumerate(trains) for a in v if t0 - w <= a <= t1 + w]
    rows.sort()
    best = 0
    for j, (a, _) in enumerate(rows):
        best = max(best, len({i for b, i in rows[j:] if b < a + w}))
    return best


#: ...and it must STAND OUT from its own surroundings: at least STANDOUT times the count
#: that the busiest 5% of 1-second stretches reach in the two minutes around it (the
#: stripe's own few seconds left out). Without this, a busy stretch is full of "stripes"
#: that are only chance, and nobody looking at the raster would point at them.
STANDOUT, AROUND_S = 2.0, 60.0


def _stripes(trains, n):
    need = max(MIN_CELLS, int(math.ceil(STRIPE_FRAC * n)))
    allon = np.sort(np.concatenate([v[np.isfinite(v)] for v in trains if len(v)]))
    if not allon.size:
        return need, []
    grid = np.arange(allon[0] - AROUND_S, allon[-1] + AROUND_S, 0.5)
    gc = np.zeros(grid.size)
    for v in trains:
        v = np.sort(v[np.isfinite(v)])
        if v.size:
            i0 = np.searchsorted(v, grid)
            i1 = np.searchsorted(v, grid + STRIPE_S)
            gc += i1 > i0
    found = []
    for a in allon:
        k = sum(1 for v in trains if np.any((v >= a) & (v < a + STRIPE_S)))
        if k < need:
            continue
        m = (np.abs(grid - a) <= AROUND_S) & (np.abs(grid - a) > 3.0)
        local = float(np.percentile(gc[m], 95)) if m.any() else 0.0
        if k >= STANDOUT * local:
            if found and a - found[-1][0] < 5.0:
                if k > found[-1][1]:
                    found[-1] = (found[-1][0], k, a)
                continue
            found.append((a, k, a))
    return need, [(a, k) for _, k, a in found]


def stage_real(work: Path, review: Path) -> None:
    """Where the eye and the detectors disagree, on the first review's eight recordings."""
    from bugarach import dataset
    from bugarach.io import load_folder
    from make_group_raster_summary import _anchor_of

    if review is None:
        raise SystemExit("--from-review is required for the real stage")
    det = json.loads((review / "measurements" / "real_detections.json").read_text())
    rec = {}
    for label, role in (("TTX", "ttx"), ("senktide", "senktide")):
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            slices = {s.slice_id: s for s in load_folder(dataset.current(role))}
        for key, d in det.items():
            lab, sid = key.split("|")
            if lab != label:
                continue
            s = slices[sid]
            g = s.meta.get("group_id")
            anchor = float(_anchor_of(s))
            for stream in ("fast", "slow"):
                trains = [np.asarray(v, float) for v in s.streams[stream].t50rise]
                n = len(trains)
                need, st = _stripes(trains, n)
                calls = {dd: [(r["onset"], r["width"]) for r in d["rows"]
                              if r["detector"] == dd and r["stream"] == stream] for dd in ALL10}
                stripes = []
                for a, k in st:
                    stripes.append(dict(
                        t=a, cells=k, in_window=any(w0 <= a <= w1 for _, w0, w1 in d["windows"]),
                        called_by=[dd for dd in ALL10 if any(
                            on - 2.5 <= a + STRIPE_S and on + max(wd, 0.0) + 2.5 >= a
                            for on, wd in calls[dd])]))
                weak = {dd: [(on, wd, _peak_cells(trains, on, on + max(wd, 0.0))) for on, wd in calls[dd]]
                        for dd in ALL10}
                rec[f"{label}|{g}|{stream}"] = dict(
                    regions=[[r_.name, float(r_.start_sec), float(r_.end_sec)] for r_ in s.regions],
                    label=label, group=g, stream=stream, slice=sid, n_roi=n, anchor=anchor,
                    need=need, windows=d["windows"], stripes=stripes, weak=weak, calls=calls,
                    trains=trains)
    # ---- the tallies ---------------------------------------------------------------
    tally = {dd: dict(stripes=0, called=0, stripes_in=0, called_in=0, calls=0, weak=0)
             for dd in ALL10}
    n_stripes = n_in = n_few = n_few_out = 0
    for r in rec.values():
        for sp in r["stripes"]:
            n_stripes += 1
            n_in += sp["in_window"]
            few = len(sp["called_by"]) <= 3
            n_few += few
            n_few_out += few and not sp["in_window"]
            for dd in ALL10:
                tally[dd]["stripes"] += 1
                tally[dd]["called"] += dd in sp["called_by"]
                if sp["in_window"]:
                    tally[dd]["stripes_in"] += 1
                    tally[dd]["called_in"] += dd in sp["called_by"]
        for dd in ALL10:
            tally[dd]["calls"] += len(r["weak"][dd])
            tally[dd]["weak"] += sum(1 for *_, p in r["weak"][dd] if p <= WEAK_CELLS)

    # ---- the close-ups ---------------------------------------------------------------
    def closeup(k, t0, t1, why):
        r = rec[k]
        win = (t0, t1)
        order = np.argsort([len(v) for v in r["trains"]], kind="stable")   # busiest on top
        return dict(key=k, label=r["label"], group=r["group"], stream=r["stream"], n_roi=r["n_roi"],
                    regions=r["regions"],
                    anchor=r["anchor"], win=list(win), why=why,
                    windows=[[w0, w1] for _, w0, w1 in r["windows"]],
                    trains=[_trains_in([r["trains"][i]], win)[0] for i in order],
                    calls={dd: _calls_in(*zip(*r["calls"][dd]), win, pad=0.0) if r["calls"][dd] else []
                           for dd in ALL10},
                    stripes=[sp for sp in r["stripes"] if t0 <= sp["t"] <= t1],
                    weak={dd: [[round(on, 2), round(wd, 2), p] for on, wd, p in r["weak"][dd]
                               if t0 - 3 <= on <= t1 and p <= WEAK_CELLS] for dd in ALL10})

    def best_outside():
        cands = [(len(sp["called_by"]), -sp["cells"], k, sp) for k, r in rec.items()
                 for sp in r["stripes"] if not sp["in_window"] and len(sp["called_by"]) <= 3]
        _, _, k, sp = min(cands, key=lambda c: (c[1], c[0]))     # the biggest stripe
        return k, sp

    def best_weak():
        cands = []
        for k, r in rec.items():
            pts = [(on, dd) for dd in ALL10 for on, wd, p in r["weak"][dd]
                   if p <= WEAK_CELLS and any(w0 <= on <= w1 for _, w0, w1 in r["windows"])]
            for on, _ in pts:
                inside = {dd for o, dd in pts if on - 10 <= o <= on + 50}
                cands.append((len(inside), k, on - 10))
        n_, k, t0 = max(cands, key=lambda c: c[0])
        return k, t0

    def best_orienting(span=600.0):
        """The stretch a newcomer should see first: the most clear stripes in ten minutes,
        inside one analysis window of one recording, so nothing has to be explained yet."""
        best = None
        for k, r in rec.items():
            for _, w0, w1 in r["windows"]:
                ins = [sp for sp in r["stripes"] if w0 <= sp["t"] <= w1]
                for sp in ins:
                    t0 = min(max(sp["t"] - span / 2, w0), max(w1 - span, w0))
                    n = sum(1 for x in ins if t0 <= x["t"] <= t0 + span)
                    if best is None or (n, r["n_roi"]) > (best[0], rec[best[1]]["n_roi"]):
                        best = (n, k, t0)
        return best[1], best[2]

    ko, spo = best_outside()
    r = rec[ko]
    wend = max((w1 for _, w0, w1 in r["windows"] if w1 <= spo["t"]), default=spo["t"] - 60)
    close = {"outside": closeup(ko, min(wend - 60, spo["t"] - 90), spo["t"] + 90, "outside")}
    ko_, t0 = best_orienting()
    close["orient"] = closeup(ko_, t0, t0 + 600.0, "orient")
    kw, t0 = best_weak()
    close["weak"] = closeup(kw, t0, t0 + 60, "weak")
    # the first review's Figure 1A: the recording where the six disagree most
    pa = json.loads((review / "measurements" / "numbers.json").read_text())["prob_a"]
    kp = f"{pa['drug']}|{pa['group']}|fast"
    a = rec[kp]["anchor"]
    close["problem"] = closeup(kp, a + 60 * pa["minutes"][0], a + 60 * pa["minutes"][1], "problem")
    # ...and its busiest 90 s inside a marked window: where locust calls most
    rp = rec[kp]
    lc = np.array([on for on, _ in rp["calls"]["cicada"]
                   if any(w0 <= on <= w1 for _, w0, w1 in rp["windows"])])
    t0 = max(lc, key=lambda s_: int(np.sum((lc >= s_) & (lc < s_ + 90)))) if lc.size else a
    close["busy"] = closeup(kp, float(t0), float(t0) + 90, "busy")
    c = close["busy"]
    put(work, "busy_counts", {dd: sum(1 for on, _ in c["calls"][dd] if t0 <= on <= t0 + 90) for dd in ALL10})
    # Whole recordings, for the overview figures. The first review's four PNGs are not reused
    # any more: they carry a lane per learned model, and those left this document (Tony,
    # 2026-09-16, "cut out the learned models for now"). Drawing them here also brings them
    # under the raster rules the rest of the figures follow.
    overview = {}
    for k, r in rec.items():
        a = r["anchor"]
        lo = min([float(np.min(v)) for v in r["trains"] if len(v)] + [a])
        hi = max([float(np.max(v)) for v in r["trains"] if len(v)] + [a])
        overview[k] = dict(
            label=r["label"], group=r["group"], stream=r["stream"], n_roi=r["n_roi"], anchor=a,
            ext=[lo, hi], regions=r["regions"], windows=[[w0, w1] for _, w0, w1 in r["windows"]],
            trains=[np.round(v, 1) for v in _by_activity(r["trains"])],
            calls={dd: [[round(on, 1), round(max(wd, 0.0), 1)] for on, wd in r["calls"][dd]]
                   for dd in CODED},
            in_window={dd: sum(1 for on, _ in r["calls"][dd]
                               if any(w0 <= on <= w1 for _, w0, w1 in r["windows"]))
                       for dd in CODED},
            stripes=[dict(t=sp["t"], cells=sp["cells"]) for sp in r["stripes"]])
    out = dict(n_stripes=n_stripes, n_in=n_in, n_few=n_few, n_few_out=n_few_out, tally=tally,
               close=close, stripe_frac=STRIPE_FRAC, stripe_s=STRIPE_S, weak_cells=WEAK_CELLS,
               n_recordings=len({v["slice"] for v in rec.values()}), overview=overview)
    put(work, "real", out)
    print(f"  real: {n_stripes} stripes, {n_in} inside windows, {n_few} called by <=3 of 10, "
          f"{n_few_out} of those outside")
    for k, v in close.items():
        print("   close-up", k, v["key"], [round((x - v["anchor"]) / 60, 2) for x in v["win"]])


# ----------------------------------------------------------------------- stage: count
# "Why not just count cells in a bin?" Tony, 2026-09-16: more than x events in a bin is a
# coordinated event — "that's what everyone else does" [not true, he adds, but Herbison and
# Moore do it]. The answer is a measurement, not an argument: the rule is run on the same
# simulated recordings and graded the same way as the six programs, then asked how much chance
# it lets through on the lab's own untreated recordings and at the published rates.
#
# The counting is binned SCE's own `_coactivity` (different cells with an event in a bin), so
# the rule differs from binned SCE in exactly one thing: its bar is a fixed number instead of a
# percentile of shifted copies.
COUNT_BINS = (2.0, 10.0)            # CoactDetect's bin, and binned SCE's
COUNT_XS = tuple(range(2, 13))
FIG_BIN = 2.0                       # the bin the figures draw
REAL_XS = tuple(range(2, 31))
CHANCE_DRAWS = 20
HERB_WIN = 10.0                     # Han et al. 2023, Methods: each peak within 10 s of the previous
HERB_KS = (2, 3, 4, 5, 6, 8)        # 2 is the published value
#: Events per cell per hour. 13.4 is the 2026 paper's own rate, so its chance curve is the one the
#: dashed "reported" line may be read against; 7.0 is the slowest rate the slice papers report (Han
#: et al. 2023, gonadectomized males). A curve at any other rate beside that line would invite a
#: comparison that is not like for like — the first draft drew 7.0/11.3/14.7 and did exactly that.
PUB_RATES = (7.0, 13.4)
PUB_CELLS = tuple(range(4, 31))
PUB_HOURS = 100.0
#: Eddleston, Morris & Herbison 2026, Results: 13.4 events/cell/h, 2.6 mSEs/cell/h, 3.7 cells
#: (29.1%) per mSE, 8-29 cells in view. 3.7 / 0.291 puts the average field near 13 cells. The one
#: paper of the set whose reported numbers are consistent with the "divide by cells" reading of
#: "per cell, per hour" that Morris & Herbison 2023 use when they convert 0.66/cell/h to a field rate.
EDDLESTON = dict(rate=13.4, mse=2.6, cells_per=3.7, share=29.1, field_lo=8, field_hi=29, field=13)


def _count_rule_calls(obs, t_lo, bw, x):
    """Bins reaching x cells; bins that touch make one call spanning all of them."""
    on = np.flatnonzero(np.asarray(obs) >= x)
    if on.size == 0:
        return np.empty(0), np.empty(0)
    br = np.flatnonzero(np.diff(on) != 1)
    s, e = np.r_[on[0], on[br + 1]], np.r_[on[br], on[-1]]
    return t_lo + s * bw, (e - s + 1) * bw


def _herbison_calls(trains, k=2, win=HERB_WIN):
    """The published slice rule, as Han et al. 2023 state it: events from at least k cells, each
    peaking within `win` seconds of the previous peak already in the event. Returns onsets,
    spans and how many different cells each event holds."""
    parts = [np.asarray(v, float) for v in trains]
    t = np.concatenate(parts) if parts else np.empty(0)
    if t.size == 0:
        return np.empty(0), np.empty(0), np.empty(0, int)
    c = np.concatenate([np.full(v.size, i) for i, v in enumerate(parts)])
    o = np.argsort(t, kind="stable")
    t, c = t[o], c[o]
    starts = np.r_[0, np.flatnonzero(np.diff(t) > win) + 1]
    ends = np.r_[starts[1:], t.size]
    on, wd, size = [], [], []
    for a, b in zip(starts, ends):
        n = np.unique(c[a:b]).size
        if n >= k:
            on.append(t[a])
            wd.append(t[b - 1] - t[a])
            size.append(n)
    return np.array(on), np.array(wd), np.array(size, int)


def _near_share(on, wd, block, tol):
    """1-second moments of an empty block that sit within the scoring tolerance of a call.

    The unit the first review's busy-stretch chance line used. It judges a point call and a
    long call alike, which a count of calls per minute does not: a rule that calls one span
    across the whole block makes ONE call there, and a per-minute count reads that as quiet."""
    grid = np.arange(block[0], block[1], 1.0)
    on, wd = np.asarray(on, float), np.asarray(wd, float)
    if on.size == 0:
        return 0, int(grid.size)
    hi = on + np.where(np.isfinite(wd), wd, 0.0)
    near = np.zeros(grid.size, bool)
    for a, b in zip(on, hi):
        near |= (grid >= a - tol) & (grid <= b + tol)
    return int(near.sum()), int(grid.size)


def _count_bench_one(job):
    regime, seed = job
    from bugarach import bench
    from bugarach.detectors.rate import recording_extent, stream_trains
    from bugarach.detectors.sce import _coactivity
    from bugarach.score import TOL_SEC, score_detections
    s, gt = bench.make_recording(regime, seed)
    block = gt.params["hot_window"]
    ext = recording_extent(s)
    trains = stream_trains(s.streams[bench.STREAM], ext)
    out = {}

    def add(name, on, wd):
        out[name] = (score_detections(gt, on, widths=wd), _near_share(on, wd, block, TOL_SEC))
    for d in CODED:
        r = bench.run_detector(d, s)
        on, wd = (r.onset_sec, r.width_sec) if hasattr(r, "onset_sec") else (r.locs, r.widths)
        if d == "sce":       # a binned call spans its bin (the scoring figure's right-hand dot)
            wd = np.full(np.size(on), float(bench.OPERATING_POINTS["sce"].params["bin_width_sec"]))
        add(d, on, wd)
    t_lo, t_hi = ext
    L = t_hi - t_lo
    rel = [np.asarray(v, float) - t_lo for v in trains]
    for bw in COUNT_BINS:
        obs = _coactivity(rel, np.zeros(len(rel)), L, t_lo, t_lo, t_hi, bw, int(np.ceil(L / bw)))
        for x in COUNT_XS:
            add(f"count|{bw:g}|{x}", *_count_rule_calls(obs, t_lo, bw, x))
    for k in HERB_KS:
        add(f"herbison|{k}", *_herbison_calls(trains, k)[:2])
    return regime, seed, out


def _count_real_one(job):
    """One untreated baseline: how often chance alone reaches each bar, from shifted copies."""
    rid, dt, win, trains = job
    from bugarach.detectors.sce import _coactivity
    from bugarach.surrogates import circular_shift
    L = int(win[1] - win[0])
    tr = [np.asarray(v, np.int64) - int(win[0]) for v in trains]
    n = len(tr)
    dur = L * dt
    minutes = dur / 60.0
    draws = [circular_shift(tr, (0, L), (rid, "why-not-count", k)).trains for k in range(CHANCE_DRAWS)]
    out = dict(n_roi=n, minutes=minutes,
               rate=float(sum(np.size(v) for v in tr)) / max(1, n) / minutes)
    for bw in COUNT_BINS:
        nb = max(1, int(np.floor(dur / bw)))

        def counts(tt):
            rel = [np.asarray(v, float) * dt for v in tt]
            return _coactivity(rel, np.zeros(n), dur, 0.0, 0.0, nb * bw - 1e-9, bw, nb)
        sur = [counts(d) for d in draws]
        per10 = [float(np.mean([np.sum(c >= x) for c in sur])) / minutes * 10 for x in REAL_XS]
        need = next((x for x, v in zip(REAL_XS, per10) if v < 1.0), None)
        out[f"chance_per10|{bw:g}"] = per10
        out[f"need|{bw:g}"] = need
    return out


def _published_chance():
    """Cells that each fire at random, independently, at a published rate, run through the
    published rule. The plainest possible null — real cells do not fire evenly — so it is the
    size of the number a chance check would have to beat, not a verdict on anyone's data."""
    rng = np.random.default_rng(20260916)

    def one(rate_h, n_cells, hours):
        T = hours * 3600.0
        trains = [np.sort(rng.uniform(0, T, rng.poisson(rate_h * hours))) for _ in range(n_cells)]
        on, _, size = _herbison_calls(trains, 2)
        return dict(mse_per_cell_h=on.size / n_cells / hours,
                    cells_per=float(size.mean()) if size.size else float("nan"))
    curves = {f"{r:g}": [dict(cells=n, **one(r, n, PUB_HOURS)) for n in PUB_CELLS] for r in PUB_RATES}
    e = EDDLESTON
    at = {str(n): one(e["rate"], n, 5 * PUB_HOURS) for n in (e["field_lo"], e["field"], e["field_hi"])}
    return dict(curves=curves, eddleston=dict(e, chance=at))


def stage_count(work: Path) -> None:
    from concurrent.futures import ProcessPoolExecutor

    from bugarach import bench, dataset
    from bugarach.detectors.sce import _coactivity
    from bugarach.io import load_folder
    from bugarach.surrogate_stats import recordings_from_slices

    # ---- the bench: the same 24 recordings, the same grading ---------------------------------
    seeds = bench.fold_split(n_folds=4, seeds_per_fold=6).seeds
    regimes = ("baseline_quiet", "baseline_busy")
    with ProcessPoolExecutor(12) as ex:
        runs = list(ex.map(_count_bench_one, [(r, sd) for r in regimes for sd in seeds]))
    table = {}
    for reg in regimes:
        table[reg] = {}
        for name in runs[0][2]:
            got = [o[name] for r, _, o in runs if r == reg]
            p = bench.pool_scores([g[0] for g in got], detector=name.split("|")[0], regime=reg, seeds=seeds)
            table[reg][name] = dict(f1=p.f1, recall6=p.recall_at(0.18), recall3=p.recall_at(0.10),
                                    empty=sum(g[1][0] for g in got) / sum(g[1][1] for g in got))
    f1 = lambda reg, bw, x: np.nan_to_num(table[reg][f"count|{bw:g}|{x}"]["f1"])   # noqa: E731
    best = {f"{bw:g}": {reg: int(max(COUNT_XS, key=lambda x: f1(reg, bw, x))) for reg in regimes}
            for bw in COUNT_BINS}
    one_bar = {f"{bw:g}": int(max(COUNT_XS, key=lambda x: f1(regimes[0], bw, x) + f1(regimes[1], bw, x)))
               for bw in COUNT_BINS}
    rec = bench.BENCH_RECORDING
    block_rate = {reg: (bench.REGIMES[reg]["bg_rate_hz"] + rec["hot_rate_hz"]) * 60 for reg in regimes}

    # ---- the picture: the rule on the simulated minutes the algorithm figures use -------------
    sim = json.loads((work / "plain.json").read_text())["sim"]
    ext = sim["ext"]
    L = ext[1] - ext[0]
    nb = int(np.ceil(L / FIG_BIN))
    rel = [np.asarray(v, float) - ext[0] for v in sim["full_trains"]]
    obs = _coactivity(rel, np.zeros(len(rel)), L, ext[0], ext[0], ext[1], FIG_BIN, nb)
    ctr = ext[0] + (np.arange(nb) + 0.5) * FIG_BIN
    on, wd = _count_rule_calls(obs, ext[0], FIG_BIN, one_bar[f"{FIG_BIN:g}"])
    demo = {}
    for key in ("A", "B"):
        w = sim[key]["win"]
        t, y = _clip(ctr, obs, w, pad=FIG_BIN)
        demo[key] = dict(t=t, y=y, calls=_calls_in(on, wd, w))

    # ---- real untreated baselines: how much chance a fixed bar lets through -------------------
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        slices = load_folder(dataset.current("steps_excluded"))
    recs, skipped = recordings_from_slices(slices, "fast")
    jobs = [(r.recording_id, float(r.dt), tuple(r.window), [np.asarray(v) for v in r.trains]) for r in recs]
    with ProcessPoolExecutor(12) as ex:
        real = list(ex.map(_count_real_one, jobs))

    out = dict(bins=list(COUNT_BINS), xs=list(COUNT_XS), fig_bin=FIG_BIN, real_xs=list(REAL_XS),
               bench=table, best=best, one_bar=one_bar, block_rate_per_min=block_rate,
               demo=demo, real=real, n_skipped=len(skipped), herb_ks=list(HERB_KS),
               published=_published_chance())
    put(work, "count", out)
    b = f"{FIG_BIN:g}"
    print(f"  count: {b} s bins — best bar quiet {best[b]['baseline_quiet']}, busy {best[b]['baseline_busy']}, "
          f"one bar {one_bar[b]}; {len(real)} real baselines ({len(skipped)} skipped)")


# ----------------------------------------------------------------------- figures
GREEN, RED, GREY, BARC = "#1b7f3b", "#b3261e", "#8c8c8c", "#111111"
SHIFT_C, SHUF_C = "#1f6fb2", "#d9730d"


def _arr(v):
    return np.asarray([np.nan if x is None else x for x in v], float)


def _clock(t):
    """A time in the recording, as a person says it: 8m12s, 22m30s."""
    m, s = divmod(int(round(float(t))), 60)
    return f"{m}m{s}s" if s else f"{m}m"


def _by_activity(trains):
    """Quietest cell at the bottom, busiest at the top, counted on what is drawn.

    `bugarach.ui.diagnostic` sorts its rasters this way and says why: the order a store
    happens to use is an arbitrary label, while how busy a cell is is a coordinate. Sorting
    on the drawn stretch rather than the whole recording is the same module's fix of
    2026-09-07."""
    return [trains[i] for i in np.argsort([len(v) for v in trains], kind="stable")]


def _lane_calls(p, fig, rows, calls, y0, row_h=16, gap=4, label_x=None, names=None, counts=True):
    """Lanes above a raster: one row per detector, one mark per call. Returns y below."""
    from svgfig import MUTED
    y = y0
    for d in rows:
        cl = calls.get(d, [])
        for on, wd in cl:
            p.span(on, on + max(wd, 0.0), row_y=y + 2, row_h=row_h - 4, color=COLORS[d])
        name = (names or NAMES).get(d, d)
        n = sum(1 for on, _ in cl if p.xlim[0] <= on <= p.xlim[1])
        lab = f"{name} · {n} call{'' if n == 1 else 's'}" if counts else name
        fig.text(label_x if label_x is not None else p.x - 8, y + row_h - 4, lab, size=12,
                 anchor="end", color=MUTED)
        y += row_h + gap
    return y


def fig_orient(W):
    """The first picture in the document: a real recording, busy, with its coordinated
    events marked. Nothing is explained yet, so there are no detector lanes on it — only
    what a person can see. Tony, 2026-09-16: lead with a busy raster and a few events."""
    from svgfig import Figure, MUTED
    c = W["real"]["close"]["orient"]
    f = Figure(1000, 560)
    L, PW = 90, 700
    win = c["win"]
    f.text(L, 24, "A · ten minutes of one real recording", size=14, weight=600)
    lane = f.panel(L, 34, PW, 22, win, (0, 1), frame=False)
    stripes = sorted(c["stripes"], key=lambda s_: -s_["cells"])
    for s_ in c["stripes"]:
        lane.down_triangle(s_["t"] + 0.5, 44, color=INK_T, size=12)
    f.text(L - 8, 48, "many cells", size=11, anchor="end", color=MUTED)
    f.text(L - 8, 62, "at once", size=11, anchor="end", color=MUTED)
    r = f.panel(L, 62, PW, 400, win, (0, 1))
    r.raster(_by_activity(c["trains"]), width=1.2)
    r.xaxis_time(offset=win[0], target=5, label="minutes")
    r.ylabel(_plural(c["n_roi"], "cell"), dx=20)
    # B: one stripe, close up, so a tick is a visible thing
    top = stripes[0]["t"] if stripes else (win[0] + win[1]) / 2
    z = (top - 10.0, top + 10.0)
    ZX, ZW = 830, 150
    f.text(ZX, 24, "B · 20 seconds of it", size=14, weight=600)
    lz = f.panel(ZX, 34, ZW, 22, z, (0, 1), frame=False)
    lz.down_triangle(top + 0.5, 44, color=INK_T, size=12)
    rz = f.panel(ZX, 62, ZW, 400, z, (0, 1))
    rz.raster(_by_activity(c["trains"]), width=2.0)
    rz.xaxis_time(offset=top, target=2, label="seconds")
    lane.span(z[0], z[1], row_y=58, row_h=3, color="#9a9a9a", min_px=4)
    f.text(L, 516, "Each row is one cell. Each tick is one moment that cell brightened.", size=13,
           color=MUTED)
    f.text(L, 536, "Where a column of ticks lines up, many cells brightened together. ▼ marks each one.",
           size=13, color=MUTED)
    f.h = 556
    return f


def fig_raster(W):
    from svgfig import Figure, MUTED
    sim = W["sim"]
    A = sim["A"]
    ev = sim["event"]
    f = Figure(960, 420)
    L, PW = 70, 560
    p = f.panel(L, 60, PW, 24, A["win"], (0, 1))
    p.down_triangle(ev["time"], 72, color=INK_T, size=12)
    f.text(L, 44, "A · one minute of a recording", size=13, weight=600)
    r = f.panel(L, 92, PW, 250, A["win"], (0, 1))
    r.raster(A["trains"])
    r.xaxis_time(label="time in the recording")
    r.ylabel(f"{sim['n_roi']} cells", dx=22)
    # the zoom
    z0, z1 = ev["time"] - 2.0, ev["time"] + 2.0
    ZX, ZW = 700, 220
    f.text(ZX, 44, "B · the same moment, 4 seconds wide", size=13, weight=600)
    pz = f.panel(ZX, 60, ZW, 24, (z0, z1), (0, 1))
    pz.down_triangle(ev["time"], 72, color=INK_T, size=12)
    rz = f.panel(ZX, 92, ZW, 250, (z0, z1), (0, 1))
    rz.raster(A["trains"], width=2.2)
    rz.xaxis_time(label="time in the recording")
    # which 4 seconds B shows: a gray bracket in A's lane, never a line across the raster
    p.span(z0, z1, row_y=62, row_h=4, color="#9a9a9a", min_px=6)
    f.text(float(p.px(z1)) + 10, 76, "the 4 seconds shown in B", size=11, color=MUTED)
    f.h = 390
    return f


INK_T = "#111111"


def fig_chance(W):
    from svgfig import Figure, nice_ticks
    sim = W["sim"]
    f = Figure(960, 400)
    cols = [("A", "A · quiet cells, one real coordinated event", 80),
            ("B", "B · busy cells, nothing planted", 530)]
    for key, title, X in cols:
        D = sim[key]
        f.text(X, 26, title, size=13, weight=600)
        lane = f.panel(X, 36, 390, 22, D["win"], (0, 1))
        if key == "A":
            lane.down_triangle(sim["event"]["time"], 47, color=INK_T, size=11)
        r = f.panel(X, 64, 390, 170, D["win"], (0, 1))
        r.raster(_by_activity(D["trains"]))
        if key == "A":
            r.ylabel(f"{sim['n_roi']} cells", dx=16)
        c = D["coact"]
        ymax = 12
        q = f.panel(X, 250, 390, 100, D["win"], (0, ymax))
        q.bars(_arr(c["t"]), _arr(c["y"]), color="#6d8fb3", width_frac=0.9)
        q.yaxis(nice_ticks(0, ymax, 3), grid=True)
        if key == "A":
            q.ylabel("cells in each", lines=["cells that brightened", "in each 2 s bin"], dx=40)
        q.xaxis_time(label="time in the recording")
        mx = int(np.nanmax(_arr(c["y"])))
        f.text(X + 390, 244, f"most in one bin: {mx} cells", size=12, anchor="end", color="#333")
    return f


def _numbered(f, p, numbered, *, size=11, color=INK_T, bold_in=None):
    """Each event drawn as its own number in its cell's sequence, one row per cell.

    A tick cannot show a reader that a row MOVED — every tick looks like every other tick.
    The number is the cue: the same digits appear in the copy, shifted along and wrapped
    round at the end (Tony, 2026-09-16, resurrecting the lab's older teaching slide)."""
    n = len(numbered)
    if not n:
        return
    rh = p.h / n
    for i, row in enumerate(numbered):
        y = p.y + p.h - (i + 0.5) * rh + 4
        for t, k in row:
            if p.xlim[0] <= t <= p.xlim[1]:
                inside = bold_in is not None and bold_in[0] <= t < bold_in[1]
                f.text(float(p.px(t)), y, str(k), size=size + (1 if inside else 0), anchor="middle",
                       weight=700 if inside else 400, color="#0b5fa8" if inside else color)


def fig_chance_steps(W):
    """The four steps, on six simulated cells whose events are NUMBERED in firing order.

    Numbers rather than ticks, because a tick cannot show that a row moved: every tick looks
    like every other one, and the wrap at the end of the recording is invisible. Simulated
    cells rather than the bench recording, because a quiet cell has one event per minute and
    every number would read "1". Tony, 2026-09-16, resurrecting the lab's MATLAB slide.
    """
    from svgfig import Figure, MUTED, nice_ticks
    S = W["toys"]["steps"]
    L, bin = S["length"], tuple(S["bin"])
    f = Figure(1000, 560)
    # step 1: the recording
    X1, W1 = 60, 260
    f.step_badge(X1 + 8, 22, "1")
    f.text(X1 + 26, 27, "Count the recording", size=14, weight=600)
    f.para(X1, 50, f"How many cells light up inside the 2-second bin being tested? Here: "
                   f"{S['observed']} of 6.", width_chars=38, size=12, color=MUTED)
    lane = f.panel(X1, 96, W1, 14, (0, L), (0, 1), frame=False)
    lane.span(*bin, row_y=98, row_h=11, color="#9bb7d4", min_px=5)
    r = f.panel(X1, 112, W1, 150, (0, L), (0, 1))
    _numbered(f, r, S["numbered"], size=12, bold_in=bin)
    r.xaxis_time(target=3)
    f.text(X1, 312, "Six cells, one row each. Each event carries its", size=11, color=MUTED)
    f.text(X1, 328, "number in that cell's own order, so a row can be", size=11, color=MUTED)
    f.text(X1, 344, "followed when it slides. Blue bar: the bin tested.", size=11, color=MUTED)
    # step 2: shifted copies
    X2, W2 = 370, 250
    f.step_badge(X2 + 8, 22, "2")
    f.text(X2 + 26, 27, "Make a shifted copy", size=14, weight=600)
    f.para(X2, 50, "Slide each cell's row by its own random amount. Events pushed off the end come back "
                   "at the start. Count again.", width_chars=42, size=12, color=MUTED)
    yy = 112
    for i, ex in enumerate(S["examples"]):
        ln = f.panel(X2, yy, W2, 12, (0, L), (0, 1), frame=False)
        ln.span(*bin, row_y=yy + 1, row_h=10, color="#9bb7d4", min_px=5)
        rr = f.panel(X2, yy + 14, W2, 100, (0, L), (0, 1))
        _numbered(f, rr, ex["numbered"], size=11, bold_in=bin)
        for j, sh in enumerate(ex["shifts"]):
            row_y = yy + 14 + 100 - (j + 0.5) * (100 / len(ex["shifts"])) + 4
            f.text(X2 - 6, row_y, f"+{sh:g}s", size=9, anchor="end", color="#9a9a9a")
        f.text(X2 + W2 + 10, yy + 60, f"copy {i + 1}", size=11, color=MUTED)
        f.text(X2 + W2 + 10, yy + 78, _plural(ex["count"], "cell"), size=12, weight=600)
        yy += 128
    f.text(X2 - 30, yy + 2, "the slide given to each row", size=10, color="#9a9a9a")
    # step 3: many copies
    X3, W3 = 760, 190
    f.step_badge(X3 + 8, 22, "3")
    f.text(X3 + 26, 27, f"Repeat {S['n_copies']} times", size=14, weight=600)
    f.para(X3, 50, "The counts from the copies are what chance gives.", width_chars=32, size=12,
           color=MUTED)
    hist = np.asarray(S["hist"], float)
    ymax = max(10.0, hist.max() * 1.15)
    h = f.panel(X3, 112, W3, 180, (-0.6, 6.6), (0, ymax))
    h.bars(np.arange(7), hist, color="#b9c6d6", width_frac=0.85)
    h.yaxis(nice_ticks(0, ymax, 4), fmt="{:,.0f}", label=f"copies (of {S['n_copies']})", dx=36)
    h.xaxis_values([0, 2, 4, 6], label="cells in the bin")
    X = float(h.px(S["bar"]))
    f.line(X, 112, X, 292, color=BARC, width=2, dash="5 4")
    f.text(X + 5, 126, "the bar", size=12, weight=600)
    h.down_triangle(S["observed"], 102, color=GREEN, size=12)
    # step 4: decide
    f.step_badge(X3 + 8, 350, "4")
    f.text(X3 + 26, 355, "Decide", size=14, weight=600)
    share = (f"{S['share_at_least'] * 100:.0f}%" if S["share_at_least"] >= 0.01
             else f"under 1%")
    f.para(X3, 378, f"Only {share} of the copies reach {S['observed']} cells, so the real moment "
                    f"(green ▼) is called a coordinated event.", width_chars=32, size=12, color=MUTED)
    f.arrow(X1 + W1 + 14, 180, X2 - 52, 180)
    f.h = yy + 30
    return f


def fig_shift_shuffle(W, numbers):
    from svgfig import Figure, MUTED, nice_ticks
    T = W["toys"]
    f = Figure(980, 900)
    rows = [("bursty", "A · cells that fire in bursts", 40,
             "A shuffle breaks the bursts apart, so events spread over more of the recording and more "
             "cells land in any bin by chance. The bar comes out too high and the real burst is missed."),
            ("even", "B · cells that fire at a steady beat", 410,
             "A shuffle lets a cell's events pile up in one bin and leave others empty, so fewer cells "
             "reach any bin by chance. The bar comes out too low and a chance lineup is called.")]
    for key, title, Y, story in rows:
        D = T[key]
        b = D["bin"]
        f.text(40, Y, title, size=14, weight=600)
        f.para(40, Y + 20, story, width_chars=130, size=12, color=MUTED)
        for j, (lab, trs, col) in enumerate((("the recording", D["trains"], INK_T),
                                             ("one shifted copy", D["shift_example"], SHIFT_C),
                                             ("one shuffled copy", D["shuffle_example"], SHUF_C))):
            X = 60 + j * 200
            f.text(X, Y + 62, lab, size=12, weight=600, color=col)
            ln = f.panel(X, Y + 68, 170, 10, (0, T["length"]), (0, 1), frame=False)
            ln.span(*b, row_y=Y + 69, row_h=8, color="#9bb7d4")
            r = f.panel(X, Y + 80, 170, 120, (0, T["length"]), (0, 1))
            r.raster(trs, width=1.4)
            r.xaxis_values([0, 10, 20], fmt="{:g}s")
            cnt = sum(1 for v in trs if np.any((np.asarray(v) >= b[0]) & (np.asarray(v) < b[1])))
            f.text(X + 170, Y + 236, f"{_plural(cnt, 'cell')} in the bin", size=11, anchor="end", color=MUTED)
        for j, (lab, hist, col, pv) in enumerate((("5,000 shifted copies", D["shift_hist"], SHIFT_C, D["p_shift"]),
                                                  ("5,000 shuffled copies", D["shuffle_hist"], SHUF_C, D["p_shuffle"]))):
            X = 690 + j * 150
            ymax = 2500
            h = f.panel(X, Y + 80, 120, 120, (-0.6, 6.6), (0, ymax))
            h.bars(np.arange(7), hist, color=col, width_frac=0.8)
            h.xaxis_values([0, 2, 4, 6])
            if j == 0:
                h.yaxis([0, 1000, 2000], fmt="{:,.0f}", label="copies", dx=44)
            h.down_triangle(D["observed"], Y + 72, color=INK_T, size=10)
            f.text(X + 60, Y + 62, lab, size=12, anchor="middle", weight=600, color=col)
            share = f"{pv * 100:.1f}%" if pv >= 0.001 else "under 0.1%"
            verdict = "called" if pv < 0.05 else "not called"
            # Say what the number is a share OF. "reach 4: 0.3%" left the reader to guess
            # (Tony, 2026-09-16); it is the share of copies whose count matched the recording's.
            f.text(X + 60, Y + 232, f"copies with {D['observed']} or more", size=11, anchor="middle",
                   color=MUTED)
            f.text(X + 60, Y + 246, f"cells in the bin: {share}", size=11, anchor="middle", color=MUTED)
            f.text(X + 60, Y + 264, f"→ {verdict}", size=12, anchor="middle", weight=700,
                   color=GREEN if (verdict == "called") == (key == "bursty") else RED)
        f.text(840, Y + 284, "across: cells in the bin · ▼ what the recording itself gave",
               size=11, anchor="middle", color=MUTED, italic=True)
        f.text(840, Y + 300, "a count that fewer than 5 copies in 100 reach is called",
               size=11, anchor="middle", color=MUTED, italic=True)
    # C: the lab's own recordings
    Y = 750
    f.text(40, Y, "C · on the lab's own recordings (84 untreated recordings, brief events)", size=14,
           weight=600)
    d = numbers["sur_fast_doubles"]
    n6 = numbers["sur_fast_n6"]
    groups = [("events landing in a 2-second bin their own cell already filled, per 1,000 events",
               [math.floor(v + 0.5) for v in (d["real"], d["shift"], d["shuffle"])], "{:.0f}", 120, 40),
              ("share of 2-second bins where 6 or more cells brighten",
               [100 * n6["real"], 100 * n6["shift"], 100 * n6["shuffle"]], "{:.2f}%", 2.0, 520)]
    for lab, vals, fmt, vmax, X in groups:
        f.text(X, Y + 22, lab, size=12, color=MUTED)
        for i, (nm, v, col) in enumerate((("recording", vals[0], INK_T), ("shifted", vals[1], SHIFT_C),
                                          ("shuffled", vals[2], SHUF_C))):
            yy = Y + 40 + i * 26
            f.text(X + 70, yy + 14, nm, size=12, anchor="end", color=col, weight=600)
            wbar = 300 * v / vmax
            f.rect(X + 78, yy + 2, wbar, 16, fill=col)
            f.text(X + 84 + wbar, yy + 15, fmt.format(v), size=12, color=INK_T)
    return f


def _found(calls, t, tol=2.5):
    return any(on - tol <= t <= on + max(wd, 0.0) + tol for on, wd in calls)


def _plural(n, word):
    return f"{n:g} {word}{'' if n == 1 else 's'}"


#: The steps each algorithm follows, in the words the page uses. {..} are filled from its
#: settings so the pictures and the settings cannot drift apart.
STEPS = {
    "rate": ["Add up every event from every cell, in a 1-second window that slides along.",
             "Work out the average of that number over the {ctx:g} seconds around each moment.",
             "Set the bar at that average plus {ex:g} events per second.",
             "Call a coordinated event wherever the count goes over the bar."],
    "coact": ["Cut time into {bin:g}-second bins. Count how many different cells light up in each.",
              "For a bin with at least 3 cells, take the {ctx:g} seconds around it and make "
              "{ns} shifted copies (Figure 4).",
              "Set the bar well above what the copies give: their average plus 3.72 times their "
              "typical spread.",
              "Call the bin if the real count is over the bar."],
    "loco": ["Cut time into {bin:g}-second bins. Count how many different cells light up in each.",
             "Every {step:g} seconds, make {ns} shifted copies of the minute before and of the minute after.",
             "On each side, find the count that only 1 copied bin in 1,000 goes over. "
             "The bar is the higher of the two sides.",
             "Call a bin if its count is over the bar and at least 3 cells take part."],
    "sce": ["Cut time into {bin:g}-second bins. Count how many different cells light up in each.",
            "Make {ns} shifted copies of the whole stretch being studied.",
            "Pool every bin from every copy. The bar is the count that only 1 bin in 100 goes over. "
            "It is one bar for the whole stretch.",
            "Call a bin if its count is over the bar and at least 3 cells take part."],
    "cicada": ["Switch each cell on for a fixed {on:g} second after each of its events (see the caption).",
               "Count how many cells are on in every 0.1-second frame.",
               "Make {ns} shifted copies of the whole recording. The bar is the count that only 1 frame "
               "in 100,000 goes over.",
               "Call each peak of the count that reaches the bar."],
    "sync": ["Give every event a score from 0 to 1: the share of the other cells that have an event "
             "close to it. This part is a published measure (SPIKE-synchronization).",
             "“Close” is judged from each cell's own gaps between its events, and is never more "
             "than {tau:g} seconds.",
             "Spread those per-event scores into a continuous line over time, by averaging the scores "
             "of the events in each 0.1-second frame.",
             "Find the peaks of that line. A peak that rises above {bar:g} and covers at least 3 events "
             "becomes a call. No copies are made."],
}


def _steps_text(det, st):
    fill = dict(ctx=st.get("context_win", st.get("context_win_sec", 60)),
                ex=st.get("excess_threshold_hz", 5), bin=st.get("int_win_sec", st.get("bin_width_sec", 1)),
                ns=st.get("n_surrogates", 100), step=st.get("thr_step_sec", 15),
                on=st.get("active_duration_sec", 1), tau=st.get("tau_max", 0.25),
                bar=st.get("C_threshold", 0.1))
    return [s.format(**fill) for s in STEPS[det]]


#: What each line in the measurement panel IS, said beside the line itself. A key at the
#: foot of the figure is not enough — Tony, 2026-09-16, on the LoCo figure: "what is the
#: purple line, what is the dashed line". The reader should not have to travel to find out.
LINE_LABELS = {
    "rate": [("events per second, every cell added up", "rate", "y"),
             ("the average nearby", GREY, "ref"), ("the bar", BARC, "bar")],
    "coact": [("cells in each 2 s bin", "coact", "y"), ("the copies' average", GREY, "mean"),
              ("the bar", BARC, "bar")],
    "loco": [("cells in each 1 s bin", "loco", "y"), ("the bar", BARC, "bar")],
    "sce": [("cells in each 10 s bin", "sce", "y"), ("the bar", BARC, "bar")],
    "cicada": [("cells switched on", "cicada", "y"), ("the bar", BARC, "bar")],
    "sync": [("score of each event", "sync", "py"),
             ("the continuous line those scores make", "#7a2a00", "cy"), ("the bar", BARC, None)],
}

MEASURE = {"rate": ("events per second", "all cells added up", (0, 14)),
           "coact": ("cells per 2 s bin", "", (0, 14)),
           "loco": ("cells per 1 s bin", "", (0, 14)),
           "sce": ("cells per 10 s bin", "", (0, 24)),
           "cicada": ("cells switched on", "per 0.1 s frame", (0, 14)),
           "sync": ("score (0 to 1)", "", (0, 0.3))}


def _measure(p, det, D):
    c = COLORS[det]
    M = D[det]
    if det == "rate":
        p.curve(_arr(M["t"]), _arr(M["ref"]), color=GREY, width=2.2)
        p.curve(_arr(M["t"]), _arr(M["y"]), color=c, width=1.3)
        p.curve(_arr(M["t"]), _arr(M["bar"]), color=BARC, width=1.8, dash="5 4")
    elif det == "coact":
        p.steps(_arr(M["t"]), _arr(M["y"]), color=c, width=1.6)
        p.dots(_arr(M["t"]), _arr(M["mean"]), color=GREY, r=2.6)
        p.dashes(_arr(M["t"]), _arr(M["bar"]), color=BARC, half_width=6)
    elif det in ("loco", "sce", "cicada"):
        p.steps(_arr(M["t"]), _arr(M["y"]), color=c, width=1.4 if det != "cicada" else 1.0)
        p.steps(_arr(M["t"]), _arr(M["bar"]), color=BARC, width=1.8, dash="5 4")
    else:
        p.dots(_arr(M["px"]), _arr(M["py"]), color=c, r=2.4, opacity=0.8)
        p.curve(_arr(M["cx"]), _arr(M["cy"]), color="#7a2a00", width=1.1)
        p.hline(M["bar"], color=BARC, width=1.8, dash="5 4")


def _hist_panel(f, X, Y, Wd, Hh, hist, *, observed, bar, color, xlabel, title, log=False,
                xmax=None, ylabel="copied bins"):
    from svgfig import MUTED, nice_ticks
    hist = np.asarray(hist, float)
    xmax = xmax or len(hist) - 1
    hist = hist[:xmax + 1]
    f.text(X, Y - 10, title, size=12, weight=600)
    if log:
        vals = np.where(hist > 0, np.log10(np.maximum(hist, 1)), np.nan)
        top = math.ceil(np.nanmax(vals))
        p = f.panel(X, Y, Wd, Hh, (-0.6, xmax + 0.6), (0, top))
        p.bars(np.arange(xmax + 1), vals, color=color, width_frac=0.85)
        ticks = list(range(0, top + 1, 2))
        for v in ticks:
            Yp = float(p.py(v))
            f.line(X - 5, Yp, X, Yp, color=MUTED)
            f.text(X - 8, Yp + 4, f"{10 ** v:,.0f}", size=11, anchor="end", color=MUTED)
        p.ylabel(ylabel, dx=52)
    else:
        top = max(1.0, hist.max() * 1.15)
        p = f.panel(X, Y, Wd, Hh, (-0.6, xmax + 0.6), (0, top))
        p.bars(np.arange(xmax + 1), hist, color=color, width_frac=0.85)
        p.yaxis(nice_ticks(0, top, 3), fmt="{:,.0f}", label=ylabel, dx=44)
    step = 2 if xmax <= 14 else 5
    p.xaxis_values(list(range(0, xmax + 1, step)), label=xlabel)
    if bar is not None and np.isfinite(bar):
        Xb = float(p.px(bar))
        f.line(Xb, Y, Xb, Y + Hh, color=BARC, width=2, dash="5 4")
        f.text(Xb + 4, Y + 14, "bar", size=11, weight=600)
    if observed is not None:
        p.down_triangle(observed, Y - 1, color=GREEN, size=11)
    return p


def fig_algorithm(W, det):
    from svgfig import Figure, MUTED, nice_ticks
    sim = W["sim"]
    st = sim["settings"][det]
    ev = sim["event"]
    f = Figure(1000, 700)
    # the recipe
    f.text(20, 26, f"How {NAMES[det]} decides", size=16, weight=700)
    y = 56
    for i, s in enumerate(_steps_text(det, st)):
        f.step_badge(32, y - 4, str(i + 1), color=COLORS[det])
        y = f.para(52, y, s, width_chars=40, size=13) + 12
    # the chance picture under the recipe
    hy = max(y + 30, 330)
    if det == "coact":
        q, b = sim["chance_coact"], sim["chance_coact_B"]
        for j, (qq, lab) in enumerate(((q, "a quiet minute (A)"), (b, "a busy minute (B)"))):
            hist = np.bincount(np.asarray(qq["counts"], int), minlength=15)[:15]
            _hist_panel(f, 80 + j * 190, hy + 20, 130, 120, hist, observed=qq["observed"], bar=qq["bar"],
                        color="#b9c6d6", xlabel="cells", title=lab, xmax=14,
                        ylabel="copies" if j == 0 else "")
        f.text(20, hy - 4, "100 shifted copies of the 60 s around one bin:", size=12, color=MUTED)
    elif det == "loco":
        q = sim["chance_loco"]
        for j, (side, lab, p999) in enumerate((("before", "the minute before", q["p999_before"]),
                                               ("after", "the minute after", q["p999_after"]))):
            _hist_panel(f, 80 + j * 190, hy + 20, 130, 120, q[side], observed=q["observed"] if j else None,
                        bar=p999, color="#c9b6e4", xlabel="cells", title=lab, log=True, xmax=10,
                        ylabel="copied bins" if j == 0 else "")
        f.text(20, hy - 4, "100 shifted copies of each side of the planted event:", size=12, color=MUTED)
    elif det == "sce":
        q = sim["chance_sce"]
        _hist_panel(f, 80, hy + 20, 250, 120, q["hist"], observed=q["observed"], bar=q["bar"],
                    color="#b8dcb8", xlabel="cells in a 10 s bin", title="every bin of 200 copies",
                    log=True, xmax=20)
        f.text(20, hy - 4, "200 shifted copies of the whole recording, pooled:", size=12, color=MUTED)
    elif det == "cicada":
        q = sim["chance_cicada"]
        _hist_panel(f, 80, hy + 20, 250, 120, q["hist"], observed=q["observed"], bar=q["bar"],
                    color="#f0b8da", xlabel="cells switched on in a frame", title="every frame of 100 copies",
                    log=True, xmax=14, ylabel="copied frames")
        f.text(20, hy - 4, "100 shifted copies of the whole recording, pooled:", size=12, color=MUTED)
    elif det == "rate":
        # The two windows, drawn to scale against each other: what gets counted (1 s) sits at
        # the middle of what it is compared against (60 s). Tony, 2026-09-16 — and both are
        # settings, not facts about the cells.
        ctx_s = float(st.get("context_win", 60.0))
        rate_s = float(st.get("rate_win", 1.0))
        f.text(20, hy - 6, "The two windows, at one moment:", size=12, weight=600)
        span = (-ctx_s / 2 - 6, ctx_s / 2 + 6)
        wp = f.panel(60, hy + 18, 290, 52, span, (0, 1), frame=False)
        wp.span(-ctx_s / 2, ctx_s / 2, row_y=hy + 22, row_h=18, color="#cfd9e6")
        f.text(float(wp.px(0)), hy + 35, f"context window · {ctx_s:g} s", size=11, anchor="middle")
        wp.span(-rate_s / 2, rate_s / 2, row_y=hy + 44, row_h=18, color=COLORS["rate"], min_px=3)
        f.text(float(wp.px(0)) + 10, hy + 57, f"counting window · {rate_s:g} s", size=11)
        f.line(float(wp.px(0)), hy + 14, float(wp.px(0)), hy + 66, color=BARC, width=1, dash="2 3")
        f.text(float(wp.px(0)), hy + 10, "the moment being scored", size=10, anchor="middle", color=MUTED)
        wp.xaxis_values([-30, 0, 30], fmt="{:g}s")
        yb = f.para(20, hy + 108,
                    f"rate+context counts every event from every cell inside the {rate_s:g}-second "
                    f"window, and compares that with the average over the {ctx_s:g}-second window "
                    f"centred on the same moment. No copies are made.", width_chars=46, size=12,
                    color=MUTED)
        f.para(20, yb + 14,
               "Both window widths are settings, like the bar: they could be tuned, and so far they "
               "have not been. Only the bar has been swept (Section 9).", width_chars=46, size=12,
               color=MUTED)
    elif det == "sync":
        n = sim["n_roi"]
        f.text(20, hy, "Why small events cannot reach the bar:", size=12, color=MUTED)
        p = f.panel(40, hy + 40, 300, 26, (0, 0.3), (0, 1))
        for k_, lab in ((3, "3 cells"), (ev["n_part"], f"{ev['n_part']} cells"), (10, "10 cells")):
            v = (k_ - 1) / (n - 1)
            X = float(p.px(v))
            f.line(X, hy + 40, X, hy + 66, color=COLORS["sync"], width=2)
            f.text(X, hy + 34, lab, size=11, anchor="middle", color=COLORS["sync"])
        Xb = float(p.px(st.get("C_threshold", 0.1)))
        f.line(Xb, hy + 36, Xb, hy + 70, color=BARC, width=2.5)
        f.text(Xb, hy + 92, "bar", size=11, anchor="middle", weight=700)
        p.xaxis_values([0, 0.2, 0.3], fmt="{:.1f}")
        f.text(40, hy + 20, "the highest score an event can reach, by how many cells join it:", size=11,
               color=MUTED)
        f.para(20, hy + 110, f"With {n} cells, an event joined by k cells can score at most "
                             f"(k−1) ÷ {n - 1}. An event joined by 3 cells tops out at "
                             f"{2 / (n - 1):.2f}, below the bar.", width_chars=46, size=12, color=MUTED)
    # the two views
    for j, (key, title) in enumerate((("A", "A · a planted event (quiet cells)"),
                                      ("B", "B · a busy stretch, nothing planted"))):
        D = sim[key]
        X, Wd = 450 + j * 275, 240
        win = D["win"]
        f.text(X, 26, title, size=13, weight=600)
        f.text(X, 42, f"one minute, from {_clock(win[0])} into the recording", size=11, color=MUTED)
        calls = D[f"{det}_calls"]
        lane = f.panel(X, 52, Wd, 50, win, (0, 1))
        if key == "A":
            ok = _found(calls, ev["time"])
            lane.down_triangle(ev["time"], 64, color=GREEN if ok else RED, size=12)
        for on, wd in calls:
            lane.span(on, on + max(wd, 0.0), row_y=78, row_h=16, color=COLORS[det])
        n_calls = sum(1 for on, wd in calls if on + wd >= win[0] and on <= win[1])
        f.text(X + Wd, 116, _plural(n_calls, "call"), size=12, anchor="end", color=MUTED)
        r = f.panel(X, 122, Wd, 178, win, (0, 1))
        r.raster(_by_activity(D["trains"]), width=1.1)
        label, sub, ylim = MEASURE[det]
        # NAME THE LINES ABOVE THE PANEL, NOT ON IT. Labels placed inside collided with the
        # data and with each other — "the average nearby" landed on the average it named
        # (Tony, 2026-09-16: "TEXT OVERLAP! UGH!"), which is also what CLAUDE.md means by
        # nothing competing with the marks. Above the frame nothing can collide by
        # construction, and the labels still sit against the panel they belong to.
        if j == 0:                       # once, beside the left panel; both columns share it
            ly = 306
            for text, col, _key in LINE_LABELS[det]:
                f.rich(X, ly, [("▬ ", dict(color=COLORS.get(col, col), weight=700)),
                               (text, dict(color=MUTED))], size=11)
                ly += 14
        p = f.panel(X, 352, Wd, 200, win, ylim)
        _measure(p, det, D)
        ticks = nice_ticks(*ylim, 4)
        p.yaxis(ticks, fmt="{:g}", grid=True)
        if j == 0:
            p.ylabel(label, lines=[label] + ([sub] if sub else []), dx=40)
            r.ylabel(f"{sim['n_roi']} cells", dx=14)
            f.text(X - 8, 72, "planted", size=11, anchor="end", color=MUTED)
            f.text(X - 8, 91, "calls", size=11, anchor="end", color=MUTED)
        # BOTH VIEWS ARE ONE MINUTE, so both axes count seconds from the start of that
        # minute. Absolute clock times (8m … 8m30s against 22m30s … 23m30s) hid the fact
        # that the panels are the same width and invited the reader to do arithmetic to
        # find out (Tony, 2026-09-16). Where each minute sits is in the panel's own title.
        p.xaxis_time(offset=win[0], target=4,
                     label="seconds from the start of this minute")
    # The foot carries only what nothing else names: the two triangles. Every line is
    # labelled beside the panel it is drawn in, so repeating it here is ink that sends the
    # reader travelling for something already in front of them.
    ky = 625
    xx = 460
    for g, col, lab in [("▼", GREEN, "planted event, found"), ("▼", RED, "planted event, missed")]:
        f.rich(xx, ky, [(g + " ", dict(color=col, weight=700)), (lab, dict(color=MUTED))], size=12)
        xx += 16 + 7.0 * len(lab) + 14
        if xx > 900:
            xx, ky = 460, ky + 20
    f.h = ky + 20
    return f


def fig_network(W):
    from svgfig import Figure, MUTED, nice_ticks
    T, sim = W["tube"], W["sim"]
    ev = sim["event"]
    A = T["A"]
    f = Figure(1000, 900)
    z = (ev["time"] - 3.0, ev["time"] + 3.0)
    boxes = [(20, 40), (350, 40), (680, 40), (20, 420), (350, 420), (680, 420)]
    titles = ["What goes in", f"Stretch each event to {T['widen_s']:g} s",
              "Brightness: share of cells lit",
              "Compare now with the seconds around it", "A small stack of layers",
              "The score, and the call"]
    words = ["The list of event times, as a raster: 1 where a cell has an event in a 0.1 s frame, 0 elsewhere.",
             "Each event is widened a little, so events a few frames apart can overlap.",
             "At each frame, the share of cells that are lit. A coordinated event is a bright flash.",
             "Four filters subtract the brightness over the surrounding seconds from the brightness right "
             "now. The widths of the filters were learned.",
             f"Six layers of simple arithmetic combine the four comparisons and the brightness. Training "
             f"adjusted {T['n_params']:,} numbers in all.",
             f"A score from 0 to 1 for every frame. Where it passes the call level ({T['threshold']:.2f}), "
             f"the network makes a call."]
    for i, ((X, Y), t, w) in enumerate(zip(boxes, titles, words)):
        f.step_badge(X + 12, Y + 6, str(i + 1), color=COLORS["tube"])
        f.text(X + 30, Y + 11, t, size=14, weight=600)
        f.para(X, Y + 34, w, width_chars=44, size=12, color=MUTED)
    PW, PH = 290, 210
    # 1 raster in (6 s)
    r = f.panel(40, 150, PW - 20, PH, z, (0, 1))
    r.raster(A["onsets"], width=2.0)
    r.xaxis_time(target=3)
    r.ylabel(f"{sim['n_roi']} cells", dx=14)
    # 2 widened
    r2 = f.panel(370, 150, PW - 20, PH, z, (0, 1))
    n = len(A["widened"])
    rh = PH / n
    for i, v in enumerate(A["widened"]):
        for t in v:
            if z[0] <= t <= z[1]:
                x0 = float(r2.px(t))
                f.rect(x0, 150 + PH - (i + 1) * rh + rh * 0.1, max(1.2, float(r2.px(t + T["dt"])) - x0), rh * 0.8,
                       fill=INK_T)
    r2.xaxis_time(target=3)
    # 3 brightness
    ta, ba = _arr(A["t"]), _arr(A["bright"])
    p3 = f.panel(700, 150, PW - 20, PH, A["win"], (0, 30))
    p3.curve(ta, ba, color=COLORS["tube"], width=1.1)
    p3.yaxis([0, 10, 20, 30], fmt="{:g}%", grid=True)
    p3.xaxis_time(target=3)
    # 4 filters: one learned kernel and the four responses
    k = T["kernel_example"]
    kl, kw = _arr(k["lag_s"]), _arr(k["w"])
    p4a = f.panel(60, 540, 110, 90, (-13, 13), (float(np.nanmin(kw)) * 1.3, float(np.nanmax(kw)) * 1.1))
    p4a.hline(0, color=GRID_C, width=1, dash=None)
    p4a.curve(kl, kw, color=COLORS["tube"], width=1.6)
    p4a.xaxis_values([-10, 0, 10], fmt="{:g}s")
    f.text(60, 530, "one learned filter", size=11, color=MUTED)
    p4 = f.panel(200, 540, 120, 90, A["win"], (-3, 8))
    for j, rr in enumerate(A["resp"]):
        p4.curve(ta, _arr(rr), color=COLORS["tube"], width=1.0)
    p4.xaxis_time(target=2)
    f.text(200, 530, "the four comparisons", size=11, color=MUTED)
    # 5 the layers
    for i in range(6):
        bx = 380 + i * 42
        f.rect(bx, 560, 34, 70, fill="#f2e1dc", stroke=COLORS["tube"], rx=4)
        f.text(bx + 17, 600, str(i + 1), size=12, anchor="middle", weight=600, color=COLORS["tube"])
        if i < 5:
            f.arrow(bx + 34, 595, bx + 42, 595, color=COLORS["tube"], head=5, width=1.2)
    f.text(380, 650, "each layer looks a little further in time", size=11, color=MUTED)
    f.text(380, 666, "than the one before", size=11, color=MUTED)
    # 6 the score, A and B
    for j, key in enumerate(("A", "B")):
        D = T[key]
        Y = 540 + j * 170
        lane = f.panel(700, Y, PW - 20, 24, D["win"], (0, 1))
        if key == "A":
            lane.down_triangle(ev["time"], Y + 8, color=GREEN if _found(D["calls"], ev["time"]) else RED, size=10)
        for on, wd in D["calls"]:
            lane.span(on, on + max(wd, 0.0), row_y=Y + 14, row_h=8, color=COLORS["tube"])
        ps = f.panel(700, Y + 28, PW - 20, 90, D["win"], (0, 1.02))
        ps.curve(_arr(D["t"]), _arr(D["score"]), color=COLORS["tube"], width=1.2)
        ps.hline(T["threshold"], color=BARC, width=1.6)
        ps.yaxis([0, 0.5, 1], fmt="{:g}")
        ps.xaxis_time(target=3)
        f.text(700 + PW - 20, Y - 4, "A · planted event, quiet cells" if key == "A" else
               "B · busy stretch, nothing planted", size=11, anchor="end", color=MUTED)
    # arrows between the stages
    p3.ylabel("cells lit", dx=44)
    f.text(700, 146, "zoomed out to 60 s", size=11, color=MUTED)
    for (x1, y1, x2, y2) in ((315, 250, 360, 250), (645, 250, 690, 250),
                             (330, 600, 372, 600), (640, 600, 692, 600)):
        f.arrow(x1, y1, x2, y2, color="#999")
    f.h = 880
    return f


GRID_C = "#dddddd"


def fig_simulator(W, numbers):
    from svgfig import Figure, MUTED
    sim = W["sim"]
    bench = numbers["bench"]
    ext = sim["ext"]
    f = Figure(1000, 470)
    L, PW = 110, 860
    lane = f.panel(L, 30, PW, 58, ext, (0, 1))
    sizes = {max(bench["participation_pct"]): "#08306b", sorted(bench["participation_pct"])[1]: "#2171b5",
             min(bench["participation_pct"]): "#6baed6"}
    for t, k in sim["planted"]:
        pct = min(sizes, key=lambda p: abs(p - 100 * k / sim["n_roi"]))
        lane.down_triangle(t, 44, color=sizes[pct], size=11)
    for t, k in sim["decoys"]:
        lane.down_triangle(t, 62, color="#555", size=10, hollow=True)
    h0, h1 = sim["hot"]
    lane.span(h0, h1, row_y=74, row_h=10, color="#f0c9a0")
    f.text(L - 8, 48, "planted", size=11, anchor="end", color=MUTED)
    f.text(L - 8, 66, "decoys", size=11, anchor="end", color=MUTED)
    f.text(L - 8, 84, "busy stretch", size=11, anchor="end", color=MUTED)
    r = f.panel(L, 94, PW, 260, ext, (0, 1))
    order = np.argsort([len(v) for v in sim["full_trains"]], kind="stable")
    r.raster([sim["full_trains"][i] for i in order], width=0.9)
    r.ylabel(f"{sim['n_roi']} cells", dx=14)
    r.xaxis_time(label="time in the recording", target=10)
    y = 412
    for pct, col in sorted(sizes.items(), reverse=True):
        #: Cell counts, not fractions — and the middle size is named for what it IS (the
        #: measured real size), not for where it sits between the other two.
        note = {18: " — the usual real size"}.get(pct, "")
        f.rich(L + {30: 0, 18: 190, 10: 430}.get(pct, 0), y,
               [("▼ ", dict(color=col, weight=700)),
                (f"planted event, {round(pct / 100 * sim['n_roi'])} cells{note}", dict(color=MUTED))],
               size=12)
    f.rich(L + 600, y, [("▽ ", dict(color="#555", weight=700)), ("decoy: built the same way, not counted", dict(color=MUTED))], size=12)
    f.rich(L, y + 22, [("▬ ", dict(color="#f0c9a0", weight=700)),
                       (f"busy stretch: every cell gets extra random events, nothing planted", dict(color=MUTED))], size=12)
    f.h = 450
    return f


def fig_grading(W, numbers):
    from svgfig import Figure, MUTED
    tol = numbers["tol_s"]
    f = Figure(1000, 250)
    L, PW, win = 150, 800, (0, 60)
    planted = [8, 27, 50]
    calls = [(7.2, 1.5), (26.0, 0.8), (27.9, 0.6), (40.0, 1.0)]
    lane = f.panel(L, 30, PW, 110, win, (0, 1))
    for t in planted:
        lane.span(t - tol, t + tol, row_y=34, row_h=26, color="#dff0e3")
    for t, ok in zip(planted, (True, True, False)):
        lane.down_triangle(t, 46, color=GREEN if ok else RED, size=13)
    labels = ["hit", "hit", "false alarm: a second call on the same event", "false alarm: nothing planted here"]
    for (on, wd), lab, row in zip(calls, labels, (0, 0, 1, 0)):
        yy = 76 + row * 30
        lane.span(on, on + wd, row_y=yy, row_h=14, color=GREEN if lab == "hit" else RED)
        f.text(float(lane.px(on + wd)) + 6, yy + 12, lab, size=12, color=GREEN if lab == "hit" else RED)
    f.text(float(lane.px(50)) - 12, 52, "miss: no call near this planted event", size=12, color=RED,
           anchor="end")
    f.text(L - 8, 52, "planted events", size=12, anchor="end", color=MUTED)
    f.text(L - 8, 88, "calls", size=12, anchor="end", color=MUTED)
    lane.xaxis_time(label="a simulated minute, drawn to show the rule")
    f.text(L, 214, f"Green bands reach {tol:g} seconds either side of each planted event. A call that touches a "
                   f"band is a hit; each call can claim only one event.", size=12, color=MUTED)
    f.text(L, 234, "Here: found 2 of 3 planted events; 2 of 4 calls were right.", size=12, color=MUTED)
    return f


def fig_scores(W, numbers, dets=CODED):
    from svgfig import Figure, MUTED
    dets = list(dets)
    f = Figure(1000, 470)
    ceil = numbers["f1_ceiling"]
    for j, (reg, title) in enumerate((("baseline_quiet", "A · quiet background"),
                                      ("baseline_busy", "B · busy background"))):
        X, PW = 170 + j * 420, 360
        f.text(X, 24, title, size=13, weight=600)
        p = f.panel(X, 36, PW, 340, (0, 1), (len(dets) - 0.5, -0.5))
        for v in (0, 0.2, 0.4, 0.6, 0.8, 1.0):
            Xv = float(p.px(v))
            f.line(Xv, 36, Xv, 376, color=GRID_C)
        Xc = float(p.px(ceil))
        f.line(Xc, 36, Xc, 376, color=BARC, dash="5 4", width=1.5)
        f.text(Xc, 392 + 14 * 0, "", size=1)
        for i, d in enumerate(dets):
            v = numbers[f"perf_{reg}_{d}"]
            Y = float(p.py(i))
            f.line(float(p.px(v["f1_min"])), Y, float(p.px(v["f1_max"])), Y, color=COLORS[d], width=3)
            f.add(f"<circle cx='{float(p.px(v['f1'])):.1f}' cy='{Y:.1f}' r='6' fill='{COLORS[d]}'/>")
            if d == "sce":
                # binned SCE's second score, SAID rather than coded as a hollow marker. A
                # second symbol makes the reader carry a key across the page to find out
                # that it is the same program measured a second way (Tony, 2026-09-16:
                # "the open symbol is confusing"). An arrow and four words do not.
                fb = numbers["sce_rescore"]["quiet" if "quiet" in reg else "busy"]["full_bin"]["tuned_f1"]
                xf = float(p.px(fb))
                f.line(float(p.px(v["f1"])) + 8, Y, xf - 8, Y, color=COLORS[d], width=1,
                       dash="2 3")
                f.add(f"<circle cx='{xf:.1f}' cy='{Y:.1f}' r='6' fill='{COLORS[d]}'/>")
                f.text(Xc - 10, Y + 20, "both dots are binned SCE (see the text)",
                       size=10, anchor="end", color=COLORS[d])
            if j == 0:
                f.text(X - 10, Y + 4, NAMES[d], size=13, anchor="end", color=INK_T)
        p.xaxis_values([0, 0.2, 0.4, 0.6, 0.8, 1.0], label="overall score (0 to 1; higher is better)")
    f.rich(170, 440, [("●", dict(color=INK_T, weight=700)), (" average   ", dict(color=MUTED)),
                      ("━", dict(color=INK_T, weight=700)),
                      (" lowest to highest across the 4 tests   ", dict(color=MUTED)),
                      ("┄", dict(color=BARC, weight=700)),
                      (f" best possible ({ceil:.2f})", dict(color=MUTED))], size=12)
    f.h = 460
    return f


def fig_busy(W, numbers, dets=CODED):
    from svgfig import Figure, MUTED
    b = numbers["blockrecall"]["per_detector"]
    dets = list(dets)
    f = Figure(1000, 470)
    X, PW = 170, 460
    #: "18% of cells take part" asked the reader to do arithmetic against a total the panel
    #: never gives, and "mid-sized" implies an arbitrary middle band. It is the MEASURED size:
    #: bench.py's own table records real coordinated events recruiting 6 of ~33 ROI. Say the count.
    n_roi = int(numbers["bench_n_roi"])
    cells = int(round(0.18 * n_roi))
    f.text(X, 24, f"A · events joined by {cells} of the {n_roi} cells — the usual real size",
           size=13, weight=600)
    p = f.panel(X, 36, PW, 340, (0, 1), (len(dets) - 0.5, -0.5))
    for v in (0, 0.25, 0.5, 0.75, 1.0):
        Xv = float(p.px(v))
        f.line(Xv, 36, Xv, 376, color=GRID_C)
    for i, d in enumerate(dets):
        v = b[d]["p18"]
        Y = float(p.py(i))
        xo, xi = float(p.px(v["outside"])), float(p.px(v["inside"]))
        f.line(xo, Y, xi, Y, color="#bbb", width=2)
        f.add(f"<circle cx='{xo:.1f}' cy='{Y:.1f}' r='6' fill='{INK_T}'/>")
        f.add(f"<circle cx='{xi:.1f}' cy='{Y:.1f}' r='6' fill='#d9730d'/>")
        f.text(X - 10, Y + 4, NAMES[d], size=13, anchor="end", color=INK_T)
        ch = v["chance"]
        f.line(float(p.px(ch)), Y - 9, float(p.px(ch)), Y + 9, color="#999", width=2)
    p.xaxis_values([0, 0.25, 0.5, 0.75, 1.0], fmt="{:.0%}", label="share of planted events found")
    X2, PW2 = 720, 240
    f.text(X2, 24, "B · false alarms in the busy stretch", size=13, weight=600)
    q = f.panel(X2, 36, PW2, 340, (-2, 1.3), (len(dets) - 0.5, -0.5))
    for v in (-2, -1, 0, 1):
        Xv = float(q.px(v))
        f.line(Xv, 36, Xv, 376, color=GRID_C)
    for i, d in enumerate(dets):
        cpm = b[d]["calls_per_min"]
        Y = float(q.py(i))
        xv = float(q.px(math.log10(max(cpm, 0.01))))
        f.rect(X2, Y - 7, xv - X2, 14, fill=COLORS[d])
        f.text(xv + 5, Y + 4, f"{cpm:.2f}" if cpm >= 0.01 else "under 0.01", size=11, color=INK_T)
    for k_, lab in zip((-2, -1, 0, 1), ("0.01", "0.1", "1", "10")):
        Xv = float(q.px(k_))
        f.line(Xv, 376, Xv, 381, color=MUTED)
        f.text(Xv, 394, lab, size=12, anchor="middle", color=MUTED)
    f.text(X2 + PW2 / 2, 412, "per minute (each step is ten times more)", size=12, anchor="middle",
           color=MUTED, italic=True)
    f.rich(X, 432, [("●", dict(color=INK_T, weight=700)), (" outside the busy stretch   ", dict(color=MUTED)),
                    ("●", dict(color="#d9730d", weight=700)), (" inside it   ", dict(color=MUTED)),
                    ("|", dict(color="#999", weight=700)), (" what calling at random would find inside", dict(color=MUTED))],
           size=12)
    f.h = 450
    return f


# ----------------------------------------------------------------------- figures: the counting rule
COUNT_C = "#8a6d3b"
QUIET_C, BUSY_C = INK_T, "#d9730d"


def fig_count_rule(W):
    """The rule's steps, on the same two simulated minutes every algorithm figure uses."""
    from svgfig import Figure, MUTED, nice_ticks
    sim, C = W["sim"], W["count"]
    bw = C["fig_bin"]
    x = C["one_bar"][f"{bw:g}"]
    ev = sim["event"]
    f = Figure(1000, 700)
    f.text(20, 26, "How the counting rule decides", size=16, weight=700)
    y = 56
    for i, s in enumerate((f"Cut the recording into bins {bw:g} seconds long.",
                           "In each bin, count how many different cells brighten at least once.",
                           f"Wherever that count reaches {x} cells, call a coordinated event. Bins side "
                           "by side that both reach it make one call.",
                           "No copies are made. The bar is the same number in every recording.")):
        f.step_badge(32, y - 4, str(i + 1), color=COUNT_C)
        y = f.para(52, y, s, width_chars=40, size=13) + 12
    for j, (key, title) in enumerate((("A", "A · a planted event (quiet cells)"),
                                      ("B", "B · a busy stretch, nothing planted"))):
        D, K = sim[key], C["demo"][key]
        X, Wd = 450 + j * 275, 240
        win = D["win"]
        f.text(X, 26, title, size=13, weight=600)
        f.text(X, 42, f"one minute, from {_clock(win[0])} into the recording", size=11, color=MUTED)
        lane = f.panel(X, 52, Wd, 50, win, (0, 1))
        if key == "A":
            ok = _found(K["calls"], ev["time"])
            lane.down_triangle(ev["time"], 64, color=GREEN if ok else RED, size=12)
        for on, wd in K["calls"]:
            lane.span(on, on + max(wd, 0.0), row_y=78, row_h=16, color=COUNT_C)
        n_calls = sum(1 for on, wd in K["calls"] if on + wd >= win[0] and on <= win[1])
        f.text(X + Wd, 116, _plural(n_calls, "call"), size=12, anchor="end", color=MUTED)
        r = f.panel(X, 122, Wd, 178, win, (0, 1))
        r.raster(_by_activity(D["trains"]), width=1.1)
        ymax = max(10, x + 3)
        p = f.panel(X, 352, Wd, 200, win, (0, ymax))
        p.bars(_arr(K["t"]), _arr(K["y"]), color="#cdb99a", width_frac=0.85)
        p.hline(x, color=BARC, width=1.8, dash="5 4")
        p.yaxis(nice_ticks(0, ymax, 4), fmt="{:g}", grid=True)
        if j == 0:
            # named above the panel, never on it (Tony, 2026-09-16: no text on the data)
            f.rich(X, 320, [("▬ ", dict(color="#cdb99a", weight=700)),
                            (f"different cells in each {bw:g} s bin", dict(color=MUTED))], size=11)
            f.rich(X, 336, [("- - ", dict(color=BARC, weight=700)),
                            (f"the bar: {x} cells, in every recording", dict(color=MUTED))], size=11)
            p.ylabel("cells", lines=["different cells", f"in each {bw:g} s bin"], dx=40)
            r.ylabel(f"{sim['n_roi']} cells", dx=14)
            f.text(X - 8, 72, "planted", size=11, anchor="end", color=MUTED)
            f.text(X - 8, 91, "calls", size=11, anchor="end", color=MUTED)
        p.xaxis_time(offset=win[0], target=4, label="seconds from the start of this minute")
    xx, ky = 460, 625
    for col, lab in ((GREEN, "planted event, found"), (RED, "planted event, missed")):
        f.rich(xx, ky, [("▼ ", dict(color=col, weight=700)), (lab, dict(color=MUTED))], size=12)
        xx += 16 + 7.0 * len(lab) + 14
    f.h = ky + 20
    return f


def fig_count_bar(W):
    """What the bar does to the score, and to calls where nothing was planted."""
    from svgfig import Figure, MUTED
    C = W["count"]
    bw = C["fig_bin"]
    xs = C["xs"]
    B = C["bench"]
    regs = (("baseline_quiet", QUIET_C, "quiet background"), ("baseline_busy", BUSY_C, "busy background"))
    # Panel B sits far enough right that A's margin labels ("CoactDetect, busy") end before B's
    # axis label begins; the first draft ran one into the other.
    f = Figure(1030, 470)
    for j, (key, title, ylim, ticks, ylab, scale) in enumerate((
            ("f1", "A · the overall score, bar by bar", (0, 1), [0, 0.25, 0.5, 0.75, 1.0], "overall score", 1),
            ("empty", "B · how much of the empty busy stretch it calls", (0, 100), [0, 25, 50, 75, 100],
             "percent of the stretch", 100))):
        X, PW, PH = (80, 330, 300) if j == 0 else (640, 300, 300)
        f.text(X, 24, title, size=13, weight=600)
        p = f.panel(X, 40, PW, PH, (xs[0] - 0.5, xs[-1] + 0.5), ylim)
        p.yaxis(ticks, fmt="{:g}", grid=True, label=ylab, dx=44)
        for reg, col, _ in regs:
            vals = [scale * np.nan_to_num(B[reg][f"count|{bw:g}|{x}"][key]) for x in xs]
            p.curve(xs, vals, color=col, width=2)
            p.dots(xs, vals, color=col, r=3.2)
            bx = C["best"][f"{bw:g}"][reg]
            v = scale * np.nan_to_num(B[reg][f"count|{bw:g}|{bx}"][key])
            f.add(f"<circle cx='{float(p.px(bx)):.1f}' cy='{float(p.py(v)):.1f}' r='8' fill='none' "
                  f"stroke='{col}' stroke-width='1.8'/>")
        # the references sit in the margin to the right of the frame, never over the curves
        cc = COLORS["coact"]
        if key == "f1":
            for reg, word in (("baseline_quiet", "quiet"), ("baseline_busy", "busy")):
                v = B[reg]["coact"]["f1"]
                p.hline(v, color=cc, width=1.4, dash="4 4")
                f.text(X + PW + 6, float(p.py(v)) + 4, f"CoactDetect, {word}", size=11, color=cc)
        else:
            v = 100 * max(B["baseline_busy"]["coact"]["empty"], B["baseline_busy"]["loco"]["empty"])
            p.hline(v, color=cc, width=1.4, dash="4 4")
            f.text(X + PW + 6, float(p.py(v)) - 10, "CoactDetect", size=11, color=cc)
            f.text(X + PW + 6, float(p.py(v)) + 4, "and LoCo", size=11, color=cc)
        p.xaxis_values(xs, label=f"the bar: different cells in one {bw:g} s bin")
    f.rich(80, 430, [("● ", dict(color=QUIET_C, weight=700)), ("quiet background   ", dict(color=MUTED)),
                     ("● ", dict(color=BUSY_C, weight=700)), ("busy background   ", dict(color=MUTED)),
                     ("◯ ", dict(color=MUTED, weight=700)), ("the bar with the best score   ", dict(color=MUTED)),
                     ("- - ", dict(color=COLORS["coact"], weight=700)),
                     ("programs that judge chance from the minutes around each moment", dict(color=MUTED))],
           size=12)
    f.h = 450
    return f


def fig_count_slices(W):
    """One dot per untreated real recording: the bar its own chance needs."""
    from svgfig import Figure, MUTED
    C = W["count"]
    bw = C["fig_bin"]
    x1 = C["one_bar"][f"{bw:g}"]
    R = C["real"]
    f = Figure(1000, 470)
    X, Y, PW, PH = 110, 44, 600, 320
    f.text(X, 24, f"{len(R)} untreated recordings, one dot each", size=13, weight=600)
    p = f.panel(X, Y, PW, PH, (-2.5, 1.0), (0, 11))
    p.yaxis([0, 2, 4, 6, 8, 10], fmt="{:g}", grid=True)
    p.ylabel("cells", lines=[f"cells needed in one {bw:g} s bin so that", "chance reaches it less than once",
                             "every 10 minutes"], dx=62)
    rate_q = C["block_rate_per_min"]["baseline_quiet"]
    Xb = float(p.px(math.log10(rate_q)))
    f.line(Xb, Y, Xb, Y + PH, color=MUTED, width=1, dash="2 3")
    f.text(Xb, Y - 6, "the simulated busy stretch", size=11, anchor="middle", color=MUTED)
    for r in R:
        need = r[f"need|{bw:g}"]
        if need is None or r["rate"] <= 0:
            continue
        col = BUSY_C if need > x1 else "#7a7a7a"
        p.dots([math.log10(r["rate"])], [need], color=col, r=4.2, opacity=0.75)
    p.hline(x1, color=BARC, width=1.6, dash="5 4")
    f.text(X + PW + 8, float(p.py(x1)) - 6, "the one bar that did best", size=11, color=INK_T)
    f.text(X + PW + 8, float(p.py(x1)) + 8, f"on simulated recordings: {x1} cells", size=11, color=INK_T)
    for v, lab in ((-2, "0.01"), (-1, "0.1"), (0, "1"), (1, "10")):
        Xv = float(p.px(v))
        f.line(Xv, Y + PH, Xv, Y + PH + 5, color=MUTED)
        f.text(Xv, Y + PH + 18, lab, size=12, anchor="middle", color=MUTED)
    f.text(X + PW / 2, Y + PH + 36, "events per cell per minute (each step is ten times more)", size=12,
           anchor="middle", color=MUTED, italic=True)
    f.rich(X, 430, [("● ", dict(color=BUSY_C, weight=700)),
                    (f"a bar of {x1} lets chance through   ", dict(color=MUTED)),
                    ("● ", dict(color="#7a7a7a", weight=700)),
                    (f"a bar of {x1} is enough, or more than enough", dict(color=MUTED))], size=12)
    f.h = 450
    return f


def fig_count_published(W):
    """The published slice rule, run on cells that fire at random and independently."""
    from svgfig import Figure, MUTED
    P = W["count"]["published"]
    e = P["eddleston"]
    shades = {"7": "#c9b79c", "13.4": "#5a4527"}
    words = {"7": "7 events per cell per hour, the slowest rate these papers report",
             "13.4": "13.4 events per cell per hour, the 2026 paper's rate"}
    f = Figure(1000, 460)
    for j, (key, title, ylim, ticks, ylab, rep) in enumerate((
            ("mse_per_cell_h", "A · synchronized events per cell per hour", (0, 4), [0, 1, 2, 3, 4],
             "events per cell per hour", e["mse"]),
            ("cells_per", "B · cells in each synchronized event", (2, 4.5), [2, 3, 4], "cells in each event",
             e["cells_per"]))):
        X, PW, PH = 90 + j * 470, 330, 290
        f.text(X, 24, title, size=13, weight=600)
        p = f.panel(X, 40, PW, PH, (PUB_CELLS[0], PUB_CELLS[-1]), ylim)
        # the field sizes the 2026 paper reports, shaded behind everything
        f.rect(float(p.px(e["field_lo"])), 40, float(p.px(e["field_hi"])) - float(p.px(e["field_lo"])), PH,
               fill="#f1ede6")
        p.yaxis(ticks, fmt="{:g}", grid=True, label=ylab, dx=40)
        for rate, rows in P["curves"].items():
            p.curve([r_["cells"] for r_ in rows], [r_[key] for r_ in rows], color=shades.get(rate, MUTED), width=2)
        p.hline(rep, color=RED, width=1.6, dash="5 4", x0=e["field_lo"], x1=e["field_hi"])
        f.text(X + PW + 6, float(p.py(rep)) - 4, "reported,", size=11, color=RED)
        f.text(X + PW + 6, float(p.py(rep)) + 10, "2026 paper", size=11, color=RED)
        p.xaxis_values([4, 8, 13, 20, 29], label="cells in view")
    spans = []
    for rate in P["curves"]:
        spans += [("▬ ", dict(color=shades.get(rate, MUTED), weight=700)),
                  (words.get(rate, f"{float(rate):g} events per cell per hour") + "   ", dict(color=MUTED))]
    f.rich(90, 400, spans, size=12)
    f.rich(90, 420, [("▮ ", dict(color="#e2dbcf", weight=700)),
                     (f"{e['field_lo']} to {e['field_hi']} cells in view, as the 2026 paper reports   ",
                      dict(color=MUTED)),
                     ("- - ", dict(color=RED, weight=700)), ("what that paper reports", dict(color=MUTED))],
           size=12)
    f.h = 440
    return f


PERIOD_COLORS = {"baseline": "#bcc3cc", "senktide": "#c96f2a", "TTX": "#4a86c5", "high K+": "#7d7d7d"}


def _period_lane(f, p, c, Y):
    """The treatment bar and the lab's analysis windows, above the call lanes."""
    for name, r0, r1 in c["regions"]:
        if r1 >= c["win"][0] and r0 <= c["win"][1]:
            p.span(max(r0, c["win"][0]), min(r1, c["win"][1]), row_y=Y, row_h=8,
                   color=PERIOD_COLORS.get(name, "#9e9e9e"))
    for w0, w1 in c["windows"]:
        if w1 >= c["win"][0] and w0 <= c["win"][1]:
            p.span(max(w0, c["win"][0]), min(w1, c["win"][1]), row_y=Y + 11, row_h=4, color="#333")


def _closeup(f, c, X, Y, PW, *, title, dets=ALL10, raster_h=180, show_weak=False, stripe_marks=True,
             label_names=True):
    from svgfig import MUTED
    win = c["win"]
    f.text(X, Y, title, size=13, weight=600)
    top = Y + 10
    pl = f.panel(X, top, PW, 18, win, (0, 1), frame=False)
    _period_lane(f, pl, c, top + 2)
    y = top + 24
    lp = f.panel(X, y, PW, len(dets) * 14 + 4, win, (0, 1))
    for i, d in enumerate(dets):
        ry = y + 3 + i * 14
        weak = {round(on, 2) for on, _, _ in c["weak"].get(d, [])}
        for on, wd in c["calls"][d]:
            isweak = show_weak and round(on, 2) in weak
            lp.span(on, on + max(wd, 0.0), row_y=ry, row_h=10, color=COLORS[d], min_px=2.5)
            if isweak:
                a = float(lp.px(on)) - 3
                b = float(lp.px(on + max(wd, 0.0))) + 3
                f.rect(a, ry - 2, max(b - a, 6), 14, stroke=RED, width=1.6)
        if label_names:
            n = sum(1 for on, _ in c["calls"][d] if win[0] <= on <= win[1])
            f.text(X - 8, ry + 9, f"{NAMES[d]} · {_plural(n, 'call')}", size=11, anchor="end", color=MUTED)
    y += len(dets) * 14 + 10
    sp = f.panel(X, y, PW, 16, win, (0, 1), frame=False)
    if stripe_marks:
        for s_ in c["stripes"]:
            sp.down_triangle(s_["t"] + 0.5, y + 8, color=INK_T, size=10)
        f.text(X - 8, y + 12, "stripes you can see", size=11, anchor="end", color=MUTED)
    y += 18
    r = f.panel(X, y, PW, raster_h, win, (0, 1))
    r.raster(c["trains"], width=1.2)
    r.xaxis_time(offset=c["anchor"], target=6,
                 label=f"minutes from the start of {c['label']}")
    f.text(X - 8, y + raster_h / 2, f"{c['stream'] == 'fast' and 'brief' or 'long'} events",
           size=11, anchor="end", color=MUTED)
    f.text(X - 8, y + raster_h / 2 + 14, _plural(c["n_roi"], "cell"), size=11, anchor="end", color=MUTED)
    return y + raster_h + 44


GROUP_WORDS_PLAIN = {"DI": "females, one stage of the cycle", "MALE": "males",
                     "ORX": "males, testes removed", "OVX": "females, ovaries removed"}


def fig_real_overview(W, label, stream):
    """One figure per drug per kind of event: four recordings, one from each group of mice.

    Drawn here rather than reused from the first review, whose versions carried a lane for each
    learned model. Those left this document (Tony, 2026-09-16), and redrawing brings these
    under the same raster rules as every other figure."""
    from svgfig import Figure, MUTED
    ov = {k: v for k, v in W["real"]["overview"].items()
          if v["label"] == label and v["stream"] == stream}
    order = [k for g in ("DI", "MALE", "ORX", "OVX") for k in ov if ov[k]["group"] == g]
    a0 = 0.0
    lo = min(ov[k]["ext"][0] - ov[k]["anchor"] for k in order)
    hi = max(ov[k]["ext"][1] - ov[k]["anchor"] for k in order)
    span = (lo - 30, hi + 30)
    L, PW = 180, 760
    f = Figure(1000, 40 + len(order) * 260)
    y = 30
    for k in order:
        c = ov[k]
        f.rich(L - 172, y, [(c["group"], dict(weight=700)),
                            (f" · {GROUP_WORDS_PLAIN.get(c['group'], '')}", dict(color=MUTED))],
               size=12)
        pl = f.panel(L, y + 6, PW, 16, span, (0, 1), frame=False)
        for name, r0, r1 in c["regions"]:
            pl.span(r0 - c["anchor"], r1 - c["anchor"], row_y=y + 8, row_h=7,
                    color=PERIOD_COLORS.get(name, "#9e9e9e"))
        for w0, w1 in c["windows"]:
            pl.span(w0 - c["anchor"], w1 - c["anchor"], row_y=y + 18, row_h=3, color="#333")
        yy = y + 26
        lp = f.panel(L, yy, PW, len(CODED) * 12 + 4, span, (0, 1))
        for i, d in enumerate(CODED):
            ry = yy + 3 + i * 12
            for on, wd in c["calls"][d]:
                lp.span(on - c["anchor"], on + wd - c["anchor"], row_y=ry, row_h=8,
                        color=COLORS[d], min_px=2)
            f.text(L - 8, ry + 8, f"{NAMES[d]} · {_plural(c['in_window'][d], 'call')}", size=10,
                   anchor="end", color=MUTED)
        yy += len(CODED) * 12 + 8
        r = f.panel(L, yy, PW, max(60, 3 * c["n_roi"]), span, (0, 1))
        r.raster([np.asarray(v, float) - c["anchor"] for v in c["trains"]], width=1.0)
        f.text(L - 8, yy + 14, _plural(c["n_roi"], "cell"), size=10, anchor="end", color=MUTED)
        y = yy + max(60, 3 * c["n_roi"]) + 26
        if k == order[-1]:
            r.xaxis_time(target=6, label=f"minutes from the moment {label} arrives")
            y += 34
    f.rich(L, y, [("▬ ", dict(color="#bcc3cc", weight=700)), ("before the drug   ", dict(color=MUTED)),
                  ("▬ ", dict(color=PERIOD_COLORS.get(label, "#9e9e9e"), weight=700)),
                  (f"{label}   ", dict(color=MUTED)),
                  ("▬ ", dict(color="#7d7d7d", weight=700)), ("high potassium   ", dict(color=MUTED)),
                  ("▬ ", dict(color="#333", weight=700)),
                  ("the stretches the lab studies; the count beside each name is that program's "
                   "calls inside them", dict(color=MUTED))], size=11)
    f.h = y + 20
    return f


def fig_problem(W):
    from svgfig import Figure
    c = W["real"]["close"]["problem"]
    f = Figure(1000, 420)
    _closeup(f, c, 190, 20, 780, title="", dets=CODED, raster_h=230, stripe_marks=False)
    f.h = 420
    return f


def fig_eye(W, figs_real="18 to 21", dets=CODED):
    from svgfig import Figure, MUTED
    R = W["real"]
    C = R["close"]
    f = Figure(1000, 1500)
    y = 24
    y = _closeup(f, C["outside"], 200, y, 770, dets=dets,
                 title="A · clear stripes just outside the analysis window (black line)")
    y = _closeup(f, C["busy"], 200, y + 10, 770, dets=dets,
                 title="B · a busy stretch inside the analysis window, with no stripe that stands out")
    y = _closeup(f, C["weak"], 200, y + 10, 770, show_weak=True, dets=dets,
                 title="C · calls with no stripe under them (red box: 3 or fewer cells line up)")
    # D: the tallies
    y += 10
    f.text(200, y, f"D · all {R['n_recordings']} recordings of Figures {figs_real}, both kinds of events",
           size=13, weight=600)
    T = R["tally"]
    dets = list(dets)
    p = f.panel(200, y + 30, 330, len(dets) * 22, (0, 1), (len(dets) - 0.5, -0.5))
    q = f.panel(640, y + 30, 330, len(dets) * 22, (0, 1), (len(dets) - 0.5, -0.5))
    f.text(200, y + 22, f"share of the {R['n_in']} clear stripes inside the windows it called", size=12,
           color=MUTED)
    f.text(640, y + 22, "share of its calls with 3 or fewer cells lined up", size=12, color=MUTED)
    for i, d in enumerate(dets):
        t = T[d]
        Y = float(p.py(i))
        v1 = t["called_in"] / max(t["stripes_in"], 1)
        v2 = t["weak"] / max(t["calls"], 1)
        f.rect(200, Y - 7, float(p.px(v1)) - 200, 14, fill=COLORS[d])
        f.text(float(p.px(v1)) + 5, Y + 4, f"{v1:.0%}", size=11)
        f.rect(640, Y - 7, float(q.px(v2)) - 640, 14, fill=COLORS[d])
        f.text(float(q.px(v2)) + 5, Y + 4, f"{v2:.0%} of {t['calls']:,}", size=11)
        f.text(190, Y + 4, NAMES[d], size=12, anchor="end")
    p.xaxis_values([0, 0.5, 1], fmt="{:.0%}")
    q.xaxis_values([0, 0.5, 1], fmt="{:.0%}")
    y2 = y + 30 + len(dets) * 22 + 40
    f.rich(200, y2, [("▼ ", dict(color=INK_T, weight=700)),
                     (f"a clear stripe: at least {R['stripe_frac']:.0%} of the cells (and at least {MIN_CELLS}) "
                      f"start an event within {R['stripe_s']:g} second, and at least twice as many as in the "
                      f"busiest seconds around it", dict(color=MUTED))], size=12)
    f.rich(200, y2 + 20, [("▬ ", dict(color="#333", weight=700)), ("the analysis windows the lab marks   ", dict(color=MUTED)),
                          ("▬ ", dict(color="#bcc3cc", weight=700)), ("baseline   ", dict(color=MUTED)),
                          ("▬ ", dict(color="#c96f2a", weight=700)), ("senktide   ", dict(color=MUTED)),
                          ("▬ ", dict(color="#4a86c5", weight=700)), ("TTX   ", dict(color=MUTED)),
                          ("▬ ", dict(color="#7d7d7d", weight=700)), ("high potassium", dict(color=MUTED))], size=12)
    f.h = y2 + 36
    return f


def _render(figs: dict, work: Path, dest: Path) -> dict:
    """Write each figure as SVG, and flatten it to PNG through Playwright chromium."""
    from playwright.sync_api import sync_playwright
    out = {}
    with sync_playwright() as pw:
        br = pw.chromium.launch()
        page = br.new_page(device_scale_factor=2, viewport={"width": 1100, "height": 900})
        for name, f in figs.items():
            svg = f.svg()
            (work / f"{name}.svg").write_text(svg, encoding="utf-8")
            page.set_content(f"<meta charset='utf-8'><body style='margin:0;background:#fff'>{svg}</body>")
            page.locator("svg").first.screenshot(path=str(dest / f"{name}.png"))
            out[name] = svg
    return out


def stage_figures(work: Path, review: Path) -> None:
    W = json.loads((work / "plain.json").read_text())
    numbers = json.loads((review / "measurements" / "numbers.json").read_text())
    figs = {"fig_orient": fig_orient(W), "fig_problem": fig_problem(W), "fig_chance": fig_chance(W),
            "fig_chance_steps": fig_chance_steps(W), "fig_shift_shuffle": fig_shift_shuffle(W, numbers)}
    for d in CODED:
        figs[f"fig_alg_{d}"] = fig_algorithm(W, d)
    figs.update({"fig_simulator": fig_simulator(W, numbers), "fig_grading": fig_grading(W, numbers),
                 "fig_scores": fig_scores(W, numbers), "fig_busy": fig_busy(W, numbers),
                 "fig_count_rule": fig_count_rule(W), "fig_count_bar": fig_count_bar(W),
                 "fig_count_slices": fig_count_slices(W), "fig_count_published": fig_count_published(W)})
    for name, label, stream in (("real_ttx_brief", "TTX", "fast"), ("real_ttx_long", "TTX", "slow"),
                                ("real_senk_brief", "senktide", "fast"),
                                ("real_senk_long", "senktide", "slow")):
        figs[name] = fig_real_overview(W, label, stream)
    figs["fig_eye"] = fig_eye(W)
    # the learned models live in their own document now (Tony, 2026-09-16)
    figs["learned_network"] = fig_network(W)
    figs["learned_scores"] = fig_scores(W, numbers, dets=LEARNED4)
    figs["learned_busy"] = fig_busy(W, numbers, dets=LEARNED4)
    _render(figs, work, work.parent)
    print("  figures:", ", ".join(figs))


# ----------------------------------------------------------------------- page
#: The first review's real-recording figures, reused as they are: one recording per group
#: of mice, per drug, per kind of event.
OLD_REAL = (("real_ttx_brief", "fig15_real_TTX_fast.png"), ("real_ttx_long", "fig16_real_TTX_slow.png"),
            ("real_senk_brief", "fig17_real_senktide_fast.png"), ("real_senk_long", "fig18_real_senktide_slow.png"))


def _pct(v, nd=0):
    return f"{100 * v:.{nd}f}%"


def _round_disagreement(N) -> dict:
    """How many detectors' rounds picked different settings, and locust's spread.

    The document has to answer "why not just keep the tuned setting?", and the honest
    answer is that there is no single one: each round picks its own, and most detectors'
    rounds disagree. Derived here rather than written into the prose so the claim cannot
    outlive the measurement.
    """
    picks = {d: N[f"opt_quiet_{d}"]["picks"] for d in CODED}
    lo, hi = (sorted(picks["cicada"], key=lambda s: float(s.replace(",", "")))[i] for i in (0, -1))
    return dict(n_setting_disagree=sum(1 for p in picks.values() if len(set(p)) > 1),
                cicada_pick_lo=lo, cicada_pick_hi=hi)


def _count_values(W) -> dict:
    """The counting section's numbers. Every one is read off the `count` stage, so the prose cannot
    drift from the measurement; the published papers' own figures are the only constants."""
    C = W["count"]
    bw = f"{C['fig_bin']:g}"
    B = C["bench"]
    q, b = "baseline_quiet", "baseline_busy"
    bq, bb, one = C["best"][bw][q], C["best"][bw][b], C["one_bar"][bw]
    f2 = lambda v: f"{v:.2f}"                                         # noqa: E731
    pc = lambda v: f"{100 * v:.0f}%" if v >= 0.01 else f"{100 * v:.1f}%"   # noqa: E731
    # for "at least X%": round DOWN, or 99.5% prints as "at least 100%"
    floor_pc = lambda v: f"{math.floor(100 * v)}%"                       # noqa: E731
    R = C["real"]
    rate = np.array([r["rate"] for r in R])
    cells = np.array([r["n_roi"] for r in R])
    need = np.array([np.nan if r[f"need|{bw}"] is None else r[f"need|{bw}"] for r in R], float)
    i1 = C["real_xs"].index(one)
    per10 = np.array([r[f"chance_per10|{bw}"][i1] for r in R])
    e = C["published"]["eddleston"]
    ch = e["chance"][str(e["field"])]
    ten = max(B[reg][f"count|10|{C['best']['10'][reg]}"]["empty"] for reg in (q, b))
    ten_min = min(B[reg][f"count|10|{C['best']['10'][reg]}"]["empty"] for reg in (q, b))
    return dict(
        cnt_bin=bw, cnt_x_lo=C["xs"][0], cnt_x_hi=C["xs"][-1], cnt_one_bar=one,
        cnt_best_quiet=bq, cnt_best_busy=bb,
        cnt_f1_best_quiet=f2(B[q][f"count|{bw}|{bq}"]["f1"]), cnt_f1_best_busy=f2(B[b][f"count|{bw}|{bb}"]["f1"]),
        cnt_f1_one_quiet=f2(B[q][f"count|{bw}|{one}"]["f1"]), cnt_f1_one_busy=f2(B[b][f"count|{bw}|{one}"]["f1"]),
        cnt_quiet_bar_on_busy=f2(B[b][f"count|{bw}|{bq}"]["f1"]),
        cnt_empty_best_quiet=pc(B[q][f"count|{bw}|{bq}"]["empty"]),
        cnt_empty_best_busy=pc(B[b][f"count|{bw}|{bb}"]["empty"]),
        cnt10_empty=floor_pc(ten_min), cnt10_empty_max=pc(ten),
        cnt_coact_f1_quiet=f2(B[q]["coact"]["f1"]), cnt_coact_f1_busy=f2(B[b]["coact"]["f1"]),
        **{f"cnt_{d}_empty_busy": pc(B[b][d]["empty"]) for d in CODED},
        herb_f1_quiet=f2(B[q]["herbison|2"]["f1"]), herb_f1_busy=f2(B[b]["herbison|2"]["f1"]),
        herb_empty_busy=floor_pc(min(B[q]["herbison|2"]["empty"], B[b]["herbison|2"]["empty"])),
        cnt_n_real=len(R), cnt_draws=CHANCE_DRAWS,
        cnt_rate_min=f"{rate.min():.3f}", cnt_rate_max=f"{rate.max():.0f}",
        cnt_rate_p10=f"{np.percentile(rate, 10):.2f}", cnt_rate_p90=f"{np.percentile(rate, 90):.1f}",
        cnt_cells_min=int(cells.min()), cnt_cells_max=int(cells.max()),
        cnt_need_min=int(np.nanmin(need)), cnt_need_max=int(np.nanmax(need)),
        cnt_n_loose=int(np.sum(need > one)), cnt_loose_max=f"{per10.max():.0f}",
        cnt_n_strict=int(np.sum(need <= 3)),
        cnt_block_slower=int(np.sum(rate < C["block_rate_per_min"][q])),
        pub_cells_lo=PUB_CELLS[0], pub_cells_hi=PUB_CELLS[-1], pub_hours=f"{PUB_HOURS:g}",
        pub_rep_rate=f"{e['rate']:g}", pub_rep_mse=f"{e['mse']:g}", pub_rep_cells=f"{e['cells_per']:g}",
        pub_rep_share=f"{e['share']:g}", pub_field=e["field"], pub_field_lo=e["field_lo"],
        pub_field_hi=e["field_hi"],
        pub_chance_mse=f"{ch['mse_per_cell_h']:.1f}", pub_chance_cells=f"{ch['cells_per']:.1f}")


def _display_values(W, N) -> dict:
    """Every number the page quotes, already worded. The template names them {{T.key}}."""
    sim, toys, tube, real = W["sim"], W["toys"], W["tube"], W["real"]
    st = sim["settings"]
    per_hour = lambda mhz: f"{mhz * 3.6:.0f}"                           # noqa: E731
    T = dict(
        n_cells_sim=sim["n_roi"], event_cells=sim["event"]["n_part"],
        event_pct=round(100 * sim["event"]["n_part"] / sim["n_roi"]),
        coact_obs=int(sim["chance_coact"]["observed"]), coact_bar_quiet=f"{sim['chance_coact']['bar']:.1f}",
        coact_bar_busy=f"{sim['chance_coact_B']['bar']:.0f}", coact_obs_busy=int(sim["chance_coact_B"]["observed"]),
        busy_max=int(np.nanmax(_arr(sim["B"]["coact"]["y"]))),
        bursty_shift=_pct(toys["bursty"]["p_shift"], 1), bursty_shuffle=_pct(toys["bursty"]["p_shuffle"], 0),
        even_shift=_pct(toys["even"]["p_shift"], 0), even_shuffle=_pct(toys["even"]["p_shuffle"], 1),
        even_cells=toys["even"]["observed"], bursty_cells=toys["bursty"]["observed"],
        doubles_real=math.floor(N["sur_fast_doubles"]["real"] + 0.5),
        doubles_shift=math.floor(N["sur_fast_doubles"]["shift"] + 0.5),
        doubles_shuffle=math.floor(N["sur_fast_doubles"]["shuffle"] + 0.5),
        n6_real=f"{100 * N['sur_fast_n6']['real']:.2f}%", n6_shift=f"{100 * N['sur_fast_n6']['shift']:.2f}%",
        n6_shuffle=f"{100 * N['sur_fast_n6']['shuffle']:.2f}%", n_baselines=N["sur_fast_n_recordings"],
        real_over_shift_8=N["sur_fast_real_over_shift"]["n8"],
        rate_ex=f"{st['rate']['excess_threshold_hz']:g}", coact_ns=st["coact"]["n_surrogates"],
        loco_ns=st["loco"]["n_surrogates"], sce_ns=st["sce"]["n_surrogates"],
        cicada_ns=st["cicada"]["n_surrogates"], cicada_on=f"{st['cicada']['active_duration_sec']:g}",
        sync_tau=f"{st['sync']['tau_max']:g}", sync_bar=f"{st['sync']['C_threshold']:g}",
        sync_max3=f"{2 / (sim['n_roi'] - 1):.2f}", sync_max_event=f"{(sim['event']['n_part'] - 1) / (sim['n_roi'] - 1):.2f}",
        tube_threshold=f"{tube['threshold']:.2f}", tube_params=f"{tube['n_params']:,}",
        tube_widen=f"{tube['widen_s']:g}", tube_centre_lo=f"{min(tube['centre_s']):.1f}",
        tube_centre_hi=f"{max(tube['centre_s']):.1f}",
        quiet_per_hour=per_hour(N["bench"]["quiet_mhz"]), busy_per_hour=per_hour(N["bench"]["busy_mhz"]),
        hot_per_hour=per_hour(N["bench"]["hot_rate_mhz"]), n_planted=N["bench"]["n_planted"],
        n_decoys=N["bench"]["n_distractors"], minutes=f"{N['bench']['minutes']:g}",
        hot_from=f"{N['bench']['hot_min'][0]:g}", hot_to=f"{N['bench']['hot_min'][1]:g}",
        min_sep_min=f"{N['bench']['min_sep_s'] / 60:g}", jitter=f"{N['bench']['jitter_s']:g}",
        real_p25_per_hour=per_hour(N["gen_real_rate_percentiles_mhz"]["p25"]),
        real_p75_per_hour=per_hour(N["gen_real_rate_percentiles_mhz"]["p75"]),
        tol=f"{N['tol_s']:g}", ceiling=f"{N['f1_ceiling']:.2f}",
        n_recordings_scored=N["rounds"]["n_recordings"], n_tests=N["rounds"]["n_folds"],
        n_choose=N["rounds"]["n_choose"], per_test=N["rounds"]["per_fold"],
        sce_fair_quiet=f"{N['sce_rescore']['quiet']['full_bin']['tuned_f1']:.2f}",
        block_recordings=N["blockrecall"]["n_recordings"], block_hot3=f"{N['blockrecall_hot3x']['block_mhz'] * 3.6:.0f}",
        n_stripes=real["n_stripes"], n_stripes_in=real["n_in"], n_stripes_out=real["n_stripes"] - real["n_in"],
        n_few=real["n_few"], n_few_out=real["n_few_out"], n_real_recordings=real["n_recordings"],
        stripe_pct=_pct(real["stripe_frac"]), weak_cells=real["weak_cells"],
        #: Event sizes as CELL COUNTS, not fractions. Tony, 2026-09-16: a percentage of a
        #: total the reader does not have in front of them is arithmetic homework, and
        #: "mid-sized" hid that 18% is the measured real size (bench.py: 6 of ~33 ROI).
        bench_n_roi=N["bench_n_roi"],
        big_cells=int(round(0.30 * N["bench_n_roi"])),
        mid_cells=int(round(0.18 * N["bench_n_roi"])),
        small_cells=int(round(0.10 * N["bench_n_roi"])),
        n_coded=len(CODED), n_learned=len(LEARNED4),
        #: The rounds do not yield a deployable setting: they yield one per round, and most
        #: detectors' rounds disagree. Tony asked why the stored value is not replaced by
        #: "the tuned one" — this is the answer, and it has to come from the data.
        **_round_disagreement(N),
    )
    for reg, tag in (("baseline_quiet", "q"), ("baseline_busy", "b")):
        for d in CODED + LEARNED4:
            T[f"f1{tag}_{d}"] = f"{N[f'perf_{reg}_{d}']['f1']:.2f}"
    for d in CODED + LEARNED4:
        b = N["blockrecall"]["per_detector"][d]
        T[f"out_{d}"] = _pct(b["p18"]["outside"])
        T[f"in_{d}"] = _pct(b["p18"]["inside"])
        T[f"fa_{d}"] = f"{b['calls_per_min']:.1f}"
        t = real["tally"][d]
        T[f"stripe_in_{d}"] = _pct(t["called_in"] / max(t["stripes_in"], 1))
        T[f"weak_{d}"] = _pct(t["weak"] / max(t["calls"], 1))
        T[f"busy_{d}"] = W.get("busy_counts", {}).get(d, "")
    for d, v in N["prob_a"]["counts"].items():
        T[f"prob_{d}"] = v
    T["prob_minutes"] = f"{N['prob_a']['minutes'][1] - N['prob_a']['minutes'][0]:g}"
    # the first review's real-recording counts, for the captions of its four figures
    for label in ("TTX", "senktide"):
        for stream in ("fast", "slow"):
            for g, v in N.get(f"real_{label}_{stream}", {}).items():
                for d, n in v["calls_in_windows"].items():
                    T[f"rw_{label}_{stream}_{g}_{d}"] = n
                for w, mhz in v["window_rate_mhz"].items():
                    T[f"rate_{label}_{stream}_{g}_{w.replace(' ', '').replace('+', 'plus')}"] = f"{mhz * 3.6:.0f}"
    # how bunched the busiest cells are, counted in 30 s stretches: 1 means as even as
    # chance allows. The simulator's busiest cells are the defect Section 7 owns up to.
    T["bunch_real_busy"] = f"{N['gen_real_fano_by_rate']['over_100']['w30']:.1f}"
    T["bunch_sim_busy"] = f"{N['gen_fitted_fano_by_rate']['over_100']['w30']:.1f}"
    T["bunch_real_quiet"] = f"{N['gen_real_fano_by_rate']['under_50']['w30']:.1f}"
    T["bunch_sim_quiet"] = f"{N['gen_fitted_fano_by_rate']['under_50']['w30']:.1f}"
    st_ = W["toys"]["steps"]
    T["steps_cells"] = 6
    T["steps_observed"] = st_["observed"]
    T["steps_copies"] = f"{st_['n_copies']:,}"
    T["steps_bin"] = f"{st_['bin'][1] - st_['bin'][0]:g}"
    T["steps_share"] = (f"{st_['share_at_least'] * 100:.0f}%" if st_["share_at_least"] >= 0.01
                        else "fewer than 1%")
    T["problem_n_roi"] = real["close"]["problem"]["n_roi"]
    T["orient_n_roi"] = real["close"]["orient"]["n_roi"]
    T["orient_n_stripes"] = len(real["close"]["orient"]["stripes"])
    T["orient_minutes"] = f"{(real['close']['orient']['win'][1] - real['close']['orient']['win'][0]) / 60:g}"
    T["orient_biggest"] = max((s_["cells"] for s_ in real["close"]["orient"]["stripes"]), default=0)
    T["outside_stripe_cells"] = max((s_["cells"] for s_ in real["close"]["outside"]["stripes"]), default=0)
    for close in ("outside", "busy", "weak"):
        c = real["close"][close]
        a = c["anchor"]
        T[f"{close}_from"] = f"{(c['win'][0] - a) / 60:.1f}"
        T[f"{close}_to"] = f"{(c['win'][1] - a) / 60:.1f}"
        T[f"{close}_n_roi"] = c["n_roi"]
        T[f"{close}_n_stripes"] = len(c["stripes"])
        for d in ALL10:
            T[f"{close}_calls_{d}"] = sum(1 for on, _ in c["calls"][d] if c["win"][0] <= on <= c["win"][1])
    import datetime as _dt
    import subprocess
    try:
        sha = subprocess.run(["git", "rev-parse", "--short", "HEAD"], capture_output=True, text=True,
                             cwd=Path(__file__).resolve().parent).stdout.strip()
    except OSError:
        sha = "unknown"
    T["built"] = f"{_dt.date.today().isoformat()} from commit {sha or 'unknown'} of the project's tools"
    T.update(_count_values(W))
    return T


def stage_page(work: Path, review: Path) -> None:
    import base64
    W = json.loads((work / "plain.json").read_text())
    N = json.loads((review / "measurements" / "numbers.json").read_text())
    prose_file = work.parent / "real_prose.json"
    if not prose_file.exists():
        raise SystemExit(f"{prose_file} is missing: the sentences about real recordings live there, "
                         "not in the repo (FOUNDATIONS §5)")
    prose = json.loads(prose_file.read_text(encoding="utf-8"))
    T = _display_values(W, N)
    page = TEMPLATE.read_text(encoding="utf-8")

    def prose_rep(m):
        if m.group(1) not in prose:
            raise SystemExit(f"real_prose.json has no key {m.group(1)!r}")
        return prose[m.group(1)]
    page = re.sub(r"\{\{PROSE:([A-Za-z0-9_]+)\}\}", prose_rep, page)
    # figure numbers, in order of appearance
    order = []
    for m in re.finditer(r"\{\{FIG:([A-Za-z0-9_]+)\}\}", page):
        if m.group(1) not in order:
            order.append(m.group(1))
    num = {name: i + 1 for i, name in enumerate(order)}

    def num_rep(m):
        if m.group(1) not in num:
            raise SystemExit(f"{{{{NUM:{m.group(1)}}}}} names a figure the page never shows")
        return str(num[m.group(1)])
    page = re.sub(r"\{\{NUM:([A-Za-z0-9_]+)\}\}", num_rep, page)
    # SECTION NUMBERS ARE COUNTED, NEVER TYPED. Sections have been added, removed and
    # reordered through this review; a hard-coded "Section 8" in prose survives the move and
    # then points at the wrong thing. The key is stable, the number is derived.
    order_s = re.findall(r'<h2 id="s\d+">\{\{SEC:([A-Za-z0-9_]+)\}\}', page)
    sec = {k: i + 1 for i, k in enumerate(order_s)}

    def sec_rep(m):
        if m.group(1) not in sec:
            raise SystemExit(f"{{{{SEC:{m.group(1)}}}}} names a section this page does not have; "
                             f"it has {', '.join(sec)}")
        return str(sec[m.group(1)])
    page = re.sub(r"\{\{SEC:([A-Za-z0-9_]+)\}\}", sec_rep, page)
    old = dict(OLD_REAL)

    def fig_rep(m):
        name = m.group(1)
        if name in old:
            b64 = base64.b64encode((review / old[name]).read_bytes()).decode()
            return f"<img alt='' src='data:image/png;base64,{b64}'>"
        svg = work / f"{name}.svg"
        if not svg.exists():
            raise SystemExit(f"no figure {name}: run --stages figures")
        return svg.read_text(encoding="utf-8")
    page = re.sub(r"\{\{FIG:([A-Za-z0-9_]+)\}\}", fig_rep, page)

    def tok(m):
        key = m.group(1)
        if key not in T:
            raise SystemExit(f"the page asks for {{{{T.{key}}}}}, which the build does not compute")
        return _html.escape(str(T[key]))
    page = re.sub(r"\{\{T\.([A-Za-z0-9_]+)\}\}", tok, page)
    left = re.findall(r"\{\{[^}]*\}\}", page)
    if left:
        raise SystemExit(f"unfilled tokens: {left[:5]}")
    _write_page(page, work.parent / "detector_review_plain.html", len(order))

    # The companion page: the learned models, held out of the review (Tony, 2026-09-16, "cut out
    # the learned models for now ... keep the material in a separate document"). It reuses the
    # same measurements and the same figure builders, so nothing was thrown away.
    comp = LEARNED_TEMPLATE.read_text(encoding="utf-8")
    comp = re.sub(r"\{\{FIG:([A-Za-z0-9_]+)\}\}", fig_rep, comp)
    comp = re.sub(r"\{\{T\.([A-Za-z0-9_]+)\}\}", tok, comp)
    left = re.findall(r"\{\{[^}]*\}\}", comp)
    if left:
        raise SystemExit(f"unfilled tokens in the companion page: {left[:5]}")
    _write_page(comp, work.parent / "learned_detectors_plain.html", 3)


def _write_page(page: str, out: Path, n_figs: int) -> None:
    """Wrap the body in a head and write it.

    Opened from disk, a page with no declared charset is read as Latin-1 and every ▼ and –
    turns to mojibake (sapper SAP005). The templates are body content; the head is added here."""
    title_and_style, _, body = page.partition("<main>")
    head = ('<!doctype html>\n<html lang="en"><head><meta charset="utf-8">'
            '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
            + title_and_style + '</head><body>\n<main>')
    out.write_text(head + body + "\n</body></html>\n", encoding="utf-8")
    words = len(re.sub(r"<svg.*?</svg>|<[^>]+>", " ", page, flags=re.S).split())
    print(f"  wrote {out.name}: {n_figs} figures, about {words:,} words of text")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--out", type=Path, default=None)
    ap.add_argument("--from-review", type=Path, default=None,
                    help="the first review's darkroom folder (measurements/, figures)")
    ap.add_argument("--stages", nargs="+", default=["all"])
    a = ap.parse_args(argv)
    if a.out is None:
        from bugarach.paths import darkroom
        a.out = darkroom() / FOLDER_NAME
    work = a.out / "_work"
    work.mkdir(parents=True, exist_ok=True)
    order = ["sim", "toys", "tube", "real", "count", "figures", "page"]
    stages = order if a.stages == ["all"] else a.stages
    for st in stages:
        print("stage", st)
        fn = globals()[f"stage_{st}"]
        if st in ("real", "figures", "page"):
            fn(work, a.from_review)
        else:
            fn(work)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
