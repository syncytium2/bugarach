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
        values=(0.0019, 0.0038, 0.0096, 0.0175, 0.0350),
        note="per-ROI background rate, in Hz. The middle three are the "
             "untreated interquartile range and its median — the bench runs "
             "from 0.0038 to 0.0175. The same planted structure is in every "
             "row; only how far it stands out changes. (Event TIMES do shift "
             "between rows: the background draw consumes RNG, so the schedule "
             "redraws. Compare structure, not event for event.)",
    ),
    "participation": dict(
        values=(0.45, 0.30, 0.18, 0.10),
        note="fraction of ROIs recruited into each event, one value per row. "
             "0.18 is the measured median; the bench plants 0.30 / 0.18 / 0.10 "
             "interleaved. The 0.10 row is about 3 ROIs — at the min_rois floor "
             "the detectors ship with, and below the floor the measurement "
             "itself was taken at, so it is a stress point, not a calibration.",
    ),
    "jitter_sec": dict(
        values=(0.0, 0.10, 0.36, 1.00),
        note="SD of participant onset jitter. 0.36 is what the bench uses. "
             "WARNING: it comes from a statistic whose own surrogate null is "
             "0.42, so most of it is the width of the measurement's gather "
             "window rather than coordination tightness — an upper bound.",
    ),
    "min_sep_sec": dict(
        values=(15.0, 45.0, 90.0, 200.0),
        base=dict(duration_sec=2400.0, n_per_level=(2, 2, 2)),
        note="the spacing floor. The shaded band on each row is one 120 s "
             "detector context window, drawn to scale: at a 15 s floor several "
             "events fall inside it, so the circular-shift null is built from "
             "data containing the signal and the threshold inflates. That is "
             "the contaminated null, and it is why the bench uses 120 s.",
    ),
    "interval_cv": dict(
        values=(0.0, 0.5, 1.0, 2.0),
        note="irregularity of the gaps between events. 0 is metronomic — a "
             "schedule a model can predict from the clock instead of from the "
             "activity. WARNING: at the bench's own spacing the realized CV is "
             "near zero regardless, because the floor leaves little room above "
             "it.",
    ),
    "hot_rate_hz": dict(
        values=(0.0, 0.02, 0.06, 0.15),
        base=dict(duration_sec=1500.0, hot_window=(500.0, 800.0),
                  ramp_sec=30.0),
        note="the promiscuity probe — extra background inside the shaded block, "
             "with no planted events in it. 0.06 is what the bench uses. A "
             "detector keyed on rate fires here; one keyed on coordination "
             "mostly does not.",
    ),
    "n_distractors": dict(
        values=(0, 3, 6, 12),
        base=dict(distractor_window=(60.0, 820.0)),
        note="correlated population bursts — real cross-ROI coincidence that is "
             "not a coordinated event, marked with an open down-triangle. They "
             "recruit the same fraction of ROIs as a planted event, so they are "
             "genuinely confusable; when they recruited more, every detector "
             "fired on all of them and the control discriminated nothing.",
    ),
    "grid_sec": dict(
        values=(0.0, 0.1, 0.5, 2.0),
        note="quantization onto the imaging grid. Coarse grids collapse jitter "
             "into lockstep, which flatters any detector binning at the same "
             "scale. The effect is sub-pixel at this width — read the row "
             "labels, not the ink.",
    ),
    "n_roi": dict(
        values=(10, 33, 66, 120),
        note="population size; the bench uses 33. Participation is a fraction, "
             "so the absolute number of co-firing ROIs scales with this — and "
             "every detector with a min_rois floor has an implicit opinion "
             "about the population size you set.",
    ),
}

