#!/usr/bin/env python3
"""Raster pages for the stack measurement: what each detector called, in lanes above the raster.

    python tools/make_stack_rasters.py --also docs/learned/runs/2026-10-07-stack

Reads the ``summary.json`` that ``tools/measure_stack.py`` wrote, picks three simulated bench
recordings on which ``stack`` and ``count_sliding`` differ most, and draws each twice, the whole
recording and a one-minute close-up:

* a **fast, busy** recording where ``stack`` makes the most extra calls on decoys;
* the recording where ``stack`` calls the most planted events **under the floor** that
  ``count_sliding`` does not;
* the **elevated-rate** recording where ``count_sliding`` makes the most calls inside the stretch
  that ``stack`` does not.

Every page is ``bugarach.ui.diagnostic``'s own ``lane_panel`` over its ``raster_panel``: nothing
is drawn on the raster, and every call sits in a lane above it, one lane per detector.

Simulated recordings only, so the pages can be committed (``--also``). The pages for real
recordings are made by ``tools/measure_stack_on_folder.py`` and go to the darkroom alone.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import tempfile
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import measure_stack as ms  # noqa: E402

FIRST_FIGURE = 5
"""``measure_stack.py`` draws Figures 1 to 4; the raster pages carry on from there."""
ZOOM_SEC = 60.0
MATCH_SEC = 2.5

HOW_TO_READ = (
    "How to read it: the raster at the bottom is the simulated recording, one row per ROI "
    "(region of interest, a cell), one black mark per calcium-event onset. Nothing is drawn "
    "on it. Each lane above it is one detector, and each bar in a lane is one call. A red "
    "cross above a bar is a call the scorer counts as a false alarm; a red ring is a second "
    "call on an event already found. The top lane is what was planted: a triangle pointing "
    "down at the raster for each planted event, green if any detector on the page found it "
    "and red if none did, and an open grey triangle for each decoy (planted coordination the "
    "bench labels as not an event).")


def lanes_of(dets: dict) -> dict:
    return {n: (np.asarray(d.onset_sec, float), np.asarray(d.width_sec, float))
            for n, d in dets.items()}


def page(lanes: dict, stream, *, ext, gt, raster_name: str, heading: str, caption: str,
         png: Path, not_run=(), width: int = 1100, names=None, colors=None,
         raster_height: int | None = None) -> bool:
    """One page: heading, lanes over raster, caption. Written as HTML beside the PNG."""
    import panel as pn

    from bugarach.ui import diagnostic as dg
    from make_diagnostic import _render_png

    top = dg.lane_panel(lanes, ext=ext, gt=gt, width=width, names=names or ms.NAME,
                        colors=colors or ms.INK, not_run=not_run)
    raster = dg.raster_panel(stream, ext=ext, gt=gt, name=raster_name, width=width,
                             height=raster_height)
    fig = (top + raster).cols(1).opts(shared_axes=True, merge_tools=True, toolbar=None)
    body = pn.Column(
        pn.pane.Markdown(f"**{heading}**", width=width),
        pn.pane.HoloViews(fig),
        pn.pane.Markdown(caption, width=width))
    html = png.with_suffix(".html")
    # Written to a temporary name and moved into place, so a synced folder only ever sees a
    # finished file (the same reason make_diagnostic.py gives).
    with tempfile.NamedTemporaryFile(dir=png.parent, suffix=".html", delete=False) as fh:
        tmp = Path(fh.name)
    body.save(str(tmp))
    os.replace(tmp, html)
    return _render_png(html, png)


def only_in(a, b) -> np.ndarray:
    """Calls of ``a`` with no call of ``b`` within :data:`MATCH_SEC`."""
    ao, aw = np.asarray(a.onset_sec, float), np.asarray(a.width_sec, float)
    bo, bw = np.asarray(b.onset_sec, float), np.asarray(b.width_sec, float)
    keep = [not np.any((bo <= o + w + MATCH_SEC) & (bo + bw >= o - MATCH_SEC))
            for o, w in zip(ao, aw)]
    return ao[np.asarray(keep, bool)] if ao.size else ao


def picks(R) -> list[dict]:
    """The three recordings, each the largest difference of its kind in the summary."""
    def rows(kind, streams=ms.STREAMS, regimes=tuple(ms.BG)):
        for s in streams:
            for g in regimes:
                for r in R["bench"][s][g]["per_recording"]:
                    if r["kind"] == kind:
                        yield s, g, r

    def best(it, key):
        return max(it, key=lambda x: key(x[2]))

    a = best(rows("planted", ("fast",), ("baseline_busy",)),
             lambda r: r["stack"]["decoy_calls"] - r["count_sliding"]["decoy_calls"])
    b = best(rows("planted"),
             lambda r: r["stack"]["under_floor_calls"] - r["count_sliding"]["under_floor_calls"])
    c = best(rows("elevated"),
             lambda r: r["count_sliding"]["calls_in_stretch"] - r["stack"]["calls_in_stretch"])
    return [dict(what="decoys", stream=a[0], regime=a[1], seed=a[2]["seed"], kind="planted"),
            dict(what="under_floor", stream=b[0], regime=b[1], seed=b[2]["seed"],
                 kind="planted"),
            dict(what="elevated", stream=c[0], regime=c[1], seed=c[2]["seed"], kind="elevated")]


def make(p: dict):
    mod = ms.bench_module(p["stream"])
    s, gt = (mod.make_recording if p["kind"] == "planted"
             else mod.make_elevated_rate_recording)(p["regime"], p["seed"])
    dets = {n: ms.run(p["stream"], n, s) for n in ms.DETECTORS}
    return mod, s, gt, dets


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--out", type=Path, default=None,
                    help=f"output folder (default: <darkroom>/{ms.FOLDER})")
    ap.add_argument("--also", type=Path, default=None, help="a second folder for the pages")
    ap.add_argument("--summary", type=Path, default=None,
                    help="measure_stack.py's summary.json (default: the one in --out)")
    a = ap.parse_args(argv)
    out = a.out
    if out is None:
        from bugarach.paths import darkroom
        out = darkroom(ms.FOLDER, create=True)
        if out is None:
            raise SystemExit("no darkroom found; pass --out")
    R = json.loads((a.summary or out / "summary.json").read_text())

    from bugarach import bench
    from bugarach.score import score_stream
    bench.use_spacing(R["settings"]["spacing"])

    made, n, notes = [], FIRST_FIGURE, []
    for p in picks(R):
        mod, s, gt, dets = make(p)
        stream = s.streams[mod.STREAM]
        from bugarach.detectors.rate import recording_extent
        ext = recording_extent(s)
        floor = gt.params.get("event_floor")
        bg = ms.BG[p["regime"]]
        counts = ", ".join(f"{ms.NAME[k]} {len(d.onset_sec)} calls" for k, d in dets.items())
        ident = (f"{p['stream']} bench, {bg} background, seed {p['seed']}, "
                 f"floor {floor} ROIs. {counts}.")
        stack_only = only_in(dets["stack"], dets["count_sliding"])
        count_only = only_in(dets["count_sliding"], dets["stack"])
        sc = score_stream(gt, dets["stack"], tol_sec=mod.TOL_SEC)
        if p["what"] == "decoys":
            title = "a fast, busy recording where stack calls more decoys than count (sliding)"
            decoys = np.asarray(gt.distractor_times, float)
            near = [t for t in stack_only
                    if decoys.size and np.min(np.abs(decoys - t)) <= MATCH_SEC + 2.0]
            centre = float(near[0] if near else (stack_only[0] if stack_only.size
                                                 else ext[1] / 2))
            look = ("Look at the open grey triangles (decoys) in the top lane: stack has a bar "
                    "under more of them than count (sliding) does, each with a red cross.")
        elif p["what"] == "under_floor":
            title = ("the recording where stack calls the most planted events under the floor "
                     "that count (sliding) misses")
            under = np.asarray(gt.times, float)[~np.asarray(sc.care, bool)]
            near = [t for t in stack_only
                    if under.size and np.min(np.abs(under - t)) <= MATCH_SEC + 2.0]
            centre = float(near[0] if near else (stack_only[0] if stack_only.size
                                                 else ext[1] / 2))
            look = ("Look for planted triangles with a stack bar under them and no count "
                    "(sliding) bar: events with fewer ROIs than the floor, which the score "
                    "leaves out for every detector.")
        else:
            h0, h1 = gt.params["hot_window"]
            title = ("an elevated-rate recording: every ROI's rate is raised between "
                     f"{h0 / 60:g} and {h1 / 60:g} minutes and nothing is planted there")
            centre = float(count_only[(count_only >= h0) & (count_only <= h1)][0]
                           if np.any((count_only >= h0) & (count_only <= h1))
                           else (h0 + h1) / 2)
            look = ("Look inside the shaded stretch: every bar there is a false alarm, and "
                    "count (sliding) has more of them than stack.")
        z0 = float(np.clip(centre - ZOOM_SEC / 2, ext[0], ext[1] - ZOOM_SEC))
        for zoom, zext in ((False, ext), (True, (z0, z0 + ZOOM_SEC))):
            scope = (f"close-up, {z0 / 60:.1f} to {(z0 + ZOOM_SEC) / 60:.1f} minutes of the "
                     f"recording in Figure {n - 1}" if zoom else "the whole 45 minutes")
            heading = f"Figure {n}. Simulated: {title} ({scope})."
            png = out / f"fig{n:02d}_raster_{p['what']}{'_closeup' if zoom else ''}.png"
            ok = page(lanes_of(dets), stream, ext=zext, gt=gt, raster_name="simulated",
                      heading=heading, caption=f"{ident} {look} {HOW_TO_READ}", png=png)
            if not ok:
                raise SystemExit(f"could not render {png.name} (playwright chromium missing?)")
            made.append(png)
            notes.append(dict(figure=n, file=png.name, **p, floor=floor, closeup=zoom,
                              window_sec=list(map(float, zext)),
                              calls={k: int(len(d.onset_sec)) for k, d in dets.items()},
                              stack_only=int(stack_only.size), count_sliding_only=int(count_only.size),
                              look=look))
            n += 1
    (out / "rasters.json").write_text(json.dumps(notes, indent=1))
    if a.also:
        import shutil
        a.also.mkdir(parents=True, exist_ok=True)
        for f in made + [out / "rasters.json"]:
            shutil.copy2(f, a.also / f.name)
    for r in notes:
        print(f"Figure {r['figure']}: {r['file']}  {r['stream']} {r['regime']} seed {r['seed']} "
              f"calls {r['calls']} only-stack {r['stack_only']} "
              f"only-count {r['count_sliding_only']}")


if __name__ == "__main__":
    main()
