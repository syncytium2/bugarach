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

import numpy as np

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


def _time_axis(f, p, *, offset, step, label, minor=None):
    """Ticks every `step` seconds from `offset` (e.g. drug arrival), labeled in whole minutes or seconds,
    denser than svgfig's automatic choice (Tony, 2026-09-17: "x-axis in figure 2 needs more ticks")."""
    from svgfig import MUTED, fmt_time
    lo, hi = p.xlim[0] - offset, p.xlim[1] - offset
    k0, k1 = int(np.ceil(lo / step - 1e-9)), int(np.floor(hi / step + 1e-9))
    for k in range(k0, k1 + 1):
        t = k * step
        X = float(p.px(t + offset))
        f.line(X, p.y + p.h, X, p.y + p.h + 4, color=MUTED)
        f.text(X, p.y + p.h + 13, "0" if k == 0 else fmt_time(t, step), size=TICK_PT, anchor="middle", color=MUTED)
    if minor:
        m0, m1 = int(np.ceil(lo / minor - 1e-9)), int(np.floor(hi / minor + 1e-9))
        for k in range(m0, m1 + 1):
            X = float(p.px(k * minor + offset))
            f.line(X, p.y + p.h, X, p.y + p.h + 2, color=MUTED)
    if label:
        f.text(p.x + p.w / 2, p.y + p.h + 26, label, size=LABEL_PT, anchor="middle", color=MUTED, italic=True)


def _closeup(f, c, X, Y, PW, *, title, dets, raster_h, tick_step, stripe_marks=True, show_weak=False):
    """A real close-up for print: part-of-experiment strip, one call lane per program, clear stripes, raster.
    The page version's layout at print sizes (make_plain_detector_review._closeup)."""
    from make_plain_detector_review import COLORS, INK_T, NAMES, RED, _period_lane, _plural
    from svgfig import MUTED
    win = c["win"]
    y = Y
    if title:
        f.text(X, y, title, size=TITLE_PT, weight=600)
        y += 6
    pl = f.panel(X, y, PW, 16, win, (0, 1), frame=False)
    _period_lane(f, pl, c, y + 2)
    y += 20
    ROW = 11
    lp = f.panel(X, y, PW, len(dets) * ROW + 3, win, (0, 1))
    for i, d in enumerate(dets):
        ry = y + 2 + i * ROW
        weak = {round(on, 2) for on, _, _ in c["weak"].get(d, [])}
        for on, wd in c["calls"][d]:
            lp.span(on, on + max(wd, 0.0), row_y=ry, row_h=8, color=COLORS[d], min_px=2)
            if show_weak and round(on, 2) in weak:
                a, b = float(lp.px(on)) - 2, float(lp.px(on + max(wd, 0.0))) + 2
                f.rect(a, ry - 1.5, max(b - a, 5), 11, stroke=RED, width=1.2)
        n = sum(1 for on, _ in c["calls"][d] if win[0] <= on <= win[1])
        f.text(X - 6, ry + 7.5, f"{NAMES[d]} · {_plural(n, 'call')}", size=TICK_PT, anchor="end", color=MUTED)
    y += len(dets) * ROW + 8
    sp = f.panel(X, y, PW, 12, win, (0, 1), frame=False)
    if stripe_marks:
        for s_ in c["stripes"]:
            sp.down_triangle(s_["t"] + 0.5, y + 6, color=INK_T, size=7)
        f.text(X - 6, y + 9, "clear stripes", size=TICK_PT, anchor="end", color=MUTED)
    y += 14
    r = f.panel(X, y, PW, raster_h, win, (0, 1))
    r.raster(c["trains"], width=0.9)
    _time_axis(f, r, offset=c["anchor"], step=tick_step, label=f"minutes from the start of {c['label']}")
    f.text(X - 6, y + raster_h / 2, f"{c['stream'] == 'fast' and 'brief' or 'long'} events", size=LABEL_PT,
           anchor="end", color=MUTED)
    f.text(X - 6, y + raster_h / 2 + 11, _plural(c["n_roi"], "neuron"), size=LABEL_PT, anchor="end", color=MUTED)
    return y + raster_h + 34


