"""Round 3, task 1 (blind review role 4, blocking): the joint fit and the coordination-rates tool
at a realistic recording window (20 min) with the event count fixed per recording.

Parameter values only. windows.csv (runs/2026-09-25-real-intervals) is read for two numbers per
stream, the baseline window duration and the event-count quantiles, and nothing else: no onset of
any recording is analysed. The simulated recordings then use:

  T = 1200 s (20 min), margin 5 s; 33 cells; b = 0.0096 Hz; 0.1 s frame; sigma 0.105 s (fast list)
  / 0.131 s (slow list); k = 7 and 13 cells per event; E = 1, 2, 4, 8, 16 events, FIXED per
  recording; 40 recordings per (stream, k, E).

The train. As realistic_counts.py: a stationary renewal train of resampled gaps (4000 s run-in),
independently thinned with probability p_E = min(1, E / (lam_list (T - 2 margin))), so that E
is the expected count, then CONDITIONED on exactly E events by rejection (redraw until the count
is E). On the fast list E = 16 exceeds the list's own 11.8 per window, so there p = 1 (no
thinning) and the conditioning does all the work. The "true" train the general form is given is
realistic_counts.thinned_train(gaps, p_E) with the fixed-count term at n_events = E. Conditioning
on the count beyond the fixed-count term is not modelled; that is a stated approximation.

Fits per recording: the general form given that train ("true") and the 20 s hard core in
theory.py's form ("page", train=None), both theory.fit_joint. The coordination-rates tool:
solve() on that recording's own (f2, f3) at each window (1, 2, 4 s), with refusals (f2 <= 0 or
f3 <= 0) counted.

Seeds: generator 5_800_000 + s, train 5_700_000 + s, thinning 5_600_000 + s, surrogates
5_900_000 + s, s = 100000 (fast 0 / slow 1) + 1000 k + 50 E + i: disjoint from rounds 1-2.

    PYTHONPATH=src python docs/learned/synthetic_validation/ch1_followups/window_counts.py --workers 44
"""
from __future__ import annotations

import argparse
import csv
import json
import sys
import time
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
SV = HERE.parent
sys.path.insert(0, str(SV))
sys.path.insert(0, str(HERE))
import theory  # noqa: E402
from realistic_counts import thinned_train, q3  # noqa: E402

WINDOWS_CSV = SV.parents[0] / "runs" / "2026-09-25-real-intervals" / "windows.csv"
STREAMS = {"fast": dict(sigma=0.105, idx=0), "slow": dict(sigma=0.131, idx=1)}
T, MARGIN, N_CELLS, BG = 1200.0, 5.0, 33, 0.0096
KS, ES, N_REC = (7, 13), (1, 2, 4, 8, 16), 40
FORMS = ("true", "page")


def window_parameters():
    """Window duration and event-count quantiles per stream, as parameter values."""
    rows = list(csv.DictReader(open(WINDOWS_CSV, newline="")))
    out = {}
    for s in ("fast", "slow", "combined"):
        v = [r for r in rows if r["stream"] == s]
        n = np.array([int(r["n_events"]) for r in v])
        h = np.array([float(r["hours"]) for r in v])
        out[s] = dict(n_windows=len(v), hours_min=float(h.min()), hours_median=float(np.median(h)),
                      hours_max=float(h.max()), count_mean=float(n.mean()),
                      count_q=dict(zip(("0", "10", "25", "50", "75", "90", "100"),
                                       [float(x) for x in np.percentile(n, [0, 10, 25, 50, 75, 90, 100])])),
                      zero_windows=int(np.sum(n == 0)), per_hour=float(n.sum() / h.sum()))
    return out


def seed_of(stream, k, E, i):
    return 100000 * STREAMS[stream]["idx"] + 1000 * k + 50 * E + i


def draw_times(gaps, p, E, seed):
    lo, hi = MARGIN, T - MARGIN
    rng_t = np.random.RandomState(5_700_000 + seed)
    rng_k = np.random.RandomState(5_600_000 + seed)
    tries = 0
    while True:
        tries += 1
        t, times = lo - 4000.0, []
        while t < hi:
            t += gaps[rng_t.randint(0, gaps.size)]
            if lo <= t < hi:
                times.append(t)
        times = np.array(times)
        times = times[rng_k.random_sample(times.size) < p]
        if times.size == E:
            return times, tries


