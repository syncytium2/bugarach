#!/usr/bin/env python3
"""Draw Stage 2 of the tube plan: planted-truth F1 by arm, and the paired leak checks.

    python tools/make_tube_ssl_figure.py --run <folder> --out <folder>

Reads ``results.jsonl`` from ``tools/tube_self_supervised.py``; writes ``tube_ssl_fig.png``.
A fit that fires nothing on the held-out fold is drawn at F1 0 and counted as silent.
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

ARMS = [("supervised", None, "supervised"),
        ("untrained", None, "untrained"),
        ("ssl_sim", 10.0, "sim\n10 s"),
        ("ssl_sim", 20.0, "sim\n20 s"),
        ("ssl_real", 10.0, "real\n10 s"),
        ("ssl_real", 20.0, "real\n20 s")]
"""The last four arms are trained against rigid shift with no labels, on simulated (sim) or real
lab recordings, at each displacement."""
MODELS = {"tube": ("#4d4d4d", -0.27), "tube_guard": ("#8c8c8c", -0.09),
          "line": ("#1f4e79", 0.09), "line_length": ("#7b3294", 0.27)}
"""Every architecture in the results file gets a row, and the two `line` builds are inked while
the tube family is grey — the figure showed only the tube family until 2026-09-16, when four
reviewers found it plotting two architectures under a caption that said four."""


def f1(v):
    x = v["f1"]
    return 0.0 if x is None or not np.isfinite(x) else float(x)


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", required=True)
    ap.add_argument("--out", required=True)  # noqa: E501
    a = ap.parse_args(argv)
    R = [json.loads(line) for line in open(Path(a.run) / "results.jsonl")]
    fig, axes = plt.subplots(1, 3, figsize=(11.5, 4.6), gridspec_kw={"width_ratios": [1.5, 1.5, 1]})
    rs = np.random.RandomState(0)
    for ax, key, letter, title in ((axes[0], "oracle", "A", "oracle threshold (reads planted truth)"),
                                   (axes[1], "label_free_2", "B",
                                    "label-free threshold (≤ 2 events per 10 min on rigid shift)")):
        for i, (arm, J, _) in enumerate(ARMS):
            for m, (c, dx) in MODELS.items():
                vals = [f1(r["scores"][key]) for r in R if r["arm"] == arm and r["model"] == m
                        and (J is None or r["J_sec"] == J)]
                x = i + dx + rs.uniform(-0.035, 0.035, len(vals))
                ax.plot(x, vals, "o", color=c, ms=3.5, alpha=0.45)
                ax.plot([i + dx - 0.07, i + dx + 0.07], [np.mean(vals)] * 2, color=c, lw=2.5)
        # The untrained arm is not a baseline: at the oracle threshold its detections are tens of
        # seconds wide and cover 95-99 % of the recording, so it "hits" planted events by being on
        # almost everywhere. Marked rather than dropped, so the absence is visible.
        u = [i for i, (arm, _, _) in enumerate(ARMS) if arm == "untrained"]
        for i in u:
            ax.axvspan(i - 0.42, i + 0.42, color="#c0392b", alpha=0.07, zorder=0)
        if u and key == "oracle":
            ax.annotate("covers 95–99 % of\nthe recording", (u[0], 0.86), ha="center",
                        fontsize=7.5, color="#c0392b")
        ax.set_xticks(range(len(ARMS)), [lab for _, _, lab in ARMS], fontsize=8)
        ax.set_xlabel("training arm (the last four read no labels)", fontsize=8.5)
        ax.set_ylim(-0.03, 0.9)
        ax.set_ylabel(f"planted-truth F1, held-out fold\n{title}")
        ax.text(0.02, 0.97, letter, transform=ax.transAxes, fontsize=12, fontweight="bold", va="top")
    bx = axes[2]
    checks = [("real_vs_shared_offset", "real vs\nshared\noffset"),
              ("unplanted_twin_vs_rigid_shift", "twin vs\nrigid\nshift"),
              ("real_vs_rigid_shift", "real vs\nrigid\nshift")]
    for i, (k, _) in enumerate(checks):
        for m, (c, dx) in MODELS.items():
            vals = [r["checks"][k]["share_real_higher"] for r in R
                    if r["arm"] == "ssl_real" and r["model"] == m]
            x = i + dx + rs.uniform(-0.035, 0.035, len(vals))
            bx.plot(x, vals, "o", color=c, ms=3.5, alpha=0.45)
            bx.plot([i + dx - 0.07, i + dx + 0.07], [np.mean(vals)] * 2, color=c, lw=2.5)
    bx.axhline(0.5, color="0.55", ls=":", lw=0.9)
    bx.set_xticks(range(len(checks)), [lab for _, lab in checks], fontsize=8)
    bx.set_xlabel("paired check (the first two must read 0.5)", fontsize=8.5)
    bx.set_ylim(0.2, 1.0)
    bx.set_ylabel("share of held-out crops where real scores higher\n(self-supervised on real lab, both J)")
    bx.text(0.03, 0.97, "C", transform=bx.transAxes, fontsize=12, fontweight="bold", va="top")
    handles = [Line2D([], [], color=c, marker="o", ls="", label=m) for m, (c, _) in MODELS.items()]
    handles += [Line2D([], [], color="0.3", lw=2.5, label="bar: mean over 4 folds × 3 training seeds"),
                Line2D([], [], color="0.3", marker="o", ls="", alpha=0.45,
                       label="dot: one fit (a fit with no true positive scores 0)"),
                Line2D([], [], color="#c0392b", lw=6, alpha=0.2,
                       label="shaded: not a baseline — see the caption"),
                Line2D([], [], color="0.55", ls=":", label="chance, 0.5 (panel C)")]
    fig.legend(handles=handles, loc="upper center", ncol=4, frameon=False, fontsize=8.5)
    fig.tight_layout(rect=(0, 0, 1, 0.89))
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    p = out / "tube_ssl_fig.png"
    fig.savefig(p, dpi=150)
    print(p)


if __name__ == "__main__":
    main()
