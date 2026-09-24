#!/usr/bin/env python3
"""Figures 1–3 and the tables of the chorus piece-length sweep.

    python tools/make_chorus_span_sweep_figures.py --run <folder> [--also docs/learned/runs/<name>]

Reads ``results.json`` from ``tools/measure_chorus_span_sweep.py``. The x axis of every figure is
the span the model is given, the whole recording first, then pieces from the 409.6 s the models
were trained on down to 30 s; it is categorical, one step per setting run.

* ``fig1_f1_by_piece_length.png`` — F1 on each model's own bench, per background.
* ``fig2_stretch_and_null.png`` — calls per minute in the elevated-rate stretch, and calls per hour
  on the no-coordination recording, on the own bench.
* ``fig3_real_agreement.png`` — on the real windows, the share of whole-window calls each piece
  length reproduces, and calls per hour.
* ``tables.md`` — every cell.
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

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))

from bugarach.time_axis import label as tlabel  # noqa: E402

STREAMS = ("fast", "slow", "combined")
MODELS = ("chorus_norm", "chorus_gain_norm")
REG = ("baseline_quiet", "baseline_busy")
BG = {"baseline_quiet": "quiet", "baseline_busy": "busy"}
COLOUR = {"fast": "#1f5fa8", "slow": "#2a9d3a", "combined": "#d9731a"}
FLOOR_NOTE = "Floor: pre-ADR-0008 (min_rois ≥ 3)."


def mode_label(m: str, whole: str = "whole\n(45m)") -> str:
    if m == "whole":
        return whole
    s = float(m[:-1])
    return "6m49.6s\n(trained)" if abs(s - 409.6) < 1e-6 else tlabel(s)


def _xaxis(ax, modes, show=True, whole="whole\n(45m)"):
    ax.set_xticks(range(len(modes)),
                  [mode_label(m, whole) for m in modes] if show else [""] * len(modes), fontsize=8)
    ax.axvline(0.5, color="#cccccc", lw=0.8, zorder=0)


def _panel(ax, text):
    """The panel's number and name, above its top-left corner, clear of the data."""
    ax.text(0.0, 1.02, text, transform=ax.transAxes, fontsize=9, va="bottom")


def _legend_below(fig, ax, ncol=3):
    h, lab = ax.get_legend_handles_labels()
    fig.legend(h, lab, loc="upper center", bbox_to_anchor=(0.5, 0.02), ncol=ncol, fontsize=8,
               frameon=False)


def _line(ax, x, y, lo, hi, colour, ls="-", label=None):
    y, lo, hi = map(np.asarray, (y, lo, hi))
    ax.errorbar(x, y, yerr=[y - lo, hi - y], color=colour, ls=ls, marker="o", ms=4, lw=1.3,
                capsize=2, label=label)


def fig1(R, out: Path) -> Path:
    modes = R["modes"]
    x = np.arange(len(modes))
    fig, axes = plt.subplots(2, 2, figsize=(12, 7.5), sharex=True, sharey=True,
                             gridspec_kw=dict(hspace=0.12, wspace=0.08))
    for i, reg in enumerate(REG):
        for j, m in enumerate(MODELS):
            ax = axes[i, j]
            for s in STREAMS:
                c = R["bench"][f"{m}@{s}|on {s}"][reg]
                _line(ax, x, [c["value"][k]["f1"] for k in modes],
                      [c["ci"][k]["f1"][0] for k in modes], [c["ci"][k]["f1"][1] for k in modes],
                      COLOUR[s], label=f"{s} model on the {s} bench")
            _xaxis(ax, modes, show=i == 1)
            if j == 0:
                ax.set_ylabel(f"F1 as scored · {BG[reg]} background", fontsize=9)
            _panel(ax, f"Figure 1{'abcd'[2 * i + j]}. {m}, {BG[reg]} background")
    for ax in axes[1]:
        ax.set_xlabel("span given to the model: the whole recording, or pieces of this length",
                      fontsize=9)
    _legend_below(fig, axes[0, 0])
    fig.text(0.01, -0.04, "Each model on its own stream's bench. Bars: 95% bootstrap interval over "
             "24 seeds (2,000 resamples). The model sees about ±27 s; pieces below 1m cannot hold "
             "one full view. " + FLOOR_NOTE, fontsize=8)
    p = out / "fig1_f1_by_piece_length.png"
    fig.savefig(p, dpi=150, bbox_inches="tight")
    plt.close(fig)
    return p


