#!/usr/bin/env python3
"""What the assessor calls, drawn above the raster it called it on.

    python tools/make_assessor_calls_figure.py --also docs/learned

Figure id `assess_calls`, the same on every machine.

**Three rasters, one difference.** Same 40 ROIs, same 30-minute window, same
generator; the calls lane sits ABOVE the data rather than on it, so the raster
can be read without the answer drawn over it (Tony, 2026-08-24).

1. **quiet, nothing planted** — background at `bench.REGIMES` quiet, 5.2 mHz/ROI.
2. **busy, nothing planted** — the same, at the busy endpoint, 19.0 mHz/ROI.
   Every call in this panel is a coincidence: no shared process exists.
3. **busy, twelve events planted** — the same background with real coordinated
   events added at known times, drawn as a second lane. This is the comparison:
   what a call on a planted event looks like beside a call on nothing.

The point is to let a person judge the calls by eye, which is the only thing that
can settle whether they look like coordination — and is the reason
`docs/RESET.md` §1 makes the instrument a person and a program together rather
than the program alone.

**The clusters drawn are the clusters counted.** `cluster_calls` below repeats
`assess._clusters`' grouping to recover the call TIMES, which `_clusters` does
not return, and then asserts its own count and spans against what `_clusters`
reports. A figure that drew a different set of clusters than the statistic used
would be worse than no figure.

This measures and changes nothing; `assess_coactivity` is parity-held
(FOUNDATIONS §2). Companion to `assess_null_leak` and to
`docs/todo/2026-08-24-the-null-leaks-and-the-excess-is-mostly-selection.md`.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np

FIGURE_ID = "assess_calls"

INK = "#16202b"
SPURIOUS = "#b03a48"
TRUE_C = "#1f7a44"
PLANTED = "#1f6fb4"
GUIDE = "#9a9a9a"

DUR = 1800.0                    # the assessed window: 30 min, over the floor
N_ROI = 40
BIN = 1.0
K = 3
MERGE_BINS = 2
WM_FACTOR = 1.5
N_SUR = 200
WIN_MIN = DUR / 60.0

#: What the rasters SHOW. The statistic is computed over the whole 30 minutes;
#: 40 ROIs x 30 minutes drawn at once is a smear, and a figure meant for a
#: person to judge by eye has to be legible at the width it is printed.
VIEW = (300.0, 660.0)

QUIET_HZ = 0.0052
BUSY_HZ = 0.0190

#: Planted events for panel 3: how many, how many ROIs each recruits, and how
#: tightly. Recruitment and tightness are in the range `derive_spec` fits from a
#: real assessment, so this is a plausible event rather than a cartoon one.
N_PLANTED = 12
PLANT_ROIS = 8
PLANT_JITTER_SEC = 0.30


def independent_trains(rate_hz: float, seed: int, n_roi: int = N_ROI):
    """Nothing planted: every ROI drawn on its own, no shared process."""
    rng = np.random.default_rng(seed)
    return [np.sort(rng.uniform(0.0, DUR, size=rng.poisson(rate_hz * DUR)))
            for _ in range(n_roi)]


def plant(trains, seed: int, n_events: int = N_PLANTED):
    """Add real coordinated events to a background, and say where they are.

    Each event picks `PLANT_ROIS` ROIs at random and gives each one an onset
    scattered around the event time. Placed at least 60 s apart so no two can be
    read as one, and away from the window edges.
    """
    rng = np.random.default_rng(10_000 + seed)
    out = [t.copy() for t in trains]
    times: list[float] = []
    while len(times) < n_events:
        t = float(rng.uniform(120.0, DUR - 120.0))
        if all(abs(t - u) > 60.0 for u in times):
            times.append(t)
    times.sort()
    for t in times:
        who = rng.choice(len(out), size=PLANT_ROIS, replace=False)
        for r in who:
            out[r] = np.sort(np.append(
                out[r], t + rng.normal(0.0, PLANT_JITTER_SEC)))
    return out, np.asarray(times)


def cluster_calls(trains, counts, k=K, bin_width=BIN, merge_bins=MERGE_BINS,
                  wm_factor=WM_FACTOR):
    """The assessor's calls, with the TIMES `assess._clusters` does not return.

    Repeats that function's grouping and gathering, then checks itself against
    it: same number of clusters, same spans to 1e-9. If the two ever disagree
    this raises rather than drawing a different set of events than the statistic
    counted.
    """
    from bugarach.assess import _clusters

    wm = wm_factor * bin_width
    n_bins = counts.size
    fire = np.flatnonzero(counts >= k)
    calls: list[dict] = []
    if fire.size:
        groups, cur = [], [int(fire[0])]
        for q in range(1, fire.size):
            if fire[q] - fire[q - 1] <= merge_bins:
                cur.append(int(fire[q]))
            else:
                groups.append(cur)
                cur = [int(fire[q])]
        groups.append(cur)

        for g in groups:
            gi = np.asarray(g, dtype=np.float64)
            tc = float(np.mean((gi + 0.5) * bin_width))
            gathered = []
            for v in trains:
                if v.size == 0:
                    continue
                near = v[np.abs(v - tc) <= wm]
                if near.size:
                    gathered.append(float(near[np.argmin(np.abs(near - tc))]))
            if len(gathered) >= k:
                oo = np.asarray(gathered, dtype=float)
                calls.append({"centre": tc, "t0": float(oo.min()),
                              "t1": float(oo.max()), "n": int(oo.size),
                              "peak": float(np.max(counts[g]))})

    _sds, _parts, _peaks, spans = _clusters(trains, counts, k, bin_width,
                                            n_bins, merge_bins, wm)
    assert len(calls) == len(spans), (
        f"drew {len(calls)} calls, the statistic counted {len(spans)}")
    if calls:
        mine = np.asarray([c["t1"] - c["t0"] for c in calls])
        assert np.max(np.abs(mine - np.asarray(spans))) < 1e-9, \
            "the drawn clusters are not the clusters the statistic counted"
    return calls


def _null_mean(trains, n_bins, seed=20260722, n_sur=N_SUR):
    from bugarach.assess import _coact_count

    rng = np.random.RandomState(seed)
    total = np.zeros(n_bins)
    for _ in range(n_sur):
        off = rng.random_sample(len(trains)) * DUR
        total += _coact_count(
            [np.mod(v + off[r], DUR) if v.size else v
             for r, v in enumerate(trains)], DUR, BIN, n_bins)
    return total / float(n_sur)


def case(label: str, rate_hz: float, seed: int, planted: bool) -> dict:
    from bugarach.assess import _coact_count

    trains = independent_trains(rate_hz, seed)
    truth = np.empty(0)
    if planted:
        trains, truth = plant(trains, seed)

    n_bins = int(np.ceil(DUR / BIN))
    counts = _coact_count(trains, DUR, BIN, n_bins)
    nm = _null_mean(trains, n_bins)
    calls = cluster_calls(trains, counts)

    bk = np.flatnonzero(counts >= K)
    excess = (counts[bk].sum() - nm[bk].sum()) / WIN_MIN

    # a call is "on" a planted event if the event time falls inside its span,
    # widened by the gather window the assessor itself used
    wm = WM_FACTOR * BIN
    for c in calls:
        c["true"] = bool(truth.size and np.any(
            (truth >= c["t0"] - wm) & (truth <= c["t1"] + wm)))

    return {"label": label, "rate": rate_hz, "trains": trains, "truth": truth,
            "calls": calls, "excess": excess,
            "n_calls": len(calls), "n_true": sum(c["true"] for c in calls),
            "in_view": sum(VIEW[0] <= c["centre"] <= VIEW[1] for c in calls)}


def build(cases: list[dict], width: int):
    import holoviews as hv

    from bugarach.ui.app import _time_axis_hook

    rows = []
    for i, c in enumerate(cases):
        last = i == len(cases) - 1

        # ---- the calls lane, ABOVE the data and never drawn on it
        segs, cols = [], []
        for call in c["calls"]:
            if not (VIEW[0] - 5 <= call["centre"] <= VIEW[1] + 5):
                continue
            segs.append((call["t0"], 0.0, call["t1"], 0.0))
            cols.append(TRUE_C if call["true"] else SPURIOUS)
        # Drawn one segment at a time so each call keeps its own colour. A
        # single Segments element with a categorical colour dimension would be
        # tidier and needs a key this element does not carry, and the call count
        # per panel is in the dozens rather than the thousands.
        lane_items = []
        for (t0, _y, t1, _y2), col in zip(segs, cols):
            lane_items.append(hv.Segments([(t0, 0.0, t1, 0.0)]).opts(
                color=col, line_width=8, alpha=0.9))
        if not lane_items:
            lane_items = [hv.Segments([]).opts(color=SPURIOUS)]

        planted_lane = []
        if c["truth"].size:
            vis = c["truth"][(c["truth"] >= VIEW[0]) & (c["truth"] <= VIEW[1])]
            # Down, at the raster this lane sits above — CLAUDE.md, plot
            # conventions.
            planted_lane = [hv.Scatter((vis, np.full(vis.size, -1.0))).opts(
                marker="inverted_triangle", size=11, color=PLANTED,
                line_color=INK, line_width=0.6)]

        # NEVER the x-axis, on any lane. One axis per linked group and it belongs
        # to the bottom row (plot conventions); the first version gave it to the
        # last lane as well as the last raster, which put a second axis in the
        # middle of the figure and read as a break between panels.
        calls_row = hv.Overlay(lane_items + planted_lane).opts(
            width=width, height=70, xlim=VIEW, ylim=(-2.0, 1.0),
            yaxis="bare", xaxis="bare", xlabel="",
            ylabel=("assessor calls" if not c["truth"].size
                    else "calls · ▼ planted"),
            fontsize={"ylabel": "9pt", "ticks": "8pt"},
            show_legend=False, toolbar=None, hooks=[_time_axis_hook])

        # ---- the raster
        ts, ys = [], []
        for r, v in enumerate(c["trains"]):
            m = (v >= VIEW[0]) & (v <= VIEW[1])
            ts.append(v[m])
            ys.append(np.full(int(m.sum()), r))
        t = np.concatenate(ts) if ts else np.empty(0)
        y = np.concatenate(ys) if ys else np.empty(0)
        raster = hv.Scatter((t, y), kdims=["t"], vdims=["roi"]).opts(
            marker="dash", angle=90, size=6, color=INK, alpha=0.75,
            width=width, height=200, xlim=VIEW, ylim=(-1, N_ROI),
            xaxis="bottom" if last else "bare",
            xlabel="time" if last else "",
            ylabel=f"{c['label']} · {N_ROI} ROI",
            fontsize={"ylabel": "9pt", "xlabel": "9pt", "ticks": "8pt"},
            toolbar=None, hooks=[_time_axis_hook])

        rows.append(calls_row)
        rows.append(raster)
    return hv.Layout(rows).cols(1).opts(shared_axes=True, toolbar=None)


def header_html(cases: list[dict]) -> str:
    rows = "".join(
        f"<tr><td style='padding:2px 14px 2px 0'>{c['label']}</td>"
        f"<td style='padding:2px 14px 2px 0;text-align:right'>"
        f"{c['rate']*1000:.1f} mHz</td>"
        f"<td style='padding:2px 14px 2px 0;text-align:right'>"
        f"{'—' if not c['truth'].size else c['truth'].size}</td>"
        f"<td style='padding:2px 14px 2px 0;text-align:right'><b>{c['n_calls']}</b></td>"
        f"<td style='padding:2px 14px 2px 0;text-align:right'>{c['n_true']}</td>"
        f"<td style='padding:2px 0;text-align:right'>{c['excess']:.2f}</td></tr>"
        for c in cases)
    return f"""
