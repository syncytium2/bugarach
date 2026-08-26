#!/usr/bin/env python3
"""What the benchmark actually looks like, beside what the recordings look like.

    python tools/make_benchmark_figures.py <export-folder> --also docs/learned

Two figures for `docs/benchmark_explainer.md`, because every argument about the bench
in the last week has been conducted in summary statistics and nobody has looked at it.

**benchmark_rasters** — the same 15 minutes of five recordings, drawn identically. Two
real ones from the export folder (the least crowded and the most crowded), then the
three simulated ones: the bench every score is measured on, the crowded diagnostic, and
the tail recording. One row per ROI, one mark per event, quietest ROI at the bottom.
Ticks above each panel are the coordinated events — **detected** on the real rows, since
real recordings have no ground truth, and **planted** on the simulated ones.

**benchmark_map** — every real recording as a dot: how crowded it is against how many
events an hour it has. The three simulated recordings are drawn on the same axes. This
is the figure that shows what the bench covers and what it does not, and it is how the
two routes into the tail became visible: dense-and-regular, and sparse-but-bursty.

Rasters reuse `bugarach.ui.diagnostic.raster_panel` rather than drawing their own, so
the picture here and the picture in the viewer are the same picture.
"""

from __future__ import annotations

import argparse
import importlib.util
import sys
from pathlib import Path

import numpy as np

WINDOW_SEC = 900.0          # the same 15 minutes for every row
REAL = "#3f4b57"
SIM = "#a03623"
MARK = "#16202b"
RULE = "#6b7784"


def _load_real(folder, stream="fast"):
    """Every characterizable recording, with its crowding and its event rate."""
    from bugarach.bench import CROWDING_GAP_SEC, OPERATING_POINTS
    from bugarach.detectors.coact import coact_detect
    from bugarach.detectors.rate import recording_extent, stream_trains
    from bugarach.io import load_folder

    params = dict(OPERATING_POINTS["coact"].params)
    out = []
    for s in load_folder(folder):
        if stream not in s.streams:
            continue
        ext = recording_extent(s)
        det = coact_detect(stream_trains(s.streams[stream], ext), ext,
                           rng_seed=20260706, **params)
        on = np.sort(np.asarray(det.onset_sec, float))
        if on.size < 4:
            continue
        d = np.diff(on)
        nn = np.minimum(np.r_[d, np.inf], np.r_[np.inf, d])
        hours = (ext[1] - ext[0]) / 3600.0
        out.append(dict(slice=s, slice_id=s.slice_id, ext=ext, onsets=on,
                        crowded=float(np.mean(nn < CROWDING_GAP_SEC)),
                        rate_per_h=on.size / hours,
                        cv=float(d.std(ddof=1) / d.mean())))
    return out


def _sim_rows():
    from bugarach.bench import (CROWDING_GAP_SEC, make_crowded_recording,
                                make_recording, make_tail_recording,
                                nearest_neighbour_gaps)
    from bugarach.detectors.rate import recording_extent
    rows = []
    for name, maker, note in (
            ("the bench — every score is measured here", make_recording,
             "events 120 s apart · nothing can crowd"),
            ("the crowded diagnostic", make_crowded_recording,
             "14 s floor · nothing is calibrated here"),
            ("the tail recording", make_tail_recording,
             "6 s floor · fitted to the crowded end of the folder")):
        sl, gt = maker("baseline_quiet", 1)
        ext = recording_extent(sl)
        t = np.sort(np.asarray(gt.times, float))
        d = np.diff(t)
        rows.append(dict(slice=sl, slice_id=name, note=note, ext=ext, onsets=t,
                         crowded=float(np.mean(nearest_neighbour_gaps(gt)
                                               < CROWDING_GAP_SEC)),
                         rate_per_h=t.size / ((ext[1] - ext[0]) / 3600.0),
                         cv=float(d.std(ddof=1) / d.mean()),
                         stream="events"))
    return rows


