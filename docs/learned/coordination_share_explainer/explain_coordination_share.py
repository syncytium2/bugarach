"""Six figures explaining ``tools/measure_coordination_rates.py``: what share of calcium events
is coordinated, measured without defining a coordinated event. For readers who are not
math-oriented.

Every figure is drawn from simulated recordings with a known answer. **No real recording is
read.** The default dataset is under a contamination stop (2026-10-05), and the cross-cell
artifact it carries is the kind of thing this statistic counts, so real numbers wait for the
producer's corrected export.

**The recordings.** Each one starts from the fast bench's own generator,
``simulate_coordination`` with :data:`bugarach.bench.BENCH_RECORDING` and a regime from
:data:`bugarach.bench.REGIMES` (32 cells, 45 minutes, unequal per-cell rates, background clumped
in time), with the bench's planted events and decoys turned off. Shared moments are then planted
here, on a gap schedule of this page's own (Tony, 2026-10-14): **2 close pairs** (moments 2 s
apart), **2 medium pairs** (10 to 20 s apart) and **7 single moments**, every pair and single at
least 120 s from the next. ``simulate_coordination`` can draw gaps from a distribution
(``gap_source``/``gap_mix``, which the bench has used by default since ADR-0010), but it cannot
plant a fixed number of pairs at fixed gaps, so the schedule is written here. The bench is not
changed. Figure 3 also scores the tool on the bench's own recordings, exactly as the tool's
calibration builds them (``measure_coordination_rates._sim``).

Everything that estimates is imported from the tool; nothing here re-derives it.

Run: python docs/learned/coordination_share_explainer/explain_coordination_share.py [--also]
  Writes to <darkroom>/bugarach/2026-10-14-coordination-share-explainer/; ``--also`` writes the
  repo copy beside this script. ``--date`` names the files (default: the page's date, so the
  README's links keep resolving when the figures are redrawn).
"""
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
for _p in (REPO / "src", REPO / "tools"):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

import measure_coordination_rates as mcr  # noqa: E402
from bugarach import bench  # noqa: E402
from bugarach.simulate import simulate_coordination  # noqa: E402

PAGE_DATE = "20261014"
DT = mcr.DT
T = float(bench.BENCH_RECORDING["duration_sec"])          # 2700 s
N = int(bench.BENCH_RECORDING["n_roi"])                    # 32 cells
LEVELS = tuple(bench.BENCH_RECORDING["participation"])     # share of cells joining, 3 levels
PER_LEVEL = int(bench.BENCH_RECORDING["n_per_level"][0])   # 5 moments at each level
N_MOMENTS = len(LEVELS) * PER_LEVEL                        # 15
SIZES = tuple(max(1, int(round(p * N))) for p in LEVELS)   # 10, 6, 3 cells
JITTER = mcr.CAL_JITTER["bugarach.bench"]                  # 0.106 s, the calibration's jitter
QUIET = float(bench.REGIMES["baseline_quiet"]["bg_rate_hz"])
BUSY = float(bench.REGIMES["baseline_busy"]["bg_rate_hz"])
HOT = bench.ELEVATED_RATE_RECORDING                        # the bench's elevated-rate stretch
SEEDS = tuple(range(1, 25))                                # 24 per background, as the tool's
SLOT_SEP = 120.0                                           # s, the bench's old spacing floor
MARGIN = 30.0                                              # s, kept clear at each end
MEDIUM_GAPS = (10.0, 20.0)
PLANT_SEED = 7919                                          # moments drawn apart from background
BASE = {**bench.BENCH_RECORDING, "n_per_level": (0, 0, 0), "n_distractors": 0,
        "hot_window": None, "hot_rate_hz": 0.0, "ramp_sec": 0.0}

SCHEDULES = {
    # name: (pairs, gap between the two moments of a pair in s, or "medium"). Rest single.
    "120 s only": (0, None),
    "medium pairs (10–20 s)": (2, "medium"),
    "close pairs (2 s)": (2, 2.0),
    "very close pairs (0.5 s)": (2, 0.5),
}

BLUE, ORANGE, GREEN, YELLOW = "#2a78d6", "#eb6834", "#1baf7a", "#eda100"  # dataviz slots 1-4
INK, MUTED, GRID = "#0b0b0b", "#52514e", "#d9d8d4"
GAP_COLOUR = {"close": BLUE, "medium": ORANGE, "single": GREEN}
SET_STYLE = {"mixed": (INK, "o"), "120 s only": (GREEN, "s"), "medium pairs (10–20 s)": (ORANGE, "^"),
             "close pairs (2 s)": (BLUE, "D"), "very close pairs (0.5 s)": (YELLOW, "v")}

