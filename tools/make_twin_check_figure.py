#!/usr/bin/env python3
"""Draw the twin check: how each scorer ranks a synthetic twin against its own rigid shift, cell by
cell, with what each cell can and cannot show written above it.

    python tools/make_twin_check_figure.py --summary <run>/summary.json
        [--out <folder>] [--also <folder>]

Reads the ``small_j_check`` block of ``summary.json`` (``tools/summarize_tube_self_supervised.py``,
digesting ``tools/check_small_j_mixes_events.py``); writes ``twin_check_fig.png``. Exploratory.

Every mark is a share of crop pairs where the twin scores above its rigid shift (ties count half;
0.5 is chance), scored with the paired checks' crops and rule. Within each twin-by-*J* cell, left to
right: the checkpoints trained against rigid shift on real recordings at *J* = 10 s, then at 20 s
(each mark pooled over its fits, a thin line spanning the per-fit range), one supervised fit per
architecture, one untrained model per architecture, and the three zero-parameter baselines.

* **A** — *J* = 1.6 s: the events twin, the events twin with independent modulation, the
  shared-modulation twin, and the independent-modulation null.
* **B** — *J* = 10 s and 20 s: the shared-modulation twin beside its own independent-modulation
  null at each displacement.

The figure describes the check; it does not test anything. The gray band is a rough scale for
sampling noise, not an interval, and the lane above each panel says where a cell has no power or
sits at the ceiling.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from figure_destination import add_arguments, save  # noqa: E402
from matplotlib.lines import Line2D  # noqa: E402
from matplotlib.patches import Patch  # noqa: E402
from matplotlib.transforms import blended_transform_factory  # noqa: E402

plt.rcParams.update({"font.size": 10.5, "axes.labelsize": 10.5, "xtick.labelsize": 9.5,
                     "ytick.labelsize": 10, "legend.fontsize": 9.5})

MODELS = {"line": ("#2a78d6", "o"), "line_length": ("#eb6834", "s"),
          "line_bound": ("#1baf7a", "D"), "tube": ("#6b6b6b", "o"), "tube_guard": ("#a8a8a8", "s")}
"""The report's inks and shapes (``tools/make_tube_ssl_figure.py``)."""
BASELINES = {"count_share": "^", "count_excess": "P", "slow_modulation": "X"}
BASELINE_LABEL = {"count_share": "count share", "count_excess": "count excess",
                  "slow_modulation": "slow modulation"}
LANES = [("trained on real, J 10 s, {m}", list(MODELS)),
         ("trained on real, J 20 s, {m}", list(MODELS)),
         ("supervised, {m}", list(MODELS)),
         ("untrained, {m}", list(MODELS)),
         ("{m}", list(BASELINES))]
"""Scorer lanes within a cell, left to right, as ``small_j_check.groups`` names the groups."""
TWIN_LABEL = {"events": "events,\nno modulation",
              "independent_modulation_with_events": "events plus\nindependent\nmodulation",
              "shared_modulation": "shared\nmodulation,\nno events",
              "independent_modulation": "independent\nmodulation,\nno events (null)"}
PANELS = [("A", [("events", "1.6"), ("independent_modulation_with_events", "1.6"),
                 ("shared_modulation", "1.6"), ("independent_modulation", "1.6")]),
          ("B", [("shared_modulation", "10"), ("independent_modulation", "10"),
                 ("shared_modulation", "20"), ("independent_modulation", "20")])]
SE_120 = 0.045
"""Binomial standard error of a share near 0.5 over 120 crop pairs, sqrt(0.25 / 120)."""
SLOT_W = [0.037, 0.037, 0.037, 0.03, 0.052]
"""Width of one mark slot in each lane, in cell widths: the black baseline marks are larger."""
LANE_GAP = 0.022
"""Extra gap between lanes, in cell widths."""


def lane_x(li, k):
    """Offset of mark ``k`` of lane ``li`` from its cell center."""
    widths = [len(members) * w for (_, members), w in zip(LANES, SLOT_W)]
    total = sum(widths) + (len(widths) - 1) * LANE_GAP
    return -total / 2 + sum(widths[:li]) + li * LANE_GAP + (k + 0.5) * SLOT_W[li]


