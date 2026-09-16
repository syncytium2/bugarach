#!/usr/bin/env python3
"""Draw Stage 2 of the tube plan: planted-truth F1 by arm, and the paired leak checks.

    python tools/make_tube_ssl_figure.py --run <folder> --out <folder>

Reads ``results.jsonl`` from ``tools/tube_self_supervised.py``; writes ``tube_ssl_fig.png``.
A fit with no true positive on the held-out fold is drawn at F1 0.
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
MODELS = {"tube": ("#6b6b6b", "o", -0.30), "tube_guard": ("#a8a8a8", "s", -0.15),
          "line": ("#2a78d6", "o", 0.0), "line_length": ("#eb6834", "s", 0.15),
          "line_bound": ("#1baf7a", "D", 0.30)}
"""Every architecture in the results file gets a column. The three `line` builds take the first
three categorical slots of the dataviz reference palette, which pass its colour-vision check on
every pair; the tube family stays grey as context. Shape separates builds inside a family, because
colour alone did not: a blind reviewer measured the two greys at a contrast ratio of 1.36."""

CHECKS = [("real_vs_shared_offset", "shared\noffset,\nsame crop"),
          ("real_vs_shared_offset_independent_crop", "shared\noffset,\nother crop"),
          ("unplanted_twin_vs_rigid_shift", "twin vs\nrigid\nshift"),
          ("real_vs_thinned", "a fifth\nof onsets\nremoved"),
          ("real_vs_rigid_shift", "rigid\nshift")]
"""The first three should read 0.5. The fourth is the POSITIVE control, added 2026-09-16: a
count change the checks must be able to see, or their 0.5 says nothing. The fifth is what the
objective paid for."""

YLIM = (-0.03, 0.9)
"""Shared by panels A and B *and* by Figure 1's bake-off axis, so a score carries between them."""


def f1(v):
    x = v.get("f1")
    return 0.0 if x is None or not np.isfinite(x) else float(x)


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args(argv)
    R = [json.loads(line) for line in open(Path(a.run) / "results.jsonl")]
    n_fits = {len([r for r in R if r["arm"] == arm and r["model"] == m
                   and (J is None or r["J_sec"] == J)]) for arm, J, _ in ARMS for m in MODELS}
    fig, axes = plt.subplots(1, 3, figsize=(16.5, 5.4),
                             gridspec_kw={"width_ratios": [1.45, 1.45, 1.2]})
    rs = np.random.RandomState(0)
    cover = [float(np.median(r["scores"]["oracle"]["coverage_share"])) for r in R
             if r["arm"] == "untrained" and r["scores"].get("oracle", {}).get("coverage_share")]
    for ax, key, letter, title in ((axes[0], "oracle", "A",
                                    "truth-reading threshold (reads planted truth)"),
                                   (axes[1], "label_free_2", "B",
                                    "label-free threshold (≤ 2 events per 10 min)")):
        for i, (arm, J, _) in enumerate(ARMS):
            for m, (c, mk, dx) in MODELS.items():
                vals = [f1(r["scores"].get(key, {})) for r in R if r["arm"] == arm
                        and r["model"] == m and (J is None or r["J_sec"] == J)]
                if not vals:
                    continue
                x = i + dx + rs.uniform(-0.03, 0.03, len(vals))
                ax.plot(x, vals, mk, color=c, ms=3.4, alpha=0.75, mew=0.4, mec="white")
                ax.plot([i + dx - 0.06, i + dx + 0.06], [np.mean(vals)] * 2, color=c, lw=2.5)
        u = [i for i, (arm, _, _) in enumerate(ARMS) if arm == "untrained"]
        for i in u:
            ax.axvspan(i - 0.45, i + 0.45, color="#c0392b", alpha=0.07, zorder=0)
        if u and key == "oracle" and cover:
            # Read from the rows, not typed: the median share of each held-out recording that the
            # untrained fits' detections cover at their truth-reading threshold.
            ax.annotate(f"detections cover\n{min(cover):.0%}–{max(cover):.0%} of\nthe recording",
                        (u[0], 0.74), ha="center", fontsize=8, color="#c0392b")
        ax.set_xticks(range(len(ARMS)), [lab for _, _, lab in ARMS], fontsize=8.5)
        ax.set_xlabel("training arm (the last four read no labels)", fontsize=9)
        ax.set_ylim(*YLIM)
        ax.set_ylabel(f"planted-truth F1, held-out fold\n{title}", fontsize=9)
        ax.text(0.02, 0.97, letter, transform=ax.transAxes, fontsize=12, fontweight="bold",
                va="top")
    bx = axes[2]
    for i, (k, _) in enumerate(CHECKS):
        for m, (c, mk, dx) in MODELS.items():
            vals = [r["checks"][k]["share_real_higher"] for r in R
                    if r["arm"] == "ssl_real" and r["model"] == m and k in r.get("checks", {})
                    and r["checks"][k]["share_real_higher"] is not None]
            if not vals:
                continue
            x = i + dx + rs.uniform(-0.03, 0.03, len(vals))
            bx.plot(x, vals, mk, color=c, ms=3.4, alpha=0.75, mew=0.4, mec="white")
            bx.plot([i + dx - 0.06, i + dx + 0.06], [np.mean(vals)] * 2, color=c, lw=2.5)
    bx.axvspan(2.5, 3.5, color="#2e7d32", alpha=0.06, zorder=0)
    bx.axhline(0.5, color="0.55", ls=":", lw=0.9)
    bx.set_xticks(range(len(CHECKS)), [lab for _, lab in CHECKS], fontsize=8)
    bx.set_xlabel("paired check (first three: should read 0.5; shaded: must move)", fontsize=9)
    bx.set_ylim(0.0, 1.0)
    bx.set_ylabel("share of held-out crops where real scores higher\n"
                  "(trained on real lab recordings, both displacements)", fontsize=9)
    bx.text(0.03, 0.97, "C", transform=bx.transAxes, fontsize=12, fontweight="bold", va="top")
    handles = [Line2D([], [], color=c, marker=mk, ls="", alpha=0.75, mew=0.4, mec="white", label=m)
               for m, (c, mk, _) in MODELS.items()]
    per_arm = "/".join(str(n) for n in sorted(n_fits))
    handles += [Line2D([], [], color="0.3", lw=2.5,
                       label=f"bar: mean over fits — {per_arm} per column in A and B,\n"
                             "twice that in C (both displacements pooled)"),
                Line2D([], [], color="0.3", marker="o", ls="", alpha=0.75,
                       label="dot: one fit (no true positive scores 0)"),
                Line2D([], [], color="#c0392b", lw=6, alpha=0.2,
                       label="shaded red: not a baseline — see the caption"),
                Line2D([], [], color="0.55", ls=":", label="chance, 0.5 (panel C)")]
    fig.legend(handles=handles, loc="upper center", ncol=5, frameon=False, fontsize=8.5)
    fig.text(0.5, 0.855, "no labels = trained against rigid shift at displacement J, on simulated "
                         "(sim) or real lab recordings · panels A and B share one F1 scale with "
                         "Figure 1 · the ≤ 0.5 and ≤ 1 events per 10 min thresholds are in the "
                         "report's table, not drawn here",
             ha="center", fontsize=8, color="0.35")
    fig.tight_layout(rect=(0, 0, 1, 0.83))
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    p = out / "tube_ssl_fig.png"
    fig.savefig(p, dpi=150)
    print(p)


if __name__ == "__main__":
    main()
