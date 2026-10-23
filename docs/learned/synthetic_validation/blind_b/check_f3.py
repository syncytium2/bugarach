import sys
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parent))
from sim_cumulant_check import one
if __name__ == "__main__":
    for base, nev in ((1000, 45), (5000, 45), (1000, 15), (5000, 15)):
        with ProcessPoolExecutor(20) as ex:
            res = list(ex.map(one, [(0.05, 0.15, nev, 0.05, s + base - 5000, (1.0,)) for s in range(60)]))
        a = np.array([r[1.0] for r in res]); e3 = a[:, 1] - a[:, 3]; e2 = a[:, 0] - a[:, 2]
        print(base, nev, "f2 mean %.3f sd %.3f | f3 mean %.3f sd %.3f median %.3f | first5 f3 %s" % (e2.mean(), e2.std(), e3.mean(), e3.std(), np.median(e3), np.round(e3[:5], 2)))