plt.rcParams.update({"font.size": 11, "axes.spines.top": False, "axes.spines.right": False,
                     "axes.edgecolor": MUTED, "xtick.color": MUTED, "ytick.color": MUTED,
                     "axes.labelcolor": INK, "legend.fontsize": 10})


# ---------------------------------------------------------------- the simulated recordings

def background(seed: int, bg_hz: float, **extra) -> list[np.ndarray]:
    """Onset times (s) per cell from the bench's own generator, nothing planted."""
    s, _ = simulate_coordination(seed=seed, **{**BASE, "bg_rate_hz": bg_hz, **extra})
    return [np.asarray(t, float) for t in s.streams[bench.STREAM].t50rise]


def schedule(rng, n_close: int, n_medium: int, close_gap: float, n_total: int):
    """Moment times (s) and each one's gap type. Pairs and singles are slots, and the gap
    between two slots is always at least SLOT_SEP."""
    kinds = ["close"] * n_close + ["medium"] * n_medium
    kinds += ["single"] * (n_total - 2 * len(kinds))
    rng.shuffle(kinds)
    spans = [close_gap if k == "close" else rng.uniform(*MEDIUM_GAPS) if k == "medium" else 0.0
             for k in kinds]
    slack = T - 2 * MARGIN - sum(spans) - SLOT_SEP * (len(kinds) - 1)
    assert slack > 0, "the schedule does not fit in the recording"
    extra = np.diff(np.concatenate([[0], np.sort(rng.uniform(0, slack, len(kinds))), [slack]]))
    t, times, gap = MARGIN + extra[0], [], []
    for k, s, e in zip(kinds, spans, extra[1:]):
        times.append(t)
        gap.append(k)
        if k != "single":
            times.append(t + s)
            gap.append(k)
        t += s + SLOT_SEP + e
    return np.array(times), gap


def recording(seed: int, bg_hz: float = QUIET, pairs: int = 2, pair_gap=2.0, mixed: bool = True,
              n_total: int = N_MOMENTS, size: int | None = None, ramp: float = 1.0, **extra):
    """Onset frames per cell, the planted moments, and the planted truth.

    ``mixed``: 2 close pairs (``pair_gap`` apart) and 2 medium pairs; otherwise ``pairs`` pairs of
    one kind (``pair_gap`` seconds, or ``"medium"``). ``size``: every moment joined by ``size``
    cells instead of the bench's three sizes. ``ramp``: the background rises linearly to ``ramp``
    times its start over the recording, by thinning, with its mean kept at ``bg_hz``. ``extra``
    goes to the generator (e.g. an elevated-rate stretch: ``hot_window``, ``hot_rate_hz``,
    ``ramp_sec``)."""
    L = int(round(T / DT))
    if ramp == 1.0:
        bg = background(seed, bg_hz, **extra)
    else:   # draw at the mean of the top, keep each onset with probability rising to 1
        top = 2 * ramp / (1 + ramp)
        thin = np.random.RandomState(seed + 31)
        bg = [t[thin.rand(t.size) < (1 + (ramp - 1) * t / T) / ramp]
              for t in background(seed, bg_hz * top, **extra)]
    rng = np.random.RandomState(seed + PLANT_SEED)
    if n_total == 0:
        times, gap = np.zeros(0), []
    elif mixed:
        times, gap = schedule(rng, 2, 2, pair_gap, n_total)
    elif pair_gap == "medium":
        times, gap = schedule(rng, 0, pairs, 2.0, n_total)
    else:
        times, gap = schedule(rng, pairs, 0, pair_gap or 2.0, n_total)
    ks = np.full(N_MOMENTS, size) if size else np.repeat(SIZES, PER_LEVEL)
    rng.shuffle(ks)
    ks = ks[:times.size]
    joined = [[] for _ in range(N)]
    for t, k in zip(times, ks):
        for c in rng.choice(N, k, replace=False):
            joined[c].append(t + rng.randn() * JITTER)
    trains, n_bg, n_pl = [], 0, 0
    for i in range(N):
        # The tool's own frame conversion and clamp (measure_coordination_rates._sim).
        plf = np.minimum(mcr._frames(joined[i], 0.0, T), L - 1)
        bgf = np.setdiff1d(np.minimum(mcr._frames(bg[i], 0.0, T), L - 1), plf)
        trains.append(np.sort(np.concatenate([bgf, plf])))
        n_bg += bgf.size
        n_pl += plf.size
    truth = dict(share=n_pl / max(n_bg + n_pl, 1), events=n_bg + n_pl, moments=int(times.size),
                 k=float(ks.mean()) if ks.size else float("nan"), lam=times.size / T)
    return dict(trains=trains, L=L, times=times, gap=gap, ks=ks, truth=truth)


