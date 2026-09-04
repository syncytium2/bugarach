#!/usr/bin/env python3
"""One PDF per group: every slice a row, field-step artifacts in red.

    python tools/make_group_raster_summary.py
    python tools/make_group_raster_summary.py --folder <a flagged review copy>
    python tools/make_group_raster_summary.py --rows-per-page 8 --also docs/learned

**Display only. No detector is constructed and none is run.** There is nothing
here to score and no ground truth to score it against — what the marks show is
the producer's events, and the only judgement drawn is the producer's own
field-step verdict, carried in a sidecar they wrote.

WHY THE RED IS NOT A VIOLATION OF THE RASTER RULE. CLAUDE.md says nothing is
ever drawn ON the raster: detections, planted events, treatment windows and
anchors all belong in a lane above it, because a mark riding over data is an
annotation on that data. Red here is not an annotation over the marks — it *is*
the mark. Each event is drawn once, in one place, and its colour says which of
two populations the event belongs to. Nothing is overlaid, nothing is added, and
removing the colour would leave the same raster with less information rather than
a cleaner one. Tony asked for it in those terms on 2026-09-04: *"draw the
excluded raster marks in red, the rest in black."*

That said, the rule's own reasoning still binds the rest of the picture, and it
is why this tool draws **no** region boundaries, no treatment windows, no
analysis bounds and no end-of-recording cue. Identity, ROI count and duration
live in the y-axis label; the legend lives in the page header, outside every
plot. Nothing competes with the ink.

THE FOLDER THIS READS IS NOT THE ANALYSIS FOLDER, AND IT MUST NOT BE. The
producer ships the field-step artifacts *removed* — `..._STEPS_EXCLUDED` is the
dataset, and their standing rule as of 2026-09-03 is that exporters ship clean
data. The flagged twin exists as a named exception for exactly one purpose,
their words: *"seeing how the artifacts change the impression the data gives.
That is a review task, and review needs the thing being reviewed."* This tool is
that review task, so it reads the flagged copy and refuses anything else — a
folder with no `field_steps_flagged.tsv` has no red to draw, and a summary with
no red in it looks identical to a summary of a corpus that never had an artifact.
Failing loudly is the only way those two can be told apart.

THE FLAGS DO NOT COME THROUGH THE LOADER, DELIBERATELY. `io.py` recognises
`width_sec`, `width_def`, `peak_sec` and `amp` and nothing else, so
`on_field_step` and `field_step_id` are read by `csv.DictReader` and dropped;
`store.Stream` has no per-event flag field. The producer names both routes and
declines to assume either. A display tool is the wrong place to widen a data
structure every detector depends on, so this joins their sidecar TSV on
`(slice_id, stream, roi, time_sec)` — four fields the loader already keeps — and
`src/` is untouched.

Destination is the darkroom, resolved by `bugarach.paths`; `--also` writes a
second copy into the repo. The path is never hardcoded: it carries a person's
name and this repo is public.
"""

from __future__ import annotations

import argparse
import csv
import sys
import warnings
from collections import defaultdict
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from bugarach import paths  # noqa: E402
from bugarach.io import load_folder  # noqa: E402

#: The producer's sidecar. Its presence is what makes a folder reviewable: it is
#: written only by the flagged run, and `..._STEPS_EXCLUDED` ships
#: `field_steps_excluded.tsv` instead — same columns, opposite meaning (what was
#: taken out, not what is still there to look at).
MANIFEST = "field_steps_flagged.tsv"

#: Names the flagged review copy has been shipped under. The producer's README
#: calls it `..._STEPS_FLAGGED_FOR_REVIEW`; it arrived on this machine as
#: `_superseded_flagrun2`. Both are tried, and neither is a path — `dataset`
#: resolves a NAME against the data root on whatever machine this is (SAP004).
FLAGGED_NAMES = (
    "2026-09-03_revised_2v_long_STEPS_FLAGGED_FOR_REVIEW",
    "_superseded_flagrun2",
)

