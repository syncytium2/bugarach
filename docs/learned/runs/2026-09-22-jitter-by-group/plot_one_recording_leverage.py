"""Figure 3: what one recording does to a between-group difference.

    python docs/learned/runs/2026-09-22-jitter-by-group/plot_one_recording_leverage.py

A group's width is read off its POOLED onset-pair counts, so a recording weighs by the pairs it
brings. Figure 2's raw curves showed one ORX recording carrying a bump near 7.5 s lag on the slow
stream; this asks what that recording does to the answer. Per stream, each group's width as
recorded and again with its own most influential recording removed, with the four-way spread and
its permutation p for the as-recorded case and after dropping the single biggest mover.

Reads ``jitter_correlogram.json`` (the ``leave_one_out`` and ``without_most_influential`` blocks,
both written by ``tools/measure_jitter_correlogram.py --by-group``) and writes
``one_recording_leverage.png`` to ``<darkroom>/bugarach/correlogram/`` unless ``--out`` says
otherwise; ``--also`` takes a copy.
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
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(REPO / "src"))

from plot_jitter_by_group import FOLDER, GROUP_INK, GROUP_ORDER, INK, MUTED, panel  # noqa: E402


def draw(rec, out: Path) -> Path:
    fig, axes = plt.subplots(1, 2, figsize=(11.5, 4.3))
    span, summaries = [], []
    for col, stream in enumerate(("fast", "slow")):
        st = rec["streams"][stream]
        groups, c = st["groups"], st["contrasts"]["hwhm"]
        names = [g for g in GROUP_ORDER if g in groups]
        ax = axes[col]
        for i, g in enumerate(names):
            r = groups[g]["hwhm"]
            loo = r["leave_one_out"]
            span.extend([r["real_sec"], loo["without_sec"]])
            ax.plot([r["real_sec"], loo["without_sec"]], [i, i], color=GROUP_INK[g], lw=1.0,
                    ls=":", zorder=1)
            ax.plot([r["real_sec"]], [i], "o", color=GROUP_INK[g], ms=7, zorder=3)
            ax.plot([loo["without_sec"]], [i], "s", ms=7, mfc="none", mec=GROUP_INK[g], mew=1.5,
                    zorder=3)
            ax.text(max(r["real_sec"], loo["without_sec"]) + 0.006, i - 0.30,
                    f"{loo['delta_sec']:+.3f} s without {loo['slice_id']}",
                    fontsize=6.2, color=MUTED, va="center")
        ax.set_yticks(range(len(names)))
        ax.set_yticklabels([f"{g} ({groups[g]['recordings']} recordings)" for g in names])
        ax.set_ylim(len(names) - 0.4, -0.9)
        ax.set_ylabel(f"{stream} · group_id")
        ax.set_xlabel("half-width at half height (s)")

        w = c["without_most_influential"]
        summaries.append(f"as recorded: spread {c['spread_sec']:.3f} s, "
                         f"p = {c['permutation']['p_any_difference']:.3f}\n"
                         f"without {w['slice_id']}: spread {w['spread_sec']:.3f} s, "
                         f"p = {w['p_any_difference']:.3f}")
        panel(ax, "a" if col == 0 else "b")
    lo, hi = min(span), max(span)
    pad = 0.06 * (hi - lo)
    for ax in axes:
        ax.set_xlim(lo - pad, hi + 5.5 * pad)
    axes[1].legend(handles=[
        Line2D([], [], ls="", marker="o", ms=6, color=MUTED, label="as recorded"),
        Line2D([], [], ls="", marker="s", ms=6, mfc="none", mec=MUTED, mew=1.4,
               label="without that group's most influential recording")],
        fontsize=6.5, frameon=False, loc="lower left", handletextpad=0.4, borderpad=0.1)

    stamp = rec["dataset"]
    caption = "\n".join([
        "Figure 3. One recording's leverage on a group's width. Filled dot: the group's "
        "half-width at half height as recorded, read off its pooled onset-pair",
        "counts. Open square: the same after removing the one recording that moves it most, named "
        "beside it. a: fast, where there was no difference to begin with",
        "and removing OVX's biggest mover leaves none (p = 0.098). b: slow — where ORX, the "
        "narrowest group and the whole reason the four-way spread came close",
        "to its null, moves 0.183 s → 0.229 s when 20250806_174 is dropped and the spread falls "
        "to the null's own median. So the slow difference is one recording,",
        f"not a group effect. Baseline windows only (FOUNDATIONS §9), {stamp['name']}.",
    ])
    fig.text(0.005, 0.004, caption, fontsize=7, color=MUTED, va="bottom")
    fig.tight_layout(rect=(0, 0.30, 1, 0.985))
    # The per-stream verdicts sit under their own panel, as figure text: an axes-relative text
    # this far below the axis joins the axes' tight bbox and shoves the panels up the page.
    for ax, text in zip(axes, summaries):
        bb = ax.get_position()
        fig.text(bb.x0 + bb.width / 2, 0.205, text, fontsize=7.5, color=INK, ha="center",
                 va="bottom")
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, dpi=170)
    plt.close(fig)
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--run", type=Path, default=HERE)
    ap.add_argument("--out", type=Path, default=None,
                    help=f"default: <darkroom>/bugarach/{FOLDER}")
    ap.add_argument("--also", type=Path, default=None)
    a = ap.parse_args(argv)

    from bugarach.paths import darkroom

    rec = json.loads((a.run / "jitter_correlogram.json").read_text(encoding="utf-8"))
    if not rec["streams"]["fast"]["contrasts"]["hwhm"].get("without_most_influential"):
        raise SystemExit("this record predates the leave-one-out block: rerun the measure")
    out = (a.out or (darkroom() / FOLDER)) / "one_recording_leverage.png"
    draw(rec, out)
    print(f"wrote {out}")
    if a.also:
        a.also.mkdir(parents=True, exist_ok=True)
        shutil.copy2(out, a.also / out.name)
        print(f"copied to {a.also / out.name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
