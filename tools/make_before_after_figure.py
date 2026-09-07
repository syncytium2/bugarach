#!/usr/bin/env python3
"""Coordinated events per minute, one period beside another, one line per recording.

    python tools/make_before_after_figure.py --detections RUN/detections.csv \
        --folder EXPORT_FOLDER --baseline LABEL --treatment LABEL [--out DIR] [--also DIR]

The shape is fireflies' before/after figure — paired points joined by a line per
recording, the first period on the left, the second on the right — drawn here for
the one quantity fireflies does not have: **coordinated events**, per detector. Two
columns, fast and slow, because they are different measurements and are never
merged; one row per detector, because each detector's calls are its own claim.
Panels are lettered; the two panels of a row share a y-axis so the streams can be
read against each other; each line ends in its recording's id.

WHAT IT IS AND IS NOT. It is *output*: the coordinated-event table read back per
recording and period, so a reader can judge each detector quickly
(`docs/pipeline.md`, Output). It is **not** a treatment-effect analysis — FOUNDATIONS
§9 leaves those to fireflies — so it fits nothing, tests nothing and draws no
bracket. The y value is a rate: calls the detector made inside the period, divided
by the length of the window the folder was scored on — resolved by the same
function `bugarach detect` used (`detect_folder.folder_analysis_windows`), never
re-derived here.

BOTH PERIODS ARE NAMED BY THE CALLER. The export contract reserves no baseline and
no treatment slot (`docs/export_folder_spec.md`, "region 1 is not assumed to be a
baseline"); the contrast is chosen downstream, so this tool takes `--baseline` and
`--treatment` as labels and matches them against the folder's `region_label`
verbatim. Every call carries the producer's `region_idx`, stamped by the detector
that ran in that window; this reads that column and nothing else about the period.
"""
from __future__ import annotations

import argparse
import csv
import math
import os
import sys
import tempfile
import warnings
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from bugarach import paths  # noqa: E402
from bugarach.detect_folder import DETECTORS, _region_index, folder_analysis_windows  # noqa: E402
from bugarach.emit import read_detections  # noqa: E402
from bugarach.io import load_folder  # noqa: E402

#: Display names, in the glossary's order (which is `detect_folder.DETECTORS`'s).
#: The keys are the `detector` column's strings — the output contract — and the
#: names are what every figure and table says. `cicada` is named locust: the key
#: is the contract, the name is the detector (docs/GLOSSARY.md).
DETECTOR_NAME = {"rate": "rate+context", "coact": "CoactDetect", "loco": "LoCo",
                 "sce": "binned SCE", "cicada": "locust", "sync": "SPIKE-synch"}


def windows(folder: Path):
    """(slice_id, region_idx) -> (label, scored duration in minutes), the way detect scored them."""
    out = {}
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        slices = load_folder(folder)
    for s in slices:
        _, wins = folder_analysis_windows(s)
        for w in wins:
            ri = _region_index(w)
            if ri is None:
                continue
            out[(s.slice_id, ri)] = ((w.label or "").strip(), float(w.win_dur) / 60.0)
    return out


def counts(detections: Path):
    """(slice_id, stream, detector, region_idx) -> calls; and the set of detectors that ran."""
    n = defaultdict(int)
    ran: set[str] = set()
    for r in read_detections(detections):
        ran.add(r["detector"])
        if r.get("region_idx") is None:
            continue                     # in no declared period: counted nowhere
        n[(r["slice_id"], str(r["stream"]).strip().lower(), r["detector"], int(r["region_idx"]))] += 1
    return n, ran


def rates(folder: Path, detections: Path, baseline: str, treatment: str):
    wins = windows(folder)
    n, ran = counts(detections)
    slices = sorted({sid for sid, _ in wins})
    streams = sorted({s for _, s, _, _ in n}) or ["fast", "slow"]
    detectors = [d for d in DETECTORS if d in ran] or list(DETECTORS)
    rows = []   # (detector, stream, slice, baseline_rate, treatment_rate, baseline_calls, treatment_calls)
    missing = []
    for sid in slices:
        b = next((k for k, v in wins.items() if k[0] == sid and v[0] == baseline), None)
        t = next((k for k, v in wins.items() if k[0] == sid and v[0] == treatment), None)
        if b is None or t is None:
            missing.append(sid)
            continue
        for d in detectors:
            for s in streams:
                nb, nt = n.get((sid, s, d, b[1]), 0), n.get((sid, s, d, t[1]), 0)
                rows.append((d, s, sid, nb / wins[b][1], nt / wins[t][1], nb, nt))
    return rows, detectors, streams, missing


#: One colour per recording, keyed in the header in its own colour. Okabe–Ito, which
#: stays distinct under the common colour-vision deficiencies; six recordings is what
#: this cohort has, and a seventh would cycle.
RECORDING_INKS = ("#0072B2", "#D55E00", "#009E73", "#CC79A7", "#E69F00", "#56B4E9", "#000000")


def recording_inks(rows):
    return {sid: RECORDING_INKS[i % len(RECORDING_INKS)]
            for i, sid in enumerate(sorted({r[2] for r in rows}))}


def dot_size(calls: int) -> float:
    """Dot area grows with the number of calls behind the rate, so a one-call
    endpoint is visibly one call. Keyed in the header."""
    return 4.0 + 2.6 * math.sqrt(calls)


