"""bugarach viewer — Panel/HoloViews port of explore_sce's browsing surface.

One group per stream (streams are GENERIC: whatever names the slice carries,
one or many — FAST/SLOW is just this project's convention): an event raster
on top, one statistic-trace row per enabled detector below, all x-linked.
Detector parameters live in the sidebar; Recompute reruns the enabled
detectors on the current slice. Detected events shade their spans on the
signal rows.

v0 scope notes: parameters apply to ALL streams (the detector APIs accept
per-stream maps; per-stream widget sets are a later refinement), and
recompute is synchronous — LoCo/CoactDetect surrogate nulls can take seconds
on long recordings.
"""

from __future__ import annotations

from pathlib import Path

import holoviews as hv
import numpy as np
import panel as pn

from bugarach.detectors import (
    cicada_detect,
    coact_detect,
    loco_detect,
    rate_detect,
    recording_extent,
    sce_detect,
    stream_trains,
    sync_detect,
)
from bugarach.io import load_events_csv
from bugarach.store import Slice, load_slice

hv.extension("bokeh")
pn.extension()


def _time_axis_hook(plot, element):
    """Minutes-friendly time axis: ticks at 1/2/5/10/15/30 x 60^k seconds
    (…30s, 1m, 2m, 5m…), labels as 45s / 2m / 2m30s. Fresh bokeh models per
    plot — they cannot be shared across documents."""
    from bokeh.models import AdaptiveTicker, CustomJSTickFormatter

    xaxis = plot.handles.get("xaxis")
    if xaxis is None:
        return
    xaxis.ticker = AdaptiveTicker(base=60,
                                  mantissas=[1, 2, 5, 10, 15, 30],
                                  min_interval=1)
    xaxis.formatter = CustomJSTickFormatter(code="""
        const s = tick;
        const sign = s < 0 ? '-' : '';
        const a = Math.abs(s);
        if (a < 60) return sign + a + 's';
        const m = Math.floor(a / 60);
        const r = Math.round(a - m * 60);
        return r ? sign + m + 'm' + String(r).padStart(2, '0') + 's'
                 : sign + m + 'm';
    """)

# explore_sce-recognizable detector palette
COLORS = {
    "rate":   "#1f77b4",
    "sce":    "#2ca02c",
    "cicada": "#9467bd",
    "sync":   "#d62728",
    "coact":  "#e69d00",
    "loco":   "#8c564b",
}
TITLES = {
    "rate": "rate+context", "sce": "binned SCE", "cicada": "CICADA",
    "sync": "SPIKE-synch", "coact": "CoactDetect", "loco": "LoCo",
}
# short row labels — the full titles overflow the slim signal rows
SHORT = {"rate": "rate", "sce": "SCE", "cicada": "CIC",
         "sync": "sync", "coact": "coact", "loco": "LoCo"}
DEFAULT_ON = ["rate", "coact", "loco"]

