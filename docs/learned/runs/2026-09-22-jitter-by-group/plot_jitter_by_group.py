"""Figure for the per-group onset correlogram: are the peak widths different between the groups?

    python docs/learned/runs/2026-09-22-jitter-by-group/plot_jitter_by_group.py
    python docs/learned/runs/2026-09-22-jitter-by-group/plot_jitter_by_group.py --also <repo folder>

Reads ``jitter_correlogram.json`` from this folder — the output of
``tools/measure_jitter_correlogram.py --by-group`` — and draws six panels, one row per stream:

* the shoulder-subtracted correlogram peak per group, normalised to its own zero-lag height, which
  is the shape the width is read off;
* the half-width at half height per group with its mouse-clustered interval;
* the label-permutation null for the spread (widest group minus narrowest) with the observed
  spread marked — the test of whether the widths differ at all.

Writes ``jitter_by_group.png`` to ``<darkroom>/bugarach/correlogram/`` unless ``--out`` says
otherwise, and copies it to ``--also`` when given. Group colours and order are
``tools/make_slow_comodulation_figure.py``'s, so the correlogram figures read as one family.
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

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
sys.path.insert(0, str(REPO / "src"))

from bugarach.groups import GROUP_ORDER  # noqa: E402  (DI, OVX, MALE, ORX — Tony, 2026-09-23)

FOLDER = "correlogram"                   # the darkroom folder Tony asked the figures to gather in
GROUP_INK = {"DI": "#0f9fb5", "MALE": "#b8860b", "ORX": "#6b3e26", "OVX": "#c51b7d"}
INK, MUTED = "#0b0b0b", "#52514e"
PEAK_LAG_SEC = 3.0

plt.rcParams.update({"font.size": 9, "axes.spines.top": False, "axes.spines.right": False,
                     "axes.edgecolor": MUTED, "xtick.color": MUTED, "ytick.color": MUTED,
                     "axes.labelcolor": INK})


def panel(ax, letter):
    """The panel's tag, in its top-left corner and clear of the marks."""
    ax.text(-0.005, 1.06, letter, transform=ax.transAxes, fontsize=11, fontweight="bold",
            color=INK, ha="right", va="top")


def shape(excess, dt, n_peak, shoulder):
    """The peak with the 5-10 s level removed, divided by its own zero-lag height."""
    x = np.asarray(excess, float)
    p = x[:n_peak + 1] - np.nanmean(x[shoulder[0]:shoulder[1] + 1])
    return p / p[0]


