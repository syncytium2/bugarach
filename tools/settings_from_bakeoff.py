#!/usr/bin/env python3
"""A bake-off's calibration, as a settings file `bugarach detect` will run at.

    python tools/settings_from_bakeoff.py --bakeoff RUN/03_bakeoff/bakeoff.json \
        --out RUN/settings/detector_settings.csv [--streams fast slow]

WHY THIS EXISTS. `fair_bakeoff.py` sweeps one declared knob per detector on the
training folds and records what each fold chose. Until now that number could only
be READ — it lived in `bakeoff.json` as a result, and `bugarach detect` had no way
to be told about it. So a knob fitted on simulated data derived from a folder never
reached that folder, and the instrument the bench scored was not the instrument
that ran. On the APV+CNQX+GZ pilot, five of the six shipped values sat outside
everything the folds chose.

This is the other half of `bugarach detect --settings`: that flag can read a
calibration, and this writes one.

WHAT IT WILL NOT DO, and each refusal is the point rather than an inconvenience:

* **It will not average folds.** Four folds that chose 99.5, 99.5, 99.9 and 99.5
  did not choose 99.6, and a mean over a knob grid is not a knob anyone ran.
  Disagreeing folds are refused by name unless `--pick` says how to resolve them.
* **It will not emit a value that sat on the end of its grid.** That is a search
  that stopped too early rather than an answer, and this project refuses such a
  point everywhere else (`bench.pick_operating_point` raises on it). `--allow-edge`
  overrides, and stamps the file so a reader of the file knows.
* **It will not write a detector the bake-off did not sweep.** A settings file
  that silently carries shipped values for the detectors nobody calibrated would
  read as a calibration of all six.

WHAT IT STAMPS. Every detector gets `fitted_on`, `fitted_knob`, `fitted_n_folds`,
`fitted_f1` and the grid endpoints, in the `fitted_*` convention the browser
already writes and `detect_folder.load_settings` already carries into `run.json`.
That is what makes the cross-dataset test possible later: a settings file that does
not say what fitted it cannot be checked against the folder it is applied to.
"""
from __future__ import annotations

import argparse
import csv
import json
import statistics
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from bugarach import paths  # noqa: E402
from bugarach.bench import OPERATING_POINTS  # noqa: E402
from bugarach.detect_folder import DETECTORS  # noqa: E402


def _fmt(v) -> str:
    """Match `emit`'s spelling so a file from here and a file from a run diff."""
    if isinstance(v, bool):
        return "true" if v else "false"
    if isinstance(v, float):
        return repr(v) if v != int(v) else str(int(v))
    return str(v)


def resolve(bake: dict, *, pick: str, allow_edge: bool):
    """Per detector: the knob value the folds support, or a refusal saying why."""
    out, refused = {}, []
    hand = bake.get("hand_written", {})
    for name in DETECTORS:
        row = hand.get(name)
        if row is None:
            continue
        op = OPERATING_POINTS[name]
        folds = [f.get("knob_value") for f in row["per_fold"]]
        folds = [v for v in folds if v is not None]
        if not folds:
            refused.append(f"{name}: the bake-off recorded no knob value")
            continue
        counts = Counter(folds)
        if len(counts) > 1:
            if pick == "refuse":
                refused.append(
                    f"{name}: folds chose {sorted(counts)} — they disagree, and a "
                    f"mean over a knob grid is not a knob anyone ran. Pass "
                    f"--pick mode or --pick median to resolve, and the file will "
                    f"say which was used")
                continue
            value = (counts.most_common(1)[0][0] if pick == "mode"
                     else statistics.median_low(sorted(folds)))
        else:
            value = folds[0]
        grid = list(op.grid)
        on_edge = bool(grid) and value in (grid[0], grid[-1])
        if on_edge and not allow_edge:
            refused.append(
                f"{name}: the folds chose {value:g}, an END of the searched grid "
                f"{grid[0]:g}..{grid[-1]:g}. This project reads that as a search "
                f"that stopped too early rather than an answer. Widen the grid and "
                f"re-run the bake-off, or pass --allow-edge and the file will say "
                f"so")
            continue
        out[name] = dict(
            knob=op.knob, value=value, folds=folds,
            f1=row["f1"]["mean"], grid=grid, on_edge=on_edge,
            n_recordings=int(bake.get("folds", 0)) * int(bake.get("seeds_per_fold", 0)),
            agreed=len(counts) == 1, pick=None if len(counts) == 1 else pick)
    return out, refused