def mark(ax, x, cell_doc, m, lane):
    y = cell_doc["pooled"]
    if m in BASELINES:
        ax.plot([x], [y], BASELINES[m], ms=7.0, color="#111111", mew=0.8, zorder=4)
        return
    c, mk = MODELS[m]
    if lane in (0, 1):
        ax.plot([x, x], [cell_doc["per_fit_min"], cell_doc["per_fit_max"]], color=c, lw=0.9,
                alpha=0.8, zorder=2, solid_capstyle="butt")
        ax.plot([x], [y], mk, ms=5.0, color=c, mec=c, mew=1.0, zorder=3)
    elif lane == 2:
        ax.plot([x], [y], mk, ms=5.2, color=c, mec="#111111", mew=1.0, zorder=3)
    else:
        ax.plot([x], [y], mk, ms=4.2, color="white", mec=c, mew=1.1, zorder=3)


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--summary", required=True)
    add_arguments(ap)
    a = ap.parse_args(argv)
    s = json.loads(Path(a.summary).read_text())
    block = s["small_j_check"]
    groups, meta = block["groups"], block["meta"]
    n_twins, n_draws = meta["twins"], meta["draws_per_twin"]
    n_fits = sorted({g["n_fits"] for name, g in groups.items() if name.startswith("trained")})
    n_sup = sorted({g["n_fits"] for name, g in groups.items() if name.startswith("supervised")})

    def share(group, key):
        return groups[group][key]["pooled"]

    # What each cell can show, computed from the data rather than typed in.
    at_ceiling = sum(share(prefix.format(m=m), "events|1.6") >= 0.995
                     for prefix, members in LANES for m in members)
    n_scorers = sum(len(members) for _, members in LANES)
    sm_shared, sm_null = share("slow_modulation", "shared_modulation|1.6"), \
        share("slow_modulation", "independent_modulation|1.6")
    ce20 = share("count_excess", "shared_modulation|20")
    ce10 = share("count_excess", "shared_modulation|10")

    def null_header(J):
        low = min(g[f"independent_modulation|{J}"]["per_fit_min"] for g in groups.values())
        return f"null: must read chance;\nthe lowest single fit\nreads {low:.3f} here"

    headers = {
        ("A", 0): f"at the ceiling: {at_ceiling} of {n_scorers}\nmarks read ≥ 0.995, so "
                  "how\nstrongly cannot be compared\n(planted events: 1 frame of jitter)",
        ("A", 1): "",
        ("A", 2): f"no power to see modulation:\nslow modulation reads {sm_shared:.3f}\n"
                  f"here and {sm_null:.3f} on its null",
        ("A", 3): null_header("1.6"),
        ("B", 0): f"not modulation alone: count\nexcess reads {ce10:.3f} through\n"
                  "coincidences that rise with\nthe square of the rate",
        ("B", 1): null_header("10"),
        ("B", 2): f"not modulation alone: count\nexcess reads {ce20:.3f} here",
        ("B", 3): null_header("20"),
    }

    fig = plt.figure(figsize=(11.0, 11.8))
    gs = fig.add_gridspec(2, 1, left=0.1, right=0.93, top=0.915, bottom=0.33, hspace=0.62)
    for row, (letter, cells) in enumerate(PANELS):
        ax = fig.add_subplot(gs[row, 0])
        ax.axhspan(0.5 - 2 * SE_120, 0.5 + 2 * SE_120, color="0.9", lw=0, zorder=0)
        ax.axhline(0.5, color="0.45", ls=":", lw=1.1, zorder=1)
        for ci, (twin, J) in enumerate(cells):
            key = f"{twin}|{J}"
            for li, (prefix, members) in enumerate(LANES):
                for k, m in enumerate(members):
                    g = groups.get(prefix.format(m=m))
                    if g and key in g:
                        mark(ax, ci + lane_x(li, k), g[key], m, li)
            if ci:
                ax.axvline(ci - 0.5, color="0.75", lw=0.8)
        tr = blended_transform_factory(ax.transData, ax.transAxes)
        for ci in range(len(cells)):
            ax.text(ci, 1.03, headers[(letter, ci)], transform=tr, ha="center", va="bottom",
                    fontsize=9.5, color="0.2", linespacing=1.15)
        ax.set_xticks(range(len(cells)),
                      [f"{TWIN_LABEL[t]}\nJ = {float(J):g} s" for t, J in cells])
        ax.set_xlim(-0.5, len(cells) - 0.5)
        ax.set_ylim(0.3, 1.05)
        ax.set_yticks([0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0])
        ax.set_ylabel("share of crop pairs where the twin\nscores above its rigid shift "
                      "(ties: half)")
        ax.text(-0.085, 1.03, letter, transform=ax.transAxes, fontsize=13, fontweight="bold",
                va="bottom")
        ax.annotate("chance", xy=(1.0, 0.5), xycoords=("axes fraction", "data"),
                    xytext=(4, 0), textcoords="offset points", ha="left", va="center",
                    fontsize=9.5, color="0.35", annotation_clip=False)

    lx = fig.add_axes([0.1, 0.085, 0.85, 0.155])
    lx.axis("off")
    h_models = [Line2D([], [], color=c, marker=mk, ls="", ms=7, mec=c, label=m)
                for m, (c, mk) in MODELS.items()]
    h_base = [Line2D([], [], color="#111111", marker=mk, ls="", ms=8, mew=0.8,
                     label=f"{BASELINE_LABEL[b]} (no parameters)") for b, mk in BASELINES.items()]
    h_arms = [Line2D([0, 0], [0, 1], color="0.3", marker="o", ms=7, lw=0.9,
                     label=f"trained against rigid shift on real recordings: mark pooled over "
                           f"{' or '.join(map(str, n_fits))} fits,\nline spanning the per-fit "
                           "range; first lane J = 10 s, second J = 20 s"),
              Line2D([], [], color="0.3", marker="o", ls="", ms=7, mec="#111111",
                     label=f"supervised: {' or '.join(map(str, n_sup))} fit per architecture "
                           "(seed 0), black edge"),
              Line2D([], [], color="0.3", marker="o", ls="", ms=5.5, mfc="white", mew=1.1,
                     label="untrained: 1 model per architecture, small open mark"),
              Line2D([], [], color="0.45", ls=":", lw=1.1, label="chance, 0.5"),
              Patch(facecolor="0.9", edgecolor="none",
                    label=f"0.5 ± {2 * SE_120:.2f}: about ±2 binomial standard errors for\n"
                          "about 120 crop pairs, ignoring that the pairs share twins")]
    leg1 = lx.legend(handles=h_arms, loc="upper left", bbox_to_anchor=(0.0, 1.0), frameon=False,
                     title="within each cell, left to right:", title_fontsize=9.5,
                     alignment="left", handlelength=1.6)
    lx.add_artist(leg1)
    lx.legend(handles=h_models + h_base, loc="upper left", bbox_to_anchor=(0.6, 1.0),
              frameon=False, title="architecture, or baseline", title_fontsize=9.5,
              alignment="left", handlelength=1.2, ncol=2, columnspacing=1.2)
    fig.text(0.1, 0.008, "\n".join([
        f"Synthetic twins at participation {meta['participation']:g}: {n_twins} twins × "
        f"{n_draws} draws per scorer, and the events twin is the same {n_twins} recordings in "
        "both draws.",
        f"Modulation: a {meta['modulation']['period_sec']:g} s cycle of depth "
        f"{meta['modulation']['depth']:g}. J: the rigid-shift displacement. Only checkpoints "
        "trained on real recordings were scored,",
        "not those trained on simulated recordings. Supervised and untrained are 1 fit per "
        "architecture each, so their spread across fits is not measured."]),
        ha="left", va="bottom", fontsize=9.5, color="0.3", linespacing=1.3)
    save(fig, "twin_check_fig.png", a, subfolder="tube_self_supervised")


if __name__ == "__main__":
    main()