def _measure(job):
    seed, kw = job
    rec = recording(seed, **kw)
    m = mcr.measure(rec["trains"], rec["L"], np.random.RandomState(seed))
    wf = int(round(1.0 / DT))
    m["raw_f2_1s"], m["raw_f3_1s"] = mcr.population_cumulants(rec["trains"], rec["L"], wf)
    return m, rec["truth"]


def run_set(pool, kw, bgs=(QUIET, BUSY), seeds=SEEDS):
    return list(pool.map(_measure, [(s, {**kw, "bg_hz": bg}) for bg in bgs for s in seeds]))


def recovered(results, w=1.0, model=mcr.ADOPTED_MODEL):
    """Each recording's share of events, as the tool reports it: f3/f2 pooled over the set,
    then each recording's own f2 and rate (``per_recording``, the path ``summarize`` takes)."""
    recs = [m for m, _ in results]
    return np.array([x["share"] / m["rate"] for x, m in zip(mcr.per_recording(recs, w, model), recs)])


def recovered_moments(results, w=1.0, model=mcr.ADOPTED_MODEL):
    pr = mcr.per_recording([m for m, _ in results], w, model)
    return np.array([x["k"] for x in pr]), np.array([x["lam"] for x in pr])


def own(results, w=1.0, model=mcr.ADOPTED_MODEL):
    """Each recording on its own, f3/f2 not pooled (``solve`` on that recording alone)."""
    out = []
    for m, _ in results:
        c = m["cum"][str(w)]
        out.append(mcr.solve(c["f2"], c["f3"], m["N"], w, model)["share"] / m["rate"])
    return np.array(out)


def in_run(tests, run, w=1.0, model=mcr.ADOPTED_MODEL):
    """What each test recording reports when it is one recording of a run that also holds
    ``run`` (a set with shared moments): f3/f2 pooled over the run plus it, as the tool does."""
    recs = [m for m, _ in run]
    return np.array([mcr.per_recording(recs + [m], w, model)[-1]["share"] / m["rate"]
                     for m, _ in tests])


def planted(results, key="share"):
    return np.array([t[key] for _, t in results])


def q(v, p):
    v = np.asarray(v, float)
    v = v[np.isfinite(v)]
    return float(np.percentile(v, p)) if v.size else None


# ---------------------------------------------------------------- figure helpers

def minutes(t: float) -> str:
    """The house time label (``_time_axis_hook``): 45s, 2m, 2m30s; zero is 0s."""
    m, s = divmod(int(round(t)), 60)
    return f"{s}s" if m == 0 else (f"{m}m" if s == 0 else f"{m}m{s:02d}s")


def time_axis(ax, t0, t1, step=30):
    ticks = np.arange(np.ceil(t0 / step) * step, t1 + 1e-9, step)
    ax.set_xticks(ticks, [minutes(t) for t in ticks])
    ax.set_xlim(t0, t1)


def letter(ax, text, x=-0.07, y=1.02):
    ax.text(x, y, text, transform=ax.transAxes, fontsize=14, fontweight="bold", va="bottom")


def artifact_name(topic: str, ext: str, date: str) -> str:
    out = subprocess.run([sys.executable, str(REPO / "tools" / "naming" / "artifact_name.py"),
                          "build", "--type", "explainer", "--topic", topic, "--ext", ext,
                          "--date", date], capture_output=True, text=True, check=True)
    return out.stdout.strip()


def save(fig, out: Path, topic: str, date: str, title: str) -> str:
    name = artifact_name(topic, "png", date)
    fig.savefig(out / name, dpi=150, bbox_inches="tight",
                metadata={"Title": title, "Author": "bugarach, explain_coordination_share.py"})
    plt.close(fig)
    return name


# ---------------------------------------------------------------- the figures

