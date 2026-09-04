#!/usr/bin/env python3
"""Per group and per treatment: every recording a row, aligned at baseline end.

    python tools/make_group_raster_summary.py
    python tools/make_group_raster_summary.py --treatments TTX senktide high\\ K+
    python tools/make_group_raster_summary.py --folder <a flagged review copy>

One page per (group, treatment) — `MALE_TTX`, `ORX_senktide`, and so on. Each
page carries the recordings in that group that received that treatment, one
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

#: Constant, and asked for. Tony, 2026-09-04: *"the height of each row constant
#: independent of the number of rois."* `raster_panel` sizes itself from ROI
#: count when height is None; passing it explicitly is what makes a 9-ROI
#: recording and a 61-ROI one occupy the same band and stay comparable.
RASTER_PX = 116
LANE_PX = 26
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


def measure(folder: Path, treatments: tuple[str, ...]):
    """Which recordings go on which page, and what each page's extent must be."""
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        slices = load_folder(folder)
    manifest = read_manifest(folder)

    pages: dict[tuple[str, str], list] = defaultdict(list)
    skipped: list[str] = []
    for sl in slices:
        anchor = _anchor_of(sl)
        if anchor is None:
            skipped.append(f"{sl.slice_id} (no {ANCHOR} region to align on)")
            continue
        labels = {(r.name or "").strip() for r in sl.regions or []}
        hit = [t for t in treatments if t in labels]
        if not hit:
            skipped.append(f"{sl.slice_id} ({', '.join(sorted(labels)) or 'no regions'})")
        for t in hit:
            pages[(sl.meta.get("group_id") or "UNGROUPED", t)].append((sl, anchor))

    built = {}
    for key, members in pages.items():
        members.sort(key=lambda p: p[0].slice_id)
        lo = min(-a for _, a in members)
        hi = max(max((float(np.nanmax(v)) for st in sl.streams.values()
                      for v in st.t50rise if len(v) and np.isfinite(v).any()),
                     default=a) - a
                 for sl, a in members)
        # out to a whole minute, so the tick ladder lands on labelled values
        built[key] = dict(members=members,
                          ext=(float(np.floor(lo / 60.0) * 60.0),
                               float(np.ceil(hi / 60.0) * 60.0)))
    return built, manifest, skipped


def build_page(members, *, ext, manifest, width: int):
    """Lane over fast raster over slow raster, per recording, all x-linked."""
    from bugarach.ui.diagnostic import raster_panel, region_lane_panel

    blocks, red_drawn = [], 0
    for sl, anchor in members:
        # A UNIQUE y-DIMENSION PER PANEL. The name is what links y-ranges across
        # panels, so leaving the defaults draws every recording against the ROI
        # count of the largest one on the page — a 19-ROI raster fills the bottom
        # 40% of its band and reads as sparse rather than small, which is the one
        # comparison a constant row height exists to make honest.
        panels = [region_lane_panel(sl.regions, ext=ext, width=width,
                                    height=LANE_PX, shift=anchor,
                                    ydim=f"region_{sl.slice_id}")]
        for sname in ("fast", "slow"):
            st = sl.streams.get(sname)
            if st is None:
                continue
            marked, n_red = [], 0
            for i in range(st.n_rois):
                rid = (str(sl.roi_ids[i]) if sl.roi_ids is not None
                       and i < len(sl.roi_ids) else str(i + 1))
                hits = manifest.get((sl.slice_id, sname, rid), ())
                marked.append(np.asarray(hits, dtype=float) - anchor)
                n_red += len(hits)
            red_drawn += n_red
            panels.append(raster_panel(
                _shift_stream(st, anchor), ext=ext, width=width,
                height=RASTER_PX, name=sname, marked=marked,
                ydim=f"roi_{sl.slice_id}_{sname}"))
        blocks.append((sl, panels))

    # ONE X-AXIS PER LINKED GROUP, on the bottom row only (CLAUDE.md). Every
    # panel carrying its own drew the tick ladder and the `t` label eighteen
    # times down a page whose rows share one axis by construction, which is both
    # noise and a lie about how many axes there are. The last raster keeps its
    # own and gets the height back that the others give up.
    flat = [p for _, ps in blocks for p in ps]
    for p in flat[:-1]:
        p.opts(xaxis=None, toolbar=None)
    if flat:
        flat[-1].opts(height=RASTER_PX + 34, toolbar=None)
    return blocks, red_drawn


