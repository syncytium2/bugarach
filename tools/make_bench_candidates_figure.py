#!/usr/bin/env python3
"""Figure 1 of the overnight tuning run: every candidate's F1 on fresh bench seeds, both ways.

    python tools/make_bench_candidates_figure.py --candidates <candidates.json> --out <folder> \
        [--also docs/learned/runs/<name>]

One panel per bench (fast, slow, combined). Each row is a candidate: CoactDetect at the shipped
operating point and at the search's proposal, then every chorus seed. A filled dot is mean F1 as
scored; a ring is mean F1 with calls on decoys left out of precision (ADR-0006); the text at the
right is calls per hour on the no-coordination recording against CoactDetect's budget. The seed each
training run picked is marked ▶. A collapsed fit (one call on every recording) is drawn in red.
"""
from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.lines import Line2D  # noqa: E402

BENCHES = ("fast", "slow", "combined")
INK = {"coact": "#0072B2", "chorus_norm": "#009E73", "chorus_gain_norm": "#CC79A7",
       "loco": "#E69F00", "sce": "#56B4E9", "rate": "#D55E00", "sync": "#999933",
       "cicada": "#000000"}
NAME = {"coact": "CoactDetect", "loco": "LoCo", "sce": "SCE", "rate": "rate+context",
        "sync": "SPIKE-synch", "cicada": "locust"}   # the sixth detector's name, ADR-0002


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--candidates", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--also", type=Path, default=None)
    a = ap.parse_args(argv)
    C = json.loads(a.candidates.read_text())
    tall = max(len(C["results"][b]) for b in BENCHES)
    fig, axes = plt.subplots(1, 3, figsize=(15, max(6.2, 0.45 * tall + 2)), sharex=True)
    seen: list = []
    for ax, bench in zip(axes, BENCHES):
        R = C["results"][bench]
        meta = C["benches"][bench]
        picked = {v["picked"] for v in meta["chorus"].values() if v.get("picked")}
        names = list(R)
        for y, name in enumerate(reversed(names)):
            r = R[name]
            kind, label = name.split(":", 1)
            fam = label.split("_" + bench)[0] if kind == "chorus" else kind
            if fam not in seen:
                seen.append(fam)
            col = "#C0392B" if r["collapsed"] else INK.get(fam, "0.4")
            ax.plot(r["mean_f1"], y, "o", color=col, ms=6)
            ax.plot(r["mean_f1_without_decoys"], y, "o", mfc="white", mec=col, ms=7, mew=1.3)
            ax.plot([r["mean_f1"], r["mean_f1_without_decoys"]], [y, y], color=col, lw=0.8)
            short = (label.replace(f"_{bench}_", " ").replace(".json", "") if kind == "chorus"
                     else f"{NAME.get(kind, kind)} {label}")
            ax.text(-0.01, y, ("▶ " if label in picked else "") + short, ha="right",
                    va="center", fontsize=7.5, transform=ax.get_yaxis_transform())
            ax.text(1.01, y, f"{r['null_calls_per_hour']:.1f}/h", ha="left", va="center",
                    fontsize=7, color="0.35", transform=ax.get_yaxis_transform())
        ax.set_yticks([])
        ax.set_ylim(-0.7, len(names) - 0.3)
        kinds = {n.split(":", 1)[0] for n in names}
        budget = (f", CoactDetect's budget {meta['budget_null_per_hour']:g} calls/h"
                  if kinds <= {"coact", "chorus"} else ", each detector's budget in the record")
        ax.set_xlabel(f"{bench} bench: mean F1 over quiet and busy (24 fresh seeds each)\n"
                      f"right: calls/h on the empty recording{budget}", fontsize=8.5)
    handles = [Line2D([], [], marker="o", ls="none", color="0.3", label="F1 as scored"),
               Line2D([], [], marker="o", ls="none", mfc="white", mec="0.3",
                      label="F1 with decoy calls left out of precision (ADR-0006)"),
               *[Line2D([], [], marker="o", ls="none", color=INK.get(f, "0.4"),
                        label=NAME.get(f, f)) for f in seen],
               Line2D([], [], marker="o", ls="none", color="#C0392B",
                      label="collapsed (one call per recording)")]
    fig.legend(handles=handles, loc="lower center", ncol=min(len(handles), 8), fontsize=8,
               frameon=False)
    fig.subplots_adjust(left=0.1, right=0.97, wspace=0.55, bottom=0.2, top=0.98)
    a.out.mkdir(parents=True, exist_ok=True)
    p = a.out / "fig1_candidates_both_ways.png"
    fig.savefig(p, dpi=150)
    if a.also:
        a.also.mkdir(parents=True, exist_ok=True)
        shutil.copy2(p, a.also / p.name)
    print(p)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
