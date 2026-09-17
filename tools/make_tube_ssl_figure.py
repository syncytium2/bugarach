#!/usr/bin/env python3
"""Draw what training against rigid shift bought: scores by arm, what a truth-reading score is made
of, and the paired checks beside the controls that can fail them.

    python tools/make_tube_ssl_figure.py --summary <run>/summary.json
        [--out <folder>] [--also <folder>]

Reads the ``training`` block of ``summary.json`` (``tools/summarize_tube_self_supervised.py``);
writes ``tube_ssl_fig.png``. Every mark is a cell mean: one arm, one displacement, one model,
averaged over its fits (a fit with no true positive scores 0). Exploratory.

Stacked so each panel reads at page width:

* **A** — planted-truth F1 at the label-free threshold, one subpanel per event-rate budget, by
  training arm, with the zero-parameter count baselines in the last columns.
* **B** — planted-truth F1 at the truth-reading threshold against the share of the held-out
  recording the detections cover there. A score earned by covering nearly everything is not
  detection.
* **C** — the paired checks, grouped by what each one can show: the nulls that must read chance,
  the positive control that must move, what the objective paid for, and the two checks that
  separate coordination from slow shared modulation.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.lines import Line2D  # noqa: E402
from figure_destination import add_arguments, save  # noqa: E402
from matplotlib.transforms import blended_transform_factory  # noqa: E402

plt.rcParams.update({"font.size": 10.5, "axes.labelsize": 10.5, "xtick.labelsize": 9.5,
                     "ytick.labelsize": 10, "legend.fontsize": 9.5})

MODELS = {"line": ("#2a78d6", "o"), "line_length": ("#eb6834", "s"),
          "line_bound": ("#1baf7a", "D"), "tube": ("#6b6b6b", "o"), "tube_guard": ("#a8a8a8", "s")}
"""The same inks as every other figure of the report: the three `line` builds on the first three
categorical slots of the dataviz reference palette, the tube family grey. Shape separates the two
greys, whose contrast ratio is only 1.36."""
BASELINES = {"count_share": "^", "count_excess": "P", "slow_modulation": "X"}
"""Zero-parameter scorers, in black: no model ink, so they never read as a trained build."""
BASELINE_LABEL = {"count_share": "count share", "count_excess": "count excess",
                  "slow_modulation": "slow modulation"}
ARMS = [("supervised", None, "supervised"), ("untrained", None, "untrained"),
        ("ssl_sim", 10.0, "sim, 10 s"), ("ssl_sim", 20.0, "sim, 20 s"),
        ("ssl_real", 10.0, "real, 10 s"), ("ssl_real", 20.0, "real, 20 s"),
        ("baseline", 10.0, "count, 10 s"), ("baseline", 20.0, "count, 20 s")]
BUDGETS = [("label_free_0.5", "≤ 0.5 events per 10 min"), ("label_free_1", "≤ 1 event per 10 min"),
           ("label_free_2", "≤ 2 events per 10 min")]
CHECK_GROUPS = [
    ("must read chance", [("real_vs_shared_offset", "shared\noffset,\nsame crop"),
                          ("real_vs_shared_offset_independent_crop", "shared\noffset,\nother crop"),
                          ("unplanted_twin_vs_rigid_shift", "stationary\ntwin"),
                          ("independent_modulation_twin_vs_rigid_shift",
                           "independent\nmodulation\ntwin")]),
    ("must move", [("real_vs_thinned", "a fifth of\nonsets\nremoved")]),
    ("trained for", [("real_vs_rigid_shift", "rigid shift\nat training J")]),
    ("coordination, or\nslow modulation?",
     [("real_vs_rigid_shift_small_J", "rigid shift\nat small J"),
      ("shared_modulation_twin_vs_rigid_shift", "shared\nmodulation\ntwin")])]
YLIM_F1 = (-0.03, 0.9)


def dodge(n, i, width):
    return (i - (n - 1) / 2) * width / max(1, n - 1) if n > 1 else 0.0


def counted(ns, unit):
    """'12 fits', '1 fit', or '11 or 12 fits' when cells differ."""
    return " or ".join(map(str, ns)) + " " + unit + ("" if ns == [1] else "s")


def cell(cells, arm, J, model):
    return cells.get(f"{arm}|{J}|{model}")


def mark(ax, x, y, model, arm, ms=6.0):
    """Model ink and shape; open for the untrained arm and the simulated arm, so supervised and
    trained-on-real read as the filled marks. Count baselines in black."""
    if model in BASELINES:
        ax.plot([x], [y], BASELINES[model], ms=ms + 1, color="#111111", mew=0.8, zorder=3)
        return
    c, mk = MODELS[model]
    hollow = arm in ("untrained", "ssl_sim")
    ax.plot([x], [y], mk, ms=ms, color="white" if hollow else c, mec=c, mew=1.3, zorder=3)


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--summary", required=True)
    add_arguments(ap)
    a = ap.parse_args(argv)
    s = json.loads(Path(a.summary).read_text())
    cells = s["training"]["cells"]
    j_small = s["constants"]["training"]["j_small_sec"]
    n_fits = sorted({c["n_fits"] for c in cells.values() if c["arm"] != "baseline"})
    n_base = sorted({c["n_fits"] for c in cells.values() if c["arm"] == "baseline"})

    fig = plt.figure(figsize=(10.5, 16.0))
    gs = fig.add_gridspec(3, 3, height_ratios=[0.9, 0.95, 1.05], hspace=0.6, wspace=0.1)

    for col, (key, title) in enumerate(BUDGETS):
        ax = fig.add_subplot(gs[0, col])
        for i, (arm, J, _) in enumerate(ARMS):
            names = list(BASELINES) if arm == "baseline" else list(MODELS)
            for k, m in enumerate(names):
                c = cell(cells, arm, J, m)
                if c and key in c["scores"]:
                    mark(ax, i + dodge(len(names), k, 0.62), c["scores"][key]["f1_mean"], m, arm,
                         ms=5.0)
        ax.axvline(5.5, color="0.75", lw=0.8)
        ax.set_xticks(range(len(ARMS)), [lab for _, _, lab in ARMS], fontsize=9, rotation=90)
        ax.set_xlim(-0.6, len(ARMS) - 0.4)
        ax.set_ylim(*YLIM_F1)
        ax.set_title(title, fontsize=10)
        if col == 0:
            ax.set_ylabel("planted-truth F1, held-out fold\nlabel-free threshold")
            ax.text(-0.36, 1.08, "A", transform=ax.transAxes, fontsize=13, fontweight="bold",
                    va="bottom")
        else:
            ax.tick_params(labelleft=False)
        if col == 1:
            ax.set_xlabel("training arm: sim and real are trained against rigid shift at J = 10 s "
                          "or 20 s,\non simulated or real lab recordings, with no labels; count: "
                          "a zero-parameter baseline")

    bx = fig.add_subplot(gs[1, :2])
    for c in cells.values():
        o = c["scores"].get("oracle", {})
        cov = o.get("coverage_share_median")
        if cov is None:
            continue
        mark(bx, cov, o["f1_mean"], c["model"], c["arm"], ms=6.5)
    bx.set_xlim(-0.03, 1.03)
    bx.set_ylim(*YLIM_F1)
    bx.set_xlabel("share of the held-out recording the detections cover\n"
                  "(median over recordings and fits)")
    bx.set_ylabel("planted-truth F1, held-out fold\ntruth-reading threshold")
    bx.text(-0.2, 1.02, "B", transform=bx.transAxes, fontsize=13, fontweight="bold", va="bottom")
    lx = fig.add_subplot(gs[1, 2])
    lx.axis("off")
    lx.legend(handles=[Line2D([], [], color=c, marker=mk, ls="", ms=7, mec=c, mew=1.3, label=m)
                       for m, (c, mk) in MODELS.items()]
              + [Line2D([], [], color="#111111", marker=mk, ls="", ms=8, mew=0.8,
                        label=f"{BASELINE_LABEL[b]}\n(no parameters)")
                 for b, mk in BASELINES.items()]
              + [Line2D([], [], color="0.3", marker="o", ls="", ms=7,
                        label="filled: supervised, or\ntrained on real recordings"),
                 Line2D([], [], color="0.3", marker="o", ls="", ms=7, mfc="white", mew=1.3,
                        label="open: untrained, or trained\non simulated recordings")],
              loc="center left", frameon=False,
              title=f"every mark: a cell mean over\n{counted(n_fits, 'fit')} (count baselines:\n"
                    f"{counted(n_base, 'held-out fold')})",
              title_fontsize=9.5, alignment="left")

    cx = fig.add_subplot(gs[2, :])
    x = 0.0
    ticks, labels, bounds = [], [], []
    lanes = [("ssl_sim", -0.27, [(J, m) for J in (10.0, 20.0) for m in MODELS]),
             ("ssl_real", 0.0, [(J, m) for J in (10.0, 20.0) for m in MODELS]),
             ("baseline", 0.27, [(J, b) for J in (10.0, 20.0) for b in BASELINES])]
    for group, checks in CHECK_GROUPS:
        start = x
        for key, lab in checks:
            for arm, off, members in lanes:
                for k, (J, m) in enumerate(members):
                    c = cell(cells, arm, J, m)
                    if c and key in c["checks"]:
                        mark(cx, x + off + dodge(len(members), k, 0.2),
                             c["checks"][key]["share_mean"], m, arm, ms=4.5)
            ticks.append(x)
            labels.append(lab)
            x += 1
        bounds.append((start, x - 1, group))
        x += 0.5
    tr = blended_transform_factory(cx.transData, cx.transAxes)
    for i, (lo, hi, group) in enumerate(bounds):
        cx.text((lo + hi) / 2, 1.02, group, transform=tr, ha="center", va="bottom", fontsize=9.5)
        if i:
            cx.axvline(lo - 0.75, color="0.75", lw=0.8)
    cx.axhline(0.5, color="0.55", ls=":", lw=1)
    cx.set_xticks(ticks, labels, fontsize=8.6)
    cx.set_xlim(-0.6, x - 0.9)
    cx.set_ylim(0.0, 1.0)
    cx.set_ylabel("share of held-out crops where the\nreal crop scores higher (ties: half)")
    cx.set_xlabel(f"paired check. Within each: trained on simulated, trained on real, count "
                  f"baselines; both J pooled; small J = {j_small:g} s")
    cx.text(-0.1, 1.12, "C", transform=cx.transAxes, fontsize=13, fontweight="bold", va="bottom")
    fig.text(0.5, 0.012, "dotted line: chance, 0.5 · J: the rigid-shift displacement",
             ha="center", fontsize=9.5, color="0.3")
    fig.subplots_adjust(left=0.13, right=0.98, top=0.96, bottom=0.08)
    save(fig, "tube_ssl_fig.png", a, subfolder="tube_self_supervised")


if __name__ == "__main__":
    main()
