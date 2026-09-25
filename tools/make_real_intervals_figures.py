#!/usr/bin/env python3
"""Figures 1 and 2 of the real-intervals measurement (ADR-0010 part 2, step 1).

    python tools/make_real_intervals_figures.py --run <folder with intervals.json> \
        [--also docs/learned/runs/<name>]

Figure 1: per stream, the cumulative distribution of the real gaps between events (baseline
windows, measured without a detector by ``tools/measure_real_intervals.py``), against the gaps the
bench plants now: neighbouring events on the scored recording (minimum spacing 120 s), on the
close-events recording (minimum 14 s) and on the tail recording (minimum 6 s), seeds 1-24.
Figure 2: the same real gaps by group, DI, OVX, MALE, ORX, one panel per stream.

Both have a log time axis. They use matplotlib, which ``pyproject.toml`` does not declare yet
(``docs/todo/2026-09-25-matplotlib-figure-tools-are-an-undeclared-dependency.md``).
"""
from __future__ import annotations

import argparse
import importlib
import json
import os
import shutil
import sys
from pathlib import Path

import numpy as np

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))
os.environ.setdefault("BUGARACH_BENCH_FLOOR", "off")     # planted times only; no floor needed

STREAMS = ("fast", "slow", "combined")
MODULE = {"fast": "bugarach.bench", "slow": "bugarach.bench_slow",
          "combined": "bugarach.bench_combined"}
GROUP_INK = {"DI": "#0072B2", "OVX": "#D55E00", "MALE": "#009E73", "ORX": "#CC79A7"}
FONT = 12


def ecdf(ax, x, **kw):
    x = np.sort(np.asarray(x, float))
    if x.size:
        ax.step(x, np.arange(1, x.size + 1) / x.size, where="post", **kw)


def bench_gaps(stream: str, seeds=range(1, 25)) -> dict:
    """The gaps between neighbouring planted events the stream's bench plants now."""
    b = importlib.import_module(MODULE[stream])
    out = {}
    for name, mk in (("scored recording, minimum 120 s", b.make_recording),
                     ("close-events recording, minimum 14 s", b.make_crowded_recording),
                     ("tail recording, minimum 6 s", b.make_tail_recording)):
        out[name] = np.concatenate([np.diff(np.sort(mk("baseline_quiet", s)[1].times))
                                    for s in seeds])
    return out


def draw(run: Path) -> list[Path]:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    from bugarach.groups import in_group_order

    plt.rcParams.update({"font.size": FONT})
    iv = json.loads((run / "intervals.json").read_text(encoding="utf-8"))["streams"]
    outs = []
    fig, axes = plt.subplots(1, 3, figsize=(16, 7.2), sharey=True)
    for ax, s, letter in zip(axes, STREAMS, "abc"):
        real = iv[s]["pooled"]
        ecdf(ax, real, color="#C00000", lw=2.4, label=f"real, baseline windows ({len(real)} gaps)")
        for (name, g), ls in zip(bench_gaps(s).items(), ("-", "--", ":")):
            ecdf(ax, g, color="0.2", lw=1.6, ls=ls, label=f"bench now: {name} ({g.size} gaps)")
        ax.set_xscale("log")
        ax.set_xlabel(f"{s} stream: gap (s, log scale)")
        ax.grid(color="0.92")
        ax.text(0.0, 1.02, letter, transform=ax.transAxes, fontsize=FONT + 3, fontweight="bold")
        ax.legend(fontsize=FONT - 3, loc="upper center", bbox_to_anchor=(0.5, -0.16), frameon=False)
    axes[0].set_ylabel("share of gaps at or below")
    fig.tight_layout()
    p = run / "figure1_real_gaps_vs_bench.png"
    fig.savefig(p, dpi=150)
    plt.close(fig)
    outs.append(p)

    fig, axes = plt.subplots(1, 3, figsize=(16, 6.4), sharey=True)
    for ax, s, letter in zip(axes, STREAMS, "abc"):
        by = iv[s]["by_group"]
        for g in in_group_order(by):
            ecdf(ax, by[g], color=GROUP_INK.get(g, "0.4"), lw=2, label=f"{g} ({len(by[g])} gaps)")
        ax.set_xscale("log")
        ax.set_xlabel(f"{s} stream: gap (s, log scale)")
        ax.grid(color="0.92")
        ax.text(0.0, 1.02, letter, transform=ax.transAxes, fontsize=FONT + 3, fontweight="bold")
        ax.legend(fontsize=FONT - 2, loc="lower right")
    axes[0].set_ylabel("share of gaps at or below")
    fig.tight_layout()
    p = run / "figure2_real_gaps_by_group.png"
    fig.savefig(p, dpi=150)
    plt.close(fig)
    outs.append(p)
    return outs


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--run", type=Path, required=True)
    ap.add_argument("--also", type=Path, default=None)
    a = ap.parse_args(argv)
    for p in draw(a.run):
        print("wrote", p)
        if a.also:
            a.also.mkdir(parents=True, exist_ok=True)
            shutil.copy2(p, a.also / p.name)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
