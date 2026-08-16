#!/usr/bin/env python3
"""Draw the problem, and the view the model is given.

    python tools/make_tube_figure.py --out docs/learned

Three rows over the same stretch of one bench recording:

* **the specks** — every onset, cells ordered by how often they fire;
* **what the tube sees** — the fraction of cells active near each instant, which
  is all the model gets after the cell axis is summed away;
* **centre minus surround** — the same trace with its own local level subtracted.

The point of the figure is the comparison between the last two. A coordinated
event is a bright spot in the middle row, but so is a busy patch of background;
the bottom row is what separates them, and it is one convolution rather than a
trained opinion.

Everything is measured off the generator's own planted truth, so the marks are
where events actually are rather than where a detector believes they are.
"""

from __future__ import annotations

import argparse
import importlib.util
import sys
from pathlib import Path

import numpy as np

WINDOW = (300.0, 1150.0)      # a stretch holding several planted events
SEED = 1
REGIME = "baseline_busy"


def _brightness(raster, half):
    """Fraction of cells with any onset within +/- half samples — one vote each.

    A max over the window before summing is the distinctness rule made exact: a
    cell that fires five times in the window still contributes one.
    """
    import torch
    x = torch.from_numpy(raster).unsqueeze(0)
    pooled = torch.nn.functional.max_pool1d(
        x.reshape(-1, 1, x.shape[-1]), kernel_size=2 * half + 1, stride=1,
        padding=half).reshape(x.shape)
    return (pooled.sum(dim=1) / max(raster.shape[0], 1)).squeeze(0).numpy()


def _dog(trace, centre, ratio=8.0):
    """Centre minus surround, both area-normalised so a flat field gives zero."""
    k = int(max(8, centre * ratio * 3))
    t = np.arange(-k, k + 1, dtype=float)
    c = np.exp(-0.5 * (t / centre) ** 2)
    s = np.exp(-0.5 * (t / (centre * ratio)) ** 2)
    kern = c / c.sum() - s / s.sum()
    return np.convolve(trace, kern, mode="same")


def build(width=980):
    import holoviews as hv

    from bugarach.bench import make_recording
    from bugarach.learn.encode import encode
    from bugarach.ui.app import _time_axis_hook

    s, gt = make_recording(REGIME, seed=SEED)
    enc = encode(s, dt=0.1)
    dt = enc.dt
    lo, hi = int(WINDOW[0] / dt), int(WINDOW[1] / dt)
    sub = enc.raster[:, lo:hi]
    t = np.arange(lo, hi) * dt

    bright = _brightness(sub, half=4)         # ~0.8 s, the measured event width
    excess = _dog(bright, centre=4.0)

    planted = [float(e.time) for e in gt.events
               if WINDOW[0] <= e.time <= WINDOW[1]]

    # --- row 1: the specks ---------------------------------------------------
    rr, cc = np.nonzero(sub)
    raster = hv.Scatter((t[cc], rr), kdims=["t"], vdims=["cell"]).opts(
        marker="square", size=1.6, color="#3a4450", alpha=.85)
    ticks = hv.Scatter((planted, [sub.shape[0] + 0.5] * len(planted)),
                       kdims=["t"], vdims=["cell"]).opts(
        marker="triangle", size=9, color="#1b7f3b")
    row1 = (raster * ticks).opts(
        width=width, height=210, xaxis=None, ylabel="cells · by rate",
        ylim=(-1, sub.shape[0] + 2), xlim=WINDOW, show_legend=False,
        fontsize={"ylabel": "10pt"}, hooks=[_time_axis_hook])

    # --- row 2: what the tube sees -------------------------------------------
    row2 = hv.Curve((t, bright), kdims=["t"], vdims=["bright"]).opts(
        color="#2f5d8a", line_width=1.2, width=width, height=150, xaxis=None,
        ylabel="cells active", xlim=WINDOW, fontsize={"ylabel": "10pt"},
        hooks=[_time_axis_hook])

    # --- row 3: centre minus surround ----------------------------------------
    zero = hv.HLine(0).opts(color="#9aa5b1", line_width=1)
    row3 = (zero * hv.Curve((t, excess), kdims=["t"], vdims=["excess"]).opts(
        color="#b0413e", line_width=1.3)).opts(
        width=width, height=195, ylabel="centre − surround", xlabel="time",
        xlim=WINDOW, fontsize={"ylabel": "10pt", "xlabel": "10pt"},
        hooks=[_time_axis_hook])

    for r in (row1, row2, row3):
        pass
    lay = row1 + row2 + row3
    return lay.cols(1).opts(shared_axes=False, merge_tools=True, toolbar=None)


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--out", type=Path, required=True)
    p.add_argument("--width", type=int, default=980)
    a = p.parse_args(argv)

    import holoviews as hv
    import panel as pn
    hv.extension("bokeh")

    spec = importlib.util.spec_from_file_location(
        "_mgf", Path(__file__).parent / "make_generator_figures.py")
    mgf = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mgf)

    a.out.mkdir(parents=True, exist_ok=True)
    page = pn.Column(
        pn.pane.HTML(
            '<div style="font:13px/1.6 system-ui,sans-serif;max-width:980px">'
            '<b style="font-size:15px">What a coordinated event looks like, and '
            'why it is hard to see</b><br>'
            '<span style="color:#555">Green triangles mark events the generator '
            'actually planted. Middle: the fraction of cells active near each '
            'instant &mdash; every onset counted once per cell. Bottom: the same '
            'trace minus its own local level.</span></div>'),
        pn.pane.HoloViews(build(a.width)))
    mgf._write(page, a.out, "tube_view", png=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
