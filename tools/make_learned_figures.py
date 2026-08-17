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
LEARNED = ("trace", "tiny", "tube")   # work order — the figures follow the table
N_SURROGATES = 1000                   # assess.py's own documented reference value

# The recording the round trip measures recovery against. **Derived from
# BENCH_RECORDING, never re-typed** — `make_generator_figures` records what
# happened the last time these were literals: an earlier version hardcoded the
# four values the bench documents as measured-wrong, and the figures illustrated
# an instrument the project had already disowned. Only what the round trip
# genuinely needs is overridden: one participation level, so "what does the
# assessor recover" has a single answer rather than a mixture, and the untreated
# median background rather than either regime endpoint.
def _planted() -> dict:
    from bugarach.bench import BENCH_RECORDING
    p = {k: v for k, v in BENCH_RECORDING.items()
         if k in ("duration_sec", "n_roi", "jitter_sec", "min_sep_sec")}
    return dict(p, bg_rate_hz=0.0096, participation=(0.18,), n_per_level=(15,),
                grid_sec=0.1)


def _result_row(r) -> dict:
    """The fields every scored thing reports — one shape for the six and the
    learned models alike, so a figure cannot accidentally plot two rules."""
    return dict(f1=r.f1, recall=r.recall, precision=r.precision,
                n_detected=r.n_detected, n_scored=r.n_scored, hot_fa=r.hot_fa,
                n_planted=r.n_planted, n_hit=r.n_hit,
                by_frac={f"{f:g}": r.recall_at(f) for f in sorted(r.by_frac)})


