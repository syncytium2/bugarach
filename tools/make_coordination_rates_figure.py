#!/usr/bin/env python3
"""What the cumulant estimator can be trusted for, and what it would move if adopted.

    python tools/make_coordination_rates_figure.py --record docs/learned/runs/2026-09-23-coordination-rates --also <dir>

Figure id `coordination_rates`, the same on every machine.

Reads `coordination_rates.json` from `tools/measure_coordination_rates.py`.

**Panel A** is the calibration: the median relative error in each cell's coordinated
share, on simulated recordings where the planted participants are known, against the
counting window. The shaded band is the tool's own +/-0.25 tolerance, and `passed` is
decided on this quantity alone. **Panel B** is what adoption would move: the bench's
current per-cell rate against the measured background rate (raw minus the coordinated
share), for both streams at all three levels.

Panel A is the one that decides how much of Panel B is usable. Fast clears the
tolerance at the 1 s window and at no other, and its 2 s neighbour misses by nearly
half; slow clears it at every window. So the fast numbers hold at exactly the window
they were measured at, with no margin either side.

**This measures and adopts nothing.** No bench constant moves here — the adoption is a
separate PR that has to follow WSMIP065's constants PR.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

FIGURE_ID = "coordination_rates"

INK = "#16202b"
GUIDE = "#9a9a9a"
BAND = "#cfd8e3"
STREAM_INK = {"fast": "#1f6fb4", "slow": "#d55e00", "combined": "#2e8b57"}
MODEL_DASH = {"fixed": "solid", "binomial": "dashed"}

#: The bench's current per-cell rates, the thing Panel B would move.
BENCH = {
    "fast": {"quiet": 0.0052, "busy": 0.019, "probe": 0.06},
    "slow": {"quiet": 0.0030, "busy": 0.0113, "probe": 0.032},
}
LEVELS = ("quiet", "busy", "probe")


def read(folder: Path) -> dict:
    d = json.loads((folder / "coordination_rates.json").read_text())
    tol = d["cal_tolerance"]

    cal = {}
    for stream, cases in d["calibration"].items():
        for case, v in cases.items():
            model, _, w = case.partition("@")
            cal.setdefault((stream, model), []).append(
                (float(w), v["share_rel_error_median"], v["passed"]))
    for key in cal:
        cal[key].sort()

    primary = d["primary_window_sec"]
    measured, usable = {}, {}
    for stream in ("fast", "slow"):
        by_w = d["streams"][stream]["by_window"]
        row = by_w[str(primary)] if str(primary) in by_w else by_w[primary]
        fixed = row["fixed"]
        usable[stream] = row.get("recordings_shape_usable", row["recordings"])
        measured[stream] = {
            "quiet": fixed["quiet_background_hz"],
            "busy": fixed["busy_background_hz"],
            "probe": fixed["probe_background_hz"],
            "quiet_raw": row["quiet_raw_hz"],
            "busy_raw": row["busy_raw_hz"],
            "probe_raw": row["probe_raw_hz"],
        }
    return {"cal": cal, "tol": tol, "measured": measured, "usable": usable,
            "primary": primary, "windows": d["windows_sec"],
            "dataset": d["dataset"], "surrogates": d["surrogates"],
            "probe_pct": d["probe_percentile"], "stretch": d["stretch_sec"]}


def build(m: dict, width: int):
    import holoviews as hv

    tol = m["tol"]
    items = [
        hv.Area((m["windows"], [-tol] * len(m["windows"]), [tol] * len(m["windows"])),
                vdims=["y", "y2"]).opts(color=BAND, line_alpha=0, alpha=0.55),
        hv.HLine(0.0).opts(color=GUIDE, line_dash="dotted", line_width=1.2),
    ]
    for (stream, model), rows in sorted(m["cal"].items()):
        xs = [r[0] for r in rows]
        ys = [r[1] for r in rows]
        items.append(hv.Curve((xs, ys), label=f"{stream} · {model}").opts(
            color=STREAM_INK[stream], line_dash=MODEL_DASH[model], line_width=2.2))
        # A filled dot passed, a hollow one failed.
        for x, y, ok in rows:
            items.append(hv.Scatter(([x], [y])).opts(
                color=STREAM_INK[stream] if ok else "#ffffff", size=9,
                line_color=STREAM_INK[stream], line_width=2))
    panel_a = hv.Overlay(items).opts(
        width=width, height=330, show_grid=True,
        xlabel="counting window (s)",
        ylabel="A · median relative error in coordinated share",
        xticks=[(w, f"{w:g} s") for w in m["windows"]],
        xlim=(0.7, 4.3), legend_position="top_left", legend_cols=2,
        fontsize={"legend": 8}, toolbar=None)

    cats, ticks = [], []
    for i, stream in enumerate(("fast", "slow")):
        for j, level in enumerate(LEVELS):
            x = i * 4 + j
            cats.append((x, stream, level))
            ticks.append((x, f"{stream}\n{level}"))
    bitems = []
    for x, stream, level in cats:
        b = BENCH[stream][level]
        raw = m["measured"][stream][level + "_raw"]
        g = m["measured"][stream][level]
        bitems.append(hv.Curve(([x, x], [b, g])).opts(color=GUIDE, line_width=1.6))
        # Three marks: what the bench holds, what this run measures raw on the bench's own
        # recording set, and what subtracting the coordinated share would leave.
        bitems.append(hv.Scatter(([x], [b])).opts(
            color="#ffffff", line_color=INK, line_width=2, size=13))
        bitems.append(hv.Scatter(([x], [raw])).opts(
            color=GUIDE, size=6, line_color=None, marker="square"))
        bitems.append(hv.Scatter(([x], [g])).opts(
            color=STREAM_INK[stream], size=10, line_color=None))
    panel_b = hv.Overlay(bitems).opts(
        width=width, height=360, show_grid=True, xticks=ticks,
        xlabel="", ylabel="B · per-cell event rate (Hz), log scale",
        logy=True, xlim=(-0.7, 6.7), toolbar=None, show_legend=False)

    return hv.Layout([panel_a, panel_b]).cols(1).opts(shared_axes=False, toolbar=None)


def header_html(m: dict) -> str:
    fast = m["measured"]["fast"]
    slow = m["measured"]["slow"]
    return f"""
