"""Does this folder conform to the import contract? — the producer's own check.

``docs/export_folder_spec.md`` tells a producer what to write. This tells them
whether they wrote it, without needing anyone on this side to look. That is the
whole design goal: a contract nobody can test against is a contract enforced by
correspondence, and the failures it lets through are the quiet ones — a window
that never arrived, a `slice_id` off by a character, an ROI population smaller
than the microscope saw.

It reports rather than judges. Every check names the file and the line, counts
what it found, and separates **can't read this** from **read it, and here is what
you may not have meant** — because most conformance failures parse perfectly.
"""

from __future__ import annotations

import csv
import warnings
from dataclasses import dataclass, field
from pathlib import Path

from bugarach.detectors.loco import effective_region_windows
from bugarach.detectors.rate import recording_extent
from bugarach.io import NO_EVENT, RESERVED, load_folder


@dataclass
class RecordingReport:
    """What one recording file turned out to hold."""

    slice_id: str
    n_rois: int = 0
    n_events: int = 0
    n_silent: int = 0
    streams: list[str] = field(default_factory=list)
    windows: list[str] = field(default_factory=list)
    frame_interval: str | None = None
    errors: list[str] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not self.errors


@dataclass
class FolderReport:
    folder: Path
    recordings: list[RecordingReport] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not self.errors and all(r.ok for r in self.recordings)

    @property
    def n_ok(self) -> int:
        return sum(1 for r in self.recordings if r.ok)


def _header(path: Path) -> list[str]:
    with path.open(newline="") as f:
        return next(csv.reader(f), [])


def check_folder(folder) -> FolderReport:
    """Read a folder as the contract and report what conformed.

    Errors are things that stop a recording being read at all. Notes are things
    that read fine and are probably not what the producer meant — a population
    with no silent ROIs declared, a table that missed a recording, an interval
    nobody supplied. Notes never fail the check; they are what a human should
    look at before believing the numbers.
    """
    folder = Path(folder)
    rep = FolderReport(folder=folder)

    if not folder.is_dir():
        rep.errors.append(f"{folder} is not a folder")
        return rep

    files = sorted(p for p in folder.glob("*.csv") if p.name not in RESERVED)
    if not files:
        rep.errors.append(
            f"no recording files. A folder holds one CSV per recording, named "
            f"by the recording; only {', '.join(RESERVED)} are reserved. "
            f"Found: {sorted(p.name for p in folder.glob('*.csv')) or 'no CSVs at all'}")
        return rep

    # the reserved tables, checked for shape before anything depends on them
    for name, required in (("regions.csv",
                            ("slice_id", "region_idx", "label",
                             "start_sec", "end_sec")),
                           ("slices.csv", ("slice_id", "frame_interval_sec"))):
        p = folder / name
        if not p.is_file():
            rep.notes.append(
                f"no {name} — allowed. Without regions.csv every recording is "
                f"one unlabelled window; without slices.csv bugarach asks for "
                f"the frame interval at load and will not proceed without it."
                if name == "slices.csv" else
                f"no {name} — allowed; every recording is then analysed as one "
                f"unlabelled window spanning its own extent.")
            continue
        missing = [c for c in required if c not in _header(p)]
        if missing:
            rep.errors.append(f"{name}: missing column(s) {', '.join(missing)}")

    if rep.errors:
        return rep

    # one load, so the check exercises the same reader the analysis will
    try:
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            slices = load_folder(folder)
    except (ValueError, OSError) as exc:
        rep.errors.append(str(exc))
        return rep

    for w in caught:
        rep.notes.append(str(w.message).replace(f"{folder.name}: ", ""))

    for s in slices:
        r = RecordingReport(slice_id=s.slice_id, streams=sorted(s.streams))
        first = s.streams[r.streams[0]]
        r.n_rois = first.n_rois
        r.n_events = sum(st.n_events for st in s.streams.values())
        # an ROI silent in EVERY stream is one the producer declared and nothing
        # else would have shown; per-stream silence is normal and not counted
        r.n_silent = sum(
            1 for i in range(r.n_rois)
            if all(st.locs[i].size == 0 for st in s.streams.values()))
        r.windows = [w.name or "(unnamed)" for w in s.regions]
        r.frame_interval = s.meta.get("frame_interval_sec")

        if r.frame_interval is None:
            r.notes.append("no frame interval — bugarach will ask for it")
        else:
            try:
                if float(r.frame_interval) <= 0:
                    r.errors.append(
                        f"frame_interval_sec is {r.frame_interval}, which is not "
                        f"a positive number of seconds")
            except ValueError:
                r.errors.append(
                    f"frame_interval_sec is {r.frame_interval!r}, which is not a "
                    f"number of seconds")
        if not r.windows:
            r.notes.append("no treatment windows — analysed as one whole-recording window")
        else:
            # THE CHECK THAT WAS MISSING. Loading a folder is not the same as
            # being able to analyse it: `region_windows` re-applies this
            # project's windowing convention and HALTS on a baseline that does
            # not start at 0 or a gap between regions. A folder that shipped
            # pre-trimmed windows loads perfectly and then halts every
            # detector — and this check passed it, so a green result was taken
            # as evidence the folder was usable. It was not.
            try:
                # exactly what a detector calls, so the check fails on what the
                # detectors would fail on rather than on a near-enough proxy
                effective_region_windows(s, recording_extent(s))
            except ValueError as exc:
                r.errors.append(
                    f"loads, but no detector can run on it: {exc}")
                if "does not match" in str(exc) or "expected 0" in str(exc):
                    r.errors.append(
                        "these look like analysis windows sent as region bounds. "
                        "Either send the RAW period — region 1 at 0, each region "
                        "starting where the last ended — or keep the raw bounds "
                        "and put your windows in analysis_start_sec / "
                        "analysis_end_sec, which are used as given")
            if all(rg.has_analysis_window for rg in s.regions if s.regions):
                r.notes.append(
                    "analysis windows supplied — scored as given, and this "
                    "project's wash-in delay and caps are not applied")
        if r.n_silent == 0:
            r.notes.append(
                f"no ROI declared with no events. If every one of the {r.n_rois} "
                f"ROIs fired, this is right; if some were quiet, they are missing "
                f"from the population and every per-ROI figure is too high "
                f"(write them as time_sec = {NO_EVENT[1].upper()})")
        rep.recordings.append(r)

    return rep


