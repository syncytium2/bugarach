#!/usr/bin/env python3
"""Draw what the second sensor buys: the bake-off, and the probe that separates the plants.

    python tools/make_line_sensors_figure.py --bakeoff <folder> --probe <folder> --out <folder>

Reads ``bakeoff.json`` from ``tools/fair_bakeoff.py`` and ``line_vs_fuzz.json`` from
``tools/probe_line_vs_fuzz.py``. Writes ``line_sensors_fig.png``. Exploratory.
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

ORDER = ["line", "tube", "tube_guard", "line_length", "coact", "loco", "rate", "cicada",
         "tube_ratio", "tube_ratio_guard", "sce", "sync", "tiny", "trace"]
LABEL = {"line": "line\n(two sensors)", "line_length": "line_length\n(length only)",
         "tube": "tube", "tube_guard": "tube_guard", "coact": "CoactDetect", "loco": "LoCo",
         "rate": "rate+context", "cicada": "locust", "sce": "binned SCE", "sync": "SPIKE-synch",
         "tiny": "tiny", "trace": "trace", "tube_ratio": "tube_ratio",
         "tube_ratio_guard": "tube_ratio_guard"}
PLANTS = [("line", "#1f4e79", "line\nK ROIs at once"),
          ("burst", "#c07a12", "burst\nK/4 ROIs × 4"),
          ("fuzz", "#7b3294", "fuzz\nK ROIs over 3 s"),
          ("wave", "#2e7d32", "wave\nK ROIs, 1 frame apart")]


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--bakeoff", required=True)
    ap.add_argument("--probe", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--k", type=int, default=16)
    a = ap.parse_args(argv)
    bake = json.loads((Path(a.bakeoff) / "bakeoff.json").read_text())
    probe = json.loads((Path(a.probe) / "line_vs_fuzz.json").read_text())["scores"]
    rows = {**bake["hand_written"], **bake["learned"]}

    fig, (ax, bx) = plt.subplots(1, 2, figsize=(13.5, 5.6),
                                 gridspec_kw={"width_ratios": [1.65, 1]})
    names = [n for n in ORDER if n in rows]
    y = np.arange(len(names))[::-1]
    for i, n in zip(y, names):
        f = rows[n]["f1"]
        c = "#1f4e79" if n == "line" else ("#7b3294" if n == "line_length" else "0.45")
        ax.plot([f["min"], f["max"]], [i, i], color=c, lw=2, alpha=0.8)
        ax.plot(f["mean"], i, "o", color=c, ms=6)
    ax.set_yticks(y, [LABEL.get(n, n).replace("\n", " ") for n in names], fontsize=8.5)
    ax.set_xlim(0.05, 0.85)
    ax.set_xlabel("planted-truth F1 on the held-out fold, one bake-off run of four folds\n"
                  "(dot: mean over folds; bar: fold range)")
    ax.text(0.01, 0.98, "A", transform=ax.transAxes, fontsize=12, fontweight="bold", va="top")

    models = [("supervised line", "two sensors"), ("supervised line_length", "length only"),
              ("supervised tube", "tube")]
    x = np.arange(len(models))
    for j, (plant, colour, _) in enumerate(PLANTS):
        vals, errs = [], []
        for m, _ in models:
            r = probe[m]
            vals.append(r[f"{plant}_{a.k}"])
            errs.append(r[f"{plant}_{a.k}_sd"])
        bx.bar(x + (j - 1.5) * 0.2, vals, 0.19, yerr=errs, color=colour, capsize=2, alpha=0.9)
    bx.set_xticks(x, [lab for _, lab in models], fontsize=9)
    bx.set_ylabel(f"response to a plant of K = {a.k} ROIs' worth of ink\n"
                  "(peak score with the plant minus the same field without it)")
    bx.set_xlabel("trained model")
    bx.text(0.03, 0.98, "B", transform=bx.transAxes, fontsize=12, fontweight="bold", va="top")
    bx.legend(handles=[Line2D([], [], color=c, lw=6, label=lab.replace("\n", ": "))
                       for _, c, lab in PLANTS], frameon=False, fontsize=8, loc="upper right")
    fig.tight_layout()
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    p = out / "line_sensors_fig.png"
    fig.savefig(p, dpi=150)
    print(p)


if __name__ == "__main__":
    main()
