#!/usr/bin/env python3
"""Figures and tables for ``tools/measure_rate_stretches.py``.

    python tools/make_rate_stretch_figures.py --run <folder> [--also docs/learned/runs/<name>]

* ``fig1_<stream>_population_rate.png`` — every recording one row, grouped by first treatment then
  group (``bugarach.groups`` order). Each row is the 60 s population rate across all of the
  recording's analysis windows; a lane **above** it carries the window spans (named) and every
  *k* = 3 stretch as a bar with a ▼ pointing down at it. Nothing is drawn on the trace.
* ``fig2_elevation_vs_breadth.png`` — every real stretch at *k* = 3, 60 s: peak within-window
  elevation against median breadth, by window type; the bench's elevated-rate test as black stars.
* ``tables.md`` — the summary per stream × window type × group × k, the GDX (OVX and ORX) senktide
  windows by recording, and the floor comparison.
"""
from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from matplotlib.lines import Line2D  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from bugarach.groups import group_key  # noqa: E402
from bugarach.time_axis import label as tlabel  # noqa: E402
from bugarach.time_axis import ticks as tticks  # noqa: E402

STREAMS = ("fast", "slow", "combined")
TYPES = ("baseline", "TTX", "senktide", "high K+", "wash")
SHORT = {"baseline": "B", "TTX": "TTX", "senktide": "SK", "high K+": "K+", "wash": "W",
         "other": "?"}
TINT = {"baseline": "#E3E3E3", "TTX": "#EDEDED", "senktide": "#B5B5B5", "high K+": "#8C8C8C",
        "wash": "#F7F7F7", "other": "#FFFFFF"}
"""Windows in the lane are NEUTRAL: grey values, a hatch for TTX, and their text labels. Blue,
vermillion and black belong to the streams and their stretch bars alone (the orchestrator,
2026-09-24: an orange slow-stream bar inside an orange senktide window could not be seen)."""
HATCH = {"TTX": "////"}
LABEL_INK = {"high K+": "white"}


def window_span(ax, a, b, kind):
    """One window in a lane: grey value, hatched where the type calls for it."""
    ax.axvspan(a, b, facecolor=TINT.get(kind, "#FFFFFF"), edgecolor="#9A9A9A",
               hatch=HATCH.get(kind), lw=0)
TREAT_ORDER = {"senktide": 0, "TTX": 1, None: 2}


def recordings(rows, stream):
    by = {}
    for r in rows:
        if r["stream"] == stream:
            by.setdefault(r["slice_id"], []).append(r)
    order = sorted(by, key=lambda sid: (TREAT_ORDER.get(by[sid][0]["first_treatment"], 3),
                                        group_key(by[sid][0]["group"] or "~"), sid))
    return [(sid, sorted(by[sid], key=lambda r: r["win_start"])) for sid in order]


