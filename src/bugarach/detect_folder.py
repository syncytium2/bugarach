"""Export folder in, ``detections.csv`` out — the headless route.

    bugarach detect my_export/

``check`` says whether a folder can be read and ``assess`` says how coordinated
it is without a detector. This is the third question and the one the six ports
exist to answer: **run them, and write the events down.**

Until this module there was no way to do that outside a browser. ``emit`` — the
writer for the whole output contract — had no caller anywhere in ``src/`` or
``tools/``, so a lab wanting a detections file had to open the page, click
through it and save by hand. Nothing could be scripted, scheduled, or run over
84 recordings while somebody had lunch.

The windowing default, and why it is not the store's
----------------------------------------------------
A recording that states ``analysis_start_sec`` / ``analysis_end_sec`` is scored
on exactly those bounds. **A recording that states nothing is scored on its raw
period bounds, with no protocol applied at all** — no wash-in delay, no cap, no
backward-measured baseline, no ``"hi"``-substring exemption, and none of the
HALT guards that require a baseline to begin at 0 and the periods to be
contiguous.

That is Tony's decision of 2026-08-18, point 4, recorded in
``docs/todo/2026-08-18-windowing-default-and-the-three-delta-interface.md`` and
never applied to code until now. It is also what FOUNDATIONS §4 has said all
along: store input derives its windows, folder input does not, and *"the two
paths must not be merged"*. What was actually happening is that the folder path
fell **through** into the store path — ``effective_region_windows`` tries the
producer's windows, and where there are none it calls ``region_windows``, which
is a 1e-9 parity port of this lab's own convention and halts on anything else.
A lab that recorded before it started treating, or left the tissue alone between
conditions, is describing its experiment; it was getting a refusal.

**The parity port is untouched**, which is the constraint the decision came
with. ``region_windows`` still encodes aCa5z's convention, still halts on the
data it was written for, and is still what a ``.mat`` store gets. This module
settles the folder's windows **once, before any detector runs**, by writing them
into the region rows as analysis windows. Every detector then reads them through
``supplied_region_windows`` — including ``sce_detect`` and ``cicada_detect``,
which derive their own windows internally and have no argument to divert. One
resolution, one policy, and the producer's bounds are validated by the same door
a producer's own windows go through.

Two detector families, and they see different spans
----------------------------------------------------
``loco``, ``sce`` and ``cicada`` take the whole recording and window it
themselves, so they scan the full extent and tag each event with the period it
landed in — including events that landed in none, when ``regions.csv`` stops
before the recording does. ``rate``, ``coact`` and ``sync`` take a stream and a
time range, and are run **once per declared window**: their rolling context then
stays inside one condition instead of straddling a treatment boundary, and every
row they produce carries the producer's own ``region_idx``. The consequence is
worth knowing rather than hiding — only the first three can report a detection
outside every declared period, and the run summary says how many did.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field, replace
from pathlib import Path

import numpy as np

from bugarach.emit import (
    events_from,
    write_detections,
    write_detector_settings,
    write_run,
)
from bugarach.store import Slice

#: Seed for every detector that draws surrogates, so a run reproduces. Written
#: into ``detector_settings.csv`` beside the parameters rather than left as a
#: default in code — a setting a reader cannot see is a setting they cannot
#: reproduce.
RNG_SEED = 20260706

#: The six, in the order the glossary names them. Three take a stream's trains
#: and a time range; three take the whole slice and window it themselves.
FLAT = ("rate", "coact", "sync")
NESTED = ("loco", "sce", "cicada")
DETECTORS = ("rate", "coact", "loco", "sce", "cicada", "sync")

#: Which per-event time each detector anchors on. Recorded in
#: ``detector_settings.csv`` rather than left implicit, because **the six do not
#: agree and that is deliberate**: CICADA anchors on the peak (``locs``) and the
#: rest on the half-rise (``t50rise``). The gap between the two runs ~0.3 s in a
#: fast stream and ~2 s in a slow one — wider than the tolerance a detection is
#: scored at — so a reader who assumes one convention for all six reads the
#: wrong thing off five columns. :mod:`bugarach.store` has the full note,
#: including why cicada's is not to be "corrected".
ONSET_FIELD = {"rate": "t50rise", "coact": "t50rise", "sync": "t50rise",
               "loco": "t50rise", "sce": "t50rise", "cicada": "locs"}


@dataclass
class RecordingDetections:
    """One recording's events, or the reason there are none."""

    slice_id: str
    n_roi: int = 0
    streams: tuple[str, ...] = ()
    windows: list[dict] = field(default_factory=list)
    n_events: int = 0
    n_outside: int = 0
    """Detections that fell in no declared period. Not an error: the three
    region-aware ports scan the whole recording, so a ``regions.csv`` that
    covers less than the recording produces them, and saying so is how a reader
    finds out the periods stop before the data does."""
    seconds: float = 0.0
    frame_interval_sec: float | None = None
    skipped: str = ""
    """Non-empty means the recording produced nothing, and this says why. An
    empty result and an absent one are different findings."""


