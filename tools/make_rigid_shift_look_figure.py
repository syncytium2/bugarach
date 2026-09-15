#!/usr/bin/env python3
"""Draw the rigid-shift look: Figure 1 (leak and count) and Figure 2 (destruction).

    python tools/make_rigid_shift_look_figure.py --run <folder>

Reads ``results.json`` and ``meta.json`` written by ``tools/look_rigid_shift.py`` and writes
``fig1_leak_count.png`` and ``fig2_destruction.png`` into the same folder. Exploratory: the
lines at 0.55, ±2 % and 0.25 are the thresholds Tony signed, drawn for reference.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

STREAMS = ("fast", "slow", "events")
INK = {"rigid_shift": "#1f4e79", "uniform_dither": "#b04a2f", "edge_thinning": "#7a7a7a"}
J_STYLE = ("-", "--", ":", "-.", (0, (5, 1, 1, 1)), (0, (1, 3)))


def _fig1(R, out):
    from matplotlib.lines import Line2D
    streams = [s for s in STREAMS if any(r["stream"] == s for r in R["leak"])]
    fig, axes = plt.subplots(len(streams), 2, figsize=(10, 3.8 * len(streams)), squeeze=False)
    for row, stream in enumerate(streams):
        ax = axes[row, 0]
        rows = [r for r in R["leak"] if r["stream"] == stream]
        Js = sorted({r["J_sec"] for r in rows})
        for gen, dx in (("rigid_shift", -0.06), ("uniform_dither", 0.10)):
            for j_i, J in enumerate(Js):
                r = next(x for x in rows if x["generator"] == gen and x["J_sec"] == J)
                x = j_i + dx
                m, s = r["by_mouse"], r["by_slice"]
                ax.plot([x, x], [m["p1_67"], m["p98_33"]], color=INK[gen], lw=2.2)
                ax.plot([x + 0.05, x + 0.05], [s["p1_67"], s["p98_33"]], color=INK[gen],
                        lw=1.0, alpha=0.6)
                ax.plot(x, m["accuracy"], "o", color=INK[gen], ms=5,
                        label=(gen.replace("_", " ") if j_i == 0 else None))
        ax.axhline(0.5, color="0.6", lw=0.8, ls=":")
        ax.axhline(0.55, color="0.3", lw=0.8, ls="--")
        ax.set_xticks(range(len(Js)), [f"{J:g} s" for J in Js])
        n = rows[0]
        ax.set_ylabel(f"{stream} · forced-choice accuracy\n({n['n_pairs']} window pairs, "
                      f"{n['n_mice']} mice, {n['n_slices']} slices)")
        ax.set_xlabel("displacement J")

        ax = axes[row, 1]
        rows = [r for r in R["count"] if r["stream"] == stream]
        rs = sorted([r for r in rows if r["generator"] == "rigid_shift"], key=lambda r: r["J_sec"])
        for j_i, r in enumerate(rs):
            m, s = r["by_mouse"], r["by_slice"]
            ax.plot([j_i, j_i], [100 * m["p1_67"], 100 * m["p98_33"]], color=INK["rigid_shift"], lw=2.2)
            ax.plot([j_i + 0.05] * 2, [100 * s["p1_67"], 100 * s["p98_33"]],
                    color=INK["rigid_shift"], lw=1.0, alpha=0.6)
            ax.plot(j_i, 100 * r["change_share"], "o", color=INK["rigid_shift"], ms=5)
        et = next(r for r in rows if r["generator"] == "edge_thinning")
        x = len(rs)
        ax.plot([x, x], [100 * et["by_mouse"]["p1_67"], 100 * et["by_mouse"]["p98_33"]],
                color=INK["edge_thinning"], lw=2.2)
        ax.plot(x, 100 * et["change_share"], "o", color=INK["edge_thinning"], ms=5)
        ax.axhspan(-2, 2, color="0.9", zorder=0)
        ax.axhline(0, color="0.6", lw=0.8, ls=":")
        ax.set_xticks(range(len(rs) + 1),
                      [f"{r['J_sec']:g} s" for r in rs] + ["edge thinning\n5 s (control)"])
        ax.set_ylabel(f"{stream} · occupied-frame change (%)\n({et['n_slices']} slices)")
        ax.set_xlabel("displacement J")
    # The legend sits above the panels: inside the leak panel it covered the dither bars.
    handles = [Line2D([], [], color=INK["rigid_shift"], marker="o", lw=2.2, label="rigid shift"),
               Line2D([], [], color=INK["uniform_dither"], marker="o", lw=2.2,
                      label="uniform dither (what a leak looks like)"),
               Line2D([], [], color="0.3", lw=2.2, label="thick bar: 1.67–98.33 % over mice"),
               Line2D([], [], color="0.3", lw=1.0, alpha=0.6, label="thin bar: same, over slices")]
    height = fig.get_size_inches()[1]
    fig.legend(handles=handles, frameon=False, fontsize=8, ncol=2, loc="upper center")
    fig.tight_layout(rect=(0, 0, 1, 1 - 0.55 / height))
    p = out / "fig1_leak_count.png"
    fig.savefig(p, dpi=160)
    plt.close(fig)
    return p


def _retained(rows, K, rs, n_boot=2000):
    before = np.array([r["before"][K] for r in rows], float)
    after = np.array([r["after"][K] for r in rows], float)
    point = after.mean() / before.mean() if before.mean() > 0 else np.nan
    idx = rs.randint(len(rows), size=(n_boot, len(rows)))
    b = before[idx].mean(1)
    dist = np.where(b > 0, after[idx].mean(1) / np.where(b > 0, b, 1), np.nan)
    d = dist[np.isfinite(dist)]
    lo, hi = (np.percentile(d, [2.5, 97.5]) if d.size else (np.nan, np.nan))
    return point, lo, hi, float(before.mean())


def _fig2(R, out):
    blocks = sorted({(d["stream"], d["bin_sec"]) for d in R["destruction"]},
                    key=lambda t: (STREAMS.index(t[0]), t[1]))
    parts = sorted({d["participation"] for d in R["destruction"]})
    fig, axes = plt.subplots(len(blocks), len(parts), figsize=(11.5, 3.1 * len(blocks)),
                             sharey=True, squeeze=False)
    rs = np.random.RandomState(20260915)
    table = []
    for i, (stream, bin_sec) in enumerate(blocks):
        for j, p in enumerate(parts):
            ax = axes[i, j]
            d = next(x for x in R["destruction"] if x["stream"] == stream
                     and x["bin_sec"] == bin_sec and x["participation"] == p)
            Ks = sorted(int(k) for k in d["variants"]["homogeneous_resample"][0]["before"])
            rigid = sorted([v for v in d["variants"] if v.startswith("rigid_shift@")],
                           key=lambda v: float(v.split("@")[1]))
            for j_i, v in enumerate(rigid):
                pts = [_retained(d["variants"][v], str(K), rs) for K in Ks]
                ax.errorbar(Ks, [q[0] for q in pts],
                            yerr=[[q[0] - q[1] for q in pts], [q[2] - q[0] for q in pts]],
                            color=INK["rigid_shift"], ls=J_STYLE[j_i], marker="o", ms=4,
                            capsize=2, label=f"rigid shift {float(v.split('@')[1]):g} s")
                for K, q in zip(Ks, pts):
                    table.append((stream, bin_sec, p, v, K, q))
            for ctl, c in (("homogeneous_resample", "0.45"), ("do_nothing", "0.7")):
                pts = [_retained(d["variants"][ctl], str(K), rs) for K in Ks]
                # On top, so a control reading 0 is not hidden under rigid-shift lines at 0.
                ax.plot(Ks, [q[0] for q in pts], color=c, lw=1, marker="s", ms=3, zorder=4,
                        label=ctl.replace("_", " ") + " (control)")
            ax.axhline(0.25, color="0.3", lw=0.8, ls="--")
            ax.set_xticks(Ks)
            if j == 0:
                ax.set_ylabel(f"{stream} · {bin_sec:g} s bin\nretained share of\nplanted coordination")
            ax.set_xlabel(f"K, co-active ROIs (absolute) · participation {p:g}")
            if j == len(parts) - 1:
                ax.legend(frameon=False, fontsize=7, loc="center left", bbox_to_anchor=(1.01, 0.5))
    fig.tight_layout()
    path = out / "fig2_destruction.png"
    fig.savefig(path, dpi=160)
    plt.close(fig)
    return path, table


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", required=True)
    a = ap.parse_args(argv)
    run = Path(a.run)
    R = json.loads((run / "results.json").read_text())
    p1 = _fig1(R, run)
    p2, table = _fig2(R, run)
    (run / "destruction_table.json").write_text(json.dumps(
        [{"stream": s, "bin_sec": b, "participation": p, "variant": v, "K": K,
          "retained": q[0], "ci95": [q[1], q[2]], "before_mean": q[3]}
         for s, b, p, v, K, q in table], indent=2))
    print(p1)
    print(p2)


if __name__ == "__main__":
    main()
