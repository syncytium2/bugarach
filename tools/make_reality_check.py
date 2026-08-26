#!/usr/bin/env python3
"""Put a real baseline recording next to what the generator makes.

    python tools/make_reality_check.py --folder <export folder> --out docs/generator

The one figure this project's synthetic-data story most needed and did not have.
Everything else in `docs/generator.md` argues about parameters; this shows the
thing the parameters are supposed to reproduce, beside the reproduction, on the
same axes.

**Which slice, and why it is publishable.** The example carries a `baseline`
region and *nothing else* — no treatment window at all. Such a recording cannot
support a before/after comparison, so it is not usable as an experimental result
and its raster can sit in a public repo (Tony, 2026-08-14). Four slices in the
archive qualify; the default is the one whose per-ROI rate lands nearest the
measured baseline median, which is also the rate the generator is calibrated to.

Needs `--folder`, an export folder (`docs/export_folder_spec.md`); without one the
script says so and writes nothing. It used to read a `.mat` store, and this line
used to say `$BUGARACH_DATA_ROOT` — a store holds every recording ever processed,
including the ones the lab withdrew, and this is the one figure here that gets
published. The folder is the whole input, and its `PROVENANCE.md` says what was left
out. Export folders are machine-local (FOUNDATIONS §5), so guessing a path is
worse than not drawing.
"""

from __future__ import annotations

import argparse
import os
import sys
import tempfile
from pathlib import Path

import numpy as np

DEFAULT_SLICE = "20240813_39"

# Three rasters stacked on one page, so each is squat by necessity — and the
# compression is the point rather than the concession: what this figure asks a
# reader to compare is TEXTURE, whether activity clumps into columns and into
# busy rows, and texture survives vertical compression better than it survives
# scrolling. 37 ROIs in this much height leaves a row pitch of about 5 px, which
# is why the mark is 2 px and not the 5 it was: a dash the height of its own row
# turns every panel into a solid field and there is no texture left to compare.
RASTER_PX = 200
RASTER_MARK_PX = 2.0


def _window(stream, lo, hi):
    """Per-ROI onsets inside the region, re-zeroed to the window start."""
    out = []
    for v in (stream.t50rise or stream.locs):
        v = np.asarray(v, dtype=float)
        v = v[np.isfinite(v)]
        out.append(np.sort(v[(v >= lo) & (v < hi)]) - lo)
    return out


def _top_share(sl, name="events"):
    """Percent of all events held by the busiest ROI — the concentration, in one
    number. A flat field lands near 100/n_roi; a real baseline field runs far
    above it."""
    counts = np.array([len(v) for v in sl.streams[name].locs], dtype=float)
    total = counts.sum()
    return 0.0 if total <= 0 else 100.0 * counts.max() / total


