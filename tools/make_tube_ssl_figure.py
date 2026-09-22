#!/usr/bin/env python3
"""Draw what training against rigid shift bought: scores by arm, what a truth-reading score is made
of, and the paired checks beside the controls that can fail them.

    python tools/make_tube_ssl_figure.py --summary <run>/summary.json
        [--out <folder>] [--also <folder>]

Reads the ``training`` block of ``summary.json`` (``tools/summarize_tube_self_supervised.py``);
writes ``tube_ssl_fig.png``. Every mark is a condition mean: one arm, one displacement, one model,
averaged over its fits (a fit with no true positive scores 0). Exploratory.

Stacked so each panel reads at page width, under one key that serves all three:

* **A** — planted-truth F1 at the label-free threshold, one row per event-rate budget, by training
  arm, with the zero-parameter count baselines in the last columns.
* **B** — planted-truth F1 at the truth-reading threshold against the share of the held-out
  recording the detections cover there, one row per arm and displacement, on a logit coverage axis
  so the crowd near full coverage spreads out. A score earned by covering nearly everything is not
  detection.
* **C** — the paired checks in two rows, grouped by what each one can show: above, the null that
  must read chance and the pipeline checks that cannot fail for any scorer at all; below, the
  positive control that must move, what the objective paid for, and the two checks that separate
  coordination from slow shared modulation. Every check carries four arm lanes: supervised, sim,
  real, count.

Marks are queued rather than drawn (``mark``) and laid out per axes (``flush``): a mark that would
land on one already placed is nudged sideways until it is clear, and in panel B, where the x axis
carries coverage rather than a category, a hairline runs from the nudged mark back to its own
value. Nothing sits hidden under anything else.
"""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from math import hypot
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.lines import Line2D  # noqa: E402
from matplotlib.patheffects import withStroke  # noqa: E402
from figure_destination import add_arguments, save  # noqa: E402

plt.rcParams.update({"font.size": 10.5, "axes.labelsize": 10.5, "xtick.labelsize": 9.5,
                     "ytick.labelsize": 10, "legend.fontsize": 9.5})

MODELS = {"line": ("#2a78d6", "o"), "line_length": ("#eb6834", "s"),
          "line_bound": ("#1baf7a", "D"), "tube": ("#6b6b6b", "o"), "tube_guard": ("#a8a8a8", "s")}
"""The same inks as every other figure of the report: the three `line` builds on the first three
categorical slots of the dataviz reference palette, the tube family gray. Shape separates the two
grays, whose contrast ratio is only 1.36."""
BASELINES = {"count_share": "^", "count_excess": "P", "slow_modulation": "X"}
"""Zero-parameter scorers, in black: no model ink, so they never read as a trained build."""
INK = "#111111"
JS = (10.0, 20.0)
ARMS = [("supervised", None, "supervised"), ("untrained", None, "untrained"),
        ("ssl_sim", 10.0, "sim, 10 s"), ("ssl_sim", 20.0, "sim, 20 s"),
        ("ssl_real", 10.0, "real, 10 s"), ("ssl_real", 20.0, "real, 20 s"),
        ("baseline", 10.0, "count, 10 s"), ("baseline", 20.0, "count, 20 s")]
BUDGETS = [("label_free_0.5", "≤ 0.5 events per 10 minutes"),
           ("label_free_1", "≤ 1 event per 10 minutes"),
           ("label_free_2", "≤ 2 events per 10 minutes")]
B_ROWS = [("supervised", None, "supervised"), ("baseline", None, "count baselines"),
          ("ssl_sim", 10.0, "sim, 10 s"), ("ssl_sim", 20.0, "sim, 20 s"),
          ("ssl_real", 10.0, "real, 10 s"), ("ssl_real", 20.0, "real, 20 s"),
          ("untrained", None, "untrained")]
C_LANES = [("supervised", "sup"), ("ssl_sim", "sim"), ("ssl_real", "real"),
           ("baseline", "count")]
