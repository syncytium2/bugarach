#!/usr/bin/env python3
"""Per group and per treatment: every recording a row, aligned at baseline end.

    python tools/make_group_raster_summary.py
    python tools/make_group_raster_summary.py --treatments TTX senktide high\\ K+
    python tools/make_group_raster_summary.py --folder <a flagged review copy>

One page per (group, treatment) — `MALE_TTX`, `ORX_senktide`, and so on. Each
page carries the recordings in that group whose FIRST treatment, the period right
after baseline, was that treatment — a later period never adds a recording — one
above the next, **all re-zeroed at the end of their own baseline** so the moment
the drug arrives is the same vertical line on every row and the rows can be read
against each other. Time runs negative through baseline and positive through
treatment.

**Display only. No detector is constructed and none is run.**

DRAWN THROUGH `ui.diagnostic`, WHICH IS THE POINT. A first version of this tool
drew its own raster in matplotlib, and it was unreadable — but the deeper problem
was that it was a SECOND DRAWING PATH. `make_real_detection_figure.py` says it in
terms: it has no plotting code of its own because *"every convention it must obey
is enforced where the panels are built, and a second drawing path is how those
conventions come apart."* Mine came apart exactly there: no lane for the
treatment cue, no shared time axis, a legend invented locally. So the two things
this figure needed that the module did not have were added TO the module —
`raster_panel(marked=...)` for the producer's second ink, and
`region_lane_panel` for the treatment strip — and this file builds panels and
saves them the way every other `make_*_figure.py` does.

WHY THE ALIGNMENT CHANGES WHAT YOU CAN SEE. Unaligned, the recordings start
together and drift apart: baseline runs 17 to 31 minutes depending on the day, so
the drug arrives at a different x on every row and a column of rows shares no
moment. Anchored at baseline end, every row's treatment starts at 0 — for TTX,
exactly 0 on all 38 recordings — and a change at the transition is a change you
can see down the page rather than one you have to take on trust.

THE FOLDER THIS READS IS NOT THE ANALYSIS FOLDER, AND IT MUST NOT BE. The
producer ships the field-step artifacts *removed*; `..._STEPS_EXCLUDED` is the
dataset. The flagged twin exists as a named exception for one purpose, their
words: *"seeing how the artifacts change the impression the data gives."* This
tool is that review, so it reads the flagged copy and refuses anything else — a
folder with no `field_steps_flagged.tsv` has no red to draw, and a page with no
red in it looks exactly like a corpus that never had an artifact.

THE FLAGS DO NOT COME THROUGH THE LOADER, DELIBERATELY. `io.py` recognises
`width_sec`, `width_def`, `peak_sec` and `amp` and nothing else, so
`on_field_step` and `field_step_id` are read and dropped; `store.Stream` has no
per-event flag field. Widening a structure every detector depends on is the wrong
move for a display tool, so this joins the producer's sidecar TSV on
`(slice_id, stream, roi, time_sec)` — four fields the loader already keeps.

Destination is the darkroom, resolved by `bugarach.paths`; `--also` writes a
second copy into the repo. The path is never hardcoded: it carries a person's
name and this repo is public.
"""

from __future__ import annotations

import argparse
import csv
import dataclasses
import os
import sys
import tempfile
import warnings
from collections import defaultdict
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from bugarach import paths  # noqa: E402
from bugarach.io import load_folder  # noqa: E402

MANIFEST = "field_steps_flagged.tsv"

#: The analysis folder's record of what was taken OUT: one row per event removed
#: for sitting within ±2 s of a confirmed field step. Its presence, with no
#: `MANIFEST` beside it, is what identifies the steps-excluded export.
EXCLUDED_MANIFEST = "field_steps_excluded.tsv"

#: The analysis dataset: the declared default in `current_export.toml`, never a
#: folder name or a role of our own (Tony, 2026-09-21 — one default dataset). It
#: carries `field_steps_excluded.tsv`, which `resolve_folder` requires.
EXCLUDED_ROLE = "default"

#: Names the flagged review copy has shipped under. The producer's README calls
#: it `..._STEPS_FLAGGED_FOR_REVIEW`; it arrived on this machine as
#: `_superseded_flagrun2`. Neither is a path — `dataset` resolves a NAME against
#: the data root on whatever machine this is (SAP004).
FLAGGED_NAMES = (
    "2026-09-03_revised_2v_long_STEPS_FLAGGED_FOR_REVIEW",
    "_superseded_flagrun2",
)

#: What gets its own page. Tony, 2026-09-04. `high K+` is deliberately NOT here:
#: it is a terminal viability challenge given to 60 of the 84 recordings, so a
#: page of it would be most of the corpus sorted by nothing.
DEFAULT_TREATMENTS = ("TTX", "senktide")

#: The anchor. Every recording in this export has exactly one `baseline`, and it
#: is always first, so its end is a real shared moment rather than a convention.
ANCHOR = "baseline"

#: Proportional to ROI count: every ROI gets the same pitch on every recording,
#: so a 10-ROI recording is a sixth the height of a 61-ROI one and the ink
#: density reads the same down the page (Tony, 2026-09-15: *"the height of the row
#: should be proportional to the number of ROIs"*). It replaced the constant 116 px
#: row he asked for on 2026-09-04, which drew a small recording's ROIs far apart
#: and a large one's packed together.
RASTER_PX_PER_ROI = 3

#: The slice id, rotated, in a column left of its block (Tony, 2026-09-15). A
#: 10-ROI block is shorter than its own id, so the block gets whitespace BELOW the
#: raster rather than a taller raster: the ink stays proportional and only the
#: gap grows.
LABEL_COL_PX = 18
SCROLL_GUTTER_PX = 60  # empty page margin on the left: somewhere to scroll from
LABEL_PX_PER_CHAR = 6.2
BLOCK_GAP_PX = 6

