"""Figure 2: how a jitter of about 0.1 s is measurable on a 0.1 s frame grid.

Reads jitter_correlogram.json beside it for panels C and D; panels A and B are drawn from the
Gaussian model directly (numpy, fixed seed). Run: uv run --with matplotlib python explain_jitter.py
"""
import json
from math import erf, sqrt
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

here = Path(__file__).resolve().parent
rec = json.loads((here / "jitter_correlogram.json").read_text())
DT = rec["dt"]
TIGHT, LOOSE = 0.11, 0.36          # measured fast (theory route), fast bench today
C_TIGHT, C_LOOSE = "#d62728", "#1f77b4"


def frame_mass(sigma, k):
    """Probability an onset scattered N(0, sigma) around a frame centre lands k frames away."""
    cdf = lambda x: 0.5 * (1 + erf(x / (sigma * sqrt(2))))  # noqa: E731
    return cdf((k + 0.5) * DT) - cdf((k - 0.5) * DT)


fig = plt.figure(figsize=(12, 8.2))
gs = fig.add_gridspec(2, 2, hspace=0.42, wspace=0.28)

# A: one event per jitter, cells as rows, true onset (open) and recorded frame (filled)
ax = fig.add_subplot(gs[0, 0])
rng = np.random.RandomState(4)
n = 10
for band, (sigma, c) in enumerate(((TIGHT, C_TIGHT), (LOOSE, C_LOOSE))):
    true = rng.randn(n) * sigma
    rec_t = np.round(true / DT) * DT
    rows = np.arange(n) + band * (n + 2)
    ax.scatter(true, rows, facecolors="none", edgecolors=c, s=30, label=f"true onset, σ = {sigma} s")
    ax.scatter(rec_t, rows, marker="s", color=c, s=26, alpha=0.8, label=f"recorded frame, σ = {sigma} s")
for x in np.arange(-1.05, 1.1, DT):
    ax.axvline(x, color="grey", lw=0.3)
ax.set_xlim(-1.05, 1.05)
ax.set_ylim(-8, 22.5)
ax.set_yticks([4.5, 16.5], [f"σ = {TIGHT} s", f"σ = {LOOSE} s"])
ax.set_ylabel("one event · 10 cells each")
ax.set_xlabel("onset relative to the event's shared time (s); grey lines are frame edges")
ax.legend(fontsize=7, loc="lower right", ncol=2)

# B: where onsets land, frame by frame
ax = fig.add_subplot(gs[0, 1])
k = np.arange(-8, 9)
w = 0.4
ax.bar(k * DT - w * DT / 2, [frame_mass(TIGHT, i) for i in k], width=w * DT, color=C_TIGHT,
       label=f"σ = {TIGHT} s (measured, fast)")
ax.bar(k * DT + w * DT / 2, [frame_mass(LOOSE, i) for i in k], width=w * DT, color=C_LOOSE,
       label=f"σ = {LOOSE} s (fast bench today)")
ax.set_xlabel("frame of the recorded onset, relative to the event's frame (s)")
ax.set_ylabel("share of a cell's onsets per frame")
q = DT / sqrt(12)
ax.text(0.02, 0.97, f"rounding to a 0.1 s frame adds\nonly 0.1/√12 = {q:.3f} s of spread:\n"
        f"√(0.11² + {q:.3f}²) = {sqrt(0.11**2 + q**2):.3f} s", transform=ax.transAxes,
        va="top", fontsize=8)
ax.legend(fontsize=7, loc="upper right")

# C: the real pair-lag peak against the shapes each jitter makes
ax = fig.add_subplot(gs[1, 0])
lags = np.arange(-15, 16)
for stream, ls in (("fast", "-"), ("slow", "--")):
    s = rec["streams"][stream]
    x = np.array(s["real_excess"])
    p = (x[:16] - np.nanmean(x[50:101]))
    p = p / p[0]
    ax.plot(lags * DT, np.r_[p[:0:-1], p], color="black", ls=ls, marker="o", ms=3,
            label=f"real {stream}, {s['recordings']} baseline windows")
fast = rec["streams"]["fast"]
for j, c in (("0.1", C_TIGHT), ("0.36", C_LOOSE)):
    x = np.array(fast["sim_excess"][j])
    p = x[:16] - np.nanmean(x[50:101])
    p = p / p[0]
    ax.plot(lags * DT, np.r_[p[:0:-1], p], color=c, lw=1.2, label=f"simulated fast, σ = {j} s")
ax.axhline(0.5, color="grey", lw=0.5)
ax.set_xlabel("lag between onsets of two different cells (s), one point per frame")
ax.set_ylabel("pair excess ÷ its zero-lag value")
ax.legend(fontsize=7, loc="upper right")

# D: calibration, planted jitter against half-width
ax = fig.add_subplot(gs[1, 1])
for stream, ls in (("fast", "-"), ("slow", "--")):
    s = rec["streams"][stream]["hwhm"]
    js = np.array([float(j) for j in s["calibration_sec"]])
    ws = np.array(list(s["calibration_sec"].values()))
    ax.plot(js, ws, ls=ls, marker="o", ms=4, color="black", label=f"{stream} bench, simulated")
    ax.hlines(s["real_sec"], 0, s["jitter_sec"], color="grey", lw=0.8, ls=ls)
    ax.vlines(s["jitter_sec"], 0, s["real_sec"], color="grey", lw=0.8, ls=ls)
rf, rs = rec["streams"]["fast"]["hwhm"], rec["streams"]["slow"]["hwhm"]
ax.text(0.2, 0.97, f"real fast: half-width {rf['real_sec']:.3f} s → σ = {rf['jitter_sec']:.3f} s\n"
        f"real slow: half-width {rs['real_sec']:.3f} s → σ = {rs['jitter_sec']:.3f} s\n"
        "(grey lines: reading each off its own stream's curve)",
        transform=ax.transAxes, va="top", fontsize=8)
ax.axvline(DT, color=C_TIGHT, lw=0.8)
ax.text(DT, 0.45, " one frame (0.1 s)", color=C_TIGHT, fontsize=8)
ax.set_xlim(0, 0.65)
ax.set_ylim(0, 1.45)
ax.set_xlabel("jitter planted in the simulation, σ (s)")
ax.set_ylabel("half-width of the pair-lag peak (s)")
ax.legend(fontsize=7, loc="lower right")

for a, letter in zip(fig.axes, "ABCD"):
    a.text(-0.1, 1.04, letter, transform=a.transAxes, fontsize=12, fontweight="bold")
fig.text(0.01, 0.005,
         "Figure 2. How a jitter of about 0.1 s is measurable with 0.1 s frames. Jitter σ: the standard deviation of the cells' "
         "onset times around an event's shared time.\n"
         "A: one simulated event per σ; each cell's true onset (open) is recorded at its frame (filled). B: where a cell's "
         "recorded onset lands, frame by frame; σ = 0.11 s still spreads over 3-5 frames.\n"
         "C: every pair of onsets from two different cells, pooled over all events, at each frame of lag; the real peaks sit "
         "close to the σ = 0.1 s shape and far from the 0.36 s one. D: the calibration; values below one frame are still told apart.",
         fontsize=8)
fig.savefig(here / "explain_jitter.png", dpi=120, bbox_inches="tight")
print(here / "explain_jitter.png")