def recording(args):
    stream, k, E, i, gaps, p = args
    import measure_coordination_rates as mcr
    from bugarach import simulate as sim
    seed = seed_of(stream, k, E, i)
    times, tries = draw_times(gaps, p, E, seed)
    orig = sim._place_renewal
    sim._place_renewal = lambda rng, m, lo_, hi_, ms, ex, cv: times.copy()  # noqa: E731
    try:
        s, gt = sim.simulate_coordination(
            duration_sec=T, n_roi=N_CELLS, bg_rate_hz=BG, participation=(k / N_CELLS,),
            n_per_level=(times.size,), jitter_sec=STREAMS[stream]["sigma"], min_sep_sec=0.0,
            grid_sec=0.1, margin_sec=MARGIN, seed=5_800_000 + seed)
    finally:
        sim._place_renewal = orig
    st = next(iter(s.streams.values()))
    L = int(round(T / mcr.DT))
    trains = [np.minimum(mcr._frames(np.asarray(tr), 0.0, T), L - 1) for tr in st.t50rise]
    m = mcr.measure(trains, L, np.random.RandomState(5_900_000 + seed))
    cum = {w: dict(f2=float(v["f2"]), f3=float(v["f3"])) for w, v in m["cum"].items()}
    tool = {w: mcr.solve(c["f2"], c["f3"], N_CELLS, float(w), "fixed") for w, c in cum.items()}
    return dict(stream=stream, k=k, E=E, i=i, seed=seed, tries=tries,
                n_events=len(gt.events), true=mcr.truth(gt, N_CELLS, T), cum=cum, tool=tool)


def fit_block(args):
    stream, k, E, form, gaps, p, cums = args
    tr = thinned_train(gaps, p, f"{stream} gaps") if form == "true" else None
    ne = float(E) if form == "true" else None
    out = []
    for cum in cums:
        f = theory.fit_joint(cum, N_CELLS, train=tr, n_events=ne)
        out.append(None if f is None else dict(sigma=f["sigma"], k=f["k"], lam=f["lam"]))
    return stream, k, E, form, out


def band(v):
    return int(sum(0.8 <= x <= 1.25 for x in v if np.isfinite(x)))


