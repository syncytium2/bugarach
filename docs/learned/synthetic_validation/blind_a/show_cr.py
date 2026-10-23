import numpy as np, itertools
out = np.load("theory_cr.npy", allow_pickle=True)
print(" b    w   sg    f   m | k0  kmed  obs-med  [obs vals]        | kIQRpred | lam0 lmed obs | sd2/f2 sd3/f3")
for o in out:
    if o["w"] not in (1.0, 4.0): continue
    print(f"{o['b']:.2f} {o['w']:2.0f} {o['sg']:4.2f} {o['f']:.2f} {o['m']:2d} | {o['k0']:.2f} {o['kmed']:.2f} {np.median(o['ko']):.2f} {np.round(np.sort(o['ko']),2)} | {o['kiqr']:.2f} | {o['lam0']:.2f} {o['lmed']:.2f} {np.median(o['lo']):.2f} | {o['sd2']/o['f2']:.2f} {o['sd3']/o['f3']:.2f}")
