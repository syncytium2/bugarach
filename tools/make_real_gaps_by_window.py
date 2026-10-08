#!/usr/bin/env python3
"""The real gaps between events, measured at several co-activity windows, side by side.

    python tools/make_real_gaps_by_window.py <folder holding window-2s/, window-1s/, window-0.5s/>

Each ``window-<w>s`` folder is one run of ``tools/measure_real_intervals.py --window-sec <w>``.
This reads their ``gaps.csv`` and ``windows.csv`` and nothing else: no export folder is opened.

**Why.** The realistic bench's gaps were measured in a 2 s window with events under 2 s apart
merged, so it plants nothing closer than about 2 s (ADR-0010 part 2). Tony, 2026-10-08: *"i
suspect we need the revised bench with short intervals."* A narrower window is what lets a
shorter gap be seen. It also lowers the floor, so more chance coincidences count as events, and
the three windows side by side show how far the answer depends on the choice.

**The four DI recordings named in the contamination stop** (#858) are reported both ways: every
number is given over all recordings and again without :data:`NAMED_IN_THE_STOP`. That is a split
of rows already measured, made here in the reading. It is not an exclusion, and nothing in the
measurement drops a recording.

Writes ``real_gaps_by_window.json`` and one figure into the same folder. Real recordings, so
the figure stays in the darkroom and this tool has no ``--also``.
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

STREAMS = ("fast", "slow", "combined")
NAMED_IN_THE_STOP = ("20260629_312", "20260629_309", "20260630_316", "20250926_235")
"""The recordings ``current_export.toml``'s contamination note names. All four are DI."""
UNDER_SEC = (1.0, 2.0, 5.0, 10.0)
INK = {0.5: "#c8501e", 1.0: "#7a4fa3", 2.0: "#111111"}
TICKS = ((0.5, "0.5s"), (1, "1s"), (2, "2s"), (5, "5s"), (10, "10s"), (30, "30s"), (60, "1m"),
         (120, "2m"), (300, "5m"), (600, "10m"), (1800, "30m"))


