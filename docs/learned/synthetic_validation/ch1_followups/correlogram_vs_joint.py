"""Task 1 (murderboard 2026-10-29, role 7, blocking): the repository's bin-free jitter estimator,
tools/measure_jitter_correlogram.py, beside Aim 0's joint fit, on the same 240 Aim 1a recordings.

Recordings. Regenerated with exactly aim1_one_source.py's call to `simulate_coordination`
(its constants N_ROI, DURATION, MIN_SEP, grid 0.1 s, and its seed 1000 + 100 * idx + seed, idx
the condition's index in its grid order); onsets go to frames with `mcr._frames` as there. Each
regenerated recording's onset count is checked against the run record's `n_onsets`.

Correlogram estimator, as shipped. Per recording: the tool's `pairs` (cross-cell onset pairs per
0.1 s lag, over the expected count) and `hwhm` (half-width at half height of the peak, after
subtracting the 5-10 s shoulder). Width to sigma through the tool's own calibration: its `_sim`
on its fast bench (`bugarach.bench`, regimes baseline_quiet and baseline_busy, seeds 1-24, its
JITTERS grid 0.05-1.0 s), pooled per planted jitter, monotone-checked and linearly interpolated,
NaN off the curve, exactly as `main()` does. That calibration was made on the bench, not on this
generator: the bench's participation, event rate, background structure (silent and hot cells,
distractors, an elevated-rate stretch) differ from Aim 1a's flat field. It is used as shipped.
Also printed: (a) the same width read through the Gaussian relation with no calibration,
sigma = HWHM / (sqrt 2 * sqrt(2 ln 2)) (the pair lag is N(0, 2 sigma^2)); (b) a per-condition
POOLED width (pairs summed over the condition's 5 recordings, as the tool pools recordings).

Joint fit. `theory.fit_joint` on each recording's stored excess cumulants (hard-core form), as
theory.check() runs it.

    PYTHONPATH=src python docs/learned/synthetic_validation/ch1_followups/correlogram_vs_joint.py --workers 40
"""
from __future__ import annotations

import argparse
import itertools
import json
import sys
import time
from collections import defaultdict
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
SV = HERE.parent
ROOT = SV.parents[2]
for p in (SV, ROOT / "tools", ROOT / "src"):
    sys.path.insert(0, str(p))
import aim1_one_source as a1  # noqa: E402
import measure_jitter_correlogram as mjc  # noqa: E402

GAUSS = np.sqrt(2.0) * np.sqrt(2.0 * np.log(2.0))   # HWHM of N(0, 2 sigma^2) over sigma


def regen(args):
    """One Aim 1a recording, regenerated through aim1_one_source's own seed path; its pairs."""
    idx, (jit, part, n_ev, bg, seed) = args
    from bugarach.simulate import simulate_coordination
    import measure_coordination_rates as mcr
    s, gt = simulate_coordination(
        duration_sec=a1.DURATION, n_roi=a1.N_ROI, bg_rate_hz=bg, participation=(part,),
        n_per_level=(n_ev,), jitter_sec=jit, min_sep_sec=a1.MIN_SEP, grid_sec=0.1,
        seed=1000 + 100 * idx + seed)
    st = next(iter(s.streams.values()))
    L = int(round(a1.DURATION / mcr.DT))
    trains = [np.minimum(mcr._frames(np.asarray(t), 0.0, a1.DURATION), L - 1) for t in st.t50rise]
    o, e = mjc.pairs(trains, L)
    return dict(cell=idx, seed=seed, n_onsets=int(sum(len(t) for t in trains)), obs=o, exp=e)