def compute() -> dict:
    from bugarach.assess import assess_coactivity
    from bugarach.bench import (DETECTORS, OPERATING_POINTS, evaluate,
                                make_recording, pool_scores, sweep)
    from bugarach.learn.train import train
    from bugarach.score import score_stream
    from bugarach.simulate import simulate_coordination

    out: dict = {}
    PLANTED = _planted()

    # --- the six, at their declared operating points --------------------------
    six = {}
    for d in DETECTORS:
        r = evaluate(d, REGIME, seeds=BENCH_SEEDS)
        six[d] = dict(_result_row(r), params=0,
                      knob=OPERATING_POINTS[d].knob,
                      knob_value=r.knob_value,
                      source=OPERATING_POINTS[d].source)
    out["six"] = six

    # --- the six, swept along their own knobs ---------------------------------
    # Without this the report compares the six at ONE point against a learned
    # model slid along its whole threshold curve, and then reports the gap as a
    # property of the architectures. Every one of the six has a declared
    # sensitivity knob and grid for exactly this purpose.
    out["six_sweep"] = {
        d: [dict(_result_row(r), knob_value=r.knob_value)
            for r in sweep(d, REGIME, seeds=BENCH_SEEDS)]
        for d in DETECTORS}

    # --- the learned models, trained and scored through the SAME pooling ------
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
        import math

        def _at(threshold):
            """Score the model at one threshold, pooled by the bench's rule."""
            tr.threshold = threshold
            scores = []
            for s in BENCH_SEEDS:
                sl, gt = mk(s)
                d, _ = tr.predict(sl)
                scores.append(score_stream(gt, d))
            return pool_scores(scores, detector=name, regime=REGIME,
                               seeds=BENCH_SEEDS)

        row = _result_row(_at(chosen_thr))
        # A single F1 point hides a real trade. Report the model's own curve so a
        # reader can see what recall costs in precision -- recall at the
        # participant floor is the stated target, and F1 does not know that.
        # ⚠ These thresholds are scored on the bench recordings themselves; only
        # `threshold` was picked on held-out seeds. Any point read off this curve
        # is selected on the evaluation set and must be labelled as such.
        # The chosen threshold is ON the curve. Without it the plotted curve
        # skipped the model's own operating point — the figure showed a peak of
        # 0.635 for a model shipping at 0.674, because the round-number grid
        # happened to straddle it.
        grid = sorted({0.5, 0.9, 0.99, 0.997, 0.999, round(chosen_thr, 5)})
        curve = [dict(_result_row(_at(thr)), threshold=thr) for thr in grid]
        chosen_i = grid.index(round(chosen_thr, 5))
        tr.threshold = chosen_thr      # restore; the sweep left it at 0.999
        learned[name] = dict(row, params=tr.n_params, threshold=chosen_thr,
                             train_seconds=tr.train_seconds,
                             loss=[float(v) for _, v in tr.history],
                             curve=curve,
                             centres=[math.exp(v) for v in
                                      tr.model.log_center.tolist()]
                             if hasattr(tr.model, "log_center") else None)
    out["learned"] = learned

    # --- assessment round trip: what the measurement recovers ------------------
    # `jit_defined` is read, not ignored: assess.py says in terms that a caller
    # ignoring it will silently quote a meaningless number, and `adapt.py`
    # already gates on it. The null is carried alongside the observation for the
    # same reason — an onset spread that matches its own surrogate is measuring
    # the gather window, not the event.
    rt: dict = {}
    for seed in ROUND_TRIP_SEEDS:
        s, gt = simulate_coordination(seed=seed, **PLANTED)
        for r in assess_coactivity(s, window=(0.0, PLANTED["duration_sec"]),
                                   min_rois=(3, 4, 6, 8),
                                   n_surrogates=N_SURROGATES):
            rt.setdefault(str(r.min_rois), []).append(
                [r.part_n_obs, r.jit_obs, r.clusters_permin, r.span_med,
                 r.jit_null, r.jit_excess, float(r.jit_defined)])
    planted_part = PLANTED["participation"][0] * PLANTED["n_roi"]
    planted_freq = PLANTED["n_per_level"][0] / (PLANTED["duration_sec"] / 60.0)

    def _col(vs, i):
        return float(np.nanmedian([v[i] for v in vs]))

    out["round_trip"] = {
        "n_seeds": len(ROUND_TRIP_SEEDS),
        "n_surrogates": N_SURROGATES,
        "planted": dict(participants=planted_part,
                        jitter=PLANTED["jitter_sec"], frequency=planted_freq),
        "by_k": {k: dict(
            participants=_col(vs, 0), jitter=_col(vs, 1),
            frequency=_col(vs, 2), span=_col(vs, 3),
            jitter_null=_col(vs, 4), jitter_excess=_col(vs, 5),
            defined_frac=float(np.mean([v[6] for v in vs])),
            participants_iqr=[float(np.nanpercentile([v[0] for v in vs], q))
                              for q in (25, 75)],
            frequency_iqr=[float(np.nanpercentile([v[2] for v in vs], q))
                           for q in (25, 75)])
            for k, vs in rt.items()},
    }

    # The realized footprint of a planted event, from the generator's own record
    # of what it planted. Quoted on the page beside the fitted widths, so it must
    # come from the recordings the widths were fitted on, and must never again be
    # attributed to the assessor.
    spans = {}
    for regime in ("baseline_quiet", "baseline_busy"):
        v = [e.observed_span[1] - e.observed_span[0]
             for s in BENCH_SEEDS
             for e in make_recording(regime, seed=s)[1].events]
        spans[regime] = dict(median=float(np.median(v)), n=len(v),
                             iqr=[float(np.percentile(v, q)) for q in (25, 75)])
    out["planted_span_sec"] = spans
    return out


# Hand-written vs learned, encoded so it survives greyscale and colour-blindness.
# The previous pair (#4c78a8 / #c44e52) had a contrast ratio of 1.00 — identical
# relative luminance — so desaturating the figure rendered all nine bars one flat
# grey and the entire coding vanished. Luminance now differs ~4x.
HAND, LEARN, TRUTH = "#4c78a8", "#7a1f22", "#1b7f3b"

# Canonical detector names. `bugarach.ui.app.TITLES` is the project's single
# source for these; a private copy here previously disagreed with the viewer on
# four of six, so a reader moving between the report and the app could not line
# them up.
def _titles():
    from bugarach.ui.app import TITLES
    return TITLES


# Plain-language names for the architectures. The source-tree keys (`tube`,
# `tiny`, `trace`) are internal identifiers a reader cannot look up.
ARCH_NAMES = {"tube": "centre−surround", "tiny": "per-cell filter bank",
              "trace": "pooled trace"}