@dataclass
class DetectionRun:
    folder: Path
    out_dir: Path
    detectors: tuple[str, ...]
    stream_asked: str | None
    records: list[RecordingDetections] = field(default_factory=list)
    n_events: int = 0
    seconds: float = 0.0
    paths: dict[str, Path] = field(default_factory=dict)

    @property
    def detected(self) -> list[RecordingDetections]:
        return [r for r in self.records if not r.skipped]

    @property
    def skipped(self) -> list[RecordingDetections]:
        return [r for r in self.records if r.skipped]


def with_folder_windows(s: Slice) -> Slice:
    """Settle this recording's analysis windows before any detector sees it.

    Where the producer stated windows, nothing changes — they are already the
    thing every detector reads. Where the producer stated none, the **raw period
    bounds become the analysis window verbatim**, which is how a folder gets
    "no protocol at all" out of machinery whose only other setting is this
    lab's protocol.

    Returns a new :class:`~bugarach.store.Slice`; the caller's is untouched, so
    a slice can still be handed to the store path afterwards.

    Three cases are deliberately left alone. A recording with no regions keeps
    none, and gets the implicit whole-recording window every consumer already
    gives it. A recording where *some* regions carry a window and others do not
    is not repaired — that is two policies inside one number, and
    ``supplied_region_windows`` says so in terms. A region whose start is not a
    finite time is skipped by every window function anyway.
    """
    regs = [r for r in s.regions if np.isfinite(r.start_sec)]
    if not regs or any(r.has_analysis_window for r in regs):
        return s
    return replace(s, regions=[
        replace(r, analysis_start_sec=float(r.start_sec),
                analysis_end_sec=float(r.end_sec))
        if np.isfinite(r.start_sec) else r
        for r in s.regions])


def folder_analysis_windows(s: Slice):
    """A folder recording, settled, and the windows it will be scored on.

    **The one place the folder path answers this question**, and the reason it
    is a function rather than three lines repeated at each call site: ``detect``
    and ``check`` had a copy each, the copies disagreed, and the answer a lab
    got depended on which command they ran. A folder that is legal under the
    contract — a baseline beginning at 500 s, a gap after it — was refused at
    the door by ``check`` and then scored happily by ``detect``, which is worse
    than either behaviour alone because nothing tells the lab which answer is
    true. ``tests/test_check_detect_agree.py`` pins the two together.

    Returns ``(slice, windows)`` and **both halves matter**. ``loco``, ``sce``
    and ``cicada`` take the whole recording and re-derive their own windows from
    its regions, with no argument that could divert them — so a caller that kept
    the unsettled slice would resolve one policy here and hand a different one
    to three of the six detectors. The settled slice is the thing to pass on.

    Idempotent: settling an already-settled recording changes nothing.
    """
    from bugarach.detectors.loco import effective_region_windows
    from bugarach.detectors.rate import recording_extent

    s = with_folder_windows(s)
    return s, effective_region_windows(s, recording_extent(s))


def _region_index(window) -> int | None:
    """The producer's own ``region_idx``, carried through the window.

    ``load_folder`` puts it in ``Region.slot``, so it survives into the
    ``RegionWindow`` a detector reports against. The implicit whole-recording
    window has no slot, and gets no index rather than an invented one.
    """
    try:
        return int(window.slot)
    except (TypeError, ValueError):
        return None


