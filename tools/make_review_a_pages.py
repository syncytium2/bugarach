#!/usr/bin/env python3
"""Review A of the route to calls: simulated recordings beside real ones, at 4x and at 3x.

    python tools/make_review_a_pages.py                      # every stream, DI and MALE
    python tools/make_review_a_pages.py --streams fast --groups di --png

One page per stream and group. Tony's step 3 (ADR 2026-11-17-b16b): *"human review of synthetic
data and real data side by side"*, with both thresholds carried in parallel (Tony, 2026-11-17:
*"we will run 3x and 4x in parallel"*). Each page holds, for one group's baseline windows:

* **Figure 1, the rasters.** Every real recording drawn three times on the same rows: the 4x
  export, the 3x export, and the 3x onsets with no 4x onset on the same cell (*3x only*). Then
  simulated recordings from that group's bench sets at each threshold (``<stream>_<group>`` and
  ``<stream>_<group>_3x``, ``docs/learned/bench_sets/``), one per background, drawn the same way
  over the same 20 minutes.
* **Figure 2, the cross-cell onset correlogram**, real against simulated at each threshold
  (``tools/measure_jitter_correlogram.py``'s statistic, imported and not re-derived).
* **Figure 3, each cell's onset rate**, real against simulated at each threshold.

**Display only. No detector is constructed and none is run, and nothing is drawn on a raster.**
The simulated recordings carry no marker for what was planted: the question the page asks is
whether they look like the data, and a marker would answer it for the eye.

**The combined stream is drawn in one ink on this page**, real and simulated alike. The real
export labels each combined onset fast or slow and the group raster pages draw the slow ones in a
second ink; the simulated combined recordings carry no such label, so two inks would tell real
from simulated at a glance.

**Baseline only** (FOUNDATIONS §9): each recording's analysis window from
``assess_folder.generation_window``. **Rows are cells in the same order on all three rasters of a
recording**, busiest at 3x on top, so a row can be followed across the thresholds.

**Matching 3x to 4x.** The two exports hold the same 12 recordings and the same cells. A 3x
onset is *3x only* when no 4x onset on that cell, in that stream, lies within
:data:`MATCH_SEC`. On 20260917_411 every matched pair agreed to the frame (0.1 s), and the count
did not move between 0.05 s and 1 s, so the tolerance is not doing the work.

**Named under the estate scheme with ``thr3x``.** The scheme has a threshold code for 4x and one
for 3x, and none for a page holding both; with no ``thr`` field a name means 4x. The page's
subject is what 3x changes, so it carries ``thr3x``.

Destination is the darkroom, resolved by ``bugarach.paths``; ``--out`` replaces it.
"""
from __future__ import annotations

import argparse
import html as _html
import os
import sys
import tempfile
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np

REPO = Path(__file__).resolve().parents[1]
for _p in (REPO / "src", REPO / "tools"):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

ROLES = {"4x": "tracked_cohorts", "3x": "tracked_cohorts_3x"}
THRS = ("4x", "3x")
STREAMS = ("fast", "slow", "combined")
GROUPS = ("di", "male")
MATCH_SEC = 0.05
SIM_SEEDS = tuple(range(1, 9))
DRAW_SEED = 1
DT = 0.1
WIDTH = 1250
ROI_PX = 3
LABEL_PX = 170
AXIS_PX = 30
GAP_PX = 4
SECTION_GAP_PX = 14
SCROLL_GUTTER_PX = 60
TIGHT = {"plot.min_border_top": 0, "plot.min_border_bottom": 0}
RATE_FLOOR_PER_MIN = 0.01
#: Okabe-Ito: 4x black, 3x blue. Real is a solid line, simulated a dashed one.
INK = {"4x": "#000000", "3x": "#0072B2"}
DASH = {"real": "solid", "sim": "dashed"}


def set_name(stream: str, group: str, thr: str) -> str:
    return f"{stream}_{group}" + ("_3x" if thr == "3x" else "")


# ---------------------------------------------------------------- the real recordings

def _window(sl):
    from bugarach.assess_folder import generation_window

    (lo, hi), _ = generation_window(sl)
    label = next((r.name for r in sl.regions if r.start_sec <= lo and hi <= r.end_sec), None)
    if label is None or label.lower() != "baseline":
        raise SystemExit(f"{sl.slice_id}: the analysis window {lo:.0f}-{hi:.0f} s is not inside "
                         f"the baseline period ({label!r}); this page draws baseline only")
    return lo, hi


def _in(t, lo, hi):
    t = np.asarray(t, float)
    return np.sort(t[np.isfinite(t) & (t >= lo) & (t < hi)])


