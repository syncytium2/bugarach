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


def _closeup(f, c, X, Y, PW, *, title, dets, raster_h, tick_step, stripe_marks=True, show_weak=False, ROW=11):
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
    bar = ROW - 3
    lp = f.panel(X, y, PW, len(dets) * ROW + 3, win, (0, 1))
    for i, d in enumerate(dets):
        ry = y + 2 + i * ROW
        weak = {round(on, 2) for on, _, _ in c["weak"].get(d, [])}
        for on, wd in c["calls"][d]:
            lp.span(on, on + max(wd, 0.0), row_y=ry, row_h=bar, color=COLORS[d], min_px=2)
            if show_weak and round(on, 2) in weak:
                a, b = float(lp.px(on)) - 2, float(lp.px(on + max(wd, 0.0))) + 2
                f.rect(a, ry - 1.5, max(b - a, 5), bar + 3, stroke=RED, width=1.2)
        n = sum(1 for on, _ in c["calls"][d] if win[0] <= on <= win[1])
        f.text(X - 6, ry + bar - 0.5, f"{NAMES[d]} · {_plural(n, 'call')}",
               size=TICK_PT if ROW >= 11 else PRINT_MIN_PT, anchor="end", color=MUTED)
    y += len(dets) * ROW + 8
    sp = f.panel(X, y, PW, 12, win, (0, 1), frame=False)
    if stripe_marks:
        for s_ in c["stripes"]:
            sp.down_triangle(s_["t"] + 0.5, y + 6, color=INK_T, size=7)
        f.text(X - 6, y + 9, "clear stripes", size=TICK_PT, anchor="end", color=MUTED)
    y += 14
    r = f.panel(X, y, PW, raster_h, win, (0, 1))
    r.raster(c["trains"], width=0.9)
    if tick_step is None:   # 3 to 7 ticks whatever the window: a fixed minute gave a 1-minute close-up one tick
        wlen = win[1] - win[0]
        tick_step = next((s_ for s_ in (5, 10, 15, 20, 30, 60, 120, 300, 600) if wlen / s_ <= 7), 600)
    lab = f"minutes from the start of {c['label']}"
    compact = ROW < 11
    _time_axis(f, r, offset=c["anchor"], step=float(tick_step), label=None if compact else lab)
    if compact:             # beside the ticks, in the margin, so it cannot run into the next panel's title
        f.text(X - 18, y + raster_h + 9, "minutes from the", size=PRINT_MIN_PT, anchor="end", color=MUTED,
               italic=True)
        f.text(X - 18, y + raster_h + 18.5, f"start of {c['label']}", size=PRINT_MIN_PT, anchor="end",
               color=MUTED, italic=True)
    f.text(X - 6, y + raster_h / 2, f"{c['stream'] == 'fast' and 'brief' or 'long'} events", size=LABEL_PT,
           anchor="end", color=MUTED)
    f.text(X - 6, y + raster_h / 2 + 11, _plural(c["n_roi"], "neuron"), size=LABEL_PT, anchor="end", color=MUTED)
    return y + raster_h + (30 if compact else 34)


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


def _hist(f, X, Y, Wd, Hh, hist, *, observed, bar, color, xlabel, title, log=False, xmax=None, ylabel=""):
    """The chance histogram at print sizes (make_plain_detector_review._hist_panel)."""
    import math

    from make_plain_detector_review import BARC, GREEN
    from svgfig import MUTED, nice_ticks
    hist = np.asarray(hist, float)
    xmax = xmax or len(hist) - 1
    hist = hist[:xmax + 1]
    f.text(X, Y - 8, title, size=LABEL_PT, weight=600)
    if log:
        vals = np.where(hist > 0, np.log10(np.maximum(hist, 1)), np.nan)
        top = math.ceil(np.nanmax(vals))
        p = f.panel(X, Y, Wd, Hh, (-0.6, xmax + 0.6), (0, top))
        p.bars(np.arange(xmax + 1), vals, color=color, width_frac=0.85)
        for v in range(0, top + 1, 2):
            Yp = float(p.py(v))
            f.line(X - 3, Yp, X, Yp, color=MUTED)
            f.text(X - 5, Yp + 3, f"{10 ** v:,.0f}", size=PRINT_MIN_PT, anchor="end", color=MUTED)
        if ylabel:   # clear of the widest tick label ("1,000,000" ran into "copied frames")
            p.ylabel(ylabel, size=PRINT_MIN_PT, dx=round(12 + 4.2 * len(f"{10 ** top:,.0f}")))
    else:
        top = max(1.0, hist.max() * 1.15)
        p = f.panel(X, Y, Wd, Hh, (-0.6, xmax + 0.6), (0, top))
        p.bars(np.arange(xmax + 1), hist, color=color, width_frac=0.85)
        for v in nice_ticks(0, top, 3):
            Yp = float(p.py(v))
            f.line(X - 3, Yp, X, Yp, color=MUTED)
            f.text(X - 5, Yp + 3, f"{v:,.0f}", size=PRINT_MIN_PT, anchor="end", color=MUTED)
        if ylabel:
            p.ylabel(ylabel, size=PRINT_MIN_PT, dx=26)
    step = 2 if xmax <= 14 else 5
    for v in range(0, xmax + 1, step):
        Xv = float(p.px(v))
        f.line(Xv, Y + Hh, Xv, Y + Hh + 3, color=MUTED)
        f.text(Xv, Y + Hh + 12, f"{v:g}", size=PRINT_MIN_PT, anchor="middle", color=MUTED)
    f.text(X + Wd / 2, Y + Hh + 23, xlabel, size=PRINT_MIN_PT, anchor="middle", color=MUTED, italic=True)
    if bar is not None and np.isfinite(bar):
        Xb = float(p.px(bar))
        f.line(Xb, Y, Xb, Y + Hh, color=BARC, width=1.5, dash="4 3")
        f.text(Xb + 3, Y + 10, "bar", size=PRINT_MIN_PT, weight=600)
    if observed is not None:
        p.down_triangle(observed, Y - 1, color=GREEN, size=8)
    return p


