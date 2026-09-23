#!/usr/bin/env python3
"""The group question in three figures: co-modulation, rate and participation, each group's number
drawn with what one recording can do to it.

    python tools/make_group_comparison_figure.py --run <folder> [--also docs/learned/runs/<name>]

``<folder>`` holds ``comodulation/summary.json`` from ``tools/measure_slow_comodulation.py`` and
``rates/coordination_rates.json`` from ``tools/measure_coordination_rates.py --by-group``. Figures
go to ``--out`` (default: ``<folder>`` itself, which is a darkroom folder) and ``--also`` copies
them into the repo.

Every panel draws a group the same way: a dot at the group's number, a **thin whisker** for the
95% interval of the bootstrap over mice, a **thick bar** for the leave-one-out range (the number
with each recording dropped in turn), and a **hollow ring** where the number lands without its
most influential recording. A gap between two groups is readable only if it is wider than both
thick bars. Groups are in ``bugarach.groups`` order.

* ``fig1_comodulation_by_group.png`` — pooled 1-minute count-variance ratio, as recorded and with
  CoactDetect's episodes removed plus the 120 s block control, per stream.
* ``fig2_rate_by_group.png`` — per-ROI rate and background rate against the bench's two regimes
  and, on the fast stream, the grid its rate sweep scores across.
* ``fig3_participation_by_group.png`` — participation and shared moments per minute against the
  bench's three planted participation levels.
"""
from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from matplotlib.lines import Line2D  # noqa: E402
from matplotlib.patches import Patch  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from bugarach.groups import in_group_order  # noqa: E402

STREAMS = ("fast", "slow", "combined")
INK = "#1f3b73"
BENCH = "#c9d4e8"


def _group(ax, x, value, interval, loo):
    """One group: bootstrap whisker, leave-one-out bar, value dot, ring without its biggest mover."""
    if interval:
        ax.plot([x, x], interval, color=INK, lw=1.0, zorder=2)
    if loo:
        lo, hi = min(loo["lo"], value), max(loo["hi"], value)
        ax.plot([x, x], [lo, hi], color=INK, lw=6, alpha=0.35, solid_capstyle="butt", zorder=3)
        if loo.get("without") is not None and np.isfinite(loo["without"]):
            ax.plot(x, loo["without"], "o", mfc="white", mec=INK, ms=7, mew=1.2, zorder=4)
    ax.plot(x, value, "o", color=INK, ms=6, zorder=5)


def _xgroups(ax, groups, counts):
    ax.set_xticks(range(len(groups)))
    ax.set_xticklabels([f"{g}\n{counts[g]} recordings" for g in groups], fontsize=8)
    ax.set_xlim(-0.6, len(groups) - 0.4)


def _legend(fig, extra=()):
    handles = [Line2D([], [], color=INK, marker="o", ls="none", label="group's number"),
               Line2D([], [], color=INK, lw=1.0, label="95% bootstrap over mice"),
               Line2D([], [], color=INK, lw=6, alpha=0.35,
                      label="leave-one-out range (one recording dropped)"),
               Line2D([], [], color=INK, marker="o", mfc="white", ls="none",
                      label="without its most influential recording"), *extra]
    fig.legend(handles=handles, loc="lower center", ncol=3, fontsize=8, frameon=False)


def figure_comodulation(summary: dict, out: Path) -> Path:
    folders = {k.split("/")[1]: v for k, v in summary["folders"].items()
               if k.split("/")[1] in STREAMS}
    arms = (("real", "as recorded"), ("minus_coact_block_120", "episodes removed\n+ 120 s block"))
    fig, axes = plt.subplots(len(arms), len(STREAMS), figsize=(11, 6.4), sharex=True,
                             squeeze=False)
    for j, stream in enumerate(STREAMS):
        F = folders[stream]
        G = F["group_influence"]
        groups = in_group_order(G["groups"])
        for i, (arm, arm_label) in enumerate(arms):
            ax = axes[i, j]
            ax.axhline(1.0, color="0.6", lw=0.8, ls=":")
            for x, g in enumerate(groups):
                bg = F["by_group"][g]["arms"][arm]
                _group(ax, x, bg["var_ratio"][-1], [bg["var_lo"][-1], bg["var_hi"][-1]],
                       G["arms"][arm]["leave_one_out"][g])
            _xgroups(ax, groups, G["recordings"])
            if j == 0:
                ax.set_ylabel(f"{arm_label}\ncount variance ÷ independent")
            ax.text(0.02, 0.97, stream, transform=ax.transAxes, va="top", fontsize=9,
                    color="0.35")
    _legend(fig, [Line2D([], [], color="0.6", ls=":", label="1 = ROIs independent")])
    fig.subplots_adjust(bottom=0.2, wspace=0.28, hspace=0.12, left=0.08, right=0.98, top=0.97)
    p = out / "fig1_comodulation_by_group.png"
    fig.savefig(p, dpi=150)
    plt.close(fig)
    return p