<div style="font:13px/1.5 -apple-system,Segoe UI,sans-serif;color:{INK};
            max-width:62rem;margin:0 auto 0.5rem">
<p><b>What the assessor calls, above the raster it called it on.</b> Same 40
ROIs, same {DUR/60:.0f}-minute window, same generator — the only difference
between the panels is the background rate and whether any coordination was
planted. Calls are drawn in a lane <i>above</i> the data so the raster can be
read without the answer over it.
<span style="color:{SPURIOUS}"><b>Red</b></span> is a call with no planted event
under it; <span style="color:{TRUE_C}"><b>green</b></span> is a call on one;
<span style="color:{PLANTED}"><b>▼</b></span> marks a planted event.</p>

<table style="border-collapse:collapse;font-size:12px">
<tr style="border-bottom:1px solid #c8d6e4">
  <th style="text-align:left;padding-right:14px">panel</th>
  <th style="text-align:right;padding-right:14px">background</th>
  <th style="text-align:right;padding-right:14px">planted</th>
  <th style="text-align:right;padding-right:14px">calls (30 min)</th>
  <th style="text-align:right;padding-right:14px">on a planted event</th>
  <th style="text-align:right">excess/min</th></tr>
{rows}
</table>

<p>The top two panels contain <b>no coordination at all</b> — every ROI's train
was drawn on its own, so every call in them is a coincidence the rate-matched
null was supposed to account for. Judge whether they look different in kind from
the green ones in the third panel, which sit on events that are really there.</p>