def fig_algorithm(W, det):
    """Figures 10-15, how each program decides: its steps and settings across the top, then what it sees
    in a planted event (A) and in a busy stretch (B) across the full width."""
    from make_plain_detector_review import (BARC, COLORS, GREEN, INK_T, LINE_LABELS, MEASURE, NAMES, RED,
                                            _by_activity, _clock, _found, _measure, _plural, _settings_rows,
                                            _steps_text)
    from svgfig import MUTED, Figure, nice_ticks
    sim = W["sim"]
    st = sim["settings"][det]
    ev = sim["event"]
    col = COLORS[det]
    f = Figure(PAGE_W, 700)

    # the steps, full width
    f.text(0, 11, f"How {NAMES[det]} decides", size=TITLE_PT + 1, weight=700)
    y = 28
    for i, s in enumerate(_steps_text(det, st)):
        f.add(f"<circle cx='7' cy='{y - 3:.1f}' r='6' fill='{col}'/>")
        f.text(7, y, str(i + 1), size=PRINT_MIN_PT, anchor="middle", weight=700, color="#fff")
        y = f.para(18, y, s, width_chars=112, size=LABEL_PT, lh=1.3) + 4

    # the settings (left) beside the chance picture (right)
    top = y + 2
    rows = _settings_rows(det, st)
    lab_x = max(66, 8 + 4.4 * max(len(v_) for v_, _ in rows) + 8)   # "4.5 per second" ran into its label
    SW = max(222, round(lab_x + 3.75 * max(len(l_) for _, l_ in rows) + 10))
    f.text(8, top + 14, "Settings", size=TITLE_PT, weight=700)
    yy = top + 28
    for val, lab in rows:
        f.text(8, yy, val, size=LABEL_PT, weight=700, color=col)
        f.text(lab_x, yy, lab, size=PRINT_MIN_PT, color=INK_T)
        yy += 12
    f.rect(1, top, SW, yy - top - 4, stroke=col, width=1.1, rx=4)
    box_bottom = yy - 4

    R = SW + 14                       # the chance picture's column
    RW = PAGE_W - R
    hy = top + 12
    if det in ("coact", "loco"):
        if det == "coact":
            q, b = sim["chance_coact"], sim["chance_coact_B"]
            f.text(R, hy - 2, "100 shifted copies of the 60 s around one bin:", size=PRINT_MIN_PT, color=MUTED)
            parts = [(np.bincount(np.asarray(qq["counts"], int), minlength=15)[:15], qq["observed"], qq["bar"],
                      lab) for qq, lab in ((q, "a quiet minute (A)"), (b, "a busy minute (B)"))]
            kw = dict(color="#b9c6d6", log=False, xmax=14, ylabel="copies")
        else:
            q = sim["chance_loco"]
            f.text(R, hy - 2, "100 shifted copies of each side of the planted event:", size=PRINT_MIN_PT,
                   color=MUTED)
            parts = [(q["before"], None, q["p999_before"], "the minute before"),
                     (q["after"], q["observed"], q["p999_after"], "the minute after")]
            kw = dict(color="#c9b6e4", log=True, xmax=10, ylabel="copied bins")
        HW = (RW - 80 - 6) // 2
        for j, (h, obs, bar, lab) in enumerate(parts):
            X = R + 40 + j * (HW + 40)
            _hist(f, X, hy + 22, HW, 62, h, observed=obs, bar=bar, xlabel="neurons", title=lab,
                  **{**kw, "ylabel": kw["ylabel"] if j == 0 else ""})
        chance_bottom = hy + 22 + 62 + 26
    elif det in ("sce", "cicada"):
        if det == "sce":
            q = sim["chance_sce"]
            head, kw = "200 shifted copies of the whole recording, pooled:", dict(
                color="#b8dcb8", xlabel="neurons in a 10 s bin", title="every bin of 200 copies", xmax=20,
                ylabel="copied bins")
        else:
            q = sim["chance_cicada"]
            head, kw = "100 shifted copies of the whole recording, pooled:", dict(
                color="#f0b8da", xlabel="neurons switched on in a frame", title="every frame of 100 copies",
                xmax=14, ylabel="copied frames")
        f.text(R, hy - 2, head, size=PRINT_MIN_PT, color=MUTED)
        _hist(f, R + 58, hy + 22, RW - 64, 62, q["hist"], observed=q["observed"], bar=q["bar"], log=True, **kw)
        chance_bottom = hy + 22 + 62 + 26
    elif det == "rate":
        ctx_s = float(st.get("context_win", 60.0))
        rate_s = float(st.get("rate_win", 1.0))
        f.text(R, hy - 2, "The two windows, at one moment:", size=LABEL_PT, weight=600)
        span = (-ctx_s / 2 - 6, ctx_s / 2 + 6)
        wp = f.panel(R + 8, hy + 14, RW - 16, 40, span, (0, 1), frame=False)
        X0 = float(wp.px(0))
        f.text(X0, hy + 12, "the moment being scored", size=PRINT_MIN_PT, anchor="middle", color=MUTED)
        wp.span(-ctx_s / 2, ctx_s / 2, row_y=hy + 17, row_h=14, color="#cfd9e6")
        f.text(float(wp.px(-ctx_s / 2)) + 4, hy + 27, f"context window · {ctx_s:g} s", size=PRINT_MIN_PT)
        wp.span(-rate_s / 2, rate_s / 2, row_y=hy + 34, row_h=14, color=COLORS["rate"], min_px=3)
        f.text(X0 + 6, hy + 44, f"counting window · {rate_s:g} s", size=PRINT_MIN_PT)
        f.line(X0, hy + 15, X0, hy + 52, color=BARC, width=0.8, dash="2 2")
        for v in (-30, 0, 30):
            Xv = float(wp.px(v))
            f.line(Xv, hy + 54, Xv, hy + 57, color=MUTED)
            f.text(Xv, hy + 65, f"{v:g}s", size=PRINT_MIN_PT, anchor="middle", color=MUTED)
        yb = f.para(R, hy + 82, f"Every event from every neuron inside the {rate_s:g} s window is counted and "
                                f"compared with the average over the {ctx_s:g} s window centred on the same "
                                f"moment. No copies are made.", width_chars=50, size=PRINT_MIN_PT, color=MUTED)
        chance_bottom = f.para(R, yb + 3, "Both widths are settings, like the bar. So far only the bar has "
                                          "been tuned.", width_chars=50, size=PRINT_MIN_PT, color=MUTED)
    else:  # sync
        n = sim["n_roi"]
        f.text(R, hy - 2, "Why small events cannot reach the bar:", size=LABEL_PT, weight=600)
        f.text(R, hy + 10, "the highest score an event can reach, by neurons joining it:", size=PRINT_MIN_PT,
               color=MUTED)
        p = f.panel(R + 10, hy + 32, RW - 24, 20, (0, 0.3), (0, 1))
        for k_ in sorted({3, ev["n_part"], 10}):
            v = (k_ - 1) / (n - 1)
            X = float(p.px(v))
            f.line(X, hy + 32, X, hy + 52, color=COLORS["sync"], width=1.6)
            f.text(X, hy + 28, f"{k_} neurons", size=PRINT_MIN_PT, anchor="middle", color=COLORS["sync"])
        Xb = float(p.px(st.get("C_threshold", 0.1)))
        f.line(Xb, hy + 30, Xb, hy + 55, color=BARC, width=2)
        for v in (0, 0.1, 0.2, 0.3):
            Xv = float(p.px(v))
            f.line(Xv, hy + 52, Xv, hy + 55, color=MUTED)
            f.text(Xv, hy + 64, f"{v:.1f}", size=PRINT_MIN_PT, anchor="middle", color=MUTED)
        f.text(Xb, hy + 74, "bar", size=PRINT_MIN_PT, anchor="middle", weight=700)
        chance_bottom = f.para(R, hy + 90, f"With {n} neurons, an event joined by k neurons can score at most "
                                           f"(k−1) ÷ {n - 1}. An event joined by 3 neurons tops out at "
                                           f"{2 / (n - 1):.2f}, below the bar.", width_chars=50,
                               size=PRINT_MIN_PT, color=MUTED)

    # the two views, full width
    y0 = max(box_bottom, chance_bottom) + 18
    L, VW, GAP = 52, 186, 30
    label, sub, ylim = MEASURE[det]
    for j, (key, title) in enumerate((("A", "A · a planted event (quiet neurons)"),
                                      ("B", "B · a busy stretch, nothing planted"))):
        D = sim[key]
        X = L + j * (VW + GAP)
        win = D["win"]
        f.text(X, y0, title, size=TITLE_PT, weight=600)
        f.text(X, y0 + 11, f"one minute, from {_clock(win[0])} into the recording", size=PRINT_MIN_PT,
               color=MUTED)
        calls = D[f"{det}_calls"]
        ly = y0 + 16
        lane = f.panel(X, ly, VW, 26, win, (0, 1))
        if key == "A":
            ok = _found(calls, ev["time"])
            lane.down_triangle(ev["time"], ly + 8, color=GREEN if ok else RED, size=8)
        for on, wd in calls:
            lane.span(on, on + max(wd, 0.0), row_y=ly + 15, row_h=8, color=col, min_px=2)
        n_calls = sum(1 for on, wd in calls if on + wd >= win[0] and on <= win[1])
        f.text(X + VW - 3, ly + 9, _plural(n_calls, "call"), size=PRINT_MIN_PT, anchor="end", color=MUTED)
        ry = ly + 30
        # 80 and 84, not 96: at 96 SPIKE-synch's figure pushed its caption onto the next Word page
        r = f.panel(X, ry, VW, 80, win, (0, 1))
        r.raster(_by_activity(D["trains"]), width=0.8)
        my = ry + 80 + 8 + 14 * 1            # room for the line key below
        p = f.panel(X, my + 8, VW, 84, win, ylim)
        _measure_print(p, det, D, _measure)
        for v in nice_ticks(*ylim, 4):
            Yv = float(p.py(v))
            f.line(X, Yv, X + VW, Yv, color="#ececec")
            f.line(X - 3, Yv, X, Yv, color=MUTED)
            f.text(X - 5, Yv + 3, f"{v:g}", size=PRINT_MIN_PT, anchor="end", color=MUTED)
        if j == 0:
            r.ylabel(f"{sim['n_roi']} neurons", size=LABEL_PT, dx=12)
            f.text(X - 5, ly + 11, "planted", size=PRINT_MIN_PT, anchor="end", color=MUTED)
            f.text(X - 5, ly + 22, "calls", size=PRINT_MIN_PT, anchor="end", color=MUTED)
            p.ylabel(label, lines=[label] + ([sub] if sub else []), size=PRINT_MIN_PT, dx=34 if sub else 30)
        _time_axis(f, p, offset=win[0], step=15.0, label="seconds from the start of this minute")
    # what each line is, named between raster and measurement, once, across both columns
    kx, ky = L, my + 2
    for text, c_, _k in LINE_LABELS[det]:
        f.text(kx, ky, "▬", size=LABEL_PT, weight=700, color=COLORS.get(c_, c_))
        f.text(kx + 11, ky, text, size=PRINT_MIN_PT, color=MUTED)
        kx += 11 + 3.7 * len(text) + 16
    by = my + 8 + 84 + 42
    kx = L
    for c_, lab in ((GREEN, "planted event, found"), (RED, "planted event, missed")):
        f.text(kx, by, "▼", size=LABEL_PT, weight=700, color=c_)
        f.text(kx + 11, by, lab, size=PRINT_MIN_PT, color=MUTED)
        kx += 11 + 3.7 * len(lab) + 18
    f.h = by + 8
    return f


