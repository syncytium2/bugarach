#!/usr/bin/env python3
"""Draw the fair bake-off: accuracy with its spread, and what each detector costs.

    python tools/make_bakeoff_figures.py --bakeoff docs/learned/bakeoff.json \
        --out docs/learned

Two panels, because the question has two halves and a table hides both.

**A — accuracy, with every fold drawn.** A bar of means invites a ranking; the
folds are drawn as points on top of it so the overlap is visible. The previous
report ranked seven detectors over an F1 spread of 0.011 and called it an
ordering, which is the defect this panel exists to prevent.

**B — the deployability plane.** Detection time against accuracy, log time, marker
area by parameter count. For a model that is going to be retrained inside an app
on a lab's own recordings, "how good" and "how expensive" are one decision, and
plotting them apart lets a reader make it wrong.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from pathlib import Path

HAND, LEARN = "#4c78a8", "#7a1f22"
ARCH = {"tube": "centre−surround (learned)", "trace": "pooled trace (learned)",
        "tiny": "per-cell bank (learned)"}


def _rows(d):
    from bugarach.ui.app import TITLES
    out = []
    for k, v in d["hand_written"].items():
        out.append(dict(name=TITLES.get(k, k), kind="hand", f1=v["f1"],
                        fit=v["calibrate_sec"]["mean"],
                        detect=v["detect_sec"]["mean"], params=0,
                        folds=[f["f1"] for f in v["per_fold"]],
                        probe=v["hot_fa"]["mean"]))
    for k, v in d["learned"].items():
        out.append(dict(name=ARCH.get(k, k), kind="learned", f1=v["f1"],
                        fit=v["train_sec"]["mean"],
                        detect=v["detect_sec"]["mean"], params=v["n_params"],
                        folds=[f["f1"] for f in v["per_fold"]],
                        probe=v["hot_fa"]["mean"]))
    return sorted(out, key=lambda r: -r["f1"]["mean"])


def build(d, width=920):
    import holoviews as hv
    import numpy as np

    rows = _rows(d)
    n_folds = d["folds"]

    # --- A: accuracy, means with every fold on top ---------------------------
    bars = hv.Bars([(r["name"], r["f1"]["mean"]) for r in rows],
                   kdims=["detector"], vdims=["F1"]).opts(
        color=hv.dim("detector").categorize(
            {r["name"]: (LEARN if r["kind"] == "learned" else HAND)
             for r in rows}, default="#8c8c8c"),
        width=width, height=390, ylim=(0, 1.0), xrotation=40,
        ylabel=f"A · F1 on the held-out fold (mean of {n_folds})", xlabel="",
        show_legend=False,
        fontsize={"ylabel": "10pt", "ticks": "9pt"})
    pts = hv.Scatter([(r["name"], f) for r in rows for f in r["folds"]],
                     kdims=["detector"], vdims=["F1"]).opts(
        color="#16202b", size=6, marker="circle", alpha=.85)
    panelA = (bars * pts).opts(width=width, height=390)

    # --- B: the deployability plane ------------------------------------------
    def _sz(p):
        # marker area by parameter count; the hand-written detectors have no
        # trained parameters, so they get the floor rather than vanishing
        return 9.0 if p == 0 else 9.0 + 13.0 * np.sqrt(p / 2400.0)

    ov = None
    for r in rows:
        c = LEARN if r["kind"] == "learned" else HAND
        s = hv.Scatter([(r["detect"], r["f1"]["mean"])],
                       kdims=["detect_sec"], vdims=["F1"]).opts(
            color=c, size=_sz(r["params"]), marker="circle", alpha=.9)
        # vertical whisker: the fold range, so the plane carries its own error
        w = hv.Curve([(r["detect"], min(r["folds"])),
                      (r["detect"], max(r["folds"]))]).opts(color=c,
                                                            line_width=1.4,
                                                            alpha=.6)
        # The rightmost marker's label ran off the panel when centred on it, so
        # labels anchor inward at the edges of the time axis.
        xs = [q["detect"] for q in rows]
        if r["detect"] >= max(xs):
            align, tx = "right", r["detect"] * 0.92
        elif r["detect"] <= min(xs):
            align, tx = "left", r["detect"] * 1.08
        else:
            align, tx = "center", r["detect"]
        t = hv.Text(tx, max(r["folds"]) + 0.035, r["name"]).opts(
            color=c, text_font_size="8pt", text_align=align)
        ov = (s * w * t) if ov is None else ov * s * w * t

    panelB = ov.opts(
        width=width, height=430, logx=True,
        xlabel="B · seconds to detect one held-out fold "
               f"({d['seeds_per_fold']} recordings) — log scale",
        ylabel="F1 (bar = fold range)", ylim=(0, 1.05),
        fontsize={"ylabel": "10pt", "xlabel": "10pt", "ticks": "9pt"},
        toolbar=None)

    return (panelA + panelB).cols(1).opts(shared_axes=False, toolbar=None)


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--bakeoff", type=Path, required=True)
    p.add_argument("--out", type=Path, required=True)
    p.add_argument("--width", type=int, default=920)
    a = p.parse_args(argv)

    import holoviews as hv
    import panel as pn
    hv.extension("bokeh")

    spec = importlib.util.spec_from_file_location(
        "_mgf", Path(__file__).parent / "make_generator_figures.py")
    mgf = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mgf)

    d = json.loads(a.bakeoff.read_text())
    a.out.mkdir(parents=True, exist_ok=True)
    mgf._write(pn.Column(pn.pane.HoloViews(build(d, a.width))),
               a.out, "bakeoff", png=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
