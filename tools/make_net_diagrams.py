#!/usr/bin/env python3
"""The one hand-drawn figure on the field-size page: three axes on one skeleton.

    python tools/make_net_diagrams.py [--out DIR] [--also DIR]

⚠ **A SCHEMATIC, and it says so on its own face.** It carries no measured quantity, no
parameter count and no traced shape, because it is a map of a design SPACE rather than
of a model: which slot each proposal moves, on a skeleton none of the four networks is.

**Every figure here that draws a MODEL is drawn by draughtsman instead**, from a
`torch.jit.trace` of the built module, with coverage checked before anything is
written — `tools/make_architecture_diagram.py --arch {tube,chorus,gauge,quorum}`. That
matters rather than being a preference: a hand-drawn diagram of a model that exists is
a second description of it, free to drift, and the tool exists because five others drew
this project's own tube and the best of them silently omitted five stages while
reporting success. This file kept four such diagrams until 2026-09-16, when the three
proposed networks were written and could be traced like anything else; they are gone
and `make_architecture_diagram.py` draws them.

Why a tool rather than hand-written markup, for the one that remains: the layout is
boxes, arrows and labels on a grid, and a hundred hand-typed coordinates drift. Colour
comes only from CSS custom properties the host page defines, so the figure reads in a
light page and a dark one.
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
              "re-measured in the same run.", 14, 190)
    return wrap("\n".join(o), 216, "The three proposed classes as three swap points on "
                "one shared skeleton")


FIGS = {"net_fig7_axes.svg": fig_axes}


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
