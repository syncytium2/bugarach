#!/usr/bin/env python3
"""Draw the slow co-modulation explainer's figures from ``measure_slow_comodulation.py``'s output.

    python tools/make_slow_comodulation_figure.py --run <folder>
    python tools/make_slow_comodulation_figure.py --run <folder> --also docs/learned/slow_comodulation

Writes into ``<darkroom>/bugarach/2026-09-17-slow-comodulation/`` unless ``--out`` names a folder:

* ``fig1_two_kinds.png`` — synthetic: planted events, shared modulation on a 20 s timescale and
  shared drift on a 5-minute one, as rasters and as cross-correlograms.
* ``fig2_the_surrogates.png`` — a schematic of the three surrogates on four onset trains.
* ``fig3_what_the_surrogates_remove.png`` — synthetic worlds and the benchmark generator against
  every arm, as correlograms and as count-variance ratios.
* ``fig4_how_much_the_count_varies.png`` — per dataset, the count-variance ratio as recorded and
  under each arm, raw and with a straight-line trend removed. Pooled; no raster.
* ``fig5_recordings.png`` — the cross-correlograms of the three datasets. Pooled; no raster.
* ``fig6_by_group.png`` — the lab streams split by group.
* ``one_recording.png`` — **darkroom only, never copied by ``--also``**: one lab fast recording's
  population count per minute, as recorded, rigid-shifted and circularly shifted. Derived from a
  single real recording, so it stays out of the repository (FOUNDATIONS §5).

Panels carry a letter tag in their corner; identity and counts live in axis labels and captions,
not in titles over the plots. Nothing is drawn on a raster: marks that belong to one sit in a lane
above it and point down.
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
from matplotlib.patches import Patch  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
from bugarach.time_axis import label as tlabel  # noqa: E402
from bugarach.time_axis import ticks as tticks  # noqa: E402

FOLDER = "2026-09-17-slow-comodulation"
DARKROOM_ONLY = ("one_recording.png",)
plt.rcParams.update({"font.size": 13, "axes.labelsize": 13, "xtick.labelsize": 12,
                     "ytick.labelsize": 12, "legend.fontsize": 12})

ARM = {  # colour, line style, width, marker, label
    "real": ("#000000", "-", 2.6, "o", "as recorded"),
    "circular": ("#969696", "-", 1.5, "s", "circular shift (the null)"),
    "block_120": ("#7b3294", "-", 1.8, "D", "block control"),
    "rigid_1.6": ("#6baed6", "-", 1.8, "v", "rigid shift, J = 1.6 s"),
    "rigid_10": ("#2171b5", "-", 1.8, "v", "rigid shift, J = 10 s"),
    "rigid_20": ("#08306b", (0, (5, 2)), 2.0, "v", "rigid shift, J = 20 s"),
    "minus_coact": ("#238b45", "-", 1.8, "^", "CoactDetect episodes removed"),
    "minus_coact_block_120": ("#238b45", (0, (1, 1.5)), 2.2, "^",
                              "episodes removed, then block control"),
}
WORLD = {  # colour, style, label
    "sim_events": ("#d95f02", "-", "planted events"),
    "shared_20s": ("#e7298a", "-", "shared modulation, 20 s"),
    "drift_5min": ("#8c510a", "-", "shared drift, 5 minutes"),
    "shallow_1min": ("#e6ab02", "-", "shallow shared modulation, 1 minute"),
    "sim_background": ("#636363", (0, (1, 1.5)), "generator background only"),
    "sim_hot_window": ("#1b9e77", "-", "promiscuity probe only"),
    "benchmark": ("#e41a1c", (0, (5, 2)), "benchmark generator, whole spec"),
}
DATASET = {"steps_excluded/fast": "lab, fast stream", "steps_excluded/slow": "lab, slow stream",
           "cossart/events": "Dard et al. 2022"}
GROUP_INK = {"DI": "#17becf", "MALE": "#bcbd22", "ORX": "#c49c94", "OVX": "#ff9896"}
GROUP_ORDER = ("DI", "MALE", "ORX", "OVX")
LAG_TICKS = (0.3, 1.0, 5.0, 15.0, 60.0, 300.0)
BAND_HATCH = {"minus_coact": "////"}


def tag(ax, letter, x=0.012, y=0.975):
    ax.text(x, y, letter, transform=ax.transAxes, ha="left", va="top", fontsize=15,
            fontweight="bold", bbox=dict(boxstyle="square,pad=0.12", fc="white", ec="none",
                                         alpha=0.85), zorder=10)


def centres(R):
    e = np.asarray(R["lag_edges_sec"])
    return np.sqrt(np.maximum(e[:-1], 0.15) * e[1:])


def lag_axis(ax, R, xlabel=True):
    ax.set_xscale("log")
    ax.set_xlim(0.13, R["lag_edges_sec"][-1] * 1.05)
    ax.set_xticks(LAG_TICKS, [tlabel(t) for t in LAG_TICKS] if xlabel else [""] * len(LAG_TICKS))
    ax.xaxis.set_minor_locator(matplotlib.ticker.NullLocator())
    ax.axhline(0, color="0.8", lw=0.8, zorder=0)
    if xlabel:
        ax.set_xlabel("lag between two ROIs' onsets (log scale;\nleftmost point holds lags 0–0.3 s)")


def curve(ax, R, S, arm, band=False):
    if arm not in S["arms"]:
        return
    c, ls, lw, _, _ = ARM[arm]
    v = S["arms"][arm]
    ax.plot(centres(R), v["excess"], color=c, ls=ls, lw=lw, zorder=3 if arm == "real" else 2)
    if band:
        if arm in BAND_HATCH:
            ax.fill_between(centres(R), v["lo"], v["hi"], facecolor="none", edgecolor=c,
                            hatch=BAND_HATCH[arm], lw=0, alpha=0.6)
        else:
            ax.fill_between(centres(R), v["lo"], v["hi"], color=c, alpha=0.15, lw=0)


def off_scale(ax, R, S, arms, hi):
    """A small down-pointing mark at the top edge above any lag bin where a curve leaves the view."""
    x = centres(R)
    over = np.zeros(len(x), bool)
    for arm in arms:
        if arm in S["arms"]:
            over |= np.asarray(S["arms"][arm]["excess"]) > hi
    if over.any():
        ax.plot(x[over], np.full(over.sum(), hi), marker="v", ls="none", color="0.45", ms=6,
                clip_on=False, zorder=5)


def arm_handles(arms, band_arms=()):
    h = [Line2D([], [], color=ARM[a][0], ls=ARM[a][1], lw=ARM[a][2], label=ARM[a][4]) for a in arms]
    for a in band_arms:
        if a in BAND_HATCH:
            h.append(Patch(facecolor="white", edgecolor=ARM[a][0], hatch=BAND_HATCH[a],
                           label=f"95 % interval over mice, {ARM[a][4]}"))
        else:
            h.append(Patch(color=ARM[a][0], alpha=0.15, label=f"95 % interval over mice, {ARM[a][4]}"))
    return h


# -- Figure 1: two kinds of shared activity ----------------------------------------------------

def _raster(ax, trains, dt, t0, t1):
    for r, t in enumerate(trains):
        ts = np.asarray(t) * dt
        ts = ts[(ts >= t0) & (ts < t1)]
        ax.vlines(ts, r + 0.12, r + 0.88, color="k", lw=1.1)
    pad = 0.01 * (t1 - t0)
    ax.set_xlim(t0 - pad, t1 + pad)
    ax.set_ylim(-0.3, len(trains) + 0.3)
    ax.set_yticks([])


def _lit_share(ax, trains, dt, t1, bin_sec=10.0):
    from bugarach.detectors._shared import distinct_coact
    edges = np.arange(0.0, t1 + bin_sec, bin_sec)
    lit = distinct_coact([np.asarray(t) * dt for t in trains], edges) / len(trains)
    ax.step(edges[:-1], lit, where="post", color="k", lw=1.0)
    ax.set_xlim(0, t1 * 1.01)


def _busiest(trains, dt, L, zoom, within):
    from bugarach.detectors._shared import distinct_coact
    edges = np.arange(0.0, L * dt + within, within)
    lit = distinct_coact([np.asarray(t) * dt for t in trains], edges)
    centre = edges[int(np.argmax(lit))] + within / 2
    return float(np.clip(np.floor((centre - zoom / 2) / 5) * 5, 0, L * dt - zoom))


def _time_ticks(ax, t0, t1):
    tk = [t for t in tticks(0.0, t1 - t0) if t <= t1 - t0 + 1e-9]
    ax.set_xticks([t0 + t for t in tk], [tlabel(t) for t in tk])


def fig1(R, out):
    syn = R["synthetic"]
    worlds = ("sim_events", "shared_20s", "drift_5min")
    fig = plt.figure(figsize=(12, 13.2))
    gs = fig.add_gridspec(4, 3, height_ratios=(0.8, 1.6, 2.1, 2.1), hspace=0.55, wspace=0.14)
    zoom = 60.0
    for col, world in enumerate(worlds):
        row = next(r for r in syn[world]["rows"] if r["raster"] is not None)
        dt, L = row["dt"], row["L"]
        span = min(L * dt, 1200.0)
        a = fig.add_subplot(gs[0, col])
        _lit_share(a, row["raster"], dt, span)
        a.set_ylim(0, 0.5)
        _time_ticks(a, 0.0, span)
        a.set_xlabel("time (first 20 minutes)", labelpad=1)
        a.set_ylabel(f"{WORLD[world][2]}\nshare lit per 10 s", fontsize=11, color=WORLD[world][0])
        if col:
            a.set_yticklabels([])
        tag(a, "ABC"[col])
        s0 = _busiest(row["raster"], dt, L, zoom, 2.0 if world == "sim_events" else zoom)
        b = fig.add_subplot(gs[1, col])
        _raster(b, row["raster"], dt, s0, s0 + zoom)
        _time_ticks(b, s0, s0 + zoom)
        b.set_xlabel(f"1-minute zoom from {tlabel(round(s0))}", labelpad=1)
        b.set_ylabel(f"{WORLD[world][2]}\n{len(row['raster'])} ROIs", fontsize=11,
                     color=WORLD[world][0])
        tag(b, "DEF"[col], x=-0.001, y=1.12)
    x = centres(R)
    for r, (scale, letter) in enumerate((("log", "G"), ("linear", "H"))):
        ax = fig.add_subplot(gs[2 + r, :])
        for world in ("sim_background", "sim_events", "shared_20s", "drift_5min"):
            c, ls, lab = WORLD[world]
            ax.plot(x, syn[world]["summary"]["arms"]["real"]["excess"], color=c, ls=ls, lw=2.2,
                    label=lab)
        ax.axhline(0, color="0.8", lw=0.8, zorder=0)
        if scale == "log":
            lag_axis(ax, R)
        else:
            ax.set_xlim(0, 125)
            tk = tticks(0, 120)
            ax.set_xticks(tk, [tlabel(t) for t in tk])
            ax.set_xlabel("lag between two ROIs' onsets (linear scale: equal widths are equal "
                          "durations)")
        ax.set_ylim(-0.15, 0.9)
        ax.set_ylabel("excess coincidence\n(observed ÷ chance − 1)")
        tag(ax, letter)
        if r == 0:
            ax.legend(frameon=False, loc="upper right")
    fig.subplots_adjust(left=0.1, right=0.98, top=0.97, bottom=0.05)
    fig.savefig(out / "fig1_two_kinds.png", dpi=150)
    plt.close(fig)


# -- Figure 2: the surrogates, drawn -----------------------------------------------------------

def fig2(R, out):
    """Schematic on fixed numbers: four onset trains over 4 minutes sharing one aligned event near
    1m40s, and what each surrogate does to them."""
    T, block = 240.0, 120.0
    base = [np.array([20.0, 100.0, 170.0]), np.array([55.0, 100.4, 210.0]),
            np.array([8.0, 99.7, 140.0, 228.0]), np.array([100.2, 190.0])]
    rigid_off = [9.0, -12.0, 15.0, 6.0]          # ROI 3's last onset leaves the window
    circ_off = [74.0, 150.0, 30.0, 205.0]
    blk_off = [[40.0, 85.0], [100.0, 20.0], [65.0, 5.0], [90.0, 44.0]]

    def blocky(t, offs):
        parts = []
        for a, o in zip((0.0, block), offs):
            s = t[(t >= a) & (t < a + block)]
            parts.append((s - a + o) % block + a)
        return np.sort(np.concatenate(parts))

    rows = [("as recorded", base, None),
            ("rigid shift\n(J = 20 s)", [np.sort(t + o) for t, o in zip(base, rigid_off)], "drop"),
            ("circular shift", [np.sort((t + o) % T) for t, o in zip(base, circ_off)], None),
            ("block control", [blocky(t, o) for t, o in zip(base, blk_off)], "block")]
    fig = plt.figure(figsize=(12, 8.4))
    gs = fig.add_gridspec(5, 1, height_ratios=(1, 1, 1, 0.22, 1), hspace=0.32)
    axes = [fig.add_subplot(gs[i]) for i in (0, 1, 2, 4)]
    lane = fig.add_subplot(gs[3], sharex=axes[3])
    for i, (ax, (lab, trains, note)) in enumerate(zip(axes, rows)):
        dropped = []
        for r, t in enumerate(trains):
            keep = (t >= 0) & (t < T)
            ax.vlines(t[keep], r + 0.12, r + 0.88, color="k", lw=2.2)
            dropped += [(x, r) for x in t[~keep]]
        ax.set_ylim(-0.2, 4.2)
        ax.set_yticks([0.5, 1.5, 2.5, 3.5], ["ROI 1", "ROI 2", "ROI 3", "ROI 4"], fontsize=11)
        ax.set_xlim(-4, T + 4)
        ax.set_ylabel(lab, fontsize=12, rotation=0, ha="right", va="center", labelpad=58)
        tag(ax, "ABCD"[i], x=-0.001, y=1.2)
        if i < 3:
            ax.set_xticklabels([])
        if note == "drop" and dropped:
            ax.text(1.0, 1.02, f"{len(dropped)} onset pushed past 4m is dropped", transform=ax.transAxes,
                    ha="right", va="bottom", fontsize=11, color="0.3")
    lane.set_ylim(0, 1)
    lane.axis("off")
    lane.plot([block], [0.35], marker="v", color="#7b3294", ms=11, clip_on=False)
    lane.text(block + 3, 0.35, "2-minute block edge", va="center", fontsize=11, color="#7b3294")
    tk = tticks(0, T)
    axes[-1].set_xticks(tk, [tlabel(t) for t in tk])
    axes[-1].set_xlabel("time (schematic)")
    fig.subplots_adjust(left=0.2, right=0.98, top=0.95, bottom=0.08)
    fig.savefig(out / "fig2_the_surrogates.png", dpi=150)
    plt.close(fig)


# -- Figure 3: what the surrogates remove, where the answer is known ---------------------------

def fig3(R, out):
    syn = R["synthetic"]
    worlds = ("sim_events", "shared_20s", "drift_5min", "shallow_1min", "benchmark")
    arms = ("circular", "rigid_1.6", "rigid_10", "rigid_20", "block_120",
            "minus_coact_block_120", "real")
    fig = plt.figure(figsize=(12.5, 15))
    gs = fig.add_gridspec(4, 2, height_ratios=(1, 1, 1, 1.05), hspace=0.42, wspace=0.28)
    for i, world in enumerate(worlds):
        ax = fig.add_subplot(gs[i // 2, i % 2])
        S = syn[world]["summary"]
        for arm in arms:
            curve(ax, R, S, arm)
        lag_axis(ax, R, xlabel=(i >= 3))
        top = 1.75 if world == "benchmark" else (0.25 if world == "shallow_1min" else 0.9)
        low = -0.05 if world == "shallow_1min" else -0.15
        ax.set_ylim(low, top)
        off_scale(ax, R, S, arms, top)
        ax.set_ylabel(f"excess coincidence, y to {top:g}\n{WORLD[world][2]}", fontsize=12)
        tag(ax, "ABCDE"[i])
    # F: count-variance ratios at 1 minute for every world and arm
    ax = fig.add_subplot(gs[2, 1])
    bar_arms = ("real", "rigid_20", "block_120", "minus_coact_block_120")
    ws = worlds + ("sim_background",)
    for j, arm in enumerate(bar_arms):
        for k, world in enumerate(ws):
            v = syn[world]["summary"]["arms"].get(arm)
            if not v:
                continue
            ax.plot(k + (j - 1.5) * 0.18, v["var_ratio"][-1], marker=ARM[arm][3], color=ARM[arm][0],
                    ms=8, ls="none")
    ax.axhline(1, color="0.5", lw=1, ls=(0, (4, 2)))
    ax.set_yscale("log")
    ax.set_yticks([0.5, 1, 2, 5, 10], ["0.5", "1", "2", "5", "10"])
    ax.yaxis.set_minor_locator(matplotlib.ticker.NullLocator())
    ax.set_xticks(range(len(ws)), ["events", "20 s", "5 min", "shallow\n1 min", "bench-\nmark",
                                   "back-\nground"], fontsize=11)
    ax.set_ylabel("count variance ÷ independent,\n1-minute bins (log scale)", fontsize=12)
    tag(ax, "F")
    h = arm_handles(arms)
    h += [Line2D([], [], color=ARM[a][0], marker=ARM[a][3], ls="none", ms=8,
                 label=f"F: {ARM[a][4]}") for a in bar_arms]
    h.append(Line2D([], [], color="0.5", ls=(0, (4, 2)), label="F: independent ROIs (= 1)"))
    h.append(Line2D([], [], color="0.45", marker="v", ls="none", ms=6, label="curve above the view"))
    lax = fig.add_subplot(gs[3, :])
    lax.axis("off")
    lax.legend(handles=h, loc="upper center", ncol=2, frameon=False)
    fig.subplots_adjust(left=0.1, right=0.98, top=0.98, bottom=0.02)
    fig.savefig(out / "fig3_what_the_surrogates_remove.png", dpi=150)
    plt.close(fig)


# -- Figure 4: the count-variance ratio on the recordings --------------------------------------

def fig4(R, out):
    names = [n for n in DATASET if n in R["folders"]]
    arms = ("real", "rigid_20", "block_120", "minus_coact_block_120")
    widths = R["var_bin_sec"]
    fig, axes = plt.subplots(1, len(names), figsize=(12.5, 5.6), sharey=True)
    for i, (ax, name) in enumerate(zip(axes, names)):
        S = R["folders"][name]["summary"]
        for j, arm in enumerate(arms):
            v = S["arms"].get(arm)
            if not v:
                continue
            x = np.arange(len(widths)) + (j - 1.5) * 0.19
            y = np.asarray(v["var_ratio"])
            lo, hi = np.asarray(v["var_lo"]), np.asarray(v["var_hi"])
            ax.errorbar(x, y, yerr=[y - lo, hi - y], fmt=ARM[arm][3], color=ARM[arm][0], ms=8,
                        elinewidth=1.4, capsize=3)
            yd = np.asarray(v["var_ratio_detrended"])
            ax.plot(x + 0.07, yd, marker=ARM[arm][3], mfc="white", mec=ARM[arm][0], ls="none",
                    ms=7, mew=1.6)
        ax.axhline(1, color="0.5", lw=1, ls=(0, (4, 2)))
        ax.set_yscale("log")
        ax.set_ylim(0.7, 25)
        ax.set_yticks([1, 2, 5, 10, 20], ["1", "2", "5", "10", "20"])
        ax.yaxis.set_minor_locator(matplotlib.ticker.NullLocator())
        ax.set_xticks(range(len(widths)), [tlabel(t) for t in widths])
        ax.set_xlim(-0.6, len(widths) - 0.4)
        ax.set_xlabel(f"bin width\n{DATASET[name]}\n{S['n_recordings']} recordings, "
                      f"{S['n_mice']} mice")
        tag(ax, "ABC"[i])
    axes[0].set_ylabel("population count variance ÷ that of\nindependent ROIs (log scale)")
    h = [Line2D([], [], color=ARM[a][0], marker=ARM[a][3], ls="none", ms=8,
                label=ARM[a][4] + (" (lab only)" if a == "minus_coact_block_120" else ""))
         for a in arms]
    h += [Line2D([], [], color="0.3", marker="o", mfc="white", ls="none", ms=7, mew=1.6,
                 label="hollow: straight-line trend removed"),
          Line2D([], [], color="0.35", lw=1.4, label="whisker: 95 % interval over mice"),
          Line2D([], [], color="0.5", ls=(0, (4, 2)), label="independent ROIs (= 1)")]
    fig.legend(handles=h, loc="lower center", ncol=3, frameon=False)
    fig.subplots_adjust(left=0.1, right=0.99, top=0.97, bottom=0.42, wspace=0.08)
    fig.savefig(out / "fig4_how_much_the_count_varies.png", dpi=150)
    plt.close(fig)


# -- Figure 5: the recordings' correlograms ----------------------------------------------------

ZOOM = {"steps_excluded/fast": (-0.15, 0.35), "steps_excluded/slow": (-0.8, 0.8),
        "cossart/events": (-0.12, 0.12)}


def fig5(R, out):
    names = [n for n in DATASET if n in R["folders"]]
    arms = ("circular", "rigid_1.6", "rigid_10", "rigid_20", "block_120", "minus_coact",
            "minus_coact_block_120", "real")
    fig = plt.figure(figsize=(12.5, 12.5))
    gs = fig.add_gridspec(3, len(names), height_ratios=(1, 1.3, 0.62), hspace=0.2, wspace=0.42)
    for c, name in enumerate(names):
        S = R["folders"][name]["summary"]
        for r in range(2):
            ax = fig.add_subplot(gs[r, c])
            for arm in arms:
                curve(ax, R, S, arm, band=arm in ("real", "minus_coact"))
            lag_axis(ax, R, xlabel=(r == 1))
            tag(ax, "ABCDEF"[r * len(names) + c])
            if r == 0:
                ax.set_ylabel(f"excess coincidence, full range\n{DATASET[name]}", fontsize=12)
            else:
                lo, hi = ZOOM[name]
                ax.set_ylim(lo, hi)
                off_scale(ax, R, S, arms, hi)
                ax.set_ylabel(f"{DATASET[name]}, zoomed to {hi:g}\n{S['n_recordings']} recordings, "
                              f"{S['n_mice']} mice", fontsize=12)
    lax = fig.add_subplot(gs[2, :])
    lax.axis("off")
    h = arm_handles(arms, band_arms=("real", "minus_coact"))
    h.append(Line2D([], [], color="0.45", marker="v", ls="none", ms=6, label="curve above the view"))
    lax.legend(handles=h, loc="upper center", ncol=2, frameon=False)
    fig.subplots_adjust(left=0.08, right=0.99, top=0.98, bottom=0.02)
    fig.savefig(out / "fig5_recordings.png", dpi=150)
    plt.close(fig)


# -- Figure 6: by group ------------------------------------------------------------------------

def fig6(R, out):
    names = [n for n in ("steps_excluded/fast", "steps_excluded/slow") if n in R["folders"]]
    if not names:
        return
    fig = plt.figure(figsize=(12.5, 11.5))
    gs = fig.add_gridspec(3, len(names), height_ratios=(1, 1, 0.55), hspace=0.22, wspace=0.26)
    x = centres(R)
    for c, name in enumerate(names):
        G = R["folders"][name]["by_group"]
        for r, arm in enumerate(("real", "minus_coact_block_120")):
            ax = fig.add_subplot(gs[r, c])
            vals = []
            for g in GROUP_ORDER:
                if g not in G:
                    continue
                v = G[g]["arms"][arm]
                ax.plot(x, v["excess"], color=GROUP_INK[g], lw=2.4)
                ax.plot(x, v["excess_equal_mice"], color=GROUP_INK[g], lw=1.4, ls=(0, (2, 2)))
                vals += [e for e, lag in zip(v["excess"], x) if lag > 2]
            lag_axis(ax, R, xlabel=(r == 1))
            hi = 0.8 if r == 0 else max(0.35, float(np.nanmax(vals)) * 1.3)
            lo = -0.8 if r == 0 else -0.1
            ax.set_ylim(lo, hi)
            for g in GROUP_ORDER:
                if g in G:
                    off_scale(ax, R, G[g], [arm], hi)
            tag(ax, "ABCD"[r * 2 + c])
            ax.set_ylabel(f"excess coincidence, y to {hi:.2g}\n{DATASET[name]}, "
                          f"{'as recorded' if arm == 'real' else 'episodes removed + block control'}",
                          fontsize=11)
    h = []
    for g in GROUP_ORDER:
        if g not in R["folders"][names[0]]["by_group"]:
            continue
        parts = []
        for name in names:
            S = R["folders"][name]["by_group"].get(g)
            if S:
                parts.append(f"{100 * S['top_mouse_share_of_pairs']:.0f} % "
                             f"{'fast' if name.endswith('fast') else 'slow'}")
        S0 = R["folders"][names[0]]["by_group"][g]
        h.append(Line2D([], [], color=GROUP_INK[g], lw=2.4,
                        label=f"{g} · {S0['n_recordings']} recordings, {S0['n_mice']} mice; "
                              f"heaviest mouse holds {', '.join(parts)} of pairs"))
    h += [Line2D([], [], color="0.3", lw=2.4, label="pooled over recordings"),
          Line2D([], [], color="0.3", lw=1.4, ls=(0, (2, 2)), label="each mouse weighted equally"),
          Line2D([], [], color="0.45", marker="v", ls="none", ms=6, label="curve above the view")]
    lax = fig.add_subplot(gs[2, :])
    lax.axis("off")
    lax.legend(handles=h, loc="upper center", ncol=1, frameon=False)
    fig.subplots_adjust(left=0.1, right=0.99, top=0.98, bottom=0.02)
    fig.savefig(out / "fig6_by_group.png", dpi=150)
    plt.close(fig)


# -- darkroom only: one real recording ---------------------------------------------------------

def one_recording(R, out):
    F = R["folders"].get("steps_excluded/fast")
    if not F:
        return
    rows = [r for r in F["rows"] if "counts_per_minute" in r]
    if not rows:
        return
    ratio = []
    for r in rows:
        c = r["counts_per_minute"]
        vc = np.var(c["circular"], ddof=1)
        ratio.append(np.var(c["real"], ddof=1) / vc if vc > 0 else np.nan)
    ratio = np.asarray(ratio)
    i = int(np.nanargmin(np.abs(ratio - np.nanmedian(ratio))))
    c = rows[i]["counts_per_minute"]
    fig, ax = plt.subplots(figsize=(12, 4.6))
    m = np.arange(len(c["real"])) + 0.5
    ax.plot(m, c["real"], color=ARM["real"][0], lw=2.6, marker="o", label="as recorded")
    ax.plot(m, c["rigid"], color=ARM["rigid_20"][0], lw=2.0, ls=ARM["rigid_20"][1],
            label="one rigid shift, J = 20 s")
    ax.plot(m, c["circular"], color=ARM["circular"][0], lw=1.8, label="one circular shift")
    tk = [t for t in tticks(0, len(c["real"]) * 60.0)]
    ax.set_xticks([t / 60.0 for t in tk], [tlabel(t) for t in tk])
    ax.set_xlabel("time in the trimmed baseline window (1-minute bins)")
    ax.set_ylabel(f"onsets per minute, all {rows[i]['n_roi']} ROIs\none lab fast-stream recording")
    ax.legend(frameon=False, loc="upper left")
    ax.set_title("")
    fig.text(0.99, 0.01, f"the recording nearest the median per-recording 1-minute ratio "
             f"({ratio[i]:.2f}, this draw)", ha="right", fontsize=10, color="0.35")
    fig.subplots_adjust(left=0.1, right=0.99, top=0.96, bottom=0.2)
    fig.savefig(out / "one_recording.png", dpi=150)
    plt.close(fig)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--run", required=True, type=Path, help="folder holding results.json")
    ap.add_argument("--out", type=Path, default=None, help=f"default: <darkroom>/bugarach/{FOLDER}")
    ap.add_argument("--also", type=Path, default=None,
                    help="also copy the figures here (repo); never the darkroom-only ones")
    a = ap.parse_args(argv)
    if a.out is None:
        from bugarach.paths import darkroom, unresolved_message
        a.out = darkroom(FOLDER, create=True)
        if a.out is None:
            raise SystemExit(unresolved_message("--out"))
    a.out.mkdir(parents=True, exist_ok=True)
    R = json.loads((a.run / "results.json").read_text())
    for old in list(a.out.glob("fig*.png")) + [a.out / n for n in DARKROOM_ONLY]:
        if old.exists():
            old.unlink()
    fig1(R, a.out)
    fig2(R, a.out)
    fig3(R, a.out)
    if R["folders"]:
        fig4(R, a.out)
        fig5(R, a.out)
        fig6(R, a.out)
        one_recording(R, a.out)
    made = sorted(a.out.glob("fig*.png")) + [a.out / n for n in DARKROOM_ONLY
                                             if (a.out / n).exists()]
    if a.also:
        a.also.mkdir(parents=True, exist_ok=True)
        for old in a.also.glob("fig*.png"):
            old.unlink()
        for p in made:
            if p.name not in DARKROOM_ONLY:
                shutil.copy2(p, a.also / p.name)
    for p in made:
        print(p)


if __name__ == "__main__":
    main()
