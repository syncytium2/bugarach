#!/usr/bin/env python3
"""chorus over the whole recording against chorus over 409.6 s pieces: does the span move the calls?

    python tools/measure_chorus_context_span.py --models <phase2 folder> --out <folder> [--workers 20]

**Why.** ``chorus_norm`` and ``chorus_gain_norm`` standardise each cell's encoder output over the
span they are given (``h.mean/std(dim=2)`` in ``bugarach.learn.nets.chorus``). They are trained on
4,096-frame crops (409.6 s at 0.1 s frames) and run on whole 2,700 s bench recordings, or on one
whole real analysis window. Tony, 2026-09-24: *"run the chorus variants over 409.6s"*. A
measurement; it decides nothing, retrains nothing and changes no detector or floor.

**Models:** the checkpoint each overnight training run picked, per stream (the ones
``tools/score_cross_stream.py`` and ``tools/detect_with_floors.py`` use), read from the overnight
Phase 2 record. Every model runs on all three benches.

**Two inference modes, same weights:**

* ``whole``: one call to ``Trained.predict`` over the whole recording (bench) or window (real);
* ``pieces``: consecutive non-overlapping 409.6 s pieces from the start of the recording or window,
  each predicted separately through ``extent``, calls concatenated. **The last piece is whatever
  remains, shorter than 409.6 s, and is predicted as it is**; nothing is padded or merged.

**The edge effect.** The model's receptive field is about ±27 s (31 frames in the per-cell stack,
511 in the head, at 0.1 s), so a piece edge cuts it. Every bench result is also given **away from
edges**: planted events and calls within :data:`EDGE_SEC` of an internal piece edge are left out of
both modes' scoring, so the difference that remains is the span's alone and the edge effect is the
difference between the two.

**Bench scoring** is ``tools/score_bench_candidates.py``'s: seeds 6000–6023 per background, the
no-coordination recording on seeds 56000–56011, F1 as scored and with decoy calls left out of
precision (ADR-0006), recall, precision, calls per minute inside the elevated-rate stretch, false
alarms per hour on the no-coordination recording; bootstrap 95% intervals over seeds for each mode
and for the paired whole − pieces difference. **Floor: pre-ADR-0008**, as the models were tuned.

**Real data** (``dataset.default()``, stamped): every analysis window, all three streams, each
stream's own models; calls per hour per mode, and the share of calls that match between the modes
(onsets within the scorer's tolerance, one to one). Descriptive only.
"""
from __future__ import annotations

import argparse
import dataclasses
import importlib
import json
import multiprocessing as mp
import sys
import time
from pathlib import Path
from types import SimpleNamespace

import numpy as np

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))
sys.path.insert(0, str(REPO / "tools"))

from score_bench_candidates import BENCHES, NULLS, REG, SEEDS  # noqa: E402

PIECE_SEC = 409.6
EDGE_SEC = 30.0
STREAMS = tuple(BENCHES)
MODELS = ("chorus_norm", "chorus_gain_norm")
PHASE2 = REPO / "docs" / "learned" / "runs" / "2026-09-24-overnight-coact-chorus" / "candidates.json"
N_BOOT = 2000
_LOADED: dict = {}


def pieces(lo: float, hi: float, size: float = PIECE_SEC) -> list[tuple[float, float]]:
    """Consecutive non-overlapping spans of ``size`` from ``lo``; the last is what remains."""
    out, a = [], lo
    while a < hi - 1e-9:
        out.append((a, min(a + size, hi)))
        a += size
    return out


def model(path: str):
    if path not in _LOADED:
        from bugarach.learn.checkpoint import load
        _LOADED[path] = load(path)
    return _LOADED[path]