#: Halved, and for the same reason the raster is dense: a detector row carries at
#: most one mark per call, so the height it needs is the height of a mark, not the
#: height of its label (Tony, 2026-09-08 — *"vertically shrink the detector row.
#: rasters can be halved for detector (similar to data rasters)"*). At 13 px a
#: ten-detector block is about the height of the raster it sits on rather than
#: twice it, and the page holds six recordings instead of three.
LANE_PX = 13
LANE_PAD_PX = 6  # above and below a lane block's rows; lane_panel's own floor is set aside
REGION_PX = 14   # two strips in one lane: the period, and the window scored
AXIS_PX = 30     # what the bottom raster adds for the page's one x-axis

#: No padding above or below a panel. Bokeh's default border is the white band
#: between the period lane and its raster, and on a page of eleven blocks it was
#: most of the vertical space that was not data.
TIGHT = {"plot.min_border_top": 0, "plot.min_border_bottom": 0}
PAGE_PX = 1500


def read_manifest(folder: Path) -> dict[tuple[str, str, str], list[float]]:
    """The producer's flagged events, keyed the way a Slice is keyed.

    `roi` in the manifest is the SOURCE-STORE ROI index and `Slice.roi_ids`
    carries the same strings, so the join needs no renumbering.
    """
    out: dict[tuple[str, str, str], list[float]] = defaultdict(list)
    with (folder / MANIFEST).open(newline="") as fh:
        for row in csv.DictReader(fh, delimiter="\t"):
            out[(row["slice_id"], row["stream"], str(row["roi"]).strip())].append(
                float(row["time_sec"]))
    return out


def read_removed(folder: Path) -> dict[tuple[str, str], int]:
    """Events the producer removed, counted per (slice_id, stream)."""
    out: dict[tuple[str, str], int] = defaultdict(int)
    with (folder / EXCLUDED_MANIFEST).open(newline="") as fh:
        for row in csv.DictReader(fh, delimiter="\t"):
            out[(row["slice_id"], str(row["stream"]).strip().lower())] += 1
    return out


def resolve_folder(explicit: str | None, *, unscanned: bool = False,
                   steps_excluded: bool = False) -> Path:
    """Find the flagged review copy, and refuse anything that is not one.

    ``unscanned`` is one exception, and it has to be asked for by name: a
    folder the producer has NEVER scanned for field steps (their export report
    says ``step-artifacts: UNCHECKED``) has no manifest because nothing was
    looked for, not because the artifacts were removed. That folder may be
    drawn — with no red, and with the page saying in its header that no scan
    was run, so the absence of red cannot be read as a clean corpus.

    ``steps_excluded`` is the other, also by name: the analysis dataset itself,
    artifacts already removed (Tony, 2026-09-15 — the pages people read the data
    from, rather than the review of what the artifacts did). It has no red to
    draw, so the header says the steps were REMOVED and how many events that
    took from the page's recordings, read from the producer's own
    ``field_steps_excluded.tsv``. A folder without that file is refused: absent
    red on a page claiming exclusion has to be backed by the exclusion record.
    """
    from bugarach import dataset

    if unscanned and steps_excluded:
        raise SystemExit("--unscanned and --steps-excluded contradict each other: "
                         "one says no scan was run, the other that its results were applied")
    if steps_excluded:
        folder = (Path(dataset.require(explicit, want="export_folder", flag="--folder"))
                  if explicit else Path(dataset.current(EXCLUDED_ROLE)))
        if not (folder / EXCLUDED_MANIFEST).is_file():
            raise SystemExit(
                f"{folder.name} has no {EXCLUDED_MANIFEST}, so nothing records that "
                "field steps were removed from it — refusing to label it steps-excluded.")
        if (folder / MANIFEST).is_file():
            raise SystemExit(
                f"{folder.name} has a {MANIFEST}: it is the flagged review copy, with the "
                "artifacts still in it. Drop --steps-excluded and let the marks be drawn.")
        return folder
    if unscanned:
        if not explicit:
            raise SystemExit("--unscanned needs --folder: there is no name to resolve "
                             "for a folder that was never scanned")
        folder = Path(dataset.require(explicit, want="export_folder", flag="--folder"))
        if (folder / MANIFEST).is_file():
            raise SystemExit(
                f"{folder.name} HAS a {MANIFEST}, so it was scanned — drop --unscanned "
                "and let the marks be drawn.")
        return folder
    if explicit:
        folder = Path(explicit).expanduser()
    else:
        folder = None
        for name in FLAGGED_NAMES:
            try:
                cand = Path(dataset.resolve(name))
            except Exception:
                continue
            if cand.is_dir():
                folder = cand
                break
        if folder is None:
            raise SystemExit(
                "could not find the flagged review copy under the data root.\n"
                f"tried: {', '.join(FLAGGED_NAMES)}\n"
                "pass --folder <path> if the producer shipped it under another name.")
    if not folder.is_dir():
        raise SystemExit(f"not a folder: {folder}")
    if not (folder / MANIFEST).is_file():
        raise SystemExit(
            f"{folder.name} has no {MANIFEST}, so it is not the flagged review copy.\n"
            "This tool draws the field-step artifacts, which means it needs the folder\n"
            "where they are STILL PRESENT and marked. The analysis folder\n"
            "(..._STEPS_EXCLUDED) has had them removed — pointing this at it would\n"
            "render pages with no red at all, which is indistinguishable from a corpus\n"
            "that never had an artifact. Refusing rather than drawing that.")
    return folder


def _anchor_of(sl) -> float | None:
    """End of this recording's baseline, or None if it has no baseline to use."""
    for r in sl.regions or []:
        if (r.name or "").strip().lower() == ANCHOR:
            return float(r.end_sec)
    return None


def treatment_one(sl) -> str | None:
    """The first period after baseline, in time order, or None if there is none."""
    for r in sorted(sl.regions or [], key=lambda r: float(r.start_sec)):
        lab = (r.name or "").strip()
        if lab and lab.lower() != ANCHOR:
            return lab
    return None