def _by_label(windows) -> dict[str, object]:
    """Label -> window, for the three detectors that report a label per event.

    Only where labels are unique. Two regions with one name cannot be told
    apart from the label alone, and guessing which is which would put the wrong
    index on a row that no reader could check.
    """
    seen: dict[str, object] = {}
    for w in windows:
        if w.label in seen:
            seen[w.label] = None
        else:
            seen[w.label] = w
    return {k: v for k, v in seen.items() if v is not None}


def detector_params(name: str, *, frame_interval_sec: float) -> dict:
    """One detector's shipped operating point, plus what the recording decides.

    The settings come from :data:`bugarach.bench.OPERATING_POINTS`, which is the
    one place in the tree that records a calibrated point together with where it
    came from. Two values are taken from the **recording** instead, because they
    are properties of the microscope and not of the calibration:

    * ``rate.grid_dt`` — the bench's 0.1 s is the generator's own grid, and the
      detector's docstring says the value MUST be the acquisition interval.
    * ``cicada.imaging_rate_hz`` — otherwise 10.0 in silence for a rig that is
      not 10 Hz, which is exactly the failure FOUNDATIONS §6 exists to prevent.
    """
    from bugarach.bench import OPERATING_POINTS

    op = OPERATING_POINTS[name]
    params = dict(op.params)
    if op.takes_rng:
        params["rng_seed"] = RNG_SEED
    if name == "rate":
        params["grid_dt"] = float(frame_interval_sec)
    elif name == "cicada":
        params["imaging_rate_hz"] = 1.0 / float(frame_interval_sec)
    return params


def _run_flat(name, s, windows, want_streams, params, identity):
    from bugarach.detectors.coact import coact_detect
    from bugarach.detectors.rate import rate_detect, stream_trains
    from bugarach.detectors.sync import sync_detect

    out = []
    for w in windows:
        span = (float(w.win_start), float(w.win_end))
        if span[1] <= span[0]:
            continue
        idx = _region_index(w)
        for sname in want_streams:
            st = s.streams[sname]
            if name == "rate":
                res = rate_detect(stream_trains(st, span), span, **params)
            elif name == "coact":
                res = coact_detect(st.t50rise, span, **params)
            else:
                res = sync_detect(st.t50rise, span, **params)
            out.extend(events_from(
                res, detector=name, slice_id=s.slice_id, stream=sname,
                region_idx=idx, region_label=w.label or None,
                identity=identity))
    return out


def _run_nested(name, s, windows, want_streams, params, identity):
    from bugarach.detectors.cicada import cicada_detect
    from bugarach.detectors.loco import loco_detect
    from bugarach.detectors.sce import sce_detect

    fn = {"loco": loco_detect, "sce": sce_detect, "cicada": cicada_detect}[name]
    # Every stream runs, even when only one was asked for: the three draw their
    # surrogates from ONE RNG stream in declaration order, so dropping a stream
    # from the call changes the numbers of the ones that remain (FOUNDATIONS
    # §2). The filter belongs on the output, not on the input.
    det = fn(s, **params)
    lookup = _by_label(windows)
    declared = {w.label for w in windows}
    out = []
    for sname in want_streams:
        res = det.streams[sname]
        rows = events_from(res, detector=name, slice_id=s.slice_id,
                           stream=sname, identity=identity)
        for row in rows:
            w = lookup.get(row.region_label)
            if w is None:
                w = next((x for x in windows
                          if x.win_start <= row.onset_sec <= x.win_end), None)
            if w is None and row.region_label not in declared:
                # The three region-aware ports scan the whole recording and tag
                # each event with the period it landed in, writing the literal
                # "none" where it landed in no declared period. That string is
                # bugarach's, and this column is the producer's own name for a
                # period — so it is written as missing rather than as a name
                # nobody sent. Contract rule 7: missing is written as missing.
                # A producer who really named a period "none" keeps it: the test
                # is whether the folder declared the label, not what it spells.
                row.region_label = None
            row.region_idx = None if w is None else _region_index(w)
        out.extend(rows)
    return out