def run(tr, sl, extent, mode: str, stream=None):
    """Calls as ``SimpleNamespace(onset_sec, width_sec)`` for one mode over ``extent``."""
    if mode == "whole":
        res, _ = tr.predict(sl, stream=stream, extent=extent)
        return SimpleNamespace(onset_sec=np.asarray(res.onset_sec, float),
                               width_sec=np.asarray(res.width_sec, float))
    on, wd = [], []
    for a, b in pieces(*extent):
        res, _ = tr.predict(sl, stream=stream, extent=(a, b))
        on += list(np.asarray(res.onset_sec, float))
        wd += list(np.asarray(res.width_sec, float))
    return SimpleNamespace(onset_sec=np.asarray(on), width_sec=np.asarray(wd))


def edges_of(extent) -> np.ndarray:
    """The internal piece edges: every boundary but the extent's own ends."""
    ps = pieces(*extent)
    return np.array([b for _, b in ps[:-1]])


def away(t, edges) -> np.ndarray:
    t = np.asarray(t, float)
    if not edges.size:
        return np.ones(t.shape, bool)
    return np.min(np.abs(t[:, None] - edges[None, :]), axis=1) > EDGE_SEC


def bench_job(args):
    mname, mstream, path, bench, regime, seed = args
    from bugarach.detectors.rate import recording_extent
    from bugarach.score import score_detections, score_stream
    b = importlib.import_module(BENCHES[bench])
    tr = model(path)
    if regime == "null":
        sl, gt = b.make_null_recording(seed + 50_000)
        ext = recording_extent(sl)
        return (mname, mstream, bench, regime, seed), {
            m: dict(n=int(run(tr, sl, ext, m).onset_sec.size), hours=gt.params["duration_sec"] / 3600)
            for m in ("whole", "pieces")}
    sl, gt = b.make_recording(regime, seed)
    ext = recording_extent(sl)
    E = edges_of(ext)
    gt_away = dataclasses.replace(gt, events=[e for e in gt.events if away([e.time], E)[0]])
    out = {}
    for m in ("whole", "pieces"):
        det = run(tr, sl, ext, m)
        keep = away(det.onset_sec, E)
        out[m] = dict(
            full=score_stream(gt, det),
            away=score_detections(gt_away, det.onset_sec[keep], widths=det.width_sec[keep]),
            onsets=det.onset_sec.tolist(), widths=det.width_sec.tolist(),
            near_edge_calls=int((~keep).sum()))
    out["edges"] = E.tolist()
    return (mname, mstream, bench, regime, seed), out


def pooled(scores, regime):
    from bugarach.bench import pool_scores
    # ``seeds`` sets the minutes behind the stretch call rate; without it the rate is per recording
    # pooled over all of them, 24 times too high.
    r = pool_scores(scores, detector="chorus", regime=regime, seeds=tuple(range(len(scores))))
    return dict(f1=r.f1, f1_without_decoys=r.f1_without_decoys, recall=r.recall,
                precision=r.precision, probe_calls_per_min=r.hot_fa_per_min)


def cell(got, key, rng) -> dict:
    """Both modes and their paired difference, per background, with bootstrap over seeds."""
    mname, mstream, bench = key
    out = {}
    for regime in REG:
        rows = [got[(mname, mstream, bench, regime, s)] for s in SEEDS]
        res = {}
        for part in ("full", "away"):
            vals = {m: pooled([r[m][part] for r in rows], regime) for m in ("whole", "pieces")}
            boots = {m: [] for m in ("whole", "pieces", "diff")}
            for _ in range(N_BOOT):
                idx = rng.randint(0, len(rows), len(rows))
                w = pooled([rows[i]["whole"][part] for i in idx], regime)
                p = pooled([rows[i]["pieces"][part] for i in idx], regime)
                boots["whole"].append(w)
                boots["pieces"].append(p)
                boots["diff"].append({k: w[k] - p[k] for k in w})
            ci = {m: {k: np.nanpercentile([b[k] for b in boots[m]], [2.5, 97.5]).tolist()
                      for k in vals["whole"]} for m in boots}
            res[part] = dict(whole=vals["whole"], pieces=vals["pieces"],
                             diff={k: vals["whole"][k] - vals["pieces"][k] for k in vals["whole"]},
                             ci=ci)
        res["near_edge_calls"] = {m: int(sum(r[m]["near_edge_calls"] for r in rows))
                                  for m in ("whole", "pieces")}
        out[regime] = res
    nulls = [got[(mname, mstream, bench, "null", s)] for s in NULLS]
    def rate(ns, m):
        return sum(n[m]["n"] for n in ns) / sum(n[m]["hours"] for n in ns)

    out["null_calls_per_hour"] = {m: rate(nulls, m) for m in ("whole", "pieces")}
    boots = {"whole": [], "pieces": [], "diff": []}
    for _ in range(N_BOOT):
        ns = [nulls[i] for i in rng.randint(0, len(nulls), len(nulls))]
        w, p = rate(ns, "whole"), rate(ns, "pieces")
        boots["whole"].append(w)
        boots["pieces"].append(p)
        boots["diff"].append(w - p)
    out["null_calls_per_hour_ci"] = {m: np.percentile(v, [2.5, 97.5]).tolist()
                                     for m, v in boots.items()}
    return out