def only_in(a, b, tol: float = MATCH_SEC) -> np.ndarray:
    """Onsets of ``a`` with no onset of ``b`` within ``tol`` seconds (both sorted)."""
    a, b = np.asarray(a, float), np.asarray(b, float)
    if a.size == 0 or b.size == 0:
        return a
    i = np.clip(np.searchsorted(b, a), 1, b.size - 1) if b.size > 1 else np.zeros(a.size, int)
    d = np.minimum(np.abs(b[i] - a), np.abs(b[np.maximum(i - 1, 0)] - a))
    return a[d > tol]


def real_trains(sl4, sl3, stream: str):
    """Per cell, the baseline onsets at 4x, at 3x, and at 3x only, re-zeroed at the window."""
    if sl4.slice_id != sl3.slice_id:
        raise SystemExit(f"the two exports disagree on recording order: {sl4.slice_id} "
                         f"against {sl3.slice_id}")
    if sl4.roi_ids is not None and list(sl4.roi_ids) != list(sl3.roi_ids):
        raise SystemExit(f"{sl4.slice_id}: the two exports list different cells")
    lo, hi = _window(sl4)
    if _window(sl3) != (lo, hi):
        raise SystemExit(f"{sl4.slice_id}: the two exports place the baseline window differently")
    t4 = [_in(t, lo, hi) - lo for t in sl4.streams[stream].t50rise]
    t3 = [_in(t, lo, hi) - lo for t in sl3.streams[stream].t50rise]
    t3o = [only_in(b, a) for a, b in zip(t4, t3)]
    return dict(lo=lo, hi=hi, t4=t4, t3=t3, t3only=t3o)


def correlogram(trains, duration_sec: float):
    """(observed, expected) cross-cell onset pairs per 0.1 s lag, 0 to 10 s."""
    import measure_jitter_correlogram as mjc

    L = int(round(duration_sec / DT))
    return mjc.pairs([np.round(np.asarray(t, float) / DT).astype(int) for t in trains], L)


def rates_per_min(trains, duration_sec: float) -> np.ndarray:
    return np.array([len(t) for t in trains], float) / (duration_sec / 60.0)


# ---------------------------------------------------------------- the simulated recordings

def _sim_one(args):
    name, regime, seed = args
    from bugarach import bench_sets

    b = bench_sets.load(name)
    s, gt = b.make_recording(regime, seed)
    dur = float(gt.params["duration_sec"])
    trains = [np.sort(np.asarray(t, float)) for t in s.streams[b.STREAM].t50rise]
    o, e = correlogram(trains, dur)
    return name, regime, seed, o, e, rates_per_min(trains, dur), dur, trains


def simulate(names, jobs: int):
    from bugarach import bench_sets

    tasks = [(n, r, s) for n in names for r in bench_sets.load(n).REGIMES for s in SIM_SEEDS]
    out = {n: dict(o=0.0, e=0.0, rates=[], draw={}, recordings=0, duration_sec=None)
           for n in names}
    with ProcessPoolExecutor(max_workers=jobs) as ex:
        for name, regime, seed, o, e, r, dur, trains in ex.map(_sim_one, tasks):
            d = out[name]
            d["o"] = d["o"] + o
            d["e"] = d["e"] + e
            d["rates"].append(r)
            d["recordings"] += 1
            d["duration_sec"] = dur
            if seed == DRAW_SEED:
                d["draw"][regime] = trains
    for d in out.values():
        d["rates"] = np.concatenate(d["rates"])
    return out


# ---------------------------------------------------------------- drawing

def _stream(trains):
    from bugarach.store import Stream

    t = [np.asarray(v, float) for v in trains]
    return Stream(locs=t, amp=[np.ones_like(v) for v in t], width=[np.zeros_like(v) for v in t],
                  t50rise=t)


def raster(trains, *, ext, ydim: str, sort: str):
    from bugarach.ui.diagnostic import raster_panel

    st = _stream(trains)
    return raster_panel(st, ext=ext, name="events", width=WIDTH - LABEL_PX,
                        height=ROI_PX * max(st.n_rois, 1), ydim=ydim, ticks="minimal",
                        sort=sort).opts(ylabel="", backend_opts=TIGHT)


def _label(lines, height: int):
    import panel as pn

    body = "<br>".join(lines)
    return pn.pane.HTML(
        f"<div style='height:{height}px;width:{LABEL_PX - 8}px;display:flex;align-items:center;"
        f"font:11px/1.25 system-ui,sans-serif;color:#111'><div>{body}</div></div>",
        width=LABEL_PX, height=height, margin=0)


