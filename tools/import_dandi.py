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
cell is active in this frame", plus frame timestamps. That is the output of the
authors' own inference (CICADA / DeepCINAC), not a fluorescence trace. So:

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


def runs(raster: np.ndarray, dt: float, t0: float):
    """Rising-edge times and run lengths, per ROI column, from a binary raster.

    Returns ``(onsets_sec, widths_sec)`` as lists indexed by column. A run that is
    still active in the final frame is closed at the end of the recording, which
    is the honest reading: the recording stopped, the cell did not.
    """
    r = np.asarray(raster, dtype=np.int16)
    n_frames, n_roi = r.shape
    pad = np.zeros((1, n_roi), dtype=np.int16)
    dif = np.diff(np.vstack([pad, r, pad]), axis=0)

    onsets, widths = [], []
    for c in range(n_roi):
        rise = np.flatnonzero(dif[:, c] == 1)
        fall = np.flatnonzero(dif[:, c] == -1)
        # The padding guarantees one falling edge per rising edge; a run open at
        # the last frame falls at n_frames, i.e. the end of the recording.
        onsets.append(t0 + rise * dt)
        widths.append((fall - rise) * dt)
    return onsets, widths


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
        t0=float(t[0]),
        roi_ids=[str(x) for x in roi_ids],
        age=str(d.get("age", "")),
        subject=str(d.get("subject", "")),
    )


def write_recording(out: Path, sess: dict) -> tuple[int, int, int]:
    """Write one ``<slice_id>.csv``. Returns (n_roi, n_events, n_silent_rois)."""
    onsets, widths = runs(sess["raster"], sess["dt"], sess["t0"])
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
                w.writerow([roi, f"{t_sec:.4f}", f"{width:.4f}", WIDTH_DEF])
                n_events += 1
    return len(sess["roi_ids"]), n_events, n_silent


def write_sidecar(out: Path, rows: list[dict]) -> None:
    """``slices.csv`` — the per-recording sidecar the contract asks for."""
    with (out / "slices.csv").open("w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["slice_id", "frame_interval_sec", "age", "subject_id",
                    "n_roi_recorded"])
        for r in rows:
            w.writerow([r["slice_id"], f"{r['dt']:.6f}", r["age"],
                        r["subject"], r["n_roi"]])


def write_provenance(out: Path, rows: list[dict], src: Path) -> None:
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

## What `time_sec` is here, and what it is not

**It is the first frame of an inferred active run — NOT a `t50rise`.** The source
is a binary raster: the authors' own activity inference, one bit per cell per
frame. There is no half-rise in a state variable, so this producer sends the
closest landmark it has, which the contract permits provided it says so. This is
that statement.

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
""")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(
        description="Build a bugarach export folder from extracted DANDI:000219 "
                    "sessions.")
    ap.add_argument("--src", required=True, type=Path,
                    help="directory of extracted .mat sessions")
    ap.add_argument("--out", type=Path, default=None,
                    help="destination folder (default: <data root>/"
                         + "/".join(DEFAULT_OUT_SUBPATH) + ")")
    ap.add_argument("--limit", type=int, default=0,
                    help="import only the first N sessions (a smoke run)")
    args = ap.parse_args(argv)

    src = args.src.expanduser()
    if not src.is_dir():
        print(f"import_dandi: no such directory: {src}", file=sys.stderr)
        return 2

    out = args.out
    if out is None:
        from bugarach import dataset
        root = dataset.data_root()
        if root is None:
            print("import_dandi: no data root found and no --out given. Set "
                  f"${dataset.ENV_VAR} or pass --out.", file=sys.stderr)
            return 2
        out = root.joinpath(*DEFAULT_OUT_SUBPATH)
    out.mkdir(parents=True, exist_ok=True)

    files = sorted(src.glob("*.mat"))
    if args.limit:
        files = files[:args.limit]
    if not files:
        print(f"import_dandi: no .mat sessions in {src}", file=sys.stderr)
        return 2

    rows = []
    for i, f in enumerate(files, 1):
        sess = read_session(f)
        n_roi, n_events, n_silent = write_recording(out, sess)
        rows.append(dict(slice_id=sess["slice_id"], dt=sess["dt"], age=sess["age"],
                         subject=sess["subject"], n_roi=n_roi, n_events=n_events,
                         n_silent=n_silent))
        print(f"[{i}/{len(files)}] {sess['slice_id'][:46]:<46} "
              f"{n_roi:>5} ROI  {n_events:>7} events  {n_silent:>4} silent",
              flush=True)

    write_sidecar(out, rows)
    write_provenance(out, rows, src)
    print(f"\n{len(rows)} recordings -> {out}")
    print(f"  {sum(r['n_events'] for r in rows)} events, "
          f"{sum(r['n_silent'] for r in rows)} zero-event ROIs kept as NA rows")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
