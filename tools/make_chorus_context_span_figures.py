#!/usr/bin/env python3
"""Figures 1 and 2 and the tables of the chorus context-span run.

    python tools/make_chorus_context_span_figures.py --run <folder> [--also docs/learned/runs/<name>]

Reads ``results.json`` from ``tools/measure_chorus_context_span.py``.

* ``fig1_whole_vs_pieces.png`` — per background (columns), the F1 of each model × trained stream ×
  scored bench under both inference modes (top), and the whole − pieces difference (bottom), all
  with 95% bootstrap intervals over seeds. The difference is drawn twice: over the whole recording,
  and with planted events and calls within 30 s of a piece edge left out of both modes.
* ``fig2_example_raster.png`` — one bench recording's raster across the elevated-rate stretch and a
  piece edge, with the planted events, both modes' calls and the piece edges in lanes above it.
  Nothing is drawn on the raster.
* ``tables.md`` — every bench cell and the real-data summary.
"""
from __future__ import annotations

import argparse
import importlib
import json
import shutil
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))

from bugarach.time_axis import label as tlabel  # noqa: E402
from bugarach.time_axis import ticks as tticks  # noqa: E402

STREAMS = ("fast", "slow", "combined")
MODELS = ("chorus_norm", "chorus_gain_norm")
REG = ("baseline_quiet", "baseline_busy")
BG = {"baseline_quiet": "quiet background", "baseline_busy": "busy background"}
MODE = {"whole": ("#1f5fa8", "o"), "pieces": ("#d9731a", "s")}
BENCHES = {"fast": "bugarach.bench", "slow": "bugarach.bench_slow",
           "combined": "bugarach.bench_combined"}
SHORT = {"fast": "F", "slow": "S", "combined": "C"}
ZOOM = (1000.0, 1700.0)


def keys():
    return [(m, s, b) for m in MODELS for s in STREAMS for b in STREAMS]