def draw(rec, out: Path) -> Path:
    dt = rec["dt"]
    n_peak = int(round(PEAK_LAG_SEC / dt))
    sh = [int(round(s / dt)) for s in rec["shoulder_sec"]]
    k = np.arange(n_peak + 1) * dt
    fig, axes = plt.subplots(2, 3, figsize=(12.5, 6.6),
                             gridspec_kw={"width_ratios": [1.25, 1.0, 1.0]})
    # Both right-hand columns run on one scale across the two streams, so fast and slow are read
    # against each other rather than each against its own zoom (Tony, 2026-09-22).
    span: list[float] = []              # the width column
    spread_span: list[float] = []       # the permutation column
    for row, stream in enumerate(("fast", "slow")):
        st = rec["streams"][stream]
        groups = st["groups"]
        names = [g for g in GROUP_ORDER if g in groups]

        ax = axes[row, 0]
        ax.axhline(0.5, color=MUTED, lw=0.6, ls=":")
        ax.plot(k, shape(st["real_excess"], dt, n_peak, sh), color=INK, lw=2.2, ls="--",
                label=f"all {st['recordings']} recordings pooled", zorder=1)
        for g in names:
            r = groups[g]
            ax.plot(k, shape(r["real_excess"], dt, n_peak, sh), color=GROUP_INK[g], lw=1.6,
                    label=f"{g} · {r['recordings']} recordings, {r['mice']} mice, "
                          f"{r['onsets']:,} onsets")
        ax.set_xlim(0, PEAK_LAG_SEC)
        ax.set_ylim(-0.15, 1.05)
        ax.set_ylabel(f"{stream} · peak ÷ its own height at zero lag")
        ax.legend(fontsize=6.5, frameon=False, loc="upper right")
        panel(ax, "a" if row == 0 else "d")

        ax = axes[row, 1]
        for i, g in enumerate(names):
            r = groups[g]["hwhm"]
            lo, hi = r["real_interval"]
            per = [x for x in r.get("per_recording_sec", []) if x is not None]
            if per:
                # One dot per recording. The vertical offset is seeded noise, not anything about
                # the recording: fanning the dots by rank instead would draw a diagonal that reads
                # as a trend against an axis that means nothing. Seeded, so a rerun redraws it.
                y = np.random.RandomState(17 + i).uniform(-0.2, 0.2, len(per))
                ax.plot(per, i + y, "o", color=GROUP_INK[g], ms=2.4, alpha=0.55, lw=0,
                        mew=0, zorder=1)
            ax.plot([lo, hi], [i, i], color=GROUP_INK[g], lw=2, zorder=2)
            ax.plot([r["real_sec"]], [i], "o", color=GROUP_INK[g], ms=6, zorder=4)
            if r.get("mean_of_recordings_sec") is not None:
                ax.plot([r["mean_of_recordings_sec"]], [i], "o", ms=8, mfc="none",
                        mec=GROUP_INK[g], mew=1.5, zorder=3)
            ax.text(hi + 0.012, i, f"{r['real_sec']:.3f} s", va="center", fontsize=7.5,
                    color=GROUP_INK[g])
            gone = r.get("recordings_with_no_peak", 0)
            if gone:
                ax.text(0.995, i + 0.34, f"{gone} of {groups[g]['recordings']} recordings, no peak",
                        transform=ax.get_yaxis_transform(), ha="right", va="center",
                        fontsize=5.8, color=MUTED)
        if row == 0:
            key = [Line2D([], [], ls="", marker="o", ms=2.4, color=MUTED, alpha=0.55,
                          label="one recording"),
                   Line2D([], [], ls="", marker="o", ms=7, mfc="none", mec=MUTED, mew=1.4,
                          label="mean over recordings"),
                   Line2D([], [], ls="-", marker="o", ms=5, color=MUTED, lw=2,
                          label="pooled width, 95% interval")]
            ax.legend(handles=key, fontsize=6, frameon=False, loc="upper right",
                      handletextpad=0.4, borderpad=0.1, labelspacing=0.25)
        pooled = st["hwhm"]
        ax.axvline(pooled["real_sec"], color=INK, lw=1.4, ls="--")
        ax.text(pooled["real_sec"], 1.01, f"pooled {pooled['real_sec']:.3f} s", fontsize=7,
                color=INK, ha="center", va="bottom", transform=ax.get_xaxis_transform())
        ax.set_yticks(range(len(names)))
        ax.set_yticklabels([f"{g} ({groups[g]['mice']} mice)" for g in names])
        ax.set_ylim(len(names) - 0.4, -0.8)
        for g in names:
            r = groups[g]["hwhm"]
            span.extend(r["real_interval"])
            span.extend(x for x in r.get("per_recording_sec", []) if x is not None)
        ax.set_ylabel(f"{stream} · group_id")
        ax.set_xlabel("half-width at half height (s)")
        panel(ax, "b" if row == 0 else "e")

        ax = axes[row, 2]
        c = st["contrasts"]["hwhm"]
        perm = c["permutation"]
        null_med, null_95 = perm["null_median_sec"], perm["null_95th_sec"]
        ax.axvspan(0, null_95, color="#dddddd", alpha=0.7, lw=0)
        ax.axvline(null_med, color=MUTED, lw=1.2)
        ax.axvline(c["spread_sec"], color="#b2182b", lw=2.2)
        ax.text(null_95, 0.86, f" null 95th {null_95:.3f} s", fontsize=7, color=MUTED,
                transform=ax.get_xaxis_transform())
        ax.text(c["spread_sec"], 0.50, f" observed {c['spread_sec']:.3f} s", fontsize=7.5,
                color="#b2182b", transform=ax.get_xaxis_transform())
        ax.text(0.5, 0.20, f"p(any difference) = {perm['p_any_difference']:.3f}\n"
                           f"{perm['draws']:,} label permutations",
                transform=ax.transAxes, fontsize=8, color=INK, ha="center")
        ax.set_yticks([])
        spread_span.extend([null_95, c["spread_sec"]])
        ax.set_ylabel(f"{stream} · spread of the four widths")
        ax.set_xlabel("widest group − narrowest group (s)")
        panel(ax, "c" if row == 0 else "f")

    # One x-axis for the shape column: both rows cover the same 0-3 s lag, so the label goes on
    # the bottom panel only.
    axes[1, 0].set_xlabel("lag between onsets in two different ROIs (s)")
    lo, hi = min(span), max(span)
    pad = 0.09 * (hi - lo)
    for ax in (axes[0, 1], axes[1, 1]):
        ax.set_xlim(lo - pad, hi + 2.4 * pad)       # room on the right for the value labels
    for ax in (axes[0, 2], axes[1, 2]):
        ax.set_xlim(0, max(spread_span) * 1.45)     # room on the right for the null's label
    stamp = rec["dataset"]
    mice = sum(g["mice"] for g in rec["streams"]["fast"]["groups"].values())
    caption = "\n".join([
        "Figure 1. The cross-ROI onset correlogram's peak width by group_id, fast (top row) and "
        "slow (bottom row). ROI = region of interest, one imaged cell;",
        "HWHM = half-width at half height, the width statistic; a shared moment's timing spread "
        "is what the HWHM is a measure of.",
        "a, d: each group's correlogram peak, with the mean excess at 5–10 s lag subtracted and "
        "divided by its own height at zero lag, so the panel shows shape alone —",
        "the dotted line at 0.5 is the height the HWHM is read at. b, e: one small dot per "
        "recording, an open circle at their mean, and the filled dot with bar for the group's",
        "own width — read off that group's POOLED onset-pair counts, with a 95% interval over "
        f"{rec.get('boot_draws', 0):,} resamples of its MICE "
        f"({rec['streams']['fast']['recordings']} recordings,",
        f"{mice} mice). Both streams share one width scale. A recording with too few onset pairs "
        "has no measurable peak and no dot; where that happens the count is under the row.",
        "c, f: the spread — widest group minus narrowest — after mouse→group labels are shuffled "
        "with each group's number of mice",
        "held fixed — grey to that stream's own null 95th percentile, the observed spread in red, "
        "and these two share one scale as well.",
        f"Baseline windows only (FOUNDATIONS §9), {stamp['name']}.",
    ])
    fig.text(0.005, 0.004, caption, fontsize=7, color=MUTED, va="bottom")
    fig.tight_layout(rect=(0, 0.155, 1, 0.985))   # the caption runs to six lines; leave it room
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, dpi=170)
    plt.close(fig)
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--run", type=Path, default=HERE, help="folder holding jitter_correlogram.json")
    ap.add_argument("--out", type=Path, default=None,
                    help=f"default: <darkroom>/bugarach/{FOLDER}")
    ap.add_argument("--also", type=Path, default=None, help="a second copy, e.g. the repo folder")
    a = ap.parse_args(argv)

    from bugarach.paths import darkroom

    rec = json.loads((a.run / "jitter_correlogram.json").read_text(encoding="utf-8"))
    if "groups" not in rec["streams"]["fast"]:
        raise SystemExit("this record has no per-group block: rerun the measure with --by-group")
    out = (a.out or (darkroom() / FOLDER)) / "jitter_by_group.png"
    draw(rec, out)
    print(f"wrote {out}")
    if a.also:
        a.also.mkdir(parents=True, exist_ok=True)
        shutil.copy2(out, a.also / out.name)
        print(f"copied to {a.also / out.name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
