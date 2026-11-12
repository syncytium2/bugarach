#!/usr/bin/env python3
"""The baseline characterization as a page a person can read: one page per stream.

    python docs/learned/runs/2026-11-12-baseline-characterization-3x-4x/page.py --out <dir>

Draws `baseline_characterization.json` (written by `characterize.py` beside this file) and
measures nothing. Every recording is a dot, drawn at 4 x sigma_est and at 3 x sigma_est and
joined by a line, so the line's slope is what the threshold does to that recording. Dots are
coloured by mouse. Figures first, text last (ADR-0014); each figure is numbered.

One page per stream because the filename scheme names one stream per file.
"""
from __future__ import annotations

import argparse
import base64
import io
import json
import subprocess
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
sys.path.insert(0, str(REPO / "src"))
sys.path.insert(0, str(REPO / "tools"))

THRS = ("4x", "3x")                     # left and right of each pair
MIN_EXPECTED_PAIRS = 5.0                # below this a recording's own correlogram is not read
MOUSE_COLORS = ("#0072B2", "#56B4E9", "#009E73", "#D55E00", "#E69F00", "#CC79A7", "#7A5C00")
OFF = {"4x": -0.17, "3x": 0.17}


def _png(fig) -> str:
    import matplotlib.pyplot as plt

    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=150)
    plt.close(fig)
    return base64.b64encode(buf.getvalue()).decode("ascii")


def _groups(rec, stream):
    S = rec["by_threshold"]["4x"]["streams"][stream]
    return [g for g in S["pooled"] if g != "all"]


def correlograms(rec, stream) -> str:
    import matplotlib.pyplot as plt

    sets = ["all"] + _groups(rec, stream)
    fig, axes = plt.subplots(1, len(sets), figsize=(11.2, 3.0), sharey=True)
    lags = np.arange(101) * 0.1
    for ax, g in zip(axes, sets):
        for thr, ls in zip(THRS, ("-", "--")):
            P = rec["by_threshold"][thr]["streams"][stream]["pooled"][g]
            x = np.array([np.nan if v is None else v for v in P["correlogram_excess"]])
            ax.plot(lags, x, color="#111", ls=ls, lw=1.4)
        ax.axhline(0, color="#999", lw=0.6)
        ax.set_xscale("symlog", linthresh=1.0)
        ax.set_xlim(0, 10)
        ax.set_xticks([0, 0.5, 1, 2, 5, 10])
        ax.set_xticklabels(["0", "0.5", "1", "2", "5", "10"])
        P4 = rec["by_threshold"]["4x"]["streams"][stream]["pooled"][g]
        ax.set_xlabel(f"lag (s)\n{'all recordings' if g == 'all' else g} · "
                      f"{P4['recordings']} recordings · {P4['mice']} mice")
    axes[0].set_ylabel("onset pairs over chance, minus 1")
    fig.tight_layout()
    return _png(fig)


def dots(rec, stream, value, ylabel, log, mice, extra=None, floor_note=None) -> str:
    """One dot per recording at each threshold, joined; a bar at each cluster's median."""
    import matplotlib.pyplot as plt

    groups = _groups(rec, stream)
    fig, ax = plt.subplots(figsize=(7.4, 3.4))
    per = {thr: {r["slice_id"]: r for r in rec["by_threshold"][thr]["streams"][stream]["per_recording"]}
           for thr in THRS}
    ids = list(per["4x"])
    vals = {thr: {sid: value(per[thr][sid]) for sid in ids} for thr in THRS}
    finite = [v for thr in THRS for v in vals[thr].values() if v is not None and (v > 0 or not log)]
    lo, hi = min(finite), max(finite)
    edge = lo / 2.2 if log else lo - 0.12 * (hi - lo)       # where unreadable recordings sit
    any_unreadable = False
    for gi, g in enumerate(groups):
        members = [sid for sid in ids if per["4x"][sid]["group"] == g]
        spread = np.linspace(-0.07, 0.07, len(members)) if len(members) > 1 else [0.0]
        for sid, dx in zip(members, spread):
            col = mice[per["4x"][sid]["mouse"]]
            pts = []
            for thr in THRS:
                v = vals[thr][sid]
                x = gi + OFF[thr] + dx
                if v is None or (log and v <= 0):
                    ax.scatter([x], [edge], s=34, facecolors="none", edgecolors=col, lw=1.1, zorder=3)
                    any_unreadable = True
                    pts.append(None)
                else:
                    ax.scatter([x], [v], s=34, color=col, zorder=3)
                    pts.append((x, v))
                if extra is not None and v is not None:
                    for w, e in extra(per[thr][sid]):
                        if e is not None and (e > 0 or not log):
                            ax.scatter([x + (0.035 if w == 2 else 0.07)], [e], s=9, color=col,
                                       alpha=0.45, zorder=2)
            if pts[0] and pts[1]:
                ax.plot([pts[0][0], pts[1][0]], [pts[0][1], pts[1][1]], color=col, lw=0.9, alpha=0.7)
        for thr in THRS:
            ok = [vals[thr][sid] for sid in members
                  if vals[thr][sid] is not None and (vals[thr][sid] > 0 or not log)]
            if ok:
                m = float(np.median(ok))
                ax.plot([gi + OFF[thr] - 0.13, gi + OFF[thr] + 0.13], [m, m], color="#111", lw=2.2,
                        zorder=4)
    ticks, labels = [], []
    for gi, g in enumerate(groups):
        for thr in THRS:
            ticks.append(gi + OFF[thr])
            labels.append(f"{g}\n{thr}")
    ax.set_xticks(ticks)
    ax.set_xticklabels(labels)
    ax.set_xlim(-0.55, len(groups) - 0.45)
    if log:
        ax.set_yscale("log")
    if any_unreadable:
        ax.axhline(edge, color="#bbb", lw=0.6, ls=":")
        ax.text(len(groups) / 2 - 0.5, edge, floor_note or "not readable", ha="center", va="bottom",
                fontsize=7, color="#555")
    ax.set_ylabel(ylabel)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    fig.tight_layout()
    return _png(fig)


