#!/usr/bin/env python3
"""Draw what the promiscuity gate refuses, and what that costs the loser.

    python tools/make_three_rules_figure.py                       # -> the darkroom
    python tools/make_three_rules_figure.py --also docs/learned   # + the repo copy

One row per background rate. Each row shows every candidate on the two mechanisms'
knob sweeps, placed by how often it fires inside a block where nothing was planted.
The dashed rule is ``MAX_PROBE_PER_MIN["rate"]`` — everything to its right is
**refused** by ``bench.pick_operating_point``, which already gates by default.

**The claim the picture carries, corrected 2026-09-02.** Half the additive sweep
sits to the right of the rule at every background, so the gate bites hard. What
this file said next was that it *"does not move the mechanism winner: additive's
best eligible F1 still beats multiplicative's at all seven points"*. That was an
artifact of two defects underneath it, both surfaced by making rule 3 **call**
``bench.pick_operating_point`` instead of reimplementing it:

* The gate **refuses**; it does not hand the sweep to the runner-up. On the two
  quietest backgrounds additive has no eligible operating point at all, so there is
  no "best eligible additive F1" there to beat multiplicative with.
* ``MULTIPLICATIVE_GRID`` stepped 5 -> 10 and stepped over multiplicative's own
  peak at the busy end — alpha 6, F1 0.667, read as 0.520.

Corrected, the gate picks multiplicative at **four of seven** backgrounds against
the probe-blind rule's two. It sits between the two scoring rules rather than on
top of either, which is the opposite of what the sentence above claimed.
Multiplicative still never trips the rule at any alpha it would plausibly be run
at; what is no longer true is that it *cannot* — at alpha 2 it fires 4.87/min, and
the old grid's lower bound was hiding the range where the mechanism can fail.

Numbers come from ``tools/probe_three_scoring_rules.py``, imported rather than
recomputed, so this figure and the todo it reports to cannot drift apart.
"""

from __future__ import annotations

import argparse
import importlib.util
import sys
from pathlib import Path

# additive/multiplicative keep the colours forks §3's figures gave them; the
# refusal rule is drawn in the same ink as every other threshold in this repo
ADDITIVE, MULTIPLICATIVE = "#a03623", "#2f6f9f"
RULE, DIM = "#16202b", "#6b7784"


def _probe():
    spec = importlib.util.spec_from_file_location(
        "_ptsr", Path(__file__).parent / "probe_three_scoring_rules.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def collect(pt):
    """Every candidate on every sweep, with its probe rate and its F1."""
    rows = []
    for bg in pt.BACKGROUND_GRID:
        for mode, grid in (("additive", pt.ADDITIVE_GRID),
                           ("multiplicative", pt.MULTIPLICATIVE_GRID)):
            for v in grid:
                r = pt._pooled(mode, v, bg)
                rows.append(dict(bg=bg, mode=mode, knob=v, f1=r.f1,
                                 probe=r.hot_fa_per_min))
    return rows


def build(rows, ceiling, width):
    import holoviews as hv

    bgs = sorted({r["bg"] for r in rows})
    marks, ticks = [], []
    for y, bg in enumerate(bgs[::-1]):
        ticks.append((y, f"{bg:.4f}"))
        for mode, col, dy in (("additive", ADDITIVE, +0.17),
                              ("multiplicative", MULTIPLICATIVE, -0.17)):
            here = [r for r in rows if r["bg"] == bg and r["mode"] == mode]
            keep = [(r["probe"], y + dy) for r in here if r["probe"] <= ceiling]
            drop = [(r["probe"], y + dy) for r in here if r["probe"] > ceiling]
            if keep:
                marks.append(hv.Scatter(keep).opts(
                    color=col, marker="circle", size=8, alpha=.9))
            if drop:
                # hollow = refused. Shape is spoken for by eligibility, so the
                # mechanism stays in the colour.
                marks.append(hv.Scatter(drop).opts(
                    color=col, marker="circle", size=9, fill_alpha=0.0,
                    line_width=1.6, alpha=.9))

    ov = marks[0]
    for m in marks[1:]:
        ov = ov * m
    ov = ov * hv.VLine(ceiling).opts(color=RULE, line_width=1.4, line_dash="dashed")

    hi = max(r["probe"] for r in rows)
    for dy, col, txt in ((0.62, ADDITIVE, "additive"),
                         (0.30, MULTIPLICATIVE, "multiplicative"),
                         (-0.02, DIM, "hollow = refused by the gate")):
        ov = ov * hv.Text(hi, len(bgs) - 1 + dy, txt).opts(
            text_align="right", text_font_size="9pt", text_color=col,
            text_baseline="middle")
    ov = ov * hv.Text(ceiling, -0.52, f"  ceiling {ceiling:g}/min").opts(
        text_align="left", text_font_size="9pt", text_color=RULE,
        text_baseline="middle")

    return ov.opts(
        width=width, height=90 + 46 * len(bgs),
        xlabel="firings per minute inside a block with nothing planted "
               "(every candidate on both sweeps)",
        ylabel="background rate (Hz per ROI)",
        yticks=ticks, ylim=(-0.8, len(bgs) - 0.2),
        xlim=(-0.4, hi * 1.06), show_legend=False,
        fontsize={"xlabel": "10pt", "ylabel": "10pt", "ticks": "9pt"},
        toolbar=None)


def main(argv=None) -> int:
    p = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    # SAP006: a tool that renders something to be READ defaults to the darkroom.
    p.add_argument("--out", type=Path, default=None,
                   help="destination (default: darkroom)")
    p.add_argument("--also", type=Path, default=None, help="extra copy, e.g. docs/learned")
    p.add_argument("--width", type=int, default=940)
    a = p.parse_args(argv)

    import holoviews as hv
    import panel as pn
    hv.extension("bokeh")

    from bugarach.bench import MAX_PROBE_PER_MIN
    from bugarach.paths import darkroom

    pt = _probe()
    ceiling = MAX_PROBE_PER_MIN[pt.DETECTOR]
    rows = collect(pt)
    refused = sum(1 for r in rows if r["probe"] > ceiling)
    print(f"  {len(rows)} candidates, {refused} refused at {ceiling:g}/min")
    for mode in ("additive", "multiplicative"):
        sub = [r for r in rows if r["mode"] == mode]
        n = sum(1 for r in sub if r["probe"] > ceiling)
        print(f"  {mode:15s} {n:3d}/{len(sub):<3d} refused   "
              f"max {max(r['probe'] for r in sub):6.1f}/min")

    spec = importlib.util.spec_from_file_location(
        "_mgf", Path(__file__).parent / "make_generator_figures.py")
    mgf = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mgf)

    page = pn.Column(pn.pane.HoloViews(build(rows, ceiling, a.width)))
    dests = [a.out or (darkroom() / "detector_history")]
    if a.also:
        dests.append(a.also)
    for dest in dests:
        dest.mkdir(parents=True, exist_ok=True)
        mgf._write(page, dest, "three_scoring_rules", png=True)
        print(f"  wrote {dest}/three_scoring_rules.png")
    return 0


if __name__ == "__main__":
    sys.exit(main())
