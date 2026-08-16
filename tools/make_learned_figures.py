#!/usr/bin/env python3
"""Compute and render the figures for the learned-detector write-up.

    python tools/make_learned_figures.py --out docs/learned          # compute + render
    python tools/make_learned_figures.py --out docs/learned --cached # render only

Everything the write-up quotes is produced here, so a reader can re-derive it
rather than take it on trust — the arrangement `fit_background_shape.py` and
`probe_vs_heterogeneity.py` already use.

Results are cached to ``<out>/learned_results.json`` because the training runs
take minutes; ``--cached`` renders from that file and refuses to invent it.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from pathlib import Path

import numpy as np

REGIME = "baseline_busy"
BENCH_SEEDS = (1, 2, 3)
ROUND_TRIP_SEEDS = tuple(range(1, 9))
LEARNED = ("tube", "tiny", "trace")

# The planted recording the round trip measures recovery against.
PLANTED = dict(duration_sec=2700.0, n_roi=33, bg_rate_hz=0.0096,
               participation=(0.18,), n_per_level=(15,), jitter_sec=0.36,
               min_sep_sec=120.0, grid_sec=0.1)


def compute() -> dict:
    from bugarach.assess import assess_coactivity
    from bugarach.bench import DETECTORS, evaluate, make_recording
    from bugarach.learn.train import train
    from bugarach.score import score_stream
    from bugarach.simulate import simulate_coordination

    out: dict = {}

    # --- the six, at their declared operating points --------------------------
    six = {}
    for d in DETECTORS:
        r = evaluate(d, REGIME, seeds=BENCH_SEEDS)
        six[d] = dict(f1=r.f1, recall=r.recall, precision=r.precision,
                      n_detected=r.n_detected, params=0)
    out["six"] = six

    # --- the learned models, trained and scored the same way ------------------
    mk = lambda seed: make_recording(REGIME, seed=seed)          # noqa: E731
    # Per-architecture learning rate. `tube` has ~1k parameters and a structured
    # front end, so it takes a much larger step than the free-form stacks; using
    # one rate for all three would report a tuning artifact as an architecture
    # difference.
    LR = {"tube": 1e-2, "tiny": 1e-3, "trace": 1e-3}
    learned = {}
    for name in LEARNED:
        tr = train(name, mk, n_train=10, steps=900, crop=4096, batch=3,
                   lr=LR[name])
        chosen_thr = float(tr.threshold)
        hit = det = pl = 0
        for s in BENCH_SEEDS:
            sl, gt = mk(s)
            d, _ = tr.predict(sl)
            sc = score_stream(gt, d)
            hit += sc.n_hit
            det += sc.n_detected
            pl += sc.n_planted
        rec = hit / pl if pl else float("nan")
        pre = hit / det if det else 0.0
        f1 = 0.0 if (rec + pre) == 0 else 2 * rec * pre / (rec + pre)
        import math
        # A single F1 point hides a real trade. Report the model's own curve at a
        # few thresholds so a reader can see what recall costs in precision --
        # recall at the participant floor is the stated target, and F1 does not
        # know that.
        curve = []
        for thr in (0.5, 0.9, 0.99, 0.997, 0.999):
            h = d_ = 0
            for s in BENCH_SEEDS:
                sl, gt = mk(s)
                tr.threshold = thr
                dd, _ = tr.predict(sl)
                sc2 = score_stream(gt, dd)
                h += sc2.n_hit; d_ += sc2.n_detected
            curve.append(dict(threshold=thr, recall=h / pl if pl else 0.0,
                              precision=h / d_ if d_ else 0.0, n_detected=d_))
        tr.threshold = chosen_thr      # restore; the sweep left it at 0.999
        learned[name] = dict(f1=f1, recall=rec, precision=pre, n_detected=det,
                             params=tr.n_params, threshold=chosen_thr,
                             train_seconds=tr.train_seconds,
                             loss=[float(v) for _, v in tr.history],
                             curve=curve,
                             centres=[math.exp(v) for v in
                                      tr.model.log_center.tolist()]
                             if hasattr(tr.model, "log_center") else None)
    out["learned"] = learned

    # --- assessment round trip: what the measurement recovers ------------------
    rt: dict = {}
    for seed in ROUND_TRIP_SEEDS:
        s, gt = simulate_coordination(seed=seed, **PLANTED)
        for r in assess_coactivity(s, window=(0.0, PLANTED["duration_sec"]),
                                   min_rois=(3, 4, 6), n_surrogates=120):
            rt.setdefault(str(r.min_rois), []).append(
                [r.part_n_obs, r.jit_obs, r.clusters_permin])
    planted_part = PLANTED["participation"][0] * PLANTED["n_roi"]
    planted_freq = PLANTED["n_per_level"][0] / (PLANTED["duration_sec"] / 60.0)
    out["round_trip"] = {
        "planted": dict(participants=planted_part,
                        jitter=PLANTED["jitter_sec"], frequency=planted_freq),
        "by_k": {k: dict(
            participants=float(np.nanmedian([v[0] for v in vs])),
            jitter=float(np.nanmedian([v[1] for v in vs])),
            frequency=float(np.nanmedian([v[2] for v in vs])))
            for k, vs in rt.items()},
    }
    return out


def _bar(hv, rows, value, ylabel, colour_key, width, height=300):
    """One grouped bar chart. Categories keep one order across every figure so a
    reader can line them up (the project's own consistency rule)."""
    import holoviews as hv_
    bars = hv_.Bars([(name, val) for name, val in rows], kdims=["detector"],
                    vdims=[value])
    return bars.opts(width=width, height=height, ylabel=ylabel, xlabel="",
                     color=hv_.dim("detector").categorize(colour_key,
                                                          default="#8c8c8c"),
                     xrotation=45, ylim=(0, 1.05), show_legend=False,
                     fontsize={"ylabel": "10pt", "ticks": "9pt"})


def build_scoreboard(res, width=920):
    import holoviews as hv

    six, learned = res["six"], res["learned"]
    NAMES = {"coact": "CoactDetect", "loco": "LoCo", "rate": "RateDetect",
             "cicada": "CICADA", "sync": "spike-sync", "sce": "SCE"}
    order = sorted(six, key=lambda d: -six[d]["f1"])
    rows = [(NAMES[d], six[d]) for d in order] + \
           [(f"{n} (learned)", learned[n]) for n in LEARNED]

    colour = {**{NAMES[d]: "#4c78a8" for d in six},
              **{f"{n} (learned)": "#c44e52" for n in LEARNED}}

    panels = []
    for value, label in (("f1", "F1"), ("recall", "recall"),
                         ("precision", "precision")):
        panels.append(_bar(hv, [(n, v[value]) for n, v in rows], value, label,
                           colour, width))
    lay = panels[0]
    for p in panels[1:]:
        lay = lay + p
    return lay.cols(1).opts(shared_axes=False, toolbar=None)


def build_round_trip(res, width=920):
    import holoviews as hv

    rt = res["round_trip"]
    planted = rt["planted"]
    keys = [("participants", "participants (#ROI)"),
            ("jitter", "onset SD (s)"),
            ("frequency", "events / min")]
    panels = []
    for key, label in keys:
        pts = [(f"K={k}", rt["by_k"][k][key]) for k in sorted(rt["by_k"])]
        bars = hv.Bars(pts, kdims=["K"], vdims=[key]).opts(
            width=width // 3, height=260, ylabel=label, xlabel="",
            color="#4c78a8", show_legend=False,
            fontsize={"ylabel": "10pt", "ticks": "9pt"})
        truth = hv.HLine(planted[key]).opts(color="#1b7f3b", line_dash="dashed",
                                            line_width=2)
        panels.append((bars * truth).opts(width=width // 3, height=260))
    lay = panels[0]
    for p in panels[1:]:
        lay = lay + p
    return lay.cols(3).opts(shared_axes=False, toolbar=None)


def build_loss(res, width=920):
    import holoviews as hv

    curves = []
    for name, colour in zip(LEARNED, ("#c44e52", "#dd8452")):
        loss = res["learned"][name]["loss"]
        step = np.arange(len(loss)) * 50
        curves.append(hv.Curve((step, loss), kdims=["step"], vdims=["loss"],
                               label=name).opts(color=colour, line_width=2))
    ov = curves[0]
    for c in curves[1:]:
        ov = ov * c
    return ov.opts(width=width, height=300, ylabel="training loss",
                   xlabel="step", legend_position="top_right",
                   fontsize={"ylabel": "10pt", "xlabel": "10pt"}, toolbar=None)


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--out", type=Path, required=True)
    p.add_argument("--cached", action="store_true",
                   help="render from the cached results instead of recomputing")
    p.add_argument("--width", type=int, default=920)
    a = p.parse_args(argv)
    a.out.mkdir(parents=True, exist_ok=True)
    cache = a.out / "learned_results.json"

    if a.cached:
        if not cache.exists():
            print(f"no cache at {cache} — run without --cached first",
                  file=sys.stderr)
            return 1
        res = json.loads(cache.read_text())
    else:
        res = compute()
        cache.write_text(json.dumps(res, indent=1, sort_keys=True))
        print(f"wrote {cache}")

    import holoviews as hv
    import panel as pn
    hv.extension("bokeh")

    spec = importlib.util.spec_from_file_location(
        "_mgf", Path(__file__).parent / "make_generator_figures.py")
    mgf = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mgf)

    for stem, fig, note in (
            ("learned_scoreboard", build_scoreboard(res, a.width),
             "Every detector and both learned models on the same three bench "
             "recordings, scored against planted truth by the same rule. "
             "Red = learned."),
            ("learned_round_trip", build_round_trip(res, a.width),
             "What the assessment recovers from a recording with known planted "
             "coordination. Dashed green = the planted value."),
            ("learned_loss", build_loss(res, a.width),
             "Training loss. Neither model descends; the oscillation is "
             "batch-to-batch variance, not slow convergence.")):
        page = pn.Column(
            pn.pane.HTML(f'<div style="font:13px/1.6 system-ui,sans-serif;'
                         f'max-width:{a.width}px">{note}</div>'),
            pn.pane.HoloViews(fig))
        mgf._write(page, a.out, stem, png=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
