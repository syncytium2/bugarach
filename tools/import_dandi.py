#!/usr/bin/env python3
"""Turn the Cossart lab's DANDI:000219 into an export folder bugarach can read.

    python tools/import_dandi.py --src <dir of extracted .mat sessions> [--out DIR]

**This is a producer, and it is the first one that is not this lab.** Everything
else bugarach reads was written by interface2's exporter from this lab's own
recordings. DANDI:000219 is another group's published source data — in vivo
two-photon calcium imaging of CA1 in mouse pups, P5–P12 — and running the ports
against it is how a question about a detector's performance stops being a
question about our preparation. See `docs/export_folder_spec.md` for the contract
this writes to.

Why this matters beyond one comparison
--------------------------------------
The contract says any producer can write a folder and that everything past `roi`
and `time_sec` is optional. **Nothing had ever tested that**, because every folder
bugarach has read came from one exporter that sends the full per-event set. This
corpus sends less than ours, and is closer to what a typical outside lab has
(FOUNDATIONS §1) — most labs have one stream, and no per-event width, peak or
amplitude.

What the source actually holds, and what it does not
----------------------------------------------------
The published data is **binarised**: an ``int8`` raster, frames × ROIs, of "this
cell is active in this frame", plus frame timestamps, found under
``processing/ophys`` in the NWB. It is **not** a fluorescence trace — some
inference step has already been applied and what arrives is a state, not a shape.

**Which step, this importer does not claim to know.** The Cossart lab publishes
CICADA and DeepCINAC and it is tempting to name one, so an earlier draft of this
docstring did. Nobody here has read their pipeline documentation. Attributing a
method to another group on a guess is a research-integrity problem, not a
citation nitpick, and this project has already had to correct one. If the answer
matters to a result, read their paper or ask them.

**Nothing this lab knows about its own event data transfers here either.** In
particular the `locs` / `t50rise` field-name history that governs our export —
where a legacy `findpeaks` name ended up holding an onset — is **ours**, and says
nothing about what is in theirs. So:

===============  ==================================================================
column           what this producer sends
===============  ==================================================================
``roi``          the source's own ``roi_ids``, as a string
``time_sec``     **the RISING EDGE of an active run — NOT a t50rise.**  See below.
``width_sec``    how long the run stayed active (falling edge − rising edge)
``width_def``    ``active_run_binary_raster`` — the producer's name for that rule
``stream``       **omitted.** One stream, and the contract says omit the column.
``peak_sec``     **omitted.** A binary raster has no peak.
``amp``          **omitted.** A binary raster has no amplitude.
===============  ==================================================================

**Times are on the session's real clock, and the movies are declared.** Each session
is five movies with 17–18 s gaps between them. ``time_sec`` is the rising frame's own
timestamp, runs are found inside each movie, and ``imaging.csv`` lists the movies as
imaged stretches (contract revision 11;
docs/adr/2026-11-14-7a3a-a-recording-imaged-in-stretches-says-so-in-imaging-csv-detec.md).
Until 2026-11-14 this wrote ``t0 + frame × dt`` and found runs across seams, which moved
every event after the first movie 17 to about 70 s early and joined events across gaps.

**The `time_sec` substitution is the one thing a reader must not miss.** The
contract defines `time_sec` as the `t50rise` — the moment a transient reached half
its rise — and says so because a producer sending peaks where onsets were meant
would change which events are found to coincide with nothing failing anywhere. A
binary raster has no half-rise to find: the signal is already a state, not a
shape. This sends the closest thing it has, which the contract explicitly permits
*provided the producer documents it* — hence `width_def`, this docstring, and the
`PROVENANCE.md` written beside the data.

**So cross-lab timing comparisons carry a caveat and it must travel with them.**
Our `time_sec` is a half-rise; this one is the first frame of an inferred active
state. Those are different landmarks and the offset between them is not measured
here. Rankings and rates are safe; a claim that two labs' events coincide to
within a tolerance is not.

**A silent ROI is a row with no time, and that is not optional.** An ROI with no
events emits ``roi,NA``. The contract is emphatic about why: one row per event
means a silent ROI otherwise has no rows at all, *absent* is indistinguishable
from *never imaged*, and every per-ROI rate then divides by the wrong denominator.
These recordings are large (117–1050 ROIs) and quiet ROIs are common, so the
error would be substantial and invisible.

**No viability judgement, in either direction.** This does not drop, flag or score
an ROI. The published corpus is the population its authors chose (FOUNDATIONS §9)
and a zero-event ROI is a measurement, not a dead cell.
"""

