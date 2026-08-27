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
the bottom row sharpens the difference, using one fixed-form convolution rather
than a trained rule about what an event looks like.

⚠ **This is an illustration of the operation, not a trace of the trained model.**
The model runs four difference-of-Gaussian kernels at once at its own fitted
widths and carries the untouched brightness trace alongside them; this draws one
kernel at one width. The constants are read from the trained model's cached
parameters rather than typed, so the illustration cannot drift from the
implementation, but it is still one channel of five.

Everything is measured off the generator's own planted truth, so the marks are
where events actually are rather than where a detector believes they are — and
that includes the **distractors**: correlated population bursts the generator
plants on purpose as negatives. They are the "moments that are not events" the
middle row shows, and leaving them unmarked tells the reader a deliberate
negative is ordinary background.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from pathlib import Path

import numpy as np

# A stretch holding several planted events, several planted distractors, AND the
# promiscuity probe at (1200, 1500) — the dense-but-random block put there
# specifically to fool a rate-sensitive detector. The window used to stop at
# 1150 s, fifty seconds short of it, so the figure arguing that centre-surround
# separates events from busy background excluded the one stretch built to break
# exactly that.
WINDOW = (300.0, 1560.0)
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


def _fitted(out_dir: Path):
    """The trained model's own centre width and surround ratio, from the cache.

    Hand-picked constants here previously disagreed with the model on every
    axis: a pooling half-width of 4 samples against the model's 1, one kernel
    against four, and a surround ratio of 8.0 that is the *initialisation* value
    rather than a fitted one. Reading the cache keeps the illustration tied to
    the implementation.
    """
    import json
    cache = out_dir / "learned_results.json"
    if not cache.exists():
        return None
    centres = json.loads(cache.read_text())["learned"]["tube"]["centres"]
    return centres


