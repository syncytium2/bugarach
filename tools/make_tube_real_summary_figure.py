#!/usr/bin/env python3
"""Draw what each detector calls on real lab recordings, beside what it calls on a rigid shift of them.

    python tools/make_tube_real_summary_figure.py --summary <run>/summary.json
        [--out <folder>] [--also <folder>]

Reads the ``real_compare`` block of ``summary.json`` (``tools/summarize_tube_self_supervised.py``);
writes ``tube_real_summary_fig.png``. One row per detector; each learned model and zero-parameter
baseline appears twice, on the recordings and, in a shaded row, on a fresh rigid shift of them that no
threshold was set on, measured against the shifted onsets. Exploratory.

Four columns share the rows:

* **A** — the share of events with onsets in at least 3 ROIs within the event's span ±0.2 s, against
  the same share at times drawn in proportion to population activity.
* **B** — the share of events within 3 s of a frame where at least 3 ROIs have an onset, against the
  same at activity-weighted random times: whether a detector fires beside co-activity even when not
  on it.
* **C** — the share of events whose span holds no onset in any ROI.
* **D** — the share of events starting within 5 s of either end of the recording, against uniform
  placement.

Agreement with CoactDetect and LoCo is in the report's table, not drawn here. Chance marks are drawn
above the detector marks so a detector sitting on its chance does not hide it.
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
BASELINES = {"count_share": ("count_share", "^"), "count_excess": ("count_excess", "P"),
             "slow_modulation": ("slow_modulation", "X")}
REFERENCE = {"coact": ("CoactDetect", "#111111", "o"), "loco": ("LoCo", "#111111", "s")}
SURROGATE = ", on its rigid shift"
CHANCE = "#111111"
"""Chance marks: a black vertical bar, a shape no detector uses (a red bar read too close to
`line_length`'s orange)."""


def rows(stats):
    """(label, stats key, ink, marker, on_surrogate), top to bottom, in the report's order."""
    out = [(name, key, c, mk, False) for key, (name, c, mk) in REFERENCE.items()]
    for m, (c, mk) in MODELS.items():
        for key, name in ((f"supervised {m} label-free", f"{m}, supervised"),
                          (f"ssl {m} J10", f"{m}, real-trained, J 10 s"),
                          (f"ssl {m} J20", f"{m}, real-trained, J 20 s")):
            out.append((name, key, c, mk, False))
            out.append(("on a rigid shift", key + SURROGATE, c, mk, True))
    for b, (name, mk) in BASELINES.items():
        key = f"baseline {b} label-free"
        out.append((f"{name} (no parameters)", key, "#111111", mk, False))
        out.append(("on a rigid shift", key + SURROGATE, "#111111", mk, True))
    return [r for r in out if r[1] in stats]


def point(ax, x, y, colour, marker, hollow, ms=6.0):
    if x is None:
        return
    ax.plot([x], [y], marker, ms=ms, color="white" if hollow else colour, mec=colour, mew=1.3,
            zorder=3)


def chance(ax, x, y):
    if x is not None:
        ax.plot([x], [y], "|", ms=11, mew=2.0, color=CHANCE, zorder=4)


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--summary", required=True)
    add_arguments(ap)
    a = ap.parse_args(argv)
    s = json.loads(Path(a.summary).read_text())
    stats = s["real_compare"]["stats"]
    R = rows(stats)
    y = list(range(len(R)))[::-1]

    fig, axes = plt.subplots(1, 4, figsize=(10.5, 0.27 * len(R) + 2.8), sharey=True,
                             gridspec_kw={"width_ratios": [1.0, 1.0, 1.0, 1.0], "wspace": 0.16})
    ax, bx, cx, dx = axes
    for yi, (label, key, c, mk, sur) in zip(y, R):
        st = stats[key]
        if sur:
            for axis in axes:
                axis.axhspan(yi - 0.5, yi + 0.5, color="0.93", zorder=0)
        point(ax, st["participation_share_ge3"], yi, c, mk, False)
        chance(ax, st["activity_random_share_ge3"], yi)
        point(bx, st.get("near_coactive_3s_share"), yi, c, mk, False)
        chance(bx, st.get("activity_random_near_coactive_3s_share"), yi)
        point(cx, st.get("empty_span_share"), yi, c, mk, False)
        point(dx, st.get("edge_within_5s_share"), yi, c, mk, False)
    labels = [(f"{label}  ({stats[key]['events_per_10min']:.1f} per 10 min)" if not sur
               else f"{label}  ({stats[key]['events_per_10min']:.1f})")
              for label, key, c, mk, sur in R]
    ax.set_yticks(y, labels)
    ax.set_ylim(-0.7, len(R) - 0.3)
    for axis in (ax, bx, cx):
        axis.set_xlim(-0.06, 1.08)
        axis.set_xticks([0, 0.5, 1], ["0", "0.5", "1"])
    ax.set_xlabel("share of events with\nonsets in ≥ 3 ROIs\n(span ± 0.2 s)", fontsize=9.5)
    bx.set_xlabel("share of events within\n3 s of a frame with\n≥ 3 ROIs active", fontsize=9.5)
    cx.set_xlabel("share of events\nwhose span holds\nno onset", fontsize=9.5)
    uniform = next((v["edge_within_5s_uniform_expectation"] for v in stats.values()
                    if v.get("edge_within_5s_uniform_expectation")), None)
    if uniform is not None:
        dx.axvline(uniform, color=CHANCE, ls=":", lw=1.4, zorder=4)
    top = max(v.get("edge_within_5s_share") or 0 for v in stats.values())
    dx.set_xlim(-0.01, max(0.2, 1.1 * top))
    dx.set_xlabel("share of events\nstarting ≤ 5 s from\na recording's end", fontsize=9.5)
    for axis, letter in zip(axes, "ABCD"):
        axis.text(0.0, 1.005, letter, transform=axis.transAxes, fontsize=13, fontweight="bold",
                  va="bottom", ha="left")
        axis.tick_params(axis="y", length=0)
    fig.legend(handles=[
        Line2D([], [], color="0.3", marker="o", ls="", ms=7,
               label="a detector's events (shape and ink: model or baseline)"),
        Line2D([], [], color=CHANCE, marker="|", ls="", ms=11, mew=2.0,
               label="A, B: the same widths at times drawn in proportion to population activity"),
        Line2D([], [], color=CHANCE, ls=":", lw=1.4,
               label="D: uniform placement" + (f", {uniform:.1%} of events" if uniform else "")),
        Line2D([], [], color="0.93", marker="s", ls="", ms=12,
               label="shaded row: the detector above, on a fresh rigid shift of each recording,\n"
                     "measured against the shifted onsets"),
        Line2D([], [], ls="", label="real-trained: trained against rigid shift on real recordings")],
        loc="lower center", ncol=1, frameon=False, bbox_to_anchor=(0.5, 0.0))
    fig.text(0.5, 1.0 - 0.25 / fig.get_figheight(),
             "events per 10 min in parentheses; each learned row pools its training seeds",
             ha="center", va="top", fontsize=9.5, color="0.3")
    fig.subplots_adjust(left=0.35, right=0.98, top=1.0 - 0.75 / fig.get_figheight(),
                        bottom=2.6 / fig.get_figheight())
    save(fig, "tube_real_summary_fig.png", a, subfolder="tube_self_supervised")


if __name__ == "__main__":
    main()
