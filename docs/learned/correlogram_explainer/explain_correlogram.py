"""Two figures explaining the cross-ROI onset correlogram to a reader who is not math-oriented.

Figure 1 builds the correlogram in four steps on a toy recording (numpy, fixed seed, round-number
settings chosen for legibility, not fitted to anything; its jitter is the measured fast value).
Figure 2 turns width into jitter and shows the real recordings; it reads only the measured run record,
``docs/learned/runs/2026-09-22-jitter-correlogram/jitter_correlogram.json``.

Run: python docs/learned/correlogram_explainer/explain_correlogram.py
"""
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

HERE = Path(__file__).resolve().parent
RUN = HERE.parents[0] / "runs" / "2026-09-22-jitter-correlogram" / "jitter_correlogram.json"

DT = 0.1                       # s, one frame
T = 3600.0                     # s, toy recording length (60 minutes)
N_CELLS = 60
BG_RATE = 0.012                # onsets per second per cell outside shared moments
SHARED_RATE = 0.05             # shared moments per second (one every 20 s on average)
JOIN = 0.3                     # chance a cell joins a given shared moment
TIGHT = 0.11                   # s: the measured fast-stream jitter
BLUE, ORANGE = "#2a78d6", "#eb6834"   # validated categorical slots 1-2 (dataviz palette)
INK, MUTED = "#0b0b0b", "#52514e"
MAX_LAG = 3.0                  # s

plt.rcParams.update({"font.size": 10, "axes.spines.top": False, "axes.spines.right": False,
                     "axes.edgecolor": MUTED, "xtick.color": MUTED, "ytick.color": MUTED,
                     "axes.labelcolor": INK})


def toy(sigma, seed):
    """Onset times per cell (s, frame-rounded) and the shared moments' times."""
    rng = np.random.RandomState(seed)
    shared = np.sort(rng.uniform(0, T, rng.poisson(SHARED_RATE * T)))
    cells = []
    for _ in range(N_CELLS):
        bg = rng.uniform(0, T, rng.poisson(BG_RATE * T))
        joins = shared[rng.rand(shared.size) < JOIN]
        on = np.concatenate([bg, joins + rng.randn(joins.size) * sigma])
        on = np.round(on[(on >= 0) & (on < T)] / DT) * DT
        cells.append(np.unique(on))
    return cells, shared


EDGES = np.arange(-MAX_LAG - DT / 2, MAX_LAG + DT, DT)
LAGS = (EDGES[:-1] + EDGES[1:]) / 2


def pair_lags(a, b):
    d = np.subtract.outer(b, a).ravel()
    return d[np.abs(d) <= MAX_LAG + DT / 2]


def correlogram(cells):
    """Observed onset pairs per 0.1 s lag over all pairs of distinct cells, and chance's count."""
    obs = np.zeros(LAGS.size)
    exp = np.zeros(LAGS.size)
    for i in range(len(cells)):
        for j in range(i + 1, len(cells)):
            obs += np.histogram(pair_lags(cells[i], cells[j]), EDGES)[0]
            exp += cells[i].size * cells[j].size * DT / T
    return obs, exp


def half_width(lags, shape):
    """Lag at which a peak scaled to 1 (floor 0) first falls to 1/2, interpolated, on lags >= 0."""
    pos = lags >= -1e-9
    x, y = lags[pos], shape[pos]
    k = int(np.argmax(y < 0.5))
    return x[k - 1] + (y[k - 1] - 0.5) / (y[k - 1] - y[k]) * (x[k] - x[k - 1])


def scaled(ratio, lags):
    floor = ratio[np.abs(lags) >= 2.0].mean()
    return (ratio - floor) / (ratio[np.argmin(np.abs(lags))] - floor)


def time_ticks(ax, t1):
    ticks = np.arange(0, t1 + 1e-9, 10)
    ax.set_xticks(ticks, ["0" if t == 0 else ("1m" if t == 60 else f"{t:.0f}s") for t in ticks])


def raster(ax, cells, rows, t0, t1, ylabel):
    """Black-and-white raster, time shown relative to t0."""
    for r, c in enumerate(cells[:rows]):
        on = c[(c >= t0) & (c <= t1)] - t0
        ax.vlines(on, r + 0.6, r + 1.4, color=INK, lw=1.4)
    ax.set_ylim(0.3, rows + 0.7)
    ax.set_yticks(range(1, rows + 1), [str(r) for r in range(1, rows + 1)])
    ax.invert_yaxis()
    ax.set_ylabel(ylabel)
    ax.set_xlim(0, t1 - t0)