def figure1(out, date):
    """The recording, its count in 1 s windows, and the same minutes in one shifted copy."""
    best = (-1, None, 0.0)
    for seed in SEEDS:
        r = recording(seed)
        for start in np.arange(0, T - 300, 10.0):
            sel = (r["times"] >= start + 10) & (r["times"] <= start + 290)
            kinds = {g for g, s in zip(r["gap"], sel) if s}
            if not {"close", "medium", "single"} <= kinds:
                continue
            score = sum(k for g, k, s in zip(r["gap"], r["ks"], sel) if s and g != "single")
            if score > best[0]:
                best = (score, seed, float(start))
    _, seed, t0 = best
    rec = recording(seed)
    t1 = t0 + 300.0
    L, wf = rec["L"], int(round(1.0 / DT))
    sur = mcr.shifted(rec["trains"], L, 2 * wf, np.random.RandomState(11))
    fig = plt.figure(figsize=(10.5, 10.5))
    gs = fig.add_gridspec(4, 1, height_ratios=[0.8, 5, 1.8, 5], hspace=0.2)
    lane = fig.add_subplot(gs[0])
    shown = {}
    for t, g in zip(rec["times"], rec["gap"]):
        if t0 <= t <= t1:
            shown[g] = True
            lane.scatter([t], [0], marker="v", s=34, color=GAP_COLOUR[g], zorder=3)
    labels = {"close": "moment in a close pair (2 s apart)",
              "medium": "moment in a medium pair (10–20 s apart)",
              "single": "single moment (120 s or more from the next)"}
    for g in ("close", "medium", "single"):
        if g in shown:
            lane.scatter([], [], marker="v", s=34, color=GAP_COLOUR[g], label=labels[g])
    pairs = [t for t, g in zip(rec["times"], rec["gap"]) if g == "close" and t0 <= t <= t1]
    for a in pairs[::2]:
        lane.text(a + 1.0, 0.45, "2 s pair", ha="center", va="bottom", fontsize=9, color=INK)
    lane.set_xlim(t0, t1)
    lane.set_ylim(-0.6, 1.4)
    lane.set_yticks([0], ["planted"])
    lane.tick_params(axis="y", length=0)
    lane.tick_params(axis="x", bottom=False, labelbottom=False)
    for s in lane.spines.values():
        s.set_visible(False)
    lane.legend(loc="lower left", bbox_to_anchor=(0, 1.15), ncol=2, frameon=False)
    letter(lane, "A", x=-0.16, y=0.25)

    def raster(ax, trains, ylabel):
        for r, tr in enumerate(trains):
            on = tr * DT
            on = on[(on >= t0) & (on <= t1)]
            ax.vlines(on, r + 0.6, r + 1.4, color=INK, lw=1.2)
        ax.set_ylim(N + 0.7, 0.3)
        ax.set_yticks([1, 8, 16, 24, 32])
        ax.set_ylabel(ylabel)

    ax = fig.add_subplot(gs[1], sharex=lane)
    raster(ax, rec["trains"], f"cell · {N} cells")
    ax.tick_params(labelbottom=False)
    letter(ax, "B", x=-0.16)
    cx = fig.add_subplot(gs[2], sharex=lane)
    edges = np.arange(t0, t1 + 1, 1.0)
    X = np.histogram(np.concatenate(rec["trains"]) * DT, edges)[0]
    cx.bar(edges[:-1] + 0.5, X, width=0.8, color=MUTED)
    cx.set_ylabel("onsets per\n1 s window (X)")
    cx.yaxis.set_major_locator(matplotlib.ticker.MaxNLocator(integer=True))
    cx.tick_params(labelbottom=False)
    letter(cx, "C", x=-0.16)
    dx = fig.add_subplot(gs[3], sharex=lane)
    raster(dx, sur, f"cell, shifted copy · {N} cells")
    time_axis(dx, t0, t1)
    dx.set_xlabel("time in the recording")
    letter(dx, "D", x=-0.16)
    name = save(fig, out, "coordinated-share-fig1-the-count", date, "Figure 1. The count")
    return name, dict(window_sec=[t0, t1], seed=seed, background_hz=QUIET,
                      gaps_in_view=sorted(shown))


