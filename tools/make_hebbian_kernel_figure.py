#!/usr/bin/env python3
"""The coincidence kernel on the frame grid, what it gives a coordinated pair, and the bound.

    python tools/make_hebbian_kernel_figure.py --also docs/proposals/2026-09-25-hebbian-coupling-detector

Figure id `hebbian_kernel`. Figure 1 of the Hebbian coupling proposal
(`docs/proposals/2026-09-25-hebbian-coupling-detector.md`). Everything in it is computed
here from the rule's own definitions; no recording is read.

- **A. The kernel on whole-frame lags.** Co(k) = cos(pi k / m) for a coincidence span of m
  frames, the end lags (|k| = m) at half weight, zero beyond. The half weights are what make
  the lag sum zero; unweighted it is -1 for every m.
- **B. What one update is worth.** The expected Co for a pair of ROIs that share an event
  time (onsets scattered by the ruled per-participant jitter sigma, floored to 0.1 s frames),
  against m. A pair with independent onsets has expected Co 0 at every m (panel A's lag
  sum), and a same-frame artifact scores 1.
- **C. The bound.** Equation 8's step size q(s) with the clamp at s0(1 +- s_d), and where
  one coincidence from rest lands at three step sizes. Above q0 = s0 s_d / 2 a single step
  from rest overshoots the clamp.

Writes an SVG (and a PNG through Playwright chromium when it can) to the darkroom by
default; `--also` writes the repo copy.
"""
from __future__ import annotations

import argparse
import math
import os
import random
import sys
from pathlib import Path

FIGURE_ID = "hebbian_kernel"

FRAME_SEC = 0.1                       # the frame interval on the default folder, about 0.1 s
SIGMA_SEC = {"fast": 0.106, "slow": 0.135}   # ruled 2026-09-22, decisions_pending.md item 2
SPANS = (2, 3, 4, 5, 6)               # coincidence span m, in whole frames

# Equation 8's constants, as clamor transcribes them (clamor/malsburg1986.py).
S0, S_D, Q0 = 0.012, 0.8, 0.01
S_MIN, S_MAX = S0 * (1 - S_D), S0 * (1 + S_D)
Q0_LIMIT = S0 * S_D / 2               # largest step whose first move from rest stays inside


def weight(k: int, m: int) -> float:
    """The kernel at whole-frame lag k for a span of m frames, end lags at half weight."""
    a = abs(k)
    if a > m:
        return 0.0
    c = math.cos(math.pi * a / m)
    return 0.5 * c if a == m else c


def lag_sum(m: int, half_ends: bool = True) -> float:
    s = sum(math.cos(math.pi * k / m) for k in range(-m, m + 1))
    return s + 1.0 if half_ends else s        # the two ends are -1 each; halving adds +1


def lag_distribution(sigma_frames: float, n: int = 400_000, seed: int = 20260925) -> dict:
    """P(lag = k frames) for two onsets scattered around one shared event time."""
    rng = random.Random(seed)
    counts: dict[int, int] = {}
    for _ in range(n):
        t = rng.random()
        k = (math.floor(t + rng.gauss(0.0, sigma_frames))
             - math.floor(t + rng.gauss(0.0, sigma_frames)))
        counts[k] = counts.get(k, 0) + 1
    return {k: c / n for k, c in counts.items()}


def q(s: float, q0: float) -> float:
    return q0 * (1.0 - ((s - S0) / (S0 * S_D)) ** 2)


def measure() -> dict:
    out = {"lag_sums": {m: (lag_sum(m, False), lag_sum(m, True)) for m in SPANS}, "coord": {}}
    for stream, sig in SIGMA_SEC.items():
        p = lag_distribution(sig / FRAME_SEC)
        rows = {}
        for m in SPANS:
            e = sum(pk * weight(k, m) for k, pk in p.items())
            neg = sum(pk for k, pk in p.items() if weight(k, m) < 0)
            rows[m] = (e, neg)
        out["coord"][stream] = rows
    steps = {}
    for label, q0 in (("paper q0 = 0.01", Q0), ("q0 = 0.004", 0.004), ("q0 / 12", Q0 / 12)):
        steps[label] = (q0, S0 + q(S0, q0))
    out["steps"] = steps
    return out


