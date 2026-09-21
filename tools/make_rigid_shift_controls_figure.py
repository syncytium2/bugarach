#!/usr/bin/env python3
"""Draw the rigid-shift controls: the shared-offset leak control and Cossart destruction.

    python tools/make_rigid_shift_controls_figure.py --lab <folder> --cossart <folder> --out <folder>

Reads the ``results.json`` written by ``tools/look_rigid_shift_controls.py`` for each folder.
Writes ``controls_fig1_leak.png`` and ``controls_fig2_cossart_destruction.png``. Exploratory:
the lines at 0.55 and 0.25 are the thresholds Tony signed, drawn for reference.
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

INK = {"rigid_shift": "#1f4e79", "shared_shift": "#c07a12"}
LABEL = {"rigid_shift": "rigid shift: each ROI its own offset",
         "shared_shift": "shared offset: every ROI the same offset (control)"}


def _leak(ax, rows, title_y, letter):
    rows = sorted(rows, key=lambda r: r["J_sec"])
    Js = np.array([r["J_sec"] for r in rows])
    for name, f in (("rigid_shift", 0.97), ("shared_shift", 1.03)):
        m = np.array([r[name]["accuracy_fold_seed_mean"] for r in rows])
        lo = np.array([r[name]["by_mouse"]["p1_67"] for r in rows])
        hi = np.array([r[name]["by_mouse"]["p98_33"] for r in rows])
        ax.vlines(Js * f, lo, hi, color=INK[name], lw=2)
        ax.plot(Js * f, m, "o-", color=INK[name], ms=5, lw=1)
    ax.axhline(0.5, color="0.55", lw=0.9, ls=":")
    ax.axhline(0.55, color="0.25", lw=0.9, ls="--")
    ax.set_xscale("log")
    ax.set_xticks(Js, [f"{J:g}" for J in Js])
    ax.minorticks_off()
    ax.set_ylim(0.43, 0.65)
    n = rows[0]
    ax.set_ylabel(f"{title_y} · forced-choice accuracy\n({n['n_pairs']:,} window pairs, "
                  f"{n['n_mice']} mice)")
    ax.set_xlabel("displacement J (s)")
    ax.text(0.02, 0.97, letter, transform=ax.transAxes, fontsize=12, fontweight="bold", va="top")


def fig_leak(lab, cos, out):
    fig, axes = plt.subplots(1, 3, figsize=(13.5, 4.4), sharey=True)
    _leak(axes[0], [r for r in lab["leak"] if r["stream"] == "fast"], "lab fast stream", "A")
    _leak(axes[1], [r for r in lab["leak"] if r["stream"] == "slow"], "lab slow stream", "B")
    _leak(axes[2], cos["leak"], "Cossart folder", "C")
    for ax in axes[1:]:
        ax.tick_params(labelleft=True)
    handles = [Line2D([], [], color=INK[n], marker="o", lw=2, label=LABEL[n])
               for n in ("rigid_shift", "shared_shift")]
    handles += [Line2D([], [], color="0.55", ls=":", label="chance, 0.5"),
                Line2D([], [], color="0.25", ls="--", label="signed leak line, 0.55"),
                Line2D([], [], color="0.3", lw=2, label="bar: 1.67–98.33 percentile over mice; "
                                                       "dot: mean over 10 fold seeds")]
    fig.legend(handles=handles, loc="upper center", ncol=3, frameon=False, fontsize=9)
    fig.tight_layout(rect=(0, 0, 1, 0.86))
    p = out / "controls_fig1_leak.png"
    fig.savefig(p, dpi=150)
    plt.close(fig)
    return p


def retained(rows, K, n_boot=2000, seed=20260915):
    before = np.array([r["before"][str(K)] for r in rows], float)
    after = np.array([r["after"][str(K)] for r in rows], float)
    point = after.mean() / before.mean()
    rs = np.random.RandomState(seed)
    idx = rs.randint(len(rows), size=(n_boot, len(rows)))
    d = after[idx].mean(1) / before[idx].mean(1)
    return point, *np.percentile(d, [2.5, 97.5])


def fig_destruction(cos, out):
    d = cos["destruction"][0]
    Ks = d["k_scan"]
    rig = sorted([v for v in d["variants"] if v.startswith("rigid_shift@")],
                 key=lambda v: float(v.split("@")[1]))
    Js = np.array([float(v.split("@")[1]) for v in rig])
    ramp = plt.get_cmap("viridis")(np.linspace(0.05, 0.85, len(Ks)))
    fig, (ax, bx) = plt.subplots(1, 2, figsize=(12.5, 4.6),
                                 gridspec_kw={"width_ratios": [2.2, 1]}, sharey=True)
    for K, c, dx in zip(Ks, ramp, np.linspace(-0.06, 0.06, len(Ks))):
        pts = [retained(d["variants"][v], K) for v in rig]
        f = np.exp(dx)
        ax.vlines(Js * f, [q[1] for q in pts], [q[2] for q in pts], color=c, lw=1.6)
        ax.plot(Js * f, [q[0] for q in pts], "o-", color=c, ms=5, lw=1.2, label=f"K = {K} ROIs")
    ax.axhline(0.25, color="0.25", lw=0.9, ls="--")
    ax.axhline(0.0, color="0.6", lw=0.8, ls=":")
    ax.set_xscale("log")
    ax.set_xticks(Js, [f"{J:g}" for J in Js])
    ax.minorticks_off()
    ax.set_xlabel("rigid-shift displacement J (s)")
    ax.set_ylabel(f"Cossart twins · retained share of planted coordination\n"
                  f"(events in 8.1 % of {d['twin_shape']['n_roi']} ROIs, 1 s bin, "
                  f"{d['n_twins']} twin pairs)")
    ax.text(0.02, 0.97, "A", transform=ax.transAxes, fontsize=12, fontweight="bold", va="top")
    names = [("homogeneous_resample", "homogeneous\nresample"),
             ("freeze_half", "freeze half\n(graded)"), ("do_nothing", "do nothing")]
    for i, (v, lab) in enumerate(names):
        for K, c, dx in zip(Ks, ramp, np.linspace(-0.25, 0.25, len(Ks))):
            q = retained(d["variants"][v], K)
            bx.vlines(i + dx, q[1], q[2], color=c, lw=1.6)
            bx.plot(i + dx, q[0], "o", color=c, ms=5)
    bx.set_xticks(range(len(names)), [n for _, n in names])
    bx.axhline(0.25, color="0.25", lw=0.9, ls="--")
    bx.axhline(0.0, color="0.6", lw=0.8, ls=":")
    bx.set_xlabel("controls (same twins, same K)")
    bx.text(0.04, 0.97, "B", transform=bx.transAxes, fontsize=12, fontweight="bold", va="top")
    handles = [Line2D([], [], color=c, marker="o", lw=1.2, label=f"K = {K} co-active ROIs")
               for K, c in zip(Ks, ramp)]
    handles += [Line2D([], [], color="0.25", ls="--", label="signed retained line, 0.25"),
                Line2D([], [], color="0.3", lw=1.6, label="bar: 95 % bootstrap over twin pairs")]
    fig.legend(handles=handles, loc="upper center", ncol=4, frameon=False, fontsize=9)
    fig.tight_layout(rect=(0, 0, 1, 0.86))
    p = out / "controls_fig2_cossart_destruction.png"
    fig.savefig(p, dpi=150)
    plt.close(fig)
    return p


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--lab", required=True)
    ap.add_argument("--cossart", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args(argv)
    lab = json.loads((Path(a.lab) / "results.json").read_text())
    cos = json.loads((Path(a.cossart) / "results.json").read_text())
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    print(fig_leak(lab, cos, out))
    print(fig_destruction(cos, out))


if __name__ == "__main__":
    main()