def figure2(out, date):
    """Same mean, wider spread: the recording against its shifted copies."""
    rec = recording(3, BUSY)
    L, wf = rec["L"], int(round(1.0 / DT))
    rng = np.random.RandomState(11)

    def counts(trains):
        return np.bincount(np.concatenate(trains) // wf, minlength=L // wf)[:L // wf]

    Xr, Xs = counts(rec["trains"]), counts(mcr.shifted(rec["trains"], L, 2 * wf, rng))
    f2r, f3r = mcr.population_cumulants(rec["trains"], L, wf)
    surs = np.array([mcr.population_cumulants(mcr.shifted(rec["trains"], L, 2 * wf, rng), L, wf)
                     for _ in range(mcr.N_SURR)])
    e2, e3 = f2r - surs[:, 0].mean(), f3r - surs[:, 1].mean()
    k = e3 / e2 + 2
    fig, (axA, axB) = plt.subplots(1, 2, figsize=(10.5, 4.4), gridspec_kw=dict(wspace=0.32))
    top = int(max(Xr.max(), Xs.max()))
    bins = np.arange(-0.5, top + 1.5)
    x = np.arange(top + 1)
    axA.bar(x - 0.2, np.histogram(Xs, bins)[0], width=0.38, color=GREEN,
            label=f"shifted copy · mean {Xs.mean():.2f} onsets per window")
    axA.bar(x + 0.2, np.histogram(Xr, bins)[0], width=0.38, color=INK,
            label=f"recording · mean {Xr.mean():.2f} onsets per window")
    axA.set_yscale("log")
    axA.set_xlabel("onsets in one 1 s window (X)")
    axA.set_ylabel(f"1 s windows (count, log scale;\n{Xr.size} windows)")
    axA.legend(frameon=False, loc="lower left", bbox_to_anchor=(0, 1.02))
    axA.xaxis.set_major_locator(matplotlib.ticker.MaxNLocator(integer=True))
    letter(axA, "A")
    jit = np.random.RandomState(5)
    for i, (real, s) in enumerate(((f2r, surs[:, 0]), (f3r, surs[:, 1]))):
        axB.scatter(np.full(s.size, i - 0.12) + jit.uniform(-0.04, 0.04, s.size), s, s=20,
                    color=GREEN, label="each of 20 shifted copies" if i == 0 else None)
        axB.scatter([i + 0.12], [real], s=70, color=INK, marker="D",
                    label="the recording" if i == 0 else None)
        axB.annotate("", xy=(i + 0.12, real), xytext=(i + 0.12, s.mean()),
                     arrowprops=dict(arrowstyle="<->", color=MUTED, lw=1.2))
        axB.text(i + 0.2, (real + s.mean()) / 2, f"excess\n{real - s.mean():.2f}", va="center")
    axB.axhline(0, color=GRID, lw=1)
    axB.set_xticks([0, 1], ["f₂\npairs beyond\nchance", "f₃\ntriples beyond\nchance"])
    axB.set_xlim(-0.5, 1.75)
    axB.set_ylabel("per 1 s window")
    axB.text(0.02, 0.62, f"k = f₃ ÷ f₂ + 2\n   = {e3:.2f} ÷ {e2:.2f} + 2\n   ≈ {k:.1f} cells per moment",
             transform=axB.transAxes, va="top")
    axB.legend(frameon=False, loc="upper left")
    letter(axB, "B")
    name = save(fig, out, "coordinated-share-fig2-wider-spread", date, "Figure 2. Same mean, wider spread")
    return name, dict(seed=3, background_hz=BUSY, mean_real=float(Xr.mean()),
                      mean_shifted=float(Xs.mean()), max_window_real=int(Xr.max()),
                      max_window_shifted=int(Xs.max()), f2=f2r, f3=f3r,
                      f2_shifted_mean=float(surs[:, 0].mean()),
                      f3_shifted_mean=float(surs[:, 1].mean()), excess_f2=e2, excess_f3=e3, k=k)


def figure3(out, date, mixed, one_size, bench_cal):
    """Recovered against planted, on three sets: three moment sizes, one size, and the bench as
    the tool's own calibration builds it."""
    fig, axes = plt.subplots(1, 3, figsize=(10.5, 4.2), sharey=True, gridspec_kw=dict(wspace=0.1))
    stats = {}
    panels = [("A", "three moment sizes (10, 6, 3 cells)", mixed, planted(mixed)),
              ("B", "one moment size (6 cells)", one_size, planted(one_size)),
              ("C", "the bench, as the tool's own check runs", bench_cal,
               np.array([t["share"] / m["rate"] for m, t in bench_cal]))]
    for ax, (tag, what, res, p) in zip(axes, panels):
        ax.axhspan(1 - mcr.CAL_TOL, 1 + mcr.CAL_TOL, color=GRID, alpha=0.7, lw=0,
                   label="pass band (±25%)" if tag == "A" else None)
        ax.axhline(1, color=MUTED, lw=1, label="right answer" if tag == "A" else None)
        stats[what] = {}
        for model, face in (("fixed", INK), ("binomial", "none")):
            r = recovered(res, 1.0, model) / p
            stats[what][model] = dict(median_error=q(r, 50) - 1, q10=q(r, 10), q90=q(r, 90),
                                      min=q(r, 0), max=q(r, 100))
            lab = f"{model} model" + (" (adopted)" if model == mcr.ADOPTED_MODEL else "")
            ax.scatter(p, r, s=26, facecolor=face, edgecolor=INK, lw=1,
                       label=lab if tag == "A" else None)
        ax.set_xlim(0, None)
        ax.xaxis.set_major_formatter(matplotlib.ticker.PercentFormatter(1.0, decimals=0))
        ax.set_xlabel(f"planted share of events\n{what}", fontsize=10)
        letter(ax, tag, x=-0.05)
        stats[what]["recordings"] = len(res)
    axes[0].set_ylabel("recovered ÷ planted (1 s window)")
    axes[0].set_ylim(0.4, 1.6)
    fig.legend(loc="lower center", bbox_to_anchor=(0.5, 1.0), ncol=4, frameon=False)
    name = save(fig, out, "coordinated-share-fig3-planted-vs-recovered", date,
                "Figure 3. Planted against recovered")
    return name, stats


def figure4(out, date, sets):
    """Window size and the intervals between moments, fixed model: the share, k and λ."""
    model = mcr.ADOPTED_MODEL
    fig, axes = plt.subplots(1, 3, figsize=(10.5, 4.0), gridspec_kw=dict(wspace=0.5))
    quantities = (("share", "share of events"), ("k", "participants per moment (k)"),
                  ("lam", "moments per minute (λ)"))
    table = {}
    for ax, (key, what), tag in zip(axes, quantities, "ABC"):
        if key == "share":
            ax.axhspan(-mcr.CAL_TOL, mcr.CAL_TOL, color=GRID, alpha=0.7, lw=0, label="pass band (±25%)")
        ax.axhline(0, color=MUTED, lw=1)
        for i, (name, res) in enumerate(sets.items()):
            p = planted(res, key)
            meds = []
            for w in mcr.WINDOWS:
                if key == "share":
                    got = recovered(res, w, model)
                    table.setdefault(name, {}).setdefault("share_binomial", {})[str(w)] = q(
                        recovered(res, w, "binomial") / p - 1, 50)
                else:
                    k, lam = recovered_moments(res, w, model)
                    got = k if key == "k" else lam
                meds.append(q(got / p - 1, 50))
                table.setdefault(name, {}).setdefault(key, {})[str(w)] = meds[-1]
            colour, marker = SET_STYLE[name]
            x = np.arange(len(mcr.WINDOWS)) + (i - 2) * 0.07
            ax.plot(x, meds, color=colour, lw=1.8, marker=marker, ms=7,
                    label=name if tag == "A" else None)
        ax.set_xticks(range(len(mcr.WINDOWS)), [f"{w:.0f} s" for w in mcr.WINDOWS])
        ax.set_xlabel("window length (w)")
        ax.set_ylabel(f"{what}:\nrecovered ÷ planted − 1", fontsize=10)
        ax.yaxis.set_major_formatter(matplotlib.ticker.PercentFormatter(1.0, decimals=0))
        letter(ax, tag, x=-0.32)
    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="lower center", bbox_to_anchor=(0.5, 1.0), ncol=3,
               frameon=False, title="intervals between moments (median over 48 recordings each)")
    name = save(fig, out, "coordinated-share-fig4-window-and-intervals", date,
                "Figure 4. Window size and the intervals between moments")
    return name, table


