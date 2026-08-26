#!/usr/bin/env python3
"""Draw what the fixed guard normalization buys, which is nothing you can measure.

    python tools/make_guard_norm_bench_figure.py                     # -> the darkroom
    python tools/make_guard_norm_bench_figure.py --also docs/learned  # + the repo copy

Three rows, one per recording. F1 against the knob the operating point is actually
chosen with — alpha, swept over `bench.OPERATING_POINTS["coact"].grid`. Red is a 5 s
guard, blue a 20 s guard, dashed the shipped `compact` normalization and solid the
`exposure` one that #315 argued for. Grey is no guard at all.

**The claim the picture carries.** The shaded band is the no-guard configuration's best
F1, plus and minus the spread across the 12 seeds. Every line's best point lands inside
it. Moving alpha one decade moves F1 further than switching the normalization does, and
further than adding the guard does — so the guard is a threshold knob at the level of
outcome, whichever way its reference is normalized, which is what `forks.md` §4a said
before any of this and for a reason that turned out to be wrong.

Numbers come from ``tools/probe_guard_norm_bench.py``, imported rather than recomputed,
so this figure and ``docs/reviews/guard_prior_art_2026-08-26.md`` cannot drift apart.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from pathlib import Path

import numpy as np

# red is the 5 s guard, blue the 20 s one; dashed is the shipped normalization
STYLE = {
    "no guard":     ("#6b7784", "solid", 3.4),
    "5s compact":   ("#a03623", "dashed", 2.2),
    "5s exposure":  ("#a03623", "solid", 2.6),
    "20s compact":  ("#2f6f9f", "dashed", 2.2),
    "20s exposure": ("#2f6f9f", "solid", 2.6),
}
BAND = "#c9d2da"
RULE = "#16202b"
NICE = {"baseline_quiet": "quiet", "baseline_busy": "busy", "crowded": "crowded"}


def _probe():
    spec = importlib.util.spec_from_file_location(
        "_pgnb", Path(__file__).parent / "probe_guard_norm_bench.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def build_row(pg, rows, regime, width, last):
    """One recording. x is the alpha grid laid out evenly and labeled with its own
    values — a real log axis inverted so strict runs rightward would not range in
    bokeh, and an evenly-spaced grid is honest here because the grid IS the knob's
    domain (`OPERATING_POINTS["coact"].grid`), not a sample of a continuum."""
    import holoviews as hv

    sub = [r for r in rows if r["regime"] == regime]
    base = max((r for r in sub if r["label"] == "no guard"), key=lambda r: r["f1"])
    pos = {a: i for i, a in enumerate(pg.ALPHAS)}          # 1e-2 leftmost, 1e-7 right
    x0, x1 = -0.35, len(pg.ALPHAS) - 0.65
    ylo = min(r["f1"] for r in sub) - 0.02
    yhi = max(r["f1"] for r in sub) + 0.02

    # A UNIQUE value dimension per row, per the repo's plot conventions: holoviews
    # links axes that share a dimension name, and three panels called "f1" come out
    # sharing one y-range spanning every regime — which is how the first render of
    # this figure got a 0.3-0.9 axis on data that lives in 0.66-0.73.
    vd = f"f1_{regime}"

    # the band is the seed spread of the reference configuration, so "inside the
    # noise" is something the reader can see rather than something I assert
    els = [hv.Rectangles([(x0, base["f1"] - base["seed_sd"],
                           x1, base["f1"] + base["seed_sd"])],
                         kdims=["x", vd, "x2", f"{vd}_hi"]).opts(
        color=BAND, line_alpha=0, alpha=.6)]

    for label, (col, dash, lw) in STYLE.items():
        rs = sorted((r for r in sub if r["label"] == label), key=lambda r: -r["alpha"])
        x = [pos[r["alpha"]] for r in rs]
        y = [r["f1"] for r in rs]
        els.append(hv.Curve((x, y), "x", vd).opts(
            color=col, line_dash=dash, line_width=lw))
        i = int(np.nanargmax(y))
        els.append(hv.Scatter([(x[i], y[i])], "x", vd).opts(color=col, size=9))

    ov = els[0]
    for e in els[1:]:
        ov = ov * e

    return ov.opts(
        width=width, height=(215 if last else 180),
        xlabel=("alpha — the knob the operating point is chosen with "
                "(stricter →)" if last else ""),
        xaxis="bottom" if last else None,
        xticks=[(i, f"{a:.0e}".replace("e-0", "e-")) for a, i in pos.items()],
        xlim=(x0, x1),
        ylabel=f"F1 · {NICE[regime]} · {base['n_planted']} planted",
        ylim=(ylo, yhi),
        show_legend=False, fontsize={"xlabel": "10pt", "ylabel": "9pt", "ticks": "9pt"},
        toolbar=None)


def key(width):
    """An in-figure key, not a legend: holoviews will not render one across Curves
    with per-element styling, and a color nothing identifies is a defect."""
    import holoviews as hv
    els = []
    y = 0
    for label, (col, dash, lw) in STYLE.items():
        els.append(hv.Curve(([0.0, 0.09], [y, y])).opts(
            color=col, line_dash=dash, line_width=lw))
        els.append(hv.Text(0.12, y, label).opts(
            text_align="left", text_font_size="9pt", text_color=col,
            text_baseline="middle"))
        y -= 1
    els.append(hv.Text(0.12, y, "band = no-guard best F1 ± its spread across 12 seeds")
               .opts(text_align="left", text_font_size="9pt", text_color=RULE,
                     text_baseline="middle"))
    ov = els[0]
    for e in els[1:]:
        ov = ov * e
    return ov.opts(width=width, height=130, xaxis=None, yaxis=None,
                   xlim=(-0.02, 1.0), ylim=(y - 0.7, 0.7), show_legend=False,
                   toolbar=None)


def main(argv=None) -> int:
    p = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    # SAP006: a tool that renders something to be READ defaults to the darkroom.
    p.add_argument("--out", type=Path, default=None, help="destination (default: darkroom)")
    p.add_argument("--also", type=Path, default=None, help="extra copy, e.g. docs/learned")
    p.add_argument("--width", type=int, default=880)
    p.add_argument("--from-json", type=Path, default=None,
                   help="reuse a sweep written by probe_guard_norm_bench.py --json, "
                        "instead of running it again (the sweep is ~5 minutes)")
    a = p.parse_args(argv)

    import holoviews as hv
    import panel as pn
    hv.extension("bokeh")

    from bugarach.paths import darkroom

    pg = _probe()
    rows = json.loads(a.from_json.read_text()) if a.from_json else pg.collect()
    for regime in pg.REGIMES:
        sub = [r for r in rows if r["regime"] == regime]
        for _, _, label in pg.CONFIGS:
            rs = [r for r in sub if r["label"] == label]
            b = max(rs, key=lambda r: r["f1"])
            print(f"  {regime:15s} {label:14s} best F1 {b['f1']:.3f} at alpha "
                  f"{b['alpha']:.0e}  seed sd {b['seed_sd']:.3f}  "
                  f"P {b['precision']:.3f} R {b['recall']:.3f}")

    panels = [build_row(pg, rows, r, a.width, last=(r == pg.REGIMES[-1]))
              for r in pg.REGIMES]
    page = pn.Column(*[pn.pane.HoloViews(x) for x in panels],
                     pn.pane.HoloViews(key(a.width)))

    spec = importlib.util.spec_from_file_location(
        "_mgf", Path(__file__).parent / "make_generator_figures.py")
    mgf = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mgf)

    dests = [a.out or (darkroom() / "detector_history")]
    if a.also:
        dests.append(a.also)
    for dest in dests:
        dest.mkdir(parents=True, exist_ok=True)
        mgf._write(page, dest, "guard_norm_bench", png=True)
        print(f"  wrote {dest}/guard_norm_bench.png")
    return 0


if __name__ == "__main__":
    sys.exit(main())
