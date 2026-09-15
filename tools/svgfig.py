"""Small hand-rolled SVG figures: panels, rasters, lanes, traces, histograms, step boxes.

Written for `make_plain_detector_review.py`, whose figures are diagrams with data inside
them — numbered steps, arrows, a histogram of chance counts beside the count it judges —
which a plotting library lays out badly. Nothing here reads data; callers pass arrays.

The house rules it makes easy to keep (CLAUDE.md, plot conventions):

* **Nothing is drawn on a raster.** `Panel.raster` draws ticks and nothing else, and no
  other method takes a raster. Cues go in a lane above it.
* **A marker above a raster points down** — `Panel.down_triangle`.
* **Minutes-friendly time axes** — `time_ticks` picks 60-base steps and labels them
  `45s`, `2m`, `2m30s`.
"""
from __future__ import annotations

import html
import itertools
import math

import numpy as np

FONT = "system-ui, -apple-system, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif"
INK, MUTED, GRID = "#1a1a1a", "#5c5c5c", "#e6e6e6"
#: Clip-path ids must be unique on the whole page, which holds many figures. `id(panel)`
#: is not: Python reuses the address of a panel that has been freed, and a repeated id
#: clips a later panel to an earlier panel's rectangle, so its marks vanish.
_CLIP_IDS = itertools.count()


def esc(s) -> str:
    return html.escape(str(s), quote=True)


def fmt_time(v: float, step: float) -> str:
    """`45s`, `2m`, `2m30s`; seconds with a decimal only when the step needs one."""
    neg = v < 0
    v = abs(v)
    if step < 1:
        s = f"{v:.1f}s"
    elif v < 60:
        s = f"{v:.0f}s"
    else:
        m, sec = divmod(int(round(v)), 60)
        s = f"{m}m" + (f"{sec}s" if sec else "")
    return ("−" if neg else "") + s


def time_ticks(lo: float, hi: float, target: int = 6):
    span = hi - lo
    steps = [b * k for k in (0.1, 1, 60, 3600) for b in (1, 2, 5, 10, 15, 30)]
    step = next((s for s in steps if span / s <= target), steps[-1])
    first = math.ceil(lo / step) * step
    ticks = [first + i * step for i in range(int((hi - first) / step + 1e-9) + 1)]
    return [(t, fmt_time(t, step)) for t in ticks]


def nice_ticks(lo: float, hi: float, target: int = 4):
    span = hi - lo if hi > lo else 1.0
    raw = span / target
    mag = 10 ** math.floor(math.log10(raw))
    step = next(m * mag for m in (1, 2, 2.5, 5, 10) if m * mag >= raw)
    first = math.ceil(lo / step - 1e-9) * step
    out = []
    v = first
    while v <= hi + 1e-9:
        out.append(round(v, 10))
        v += step
    return out