"""Panel C's lanes, left to right inside every check, named by a token short enough to print
horizontally in every check (the axis label spells each one out). The untrained arm is left out: it
separates nothing, and a fifth lane would crowd the four the argument compares."""
CHECK_ROWS = [
    ((0.38, 0.632), [0.4, 0.45, 0.5, 0.55, 0.6], 0.605,
     [("null: must read chance", [("real_vs_shared_offset", "shared offset,\nsame crop")]),
      ("pipeline checks: cannot fail for any scorer",
       [("real_vs_shared_offset_independent_crop", "shared offset,\nother crop"),
        ("unplanted_twin_vs_rigid_shift", "stationary\ntwin"),
        ("independent_modulation_twin_vs_rigid_shift", "independent\nmodulation twin")])]),
    ((0.485, 1.05), [0.5, 0.6, 0.7, 0.8, 0.9, 1.0], 0.975,
     [("positive control: must move", [("real_vs_thinned", "a fifth of\nonsets removed")]),
      ("trained for", [("real_vs_rigid_shift", "rigid shift\nat training J")]),
      ("coordination, or slow modulation?",
       [("real_vs_rigid_shift_small_J", "rigid shift\nat small J"),
        ("shared_modulation_twin_vs_rigid_shift", "shared\nmodulation twin")])])]
"""Which checks can fail, and so what each group is entitled to claim. Against an independent crop
the shared offset is exchangeable with the real crop; the stationary twin is unchanged by rigid
shift; independent modulation is exchangeable with its own shift. Those three read chance for any
scorer at all, so they check the pipeline and say nothing about a model. The same-crop shared
offset keeps the crop's own rates and can fail, so it is the null."""
YLIM_F1 = (-0.03, 0.9)
YLIM_B = (0.40, 0.75)
COVER_TICKS = [0.003, 0.01, 0.03, 0.1, 0.3, 0.5, 0.7, 0.9, 0.97, 0.99]
DPI = 150
WIDE_IN, TALL_IN = 10.5, 14.3
"""Page size in inches. Each section below is placed in inches from the top edge, so the height is
the sum of what the panels and their labels need, not a ratio to be tuned."""


def dodge(n, i, width):
    return (i - (n - 1) / 2) * width / max(1, n - 1) if n > 1 else 0.0


def counted(ns, unit):
    """'12 fits', '1 fit', or '11 or 12 fits' when cells differ."""
    return " or ".join(map(str, ns)) + " " + unit + ("" if ns == [1] else "s")


def cell(cells, arm, J, model):
    return cells.get(f"{arm}|{J}|{model}")


QUEUE: dict = defaultdict(list)


def mark(ax, x, y, model, J, ms=6.0):
    """Queue one mark for ``ax``: model ink and shape, open at J = 20 s, filled at J = 10 s and for
    the arms with no J (supervised, untrained); count baselines in black. ``flush`` draws it."""
    QUEUE[ax].append((x, y, model, J, ms))


def _style(model, J, ms):
    hollow = J == 20.0
    if model in BASELINES:
        return BASELINES[model], dict(ms=ms + 1, color=INK, mec=INK,
                                      mfc="white" if hollow else INK,
                                      mew=1.0 if hollow else 0.8)
    c, mk = MODELS[model]
    return mk, dict(ms=ms, color=c, mfc="white" if hollow else c, mec=c, mew=1.3)


def _to_px(ax, xs, ys):
    """Data coordinates to pixels within the axes, using the axes' own scales."""
    p = ax.get_position()
    w = p.width * ax.figure.get_figwidth() * DPI
    h = p.height * ax.figure.get_figheight() * DPI
    tx, ty = ax.xaxis.get_transform(), ax.yaxis.get_transform()
    (x0, x1), (y0, y1) = tx.transform(ax.get_xlim()), ty.transform(ax.get_ylim())
    px = [(tx.transform([x])[0] - x0) / (x1 - x0) * w for x in xs]
    py = [(ty.transform([y])[0] - y0) / (y1 - y0) * h for y in ys]
    return px, py, w, tx, x0, x1