def rasters(real, sims, *, stream: str, group: str, ext):
    """Figure 1's rows: (label lines, panel) for each raster, real recordings first."""
    rows = []
    for sid, r in real:
        order = np.argsort([-len(t) for t in r["t3"]], kind="stable")
        n = len(order)
        for key, what in (("t4", "4x"), ("t3", "3x"), ("t3only", "3x only")):
            trains = [r[key][i] for i in order]
            k = int(sum(len(t) for t in trains))
            p = raster(trains, ext=ext, ydim=f"roi_{sid}_{key}", sort="store")
            rows.append(([f"<b>{sid}</b>" if key == "t4" else "&nbsp;",
                          f"real · {what}", f"{n} cells · {k} onsets"], p))
    for thr in THRS:
        name = set_name(stream, group, thr)
        for regime, trains in sims[name]["draw"].items():
            trains = [t[t < ext[1]] for t in trains]
            k = int(sum(len(t) for t in trains))
            p = raster(trains, ext=ext, ydim=f"roi_{name}_{regime}", sort="freq")
            rows.append(([f"<b>simulated · {thr}</b>", f"{name}, {regime.replace('_', ' ')}",
                          f"seed {DRAW_SEED} · {len(trains)} cells · {k} onsets"], p))
    return rows


def _excess(o, e):
    with np.errstate(invalid="ignore", divide="ignore"):
        return np.asarray(o, float) / np.asarray(e, float) - 1.0


def correlogram_figure(curves):
    import holoviews as hv

    lag = np.arange(len(next(iter(curves.values())))) * DT
    layers = [hv.Curve((lag, y), kdims=["lag_s"], vdims=["excess"]).opts(
        color=INK[thr], line_dash=DASH[kind], line_width=2 if kind == "real" else 1.5)
        for (kind, thr), y in curves.items()]
    return hv.Overlay(layers).opts(
        width=640, height=300, xlabel="lag between onsets in two cells (s)",
        ylabel="excess pairs (observed / chance − 1)", show_legend=False, toolbar=None)


def rate_figure(rates):
    import holoviews as hv

    layers = []
    for (kind, thr), r in rates.items():
        x = np.sort(np.maximum(np.asarray(r, float), RATE_FLOOR_PER_MIN))
        y = np.arange(1, x.size + 1) / x.size
        layers.append(hv.Curve((x, y), kdims=["rate_per_min"], vdims=["share"]).opts(
            interpolation="steps-post", color=INK[thr], line_dash=DASH[kind],
            line_width=2 if kind == "real" else 1.5))
    return hv.Overlay(layers).opts(
        width=640, height=300, logx=True, xlabel="onsets per minute, per cell (log scale)",
        ylabel="share of cells at or below", show_legend=False, toolbar=None)


def legend_html() -> str:
    def key(thr, kind):
        dash = "border-top-style:dashed" if kind == "sim" else "border-top-style:solid"
        return (f"<span style='display:inline-block;width:26px;margin:0 4px 3px 10px;"
                f"border-top:{2 if kind == 'real' else 1.5}px {INK[thr]};{dash};"
                f"border-top-color:{INK[thr]}'></span>"
                f"{'real' if kind == 'real' else 'simulated'} {thr}")
    return "".join(key(t, k) for t in THRS for k in ("real", "sim"))


def page_name(stream: str, group: str, date: str) -> str:
    from naming import artifact_name

    return artifact_name.build(
        artifact_name.load_codes(), type="raster", ext="html", date=date, signal="roi",
        stream=stream, treatment="baseline", groups=group, win="win20min", thr="thr3x")


