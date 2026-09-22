#!/usr/bin/env python3
"""The brief intro to the coordination analysis: the problem, and the instrument.

    python tools/make_intro_figures.py                    # both, -> the darkroom
    python tools/make_intro_figures.py --figures 3        # only the simulated one
    python tools/make_intro_figures.py --sweeps saved.json  # reuse a sweep

Drawn for Tony's 2026-09-14 ask for *"a very brief intro to the current state of our
coordination analysis"*, with three figures. This tool draws two of them; the third is
already a tool:

* **Figure 1 — the problem.** Real senktide recordings from the default dataset (those whose
  first period after baseline is senktide — the rule the producer's own `senktide` split
  used, which is now an archive role), one per
  experimental group, each the median-sized field of its group, fast stream, aligned
  at the end of baseline, with the recorded periods and scored windows in a lane above
  each raster. The shape is the viewer's overview page, drawn through
  `make_group_raster_summary.build_page` so there is no second drawing path.
* **Figure 2 — how the detectors work, one per family.** Not drawn here:
  `python tools/make_diagnostic.py --bench baseline_quiet --without rate coact cicada
  --tube`. The three adaptive-threshold detectors, zoomed, are
  `tools/make_mechanism_figure.py`.
* **Figure 3 — the instrument.** Panel A: the bench recording at both ends of the
  background axis with its truth lane. Panel B: each detector's knob swept on the bench
  (`bench.sweep`), with the shipped value and the value `bench.pick_operating_point`
  picks — or no pick, where the rule refuses an edge-of-grid optimum.

**Figure 1 is real, unpublished treatment data, so there is no `--also`.** FOUNDATIONS
§5: nothing derived from a real recording is committed, and the one released slice is
a baseline. The destination is the darkroom and nowhere in the repo.

**Figure 3's truth lane is drawn here, not by `lane_panel`.** With no detector on the
page `lane_panel` colours every planted event "missed" — red — which is a verdict
nobody made.

The sweep takes about a minute at 12 recordings per knob value on four processes.
`--sweeps` reuses a saved one; the tool writes `sweeps.json` beside the figures either
way, so the numbers behind panel B travel with it.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import tempfile
import time
import warnings
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))

W = 1060
CAP = "font:13px/1.45 system-ui,sans-serif;color:#222;max-width:1040px;margin:4px 0 10px 0"
SUB = "font:12px system-ui,sans-serif;color:#111;margin:10px 0 0 78px"
GROUPS = ("DI", "MALE", "ORX", "OVX")
SWEPT = ("loco", "coact", "sync", "sce")
SWEEP_REGIME = "baseline_quiet"
KNOB_UNITS = {
    "threshold_pctile": "percentile of the surrogate null",
    "alpha": "false-alarm probability per bin",
    "C_threshold": "SPIKE-synchronization value, 0–1",
    "excess_threshold_hz": "events/s",
}


# ------------------------------------------------------------------ the sweep
def _sweep_one(job):
    from bugarach import bench

    det, seeds = job
    t0 = time.time()
    op = bench.OPERATING_POINTS[det]
    curve = bench.sweep(det, SWEEP_REGIME, seeds)
    rows = [dict(v=r.knob_value, f1=r.f1, recall=r.recall, precision=r.precision,
                 probe_per_min=r.hot_fa_per_min, n_planted=r.n_planted) for r in curve]
    try:
        best = bench.pick_operating_point(
            curve, max_probe_per_min=bench.MAX_PROBE_PER_MIN.get(det))
        pick = dict(v=best.knob_value, f1=best.f1, note="picked")
    except Exception as exc:          # noqa: BLE001 — a refusal is the result here
        pick = dict(v=None, note=f"{type(exc).__name__}: {exc}")
    return det, dict(knob=op.knob, shipped=op.params[op.knob], rows=rows, pick=pick,
                     secs=round(time.time() - t0, 1))


def run_sweeps(n_seeds: int, workers: int) -> dict:
    from bugarach.score import TOL_SEC

    seeds = tuple(range(1, n_seeds + 1))
    with ProcessPoolExecutor(workers) as ex:
        curves = dict(ex.map(_sweep_one, [(d, seeds) for d in SWEPT]))
    return dict(regime=SWEEP_REGIME, seeds=list(seeds), tol_sec=TOL_SEC, curves=curves)


# ------------------------------------------------------------------ figures
def _save(pn, items, dest: Path, name: str) -> list[Path]:
    from make_diagnostic import _render_png

    html = dest / f"{name}.html"
    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td) / "p.html"
        pn.Column(*items).save(str(tmp))       # write-then-replace: the darkroom is Dropbox
        os.replace(tmp, html)
    out = [html]
    if _render_png(html, html.with_suffix(".png"), scale=2):
        out.append(html.with_suffix(".png"))
    return out


def figure1(hv, pn, dest: Path) -> list[Path]:
    from bugarach import dataset
    from bugarach.io import load_folder
    from make_group_raster_summary import _anchor_of, build_page, treatment_one

    # The senktide cohort of the default dataset, selected the way the producer's split
    # was: by first non-baseline period. The split folder itself (`senktide`) is a subset
    # of `steps_excluded` and carries its contamination, so it is an archive now.
    folder = dataset.default()
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        slices = [s for s in load_folder(folder)
                  if (treatment_one(s) or "").strip().lower() == "senktide"]
    members = []
    for g in GROUPS:
        grp = sorted((s for s in slices
                      if s.meta.get("group_id") == g and _anchor_of(s) is not None),
                     key=lambda s: s.streams["fast"].n_rois)
        if grp:
            pick = grp[len(grp) // 2]          # the median-sized field in the group
            members.append((pick, _anchor_of(pick)))
    ext = (-21 * 60.0, 23 * 60.0)
    blocks, _ = build_page(members, ext=ext, manifest={}, width=W, stream="fast")
    items = [pn.pane.HTML(
        f"<div style='{CAP}'><b>Figure 1. The problem: which of these alignments are "
        f"coordination?</b> {len(members)} real recordings from the senktide cohort, one per "
        "experimental group, each the median-sized field of its group; fast stream. Each row of "
        "a raster is one ROI (region of interest, one cell), each tick one calcium-event onset, "
        "quietest ROI at the bottom. Recordings are aligned at the end of baseline, so senktide "
        "arrives at 0 on every one. The bar above each raster is the period recorded (grey "
        "baseline, orange senktide); the dark rule under it is the window the producer scores. "
        "Vertical alignments of many ROIs are what we call coordinated events — but cells also "
        "line up by chance, chance alignments rise with firing rate, and senktide raises firing "
        "rate. There is no ground truth on a real recording, so a detector's call here is a "
        "claim, not a measurement.</div>")]
    for sl, panels in blocks:
        items.append(pn.pane.HTML(
            f"<div style='{SUB}'><b>{sl.meta.get('group_id')}</b><span style='color:#666'> · "
            f"{sl.streams['fast'].n_rois} ROIs · recording {sl.slice_id}</span></div>"))
        items += [pn.pane.HoloViews(p) for p in panels]
    items.append(pn.pane.HTML(
        f"<div style='{CAP};color:#666'>Folder: {folder.name} (field-step artifacts excluded "
        "by the producer). Time axis: minutes relative to the end of baseline.</div>"))
    return _save(pn, items, dest, "figure1_the_problem")


def figure3(hv, pn, dest: Path, sweeps: dict) -> list[Path]:
    from bugarach import bench
    from bugarach.ui.app import TITLES
    from bugarach.ui.diagnostic import raster_panel

    rec = bench.BENCH_RECORDING
    ext = (0.0, rec["duration_sec"])
    hw = rec["hot_window"]
    levels = ", ".join(f"{int(round(p * 100))}%" for p in rec["participation"])
    items = [pn.pane.HTML(
        f"<div style='{CAP}'><b>Figure 3. The instrument: simulated recordings with planted "
        "coordination, and the sweep that sets each detector's operating point.</b> Panel A: "
        "the bench recording at the two ends of the background-rate axis, both taken from "
        f"untreated baselines only — quiet ({bench.REGIMES['baseline_quiet']['bg_rate_hz']} Hz "
        f"per ROI) and busy ({bench.REGIMES['baseline_busy']['bg_rate_hz']} Hz per ROI), the "
        "25th and 75th percentiles of slice-mean per-ROI rate. "
        f"{rec['n_roi']} ROIs, {rec['duration_sec'] / 60:g} minutes, "
        f"{sum(rec['n_per_level'])} planted coordinated events ({rec['n_per_level'][0]} each "
        f"with {levels} of ROIs participating), with per-ROI rate heterogeneity and burstiness "
        "fitted to real baselines. The lane above each raster carries the truth: ▼ a planted "
        "event, ▽ a distractor (a correlated burst that is coincidence, not coordination), and "
        f"the shaded strip is the promiscuity probe — a {(hw[1] - hw[0]) / 60:g}-minute dense "
        "block with nothing planted, so any call inside it is a false alarm by "
        "construction.</div>")]
    blocks = []
    for regime, label in (("baseline_quiet", "quiet background"),
                          ("baseline_busy", "busy background")):
        s, gt = bench.make_recording(regime, 1)
        yd = f"truth_{regime}"
        planted = np.asarray(gt.times, float)
        distr = np.asarray(gt.distractor_times, float)
        truth = (hv.Scatter(([ext[0]], [0.0]), kdims=["t"], vdims=[yd]).opts(alpha=0)
                 * hv.Rectangles([(hw[0], 0.0, hw[1], 1.0)]).opts(color="#f3dcc0",
                                                                   line_alpha=0)
                 * hv.Scatter((distr, np.full(distr.size, 0.72)), kdims=["t"], vdims=[yd])
                 .opts(marker="inverted_triangle", size=10, fill_alpha=0, line_color="#555")
                 * hv.Scatter((planted, np.full(planted.size, 0.35)), kdims=["t"], vdims=[yd])
                 .opts(marker="inverted_triangle", size=11, color="#111")
                 ).opts(width=W, height=46, xlim=ext, ylim=(0, 1), yaxis=None, xaxis=None,
                        toolbar=None, show_legend=False)
        raster = raster_panel(s.streams["events"], ext=ext, width=W, height=150,
                              name="simulated", ydim=f"roi_{regime}", ticks="minimal")
        blocks.append((label, [truth, raster]))
    flat = [p for _, ps in blocks for p in ps]
    for p in flat[:-1]:
        p.opts(xaxis=None, toolbar=None)
    flat[-1].opts(height=150 + 34, toolbar=None)
    for i, (label, ps) in enumerate(blocks):
        items.append(pn.pane.HTML(f"<div style='{SUB}'><b>A{i + 1}</b> · {label}</div>"))
        items += [pn.pane.HoloViews(p) for p in ps]

    n_rec = len(sweeps["seeds"])
    off_grid = [TITLES.get(d, d) for d, c in sweeps["curves"].items()
                if c["shipped"] not in [r["v"] for r in c["rows"]]]
    refused = [TITLES.get(d, d) for d, c in sweeps["curves"].items() if c["pick"]["v"] is None]
    items.append(pn.pane.HTML(
        f"<div style='{CAP};margin-top:22px'>Panel B: each detector's sensitivity knob swept "
        f"across its grid on {n_rec} simulated recordings ({sweeps['regime'].replace('baseline_', '')} "
        f"background, {n_rec * sum(rec['n_per_level'])} planted events in total). F1 is the "
        "harmonic mean of recall and precision, pooled over recordings; a call counts as a hit "
        f"within {sweeps['tol_sec']:g} s of a planted event. ○ is the value the detector "
        "currently ships at; ● is the value the selection rule picks — the highest F1 whose "
        "neighbours on the grid bracket it, and whose firing rate inside the probe stays under "
        "that detector's ceiling."
        + (f" {', '.join(off_grid)} ships at a value between grid points, so has no ○."
           if off_grid else "")
        + (f" <b>{', '.join(refused)} gets no ●: F1 peaks at the end of its grid, and the rule "
           "refuses to call the end of a search an optimum.</b>" if refused else "")
        + "</div>"))
    plots = []
    for det in SWEPT:
        c = sweeps["curves"][det]
        vals = [r["v"] for r in c["rows"]]
        idx = np.arange(len(vals))
        f1 = np.array([r["f1"] for r in c["rows"]])
        xd, yd = f"knob_{det}", f"f1_{det}"
        over = (hv.Curve((idx, f1), kdims=[xd], vdims=[yd]).opts(color="#333", line_width=1.5)
                * hv.Scatter((idx, f1), kdims=[xd], vdims=[yd]).opts(color="#333", size=4))
        if c["shipped"] in vals:
            si = vals.index(c["shipped"])
            over = over * hv.Scatter(([si], [f1[si]]), kdims=[xd], vdims=[yd]).opts(
                marker="circle", size=15, fill_alpha=0, line_color="#1f6fb2", line_width=2)
        if c["pick"]["v"] is not None:
            pi = vals.index(c["pick"]["v"])
            over = over * hv.Scatter(([pi], [f1[pi]]), kdims=[xd], vdims=[yd]).opts(
                marker="circle", size=9, color="#1a7f37")
        plots.append(over.opts(
            width=520, height=230, ylim=(0, 1), toolbar=None, show_grid=True,
            xticks=[(i, f"{v:g}") for i, v in enumerate(vals)],
            xlabel=f"{c['knob']} ({KNOB_UNITS.get(c['knob'], '')})",
            ylabel=f"B · {TITLES.get(det, det)} · F1",
            fontsize={"xticks": "8pt", "labels": "9pt"}))
    items.append(pn.pane.HoloViews(hv.Layout(plots).cols(2).opts(shared_axes=False,
                                                                 toolbar=None)))
    return _save(pn, items, dest, "figure3_simulation_and_optimization")


def main(argv=None) -> int:
    from bugarach.paths import darkroom, unresolved_message

    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--figures", nargs="+", choices=("1", "3"), default=["1", "3"])
    ap.add_argument("--sweeps", type=Path, default=None,
                    help="reuse a saved sweeps.json instead of running the sweep")
    ap.add_argument("--seeds", type=int, default=12,
                    help="simulated recordings per knob value (default 12; 3 is inside "
                         "the noise on this bench)")
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--out", type=Path, default=None,
                    help="destination directory (default: <darkroom>/coordination_intro)")
    a = ap.parse_args(argv)

    if a.out:
        dest = a.out.expanduser()
    else:
        root = darkroom(create=True)
        if root is None:
            print(unresolved_message(), file=sys.stderr)
            return 2
        dest = root / "coordination_intro"
    dest.mkdir(parents=True, exist_ok=True)

    import holoviews as hv
    import panel as pn
    hv.extension("bokeh")

    written: list[Path] = []
    if "1" in a.figures:
        written += figure1(hv, pn, dest)
    if "3" in a.figures:
        if a.sweeps:
            sweeps = json.loads(a.sweeps.read_text())
        else:
            sweeps = run_sweeps(a.seeds, a.workers)
        (dest / "sweeps.json").write_text(json.dumps(sweeps, indent=1))
        written.append(dest / "sweeps.json")
        written += figure3(hv, pn, dest, sweeps)
    for p in written:
        print("wrote", p)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