def build(gen=None, width=980, out_dir: Path | None = None):
    import holoviews as hv

    from bugarach.bench import make_recording
    from bugarach.learn.encode import encode
    from bugarach.ui.app import _time_axis_hook

    s, gt = make_recording(REGIME, seed=SEED, **(gen or {}))
    enc = encode(s, dt=0.1)
    dt = enc.dt
    lo, hi = int(WINDOW[0] / dt), int(WINDOW[1] / dt)
    # Compute over the WHOLE recording, then crop for display. Cropping first
    # convolved ~19 s at each end against zero padding, which the model never sees.
    full_bright_src = enc.raster
    t = np.arange(lo, hi) * dt

    centres = _fitted(out_dir) if out_dir else None
    # The model's cap window is set from its SMALLEST fitted centre, truncated to
    # an integer — with the fitted centres that is 1 sample, not 4.
    half = int(min(centres)) if centres else 1
    centre = centres[1] if centres else 4.0     # the scale the page quotes

    bright_full = _brightness(full_bright_src, half=max(half, 1))
    excess_full = _dog(bright_full, centre=centre)
    bright, excess = bright_full[lo:hi], excess_full[lo:hi]
    sub = enc.raster[:, lo:hi]

    inwin = lambda v: WINDOW[0] <= v <= WINDOW[1]                    # noqa: E731
    planted = [float(e.time) for e in gt.events if inwin(e.time)]
    distractors = [float(v) for v in getattr(gt, "distractor_times", [])
                   if inwin(v)]
    hot = gt.params.get("hot_window") if hasattr(gt, "params") else None

    def _probe(fig):
        """Shade the promiscuity probe wherever it appears."""
        if not hot:
            return fig
        return hv.VSpan(hot[0], hot[1]).opts(
            color="#c9a227", alpha=0.13, line_alpha=0) * fig

    # --- A: the specks -------------------------------------------------------
    rr, cc = np.nonzero(sub)
    raster = hv.Scatter((t[cc], rr), kdims=["t"], vdims=["cell"]).opts(
        marker="square", size=1.6, color="#3a4450", alpha=.85)
    # Two marker rows, not one. Drawn at the same height, a planted event and a
    # distractor 4 s apart overlapped into what reads as a six-pointed star — a
    # third category the caption never declares.
    ticks = hv.Scatter((planted, [sub.shape[0] + 1.6] * len(planted)),
                       kdims=["t"], vdims=["cell"]).opts(
        # Down, at the raster it is about — CLAUDE.md, plot conventions. It is a
        # solid green triangle against the distractors' open grey one below.
        marker="inverted_triangle", size=9, color="#1b7f3b")
    # Distractors carry the project's existing convention — an open inverted
    # triangle in grey (`make_generator_figures.build`).
    dmark = hv.Scatter((distractors, [sub.shape[0] - 0.6] * len(distractors)),
                       kdims=["t"], vdims=["cell"]).opts(
        marker="inverted_triangle", size=9, color="#5a5a5a", fill_alpha=0,
        line_width=1.4)
    rowA = _probe(raster * ticks * dmark).opts(
        width=width, height=210, xaxis=None,
        ylabel=f"A · cell (rank by rate) · {sub.shape[0]} ROI",
        ylim=(-1, sub.shape[0] + 2), xlim=WINDOW, show_legend=False,
        fontsize={"ylabel": "10pt", "ticks": "10pt"},
        hooks=[_time_axis_hook])

    # --- B: what the tube sees -----------------------------------------------
    rowB = _probe(hv.Curve((t, bright), kdims=["t"], vdims=["bright"]).opts(
        color="#2f5d8a", line_width=1.2)).opts(
        width=width, height=150, xaxis=None,
        ylabel="B · cells active (fraction)", xlim=WINDOW,
        fontsize={"ylabel": "10pt", "ticks": "10pt"},
        hooks=[_time_axis_hook])

    # --- C: centre minus surround --------------------------------------------
    zero = hv.HLine(0).opts(color="#9aa5b1", line_width=1)
    # Height, not wording. A y-label is laid out against the panel's own height,
    # so lengthening it to carry units clipped the last glyphs off the bottom —
    # the classic "any font or label change is a layout change" regression. The
    # extra 55 px is the axis row this panel carries and the other two do not.
    rowC = _probe(zero * hv.Curve((t, excess), kdims=["t"],
                                  vdims=["excess"]).opts(
        color="#b0413e", line_width=1.3)).opts(
        width=width, height=250,
        ylabel="C · centre − surround (fraction)", xlabel="time (min:sec)",
        xlim=WINDOW, fontsize={"ylabel": "10pt", "xlabel": "10pt", "ticks": "10pt"},
        hooks=[_time_axis_hook])

    lay = rowA + rowB + rowC
    return lay.cols(1).opts(shared_axes=False, merge_tools=True, toolbar=None)


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--out", type=Path, default=None,
                   help="destination; default $BUGARACH_DARKROOM (sapper SAP006)")
    p.add_argument("--width", type=int, default=980)
    p.add_argument("--name", default="tube_view")
    p.add_argument("--spec", type=Path, default=None,
                   help="generator_spec.json — draw the simulated data set fitted from real "
                        "recordings rather than the bench's flat background. A "
                        "figure of the problem must show the simulated data set the report "
                        "scores on, or it illustrates a different problem.")
    a = p.parse_args(argv)

    import holoviews as hv
    import panel as pn
    hv.extension("bokeh")

    spec = importlib.util.spec_from_file_location(
        "_mgf", Path(__file__).parent / "make_generator_figures.py")
    mgf = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mgf)

    from bugarach.paths import darkroom, unresolved_message
    out_dir = a.out or darkroom()
    if out_dir is None:
        print(unresolved_message(), file=sys.stderr)
        return 1
    out_dir.mkdir(parents=True, exist_ok=True)
    # No title or standfirst baked into the raster — the HTML figcaption is the
    # single caption, where it is selectable, reflows, and follows the theme.
    gen = {}
    if a.spec:
        doc = json.loads(a.spec.read_text())
        gen = {k: v for k, v in doc["generator"].items() if k != "bg_rate_hz"}
        # bg_rate_hz stays with REGIME: this figure is drawn in the busy regime
        # on purpose, and the spec's fitted median would quietly replace it.
    mgf._write(pn.Column(pn.pane.HoloViews(build(gen, a.width, out_dir=out_dir))),
               out_dir, a.name, png=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