class Figure:
    def __init__(self, width: int, height: int, *, bg: str = "#ffffff"):
        self.w, self.h, self.bg = width, height, bg
        self.parts: list[str] = []

    def add(self, s: str) -> None:
        self.parts.append(s)

    def text(self, x, y, s, *, size=13, anchor="start", weight=400, color=INK, italic=False,
             rotate=None, baseline="alphabetic"):
        tr = f" transform='rotate({rotate} {x:.1f} {y:.1f})'" if rotate is not None else ""
        st = " font-style='italic'" if italic else ""
        self.add(f"<text x='{x:.1f}' y='{y:.1f}' font-size='{size}' text-anchor='{anchor}' "
                 f"font-weight='{weight}' fill='{color}' dominant-baseline='{baseline}'{st}{tr}>{esc(s)}</text>")

    def rich(self, x, y, spans, *, size=13, anchor="start"):
        """One line of text in several styles: spans are (text, dict(weight=, color=))."""
        inner = "".join(f"<tspan font-weight='{o.get('weight', 400)}' fill='{o.get('color', INK)}'"
                        f"{' font-style=\"italic\"' if o.get('italic') else ''}>{esc(t)}</tspan>"
                        for t, o in spans)
        self.add(f"<text x='{x:.1f}' y='{y:.1f}' font-size='{size}' text-anchor='{anchor}'>{inner}</text>")

    def para(self, x, y, s, *, width_chars=40, size=13, lh=1.35, color=INK, weight=400):
        """Wrap plain text into lines; returns the y after the last line."""
        words, line, lines = str(s).split(), "", []
        for w in words:
            if len(line) + len(w) + 1 > width_chars and line:
                lines.append(line)
                line = w
            else:
                line = f"{line} {w}".strip()
        if line:
            lines.append(line)
        for i, ln in enumerate(lines):
            self.text(x, y + i * size * lh, ln, size=size, color=color, weight=weight)
        return y + len(lines) * size * lh

    def line(self, x1, y1, x2, y2, *, color=INK, width=1.0, dash=None, cap="butt"):
        d = f" stroke-dasharray='{dash}'" if dash else ""
        self.add(f"<line x1='{x1:.1f}' y1='{y1:.1f}' x2='{x2:.1f}' y2='{y2:.1f}' stroke='{color}' "
                 f"stroke-width='{width}' stroke-linecap='{cap}'{d}/>")

    def rect(self, x, y, w, h, *, fill="none", stroke="none", width=1.0, rx=0, opacity=1.0):
        self.add(f"<rect x='{x:.1f}' y='{y:.1f}' width='{max(w, 0):.1f}' height='{max(h, 0):.1f}' rx='{rx}' "
                 f"fill='{fill}' stroke='{stroke}' stroke-width='{width}' opacity='{opacity}'/>")

    def arrow(self, x1, y1, x2, y2, *, color=MUTED, width=1.6, head=7):
        self.line(x1, y1, x2, y2, color=color, width=width)
        ang = math.atan2(y2 - y1, x2 - x1)
        p = [(x2, y2),
             (x2 - head * math.cos(ang - 0.45), y2 - head * math.sin(ang - 0.45)),
             (x2 - head * math.cos(ang + 0.45), y2 - head * math.sin(ang + 0.45))]
        self.add("<polygon points='" + " ".join(f"{a:.1f},{b:.1f}" for a, b in p) + f"' fill='{color}'/>")

    def step_badge(self, x, y, n, *, color="#333", r=11):
        self.add(f"<circle cx='{x:.1f}' cy='{y:.1f}' r='{r}' fill='{color}'/>")
        self.text(x, y + 4.5, n, size=13, anchor="middle", weight=700, color="#fff")

    def panel(self, x, y, w, h, xlim, ylim, **kw) -> "Panel":
        return Panel(self, x, y, w, h, xlim, ylim, **kw)

    def svg(self) -> str:
        return (f"<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 {self.w} {self.h}' "
                f"width='{self.w}' height='{self.h}' font-family=\"{FONT}\" "
                f"style='max-width:100%;height:auto;background:{self.bg}'>"
                f"<rect width='100%' height='100%' fill='{self.bg}'/>" + "".join(self.parts) + "</svg>")