def lane(ax, times, t0, t1, label):
    """Cue lane ABOVE a raster: down-pointing marks, never drawn on the raster itself."""
    t = times[(times >= t0) & (times <= t1)] - t0
    ax.scatter(t, np.zeros_like(t), marker="v", s=46, color=MUTED)
    ax.set_xlim(0, t1 - t0)
    ax.set_ylim(-0.6, 0.6)
    ax.set_yticks([0], [label])
    ax.tick_params(axis="y", length=0)
    ax.set_xticks([])
    for s in ax.spines.values():
        s.set_visible(False)


# ---------------------------------------------------------------- Figure 1: building it
cells, shared = toy(TIGHT, seed=7)
obs, exp = correlogram(cells)
ratio = obs / exp
hw = half_width(LAGS, scaled(ratio, LAGS))

fig = plt.figure(figsize=(12, 8.6))
gs = fig.add_gridspec(2, 2, hspace=0.5, wspace=0.28)

gA = gs[0, 0].subgridspec(2, 1, height_ratios=[1, 7], hspace=0.05)
T0 = 2870.0                    # s: a minute where five shared moments are visible in cells 1-8
lane(fig.add_subplot(gA[0]), shared, T0, T0 + 60, "shared\nmoment")
ax = fig.add_subplot(gA[1])
raster(ax, cells, 8, T0, T0 + 60, f"cell (8 of {N_CELLS} cells)")
time_ticks(ax, 60)
ax.set_xlabel("time (one minute, 47m50s to 48m50s, of a 60-minute recording)")
ax.text(-0.13, 1.16, "A", transform=ax.transAxes, fontsize=14, fontweight="bold")

# B: one pair of cells, every onset-to-onset time within 3 s, as a dot plot
ax = fig.add_subplot(gs[0, 1])
counts = [(np.histogram(pair_lags(cells[0], cells[j]), EDGES)[0][np.abs(LAGS) < 0.25].sum(), j)
          for j in range(1, N_CELLS)]
j = max(counts)[1]
d = np.round(pair_lags(cells[0], cells[j]) / DT) * DT
for lag in np.unique(d):
    k = int(np.sum(np.isclose(d, lag)))
    ax.scatter(np.full(k, lag), np.arange(1, k + 1), s=22, color=INK)
ax.set_xlim(-MAX_LAG, MAX_LAG)
ax.set_ylim(0, None)
ax.yaxis.set_major_locator(matplotlib.ticker.MaxNLocator(integer=True))
ax.set_xlabel(f"time from a cell-1 onset to a cell-{j + 1} onset (s)")
ax.set_ylabel(f"onset pairs, cells 1 and {j + 1} (count)")
ax.axvline(0, color=MUTED, lw=0.6, ls=":")
ax.text(-0.13, 1.04, "B", transform=ax.transAxes, fontsize=14, fontweight="bold")

# C: every pair of cells pooled, against what chance alone would give
ax = fig.add_subplot(gs[1, 0])
ax.bar(LAGS, obs, width=DT * 0.85, color=INK)
ax.plot(LAGS, exp, color=ORANGE, lw=2, ls="--")
ax.text(0.7, exp[0] * 3.2, "orange dashes: chance\n(cells firing independently)",
        color=INK, fontsize=9)
ax.set_xlim(-MAX_LAG, MAX_LAG)
ax.set_xlabel("time between the two onsets (s)")
ax.set_ylabel(f"onset pairs, all {N_CELLS * (N_CELLS - 1) // 2} pairs of cells (count)")
ax.text(-0.13, 1.04, "C", transform=ax.transAxes, fontsize=14, fontweight="bold")

# D: divided by chance; the width at half height is the answer
ax = fig.add_subplot(gs[1, 1])
ax.plot(LAGS, ratio, color=INK, lw=2)
floor = ratio[np.abs(LAGS) >= 2.0].mean()
peak = ratio[np.argmin(np.abs(LAGS))]
half = floor + (peak - floor) / 2
ax.axhline(1, color=ORANGE, lw=2, ls="--")
ax.text(-2.9, 1.25, "chance", color=INK, fontsize=9)
ax.plot([-hw, hw], [half, half], color=BLUE, lw=2.5)
ax.annotate("", xy=(hw, half), xytext=(0, half),
            arrowprops=dict(arrowstyle="<->", color=BLUE, lw=1.5))
