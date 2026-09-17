#!/usr/bin/env python3
"""Draw the supervised bake-off, its fold-by-fold comparisons, and the plant probe.

    python tools/make_line_sensors_figure.py --summary <run>/summary.json
        [--out <folder>] [--also <folder>]

Reads ``summary.json`` (``tools/summarize_tube_self_supervised.py``), which carries the bake-off
averaged over training seeds, the paired comparisons with their intervals, and the plant probe with
its standard errors. Writes ``line_sensors_fig.png``. Exploratory.

Stacked so each panel reads at page width:

* **A** — every detector's held-out F1, one mark per fold (averaged over training seeds), a bar for
  the mean. Grouped by family, not ordered by score.
* **B** — the comparisons the report makes: a black bar for the mean over folds on the 95 % interval
  corrected for overlapping training folds (Nadeau & Bengio 2003), and each fold as a small gray
  cross; the fold with the largest difference is a darker cross.
* **C** — the plant probe: the synchronous plant's response divided by a burst's, fuzz's and a
  wave's, by plant size, one line per supervised model, with an approximate standard error.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.patheffects as pe  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from matplotlib.legend_handler import HandlerTuple  # noqa: E402
from matplotlib.lines import Line2D  # noqa: E402
from figure_destination import add_arguments, save  # noqa: E402

plt.rcParams.update({"font.size": 10.5, "axes.labelsize": 10.5, "xtick.labelsize": 10,
                     "ytick.labelsize": 9.5, "legend.fontsize": 9.5})
"""9.5 pt is the floor everywhere in this figure; the row labels sit on it so a two-line label fits
inside one row of panel A."""

ORDER = ["line", "line_length", "line_bound", "tube", "tube_guard", "tube_ratio",
         "tube_ratio_guard", "tiny", "trace", "coact", "loco", "rate", "sce", "cicada", "sync"]
"""Grouped by family, NOT sorted by score: a chart ordered by F1 says "ranking" before its label is
read, and at four folds these are not an ordering (MILESTONES: a table of performance, not a
ranking). The same order is used by the report's table."""
INK = {"line": ("#2a78d6", "o"), "line_length": ("#eb6834", "s"), "line_bound": ("#1baf7a", "D"),
       "tube": ("#6b6b6b", "o"), "tube_guard": ("#a8a8a8", "s")}
"""One ink and one shape per model across every figure in the report. The three `line` builds take
the first three categorical slots of the dataviz reference palette (color-vision separation passes
on every pair); `tube` is dark gray and `tube_guard` light gray everywhere. Shape repeats identity,
because the aqua sits below 3:1 against white."""
OTHER, OTHER_BAR = ("#8a8a8a", "x"), "#4a4a4a"
"""Detectors with no report-wide identity: a gray cross with a white halo, so no circle, square or
diamond is spent on them, and a darker bar for the mean, so crosses sitting on it (all four of
`tiny`'s folds score the same) stay visible."""
LABEL = {"line": "line (relative length and concentration channels)",
         "line_length": "line_length (relative length only)",
         "line_bound": "line_bound (vote bounded in time, resting level subtracted)",
         "tube": "tube", "tube_guard": "tube_guard", "coact": "CoactDetect", "loco": "LoCo",
         "rate": "rate+context", "cicada": "locust", "sce": "binned SCE", "sync": "SPIKE-synch",
         "tiny": "tiny (threshold on its grid floor)", "trace": "trace", "tube_ratio": "tube_ratio",
         "tube_ratio_guard": "tube_ratio_guard"}
"""The report calls `line`'s second sensor the **concentration channels** everywhere; "two sensors"
was a retired name for the same object, and several names for one object cost a reader a lookup."""
SHORT = {"line": "line", "line_length": "line_length", "line_bound": "line_bound", "tube": "tube"}
"""Panel C's legend names the models only: panel A's rows already say what each one computes, and a
one-line legend keeps the panel from growing a block of prose under it."""
PAIRS = ["line - coact", "line_length - coact", "line_bound - coact", "tube - coact",
         "line - line_length", "line_bound - line", "line - tube", "coact - loco"]
PAIR_LABEL = {"line - coact": "line − CoactDetect",
              "line_length - coact": "line_length − CoactDetect",
              "line_bound - coact": "line_bound − CoactDetect",
              "tube - coact": "tube − CoactDetect",
              "line - line_length": "line − line_length (concentration channels)",
              "line_bound - line": "line_bound − line (two changes: time bound and resting level)",
              "line - tube": "line − tube", "coact - loco": "CoactDetect − LoCo"}
