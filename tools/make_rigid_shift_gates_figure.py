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
  cells-mean channels: a hand-built center-surround bank at `tube`'s initial scales and beyond, and
  what fitted `tube` and `line` heads receive, one mark per held-out fold, dodged so all four show.
* **D — the aggregate test on synthetic twins.** Planted events, shared slow modulation with no
  events, independent modulation, and the stationary twin, each against its own rigid shift.

Every series names its role in the legend (under test, null control, positive control), and the
legends say what the bars are: a 95 % interval from a bootstrap that resamples mice (twins, in D)
and refits the classifier (``look_rigid_shift.refit_bootstrap``).

Inks: surrogates in panels A and B take slots of the dataviz reference palette that no model uses
(violet, magenta, yellow); models in panel C keep the ink and shape they have in every other figure
of the report (`tube` gray circle, `line` blue circle). The hand-built bank is a black hexagon, and
panel D's twins are a red star, a teal pentagon, a plum cross and an olive plus: one ink and one
shape per concept, none of them a model's and none of them reused between panels.
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
                     "ytick.labelsize": 10, "legend.fontsize": 9.5,
                     "legend.title_fontsize": 9.5})

DASH = "\N{EM DASH}"
CONTROLS = [("rigid_shift", f"rigid shift {DASH} under test: must read chance",
             "#4a3aa7", "o", True),
            ("shared_shift", f"shared offset {DASH} null control: must read chance",
             "#333333", "s", False),
            ("uniform_dither", f"per-onset dither {DASH} positive control: must separate",
             "#e87ba4", "D", True),
            ("circular_shift", f"per-ROI circular shift {DASH} positive control: must separate",
             "#eda100", "^", True)]
# (key, label, ink, marker). The hand-built bank takes an ink and shape no model uses anywhere in
# the report; fitted models keep their own (tube gray circle, line blue circle).
BANKS = [("init", "hand-built initial bank (tube's starting scales)", "#000000", "h"),
         ("tube", "fitted tube, one mark per held-out fold (4 folds)", "#6b6b6b", "o"),
         ("line", "fitted line, one mark per held-out fold (4 folds)", "#2a78d6", "o")]
# (key, label, ink, marker, filled). One ink and one shape per concept across the whole report:
# every twin takes an ink and a shape that no surrogate in panels A and B, no bank in panel C and
# no model anywhere in the report uses (#2a78d6, #eb6834, #1baf7a, #6b6b6b and #a8a8a8 are the
# model inks; circle, square, diamond, triangle and hexagon are spoken for).
TWINS = [("planted_vs_rigid_shift", f"events twin, planted events only {DASH} positive control: must separate",
          "#c2262e", "*", True),
         ("shared_modulation_vs_rigid_shift",
          f"shared-modulation twin, no events {DASH}\nwhat slow co-modulation alone reads",
          "#14807e", "p", True),
         ("independent_modulation_vs_rigid_shift",
          f"independent-modulation twin {DASH} null control:\nmust read chance",
          "#7a2b6b", "X", True),
         ("unplanted_vs_rigid_shift", f"stationary twin {DASH} cannot fail", "#5c6610", "P",
          False)]
TWIN_MS = {"*": 10.0, "p": 7.5, "X": 7.5, "P": 8.0}
YLIM = (0.3, 1.0)
CHANCE_INK = "0.45"
FOLD_STEP = 0.085       # x spacing between held-out folds of one fitted model, in J slots
LEGEND = dict(loc="upper left", bbox_to_anchor=(-0.02, -0.12), ncol=1, frameon=False,
              alignment="left", handletextpad=0.6, labelspacing=0.45)


def dodge(n, i, width=0.5):
    return (i - (n - 1) / 2) * width / max(1, n - 1) if n > 1 else 0.0


