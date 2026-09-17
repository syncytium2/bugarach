#!/usr/bin/env python3
"""Sliding LoCo and CoactDetect against their binned ports, on real baseline windows.

    python tools/compare_sliding_vs_binned.py --jobs 12
    python tools/compare_sliding_vs_binned.py --tolerances 0.5 2.5 --no-figures

**The question.** ``docs/forks.md`` §14 changed how LoCo and CoactDetect count: a window
that slides with the data instead of a grid laid from the start of the recording, and a
null computed exactly instead of drawn. On bench recordings that is measured against
planted truth. **On real recordings there is no answer key**, so the only honest question
is how far the two modes disagree — and a large disagreement is a finding to explain
before the sliding mode ships, not a detail.

**What it runs.** Both detectors, both modes, at
``bench.OPERATING_POINTS`` (⚠ values tuned for the BINNED mode: the sliding operating
points are what goal 1's search is choosing, so read this as *these settings in two
modes*, never as *the calibrated sliding detector*). One recording at a time, on
:data:`~bugarach.bench.MEASURED_STREAM`, inside each recording's **baseline analysis
window** — the window ``regions.csv`` says to score, via
:func:`bugarach.assess_folder.generation_window`. Baseline only (FOUNDATIONS §9), and
only the folder the program allows (:data:`~bugarach.bench.MEASURED_ROLE`).

**What it reports.** Per recording and per detector: calls in each mode, calls per hour,
and how many calls of each mode have a call of the other within a tolerance — both
directions, because they answer different questions. *Recovered* is the fraction of binned
calls a sliding run also makes; *new* is the fraction of sliding calls the binned run does
not.

**Where the output goes.** The darkroom, because it is derived from real recordings
(FOUNDATIONS §5) and carries recording ids. The summary printed at the end carries none,
and is what a repo-side note may quote.
"""

from __future__ import annotations

import argparse
import dataclasses
import datetime as _dt
import json
import sys
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np

REPO = Path(__file__).resolve().parents[1]
if str(REPO / "src") not in sys.path:
    sys.path.insert(0, str(REPO / "src"))

DETECTORS = ("loco", "coact")
MODES = ("binned", "sliding")


def _window_slice(s, stream):
    """The recording reduced to one stream inside its baseline analysis window.

    Events are re-zeroed and the regions dropped, so every detector sees one implicit
    whole-recording window (FOUNDATIONS §4) that IS the baseline analysis window. Leaving
    the regions on would run the detectors over the treatments too, which FOUNDATIONS §9
    does not allow as a source of coordination properties.
    """
    from bugarach import bench
    from bugarach.assess_folder import NoBaselineRegion, generation_window

    try:
        window, _ = generation_window(s)
    except NoBaselineRegion as e:
        return None, str(e)
    if window is None:
        return None, "no regions declared, so no baseline window"
    lo, hi = window
    st = s.streams[stream]
    kw = {}
    for f in ("locs", "t50rise", "peak"):
        v = getattr(st, f, None)
        if v is None:
            continue
        kw[f] = [np.sort(np.asarray(a, float)[(np.asarray(a, float) >= lo)
                                              & (np.asarray(a, float) < hi)]) - lo
                 for a in v]
    for f in ("width", "amp"):
        v = getattr(st, f, None)
        if v is None:
            continue
        kw[f] = [np.asarray(w, float)[(np.asarray(t, float) >= lo) & (np.asarray(t, float) < hi)]
                 for w, t in zip(v, (st.t50rise or st.locs))]
    inner = dataclasses.replace(st, **kw)
    return dataclasses.replace(s, streams={bench.STREAM: inner}, regions=[]), (hi - lo)


def _calls(sl, detector, mode):
    """Onsets (s) of one detector's calls in one window mode."""
    from bugarach import bench
    from bugarach.detectors.coact import coact_detect
    from bugarach.detectors.loco import loco_detect
    from bugarach.detectors.rate import recording_extent, stream_trains

    params = dict(bench.OPERATING_POINTS[detector].params)
    params["window_mode"] = mode
    if detector == "loco":
        out = loco_detect(sl, **params).streams[bench.STREAM]
    else:
        ext = recording_extent(sl)
        trains = stream_trains(sl.streams[bench.STREAM], ext)
        out = coact_detect(trains, ext, **params)
    return np.asarray(out.onset_sec, dtype=float)


def _matched(a, b, tol):
    """Fraction of ``a``'s calls with a call of ``b`` within ``tol`` seconds."""
    if a.size == 0:
        return float("nan")
    if b.size == 0:
        return 0.0
    return float(np.mean([np.min(np.abs(b - t)) <= tol for t in a]))


