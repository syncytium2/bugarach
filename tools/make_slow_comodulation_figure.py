#!/usr/bin/env python3
"""Draw the slow co-modulation explainer's figures from ``measure_slow_comodulation.py``'s output.

    python tools/make_slow_comodulation_figure.py --run <folder>          # into the darkroom
    python tools/make_slow_comodulation_figure.py --run <folder> --also docs/learned/slow_comodulation

Writes, into ``<darkroom>/2026-09-17-slow-comodulation/`` unless ``--out`` names a folder:

* ``fig1_three_kinds.png`` — synthetic: rasters of planted events, shared modulation on a 20 s
  timescale and shared drift on a 5-minute one, the share of ROIs lit above each, and the
  cross-correlogram of every synthetic world.
* ``fig2_what_the_surrogates_remove.png`` — synthetic: each world against rigid shift at three
  displacements, the 2-minute block control and the circular-shift null.
* ``fig3_recordings.png`` — the lab fast and slow streams and the Cossart folder, pooled over
  recordings: the peak on top, the shoulder zoomed below.
* ``fig4_by_group.png`` — the lab streams split by group (FOUNDATIONS §9: a pooled number is not
  admissible on its own).

``--also`` copies every figure to a repo folder. None holds a real raster (FOUNDATIONS §5): the
real-recording figures are curves pooled over recordings.
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

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

FOLDER = "2026-09-17-slow-comodulation"
INK = {"real": "#111111", "circular": "#9a9a9a", "block_120": "#c2502a",
       "rigid_1.6": "#9ecae1", "rigid_10": "#4292c6", "rigid_20": "#08306b",
       "minus_coact": "#41ab5d"}
LABEL = {"real": "as recorded", "circular": "circular shift (the null)",
         "block_120": "circular shift within 2-minute blocks",
         "rigid_1.6": "rigid shift, J 1.6 s", "rigid_10": "rigid shift, J 10 s",
         "rigid_20": "rigid shift, J 20 s", "minus_coact": "CoactDetect episodes removed"}
WORLD = {"independent": "independent ROIs", "events": "planted sub-second events",
         "shared": "shared modulation, 20 s timescale", "drift": "shared drift, 5-minute timescale",
         "per_roi": "per-ROI modulation (the simulator's kind)",
         "events_shared": "events + shared 20 s modulation"}
WORLD_INK = {"independent": "#9a9a9a", "events": "#111111", "shared": "#c2502a",
             "drift": "#7b3294", "per_roi": "#e0a458", "events_shared": "#3182bd"}
GROUP_INK = {"DI": "#1b9e77", "MALE": "#d95f02", "ORX": "#7570b3", "OVX": "#e7298a"}
FOLDER_TITLE = {"steps_excluded/fast": "lab, fast stream", "steps_excluded/slow": "lab, slow stream",
                "cossart/events": "Cossart folder"}
LAG_TICKS = (0.25, 1.0, 5.0, 15.0, 60.0, 300.0)


def fmt_sec(s: float) -> str:
    """Minutes-friendly labels: 0.25s, 1s, 45s, 2m, 2m30s."""
    if s < 60:
        return f"{s:g}s"
    m, r = divmod(int(round(s)), 60)
    return f"{m}m" if r == 0 else f"{m}m{r}s"


def lag_axis(ax, R, xlabel=True):
    ax.set_xscale("log")
    ax.set_xlim(0.12, R["lag_edges_sec"][-1])
    ax.set_xticks(LAG_TICKS, [fmt_sec(t) for t in LAG_TICKS] if xlabel else [""] * len(LAG_TICKS))
    ax.xaxis.set_minor_locator(matplotlib.ticker.NullLocator())
    ax.axhline(0, color="0.8", lw=0.8, zorder=0)
    if xlabel:
        ax.set_xlabel("lag between onsets in two different ROIs")


def centres(R):
    e = np.asarray(R["lag_edges_sec"])
    return np.sqrt(np.maximum(e[:-1], 0.125) * e[1:])


def curve(ax, R, S, arm, band=False, lw=1.5, label=True):
    if arm not in S["arms"]:
        return
    x = centres(R)
    v = S["arms"][arm]
    ax.plot(x, v["excess"], color=INK[arm], lw=lw, label=LABEL[arm] if label else None)
    if band:
        ax.fill_between(x, v["lo"], v["hi"], color=INK[arm], alpha=0.15, lw=0)


def _raster(ax, trains, dt, t0, t1):
    for r, t in enumerate(trains):
        ts = np.asarray(t) * dt
        ts = ts[(ts >= t0) & (ts < t1)]
        ax.vlines(ts, r + 0.1, r + 0.9, color="k", lw=0.9)
    ax.set_xlim(t0, t1)
    ax.set_ylim(0, len(trains))
    ax.set_yticks([])


def _lit_share(ax, trains, dt, t0, t1, bin_sec=10.0):
    edges = np.arange(t0, t1 + bin_sec, bin_sec)
    lit = np.zeros(edges.size - 1)
    for t in trains:
        h, _ = np.histogram(np.asarray(t) * dt, edges)
        lit += h > 0
    ax.step(edges[:-1], lit / len(trains), where="post", color="k", lw=1.0)
    ax.set_xlim(t0, t1)


def time_ticks(ax, t0, t1, step=120.0):
    ticks = np.arange(t0, t1 + 1, step)
    ax.set_xticks(ticks, [fmt_sec(t - t0) for t in ticks])


def fig1(R, out: Path):
    syn = R["synthetic"]
    fig = plt.figure(figsize=(12.5, 8.8))
    gs = fig.add_gridspec(3, 3, height_ratios=(0.8, 2.0, 2.5), hspace=0.32, wspace=0.08)
    t0, t1 = 60.0, 1140.0
    for col, world in enumerate(("events", "shared", "drift")):
        row = next(r for r in syn[world]["rows"] if r["raster"] is not None)
        a_top = fig.add_subplot(gs[0, col])
        _lit_share(a_top, row["raster"], row["dt"], t0, t1)
        a_top.set_ylim(0, 0.8)
        a_top.set_xticks([])
        if col:
            a_top.set_yticklabels([])
        else:
            a_top.set_ylabel("share of ROIs\nlit, 10 s bins")
        a_top.set_title(f"{'ABC'[col]}. {WORLD[world]}", loc="left", fontsize=10)
        a_r = fig.add_subplot(gs[1, col])
        _raster(a_r, row["raster"], row["dt"], t0, t1)
        time_ticks(a_r, t0, t1, 300.0)
        if col == 0:
            a_r.set_ylabel(f"{len(row['raster'])} ROIs, one recording")
    ax = fig.add_subplot(gs[2, :])
    x = centres(R)
    for world in ("independent", "per_roi", "events", "shared", "drift"):
        ax.plot(x, syn[world]["summary"]["arms"]["real"]["excess"], color=WORLD_INK[world], lw=2.0,
                label=WORLD[world])
    lag_axis(ax, R)
    ax.set_yscale("symlog", linthresh=1.0, linscale=1.5)
    ax.set_ylabel("excess coincidence\n(observed ÷ chance − 1)")
    ax.set_title(f"D. Cross-correlogram of each world, pooled over "
                 f"{syn['events']['summary']['n_recordings']} recordings per world",
                 loc="left", fontsize=10)
    ax.legend(frameon=False, fontsize=8.5, loc="upper right")
    fig.subplots_adjust(left=0.08, right=0.985, top=0.96, bottom=0.07)
    fig.savefig(out / "fig1_three_kinds.png", dpi=150)
    plt.close(fig)


ARMS_SYN = ("circular", "block_120", "rigid_20", "rigid_10", "rigid_1.6", "real")


def fig2(R, out: Path):
    syn = R["synthetic"]
    worlds = ("events", "shared", "drift")
    fig, axes = plt.subplots(1, 3, figsize=(12.5, 4.6))
    for i, (ax, world) in enumerate(zip(axes, worlds)):
        S = syn[world]["summary"]
        for arm in ARMS_SYN:
            curve(ax, R, S, arm, lw=2.0 if arm == "real" else 1.5)
        lag_axis(ax, R)
        if world == "events":
            ax.set_yscale("symlog", linthresh=0.5, linscale=1.5)
        ax.set_title(f"{'ABC'[i]}. {WORLD[world]}", loc="left", fontsize=10)
    axes[0].set_ylabel("excess coincidence\n(observed ÷ chance − 1)")
    h, lab = axes[0].get_legend_handles_labels()
    fig.legend(h, lab, frameon=False, fontsize=8.5, loc="lower center", ncol=len(lab))
    fig.subplots_adjust(left=0.07, right=0.99, top=0.9, bottom=0.25, wspace=0.2)
    fig.savefig(out / "fig2_what_the_surrogates_remove.png", dpi=150)
    plt.close(fig)


def fig3(R, out: Path):
    names = [n for n in FOLDER_TITLE if n in R["folders"]]
    fig, axes = plt.subplots(2, len(names), figsize=(4.3 * len(names), 7.2), squeeze=False,
                             gridspec_kw=dict(height_ratios=(1, 1.25), hspace=0.1, wspace=0.22))
    for c, name in enumerate(names):
        S = R["folders"][name]["summary"]
        for r in range(2):
            ax = axes[r, c]
            for arm in ("circular", "block_120", "rigid_20", "rigid_10", "rigid_1.6"):
                curve(ax, R, S, arm, label=(r == 1))
            curve(ax, R, S, "minus_coact", band=True, label=(r == 1))
            curve(ax, R, S, "real", band=True, lw=2.2, label=(r == 1))
            lag_axis(ax, R, xlabel=(r == 1))
        axes[0, c].set_title(f"{'ABC'[c]}. {FOLDER_TITLE[name]} · {S['n_recordings']} recordings, "
                             f"{S['n_mice']} mice", loc="left", fontsize=9.5)
        axes[1, c].set_ylim(-0.7, 0.7)
    axes[0, 0].set_ylabel("the peak: full range\nexcess coincidence")
    axes[1, 0].set_ylabel("the shoulder: zoomed to ±0.7\nshaded: 95 % interval over mice")
    axes[1, 0].legend(frameon=False, fontsize=7.5, loc="lower right")
    fig.subplots_adjust(left=0.07, right=0.99, top=0.95, bottom=0.08)
    fig.savefig(out / "fig3_recordings.png", dpi=150)
    plt.close(fig)


def fig4(R, out: Path):
    names = [n for n in ("steps_excluded/fast", "steps_excluded/slow") if n in R["folders"]]
    if not names:
        return
    fig, axes = plt.subplots(2, len(names), figsize=(6.2 * len(names), 7.0), squeeze=False,
                             gridspec_kw=dict(hspace=0.1, wspace=0.18))
    x = centres(R)
    for c, name in enumerate(names):
        G = R["folders"][name]["by_group"]
        for r, arm in enumerate(("real", "block_120")):
            ax = axes[r, c]
            for g, S in G.items():
                v = S["arms"][arm]
                ax.plot(x, v["excess"], color=GROUP_INK.get(g, "k"), lw=1.8,
                        label=f"{g} · {S['n_recordings']} recordings, {S['n_mice']} mice")
                ax.fill_between(x, v["lo"], v["hi"], color=GROUP_INK.get(g, "k"), alpha=0.08, lw=0)
            lag_axis(ax, R, xlabel=(r == 1))
            ax.set_ylim(-0.7, 0.8)
        axes[0, c].set_title(f"{'AB'[c]}. {FOLDER_TITLE[name]}, by group", loc="left", fontsize=10)
    axes[0, 0].set_ylabel("as recorded, zoomed to the shoulder\nexcess coincidence")
    axes[1, 0].set_ylabel("circular shift within 2-minute blocks\nexcess coincidence")
    axes[0, 0].legend(frameon=False, fontsize=8, loc="upper right")
    fig.subplots_adjust(left=0.08, right=0.99, top=0.95, bottom=0.08)
    fig.savefig(out / "fig4_by_group.png", dpi=150)
    plt.close(fig)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--run", required=True, type=Path, help="folder holding results.json")
    ap.add_argument("--out", type=Path, default=None, help=f"default: <darkroom>/{FOLDER}")
    ap.add_argument("--also", type=Path, default=None, help="also copy the figures here (repo)")
    a = ap.parse_args(argv)
    if a.out is None:
        from bugarach.paths import darkroom
        a.out = darkroom(FOLDER, create=True)
        if a.out is None:
            raise SystemExit("no darkroom on this machine: pass --out")
    a.out.mkdir(parents=True, exist_ok=True)
    R = json.loads((a.run / "results.json").read_text())
    fig1(R, a.out)
    fig2(R, a.out)
    if R["folders"]:
        fig3(R, a.out)
        fig4(R, a.out)
    made = sorted(a.out.glob("fig*.png"))
    if a.also:
        a.also.mkdir(parents=True, exist_ok=True)
        for p in made:
            shutil.copy2(p, a.also / p.name)
    for p in made:
        print(p)


if __name__ == "__main__":
    main()
