#!/usr/bin/env python3
"""Draw the guard's empty-stratum rise landing on its closed form, and then leaving.

    python tools/make_guard_exposure_figure.py                    # -> the darkroom
    python tools/make_guard_exposure_figure.py --also docs/learned  # + the repo copy

One panel, two lanes per row. Each segment runs from 1.0 — no change — out to the
factor by which the guard multiplied CoactDetect's own bar, split by whether the
excised band held any events.

**The claim the picture carries.** On the ``compact`` lanes the empty-stratum segment
stops at the open marker, which is the closed form ``C / (C - guard)`` and not a fit:
the rise where the guard removed *nothing* is a normalization, arithmetic that would be
there if the recording contained no biology at all. On the ``exposure`` lanes — where
the guard drops the excised events and keeps the window length — that segment collapses
to the line, and the occupied segment gets **longer**, because the normalization had
been cancelling part of the masking relief.

Numbers come from ``tools/probe_guard_exposure.py``, imported rather than recomputed,
so this figure and ``docs/reviews/guard_prior_art_2026-08-26.md`` cannot drift apart.
"""

from __future__ import annotations

import argparse
import importlib.util
import sys
from pathlib import Path

import numpy as np

# same two strata, same two colours as make_guard_figure.py — the reader meets
# this figure next to that one and a recoloured stratum reads as a new variable
EMPTY, OCCUPIED = "#a03623", "#2f6f9f"
RULE, PRED = "#16202b", "#6b7784"


def _probe():
    spec = importlib.util.spec_from_file_location(
        "_pge", Path(__file__).parent / "probe_guard_exposure.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def collect(pg, crowded, n_sur):
    from bugarach.bench import make_crowded_recording, make_recording
    makers = [("bench", lambda s: make_recording(pg.REGIME, s))]
    if crowded:
        makers.insert(0, ("crowded", lambda s: make_crowded_recording(pg.REGIME, s)))
    rows = []
    for label, maker in makers:
        for g in pg.GUARDS:
            for norm in ("compact", "exposure"):
                e, o, p, ps = pg.run_coact(maker, g, norm, n_sur)
                rows.append(dict(
                    rec=label, guard=g, norm=norm,
                    empty=float(np.nanmean(e)), occ=float(np.nanmean(o)),
                    # spread ACROSS SEEDS, not across bins: bins within one seed
                    # share a recording and a surrogate pool, so a bin-wise sd
                    # would flatter every row here
                    sd_empty=float(np.nanstd(ps[:, 0], ddof=1)),
                    sd_occ=float(np.nanstd(ps[:, 1], ddof=1)),
                    pred=float(np.nanmean(p)) if norm == "compact" else 1.0,
                    n_empty=int(np.isfinite(e).sum()), n_occ=int(np.isfinite(o).sum()),
                    seeds_below=int(np.sum(ps[:, 1] < 1.0))))
    return rows


def build(rows, width):
    import holoviews as hv

    lanes, ticks = [], []
    y = 0.0
    for r in rows[::-1]:                       # holoviews y grows upward
        ticks.append((y, f"{r['rec']} · {r['guard']:.0f}s · {r['norm']}"))
        for v, sd, col, dy in ((r["empty"], r["sd_empty"], EMPTY, +0.18),
                               (r["occ"], r["sd_occ"], OCCUPIED, -0.18)):
            lanes.append(hv.Segments([(1.0, y + dy, v, y + dy)]).opts(
                color=col, line_width=9, alpha=.92))
            lanes.append(hv.Segments([(v - sd, y + dy, v + sd, y + dy)]).opts(
                color=RULE, line_width=1.4, alpha=.75))
        if r["norm"] == "compact":
            # the closed form, drawn where the measurement should stop if it is right
            lanes.append(hv.Scatter([(r["pred"], y + 0.18)]).opts(
                color=PRED, marker="circle", size=11, fill_alpha=0.0, line_width=1.8))
        y += 1.0

    ov = lanes[0]
    for e in lanes[1:]:
        ov = ov * e
    ov = ov * hv.VLine(1.0).opts(color=RULE, line_width=1.2, line_dash="dotted")

    hi = max(max(r["empty"] + r["sd_empty"], r["pred"]) for r in rows)
    lo = min(r["occ"] - r["sd_occ"] for r in rows)
    span = hi - lo
    kx = hi - 0.02 * span
    for dy, col, txt in (
            (0.66, EMPTY, "the excised band held NO events"),
            (0.30, OCCUPIED, "the excised band held events"),
            (-0.06, PRED, "○  C / (C − guard), the closed form")):
        ov = ov * hv.Text(kx, len(rows) - 1 + dy, txt).opts(
            text_align="right", text_font_size="9pt", text_color=col,
            text_baseline="middle")

    return ov.opts(
        width=width, height=70 + 52 * len(rows),
        xlabel="factor the guard applies to CoactDetect's own bar  "
               "(bar with guard ÷ bar without)",
        ylabel="", yticks=ticks, ylim=(-0.6, len(rows) - 0.15),
        xlim=(lo - 0.06 * span, hi + 0.06 * span),
        show_legend=False,
        fontsize={"xlabel": "10pt", "ticks": "9pt"},
        toolbar=None)


def main(argv=None) -> int:
    p = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    # SAP006: a tool that renders something to be READ defaults to the darkroom.
    p.add_argument("--out", type=Path, default=None, help="destination (default: darkroom)")
    p.add_argument("--also", type=Path, default=None, help="extra copy, e.g. docs/learned")
    p.add_argument("--width", type=int, default=940)
    p.add_argument("--surrogates", type=int, default=500)
    p.add_argument("--no-crowded", action="store_true",
                   help="bench only — faster, and drops the rows the finding rests on")
    a = p.parse_args(argv)

    import holoviews as hv
    import panel as pn
    hv.extension("bokeh")

    from bugarach.paths import darkroom

    pg = _probe()
    rows = collect(pg, crowded=not a.no_crowded, n_sur=a.surrogates)
    for r in rows:
        print(f"  {r['rec']:8s} {r['guard']:4.0f}s {r['norm']:9s}  "
              f"empty x{r['empty']:.4f} +-{r['sd_empty']:.4f} (n={r['n_empty']:5d}) "
              f"predicted x{r['pred']:.4f}   "
              f"occupied x{r['occ']:.4f} +-{r['sd_occ']:.4f} (n={r['n_occ']:5d}) "
              f"{r['seeds_below']}/{len(pg.SEEDS)} seeds below 1")

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
        mgf._write(page, dest, "guard_exposure", png=True)
        print(f"  wrote {dest}/guard_exposure.png")
    return 0


if __name__ == "__main__":
    sys.exit(main())