def _shift_stream(stream, shift: float):
    """The same stream, re-zeroed. Times move; nothing else does.

    **`width` is deliberately untouched, and that is the whole of this
    function's opinion about duration.** A width is an interval, so a change of
    origin cannot alter it; shifting it would be deriving a new one, which is
    the producer's call and not this repo's (FOUNDATIONS §7). The three fields
    below are absolute times and are the only things a re-zeroing may move.

    Each is assigned on its own line ON PURPOSE. Written as one `replace(...)`
    call the three names share a line, and SAP012 blocks that — correctly, by
    its own design: it matches the comma form precisely because the defect it
    was written for hid a subtraction across two of these fields. A per-line
    matcher cannot tell "subtract one of these from another" from "apply the
    same offset to each", and it should not try. See
    `docs/sapper_feedback/2026-09-04-sap012-cannot-see-a-shift.md`.
    """
    def mv(rows):
        if rows is None:
            return None
        return [np.asarray(v, dtype=float) - shift for v in rows]

    moved = {}
    moved["locs"] = mv(stream.locs)
    moved["t50rise"] = mv(stream.t50rise)
    moved["peak"] = mv(stream.peak)
    return dataclasses.replace(stream, **moved)


COMBINED = "fast+slow"

# The slow ink, on the combined page. Vermillion rather than a red or a blue,
# and the reason is measured rather than taste: against RASTER_INK (#2b2b2b) at
# 2 px this is the pair a colour-blind reviewer can still separate. OKLab ΔE ×100
# under the worst of protan/deutan, from the dataviz validator —
#   #d55e00 vermillion 28.1   #0072b2 blue 26.2   #e8000b red 18.7   #c1272d red 15.0
# A red reads as the punchiest choice to full-colour vision and is the WORST of
# the four for a protan reader, because red against near-black is exactly the
# pair that collapses. #ff6d00 scores higher still (35.0) and fails contrast
# against white, which at a 2 px mark is the other way to be unreadable.
STREAM_INK = "#d55e00"


def _combined_stream(sl):
    """Both streams as one raster, and the slow onsets to ink inside it.

    Returns ``(stream, marked)`` — a stream whose events are the union of this
    recording's fast and slow events per ROI, and the per-ROI slow onset times
    that ``raster_panel(marked=...)`` inks a second colour. ``(None, None)``
    when the recording does not carry both streams.

    THIS IS THE SANCTIONED SECOND INK, NOT AN EXCEPTION TO THE RASTER RULE.
    ``raster_panel``'s docstring draws the line at *who is asserting*: a
    detection is this project's claim and belongs in the lane above, while a
    partition the EXPORTER shipped is "already true of the row before anything
    here read it" and "is not annotation, it is the raster". ``stream`` is that
    partition — a column of the export contract
    (``docs/export_folder_spec.md``), decided upstream. Nothing is added: the
    union is drawn once per event, and the ink says which population the
    producer put it in.

    **It supersedes one page per stream for this mode only, and the earlier
    ruling is right about what it forbade.** Tony, 2026-09-08, split the pages
    because stacking a fast raster above a slow one per recording doubled the
    page and invited a down-page comparison between two different measurements.
    This draws ONE raster, so neither cost applies — and the combined-stream
    goal Tony set on 2026-09-22 is the case that ruling did not contemplate:
    there the streams are meant to be read as one tagged dataset.

    **The combined stream declares no width rule, deliberately.** ``width_sec``
    means different quantities in the two streams — ``halfprom_width_findpeaks_w``
    in fast, ``rise_interval_peak_minus_t50rise`` in slow — and the contract says
    a consumer comparing widths across streams must read ``width_def`` first. A
    union carries no single rule, and spec rule 6 is that a width whose rule did
    not travel is worse than no width, so ``width_def`` is ``None`` here. The
    raster draws onsets and never a width, so nothing is lost on this page.
    """
    from bugarach.store import Stream

    fast, slow = sl.streams.get("fast"), sl.streams.get("slow")
    if fast is None or slow is None:
        return None, None

    def field(st, name, i):
        v = getattr(st, name, None)
        if v is None or i >= len(v):
            return np.zeros(0, dtype=float)
        return np.asarray(v[i], dtype=float).ravel()

    n_roi = max(fast.n_rois, slow.n_rois)
    locs, amp, width, t50, marked = [], [], [], [], []
    for i in range(n_roi):
        t = np.concatenate([field(fast, "t50rise", i), field(slow, "t50rise", i)])
        order = np.argsort(t, kind="stable")
        t50.append(t[order])
        for name, out in (("locs", locs), ("amp", amp), ("width", width)):
            both = np.concatenate([field(fast, name, i), field(slow, name, i)])
            out.append(both[order] if both.size == order.size else both)
        marked.append(field(slow, "t50rise", i))

    return Stream(locs=locs, amp=amp, width=width, t50rise=t50,
                  width_def=None, peak=None), marked