def fig1(R, stream, out: Path) -> Path:
    recs = recordings(R["rows"], stream)
    n = len(recs)
    fig = plt.figure(figsize=(14, 0.72 * n + 1.5))
    # lane, trace, gap: the gap keeps one recording's trace from reading as the next one's.
    gs = fig.add_gridspec(3 * n, 1, height_ratios=[0.28, 1.0, 0.3] * n, hspace=0.0)

    def baseline_end(ws):
        """Where this recording's time axis puts 0: the end of its baseline window (Tony,
        2026-09-24: "align by baseline end"). A recording with no baseline window keeps its own
        clock and says so in its label."""
        b = next((w for w in ws if w["window_type"] == "baseline"), None)
        return (b["win_end"], True) if b else (0.0, False)

    shifts = {sid: baseline_end(ws) for sid, ws in recs}
    tmin = min(w["win_start"] - shifts[sid][0] for sid, ws in recs for w in ws)
    tmax = max(w["win_end"] - shifts[sid][0] for sid, ws in recs for w in ws)
    axes, first = [], None
    for i, (sid, ws) in enumerate(recs):
        z, aligned = shifts[sid]
        lane = fig.add_subplot(gs[3 * i], sharex=first)
        first = first or lane
        ax = fig.add_subplot(gs[3 * i + 1], sharex=first)
        lane.text(-0.005, 0.0, f"{sid}  {ws[0]['group']} · first: {ws[0]['first_treatment'] or '-'}"
                  + ("" if aligned else " · NO BASELINE, unaligned"),
                  transform=lane.transAxes, ha="right", va="top", fontsize=6.5)
        for w in ws:
            a, b = w["win_start"] - z, w["win_end"] - z
            window_span(lane, a, b, w["window_type"])
            lane.text((a + b) / 2, 0.5, SHORT.get(w["window_type"], "?"),
                      ha="center", va="center", fontsize=5.5,
                      color=LABEL_INK.get(w["window_type"], "0.2"))
            c = w["measures"]["60.0"].get("curve")
            if c:
                ax.plot(np.asarray(c["starts"]) + 30.0 - z, c["rate_hz"], color="#1f3b73",
                        lw=0.6)
            for st in w["measures"]["60.0"].get("stretches", {}).get("3.0", []):
                lane.plot([st["start"] - z, st["end"] - z], [0.15, 0.15], color="#C0392B", lw=2)
                lane.plot((st["start"] + st["end"]) / 2 - z, 0.55, "v", color="#C0392B", ms=4)
        # t = 0 is marked in the lane, never on the trace.
        lane.plot([0, 0], [0.0, 1.0], color="black", lw=1.0)
        lane.set_ylim(0, 1)
        lane.axis("off")
        ax.set_yticks([])
        for sp in ("top", "right"):
            ax.spines[sp].set_visible(False)
        ax.tick_params(axis="x", labelbottom=False, length=2)
        axes.append(ax)
    tk = tticks(tmin, tmax)
    last = axes[-1]
    last.set_xlim(tmin, tmax)
    last.set_xticks(tk)
    last.set_xticklabels(["0" if t == 0 else tlabel(t) for t in tk], fontsize=10)
    last.tick_params(axis="x", labelbottom=True, length=4)
    last.set_xlabel(f"{stream} stream: time relative to the end of each recording's baseline "
                    "window, minutes (negative = baseline). Each row's trace is its population "
                    "rate (onsets per ROI per second, 60 s window, own scale); the lane above shows "
                    "the windows, t = 0 (black tick) and every k = 3 stretch (red bar, ▼)",
                    fontsize=8.5)
    p = out / f"fig1_{stream}_population_rate.png"
    fig.savefig(p, dpi=130, bbox_inches="tight")
    plt.close(fig)
    return p


def fig2(R, out: Path) -> Path:
    fig, ax = plt.subplots(figsize=(8.5, 5.8))
    col = {"baseline": "0.45", "TTX": "#3182BD", "senktide": "#E6550D", "high K+": "#31A354",
           "wash": "#9E9AC8"}
    mark = {"fast": "o", "slow": "s", "combined": "^"}
    for r in R["rows"]:
        for st in r["measures"]["60.0"].get("stretches", {}).get("3.0", []):
            ax.plot(st["median_breadth"], st["peak_elevation"], mark[r["stream"]], ms=4.5,
                    alpha=0.7, color=col.get(r["window_type"], "0.6"), mec="none")
    for b in R["bench"]:
        for st in b["measures"]["60.0"].get("stretches", {}).get("3.0", []):
            ax.plot(st["median_breadth"], st["peak_elevation"], "*", ms=11, color="black")
    ax.set_yscale("log")
    ax.set_yticks([3, 5, 10, 20, 50])
    ax.set_yticklabels(["3", "5", "10", "20", "50"])
    ax.minorticks_off()
    ax.set_xlabel("median breadth over the stretch (fraction of ROIs above their own median)")
    ax.set_ylabel("peak within-window elevation (× the window's median population rate)")
    h = [Line2D([], [], marker="o", ls="none", color=c, label=t) for t, c in col.items()]
    h += [Line2D([], [], marker=m, ls="none", color="0.3", label=f"{s} stream")
          for s, m in mark.items()]
    h += [Line2D([], [], marker="*", ls="none", color="black", ms=11,
                 label="bench's elevated-rate test (seeds 1–8, quiet and busy)")]
    ax.legend(handles=h, fontsize=7.5, loc="upper left", frameon=False)
    p = out / "fig2_elevation_vs_breadth.png"
    fig.savefig(p, dpi=150, bbox_inches="tight")
    plt.close(fig)
    return p


