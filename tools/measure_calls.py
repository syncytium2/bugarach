#!/usr/bin/env python3
"""Width and amplitude of every call in a detections.csv, by one yardstick for all detectors.

    python tools/measure_calls.py --detections <run>/detections.csv
    python tools/measure_calls.py --detections <run>/detections.csv --dataset <name>

Reads the calls a ``bugarach detect`` run wrote and the export folder it ran on (the declared
default unless ``--dataset`` names another), and writes ``calls_measured.csv`` beside the
detections: every detections column unchanged, then the measured ones from
:mod:`bugarach.call_measure` — ``core_span_sec`` (the **width**: earliest to last onset in the
coordinated event), ``amplitude`` (cells taking part divided by the mean interval between their
onsets, cells per second), and the rest. The lengths the measurement used are columns too, so a
row can be re-derived without this tool's defaults.

**Region comes from the detections, unchanged.** ``region_idx`` and ``region_label`` are the
producer's, carried through; picking baseline and the first treatment is the consumer's call
(``docs/export_folder_spec.md``, "No privileged region").

Tony, 2026-09-21.
"""
from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

OUT_NAME = "calls_measured.csv"


def measure_rows(rows: list[dict], slices: dict, *, lengths: dict | None = None) -> list[dict]:
    """One output row per detection row, the detection's columns first.

    ``slices`` maps slice_id to a loaded :class:`bugarach.store.Slice`. ``lengths`` maps a
    stream name to (gap_sec, half_aperture_sec), overriding :data:`call_measure.DEFAULTS`.
    A row whose slice or stream is not in the folder is refused, not skipped: a measurement
    silently missing from some rows is the failure a per-row table cannot show.
    """
    from bugarach import call_measure as cm

    out = []
    for row in rows:
        sid, stream_name = str(row["slice_id"]), str(row["stream"])
        sl = slices.get(sid)
        if sl is None or stream_name not in sl.streams:
            raise SystemExit(f"detections name {sid!r} / {stream_name!r}, which the export "
                             f"folder does not carry — wrong --dataset?")
        if not sl.dt or sl.dt <= 0:
            raise SystemExit(f"{sid}: no frame interval, which the amplitude's floor needs")
        gap, half = (lengths or {}).get(stream_name.lower(), cm.defaults_for(stream_name))
        center = cm.call_center(row["onset_sec"], row.get("width_sec"))
        w = row.get("width_sec")
        window = (row["onset_sec"], row["onset_sec"] + w) if w is not None else None
        m = cm.measure_call(sl.streams[stream_name], center, gap_sec=gap,
                            half_aperture_sec=half, min_interval_sec=float(sl.dt),
                            window=window)
        out.append({**row, "center_sec": center, **m.row()})
    return out


def write(rows: list[dict], path: Path) -> Path:
    if not rows:
        raise SystemExit("no detections to measure")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]))
        w.writeheader()
        for r in rows:
            w.writerow({k: ("NA" if v is None or (isinstance(v, float) and v != v) else v)
                        for k, v in r.items()})
    return path


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--detections", type=Path, required=True)
    ap.add_argument("--dataset", default=None,
                    help="export folder the detections were run on (default: the declared default)")
    ap.add_argument("--out", type=Path, default=None,
                    help=f"output file (default: {OUT_NAME} beside the detections)")
    a = ap.parse_args(argv)

    from bugarach import dataset
    from bugarach.emit import read_detections
    from bugarach.io import load_folder

    folder = (dataset.require(a.dataset, want="export_folder") if a.dataset
              else dataset.default())
    slices = {s.slice_id: s for s in load_folder(folder)}
    rows = read_detections(a.detections)
    out = write(measure_rows(rows, slices), a.out or a.detections.with_name(OUT_NAME))
    print(f"measured {len(rows)} calls on {Path(folder).name} -> {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
