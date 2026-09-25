#!/usr/bin/env python3
"""The elevated-rate recording (ADR-0009 decision 1): every detector's calls inside its stretch and
outside it, per stream and background, against the budgets.

    python tools/make_elevated_rate_figure.py --candidates <candidates.json> [<more> ...] \
        --out <folder> [--also docs/learned/runs/<name>]

**What it reads.** ``candidates.json`` files written by ``tools/score_bench_candidates.py``, which
score every candidate on the elevated-rate recording on fresh seeds (66000–66011): calls per minute
inside the 300 s stretch (``probe_calls_per_min``) and calls per hour outside it
(``elevated_calls_per_hour_outside``), for the quiet and the busy background. Several files may be
given (a night's streams are often scored in separate runs); a later file's row replaces an earlier
one's for the same stream and candidate. For chorus only the seed each training run picked is
drawn.

**What it draws.** One column per stream (fast, slow, combined). Top row: calls per minute inside
the stretch, against ``MAX_PROBE_PER_MIN``, which gates both backgrounds. Bottom row: calls per
hour outside it, against ``MAX_FALSE_POSITIVES_PER_HOUR``, which gates the quiet background only
(the background that budget was measured on); busy is reported, not gated. Each budget is a short
black bar over its detector. Chorus has no budget of its own; it is held to CoactDetect's, as the
chorus pick is, so that bar is drawn over the chorus columns too, dashed. Filled marks are the
quiet background, open marks the busy one; circles are the shipped point, triangles the search's
proposal. Panels are lettered; the caption lives in the report, not in the image.
"""
from __future__ import annotations

import argparse
import importlib
import json
import shutil
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.lines import Line2D  # noqa: E402

STREAMS = ("fast", "slow", "combined")
MODULE = {"fast": "bugarach.bench", "slow": "bugarach.bench_slow",
          "combined": "bugarach.bench_combined"}
ORDER = ("coact", "loco", "sce", "rate", "sync", "cicada", "chorus_norm", "chorus_gain_norm")
NAME = {"coact": "CoactDetect", "loco": "LoCo", "sce": "binned SCE", "rate": "rate+context",
        "sync": "SPIKE-synch", "cicada": "locust", "chorus_norm": "chorus_norm",
        "chorus_gain_norm": "chorus_gain_norm"}
INK = {"coact": "#0072B2", "loco": "#E69F00", "sce": "#56B4E9", "rate": "#D55E00",
       "sync": "#999933", "cicada": "#000000", "chorus_norm": "#009E73",
       "chorus_gain_norm": "#CC79A7"}
BACKGROUNDS = ("baseline_quiet", "baseline_busy")
CHORUS = ("chorus_norm", "chorus_gain_norm")
FONT = 12
"""Points. At 150 dpi on a figure 13 in wide, a report page scales the image to about 0.4, so this
keeps every label near 10 px there (the report asked for nothing under about 9 px)."""


def collect(paths) -> dict:
    """``{stream: {(family, which): results row}}``; a later file wins for the same key."""
    out: dict = {s: {} for s in STREAMS}
    for p in paths:
        c = json.loads(Path(p).read_text(encoding="utf-8"))
        for stream, rows in c["results"].items():
            picked = {v.get("picked") for v in
                      c["benches"].get(stream, {}).get("chorus", {}).values()}
            for key, row in rows.items():
                kind, label = key.split(":", 1)
                if kind == "chorus":
                    if label not in picked:
                        continue
                    fam = label.split(f"_{stream}_")[0]
                    out[stream][(fam, "picked")] = row
                else:
                    out[stream][(kind, label)] = row
    return out


