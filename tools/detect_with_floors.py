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
  ``min_n`` (``bench.FLOORED_SETTING``). Rate+context and locust have none, so they run once
  (variant ``unfloored``) and every call is kept (ADR-0010 part 6);
* **chorus** (``chorus_norm`` and ``chorus_gain_norm``, the checkpoint each training run's own rule
  picked for that stream), once per window, every call kept, as for rate+context and locust.

**Every call carries its participants**, by one rule for every detector
(:data:`PARTICIPANT_PAD_SEC`): ROIs with an onset in [onset − 1 s, onset + width + 1 s]. Beside
each call are the window's own floor and its baseline floor. For a detector with no participation
setting, ``reaches_<variant>`` says whether the call reaches each floor, and ``windows.csv`` counts
those calls per floor, **labelled with its rule** (``count_rule``). The counts are readings of the
calls (verdict flips, calls lost at floor + 1); no call is removed. **The review tool shows what
detectors call, and never changes it** (ADR-0010 part 6, agreed by Tony 2026-09-25). Until then this
tool deleted the rate+context, locust and chorus calls whose participants, counted forward only
from the onset, missed the floor.

**Floors** are ``bugarach.event_floor.window_floor`` per window and stream, from that window's own
events: ``max(3, chance floor)`` at 1 call per hour, *J* = 20 s, 1,000 draws. A window shorter than
the shift can take (under 2*J* + 2 s) has no floor, and its floored rows are left empty rather than
filled with a default. On a baseline window the two floors are the same number.

**``--floor-offset N``** adds a variant ``own_plus_N``: the window's own floor raised by N co-active
ROIs, run and kept by the same rule as the other two. It is evidence for a decision (Tony,
2026-09-25, weighing floor + 1 for how confidently people call events near the floor), not
ADR-0008's rule, and the default output does not change.

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


PARTICIPANT_PAD_SEC = 1.0
"""How far either side of a call's span its participants are counted (ADR-0010 part 6). One rule for
every detector, stated on the page: ROIs with an onset in [onset − pad, onset + width + pad]. The
width is open for Tony (ADR-0010 open point 3), so it is a named constant rather than a literal.

It replaced ``[onset, onset + max(width, 2 s)]``, which looked only forward: chorus puts its onset
mid-stripe, so the old window missed the stripe's first half and the old filter deleted chorus
calls whose centred count cleared the floor (ADR-0010, Context)."""

PARTICIPANTS_RULE = ("ROIs with an onset in [onset - {pad:g} s, onset + width + {pad:g} s], "
                     "the same for every detector").format(pad=PARTICIPANT_PAD_SEC)

COUNT_RULE_RAN = "the detector ran at this floor, its own participation minimum (ADR-0008)"
COUNT_RULE_ALL = "every call the detector made; nothing removed"
COUNT_RULE_COUNTED = ("calls whose participants reach this floor, counted beside the calls; "
                      "no call removed (ADR-0010 part 6)")


def participants(trains_sec, onset: float, width: float,
                 pad: float = PARTICIPANT_PAD_SEC) -> int:
    """ROIs with at least one onset in ``[onset − pad, onset + width + pad]``. A missing or
    negative width counts as zero."""
    w = float(width) if np.isfinite(width) and width > 0 else 0.0
    lo, hi = onset - pad, onset + w + pad
    return int(sum(np.any((np.asarray(t, float) >= lo) & (np.asarray(t, float) <= hi))
                   for t in trains_sec))


def reaches(p: int, fl: dict, variants) -> dict:
    """``reaches_<variant>``: whether a call's participants reach each floor, or ``None`` where
    that floor does not exist. A label beside the call, never a filter on it."""
    return {f"reaches_{v}": (None if fl.get(v) is None else bool(p >= fl[v])) for v in variants}