def fig2(R, out: Path) -> Path:
    modes = R["modes"]
    x = np.arange(len(modes))
    fig, axes = plt.subplots(2, 2, figsize=(12, 7.0), sharex=True,
                             gridspec_kw=dict(hspace=0.12, wspace=0.18))
    for j, m in enumerate(MODELS):
        top, bot = axes[0, j], axes[1, j]
        for s in STREAMS:
            c = R["bench"][f"{m}@{s}|on {s}"]
            for reg, ls in zip(REG, ("-", "--")):
                k = "probe_calls_per_min"
                _line(top, x, [c[reg]["value"][q][k] for q in modes],
                      [c[reg]["ci"][q][k][0] for q in modes], [c[reg]["ci"][q][k][1] for q in modes],
                      COLOUR[s], ls, label=f"{s}, {BG[reg]} background")
            _line(bot, x, [c["null_calls_per_hour"][q] for q in modes],
                  [c["null_calls_per_hour_ci"][q][0] for q in modes],
                  [c["null_calls_per_hour_ci"][q][1] for q in modes], COLOUR[s], label=s)
        _xaxis(top, modes, show=False)
        _xaxis(bot, modes)
        _panel(top, f"Figure 2{'ab'[j]}. {m}: the elevated-rate stretch")
        _panel(bot, f"Figure 2{'cd'[j]}. {m}: the no-coordination recording")
        bot.set_xlabel("span given to the model", fontsize=9)
    fig.subplots_adjust(hspace=0.2)
    axes[0, 0].set_ylabel("calls per minute in the\nelevated-rate stretch (20m–25m)", fontsize=9)
    axes[1, 0].set_ylabel("calls per hour on the\nno-coordination recording", fontsize=9)
    _legend_below(fig, axes[0, 0])
    fig.text(0.01, -0.07, "Own bench. Stretch: 24 seeds per background, 5 minutes of stretch each; "
             "no coordination: 12 seeds, 9 hours per setting. Bars: 95% bootstrap over seeds. "
             + FLOOR_NOTE, fontsize=8)
    p = out / "fig2_stretch_and_null.png"
    fig.savefig(p, dpi=150, bbox_inches="tight")
    plt.close(fig)
    return p


def fig3(R, out: Path) -> Path:
    modes = R["modes"]
    S = R["real_summary"]["cells"]
    x = np.arange(len(modes))
    fig, axes = plt.subplots(2, 2, figsize=(12, 7.0), sharex=True,
                             gridspec_kw=dict(hspace=0.12, wspace=0.18))
    for j, m in enumerate(MODELS):
        top, bot = axes[0, j], axes[1, j]
        for s in STREAMS:
            for kind, ls in (("baseline", "-"), ("treatment", "--")):
                c = S[f"{m}@{s}|{kind}|all"]
                share = [np.nan] + [100 * c["share_of_whole_reproduced"][q] for q in modes[1:]]
                top.plot(x, share, color=COLOUR[s], ls=ls, marker="o", ms=4,
                         label=f"{s}, {kind} windows")
                bot.plot(x, [c["calls_per_hour"][q] for q in modes], color=COLOUR[s], ls=ls,
                         marker="o", ms=4)
        _xaxis(top, modes, show=False, whole="whole\nwindow")
        _xaxis(bot, modes, whole="whole\nwindow")
        _panel(top, f"Figure 3{'ab'[j]}. {m}: agreement with the whole window")
        _panel(bot, f"Figure 3{'cd'[j]}. {m}: calls per hour")
        bot.set_xlabel("span given to the model: the whole window, or pieces of this length",
                       fontsize=9)
    fig.subplots_adjust(hspace=0.2)
    axes[0, 0].set_ylabel("% of whole-window calls\nreproduced within 2.5 s", fontsize=9)
    axes[1, 0].set_ylabel("calls per hour", fontsize=9)
    _legend_below(fig, axes[0, 0])
    n = S["chorus_norm@fast|all|all"]
    fig.text(0.01, -0.07, f"The 66 recordings, {n['windows']} analysis windows, {n['hours']:.1f} "
             "hours per stream; every group pooled. Descriptive only. " + FLOOR_NOTE, fontsize=8)
    p = out / "fig3_real_agreement.png"
    fig.savefig(p, dpi=150, bbox_inches="tight")
    plt.close(fig)
    return p


def _ci(v, ci, f="{:.3f}"):
    return f"{f.format(v)} [{f.format(ci[0])}, {f.format(ci[1])}]"