#: Constant, and the point of the figure. Tony, 2026-09-04: *"the height of each
#: row constant independent of the number of rois."* A row is a slice, not a
#: stack of ROIs, so the ROI axis is normalised into the band rather than setting
#: it. Two slices 20 ROIs apart get the same ink budget and the eye can compare
#: them; scaling by ROI count makes the biggest recording look like the busiest.
ROW_INCHES = 0.62

#: Fast above, slow below, inside the one row. Both streams carry the artifact —
#: the producer measured 8.5x (fast) and 22.7x (slow) each slice's own rate — so
#: a summary showing one stream would show half the problem.
STREAM_ORDER = ("fast", "slow")

BLACK = "#000000"
#: Not a signal colour picked for contrast: this is the repo's own detector red,
#: already the ink for "this is the thing you are looking for" elsewhere.
RED = "#a03623"


def _tick_step(span: float) -> float:
    """Ticks at 1/2/5/10/15/30 x 60^k seconds — the repo's time axis, in mpl.

    `ui.app._time_axis_hook` owns this for the browser through bokeh's
    `AdaptiveTicker(base=60, mantissas=[1, 2, 5, 10, 15, 30])`. Matplotlib has no
    equivalent ticker, so the mantissa ladder is walked by hand rather than
    letting mpl pick decimal ticks: a raster labelled 500s/1000s/1500s is exactly
    the axis the convention exists to prevent.
    """
    if span <= 0:
        return 1.0
    for k in range(-1, 4):
        for m in (1, 2, 5, 10, 15, 30):
            step = m * (60.0 ** k)
            if step >= 1 and span / step <= 8:
                return step
    return 30 * (60.0 ** 3)


def _fmt_time(s: float) -> str:
    """45s / 2m / 2m30s — never a raw second count past a minute."""
    sign = "-" if s < 0 else ""
    a = abs(s)
    if a < 60:
        return f"{sign}{a:g}s"
    m, r = divmod(a, 60.0)
    r = round(r)
    if r == 60:
        m, r = m + 1, 0
    return f"{sign}{int(m)}m{int(r):02d}s" if r else f"{sign}{int(m)}m"


def read_manifest(folder: Path) -> dict[tuple[str, str, str], set[float]]:
    """The producer's flagged events, keyed the way a Slice is keyed.

    `roi` in the manifest is the SOURCE-STORE ROI index and `Slice.roi_ids`
    carries the same strings, so the join needs no renumbering. Times are written
    at `%.6f` on both sides and parsed from the same text by the same float
    reader, so equality is exact rather than approximate — but they are rounded
    anyway, because relying on that silently is how a join starts missing rows
    the day someone changes a format string.
    """
    out: dict[tuple[str, str, str], set[float]] = defaultdict(set)
    with (folder / MANIFEST).open(newline="") as fh:
        for row in csv.DictReader(fh, delimiter="\t"):
            key = (row["slice_id"], row["stream"], str(row["roi"]).strip())
            out[key].add(round(float(row["time_sec"]), 6))
    return out


def resolve_folder(explicit: str | None) -> Path:
    """Find the flagged review copy, and refuse anything that is not one."""
    from bugarach import dataset

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
                "pass --folder <path> if the producer shipped it under another name."
            )
    if not folder.is_dir():
        raise SystemExit(f"not a folder: {folder}")
    if not (folder / MANIFEST).is_file():
        raise SystemExit(
            f"{folder.name} has no {MANIFEST}, so it is not the flagged review copy.\n"
            "This tool draws the field-step artifacts, which means it needs the folder\n"
            "where they are STILL PRESENT and marked. The analysis folder\n"
            "(..._STEPS_EXCLUDED) has had them removed — pointing this at it would\n"
            "render a summary with no red in it, which is indistinguishable from a\n"
            "corpus that never had an artifact. Refusing rather than drawing that."
        )
    return folder


