#!/usr/bin/env python3
"""Draw what the tube models trained against rigid shift called on one real recording.

    python tools/make_tube_real_lanes.py --run <tube_ssl_real_compare output> --out <folder>
    python tools/make_tube_real_lanes.py --run <...> --out <...> --slice 20240813_39 --zoom 120

Reads ``events.json`` from ``tools/tube_ssl_real_compare.py`` and draws, for one recording's
baseline, a lane per detector above the raster: CoactDetect, LoCo, supervised tube, and tube and
tube_guard trained against rigid shift (J = 10 s, training seed 0). Two views: the whole baseline
and a zoom around the recording's first CoactDetect event.

No plotting code of its own: panels come from :mod:`bugarach.ui.diagnostic` (``lane_panel``
above ``raster_panel``; nothing drawn on the raster) and the flat render from
``make_diagnostic._render_png``, exactly as ``make_real_detection_figure.py`` does. Nothing is
planted here, so every mark is a claim, not a verdict. Real rasters stay in the darkroom.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import tempfile
import warnings
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

DEFAULT_SLICE = "20240813_39"

#: The lane sets this tool knows how to draw, selected with ``--family``. ``line`` is the default
#: because it is the family the 2026-09-16 report argues about, and because the claim that most
#: needs a picture — half the calls from `line` trained against rigid shift land where no ROI has
#: an onset — is a claim about *these* rows. ``tube`` is kept so the earlier renders reproduce.
LANE_SETS = {
    "line": [("coact", "CoactDetect"), ("loco", "LoCo"),
             ("supervised line label-free", "line, supervised"),
             ("ssl line J10", "line, no labels (J 10 s)"),
             ("ssl line J20", "line, no labels (J 20 s)")],
    "tube": [("coact", "CoactDetect"), ("loco", "LoCo"),
             ("supervised tube label-free", "tube, supervised"),
             ("ssl tube J10", "tube, no labels (J 10 s)"),
             ("ssl tube_guard J10", "tube_guard, no labels (J 10 s)")],
}
LANES = LANE_SETS["line"]
COLORS = {"CoactDetect": "#1f4e79", "LoCo": "#2e7d32",
          "line, supervised": "#555555", "tube, supervised": "#555555",
          "line, no labels (J 10 s)": "#c07a12", "line, no labels (J 20 s)": "#7b3294",
          "tube, no labels (J 10 s)": "#c07a12", "tube_guard, no labels (J 10 s)": "#7b3294"}


def build(events, slice_id, zoom_sec, width):
    import holoviews as hv
    hv.extension("bokeh")
    from bugarach import dataset
    from bugarach.detect_folder import folder_analysis_windows
    from bugarach.io import load_folder
    from bugarach.ui.diagnostic import lane_panel, raster_panel

    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        slices = {s.slice_id: s for s in load_folder(dataset.current("steps_excluded"))}
    sl, windows = folder_analysis_windows(slices[slice_id])
    base = next(w for w in windows if (w.label or "").strip().lower().startswith("baseline"))
    full = (float(base.win_start), float(base.win_end))
    stream = sl.streams["fast"]

    def lanes_for():
        out = {}
        for key, label in LANES:
            run = events[key][0]
            ev = run.get(slice_id, [])
            out[label] = (np.asarray([o for o, _ in ev], float), np.asarray([w for _, w in ev], float))
        return out

    lanes = lanes_for()
    co = lanes["CoactDetect"][0]
    centre = float(co[0]) if co.size else float(np.mean(full))
    zoom = (max(full[0], centre - zoom_sec / 2), min(full[1], centre + zoom_sec / 2))
    figs = []
    for ext, h in ((full, 240), (zoom, 240)):
        lane = lane_panel(lanes, ext=ext, width=width, colors=COLORS)
        raster = raster_panel(stream, ext=ext, name="fast", width=width, height=h, mark_px=2.0)
        figs.append((lane + raster).cols(1).opts(hv.opts.Layout(shared_axes=True,
                                                                toolbar="above")))
    counts = {label: int(v[0].size) for label, v in lanes.items()}
    tail = " Events per lane over the whole baseline: " + ", ".join(
        f"{k} {v}" for k, v in counts.items()) + ". Nothing is planted: every mark is a claim."
    headers = [f"{slice_id} — lab fast stream, whole baseline ({full[0]:g}–{full[1]:g} s)." + tail,
               f"{slice_id} — lab fast stream, {zoom[1] - zoom[0]:g} s of baseline around its first "
               f"CoactDetect event ({zoom[0]:g}–{zoom[1]:g} s)." + tail]
    return figs, headers


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--run", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--slice", dest="slice_id", default=DEFAULT_SLICE)
    ap.add_argument("--zoom", type=float, default=120.0)
    ap.add_argument("--width", type=int, default=1100)
    ap.add_argument("--family", choices=sorted(LANE_SETS), default="line",
                    help="which architecture family to draw lanes for (default: line)")
    a = ap.parse_args(argv)
    global LANES
    LANES = LANE_SETS[a.family]
    events = json.loads((Path(a.run) / "events.json").read_text())
    figs, headers = build(events, a.slice_id, a.zoom, a.width)
    import panel as pn
    from make_diagnostic import _render_png
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    # One file per view. In one document the two views share the `t` axis through holoviews'
    # linking, so the zoom silently kept the whole baseline's range.
    for fig, header, view in zip(figs, headers, ("baseline", "zoom")):
        html = out / f"tube_real_lanes_{a.slice_id}_{view}.html"
        with tempfile.TemporaryDirectory() as td:
            tmp = Path(td) / "f.html"
            pn.Column(pn.pane.Markdown(header), pn.pane.HoloViews(fig)).save(str(tmp))
            os.replace(tmp, html)
        png = html.with_suffix(".png")
        print(html)
        if _render_png(html, png, scale=2):
            print(png)


if __name__ == "__main__":
    main()