def _bar(hv, rows, value, ylabel, colour_key, width, height=300, xaxis="bottom"):
    """One grouped bar chart. Categories keep one order across every figure so a
    reader can line them up (the project's own consistency rule)."""
    import holoviews as hv_
    bars = hv_.Bars([(name, val) for name, val in rows], kdims=["detector"],
                    vdims=[value])
    return bars.opts(width=width, height=height, ylabel=ylabel, xlabel="",
                     color=hv_.dim("detector").categorize(colour_key,
                                                          default="#8c8c8c"),
                     xrotation=45, ylim=(0, 1.05), show_legend=False,
                     xaxis=xaxis,
                     fontsize={"ylabel": "10pt", "ticks": "9pt"})


def build_floor(res, width=920):
    """Recall against how many cells took part — the axis the six fall over on.

    This is the report's result. Every other comparison here pools the three
    planted recruitment levels into one number, which is exactly where the
    interesting behaviour hides: at the top level every detector is perfect, and
    at the bottom one almost none of them fire at all.
    """
    import holoviews as hv

    TITLES = _titles()
    six, learned = res["six"], res["learned"]
    fracs = sorted((float(f) for f in six["rate"]["by_frac"]), reverse=False)

    def _line(row, label, colour, width_px, dash="solid"):  # noqa: D401
        pts = [(f, row["by_frac"][f"{f:g}"]) for f in fracs]
        return hv.Curve(pts, kdims=["participation"], vdims=["recall"],
                        label=label).opts(color=colour, line_width=width_px,
                                          line_dash=dash) * \
            hv.Scatter(pts).opts(color=colour, size=7)

    # Dash carries identity; colour carries class. Six legend rows with the same
    # blue swatch name six things the panel cannot tell apart, while the caption
    # makes per-detector claims about them.
    DASH = {"rate": "solid", "coact": "dashed", "loco": "dotted",
            "cicada": "dashdot", "sce": (8, 3, 2, 3), "sync": (2, 4)}
    ov = None
    for d in sorted(six, key=lambda d: -six[d]["by_frac"][f"{fracs[0]:g}"]):
        c = _line(six[d], TITLES[d], HAND, 1.6, DASH.get(d, "solid"))
        ov = c if ov is None else ov * c
    ov = ov * _line(learned["tube"], "centre−surround (learned)", LEARN, 3.4)

    # Ticks at the three planted levels and nowhere else. A linear axis invents
    # 0.15 and 0.25, which are not levels the generator plants and not points any
    # line was measured at — the segments between the three are interpolation.
    n_roi = 33
    ticks = [(f, f"{f:g}  ({round(f * n_roi)} cells)") for f in fracs]
    # Legend outside the axes. Seven series cross most of the plot area, so any
    # in-axes corner puts the key on top of the data it explains.
    return ov.opts(width=width, height=390,
                   xlabel="cells taking part (fraction of the 33 in the recording)",
                   ylabel="recall (fraction of planted events)", ylim=(-0.04, 1.06), xticks=ticks,
                   legend_position="right", legend_cols=1,
                   fontsize={"ylabel": "10pt", "xlabel": "10pt",
                             "ticks": "9pt", "legend": "8pt"},
                   toolbar=None)


