import json, itertools, numpy as np
th = np.load("theory_cr.npy", allow_pickle=True); fr = json.loads(open("fresh_cr.json").read())
rat2, rat3, bias2, bias3 = [], [], [], []
for o in th:
    F = np.array([r["cum"][str(o["w"])] for r in fr if (r["jit"], r["part"], r["m"], r["bg"]) == (o["sg"], o["f"], o["m"], o["b"])])
    rat2.append((o["b"], F[:,0].std(ddof=1)/o["sd2"])); rat3.append((o["b"], F[:,1].std(ddof=1)/o["sd3"]))
    bias2.append(F[:,0].mean()/o["f2"]); bias3.append(F[:,1].mean()/o["f3"])
for b in (0.01, 0.05):
    a = [x for bb, x in rat2 if bb == b]; c = [x for bb, x in rat3 if bb == b]
    print(f"b={b}: observed SD / predicted SD, median (IQR) over 72 cell x window: f2 {np.median(a):.2f} ({np.percentile(a,25):.2f}-{np.percentile(a,75):.2f}), f3 {np.median(c):.2f} ({np.percentile(c,25):.2f}-{np.percentile(c,75):.2f})")
print(f"mean f2 obs/pred median {np.median(bias2):.3f} IQR {np.percentile(bias2,25):.3f}-{np.percentile(bias2,75):.3f}; f3 {np.median(bias3):.3f} IQR {np.percentile(bias3,25):.3f}-{np.percentile(bias3,75):.3f}")
