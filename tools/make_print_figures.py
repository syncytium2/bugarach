#!/usr/bin/env python3
"""Print versions of the plain review's figures, drawn at the size the Word page gives them.

    python tools/make_print_figures.py --plain <darkroom>/bugarach/2026-09-15-detector-review-plain --figs fig_orient

Why a second set (Tony, 2026-09-17: "start remaking each figure with proper font sizes"). The page figures
were drawn on a canvas about 1000 units wide for a web column and placed 6.5 in wide in the Word document,
so their 11-13 unit labels printed at 5-6 pt beside 11 pt text (murderboard 2026-09-17, role 10). Here the
canvas IS the placed width: 1 unit = 1 pt at 6.5 in (468 units), so a font size in this file is the size a
reader sees. Nothing goes below PRINT_MIN_PT.

Reads the same measurements as `make_plain_detector_review.py` (`_work/plain.json`); writes SVG and PNG to
`<plain>/print_figures/` only. They are NOT put into the document: Tony is editing it by hand.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

#: The Word page's text width in points, the canvas width of every print figure.
PAGE_W = 468
#: Smallest text allowed in a print figure, in points.
PRINT_MIN_PT = 8
#: Body sizes: panel titles, labels and ticks.
TITLE_PT, LABEL_PT, TICK_PT = 10, 9, 8.5
#: PNG pixels per point: 4 gives 1872 px across 6.5 in, about 290 pixels per inch.
SCALE = 4


def fig_orient(W):
    """Figure 1, how to read a raster: ten minutes of one real recording (A) and 20 s of it (B)."""
    from make_plain_detector_review import INK_T, _by_activity, _plural
    from svgfig import MUTED, Figure

    c = W["real"]["close"]["orient"]
    win = c["win"]
    f = Figure(PAGE_W, 300)
    L, PW = 58, 286                       # panel A
    ZX, ZW = 378, 74                      # panel B
    TOP, RH = 42, 200                     # raster top and height

    f.text(L, 12, "A · ten minutes of one real recording", size=TITLE_PT, weight=600)
    lane = f.panel(L, 20, PW, 16, win, (0, 1), frame=False)
    for s_ in c["stripes"]:
        lane.down_triangle(s_["t"] + 0.5, 28, color=INK_T, size=7)
    f.text(L - 8, 27, "clear", size=TICK_PT, anchor="end", color=MUTED)
    f.text(L - 8, 36, "stripes", size=TICK_PT, anchor="end", color=MUTED)
    r = f.panel(L, TOP, PW, RH, win, (0, 1))
    r.raster(_by_activity(c["trains"]), width=0.8)
    r.xaxis_time(offset=win[0], target=5, label="minutes", size=TICK_PT)
    r.ylabel(_plural(c["n_roi"], "neuron"), size=LABEL_PT, dx=14)

    stripes = sorted(c["stripes"], key=lambda s_: -s_["cells"])
    top = stripes[0]["t"] if stripes else (win[0] + win[1]) / 2
    z = (top - 10.0, top + 10.0)
    f.text(ZX, 12, "B · 20 s of A", size=TITLE_PT, weight=600)
    lz = f.panel(ZX, 20, ZW, 16, z, (0, 1), frame=False)
    lz.down_triangle(top + 0.5, 28, color=INK_T, size=7)
    rz = f.panel(ZX, TOP, ZW, RH, z, (0, 1))
    rz.raster(_by_activity(c["trains"]), width=1.4)
    rz.xaxis_time(offset=top, target=2, label="seconds", size=TICK_PT)
    # which 20 s B shows: a gray bar in A's marker lane, named where it sits (never drawn on the raster)
    lane.span(z[0], z[1], row_y=37, row_h=3, color="#9a9a9a", min_px=3)
    f.text(float(lane.px(z[1])) + 3, 41, "B", size=PRINT_MIN_PT, color=MUTED)
    f.h = TOP + RH + 46
    return f


FIGURES = {"fig_orient": ("fig01_orient", fig_orient)}


def render(figs: dict, out: Path) -> None:
    from playwright.sync_api import sync_playwright
    out.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as pw:
        br = pw.chromium.launch()
        page = br.new_page(device_scale_factor=SCALE, viewport={"width": PAGE_W + 20, "height": 900})
        for stem, f in figs.items():
            svg = f.svg()
            (out / f"{stem}.svg").write_text(svg, encoding="utf-8")
            page.set_content(f"<meta charset='utf-8'><body style='margin:0;background:#fff'>{svg}</body>")
            page.locator("svg").first.screenshot(path=str(out / f"{stem}.png"))
            print("  wrote", stem, f"{PAGE_W}x{f.h:.0f} pt")
        br.close()


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--plain", type=Path, required=True, help="the plain review's darkroom folder")
    ap.add_argument("--figs", nargs="+", default=list(FIGURES))
    a = ap.parse_args(argv)
    W = json.loads((a.plain / "_work" / "plain.json").read_text())
    figs = {FIGURES[n][0]: FIGURES[n][1](W) for n in a.figs}
    render(figs, a.plain / "print_figures")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
