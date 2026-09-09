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

FACETED BY EXPERIMENTAL GROUP, AND ON THIS CORPUS THAT IS NOT A PREFERENCE.
FOUNDATIONS §9: effects run in OPPOSITE DIRECTIONS by group — ORX up, male
unchanged, diestrus down under TTX — so a panel pooling them hides a sign change
and is not admissible on its own. ``--facet group`` puts one group per column and
is the default whenever the folder's `slices.csv` carries `group_id`; each panel is
then a standard fireflies before/after over that group's recordings.

ONE PAGE PER DETECTOR (``--per-detector``). Twelve detectors x two streams x four
groups does not fit one page legibly, and stacking them invites reading down a
column as though it were a ranking — which is the thing `performance_table.md`
declines to do. Each page carries one detector's claim, its own y-scale, and the
same facet grid, so pages can be flipped against each other.

Y-AXES: shared ACROSS the group facets of one stream, never across streams and
never across detectors. Groups are the comparison the facets exist to allow, so
they need one scale; fast and slow are different measurements, and two detectors'
rates are two different instruments' units.

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
                 "tube": "tube (learned)", "tube_guard": "tube_guard",
                 "tube_ratio": "tube_ratio", "tube_ratio_guard": "tube_ratio_guard",
                 "trace": "pooled trace", "tiny": "shared per-ROI filter",
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


def counts(*detections: Path):
    """(slice_id, stream, detector, region_idx) -> calls; and the set of detectors that ran."""
    n = defaultdict(int)
    order: list[str] = []
    for path in detections:
        for r in read_detections(path):
            if r["detector"] not in order:
                order.append(r["detector"])
            if r.get("region_idx") is None:
                continue                 # in no declared period: counted nowhere
            n[(r["slice_id"], str(r["stream"]).strip().lower(),
               r["detector"], int(r["region_idx"]))] += 1
    return n, order


def groups_of(folder: Path) -> dict[str, str]:
    """slice_id -> group_id, from the folder's own `slices.csv`.

    The producer's column, carried unchanged. Recordings whose folder does not
    declare a group come back under ``""`` and are drawn in one unlabelled facet
    rather than being dropped — a missing group is a fact about the folder, and
    silently discarding those recordings would shrink an n nobody was told about.
    """
    out: dict[str, str] = {}
    f = Path(folder) / "slices.csv"
    if not f.is_file():
        return out
    with f.open(newline="") as fh:
        for r in csv.DictReader(fh):
            out[str(r.get("slice_id", "")).strip()] = str(r.get("group_id") or "").strip()
    return out


def rates(folder: Path, *detections: Path, baseline: str, treatment: str):
    wins = windows(folder)
    n, ran = counts(*detections)
    grp = groups_of(folder)
    slices = sorted({sid for sid, _ in wins})
    streams = sorted({s for _, s, _, _ in n}) or ["fast", "slow"]
    # The glossary's order for the six, then arrival for anything else — a learned
    # model, or a detector from outside this project. A table that reordered itself
    # because a second file was passed would make two runs incomparable by eye.
    detectors = ([d for d in DETECTORS if d in ran]
                 + [d for d in ran if d not in DETECTORS]) or list(DETECTORS)
    # (detector, stream, slice, group, baseline_rate, treatment_rate,
    #  baseline_calls, treatment_calls)
    rows = []
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
                rows.append((d, s, sid, grp.get(sid, ""),
                             nb / wins[b][1], nt / wins[t][1], nb, nt))
    return rows, detectors, streams, missing


#: One colour per recording, keyed in the header in its own colour. Okabe–Ito, which
#: stays distinct under the common colour-vision deficiencies; six recordings is what
#: this cohort has, and a seventh would cycle.
RECORDING_INKS = ("#0072B2", "#D55E00", "#009E73", "#CC79A7", "#E69F00", "#56B4E9", "#000000")


def recording_inks(rows):
    return {sid: RECORDING_INKS[i % len(RECORDING_INKS)]
            for i, sid in enumerate(sorted({r[2] for r in rows}))}


#: One ink per experimental group. Okabe–Ito again, and the ink is the FACET's
#: identity rather than any recording's: with 29–38 recordings a per-recording key
#: is unreadable, so identity moves to the sidecar CSV, which carries every
#: recording's id, group and both counts.
GROUP_INKS = ("#0072B2", "#D55E00", "#009E73", "#CC79A7", "#E69F00", "#56B4E9", "#000000")