from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

import numpy as np

REPO = Path(__file__).resolve().parent.parent
if str(REPO / "src") not in sys.path:
    sys.path.insert(0, str(REPO / "src"))

#: The producer's name for what `width_sec` measures here. Constant within the
#: stream, and never parsed by bugarach — it is carried so a consumer comparing
#: widths across producers can see the definitions differ before comparing.
WIDTH_DEF = "active_run_binary_raster"

#: Where a foreign corpus goes. Deliberately NOT `exports/bugarach/`, which
#: `dataset.resolve()` searches for bare names — a foreign folder there is one
#: typo away from being read as this lab's data.
DEFAULT_OUT_SUBPATH = ("exports", "external", "dandi_000219")


#: A step between frame timestamps longer than this many frame intervals is a gap in
#: imaging, not jitter. DANDI:000219's gaps are 17–18 s against intervals of 0.09–0.12 s,
#: about 150 intervals; a dropped frame or two is not a new movie.
GAP_FACTOR = 10.0


def movies(t: np.ndarray, dt: float) -> list[tuple[int, int]]:
    """``[first, stop)`` frame ranges imaged without a break, read off the timestamps.

    Each DANDI:000219 session is five movies of 2,500 frames with 17–18 s between them,
    but that is what the timestamps say, not a constant this function assumes."""
    t = np.asarray(t, dtype=float)
    cut = np.flatnonzero(np.diff(t) > GAP_FACTOR * dt) + 1
    edges = np.concatenate([[0], cut, [t.size]])
    return [(int(a), int(b)) for a, b in zip(edges[:-1], edges[1:])]


def stretches(t: np.ndarray, dt: float) -> list[tuple[float, float]]:
    """Each movie as ``(start_sec, end_sec)`` on the real clock, for ``imaging.csv``: from
    its first frame's time to its last frame's time plus one interval."""
    t = np.asarray(t, dtype=float)
    return [(float(t[a]), float(t[b - 1] + dt)) for a, b in movies(t, dt)]


def runs(raster: np.ndarray, t: np.ndarray, dt: float):
    """Rising-edge times and run lengths, per ROI column, from a binary raster.

    Returns ``(onsets_sec, widths_sec)`` as lists indexed by column.

    **Times are the frames' own timestamps**, so an event in the third movie is placed
    after the two gaps before it. They used to be ``t0 + frame × dt``, which closed the
    gaps and put every event after the first movie 17 to about 70 s early.

    **Runs are found inside each movie.** A cell active in the last frame of one movie
    and the first of the next is two events: the frames are adjacent in the array and
    17 s apart in time, and one event spanning them would claim activity nobody imaged.
    A run still active at the end of a movie closes there, which is the honest reading:
    the imaging stopped, the cell did not.

    A width runs from the first active frame's time to the last active frame's time plus
    one interval ``dt``: a run of k frames is about k × ``dt``.
    """
    r = np.asarray(raster, dtype=np.int16)
    t = np.asarray(t, dtype=float)
    n_frames, n_roi = r.shape
    if t.size != n_frames:
        raise ValueError(f"{t.size} timestamps for {n_frames} frames")
    onsets = [[] for _ in range(n_roi)]
    widths = [[] for _ in range(n_roi)]
    for a, b in movies(t, dt):
        seg = r[a:b]
        pad = np.zeros((1, n_roi), dtype=np.int16)
        dif = np.diff(np.vstack([pad, seg, pad]), axis=0)
        for c in range(n_roi):
            rise = np.flatnonzero(dif[:, c] == 1)
            fall = np.flatnonzero(dif[:, c] == -1)
            # One falling edge per rising edge, by the padding; a run open at the
            # movie's last frame falls at its end.
            onsets[c].append(t[a + rise])
            # Last active frame's time plus one interval, minus the first: on the
            # same clock as the stretch's end, so a run closing with its movie ends
            # exactly where the movie does, whatever the frame jitter.
            widths[c].append(t[a + fall - 1] + dt - t[a + rise])
    return ([np.concatenate(v) if v else np.empty(0) for v in onsets],
            [np.concatenate(v) if v else np.empty(0) for v in widths])