def raster_row(row, width, last):
    """One recording's first WINDOW_SEC, drawn the way the viewer draws it."""
    import holoviews as hv
    from bugarach.ui.diagnostic import raster_panel

    ext = (row["ext"][0], min(row["ext"][1], row["ext"][0] + WINDOW_SEC))
    panel = raster_panel(row["slice"].streams[row.get("stream", "fast")],
                         ext=ext, name=row.get("stream", "fast"),
                         width=width, height=150, mark_px=2.0)
    ons = row["onsets"]
    ons = ons[(ons >= ext[0]) & (ons <= ext[1])]
    for t in ons:
        panel = panel * hv.VLine(t).opts(color=SIM if row.get("sim") else MARK,
                                         line_width=1.1, alpha=.55)
    # The identity goes INSIDE the panel, not in the y label. Five rows of
    # two-line y labels is five rows of clipped text — the first render of this
    # figure lost the recording id off the left edge of every panel.
    n_roi = row["slice"].streams[row.get("stream", "fast")].n_rois
    col = SIM if row.get("sim") else REAL
    # the label sits ABOVE every mark, in space made for it. Laid over the raster
    # it was unreadable on exactly the two panels that matter most — the real
    # recordings, whose busiest ROI runs the full width of the row.
    x0 = ext[0] + 0.010 * (ext[1] - ext[0])
    panel = panel * hv.Text(x0, n_roi * 1.30, row["slice_id"]).opts(
        text_align="left", text_font_size="10pt", text_color=col,
        text_baseline="middle", text_font_style="bold")
    panel = panel * hv.Text(x0, n_roi * 1.13,
                            f"{row['crowded']:.2f} crowded · "
                            f"{row['rate_per_h']:.0f} coordinated events/h · "
                            f"CV {row['cv']:.2f}"
                            + (f" · {row['note']}" if row.get("note") else "")).opts(
        text_align="left", text_font_size="8pt", text_color=RULE,
        text_baseline="middle")
    return panel.opts(width=width, height=185,
                      xlabel="time (s from the start of the recording)" if last else "",
                      xaxis="bottom" if last else None,
                      ylabel=f"{n_roi} ROI", ylim=(-1, n_roi * 1.42),
                      show_legend=False,
                      fontsize={"ylabel": "9pt", "xlabel": "10pt", "ticks": "9pt"},
                      toolbar=None)


def build_map(real, sims, width):
    import holoviews as hv
    x = np.array([r["crowded"] for r in real])
    y = np.array([r["rate_per_h"] for r in real])
    els = [hv.Scatter((x, y), "crowded", "rate").opts(
        color=REAL, size=7, alpha=.8)]
    for r in sims:
        els.append(hv.Scatter([(r["crowded"], r["rate_per_h"])],
                              "crowded", "rate").opts(
            color=SIM, size=15, marker="triangle", line_color=MARK, line_width=1))
        els.append(hv.Text(r["crowded"], r["rate_per_h"] + 4,
                           r["slice_id"].split(" — ")[0]).opts(
            text_align="center", text_font_size="9pt", text_color=SIM,
            text_baseline="bottom"))
    els.append(hv.Text(0.60, float(np.median(y)), "real recordings").opts(
        text_align="left", text_font_size="9pt", text_color=REAL,
        text_baseline="middle"))
    ov = els[0]
    for e in els[1:]:
        ov = ov * e
    return ov.opts(
        width=width, height=430,
        xlabel="crowded — fraction of events with another inside ±30 s",
        ylabel=f"events per hour · {len(real)} real recordings",
        xlim=(-0.04, 0.78), ylim=(-3, max(float(y.max()), 65.0) + 12),
        show_legend=False,
        fontsize={"xlabel": "10pt", "ylabel": "9pt", "ticks": "9pt"}, toolbar=None)


def main(argv=None) -> int:
    p = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("folder", type=Path, help="an export folder")
    # SAP006: a tool that renders something to be READ defaults to the darkroom.
    p.add_argument("--out", type=Path, default=None)
    p.add_argument("--also", type=Path, default=None)
    p.add_argument("--width", type=int, default=920)
    a = p.parse_args(argv)

    import holoviews as hv
    import panel as pn
    hv.extension("bokeh")

    from bugarach.paths import darkroom

    real = _load_real(a.folder)
    sims = _sim_rows()
    for r in sims:
        r["sim"] = True

    lo = min(real, key=lambda r: (r["crowded"], -r["onsets"].size))
    hi = max(real, key=lambda r: r["crowded"])
    for r in (lo, hi):
        r["stream"] = "fast"
    lo["slice_id"] = f"{lo['slice_id']} — a real recording, uncrowded"
    hi["slice_id"] = f"{hi['slice_id']} — a real recording, the crowded end"

    rows = [lo, hi] + sims
    print("  rasters, in order:")
    for r in rows:
        print(f"    {r['slice_id'][:52]:52s} crowded {r['crowded']:.2f}  "
              f"{r['rate_per_h']:5.1f} ev/h  CV {r['cv']:.2f}")

    spec = importlib.util.spec_from_file_location(
        "_mgf", Path(__file__).parent / "make_generator_figures.py")
    mgf = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mgf)

    dests = [a.out or (darkroom() / "detector_history")]
    if a.also:
        dests.append(a.also)

    rasters = pn.Column(*[pn.pane.HoloViews(
        raster_row(r, a.width, last=(i == len(rows) - 1)))
        for i, r in enumerate(rows)])
    the_map = pn.Column(pn.pane.HoloViews(build_map(real, sims, a.width)))

    for dest in dests:
        dest.mkdir(parents=True, exist_ok=True)
        mgf._write(rasters, dest, "benchmark_rasters", png=True)
        mgf._write(the_map, dest, "benchmark_map", png=True)
        print(f"  wrote {dest}/benchmark_rasters.png and benchmark_map.png")
    return 0


if __name__ == "__main__":
    sys.exit(main())
