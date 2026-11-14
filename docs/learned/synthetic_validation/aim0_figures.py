"""Figures 2-4 for Aim 0: predictions against simulation.

Figure 2: the coordination-rates tool's estimates, predicted against measured, one point per
condition and window (its chance-cluster panels are now the chapter's Figure 1.9).
Figure 3: assembled against random participation as the number of assemblies grows.
Figure 4: the order indicator against its closed forms and fits.
Reads theory_check.json, membership_limit.json and order_limit.json beside this file (run
theory.py, membership_limit.py and order_limit.py first). Captions are on the goal page.

    PYTHONPATH=src python docs/learned/synthetic_validation/aim0_figures.py [--out DIR] [--no-repo]
"""
from __future__ import annotations

import argparse
import json
from datetime import datetime
import sys
from pathlib import Path

import matplotlib
import matplotlib.ticker

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
    ax.text(-0.02, 1.03, c, transform=ax.transAxes, fontsize=15, fontweight="bold",
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
        fig.savefig(d / fname, dpi=130, metadata={
            "Title": title, "Author": META,
            "Creation Time": datetime.now().isoformat(timespec="seconds")})
        print(d / fname)
    plt.close(fig)


def fig2(dests):
    """Predicted against measured for the coordination-rates tool, 2 x 3. The chance-cluster
    panels that were D and H are the chapter's Figure 1.9 (ch1_new_figures.py, chance) and were
    dropped here (chapter review round 3, role 9 F7)."""
    tc = json.loads((HERE / "theory_check.json").read_text())
    cr = tc["coord_rates"]
    quant = [("k", "participants per event"), ("lam", "coordinated events per min"),
             ("share", "coordinated onset rate per cell")]
    lim = (0.15, 2.6)
    fig, axes = plt.subplots(2, 3, figsize=(11, 7.6))
    L = "ABCDEF"
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
            style(ax); letter(ax, L[i * 3 + j])
            off = [r for r in rows if np.isfinite(r["meas"][q]) and not (lim[0] <= r["meas"][q] <= lim[1])]
            if off:
                ks = sorted({r["k"] for r in off})
                hi_n = sum(r["meas"][q] > lim[1] for r in off)
                where = ",\n".join(x for x in (f"{hi_n} above" if hi_n else "",
                                               f"{len(off) - hi_n} below" if len(off) - hi_n else "") if x)
                # narrow, in the empty lower-right corner (below the identity line, right of x = 1.4)
                ax.text(0.98, 0.02, f"{len(off)} off scale:\n{where}\n({', '.join(str(x) for x in ks)}-cell)",
                        transform=ax.transAxes, ha="right", va="bottom", fontsize=10.5, color="#444")
        fig.text(0.012, 0.71 - 0.43 * i, f"background {bg:g} Hz per cell", rotation=90,
                 fontsize=12, va="center")
    handles = [Line2D([], [], color=c, marker=m, ls="none", ms=7,
                      label=f"measured, placed at the hard-core prediction, {kk} cells per event")
               for kk, (c, m) in K_STYLE.items()]
    handles += [Line2D([], [], color=GREY, marker="o", ls="none", ms=5,
                       label="same measurements, placed at the Poisson-train prediction"),
                Line2D([], [], color="#888", ls=":", label="prediction = measurement")]
    fig.legend(handles=handles, loc="upper center", ncol=2, frameon=False, fontsize=10.5)
    fig.tight_layout(rect=(0.03, 0, 1, 0.86))
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
    ax.set_ylabel("pair co-participation variance\n÷ random")
    style(ax); letter(ax, "A")
    ax.legend(frameon=False, fontsize=11, loc="upper left")
    ax = axes[1]
    both = [100 * r["verdicts"]["structure-beyond-rate"] / r["n"] for r in rows]
    ax.plot(reuse, both, "-o", color="#6250d6", ms=7, label="both nulls reject")
    ax.plot(reuse, [100 * r["flagged"] for r in rows], "--s", color="#6250d6", ms=5, mfc="white",
            lw=1.2, label="either null rejects")
    rb = 100 * m["random_verdicts"]["structure-beyond-rate"] / m["reps_verdict"]
    re_ = 100 * m["random_flagged"]
    ax.axhline(re_, color="#888", ls="--", lw=0.8, label=f"random participation, either ({re_:.0f} %)")
    ax.axhline(rb, color="#888", ls=":", lw=1, label=f"random participation, both ({rb:.0f} %)")
    ax.text(0.62, 0.62, f"at M = 1\n(E/M = {m['E']}):\nuniform null\nonly",
            transform=ax.transAxes, ha="left", va="top", fontsize=11, color="#444")
    ax.legend(frameon=False, fontsize=11, loc="upper center", bbox_to_anchor=(0.5, -0.16), ncol=2)
    ax.set_xscale("log"); ax.set_xlim(*xl); ax.set_ylim(-4, 105)
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
    fig, axes = plt.subplots(1, 3, figsize=(13, 6.4))
    ax = axes[0]
    rr = np.geomspace(0.1, 10, 200)
    c200 = [r for r in o["none"] if r["E"] == 200][0]["c_score"]
    f0_200 = c200 / np.sqrt(ol.nbar(N, k, 200))
    ax.plot(rr, ol.pred_one(rr), color=PRED, lw=2, label="signal (2/π) arctan r")
    ax.plot(rr, np.hypot(ol.pred_one(rr), f0_200), color=PRED, lw=1.5, ls="--",
            label="with no-order bias")
    ax.plot([r["r"] for r in o["one"]], [r["measured"] for r in o["one"]], "o", color=SIM, ms=7,
            label="simulated")
    ax.set_xscale("log"); ax.set_yscale("log"); ax.set_ylim(0.04, 1.1)
    ax.set_yticks([0.05, 0.1, 0.2, 0.4, 0.8]); plain_log(ax, "y")
    ax.set_xlabel("r = template spread ÷ jitter"); ax.set_ylabel("order indicator F")
    style(ax); letter(ax, "A")
    ax.legend(frameon=False, fontsize=12, loc="upper center", bbox_to_anchor=(0.45, -0.2))
    ax = axes[1]
    f0 = o["many"][0]["F_0"]
    MM = np.geomspace(2, 300, 200)
    ax.plot(MM, ol.pred_many(2.5, MM), "-", color=PRED, lw=2,
            label="signal $F_M$, M ≥ 2")
    ax.plot(MM, np.hypot(ol.pred_many(2.5, MM), f0), "--", color=PRED, lw=1.5,
            label="with bias $F_0$")
    ax.plot([1], [o["many"][0]["predicted"]], "D", color=PRED, ms=7, mfc="white",
            label="M = 1 closed form")
    ax.plot([r["M"] for r in o["many"]], [r["measured"] for r in o["many"]], "o", color=SIM, ms=7,
            label="simulated")
    ax.set_xscale("log"); ax.set_yscale("log"); ax.set_ylim(0.04, 1.1)
    ax.set_yticks([0.05, 0.1, 0.2, 0.4, 0.8]); plain_log(ax, "y")
    ax.set_xlabel("latency templates M (r = 2.5, 2000 events)"); ax.set_ylabel("order indicator F")
    style(ax); letter(ax, "B")
    ax.legend(frameon=False, fontsize=12, loc="upper center", bbox_to_anchor=(0.45, -0.2))
    ax = axes[2]
    # Score sort: derived, nothing fitted (kendall_w/derivation.md). The exact finite-n̄ mean is the
    # lattice convolution kendall_w.F_exact over integer event counts E; the asymptote is c(N,k)/√n̄,
    # c = √(4(k+1)/(3πN)). Same color (PRED) as the closed forms in A and B.
    sys.path.insert(0, str(HERE / "kendall_w"))
    import kendall_w as kw
    EE = np.unique(np.round(np.geomspace(3, 1000, 80)).astype(int))
    nbE = np.array([ol.nbar(N, k, E) for E in EE])
    cN = kw.c_score(N, k)
    nb_axis = np.geomspace(0.25, 90, 200)
    ax.plot(nbE, [kw.F_exact(N, k, int(E)) for E in EE], "-", color=PRED, lw=2,
            label="derived exact mean, score sort")
    ax.plot(nb_axis, cN / np.sqrt(nb_axis), ":", color=PRED, lw=1.8,
            label=f"derived asymptote {cN:.3f} / √n̄")
    nb = np.array([r["n_bar"] for r in o["none"]])
    # The record order_limit.json starts at n̄ = 2.1; the two points below it are the separate
    # 200-recording check in kendall_w/kendall_w_output.txt, section C (E = 5 and 10 events).
    lowC = []
    txt = (HERE / "kendall_w" / "kendall_w_output.txt").read_text(encoding="utf-8").splitlines()
    i0 = next(i for i, l in enumerate(txt) if l.startswith("C. 33 cells, 10 per event"))
    for l in txt[i0 + 2:]:
        f = l.replace("|", " ").split()
        if len(f) < 8 or not f[0].isdigit():
            break
        if float(f[1]) < 2:
            lowC.append((float(f[1]), float(f[3]), float(f[6])))   # n̄, F√n̄ score, F√n̄ search
    lowC = np.array(lowC)
    for j, (key, col, mk, lab) in enumerate((("c_score", SIM, "o", "score sort"),
                                             ("c_search", SEARCH, "s", "local search"))):
        c = np.array([r[key] for r in o["none"]])
        ax.plot(nb, c / np.sqrt(nb), mk, color=col, ms=7, label=f"simulated, {lab}")
        if len(lowC):
            ax.plot(lowC[:, 0], lowC[:, 1 + j] / np.sqrt(lowC[:, 0]), mk, color=col, ms=7,
                    mfc="white", mew=1.5)
        if key == "c_search":
            ax.plot(nb_axis, np.mean(c) / np.sqrt(nb_axis), "-", color=col, lw=1.5,
                    label=f"fitted {np.mean(c):.2f} / √n̄, local search")
    if len(lowC):
        ax.plot([], [], "o", color="#444", mfc="white", mew=1.5, ms=7,
                label="open: separate check, 200 recordings")
    ax.set_xscale("log"); ax.set_yscale("log"); ax.set_ylim(0.04, 1.1); ax.set_xlim(0.25, 90)
    ax.set_xticks([0.3, 1, 3, 10, 30]); ax.set_yticks([0.05, 0.1, 0.2, 0.4, 0.8]); plain_log(ax)
    ax.set_xlabel("events a pair of cells shares, n̄"); ax.set_ylabel("order indicator F, no order")
    style(ax); letter(ax, "C")
    ax.legend(frameon=False, fontsize=12, loc="upper center", bbox_to_anchor=(0.45, -0.2), ncol=1)
    for a_ in axes:
        a_.xaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda v, _: f"{v:g}"))
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