def build(args):
    import holoviews as hv

    hv.extension("bokeh")

    from bugarach.detectors.loco import loco_detect
    from bugarach.io import load_folder, slice_from_events
    from bugarach.simulate import simulate_coordination
    from bugarach.ui.app import _time_axis_hook
    from bugarach.ui.diagnostic import lane_panel, raster_panel

    if not args.folder:
        raise SystemExit(
            "--folder is required: this figure draws a real recording, and the "
            "arrive as an export folder (docs/export_folder_spec.md). It used "
            "to open a .mat store, which holds every recording ever processed "
            "including the ones the lab withdrew. This figure is PUBLISHED "
            "(FOUNDATIONS §5), so that is the last place to draw from a set "
            "nobody approved. Nothing written.")

    hit = [s for s in load_folder(Path(args.folder).expanduser())
           if str(s.slice_id) == str(args.slice)]
    if not hit:
        raise SystemExit(
            f"{args.slice} is not in {args.folder}. If the lab withdrew it, that "
            f"is the answer, and it certainly must not be published — the "
            f"folder is the input and its PROVENANCE.md says what was dropped.")

    real = hit[0]
    names = [(r.name or "").strip().lower() for r in real.regions]
    if set(names) != {"baseline"}:
        # The publishability argument rests entirely on this, so it is a guard,
        # not a comment: a slice carrying a treatment window is a before/after
        # result and does not belong in a public figure.
        raise SystemExit(
            f"{args.slice} has regions {sorted(set(names))} — this figure only "
            "renders baseline-only recordings, which carry no before/after "
            "result and are therefore publishable.")

    reg = real.regions[0]
    dur = reg.end_sec - reg.start_sec
    stream = real.streams["fast"]
    n_roi = stream.n_rois
    ev = _window(stream, reg.start_sec, reg.end_sec)
    total = sum(v.size for v in ev)
    rate = total / (n_roi * dur)

    real_win = slice_from_events(ev, dt=None, slice_id="real")

    def generated(shape):
        return simulate_coordination(
            seed=args.seed, duration_sec=dur, n_roi=n_roi, bg_rate_hz=rate,
            bg_rate_shape=shape,
            participation=(0.30, 0.18, 0.10),
            n_per_level=(args.per_level,) * 3,
            jitter_sec=0.36, min_sep_sec=120.0, interval_cv=1.0)

    synth, gt = generated(None)
    # Ground truth is PER RUN, not shared. The background draw consumes random
    # numbers, so the heterogeneous run's events land at different times than the
    # flat run's at the same seed. An earlier version of this figure marked the
    # flat run's planted times on the heterogeneous raster, where nothing had
    # been planted — the triangles pointed at background.
    truth = {"synthetic": gt}
    series = [("real", real_win), ("synthetic", synth)]
    if args.shape is not None:
        hetero, hetero_gt = generated(args.shape)
        truth["heterogeneous"] = hetero_gt
        series.append(("heterogeneous", hetero))

    ext = (0.0, dur)
    det = {}
    for label, sl in series:
        d = loco_detect(sl, n_surrogates=100, rng_seed=7).streams["events"]
        det[label] = d

    rows = []
    for label, sl in series:
        d = det[label]
        # WHAT A DETECTOR MADE OF THE RECORDING RIDES IN A LANE ABOVE IT, never
        # on it. Drawn into the raster the marks land on the busiest ROI rows and
        # cover them; worse, sitting among the onsets they invite the reader to
        # take the ones beneath as the events LoCo recruited, which is a
        # per-onset claim LoCo does not make. This is the convention the
        # six-detector figure and the viewer already hold to — the recording
        # below, the reading above — and this figure was the last one out of step
        # with it (Tony, opening the site, 2026-08-22).
        #
        # Planted truth exists in every generated panel and in none of the real
        # one — and each panel gets ITS OWN, because the two generated runs do
        # not share a schedule. `lane_panel` drops the "planted" row when there is
        # no truth to draw, so the real panel gets a LoCo lane and nothing else.
        own = truth.get(label)
        # A SPAN, NOT A POINT: LoCo reports a window, and the diamond marking its
        # onset alone was all that remained of the extent once the inked onsets
        # went. `lane_panel` draws `onset → onset + width`, which is what the
        # detector actually returns.
        rows.append(lane_panel({"loco": (d.onset_sec,
                                         getattr(d, "width_sec", None))},
                               ext=ext, gt=own, width=args.width))
        panel = raster_panel(sl.streams["events"], ext=ext,
                             name=label, width=args.width,
                             height=RASTER_PX, mark_px=RASTER_MARK_PX)
        # Keep this SHORT, and shorter now than it was. The bottom panel spends
        # part of its height on an x-axis the top one does not have, so its
        # rotated y-label has less room to run in and a long string is clipped
        # with no error — the figure read "9.5 mHz/RC" until 2026-08-15,
        # including on the public site. That was at 250 px; the raster is
        # shorter than that now, and "REAL · 9.5 mHz/ROI" would have walked back
        # into the same clip. The header line above the figure already gives the
        # ROI count, the duration AND the per-ROI rate, so the axis carries the
        # one thing the header cannot: which panel you are looking at.
        # The published two-panel figure keeps saying GENERATED. Only when the
        # third panel is present does "generated" become ambiguous, and only
        # then do the two generated rows need distinguishing from each other.
        if len(series) > 2:
            lab = {"real": "REAL", "synthetic": "FLAT BG",
                   "heterogeneous": "VARIED BG"}[label]
        else:
            lab = "REAL" if label == "real" else "GENERATED"
        last = label == series[-1][0]
        rows.append(panel.opts(
            width=args.width, height=RASTER_PX, xlim=ext, ylim=(-1, n_roi),
            xaxis="bottom" if last else None,
            ylabel=lab, xlabel="time" if last else "", title="",
            fontsize={"ylabel": "10pt"}, show_legend=False,
            hooks=[_time_axis_hook]))

    fig = rows[0]
    for r in rows[1:]:
        fig = fig + r
    fig = fig.cols(1).opts(shared_axes=False, merge_tools=True, toolbar=None)
    header = (
        f'<div style="font:13px/1.6 system-ui,sans-serif;max-width:{args.width}px">'
        f'<b style="font-size:15px">A real recording, and the generator asked to '
        f'imitate it</b><br>'
        f'Top: slice <code>{args.slice}</code>, {n_roi} ROI over '
        f'{dur/60:.0f} min — a <b>baseline-only</b> recording, so it carries no '
        # Plain words, not the function name: this figure is published on the
        # public site, and a reader who has never seen the source cannot use
        # "simulate_coordination" for anything.
        + (f'before/after result. Below it: the generator run at the '
           if args.shape is not None else
           f'before/after result. Bottom: the generator run at the ')
        + f'same ROI count, duration and per-ROI rate '
        f'({rate*1000:.1f} mHz), with events planted at the measured '
        f'participation and jitter.<br>'
        f'Each raster carries a lane above it, and nothing is drawn on the '
        f'raster itself: every onset is the same mark, whatever a detector made '
        f'of it. '
        f'<span style="color:#8c564b">▮</span> <b>LoCo</b> — one bar per '
        f'coordinated-event call, same detector and settings on both. The bar '
        f'spans the window called; these run under a second, which is thinner '
        f'than a pixel at 30 minutes across, so they are drawn at a minimum '
        f'visible width. '
        f'<span style="color:#1b7f3b">▲</span> <b>planted</b> — the truth, '
        f'which exists only below; <span style="color:#b3261e">▼</span> is one '
        f'LoCo did not call and <span style="color:#b3261e">✕</span> a call '
        f'with nothing planted within 1.5 s.<br>'
        f'<span style="color:#555">LoCo finds <b>{det["real"].onset_sec.size}</b> '
        f'in the real recording and <b>{det["synthetic"].onset_sec.size}</b> in '
        f'the generated one, where <b>{len(gt.times)}</b> were planted.</span>'
        + (f'<br><span style="color:#555">Third panel: the same generator with '
           f'per-ROI rates drawn from a Gamma of shape <b>{args.shape:g}</b> '
           f'instead of one rate for every ROI, at the same mean. Its busiest ROI '
           f'carries <b>{_top_share(series[2][1]):.0f}%</b> of its events against '
           f'<b>{_top_share(real_win):.0f}%</b> in the real recording and '
           f'<b>{_top_share(synth):.0f}%</b> in the flat one. LoCo finds '
           f'<b>{det["heterogeneous"].onset_sec.size}</b> there. The planted '
           f'schedule is NOT shared between the two generated panels — the '
           f'background draw consumes random numbers, so each carries its own '
           f'truth marks.</span>'
           if args.shape is not None else '')
        + '</div>')
    return fig, header