<div style="font-family:-apple-system,Segoe UI,sans-serif;max-width:1240px;
            color:#16202b;line-height:1.45">
<p><b>Figure 1. What the estimator can carry, and what it would move.</b> Measured on
{m['dataset']['recordings']} baseline recordings of
<code>{m['dataset']['name']}</code>, {m['surrogates']} surrogate draws per recording.
The <b>coordinated share</b> is the part of a cell's own firing rate that belongs to
moments shared with other cells; the <b>background rate</b> is its total rate minus
that share. <b>Fixed</b> and <b>binomial</b> are the two models that bracket how many
cells join a shared moment — pairs and triples fix the spread, not the mean.</p>
<p><b>Panel A — the calibration, and it is not uniform.</b> Median relative error in the
recovered coordinated share on simulated recordings where the planted participants are
known; the band is the tool's own ±{m['tol']:.2f} tolerance, and its <code>passed</code>
flag is decided on this quantity alone. Filled dots cleared it, hollow ones did not.
<b>Slow clears every window; fast clears only {m['primary']:g} s</b>, missing by +0.46 at
2 s and +1.00 at 4 s. Fast's binomial case at {m['primary']:g} s clears by 0.002. So the
fast numbers hold at exactly the window they were measured at, with no margin either
side, and the slow ones travel.</p>
<p><b>Panel B — what adoption would move</b>, log scale. Three marks per column: the bench's
current value (hollow), this run's <b>raw</b> rate (small grey square) and the
<b>background</b> rate it proposes (filled). Quiet and busy are measured on the bench's own
recording set — the {m['usable']['fast']} of {m['dataset']['recordings']} fast recordings
(and {m['usable']['slow']} slow) that clear <code>fit_background_shape</code>'s floors,
which is the set <code>remeasure_bench.py</code> used to set <code>bench.REGIMES</code>.</p>
<p><b>The raw rates reproduce the bench, which is the reassuring part</b>: fast quiet
−3.0%, fast busy +0.2%, slow quiet +0.6%, slow busy +0.3%. So the grey square sits on the
hollow circle, and the whole of the proposed change is the coordination subtraction —
<b>quiet and busy fall 13% to 22%</b> — rather than any disagreement about the rate.
<i>An earlier version of this figure measured quiet and busy over all 84 recordings and
reported a 30% fall; that was the two recording sets differing, not a measurement.</i></p>
<p><b>The probes are the exception, and they split.</b> Raw → background costs fast
<b>−0.6%</b> at the probe against −16.5% at quiet, so fast's busiest stretches are not its
coordinated ones and its <b>+112%</b> is purely a change of <i>definition</i> — a measured
{m['probe_pct']:g}th percentile of {m['stretch']:g}-second stretches in place of a chosen
multiple of the median. Slow's costs <b>−35.9%</b>: its busiest stretches <i>are</i> its
coordinated ones, and its small net −9% is two large opposite moves cancelling. Slow is
also the stream whose ungated calibration terms are weakest (moment rate −22.8%), so that
36% is the number to check before anything rests on it.</p>
</div>"""


def _render_png(html_path: Path, png_path: Path, *, wait_ms: int = 2500,
                width: int = 1400, height: int = 1120) -> bool:
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
    p.add_argument("--record", type=Path, required=True,
                   help="folder holding coordination_rates.json")
    p.add_argument("--width", type=int, default=1140)
    p.add_argument("--out", default=None, help="destination; defaults to the darkroom")
    p.add_argument("--also", type=Path, default=None, help="second destination")
    p.add_argument("--no-png", dest="png", action="store_false", default=True)
    a = p.parse_args()

    m = read(a.record)
    for (stream, model), rows in sorted(m["cal"].items()):
        cells = " ".join(f"{w:g}s={e:+.3f}{'' if ok else '*'}" for w, e, ok in rows)
        print(f"  {stream:<9} {model:<9} {cells}   (* = outside tolerance)")

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
