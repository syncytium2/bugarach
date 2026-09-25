#!/usr/bin/env python3
"""Detection on the default export folder, every window scored under its own floor and its baseline's.

    python tools/detect_with_floors.py --candidates <candidates.json> --models <phase2 folder> \
        --out <run folder> [--workers 16] [--draws 1000]

**What it runs.** On every recording of ``dataset.default()`` (the export folder, read-only), every
analysis window the folder declares (``detect_folder.folder_analysis_windows``, the same windows
``bugarach detect`` scores), on the fast, slow and combined streams:

* **Every coded detector** in ``candidates.json`` at the setting ``tools/score_bench_candidates.py``
  recorded for that stream (the search's proposal where it had one, else the shipped operating
  point), run two ways (ADR-0008 decision 4, via ``event_floor.treatment_floors``): ``own_floor``
  at the window's own floor and ``baseline_floor`` at the same recording's baseline floor. The
  floor is the participation minimum of CoactDetect, LoCo and binned SCE and SPIKE-synch's
  ``min_n`` (``bench.FLOORED_SETTING``); rate+context and locust have none, so their calls are
  kept when their participants reach it. The pre-ADR-0008 ``tuned`` run of 2026-09-24 is gone:
  nothing tonight is scored pre-ADR-0008;
* **chorus** (``chorus_norm`` and ``chorus_gain_norm``, the checkpoint each training run's own rule
  picked for that stream), once per window. It has no participation parameter, so each call's
  **participants** are counted (ROIs with an onset inside the call's span, the span widened to the
  2 s co-activity window when it is shorter) and the call is kept or not under each floor. That is
  ADR-0008's "the scoring of treatment windows runs twice … reuses the same trained models".

**Floors** are ``bugarach.event_floor.window_floor`` per window and stream, from that window's own
events: ``max(3, chance floor)`` at 1 call per hour, *J* = 20 s, 1,000 draws. A window shorter than
the shift can take (under 2*J* + 2 s) has no floor, and its floored rows are left empty rather than
filled with a default. On a baseline window the two floors are the same number.

**What it writes** (``--out``): ``calls.csv`` (one row per call), ``windows.csv`` (one row per
recording × window × stream × detector × variant: floors, calls, calls per hour),
``results.json`` (the dataset stamp, settings, and the group summaries in ``bugarach.groups``
order), which is also the finish marker ``tools/archive_run.py`` waits for. Nothing is filtered:
every recording in the folder is run, and one that fails is recorded with its error.
"""
from __future__ import annotations

import argparse
import csv
import json
import math
import multiprocessing as mp
import sys
import time
from pathlib import Path

import numpy as np

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))

TAG = "detect-with-floors-2026-09-24"
STREAMS = ("fast", "slow", "combined")
VARIANTS = ("own_floor", "baseline_floor")
from bugarach.bench import FLOOR_LABEL  # noqa: E402  (after the sys.path line above)
from bugarach.bench import FLOORED_SETTING as FLOORED  # noqa: E402
# The detectors whose participation minimum the floor sets run at it. The rest (rate+context,
# locust) run as tuned and keep the calls whose participants reach the floor, as chorus does.
_MODELS: dict = {}


def is_baseline(label) -> bool:
    return (label or "").strip().lower().startswith("baseline")


def seeded(det: str, params: dict) -> dict:
    """``params`` with the fixed ``rng_seed`` `bugarach detect` gives every detector that draws
    random numbers (``detect_folder.RNG_SEED``), unless the settings name one.

    Without it locust and SCE draw their surrogate thresholds from an unseeded generator, so the
    same run gives different calls: the final-parameters night's two real-data runs differed in
    four locust verdicts for no other reason (2026-09-25)."""
    from bugarach.bench import OPERATING_POINTS
    from bugarach.detect_folder import RNG_SEED

    op = OPERATING_POINTS.get(det)
    if op is None or not op.takes_rng or "rng_seed" in params:
        return params
    return {**params, "rng_seed": RNG_SEED}


def frames_in(trains_sec, lo: float, dt: float) -> list[np.ndarray]:
    return [np.unique(np.floor((np.asarray(t, float) - lo) / dt + 1e-9).astype(np.int64))
            for t in trains_sec]