def measure(folder: Path, treatments: tuple[str, ...], *, unscanned: bool = False,
            steps_excluded: bool = False, groups: tuple[str, ...] | None = None,
            combined: bool = False):
    """Which recordings go on which page, and what each page's extent must be."""
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        slices = load_folder(folder)
    manifest = {} if (unscanned or steps_excluded) else read_manifest(folder)
    if groups:
        slices = [sl for sl in slices if (sl.meta.get("group_id") or "UNGROUPED") in groups]

    pages: dict[tuple[str, str], list] = defaultdict(list)
    skipped: list[str] = []
    for sl in slices:
        anchor = _anchor_of(sl)
        if anchor is None:
            skipped.append(f"{sl.slice_id} (no {ANCHOR} region to align on)")
            continue
        # TREATMENT 1 DECIDES THE PAGE, AND NOTHING AFTER IT (Tony, 2026-09-15:
        # "treatment 1 is the only one that matters for inclusion on a page").
        # Matching any period put a recording given TTX and then senktide on the
        # senktide page too, where its senktide arrives on a slice already
        # treated — 35 recordings on the senktide pages against the producer's
        # 29 in its senktide-first folder.
        first = treatment_one(sl)
        hit = [t for t in treatments if t == first]
        if not hit:
            skipped.append(f"{sl.slice_id} (treatment 1: {first or 'none'})")
        for t in hit:
            # ONE PAGE PER STREAM, not one page carrying both (Tony, 2026-09-08).
            # fast and slow are different measurements, and stacking them per
            # recording doubled every page while inviting exactly the comparison
            # down the page that "never pooled" exists to prevent. Split, each
            # page is one measurement of six recordings and half the height.
            # ``combined`` is the exception that ruling did not contemplate:
            # one raster carrying both streams in two inks, for the
            # combined-stream goal. See _combined_stream.
            for sname in ([COMBINED] if combined else sorted(sl.streams)):
                pages[(sl.meta.get("group_id") or "UNGROUPED", t, sname)].append(
                    (sl, anchor))

    built = {}
    for key, members in pages.items():
        members.sort(key=lambda p: p[0].slice_id)
        lo = min(-a for _, a in members)
        # THE FULL RECORDING, not the last event in it. Taking the extent from
        # the last onset ends the page wherever the quietest tail happened to
        # stop firing, so a recording whose high-K+ period runs on in silence is
        # drawn as if the acquisition ended early, and its period bar is cut off
        # mid-bar with nothing to say it was cut. The period bounds are what the
        # producer recorded, so they set the extent and the events sit inside it
        # (Tony, 2026-09-08: "show the full calcium trace length and all
        # treatments").
        hi = max(max([float(np.nanmax(v)) for st in sl.streams.values()
                      for v in st.t50rise if len(v) and np.isfinite(v).any()]
                     + [float(r.end_sec) for r in sl.regions or []]
                     or [a]) - a
                 for sl, a in members)
        # out to a whole minute, so the tick ladder lands on labelled values
        built[key] = dict(members=members,
                          ext=(float(np.floor(lo / 60.0) * 60.0),
                               float(np.ceil(hi / 60.0) * 60.0)))
    return built, manifest, skipped


#: Fills for period labels the shared palette does not know. `REGION_FILL` names
#: this lab's own treatments; a stranger's folder arrives with labels it has never
#: seen, and two unknown labels falling back to the same grey is a lane where the
#: two periods a reader must tell apart cannot be told apart (murderboard
#: 2026-09-07, role 10, on the pilot cohort's APV+CNQX+GZ against high K+).
UNKNOWN_LABEL_FILLS = ("#d08a3a", "#5a9a6a", "#9a5aa0", "#c9a227", "#4a90a4")


def _name_unknown_labels(members):
    """Give each period label the palette does not know a distinct colour, once."""
    from bugarach.ui import diagnostic

    unknown = []
    for sl, _ in members:
        for r in sl.regions or []:
            lab = (r.name or "").strip()
            if lab and lab not in diagnostic.REGION_FILL and lab not in unknown:
                unknown.append(lab)
    for i, lab in enumerate(unknown):
        diagnostic.REGION_FILL[lab] = UNKNOWN_LABEL_FILLS[i % len(UNKNOWN_LABEL_FILLS)]
    return unknown


#: Display names for the lane rows, overriding the viewer's map. `cicada` is the
#: output contract and `locust` is the detector; the viewer still says "sixth",
#: which is a stale label with an open item against it and must not reach a
#: reader outside this project.
LANE_NAMES = {"cicada": "locust"}

#: A PAGE PALETTE, not the viewer's. Tony, 2026-09-08: *"more striking, contrasty
#: colors."* The viewer's inks are a muted qualitative set chosen to sit under a
#: user's attention for an hour; ten of them stacked at a few pixels a row on a
#: printed page is a different problem, and the marks a reader must tell apart
#: are one or two pixels wide. So: full-saturation hues for the six, well spread
#: around the wheel, and the learned family in a gold-to-brown ramp that reads as
#: one kind at a glance while still separating its four members.
LANE_COLORS = {
    "rate": "#0B5FFF", "coact": "#00B3A4", "loco": "#7A00E6",
    "sce": "#00A100", "cicada": "#FF00A8", "sync": "#FF3B00",
    # A warm ramp, dark to light, well separated at the ends AND in the middle.
    # A first attempt ran four browns from #4A2E00 to #D4A017 and the top two were
    # one colour at a 13 px row height.
    "tube": "#7F0000", "tube_guard": "#D62828",
    "tube_ratio": "#F77F00", "tube_ratio_guard": "#FCBF49",
    "trace": "#5C5C5C", "tiny": "#8C8C8C",
}


def detector_lanes(*detections: Path):
    """(slice_id, stream) -> {detector: (onsets, widths)}, in the glossary's order.

    Read straight from the detect step's own output, so the marks on the page
    are the calls in the table and not a second opinion about them.
    """
    from bugarach.detect_folder import DETECTORS
    from bugarach.emit import read_detections

    # ORDER IS THE GLOSSARY'S, THEN ARRIVAL. The six ports have a canonical order
    # and keep it; anything else — a learned model, a detector from outside this
    # project — lands after them in the order its file was given, so the page
    # never reorders itself because a run produced a different set.
    acc: dict = defaultdict(lambda: defaultdict(lambda: ([], [])))
    seen_order: list[str] = []
    for path in detections:
        for r in read_detections(path):
            key = (r["slice_id"], str(r["stream"]).strip().lower())
            if r["detector"] not in seen_order:
                seen_order.append(r["detector"])
            on, wd = acc[key][r["detector"]]
            on.append(float(r["onset_sec"]))
            wd.append(float(r.get("width_sec") or 0.0))
    DETECTORS = list(DETECTORS) + [d for d in seen_order if d not in DETECTORS]
    # EVERY DETECTOR GETS A ROW ON EVERY RECORDING, including the ones that
    # called nothing there. Dropping a silent detector's row silently changes
    # which rows a reader is looking at from one recording to the next, so the
    # eye compares LoCo against SPIKE-synch without noticing, and a detector
    # that found nothing — which is a result — looks like a detector that was
    # never asked. An empty row here means exactly what it should: it ran.
    ran = [d for d in DETECTORS if any(d in per for per in acc.values())]
    out = {}
    for key, per_det in acc.items():
        out[key] = {d: (np.asarray(per_det[d][0] if d in per_det else [], float),
                        np.asarray(per_det[d][1] if d in per_det else [], float))
                    for d in ran}
    return out


