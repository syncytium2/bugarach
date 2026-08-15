"""The troubleshooting view: detector lanes over an ROI raster, sharing an x-axis.

The interactive viewer in :mod:`bugarach.ui.app` browses a slice. This answers a
different question — *why did this detector fire there, and did it find what was
planted?* — and returns a figure you can save next to a run.

Structure, and why it is two panels rather than one
---------------------------------------------------
A first version drew the detector lanes *inside* the raster axes, the way
``explore_sce``'s ``drawStream`` does, with lane names written as floating text
at the left edge. In MATLAB that works because the text is placed in normalized
figure coordinates outside the data area. Rebuilt naively it does not: the labels
land **on top of the data**, and there is no axis to hang them off.

So the lanes get their own panel with a real categorical y-axis, x-linked to the
raster through the shared ``t`` dimension. Detector names are tick labels — they
cannot collide with anything, at any zoom, by construction.

Reading it
----------
* **Lanes panel** — the **planted** row first, then one row per detector. Ground
  truth leads because every row under it is an attempt at it, and a reader
  scanning down should meet the answer before the attempts. A bar spans
  ``onset → onset + width``: that is what the detector claimed. A **✕** marks a
  detection that matched no planted event (a false alarm), a **○** a duplicate
  of one another detection already claimed. On the planted row, ▲ marks an event
  some detector recovered and ▼ one every detector missed, with ▽ distractors
  riding above.
* **Raster** — one row per ROI, sorted quietest at the bottom, so coordination
  reads as a vertical stripe rather than being lost in store order. Onsets that
  fall inside a detected window are **highlighted**; everything else is muted
  grey. The highlight answers "what did this detector actually claim", and the
  grey around it answers "what did it leave".
* **Shaded band** — a dense-but-random block containing **no** planted events by
  construction. Detections inside it are false alarms, and a detector that keys
  on rate rather than coordination lights it up. That is the promiscuity probe.

Colour is used for one thing at a time: detector identity in the lanes, and
found/missed in the ground-truth row. The raster is deliberately monochrome so
it never competes with them.

Plot conventions follow CLAUDE.md: 60-base time ticks via the shared
``_time_axis_hook``, identity in the y-label, x linked through ``t``.
"""

from __future__ import annotations

import holoviews as hv
import numpy as np

from bugarach.score import score_detections
from bugarach.ui.app import COLORS, TITLES, _signal_row, _time_axis_hook

FOUND = "#1b7f3b"
MISSED = "#b3261e"
FALSE_ALARM = "#b3261e"
RASTER_MUTED = "#c9c9c9"
RASTER_HIT = "#1f1f1f"
PROBE_BAND = "#e8a33d"


def _spans(onsets, widths, ext):
    """(onset, width) -> [(t0, t1)] clipped to the extent.

    A zero or non-finite width becomes a small visible sliver rather than
    nothing: a detection drawn as zero pixels reads as "the detector found
    nothing here", which is the opposite of the truth.
    """
    if onsets is None or np.size(onsets) == 0:
        return []
    o = np.asarray(onsets, dtype=float).ravel()
    w = np.asarray(widths, dtype=float).ravel() if widths is not None \
        else np.zeros_like(o)
    if w.size != o.size:
        w = np.zeros_like(o)
    span = float(ext[1] - ext[0])
    floor = max(span * 0.002, 1e-9)
    out = []
    for a, b in zip(o, w):
        if not np.isfinite(a):
            continue
        ww = b if np.isfinite(b) and b > 0 else 0.0
        out.append((max(a, ext[0]), min(a + max(ww, floor), ext[1])))
    return out


def _is_member(t, spans):
    """Per onset: does it fall inside any detected window?"""
    if not spans or t.size == 0:
        return np.zeros(t.size, dtype=bool)
    lo = np.array([s[0] for s in spans])
    hi = np.array([s[1] for s in spans])
    return np.any((t[:, None] >= lo[None, :]) & (t[:, None] <= hi[None, :]), axis=1)