def format_report(rep: FolderReport) -> str:
    """The report a producer reads in a terminal."""
    out = [f"export folder: {rep.folder}"]
    if rep.errors:
        out.append("")
        for e in rep.errors:
            out.append(f"  FAIL  {e}")
        out.append("")
        out.append(("NOT CONFORMING — see the export contract: docs/export_folder_spec.md in "
         "the bugarach repo, or export_folder_spec.html beside the one-page "
         "producer guide wherever that was sent to you"))
        return "\n".join(out)

    out.append(f"{len(rep.recordings)} recording(s), {rep.n_ok} conforming")
    out.append("")
    w = max((len(r.slice_id) for r in rep.recordings), default=10)
    for r in rep.recordings:
        flag = "ok  " if r.ok else "FAIL"
        out.append(
            f"  {flag} {r.slice_id:<{w}}  {r.n_rois:4d} ROI "
            f"({r.n_silent} with no events)  {r.n_events:6d} events  "
            f"streams {'+'.join(r.streams)}  "
            f"dt {r.frame_interval or '—'}  "
            f"windows {', '.join(r.windows) or '—'}")
        for e in r.errors:
            out.append(f"       ! {e}")
        for n in r.notes:
            out.append(f"       · {n}")
    if rep.notes:
        out.append("")
        out.append("  folder:")
        for n in rep.notes:
            out.append(f"       · {n}")
    out.append("")
    out.append("CONFORMING" if rep.ok else ("NOT CONFORMING — see the export contract: docs/export_folder_spec.md in "
         "the bugarach repo, or export_folder_spec.html beside the one-page "
         "producer guide wherever that was sent to you"))
    if rep.ok:
        out.append("Lines marked · read fine and may still not be what you meant.")
    return "\n".join(out)