"""Worded as the report's comparison table words them."""
FOLD_INK, FOLD_FLAG_INK, FOLD_MARK = "#9a9a9a", "#333333", "x"
"""Folds in panel B are small, recessive crosses — never a circle, square or diamond, which mean
models — so the black bar for the mean is the mark a reader lands on. A filled mark on one fold
read as a forest plot's pooled estimate."""
FOLD_STEP = 0.26
"""Vertical offset between folds in a row of panel B: fold 1 on top, fold 4 at the bottom, so two
folds with the same difference cannot hide each other."""
PLANTS = ["burst", "fuzz", "wave"]
YLIM_PROBE = (0.8, 12.0)
PROBE_TICKS = [1, 1.5, 2, 3, 5, 10]
"""Log scale, because the quantity is a ratio and the burst ratios reach 10: every value sits on the
axis, so nothing needs an off-scale note."""
YLIM_F1 = (-0.03, 0.9)
PROBE_LEFT, PROBE_GAP = 0.13, 0.055
"""Panel C is laid out across the page instead of in the label gutter panels A and B need."""
LETTER_X = 0.025
"""Panel letters sit at this figure fraction from the left, outside the row-label gutter."""


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

    fig = plt.figure(figsize=(10.5, 11.6))
    gs = fig.add_gridspec(5, 3, height_ratios=[3.4, 0.75, 2.2, 1.0, 1.3], hspace=0.2,
                          wspace=0.26)
    # Rows 2 and 4 hold nothing but a legend, so a legend can never land on a panel and the gaps
    # between panels stay the height of one x-axis label. Every row label is one line, which is
    # what lets a row be 34 px instead of 46 px; the label gutter pays for it in width instead.
    fig.subplots_adjust(left=0.45, right=0.985, top=0.975, bottom=0.168)
    row_top = {r: gs[r, :].get_position(fig).y1 - 0.012 for r in range(5)}
    # The 0.012 keeps a legend clear of the x-axis label of the panel above it.
    probe_bottom = gs[4, :].get_position(fig).y0
    # A legend is centred on the page, not on its panel: the panels start at 45 % of the width to
    # leave room for the row labels, and a legend centred there would run off the right edge.

    # A: held-out F1 per detector
    ax = fig.add_subplot(gs[0, :])
    names = [n for n in ORDER if n in rows]
    n_folds = len(rows[names[0]]["f1_fold_means"])
    y = np.arange(len(names))[::-1]
    for i, n in zip(y, names):
        c, mk = INK.get(n, OTHER)
        cross = mk == "x"
        per = rows[n]["f1_fold_means"]
        halo = [pe.Stroke(linewidth=2.4, foreground="white"), pe.Normal()] if cross else None
        ax.plot(per, i + (1.5 - np.arange(len(per))) * 0.28, mk, color=c, ms=4.0,
                mew=1.1 if cross else 0.4, mec=c if cross else "white", ls="", zorder=3,
                path_effects=halo)
        ax.plot([rows[n]["f1_mean"]] * 2, [i - 0.44, i + 0.44], color=OTHER_BAR if cross else c,
                lw=2.2, zorder=2)
    ax.set_yticks(y, [LABEL.get(n, n) for n in names])
    ax.set_xlim(*YLIM_F1)
    ax.set_xlabel("held-out F1 (harmonic mean of recall and precision)")
    model_folds = tuple(Line2D([], [], color=INK[m][0], marker=INK[m][1], ls="", ms=5.5, mew=0.4,
                               mec="white") for m in ("line", "line_length", "line_bound"))
    fig.legend(handles=[
        model_folds,
        Line2D([], [], color=OTHER[0], marker="x", ls="", ms=5.5, mew=1.1),
        Line2D([], [], color="#444444", marker="|", ls="", ms=11, mew=2.2)],
        labels=[f"one fold of a model, mean of {n_seeds} training\nseeds (folds 1 to {n_folds}, "
                "top to bottom, in every row)",
                "one fold, other detectors",
                f"mean of {n_folds} folds (not an interval)"],
        handler_map={tuple: HandlerTuple(ndivide=None, pad=0.3)}, handlelength=3.4,
        columnspacing=2.0, handletextpad=0.7, loc="upper center", ncol=2, frameon=False,
        bbox_to_anchor=(0.5, row_top[1]))

    # B: paired fold differences
    bx = fig.add_subplot(gs[2, :])
    pairs = [p for p in PAIRS if p in bake["paired"]]
    yb = np.arange(len(pairs))[::-1]
    for i, key in zip(yb, pairs):
        p = bake["paired"][key]
        lo, hi = p["ci95_nadeau_bengio"]
        bx.hlines(i, lo, hi, color="#c4c4c4", lw=3.0, zorder=1)
        for f, d in enumerate(p["differences"]):
            flag = f == p["largest_fold"]
            bx.plot([d], [i + (1.5 - f) * FOLD_STEP], FOLD_MARK, ms=4.6, mew=1.3,
                    color=FOLD_FLAG_INK if flag else FOLD_INK, zorder=4,
                    path_effects=[pe.Stroke(linewidth=3.4, foreground="white"), pe.Normal()])
        bx.plot([p["mean"]] * 2, [i - 0.4, i + 0.4], color="#000000", lw=3.4, zorder=3,
                solid_capstyle="butt")
    bx.axvline(0, color="0.45", ls=":", lw=1.2, zorder=1.5)
    bx.set_ylim(yb.min() - 0.6, yb.max() + 0.6)
    bx.set_yticks(yb, [PAIR_LABEL[k] for k in pairs])
    bx.set_xlabel("paired difference in held-out F1 (first minus second, same fold)")
    fig.legend(handles=[
        Line2D([], [], color="#000000", marker="|", ls="", ms=14, mew=3.4,
               label=f"mean of {n_folds} folds"),
        Line2D([], [], color=FOLD_INK, marker=FOLD_MARK, ls="", ms=6, mew=1.4,
               label=f"one fold, mean of {n_seeds} training seeds\n"
                     f"(folds 1 to {n_folds}, top to bottom)"),
        Line2D([], [], color=FOLD_FLAG_INK, marker=FOLD_MARK, ls="", ms=6, mew=1.4,
               label="dark cross: the fold with the largest difference"),
        Line2D([], [], color="0.45", ls=":", lw=1.2, label="dotted: no difference (0 F1)"),
        Line2D([], [], color="#c4c4c4", lw=3.0,
               label="95 % interval, Nadeau–Bengio corrected; it assumes\ndistinct training sets "
                     "per fold, but 2 of the 4 folds\nshare one fitted model per seed")],
        loc="upper center", ncol=2, frameon=False, columnspacing=2.0,
        bbox_to_anchor=(0.5, row_top[3]))

    # C: the plant probe
    models = [m for m in ("line", "line_length", "line_bound", "tube")
              if f"supervised {m}" in probe]
    probe_w = (0.985 - PROBE_LEFT - 2 * PROBE_GAP) / 3
    for col, plant in enumerate(PLANTS):
        cx = fig.add_axes([PROBE_LEFT + col * (probe_w + PROBE_GAP), probe_bottom, probe_w,
                           row_top[4] - probe_bottom])
        # Placed by hand rather than in the gridspec: panels A and B spend 45 % of the width on row
        # labels, and the probe needs no gutter that wide, so it takes the page instead.
        for m in models:
            color, mk = INK[m]
            cells = probe[f"supervised {m}"][plant]
            Ks = sorted(cells, key=int)
            xs = [int(K) for K in Ks]
            vals = [cells[K]["ratio"] for K in Ks]
            ses = [cells[K]["ratio_se_approx"] for K in Ks]
            cx.plot(xs, vals, "-", color=color, lw=1.4)
            for xk, v, se, K in zip(xs, vals, ses, Ks):
                shaky = cells[K]["denominator_within_1sd_of_zero"]
                if not shaky:
                    cx.vlines(xk, v - se, v + se, color=color, lw=1.2)
                cx.plot([xk], [v], mk, ms=6, color="white" if shaky else color, mec=color,
                        mew=1.3, zorder=3)
        cx.axhline(1.0, color="0.45", ls=":", lw=1.2)
        cx.set_xscale("log", base=2)
        cx.set_xticks([4, 8, 16], ["4", "8", "16"])
        cx.set_yscale("log")
        cx.set_ylim(*YLIM_PROBE)
        cx.set_yticks(PROBE_TICKS, [f"{t:g}" for t in PROBE_TICKS])
        cx.minorticks_off()
        cx.set_xlabel(f"plant size (ROIs)\ndivided by a {plant}")
        if col == 0:
            cx.set_ylabel("synchronous plant's response\n÷ other plant's (log ratio)")
    model_handles = [Line2D([], [], color=INK[m][0], marker=INK[m][1], lw=1.4, label=SHORT[m])
                     for m in models]
    open_handle = tuple(Line2D([], [], color=INK[m][0], marker=INK[m][1], ls="", ms=6,
                               mfc="white", mew=1.3) for m in models[:3])
    se_handle = Line2D([], [], color="#444444", marker="|", ls="", ms=14, mew=1.2)
    one_handle = Line2D([], [], color="0.45", ls=":", lw=1.2)
    fig.legend(handles=model_handles + [open_handle, se_handle, one_handle],
               labels=[h.get_label() for h in model_handles]
               + ["open mark: divisor within one\nstandard deviation of zero (no error bar)",
                  "vertical bar: ± approximate\nstandard error",
                  "dotted: ratio 1, the two\nplants answered alike"],
               handler_map={tuple: HandlerTuple(ndivide=None, pad=0.6)}, columnspacing=1.4,
               loc="upper center", ncol=4, frameon=False, labelspacing=0.4,
               bbox_to_anchor=(0.5, probe_bottom - 0.055))
    fig.text(0.5, 0.006, "ROI: region of interest, one imaged cell.   SCE: synchronous calcium "
             "events.\nPanels A and B score 4 held-out folds of 30 planted events each; F1 runs "
             "from 0 to 1 and has no further unit.", linespacing=1.4,
             ha="center", va="bottom", fontsize=9.5, color="#333333")
    for row, letter in ((0, "A"), (2, "B"), (4, "C")):
        fig.text(LETTER_X, gs[row, :].get_position(fig).y1, letter, fontsize=13,
                 fontweight="bold", va="top", ha="left")
    # The letters are placed in figure coordinates because the row labels need a wide gutter and an
    # axes-relative offset would put each letter at a different distance from the page edge.
    save(fig, "line_sensors_fig.png", a, subfolder="tube_self_supervised")


if __name__ == "__main__":
    main()
