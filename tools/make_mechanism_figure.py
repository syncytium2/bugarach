#!/usr/bin/env python3
"""How LoCo, CoactDetect and rate+context decide — two zoomed windows, drawn.

    python tools/make_mechanism_figure.py                        # -> the darkroom
    python tools/make_mechanism_figure.py --also docs/learned    # + the repo copy

The three adaptive-threshold detectors ask one question — *is there more co-firing
right now than the local background explains?* — and differ in what they count and
how they estimate that background. `make_diagnostic.py` draws all of it over 45
minutes, where a threshold is a hairline and two of the three bars cannot be seen at
all (Tony, 2026-09-14: *"need to find simple figures showing how the loco/coact rate
detect work"*; nothing in the tree did). This zooms to two 3-minute windows of the
bench recording, side by side:

* **A** — a planted coordinated event that all three detect.
* **B** — inside the promiscuity probe, where every ROI fires faster and nothing is
  planted, so any call is a false alarm by construction.

Each column is a truth-and-calls lane, the raster, then one trace per detector: what
it counts (its colour), its estimate of the local background (grey), and the bar that
estimate implies (black).

**CoactDetect's bar is reconstructed here, and says so.** The detector reports a
z-score per candidate bin, not a threshold. The count that would reach p = alpha is
null mean + z* x null sd, and the null sd is recovered as (obs - null mean) / z, so
the bar exists only at bins the detector tested (obs >= min_rois). It is the figure's
arithmetic on the detector's own numbers, not a number the detector emits.

**Calls are filtered to the window before they reach `lane_panel`.**
`ui.diagnostic._spans` clamps a span that starts past the extent into an inverted bar
across the whole lane; every other caller passes the whole recording and never meets
it. Filed: `docs/todo/2026-09-14-lane-spans-invert-outside-a-sub-extent.md`.

The defaults (seed 3, quiet background, windows 400–580 s and 1290–1470 s) pick a
planted event at 491.9 s with 18% of ROIs participating and two rate+context false
alarms inside the probe. A different seed moves the planted events, so pass
`--window-a` with it. Everything drawn is simulated, so `--also` is safe.
"""
from __future__ import annotations

import argparse
import os
import sys
import tempfile
from pathlib import Path
from statistics import NormalDist

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))

DETS = ("loco", "coact", "rate")
COLW = 520          # two columns must fit _render_png's 1180 px viewport
TRACE_H = 150
GREY = "#8c8c8c"
NAME = "figure_mechanism_loco_coact_rate"


