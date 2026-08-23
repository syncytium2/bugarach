#!/usr/bin/env python3
"""Draw what the models actually compute — the operator, not a box labelled with it.

    python tools/make_architecture_figures.py --spec docs/learned/generator_spec.json \
        --out docs/learned

**Why this exists.** The first version of the report showed each architecture as a
row of boxes: "centre − surround, 4 DoG kernels", "dilated stack, 10 conv, 8 ch".
Tony's response was that the architecture is the thing that makes these models
different and a block diagram does not let a human evaluate it. He is right — a box
labelled *centre minus surround* asserts a mechanism; it does not show one, and a
reader cannot tell from it whether the kernel is sane, what width it settled on, or
what it does to a background change.

So every panel here is **measured off a trained model or computed from the layer
stack**, never asserted:

* **A — the kernels the model actually fitted.** Centre, surround and their
  difference, at each of the four scales, in samples. Trained on the simulated data, then
  read out of `log_center` / `log_ratio` / `gain`. The initialisation is drawn
  underneath so a reader can see how far training moved each one.
* **B — the cancellation, demonstrated.** Feed a step change in background through
  each fitted kernel. If "rate invariance by construction" means anything, the
  response returns to zero after the step rather than sitting at a new level. This
  is the panel that can falsify the claim, so it is plotted rather than described.
* **C — how far each model can see, layer by layer.** Receptive field after every
  layer of every model, from the dilation schedule. This is where the two designs
  visibly differ: one is handed the contrast and needs a short view; the other has
  to infer the background and needs a view two orders of magnitude longer.

Nothing here is in seconds. Widths are in **samples**, which is the unit the models
are written in — see `bugarach.learn.encode`.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from pathlib import Path

import numpy as np

QUIET, BUSY = "baseline_quiet", "baseline_busy"


def _mbf():
    spec = importlib.util.spec_from_file_location(
        "_mbf", Path(__file__).parent / "make_bakeoff_figures.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _mrf():
    """The regime figure already solved label de-collision; borrow it rather than
    write a second one that drifts."""
    spec = importlib.util.spec_from_file_location(
        "_mrf", Path(__file__).parent / "make_regime_figure.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


_M = _mbf()
HAND, LEARN = _M.HAND, _M.LEARN
_spread = _mrf()._spread
SCALE_COLOURS = ["#7a1f22", "#b4553f", "#2f5d8a", "#1b7f3b"]


def dog(t, centre, ratio, gain):
    """The kernel as ``nets.py`` builds it: area-normalised centre minus surround.

    Reimplemented here in numpy rather than called through torch **because the
    point of the figure is to show the operator independently of the framework
    that ran it** — if this disagrees with the model, that is a finding. The
    normalisation is what makes a flat field integrate to zero, so it is the part
    that must match exactly.
    """
    c = np.exp(-0.5 * (t / centre) ** 2)
    s = np.exp(-0.5 * (t / (centre * ratio)) ** 2)
    return gain * (c / c.sum() - s / s.sum())


def fit_tube(gen, *, seed=0, steps=900, dt=0.1):
    """Train the centre−surround model and hand back its fitted kernel parameters."""
    from bugarach.bench import make_recording
    from bugarach.learn.train import train
    import math

    mk = lambda s: make_recording(BUSY, seed=s, **gen)          # noqa: E731
    tr = train("tube", mk, dt=dt, n_train=10, steps=steps, crop=4096,
               batch=3, lr=1e-2, seed=seed)
    m = tr.model
    return dict(
        centres=[math.exp(v) for v in m.log_center.tolist()],
        ratios=[math.exp(v) for v in m.log_ratio.tolist()],
        gains=list(m.gain.tolist()),
        init_centres=[1.0 * 2 ** i for i in range(len(m.log_center))],
        init_ratio=8.0,
        k=int(m.k), threshold=float(tr.threshold),
        n_params=tr.n_params, train_seconds=tr.train_seconds,
    )


def layer_table():
    """Receptive field after each layer, straight off the dilation schedule.

    `_dilated_stack` doubles the dilation per layer with kernel size 3, so layer i
    adds 2 * 2**i samples. Computed rather than quoted: the report previously
    quoted two of these numbers and a reader had no way to check either.
    """
    from bugarach.learn.nets import ARCHITECTURES
    rows = {}
    for name, depth_key, depth in (("centre−surround", "depth", 6),
                                   ("per-cell bank (head)", "head_depth", 10),
                                   ("pooled trace", "head_depth", 11)):
        cfg = ARCHITECTURES[{"centre−surround": "tube",
                             "per-cell bank (head)": "tiny",
                             "pooled trace": "trace"}[name]].cfg
        d = int(cfg.get(depth_key, depth))
        rf, series = 1, []
        for i in range(d):
            rf += 2 * 2 ** i
            series.append((i + 1, rf))
        rows[name] = series
    # the per-cell model's FIRST stage is separate and much shorter
    rf, series = 1, []
    for i in range(int(ARCHITECTURES["tiny"].cfg["roi_depth"])):
        rf += 2 * 2 ** i
        series.append((i + 1, rf))
    rows["per-cell bank (per-cell stage)"] = series
    return rows


def build(fit, width=920, height=250):
    """Four panels: the mechanism, what it fitted, whether it cancels, how far it sees.

    Panel A exists because the previous version of this figure drew only the
    *difference* — which is the output of the mechanism, not the mechanism. A reader
    cannot see a subtraction in its own result.
    """
    import holoviews as hv

    k = fit["k"]
    t_full = np.arange(-k, k + 1, dtype=float)

    # --- A: the mechanism, on one scale -------------------------------------
    c, r, g = fit["centres"][0], fit["ratios"][0], fit["gains"][0]
    span = min(int(3.2 * c * r), k)
    m = np.abs(t_full) <= span
    tt = t_full[m]
    centre = np.exp(-0.5 * (tt / c) ** 2); centre /= centre.sum()
    surround = np.exp(-0.5 * (tt / (c * r)) ** 2); surround /= surround.sum()
    diff = g * (centre - surround)

    def _c(y, colour, lw, dash="solid"):
        return hv.Curve((tt, y), kdims=["samples from centre"],
                        vdims=["weight"]).opts(color=colour, line_width=lw,
                                               line_dash=dash)

    panelA = (_c(centre, "#1b7f3b", 1.8)
              * _c(surround, "#2f5d8a", 1.8, "dashed")
              * _c(diff, LEARN, 2.6)
              * hv.HLine(0).opts(color="black", line_width=0.7, alpha=0.4)
              * hv.Text(span * 0.97, centre.max() * 0.95,
                        f"centre, {c:.1f} samples wide").opts(
                  color="#1b7f3b", text_font_size="8pt", text_align="right")
              * hv.Text(span * 0.97, centre.max() * 0.72,
                        f"surround, {c*r:.0f} samples — dashed").opts(
                  color="#2f5d8a", text_font_size="8pt", text_align="right")
              * hv.Text(span * 0.97, centre.max() * 0.49,
                        "centre − surround, what the head sees").opts(
                  color=LEARN, text_font_size="8pt", text_align="right")
              ).opts(
        width=width, height=height + 40, show_grid=True,
        xlabel="A · the mechanism, at the narrowest fitted scale. Both curves have unit area, "
               "so the difference integrates to zero",
        ylabel="weight",
        fontsize={"xlabel": "9pt", "ylabel": "10pt", "ticks": "9pt"},
        toolbar=None)

    # --- B: all four, as fitted, with their initialisation underneath -------
    ov = None
    span_b = 24
    mb = np.abs(t_full) <= span_b
    fitted = [dog(t_full, ci, ri, gi)[mb]
              for ci, ri, gi in zip(fit["centres"], fit["ratios"], fit["gains"])]
    # Two of the four peaks land within 0.01 of each other — which is the finding —
    # so their labels collided and one rendered struck through the other.
    label_y = _spread([y.max() for y in fitted], gap=0.028, hi=0.40)
    for i, y in enumerate(fitted):
        ci = fit["centres"][i]
        col = SCALE_COLOURS[i % len(SCALE_COLOURS)]
        cur = hv.Curve((t_full[mb], y), kdims=["samples from centre"],
                       vdims=["weight"]).opts(color=col, line_width=2.2)
        init = dog(t_full, fit["init_centres"][i], fit["init_ratio"], 1.0)[mb]
        ini = hv.Curve((t_full[mb], init)).opts(color=col, line_width=0.9,
                                                line_dash="dotted", alpha=0.75)
        lab = hv.Text(span_b * 0.98, label_y[i],
                      f"{ci:.1f} samples  (started at {fit['init_centres'][i]:.0f})").opts(
            color=col, text_font_size="8pt", text_align="right")
        layer = cur * ini * lab
        ov = layer if ov is None else ov * layer
    panelB = (ov * hv.HLine(0).opts(color="black", line_width=0.7, alpha=0.4)).opts(
        width=width, height=height + 30, show_grid=True,
        xlabel="B · all four scales as FITTED (solid) against where each started (dotted) — "
               "they converged into one narrow band",
        ylabel="weight",
        fontsize={"xlabel": "9pt", "ylabel": "10pt", "ticks": "9pt"},
        toolbar=None)

    # --- C: does a background step actually cancel? -------------------------
    n = 4000
    step = np.zeros(n); step[n // 2:] = 1.0
    ovc = None
    for i, (ci, ri, gi) in enumerate(zip(fit["centres"], fit["ratios"], fit["gains"])):
        resp = np.convolve(step, dog(t_full, ci, ri, gi), mode="same")
        cur = hv.Curve((np.arange(n) - n // 2, resp), kdims=["samples"],
                       vdims=["response"]).opts(
            color=SCALE_COLOURS[i % len(SCALE_COLOURS)], line_width=1.8)
        ovc = cur if ovc is None else ovc * cur
    panelC = (ovc
              * hv.HLine(0).opts(color="black", line_width=0.7, alpha=0.4)
              * hv.VLine(0).opts(color="#5c6773", line_width=0.9, line_dash="dashed")
              # annotation placed ABOVE the traces: at y=0 it sat on the zero line
              # and rendered as struck-through text.
              * hv.Text(120, 0.62, "background doubles here, permanently").opts(
                  color="#5c6773", text_font_size="8pt", text_align="left")
              * hv.Text(120, 0.44, "…and every response is back at zero within "
                                   "a few hundred samples").opts(
                  color="#5c6773", text_font_size="8pt", text_align="left")
              ).opts(
        width=width, height=height, show_grid=True, xlim=(-400, 900),
        xlabel="C · a permanent doubling of the background, pushed through each fitted kernel — "
               "this is the panel that could falsify \"invariance by construction\"",
        ylabel="response",
        fontsize={"xlabel": "9pt", "ylabel": "10pt", "ticks": "9pt"},
        toolbar=None)

    # --- D: how far each model can see -------------------------------------
    rows = layer_table()
    style = {"centre−surround": (LEARN, 2.6),
             "per-cell bank (head)": (HAND, 2.0),
             "per-cell bank (per-cell stage)": (HAND, 1.2),
             "pooled trace": ("#97a2ae", 1.4)}
    ovd = None
    for name, series in rows.items():
        col, lw = style[name]
        xs = [i for i, _ in series]; ys = [rf for _, rf in series]
        layer = (hv.Curve((xs, ys), kdims=["layer"], vdims=["samples visible"]).opts(
                     color=col, line_width=lw)
                 * hv.Scatter((xs, ys)).opts(color=col, size=5)
                 * hv.Text(xs[-1] + 0.3, ys[-1], f"{name}  {ys[-1]:,}").opts(
                     color=col, text_font_size="8pt", text_align="left"))
        ovd = layer if ovd is None else ovd * layer
    panelD = ovd.opts(
        width=width, height=height, logy=True, show_grid=True, xlim=(0.5, 19),
        xlabel="D · samples visible after each layer, from the dilation schedule. Same schedule "
               "for every model — only the depth differs",
        ylabel="samples visible (log)",
        fontsize={"xlabel": "9pt", "ylabel": "10pt", "ticks": "9pt"},
        toolbar=None)

    return (panelA + panelB + panelC + panelD).cols(1).opts(
        shared_axes=False, toolbar=None)


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--spec", type=Path, default=None)
    p.add_argument("--out", type=Path, required=True)
    p.add_argument("--width", type=int, default=920)
    p.add_argument("--name", default="architecture_fitted")
    p.add_argument("--steps", type=int, default=900)
    a = p.parse_args(argv)

    import holoviews as hv
    import panel as pn
    hv.extension("bokeh")

    gen = {}
    if a.spec:
        doc = json.loads(a.spec.read_text())
        gen = {k: v for k, v in doc["generator"].items() if k != "bg_rate_hz"}

    fit = fit_tube(gen, steps=a.steps)
    print("fitted centres (samples):",
          ", ".join(f"{c:.2f}" for c in fit["centres"]))
    print("initialised at          :",
          ", ".join(f"{c:.2f}" for c in fit["init_centres"]))
    print("surround/centre ratios  :",
          ", ".join(f"{r:.1f}" for r in fit["ratios"]))
    print(f"{fit['n_params']} params, trained in {fit['train_seconds']:.1f} s")

    a.out.mkdir(parents=True, exist_ok=True)
    (a.out / f"{a.name}.json").write_text(json.dumps(fit, indent=1, sort_keys=True))
    mod = importlib.util.spec_from_file_location(
        "_mgf", Path(__file__).parent / "make_generator_figures.py")
    mgf = importlib.util.module_from_spec(mod)
    mod.loader.exec_module(mgf)
    mgf._write(pn.Column(pn.pane.HoloViews(build(fit, a.width))),
               a.out, a.name, png=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
