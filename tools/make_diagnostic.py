#!/usr/bin/env python3
"""Build the coordination diagnostic and write it to the darkroom.

    python tools/make_diagnostic.py                    # defaults
    python tools/make_diagnostic.py --seed 7 --duration 3000
    python tools/make_diagnostic.py --out ./somewhere  # override the destination

Produces, named by the run so successive runs sit side by side rather than
overwriting each other:

    coord_diagnostic_<tag>.html   the interactive view — zoom into a false alarm
    coord_diagnostic_<tag>.png    a flat render of the same page
    coord_diagnostic_<tag>.txt    the scoreboard, in text so it can go in a
                                  commit message or a log where a figure cannot

The PNG is not a convenience. The first version of this figure shipped with its
lane labels written on top of the data, an unexplained marker, and detections
too faint to see — because it was published without anyone rendering it. Both
the darkroom README ("render every slide and look at it before shipping") and
the murderboard's build-and-craft gate already said not to do that. Producing
the flat render in the same command is that rule mechanized: the picture a
reader will see is now an artifact of the build, previewable in Dropbox without
opening anything.

Destination is ``$BUGARACH_DARKROOM`` (see ``bugarach.paths``). It is never
hardcoded: that path carries a person's name and this repo is public. With the
variable unset the script says so and writes nothing, rather than guessing —
the darkroom is mounted on every machine, so a wrong guess scatters files into
another project's folder instead of failing locally.

Files are written to a temporary name and moved into place. The darkroom README
records 188 MB of hash-named orphans created by writing into Dropbox in place;
an atomic replace means the folder only ever sees a finished file.
"""

from __future__ import annotations

import argparse
import os
import sys
import tempfile
from pathlib import Path

import numpy as np

# The six, at the operating points the bench declares, with their provenance —
# so this figure and the scores in bugarach.bench describe the same detectors.
# An earlier version used "deliberately plain values chosen to make the picture
# legible", which quietly meant the diagnostic and the bench could disagree
# about what a detector does; coact at the MATLAB signature default scores F1
# 0.72 against 1.00 at its calibrated point, and a picture drawn at the wrong
# one is a picture of a different detector.
#
# (loco and cicada used to fail here outright — their defaults were (FAST, SLOW)
# pairs that could not broadcast to a single-stream slice. Fixed 2026-08-13;
# the "did not run" path below stays, because a detector that cannot run is a
# finding worth printing rather than a crash worth losing the figure to.)
def _detector_params():
    from bugarach.bench import OPERATING_POINTS
    return {name: dict(op.params) for name, op in OPERATING_POINTS.items()}