def detect_slice(s: Slice, *, detectors=DETECTORS, stream: str | None = None,
                 frame_interval_sec: float | None = None):
    """Run the detectors over one recording. Returns ``(events, windows)``.

    ``s`` is taken as it came out of :func:`bugarach.io.load_folder`; the
    windowing is settled here, so a caller cannot forget to.
    """
    s, windows = folder_analysis_windows(s)

    names = list(s.streams)
    want = [n for n in names if stream is None or n == stream]
    if not want:
        raise ValueError(
            f"{s.slice_id}: no stream named {stream!r} — this recording carries "
            f"{', '.join(names)}. Stream names are the lab's own strings and "
            f"bugarach does not translate them")

    if frame_interval_sec is None:
        raise ValueError(
            f"{s.slice_id}: no frame interval. Three detectors build their "
            f"analysis grid from it, it cannot be recovered from onset times, "
            f"and there is no default because a default here is a guess about "
            f"somebody else's microscope (FOUNDATIONS §6). Put "
            f"frame_interval_sec in slices.csv, or pass --frame-interval")

    identity = dict(s.meta)
    events = []
    for name in detectors:
        params = detector_params(name, frame_interval_sec=frame_interval_sec)
        runner = _run_flat if name in FLAT else _run_nested
        events.extend(runner(name, s, windows, want, params, identity))
    return events, windows


def detect_folder(folder, *, out_dir, detectors=DETECTORS,
                  stream: str | None = None,
                  frame_interval_sec: float | None = None,
                  limit: int | None = None, progress=None) -> DetectionRun:
    """Detect over a whole export folder and write the output contract.

    Writes three files into ``out_dir``: ``detections.csv`` (one row per event),
    ``detector_settings.csv`` (every parameter each detector ran with) and
    ``run.json`` (the roster, the frame intervals, the windowing policy and the
    windows actually scored).

    ``progress`` is called as ``progress(done, total, slice_id)`` before each
    recording, so a caller can say what it is doing rather than going quiet for
    two minutes.

    **A recording that fails is recorded, not fatal.** One malformed region in a
    folder of 85 must not cost the other 84; the reason lands in the run's
    roster where a reader can see which recordings produced nothing and why.
    """
    from bugarach.io import load_folder

    folder = Path(folder)
    out_dir = Path(out_dir)
    bad = [d for d in detectors if d not in DETECTORS]
    if bad:
        raise ValueError(
            f"unknown detector(s) {', '.join(bad)} — have "
            f"{', '.join(DETECTORS)}")

    run = DetectionRun(folder=folder, out_dir=out_dir,
                       detectors=tuple(detectors), stream_asked=stream)
    slices = load_folder(folder)
    if limit is not None:
        slices = slices[:limit]

    started = time.monotonic()
    all_events: list = []
    settings: dict[tuple[str, str], dict] = {}
    windows_by_slice: dict[str, list] = {}
    intervals: dict[str, float | None] = {}

    for i, s in enumerate(slices):
        if progress is not None:
            progress(i, len(slices), s.slice_id)
        rec = RecordingDetections(slice_id=s.slice_id, streams=tuple(s.streams))
        run.records.append(rec)
        if s.streams:
            rec.n_roi = s.streams[next(iter(s.streams))].n_rois

        dt = frame_interval_sec
        if dt is None:
            raw = s.meta.get("frame_interval_sec")
            try:
                dt = float(raw) if raw not in (None, "") else None
            except (TypeError, ValueError):
                dt = None
        rec.frame_interval_sec = dt
        intervals[s.slice_id] = dt

        t0 = time.monotonic()
        try:
            events, windows = detect_slice(
                s, detectors=detectors, stream=stream, frame_interval_sec=dt)
        except Exception as exc:                      # noqa: BLE001
            rec.skipped = f"{type(exc).__name__}: {exc}"
            rec.seconds = time.monotonic() - t0
            continue
        rec.seconds = time.monotonic() - t0
        rec.n_events = len(events)
        rec.n_outside = sum(1 for e in events if e.region_idx is None
                            and windows and windows[0].slot)
        rec.windows = [
            dict(region_idx=_region_index(w), label=w.label,
                 raw_start_sec=w.raw_start, raw_end_sec=w.raw_end,
                 scored_start_sec=w.win_start, scored_end_sec=w.win_end)
            for w in windows]
        windows_by_slice[s.slice_id] = rec.windows
        all_events.extend(events)

        for name in detectors:
            row = dict(detector_params(name, frame_interval_sec=dt),
                       onset_field=ONSET_FIELD[name])
            for sname in (n for n in s.streams if stream is None or n == stream):
                # A folder whose recordings carry different frame intervals runs
                # the grid-building detectors at different settings, and one row
                # cannot say two things. Flagged rather than silently overwritten.
                prev = settings.get((name, sname))
                if prev is not None and prev != row:
                    row = {k: (v if prev.get(k) == v else "varies by recording")
                           for k, v in row.items()}
                settings[(name, sname)] = row

    if progress is not None:
        progress(len(slices), len(slices), None)

    run.seconds = time.monotonic() - started
    run.n_events = len(all_events)

    out_dir.mkdir(parents=True, exist_ok=True)
    run.paths["detections"] = write_detections(all_events,
                                               out_dir / "detections.csv")
    run.paths["settings"] = write_detector_settings(
        settings, out_dir / "detector_settings.csv")
    run.paths["run"] = write_run(
        out_dir / "run.json",
        slices=[r.slice_id for r in run.records],
        frame_interval_sec=intervals,
        code_version=_code_version(),
        extra={
            "input_folder": str(folder),
            "detectors": list(detectors),
            "stream": stream,
            "rng_seed": RNG_SEED,
            "window_policy": (
                "the producer's analysis windows where the folder states them, "
                "and otherwise the raw period bounds verbatim — no wash-in "
                "delay, no cap, no baseline privilege, no label special-casing "
                "(Tony 2026-08-18; FOUNDATIONS §4)"),
            "windows": windows_by_slice,
            "not_detected": {r.slice_id: r.skipped for r in run.skipped},
            "elapsed_sec": round(run.seconds, 3),
        })
    return run