def group_inks(groups):
    return {g: GROUP_INKS[i % len(GROUP_INKS)] for i, g in enumerate(groups)}


def facet_groups(rows) -> list[str]:
    """The groups present, named ones first and the unlabelled facet last."""
    gs = sorted({r[3] for r in rows})
    return [g for g in gs if g] + ([""] if "" in gs else [])


def dot_size(calls: int) -> float:
    """Dot area grows with the number of calls behind the rate, so a one-call
    endpoint is visibly one call. Keyed in the header."""
    return 4.0 + 2.6 * math.sqrt(calls)


def build_faceted(rows, detector, streams, groups, baseline, treatment, *,
                  width=330, height=300):
    """One detector's page: rows are streams, columns are experimental groups.

    **Y is shared across the group facets of one stream and never beyond it.**
    Comparing groups is the entire reason the facets exist, and facets on
    different scales cannot be compared by eye — so the row shares one range. It
    stops at the row: fast and slow are different measurements (GLOSSARY), and
    another detector's rate is another instrument's unit.

    Nothing is drawn over the data. Each panel is a plain before/after — paired
    points joined per recording — and its identity (group, stream, n) lives in the
    y-axis label, which is where this project puts identity.
    """
    import holoviews as hv
    hv.extension("bokeh")

    inks = group_inks(groups)
    letters = iter("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz")
    panels = []
    for s in streams:
        row_rows = [r for r in rows if r[0] == detector and r[1] == s]
        # One range for the whole stream row, computed before any panel is drawn.
        ymax = max([max(r[4], r[5]) for r in row_rows] or [0.0]) * 1.15 or 1.0
        for g in groups:
            sub = [r for r in row_rows if r[3] == g]
            letter = next(letters)
            ink = inks[g]
            els = []
            for _, _, sid, _, b, t, nb, nt in sub:
                els.append(hv.Curve([(baseline, b), (treatment, t)],
                                    kdims=["period"], vdims=[f"rate_{s}"]
                                    ).opts(color=ink, line_width=1.4, alpha=0.7))
                for x, v, nn in ((baseline, b, nb), (treatment, t, nt)):
                    # Hollow means NO calls at all. Filled-but-tiny reads as one
                    # call, and "none" and "one" are the difference between a
                    # detector that was silent and one that fired once.
                    els.append(hv.Scatter([(x, v)], kdims=["period"],
                                          vdims=[f"rate_{s}"]
                                          ).opts(color=("white" if nn == 0 else ink),
                                                 line_color=ink, line_width=1.3,
                                                 size=dot_size(nn), alpha=0.9))
            ov = (hv.Overlay(els) if els
                  else hv.Curve([], kdims=["period"], vdims=[f"rate_{s}"]))
            ov = ov.opts(width=width, height=height, toolbar=None,
                         show_legend=False,
                         ylabel=f"{letter} · {g or 'no group'} · {s} · "
                                f"{len(sub)} rec · events/min",
                         xlabel="period", padding=(0.25, 0.1),
                         ylim=(-0.05 * ymax, ymax))
            panels.append(ov)
    return hv.Layout(panels).cols(len(groups)).opts(shared_axes=False, toolbar=None)