def main(argv=None):
    p = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--folder", default=None,
                   help="export folder holding the recording to draw "
                        "(docs/export_folder_spec.md)")
    p.add_argument("--slice", default=DEFAULT_SLICE)
    p.add_argument("--seed", type=int, default=5)
    p.add_argument("--per-level", type=int, default=4)
    p.add_argument("--shape", type=float, default=None, metavar="A",
                   help="add a third panel whose per-ROI background rates are "
                        "drawn from Gamma(A, mean/A) instead of every ROI "
                        "getting the same rate. The fitted value is "
                        "bugarach.bench.MEASURED_RATE_SHAPE; re-derive it with "
                        "tools/fit_background_shape.py.")
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
        dest = darkroom(create=True)
        if dest is None:
            print(unresolved_message(), file=sys.stderr)
            return 2

    import panel as pn

    fig, header = build(args)
    page = pn.Column(pn.pane.HTML(header), pn.pane.HoloViews(fig))

    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td) / "page.html"
        page.save(str(tmp))
        html = dest / "reality_check.html"
        os.replace(tmp, html)
    print(f"wrote {html}")
    if args.png:
        shot = dest / "reality_check.png"
        if _render_png(html, shot):
            print(f"      {shot}")
        else:
            print("      (PNG skipped)", file=sys.stderr)
    return 0


def _render_png(html_path: Path, png_path: Path, *, wait_ms: int = 3000) -> bool:
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        return False
    try:
        with sync_playwright() as pw:
            browser = pw.chromium.launch()
            page = browser.new_page(viewport={"width": 1120, "height": 900},
                                    device_scale_factor=2)
            page.goto(html_path.resolve().as_uri())
            page.wait_for_timeout(wait_ms)
            h = page.evaluate(
                "Math.ceil(Math.max(...Array.from("
                "document.body.querySelectorAll('canvas, .bk-Canvas, div'))"
                ".filter(e => e.offsetHeight > 0 && e.offsetHeight < 890)"
                ".map(e => e.getBoundingClientRect().bottom)))")
            w = page.evaluate(
                "Math.ceil(Math.max(...Array.from("
                "document.body.querySelectorAll('canvas, .bk-Canvas, div'))"
                ".filter(e => e.offsetWidth > 0 && e.offsetWidth < 1119)"
                ".map(e => e.getBoundingClientRect().right)))")
            with tempfile.TemporaryDirectory() as td:
                tmp = Path(td) / "shot.png"
                page.screenshot(path=str(tmp), clip={
                    "x": 0, "y": 0,
                    "width": min(float(w) + 12, 1120.0),
                    "height": min(float(h) + 12, 900.0)})
                browser.close()
                os.replace(tmp, png_path)
        return True
    except Exception as exc:                           # noqa: BLE001
        print(f"      PNG render failed: {type(exc).__name__}: {exc}",
              file=sys.stderr)
        return False


if __name__ == "__main__":
    raise SystemExit(main())
