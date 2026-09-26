#!/usr/bin/env python3
"""Score tuned CoactDetect settings and trained chorus checkpoints on bench seeds nothing chose on.

    python tools/score_bench_candidates.py --phase2 <folder> [--phase2 <folder> ...] --out <folder>

``--phase2`` repeats: the full-panel night (ADR-0010) searched and trained on two machines, each
into its own folder, and the scorer reads both in place rather than from a copy. Each search and
each training log is taken from the one root that holds it; two roots holding the same one is an
error, never a silent choice. Every model the training tool trains (its ``MODELS``) is scored
when its log is there.

**Why.** The overnight run of 2026-09-24 tuned CoactDetect (``tools/search_all_settings.py``) and
trained two chorus nets (``tools/train_learned_on_bench.py``) on each of the fast, slow and combined
benches. Each tool scores on its own held-out seeds, and chorus's best seed is *chosen* on them, so
its F1 there is a selection score. This tool scores every candidate on **fresh** seeds
(:data:`SEEDS`, both backgrounds) so the two families are compared on recordings neither selection
saw, and it reports F1 **both ways** (ADR-0006): as scored, and with calls on decoys left out of
precision.

**Candidates per bench.**

* CoactDetect at the bench's shipped operating point, and at the search's proposal: the held-out
  candidate with the highest mean F1 whose gain over the shipped point has a 95% bootstrap interval
  above zero (the repository's retune rule), or the shipped point when none has. **Proposals are
  not written into the bench**; adopting one is Tony's.
* Every chorus seed that was trained, and which seed the training tool's own rule picks (highest
  mean held-out F1 among seeds at or under CoactDetect's empty-recording budget).

**Collapse** (``docs/todo/2026-09-19-chorus-norm-does-not-train-at-lr-0.03.md``): a fit that makes
exactly one call on every recording. Flagged per seed with the count of recordings where it made
one call, and kept in the table: dropping a collapsed fit would select on the outcome.

The run is stamped with the bench it measured; the bench is simulated, so there is no dataset.
"""
from __future__ import annotations

import argparse
import importlib
import json
import math
import multiprocessing as mp
import re
import sys
from pathlib import Path

import numpy as np

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))

BENCHES = {"fast": "bugarach.bench", "slow": "bugarach.bench_slow",
           "combined": "bugarach.bench_combined"}
REG = ("baseline_quiet", "baseline_busy")
SEEDS = tuple(range(6000, 6024))
NULLS = tuple(range(6000, 6012))
sys.path.insert(0, str(REPO / "tools"))
from train_learned_on_bench import MODELS  # noqa: E402  the panel the training tool trains
_MODEL_CACHE: dict = {}
BOOTSTRAP = 2000
BOOTSTRAP_SEED = 20260925


def seeds_for(bench: str) -> tuple:
    """Fresh seeds for ``bench``: :data:`SEEDS`, doubled on fast under a realistic spacing
    (``bench.seed_factor``; ADR-0010 ruling 2), continuing the same range."""
    from bugarach.bench import seed_factor
    return tuple(range(SEEDS[0], SEEDS[0] + len(SEEDS) * seed_factor(bench)))


def nulls_for(bench: str) -> tuple:
    """No-coordination and elevated-rate seeds for ``bench``: :data:`NULLS`, doubled the same way."""
    from bugarach.bench import seed_factor
    return tuple(range(NULLS[0], NULLS[0] + len(NULLS) * seed_factor(bench)))


def per_seed_f1(got: dict, pool_scores, bench: str, kind: str, name: str, seeds) -> np.ndarray:
    """F1 per seed, pooled over that seed's quiet and busy recordings."""
    return np.array([pool_scores([got[(bench, kind, name, reg, s)] for reg in REG],
                                 detector=kind, regime="both").f1 for s in seeds], float)