def build(rows, detectors, streams, baseline, treatment, *, width=400, height=220):
    import holoviews as hv
    hv.extension("bokeh")

    inks = recording_inks(rows)
    letters = iter("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
    panels = []
    for d in detectors:
        row_rows = [r for r in rows if r[0] == d]
        ymax = max([max(r[3], r[4]) for r in row_rows] or [0.0]) * 1.15 or 1.0
        for s in streams:
            sub = [r for r in row_rows if r[1] == s]
            letter = next(letters)
            els = []
            for _, _, sid, b, t, nb, nt in sub:
                els.append(hv.Curve([(baseline, b), (treatment, t)], kdims=["period"],
                                    vdims=[f"rate_{d}_{s}"]).opts(color=inks[sid], line_width=1.6, alpha=0.85))
                for x, v, n in ((baseline, b, nb), (treatment, t, nt)):
                    els.append(hv.Scatter([(x, v)], kdims=["period"], vdims=[f"rate_{d}_{s}"]
                                          ).opts(color=inks[sid], size=dot_size(n), alpha=0.9))
            ov = hv.Overlay(els) if els else hv.Curve([], kdims=["period"], vdims=[f"rate_{d}_{s}"])
            ov = ov.opts(width=width, height=height, toolbar=None, show_legend=False,
                         ylabel=f"{letter} · {DETECTOR_NAME.get(d, d)} · {s} · events/min",
                         xlabel="period", padding=(0.25, 0.1), ylim=(-0.05 * ymax, ymax))
            panels.append(ov)
    return hv.Layout(panels).cols(len(streams)).opts(shared_axes=False, toolbar=None)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--detections", required=True, type=Path)
    ap.add_argument("--folder", required=True, type=Path,
                    help="the export folder detect ran on (regions.csv, slices.csv, recordings)")
    ap.add_argument("--baseline", required=True, help="region_label of the first period")
    ap.add_argument("--treatment", required=True, help="region_label of the second period")
    ap.add_argument("--out", default=None, help="destination directory (default: the darkroom)")
    ap.add_argument("--also", default=None, help="write a second copy here")
    ap.add_argument("--stem", default="before_after_coordinated_events")
    a = ap.parse_args(argv)

    rows, detectors, streams, missing = rates(a.folder, a.detections, a.baseline, a.treatment)
    if not rows:
        print(f"nothing to draw: no recording has both a {a.baseline!r} and a {a.treatment!r} period",
              file=sys.stderr)
        return 1

    if a.out:
        dest = Path(a.out).expanduser()
    else:
        root = paths.darkroom(create=True)
        if root is None:
            print(paths.unresolved_message(), file=sys.stderr)
            return 2
        dest = root / "before_after_coordinated_events"
    dest.mkdir(parents=True, exist_ok=True)

    import panel as pn
    from make_generator_figures import _write

    inks = recording_inks(rows)
    key = " &nbsp; ".join(
        f"<span style='display:inline-block;width:11px;height:11px;background:{ink};vertical-align:-1px;"
        f"margin-right:4px'></span><span style='color:{ink}'>{sid}</span>" for sid, ink in inks.items())
    header = pn.pane.HTML(
        f"<div style='font:13px system-ui,sans-serif;color:#111;max-width:900px'>"
        f"<b style='font-size:16px'>coordinated events per minute · {a.baseline} → {a.treatment}</b>"
        f" &nbsp;—&nbsp; one line per recording (n = {len(inks)}), fast beside slow, "
        f"one row per detector; the two panels of a row share a y-axis, and the y-range differs "
        f"by detector row."
        f"<div style='margin:5px 0 0'>recordings: {key}</div>"
        f"<div style='margin:4px 0 0;color:#444'>dot area grows with the calls behind the rate: "
        + " &nbsp;".join(
            f"<span style='display:inline-block;width:{dot_size(n):.0f}px;height:{dot_size(n):.0f}px;"
            f"border-radius:50%;background:#555;vertical-align:middle'></span> {n}"
            for n in (1, 10, 50)) + " calls</div>"
        f"<div style='margin:5px 0 0;color:#444'>Descriptive output, not an analysis: calls at the "
        f"shipped operating points inside each period, divided by the length of the window the folder "
        f"was scored on. No statistic, no ground truth, no verdict — a mark on a real recording is a "
        f"claim; treatment effects are analysed by fireflies, the sister project, not here. "
        f"{'Skipped, lacking one of the two periods: ' + ', '.join(missing) if missing else ''}</div>"
        f"<div style='margin:4px 0 0;color:#777;font-size:11px'>{a.folder.name} · "
        f"{a.detections.parent.name}/{a.detections.name}</div></div>")
    page = pn.Column(header, pn.pane.HoloViews(build(rows, detectors, streams, a.baseline, a.treatment)))
    _write(page, dest, a.stem, png=True)

    table = dest / f"{a.stem}.csv"
    with table.open("w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["detector", "detector_name", "stream", "slice_id",
                    f"{a.baseline}_calls", f"{a.baseline}_events_per_min",
                    f"{a.treatment}_calls", f"{a.treatment}_events_per_min"])
        for d, s, sid, b, t, nb, nt in rows:
            w.writerow([d, DETECTOR_NAME.get(d, d), s, sid, nb, f"{b:.4f}", nt, f"{t:.4f}"])
    print(f"wrote {table}")
    if a.also:
        also = Path(a.also).expanduser()
        also.mkdir(parents=True, exist_ok=True)
        for f in dest.glob(f"{a.stem}.*"):
            with tempfile.TemporaryDirectory() as td:
                tmp = Path(td) / f.name
                tmp.write_bytes(f.read_bytes())
                os.replace(tmp, also / f.name)
        print(f"also {also}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
