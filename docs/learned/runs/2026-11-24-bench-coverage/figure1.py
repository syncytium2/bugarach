"""Figure 1 of this folder's README. Run from the repository root:
    python docs/learned/runs/2026-11-24-bench-coverage/figure1.py <output.png>

Per-recording background vs short-lag cross-ROI excess, 4x and 3x, groups x streams.
Background = the recording's mean per-ROI onset rate minus its coordinated share, both read from
the stage 1 coordination-rates record of that threshold (the bench's own definition,
tools/remeasure_bench.py). Excess: Review A's statistic, baseline analysis windows."""
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path.cwd()
sys.path[:0] = [str(ROOT / "src"), str(ROOT / "tools")]
import make_review_a_pages as ra  # noqa: E402
from bugarach import dataset  # noqa: E402
from bugarach.groups import in_group_order  # noqa: E402
from bugarach.io import load_folder  # noqa: E402

K = 3
RATES = {"4x": "docs/learned/runs/2026-11-12-stage1-tracked-cohorts-three-streams/rates/"
               "coordination_rates.json",
         "3x": "docs/learned/runs/2026-11-13-stage1-tracked-cohorts-3x/rates/"
               "coordination_rates.json"}
out = Path(sys.argv[1])
st = {"4x": dataset.stamp("tracked_cohorts")["name"],
      "3x": dataset.stamp("tracked_cohorts_3x")["name"]}
bg = {}
for thr, p in RATES.items():
    d = json.loads((ROOT / p).read_text())
    if d["dataset"]["name"] != st[thr]:
        raise SystemExit(f"{p} was measured on {d['dataset']['name']}, not {st[thr]}")
    for stream, v in d["streams"].items():
        for r in v["per_recording"]:
            share = r.get("share_hz") or 0.0
            bg[(thr, stream, r["slice_id"])] = max(r["rate_hz"] - share, 0.0) * 60.0

s4 = load_folder(dataset.current("tracked_cohorts"))
s3 = load_folder(dataset.current("tracked_cohorts_3x"))
rows = []
for a, b in zip(s4, s3):
    g = str(a.meta.get("group_id") or "").strip().upper()
    for stream in ra.STREAMS:
        r = ra.real_trains(a, b, stream)
        for thr, key in (("4x", "t4"), ("3x", "t3")):
            o, e = ra.correlogram(r[key], r["hi"] - r["lo"])
            o, e = np.asarray(o, float), np.asarray(e, float)
            rows.append(dict(rec=a.slice_id, group=g, stream=stream, thr=thr, rois=len(r[key]),
                             bg=bg[(thr, stream, a.slice_id)],
                             excess=o[:K].sum() / e[:K].sum() - 1.0))
for x in rows:
    print(f"{x['thr']} {x['stream']:9} {x['group']:5} {x['rec']} bg {x['bg']:6.3f}/min "
          f"excess {x['excess']:6.2f}")

import matplotlib  # noqa: E402
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.lines import Line2D  # noqa: E402
from matplotlib.ticker import FuncFormatter  # noqa: E402

groups = in_group_order(sorted({x["group"] for x in rows}))
PAL = {"DI": {"fast": "#08306B", "slow": "#2171B5", "combined": "#9ECAE1"},
       "MALE": {"fast": "#7F2704", "slow": "#E6550D", "combined": "#FDAE6B"}}
LINE = {"DI": "#2171B5", "MALE": "#E6550D"}
MARK = {"fast": "o", "slow": "s", "combined": "D"}
AREA = 2.6  # marker area (points^2) per ROI: area is proportional to the recording's ROI count

xs = [x["bg"] for x in rows if x["bg"] > 0]
xlo, xhi = min(xs) / 1.4, max(xs) * 1.4
ymax = max(x["excess"] for x in rows) * 1.08
fig, axes = plt.subplots(1, 2, figsize=(14, 6.6), sharey=True)
for ax, thr in zip(axes, ("4x", "3x")):
    pts = [x for x in rows if x["thr"] == thr]
    for rec in sorted({x["rec"] for x in pts}):
        rr = sorted([x for x in pts if x["rec"] == rec], key=lambda x: ra.STREAMS.index(x["stream"]))
        g = rr[0]["group"]
        for x in rr:
            ax.scatter(x["bg"], x["excess"], marker=MARK[x["stream"]], s=AREA * x["rois"],
                       color=PAL[g][x["stream"]], edgecolors="white", linewidths=0.6, zorder=3,
                       alpha=0.9)
            ax.annotate(rec[-3:], (x["bg"], x["excess"]), textcoords="offset points",
                        xytext=(3 + 0.55 * np.sqrt(AREA * x["rois"]), 2), fontsize=6,
                        color=PAL[g][x["stream"]]
                        if x["stream"] != "combined" else LINE[g], alpha=0.85)
    ax.set_xscale("log")
    ticks = [0.1, 0.2, 0.5, 1, 2, 5, 10]
    ax.set_xticks(ticks)
    ax.set_xticks([], minor=True)
    ax.xaxis.set_major_formatter(FuncFormatter(lambda v, _: f"{v:g}"))
    ax.axhline(0, color="#999999", lw=0.8)
    ax.set_xlim(xlo, xhi)
    ax.set_ylim(-1.5, ymax)
    ax.set_xlabel("background: onsets per minute per ROI, coordinated share removed (log scale)")
    ax.spines[["top", "right"]].set_visible(False)
    ax.set_ylabel(f"{thr} export · excess pairs, lag 0-0.3 s", fontsize=9)
    ax.yaxis.set_tick_params(labelleft=True)
handles = [Line2D([], [], marker=MARK[s], ls="", markersize=7, color=PAL[g][s],
                  markeredgecolor="white", label=f"{g} · {s}")
           for g in groups for s in ra.STREAMS]
handles += [Line2D([], [], marker="o", ls="", color="#888888", markeredgecolor="white",
                   markersize=np.sqrt(AREA * n), label=f"{n} ROIs") for n in (20, 40, 70)]
fig.legend(handles=handles, ncol=9, loc="upper left", bbox_to_anchor=(0.01, 0.925),
           frameon=False, fontsize=8.5, handletextpad=0.3, columnspacing=1.4)
fig.text(0.01, 0.995,
         "Figure 1. Each real recording's background against its cross-ROI onset excess at lag 0 "
         "to 0.3 s (observed pairs / chance - 1), at the 4x export (left) and the 3x export "
         "(right).\nBackground is the bench's own: mean onset rate per ROI minus the recording's "
         "coordinated share (stage 1 rates record). Mark area is proportional to the recording's "
         "ROI count.\nEach recording appears once per stream; the "
         "number beside a mark is the recording's last three digits. Baseline analysis window. "
         "0 is no excess.", fontsize=8.5, va="top")
fig.text(0.01, 0.004, f"Datasets: {st['4x']}; {st['3x']}.\nRecords: {RATES['4x']}; "
         f"{RATES['3x']}. Display only; no comparison between groups is made.",
         fontsize=7, color="#555555")
fig.tight_layout(rect=(0, 0.04, 1, 0.86))
fig.savefig(out, dpi=160)
print(out, file=sys.stderr)
