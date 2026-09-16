#!/usr/bin/env python3
"""Draw what the second sensor buys: the bake-off, and the probe that separates the plants.

    python tools/make_line_sensors_figure.py --bakeoff <folder> --probe <folder> --out <folder>

Reads ``bakeoff.json`` from ``tools/fair_bakeoff.py`` and ``line_vs_fuzz.json`` from
``tools/probe_line_vs_fuzz.py``. Writes ``line_sensors_fig.png``. Exploratory.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from matplotlib.lines import Line2D  # noqa: E402

ORDER = ["line", "line_length", "tube", "tube_guard", "tube_ratio", "tube_ratio_guard",
         "tiny", "trace", "coact", "loco", "rate", "cicada", "sce", "sync"]
"""Grouped by family, NOT sorted by score. `tools/make_bakeoff_summary_figure.py` carries the
reason as a murderboard finding of 2026-09-07: a chart ordered by F1 says "ranking" before its
label is read, and at four folds these are intervals rather than an ordering."""
LABEL = {"line": "line\n(two sensors)", "line_length": "line_length\n(length only)",
         "tube": "tube", "tube_guard": "tube_guard", "coact": "CoactDetect", "loco": "LoCo",
         "rate": "rate+context", "cicada": "locust", "sce": "binned SCE", "sync": "SPIKE-synch",
         "tiny": "tiny", "trace": "trace", "tube_ratio": "tube_ratio",
         "tube_ratio_guard": "tube_ratio_guard"}
COMPARISONS = [("burst", "-", "÷ burst (same ink, a quarter of the ROIs)"),
               ("fuzz", "-.", "÷ fuzz (same ROIs, spread over 2.9 s)"),
               ("wave", "--", "÷ wave (same ROIs, one frame apart)")]
"""All three comparisons the probe computes. `fuzz` was measured for every model and plant size,
named the tool (`probe_line_vs_fuzz.py`), introduced in the caption as one of four equal-ink
plants — and drawn nowhere, because the constant that listed it was never read in `main()`. Three
blind reviewers found the same hole independently; it is the comparison closest to what the second
sensor is supposed to measure."""

YLIM_F1 = (-0.03, 0.9)
"""Shared with Figure 2's panels A and B so a score carries between the two figures."""


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--bakeoff", required=True)
    ap.add_argument("--probe", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--k", type=int, default=16)
    a = ap.parse_args(argv)
    bake = json.loads((Path(a.bakeoff) / "bakeoff.json").read_text())
    probe = json.loads((Path(a.probe) / "line_vs_fuzz.json").read_text())["scores"]
    rows = {**bake["hand_written"], **bake["learned"]}

    fig, (ax, bx) = plt.subplots(1, 2, figsize=(13.5, 5.4),
                                 gridspec_kw={"width_ratios": [1.6, 1]})
    names = [n for n in ORDER if n in rows]
    y = np.arange(len(names))[::-1]
    rs = np.random.RandomState(0)
    # The FOUR FOLDS, drawn as four points, with a bar for the mean only. A dot-with-a-range-bar on
    # a stacked categorical axis is the visual grammar of a forest plot, where the bar is a
    # confidence interval and non-overlap reads as significance — and this page's central claim is
    # that the ordering is NOT separable. The idiom is recognised before the axis label is read, so
    # the label saying "fold range" could not undo it. Four dots say "four measurements" instead,
    # and it is the same language Figure 2 already uses for its fits.
    for i, n in zip(y, names):
        f = rows[n]["f1"]
        c = "#1f4e79" if n == "line" else ("#7b3294" if n == "line_length" else "#4d4d4d")
        per = [d["f1"] for d in sorted(rows[n]["per_fold"], key=lambda d: d["fold"])]
        ax.plot(per, i + rs.uniform(-0.16, 0.16, len(per)), "o", color=c, ms=4.2,
                alpha=0.65, mew=0.4, mec="white")
        ax.plot([f["mean"]] * 2, [i - 0.3, i + 0.3], color=c, lw=2.4)
    ax.set_yticks(y, [LABEL.get(n, n).replace("\n", " ") for n in names], fontsize=8.5)
    ax.set_xlim(*YLIM_F1)
    ax.set_xlabel("planted-truth F1 on the held-out fold, one bake-off run of four folds\n"
                  "(dot: one fold; bar: mean over the four — NOT a confidence interval)",
                  fontsize=9)
    ax.text(-0.21, 1.06, "A", transform=ax.transAxes, fontsize=12, fontweight="bold", va="top")

    # Ratios, not absolute responses: subtracting the unplanted field removes each model's offset
    # but not its gain, so only a ratio compares models. And every K that was measured is drawn —
    # the separation the orientation channels buy appears at the largest plant and not below it.
    models = [("supervised line", "line (two sensors)", "#1f4e79"),
              ("supervised line_length", "line_length (length only)", "#7b3294"),
              ("supervised tube", "tube", "#4d4d4d")]
    Ks = sorted({int(k.split("_")[1]) for k in probe["supervised line"] if k.startswith("line_")
                 and not k.endswith(("sd",))})
    # An OPEN marker where the denominator is within one standard deviation of zero over the 12
    # fields. A ratio whose divisor is consistent with no response is not a measurement of
    # discrimination, and the largest numbers in this panel are exactly those cells.
    for m, lab, colour in models:
        r = probe[m]
        for plant, style, _ in COMPARISONS:
            vals = [r[f"line_{K}"] / r[f"{plant}_{K}"] for K in Ks]
            bx.plot(Ks, vals, style, color=colour, lw=1.4, zorder=2)
            for K, v in zip(Ks, vals):
                shaky = abs(r[f"{plant}_{K}"]) < r.get(f"{plant}_{K}_sd", 0.0)
                bx.plot([K], [v], "o", ms=4.6, zorder=3, color="white" if shaky else colour,
                        mec=colour, mew=1.3)
    bx.axhline(1.0, color="0.55", ls=":", lw=0.9)
    bx.set_xscale("log", base=2)
    bx.set_xticks(Ks, [str(K) for K in Ks])
    bx.set_xlabel("plant size: ROIs' worth of onsets (log₂ spacing)", fontsize=9)
    bx.set_ylabel("the line's response ÷ the other plant's\n(above 1: the line answers more)",
                  fontsize=9)
    bx.text(-0.20, 1.06, "B", transform=bx.transAxes, fontsize=12, fontweight="bold", va="top")
    # Two keys, labelled, because colour and line style encode different things and a flat list
    # made a reader deduce that "tube" and "÷ burst" are not the same kind of entry. Both sit in
    # the upper RIGHT: every series falls from left to right, so the left is where the ink is and
    # the previous placement put the key on top of the two largest points in the panel.
    lg = bx.legend(handles=[Line2D([], [], color=c, lw=1.6, label=lab) for _, lab, c in models],
                   title="model", frameon=False, fontsize=7.5, title_fontsize=7.5,
                   alignment="left", loc="upper right", bbox_to_anchor=(1.0, 1.0))
    bx.add_artist(lg)
    bx.legend(handles=[Line2D([], [], color="0.3", ls=s, label=lab) for _, s, lab in COMPARISONS]
              + [Line2D([], [], color="white", marker="o", ls="", ms=5, mec="0.3", mew=1.3,
                        label="open: divisor within 1 SD of zero")],
              title="compared against", frameon=False, fontsize=7.5, title_fontsize=7.5,
              alignment="left", loc="upper right", bbox_to_anchor=(1.0, 0.74))
    fig.tight_layout()
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    p = out / "line_sensors_fig.png"
    fig.savefig(p, dpi=150)
    print(p)


if __name__ == "__main__":
    main()