def match_share(a, b, tol) -> tuple[int, int, int]:
    """One-to-one matches between onset lists within ``tol``, closest first."""
    a, b = np.asarray(a, float), np.asarray(b, float)
    if not a.size or not b.size:
        return 0, a.size, b.size
    d = np.abs(a[:, None] - b[None, :])
    pairs = sorted(zip(d.ravel(), *np.unravel_index(np.arange(d.size), d.shape)))
    ua, ub, n = set(), set(), 0
    for dist, i, j in pairs:
        if dist > tol:
            break
        if i not in ua and j not in ub:
            ua.add(i)
            ub.add(j)
            n += 1
    return n, a.size, b.size


def real_job(args):
    i, folder, paths = args
    from bugarach.combined import COMBINED, has_sources, stream_of
    from bugarach.detect_folder import folder_analysis_windows
    from bugarach.io import load_folder
    from bugarach.score import TOL_SEC
    s = load_folder(Path(folder))[i]
    meta = getattr(s, "meta", {}) or {}
    head = dict(slice_id=s.slice_id, group=(str(meta.get("group_id")).strip() or None)
                if meta.get("group_id") else None,
                mouse=str(meta.get("subject_id") or s.slice_id))
    s, windows = folder_analysis_windows(s)
    if has_sources(s) and COMBINED not in s.streams:
        s.streams[COMBINED] = stream_of(s, COMBINED)
    rows = []
    for w in windows:
        lo, hi = float(w.win_start), float(w.win_end)
        if hi <= lo:
            continue
        label = (w.label or "").strip()
        for sname in STREAMS:
            if sname not in s.streams:
                continue
            for mname in MODELS:
                tr = model(paths[f"{mname}@{sname}"])
                c = {m: run(tr, s, (lo, hi), m, stream=sname).onset_sec for m in ("whole", "pieces")}
                n, nw, npc = match_share(c["whole"], c["pieces"], TOL_SEC)
                rows.append(dict(head, label=label, stream=sname, model=mname,
                                 hours=(hi - lo) / 3600, whole=int(nw), pieces=int(npc),
                                 matched=int(n)))
    return rows


def window_kind(label) -> str:
    return "baseline" if (label or "").strip().lower().startswith("baseline") else "treatment"


def real_summary(rows) -> dict:
    """Calls per hour per mode and the share matched, per model x stream x window kind x group."""
    from bugarach.groups import in_group_order
    groups = list(in_group_order({r["group"] for r in rows if r.get("group")}))
    out = {}
    for sname in STREAMS:
        for mname in MODELS:
            for kind in ("baseline", "treatment", "all"):
                for g in [*groups, "all"]:
                    rs = [r for r in rows if r["stream"] == sname and r["model"] == mname
                          and (g == "all" or r["group"] == g)
                          and (kind == "all" or window_kind(r["label"]) == kind)]
                    if not rs:
                        continue
                    h = sum(r["hours"] for r in rs)
                    w, p, m = (sum(r[k] for r in rs) for k in ("whole", "pieces", "matched"))
                    out[f"{mname}@{sname}|{kind}|{g}"] = dict(
                        windows=len(rs), hours=h, whole_per_hour=w / h, pieces_per_hour=p / h,
                        whole=w, pieces=p, matched=m,
                        share_of_whole_matched=m / w if w else None,
                        share_of_pieces_matched=m / p if p else None)
    return dict(groups=groups, cells=out)


