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
made-up timescales that survived a rebuild because nobody had a picture of
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
        # Re-derived 2026-08-20 with bench.REGIMES: the middle three are p25,
        # median and p75 of slice-mean per-ROI rate on the EXPORT FOLDER, the
        # export folder the lab approved. The outer two stay at half p25 and twice p75.
        values=(0.0026, 0.0052, 0.0102, 0.0190, 0.0380),
        note="per-ROI background rate, in Hz. The middle three are the "
             "untreated interquartile range and its median — the bench runs "
             "from 0.0052 to 0.0190. The same planted structure is in every "
             "row; only how far it stands out changes. (Event TIMES do shift "
             "between rows: the background draw consumes RNG, so the schedule "
             "redraws. Compare structure, not event for event.)",
    ),
    "bg_rate_shape": dict(
        values=(None, 4.0, 1.0, 0.275),
        note="how unevenly the background is spread across ROIs. The top row is "
             "None — every ROI at the same rate, which is what this generator "
             "did for its whole life. Below it each ROI draws its own rate from "
             "a Gamma of that shape, with the MEAN held at bg_rate_hz, so what "
             "changes down the rows is the spread and nothing else. 0.275 is "
             "the value fitted to 81 real baseline windows "
             "(bench.MEASURED_RATE_SHAPE): most ROIs nearly silent, a few "
             "carrying the recording. The rows go from an even speckle to a "
             "field with empty lanes and dense ones, and the real recordings "
             "look like the bottom row.",
    ),
    "bg_burst_shape": dict(
        values=(None, 1.388, (1.547, 1.388)),
        base=dict(bg_rate_shape=0.275, duration_sec=1800.0, n_per_level=(3, 3, 3),
                  min_sep_sec=120.0),
        note="whether an ROI's own events clump in TIME. Rows share a background "
             "that is already uneven across ROIs (bg_rate_shape=0.275), so what "
             "changes is only how each ROI spends its events. Top: a constant "
             "rate, evenly spread. Middle: one scale, 60 s bins. Bottom: two "
             "scales, 300 s and 60 s, which is what real windows need — their "
             "variance/mean keeps rising with the window (1.8 at 30 s, 2.6 at "
             "60 s, 3.9 at 120 s, 5.7 at 300 s), and independent bins stop "
             "growing once you look wider than the bin. Watch the busy ROIs "
             "gather into stretches instead of ticking steadily.",
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
             "activity. At the bench's own spacing the knob still works but is "
             "compressed: 0 / 0.5 / 1.0 / 2.0 realize about 0.00 / 0.06 / 0.10 "
             "/ 0.20, because the floor leaves little room above it.",
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


def _vlabel(param, value):
    """``param=value`` for a row label.

    ``None`` is a legitimate value for a knob whose "off" is itself the thing
    being compared against — ``bg_rate_shape=None`` is the flat field — and
    ``:g`` cannot format it. A knob may also take a SEQUENCE, when it names more
    than one scale.
    """
    if value is None:
        return f"{param}=None"
    if isinstance(value, (tuple, list)):
        return f"{param}=({', '.join(format(v, 'g') for v in value)})"
    return f"{param}={value:g}"


#: Longest y-label a 196 px row can set rotated before the ends are cut off with
#: no error. Measured off the render, not guessed: at 34 characters the label
#: fits, at 38 the tail goes. A multi-scale value like
#: ``bg_burst_shape=(1.547, 1.388)`` is already 30 before the ROI count is added.
_YLABEL_MAX = 34


def _ylabel(param, value, n_roi):
    """Row label, dropping the ROI count when the value itself is long.

    Every row of a figure carries the same ROI count, and the header states it —
    so it is the part that can go. Losing the tail of the VALUE would leave a row
    labelled with a number that is not the one it was drawn at.
    """
    label = _vlabel(param, value)
    with_count = f"{label} · {n_roi} ROI"
    return with_count if len(with_count) <= _YLABEL_MAX else label


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
    elif param == "bg_burst_shape":
        # The bins travel with the shapes: one shape is one scale at 60 s, a pair
        # is the 300/60 s pair they were fitted at. Setting shapes without
        # matching bins is an error the generator refuses, correctly.
        kw["bg_burst_shape"] = value
        if isinstance(value, (tuple, list)):
            kw["bg_burst_bin_sec"] = (300.0, 60.0)[-len(value):]
        elif value is not None:
            kw["bg_burst_bin_sec"] = 60.0
    else:
        kw[param] = value
    return simulate_coordination(seed=seed, **kw)


# 196 px rows, not 170: at the tighter height the per-row y-labels abutted
# each other and the bottom one clipped ("min_sep_sec=200 · 33 RO"). Found by
# zoom-cropping the render — an ink-box check cannot see a label collided
# with by its neighbour rather than by the page edge.
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
        # Every onset draws the same. This used to ink the ones inside a planted
        # event, which made the structure easy to see and also drew it for the
        # reader: the ink came from the ground truth, so a setting that planted
        # something no detector could recover still produced tidy inked columns.
        # The participation figure is the case in point — at 0.10 the bottom row
        # now looks nearly structureless, which is the honest rendering of a
        # stress point below the detectors' own min_rois floor. Planted times are
        # ticked along the top, to be compared against an unmarked raster.
        panel = raster_panel(s.streams["events"], ext=ext, gt=gt,
                             name=_vlabel(param, value),
                             width=width, height=170)
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
            width=width, height=196, xlim=ext, ylim=(-1, n_roi), xaxis=None,
            ylabel=_ylabel(param, value, n_roi), xlabel="time",
            title="",
            fontsize={"ylabel": "10pt"}, show_legend=False,
            hooks=[_time_axis_hook]))
    # The bottom row is the only one carrying an x-axis, and an axis with tick
    # labels and a title costs about 45 px. Giving it +2 spends that out of the
    # PLOT area instead: its raster is squashed relative to every row above, and
    # its rotated y-label — laid out against the shorter plot — is silently
    # clipped ("… · 33 R"). Match the plot areas by paying for the axis in
    # addition to the row height, per the project's plot conventions.
    rows[-1] = rows[-1].opts(height=196 + 45, xaxis="bottom")

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

    from bugarach.paths import darkroom, unresolved_message

    if args.out:
        dest = Path(args.out).expanduser()
        dest.mkdir(parents=True, exist_ok=True)
    else:
        dest = darkroom()
        if dest is None:
            print(unresolved_message(), file=sys.stderr)
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
        # ▽ is drawn only where the sweep plants distractors, so the key names it
        # only there. A glyph defined in a caption and absent from the figure
        # sends a reader hunting for something that is not in the picture.
        has_distractors = param == "n_distractors" or bool(
            SWEEPS[param].get("base", {}).get("n_distractors"))
        distractor_key = ('<span style="color:#5a5a5a">▽</span> distractors · '
                          if has_distractors else "")
        page = pn.Column(
            pn.pane.HTML(
                f'<div style="font:13px/1.6 system-ui,sans-serif;max-width:1000px">'
                f'<b style="font-size:15px">{param}</b> — {note}<br>'
                f'<span style="color:#555">Everything else held. '
                f'<span style="color:#1b7f3b">▲</span> planted event times · '
                f'{distractor_key}'
                f'every raster onset drawn the same · '
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
                # Exclude the viewport-sized wrappers by comparing against the
                # viewport itself, never against a pixel constant. A literal
                # (`< 1100`) is a cap on how tall a figure may be before the
                # filter silently drops EVERY element: Math.max() of nothing is
                # -Infinity, which reaches the screenshot clip as a height and
                # fails with a JSON parse error naming neither the figure nor
                # the cause. Adding a fifth row to one sweep was enough.
                h = page.evaluate(
                    "(() => { const vh = window.innerHeight;"
                    "const b = [...document.body.querySelectorAll("
                    "'canvas, .bk-Canvas, div')]"
                    ".filter(e => e.offsetHeight > 0"
                    " && Math.abs(e.offsetHeight - vh) > 2)"
                    ".map(e => e.getBoundingClientRect().bottom);"
                    "return b.length ? Math.ceil(Math.max(...b)) : 0; })()")
                w = page.evaluate(
                    "(() => { const vw = window.innerWidth;"
                    "const r = [...document.body.querySelectorAll("
                    "'canvas, .bk-Canvas, div')]"
                    ".filter(e => e.offsetWidth > 0"
                    " && Math.abs(e.offsetWidth - vw) > 2)"
                    ".map(e => e.getBoundingClientRect().right);"
                    "return r.length ? Math.ceil(Math.max(...r)) : 0; })()")
                if h <= 0 or w <= 0:
                    raise RuntimeError(
                        f"measured no rendered content ({w}x{h}) — the page "
                        f"did not draw, or every element matched the viewport")
                page.screenshot(path=str(tmp), clip={
                    "x": 0, "y": 0,
                    "width": min(float(w) + 12, 1120.0),
                    "height": min(float(h) + 12, 4000.0)})
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
