#!/usr/bin/env python3
"""Figures for ``tools/detect_with_floors.py``: the floors, and what each floor does to the calls.

    python tools/make_detect_floors_figure.py --run <run folder> --out <folder> [--also <repo dir>]

Reads ``windows.csv``. Each recording's **first treatment** is its first window, in the producer's
region order, whose label is not baseline. Groups are in ``bugarach.groups`` order.

* ``fig1_floors.png`` — per stream, each recording's first-treatment floor against its baseline
  floor (co-active ROIs), coloured by group, marked by treatment. On the diagonal the two floors
  agree; above it, the treatment's own events reach more co-active ROIs by chance.
* ``fig2_calls_per_hour.png`` — calls per hour, one mark per recording, for CoactDetect and
  ``chorus_norm``: at baseline, then in the first treatment window under its own floor and under
  the baseline floor. Rows are detector × first treatment, columns streams; the bar is the median.
"""
from __future__ import annotations

import argparse
import csv
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
MARK = {"senktide": "o", "TTX": "s"}


def load(run: Path):
    rows = list(csv.DictReader((run / "windows.csv").open(encoding="utf-8")))
    for r in rows:
        r["region_idx"] = int(r["region_idx"]) if r["region_idx"] not in ("", "None") else -1
        for k in ("own_floor", "baseline_floor", "calls_per_hour"):
            r[k] = float(r[k]) if r[k] not in ("", "None") else None
    first = {}
    for r in rows:
        if r["window_kind"] == "treatment":
            sid = r["slice_id"]
            if sid not in first or r["region_idx"] < first[sid]:
                first[sid] = r["region_idx"]
    return rows, first


def fig_floors(rows, first, out: Path) -> Path:
    fig, axes = plt.subplots(1, 3, figsize=(12, 4.4))
    for ax, st in zip(axes, STREAMS):
        pts = [r for r in rows if r["stream"] == st and r["detector"] == "coact"
               and r["variant"] == "tuned" and first.get(r["slice_id"]) == r["region_idx"]
               and r["own_floor"] is not None and r["baseline_floor"] is not None]
        hi = max([p["own_floor"] for p in pts] + [p["baseline_floor"] for p in pts] + [5]) + 2
        ax.plot([0, hi], [0, hi], color="0.6", lw=0.8)
        for p in pts:
            ax.plot(p["baseline_floor"] + np.random.uniform(-0.15, 0.15),
                    p["own_floor"] + np.random.uniform(-0.15, 0.15),
                    MARK.get(p["label"], "^"), color=COLOUR.get(p["group"], "0.4"), ms=5,
                    alpha=0.8)
        ax.set_xlabel(f"{st}: baseline floor, co-active ROIs")
        ax.set_xlim(0, hi)
        ax.set_ylim(0, hi)
    axes[0].set_ylabel("first-treatment window's\nown floor, co-active ROIs")
    groups = in_group_order(r["group"] for r in rows if r["group"])
    h = [Line2D([], [], marker="o", ls="none", color=COLOUR.get(g, "0.4"), label=g)
         for g in groups]
    h += [Line2D([], [], marker=m, ls="none", color="0.4", label=f"first treatment {t}")
          for t, m in MARK.items()]
    h += [Line2D([], [], color="0.6", label="the two floors agree")]
    fig.legend(handles=h, loc="lower center", ncol=7, fontsize=8, frameon=False)
    fig.subplots_adjust(bottom=0.25, wspace=0.25, left=0.07, right=0.99, top=0.97)
    p = out / "fig1_floors.png"
    fig.savefig(p, dpi=150)
    plt.close(fig)
    return p


def fig_calls(rows, first, out: Path) -> Path:
    groups = in_group_order(r["group"] for r in rows if r["group"])
    dets = (("coact", "tuned", "own_floor", "baseline_floor", "CoactDetect"),
            ("chorus_norm", "unfloored", "own_floor", "baseline_floor", "chorus_norm"))
    treatments = [t for t in MARK]
    fig, axes = plt.subplots(len(dets) * len(treatments), 3, figsize=(13, 12), squeeze=False)
    cols = ("baseline", "treatment, own floor", "treatment, baseline floor")
    for i, (det, base_var, own_var, bfl_var, dlabel) in enumerate(dets):
        for t_i, treat in enumerate(treatments):
            row_i = i * len(treatments) + t_i
            for j, st in enumerate(STREAMS):
                ax = axes[row_i, j]
                for gi, g in enumerate(groups):
                    sids = {r["slice_id"] for r in rows if r["group"] == g
                            and r["window_kind"] == "treatment" and r["label"] == treat
                            and first.get(r["slice_id"]) == r["region_idx"]}
                    series = []
                    for ci, (kind, var) in enumerate((("baseline", "own_floor"),
                                                      ("treatment", own_var),
                                                      ("treatment", bfl_var))):
                        v = [r["calls_per_hour"] for r in rows
                             if r["slice_id"] in sids and r["stream"] == st
                             and r["detector"] == det and r["variant"] == var
                             and r["window_kind"] == kind and r["calls_per_hour"] is not None
                             and (kind == "baseline" or first.get(r["slice_id"])
                                  == r["region_idx"])]
                        x = gi * 4 + ci
                        ax.plot(x + np.random.uniform(-0.18, 0.18, len(v)), v, "o", ms=3,
                                color=COLOUR.get(g, "0.4"), alpha=[0.35, 0.8, 0.8][ci],
                                mfc=[None, None, "white"][ci])
                        if v:
                            ax.plot([x - 0.3, x + 0.3], [np.median(v)] * 2, color="0.2", lw=1.6)
                        series.append(len(v))
                ax.set_xticks([gi * 4 + 1 for gi in range(len(groups))])
                ax.set_xticklabels([f"{g}" for g in groups], fontsize=8)
                ax.set_yscale("symlog", linthresh=1)
                ax.set_ylim(bottom=0)
                if j == 0:
                    ax.set_ylabel(f"{dlabel}\nfirst treatment {treat}\ncalls per hour",
                                  fontsize=8.5)
                if row_i == len(dets) * len(treatments) - 1:
                    ax.set_xlabel(f"{st} stream", fontsize=9)
    h = [Line2D([], [], marker="o", ls="none", color="0.4", alpha=0.35, label=cols[0]),
         Line2D([], [], marker="o", ls="none", color="0.4", label=cols[1]),
         Line2D([], [], marker="o", ls="none", color="0.4", mfc="white", label=cols[2]),
         Line2D([], [], color="0.2", lw=1.6, label="median over recordings")]
    h += [Line2D([], [], marker="o", ls="none", color=COLOUR.get(g, "0.4"), label=g)
          for g in groups]
    fig.legend(handles=h, loc="lower center", ncol=8, fontsize=8, frameon=False,
               title="within each group, left to right", title_fontsize=8)
    fig.subplots_adjust(left=0.08, right=0.99, top=0.99, bottom=0.09, hspace=0.25, wspace=0.18)
    p = out / "fig2_calls_per_hour.png"
    fig.savefig(p, dpi=150)
    plt.close(fig)
    return p


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--run", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--also", type=Path, default=None)
    a = ap.parse_args(argv)
    np.random.seed(0)
    rows, first = load(a.run)
    a.out.mkdir(parents=True, exist_ok=True)
    made = [fig_floors(rows, first, a.out), fig_calls(rows, first, a.out)]
    if a.also:
        a.also.mkdir(parents=True, exist_ok=True)
        for p in made:
            shutil.copy2(p, a.also / p.name)
    for p in made:
        print(p)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