def _row_segments(stream, flagged: set[float] | None, roi_ids, y0: float, y1: float):
    """Vertical ticks for one stream, split into the two inks.

    One segment per event, spanning that ROI's lane within the band. Returned as
    two lists so the red can be drawn last and never be hidden under a black
    neighbour a tenth of a second away — at these densities whichever is drawn
    second is the one you see, and the artifact is the thing being looked for.
    """
    n = max(stream.n_rois, 1)
    lane = (y1 - y0) / n
    by_roi = flagged or {}
    plain: list[list[tuple[float, float]]] = []
    marked: list[list[tuple[float, float]]] = []
    for i, times in enumerate(stream.locs):
        if not len(times):
            continue
        top = y1 - i * lane
        bot = top - lane
        rid = str(roi_ids[i]) if roi_ids is not None and i < len(roi_ids) else str(i + 1)
        hits = by_roi.get(rid, ())
        for t in np.asarray(times, dtype=float):
            seg = [(t, bot), (t, top)]
            (marked if round(float(t), 6) in hits else plain).append(seg)
    return plain, marked


def build_pages(folder: Path, *, rows_per_page: int):
    """Group the slices, and say what each row will be. Sorted, never arbitrary."""
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        slices = load_folder(folder)
    groups: dict[str, list] = defaultdict(list)
    for sl in slices:
        groups[sl.meta.get("group_id") or "UNGROUPED"].append(sl)
    for name in groups:
        groups[name].sort(key=lambda s: s.slice_id)
    pages = {}
    for name, members in sorted(groups.items()):
        pages[name] = [members[i:i + rows_per_page]
                       for i in range(0, len(members), rows_per_page)]
    return pages


