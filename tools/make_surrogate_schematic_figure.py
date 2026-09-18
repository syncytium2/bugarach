#!/usr/bin/env python3
"""Draw what each surrogate in the rigid-shift report does to a recording, on a toy raster.

    python tools/make_surrogate_schematic_figure.py [--out <folder>] [--also <folder>]

Writes ``surrogate_schematic_fig.png``. **Illustrative, not a measurement**: six synthetic ROIs over
one minute, with two coordinated events (every ROI within a fraction of a second, at 12 s and 38 s)
and a few onsets of background. Each row below the recording is one transform, with its offsets set
by hand so the picture is the same every time and reads at a glance:

* **rigid shift** — one offset per ROI, drawn within ±*J*; every ROI keeps its own intervals, the
  alignment between ROIs is broken, and onsets pushed past either end are dropped;
* **shared offset** — one offset for every ROI; the alignment is kept, so a detector of alignment
  should not tell it from the recording;
* **per-onset dither** — every onset moves on its own within ±*J*; alignment and each ROI's own
  intervals are both broken;
* **per-ROI circular shift** — one offset per ROI of any size, wrapped at the end; intervals are
  kept except the one across the wrap, and alignment is broken.

The raster is synthetic, so the figure is not bound by FOUNDATIONS §5 and has a repo copy. Nothing
is drawn on the rasters: what each row keeps and breaks sits in the text beside it.
"""

from __future__ import annotations

import argparse

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from figure_destination import add_arguments, save  # noqa: E402

plt.rcParams.update({"font.size": 10.5, "axes.labelsize": 10.5, "xtick.labelsize": 10,
                     "ytick.labelsize": 10})

LENGTH_SEC = 60.0
J_SEC = 10.0
EVENTS_SEC = (12.0, 38.0)
EVENT_JITTER_SEC = (0.0, 0.2, -0.1, 0.3, 0.1, -0.2)
BACKGROUND_SEC = ((3.0, 27.5, 55.0), (8.5, 47.0), (21.0, 51.5, 58.5), (5.5, 31.0),
                  (17.5, 44.5, 57.0), (1.5, 25.0, 49.0))
RIGID_OFFSETS_SEC = (7.0, -4.0, 9.0, -8.0, 3.0, -6.0)
SHARED_OFFSET_SEC = 6.0
CIRCULAR_OFFSETS_SEC = (23.0, -17.0, 41.0, 8.0, -35.0, 29.0)
DITHER_SEED = 7


def recording():
    return [np.sort(np.array([e + j for e in EVENTS_SEC] + list(bg)))
            for j, bg in zip(EVENT_JITTER_SEC, BACKGROUND_SEC)]


def shifted(trains, offsets):
    """Move each train by its offset and drop what leaves the recording; return (trains, dropped)."""
    out, dropped = [], 0
    for t, off in zip(trains, offsets):
        moved = t + off
        keep = (moved >= 0) & (moved < LENGTH_SEC)
        dropped += int((~keep).sum())
        out.append(moved[keep])
    return out, dropped


def dithered(trains):
    rng = np.random.RandomState(DITHER_SEED)
    moved = [t + rng.uniform(-J_SEC, J_SEC, t.size) for t in trains]
    kept = [np.sort(m[(m >= 0) & (m < LENGTH_SEC)]) for m in moved]
    return kept, sum(m.size - k.size for m, k in zip(moved, kept))


def circular(trains):
    return [np.sort((t + off) % LENGTH_SEC) for t, off in zip(trains, CIRCULAR_OFFSETS_SEC)]


def onsets(n):
    return f"{n} onset" + ("" if n == 1 else "s")


def seconds_label(s):
    """Minutes-friendly tick labels, as the report's other time axes: 45s, 1m, 1m30s."""
    s = int(round(s))
    m, r = divmod(s, 60)
    return f"{r}s" if m == 0 else (f"{m}m" if r == 0 else f"{m}m{r}s")


def main(argv=None):
    ap = argparse.ArgumentParser()
    add_arguments(ap)
    a = ap.parse_args(argv)
    rec = recording()
    rigid, rigid_dropped = shifted(rec, RIGID_OFFSETS_SEC)
    shared, shared_dropped = shifted(rec, [SHARED_OFFSET_SEC] * len(rec))
    dither, dither_dropped = dithered(rec)
    rows = [
        ("recording", rec,
         "two coordinated events, at 12 s and 38 s,\nand a few background onsets"),
        (f"rigid shift\nJ = {J_SEC:g} s", rigid,
         "one offset per ROI, within ±J\nkeeps: each ROI's intervals\n"
         f"breaks: alignment between ROIs\n{onsets(rigid_dropped)} pushed past an end, dropped"),
        ("shared offset", shared,
         f"one offset, {SHARED_OFFSET_SEC:g} s, for every ROI\nkeeps: intervals and alignment\n"
         f"{onsets(shared_dropped)} pushed past the end, dropped"),
        (f"per-onset dither\nJ = {J_SEC:g} s", dither,
         "every onset moved on its own, within ±J\nbreaks: alignment and each ROI's intervals\n"
         f"{onsets(dither_dropped)} pushed past an end, dropped"),
        ("per-ROI\ncircular shift", circular(rec),
         "one offset per ROI, any size, wrapped\nkeeps: each ROI's intervals but one\n"
         "breaks: alignment between ROIs"),
    ]
    fig, axes = plt.subplots(len(rows), 1, figsize=(10.5, 1.45 * len(rows) + 0.8), sharex=True)
    n_roi = len(rec)
    for ax, (name, trains, note) in zip(axes, rows):
        ax.eventplot(trains, lineoffsets=np.arange(n_roi), linelengths=0.7, linewidths=1.6,
                     colors="black")
        ax.set_ylim(-0.7, n_roi - 0.3)
        ax.set_yticks([])
        ax.set_ylabel(f"{name}\n{n_roi} ROIs", rotation=0, ha="right", va="center", labelpad=8)
        ax.set_xlim(0, LENGTH_SEC)
        for side in ("top", "right"):
            ax.spines[side].set_visible(False)
        ax.text(1.02, 0.5, note, transform=ax.transAxes, ha="left", va="center", fontsize=9.5,
                color="0.2")
    ticks = np.arange(0, LENGTH_SEC + 1, 15)
    axes[-1].set_xticks(ticks, [seconds_label(t) for t in ticks])
    axes[-1].set_xlabel("time in a synthetic one-minute recording\n"
                        "(its ends are a far larger share of it than of a real one)")
    fig.subplots_adjust(left=0.17, right=0.66, top=0.98, bottom=0.1, hspace=0.25)
    save(fig, "surrogate_schematic_fig.png", a, subfolder="tube_self_supervised")


if __name__ == "__main__":
    main()
