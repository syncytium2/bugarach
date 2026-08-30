#!/usr/bin/env python3
"""Run detectors on one REAL recording and draw what they claimed.

    python tools/make_real_detection_figure.py                       # defaults
    python tools/make_real_detection_figure.py --slice 20240815a51
    python tools/make_real_detection_figure.py --detectors sce loco cicada

Two tools already stood on either side of this question and neither answered it.
``make_diagnostic.py`` draws lanes over a raster and scores them, but only ever
on a *simulated* recording — its input is ``simulate_coordination`` or the bench,
so it can never say what a detector does to real tissue. ``make_reality_check.py``
reads the export folder, but what it draws is TEXTURE: real raster beside
synthetic raster, to argue about the generator. Nobody could see a real recording
with the detections marked on it without writing it by hand.

**There is no ground-truth row and there cannot be one.** Nothing was planted in
a real slice, so a mark here is a claim and not a verdict — no ✕, no scoreboard,
no F1. ``lane_panel`` already draws exactly that when ``gt`` is None, which is
why this file has no plotting code of its own: every convention it must obey
(one ink on the raster, cues in a lane above it pointing down, 60-base time
ticks, x linked through ``t``) is enforced where the panels are built, and a
second drawing path is how those conventions come apart. CLAUDE.md's raster rule
has been broken exactly once, by a tool that overlaid from outside the module.

**Windows come from the folder, verbatim.** ``folder_analysis_windows`` settles
them before any detector sees the slice — the producer's bounds, no wash-in
delay, no cap, no baseline privilege (FOUNDATIONS §4) — and it is the one place
in the tree that answers this, so it is called rather than re-derived here.

Detectors run at the operating points in ``bugarach.bench``, so this figure and
the bench scores describe the same detectors.

Destination is the darkroom, resolved by ``bugarach.paths``; ``--out`` overrides.
The path is never hardcoded — it carries a person's name and this repo is public.
"""

from __future__ import annotations

import argparse
import os
import sys
import tempfile
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))

#: A recording carrying a `baseline` region and NOTHING else — no treatment
#: window at all, so it cannot support a before/after comparison and its raster
#: is publishable (Tony, 2026-08-14; FOUNDATIONS §5 releases this slice by name).
#: Its per-ROI FAST rate sits inside the measured baseline interquartile band,
#: 0.0052–0.0190 Hz, which is what makes it ordinary rather than merely safe.
#: Four other slices in the current export also qualify on the publishability
#: test; two of them fire at 0.0025 Hz, a quarter of that band's floor.
DEFAULT_SLICE = "20240813_39"

#: Short on purpose. A coordinated event is a VERTICAL alignment and vision
#: reads one better over less distance — `raster_panel`'s docstring carries the
#: argument. `mark_px` has to come down with it, or a dash as tall as its own
#: row makes every column look solid whether or not anything coordinated.
RASTER_PX = 220


class NoDetectorRan(RuntimeError):
    """Every detector failed, so there is no figure — only an empty one.

    The same threshold ``make_diagnostic`` uses, and for the same reason: one
    detector failing on one slice is a finding worth printing beside the others,
    and *every* detector failing at once has never meant that many independent
    findings. It has meant the call site was wrong, and the cost of not
    distinguishing the two is a valid PNG with blank lanes that looks like a
    result.
    """


def build(args):
    import holoviews as hv

    hv.extension("bokeh")

    from bugarach.bench import OPERATING_POINTS
    from bugarach.detect_folder import folder_analysis_windows
    from bugarach.detectors.rate import recording_extent
    from bugarach.io import load_folder
    from bugarach.ui.app import _compute
    from bugarach.ui.diagnostic import lane_panel, raster_panel

    slices = {s.slice_id: s for s in load_folder(args.folder)}
    if args.slice_id not in slices:
        raise SystemExit(
            f"{args.folder} has no recording {args.slice_id!r}. It holds "
            f"{len(slices)}: {', '.join(sorted(slices)[:6])}…")

    # Settled BEFORE anything runs, and the settled slice is what goes on: sce
    # and loco re-derive their own windows off the regions and have no argument
    # that could divert them, so keeping the unsettled one would resolve one
    # policy here and hand a different one to both detectors.
    sl, windows = folder_analysis_windows(slices[args.slice_id])
    ext = recording_extent(sl)
    dt = float(sl.require_dt("the real-recording detection figure"))

    if args.stream not in sl.streams:
        raise SystemExit(
            f"{sl.slice_id} carries {', '.join(sl.streams)}, not "
            f"{args.stream!r}. Stream names are the lab's own strings and "
            f"bugarach does not translate them.")

    lanes, failed, counts = {}, {}, {}
    for det in args.detectors:
        try:
            # Read the fields by name, not by position: `StreamResult` has grown
            # a field before, and unpacking positionally broke silently when it
            # did.
            res = _compute(det, sl, ext, dict(OPERATING_POINTS[det].params),
                           dt=dt)[args.stream]
            lanes[det] = res.events
            counts[det] = int(np.size(res.events[0]))
        except Exception as exc:                      # noqa: BLE001
            failed[det] = f"{type(exc).__name__}: {exc}"

    if failed and not lanes:
        raise NoDetectorRan(
            f"not one of the {len(failed)} detectors ran on {sl.slice_id}, so "
            f"there is no figure to draw — only a raster with blank lanes, "
            f"which looks like a result and is not one. What each raised:\n  "
            + "\n  ".join(f"{k}: {v}" for k, v in failed.items()))

    stream = sl.streams[args.stream]
    # gt=None throughout: nothing was planted, so there is no row to judge these
    # against and no marker in this figure means "wrong".
    lane = lane_panel(lanes, ext=ext, width=args.width)
    raster = raster_panel(stream, ext=ext, name=args.stream, width=args.width,
                          height=RASTER_PX, mark_px=args.mark_px)
    fig = (lane + raster).cols(1).opts(
        hv.opts.Layout(shared_axes=True, toolbar="above"))

    n_roi = stream.n_rois
    n_ev = sum(int(np.sum(np.isfinite(np.asarray(v, dtype=float))))
               for v in stream.t50rise)
    span = float(ext[1] - ext[0])
    regions = ", ".join(f"{w.label or 'unnamed'} {w.win_start:g}–{w.win_end:g}s"
                        for w in windows)

    header = [
        f"{sl.slice_id} — real recording, {args.stream} stream",
        f"{n_roi} ROI · {span:g}s · {n_ev} events · "
        f"{n_ev / max(n_roi, 1) / max(span, 1e-9):.4f} Hz per ROI · dt {dt:g}s",
        f"windows, taken from the folder verbatim: {regions}",
    ]
    body = ["", "detections (onsets):"]
    body += [f"  {k}: {v}" for k, v in counts.items()]
    if failed:
        body += ["", "did not run:"] + [f"  {k}: {v}" for k, v in failed.items()]
    body += [
        "",
        "NOTHING WAS PLANTED HERE, so there is no ground-truth row and no score.",
        "Every mark above the raster is a claim, not a verdict: a bar spans what",
        "the detector said it found, and this figure has no way to tell you",
        "whether it was right. The detectors run at the operating points declared",
        "in bugarach.bench, so this figure and the bench scores describe the same",
        "detectors — the bench is where a number about correctness comes from.",
    ]
    return fig, header, "\n".join(header + body)


