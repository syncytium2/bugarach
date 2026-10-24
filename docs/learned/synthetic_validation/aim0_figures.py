"""Figures 2-4 for Aim 0: predictions against simulation.

Figure 2: the coordination-rates tool's estimates, predicted against measured, one point per
condition, and the assessor's chance clusters on background-only recordings.
Figure 3: assembled against random participation as the number of assemblies grows.
Figure 4: the order indicator against its closed forms.
Reads theory_check.json, membership_limit.json and order_limit.json beside this file (run
theory.py, membership_limit.py and order_limit.py first). Captions are on the goal page.

    PYTHONPATH=src python docs/learned/synthetic_validation/aim0_figures.py [--out DIR] [--no-repo]
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "tools"))

K_COL = {5: "#eda100", 10: "#2a78d6", 20: "#1baf7a"}   # participants per event
GREY = "#9a9a9a"
META = "bugarach synthetic validation (docs/learned/synthetic_validation)"


def style(ax):
    for sp in ("top", "right"):
        ax.spines[sp].set_visible(False)
    ax.grid(True, color="#e5e5e5", lw=0.6)


def letter(ax, c):
    """Panel letter outside the plot area, above its top-left corner, clear of the data."""
    ax.text(-0.02, 1.04, c, transform=ax.transAxes, fontsize=12, fontweight="bold",
            va="bottom", ha="right")


def plain_log(ax, axis="both"):
    from matplotlib.ticker import NullFormatter, ScalarFormatter
    for a_ in ((ax.xaxis, ax.yaxis) if axis == "both" else ((ax.xaxis,) if axis == "x" else (ax.yaxis,))):
        f = ScalarFormatter(); f.set_scientific(False)
        a_.set_major_formatter(f); a_.set_minor_formatter(NullFormatter())


def name(topic, type_="recovery"):
    from naming import artifact_name
    return artifact_name.build(artifact_name.load_codes(), source="synth", type=type_,
                               form="plot", topic=topic, ext="png", date="20261023")


def save(fig, fname, title, dests):
    for d in dests:
        fig.savefig(d / fname, dpi=130, metadata={"Title": title, "Author": META})
        print(d / fname)
    plt.close(fig)


def fig2(dests):
    tc = json.loads((HERE / "theory_check.json").read_text())
    cr = tc["coord_rates"]
    quant = [("k", "participants per event"), ("lam", "coordinated events per min"),
             ("share", "coordinated share of onsets")]
    fig, axes = plt.subplots(2, 4, figsize=(15, 7.6))
    L = "ABCDEFGH"
    for i, bg in enumerate((0.01, 0.05)):
        rows = [r for r in cr if r["bg"] == bg]
        for j, (q, lab) in enumerate(quant):
            ax = axes[i, j]
            ax.plot([0, 3], [0, 3], color="#888", ls="--", lw=1, zorder=0)
            px = [r["poisson"][q] for r in rows]; my = [r["meas"][q] for r in rows]
            ax.scatter(px, my, s=14, color=GREY, alpha=0.7, zorder=1,
                       label="Poisson event train (no at-most-one-event term)" if (i, j) == (0, 0) else None)
            for kk, col in K_COL.items():
                rr = [r for r in rows if r["k"] == kk]
                ax.scatter([r["exact"][q] for r in rr], [r["meas"][q] for r in rr], s=26,
                           color=col, edgecolor="white", lw=0.5, zorder=2,
                           label=f"exact prediction, {kk} cells per event" if (i, j) == (0, 0) else None)
            ax.set_xlim(0.2, 2.6); ax.set_ylim(0.2, 2.6)
            ax.set_xlabel("predicted ÷ planted")
            ax.set_ylabel(lab + "\nmeasured ÷ planted")
            style(ax); letter(ax, L[i * 4 + j])
            off = sum(1 for v in my if np.isfinite(v) and (v > 2.6 or v < 0.2))
            if off:
                ax.text(0.98, 0.03, f"{off} conditions off scale", transform=ax.transAxes,
                        ha="right", fontsize=8.5, color="#555")
        ax = axes[i, 3]
        ch = [c for c in tc["chance"] if c["bg"] == bg]
        lo = 1e-3
        ax.plot([lo, 20], [lo, 20], color="#888", ls="--", lw=1, zorder=0)
        zero = [c for c in ch if c["predicted"] < lo and c["measured_median"] < lo]
        if zero:
            ax.text(0.97, 0.05, ", ".join(f"K = {c['K']}" for c in zero) +
                    ": none predicted, none measured", transform=ax.transAxes, ha="right",
                    fontsize=9, color="#333")
        for c in [c for c in ch if c not in zero]:
            x = max(c["predicted"], lo); y = max(c["measured_median"], lo)
            ax.errorbar(x, y, yerr=[[max(y - max(c["measured_q"][0], lo), 0)],
                                    [max(c["measured_q"][2], lo) - y]],
                        fmt="o", color="#6250d6", ms=7, capsize=3, zorder=2)
            ax.annotate(f"K = {c['K']}", (x, y), textcoords="offset points", xytext=(8, -4),
                        fontsize=9, color="#333")
        ax.set_xscale("log"); ax.set_yscale("log"); ax.set_xlim(lo, 20); ax.set_ylim(lo, 20)
        ax.set_xlabel("predicted (per min)")
        ax.set_ylabel("chance clusters, background only\nmeasured (per min)")
        style(ax); letter(ax, L[i * 4 + 3])
        fig.text(0.004, 0.72 - 0.45 * i, f"background {bg:g} Hz per cell", rotation=90,
                 fontsize=11, va="center")
    fig.legend(loc="upper center", ncol=4, frameon=False, fontsize=9.5)
    fig.tight_layout(rect=(0.02, 0, 1, 0.93))
    save(fig, name("one source predicted against measured"),
         "Figure 2. Aim 0 predictions against Aim 1a, per condition", dests)


def fig3(dests):
    m = json.loads((HERE / "membership_limit.json").read_text())
    rows = m["rows"]
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.4))
    ax = axes[0]
    reuse = np.array([r["reuse"] for r in rows]); x = np.maximum(reuse, 1e-4)
    xx = np.geomspace(1e-4, 60, 200)
    ax.plot(xx, 1 + (m["E"] - 1) * xx / m["E"], color="#2a78d6", lw=2, label="predicted 1 + (E − 1)/M")
    ax.plot(x, [r["measured"] for r in rows], "o", color="#eb6834", ms=7, label="simulated (mean of 400)")
    ax.axhspan(1, m["random_p95"], color="#e5e5e5", zorder=0, label="random participation, 95 % range")
    ax.set_xscale("log"); ax.set_yscale("log")
    ax.set_xlabel("reuse: events per assembly, E/M")
    ax.set_ylabel("pair-count variance ÷ random")
    style(ax); letter(ax, "A"); ax.legend(frameon=False, fontsize=9, loc="upper left", bbox_to_anchor=(0.06, 1))
    ax = axes[1]
    ax.plot(x, [100 * r["detected"] for r in rows], "-o", color="#6250d6", ms=7)
    ax.axhline(5, color="#888", ls="--", lw=1)
    ax.text(2.0, 8, "5 % by chance", fontsize=9, color="#555")
    ax.set_xscale("log"); ax.set_ylim(0, 105)
    ax.set_xlabel("reuse: events per assembly, E/M")
    ax.set_ylabel("recordings detected (%)")
    style(ax); letter(ax, "B")
    fig.tight_layout()
    save(fig, name("assemblies converge to random", "assembly-membership"),
         "Figure 3. Assembled against random participation", dests)


def fig4(dests):
    o = json.loads((HERE / "order_limit.json").read_text())
    fig, axes = plt.subplots(1, 3, figsize=(15, 4.6))
    ax = axes[0]
    tt = np.geomspace(0.1, 10, 200)
    ax.plot(tt, 2 / np.pi * np.arctan(tt), color="#2a78d6", lw=2, label="(2/π) arctan τ")
    ax.plot([r["tau"] for r in o["one"]], [r["measured"] for r in o["one"]], "o", color="#eb6834",
            ms=7, label="simulated, score sort")
    ax.set_xscale("log"); ax.set_ylim(0, 1)
    ax.set_xlabel("τ = template spread ÷ jitter"); ax.set_ylabel("order indicator F")
    style(ax); letter(ax, "A"); ax.legend(frameon=False, fontsize=9, loc="upper left", bbox_to_anchor=(0.06, 1))
    ax = axes[1]
    Ms = np.array([r["M"] for r in o["many"]])
    ax.plot(Ms, [r["predicted"] for r in o["many"]], "-", color="#2a78d6", lw=2,
            label="predicted √(F_M² + F_0²)")
    ax.plot(Ms, [r["F_M"] for r in o["many"]], ":", color="#2a78d6", lw=1.5, label="signal term F_M alone")
    ax.plot(Ms, [r["measured"] for r in o["many"]], "o", color="#eb6834", ms=7, label="simulated, score sort")
    ax.set_xscale("log"); ax.set_yscale("log")
    ax.set_xlabel("latency templates M (τ = 2.5)"); ax.set_ylabel("order indicator F")
    ax.set_yticks([0.05, 0.1, 0.2, 0.4, 0.8]); plain_log(ax, "y")
    style(ax); letter(ax, "B"); ax.legend(frameon=False, fontsize=9, loc="lower left")
    ax = axes[2]
    nb = np.array([r["n_bar"] for r in o["none"]])
    for key, col, lab in (("c_score", "#eb6834", "score sort"), ("c_search", "#e34948", "local search")):
        c = np.array([r[key] for r in o["none"]])
        ax.plot(nb, c / np.sqrt(nb), "o", color=col, ms=7, label=f"simulated, {lab}")
        ax.plot(nb, np.mean(c) / np.sqrt(nb), "-", color=col, lw=1.5,
                label=f"fitted {np.mean(c):.2f} / √n̄")
    ax.set_xscale("log"); ax.set_yscale("log")
    ax.set_xlabel("events a pair of cells shares, n̄"); ax.set_ylabel("order indicator F, no order planted")
    ax.set_xticks([2, 5, 10, 20, 50]); ax.set_yticks([0.05, 0.1, 0.2, 0.3]); plain_log(ax)
    style(ax); letter(ax, "C"); ax.legend(frameon=False, fontsize=9, loc="lower left")
    fig.tight_layout()
    save(fig, name("order indicator closed forms"),
         "Figure 4. The order indicator against its closed forms", dests)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, default=None)
    ap.add_argument("--no-repo", action="store_true")
    a = ap.parse_args()
    if a.out is None:
        from bugarach.paths import darkroom
        a.out = darkroom() / "2026-10-23-synthetic-validation"
    a.out.mkdir(parents=True, exist_ok=True)
    dests = [a.out] + ([] if a.no_repo else [HERE])
    fig2(dests); fig3(dests); fig4(dests)


if __name__ == "__main__":
    main()