def figure5(out, date, run, durations, amplitudes, nulls, slow):
    """What it counts that it should not: a field-wide busy stretch (by length and by size), and
    what subtracting the shifted copies does to steady and slowly rising backgrounds."""
    fig, (axA, axB, axC) = plt.subplots(1, 3, figsize=(10.5, 4.6),
                                        gridspec_kw=dict(wspace=0.75, width_ratios=[1, 0.8, 1.1]))
    stats = {"A": {}, "B": {}, "C": {}}
    null_share = in_run(nulls, run)
    stats["A"]["no stretch"] = dict(median=q(null_share, 50), q10=q(null_share, 10),
                                    q90=q(null_share, 90), min=q(null_share, 0), max=q(null_share, 100))
    xs, med, lo, hi = [], [], [], []
    for i, (d, res) in enumerate(durations.items()):
        s = in_run(res, run)
        xs.append(i)
        med.append(q(s, 50))
        lo.append(q(s, 10))
        hi.append(q(s, 90))
        stats["A"][f"{d:g} s"] = dict(median=med[-1], q10=lo[-1], q90=hi[-1], max=q(s, 100))
    axA.fill_between(xs, lo, hi, color=GRID, lw=0, label="10th–90th percentile")
    axA.plot(xs, med, color=INK, marker="o", lw=1.8, label="median, 24 recordings")
    axA.axhline(0, color=MUTED, lw=1)
    axA.axhline(stats["A"]["no stretch"]["median"], color=MUTED, lw=1, ls=":",
                label="no stretch (median)")
    axA.set_xticks(xs, [minutes(d) for d in durations])
    axA.set_xlabel(f"length of a stretch at +{HOT['hot_rate_hz']} onsets\nper second per cell (sharp edges)",
                   fontsize=10)
    axA.set_ylabel("share of events reported coordinated\n(nothing planted; 1 s window)", fontsize=10)
    axA.yaxis.set_major_formatter(matplotlib.ticker.PercentFormatter(1.0, decimals=1))
    axA.legend(frameon=False, fontsize=9, loc="upper right")
    letter(axA, "A", x=-0.3)
    xs, med, lo, hi = [], [], [], []
    for mult, (res, frac) in amplitudes.items():
        s = in_run(res, run)
        xs.append(mult)
        med.append(q(s, 50))
        lo.append(q(s, 10))
        hi.append(q(s, 90))
        stats["B"][f"{mult:.0f}x"] = dict(median=med[-1], q10=lo[-1], q90=hi[-1],
                                          share_of_onsets_in_stretch=frac)
    axB.fill_between(xs, lo, hi, color=GRID, lw=0)
    axB.plot(xs, med, color=INK, marker="o", lw=1.8)
    axB.axhline(0, color=MUTED, lw=1)
    axB.set_xscale("log")
    axB.set_xticks(xs, [f"{x:.0f}×" for x in xs])
    axB.xaxis.set_minor_locator(matplotlib.ticker.NullLocator())
    axB.set_xlabel("rate inside a 5-minute stretch\n÷ the background (the bench's 30 s ramps)",
                   fontsize=10)
    axB.yaxis.set_major_formatter(matplotlib.ticker.PercentFormatter(1.0, decimals=1))
    letter(axB, "B", x=-0.18)
    for i, (label, res) in enumerate(slow.items()):
        raw = np.array([m["raw_f2_1s"] for m, _ in res])
        exc = np.array([m["cum"]["1.0"]["f2"] for m, _ in res])
        jit = np.random.RandomState(i).uniform(-0.12, 0.12, raw.size)
        axC.scatter(raw, np.full(raw.size, i) + jit, s=18, facecolor="none", edgecolor=INK, lw=0.9,
                    label="before subtracting the copies" if i == 0 else None)
        axC.scatter(exc, np.full(exc.size, i) + jit, s=18, color=INK,
                    label="after" if i == 0 else None)
        stats["C"][label.replace("\n", " ")] = dict(raw_f2_median=q(raw, 50), excess_f2_median=q(exc, 50),
                                                    removed=1 - q(exc, 50) / q(raw, 50) if q(raw, 50) else None)
    axC.axvline(0, color=MUTED, lw=1)
    axC.set_yticks(range(len(slow)), list(slow))
    axC.set_ylim(len(slow) - 0.5, -0.5)
    axC.set_xlabel("pairs beyond chance, f₂\n(per 1 s window; nothing planted)", fontsize=10)
    axC.legend(frameon=False, fontsize=9, loc="lower left", bbox_to_anchor=(0, 1.0))
    letter(axC, "C", x=-0.55)
    name = save(fig, out, "coordinated-share-fig5-what-else-counts", date,
                "Figure 5. What else it counts")
    return name, stats