# ------------------------------------------------------------------ drawing (plain SVG)
INK, GRID, MUTED = "#1f1f1f", "#d6d6d6", "#6b6b6b"
FAST, SLOW, WARN = "#1b6ca8", "#c2571a", "#b3261e"
FONT = "font-family='Helvetica, Arial, sans-serif'"


def _t(x, y, s, size=13, anchor="middle", fill=INK, weight="normal", rotate=None):
    rot = f" transform='rotate({rotate} {x} {y})'" if rotate else ""
    return (f"<text x='{x:.1f}' y='{y:.1f}' font-size='{size}' text-anchor='{anchor}' "
            f"fill='{fill}' font-weight='{weight}' {FONT}{rot}>{s}</text>")


class Axes:
    def __init__(self, x0, y0, w, h, xlim, ylim):
        self.x0, self.y0, self.w, self.h, self.xlim, self.ylim = x0, y0, w, h, xlim, ylim

    def X(self, v):
        return self.x0 + (v - self.xlim[0]) / (self.xlim[1] - self.xlim[0]) * self.w

    def Y(self, v):
        return self.y0 + self.h - (v - self.ylim[0]) / (self.ylim[1] - self.ylim[0]) * self.h

    def frame(self, xticks, yticks, xlabel, ylabel, letter, xfmt=str, yfmt=str):
        o = [f"<rect x='{self.x0}' y='{self.y0}' width='{self.w}' height='{self.h}' "
             f"fill='none' stroke='{INK}' stroke-width='1'/>"]
        for v in xticks:
            o.append(f"<line x1='{self.X(v):.1f}' y1='{self.y0 + self.h}' x2='{self.X(v):.1f}' "
                     f"y2='{self.y0 + self.h + 5}' stroke='{INK}'/>")
            o.append(_t(self.X(v), self.y0 + self.h + 19, xfmt(v), 12))
        for v in yticks:
            o.append(f"<line x1='{self.x0}' y1='{self.Y(v):.1f}' x2='{self.x0 + self.w}' "
                     f"y2='{self.Y(v):.1f}' stroke='{GRID}' stroke-width='0.8'/>")
            o.append(_t(self.x0 - 8, self.Y(v) + 4, yfmt(v), 12, "end"))
        o.append(_t(self.x0 + self.w / 2, self.y0 + self.h + 40, xlabel, 13))
        o.append(_t(self.x0 - 48, self.y0 + self.h / 2, ylabel, 13, rotate=-90))
        o.append(_t(self.x0 - 52, self.y0 - 12, letter, 17, "start", weight="bold"))
        return o


