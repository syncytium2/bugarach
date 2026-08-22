#!/usr/bin/env python3
"""What radar's problem actually is, and where it is ours too.

    python tools/make_clutter_edge_figure.py                      # -> the darkroom
    python tools/make_clutter_edge_figure.py --also docs/learned   # + the repo copy

Radar does **not** need coordination detection. It asks whether there is a target
in *this* cell, one cell at a time; nothing in it corresponds to "are these
channels together". What radar needed — and built CFAR for — is the layer
underneath that question: **a threshold, when the background moves.** That is the
layer coordination detection turned out to need too, which is why the machinery
transferred and the question did not.

**A — the radar problem. Drawn, not measured.** A receiver's output along range,
with a clutter region in the middle: same receiver, same noise process, higher
local power. Two targets of identical strength, one inside the clutter and one
outside. A fixed threshold cannot be placed: low enough to catch the target in the
clear, and the clutter block fires everywhere; high enough to survive the clutter,
and the clear-air target is gone. The CFAR threshold is the local mean of a
reference window either side of the cell under test, times a constant — so it
climbs at the clutter edge and both targets clear it. Synthetic, seeded, and
labelled as a schematic: it illustrates the mechanism the literature describes, it
is not radar data.

**B — the same shape in our own recording. Measured.** The bench recording's
promiscuity block is a rate step with a 30 s ramp and **no planted events**, which
is a clutter edge in this substrate. One coactivity trace, two thresholds: the
stationary bar one-per-region, and LoCo's rolling envelope. Both detectors are run
at **bin_width_sec=1.0** so the two thresholds sit on the same statistic — that is
a deliberate departure from binned SCE's shipped 10 s operating point, because the
panel is about the threshold rule and not about scoring either detector.
"""

from __future__ import annotations

import argparse
import importlib.util
import sys
from pathlib import Path

CLUTTER, FIXED, ADAPTIVE, TARGET = "#c8d6e4", "#a03623", "#2f6f9f", "#16202b"
BENCH_REGIME, SEED, BIN = "baseline_quiet", 3, 1.0


def radar_panel(width):
    """A range profile with a clutter block, seeded — a schematic, not data."""
    import holoviews as hv
    import numpy as np

    rng = np.random.default_rng(12345)
    n, edge_lo, edge_hi = 600, 240, 400
    # Square-law receiver output is exponential in power; the clutter block is the
    # same process at a higher mean, which is exactly what makes a fixed threshold
    # impossible rather than merely badly tuned.
    mean = np.where((np.arange(n) >= edge_lo) & (np.arange(n) < edge_hi), 9.0, 1.0)
    x = rng.exponential(mean)
    tgt_clear, tgt_clutter = 120, 320
    x[tgt_clear] += 11.0          # identical target strength, different backgrounds
    x[tgt_clutter] += 11.0

    # CA-CFAR: mean of a leading and a lagging reference window, with a guard
    # interval so the target cannot inflate the bar it has to clear.
    n_ref, n_guard, alpha = 24, 4, 2.6
    thr = np.full(n, np.nan)
    for i in range(n):
        lo_a, lo_b = i - n_guard - n_ref, i - n_guard
        hi_a, hi_b = i + n_guard + 1, i + n_guard + 1 + n_ref
        ref = np.concatenate([x[max(lo_a, 0):max(lo_b, 0)], x[min(hi_a, n):min(hi_b, n)]])
        if ref.size:
            thr[i] = alpha * ref.mean()

    fixed = 12.0                  # low enough for the clear-air target
    # Every element carries value dimension "p", unique to this panel: two plots
    # sharing a dimension name link their y-ranges, and this figure's whole point
    # is two panels on incomparable scales (CLAUDE.md: unlinked y, linked x).
    band = hv.Area([(edge_lo, 0, 46), (edge_hi, 0, 46)],
                   kdims=["range"], vdims=["p_lo", "p_hi"]).opts(
        color=CLUTTER, line_alpha=0, alpha=.75)
    ret = hv.Spikes((np.arange(n), x), kdims=["range"], vdims=["p"]).opts(
        color="#5c6773", line_width=1.0, alpha=.85)
    fx = hv.Curve([(0, fixed), (n, fixed)], kdims=["range"], vdims=["p"]).opts(
        color=FIXED, line_width=2.0, line_dash="dashed")
    ad = hv.Curve((np.arange(n), thr), kdims=["range"], vdims=["p"]).opts(
        color=ADAPTIVE, line_width=2.2)
    hits = hv.Scatter(([tgt_clear, tgt_clutter], [x[tgt_clear] + 3, x[tgt_clutter] + 3]),
                      kdims=["range"], vdims=["p"]).opts(
        color=TARGET, marker="inverted_triangle", size=11)
    n_fa = int(np.sum(x[edge_lo:edge_hi] > fixed)) - 1   # minus the real target
    notes = [
        hv.Text(tgt_clear, x[tgt_clear] + 6.0, "target,\nclear air").opts(
            text_font_size="8pt", text_color=TARGET, text_align="center"),
        hv.Text(tgt_clutter, 45, "target, in clutter").opts(
            text_font_size="8pt", text_color=TARGET, text_align="center"),
        hv.Text(n - 8, fixed - 2.2, "fixed threshold").opts(
            text_font_size="8pt", text_color=FIXED, text_align="right"),
        hv.Text(n - 8, 31, "CFAR: local mean x constant").opts(
            text_font_size="8pt", text_color=ADAPTIVE, text_align="right"),
        hv.Text(edge_lo - 12, 40,
                f"clutter — the fixed bar\nfires {n_fa}x in here, on nothing").opts(
            text_font_size="8pt", text_color=FIXED, text_align="right"),
    ]
    ov = band * ret * fx * ad * hits
    for t in notes:
        ov = ov * t
    return ov.opts(
        width=width, height=300, xlim=(0, n), ylim=(0, 47),
        xlabel="A · RADAR, drawn not measured — range cell",
        ylabel="receiver output (a.u.)",
        fontsize={"xlabel": "10pt", "ylabel": "10pt", "ticks": "9pt"},
        toolbar=None)


