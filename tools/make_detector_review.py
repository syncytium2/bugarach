#!/usr/bin/env python3
"""The detector review: every detector, how it decides, how it was tested, and real rasters.

    python tools/make_detector_review.py --bakeoff RUN_DIR            # everything
    python tools/make_detector_review.py --bakeoff RUN_DIR --stages mechanism page

Written for Tony's 2026-09-15 ask: a document for **external review** that describes each
detector — the six hand-written ones and the learned ones — with a figure of how it
decides; a figure on surrogates; the simulator; the optimization procedure; and the
detectors run on real TTX and senktide recordings. Unsupervised methods are out of scope.

**Real treatment data is in this page, so it has no `--also` and no repo copy.**
FOUNDATIONS §5. The page, its figures and the measurements behind them go to one darkroom
folder, claimed on the git board.

**Numbers in the page come from measurements, not typing.** The prose is
`tools/detector_review_template.html`; a number in it is a ``{{token}}`` filled from
``<out>/_work/numbers.json``, which the stages below write, so a figure and the sentence
under it cannot drift apart. A token the build cannot fill is a build failure. Detector
settings the text describes (a 2 s bin, a 60 s window) are quoted from
``bench.OPERATING_POINTS`` through tokens too.

**Words about the treatment recordings are not in the repo either.** A sentence saying what
a TTX or senktide recording shows is a result, so the template carries ``{{PROSE:key}}``
and the sentence lives in ``<out>/real_prose.json``, beside the page. A missing key fails
the build.

``--bakeoff`` is a directory holding ``baseline_quiet/`` and ``baseline_busy/``, each with
three ``tools/fair_bakeoff.py`` runs (training seeds 0, 1, 2) over the bench recording at
that background level::

    python tools/fair_bakeoff.py --spec spec_baseline_quiet.json --out RUN/baseline_quiet \\
        --folds 4 --seeds-per-fold 6 --train-seed 0     # and 1, 2; and busy

Stages, each cached in ``<out>/_work`` so a prose edit rebuilds in seconds:

* ``models``         — train the six learned architectures once on the bench's quiet
  recordings (the fair bake-off's settings, fold 0) and save checkpoints. Figures 9 and
  13–16 use these single runs; Figure 12 uses the bake-off's three.
* ``problem``        — Figure 1.
* ``surrogate_data`` — the numbers behind Figure 2. Needs Elephant (the shuffle is
  ``surrogates.homogeneous_resample``), so it may run under another venv.
* ``surrogates``     — Figure 2.
* ``mechanism``      — Figures 3–8: each hand-written detector on two 3-minute windows.
* ``learned``        — Figure 9.
* ``generator``      — Figure 10.
* ``sweeps``         — every hand-written detector's setting list on the bake-off's
  recordings (``bench.sweep``).
* ``shipped``        — the hand-written detectors at the settings they ship with
  (``bench.evaluate``), on the same recordings.
* ``optimization``   — Figure 11.
* ``performance``    — Figure 12 and Table 2.
* ``real``           — Figures 13–16.
* ``page``           — fill the template, embed the figures, write the HTML.
"""
from __future__ import annotations

import argparse
import base64
import contextlib
import datetime as _dt
import json
import os
import re
import subprocess
import sys
import tempfile
import time
import warnings
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))

FOLDER_NAME = "2026-09-15-detector-review"
TEMPLATE = Path(__file__).resolve().parent / "detector_review_template.html"

#: The bench recording Figures 1B, 2C and 3–9 are drawn on — the seed and windows
#: `make_mechanism_figure.py` settled on: a planted event at 491.9 s with 18% of ROIs
#: taking part, and a window inside the dense block where nothing is planted.
SEED, REGIME = 3, "baseline_quiet"
WIN_A, WIN_B = (400.0, 580.0), (1290.0, 1470.0)
#: The bench recording Figure 10 draws in full.
GEN_SEED = 1

COLW = 520
TRACE_H = 150
GREY = "#8c8c8c"
BAR = "#111111"
GROUPS = ("DI", "MALE", "ORX", "OVX")
LEARNED = ("tube", "tube_guard", "tube_ratio", "tube_ratio_guard", "trace", "tiny")
CONTROLS = ("trace", "tiny")
CODED = ("rate", "coact", "loco", "sce", "cicada", "sync")
TIME_LABEL = "time in recording"

#: Display names. locust is keyed `cicada` in code and must never be shown as that, or as
#: the viewer's stale "sixth". The learned variants get reader names, not identifiers.
NAMES = {"rate": "rate+context", "coact": "CoactDetect", "loco": "LoCo",
         "sce": "binned SCE", "cicada": "locust", "sync": "SPIKE-synch",
         "tube": "tube", "tube_guard": "tube-guard", "tube_ratio": "tube-ratio",
         "tube_ratio_guard": "tube-ratio-guard", "trace": "trace", "tiny": "tiny"}


# ----------------------------------------------------------------------- plumbing
def _hv():
    import holoviews as hv
    import panel as pn
    hv.extension("bokeh")
    return hv, pn


def save_figure(items, work: Path, name: str, *, scale: int = 2) -> Path:
    """Save a Panel column as HTML and flatten it to PNG. Returns the PNG path."""
    from make_diagnostic import _render_png

    _, pn = _hv()
    html = work / f"{name}.html"
    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td) / "p.html"
        pn.Column(*items).save(str(tmp))
        os.replace(tmp, html)
    png = html.with_suffix(".png")
    if not _render_png(html, png, scale=scale):
        raise RuntimeError(f"{name}: no PNG (python -m playwright install chromium)")
    return png


def put(work: Path, key: str, value) -> None:
    """Record a number the page will quote."""
    f = work / "numbers.json"
    d = json.loads(f.read_text()) if f.exists() else {}
    d[key] = value
    f.write_text(json.dumps(d, indent=1, sort_keys=True))


def sub_head(pn, text):
    return pn.pane.HTML(f"<div style='font:600 12px system-ui;margin:0 0 2px 70px'>{text}</div>")


def key_html(pn, parts):
    """A key set in its own colors, beside the figure rather than in prose above it."""
    return pn.pane.HTML("<div style='font:12px system-ui;color:#222;margin:2px 0 4px 70px'>"
                        + " &nbsp;&nbsp; ".join(parts) + "</div>")


def glyph(ch, color, label):
    return f"<span style='color:{color};font-weight:700'>{ch}</span> {label}"


LANE_KEY = [glyph("▼", "#1b7f3b", "planted event, found"),
            glyph("▼", "#b3261e", "planted event, missed"),
            glyph("▮", "#555", "a call (drawn in the detector's color)"),
            glyph("✕", "#b3261e", "false alarm"),
            glyph("○", "#b3261e", "second call on an event already found"),
            "<span style='background:#f6e7d3;padding:0 6px'>shaded</span> busy block"]


def trace_opts(el, win, ylabel, *, last, ylim):
    from bugarach.ui.app import _time_axis_hook
    return el.opts(width=COLW, height=TRACE_H + (30 if last else 0), xlim=win, ylim=ylim,
                   ylabel=ylabel, xlabel=TIME_LABEL if last else "", title="", toolbar=None,
                   show_legend=False, hooks=[_time_axis_hook], fontsize={"ylabel": "9pt"},
                   shared_axes=False, **({} if last else {"xaxis": None}))


def shipped(det: str) -> dict:
    from bugarach.bench import OPERATING_POINTS
    return dict(OPERATING_POINTS[det].params)


# ----------------------------------------------------------------------- models
def _train_one(job):
    name, out = job
    from bugarach.bench import fold_split, make_recording
    from bugarach.learn.checkpoint import save
    from bugarach.learn.train import fold_maker, train
    from fair_bakeoff import LR

    split = fold_split(n_folds=4, seeds_per_fold=6)
    seeds = list(split.train(0))
    cache = {}

    def rec(seed):
        if seed not in cache:
            cache[seed] = make_recording(REGIME, seed)
        return cache[seed]

    mk, n_fit, n_val = fold_maker(rec, seeds)
    n_train = min(10, n_fit)
    t0 = time.perf_counter()
    tr = train(name, mk, n_train=n_train, steps=900, crop=4096, batch=3,
               lr=LR[name], seed=0)
    secs = time.perf_counter() - t0
    path = Path(out) / f"{name}.json"
    save(tr, path, trained_on=f"bench {REGIME}, recording seeds {seeds[0]}-{seeds[-1]}",
         train_seed=0, steps=900, n_fit=n_train, n_threshold_val=n_val,
         note="detector review, 2026-09-15")
    return name, dict(threshold=float(tr.threshold), n_params=int(tr.n_params),
                      train_sec=round(secs, 1), seeds=[seeds[0], seeds[-1]],
                      n_fit=n_train, n_val=n_val, lr=LR[name])


def stage_models(work: Path, workers: int) -> None:
    out = work / "models"
    out.mkdir(parents=True, exist_ok=True)
    with ProcessPoolExecutor(workers) as ex:
        res = dict(ex.map(_train_one, [(n, str(out)) for n in LEARNED]))
    (out / "models.json").write_text(json.dumps(res, indent=1))
    for n, r in res.items():
        print(f"  trained {n}: threshold {r['threshold']:.4g}, {r['n_params']} parameters")


def load_models(work: Path) -> dict:
    """The learned checkpoints that exist. A rebuild of the hand-written detectors alone (a
    work folder with no ``models/``) gets none, and carries the learned results over from an
    earlier build with ``--carry-learned`` — they do not depend on the detectors' settings."""
    from bugarach.learn.checkpoint import load
    return {n: load(work / "models" / f"{n}.json") for n in LEARNED
            if (work / "models" / f"{n}.json").exists()}


# ----------------------------------------------------------------------- shared pieces
def _bench(seed=SEED):
    from bugarach.bench import make_recording
    from bugarach.detectors.rate import recording_extent
    s, gt = make_recording(REGIME, seed)
    return s, gt, recording_extent(s)


def _in(win, pad=5.0):
    return lambda t: (np.asarray(t) >= win[0] - pad) & (np.asarray(t) <= win[1] + pad)


def _overlapping(on, wd, win):
    """Calls that reach the window, UNCHANGED. `lane_panel` re-scores what it is given, so
    a call clipped to the window would be judged as a call the detector never made; its
    own `_spans` clips the drawing. Calls within the scoring tolerance of the window are
    kept too — one just outside can be the match for an event just inside — but none that
    starts past the window's end, which `_spans` does not expect."""
    from bugarach.score import TOL_SEC
    on, wd = np.asarray(on, float), np.asarray(wd, float)
    end = on + np.where(np.isfinite(wd), wd, 0.0)
    keep = (end >= win[0] - TOL_SEC) & (on <= win[1])
    return on[keep], wd[keep]


def _count_label(det, onsets, span):
    """'LoCo · 2 calls': identity and count in the lane label, never in a caption
    (CLAUDE.md, compact labeling). A call counts where it starts."""
    on = np.asarray(onsets, float)
    n = int(np.sum((on >= span[0]) & (on < span[1])))
    return f"{NAMES[det]} · {n} call{'' if n == 1 else 's'}"


@contextlib.contextmanager
def _page_layout(names=None, raster_px=None):
    """Borrow `build_page` with reader names (counts included) and a taller raster, and
    put the module back afterwards: it is shared with the group-summary tool."""
    import make_group_raster_summary as mg
    old = (mg.LANE_NAMES, mg.RASTER_PX)
    mg.LANE_NAMES = {**mg.LANE_NAMES, **(names or {})}
    mg.RASTER_PX = raster_px or mg.RASTER_PX
    try:
        yield
    finally:
        mg.LANE_NAMES, mg.RASTER_PX = old


def _lane(dets, calls, win, gt, *, row_px=26):
    from bugarach.ui.diagnostic import lane_panel
    from make_group_raster_summary import LANE_COLORS
    lanes = {d: _overlapping(*calls[d], win) for d in dets}
    return lane_panel(lanes, ext=win, gt=gt, width=COLW, row_px=row_px,
                      names={d: _count_label(d, calls[d][0], win) for d in dets},
                      colors={d: LANE_COLORS.get(d, "#555") for d in dets}).opts(
        toolbar=None, xaxis=None, xlim=win, shared_axes=False)


def _raster(s, win, key, *, width=COLW, height=130, xaxis=False):
    from bugarach.ui.diagnostic import raster_panel
    r = raster_panel(s.streams["events"], ext=win, width=width, height=height,
                     name="simulated", ydim=f"roi_{key}", ticks="minimal").opts(
        toolbar=None, xlim=win, shared_axes=False,
        ylabel=f"simulated · {s.streams['events'].n_rois} ROIs")
    return r.opts(xlabel=TIME_LABEL) if xaxis else r.opts(xaxis=None)


def _window_counts(on, wd, gt, win):
    """Planted events whose time lies in the window, how many a detector found, and how
    many of its calls START in the window (a call is counted once, where it begins)."""
    from bugarach.score import score_detections
    sc = score_detections(gt, on, widths=wd)
    t = np.asarray(gt.times, float)
    inwin = (t >= win[0]) & (t <= win[1])
    on = np.asarray(on, float)
    return dict(planted=int(inwin.sum()), found=int(sc.hits[inwin].sum()),
                calls=int(np.sum((on >= win[0]) & (on < win[1]))))


def coded_results(s, ext):
    """Every hand-written detector at its shipped setting, through the viewer's own
    `_compute`, so the traces are the detector's."""
    from bugarach.ui.app import _compute
    from make_diagnostic import _detector_params, _dt_for
    params = _detector_params()
    dt = _dt_for(s)
    return {d: _compute(d, s, ext, params[d], dt=dt)["events"] for d in CODED}, params


# ----------------------------------------------------------------------- figure 1
def _period_key(periods):
    from bugarach.ui.diagnostic import REGION_FILL
    return ([f"<span style='display:inline-block;width:12px;height:10px;"
             f"background:{REGION_FILL.get(p, '#9e9e9e')}'></span> {p}" for p in periods]
            + ["<span style='display:inline-block;width:18px;height:3px;background:#333;"
               "vertical-align:middle'></span> the windows the lab marks for analysis"])


def stage_problem(work: Path) -> None:
    hv, pn = _hv()
    from make_group_raster_summary import _anchor_of, build_page

    # A: the problem itself. Of the eight real recordings Section 8 shows (fast stream),
    # the one where the six hand-written detectors' counts inside the marked windows are
    # furthest apart — chosen for that, and the caption says so.
    picks = _real_members()
    real = _real_detections(work)
    ext_c = (-3 * 60.0, 10 * 60.0)      # the 13 minutes drawn, and the ones ranked on
    spread = []
    for label, _ in REAL_ROLES:
        for s in picks[label]["members"]:
            d = real[(label, s.slice_id)]
            a = _anchor_of(s)
            n = []
            for dd in CODED:
                on = np.array([r["onset"] for r in d["rows"]
                               if r["detector"] == dd and r["stream"] == "fast"], float) - a
                n.append(int(np.sum((on >= ext_c[0]) & (on < ext_c[1]))))
            spread.append(((max(n) + 1) / (min(n) + 1), label, s))
    ratio, label, rec = max(spread, key=lambda x: x[0])
    det = real[(label, rec.slice_id)]
    anchor = _anchor_of(rec)
    per = {}
    for d in CODED:
        rr = [r for r in det["rows"] if r["detector"] == d and r["stream"] == "fast"]
        per[d] = (np.array([r["onset"] for r in rr], float),
                  np.array([r["width"] for r in rr], float))
    counts = {d: int(np.sum((per[d][0] - anchor >= ext_c[0]) & (per[d][0] - anchor < ext_c[1])))
              for d in CODED}
    put(work, "prob_a", dict(counts=counts, n_roi=rec.streams["fast"].n_rois, drug=label,
                             group=rec.meta.get("group_id"),
                             minutes=[ext_c[0] / 60, ext_c[1] / 60]))
    names = {d: f"{NAMES[d]} · {counts[d]} call{'' if counts[d] == 1 else 's'}" for d in CODED}
    with _page_layout(names=names, raster_px=150):
        blocks, _ = build_page([(rec, anchor)], ext=ext_c, manifest={}, width=1060,
                               stream="fast", lanes={(rec.slice_id, "fast"): per}, lane_px=16)
    panels = blocks[0][1]
    panels[-1] = panels[-1].opts(xlabel=f"minutes from the end of baseline ({label} starts at 0)",
                                 ylabel=f"fast · {rec.streams['fast'].n_rois} ROIs")
    periods = [r.name for r in rec.regions if r.name
               and r.start_sec - anchor < ext_c[1] and r.end_sec - anchor > ext_c[0]]

    # B: what a detector is graded against — a simulated recording with a known answer
    sb, gt, ext = _bench()
    win = WIN_A
    lane = (hv.Scatter(([win[0]], [0.0]), "t", "truth_prob").opts(alpha=0)
            * hv.Scatter((np.asarray(gt.times, float), [0.35] * len(gt.times)), "t",
                         "truth_prob").opts(marker="inverted_triangle", size=12, color="#111")
            ).opts(width=1060, height=46, xlim=win, ylim=(0, 1), yaxis=None, xaxis=None,
                   toolbar=None, shared_axes=False)
    rb = _raster(sb, win, "prob_b", width=1060, height=175, xaxis=True)
    items = [sub_head(pn, f"A · a real recording as {label} arrives (fast stream): six "
                          "detectors, the same events, very different answers"),
             key_html(pn, _period_key(periods)),
             *[pn.pane.HoloViews(p) for p in panels],
             sub_head(pn, "B · three minutes of a simulated recording: ▼ marks the one "
                          "coordinated event we planted, so here the answer is known"),
             pn.pane.HoloViews(lane), pn.pane.HoloViews(rb)]
    png = save_figure(items, work, "fig01_problem")
    print("  wrote", png.name)