def _base():
    """The bench's own recording, shortened so a sweep row stays legible.

    Every value that is not being swept comes from ``BENCH_RECORDING`` — which is
    calibrated from untreated slices — rather than from a literal here. An
    earlier version hardcoded ``bg_rate_hz=0.05``, ``jitter_sec=0.05``,
    ``participation=(1.0, 0.75, 0.50)`` and ``min_sep_sec=15``: precisely the
    four values the bench documents as measured-wrong. The figures illustrated an
    instrument the project had already disowned, which is a strange thing for a
    document whose thesis is that an unseen knob is a guessed knob.
    """
    from bugarach.bench import BENCH_RECORDING, REGIMES
    keep = ("n_roi", "participation", "jitter_sec", "min_sep_sec",
            "interval_cv", "distractor_frac")
    base = {k: v for k, v in BENCH_RECORDING.items() if k in keep}
    base.update(duration_sec=900.0, n_per_level=(2, 2, 2),
                min_sep_sec=90.0,          # 6 events in 900 s; the floor still binds
                bg_rate_hz=REGIMES["baseline_quiet"]["bg_rate_hz"])
    return base


BASE = _base()


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
        if len(gt.distractors):
            dt = gt.distractor_times
            panel = panel * hv.Scatter(
                (dt, np.full(dt.size, n_roi - 2.0)),
                kdims=["t"], vdims=["roi"]).opts(
                marker="inverted_triangle", size=8, color="#5a5a5a",
                fill_alpha=0.0, line_width=1.4)
        # the context window the contaminated-null argument is about, to scale
        if param == "min_sep_sec":
            panel = hv.VSpan(60.0, 180.0).opts(
                color="#4c78a8", alpha=0.12) * panel
        rows.append(panel.opts(
            width=width, height=170, xlim=ext, ylim=(-1, n_roi), xaxis=None,
            ylabel=f"{param}={value:g} · {n_roi} ROI", xlabel="time",
            title="",
            fontsize={"ylabel": "10pt"}, show_legend=False,
            hooks=[_time_axis_hook]))
    rows[-1] = rows[-1].opts(height=198, xaxis="bottom")

    layout = rows[0]
    for r in rows[1:]:
        layout = layout + r
    # shared_axes=False: linking would override the per-row ylim set above,
    # which flattened the n_roi=10 panel into a sliver on a 0-120 axis. x is
    # already pinned by xlim on every row, so nothing is lost.
    return layout.cols(1).opts(shared_axes=False, merge_tools=True,
                               toolbar=None)


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
            page.goto(html_path.resolve().as_uri())
            page.wait_for_timeout(wait_ms)
            with tempfile.TemporaryDirectory() as td:
                tmp = Path(td) / "shot.png"
                # Clip to the ink, not the viewport. A full_page screenshot of
                # a short page pads to the viewport height, and body's own box
                # is the viewport too — so measure the lowest rendered element
                # and cut there. Roughly a third of every figure was blank
                # canvas before this, which pushed the raster rows smaller than
                # they needed to be.
                # exclude the containers themselves: Panel gives body/html
                # height:100%, so their own box reports the viewport and would
                # dominate the max, measuring exactly the thing we are cutting.
                h = page.evaluate(
                    "Math.ceil(Math.max(...Array.from("
                    "document.body.querySelectorAll('canvas, .bk-Canvas, div'))"
                    ".filter(e => e.offsetHeight > 0 && e.offsetHeight < 1100)"
                    ".map(e => e.getBoundingClientRect().bottom)))")
                w = page.evaluate(
                    "Math.ceil(Math.max(...Array.from("
                    "document.body.querySelectorAll('canvas, .bk-Canvas, div'))"
                    ".filter(e => e.offsetWidth > 0 && e.offsetWidth < 1119)"
                    ".map(e => e.getBoundingClientRect().right)))")
                page.screenshot(path=str(tmp), clip={
                    "x": 0, "y": 0,
                    "width": min(float(w) + 12, 1120.0),
                    "height": min(float(h) + 12, 1200.0)})
                browser.close()
                os.replace(tmp, png_path)
        return True
    except Exception as exc:                           # noqa: BLE001
        # print it: the sibling tool does, and this copy's silence let a
        # relative --out fail for months while claiming chromium was missing.
        print(f"      PNG render failed: {type(exc).__name__}: {exc}",
              file=sys.stderr)
        return False


if __name__ == "__main__":
    raise SystemExit(main())