def _one(args):
    """One recording, both detectors, both modes. Top-level, so Windows can spawn it."""
    folder, index, stream, tolerances = args
    from bugarach.io import load_folder

    s = load_folder(Path(folder))[index]
    row = {"slice_id": s.slice_id, "skipped": None}
    if stream not in s.streams:
        row["skipped"] = f"no {stream!r} stream"
        return row
    sl, dur = _window_slice(s, stream)
    if sl is None:
        row["skipped"] = dur
        return row
    row["window_sec"] = float(dur)
    row["n_roi"] = int(sl.streams[list(sl.streams)[0]].n_rois)
    row["n_events"] = int(sum(len(a) for a in (sl.streams[list(sl.streams)[0]].t50rise
                                               or sl.streams[list(sl.streams)[0]].locs)))
    widest = max(tolerances)
    for det in DETECTORS:
        calls = {m: _calls(sl, det, m) for m in MODES}
        # Where a binned call and a sliding call are the same call, how far apart are the
        # two onsets? Binned CoactDetect reported a BIN EDGE and sliding reports the first
        # participating event (docs/forks.md §14), so a mode change moves the onset without
        # changing which moment was found. Signed, sliding minus binned.
        shifts = []
        if calls["binned"].size and calls["sliding"].size:
            for t in calls["binned"]:
                d = calls["sliding"] - t
                j = int(np.argmin(np.abs(d)))
                if abs(d[j]) <= widest:
                    shifts.append(float(d[j]))
        row[det] = {
            "calls": {m: int(c.size) for m, c in calls.items()},
            "calls_per_hour": {m: float(c.size / (dur / 3600.0)) for m, c in calls.items()},
            "recovered": {f"{t}": _matched(calls["binned"], calls["sliding"], t) for t in tolerances},
            "new": {f"{t}": float(1.0 - _matched(calls["sliding"], calls["binned"], t))
                    for t in tolerances},
            "onset_shift_sec": {
                "n": len(shifts),
                "median": float(np.median(shifts)) if shifts else float("nan"),
                "median_abs": float(np.median(np.abs(shifts))) if shifts else float("nan"),
            },
        }
    return row


NAMES = {"loco": "LoCo", "coact": "CoactDetect"}