def build_curve(res, width=920):
    """Precision against recall, with the six swept along their own knobs.

    The six each carry a declared sensitivity knob and grid. Comparing them at
    one point against a learned model slid along its whole curve is not a
    comparison of architectures, and the correction is one call to `bench.sweep`.
    """
    import holoviews as hv

    TITLES = _titles()
    # Hand-placed label offsets. `rate+context` and `CoactDetect` land within
    # 0.03 of each other in both axes, so a single centred offset writes one on
    # top of the other.
    NUDGE = {"rate": (0.055, 0.052, "left"), "coact": (-0.02, -0.075, "right"),
             "loco": (-0.01, 0.05, "center"), "cicada": (0.0, -0.075, "center"),
             "sce": (0.02, 0.05, "left"), "sync": (-0.015, 0.05, "right")}
    # The six share one hue because they are the comparison class — but six
    # identical pale-blue curves cannot be bound to the six names floating beside
    # them, and the captions make per-detector claims. Dash pattern carries the
    # identity that colour deliberately does not.
    DASH = {"rate": "solid", "coact": "dashed", "loco": "dotted",
            "cicada": "dashdot", "sce": (8, 3, 2, 3), "sync": (2, 4)}
    ov = None
    for d, pts in res["six_sweep"].items():
        xy = sorted((p["recall"], p["precision"]) for p in pts
                    if np.isfinite(p["recall"]) and np.isfinite(p["precision"]))
        c = hv.Curve(xy, kdims=["recall"], vdims=["precision"]).opts(
            color=HAND, line_width=1.4, alpha=0.75,
            line_dash=DASH.get(d, "solid"))
        here = res["six"][d]
        m = hv.Scatter([(here["recall"], here["precision"])]).opts(
            color=HAND, size=9, marker="circle")
        dx, dy, align = NUDGE.get(d, (0.0, 0.05, "center"))
        lab = hv.Text(here["recall"] + dx, here["precision"] + dy,
                      TITLES[d]).opts(color=HAND, text_font_size="8pt",
                                      text_align=align)
        ov = (c * m * lab) if ov is None else ov * c * m * lab

    tube = res["learned"]["tube"]
    xy = sorted((p["recall"], p["precision"]) for p in tube["curve"])
    ov = ov * hv.Curve(xy, kdims=["recall"], vdims=["precision"]).opts(
        color=LEARN, line_width=3.2)
    ov = ov * hv.Scatter(xy).opts(color=LEARN, size=8)
    ov = ov * hv.Scatter([(tube["recall"], tube["precision"])]).opts(
        color=LEARN, size=15, marker="diamond")
    # Placed in the clear space above the curve's high-precision end. Centred on
    # its own marker, the thick red line ran straight through the word
    # "surround" — the one curve the page is about carrying the one struck-out
    # label.
    ov = ov * hv.Text(0.30, 1.05, "centre−surround (learned)").opts(
        color=LEARN, text_font_size="8.5pt", text_align="left")

    return ov.opts(width=width, height=430, xlabel="recall (fraction of planted events)",
                   ylabel="precision (fraction of scored detections)",
                   xlim=(-0.02, 1.02), ylim=(-0.02, 1.12),
                   fontsize={"ylabel": "10pt", "xlabel": "10pt", "ticks": "9pt"},
                   toolbar=None)


def build_scoreboard(res, width=920):
    import holoviews as hv

    TITLES = _titles()
    six, learned = res["six"], res["learned"]
    order = sorted(six, key=lambda d: -six[d]["f1"])
    rows = [(TITLES[d], six[d]) for d in order] + \
           [(f"{ARCH_NAMES[n]} (learned)", learned[n]) for n in LEARNED]

    colour = {**{TITLES[d]: HAND for d in six},
              **{f"{ARCH_NAMES[n]} (learned)": LEARN for n in LEARNED}}

    panels = []
    specs = (("f1", "A · F1 (0–1)"), ("recall", "B · recall (fraction)"),
             ("precision", "C · precision (fraction)"))
    for i, (value, label) in enumerate(specs):
        last = i == len(specs) - 1
        # One x-axis per linked group, bottom row only, with extra height so the
        # plot areas match (CLAUDE.md). The nine rotated labels were previously
        # drawn three times, costing a third of the figure to redundant ink.
        panels.append(_bar(hv, [(n, v[value]) for n, v in rows], value, label,
                           colour, width, height=300 + (95 if last else 0),
                           xaxis="bottom" if last else None))
    lay = panels[0]
    for p in panels[1:]:
        lay = lay + p
    return lay.cols(1).opts(shared_axes=False, toolbar=None)