def build_page(members, *, ext, manifest, width: int, stream: str,
               lanes=None, not_run=(), lane_px: int = None, roi_px: int = None,
               slow_ink: str = STREAM_INK, zoom: bool = False):
    """Regions over detector lanes over raster, for ONE stream, per recording."""
    from bugarach.detect_folder import folder_analysis_windows
    from bugarach.ui.diagnostic import lane_panel, raster_panel, region_lane_panel

    _name_unknown_labels(members)
    lanes = lanes or {}
    blocks, red_drawn = [], 0
    for sl, anchor in members:
        # A UNIQUE y-DIMENSION PER PANEL. The name is what links y-ranges across
        # panels, so leaving the defaults draws every recording against the ROI
        # count of the largest one on the page — a 19-ROI raster fills the bottom
        # 40% of its band and reads as sparse rather than small, which is the one
        # comparison a constant row height exists to make honest.
        _, wins = folder_analysis_windows(sl)
        panels = [region_lane_panel(sl.regions, ext=ext, width=width,
                                    height=REGION_PX, shift=anchor,
                                    ydim=f"region_{sl.slice_id}",
                                    analysis=[(w.win_start, w.win_end) for w in wins])]
        for sname in (stream,):
            if sname == COMBINED:
                st, slow_onsets = _combined_stream(sl)
            else:
                st, slow_onsets = sl.streams.get(sname), None
            if st is None:
                continue
            # The detector's calls sit between the periods and the raster they
            # were made on: below the window that says what was going on, above
            # the marks they are a claim about.
            per_det = lanes.get((sl.slice_id, sname), {})
            if per_det or not_run:
                shifted = {d: (on - anchor, wd) for d, (on, wd) in per_det.items()}
                row = lane_px or LANE_PX
                n_rows = len(set(per_det) | set(not_run))
                # SIZED TO ITS ROWS, NOT TO lane_panel's FLOOR. The shared panel is
                # max(90, rows x row_px + 46) tall: room for an axis and borders a
                # standalone figure needs and this page strips. With two detectors
                # that floor made the lanes as tall as a 30-cell raster (Tony,
                # 2026-09-21: "the rasters themselves should dominate. the detection
                # has too much white space"). The rows keep their size; the padding goes.
                panels.append(lane_panel(shifted, ext=ext, width=width,
                                         row_px=row, not_run=not_run,
                                         names=LANE_NAMES, colors=LANE_COLORS)
                              .opts(height=row * n_rows + LANE_PAD_PX,
                                    backend_opts=TIGHT))
            marked, n_red = [], 0
            if slow_onsets is not None:
                # The producer's own partition: slow events, inked inside the
                # union raster. No manifest is involved and nothing is red.
                marked = [np.asarray(m, dtype=float) - anchor for m in slow_onsets]
            else:
                for i in range(st.n_rois):
                    rid = (str(sl.roi_ids[i]) if sl.roi_ids is not None
                           and i < len(sl.roi_ids) else str(i + 1))
                    hits = manifest.get((sl.slice_id, sname, rid), ())
                    marked.append(np.asarray(hits, dtype=float) - anchor)
                    n_red += len(hits)
            red_drawn += n_red
            # No y-label: the slice id sits rotated to the left of the block, the
            # stream is in the page title, and the top tick already says the ROI
            # count. A rotated label inside a 30 px raster is clipped anyway.
            panels.append(raster_panel(
                _shift_stream(st, anchor), ext=ext, width=width,
                height=raster_px(st.n_rois, roi_px), name=sname, marked=marked,
                marked_ink=slow_ink if slow_onsets is not None else None,
                ydim=f"roi_{sl.slice_id}_{sname}", ticks="minimal"
            ).opts(ylabel="", backend_opts=TIGHT))
        blocks.append((sl, panels))

    # ONE X-AXIS PER LINKED GROUP, on the bottom row only (CLAUDE.md). Every
    # panel carrying its own drew the tick ladder and the `t` label eighteen
    # times down a page whose rows share one axis by construction, which is both
    # noise and a lie about how many axes there are. The last raster keeps its
    # own and gets the height back that the others give up.
    flat = [p for _, ps in blocks for p in ps]
    for p in flat[:-1]:
        p.opts(xaxis=None, toolbar=None, backend_opts=TIGHT)
    if flat:
        last_h = flat[-1].opts.get("plot").kwargs.get("height") or 0
        flat[-1].opts(height=last_h + AXIS_PX, toolbar=None)
    # ONE TOOLBAR FOR THE WHOLE PAGE, and only when asked for. Every panel on
    # this page was built with `toolbar=None` because the page's other life is a
    # flat PNG, and a screenshot of eighteen toolbars is eighteen widgets nobody
    # can press. That left the HTML with no way to zoom at all — which is the
    # half of the page a reader actually opens when the question is whether a
    # column of marks is a column. The panels already declare the right tools
    # (`xwheel_zoom`, `xpan`, `reset`, with `xpan` active, per CLAUDE.md's
    # "scroll wins"); this only stops discarding them. It goes on the FIRST
    # panel so it is reachable without scrolling to the bottom of a long page,
    # and x is linked through the shared `t` dimension, so zooming any panel
    # zooms all of them — which is the comparison the page is for.
    if zoom and flat:
        flat[0].opts(toolbar="above")
    return blocks, red_drawn


