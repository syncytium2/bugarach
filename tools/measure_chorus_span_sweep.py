#!/usr/bin/env python3
"""How short a span chorus can run on: the 409.6 s-trained checkpoints over shorter and shorter pieces.

    python tools/measure_chorus_span_sweep.py --models <phase2 folder> --out <folder> [--workers 20]

**Why.** Tony, 2026-09-24, after the context-span run (``tools/measure_chorus_context_span.py``):
*"what if we test how little chorus needs to see?"* and *"train it at 400, run it short"*. The
checkpoints are the ones each overnight training run picked, trained on 4,096-frame (409.6 s)
crops; nothing is retrained. A measurement; it decides nothing.

**Modes, same weights:** ``whole`` (one prediction over the recording or window) and, for each
length in :data:`LENGTHS`, consecutive non-overlapping pieces of that length from the start of the
extent, each predicted separately through ``extent``, calls concatenated. The last piece of each is
whatever remains and is predicted as it is (``measure_chorus_context_span.pieces``).

**What a piece can see.** The model's receptive field is about ±27 s, so a 60 s piece barely holds
one full view and a 30 s piece never does. Every piece is also standardised over its own span, so a
short piece is normalised against very few events. This is **not** a causal test: inside a piece
the model still looks up to 27 s ahead.

**Scoring** is ``tools/score_bench_candidates.py``'s over everything, edges included (below 60 s
every call is within 30 s of an edge, so the context-span run's away-from-edge scoring has nothing
left to score): seeds 6000–6023 per background, the no-coordination recording on seeds
56000–56011, F1 as scored and without decoys (ADR-0006), recall, precision, calls per minute in the
elevated-rate stretch, false alarms per hour on the no-coordination recording, each with a bootstrap
95% interval over seeds and the paired difference from ``whole``. Floor: pre-ADR-0008.

**Real data** (``dataset.default()``, stamped): every analysis window, all three streams, each
stream's own models; calls per hour per mode and the share of ``whole``'s calls that each piece
length reproduces within the scorer's tolerance. Descriptive only.
"""
from __future__ import annotations

import argparse
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

from measure_chorus_context_span import (  # noqa: E402
    MODELS, PHASE2, STREAMS, match_share, model, pieces, public, window_kind)
from score_bench_candidates import BENCHES, NULLS, REG, SEEDS  # noqa: E402

LENGTHS = (409.6, 300.0, 200.0, 100.0, 60.0, 30.0)
MODES = ("whole", *(f"{L:g}s" for L in LENGTHS))
METRICS = ("f1", "f1_without_decoys", "recall", "precision", "probe_calls_per_min")
N_BOOT = 2000


def run(tr, sl, extent, mode: str, stream=None):
    """Calls as ``SimpleNamespace(onset_sec, width_sec)``; ``mode`` is ``whole`` or ``<L>s``."""
    spans = [extent] if mode == "whole" else pieces(*extent, size=float(mode[:-1]))
    on, wd = [], []
    for a, b in spans:
        res, _ = tr.predict(sl, stream=stream, extent=(a, b))
        on += list(np.asarray(res.onset_sec, float))
        wd += list(np.asarray(res.width_sec, float))
    return SimpleNamespace(onset_sec=np.asarray(on), width_sec=np.asarray(wd))


def bench_job(args):
    mname, mstream, path, bench, regime, seed = args
    from bugarach.detectors.rate import recording_extent
    from bugarach.score import score_stream
    b = importlib.import_module(BENCHES[bench])
    tr = model(path)
    if regime == "null":
        sl, gt = b.make_null_recording(seed + 50_000)
        ext = recording_extent(sl)
        return (mname, mstream, bench, regime, seed), {
            m: dict(n=int(run(tr, sl, ext, m).onset_sec.size), hours=gt.params["duration_sec"] / 3600)
            for m in MODES}
    sl, gt = b.make_recording(regime, seed)
    ext = recording_extent(sl)
    return (mname, mstream, bench, regime, seed), {m: score_stream(gt, run(tr, sl, ext, m))
                                                   for m in MODES}


def pooled(scores, regime):
    from bugarach.bench import pool_scores
    # ``seeds`` sets the minutes behind the stretch call rate (one stretch per recording).
    r = pool_scores(scores, detector="chorus", regime=regime, seeds=tuple(range(len(scores))))
    return dict(f1=r.f1, f1_without_decoys=r.f1_without_decoys, recall=r.recall,
                precision=r.precision, probe_calls_per_min=r.hot_fa_per_min)