def _measure_print(p, det, D, page_measure):
    """The measurement lines, thinner than the page's for a panel a fifth the size."""
    from make_plain_detector_review import BARC, COLORS, GREY, _arr
    c = COLORS[det]
    M = D[det]
    if det == "rate":
        p.curve(_arr(M["t"]), _arr(M["ref"]), color=GREY, width=1.6)
        p.curve(_arr(M["t"]), _arr(M["y"]), color=c, width=0.9)
        p.curve(_arr(M["t"]), _arr(M["bar"]), color=BARC, width=1.3, dash="4 3")
    elif det == "coact":
        p.steps(_arr(M["t"]), _arr(M["y"]), color=c, width=1.1)
        p.dots(_arr(M["t"]), _arr(M["mean"]), color=GREY, r=1.6)
        p.dashes(_arr(M["t"]), _arr(M["bar"]), color=BARC, half_width=3, width=1.6)
    elif det in ("loco", "sce", "cicada"):
        p.steps(_arr(M["t"]), _arr(M["y"]), color=c, width=1.0 if det != "cicada" else 0.7)
        p.steps(_arr(M["t"]), _arr(M["bar"]), color=BARC, width=1.3, dash="4 3")
    else:
        p.dots(_arr(M["px"]), _arr(M["py"]), color=c, r=1.5, opacity=0.8)
        p.curve(_arr(M["cx"]), _arr(M["cy"]), color="#7a2a00", width=0.8)
        p.hline(M["bar"], color=BARC, width=1.3, dash="4 3")


def fig_scores(W):
    """Figure 18, the six programs' overall scores on held-out simulated recordings, quiet (A) and busy (B)."""
    from make_plain_detector_review import BARC, CODED, COLORS, GRID_C, INK_T, NAMES
    from svgfig import MUTED, Figure
    numbers = W["_numbers"]
    dets = list(CODED)
    f = Figure(PAGE_W, 300)
    ceil = numbers["f1_ceiling"]
    TOP, RH = 22, 22 * len(dets)
    for j, (reg, title) in enumerate((("baseline_quiet", "A · quiet background"),
                                      ("baseline_busy", "B · busy background"))):
        X, PW = 76 + j * 200, 178
        f.text(X, 12, title, size=TITLE_PT, weight=600)
        p = f.panel(X, TOP, PW, RH, (0, 1), (len(dets) - 0.5, -0.5))
        for v in (0, 0.2, 0.4, 0.6, 0.8, 1.0):
            Xv = float(p.px(v))
            f.line(Xv, TOP, Xv, TOP + RH, color=GRID_C)
            f.line(Xv, TOP + RH, Xv, TOP + RH + 3, color=MUTED)
            f.text(Xv, TOP + RH + 12, f"{v:g}", size=TICK_PT, anchor="middle", color=MUTED)
        Xc = float(p.px(ceil))
        f.line(Xc, TOP, Xc, TOP + RH, color=BARC, dash="4 3", width=1.1)
        for i, d in enumerate(dets):
            v = numbers[f"stored_{reg}_{d}"]
            Y = float(p.py(i))
            f.line(float(p.px(v["f1_min"])), Y, float(p.px(v["f1_max"])), Y, color=COLORS[d], width=2.2)
            f.add(f"<circle cx='{float(p.px(v['f1'])):.1f}' cy='{Y:.1f}' r='4' fill='{COLORS[d]}'/>")
            if j == 0:
                f.text(X - 6, Y + 3, NAMES[d], size=LABEL_PT, anchor="end", color=INK_T)
        f.text(X + PW / 2, TOP + RH + 25, "overall score (0 to 1; higher is better)", size=LABEL_PT,
               anchor="middle", color=MUTED, italic=True)
    sr = numbers["stored_rounds"]
    ky = TOP + RH + 44
    kx = 76
    for glyph, col, lab in (("●", INK_T, f"all {sr['n_recordings']} recordings"),
                            ("━", INK_T, f"lowest to highest of {sr['n_groups']} groups of {sr['per_group']}"),
                            ("┄", BARC, f"best possible ({ceil:.2f})")):
        f.text(kx, ky, glyph, size=LABEL_PT, weight=700, color=col)
        f.text(kx + 11, ky, lab, size=TICK_PT, color=MUTED)
        kx += 11 + 3.9 * len(lab) + 16
    f.h = ky + 8
    return f


def fig_busy(W):
    """Figure 19, the busy stretch: planted events found outside and inside it (A), false alarms inside (B)."""
    import math

    from make_plain_detector_review import CODED, COLORS, GRID_C, INK_T, NAMES
    from svgfig import MUTED, Figure
    numbers = W["_numbers"]
    b = numbers["blockrecall"]["per_detector"]
    dets = list(CODED)
    f = Figure(PAGE_W, 300)
    n_roi = int(numbers["bench_n_roi"])
    cells = int(round(0.18 * n_roi))
    TOP, RH = 34, 22 * len(dets)
    X, PW = 76, 214
    f.text(X, 11, f"A · events joined by {cells} of the {n_roi} neurons,", size=TITLE_PT, weight=600)
    f.text(X, 24, "the usual real size", size=TITLE_PT, weight=600)
    p = f.panel(X, TOP, PW, RH, (0, 1), (len(dets) - 0.5, -0.5))
    for v in (0, 0.25, 0.5, 0.75, 1.0):
        Xv = float(p.px(v))
        f.line(Xv, TOP, Xv, TOP + RH, color=GRID_C)
        f.line(Xv, TOP + RH, Xv, TOP + RH + 3, color=MUTED)
        f.text(Xv, TOP + RH + 12, f"{v:.0%}", size=TICK_PT, anchor="middle", color=MUTED)
    for i, d in enumerate(dets):
        v = b[d]["p18"]
        Y = float(p.py(i))
        xo, xi = float(p.px(v["outside"])), float(p.px(v["inside"]))
        f.line(xo, Y, xi, Y, color="#bbb", width=1.6)
        ch = float(p.px(v["chance"]))
        f.line(ch, Y - 6, ch, Y + 6, color="#999", width=1.6)
        f.add(f"<circle cx='{xo:.1f}' cy='{Y:.1f}' r='4' fill='{INK_T}'/>")
        f.add(f"<circle cx='{xi:.1f}' cy='{Y:.1f}' r='4' fill='#d9730d'/>")
        f.text(X - 6, Y + 3, NAMES[d], size=LABEL_PT, anchor="end", color=INK_T)
    f.text(X + PW / 2, TOP + RH + 25, "share of planted events found", size=LABEL_PT, anchor="middle",
           color=MUTED, italic=True)
    X2, PW2 = 318, 120
    f.text(X2, 11, "B · false alarms", size=TITLE_PT, weight=600)
    f.text(X2, 24, "in the busy stretch", size=TITLE_PT, weight=600)
    q = f.panel(X2, TOP, PW2, RH, (-2, 1.3), (len(dets) - 0.5, -0.5))
    for k_, lab in zip((-2, -1, 0, 1), ("0.01", "0.1", "1", "10")):
        Xv = float(q.px(k_))
        f.line(Xv, TOP, Xv, TOP + RH, color=GRID_C)
        f.line(Xv, TOP + RH, Xv, TOP + RH + 3, color=MUTED)
        f.text(Xv, TOP + RH + 12, lab, size=TICK_PT, anchor="middle", color=MUTED)
    for i, d in enumerate(dets):
        cpm = b[d]["calls_per_min"]
        Y = float(q.py(i))
        xv = float(q.px(math.log10(max(cpm, 0.01))))
        f.rect(X2, Y - 5, xv - X2, 10, fill=COLORS[d])
        f.text(xv + 4, Y + 3, f"{cpm:.2f}" if cpm >= 0.01 else "under 0.01", size=PRINT_MIN_PT, color=INK_T)
    f.text(X2 + PW2 / 2, TOP + RH + 25, "per minute", size=LABEL_PT, anchor="middle", color=MUTED, italic=True)
    f.text(X2 + PW2 / 2, TOP + RH + 36, "(each step is ten times more)", size=PRINT_MIN_PT, anchor="middle",
           color=MUTED, italic=True)
    ky = TOP + RH + 56
    kx = 76
    for glyph, col, lab in (("●", INK_T, "outside the busy stretch"), ("●", "#d9730d", "inside it"),
                            ("|", "#999", "what calling at random would find inside")):
        f.text(kx, ky, glyph, size=LABEL_PT, weight=700, color=col)
        f.text(kx + 9, ky, lab, size=TICK_PT, color=MUTED)
        kx += 9 + 3.9 * len(lab) + 16
    f.h = ky + 8
    return f