def build_page(stream: str, group: str, real, sims, stamps) -> "object":
    import panel as pn

    from bugarach.ui.app import _time_axis_hook
    from bugarach.ui.navigate import navigation_hook

    ext = (0.0, 1200.0)
    rows = rasters(real, sims, stream=stream, group=group, ext=ext)
    panels = [p for _, p in rows]
    for p in panels[:-1]:
        p.opts(xaxis=None, toolbar=None, backend_opts=TIGHT)
    last_h = panels[-1].opts.get("plot").kwargs.get("height") or 0
    panels[-1].opts(height=last_h + AXIS_PX, toolbar=None)
    for p in panels:
        p.opts(hooks=[_time_axis_hook, navigation_hook])

    G = group.upper()
    n_real = len(real)
    curves, rates = {}, {}
    for thr in THRS:
        o = sum(r[f"pairs{thr}"][0] for _, r in real)
        e = sum(r[f"pairs{thr}"][1] for _, r in real)
        curves[("real", thr)] = _excess(o, e)
        rates[("real", thr)] = np.concatenate([r[f"rates{thr}"] for _, r in real])
        s = sims[set_name(stream, group, thr)]
        curves[("sim", thr)] = _excess(s["o"], s["e"])
        rates[("sim", thr)] = s["rates"]

    def heading(n, name):
        return pn.pane.HTML(
            f"<div style='font:600 14px system-ui,sans-serif;margin:{SECTION_GAP_PX}px 0 4px'>"
            f"Figure {n}. {name}<span style='font-weight:400;font-size:12px'>"
            f"{legend_html() if n > 1 else ''}</span></div>", width=WIDTH)

    items = [pn.pane.HTML(
        f"<h2 style='font:600 18px system-ui,sans-serif;margin:8px 0 2px'>Review A · {stream} · "
        f"{G} · baseline · real at 4x and 3x beside simulated</h2>", width=WIDTH),
        heading(1, f"Rasters: {n_real} real {G} recordings, each at 4x, at 3x and 3x only; "
                   f"then simulated recordings from the {G} sets at each threshold. "
                   f"One row per cell, one mark per onset, first 20 minutes")]
    sim_start = 3 * n_real
    for i, (lines, p) in enumerate(rows):
        h = (p.opts.get("plot").kwargs.get("height") or 0)
        if i == sim_start:
            items.append(pn.pane.HTML(
                "<div style='font:600 12px system-ui,sans-serif;margin:10px 0 4px;"
                "border-top:1px solid #999;padding-top:6px'>Simulated</div>", width=WIDTH))
        gap = GAP_PX if (i % 3 == 2 or i >= sim_start) else 0
        items.append(pn.Row(_label(lines, h), pn.pane.HoloViews(p, margin=0, linked_axes=True),
                            margin=(0, 0, gap, 0)))
    items += [heading(2, "Cross-cell onset correlogram, all recordings of the group pooled"),
              pn.pane.HoloViews(correlogram_figure(curves), linked_axes=False),
              heading(3, "Each cell's onset rate over its baseline window"),
              pn.pane.HoloViews(rate_figure(rates), linked_axes=False),
              pn.pane.HTML(explainer(stream, group, real, sims, stamps), width=WIDTH - 100)]
    return pn.Column(*items, margin=(0, 0, 0, SCROLL_GUTTER_PX))


def explainer(stream, group, real, sims, stamps) -> str:
    G = group.upper()
    s4, s3 = (sims[set_name(stream, group, t)] for t in THRS)
    n4 = sum(int(sum(len(t) for t in r["t4"])) for _, r in real)
    n3 = sum(int(sum(len(t) for t in r["t3"])) for _, r in real)
    n3o = sum(int(sum(len(t) for t in r["t3only"])) for _, r in real)
    n4o = sum(int(sum(len(only_in(a, b)) for a, b in zip(r["t4"], r["t3"]))) for _, r in real)
    esc = _html.escape
    return f"""
<div style='font:13px/1.5 system-ui,sans-serif;color:#222;margin-top:18px'>
<h3 style='font-size:15px'>What this page is</h3>
<p>Review A of the route to calls (ADR 2026-11-17-b16b, Tony's step 3): do simulated recordings
look like the real ones, at each threshold? Nothing on it is scored and no detector runs.</p>
<p><b>Datasets.</b> 4x: <code>{esc(stamps['4x'])}</code>. 3x: <code>{esc(stamps['3x'])}</code>.
Each recording's baseline analysis window only (20 minutes each), re-zeroed at its start.
Bench sets: <code>{set_name(stream, group, '4x')}</code> and <code>{set_name(stream, group, '3x')}</code>
(<code>docs/learned/bench_sets/</code>), built from the {G} recordings' own measured values.</p>
<h3 style='font-size:15px'>How to read Figure 1, the rasters</h3>
<p>Each real recording is drawn three times. <b>4x</b> and <b>3x</b> are the two exports.
<b>3x only</b> is the 3x onsets with no 4x onset on the same cell within {MATCH_SEC} s: what
lowering the threshold adds. Rows are cells in the same order on all three, busiest at 3x on top,
so a row can be followed down. Across the {len(real)} {G} recordings: {n4} onsets at 4x, {n3} at
3x, {n3o} of them 3x only, and {n4o} 4x onsets with no 3x partner.</p>
<p>The simulated recordings are drawn the same way, rows sorted busiest on top, over their first
20 minutes ({s4['duration_sec']:.0f} s are simulated). One recording per background
(quiet and busy), seed {DRAW_SEED}. What was planted is not marked, on purpose: the question is
whether a simulated recording looks like a real one, and a marker would answer it for the eye.</p>
<p>The combined stream is drawn in one ink here, real and simulated alike: the simulated
recordings do not label onsets fast or slow, so a second ink would tell them apart.</p>
<p>Navigation: Ctrl+wheel zooms time at the cursor, a drag zooms to a box (time only),
Shift-drag slides, double-click shows everything, Ctrl+Z steps back.</p>
<h3 style='font-size:15px'>How to read Figures 2 and 3</h3>
<p><b>Figure 2</b> counts onset pairs in two different cells at each lag, against the count expected
if every cell's onsets were independent at its own total (Perkel, Gerstein &amp; Moore 1967; the
statistic of <code>tools/measure_jitter_correlogram.py</code>). A peak at short lags is onsets
arriving together; its width reflects their spread. Real curves pool the {len(real)} recordings;
simulated curves pool {s4['recordings']} recordings per threshold ({len(SIM_SEEDS)} seeds × 2
backgrounds, full length).</p>
<p><b>Figure 3</b> is the cumulative share of cells at or below each onset rate. Cells with no onset
in the window are drawn at {RATE_FLOOR_PER_MIN} per minute so the log axis can hold them.</p>
<p>Solid lines are real, dashed are simulated; black is 4x, blue is 3x.</p>
<h3 style='font-size:15px'>What this does not show</h3>
<p>Whether the 4x or the 3x export is right: both run through the route in parallel (Tony,
2026-11-17). Anything about {G} against another group: the sets describe the data for simulation
and the page compares nothing between groups (ADR-0017). The pooled set
(<code>{stream}_all</code>) is not drawn; its recordings are the DI and MALE pages together.</p>
</div>"""


