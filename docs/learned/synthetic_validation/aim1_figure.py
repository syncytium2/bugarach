"""Figure 1 for Aim 1a: what each estimate recovers, against planted jitter.

Measured values only; the Aim 0 predictions are compared in Figure 2 (aim0_figures.py). The
caption lives on the goal page. Reads aim1_one_source.json beside this file. Writes the PNG to
--out (default: the darkroom folder this goal claims) and, unless --no-repo, a copy beside this
file. Panels A-C and E-G are recovered / planted; D and H are recovered jitter in seconds against
the identity line, so an estimator that returns a constant reads as a flat line. Only events of
10 or more cells are plotted (5-cell events are below the event floor; the page quotes them).
The assessor's jitter is plotted wherever it observed clusters: its `jit_defined` flag also needs
a surrogate cluster, which the run's 120 surrogates (shipped default 1000) often lack at K = 6.
In A-C and E-G the series are offset sideways for legibility; in D and H they sit at the planted
jitter, so the identity line reads true.

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
from matplotlib.lines import Line2D
import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "tools"))
sys.path.insert(0, str(HERE))

plt.rcParams.update({"font.size": 12})

# (key, label, colour, marker, line style). Colour picks the member; marker and line pick the
# family (circle/solid: coordination rates; square/dashed: assessor; diamond: the joint fit), so
# no pair is told apart by colour alone.
SERIES = [
    ("cr 1.0", "coordination rates, 1 s window", "#2a78d6", "o", "-"),
    ("cr 2.0", "coordination rates, 2 s window", "#eb6834", "o", "-"),
    ("cr 4.0", "coordination rates, 4 s window", "#1baf7a", "o", "-"),
    ("as 3", "assessor, K = 3 cells", "#eda100", "s", "--"),
    ("as 4", "assessor, K = 4 cells", "#e87ba4", "s", "--"),
    ("as 6", "assessor, K = 6 cells", "#008300", "s", "--"),
    ("fit", "joint fit across windows", "#6250d6", "D", "-"),
]
PARAMS = [  # (y label, truth key, coordination-rates key, assessor key)
    ("participants per event", "k", "k", "part"),
    ("coordinated events per min", "per_min", "lam", "per_min"),
    ("coordinated share of onsets", "share", "share", None),
    ("jitter SD", "jitter", None, "jit"),
]
YLIM = (0.05, 30)
JLIM = (0.004, 3)


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
    fig, axes = plt.subplots(len(bgs), len(PARAMS), figsize=(12.5, 7.6), sharex=True)
    letters = "ABCDEFGH"
    any_off = False
    for i, bg in enumerate(bgs):
        for j, (label, tkey, ckey, akey) in enumerate(PARAMS):
            ax = axes[i, j]
            jitter_panel = tkey == "jitter"
            if jitter_panel:
                xx = np.array([0.03, 1.5])
                ax.plot(xx, xx, color="#888", lw=1, ls=":", zorder=0)
            else:
                ax.axhline(1.0, color="#888", lw=1, ls=":", zorder=0)
            for s_i, (skey, slabel, col, mk, ls) in enumerate(SERIES):
                med, lo, hi, xs = [], [], [], []
                for jt in jits:
                    vals = []
                    for r in rows:
                        if (r["true"]["bg_rate"] != bg or r["true"]["jitter"] != jt
                                or r["true"]["k"] < 9.5):
                            continue
                        v = value(r, skey, tkey, ckey, akey)
                        t = r["true"][tkey]
                        if v is None or not np.isfinite(v) or not t:
                            continue
                        vals.append(v if jitter_panel else v / t)
                    if vals:
                        xs.append(jt if jitter_panel else jt * (1.09 ** (s_i - 3)))
                        q = np.percentile(vals, [25, 50, 75])
                        lo.append(q[0]); med.append(q[1]); hi.append(q[2])
                if not xs:
                    continue
                ylim = JLIM if jitter_panel else YLIM
                ax.plot(xs, med, ls=ls, marker=mk, color=col, lw=1.8, ms=6)
                ax.vlines(xs, np.clip(lo, ylim[0], None), np.minimum(hi, ylim[1]), color=col, lw=1.5)
                off = [x for x, l in zip(xs, lo) if l < ylim[0]]
                if off:   # an interquartile bar running off the bottom is marked, not cut
                    any_off = True
                    ax.plot(off, [ylim[0] * 1.25] * len(off), "v", color=col, ms=7)
            ax.set_xscale("log"); ax.set_yscale("log")
            ax.set_ylim(*(JLIM if jitter_panel else YLIM))
            ax.set_xticks(jits); ax.set_xticklabels([f"{x:g}" for x in jits])
            ax.grid(True, which="major", color="#e5e5e5", lw=0.6)
            for sp in ("top", "right"):
                ax.spines[sp].set_visible(False)
            ax.text(-0.02, 1.03, letters[i * len(PARAMS) + j], transform=ax.transAxes,
                    fontsize=13, fontweight="bold", va="bottom", ha="right")
            if i == len(bgs) - 1:
                ax.set_xlabel("planted jitter SD (s)")
            ax.set_ylabel(f"{label}\n" + ("recovered (s)" if jitter_panel else "recovered ÷ planted"),
                          fontsize=11)
        fig.text(0.012, 0.70 - 0.40 * i, f"background {bg:g} Hz per cell", rotation=90,
                 fontsize=12, va="center")
    handles = [Line2D([], [], color=c, marker=m, ls=l, lw=1.8, ms=6, label=lab)
               for _, lab, c, m, l in SERIES]
    handles += [Line2D([], [], color="#888", ls=":", label="perfect recovery"),
                Line2D([], [], color="#444", marker="|", ls="none", ms=12, mew=1.5,
                       label="interquartile range")]
    if any_off:
        handles.append(Line2D([], [], color="#444", marker="v", ls="none", ms=7,
                              label="range continues below the axis"))
    fig.legend(handles=handles, loc="upper center", ncol=4, frameon=False, fontsize=10.5)
    fig.tight_layout(rect=(0.03, 0.0, 1, 0.86))
    from naming import artifact_name
    name = artifact_name.build(artifact_name.load_codes(), source="synth", type="recovery",
                               form="plot", topic="one source jitter", ext="png",
                               date="20261023")
    meta = {"Title": "Figure 1, recovery against planted jitter (Aim 1a)",
            "Author": "bugarach synthetic validation (docs/learned/synthetic_validation)",
            "Creation Time": __import__("datetime").datetime.now().isoformat(timespec="seconds")}
    for d in [a.out] + ([] if a.no_repo else [HERE]):
        fig.savefig(d / name, dpi=130, metadata=meta)
        print(d / name)


if __name__ == "__main__":
    main()