def summarize(res):
    print("windows.csv, parameter values only (window duration, events per window):")
    for s, w in res["window_parameters"].items():
        q = w["count_q"]
        print(f"  {s:8s}: {w['n_windows']} windows, {60 * w['hours_min']:.0f}-{60 * w['hours_max']:.0f} min "
              f"(median {60 * w['hours_median']:.0f}); events mean {w['count_mean']:.2f}, quantiles "
              f"0/10/25/50/75/90/100 % = {q['0']:.0f}/{q['10']:.0f}/{q['25']:.0f}/{q['50']:.1f}/"
              f"{q['75']:.2f}/{q['90']:.1f}/{q['100']:.0f}; zero-event windows {w['zero_windows']}; "
              f"{w['per_hour']:.2f} per hour")
    print(f"\nsimulated: T {T:.0f} s, {N_CELLS} cells, b {BG} Hz, 0.1 s frame, {N_REC} recordings "
          "per (stream, k, E), E fixed. Ratios fitted / planted, median [IQR]; 'lo' = sigma at the "
          "0.005 s floor (within 2 %), 'hi' = at 5 s; band = within 0.8-1.25; rate is against each "
          "recording's own planted rate; 'none' = fit returned no answer (f2 <= 0 at every window)")
    summ = []
    for stream in STREAMS:
        s = STREAMS[stream]["sigma"]
        for k in KS:
            for E in ES:
                rs = [r for r in res["rows"] if r["stream"] == stream and r["k"] == k and r["E"] == E]
                rs.sort(key=lambda r: r["i"])
                p = res["p_thin"][stream][str(E)]
                line = dict(stream=stream, k=k, E=E, p_thin=p,
                            mean_tries=float(np.mean([r["tries"] for r in rs])))
                for form in FORMS:
                    fs = res["fits"][f"{stream},{k},{E},{form}"]
                    ok = [(f, r) for f, r in zip(fs, rs) if f is not None]
                    sr = [f["sigma"] / s for f, _ in ok]
                    kr = [f["k"] / k for f, _ in ok]
                    lr = [f["lam"] / r["true"]["lam"] for f, r in ok]
                    line[form] = dict(
                        n_fit=len(ok), sigma_q=q3(sr), k_q=q3(kr), lam_q=q3(lr),
                        sigma_lo=int(sum(f["sigma"] <= 0.005 * 1.02 for f, _ in ok)),
                        sigma_hi=int(sum(f["sigma"] >= 5.0 / 1.02 for f, _ in ok)),
                        k_bound=int(sum(f["k"] <= 2.001 * 1.02 or f["k"] >= N_CELLS / 1.02 for f, _ in ok)),
                        lam_bound=int(sum(f["lam"] <= 1e-6 * 1.02 or f["lam"] >= 1 / 1.02 for f, _ in ok)),
                        sigma_band=band(sr), k_band=band(kr), lam_band=band(lr))
                line["tool"] = {}
                for w in ("1.0", "2.0", "4.0"):
                    pk = np.array([r["tool"][w]["k"] / k for r in rs])
                    pl = np.array([r["tool"][w]["lam"] / r["true"]["lam"] for r in rs])
                    fin = np.isfinite(pk)
                    line["tool"][w] = dict(refused=int(np.sum(~fin)), k_q=q3(pk), lam_q=q3(pl),
                                           k_band=band(pk), lam_band=band(pl),
                                           k_per_recording=[float(x) for x in pk])
                summ.append(line)
    print("\njoint fit (true = general form given the thinned train, fixed count E; page = 20 s "
          "hard core, theory.py's form)")
    print("  stream  k   E form | sigma median [IQR] (lo, hi; band) | participants (band) | rate (band) | none")
    for a in summ:
        for form in FORMS:
            f = a[form]
            sq, kq, lq = f["sigma_q"], f["k_q"], f["lam_q"]
            print(f"  {a['stream']:5s} {a['k']:2d} {a['E']:3d} {form:4s} | {sq[1]:.2f} [{sq[0]:.2f}, "
                  f"{sq[2]:.2f}] ({f['sigma_lo']}, {f['sigma_hi']}; {f['sigma_band']}) | {kq[1]:.2f} "
                  f"[{kq[0]:.2f}, {kq[2]:.2f}] ({f['k_band']}) | {lq[1]:.2f} [{lq[0]:.2f}, {lq[2]:.2f}] "
                  f"({f['lam_band']}) | {N_REC - f['n_fit']}   k/lam at bound {f['k_bound']}/{f['lam_bound']}")
    print("\ncoordination-rates tool, solve() on each recording's own f2, f3: participants / planted "
          "median [IQR] (band of 40; refused = f2 or f3 not positive) | rate / planted median [IQR] (band)")
    for a in summ:
        for w, t in a["tool"].items():
            kq, lq = t["k_q"], t["lam_q"]
            print(f"  {a['stream']:5s} {a['k']:2d} {a['E']:3d} w {float(w):g} s | participants {kq[1]:.2f} "
                  f"[{kq[0]:.2f}, {kq[2]:.2f}] (band {t['k_band']}; refused {t['refused']}) | rate "
                  f"{lq[1]:.2f} [{lq[0]:.2f}, {lq[2]:.2f}] (band {t['lam_band']})")
    res["summary"] = summ


def run(ex):
    res = dict(T=T, margin=MARGIN, n_cells=N_CELLS, bg=BG, ks=KS, Es=ES, n_rec=N_REC,
               window_parameters=window_parameters(), p_thin={}, rows=[], fits={})
    jobs, gl = [], {}
    for stream in STREAMS:
        gaps = theory.load_gaps(stream)
        gl[stream] = gaps
        lam_list = 1.0 / gaps.mean()
        res["p_thin"][stream] = {str(E): float(min(1.0, E / (lam_list * (T - 2 * MARGIN)))) for E in ES}
        for k in KS:
            for E in ES:
                for i in range(N_REC):
                    jobs.append((stream, k, E, i, gaps, res["p_thin"][stream][str(E)]))
    res["rows"] = list(ex.map(recording, jobs, chunksize=2))
    fj = []
    for stream in STREAMS:
        for k in KS:
            for E in ES:
                rs = sorted([r for r in res["rows"] if r["stream"] == stream and r["k"] == k
                             and r["E"] == E], key=lambda r: r["i"])
                for form in FORMS:
                    fj.append((stream, k, E, form, gl[stream], res["p_thin"][stream][str(E)],
                               [r["cum"] for r in rs]))
    for stream, k, E, form, out in ex.map(fit_block, fj):
        res["fits"][f"{stream},{k},{E},{form}"] = out
    return res


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--workers", type=int, default=40)
    ap.add_argument("--from-record", action="store_true")
    a = ap.parse_args()
    path = HERE / "window_counts.json"
    if a.from_record:
        res = json.loads(path.read_text())
    else:
        t0 = time.time()
        with ProcessPoolExecutor(a.workers) as ex:
            res = run(ex)
        res["runtime_sec"] = time.time() - t0
        print(f"{res['runtime_sec']:.0f} s", file=sys.stderr)
    summarize(res)
    path.write_text(json.dumps(res, indent=1, default=float))