# ---------------------------------------------------------------- main

def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--streams", nargs="+", default=list(STREAMS), choices=STREAMS)
    ap.add_argument("--groups", nargs="+", default=list(GROUPS), choices=GROUPS)
    ap.add_argument("--out", type=Path, default=None,
                    help="destination folder (default: the darkroom's 2026-11-17-review-a/)")
    ap.add_argument("--date", default="20261117", help="the date in the file names, YYYYMMDD")
    ap.add_argument("--jobs", type=int, default=12)
    ap.add_argument("--png", action="store_true", help="also write a flat PNG of each page")
    a = ap.parse_args(argv)

    from bugarach import dataset, paths
    from bugarach.groups import group_key
    from bugarach.io import load_folder
    from bugarach.ui.navigate import add_navigation

    out = a.out or paths.darkroom() / "2026-11-17-review-a"
    out.mkdir(parents=True, exist_ok=True)
    folders = {t: dataset.current(r) for t, r in ROLES.items()}
    stamps = {t: dataset.stamp(r)["name"] for t, r in ROLES.items()}
    slices = {t: load_folder(f) for t, f in folders.items()}
    groups = sorted(a.groups, key=lambda g: group_key(g.upper()))

    names = [set_name(s, g, t) for s in a.streams for g in groups for t in THRS]
    print(f"simulating {len(names)} sets x {len(SIM_SEEDS)} seeds x 2 backgrounds",
          file=sys.stderr)
    sims = simulate(names, a.jobs)

    for stream in a.streams:
        for group in groups:
            real = []
            for s4, s3 in zip(slices["4x"], slices["3x"]):
                if str(s4.meta.get("group_id") or "").strip().lower() != group:
                    continue
                r = real_trains(s4, s3, stream)
                dur = r["hi"] - r["lo"]
                for thr, key in (("4x", "t4"), ("3x", "t3")):
                    r[f"pairs{thr}"] = correlogram(r[key], dur)
                    r[f"rates{thr}"] = rates_per_min(r[key], dur)
                real.append((s4.slice_id, r))
            if not real:
                print(f"no {group} recordings for {stream}; no page", file=sys.stderr)
                continue
            html = out / page_name(stream, group, a.date)
            page = build_page(stream, group, real, sims, stamps)
            with tempfile.TemporaryDirectory() as td:
                tmp = Path(td) / "p.html"
                page.save(str(tmp), title=f"Review A {stream} {group.upper()}")
                if a.png:
                    from make_diagnostic import _render_png
                    shot = html.with_suffix(".png")
                    print("wrote" if _render_png(tmp, shot) else "no PNG for", shot.name)
                tmp.write_text(add_navigation(tmp.read_text(encoding="utf-8")), encoding="utf-8")
                os.replace(tmp, html)
            print("wrote", html)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
