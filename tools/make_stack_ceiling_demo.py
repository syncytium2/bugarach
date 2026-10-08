#!/usr/bin/env python3
"""An animated page for the stack ceiling: a period of a simulated recording, shifting.

    python tools/make_stack_ceiling_demo.py --also docs/learned/runs/2026-10-08-stack-ceiling

Tony, 2026-10-08: *"what is the tallest stack of width w we can create from circular shifting
events over period p?"*, then *"make this visual ... use a simulated data set and show it
shifting with the analysis"*. The measure is ``bugarach.detectors.stack_ceiling``; this draws it.

Two simulated recordings, both the bench's own (``bench.BENCH_RECORDING`` at the busy baseline
background, shortened to 15 minutes): one with six planted events and no decoys, one with a
stretch of raised rate and nothing planted (``bench.ELEVATED_RATE_RECORDING``, the stretch moved
to fit). ADR-0009 keeps those two apart, so the page does too.

The page animates in the browser, so it computes the height, the ceiling and the growth curve
itself. **This tool holds the page to the Python module before it writes anything**: it loads
the page headless, reads back what the page computed at every moment of both recordings and at
every preset moment, and refuses on any difference. The picture it saves is the first preset
moment partway through the shift.

Simulated recordings only, so the page can be committed (``--also``).
"""

from __future__ import annotations

import argparse
import json
import shutil
import sys
import tempfile
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from bugarach import bench, simulate  # noqa: E402
from bugarach.detectors.stack_ceiling import (  # noqa: E402
    MINIMUM_ROIS, call_moments, expected_height, rebuild_cost, stack_ceiling)
from bugarach.paths import darkroom  # noqa: E402

TEMPLATE = Path(__file__).with_name("stack_ceiling_demo.template.html")
NAME = "explainer_stack-ceiling_20261008"      # tools/naming/artifact_name.py build
FOLDER = "2026-10-08-stack-ceiling"

DURATION_SEC = 900.0
WIDTH_SEC, PERIOD_SEC = 2.0, 120.0
WIDTHS_SEC = (0.3, 0.5, 1.0, 2.0)              # stack's widths
PERIODS_SEC = (60.0, 120.0, 240.0)
STRETCH = (420.0, 660.0)
CLEAR_OF_EVENTS_SEC = 10.0
CHECK_RADII_SEC = (0.15, 1.0, 5.0, 20.0, 60.0)
SEED = 7
STRIDE = 5
THRESHOLDS = {"rebuild": 10.0, "fill": 0.4}
"""Where the page's two settings start. Picked by eye on seeds 7 to 10 of these two recordings,
so they are a starting point for the sliders and nothing more."""
MERGE_GAP_SEC = 0.5                             # stack's merge gap on the fast stream
MATCH_SEC = 2.5                                 # make_stack_rasters.py's matching tolerance


def scored(rec, r, score: np.ndarray, threshold: float) -> dict:
    """The calls at one setting, and the page's own light verdict on them: a planted event is
    found when a call lies within ``MATCH_SEC`` of it, and a call with no planted event that
    near is false. This is not the bench's scorer."""
    calls = call_moments(r, score, threshold, merge_gap_sec=MERGE_GAP_SEC)
    ev = np.array([e["time_sec"] for e in rec["events"]])
    near = ((ev[None, :] >= calls[:, :1] - MATCH_SEC) & (ev[None, :] <= calls[:, 1:2] + MATCH_SEC)
            if ev.size and len(calls) else np.zeros((len(calls), ev.size), bool))
    return dict(calls=calls, found=int(near.any(axis=0).sum()), planted=int(ev.size),
                false=int((~near.any(axis=1)).sum()))


def recordings():
    base = dict(bench.BENCH_RECORDING)
    base.update(bench.REGIMES["baseline_busy"])
    base.update(duration_sec=DURATION_SEC, n_distractors=0, distractor_window=None)
    planted = dict(base, n_per_level=(2, 2, 2), min_sep_sec=90.0)
    raised = dict(base)
    raised.update(bench.ELEVATED_RATE_RECORDING)
    raised.update(hot_window=STRETCH)
    out = []
    for key, kw, caption in (
            ("planted", planted,
             "The recording with six planted events; the top lane points down at each."),
            ("raised", raised,
             "The recording with nothing planted and a stretch where every ROI's rate is "
             "raised, hashed in the top lane.")):
        s, gt = simulate.simulate_coordination(seed=SEED, **kw)
        trains = [np.sort(np.asarray(v, float)) for v in s.streams["events"].locs]
        out.append(dict(
            key=key, caption=caption, duration_sec=DURATION_SEC, trains=trains,
            events=[dict(time_sec=float(e.time), n_rois=int(e.n_part)) for e in gt.events],
            stretch=list(STRETCH) if kw.get("hot_window") else None,
            hot_rate_hz=float(kw.get("hot_rate_hz") or 0.0), bg_rate_hz=float(kw["bg_rate_hz"])))
    return out


