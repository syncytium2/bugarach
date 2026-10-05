#!/usr/bin/env python3
"""Figures and tables for ``tools/measure_rate_stretches.py``.

    python tools/make_rate_stretch_figures.py --run <folder> [--also docs/learned/runs/<name>]

* ``fig1_<stream>_population_rate.png`` — every recording one row, one stream, each row on its own
  y-scale.
* ``fig3_three_streams_one_scale.png`` — the same rows with fast, slow and combined superimposed on
  ONE y-scale, with a single reference axis.

Both are drawn by :func:`stacked`, so they share one layout:

* rows grouped by first treatment (senktide, then TTX), then group (``bugarach.groups`` order), with
  a gap between groups and a larger one between the two blocks, each block labelled at its left;
* every row aligned at the end of its recording's baseline window (t = 0), on one shared,
  minutes-friendly time axis drawn **only under the last row of each block**;
* a thin window lane above each trace: windows in neutral greys (TTX hatched), t = 0 as a black
  tick, and every *k* = 3 stretch as a bar with a ▼ pointing down, in its stream's colour. Window
  names are written on the first row of each block only; a key in the legend identifies the grey
  tones below it. Each lane sits flush on its own trace and a wider gap separates rows. Nothing is
  drawn on the traces.

* ``fig2_elevation_vs_breadth.png`` — every real stretch at *k* = 3, 60 s: peak within-window
  elevation against median breadth, by window type; the bench's elevated-rate test as black stars.
* ``tables.md`` — the summary per stream × window type × group × k, the GDX (OVX and ORX) senktide
  windows by recording, and the floor comparison.
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

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))
from bugarach.groups import group_key  # noqa: E402
from bugarach.time_axis import label as tlabel  # noqa: E402
from bugarach.time_axis import ticks as tticks  # noqa: E402

STREAMS = ("fast", "slow", "combined")
TYPES = ("baseline", "TTX", "senktide", "high K+", "wash")
SHORT = {"baseline": "B", "TTX": "TTX", "senktide": "SK", "high K+": "K+", "wash": "W",
         "other": "?"}
TINT = {"baseline": "#E3E3E3", "TTX": "#EDEDED", "senktide": "#B5B5B5", "high K+": "#8C8C8C",
        "wash": "#F7F7F7", "other": "#FFFFFF"}
"""Windows in the lane are NEUTRAL: grey values, a hatch for TTX, and their text labels. Blue,
vermillion and black belong to the streams and their stretch bars alone (the orchestrator,
2026-09-24: an orange slow-stream bar inside an orange senktide window could not be seen)."""
HATCH = {"TTX": "////"}
LABEL_INK = {"high K+": "white"}
STREAM_INK = {"fast": "#0072B2", "slow": "#D55E00", "combined": "#000000"}
"""Okabe–Ito blue and vermillion, and black: high contrast and colourblind-safe."""
TREAT_ORDER = {"senktide": 0, "TTX": 1, None: 2}
LANE, TRACE, ROW_GAP, GROUP_GAP, BLOCK_GAP, AXIS_ROOM = 0.22, 1.25, 0.9, 1.6, 2.6, 1.2
# The lane sits flush on its own trace (no gap inside a row) and rows are separated by a gap
# several times the lane's height, so each lane reads with the trace beneath it, not above it.
"""Height ratios. The lane is a thin strip and the freed height goes to the trace (Tony,
2026-09-24: "make more room for the data by vertically shrinking the b/sk/ttx bands")."""


def window_span(ax, a, b, kind):
    """One window in a lane: grey value, hatched where the type calls for it."""
    ax.axvspan(a, b, facecolor=TINT.get(kind, "#FFFFFF"), edgecolor="#9A9A9A",
               hatch=HATCH.get(kind), lw=0)


def recordings(rows, stream):
    by = {}
    for r in rows:
        if r["stream"] == stream:
            by.setdefault(r["slice_id"], []).append(r)
    order = sorted(by, key=lambda sid: (TREAT_ORDER.get(by[sid][0]["first_treatment"], 3),
                                        group_key(by[sid][0]["group"] or "~"), sid))
    return [(sid, sorted(by[sid], key=lambda r: r["win_start"])) for sid in order]


def full_curves(R, run: Path) -> dict:
    """The population rate over each WHOLE recording, per stream (60 s window, 10 s step): the
    same statistic as the run's per-window curves, computed across the gaps between analysis
    windows too (Tony, 2026-09-24: *"the measurement is not affected by analysis windows, the
    values extracted are"*). Figures only: stretches and every tabled number still come from the
    windows. Cached beside ``results.json`` as ``full_curves.json``, stamped with its dataset,
    and refused if that dataset is not the one the run measured."""
    cache = run / "full_curves.json"
    if cache.exists():
        C = json.loads(cache.read_text())
        if C.get("dataset") == R["dataset"]:
            return C["curves"]
    import measure_rate_stretches as mrs

    from bugarach import dataset
    from bugarach.combined import COMBINED, has_sources, stream_of
    from bugarach.detectors.rate import recording_extent, stream_trains
    from bugarach.io import load_folder
    if dataset.stamp() != R["dataset"]:
        raise SystemExit(f"default dataset {dataset.stamp()} is not the run's {R['dataset']}")
    want = {r["slice_id"] for r in R["rows"]}
    curves = {}
    for s in load_folder(dataset.default()):
        if s.slice_id not in want:
            continue
        if has_sources(s) and COMBINED not in s.streams:
            s.streams[COMBINED] = stream_of(s, COMBINED)
        lo, hi = recording_extent(s)
        for st in STREAMS:
            if st in s.streams:
                starts, pop, _ = mrs.rates(stream_trains(s.streams[st], (lo, hi)), lo, hi,
                                           mrs.PRIMARY)
                curves.setdefault(s.slice_id, {})[st] = dict(starts=starts.tolist(),
                                                             rate_hz=pop.tolist())
    cache.write_text(json.dumps(dict(dataset=R["dataset"], width_sec=mrs.PRIMARY,
                                     step_sec=mrs.STEP, curves=curves)))
    return curves


def stacked(R, streams, shared: bool, path: Path, curves: dict) -> tuple[Path, dict]:
    """One row per recording, ``streams`` superimposed; see the module docstring for the layout.
    ``shared``: one y-scale for every row with a single reference axis; otherwise each row on its
    own scale with none. Returns the path and the scale used."""
    by = {}
    for r in R["rows"]:
        by.setdefault(r["slice_id"], {}).setdefault(r["stream"], []).append(r)
    for sid in by:
        for s in by[sid]:
            by[sid][s].sort(key=lambda r: r["win_start"])
    order = [sid for sid, _ in recordings(R["rows"], streams[0])]
    def where(sid, t_center):
        """The analysis window a time falls in, or "between windows"."""
        for w in by[sid][streams[0]]:
            if w["win_start"] <= t_center < w["win_end"]:
                return w["window_type"]
        return "between windows"

    peaks = []
    for sid in order:
        for s in streams:
            c = curves.get(sid, {}).get(s)
            if c and c["rate_hz"]:
                j = int(np.argmax(c["rate_hz"]))
                t = c["starts"][j] + 30.0
                peaks.append((c["rate_hz"][j], sid, s, where(sid, t), t))
    peaks.sort(reverse=True)
    ymax = float(np.ceil(peaks[0][0] * 100) / 100) if peaks else 1.0
    lead = streams[0]

    def zero(ws):
        b = next((w for w in ws if w["window_type"] == "baseline"), None)
        return b["win_end"] if b else 0.0

    def treat(sid):
        return by[sid][lead][0]["first_treatment"]

    # Slots: lane, trace and gaps; the last row of each block gets room for its axis.
    slots, prev = [], None
    for i, sid in enumerate(order):
        head = by[sid][lead][0]
        key = (head["first_treatment"], head["group"])
        if prev is not None and key[0] != prev[0]:
            slots.append(("gap", BLOCK_GAP))
        elif prev is not None and key[1] != prev[1]:
            slots.append(("gap", GROUP_GAP))
        last_in_block = i + 1 == len(order) or treat(order[i + 1]) != key[0]
        slots += [("lane", sid), ("trace", sid),
                  ("gap", AXIS_ROOM if last_in_block else ROW_GAP)]
        prev = key
    ratios = [LANE if k == "lane" else TRACE if k == "trace" else v for k, v in slots]
    fig = plt.figure(figsize=(14, 0.3 * sum(ratios) + 1.2))
    gs = fig.add_gridspec(len(slots), 1, height_ratios=ratios, hspace=0.0, top=0.975,
                          bottom=0.02)
    zs = {sid: zero(by[sid][lead]) for sid in order}
    tmin = min(w["win_start"] - zs[sid] for sid in order for w in by[sid][lead])
    tmax = max(w["win_end"] - zs[sid] for sid in order for w in by[sid][lead])
    tk = tticks(tmin, tmax)
    level = ({s: 0.25 for s in streams} if len(streams) == 1
             else {"fast": 0.12, "slow": 0.42, "combined": 0.72})
    first, traces, block_top, prev_treat = None, [], {}, None
    for i, (kind, v) in enumerate(slots):
        if kind == "gap":
            continue
        sid = v
        z = zs[sid]
        ax = fig.add_subplot(gs[i], sharex=first)
        first = first or ax
        ws_lead = by[sid][lead]
        if kind == "lane":
            t = treat(sid)
            block_top.setdefault(t, ax)
            # Window names on the first row of each first-treatment block only (Tony); the lane's
            # grey tones and the legend's key identify the windows below it.
            named = t != prev_treat
            prev_treat = t
            for w in ws_lead:
                a, b = w["win_start"] - z, w["win_end"] - z
                window_span(ax, a, b, w["window_type"])
                if named:
                    ax.text((a + b) / 2, 1.15, SHORT.get(w["window_type"], "?"), ha="center",
                            va="bottom", fontsize=6, color="0.25")
            for s in streams:
                for w in by[sid].get(s, []):
                    for st in w["measures"]["60.0"].get("stretches", {}).get("3.0", []):
                        ax.plot([st["start"] - z, st["end"] - z], [level[s]] * 2,
                                color=STREAM_INK[s], lw=1.6, solid_capstyle="butt")
                        ax.plot((st["start"] + st["end"]) / 2 - z, level[s] + 0.22, "v",
                                color=STREAM_INK[s], ms=3)
            ax.plot([0, 0], [0, 1], color="black", lw=1.0)
            ax.set_ylim(0, 1)
            ax.axis("off")
        else:
            # One continuous curve over the whole recording, gaps between windows included.
            for s in streams:
                c = curves.get(sid, {}).get(s)
                if c:
                    ax.plot(np.asarray(c["starts"]) + 30.0 - z, c["rate_hz"],
                            color=STREAM_INK[s], lw=0.6, alpha=0.9)
            if shared:
                ax.set_ylim(0, ymax)
            # The recording's name sits level with its own trace, not with a lane edge that
            # borders the row above.
            ax.text(-0.005, 0.5, f"{sid}  {ws_lead[0]['group']}", transform=ax.transAxes,
                    ha="right", va="center", fontsize=6.5)
            ax.set_yticks([])
            for sp in ("top", "right", "left"):
                ax.spines[sp].set_visible(False)
            nxt = slots[i + 1] if i + 1 < len(slots) else ("gap", AXIS_ROOM)
            if nxt == ("gap", AXIS_ROOM):
                # The last row of a first-treatment block carries that block's time axis.
                ax.set_xticks(tk)
                ax.set_xticklabels(["0" if x == 0 else tlabel(x) for x in tk], fontsize=9)
                ax.tick_params(axis="x", labelbottom=True, length=4)
                ax.set_xlabel("time relative to the end of each recording's baseline window, "
                              "minutes (negative = baseline)", fontsize=8.5)
            else:
                ax.spines["bottom"].set_visible(False)
                ax.tick_params(axis="x", bottom=False, labelbottom=False)
            traces.append(ax)
    first.set_xlim(tmin, tmax)
    if shared:
        ref = traces[0]
        ref.spines["right"].set_visible(True)
        ref.yaxis.tick_right()
        ref.yaxis.set_label_position("right")
        ref.set_yticks([0, ymax])
        ref.set_yticklabels(["0", f"{ymax:g}"], fontsize=7.5)
        ref.set_ylabel("onsets per ROI per second\n(the same scale in every row)", fontsize=7,
                       rotation=0, ha="left", va="center", labelpad=10)
    for t, ax in block_top.items():
        ax.text(-0.13, 3.2, f"first treatment: {t or 'none'}", transform=ax.transAxes,
                ha="left", va="bottom", fontsize=10, fontweight="bold")
    from matplotlib.patches import Patch
    key = [Patch(facecolor=TINT[k], edgecolor="#9A9A9A", hatch=HATCH.get(k), lw=0.5,
                 label=f"{SHORT[k]} {k}") for k in ("baseline", "senktide", "TTX", "wash",
                                                     "high K+")]
    fig.legend(handles=[*(Line2D([], [], color=STREAM_INK[s], lw=1.6, label=f"{s} stream")
                          for s in streams), *key],
               loc="lower center", ncol=len(streams) + len(key), fontsize=9, frameon=False,
               bbox_to_anchor=(0.5, 0.985))
    fig.savefig(path, dpi=130, bbox_inches="tight")
    plt.close(fig)
    return path, dict(ymax=ymax, largest=peaks[0] if peaks else None,
                      second=peaks[1] if len(peaks) > 1 else None)


def fig1(R, stream, out: Path, curves: dict) -> Path:
    """One stream, each row on its own y-scale."""
    return stacked(R, (stream,), False, out / f"fig1_{stream}_population_rate.png", curves)[0]


ROW_HZ = 0.23
"""Figure 3's gain: one row height is 0.23 onsets per ROI per second (Tony, 2026-09-24: "let the
plots overrun their axes ... a mag of ~2x"). The largest peak, 0.452, reaches about two rows."""


ROW_HZ_3B = 0.23 * 2 / 3
"""Figure 3b's gain, 1.5 × Figure 3's: one row height is 0.23 × 2/3 = 0.15333… onsets per ROI per
second (Tony, 2026-09-24: "keep this one but lets try 3x"). The largest peak reaches ~2.95 rows."""


def fig3(R, out: Path, curves: dict, row_hz: float = ROW_HZ,
         name: str = "fig3_three_streams_one_scale.png",
         ref: str = "right") -> tuple[Path, dict]:
    """The three streams superimposed on ONE scale, drawn as a hidden-line waterfall.

    One axes, one row per recording at its own vertical offset; a row height is :data:`ROW_HZ`.
    A trace that exceeds it runs up into the rows above, unclipped and never rescaled. Rows are
    drawn from the top down, each at a higher z-order than the row above it, and each row's traces
    sit on a white fill from their baseline up to the highest of the three curves, so a lower
    row's peak covers what lies behind it instead of tangling with it. Within a row: fill, then the
    window lane, then the traces, so a peak that crosses its own lane stays visible. Everything else
    is Figure 1's layout. Returns the path and a record of the scale and of rows that overrun."""
    by = {}
    for r in R["rows"]:
        by.setdefault(r["slice_id"], {}).setdefault(r["stream"], []).append(r)
    for sid in by:
        for s in by[sid]:
            by[sid][s].sort(key=lambda r: r["win_start"])
    lead = "fast"
    order = [sid for sid, _ in recordings(R["rows"], lead)]

    def zero(ws):
        b = next((w for w in ws if w["window_type"] == "baseline"), None)
        return b["win_end"] if b else 0.0

    def treat(sid):
        return by[sid][lead][0]["first_treatment"]

    # Two columns (Tony, 2026-09-24: "put the TTX rows in a second column"): every recording with
    # a TTX window goes right, the rest left; each keeps the Figure-1 order within it.
    has_ttx = {sid: any(w["window_type"] == "TTX" for w in by[sid][lead]) for sid in order}
    columns = [[s for s in order if not has_ttx[s]], [s for s in order if has_ttx[s]]]
    columns = [c for c in columns if c]
    H, LH, GAP, GGAP, BGAP, AXROOM = 1.0, 0.2, 0.55, 1.1, 2.6, 1.4
    zs = {sid: zero(by[sid][lead]) for sid in order}
    lay = []
    for col in columns:
        y, base, prev, block_last = 0.0, {}, None, {}
        for sid in col:
            head = by[sid][lead][0]
            key = (head["first_treatment"], head["group"])
            if prev is not None:
                y -= BGAP + AXROOM if key[0] != prev[0] else (GGAP if key[1] != prev[1] else GAP)
            y -= LH + H
            base[sid] = y
            block_last[key[0]] = sid
            prev = key
        tmin = min(w["win_start"] - zs[sid] for sid in col for w in by[sid][lead])
        tmax = max(w["win_end"] - zs[sid] for sid in col for w in by[sid][lead])
        lay.append(dict(sids=col, base=base, block_last=block_last, y_end=y, tmin=tmin,
                        tmax=tmax))
    ytop = 2.8
    ymin = min(c["y_end"] for c in lay) - AXROOM
    # Same seconds per inch in every column, and the same data units per inch vertically.
    SEC_PER_IN, UNITS_PER_IN = 400.0, 1 / 0.3
    L_MARGIN, GUTTER, R_MARGIN, TOP_IN, BOT_IN = 1.5, 1.7, 2.3, 0.6, 0.2
    widths = [(c["tmax"] - c["tmin"]) / SEC_PER_IN for c in lay]
    data_h = (ytop - ymin) / UNITS_PER_IN
    W = L_MARGIN + sum(widths) + GUTTER * (len(lay) - 1) + R_MARGIN
    Hfig = data_h + TOP_IN + BOT_IN
    fig = plt.figure(figsize=(W, Hfig))
    axes, x0 = [], L_MARGIN
    for c, wi in zip(lay, widths):
        ax = fig.add_axes([x0 / W, BOT_IN / Hfig, wi / W, data_h / Hfig])
        ax.set_xlim(c["tmin"], c["tmax"])
        ax.set_ylim(ymin, ytop)
        ax.axis("off")
        axes.append(ax)
        x0 += wi + GUTTER
    level = {"fast": 0.15, "slow": 0.45, "combined": 0.75}
    overrun = []
    t_all = (min(c["tmin"] for c in lay), max(c["tmax"] for c in lay))
    for c in lay:
        c["t_all"] = t_all
    for ax, c in zip(axes, lay):
        overrun += _waterfall_column(ax, c, by, curves, zs, treat, lead, level,
                                     (H, LH, AXROOM), row_hz)
    if ref == "right":
        # The one reference scale for the whole figure: a bar one row high, right of the last
        # column's first row.
        ax, c = axes[-1], lay[-1]
        b0 = c["base"][c["sids"][0]]
        span = c["tmax"] - c["tmin"]
        xr = c["tmax"] + span * 0.015
        ax.plot([xr, xr], [b0, b0 + H], color="black", lw=1.2, clip_on=False)
        for yy, lab in ((b0, "0"), (b0 + H, f"{row_hz:g}")):
            ax.plot([xr, xr + span * 0.005], [yy, yy], color="black", lw=1.2, clip_on=False)
            ax.text(xr + span * 0.009, yy, lab, ha="left", va="center", fontsize=7.5,
                    clip_on=False)
        ax.text(xr + span * 0.04, b0 + H / 2, "onsets per ROI per second\n(one row height, "
                "the same in\nevery row and column)", ha="left", va="center", fontsize=7,
                clip_on=False)
    else:
        # Top left, in the empty space above the first column's block label (Tony, 2026-09-24).
        ax, c = axes[0], lay[0]
        span = c["tmax"] - c["tmin"]
        xr, y0 = c["tmin"] - span * 0.1, 1.5
        ax.plot([xr, xr], [y0, y0 + H], color="black", lw=1.4, clip_on=False)
        for yy, lab in ((y0, "0"), (y0 + H, f"{row_hz:.4f}")):
            ax.plot([xr, xr + span * 0.006], [yy, yy], color="black", lw=1.4, clip_on=False)
            ax.text(xr + span * 0.01, yy, lab, ha="left", va="center", fontsize=8,
                    clip_on=False)
        ax.text(xr + span * 0.07, y0 + H / 2, "onsets per ROI per second: one row height, the "
                "same in every row and column", ha="left", va="center", fontsize=8,
                clip_on=False)
    from matplotlib.patches import Patch
    key = [Patch(facecolor=TINT[k], edgecolor="#9A9A9A", hatch=HATCH.get(k), lw=0.5,
                 label=f"{SHORT[k]} {k}") for k in ("baseline", "senktide", "TTX", "wash",
                                                     "high K+")]
    fig.legend(handles=[*(Line2D([], [], color=STREAM_INK[s], lw=1.6, label=f"{s} stream")
                          for s in STREAMS), *key],
               loc="upper center", ncol=8, fontsize=9, frameon=False,
               bbox_to_anchor=(0.5, 1.0))
    p = out / name
    fig.savefig(p, dpi=130)
    plt.close(fig)
    overrun.sort(key=lambda r: -r[1])
    return p, dict(row_hz=row_hz, size_in=[round(W, 1), round(Hfig, 1)],
                   columns=[dict(recordings=len(c["sids"]),
                                 first_treatments=sorted({str(treat(s)) for s in c["sids"]}),
                                 minutes=round((c["tmax"] - c["tmin"]) / 60, 1)) for c in lay],
                   largest=overrun[0] if overrun else None,
                   rows_over_one_row=len(overrun), rows_over_two_rows=sum(r[2] > 2 for r in overrun),
                   overrun=[dict(slice_id=a, peak_hz=b, rows=c) for a, b, c in overrun])


def _waterfall_column(ax, c, by, curves, zs, treat, lead, level, dims,
                      row_hz: float = ROW_HZ) -> list:
    """Draw one column of Figure 3's waterfall into ``ax``; returns the rows that overrun one row
    height as ``(slice_id, peak_hz, rows)``."""
    H, LH, AXROOM = dims
    base, block_last, tmin, tmax = c["base"], c["block_last"], c["tmin"], c["tmax"]
    t_all = c["t_all"]          # read now: `c` is reused for curves in the loop below
    order = c["sids"]
    overrun, prev_treat = [], None
    for k, sid in enumerate(order):
        b0, z = base[sid], zs[sid]
        zf, zl, zt = 10 + 3 * k, 11 + 3 * k, 12 + 3 * k
        lane_lo = b0 + H
        t = treat(sid)
        named = t != prev_treat
        prev_treat = t
        # the lane, flush on top of the trace's row
        for w in by[sid][lead]:
            a, b = w["win_start"] - z, w["win_end"] - z
            ax.add_patch(plt.Rectangle((a, lane_lo), b - a, LH, facecolor=TINT.get(
                w["window_type"], "#FFFFFF"), edgecolor="#9A9A9A", hatch=HATCH.get(
                w["window_type"]), lw=0, zorder=zl))
            if named:
                ax.text((a + b) / 2, lane_lo + LH + 0.12, SHORT.get(w["window_type"], "?"),
                        ha="center", va="bottom", fontsize=6, color="0.25", zorder=zl)
        for s in STREAMS:
            for w in by[sid].get(s, []):
                for st in w["measures"]["60.0"].get("stretches", {}).get("3.0", []):
                    yy = lane_lo + LH * level[s]
                    ax.plot([st["start"] - z, st["end"] - z], [yy, yy], color=STREAM_INK[s],
                            lw=1.6, solid_capstyle="butt", zorder=zl + 0.5)
        ax.plot([0, 0], [lane_lo, lane_lo + LH], color="black", lw=1.0, zorder=zl + 0.5)
        # the traces: white fill up to the highest curve, then the curves
        cs = {s: curves.get(sid, {}).get(s) for s in STREAMS}
        grid = next((np.asarray(c["starts"]) for c in cs.values() if c), None)
        if grid is not None:
            top = np.max([np.asarray(c["rate_hz"]) for c in cs.values()
                          if c and len(c["rate_hz"]) == grid.size], axis=0)
            x = grid + 30.0 - z
            ax.fill_between(x, b0, b0 + top / row_hz, color="white", lw=0, zorder=zf)
            peak = float(top.max())
            if peak > row_hz:
                overrun.append((sid, peak, peak / row_hz))
            for s in STREAMS:
                c = cs[s]
                if c:
                    ax.plot(x, b0 + np.asarray(c["rate_hz"]) / row_hz, color=STREAM_INK[s],
                            lw=0.6, zorder=zt)
        ax.plot([tmin, tmax], [b0, b0], color="0.85", lw=0.4, zorder=zf - 0.5)
        ax.text(tmin - (tmax - tmin) * 0.005, b0 + H / 2, f"{sid}  {by[sid][lead][0]['group']}",
                ha="right", va="center", fontsize=6.5, clip_on=False)
    # One time axis under the last row of each first-treatment block. Every column uses the tick
    # interval of the widest one, so equal minutes look the same in both.
    tk = [x for x in tticks(t_all[0], t_all[1]) if tmin <= x <= tmax]
    for tr, sid in block_last.items():
        ya = base[sid] - 0.35
        ax.plot([tmin, tmax], [ya, ya], color="black", lw=0.8, clip_on=False)
        for x in tk:
            ax.plot([x, x], [ya, ya - 0.15], color="black", lw=0.8, clip_on=False)
            ax.text(x, ya - 0.25, "0" if x == 0 else tlabel(x), ha="center", va="top",
                    fontsize=9, clip_on=False)
        ax.text((tmin + tmax) / 2, ya - 0.8, "time relative to the end of each recording's "
                "baseline window, minutes (negative = baseline)", ha="center", va="top",
                fontsize=8.5, clip_on=False)
    firsts = {}
    for sid in order:
        firsts.setdefault(treat(sid), sid)
    for tr, sid in firsts.items():
        ax.text(tmin, base[sid] + H + LH + 0.75, f"first treatment: {tr or 'none'}",
                ha="left", va="bottom", fontsize=10, fontweight="bold", clip_on=False)
    return overrun


def fig2(R, out: Path) -> Path:
    fig, ax = plt.subplots(figsize=(8.5, 5.8))
    col = {"baseline": "0.45", "TTX": "#3182BD", "senktide": "#E6550D", "high K+": "#31A354",
           "wash": "#9E9AC8"}
    mark = {"fast": "o", "slow": "s", "combined": "^"}
    for r in R["rows"]:
        for st in r["measures"]["60.0"].get("stretches", {}).get("3.0", []):
            ax.plot(st["median_breadth"], st["peak_elevation"], mark[r["stream"]], ms=4.5,
                    alpha=0.7, color=col.get(r["window_type"], "0.6"), mec="none")
    for b in R["bench"]:
        for st in b["measures"]["60.0"].get("stretches", {}).get("3.0", []):
            ax.plot(st["median_breadth"], st["peak_elevation"], "*", ms=11, color="black")
    ax.set_yscale("log")
    ax.set_yticks([3, 5, 10, 20, 50])
    ax.set_yticklabels(["3", "5", "10", "20", "50"])
    ax.minorticks_off()
    ax.set_xlabel("median breadth over the stretch (fraction of ROIs above their own median)")
    ax.set_ylabel("peak within-window elevation (× the window's median population rate)")
    h = [Line2D([], [], marker="o", ls="none", color=c, label=t) for t, c in col.items()]
    h += [Line2D([], [], marker=m, ls="none", color="0.3", label=f"{s} stream")
          for s, m in mark.items()]
    h += [Line2D([], [], marker="*", ls="none", color="black", ms=11,
                 label="bench's elevated-rate test (seeds 1–8, quiet and busy)")]
    ax.legend(handles=h, fontsize=7.5, loc="upper left", frameon=False)
    p = out / "fig2_elevation_vs_breadth.png"
    fig.savefig(p, dpi=150, bbox_inches="tight")
    plt.close(fig)
    return p


def fmt(x, d=2):
    return "–" if x is None else f"{x:.{d}f}"


def tables(R, out: Path) -> Path:
    S, groups = R["summary"], R["groups"]
    L = []
    sections = (("BASELINE windows only: the only admissible source for anything that shapes the "
                 "bench (FOUNDATIONS §9)", ("baseline",)),
                ("Treatment and control windows: DESCRIPTIVE ONLY, not calibration",
                 ("TTX", "senktide", "high K+", "wash")))
    for title, types in sections:
        L += [f"### {title}", ""]
        for stream in STREAMS:
            L += [f"#### {stream} stream, 60 s window", "",
                  "| window type | group | windows | recordings with a stretch, k = 2 / 3 / 5 | "
                  "stretches per hour, k = 2 / 3 / 5 | median duration, s, k = 3 | "
                  "median peak elevation, ×, k = 3 | median breadth, k = 3 |",
                  "|---|---|---|---|---|---|---|---|"]
            for wt in types:
                for g in [*groups, "all"]:
                    c = S.get(stream, {}).get(wt, {}).get(g)
                    if not c:
                        continue
                    k2, k3, k5 = c["2.0"], c["3.0"], c["5.0"]
                    L.append(
                        f"| {wt} | {g} | {k3['windows']} | {k2['recordings_with_stretch']} / "
                        f"{k3['recordings_with_stretch']} / {k5['recordings_with_stretch']} | "
                        f"{fmt(k2['stretches_per_hour'])} / {fmt(k3['stretches_per_hour'])} / "
                        f"{fmt(k5['stretches_per_hour'])} | "
                        f"{fmt(k3['median_duration_sec'], 0)} | "
                        f"{fmt(k3['median_peak_elevation'], 1)} | {fmt(k3['median_breadth'])} |")
            L.append("")
    L += ["#### The GDX senktide windows (OVX and ORX), by recording, 60 s window", "",
          "| recording | group | stream | window median rate, Hz | peak within-window elevation, × "
          "| k = 3 stretches: start into window (s), duration (s), peak (×), breadth |",
          "|---|---|---|---|---|---|"]
    for r in sorted(R["rows"], key=lambda r: (group_key(r["group"] or "~"), r["slice_id"],
                                               STREAMS.index(r["stream"]))):
        if r["window_type"] != "senktide" or r["group"] not in ("OVX", "ORX"):
            continue
        m = r["measures"]["60.0"]
        st = m.get("stretches", {}).get("3.0", [])
        desc = "; ".join(f"{x['start'] - r['win_start']:.0f}, {x['duration']:.0f}, "
                         f"{x['peak_elevation']:.1f}, {x['median_breadth']:.2f}" for x in st) or "none"
        L.append(f"| {r['slice_id']} | {r['group']} | {r['stream']} | {fmt(m['median_rate_hz'], 4)} "
                 f"| {fmt(m['peak_elevation'], 1)} | {desc} |")
    L += ["", "#### The ADR-0008 floor, whole window against stretches (k = 3) removed", "",
          "| stream | window type | group | windows with a stretch | median floor, whole window, "
          "ROIs | median floor, stretches removed, ROIs | windows where the floor falls |",
          "|---|---|---|---|---|---|---|"]
    for stream in STREAMS:
        for wt in TYPES:
            for g in [*groups, "all"]:
                rs = [r for r in R["rows"] if r["stream"] == stream and r["window_type"] == wt
                      and (g == "all" or r["group"] == g)
                      and r["floor"]["seconds_removed"] > 0
                      and "floor" in r["floor"]["whole"]
                      and "floor" in r["floor"]["stretches_removed"]]
                if not rs:
                    continue
                w = [r["floor"]["whole"]["floor"] for r in rs]
                x = [r["floor"]["stretches_removed"]["floor"] for r in rs]
                L.append(f"| {stream} | {wt} | {g} | {len(rs)} | {np.median(w):.0f} | "
                         f"{np.median(x):.0f} | {sum(a < b for a, b in zip(x, w))} |")
    L += ["", "#### The bench's elevated-rate test on the same scales (60 s window, k = 3)", "",
          "| bench | background | peak within-window elevation, × | duration, s | median breadth |",
          "|---|---|---|---|---|"]
    for stream in STREAMS:
        for reg in ("baseline_quiet", "baseline_busy"):
            bs = [b for b in R["bench"] if b["stream"] == stream and b["regime"] == reg]
            st = [s for b in bs for s in b["measures"]["60.0"]["stretches"]["3.0"]]
            if st:
                L.append(f"| {stream} | {reg.split('_')[1]} | "
                         f"{np.median([s['peak_elevation'] for s in st]):.1f} "
                         f"({min(s['peak_elevation'] for s in st):.1f}–"
                         f"{max(s['peak_elevation'] for s in st):.1f}) | "
                         f"{np.median([s['duration'] for s in st]):.0f} | "
                         f"{np.median([s['median_breadth'] for s in st]):.2f} |")
    p = out / "tables.md"
    p.write_text("\n".join(L) + "\n", encoding="utf-8")
    return p


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--run", type=Path, required=True)
    ap.add_argument("--also", type=Path, default=None)
    a = ap.parse_args(argv)
    R = json.loads((a.run / "results.json").read_text())
    curves = full_curves(R, a.run)
    p3, scale = fig3(R, a.run, curves)
    print("figure 3 scale:", scale)
    p3b, scale_b = fig3(R, a.run, curves, row_hz=ROW_HZ_3B, name="fig3b_three_streams_gain3.png",
                        ref="topleft")
    print("figure 3b scale:", json.dumps(scale_b))
    made = [*(fig1(R, s, a.run, curves) for s in STREAMS), fig2(R, a.run), p3, p3b,
            tables(R, a.run)]
    if a.also:
        a.also.mkdir(parents=True, exist_ok=True)
        for p in made:
            shutil.copy2(p, a.also / p.name)
    for p in made:
        print(p)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