def main(argv=None):
    p = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--folder", default=None,
                   help="export folder; default: the current one, as "
                        "bugarach.dataset resolves it")
    p.add_argument("--slice", dest="slice_id", default=DEFAULT_SLICE,
                   help=f"recording id (default {DEFAULT_SLICE})")
    p.add_argument("--stream", default="fast")
    p.add_argument("--detectors", nargs="+", default=["sce", "loco"])
    p.add_argument("--width", type=int, default=1000)
    p.add_argument("--mark-px", type=float, default=2.0,
                   help="height of one onset mark in px; wants to stay under "
                        "about a third of the row pitch (RASTER_PX / n_roi)")
    p.add_argument("--tag", default=None,
                   help="filename suffix (default: the slice id)")
    p.add_argument("--out", default=None,
                   help="destination directory; default $BUGARACH_DARKROOM")
    p.add_argument("--no-png", dest="png", action="store_false", default=True,
                   help="skip the flat render (needs playwright chromium)")
    p.add_argument("--scale", type=int, default=3,
                   help="device pixel ratio for the PNG — how far it can be "
                        "zoomed before it goes soft")
    args = p.parse_args(argv)

    from bugarach import dataset
    from bugarach.paths import darkroom, unresolved_message

    args.folder = dataset.require(args.folder or dataset.current(),
                                  want="export_folder", flag="--folder")
    print(dataset.describe(args.folder))

    if args.out:
        dest = Path(args.out).expanduser()
        dest.mkdir(parents=True, exist_ok=True)
    else:
        dest = darkroom(create=True)
        if dest is None:
            print(unresolved_message(), file=sys.stderr)
            return 2

    # The refusal has to reach the exit code: a caller that reads only that
    # would otherwise be told an empty figure was written successfully.
    try:
        fig, header, report = build(args)
    except NoDetectorRan as exc:
        print(f"make_real_detection_figure: {exc}", file=sys.stderr)
        return 1

    import panel as pn

    tag = args.tag or args.slice_id
    html = dest / f"real_detection_{tag}.html"
    txt = dest / f"real_detection_{tag}.txt"

    # write-then-replace: the darkroom is inside Dropbox, and writing in place
    # is what produced its 188 MB of hash-named orphans.
    with tempfile.TemporaryDirectory() as td:
        tmp_html = Path(td) / "fig.html"
        pn.Column(
            pn.pane.Markdown("### " + header[0] + "\n\n" + "  \n".join(header[1:])),
            pn.pane.HoloViews(fig),
            pn.pane.HTML("<pre style='font:12px ui-monospace,monospace'>"
                         + report + "</pre>"),
        ).save(str(tmp_html))
        os.replace(tmp_html, html)
        tmp_txt = Path(td) / "r.txt"
        tmp_txt.write_text(report + "\n", encoding="utf-8")
        os.replace(tmp_txt, txt)

    written = [html, txt]
    if args.png:
        # The flat render is not a convenience: it is the picture a reader will
        # see, and this project has shipped a figure nobody looked at.
        from make_diagnostic import _render_png

        shot = dest / f"real_detection_{tag}.png"
        if _render_png(html, shot, scale=args.scale):
            written.append(shot)
        else:
            print("(no PNG: pip install playwright && python -m playwright "
                  "install chromium, or pass --no-png)", file=sys.stderr)

    print(report)
    print("\nwrote " + "\n      ".join(str(w) for w in written))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
