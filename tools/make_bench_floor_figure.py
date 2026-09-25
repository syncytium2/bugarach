#!/usr/bin/env python3
"""The bench floors re-measured under ADR-0009: each recording's ADR-0008 floor by bench and
background, against ADR-0009's expected ranges, and the planted events it leaves out of scoring.

    python tools/make_bench_floor_figure.py --floors <bench_floor.json> --out <folder> \
        [--also docs/learned/runs/<name>]

**What it reads.** ``bench_floor.json`` from ``tools/probe_bench_floor.py``: per bench (fast, slow,
combined) and background (quiet, busy), the floor of every planted recording, of the elevated-rate
recording and of the no-coordination recording (quiet only), and how many planted events sit under
their recording's floor at each participation level.

**What it draws.** Left: the floor range over seeds, in co-active ROIs, for the planted recording
(bar), with ADR-0009's expected range shaded behind it, and the elevated-rate and no-coordination
recordings' floors beside it. Right: the share of planted events under the floor at each
participation level; under ADR-0009 decision 2 those are "don't care", neither hit nor miss.
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
from matplotlib.patches import Patch  # noqa: E402

BENCHES = ("fast", "slow", "combined")
BACKGROUNDS = ("baseline_quiet", "baseline_busy")
SHORT = {"baseline_quiet": "quiet", "baseline_busy": "busy"}
INK = {"baseline_quiet": "#0072B2", "baseline_busy": "#D55E00"}


def draw(rec: dict, out_png: Path) -> Path:
    S, expected = rec["summary"], rec.get("expected", {})
    fig, (ax, bx) = plt.subplots(1, 2, figsize=(14, 5.6), gridspec_kw=dict(width_ratios=[1, 1.3]))
    ticks, labels = [], []
    for i, bench in enumerate(BENCHES):
        lo_hi = expected.get(bench)
        if lo_hi:
            ax.fill_between([i - 0.42, i + 0.42], lo_hi[0], lo_hi[1], color="0.9", zorder=0)
        for j, bg in enumerate(BACKGROUNDS):
            e = S.get(f"{bench}/{bg}")
            if not e:
                continue
            x = i + (j - 0.5) * 0.36
            lo, hi = e["bench_floor_range"]
            ax.plot([x, x], [lo, hi], color=INK[bg], lw=7, solid_capstyle="butt")
            el = e["elevated_rate_floor_range"]
            ax.plot([x + 0.09] * 2, el, color=INK[bg], lw=2, ls=":")
            ax.plot(x + 0.09, el[1], "v", color=INK[bg], ms=6)
            if "null_floor_range" in e:
                nl = e["null_floor_range"]
                ax.plot([x - 0.09] * 2, nl, color="0.45", lw=2)
        ticks.append(i)
        labels.append(bench)
    ax.set_xticks(ticks)
    ax.set_xticklabels(labels)
    ax.set_xlim(-0.6, len(BENCHES) - 0.4)
    ax.set_ylabel("floor, co-active ROIs (range over 8 seeds)")
    ax.set_ylim(0, ax.get_ylim()[1] * 1.45)          # headroom: the legend sits above the data
    ax.grid(axis="y", color="0.92", lw=0.6)
    ax.legend(handles=[
        Line2D([], [], color=INK["baseline_quiet"], lw=7, label="planted recording, quiet"),
        Line2D([], [], color=INK["baseline_busy"], lw=7, label="planted recording, busy"),
        Line2D([], [], color="0.3", lw=2, ls=":", marker="v",
               label="elevated-rate recording (same background)"),
        Line2D([], [], color="0.45", lw=2, label="no-coordination recording (quiet)"),
        Patch(color="0.9", label="ADR-0009's expected planted-recording range")],
        fontsize=8, loc="upper left", frameon=False)
    x = 0
    xt, xl = [], []
    for bench in BENCHES:
        for bg in BACKGROUNDS:
            e = S.get(f"{bench}/{bg}")
            if not e:
                continue
            by = e["below_floor_by_participants"]
            bx.text(x + (len(by) - 1) / 2, 106, f"{bench}\n{SHORT[bg]}", ha="center",
                    fontsize=8, color=INK[bg])
            for k in sorted(by, key=int):
                v = by[k]
                bx.bar(x, 100 * v["share"], color=INK[bg], width=0.8)
                bx.text(x, 100 * v["share"] + 1.5, f"{v['below_floor']}/{v['planted']}",
                        ha="center", fontsize=6.5, color="0.3")
                xt.append(x)
                xl.append(f"{k}")
                x += 1
            x += 0.8
        x += 0.8
    bx.set_xticks(xt)
    bx.set_xticklabels(xl, fontsize=8)
    bx.set_ylim(0, 118)
    bx.set_ylabel("planted events under the floor, % of events at that level")
    bx.set_xlabel("participants per planted event", fontsize=9)
    bx.grid(axis="y", color="0.92", lw=0.6)
    fig.text(0.01, 0.01, "Figure 4. The bench floors re-measured on the ADR-0009 generator "
             "(tools/probe_bench_floor.py, 8 seeds × 2 backgrounds × 3 benches, 1,000 null "
             "draws each). Right: counts are events under the floor / events planted.",
             fontsize=8.5, color="0.25")
    fig.tight_layout(rect=(0, 0.05, 1, 1))
    out_png.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_png, dpi=150)
    plt.close(fig)
    return out_png


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--floors", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--also", type=Path, default=None)
    a = ap.parse_args(argv)
    png = draw(json.loads(a.floors.read_text(encoding="utf-8")), a.out / "figure4_bench_floors.png")
    print(f"wrote {png}")
    if a.also:
        a.also.mkdir(parents=True, exist_ok=True)
        shutil.copy2(png, a.also / png.name)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
