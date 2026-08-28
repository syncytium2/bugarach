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

**Its verdict is binding on the rest of the app.** A folder this says is
conforming is one ``bugarach detect`` will score, and a recording it refuses is
one ``detect`` refuses for the same stated reason — because both ask
:func:`bugarach.detect_folder.folder_analysis_windows`, the one resolver, rather
than each deriving windows from the same rules read twice.
"""

from __future__ import annotations

import csv
import textwrap
import warnings
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np

from bugarach.detect_folder import folder_analysis_windows
from bugarach.io import NO_EVENT, RESERVED, load_folder


#: The notes a recording can carry, as fixed strings.
#:
#: **Fixed because they repeat, and repetition is what made this report
#: unreadable.** On the lab's own 84-recording export, `bugarach check` printed
#: 166 lines of which 76 were byte-identical copies of one 40-word advisory,
#: and the verdict — the answer to the question the command asks — was the last
#: line of the file. A folder that is fine read like a fault log. So a note is
#: now a short invariant sentence, its explanation lives once in
#: ``NOTE_DETAIL``, and ``format_report`` says it once and names how many
#: recordings it covers.
NO_FRAME_INTERVAL = "no frame interval — bugarach will ask for it"
NO_WINDOWS = "no treatment windows — analysed as one whole-recording window"
ANALYSIS_WINDOWS_SUPPLIED = "analysis windows supplied — scored as given"
RAW_BOUNDS_SCORED = "no analysis windows — the raw period bounds are scored as given"
NO_SILENCE_DECLARED = "no ROI declared with no events"
NO_WIDTH = "no per-event width"
PART_WIDTH = "some streams carry no per-event width"

#: The long half of each note, said once per folder rather than once per
#: recording. Keyed by the note itself.
NOTE_DETAIL = {
    NO_SILENCE_DECLARED: (
        f"If every ROI in those recordings fired, this is right. If some were "
        f"quiet they are missing from the population, every per-ROI figure "
        f"computed from it is too high, and nothing downstream can tell — "
        f"write them as time_sec = {NO_EVENT[1].upper()}."),
    ANALYSIS_WINDOWS_SUPPLIED: (
        "This project's wash-in delay and duration caps are not applied to "
        "them; your bounds are used exactly as sent."),
    RAW_BOUNDS_SCORED: (
        "start_sec and end_sec are scored verbatim — no wash-in delay, no "
        "duration cap, no baseline measured backward from its end, and no "
        "exemption for a label containing \"hi\". Those encode this project's "
        "protocol and are not applied to yours. If the part of a period you "
        "want scored is narrower than the period itself, say so in "
        "analysis_start_sec / analysis_end_sec."),
    # Scoped to the reader, and named per ADR-0002. Both producer-facing documents
    # were corrected on 2026-08-28 (export contract revision 8) to say "runs in
    # `bugarach detect`", because the browser viewer's locust declines without a
    # peak — this string was the last copy still claiming it flatly, and it is the
    # one a producer actually reads. "CICADA" here named the upstream tool for a
    # detector ADR-0002 renamed; the identifier `cicada` is untouched.
    NO_WIDTH: (
        "width_sec is asked for and not required, so this folder conforms and "
        "every detector runs in bugarach detect. What it cannot do is score "
        "per-event durations: locust's per-event mode has nothing to read, and "
        "no other column implies a width. In the browser viewer, which runs "
        "per-event by default, locust also needs a peak. Send width_sec with "
        "the width_def naming the rule that produced it, and send peak_sec if "
        "you have it."),
    PART_WIDTH: (
        "Width is per stream, so a stream without one is simply not available "
        "to per-event duration scoring while the others are."),
    NO_FRAME_INTERVAL: (
        "Three of the six detectors build their analysis grid from it, it is a "
        "property of the microscope, and there is no default — so bugarach "
        "asks rather than guessing. Put it in slices.csv to stop being asked."),
}


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
    #: the producer's own name(s) for the rule behind width_sec, one per stream
    width_defs: list[str] = field(default_factory=list)
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
            r.notes.append(NO_FRAME_INTERVAL)
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
            r.notes.append(NO_WINDOWS)
        else:
            # Loading a folder is not the same as being able to analyse it, so
            # the check resolves the windows too — through
            # `folder_analysis_windows`, which is the SAME function `bugarach
            # detect` calls and not a second reading of the same rules. The
            # second reading is what went wrong: this call site used to derive
            # its own with `effective_region_windows`, which falls through into
            # `region_windows` and halts on a baseline that does not begin at 0
            # or a gap between periods. Those two guards are aCa5z's protocol,
            # correct for a `.mat` store and wrong as a condition of entry for
            # anybody else (FOUNDATIONS §4) — so a lab that started recording
            # before it started treating was told at the door that its legal
            # folder was malformed, and then watched `detect` score it without
            # complaint. Conforming is conforming, and one resolver is how the
            # two commands stay unable to disagree.
            finite = [rg for rg in s.regions if np.isfinite(rg.start_sec)]
            supplied = bool(finite) and all(
                rg.has_analysis_window for rg in finite)
            try:
                folder_analysis_windows(s)
            except ValueError as exc:
                r.errors.append(
                    f"loads, but no detector can run on it: {exc}")
            else:
                # what will actually be scored, said plainly, because the two
                # answers are different numbers and the file does not show which
                r.notes.append(ANALYSIS_WINDOWS_SUPPLIED if supplied
                               else RAW_BOUNDS_SCORED)
        if r.n_silent == 0:
            r.notes.append(NO_SILENCE_DECLARED)
        # width is asked for and not required, so its absence is a note. What it
        # costs is real and invisible from the file: CICADA's per-event duration
        # mode has nothing to run on, and no other column implies the width.
        bare = [n for n, st in s.streams.items() if not st.has_width]
        if bare and len(bare) == len(s.streams):
            r.notes.append(NO_WIDTH)
        elif bare:
            r.notes.append(f"{PART_WIDTH} ({', '.join(sorted(bare))})")
        r.width_defs = sorted({st.width_def for st in s.streams.values()
                               if st.width_def})
        rep.recordings.append(r)

    return rep


NOT_CONFORMING = (
    "NOT CONFORMING — see the export contract: docs/export_folder_spec.md in "
    "the bugarach repo, or export_folder_spec.html beside the one-page "
    "producer guide wherever that was sent to you")


def _wrap(text: str, width: int = 76, indent: str = " " * 9) -> list[str]:
    """Fold one explanation to terminal width. Only used for the folder notes,
    which are said once and can therefore afford to be a sentence."""
    return [indent + line for line in textwrap.wrap(text, width) or [""]]


def _shared_notes(rep: FolderReport) -> tuple[list[tuple[str, list[str]]], set[str]]:
    """Notes that more than one recording carries, and the set of them.

    A note repeated 76 times is not 76 findings; it is one finding about 76
    recordings, and printing it per recording buries the ones that are not.
    """
    order: list[str] = []
    who: dict[str, list[str]] = {}
    for r in rep.recordings:
        for n in r.notes:
            if n not in who:
                order.append(n)
                who[n] = []
            who[n].append(r.slice_id)
    shared = [(n, who[n]) for n in order if len(who[n]) > 1]
    return shared, {n for n, _ in shared}


def format_report(rep: FolderReport) -> str:
    """The report a producer reads in a terminal.

    **The verdict is the second line, not the last.** This is the first command
    a lab runs against its own folder, so what it prints is the app's first
    impression — and the answer to "does my folder conform" should not be at
    the bottom of ninety lines of detail that only matter if it does not.
    """
    if rep.errors:
        out = [f"export folder: {rep.folder}", "", NOT_CONFORMING, ""]
        for e in rep.errors:
            out.append(f"  FAIL  {e}")
        return "\n".join(out)

    verdict = "CONFORMING" if rep.ok else NOT_CONFORMING
    out = [f"export folder: {rep.folder}",
           f"{verdict} — {len(rep.recordings)} recording(s), "
           f"{rep.n_ok} conforming"]

    # Which width rules arrived, named rather than counted: width is defined by
    # the producer and the definition is the only thing that says what the
    # number means. Two rules across two streams is the expected shape, not a
    # warning — a fast transient and a slow one are not measured the same way.
    widths = sorted({d for r in rep.recordings for d in r.width_defs})
    if widths:
        n_with = sum(1 for r in rep.recordings if r.width_defs)
        out.append(f"per-event width: {', '.join(widths)} "
                   f"({n_with} of {len(rep.recordings)} recordings)")
    out.append("")

    shared, collapsed = _shared_notes(rep)
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
        # a note the whole folder shares is said once, below, with its count —
        # here we keep only what is true of THIS recording and not the others
        for n in r.notes:
            if n in collapsed:
                continue
            out.append(f"       · {n}")
            out.extend(_wrap(NOTE_DETAIL[n]) if n in NOTE_DETAIL else [])

    total = len(rep.recordings)
    if shared or rep.notes:
        out.append("")
        out.append("  notes — these read fine and may still not be what you meant:")
    for n, ids in shared:
        scope = ("every recording" if len(ids) == total
                 else f"{len(ids)} of {total} recordings")
        named = "" if len(ids) == total else \
            f" ({', '.join(ids[:4])}{' …' if len(ids) > 4 else ''})"
        out.append(f"       · {n} — {scope}{named}")
        out.extend(_wrap(NOTE_DETAIL[n]) if n in NOTE_DETAIL else [])
    for n in rep.notes:
        out.append(f"       · {n}")
    return "\n".join(out)