def build(rows, detectors, streams, baseline, treatment, *, width=400, height=300):
    """Panel height is set by the y-axis LABEL, not by the data.

    The label carries the panel's identity and its unit, because this project puts
    identity in the axis label and never in a title above the plot. It is rotated, so
    the plot's height is the space it has to fit in — and at 220 px eight of twelve
    panels lost their unit off the end ("... · events/m"), which a murderboard round
    caught in the render rather than in the code. Height is the fix; shortening the
    label would have cost the identity instead.
    """
    import holoviews as hv
    hv.extension("bokeh")

    inks = recording_inks(rows)
    letters = iter("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
    panels = []
    for d in detectors:
        row_rows = [r for r in rows if r[0] == d]
        ymax = max([max(r[4], r[5]) for r in row_rows] or [0.0]) * 1.15 or 1.0
        for s in streams:
            sub = [r for r in row_rows if r[1] == s]
            letter = next(letters)
            els = []
            for _, _, sid, _, b, t, nb, nt in sub:
                els.append(hv.Curve([(baseline, b), (treatment, t)], kdims=["period"],
                                    vdims=[f"rate_{d}_{s}"]).opts(color=inks[sid], line_width=1.6, alpha=0.85))
                for x, v, n in ((baseline, b, nb), (treatment, t, nt)):
                    # A period with no calls at all is drawn hollow. Filled-but-tiny read
                    # as one call, and "none" and "one" are the difference between a
                    # detector that was silent and one that fired once.
                    fill = "white" if n == 0 else inks[sid]
                    els.append(hv.Scatter([(x, v)], kdims=["period"], vdims=[f"rate_{d}_{s}"]
                                          ).opts(color=fill, line_color=inks[sid], line_width=1.5,
                                                 size=dot_size(n), alpha=0.9))
            ov = hv.Overlay(els) if els else hv.Curve([], kdims=["period"], vdims=[f"rate_{d}_{s}"])
            ov = ov.opts(width=width, height=height, toolbar=None, show_legend=False,
                         ylabel=f"{letter} · {DETECTOR_NAME.get(d, d)} · {s} · events/min",
                         xlabel="period", padding=(0.25, 0.1), ylim=(-0.05 * ymax, ymax))
            panels.append(ov)
    return hv.Layout(panels).cols(len(streams)).opts(shared_axes=False, toolbar=None)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--detections", required=True, nargs="+", type=Path,
                    help="one or more detections.csv in the emit contract — detect's "
                         "own, and any other run in the same shape (a learned one)")
    ap.add_argument("--folder", required=True, type=Path,
                    help="the export folder detect ran on (regions.csv, slices.csv, recordings)")
    ap.add_argument("--baseline", required=True, help="region_label of the first period")
    ap.add_argument("--treatment", required=True, help="region_label of the second period")
    ap.add_argument("--out", default=None, help="destination directory (default: the darkroom)")
    ap.add_argument("--also", default=None, help="write a second copy here")
    ap.add_argument("--stem", default="before_after_coordinated_events")
    ap.add_argument("--per-detector", action="store_true",
                    help="write ONE PAGE PER DETECTOR, faceted by experimental "
                         "group (columns) and stream (rows), instead of one page "
                         "stacking every detector. Twelve detectors x two streams "
                         "x four groups does not fit one page legibly, and "
                         "stacking them invites reading down a column as a "
                         "ranking — which is what performance_table.md declines "
                         "to do")
    ap.add_argument("--facet", choices=("group", "none"), default="group",
                    help="facet each page by the producer's group_id (default) "
                         "or not at all. FOUNDATIONS section 9: effects run in "
                         "OPPOSITE DIRECTIONS by group on this preparation, so a "
                         "pooled panel can hide a sign change and is not "
                         "admissible on its own. Only meaningful with "
                         "--per-detector")
    a = ap.parse_args(argv)

    rows, detectors, streams, missing = rates(a.folder, *a.detections,
                                              baseline=a.baseline, treatment=a.treatment)
    # A RECORDING THE DETECTIONS FILE NEVER MENTIONS IS DRAWN AT ZERO, and at
    # zero it is indistinguishable from a recording that was scored and found
    # nothing. Those are different facts — one is a detector's answer, the other
    # is a run that did not cover this recording (a `--limit`, a crash, the wrong
    # file). Nothing downstream can tell them apart, so the count is put on the
    # page rather than left for a reader to not notice.
    silent = sorted({r[2] for r in rows} - {sid for sid, _, _, _ in counts(*a.detections)[0]})
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
        + " &nbsp;·&nbsp; ".join(f"{d.parent.name}/{d.name}" for d in a.detections)
        + "</div></div>")
    if a.per_detector:
        groups = facet_groups(rows) if a.facet == "group" else [""]
        if a.facet != "group":
            # One facet holding everything: the page shape stays identical so the
            # two forms are comparable, and the pooled panel is what the caller
            # asked for rather than something inferred.
            rows = [(d, s, sid, "", b, t, nb, nt) for d, s, sid, _, b, t, nb, nt in rows]
        ginks = group_inks(groups)
        gkey = " &nbsp; ".join(
            f"<span style='display:inline-block;width:11px;height:11px;"
            f"background:{ink};vertical-align:-1px;margin-right:4px'></span>"
            f"<span style='color:{ink}'>{g or 'no group'}</span>"
            for g, ink in ginks.items())
        for d in detectors:
            name = DETECTOR_NAME.get(d, d)
            head = pn.pane.HTML(
                f"<div style='font:13px system-ui,sans-serif;color:#111;max-width:1200px'>"
                f"<b style='font-size:16px'>{name} · coordinated events per minute · "
                f"{a.baseline} → {a.treatment}</b>"
                f" &nbsp;—&nbsp; one line per recording; columns are experimental "
                f"groups, rows are streams. <b>The y-range is shared across the "
                f"group facets of a stream and nowhere else</b>: comparing groups "
                f"is what the facets are for, while fast and slow are different "
                f"measurements and another detector's rate is another "
                f"instrument's unit."
                f"<div style='margin:5px 0 0'>groups: {gkey}</div>"
                f"<div style='margin:4px 0 0;color:#444'>dot area grows with the "
                f"calls behind the rate: "
                + " &nbsp;".join(
                    f"<span style='display:inline-block;width:{dot_size(n):.0f}px;"
                    f"height:{dot_size(n):.0f}px;border-radius:50%;background:#555;"
                    f"vertical-align:middle'></span> {n}" for n in (1, 10, 50))
                + " calls &nbsp;·&nbsp; hollow = no calls at all in that period, "
                  "which is not the same as a small rate</div>"
                f"<div style='margin:5px 0 0;color:#444'>Descriptive output, not "
                f"an analysis: calls inside each period divided by the length of "
                f"the window the folder was scored on. No statistic, no ground "
                f"truth, no verdict — there IS no ground truth on a real folder, "
                f"and a mark on a real recording is a claim. Treatment effects "
                f"are analysed by fireflies, not here; group facets are shown "
                f"separately because effects run in opposite directions by group "
                f"on this preparation, so a pooled panel can hide a sign change. "
                f"{'Skipped, lacking one of the two periods: ' + ', '.join(missing) if missing else ''}</div>"
                + (f"<div style='margin:4px 0 0;color:#a00'>⚠ {len(silent)} of "
                   f"{len(silent) + len({r[2] for r in rows}) - len(silent)} "
                   f"recordings contribute no call from ANY detector in this "
                   f"file and are drawn at zero: {', '.join(silent)}. At zero "
                   f"that is indistinguishable from a detector that ran and "
                   f"found nothing — check this is a complete run.</div>"
                   if silent else "")
                + f"<div style='margin:4px 0 0;color:#777;font-size:11px'>{a.folder.name} · "
                + " &nbsp;·&nbsp; ".join(f"{p.parent.name}/{p.name}" for p in a.detections)
                + "</div></div>")
            page = pn.Column(head, pn.pane.HoloViews(
                build_faceted(rows, d, streams, groups, a.baseline, a.treatment)))
            # The capture width has to follow the facet count. At the shared
            # default a four-group page lost its fourth column with no error and
            # a PNG that looked finished; 90 px per column covers the rotated
            # y-label and the tick text beside each panel.
            _write(page, dest, f"{a.stem}__{d}", png=True,
                   viewport_width=max(1120, len(groups) * (330 + 90) + 40))
    else:
        page = pn.Column(header, pn.pane.HoloViews(build(rows, detectors, streams, a.baseline, a.treatment)))
        _write(page, dest, a.stem, png=True)

    table = dest / f"{a.stem}.csv"
    with table.open("w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["detector", "detector_name", "stream", "slice_id", "group_id",
                    f"{a.baseline}_calls", f"{a.baseline}_events_per_min",
                    f"{a.treatment}_calls", f"{a.treatment}_events_per_min"])
        for d, s, sid, g, b, t, nb, nt in rows:
            w.writerow([d, DETECTOR_NAME.get(d, d), s, sid, g,
                        nb, f"{b:.4f}", nt, f"{t:.4f}"])
    print(f"wrote {table}")
    if a.also:
        also = Path(a.also).expanduser()
        also.mkdir(parents=True, exist_ok=True)
        for f in sorted(dest.glob(f"{a.stem}*")):
            with tempfile.TemporaryDirectory() as td:
                tmp = Path(td) / f.name
                tmp.write_bytes(f.read_bytes())
                os.replace(tmp, also / f.name)
        print(f"also {also}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