def centres(dt: float) -> np.ndarray:
    """Every moment the page can show: half a frame off the onset grid, so no window edge lands
    on an onset."""
    return (np.arange(int(DURATION_SEC / dt)) + 0.5) * dt


def scenes(recs, dt: float) -> list[dict]:
    c = centres(dt)
    planted, raised = recs
    r = stack_ceiling(planted["trains"], c, width_sec=WIDTH_SEC, period_sec=PERIOD_SEC)
    out = []
    by_size = sorted(planted["events"], key=lambda e: (-e["n_rois"], e["time_sec"]))
    seen = set()
    for e in by_size:
        if e["n_rois"] in seen:
            continue
        seen.add(e["n_rois"])
        near = np.abs(c - e["time_sec"]) <= WIDTH_SEC / 2
        t = float(c[near][np.argmax(r.height[near])])
        out.append(dict(recording=0, time_sec=t,
                        label=f"planted event, {e['n_rois']} ROIs"))
    times = np.array([e["time_sec"] for e in planted["events"]])
    clear = np.abs(c[:, None] - times[None, :]).min(axis=1) > CLEAR_OF_EVENTS_SEC
    k = int(np.argmax(np.where(clear, r.fill, -1.0)))
    out.append(dict(recording=0, time_sec=float(c[k]), label="background, where fill is highest"))
    q = stack_ceiling(raised["trains"], c, width_sec=WIDTH_SEC, period_sec=PERIOD_SEC)
    inside = (c >= STRETCH[0]) & (c <= STRETCH[1])
    k = int(np.argmax(np.where(inside, q.fill, -1.0)))
    out.append(dict(recording=1, time_sec=float(c[k]),
                    label="raised-rate stretch, where fill is highest"))
    return out


def build(recs, scs, dt: float) -> str:
    planted = recs[0]
    data = dict(
        frame_interval_sec=dt, width_sec=WIDTH_SEC, period_sec=PERIOD_SEC,
        widths_sec=list(WIDTHS_SEC), periods_sec=list(PERIODS_SEC),
        check_radii_sec=list(CHECK_RADII_SEC), scenes=scs,
        stride=STRIDE, thresholds=THRESHOLDS, min_rois=MINIMUM_ROIS,
        merge_gap_sec=MERGE_GAP_SEC, match_sec=MATCH_SEC,
        recordings=[dict(caption=r["caption"], duration_sec=r["duration_sec"],
                         trains=[np.round(t, 4).tolist() for t in r["trains"]],
                         events=r["events"], stretch=r["stretch"]) for r in recs],
        footnote=(
            f"Both recordings are simulated by the bench's generator (seed {SEED}): "
            f"{len(planted['trains'])} ROIs, {DURATION_SEC / 60:.0f} minutes, the busy baseline "
            f"background of {planted['bg_rate_hz']} Hz per ROI, onsets on a "
            f"{dt:g} s frame grid. The planted events hold "
            + ", ".join(str(e["n_rois"]) for e in planted["events"])
            + f" ROIs. The raised-rate stretch runs from {STRETCH[0]:.0f} s to {STRETCH[1]:.0f} s "
            f"at up to {recs[1]['hot_rate_hz']} Hz per ROI. Moments sit half a frame off the grid, "
            "so a window edge never lands on an onset. Built by tools/make_stack_ceiling_demo.py, "
            "which checks every number this page computes against "
            "bugarach.detectors.stack_ceiling before writing it."))
    return TEMPLATE.read_text().replace("/*DATA*/null", json.dumps(data, separators=(",", ":")))


def reference(recs, scs, dt: float) -> list[dict]:
    """What the page must compute, from the Python module."""
    c = centres(dt)
    out = []
    for i, r in enumerate(recs):
        whole = stack_ceiling(r["trains"], c, width_sec=WIDTH_SEC, period_sec=PERIOD_SEC)
        at = []
        for s in scs:
            if s["recording"] != i:
                continue
            m = stack_ceiling(r["trains"], [s["time_sec"]], width_sec=WIDTH_SEC,
                              period_sec=PERIOD_SEC)
            need = np.sort(m.shift_needed[0])
            at.append(dict(
                needs=need[np.isfinite(need)].tolist(), half=float(m.half_shift_sec[0]),
                expected=expected_height(r["trains"], s["time_sec"], period_sec=PERIOD_SEC,
                                         radii_sec=CHECK_RADII_SEC).tolist()))
        cost = rebuild_cost(whole, stride=STRIDE)
        score = {"rebuild": cost, "fill": whole.fill}
        out.append(dict(
            height=whole.height.tolist(), ceiling=whole.ceiling.tolist(), rebuild=cost.tolist(),
            calls={k: scored(r, whole, score[k], THRESHOLDS[k])["calls"].tolist()
                   for k in THRESHOLDS},
            scenes=at, whole=whole, score=score))
    return out