def figure_rates(rates: dict, out: Path) -> Path:
    fig, axes = plt.subplots(2, len(STREAMS), figsize=(11, 6.4), squeeze=False)
    rows = (("rate_median_hz", "per-ROI rate, Hz\n(median of recordings)"),
            ("background_median_hz", "background rate, Hz\n(coordinated share removed)"))
    for j, stream in enumerate(STREAMS):
        B = rates["by_group"][stream]
        groups = in_group_order(B["groups"])
        ax_bench = B["bench"]
        for i, (name, label) in enumerate(rows):
            ax = axes[i, j]
            if name == "background_median_hz":
                ax.axhspan(ax_bench["quiet_hz"], ax_bench["busy_hz"], color=BENCH, zorder=0)
                if ax_bench["background_grid_hz"]:
                    for y in (min(ax_bench["background_grid_hz"]),
                              max(ax_bench["background_grid_hz"])):
                        ax.axhline(y, color="0.5", ls="--", lw=0.8)
                for x, g in enumerate(groups):
                    s = B["stats"]
                    ax.plot([x + 0.28] * 2, [s["background_q25_hz"]["groups"][g]["value"],
                                             s["background_q75_hz"]["groups"][g]["value"]],
                            color="0.35", lw=2.5, solid_capstyle="butt")
            S = B["stats"][name]["groups"]
            for x, g in enumerate(groups):
                _group(ax, x, S[g]["value"], S[g]["interval"], S[g]["leave_one_out"])
            _xgroups(ax, groups, B["recordings"])
            ax.set_ylim(bottom=0)
            if j == 0:
                ax.set_ylabel(label)
            ax.text(0.02, 0.97, stream, transform=ax.transAxes, va="top", fontsize=9,
                    color="0.35")
    _legend(fig, [Patch(color=BENCH, label="bench's quiet–busy regimes"),
                  Line2D([], [], color="0.5", ls="--", label="ends of the fast bench's rate sweep"),
                  Line2D([], [], color="0.35", lw=2.5,
                         label="group's interquartile background (beside the dot)")])
    fig.subplots_adjust(bottom=0.22, wspace=0.3, hspace=0.25, left=0.09, right=0.98, top=0.97)
    p = out / "fig2_rate_by_group.png"
    fig.savefig(p, dpi=150)
    plt.close(fig)
    return p


def figure_participation(rates: dict, out: Path) -> Path:
    fig, axes = plt.subplots(2, len(STREAMS), figsize=(11, 6.4), squeeze=False)
    rows = (("participation", "participation\n(share of ROIs per shared moment)"),
            ("shared_moments_per_min", "shared moments per minute"))
    for j, stream in enumerate(STREAMS):
        B = rates["by_group"][stream]
        groups = in_group_order(B["groups"])
        for i, (name, label) in enumerate(rows):
            ax = axes[i, j]
            if name == "participation":
                for lv in B["bench"]["participation_levels"]:
                    ax.axhline(lv, color="0.5", ls="--", lw=0.8)
                ax.axhline(1.0, color="#b03a2e", ls=":", lw=1.0)
            S = B["stats"][name]["groups"]
            for x, g in enumerate(groups):
                _group(ax, x, S[g]["value"], S[g]["interval"], S[g]["leave_one_out"])
            _xgroups(ax, groups, B["recordings"])
            ax.set_ylim(bottom=0)
            if j == 0:
                ax.set_ylabel(label)
            ax.text(0.02, 0.97, stream, transform=ax.transAxes, va="top", fontsize=9,
                    color="0.35")
    _legend(fig, [Line2D([], [], color="0.5", ls="--",
                         label="bench's three planted participation levels"),
                  Line2D([], [], color="#b03a2e", ls=":",
                         label="every ROI (above it the estimator has saturated)")])
    fig.subplots_adjust(bottom=0.2, wspace=0.3, hspace=0.25, left=0.09, right=0.98, top=0.97)
    p = out / "fig3_participation_by_group.png"
    fig.savefig(p, dpi=150)
    plt.close(fig)
    return p


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--run", type=Path, required=True)
    ap.add_argument("--out", type=Path, default=None, help="default: --run")
    ap.add_argument("--also", type=Path, default=None, help="copy the figures here too")
    a = ap.parse_args(argv)
    out = a.out or a.run
    out.mkdir(parents=True, exist_ok=True)
    summary = json.loads((a.run / "comodulation" / "summary.json").read_text())
    rates = json.loads((a.run / "rates" / "coordination_rates.json").read_text())
    made = [figure_comodulation(summary, out), figure_rates(rates, out),
            figure_participation(rates, out)]
    if a.also:
        a.also.mkdir(parents=True, exist_ok=True)
        for p in made:
            shutil.copy2(p, a.also / p.name)
    for p in made:
        print(p)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