def public(paths: dict, models: Path) -> dict:
    """Model paths as the record keeps them: under the darkroom, never a personal absolute path
    (SAP004; this repository is public)."""
    from bugarach.paths import darkroom
    try:
        base = Path(models).resolve().relative_to(darkroom().resolve()).as_posix()
        base = f"<darkroom>/bugarach/{base}"
    except ValueError:
        base = f"<models>/{Path(models).name}"
    return {k: f"{base}/{Path(v).parent.name}/{Path(v).name}" for k, v in paths.items()}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--models", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--workers", type=int, default=20)
    ap.add_argument("--limit", type=int, default=None, help="real recordings (smoke runs)")
    a = ap.parse_args(argv)
    a.out.mkdir(parents=True, exist_ok=True)
    cand = json.loads(PHASE2.read_text())
    paths = {f"{m}@{s}": str(a.models / f"models-{s}" / cand["benches"][s]["chorus"][m]["picked"])
             for s in STREAMS for m in MODELS}
    t0 = time.time()
    jobs = [(m, s, paths[f"{m}@{s}"], b, reg, seed) for m in MODELS for s in STREAMS
            for b in STREAMS for reg in (*REG, "null")
            for seed in (NULLS if reg == "null" else SEEDS)]
    from bugarach import dataset
    from bugarach.io import load_folder
    folder = dataset.default()
    n = len(load_folder(folder))
    if a.limit:
        n = min(n, a.limit)
    with mp.Pool(a.workers) as pool:
        got = dict(pool.map(bench_job, jobs, chunksize=2))
        real = [r for rs in pool.map(real_job, [(i, str(folder), paths) for i in range(n)])
                for r in rs]
    rng = np.random.RandomState(20260924)
    bench = {f"{m}@{s}|on {b}": cell(got, (m, s, b), rng) for m in MODELS for s in STREAMS
             for b in STREAMS}
    # Figure 2's recording, by rule rather than by eye: the cell where the modes' F1 differ most,
    # and in it the seed where their call counts differ most.
    ck, creg = max(((k, reg) for k in bench for reg in REG),
                   key=lambda kr: abs(bench[kr[0]][kr[1]]["full"]["diff"]["f1"]))
    mname, rest = ck.split("@")
    sname, bname = rest.split("|on ")
    seed = max(SEEDS, key=lambda s: abs(len(got[(mname, sname, bname, creg, s)]["whole"]["onsets"])
                                        - len(got[(mname, sname, bname, creg, s)]["pieces"]["onsets"])))
    ex = got[(mname, sname, bname, creg, seed)]
    res = dict(dataset=dataset.stamp(), piece_sec=PIECE_SEC, edge_sec=EDGE_SEC,
               seeds=[SEEDS[0], SEEDS[-1]], null_seeds=[NULLS[0] + 50_000, NULLS[-1] + 50_000],
               n_boot=N_BOOT, floor="pre-ADR-0008", models=public(paths, a.models), bench=bench, real=real,
               real_summary=real_summary(real),
               example=dict(model=f"{mname}@{sname}", bench=bname, regime=creg,
                            seed=seed, edges=ex["edges"],
                            rule="largest |whole - pieces| F1 cell; in it, the seed whose two "
                                 "modes' call counts differ most",
                            whole=dict(onsets=ex["whole"]["onsets"], widths=ex["whole"]["widths"]),
                            pieces=dict(onsets=ex["pieces"]["onsets"],
                                        widths=ex["pieces"]["widths"])),
               elapsed_sec=time.time() - t0)
    (a.out / "results.json").write_text(json.dumps(res, default=float) + "\n")
    print(f"{len(jobs)} bench jobs, {n} recordings, {time.time() - t0:.0f} s; wrote {a.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
