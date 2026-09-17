#!/usr/bin/env python3
"""Draw the two leak tests rigid shift has to pass, each beside the controls that can fail them.

    python tools/make_rigid_shift_gates_figure.py --run <folder>
        [--out <folder>] [--also <folder>]

Reads ``controls_lab/results.json`` (``tools/look_rigid_shift_controls.py --leak-only``) and
``aggregate_leak/results.json`` (``tools/tube_aggregate_leak.py``); writes
``rigid_shift_gates_fig.png``. Exploratory.

Four panels, stacked two by two so each reads at page width:

* **A, B — the per-ROI test, lab fast and lab slow.** Accuracy of a classifier over per-ROI
  statistics at telling a recording from rigid shift, a shared offset, per-onset dither and a
  per-ROI circular shift, by displacement.
* **C — the aggregate test on real recordings, lab fast.** The same forced choice read off the
  cells-mean channels: a hand-built centre-surround bank at `tube`'s initial scales and beyond, and
  what fitted `tube` and `line` heads receive.
* **D — the aggregate test on synthetic twins.** Planted events, shared slow modulation with no
  events, independent modulation, and the stationary twin, each against its own rigid shift.

Inks: surrogates in panels A and B take slots of the dataviz reference palette that no model uses
(violet, magenta, yellow); models in panel C keep the ink they have in every other figure of the
report (`tube` grey, `line` blue).
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from matplotlib.lines import Line2D  # noqa: E402
from figure_destination import add_arguments, save  # noqa: E402

plt.rcParams.update({"font.size": 10.5, "axes.labelsize": 10.5, "xtick.labelsize": 10,
                     "ytick.labelsize": 10, "legend.fontsize": 9.5})

CONTROLS = [("rigid_shift", "rigid shift", "#4a3aa7", "o", True),
            ("shared_shift", "shared offset: should read chance", "#333333", "s", False),
            ("uniform_dither", "per-onset dither: must separate", "#e87ba4", "D", True),
            ("circular_shift", "per-ROI circular shift", "#eda100", "^", True)]
BANKS = [("init", "hand-built bank at tube's initial scales", "#9a9a9a", "s"),
         ("tube", "fitted tube (four folds)", "#6b6b6b", "o"),
         ("line", "fitted line (four folds)", "#2a78d6", "o")]
TWINS = [("planted_vs_rigid_shift", "planted events: must separate", "#111111", "o", True),
         ("shared_modulation_vs_rigid_shift", "shared modulation, no events", "#4a3aa7", "D", True),
         ("independent_modulation_vs_rigid_shift", "independent modulation: must read chance",
          "#e87ba4", "s", True),
         ("unplanted_vs_rigid_shift", "stationary twin (cannot fail)", "#111111", "o", False)]
YLIM = (0.3, 1.0)


def dodge(n, i, width=0.5):
    return (i - (n - 1) / 2) * width / max(1, n - 1) if n > 1 else 0.0


def point(ax, x, acc, lo, hi, colour, marker, filled, ms=6.5):
    ax.vlines(x, lo, hi, color=colour, lw=1.5, alpha=0.9 if filled else 0.6)
    ax.plot([x], [acc], marker, ms=ms, color=colour if filled else "white", mec=colour, mew=1.4,
            zorder=3)


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", required=True)
    add_arguments(ap)
    a = ap.parse_args(argv)
    run = Path(a.run)
    C = json.loads((run / "controls_lab" / "results.json").read_text())["leak"]
    G = json.loads((run / "aggregate_leak" / "results.json").read_text())

    fig, axes = plt.subplots(2, 2, figsize=(10.5, 13.0))
    for ax, stream, letter in ((axes[0, 0], "fast", "A"), (axes[0, 1], "slow", "B")):
        rows = sorted((r for r in C if r["stream"] == stream), key=lambda r: r["J_sec"])
        x = np.arange(len(rows))
        present = [c for c in CONTROLS if c[0] in rows[0]]
        for k, (key, _, colour, marker, filled) in enumerate(present):
            for i, r in enumerate(rows):
                b = r[key]["by_mouse"]
                point(ax, i + dodge(len(present), k), b["accuracy"], b["p2_5"], b["p97_5"],
                      colour, marker, filled)
        ax.axhline(0.5, color="0.55", ls=":", lw=1)
        ax.set_xticks(x, [f"{r['J_sec']:g}" for r in rows])
        ax.set_ylim(*YLIM)
        ax.set_xlabel("displacement J (s)")
        ax.set_ylabel(f"lab {stream}: per-ROI classifier accuracy\n"
                      f"({rows[0]['n_pairs']:,} window pairs, {rows[0]['n_mice']} mice)")
        ax.text(0.02, 0.97, letter, transform=ax.transAxes, fontsize=13, fontweight="bold",
                va="top")
    axes[0, 0].legend(handles=[Line2D([], [], color=c, marker=m, ls="", ms=7,
                                      mfc=c if f else "white", mec=c, mew=1.4, label=lab)
                               for _, lab, c, m, f in CONTROLS if _ in C[0]],
                      title="panels A and B", title_fontsize=9.5, alignment="left",
                      loc="upper center", bbox_to_anchor=(0.5, -0.13), ncol=1, frameon=False)

    ax = axes[1, 0]
    Js = sorted({r["J_sec"] for r in G if r["stream"] == "fast" and r["kind"] == "real"})
    x = np.arange(len(Js))
    for k, (bank, _, colour, marker) in enumerate(BANKS):
        for key, filled, off in (("real_vs_rigid_shift", True, -0.06),
                                 ("real_vs_shared_offset", False, 0.06)):
            for i, J in enumerate(Js):
                cells = [r for r in G if r["stream"] == "fast" and r["J_sec"] == J
                         and r["kind"] == "real"
                         and (r["bank"] == "init" if bank == "init"
                              else r["bank"] == "fitted" and r.get("model") == bank)]
                if not cells:
                    continue
                # One point per fitted fold, so a spread narrower than a marker is still visible.
                for q in cells:
                    s = q[key]["all"]
                    point(ax, i + dodge(len(BANKS), k, 0.6) + off, s["accuracy"], s["p2_5"],
                          s["p97_5"], colour, marker, filled, ms=5.5)
    ax.axhline(0.5, color="0.55", ls=":", lw=1)
    ax.set_xticks(x, [f"{J:g}" for J in Js])
    ax.set_ylim(*YLIM)
    ax.set_xlabel("displacement J (s)")
    ax.set_ylabel("lab fast, real recordings:\naccuracy from the cells-mean channels")
    ax.text(0.02, 0.97, "C", transform=ax.transAxes, fontsize=13, fontweight="bold", va="top")
    ax.legend(handles=[Line2D([], [], color=c, marker=m, ls="", ms=7, label=lab)
                       for _, lab, c, m in BANKS]
              + [Line2D([], [], color="0.2", marker="D", ls="", ms=7,
                        label="filled: vs rigid shift"),
                 Line2D([], [], color="0.2", marker="D", ls="", ms=7, mfc="white",
                        label="open: vs shared offset (should read chance)")],
              loc="upper center", bbox_to_anchor=(0.5, -0.13), ncol=1, frameon=False)

    ax = axes[1, 1]
    for k, (key, _, colour, marker, filled) in enumerate(TWINS):
        for i, J in enumerate(Js):
            cells = [r for r in G if r["stream"] == "fast" and r["J_sec"] == J
                     and r["kind"] == "twin" and r["bank"] == "init" and key in r]
            for q in cells:
                s = q[key]["all"]
                point(ax, i + dodge(len(TWINS), k, 0.6), s["accuracy"], s["p2_5"], s["p97_5"],
                      colour, marker, filled)
    ax.axhline(0.5, color="0.55", ls=":", lw=1)
    ax.set_xticks(x, [f"{J:g}" for J in Js])
    ax.set_ylim(*YLIM)
    ax.set_xlabel("displacement J (s)")
    ax.set_ylabel("synthetic twins against their rigid shift:\n"
                  "accuracy from the hand-built initial bank")
    ax.text(0.02, 0.97, "D", transform=ax.transAxes, fontsize=13, fontweight="bold", va="top")
    ax.legend(handles=[Line2D([], [], color=c, marker=m, ls="", ms=7, mfc=c if f else "white",
                              mec=c, mew=1.4, label=lab) for _, lab, c, m, f in TWINS],
              loc="upper center", bbox_to_anchor=(0.5, -0.13), ncol=1, frameon=False)
    fig.text(0.5, 0.005, "bars: 95 % interval from a refitting bootstrap that resamples mice "
                         "(twins: resamples twins); dotted line: chance, 0.5",
             ha="center", fontsize=9.5, color="0.3")
    fig.tight_layout(rect=(0, 0.02, 1, 1))
    save(fig, "rigid_shift_gates_fig.png", a, subfolder="tube_self_supervised")


if __name__ == "__main__":
    main()