def point(ax, x, acc, lo, hi, color, marker, filled, ms=6.5, lw=1.5):
    ax.vlines(x, lo, hi, color=color, lw=lw, alpha=0.9 if filled else 0.6)
    ax.plot([x], [acc], marker, ms=ms, color=color if filled else "white", mec=color, mew=1.4,
            zorder=3)


def key(color, marker, label, filled=True, ms=7):
    return Line2D([], [], color=color, marker=marker, ls="", ms=ms,
                  mfc=color if filled else "white", mec=color, mew=1.4, label=label)


def bar_key(label):
    return Line2D([], [], color="0.3", marker="|", ls="", ms=16, mew=1.5, label=label)


def chance_key():
    return Line2D([], [], color=CHANCE_INK, ls=":", lw=1.3,
                  label="dotted line: chance, 0.5 accuracy")


def chance(ax):
    ax.axhline(0.5, color=CHANCE_INK, ls=":", lw=1.3, zorder=1)


def letter(ax, text):
    ax.text(0.02, 0.97, text, transform=ax.transAxes, fontsize=13, fontweight="bold", va="top")


def interval_label(n, unit):
    return (f"bar: 95 % interval from a bootstrap that resamples\n"
            f"the {n} {unit} and refits the classifier")


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", required=True)
    add_arguments(ap)
    a = ap.parse_args(argv)
    run = Path(a.run)
    C = json.loads((run / "controls_lab" / "results.json").read_text())["leak"]
    G = json.loads((run / "aggregate_leak" / "results.json").read_text())

    fig, axes = plt.subplots(2, 2, figsize=(11.0, 14.0))
    n_mice_ab = set()
    for ax, stream, name in ((axes[0, 0], "fast", "A"), (axes[0, 1], "slow", "B")):
        rows = sorted((r for r in C if r["stream"] == stream), key=lambda r: r["J_sec"])
        x = np.arange(len(rows))
        present = [c for c in CONTROLS if c[0] in rows[0]]
        for k, (k_name, _, color, marker, filled) in enumerate(present):
            for i, r in enumerate(rows):
                b = r[k_name]["by_mouse"]
                point(ax, i + dodge(len(present), k), b["accuracy"], b["p2_5"], b["p97_5"],
                      color, marker, filled)
        chance(ax)
        ax.set_xticks(x, [f"{r['J_sec']:g}" for r in rows])
        ax.set_ylim(*YLIM)
        if stream == "slow":
            # The slow displacements are 1.4 s times powers of two, not rounded fast ones.
            base = rows[0]["J_sec"]
            mult = ", ".join(f"{r['J_sec'] / base:g}" for r in rows)
            ax.set_xlabel(f"displacement J (s): {base:g} s \N{MULTIPLICATION SIGN} {mult}")
        else:
            ax.set_xlabel("displacement J (s)")
        ax.set_ylabel(f"lab {stream} stream: per-ROI classifier accuracy\n"
                      f"({rows[0]['n_pairs']:,} window pairs, {rows[0]['n_mice']} mice)")
        n_mice_ab.add(rows[0]["n_mice"])
        letter(ax, name)
    axes[0, 0].legend(handles=[key(c, m, lab, f) for k_name, lab, c, m, f in CONTROLS
                               if k_name in C[0]],
                      title="panels A and B: the lab recording against each transform\n"
                            "(ROI: region of interest)", **LEGEND)
    axes[0, 1].legend(handles=[bar_key(interval_label("/".join(map(str, sorted(n_mice_ab))),
                                                      "mice")),
                               chance_key()],
                      title="panels A and B: how to read", **LEGEND)

    ax = axes[1, 0]
    real = [r for r in G if r["stream"] == "fast" and r["kind"] == "real"]
    Js = sorted({r["J_sec"] for r in real})
    x = np.arange(len(Js))
    # Slot layout within one J: the hand-built bank, then tube's folds, then line's folds, with a
    # wider gap between groups than between folds so each model's four marks read as a set.
    gap = 1.6 * FOLD_STEP
    offsets, pos = {}, 0.0
    for bank, _, _, _ in BANKS:
        n = 1 if bank == "init" else 4
        offsets[bank] = [pos + j * FOLD_STEP for j in range(n)]
        pos = offsets[bank][-1] + gap
    span = offsets["line"][-1]
    offsets = {b: [o - span / 2 for o in v] for b, v in offsets.items()}
    for bank, _, color, marker in BANKS:
        for i, J in enumerate(Js):
            cells = [r for r in real if r["J_sec"] == J
                     and (r["bank"] == "init" if bank == "init"
                          else r["bank"] == "fitted" and r.get("model") == bank)]
            cells.sort(key=lambda r: r.get("held_fold", 0))
            for j, q in enumerate(cells):
                for k_name, filled in (("real_vs_rigid_shift", True),
                                       ("real_vs_shared_offset", False)):
                    s = q[k_name]["all"]
                    point(ax, i + offsets[bank][j], s["accuracy"], s["p2_5"], s["p97_5"],
                          color, marker, filled, ms=5.0 if marker == "o" else 6.5, lw=1.2)
    chance(ax)
    # Faint rules between displacements, so each dodged cluster reads as belonging to its J.
    for i in range(len(Js) - 1):
        ax.axvline(i + 0.5, color="0.85", lw=0.8, zorder=0)
    ax.set_xticks(x, [f"{J:g}" for J in Js])
    ax.set_xlim(-0.55, len(Js) - 0.45)
    ax.set_ylim(*YLIM)
    ax.set_xlabel("displacement J (s)")
    n_mice_c = sorted({r["n_mice"] for r in real})
    ax.set_ylabel("lab fast stream, real recordings: accuracy from\n"
                  f"the cells-mean channels ({real[0]['n_pairs']:,} window pairs, "
                  f"{'/'.join(map(str, n_mice_c))} mice)")
    letter(ax, "C")
    ax.legend(handles=[key(c, m, lab) for _, lab, c, m in BANKS]
              + [key("0.2", "o", f"filled: real vs rigid shift {DASH} under test"),
                 key("0.2", "o", f"open: real vs shared offset {DASH} null control:\n"
                                 "must read chance", filled=False),
                 bar_key(interval_label("/".join(map(str, n_mice_c)), "mice")),
                 chance_key()],
              **LEGEND)

    ax = axes[1, 1]
    twins = [r for r in G if r["stream"] == "fast" and r["kind"] == "twin" and r["bank"] == "init"]
    for k, (k_name, _, color, marker, filled) in enumerate(TWINS):
        for i, J in enumerate(Js):
            for q in (r for r in twins if r["J_sec"] == J and k_name in r):
                s = q[k_name]["all"]
                point(ax, i + dodge(len(TWINS), k, 0.6), s["accuracy"], s["p2_5"], s["p97_5"],
                      color, marker, filled, ms=TWIN_MS[marker])
    chance(ax)
    ax.set_xticks(x, [f"{J:g}" for J in Js])
    ax.set_xlim(-0.55, len(Js) - 0.45)
    ax.set_ylim(*YLIM)
    ax.set_xlabel("displacement J (s)")
    n_twins, n_pairs_d = twins[0]["n_twins"], twins[0]["n_pairs"]
    ax.set_ylabel("synthetic twins against their rigid shift: accuracy\n"
                  f"from the hand-built initial bank ({n_twins} twins, "
                  f"{n_pairs_d:,} window pairs)")
    letter(ax, "D")
    ax.legend(handles=[key(c, m, lab, f, ms=TWIN_MS[m]) for _, lab, c, m, f in TWINS]
              + [bar_key(interval_label(n_twins, "twins")), chance_key()],
              **LEGEND)
    fig.tight_layout(h_pad=2.0, w_pad=2.5)
    save(fig, "rigid_shift_gates_fig.png", a, subfolder="tube_self_supervised")


if __name__ == "__main__":
    main()
