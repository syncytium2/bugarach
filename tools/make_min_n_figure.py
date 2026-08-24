#!/usr/bin/env python3
"""SPIKE-synch's `min_n` floor against the participant count it reads as.

    python tools/make_min_n_figure.py --also docs/learned

Figure id `sync_min_n`, the same on every machine.

**The floor and the participant count are two different numbers, and the detector
computes both.** `min_n` gates on `ev_sum` — the sum, over an event's bins, of
`Cn`, where `Cn` is the size of the same-time group that LAST wrote to that bin.
`n_participating_rois` is the count of distinct ROIs with an event inside the
detected span. The first is what the floor uses; the second is what "a coordinated
event needs at least 3 ROIs" means, and it is already sitting in the result object,
computed for the artifact test.

They come apart two ways, both visible here:

1. **An ROI firing in several bins of one event contributes several times.**
2. **Within a bin only the last same-time group survives the binning**, so earlier
   simultaneous groups are dropped from the number entirely.

Thomas Kreuz, by email to Tony in April 2026, on his own lab's detection layer for
this profile: they added *"a quite sophisticated postprocessing where we made sure
that no event contains more than one spike from the same pixel (which was
essential for the new method proposed in Ref. 47)"*. This figure is that rule's
absence, measured.

**This measures; it changes nothing.** `min_n` as it stands is what the MATLAB
does, parity is the product, and any change lands behind a flag (`docs/forks.md`
#1). The point is to know the size of the gap before arguing about it.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np

FIGURE_ID = "sync_min_n"

QUIET_C = "#1f6fb4"
BUSY_C = "#b03a48"
GUIDE = "#9a9a9a"
INK = "#16202b"

#: The shipped default, and the number a reader takes to mean "at least this many
#: ROIs took part".
MIN_N = 3

SEEDS = tuple(range(1, 13))
REGIMES = ("baseline_quiet", "baseline_busy")


def measure(regime: str, seeds=SEEDS) -> dict:
    """Per detected event: what the floor gated on, and how many ROIs took part."""
    from bugarach.bench import OPERATING_POINTS, make_recording, run_detector

    gated, distinct = [], []
    for seed in seeds:
        sl, _gt = make_recording(regime, seed)
        trains = [np.asarray(v) for v in sl.streams["events"].t50rise]
        # THROUGH `run_detector`, not by hand. The first version of this tool
        # passed `ext=(0.0, 2700.0)` — the nominal duration — where the detector
        # is given `recording_extent(s)`, which is the span of the events
        # themselves and on seed 1 is (0.3, 2692.8). Close enough to look right
        # and different enough to move the counts: 5 events below the floor
        # became 7. The bench has one way to run a detector at its operating
        # point; a figure about the bench uses it.
        det = run_detector("sync", sl, min_n=MIN_N)
        assert det.settings["tau_max"] == OPERATING_POINTS["sync"].params["tau_max"]
        # the quantity the floor gated on, recomputed from the bins it kept
        gated.append(np.array([det.Cn[(det.Cx >= b) & (det.Cx <= e)].sum()
                               for b, e in zip(det.locs, det.ends)]))
        distinct.append(np.asarray(det.n_participating_rois))
    g = np.concatenate(gated) if gated else np.empty(0)
    d = np.concatenate(distinct) if distinct else np.empty(0)
    return dict(regime=regime, gated=g, distinct=d,
                n=g.size, inflated=int((g > d).sum()),
                under=int((d < MIN_N).sum()),
                singles=int((d <= 1).sum()))


def build(stats: list[dict], width: int):
    import holoviews as hv

    panels = []
    for s in stats:
        colour = QUIET_C if s["regime"].endswith("quiet") else BUSY_C
        # jitter both axes: these are small integers and points land on top of
        # one another, which would hide the count that matters
        rng = np.random.RandomState(0)
        jx = s["gated"] + rng.uniform(-0.18, 0.18, s["gated"].size)
        jy = s["distinct"] + rng.uniform(-0.18, 0.18, s["distinct"].size)
        lo, hi = 0, max(12, int(s["gated"].max()) + 1)

        unity = hv.Curve(([lo, hi], [lo, hi])).opts(
            color=GUIDE, line_dash="dotted", line_width=1)
        floor_h = hv.HLine(MIN_N).opts(color=GUIDE, line_dash="dashed",
                                       line_width=1)
        floor_v = hv.VLine(MIN_N).opts(color=INK, line_width=1.5)
        pts = hv.Scatter((jx, jy)).opts(
            color=colour, size=5, alpha=0.55, line_color=None)
        bad = s["distinct"] < MIN_N
        flagged = hv.Scatter((jx[bad], jy[bad])).opts(
            color=BUSY_C, size=9, alpha=0.95, line_color=INK, line_width=0.8)

        pct = 100.0 * s["under"] / max(s["n"], 1)
        short = s["regime"].replace("baseline_", "")
        panels.append((unity * floor_h * floor_v * pts * flagged).opts(
            width=width // 2, height=380,
            xlabel="min_n gated on this — sum of Cn over the event's bins",
            ylabel=f"distinct ROIs · {short} ({s['under']}/{s['n']} below, {pct:.0f}%)",
            xlim=(lo, hi),
            # -0.6 so a single-ROI event is a visible point, not a sliver on the
            # frame: those are the ones the figure exists to show
            ylim=(-0.6, max(12, int(s["distinct"].max()) + 1)),
            fontsize={"xlabel": "9pt", "ylabel": "9pt", "ticks": "8pt"},
            show_legend=False, toolbar=None))
    return hv.Layout(panels).cols(2).opts(shared_axes=False)


def header_html(stats: list[dict]) -> str:
    rows = "".join(
        f"<tr><td style='padding:2px 14px 2px 0'>{s['regime']}</td>"
        f"<td style='padding:2px 14px 2px 0;text-align:right'>{s['n']}</td>"
        f"<td style='padding:2px 14px 2px 0;text-align:right'>{s['inflated']}</td>"
        f"<td style='padding:2px 14px 2px 0;text-align:right'><b>{s['under']}</b></td>"
        f"<td style='padding:2px 0;text-align:right'>{s['singles']}</td></tr>"
        for s in stats)
    return f"""
