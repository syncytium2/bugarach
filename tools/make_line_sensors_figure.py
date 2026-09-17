#!/usr/bin/env python3
"""Draw the supervised bake-off, its fold-by-fold comparisons, and the plant probe.

    python tools/make_line_sensors_figure.py --summary <run>/summary.json
        [--out <folder>] [--also <folder>]

Reads ``summary.json`` (``tools/summarize_tube_self_supervised.py``), which carries the bake-off
averaged over training seeds, the paired comparisons with their intervals, and the plant probe with
its standard errors. Writes ``line_sensors_fig.png``. Exploratory.

Stacked so each panel reads at page width:

* **A** — every detector's held-out F1, one dot per fold (averaged over training seeds), a bar for
  the mean. Grouped by family, not ordered by score.
* **B** — the comparisons the report makes, fold by fold, with the 95 % interval corrected for
  overlapping training folds (Nadeau & Bengio 2003). The fold that carries a margin is marked.
* **C, D, E** — the plant probe: the line plant's response divided by a burst's, fuzz's and a
  wave's, by plant size, one line per supervised model, with an approximate standard error.
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
from figure_destination import add_arguments, save  # noqa: E402

plt.rcParams.update({"font.size": 10.5, "axes.labelsize": 10.5, "xtick.labelsize": 10,
                     "ytick.labelsize": 10, "legend.fontsize": 9.5})

ORDER = ["line", "line_length", "line_bound", "tube", "tube_guard", "tube_ratio",
         "tube_ratio_guard", "tiny", "trace", "coact", "loco", "rate", "sce", "cicada", "sync"]
"""Grouped by family, NOT sorted by score: a chart ordered by F1 says "ranking" before its label is
read, and at four folds these are not an ordering (MILESTONES: a table of performance, not a
ranking). The same order is used by the report's table."""
INK = {"line": ("#2a78d6", "o"), "line_length": ("#eb6834", "s"), "line_bound": ("#1baf7a", "D"),
       "tube": ("#6b6b6b", "o")}
"""The three `line` builds take the first three categorical slots of the dataviz reference palette
(colour-vision separation passes on every pair); `tube` is grey everywhere in the report. Shape
repeats identity, because the aqua sits below 3:1 against white."""
GREY = ("#8a8a8a", "o")
LABEL = {"line": "line (two sensors)", "line_length": "line_length (length only)",
         "line_bound": "line_bound (vote bounded in time)", "tube": "tube",
         "tube_guard": "tube_guard", "coact": "CoactDetect", "loco": "LoCo",
         "rate": "rate+context", "cicada": "locust", "sce": "binned SCE", "sync": "SPIKE-synch",
         "tiny": "tiny (threshold on its grid floor)", "trace": "trace", "tube_ratio": "tube_ratio",
         "tube_ratio_guard": "tube_ratio_guard"}
PAIRS = ["line - coact", "line_length - coact", "line_bound - coact", "tube - coact",
         "line - line_length", "line_bound - line", "line - tube", "coact - loco"]
PAIR_LABEL = {"line - coact": "line − CoactDetect",
              "line_length - coact": "line_length − CoactDetect",
              "line_bound - coact": "line_bound − CoactDetect",
              "tube - coact": "tube − CoactDetect",
              "line - line_length": "line − line_length (second sensor)",
              "line_bound - line": "line_bound − line (bounded vote)",
              "line - tube": "line − tube", "coact - loco": "CoactDetect − LoCo"}
