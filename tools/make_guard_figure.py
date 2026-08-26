#!/usr/bin/env python3
"""Draw where the guard interval moves the bar.

    python tools/make_guard_figure.py                      # -> the darkroom
    python tools/make_guard_figure.py --also docs/learned   # + the repo copy

One panel. For each detector, recording and guard width, the shift the guard makes
to the detector's own bar — split by whether the excised band actually held any
events. Bars to the right of zero mean the guard RAISED the threshold; to the left,
lowered it.

**The claim the picture carries:** the two strata point in opposite directions. A
guard that lowered the bar because its reference got smaller would push both strata
the same way; one that relieves self-masking moves only the stratum where it removed
something. Neither is what happens — the empty stratum moves the *other* way, because
compaction packs the retained events onto a shorter line and raises their density.

Numbers come from ``tools/probe_guard_where_it_lands.py``, imported rather than
recomputed, so the figure and `docs/reviews/guard_where_it_lands_2026-08-25.md`
cannot drift apart. Nothing here is hand-entered.
"""

from __future__ import annotations

import argparse
import importlib.util
import sys
from pathlib import Path

import numpy as np

# the two strata are the whole argument, so they are the colour
EMPTY, OCCUPIED = "#a03623", "#2f6f9f"
NOISY = "#9aa4ae"


def _probe():
    spec = importlib.util.spec_from_file_location(
        "_pg", Path(__file__).parent / "probe_guard_where_it_lands.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def collect(pg, crowded):
    from bugarach.bench import make_crowded_recording, make_recording
    makers = [("bench", lambda s: make_recording(pg.REGIME, s))]
    if crowded:
        makers.insert(0, ("crowded", lambda s: make_crowded_recording(pg.REGIME, s)))
    rows = []
    for label, maker in makers:
        for which in ("loco", "coact"):
            for g in pg.GUARDS:
                e, o, ps = pg.run(which, maker, g)
                # "every seed agrees" is the honest strength test, not a p-value:
                # 4 seeds cannot support one, and a sign that flips per seed is
                # exactly what a bare pooled mean would hide
                flip = bool(np.all(ps[:, 0] > 0) and np.all(ps[:, 1] < 0))
                # as a PERCENTAGE of the bar it moved. LoCo's bar sits near 2.9 and
                # CoactDetect's near 0.5, so absolute shifts are not comparable
                # between them and a shared axis silently favours the larger bar.
                be, bo = float(e[1].mean()), float(o[1].mean())
                rows.append(dict(
                    rec=label, det="LoCo" if which == "loco" else "CoactDetect",
                    guard=g, flip=flip,
                    d_empty=100 * float(e[0].mean()) / be,
                    sd_empty=100 * float(ps[:, 0].std(ddof=1)) / be,
                    d_occ=100 * float(o[0].mean()) / bo,
                    sd_occ=100 * float(ps[:, 1].std(ddof=1)) / bo,
                    bar_empty=be, bar_occ=bo,
                    n_empty=int(e.shape[1]), n_occ=int(o.shape[1])))
    return rows


def build(rows, width):
    import holoviews as hv

    lanes, ticks = [], []
    y = 0.0
    for r in rows[::-1]:                       # holoviews y grows upward
        star = "" if r["flip"] else "  (inside seed noise)"
        ticks.append((y, f"{r['rec']} · {r['det']} · {r['guard']:.0f}s{star}"))
        col_e = EMPTY if r["flip"] else NOISY
        col_o = OCCUPIED if r["flip"] else NOISY
        for d, sd, col, dy in ((r["d_empty"], r["sd_empty"], col_e, +0.18),
                               (r["d_occ"], r["sd_occ"], col_o, -0.18)):
            lanes.append(hv.Segments([(0.0, y + dy, d, y + dy)]).opts(
                color=col, line_width=9, alpha=.92))
            lanes.append(hv.Segments([(d - sd, y + dy, d + sd, y + dy)]).opts(
                color="#16202b", line_width=1.4, alpha=.75))
        y += 1.0

    ov = lanes[0]
    for e in lanes[1:]:
        ov = ov * e
    ov = ov * hv.VLine(0).opts(color="#16202b", line_width=1.2, line_dash="dotted")

    # An in-figure key, not a legend: the NaN-scatter proxy holoviews wants for a
    # legend does not render beside Segments, and a colour nothing identifies is a
    # defect whether or not the legend call succeeded.
    hi = max(r["d_empty"] + r["sd_empty"] for r in rows)
    lo = min(r["d_occ"] - r["sd_occ"] for r in rows)
    span = hi - lo
    kx = hi - 0.02 * span
    for dy, col, txt in ((0.62, EMPTY, "the excised band held NO events"),
                         (0.20, OCCUPIED, "the excised band held events")):
        ov = ov * hv.Text(kx, len(rows) - 1 + dy, txt).opts(
            text_align="right", text_font_size="9pt", text_color=col,
            text_baseline="middle")

    return ov.opts(
        width=width, height=70 + 52 * len(rows),
        xlabel="shift the guard makes to the detector's own bar, as % of that bar "
               "(with guard − without)",
        ylabel="", yticks=ticks, ylim=(-0.6, len(rows) - 0.15),
        xlim=(lo - 0.06 * span, hi + 0.06 * span),
        show_legend=False,
        fontsize={"xlabel": "10pt", "ticks": "9pt"},
        toolbar=None)


def main(argv=None) -> int:
    p = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    # SAP006: a tool that renders something to be READ defaults to the darkroom.
    p.add_argument("--out", type=Path, default=None,
                   help="destination (default: the darkroom)")
    p.add_argument("--also", type=Path, default=None, help="extra copy, e.g. docs/learned")
    p.add_argument("--width", type=int, default=940)
    p.add_argument("--no-crowded", action="store_true",
                   help="bench only — faster, and drops the rows the finding rests on")
    a = p.parse_args(argv)

    import holoviews as hv
    import panel as pn
    hv.extension("bokeh")

    from bugarach.paths import darkroom

    pg = _probe()
    rows = collect(pg, crowded=not a.no_crowded)
    for r in rows:
        print(f"  {r['rec']:8s} {r['det']:12s} {r['guard']:4.0f}s  "
              f"empty {r['d_empty']:+6.2f}% +-{r['sd_empty']:5.2f} (n={r['n_empty']:5d}) "
              f"on bar {r['bar_empty']:.2f}   "
              f"occupied {r['d_occ']:+6.2f}% +-{r['sd_occ']:5.2f} (n={r['n_occ']:5d}) "
              f"on bar {r['bar_occ']:.2f}   "
              f"{'flip' if r['flip'] else 'noisy'}")

    spec = importlib.util.spec_from_file_location(
        "_mgf", Path(__file__).parent / "make_generator_figures.py")
    mgf = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mgf)

    page = pn.Column(pn.pane.HoloViews(build(rows, a.width)))
    dests = [a.out or (darkroom() / "detector_history")]
    if a.also:
        dests.append(a.also)
    for dest in dests:
        dest.mkdir(parents=True, exist_ok=True)
        mgf._write(page, dest, "guard_where_it_lands", png=True)
        print(f"  wrote {dest}/guard_where_it_lands.png")
    return 0


if __name__ == "__main__":
    sys.exit(main())