def draw(rows: dict, out_png: Path) -> Path:
    plt.rcParams.update({"font.size": FONT})
    fig, axes = plt.subplots(2, 3, figsize=(13, 10.5), sharey="row")
    for col, stream in enumerate(STREAMS):
        b = importlib.import_module(MODULE[stream])
        present = [f for f in ORDER if any(k[0] == f for k in rows[stream])]
        for row_i, (field, budget, unit) in enumerate((
                ("probe_calls_per_min", b.MAX_PROBE_PER_MIN, "calls per minute"),
                ("elevated_calls_per_hour_outside", b.MAX_FALSE_POSITIVES_PER_HOUR,
                 "calls per hour"))):
            ax = axes[row_i, col]
            for x, fam in enumerate(present):
                for (f, which), r in rows[stream].items():
                    if f != fam:
                        continue
                    dx = 0.14 if which == "proposal" else -0.14 if which == "shipped" else 0.0
                    mk = "^" if which == "proposal" else "o"
                    for bg in BACKGROUNDS:
                        v = r[bg].get(field)
                        if v is None:
                            continue
                        quiet = bg == "baseline_quiet"
                        ax.plot(x + dx + (-0.05 if quiet else 0.05), v, mk, ms=7,
                                color=INK[fam], mfc=INK[fam] if quiet else "white", mew=1.4)
                if fam in budget:
                    ax.plot([x - 0.35, x + 0.35], [budget[fam]] * 2, color="black", lw=2.2)
                elif fam in CHORUS and "coact" in budget:
                    # Chorus is held to CoactDetect's limits (the chorus pick's own rule).
                    ax.plot([x - 0.35, x + 0.35], [budget["coact"]] * 2, color="black", lw=2.2,
                            ls=(0, (2, 1.5)))
            ax.set_yscale("symlog", linthresh=0.1)
            ax.set_xticks(range(len(present)))
            ax.set_xticklabels([NAME[f] for f in present], rotation=40, ha="right",
                               fontsize=FONT - 1)
            ax.tick_params(axis="y", labelsize=FONT - 1)
            ax.set_xlim(-0.6, len(present) - 0.4)
            ax.grid(axis="y", color="0.9", lw=0.6)
            ax.text(0.0, 1.02, "abcdef"[row_i * 3 + col], transform=ax.transAxes,
                    fontsize=FONT + 3, fontweight="bold", va="bottom", ha="left")
            if col == 0:
                ax.set_ylabel(("inside the stretch,\n" if row_i == 0 else "outside the stretch,\n")
                              + unit + " (symmetric log)", fontsize=FONT)
            if row_i == 1:
                ax.set_xlabel(f"{stream} stream", fontsize=FONT + 1)
    handles = [
        Line2D([], [], marker="o", ls="none", color="0.3", label="shipped point"),
        Line2D([], [], marker="^", ls="none", color="0.3", label="search's proposal"),
        Line2D([], [], marker="o", ls="none", color="0.3", label="quiet background (filled)"),
        Line2D([], [], marker="o", ls="none", mfc="white", mec="0.3",
               label="busy background (open)"),
        Line2D([], [], color="black", lw=2.2, label="limit (top: both backgrounds; "
                                                     "bottom: quiet only)"),
        Line2D([], [], color="black", lw=2.2, ls=(0, (2, 1.5)),
               label="CoactDetect's limit, applied to chorus"),
        *[Line2D([], [], marker="o", ls="none", color=INK[f], label=NAME[f]) for f in ORDER]]
    fig.legend(handles=handles, loc="lower center", ncol=4, fontsize=FONT - 1, frameon=False)
    fig.tight_layout(rect=(0, 0.115, 1, 1))
    out_png.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_png, dpi=150)
    plt.close(fig)
    return out_png


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--candidates", type=Path, nargs="+", required=True)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--also", type=Path, default=None)
    a = ap.parse_args(argv)
    png = draw(collect(a.candidates), a.out / "figure3_elevated_rate.png")
    print(f"wrote {png}")
    if a.also:
        a.also.mkdir(parents=True, exist_ok=True)
        shutil.copy2(png, a.also / png.name)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
