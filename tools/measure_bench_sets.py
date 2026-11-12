#!/usr/bin/env python3
"""Measure one bench per stream and per set of recordings, and write each as a record.

    python tools/measure_bench_sets.py --stage1 docs/learned/runs/<stage 1 run> --jobs 10

A **set** is the recordings a bench is built from: every recording of the default folder
(``all``) or one group's (``di``, ``male``, ...). For each stream the export carries and each
set, this writes ``docs/learned/bench_sets/<stream>_<set>.json``, which
:mod:`bugarach.bench_sets` turns into a bench the search and scoring tools take by name
(``fast_di``).

**Why.** Tony, 2026-11-12: one synthetic set containing both groups, and one per group, each
tuned on its own and scored on the others. The three bench modules hold one hand-transcribed
set of constants per stream, so a second set had nowhere to live. This is item 4 of the
stream-readiness route's *Owed* list: stage 1 ends in a file.

**Nothing is measured a new way.** Every value comes from the function the route already
uses, run on the set's recordings:

* rate and burst shapes, quiet and busy background, cells, participation:
  ``tools/remeasure_bench.py`` (``_values``), on ``tools/measure_slow_bench.py``'s per-recording
  measurement, with the coordinated share from the stage 1 rates record;
* jitter: the stage 1 correlogram record, its own per-group entry for a group;
* event widths: ``measure_slow_bench.width_quantiles``;
* the elevated-rate level: ``tools/measure_coordination_rates.py`` (``summarize``), the 99th
  percentile of 300 s baseline stretches, background;
* gaps between events and events per hour: the stage 1 ``measure_real_intervals`` run.

The split by group describes the data for building synthetic recordings. It tests nothing
between the groups (ADR-0017).

Baseline analysis windows only. Reads the default folder and refuses stage 1 records measured
on another one.
"""
from __future__ import annotations

import argparse
import csv
import datetime as _dt
import json
import sys
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))
sys.path.insert(0, str(REPO / "tools"))

STREAMS = ("fast", "slow", "combined")
ALL = "all"
MIN_RECORDINGS = 4
"""Fewer recordings than this and the quartiles that set the two backgrounds are read off
three points or fewer; the set is written with a caveat saying so."""


def _group_of(rec) -> str | None:
    g = rec.get("group")
    return str(g).strip().upper() if g else None


def _interval(draws) -> list[float]:
    return [float(x) for x in np.nanpercentile(draws, [2.5, 97.5])]


def _bootstrap(recs, fn, boot: int, seed: int) -> dict:
    point = fn(recs)
    rng = np.random.RandomState(seed)
    draws = {k: [] for k in point}
    for _ in range(boot):
        pick = [recs[i] for i in rng.randint(0, len(recs), len(recs))]
        try:
            vals = fn(pick)
        except Exception:                                   # noqa: BLE001  a draw with no fit
            continue
        for k, v in vals.items():
            draws[k].append(v)
    return {k: {"measured": float(point[k]), "lo": _interval(draws[k])[0],
                "hi": _interval(draws[k])[1]} for k in point}


def _jitter(record: dict, stream: str, group: str | None) -> dict:
    s = record["streams"][stream]
    stat = s.get("primary", "hwhm")
    if group is None:
        row = s[stat]
        return {"measured": float(row["jitter_sec"]), "lo": float(row["jitter_interval"][0]),
                "hi": float(row["jitter_interval"][1]), "statistic": stat,
                "draws_off_the_calibration": int(row.get("boot_outside_calibration", 0))}
    groups = {str(k).upper(): v for k, v in (s.get("groups") or {}).items()}
    if group not in groups:
        raise SystemExit(f"the jitter record has no {stream!r} entry for group {group!r}; "
                         f"run tools/measure_jitter_correlogram.py with --by-group")
    row = groups[group][stat]
    sig = row.get("sigma_sec", row.get("jitter_sec"))
    ci = row.get("sigma_interval", row.get("jitter_interval"))
    if sig is None or ci is None:
        raise SystemExit(f"the jitter record's {stream!r}/{group!r} entry has no calibrated "
                         f"jitter (keys: {sorted(row)})")
    return {"measured": float(sig), "lo": float(ci[0]), "hi": float(ci[1]), "statistic": stat}


def _gaps(intervals_dir: Path, stream: str, group: str | None) -> list[float]:
    out = []
    with (intervals_dir / "gaps.csv").open(encoding="utf-8", newline="") as fh:
        for row in csv.DictReader(fh):
            if row["stream"] != stream:
                continue
            if group is not None and row["group"].strip().upper() != group:
                continue
            out.append(round(float(row["gap_sec"]), 3))
    return out