def _code_version() -> str | None:
    """The commit this ran at, when the tree is a git checkout."""
    import subprocess
    try:
        out = subprocess.run(["git", "rev-parse", "HEAD"],
                             cwd=Path(__file__).resolve().parent,
                             capture_output=True, text=True, timeout=5)
    except (OSError, subprocess.SubprocessError):      # pragma: no cover - env
        return None
    return out.stdout.strip() or None


def format_run(run: DetectionRun) -> str:
    """What the terminal says when it is over."""
    L = [f"export folder: {run.folder}",
         f"{len(run.records)} recording(s), {len(run.detected)} detected on, "
         f"{len(run.skipped)} not",
         f"detectors: {', '.join(run.detectors)} · stream "
         + (run.stream_asked or "every stream in each recording")
         + f" · seed {RNG_SEED}",
         ""]
    for rec in run.records:
        if rec.skipped:
            L.append(f"  {rec.slice_id}  — nothing detected: {rec.skipped}")
            continue
        outside = f"  ({rec.n_outside} outside every period)" if rec.n_outside else ""
        L.append(f"  {rec.slice_id}  {rec.n_roi} ROI  "
                 f"streams {'+'.join(rec.streams)}  "
                 f"{len(rec.windows)} window(s)  "
                 f"{rec.n_events} detection(s){outside}  {rec.seconds:.1f}s")
    L.append("")
    L.append(f"  {run.n_events} detection(s) in {run.seconds:.1f}s")
    n_out = sum(r.n_outside for r in run.records)
    if n_out:
        L.append(f"  {n_out} of them fell in no declared period and carry no "
                 f"region — regions.csv")
        L.append("  stops before the recording does. The three region-aware "
                 "ports scan the whole")
        L.append("  extent and tag; the other three are run per declared "
                 "window and cannot.")
    for key in ("detections", "settings", "run"):
        if key in run.paths:
            L.append(f"  wrote {run.paths[key]}")
    L.append("")
    L.append("  Windows: the producer's analysis windows where the folder states")
    L.append("  them, and otherwise the raw period bounds as sent — no wash-in")
    L.append("  delay, no cap, no label special-casing. run.json records the")
    L.append("  exact span scored for every region.")
    return "\n".join(L)
