"""Figure 2: the correlograms as measured — no shoulder subtracted, no peak normalised.

    python docs/learned/runs/2026-09-22-jitter-by-group/plot_raw_correlograms.py

Figure 1's peak panels answer "how wide", so they subtract the 5–10 s level and divide by the
zero-lag height — which throws away two things a reader asks about next: how TALL each group's
peak is, and what the curve does out at the lags the width is measured against. Tony, 2026-09-23:
*"what do the raw correlograms look like? these are minus the 5-10s lag"*. This draws the
unmodified excess.

Left column: the whole curve out to 10 s lag, on each stream's own scale. Right column: the same
curves with the zero-lag spike off the top, so the shoulder is legible, and each group's own
5–10 s mean — the level Figure 1 subtracts — drawn as a dashed line in its colour.

Reads ``jitter_correlogram.json`` from this folder and writes ``raw_correlograms.png`` to
``<darkroom>/bugarach/correlogram/`` unless ``--out`` says otherwise; ``--also`` takes a copy.
Palette, panel tags and the darkroom folder come from ``plot_jitter_by_group`` beside it.
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

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(REPO / "src"))

from plot_jitter_by_group import FOLDER, GROUP_INK, GROUP_ORDER, INK, MUTED, panel  # noqa: E402

ZOOM_FROM_SEC = 0.8      # where the zoom column starts looking, past the peak's shoulder


def draw(rec, out: Path) -> Path:
    dt = rec["dt"]
    sh = [int(round(s / dt)) for s in rec["shoulder_sec"]]
    fig, axes = plt.subplots(2, 2, figsize=(11.5, 6.4))
    for row, stream in enumerate(("fast", "slow")):
        st = rec["streams"][stream]
        groups = st["groups"]
        names = [g for g in GROUP_ORDER if g in groups]
        k = np.arange(len(st["real_excess"])) * dt

        for col in (0, 1):
            ax = axes[row, col]
            ax.axhline(0, color=MUTED, lw=0.8)
            ax.plot(k, st["real_excess"], color=INK, lw=2.0, ls="--", zorder=3,
                    label=f"all {st['recordings']} recordings pooled")
            for g in names:
                x = np.asarray(groups[g]["real_excess"], float)
                ax.plot(k, x, color=GROUP_INK[g], lw=1.4,
                        label=f"{g} · peak {x[0]:.1f} at zero lag")
                if col == 1:
                    lvl = float(np.nanmean(x[sh[0]:sh[1] + 1]))
                    ax.plot([5.0, 10.0], [lvl, lvl], color=GROUP_INK[g], lw=1.2, ls=":")
            ax.set_xlim(0, k[-1])
            ax.set_xlabel("lag between onsets in two different ROIs (s)" if row == 1 else "")

        axes[row, 0].set_ylabel(f"{stream} · excess coincidence")
        axes[row, 0].legend(fontsize=6.5, frameon=False, loc="upper right")
        panel(axes[row, 0], "a" if row == 0 else "c")

        ax = axes[row, 1]
        i0 = int(round(ZOOM_FROM_SEC / dt))
        tail = np.concatenate([np.asarray(groups[g]["real_excess"], float)[i0:] for g in names])
        lo, hi = float(np.nanmin(tail)), float(np.nanmax(tail))
        pad = 0.18 * (hi - lo)
        ax.set_ylim(lo - pad, hi + pad)
        ax.set_ylabel(f"{stream} · excess, peak off the top")
        panel(ax, "b" if row == 0 else "d")

    stamp = rec["dataset"]
    caption = "\n".join([
        "Figure 2. The same correlograms as measured, with nothing subtracted and nothing "
        "normalised. ROI = region of interest, one imaged cell. Excess coincidence is",
        "observed ÷ expected onset pairs − 1 at each 0.1 s lag, pooled within a group: 0 means no "
        "more pairs than the ROIs' own rates predict, and a negative value",
        "means fewer. a, c: the whole curve. b, d: the same, with the zero-lag spike above the "
        "frame, so the shoulder the width is measured against is legible;",
        "each group's dotted line is its own mean excess over 5–10 s. Figure 1's peak panels "
        "subtract that line and divide by the zero-lag height, which is what",
        "makes them comparable across groups and what hides the peak HEIGHTS shown here. "
        f"Baseline windows only (FOUNDATIONS §9), {stamp['name']}.",
    ])
    fig.text(0.005, 0.004, caption, fontsize=7, color=MUTED, va="bottom")
    fig.tight_layout(rect=(0, 0.125, 1, 0.985))
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
    out = (a.out or (darkroom() / FOLDER)) / "raw_correlograms.png"
    draw(rec, out)
    print(f"wrote {out}")
    if a.also:
        a.also.mkdir(parents=True, exist_ok=True)
        shutil.copy2(out, a.also / out.name)
        print(f"copied to {a.also / out.name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
