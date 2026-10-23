import json, itertools, sys
import numpy as np
sys.path.insert(0, "../tools")
from measure_coordination_rates import solve
from theory_common import N, T
th = np.load("theory_cr.npy", allow_pickle=True)
fr = json.loads(open("fresh_cr.json").read())
old = json.loads(open("../docs/learned/synthetic_validation/aim1_one_source.json").read())["rows"]
print("k_hat/k and rate_hat/rate, medians pooled over part, m, seeds: theory | fresh (10 indep seeds/cell) | Aim1a record")
print(" b    w   sigma |  k: th  fresh  rec | rate: th  fresh  rec | share: th fresh rec | NaN% fresh")
for b, w, sg in itertools.product((0.01, 0.05), (1.0, 2.0, 4.0), (0.05, 0.2, 0.5, 1.0)):
    T_ = [o for o in th if (o["b"], o["w"], o["sg"]) == (b, w, sg)]
    F = [r for r in fr if (r["bg"], r["jit"]) == (b, sg)]
    sols = [(solve(*r["cum"][str(w)], N, w, "fixed"), r) for r in F]
    kf = [s["k"]/r["k"] for s, r in sols]; lf = [s["lam"]/(r["m"]/T) for s, r in sols]
    sf = [s["share"]/(r["m"]*r["k"]/(N*T)) for s, r in sols]
    O = [r for r in old if (r["true"]["bg_rate"], r["true"]["jitter"]) == (b, sg)]
    ko = [r["coord_rates"][str(w)]["k"]/r["true"]["k"] for r in O]
    lo = [r["coord_rates"][str(w)]["lam"]/r["true"]["lam"] for r in O]
    so = [r["coord_rates"][str(w)]["share"]/r["true"]["share"] for r in O]
    m = lambda key: np.median([o[key] for o in T_])
    print(f"{b:.2f} {w:3.0f} {sg:5.2f} | {m('kmed'):5.2f} {np.nanmedian(kf):5.2f} {np.nanmedian(ko):5.2f} | {m('lmed'):5.2f} {np.nanmedian(lf):5.2f} {np.nanmedian(lo):5.2f} | {m('smed'):5.2f} {np.nanmedian(sf):5.2f} {np.nanmedian(so):5.2f} | {100*np.mean(np.isnan(kf)):3.0f}")