def fig_real_overview(W, label, stream):
    """Figures 21-24, four real recordings per drug per kind of event, one from each group of mice.

    For print the program names go once, in a key across the top, and each call row carries only its
    count, in the program's colour: a name on every row of every recording needed ~90 pt of margin and
    9 pt rows, which made the figure too tall to share a Word page with its caption."""
    from make_plain_detector_review import (CODED, COLORS, GROUP_WORDS_PLAIN, INK_T, NAMES, PERIOD_COLORS,
                                            _plural)
    from svgfig import MUTED, Figure
    ov = {k: v for k, v in W["real"]["overview"].items() if v["label"] == label and v["stream"] == stream}
    order = [k for g in ("DI", "MALE", "ORX", "OVX") for k in ov if ov[k]["group"] == g]
    lo = min(ov[k]["ext"][0] - ov[k]["anchor"] for k in order)
    hi = max(ov[k]["ext"][1] - ov[k]["anchor"] for k in order)
    span = (lo - 30, hi + 30)
    L, PW = 26, PAGE_W - 26 - 6
    ROW = 7
    f = Figure(PAGE_W, 700)
    # the key: which colour is which program
    kx, y = L, 9
    f.text(0, y, "calls:", size=PRINT_MIN_PT, color=MUTED)
    for d in CODED:
        f.text(kx, y, "▬", size=LABEL_PT, weight=700, color=COLORS[d])
        f.text(kx + 11, y, NAMES[d], size=TICK_PT, color=INK_T)
        kx += 11 + 4.2 * len(NAMES[d]) + 14
    y = 26
    for k in order:
        c = ov[k]
        f.text(L, y, c["group"], size=LABEL_PT, weight=700)
        f.text(L + 6.0 * len(c["group"]) + 3, y, f"· {GROUP_WORDS_PLAIN.get(c['group'], '')} · "
                                                 f"{_plural(c['n_roi'], 'neuron')}", size=TICK_PT, color=MUTED)
        pl = f.panel(L, y + 3, PW, 10, span, (0, 1), frame=False)
        for name, r0, r1 in c["regions"]:
            pl.span(r0 - c["anchor"], r1 - c["anchor"], row_y=y + 4, row_h=5, color=PERIOD_COLORS.get(name, "#9e9e9e"))
        for w0, w1 in c["windows"]:
            pl.span(w0 - c["anchor"], w1 - c["anchor"], row_y=y + 10.5, row_h=2.5, color="#333")
        yy = y + 15
        lp = f.panel(L, yy, PW, len(CODED) * ROW + 3, span, (0, 1))
        for i, d in enumerate(CODED):
            ry = yy + 2 + i * ROW
            for on, wd in c["calls"][d]:
                lp.span(on - c["anchor"], on + wd - c["anchor"], row_y=ry, row_h=5, color=COLORS[d], min_px=1.5)
            f.text(L - 4, ry + 5.5, f"{c['in_window'][d]:,}", size=PRINT_MIN_PT, anchor="end", weight=700,
                   color=COLORS[d])
        yy += len(CODED) * ROW + 6
        rh = float(np.clip(1.3 * c["n_roi"], 36, 56))
        r = f.panel(L, yy, PW, rh, span, (0, 1))
        r.raster([np.asarray(v, float) - c["anchor"] for v in c["trains"]], width=0.7)
        y = yy + rh + 16
        if k == order[-1]:
            _time_axis(f, r, offset=0.0, step=600.0 if (span[1] - span[0]) > 2400 else 300.0,
                       label=f"minutes from the moment {label} arrives")
            y += 22
    for line in ((("#bcc3cc", "before the drug"), (PERIOD_COLORS.get(label, "#9e9e9e"), label),
                  ("#7d7d7d", "high potassium"), ("#333", "the stretches the lab studies")),):
        kx = L
        for col, lab in line:
            f.text(kx, y, "▬", size=LABEL_PT, weight=700, color=col)
            f.text(kx + 11, y, lab, size=TICK_PT, color=MUTED)
            kx += 11 + 4.2 * len(lab) + 14
    f.text(L, y + 12, "The number at the left of each row of calls is that program's calls inside the stretches "
                      "the lab studies.", size=TICK_PT, color=MUTED)
    f.h = y + 18
    return f


def fig_eye(W):
    """Figure 25, close-ups of real recordings (A-C) and the tallies over every real recording (D)."""
    from make_plain_detector_review import CODED, COLORS, INK_T, MIN_CELLS, NAMES, PERIOD_COLORS
    from svgfig import MUTED, Figure
    R = W["real"]
    C = R["close"]
    dets = list(CODED)
    f = Figure(PAGE_W, 900)
    X, PW = 96, PAGE_W - 96 - 12
    y = 10
    for key, title, weak in (("outside", "A · clear stripes just outside the analysis window (black line)", False),
                             ("busy", "B · a busy stretch inside the analysis window, no stripe that stands out",
                              False),
                             ("weak", "C · calls with no stripe under them (red box: a coordinated event of "
                                      "3 or fewer neurons)", True)):
        f.text(0, y, title, size=TITLE_PT, weight=600)
        # raster 36, not 50: at 50 the figure was 721 pt, taller than the Word page
        y = _closeup(f, C[key], X, y + 2, PW, title="", dets=dets, raster_h=36, tick_step=None, show_weak=weak,
                     ROW=9)
    # D: the tallies
    T = R["tally"]
    f.text(0, y, f"D · all {R['n_recordings']} real recordings of the previous four figures, both kinds of events",
           size=TITLE_PT, weight=600)
    PX, PPW, QX, QPW = 74, 150, 300, 108
    f.text(PX, y + 13, f"share of the {R['n_in']} clear stripes inside", size=PRINT_MIN_PT, color=MUTED)
    f.text(PX, y + 23, "the windows it called", size=PRINT_MIN_PT, color=MUTED)
    f.text(QX, y + 13, "share of its calls on coordinated", size=PRINT_MIN_PT, color=MUTED)
    f.text(QX, y + 23, "events of 3 or fewer neurons", size=PRINT_MIN_PT, color=MUTED)
    ty, RH = y + 30, 10 * len(dets)
    p = f.panel(PX, ty, PPW, RH, (0, 1), (len(dets) - 0.5, -0.5))
    q = f.panel(QX, ty, QPW, RH, (0, 1), (len(dets) - 0.5, -0.5))
    for i, d in enumerate(dets):
        t = T[d]
        Y = float(p.py(i))
        v1 = t["called_in"] / max(t["stripes_in"], 1)
        v2 = t["weak"] / max(t["calls"], 1)
        f.rect(PX, Y - 3.5, float(p.px(v1)) - PX, 7, fill=COLORS[d])
        f.text(float(p.px(v1)) + 3, Y + 3, f"{v1:.0%}", size=PRINT_MIN_PT)
        f.rect(QX, Y - 3.5, float(q.px(v2)) - QX, 7, fill=COLORS[d])
        f.text(float(q.px(v2)) + 3, Y + 3, f"{v2:.0%} of {t['calls']:,}", size=PRINT_MIN_PT)
        f.text(PX - 6, Y + 3, NAMES[d], size=TICK_PT, anchor="end", color=INK_T)
    for pan, x0, w in ((p, PX, PPW), (q, QX, QPW)):
        for v in (0, 0.5, 1):
            Xv = float(pan.px(v))
            f.line(Xv, ty + RH, Xv, ty + RH + 3, color=MUTED)
            f.text(Xv, ty + RH + 12, f"{v:.0%}", size=PRINT_MIN_PT, anchor="middle", color=MUTED)
    y2 = ty + RH + 25
    f.text(0, y2, "▼", size=LABEL_PT, weight=700, color=INK_T)
    f.text(10, y2, f"a clear stripe: at least {R['stripe_frac']:.0%} of the neurons (and at least {MIN_CELLS}) start "
                   f"an event within {R['stripe_s']:g} second, and at least twice", size=PRINT_MIN_PT, color=MUTED)
    f.text(10, y2 + 10, "as many as in the busiest seconds around it", size=PRINT_MIN_PT, color=MUTED)
    kx = 0
    for col, lab in (("#333", "the analysis windows the lab marks"), (PERIOD_COLORS["baseline"], "baseline"),
                     (PERIOD_COLORS["senktide"], "senktide"), (PERIOD_COLORS["TTX"], "TTX"),
                     (PERIOD_COLORS["high K+"], "high potassium")):
        f.text(kx, y2 + 23, "▬", size=LABEL_PT, weight=700, color=col)
        f.text(kx + 11, y2 + 23, lab, size=PRINT_MIN_PT, color=MUTED)
        kx += 11 + 3.9 * len(lab) + 12
    f.h = y2 + 29
    return f


def _key(f, x, y, items, *, gap=14, size=TICK_PT):
    """One legend row: (glyph, colour, words) items, left to right; returns the x after the last."""
    from svgfig import MUTED
    for glyph, col, lab in items:
        f.text(x, y, glyph, size=LABEL_PT, weight=700, color=col)
        gw = 12 if len(glyph) == 1 else 16
        f.text(x + gw, y, lab, size=size, color=MUTED)
        x += gw + 3.9 * len(lab) + gap
    return x