def readable(key):
    def f(r):
        if r["corr_expected_pairs_at_zero_lag"] < MIN_EXPECTED_PAIRS:
            return None
        return r[key]
    return f


def build(rec, stream) -> str:
    per4 = rec["by_threshold"]["4x"]["streams"][stream]["per_recording"]
    mouse_ids = list(dict.fromkeys(r["mouse"] for r in per4))
    mice = {m: MOUSE_COLORS[i % len(MOUSE_COLORS)] for i, m in enumerate(mouse_ids)}
    mouse_group = {r["mouse"]: r["group"] for r in per4}
    key = "".join(f'<span class="key" style="background:{c};border-color:{c}"></span>'
                  f"mouse {m} ({mouse_group[m]})" for m, c in mice.items())
    pair_key = ('<span class="line" style="border-top:2px solid #111"></span>median of the '
                "recordings in that cluster · each recording is one dot at 4x and one at 3x, "
                "joined by a line")
    figs = [
        ("the onset correlogram, pooled",
         '<span class="line" style="border-top:2px solid #111"></span>4 x sigma_est'
         '<span class="line" style="border-top:2px dashed #111"></span>3 x sigma_est',
         correlograms(rec, stream)),
        ("onset rate per ROI", key + " · " + pair_key,
         dots(rec, stream, lambda r: r["rate_hz"], "onsets per ROI per second", True, mice)),
        ("height of the correlogram peak at zero lag", key,
         dots(rec, stream, readable("corr_excess_at_zero_lag"),
              "onset pairs over chance, minus 1", True, mice,
              floor_note=f"open: fewer than {MIN_EXPECTED_PAIRS:.0f} pairs expected by chance")),
        ("width of the correlogram peak", key,
         dots(rec, stream, readable("corr_half_width_sec"),
              "half-width at half height (s)", False, mice,
              floor_note=f"open: fewer than {MIN_EXPECTED_PAIRS:.0f} pairs expected by chance")),
        ("excess onset pairs", key + " · large dot: 1 s window; small dots to its right: 2 s, then 4 s",
         dots(rec, stream, lambda r: r["cum"]["1.0"]["f2"], "excess onset pairs per second of window",
              True, mice,
              extra=lambda r: [(2, r["cum"]["2.0"]["f2"] / 2.0), (4, r["cum"]["4.0"]["f2"] / 4.0)],
              floor_note="open: no excess over the shifted copies")),
    ]
    P = {thr: rec["by_threshold"][thr]["streams"][stream]["pooled"]["all"] for thr in THRS}
    names = {thr: rec["by_threshold"][thr]["dataset"]["name"] for thr in THRS}
    body = "".join(
        f'<figure><figcaption><b>Figure {i}, {name}.</b> {legend}</figcaption>'
        f'<img alt="Figure {i}, {name}" src="data:image/png;base64,{png}"></figure>'
        for i, (name, legend, png) in enumerate(figs, 1))
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Baseline onset timing, {stream} stream, 3x and 4x</title>
<style>
  body {{ font: 14px/1.45 -apple-system, "Segoe UI", Helvetica, Arial, sans-serif; color: #111;
         background: #fff; margin: 0; }}
  main {{ max-width: 1120px; margin: 0 auto; padding: 18px 20px 60px; }}
  h1 {{ font-size: 20px; margin: 0 0 6px; }}
  p {{ margin: 6px 0; max-width: 980px; }}
  figure {{ margin: 18px 0 0; }}
  figcaption {{ color: #222; margin: 0 0 4px; max-width: 1080px; }}
  img {{ display: block; max-width: 100%; }}
  .key {{ display: inline-block; width: 10px; height: 10px; border-radius: 5px; vertical-align: -1px;
         margin: 0 3px 0 10px; border: 1px solid #111; }}
  .line {{ display: inline-block; width: 22px; height: 0; vertical-align: 4px; margin: 0 4px 0 10px; }}
  .how {{ color: #333; }}
  .note {{ color: #555; font-size: 13px; }}
</style></head><body><main>
<h1>Baseline onset timing · {stream} stream · thresholds 4x and 3x</h1>
{body}
<p class="how"><b>What is measured.</b> Each recording's baseline analysis window only
(1,200 s per recording, {P['4x']['baseline_minutes']:.0f} min in all), in the {stream} stream as
exported. {P['4x']['recordings']} recordings from {P['4x']['mice']} mice;
{P['4x']['rois']} ROIs (regions of interest, one per cell) and {P['4x']['onsets']:,} onsets at 4x,
{P['3x']['rois']} ROIs and {P['3x']['onsets']:,} onsets at 3x. "4x" and "3x" are the event
threshold, 4 or 3 times sigma_est, the producer's estimate of each trace's noise. No event of
coordinated activity is defined and no model is fitted. DI and MALE are shown apart to describe
the data for building synthetic recordings; nothing here tests one group against the other.</p>
<p class="how"><b>Figure 1, the onset correlogram, pooled.</b> For every pair of different ROIs in
a recording, the lag between an onset in one and an onset in the other is counted in steps of one
frame (0.1 s), and divided by the count expected if the two ROIs were unrelated. Zero means chance;
1 means twice as many pairs as chance. A peak at short lags is onsets shared between ROIs. Counts
are pooled over the recordings named under each panel before dividing. The lag axis is linear to
1 s and logarithmic beyond.</p>
<p class="how"><b>Figure 2, onset rate per ROI.</b> The mean over a recording's ROIs of onsets per
second.</p>
<p class="how"><b>Figures 3 and 4, the peak of each recording's own correlogram.</b> Its height at
zero lag, and its half-width at half height after the level at 5 to 10 s is subtracted. A narrower
peak means shared onsets are more tightly timed. A recording with fewer than
{MIN_EXPECTED_PAIRS:.0f} pairs expected by chance at zero lag has too few onsets for its own peak
to be read, and is drawn open on the dotted line at the bottom.</p>
<p class="how"><b>Figure 5, excess onset pairs.</b> Onsets of all ROIs are counted in a sliding
window. The number of onset pairs in a window beyond what independent ROIs would give, minus the
same count after every ROI's train is shifted in time by its own amount, divided by the window's
length. It grows with how often onsets are shared and with how many ROIs share them.</p>
<p class="note">Datasets: {names['4x']} (the default) and {names['3x']}. Working material, not
murderboarded. Record: docs/learned/runs/2026-11-12-baseline-characterization-3x-4x/ in the
bugarach repository.</p>
</main></body></html>
"""


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", type=Path, help="destination (default: the darkroom)")
    ap.add_argument("--png", action="store_true", help="also write a flat .png of each page")
    a = ap.parse_args(argv)
    import matplotlib
    matplotlib.use("Agg")
    from bugarach import paths

    out = a.out or paths.darkroom() / "2026-11-12-baseline-characterization-3x-and-4x"
    out.mkdir(parents=True, exist_ok=True)
    rec = json.loads((HERE / "baseline_characterization.json").read_text(encoding="utf-8"))
    for stream in ("fast", "slow"):
        name = subprocess.run(
            [sys.executable, str(REPO / "tools/naming/artifact_name.py"), "build", "--type", "report",
             "--signal", "roi", "--stream", stream, "--treatment", "baseline", "--groups", "di+male",
             "--win", "win20min", "--date", "20261112", "--ext", "html"],
            capture_output=True, text=True)
        if name.returncode != 0 or not name.stdout.strip():
            raise SystemExit(f"naming tool refused: {name.stderr or name.stdout}")
        html = out / name.stdout.strip().splitlines()[-1]
        html.write_text(build(rec, stream), encoding="utf-8")
        print("wrote", html.name)
        if a.png:
            from make_diagnostic import _render_png
            shot = html.with_suffix(".png")
            print("wrote" if _render_png(html, shot, scale=2) else "no PNG for", shot.name)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
