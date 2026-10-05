#!/usr/bin/env python3
"""Figure 1 and the leaderboard tables of the cross-stream 3 x 3.

    python tools/make_cross_stream_figure.py --run <folder> [--also docs/learned/runs/<name>]

Reads ``cross_stream.json`` from ``tools/score_cross_stream.py``.

* ``fig1_cross_stream_3x3.png`` — one panel per detector, a 3 x 3 grid: rows the stream the version
  was tuned or trained on, columns the bench it was scored on. Colour is mean F1 as scored, on one
  scale for every panel. Each cell reads, top to bottom: F1 as scored with its 95% bootstrap
  interval over seeds, F1 with decoy calls left out of precision, and calls per hour on the
  no-coordination recording. Each version is the one its bench settled on (the search's proposal
  where there is one); the shipped points are in the tables.
* ``leaderboards.md`` — one table per scored-on stream, every version as a row, best F1 first.
"""
from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

STREAMS = ("fast", "slow", "combined")
ORDER = ("coact", "loco", "sce", "rate", "sync", "cicada", "chorus_norm", "chorus_gain_norm")
VMIN, VMAX = 0.45, 0.90


def find(rows, det, variant, tuned, scored):
    return next(r for r in rows if r["det"] == det and r["variant"] == variant
                and r["tuned"] == tuned and r["scored"] == scored)


def figure(R, out: Path) -> Path:
    rows, names, chosen = R["rows"], R["names"], R["chosen"]
    fig, axes = plt.subplots(2, 4, figsize=(21, 10))
    fig.subplots_adjust(wspace=0.55, hspace=0.3)
    cmap = plt.get_cmap("viridis")
    for k, (ax, det) in enumerate(zip(axes.ravel(), ORDER)):
        grid = np.full((3, 3), np.nan)
        for i, tuned in enumerate(STREAMS):
            for j, scored in enumerate(STREAMS):
                r = find(rows, det, chosen[det][tuned], tuned, scored)
                if "not_runnable_as_is" in r:
                    ax.text(j, i, "not runnable\nas-is", ha="center", va="center", fontsize=7)
                    continue
                grid[i, j] = r["mean_f1"]
                lo, hi = r["mean_f1_ci"]
                txt = (f"{r['mean_f1']:.3f}\n[{lo:.3f}, {hi:.3f}]\n"
                       f"{r['mean_f1_without_decoys']:.3f}\n{r['null_calls_per_hour']:.1f}/h")
                ink = "white" if r["mean_f1"] < (VMIN + VMAX) / 2 else "black"
                ax.text(j, i, txt, ha="center", va="center", fontsize=7, color=ink,
                        fontweight="bold" if i == j else "normal")
        im = ax.imshow(grid, cmap=cmap, vmin=VMIN, vmax=VMAX)
        ax.set_xticks(range(3))
        ax.set_xticklabels([f"on {s}" for s in STREAMS], fontsize=8)
        ax.set_yticks(range(3))
        ax.set_yticklabels([f"{s}\n({chosen[det][s]})" for s in STREAMS], fontsize=7.5)
        ax.set_xlabel(f"{names[det]}: scored on", fontsize=9)
        if k % 4 == 0:
            ax.set_ylabel("tuned on", fontsize=9)
    cb = fig.colorbar(im, ax=axes, shrink=0.6, pad=0.02)
    cb.set_label("mean F1 as scored (quiet and busy, 24 fresh seeds each)")
    fig.text(0.01, 0.01, "each cell: F1 as scored  ·  [95% bootstrap over seeds]  ·  F1 with decoy "
             "calls left out of precision  ·  calls/h on the no-coordination recording; "
             "diagonal in bold", fontsize=8.5)
    p = out / "fig1_cross_stream_3x3.png"
    fig.savefig(p, dpi=150, bbox_inches="tight")
    plt.close(fig)
    return p


def tables(R, out: Path) -> Path:
    rows, names = R["rows"], R["names"]
    lines = []
    for scored in STREAMS:
        rs = [r for r in rows if r["scored"] == scored and "mean_f1" in r]
        rs.sort(key=lambda r: -r["mean_f1"])
        lines += [f"#### Scored on the {scored} bench", "",
                  "| rank | detector | version | tuned on | F1 as scored [95%] | "
                  "F1 without decoy calls [95%] | calls/h, no-coordination |",
                  "|---|---|---|---|---|---|---|"]
        for k, r in enumerate(rs, 1):
            lo, hi = r["mean_f1_ci"]
            wlo, whi = r["mean_f1_without_decoys_ci"]
            home = " (own bench)" if r["tuned"] == scored else ""
            lines.append(f"| {k} | {names[r['det']]} | {r['variant']} | {r['tuned']}{home} | "
                         f"{r['mean_f1']:.3f} [{lo:.3f}, {hi:.3f}] | "
                         f"{r['mean_f1_without_decoys']:.3f} [{wlo:.3f}, {whi:.3f}] | "
                         f"{r['null_calls_per_hour']:.2f} |")
        bad = [r for r in rows if r["scored"] == scored and "not_runnable_as_is" in r]
        for r in bad:
            lines.append(f"| — | {names[r['det']]} | {r['variant']} | {r['tuned']} | "
                         f"not runnable as-is: {r['not_runnable_as_is'][0]} | | |")
        lines.append("")
    p = out / "leaderboards.md"
    p.write_text("\n".join(lines), encoding="utf-8")
    return p


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--run", type=Path, required=True)
    ap.add_argument("--also", type=Path, default=None)
    a = ap.parse_args(argv)
    R = json.loads((a.run / "cross_stream.json").read_text())
    made = [figure(R, a.run), tables(R, a.run)]
    if a.also:
        a.also.mkdir(parents=True, exist_ok=True)
        for p in [*made, a.run / "cross_stream.json"]:
            shutil.copy2(p, a.also / p.name)
    for p in made:
        print(p)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