def flush(ax, tether=False, cap_px=14.0):
    """Draw ``ax``'s queued marks, nudging sideways any mark that would land on one already drawn.

    The nudge is the smallest that clears, at most ``cap_px``; with ``tether`` a hairline runs from
    the mark back to its own x value, so a nudged mark still reads off the axis.
    """
    items = QUEUE.pop(ax, [])
    if not items:
        return
    xs, ys = [i[0] for i in items], [i[1] for i in items]
    px, py, w, tx, x0, x1 = _to_px(ax, xs, ys)
    order = sorted(range(len(items)), key=lambda i: (xs[i], ys[i]))
    placed: list[tuple[float, float, float]] = []
    for i in order:
        need = (items[i][4] + 2.0) * DPI / 72  # mark, its edge and its white ring
        steps = [0.0] + [k * 2.5 * d for k in range(1, int(cap_px / 2.5) + 1) for d in (1, -1)]
        best, best_gap = 0.0, -1e9
        for step in steps:
            if abs(step) > cap_px:
                continue
            gap = min((hypot(px[i] + step - qx, py[i] - qy) - (need + qn) / 2
                       for qx, qy, qn in placed), default=1e9)
            if gap >= 0:
                best = step
                break
            if gap > best_gap:
                best, best_gap = step, gap
        placed.append((px[i] + best, py[i], need))
        x, y, model, J, ms = items[i]
        if best:
            frac = (px[i] + best) / w
            x_draw = tx.inverted().transform([x0 + frac * (x1 - x0)])[0]
            if tether:
                ax.plot([x, x_draw], [y, y], "-", color="0.6", lw=0.8, zorder=2)
        else:
            x_draw = x
        mk, style = _style(model, J, ms)
        ax.plot([x_draw], [y], mk, zorder=3,
                path_effects=[withStroke(linewidth=2.6, foreground="white")], **style)