def raster_px(n_rois: int, roi_px: int | None = None) -> int:
    return (roi_px or RASTER_PX_PER_ROI) * max(int(n_rois), 1)


def block_heights(slice_id: str, n_rois: int) -> tuple[int, int]:
    """(data height, label height) for one block, in px.

    The label height is the larger of the two: an id longer than its block gets
    the room it needs as whitespace below the raster, never as a taller raster.
    """
    data = REGION_PX + raster_px(n_rois)
    return data, max(data, int(len(slice_id) * LABEL_PX_PER_CHAR) + 6)


def header_html(group: str, treatment: str, members, ext, folder: Path,
                *, stream: str = "", unscanned: bool = False, ran=(), not_run=(),
                excluded=(), note=None, removed: dict | None = None,
                slow_ink: str = STREAM_INK,
                detections: Path | None = None, roi_px: int | None = None) -> str:
    """The key, and the provenance. Outside every plot, per the conventions."""
    from bugarach.ui.diagnostic import MARKED_INK, RASTER_INK, REGION_FILL

    def chip(colour, label):
        return (f"<span style='display:inline-block;width:11px;height:11px;"
                f"background:{colour};vertical-align:-1px;margin-right:5px;"
                f"border:0.5px solid #fff'></span>{label}")

    seen = []
    for sl, _ in members:
        for r in sl.regions or []:
            lab = (r.name or "").strip()
            if lab and lab not in seen:
                seen.append(lab)
    regions = " &nbsp; ".join(chip(REGION_FILL.get(l, "#9e9e9e"), l) for l in seen)
    # Built here rather than inline in the f-string below. A newline INSIDE an
    # f-string expression is PEP 701, which is 3.12+; on 3.11 the same source is
    # `SyntaxError: unterminated string literal` at import, so the whole module
    # fails to load and every test in the file errors at collection. Local 3.14
    # accepted it and CI's 3.11 leg did not — this project supports >=3.11.
    red_key = chip(MARKED_INK, "event on a confirmed whole-field brightness step "
                               "(field-step artifact)")
    if stream == COMBINED:
        # THE INK IS THE PRODUCER'S STREAM COLUMN, so the key names the two
        # populations and nothing else. Saying "nothing on this page is marked"
        # here — the removed-artifact wording below — would be false on a page
        # where every slow event is inked, and a legend that contradicts the
        # picture is worse than none.
        removed_note = ""
        if removed is not None:
            n = sum(removed.get((sl.slice_id, s), 0)
                    for sl, _ in members for s in ("fast", "slow"))
            removed_note = (f" &nbsp;&nbsp; <span style='color:#777'>field-step "
                            f"artifacts already removed by the producer: {n} events "
                            f"across both streams on these {len(members)} recordings "
                            f"({EXCLUDED_MANIFEST})</span>")
        red_key = (chip(RASTER_INK, "<b>fast</b> event") + " &nbsp; "
                   + chip(slow_ink, "<b>slow</b> event")
                   + " &nbsp; <span style='color:#444'>one mark per event, each drawn "
                     "once; the ink is the producer's own <code>stream</code> column, "
                     "not a detector's claim</span>" + removed_note)
    elif unscanned:
        # No red on this page, and the reader has to be told WHY there is none:
        # nobody looked, which is not the same as nothing being there.
        red_key = ("<b style='color:#b00'>⚠ no field-step scan has been run on this "
                   "folder</b> (the producer's export report says UNCHECKED) — nothing "
                   "is marked, and the absence of red is not evidence of a clean cohort")
    elif removed is not None:
        # No red here either, for the opposite reason: the artifacts were found
        # and taken out. The count is this page's recordings on this page's
        # stream, so a reader can see what the clean page cost.
        hit = sorted((sl.slice_id, removed[(sl.slice_id, stream)]) for sl, _ in members
                     if removed.get((sl.slice_id, stream)))
        n = sum(k for _, k in hit)
        where = (" — " + ", ".join(f"{sid}: {k} events" for sid, k in hit)) if hit else ""
        red_key = (f"<b>field-step artifacts removed by the producer</b>: {n} {stream} "
                   f"events on {len(hit)} of these {len(members)} recordings{where} "
                   f"(listed in {EXCLUDED_MANIFEST}); nothing on this page is marked")
    from bugarach.ui.app import COLORS, TITLES

    if ran:
        det_key = (
            "<div style='margin:4px 0 0;color:#444'>detector lanes, one block per "
            "stream, between the periods and the raster they were called on: &nbsp; "
            + " &nbsp; ".join(
                chip(LANE_COLORS.get(d) or COLORS.get(d, "#555"),
                     LANE_NAMES.get(d, TITLES.get(d, d)))
                for d in ran))
        if excluded:
            det_key += (
                " &nbsp;&nbsp; <span style='color:#777'>left off this page to save "
                "space: <b>" + ", ".join(
                    LANE_NAMES.get(d, TITLES.get(d, d)) for d in excluded)
                + "</b> — their calls are still in the files above</span>")
        if not_run:
            det_key += (
                " &nbsp;&nbsp; " + chip("#d8d8d8", "")
                + "<b>" + ", ".join(LANE_NAMES.get(d, TITLES.get(d, d)) for d in not_run) + "</b> — "
                "trained in the bake-off and <b>not runnable on real data</b>: nothing "
                "persists a trained model, so these rows are grey rather than empty, "
                "because an empty lane would say the detector ran and found nothing")
        det_key += "</div>"
    else:
        det_key = ("<div style='margin:4px 0 0;color:#444'>no detector was run — "
                   "pass <code>--detections</code> to draw the calls</div>")
    src = "".join(f" &nbsp;·&nbsp; {d.parent.name}/{d.name}" for d in (detections or []))
    note_html = (f"<div style='margin:4px 0 0;color:#b00'>⚠ {note}</div>") if note else ""
    return (
        f"<div style='font:13px system-ui,sans-serif;color:#111;margin:0 0 6px'>"
        f"<b style='font-size:16px'>{group} · {treatment} · {stream}</b> &nbsp;—&nbsp; "
        f"{len(members)} recording(s), each row one recording, "
        f"<b>t = 0 is the end of that recording's baseline</b>"
        f"<div style='margin:5px 0 0;color:#444'>"
        # The combined key names both inks itself, so the generic "event" chip
        # would sit in front of it saying the fast ink twice.
        f"{'' if stream == COMBINED else chip(RASTER_INK, 'event') + ' &nbsp; '}"
        f"{red_key}"
        f"</div>"
        f"{note_html}"
        f"<div style='margin:4px 0 0;color:#444'>regions: {regions} &nbsp;&nbsp; "
        f"{chip('#222222', 'the window actually scored, along the bottom of its period bar')}"
        f"</div>"
        f"{det_key}"
        f"<div style='margin:5px 0 0;color:#777;font-size:11px'>"
        f"{folder.name}{src} &nbsp;·&nbsp; extent {ext[0] / 60:.0f}m to +{ext[1] / 60:.0f}m, "
        f"the full recorded length of the longest recording &nbsp;·&nbsp; "
        f"raster height is proportional to ROI count ({roi_px or RASTER_PX_PER_ROI} px per ROI); "
        f"slice id at the left of each recording</div></div>")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--folder", default=None,
                    help="path to the flagged review copy (default: resolve by name)")
    ap.add_argument("--out", default=None,
                    help="destination directory (default: the darkroom)")
    ap.add_argument("--also", default=None, help="write a second copy here")
    ap.add_argument("--treatments", nargs="+", default=list(DEFAULT_TREATMENTS),
                    help=f"one page per group per treatment (default: "
                         f"{' '.join(DEFAULT_TREATMENTS)})")
    ap.add_argument("--width", type=int, default=PAGE_PX)
    ap.add_argument("--no-png", action="store_true",
                    help="skip the flat render (needs playwright chromium)")
    ap.add_argument("--unscanned", action="store_true",
                    help="the folder was NEVER scanned for field steps (producer: "
                         "UNCHECKED), so it has no manifest. Draw it with no red and "
                         "say so in the header. Needs --folder.")
    ap.add_argument("--steps-excluded", action="store_true",
                    help=f"draw the ANALYSIS dataset, field-step artifacts already "
                         f"removed (default: the '{EXCLUDED_ROLE}' export). No red; the header "
                         f"counts what {EXCLUDED_MANIFEST} says was removed.")
    ap.add_argument("--groups", nargs="+", default=None, metavar="GROUP",
                    help="only these groups (e.g. DI) — for rendering one page to review")
    ap.add_argument("--detections", default=None, nargs="+", type=Path,
                    help="one or more detections.csv — detect's own, and any other "
                         "file in the same contract (a learned run, say). Draws a "
                         "detector lane block between the periods and each raster.")
    ap.add_argument("--exclude", nargs="*", default=(), metavar="DETECTOR",
                    help="detectors to leave off the page. Their calls stay in the "
                         "files this reads — this is page space, not a data decision.")
    ap.add_argument("--lane-px", type=int, default=None,
                    help=f"height of one detector row in px (default {LANE_PX})")
    ap.add_argument("--ink", choices=("field-steps", "stream"), default="field-steps",
                    help="what the second ink means. 'field-steps' (default) inks the "
                         "producer's flagged artifacts on one raster per stream. "
                         "'stream' draws ONE raster per (group, treatment) carrying "
                         "both streams, slow inked, for the combined-stream goal.")
    ap.add_argument("--zoom", action="store_true",
                    help="keep one toolbar on the page so the HTML can be zoomed "
                         "and panned (x is linked, so one panel zooms all). The "
                         "toolbar is then in the PNG too — pass --no-png for a "
                         "clean flat render, or render twice.")
    ap.add_argument("--slow-ink", default=STREAM_INK, metavar="HEX",
                    help=f"the slow stream's ink on an --ink stream page "
                         f"(default {STREAM_INK}). Changing it re-opens a measured "
                         f"choice: check the new pair with the dataviz validator "
                         f"before adopting it.")
    ap.add_argument("--streams", nargs="+", default=None, metavar="STREAM",
                    help="only these streams' pages (default: every stream). Tony, "
                         "2026-09-21: fast only until the slow bench's run has finished")
    ap.add_argument("--png-scale", type=int, default=3,
                    help="device pixel ratio of the flat PNG (default 3; 6 doubles it — "
                         "Tony, 2026-09-21. A tall page can reach Chromium's ~16k px "
                         "screenshot limit)")
    ap.add_argument("--roi-px", type=int, default=None,
                    help=f"raster height per ROI in px (default {RASTER_PX_PER_ROI}). "
                         f"Still proportional to the ROI count, so ink density reads the "
                         f"same down the page; a larger value lets the raster dominate a "
                         f"page with few detector lanes")
    ap.add_argument("--note", default=None,
                    help="one extra line for the header — a caveat this page must "
                         "carry that the files it reads cannot tell it")
    ap.add_argument("--not-run", nargs="*", default=None, metavar="DETECTOR",
                    help="detectors to show as rows that never ran (grey, labelled), "
                         "so their absence is visible rather than silent. Defaults to "
                         "the learned models when --detections is given, because "
                         "nothing persists a trained model.")
    a = ap.parse_args(argv)

    folder = resolve_folder(a.folder, unscanned=a.unscanned,
                            steps_excluded=a.steps_excluded)
    removed = read_removed(folder) if a.steps_excluded else None
    if a.out:
        dest = Path(a.out).expanduser()
    else:
        root = paths.darkroom(create=True)
        if root is None:
            print(paths.unresolved_message(), file=sys.stderr)
            return 2
        # Named for what is in it, not for the branch that made it.
        # A separate folder for the excluded pages: same filenames, different
        # data, and overwriting the flagged review in place would lose it.
        dest = root / ("rasters_by_group_and_treatment_baseline_aligned"
                       + ("_steps_excluded" if a.steps_excluded else ""))
    dest.mkdir(parents=True, exist_ok=True)

    import panel as pn

    pages, manifest, skipped = measure(folder, tuple(a.treatments),
                                       unscanned=a.unscanned,
                                       steps_excluded=a.steps_excluded,
                                       groups=tuple(a.groups) if a.groups else None,
                                       combined=a.ink == "stream")
    if not pages:
        print("no (group, treatment) page has any recording", file=sys.stderr)
        return 1

    lanes = detector_lanes(*a.detections) if a.detections else {}
    if a.exclude:
        drop = set(a.exclude)
        lanes = {k: {d: v for d, v in per.items() if d not in drop}
                 for k, per in lanes.items()}
    ran = list(dict.fromkeys(d for per in lanes.values() for d in per))
    not_run = tuple(a.not_run) if a.not_run is not None else ()

    written, total_red = [], 0
    for (group, treatment, stream), spec in sorted(pages.items()):
        if a.streams and stream not in a.streams:
            continue
        blocks, red = build_page(spec["members"], ext=spec["ext"],
                                 manifest=manifest, width=a.width, stream=stream,
                                 lanes=lanes, not_run=not_run, lane_px=a.lane_px,
                                 roi_px=a.roi_px, slow_ink=a.slow_ink, zoom=a.zoom)
        total_red += red
        html = dest / f"{group}_{treatment.replace(' ', '')}_{stream}.html"

        items = [pn.pane.HTML(header_html(group, treatment, spec["members"],
                                          spec["ext"], folder, stream=stream,
                                          unscanned=a.unscanned, ran=ran,
                                          not_run=not_run, excluded=a.exclude,
                                          detections=a.detections, note=a.note,
                                          removed=removed, roi_px=a.roi_px,
                                          slow_ink=a.slow_ink))]
        for sl, panels in blocks:
            # THE ID, ROTATED, IN ITS OWN COLUMN — an HTML block and not the
            # raster's y-label. As a y-label it is clipped to the plot's height:
            # at 116 px it came out as "0240827a55", and a truncated identifier
            # still looks like an answer. Its own column is as tall as the id
            # needs, and a block shorter than that gets the difference as space.
            st = sl.streams.get(stream)
            data_h, label_h = block_heights(sl.slice_id, st.n_rois if st else 0)
            label = pn.pane.HTML(
                f"<div style='height:{label_h}px;width:{LABEL_COL_PX}px;"
                f"display:flex;align-items:center;justify-content:center'>"
                f"<span style='writing-mode:vertical-rl;transform:rotate(180deg);"
                f"font:600 10px system-ui,sans-serif;color:#111;white-space:nowrap'>"
                f"{sl.slice_id}</span></div>",
                width=LABEL_COL_PX, height=label_h, margin=(0, 0, 0, 0))
            col = [pn.pane.HoloViews(p, margin=0, linked_axes=True) for p in panels]
            if label_h > data_h:
                col.append(pn.Spacer(height=label_h - data_h, margin=0))
            items.append(pn.Row(label, pn.Column(*col, margin=0),
                                margin=(0, 0, BLOCK_GAP_PX, 0)))

        with tempfile.TemporaryDirectory() as td:
            tmp = Path(td) / "p.html"
            # write-then-replace: the darkroom is inside Dropbox, and writing in
            # place is what produced its 188 MB of hash-named orphans.
            # A SCROLL GUTTER. The plots span the page, so there was nowhere to rest the
            # cursor and scroll without landing on a plot (Tony, 2026-09-21: "need a
            # little space on the left so there is a place to put the cursor to scroll").
            pn.Column(*items, margin=(0, 0, 0, SCROLL_GUTTER_PX)).save(str(tmp))
            os.replace(tmp, html)
        written.append(html)
        if not a.no_png:
            from make_diagnostic import _render_png
            shot = html.with_suffix(".png")
            if _render_png(html, shot, scale=a.png_scale):
                written.append(shot)
            else:
                print("(no PNG: pip install playwright && python -m playwright "
                      "install chromium, or pass --no-png)", file=sys.stderr)
        print(f"  {group:9s} {treatment:9s} {len(spec['members']):2d} recording(s), "
              f"{red:3d} red, extent {spec['ext'][0] / 60:+.0f}m..{spec['ext'][1] / 60:+.0f}m")

    if a.also:
        alt = Path(a.also).expanduser()
        alt.mkdir(parents=True, exist_ok=True)
        for p in written:
            (alt / p.name).write_bytes(p.read_bytes())

    in_manifest = sum(len(v) for v in manifest.values())
    print(f"\nread   {folder}")
    print(f"wrote  {len(written)} file(s) -> {dest}")
    if skipped:
        # Said out loud, every run. A recording that is on no page is invisible,
        # and a reader who does not know that will read these eight pages as the
        # whole corpus.
        print(f"\n{len(skipped)} recording(s) on NO page "
              f"(treatment 1 is not {'/'.join(a.treatments)}):")
        for s in sorted(skipped):
            print(f"  {s}")
    if removed is not None:
        print(f"\nsteps-excluded: no red drawn; {sum(removed.values())} events listed "
              f"as removed in {EXCLUDED_MANIFEST}")
    else:
        print(f"\nred marks {total_red} drawn / {in_manifest} in {MANIFEST} "
              f"(a recording on two pages is drawn on both)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
