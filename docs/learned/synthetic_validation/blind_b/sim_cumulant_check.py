"""Extra simulations: excess f2, f3 of measure_coordination_rates over many seeds, vs theory
(with the hard-core / one-event-per-window correction). Usage: python sim_cumulant_check.py"""
import sys, json
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor
import numpy as np
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools")); sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))
N, T = 33, 2700.0

def one(args):
    sig, part, n_ev, b, seed, wins = args
    from bugarach.simulate import simulate_coordination
    import measure_coordination_rates as mcr
    s, gt = simulate_coordination(duration_sec=T, n_roi=N, bg_rate_hz=b, participation=(part,),
        n_per_level=(n_ev,), jitter_sec=sig, min_sep_sec=20.0, grid_sec=0.1, seed=5000 + seed)
    st = next(iter(s.streams.values()))
    L = int(round(T / mcr.DT))
    trains = [np.minimum(mcr._frames(np.asarray(t), 0.0, T), L - 1) for t in st.t50rise]
    rng = np.random.RandomState(abs(seed) + 7)
    out = {}
    for w in wins:
        wf = int(round(w / mcr.DT))
        raw = mcr.population_cumulants(trains, L, wf)
        sur = np.array([mcr.population_cumulants(mcr.shifted(trains, L, 2 * wf, rng), L, wf) for _ in range(20)]).mean(0)
        out[w] = (raw[0], raw[1], sur[0], sur[1])
    return out

if __name__ == "__main__":
    from theory_cumulant import P_m
    cases = [(0.05, 0.15, 45, 0.05), (0.05, 0.15, 45, 0.01), (0.05, 0.6, 45, 0.01), (1.0, 0.3, 45, 0.05)]
    wins = (1.0, 4.0)
    nseed = 40
    with ProcessPoolExecutor(20) as ex:
        for c in cases:
            res = list(ex.map(one, [(*c, s, wins) for s in range(nseed)]))
            sig, part, n_ev, b = c
            k = max(1, int(np.floor(part * N + 0.5)))
            for w in wins:
                a = np.array([r[w] for r in res])
                ex2, ex3 = a[:, 0] - a[:, 2], a[:, 1] - a[:, 3]
                P2, P3 = P_m(sig, w, 2), P_m(sig, w, 3)
                p = n_ev / T * w; m = p * k
                f2_0 = p * k * (k - 1) * P2; f3_0 = p * k * (k - 1) * (k - 2) * P3
                f2_hc = f2_0 - m * m * (1 - 1 / N)
                f3_hc = f3_0 - 3 * f2_0 * m + 2 * m ** 3
                mu = N * b * w; n = T / w; ES2 = p * k * k
                sd3 = np.sqrt((6 * mu**3 + 18 * mu**2 * ES2) / n * 1.05)
                print(f"sig={sig} k={k} nev={n_ev} b={b} w={w}: f2 mean {ex2.mean():.4g} (se {ex2.std()/np.sqrt(nseed):.2g}) "
                      f"pred0 {f2_0:.4g} predHC {f2_hc:.4g} | f3 mean {ex3.mean():.4g} (sd {ex3.std():.2g}) pred0 {f3_0:.4g} "
                      f"predHC {f3_hc:.4g} sd_pred {sd3:.2g} | raw f3 {a[:,1].mean():.3g} sur f3 {a[:,3].mean():.3g} | median f3 {np.median(ex3):.4g}", flush=True)
