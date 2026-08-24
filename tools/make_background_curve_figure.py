#!/usr/bin/env python3
"""Every detector's F1 across the background rate, and the ranking that does not survive it.

    python tools/make_background_curve_figure.py --also docs/learned

Figure id `background_curve`, the same on every machine.

`docs/RESET.md` §7 item 2: *"The background axis becomes a reported curve, not a
point."* This draws the curve.

**Panel A** is every detector's F1 across `bench.BACKGROUND_GRID`, with the two
`REGIMES` endpoints marked. **Panel B** is the rank of each detector at each
point on that axis — the part a table of single numbers cannot show.

The comparison worth making is with the tolerance curve, which asked the same
question and got the reassuring answer: five of six detectors were flat, so the
inherited 1.5 s was granting slack nobody used. Nothing is flat here, the
smallest spread is larger than the gap the published bake-off asks readers to
believe between its top two rows, and **the best detector at the quiet endpoint
is not the best detector at the busy one**.

**This measures and changes nothing.** `REGIMES` is untouched, no operating point
moves, `evaluate` is unchanged, and `tests/test_background_curve.py` pins the
curve against `evaluate` where the grid meets a regime so the two cannot drift
apart.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np

FIGURE_ID = "background_curve"

INK = "#16202b"
GUIDE = "#9a9a9a"
COLOURS = {
    "coact": "#b03a48", "loco": "#1f6fb4", "rate": "#2e8b57",
    "cicada": "#7a4fa3", "sync": "#c9782a", "sce": "#5c6773",
}
LABELS = {"coact": "CoactDetect", "loco": "LoCo", "rate": "rate+context",
          "cicada": "locust", "sync": "SPIKE-synch", "sce": "binned SCE"}

SEEDS = (1, 2, 3)
REGIME = "baseline_quiet"

#: The gap between the top two rows of the published bake-off. Every spread below
#: is quoted against it, because that is the difference the table asks a reader to
#: treat as meaningful.
BAKEOFF_TOP_GAP = 0.017


def measure() -> dict:
    from bugarach.bench import (BACKGROUND_GRID, DETECTORS, REGIMES,
                                background_spread, describe_background,
                                evaluate_background_curve)

    curves = {n: evaluate_background_curve(n, REGIME, SEEDS) for n in DETECTORS}
    rates = list(BACKGROUND_GRID)
    order_at = {r: sorted(DETECTORS, key=lambda n: -curves[n][r].f1)
                for r in rates}
    return {
        "rates": rates,
        "f1": {n: [curves[n][r].f1 for r in rates] for n in DETECTORS},
        "rank": {n: [order_at[r].index(n) + 1 for r in rates] for n in DETECTORS},
        "spread": {n: background_spread(curves[n]) for n in DETECTORS},
        "said": {n: describe_background(curves[n]) for n in DETECTORS},
        "quiet": REGIMES["baseline_quiet"]["bg_rate_hz"],
        "busy": REGIMES["baseline_busy"]["bg_rate_hz"],
        "order_at": order_at,
    }


def build(m: dict, width: int):
    import holoviews as hv

    x = [r * 1000.0 for r in m["rates"]]
    marks = [m["quiet"] * 1000.0, m["busy"] * 1000.0]

    # ---- Panel A: F1 across the axis
    items = []
    for r in marks:
        items.append(hv.VLine(r).opts(color=GUIDE, line_dash="dashed",
                                      line_width=1))
    for n, f1 in sorted(m["f1"].items(), key=lambda kv: -max(kv[1])):
        c = COLOURS[n]
        items.append(hv.Curve((x, f1), label=LABELS[n]).opts(
            color=c, line_width=2.2))
        items.append(hv.Scatter((x, f1)).opts(color=c, size=6, line_color=None))
    panel_a = hv.Overlay(items).opts(
        width=width // 2, height=420, logx=True,
        xlabel="background rate (mHz per ROI), log scale · dashed: the two REGIMES",
        ylabel="F1 · same planted events throughout",
        ylim=(0.0, 0.9),
        fontsize={"xlabel": "9pt", "ylabel": "9pt", "ticks": "8pt",
                  "legend": "8pt"},
        legend_position="bottom_left", legend_cols=2,
        toolbar=None, show_grid=True)

    # ---- Panel B: the ranking, inverted so first place is at the top
    ritems = []
    for r in marks:
        ritems.append(hv.VLine(r).opts(color=GUIDE, line_dash="dashed",
                                       line_width=1))
    for n, rank in m["rank"].items():
        c = COLOURS[n]
        ritems.append(hv.Curve((x, rank)).opts(color=c, line_width=2.2))
        ritems.append(hv.Scatter((x, rank)).opts(
            color=c, size=9, line_color=INK, line_width=0.6))
    panel_b = hv.Overlay(ritems).opts(
        width=width // 2, height=420, logx=True, invert_yaxis=True,
        xlabel="background rate (mHz per ROI), log scale",
        ylabel="rank · 1 is best",
        # ylim stays (low, high) even with invert_yaxis — passing it reversed as
        # well flipped the axis twice and put first place at the bottom, under a
        # label saying 1 is best.
        ylim=(0.4, 6.6),
        fontsize={"xlabel": "9pt", "ylabel": "9pt", "ticks": "8pt"},
        show_legend=False, toolbar=None, show_grid=True)

    return hv.Layout([panel_a, panel_b]).cols(2).opts(
        shared_axes=False, toolbar=None)


def header_html(m: dict) -> str:
    order = sorted(m["spread"], key=lambda n: -m["spread"][n])
    rows = "".join(
        f"<tr><td style='padding:2px 14px 2px 0'>"
        f"<span style='color:{COLOURS[n]}'>&#9632;</span> {LABELS[n]}</td>"
        f"<td style='padding:2px 14px 2px 0;text-align:right'>"
        f"{m['f1'][n][m['rates'].index(m['quiet'])]:.3f}</td>"
        f"<td style='padding:2px 14px 2px 0;text-align:right'>"
        f"{m['f1'][n][m['rates'].index(m['busy'])]:.3f}</td>"
        f"<td style='padding:2px 14px 2px 0;text-align:right'><b>"
        f"{m['spread'][n]:.3f}</b></td>"
        f"<td style='padding:2px 0;text-align:right'>"
        f"{m['spread'][n]/BAKEOFF_TOP_GAP:.0f}&times;</td></tr>"
        for n in order)
    quiet_best = LABELS[m["order_at"][m["quiet"]][0]]
    busy_best = LABELS[m["order_at"][m["busy"]][0]]
    return f"""