def cell(got, key, rng) -> dict:
    """Every mode and its paired difference from ``whole``, per background, bootstrap over seeds."""
    mname, mstream, bench = key
    out = {}
    for regime in REG:
        rows = [got[(mname, mstream, bench, regime, s)] for s in SEEDS]
        vals = {m: pooled([r[m] for r in rows], regime) for m in MODES}
        boots = {m: [] for m in MODES}
        for _ in range(N_BOOT):
            idx = rng.randint(0, len(rows), len(rows))
            for m in MODES:
                boots[m].append(pooled([rows[i][m] for i in idx], regime))
        ci = {m: {k: np.nanpercentile([b[k] for b in boots[m]], [2.5, 97.5]).tolist()
                  for k in METRICS} for m in MODES}
        diff = {m: {k: vals[m][k] - vals["whole"][k] for k in METRICS} for m in MODES[1:]}
        diff_ci = {m: {k: np.nanpercentile([boots[m][j][k] - boots["whole"][j][k]
                                            for j in range(N_BOOT)], [2.5, 97.5]).tolist()
                       for k in METRICS} for m in MODES[1:]}
        out[regime] = dict(value=vals, ci=ci, diff_from_whole=diff, diff_ci=diff_ci)
    nulls = [got[(mname, mstream, bench, "null", s)] for s in NULLS]

    def rate(ns, m):
        return sum(n[m]["n"] for n in ns) / sum(n[m]["hours"] for n in ns)

    nb = {m: [] for m in MODES}
    for _ in range(N_BOOT):
        ns = [nulls[i] for i in rng.randint(0, len(nulls), len(nulls))]
        for m in MODES:
            nb[m].append(rate(ns, m))
    out["null_calls_per_hour"] = {m: rate(nulls, m) for m in MODES}
    out["null_calls_per_hour_ci"] = {m: np.percentile(nb[m], [2.5, 97.5]).tolist() for m in MODES}
    out["null_diff_ci"] = {m: np.percentile(np.subtract(nb[m], nb["whole"]), [2.5, 97.5]).tolist()
                           for m in MODES[1:]}
    return out


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
                c = {m: run(tr, s, (lo, hi), m, stream=sname).onset_sec for m in MODES}
                row = dict(head, label=label, stream=sname, model=mname, hours=(hi - lo) / 3600,
                           calls={m: int(c[m].size) for m in MODES})
                row["matched_with_whole"] = {m: int(match_share(c["whole"], c[m], TOL_SEC)[0])
                                             for m in MODES[1:]}
                rows.append(row)
    return rows


def real_summary(rows) -> dict:
    """Calls per hour per mode and the share of whole's calls each mode reproduces, per model x
    stream x window kind x group."""
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
                    calls = {m: sum(r["calls"][m] for r in rs) for m in MODES}
                    matched = {m: sum(r["matched_with_whole"][m] for r in rs) for m in MODES[1:]}
                    out[f"{mname}@{sname}|{kind}|{g}"] = dict(
                        windows=len(rs), hours=h, calls=calls,
                        calls_per_hour={m: calls[m] / h for m in MODES}, matched_with_whole=matched,
                        share_of_whole_reproduced={m: matched[m] / calls["whole"] if calls["whole"]
                                                   else None for m in MODES[1:]},
                        share_matching_whole={m: matched[m] / calls[m] if calls[m] else None
                                              for m in MODES[1:]})
    return dict(groups=groups, cells=out)


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
    res = dict(dataset=dataset.stamp(), lengths_sec=list(LENGTHS), modes=list(MODES),
               seeds=[SEEDS[0], SEEDS[-1]], null_seeds=[NULLS[0] + 50_000, NULLS[-1] + 50_000],
               n_boot=N_BOOT, floor="pre-ADR-0008", models=public(paths, a.models), bench=bench,
               real=real, real_summary=real_summary(real), elapsed_sec=time.time() - t0)
    (a.out / "results.json").write_text(json.dumps(res, default=float) + "\n")
    print(f"{len(jobs)} bench jobs x {len(MODES)} modes, {n} recordings, {time.time() - t0:.0f} s; "
          f"wrote {a.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
