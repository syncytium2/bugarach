#!/usr/bin/env python3
"""Draw the two gates the label-free run stood on, rebuilt so each can fail.

    python tools/make_rigid_shift_gates_figure.py --run <folder> --out <folder>

Reads ``controls_lab/results.json`` (``tools/look_rigid_shift_controls.py --leak-only``) and
``aggregate_leak/results.json`` (``tools/tube_aggregate_leak.py``); writes
``rigid_shift_gates_fig.png``. Exploratory.

* **Panels A and B, the leak controls on the lab fast and slow streams.** A per-ROI classifier's
  accuracy at telling a recording from rigid shift, from a shared offset (should be chance), and
  from per-onset dither at the same displacement — the positive control, which must separate or
  the chance readings beside it show nothing.
* **Panel C, the aggregate-channel gate on the lab fast stream.** The same forced choice read off
  what a model's head receives: `tube` at initialisation (the bank that licensed training) beside
  fitted `tube` and fitted `line`, one fit per held-out fold, drawn as the range over folds.
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

CONTROLS = [("rigid_shift", "rigid shift", "#2a78d6", "o"),
            ("shared_shift", "shared offset (should be chance)", "#6b6b6b", "s"),
            ("uniform_dither", "per-onset dither (positive control: must separate)", "#eb6834",
             "D")]
BANKS = [("init", "tube at initialisation (licensed training)", "#6b6b6b", "s"),
         ("tube", "fitted tube", "#2a78d6", "o"),
         ("line", "fitted line", "#1baf7a", "D")]


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args(argv)
    run = Path(a.run)
    C = json.loads((run / "controls_lab" / "results.json").read_text())["leak"]
    G = json.loads((run / "aggregate_leak" / "results.json").read_text())

    fig, axes = plt.subplots(1, 3, figsize=(15.5, 4.9), gridspec_kw={"width_ratios": [1, 1, 1.1]})
    for ax, stream, letter in ((axes[0], "fast", "A"), (axes[1], "slow", "B")):
        rows = sorted((r for r in C if r["stream"] == stream), key=lambda r: r["J_sec"])
        Js = [r["J_sec"] for r in rows]
        x = np.arange(len(Js))
        for k, (key, _, c, mk) in enumerate(CONTROLS):
            dx = (k - 1) * 0.16
            acc = [r[key]["by_mouse"]["accuracy"] for r in rows]
            lo = [r[key]["by_mouse"]["p2_5"] for r in rows]
            hi = [r[key]["by_mouse"]["p97_5"] for r in rows]
            ax.vlines(x + dx, lo, hi, color=c, lw=1.6)
            ax.plot(x + dx, acc, mk, color=c, ms=6, mec="white", mew=0.6)
        ax.axhline(0.5, color="0.55", ls=":", lw=0.9)
        ax.set_xticks(x, [f"{J:g}" for J in Js])
        ax.set_ylim(0.3, 1.0)
        ax.set_xlabel("displacement J (s)", fontsize=9)
        n = rows[0]["n_pairs"] if rows else 0
        ax.set_ylabel(f"lab {stream} · per-ROI classifier accuracy\n({n:,} window pairs, "
                      "mouse-grouped folds)", fontsize=9)
        ax.text(0.03, 0.97, letter, transform=ax.transAxes, fontsize=12, fontweight="bold",
                va="top")

    bx = axes[2]
    Js = sorted({r["J_sec"] for r in G if r["stream"] == "fast"})
    x = np.arange(len(Js))
    for k, (bank, _, c, mk) in enumerate(BANKS):
        dx = (k - 1) * 0.16
        for key, filled in (("real_vs_rigid_shift", True), ("real_vs_shared_offset", False)):
            lo, hi, mid = [], [], []
            for J in Js:
                cells = [r for r in G if r["stream"] == "fast" and r["J_sec"] == J
                         and r["kind"] == "real"
                         and (r["bank"] == "init" if bank == "init"
                              else r["bank"] == "fitted" and r["model"] == bank)]
                if not cells:
                    lo.append(np.nan); hi.append(np.nan); mid.append(np.nan)
                    continue
                accs = [q[key]["all"]["accuracy"] for q in cells]
                if len(cells) == 1:
                    lo.append(cells[0][key]["all"]["p2_5"]); hi.append(cells[0][key]["all"]["p97_5"])
                else:
                    lo.append(min(accs)); hi.append(max(accs))
                mid.append(float(np.mean(accs)))
            off = dx + (0.0 if filled else 0.05)
            bx.vlines(x + off, lo, hi, color=c, lw=1.6, alpha=1.0 if filled else 0.6)
            bx.plot(x + off, mid, mk, ms=6, color=c if filled else "white", mec=c, mew=1.3)
    bx.axhline(0.5, color="0.55", ls=":", lw=0.9)
    bx.set_xticks(x, [f"{J:g}" for J in Js])
    bx.set_ylim(0.3, 1.0)
    bx.set_xlabel("displacement J (s)", fontsize=9)
    bx.set_ylabel("lab fast · accuracy from a model's head input,\nall channels pooled", fontsize=9)
    bx.text(0.03, 0.97, "C", transform=bx.transAxes, fontsize=12, fontweight="bold", va="top")

    handles = [Line2D([], [], color=c, marker=mk, ls="", ms=6, label=lab)
               for _, lab, c, mk in CONTROLS]
    handles += [Line2D([], [], color="0.3", lw=1.6,
                       label="A, B bar: 95 % mouse-resampled interval, refitting bootstrap")]
    fig.legend(handles=handles, loc="upper left", bbox_to_anchor=(0.02, 1.0), ncol=2,
               frameon=False, fontsize=8.3, title="panels A and B", title_fontsize=8.3,
               alignment="left")
    h2 = [Line2D([], [], color=c, marker=mk, ls="", ms=6, label=lab) for _, lab, c, mk in BANKS]
    h2 += [Line2D([], [], color="0.3", marker="o", ls="", ms=6, label="filled: real vs rigid shift"),
           Line2D([], [], color="0.3", marker="o", ls="", ms=6, mfc="white",
                  label="open: real vs shared offset (should be chance)"),
           Line2D([], [], color="0.3", lw=1.6,
                  label="C bar: range over four fitted folds (initial bank: 95 % interval)")]
    fig.legend(handles=h2, loc="upper right", bbox_to_anchor=(0.995, 1.0), ncol=2,
               frameon=False, fontsize=8.3, title="panel C", title_fontsize=8.3,
               alignment="left")
    fig.tight_layout(rect=(0, 0, 1, 0.8))
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    p = out / "rigid_shift_gates_fig.png"
    fig.savefig(p, dpi=150)
    print(p)


if __name__ == "__main__":
    main()
