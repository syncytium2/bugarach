#!/usr/bin/env python3
"""Draw the gap-dependent gain a matched threshold change cannot buy.

    python tools/make_tail_figure.py --from-json tail.json --also docs/learned

Two rows, one x axis: each planted event's own nearest-neighbour gap, tightest on the
left. `<10s` is the bin `CROWDED_RECORDING` cannot populate at all — its floor is 14 s —
and `bench.TAIL_RECORDING` exists to reach it.

**Top — recall.** Grey is no guard at the shipped alpha. Blue is a 20 s guard with the
`exposure` normalization. The dashed line is the **control**: no guard at all, alpha
loosened until its overall recall matches the guarded run. It lands on the guard in
every bin but the tightest.

**Bottom — guard minus control**, paired per seed. A uniform loosening is subtracted
out, so only a gap-dependent component can survive. One bin does, and it is the bin
where events sit inside each other's reference window.

Numbers come from ``tools/probe_guard_in_the_tail.py``.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from pathlib import Path

import numpy as np

BASE = "#6b7784"
GUARD = "#2f6f9f"
CTRL = "#a03623"
RULE = "#16202b"
BAND = "#c9d2da"


def _probe():
    spec = importlib.util.spec_from_file_location(
        "_pt", Path(__file__).parent / "probe_guard_in_the_tail.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def build_recall(d, width):
    import holoviews as hv
    labels = d["labels"]
    x = np.arange(len(labels))
    vd = "recall_tail"
    series = [("no guard", np.nanmean(np.array(d["recall"]["no guard"]), 0),
               BASE, "solid", 3.0),
              ("20s exposure guard", np.nanmean(np.array(d["recall"]["20s exposure"]), 0),
               GUARD, "solid", 3.0),
              (f"no guard @ alpha {float(d['control_alpha']):.0e}  (the control)",
               np.nanmean(np.array(d["control_recall"]), 0), CTRL, "dashed", 2.4)]
    els = []
    for name, y, col, dash, lw in series:
        els.append(hv.Curve((x, y), "gap", vd).opts(
            color=col, line_dash=dash, line_width=lw))
        els.append(hv.Scatter((x, y), "gap", vd).opts(color=col, size=8))
    hi = max(float(np.nanmax(s[1])) for s in series)
    lo = min(float(np.nanmin(s[1])) for s in series)
    for i, (name, _, col, _, _) in enumerate(series):
        els.append(hv.Text(len(labels) - 0.55, lo + (0.16 - 0.075 * i) * (hi - lo),
                           name).opts(text_align="right", text_font_size="9pt",
                                      text_color=col, text_baseline="middle"))
    ov = els[0]
    for e in els[1:]:
        ov = ov * e
    n = sum(d["planted"])
    return ov.opts(width=width, height=250, xaxis=None,
                   ylabel=f"recall · {int(n)} planted events",
                   xlim=(-0.35, len(labels) - 0.5), ylim=(lo - 0.04, hi + 0.03),
                   show_legend=False,
                   fontsize={"ylabel": "9pt", "ticks": "9pt"}, toolbar=None)


def build_residual(d, width):
    import holoviews as hv
    labels = d["labels"]
    x = np.arange(len(labels))
    res = d["residual"]
    m = np.array(res["mean"], float)
    sd = np.array(res["sd"], float)
    vd = "delta_tail"
    els = [hv.Rectangles([(-0.35, -0.004, len(labels) - 0.5, 0.004)],
                         kdims=["gap", vd, "gap2", f"{vd}_hi"]).opts(
        color=BAND, line_alpha=0, alpha=.6)]
    for i in x:
        els.append(hv.Segments([(i, m[i] - sd[i], i, m[i] + sd[i])],
                               kdims=["gap", vd, "gap2", f"{vd}_hi"]).opts(
            color=RULE, line_width=1.4, alpha=.7))
        els.append(hv.Segments([(i, 0.0, i, m[i])],
                               kdims=["gap", vd, "gap2", f"{vd}_hi"]).opts(
            color=GUARD, line_width=10, alpha=.9))
    els.append(hv.Scatter((x, m), "gap", vd).opts(color=GUARD, size=10))
    for i in x:
        els.append(hv.Text(i, m[i] + sd[i] + 0.012,
                           f"{res['agree'][i]}/{res['n']}").opts(
            text_align="center", text_font_size="8pt", text_color=RULE))
    ov = els[0]
    for e in els[1:]:
        ov = ov * e
    ov = ov * hv.HLine(0).opts(color=RULE, line_width=1.2, line_dash="dotted")
    top = float(np.max(m + sd)) + 0.045
    bot = float(np.min(m - sd)) - 0.02
    return ov.opts(
        width=width, height=290,
        xlabel="each planted event's own nearest-neighbour gap  (tightest on the left)",
        xticks=[(i, l) for i, l in enumerate(labels)],
        ylabel="guard − control, paired  (± sd over seeds)",
        xlim=(-0.35, len(labels) - 0.5), ylim=(bot, top),
        show_legend=False,
        fontsize={"xlabel": "10pt", "ylabel": "9pt", "ticks": "9pt"}, toolbar=None)


def main(argv=None) -> int:
    p = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    # SAP006: a tool that renders something to be READ defaults to the darkroom.
    p.add_argument("--out", type=Path, default=None, help="destination (default: darkroom)")
    p.add_argument("--also", type=Path, default=None)
    p.add_argument("--width", type=int, default=900)
    p.add_argument("--from-json", type=Path, default=None,
                   help="a run written by probe_guard_in_the_tail.py --json")
    p.add_argument("--seeds", type=int, default=24)
    a = p.parse_args(argv)

    import holoviews as hv
    import panel as pn
    hv.extension("bokeh")

    from bugarach.paths import darkroom

    if a.from_json:
        d = json.loads(a.from_json.read_text())
    else:
        pt = _probe()
        r = pt.collect(tuple(range(1, a.seeds + 1)))
        d = dict(labels=pt.LABELS, control_alpha=r["control_alpha"],
                 planted=r["base"]["planted"],
                 recall={k: v["recall"].tolist() for k, v in r["runs"].items()},
                 control_recall=r["control"]["recall"].tolist(),
                 residual={k: (v.tolist() if isinstance(v, np.ndarray) else v)
                           for k, v in r["residual"].items()})

    res = d["residual"]
    for i, l in enumerate(d["labels"]):
        print(f"  {l:>8s}  guard-control {res['mean'][i]:+.3f} ± {res['sd'][i]:.3f}  "
              f"{res['agree'][i]}/{res['n']} seeds agree")

    page = pn.Column(pn.pane.HoloViews(build_recall(d, a.width)),
                     pn.pane.HoloViews(build_residual(d, a.width)))

    spec = importlib.util.spec_from_file_location(
        "_mgf", Path(__file__).parent / "make_generator_figures.py")
    mgf = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mgf)

    dests = [a.out or (darkroom() / "detector_history")]
    if a.also:
        dests.append(a.also)
    for dest in dests:
        dest.mkdir(parents=True, exist_ok=True)
        mgf._write(page, dest, "guard_in_the_tail", png=True)
        print(f"  wrote {dest}/guard_in_the_tail.png")
    return 0


if __name__ == "__main__":
    sys.exit(main())