<div style="font:13px/1.5 -apple-system,Segoe UI,sans-serif;color:#16202b;
            max-width:56rem;margin:0 auto 0.5rem">
<p><b>SPIKE-synch's floor does not count participants.</b> <code>min_n</code>
gates on the sum of <code>Cn</code> across an event's bins; the detector separately
computes <code>n_participating_rois</code>, the distinct ROIs inside the detected
span, and uses it only for the artifact test. Points below the dashed line are
events reported as coordinated with fewer than {MIN_N} ROIs in them — the floor
passed them and a participant count would not have. The dotted diagonal is where
the two numbers would agree.</p>
<table style="border-collapse:collapse;font-size:12px">
<tr style="border-bottom:1px solid #c8d6e4">
  <th style="text-align:left;padding-right:14px">regime</th>
  <th style="text-align:right;padding-right:14px">events</th>
  <th style="text-align:right;padding-right:14px">gated &gt; participants</th>
  <th style="text-align:right;padding-right:14px">below the floor</th>
  <th style="text-align:right">single-ROI</th></tr>
{rows}
</table>
<p style="color:#5c6773">12 seeds per regime, the bench recording, SPIKE-synch at
its benched operating point. Nothing is changed by this figure: <code>min_n</code>
is what the MATLAB does and parity is the product.</p>
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
            pg.screenshot(path=str(png_path), full_page=False)
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

    stats = [measure(r) for r in REGIMES]
    for s in stats:
        print(f"{s['regime']:<16} {s['n']:>4} events · "
              f"{s['inflated']:>3} gated above their participant count · "
              f"{s['under']:>3} below the floor · {s['singles']} single-ROI")

    from bugarach.paths import darkroom, unresolved_message
    dest = Path(a.out) if a.out else darkroom()
    if dest is None:
        print(unresolved_message(), file=sys.stderr)
        return 1

    import holoviews as hv
    import panel as pn
    hv.extension("bokeh")
    layout = build(stats, a.width)

    dests = [dest] + ([a.also] if a.also else [])
    for i, d in enumerate(dests):
        d.mkdir(parents=True, exist_ok=True)
        html = d / f"{FIGURE_ID}.html"
        pn.panel(pn.Column(pn.pane.HTML(header_html(stats)),
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