def _base(ext, ydim: str):
    """An invisible t-dimensioned point, placed FIRST in every overlay.

    Two jobs, both learned by getting them wrong:

    1. HoloViews takes its x-dimension from the first element, and
       ``Rectangles`` carries ``x0`` — leading with one relabels the shared axis
       to "x0" and silently unlinks it from the raster. ``ui.app`` documents this
       trap for the signal rows; this is the same trap one element type over.
    2. The y-dimension NAME is what links y-ranges between panels. Sharing a name
       across the lane panel and the raster made the lanes inherit the raster's
       0–30 ROI range and collapse into a sliver at the bottom. Each panel passes
       its own name, which is the same rule CLAUDE.md already states for the
       signal rows: unique value dimension per row, so y never links; x links
       through the shared ``t``.
    """
    return hv.Scatter(([ext[0]], [0.0]), kdims=["t"], vdims=[ydim]).opts(alpha=0)


def lane_panel(lanes: dict, *, ext, gt=None, tol_sec: float = 1.5,
               width: int = 1000, row_px: int = 26):
    """Detector lanes with a real categorical y-axis (labels cannot collide)."""
    lanes = lanes or {}
    # Ground truth goes at the TOP: it is what every other row is judged
    # against, and a reader scanning down should meet the answer before the
    # attempts at it (Tony, 2026-08-15). Distractors ride just above it and
    # still clear `ylim` — the top row sits 0.8 units below the limit and the
    # marker needs about 0.14.
    rows = (["planted"] if gt is not None else []) + list(lanes)
    ypos = {name: len(rows) - 1 - i for i, name in enumerate(rows)}
    items = [_base(ext, "lane")]

    if gt is not None:
        hw = gt.params.get("hot_window")
        if hw is not None:
            items.append(hv.VSpan(float(hw[0]), float(hw[1])).opts(
                color=PROBE_BAND, alpha=0.16))

    for key, ev in lanes.items():
        y = ypos[key]
        colour = COLORS.get(key, "#555555")
        sp = _spans(ev[0], ev[1] if len(ev) > 1 else None, ext)
        if sp:
            items.append(hv.Rectangles(
                [(a, y - 0.30, b, y + 0.30) for a, b in sp]
            ).opts(color=colour, line_color=colour, line_width=1, alpha=0.9))
        if gt is not None:
            # spans, not points — the same rule the scoreboard and the bench
            # use. Scored as points, a binned detector's bin edge lands up to a
            # bin-width early and gets an ✕ beside the very event it found:
            # every SCE detection was marked a false alarm while sitting on top
            # of a planted one.
            sc = score_detections(gt, ev[0],
                                  widths=ev[1] if len(ev) > 1 else None,
                                  tol_sec=tol_sec)
            # a duplicate — a second detection of an event another detection
            # already claimed — is not the same failure as firing at nothing,
            # and drawing both as ✕ is what made the lanes look like every
            # detector was hallucinating next to real events.
            dup = set(np.round(sc.dup_times, 6).tolist())
            spurious = np.array([t for t in sc.fa_times
                                 if round(float(t), 6) not in dup])
            if spurious.size:
                items.append(hv.Scatter(
                    (spurious, np.full(spurious.size, y + 0.40))).opts(
                    marker="x", size=7, color=FALSE_ALARM, line_width=2,
                    alpha=0.95))
            if sc.dup_times.size:
                items.append(hv.Scatter(
                    (sc.dup_times, np.full(sc.dup_times.size, y + 0.40))).opts(
                    marker="circle", size=5, color=FALSE_ALARM, alpha=0.55,
                    line_color=FALSE_ALARM, line_width=1, fill_alpha=0.0))

    if gt is not None and len(getattr(gt, "distractors", [])):
        # A named element with no ink reads as deliberate: the report header
        # counts distractors, so the figure has to show them.
        dt = np.asarray(gt.distractor_times, dtype=float)
        items.append(hv.Scatter((dt, np.full(dt.size, ypos["planted"] + 0.42))).opts(
            marker="inverted_triangle", size=7, color="#5a5a5a",
            fill_alpha=0.0, line_width=1.2))

    if gt is not None:
        y = ypos["planted"]
        planted = np.asarray(gt.times, dtype=float)
        if planted.size:
            found = np.zeros(planted.size, dtype=bool)
            for ev in lanes.values():
                found |= score_detections(gt, ev[0],
                                          widths=ev[1] if len(ev) > 1 else None,
                                          tol_sec=tol_sec).hits
            for mask, colour, marker in ((found, FOUND, "triangle"),
                                         (~found, MISSED, "inverted_triangle")):
                if np.any(mask):
                    items.append(hv.Scatter(
                        (planted[mask], np.full(int(mask.sum()), y))
                    ).opts(marker=marker, size=10, color=colour,
                           line_color="white", line_width=1))

    yticks = [(ypos[n], TITLES.get(n, n)) for n in rows]
    return hv.Overlay(items).opts(
        width=width, height=max(90, row_px * len(rows) + 46),
        xlim=tuple(ext), ylim=(-0.8, len(rows) - 0.2),
        yticks=yticks, ylabel="", xlabel="", title="", xaxis=None,
        fontsize={"yticks": "9pt"},
        show_legend=False, hooks=[_time_axis_hook],
        tools=["xwheel_zoom", "xpan", "reset", "hover"],
        active_tools=["xpan"], default_tools=["reset"],
    )