def read_session(path: Path):
    """One extracted ``.mat`` session -> the fields this producer needs."""
    import scipy.io as sio

    d = sio.loadmat(path, squeeze_me=True)
    raster = np.atleast_2d(d["raster"])
    t = np.atleast_1d(np.asarray(d["t"], dtype=float))
    if raster.shape[0] != t.size and raster.shape[1] == t.size:
        raster = raster.T
    roi_ids = np.atleast_1d(d["roi_ids"]) if "roi_ids" in d \
        else np.arange(raster.shape[1])
    return dict(
        slice_id=str(d.get("session", path.stem)),
        raster=raster,
        dt=float(d["dt"]),
        t=t,
        roi_ids=[str(x) for x in roi_ids],
        age=str(d.get("age", "")),
        subject=str(d.get("subject", "")),
    )


#: The NWB series the published raster lives in, as `dandi-cache slice --preset
#: cossart-raster` flattens it into an .npz key ("/" becomes "__"). The series name
#: carries a version string ("raster dur v26_5_v37_6"), so it is matched by prefix.
NPZ_RASTER_PREFIX = "processing__ophys__fluorescence_all_cells__raster"


def read_npz_session(path: Path, *, slice_id: str, subject: str = "", age: str = ""):
    """One session sliced from the NWB by `dandi-cache slice` -> the fields this producer
    needs. The slice holds the raster, its frame timestamps and the ROI ids and nothing
    else, so identity comes from the caller (the manifest), not from the file.

    The frame interval is the median step between timestamps: the four or so gaps
    between movies are outliers among about 12,500 steps and do not move it."""
    z = np.load(path, allow_pickle=False)
    series = sorted({k.rsplit("__", 1)[0] for k in z.files
                     if k.startswith(NPZ_RASTER_PREFIX)})
    if len(series) != 1:
        raise ValueError(f"{path.name}: expected one raster series, found {series}")
    s = series[0]
    raster = np.atleast_2d(z[f"{s}__data"])
    t = np.atleast_1d(np.asarray(z[f"{s}__timestamps"], dtype=float))
    if raster.shape[0] != t.size and raster.shape[1] == t.size:
        raster = raster.T
    rois = z[f"{s}__rois"] if f"{s}__rois" in z.files else np.arange(raster.shape[1])
    return dict(slice_id=slice_id, raster=raster, dt=float(np.median(np.diff(t))), t=t,
                roi_ids=[str(x) for x in np.atleast_1d(rois)], age=age, subject=subject)


def read_manifest(path: Path) -> list[dict]:
    """An explicit list of sessions to import, one row each: ``npz``, ``slice_id``, and
    optionally ``subject_id``, ``age`` and ``analysis_hold``.

    Explicit on purpose. Scanning a directory imports whatever happens to be in it, and a
    session left out for a reason is then one stray file away from coming back in. A
    relative ``npz`` path is read against the manifest's own folder."""
    with path.open(newline="") as fh:
        rows = list(csv.DictReader(fh))
    if not rows or not {"npz", "slice_id"} <= set(rows[0]):
        raise ValueError(f"{path.name}: a manifest needs columns npz and slice_id")
    for r in rows:
        p = Path(r["npz"]).expanduser()
        r["npz"] = p if p.is_absolute() else path.parent / p
    return rows