# ----------------------------------------------------------------------- surrogates
def _coact_frames(trains, L, bin_frames):
    nb = int(np.ceil(L / bin_frames))
    c = np.zeros(nb, dtype=np.int32)
    for v in trains:
        if v.size:
            c[np.unique(v // bin_frames)] += 1
    return c


def _doubles(trains, bin_frames):
    """Events that land in a 2 s bin their own ROI already occupies."""
    return int(sum(v.size - np.unique(v // bin_frames).size for v in trains if v.size))


def _surrogate_survival(job):
    """Share of 2 s bins with at least n ROIs, in real baselines and under shift and
    shuffle; per group too, and how often an ROI puts two events in one bin."""
    stream, n_draws = job
    from bugarach import dataset
    from bugarach.io import load_folder
    from bugarach.surrogate_stats import recordings_from_slices
    from bugarach.surrogates import circular_shift, homogeneous_resample
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        slices = load_folder(dataset.current("steps_excluded"))
    recs, _ = recordings_from_slices(slices, stream)
    N = np.arange(0, 41)
    kinds = ("real", "shift", "shuffle")
    tallies = {g: {k: np.zeros(N.size) for k in kinds} for g in ("all",) + GROUPS}
    nbins = {g: {k: 0 for k in kinds} for g in ("all",) + GROUPS}
    doubles = {k: 0 for k in kinds}
    n_events = 0
    for rec in recs:
        L = rec.window[1] - rec.window[0]
        tr = [np.asarray(v, np.int64) - rec.window[0] for v in rec.trains]
        bf = int(round(2.0 / rec.dt))
        g = rec.group if rec.group in GROUPS else None
        n_events += sum(v.size for v in tr)

        def tally(name, trains, share=1):
            c = _coact_frames(trains, L, bf)
            vals = np.array([(c >= k).sum() for k in N])
            for grp in ("all",) + ((g,) if g else ()):
                tallies[grp][name] += vals
                nbins[grp][name] += c.size
            doubles[name] += _doubles(trains, bf) * share
        tally("real", tr, share=n_draws)
        for d in range(n_draws):
            key = (rec.recording_id, stream, "detector-review", d)
            tally("shift", circular_shift(tr, (0, L), key).trains)
            tally("shuffle", homogeneous_resample(tr, (0, L), key).trains)
    surv = {g: {k: (tallies[g][k] / max(nbins[g][k], 1)).tolist() for k in kinds}
            for g in tallies}
    return stream, dict(N=N.tolist(), n_recordings=len(recs), n_draws=n_draws, surv=surv,
                        doubles_per_1000_events={k: 1000 * doubles[k] / (n_events * n_draws)
                                                 for k in kinds},
                        n_events=n_events)


def stage_surrogate_data(work: Path) -> None:
    """The numbers behind Figure 2. Needs Elephant."""
    from bugarach import dataset
    from bugarach.io import load_folder
    from bugarach.surrogate_stats import recordings_from_slices
    from bugarach.surrogates import circular_shift, homogeneous_resample
    with ProcessPoolExecutor(2) as ex:
        surv = dict(ex.map(_surrogate_survival, [("fast", 50), ("slow", 50)]))
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        slices = load_folder(dataset.current("steps_excluded"))
    recs, _ = recordings_from_slices(slices, "fast")
    # the recording whose fast baseline has the most events, so the pattern is visible —
    # a deliberate extreme, and the caption says so
    best = max(recs, key=lambda r: sum(np.size(v) for v in r.trains))
    L = best.window[1] - best.window[0]
    tr = [np.asarray(v, np.int64) - best.window[0] for v in best.trains]
    key = (best.recording_id, "fast", "detector-review-figure", 0)
    surv["panel_a"] = dict(
        dt=best.dt, L=L, n_recordings_ranked=len(recs), real=[v.tolist() for v in tr],
        shift=[v.tolist() for v in circular_shift(tr, (0, L), key).trains],
        shuffle=[v.tolist() for v in homogeneous_resample(tr, (0, L), key).trains])
    (work / "surrogate_survival.json").write_text(json.dumps(surv))
    print("  wrote surrogate_survival.json")


def _bench_survival(N):
    """The same survival curve for the 24 bench recordings the rounds score (quiet level),
    outside the busy block: does the simulator line ROIs up the way real baselines do?"""
    from bugarach.bench import make_recording
    tallies, nbins = np.zeros(N.size), 0
    for seed in range(1000, 1024):
        s, gt = make_recording("baseline_quiet", seed)
        hw = gt.params["hot_window"]
        dur = gt.params["duration_sec"]
        c = np.zeros(int(np.ceil(dur / 2.0)), dtype=int)
        for v in s.streams["events"].t50rise:
            v = np.asarray(v, float)
            if v.size:
                c[np.unique(np.clip((v // 2.0).astype(int), 0, c.size - 1))] += 1
        ctr = (np.arange(c.size) + 0.5) * 2.0
        c = c[(ctr < hw[0]) | (ctr > hw[1])]
        tallies += np.array([(c >= k).sum() for k in N])
        nbins += c.size
    return tallies / nbins


def stage_surrogates(work: Path) -> None:
    hv, pn = _hv()
    from bugarach.score import TOL_SEC
    from bugarach.ui.app import _time_axis_hook

    cache = work / "surrogate_survival.json"
    if not cache.exists():
        raise SystemExit("run --stages surrogate_data first, with a Python that has Elephant")
    surv = json.loads(cache.read_text())

    # ---- A: one real baseline raster, its shift and its shuffle ----------------------
    A = surv["panel_a"]
    dt = A["dt"]
    versions = {k: [np.asarray(v, np.int64) for v in A[k]] for k in ("real", "shift", "shuffle")}
    tr = versions["real"]
    order = np.argsort([v.size for v in tr], kind="stable")      # quietest ROI at the bottom
    view = (0.0, 300.0)
    labels = {"real": "A1 · recorded", "shift": "A2 · circular shift",
              "shuffle": "A3 · shuffle"}
    rasters = []
    for name, trains in versions.items():
        ts, ys = [], []
        for row, roi in enumerate(order):
            t = trains[roi] * dt
            t = t[(t >= view[0]) & (t <= view[1])]
            ts.append(t)
            ys.append(np.full(t.size, row + 1))
        t, y = np.concatenate(ts), np.concatenate(ys)
        yd = f"roi_sur_{name}"
        raster = hv.Segments((t, y - 0.35, t, y + 0.35), kdims=["t", yd, "t1", "y1"]).opts(
            color="#2b2b2b", line_width=1.3)
        rasters.append(raster.opts(width=1060, height=150, xlim=view, ylim=(0.3, len(tr) + 0.7),
                                   ylabel=f"{labels[name]} · {len(tr)} ROIs", xlabel="",
                                   yticks=[1, len(tr)], toolbar=None, hooks=[_time_axis_hook],
                                   fontsize={"ylabel": "9pt"}, xaxis=None, shared_axes=False))
    rasters[-1] = rasters[-1].opts(xaxis="bottom", height=180, xlabel="time in the baseline")

    # ---- B: how often chance alone lines up n ROIs -------------------------------------
    plots = []
    colours = {"real": "#111111", "shift": "#0B5FFF", "shuffle": "#F77F00"}
    sim = _bench_survival(np.array(surv["fast"]["N"]))
    for j, stream in enumerate(("fast", "slow")):
        d = surv[stream]
        N = np.array(d["N"])
        ov = []
        for name in ("real", "shift", "shuffle"):
            p = np.array(d["surv"]["all"][name])
            m = (N >= 1) & (p > 0)
            ov.append(hv.Curve((N[m], p[m]), f"n_{stream}", f"p_{stream}").opts(
                color=colours[name], line_width=2.2,
                line_dash="solid" if name != "real" else "dashed"))
        if stream == "fast":
            m = (N >= 1) & (sim > 0)
            ov.append(hv.Curve((N[m], sim[m]), f"n_{stream}", f"p_{stream}").opts(
                color="#1b7f3b", line_width=2.2, line_dash="dotdash"))
        ov.append(hv.VLine(6).opts(color="#999", line_dash="dotted", line_width=1))
        plots.append(hv.Overlay(ov).opts(
            width=520, height=320, logy=True, xlim=(1, 16), ylim=(1e-6, 1), yticks=[(1, "100%"), (0.1, "10%"), (0.01, "1%"), (1e-3, "0.1%"), (1e-4, "0.01%"), (1e-5, "0.001%"), (1e-6, "0.0001%")],
            xlabel=f"n, ROIs with an event in one 2 s bin ({stream} stream)",
            ylabel=f"B{j + 1} · share of bins with at least n ROIs",
            show_legend=False, toolbar=None, show_grid=True,
            fontsize={"ylabel": "9pt", "xlabel": "9pt"}))
        ratio = {}
        for n in (8, 10, 12):
            i = int(np.flatnonzero(N == n)[0])
            sh = d["surv"]["all"]["shift"][i]
            ratio[f"n{n}"] = round(d["surv"]["all"]["real"][i] / sh) if sh > 0 else None
        put(work, f"sur_{stream}_real_over_shift", ratio)
    i8 = int(np.flatnonzero(np.array(surv["fast"]["N"]) == 8)[0])
    put(work, "sur_sim_n8", dict(sim=float(sim[i8]), real=surv["fast"]["surv"]["all"]["real"][i8]))

    # ---- D: the mechanism in one number: a cell's second event in a bin it already filled
    bars = []
    for stream in ("fast", "slow"):
        dd = surv[stream]["doubles_per_1000_events"]
        bars += [(stream, lab, dd[k]) for k, lab in (("real", "recorded"),
                                                     ("shift", "circular shift"),
                                                     ("shuffle", "shuffle"))]
    # the value rides in the tick label, so a zero bar still says "0"
    xs = [f"{st} · {kd} · {v:.0f}" for st, kd, v in bars]
    dplot = hv.Bars([(x, v, kd) for x, (_, kd, v) in zip(xs, bars)],
                    hv.Dimension("bar", values=xs), ["per1000", "kind"]).opts(
        color="kind", cmap={"recorded": "#111111", "circular shift": "#0B5FFF",
                            "shuffle": "#F77F00"},
        width=1060, height=230, ylim=(0, 120), ylabel="C · events per 1,000",
        xlabel="", toolbar=None, show_legend=False,
        fontsize={"ylabel": "9pt", "xticks": "9pt"}, shared_axes=False)
    for stream in ("fast", "slow"):
        d = surv[stream]
        N = np.array(d["N"])
        for n in (4, 6, 8):
            i = int(np.flatnonzero(N == n)[0])
            put(work, f"sur_{stream}_n{n}", {k: d["surv"]["all"][k][i]
                                             for k in ("real", "shift", "shuffle")})
        i6 = int(np.flatnonzero(N == 6)[0])
        order_ok = [g for g in GROUPS if g in d["surv"]
                    and d["surv"][g]["shuffle"][i6] < d["surv"][g]["shift"][i6]]
        put(work, f"sur_{stream}_groups_shuffle_below_shift", len(order_ok))
        put(work, f"sur_{stream}_groups_real_above_shift",
            len([g for g in GROUPS if g in d["surv"]
                 and d["surv"][g]["real"][i6] > d["surv"][g]["shift"][i6]]))
        put(work, f"sur_{stream}_doubles", {k: round(v, 1)
                                            for k, v in d["doubles_per_1000_events"].items()})
        put(work, f"sur_{stream}_n_recordings", d["n_recordings"])
        put(work, "sur_n_draws", d["n_draws"])

    # ---- C: a bar from the whole recording versus a bar from the neighbourhood ---------
    s, gt, ext = _bench()
    trains = [np.asarray(v, float) for v in s.streams["events"].t50rise]
    bw, C, n_whole, n_near, pct = 2.0, 60.0, 200, 100, 99.9
    T = ext[1] - ext[0]
    nb = int(np.ceil(T / bw))

    def counts_of(trs, lo_, L_):
        n = int(np.ceil(L_ / bw))
        c = np.zeros(n)
        for v in trs:
            if v.size:
                c[np.unique(np.clip(((v - lo_) // bw).astype(int), 0, n - 1))] += 1
        return c
    obs = counts_of(trains, ext[0], T)
    rng = np.random.RandomState(7)
    from bugarach.assess import circular_shift_trains
    from bugarach.detectors._shared import matlab_prctile
    rel = [v - ext[0] for v in trains]
    pool = np.concatenate([counts_of([x + ext[0] for x in circular_shift_trains(rel, T, rng)],
                                     ext[0], T) for _ in range(n_whole)])
    global_bar = matlab_prctile(pool, pct)
    ctr = ext[0] + (np.arange(nb) + 0.5) * bw
    view_c = (900.0, 1800.0)
    local_bar = np.full(nb, np.nan)
    for b in np.flatnonzero((ctr >= view_c[0] - 5) & (ctr <= view_c[1] + 5)):
        lo_, hi_ = max(ext[0], ctr[b] - C / 2), min(ext[1], ctr[b] + C / 2)
        sub = [v[(v >= lo_) & (v < hi_)] - lo_ for v in trains]
        vals = np.concatenate([counts_of([x + lo_ for x in circular_shift_trains(sub, hi_ - lo_, rng)],
                                         lo_, hi_ - lo_) for _ in range(n_near)])
        local_bar[b] = matlab_prctile(vals, pct)
    k = (ctr >= view_c[0]) & (ctr <= view_c[1])
    calls_g = ctr[k & (obs > global_bar) & (obs >= 3)]
    calls_l = ctr[k & (obs > local_bar) & (obs >= 3)]
    hw = gt.params["hot_window"]
    planted = np.asarray(gt.times, float)
    decoys = np.asarray(gt.distractor_times, float)
    inb = lambda x: (x >= hw[0]) & (x <= hw[1])  # noqa: E731

    def near_any(calls, targets):
        return int(sum(np.any(np.abs(targets - c) <= TOL_SEC) for c in calls)) if targets.size else 0
    out_g = calls_g[~inb(calls_g)]
    out_l = calls_l[~inb(calls_l)]
    put(work, "sur_c", dict(
        bin_s=bw, window_s=C, n_whole=n_whole, n_near=n_near, pct=pct,
        global_bar=float(global_bar), calls_global_in_block=int(inb(calls_g).sum()),
        calls_local_in_block=int(inb(calls_l).sum()),
        outside_global=int(out_g.size), outside_local=int(out_l.size),
        outside_on_planted=near_any(np.union1d(out_g, out_l), planted[(planted >= view_c[0]) & (planted <= view_c[1])]),
        outside_on_decoy=near_any(np.union1d(out_g, out_l), decoys),
        local_bar_in_block_median=float(np.nanmedian(local_bar[k & inb(ctr)])),
        block_min=f"{hw[0] / 60:.0f}–{hw[1] / 60:.0f}",
        view_min=f"{view_c[0] / 60:.0f}–{view_c[1] / 60:.0f}",
        planted_in_view=int(np.sum((planted >= view_c[0]) & (planted <= view_c[1]))),
        missed_in_view=[dict(pct=int(round(e.frac * 100)), n_part=e.n_part)
                        for e in gt.events if view_c[0] <= e.time <= view_c[1]
                        and not np.any(np.abs(np.union1d(out_g, out_l) - e.time) <= TOL_SEC)]))
    pv = planted[(planted >= view_c[0]) & (planted <= view_c[1])]
    dv = decoys[(decoys >= view_c[0]) & (decoys <= view_c[1])]
    lane = (hv.Scatter(([view_c[0]], [0.0]), "t", "lane_c").opts(alpha=0)
            * hv.VSpan(hw[0], hw[1]).opts(color="#e8a33d", alpha=0.16)
            * hv.Scatter((pv, np.full(pv.size, 3.0)), "t", "lane_c").opts(
                marker="inverted_triangle", size=10, color="#111")
            * hv.Scatter((dv, np.full(dv.size, 2.0)), "t", "lane_c").opts(
                marker="inverted_triangle", size=10, fill_alpha=0, line_color="#555")
            * hv.Rectangles([(c - 1, 0.7, c + 1, 1.3) for c in calls_g]).opts(color="#8c8c8c",
                                                                                 line_alpha=0)
            * hv.Rectangles([(c - 1, -0.3, c + 1, 0.3) for c in calls_l]).opts(color="#7A00E6",
                                                                                  line_alpha=0)
            ).opts(width=1060, height=130, xlim=view_c, ylim=(-0.7, 3.6), toolbar=None,
                   xaxis=None, yticks=[(3, "planted"), (2, "decoy"),
                                       (1, f"whole-recording bar · {calls_g.size} calls"),
                                       (0, f"nearby-60 s bar · {calls_l.size} calls")],
                   ylabel="", shared_axes=False, fontsize={"yticks": "9pt"})
    from bugarach.ui.diagnostic import raster_panel
    rast = raster_panel(s.streams["events"], ext=view_c, width=1060, height=130,
                        name="simulated", ydim="roi_sur_c", ticks="minimal").opts(ylabel=f"simulated · {s.streams['events'].n_rois} ROIs",
        toolbar=None, xaxis=None, xlim=view_c, shared_axes=False)
    trace = (hv.Curve((ctr[k], obs[k]), "t", "c_obs").opts(interpolation="steps-mid",
                                                          color="#0B5FFF", line_width=1)
             * hv.HLine(global_bar).opts(color="#8c8c8c", line_width=2.4, line_dash="dashed")
             * hv.Curve((ctr[k], local_bar[k]), "t", "c_obs").opts(color="#7A00E6", line_width=2.4)
             ).opts(width=1060, height=210, xlim=view_c, ylim=(0, 14), toolbar=None,
                    ylabel="D · ROIs per 2 s bin", xlabel=TIME_LABEL,
                    shared_axes=False, hooks=[_time_axis_hook], fontsize={"ylabel": "9pt"})

    items = [sub_head(pn, "A · five minutes of the busiest real baseline (fast stream), and two "
                          "surrogates of it"), *[pn.pane.HoloViews(r) for r in rasters],
             sub_head(pn, "B · how often n ROIs line up: real baselines against the two "
                          "surrogates (B1 fast stream, B2 slow stream)"),
             key_html(pn, [glyph("- -", "#111", "recorded"), glyph("—", "#0B5FFF", "circular shift"),
                           glyph("—", "#F77F00", "shuffle"),
                           glyph("-·-", "#1b7f3b", "simulated recordings, Section 5 (B1 only)"),
                           glyph("┊", "#999", "n = 6")]),
             pn.pane.HoloViews(hv.Layout(plots).cols(2).opts(shared_axes=False, toolbar=None)),
             sub_head(pn, "C · why: how often a cell's event lands in a 2 s bin that cell already "
                          "filled"),
             key_html(pn, [glyph("▮", "#111", "recorded"), glyph("▮", "#0B5FFF", "circular shift"),
                           glyph("▮", "#F77F00", "shuffle")]),
             pn.pane.HoloViews(dplot),
             sub_head(pn, f"D · a sketch of where the surrogate is drawn from (not a shipped detector): minutes {view_c[0] / 60:.0f}–"
                          f"{view_c[1] / 60:.0f} of a simulated recording whose busy block has "
                          "nothing planted inside it"),
             key_html(pn, [glyph("—", "#0B5FFF", "ROIs active per 2 s bin"),
                           glyph("- -", "#8c8c8c", "bar from the whole recording"),
                           glyph("—", "#7A00E6", "bar from the nearby 60 s"),
                           glyph("▼", "#111", "planted"), glyph("▽", "#555", "decoy"),
                           "<span style='background:#f6e7d3;padding:0 6px'>shaded</span> busy block"]),
             *[pn.pane.HoloViews(p) for p in (lane, rast, trace)]]
    put(work, "sur_a", dict(n_roi=len(tr), n_recordings=A["n_recordings_ranked"]))
    png = save_figure(items, work, "fig02_surrogates")
    print("  wrote", png.name)


# ----------------------------------------------------------------------- mechanism
def _trace_rate(hv, r, params, win, key):
    t, y = np.asarray(r.t), np.asarray(r.y)
    ref = np.asarray(r.extra["ref"], float)
    k = _in(win)(t)
    yd = f"rate_{key}"
    ex = params["rate"]["excess_threshold_hz"]
    el = (hv.Curve((t[k], y[k]), "t", yd).opts(color="#0B5FFF", line_width=1.2)
          * hv.Curve((t[k], ref[k]), "t", yd).opts(color=GREY, line_width=2.2)
          * hv.Curve((t[k], ref[k] + ex), "t", yd).opts(color=BAR, line_dash="dotted",
                                                         line_width=2))
    return [("events per second", el, (0, 14))]


def _trace_coact(hv, r, params, win, key):
    from make_mechanism_figure import coact_bar
    ctr, obs, nm, bar = coact_bar(r.result)
    k = _in(win)(ctr)
    kb, kn = k & np.isfinite(bar), k & np.isfinite(nm)
    yd = f"coact_{key}"
    el = (hv.Curve((ctr[k], obs[k]), "t", yd).opts(interpolation="steps-mid",
                                                    color="#00B3A4", line_width=1.4)
          * hv.Scatter((ctr[kn], nm[kn]), "t", yd).opts(color=GREY, size=5)
          * hv.Scatter((ctr[kb], bar[kb]), "t", yd).opts(marker="dash", size=16, color=BAR,
                                                          line_width=2.5))
    return [("ROIs per 2 s bin", el, (0, 14))]


def _trace_loco(hv, r, params, win, key):
    t, y = np.asarray(r.t), np.asarray(r.y)
    thr = np.asarray(r.extra["threshold"], float)
    k = _in(win)(t)
    yd = f"loco_{key}"
    el = (hv.Curve((t[k], y[k]), "t", yd).opts(interpolation="steps-mid", color="#7A00E6",
                                                line_width=1.4)
          * hv.Curve((t[k], thr[k]), "t", yd).opts(color=BAR, line_dash="dotted",
                                                    line_width=2, interpolation="steps-mid"))
    return [("ROIs per 1 s bin", el, (0, 14))]


def _trace_sce(hv, r, params, win, key):
    t, y = np.asarray(r.t), np.asarray(r.y)
    thr = np.asarray(r.extra["threshold"], float)
    k = _in(win, pad=10.0)(t)
    yd = f"sce_{key}"
    el = (hv.Curve((t[k], y[k]), "t", yd).opts(interpolation="steps-mid", color="#00A100",
                                                line_width=1.6)
          * hv.Curve((t[k], thr[k]), "t", yd).opts(color=BAR, line_dash="dotted",
                                                    line_width=2))
    return [("ROIs per 10 s bin", el, (0, 24))]


def _trace_cicada(hv, r, params, win, key):
    t, y = np.asarray(r.t), np.asarray(r.y)
    thr = np.asarray(r.extra["threshold"], float)
    k = _in(win)(t)
    yd = f"cicada_{key}"
    el = (hv.Curve((t[k], y[k]), "t", yd).opts(interpolation="steps-mid", color="#FF00A8",
                                                line_width=1.0)
          * hv.Curve((t[k], thr[k]), "t", yd).opts(color=BAR, line_dash="dotted",
                                                    line_width=2))
    return [("ROIs on, per frame", el, (0, 14))]


def _trace_sync(hv, r, params, win, key):
    raw = r.result
    px, py = np.asarray(raw.profile_x), np.asarray(raw.profile_y)
    cx, cy = np.asarray(raw.Cx), np.asarray(raw.Cy)
    kp, kc = _in(win)(px), _in(win)(cx)
    thr = float(params["sync"]["C_threshold"])
    yd1, yd2 = f"syncp_{key}", f"syncb_{key}"
    el1 = (hv.Scatter((px[kp], py[kp]), "t", yd1).opts(color="#FF3B00", size=4, alpha=0.7))
    el2 = (hv.Curve((cx[kc], cy[kc]), "t", yd2).opts(color="#FF3B00", line_width=1.0)
           * hv.HLine(thr).opts(color=BAR, line_dash="dotted", line_width=2))
    return [("event scores (0–1)", el1, (-0.01, 0.3)),
            ("frame score (0–1)", el2, (-0.01, 0.3))]


TRACES = {"rate": _trace_rate, "coact": _trace_coact, "loco": _trace_loco,
          "sce": _trace_sce, "cicada": _trace_cicada, "sync": _trace_sync}
FIG_OF = {"rate": 3, "coact": 4, "loco": 5, "sce": 6, "cicada": 7, "sync": 8}
TRACE_KEY = {
    "rate": [glyph("—", "#0B5FFF", "events per second, all ROIs together"),
             glyph("—", GREY, "average over the nearby 60 s"), glyph("┈", BAR, "the bar")],
    "coact": [glyph("—", "#00B3A4", "ROIs with an event in each 2 s bin"),
              glyph("●", GREY, "surrogates' average"),
              glyph("━", BAR, "the bar, at each bin it tested")],
    "loco": [glyph("—", "#7A00E6", "ROIs with an event in each 1 s bin"),
             glyph("┈", BAR, "the bar")],
    "sce": [glyph("—", "#00A100", "ROIs with an event in each 10 s bin"),
            glyph("┈", BAR, "the bar")],
    "cicada": [glyph("—", "#FF00A8", "ROIs switched on in each 0.1 s frame"),
               glyph("┈", BAR, "the bar")],
    "sync": [glyph("●", "#FF3B00", "each event's score"),
             glyph("—", "#FF3B00", "score in each 0.1 s frame"), glyph("┈", BAR, "the bar")]}


def stage_mechanism(work: Path) -> None:
    hv, pn = _hv()
    from bugarach.score import TOL_SEC, score_stream
    s, gt, ext = _bench()
    res, params = coded_results(s, ext)
    a_evt = [e for e in gt.events if WIN_A[0] <= e.time <= WIN_A[1]]
    put(work, "bench_seed", SEED)
    put(work, "win_a", dict(start=f"{int(WIN_A[0] // 60)} min {int(WIN_A[0] % 60)} s",
                            end=f"{int(WIN_A[1] // 60)} min {int(WIN_A[1] % 60)} s"))
    put(work, "win_b", dict(start=f"{int(WIN_B[0] // 60)} min {int(WIN_B[0] % 60)} s",
                            end=f"{int(WIN_B[1] // 60)} min {int(WIN_B[1] % 60)} s"))
    e = a_evt[0]
    put(work, "a_event", dict(time_s=round(e.time, 1), n_part=e.n_part,
                              pct=int(round(e.frac * 100)), others=s.streams["events"].n_rois - 1,
                              max_score=round((e.n_part - 1) / (s.streams["events"].n_rois - 1), 2),
                              span_s=round(max(e.onsets) - min(e.onsets), 2)))
    put(work, "bench_n_roi", s.streams["events"].n_rois)
    near = [d for d in gt.distractors if any(abs(d.time - p) <= TOL_SEC for p in gt.times)]
    put(work, "bench_seed_decoys_on_planted", len(near))
    put(work, "settings", {d: {k: v for k, v in shipped(d).items()} for d in CODED})
    from statistics import NormalDist
    alpha = shipped("coact")["alpha"]
    put(work, "coact_bar", dict(one_in=f"{round(1 / alpha):,}",
                                z=round(NormalDist().inv_cdf(1 - alpha), 2)))
    calls = {}
    for det in CODED:
        r = res[det]
        calls[det] = tuple(np.asarray(a, float) for a in r.events[:2])
    for det in CODED:
        r = res[det]
        cols = []
        for key, win, label in (("A", WIN_A, "A · a planted coordinated event"),
                                ("B", WIN_B, "B · the busy block, nothing planted")):
            put(work, f"{det}_win{key}", _window_counts(*calls[det], gt, win))
            panels = [_lane((det,), calls, win, gt), _raster(s, win, key)]
            rows = TRACES[det](hv, r, params, win, key)
            for i, (ylabel, el, ylim) in enumerate(rows):
                panels.append(trace_opts(el, win, ylabel, last=i == len(rows) - 1, ylim=ylim))
            cols.append(pn.Column(sub_head(pn, label),
                                  *[pn.pane.HoloViews(p) for p in panels]))
        png = save_figure([key_html(pn, LANE_KEY), key_html(pn, TRACE_KEY[det]), pn.Row(*cols)],
                          work,
                          f"fig{FIG_OF[det]:02d}_{det}")
        print("  wrote", png.name)
        sc = score_stream(gt, r.result)
        put(work, f"{det}_bench_seed_score",
            dict(calls=int(sc.n_detected), hits=int(sc.n_hit), planted=int(sc.n_planted),
                 probe_calls=int(sc.hot_fa)))
    if res["sce"].result is not None:
        thr = np.asarray(res["sce"].extra["threshold"], float)
        t = np.asarray(res["sce"].t)
        y = np.asarray(res["sce"].y)
        i = int(np.argmin(np.abs(t - a_evt[0].time)))
        put(work, "sce_winA_bin", dict(count=int(y[i]), bar=float(np.nanmax(thr))))


# ----------------------------------------------------------------------- learned
def _kernels(checkpoint):
    """(centre, surround) per scale, in frames, through the project's own kernel code.

    `tube` is loaded into the subtract-mode variant it is defined against; the variants
    already are that class. So all four panels come from `_centre_surround`.
    """
    import torch
    from bugarach.learn.nets.tube import _build_tube_variant
    m = checkpoint.model
    if hasattr(m, "_centre_surround"):
        net = m
    else:
        from bugarach.learn.nets import ARCHITECTURES
        net = _build_tube_variant(mode="subtract", guard_frames=0, **ARCHITECTURES["tube"].cfg)
        net.load_state_dict(m.state_dict())
    with torch.no_grad():
        ck, sk = net._centre_surround("cpu")
    return ck.squeeze(1).numpy(), sk.squeeze(1).numpy(), net.k


def stage_learned(work: Path) -> None:
    import torch
    hv, pn = _hv()
    from bugarach.learn.encode import encode
    from bugarach.score import score_stream

    models = load_models(work)
    meta = json.loads((work / "models" / "models.json").read_text())
    s, gt, ext = _bench()
    dt = float(s.require_dt("the learned figure"))
    calls = {n: models[n].predict(s)[0] for n in LEARNED}
    enc = encode(s, dt=dt)
    x = torch.from_numpy(enc.raster).unsqueeze(0)
    t = enc.t0 + np.arange(enc.n_frame) * dt

    tube = models["tube"].model
    with torch.no_grad():
        score = torch.sigmoid(tube(x)).squeeze(0).numpy()
        kmin = int(torch.exp(tube.log_center.detach()).min().clamp(1, tube.k))
        pooled = torch.nn.functional.max_pool1d(x.reshape(-1, 1, enc.n_frame),
                                                kernel_size=2 * kmin + 1, stride=1,
                                                padding=kmin).reshape(1, -1, enc.n_frame)
        bright = (pooled.sum(dim=1) / enc.n_roi).squeeze(0).numpy()
    thr = float(models["tube"].threshold)
    put(work, "tube_kmin_frames", kmin)
    put(work, "tube_widen_s", round((2 * kmin + 1) * dt, 1))
    for n in LEARNED:  # the checkpoint's own record, not the training-time summary
        prov = json.loads((work / "models" / f"{n}.json").read_text())["provenance"]
        meta[n].update(n_fit=prov["n_fit"], n_val=prov["n_threshold_val"])
    put(work, "learned_meta", meta)
    from bugarach.learn.nets import ARCHITECTURES
    c = torch.exp(tube.log_center.detach()).clamp(0.5, tube.k / 2).numpy()
    ratio = torch.exp(tube.log_ratio.detach()).clamp(
        1.5, float(ARCHITECTURES["tube"].cfg["max_ratio"])).numpy()
    put(work, "tube_sigma", dict(centre=[round(float(v * dt), 2) for v in c],
                                 surround=[round(float(v * r * dt), 1) for v, r in zip(c, ratio)],
                                 cutoff_s=round(tube.k * dt, 1)))

    # ---- A: the kernels, one shared y range ------------------------------------------------
    kplots = []
    from make_group_raster_summary import LANE_COLORS
    tubes = ("tube", "tube_guard", "tube_ratio", "tube_ratio_guard")
    kern = {n: _kernels(models[n]) for n in tubes}
    # EACH FILTER SCALED TO ITS OWN PEAK. On one shared weight scale a 16 s surround is a
    # flat line on zero next to a 0.2 s centre, and the contrast the design is about —
    # short centre, long surround — could only be read from numbers in the text.
    lag_ticks = [(v, f"{v:+d}s" if v else "0s") for v in (-12, -8, -4, 0, 4, 8, 12)]
    for j, (name, (c, sr, K)) in enumerate(kern.items()):
        lag = np.arange(-K, K + 1) * dt
        ov = []
        for i in range(c.shape[0]):
            ov.append(hv.Curve((lag, c[i] / np.max(np.abs(c[i]))), f"lag_{name}", "weight").opts(
                color=LANE_COLORS[name], line_width=1.8, alpha=0.45 + 0.15 * i))
            ov.append(hv.Curve((lag, -sr[i] / np.max(np.abs(sr[i]))), f"lag_{name}",
                               "weight").opts(color=GREY, line_width=1.4, alpha=0.45 + 0.15 * i))
        bottom = j >= 2
        kplots.append(hv.Overlay(ov).opts(
            width=520, height=190 + (30 if bottom else 0), xlim=(-13.5, 13.5), ylim=(-1.15, 1.15),
            toolbar=None, show_grid=True, xticks=lag_ticks, yticks=[(-1, "−1"), (0, "0"), (1, "1")],
            xlabel="before (−) and after (+) the moment scored" if bottom else "",
            ylabel=f"A{j + 1} · {NAMES[name]} · weight (scaled)", fontsize={"ylabel": "9pt", "xlabel": "9pt"},
            shared_axes=False, **({} if bottom else {"xaxis": None})))

    # ---- B, C: two windows ---------------------------------------------------------------
    cl = {n: (np.asarray(calls[n].onset_sec, float), np.asarray(calls[n].width_sec, float))
          for n in LEARNED}
    cols = []
    for key, win, label, tag in (("B", WIN_A, "B · a planted coordinated event", "A"),
                                 ("C", WIN_B, "C · the busy block, nothing planted", "B")):
        for n in LEARNED:
            put(work, f"{n}_win{tag}", _window_counts(*cl[n], gt, win))
        lane = _lane(tubes, cl, win, gt, row_px=22)
        m = _in(win)(t)
        b = trace_opts(hv.Curve((t[m], bright[m] * 100), "t", f"bright_{key}").opts(
            color="#7F0000", line_width=1.0), win, "% of ROIs on, after widening",
            last=False, ylim=(0, 30))
        sc = trace_opts(hv.Curve((t[m], score[m]), "t", f"score_{key}").opts(
            color="#7F0000", line_width=1.2)
            * hv.HLine(thr).opts(color=BAR, line_dash="dotted", line_width=2),
            win, "tube · score, 0–1", last=True, ylim=(-0.03, 1.03))
        cols.append(pn.Column(sub_head(pn, label),
                              *[pn.pane.HoloViews(p) for p in (lane, _raster(s, win, key), b, sc)]))
    for n in LEARNED:
        r = score_stream(gt, calls[n])
        cover = min(float(np.nansum(np.asarray(calls[n].width_sec, float))),
                    ext[1] - ext[0]) / (ext[1] - ext[0])
        put(work, f"{n}_bench_seed_score", dict(calls=int(r.n_detected), hits=int(r.n_hit),
                                                planted=int(r.n_planted),
                                                probe_calls=int(r.hot_fa),
                                                time_covered=round(cover, 2)))
    items = [sub_head(pn, "A · the time filters each tube model learned"),
             key_html(pn, ["colored: the four center filters, in each model's own color",
                           glyph("—", GREY, "the four surround filters, drawn below zero"),
                           "each filter scaled to its own peak"]),
             pn.pane.HoloViews(hv.Layout(kplots).cols(2).opts(shared_axes=False, toolbar=None)),
             key_html(pn, LANE_KEY[1:] + [glyph("▼", "#1b7f3b",
                                                 "planted event, found by any of the four")]),
             key_html(pn, [glyph("—", "#7F0000", "tube's brightness, then tube's score"),
                           glyph("┈", BAR, "tube's call level")]),
             pn.Row(*cols)]
    png = save_figure(items, work, "fig09_learned")
    print("  wrote", png.name)


# ----------------------------------------------------------------------- generator
FANO_WINDOWS = (30.0, 60.0, 120.0, 300.0)
#: (key, low Hz, high Hz, label) — ROI rate bands for the bunching split
RATE_BANDS = (("under_20", 0.0, 0.02, "under 20 mHz"), ("20_50", 0.02, 0.05, "20–50 mHz"),
              ("50_100", 0.05, 0.1, "50–100 mHz"), ("over_100", 0.1, np.inf, "over 100 mHz"))


def stage_generator(work: Path) -> None:
    hv, pn = _hv()
    from bugarach import bench, dataset
    from bugarach.count_dispersion import burst_rows, fano
    from bugarach.io import load_folder
    from bugarach.simulate import simulate_coordination
    from bugarach.surrogate_stats import recordings_from_slices
    from bugarach.ui.app import _time_axis_hook
    from bugarach.ui.diagnostic import raster_panel

    rec = bench.BENCH_RECORDING
    ext = (0.0, rec["duration_sec"])
    hw = rec["hot_window"]
    W = 1060

    def truth(gt, key, ext_, width):
        planted = np.asarray(gt.times, float)
        distr = np.asarray(gt.distractor_times, float)
        return (hv.Scatter(([ext_[0]], [0.0]), "t", f"truth_{key}").opts(alpha=0)
                * hv.Rectangles([(hw[0], 0.0, hw[1], 1.0)]).opts(color="#f3dcc0", line_alpha=0)
                * hv.Scatter((distr, np.full(distr.size, 0.75)), "t", f"truth_{key}").opts(
                    marker="inverted_triangle", size=10, fill_alpha=0, line_color="#555")
                * hv.Scatter((planted, np.full(planted.size, 0.27)), "t", f"truth_{key}").opts(
                    marker="inverted_triangle", size=11, color="#111")).opts(
            width=width, height=62, xlim=ext_, ylim=(0, 1), xaxis=None,
            yticks=[(0.27, f"planted · {planted.size} events"),
                    (0.75, f"decoys · {distr.size}")], ylabel="",
            fontsize={"yticks": "9pt"}, toolbar=None, show_legend=False, shared_axes=False)

    items = [key_html(pn, [glyph("▼", "#111", "planted event"), glyph("▽", "#555", "decoy"),
                           "<span style='background:#f3dcc0;padding:0 6px'>shaded</span> busy block"])]
    for i, (regime, label) in enumerate((("baseline_quiet", "quiet background"),
                                         ("baseline_busy", "busy background"))):
        s, gt = bench.make_recording(regime, GEN_SEED)
        items.append(sub_head(pn, f"A{i + 1} · a bench recording, {label} "
                                  f"({bench.REGIMES[regime]['bg_rate_hz'] * 1000:g} mHz per ROI)"))
        r = raster_panel(s.streams["events"], ext=ext, width=W, height=140, name="simulated",
                         ydim=f"roi_gen_{regime}", ticks="minimal").opts(
            toolbar=None, xlim=ext, shared_axes=False, ylabel=f"simulated · {s.streams['events'].n_rois} ROIs",
            **({"xaxis": None} if i == 0 else {"height": 170, "xlabel": TIME_LABEL}))
        items += [pn.pane.HoloViews(truth(gt, regime, ext, W)), pn.pane.HoloViews(r)]
        if i == 0:
            gt_quiet, s_quiet = gt, s

    e = sorted(gt_quiet.events, key=lambda e: -e.n_part)[0]
    zoom = (e.time - 1.5, e.time + 1.5)
    put(work, "gen_zoom_event", dict(n_part=e.n_part, pct=int(round(e.frac * 100)),
                                     spread_s=round(max(e.onsets) - min(e.onsets), 2)))
    zr = raster_panel(s_quiet.streams["events"], ext=zoom, width=W, height=170,
                      name="simulated", ydim="roi_gen_zoom", ticks="minimal", mark_px=3).opts(
        toolbar=None, xlim=zoom, shared_axes=False, xlabel=TIME_LABEL,
        ylabel=f"simulated · {s_quiet.streams['events'].n_rois} ROIs")
    zl = (hv.Scatter(([zoom[0]], [0.0]), "t", "truth_zoom").opts(alpha=0)
          * hv.Scatter(([e.time], [0.35]), "t", "truth_zoom").opts(
              marker="inverted_triangle", size=11, color="#111")).opts(
        width=W, height=46, xlim=zoom, ylim=(0, 1), yaxis=None, xaxis=None, toolbar=None,
        shared_axes=False)
    items += [sub_head(pn, "B · one planted event in A1, 3 seconds around it"),
              pn.pane.HoloViews(zl), pn.pane.HoloViews(zr)]

    cache = work / "generator_stats.json"
    if cache.exists():
        stats = json.loads(cache.read_text())
    else:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            slices = load_folder(dataset.current("steps_excluded"))
        # The windows the background shape was FITTED on (and the regime levels were
        # read off): the fitter's own selection, floors included, so the comparison is
        # against the set the simulator was built from.
        from fit_background_shape import baseline_trains
        got = [g for g in (baseline_trains(sl) for sl in slices) if g is not None]
        stats = {k: dict(rates=[], windows=[]) for k in ("real", "flat", "fitted")}
        slice_means = []
        for i, (tr, dur) in enumerate(got):
            tr = [np.asarray(v, float) for v in tr]
            rates = [v.size / dur for v in tr]
            if not np.mean(rates) > 0:
                continue
            slice_means.append(float(np.mean(rates)))
            stats["real"]["rates"] += rates
            stats["real"]["windows"].append(([v.tolist() for v in tr], dur))
            for kind, extra in (("flat", dict(bg_rate_shape=None, bg_burst_shape=None)),
                                ("fitted", dict(bg_rate_shape=rec["bg_rate_shape"],
                                                bg_burst_shape=rec["bg_burst_shape"],
                                                bg_burst_bin_sec=rec["bg_burst_bin_sec"]))):
                sim, _ = simulate_coordination(
                    seed=5000 + i, duration_sec=float(dur), n_roi=len(rates),
                    bg_rate_hz=float(np.mean(rates)), n_per_level=(0,), participation=(0.1,),
                    **extra)
                st = [np.asarray(v, float) for v in sim.streams["events"].t50rise]
                stats[kind]["rates"] += [v.size / dur for v in st]
                stats[kind]["windows"].append(([v.tolist() for v in st], dur))
        stats["slice_means"] = slice_means
        cache.write_text(json.dumps(stats))

    put(work, "gen_real_rate_percentiles_mhz",
        dict(p25=round(1000 * float(np.percentile(stats["slice_means"], 25)), 1),
             p50=round(1000 * float(np.percentile(stats["slice_means"], 50)), 1),
             p75=round(1000 * float(np.percentile(stats["slice_means"], 75)), 1),
             n=len(stats["slice_means"])))
    # what the bench recordings actually carry outside the busy block, planted events and
    # decoys included — the like-for-like number beside a real recording's average rate
    realized = {}
    for regime in ("baseline_quiet", "baseline_busy"):
        per = []
        for seed in range(1000, 1024):
            sb, gtb = bench.make_recording(regime, seed)
            hwb, T = gtb.params["hot_window"], gtb.params["duration_sec"]
            n = sum(int(np.sum((np.asarray(v) < hwb[0]) | (np.asarray(v) > hwb[1])))
                    for v in sb.streams["events"].t50rise)
            per.append(n / (sb.streams["events"].n_rois * (T - (hwb[1] - hwb[0]))))
        realized[regime.split("_")[1]] = round(1000 * float(np.mean(per)), 1)
        # the background alone, against its nominal setting
        bg = []
        for seed in range(1000, 1024):
            sb, gtb = bench.make_recording(regime, seed, n_distractors=0, n_per_level=(0, 0, 0),
                                           hot_window=None, hot_rate_hz=0.0)
            T = gtb.params["duration_sec"]
            bg.append(sum(len(v) for v in sb.streams["events"].t50rise)
                      / (sb.streams["events"].n_rois * T))
        realized[regime.split("_")[1] + "_background_only"] = round(1000 * float(np.mean(bg)), 1)
    put(work, "bench_realized_mhz", realized)
    colours = {"real": "#111111", "flat": "#F77F00", "fitted": "#0B5FFF"}
    bins = np.arange(-4.0, 0.01, 0.25)                    # log10 Hz
    hists = []
    for kind in ("real", "flat", "fitted"):
        r = np.asarray(stats[kind]["rates"])
        silent = float(np.mean(r == 0))
        put(work, f"gen_{kind}", dict(silent_pct=round(100 * silent), n_roi=int(r.size),
                                      median_mhz=round(1000 * float(np.median(r)), 1)))
        h, _ = np.histogram(np.log10(r[r > 0]), bins=bins)
        hists.append(hv.Curve((np.repeat(bins, 2)[1:-1] + 3, np.repeat(h / r.size, 2)),
                              "log_rate", "share",
                              label=f"{ {'real': 'recorded'}.get(kind, kind)} · {round(100 * silent)}% of ROIs with no event").opts(
            color=colours[kind], line_width=2.2))
    ch = hv.Overlay(hists).opts(width=520, height=280, toolbar=None, show_grid=True,
                                xticks=[(-1, "0.1"), (0, "1"), (1, "10"), (2, "100"), (3, "1000")],
                                xlabel="event rate of one ROI in its baseline (mHz, log scale)",
                                ylabel="C · share of all ROIs", legend_position="top_left", ylim=(0, 0.4),
                                fontsize={"ylabel": "9pt", "xlabel": "9pt", "legend": "8pt"})
    fano_curves = []
    band_rows = {}
    for kind in ("real", "flat", "fitted"):
        wins = [([np.asarray(v, float) for v in tr], dur) for tr, dur in stats[kind]["windows"]]
        vals = [fano(burst_rows(wins, w)) for w in FANO_WINDOWS]
        put(work, f"gen_{kind}_fano", [round(v, 2) for v in vals])
        # the same statistic split by each ROI's own rate: where the gap comes from
        strata = {}
        for name, lo_hz, hi_hz, _ in RATE_BANDS + (("under_50", 0.0, 0.05, ""),):
            sub = [([v for v in tr if lo_hz <= v.size / dur < hi_hz], dur) for tr, dur in wins]
            strata[name] = {f"w{w}": round(fano(burst_rows(sub, w)), 2) for w in (30, 300)}
            strata[name]["n_roi"] = len(burst_rows(sub, 30))
        put(work, f"gen_{kind}_fano_by_rate", strata)
        band_rows[kind] = strata
        fano_curves.append(hv.Curve((list(FANO_WINDOWS), vals), "fano_w", "fano", label={"real": "recorded"}.get(kind, kind)).opts(
            color=colours[kind], line_width=2.2)
            * hv.Scatter((list(FANO_WINDOWS), vals), "fano_w", "fano").opts(color=colours[kind],
                                                                            size=7))
    cd = hv.Overlay(fano_curves).opts(width=520, height=280, toolbar=None, show_grid=True,
                                      logx=True, xticks=[(30, "30s"), (60, "1m"), (120, "2m"), (300, "5m")], xlim=(26, 340),
                                      xlabel="window length (log scale)",
                                      ylabel="D · bunching (variance ÷ average count)",
                                      legend_position="top_left",
                                      fontsize={"ylabel": "9pt", "xlabel": "9pt"})
    # E: bunching in 30 s windows by each ROI's own rate — where the simulator goes wrong
    ev = []
    for kind in ("real", "fitted"):
        xs_ = [i + (-0.12 if kind == "real" else 0.12) for i in range(len(RATE_BANDS))]
        ys_ = [band_rows[kind][b[0]]["w30"] for b in RATE_BANDS]
        ev.append(hv.Scatter((xs_, ys_), "band", "fano_band").opts(color=colours[kind], size=11))
    ce = hv.Overlay(ev).opts(
        width=1060, height=240, toolbar=None, show_grid=True, logy=True, ylim=(0.8, 20),
        yticks=[(1, "1"), (2, "2"), (5, "5"), (10, "10"), (20, "20")],
        xticks=[(i, b[3]) for i, b in enumerate(RATE_BANDS)], xlim=(-0.5, len(RATE_BANDS) - 0.5),
        xlabel="event rate of the ROI in its baseline", ylabel="E · bunching, 30 s windows",
        fontsize={"ylabel": "9pt", "xlabel": "9pt"}, shared_axes=False)
    items += [sub_head(pn, "C, D · real baselines against simulations matched to each one "
                           "(fast stream)"),
              pn.pane.HoloViews(hv.Layout([ch, cd]).cols(2).opts(shared_axes=False,
                                                                 toolbar=None)),
              sub_head(pn, "E · the same bunching, split by how busy each ROI is"),
              key_html(pn, [glyph("●", colours["real"], "recorded"),
                            glyph("●", colours["fitted"], "fitted simulation")]),
              pn.pane.HoloViews(ce)]
    put(work, "bench", dict(n_roi=rec["n_roi"], minutes=rec["duration_sec"] / 60,
                            n_planted=sum(rec["n_per_level"]),
                            per_level=rec["n_per_level"][0],
                            participation_pct=[int(round(p * 100)) for p in rec["participation"]],
                            jitter_s=rec["jitter_sec"], min_sep_s=rec["min_sep_sec"],
                            hot_min=[hw[0] / 60, hw[1] / 60], hot_rate_mhz=rec["hot_rate_hz"] * 1000,
                            ramp_s=rec["ramp_sec"],
                            n_distractors=rec["n_distractors"],
                            distractor_pct=int(round(rec["distractor_frac"] * 100)),
                            distractor_window_min=[rec["distractor_window"][0] / 60,
                                                   rec["distractor_window"][1] / 60],
                            quiet_mhz=round(bench.REGIMES["baseline_quiet"]["bg_rate_hz"] * 1000, 1),
                            busy_mhz=round(bench.REGIMES["baseline_busy"]["bg_rate_hz"] * 1000, 1),
                            burst_bins_min=[b / 60 for b in rec["bg_burst_bin_sec"]],
                            gen_seed=GEN_SEED, mech_seed=SEED,
                            precision_ceiling=round(sum(rec["n_per_level"])
                                                    / (sum(rec["n_per_level"]) + rec["n_distractors"]), 2)))
    png = save_figure(items, work, "fig10_generator")
    print("  wrote", png.name)


# ----------------------------------------------------------------------- sweeps and shipped
def _bakeoff_seeds():
    from bugarach.bench import fold_split
    return fold_split(n_folds=4, seeds_per_fold=6).seeds


def _sweep_one(job):
    det, regime = job
    from bugarach import bench
    op = bench.OPERATING_POINTS[det]
    curve = bench.sweep(det, regime, _bakeoff_seeds())
    return f"{det}|{regime}", dict(
        knob=op.knob, shipped=op.params[op.knob],
        rows=[dict(v=r.knob_value, f1=r.f1, recall=r.recall, precision=r.precision,
                   probe_per_min=r.hot_fa_per_min) for r in curve])


def stage_sweeps(work: Path, workers: int = 12) -> None:
    jobs = [(d, r) for r in ("baseline_quiet", "baseline_busy") for d in CODED]
    with ProcessPoolExecutor(workers) as ex:
        res = dict(ex.map(_sweep_one, jobs))
    (work / "sweeps.json").write_text(json.dumps(res, indent=1))
    print("  wrote sweeps.json")


def _shipped_one(job):
    det, regime = job
    from bugarach import bench
    r = bench.evaluate(det, regime, _bakeoff_seeds())
    return f"{det}|{regime}", dict(f1=r.f1, recall=r.recall, precision=r.precision,
                                   probe_per_min=r.hot_fa_per_min,
                                   by_frac={f"p{round(k * 100)}": r.recall_at(k) for k in r.by_frac})


def stage_shipped(work: Path, workers: int = 12) -> None:
    """The hand-written detectors at the settings Figures 3–8 and 15–18 use, on the same 24
    recordings the rounds score. Those settings were not chosen on these recordings."""
    jobs = [(d, r) for r in ("baseline_quiet", "baseline_busy") for d in CODED]
    with ProcessPoolExecutor(workers) as ex:
        res = dict(ex.map(_shipped_one, jobs))
    (work / "shipped.json").write_text(json.dumps(res, indent=1))
    for k, v in res.items():
        det, regime = k.split("|")
        put(work, f"shipped_{regime}_{det}", v)
    print("  wrote shipped.json")


def _stored_one(job):
    det, regime, seed = job
    from bugarach import bench
    from bugarach.score import score_stream
    s, gt = bench.make_recording(regime, seed)
    return (det, regime, seed), score_stream(gt, bench.run_detector(det, s))


def stage_stored(work: Path, workers: int = 12) -> None:
    """Each hand-written detector at its stored setting, on the 24 recordings the rounds
    score (seeds 1000-1023), pooled over all 24 and, for the spread, over each group of six.

    No setting was chosen on these recordings: ``tools/retune_operating_points.py`` chose
    the 2026-09-16 values on seeds 1-48. So unlike ``shipped``, which reports the same run
    beside the rounds, this is the score to quote for the settings as they stand."""
    from bugarach import bench
    split = bench.fold_split(n_folds=4, seeds_per_fold=6)
    regimes = ("baseline_quiet", "baseline_busy")
    jobs = [(d, r, s) for r in regimes for d in CODED for s in split.seeds]
    with ProcessPoolExecutor(workers) as ex:
        res = dict(ex.map(_stored_one, jobs))
    per = split.seeds_per_fold
    for r in regimes:
        for d in CODED:
            scores = [res[(d, r, s)] for s in split.seeds]
            pooled = bench.pool_scores(scores, detector=d, regime=r, seeds=split.seeds)
            groups = [bench.pool_scores(scores[i * per:(i + 1) * per], detector=d, regime=r,
                                        seeds=split.seeds[i * per:(i + 1) * per])
                      for i in range(split.n_folds)]
            op = bench.OPERATING_POINTS[d]
            put(work, f"stored_{r}_{d}", dict(
                f1=pooled.f1, f1_min=min(g.f1 for g in groups), f1_max=max(g.f1 for g in groups),
                recall=pooled.recall, precision=pooled.precision,
                probe_per_min=pooled.hot_fa_per_min,
                probe_max_group=max(g.hot_fa_per_min for g in groups),
                recall_by_pct={f"p{round(k * 100)}": pooled.recall_at(k) for k in pooled.by_frac},
                knob=op.knob, value=op.params[op.knob]))
            print(f"  {r:15s} {d:7s} F1 {pooled.f1:.3f} ({min(g.f1 for g in groups):.3f}"
                  f"–{max(g.f1 for g in groups):.3f})  empty-stretch {pooled.hot_fa_per_min:.2f}/min")
    put(work, "stored_rounds", dict(n_recordings=len(split.seeds), n_groups=split.n_folds,
                                    per_group=per, seeds=[split.seeds[0], split.seeds[-1]]))


#: Recordings no setting and no model has seen: the rounds use seeds 1000-1023.
BLOCK_SEEDS = tuple(range(2000, 2024))
BLOCK_SIZES = (0.30, 0.18, 0.10)
#: Inside the busy block, clear of its 30 s ease-in and of its edges.
BLOCK_PLACE = (1240.0, 1460.0)


def _block_events(seed, frac, hot_rate_hz=None):
    """A bench recording whose decoys are moved into the busy block at one event size.

    A decoy is built exactly as a planted event is (`simulate.py`), so two of them placed
    inside the block are planted events there in all but name. The bench keeps planted
    events out of the block on purpose; this is the recording that asks what that hides.
    The recording then has no decoys outside the block. Draws are repeated with a new seed
    until the two sit at least the bench's own spacing apart (120 s), so the inside events
    are no more crowded than the planted ones outside. ``hot_rate_hz`` makes the block busier.
    """
    from bugarach.bench import BENCH_RECORDING, make_recording
    extra = {} if hot_rate_hz is None else {"hot_rate_hz": hot_rate_hz}
    sep = BENCH_RECORDING["min_sep_sec"]
    for attempt in range(200):
        s, gt = make_recording("baseline_quiet", seed + 100_000 * attempt, n_distractors=2,
                               distractor_frac=frac, distractor_window=BLOCK_PLACE,
                               distractor_jitter=BENCH_RECORDING["jitter_sec"], **extra)
        t = sorted(d.time for d in gt.distractors)
        if t[1] - t[0] >= sep:
            return s, gt
    raise RuntimeError(f"seed {seed}: no draw put the two block events {sep:g} s apart")


def _wilson(k, n, z=1.96):
    """95% interval for a proportion, usable at 0 and at n."""
    if n == 0:
        return (float("nan"), float("nan"))
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * np.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return (max(0.0, c - h), min(1.0, c + h))


def _blockrecall_one(job):
    seed, frac, work, hot = job
    from types import SimpleNamespace
    from bugarach import bench
    from bugarach.score import TOL_SEC, score_detections, score_stream
    s, gt = _block_events(seed, frac, hot)
    inside = SimpleNamespace(times=[d.time for d in gt.distractors], events=gt.distractors,
                             params={}, distractors=[])
    models = load_models(Path(work))
    out = {}
    for det in list(CODED) + [n for n in LEARNED if n not in CONTROLS and n in models]:
        r = bench.run_detector(det, s) if det in CODED else models[det].predict(s)[0]
        on, wd = ((r.onset_sec, r.width_sec) if hasattr(r, "onset_sec") else (r.locs, r.widths))
        if det == "sce":   # score each call over its own bin (see _sce_rescore_one)
            bw = float(bench.OPERATING_POINTS["sce"].params["bin_width_sec"])
            wd = np.full(np.asarray(on).size, bw)
        sc_out = score_detections(gt, on, widths=wd)
        sc_in = score_detections(inside, on, widths=wd)
        n, h = sc_out.by_frac.get(frac, (0, 0))
        # A detector calling all through the block "finds" anything placed there. So also
        # ask how often a block moment with no event in reach sits within the tolerance
        # of a call: recall means something only above that.
        lo = np.asarray(on, float)
        hi = lo + np.where(np.isfinite(np.asarray(wd, float)), np.asarray(wd, float), 0.0)
        grid = np.arange(BLOCK_PLACE[0], BLOCK_PLACE[1], 1.0)
        far = np.all([np.abs(grid - t) > 10.0 for t in inside.times], axis=0)
        grid = grid[far]
        near = [bool(np.any((hi >= g - TOL_SEC) & (lo <= g + TOL_SEC))) for g in grid]
        # calls that start in the block but nowhere near the two events: false alarms, per
        # minute, for these very copies on these very recordings
        start_ok = ((lo >= BLOCK_PLACE[0]) & (lo < BLOCK_PLACE[1])
                    & np.all([np.abs(lo - t) > 10.0 for t in inside.times], axis=0))
        minutes = (BLOCK_PLACE[1] - BLOCK_PLACE[0] - 20.0 * len(inside.times)) / 60.0
        out[det] = dict(in_n=int(sc_in.n_planted), in_hit=int(sc_in.n_hit), out_n=int(n),
                        out_hit=int(h), chance=float(np.mean(near)) if near else float("nan"),
                        block_calls=int(start_ok.sum()), block_minutes=minutes)
    return f"{seed}|{frac}", out


def stage_blockrecall(work: Path, workers: int = 12) -> None:
    """Recall for planted-style events inside the busy block, against the same recordings'
    planted events outside it, every detector at its shipped setting (learned: the single
    copies). The block's calls are left out of precision, so without this a detector that
    goes blind inside the block loses nothing on the bench."""
    from bugarach.bench import BENCH_RECORDING
    base_rate = BENCH_RECORDING["hot_rate_hz"]

    def run(hot, name):
        cache = work / name
        if cache.exists():
            return json.loads(cache.read_text())
        jobs = [(seed, f, str(work), hot) for seed in BLOCK_SEEDS for f in BLOCK_SIZES]
        with ProcessPoolExecutor(workers) as ex:
            got = dict(ex.map(_blockrecall_one, jobs))
        if CARRY is not None:
            old = json.loads((CARRY / name).read_text())
            for k, v in got.items():
                v.update({d: r for d, r in old[k].items() if d in LEARNED and d not in v})
        cache.write_text(json.dumps(got, indent=1))
        return got

    def summarise(res):
        out = {}
        for det in next(iter(res.values())):
            row = {}
            for f in BLOCK_SIZES:
                per = [res[f"{seed}|{f}"][det] for seed in BLOCK_SEEDS]
                i_n, i_h = sum(p["in_n"] for p in per), sum(p["in_hit"] for p in per)
                o_n, o_h = sum(p["out_n"] for p in per), sum(p["out_hit"] for p in per)
                ch = float(np.nanmean([p["chance"] for p in per]))
                inside = i_h / i_n
                row[f"p{round(f * 100)}"] = dict(
                    inside=inside, outside=o_h / o_n, n_inside=i_n, n_outside=o_n, chance=ch,
                    inside_ci=_wilson(i_h, i_n), outside_ci=_wilson(o_h, o_n),
                    # recall above chance, as a share of what chance leaves to find
                    # undefined when chance alone already reaches nearly everything
                    inside_corrected=(max(0.0, (inside - ch) / (1 - ch)) if ch < 0.9
                                      else float("nan")))
            allp = [res[f"{seed}|{f}"][det] for seed in BLOCK_SEEDS for f in BLOCK_SIZES]
            row["calls_per_min"] = (sum(p["block_calls"] for p in allp)
                                    / sum(p["block_minutes"] for p in allp))
            out[det] = row
        return out

    res = run(None, "blockrecall.json")
    summary = summarise(res)
    dets = list(summary)
    hot3 = summarise(run(3 * base_rate, "blockrecall_hot3x.json"))
    put(work, "blockrecall", dict(per_detector=summary, n_seeds=len(BLOCK_SEEDS),
                                  n_recordings=len(BLOCK_SEEDS) * len(BLOCK_SIZES),
                                  events_per_recording=2, events_per_size=2 * len(BLOCK_SEEDS),
                                  seeds=[BLOCK_SEEDS[0], BLOCK_SEEDS[-1]],
                                  block_mhz=round(1000 * base_rate),
                                  min_gap_s=BENCH_RECORDING["min_sep_sec"]))
    put(work, "blockrecall_hot3x", dict(per_detector=hot3, block_mhz=round(3000 * base_rate)))
    for det, row in summary.items():
        print(f"  {det:18s} " + "  ".join(f"{k}: in {v['inside']:.2f} out {v['outside']:.2f}"
                                           for k, v in row.items() if k.startswith("p"))
              + f"  block calls/min {row['calls_per_min']:.2f}")

    hv, pn = _hv()
    from make_group_raster_summary import LANE_COLORS
    ticks = [(i, NAMES[d]) for i, d in enumerate(dets)]
    panels = []
    for j, f in enumerate(BLOCK_SIZES):
        key = f"p{round(f * 100)}"
        x = np.arange(len(dets))
        yd, xd = f"br_{key}", f"brx_{key}"
        out_ = np.array([summary[d][key]["outside"] for d in dets])
        in_ = np.array([summary[d][key]["inside"] for d in dets])
        ch = np.array([summary[d][key]["chance"] for d in dets])
        oci = [summary[d][key]["outside_ci"] for d in dets]
        ici = [summary[d][key]["inside_ci"] for d in dets]
        xo, xi_ = x - 0.16, x + 0.16
        # hollow where recall inside the block is within 0.1 of chance: found by luck
        lucky = in_ - ch < 0.1
        seg = [xd, yd, f"{xd}1", f"{yd}1"]
        el = (hv.Segments([(a, o, b, i) for a, b, o, i in zip(xo, xi_, out_, in_)], seg).opts(
                  color="#cfcfcf", line_width=2)
              * hv.Segments([(a, lo, a, hi) for a, (lo, hi) in zip(xo, oci)], seg).opts(
                  color="#111", line_width=1.5)
              * hv.Segments([(a, lo, a, hi) for a, (lo, hi) in zip(xi_, ici)], seg).opts(
                  color="#c77a12", line_width=1.5)
              * hv.Scatter((xi_, ch), xd, yd).opts(marker="dash", size=26, color="#9e9e9e",
                                                   line_width=3)
              * hv.Scatter((xo, out_), xd, yd).opts(color="#111", size=10)
              * hv.Scatter((xi_[~lucky], in_[~lucky]), xd, yd).opts(color="#c77a12", size=11)
              * hv.Scatter((xi_[lucky], in_[lucky]), xd, yd).opts(
                  color="#c77a12", size=11, fill_alpha=0, line_width=2.5))
        last = j == len(BLOCK_SIZES) - 1
        panels.append(el.opts(
            width=1060, height=200 + (70 if last else 0), ylim=(-0.04, 1.06),
            xlim=(-0.6, len(dets) - 0.4), xticks=ticks, xrotation=35 if last else 0,
            ylabel=f"{'ABC'[j]} · {round(f * 100)}% of ROIs · recall (0–1)", xlabel="",
            toolbar=None, show_grid=True, shared_axes=False,
            fontsize={"ylabel": "9pt", "xticks": "9pt"}, **({} if last else {"xaxis": None})))
    items = [key_html(pn, [glyph("●", "#111", "recall outside the busy block (left)"),
                           glyph("●", "#c77a12", "recall inside it (right)"),
                           glyph("○", "#c77a12", "inside, within 0.1 of chance"),
                           glyph("▬", "#9e9e9e", "chance line"),
                           glyph("│", "#555", "95% range")]),
             *[pn.pane.HoloViews(p) for p in panels]]
    png = save_figure(items, work, "fig13_blockrecall")
    print("  wrote", png.name)

    # the trade-off in one picture: false alarms in a busy stretch against what is still
    # found there, for the same copies on the same recordings
    NO_INFO = -0.08          # where a detector whose chance line reaches ~everything sits

    def xy(summ, d):
        y_ = summ[d]["p18"]["inside_corrected"]
        return max(summ[d]["calls_per_min"], 0.01), (NO_INFO if not np.isfinite(y_) else y_)
    base = {d: xy(summary, d) for d in dets}
    tri = {d: xy(hot3, d) for d in dets}
    links = hv.Segments([(base[d][0], base[d][1], tri[d][0], tri[d][1]) for d in dets],
                        ["tx", "ty", "tx1", "ty1"]).opts(color="#b5b5b5", line_width=1.5,
                                                         line_dash="dotted")
    pts = hv.Overlay([hv.Scatter(([base[d][0]], [base[d][1]]), "tx", "ty").opts(
        color=LANE_COLORS.get(d, "#555"), size=16, line_color="#111", line_width=0.8)
        for d in dets])
    pts3 = hv.Overlay([hv.Scatter(([tri[d][0]], [tri[d][1]]), "tx", "ty").opts(
        color=LANE_COLORS.get(d, "#555"), size=13, fill_alpha=0, line_width=2.5)
        for d in dets])
    # hand-placed labels where points coincide (log x: offsets are factors)
    nudge = {"cicada": (1.25, -0.02), "sce": (1.25, 0.05), "tube_ratio": (1.25, 0.05),
             "tube_ratio_guard": (1.25, -0.06), "tube": (1.2, -0.05), "sync": (0.25, 0.05)}
    labels = hv.Labels([(base[d][0] * nudge.get(d, (1.2, 0.035))[0],
                         base[d][1] + nudge.get(d, (1.2, 0.035))[1],
                         NAMES[d] + (" (no information)" if base[d][1] == NO_INFO else ""))
                        for d in dets], ["tx", "ty"], "name").opts(
        text_font_size="10pt", text_align="left", text_color="#222")
    corner = hv.Rectangles([(0.006, 0.5, 1.0, 1.05)]).opts(color="#dfe9d8", line_alpha=0)
    trade = (corner * links * pts3 * pts * labels).opts(
        width=1060, height=480, logx=True, xlim=(0.006, 120), ylim=(-0.2, 1.1),
        xticks=[(0.01, "0.01"), (0.1, "0.1"), (1, "1"), (10, "10"), (100, "100")],
        yticks=[(NO_INFO, "chance"), (0, "0"), (0.2, "0.2"), (0.4, "0.4"), (0.6, "0.6"),
                (0.8, "0.8"), (1, "1")],
        xlabel="false alarms per minute inside the busy block (log scale; 0.01 means fewer)",
        ylabel="mid-sized events found inside it, beyond chance (0–1)",
        toolbar=None, show_grid=True, shared_axes=False,
        fontsize={"ylabel": "9pt", "xlabel": "9pt"})
    items = [key_html(pn, [glyph("●", "#555", f"busy block as in the bench "
                                              f"(+{round(1000 * base_rate)} mHz per ROI)"),
                           glyph("○", "#555", f"three times busier "
                                              f"(+{round(3000 * base_rate)} mHz)"),
                           "<span style='background:#dfe9d8;padding:0 6px'>shaded</span> "
                           "fewer than 1 false alarm a minute and at least half the events "
                           "chance leaves still found"]),
             pn.pane.HoloViews(trade)]
    png = save_figure(items, work, "fig19_tradeoff")
    print("  wrote", png.name)


def _sce_rescore_one(job):
    """binned SCE on one bench recording at every value on its list, scored two ways.

    `sce_detect` reports a call as starting at its bin but only as wide as the spread of
    the events inside (`width_sec = tlast - tfirst`, the MATLAB contract). The scorer reads
    that as the call's stretch, which starts at the bin edge and can end before the events
    it was made on. With merging off (the shipped default), a call's own bin is exactly
    [onset, onset + bin width], so the second score uses that.
    """
    regime, seed = job
    from bugarach import bench
    from bugarach.score import score_detections, score_stream
    op = bench.OPERATING_POINTS["sce"]
    s, gt = bench.make_recording(regime, seed)
    out = {}
    for v in op.grid:
        det = bench.run_detector("sce", s, **{op.knob: v})
        bw = float(op.params["bin_width_sec"])
        for tag, sc in (("as_shipped", score_stream(gt, det)),
                        ("full_bin", score_detections(gt, det.onset_sec,
                                                      widths=np.full(det.onset_sec.size, bw)))):
            out[f"{v}|{tag}"] = dict(n_planted=sc.n_planted, n_detected=sc.n_detected,
                                    n_hit=sc.n_hit, n_fa=sc.n_fa, hot_fa=sc.hot_fa,
                                    distractor_hits=sc.distractor_hits, tol_sec=sc.tol_sec,
                                    by_frac={str(k): list(n) for k, n in sc.by_frac.items()})
    return f"{regime}|{seed}", out


def stage_sce_rescore(work: Path, workers: int = 12) -> None:
    """How much the span mismatch costs binned SCE, through the same rounds as Section 7."""
    from types import SimpleNamespace
    from bugarach import bench
    op = bench.OPERATING_POINTS["sce"]
    split = bench.fold_split(n_folds=4, seeds_per_fold=6)
    cache = work / "sce_rescore.json"
    if cache.exists():
        res = json.loads(cache.read_text())
    else:
        jobs = [(r, sd) for r in ("baseline_quiet", "baseline_busy") for sd in split.seeds]
        with ProcessPoolExecutor(workers) as ex:
            res = dict(ex.map(_sce_rescore_one, jobs))
        cache.write_text(json.dumps(res))

    def pooled(regime, seeds, v, tag):
        scs = []
        for sd in seeds:
            d = dict(res[f"{regime}|{sd}"][f"{v}|{tag}"])
            d["by_frac"] = {float(k): tuple(n) for k, n in d["by_frac"].items()}
            scs.append(SimpleNamespace(**d))
        return bench.pool_scores(scs, detector="sce", regime=regime, seeds=seeds)

    out = {}
    for regime in ("baseline_quiet", "baseline_busy"):
        row = {}
        for tag in ("as_shipped", "full_bin"):
            f1s, small = [], []
            for held in range(4):
                best_v, best_f1 = None, -1.0
                for v in op.grid:                       # loosest first; ties keep the looser
                    p = pooled(regime, split.train(held), v, tag)
                    if np.isfinite(p.f1) and p.f1 > best_f1:
                        best_f1, best_v = p.f1, v
                p = pooled(regime, split.test(held), best_v, tag)
                f1s.append(p.f1)
                small.append(p.recall_at(0.10))
            sh = pooled(regime, split.seeds, op.params[op.knob], tag)
            row[tag] = dict(tuned_f1=float(np.mean(f1s)), tuned_f1_min=float(min(f1s)),
                            tuned_f1_max=float(max(f1s)), tuned_small=float(np.mean(small)),
                            shipped_f1=float(sh.f1), shipped_recall=float(sh.recall),
                            shipped_precision=float(sh.precision))
        out[regime.split("_")[1]] = row
        print(f"  {regime}: " + "  ".join(f"{t}: tuned {v['tuned_f1']:.3f} shipped {v['shipped_f1']:.3f}"
                                         for t, v in row.items()))
    put(work, "sce_rescore", out)


def _bakeoff(bakeoff: Path, regime: str) -> dict:
    """The three training-seed runs of one background level: hand-written results from
    seed 0 (they do not depend on it — checked), learned results from all three."""
    files = sorted((bakeoff / regime).glob("bakeoff*.json"))
    if len(files) != 3:
        raise SystemExit(f"{bakeoff / regime}: want 3 bakeoff files, found {len(files)}")
    runs = [json.loads(f.read_text()) for f in files]
    a, b = runs[0]["hand_written"], runs[1]["hand_written"]
    for det in a:
        if [f["f1"] for f in a[det]["per_fold"]] != [f["f1"] for f in b[det]["per_fold"]]:
            raise SystemExit(f"{det}: hand-written results differ between training seeds")
    return dict(runs=runs, files=files, coded=runs[0]["hand_written"],
                learned={n: [r["learned"][n] for r in runs] for n in runs[0]["learned"]})


# ----------------------------------------------------------------------- optimization
KNOB_LABEL = {"rate": "bar: events per second above the average",
              "coact": "chance allowed per bin (1 in …)",
              "loco": "bar: percentile of surrogate counts",
              "sce": "bar: percentile of surrogate counts",
              "cicada": "bar: percentile of surrogate counts",
              "sync": "bar: average score (0–1)"}


def _tick(det, v):
    if det == "coact":
        return f"{1 / v:,.0f}"
    return f"{v:.10g}"


def stage_optimization(work: Path, bakeoff: Path) -> None:
    hv, pn = _hv()
    from bugarach import bench
    from bugarach.score import TOL_SEC
    from bugarach.ui.app import _time_axis_hook

    sweeps = json.loads((work / "sweeps.json").read_text())
    quiet, busy = _bakeoff(bakeoff, "baseline_quiet"), _bakeoff(bakeoff, "baseline_busy")
    seeds = quiet["runs"][0]["seeds"]
    per_fold = int(quiet["runs"][0]["seeds_per_fold"])
    n_folds = int(quiet["runs"][0]["folds"])

    # ---- A: the scoring rule, drawn -------------------------------------------------
    ext = (0.0, 60.0)
    planted = [12.0, 31.0, 50.0]
    calls = [(11.2, 1.4), (33.0, 0.8), (40.0, 1.0), (31.4, 0.6)]
    yd = "score_demo"
    tol = TOL_SEC
    el = hv.Scatter(([ext[0]], [0.0]), "t", yd).opts(alpha=0)
    for p in planted:
        el = el * hv.Rectangles([(p - tol, 1.55, p + tol, 2.45)]).opts(color="#dfe9d8",
                                                                       line_alpha=0)
    el = (el * hv.Scatter((planted, [2.0] * 3), "t", yd).opts(
        marker="inverted_triangle", size=13, color="#111")
        * hv.Rectangles([(a, 0.7, a + w, 1.3) for a, w in calls]).opts(color="#0B5FFF",
                                                                        line_alpha=0))
    for x, y, txt in [(12.0, 0.25, f"hit: the call covers\nor sits within {TOL_SEC:g} s"),
                      (31.2, 0.25, "hit, plus a second call\non it (a false alarm)"),
                      (40.5, 0.25, "false alarm:\nnothing planted"),
                      (50.0, 0.25, f"miss: no call\nwithin {TOL_SEC:g} s")]:
        el = el * hv.Text(x, y, txt).opts(text_font_size="9pt", text_color="#333")
    panel_a = el.opts(width=1060, height=170, xlim=ext, ylim=(-0.6, 2.7), toolbar=None,
                      yticks=[(2, "planted"), (1, "calls")], ylabel="", xlabel="time",
                      hooks=[_time_axis_hook], shared_axes=False, fontsize={"yticks": "9pt"})

    # ---- B: the rounds ----------------------------------------------------------------
    rects_tr, rects_te = [], []
    for held in range(n_folds):
        for i, _ in enumerate(seeds):
            box = (i + 0.08, n_folds - 1 - held + 0.15, i + 0.92, n_folds - 1 - held + 0.85)
            (rects_te if i // per_fold == held else rects_tr).append(box)
    panel_b = (hv.Rectangles(rects_tr).opts(color="#d9d9d9", line_alpha=0)
               * hv.Rectangles(rects_te).opts(color="#0B5FFF", line_alpha=0)).opts(
        width=1060, height=150, xlim=(0, len(seeds)), ylim=(0, n_folds), toolbar=None,
        yticks=[(n_folds - 0.5 - h, f"round {h + 1}") for h in range(n_folds)],
        xticks=[(i + 0.5, str(i + 1)) for i in range(0, len(seeds), 3)],
        xlabel="simulated recording", ylabel="", shared_axes=False,
        fontsize={"yticks": "9pt", "xlabel": "9pt"})

    # ---- C: the sweeps ------------------------------------------------------------------
    plots = []
    for det in CODED:
        c = sweeps[f"{det}|baseline_quiet"]
        vals = [r["v"] for r in c["rows"]]
        idx = np.arange(len(vals))
        f1 = np.array([r["f1"] for r in c["rows"]])
        rec = np.array([r["recall"] for r in c["rows"]])
        prec = np.array([r["precision"] for r in c["rows"]])
        probe = np.array([r["probe_per_min"] for r in c["rows"]])
        ceiling = bench.MAX_PROBE_PER_MIN[det]
        xd, ydd = f"knob_{det}", f"f1_{det}"
        ov = (hv.Scatter((idx, rec), xd, ydd).opts(color="#5a8fb0", marker="triangle", size=6)
              * hv.Scatter((idx, prec), xd, ydd).opts(color="#b08a3c", marker="square", size=5)
              * hv.Scatter((idx, f1), xd, ydd).opts(color="#222", size=7))
        over = probe > ceiling
        if over.any():
            # a square, not ✕: ✕ already means "false alarm" in Figures 3–9
            ov = ov * hv.Scatter((idx[over], f1[over]), xd, ydd).opts(
                marker="square", size=15, fill_alpha=0, line_color="#b3261e", line_width=2)
        picks = [f["knob_value"] for f in quiet["coded"][det]["per_fold"]]
        uniq = np.unique([vals.index(p) for p in picks])
        ov = ov * hv.Scatter((uniq, f1[uniq]), xd, ydd).opts(
            marker="circle", size=17, fill_alpha=0, line_color="#1a7f37", line_width=2.5)
        if c["shipped"] in vals:
            si = vals.index(c["shipped"])
            ov = ov * hv.Scatter(([si], [f1[si]]), xd, ydd).opts(
                marker="diamond", size=12, fill_alpha=0, line_color="#7A00E6", line_width=2.5)
        plots.append(ov.opts(
            width=345, height=230, ylim=(0, 1.02), xlim=(-0.6, len(vals) - 0.4), toolbar=None,
            show_grid=True, xticks=[(i, _tick(det, v)) for i, v in enumerate(vals)],
            xlabel=KNOB_LABEL[det], ylabel=f"{NAMES[det]} · score (0–1)",
            fontsize={"xticks": "8pt", "labels": "8pt"}, xrotation=45, shared_axes=False))
    for det in CODED:
        vals = [r["v"] for r in sweeps[f"{det}|baseline_quiet"]["rows"]]
        for regime, bk in (("quiet", quiet), ("busy", busy)):
            rows = sweeps[f"{det}|baseline_{regime}"]["rows"]
            picks = [f["knob_value"] for f in bk["coded"][det]["per_fold"]]
            f1s = [r["f1"] for r in rows]
            ties = sum(abs(f - f1s[0]) < 1e-9 for f in f1s)
            ceiling = bench.MAX_PROBE_PER_MIN[det]
            probe_by_v = {r["v"]: r["probe_per_min"] for r in rows}
            put(work, f"opt_{regime}_{det}", dict(
                picks=[_tick(det, p) for p in picks],
                n_lowest=sum(p == vals[0] for p in picks),
                lowest=_tick(det, vals[0]), highest=_tick(det, vals[-1]),
                n_tied_at_low_end=ties,
                picks_over_limit=sum(probe_by_v[p] > ceiling for p in picks),
                sweep_f1_min=min(f1s), sweep_f1_max=max(f1s),
                shipped_on_list=shipped(det)[bench.OPERATING_POINTS[det].knob] in vals))
    put(work, "tol_s", TOL_SEC)
    put(work, "rounds", dict(n_recordings=len(seeds), n_folds=n_folds, per_fold=per_fold,
                             n_train_groups=n_folds - 1, n_choose=(n_folds - 1) * per_fold))
    put(work, "ceilings", bench.MAX_PROBE_PER_MIN)
    items = [sub_head(pn, "A · how a call is scored against the answer key"),
             pn.pane.HoloViews(panel_a),
             sub_head(pn, "B · four rounds: blue recordings are scored; gray ones are used to "
                          "choose the setting, or to train"),
             pn.pane.HoloViews(panel_b)]
    png = save_figure(items, work, "fig11_grading")
    print("  wrote", png.name)
    items = [key_html(pn, [glyph("●", "#222", "F1 score"), glyph("▲", "#5a8fb0", "recall"),
                           glyph("■", "#b08a3c", "precision"),
                           glyph("○", "#1a7f37", "chosen in at least one round"),
                           glyph("◇", "#7A00E6", "the setting it ships with"),
                           glyph("□", "#b3261e",
                                 f"breaks its busy-block limit (on all {len(seeds)} recordings)")]),
             pn.pane.HoloViews(hv.Layout(plots).cols(3).opts(shared_axes=False, toolbar=None))]
    png = save_figure(items, work, "fig14_settings")
    print("  wrote", png.name)


# ----------------------------------------------------------------------- performance
def _perf_rows(bake: dict, regime: str, work: Path) -> dict:
    """Per detector, through `bugarach.performance` so the page and the project's own table
    agree; recall by event size and per-round busy-block rates are kept locally."""
    from bugarach.bench import BENCH_RECORDING, MAX_PROBE_PER_MIN
    from bugarach.performance import fold_scores_from_bakeoff, performance_table
    coded_scores = [s for s in fold_scores_from_bakeoff(bake["runs"][0]) if s.detector in CODED]
    learned_scores = [s for run in bake["runs"] for s in fold_scores_from_bakeoff(run)
                      if s.detector in LEARNED]
    table = performance_table(coded_scores + learned_scores)
    out = {}
    for det in list(CODED) + list(LEARNED):
        row = table.row(det)
        scores = [s for s in (coded_scores if det in CODED else learned_scores)
                  if s.detector == det]
        levels = sorted({k for s in scores for k in s.by_frac}, key=float, reverse=True)
        per_round = [s.hot_fa_per_min for s in scores]
        ceiling = MAX_PROBE_PER_MIN.get(det)
        folds = (bake["coded"][det]["per_fold"] if det in CODED
                 else [f for run in bake["learned"][det] for f in run["per_fold"]])
        d = dict(family="coded" if det in CODED else "learned",
                 f1=row.f1, f1_min=row.f1_lo, f1_max=row.f1_hi, recall=row.recall,
                 precision=row.precision, probe_per_min=row.probe_per_min,
                 probe_max_round=max(per_round), ceiling=ceiling,
                 rounds_over_limit=(sum(p > ceiling for p in per_round) if ceiling else None),
                 x_realtime=row.detect_x_realtime, n_scores=row.n_folds,
                 f1_per_score=[s.f1 for s in scores],
                 recall_by_pct={f"p{round(float(lv) * 100)}":
                                float(np.nanmean([s.by_frac[lv] for s in scores]))
                                for lv in levels},
                 thresholds=[f.get("threshold") for f in folds if "threshold" in f],
                 # share of decoys with any call in reach: coverage, not a count of calls,
                 # so no precision is rebuilt from it (performance.MAX_DISTRACTOR_RATE)
                 decoys_share=row.distractor_rate)
        out[det] = d
        put(work, f"perf_{regime}_{det}", {k: v for k, v in d.items() if k != "f1_per_score"})
    slow = min(out, key=lambda k: out[k]["x_realtime"])
    fast = max(out, key=lambda k: out[k]["x_realtime"])
    put(work, f"perf_{regime}_slowest", dict(name=NAMES[slow], x=out[slow]["x_realtime"]))
    put(work, f"perf_{regime}_fastest", dict(name=NAMES[fast], x=out[fast]["x_realtime"]))
    return out


def stage_performance(work: Path, bakeoff: Path) -> None:
    hv, pn = _hv()
    order = list(CODED) + list(LEARNED)
    shipped_res = json.loads((work / "shipped.json").read_text())
    rows = {r: _perf_rows(_bakeoff(bakeoff, r), r, work)
            for r in ("baseline_quiet", "baseline_busy")}
    fams = {"coded": "#0B5FFF", "learned": "#7F0000"}
    ticks = [(i, NAMES[d]) for i, d in enumerate(order)]
    # The best a detector that sees only event times can do: find all 15 planted events and
    # every decoy too, since decoys look the same (precision 15/21, recall 1).
    from bugarach.bench import BENCH_RECORDING
    n_p = sum(BENCH_RECORDING["n_per_level"])
    p_max = n_p / (n_p + BENCH_RECORDING["n_distractors"])
    f1_ceiling = 2 * p_max / (1 + p_max)
    put(work, "f1_ceiling", round(f1_ceiling, 2))
    plots = []
    for regime, label in (("baseline_quiet", "quiet"), ("baseline_busy", "busy")):
        xs, ys, cs, mx, my, sx, sy = [], [], [], [], [], [], []
        for i, det in enumerate(order):
            d = rows[regime][det]
            f1 = d["f1_per_score"]
            xs += list(i + np.linspace(-0.22, 0.22, len(f1)))
            ys += f1
            cs += [fams[d["family"]]] * len(f1)
            mx.append(i)
            my.append(d["f1"])
            if det in CODED:
                sx.append(i + 0.32)
                sy.append(shipped_res[f"{det}|{regime}"]["f1"])
        xd, yd = f"det_{regime}", f"f1_{regime}"
        el = (hv.HLine(f1_ceiling).opts(color="#1b7f3b", line_dash="dashed", line_width=1.5)
              * hv.Points((xs, ys, cs), [xd, yd], "c").opts(color="c", size=5, alpha=0.55)
              * hv.Scatter((mx, my), xd, yd).opts(marker="dash", size=26, color="#111", line_width=3)
              * hv.Scatter((sx, sy), xd, yd).opts(marker="diamond", size=11, fill_alpha=0,
                                                  line_color="#7A00E6", line_width=2))
        plots.append(el.opts(width=520, height=300, ylim=(0, 1), xlim=(-0.6, len(order) - 0.4),
                             xticks=ticks, xrotation=55,
                             ylabel=f"A{1 if label == 'quiet' else 2} · {label} background · F1 score (0–1)", xlabel="",
                             toolbar=None, show_grid=True, shared_axes=False,
                             fontsize={"xticks": "8pt", "ylabel": "9pt"}))
    floor = 0.01
    pxs, pys, pcs, cx, cy, sx, sy = [], [], [], [], [], [], []
    useful = [d for d in order if d not in CONTROLS]   # a call spanning the recording: no rate
    for i, det in enumerate(useful):
        d = rows["baseline_quiet"][det]
        pxs.append(i)
        pys.append(max(d["probe_per_min"], floor))
        pcs.append(fams[d["family"]])
        if d["ceiling"] is not None:
            cx.append(i)
            cy.append(d["ceiling"])
        if det in CODED:
            sx.append(i + 0.3)
            sy.append(max(shipped_res[f"{det}|baseline_quiet"]["probe_per_min"], floor))
    probe = (hv.HLine(floor).opts(color="#bbb", line_dash="dotted", line_width=1)
             * hv.Points((pxs, pys, pcs), ["det_p", "probe"], "c").opts(color="c", size=10)
             * hv.Scatter((sx, sy), "det_p", "probe").opts(marker="diamond", size=11, fill_alpha=0,
                                                           line_color="#7A00E6", line_width=2)
             * hv.Scatter((cx, cy), "det_p", "probe").opts(marker="dash", size=26,
                                                           color="#b3261e", line_width=3)).opts(
        width=520, height=320, logy=True, ylim=(0.006, 200), xlim=(-0.6, len(useful) - 0.4),
        xticks=[(i, NAMES[d]) for i, d in enumerate(useful)], xrotation=35, toolbar=None,
        yticks=[(0.01, "0.01"), (0.1, "0.1"), (1, "1"), (10, "10"), (100, "100")],
        ylabel="B · false alarms per minute, busy block", xlabel="", show_grid=True,
        fontsize={"xticks": "9pt", "ylabel": "9pt"}, shared_axes=False)
    shade = {"p30": "#111111", "p18": "#6f6f6f", "p10": "#c8c8c8"}
    uticks = [(i, NAMES[d]) for i, d in enumerate(useful)]
    parts = []
    for k, (regime, label) in enumerate((("baseline_quiet", "quiet"), ("baseline_busy", "busy"))):
        lv_plots = []
        for j, lv in enumerate(("p30", "p18", "p10")):
            xs_ = np.arange(len(useful)) + (j - 1) * 0.24
            ys_ = [rows[regime][d]["recall_by_pct"][lv] for d in useful]
            lv_plots.append(hv.Scatter((xs_, ys_), f"det_c{k}", "rec").opts(
                color=shade[lv], size=9, line_color="#111", line_width=0.8))
        # small events at the setting each hand-written detector ships with
        shx = [i + 0.24 for i, d in enumerate(useful) if d in CODED]
        shy = [shipped_res[f"{d}|{regime}"]["by_frac"]["p10"] for d in useful if d in CODED]
        lv_plots.append(hv.Scatter((shx, shy), f"det_c{k}", "rec").opts(
            marker="diamond", size=11, fill_alpha=0, line_color="#7A00E6", line_width=2))
        parts.append(hv.Overlay(lv_plots).opts(
            width=520, height=300, ylim=(-0.03, 1.05), toolbar=None, show_grid=True,
            xlim=(-0.6, len(useful) - 0.4), xrotation=55, xticks=uticks, xlabel="",
            show_legend=False, ylabel=f"C{k + 1} · {label} background · recall (0–1)",
            fontsize={"ylabel": "9pt", "xticks": "8pt"}, shared_axes=False))
    items = [sub_head(pn, "A · F1 score on simulated recordings the setting or training never saw"),
             key_html(pn, [glyph("●", "#0B5FFF", "hand-written, one round"),
                           glyph("●", "#7F0000", "learned, one round and training run"),
                           glyph("▬", "#111", "average"),
                           glyph("◇", "#7A00E6", "hand-written, at the setting it ships with"),
                           glyph("┅", "#1b7f3b", f"the best F1 possible here ({f1_ceiling:.2f})")]),
             pn.pane.HoloViews(hv.Layout(plots).cols(2).opts(shared_axes=False, toolbar=None)),
             sub_head(pn, "B · false alarms per minute in the busy block, where nothing is "
                          "planted (quiet background)"),
             key_html(pn, [glyph("●", "#0B5FFF", "hand-written, average"),
                           glyph("●", "#7F0000", "learned, average"),
                           glyph("◇", "#7A00E6", "at the setting it ships with"),
                           glyph("▬", "#b3261e", "the limit (hand-written only)"),
                           glyph("┄", "#bbb", "fewer than 0.01 per minute: drawn on this line")]),
             pn.pane.HoloViews(probe.opts(width=1060)),
             sub_head(pn, "C · recall by event size, tuned settings averaged over rounds: "
                          "C1 quiet background, C2 busy background"),
             key_html(pn, [glyph("●", "#111", "large events (30% of ROIs)"),
                           glyph("●", "#6f6f6f", "mid-sized (18%)"),
                           glyph("●", "#c8c8c8", "small (10%)"),
                           glyph("◇", "#7A00E6", "small events at the shipped setting"),
                           "left to right within each detector"]),
             pn.pane.HoloViews(hv.Layout(parts).cols(2).opts(shared_axes=False, toolbar=None))]
    png = save_figure(items, work, "fig12_performance")
    print("  wrote", png.name)

    def cell(v, fmt="{:.2f}"):
        return "—" if v is None or (isinstance(v, float) and not np.isfinite(v)) else fmt.format(v)
    head = ("<tr><th rowspan=2 class=d>detector</th>"
            "<th colspan=2>F1 score, quiet background (0–1)</th>"
            "<th colspan=2>F1 score, busy background (0–1)</th>"
            "<th colspan=3>quiet background (0–1)</th>"
            "<th colspan=4>false alarms per minute in the busy block, quiet background</th>"
            "<th colspan=5>at the setting it ships with</th>"
            "<th rowspan=2>speed, quiet background (times faster than real time)</th></tr>"
            "<tr><th>average</th><th>lowest–highest</th><th>average</th><th>lowest–highest</th>"
            "<th>recall</th><th>precision</th><th>recall, small events</th>"
            "<th>average</th><th>worst round</th><th>limit</th><th>average under the limit?</th>"
            "<th>F1, quiet</th><th>F1, busy</th><th>small events, quiet</th>"
            "<th>small events, busy</th><th>busy-block false alarms per minute, quiet</th></tr>")
    body = []
    for det in order:
        q, b = rows["baseline_quiet"][det], rows["baseline_busy"][det]
        over = q["ceiling"] is not None and q["probe_max_round"] > q["ceiling"]
        ctrl = det in CONTROLS
        sq = shipped_res.get(f"{det}|baseline_quiet")
        sb = shipped_res.get(f"{det}|baseline_busy")
        dash = "—"
        gate = (dash if q["ceiling"] is None or ctrl
                else ("yes" if q["probe_per_min"] <= q["ceiling"] else "no"))
        mark = " (failed control)¹" if ctrl else ("²" if det == "sce" else "")
        body.append(
            f"<tr><td class=d>{NAMES[det]}{mark}</td>"
            f"<td>{cell(q['f1'])}</td><td>{cell(q['f1_min'])}–{cell(q['f1_max'])}</td>"
            f"<td>{cell(b['f1'])}</td><td>{cell(b['f1_min'])}–{cell(b['f1_max'])}</td>"
            f"<td>{cell(q['recall'])}</td>"
            f"<td>{dash if ctrl else cell(q['precision'])}</td>"
            f"<td>{cell(q['recall_by_pct'].get('p10'))}</td>"
            f"<td>{dash if ctrl else cell(q['probe_per_min'], '{:.2f}')}</td>"
            f"<td{' class=over' if over else ''}>{dash if ctrl else cell(q['probe_max_round'], '{:.2f}')}</td>"
            f"<td>{cell(q['ceiling'], '{:g}') if q['ceiling'] is not None else dash}</td>"
            f"<td>{gate}</td>"
            f"<td>{cell(sq['f1']) if sq else dash}</td><td>{cell(sb['f1']) if sb else dash}</td>"
            f"<td>{cell(sq['by_frac']['p10']) if sq else dash}</td>"
            f"<td>{cell(sb['by_frac']['p10']) if sb else dash}</td>"
            f"<td>{cell(sq['probe_per_min'], '{:.2f}') if sq else dash}</td>"
            f"<td>{cell(q['x_realtime'], '{:,.0f}')}</td></tr>")
    (work / "table_performance.html").write_text(
        "<table class=perf><thead>" + head + "</thead><tbody>" + "".join(body)
        + "</tbody></table>", encoding="utf-8")


# ----------------------------------------------------------------------- real data
REAL_ROLES = (("TTX", "ttx"), ("senktide", "senktide"))
GROUP_WORDS = {"DI": "females in diestrus", "MALE": "males",
               "ORX": "males with testes removed", "OVX": "females with ovaries removed"}


def _real_members():
    """One recording per group per treatment: the median-sized fast field of the group,
    as `make_intro_figures.figure1` picks them. Treatment 1 decides the category; the
    whole recording is drawn."""
    from bugarach import dataset
    from bugarach.io import load_folder
    from make_group_raster_summary import _anchor_of
    out = {}
    for label, role in REAL_ROLES:
        folder = dataset.current(role)
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            slices = load_folder(folder)
        picks = []
        for g in GROUPS:
            grp = sorted((s for s in slices
                          if s.meta.get("group_id") == g and _anchor_of(s) is not None),
                         key=lambda s: (s.streams["fast"].n_rois, s.slice_id))
            if grp:
                picks.append(grp[len(grp) // 2])
        out[label] = dict(folder=folder, members=picks,
                          n_in_cohort={g: sum(1 for s in slices if s.meta.get("group_id") == g)
                                       for g in GROUPS})
    return out


def _detect_real(job):
    label, role, slice_id, model_dir = job
    from bugarach import dataset
    from bugarach.detect_folder import detect_slice
    from bugarach.io import load_folder
    from bugarach.learn.checkpoint import load
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        s = next(x for x in load_folder(dataset.current(role)) if x.slice_id == slice_id)
        models = [load(Path(model_dir) / f"{n}.json") for n in LEARNED
                  if (Path(model_dir) / f"{n}.json").exists()]
        events, windows = detect_slice(s, models=models)
    rows = [dict(stream=e.stream, detector=e.detector, onset=float(e.onset_sec),
                 width=float(e.width_sec) if e.width_sec is not None else 0.0,
                 region=e.region_label) for e in events]
    return (label, slice_id), dict(rows=rows, windows=[(w.label, float(w.win_start),
                                                        float(w.win_end)) for w in windows])


def _real_detections(work: Path, workers: int = 8) -> dict:
    cache = work / "real_detections.json"
    if cache.exists():
        return {tuple(k.split("|")): v for k, v in json.loads(cache.read_text()).items()}
    picks = _real_members()
    jobs = [(label, role, s.slice_id, str(work / "models"))
            for label, role in REAL_ROLES for s in picks[label]["members"]]
    with ProcessPoolExecutor(min(workers, len(jobs))) as ex:
        det = dict(ex.map(_detect_real, jobs))
    if CARRY is not None:
        old = json.loads((CARRY / "real_detections.json").read_text())
        for k, v in det.items():
            key = "|".join(k)
            if key not in old:
                raise SystemExit(f"--carry-learned: {key} is not in the earlier build")
            have = {r["detector"] for r in v["rows"]}
            v["rows"] += [r for r in old[key]["rows"] if r["detector"] in LEARNED
                          and r["detector"] not in have]
    cache.write_text(json.dumps({"|".join(k): v for k, v in det.items()}))
    return det


def stage_real(work: Path, workers: int) -> None:
    hv, pn = _hv()
    from bugarach.ui.diagnostic import REGION_FILL
    from make_group_raster_summary import _anchor_of, build_page

    picks = _real_members()
    det = _real_detections(work, workers)
    shown = list(CODED) + [d for d in LEARNED if d not in CONTROLS]
    fig = 15
    for label, _role in REAL_ROLES:
        members = [(s, _anchor_of(s)) for s in picks[label]["members"]]
        put(work, f"real_{label}_cohort", picks[label]["n_in_cohort"])
        lo = min(-a for _, a in members)
        hi = max(max([float(np.nanmax(v)) for st in s.streams.values() for v in st.t50rise
                      if len(v) and np.isfinite(v).any()]
                     + [float(r.end_sec) for r in s.regions or []]) - a for s, a in members)
        ext = (float(np.floor(lo / 60) * 60), float(np.ceil((hi + 30.0) / 60) * 60))
        periods = []
        for s, _ in members:
            for r in s.regions:
                if r.name and r.name not in periods:
                    periods.append(r.name)
        for stream in ("fast", "slow"):
            lanes, summary = {}, {}
            for s, a in members:
                d = det[(label, s.slice_id)]
                wins = d["windows"]
                per, in_win, ctrl_cover = {}, {}, {}
                for dd in list(CODED) + list(LEARNED):
                    rr = [r for r in d["rows"] if r["detector"] == dd and r["stream"] == stream]
                    on = np.array([r["onset"] for r in rr], float)
                    wd = np.array([r["width"] for r in rr], float)
                    inside = np.zeros(on.size, bool)
                    for _, w0, w1 in wins:          # closed, as `detect_folder` counts
                        inside |= (on >= w0) & (on <= w1)
                    in_win[dd] = int(inside.sum())
                    if dd in CONTROLS:
                        span = sum(w1 - w0 for _, w0, w1 in wins)
                        ctrl_cover[dd] = round(float(np.minimum(wd, 1e9).sum()) / span, 2) if span else None
                    else:
                        per[dd] = (on, wd)
                lanes[(s.slice_id, stream)] = per
                # how busy each marked window is: mean events per ROI per second, in mHz,
                # to set beside the simulated busy block (Section 10)
                win_rate = {}
                for wname, w0, w1 in wins:
                    ev = [np.asarray(v, float) for v in s.streams[stream].t50rise]
                    n_ev = sum(int(np.sum((v >= w0) & (v <= w1))) for v in ev)
                    win_rate[wname] = round(1000 * n_ev / (len(ev) * (w1 - w0)), 1)
                summary[s.meta.get("group_id")] = dict(n_roi=s.streams[stream].n_rois,
                                                        calls_in_windows=in_win,
                                                        control_time_covered=ctrl_cover,
                                                        window_rate_mhz=win_rate)
            put(work, f"real_{label}_{stream}", summary)
            # One build per recording, so each lane label can carry that recording's own
            # count inside the marked windows; then one x-axis for the whole figure.
            raster_px = 150
            blocks = []
            for s, a in members:
                n_in = summary[s.meta.get("group_id")]["calls_in_windows"]
                names = {dd: f"{NAMES[dd]} · {n_in[dd]} call{'' if n_in[dd] == 1 else 's'}" for dd in shown}
                with _page_layout(names=names, raster_px=raster_px):
                    b, _ = build_page([(s, a)], ext=ext, manifest={}, width=1060,
                                      stream=stream, lanes={(s.slice_id, stream):
                                                            lanes[(s.slice_id, stream)]},
                                      lane_px=9)
                blocks += b
            flat = [p for _, ps in blocks for p in ps]
            for p in flat[:-1]:
                p.opts(xaxis=None)
            for _, ps in blocks[:-1]:
                ps[-1].opts(height=raster_px)
            items = [key_html(pn, _period_key(periods)
                              + ["lanes: one mark per call; the number beside each name is its "
                                 "calls inside the marked windows"])]
            for sl, panels in blocks:
                panels[-1].opts(ylabel=f"{stream} · {sl.streams[stream].n_rois} ROIs")
                g = sl.meta.get("group_id")
                items.append(pn.pane.HTML(
                    f"<div style='font:12px system-ui,sans-serif;color:#111;margin:9px 0 0 78px'>"
                    f"<b>{g}</b><span style='color:#666'> · {GROUP_WORDS.get(g, '')}</span></div>"))
                items += [pn.pane.HoloViews(p) for p in panels]
            last = items[-1].object
            items[-1] = pn.pane.HoloViews(last.opts(
                xlabel=f"minutes from the end of baseline ({label} starts at 0)"))
            png = save_figure(items, work, f"fig{fig:02d}_real_{label}_{stream}")
            print("  wrote", png.name)
            fig += 1


# ----------------------------------------------------------------------- page
TOKEN = re.compile(r"\{\{\s*([A-Za-z0-9_.|:,%\-{} ]+?)\s*\}\}")


def _lookup(numbers: dict, path: str):
    cur = numbers
    for part in path.split("."):
        if isinstance(cur, dict) and part in cur:
            cur = cur[part]
        elif isinstance(cur, list) and part.isdigit():
            cur = cur[int(part)]
        else:
            raise KeyError(path)
    return cur


def fill(template: str, numbers: dict) -> str:
    """``{{path}}`` or ``{{path|fmt}}`` — fmt is a Python format spec, ``pct`` for a 0–1
    value as a whole percent, or ``min`` for seconds as whole minutes. Every token must
    resolve; a hole fails the build."""
    missing = []

    def rep(m):
        path, _, fmt = m.group(1).partition("|")
        try:
            v = _lookup(numbers, path.strip())
        except KeyError:
            missing.append(path)
            return m.group(0)
        fmt = fmt.strip()
        if fmt == "pct":
            return f"{int(100 * v + 0.5)}%"   # half up: 52.5% reads 53%
        return format(v, fmt) if fmt else str(v)
    out = TOKEN.sub(rep, template)
    if missing:
        raise SystemExit("unfilled tokens: " + ", ".join(sorted(set(missing))))
    return out


def stage_page(work: Path, bakeoff, dest: Path) -> None:
    numbers = json.loads((work / "numbers.json").read_text())
    root = Path(__file__).resolve().parent.parent
    try:
        sha = subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=root,
                             capture_output=True, text=True).stdout.strip()
        dirty = bool(subprocess.run(["git", "status", "--porcelain", "--", "tools", "src"],
                                    cwd=root, capture_output=True, text=True).stdout.strip())
    except OSError:
        sha, dirty = "unknown", False
    numbers["build"] = dict(date=_dt.date.today().isoformat(),
                            commit=sha + (" plus uncommitted changes" if dirty else ""))
    html = TEMPLATE.read_text(encoding="utf-8")
    # Sentences that say what the treatment recordings show are results (FOUNDATIONS §5),
    # so they live beside the page in the darkroom, never in this public template.
    prose_file = dest / "real_prose.json"
    if not prose_file.exists():
        raise SystemExit(f"{prose_file} is missing: the real-recording prose is kept with "
                         "the output, not in the repo (FOUNDATIONS §5)")
    prose = json.loads(prose_file.read_text(encoding="utf-8"))
    holes = []

    def prose_rep(m):
        if m.group(1) not in prose:
            holes.append(m.group(1))
            return m.group(0)
        return prose[m.group(1)]
    html = re.sub(r"\{\{PROSE:([a-z0-9_]+)\}\}", prose_rep, html)
    if holes:
        raise SystemExit(f"{prose_file.name} lacks: " + ", ".join(sorted(set(holes))))
    html = html.replace("{{TABLE_PERFORMANCE}}",
                        (work / "table_performance.html").read_text(encoding="utf-8"))

    def img(m):
        name = m.group(1)
        png = work / f"{name}.png"
        if not png.exists():
            raise SystemExit(f"figure {name} has not been drawn")
        data = base64.b64encode(png.read_bytes()).decode()
        return (f'<a href="{name}.png"><img src="data:image/png;base64,{data}" '
                f'alt="{m.group(2)}"></a>')
    html = re.sub(r'<img data-fig="([^"]+)" alt="([^"]*)">', img, html)
    html = fill(html, numbers)
    out = dest / "detector_review.html"
    tmp = out.with_suffix(".tmp")
    tmp.write_text(html, encoding="utf-8")
    os.replace(tmp, out)
    for p in sorted(work.glob("fig*.png")):
        (dest / p.name).write_bytes(p.read_bytes())
    print(f"  wrote {out} ({out.stat().st_size / 1e6:.1f} MB)")


# ----------------------------------------------------------------------- main
STAGE_ORDER = ["models", "real", "problem", "surrogates", "mechanism", "learned", "generator",
               "sweeps", "shipped", "stored", "blockrecall", "sce_rescore", "optimization",
               "performance", "page"]

#: ``--carry-learned``: an earlier build's ``measurements/``, whose learned-model results are
#: merged into a rebuild that has no checkpoints. Learned results do not read the hand-written
#: detectors' settings, so a settings rebuild leaves them as they were.
CARRY: Path | None = None


def main(argv=None) -> int:
    from bugarach.paths import darkroom, unresolved_message

    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--stages", nargs="+", default=["all"])
    ap.add_argument("--bakeoff", type=Path, default=None,
                    help="directory holding baseline_quiet/ and baseline_busy/ fair_bakeoff runs")
    ap.add_argument("--out", type=Path, default=None,
                    help=f"destination (default: <darkroom>/{FOLDER_NAME})")
    ap.add_argument("--workers", type=int, default=6)
    ap.add_argument("--carry-learned", type=Path, default=None,
                    help="an earlier build's measurements/ to take learned-model results from, "
                         "when this build has no model checkpoints")
    a = ap.parse_args(argv)
    global CARRY
    CARRY = a.carry_learned

    if a.out:
        dest = a.out.expanduser()
    else:
        root = darkroom(create=True)
        if root is None:
            print(unresolved_message(), file=sys.stderr)
            return 2
        dest = root / FOLDER_NAME
    work = dest / "_work"
    work.mkdir(parents=True, exist_ok=True)

    stages = STAGE_ORDER if a.stages == ["all"] else a.stages
    for st in stages:
        t0 = time.time()
        print(f"stage {st}")
        fn = globals()[f"stage_{st}"]
        if st in ("models", "sweeps", "shipped", "stored", "blockrecall", "sce_rescore", "real"):
            fn(work, a.workers)
        elif st in ("optimization", "performance"):
            fn(work, a.bakeoff)
        elif st == "page":
            fn(work, a.bakeoff, dest)
        else:
            fn(work)
        print(f"  ({time.time() - t0:.0f} s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