def _figures(rows, tolerances, out_dir):
    """Figures 1 and 2: calls per recording, and how much of the binned call list survives.

    Drawn with this project's own stack — holoviews through bokeh, flattened to a PNG by
    `make_diagnostic._render_png` — because matplotlib is not a declared dependency of
    this repo (`pyproject.toml` has no entry for it, though two older figure tools import
    it anyway).

    Conventions, from CLAUDE.md: no titles, identity and counts in the axis labels, every
    number with its unit, and the figure number in the label of each panel, since a PNG
    carries no caption of its own.
    """
    import holoviews as hv

    sys.path.insert(0, str(REPO / "tools"))
    from make_diagnostic import _render_png

    hv.extension("bokeh")
    panels = []
    for det in DETECTORS:
        b = np.array([r[det]["calls"]["binned"] for r in rows], float)
        s = np.array([r[det]["calls"]["sliding"] for r in rows], float)
        hi = float(max(1.0, b.max(), s.max())) * 1.05
        unity = hv.Curve([(0, 0), (hi, hi)]).opts(color="#999999", line_width=1)
        pts = hv.Points((b, s)).opts(size=7, color="#222222", alpha=0.75)
        panels.append((unity * pts).opts(
            width=460, height=380, xlim=(-0.02 * hi, hi), ylim=(-0.02 * hi, hi),
            shared_axes=False, toolbar=None,
            xlabel=f"{NAMES[det]} binned · calls",
            ylabel=f"Figure 1 · {NAMES[det]} sliding · calls ({len(rows)} recordings)"))
    for det in DETECTORS:
        overlay = []
        for t, colour in zip(tolerances, ("#222222", "#8c8c8c")):
            v = np.array([r[det]["recovered"][f"{t}"] for r in rows], float)
            v = v[np.isfinite(v)]
            counts, edges = np.histogram(v, bins=np.linspace(0, 1, 21))
            overlay.append(hv.Histogram((edges, counts)).opts(
                fill_alpha=0.0, line_color=colour, line_width=2))
        panels.append(hv.Overlay(overlay).opts(
            width=460, height=380, xlim=(0.0, 1.0), shared_axes=False, toolbar=None,
            xlabel=f"{NAMES[det]} · fraction of binned calls also made sliding",
            ylabel=f"Figure 2 · recordings ({len(rows)}; dark {tolerances[0]} s, "
                   f"light {tolerances[-1]} s)"))

    out_dir = Path(out_dir)
    html = out_dir / "sliding_vs_binned.html"
    layout = hv.Layout(panels).cols(2).opts(shared_axes=False, toolbar=None)
    hv.save(layout, str(html), backend="bokeh")
    png = out_dir / "sliding_vs_binned.png"
    if _render_png(html, png):
        return png
    print("(no PNG: needs playwright chromium; the HTML is there)", file=sys.stderr)
    return html


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--role", default=None,
                   help="current_export.toml role (default: the folder the bench is measured on)")
    p.add_argument("--jobs", type=int, default=1)
    p.add_argument("--limit", type=int, default=None, help="first N recordings only")
    p.add_argument("--tolerances", type=float, nargs="+", default=[0.5, 2.5],
                   help="seconds within which a call of one mode counts as a call of the other. "
                        "2.5 s is score.TOL_SEC, what the bench scores at")
    p.add_argument("--out", default=None,
                   help="output directory (default: <darkroom>/bugarach/<today>-sliding-vs-binned)")
    p.add_argument("--no-figures", action="store_true")
    a = p.parse_args(argv)

    from bugarach import bench, dataset, paths
    from bugarach.io import load_folder

    role = a.role or bench.MEASURED_ROLE
    folder = dataset.current(role)
    stream = bench.MEASURED_STREAM
    n = len(load_folder(folder))
    if a.limit:
        n = min(n, a.limit)
    out_dir = Path(a.out) if a.out else (paths.darkroom()
                                         / f"{_dt.date.today().isoformat()}-sliding-vs-binned")
    out_dir.mkdir(parents=True, exist_ok=True)
    print(f"role {role!r} -> {dataset.current_name(role)}, stream {stream!r}, "
          f"baseline analysis windows, {n} recordings")
    print(f"out {out_dir}")

    tasks = [(str(folder), i, stream, a.tolerances) for i in range(n)]
    if a.jobs > 1:
        with ProcessPoolExecutor(max_workers=a.jobs) as ex:
            rows = list(ex.map(_one, tasks))
    else:
        rows = [_one(t) for t in tasks]
    skipped = {r["slice_id"]: r["skipped"] for r in rows if r["skipped"]}
    rows = [r for r in rows if not r["skipped"]]
    print(f"{len(rows)} recordings compared, {len(skipped)} skipped")

    names = {"loco": "LoCo", "coact": "CoactDetect"}
    summary = {}
    for det in DETECTORS:
        b = np.array([r[det]["calls"]["binned"] for r in rows], float)
        s = np.array([r[det]["calls"]["sliding"] for r in rows], float)
        bh = np.array([r[det]["calls_per_hour"]["binned"] for r in rows], float)
        sh = np.array([r[det]["calls_per_hour"]["sliding"] for r in rows], float)
        summary[det] = {
            "calls_total": {"binned": int(b.sum()), "sliding": int(s.sum())},
            "calls_per_hour_median": {"binned": float(np.median(bh)), "sliding": float(np.median(sh))},
            "recordings_with_more_calls_sliding": int((s > b).sum()),
            "recordings_with_fewer_calls_sliding": int((s < b).sum()),
            "recovered_median": {f"{t}": float(np.nanmedian(
                [r[det]["recovered"][f"{t}"] for r in rows])) for t in a.tolerances},
            "new_median": {f"{t}": float(np.nanmedian(
                [r[det]["new"][f"{t}"] for r in rows])) for t in a.tolerances},
            "onset_shift_sec_median": float(np.nanmedian(
                [r[det]["onset_shift_sec"]["median"] for r in rows])),
            "onset_shift_sec_median_abs": float(np.nanmedian(
                [r[det]["onset_shift_sec"]["median_abs"] for r in rows])),
        }
        d = summary[det]
        print(f"\n{names[det]}: {d['calls_total']['binned']} calls binned, "
              f"{d['calls_total']['sliding']} sliding "
              f"(median {d['calls_per_hour_median']['binned']:.1f} and "
              f"{d['calls_per_hour_median']['sliding']:.1f} calls per hour); "
              f"sliding calls more in {d['recordings_with_more_calls_sliding']} recordings, "
              f"fewer in {d['recordings_with_fewer_calls_sliding']}")
        for t in a.tolerances:
            print(f"   within {t} s: median {d['recovered_median'][f'{t}']:.2f} of binned calls "
                  f"recovered, median {d['new_median'][f'{t}']:.2f} of sliding calls new")
        print(f"   where a call is the same call, its onset moves a median "
              f"{d['onset_shift_sec_median']:+.2f} s (median absolute "
              f"{d['onset_shift_sec_median_abs']:.2f} s), sliding minus binned")

    record = {
        "role": role, "folder": dataset.current_name(role), "stream": stream,
        "window": "baseline analysis window (assess_folder.generation_window)",
        "operating_points": {d: {k: v for k, v in bench.OPERATING_POINTS[d].params.items()}
                             for d in DETECTORS},
        "operating_point_caveat": "values tuned for the binned mode; the sliding points are "
                                  "what goal 1's search is choosing",
        "tolerances_sec": list(a.tolerances),
        "measured_on": _dt.date.today().isoformat(),
        "skipped": skipped, "summary": summary, "rows": rows,
    }
    (out_dir / "sliding_vs_binned.json").write_text(
        json.dumps(record, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    print(f"\nwrote {out_dir / 'sliding_vs_binned.json'}")
    if not a.no_figures:
        print(f"wrote {_figures(rows, a.tolerances, out_dir)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
