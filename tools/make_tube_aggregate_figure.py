#!/usr/bin/env python3
"""Draw Stage 1 of the tube plan: what tube's cells-mean channel can tell apart, by scale.

    python tools/make_tube_aggregate_figure.py --run <folder> --out <folder>

Reads ``results.json`` from ``tools/tube_aggregate_leak.py``; writes ``tube_aggregate_fig.png``.
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

INK = {"real_vs_rigid_shift": "#1f4e79", "real_vs_shared_offset": "#c07a12"}


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args(argv)
    R = json.loads((Path(a.run) / "results.json").read_text())
    meta = json.loads((Path(a.run) / "meta.json").read_text())
    centres = meta["centres_frames"]
    streams = ["fast", "slow"]
    Js = {s: sorted({r["J_sec"] for r in R if r["stream"] == s}) for s in streams}
    ramp = {s: plt.get_cmap("Blues")(np.linspace(0.45, 0.95, len(Js[s]))) for s in streams}
    oramp = {s: plt.get_cmap("Oranges")(np.linspace(0.45, 0.95, len(Js[s]))) for s in streams}
    fig, axes = plt.subplots(2, 2, figsize=(12.5, 8.2),
                             gridspec_kw={"width_ratios": [2.2, 1]})
    dt = 0.1
    for i, s in enumerate(streams):
        ax, bx = axes[i]
        for j, J in enumerate(Js[s]):
            r = next(x for x in R if x["stream"] == s and x["J_sec"] == J and x["kind"] == "real")
            for key, cmap in (("real_vs_rigid_shift", ramp), ("real_vs_shared_offset", oramp)):
                acc = [r[key][str(c)]["accuracy"] for c in centres]
                ax.plot([c * dt for c in centres], acc, "o-", color=cmap[s][j], ms=4, lw=1.3)
        ax.axhline(0.5, color="0.55", ls=":", lw=0.9)
        ax.axhline(0.55, color="0.25", ls="--", lw=0.9)
        ax.set_xscale("log")
        ax.set_xticks([c * dt for c in centres], [f"{c * dt:g}" for c in centres])
        ax.minorticks_off()
        ax.set_ylim(0.44, 0.72)
        n = r["n_pairs"]
        ax.set_ylabel(f"lab {s} · accuracy at one scale\n({n:,} window pairs)")
        ax.set_xlabel("centre width of tube's centre-surround kernel (s)")
        ax.text(0.02, 0.97, "AB"[i] if i == 0 else "C", transform=ax.transAxes, fontsize=12,
                fontweight="bold", va="top")
        # Right: all scales pooled, with the twin contrasts.
        rows = []
        for J in Js[s]:
            rr = next(x for x in R if x["stream"] == s and x["J_sec"] == J and x["kind"] == "real")
            tw = next(x for x in R if x["stream"] == s and x["J_sec"] == J and x["kind"] == "twin")
            rows.append((J, rr["real_vs_rigid_shift"]["all"], rr["real_vs_shared_offset"]["all"],
                         tw["unplanted_vs_rigid_shift"]["all"], tw["planted_vs_rigid_shift"]["all"]))
        x = np.arange(len(rows))
        specs = [(1, "#1f4e79", "o", -0.24), (2, "#c07a12", "o", -0.08),
                 (3, "0.45", "s", 0.08), (4, "#2e7d32", "D", 0.24)]
        for col, c, m, dx in specs:
            pts = [q[col] for q in rows]
            bx.vlines(x + dx, [p["p1_67"] for p in pts], [p["p98_33"] for p in pts], color=c, lw=1.8)
            bx.plot(x + dx, [p["accuracy"] for p in pts], m, color=c, ms=5)
        bx.axhline(0.5, color="0.55", ls=":", lw=0.9)
        bx.axhline(0.55, color="0.25", ls="--", lw=0.9)
        bx.set_xticks(x, [f"{q[0]:g}" for q in rows])
        bx.set_ylim(0.35, 1.0)
        bx.set_xlabel("displacement J (s)")
        bx.set_ylabel("accuracy, all scales pooled")
        bx.text(0.03, 0.97, "B" if i == 0 else "D", transform=bx.transAxes, fontsize=12,
                fontweight="bold", va="top")
    axes[0][0].texts[0].set_text("A")
    handles = [Line2D([], [], color="#1f4e79", marker="o", label="real vs rigid shift (lighter = smaller J)"),
               Line2D([], [], color="#c07a12", marker="o", label="real vs shared offset: must be chance"),
               Line2D([], [], color="0.45", marker="s", ls="", label="unplanted twin vs its rigid shift: must be chance"),
               Line2D([], [], color="#2e7d32", marker="D", ls="", label="planted twin vs its rigid shift: must separate"),
               Line2D([], [], color="0.55", ls=":", label="chance, 0.5"),
               Line2D([], [], color="0.25", ls="--", label="0.55 reference"),
               Line2D([], [], color="0.3", lw=1.8, label="bar: 1.67–98.33 percentile, refitting bootstrap")]
    fig.legend(handles=handles, loc="upper center", ncol=3, frameon=False, fontsize=9)
    fig.tight_layout(rect=(0, 0, 1, 0.9))
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    p = out / "tube_aggregate_fig.png"
    fig.savefig(p, dpi=150)
    print(p)


if __name__ == "__main__":
    main()
