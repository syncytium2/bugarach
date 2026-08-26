#!/usr/bin/env python3
"""Draw whether the bench can show a guard effect at all, and then whether it does.

    python tools/make_guard_bench_validity_figure.py                     # -> darkroom
    python tools/make_guard_bench_validity_figure.py --also docs/learned  # + repo copy

**Top panel — where the simulated recordings sit in the real range.** One dot per real
recording in the export folder, x = the fraction of its detected events with another
inside their own ±30 s reference window, sorted. The two rules are what the simulator
plants: the bench at **0.00**, the `crowded` diagnostic at **0.38**. Read the top panel
first, because it decides what the bottom one is worth.

**Bottom panel — six rows,** three recordings crossed with the flat field the bench
ships and the fitted Gamma field `assess` measures off real recordings. Each dot is one
guard configuration's **best F1 over the alpha grid** minus the no-guard
configuration's, so zero is "the guard bought nothing" and the grey band is the no-guard
row's own spread across 12 seeds.

**The claim the picture carries, and it is about the instrument before it is about the
guard.** The four rows marked *mutual masking impossible* have a measured crowding
fraction of **0.00**: `BENCH_RECORDING` plants events 120 s apart against a ±30 s
reference window, so no planted event is ever inside another's context and the thing
guard cells exist for cannot happen there. Those rows cannot answer the question
whatever their dots do. Only the two `crowded` rows can.

Numbers come from ``tools/probe_guard_norm_bench.py`` and
``tools/probe_real_crowding.py``, imported or read from their own JSON rather than
recomputed here.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from pathlib import Path

import numpy as np

# same palette as make_guard_norm_bench_figure.py: red is 5 s, blue 20 s, and the
# open marker is the shipped `compact` normalization
STYLE = {
    "5s compact":   ("#a03623", False),
    "5s exposure":  ("#a03623", True),
    "20s compact":  ("#2f6f9f", False),
    "20s exposure": ("#2f6f9f", True),
}
BAND = "#c9d2da"
RULE = "#16202b"
DEAD = "#9aa4ae"
NICE = {"baseline_quiet": "quiet", "baseline_busy": "busy", "crowded": "crowded"}


def _probe():
    spec = importlib.util.spec_from_file_location(
        "_pgnb", Path(__file__).parent / "probe_guard_norm_bench.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def rows_for(pg, rows):
    """One entry per (field, recording), with each config's best-F1 delta."""
    out = []
    for field in ("flat", "fitted"):
        for regime in pg.REGIMES:
            sub = [r for r in rows if r["field"] == field and r["regime"] == regime]
            if not sub:
                continue
            best = {}
            for _, _, label in pg.CONFIGS:
                rs = [r for r in sub if r["label"] == label]
                best[label] = max(rs, key=lambda r: r["f1"])
            base = best["no guard"]
            out.append(dict(
                field=field, regime=regime, crowded=sub[0]["crowded_frac"],
                sd=base["seed_sd"], base_f1=base["f1"],
                delta={k: v["f1"] - base["f1"] for k, v in best.items()
                       if k != "no guard"},
                alpha={k: v["alpha"] for k, v in best.items()}))
    return out


def build(entries, width):
    import holoviews as hv

    els, ticks = [], []
    y = 0.0
    for e in entries[::-1]:                     # holoviews y grows upward
        dead = e["crowded"] <= 0.0
        tag = "  ⟂ mutual masking impossible" if dead else f"  · {e['crowded']:.0%} crowded"
        ticks.append((y, f"{NICE[e['regime']]} · {e['field']} field{tag}"))
        els.append(hv.Rectangles([(-e["sd"], y - 0.38, e["sd"], y + 0.38)]).opts(
            color=BAND, line_alpha=0, alpha=.75 if not dead else .35))
        for i, (label, (col, filled)) in enumerate(STYLE.items()):
            d = e["delta"][label]
            dy = 0.27 - 0.18 * i
            els.append(hv.Scatter([(d, y + dy)]).opts(
                color=(col if not dead else DEAD), size=10,
                marker="circle", fill_alpha=1.0 if filled else 0.0, line_width=2))
        y += 1.0

    ov = els[0]
    for e in els[1:]:
        ov = ov * e
    ov = ov * hv.VLine(0).opts(color=RULE, line_width=1.2, line_dash="dotted")

    # the x range has to hold the WHOLE band, both sides. Clipping its left half at
    # the axis edge draws a band that appears to start at the frame, which reads as
    # one-sided when the claim is that zero sits in the middle of it.
    reach = max(max(abs(v) for v in e["delta"].values()) for e in entries)
    reach = max(reach, max(e["sd"] for e in entries))
    return ov.opts(
        width=width, height=90 + 58 * len(entries),
        xlabel="best F1 minus the no-guard configuration's best  "
               "(alpha re-swept for each, 12 seeds)",
        ylabel="", yticks=ticks, ylim=(-0.6, len(entries) - 0.35),
        xlim=(-reach * 1.12, reach * 1.12),
        show_legend=False, fontsize={"xlabel": "10pt", "ticks": "9pt"},
        toolbar=None)