# widget spec: (param, label, default, (lo, hi), step)
PARAM_SPECS = {
    "rate": [
        ("grid_dt", "grid dt (s) — set to the acquisition sampling interval",
         0.1, (0.001, 1.0), 0.001),
        ("excess_threshold_hz", "excess thr (Hz)", 5.0, (0.0, 30.0), 0.5),
        ("merge_gap_s", "merge gap (s)", 3.0, (0.0, 10.0), 0.5),
        ("rate_win", "rate win (s)", 1.0, (0.1, 10.0), 0.1),
        ("context_win", "context win (s)", 60.0, (5.0, 300.0), 5.0),
    ],
    "sce": [
        ("bin_width_sec", "bin (s)", 10.0, (0.5, 30.0), 0.5),
        ("threshold_pctile", "pctile", 99.0, (50.0, 100.0), 0.5),
        ("n_surrogates", "surrogates", 200, (20, 1000), 10),
        ("min_rois", "min ROIs", 3, (2, 15), 1),
    ],
    "cicada": [
        ("n_synchronous_frames", "sync frames", 2, (1, 10), 1),
        ("active_duration_sec", "fixed dur (s)", 1.0, (0.1, 5.0), 0.1),
        ("sce_percentile", "pctile", 99.9, (50.0, 100.0), 0.1),
        ("n_surrogates", "surrogates", 50, (10, 500), 10),
        ("sce_min_distance_frames", "min dist (frames)", 4, (1, 50), 1),
        ("imaging_rate_hz", "imaging rate (Hz)", 10.0, (1.0, 100.0), 1.0),
    ],
    "sync": [
        ("tau_max", "tau cap (s)", 0.25, (0.05, 3.0), 0.05),
        ("max_gap", "max gap (s)", 0.5, (0.0, 5.0), 0.1),
        ("C_threshold", "C thr", 0.1, (0.0, 1.0), 0.01),
        ("C_min", "C min", 0.1, (0.0, 1.0), 0.01),
        ("min_n", "min N", 3, (1, 15), 1),
    ],
    "coact": [
        ("int_win_sec", "int win (s)", 1.0, (0.05, 3.0), 0.05),
        ("context_win_sec", "context (s)", 60.0, (10.0, 300.0), 5.0),
        ("min_rois", "min ROIs", 3, (2, 15), 1),
        ("n_surrogates", "surrogates", 100, (20, 500), 10),
        ("alpha", "alpha", 1e-3, (1e-6, 0.1), 1e-4),
    ],
    "loco": [
        ("bin_width_sec", "bin (s)", 1.0, (0.5, 10.0), 0.5),
        ("context_win_sec", "context (s)", 120.0, (10.0, 300.0), 10.0),
        ("threshold_pctile", "pctile", 99.9, (50.0, 100.0), 0.1),
        ("min_rois", "min ROIs", 3, (2, 15), 1),
        ("n_surrogates", "surrogates", 100, (20, 500), 10),
        ("thr_step_sec", "thr step (s)", 15.0, (5.0, 60.0), 5.0),
        ("merge_gap_sec", "merge gap (s)", 2.0, (0.0, 10.0), 0.5),
    ],
}
RNG_SEED = 20260706


def _compute(det: str, s: Slice, ext, params: dict):
    """Run one detector on all streams -> {stream: (t, y, events, extra)}.

    events = (onsets, widths); extra = dict with optional 'ref' trace and
    'threshold' (scalar or per-bin envelope) for the signal row."""
    out = {}
    if det == "rate":
        for name, st in s.streams.items():
            r = rate_detect(stream_trains(st, ext), ext, **params)
            out[name] = (r.signal.t, r.signal.y, (r.locs, r.widths),
                         {"ref": r.signal.ref})
    elif det == "coact":
        for name, st in s.streams.items():
            r = coact_detect(st.t50rise, ext, rng_seed=RNG_SEED, **params)
            out[name] = (r.ctr, r.obs, (r.onset_sec, r.width_sec),
                         {"ref": r.nullmean_prof})
    elif det == "loco":
        r = loco_detect(s, rng_seed=RNG_SEED, **params)
        for name, res in r.streams.items():
            out[name] = (res.signal.t, res.signal.y,
                         (res.onset_sec, res.width_sec),
                         {"threshold": res.signal.threshold})
    elif det == "sce":
        r = sce_detect(s, rng_seed=RNG_SEED, emit_signal=True, **params)
        for name, res in r.streams.items():
            thr = np.full(res.signal.t.size, np.nan)
            for seg in res.signal.thresholds:
                m = (res.signal.t >= seg["win_start"]) & \
                    (res.signal.t <= seg["win_end"])
                thr[m] = seg["value"]
            out[name] = (res.signal.t, res.signal.y,
                         (res.onset_sec, res.width_sec), {"threshold": thr})
    elif det == "cicada":
        r = cicada_detect(s, rng_seed=RNG_SEED, emit_signal=True,
                          onset_field="t50rise", **params)
        for name, res in r.streams.items():
            thr = np.full(res.signal.t.size, np.nan)
            for seg in res.signal.thresholds:
                m = (res.signal.t >= seg["win_start"]) & \
                    (res.signal.t <= seg["win_end"])
                thr[m] = seg["value"]
            out[name] = (res.signal.t, res.signal.y,
                         (res.onset_sec, res.width_sec), {"threshold": thr})
    elif det == "sync":
        for name, st in s.streams.items():
            r = sync_detect(st.t50rise, ext, **params)
            out[name] = (r.Cx, r.Cy, (r.locs, r.widths),
                         {"threshold": params.get("C_threshold", 0.1)})
    return out


