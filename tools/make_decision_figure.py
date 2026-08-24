#!/usr/bin/env python3
"""The two open decisions in the revision plan, and what each one costs.

    python tools/make_decision_figure.py --background <background.json> \
        --also docs/learned

Phase 0 of `docs/todo/2026-08-22-the-revision-plan-mechanism-before-calibration.md`
blocks on two questions. Both are easier to answer looking at them than reading
them, and the cost of each is measured rather than argued.

**A — what the background choice IS.** The bench draws every ROI at the same rate.
Real fields do not: the maximum-likelihood Gamma shape over 81 baseline windows
and 2 643 ROIs is 0.275, which leaves a third of ROIs silent and gives the busiest
a rate two orders of magnitude above the median. Panel A draws the two fields the
choice is between.

**B — what it COSTS.** Every detector at its shipped operating point, scored on
both backgrounds, same seeds. This is the answer to "is it a big change": every
score moves, they move in both directions, and the middle of the ranking reorders.

**C — the scoring tolerance, both halves at once.** F1 against the edge gap that
counts as a hit. Five of six detectors plateau by 0.75 s, so the shipped 1.5 s is
deep in flat territory and the ranking is stable across the whole sweep — the
choice is low-stakes for the comparison. It is not low-stakes for one number:
binned SCE is the only detector still climbing at 1.5 s, because its 10 s bins
make its detections coarse and only a loose tolerance credits them.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from pathlib import Path

FLAT, FITTED = "#a03623", "#2f6f9f"
INK, MUTED, RULE = "#16202b", "#5c6773", "#c8d6e4"
TITLES = {"rate": "rate+context", "sce": "binned SCE", "cicada": "locust",
          "sync": "SPIKE-synch", "coact": "CoactDetect", "loco": "LoCo"}


def panel_a(bg, width):
    """The two fields the decision is between."""
    import holoviews as hv
    import numpy as np

    edges = np.asarray(bg["rates"]["edges_mhz"], dtype=float)
    hist = np.asarray(bg["rates"]["fitted_hist"], dtype=float)
    hist = hist / hist.sum()
    ctr = (edges[:-1] + edges[1:]) / 2
    flat_mhz = bg["rates"]["flat"]["median_mhz"]

    # The flat field puts EVERY ROI at one rate, so its honest bar is 1.0 — far
    # off the top of the fitted histogram. Drawn to the ceiling and labelled as
    # such rather than scaled down, which would read as "most" instead of "all".
    top = hist.max() * 1.55
    bars = hv.Spikes((ctr, hist), kdims=["mhz"], vdims=["frac"]).opts(
        color=FITTED, line_width=6, alpha=.85)
    spike = hv.Spikes(([flat_mhz], [top]), kdims=["mhz"], vdims=["frac"]).opts(
        color=FLAT, line_width=6)
    notes = [
        hv.Text(flat_mhz + 1.2, top * .97,
                "FLAT — what the bench runs now\nevery ROI at one rate, "
                f"{flat_mhz:.1f} mHz, none silent\n(bar runs to 1.0, off the top)"
                ).opts(
            text_font_size="8pt", text_color=FLAT, text_align="left",
            text_baseline="top"),
        hv.Text(26, hist.max() * .62,
                "FITTED — measured, Gamma shape 0.275\n"
                f"{100*bg['rates']['fitted']['silent_frac']:.0f}% silent, "
                "median 1.1 mHz, long tail").opts(
            text_font_size="8pt", text_color=FITTED, text_align="left",
            text_baseline="top"),
        hv.Text(58, top * .93,
                "real: 35% silent, busiest 486 mHz\n"
                "(81 baseline windows, 2 643 ROIs)").opts(
            text_font_size="8pt", text_color=MUTED, text_align="right",
            text_baseline="top"),
    ]
    ov = bars * spike
    for n in notes:
        ov = ov * n
    return ov.opts(
        width=width, height=280, xlim=(-1, 60), ylim=(0, top),
        xlabel="A · DECISION 1, what it is — per-ROI background rate (mHz)",
        ylabel="fraction of ROIs",
        fontsize={"xlabel": "10pt", "ylabel": "10pt", "ticks": "9pt"},
        toolbar=None)


def panel_b(bg, width):
    """Every detector at its shipped point, on both backgrounds."""
    import holoviews as hv

    names = sorted(bg["flat"], key=lambda n: -bg["flat"][n]["f1"])
    ov = None
    for i, n in enumerate(names):
        a, b = bg["flat"][n]["f1"], bg["fitted"][n]["f1"]
        line = hv.Curve([(0, i), (1, i)], kdims=["x"], vdims=["row"]).opts(
            color=RULE, line_width=1.0)
        pa = hv.Scatter([(0, i)], kdims=["x"], vdims=["row"]).opts(
            color=FLAT, size=9)
        pb = hv.Scatter([(1, i)], kdims=["x"], vdims=["row"]).opts(
            color=FITTED, size=9)
        lab = hv.Text(-0.06, i, TITLES[n]).opts(
            text_font_size="9pt", text_color=INK, text_align="right",
            text_baseline="middle")
        va = hv.Text(0.04, i, f"{a:.3f}").opts(
            text_font_size="8pt", text_color=FLAT, text_align="left",
            text_baseline="middle")
        d = b - a
        vb = hv.Text(1.04, i, f"{b:.3f}   {d:+.3f}").opts(
            text_font_size="8pt", text_color=FITTED if d > 0 else FLAT,
            text_align="left", text_baseline="middle")
        block = line * pa * pb * lab * va * vb
        ov = block if ov is None else ov * block
    heads = (hv.Text(0, len(names) - 0.35, "FLAT").opts(
                 text_font_size="9pt", text_color=FLAT, text_align="center")
             * hv.Text(1, len(names) - 0.35, "FITTED").opts(
                 text_font_size="9pt", text_color=FITTED, text_align="center"))
    caption = hv.Text(
        0.5, -0.62,
        "B · DECISION 1, what it costs — every detector at its shipped operating "
        "point, 3 seeds. Every score moves, in both directions.").opts(
        text_font_size="10pt", text_color=INK, text_align="center",
        text_baseline="middle", text_font_style="italic")
    return (ov * heads * caption).opts(
        width=width, height=300, xlim=(-0.42, 1.42),
        ylim=(-0.95, len(names) - 0.05),
        yaxis=None, xaxis=None, xlabel="", ylabel="",
        toolbar=None)


def panel_c(tol, width):
    """F1 against the edge gap that counts as a hit."""
    import holoviews as hv
    import numpy as np

    tols = np.asarray(tol["tols"], dtype=float)
    f1 = tol["f1"]["baseline_quiet"]
    order = sorted(f1, key=lambda n: -f1[n][-1])
    # Curves end within 0.016 of each other in two places, so the end-labels
    # collide and each reads as belonging to the other. Nudged by hand and
    # checked against the render; six curves, no rule would do better.
    NUDGE = {"loco": +0.028, "coact": -0.022, "sce": +0.022, "sync": -0.022}
    ov = None
    for n in order:
        y = np.asarray(f1[n], dtype=float)
        is_sce = n == "sce"
        c = FLAT if is_sce else MUTED
        cur = hv.Curve((tols, y), kdims=["tol"], vdims=["f1"]).opts(
            color=c, line_width=2.4 if is_sce else 1.4,
            alpha=1.0 if is_sce else .55)
        lab = hv.Text(tols[-1] + 0.08, y[-1] + NUDGE.get(n, 0.0),
                      TITLES[n]).opts(
            text_font_size="8pt", text_color=c, text_align="left",
            text_baseline="middle", text_alpha=1.0 if is_sce else .75)
        ov = (cur * lab) if ov is None else ov * cur * lab
    marks = [
        hv.Curve([(0.75, 0), (0.75, .85)], kdims=["tol"], vdims=["f1"]).opts(
            color=INK, line_width=1.0, line_dash="dotted"),
        hv.Curve([(1.5, 0), (1.5, .85)], kdims=["tol"], vdims=["f1"]).opts(
            color=INK, line_width=1.4, line_dash="dashed"),
        hv.Text(0.72, .86, "five of six flat from here").opts(
            text_font_size="8pt", text_color=INK, text_align="right",
            text_baseline="bottom"),
        hv.Text(1.53, .86, "shipped, 1.5 s").opts(
            text_font_size="8pt", text_color=INK, text_align="left",
            text_baseline="bottom"),
        hv.Text(3.0, .09,
                "ranking unchanged from 0.4 s to 2.0 s — the choice is\n"
                "low-stakes for the comparison, and costs binned SCE 0.13").opts(
            text_font_size="8pt", text_color=MUTED, text_align="right",
            text_baseline="bottom"),
    ]
    for m in marks:
        ov = ov * m
    return ov.opts(
        width=width, height=300, xlim=(0, 3.6), ylim=(0, .95),
        xlabel="C · DECISION 2 — edge gap counted as a hit (s); "
               "median planted event is 0.80 s wide",
        ylabel="F1 (3 seeds, baseline_quiet)",
        fontsize={"xlabel": "10pt", "ylabel": "10pt", "ticks": "9pt"},
        toolbar=None)


def main(argv=None) -> int:
    p = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--background", type=Path, required=True,
                   help="JSON from the flat-vs-fitted measurement")
    p.add_argument("--tolerance", type=Path,
                   default=Path("docs/learned/tolerance_sweep.json"))
    # SAP006: a tool that renders something to be READ defaults to the darkroom.
    p.add_argument("--out", type=Path, default=None)
    p.add_argument("--also", type=Path, default=None)
    p.add_argument("--width", type=int, default=960)
    a = p.parse_args(argv)

    import holoviews as hv
    import panel as pn
    hv.extension("bokeh")

    from bugarach.paths import darkroom

    spec = importlib.util.spec_from_file_location(
        "_mgf", Path(__file__).parent / "make_generator_figures.py")
    mgf = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mgf)

    bg = json.loads(a.background.read_text())
    tol = json.loads(a.tolerance.read_text())
    page = pn.Column(
        pn.pane.HoloViews(panel_a(bg, a.width)),
        pn.pane.HoloViews(panel_b(bg, a.width)),
        pn.pane.HoloViews(panel_c(tol, a.width)))
    dests = [a.out or (darkroom() / "detector_history")]
    if a.also:
        dests.append(a.also)
    for dest in dests:
        dest.mkdir(parents=True, exist_ok=True)
        mgf._write(page, dest, "two_decisions", png=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