def paired_difference(f1: np.ndarray, ref: np.ndarray) -> dict:
    """Mean F1 minus the reference's over the same seeds, with a 95% bootstrap interval over
    seeds (ADR-0010 ruling 4). Seeds where either F1 is undefined are left out and counted."""
    ok = np.isfinite(f1) & np.isfinite(ref)
    d = (f1 - ref)[ok]
    if not d.size:
        return dict(mid=None, lo=None, hi=None, n_seeds=0, n_dropped=int((~ok).sum()))
    rng = np.random.RandomState(BOOTSTRAP_SEED)
    boot = d[rng.randint(0, d.size, size=(BOOTSTRAP, d.size))].mean(axis=1)
    return dict(mid=float(d.mean()), lo=float(np.percentile(boot, 2.5)),
                hi=float(np.percentile(boot, 97.5)), n_seeds=int(d.size),
                n_dropped=int((~ok).sum()))


def proposal(search: dict, det: str = "coact") -> tuple[str, dict, dict]:
    """``(name, params, held-out row)``: the search's best held-out candidate for ``det`` whose
    gain interval is above zero, else the shipped point."""
    ho = search["held_out"][det]
    best = ("shipped", ho["shipped"])
    for name, row in ho.items():
        g = row.get("gain_vs_shipped") or {}
        if name != "shipped" and g.get("lo") is not None and g["lo"] > 0 \
                and row["mean_f1"] > best[1]["mean_f1"]:
            best = (name, row)
    return best[0], dict(best[1]["params"]), best[1]


def the_one_root(roots, rel: str) -> Path | None:
    """The single root under which ``rel`` exists; None when none does. Two roots holding it is
    an error: which machine's run gets scored is not the scorer's to choose."""
    roots = [roots] if isinstance(roots, (str, Path)) else list(roots)
    hits = [Path(r) for r in roots if (Path(r) / rel).exists()]
    if len(hits) > 1:
        raise ValueError(f"{rel} is in more than one --phase2 root: {', '.join(map(str, hits))}")
    return hits[0] if hits else None


def load_search(phase2, pattern: str, bench: str, det: str) -> dict:
    """The search record that holds ``det`` on ``bench``: one folder per bench, or, when the
    pattern names ``{det}``, one folder per detector (a search run with ``--only``). ``phase2``
    is one root or several; the record must be under exactly one."""
    rel = f"{pattern.format(bench=bench, det=det)}/search.json"
    root = the_one_root(phase2, rel)
    if root is None:
        raise FileNotFoundError(f"no {rel} under {phase2}")
    return json.loads((root / rel).read_text(encoding="utf-8"))


def bracketing_of(search: dict, det: str, name: str) -> dict:
    """The search's bracketing verdict for one candidate. A search that predates the record
    (before 2026-09-25) cannot say, and is reported as unknown, never as bracketed."""
    br = (search.get("bracketing") or {}).get(det, {}).get(name)
    if br is None:
        return dict(bracketed=None, unbracketed_axes={}, note="not recorded by this search")
    return br


def adoptable_on_the_search(name: str, row: dict, br: dict) -> bool:
    """A proposal whose held-out gain interval is above zero AND which is bracketed. Budgets on
    fresh seeds are the morning report's to add; an unbracketed proposal is never adoptable."""
    g = row.get("gain_vs_shipped") or {}
    return (name != "shipped" and br.get("bracketed") is True
            and g.get("lo") is not None and g["lo"] > 0)


def train_rows(log: Path) -> list[dict]:
    """Every seed row the training tool printed. ``utf-8-sig``: a log redirected by Windows
    PowerShell opens with a byte-order mark, which hid the first row, seed 0, from every one of
    the full-panel night's 24 logs (2026-09-26). The log's own ``best:`` line must name a row
    read here, so a row lost some other way is an error rather than a silent gap."""
    rows, best = [], None
    for line in log.read_text(encoding="utf-8-sig").splitlines():
        line = line.strip()
        if line.startswith("{") and '"seed"' in line:
            rows.append(json.loads(line))
        elif line.startswith("best: "):
            best = line.split()[1]
    if best is not None and best not in {r["path"] for r in rows}:
        raise ValueError(f"{log}: its best seed {best} is not among the rows read")
    return rows


