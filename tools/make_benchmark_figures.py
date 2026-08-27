#!/usr/bin/env python3
"""What the benchmark actually looks like, beside what the recordings look like.

    python tools/make_benchmark_figures.py <export-folder> --also docs/learned

Two figures for `docs/benchmark_explainer.md`, because every argument about the bench
in the last week was conducted in summary statistics and nobody looked at it.

**benchmark_rasters** — the same 15 minutes of five recordings, drawn identically. Two
real ones from the export folder (the least crowded and the most crowded), then the
three simulated ones: the bench every score is measured on, the crowded diagnostic, and
the tail recording. One row per ROI, one mark per event, quietest ROI at the bottom.

**benchmark_map** — every real recording as a dot: how crowded it is against how many
events an hour it has, with the three simulated recordings on the same axes. This is
the figure that shows what the bench covers and what it does not, and it is how the two
routes into the tail became visible: dense-and-regular, and sparse-but-bursty.

## Nothing is drawn on the raster

CLAUDE.md's plot conventions, and sapper SAP009. The raster is **black and white** —
one ink, one mark per event, nothing competing with it. The coordinated events go in a
**cue lane above** it: open circles for events a detector *found* on a real recording,
filled triangles for events *planted* in a simulated one. Identity and counts go in a
text header outside the plots.

An earlier version of this file drew both the cue marks and the labels straight onto
the raster, which is what prompted the rule. On the two panels that mattered most — the
real recordings, whose busiest ROI runs a near-solid line across the row — the labels
were unreadable and the cue marks were indistinguishable from data.

**Why not `ui.diagnostic.lane_panel`.** That is the right thing to stack above a raster
when there is a detector to score: it draws hits, misses, false alarms and duplicates
against ground truth. Here there is nothing to score — the real recordings have no
ground truth at all, and on the simulated ones the point is what was planted, not how
well anything found it. Its machinery would be inert, so this draws one row of symbols
and says so.
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
INK = "#16202b"
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
                        stream=stream, sim=False,
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
                         stream="events", sim=True,
                         crowded=float(np.mean(nearest_neighbour_gaps(gt)
                                               < CROWDING_GAP_SEC)),
                         rate_per_h=t.size / ((ext[1] - ext[0]) / 3600.0),
                         cv=float(d.std(ddof=1) / d.mean())))
    return rows


def header(row):
    """Identity and counts, as text OUTSIDE any plot — never over the marks."""
    import panel as pn
    col = SIM if row["sim"] else REAL
    kind = "planted" if row["sim"] else "detected"
    bits = (f"{row['crowded']:.2f} crowded &middot; {row['rate_per_h']:.0f} "
            f"coordinated events/h ({kind}) &middot; CV {row['cv']:.2f}")
    if row.get("note"):
        bits += f" &middot; {row['note']}"
    return pn.pane.HTML(
        f'<div style="font:600 13px/1.35 system-ui,sans-serif;color:{col};'
        f'margin:16px 0 0 92px">{row["slice_id"]}'
        f'<div style="font:400 11px/1.5 system-ui,sans-serif;color:{RULE}">'
        f'{bits}</div></div>', height=46, margin=0)


def cue_lane(row, ext, width):
    """One row of symbols, ABOVE the raster, x-linked to it through ``t``.

    A unique y dimension name per lane, per CLAUDE.md: holoviews links y-ranges
    between panels that share a dimension NAME, and a lane sharing the raster's
    name inherits its 0–40 ROI range and collapses into a sliver.
    """
    import holoviews as hv
    ons = np.asarray(row["onsets"], float)
    ons = ons[(ons >= ext[0]) & (ons <= ext[1])]
    ydim = f"cue_{abs(hash(row['slice_id'])) % 100000}"
    lane = hv.Scatter(([ext[0]], [0.0]), kdims=["t"], vdims=[ydim]).opts(alpha=0)
    if ons.size:
        lane = lane * hv.Scatter(
            (ons, np.zeros(ons.size)), kdims=["t"], vdims=[ydim]).opts(
            marker="triangle" if row["sim"] else "circle",
            size=9, color=SIM if row["sim"] else REAL,
            fill_alpha=1.0 if row["sim"] else 0.0, line_width=1.6)
    return lane.opts(width=width, height=34, xaxis=None, yaxis=None,
                     xlim=(ext[0], ext[1]), ylim=(-1, 1),
                     show_legend=False, toolbar=None)


def clean_raster(row, ext, width, last):
    """The raster, and only the raster. One ink, one mark per event."""
    from bugarach.ui.diagnostic import raster_panel
    n_roi = row["slice"].streams[row["stream"]].n_rois
    raster = raster_panel(row["slice"].streams[row["stream"]], ext=ext,
                          name=row["stream"], width=width, height=150,
                          mark_px=2.0)
    return raster.opts(
        width=width, height=170 if last else 150,
        # the axis hook gives 60-base ticks ("2m", "4m"), so the label must not
        # say seconds — CLAUDE.md's minutes-friendly rule, one step further
        xlabel="time from the start of the recording" if last else "",
        xaxis="bottom" if last else None,
        ylabel=f"{n_roi} ROI", ylim=(-1, n_roi + 1),
        show_legend=False,
        fontsize={"ylabel": "9pt", "xlabel": "10pt", "ticks": "9pt"},
        toolbar=None)


def build_map(real, sims, width):
    import holoviews as hv
    x = np.array([r["crowded"] for r in real])
    y = np.array([r["rate_per_h"] for r in real])
    els = [hv.Scatter((x, y), "crowded", "rate").opts(color=REAL, size=7, alpha=.8)]
    for r in sims:
        els.append(hv.Scatter([(r["crowded"], r["rate_per_h"])],
                              "crowded", "rate").opts(
            color=SIM, size=15, marker="triangle", line_color=INK, line_width=1))
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
    lo = min(real, key=lambda r: (r["crowded"], -r["onsets"].size))
    hi = max(real, key=lambda r: r["crowded"])
    lo = dict(lo, slice_id=f"{lo['slice_id']} — a real recording, uncrowded")
    hi = dict(hi, slice_id=f"{hi['slice_id']} — a real recording, the crowded end")
    rows = [lo, hi] + sims

    print("  rasters, in order:")
    for r in rows:
        print(f"    {r['slice_id'][:52]:52s} crowded {r['crowded']:.2f}  "
              f"{r['rate_per_h']:5.1f} ev/h  CV {r['cv']:.2f}")

    spec = importlib.util.spec_from_file_location(
        "_mgf", Path(__file__).parent / "make_generator_figures.py")
    mgf = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mgf)

    panes = []
    for i, r in enumerate(rows):
        ext = (r["ext"][0], min(r["ext"][1], r["ext"][0] + WINDOW_SEC))
        panes.append(header(r))
        panes.append(pn.pane.HoloViews(cue_lane(r, ext, a.width)))
        panes.append(pn.pane.HoloViews(
            clean_raster(r, ext, a.width, last=(i == len(rows) - 1))))
    panes.append(pn.pane.HTML(
        f'<div style="font:400 11px/1.6 system-ui,sans-serif;color:{RULE};'
        f'margin:8px 0 0 92px">&#9650; planted coordinated event '
        f'&nbsp;&nbsp;&nbsp; &#9675; coordinated event a detector found'
        f'<br>the cue lane sits above each raster; the raster itself is the '
        f'recording and nothing else</div>', height=44, margin=0))
    rasters = pn.Column(*panes)
    the_map = pn.Column(pn.pane.HoloViews(build_map(real, sims, a.width)))

    dests = [a.out or (darkroom() / "detector_history")]
    if a.also:
        dests.append(a.also)
    for dest in dests:
        dest.mkdir(parents=True, exist_ok=True)
        mgf._write(rasters, dest, "benchmark_rasters", png=True)
        mgf._write(the_map, dest, "benchmark_map", png=True)
        print(f"  wrote {dest}/benchmark_rasters.png and benchmark_map.png")
    return 0


if __name__ == "__main__":
    sys.exit(main())
