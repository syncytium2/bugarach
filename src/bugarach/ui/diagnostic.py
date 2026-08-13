"""The troubleshooting view: raster + detector lanes + ground truth, one x-axis.

Ported from interface2's ``explore_sce`` (``drawStream``). The interactive viewer
in :mod:`bugarach.ui.app` browses a slice; this answers a different question —
*why did this detector fire there, and did it find what was planted?* — and
returns a static figure you can save next to a run.

What is carried over from the original, and why each detail is load-bearing:

* **Detector lanes above the raster.** One row per detector, each detection drawn
  as a bar spanning ``onset → onset + width``. Stacked, they make disagreement
  between the six legible at a glance, which a per-detector plot cannot.
* **A white separator band** between the raster and the lanes. Without it a
  horizontal duration bar reads as a burst of raster activity — the original
  calls this out explicitly, and it is worth keeping.
* **ROIs sorted by event count, ascending.** Quiet ROIs at the bottom, busy ones
  at the top; coordination reads as a vertical stripe instead of being lost in
  whichever order the store happened to use.
* **Isolated events in red.** An onset that falls inside no detected coordination
  window is drawn red, the rest in grey. This is the diagnostic that shows *what
  a detector left on the table* rather than only what it claimed.
* **Lane geometry scales with ROI count** (``ls = max(1, n_roi / 50)``), so lanes
  stay visible on a 400-ROI recording instead of being squeezed into a sliver.

What is new here, because the original could not have it: a **ground-truth lane**.
With planted data there is a right answer, so hits, misses and false alarms are
drawn rather than inferred — green for a recovered event, red for a missed one,
and a marker on each detection that matched nothing.

Plot conventions follow CLAUDE.md: 60-base time ticks via the shared
``_time_axis_hook``, identity in the y-label rather than a title, x linked
through the shared ``t`` dimension, y unlinked per row.
"""

from __future__ import annotations

import holoviews as hv
import numpy as np

from bugarach.score import score_detections
from bugarach.ui.app import COLORS, SHORT, _time_axis_hook

GT_HIT = "#2e7d32"
GT_MISS = "#c62828"
ISOLATED = "#d92020"
MEMBER = "#444444"


def _spans(onsets, widths, ext):
    """(onset, width) pairs -> [(t0, t1)], clipped to the extent. A zero or
    non-finite width becomes a hairline so the detection is still visible —
    losing it entirely would read as 'the detector found nothing there'."""
    if onsets is None or np.size(onsets) == 0:
        return []
    o = np.asarray(onsets, dtype=float).ravel()
    w = np.asarray(widths, dtype=float).ravel() if widths is not None \
        else np.zeros_like(o)
    if w.size != o.size:
        w = np.zeros_like(o)
    span = float(ext[1] - ext[0])
    hair = max(span * 0.0015, 1e-9)
    out = []
    for a, b in zip(o, w):
        if not np.isfinite(a):
            continue
        ww = b if np.isfinite(b) and b > 0 else hair
        out.append((max(a, ext[0]), min(a + ww, ext[1])))
    return out


def _is_member(t, spans, tol=0.0):
    """Boolean per onset: does it fall inside any detected window?"""
    if not spans or t.size == 0:
        return np.zeros(t.size, dtype=bool)
    lo = np.array([s[0] for s in spans]) - tol
    hi = np.array([s[1] for s in spans]) + tol
    return np.any((t[:, None] >= lo[None, :]) & (t[:, None] <= hi[None, :]), axis=1)