class Panel:
    def __init__(self, fig: Figure, x, y, w, h, xlim, ylim, *, frame=True):
        self.f, self.x, self.y, self.w, self.h = fig, x, y, w, h
        self.xlim, self.ylim = xlim, ylim
        if frame:
            fig.rect(x, y, w, h, stroke="#cfcfcf", width=1)

    # coordinates
    def px(self, v):
        a, b = self.xlim
        return self.x + (np.asarray(v, float) - a) / (b - a) * self.w

    def py(self, v):
        a, b = self.ylim
        return self.y + self.h - (np.asarray(v, float) - a) / (b - a) * self.h

    def _clip_open(self):
        cid = f"clip{next(_CLIP_IDS)}"
        self.f.add(f"<clipPath id='{cid}'><rect x='{self.x}' y='{self.y - 1}' width='{self.w}' "
                   f"height='{self.h + 2}'/></clipPath><g clip-path='url(#{cid})'>")

    def _clip_close(self):
        self.f.add("</g>")

    # axes
    def xaxis_time(self, *, label=None, offset=0.0, target=6, size=12):
        """Ticks at `offset`-relative times (e.g. minutes from drug arrival)."""
        lo, hi = self.xlim
        for t, lab in time_ticks(lo - offset, hi - offset, target):
            X = float(self.px(t + offset))
            self.f.line(X, self.y + self.h, X, self.y + self.h + 5, color=MUTED)
            self.f.text(X, self.y + self.h + 18, lab, size=size, anchor="middle", color=MUTED)
        if label:
            self.f.text(self.x + self.w / 2, self.y + self.h + 36, label, size=size, anchor="middle",
                        color=MUTED, italic=True)

    def xaxis_values(self, ticks, *, label=None, size=12, fmt="{:g}"):
        for v in ticks:
            X = float(self.px(v))
            self.f.line(X, self.y + self.h, X, self.y + self.h + 5, color=MUTED)
            self.f.text(X, self.y + self.h + 18, v if isinstance(v, str) else fmt.format(v),
                        size=size, anchor="middle", color=MUTED)
        if label:
            self.f.text(self.x + self.w / 2, self.y + self.h + 36, label, size=size, anchor="middle",
                        color=MUTED, italic=True)

    def yaxis(self, ticks, *, label=None, size=12, fmt="{:g}", grid=False, lines=None, dx=None):
        for v in ticks:
            Y = float(self.py(v))
            if grid:
                self.f.line(self.x, Y, self.x + self.w, Y, color=GRID)
            self.f.line(self.x - 5, Y, self.x, Y, color=MUTED)
            self.f.text(self.x - 8, Y + 4, fmt.format(v), size=size, anchor="end", color=MUTED)
        if label:
            self.ylabel(label, size=size, lines=lines, dx=dx)

    def ylabel(self, label, *, size=12, lines=None, dx=None):
        lines = lines or [label]
        X = self.x - (dx if dx is not None else 36)
        cy = self.y + self.h / 2
        for i, ln in enumerate(lines):
            off = (i - (len(lines) - 1) / 2) * (size + 2)
            self.f.text(X + off, cy, ln, size=size, anchor="middle", color=MUTED, rotate=-90)

    # marks
    def raster(self, trains, *, color=INK, tick_frac=0.8, width=1.3):
        """One row per cell, one tick per event, and nothing else — ever."""
        n = len(trains)
        if not n:
            return
        rh = self.h / n
        self._clip_open()
        segs = []
        for i, v in enumerate(trains):
            y0 = self.y + self.h - (i + 1) * rh + rh * (1 - tick_frac) / 2
            y1 = y0 + rh * tick_frac
            for t in np.asarray(v, float):
                if self.xlim[0] <= t <= self.xlim[1]:
                    X = float(self.px(t))
                    segs.append(f"M{X:.1f} {y0:.1f}V{y1:.1f}")
        if segs:
            self.f.add(f"<path d='{''.join(segs)}' stroke='{color}' stroke-width='{width}' fill='none'/>")
        self._clip_close()

    def steps(self, t, y, *, color, width=1.6, where="mid", fill=None, dash=None):
        t, y = np.asarray(t, float), np.asarray(y, float)
        if not t.size:
            return
        dt = np.diff(t)
        half = np.r_[dt[0] if dt.size else 1.0, dt] / 2 if where == "mid" else np.zeros_like(t)
        pts = []
        for i in range(t.size):
            if not np.isfinite(y[i]):
                continue
            a = t[i] - (half[i] if where == "mid" else 0)
            b = t[i] + (np.r_[dt, dt[-1] if dt.size else 1.0][i] / 2 if where == "mid" else
                        (dt[i] if i < dt.size else 0))
            pts.append((a, y[i]))
            pts.append((b, y[i]))
        self._path(pts, color=color, width=width, fill=fill, dash=dash)

    def curve(self, t, y, *, color, width=1.5, dash=None):
        t, y = np.asarray(t, float), np.asarray(y, float)
        ok = np.isfinite(y)
        # break the path at gaps
        run = []
        for i in range(t.size):
            if ok[i]:
                run.append((t[i], y[i]))
            elif run:
                self._path(run, color=color, width=width, dash=dash)
                run = []
        if run:
            self._path(run, color=color, width=width, dash=dash)

    def _path(self, pts, *, color, width, fill=None, dash=None):
        if not pts:
            return
        self._clip_open()
        d = "M" + "L".join(f"{float(self.px(a)):.1f} {float(self.py(b)):.1f}" for a, b in pts)
        ds = f" stroke-dasharray='{dash}'" if dash else ""
        self.f.add(f"<path d='{d}' stroke='{color}' stroke-width='{width}' fill='none' "
                   f"stroke-linejoin='round'{ds}/>")
        self._clip_close()

    def hline(self, v, *, color=INK, width=1.6, dash="5 4", x0=None, x1=None):
        Y = float(self.py(v))
        a = self.x if x0 is None else float(self.px(x0))
        b = self.x + self.w if x1 is None else float(self.px(x1))
        self.f.line(a, Y, b, Y, color=color, width=width, dash=dash)

    def vline(self, v, *, color=MUTED, width=1.0, dash="3 3"):
        X = float(self.px(v))
        self.f.line(X, self.y, X, self.y + self.h, color=color, width=width, dash=dash)

    def dots(self, t, y, *, color, r=2.4, opacity=1.0):
        for a, b in zip(np.asarray(t, float), np.asarray(y, float)):
            if np.isfinite(b) and self.xlim[0] <= a <= self.xlim[1]:
                self.f.add(f"<circle cx='{float(self.px(a)):.1f}' cy='{float(self.py(b)):.1f}' r='{r}' "
                           f"fill='{color}' opacity='{opacity}'/>")

    def dashes(self, t, y, *, color, half_width=5, width=2.4):
        for a, b in zip(np.asarray(t, float), np.asarray(y, float)):
            if np.isfinite(b) and self.xlim[0] <= a <= self.xlim[1]:
                X, Y = float(self.px(a)), float(self.py(b))
                self.f.line(X - half_width, Y, X + half_width, Y, color=color, width=width)

    def bars(self, xs, hs, *, color, width_frac=0.8, stroke="none", x_is_center=True):
        xs, hs = np.asarray(xs, float), np.asarray(hs, float)
        step = (xs[1] - xs[0]) if xs.size > 1 else 1.0
        for a, b in zip(xs, hs):
            if not np.isfinite(b) or b <= self.ylim[0]:
                continue
            x0 = float(self.px(a - step * width_frac / 2)) if x_is_center else float(self.px(a))
            x1 = float(self.px(a + step * width_frac / 2)) if x_is_center else float(self.px(a + step * width_frac))
            y1 = float(self.py(min(b, self.ylim[1])))
            self.f.rect(x0, y1, x1 - x0, float(self.py(self.ylim[0])) - y1, fill=color, stroke=stroke)

    def span(self, t0, t1, *, row_y, row_h, color, opacity=1.0, min_px=2.0):
        a, b = float(self.px(max(t0, self.xlim[0]))), float(self.px(min(t1, self.xlim[1])))
        if b < self.x or a > self.x + self.w:
            return
        if b - a < min_px:
            c = (a + b) / 2
            a, b = c - min_px / 2, c + min_px / 2
        self.f.rect(a, row_y, b - a, row_h, fill=color, opacity=opacity)

    def down_triangle(self, t, y, *, color, size=9, hollow=False):
        if not (self.xlim[0] <= t <= self.xlim[1]):
            return
        X = float(self.px(t))
        pts = f"{X - size / 2:.1f},{y - size * 0.45:.1f} {X + size / 2:.1f},{y - size * 0.45:.1f} {X:.1f},{y + size * 0.5:.1f}"
        if hollow:
            self.f.add(f"<polygon points='{pts}' fill='#fff' stroke='{color}' stroke-width='1.4'/>")
        else:
            self.f.add(f"<polygon points='{pts}' fill='{color}'/>")
