#!/usr/bin/env python3
"""Draw what each detector calls on real lab recordings, beside what it calls on their rigid shift.

    python tools/make_tube_real_summary_figure.py --summary <run>/summary.json
        [--out <folder>] [--also <folder>]

Reads the ``real_compare`` block of ``summary.json`` (``tools/summarize_tube_self_supervised.py``,
run with edges); writes ``tube_real_summary_fig.png``. One row per detector; each learned model and
count baseline appears twice, on the recordings and on a rigid shift of them. Exploratory.

Four columns share the rows:

* **A** — the share of events in which at least 3 ROIs have an onset, against the same share at
  uniformly random times and at times drawn in proportion to population activity.
* **B** — the share of events whose onset lies within 5 s of a recording edge, against what uniform
  placement gives. Rigid shift drops onsets pushed past an edge, so a detector trained against it
  can learn where edges are.
* **C, D** — the share of a detector's events that a CoactDetect event (C) or a LoCo event (D)
  overlaps within 1 s, against the same overlap at random times.
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

plt.rcParams.update({"font.size": 10.5, "axes.labelsize": 10.5, "xtick.labelsize": 10,
                     "ytick.labelsize": 9.5, "legend.fontsize": 9.5})

MODELS = {"line": ("#2a78d6", "o"), "line_length": ("#eb6834", "s"),
          "line_bound": ("#1baf7a", "D"), "tube": ("#6b6b6b", "o"), "tube_guard": ("#a8a8a8", "s")}
"""Model inks and shapes as in every other figure of the report."""
BASELINES = {"count_share": ("count share", "^"), "count_excess": ("count excess", "P"),
             "slow_modulation": ("slow modulation", "X")}
REFERENCE = {"coact": ("CoactDetect", "#111111", "o"), "loco": ("LoCo", "#111111", "s")}
EDGE_KEY = "within_5s"
SURROGATE = ", on its rigid shift"


def rows(stats):
    """(label, stats key, ink, marker, on_surrogate), top to bottom, in the report's order."""
    out = [(name, key, c, mk, False) for key, (name, c, mk) in REFERENCE.items()]
    for m, (c, mk) in MODELS.items():
        for key, name in ((f"supervised {m} label-free", f"{m}, supervised"),
                          (f"ssl {m} J10", f"{m}, no labels, J = 10 s"),
                          (f"ssl {m} J20", f"{m}, no labels, J = 20 s")):
            out.append((name, key, c, mk, False))
            out.append(("    on its rigid shift", key + SURROGATE, c, mk, True))
    for b, (name, mk) in BASELINES.items():
        key = f"baseline {b} label-free"
        out.append((f"{name} (no parameters)", key, "#111111", mk, False))
        out.append(("    on its rigid shift", key + SURROGATE, "#111111", mk, True))
    return [r for r in out if r[1] in stats]


def point(ax, x, y, colour, marker, hollow, ms=6.0):
    ax.plot([x], [y], marker, ms=ms, color="white" if hollow else colour, mec=colour, mew=1.3,
            zorder=3)


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--summary", required=True)
    add_arguments(ap)
    a = ap.parse_args(argv)
    s = json.loads(Path(a.summary).read_text())
    real = s["real_compare"]
    stats, agree, edges = real["stats"], real["agreement"], real["edge_shares"]
    R = rows(stats)
    y = list(range(len(R)))[::-1]

    fig, axes = plt.subplots(1, 4, figsize=(10.5, 0.27 * len(R) + 2.6), sharey=True,
                             gridspec_kw={"width_ratios": [1.2, 1.0, 1.0, 1.0], "wspace": 0.16})
    ax, bx, cx, dx = axes
    for yi, (label, key, c, mk, sur) in zip(y, R):
        st = stats[key]
        if yi % 2 == 0:
            for axis in axes:
                axis.axhspan(yi - 0.5, yi + 0.5, color="0.96", zorder=0)
        ax.plot([st["random_share_ge3"]], [yi], "|", ms=9, mew=1.6, color="0.45", zorder=2)
        ax.plot([st["activity_random_share_ge3"]], [yi], "x", ms=6, mew=1.4, color="0.45", zorder=2)
        point(ax, st["participation_share_ge3"], yi, c, mk, sur)
        e = edges.get(key)
        if e:
            point(bx, e[EDGE_KEY], yi, c, mk, sur)
        for axis, ref in ((cx, "coact"), (dx, "loco")):
            g = agree.get(f"{key} -> {ref}")
            if g:
                axis.plot([g["chance"]], [yi], "|", ms=9, mew=1.6, color="0.45", zorder=2)
                point(axis, g["share"], yi, c, mk, sur)
    labels = [f"{label}  ({stats[key]['events_per_10min']:.1f} per 10 min)" for label, key, *_ in R]
    ax.set_yticks(y, labels)
    ax.set_ylim(-0.7, len(R) - 0.3)
    ax.set_xlim(-0.06, 1.08)
    ax.set_xticks([0, 0.5, 1], ["0", "0.5", "1"])
    ax.set_xlabel("share of events\nwith onsets in\n≥ 3 ROIs", fontsize=9.5)
    uniform = edges[next(k for k in edges)]["uniform_expectation"][EDGE_KEY]
    bx.axvline(uniform, color="0.45", ls=":", lw=1.2)
    bx.set_xlim(-0.02, max(0.2, 1.1 * max(e[EDGE_KEY] for e in edges.values())))
    bx.set_xlabel("share of events\nstarting ≤ 5 s\nfrom an edge", fontsize=9.5)
    for axis, name in ((cx, "CoactDetect"), (dx, "LoCo")):
        axis.set_xlim(-0.06, 1.08)
        axis.set_xticks([0, 0.5, 1], ["0", "0.5", "1"])
        axis.set_xlabel(f"share of events\noverlapped by\n{name} (± 1 s)", fontsize=9.5)
    for axis, letter in zip(axes, "ABCD"):
        axis.text(0.0, 1.005, letter, transform=axis.transAxes, fontsize=13, fontweight="bold",
                  va="bottom", ha="left")
        axis.tick_params(axis="y", length=0)
    rate_note = "events per 10 min in brackets; counts pool every run of each detector"
    fig.legend(handles=[
        Line2D([], [], color="0.3", marker="o", ls="", ms=7, label="filled: on the recordings"),
        Line2D([], [], color="0.3", marker="o", ls="", ms=7, mfc="white", mew=1.3,
               label="open: on a rigid shift of them"),
        Line2D([], [], color="0.45", marker="|", ls="", ms=9, mew=1.6,
               label="A, C, D: same event widths at uniformly random times"),
        Line2D([], [], color="0.45", marker="x", ls="", ms=6, mew=1.4,
               label="A: at times drawn in proportion to population activity"),
        Line2D([], [], color="0.45", ls=":", lw=1.2,
               label=f"B: uniform placement, {uniform:.1%} of events")],
        loc="lower center", ncol=2, frameon=False, bbox_to_anchor=(0.5, 0.0))
    fig.text(0.5, 1.0 - 0.25 / fig.get_figheight(), rate_note, ha="center", va="top", fontsize=9.5,
             color="0.3")
    fig.subplots_adjust(left=0.36, right=0.98, top=1.0 - 0.75 / fig.get_figheight(),
                        bottom=1.9 / fig.get_figheight())
    save(fig, "tube_real_summary_fig.png", a, subfolder="tube_self_supervised")


if __name__ == "__main__":
    main()