def bugarach_panel(width):
    """The bench recording's rate step, with both threshold rules on one trace."""
    import holoviews as hv
    import numpy as np

    from bugarach.bench import BENCH_RECORDING, make_recording
    from bugarach.detectors.loco import loco_detect
    from bugarach.detectors.rate import recording_extent
    from bugarach.detectors.sce import sce_detect
    from bugarach.ui.app import _time_axis_hook

    slice_, gt = make_recording(BENCH_REGIME, SEED)
    ext = recording_extent(slice_)
    hot_lo, hot_hi = BENCH_RECORDING["hot_window"]

    lo = loco_detect(slice_, rng_seed=7, bin_width_sec=BIN, context_win_sec=120.0,
                     thr_step_sec=15.0, merge_gap_sec=2.0, threshold_pctile=99.9,
                     n_surrogates=100)
    sc = sce_detect(slice_, rng_seed=7, emit_signal=True, bin_width_sec=BIN,
                    threshold_pctile=99.0, n_surrogates=200)
    lr = lo.streams["events"]
    sr = sc.streams["events"]
    t, y = lr.signal.t, lr.signal.y
    # The rolling bar goes infinite where a half-context holds no events at all;
    # that is "nothing could clear this", not a value to draw.
    env = np.asarray(lr.signal.threshold, dtype=float)
    env = np.where(np.isfinite(env), env, np.nan)
    flat = float(np.unique(np.asarray(sr.threshold))[0])

    # Headroom above the trace so the annotations never sit on the data. Value
    # dimension "coact" is unique to this panel — see the note in radar_panel.
    top = float(np.nanmax(y))
    ymax = top + 5.5
    band = hv.Area([(hot_lo, 0, ymax), (hot_hi, 0, ymax)],
                   kdims=["t"], vdims=["c_lo", "c_hi"]).opts(
        color=CLUTTER, line_alpha=0, alpha=.75)
    trace = hv.Curve((t, y), kdims=["t"], vdims=["coact"]).opts(
        color="#5c6773", line_width=.9, alpha=.9)
    fx = hv.Curve([(ext[0], flat), (ext[1], flat)], kdims=["t"],
                  vdims=["coact"]).opts(color=FIXED, line_width=2.0,
                                        line_dash="dashed")
    ad = hv.Curve((t, env), kdims=["t"], vdims=["coact"]).opts(
        color=ADAPTIVE, line_width=1.8)
    planted = np.array([e.time for e in gt.events], dtype=float)
    truth = hv.Scatter((planted, np.full(planted.size, ymax - 1.0)),
                       kdims=["t"], vdims=["coact"]).opts(
        color=TARGET, marker="inverted_triangle", size=8)
    n_hot_sce = int(np.sum((sr.onset_sec >= hot_lo) & (sr.onset_sec <= hot_hi)))
    n_hot_loco = int(np.sum((lr.onset_sec >= hot_lo) & (lr.onset_sec <= hot_hi)))
    notes = [
        hv.Text(ext[1] - 30, flat - 0.75,
                f"stationary bar — {sr.n_events} detections").opts(
            text_font_size="8pt", text_color=FIXED, text_align="right"),
        hv.Text(ext[1] - 30, ymax - 2.6,
                f"rolling bar — {lr.n_events} detections").opts(
            text_font_size="8pt", text_color=ADAPTIVE, text_align="right"),
        hv.Text(hot_lo - 25, ymax - 3.9,
                f"nothing planted here —\nstationary {n_hot_sce}, rolling {n_hot_loco}").opts(
            text_font_size="8pt", text_color=FIXED, text_align="right"),
        # below the marker row, not on it — at ymax - 1.0 this label sat on the
        # first triangle and read as though it annotated that one event
        hv.Text(ext[0] + 25, ymax - 2.5, f"{planted.size} planted").opts(
            text_font_size="8pt", text_color=TARGET, text_align="left"),
    ]
    ov = band * trace * fx * ad * truth
    for n in notes:
        ov = ov * n
    return ov.opts(
        width=width, height=300, xlim=ext, ylim=(0, ymax + 0.4),
        xlabel="B · BUGARACH, measured — the bench recording, both bars on one statistic",
        ylabel=f"distinct ROI per {BIN:g} s bin",
        fontsize={"xlabel": "10pt", "ylabel": "10pt", "ticks": "9pt"},
        toolbar=None, hooks=[_time_axis_hook])


def main(argv=None) -> int:
    p = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    # SAP006: a tool that renders something to be READ defaults to the darkroom.
    p.add_argument("--out", type=Path, default=None)
    p.add_argument("--also", type=Path, default=None)
    p.add_argument("--width", type=int, default=980)
    a = p.parse_args(argv)

    import holoviews as hv
    import panel as pn
    hv.extension("bokeh")

    from bugarach.paths import darkroom

    spec = importlib.util.spec_from_file_location(
        "_mgf", Path(__file__).parent / "make_generator_figures.py")
    mgf = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mgf)

    page = pn.Column(pn.pane.HoloViews(radar_panel(a.width)),
                     pn.pane.HoloViews(bugarach_panel(a.width)))
    dests = [a.out or (darkroom() / "detector_history")]
    if a.also:
        dests.append(a.also)
    for dest in dests:
        dest.mkdir(parents=True, exist_ok=True)
        mgf._write(page, dest, "clutter_edge", png=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