def rows_for(resolved: dict, *, streams, fitted_on: str):
    """The four-column shape both writers use, parameters alphabetical."""
    rows = []
    for name in DETECTORS:
        got = resolved.get(name)
        if got is None:
            continue
        params = dict(OPERATING_POINTS[name].params)
        params[got["knob"]] = got["value"]
        for stream in streams:
            for key in sorted(params):
                rows.append(dict(detector=name, stream=stream, parameter=key,
                                 value=_fmt(params[key])))
            prov = {
                "fitted_on": fitted_on,
                "fitted_by": "sweep",
                "fitted_knob": got["knob"],
                "fitted_f1": _fmt(round(got["f1"], 4)),
                "fitted_n_folds": len(got["folds"]),
                "fitted_n_recordings": got["n_recordings"],
                "fitted_held_out": "yes",
                "fitted_folds_agreed": "yes" if got["agreed"] else "no",
                "fitted_grid_from": _fmt(got["grid"][0]) if got["grid"] else "",
                "fitted_grid_to": _fmt(got["grid"][-1]) if got["grid"] else "",
                "fitted_grid_steps": len(got["grid"]),
                "fitted_grid_default": "yes",
            }
            if got["pick"]:
                prov["fitted_folds_resolved_by"] = got["pick"]
            if got["on_edge"]:
                prov["fitted_grid_edge"] = (
                    "yes — the search was still climbing when the grid ran out, "
                    "so this is a bound rather than an operating point")
            for key in sorted(prov):
                rows.append(dict(detector=name, stream=stream, parameter=key,
                                 value=str(prov[key])))
    return rows


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--bakeoff", required=True, type=Path)
    ap.add_argument("--streams", nargs="+", default=["fast", "slow"],
                    help="stream names to write a block for (default: fast slow). "
                         "Use one name when the calibration is stream-specific")
    ap.add_argument("--pick", choices=("refuse", "mode", "median"), default="refuse",
                    help="what to do when folds disagree (default: refuse)")
    ap.add_argument("--allow-edge", action="store_true",
                    help="emit a value that sat on an end of its grid, stamping "
                         "the file to say so")
    ap.add_argument("--out", type=Path, default=None,
                    help="destination file (default: the darkroom)")
    ap.add_argument("--also", type=Path, default=None, help="a second copy")
    a = ap.parse_args(argv)

    bake = json.loads(a.bakeoff.read_text())
    resolved, refused = resolve(bake, pick=a.pick, allow_edge=a.allow_edge)

    for line in refused:
        print(f"  refused  {line}", file=sys.stderr)
    if not resolved:
        print("nothing to write — every detector was refused above", file=sys.stderr)
        return 2

    fitted_on = str(bake.get("provenance", {}).get("store")
                    or bake.get("spec", {}).get("store")
                    or a.bakeoff.parent.parent.name)
    rows = rows_for(resolved, streams=a.streams, fitted_on=fitted_on)

    out = a.out
    if out is None:
        root = paths.darkroom(create=True)
        if root is None:
            print(paths.unresolved_message(), file=sys.stderr)
            return 2
        out = root / "settings" / "detector_settings.csv"
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=("detector", "stream", "parameter",
                                           "value"), lineterminator="\n")
        w.writeheader()
        w.writerows(rows)
    print(f"wrote {out}")
    for name, got in resolved.items():
        shipped = OPERATING_POINTS[name].params.get(got["knob"])
        moved = "" if shipped == got["value"] else f"   (shipped {shipped:g})"
        print(f"  {name:8} {got['knob']:20} {got['value']:g}{moved}")
    if refused:
        print(f"  {len(refused)} detector(s) refused — they are NOT in the file, "
              f"so nothing runs them at a value nobody chose", file=sys.stderr)
    if a.also:
        a.also.parent.mkdir(parents=True, exist_ok=True)
        a.also.write_bytes(out.read_bytes())
        print(f"also {a.also}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
