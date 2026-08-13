#!/usr/bin/env python3
"""Render what each generator parameter actually does to the data.

    python tools/make_generator_figures.py                  # every parameter
    python tools/make_generator_figures.py --param jitter_sec
    python tools/make_generator_figures.py --out ./somewhere

One PNG per parameter: the same recording generated at three or four values of
that knob, rasters stacked and x-linked, everything else held. Planted event
times are ticked along the top of each row, so "did the structure change or did
only the background change" is answerable by looking.

These exist because the generator's parameters are the experiment's assumptions.
``docs/simulation_plan.md`` §5 records what it cost to get two of them wrong —
event spacing that put four coordinated events inside every null window, and
made-up timescales that survived two rebuilds because nobody had a picture of
what they implied. A knob whose effect you cannot see is a knob you are guessing
at.

Destination is ``$BUGARACH_DARKROOM`` (see ``bugarach.paths``), never hardcoded:
that path carries a person's name and this repo is public. With the variable
unset, pass ``--out``.
"""

from __future__ import annotations

import argparse
import os
import sys
import tempfile
from pathlib import Path

import numpy as np

# Each entry: the values swept, a one-line note on what the reader should see,
# and any base-recording overrides that value range needs to be legible.
SWEEPS: dict[str, dict] = {
    "bg_rate_hz": dict(
        values=(0.02, 0.05, 0.15, 0.40),
        note="per-ROI background firing. The planted events are identical in "
             "all four rows — only how well they stand out changes. This is the "
             "sparse/dense regime axis the bench shifts along.",
    ),
    "jitter_sec": dict(
        values=(0.0, 0.05, 0.5, 2.0),
        note="SD of participant onset jitter — how tightly the participating "
             "ROIs fire together. 0 is a perfect vertical stripe; by 2 s the "
             "event is a smear no coincidence detector can bind.",
    ),
    "interval_cv": dict(
        values=(0.0, 0.5, 1.0, 2.0),
        note="irregularity of the gaps between events. 0 is metronomic and is a "
             "cue a model can learn instead of learning coordination; 1 is "
             "Poisson-like above the floor; >1 is bursty.",
    ),
    "min_sep_sec": dict(
        values=(15.0, 60.0, 120.0, 300.0),
        base=dict(duration_sec=3600.0),
        note="the spacing floor, and the contaminated-null axis. Detectors "
             "estimate their null over context windows up to 120 s: at 15 s "
             "several coordinated events sit inside every window, so the "
             "surrogate 'null' contains the signal and the threshold inflates.",
    ),
    "participation": dict(
        values=(1.0, 0.75, 0.5, 0.25),
        note="fraction of ROIs recruited into each event, one value per row "
             "(elsewhere the generator interleaves all three). The participant "
             "floor: somewhere down this axis every detector stops seeing it.",
    ),
    "hot_rate_hz": dict(
        values=(0.0, 0.1, 0.3, 0.6),
        base=dict(hot_window=(240.0, 420.0), ramp_sec=30.0),
        note="the promiscuity probe — a dense-but-random block (shaded) with "
             "NO planted events, ramping in rather than stepping. A detector "
             "keyed on rate fires here; one keyed on coordination does not.",
    ),
    "n_distractors": dict(
        values=(0, 3, 6, 12),
        base=dict(distractor_frac=0.5),
        note="correlated population bursts: real cross-ROI coincidence that is "
             "not a coordinated event. They look like events in the raster on "
             "purpose — they are the negatives that separate 'found "
             "coordination' from 'found something happening at once'.",
    ),
    "grid_sec": dict(
        values=(0.0, 0.1, 0.5, 2.0),
        note="quantization onto the imaging grid. 0 is continuous time; coarse "
             "grids collapse jitter into lockstep, which flatters any detector "
             "binning at the same scale.",
    ),
    "n_roi": dict(
        values=(10, 30, 60, 120),
        note="population size. Participation is a fraction, so the absolute "
             "number of co-firing ROIs scales with this — and every detector "
             "with a min_rois floor has an implicit opinion about it.",
    ),
}

BASE = dict(
    duration_sec=600.0,
    n_roi=30,
    bg_rate_hz=0.05,
    participation=(1.0, 0.75, 0.50),
    n_per_level=(2, 2, 2),
    jitter_sec=0.05,
    min_sep_sec=15.0,
    interval_cv=1.0,
)


def _row(param, value, base, seed):
    """One recording at one value of one parameter."""
    from bugarach.simulate import simulate_coordination

    kw = {**BASE, **base}
    if param == "participation":
        # a single level, so the row shows that recruitment fraction alone
        kw["participation"] = (value,)
        kw["n_per_level"] = (6,)
    elif param == "n_distractors":
        kw["n_distractors"] = value
    else:
        kw[param] = value
    return simulate_coordination(seed=seed, **kw)


