"""Figure for jitter_correlogram.json: the real peaks against the simulator's, both streams."""
import json
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

here = Path(__file__).resolve().parent
rec = json.loads((here / "jitter_correlogram.json").read_text())
k = np.arange(101) * rec["dt"]
fig, axes = plt.subplots(2, 2, figsize=(11, 7))
for col, stream in enumerate(("fast", "slow")):
    r = rec["streams"][stream]
    real = np.array(r["real_excess"])
    sh = np.nanmean(real[50:101])
    ax = axes[0, col]
    ax.plot(k, real, color="black", lw=2, label=f"real, {r['recordings']} baseline windows")
    for j, c in (("0.1", "#c6dbef"), ("0.15", "#6baed6"), ("0.36", "#2171b5"), ("1.0", "#08306b")):
        ax.plot(k, np.array(r["sim_excess"][j]), color=c, lw=1, label=f"simulated, jitter {j} s")
    ax.set_xlim(0, 10)
    ax.set_ylabel(f"{stream} · excess coincidence")
    ax.legend(fontsize=7)
    ax = axes[1, col]
    rp = real[:31] - sh
    ax.plot(k[:31], rp / rp[0], color="black", lw=2, label="real")
    for j, c in (("0.1", "#c6dbef"), ("0.15", "#6baed6"), ("0.36", "#2171b5"), ("1.0", "#08306b")):
        s = np.array(r["sim_excess"][j])
        sp = s[:31] - np.nanmean(s[50:101])
        ax.plot(k[:31], sp / sp[0], color=c, lw=1, label=f"simulated {j} s")
    ax.axhline(0, color="grey", lw=0.5)
    ax.set_ylabel(f"{stream} · peak ÷ its zero-lag value")
    ax.legend(fontsize=7)
for ax in axes[1]:
    ax.set_xlabel("lag between onsets in distinct ROIs (s)")
fig.text(0.01, 0.005,
         "Figure 1. Top: excess coincidence (observed ÷ expected onset pairs − 1) at each 0.1 s lag, "
         "pooled over recordings. Bottom: the 0-3 s peak after subtracting the 5-10 s level,\n"
         "scaled to 1 at zero lag, so the shapes compare regardless of height. Simulated: that "
         "stream's bench, both backgrounds, seeds 1-24,\n"
         "at the planted jitter named. Fast sits between the simulated 0.1 and 0.15 s along its "
         "whole length; slow has a core like that and a longer tail.", fontsize=8)
fig.tight_layout(rect=(0, 0.07, 1, 1))
fig.savefig(here / "jitter_correlogram.png", dpi=120)
print(here / "jitter_correlogram.png")