def raster_panel(stream, *, ext, member_spans=None, gt=None, name="events",
                 width: int = 1000, height: int | None = None):
    """ROI raster, quietest ROI at the bottom, onsets inside a detected window
    highlighted against a muted background."""
    n_roi = stream.n_rois
    counts = [int(np.sum(np.isfinite(np.asarray(v, dtype=float))))
              for v in stream.t50rise]
    order = np.argsort(counts, kind="stable")

    ts, ys = [], []
    for row, roi in enumerate(order):
        v = np.asarray(stream.t50rise[roi], dtype=float)
        v = v[np.isfinite(v) & (v >= ext[0]) & (v <= ext[1])]
        if v.size:
            ts.append(v)
            ys.append(np.full(v.size, row))
    t = np.concatenate(ts) if ts else np.zeros(0)
    y = np.concatenate(ys) if ys else np.zeros(0)
    mem = _is_member(t, member_spans or [])

    items = [_base(ext, "roi")]
    if gt is not None:
        hw = gt.params.get("hot_window")
        if hw is not None:
            items.append(hv.VSpan(float(hw[0]), float(hw[1])).opts(
                color=PROBE_BAND, alpha=0.16))
    # muted first, highlighted on top, so a claimed event is never hidden
    for mask, colour, alpha, size in ((~mem, RASTER_MUTED, 0.85, 4),
                                      (mem, RASTER_HIT, 0.95, 6)):
        if np.any(mask):
            items.append(hv.Scatter((t[mask], y[mask]),
                                    kdims=["t"], vdims=["roi"]).opts(
                marker="dash", angle=90, size=size, color=colour, alpha=alpha))

    if height is None:
        height = int(np.clip(30 + 9 * n_roi, 200, 640))
    return hv.Overlay(items).opts(
        width=width, height=height, xlim=tuple(ext), ylim=(-1, n_roi),
        ylabel=f"{name} · {n_roi} ROI", title="",
        fontsize={"ylabel": "10pt"},
        show_legend=False, hooks=[_time_axis_hook],
        tools=["xwheel_zoom", "xpan", "reset", "hover"],
        active_tools=["xpan"], default_tools=["reset"],
    )


