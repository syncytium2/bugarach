#!/usr/bin/env python3
"""The chance floor in four figures, from ``tools/measure_chance_floor.py``'s ``results.json``.

    python tools/make_chance_floor_figure.py --run <folder> [--also docs/learned/runs/<name>]

Figures go to ``--out`` (default ``--run``, a darkroom folder); ``--also`` copies them to the repo.
One panel per stream (fast, slow, combined); groups coloured in ``bugarach.groups`` order. Floors
are whole ROIs, so recordings that share a value are spread sideways by a fixed small offset per
group rather than drawn on top of each other.

* ``fig1_floor_vs_rois.png`` — the empirical floor (rigid-shift null, at most one call per hour)
  against ROI count, with the pooled fixed-count, fixed-fraction and count-plus-fraction lines.
* ``fig2_floor_fraction_vs_rois.png`` — the same floor as a fraction of the ROI count.
* ``fig3_floor_vs_rate.png`` — the floor against the recording's mean per-ROI rate.
* ``fig4_empirical_vs_closed_form.png`` — the empirical floor against the probe's closed form and
  against the Poisson-binomial at the bench's window, one recording per mark.
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

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from bugarach.groups import in_group_order  # noqa: E402

STREAMS = ("fast", "slow", "combined")
COLOUR = {"DI": "#0072B2", "OVX": "#E69F00", "MALE": "#009E73", "ORX": "#CC79A7"}
"""Okabe–Ito colours, readable with the common colour-vision deficiencies."""


def _offset(groups):
    return {g: (i - (len(groups) - 1) / 2) * 0.35 for i, g in enumerate(groups)}


def _groups(R):
    return in_group_order(r["group"] for S in R["streams"].values() for r in S["rows"]
                          if r.get("group"))


def _legend(fig, groups, R, extra=()):
    n = {g: sum(1 for r in R["streams"]["fast"]["rows"] if r["group"] == g) for g in groups}
    handles = [Line2D([], [], marker="o", ls="none", color=COLOUR.get(g, "0.4"),
                      label=f"{g} ({n[g]} recordings)") for g in groups]
    fig.legend(handles=[*handles, *extra], loc="lower center", ncol=4, fontsize=8, frameon=False)


def figure_floor(R, out: Path, fraction: bool) -> Path:
    groups = _groups(R)
    off = _offset(groups)
    fig, axes = plt.subplots(1, 3, figsize=(12, 4.4), sharey=True)
    for ax, stream in zip(axes, STREAMS):
        S = R["streams"][stream]
        rows = S["rows"]
        for r in rows:
            y = r["floor_fraction"] if fraction else r["floor"]
            ax.plot(r["n_roi"] + off.get(r["group"], 0), y, "o", ms=4.5, alpha=0.8,
                    color=COLOUR.get(r["group"], "0.4"))
        sc = S["by_group"]["scaling"]["pooled"]
        n = np.linspace(min(r["n_roi"] for r in rows), max(r["n_roi"] for r in rows), 50)
        c, f = sc["count_rule"]["count"], sc["fraction_rule"]["fraction"]
        a, b = sc["count_and_fraction_rule"]["count"], sc["count_and_fraction_rule"]["fraction"]
        lines = ((c + 0 * n, "-", "fixed count"), (f * n, "--", "fixed fraction"),
                 (a + b * n, ":", "count + fraction"))
        for y, ls, _ in lines:
            ax.plot(n, y / n if fraction else y, ls, color="0.35", lw=1.1)
        ax.text(0.02, 0.97, f"{stream} · slope on log ROIs "
                f"{sc['slope_log_floor_on_log_rois']:.2f}",
                transform=ax.transAxes, va="top", fontsize=9, color="0.3")
        ax.set_xlabel("ROIs in the recording")
    axes[0].set_ylabel("chance floor as a fraction of the ROIs" if fraction
                       else "chance floor, co-active ROIs")
    _legend(fig, groups, R, [Line2D([], [], ls=ls, color="0.35", label=f"pooled {lab} rule")
                             for _, ls, lab in lines])
    fig.subplots_adjust(bottom=0.27, wspace=0.08, left=0.07, right=0.99, top=0.97)
    p = out / ("fig2_floor_fraction_vs_rois.png" if fraction else "fig1_floor_vs_rois.png")
    fig.savefig(p, dpi=150)
    plt.close(fig)
    return p


def figure_rate(R, out: Path) -> Path:
    groups = _groups(R)
    fig, axes = plt.subplots(1, 3, figsize=(12, 4.4), sharey=True)
    for ax, stream in zip(axes, STREAMS):
        for r in R["streams"][stream]["rows"]:
            if r["mean_rate_hz"] > 0:
                ax.plot(r["mean_rate_hz"], r["floor"], "o", ms=4.5, alpha=0.8,
                        color=COLOUR.get(r["group"], "0.4"))
        ax.set_xscale("log")
        ax.set_xlabel("mean per-ROI rate on the baseline window, Hz")
        ax.text(0.02, 0.97, stream, transform=ax.transAxes, va="top", fontsize=9, color="0.3")
    axes[0].set_ylabel("chance floor, co-active ROIs")
    _legend(fig, groups, R)
    fig.subplots_adjust(bottom=0.24, wspace=0.08, left=0.07, right=0.99, top=0.97)
    p = out / "fig3_floor_vs_rate.png"
    fig.savefig(p, dpi=150)
    plt.close(fig)
    return p


def figure_closed_form(R, out: Path) -> Path:
    groups = _groups(R)
    forms = (("probe_homogeneous", "probe's closed form\n(one rate, 0.9 s widening)"),
             ("window_poisson_binomial", "Poisson-binomial at the\nbench's 2 s window"))
    fig, axes = plt.subplots(2, 3, figsize=(12, 7.6), sharex=True, sharey=True)
    rs = np.random.RandomState(0)
    for j, stream in enumerate(STREAMS):
        rows = R["streams"][stream]["rows"]
        hi = max(max(r["floor"] for r in rows),
                 max(r["closed_form"][k] for r in rows for k, _ in forms)) + 1
        for i, (key, label) in enumerate(forms):
            ax = axes[i, j]
            ax.plot([0, hi], [0, hi], color="0.6", lw=0.8)
            for r in rows:
                ax.plot(r["closed_form"][key] + rs.uniform(-0.2, 0.2),
                        r["floor"] + rs.uniform(-0.2, 0.2), "o", ms=4, alpha=0.75,
                        color=COLOUR.get(r["group"], "0.4"))
            if j == 0:
                ax.set_ylabel(f"empirical floor, ROIs\nagainst the {label}", fontsize=8.5)
            if i == 1:
                ax.set_xlabel("closed-form floor, ROIs")
            if i == 0:
                ax.text(0.02, 0.97, stream, transform=ax.transAxes, va="top", fontsize=9,
                        color="0.3")
    _legend(fig, groups, R, [Line2D([], [], color="0.6", label="the two agree")])
    fig.subplots_adjust(bottom=0.14, wspace=0.08, hspace=0.08, left=0.1, right=0.99, top=0.98)
    p = out / "fig4_empirical_vs_closed_form.png"
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
    R = json.loads((a.run / "results.json").read_text())
    made = [figure_floor(R, out, False), figure_floor(R, out, True), figure_rate(R, out),
            figure_closed_form(R, out)]
    if a.also:
        a.also.mkdir(parents=True, exist_ok=True)
        for p in made:
            shutil.copy2(p, a.also / p.name)
    for p in made:
        print(p)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