def figure6(out, date, groups):
    """How far one recording strays: each recording's answer on its own, and as the tool
    reports it (f3/f2 pooled over the set)."""
    fig, ax = plt.subplots(figsize=(10.5, 4.4))
    stats = {}
    for i, (label, res) in enumerate(groups.items()):
        p = planted(res)
        mine, tool = own(res) / p, recovered(res) / p
        jit = np.random.RandomState(i)
        for dx, v, face, name in ((-0.17, mine, "none", "the recording on its own"),
                                  (0.17, tool, INK, "as the tool reports it (pooled over the set)")):
            ok = np.isfinite(v)
            ax.scatter(np.full(ok.sum(), i + dx) + jit.uniform(-0.06, 0.06, ok.sum()), v[ok], s=18,
                       facecolor=face, edgecolor=INK, lw=0.9, label=name if i == 0 else None)
            ax.plot([i + dx - 0.1, i + dx + 0.1], [q(v, 50)] * 2, color=ORANGE, lw=2.5,
                    label="median" if (i == 0 and dx > 0) else None)
        stats[label.replace("\n", " ")] = dict(
            recordings=len(res), no_answer=int((~np.isfinite(mine)).sum()),
            own=dict(q10=q(mine, 10), median=q(mine, 50), q90=q(mine, 90), min=q(mine, 0), max=q(mine, 100)),
            tool=dict(q10=q(tool, 10), median=q(tool, 50), q90=q(tool, 90), min=q(tool, 0), max=q(tool, 100)),
            planted_share_median=q(p, 50), event_rate_hz=q([m["rate"] for m, _ in res], 50))
    ax.axhline(1, color=MUTED, lw=1, label="right answer")
    ax.set_xticks(range(len(groups)), list(groups))
    ax.set_ylim(0, None)
    ax.set_ylabel("share recovered ÷ planted\n(fixed model, 1 s window)")
    ax.legend(frameon=False, loc="lower center", bbox_to_anchor=(0.5, 1.0), ncol=4)
    name = save(fig, out, "coordinated-share-fig6-one-recording", date,
                "Figure 6. How far one recording strays")
    return name, stats


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--out", type=Path, default=None,
                    help="default: <darkroom>/bugarach/2026-10-14-coordination-share-explainer")
    ap.add_argument("--also", action="store_true", help="also write the repo copy beside this script")
    ap.add_argument("--date", default=PAGE_DATE, help="the date in the file names (default: the page's)")
    ap.add_argument("--jobs", type=int, default=8)
    a = ap.parse_args()
    if a.out is None:
        from bugarach.paths import darkroom
        root = darkroom()
        if root is None:
            sys.exit("no darkroom found: set BUGARACH_DARKROOM or pass --out")
        a.out = root / "2026-10-14-coordination-share-explainer"
    a.out.mkdir(parents=True, exist_ok=True)
    record = dict(note="simulated recordings only; no real recording read",
                  generator="bugarach.simulate.simulate_coordination with bench.BENCH_RECORDING, "
                            "planted events and decoys off; moments planted by this script",
                  cells=N, duration_sec=T, moment_sizes=list(SIZES), moments=N_MOMENTS,
                  jitter_sec=JITTER, quiet_hz=QUIET, busy_hz=BUSY, seeds=len(SEEDS),
                  stretch_hz=HOT["hot_rate_hz"], figures={})
    with ProcessPoolExecutor(a.jobs) as pool:
        mixed = run_set(pool, dict())
        one_size = run_set(pool, dict(size=SIZES[1]))
        bench_cal = list(pool.map(mcr._sim, [("bugarach.bench", r, s)
                                             for r in ("baseline_quiet", "baseline_busy") for s in SEEDS]))
        sets = {"mixed": mixed}
        for name, (n, gap) in SCHEDULES.items():
            sets[name] = run_set(pool, dict(mixed=False, pairs=n, pair_gap=gap))
        quiet_run = run_set(pool, dict(), bgs=(QUIET,))
        nulls = run_set(pool, dict(n_total=0), bgs=(QUIET,))
        durations = {d: run_set(pool, dict(n_total=0, hot_window=(1200.0, 1200.0 + d),
                                           hot_rate_hz=HOT["hot_rate_hz"], ramp_sec=0.0), bgs=(QUIET,))
                     for d in (10.0, 30.0, 60.0, 120.0, 300.0, 900.0)}
        amplitudes = {}
        for added in (QUIET, 4 * QUIET, 9 * QUIET, HOT["hot_rate_hz"]):
            res = run_set(pool, dict(n_total=0, hot_window=HOT["hot_window"], hot_rate_hz=added,
                                     ramp_sec=HOT["ramp_sec"]), bgs=(QUIET,))
            span = HOT["hot_window"][1] - HOT["hot_window"][0]
            frac = added * span / (added * span + QUIET * T)
            amplitudes[(QUIET + added) / QUIET] = (res, frac)
        hi = 13.0 * QUIET
        slow = {"steady, quiet": nulls,
                "rising 3× over\n45 min, quiet": run_set(pool, dict(n_total=0, ramp=3.0), bgs=(QUIET,)),
                "steady,\n13× quiet": run_set(pool, dict(n_total=0), bgs=(hi,)),
                "rising 3× over\n45 min, 13× quiet": run_set(pool, dict(n_total=0, ramp=3.0), bgs=(hi,))}
        groups = {f"{n} moments\nquiet": run_set(pool, dict(mixed=False, pairs=0, n_total=n), bgs=(QUIET,))
                  for n in (15, 6, 3)}
        groups["15 moments\n¼ quiet"] = run_set(pool, dict(mixed=False, pairs=0), bgs=(QUIET / 4,))
        groups["15 moments\nbusy"] = run_set(pool, dict(mixed=False, pairs=0), bgs=(BUSY,))
    written = []
    for num, fn in (("1", lambda: figure1(a.out, a.date)), ("2", lambda: figure2(a.out, a.date)),
                    ("3", lambda: figure3(a.out, a.date, mixed, one_size, bench_cal)),
                    ("4", lambda: figure4(a.out, a.date, sets)),
                    ("5", lambda: figure5(a.out, a.date, quiet_run, durations, amplitudes, nulls, slow)),
                    ("6", lambda: figure6(a.out, a.date, groups))):
        fname, stats = fn()
        written.append(fname)
        record["figures"][num] = dict(file=fname, numbers=stats)
        print(f"figure {num}: {fname}", file=sys.stderr)
    (a.out / "numbers.json").write_text(json.dumps(record, indent=1, default=float))
    written.append("numbers.json")
    if a.also:
        for f in written:
            shutil.copy2(a.out / f, HERE / f)
    print(json.dumps(record["figures"], indent=1, default=float))


if __name__ == "__main__":
    main()