def trace_panel(traces: dict, *, ext, width: int = 1000, height: int = 112):
    """One analysis trace per detector, x-linked to the raster above.

    The lanes say *what* a detector claimed; these say **why**. Each row is the
    statistic the detector actually thresholds — distinct-ROI coactivity, event
    rate against its rolling context, the SPIKE-synchrony profile — drawn with
    its threshold and its claimed windows shaded on top. A detection is then
    readable as a crossing rather than as an assertion, and a *miss* becomes
    legible too: a peak that rose and stopped short is a different failure from
    a statistic that never moved.

    It answers questions the lanes cannot. SCE's ceiling on a long recording
    looks like a bad threshold until you see the trace — a 10 s-binned staircase
    against a flat percentile line, where the percentile is taken over bins, so
    the number of bins that can clear it is set by how long the recording is.

    Rows reuse ``ui.app._signal_row`` — but each one is given an **explicit
    ylim**, which the viewer does not need and this figure does.

    The unique-value-dimension trick that keeps y unlinked in ``ui.app`` is not
    sufficient inside an ``hv.Layout`` with ``shared_axes``. The curve's value
    dimension is per-detector, but the detection shading is ``hv.Rectangles``,
    whose ``y0``/``y1`` dimensions are named identically in every row — so the
    ranges link through the shading instead of through the curve. Measured
    before this line existed: five of six rows rendered at y=(-3.7, 40.7),
    squashing spike-sync's 0–1 synchrony profile into a flat line at the bottom
    of an ROI-count axis. It looked like a detector that never fired, on a row
    labelled with its 222 detections.

    That is the same trap ``_base`` documents for the x-axis, one element type
    over. Pinning the limits from each row's own data is the fix that does not
    depend on getting HoloViews dimension matching exactly right.
    """
    rows = []
    for det, (t, y, events, extra) in traces.items():
        fy = np.asarray(y, dtype=float)
        fy = fy[np.isfinite(fy)]
        top = float(fy.max()) if fy.size else 1.0
        bottom = min(0.0, float(fy.min()) if fy.size else 0.0)
        pad = max((top - bottom) * 0.08, 1e-9)
        # Full name, not the viewer's abbreviation: this figure's rows are tall
        # enough to carry it, and the rotated y-label is the only place a reader
        # learns which detector a trace belongs to. `height` is set by the
        # longest of them — "rate+context (14)" runs ~100px at 9pt, so a row
        # short enough for "CIC" clips it.
        rows.append(_signal_row(det, t, y, events, extra, ext,
                                label=TITLES.get(det, det)).opts(
            width=width, height=height, xaxis=None,
            ylim=(bottom - pad, top + pad)))
    if rows:
        rows[-1] = rows[-1].opts(height=height + 28, xaxis="bottom")
    return rows


def coordination_diagnostic(stream, *, ext, lanes=None, gt=None,
                            member_source: str | None = None,
                            tol_sec: float = 1.5, name: str = "events",
                            traces=None,
                            width: int = 1000, height: int | None = None):
    """Lanes over raster over analysis traces, all x-linked.

    ``traces`` is ``ui.app._compute``'s output for one stream, keyed by detector
    — ``{det: (t, y, (onsets, widths), extra)}``. Omit it for the lanes-only
    figure.
    """
    lanes = lanes or {}
    src = member_source or (next(iter(lanes)) if lanes else None)
    spans = _spans(lanes[src][0], lanes[src][1], ext) if src in lanes else []
    top = lane_panel(lanes, ext=ext, gt=gt, tol_sec=tol_sec, width=width)
    bottom = raster_panel(stream, ext=ext, member_spans=spans, gt=gt, name=name,
                          width=width, height=height)
    # shared_axes links by DIMENSION NAME: both panels use "t" for x, and their
    # y dimensions are deliberately named differently ("lane" vs "roi") so only
    # x links. Same rule as the signal rows in ui.app.
    panels = [top, bottom]
    if traces:
        # the raster stops drawing an x-axis once something sits below it
        panels[1] = bottom.opts(xaxis=None)
        panels += trace_panel(traces, ext=ext, width=width)
    layout = panels[0]
    for p in panels[1:]:
        layout = layout + p
    # toolbar=None: these render to static PNG for documents, and live
    # pan/zoom/save icons baked into an image are chrome a reader tries
    # to click. The interactive HTML keeps its own.
    return layout.cols(1).opts(shared_axes=True, merge_tools=True,
                               toolbar=None)


