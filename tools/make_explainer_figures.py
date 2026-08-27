#!/usr/bin/env python3
"""Two things a reader said they could not follow, drawn instead of described.

    python tools/make_explainer_figures.py --spec docs/learned/generator_spec.json \
        --out docs/learned

**K** and **what the model is actually handed** are both load-bearing and both were
prose-only in the report. Tony's note: *"I think I need a figure on what k means. I
also don't understand the input to the model."* Neither is hard to see once drawn —
which is the point, and the reason they were the wrong things to explain in words.

* **`explain_k`** — K is a **threshold on how many cells are active at once**. A bin
  where at least K cells fire counts as co-active; runs of such bins become one
  event. So K is the knob for *what counts as coordination at all*, and raising it
  does not shrink events, it deletes the smaller ones. Drawn as the coactivity trace
  with each candidate K as a line, the surviving bins marked, and the resulting event
  rate beside it — measured off the assessor's own scan, not asserted.
* **`explain_input`** — the model receives **one binary number per cell per frame**:
  did this cell have an onset here. Nothing else. Not amplitude, not width, not the
  fluorescence trace, not the cell's identity — rows are sorted busiest-first, so row
  index means *how active this cell is relative to the others* and nothing more.
  Drawn as the actual encoded array with a planted event zoomed, so the sparsity is
  visible rather than claimed.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from pathlib import Path

import numpy as np

HAND, LEARN, TRUTH = "#4c78a8", "#7a1f22", "#1b7f3b"


def _mgf():
    spec = importlib.util.spec_from_file_location(
        "_mgf", Path(__file__).parent / "make_generator_figures.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def coactivity(enc, bin_frames: int):
    """Cells active per bin — the quantity K thresholds.

    One cell, one vote: a cell active twice inside a bin counts once, which is the
    whole distinction between coordination and one busy cell (GLOSSARY).
    """
    x = (enc.raster > 0)
    n_bins = x.shape[1] // bin_frames
    trimmed = x[:, :n_bins * bin_frames].reshape(x.shape[0], n_bins, bin_frames)
    return trimmed.any(axis=2).sum(axis=0)


def build_k(enc, gt, scan, dt, bin_frames, width, ks=(3, 4, 6, 8)):
    import holoviews as hv

    co = coactivity(enc, bin_frames)
    t = np.arange(len(co)) * bin_frames * dt
    lo, hi = 1150.0, 1450.0                    # a window with planted events in it
    m = (t >= lo) & (t <= hi)

    colours = {3: LEARN, 4: "#b4553f", 6: HAND, 8: "#5c6773"}
    ov = hv.Curve((t[m], co[m]), kdims=["seconds"],
                  vdims=["cells active"]).opts(color="#16202b", line_width=1.4)
    for k in ks:
        ov = ov * hv.HLine(k).opts(color=colours[k], line_width=1.3,
                                   line_dash="dashed")
        ov = ov * hv.Text(hi - 4, k + 0.42, f"K={k}").opts(
            color=colours[k], text_font_size="8pt", text_align="right")
        sel = m & (co >= k)
        if sel.any():
            ov = ov * hv.Scatter((t[sel], np.full(sel.sum(), k))).opts(
                color=colours[k], size=4, marker="square")
    for e in gt.events:
        if e.kind != "coordinated":
            continue
        if lo <= e.time <= hi:
            # Above the trace, so it points down at it — CLAUDE.md, plot
            # conventions. Not a raster, same reason: a marker riding over data
            # is an annotation on the data, and an annotation points at its
            # subject.
            ov = ov * hv.Scatter([(e.time, float(max(ks)) + 1.0)]).opts(
                color=TRUTH, size=9, marker="inverted_triangle")

    # Headroom, explicitly. Auto-ranging cropped the K=6 and K=8 lines and the
    # planted-event markers straight out of the view, while the caption went on
    # promising both — a figure disagreeing with its own caption.
    top = max(int(co[m].max()), max(ks)) + 2
    panelA = ov.opts(
        width=width, height=290, show_grid=True, ylim=(-0.4, top),
        xlabel="A · cells active per bin. Each dashed line is a candidate K; squares are "
               "the bins that survive it; green triangles mark the planted events. "
               "Nothing in this window reaches K=6, which is what raising K costs",
        ylabel="cells active in bin",
        fontsize={"xlabel": "9pt", "ylabel": "10pt", "ticks": "9pt"},
        toolbar=None)

    pts = [(int(k), scan[str(k)]["clusters_permin"]) for k in sorted(scan, key=int)]
    bars = hv.Bars(pts, kdims=["K"], vdims=["events per minute"]).opts(
        color=LEARN, width=width, height=250, show_grid=True,
        xlabel="B · what that threshold costs: events per minute the assessor finds, "
               "measured across 85 real recordings",
        ylabel="events per minute",
        fontsize={"xlabel": "9pt", "ylabel": "10pt", "ticks": "9pt"},
        toolbar=None)
    labels = hv.Labels([(k, v + 0.012, f"{v:.3f}") for k, v in pts]).opts(
        text_font_size="8pt", text_color="#16202b")
    return (panelA + (bars * labels)).cols(1).opts(shared_axes=False, toolbar=None)


def build_input(enc, gt, dt, width):
    import holoviews as hv

    x = (enc.raster > 0).astype(int)
    n_roi, n_frames = x.shape
    rows, cols = np.nonzero(x)

    full = hv.Scatter((cols * dt, rows), kdims=["seconds"], vdims=["row"]).opts(
        color="#16202b", size=1.6, width=width, height=270, invert_yaxis=True,
        xlabel="A · the whole array. One mark = one onset. Rows are sorted "
               "busiest-first, so row 0 is the most active cell",
        ylabel=f"row (0–{n_roi - 1}), sorted by rate",
        fontsize={"xlabel": "9pt", "ylabel": "10pt", "ticks": "9pt"}, toolbar=None)

    # The BIGGEST planted event, not the median one. The median has three
    # participants and renders as two dots, which teaches a reader nothing except
    # that the figure is broken. The largest shows the signature the model has to
    # find, and the empty rows around it are the other half of the lesson.
    coord = [e for e in gt.events if e.kind == "coordinated"]
    ev = max(coord, key=lambda e: e.n_part)
    lo, hi = ev.time - 6.0, ev.time + 6.0
    sel = (cols * dt >= lo) & (cols * dt <= hi)
    zoom = (hv.Scatter((cols[sel] * dt, rows[sel])).opts(
                color="#16202b", size=7, marker="square")
            * hv.VLine(ev.time).opts(color=TRUTH, line_width=1.4, line_dash="dashed")
            * hv.Text(ev.time + 0.3, 1.6,
                      f"planted event — {ev.n_part} of {n_roi} cells").opts(
                color=TRUTH, text_font_size="8pt", text_align="left")
            ).opts(
        width=width, height=250, invert_yaxis=True, xlim=(lo, hi),
        ylim=(-1, n_roi), show_grid=True,
        xlabel="B · twelve seconds around the largest planted event, every frame drawn. "
               "This is the whole of what the model gets: which cells, which frames. "
               "The empty rows are cells that did nothing",
        ylabel="row",
        fontsize={"xlabel": "9pt", "ylabel": "10pt", "ticks": "9pt"}, toolbar=None)
    return (full + zoom).cols(1).opts(shared_axes=False, toolbar=None)


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--spec", type=Path, required=True)
    p.add_argument("--out", type=Path, required=True)
    p.add_argument("--width", type=int, default=920)
    p.add_argument("--seed", type=int, default=1)
    a = p.parse_args(argv)

    import holoviews as hv
    import panel as pn
    hv.extension("bokeh")
    from bugarach.bench import make_recording
    from bugarach.learn.encode import encode

    doc = json.loads(a.spec.read_text())
    gen = {k: v for k, v in doc["generator"].items() if k != "bg_rate_hz"}
    dt = float(doc["generator"]["grid_sec"])
    sl, gt = make_recording("baseline_busy", seed=a.seed, **gen)
    enc = encode(sl, dt=dt)
    bin_frames = max(1, int(round(0.2 / dt)))
    print(f"{enc.raster.shape[0]} rows x {enc.raster.shape[1]} frames, dt={dt}s, "
          f"{int((enc.raster > 0).sum())} onsets, "
          f"{sum(1 for e in gt.events if e.kind == 'coordinated')} coordinated "
          f"(+{sum(1 for e in gt.events if e.kind != 'coordinated')} distractors)")

    mgf = _mgf()
    a.out.mkdir(parents=True, exist_ok=True)
    mgf._write(pn.Column(pn.pane.HoloViews(
        build_k(enc, gt, doc["k_scan"], dt, bin_frames, a.width))),
        a.out, "explain_k", png=True)
    mgf._write(pn.Column(pn.pane.HoloViews(build_input(enc, gt, dt, a.width))),
               a.out, "explain_input", png=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
