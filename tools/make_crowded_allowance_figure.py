#!/usr/bin/env python3
"""Where the merge-gap verdict moves with the crowded allowance, and where the search runs off its grid.

    python tools/make_crowded_allowance_figure.py --sweep <sweep folder> --also docs/learned/runs/2026-09-21-crowded-allowance-sweep

Figure id `crowded_allowance`, the same on every machine.

Reads the sweep written by `tools/tune_net_merge_gap.py select --max-drop ...` at
eleven allowances on both seed draws (`sweep_summary.json`).

**Panel A (ungated) and Panel B (gated)** are the held-out mean F1 difference, net
minus CoactDetect, against the allowance. Negative is CoactDetect ahead. **Panel C**
is how many of the 32 selections (4 nets x 4 outer folds x 2 selection rules) chose
the top of the gap grid, 30 s.

Panel C is why the other two cannot be read alone. The allowances where a verdict
flips are the allowances where the search is pinned at the edge of its own grid, so
the flip measures the grid's end and not a better gap.

**This measures and changes nothing.** No operating point moves, the merge-gap page
is untouched, and whether any of this passes the unsigned 0.02 allowance is Tony's
call, not this figure's.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

FIGURE_ID = "crowded_allowance"

INK = "#16202b"
GUIDE = "#9a9a9a"
ZERO = "#4a4a4a"

# Four inks a protan/deutan reader can still separate against each other and
# against the guide grey; the repo's own figure palette, extended by one.
COLOURS = {
    "chorus_norm": "#1f6fb4",
    "chorus_gain_norm": "#d55e00",
    "line_length": "#2e8b57",
    "tube": "#6a3d9a",
}
LABELS = {
    "chorus_norm": "chorus",
    "chorus_gain_norm": "chorus-gain",
    "line_length": "line-length",
    "tube": "tube",
}
NETS = list(COLOURS)
DRAWS = {"run": "solid", "replicate": "dashed"}

#: The allowance the run adopted, and the one the sweep exists to question.
ADOPTED = 0.02


def _order(keys):
    """Allowances smallest first, with the no-check row last."""
    numeric = sorted((k for k in keys if k != "nocheck"), key=float)
    return numeric + (["nocheck"] if "nocheck" in keys else [])


def read(sweep: Path) -> dict:
    s = json.loads((sweep / "sweep_summary.json").read_text())["allowances"]
    order = _order(s)
    rows = {}
    for draw in DRAWS:
        for net in NETS:
            for gating in ("ungated", "gated"):
                xs, ys = [], []
                for i, a in enumerate(order):
                    block = s[a].get(draw)
                    if not block:
                        continue
                    cell = block["selections"][gating].get(net)
                    if cell is None:
                        continue
                    xs.append(i)
                    ys.append(cell["mean"])
                if xs:
                    rows[(draw, net, gating)] = (xs, ys)
    edge = {}
    for draw in DRAWS:
        xs, ys = [], []
        for i, a in enumerate(order):
            block = s[a].get(draw)
            if not block or block.get("gaps_at_grid_edge") is None:
                continue
            xs.append(i)
            ys.append(block["gaps_at_grid_edge"])
        if xs:
            edge[draw] = (xs, ys)
    labels = [("no check" if a == "nocheck" else a) for a in order]
    adopted_at = order.index(str(ADOPTED)) if str(ADOPTED) in order else None
    return {"order": order, "labels": labels, "rows": rows,
            "edge": edge, "adopted_at": adopted_at}


def build(m: dict, width: int):
    import holoviews as hv

    ticks = [(i, t) for i, t in enumerate(m["labels"])]
    n = len(m["labels"])

    def guides(with_zero: bool):
        items = []
        if m["adopted_at"] is not None:
            items.append(hv.VLine(m["adopted_at"]).opts(
                color=GUIDE, line_dash="dashed", line_width=1.2))
        if with_zero:
            items.append(hv.HLine(0.0).opts(
                color=ZERO, line_dash="dotted", line_width=1.2))
        return items

    # Only the bottom panel carries the x-axis; it is taller by exactly the
    # room the axis takes, so the three plot areas still match.
    panels = []
    for letter, gating in (("A", "ungated"), ("B", "gated")):
        items = guides(True)
        for draw, dash in DRAWS.items():
            for net in NETS:
                key = (draw, net, gating)
                if key not in m["rows"]:
                    continue
                xs, ys = m["rows"][key]
                label = f"{LABELS[net]} · {draw}"
                items.append(hv.Curve((xs, ys), label=label).opts(
                    color=COLOURS[net], line_dash=dash, line_width=2.2))
                items.append(hv.Scatter((xs, ys)).opts(
                    color=COLOURS[net], size=5, line_color=None))
        show_legend = letter == "A"
        panels.append(hv.Overlay(items).opts(
            width=width, height=250, show_grid=True,
            xticks=ticks, xlabel="", xaxis=None,
            ylabel=f"{letter} · {gating} — mean ΔF1, net − coact",
            xlim=(-0.4, n - 0.6), show_legend=show_legend,
            # Top-left: every curve is at or below zero across the strict
            # allowances, so this corner is the one that hides no data.
            legend_position="top_left", legend_cols=4,
            fontsize={"legend": 8}, toolbar=None))

    items = guides(False)
    for draw, dash in DRAWS.items():
        if draw not in m["edge"]:
            continue
        xs, ys = m["edge"][draw]
        items.append(hv.Curve((xs, ys), label=draw).opts(
            color=INK, line_dash=dash, line_width=2.2))
        items.append(hv.Scatter((xs, ys)).opts(
            color=INK, size=5, line_color=None))
    panels.append(hv.Overlay(items).opts(
        width=width, height=310, show_grid=True, xticks=ticks,
        xlabel="crowded allowance — mean F1 a gap may cost on the crowded recordings",
        ylabel="C · at the 30 s grid edge (of 32 selections)",
        xlim=(-0.4, n - 0.6), ylim=(-1.5, 34),
        legend_position="top_left", fontsize={"legend": 8}, toolbar=None))

    return hv.Layout(panels).cols(1).opts(shared_axes=False, toolbar=None)


def header_html(m: dict) -> str:
    return f"""