def members(arm, J=None):
    """(J, scorer) pairs drawn for an arm, J = 10 s first; one J only when ``J`` is given."""
    if arm in ("supervised", "untrained"):
        return [(None, m) for m in MODELS]
    names = list(BASELINES) if arm == "baseline" else list(MODELS)
    return [(j, m) for j in ((J,) if J else JS) for m in names]


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--summary", required=True)
    add_arguments(ap)
    a = ap.parse_args(argv)
    s = json.loads(Path(a.summary).read_text())
    cells = s["training"]["cells"]
    j_small = s["constants"]["training"]["j_small_sec"]
    n_fits = sorted({c["n_fits"] for c in cells.values() if c["arm"] != "baseline"})
    n_base = sorted({c["n_fits"] for c in cells.values() if c["arm"] == "baseline"})

    fig = plt.figure(figsize=(WIDE_IN, TALL_IN))

    def band(top_in, bottom_in, rows=1, hspace=0.14, left=0.215, height_ratios=None):
        """A section of the page, placed in inches from the top edge; rows share its height."""
        return fig.add_gridspec(rows, 1, left=left, right=0.985, hspace=hspace,
                                height_ratios=height_ratios,
                                top=1 - top_in / TALL_IN, bottom=1 - bottom_in / TALL_IN)

    # the key: every panel's marks, across the full page width
    kx = fig.add_subplot(band(0.06, 0.98, left=0.03)[0])
    kx.axis("off")
    kx.legend(
        handles=[Line2D([], [], color=c, marker=mk, ls="", ms=7, mec=c, mew=1.3, label=m)
                 for m, (c, mk) in MODELS.items()]
        + [Line2D([], [], color=INK, marker=mk, ls="", ms=8, mew=0.8,
                  label=f"{b} (no parameters)") for b, mk in BASELINES.items()]
        + [Line2D([], [], color="0.3", marker="o", ls="", ms=7,
                  label="filled: J = 10 s, or an arm\nwith no J (supervised, untrained)"),
           Line2D([], [], color="0.3", marker="o", ls="", ms=7, mfc="white", mew=1.3,
                  label="open: J = 20 s")],
        loc="center", ncol=4, frameon=False, columnspacing=1.2, handletextpad=0.3,
        title=f"Every mark is a condition mean over {counted(n_fits, 'fit')} (count baselines: "
              f"{counted(n_base, 'held-out fold')}); a fit with no true positive scores 0.\n"
              "F1: the harmonic mean of precision and recall against planted events. "
              "J: the rigid-shift displacement.",
        title_fontsize=9.5)

    # A: label-free F1 by arm, one row per event-rate budget
    ga = band(1.10, 4.00, len(BUDGETS))
    axes_a = []
    for row, (key, rate) in enumerate(BUDGETS):
        ax = fig.add_subplot(ga[row], sharex=axes_a[0] if axes_a else None)
        axes_a.append(ax)
        for i, (arm, J, _) in enumerate(ARMS):
            names = list(BASELINES) if arm == "baseline" else list(MODELS)
            for k, m in enumerate(names):
                c = cell(cells, arm, J, m)
                if c and key in c["scores"]:
                    mark(ax, i + dodge(len(names), k, 0.5), c["scores"][key]["f1_mean"], m, J,
                         ms=5.5)
        ax.set_xticks(range(len(ARMS)), [lab for _, _, lab in ARMS], fontsize=9.5)
        ax.set_xlim(-0.6, len(ARMS) - 0.4)
        ax.set_ylim(*YLIM_F1)
        ax.set_yticks([0.0, 0.2, 0.4, 0.6, 0.8])
        ax.text(0.995, 0.96, rate, transform=ax.transAxes, ha="right", va="top", fontsize=9.5)
        if row < len(BUDGETS) - 1:
            ax.tick_params(labelbottom=False)
        else:
            ax.set_xlabel("training arm: sim and real are trained against rigid shift at J = 10 s "
                          "or 20 s,\non simulated or real lab recordings, with no labels; count: "
                          "a zero-parameter baseline")
        flush(ax, cap_px=13.0)

    # B: truth-reading F1 against coverage, one row per arm and displacement, logit coverage axis
    gb = band(4.70, 8.90, len(B_ROWS))
    axes_b = []
    for r, (arm, J_row, label) in enumerate(B_ROWS):
        ax = fig.add_subplot(gb[r], sharex=axes_b[0] if axes_b else None)
        axes_b.append(ax)
        n = 0
        seen = set()
        for J, m in members(arm, J_row):
            c = cell(cells, arm, J, m)
            o = (c or {}).get("scores", {}).get("oracle", {})
            cov = o.get("coverage_share_median")
            if cov is None:
                continue
            if arm == "baseline":
                # a count baseline scores the same at both J here: one mark per scorer
                if m in seen:
                    continue
                seen.add(m)
                J = 10.0
            mark(ax, cov, o["f1_mean"], m, J, ms=5.0)
            n += 1
        half = ax.axvline(0.5, color="0.45", ls=":", lw=1.2, zorder=1)
        if r == 0:
            ax.legend([half], ["half the recording covered, 50 %"], loc="upper right",
                      frameon=False, handlelength=2.2)
        ax.set_xscale("logit")
        ax.set_xlim(0.0025, 0.992)
        ax.set_ylim(*YLIM_B)
        ax.set_yticks([0.4, 0.5, 0.6, 0.7])
        ax.grid(axis="x", color="0.9", lw=0.8, zorder=0)
        unit = "scorers" if arm == "baseline" else "models"
        # horizontal, so a row only has to be as tall as its marks need
        ax.set_ylabel(f"{label}\n({n} {unit})", fontsize=9.5, rotation=0, ha="right",
                      va="center", ma="right", labelpad=6)
        if r < len(B_ROWS) - 1:
            ax.tick_params(labelbottom=False)
        ax.minorticks_off()
        flush(ax, tether=True)
    xb = axes_b[-1]
    xb.set_xticks(COVER_TICKS, [f"{100 * t:g} %" for t in COVER_TICKS])
    xb.minorticks_off()
    xb.set_xlabel("share of the held-out recording the detections cover, in % "
                  "(logit scale, which spreads both ends)\nmedian over recordings and fits; a "
                  "mark nudged clear of another keeps a hairline to its own share")

    # C: the paired checks, four arm lanes inside every check, the chance half above the moving one
    # the lower row carries the wider range of shares, so it gets the taller half
    gc = band(9.70, 12.90, len(CHECK_ROWS), hspace=0.67, height_ratios=[0.82, 1.18])
    axes_c = []
    offs = [-0.33, -0.11, 0.11, 0.33]
    for r, (ylim, yticks, lane_y, groups) in enumerate(CHECK_ROWS):
        cx = fig.add_subplot(gc[r])
        axes_c.append(cx)
        x = 0.0
        ticks, labels, bounds = [], [], []
        for group, checks in groups:
            start = x
            for key, lab in checks:
                for (arm, lane), off in zip(C_LANES, offs):
                    for J, m in members(arm):
                        c = cell(cells, arm, J, m)
                        if c and key in c["checks"]:
                            mark(cx, x + off, c["checks"][key]["share_mean"], m, J, ms=4.2)
                    cx.text(x + off, lane_y, lane, ha="center", va="bottom", fontsize=9.5,
                            color="0.35")
                ticks.append(x)
                labels.append(lab)
                x += 1
            bounds.append((start, x - 1, group))
            x += 0.3
        for i, (lo, hi, group) in enumerate(bounds):
            if i:
                cx.axvline(lo - 0.65, color="0.75", lw=0.8)
            cx.annotate(group, xy=((lo + hi) / 2, 0), xycoords=("data", "axes fraction"),
                        xytext=(0, -34), textcoords="offset points", ha="center", va="top",
                        fontsize=9.5, fontweight="bold", annotation_clip=False)
        chance = cx.axhline(0.5, color="0.45", ls=":", lw=1.2, zorder=1)
        if r == 0:
            cx.legend([chance], ["chance, 0.5"], loc="lower left", frameon=False,
                      handlelength=2.2)
        cx.set_xticks(ticks, labels, fontsize=9.5)
        cx.set_xlim(-0.52, x - 0.78)
        cx.set_ylim(*ylim)
        cx.set_yticks(yticks)
        flush(cx, cap_px=30.0)
    axes_c[-1].set_xlabel(
        "paired check. Lanes in every check, left to right: sup, supervised; sim, trained against "
        "rigid shift on simulated\nrecordings; real, trained against rigid shift on real "
        "recordings; count, the count baselines. Both J shown in every\nlane that has one. "
        f"Small J = {j_small:g} s. The untrained arm is not drawn.", labelpad=30)

    for ax, letter in ((axes_a[0], "A"), (axes_b[0], "B"), (axes_c[0], "C")):
        p = ax.get_position()
        fig.text(0.015, p.y1 + 0.004, letter, fontsize=13, fontweight="bold", va="bottom")
    # one quantity label per stack, left of its rows; panel B's sits outside its row names
    for stack, dx, label in (
            (axes_a, 0.105, "planted-truth F1, held-out fold,\nat the label-free threshold"),
            (axes_b, 0.185, "planted-truth F1, held-out fold,\nat the truth-reading threshold"),
            (axes_c, 0.105, "share of held-out real crops where\n"
                            "the real crop scores higher (ties: half)")):
        top, bot = stack[0].get_position(), stack[-1].get_position()
        fig.text(top.x0 - dx, (top.y1 + bot.y0) / 2, label, rotation=90, ha="center",
                 va="center", fontsize=10.5, ma="center")
    save(fig, "tube_ssl_fig.png", a, subfolder="tube_self_supervised", dpi=DPI)


if __name__ == "__main__":
    main()
