#!/usr/bin/env python3
"""Show what the promiscuity probe does to a shaped background.

    python tools/probe_vs_heterogeneity.py                 # numbers only
    python tools/probe_vs_heterogeneity.py --out docs/generator

Every quantity quoted in ``docs/generator_revision_input.md`` §1 is printed by
this script, so the claim can be re-derived rather than taken on trust — the same
arrangement `tools/fit_background_shape.py` gives the background-shape fit.

The finding
-----------
``bg_rate_shape`` gives the background a realistic shape: a few busy ROIs, many
near-silent. ``hot_window`` raises **every** ROI by the same absolute rate. Run
both and the second erases the first — the silent ROIs the shape exists to
produce are filled in by the probe, and a recording that was supposed to have a
quiet tail has none.

Both features are individually well-argued. Their product does not look chosen,
which is the point worth putting in front of a parameter revision.

Nothing here is a claim about the preparation. It is arithmetic about the
generator, and the figure is the generator's own output rendered through the
viewer's own raster panel.
"""

from __future__ import annotations

import argparse
import importlib.util
import sys
from pathlib import Path

import numpy as np

SEEDS = tuple(range(1, 41))
"""Enough seeds that the silent fraction is stable to a few tenths of a percent.
Disjoint from nothing in particular — there is no training set here, and the
bench's own scoring seeds (1, 2, 3) are included deliberately so the numbers
describe the recordings the bench actually scores."""


def _bench():
    from bugarach.bench import (
        BENCH_RECORDING,
        MEASURED_BURST_BINS,
        MEASURED_BURST_SHAPE,
        MEASURED_RATE_SHAPE,
    )
    return (BENCH_RECORDING, MEASURED_RATE_SHAPE, MEASURED_BURST_SHAPE,
            MEASURED_BURST_BINS)


def _silent_fraction(*, shape, probe, duration, bg_rate, n_roi, hot, ramp):
    """Fraction of ROIs with no event at all, background only (nothing planted).

    Planted events and distractors are excluded by planting none, rather than by
    generating them and subtracting: subtracting counts is what produced a wrong
    number in the first draft of the handoff, because the hot window is
    background too and does not appear in ``gt``.
    """
    from bugarach.simulate import simulate_coordination

    out = []
    for seed in SEEDS:
        s, _ = simulate_coordination(
            seed=seed, duration_sec=duration, n_roi=n_roi, bg_rate_hz=bg_rate,
            bg_rate_shape=shape, n_per_level=(0, 0, 0), margin_sec=5.0,
            hot_window=hot if probe else None,
            hot_rate_hz=hot[2] if probe else 0.0,
            ramp_sec=ramp if probe else 0.0)
        out.append(np.mean([len(v) == 0 for v in s.streams["events"].locs]))
    return float(np.mean(out))


def numbers():
    BENCH, RATE_SHAPE, BURST_SHAPE, BURST_BINS = _bench()
    from bugarach.simulate import simulate_coordination

    dur = BENCH["duration_sec"]
    n_roi = BENCH["n_roi"]
    hw, hr, ramp = BENCH["hot_window"], BENCH["hot_rate_hz"], BENCH["ramp_sec"]
    bg = 0.0096                       # measured baseline median, per ROI
    hot = (hw[0], hw[1], hr)
    span = hw[1] - hw[0]

    print(f"bench recording: {dur:.0f} s, {n_roi} ROI, background {bg} Hz/ROI")
    print(f"probe: {hw[0]:.0f}-{hw[1]:.0f} s at {hr} Hz/ROI, "
          f"{ramp:.0f} s linear wash-in")
    print()

    # --- how much of an ROI's activity the probe contributes ------------------
    # Measured, not computed: hot_rate_hz * span overstates it, because ramp_sec
    # thins the wash-in and loses half the ramp. That error (18.0 vs 17.1) was a
    # finding against the first draft of the handoff doc.
    probe_only = []
    for seed in SEEDS:
        s, _ = simulate_coordination(
            seed=seed, duration_sec=dur, n_roi=n_roi, bg_rate_hz=0.0,
            n_per_level=(0, 0, 0), hot_window=hw, hot_rate_hz=hr,
            ramp_sec=ramp, margin_sec=5.0)
        probe_only.append(np.mean([len(v) for v in s.streams["events"].locs]))
    probe_events = float(np.mean(probe_only))
    bg_events = bg * dur

    print("events per ROI")
    print(f"   background, whole recording   {bg_events:6.2f}")
    print(f"   probe, naive hot_rate*span    {hr * span:6.2f}   <- overstates")
    print(f"   probe, measured               {probe_events:6.2f}")
    print(f"   probe span                    {span / dur * 100:5.1f}% of the recording")
    print(f"   probe share of activity       {probe_events / (bg_events + probe_events) * 100:5.1f}%")
    print()

    # --- the silent tail, with and without the probe --------------------------
    print("ROIs with no background event at all")
    for label, shape, probe in [
            ("flat background,  probe off", None, False),
            ("flat background,  probe on ", None, True),
            ("fitted shape,     probe off", RATE_SHAPE, False),
            ("fitted shape,     probe on ", RATE_SHAPE, True)]:
        f = _silent_fraction(shape=shape, probe=probe, duration=dur,
                             bg_rate=bg, n_roi=n_roi, hot=hot, ramp=ramp)
        print(f"   {label}   {f * 100:5.1f}%")
    print()

    print("silent fraction vs recording length (fitted shape, probe off)")
    print("   real baseline windows measure ~35% (bench.MEASURED_RATE_SHAPE)")
    for d in (300.0, 600.0, 1200.0, 1800.0, 2700.0, 5400.0):
        f = _silent_fraction(shape=RATE_SHAPE, probe=False, duration=d,
                             bg_rate=bg, n_roi=n_roi, hot=hot, ramp=ramp)
        print(f"   {d:7.0f} s ({d / 60:5.1f} min)   {f * 100:5.1f}%")