def rows_of(path: Path) -> list[dict]:
    with path.open(newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def named(slice_id: str) -> bool:
    return any(n in slice_id for n in NAMED_IN_THE_STOP)


def describe(gaps, windows) -> dict:
    g = np.array([float(r["gap_sec"]) for r in gaps])
    ok = [w for w in windows if w["floor"] not in ("", None)]
    hours = sum(float(w["hours"]) for w in ok)
    n_events = sum(int(w["n_events"]) for w in ok)
    floors = np.array([int(w["floor"]) for w in ok])
    out = dict(n_recordings=len({w["slice_id"] for w in ok}), n_windows=len(ok), hours=hours,
               n_events=n_events, events_per_hour=n_events / hours if hours else None,
               n_gaps=int(g.size),
               floor_min_median_max=[int(floors.min()), float(np.median(floors)),
                                     int(floors.max())] if floors.size else None)
    if g.size:
        out.update(min_gap_sec=float(g.min()), median_gap_sec=float(np.median(g)),
                   **{f"share_under_{u:g}_sec": float(np.mean(g < u)) for u in UNDER_SEC},
                   **{f"n_under_{u:g}_sec": int(np.sum(g < u)) for u in UNDER_SEC})
    return out


def measure(root: Path) -> dict:
    R = dict(windows_sec=[], named_in_the_stop=list(NAMED_IN_THE_STOP), by_window={}, gaps={})
    for folder in sorted(root.glob("window-*s"), key=lambda p: float(p.name[7:-1])):
        w = float(folder.name[7:-1])
        if not (folder / "gaps.csv").exists():
            continue
        gaps, windows = rows_of(folder / "gaps.csv"), rows_of(folder / "windows.csv")
        stamp = json.loads((folder / "summary.json").read_text()).get("dataset")
        entry = dict(dataset=stamp, streams={})
        for s in STREAMS:
            gs = [r for r in gaps if r["stream"] == s]
            ws = [r for r in windows if r["stream"] == s]
            entry["streams"][s] = dict(
                all=describe(gs, ws),
                without_the_named=describe([r for r in gs if not named(r["slice_id"])],
                                           [r for r in ws if not named(r["slice_id"])]),
                the_named_alone=describe([r for r in gs if named(r["slice_id"])],
                                         [r for r in ws if named(r["slice_id"])]))
            R["gaps"][f"{w:g}", s] = np.array([float(r["gap_sec"]) for r in gs])
            R["gaps"][f"{w:g}", s, "without"] = np.array(
                [float(r["gap_sec"]) for r in gs if not named(r["slice_id"])])
        R["windows_sec"].append(w)
        R["by_window"][f"{w:g}"] = entry
    return R


def figure(R, out: Path) -> Path:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, axes = plt.subplots(1, 3, figsize=(12.5, 4.2), sharey=True)
    for ax, s in zip(axes, STREAMS):
        for w in R["windows_sec"]:
            for key, style, alpha in (((f"{w:g}", s), "-", 1.0),
                                      ((f"{w:g}", s, "without"), ":", 0.9)):
                g = np.sort(R["gaps"][key])
                if not g.size:
                    continue
                label = None
                if style == "-":
                    label = f"{w:g} s window · {g.size} gaps"
                ax.step(g, np.arange(1, g.size + 1) / g.size, where="post", color=INK.get(w, "#555"),
                        lw=1.5 if style == "-" else 1.0, ls=style, alpha=alpha, label=label)
        ax.set_xscale("log")
        ax.set_xlim(0.4, 2400)
        ax.set_xticks([t for t, _ in TICKS], [n for _, n in TICKS], fontsize=7.5)
        ax.minorticks_off()
        ax.set_ylim(0, 1)
        ax.set_xlabel("gap between neighbouring events", fontsize=8)
        ax.set_ylabel(f"{s} · share of gaps shorter", fontsize=8)
        ax.tick_params(axis="y", labelsize=8)
        ax.legend(fontsize=7.5, frameon=False, loc="lower right")
        for side in ("top", "right"):
            ax.spines[side].set_visible(False)
    fig.tight_layout()
    path = out / "explainer_real-gaps-by-window_20261008.png"   # tools/naming/artifact_name.py
    fig.savefig(path, dpi=170)
    plt.close(fig)
    return path


def table(R) -> str:
    lines = []
    for s in STREAMS:
        lines.append(f"\n{s}")
        lines.append("  window  recordings   floor min/med/max  events  per hour  gaps   "
                     "min gap  median   <1 s    <2 s    <5 s    <10 s")
        for w in R["windows_sec"]:
            for which, tag in (("all", "all"), ("without_the_named", "w/o 4")):
                d = R["by_window"][f"{w:g}"]["streams"][s][which]
                if not d.get("n_gaps"):
                    lines.append(f"  {w:>4g} s  {tag:<6} no gaps")
                    continue
                f = d["floor_min_median_max"]
                lines.append(
                    f"  {w:>4g} s  {tag:<5}{d['n_recordings']:>4}   {f[0]:>3}/{f[1]:>4g}/{f[2]:<4}"
                    f"      {d['n_events']:>6}  {d['events_per_hour']:>8.1f}  {d['n_gaps']:>5}  "
                    f"{d['min_gap_sec']:>6.2f}s  {d['median_gap_sec']:>6.1f}s  "
                    + "  ".join(f"{d[f'share_under_{u:g}_sec']:>6.3f}" for u in UNDER_SEC))
    return "\n".join(lines)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("root", type=Path, help="the folder holding the window-<w>s folders")
    a = ap.parse_args(argv)
    R = measure(a.root)
    if not R["windows_sec"]:
        raise SystemExit(f"no finished window-<w>s folder under {a.root}")
    gaps = R.pop("gaps")
    (a.root / "real_gaps_by_window.json").write_text(json.dumps(R, indent=1) + "\n")
    R["gaps"] = gaps
    print(figure(R, a.root))
    print(table(R))


if __name__ == "__main__":
    main()
