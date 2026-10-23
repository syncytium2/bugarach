"""Figure 1 for Aim 1a: recovered divided by planted, for each parameter, against planted jitter.

Reads aim1_one_source.json beside this file. Writes the PNG to the darkroom folder this goal
claims, and a copy beside this file (--also is the default here: the figure is small).

    PYTHONPATH=src python docs/learned/synthetic_validation/aim1_figure.py
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

# Fixed categorical order (dataviz default palette, light mode).
SERIES = [
    ("cr 1.0", "coordination rates, 1 s window", "#2a78d6"),
    ("cr 2.0", "coordination rates, 2 s window", "#eb6834"),
    ("cr 4.0", "coordination rates, 4 s window", "#1baf7a"),
    ("as 3", "assess, K = 3 cells", "#eda100"),
    ("as 4", "assess, K = 4 cells", "#e87ba4"),
    ("as 6", "assess, K = 6 cells", "#008300"),
]
PARAMS = [  # (column label, truth key, coord-rates key, assess key)
    ("participants per event (cells)", "k", "k", "part"),
    ("coordinated events per min", "per_min", "lam", "per_min"),
    ("coordinated share of onsets", "share", "share", None),
    ("jitter, SD (s)", "jitter", None, "jit"),
]


def value(row, series, cr_key, as_key):
    kind, arg = series.split()
    if kind == "cr":
        if cr_key is None:
            return None
        v = row["coord_rates"][arg][cr_key]
        return v * 60.0 if cr_key == "lam" else v
    if as_key is None:
        return None
    return row["assess"][arg][as_key]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, default=None)
    a = ap.parse_args()
    rec = json.loads((HERE / "aim1_one_source.json").read_text())
    rows = rec["rows"]
    if a.out is None:
        from bugarach.paths import darkroom
        a.out = darkroom() / "2026-10-23-synthetic-validation"
    a.out.mkdir(parents=True, exist_ok=True)

    jits = sorted({r["true"]["jitter"] for r in rows})
    bgs = sorted({r["true"]["bg_rate"] for r in rows})
    fig, axes = plt.subplots(len(bgs), len(PARAMS), figsize=(15, 6.6), sharex=True, sharey=True)
    for i, bg in enumerate(bgs):
        for j, (label, tkey, ckey, akey) in enumerate(PARAMS):
            ax = axes[i, j]
            ax.axhline(1.0, color="#888", lw=1, ls="--", zorder=0)
            for s_i, (skey, slabel, col) in enumerate(SERIES):
                med, lo, hi, xs = [], [], [], []
                for jt in jits:
                    rat = []
                    for r in rows:
                        if r["true"]["bg_rate"] != bg or r["true"]["jitter"] != jt:
                            continue
                        v = value(r, skey, ckey, akey)
                        t = r["true"][tkey]
                        if v is None or not np.isfinite(v) or not t:
                            continue
                        rat.append(v / t)
                    if rat:
                        xs.append(jt * (1.04 ** (s_i - 2.5)))
                        q = np.percentile(rat, [25, 50, 75])
                        lo.append(q[0]); med.append(q[1]); hi.append(q[2])
                if xs:
                    ax.plot(xs, med, "-o", color=col, lw=2, ms=6, label=slabel if (i, j) == (0, 0) else None)
                    ax.vlines(xs, lo, hi, color=col, lw=1.5, alpha=0.7)
            ax.set_xscale("log"); ax.set_yscale("log")
            ax.set_ylim(0.08, 30)
            ax.set_xticks(jits); ax.set_xticklabels([f"{j:g}" for j in jits])
            ax.grid(True, which="major", color="#e5e5e5", lw=0.6)
            for sp in ("top", "right"):
                ax.spines[sp].set_visible(False)
            if i == len(bgs) - 1:
                ax.set_xlabel("planted jitter, SD (s)")
            if j == 0:
                ax.set_ylabel(f"recovered ÷ planted\nbackground {bg:g} Hz per cell")
            if i == 0:
                ax.text(0.02, 1.02, label, transform=ax.transAxes, fontsize=10, color="#333")
    fig.legend(loc="upper center", ncol=6, frameon=False, fontsize=9)
    n_rec = len(rows)
    fig.text(0.01, 0.005,
             f"Figure 1. Aim 1a, one source, random membership. {n_rec} simulated recordings "
             f"({rec['n_roi']} cells, {rec['duration_sec'] / 60:.0f} min each); points are medians "
             "over seeds, participation (0.15/0.3/0.6) and event count (15/45), bars the "
             "interquartile range. Dashed line: perfect recovery.", fontsize=8.5, color="#333")
    fig.tight_layout(rect=(0, 0.03, 1, 0.94))
    # Synthetic data: the synth source, a recovery plot, and a topic (armory naming README).
    sys.path.insert(0, str(ROOT / "tools"))
    from naming import artifact_name
    name = artifact_name.build(artifact_name.load_codes(), source="synth", type="recovery",
                               form="plot", topic="one source jitter", ext="png",
                               date="20261023")
    for d in (a.out, HERE):
        fig.savefig(d / name, dpi=130)
        print(d / name)


if __name__ == "__main__":
    main()
