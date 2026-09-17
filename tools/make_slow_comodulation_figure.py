#!/usr/bin/env python3
"""Draw the slow co-modulation explainer's figures from ``measure_slow_comodulation.py``'s output.

    python tools/make_slow_comodulation_figure.py --run <folder>
    python tools/make_slow_comodulation_figure.py --run <folder> --also docs/learned/slow_comodulation

Writes into ``<darkroom>/bugarach/2026-09-17-slow-comodulation/`` unless ``--out`` names a folder:

* ``fig1_how_much_the_count_swings.png`` — per dataset, how much more the population onset
  count swings than independent ROIs would make it, at 1 s, 10 s and 60 s, as recorded and under
  each surrogate. Pooled over recordings; no raster.
* ``fig2_three_kinds.png`` — synthetic: planted events, shared modulation on a 20 s timescale and
  shared drift on a 5-minute one, as rasters and as cross-correlograms.
* ``fig3_the_surrogates.png`` — a schematic of the three surrogates on four synthetic onset trains.
* ``fig4_what_the_surrogates_remove.png`` — synthetic: each world, and the benchmark generator,
  against every surrogate.
* ``fig5_recordings.png`` — the cross-correlograms of the three datasets. Pooled; no raster.
* ``fig6_by_group.png`` — the lab streams split by group, pooled and with mice weighted equally.

None holds a real raster (FOUNDATIONS §5). Panels carry a letter tag; identity and counts are in
the axis labels and the captions, not in titles over the plots.
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

FOLDER = "2026-09-17-slow-comodulation"
plt.rcParams.update({"font.size": 11, "axes.labelsize": 11, "xtick.labelsize": 10,
                     "ytick.labelsize": 10, "legend.fontsize": 10})

ARM = {  # colour, line style, width, label
    "real": ("#000000", "-", 2.4, "as recorded"),
    "circular": ("#969696", "-", 1.4, "circular shift (the null)"),
    "block_120": ("#7b3294", "-", 1.6, "block control (circular shift within 2-minute blocks)"),
    "rigid_1.6": ("#6baed6", "-", 1.6, "rigid shift, J = 1.6 s"),
    "rigid_10": ("#2171b5", "-", 1.6, "rigid shift, J = 10 s"),
    "rigid_20": ("#08306b", (0, (5, 2)), 1.8, "rigid shift, J = 20 s"),
    "minus_coact": ("#238b45", "-", 1.6, "CoactDetect episodes removed"),
    "minus_coact_block_120": ("#238b45", (0, (1, 1.5)), 2.0,
                              "CoactDetect episodes removed, then block control"),
}
ARM_ORDER = ("circular", "rigid_1.6", "rigid_10", "rigid_20", "block_120", "minus_coact",
             "minus_coact_block_120", "real")
WORLD = {  # colour, style, label
    "sim_events": ("#d95f02", "-", "planted events (generator, no hot window)"),
    "shared_20s": ("#e7298a", "-", "shared modulation, 20 s timescale"),
    "drift_5min": ("#8c510a", "-", "shared drift, 5-minute timescale"),
    "sim_background": ("#636363", (0, (1, 1.5)), "generator background only"),
    "benchmark": ("#e41a1c", (0, (5, 2)), "benchmark generator, whole spec"),
}
DATASET = {"steps_excluded/fast": "lab, fast stream", "steps_excluded/slow": "lab, slow stream",
           "cossart/events": "Dard et al. 2022 dataset", "benchmark": "benchmark generator"}
GROUP_INK = {"DI": "#1b9e77", "MALE": "#e6ab02", "ORX": "#a65628", "OVX": "#e7298a"}
LAG_TICKS = (0.3, 1.0, 5.0, 15.0, 60.0, 300.0)


def tag(ax, letter):
    ax.text(0.012, 0.975, letter, transform=ax.transAxes, ha="left", va="top",
            fontsize=13, fontweight="bold",
            bbox=dict(boxstyle="square,pad=0.15", fc="white", ec="none", alpha=0.85))


def centres(R):
    e = np.asarray(R["lag_edges_sec"])
    return np.sqrt(np.maximum(e[:-1], 0.15) * e[1:])


def lag_axis(ax, R, xlabel=True):
    ax.set_xscale("log")
    ax.set_xlim(0.13, R["lag_edges_sec"][-1])
    ax.set_xticks(LAG_TICKS, [tlabel(t) for t in LAG_TICKS] if xlabel else [""] * len(LAG_TICKS))
    ax.xaxis.set_minor_locator(matplotlib.ticker.NullLocator())
    ax.axhline(0, color="0.8", lw=0.8, zorder=0)
    if xlabel:
        ax.set_xlabel("lag between two ROIs' onsets (log scale)")


def curve(ax, R, S, arm, band=False):
    if arm not in S["arms"]:
        return
    c, ls, lw, _ = ARM[arm]
    v = S["arms"][arm]
    ax.plot(centres(R), v["excess"], color=c, ls=ls, lw=lw)
    if band:
        ax.fill_between(centres(R), v["lo"], v["hi"], color=c, alpha=0.18, lw=0)


def arm_legend(fig, arms, band_arms=(), ncol=3, y=0.0):
    h = [Line2D([], [], color=ARM[a][0], ls=ARM[a][1], lw=ARM[a][2], label=ARM[a][3])
         for a in arms]
    h += [Patch(color=ARM[a][0], alpha=0.18, label=f"95 % interval over mice, {ARM[a][3]}")
          for a in band_arms]
    fig.legend(handles=h, loc="lower center", ncol=ncol, frameon=False, bbox_to_anchor=(0.5, y))


def symlog_axis(ax, linthresh, ticks):
    ax.set_yscale("symlog", linthresh=linthresh, linscale=1.2)
    ax.set_yticks(ticks, [f"{t:g}" for t in ticks])
    ax.yaxis.set_minor_locator(matplotlib.ticker.NullLocator())


# -- Figure 1 ---------------------------------------------------------------------------------

def fig1(R, out):
    names = [n for n in ("steps_excluded/fast", "steps_excluded/slow", "cossart/events")
             if n in R["folders"]] + ["benchmark"]
    arms = ("real", "rigid_20", "block_120", "minus_coact_block_120")
    fig, axes = plt.subplots(1, len(names), figsize=(12, 4.6), sharey=True)
    widths = R["var_bin_sec"]
    for i, (ax, name) in enumerate(zip(axes, names)):
        S = (R["synthetic"]["benchmark"]["summary"] if name == "benchmark"
             else R["folders"][name]["summary"])
        present = [a for a in arms if a in S["arms"]]
        w = 0.8 / len(arms)
        for j, arm in enumerate(arms):
            if arm not in S["arms"]:
                continue
            v = S["arms"][arm]
            x = np.arange(len(widths)) + (j - (len(arms) - 1) / 2) * w
            vr = np.asarray(v["var_ratio"])
            ax.bar(x, vr, width=w * 0.92, color=ARM[arm][0], alpha=0.85 if arm != "real" else 1,
                   hatch="///" if arm == "minus_coact_block_120" else None,
                   edgecolor="white", lw=0)
            if name != "benchmark":
                lo, hi = np.asarray(v["var_lo"]), np.asarray(v["var_hi"])
                ax.errorbar(x, vr, yerr=[vr - lo, hi - vr], fmt="none", ecolor="0.35",
                            elinewidth=1, capsize=2)
        ax.axhline(1, color="0.5", lw=1, ls=(0, (4, 2)))
        ax.set_yscale("log")
        ax.set_yticks([1, 2, 5, 10, 20], ["1", "2", "5", "10", "20"])
        ax.yaxis.set_minor_locator(matplotlib.ticker.NullLocator())
        ax.set_xticks(range(len(widths)), [tlabel(t) for t in widths])
        n = S["n_recordings"]
        unit = "mice" if name != "benchmark" else "generator seeds"
        ax.set_xlabel(f"bin width\n{DATASET[name]}\n{n} recordings"
                      + (f", {S['n_mice']} {unit}" if name != "benchmark" else ""))
        tag(ax, "ABCD"[i])
        if len(present) < len(arms):
            ax.text(0.98, 0.975, "no CoactDetect arm", transform=ax.transAxes, ha="right",
                    va="top", fontsize=9, color="0.35")
    axes[0].set_ylabel("population count variance ÷ that of\nindependent ROIs (log scale)")
    h = [Patch(color=ARM[a][0], label=ARM[a][3], hatch="///" if a == "minus_coact_block_120"
               else None) for a in arms]
    h.append(Line2D([], [], color="0.5", ls=(0, (4, 2)), label="independent ROIs (= 1)"))
    h.append(Line2D([], [], color="0.35", lw=1, label="95 % interval over mice"))
    fig.legend(handles=h, loc="lower center", ncol=3, frameon=False)
    fig.subplots_adjust(left=0.08, right=0.99, top=0.97, bottom=0.36, wspace=0.08)
    fig.savefig(out / "fig1_how_much_the_count_swings.png", dpi=150)
    plt.close(fig)


# -- Figure 2 ---------------------------------------------------------------------------------

def _raster(ax, trains, dt, t0, t1):
    for r, t in enumerate(trains):
        ts = np.asarray(t) * dt
        ts = ts[(ts >= t0) & (ts < t1)]
        ax.vlines(ts, r + 0.1, r + 0.9, color="k", lw=1.0)
    ax.set_xlim(t0, t1)
    ax.set_ylim(0, len(trains))
    ax.set_yticks([])


def _lit_share(ax, trains, dt, t1, bin_sec=10.0):
    from bugarach.detectors._shared import distinct_coact
    edges = np.arange(0.0, t1 + bin_sec, bin_sec)
    lit = distinct_coact([np.asarray(t) * dt for t in trains], edges) / len(trains)
    ax.step(edges[:-1], lit, where="post", color="k", lw=1.0)
    ax.set_xlim(0, t1)


def _busiest(trains, dt, L, zoom, within):
    """Start of the 1-minute window holding the most ROIs lit together within ``within`` seconds:
    a coincidence for the planted-event world, the busiest minute for the others."""
    from bugarach.detectors._shared import distinct_coact
    edges = np.arange(0.0, L * dt + within, within)
    lit = distinct_coact([np.asarray(t) * dt for t in trains], edges)
    centre = edges[int(np.argmax(lit))] + within / 2
    return float(np.clip(np.floor((centre - zoom / 2) / 5) * 5, 0, L * dt - zoom))


def _ticks(ax, t0, t1, step):
    ticks = np.arange(t0, t1 + 1e-9, step)
    ax.set_xticks(ticks, [tlabel(t - t0) for t in ticks])


def fig2(R, out):
    syn = R["synthetic"]
    worlds = ("sim_events", "shared_20s", "drift_5min")
    fig = plt.figure(figsize=(12, 11))
    gs = fig.add_gridspec(4, 3, height_ratios=(0.75, 1.5, 2.2, 2.2), hspace=0.42, wspace=0.1)
    zoom = 60.0
    for col, world in enumerate(worlds):
        row = next(r for r in syn[world]["rows"] if r["raster"] is not None)
        dt, L = row["dt"], row["L"]
        a = fig.add_subplot(gs[0, col])
        _lit_share(a, row["raster"], dt, L * dt)
        a.set_ylim(0, 0.5)
        _ticks(a, 0, L * dt, 600.0 if L * dt > 1500 else 300.0)
        a.set_xlabel("time in the recording", labelpad=1)
        if col == 0:
            a.set_ylabel("share of ROIs\nlit per 10 s")
        else:
            a.set_yticklabels([])
        tag(a, "ABC"[col])
        s0 = _busiest(row["raster"], dt, L, zoom, 2.0 if world == "sim_events" else zoom)
        b = fig.add_subplot(gs[1, col])
        _raster(b, row["raster"], dt, s0, s0 + zoom)
        _ticks(b, s0, s0 + zoom, 15.0)
        b.set_xlabel(f"1-minute zoom from {tlabel(round(s0))}", labelpad=1)
        tag(b, "DEF"[col])
        if col == 0:
            b.set_ylabel(f"{len(row['raster'])} ROIs")
        c, _, lab = WORLD[world]
        b.text(0.5, 1.02, lab, transform=b.transAxes, ha="center", va="bottom", color=c,
               fontsize=11)
    x = centres(R)
    for r, (scale, letter) in enumerate((("log", "G"), ("linear", "H"))):
        ax = fig.add_subplot(gs[2 + r, :])
        for world in ("sim_background", "sim_events", "shared_20s", "drift_5min"):
            c, ls, lab = WORLD[world]
            v = syn[world]["summary"]["arms"]["real"]["excess"]
            ax.plot(x, v, color=c, ls=ls, lw=2.0, label=lab)
        ax.axhline(0, color="0.8", lw=0.8, zorder=0)
        if scale == "log":
            lag_axis(ax, R)
        else:
            ax.set_xlim(0, 125)
            ticks = [0, 15, 30, 60, 90, 120]
            ax.set_xticks(ticks, [tlabel(t) for t in ticks])
            ax.set_xlabel("lag between two ROIs' onsets (linear scale: equal widths are equal "
                          "durations)")
        ax.set_ylim(-0.15, 0.9)
        ax.set_ylabel(f"excess coincidence\n(observed ÷ chance − 1)")
        tag(ax, letter)
        if r == 0:
            ax.legend(frameon=False, loc="upper right")
    n = syn["sim_events"]["summary"]["n_recordings"]
    fig.subplots_adjust(left=0.08, right=0.99, top=0.98, bottom=0.05)
    fig.savefig(out / "fig2_three_kinds.png", dpi=150)
    plt.close(fig)
    return n


# -- Figure 3 ---------------------------------------------------------------------------------

def fig3(R, out):
    """Schematic: four onset trains over 4 minutes with one aligned event at 100 s, and what each
    surrogate does to them. Drawn from fixed numbers, not from the run."""
    base = [np.array([20.0, 100.0, 170.0]), np.array([55.0, 100.4, 210.0]),
            np.array([8.0, 99.7, 140.0, 230.0]), np.array([100.2, 190.0])]
    T = 240.0
    rigid_off = [9.0, -12.0, 4.0, 15.0]
    circ_off = [70.0, 150.0, 30.0, 200.0]
    block = 120.0
    blk_off = [[40.0, 85.0], [100.0, 20.0], [65.0, 5.0], [90.0, 50.0]]

    def blocky(t, offs):
        out_ = []
        for k, (a, o) in enumerate(zip((0.0, block), offs)):
            s = t[(t >= a) & (t < a + block)]
            out_.append((s - a + o) % block + a)
        return np.concatenate(out_)

    rows = [("as recorded", base),
            ("rigid shift: each ROI's whole train slid by its own offset within ±J; "
             "what leaves the window is dropped",
             [np.sort(t + o)[(t + o >= 0) & (t + o < T)] for t, o in zip(base, rigid_off)]),
            ("circular shift: each ROI's train slid by its own lag, wrapping round the window",
             [np.sort((t + o) % T) for t, o in zip(base, circ_off)]),
            ("block control: the circular shift inside each 2-minute block separately",
             [np.sort(blocky(t, o)) for t, o in zip(base, blk_off)])]
    fig, axes = plt.subplots(len(rows), 1, figsize=(12, 7.2), sharex=True)
    for i, (ax, (lab, trains)) in enumerate(zip(axes, rows)):
        for r, t in enumerate(trains):
            ax.vlines(t, r + 0.12, r + 0.88, color="k", lw=2.0)
        ax.set_ylim(0, len(trains))
        ax.set_yticks([0.5, 1.5, 2.5, 3.5], ["ROI 1", "ROI 2", "ROI 3", "ROI 4"], fontsize=9)
        ax.set_xlim(0, T)
        ax.text(0.0, 1.03, lab, transform=ax.transAxes, ha="left", va="bottom", fontsize=10.5)
        tag(ax, "ABCD"[i])
        if i == 3:
            for x in (block,):
                ax.axvline(x, color="#7b3294", lw=1.2, ls=(0, (3, 2)))
    axes[-1].set_xticks(np.arange(0, T + 1, 30), [tlabel(t) for t in np.arange(0, T + 1, 30)])
    axes[-1].set_xlabel("time (schematic)")
    fig.legend(handles=[Line2D([], [], color="#7b3294", ls=(0, (3, 2)), label="2-minute block edge")],
               loc="lower right", frameon=False)
    fig.subplots_adjust(left=0.07, right=0.99, top=0.95, bottom=0.1, hspace=0.55)
    fig.savefig(out / "fig3_the_surrogates.png", dpi=150)
    plt.close(fig)


# -- Figure 4 ---------------------------------------------------------------------------------

def fig4(R, out):
    syn = R["synthetic"]
    worlds = ("sim_events", "shared_20s", "drift_5min", "benchmark")
    arms = ("circular", "rigid_1.6", "rigid_10", "rigid_20", "block_120", "real")
    fig, axes = plt.subplots(2, 2, figsize=(12, 8.2))
    for i, (ax, world) in enumerate(zip(axes.ravel(), worlds)):
        S = syn[world]["summary"]
        for arm in arms:
            curve(ax, R, S, arm)
        lag_axis(ax, R, xlabel=(i >= 2))
        ax.set_ylim(-0.15, 1.75 if world == "benchmark" else 0.9)
        ax.set_ylabel(f"excess coincidence\n{WORLD[world][2]}")
        tag(ax, "ABCD"[i])
    arm_legend(fig, arms, ncol=3)
    fig.subplots_adjust(left=0.09, right=0.99, top=0.98, bottom=0.2, hspace=0.12, wspace=0.22)
    fig.savefig(out / "fig4_what_the_surrogates_remove.png", dpi=150)
    plt.close(fig)


# -- Figure 5 ---------------------------------------------------------------------------------

ZOOM = {"steps_excluded/fast": (-0.15, 0.35), "steps_excluded/slow": (-0.8, 0.8),
        "cossart/events": (-0.12, 0.12)}


def fig5(R, out):
    names = [n for n in DATASET if n in R["folders"]]
    arms = ("circular", "rigid_1.6", "rigid_10", "rigid_20", "block_120", "minus_coact",
            "minus_coact_block_120", "real")
    fig, axes = plt.subplots(2, len(names), figsize=(12.5, 8.2), squeeze=False,
                             gridspec_kw=dict(height_ratios=(1, 1.3)))
    for c, name in enumerate(names):
        S = R["folders"][name]["summary"]
        for r in range(2):
            ax = axes[r, c]
            for arm in arms:
                curve(ax, R, S, arm, band=arm in ("real", "minus_coact"))
            lag_axis(ax, R, xlabel=(r == 1))
            tag(ax, "ABCDEF"[r * len(names) + c])
        lo, hi = ZOOM[name]
        axes[1, c].set_ylim(lo, hi)
        axes[0, c].set_ylabel(f"excess coincidence\n{DATASET[name]}")
        axes[1, c].set_ylabel(f"excess coincidence, zoomed\n"
                              f"{S['n_recordings']} recordings, {S['n_mice']} mice")
    arm_legend(fig, arms, band_arms=("real", "minus_coact"), ncol=3)
    fig.subplots_adjust(left=0.07, right=0.99, top=0.98, bottom=0.2, hspace=0.12, wspace=0.34)
    fig.savefig(out / "fig5_recordings.png", dpi=150)
    plt.close(fig)


# -- Figure 6 ---------------------------------------------------------------------------------

def fig6(R, out):
    names = [n for n in ("steps_excluded/fast", "steps_excluded/slow") if n in R["folders"]]
    if not names:
        return
    fig, axes = plt.subplots(2, len(names), figsize=(12, 8.2), squeeze=False)
    x = centres(R)
    for c, name in enumerate(names):
        G = R["folders"][name]["by_group"]
        for r, arm in enumerate(("real", "minus_coact_block_120")):
            ax = axes[r, c]
            for g, S in G.items():
                v = S["arms"][arm]
                ax.plot(x, v["excess"], color=GROUP_INK.get(g, "k"), lw=2.0)
                ax.plot(x, v["excess_equal_mice"], color=GROUP_INK.get(g, "k"), lw=1.2,
                        ls=(0, (2, 2)))
            lag_axis(ax, R, xlabel=(r == 1))
            ax.set_ylim(-0.8, 0.8)
            tag(ax, "ABCD"[r * 2 + c])
            ax.set_ylabel(f"excess coincidence\n{DATASET[name]}, "
                          f"{'as recorded' if arm == 'real' else 'episodes removed + block control'}",
                          fontsize=10)
    G0 = R["folders"][names[0]]["by_group"]
    h = [Line2D([], [], color=GROUP_INK.get(g, "k"), lw=2.0,
                label=f"{g} · {S['n_recordings']} recordings, {S['n_mice']} mice; "
                      f"heaviest mouse {100 * S['top_mouse_share_of_pairs']:.0f} % of pairs")
         for g, S in G0.items()]
    h += [Line2D([], [], color="0.3", lw=2.0, label="pooled over recordings"),
          Line2D([], [], color="0.3", lw=1.2, ls=(0, (2, 2)), label="each mouse weighted equally")]
    fig.legend(handles=h, loc="lower center", ncol=2, frameon=False)
    fig.subplots_adjust(left=0.09, right=0.99, top=0.98, bottom=0.2, hspace=0.12, wspace=0.22)
    fig.savefig(out / "fig6_by_group.png", dpi=150)
    plt.close(fig)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--run", required=True, type=Path, help="folder holding results.json")
    ap.add_argument("--out", type=Path, default=None, help=f"default: <darkroom>/bugarach/{FOLDER}")
    ap.add_argument("--also", type=Path, default=None, help="also copy the figures here (repo)")
    a = ap.parse_args(argv)
    if a.out is None:
        from bugarach.paths import darkroom, unresolved_message
        a.out = darkroom(FOLDER, create=True)
        if a.out is None:
            raise SystemExit(unresolved_message("--out"))
    a.out.mkdir(parents=True, exist_ok=True)
    R = json.loads((a.run / "results.json").read_text())
    for old in a.out.glob("fig*.png"):
        old.unlink()
    fig2(R, a.out)
    fig3(R, a.out)
    fig4(R, a.out)
    if R["folders"]:
        fig1(R, a.out)
        fig5(R, a.out)
        fig6(R, a.out)
    made = sorted(a.out.glob("fig*.png"))
    if a.also:
        a.also.mkdir(parents=True, exist_ok=True)
        for old in a.also.glob("fig*.png"):
            old.unlink()
        for p in made:
            shutil.copy2(p, a.also / p.name)
    for p in made:
        print(p)


if __name__ == "__main__":
    main()