def build_crowding(crowd, width):
    """Every real recording as one dot, sorted by how crowded it is, against the two
    values the simulator plants. No binning choice to argue about, and no recording
    hidden inside a bar."""
    import holoviews as hv

    fr = np.sort(np.array([r["crowded_frac"] for r in crowd["recordings"]]))
    n = fr.size
    els = [hv.Scatter((fr, np.arange(n)), "crowded_frac", "rank").opts(
        color="#3f4b57", size=6, alpha=.85)]
    for x, col, txt in ((crowd["bench_planted"], "#a03623",
                         "the bench plants 0.00"),
                        (crowd["crowded_planted"], "#2f6f9f",
                         "the crowded diagnostic plants 0.38")):
        els.append(hv.VLine(x).opts(color=col, line_width=1.8, line_dash="dashed"))
        els.append(hv.Text(x + 0.012, n * 0.30, txt).opts(
            text_align="left", text_font_size="9pt", text_color=col,
            text_baseline="middle"))
    ov = els[0]
    for e in els[1:]:
        ov = ov * e
    above = int((fr > crowd["crowded_planted"]).sum())
    return ov.opts(
        width=width, height=250,
        xlabel="fraction of a recording's detected events with another inside "
               "its own ±30 s reference window",
        ylabel=f"real recordings · {n} · {above} above 0.38",
        xlim=(-0.03, max(0.62, float(fr.max()) + 0.03)), ylim=(-1.5, n + 1.5),
        show_legend=False, fontsize={"xlabel": "10pt", "ylabel": "9pt", "ticks": "9pt"},
        toolbar=None)


def key(width):
    """In-figure key: holoviews will not render a legend across per-element styling,
    and a color nothing identifies is a defect whether or not the call succeeded."""
    import holoviews as hv
    els, y = [], 0
    for label, (col, filled) in STYLE.items():
        els.append(hv.Scatter([(0.02, y)]).opts(
            color=col, size=10, marker="circle",
            fill_alpha=1.0 if filled else 0.0, line_width=2))
        els.append(hv.Text(0.06, y, label).opts(
            text_align="left", text_font_size="9pt", text_color=col,
            text_baseline="middle"))
        y -= 1
    for txt in ("band = no-guard best F1 ± its spread across 12 seeds",
                "⟂ = no planted event is ever inside another's reference window,",
                "      so the guard's mutual-masking half cannot fire on that row"):
        els.append(hv.Text(0.06, y, txt).opts(
            text_align="left", text_font_size="9pt", text_color=RULE,
            text_baseline="middle"))
        y -= 1
    ov = els[0]
    for e in els[1:]:
        ov = ov * e
    return ov.opts(width=width, height=150, xaxis=None, yaxis=None,
                   xlim=(-0.01, 1.0), ylim=(y + 0.3, 0.7), show_legend=False,
                   toolbar=None)


def main(argv=None) -> int:
    p = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    # SAP006: a tool that renders something to be READ defaults to the darkroom.
    p.add_argument("--out", type=Path, default=None, help="destination (default: darkroom)")
    p.add_argument("--also", type=Path, default=None, help="extra copy, e.g. docs/learned")
    p.add_argument("--width", type=int, default=940)
    p.add_argument("--from-json", type=Path, default=None,
                   help="reuse a sweep written by probe_guard_norm_bench.py --json")
    p.add_argument("--crowding-json", type=Path, default=None,
                   help="the JSON from probe_real_crowding.py — draws the top panel. "
                        "Without it the figure is the bench talking about itself.")
    a = p.parse_args(argv)

    import holoviews as hv
    import panel as pn
    hv.extension("bokeh")

    from bugarach.paths import darkroom

    pg = _probe()
    rows = json.loads(a.from_json.read_text()) if a.from_json else pg.collect()
    entries = rows_for(pg, rows)
    for e in entries:
        ds = "  ".join(f"{k} {v:+.3f}" for k, v in e["delta"].items())
        print(f"  {e['regime']:15s} {e['field']:7s} crowded {e['crowded']:.2f}  "
              f"base F1 {e['base_f1']:.3f} sd {e['sd']:.3f} | {ds}")

    panes = []
    if a.crowding_json:
        crowd = json.loads(a.crowding_json.read_text())
        fr = np.array([r["crowded_frac"] for r in crowd["recordings"]])
        print(f"  real crowding: {fr.size} recordings, median {np.median(fr):.2f}, "
              f"IQR {np.percentile(fr, 25):.2f}-{np.percentile(fr, 75):.2f}, "
              f"range {fr.min():.2f}-{fr.max():.2f}")
        panes.append(pn.pane.HoloViews(build_crowding(crowd, a.width)))
    panes += [pn.pane.HoloViews(build(entries, a.width)),
              pn.pane.HoloViews(key(a.width))]
    page = pn.Column(*panes)

    spec = importlib.util.spec_from_file_location(
        "_mgf", Path(__file__).parent / "make_generator_figures.py")
    mgf = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mgf)

    dests = [a.out or (darkroom() / "detector_history")]
    if a.also:
        dests.append(a.also)
    for dest in dests:
        dest.mkdir(parents=True, exist_ok=True)
        mgf._write(page, dest, "guard_bench_validity", png=True)
        print(f"  wrote {dest}/guard_bench_validity.png")
    return 0


if __name__ == "__main__":
    sys.exit(main())