def fmt(x, d=2):
    return "–" if x is None else f"{x:.{d}f}"


def tables(R, out: Path) -> Path:
    S, groups = R["summary"], R["groups"]
    L = []
    sections = (("BASELINE windows only: the only admissible source for anything that shapes the "
                 "bench (FOUNDATIONS §9)", ("baseline",)),
                ("Treatment and control windows: DESCRIPTIVE ONLY, not calibration",
                 ("TTX", "senktide", "high K+", "wash")))
    for title, types in sections:
        L += [f"### {title}", ""]
        for stream in STREAMS:
            L += [f"#### {stream} stream, 60 s window", "",
                  "| window type | group | windows | recordings with a stretch, k = 2 / 3 / 5 | "
                  "stretches per hour, k = 2 / 3 / 5 | median duration, s, k = 3 | "
                  "median peak elevation, ×, k = 3 | median breadth, k = 3 |",
                  "|---|---|---|---|---|---|---|---|"]
            for wt in types:
                for g in [*groups, "all"]:
                    c = S.get(stream, {}).get(wt, {}).get(g)
                    if not c:
                        continue
                    k2, k3, k5 = c["2.0"], c["3.0"], c["5.0"]
                    L.append(
                        f"| {wt} | {g} | {k3['windows']} | {k2['recordings_with_stretch']} / "
                        f"{k3['recordings_with_stretch']} / {k5['recordings_with_stretch']} | "
                        f"{fmt(k2['stretches_per_hour'])} / {fmt(k3['stretches_per_hour'])} / "
                        f"{fmt(k5['stretches_per_hour'])} | "
                        f"{fmt(k3['median_duration_sec'], 0)} | "
                        f"{fmt(k3['median_peak_elevation'], 1)} | {fmt(k3['median_breadth'])} |")
            L.append("")
    L += ["#### The GDX senktide windows (OVX and ORX), by recording, 60 s window", "",
          "| recording | group | stream | window median rate, Hz | peak within-window elevation, × "
          "| k = 3 stretches: start into window (s), duration (s), peak (×), breadth |",
          "|---|---|---|---|---|---|"]
    for r in sorted(R["rows"], key=lambda r: (group_key(r["group"] or "~"), r["slice_id"],
                                               STREAMS.index(r["stream"]))):
        if r["window_type"] != "senktide" or r["group"] not in ("OVX", "ORX"):
            continue
        m = r["measures"]["60.0"]
        st = m.get("stretches", {}).get("3.0", [])
        desc = "; ".join(f"{x['start'] - r['win_start']:.0f}, {x['duration']:.0f}, "
                         f"{x['peak_elevation']:.1f}, {x['median_breadth']:.2f}" for x in st) or "none"
        L.append(f"| {r['slice_id']} | {r['group']} | {r['stream']} | {fmt(m['median_rate_hz'], 4)} "
                 f"| {fmt(m['peak_elevation'], 1)} | {desc} |")
    L += ["", "#### The ADR-0008 floor, whole window against stretches (k = 3) removed", "",
          "| stream | window type | group | windows with a stretch | median floor, whole window, "
          "ROIs | median floor, stretches removed, ROIs | windows where the floor falls |",
          "|---|---|---|---|---|---|---|"]
    for stream in STREAMS:
        for wt in TYPES:
            for g in [*groups, "all"]:
                rs = [r for r in R["rows"] if r["stream"] == stream and r["window_type"] == wt
                      and (g == "all" or r["group"] == g)
                      and r["floor"]["seconds_removed"] > 0
                      and "floor" in r["floor"]["whole"]
                      and "floor" in r["floor"]["stretches_removed"]]
                if not rs:
                    continue
                w = [r["floor"]["whole"]["floor"] for r in rs]
                x = [r["floor"]["stretches_removed"]["floor"] for r in rs]
                L.append(f"| {stream} | {wt} | {g} | {len(rs)} | {np.median(w):.0f} | "
                         f"{np.median(x):.0f} | {sum(a < b for a, b in zip(x, w))} |")
    L += ["", "#### The bench's elevated-rate test on the same scales (60 s window, k = 3)", "",
          "| bench | background | peak within-window elevation, × | duration, s | median breadth |",
          "|---|---|---|---|---|"]
    for stream in STREAMS:
        for reg in ("baseline_quiet", "baseline_busy"):
            bs = [b for b in R["bench"] if b["stream"] == stream and b["regime"] == reg]
            st = [s for b in bs for s in b["measures"]["60.0"]["stretches"]["3.0"]]
            if st:
                L.append(f"| {stream} | {reg.split('_')[1]} | "
                         f"{np.median([s['peak_elevation'] for s in st]):.1f} "
                         f"({min(s['peak_elevation'] for s in st):.1f}–"
                         f"{max(s['peak_elevation'] for s in st):.1f}) | "
                         f"{np.median([s['duration'] for s in st]):.0f} | "
                         f"{np.median([s['median_breadth'] for s in st]):.2f} |")
    p = out / "tables.md"
    p.write_text("\n".join(L) + "\n", encoding="utf-8")
    return p


