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

from bugarach.dataset import preferred_stream

# The vocabulary a lab actually writes for an untreated period. Deliberately does
# NOT fall back to "region 1 is the baseline": the export contract calls that out
# as something producers must not do, and this project's own MATLAB exporter has
# done it. An unnamed region is skipped and counted, never guessed at.
BASELINE_TOKENS = ("baseline", "base", "pre", "control", "acsf")


def is_baseline(region, designated: tuple[str, ...] | None = None) -> bool:
    """True when this region is the untreated one.

    ``designated`` is what the READER said their baseline is called, and when
    it is given it REPLACES the vocabulary above rather than adding to it.
    Replacing is the point: a lab that designates ``vehicle`` and also has a
    period called ``pre-wash`` means the first one, and a rule that kept
    guessing alongside the designation would quietly measure the other.

    Tony, 2026-09-10 — *"can we use whatever the user provides as baseline.
    maybe they call it control, or 'pre'"*. Both of those were already in the
    list; the ones that were not (``vehicle``, ``naive``, ``ctrl``) had no way
    in at all, and the folder walk skipped those recordings rather than asking.
    The answer is not a longer list. This page's own rule is that **the
    baseline is designated, not detected** — the tokens are the opening guess
    for a reader who has not said, and nothing more.

    Matching is a case-insensitive prefix either way, so ``vehicle`` covers
    ``Vehicle 2`` the same way ``pre`` covers ``pre-drug``.
    """
    name = (getattr(region, "name", None) or "").strip().lower()
    want = tuple(d.strip().lower() for d in (designated or ()) if d.strip())
    return bool(name) and any(name.startswith(t) for t in (want or BASELINE_TOKENS))


WHOLE_RECORDING_SOURCE = "whole recording (no regions declared)"
"""The ``source`` :func:`generation_window` names when it had to assume."""


class NoBaselineRegion(ValueError):
    """The recording declares regions and none of them is a baseline.

    Raised rather than returned, because the recording is skipped: coordination
    properties are not taken from treatments (FOUNDATIONS §9). The message names
    what the recording does call its periods, so the reader can designate one."""


