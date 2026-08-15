#!/usr/bin/env python3
"""Put a real baseline recording next to what the generator makes.

    python tools/make_reality_check.py --out docs/generator

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

Needs `$BUGARACH_DATA_ROOT`; without it the script says so and writes nothing,
because real stores are machine-local (FOUNDATIONS §5) and guessing a path is
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
ARCHIVE = "processed_archive/event_store_onset_revised_2v"


def _window(stream, lo, hi):
    """Per-ROI onsets inside the region, re-zeroed to the window start."""
    out = []
    for v in (stream.t50rise or stream.locs):
        v = np.asarray(v, dtype=float)
        v = v[np.isfinite(v)]
        out.append(np.sort(v[(v >= lo) & (v < hi)]) - lo)
    return out


def build(args):
    import holoviews as hv

    hv.extension("bokeh")

    from bugarach.detectors.loco import loco_detect
    from bugarach.io import slice_from_events
    from bugarach.simulate import simulate_coordination
    from bugarach.store import load_slice
    from bugarach.ui.app import _time_axis_hook
    from bugarach.ui.diagnostic import raster_panel

    root = os.environ.get("BUGARACH_DATA_ROOT", "").strip()
    if not root:
        raise SystemExit(
            "BUGARACH_DATA_ROOT is not set — this figure needs a real recording, "
            "and real stores are machine-local. Nothing written.")

    path = Path(root).expanduser() / ARCHIVE / f"{args.slice}.mat"
    if not path.exists():
        raise SystemExit(f"no such slice: {path}")

    real = load_slice(path)
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

    real_win = slice_from_events(ev, slice_id="real")
    synth, gt = simulate_coordination(
        seed=args.seed, duration_sec=dur, n_roi=n_roi, bg_rate_hz=rate,
        participation=(0.30, 0.18, 0.10),
        n_per_level=(args.per_level,) * 3,
        jitter_sec=0.36, min_sep_sec=120.0, interval_cv=1.0)

    ext = (0.0, dur)
    det = {}
    for label, sl in (("real", real_win), ("synthetic", synth)):
        d = loco_detect(sl, n_surrogates=100, rng_seed=7).streams["events"]
        det[label] = d

    rows = []
    for label, sl in (("real", real_win), ("synthetic", synth)):
        d = det[label]
        spans = [(o, o + max(w, 1.0)) for o, w in zip(d.onset_sec, d.width_sec)]
        panel = raster_panel(sl.streams["events"], ext=ext, member_spans=spans,
                             name=label, width=args.width, height=250)
        # LoCo's calls, marked the same way in both panels — the comparison the
        # figure exists to make is "does a detector behave the same on each".
        if d.onset_sec.size:
            panel = panel * hv.Scatter(
                (d.onset_sec, np.full(d.onset_sec.size, n_roi - 0.6)),
                kdims=["t"], vdims=["roi"]).opts(
                marker="diamond", size=9, color="#7b4a9c", alpha=0.95)
        # planted truth exists only on the right-hand side of the comparison
        if label == "synthetic" and len(gt.times):
            panel = panel * hv.Scatter(
                (gt.times, np.full(gt.times.size, n_roi - 2.4)),
                kdims=["t"], vdims=["roi"]).opts(
                marker="triangle", size=8, color="#1b7f3b", alpha=0.95)
        # Keep this SHORT. The bottom panel spends part of its 250 px on an
        # x-axis the top one does not have, so its rotated y-label has less room
        # to run in and a long string is clipped with no error — the figure read
        # "9.5 mHz/RC" until 2026-08-15, including on the public site. The ROI
        # count is already in the header line, so the axis need not repeat it.
        lab = ("REAL" if label == "real" else "GENERATED") + \
              f" · {rate*1000:.1f} mHz/ROI"
        rows.append(panel.opts(
            width=args.width, height=250, xlim=ext, ylim=(-1, n_roi),
            xaxis=None if label == "real" else "bottom",
            ylabel=lab, xlabel="" if label == "real" else "time", title="",
            fontsize={"ylabel": "10pt"}, show_legend=False,
            hooks=[_time_axis_hook]))

    fig = (rows[0] + rows[1]).cols(1).opts(shared_axes=False, merge_tools=True,
                                           toolbar=None)
    header = (
        f'<div style="font:13px/1.6 system-ui,sans-serif;max-width:{args.width}px">'
        f'<b style="font-size:15px">A real recording, and the generator asked to '
        f'imitate it</b><br>'
        f'Top: slice <code>{args.slice}</code>, {n_roi} ROI over '
        f'{dur/60:.0f} min — a <b>baseline-only</b> recording, so it carries no '
        # Plain words, not the function name: this figure is published on the
        # public site, and a reader who has never seen the source cannot use
        # "simulate_coordination" for anything.
        f'before/after result. Bottom: the generator run at the '
        f'same ROI count, duration and per-ROI rate '
        f'({rate*1000:.1f} mHz), with events planted at the measured '
        f'participation and jitter.<br>'
        f'<span style="color:#7b4a9c">◆</span> LoCo\'s coordinated-event calls, '
        f'the same detector and settings on both · '
        f'<span style="color:#1b7f3b">▲</span> planted truth, which exists only '
        f'below · onsets inside a called window are dark, the rest muted.<br>'
        f'<span style="color:#555">LoCo finds <b>{det["real"].onset_sec.size}</b> '
        f'in the real recording and <b>{det["synthetic"].onset_sec.size}</b> in '
        f'the generated one, where <b>{len(gt.times)}</b> were planted.</span>'
        f'</div>')
    return fig, header


def main(argv=None):
    p = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--slice", default=DEFAULT_SLICE)
    p.add_argument("--seed", type=int, default=5)
    p.add_argument("--per-level", type=int, default=4)
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
        dest = darkroom(create=True)
        if dest is None:
            print(f"{ENV_VAR} is not set and --out was not given — writing "
                  "nothing rather than guessing.", file=sys.stderr)
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
