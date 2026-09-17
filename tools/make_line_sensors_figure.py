#!/usr/bin/env python3
"""Draw what the second sensor and the time-bounded vote buy: the bake-off, and the plant probe.

    python tools/make_line_sensors_figure.py --summary <run>/summary.json --probe <folder> --out <folder>

Reads the bake-off from ``summary.json`` (``tools/summarize_tube_self_supervised.py``, which
averages every training seed's ``bakeoff.json``) and ``line_vs_fuzz.json`` from
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

ORDER = ["line", "line_length", "line_bound", "tube", "tube_guard", "tube_ratio",
         "tube_ratio_guard", "tiny", "trace", "coact", "loco", "rate", "cicada", "sce", "sync"]
"""Grouped by family, NOT sorted by score. `tools/make_bakeoff_summary_figure.py` carries the
reason as a murderboard finding of 2026-09-07: a chart ordered by F1 says "ranking" before its
label is read, and at four folds these are intervals rather than an ordering."""
INK = {"line": ("#2a78d6", "o"), "line_length": ("#eb6834", "s"), "line_bound": ("#1baf7a", "D")}
"""The three `line` builds take the first three categorical slots of the dataviz reference
palette, which pass the colour-vision check on every pair (worst ΔE 9.2, deuteranopia). The
previous blue and purple did not (ΔE 5.4). Everything else stays grey on purpose: context, not
identity. Shape repeats the identity, because the aqua sits below 3:1 against white."""
GREY = ("#6b6b6b", "o")
LABEL = {"line": "line (two sensors)", "line_length": "line_length (length only)",
         "line_bound": "line_bound (vote bounded in time)",
         "tube": "tube", "tube_guard": "tube_guard", "coact": "CoactDetect", "loco": "LoCo",
         "rate": "rate+context", "cicada": "locust", "sce": "binned SCE", "sync": "SPIKE-synch",
         "tiny": "tiny", "trace": "trace", "tube_ratio": "tube_ratio",
         "tube_ratio_guard": "tube_ratio_guard"}
COMPARISONS = [("burst", "-", "÷ burst (same ink, a quarter of the ROIs)"),
               ("fuzz", "-.", "÷ fuzz (same ROIs, spread over 2.9 s)"),
               ("wave", "--", "÷ wave (same ROIs, one frame apart)")]
"""All three comparisons the probe computes. `fuzz` was once measured and drawn nowhere, because
the constant listing it was never read in `main()`; three blind reviewers found it."""

YLIM_F1 = (-0.03, 0.9)
"""Shared with Figure 2's panels A and B so a score carries between the two figures."""


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--summary", required=True)
    ap.add_argument("--probe", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args(argv)
    bake = json.loads(Path(a.summary).read_text())["bakeoff"]
    probe = json.loads((Path(a.probe) / "line_vs_fuzz.json").read_text())["scores"]
    rows = bake["detectors"]
    n_seeds = len(bake["seeds"])

    fig, (ax, bx) = plt.subplots(1, 2, figsize=(14.0, 5.8),
                                 gridspec_kw={"width_ratios": [1.6, 1]})
    names = [n for n in ORDER if n in rows]
    y = np.arange(len(names))[::-1]
    rs = np.random.RandomState(0)
    # Each FOLD is one point — its F1 averaged over the training seeds — with a bar for the mean of
    # the four. A dot with a range bar on a stacked categorical axis reads as a forest plot, where
    # the bar is a confidence interval and non-overlap is significance; this page's claim is that
    # the ordering is NOT separable, so the folds are drawn as the measurements they are.
    for i, n in zip(y, names):
        c, mk = INK.get(n, GREY)
        per = rows[n]["f1_fold_means"]
        ax.plot(per, i + rs.uniform(-0.16, 0.16, len(per)), mk, color=c, ms=4.4,
                alpha=0.8, mew=0.5, mec="white")
        ax.plot([rows[n]["f1_mean"]] * 2, [i - 0.3, i + 0.3], color=c, lw=2.4)
    ax.set_yticks(y, [LABEL.get(n, n) for n in names], fontsize=8.5)
    ax.set_xlim(*YLIM_F1)
    ax.set_xlabel(f"planted-truth F1 on the held-out fold, four folds × {n_seeds} training seeds\n"
                  f"(dot: one fold, averaged over the {n_seeds} seeds; bar: mean over the four "
                  "folds — NOT a confidence interval)", fontsize=9)
    ax.text(-0.25, 1.06, "A", transform=ax.transAxes, fontsize=12, fontweight="bold", va="top")

    models = [(f"supervised {m}", m) for m in ("line", "line_length", "line_bound", "tube")]
    models = [(k, m) for k, m in models if k in probe]
    Ks = sorted({int(k.split("_")[1]) for k in probe["supervised line"] if k.startswith("line_")
                 and not k.endswith(("sd",))})
    # An OPEN marker where the divisor is within one standard deviation of zero over the fields.
    # A ratio whose divisor is consistent with no response is not a measurement of discrimination.
    # The axis stops at YMAX. A ratio above it is drawn ON the edge with its value beside it,
    # because one open point at 9.8 flattened every other line in the panel against 1.
    YMAX = 5.6
    for key, m in models:
        r = probe[key]
        colour, mk = INK.get(m, GREY)
        for plant, style, _ in COMPARISONS:
            vals = [r[f"line_{K}"] / r[f"{plant}_{K}"] for K in Ks]
            bx.plot(Ks, [min(v, YMAX) for v in vals], style, color=colour, lw=1.4, zorder=2)
            for K, v in zip(Ks, vals):
                shaky = abs(r[f"{plant}_{K}"]) < r.get(f"{plant}_{K}_sd", 0.0)
                bx.plot([K], [min(v, YMAX)], mk, ms=5.0, zorder=3,
                        color="white" if shaky else colour, mec=colour, mew=1.3, clip_on=False)
                if v > YMAX:
                    bx.annotate(f"{v:.1f} (off scale)", (K, YMAX), xytext=(9, -14),
                                textcoords="offset points", fontsize=7.5, color="0.25")
    bx.set_ylim(0.8, YMAX)
    bx.axhline(1.0, color="0.55", ls=":", lw=0.9)
    bx.set_xscale("log", base=2)
    bx.set_xticks(Ks, [str(K) for K in Ks])
    bx.set_xlabel("plant size: ROIs' worth of onsets (log₂ spacing)", fontsize=9)
    bx.set_ylabel("the line plant's response ÷ the other plant's\n"
                  "(above 1: the line plant answers more)", fontsize=9)
    bx.text(-0.20, 1.06, "B", transform=bx.transAxes, fontsize=12, fontweight="bold", va="top")
    lg = bx.legend(handles=[Line2D([], [], color=INK.get(m, GREY)[0], marker=INK.get(m, GREY)[1],
                                   lw=1.6, label=LABEL[m]) for _, m in models],
                   title="supervised model", frameon=False, fontsize=7.5, title_fontsize=7.5,
                   alignment="left", loc="upper right", bbox_to_anchor=(1.0, 1.0))
    bx.add_artist(lg)
    bx.legend(handles=[Line2D([], [], color="0.3", ls=s, label=lab) for _, s, lab in COMPARISONS]
              + [Line2D([], [], color="white", marker="o", ls="", ms=5, mec="0.3", mew=1.3,
                        label="open: divisor within 1 SD of zero")],
              title="compared against", frameon=False, fontsize=7.5, title_fontsize=7.5,
              alignment="left", loc="upper right", bbox_to_anchor=(1.0, 0.70))
    fig.tight_layout()
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    p = out / "line_sensors_fig.png"
    fig.savefig(p, dpi=150)
    print(p)


if __name__ == "__main__":
    main()