def _raster(stream, name: str, ext) -> hv.Scatter:
    ts, ys = [], []
    for i, v in enumerate(stream.t50rise):
        v = np.asarray(v, dtype=float)
        v = v[np.isfinite(v)]
        ts.append(v)
        ys.append(np.full(v.size, i))
    t = np.concatenate(ts) if ts else np.empty(0)
    y = np.concatenate(ys) if ys else np.empty(0)
    # no title — vertical space is precious; the y-label carries identity.
    # wheel zoom stays in the toolbar but NOT active, so the mouse wheel
    # scrolls the page; drag pans, toolbar toggles zoom when wanted
    return hv.Scatter((t, y), kdims=["t"], vdims=["roi"]).opts(
        marker="dash", angle=90, size=5, color="black", alpha=0.7,
        width=950, height=150, xlim=ext, title="",
        ylabel=f"{name} · {stream.n_rois} ROI",
        fontsize={"ylabel": "10pt"},
        tools=["xwheel_zoom", "xpan", "reset", "hover"],
        active_tools=["xpan"], default_tools=["reset"],
        hooks=[_time_axis_hook],
    )


def _signal_row(det, t, y, events, extra, ext) -> hv.Overlay:
    color = COLORS[det]
    onsets, widths = events
    # curve FIRST: the overlay inherits its 't' dimension, keeping every row
    # on the same axis as the rasters (Rectangles would impose 'x0').
    # the value dimension is UNIQUE per detector so y-ranges do NOT link
    # across rows (a 0-1 synchrony trace must not share the ROI-count scale)
    ydim = hv.Dimension(f"{det}_y", label=TITLES[det])
    items = [hv.Curve((t, y), kdims=["t"], vdims=[ydim]).opts(
        color=color, line_width=1)]
    if onsets is not None and np.size(onsets):
        w = np.where(np.isfinite(widths) & (widths > 0), widths, 0.5)
        finite_y = y[np.isfinite(y)]
        top = float(finite_y.max()) if finite_y.size else 1.0
        rects = [(o, 0.0, o + ww, top) for o, ww in zip(onsets, w)]
        items.append(hv.Rectangles(rects).opts(
            color=color, alpha=0.25, line_alpha=0))
    ref = extra.get("ref")
    if ref is not None and np.size(ref) == np.size(t):
        items.append(hv.Curve((t, ref), kdims=["t"], vdims=[ydim]).opts(
            color="gray", line_width=1, line_dash="dashed"))
    thr = extra.get("threshold")
    if thr is not None:
        if np.isscalar(thr):
            items.append(hv.HLine(float(thr)).opts(
                color=color, line_dash="dotted", line_width=1))
        elif np.size(thr) == np.size(t):
            items.append(hv.Curve((t, thr), kdims=["t"], vdims=[ydim]).opts(
                color="black", line_width=1, line_dash="dotted"))
    n_ev = int(np.size(onsets)) if onsets is not None else 0
    # identity + event count live on the y-label; titles are redundant rows
    return hv.Overlay(items).opts(
        width=950, height=75, xlim=ext, xlabel="", title="",
        ylabel=f"{SHORT[det]} ({n_ev})", yticks=2,
        fontsize={"ylabel": "9pt"},
        show_legend=False, hooks=[_time_axis_hook],
        tools=["xwheel_zoom", "xpan", "reset"],
        active_tools=["xpan"], default_tools=["reset"],
    )