def build(args):
    import holoviews as hv
    import panel as pn

    hv.extension("bokeh")

    from bugarach.bench import make_recording
    from bugarach.detectors.rate import recording_extent
    from bugarach.ui.app import COLORS, TITLES, _compute, _time_axis_hook
    from bugarach.ui.diagnostic import lane_panel, raster_panel
    from make_diagnostic import _detector_params, _dt_for

    s, gt = make_recording(args.regime, args.seed)
    ext = recording_extent(s)
    dt = _dt_for(s)
    params = _detector_params(("sce", "sync", "cicada"))   # keep only the three drawn
    res = {d: _compute(d, s, ext, params[d], dt=dt)["events"] for d in DETS}
    zstar = NormalDist().inv_cdf(1 - res["coact"].result.opts["alpha"])
    min_rois = res["coact"].result.opts["min_rois"]
    excess = params["rate"]["excess_threshold_hz"]

    def trace_opts(el, win, ylabel, *, last):
        # shared_axes=False: the two columns cover different windows and would
        # otherwise link through the common `t` dimension.
        return el.opts(width=COLW, height=TRACE_H + (30 if last else 0), xlim=win,
                       ylim=(0, 14), ylabel=ylabel, xlabel="", title="", toolbar=None,
                       show_legend=False, hooks=[_time_axis_hook],
                       fontsize={"ylabel": "9pt"}, shared_axes=False,
                       **({} if last else {"xaxis": None}))

    def column(key, win):
        near = lambda t: (t >= win[0] - 5) & (t <= win[1] + 5)  # noqa: E731
        lanes = {}
        for d in DETS:
            on, wd = (np.asarray(a, float) for a in res[d].events[:2])
            keep = (on >= win[0]) & (on <= win[1])
            lanes[d] = (on[keep], wd[keep])
        panels = [lane_panel(lanes, ext=win, gt=gt, width=COLW, row_px=24,
                             names=TITLES, colors=COLORS)
                  .opts(toolbar=None, xaxis=None, xlim=win, shared_axes=False)]
        raster = raster_panel(s.streams["events"], ext=win, width=COLW, height=130,
                              name="simulated", ydim=f"roi_{key}", ticks="minimal")
        panels.append(raster.opts(toolbar=None, xaxis=None, xlim=win, shared_axes=False))

        r = res["loco"]
        t, y = np.asarray(r.t), np.asarray(r.y)
        thr = np.asarray(r.extra["threshold"], float)
        k, yd = near(t), f"loco_{key}"
        el = (hv.Curve((t[k], y[k]), "t", yd).opts(interpolation="steps-mid",
                                                    color=COLORS["loco"], line_width=1.4)
              * hv.Curve((t[k], thr[k]), "t", yd).opts(color="#111", line_dash="dotted",
                                                        line_width=2))
        panels.append(trace_opts(el, win, "LoCo · ROIs / 1 s bin", last=False))

        raw = res["coact"].result
        ctr, obs = np.asarray(raw.ctr), np.asarray(raw.obs, float)
        nm, z = np.asarray(raw.nullmean_prof, float), np.asarray(raw.z_prof, float)
        ok = np.isfinite(z) & (z > 0) & np.isfinite(nm)
        sd = np.full(obs.size, np.nan)
        sd[ok] = (obs[ok] - nm[ok]) / z[ok]
        bar = nm + zstar * sd
        k, yd = near(ctr), f"coact_{key}"
        kb, kn = k & np.isfinite(bar), k & np.isfinite(nm)
        el = (hv.Curve((ctr[k], obs[k]), "t", yd).opts(interpolation="steps-mid",
                                                        color=COLORS["coact"], line_width=1.4)
              * hv.Scatter((ctr[kn], nm[kn]), "t", yd).opts(color=GREY, size=4)
              * hv.Scatter((ctr[kb], bar[kb]), "t", yd).opts(marker="dash", size=16,
                                                              color="#111", line_width=2.5))
        panels.append(trace_opts(el, win, "CoactDetect · ROIs / 2 s bin", last=False))

        r = res["rate"]
        t, y = np.asarray(r.t), np.asarray(r.y)
        ref = np.asarray(r.extra["ref"], float)
        k, yd = near(t), f"rate_{key}"
        el = (hv.Curve((t[k], y[k]), "t", yd).opts(color=COLORS["rate"], line_width=1.2)
              * hv.Curve((t[k], ref[k]), "t", yd).opts(color=GREY, line_width=2)
              * hv.Curve((t[k], ref[k] + excess), "t", yd).opts(color="#111",
                                                                 line_dash="dotted",
                                                                 line_width=2))
        panels.append(trace_opts(el, win, "rate+context · events/s", last=True))
        return panels

    n_roi = s.streams["events"].n_rois
    head = "font:13px/1.45 system-ui,sans-serif;color:#222;max-width:1220px;margin:4px 0 12px"
    caption = pn.pane.HTML(
        f"<div style='{head}'><b>Figure 2b. How the three adaptive-threshold detectors "
        "decide.</b> All three ask the same question, <i>is there more co-firing right now "
        "than the local background explains?</i>, and differ in what they count and how they "
        f"estimate the background. One simulated recording ({n_roi} ROIs, bench, "
        f"{args.regime.replace('baseline_', '')} background, seed {args.seed}), two 3-minute "
        "windows. <b>Column A</b>: a planted coordinated event. <b>Column B</b>: inside the "
        "promiscuity probe, a block where every ROI fires faster and nothing is planted, so "
        "any call is a false alarm. Top lane: ▼ planted event (green = recovered), then one "
        "row of calls per detector (✕ = false alarm). In every trace below the raster: "
        "<b>coloured line</b> = what the detector counts; <b>grey</b> = its estimate of the "
        "local background; <b>black dotted or dashes</b> = the bar it must clear."
        "<ul style='margin:6px 0 0 18px;padding:0'>"
        "<li><b>LoCo</b> counts distinct ROIs active in each 1 s bin. Its bar is the "
        f"{params['loco']['threshold_pctile']:g}th percentile of that same count after each "
        "ROI's events are circularly shifted at random (which keeps every cell's rate and "
        "destroys only cross-cell timing), taken over "
        f"{params['loco']['context_win_sec'] / 2:g} s either side and set by whichever side "
        "is higher. Where firing is dense the bar rises with it.</li>"
        "<li><b>CoactDetect</b> counts distinct ROIs in each 2 s bin. For every bin with at "
        f"least {min_rois}, it builds a surrogate null from a "
        f"{params['coact']['context_win_sec']:g} s window centred on that bin (grey dots = "
        f"null mean) and fires if the count is {zstar:.2f} null standard deviations above it "
        f"(p ≤ {params['coact']['alpha']:g}). The black dashes are that bar in ROI units, "
        "reconstructed from the detector's own z-scores and drawn only at the bins it "
        "tested.</li>"
        "<li><b>rate+context</b> counts events per second across all ROIs (a 1 s window, so "
        "one busy cell can drive it). Its background is the plain "
        f"{params['rate']['context_win']:g} s average rate (grey); it fires when the rate "
        f"exceeds that average by {excess:g} events/s. The bar moves with the mean but not "
        "with the variance, so a busy block's fluctuations can cross it.</li></ul></div>")

    windows = {"A": tuple(args.window_a), "B": tuple(args.window_b)}
    labels = {"A": "A · planted event", "B": "B · promiscuity probe, nothing planted"}
    row = pn.Row(*[
        pn.Column(pn.pane.HTML("<div style='font:600 12px system-ui;margin:0 0 2px 70px'>"
                               f"{labels[k]}</div>"),
                  *[pn.pane.HoloViews(p) for p in column(k, w)])
        for k, w in windows.items()])
    return pn.Column(caption, row)


