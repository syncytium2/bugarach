"""Recordings imaged in stretches: splice them for detection, map calls back.

Some recordings were not imaged continuously. The Cossart lab's DANDI:000219 sessions
are five movies of 2,500 frames with 17–18 s between them, and the producer says so in
``imaging.csv`` (``docs/export_folder_spec.md``, revision 11). Event times stay on the
recording's real clock; this module is the one place that moves them anywhere else.

Why detection does not run on the real clock
--------------------------------------------
Every null in this package builds its grid over the recording's extent and knows
nothing about gaps. Fed real times, it counts each gap as recording time in which the
data hold no events but its circular shifts place some. That dilutes the null and
lowers the threshold. So detection runs on a **spliced** clock, the stretches placed
back to back, and every call is mapped back with :meth:`Spliced.to_real` before it is
reported, drawn or compared with anything on an external clock.

The pad, and why it has no default
----------------------------------
A seam on the spliced clock is a place where two frames 17 s apart sit next to each
other. A detector that looks at one frame at a time (locust, as CICADA does) never
pairs across it, and CICADA itself runs on the spliced raster, so ``pad_sec=0``
reproduces their convention. A detector that counts coincidence in a window (CoactDetect,
LoCo, the counts, binned SCE) **does** pair across it: a 2 s window at a seam joins the
last second of one movie to the first second of the next. ``pad_sec`` inserts that much
empty time at each seam, and it must be at least the detector's window to stop the
pairing. Empty time dilutes the null a little (four seams of 3 s in a 20-minute
recording is 1%), which is the price of not inventing coincidence. The caller states the
pad, because the right one depends on the detector and a default would be a guess
(docs/adr/2026-11-14-7a3a-a-recording-imaged-in-stretches-says-so-in-imaging-csv-detec.md).
"""

from __future__ import annotations

from dataclasses import dataclass, replace

import numpy as np

from bugarach.store import Slice

#: Slack for float comparison on the recording's clock, in seconds. Far below any
#: frame interval; it only absorbs the rounding of a timestamp written to 4 decimals.
TOL_SEC = 1e-3


class EventOutsideImagingError(ValueError):
    """An event sits where the producer says nothing was imaged, or runs across a gap."""


def stretches(s: Slice) -> list[tuple[float, float]] | None:
    """The recording's imaged stretches, or ``None`` when it is one continuous stretch."""
    return None if not s.imaging or len(s.imaging) < 2 else list(s.imaging)


def validate(s: Slice) -> None:
    """Refuse a recording whose events contradict its own ``imaging.csv``.

    Stretches must be chronological and must not overlap. Every event must start
    inside a stretch, and an event with a width must end inside the same one: a run that
    crosses a gap is one event reported as spanning time nobody imaged, which is the
    exact defect ``imaging.csv`` exists to prevent.
    """
    if not s.imaging:
        return
    st = np.asarray(s.imaging, dtype=float)
    if (st[:, 1] <= st[:, 0]).any():
        raise ValueError(f"{s.slice_id}: an imaged stretch ends before it starts: {s.imaging}")
    if len(st) > 1 and (st[1:, 0] < st[:-1, 1] - TOL_SEC).any():
        raise ValueError(f"{s.slice_id}: imaged stretches overlap or are out of order: "
                         f"{s.imaging}")
    for name, stream in s.streams.items():
        widths = stream.width if stream.has_width else None
        for i, times in enumerate(stream.locs):
            t = np.asarray(times, dtype=float)
            if t.size == 0:
                continue
            k = np.searchsorted(st[:, 0], t + TOL_SEC, side="right") - 1
            inside = (k >= 0) & (t < st[np.clip(k, 0, None), 1] + TOL_SEC)
            if not inside.all():
                bad = t[~inside][0]
                raise EventOutsideImagingError(
                    f"{s.slice_id}, stream '{name}', ROI {i}: an event at {bad:.4f} s "
                    f"falls outside every imaged stretch in imaging.csv. Either the "
                    f"event or the stretch is wrong, and that is the producer's to "
                    f"settle (docs/export_folder_spec.md, imaging.csv).")
            if widths is not None:
                w = np.asarray(widths[i], dtype=float)
                end = t + np.where(np.isfinite(w), w, 0.0)
                over = end > st[k, 1] + TOL_SEC
                if over.any():
                    bad = t[over][0]
                    raise EventOutsideImagingError(
                        f"{s.slice_id}, stream '{name}', ROI {i}: the event at "
                        f"{bad:.4f} s runs past the end of its imaged stretch "
                        f"({st[k[over][0], 1]:.4f} s). An event cannot span a gap "
                        f"in imaging; split it at the seam.")