def build_viewer(slices: dict[str, Slice], *, title: str = "bugarach"):
    """Assemble the viewer for a set of named slices. Returns a Panel
    template servable with `panel serve` / pn.serve()."""
    if not slices:
        raise ValueError("no slices to view")

    slice_sel = pn.widgets.Select(name="slice", options=list(slices))
    # Toggle buttons, not checkboxes — a full-size click target
    det_checks = {d: pn.widgets.Toggle(name=TITLES[d], value=d in DEFAULT_ON,
                                       button_type="primary",
                                       button_style="outline",
                                       sizing_mode="stretch_width")
                  for d in PARAM_SPECS}
    widgets: dict[str, dict[str, pn.widgets.Widget]] = {}
    accordion_items = []
    for det, specs in PARAM_SPECS.items():
        ws = {}
        for pname, label, default, (lo, hi), step in specs:
            if isinstance(default, int):
                w = pn.widgets.IntInput(name=label, value=default,
                                        start=int(lo), end=int(hi),
                                        step=int(step))
            else:
                w = pn.widgets.FloatInput(name=label, value=default,
                                          start=lo, end=hi, step=step)
            ws[pname] = w
        widgets[det] = ws
        accordion_items.append((TITLES[det], pn.Column(*ws.values())))
    # enable toggles live OUTSIDE the accordion, always visible, big targets
    toggle_grid = pn.GridBox(*det_checks.values(), ncols=2)

    go = pn.widgets.Button(name="Recompute", button_type="primary")
    status = pn.pane.Markdown("")
    main = pn.Column(sizing_mode="stretch_width")

    def render(_=None):
        s = slices[slice_sel.value]
        ext = recording_extent(s)
        enabled = [d for d, c in det_checks.items() if c.value]
        status.object = f"computing {', '.join(enabled) or 'nothing'} …"
        results = {}
        try:
            for det in enabled:
                params = {p: w.value for p, w in widgets[det].items()}
                results[det] = _compute(det, s, ext, params)
        except Exception as e:  # surface, don't crash the app
            status.object = f"**error:** {e}"
            return
        blocks = []
        for name, stream in s.streams.items():
            rows = [_raster(stream, name, ext)]
            for det in enabled:
                if name in results[det]:
                    t, y, events, extra = results[det][name]
                    if np.size(t):
                        rows.append(_signal_row(det, t, y, events, extra, ext))
            # one x-axis per group: only the bottom row shows it (zoom/pan
            # stays linked through the shared 't' dimension). The bottom row
            # gets extra height so its PLOT area matches the others — the
            # axis+label live in the extra 45px, not carved out of the plot
            last = len(rows) - 1
            styled = []
            for i, r in enumerate(rows):
                if i < last:
                    styled.append(r.opts(xaxis=None))
                else:
                    base_h = 150 if i == 0 else 75   # raster may be last
                    styled.append(r.opts(height=base_h + 45))
            layout = hv.Layout(styled).cols(1).opts(shared_axes=True)
            blocks.append(pn.pane.HoloViews(layout))
        main.objects = blocks
        status.object = f"`{s.slice_id}` — {len(s.streams)} stream(s)"

    go.on_click(render)
    slice_sel.param.watch(render, "value")
    render()

    sidebar = pn.Column(
        slice_sel, go, status, toggle_grid,
        pn.pane.Markdown("**parameters**", margin=(6, 0, 0, 5)),
        pn.Accordion(*accordion_items, active=[]),
        width=340,
    )
    return pn.template.FastListTemplate(
        title=title, sidebar=[sidebar], main=[main],
        accent_base_color="#4f6d7a", header_background="#4f6d7a",
    )


def load_any(path) -> tuple[str, Slice]:
    """Load a slice from a store .mat or an events CSV."""
    path = Path(path)
    s = load_events_csv(path) if path.suffix.lower() == ".csv" \
        else load_slice(path)
    return s.slice_id, s
