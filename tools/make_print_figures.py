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


FIGURES = {"fig_orient": ("fig01_orient", fig_orient), "fig_problem": ("fig02_problem", fig_problem),
           "fig_chance": ("fig03_chance", fig_chance)}
for _i, _d in enumerate(("rate", "coact", "loco", "sce", "cicada", "sync")):
    FIGURES[f"fig_alg_{_d}"] = (f"fig{10 + _i}_alg_{_d}", lambda W, _d=_d: fig_algorithm(W, _d))
FIGURES.update({"fig_scores": ("fig18_scores", fig_scores), "fig_busy": ("fig19_busy", fig_busy)})
for _i, (_n, _l, _s) in enumerate((("real_ttx_brief", "TTX", "fast"), ("real_ttx_long", "TTX", "slow"),
                                   ("real_senk_brief", "senktide", "fast"), ("real_senk_long", "senktide", "slow"))):
    FIGURES[_n] = (f"fig{21 + _i}_{_n}", lambda W, _l=_l, _s=_s: fig_real_overview(W, _l, _s))
FIGURES["fig_eye"] = ("fig25_eye", fig_eye)


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