@dataclass(frozen=True)
class Spliced:
    """A recording on its spliced clock, with the map back to its real one."""

    slice: Slice
    real_starts: np.ndarray        # each stretch's start on the real clock
    spliced_starts: np.ndarray     # the same start on the spliced clock
    durations: np.ndarray          # each stretch's length
    pad_sec: float

    @property
    def seams(self) -> np.ndarray:
        """Where each stretch after the first begins on the spliced clock."""
        return self.spliced_starts[1:]

    def to_real(self, t) -> np.ndarray:
        """Spliced time -> real time. A time inside a pad maps to the end of the
        stretch before it: nothing was imaged there, so nothing is placed in the gap."""
        t = np.asarray(t, dtype=float)
        k = np.clip(np.searchsorted(self.spliced_starts, t, side="right") - 1, 0, None)
        off = np.minimum(t - self.spliced_starts[k], self.durations[k])
        return np.where(t < self.spliced_starts[0], t, self.real_starts[k] + off)

    def to_spliced(self, t, *, side: str = "start") -> np.ndarray:
        """Real time -> spliced time. A time inside a gap goes to the start of the next
        stretch (``side="start"``) or the end of the previous one (``side="end"``)."""
        t = np.asarray(t, dtype=float)
        ends = self.real_starts + self.durations
        k = np.clip(np.searchsorted(self.real_starts, t, side="right") - 1, 0, None)
        out = self.spliced_starts[k] + (t - self.real_starts[k])
        in_gap = (t >= ends[k]) & (k + 1 < self.real_starts.size)
        if side == "start":
            nxt = np.clip(k + 1, 0, self.real_starts.size - 1)
            out = np.where(in_gap, self.spliced_starts[nxt], out)
        else:
            out = np.where(in_gap, self.spliced_starts[k] + self.durations[k], out)
        return np.where(t < self.real_starts[0], t, out)


def splice(s: Slice, *, pad_sec: float) -> Spliced:
    """Put a recording's imaged stretches back to back, ``pad_sec`` apart.

    Returns the recording on the spliced clock (event times, peaks and regions moved;
    widths and amplitudes unchanged) and the map back. A recording with one stretch, or
    with no ``imaging.csv``, comes back as it is, with an identity map.
    """
    if pad_sec < 0:
        raise ValueError("pad_sec is empty time inserted at each seam; it cannot be negative")
    validate(s)
    st = stretches(s)
    if st is None:
        t0 = s.imaging[0][0] if s.imaging else 0.0
        dur = (s.imaging[0][1] - t0) if s.imaging else np.inf
        return Spliced(s, np.array([t0]), np.array([t0]), np.array([dur]), float(pad_sec))
    st = np.asarray(st, dtype=float)
    real0, dur = st[:, 0], st[:, 1] - st[:, 0]
    spl0 = real0[0] + np.concatenate([[0.0], np.cumsum(dur[:-1] + pad_sec)])
    m = Spliced(s, real0, spl0, dur, float(pad_sec))

    def move(arrs):
        return None if arrs is None else [m.to_spliced(a) for a in arrs]

    # Every time field moves by the same offset; widths and amplitudes are not times and
    # are carried as the producer sent them.
    streams = {name: replace(st_,
                             locs=move(st_.locs),
                             t50rise=move(st_.t50rise),
                             peak=move(st_.peak))
               for name, st_ in s.streams.items()}
    regions = [replace(r,
                       start_sec=float(m.to_spliced(r.start_sec, side="start")),
                       end_sec=float(m.to_spliced(r.end_sec, side="end")),
                       analysis_start_sec=None if r.analysis_start_sec is None else
                       float(m.to_spliced(r.analysis_start_sec, side="start")),
                       analysis_end_sec=None if r.analysis_end_sec is None else
                       float(m.to_spliced(r.analysis_end_sec, side="end")))
               for r in s.regions]
    out = replace(s, streams=streams, regions=regions, imaging=None)
    return replace(m, slice=out)


def pieces(start: float, end: float, imaging) -> list[tuple[float, float]]:
    """A span on the real clock, cut where it crosses a gap: the parts that were imaged.

    For drawing a call. A span mapped from the spliced clock can start in one stretch and
    end in the next, and drawn whole it covers time in which nothing was recorded."""
    if not imaging:
        return [(start, end)]
    out = [(max(start, a), min(end, b)) for a, b in imaging]
    return [(a, b) for a, b in out if b > a]