def fig_problem(W):
    """Figure 2, different answers from different programs: 13 minutes of one real recording."""
    from make_plain_detector_review import CODED
    from svgfig import Figure
    c = W["real"]["close"]["problem"]
    f = Figure(PAGE_W, 300)
    f.h = _closeup(f, c, 104, 4, PAGE_W - 104 - 14, title="", dets=CODED, raster_h=150, tick_step=60.0)
    return f


def fig_chance(W):
    """Figure 3, busy neurons produce coordinated events by chance: a quiet minute with one planted event (A)
    and a busy minute with nothing planted (B), each with its count of neurons per 2 s bin."""
    from make_plain_detector_review import INK_T, _arr, _by_activity, _clock
    from svgfig import MUTED, Figure, nice_ticks
    sim = W["sim"]
    f = Figure(PAGE_W, 300)
    CW = 180
    cols = [("A", ("A · quiet neurons,", "one planted coordinated event"), 62),
            ("B", ("B · busy neurons,", "nothing planted"), 280)]
    for key, (t1, t2), X in cols:
        D = sim[key]
        win = D["win"]
        f.text(X, 11, t1, size=TITLE_PT, weight=600)
        f.text(X, 23, t2, size=TITLE_PT, weight=600)
        f.text(X, 35, f"one minute, from {_clock(win[0])} into the recording", size=PRINT_MIN_PT, color=MUTED)
        lane = f.panel(X, 40, CW, 13, win, (0, 1))
        if key == "A":
            lane.down_triangle(sim["event"]["time"], 47, color=INK_T, size=7)
        r = f.panel(X, 57, CW, 110, win, (0, 1))
        r.raster(_by_activity(D["trains"]), width=0.9)
        if key == "A":
            f.text(X - 6, 49, "planted", size=TICK_PT, anchor="end", color=MUTED)
            r.ylabel(f"{sim['n_roi']} neurons", size=LABEL_PT, dx=10)
        c = D["coact"]
        ymax = 12
        q = f.panel(X, 186, CW, 62, win, (0, ymax))
        ct, cy = _arr(c["t"]), _arr(c["y"])
        inside = (ct - 1.0 >= win[0] - 1e-6) & (ct + 1.0 <= win[1] + 1e-6)   # whole 2 s bins only
        q.bars(ct[inside], cy[inside], color="#6d8fb3", width_frac=0.9)
        q.yaxis(nice_ticks(0, ymax, 3), grid=True, size=TICK_PT)
        if key == "A":
            q.ylabel("neurons in each", lines=["neurons with an event", "in each 2 s bin"], size=TICK_PT, dx=30)
        q.xaxis_time(offset=win[0], target=4, label="seconds from the start of this minute", size=TICK_PT)
        mx = int(np.nanmax(cy[inside]))
        if key == "B":
            # the tallest bin, marked where it stands (Tony, 2026-09-17: "put an asterisk by the peak")
            k = int(np.nanargmax(np.where(inside, cy, -1)))
            f.text(float(q.px(ct[k])), float(q.py(cy[k])) - 2, "*", size=13, anchor="middle", weight=700,
                   color=INK_T)
            f.text(X + CW, 180, f"* most in one bin: {mx} neurons", size=TICK_PT, anchor="end", color=INK_T)
        else:
            f.text(X + CW, 180, f"most in one bin: {mx} neurons", size=TICK_PT, anchor="end", color=INK_T)
    f.h = 186 + 62 + 44
    return f


FIGURES = {"fig_orient": ("fig01_orient", fig_orient), "fig_problem": ("fig02_problem", fig_problem),
           "fig_chance": ("fig03_chance", fig_chance)}


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