ax.text(hw + 0.12, half, f"half-width at half height\n= {hw:.2f} s", color=INK, va="center",
        fontsize=9)
ax.set_xlim(-MAX_LAG, MAX_LAG)
ax.set_ylim(0, None)
ax.set_xlabel("time between the two onsets (s)")
ax.set_ylabel("onset pairs ÷ chance (times as many)")
ax.text(-0.13, 1.04, "D", transform=ax.transAxes, fontsize=14, fontweight="bold")

fig.savefig(HERE / "figure1_building_the_correlogram.png", dpi=150, bbox_inches="tight")
plt.close(fig)
print(f"figure 1: toy half-width {hw:.3f} s; pair shown cells 1 and {j + 1}")

# ---------------------------------------------------------------- Figure 2: width to jitter, real data
rec = json.loads(RUN.read_text())
fig, (axC, axD) = plt.subplots(1, 2, figsize=(12, 4.6), gridspec_kw=dict(wspace=0.28))
STREAM_COLOUR = {"fast": BLUE, "slow": ORANGE}

# A: the ruler, made on simulated recordings whose jitter is known
ax = axC
for stream, ls in (("fast", "-"), ("slow", "--")):
    h = rec["streams"][stream]["hwhm"]
    x = np.array([float(k) for k in h["calibration_sec"]])
    y = np.array(list(h["calibration_sec"].values()))
    keep = x <= 0.3
    ax.plot(x[keep], y[keep], color=MUTED, lw=1.6, ls=ls, marker="o", ms=4,
            label=f"{stream} stream's simulated recordings")
    real, jit = h["real_sec"], h["jitter_sec"]
    ax.plot([0, jit], [real, real], color=INK, lw=1, ls=":")
    ax.plot([jit, jit], [0, real], color=INK, lw=1, ls=":")
    ax.scatter([jit], [real], color=STREAM_COLOUR[stream], s=70, zorder=5)
    ax.annotate(f"real {stream} stream: {real:.2f} s wide → {jit:.2f} s jitter",
                xy=(jit, real), xytext=(0.165, 0.09 if stream == "fast" else 0.3), fontsize=9,
                arrowprops=dict(arrowstyle="-", color=MUTED, lw=0.8))
ax.set_xlim(0, 0.31)
ax.set_ylim(0, 0.55)
ax.set_xlabel("jitter planted in the simulated recordings (s)")
ax.set_ylabel("half-width measured on them (s)")
ax.legend(fontsize=8, loc="upper left", frameon=False)
ax.text(-0.13, 1.04, "A", transform=ax.transAxes, fontsize=14, fontweight="bold")

# B: each real stream against the simulated shape at the jitter read off for it
ax = axD
lag1 = np.arange(len(rec["streams"]["fast"]["real_excess"])) * rec["dt"]


def mirrored(ex):
    ex = np.asarray(ex, float)
    shoulder = ex[(lag1 >= 5) & (lag1 <= 10)].mean()
    s = (ex - shoulder) / (ex[0] - shoulder)
    keep = lag1 <= 1.5 + 1e-9
    return np.concatenate([-lag1[keep][:0:-1], lag1[keep]]), np.concatenate([s[keep][:0:-1], s[keep]])


for stream, key, ls in (("fast", "0.1", "-"), ("slow", "0.15", "--")):
    c = STREAM_COLOUR[stream]
    x, y = mirrored(rec["streams"][stream]["sim_excess"][key])
    ax.plot(x, y, color=c, lw=5, alpha=0.35, ls=ls,
            label=f"simulated {stream}, {key} s jitter")
    x, y = mirrored(rec["streams"][stream]["real_excess"])
    ax.plot(x, y, color=c, lw=1.8, ls=ls, label=f"real {stream} stream")
ax.axhline(0, color=MUTED, lw=0.6)
ax.set_xlim(-1.5, 1.5)
ax.set_xlabel("time between the two onsets (s)")
ax.set_ylabel("peak height (top = 1)")
ax.legend(fontsize=8, loc="upper right", frameon=False)
ax.text(-0.13, 1.04, "B", transform=ax.transAxes, fontsize=14, fontweight="bold")

fig.savefig(HERE / "figure2_what_the_width_means.png", dpi=150, bbox_inches="tight")
plt.close(fig)
print("figure 2 written")