def fig1(R, out: Path) -> Path:
    ks = keys()
    x = np.arange(len(ks), dtype=float)
    x[len(ks) // 2:] += 1.0  # a gap between the two models
    fig, axes = plt.subplots(2, 2, figsize=(15, 7.5), sharex=True,
                             gridspec_kw=dict(height_ratios=(1.4, 1.0), hspace=0.08, wspace=0.18))
    for col, reg in enumerate(REG):
        top, bot = axes[0, col], axes[1, col]
        for k, (m, s, b) in enumerate(ks):
            c = R["bench"][f"{m}@{s}|on {b}"][reg]["full"]
            for dx, mode in ((-0.17, "whole"), (0.17, "pieces")):
                lo, hi = c["ci"][mode]["f1"]
                colour, mark = MODE[mode]
                top.errorbar(x[k] + dx, c[mode]["f1"], yerr=[[c[mode]["f1"] - lo], [hi - c[mode]["f1"]]],
                             fmt=mark, color=colour, ms=5, lw=1.2, capsize=2,
                             mfc=colour if s == b else "white")
            for dx, part, mark in ((-0.17, "full", "o"), (0.17, "away", "^")):
                d = R["bench"][f"{m}@{s}|on {b}"][reg][part]
                lo, hi = d["ci"]["diff"]["f1"]
                bot.errorbar(x[k] + dx, d["diff"]["f1"], yerr=[[d["diff"]["f1"] - lo], [hi - d["diff"]["f1"]]],
                             fmt=mark, color="black" if part == "full" else "#777777", ms=5, lw=1.2,
                             capsize=2)
        bot.axhline(0, color="#999999", lw=0.8, zorder=0)
        top.set_ylabel(f"F1 as scored · {BG[reg]}" if col == 0 else f"F1 · {BG[reg]}", fontsize=9)
        top.text(0.01, 0.97, f"Figure 1{'ab'[col]}. {BG[reg]}", transform=top.transAxes,
                 va="top", fontsize=9)
        bot.set_ylabel("whole − pieces, F1", fontsize=9)
        bot.set_xticks(x, [f"{SHORT[s]}→{SHORT[b]}" for _, s, b in ks], fontsize=8)
        for i, m in enumerate(MODELS):
            bot.text(x[i * 9: (i + 1) * 9].mean(), -0.28, m, transform=bot.get_xaxis_transform(),
                     ha="center", fontsize=9)
    handles = [
        plt.Line2D([], [], color=MODE["whole"][0], marker="o", ls="", label="whole recording"),
        plt.Line2D([], [], color=MODE["pieces"][0], marker="s", ls="", label="409.6 s pieces"),
        plt.Line2D([], [], color="black", marker="o", ls="", label="difference, every event and call"),
        plt.Line2D([], [], color="#777777", marker="^", ls="",
                   label="difference, events and calls > 30 s from a piece edge"),
    ]
    fig.legend(handles=handles, loc="lower center", ncol=4, fontsize=8.5, frameon=False,
               bbox_to_anchor=(0.5, -0.04))
    fig.text(0.01, -0.09, "x: trained stream → scored bench (F fast, S slow, C combined); filled "
             "marker = the model on its own bench. Bars: 95% bootstrap interval over 24 seeds "
             "(2,000 resamples, seeds paired between the modes). Floor: pre-ADR-0008 (min_rois ≥ 3).",
             fontsize=8)
    p = out / "fig1_whole_vs_pieces.png"
    fig.savefig(p, dpi=150, bbox_inches="tight")
    plt.close(fig)
    return p


def _time_ticks(ax, t0, t1):
    tk = [t for t in tticks(t0, t1) if t0 - 1e-9 <= t <= t1 + 1e-9]
    ax.set_xticks(tk, [tlabel(t) for t in tk])


def fig2(R, out: Path) -> Path:
    from bugarach.detectors.rate import stream_trains
    from bugarach.score import TOL_SEC
    ex = R["example"]
    b = importlib.import_module(BENCHES[ex["bench"]])
    sl, gt = b.make_recording(ex["regime"], ex["seed"])
    lo, hi = ZOOM
    trains = stream_trains(sl.streams[next(iter(sl.streams))], (lo, hi), "t50rise")
    order = np.argsort([-len(t) for t in trains], kind="stable")
    planted = np.array([e.time for e in gt.events])
    planted = planted[(planted >= lo) & (planted <= hi)]
    stretch = b.BENCH_RECORDING["hot_window"]
    fig, axes = plt.subplots(5, 1, figsize=(13, 7.2), sharex=True,
                             gridspec_kw=dict(height_ratios=(0.45, 0.45, 0.6, 0.6, 4.0), hspace=0.06))
    lane_stretch, lane_planted, lane_whole, lane_pieces, raster = axes
    lane_stretch.axvspan(*stretch, ymin=0.3, ymax=0.7, color="#bbbbbb")
    for e in ex["edges"]:
        if lo <= e <= hi:
            lane_stretch.plot([e, e], [0, 1], color="#d9731a", lw=2)
    lane_stretch.set_ylabel("stretch ·\npiece edges", rotation=0, ha="right", va="center", fontsize=8)
    lane_planted.plot(planted, np.zeros_like(planted), "v", color="black", ms=6)
    lane_planted.set_ylabel(f"planted ({planted.size})", rotation=0, ha="right", va="center",
                            fontsize=8)
    for ax, mode in ((lane_whole, "whole"), (lane_pieces, "pieces")):
        on = np.array(ex[mode]["onsets"])
        on = on[(on >= lo) & (on <= hi)]
        hit = np.array([planted.size > 0 and np.min(np.abs(planted - t)) <= TOL_SEC for t in on],
                       bool)
        ax.plot(on[hit], np.zeros(hit.sum()), "v", color="#2a9d3a", ms=7)
        ax.plot(on[~hit], np.zeros((~hit).sum()), "v", color="#c62828", ms=7)
        name = "whole" if mode == "whole" else "pieces"
        ax.set_ylabel(f"{name} ({on.size} call{'' if on.size == 1 else 's'})", rotation=0, ha="right", va="center", fontsize=8)
    for ax in axes[:4]:
        ax.set_yticks([])
        ax.set_ylim(-1, 1) if ax is not lane_stretch else ax.set_ylim(0, 1)
        for sp in ("top", "right", "left"):
            ax.spines[sp].set_visible(False)
    for r, i in enumerate(order):
        t = trains[i]
        raster.plot(t, np.full(t.shape, r), "|", color="black", ms=4, mew=0.8)
    raster.set_ylim(len(trains) - 0.5, -0.5)
    raster.set_yticks([])
    raster.set_ylabel(f"events · {len(trains)} ROIs", fontsize=9)
    raster.set_xlim(lo, hi)
    _time_ticks(raster, lo, hi)
    raster.set_xlabel("time in the recording", fontsize=9)
    m, s = ex["model"].split("@")
    fig.text(0.01, 1.02, f"Figure 2. {m} trained on the {s} stream, run on the {ex['bench']} "
             f"bench, {BG[ex['regime']]}, seed {ex['seed']}: {tlabel(lo)} to {tlabel(hi)}. "
             f"Chosen by rule: the cell whose two modes' F1 differ most, and in it the seed whose "
             f"two modes' call counts differ most.\nGrey bar: the elevated-rate stretch "
             f"({tlabel(stretch[0])}–{tlabel(stretch[1])}); orange ticks: piece edges. Call ▼ "
             "green when within 2.5 s of a planted event, red otherwise.", fontsize=8.5, va="bottom")
    p = out / "fig2_example_raster.png"
    fig.savefig(p, dpi=150, bbox_inches="tight")
    plt.close(fig)
    return p


def _ci(v, ci, f="{:.3f}"):
    return f"{f.format(v)} [{f.format(ci[0])}, {f.format(ci[1])}]"


def tables(R, out: Path) -> Path:
    L = ["#### Bench, every cell (F1 as scored; intervals are 95% bootstrap over 24 seeds)", "",
         "| model | trained on | scored on | background | F1 whole | F1 pieces | whole − pieces | "
         "whole − pieces, > 30 s from edges | F1 w/o decoys, whole − pieces | "
         "stretch calls/min whole · pieces | same, > 30 s from edges | "
         "calls near an edge, whole · pieces |",
         "|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for m, s, b in keys():
        c = R["bench"][f"{m}@{s}|on {b}"]
        for reg in REG:
            f, a = c[reg]["full"], c[reg]["away"]
            L.append(
                f"| {m} | {s} | {b} | {BG[reg].split()[0]} | "
                f"{_ci(f['whole']['f1'], f['ci']['whole']['f1'])} | "
                f"{_ci(f['pieces']['f1'], f['ci']['pieces']['f1'])} | "
                f"{_ci(f['diff']['f1'], f['ci']['diff']['f1'], '{:+.3f}')} | "
                f"{_ci(a['diff']['f1'], a['ci']['diff']['f1'], '{:+.3f}')} | "
                f"{_ci(f['diff']['f1_without_decoys'], f['ci']['diff']['f1_without_decoys'], '{:+.3f}')} | "
                f"{f['whole']['probe_calls_per_min']:.2f} · {f['pieces']['probe_calls_per_min']:.2f} | "
                f"{a['whole']['probe_calls_per_min']:.2f} · {a['pieces']['probe_calls_per_min']:.2f} | "
                f"{c[reg]['near_edge_calls']['whole']} · {c[reg]['near_edge_calls']['pieces']} |")
    L += ["", "#### No-coordination recording, calls per hour (12 seeds, 9 hours each mode)", "",
          "| model | trained on | scored on | whole [95%] | pieces [95%] | whole − pieces [95%] |",
          "|---|---|---|---|---|---|"]
    for m, s, b in keys():
        c = R["bench"][f"{m}@{s}|on {b}"]
        n, ci = c["null_calls_per_hour"], c["null_calls_per_hour_ci"]
        L.append(f"| {m} | {s} | {b} | {_ci(n['whole'], ci['whole'], '{:.2f}')} | "
                 f"{_ci(n['pieces'], ci['pieces'], '{:.2f}')} | "
                 f"{_ci(n['whole'] - n['pieces'], ci['diff'], '{:+.2f}')} |")
    S = R["real_summary"]
    L += ["", "#### Real windows, all groups (calls per hour; share = calls matched one-to-one "
          "within 2.5 s)", "",
          "| model | stream | windows | kind | hours | whole calls/h | pieces calls/h | "
          "share of whole calls matched | share of pieces calls matched |",
          "|---|---|---|---|---|---|---|---|---|"]
    for s in STREAMS:
        for m in MODELS:
            for kind in ("baseline", "treatment", "all"):
                c = S["cells"].get(f"{m}@{s}|{kind}|all")
                if not c:
                    continue
                sw = "—" if c["share_of_whole_matched"] is None else f"{c['share_of_whole_matched']:.1%}"
                sp = "—" if c["share_of_pieces_matched"] is None else f"{c['share_of_pieces_matched']:.1%}"
                L.append(f"| {m} | {s} | {c['windows']} | {kind} | {c['hours']:.1f} | "
                         f"{c['whole_per_hour']:.2f} | {c['pieces_per_hour']:.2f} | {sw} | {sp} |")
    L += ["", "#### Real windows by group and window kind", "",
          "| model | stream | group | windows | whole calls/h | pieces calls/h | "
          "share of whole calls matched |", "|---|---|---|---|---|---|---|"]
    for s in STREAMS:
        for m in MODELS:
            for g in S["groups"]:
                for kind in ("baseline", "treatment"):
                    c = S["cells"].get(f"{m}@{s}|{kind}|{g}")
                    if not c:
                        continue
                    sw = ("—" if c["share_of_whole_matched"] is None
                          else f"{c['share_of_whole_matched']:.1%}")
                    L.append(f"| {m} | {s} | {g} · {kind} | {c['windows']} | "
                             f"{c['whole_per_hour']:.2f} | {c['pieces_per_hour']:.2f} | {sw} |")
    p = out / "tables.md"
    p.write_text("\n".join(L) + "\n", encoding="utf-8")
    return p


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--run", type=Path, required=True)
    ap.add_argument("--also", type=Path, default=None)
    a = ap.parse_args(argv)
    R = json.loads((a.run / "results.json").read_text())
    made = [fig1(R, a.run), fig2(R, a.run), tables(R, a.run)]
    if a.also:
        a.also.mkdir(parents=True, exist_ok=True)
        for p in [*made, a.run / "results.json"]:
            shutil.copy2(p, a.also / p.name)
    for p in made:
        print(p)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
