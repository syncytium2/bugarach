#!/usr/bin/env python3
"""Figure 1 of the methods section: one benchmark recording, as the detectors see it.

    python tools/make_methods_bench_figure.py --also docs/methods/figures

One synthetic benchmark recording (``bench.make_recording``, quiet background, seed 1),
drawn as two x-linked rows. The **lane** on top holds what was planted: one row of
down-pointing marks per participation level, a row for the distractors, and the
elevated-rate block as a shaded span. The **raster** below is black and white, one mark
per event, nothing drawn on it (CLAUDE.md plot conventions; sapper SAP009). A reader
compares the lane with the raster to see how much of the planted structure is visible
by eye, which is the question the methods text cannot answer in words.

Destination defaults to ``<darkroom>/2026-09-22-methods/`` (``bugarach.paths``);
``--also`` writes the repo copy the manuscript build embeds.
"""

from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))

#: Participation levels, top to bottom in the lane, with their inks.
LEVELS = ((0.30, "#1b7f3b"), (0.18, "#4c78a8"), (0.10, "#b279a2"))
DISTRACTOR_INK = "#5a5a5a"


def build(seed: int, width: int):
    import holoviews as hv

    from bugarach.bench import BENCH_RECORDING, make_recording
    from bugarach.ui.app import _time_axis_hook
    from bugarach.ui.diagnostic import raster_panel

    s, gt = make_recording("baseline_quiet", seed)
    T = BENCH_RECORDING["duration_sec"]
    ext = (0.0, T)
    n_roi = s.streams["events"].n_rois

    # lane rows: 3 = 30 %, 2 = 18 %, 1 = 10 %, 0 = distractors
    lo, hi = BENCH_RECORDING["hot_window"]
    lane = hv.VSpan(lo, hi).opts(color="#d9a441", alpha=0.35)
    for row, (frac, ink) in zip((3, 2, 1), LEVELS):
        t = gt.times[np.isclose(gt.frac, frac)]
        lane = lane * hv.Scatter((t, np.full(t.size, row)), kdims=["t"],
                                 vdims=["lane"]).opts(
            marker="inverted_triangle", size=9, color=ink)
    dt = gt.distractor_times
    lane = lane * hv.Scatter((dt, np.zeros(dt.size)), kdims=["t"],
                             vdims=["lane"]).opts(
        marker="inverted_triangle", size=9, color=DISTRACTOR_INK,
        fill_alpha=0.0, line_width=1.5)
    lane = lane.opts(
        width=width, height=120, xlim=ext, ylim=(-0.7, 3.7), xaxis=None,
        yticks=[(3, "30% · 10 cells"), (2, "18% · 6 cells"), (1, "10% · 3 cells"),
                (0, "distractor · 6 cells")],
        ylabel="", title="", show_legend=False, toolbar=None,
        fontsize={"yticks": "9pt"}, hooks=[_time_axis_hook])

    raster = raster_panel(s.streams["events"], ext=ext, name="events",
                          width=width, height=300)
    raster = raster.opts(
        width=width, height=300 + 45, xlim=ext, ylim=(-1, n_roi),
        ylabel=f"cells · {n_roi}", xlabel="time", title="", toolbar=None,
        fontsize={"ylabel": "10pt"}, hooks=[_time_axis_hook])
    return (lane + raster).cols(1).opts(shared_axes=False, toolbar=None), gt


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--seed", type=int, default=1)
    p.add_argument("--width", type=int, default=1000)
    p.add_argument("--out", default=None,
                   help="destination directory; default <darkroom>/2026-09-22-methods")
    p.add_argument("--also", default=None, help="also copy the PNG here (repo copy)")
    args = p.parse_args(argv)

    from bugarach.paths import darkroom, unresolved_message

    if args.out:
        dest = Path(args.out).expanduser()
    else:
        root = darkroom()
        if root is None:
            print(unresolved_message(), file=sys.stderr)
            return 2
        dest = root / "2026-09-22-methods"
    dest.mkdir(parents=True, exist_ok=True)

    import holoviews as hv
    import panel as pn

    from make_generator_figures import _write

    hv.extension("bokeh")
    fig, gt = build(args.seed, args.width)
    key = " · ".join(f'<span style="color:{ink}">▼</span> {round(f * 100)}%'
                     for f, ink in LEVELS)
    page = pn.Column(
        pn.pane.HTML(
            '<div style="font:13px/1.5 system-ui,sans-serif;max-width:1000px;'
            'color:#444">Benchmark recording, quiet background, seed '
            f'{args.seed}: {len(gt.events)} planted events ({key}), '
            f'<span style="color:{DISTRACTOR_INK}">▽</span> '
            f'{len(gt.distractors)} distractors, '
            '<span style="background:#f1dcae">&nbsp;elevated-rate block&nbsp;</span>'
            '</div>'),
        pn.pane.HoloViews(fig))
    stem = "fig1_benchmark_recording"
    _write(page, dest, stem, True, viewport_width=args.width + 120)
    if args.also:
        also = Path(args.also)
        also.mkdir(parents=True, exist_ok=True)
        shutil.copy2(dest / f"{stem}.png", also / f"{stem}.png")
        print(f"      {also / (stem + '.png')}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