def counted_rows(common: dict, det_name: str, parts, fl: dict, variants, hours) -> list[dict]:
    """The window rows of a detector with no participation setting: every call under
    ``unfloored``, then, per floor, how many of those calls reach it. The counts are labelled
    with their rule, because they are a reading of the calls, not calls a detector made."""
    out = []
    for variant, k, rule in (("unfloored", 0, COUNT_RULE_ALL),
                             *((v, fl[v], COUNT_RULE_COUNTED) for v in variants)):
        n = None if k is None else int(sum(p >= k for p in parts))
        out.append(dict(common, detector=det_name, variant=variant, min_participants=k,
                        n_calls=n, calls_per_hour=(n / hours) if n is not None and hours else None,
                        count_rule=rule))
    return out


def plus_variant(offset: int) -> str | None:
    """The variant name for the window's own floor raised by ``offset`` co-active ROIs, or
    ``None`` when there is no offset. Evidence for a decision, not a rule: ADR-0008's floor is
    ``own_floor``, and this runs beside it (Tony, 2026-09-25, weighing floor + 1)."""
    return f"own_plus_{int(offset)}" if offset else None


def recording_task(args):
    i, folder, settings, model_paths, draws, *rest = args
    offset = int(rest[0]) if rest else 0
    plus = plus_variant(offset)
    variants = VARIANTS + ((plus,) if plus else ())
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
                if plus:
                    fl[plus] = None if fl["own_floor"] is None else fl["own_floor"] + offset
                common = dict(**head, region_idx=idx, label=label,
                              window_kind="baseline" if is_baseline(label) else "treatment",
                              stream=sname, win_start=lo, win_end=hi, hours=hours,
                              n_roi=len(tr), **fl,
                              own_chance_floor=own.chance_floor if own else None,
                              own_floor_stable=own.stable if own else None)
                def run(det_name, params, k):
                    """One run of a coded detector, its calls inside this window."""
                    if det_name in ("coact", "rate", "sync"):
                        fn = {"coact": coact_detect, "rate": rate_detect,
                              "sync": sync_detect}[det_name]
                        p = dict(params)
                        if det_name in FLOORED:
                            p[FLOORED[det_name]] = int(k)
                        det = fn(tr, (lo, hi), **p)
                    else:
                        det = nested(det_name, params, k).streams[sname]
                    on = np.asarray(getattr(det, "onset_sec", getattr(det, "locs", [])), float)
                    wd = np.asarray(getattr(det, "width_sec", getattr(det, "widths", [])), float)
                    inside = (on >= lo) & (on < hi)
                    return on[inside], wd[inside]

                for det_name, params in settings[sname].items():
                    params = {k: v for k, v in params.items() if k != FLOORED.get(det_name)}
                    if det_name not in FLOORED:
                        # NO PARTICIPATION SETTING: THE DETECTOR RUNS AS DEFINED, ONCE, AND EVERY
                        # CALL IS KEPT (ADR-0010 part 6). Until 2026-09-25 this tool deleted the
                        # calls of rate+context and locust whose participants missed the floor,
                        # a rule of the tool's own that the bench never applied to them.
                        on, wd = run(det_name, params, 0)
                        parts = [participants(tr, a_, b_) for a_, b_ in zip(on, wd)]
                        for a_, b_, p_ in zip(on, wd, parts):
                            calls.append(dict(common, detector=det_name, variant="unfloored",
                                              onset_sec=float(a_), width_sec=float(b_),
                                              participants=int(p_),
                                              **reaches(p_, fl, variants)))
                        rows.extend(counted_rows(common, det_name, parts, fl, variants, hours))
                        continue
                    for variant in variants:
                        k = fl[variant]
                        if k is None:
                            rows.append(dict(common, detector=det_name, variant=variant,
                                             min_participants=None, n_calls=None,
                                             calls_per_hour=None, count_rule=COUNT_RULE_RAN))
                            continue
                        # The floor is this detector's own participation minimum: it ran at it,
                        # and every call it made is kept.
                        on, wd = run(det_name, params, k)
                        for a_, b_ in zip(on, wd):
                            calls.append(dict(common, detector=det_name, variant=variant,
                                              onset_sec=float(a_), width_sec=float(b_),
                                              participants=participants(tr, a_, b_)))
                        n = int(on.size)
                        rows.append(dict(common, detector=det_name, variant=variant,
                                         min_participants=int(k), n_calls=n,
                                         calls_per_hour=n / hours if hours else None,
                                         count_rule=COUNT_RULE_RAN))
                for name, path in model_paths.items():
                    if not name.endswith(f"@{sname}"):
                        continue
                    res, _ = _MODELS[path].predict(s, stream=sname, extent=(lo, hi))
                    parts = [participants(tr, a_, b_)
                             for a_, b_ in zip(res.onset_sec, res.width_sec)]
                    det_name = name.split("@")[0]
                    for a_, b_, p in zip(res.onset_sec, res.width_sec, parts):
                        calls.append(dict(common, detector=det_name, variant="unfloored",
                                          onset_sec=float(a_), width_sec=float(b_),
                                          participants=int(p), **reaches(p, fl, variants)))
                    rows.extend(counted_rows(common, det_name, parts, fl, variants, hours))
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
    ap.add_argument("--floor-offset", type=int, default=0,
                    help="also score every window at its own floor raised by this many co-active "
                         "ROIs, as the variant own_plus_<N> (default 0: no extra variant). "
                         "Evidence for a decision, not ADR-0008's rule")
    a = ap.parse_args(argv)
    a.out.mkdir(parents=True, exist_ok=True)
    plus = plus_variant(a.floor_offset)

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
                        [(i, str(folder), settings, model_paths, a.draws, a.floor_offset)
                         for i in range(n)])
    rows = [r for rec in recs for r in rec["rows"]]
    calls = [c for rec in recs for c in rec["calls"]]
    failed = [dict(slice_id=r["slice_id"], error=r["error"]) for r in recs if not r["ok"]]
    groups = in_group_order(r["group"] for r in recs if r.get("group"))
    fields = ["slice_id", "group", "mouse", "region_idx", "label", "window_kind", "stream",
              "detector", "variant", "count_rule", "min_participants", "n_calls",
              "calls_per_hour", "hours",
              "n_roi", "own_floor", "baseline_floor", *((plus,) if plus else ()),
              "own_chance_floor", "own_floor_stable", "win_start", "win_end"]
    with (a.out / "windows.csv").open("w", newline="", encoding="utf-8") as fh:
        wr = csv.DictWriter(fh, fieldnames=fields, extrasaction="ignore")
        wr.writeheader()
        wr.writerows(rows)
    cfields = ["slice_id", "group", "region_idx", "label", "window_kind", "stream", "detector",
               "variant", "onset_sec", "width_sec", "participants", "own_floor",
               "baseline_floor", *((plus,) if plus else ()),
               *(f"reaches_{v}" for v in (*VARIANTS, *((plus,) if plus else ())))]
    with (a.out / "calls.csv").open("w", newline="", encoding="utf-8") as fh:
        wr = csv.DictWriter(fh, fieldnames=cfields, extrasaction="ignore")
        wr.writeheader()
        wr.writerows(calls)
    res = dict(tag=TAG, dataset=dataset.stamp(), recordings=n, failed=failed,
               elapsed_sec=time.time() - t0, draws=a.draws, groups=groups, chosen=chosen,
               floor=FLOOR_LABEL + ": every window under its own floor and its recording's "
                     "baseline floor (event_floor.treatment_floors). CoactDetect, LoCo, binned "
                     "SCE and SPIKE-synch run at each floor; rate+context, locust and chorus run "
                     "once ('unfloored'), keep every call, and are counted against each floor "
                     "(ADR-0010 part 6)",
               participants_rule=PARTICIPANTS_RULE, participant_pad_sec=PARTICIPANT_PAD_SEC,
               count_rules=dict(ran=COUNT_RULE_RAN, unfloored=COUNT_RULE_ALL,
                                counted=COUNT_RULE_COUNTED),
               floor_offset=a.floor_offset, offset_variant=plus,
               summary=summarise(rows, groups),
               floors={rec["slice_id"]: rec["floors"] for rec in recs})
    (a.out / "results.json").write_text(json.dumps(res, indent=1, default=float) + "\n")
    print(f"{n} recordings, {len(failed)} failed, {len(calls)} calls, "
          f"{time.time() - t0:.0f} s; wrote {a.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