def build(param: str, seed: int, width: int):
    import holoviews as hv

    from bugarach.ui.app import _time_axis_hook
    from bugarach.ui.diagnostic import raster_panel

    spec = SWEEPS[param]
    rows = []
    for value in spec["values"]:
        s, gt = _row(param, value, spec.get("base", {}), seed)
        n_roi = s.streams["events"].n_rois
        ext = (0.0, {**BASE, **spec.get("base", {})}["duration_sec"])
        # highlight the onsets belonging to planted events. raster_panel's
        # member highlighting normally answers "what did this detector claim";
        # here there is no detector, and the question is "what did the generator
        # plant" — without this every onset renders muted grey and the figure
        # shows a uniform wash whatever the knob is set to.
        pad = max(3.0 * float(gt.params.get("jitter_sec", 0.05)), 0.5)
        planted_spans = [(t - pad, t + pad) for t in gt.times]
        panel = raster_panel(s.streams["events"], ext=ext, gt=gt,
                             member_spans=planted_spans,
                             name=f"{param}={value:g}", width=width, height=170)
        # planted times ticked along the top: the structure, separate from the
        # background it is buried in
        if len(gt.times):
            panel = panel * hv.Scatter(
                (gt.times, np.full(gt.times.size, n_roi - 0.5)),
                kdims=["t"], vdims=["roi"]).opts(
                marker="triangle", size=7, color="#1b7f3b", alpha=0.9)
        # opts go on AFTER the overlay, not before: overlaying returns a new
        # element whose options are its own, so a width/ylabel/hook set on the
        # raster is silently dropped. First render of this figure came out a
        # quarter as wide, labelled "roi", with the time axis in raw seconds
        # instead of the 60-base ticks CLAUDE.md requires — all three the same
        # mistake.
        rows.append(panel.opts(
            width=width, height=170, xlim=ext, ylim=(-1, n_roi), xaxis=None,
            ylabel=f"{param}={value:g}", xlabel="", title="",
            fontsize={"ylabel": "10pt"}, show_legend=False,
            hooks=[_time_axis_hook]))
    rows[-1] = rows[-1].opts(height=198, xaxis="bottom")

    layout = rows[0]
    for r in rows[1:]:
        layout = layout + r
    return layout.cols(1).opts(shared_axes=True, merge_tools=True)


def main(argv=None):
    p = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--param", choices=sorted(SWEEPS), default=None,
                   help="one parameter; default renders all of them")
    p.add_argument("--seed", type=int, default=5)
    p.add_argument("--width", type=int, default=1000)
    p.add_argument("--out", default=None,
                   help="destination directory; default $BUGARACH_DARKROOM")
    p.add_argument("--no-png", dest="png", action="store_false", default=True)
    args = p.parse_args(argv)

    from bugarach.paths import ENV_VAR, darkroom

    if args.out:
        dest = Path(args.out).expanduser()
        dest.mkdir(parents=True, exist_ok=True)
    else:
        dest = darkroom()
        if dest is None:
            print(f"{ENV_VAR} is not set and --out was not given — writing "
                  "nothing rather than guessing a destination.", file=sys.stderr)
            return 2
        dest = dest / "generator"
        dest.mkdir(parents=True, exist_ok=True)

    import holoviews as hv
    import panel as pn

    hv.extension("bokeh")

    params = [args.param] if args.param else sorted(SWEEPS)
    for param in params:
        fig = build(param, args.seed, args.width)
        note = SWEEPS[param]["note"]
        page = pn.Column(
            pn.pane.HTML(
                f'<div style="font:13px/1.6 system-ui,sans-serif;max-width:1000px">'
                f'<b style="font-size:15px">{param}</b> — {note}<br>'
                f'<span style="color:#555">Everything else held. '
                f'<span style="color:#1b7f3b">▲</span> planted event times · '
                f'seed {args.seed}.</span></div>'),
            pn.pane.HoloViews(fig))
        _write(page, dest, f"generator_{param}", args.png)
    return 0


def _write(page, dest: Path, stem: str, png: bool):
    """Write to a temporary name and move into place — the darkroom README
    records 188 MB of hash-named orphans from writing into Dropbox in place."""
    with tempfile.TemporaryDirectory() as td:
        tmp_html = Path(td) / "page.html"
        page.save(str(tmp_html))
        html = dest / f"{stem}.html"
        os.replace(tmp_html, html)
    print(f"wrote {html}")
    if png:
        shot = dest / f"{stem}.png"
        if _render_png(html, shot):
            print(f"      {shot}")
        else:
            print("      (PNG skipped — needs playwright chromium)",
                  file=sys.stderr)


def _render_png(html_path: Path, png_path: Path, *, wait_ms: int = 3000) -> bool:
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        return False
    try:
        with sync_playwright() as pw:
            browser = pw.chromium.launch()
            page = browser.new_page(viewport={"width": 1120, "height": 1200},
                                   device_scale_factor=2)
            page.goto(html_path.as_uri())
            page.wait_for_timeout(wait_ms)
            with tempfile.TemporaryDirectory() as td:
                tmp = Path(td) / "shot.png"
                page.screenshot(path=str(tmp), full_page=True)
                browser.close()
                os.replace(tmp, png_path)
        return True
    except Exception:                                  # noqa: BLE001
        return False


if __name__ == "__main__":
    raise SystemExit(main())