def header_html(group: str, treatment: str, members, ext, folder: Path) -> str:
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
    return (
        f"<div style='font:13px system-ui,sans-serif;color:#111;margin:0 0 6px'>"
        f"<b style='font-size:16px'>{group} · {treatment}</b> &nbsp;—&nbsp; "
        f"{len(members)} recording(s), each row one recording, "
        f"<b>t = 0 is the end of that recording's baseline</b>"
        f"<div style='margin:5px 0 0;color:#444'>"
        f"{chip(RASTER_INK, 'event')} &nbsp; "
        f"{red_key}"
        f"</div>"
        f"<div style='margin:4px 0 0;color:#444'>regions: {regions}</div>"
        f"<div style='margin:5px 0 0;color:#777;font-size:11px'>"
        f"{folder.name} &nbsp;·&nbsp; extent {ext[0] / 60:.0f}m to +{ext[1] / 60:.0f}m "
        f"&nbsp;·&nbsp; row height is constant and does not scale with ROI count "
        f"&nbsp;·&nbsp; no detector was run</div></div>")


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
    a = ap.parse_args(argv)

    folder = resolve_folder(a.folder)
    if a.out:
        dest = Path(a.out).expanduser()
    else:
        root = paths.darkroom(create=True)
        if root is None:
            print(paths.unresolved_message(), file=sys.stderr)
            return 2
        # Named for what is in it, not for the branch that made it.
        dest = root / "rasters_by_group_and_treatment_baseline_aligned"
    dest.mkdir(parents=True, exist_ok=True)

    import panel as pn

    pages, manifest, skipped = measure(folder, tuple(a.treatments))
    if not pages:
        print("no (group, treatment) page has any recording", file=sys.stderr)
        return 1

    written, total_red = [], 0
    for (group, treatment), spec in sorted(pages.items()):
        blocks, red = build_page(spec["members"], ext=spec["ext"],
                                 manifest=manifest, width=a.width)
        total_red += red
        html = dest / f"{group}_{treatment.replace(' ', '')}.html"

        items = [pn.pane.HTML(header_html(group, treatment, spec["members"],
                                          spec["ext"], folder))]
        for sl, panels in blocks:
            # A TEXT HEADER OUTSIDE THE PLOT, which is what the convention offers
            # beside the y-label — and here it is the one that works. Rotated
            # into a 116 px y-label the recording id was clipped to
            # "0240827a55", and a truncated identifier on a per-recording figure
            # is worse than none: it still looks like an answer.
            n_roi = next((s.n_rois for s in sl.streams.values()), 0)
            items.append(pn.pane.HTML(
                f"<div style='font:12px system-ui,sans-serif;color:#111;"
                f"margin:9px 0 0 78px'><b>{sl.slice_id}</b>"
                f"<span style='color:#666'> · {n_roi} ROI · "
                f"{sl.meta.get('group_id', '?')}</span></div>"))
            items += [pn.pane.HoloViews(p) for p in panels]

        with tempfile.TemporaryDirectory() as td:
            tmp = Path(td) / "p.html"
            # write-then-replace: the darkroom is inside Dropbox, and writing in
            # place is what produced its 188 MB of hash-named orphans.
            pn.Column(*items).save(str(tmp))
            os.replace(tmp, html)
        written.append(html)
        if not a.no_png:
            from make_diagnostic import _render_png
            shot = html.with_suffix(".png")
            if _render_png(html, shot):
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
              f"(no {'/'.join(a.treatments)} region):")
        for s in sorted(skipped):
            print(f"  {s}")
    print(f"\nred marks {total_red} drawn / {in_manifest} in {MANIFEST} "
          f"(a recording on two pages is drawn on both)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
