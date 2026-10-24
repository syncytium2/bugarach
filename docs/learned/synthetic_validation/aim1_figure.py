"""Figure 1 for Aim 1a: recovered divided by planted, for each parameter, against planted jitter.

Measured values only; the Aim 0 predictions are compared in Figure 2 (aim0_figures.py). The
caption lives on the goal page, where it is set at body size. Reads aim1_one_source.json beside
this file. Writes the PNG to --out (default: the darkroom folder this goal claims) and, unless
--no-repo, a copy beside this file.

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
sys.path.insert(0, str(ROOT / "tools"))
sys.path.insert(0, str(HERE))

# Fixed categorical order (dataviz default palette, light mode); K = 6 takes red, not a second
# green, so it cannot be confused with the 4 s window (murderboard role 10).
SERIES = [
    ("cr 1.0", "coordination rates, 1 s window", "#2a78d6"),
    ("cr 2.0", "coordination rates, 2 s window", "#eb6834"),
    ("cr 4.0", "coordination rates, 4 s window", "#1baf7a"),
    ("as 3", "assessor, K = 3 cells", "#eda100"),
    ("as 4", "assessor, K = 4 cells", "#e87ba4"),
    ("as 6", "assessor, K = 6 cells", "#e34948"),
    ("fit", "coordination rates, joint fit across windows", "#6250d6"),
]
PARAMS = [  # (y label, truth key, coordination-rates key, assessor key)
    ("participants per event", "k", "k", "part"),
    ("coordinated events per min", "per_min", "lam", "per_min"),
    ("coordinated share of onsets", "share", "share", None),
    ("jitter SD", "jitter", None, "jit"),
]
YLIM = (0.05, 30)


def value(row, series, tkey, cr_key, as_key):
    """The recovered value of `tkey` from one estimator, or None where it gives none."""
    kind, _, arg = series.partition(" ")
    if kind == "fit":
        f = row.get("_fit")
        if f is None:
            return None
        return {"k": f["k"], "per_min": f["lam"] * 60.0, "jitter": f["sigma"]}.get(tkey)
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
    ap.add_argument("--no-repo", action="store_true", help="do not write the copy beside this file")
    a = ap.parse_args()
    rec = json.loads((HERE / "aim1_one_source.json").read_text())
    rows = rec["rows"]
    import theory
    for r in rows:
        r["_fit"] = theory.fit_joint(r["cum"], rec["n_roi"])
    if a.out is None:
        from bugarach.paths import darkroom
        a.out = darkroom() / "2026-10-23-synthetic-validation"
    a.out.mkdir(parents=True, exist_ok=True)

    jits = sorted({r["true"]["jitter"] for r in rows})
    bgs = sorted({r["true"]["bg_rate"] for r in rows})
    fig, axes = plt.subplots(len(bgs), len(PARAMS), figsize=(15, 7.4), sharex=True, sharey=True)
    letters = "ABCDEFGH"
    for i, bg in enumerate(bgs):
        for j, (label, tkey, ckey, akey) in enumerate(PARAMS):
            ax = axes[i, j]
            ax.axhline(1.0, color="#888", lw=1, ls="--", zorder=0,
                       label="perfect recovery" if (i, j) == (0, 0) else None)
            for s_i, (skey, slabel, col) in enumerate(SERIES):
                if skey == "fit" and tkey == "share":
                    continue
                med, lo, hi, xs = [], [], [], []
                for jt in jits:
                    rat = []
                    for r in rows:
                        if r["true"]["bg_rate"] != bg or r["true"]["jitter"] != jt:
                            continue
                        v = value(r, skey, tkey, ckey, akey)
                        t = r["true"][tkey]
                        if v is None or not np.isfinite(v) or not t:
                            continue
                        rat.append(v / t)
                    if rat:
                        xs.append(jt * (1.04 ** (s_i - 3)))
                        q = np.percentile(rat, [25, 50, 75])
                        lo.append(q[0]); med.append(q[1]); hi.append(q[2])
                if xs:
                    first = (i, j) == (0, 3) if skey == "fit" else (i, j) == (0, 0)
                    ax.plot(xs, med, "-o", color=col, lw=2, ms=6, label=slabel if first else None)
                    lo_c = np.clip(lo, YLIM[0], None)
                    ax.vlines(xs, lo_c, hi, color=col, lw=1.5, alpha=0.7)
                    off = [x for x, l in zip(xs, lo) if l < YLIM[0]]
                    if off:   # an interquartile bar running off the bottom is marked, not cut
                        ax.plot(off, [YLIM[0] * 1.15] * len(off), "v", color=col, ms=7)
            ax.set_xscale("log"); ax.set_yscale("log")
            ax.set_ylim(*YLIM)
            ax.set_xticks(jits); ax.set_xticklabels([f"{x:g}" for x in jits])
            ax.grid(True, which="major", color="#e5e5e5", lw=0.6)
            for sp in ("top", "right"):
                ax.spines[sp].set_visible(False)
            ax.text(0.02, 0.96, letters[i * len(PARAMS) + j], transform=ax.transAxes,
                    fontsize=12, fontweight="bold", va="top")
            if i == len(bgs) - 1:
                ax.set_xlabel("planted jitter SD (s)")
            ax.set_ylabel(f"{label}\nrecovered ÷ planted", fontsize=9)
            ax.yaxis.set_tick_params(labelleft=True)
        fig.text(0.004, 0.70 - 0.42 * i, f"background {bg:g} Hz per cell", rotation=90,
                 fontsize=11, va="center")
    fig.legend(loc="upper center", ncol=4, frameon=False, fontsize=9.5)
    fig.tight_layout(rect=(0.02, 0.0, 1, 0.90))
    sys.path.insert(0, str(ROOT / "tools"))
    from naming import artifact_name
    name = artifact_name.build(artifact_name.load_codes(), source="synth", type="recovery",
                               form="plot", topic="one source jitter", ext="png",
                               date="20261023")
    meta = {"Title": "Figure 1. Aim 1a, measured recovery against planted jitter",
            "Author": "bugarach synthetic validation (docs/learned/synthetic_validation)"}
    dests = [a.out] + ([] if a.no_repo else [HERE])
    for d in dests:
        fig.savefig(d / name, dpi=130, metadata=meta)
        print(d / name)


if __name__ == "__main__":
    main()