def generation_window(s, *, baseline_labels: tuple[str, ...] | None = None
                      ) -> tuple[tuple[float, float] | None, str]:
    """The span to measure one recording over, and who chose it.

    Returns ``(window, source)``. ``window`` is ``(start_sec, end_sec)``, or
    ``None`` for the whole recording; ``source`` is the sentence a report prints
    beside the number, because the window is half of what a number means.

    Two fallbacks, both kept deliberately:

    * **No regions declared** — the whole recording, ``window=None``, with
      :data:`WHOLE_RECORDING_SOURCE` as the source. The export contract gives such
      a recording one implicit whole-recording window, so it is measured rather
      than dropped, but a whole-recording window is an assumption and not a
      baseline, and the source says so.
    * **Regions declared, none a baseline** — :class:`NoBaselineRegion` is
      raised and the recording is skipped.

    Otherwise the longest baseline region wins, and the producer's own analysis
    window wins inside it wherever the folder states one.

    Moved here out of :func:`assess_folder` (2026-09-11) so the surrogate screen
    reads the same rule rather than a sixth copy of it. The five older copies in
    ``tools/`` are left for their own change.
    """
    regions = list(s.regions or [])
    if not regions:
        # A folder with no regions.csv is the common case for a lab that has
        # not declared its periods. The contract gives such a recording one
        # implicit whole-recording window, so it gets assessed rather than
        # dropped — but the window it got is named in the report, because a
        # whole-recording window is an assumption and not a baseline.
        return None, WHOLE_RECORDING_SOURCE
    base = [r for r in regions if is_baseline(r, baseline_labels)]
    if not base:
        # Name what IS there. The reader's next move is to designate one
        # of these, and they cannot do that without knowing what the
        # folder calls its periods — "none named as a baseline" alone
        # sends them to open a CSV.
        seen = sorted({(r.name or "(unnamed)") for r in regions})
        how = (f"you designated {', '.join(baseline_labels)}"
               if baseline_labels else
               f"looked for {', '.join(BASELINE_TOKENS)}")
        raise NoBaselineRegion(
            f"{len(regions)} region(s), none named as a baseline "
            f"({how}; this recording has {', '.join(seen)}) — "
            f"coordination properties are not taken from treatments")
    r = max(base, key=lambda r: r.end_sec - r.start_sec)
    # The producer's own analysis window WINS wherever the folder states
    # one. `start_sec`/`end_sec` are what happened; `analysis_*` is what
    # to score, and they are rarely the same once a wash-in delay or a
    # cap has been applied. Measuring the raw period while calling the
    # result the analysis is the defect this line exists to prevent —
    # and it was live for a few hours on 2026-08-18, with the viewer
    # shading the analysis window and both assessors measuring the raw
    # one.
    # Who decided this region was the baseline travels with the window,
    # because "we matched your word" and "we guessed from a built-in
    # list" are different claims and only one of them is the reader's.
    why = " (you designated it)" if baseline_labels else ""
    if r.has_analysis_window:
        return ((float(r.analysis_start_sec), float(r.analysis_end_sec)),
                f"baseline region {r.name!r}{why}, "
                f"analysis window as the folder states it")
    return ((r.start_sec, r.end_sec),
            f"baseline region {r.name!r}{why}, whole "
            f"period (no analysis window sent)")


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

    @property
    def assumed(self) -> list[RecordingAssessment]:
        """Assessed on the WHOLE RECORDING, because the folder declared no
        periods for them.

        The window is the right one — the export contract gives an unannotated
        recording a single region spanning its own extent — but it is this
        project's assumption rather than the producer's statement, and if such
        a recording is in fact a treated preparation, nothing downstream would
        say so. Each already carries it in ``window_source``; this counts them
        so the summary can say it once, at the top, where a reader who is not
        reading every block still meets it.

        Keyed on ``window_source`` and NOT on ``window is None``: a measured
        recording's window is backfilled from its own result once the extent is
        known, so by the time anyone asks, the window is a pair of numbers
        whichever way it was chosen. ``window_source`` is the part that still
        remembers who chose it."""
        return [r for r in self.measured
                if "no regions declared" in r.window_source]