<p style="color:#5c6773">K = {K}, {BIN:.0f} s bins, {N_SUR} surrogates,
{PLANT_ROIS} ROIs per planted event at {PLANT_JITTER_SEC*1000:.0f} ms jitter.
Counts and the excess are over the whole {DUR/60:.0f} minutes; the rasters show
{(VIEW[1]-VIEW[0])/60:.0f} minutes of it so the events are legible.
<b>This measures and changes nothing</b> — <code>assess_coactivity</code> is
1e-9 parity-held against <code>measure_coordination_timescale.m</code>. The
clusters drawn here are asserted against the ones the statistic counted.</p>
</div>"""


def _render_png(html_path: Path, png_path: Path, *, wait_ms: int = 3000,
                width: int = 1500, height: int = 1500) -> bool:
    try:
        from playwright.sync_api import sync_playwright
    except Exception as exc:                                   # noqa: BLE001
        print(f"(PNG render skipped: {exc})", file=sys.stderr)
        return False
    try:
        with sync_playwright() as pw:
            b = pw.chromium.launch()
            pg = b.new_page(viewport={"width": width, "height": height},
                            device_scale_factor=2)
            pg.goto(html_path.resolve().as_uri())
            pg.wait_for_timeout(wait_ms)
            pg.screenshot(path=str(png_path), full_page=True)
            b.close()
        return True
    except Exception as exc:                                   # noqa: BLE001
        print(f"(PNG render failed: {type(exc).__name__}: {exc})", file=sys.stderr)
        return False


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--width", type=int, default=1100)
    p.add_argument("--out", default=None,
                   help="destination; defaults to the darkroom")
    p.add_argument("--also", type=Path, default=None,
                   help="second destination, e.g. docs/learned")
    p.add_argument("--no-png", dest="png", action="store_false", default=True)
    a = p.parse_args()

    # Labels stay short: they are the y-axis label of a 200px row, and the first
    # version clipped the longest one to "40 R(".
    cases = [
        case("quiet · nothing", QUIET_HZ, seed=1, planted=False),
        case("busy · nothing", BUSY_HZ, seed=1, planted=False),
        case("busy · 12 planted", BUSY_HZ, seed=2, planted=True),
    ]
    for c in cases:
        print(f"  {c['label']:<28} {c['n_calls']:>4} calls · "
              f"{c['n_true']:>3} on a planted event · "
              f"excess {c['excess']:7.2f}/min · {c['in_view']} in view")

    from bugarach.paths import darkroom, unresolved_message
    dest = Path(a.out) if a.out else darkroom()
    if dest is None:
        print(unresolved_message(), file=sys.stderr)
        return 1

    import holoviews as hv
    import panel as pn
    hv.extension("bokeh")
    layout = build(cases, a.width)

    dests = [dest] + ([a.also] if a.also else [])
    for i, d in enumerate(dests):
        d.mkdir(parents=True, exist_ok=True)
        html = d / f"{FIGURE_ID}.html"
        pn.panel(pn.Column(pn.pane.HTML(header_html(cases)),
                           pn.pane.HoloViews(layout))).save(str(html))
        print(f"wrote {html}")
        if a.png:
            shot = d / f"{FIGURE_ID}.png"
            if i == 0:
                if _render_png(html, shot):
                    print(f"wrote {shot}")
            else:
                src = dests[0] / f"{FIGURE_ID}.png"
                if src.is_file():
                    shot.write_bytes(src.read_bytes())
                    print(f"wrote {shot}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
