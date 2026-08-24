#!/usr/bin/env python3
"""Draw the two pictures behind `docs/detector_history.md`.

    python tools/make_cfar_figures.py                      # -> the darkroom
    python tools/make_cfar_figures.py --also docs/learned  # + the repo copy

**A — the promiscuity probe, ordered by where each detector's threshold comes
from.** The probe block contains no planted events, so every firing inside it is
a false alarm by construction. Plotted against F1 on a log firing axis, the
detectors separate by *null locality* rather than by statistic: the two whose bar
is one number per region fire 59 and 215 times, and the two whose bar follows
local density fire 1 and 2. That is a 100-fold separation along the axis radar's
CFAR literature is organised around, and it is the evidence the history document
rests on.

**B — where each rolling detector draws its background estimate.** A CFAR
detector excludes the cells immediately around the one under test — the guard
interval — so a real event cannot leak into the estimate of the background it is
judged against. None of bugarach's three rolling detectors has one; this panel
draws the windows from the shipped defaults so the omission is visible rather
than argued.

Numbers come from `docs/learned/bakeoff.json` (panel A) and from the detector
docstrings' shipped defaults (panel B); nothing here is hand-entered except the
family labels, which are this document's reading and are stated as such.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from pathlib import Path

# Null locality is the axis the figure exists to show, so it is the colour.
STATIONARY, BROKEN, LOCAL, INTRINSIC = "#a03623", "#d6883a", "#2f6f9f", "#6b6b6b"
FAMILY = {
    "cicada": ("locust", STATIONARY),
    "sce": ("binned SCE", STATIONARY),
    "rate": ("rate+context", BROKEN),
    "sync": ("SPIKE-synch", INTRINSIC),
    "loco": ("LoCo", LOCAL),
    "coact": ("CoactDetect", LOCAL),
}
LEGEND = [("one bar per region (stationary)", STATIONARY),
          ("rolling window, additive bar", BROKEN),
          ("rolling window, rate-local bar", LOCAL),
          ("self-normalising, no bar", INTRINSIC)]


def _rows(d):
    out = []
    for k, v in d["hand_written"].items():
        name, colour = FAMILY[k]
        out.append(dict(key=k, name=name, colour=colour,
                        f1=v["f1"]["mean"], probe=v["hot_fa"]["mean"],
                        recall=v["recall"]))
    return sorted(out, key=lambda r: r["probe"])


def build_a(rows, width, n_folds):
    import holoviews as hv

    # log x: the spread is 1.2 to 215, and a linear axis collapses the whole
    # rate-local end into the origin — which is the half the figure is about.
    floor = 0.8   # CoactDetect's 1.2 must sit off the axis edge on a log scale
    # Hand-placed, because six points at these coordinates cannot be laid out by
    # a rule: CoactDetect and LoCo sit within 0.013 of F1 of each other, so a
    # uniform "label to the right" put LoCo's name beside CoactDetect's marker
    # and each read as labelling the other. Offsets are (x-factor, y-offset,
    # alignment) and every one of them is checked against the render.
    PLACE = {
        "coact": (1.30, +0.035, "left"),
        "loco": (1.30, -0.035, "left"),
        "sync": (1.35, 0.0, "left"),
        "rate": (1.35, 0.0, "left"),
        "sce": (1.35, 0.0, "left"),
        "cicada": (0.72, 0.0, "right"),
    }
    ov = None
    for r in rows:
        x = max(r["probe"], floor)
        pt = hv.Scatter([(x, r["f1"])], kdims=["probe"], vdims=["F1"]).opts(
            color=r["colour"], size=13, marker="circle", alpha=.92,
            line_color="#16202b", line_width=1.0)
        fx, dy, align = PLACE[r["key"]]
        t = hv.Text(x * fx, r["f1"] + dy, r["name"]).opts(
            text_align=align, text_font_size="9pt",
            text_color="#16202b", text_baseline="middle")
        ov = (pt * t) if ov is None else ov * pt * t
    for label, colour in LEGEND:
        ov = ov * hv.Scatter([(float("nan"), float("nan"))], label=label).opts(
            color=colour, size=9, marker="circle")
    return ov.opts(
        width=width, height=380, logx=True, xlim=(0.45, 900), ylim=(0.15, 0.80),
        xlabel="A · firings inside a block containing no planted events "
               "(mean of %d folds, log)" % n_folds,
        ylabel="F1 on the held-out fold (mean of %d)" % n_folds,
        show_legend=True, legend_position="bottom_right",
        fontsize={"xlabel": "10pt", "ylabel": "10pt", "ticks": "9pt",
                  "legend": "8pt"},
        toolbar=None)


def build_b(width):
    """Reference-window geometry at the shipped FAST defaults, one lane each."""
    import holoviews as hv

    from bugarach.ui.app import _time_axis_hook

    # The anchor sits at t = 0 and the axis runs either side of it. An absolute
    # placement (150 s, say) renders ticks like "2m30s" that a reader takes for
    # real recording times; the only quantity this panel is about is distance
    # FROM the moment under test.
    a = 0.0
    lanes = [
        # label, half-window reach each side, drawn as two abutting halves?
        ("LoCo · anchor, 120 s context", 60.0, True,
         "two halves, both touching the anchor"),
        ("CoactDetect · bin, 60 s context", 30.0, False,
         "one window, centred on the bin under test"),
        ("rate+context · 60 s context", 30.0, False,
         "centred mean, test window inside it"),
    ]
    rows = []
    for i, (label, reach, split, note) in enumerate(lanes):
        y = len(lanes) - i
        band = hv.Area([(a - reach, y - .30, y + .30),
                        (a + reach, y - .30, y + .30)],
                       kdims=["t"], vdims=["lo", "hi"]).opts(
            color="#c8d6e4", line_color="#7f9db9", line_width=1.0, alpha=.85)
        rows.append(band)
        # LoCo's two halves meet AT the anchor, so its seam and the moment under
        # test are the same line — drawing a dotted seam under the red bar put
        # an invisible element in the figure. The note text carries it instead.
        del split
        # the moment under test: a hard bar, and it sits INSIDE the band above
        rows.append(hv.Curve([(a, y - .30), (a, y + .30)], kdims=["t"]).opts(
            color="#a03623", line_width=3.0))
        rows.append(hv.Text(a + reach + 8, y, note).opts(
            text_align="left", text_font_size="8pt", text_color="#5a5a5a",
            text_baseline="middle"))
        rows.append(hv.Text(a - reach - 8, y, label).opts(
            text_align="right", text_font_size="9pt", text_color="#16202b",
            text_baseline="middle"))
    ov = rows[0]
    for r in rows[1:]:
        ov = ov * r
    return ov.opts(
        width=width, height=250, xlim=(-240, 175), ylim=(0.3, 3.9), yaxis=None,
        xlabel="B · time either side of the moment under test (red bar). It "
               "lies inside every window that judges it: no guard interval "
               "anywhere.",
        fontsize={"xlabel": "10pt", "ticks": "9pt"},
        toolbar=None, hooks=[_time_axis_hook])


def main(argv=None) -> int:
    p = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--bakeoff", type=Path,
                   default=Path("docs/learned/bakeoff.json"))
    # SAP006: a tool that renders something to be READ defaults to the darkroom.
    p.add_argument("--out", type=Path, default=None,
                   help="destination (default: the darkroom)")
    p.add_argument("--also", type=Path, default=None,
                   help="extra copy, e.g. the repo's docs/learned")
    p.add_argument("--width", type=int, default=920)
    a = p.parse_args(argv)

    import holoviews as hv
    import panel as pn
    hv.extension("bokeh")

    from bugarach.paths import darkroom

    spec = importlib.util.spec_from_file_location(
        "_mgf", Path(__file__).parent / "make_generator_figures.py")
    mgf = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mgf)

    d = json.loads(a.bakeoff.read_text())
    rows = _rows(d)
    page = pn.Column(
        pn.pane.HoloViews(build_a(rows, a.width, d["folds"])),
        pn.pane.HoloViews(build_b(a.width)))

    dests = [a.out or (darkroom() / "detector_history")]
    if a.also:
        dests.append(a.also)
    for dest in dests:
        dest.mkdir(parents=True, exist_ok=True)
        mgf._write(page, dest, "cfar_map", png=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