def participants(trains_sec, onset: float, width: float, min_span: float) -> int:
    """ROIs with at least one onset in ``[onset, onset + max(width, min_span)]``."""
    hi = onset + max(float(width), min_span)
    return int(sum(np.any((t >= onset) & (t <= hi)) for t in trains_sec))


def recording_task(args):
    i, folder, settings, model_paths, draws = args
    from bugarach import event_floor as ef
    from bugarach.combined import COMBINED, has_sources, stream_of
    from bugarach.detect_folder import _region_index, folder_analysis_windows, with_microscope
    from bugarach.detectors.cicada import cicada_detect
    from bugarach.detectors.coact import coact_detect
    from bugarach.detectors.loco import loco_detect
    from bugarach.detectors.rate import rate_detect, stream_trains
    from bugarach.detectors.sce import sce_detect
    from bugarach.detectors.sync import sync_detect
    from bugarach.io import load_folder

    s = load_folder(Path(folder))[i]
    meta = getattr(s, "meta", {}) or {}
    head = dict(slice_id=s.slice_id, group=(str(meta.get("group_id")).strip() or None)
                if meta.get("group_id") else None,
                mouse=str(meta.get("subject_id") or s.slice_id))
    try:
        s, windows = folder_analysis_windows(s)
        if has_sources(s) and COMBINED not in s.streams:
            s.streams[COMBINED] = stream_of(s, COMBINED)
        dt = s.require_dt()
        # The settings were tuned on the bench; rate+context's grid and locust's frame rate belong
        # to this recording's microscope, as in `bugarach detect` (detect_folder.with_microscope).
        # Until 2026-09-25 this tool ran CoactDetect only, so neither was ever reached.
        settings = {sn: {d: seeded(d, with_microscope(d, p, dt)) for d, p in by_det.items()}
                    for sn, by_det in settings.items()}
        for name, path in model_paths.items():
            if path not in _MODELS:
                from bugarach.learn.checkpoint import load
                _MODELS[path] = load(path)
        calls, rows, floors = [], [], {}
        # Every window's floor first, so the baseline floor is known before anything is scored.
        wins = []
        for w in windows:
            lo, hi = float(w.win_start), float(w.win_end)
            if hi <= lo:
                continue
            wins.append((w, lo, hi, _region_index(w), (w.label or "").strip() or None))
        for w, lo, hi, idx, label in wins:
            for sname in STREAMS:
                if sname not in s.streams:
                    continue
                tr = stream_trains(s.streams[sname], (lo, hi))
                n_frames = int(round((hi - lo) / dt))
                try:
                    f = ef.window_floor(frames_in(tr, lo, dt), n_frames, dt,
                                        key=(TAG, s.slice_id, sname, idx), draws=draws)
                    floors[(idx, sname)] = f
                except ValueError:
                    floors[(idx, sname)] = None
        base_idx = next((idx for _, _, _, idx, label in wins if is_baseline(label)), None)
        # Slice-level detectors (LoCo, binned SCE) take one participation minimum for the whole
        # recording, so they run once per distinct floor and each window keeps the calls of the
        # run at its own floor.
        nested_runs: dict = {}

        def nested(det_name, params, k):
            key = (det_name, int(k))
            if key not in nested_runs:
                fn = {"loco": loco_detect, "sce": sce_detect, "cicada": cicada_detect}[det_name]
                p = dict(params)
                if det_name in FLOORED:
                    p[FLOORED[det_name]] = int(k)
                nested_runs[key] = fn(s, **p)
            return nested_runs[key]

        for w, lo, hi, idx, label in wins:
            hours = (hi - lo) / 3600.0
            for sname in STREAMS:
                if sname not in s.streams:
                    continue
                tr = stream_trains(s.streams[sname], (lo, hi))
                own = floors.get((idx, sname))
                base = floors.get((base_idx, sname)) if base_idx is not None else None
                pair = ef.treatment_floors(own, base) if own and base else None
                fl = dict(own_floor=pair["own"] if pair else (own.floor if own else None),
                          baseline_floor=pair["baseline"] if pair else
                          (base.floor if base else None))
                common = dict(**head, region_idx=idx, label=label,
                              window_kind="baseline" if is_baseline(label) else "treatment",
                              stream=sname, win_start=lo, win_end=hi, hours=hours,
                              n_roi=len(tr), **fl,
                              own_chance_floor=own.chance_floor if own else None,
                              own_floor_stable=own.stable if own else None)
                for det_name, params in settings[sname].items():
                    params = {k: v for k, v in params.items() if k != FLOORED.get(det_name)}
                    for variant in VARIANTS:
                        k = fl[variant]
                        if k is None:
                            rows.append(dict(common, detector=det_name, variant=variant,
                                             min_participants=None, n_calls=None,
                                             calls_per_hour=None))
                            continue
                        if det_name in ("coact", "rate", "sync"):
                            fn = {"coact": coact_detect, "rate": rate_detect,
                                  "sync": sync_detect}[det_name]
                            p = dict(params)
                            if det_name in FLOORED:
                                p[FLOORED[det_name]] = int(k)
                            det = fn(tr, (lo, hi), **p)
                        else:
                            det = nested(det_name, params, k).streams[sname]
                        on = np.asarray(getattr(det, "onset_sec", getattr(det, "locs", [])),
                                        float)
                        wd = np.asarray(getattr(det, "width_sec", getattr(det, "widths", [])),
                                        float)
                        inside = (on >= lo) & (on < hi)
                        on, wd = on[inside], wd[inside]
                        parts = [participants(tr, a_, b_, ef.WINDOW_SEC)
                                 for a_, b_ in zip(on, wd)]
                        # A detector with no participation minimum has the floor applied to its
                        # calls' participants, as chorus does; one that takes it ran at it.
                        keep = ([True] * len(parts) if det_name in FLOORED
                                else [p_ >= k for p_ in parts])
                        for a_, b_, p_, ok in zip(on, wd, parts, keep):
                            if ok:
                                calls.append(dict(common, detector=det_name, variant=variant,
                                                  onset_sec=float(a_), width_sec=float(b_),
                                                  participants=int(p_)))
                        n = int(sum(keep))
                        rows.append(dict(common, detector=det_name, variant=variant,
                                         min_participants=int(k), n_calls=n,
                                         calls_per_hour=n / hours if hours else None))
                for name, path in model_paths.items():
                    if not name.endswith(f"@{sname}"):
                        continue
                    res, _ = _MODELS[path].predict(s, stream=sname, extent=(lo, hi))
                    parts = [participants(tr, a_, b_, ef.WINDOW_SEC)
                             for a_, b_ in zip(res.onset_sec, res.width_sec)]
                    det_name = name.split("@")[0]
                    for a_, b_, p in zip(res.onset_sec, res.width_sec, parts):
                        calls.append(dict(common, detector=det_name, variant="unfloored",
                                          onset_sec=float(a_), width_sec=float(b_),
                                          participants=int(p)))
                    for variant, k in (("unfloored", 0), ("own_floor", fl["own_floor"]),
                                       ("baseline_floor", fl["baseline_floor"])):
                        n = None if k is None else int(sum(p >= k for p in parts))
                        rows.append(dict(common, detector=det_name, variant=variant,
                                         min_participants=k, n_calls=n,
                                         calls_per_hour=(n / hours) if n is not None and hours
                                         else None))
        return dict(head, ok=True, rows=rows, calls=calls,
                    floors={f"{idx}|{sn}": (f.as_dict() if f else None)
                            for (idx, sn), f in floors.items()})
    except Exception as e:  # noqa: BLE001 - recorded, never dropped silently
        return dict(head, ok=False, error=f"{type(e).__name__}: {e}", rows=[], calls=[],
                    floors={})