def joint(args):
    import theory
    cum, n = args
    return theory.fit_joint(cum, n)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--workers", type=int, default=40)
    a = ap.parse_args()
    rec = json.loads((SV / "aim1_one_source.json").read_text())
    cells = list(itertools.product(a1.JITTERS, a1.PARTS, a1.N_EVENTS, a1.BG_RATES))
    grid = [(i, (*c, s)) for i, c in enumerate(cells) for s in a1.SEEDS]
    by_key = {(r["cell"], r["seed"]): r for r in rec["rows"]}
    t0 = time.time()
    with ProcessPoolExecutor(a.workers) as ex:
        sims = list(ex.map(regen, grid))
        cal_jobs = [("bugarach.bench", reg, s, j) for j in mjc.JITTERS
                    for reg in ("baseline_quiet", "baseline_busy") for s in mjc.SIM_SEEDS]
        cal_res = list(ex.map(mjc._sim, cal_jobs, chunksize=4))
        rows = [by_key[(x["cell"], x["seed"])] for x in sims]
        fits = list(ex.map(joint, [(r["cum"], rec["n_roi"]) for r in rows]))
    print(f"regenerated {len(sims)} recordings, {len(cal_res)} calibration recordings, "
          f"{len(fits)} joint fits in {time.time() - t0:.0f} s", file=sys.stderr)

    mismatch = sum(x["n_onsets"] != r["true"]["n_onsets"] for x, r in zip(sims, rows))
    print(f"regeneration check: onset count differs from the run record in {mismatch} of "
          f"{len(sims)} recordings")

    per_j = len(cal_res) // len(mjc.JITTERS)
    cal = {j: mjc.pooled(cal_res[i * per_j:(i + 1) * per_j]) for i, j in enumerate(mjc.JITTERS)}
    ws = np.array([mjc.hwhm(*cal[j]) for j in mjc.JITTERS])
    monotone = bool(np.all(np.diff(ws) > 0))

    def to_sigma(w):
        return float(np.interp(w, ws, mjc.JITTERS, left=np.nan, right=np.nan)) if monotone else np.nan

    import bugarach.bench as bench
    print(f"shipped calibration (tool's _sim on bugarach.bench, bench jitter now "
          f"{bench.BENCH_RECORDING['jitter_sec']} s; 48 recordings per jitter): hwhm "
          + ", ".join(f"{j:g}->{w:.3f}" for j, w in zip(mjc.JITTERS, ws))
          + ("" if monotone else " NOT MONOTONE"))

    per = []
    for x, r, f in zip(sims, rows, fits):
        t = r["true"]
        w = mjc.hwhm(x["obs"], x["exp"])
        per.append(dict(cell=x["cell"], seed=x["seed"], bg=t["bg_rate"], sigma=t["jitter"],
                        k=int(round(t["k"])), n_events=t["n_events"], hwhm=w,
                        corr_sigma=to_sigma(w) if np.isfinite(w) else np.nan,
                        gauss_sigma=w / GAUSS if np.isfinite(w) else np.nan,
                        joint_sigma=f["sigma"] if f else np.nan,
                        joint_at_bound=bool(f["at_bound"]) if f else None))
    # per-condition pooled width (pairs summed over the condition's 5 recordings)
    pool = defaultdict(list)
    for x, p in zip(sims, per):
        pool[(p["bg"], p["sigma"], p["k"], p["n_events"])].append((x["obs"], x["exp"]))
    pooled = {}
    for key, v in pool.items():
        w = mjc.hwhm(*mjc.pooled(v))
        pooled[key] = dict(hwhm=w, corr_sigma=to_sigma(w) if np.isfinite(w) else np.nan)

    def q(v):
        v = np.asarray(v, float)
        f = v[np.isfinite(v)]
        if not f.size:
            return "      -            "
        a, b, c = np.percentile(f, [25, 50, 75])
        return f"{b:5.2f} [{a:4.2f},{c:4.2f}]"

    print("\nrecovered / planted jitter per recording: median [IQR]; n off = recordings with no "
          "estimate (correlogram: no peak or off the calibration curve; joint fit: unusable), "
          "b = joint fit at its sigma bound")
    print(f"  {'bg':>5} {'sigma':>5} {'cells':>6} {'n':>3} | {'correlogram (shipped cal.)':>26} "
          f"{'off':>3} | {'correlogram, Gaussian':>21} | {'joint fit':>18} {'off':>3} {'b':>2} "
          f"| pooled-condition correlogram, median [range]")
    summary = []
    for bg in a1.BG_RATES:
        for s in a1.JITTERS:
            for lab, sel in (("10+", lambda p: p["k"] >= 10), ("5", lambda p: p["k"] == 5)):
                ps = [p for p in per if p["bg"] == bg and p["sigma"] == s and sel(p)]
                cr = [p["corr_sigma"] / s for p in ps]
                gr = [p["gauss_sigma"] / s for p in ps]
                jr = [p["joint_sigma"] / s for p in ps]
                pc = [pooled[(bg, s, k, ne)]["corr_sigma"] / s for (bg_, s_, k, ne) in pooled
                      if bg_ == bg and s_ == s and sel(dict(k=k))]
                pcf = [v for v in pc if np.isfinite(v)]
                off_c = int(np.sum(~np.isfinite(cr)))
                off_j = int(np.sum(~np.isfinite(jr)))
                nb = sum(bool(p["joint_at_bound"]) for p in ps)
                print(f"  {bg:>5} {s:>5} {lab:>6} {len(ps):>3} | {q(cr):>26} {off_c:>3} | "
                      f"{q(gr):>21} | {q(jr):>18} {off_j:>3} {nb:>2} | "
                      + (f"{np.median(pcf):.2f} [{min(pcf):.2f}-{max(pcf):.2f}] "
                         f"({len(pc) - len(pcf)} of {len(pc)} off)" if pcf else
                         f"- ({len(pc)} of {len(pc)} off)"))

                def qs(v):
                    v = np.asarray(v, float); v = v[np.isfinite(v)]
                    return [float(x) for x in np.percentile(v, [25, 50, 75])] if v.size else None
                summary.append(dict(bg=bg, sigma=s, cells=lab, n=len(ps),
                                    correlogram_ratio_q=qs(cr), correlogram_off=off_c,
                                    gaussian_ratio_q=qs(gr), joint_ratio_q=qs(jr),
                                    joint_unusable=off_j, joint_at_bound=nb,
                                    pooled_condition_correlogram_ratio=[None if not np.isfinite(v)
                                                                        else float(v) for v in pc]))
    out = dict(what="correlogram (tools/measure_jitter_correlogram.py, shipped calibration) vs "
                    "theory.fit_joint on the 240 Aim 1a recordings",
               regeneration_mismatches=mismatch,
               calibration=dict(bench="bugarach.bench", regimes=["baseline_quiet", "baseline_busy"],
                                seeds=[mjc.SIM_SEEDS[0], mjc.SIM_SEEDS[-1]],
                                jitters=list(mjc.JITTERS), hwhm=ws.tolist(), monotone=monotone,
                                bench_jitter_sec=bench.BENCH_RECORDING["jitter_sec"]),
               summary=summary,
               per_recording=[{k: (None if isinstance(v, float) and not np.isfinite(v) else v)
                               for k, v in p.items()} for p in per])
    (HERE / "correlogram_vs_joint.json").write_text(json.dumps(out, indent=1, default=float))


if __name__ == "__main__":
    main()