<div style="font-family:-apple-system,Segoe UI,sans-serif;max-width:{1240}px;
            color:#16202b;line-height:1.45">
<p><b>Figure 1. The crowded allowance, swept.</b> <b>F1</b> is the harmonic mean of
recall and precision; <b>ΔF1</b> the held-out mean F1 of a learned detector (a
&ldquo;net&rdquo;) minus CoactDetect's on the same outer folds, so <b>negative is
CoactDetect ahead</b>. The <b>crowded allowance</b> is how much mean F1 a wider merge
gap may cost on the crowded recordings before goal 1's move rule refuses it; the run
used <b>0.02</b>, marked by the dashed vertical guide. <b>Ungated</b> picks the gap on
F1 alone, <b>gated</b> picks gap and threshold together under the shared rate budget.
Solid is the original seed draw, dashed the replicate. The replicate stops at 0.02
going left: its three strict rows need crowded scores the 2026-09-18 run never
cached, and topping them up is a loop that had not converged when this was drawn.</p>
<p><b>Panel C is the one that constrains the other two.</b> Every verdict that flips
does so at an allowance where the chosen gap is pinned at 30 s, the top of the grid
(<code>gaps_sec</code> ends there). At 0.10 that is 1 selection of 32; at 0.15, 19;
at 0.25 and looser, all 32. A flip measured with the search sitting on the edge of
its own grid says the grid ended, not that a better gap was found.</p>
</div>"""


def _render_png(html_path: Path, png_path: Path, *, wait_ms: int = 2500,
                width: int = 1400, height: int = 900) -> bool:
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
    p.add_argument("--sweep", type=Path, required=True,
                   help="folder holding sweep_summary.json")
    p.add_argument("--width", type=int, default=1140)
    p.add_argument("--out", default=None,
                   help="destination; defaults to the darkroom")
    p.add_argument("--also", type=Path, default=None,
                   help="second destination, e.g. the run record")
    p.add_argument("--no-png", dest="png", action="store_false", default=True)
    a = p.parse_args()

    m = read(a.sweep)
    print(f"allowances: {', '.join(m['labels'])}")
    for draw, (xs, ys) in m["edge"].items():
        pairs = ", ".join(f"{m['labels'][x]}={y}" for x, y in zip(xs, ys))
        print(f"  at grid edge, {draw}: {pairs}")

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