FIGURE_SEED = 8
"""The seed the figure draws, chosen to be **representative rather than
flattering**.

Across the 40 seeds this script measures, the silent-ROI count runs 4 to 14 of
33 around a mean of 8.8 (26.7%). Seed 1 — the obvious default, and what the first
draft of this figure used — sits at **14, the maximum of the whole set**, so it
showed the argument at its strongest and would have been the one number a
reviewer could not reproduce. Seed 8 gives 9/33 (27.3%), nearest the mean.
"""


def build(width: int):
    """Three rasters: what the bench runs, what the shape gives, and the product."""
    import holoviews as hv

    from bugarach.simulate import simulate_coordination
    from bugarach.ui.app import _time_axis_hook
    from bugarach.ui.diagnostic import raster_panel

    BENCH, RATE_SHAPE, _, _ = _bench()
    dur, n_roi = BENCH["duration_sec"], BENCH["n_roi"]
    hw, hr, ramp = BENCH["hot_window"], BENCH["hot_rate_hz"], BENCH["ramp_sec"]
    bg = 0.0096

    rows = []
    # Short labels on purpose. The y-label is rotated and laid out against the
    # plot height, so a long one is silently clipped at both ends — a first cut
    # read "14/3", losing a digit off a count. The explanation lives in the
    # caption, where it is set in the document's own type and cannot be cut.
    cases = [
        (None, True, "flat · probe on"),
        (RATE_SHAPE, False, "shaped · probe off"),
        (RATE_SHAPE, True, "shaped · probe on"),
    ]
    for shape, probe, label in cases:
        s, gt = simulate_coordination(
            seed=FIGURE_SEED, duration_sec=dur, n_roi=n_roi, bg_rate_hz=bg,
            bg_rate_shape=shape, n_per_level=(0, 0, 0), margin_sec=5.0,
            hot_window=hw if probe else None,
            hot_rate_hz=hr if probe else 0.0,
            ramp_sec=ramp if probe else 0.0)
        silent = sum(len(v) == 0 for v in s.streams["events"].locs)
        panel = raster_panel(s.streams["events"], ext=(0.0, dur), gt=gt,
                             name=label, width=width, height=170)
        if probe:
            # the probe's own span, so the reader can see which band filled in
            panel = hv.VSpan(hw[0], hw[1]).opts(
                color="#d1892f", alpha=0.13) * panel
        rows.append(panel.opts(
            width=width, height=196, xlim=(0.0, dur), ylim=(-1, n_roi),
            xaxis=None, xlabel="time",
            ylabel=f"{label} · {silent}/{n_roi} silent",
            title="", fontsize={"ylabel": "9pt"}, show_legend=False,
            hooks=[_time_axis_hook]))
    rows[-1] = rows[-1].opts(height=196 + 45, xaxis="bottom")

    layout = rows[0]
    for r in rows[1:]:
        layout = layout + r
    return layout.cols(1).opts(shared_axes=False, merge_tools=True,
                               toolbar=None)


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--out", type=Path, default=None,
                   help="directory for the figure; omit to print numbers only")
    p.add_argument("--width", type=int, default=1000)
    a = p.parse_args(argv)

    numbers()

    if a.out is None:
        print("\n(no --out given, figure not rendered)")
        return 0

    import holoviews as hv
    import panel as pn
    hv.extension("bokeh")

    # Reuse the generator-figure writer rather than re-deriving it: it writes to
    # a temporary name and moves into place, because writing into Dropbox in
    # place left 188 MB of hash-named orphans (its own docstring). It takes a
    # Panel object, not a HoloViews Layout — the same wrapping its own caller does.
    spec = importlib.util.spec_from_file_location(
        "_mgf", Path(__file__).parent / "make_generator_figures.py")
    mgf = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mgf)

    page = pn.Column(
        pn.pane.HTML(
            '<div style="font:13px/1.6 system-ui,sans-serif;max-width:1000px">'
            '<b style="font-size:15px">the probe fills in the quiet tail</b> — '
            'background only, nothing planted. Quietest ROI at the bottom.<br>'
            '<span style="color:#555">'
            '<b>flat</b> = the background the bench runs today · '
            '<b>shaped</b> = <code>bg_rate_shape</code> at its fitted value, which is '
            'what gives a real field its quiet ROIs.<br>'
            'The shaded band is the <b>promiscuity probe</b>: a dense-but-random '
            'block with no planted events, which raises every ROI by the same '
            '<i>absolute</i> rate. <b>shaped \u00b7 probe off</b> has a visibly empty '
            'lower half; <b>shaped \u00b7 probe on</b> is the same recording with '
            'the probe added, and it does not.<br>'
            f'Seed {FIGURE_SEED}, chosen as the seed nearest the 40-seed mean '
            '(26.7% silent) rather than the most striking one.</span></div>'),
        pn.pane.HoloViews(build(a.width)))

    a.out.mkdir(parents=True, exist_ok=True)
    mgf._write(page, a.out, "probe_vs_heterogeneity", png=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
