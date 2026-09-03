"""Treatment timing and analysis windows: say they are missing, and offer a start.

Stage one of the loop asks a user for two things beyond the recordings — **when
each treatment ran**, and **which part of each period to score**. Both are
optional under the contract and both were near-silent when absent: no
``regions.csv`` was a `·` note that never fails and sat under ninety lines of
per-recording detail, and missing ``analysis_*`` columns were not mentioned at
all. A user could take a folder through `check`, `assess` and `detect`, get a
table out, and never learn that every number in it came from one unlabelled
window.

**It stays a report, not a refusal, and that is deliberate.** A folder holding
only recording files **conforms** — contract rule 2, and the reason is written in
export contract revision 7: the last time this side turned its own protocol into
a condition of entry, `bugarach check` refused a baseline that did not begin at 0
and **83 of 85** of interface2's recordings were turned away at the door while
`detect` scored them happily. So absence is told loudly and given a way through;
it is never an error.

The way through is :func:`scaffold`, which writes a ``regions.csv`` a person then
edits. It cannot know the treatment names, so it writes
:data:`SCAFFOLD_LABEL` — and `bugarach check` **refuses** a folder still carrying
it. That is the one thing here that does fail a folder, and it is not a protocol
judgement: the contract requires ``label`` to be the period's real name, and a
placeholder is the positional name the contract names as a thing a producer must
not send.
"""

from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path

import numpy as np

from bugarach.detectors.rate import recording_extent
from bugarach.io import RESERVED, load_folder

#: What :func:`scaffold` writes where the treatment name belongs.
#:
#: **Deliberately not a plausible name.** `region 1`, `treatment 2` and `baseline`
#: are all things the contract tells producers not to send, and all three would
#: pass a check and read as real downstream — `baseline` worst of all, because
#: this project's own exporter really does overwrite region 1 with it, so a reader
#: has no way to tell a manufactured claim from a real one. This string is
#: unmistakable, greppable, and refused at the door.
SCAFFOLD_LABEL = "UNNAMED-EDIT-THIS"

#: The header :func:`scaffold` writes, in contract order.
COLUMNS = ("slice_id", "region_idx", "label", "start_sec", "end_sec")
ANALYSIS_COLUMNS = ("analysis_start_sec", "analysis_end_sec")


@dataclass
class RecordingWindows:
    """What one recording says about its own periods."""

    slice_id: str
    n_regions: int
    n_with_analysis: int
    extent: tuple[float, float] | None

    @property
    def has_timing(self) -> bool:
        return self.n_regions > 0

    @property
    def has_analysis(self) -> bool:
        """All regions or none — half an analysis window is refused by the
        contract, so a partial count here is a producer bug rather than a
        partial answer, and this reports it as *not supplied*."""
        return self.n_regions > 0 and self.n_with_analysis == self.n_regions


@dataclass
class FolderWindows:
    folder: Path
    recordings: list[RecordingWindows]
    has_regions_file: bool

    @property
    def missing_timing(self) -> list[str]:
        return [r.slice_id for r in self.recordings if not r.has_timing]

    @property
    def missing_analysis(self) -> list[str]:
        """Recordings that HAVE periods and no analysis windows.

        A recording with no periods at all is not counted here: it is missing the
        first thing, and telling someone about the second while the first is
        absent buries the one that matters.
        """
        return [r.slice_id for r in self.recordings
                if r.has_timing and not r.has_analysis]


def describe(folder) -> FolderWindows:
    """What the folder states about periods, per recording."""
    folder = Path(folder)
    out = []
    for s in load_folder(folder):
        finite = [rg for rg in s.regions if np.isfinite(rg.start_sec)]
        try:
            extent = recording_extent(s)
        except ValueError:
            extent = None
        out.append(RecordingWindows(
            slice_id=s.slice_id,
            n_regions=len(finite),
            n_with_analysis=sum(1 for rg in finite if rg.has_analysis_window),
            extent=extent))
    return FolderWindows(folder=folder, recordings=out,
                         has_regions_file=(folder / "regions.csv").is_file())


class RegionsFileExists(FileExistsError):
    """Refused rather than overwritten. A `regions.csv` is a person's record of
    what they did to the tissue; regenerating it from event times would replace
    that record with a guess, and the guess looks identical in a diff."""


def scaffold(folder, *, with_analysis: bool = False,
             force: bool = False) -> tuple[Path, list[dict]]:
    """Write a ``regions.csv`` for a person to edit. Returns (path, rows).

    One row per recording, spanning that recording's own event extent, with the
    label left as :data:`SCAFFOLD_LABEL`.

    **The bounds are a starting point and the caller must say so.** They come
    from the first and last event time, which is not the recording's extent —
    nothing in the folder carries that — and a period that began before the first
    event or ran past the last one is invisible here. A user who ran two
    treatments has to add the rows; this cannot know how many there were.
    """
    folder = Path(folder)
    path = folder / "regions.csv"
    if path.is_file() and not force:
        raise RegionsFileExists(
            f"{path} already exists. It records what a person did to the "
            f"tissue, so this will not overwrite it — edit it, or pass "
            f"force=True if you are certain it is a stale scaffold.")

    cols = list(COLUMNS) + (list(ANALYSIS_COLUMNS) if with_analysis else [])
    rows = []
    for r in describe(folder).recordings:
        if r.extent is None:
            continue
        lo, hi = r.extent
        row = {"slice_id": r.slice_id, "region_idx": 1,
               "label": SCAFFOLD_LABEL,
               "start_sec": f"{lo:.6g}", "end_sec": f"{hi:.6g}"}
        if with_analysis:
            row["analysis_start_sec"] = f"{lo:.6g}"
            row["analysis_end_sec"] = f"{hi:.6g}"
        rows.append(row)

    if not rows:
        raise ValueError(
            f"no recording in {folder} has a usable event extent, so there is "
            f"nothing to scaffold bounds from")

    # newline="" and \n line endings, per the contract's own format rule — the
    # file this writes has to pass the check that reads it.
    with path.open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=cols, lineterminator="\n")
        w.writeheader()
        w.writerows(rows)
    return path, rows


def format_windows(fw: FolderWindows) -> str:
    """The report `bugarach windows` prints."""
    out = [f"export folder: {fw.folder}",
           f"{len(fw.recordings)} recording(s), "
           f"{sum(1 for r in fw.recordings if r.has_timing)} with treatment "
           f"timing, "
           f"{sum(1 for r in fw.recordings if r.has_analysis)} with analysis "
           f"windows",
           ""]
    w = max((len(r.slice_id) for r in fw.recordings), default=10)
    for r in fw.recordings:
        timing = f"{r.n_regions} period(s)" if r.has_timing else "NO PERIODS"
        if not r.has_timing:
            analysis = "—"
        elif r.has_analysis:
            analysis = "analysis windows on all"
        elif r.n_with_analysis:
            analysis = (f"analysis windows on {r.n_with_analysis} of "
                        f"{r.n_regions} — REFUSED, all or none")
        else:
            analysis = "raw bounds scored whole"
        span = ("—" if r.extent is None
                else f"events {r.extent[0]:.0f}–{r.extent[1]:.0f}s")
        out.append(f"  {r.slice_id:<{w}}  {timing:<14}  {analysis:<44}  {span}")
    return "\n".join(out)
