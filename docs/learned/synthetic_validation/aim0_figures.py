"""Figures 2-4 for Aim 0: predictions against simulation.

Figure 2: the coordination-rates tool's estimates, predicted against measured, one point per
condition and window, and the assessor's chance clusters on background-only recordings.
Figure 3: assembled against random participation as the number of assemblies grows.
Figure 4: the order indicator against its closed forms and fits.
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
from matplotlib.lines import Line2D
import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "tools"))
sys.path.insert(0, str(HERE))

plt.rcParams.update({"font.size": 12})
# Participants per event: one hue, light to dark (ordinal), distinct from Figure 1's series.
K_STYLE = {5: ("#86b6ef", "v"), 10: ("#2a78d6", "o"), 20: ("#0d366b", "s")}
GREY = "#9a9a9a"
PRED = "#2a78d6"       # a prediction curve, in Figures 3 and 4
SIM = "#eb6834"        # simulation points under the score sort, in Figures 3 and 4
SEARCH = "#555555"     # simulation points under the local search, Figure 4
META = "bugarach synthetic validation (docs/learned/synthetic_validation)"


def style(ax):
    for sp in ("top", "right"):
        ax.spines[sp].set_visible(False)
    ax.grid(True, color="#e5e5e5", lw=0.6)


def letter(ax, c):
    """Panel letter outside the plot area, above its top-left corner, as in Figure 1."""
    ax.text(-0.02, 1.03, c, transform=ax.transAxes, fontsize=13, fontweight="bold",
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
        fig.savefig(d / fname, dpi=130, metadata={"Title": title, "Author": META,
                                                  "Creation Time": "2026-10-23"})
        print(d / fname)
    plt.close(fig)


def fig2(dests):
    tc = json.loads((HERE / "theory_check.json").read_text())
    cr = tc["coord_rates"]
    quant = [("k", "participants per event"), ("lam", "coordinated events per min"),
             ("share", "coordinated share of onsets")]
    lim = (0.2, 2.6)
    fig, axes = plt.subplots(2, 4, figsize=(13, 7.4))
    L = "ABCDEFGH"
    for i, bg in enumerate((0.01, 0.05)):
        rows = [r for r in cr if r["bg"] == bg]
        for j, (q, lab) in enumerate(quant):
            ax = axes[i, j]
            ax.plot(lim, lim, color="#888", ls=":", lw=1, zorder=0)
            ax.scatter([r["poisson"][q] for r in rows], [r["meas"][q] for r in rows], s=14,
                       color=GREY, alpha=0.7, zorder=1)
            for kk, (col, mk) in K_STYLE.items():
                rr = [r for r in rows if r["k"] == kk]
                ax.scatter([r["exact"][q] for r in rr], [r["meas"][q] for r in rr], s=30,
                           color=col, marker=mk, edgecolor="white", lw=0.5, zorder=2)
            ax.set_xlim(*lim); ax.set_ylim(*lim)
            ax.set_xlabel("predicted ÷ planted")
            ax.set_ylabel(lab + "\nmeasured ÷ planted", fontsize=11)
            style(ax); letter(ax, L[i * 4 + j])
            off = [r for r in rows if np.isfinite(r["meas"][q]) and not (lim[0] <= r["meas"][q] <= lim[1])]
            if off:
                ks = sorted({r["k"] for r in off})
                ax.text(0.03, 0.97, f"{len(off)} off scale\n({', '.join(str(x) for x in ks)}-cell events)",
                        transform=ax.transAxes, ha="left", va="top", fontsize=10, color="#444")
        ax = axes[i, 3]
        ch = [c for c in tc["chance"] if c["bg"] == bg]
        lo_ax, hi_ax = 1e-3, 20
        ax.plot([lo_ax, hi_ax], [lo_ax, hi_ax], color="#888", ls=":", lw=1, zorder=0)
        tiny = [c for c in ch if c["predicted"] < lo_ax and c["pooled_rate"] < lo_ax]
        if tiny:
            ax.text(0.03, 0.95, "\n".join(f"K = {c['K']}: {c['predicted']:.0e}/min predicted,\n"
                                          f"{c['pooled_count']} clusters measured" for c in tiny),
                    transform=ax.transAxes, ha="left", va="top", fontsize=10, color="#333")
        for c in [c for c in ch if c not in tiny]:
            x, y = c["predicted"], c["pooled_rate"]
            ax.errorbar(x, y, yerr=[[y - c["pooled_rate_ci"][0]], [c["pooled_rate_ci"][1] - y]],
                        fmt="o", color="#6250d6", ms=7, capsize=3, zorder=2)
            ax.annotate(f"K = {c['K']}", (x, y), textcoords="offset points", xytext=(-10, 8),
                        ha="right", fontsize=10, color="#333")
        ax.set_xscale("log"); ax.set_yscale("log"); ax.set_xlim(lo_ax, hi_ax); ax.set_ylim(lo_ax, hi_ax)
        ax.set_xlabel("predicted (per min)")
        ax.set_ylabel("chance clusters, background only\nmeasured (per min)", fontsize=11)
        style(ax); letter(ax, L[i * 4 + 3])
        fig.text(0.005, 0.71 - 0.43 * i, f"background {bg:g} Hz per cell", rotation=90,
                 fontsize=12, va="center")
    handles = [Line2D([], [], color=c, marker=m, ls="none", ms=7,
                      label=f"full prediction, {kk} cells per event") for kk, (c, m) in K_STYLE.items()]
    handles += [Line2D([], [], color=GREY, marker="o", ls="none", ms=5,
                       label="Poisson events (no at-most-one-event term)"),
                Line2D([], [], color="#888", ls=":", label="prediction = measurement"),
                Line2D([], [], color="#6250d6", marker="o", ls="-", ms=7,
                       label="chance clusters: pooled rate, 95 % interval")]
    fig.legend(handles=handles, loc="upper center", ncol=3, frameon=False, fontsize=10.5)
    fig.tight_layout(rect=(0.02, 0, 1, 0.88))
    save(fig, name("one source predicted against measured"),
         "Figure 2, predicted against measured (Aim 0)", dests)


def fig3(dests):
    m = json.loads((HERE / "membership_limit.json").read_text())
    rows = m["rows"]
    reuse = np.array([r["reuse"] for r in rows])
    xl = (2e-3, 100)
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.6))
    ax = axes[0]
    xx = np.geomspace(*xl, 200)
    ax.plot(xx, 1 + (m["E"] - 1) * xx / m["E"], color=PRED, lw=2, label="predicted 1 + (E − 1)/M")
    ax.plot(reuse, [r["measured"] for r in rows], "o", color=SIM, ms=7,
            label=f"simulated (mean of {m['reps_mean']})")
    ax.set_xscale("log"); ax.set_yscale("log"); ax.set_xlim(*xl)
    ax.set_xlabel("reuse: events per assembly, E/M")
    ax.set_ylabel("pair-count variance ÷ random")
    style(ax); letter(ax, "A")
    ax.legend(frameon=False, fontsize=10.5, loc="upper left")
    ax = axes[1]
    ax.plot(reuse, [100 * r["flagged"] for r in rows], "-o", color="#6250d6", ms=7,
            label="flagged by the assembly verdict")
    ax.axhline(100 * m["random_flagged"], color="#888", ls=":", lw=1)
    ax.text(3e-3, 100 * m["random_flagged"] + 3,
            f"{100 * m['random_flagged']:.0f} % flagged under random participation", fontsize=10,
            color="#444")
    ax.text(0.97, 0.55, "at M = 1 every recording reads\n'uniform-only' (one saturated assembly)",
            transform=ax.transAxes, ha="right", va="top", fontsize=10, color="#444")
    ax.set_xscale("log"); ax.set_xlim(*xl); ax.set_ylim(0, 105)
    ax.set_xlabel("reuse: events per assembly, E/M")
    ax.set_ylabel(f"recordings flagged (%, of {m['reps_verdict']})")
    style(ax); letter(ax, "B")
    fig.tight_layout()
    save(fig, name("assemblies converge to random", "assembly-membership"),
         "Figure 3, assembled against random participation (Aim 0)", dests)


def fig4(dests):
    import order_limit as ol
    o = json.loads((HERE / "order_limit.json").read_text())
    N, k = o["N"], o["k"]
    fig, axes = plt.subplots(1, 3, figsize=(13, 4.8))
    ax = axes[0]
    rr = np.geomspace(0.1, 10, 200)
    c200 = [r for r in o["none"] if r["E"] == 200][0]["c_score"]
    f0_200 = c200 / np.sqrt(ol.nbar(N, k, 200))
    ax.plot(rr, ol.pred_one(rr), color=PRED, lw=2, label="(2/π) arctan r")
    ax.plot(rr, np.hypot(ol.pred_one(rr), f0_200), color=PRED, lw=1.5, ls="--",
            label="with the no-order bias of 200 events")
    ax.plot([r["r"] for r in o["one"]], [r["measured"] for r in o["one"]], "o", color=SIM, ms=7,
            label="simulated, score sort")
    ax.set_xscale("log"); ax.set_yscale("log"); ax.set_ylim(0.04, 1.1)
    ax.set_yticks([0.05, 0.1, 0.2, 0.4, 0.8]); plain_log(ax, "y")
    ax.set_xlabel("r = template spread ÷ jitter"); ax.set_ylabel("order indicator F")
    style(ax); letter(ax, "A"); ax.legend(frameon=False, fontsize=10, loc="lower right")
    ax = axes[1]
    f0 = o["many"][0]["F_0"]
    MM = np.geomspace(2, 300, 200)
    ax.plot(MM, np.hypot(ol.pred_many(2.5, MM), f0), "-", color=PRED, lw=2,
            label="predicted √(F_M² + F_0²)")
    ax.plot(MM, ol.pred_many(2.5, MM), ":", color=PRED, lw=1.5, label="signal term F_M alone")
    ax.plot([1], [o["many"][0]["predicted"]], "D", color=PRED, ms=7, mfc="white",
            label="M = 1: (2/π) arctan r")
    ax.plot([r["M"] for r in o["many"]], [r["measured"] for r in o["many"]], "o", color=SIM, ms=7,
            label="simulated, score sort")
    ax.set_xscale("log"); ax.set_yscale("log"); ax.set_ylim(0.04, 1.1)
    ax.set_yticks([0.05, 0.1, 0.2, 0.4, 0.8]); plain_log(ax, "y")
    ax.set_xlabel("latency templates M (r = 2.5, 2000 events)"); ax.set_ylabel("order indicator F")
    style(ax); letter(ax, "B"); ax.legend(frameon=False, fontsize=10, loc="lower left")
    ax = axes[2]
    nb = np.array([r["n_bar"] for r in o["none"]])
    for key, col, mk, lab in (("c_score", SIM, "o", "score sort"), ("c_search", SEARCH, "s", "local search")):
        c = np.array([r[key] for r in o["none"]])
        ax.plot(nb, c / np.sqrt(nb), mk, color=col, ms=7, label=f"simulated, {lab}")
        ax.plot(nb, np.mean(c) / np.sqrt(nb), "-", color=col, lw=1.5,
                label=f"fitted {np.mean(c):.2f} / √n̄")
    ax.set_xscale("log"); ax.set_yscale("log"); ax.set_ylim(0.04, 1.1)
    ax.set_xticks([2, 5, 10, 20, 50]); ax.set_yticks([0.05, 0.1, 0.2, 0.4, 0.8]); plain_log(ax)
    ax.set_xlabel("events a pair of cells shares, n̄"); ax.set_ylabel("order indicator F, no order")
    style(ax); letter(ax, "C"); ax.legend(frameon=False, fontsize=10, loc="upper right")
    fig.tight_layout()
    save(fig, name("order indicator closed forms"),
         "Figure 4, an order indicator against its closed forms and fits (Aim 0)", dests)


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