def tables(R, out: Path) -> Path:
    modes = R["modes"]
    names = [mode_label(m).replace("\n", " ") for m in modes]
    L = ["#### F1 as scored, every cell (whole, then the difference from whole with its paired "
         "95% interval)", "",
         "| model | trained on | scored on | background | " + " | ".join(names) + " |",
         "|---" * (4 + len(modes)) + "|"]
    for m in MODELS:
        for s in STREAMS:
            for b in STREAMS:
                for reg in REG:
                    c = R["bench"][f"{m}@{s}|on {b}"][reg]
                    cells = [f"{c['value']['whole']['f1']:.3f}"] + [
                        _ci(c["diff_from_whole"][q]["f1"], c["diff_ci"][q]["f1"], "{:+.3f}")
                        for q in modes[1:]]
                    L.append(f"| {m} | {s} | {b} | {BG[reg]} | " + " | ".join(cells) + " |")
    for title, key, f in (("recall", "recall", "{:.3f}"), ("precision", "precision", "{:.3f}"),
                          ("calls per minute in the elevated-rate stretch", "probe_calls_per_min",
                           "{:.2f}")):
        L += ["", f"#### {title[0].upper() + title[1:]}, own bench", "",
              "| model | stream | background | " + " | ".join(names) + " |",
              "|---" * (3 + len(modes)) + "|"]
        for m in MODELS:
            for s in STREAMS:
                for reg in REG:
                    c = R["bench"][f"{m}@{s}|on {s}"][reg]
                    L.append(f"| {m} | {s} | {BG[reg]} | " + " | ".join(
                        _ci(c["value"][q][key], c["ci"][q][key], f) for q in modes) + " |")
    L += ["", "#### Calls per hour on the no-coordination recording (12 seeds, 9 hours per setting)",
          "", "| model | trained on | scored on | " + " | ".join(names) + " |",
          "|---" * (3 + len(modes)) + "|"]
    for m in MODELS:
        for s in STREAMS:
            for b in STREAMS:
                c = R["bench"][f"{m}@{s}|on {b}"]
                L.append(f"| {m} | {s} | {b} | " + " | ".join(
                    f"{c['null_calls_per_hour'][q]:.2f}" for q in modes) + " |")
    S = R["real_summary"]
    L += ["", "#### Real windows: calls per hour, and % of whole-window calls reproduced within "
          "2.5 s", "", "| model | stream | windows | " + " | ".join(names) + " |",
          "|---" * (3 + len(modes)) + "|"]
    for s in STREAMS:
        for m in MODELS:
            for kind in ("baseline", "treatment", "all"):
                c = S["cells"][f"{m}@{s}|{kind}|all"]
                cells = [f"{c['calls_per_hour']['whole']:.1f}/h"] + [
                    f"{c['calls_per_hour'][q]:.1f}/h · {100 * c['share_of_whole_reproduced'][q]:.0f}%"
                    for q in modes[1:]]
                L.append(f"| {m} | {s} | {kind} ({c['windows']}) | " + " | ".join(cells) + " |")
    L += ["", "#### Real windows by group: % of whole-window calls reproduced", "",
          "| model | stream | group · windows | " + " | ".join(names[1:]) + " |",
          "|---" * (2 + len(modes)) + "|"]
    for s in STREAMS:
        for m in MODELS:
            for g in S["groups"]:
                for kind in ("baseline", "treatment"):
                    c = S["cells"].get(f"{m}@{s}|{kind}|{g}")
                    if not c:
                        continue
                    L.append(f"| {m} | {s} | {g} · {kind} ({c['calls']['whole']} whole calls) | "
                             + " | ".join("—" if c["share_of_whole_reproduced"][q] is None else
                                          f"{100 * c['share_of_whole_reproduced'][q]:.0f}%"
                                          for q in modes[1:]) + " |")
    p = out / "tables.md"
    p.write_text("\n".join(L) + "\n", encoding="utf-8")
    return p


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--run", type=Path, required=True)
    ap.add_argument("--also", type=Path, default=None)
    a = ap.parse_args(argv)
    R = json.loads((a.run / "results.json").read_text())
    made = [fig1(R, a.run), fig2(R, a.run), fig3(R, a.run), tables(R, a.run)]
    if a.also:
        a.also.mkdir(parents=True, exist_ok=True)
        for p in [*made, a.run / "results.json"]:
            shutil.copy2(p, a.also / p.name)
    for p in made:
        print(p)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