def build(args):
    import holoviews as hv
    import panel as pn

    hv.extension("bokeh")

    from bugarach.detectors.rate import recording_extent
    from bugarach.simulate import simulate_coordination
    from bugarach.ui.app import _compute
    from bugarach.ui.diagnostic import (coordination_diagnostic, legend_html,
                                        score_table)

    if args.bench:
        # The bench's own recording, so the figure and the scores in
        # bugarach.bench describe the same run rather than merely the same
        # detectors. The two differ in ways that matter — the bench spaces
        # events 120 s apart to keep the null clean, this tool's default is 15 s
        # — and a picture drawn on a different recording is not evidence about
        # the bench.
        from bugarach.bench import BENCH_RECORDING, make_recording
        slice_, gt = make_recording(args.bench, args.seed)
        args.duration = BENCH_RECORDING["duration_sec"]
        args.n_roi = BENCH_RECORDING["n_roi"]
    else:
        slice_, gt = simulate_coordination(
            seed=args.seed,
            duration_sec=args.duration,
            n_roi=args.n_roi,
            n_per_level=(args.per_level,) * 3,
            interval_cv=args.interval_cv,
            hot_window=(args.duration * 0.4, args.duration * 0.6) if args.hot else None,
            hot_rate_hz=args.hot_rate if args.hot else 0.0,
            ramp_sec=args.duration * 0.02 if args.hot else 0.0,
            n_distractors=args.distractors,
        )
    ext = recording_extent(slice_)

    lanes, traces, failed = {}, {}, {}
    for det, params in _detector_params().items():
        try:
            t, y, events, extra = _compute(det, slice_, ext, params)["events"]
            lanes[det] = events
            traces[det] = (t, y, events, extra)
        except Exception as exc:                      # noqa: BLE001
            # A detector that cannot run on this slice is a finding, not a crash
            # — record it in the sidecar instead of losing the whole figure.
            failed[det] = f"{type(exc).__name__}: {exc}"

    fig = coordination_diagnostic(slice_.streams["events"], ext=ext, lanes=lanes,
                                  gt=gt, traces=traces, height=args.height)
    legend = legend_html(lanes, gt)

    header = [
        f"bugarach coordination diagnostic — seed {args.seed}",
        f"{args.n_roi} ROI · {args.duration:g}s · {len(gt.events)} planted events"
        + (f" · bench {args.bench} regime" if args.bench
           else f" · interval CV {args.interval_cv:g}"),
    ]
    # read the probe and distractors off the ground truth, not off the CLI args:
    # with --bench the recording came from bugarach.bench and the args no longer
    # describe it. A caption that describes a different recording is worse than
    # no caption.
    hot = gt.params.get("hot_window")
    if hot:
        header.append(
            f"dense-but-random block {hot[0]:g}–{hot[1]:g}s at "
            f"+{gt.params.get('hot_rate_hz', args.hot_rate):g} Hz/ROI — contains "
            f"NO planted events, so detections inside it are false alarms by "
            f"construction")
    if gt.distractors:
        header.append(f"{len(gt.distractors)} correlated-burst distractors — real "
                      f"coincidence that is not a coordinated event")
    header += ["", score_table(gt, lanes)]
    if failed:
        header += ["", "did not run:"]
        header += [f"  {k}: {v}" for k, v in failed.items()]
    header += ["", "Detectors run at the operating points declared in "
                   "bugarach.bench, so this figure and the bench scores describe "
                   "the same detectors. Still a troubleshooting view, not a "
                   "ranking — one seed is not a measurement."]
    report = "\n".join(header)

    return fig, legend, header, report, pn


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--seed", type=int, default=3)
    p.add_argument("--duration", type=float, default=1800.0)
    p.add_argument("--n-roi", type=int, default=30)
    p.add_argument("--per-level", type=int, default=5,
                   help="planted events at each of 100%%/75%%/50%% participation")
    p.add_argument("--interval-cv", type=float, default=1.0,
                   help="0 regular, 1 Poisson-like, >1 bursty")
    p.add_argument("--hot", action="store_true", default=True,
                   help="include the dense-but-random probe block (default on)")
    p.add_argument("--no-hot", dest="hot", action="store_false")
    p.add_argument("--hot-rate", type=float, default=0.25)
    p.add_argument("--distractors", type=int, default=3)
    p.add_argument("--height", type=int, default=560)
    from bugarach.bench import REGIMES as _R
    p.add_argument("--bench", choices=tuple(_R), default=None,
                   help="render the bugarach.bench recording for this regime "
                        "instead of one built from the options above")
    p.add_argument("--tag", default=None, help="filename suffix (default: seed)")
    p.add_argument("--out", default=None,
                   help="destination directory; default $BUGARACH_DARKROOM")
    p.add_argument("--no-png", dest="png", action="store_false", default=True,
                   help="skip the flat render (needs playwright chromium)")
    p.add_argument("--scale", type=int, default=3,
                   help="device pixel ratio for the PNG — how far it can be "
                        "zoomed before it goes soft (default 3, ~1.4 MB)")
    args = p.parse_args(argv)

    from bugarach.paths import ENV_VAR, darkroom

    if args.out:
        dest = Path(args.out).expanduser()
        dest.mkdir(parents=True, exist_ok=True)
    else:
        dest = darkroom(create=True)
        if dest is None:
            print(f"{ENV_VAR} is not set, so there is nowhere agreed to write.\n"
                  f"Set it to this repo's darkroom folder, or pass --out DIR.\n"
                  f"Not guessing: the darkroom is visible from every machine, so "
                  f"a wrong guess lands files in another project's folder.",
                  file=sys.stderr)
            return 2

    fig, legend, header, report, pn = build(args)
    tag = args.tag or f"seed{args.seed}"
    html, txt = dest / f"coord_diagnostic_{tag}.html", dest / f"coord_diagnostic_{tag}.txt"

    # write-then-replace: the darkroom is inside Dropbox, and writing in place is
    # what produced its orphaned-file problem.
    with tempfile.TemporaryDirectory() as td:
        tmp_html = Path(td) / "fig.html"
        # header + legend + figure: a figure whose markers need explaining
        # and does not carry the explanation is not finished.
        title = header[0]
        subtitle = "  \n".join(header[1:4])
        page = pn.Column(
            pn.pane.Markdown("### " + title + "\n\n" + subtitle),
            pn.pane.HTML(legend),
            pn.pane.HoloViews(fig),
            pn.pane.HTML("<pre style='font:12px ui-monospace,monospace'>"
                         + report + "</pre>"),
        )
        page.save(str(tmp_html))
        os.replace(tmp_html, html)
        tmp_txt = Path(td) / "report.txt"
        tmp_txt.write_text(report + "\n", encoding="utf-8")
        os.replace(tmp_txt, txt)

    written = [html, txt]
    if getattr(args, "png", True):
        shot = dest / f"coord_diagnostic_{tag}.png"
        if _render_png(html, shot, scale=getattr(args, "scale", 3)):
            written.append(shot)
        else:
            print("(no PNG: pip install playwright && python -m playwright "
                  "install chromium, or pass --no-png)", file=sys.stderr)

    print(report)
    print("\nwrote " + "\n      ".join(str(w) for w in written))
    return 0


def _render_png(html_path: Path, png_path: Path, *, wait_ms: int = 3500,
                scale: int = 3) -> bool:
    """Flatten the page to a PNG. Returns False rather than raising when the
    browser is unavailable — a missing screenshot must not cost you the figure.

    ``scale`` is the device pixel ratio the page is rendered at, and it is what
    decides whether the figure survives being zoomed into. This view is read by
    zooming — a 45-minute recording at 1180 CSS px puts a 0.36 s jitter well
    under one pixel, and the reason to open it at all is usually to look closely
    at one event. At 2 the raster ticks and the lane markers go soft before you
    get there (Tony, 2026-08-15), so 3 is the default and the cost is file size:
    roughly 0.7 MB at 2, 1.4 MB at 3.
    """
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        return False
    try:
        with tempfile.TemporaryDirectory() as td:
            tmp = Path(td) / "shot.png"
            with sync_playwright() as pw:
                browser = pw.chromium.launch()
                page = browser.new_page(viewport={"width": 1180, "height": 1400},
                                   device_scale_factor=scale)
                page.goto(html_path.resolve().as_uri())
                page.wait_for_timeout(wait_ms)      # bokeh draws after load
                page.screenshot(path=str(tmp), full_page=True)
                browser.close()
            os.replace(tmp, png_path)
        return True
    except Exception as exc:                        # noqa: BLE001
        print(f"(PNG render failed: {type(exc).__name__}: {exc})", file=sys.stderr)
        return False


if __name__ == "__main__":
    raise SystemExit(main())