def build_round_trip(res, width=920):
    import holoviews as hv

    rt = res["round_trip"]
    planted = rt["planted"]
    keys = [("participants", "A · participants (#ROI)", None),
            ("jitter", "B · onset SD (s)", "jitter_null"),
            ("frequency", "C · events / min", None)]
    panels = []
    for key, label, null_key in keys:
        vals = [rt["by_k"][k][key] for k in sorted(rt["by_k"], key=int)]
        pts = [(f"K={k}", rt["by_k"][k][key])
               for k in sorted(rt["by_k"], key=int)]
        # Headroom. Bokeh ranged these to the data maximum, so bar tops WERE the
        # frame line and panel B's three values sat above its highest tick —
        # unreadable, and indistinguishable from clipping.
        top = 1.18 * max(vals + [planted[key]])
        bars = hv.Bars(pts, kdims=["K"], vdims=[key]).opts(
            width=width // 3, height=280, ylabel=label, xlabel="",
            color=HAND, show_legend=False, ylim=(0, top),
            fontsize={"ylabel": "10pt", "ticks": "9pt"})
        layer = bars * hv.HLine(planted[key]).opts(
            color=TRUTH, line_dash="dashed", line_width=2)
        if null_key:
            # The surrogate null, drawn because the observation sitting on it is
            # the finding: an onset spread that matches its own circular-shift
            # null is measuring the gather window, not the event.
            #
            # Solid, dark, and heavy, over a white halo. Drawn as pale grey
            # dotted over dark blue bar fill it was unfindable below 4x zoom and
            # vanished entirely where it crossed the planted-value line — an
            # invisible line carrying the panel's whole argument.
            nulls = [rt["by_k"][k][null_key] for k in sorted(rt["by_k"], key=int)]
            pts_n = [(f"K={k}", n) for k, n in
                     zip(sorted(rt["by_k"], key=int), nulls)]
            layer = layer * hv.Curve(pts_n).opts(
                color="#ffffff", line_width=6, alpha=0.85)
            layer = layer * hv.Curve(pts_n).opts(
                color="#16202b", line_width=2.6)
            layer = layer * hv.Scatter(pts_n).opts(
                color="#16202b", size=8, marker="square")
        panels.append(layer.opts(width=width // 3, height=280))
    lay = panels[0]
    for p in panels[1:]:
        lay = lay + p
    return lay.cols(3).opts(shared_axes=False, toolbar=None)


def build_loss(res, width=920):
    import holoviews as hv

    # One colour per model. This previously zipped three names against two
    # colours, so `trace` was silently dropped and the accompanying note said
    # "neither model" of three.
    colours = {"tube": LEARN, "tiny": "#dd8452", "trace": "#8c8c8c"}
    curves = []
    for name in LEARNED:
        loss = res["learned"][name]["loss"]
        step = np.arange(len(loss)) * 50
        curves.append(hv.Curve((step, loss), kdims=["step"], vdims=["loss"],
                               label=f"{ARCH_NAMES[name]} "
                                     f"({res['learned'][name]['params']:,} params)")
                      .opts(color=colours[name],
                            line_width=3.0 if name == "tube" else 1.8))
    ov = curves[0]
    for c in curves[1:]:
        ov = ov * c
    # Legend outside the axes. In the top-right corner its opaque box sat over
    # the tail of both non-descending curves — including where they end, which
    # is the claim the figure is captioned with.
    return ov.opts(width=width, height=320, ylabel="training loss (0–2)",
                   xlabel="step", legend_position="right",
                   fontsize={"ylabel": "10pt", "xlabel": "10pt",
                             "ticks": "10pt", "legend": "9pt"}, toolbar=None)


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

    # No title or standfirst above the plot. Each figure previously carried a
    # baked-in sentence restating the HTML figcaption below it — unselectable
    # raster text that does not reflow, does not scale, stays dark-on-white in
    # dark mode, and spends ~10% of the figure's height saying what the caption
    # already says. `CLAUDE.md`: no titles above plots.
    for stem, fig in (
            ("learned_floor", build_floor(res, a.width)),
            ("learned_curve", build_curve(res, a.width)),
            ("learned_scoreboard", build_scoreboard(res, a.width)),
            ("learned_round_trip", build_round_trip(res, a.width)),
            ("learned_loss", build_loss(res, a.width))):
        mgf._write(pn.Column(pn.pane.HoloViews(fig)), a.out, stem, png=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