def check_and_shoot(html: Path, png: Path, want: list[dict], shift_sec: float) -> None:
    from playwright.sync_api import sync_playwright

    with sync_playwright() as pw:
        browser = pw.chromium.launch()
        page = browser.new_page(viewport={"width": 1160, "height": 900}, device_scale_factor=2)
        errors = []
        page.on("pageerror", lambda e: errors.append(str(e)))
        page.goto(html.resolve().as_uri())
        got = page.evaluate("window.__check()")
        if errors:
            raise SystemExit(f"the page raised: {errors}")
        for i, (g, w) in enumerate(zip(got, want, strict=True)):
            for key in ("height", "ceiling"):
                if g[key] != w[key]:
                    bad = int(np.flatnonzero(np.asarray(g[key]) != np.asarray(w[key]))[0])
                    raise SystemExit(f"recording {i}: the page's {key} differs from "
                                     f"stack_ceiling at moment {bad}")
            if not np.allclose(g["rebuild"], w["rebuild"], atol=1e-9):
                raise SystemExit(f"recording {i}: the page's rebuild cost differs from the module")
            for key, rows in w["calls"].items():
                if np.shape(g["calls"][key]) != np.shape(rows) or not np.allclose(
                        np.asarray(g["calls"][key], float).reshape(-1, 3),
                        np.asarray(rows, float).reshape(-1, 3), atol=1e-9):
                    raise SystemExit(f"recording {i}: the page's {key} calls differ from the module")
            for gs, ws in zip(g["scenes"], w["scenes"], strict=True):
                for key in ("needs", "expected"):
                    if not np.allclose(gs[key], ws[key], atol=1e-9):
                        raise SystemExit(f"recording {i}: the page's {key} differ from the module")
                if not np.isclose(gs["half"], ws["half"], atol=1e-9):
                    raise SystemExit(f"recording {i}: half-ceiling shift differs")
        page.evaluate(f"window.__set(0, {shift_sec})")
        page.screenshot(path=str(png), full_page=True)
        browser.close()


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--out", type=Path, default=None,
                    help=f"folder for the page (default: the darkroom's {FOLDER}/)")
    ap.add_argument("--also", type=Path, default=None, help="a second folder for the page")
    a = ap.parse_args(argv)
    out = a.out or darkroom(FOLDER, create=True)
    if out is None:
        raise SystemExit("no darkroom found: pass --out")
    out.mkdir(parents=True, exist_ok=True)

    dt = float(bench.BENCH_RECORDING.get("grid_sec", 0.1))
    recs = recordings()
    scs = scenes(recs, dt)
    html_text = build(recs, scs, dt)
    want = reference(recs, scs, dt)
    with tempfile.TemporaryDirectory() as td:
        html, png = Path(td) / f"{NAME}.html", Path(td) / f"{NAME}.png"
        html.write_text(html_text)
        first = want[scs[0]["recording"]]["scenes"][0]
        needs = np.asarray(first["needs"])
        midway = needs[(int((needs == 0).sum()) + needs.size) // 2]   # half the gap to the ceiling
        check_and_shoot(html, png, want, shift_sec=round(float(midway), 1))
        for dest in filter(None, (out, a.also)):
            dest.mkdir(parents=True, exist_ok=True)
            for f in (html, png):
                shutil.copy2(f, dest / f.name)
                print(dest / f.name)

    c = centres(dt)
    print("\nmoment                                        height  ceiling  fill  rebuild cost")
    for s in scs:
        w = want[s["recording"]]
        k = int(np.argmin(np.abs(c - s["time_sec"])))
        print(f"{s['label']:<44}  {int(w['whole'].height[k]):>2} ROIs  "
              f"{int(w['whole'].ceiling[k]):>2} ROIs  {w['whole'].fill[k]:.2f}  "
              f"{w['score']['rebuild'][k]:.1f} s")
    print("\nrule                      recording  calls  planted found  false calls")
    for key, label in (("rebuild", f"rebuild cost >= {THRESHOLDS['rebuild']:g} s"),
                       ("fill", f"fill >= {THRESHOLDS['fill']:g}")):
        for r, w in zip(recs, want):
            v = scored(r, w["whole"], w["score"][key], THRESHOLDS[key])
            print(f"{label:<24}  {r['key']:<9}  {len(v['calls']):>5}  "
                  f"{v['found']} of {v['planted']:<8}  {v['false']}")


if __name__ == "__main__":
    main()