def _key(kind: str, colour: str, size: int = 16) -> str:
    """One legend key, drawn as SVG rather than typed as a character.

    The first version used Unicode glyphs — ``&#10005;`` for the false alarm and
    ``&#9711;`` for the duplicate. They do not line up: U+2715 and U+25EF carry
    different vertical metrics in every system font, so the two markers that
    have to read as a matched pair sat at visibly different heights, and a
    reader could not tell whether the offset meant something (Tony, 2026-08-15).
    In the *plot* they were always aligned — both are drawn at ``y + 0.40`` —
    which made the legend actively misleading about the figure it explains.

    Drawing them puts the baseline under our control and makes each key the same
    shape bokeh renders, instead of the nearest character to it.
    """
    c = size / 2
    body = {
        "x": f'<path d="M{c-4.6} {c-4.6}L{c+4.6} {c+4.6}M{c+4.6} {c-4.6}'
             f'L{c-4.6} {c+4.6}" stroke="{colour}" stroke-width="2.2" '
             f'stroke-linecap="round" fill="none"/>',
        "circle": f'<circle cx="{c}" cy="{c}" r="4.1" stroke="{colour}" '
                  f'stroke-width="1.5" fill="none"/>',
        "triangle": f'<path d="M{c} {c-5}L{c+5} {c+3.8}L{c-5} {c+3.8}Z" '
                    f'fill="{colour}" stroke="white" stroke-width="1"/>',
        "inverted": f'<path d="M{c} {c+5}L{c+5} {c-3.8}L{c-5} {c-3.8}Z" '
                    f'fill="{colour}" stroke="white" stroke-width="1"/>',
        "inverted_open": f'<path d="M{c} {c+4.6}L{c+4.6} {c-3.5}L{c-4.6} '
                         f'{c-3.5}Z" stroke="{colour}" stroke-width="1.3" '
                         f'fill="none"/>',
        "bar": f'<rect x="{c-5.5}" y="{c-5.5}" width="11" height="11" '
               f'fill="{colour}"/>',
        "tick": f'<line x1="{c}" y1="{c-5.5}" x2="{c}" y2="{c+5.5}" '
                f'stroke="{colour}" stroke-width="2.6"/>',
        "dotted": f'<line x1="0.5" y1="{c}" x2="{size-0.5}" y2="{c}" '
                  f'stroke="{colour}" stroke-width="1.8" stroke-dasharray="2 2"/>',
        "band": f'<rect x="0" y="{c-6}" width="{size}" height="12" '
                f'fill="{colour}" opacity="0.35"/>',
    }[kind]
    return (f'<svg width="{size}" height="{size}" viewBox="0 0 {size} {size}" '
            f'style="display:block">{body}</svg>')