def _xticks(f, p, ticks, fmt="{:g}", *, label=None, size=TICK_PT):
    from svgfig import MUTED
    for v in ticks:
        Xv = float(p.px(v))
        f.line(Xv, p.y + p.h, Xv, p.y + p.h + 3, color=MUTED)
        f.text(Xv, p.y + p.h + 12, v if isinstance(v, str) else fmt.format(v), size=size, anchor="middle",
               color=MUTED)
    if label:
        f.text(p.x + p.w / 2, p.y + p.h + 24, label, size=LABEL_PT, anchor="middle", color=MUTED, italic=True)


def _yticks(f, p, ticks, fmt="{:g}", *, grid=True, size=TICK_PT):
    from svgfig import MUTED
    for v in ticks:
        Yv = float(p.py(v))
        if grid:
            f.line(p.x, Yv, p.x + p.w, Yv, color="#e6e6e6")
        f.line(p.x - 3, Yv, p.x, Yv, color=MUTED)
        f.text(p.x - 5, Yv + 3, fmt.format(v), size=size, anchor="end", color=MUTED)


def fig_count_rule(W):
    """Figure 4, how the interval rule decides: steps across the top, a planted event (A) and a busy
    stretch (B) below."""
    from make_plain_detector_review import (BARC, COUNT_C, GREEN, INK_T, RED, _arr, _by_activity, _clock,
                                            _found, _plural)
    from svgfig import MUTED, Figure, nice_ticks
    sim, C = W["sim"], W["count"]
    bw = C["fig_w"]
    x = C["one_bar"][f"interval|{bw:g}"]
    ev = sim["event"]
    f = Figure(PAGE_W, 700)
    f.text(0, 11, "How the interval rule decides", size=TITLE_PT + 1, weight=700)
    y = 28
    for i, s in enumerate((f"Slide a window {bw:g} seconds long along the recording.",
                           "Wherever it sits, count how many different neurons have an event inside it.",
                           f"Wherever that count reaches {x} neurons, call a coordinated event. Windows "
                           "that overlap make one call.",
                           "It never asks what chance would produce. The bar is the same number in every "
                           "recording.")):
        f.add(f"<circle cx='7' cy='{y - 3:.1f}' r='6' fill='{COUNT_C}'/>")
        f.text(7, y, str(i + 1), size=PRINT_MIN_PT, anchor="middle", weight=700, color="#fff")
        y = f.para(18, y, s, width_chars=112, size=LABEL_PT, lh=1.3) + 4
    y0 = y + 14
    L, VW, GAP = 52, 186, 30
    ymax = int(max(10, x + 3, *[np.nanmax(_arr(C["demo"][k_]["y"])) + 1 for k_ in ("A", "B")]))
    ymax += ymax % 2
    for j, (key, title) in enumerate((("A", "A · a planted event (quiet neurons)"),
                                      ("B", "B · a busy stretch, nothing planted"))):
        D, K = sim[key], C["demo"][key]
        X = L + j * (VW + GAP)
        win = D["win"]
        f.text(X, y0, title, size=TITLE_PT, weight=600)
        f.text(X, y0 + 11, f"one minute, from {_clock(win[0])} into the recording", size=PRINT_MIN_PT, color=MUTED)
        ly = y0 + 16
        lane = f.panel(X, ly, VW, 26, win, (0, 1))
        if key == "A":
            lane.down_triangle(ev["time"], ly + 8, color=GREEN if _found(K["calls"], ev["time"]) else RED, size=8)
        for on, wd in K["calls"]:
            lane.span(on, on + max(wd, 0.0), row_y=ly + 15, row_h=8, color=COUNT_C, min_px=2)
        n_calls = sum(1 for on, wd in K["calls"] if on + wd >= win[0] and on <= win[1])
        f.text(X + VW - 3, ly + 9, _plural(n_calls, "call"), size=PRINT_MIN_PT, anchor="end", color=MUTED)
        ry = ly + 30
        r = f.panel(X, ry, VW, 80, win, (0, 1))
        r.raster(_by_activity(D["trains"]), width=0.8)
        my = ry + 80 + 8 + 26
        p = f.panel(X, my + 6, VW, 84, win, (0, ymax))
        _yticks(f, p, nice_ticks(0, ymax, 4))
        p.steps(_arr(K["t"]), _arr(K["y"]), color=COUNT_C, width=1.1)
        p.hline(x, color=BARC, width=1.3, dash="4 3")
        if j == 0:
            r.ylabel(f"{sim['n_roi']} neurons", size=LABEL_PT, dx=12)
            f.text(X - 5, ly + 11, "planted", size=PRINT_MIN_PT, anchor="end", color=MUTED)
            f.text(X - 5, ly + 22, "calls", size=PRINT_MIN_PT, anchor="end", color=MUTED)
            p.ylabel("neurons", lines=["different neurons", f"in the next {bw:g} s"], size=PRINT_MIN_PT, dx=34)
        _time_axis(f, p, offset=win[0], step=15.0, label="seconds from the start of this minute")
    _key(f, L, my - 12, [("▬", COUNT_C, f"different neurons in the {bw:g} s window starting here")])
    _key(f, L, my, [("- -", BARC, f"the bar: {x} neurons, in every recording")])
    by = my + 6 + 84 + 42
    _key(f, L, by, [("▼", GREEN, "planted event, found"), ("▼", RED, "planted event, missed")])
    f.h = by + 8
    return f


