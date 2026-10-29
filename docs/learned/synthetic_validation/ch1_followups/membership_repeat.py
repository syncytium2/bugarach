"""Round 3, tasks 4 and 8 (blind review roles 4, 6, 7): the assembly test conditional on a
repeated assembly, and which statistic carries each rejection at the shipped surrogate count.

membership_limit.py's model (N = 33 cells, k = 10 per event, E = 45 events, M random k-sets, each
event picking one uniformly; perfect readout), its `sets_for` logic re-drawn here so that the
assembly index of every event is kept. A recording "has a repeat" when some assembly is picked by
two or more of its 45 events (birthday probability 1 - prod_{i<E} (1 - i/M)).

Tests: the shipped bugarach.assembly pvalues_margin / pvalues_uniform (each returns the
dispersion and leading-eigenvalue p-values) and AssemblyResult.verdict (Bonferroni over the two
statistics, alpha/2 each). "Both-null rejection" = verdict "structure-beyond-rate".

Task 4: M = 1000 (reuse E/M = 0.045), 1000 recordings, 200 surrogates per null (as
membership_limit.py) AND the shipped default 1000 (assess_assemblies' n_surrogates), on the same
membership matrices. Rejection conditional on >= 1 repeat and on 0 repeats, Wilson 95 % CIs.
Task 8: M = 1000, 150, 45 (reuse 0.045, 0.3, 1) and random participation (size), 1000
surrogates: per null, how often the dispersion statistic, the eigenvalue statistic, or both are
below alpha/2. M = 150, 45 and random: 400 recordings each.

Seeds 3_000_000 + 100_000 arm + i (membership), RandomState(same + 50_000_000 x surrogate tag).

    PYTHONPATH=src python docs/learned/synthetic_validation/ch1_followups/membership_repeat.py --workers 40
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
SV = HERE.parent
sys.path.insert(0, str(SV))
import membership_limit as ml  # noqa: E402

N, K, E, ALPHA = ml.N, ml.k, ml.E, ml.ALPHA
ARMS = {"M1000": (1000, 1000), "M150": (150, 400), "M45": (45, 400), "random": (None, 400)}


def job(args):
    from bugarach.assembly import AssemblyResult, membership_matrix, pvalues_margin, pvalues_uniform
    arm, ai, i, surrs = args
    M = ARMS[arm][0]
    seed = 3_000_000 + 100_000 * ai + i
    rng = np.random.default_rng(seed)
    if M is None:
        sets, idx = [rng.choice(N, K, replace=False) for _ in range(E)], np.arange(E)
    else:
        A = [rng.choice(N, K, replace=False) for _ in range(M)]
        idx = rng.integers(0, M, E)
        sets = [A[j] for j in idx]
    _, cnt = np.unique(idx, return_counts=True)
    X = membership_matrix(sets, N)
    out = dict(arm=arm, i=i, repeats=int(E - cnt.size), max_mult=int(cnt.max()), tests={})
    for ns in surrs:
        rs = np.random.RandomState(seed + 50_000_000 * (1 if ns == 200 else 2))
        md, me = pvalues_margin(rs, X, ns)
        ud, ue = pvalues_uniform(rs, X, ns)
        r = AssemblyResult(min_rois=K, n_events=E, n_roi=N, defined=True, p_margin_disp=md,
                           p_margin_eig=me, p_uniform_disp=ud, p_uniform_eig=ue)
        out["tests"][str(ns)] = dict(md=md, me=me, ud=ud, ue=ue, verdict=r.verdict(ALPHA))
    return out


def wilson(x, n, z=1.96):
    if n == 0:
        return [float("nan")] * 3
    p = x / n
    c = (p + z * z / (2 * n)) / (1 + z * z / n)
    h = z * np.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / (1 + z * z / n)
    return [p, c - h, c + h]


def fmt(w):
    return f"{w[0]:.3f} [{w[1]:.3f}, {w[2]:.3f}]"


if __name__ == "__main__":
    from bugarach.assembly import assess_assemblies
    import inspect
    shipped = inspect.signature(assess_assemblies).parameters["n_surrogates"].default
    ap = argparse.ArgumentParser()
    ap.add_argument("--workers", type=int, default=40)
    a = ap.parse_args()
    jobs = []
    for ai, (arm, (M, n)) in enumerate(ARMS.items()):
        surrs = (200, 1000) if arm == "M1000" else (1000,)
        jobs += [(arm, ai, i, surrs) for i in range(n)]
    t0 = time.time()
    with ProcessPoolExecutor(a.workers) as ex:
        rows = list(ex.map(job, jobs, chunksize=4))
    rt = time.time() - t0
    print(f"{rt:.0f} s", file=sys.stderr)
    rec = dict(N=N, k=K, E=E, alpha=ALPHA, shipped_n_surrogates=shipped, arms={k: list(v) for k, v in ARMS.items()},
               rows=rows, runtime_sec=rt, summary={})
    print(f"{N} cells, {K} per event, {E} events; verdict at alpha {ALPHA} (alpha/2 per statistic); "
          f"assess_assemblies' default n_surrogates = {shipped}")
    m = [r for r in rows if r["arm"] == "M1000"]
    rep = [r for r in m if r["repeats"] > 0]
    nrep = [r for r in m if r["repeats"] == 0]
    birthday = 1 - np.prod(1 - np.arange(E) / 1000)
    print(f"\nTask 4: M = 1000 (reuse {E / 1000:.3f}), {len(m)} recordings")
    print(f"  share with >= 1 repeated assembly: {fmt(wilson(len(rep), len(m)))} (birthday "
          f"{birthday:.3f}); repeats per recording: " +
          ", ".join(f"{v}: {sum(r['repeats'] == v for r in m)}" for v in range(0, 5)) + ", 5+: " +
          str(sum(r["repeats"] >= 5 for r in m)))
    s4 = dict(share_repeat=wilson(len(rep), len(m)), birthday=birthday)
    for ns in ("200", "1000"):
        for lab, grp in (("all", m), (">= 1 repeat", rep), ("0 repeats", nrep), ("exactly 1 repeat",
                         [r for r in m if r["repeats"] == 1]), (">= 2 repeats", [r for r in m if r["repeats"] >= 2])):
            both = sum(r["tests"][ns]["verdict"] == "structure-beyond-rate" for r in grp)
            anyf = sum(r["tests"][ns]["verdict"] != "no-assembly" for r in grp)
            s4[f"{ns},{lab}"] = dict(n=len(grp), both=wilson(both, len(grp)), any=wilson(anyf, len(grp)))
            print(f"  {ns:>4} surrogates, {lab:16s} (n {len(grp):4d}): both-null rejection {fmt(wilson(both, len(grp)))}"
                  f" | any flag {fmt(wilson(anyf, len(grp)))}")
    rec["summary"]["task4"] = s4
    print(f"\nTask 8: which statistic rejects (p < alpha/2 = {ALPHA / 2}), {shipped} surrogates; "
          "shares of recordings")
    print("  arm (reuse)      n | margin: disp only / eig only / both / either | uniform: disp only / "
          "eig only / both / either | verdicts")
    for arm, (M, n) in ARMS.items():
        g = [r["tests"]["1000"] for r in rows if r["arm"] == arm]
        a2 = ALPHA / 2
        line, sm = f"  {arm:7s} ({'-' if M is None else f'{E / M:.3f}'}) {len(g):4d} |", {}
        for null, (dk, ek) in (("margin", ("md", "me")), ("uniform", ("ud", "ue"))):
            d = np.array([t[dk] < a2 for t in g])
            e = np.array([t[ek] < a2 for t in g])
            v = dict(disp_only=float(np.mean(d & ~e)), eig_only=float(np.mean(e & ~d)),
                     both=float(np.mean(d & e)), either=float(np.mean(d | e)))
            sm[null] = v
            line += f" {v['disp_only']:.3f} / {v['eig_only']:.3f} / {v['both']:.3f} / {v['either']:.3f} |"
        words = ("no-assembly", "uniform-only", "margin-only", "structure-beyond-rate")
        sm["verdicts"] = {w: sum(t["verdict"] == w for t in g) for w in words}
        rec["summary"][f"task8,{arm}"] = sm
        print(line + " " + str(sm["verdicts"]))
    (HERE / "membership_repeat.json").write_text(json.dumps(rec, indent=1, default=float))
