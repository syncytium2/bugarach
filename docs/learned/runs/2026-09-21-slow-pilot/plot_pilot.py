import json
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

R = Path(sys.argv[1])
NAMES = {"coact": "CoactDetect", "loco": "LoCo", "sync": "SPIKE-synch",
         "chorus_norm": "chorus_norm (net)", "tube": "tube (net)"}
fig, axes = plt.subplots(1, 2, figsize=(10, 3.8), sharey=False)
for ax, which in zip(axes, ("fast", "slow")):
    d = json.load(open(R / f"{which}.json"))
    rows = [(NAMES[k], [v["mean"]], "#444") for k, v in d["coded"].items()]
    rows += [(NAMES[k], [r["mean"] for r in v], "#d62728") for k, v in d["nets"].items()]
    for i, (name, vals, c) in enumerate(rows):
        ax.scatter(vals, [i] * len(vals), color=c, s=36, zorder=3)
    ax.set_yticks(range(len(rows)), [r[0] for r in rows])
    ax.invert_yaxis()
    ax.set_xlabel("mean F1, quiet and busy backgrounds")
    ax.set_ylabel(f"{which} bench · 48 recordings")
    ax.grid(axis="x", alpha=0.3)
    lo = min(min(r[1]) for r in rows)
    ax.set_xlim(lo - 0.03, max(max(r[1]) for r in rows) + 0.03)
fig.text(0.01, 0.01, "Figure 1. Step B pilot: coded detectors at each bench's operating points (grey) and two "
         "untuned nets at three training seeds each (red),\nscored on fresh recordings 4000-4023 per "
         "background. On slow the whole field sits within 0.032 F1; on fast it spans 0.29.", fontsize=8)
fig.tight_layout(rect=(0, 0.1, 1, 1))
fig.savefig(sys.argv[2], dpi=130)