def main(argv=None) -> int:
    from bugarach.paths import darkroom, unresolved_message
    from make_diagnostic import _render_png

    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--seed", type=int, default=3)
    ap.add_argument("--regime", default="baseline_quiet")
    ap.add_argument("--window-a", type=float, nargs=2, default=(400.0, 580.0),
                    metavar=("START_S", "END_S"), help="window around a planted event")
    ap.add_argument("--window-b", type=float, nargs=2, default=(1290.0, 1470.0),
                    metavar=("START_S", "END_S"), help="window inside the probe block")
    ap.add_argument("--out", type=Path, default=None,
                    help="destination directory (default: the darkroom)")
    ap.add_argument("--also", type=Path, default=None, help="write a second copy here")
    args = ap.parse_args(argv)

    if args.out:
        dest = args.out.expanduser()
    else:
        root = darkroom(create=True)
        if root is None:
            print(unresolved_message(), file=sys.stderr)
            return 2
        dest = root
    dest.mkdir(parents=True, exist_ok=True)

    page = build(args)
    html = dest / f"{NAME}.html"
    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td) / "p.html"
        page.save(str(tmp))               # write-then-replace: the darkroom is Dropbox
        os.replace(tmp, html)
    written = [html]
    png = html.with_suffix(".png")
    if _render_png(html, png, scale=2):
        written.append(png)
    else:
        print("(no PNG: python -m playwright install chromium)", file=sys.stderr)
    if args.also:
        args.also.mkdir(parents=True, exist_ok=True)
        for p in list(written):
            (args.also / p.name).write_bytes(p.read_bytes())
            written.append(args.also / p.name)
    for p in written:
        print("wrote", p)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