def assess_folder(folder, *, stream: str | None = None,
                  n_surrogates: int = 1000, bin_width_sec: float | None = None,
                  limit: int | None = None, progress=None,
                  min_rois=None, min_rois_frac=None,
                  min_rois_floor: int | None = None,
                  baseline_labels: tuple[str, ...] | None = None,
                  ) -> FolderAssessment:
    """Assess every recording in an export folder that may be assessed.

    Reads the folder with the same loader the rest of bugarach uses, so a folder
    that passes ``bugarach check`` is a folder this can read.

    ``progress`` is called as ``progress(done, total, slice_id)`` before each
    recording, and once more with ``None`` when the last one finishes. It exists
    because this runs for **two minutes** on a real folder — 117 s over 84
    recordings at a thousand circular-shift surrogates each — and printed
    nothing whatever until the report arrived complete at the end. A user cannot
    tell that from a hang, and on the flagship folder command that is a defect
    rather than a missing nicety.
    """
    from bugarach.assess import assess_coactivity
    from bugarach.io import load_folder

    folder = Path(folder)
    out = FolderAssessment(folder=folder, stream_asked=stream,
                           n_surrogates=n_surrogates, bin_width_sec=bin_width_sec)

    slices = load_folder(folder)
    if limit is not None:
        slices = slices[:limit]

    for i, s in enumerate(slices):
        if progress is not None:
            progress(i, len(slices), s.slice_id)
        rec = RecordingAssessment(slice_id=s.slice_id)
        out.records.append(rec)

        for r in (s.regions or []):
            nm = (getattr(r, "name", None) or "<unnamed>").strip().lower()
            out.region_counts[nm] = out.region_counts.get(nm, 0) + 1

        names = list(s.streams)
        if not names:
            rec.skipped = "no streams in the recording"
            continue
        # Was `names[0]` — a silent choice between two utterly different
        # measurements, decided by dict order. `dataset.preferred_stream` is the
        # declared answer; a caller naming a stream still wins.
        want = stream if stream in names else preferred_stream(names)
        rec.stream = want
        rec.n_roi = s.streams[want].n_rois

        # The rule lives in `generation_window` so the surrogate screen reads
        # the same one; both fallbacks are there, unchanged.
        try:
            window, rec.window_source = generation_window(
                s, baseline_labels=baseline_labels)
        except NoBaselineRegion as e:
            rec.skipped = str(e)
            continue
        if window is not None:
            rec.window = window

        try:
            rec.results = assess_coactivity(
                s, stream=want, window=window, n_surrogates=n_surrogates,
                **({} if min_rois is None else {"min_rois": tuple(min_rois)}),
                **({} if min_rois_frac is None
                   else {"min_rois_frac": tuple(min_rois_frac)}),
                **({} if min_rois_floor is None
                   else {"min_rois_floor": int(min_rois_floor)}),
                **({} if bin_width_sec is None else {"bin_width_sec": bin_width_sec}))
        except Exception as e:                        # noqa: BLE001
            rec.skipped = f"{type(e).__name__}: {e}"
            continue
        if window is None and rec.results:
            a = rec.results[0]
            rec.window = (0.0, float(a.win_dur))

    if progress is not None:
        progress(len(slices), len(slices), None)
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
    # Said once, at the top. The per-recording `window:` line has always
    # carried it, but a reader scanning 84 blocks for numbers is not reading
    # 84 window lines, and "we measured the whole recording because nobody told
    # us what the periods were" is the kind of thing that has to arrive before
    # the numbers rather than beside them.
    if fa.assumed:
        L.append(f"⚠ {len(fa.assumed)} of them declare no regions, so the WHOLE "
                 f"RECORDING was used: "
                 + ", ".join(r.slice_id for r in fa.assumed[:6])
                 + (" …" if len(fa.assumed) > 6 else "")
                 + ". That window is an assumption of ours, not the folder's "
                   "statement — if any is a treated preparation, it is being "
                   "read as a baseline.")
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

        # When K came from a percentage, BOTH numbers go in the row. The
        # percentage is what a person set and is the same on every recording;
        # the count is what it became here and is not. Printing only the first
        # hides that 10% is a floor of 1 on a small field; only the second hides
        # that one setting produced them.
        by_frac = any(a.min_rois_frac is not None for a in rec.results)
        head = "  K (% of ROI)" if by_frac else "       K"
        L.append(f"{head}   coact excess/min   clusters/min   participants   "
                 f"span (s)   tightness vs null")
        for a in rec.results:
            jit = (f"{_fmt(a.jit_excess)}"
                   if a.jit_defined else "undefined (no cluster in surrogates)")
            if by_frac:
                pct = ("—" if a.min_rois_frac is None
                       else f"{100.0 * a.min_rois_frac:g}%")
                lead = f"  {a.min_rois:>3} ({pct:>5})"
            else:
                lead = f"      {a.min_rois:>2}"
            L.append(f"{lead}   {_fmt(a.coact_excess):>15}   "
                     f"{_fmt(a.clusters_permin):>12}   {_fmt(a.part_n_obs, 1):>12}   "
                     f"{_fmt(a.span_med):>8}   {jit}")
        if by_frac and any(a.min_rois == 1 for a in rec.results):
            L.append("       ⚠ a percentage rounded to K=1 here — one co-active "
                     "ROI is no floor at all")
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
