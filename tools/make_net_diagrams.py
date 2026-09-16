#!/usr/bin/env python3
"""Mechanism diagrams for the shipped tube and the three proposed classes of net.

    python tools/make_net_diagrams.py [--out DIR] [--also DIR]

⚠ **These are SCHEMATICS and every one of them says so on its own face.** They carry
no measured quantity, no parameter count and no traced shape. The front page's
architecture drawing is different in kind: draughtsman traces a real `torch` module
and resolves every number against that trace, so it *cannot* draw a stage the model
does not have. Three of the four networks below do not exist, so there is nothing to
trace, and a hand-built `graph.json` would claim a provenance it does not have. When
one is built, its figure is drawn by `tools/make_architecture_diagram.py` and this
one is retired.

Why a tool rather than hand-written markup: the layout is boxes, arrows and labels on
a grid, and a hundred hand-typed coordinates drift. Colour comes only from CSS custom
properties the host page defines, so a figure reads in a light page and a dark one.
"""
from __future__ import annotations

import argparse
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent

W = 880
BOX_H = 52
GAP = 20


def esc(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def note(text: str, x: float, y: float, width: float = 128, lead: float = 14.0) -> list:
    """The paragraph under a diagram, wrapped by hand. SVG text does not wrap, and
    a <text> longer than the viewBox simply runs off the edge without complaining."""
    words, lines, cur = text.split(), [], ""
    for w in words:
        if len(cur) + len(w) + 1 > width:
            lines.append(cur)
            cur = w
        else:
            cur = f"{cur} {w}".strip()
    if cur:
        lines.append(cur)
    return [f'<text class="dnote" x="{x}" y="{y + i*lead:.1f}">{esc(ln)}</text>'
            for i, ln in enumerate(lines)]


def wrap(body: str, height: int, label: str) -> str:
    return (f'<svg viewBox="0 0 {W} {height}" role="img" aria-label="{esc(label)}">\n'
            '<defs><marker id="ar" viewBox="0 0 8 8" refX="7" refY="4" markerWidth="7" '
            'markerHeight="7" orient="auto"><path d="M0,0 L8,4 L0,8 z" '
            'style="fill:var(--rule-strong)"/></marker></defs>\n'
            + body + "\n</svg>")


def chain(stages, y, x0=14.0, right=W - 14.0, warn=(), accent=()):
    """A left-to-right chain of stages. Each stage is (name, unit-under-the-box)."""
    n = len(stages)
    w = (right - x0 - GAP * (n - 1)) / n
    out, centres = [], []
    for i, (name, unit) in enumerate(stages):
        x = x0 + i * (w + GAP)
        cls = "nbox"
        if i in warn:
            cls += " warn"
        if i in accent:
            cls += " on"
        out.append(f'<rect class="{cls}" x="{x:.1f}" y="{y}" width="{w:.1f}" '
                   f'height="{BOX_H}" rx="3"/>')
        for j, line in enumerate(name.split("|")):
            out.append(f'<text class="nname" x="{x + w/2:.1f}" '
                       f'y="{y + (BOX_H/2 - 4) + j*13 - (len(name.split("|"))-1)*6:.1f}" '
                       f'text-anchor="middle">{esc(line)}</text>')
        for j, line in enumerate(unit.split("|")):
            out.append(f'<text class="nunit" x="{x + w/2:.1f}" '
                       f'y="{y + BOX_H + 15 + j*12:.1f}" text-anchor="middle">'
                       f'{esc(line)}</text>')
        centres.append((x, x + w))
        if i:
            px = centres[i - 1][1]
            out.append(f'<line class="arw" x1="{px:.1f}" y1="{y + BOX_H/2}" '
                       f'x2="{x - 4:.1f}" y2="{y + BOX_H/2}" marker-end="url(#ar)"/>')
    return out, centres, w


def raster_glyph(x, y, cols=9, rows=6, cell=7.0, marks=(), col_hit=None):
    """A small onset raster. NOTHING IS DRAWN ON IT — the rule holds for a schematic
    too, so a cue goes in the lane above, never over the marks (CLAUDE.md, 2026-08-26)."""
    out = [f'<rect class="rastbg" x="{x-2}" y="{y-2}" width="{cols*cell+4}" '
           f'height="{rows*cell+4}" rx="2"/>']
    for (r, c) in marks:
        out.append(f'<rect class="mkr" x="{x + c*cell:.1f}" y="{y + r*cell:.1f}" '
                   f'width="{cell-2:.1f}" height="{cell-2:.1f}"/>')
    if col_hit is not None:
        cx = x + col_hit * cell + (cell - 2) / 2
        out.append(f'<path class="lanetri" d="M{cx-4:.1f},{y-12:.1f} '
                   f'L{cx+4:.1f},{y-12:.1f} L{cx:.1f},{y-5:.1f} z"/>')
    return out


EVENT = [(r, 4) for r in range(6)]
BG = [(0, 0), (2, 1), (5, 2), (1, 6), (3, 7), (4, 8), (0, 8), (5, 6)]


# --------------------------------------------------------------- figure 3
def fig_tube() -> str:
    o = ['<text class="dtitle" x="14" y="20">what all four tubes read</text>']
    o += raster_glyph(24, 44, marks=EVENT + BG, col_hit=4)
    o.append('<text class="nunit" x="55" y="112" text-anchor="middle">'
             '9 cells × frames</text>')
    o.append('<text class="nunit" x="55" y="124" text-anchor="middle">binary</text>')
    st = [("widen each|onset", "cells × frames"),
          ("mean over|cells", "ONE trace|a fraction, 0 to 1"),
          ("difference-of-|Gaussian bank", "4 traces|zero-integral"),
          ("dilated|stack", "8 wide, 6 deep"),
          ("per-frame|score", "1 × frames")]
    body, centres, w = chain(st, 44, x0=112.0, warn=(1,))
    o += body
    o.append(f'<line class="arw" x1="94" y1="70" x2="108" y2="70" marker-end="url(#ar)"/>')
    # the bypass, which is the one path the kernel never reaches
    a = centres[1]
    b = centres[3]
    mid = (a[1] + b[0]) / 2
    o.append(f'<path class="bypass" d="M{a[1]:.1f},{44+BOX_H-8:.1f} '
             f'C{mid:.1f},{182} {mid:.1f},{182} {b[0]-4:.1f},{44+BOX_H-8:.1f}" '
             f'marker-end="url(#ar)"/>')
    o.append(f'<text class="nunit warn" x="{mid:.1f}" y="196" text-anchor="middle">'
             f'the bypass — the absolute level, un-normalized</text>')
    o.append(f'<text class="flag" x="{(a[0]+a[1])/2:.1f}" y="150" text-anchor="middle">'
             f'the cell axis ends here</text>')
    o.append(f'<text class="nunit" x="{(a[0]+a[1])/2:.1f}" y="164" text-anchor="middle">'
             f'below this stage the field size is only a divisor,</text>')
    o.append(f'<text class="nunit" x="{(a[0]+a[1])/2:.1f}" y="176" text-anchor="middle">'
             f'and nothing later can ask how many cells fired</text>')
    o += note("The guard moves a hole into the surround; the ratio replaces the "
              "subtraction with a difference of logs. Both act to the RIGHT of the "
              "flag, so all four variants share this stage and share its behaviour "
              "when the field changes size.", 14, 226)
    return wrap("\n".join(o), 264, "The tube pipeline, with the cell axis ending at "
                "the mean over cells")


# --------------------------------------------------------------- figure 4
def fig_chorus() -> str:
    o = ['<text class="dtitle" x="14" y="20">chorus — the cell axis survives '
         'the filter</text>']
    o += raster_glyph(16, 44, marks=EVENT + BG, col_hit=4)
    st = [("one shared filter,|run on each cell", "cells × channels × frames"),
          ("bounded vote|per cell", "one cell, one vote"),
          ("symmetric pool|over cells", "mean · spread · top-m|"
           "the SHAPE, not the level"),
          ("read the|pooled shape", "1 × frames")]
    body, centres, w = chain(st, 44, x0=112.0, accent=(2,))
    o += body
    o.append('<line class="arw" x1="94" y1="70" x2="108" y2="70" marker-end="url(#ar)"/>')
    a = centres[2]
    o.append(f'<text class="flag on" x="{(a[0]+a[1])/2:.1f}" y="148" '
             f'text-anchor="middle">every cell is still a cell here</text>')
    o += note("The pool returns several symmetric functions instead of one sum, so "
              "the head sees how the activity is DISTRIBUTED across the field and "
              "not only how much of it there is. Mean and top-m both carry over a "
              "change of field size; a sum does not. This is the Deep Sets shape "
              "(Zaheer and colleagues, 2017), and `tiny` is already a member of the "
              "family — which is the reason to re-run `tiny` under control before building anything new.", 14, 176)
    return wrap("\n".join(o), 226, "chorus: a per-cell filter, a bounded vote, and a "
                "symmetric pool that returns several statistics")


# --------------------------------------------------------------- figure 5
def fig_gauge() -> str:
    o = ['<text class="dtitle" x="14" y="20">gauge — the bar is built from the '
         'recording being judged</text>']
    o += raster_glyph(16, 50, marks=EVENT + BG, col_hit=4)
    o.append('<text class="nunit" x="48" y="118" text-anchor="middle">the window</text>')
    # three shifted copies, drawn small
    for i in range(3):
        rows = [((r + i + 1) % 6, (c + 2 * i + 1) % 9) for (r, c) in EVENT]
        o += raster_glyph(16, 152 + i * 30, rows=6, cell=4.4, marks=rows + [
            ((r + i) % 6, (c + i) % 9) for (r, c) in BG])
    o.append('<text class="nunit" x="48" y="248" text-anchor="middle">'
             'B copies, each cell|rolled on its own</text>')

    fx, fw, fy = 128.0, 168.0, 50.0
    o.append(f'<rect class="nbox" x="{fx}" y="{fy}" width="{fw}" height="{BOX_H}" rx="3"/>')
    o.append(f'<text class="nname" x="{fx+fw/2:.1f}" y="{fy+BOX_H/2+4:.1f}" '
             f'text-anchor="middle">any feature stage</text>')
    o.append(f'<rect class="nbox" x="{fx}" y="{fy+150}" width="{fw}" height="{BOX_H}" rx="3"/>')
    o.append(f'<text class="nname" x="{fx+fw/2:.1f}" y="{fy+150+BOX_H/2+4:.1f}" '
             f'text-anchor="middle">the same stage, shared weights</text>')
    o.append(f'<line class="arw" x1="94" y1="76" x2="{fx-4}" y2="76" marker-end="url(#ar)"/>')
    o.append(f'<line class="arw" x1="94" y1="226" x2="{fx-4}" y2="226" marker-end="url(#ar)"/>')

    sx, sw = fx + fw + 44, 196.0
    o.append(f'<rect class="nbox on" x="{sx}" y="{fy+66}" width="{sw}" height="{BOX_H+16}" rx="3"/>')
    o.append(f'<text class="nname" x="{sx+sw/2:.1f}" y="{fy+66+24:.1f}" '
             f'text-anchor="middle">standardize</text>')
    o.append(f'<text class="nunit" x="{sx+sw/2:.1f}" y="{fy+66+42:.1f}" '
             f'text-anchor="middle">(observed &#8722; null mean) &#247; null spread</text>')
    o.append(f'<path class="arw" d="M{fx+fw:.1f},{fy+BOX_H/2:.1f} '
             f'L{sx-14:.1f},{fy+BOX_H/2:.1f} L{sx-14:.1f},{fy+92:.1f} L{sx-4:.1f},'
             f'{fy+92:.1f}" marker-end="url(#ar)" fill="none"/>')
    o.append(f'<path class="arw" d="M{fx+fw:.1f},{fy+150+BOX_H/2:.1f} '
             f'L{sx-14:.1f},{fy+150+BOX_H/2:.1f} L{sx-14:.1f},{fy+100:.1f} '
             f'L{sx-4:.1f},{fy+100:.1f}" marker-end="url(#ar)" fill="none"/>')

    hx = sx + sw + 34
    hw = W - 14 - hx
    o.append(f'<rect class="nbox" x="{hx}" y="{fy+66}" width="{hw}" height="{BOX_H+16}" rx="3"/>')
    o.append(f'<text class="nname" x="{hx+hw/2:.1f}" y="{fy+66+30:.1f}" '
             f'text-anchor="middle">head → score</text>')
    o.append(f'<line class="arw" x1="{sx+sw}" y1="{fy+96}" x2="{hx-4}" y2="{fy+96}" '
             f'marker-end="url(#ar)"/>')
    o.append(f'<text class="flag on" x="{sx+sw/2:.1f}" y="{fy+146:.1f}" '
             f'text-anchor="middle">what leaves here has the same null at 9 cells and '
             f'at 1,050</text>')
    o += note("A roll is one tensor operation and costs nothing; what it costs is B "
              "extra passes through the feature stage, and that is the number to "
              "measure first. The shift destroys timing ACROSS cells and preserves "
              "each cell’s own rate and intervals exactly — which is why the same "
              "surrogate is under scrutiny elsewhere in this project, and why this "
              "one has to clear the same leak screen before it is trusted.", 14, 286)
    return wrap("\n".join(o), 340, "gauge: the feature stage is run on the window and "
                "on B surrogate copies, and the output is standardized against them")


# --------------------------------------------------------------- figure 6
def fig_quorum() -> str:
    o = ['<text class="dtitle" x="14" y="20">quorum — a rank, not a count and '
         'not a fraction</text>']
    o += raster_glyph(16, 44, marks=EVENT + BG, col_hit=4)
    st = [("score each cell|against ITS OWN rate", "a surprise per cell|busy cells "
           "are worth less"),
          ("sort the cells|within each frame", "an ordered column"),
          ("take the top m,|m = a × N to the power b", "b fitted between|0 and 1"),
          ("head|→ score", "1 × frames")]
    body, centres, w = chain(st, 44, x0=112.0, accent=(2,))
    o += body
    o.append('<line class="arw" x1="94" y1="70" x2="108" y2="70" marker-end="url(#ar)"/>')
    a = centres[2]
    o.append(f'<text class="flag on" x="{(a[0]+a[1])/2:.1f}" y="148" text-anchor="middle">'
             f'b = 0 is a fixed count · b = 1 is a fixed fraction</text>')
    o += note("Figure 2, the chance floor, says the honest rule lies between those "
              "two bounds, so the exponent is fitted rather than chosen and its "
              "fitted value is itself the result. If it runs to a bound, one of the "
              "two rules was right after all. This is ordered-statistic CFAR moved "
              "off the time axis and onto the cell axis — the censored surround the "
              "tube screen left out, where a partial sort over cells costs one kernel instead of a sliding window.", 14, 176)
    return wrap("\n".join(o), 230, "quorum: per-cell surprise, a sort over cells, and a "
                "top-m pool whose m grows with the field size at a fitted exponent")


# --------------------------------------------------------------- figure 7
def fig_axes() -> str:
    o = ['<text class="dtitle" x="14" y="20">three axes on one skeleton, not three '
         'horses in one race</text>']
    st = [("raster", "cells × frames"),
          ("per-cell|stage", "A · chorus"),
          ("pool over|cells", "C · quorum"),
          ("calibrate", "B · gauge"),
          ("head|→ score", "1 × frames")]
    body, centres, w = chain(st, 40, accent=(1, 2, 3))
    o += body
    for i, (name, blurb) in enumerate((
            ("A", "what each cell contributes, before anything is pooled"),
            ("C", "how the field is summarized into one number"),
            ("B", "what the number is compared against"))):
        a = centres[i + 1]
        o.append(f'<text class="axl" x="{(a[0]+a[1])/2:.1f}" y="128" '
                 f'text-anchor="middle">{name}</text>')
        o.append(f'<text class="nunit" x="{(a[0]+a[1])/2:.1f}" y="146" '
                 f'text-anchor="middle">{esc(blurb)}</text>')
    o += note("The shipped tube fills all three: A is nothing, C is a mean, and B is a "
              "difference of Gaussians in time. The 2\u00d72 that produced the guard "
              "and the ratio variants moved B alone, twice, which is why none of the "
              "four can differ from the others when the field changes size. Each "
              "proposal moves one axis, with the shipped tube as the control, "
              "re-measured in the same run.", 14, 176)
    return wrap("\n".join(o), 216, "The three proposed classes as three swap points on "
                "one shared skeleton")


FIGS = {"net_fig3_tube.svg": fig_tube,
        "net_fig4_chorus.svg": fig_chorus,
        "net_fig5_gauge.svg": fig_gauge,
        "net_fig6_quorum.svg": fig_quorum,
        "net_fig7_axes.svg": fig_axes}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", default=None, help="where the SVGs go (default: darkroom)")
    ap.add_argument("--also", default=None, help="a second copy, usually the repo")
    args = ap.parse_args()
    out_dir = args.out
    if out_dir is None:
        try:
            from bugarach.paths import darkroom
            out_dir = str(darkroom())
        except Exception:                                   # pragma: no cover
            out_dir = str(REPO / "docs" / "proposals" / "figures")
    for d in [out_dir] + ([args.also] if args.also else []):
        Path(d).mkdir(parents=True, exist_ok=True)
        for name, fn in FIGS.items():
            (Path(d) / name).write_text(fn() + "\n")
            print(Path(d) / name)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
