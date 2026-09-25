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
recordings' floors beside it; each range is a vertical line with a plain tick at each end. Right:
the share of planted events under the floor at each participation level; under ADR-0009 decision
2 those are "don't care", neither hit nor miss. Panels are lettered; the caption lives in the
report, not in the image.
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
FONT = 12
"""Points; with a figure 13 in wide this keeps labels near 10 px at report page width."""


def draw(rec: dict, out_png: Path) -> Path:
    plt.rcParams.update({"font.size": FONT})
    S, expected = rec["summary"], rec.get("expected", {})
    fig, (ax, bx) = plt.subplots(1, 2, figsize=(13, 6.8), gridspec_kw=dict(width_ratios=[1, 1.35]))
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
            # A range, not a value: a dotted line with a plain tick at each end.
            ax.plot([x + 0.09] * 2, el, color=INK[bg], lw=2, ls=":")
            ax.plot([x + 0.09] * 2, el, "_", color=INK[bg], ms=10, mew=2)
            if "null_floor_range" in e:
                nl = e["null_floor_range"]
                ax.plot([x - 0.09] * 2, nl, color="0.45", lw=2)
        ticks.append(i)
        labels.append(bench)
    ax.set_xticks(ticks)
    ax.set_xticklabels(labels)
    ax.set_xlim(-0.6, len(BENCHES) - 0.4)
    ax.set_xlabel("bench")
    ax.set_ylabel("floor, co-active ROIs\n(range over 8 seeds)")
    ax.set_ylim(0, ax.get_ylim()[1] * 1.6)           # headroom: the legend sits above the data
    ax.grid(axis="y", color="0.92", lw=0.6)
    ax.legend(handles=[
        Line2D([], [], color=INK["baseline_quiet"], lw=7, label="planted recording, quiet"),
        Line2D([], [], color=INK["baseline_busy"], lw=7, label="planted recording, busy"),
        Line2D([], [], color="0.3", lw=2, ls=":", marker="_", ms=10, mew=2,
               label="elevated-rate recording,\nsame background"),
        Line2D([], [], color="0.45", lw=2, label="no-coordination recording, quiet"),
        Patch(color="0.9", label="ADR-0009's expected range")],
        fontsize=FONT - 1, loc="upper left", frameon=False)
    for axis, letter in ((ax, "a"), (bx, "b")):
        axis.text(0.0, 1.02, letter, transform=axis.transAxes, fontsize=FONT + 3,
                  fontweight="bold", va="bottom", ha="left")
    x = 0
    xt, xl = [], []
    for bench in BENCHES:
        for bg in BACKGROUNDS:
            e = S.get(f"{bench}/{bg}")
            if not e:
                continue
            by = e["below_floor_by_participants"]
            bx.text(x + (len(by) - 1) / 2, 128, f"{bench}\n{SHORT[bg]}", ha="center",
                    va="bottom", fontsize=FONT - 1, color=INK[bg])
            for k in sorted(by, key=int):
                v = by[k]
                bx.bar(x, 100 * v["share"], color=INK[bg], width=0.8)
                bx.text(x, 100 * v["share"] + 2, f"{v['below_floor']}/{v['planted']}",
                        ha="center", va="bottom", rotation=90, fontsize=FONT - 2, color="0.3")
                xt.append(x)
                xl.append(f"{k}")
                x += 1
            x += 0.8
        x += 0.8
    bx.set_xticks(xt)
    bx.set_xticklabels(xl, fontsize=FONT - 1)
    bx.set_ylim(0, 145)
    bx.set_yticks(range(0, 101, 20))
    bx.set_ylabel("planted events under the floor,\n% of events at that level")
    bx.set_xlabel("participants per planted event (label over each bar: under the floor / planted)")
    bx.grid(axis="y", color="0.92", lw=0.6)
    fig.tight_layout()
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