def fig_count_edge(W):
    """Figure 5, what a fixed bin edge costs: share of planted events found, by where they fall on the grid."""
    from make_plain_detector_review import COLORS, COUNT_C
    from svgfig import MUTED, Figure
    C = W["count"]
    E = C["edge"]
    x = C["x_edge"]
    bw = C["edge_bin"]
    lines = (("interval", COUNT_C, f"counting within a sliding {bw:g} s window, bar of {x} neurons", "", 1.8),
             ("bin", "#b59a6a", f"counting in fixed {bw:g} s bins, the same bar", "4 3", 1.8),
             ("coact", COLORS["coact"], f"CoactDetect (fixed {bw:g} s bins)", "", 1.3),
             ("loco", COLORS["loco"], "LoCo (fixed 1 s bins)", "", 1.3))
    f = Figure(PAGE_W, 400)
    f.text(0, 11, "Events joined by 6 neurons: the share found, by where each fell against the bins",
           size=TITLE_PT, weight=600)
    X, Y, PW, PH = 52, 24, 400, 170
    p = f.panel(X, Y, PW, PH, (0, 0.5), (0, 1.05))
    _yticks(f, p, [0, 0.25, 0.5, 0.75, 1.0], "{:.0%}")
    p.ylabel("share found", size=LABEL_PT, dx=38)
    for key, col, _, dash, wdt in lines:
        xs = [(g["lo"] + g["hi"]) / 2 for g in E[key]]
        ys = [g["found"] for g in E[key]]
        p.curve(xs, ys, color=col, width=wdt, dash=dash or None)
        p.dots(xs, ys, color=col, r=2.4)
    _xticks(f, p, [0, 0.125, 0.25, 0.375, 0.5],
            label="distance from the nearest bin edge, as a share of the bin (0.5 = the middle)")
    ly = Y + PH + 42
    for i, (key, col, lab, dash, _) in enumerate(lines):
        _key(f, X + (i % 2) * 214, ly + (i // 2) * 12, [("▬", col, lab)], size=PRINT_MIN_PT)
    ns = ", ".join(str(g["n"]) for g in E["bin"])
    f.text(X, ly + 28, f"{C['n_edge_events']} planted events, both backgrounds; {ns} in the four groups, "
                       "left to right", size=PRINT_MIN_PT, color=MUTED)
    f.h = ly + 34
    return f


def fig_count_slices(W):
    """Figure 6, one dot per untreated real recording: the bar its own chance needs."""
    import math

    from make_plain_detector_review import BARC, BUSY_C, INK_T
    from svgfig import MUTED, Figure
    C = W["count"]
    bw = C["fig_w"]
    x1 = C["one_bar"][f"interval|{bw:g}"]
    R = C["real"]
    top = max([r[f"need|{bw:g}"] or 0 for r in R] + [x1]) + 1
    f = Figure(PAGE_W, 400)
    X, Y, PW, PH = 70, 32, 288, 190
    f.text(0, 11, f"{len(R)} untreated recordings, one dot each", size=TITLE_PT, weight=600)
    p = f.panel(X, Y, PW, PH, (-2.5, 1.0), (0, top))
    _yticks(f, p, list(range(0, top + 1, 2)))
    p.ylabel("neurons", lines=[f"neurons needed within {bw:g} s so that", "chance reaches it less than once",
                               "every 10 minutes"], size=PRINT_MIN_PT, dx=48)
    rate_q = C["block_rate_per_min"]["baseline_quiet"]
    Xb = float(p.px(math.log10(rate_q)))
    f.line(Xb, Y, Xb, Y + PH, color=MUTED, width=0.8, dash="2 2")
    f.text(Xb, Y - 4, "the simulated busy stretch", size=PRINT_MIN_PT, anchor="middle", color=MUTED)
    for r in R:
        need = r[f"need|{bw:g}"]
        if need is None or r["rate"] <= 0:
            continue
        p.dots([math.log10(r["rate"])], [need], color=BUSY_C if need > x1 else "#7a7a7a", r=2.8, opacity=0.75)
    p.hline(x1, color=BARC, width=1.2, dash="4 3")
    for i, ln in enumerate(("the one bar that did", "best on simulated", f"recordings: {x1} neurons")):
        f.text(X + PW + 6, float(p.py(x1)) - 8 + 10 * i, ln, size=TICK_PT, color=INK_T)
    # log ticks, labelled with the rate itself rather than its exponent
    for v, lab in ((-2, "0.01"), (-1, "0.1"), (0, "1"), (1, "10")):
        Xv = float(p.px(v))
        f.line(Xv, Y + PH, Xv, Y + PH + 3, color=MUTED)
        f.text(Xv, Y + PH + 12, lab, size=TICK_PT, anchor="middle", color=MUTED)
    f.text(X + PW / 2, Y + PH + 24, "events per neuron per minute (each step is ten times more)", size=LABEL_PT,
           anchor="middle", color=MUTED, italic=True)
    ky = Y + PH + 42
    _key(f, X, ky, [("●", BUSY_C, f"a bar of {x1} lets chance through"),
                    ("●", "#7a7a7a", f"a bar of {x1} is enough, or more than enough")])
    f.h = ky + 8
    return f


def fig_count_published(W):
    """Figure 7, the published slice rule run on neurons that fire at random and independently."""
    from make_plain_detector_review import PUB_CELLS, RED
    from svgfig import MUTED, Figure
    P = W["count"]["published"]
    e = P["eddleston"]
    shades = {"7": "#c9b79c", "13.4": "#5a4527"}
    words = {"7": "7 events per neuron per hour, the slowest reported (Han and others, 2023)",
             "13.4": "13.4 events per neuron per hour, the rate in Eddleston and others (2026)"}
    f = Figure(PAGE_W, 400)
    TOP, PH = 22, 170
    for j, (key, title, ylim, ticks, ylab, rep) in enumerate((
            ("mse_per_cell_h", "A · mSEs per neuron per hour", (0, 4), [0, 1, 2, 3, 4],
             "mSEs per neuron per hour", e["mse"]),
            ("cells_per", "B · neurons in each mSE", (2, 4.5), [2, 3, 4], "neurons in each mSE",
             e["cells_per"]))):
        X, PW = (40, 150) if j == 0 else (292, 120)
        f.text(X - 30, 11, title, size=TITLE_PT, weight=600)
        p = f.panel(X, TOP, PW, PH, (PUB_CELLS[0], PUB_CELLS[-1]), ylim)
        f.rect(float(p.px(e["field_lo"])), TOP, float(p.px(e["field_hi"])) - float(p.px(e["field_lo"])), PH,
               fill="#f1ede6")
        _yticks(f, p, ticks)
        p.ylabel(ylab, size=PRINT_MIN_PT, dx=20)
        for rate, rows in P["curves"].items():
            p.curve([r_["cells"] for r_ in rows], [r_[key] for r_ in rows], color=shades.get(rate, MUTED),
                    width=1.5)
        p.hline(rep, color=RED, width=1.2, dash="4 3", x0=e["field_lo"], x1=e["field_hi"])
        for i_, ln in enumerate(("reported by", "Eddleston and", "others, 2026")):
            f.text(X + PW + 4, float(p.py(rep)) - 7 + 10 * i_, ln, size=PRINT_MIN_PT, color=RED)
        _xticks(f, p, [5, 10, 15, 20, 25, 30], label="total number of neurons")
    ky = TOP + PH + 42
    for i, rate in enumerate(P["curves"]):
        _key(f, 10, ky + 11 * i, [("▬", shades.get(rate, MUTED),
                                   words.get(rate, f"{float(rate):g} events per neuron per hour"))])
    ky += 11 * len(P["curves"])
    _key(f, 10, ky, [("▮", "#e2dbcf", f"{e['field_lo']} to {e['field_hi']} neurons, as Eddleston and others "
                                      "(2026) report"), ("- -", RED, "the averages they report")])
    f.h = ky + 8
    return f


def fig_chance_steps(W):
    """Figure 8, the four steps of a shifted-copy test, on six simulated neurons with numbered events.
    Print layout: steps 1 and 3 side by side, step 2's three copies across the full width, step 4 below."""
    from make_plain_detector_review import BARC, GREEN, INK_T, _numbered, _plural
    from svgfig import MUTED, Figure, nice_ticks
    S = W["toys"]["steps"]
    L, bin_ = S["length"], tuple(S["bin"])
    BLUE = "#9bb7d4"
    f = Figure(PAGE_W, 600)

    def badge(x, y, n, title):
        f.add(f"<circle cx='{x + 6}' cy='{y - 3.5:.1f}' r='6.5' fill='#333'/>")
        f.text(x + 6, y, n, size=PRINT_MIN_PT, anchor="middle", weight=700, color="#fff")
        f.text(x + 17, y, title, size=TITLE_PT, weight=600)

    # step 1
    X1, W1 = 14, 200
    badge(X1 - 6, 11, "1", "Count the recording")
    f.para(X1, 25, f"How many neurons have an event inside the 2-second bin being tested? Here: {S['observed']} "
                   "of 6.", width_chars=46, size=TICK_PT, color=MUTED, lh=1.25)
    lane = f.panel(X1, 44, W1, 8, (0, L), (0, 1), frame=False)
    lane.span(*bin_, row_y=45, row_h=6, color=BLUE, min_px=4)
    r = f.panel(X1, 54, W1, 96, (0, L), (0, 1))
    _numbered(f, r, S["numbered"], size=8, bold_in=bin_)
    _xticks(f, r, [0, L / 2, L], fmt="{:g}s")
    f.para(X1, 175, "Six neurons, one row each. Each event carries its number in that neuron's own order, so a "
                    "row can be followed when it slides. Blue bar: the bin tested.", width_chars=46,
           size=PRINT_MIN_PT, color=MUTED, lh=1.25)
    # step 3
    X3, W3 = 290, 160
    badge(X3 - 40, 11, "3", f"Repeat {S['n_copies']} times")
    f.text(X3 - 34, 25, "The counts from the copies are what chance gives.", size=TICK_PT, color=MUTED)
    hist = np.asarray(S["hist"], float)
    ymax = max(10.0, hist.max() * 1.15)
    h = f.panel(X3, 54, W3, 96, (-0.6, 6.6), (0, ymax))
    h.bars(np.arange(7), hist, color="#b9c6d6", width_frac=0.85)
    _yticks(f, h, nice_ticks(0, ymax, 4), "{:,.0f}", grid=False)
    h.ylabel("copies", lines=[f"copies (of {S['n_copies']})"], size=PRINT_MIN_PT, dx=26)
    _xticks(f, h, [0, 2, 4, 6], label="neurons in the bin")
    Xb = float(h.px(S["bar"]))
    f.line(Xb, 54, Xb, 150, color=BARC, width=1.4, dash="4 3")
    f.text(Xb + 4, 64, "the bar", size=TICK_PT, weight=600)
    h.down_triangle(S["observed"], 50, color=GREEN, size=8)
    # step 2
    y2 = 222
    badge(X1 - 6, y2, "2", "Make a shifted copy")
    f.text(X1 + 118, y2, "Slide each neuron's row by its own random amount. Events pushed off", size=TICK_PT,
           color=MUTED)
    f.text(X1 + 118, y2 + 11, "the end come back at the start. Count again.", size=TICK_PT, color=MUTED)
    CW, cy = 112, y2 + 24
    for i, ex in enumerate(S["examples"]):
        X = 44 + i * (CW + 42)
        ln = f.panel(X, cy, CW, 8, (0, L), (0, 1), frame=False)
        ln.span(*bin_, row_y=cy + 1, row_h=6, color=BLUE, min_px=4)
        rr = f.panel(X, cy + 10, CW, 84, (0, L), (0, 1))
        _numbered(f, rr, ex["numbered"], size=8, bold_in=bin_)
        n_ = len(ex["shifts"])
        for j, sh in enumerate(ex["shifts"]):
            ry_ = cy + 10 + 84 - (j + 0.5) * (84 / n_) + 3
            f.text(X - 3, ry_, f"+{sh:g}s", size=PRINT_MIN_PT, anchor="end", color="#8a8a8a")
        f.text(X, cy + 106, f"copy {i + 1}:", size=TICK_PT, color=MUTED)
        f.text(X + 34, cy + 106, _plural(ex["count"], "neuron"), size=TICK_PT, weight=700, color=INK_T)
    f.text(14, cy + 118, "grey: the slide given to each row", size=PRINT_MIN_PT, color="#8a8a8a")
    # step 4
    y4 = cy + 140
    badge(X1 - 6, y4, "4", "Decide")
    share = f"{S['share_at_least'] * 100:.0f}%" if S["share_at_least"] >= 0.01 else "under 1%"
    f.text(X1 + 50, y4, f"Only {share} of the copies reach {S['observed']} neurons, so the real moment",
           size=TICK_PT, color=MUTED)
    f.text(X1 + 50, y4 + 11, "(green ▼ in step 3) is called a coordinated event.", size=TICK_PT, color=MUTED)
    f.h = y4 + 17
    return f


def fig_shift_shuffle(W):
    """Figure 9, shifted copies against shuffled copies: bursty neurons (A), a steady beat (B), and the lab's
    own recordings (C)."""
    import math

    from make_plain_detector_review import GREEN, INK_T, RED, SHIFT_C, SHUF_C, _plural
    from svgfig import MUTED, Figure
    T = W["toys"]
    numbers = W["_numbers"]
    f = Figure(PAGE_W, 700)
    rows = [("bursty", "A · neurons with events in bursts",
             "A shuffle breaks the bursts apart, so events spread over more of the recording and more neurons land "
             "in any bin by chance. The bar comes out too high and the burst that was put in is missed."),
            ("even", "B · neurons with events at a steady beat",
             "A shuffle lets a neuron's events pile up in one bin and leave others empty, so fewer neurons reach any "
             "bin by chance. The bar comes out too low and a coordinated event that is only chance is called.")]
    Y = 11
    for key, title, story in rows:
        D = T[key]
        b = D["bin"]
        f.text(0, Y, title, size=TITLE_PT, weight=600)
        yy = f.para(0, Y + 12, story, width_chars=116, size=TICK_PT, color=MUTED, lh=1.25)
        py = yy + 14
        for j, (lab, trs, col) in enumerate((("the recording", D["trains"], INK_T),
                                             ("one shifted copy", D["shift_example"], SHIFT_C),
                                             ("one shuffled copy", D["shuffle_example"], SHUF_C))):
            # 74 wide with 18 between: at 80 and 12 one raster's "20s" ran into the next one's "0s"
            X = 8 + j * 96
            f.text(X, py, lab, size=TICK_PT, weight=600, color=col)
            ln = f.panel(X, py + 4, 76, 6, (0, T["length"]), (0, 1), frame=False)
            ln.span(*b, row_y=py + 4, row_h=5, color="#9bb7d4")
            r = f.panel(X, py + 11, 76, 64, (0, T["length"]), (0, 1))
            r.raster(trs, width=1.0)
            _xticks(f, r, [0, 10, 20], "{:g}s", size=PRINT_MIN_PT)
            cnt = sum(1 for v in trs if np.any((np.asarray(v) >= b[0]) & (np.asarray(v) < b[1])))
            f.text(X + 76, py + 11 + 64 + 23, f"{_plural(cnt, 'neuron')} in the bin", size=PRINT_MIN_PT,
                   anchor="end", color=MUTED)
        for j, (lab, hist, col, pv) in enumerate((("5,000 shifted", D["shift_hist"], SHIFT_C, D["p_shift"]),
                                                  ("5,000 shuffled", D["shuffle_hist"], SHUF_C, D["p_shuffle"]))):
            X = 320 + j * 80
            h = f.panel(X, py + 11, 62, 64, (-0.6, 6.6), (0, 2500))
            h.bars(np.arange(7), hist, color=col, width_frac=0.8)
            _xticks(f, h, [0, 2, 4, 6], size=PRINT_MIN_PT)
            if j == 0:
                _yticks(f, h, [0, 1000, 2000], "{:,.0f}", grid=False, size=PRINT_MIN_PT)
                h.ylabel("copies", size=PRINT_MIN_PT, dx=30)
            h.down_triangle(D["observed"], py + 9, color=INK_T, size=6)
            f.text(X + 31, py - 8, lab, size=TICK_PT, anchor="middle", weight=600, color=col)
            f.text(X + 31, py + 1, "copies", size=TICK_PT, anchor="middle", weight=600, color=col)
            share = f"{pv * 100:.1f}%" if pv >= 0.001 else "under 0.1%"
            verdict = "called" if pv < 0.05 else "not called"
            by = py + 11 + 64 + 23
            f.text(X + 31, by, f"with {D['observed']} or more", size=PRINT_MIN_PT, anchor="middle", color=MUTED)
            f.text(X + 31, by + 9, f"neurons: {share}", size=PRINT_MIN_PT, anchor="middle", color=MUTED)
            f.text(X + 31, by + 19, f"→ {verdict}", size=TICK_PT, anchor="middle", weight=700,
                   color=GREEN if (verdict == "called") == (key == "bursty") else RED)
        Y = py + 11 + 64 + 23 + 36
    f.text(PAGE_W, Y - 4, "histograms: across, neurons in the bin · ▼ what the recording itself gave · a count "
                          "that fewer than 5 copies in 100 reach is called", size=PRINT_MIN_PT, anchor="end",
           color=MUTED, italic=True)
    # C: the lab's own recordings
    Y += 16
    f.text(0, Y, "C · on the lab's own recordings (84 untreated recordings, brief events)", size=TITLE_PT, weight=600)
    d = numbers["sur_fast_doubles"]
    n6 = numbers["sur_fast_n6"]
    groups = [(("events landing in a 2-second bin their own", "neuron already filled, per 1,000 events"),
               [math.floor(v + 0.5) for v in (d["real"], d["shift"], d["shuffle"])], "{:.0f}", 120, 0),
              (("share of 2-second bins where 6 or more", "neurons have an event"),
               [100 * n6["real"], 100 * n6["shift"], 100 * n6["shuffle"]], "{:.2f}%", 2.0, 240)]
    for (l1, l2), vals, fmt, vmax, X in groups:
        f.text(X, Y + 13, l1, size=TICK_PT, color=MUTED)
        f.text(X, Y + 23, l2, size=TICK_PT, color=MUTED)
        for i, (nm, v, col) in enumerate((("recording", vals[0], INK_T), ("shifted", vals[1], SHIFT_C),
                                          ("shuffled", vals[2], SHUF_C))):
            yy = Y + 30 + i * 13
            f.text(X + 46, yy + 8, nm, size=TICK_PT, anchor="end", color=col, weight=600)
            wbar = 150 * v / vmax
            f.rect(X + 50, yy, wbar, 9, fill=col)
            f.text(X + 54 + wbar, yy + 8, fmt.format(v), size=TICK_PT, color=INK_T)
    f.h = Y + 30 + 3 * 13 + 4
    return f


def fig_simulator(W):
    """Figure 16, one simulated recording: planted events, decoys, the busy stretch, and the raster."""
    from svgfig import MUTED, Figure
    sim = W["sim"]
    bench = W["_numbers"]["bench"]
    ext = sim["ext"]
    f = Figure(PAGE_W, 400)
    L, PW = 58, PAGE_W - 58 - 8
    lane = f.panel(L, 4, PW, 38, ext, (0, 1))
    sizes = {max(bench["participation_pct"]): "#08306b", sorted(bench["participation_pct"])[1]: "#2171b5",
             min(bench["participation_pct"]): "#6baed6"}
    for t, k in sim["planted"]:
        pct = min(sizes, key=lambda p_: abs(p_ - 100 * k / sim["n_roi"]))
        lane.down_triangle(t, 12, color=sizes[pct], size=7)
    for t, k in sim["decoys"]:
        lane.down_triangle(t, 24, color="#555", size=6.5, hollow=True)
    h0, h1 = sim["hot"]
    lane.span(h0, h1, row_y=32, row_h=7, color="#f0c9a0")
    f.text(L - 5, 14, "planted", size=TICK_PT, anchor="end", color=MUTED)
    f.text(L - 5, 26, "decoys", size=TICK_PT, anchor="end", color=MUTED)
    f.text(L - 5, 38, "busy stretch", size=TICK_PT, anchor="end", color=MUTED)
    r = f.panel(L, 46, PW, 170, ext, (0, 1))
    order = np.argsort([len(v) for v in sim["full_trains"]], kind="stable")
    r.raster([sim["full_trains"][i] for i in order], width=0.6)
    r.ylabel(f"{sim['n_roi']} neurons", size=LABEL_PT, dx=10)
    span_s = ext[1] - ext[0]
    _time_axis(f, r, offset=ext[0], step=300.0 if span_s > 1800 else 120.0, label="time in the recording")
    ky = 46 + 170 + 42
    items = []
    for pct, col in sorted(sizes.items(), reverse=True):
        note = {18: ", the usual real size"}.get(pct, "")
        items.append(("▼", col, f"planted event, {round(pct / 100 * sim['n_roi'])} neurons{note}"))
    _key(f, L, ky, items[:2])
    _key(f, L, ky + 11, items[2:] + [("▽", "#555", "decoy: built the same way, not counted")])
    _key(f, L, ky + 22, [("▬", "#f0c9a0", "busy stretch: every neuron gets extra random events, nothing planted")])
    f.h = ky + 28
    return f


def fig_grading(W):
    """Figure 17, how calls are graded against planted events, on a made-up minute."""
    from make_plain_detector_review import GREEN, RED
    from svgfig import MUTED, Figure
    tol = W["_numbers"]["tol_s"]
    f = Figure(PAGE_W, 200)
    L, PW, win = 76, PAGE_W - 76 - 8, (0, 60)
    planted = [8, 27, 50]
    calls = [(7.2, 1.5), (26.0, 0.8), (27.9, 0.6), (40.0, 1.0)]
    lane = f.panel(L, 4, PW, 76, win, (0, 1))
    for t in planted:
        lane.span(t - tol, t + tol, row_y=6, row_h=16, color="#dff0e3")
    for t, ok in zip(planted, (True, True, False)):
        lane.down_triangle(t, 14, color=GREEN if ok else RED, size=8)
    labels = [("hit",), ("hit",), ("false alarm: a second", "call on the same event"),
              ("false alarm:", "nothing planted here")]
    for (on, wd), lab, row in zip(calls, labels, (0, 0, 1, 0)):
        yy = 30 + row * 24
        col = GREEN if lab[0] == "hit" else RED
        lane.span(on, on + wd, row_y=yy, row_h=9, color=col)
        for i, ln in enumerate(lab):
            f.text(float(lane.px(on + wd)) + 4, yy + 8 + 9 * i, ln, size=TICK_PT, color=col)
    # two lines: on one it ran back into the second planted event's band
    f.text(float(lane.px(50 - tol)) - 4, 13, "miss: no call near", size=TICK_PT, color=RED, anchor="end")
    f.text(float(lane.px(50 - tol)) - 4, 22, "this planted event", size=TICK_PT, color=RED, anchor="end")
    f.text(L - 5, 17, "planted events", size=TICK_PT, anchor="end", color=MUTED)
    f.text(L - 5, 40, "calls", size=TICK_PT, anchor="end", color=MUTED)
    _time_axis(f, lane, offset=0.0, step=10.0, label="a simulated minute, drawn to show the rule")
    y = f.para(0, 4 + 76 + 42, f"Green bands reach {tol:g} seconds either side of each planted event. A call that "
                               f"touches a band is a hit; each planted event counts only one call.",
               width_chars=108, size=TICK_PT, color=MUTED, lh=1.25)
    f.text(0, y, "Here: found 2 of 3 planted events; 2 of 4 calls were right.", size=TICK_PT, color=MUTED)
    f.h = y + 6
    return f


def fig_count_bar(W):
    """Figure 20, what the interval rule's bar does to the overall score (A) and to calls in the empty busy
    stretch (B)."""
    from make_plain_detector_review import BUSY_C, COLORS, QUIET_C
    from svgfig import MUTED, Figure
    C = W["count"]
    bw = C["fig_w"]
    rk = f"interval|{bw:g}"
    xs = C["xs"]
    B = C["bench"]
    regs = (("baseline_quiet", QUIET_C), ("baseline_busy", BUSY_C))
    f = Figure(PAGE_W, 400)
    TOP, PH = 30, 150
    cc = COLORS["coact"]
    for j, (key, t1, t2, ylim, ticks, ylab, scale) in enumerate((
            ("f1", "A · the overall score,", "bar by bar", (0, 1), [0, 0.25, 0.5, 0.75, 1.0], "overall score", 1),
            ("empty", "B · how much of the empty", "busy stretch it calls", (0, 100), [0, 25, 50, 75, 100],
             "percent of the stretch", 100))):
        X, PW = (44, 146) if j == 0 else (300, 112)
        f.text(X, 11, t1, size=TITLE_PT, weight=600)
        f.text(X, 23, t2, size=TITLE_PT, weight=600)
        p = f.panel(X, TOP, PW, PH, (xs[0] - 0.5, xs[-1] + 0.5), ylim)
        _yticks(f, p, ticks)
        p.ylabel(ylab, size=LABEL_PT, dx=32 if j == 0 else 28)
        for reg, col in regs:
            vals = [scale * np.nan_to_num(B[reg][f"{rk}|{x}"][key]) for x in xs]
            p.curve(xs, vals, color=col, width=1.4)
            p.dots(xs, vals, color=col, r=2.2)
            bx = C["best"][rk][reg]
            v = scale * np.nan_to_num(B[reg][f"{rk}|{bx}"][key])
            f.add(f"<circle cx='{float(p.px(bx)):.1f}' cy='{float(p.py(v)):.1f}' r='5' fill='none' "
                  f"stroke='{col}' stroke-width='1.2'/>")
        if key == "f1":
            for reg, word in (("baseline_quiet", "quiet"), ("baseline_busy", "busy")):
                v = B[reg]["coact"]["f1"]
                p.hline(v, color=cc, width=1.0, dash="3 3")
                f.text(X + PW + 4, float(p.py(v)) + 3, f"CoactDetect, {word}", size=PRINT_MIN_PT, color=cc)
        else:
            v = 100 * max(B["baseline_busy"]["coact"]["empty"], B["baseline_busy"]["loco"]["empty"])
            p.hline(v, color=cc, width=1.0, dash="3 3")
            f.text(X + PW + 4, float(p.py(v)) - 6, "CoactDetect", size=PRINT_MIN_PT, color=cc)
            f.text(X + PW + 4, float(p.py(v)) + 4, "and LoCo", size=PRINT_MIN_PT, color=cc)
        # every other bar labelled in the narrower panel: all of them ran together ("101112")
        _xticks(f, p, xs if j == 0 else [v for v in xs if v % 2 == 0],
                label=f"the bar: different neurons within {bw:g} s")
    ky = TOP + PH + 44
    _key(f, 44, ky, [("●", QUIET_C, "quiet background"), ("●", BUSY_C, "busy background"),
                     ("◯", MUTED, "the bar with the best score")])
    _key(f, 44, ky + 11, [("- -", cc, "programs that judge chance from the minutes around each moment")])
    f.h = ky + 17
    return f


FIGURES = {"fig_orient": ("fig01_orient", fig_orient), "fig_problem": ("fig02_problem", fig_problem),
           "fig_chance": ("fig03_chance", fig_chance)}
for _i, _d in enumerate(("rate", "coact", "loco", "sce", "cicada", "sync")):
    FIGURES[f"fig_alg_{_d}"] = (f"fig{10 + _i}_alg_{_d}", lambda W, _d=_d: fig_algorithm(W, _d))
FIGURES.update({"fig_scores": ("fig18_scores", fig_scores), "fig_busy": ("fig19_busy", fig_busy)})
for _i, (_n, _l, _s) in enumerate((("real_ttx_brief", "TTX", "fast"), ("real_ttx_long", "TTX", "slow"),
                                   ("real_senk_brief", "senktide", "fast"), ("real_senk_long", "senktide", "slow"))):
    FIGURES[_n] = (f"fig{21 + _i}_{_n}", lambda W, _l=_l, _s=_s: fig_real_overview(W, _l, _s))
FIGURES["fig_eye"] = ("fig25_eye", fig_eye)
FIGURES.update({"fig_count_rule": ("fig04_count_rule", fig_count_rule),
                "fig_count_edge": ("fig05_count_edge", fig_count_edge),
                "fig_count_slices": ("fig06_count_slices", fig_count_slices),
                "fig_count_published": ("fig07_count_published", fig_count_published),
                "fig_chance_steps": ("fig08_chance_steps", fig_chance_steps),
                "fig_shift_shuffle": ("fig09_shift_shuffle", fig_shift_shuffle),
                "fig_simulator": ("fig16_simulator", fig_simulator),
                "fig_grading": ("fig17_grading", fig_grading),
                "fig_count_bar": ("fig20_count_bar", fig_count_bar)})


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
    # the held-out scores the page quotes: the review rebuilt on the stored settings (make_detector_review.py)
    nums = a.plain / "_review_best" / "_work" / "numbers.json"
    W["_numbers"] = json.loads(nums.read_text()) if nums.exists() else None
    figs = {FIGURES[n][0]: FIGURES[n][1](W) for n in a.figs}
    render(figs, a.plain / "print_figures")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