def legend_html(lanes: dict, gt=None, member_source: str | None = None) -> str:
    """The key. A reader should never have to guess what a marker means.

    Laid out as a legend and not as prose: **symbol first, then what it means**,
    one entry per row, keys aligned in their own column. The earlier version ran
    the symbols inline through sentences, so finding out what ``✕`` meant took
    reading a paragraph to locate it (Tony, 2026-08-15).
    """
    src = member_source or (next(iter(lanes)) if lanes else None)
    src_name = TITLES.get(src, src) if src else "—"

    def row(key: str, text: str) -> str:
        return (f'<div style="display:flex;gap:9px;align-items:flex-start;'
                f'margin:3px 0">'
                f'<div style="flex:0 0 18px;padding-top:2px">{key}</div>'
                f'<div>{text}</div></div>')

    swatches = "".join(
        f'<span style="display:inline-flex;align-items:center;gap:4px;'
        f'margin-right:11px">{_key("bar", COLORS.get(k, "#555"), 12)}'
        f'{TITLES.get(k, k)}</span>' for k in lanes)

    entries = [
        (_key("bar", COLORS.get(src, "#555")),
         "<b>Lane bar</b> — one row per detector; the bar spans a detection's "
         "<i>onset → onset + width</i>. Colour is detector identity:<br>"
         f'<div style="display:flex;flex-wrap:wrap;margin-top:3px">{swatches}</div>'),
        (_key("x", FALSE_ALARM),
         "<b>False alarm</b> — a detection near <b>no</b> planted event."),
        (_key("circle", FALSE_ALARM),
         "<b>Duplicate</b> — it lands on a real event another detection already "
         "claimed, and matching is one-to-one, so it is left over. "
         "Fragmentation, not hallucination."),
        (_key("triangle", FOUND),
         "<b>Planted event, recovered</b> by at least one detector."),
        (_key("inverted", MISSED),
         "<b>Planted event, missed</b> by all of them."),
        (_key("inverted_open", "#5a5a5a"),
         "<b>Distractor</b> — a correlated burst that is real coincidence but "
         "<b>not</b> a coordinated event."),
        (_key("tick", RASTER_HIT),
         f"<b>Raster onset, claimed</b> — it falls inside a window claimed by "
         f"<b>{src_name}</b>. One raster row per ROI, quietest at the bottom."),
        (_key("tick", "#9a9a9a"),
         "<b>Raster onset, unclaimed</b> — outside every window that detector "
         "reported."),
        (_key("dotted", "#333"),
         "<b>Threshold</b> — a detector's own cut on its own trace (four of the "
         "six expose one)."),
        (_key("band", PROBE_BAND),
         "<b>Dense-but-random block</b> — elevated firing rate and <b>no planted "
         "events</b>, so every detection inside it is a false alarm by "
         "construction."),
    ]
    body = "".join(row(k, t) for k, t in entries)
    return f"""
<div style="font:13px/1.5 system-ui,sans-serif;color:#222;max-width:1000px">
  <div style="font-weight:700;margin-bottom:5px">How to read this</div>
  {body}
</div>"""


def score_table(gt, lanes: dict, *, tol_sec: float = 1.5) -> str:
    """Plain-text scoreboard — the numbers behind the picture, in a form that
    can travel into a commit message or a log where a figure cannot.

    Scored the same way :mod:`bugarach.bench` scores: **spans, not points**, and
    the promiscuity probe kept out of precision. Both matter here or the table
    contradicts the bench it sits beside. Measured while wiring this up: scoring
    SCE's 10 s bin edges as points read 0.20 recall against the bench's 0.73–0.87
    on the same recording, and folding the probe into precision took it to 0.07.
    A caption that disagrees with the measurement is worse than no caption.
    """
    rows = ["detector      recall  prec    F1   FA  probe  by participation",
            "-" * 76]
    for key, ev in lanes.items():
        onsets, widths = ev[0], ev[1]
        s = score_detections(gt, onsets, widths=widths, tol_sec=tol_sec)
        scored = s.n_detected - s.hot_fa          # probe firings are their own number
        prec = s.n_hit / scored if scored else float("nan")
        f1 = (2 * s.recall * prec / (s.recall + prec)
              if np.isfinite(s.recall) and np.isfinite(prec) and (s.recall + prec)
              else float("nan"))
        by = " ".join(f"{int(f * 100)}%:{s.recall_at(f):.2f}"
                      for f in sorted(s.by_frac, reverse=True))
        rows.append(f"{TITLES.get(key, key):<13s} {s.recall:5.2f}  {prec:5.2f}  "
                    f"{f1:5.2f} {s.n_fa - s.hot_fa:4d}  {s.hot_fa:4d}   {by}")
    return "\n".join(rows)