def picked(rows: list[dict], budget: float) -> dict | None:
    """The training rule's pick: the best held-out mean among seeds within the empty-recording
    budget. None when no seed is within it: that run is scored as a comparator, never picked."""
    ok = [r for r in rows if r["null_per_hour"] <= budget]
    return max(ok, key=lambda r: r["mean"]) if ok else None


CODED = ("coact", "loco", "sce", "rate", "sync", "cicada")


def b_under_floor(bench: str, r) -> dict:
    """ADR-0009 decision 2's counts for one pooled score."""
    return importlib.import_module(BENCHES[bench]).under_floor_report(r)


def _runner(kind: str, spec):
    if kind in CODED:
        def run(b, sl):
            return b.run_detector(kind, sl, **spec)
        return run
    path = Path(spec)
    if path not in _MODEL_CACHE:
        from bugarach.learn.checkpoint import load
        _MODEL_CACHE[path] = load(path)
    tr = _MODEL_CACHE[path]
    return lambda b, sl: tr.predict(sl)[0]


def job(args):
    bench, kind, name, spec, regime, seed = args
    from bugarach.score import score_stream
    b = importlib.import_module(BENCHES[bench])
    run = _runner(kind, spec)
    if regime == "null":
        sl, gt = b.make_null_recording(seed + b.NULL_SEED_OFFSET)
        det = run(b, sl)
        sc = score_stream(gt, det)
        return (bench, kind, name, regime, seed), dict(
            n_detected=sc.n_detected, hours=gt.params["duration_sec"] / 3600.0)
    if regime.startswith("elevated:"):
        # ADR-0009's elevated-rate recording; the maker adds ELEVATED_SEED_OFFSET itself.
        sl, gt = b.make_elevated_rate_recording(regime.split(":", 1)[1], seed)
        sc = score_stream(gt, run(b, sl))
        h0, h1 = gt.params["hot_window"]
        return (bench, kind, name, regime, seed), dict(
            calls_in=sc.hot_fa, calls_out=sc.n_detected - sc.hot_fa, minutes_in=(h1 - h0) / 60.0,
            hours_out=(gt.params["duration_sec"] - (h1 - h0)) / 3600.0)
    sl, gt = b.make_recording(regime, seed)
    sc = score_stream(gt, run(b, sl))
    return (bench, kind, name, regime, seed), sc


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--phase2", type=Path, required=True, action="append",
                    help="a folder holding searches and training (train-<model>-<bench>.log, "
                         "models-<bench>/); repeat to read several, each in place")
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--workers", type=int, default=16)
    ap.add_argument("--detectors", nargs="+", default=["coact"], choices=CODED,
                    help="coded detectors to score, shipped and proposal (default coact)")
    ap.add_argument("--search", default="search-coact-{bench}",
                    help="each bench's search folder under --phase2, {bench} filled in; with {det} "
                         "in it, one search per detector (search_all_settings.py --only)")
    ap.add_argument("--benches", nargs="+", default=list(BENCHES), choices=list(BENCHES),
                    help="which benches to score (default all three)")
    ap.add_argument("--spacing", choices=("bench", "realistic", "orx"), default="bench",
                    help="how the bench spaces its planted events (bench.SPACINGS; default "
                         "'bench', unchanged). Under 'realistic' and 'orx' fast's fresh and null "
                         "seeds are doubled (ADR-0010 ruling 2)")
    a = ap.parse_args(argv)
    a.out.mkdir(parents=True, exist_ok=True)

    from bugarach import bench as _b
    from bugarach.bench import pool_scores

    _b.use_spacing(a.spacing)            # before the pool: every worker plants at this spacing
    S = {bn: seeds_for(bn) for bn in a.benches}
    N = {bn: nulls_for(bn) for bn in a.benches}

    cands, meta = [], {}
    for bench in a.benches:
        b = importlib.import_module(BENCHES[bench])
        budget = float(b.MAX_FALSE_POSITIVES_PER_HOUR["coact"])
        meta[bench] = dict(budget_null_per_hour=budget, search_elapsed_min={}, chorus={},
                           detectors={})
        for det in a.detectors:
            search = load_search(a.phase2, a.search, bench, det)
            meta[bench]["search_elapsed_min"][det] = search.get("elapsed_min")
            pname, pparams, prow = proposal(search, det)
            shipped = dict(b.OPERATING_POINTS[det].params)
            br = bracketing_of(search, det, pname)
            meta[bench]["detectors"][det] = dict(
                shipped=shipped, proposal=dict(name=pname, params=pparams, search_row=prow,
                                               bracketing=br,
                                               unbracketed=br.get("bracketed") is not True
                                               and pname != "shipped",
                                               adoptable=adoptable_on_the_search(pname, prow, br)),
                budget_null_per_hour=float(b.MAX_FALSE_POSITIVES_PER_HOUR[det]),
                search_floor=search.get("floor", "pre-ADR-0008 (not recorded by the search)"))
            if det == "coact":      # the keys detect_with_floors.py reads
                meta[bench]["coact_shipped"] = shipped
                meta[bench]["coact_proposal"] = dict(name=pname, params=pparams,
                                                     search_row=prow)
            cands.append((bench, det, "shipped", shipped))
            if pname != "shipped":
                cands.append((bench, det, "proposal", pparams))
        for m in MODELS:
            root = the_one_root(a.phase2, f"train-{m}-{bench}.log")
            if root is None:
                continue
            rows = train_rows(root / f"train-{m}-{bench}.log")
            pick = picked(rows, budget)
            best = max(rows, key=lambda r: r["mean"]) if rows else None
            meta[bench]["chorus"][m] = dict(
                train_rows=rows, models_root=str(root), picked=pick["path"] if pick else None,
                out_of_budget=None if pick or not best else dict(
                    best=best["path"], note="no seed within the empty-recording budget; scored "
                                            "as a comparator, never a pick"))
            for r in rows:
                cands.append((bench, "chorus", r["path"],
                              str(root / f"models-{bench}" / r["path"])))

    jobs = [(bench, kind, name, spec, reg, s) for bench, kind, name, spec in cands
            for reg in REG for s in S[bench]]
    jobs += [(bench, kind, name, spec, "null", s) for bench, kind, name, spec in cands
             for s in N[bench]]
    jobs += [(bench, kind, name, spec, f"elevated:{reg}", s) for bench, kind, name, spec in cands
             for reg in REG for s in N[bench]]
    with mp.Pool(a.workers) as pool:
        got = dict(pool.map(job, jobs, chunksize=4))

    results = {}
    for bench, kind, name, spec in cands:
        row = {}
        one_call = 0
        SEEDS, NULLS = S[bench], N[bench]
        for reg in REG:
            scores = [got[(bench, kind, name, reg, s)] for s in SEEDS]
            one_call += sum(sc.n_detected == 1 for sc in scores)
            r = pool_scores(scores, detector=kind, regime=reg, seeds=SEEDS)
            el = [got[(bench, kind, name, f"elevated:{reg}", s)] for s in NULLS]
            row[reg] = dict(f1=r.f1, f1_without_decoys=r.f1_without_decoys, recall=r.recall,
                            precision=r.precision,
                            precision_without_decoys=r.precision_without_decoys,
                            decoy_calls=r.decoy_calls, n_planted=r.n_planted, n_hit=r.n_hit,
                            merged_calls=r.n_merged_calls,
                            n_detected=r.n_detected,
                            probe_calls_per_min=(sum(e["calls_in"] for e in el)
                                                 / sum(e["minutes_in"] for e in el)),
                            elevated_calls_per_hour_outside=(sum(e["calls_out"] for e in el)
                                                             / sum(e["hours_out"] for e in el)),
                            recall_by_participation={f"{f:g}": r.recall_at(f)
                                                     for f in sorted(r.by_frac)},
                            under_floor=b_under_floor(bench, r))
        nulls = [got[(bench, kind, name, "null", s)] for s in NULLS]
        row["null_calls_per_hour"] = (sum(n["n_detected"] for n in nulls)
                                      / sum(n["hours"] for n in nulls))
        row["mean_f1"] = float(np.mean([row[r]["f1"] for r in REG]))
        row["mean_f1_without_decoys"] = float(np.mean([row[r]["f1_without_decoys"] for r in REG]))
        row["recordings_with_one_call"] = int(one_call)
        row["collapsed"] = bool(one_call == len(REG) * len(SEEDS))
        results.setdefault(bench, {})[f"{kind}:{name}"] = row
        print(f"{bench:8s} {kind:6s} {name:34s} F1 {row['mean_f1']:.3f} "
              f"(without decoys {row['mean_f1_without_decoys']:.3f}), "
              f"{row['null_calls_per_hour']:.2f} calls/h on the empty recording"
              + ("  COLLAPSED" if row["collapsed"] else ""), flush=True)
    # Ruling 4 (ADR-0010): every candidate's fresh-seed F1 as a PAIRED difference from
    # CoactDetect on the same recordings, with a 95% bootstrap interval over seeds.
    for bench in a.benches:
        for ref in ("coact:shipped", "coact:proposal"):
            if f"{ref}" not in results.get(bench, {}):
                continue
            rk, rn = ref.split(":", 1)
            ref_f1 = per_seed_f1(got, pool_scores, bench, rk, rn, S[bench])
            for key, row in results[bench].items():
                kind, name = key.split(":", 1)
                row.setdefault("paired_f1_vs_coact", {})[rn] = paired_difference(
                    per_seed_f1(got, pool_scores, bench, kind, name, S[bench]), ref_f1)
    from bugarach.bench import ELEVATED_SEED_OFFSET, FLOOR_LABEL, NULL_SEED_OFFSET
    # The single-range keys stay for readers written before per-bench seeds: the first bench's.
    SEEDS, NULLS = S[a.benches[0]], N[a.benches[0]]
    rec = dict(spacing=_b.spacing(),
               seeds_by_bench={bn: [S[bn][0], S[bn][-1]] for bn in a.benches},
               null_seeds_by_bench={bn: [N[bn][0] + NULL_SEED_OFFSET, N[bn][-1] + NULL_SEED_OFFSET]
                                    for bn in a.benches},
               elevated_rate_seeds_by_bench={bn: [N[bn][0] + ELEVATED_SEED_OFFSET,
                                                  N[bn][-1] + ELEVATED_SEED_OFFSET]
                                             for bn in a.benches},
               seeds=[SEEDS[0], SEEDS[-1]],
               null_seeds=[NULLS[0] + NULL_SEED_OFFSET, NULLS[-1] + NULL_SEED_OFFSET],
               elevated_rate_seeds=[NULLS[0] + ELEVATED_SEED_OFFSET,
                                    NULLS[-1] + ELEVATED_SEED_OFFSET],
               benches=meta, results=results, floor=FLOOR_LABEL,
               note="coded detectors run at each recording's ADR-0008 floor (min_rois, and "
                    "SPIKE-synch's min_n); planted events under it are don't-care in every "
                    "score (ADR-0009 decision 2), counted in under_floor. chorus has no "
                    "participation parameter and is scored under the same rule.")
    (a.out / "candidates.json").write_text(json.dumps(rec, indent=1, default=float) + "\n")
    print(f"wrote {a.out / 'candidates.json'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