def summarise(rows, groups):
    """Median calls per hour and median floors, per group × window kind × stream × detector ×
    variant, over recordings, with the number of recordings each median is taken over."""
    out = {}
    keyf = ("window_kind", "stream", "detector", "variant")
    for g in [*groups, "all"]:
        rs = [r for r in rows if g == "all" or r["group"] == g]
        cells = {}
        for r in rs:
            cells.setdefault(tuple(r[k] for k in keyf), []).append(r)
        for key, cell in cells.items():
            v = [r["calls_per_hour"] for r in cell if r["calls_per_hour"] is not None]
            fl = [r["own_floor"] for r in cell if r["own_floor"] is not None]
            out.setdefault(g, {})["|".join(map(str, key))] = dict(
                windows=len(cell), recordings=len({r["slice_id"] for r in cell}),
                median_calls_per_hour=float(np.median(v)) if v else None,
                q25_calls_per_hour=float(np.percentile(v, 25)) if v else None,
                q75_calls_per_hour=float(np.percentile(v, 75)) if v else None,
                median_own_floor=float(np.median(fl)) if fl else None)
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--candidates", type=Path, required=True)
    ap.add_argument("--models", type=Path, required=True, help="the phase-2 folder")
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--workers", type=int, default=16)
    ap.add_argument("--draws", type=int, default=1000)
    ap.add_argument("--limit", type=int, default=None)
    a = ap.parse_args(argv)
    a.out.mkdir(parents=True, exist_ok=True)

    from bugarach import dataset
    from bugarach.groups import in_group_order
    from bugarach.io import load_folder

    cand = json.loads(a.candidates.read_text())
    settings, model_paths, chosen = {}, {}, {}
    for sname in STREAMS:
        B = cand["benches"][sname]
        dets = B.get("detectors") or {"coact": dict(shipped=B["coact_shipped"],
                                                    proposal=B["coact_proposal"])}
        settings[sname], chosen[sname] = {}, dict(detectors={}, chorus={})
        for det, info in dets.items():
            prop = info["proposal"]
            use = prop["name"] != "shipped"
            settings[sname][det] = dict(prop["params"] if use else info["shipped"])
            chosen[sname]["detectors"][det] = dict(which="proposal" if use else "shipped",
                                                   params=settings[sname][det])
        for m, info in B["chorus"].items():
            if info.get("picked"):
                model_paths[f"{m}@{sname}"] = str(a.models / f"models-{sname}" / info["picked"])
                chosen[sname]["chorus"][m] = info["picked"]
    folder = dataset.default()
    n = len(load_folder(folder))
    if a.limit:
        n = min(n, a.limit)
    t0 = time.time()
    with mp.Pool(a.workers) as pool:
        recs = pool.map(recording_task,
                        [(i, str(folder), settings, model_paths, a.draws) for i in range(n)])
    rows = [r for rec in recs for r in rec["rows"]]
    calls = [c for rec in recs for c in rec["calls"]]
    failed = [dict(slice_id=r["slice_id"], error=r["error"]) for r in recs if not r["ok"]]
    groups = in_group_order(r["group"] for r in recs if r.get("group"))
    fields = ["slice_id", "group", "mouse", "region_idx", "label", "window_kind", "stream",
              "detector", "variant", "min_participants", "n_calls", "calls_per_hour", "hours",
              "n_roi", "own_floor", "baseline_floor", "own_chance_floor", "own_floor_stable",
              "win_start", "win_end"]
    with (a.out / "windows.csv").open("w", newline="", encoding="utf-8") as fh:
        wr = csv.DictWriter(fh, fieldnames=fields, extrasaction="ignore")
        wr.writeheader()
        wr.writerows(rows)
    cfields = ["slice_id", "group", "region_idx", "label", "window_kind", "stream", "detector",
               "variant", "onset_sec", "width_sec", "participants", "own_floor",
               "baseline_floor"]
    with (a.out / "calls.csv").open("w", newline="", encoding="utf-8") as fh:
        wr = csv.DictWriter(fh, fieldnames=cfields, extrasaction="ignore")
        wr.writeheader()
        wr.writerows(calls)
    res = dict(tag=TAG, dataset=dataset.stamp(), recordings=n, failed=failed,
               elapsed_sec=time.time() - t0, draws=a.draws, groups=groups, chosen=chosen,
               floor=FLOOR_LABEL + ": every window under its own floor and its recording's "
                     "baseline floor (event_floor.treatment_floors); chorus also 'unfloored'",
               participants_rule="ROIs with an onset in [onset, onset + max(width, 2 s)]",
               summary=summarise(rows, groups),
               floors={rec["slice_id"]: rec["floors"] for rec in recs})
    (a.out / "results.json").write_text(json.dumps(res, indent=1, default=float) + "\n")
    print(f"{n} recordings, {len(failed)} failed, {len(calls)} calls, "
          f"{time.time() - t0:.0f} s; wrote {a.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