STREAM_INK = {"fast": "#0072B2", "slow": "#D55E00", "combined": "#000000"}
"""Okabe–Ito blue and vermillion, and black: high contrast and colourblind-safe."""


def fig3(R, out: Path) -> tuple[Path, dict]:
    """The three streams superimposed per recording on ONE y-scale, grouped with gaps.

    Same layout as Figure 1 (aligned at baseline end, window lane above each trace, nothing drawn
    on the traces), with stretch bars in the lane coloured by stream. Returns the path and the
    scale it used, so the caption can quote it."""
    by = {}
    for r in R["rows"]:
        by.setdefault(r["slice_id"], {}).setdefault(r["stream"], []).append(r)
    order = [sid for sid, _ in recordings(R["rows"], "fast")]
    peaks = []
    for sid in order:
        for s, ws in by[sid].items():
            for w in ws:
                c = w["measures"]["60.0"].get("curve")
                if c and c["rate_hz"]:
                    peaks.append((max(c["rate_hz"]), sid, s, w["window_type"]))
    peaks.sort(reverse=True)
    ymax = float(np.ceil(peaks[0][0] * 100) / 100)

    def zero(ws):
        b = next((w for w in ws if w["window_type"] == "baseline"), None)
        return b["win_end"] if b else 0.0

    # Rows grouped: first treatment blocks, groups within, gaps between.
    slots, prev = [], None
    for sid in order:
        head = by[sid]["fast"][0]
        key = (head["first_treatment"], head["group"])
        if prev is not None and key[0] != prev[0]:
            slots.append(("gap", 1.6))
        elif prev is not None and key[1] != prev[1]:
            slots.append(("gap", 0.7))
        slots += [("lane", sid), ("trace", sid), ("gap", 0.25)]
        prev = key
    ratios = [0.42 if k == "lane" else 1.0 if k == "trace" else v for k, v in slots]
    fig = plt.figure(figsize=(14, 0.3 * sum(ratios) + 1.2))
    gs = fig.add_gridspec(len(slots), 1, height_ratios=ratios, hspace=0.0, top=0.975,
                          bottom=0.03)
    zs = {sid: zero(by[sid]["fast"]) for sid in order}
    tmin = min(w["win_start"] - zs[sid] for sid in order for w in by[sid]["fast"])
    tmax = max(w["win_end"] - zs[sid] for sid in order for w in by[sid]["fast"])
    first, traces, lanes, block_top = None, [], {}, {}
    level = {"fast": 0.12, "slow": 0.32, "combined": 0.52}
    for i, (kind, v) in enumerate(slots):
        if kind == "gap":
            continue
        sid = v
        z = zs[sid]
        ax = fig.add_subplot(gs[i], sharex=first)
        first = first or ax
        if kind == "lane":
            head = by[sid]["fast"][0]
            block_top.setdefault(head["first_treatment"], ax)
            for w in by[sid]["fast"]:
                a, b = w["win_start"] - z, w["win_end"] - z
                window_span(ax, a, b, w["window_type"])
                ax.text((a + b) / 2, 0.85, SHORT.get(w["window_type"], "?"), ha="center",
                        va="center", fontsize=5, color=LABEL_INK.get(w["window_type"], "0.2"))
            for s in STREAMS:
                for w in by[sid].get(s, []):
                    for st in w["measures"]["60.0"].get("stretches", {}).get("3.0", []):
                        ax.plot([st["start"] - z, st["end"] - z], [level[s]] * 2,
                                color=STREAM_INK[s], lw=1.8)
                        ax.plot((st["start"] + st["end"]) / 2 - z, level[s] + 0.1, "v",
                                color=STREAM_INK[s], ms=3)
            ax.plot([0, 0], [0, 1], color="black", lw=1.0)
            ax.text(-0.005, 0.0, f"{sid}  {head['group']}", transform=ax.transAxes,
                    ha="right", va="top", fontsize=6.5)
            ax.set_ylim(0, 1)
            ax.axis("off")
            lanes[sid] = ax
        else:
            for s in STREAMS:
                for w in by[sid].get(s, []):
                    c = w["measures"]["60.0"].get("curve")
                    if c:
                        ax.plot(np.asarray(c["starts"]) + 30.0 - z, c["rate_hz"],
                                color=STREAM_INK[s], lw=0.55, alpha=0.9)
            ax.set_ylim(0, ymax)
            ax.set_yticks([])
            for sp in ("top", "right"):
                ax.spines[sp].set_visible(False)
            ax.tick_params(axis="x", labelbottom=False, length=2)
            traces.append(ax)
    # The one reference y-axis: on the first trace only.
    ref = traces[0]
    ref.spines["right"].set_visible(True)
    ref.yaxis.tick_right()
    ref.yaxis.set_label_position("right")
    ref.set_yticks([0, ymax])
    ref.set_yticklabels(["0", f"{ymax:g}"], fontsize=7.5)
    ref.set_ylabel("onsets per ROI per second\n(the same scale in every row)", fontsize=7,
                   rotation=0, ha="left", va="center", labelpad=10)
    for treat, ax in block_top.items():
        ax.text(-0.13, 1.6, f"first treatment: {treat or 'none'}", transform=ax.transAxes,
                ha="left", va="bottom", fontsize=10, fontweight="bold")
    tk = tticks(tmin, tmax)
    last = traces[-1]
    last.set_xlim(tmin, tmax)
    last.set_xticks(tk)
    last.set_xticklabels(["0" if t == 0 else tlabel(t) for t in tk], fontsize=10)
    last.tick_params(axis="x", labelbottom=True, length=4)
    last.set_xlabel("time relative to the end of each recording's baseline window, minutes "
                    "(negative = baseline)", fontsize=9)
    fig.legend(handles=[Line2D([], [], color=STREAM_INK[s], lw=1.6, label=f"{s} stream")
                        for s in STREAMS],
               loc="lower center", ncol=3, fontsize=10, frameon=False,
               bbox_to_anchor=(0.5, 0.985))
    p = out / "fig3_three_streams_one_scale.png"
    fig.savefig(p, dpi=130, bbox_inches="tight")
    plt.close(fig)
    return p, dict(ymax=ymax, largest=peaks[0], second=peaks[1])


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--run", type=Path, required=True)
    ap.add_argument("--also", type=Path, default=None)
    a = ap.parse_args(argv)
    R = json.loads((a.run / "results.json").read_text())
    p3, scale = fig3(R, a.run)
    print("figure 3 scale:", scale)
    made = [*(fig1(R, s, a.run) for s in STREAMS), fig2(R, a.run), p3, tables(R, a.run)]
    if a.also:
        a.also.mkdir(parents=True, exist_ok=True)
        for p in made:
            shutil.copy2(p, a.also / p.name)
    for p in made:
        print(p)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
