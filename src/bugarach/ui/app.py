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

Three things the sidebar is not free to decide for itself:

* **The starting parameters are the calibrated ones**, read out of
  :data:`bugarach.bench.OPERATING_POINTS` at import rather than retyped here.
  They were retyped here once, and two of them fell behind: CICADA opened at
  the 99.9th percentile the project retired for firing 7.3 false events an hour
  (FOUNDATIONS §9), and CoactDetect at ``alpha=1e-3``/``int_win_sec=1.0``,
  where the bench measures F1 0.72 against 1.00 at the calibrated pair. A
  duplicated constant is how those drifted, so there is no longer a second
  copy: :data:`CALIBRATED` marks a widget whose default comes from the bench,
  and :func:`_resolve_specs` refuses at import if a benched parameter is
  written out as a literal here instead.
* **The sampling interval comes from the recording**, never from this file.
  FOUNDATIONS §6: dt is a property of the recording, nothing downstream can
  recover it, and there is no default. An export folder states it in
  ``slices.csv``; the viewer reads it, shows it, derives rate+context's
  ``grid_dt`` and CICADA's ``imaging_rate_hz`` from it, and **refuses to run a
  detector on a recording that does not carry one** rather than quietly
  assuming this lab's 10 Hz. A person who knows the interval can type it in —
  which is what ``bugarach check`` already promises ("no frame interval —
  bugarach will ask for it").
* **What is on screen can be taken away.** The Save button writes the project's
  own output contract through :mod:`bugarach.emit` — no second serializer —
  and never a private viewer dialect.
"""

from __future__ import annotations

import io
import zipfile
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import NamedTuple

import holoviews as hv
import numpy as np
import panel as pn

from bugarach import emit
from bugarach.bench import OPERATING_POINTS
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
    """Own the time axis: minutes-friendly ticks, and zoom that follows it.

    Ticks at 1/2/5/10/15/30 x 60^k seconds (…30s, 1m, 2m, 5m…), labelled
    45s / 2m / 2m30s. Fresh bokeh models per plot — they cannot be shared
    across documents.

    **Zoom is constrained to x here rather than at the call site.** Every panel
    declares ``xwheel_zoom``/``xpan``, and it is not enough: HoloViews adds its
    own toolbar back when the panels are merged into a layout, and the built
    figure shipped eight unconstrained ``BoxZoomTool``s with no ``dimensions``
    set at all. Zooming y on these plots is meaningless — the axis is an ROI
    index or a detector name — and it silently desynchronises rows that are
    supposed to be read against each other. Doing it in the hook means a panel
    added later cannot forget it, since every panel already needs this hook for
    its ticks.
    """
    from bokeh.models import (AdaptiveTicker, BoxZoomTool, CustomJSTickFormatter,
                              PanTool, WheelZoomTool)

    toolbar = getattr(plot.state, "toolbar", None)
    wheel = None
    for tool in getattr(toolbar, "tools", ()) or ():
        if isinstance(tool, (BoxZoomTool, WheelZoomTool, PanTool)):
            tool.dimensions = "width"
        if isinstance(tool, WheelZoomTool):
            wheel = tool
    # Constraining the wheel is not enough to make it work: bokeh leaves
    # active_scroll on "auto" and nothing claims the wheel, so scrolling over
    # the plot did nothing at all and zooming meant finding the box-zoom button
    # first. Hand the wheel to the x-constrained zoom explicitly.
    if wheel is not None and toolbar is not None:
        toolbar.active_scroll = wheel

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


class _Calibrated:
    """Marker for "this widget opens at the calibrated operating point"."""

    def __repr__(self) -> str:              # so a traceback names it usefully
        return "CALIBRATED"


#: Write this instead of a number, and the widget opens at whatever
#: ``bench.OPERATING_POINTS[detector].params[name]`` says. There is deliberately
#: no way to write the number here as well: see :func:`_resolve_specs`.
CALIBRATED = _Calibrated()

#: Parameters the RECORDING decides, not the person and not the bench. They get
#: no widget at all — a settable box next to a value read from the data is an
#: invitation to overrule the recording about its own sampling rate. The single
#: frame-interval input in the sidebar is where dt is stated; these are derived
#: from it at compute time by :func:`_dt_derived`.
DT_DERIVED = {"rate": ("grid_dt",), "cicada": ("imaging_rate_hz",)}

# widget spec: (param, label, default, (lo, hi), step). `default` is either a
# literal — for a knob the bench does not declare, which therefore runs at the
# detector's own signature default — or CALIBRATED.
_SPECS = {
    "rate": [
        ("excess_threshold_hz", "excess thr (Hz)", CALIBRATED, (0.0, 30.0), 0.5),
        ("merge_gap_s", "merge gap (s)", 3.0, (0.0, 10.0), 0.5),
        ("rate_win", "rate win (s)", CALIBRATED, (0.1, 10.0), 0.1),
        ("context_win", "context win (s)", CALIBRATED, (5.0, 300.0), 5.0),
    ],
    "sce": [
        ("bin_width_sec", "bin (s)", CALIBRATED, (0.5, 30.0), 0.5),
        ("threshold_pctile", "pctile", CALIBRATED, (50.0, 100.0), 0.5),
        ("n_surrogates", "surrogates", CALIBRATED, (20, 1000), 10),
        ("min_rois", "min ROIs", 3, (2, 15), 1),
    ],
    "cicada": [
        # not benched: the bench runs CICADA at the signature's 1 frame. 2 is the
        # viewer's own choice and the one divergence left in this table that the
        # import-time check cannot see, because there is no bench value to
        # compare against. Named here so it is a decision rather than a leftover.
        ("n_synchronous_frames", "sync frames", 2, (1, 10), 1),
        ("active_duration_sec", "fixed dur (s)", CALIBRATED, (0.1, 5.0), 0.1),
        # step is 1e-3, not 0.1: at the calibrated 99.999 a tenth-of-a-percent
        # spinner cannot reach a neighbouring value, so the arrows are useless
        # exactly where somebody would want to nudge it.
        ("sce_percentile", "pctile", CALIBRATED, (50.0, 100.0), 0.001),
        ("n_surrogates", "surrogates", CALIBRATED, (10, 500), 10),
        ("sce_min_distance_frames", "min dist (frames)", 4, (1, 50), 1),
    ],
    "sync": [
        ("tau_max", "tau cap (s)", CALIBRATED, (0.05, 3.0), 0.05),
        ("max_gap", "max gap (s)", CALIBRATED, (0.0, 5.0), 0.1),
        ("C_threshold", "C thr", CALIBRATED, (0.0, 1.0), 0.01),
        ("C_min", "C min", CALIBRATED, (0.0, 1.0), 0.01),
        ("min_n", "min N", 3, (1, 15), 1),
    ],
    "coact": [
        ("int_win_sec", "int win (s)", CALIBRATED, (0.05, 3.0), 0.05),
        ("context_win_sec", "context (s)", CALIBRATED, (10.0, 300.0), 5.0),
        ("min_rois", "min ROIs", 3, (2, 15), 1),
        ("n_surrogates", "surrogates", CALIBRATED, (20, 500), 10),
        # 1e-5, not 1e-4: the calibrated alpha IS 1e-4, so a step of 1e-4 makes
        # the first click land on zero.
        ("alpha", "alpha", CALIBRATED, (1e-6, 0.1), 1e-5),
    ],
    "loco": [
        ("bin_width_sec", "bin (s)", CALIBRATED, (0.5, 10.0), 0.5),
        ("context_win_sec", "context (s)", CALIBRATED, (10.0, 300.0), 10.0),
        ("threshold_pctile", "pctile", CALIBRATED, (50.0, 100.0), 0.1),
        ("min_rois", "min ROIs", 3, (2, 15), 1),
        ("n_surrogates", "surrogates", CALIBRATED, (20, 500), 10),
        ("thr_step_sec", "thr step (s)", CALIBRATED, (5.0, 60.0), 5.0),
        ("merge_gap_sec", "merge gap (s)", CALIBRATED, (0.0, 10.0), 0.5),
    ],
}


def _resolve_specs(specs: dict) -> dict:
    """Fill in the calibrated defaults, and refuse a second copy of one.

    Three refusals, all at import so a mistake here cannot reach a screen:

    * ``CALIBRATED`` on a parameter the bench does not declare — the widget
      would have no value at all.
    * a **literal** on a parameter the bench *does* declare — that is precisely
      the second hand-maintained copy that let CICADA and CoactDetect drift.
    * a widget for a parameter the recording decides (:data:`DT_DERIVED`).
    * a default outside its own slider bounds — a box that opens showing a
      value it will not accept back.
    """
    out = {}
    for det, rows in specs.items():
        point = OPERATING_POINTS[det].params
        derived = DT_DERIVED.get(det, ())
        resolved = []
        for pname, label, default, bounds, step in rows:
            if pname in derived:
                raise ValueError(
                    f"{det}.{pname} is derived from the recording's frame "
                    f"interval (FOUNDATIONS §6) and must not have a widget")
            if default is CALIBRATED:
                if pname not in point:
                    raise ValueError(
                        f"{det}.{pname} is marked CALIBRATED but "
                        f"bench.OPERATING_POINTS['{det}'] does not declare it — "
                        f"either add it there with its provenance, or give the "
                        f"widget its own literal default")
                default = point[pname]
            elif pname in point:
                raise ValueError(
                    f"{det}.{pname} has a literal default of {default!r} here "
                    f"AND a calibrated value of {point[pname]!r} in "
                    f"bench.OPERATING_POINTS. Two copies of one number is how "
                    f"the viewer came to ship uncalibrated settings; write "
                    f"CALIBRATED instead")
            lo, hi = bounds
            if not lo <= default <= hi:
                raise ValueError(
                    f"{det}.{pname} opens at {default!r}, outside its own "
                    f"widget range {bounds}")
            resolved.append((pname, label, default, bounds, step))
        out[det] = resolved
    return out


PARAM_SPECS = _resolve_specs(_SPECS)
RNG_SEED = 20260706

#: Column of an export folder's ``slices.csv`` that states the sampling interval.
FRAME_INTERVAL_KEY = "frame_interval_sec"


class FrameIntervalMissing(ValueError):
    """No sampling interval for this recording, so nothing may be computed.

    FOUNDATIONS §6: the interval is a property of the recording, nothing
    downstream can recover it, and there is no default. The viewer's answer is
    to show the rasters — which need no dt — and refuse the detectors.
    """


def frame_interval_sec(s: Slice) -> float | None:
    """The recording's own sampling interval in seconds, or ``None``.

    ``None`` means the recording never said — a plain event CSV, or a folder
    whose ``slices.csv`` has no row for it. A value that is present but not a
    positive number is a producer bug and raises, because silently treating it
    as absent would hide the typo that caused it.
    """
    raw = (s.meta or {}).get(FRAME_INTERVAL_KEY)
    if raw is None or str(raw).strip() == "":
        return None
    try:
        dt = float(raw)
    except (TypeError, ValueError):
        raise FrameIntervalMissing(
            f"{s.slice_id}: {FRAME_INTERVAL_KEY} is {raw!r}, which is not a "
            f"number of seconds") from None
    if not (np.isfinite(dt) and dt > 0):
        raise FrameIntervalMissing(
            f"{s.slice_id}: {FRAME_INTERVAL_KEY} is {dt!r}, which is not a "
            f"positive number of seconds")
    return dt


def _dt_derived(det: str, dt: float) -> dict:
    """The parameters this detector takes from the recording's own interval.

    CICADA states the same fact upside down — it wants a rate where the others
    want an interval — and inverting it here, once, is why there is no second
    place for the two to disagree.
    """
    if det == "rate":
        return {"grid_dt": dt}
    if det == "cicada":
        return {"imaging_rate_hz": 1.0 / dt}
    return {}


class StreamResult(NamedTuple):
    """One detector's answer for one stream: what to draw, and what to write.

    ``result`` is the detector's own per-stream result object, carried through
    untouched so :mod:`bugarach.emit` can read it. The plot arrays cannot stand
    in for it — a row of the output file needs the strength, the participant
    count and the region the detector scored in, none of which survive being
    flattened into a curve.
    """

    t: np.ndarray
    y: np.ndarray
    events: tuple
    extra: dict
    result: object


def _compute(det: str, s: Slice, ext, params: dict, *, dt: float):
    """Run one detector on all streams -> {stream: :class:`StreamResult`}.

    ``dt`` is the recording's sampling interval and is **required**: the
    parameters in :data:`DT_DERIVED` are computed from it here rather than
    taken from a widget, and a recording that does not state one is refused
    (FOUNDATIONS §6) instead of being run on an assumed 10 Hz grid.
    """
    if dt is None or not np.isfinite(dt) or dt <= 0:
        raise FrameIntervalMissing(
            f"{s.slice_id}: no sampling interval, so no detector may run. "
            f"bugarach does not assume one — add {FRAME_INTERVAL_KEY} to the "
            f"folder's slices.csv, or type the interval in the sidebar.")
    params = {**params, **_dt_derived(det, dt)}
    out = {}
    if det == "rate":
        for name, st in s.streams.items():
            r = rate_detect(stream_trains(st, ext), ext, **params)
            out[name] = StreamResult(r.signal.t, r.signal.y, (r.locs, r.widths),
                                     {"ref": r.signal.ref}, r)
    elif det == "coact":
        for name, st in s.streams.items():
            r = coact_detect(st.t50rise, ext, rng_seed=RNG_SEED, **params)
            out[name] = StreamResult(r.ctr, r.obs, (r.onset_sec, r.width_sec),
                                     {"ref": r.nullmean_prof}, r)
    elif det == "loco":
        r = loco_detect(s, rng_seed=RNG_SEED, **params)
        for name, res in r.streams.items():
            out[name] = StreamResult(res.signal.t, res.signal.y,
                                     (res.onset_sec, res.width_sec),
                                     {"threshold": res.signal.threshold}, res)
    elif det == "sce":
        r = sce_detect(s, rng_seed=RNG_SEED, emit_signal=True, **params)
        for name, res in r.streams.items():
            thr = np.full(res.signal.t.size, np.nan)
            for seg in res.signal.thresholds:
                m = (res.signal.t >= seg["win_start"]) & \
                    (res.signal.t <= seg["win_end"])
                thr[m] = seg["value"]
            out[name] = StreamResult(res.signal.t, res.signal.y,
                                     (res.onset_sec, res.width_sec),
                                     {"threshold": thr}, res)
    elif det == "cicada":
        r = cicada_detect(s, rng_seed=RNG_SEED, emit_signal=True,
                          onset_field="t50rise", **params)
        for name, res in r.streams.items():
            thr = np.full(res.signal.t.size, np.nan)
            for seg in res.signal.thresholds:
                m = (res.signal.t >= seg["win_start"]) & \
                    (res.signal.t <= seg["win_end"])
                thr[m] = seg["value"]
            out[name] = StreamResult(res.signal.t, res.signal.y,
                                     (res.onset_sec, res.width_sec),
                                     {"threshold": thr}, res)
    elif det == "sync":
        for name, st in s.streams.items():
            r = sync_detect(st.t50rise, ext, **params)
            out[name] = StreamResult(r.Cx, r.Cy, (r.locs, r.widths),
                                     {"threshold": params.get("C_threshold",
                                                              0.1)}, r)
    return out


# --------------------------------------------------------------------------
# Taking the answer away: the screen, written as the project's output contract.
# Every byte below comes out of `bugarach.emit`. There is no serializer here,
# on purpose — a second one is how a column comes to mean two things.
# --------------------------------------------------------------------------

#: What LoCo, SCE and CICADA report for an event whose onset fell inside no
#: declared window. It is a sentinel and not a name anybody wrote, so it must not
#: reach ``region_label`` — a reader would take a column saying ``none`` for a
#: period actually called that, which is the plausible-wrong-answer the output
#: contract exists to refuse. It becomes ``NA``, which is what absence is spelled.
NO_REGION = "none"


def _region_indices(s: Slice) -> dict[str, int]:
    """label -> the producer's own ``region_idx``, as the folder stated it.

    ``Region.slot`` is where :func:`bugarach.io.load_folder` parks the
    ``region_idx`` column, and the label is what the detectors report per event.
    This is the join between the two, and it is needed because the three
    slice-level detectors return a region **name** per event and never an index,
    while ``detections.csv`` wants both. A slot that is not an integer, or a
    region with no name, simply does not join — the row keeps its label and
    reports ``NA`` for the index rather than inventing one.
    """
    out: dict[str, int] = {}
    for r in s.regions:
        if r.name is None or r.slot is None:
            continue
        try:
            out.setdefault(str(r.name), int(r.slot))
        except (TypeError, ValueError):
            continue
    return out


def detections_for(s: Slice, results: dict) -> list:
    """Every event on screen, as :class:`bugarach.emit.DetectedEvent` rows.

    ``results`` is ``{detector: {stream: StreamResult}}`` — what
    :func:`_compute` returned for each enabled detector.

    Two pieces of glue that a one-liner does not have:

    * **the identity columns.** ``events_from`` carries them only if handed
      them, and ``Slice.meta`` is exactly the recording's ``slices.csv`` row, so
      that is what it gets. ``emit`` refuses to let a carried column overwrite a
      computed one, so a producer with a ``detector`` column stays harmless.
    * **the region index.** ``events_from`` takes one ``region_idx`` for the
      whole call, but the slice-level detectors attribute each event to a window
      by name, so the index is filled per event through
      :func:`_region_indices`. The three that run over the whole recording get
      ``NA`` for both: the viewer runs them once over the full extent rather
      than once per window, and naming the window an event's onset happens to
      land in would report a per-window analysis that did not happen.

    The :data:`NO_REGION` sentinel is undone here as well, unless the recording
    really does declare a window by that name.
    """
    by_label = _region_indices(s)
    identity = dict(s.meta or {})
    rows = []
    for det, per_stream in results.items():
        for stream, sr in per_stream.items():
            events = emit.events_from(sr.result, detector=det,
                                      slice_id=s.slice_id, stream=stream,
                                      identity=identity)
            for e in events:
                label = e.region_label
                if label is None:
                    continue
                if str(label) == NO_REGION and NO_REGION not in by_label:
                    e.region_label = None
                    continue
                e.region_idx = by_label.get(str(label))
            rows.extend(events)
    return rows


def detection_bundle(s: Slice, results: dict, settings: dict, *,
                     dt: float | None) -> io.BytesIO:
    """The three output files, zipped, ready to hand to a browser.

    ``detections.csv`` and ``detector_settings.csv`` are the contract in
    ``docs/export_folder_spec.md``; ``run.json`` is the provenance a table of
    times cannot carry — which recording was looked at, and at what sampling
    interval. They are written by :mod:`bugarach.emit` into a scratch directory
    and zipped verbatim, so what a person downloads is byte-for-byte what the
    rest of the project writes rather than a lookalike assembled here.

    A recording with no detections still gets all three files. An empty result
    is a finding; an absent file is a bug, and they must not look alike.
    """
    buf = io.BytesIO()
    with TemporaryDirectory() as tmp:
        d = Path(tmp)
        emit.write_detections(detections_for(s, results), d / "detections.csv")
        emit.write_detector_settings(settings, d / "detector_settings.csv")
        emit.write_run(
            d / "run.json",
            slices=[s.slice_id],
            frame_interval_sec={s.slice_id: dt},
            code_version=_code_version(),
            extra={"produced_by": "bugarach viewer",
                   "detectors": sorted({det for det, _ in settings})})
        with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
            for name in ("detections.csv", "detector_settings.csv", "run.json"):
                z.write(d / name, arcname=name)
    buf.seek(0)
    return buf


def _code_version() -> str | None:
    from importlib.metadata import PackageNotFoundError, version

    try:
        return version("bugarach")
    except PackageNotFoundError:      # running from a source tree, uninstalled
        return None


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


def _signal_row(det, t, y, events, extra, ext, label: str | None = None) -> hv.Overlay:
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
    # identity + event count live on the y-label; titles are redundant rows.
    # The viewer's 75px rows only fit the abbreviation; a caller with taller
    # rows passes `label` and gets the real name — "CIC" is not CICADA to
    # anyone who has met the other CIC (Tony, 2026-08-15).
    return hv.Overlay(items).opts(
        width=950, height=75, xlim=ext, xlabel="", title="",
        ylabel=f"{label or SHORT[det]} ({n_ev})", yticks=2,
        fontsize={"ylabel": "9pt"},
        show_legend=False, hooks=[_time_axis_hook],
        tools=["xwheel_zoom", "xpan", "reset"],
        active_tools=["xpan"], default_tools=["reset"],
    )


def build_viewer(slices: dict[str, Slice], *, title: str = "bugarach",
                 raster_only: bool = False):
    """Assemble the viewer for a set of named slices. Returns a Panel
    template servable with `panel serve` / pn.serve().

    ``raster_only`` shows the recordings and nothing else — no detectors, no
    parameters, no recompute. It is the honest first look at a folder you were
    just handed: every detector on this page is a claim about the data, and
    before making one it is worth seeing what arrived. It also loads instantly
    on a deck this size, because nothing is computed."""
    if not slices:
        raise ValueError("no slices to view")

    if raster_only:
        return _build_raster_viewer(slices, title=title)

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

    # The sampling interval, stated once and used everywhere. It is an INPUT
    # rather than a read-out because §6 puts the interval in the hands of the
    # person who knows it: a folder that states it fills this in, and a bare
    # event CSV — which cannot state it — leaves it empty until somebody says.
    dt_input = pn.widgets.FloatInput(
        name="frame interval (s)", value=None,
        start=1e-6, end=10.0, step=0.001, format="0.00000")
    dt_note = pn.pane.Markdown("", margin=(-10, 0, 4, 10))
    # What the download will contain, and whether there is anything to download.
    save = pn.widgets.FileDownload(
        label="Save detections", filename="detections.zip",
        button_type="primary", disabled=True, auto=True,
        embed=False, callback=lambda: _bundle())
    shown: dict = {}

    def _bundle() -> io.BytesIO:
        """Whatever is on screen right now, as the project's output files."""
        return detection_bundle(shown["slice"], shown["results"],
                                shown["settings"], dt=shown["dt"])

    def _sync_dt(_=None):
        """Reset the interval from the recording each time one is chosen.

        Deliberately not sticky: carrying a hand-typed interval onto the next
        recording is how one folder's 20 Hz silently rescales another's.
        """
        s = slices[slice_sel.value]
        try:
            dt = frame_interval_sec(s)
        except FrameIntervalMissing as e:
            dt_input.value = None
            dt_note.object = f"⚠ {e}"
            return
        dt_input.value = dt
        dt_note.object = (
            f"from the recording (`{FRAME_INTERVAL_KEY}` = {dt:g})"
            if dt is not None else
            "**this recording does not state one** — detectors stay off until "
            "you type it. bugarach never assumes an interval (FOUNDATIONS §6).")

    def render(_=None):
        s = slices[slice_sel.value]
        ext = recording_extent(s)
        dt = dt_input.value
        enabled = [d for d, c in det_checks.items() if c.value]
        status.object = f"computing {', '.join(enabled) or 'nothing'} …"
        results = {}
        settings = {}
        try:
            for det in enabled:
                params = {p: w.value for p, w in widgets[det].items()}
                results[det] = _compute(det, s, ext, params, dt=dt)
                for name in results[det]:
                    settings[(det, name)] = {**params, **_dt_derived(det, dt)}
        except Exception as e:  # surface, don't crash the app
            # the id is in the heading, so strip the copy the exception
            # carries — said twice it reads like two different failures
            why = str(e).removeprefix(f"{s.slice_id}: ")
            status.object = f"**cannot analyse `{s.slice_id}`:** {why}"
            save.disabled = True
            main.objects = _raster_blocks(s, ext)
            return
        shown.update(slice=s, results=results, settings=settings, dt=dt)
        n_events = sum(int(np.size(v.events[0])) for r in results.values()
                       for v in r.values())
        save.filename = f"{s.slice_id}_detections.zip"
        save.disabled = not results
        blocks = []
        for name, stream in s.streams.items():
            rows = [_raster(stream, name, ext)]
            for det in enabled:
                if name in results[det]:
                    t, y, events, extra, _ = results[det][name]
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
        # The interval is named in the same breath as the result, because it is
        # not a setting of the viewer — it scaled the numbers above it.
        status.object = (
            f"`{s.slice_id}` — {len(s.streams)} stream(s) · "
            f"dt {dt:g} s ({1.0 / dt:g} Hz) · {n_events} event(s)")

    def _raster_blocks(s, ext):
        """The recordings with nothing computed over them.

        What a refusal leaves on screen: rasters need no sampling interval, so
        declining to analyse a recording is not a reason to stop showing it.
        """
        rows = [_raster(stream, name, ext)
                for name, stream in s.streams.items()]
        last_i = len(rows) - 1
        styled = [r.opts(xaxis=None) if i < last_i else r.opts(height=195)
                  for i, r in enumerate(rows)]
        return [pn.pane.HoloViews(hv.Layout(styled).cols(1)
                                  .opts(shared_axes=True))]

    def _on_slice(_=None):
        _sync_dt()
        render()

    go.on_click(render)
    slice_sel.param.watch(_on_slice, "value")
    _sync_dt()
    render()

    sidebar = pn.Column(
        slice_sel, dt_input, dt_note, go, status, save, toggle_grid,
        pn.pane.Markdown("**parameters**", margin=(6, 0, 0, 5)),
        pn.Accordion(*accordion_items, active=[]),
        width=340,
    )
    return pn.template.FastListTemplate(
        title=title, sidebar=[sidebar], main=[main],
        accent_base_color="#4f6d7a", header_background="#4f6d7a",
    )


def _build_raster_viewer(slices: dict[str, Slice], *, title: str):
    """The recordings, and nothing that interprets them."""
    slice_sel = pn.widgets.Select(name="recording", options=list(slices))
    status = pn.pane.Markdown("")
    main = pn.Column(sizing_mode="stretch_width")

    def render(_=None):
        s = slices[slice_sel.value]
        ext = recording_extent(s)
        rows = [_raster(stream, name, ext)
                for name, stream in s.streams.items()]
        last = len(rows) - 1
        styled = [r.opts(xaxis=None) if i < last else r.opts(height=195)
                  for i, r in enumerate(rows)]
        main.objects = [pn.pane.HoloViews(
            hv.Layout(styled).cols(1).opts(shared_axes=True))]

        # what the reader needs to judge the picture: how long, how many ROIs,
        # and which periods — a raster with no windows named is a wall of dots
        mins = (ext[1] - ext[0]) / 60.0
        n_events = sum(st.n_events for st in s.streams.values())
        quiet = sum(1 for i in range(next(iter(s.streams.values())).n_rois)
                    if all(st.locs[i].size == 0 for st in s.streams.values()))
        try:
            dt = frame_interval_sec(s)
            dt_bit = (f"dt {dt:g} s ({1.0 / dt:g} Hz)" if dt is not None
                      else "**no frame interval stated** — not analysable")
        except FrameIntervalMissing as e:
            dt_bit = f"⚠ {e}"
        bits = [f"`{s.slice_id}`",
                f"{next(iter(s.streams.values())).n_rois} ROI"
                + (f" ({quiet} with no events)" if quiet else ""),
                f"{n_events} events",
                f"{mins:.1f} min",
                # named here too: raster-only is the first look at a folder
                # somebody just sent, and whether it can be analysed at all is
                # part of what arrived
                dt_bit,
                " · ".join(f"{r.name or '(unnamed)'} "
                           f"{r.start_sec / 60:.0f}–{r.end_sec / 60:.0f}m"
                           for r in s.regions) or "no windows declared"]
        status.object = "  \n".join(bits)

    slice_sel.param.watch(render, "value")
    render()
    return pn.template.FastListTemplate(
        title=title, sidebar=[pn.Column(slice_sel, status, width=340)],
        main=[main], accent_base_color="#4f6d7a",
        header_background="#4f6d7a",
    )


def load_any(path) -> tuple[str, Slice]:
    """Load a slice from a store .mat or an events CSV."""
    path = Path(path)
    s = load_events_csv(path) if path.suffix.lower() == ".csv" \
        else load_slice(path)
    return s.slice_id, s