def write_recording(out: Path, sess: dict) -> tuple[int, int, int]:
    """Write one ``<slice_id>.csv``. Returns (n_roi, n_events, n_silent_rois)."""
    onsets, widths = runs(sess["raster"], sess["t"], sess["dt"])
    n_events = n_silent = 0
    with (out / f"{sess['slice_id']}.csv").open("w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["roi", "time_sec", "width_sec", "width_def"])
        for roi, on, wid in zip(sess["roi_ids"], onsets, widths):
            if on.size == 0:
                # The contract's only way to say "recorded, fired nothing".
                w.writerow([roi, "NA", "", ""])
                n_silent += 1
                continue
            for t_sec, width in zip(on, wid):
                w.writerow([roi, f"{t_sec:.6f}", f"{width:.6f}", WIDTH_DEF])
                n_events += 1
    return len(sess["roi_ids"]), n_events, n_silent


def write_imaging(out: Path, sessions: list[dict]) -> None:
    """``imaging.csv``: each session's movies as imaged stretches on the real clock
    (contract revision 11). Without it, a consumer cannot know where the gaps are."""
    with (out / "imaging.csv").open("w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["slice_id", "stretch_idx", "start_sec", "end_sec"])
        for sess in sessions:
            for k, (a, b) in enumerate(stretches(sess["t"], sess["dt"]), start=1):
                w.writerow([sess["slice_id"], k, f"{a:.6f}", f"{b:.6f}"])


def write_sidecar(out: Path, rows: list[dict]) -> None:
    """``slices.csv`` — the per-recording sidecar the contract asks for."""
    with (out / "slices.csv").open("w", newline="") as fh:
        w = csv.writer(fh)
        holds = any(r.get("hold") for r in rows)
        w.writerow(["slice_id", "frame_interval_sec", "age", "subject_id",
                    "n_roi_recorded"] + (["analysis_hold"] if holds else []))
        for r in rows:
            w.writerow([r["slice_id"], f"{r['dt']:.6f}", r["age"],
                        r["subject"], r["n_roi"]]
                       + ([r.get("hold", "")] if holds else []))


def write_provenance(out: Path, rows: list[dict], src: Path, note: str = "") -> None:
    """What the CSVs cannot say about themselves."""
    n_ev = sum(r["n_events"] for r in rows)
    n_roi = sum(r["n_roi"] for r in rows)
    n_silent = sum(r["n_silent"] for r in rows)
    (out / "PROVENANCE.md").write_text(f"""\
# DANDI:000219 as a bugarach export folder

**Not this lab's data.** In vivo two-photon calcium imaging of CA1 in awake mouse
pups (P5–P12), published by the Cossart lab as DANDI:000219 under **CC-BY-4.0**.
Cite the authors, not this folder. Written by `tools/import_dandi.py` from the
extracted sessions at `{src.name}/`.

- recordings: **{len(rows)}**
- ROIs: **{n_roi}** across all recordings, of which **{n_silent}** produced no event
- events: **{n_ev}**
- movies: {", ".join(sorted({str(r["n_movies"]) for r in rows}))} per recording, listed in
  `imaging.csv`

## The clock, and the gaps

**Every time here is the frame's own timestamp from the source**, so the 17–18 s
gaps between movies are where they happened. `imaging.csv` lists each recording's
movies as imaged stretches (contract revision 11). **Runs are found inside each
movie**: a cell active across a seam is two events, never one that spans a gap.
Detection splices the movies back to back and maps its calls back to this clock
(`bugarach.imaging`). Before 2026-11-14 this folder used `t0 + frame × dt` and
merged runs across seams; a folder written then is wrong on both counts.

## What `time_sec` is here, and what it is not

**It is the first frame of an inferred active run — NOT a `t50rise`.** The source
is a binary raster, one bit per cell per frame: some inference step ran before
publication and **this importer does not claim to know which one.** There is no
half-rise in a state variable, so this producer sends the closest landmark it
has, which the contract permits provided it says so. This is that statement.

**What is in this corpus is the authors' business and is not documented here
beyond what the files show.** Nothing about this lab's own event data — its
`locs` / `t50rise` field-name history in particular — has been assumed to apply.

**Consequence for anyone comparing this folder to this lab's:** our `time_sec` is
a half-rise and this one is a state onset. They are different landmarks, and the
offset between them is **not measured**. Rates, counts and detector rankings are
safe. A claim that events in the two corpora coincide within a scoring tolerance
is **not available** from these files.

## What `width_sec` is

`width_def = {WIDTH_DEF}` — the falling edge minus the rising edge of the active
run, in seconds. It is **not** a fluorescence transient width and not comparable
to this lab's `halfprom_width_findpeaks_w` without saying so. Read `width_def`
before comparing anything.

## What is absent, and why

- **`peak_sec`** — a binary raster has no peak.
- **`amp`** — a binary raster has no amplitude. The source is already thresholded.
- **`stream`** — one stream. The contract says a single-stream producer omits the
  column, and most labs are single-stream (FOUNDATIONS §3).

## Zero-event ROIs are present as `NA` rows

{n_silent} of {n_roi} ROIs fired nothing and each is written as `roi,NA`. They are
**not** dropped. A silent ROI with no rows is indistinguishable from one never
imaged, and every per-ROI rate would then divide by the wrong denominator. No
viability judgement is made or implied: a zero-event ROI is a measurement.

## Where this folder lives, and why not with the others

Deliberately **outside** `exports/bugarach/`. `dataset.resolve()` searches that
directory for bare names, and a foreign corpus sitting there is one typo from
being read as this lab's data. It is not named in `current_export.toml`. Pass it
by path.
""" + (f"\n## Note from whoever ran this import\n\n{note}\n" if note else "")
        + ("\n## Recordings on hold\n\n`slices.csv` carries an `analysis_hold` column. A "
           "recording with text there is in the folder and must not be analysed until "
           "that text says otherwise.\n" if any(r.get("hold") for r in rows) else ""))


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(
        description="Build a bugarach export folder from extracted DANDI:000219 "
                    "sessions.")
    given = ap.add_mutually_exclusive_group(required=True)
    given.add_argument("--src", type=Path,
                       help="directory of extracted .mat sessions (every one is imported)")
    given.add_argument("--manifest", type=Path,
                       help="CSV listing exactly the sessions to import, as .npz files "
                            "from `dandi-cache slice --preset cossart-raster` (columns "
                            "npz, slice_id; optional subject_id, age, analysis_hold)")
    ap.add_argument("--out", type=Path, default=None,
                    help="destination folder (default: <data root>/"
                         + "/".join(DEFAULT_OUT_SUBPATH) + ")")
    ap.add_argument("--limit", type=int, default=0,
                    help="import only the first N sessions (a smoke run)")
    ap.add_argument("--note", default="",
                    help="a paragraph added to PROVENANCE.md, e.g. why sessions were "
                         "left out")
    args = ap.parse_args(argv)

    if args.src is not None:
        src = args.src.expanduser()
        if not src.is_dir():
            print(f"import_dandi: no such directory: {src}", file=sys.stderr)
            return 2
        files = sorted(src.glob("*.mat"))
        if not files:
            print(f"import_dandi: no .mat sessions in {src}", file=sys.stderr)
            return 2
        jobs = [(f, lambda f=f: read_session(f), "") for f in files]
    else:
        src = args.manifest.expanduser()
        listed = read_manifest(src)
        missing = [str(r["npz"]) for r in listed if not Path(r["npz"]).is_file()]
        if missing:
            print(f"import_dandi: {len(missing)} manifest file(s) not found, e.g. "
                  f"{missing[0]}", file=sys.stderr)
            return 2
        jobs = [(r["npz"], lambda r=r: read_npz_session(
                    Path(r["npz"]), slice_id=r["slice_id"],
                    subject=r.get("subject_id", ""), age=r.get("age", "")),
                 r.get("analysis_hold", "")) for r in listed]
    if args.limit:
        jobs = jobs[:args.limit]

    out = args.out
    if out is None:
        from bugarach import dataset
        root = dataset.data_root()
        if root is None:
            print("import_dandi: no data root found and no --out given. Set "
                  f"${dataset.ENV_VAR} or pass --out.", file=sys.stderr)
            return 2
        out = root.joinpath(*DEFAULT_OUT_SUBPATH)
    if out.is_dir() and any(out.glob("*.csv")):
        # A recording left over from an earlier import would load beside the new ones,
        # on the old clock, and nothing would say so.
        print(f"import_dandi: {out} already holds CSVs. Write to an empty folder and "
              f"replace the old one yourself.", file=sys.stderr)
        return 2
    out.mkdir(parents=True, exist_ok=True)

    rows = []
    for i, (where, load, hold) in enumerate(jobs, 1):
        sess = load()
        n_roi, n_events, n_silent = write_recording(out, sess)
        rows.append(dict(slice_id=sess["slice_id"], dt=sess["dt"], age=sess["age"],
                         subject=sess["subject"], n_roi=n_roi, n_events=n_events,
                         n_silent=n_silent, t=sess["t"], hold=hold,
                         n_movies=len(movies(sess["t"], sess["dt"]))))
        print(f"[{i}/{len(jobs)}] {sess['slice_id'][:46]:<46} "
              f"{n_roi:>5} ROI  {n_events:>7} events  {n_silent:>4} silent  "
              f"{rows[-1]['n_movies']} movies", flush=True)

    write_sidecar(out, rows)
    write_imaging(out, rows)
    write_provenance(out, rows, src, note=args.note)
    print(f"\n{len(rows)} recordings -> {out}")
    print(f"  {sum(r['n_events'] for r in rows)} events, "
          f"{sum(r['n_silent'] for r in rows)} zero-event ROIs kept as NA rows")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