<div style="font:13px/1.5 -apple-system,Segoe UI,sans-serif;color:{INK};
            max-width:62rem;margin:0 auto 0.5rem">
<p><b>An operating point is chosen at one background rate and quoted as though it
held across the axis.</b> It does not. Same planted events throughout — same
count, same times, same recruitment — with only the field they sit in changing.
The dashed lines are the two <code>REGIMES</code> endpoints, which are the
interquartile spread of <i>untreated</i> slices rather than a treatment effect.</p>

<table style="border-collapse:collapse;font-size:12px">
<tr style="border-bottom:1px solid #c8d6e4">
  <th style="text-align:left;padding-right:14px">detector</th>
  <th style="text-align:right;padding-right:14px">F1 at quiet</th>
  <th style="text-align:right;padding-right:14px">F1 at busy</th>
  <th style="text-align:right;padding-right:14px">spread across grid</th>
  <th style="text-align:right">vs the bake-off's top gap</th></tr>
{rows}
</table>

<p><b>The ranking does not survive it either</b> (panel B). The best detector at
the quiet endpoint is <b>{quiet_best}</b>; at the busy endpoint it is
<b>{busy_best}</b> — and those two points are both regimes this project fits and
reports at. One detector moves four places across the grid.</p>

<p><b>Compare with the tolerance curve, which asked the same question and got the
opposite answer.</b> Five of six detectors were flat across
<code>TOLERANCE_GRID</code>, so the inherited 1.5&nbsp;s was granting slack nobody
used and no comparison rested on it. Here the <i>smallest</i> spread is
{min(m['spread'].values())/BAKEOFF_TOP_GAP:.0f}&times; the difference the
published bake-off asks readers to believe between its top two rows, so
<code>describe_background</code> refuses a bare F1 for every one of the six.</p>

<p style="color:#5c6773">{len(SEEDS)} seeds per point, base recording
<code>{REGIME}</code>, matching tolerance 1.5&nbsp;s.
<b>This measures and changes nothing:</b> <code>REGIMES</code> is untouched, no
operating point moves, and <code>evaluate</code> is unchanged.
<code>tests/test_background_curve.py</code> pins the curve against
<code>evaluate</code> where the grid meets a regime, so the two cannot drift.</p>
</div>"""


def _render_png(html_path: Path, png_path: Path, *, wait_ms: int = 2500,
                width: int = 1500, height: int = 1000) -> bool:
    try:
        from playwright.sync_api import sync_playwright
    except Exception as exc:                                   # noqa: BLE001
        print(f"(PNG render skipped: {exc})", file=sys.stderr)
        return False
    try:
        with sync_playwright() as pw:
            b = pw.chromium.launch()
            pg = b.new_page(viewport={"width": width, "height": height},
                            device_scale_factor=2)
            pg.goto(html_path.resolve().as_uri())
            pg.wait_for_timeout(wait_ms)
            pg.screenshot(path=str(png_path), full_page=True)
            b.close()
        return True
    except Exception as exc:                                   # noqa: BLE001
        print(f"(PNG render failed: {type(exc).__name__}: {exc})", file=sys.stderr)
        return False


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--width", type=int, default=1240)
    p.add_argument("--out", default=None,
                   help="destination; defaults to the darkroom")
    p.add_argument("--also", type=Path, default=None,
                   help="second destination, e.g. docs/learned")
    p.add_argument("--no-png", dest="png", action="store_false", default=True)
    a = p.parse_args()

    print("scoring every detector across the background grid…")
    m = measure()
    for n in sorted(m["spread"], key=lambda k: -m["spread"][k]):
        print(f"  {LABELS[n]:<14} spread {m['spread'][n]:.3f}  {m['said'][n]}")
    print(f"  best at quiet: {LABELS[m['order_at'][m['quiet']][0]]} · "
          f"best at busy: {LABELS[m['order_at'][m['busy']][0]]}")

    from bugarach.paths import darkroom, unresolved_message
    dest = Path(a.out) if a.out else darkroom()
    if dest is None:
        print(unresolved_message(), file=sys.stderr)
        return 1

    import holoviews as hv
    import panel as pn
    hv.extension("bokeh")
    layout = build(m, a.width)

    dests = [dest] + ([a.also] if a.also else [])
    for i, d in enumerate(dests):
        d.mkdir(parents=True, exist_ok=True)
        html = d / f"{FIGURE_ID}.html"
        pn.panel(pn.Column(pn.pane.HTML(header_html(m)),
                           pn.pane.HoloViews(layout))).save(str(html))
        print(f"wrote {html}")
        if a.png:
            shot = d / f"{FIGURE_ID}.png"
            if i == 0:
                if _render_png(html, shot):
                    print(f"wrote {shot}")
            else:
                src = dests[0] / f"{FIGURE_ID}.png"
                if src.is_file():
                    shot.write_bytes(src.read_bytes())
                    print(f"wrote {shot}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
