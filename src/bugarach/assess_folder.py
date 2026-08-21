"""Point the assessment at an export folder — a lab's own recordings, measured.

    bugarach assess my_export/

``bugarach check`` answers *can this folder be read*. This answers the next
question a lab actually has: **how coordinated are these recordings**, measured
without any detector's opinion in it. :mod:`bugarach.assess` does the measuring;
this module is only the part that knows about folders, windows and what may be
reported.

**It reports; it does not decide.** Three rules it inherits rather than invents:

* **K is a scan, never a choice.** ``min_rois`` changes the headline by an order of
  magnitude, so every K is printed and none is picked. A caller quoting one number
  must say which K produced it.
* **``jit_defined`` is a state, not a NaN.** The tightness comparison can be
  undefined while a finite-looking number sits in the field, and a reader who takes
  the number and skips the flag parameterizes tightness off nothing.
* **Baseline regions only.** FOUNDATIONS §9 — treatments are what the instruments
  are pointed at, so taking coordination properties from them assumes the answer.
  Non-baseline regions are counted and skipped, and the count is printed so the
  skip is visible rather than silent.

Nothing here writes, and nothing here turns a measurement into a generator
parameter. That step needs a human who has looked at the recording — see
``docs/todo/2026-08-16-assessment-needs-a-human-in-the-loop.md``.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

# The vocabulary a lab actually writes for an untreated period. Deliberately does
# NOT fall back to "region 1 is the baseline": the export contract calls that out
# as something producers must not do, and this project's own MATLAB exporter has
# done it. An unnamed region is skipped and counted, never guessed at.
BASELINE_TOKENS = ("baseline", "base", "pre", "control", "acsf")


def is_baseline(region) -> bool:
    """True when a region's own name says it is untreated."""
    name = (getattr(region, "name", None) or "").strip().lower()
    return bool(name) and any(name.startswith(t) for t in BASELINE_TOKENS)


@dataclass
class RecordingAssessment:
    """One recording's assessment, or the reason there isn't one."""

    slice_id: str
    stream: str | None = None
    n_roi: int = 0
    window: tuple[float, float] | None = None
    window_source: str = ""
    """How the window was chosen — ``"baseline region <name>"`` or
    ``"whole recording (no regions declared)"``. Printed, because the window is
    half of what a number means."""
    results: list = field(default_factory=list)
    """One :class:`bugarach.assess.Assessment` per K, in scan order."""
    skipped: str = ""
    """Non-empty means nothing was measured, and this says why."""


@dataclass
class FolderAssessment:
    folder: Path
    records: list[RecordingAssessment] = field(default_factory=list)
    stream_asked: str | None = None
    n_surrogates: int = 1000
    bin_width_sec: float | None = None
    region_counts: dict = field(default_factory=dict)

    @property
    def measured(self) -> list[RecordingAssessment]:
        return [r for r in self.records if not r.skipped]

    @property
    def skipped(self) -> list[RecordingAssessment]:
        return [r for r in self.records if r.skipped]