def build(meas: dict) -> str:
    W, H = 1260, 540
    o = [f"<svg xmlns='http://www.w3.org/2000/svg' width='{W}' height='{H}' "
         f"viewBox='0 0 {W} {H}'>", f"<rect width='{W}' height='{H}' fill='white'/>"]

    # A. the kernel at m = 4 frames on whole-frame lags, the continuous cosine behind it
    m = 4
    a = Axes(80, 40, 320, 330, (-m - 1.5, m + 1.5), (-1.15, 1.15))
    o += a.frame(range(-m - 1, m + 2), (-1, -0.5, 0, 0.5, 1),
                 f"lag between two onsets (frames of {FRAME_SEC} s)",
                 "update weight Co (unitless)", "A", yfmt=lambda v: f"{v:g}")
    pts = " ".join(f"{a.X(x):.1f},{a.Y(math.cos(math.pi * x / m)):.1f}"
                   for x in [i / 20 for i in range(-20 * m, 20 * m + 1)])
    o.append(f"<polyline points='{pts}' fill='none' stroke='{MUTED}' stroke-width='1.2' "
             f"stroke-dasharray='4 3'/>")
    for k in range(-m - 1, m + 2):
        v = weight(k, m)
        o.append(f"<line x1='{a.X(k):.1f}' y1='{a.Y(0):.1f}' x2='{a.X(k):.1f}' "
                 f"y2='{a.Y(v):.1f}' stroke='{INK}' stroke-width='2'/>")
        hollow = abs(k) == m
        o.append(f"<circle cx='{a.X(k):.1f}' cy='{a.Y(v):.1f}' r='4.5' "
                 f"fill='{'white' if hollow else INK}' stroke='{INK}' stroke-width='1.6'/>")
    unw, half = meas["lag_sums"][m]
    o.append(_t(a.X(0), a.y0 + a.h + 62,
                f"span m = {m} frames · lag sum {unw:.0f} unweighted, {abs(half):.0f} with the "
                f"hollow end lags at half weight", 12, fill=MUTED))

    # B. expected Co per update for a coordinated pair, against the span
    b = Axes(520, 40, 300, 330, (1.5, 6.5), (-0.1, 1.05))
    o += b.frame(SPANS, (0, 0.25, 0.5, 0.75, 1.0),
                 f"coincidence span m (frames of {FRAME_SEC} s)",
                 "expected Co per update (unitless)", "B", yfmt=lambda v: f"{v:g}")
    o.append(f"<line x1='{b.X(1.5)}' y1='{b.Y(0):.1f}' x2='{b.X(6.5)}' y2='{b.Y(0):.1f}' "
             f"stroke='{INK}' stroke-width='1.4'/>")
    o.append(_t(b.X(6.4), b.Y(0) - 7, "independent onsets: 0 at every span", 11, "end", MUTED))
    o.append(f"<line x1='{b.X(1.5)}' y1='{b.Y(1):.1f}' x2='{b.X(6.5)}' y2='{b.Y(1):.1f}' "
             f"stroke='{WARN}' stroke-width='1.2' stroke-dasharray='5 4'/>")
    o.append(_t(b.X(6.4), b.Y(1) + 15, "same-frame artifact: 1", 11, "end", WARN))
    for stream, col in (("fast", FAST), ("slow", SLOW)):
        rows = meas["coord"][stream]
        pts = " ".join(f"{b.X(mm):.1f},{b.Y(rows[mm][0]):.1f}" for mm in SPANS)
        o.append(f"<polyline points='{pts}' fill='none' stroke='{col}' stroke-width='2'/>")
        for mm in SPANS:
            o.append(f"<circle cx='{b.X(mm):.1f}' cy='{b.Y(rows[mm][0]):.1f}' r='4' "
                     f"fill='{col}'/>")
    ly = b.Y(0.9)
    for i, (stream, col) in enumerate((("fast", FAST), ("slow", SLOW))):
        sig = SIGMA_SEC[stream]
        o.append(f"<circle cx='{b.x0 + 16}' cy='{ly + 18 * i - 4}' r='4' fill='{col}'/>")
        o.append(_t(b.x0 + 26, ly + 18 * i, f"{stream} stream, jitter σ = {sig} s", 11,
                    "start", col))

    # C. the bound: q(s) and where one coincidence from rest lands
    c = Axes(940, 40, 290, 330, (0.0, 0.0245), (-0.0015, 0.0112))
    o += c.frame((0.0, 0.006, 0.012, 0.018, 0.024), (0, 0.004, 0.008),
                 "coupling s (paper's units)", "step size q(s) (paper's units)", "C",
                 xfmt=lambda v: f"{v:.3f}", yfmt=lambda v: f"{v:.3f}")
    for lim, name in ((S_MIN, "clamp"), (S_MAX, "clamp")):
        o.append(f"<line x1='{c.X(lim):.1f}' y1='{c.y0}' x2='{c.X(lim):.1f}' "
                 f"y2='{c.y0 + c.h}' stroke='{MUTED}' stroke-width='1.2' "
                 f"stroke-dasharray='3 3'/>")
        o.append(_t(c.X(lim), c.y0 - 4, name, 11, fill=MUTED))
    o.append(f"<line x1='{c.x0}' y1='{c.Y(0):.1f}' x2='{c.x0 + c.w}' y2='{c.Y(0):.1f}' "
             f"stroke='{INK}' stroke-width='1'/>")
    pts = " ".join(f"{c.X(s):.1f},{c.Y(q(s, Q0)):.1f}"
                   for s in [i * 0.0245 / 200 for i in range(201)] if q(s, Q0) > -0.0015)
    o.append(f"<polyline points='{pts}' fill='none' stroke='{INK}' stroke-width='2'/>")
    marks = (("paper q0 = 0.01", WARN), ("q0 = 0.004", FAST), ("q0 / 12", SLOW))
    for i, (label, col) in enumerate(marks):
        q0, s1 = meas["steps"][label]
        o.append(f"<path d='M {c.X(s1):.1f} {c.Y(0) + 4:.1f} l -5 9 l 10 0 z' fill='{col}'/>")
        o.append(_t(c.x0 - 40, c.y0 + c.h + 66 + 17 * i,
                    f"▲ {label}: one coincidence from rest → s = {s1:.4f}", 11, "start", col))
    o.append(_t(c.x0 - 40, c.y0 + c.h + 66 + 17 * 3,
                "curve: q(s) at the paper's q0 = 0.01", 11, "start"))
    o.append("</svg>")
    return "\n".join(o)