def draw(folder: Path, out_dir: Path, *, rows_per_page: int, also: Path | None):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.backends.backend_pdf import PdfPages
    from matplotlib.collections import LineCollection

    manifest = read_manifest(folder)
    by_slice_stream: dict[tuple[str, str], dict[str, set[float]]] = defaultdict(dict)
    for (sid, stream, rid), times in manifest.items():
        by_slice_stream[(sid, stream)][rid] = times

    pages = build_pages(folder, rows_per_page=rows_per_page)
    out_dir.mkdir(parents=True, exist_ok=True)
    written, drawn_red = [], 0

    for group, chunks in pages.items():
        # One x range for the whole group: rows are meant to be read against each
        # other, and a per-row extent would silently rescale time between them.
        span = max((max((float(np.max(a)) for st in sl.streams.values()
                         for a in st.locs if len(a)), default=0.0)
                    for chunk in chunks for sl in chunk), default=1.0)
        span = max(span, 1.0)
        step = _tick_step(span)
        ticks = np.arange(0, span + step, step)

        path = out_dir / f"{folder.name}__{group}.pdf"
        n_slices = sum(len(c) for c in chunks)
        with PdfPages(path) as pdf:
            for page_i, chunk in enumerate(chunks, start=1):
                fig_h = 1.15 + ROW_INCHES * len(chunk)
                fig, axes = plt.subplots(
                    len(chunk), 1, figsize=(15.0, fig_h), squeeze=False,
                    gridspec_kw=dict(hspace=0.0, top=1 - 0.72 / fig_h,
                                     bottom=0.42 / fig_h, left=0.105, right=0.995))
                axes = [a[0] for a in axes]
                for ax, sl in zip(axes, chunk):
                    plain_all, marked_all = [], []
                    for si, sname in enumerate(STREAM_ORDER):
                        st = sl.streams.get(sname)
                        if st is None:
                            continue
                        # fast occupies the top half of the band, slow the bottom
                        y1, y0 = (1.0, 0.52) if si == 0 else (0.48, 0.0)
                        flagged = by_slice_stream.get((sl.slice_id, sname), {})
                        p, m = _row_segments(st, flagged, sl.roi_ids, y0, y1)
                        plain_all += p
                        marked_all += m
                    drawn_red += len(marked_all)
                    if plain_all:
                        ax.add_collection(LineCollection(
                            plain_all, colors=BLACK, linewidths=0.45,
                            antialiased=False, zorder=2))
                    if marked_all:
                        # WIDER, AND THE WIDTH IS NOT DECORATION. A step is one
                        # moment: every event it generates lands inside ±2 s, which
                        # over an hour-wide page is a third of a point — thinner than
                        # the line that would draw it, so the artifact renders as
                        # nothing at all and the row reads clean. The mark is still
                        # at its own time and still only on the ROIs that fired; what
                        # is widened is the stroke, so a real moment survives the
                        # page scale. Drawn last and above, because at these
                        # densities whichever ink lands second is the one you see.
                        ax.add_collection(LineCollection(
                            marked_all, colors=RED, linewidths=1.8,
                            antialiased=True, zorder=3))
                    # the hairline between the two streams, outside both bands
                    ax.axhline(0.50, color="#c8c8c8", lw=0.4, zorder=0)
                    ax.set_xlim(0, span)
                    ax.set_ylim(0, 1)
                    ax.set_yticks([])
                    for side in ("top", "right", "left"):
                        ax.spines[side].set_visible(False)
                    dur = max((float(np.max(a)) for st in sl.streams.values()
                               for a in st.locs if len(a)), default=0.0)
                    n_red = sum(len(times)
                                for (sid, _s), rois in by_slice_stream.items()
                                if sid == sl.slice_id
                                for times in rois.values())
                    lab = (f"{sl.slice_id}\n{sl.streams['fast'].n_rois} ROI · "
                           f"{_fmt_time(dur)}")
                    if n_red:
                        lab += f" · {n_red} red"
                    ax.set_ylabel(lab, rotation=0, ha="right", va="center",
                                  fontsize=7.2, labelpad=8,
                                  color="#111111", linespacing=1.35)
                    ax.tick_params(axis="x", length=2, labelsize=7)
                    if ax is axes[-1]:
                        ax.set_xticks(ticks)
                        ax.set_xticklabels([_fmt_time(t) for t in ticks])
                        ax.spines["bottom"].set_color("#888888")
                    else:
                        ax.set_xticks([])
                        ax.spines["bottom"].set_visible(False)

                head = (f"{group} — {n_slices} recording(s) · fast above the hairline, "
                        f"slow below · one row is one recording, and row height does "
                        f"not scale with ROI count")
                sub = ("black = event as the producer exported it     "
                       "red = event on a confirmed whole-field brightness step "
                       "(field-step artifact)     no detector was run")
                fig.text(0.105, 1 - 0.20 / fig_h, head, fontsize=9.6, va="top",
                         color="#111111")
                fig.text(0.105, 1 - 0.42 / fig_h, sub, fontsize=7.4, va="top",
                         color="#555555")
                fig.text(0.995, 1 - 0.20 / fig_h,
                         f"{folder.name}   ·   page {page_i}/{len(chunks)}",
                         fontsize=7.2, va="top", ha="right", color="#777777")
                pdf.savefig(fig)
                plt.close(fig)
        written.append(path)
        if also is not None:
            also.mkdir(parents=True, exist_ok=True)
            (also / path.name).write_bytes(path.read_bytes())

    return written, drawn_red, sum(len(v) for v in manifest.values())


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--folder", default=None,
                    help="path to the flagged review copy (default: resolve by name)")
    ap.add_argument("--out", default=None,
                    help="destination directory (default: the darkroom)")
    ap.add_argument("--also", default=None,
                    help="write a second copy here, e.g. a repo folder")
    ap.add_argument("--rows-per-page", type=int, default=12,
                    help="rows per page; row HEIGHT is constant either way")
    a = ap.parse_args(argv)

    folder = resolve_folder(a.folder)
    out_dir = Path(a.out).expanduser() if a.out else paths.darkroom() / "raster_summaries"
    also = Path(a.also).expanduser() if a.also else None

    written, drawn, expected = draw(folder, out_dir, rows_per_page=a.rows_per_page,
                                    also=also)
    print(f"read      {folder}")
    print(f"wrote     {len(written)} PDF(s) -> {out_dir}")
    for p in written:
        print(f"          {p.name}")
    if also:
        print(f"also      {also}")
    print(f"red marks {drawn} drawn / {expected} in {MANIFEST}")
    if drawn != expected:
        # Not cosmetic. A row that fails to join loses its red and the page then
        # says the recording is clean, which is the one thing this figure must
        # never say by accident.
        print("WARNING: the join dropped rows — the pages under-report the artifact.",
              file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