def coordination_raster(
    stream,
    *,
    ext,
    lanes: dict | None = None,
    gt=None,
    member_source: str | None = None,
    tol_sec: float = 1.5,
    name: str = "events",
    width: int = 950,
    height: int | None = None,
):
    """Raster with detector lanes and (optionally) a ground-truth lane.

    stream: a :class:`bugarach.store.Stream`.
    ext: ``(t_lo, t_hi)``.
    lanes: ``{detector_name: (onsets, widths)}`` — exactly the shape
      ``bugarach.ui.app._compute`` already produces, so any of the six drops in.
    gt: a :class:`bugarach.simulate.GroundTruth`; adds the ground-truth lane and
      marks each detection lane's false alarms.
    member_source: which detector's windows decide whether a raster onset is a
      coordination member (red = isolated). Defaults to the first lane.
    tol_sec: match tolerance for hits/misses.
    """
    lanes = lanes or {}
    n_roi = stream.n_rois

    # --- ROI order: quietest at the bottom, so coordination reads as a stripe
    counts = [int(np.sum(np.isfinite(np.asarray(v, dtype=float))))
              for v in stream.t50rise]
    order = np.argsort(counts, kind="stable")

    src = member_source or (next(iter(lanes)) if lanes else None)
    src_spans = _spans(*lanes[src], ext) if src in lanes else []

    ts, ys, member = [], [], []
    for row, roi in enumerate(order):
        v = np.asarray(stream.t50rise[roi], dtype=float)
        v = v[np.isfinite(v) & (v >= ext[0]) & (v <= ext[1])]
        if v.size == 0:
            continue
        ts.append(v)
        ys.append(np.full(v.size, row))
        member.append(_is_member(v, src_spans))
    t = np.concatenate(ts) if ts else np.zeros(0)
    y = np.concatenate(ys) if ys else np.zeros(0)
    mem = np.concatenate(member) if member else np.zeros(0, dtype=bool)

    # --- lane geometry, scaled to the population (ported from drawStream)
    ls = max(1.0, n_roi / 50.0)
    gap = 1.1 * ls
    raster_gap = 2.0 * ls
    bar_h = 0.34 * ls
    n_lane = len(lanes) + (1 if gt is not None else 0)
    y0 = n_roi + raster_gap
    y_max = y0 + max(n_lane, 1) * gap + 0.6 * ls

    items = []

    # white separator: a duration bar must never read as raster activity
    items.append(hv.Rectangles(
        [(ext[0], n_roi + 0.4 * ls, ext[1], y0 - bar_h - 0.05 * ls)]
    ).opts(color="white", line_alpha=0, alpha=1.0))

    # --- raster: isolated onsets red, members grey
    for m, colour, label in ((~mem, ISOLATED, "isolated"), (mem, MEMBER, "in a window")):
        if not np.any(m):
            continue
        items.append(hv.Scatter((t[m], y[m]), kdims=["t"], vdims=["roi"]).opts(
            marker="dash", angle=90, size=5, color=colour,
            alpha=0.85 if colour == ISOLATED else 0.55))

    # --- detector lanes, first at the top
    lane_y = {}
    for j, (key, ev) in enumerate(lanes.items()):
        yy = y0 + (n_lane - 1 - j) * gap
        lane_y[key] = yy
        sp = _spans(*ev, ext)
        colour = COLORS.get(key, "#555555")
        if sp:
            items.append(hv.Rectangles(
                [(a, yy - bar_h, b, yy + bar_h) for a, b in sp]
            ).opts(color=colour, line_alpha=0, alpha=0.85))
        items.append(hv.Text(ext[0], yy + bar_h * 1.6,
                             SHORT.get(key, key), halign="left",
                             fontsize=8).opts(color=colour))

        # false alarms, when there is a truth to be wrong about
        if gt is not None:
            sc = score_detections(gt, ev[0], tol_sec=tol_sec)
            if sc.fa_times.size:
                items.append(hv.Scatter(
                    (sc.fa_times, np.full(sc.fa_times.size, yy))
                ).opts(marker="x", size=7, color=ISOLATED, alpha=0.9))

    # --- ground truth lane at the bottom of the stack
    if gt is not None:
        yy = y0
        planted = np.asarray(gt.times, dtype=float)
        if planted.size:
            ref = next(iter(lanes)) if lanes else None
            hits = (score_detections(gt, lanes[ref][0], tol_sec=tol_sec).hits
                    if ref else np.zeros(planted.size, dtype=bool))
            for m, colour in ((hits, GT_HIT), (~hits, GT_MISS)):
                if np.any(m):
                    items.append(hv.Scatter(
                        (planted[m], np.full(int(m.sum()), yy))
                    ).opts(marker="triangle", size=9, color=colour, alpha=0.95))
        items.append(hv.Text(ext[0], yy + bar_h * 1.6, "planted",
                             halign="left", fontsize=8).opts(color="#333333"))
        # the dense-but-random block, if there is one: it should stay empty
        hw = gt.params.get("hot_window")
        if hw is not None:
            items.append(hv.Rectangles([(hw[0], 0, hw[1], y_max)]).opts(
                color="#b0761f", alpha=0.10, line_alpha=0))

    if height is None:
        height = int(np.clip(120 + 3.2 * n_roi + 14 * n_lane, 180, 700))

    return hv.Overlay(items).opts(
        width=width, height=height, xlim=tuple(ext), ylim=(0, y_max),
        title="", ylabel=f"{name} · {n_roi} ROI", yaxis=None,
        fontsize={"ylabel": "10pt"},
        show_legend=False, hooks=[_time_axis_hook],
        tools=["xwheel_zoom", "xpan", "reset", "hover"],
        active_tools=["xpan"], default_tools=["reset"],
    )


def score_table(gt, lanes: dict, *, tol_sec: float = 1.5) -> str:
    """Plain-text scoreboard for the same lanes — the numbers behind the picture.

    Deliberately text: it belongs in a log or a commit message next to the run,
    where a PNG cannot go.
    """
    rows = ["detector    recall  prec    F1   FA  hotFA  by participation",
            "-" * 74]
    for key, ev in lanes.items():
        s = score_detections(gt, ev[0], tol_sec=tol_sec)
        by = " ".join(f"{int(f * 100)}%:{s.recall_at(f):.2f}"
                      for f in sorted(s.by_frac, reverse=True))
        rows.append(f"{SHORT.get(key, key):<11s} {s.recall:5.2f}  {s.precision:5.2f}  "
                    f"{s.f1:5.2f} {s.n_fa:4d}  {s.hot_fa:4d}   {by}")
    return "\n".join(rows)