def _render_png(svg: Path, png: Path) -> bool:
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        return False
    try:
        with sync_playwright() as p:
            # A machine whose Playwright and browser versions differ names its browser here.
            exe = os.environ.get("BUGARACH_CHROMIUM")
            b = p.chromium.launch(executable_path=exe) if exe else p.chromium.launch()
            pg = b.new_page(viewport={"width": 1260, "height": 540}, device_scale_factor=2)
            pg.goto(svg.resolve().as_uri())
            pg.screenshot(path=str(png), full_page=True)
            b.close()
        return True
    except Exception as exc:                       # a missing browser is a skip, not a failure
        print(f"png skipped: {exc}", file=sys.stderr)
        return False


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--out", default=None, help="destination directory; default the darkroom")
    p.add_argument("--also", type=Path, default=None, help="a second copy, e.g. in the repo")
    p.add_argument("--no-png", dest="png", action="store_false", default=True)
    a = p.parse_args(argv)

    meas = measure()
    for m, (unw, half) in meas["lag_sums"].items():
        print(f"span {m} frames: lag sum {unw:+.3f} unweighted, {half:+.3f} half-weighted ends")
    for stream, rows in meas["coord"].items():
        for m, (e, neg) in rows.items():
            print(f"{stream} span {m} frames ({m * FRAME_SEC:.1f} s): expected Co {e:.3f}, "
                  f"{neg * 100:.0f}% of coordinated updates negative")
    for label, (q0, s1) in meas["steps"].items():
        print(f"{label}: one coincidence from rest lands at s = {s1:.5f} "
              f"(clamp {S_MIN:.4f}-{S_MAX:.4f}; overshoot limit q0 < {Q0_LIMIT:.4f})")

    sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
    from bugarach.paths import darkroom
    dests = [Path(a.out) if a.out else darkroom(FIGURE_ID)]
    if dests[0] is None:
        print("darkroom not found — skipping the darkroom copy", file=sys.stderr)
        dests = []
    if a.also:
        dests.append(a.also)
    svg_text = build(meas)
    for d in dests:
        d.mkdir(parents=True, exist_ok=True)
        svg = d / f"{FIGURE_ID}.svg"
        svg.write_text(svg_text)
        print(f"wrote {svg}")
        if a.png and _render_png(svg, d / f"{FIGURE_ID}.png"):
            print(f"wrote {d / f'{FIGURE_ID}.png'}")
    return 0 if dests else 1


if __name__ == "__main__":
    sys.exit(main())
