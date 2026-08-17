#!/usr/bin/env python3
"""Draw what the scoring tolerance is hiding.

    python tools/make_tolerance_figure.py --out docs/learned

The bench scores a detection as a hit when its interval comes within
``tol_sec`` of a planted event, measured edge to edge, and ``tol_sec`` is fixed
at 1.5 s everywhere. The sleep-EEG event-detection literature does not fix it:
DOSED (Chambon et al. 2019) reports F1 against an overlap criterion swept from
0.1 to 0.9 and re-tunes every competitor at each value, and SEED (Tapia-Rivas
et al. 2024) adds mean IoU as a separate localization score. This tool asks
what our own numbers do under the same treatment.

Two things a reader should take from the result, and they point opposite ways:

**The published ranking survives.** Whoever leads a regime leads it at every
tolerance, so no comparison in the report rests on the choice of 1.5 s.

**But 1.5 s is deep in the saturated part of every curve.** Each detector has
plateaued by about 0.75 s, so above that the bench cannot tell a detector that
lands on an event from one that lands a second away. Localization accuracy is
invisible to it. That is not a defect of a number, it is a missing instrument —
and the detectors it hides most are the binned ones, which is exactly where the
error lives.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from pathlib import Path

# The report's palette: hand-written detectors in blue, so a learned model
# added to this figure later is visibly not one of them.
HAND = "#4c78a8"
ACCENT = "#7a1f22"
TOLS = (0.1, 0.15, 0.25, 0.4, 0.5, 0.75, 1.0, 1.25, 1.5, 2.0, 2.5, 3.0)
REGIMES = ("baseline_quiet", "baseline_busy")
SHIPPED_TOL = 1.5

# One style per detector, fixed across panels. Colours are Bokeh's Colorblind
# palette; the dash carries the same distinction again, because six lines is
# past what colour alone separates and this figure gets printed.
STYLE = {
    "loco":   ("#0072B2", "solid"),
    "coact":  ("#E69F00", "dashed"),
    "rate":   ("#F0E442", "dotted"),
    "cicada": ("#009E73", "dotdash"),
    "sync":   ("#56B4E9", "dashdot"),
    "sce":    ("#D55E00", "solid"),
}


def measure(tols=TOLS, seeds=(1, 2, 3)) -> dict:
    """F1 for every detector at every tolerance, in both regimes."""
    from bugarach.bench import DETECTORS, evaluate

    out = {"tols": list(tols), "seeds": list(seeds), "shipped_tol": SHIPPED_TOL,
           "f1": {}}
    for regime in REGIMES:
        out["f1"][regime] = {
            det: [evaluate(det, regime, seeds=seeds, tol_sec=t).f1 for t in tols]
            for det in DETECTORS
        }
    return out


def build(d, width=920):
    import holoviews as hv

    from bugarach.ui.app import TITLES

    tols = d["tols"]
    panels = []
    for regime in REGIMES:
        rows = d["f1"][regime]
        # Rank by F1 at the shipped tolerance so the legend order matches the
        # ordering a reader has already seen in the bake-off.
        i_ship = tols.index(d["shipped_tol"])
        order = sorted(rows, key=lambda k: -rows[k][i_ship])

        curves = []
        for det in order:
            # Style is keyed to the DETECTOR, never to its rank in this panel.
            # Cycling by position made LoCo blue in one panel and yellow in the
            # other, because the leader changes between regimes — the figure
            # then reads as though a different detector had moved.
            colour, dash = STYLE[det]
            curves.append(
                hv.Curve([(t, f) for t, f in zip(tols, rows[det])],
                         kdims=["tolerance (s)"],
                         vdims=[f"F1 ({regime.split('_')[1]})"],
                         label=TITLES.get(det, det)).opts(
                    color=colour, line_dash=dash, line_width=2))

        rule = hv.VLine(d["shipped_tol"]).opts(color=ACCENT, line_width=1.5,
                                               line_dash="dashed")
        note = hv.Text(d["shipped_tol"], 0.06, " shipped: 1.5 s",
                       halign="left").opts(color=ACCENT, text_font_size="9pt")
        last = regime == REGIMES[-1]
        panels.append((hv.Overlay(curves) * rule * note).opts(
            width=width, height=330 if last else 300, ylim=(0, 1),
            show_grid=True, toolbar=None,
            legend_position="right", legend_cols=1,
            xlabel="scoring tolerance (s)" if last else "",
            xaxis="bottom" if last else None,
            fontsize={"legend": 8, "labels": 10, "ticks": 9}))

    return hv.Layout(panels).cols(1).opts(shared_axes=False, toolbar=None)


def main(argv=None) -> int:
    p = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--out", type=Path, required=True)
    p.add_argument("--width", type=int, default=920)
    p.add_argument("--json", type=Path, default=None,
                   help="reuse a previous measurement instead of re-running it")
    a = p.parse_args(argv)

    import holoviews as hv
    import panel as pn
    hv.extension("bokeh")

    d = json.loads(a.json.read_text()) if a.json else measure()

    a.out.mkdir(parents=True, exist_ok=True)
    (a.out / "tolerance_sweep.json").write_text(json.dumps(d, indent=1) + "\n")

    spec = importlib.util.spec_from_file_location(
        "_mgf", Path(__file__).parent / "make_generator_figures.py")
    mgf = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mgf)
    mgf._write(pn.Column(pn.pane.HoloViews(build(d, a.width))),
               a.out, "tolerance_sweep", png=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