def assess_folder(folder, *, stream: str | None = None,
                  n_surrogates: int = 1000, bin_width_sec: float | None = None,
                  limit: int | None = None) -> FolderAssessment:
    """Assess every recording in an export folder that may be assessed.

    Reads the folder with the same loader the rest of bugarach uses, so a folder
    that passes ``bugarach check`` is a folder this can read.
    """
    from bugarach.assess import assess_coactivity
    from bugarach.io import load_folder

    folder = Path(folder)
    out = FolderAssessment(folder=folder, stream_asked=stream,
                           n_surrogates=n_surrogates, bin_width_sec=bin_width_sec)

    slices = load_folder(folder)
    if limit is not None:
        slices = slices[:limit]

    for s in slices:
        rec = RecordingAssessment(slice_id=s.slice_id)
        out.records.append(rec)

        for r in (s.regions or []):
            nm = (getattr(r, "name", None) or "<unnamed>").strip().lower()
            out.region_counts[nm] = out.region_counts.get(nm, 0) + 1

        names = list(s.streams)
        if not names:
            rec.skipped = "no streams in the recording"
            continue
        want = stream if stream in names else names[0]
        rec.stream = want
        rec.n_roi = s.streams[want].n_rois

        regions = list(s.regions or [])
        if not regions:
            # A folder with no regions.csv is the common case for a lab that has
            # not declared its periods. The contract gives such a recording one
            # implicit whole-recording window, so it gets assessed rather than
            # dropped — but the window it got is named in the report, because a
            # whole-recording window is an assumption and not a baseline.
            window = None
            rec.window_source = "whole recording (no regions declared)"
        else:
            base = [r for r in regions if is_baseline(r)]
            if not base:
                rec.skipped = (
                    f"{len(regions)} region(s), none named as a baseline — "
                    f"coordination properties are not taken from treatments")
                continue
            r = max(base, key=lambda r: r.end_sec - r.start_sec)
            # The producer's own analysis window WINS wherever the folder states
            # one. `start_sec`/`end_sec` are what happened; `analysis_*` is what
            # to score, and they are rarely the same once a wash-in delay or a
            # cap has been applied. Measuring the raw period while calling the
            # result the analysis is the defect this line exists to prevent —
            # and it was live for a few hours on 2026-08-18, with the viewer
            # shading the analysis window and both assessors measuring the raw
            # one.
            if r.has_analysis_window:
                window = (float(r.analysis_start_sec), float(r.analysis_end_sec))
                rec.window_source = (f"baseline region {r.name!r}, "
                                     f"analysis window as the folder states it")
            else:
                window = (r.start_sec, r.end_sec)
                rec.window_source = (f"baseline region {r.name!r}, whole period "
                                     f"(no analysis window sent)")
            rec.window = window

        try:
            rec.results = assess_coactivity(
                s, stream=want, window=window, n_surrogates=n_surrogates,
                **({} if bin_width_sec is None else {"bin_width_sec": bin_width_sec}))
        except Exception as e:                        # noqa: BLE001
            rec.skipped = f"{type(e).__name__}: {e}"
            continue
        if window is None and rec.results:
            a = rec.results[0]
            rec.window = (0.0, float(a.win_dur))

    return out


def _fmt(x, nd=3, missing="—"):
    """A number, or a dash. Never the string 'nan' — a reader skims past 'nan'
    as a rendering artifact and reads it as zero."""
    try:
        if x != x:                                    # NaN
            return missing
        return f"{x:.{nd}f}"
    except (TypeError, ValueError):
        return missing


def format_assessment(fa: FolderAssessment) -> str:
    """The scoreboard. One block per recording, one row per K."""
    L: list[str] = []
    L.append(f"export folder: {fa.folder}")
    L.append(f"{len(fa.records)} recording(s), {len(fa.measured)} assessed, "
             f"{len(fa.skipped)} not")
    bw = "1.0 (default)" if fa.bin_width_sec is None else f"{fa.bin_width_sec}"
    L.append(f"conventions: {fa.n_surrogates} circular-shift surrogates · "
             f"bin {bw} s · stream "
             + (fa.stream_asked or "first in each recording"))
    L.append("")

    for rec in fa.records:
        head = f"  {rec.slice_id}"
        if rec.skipped:
            L.append(f"{head}  — not assessed: {rec.skipped}")
            continue
        span = ""
        if rec.window:
            span = f"  {(rec.window[1] - rec.window[0]) / 60:.1f} min"
        L.append(f"{head}  {rec.n_roi} ROI  stream {rec.stream}{span}")
        L.append(f"      window: {rec.window_source}")

        if rec.results and not rec.results[0].meets_floor:
            a = rec.results[0]
            L.append(f"      window is {a.win_dur / 60:.1f} min, under the "
                     f"assessment's floor — every measure is undefined, and "
                     f"none is printed")
            continue

        L.append("       K   coact excess/min   clusters/min   participants   "
                 "span (s)   tightness vs null")
        for a in rec.results:
            jit = (f"{_fmt(a.jit_excess)}"
                   if a.jit_defined else "undefined (no cluster in surrogates)")
            L.append(f"      {a.min_rois:>2}   {_fmt(a.coact_excess):>15}   "
                     f"{_fmt(a.clusters_permin):>12}   {_fmt(a.part_n_obs, 1):>12}   "
                     f"{_fmt(a.span_med):>8}   {jit}")
        L.append("")

    if fa.region_counts:
        seen = ", ".join(f"{k} ({v})" for k, v in sorted(fa.region_counts.items()))
        L.append(f"  regions seen across the folder: {seen}")
    L.append("")
    L.append("  K is a scan, not a choice. It moves the headline by an order of")
    L.append("  magnitude, so quoting one of these numbers means naming the K it")
    L.append("  came from. Nothing here has picked one, and nothing here has")
    L.append("  turned a measurement into a setting — that needs somebody who has")
    L.append("  looked at the recording.")
    return "\n".join(L)