def _events_per_hour(summary: dict, stream: str, group: str | None) -> dict:
    s = summary["summary"][stream]
    row = s["all"] if group is None else {str(k).upper(): v for k, v in s["groups"].items()}[group]
    return {"events_per_hour": float(row["events_per_hour"]), "events": int(row["n_events"]),
            "hours": float(row["hours"])}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--stage1", type=Path, required=True,
                    help="the stage 1 run folder: jitter/, rates/ and intervals/ on the default")
    ap.add_argument("--out", type=Path, default=REPO / "docs/learned/bench_sets")
    ap.add_argument("--jobs", type=int, default=8)
    ap.add_argument("--boot", type=int, default=200)
    ap.add_argument("--seed", type=int, default=20261112)
    ap.add_argument("--surrogates", type=int, default=1000)
    a = ap.parse_args(argv)

    import measure_coordination_rates as mcr
    import measure_slow_bench as msb
    import remeasure_bench as rb

    from bugarach import dataset
    from bugarach.groups import in_group_order
    from bugarach.io import load_folder

    folder = dataset.default()
    stamp = dataset.stamp()
    slices = load_folder(folder)
    n = len(slices)
    meta = {s.slice_id: {"group": (str(s.meta.get("group_id")).strip().upper()
                                   if s.meta.get("group_id") else None),
                         "mouse": str(s.meta.get("subject_id") or s.meta.get("mouse_id")
                                      or s.slice_id)} for s in slices}
    streams = [st for st in STREAMS if all(st in s.streams for s in slices)]
    groups = in_group_order({m["group"] for m in meta.values() if m["group"]})

    jitter_path = a.stage1 / "jitter" / "jitter_correlogram.json"
    rates_path = a.stage1 / "rates" / "coordination_rates.json"
    intervals_dir = a.stage1 / "intervals"
    jitter_rec = json.loads(jitter_path.read_text(encoding="utf-8"))
    intervals = json.loads((intervals_dir / "summary.json").read_text(encoding="utf-8"))
    for what, rec in (("jitter", jitter_rec), ("intervals", intervals)):
        on = (rec.get("dataset") or {}).get("name")
        if on != stamp["name"]:
            raise SystemExit(f"the {what} record was measured on {on!r}, and the default is "
                             f"{stamp['name']!r}")

    bins = msb.BINS
    a.out.mkdir(parents=True, exist_ok=True)
    written = []
    with ProcessPoolExecutor(a.jobs) as ex:
        rates = [r for r in ex.map(mcr._real, [(str(folder), i, a.seed) for i in range(n)]) if r]
        for stream in streams:
            recs = list(ex.map(msb._measure_recording,
                               [(str(folder), i, a.surrogates, bins, stream) for i in range(n)]))
            skipped = {r["slice_id"]: r["skipped"] for r in recs if r["skipped"]}
            recs = [r for r in recs if not r["skipped"]]
            shares = rb._shares_from_record(rates_path, stamp["name"], stream)
            for r in recs:
                r["share_hz"] = shares.get(r["slice_id"])
                r["group"] = meta[r["slice_id"]]["group"]
            for group in (None, *groups):
                name = ALL if group is None else group.lower()
                mine = [r for r in recs if group is None or _group_of(r) == group]
                if not mine:
                    continue
                ids = sorted(r["slice_id"] for r in mine)
                values = _bootstrap(mine, lambda rs: msb._all_values(rs, bins), a.boot, a.seed)
                values = {k: v for k, v in values.items()
                          if "@" not in k and k != "jitter_sec_clustering"}
                values["jitter_sec"] = _jitter(jitter_rec, stream, group)
                rr = [dict(r[stream], slice_id=r["slice_id"]) for r in rates
                      if stream in r and r["slice_id"] in ids]
                summ = mcr.summarize(rr, mcr.PRIMARY_W)[mcr.ADOPTED_MODEL]
                caveats = []
                if len(mine) < MIN_RECORDINGS:
                    caveats.append(f"{len(mine)} recordings: the quiet and busy backgrounds are "
                                   f"quartiles of {len(mine)} values")
                if values["jitter_sec"].get("draws_off_the_calibration"):
                    caveats.append(f"jitter: {values['jitter_sec']['draws_off_the_calibration']}"
                                   f" of {a.boot} bootstrap draws fell off the calibration curve")
                record = {
                    "set": f"{stream}_{name}", "stream": stream, "group": group or ALL,
                    "dataset": stamp, "window": rb.WINDOW_RULE,
                    "recordings": ids, "skipped": {k: v for k, v in skipped.items()},
                    "mice": len({meta[i]["mouse"] for i in ids}),
                    "values": values,
                    "width_quantiles": msb.width_quantiles(mine),
                    "elevated_rate_hz": float(summ["probe_background_hz"]),
                    "coordinated_share_of_rate": float(summ["coordinated_share_of_rate"]),
                    "events": _events_per_hour(intervals, stream, group),
                    "gaps_sec": _gaps(intervals_dir, stream, group),
                    "sources": {"jitter": rb._repo_relative(jitter_path),
                                "rates": rb._repo_relative(rates_path),
                                "intervals": rb._repo_relative(intervals_dir)},
                    "bootstrap_draws": a.boot, "seed": a.seed, "surrogates": a.surrogates,
                    "measured_on": _dt.date.today().isoformat(), "commit": rb._commit(),
                    "tool": "tools/measure_bench_sets.py", "caveats": caveats,
                }
                path = a.out / f"{stream}_{name}.json"
                path.write_text(json.dumps(record, indent=1, sort_keys=True) + "\n",
                                encoding="utf-8")
                written.append(path)
                v = values
                print(f"{record['set']:14s} {len(ids):2d} rec, {record['mice']} mice | cells "
                      f"{v['n_roi']['measured']:.0f} | participation "
                      f"{v['participation']['measured']:.3f} | jitter "
                      f"{v['jitter_sec']['measured']:.3f} s | background "
                      f"{v['regime_quiet_hz']['measured']:.4f} to "
                      f"{v['regime_busy_hz']['measured']:.4f} Hz | elevated "
                      f"{record['elevated_rate_hz']:.4f} Hz | "
                      f"{record['events']['events_per_hour']:.1f} events/h, "
                      f"{len(record['gaps_sec'])} gaps")
    print(f"wrote {len(written)} records to {rb._repo_relative(a.out)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