FOLD_MARKERS = ["o", "s", "D", "^"]
PLANTS = [("burst", "÷ burst"), ("fuzz", "÷ fuzz"), ("wave", "÷ wave")]
YLIM_PROBE = (0.8, 12.0)
PROBE_TICKS = [1, 1.5, 2, 3, 5, 10]
"""Log scale, because the quantity is a ratio and the burst ratios reach 10: every value sits on the
axis, so nothing needs an off-scale note."""
YLIM_F1 = (-0.03, 0.9)


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--summary", required=True)
    add_arguments(ap)
    ap.add_argument("--probe", default=None, help="ignored; the probe is read from the summary")
    a = ap.parse_args(argv)
    s = json.loads(Path(a.summary).read_text())
    bake, probe = s["bakeoff"], s["probe"]
    rows = bake["detectors"]
    n_seeds = len(bake["seeds"])

    fig = plt.figure(figsize=(10.5, 15.5))
    gs = fig.add_gridspec(3, 3, height_ratios=[1.35, 1.0, 0.75], hspace=0.42, wspace=0.28)
    ax = fig.add_subplot(gs[0, :])
    names = [n for n in ORDER if n in rows]
    y = np.arange(len(names))[::-1]
    rs = np.random.RandomState(0)
    for i, n in zip(y, names):
        c, mk = INK.get(n, GREY)
        per = rows[n]["f1_fold_means"]
        ax.plot(per, i + rs.uniform(-0.18, 0.18, len(per)), mk, color=c, ms=5.5, alpha=0.85,
                mew=0.5, mec="white")
        ax.plot([rows[n]["f1_mean"]] * 2, [i - 0.32, i + 0.32], color=c, lw=2.6)
    ax.set_yticks(y, [LABEL.get(n, n) for n in names])
    ax.set_xlim(*YLIM_F1)
    ax.set_xlabel(f"held-out F1 (dot: one fold, mean of {n_seeds} training seeds; "
                  "bar: mean of folds)")
    ax.text(-0.3, 1.02, "A", transform=ax.transAxes, fontsize=13, fontweight="bold", va="bottom")

    bx = fig.add_subplot(gs[1, :])
    pairs = [p for p in PAIRS if p in bake["paired"]]
    yb = np.arange(len(pairs))[::-1]
    for i, key in zip(yb, pairs):
        p = bake["paired"][key]
        lo, hi = p["ci95_nadeau_bengio"]
        bx.hlines(i, lo, hi, color="0.55", lw=2.2)
        for f, d in enumerate(p["differences"]):
            carries = f == p["largest_fold"]
            bx.plot([d], [i + (f - 1.5) * 0.12], FOLD_MARKERS[f], ms=6.5,
                    color="#111111" if carries else "white", mec="#111111", mew=1.2)
        bx.plot([p["mean"]] * 2, [i - 0.33, i + 0.33], color="#111111", lw=2.4)
    bx.axvline(0, color="0.55", ls=":", lw=1)
    bx.set_yticks(yb, [PAIR_LABEL[k] for k in pairs])
    bx.set_xlabel("paired difference in held-out F1 (bar: mean; grey: corrected 95 % interval)")
    bx.text(-0.3, 1.02, "B", transform=bx.transAxes, fontsize=13, fontweight="bold", va="bottom")
    bx.legend(handles=[Line2D([], [], color="#111111", marker=m, ls="", ms=7, mfc="white",
                              label=f"fold {f + 1}") for f, m in enumerate(FOLD_MARKERS)]
              + [Line2D([], [], color="#111111", marker="o", ls="", ms=7,
                        label="filled: the fold with the largest difference")],
              loc="upper center", bbox_to_anchor=(0.5, -0.13), ncol=5, frameon=False)

    models = [m for m in ("line", "line_length", "line_bound", "tube")
              if f"supervised {m}" in probe]
    for col, (plant, title) in enumerate(PLANTS):
        cx = fig.add_subplot(gs[2, col])
        for m in models:
            colour, mk = INK[m]
            cells = probe[f"supervised {m}"][plant]
            Ks = sorted(cells, key=int)
            xs = [int(K) for K in Ks]
            vals = [cells[K]["ratio"] for K in Ks]
            ses = [cells[K]["ratio_se_approx"] for K in Ks]
            cx.plot(xs, vals, "-", color=colour, lw=1.4)
            for xk, v, se, K in zip(xs, vals, ses, Ks):
                shaky = cells[K]["denominator_within_1sd_of_zero"]
                if not shaky:
                    cx.vlines(xk, v - se, v + se, color=colour, lw=1.2)
                cx.plot([xk], [v], mk, ms=6, color="white" if shaky else colour, mec=colour,
                        mew=1.3, zorder=3)
        cx.axhline(1.0, color="0.55", ls=":", lw=1)
        cx.set_xscale("log", base=2)
        cx.set_xticks([4, 8, 16], ["4", "8", "16"])
        cx.set_yscale("log")
        cx.set_ylim(*YLIM_PROBE)
        cx.set_yticks(PROBE_TICKS, [f"{t:g}" for t in PROBE_TICKS])
        cx.minorticks_off()
        cx.set_title(title, fontsize=10.5)
        cx.set_xlabel("plant size (ROIs)")
        if col == 0:
            cx.set_ylabel("line plant's response ÷ other plant's\n(log scale)")
            cx.text(-0.42, 1.12, "C", transform=cx.transAxes, fontsize=13, fontweight="bold",
                    va="bottom")
    fig.legend(handles=[Line2D([], [], color=INK[m][0], marker=INK[m][1], lw=1.4, label=LABEL[m])
                        for m in models]
               + [Line2D([], [], color="0.3", marker="o", ls="", mfc="white",
                         label="open: divisor within one standard deviation of zero")],
               loc="lower center", ncol=3, frameon=False, bbox_to_anchor=(0.5, 0.0))
    fig.subplots_adjust(left=0.27, right=0.97, top=0.98, bottom=0.08)
    save(fig, "line_sensors_fig.png", a, subfolder="tube_self_supervised")


if __name__ == "__main__":
    main()
