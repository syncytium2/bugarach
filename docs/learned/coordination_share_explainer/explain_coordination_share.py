"""Five figures explaining ``tools/measure_coordination_rates.py``: what share of calcium events
are coordinated, measured without defining an event. For readers who are not math-oriented.

Every figure is drawn from synthetic recordings made here, with a known answer. **No real
recording is read.** The default dataset is under a contamination stop (2026-10-05) and the
cross-cell artifact it carries is the kind this statistic counts, so the real numbers wait for
the producer's corrected export.

**The recordings are this page's own, and temporary** (Tony, 2026-10-14): the fast bench's cells,
background and planted moments (``bugarach.bench``: 32 cells, 45 minutes, 15 moments, 5 at each
of three participant counts), but placed on a gap schedule the bench does not have. Every
recording in the main set holds **2 close pairs** (moments 2 s apart), **2 medium pairs** (10 to
20 s apart) and **7 single moments**, every pair and single at least 120 s from the next. The
bench is not changed. ``simulate.simulate_coordination`` has no way to set a gap schedule, which
is why the planting is written out here; everything that estimates is imported from the tool.

Run: python docs/learned/coordination_share_explainer/explain_coordination_share.py [--also]
  Writes to <darkroom>/bugarach/2026-10-14-coordination-share-explainer/; ``--also`` writes the
  repo copy beside this script.
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

DT = mcr.DT
T = float(bench.BENCH_RECORDING["duration_sec"])          # 2700 s
N = int(bench.BENCH_RECORDING["n_roi"])                    # 32 cells
LEVELS = tuple(bench.BENCH_RECORDING["participation"])     # share of cells joining, 3 levels
PER_LEVEL = int(bench.BENCH_RECORDING["n_per_level"][0])   # 5 moments at each level
SHAPE = float(bench.BENCH_RECORDING["bg_rate_shape"])      # how unequal the cells' rates are
JITTER = mcr.CAL_JITTER["bugarach.bench"]                  # 0.106 s, the measured fast jitter
QUIET = float(bench.REGIMES["baseline_quiet"]["bg_rate_hz"])
BUSY = float(bench.REGIMES["baseline_busy"]["bg_rate_hz"])
SEEDS = tuple(range(1, 25))                                # 24 per background, as the tool's
SLOT_SEP = 120.0                                           # s, the bench's spacing
MARGIN = 30.0                                              # s, kept clear at each end
CLOSE_GAP = 2.0
MEDIUM_GAPS = (10.0, 20.0)
PROBE_HZ = 0.127                                           # the bench probe, CAL_NO_PROBE
STRETCH = 300.0

SCHEDULES = {
    # name: (close pairs, medium pairs). Every other moment is single.
    "mixed": (2, 2),
    "120 s only": (0, 0),
    "close pairs": (2, 0),
    "medium pairs": (0, 2),
}

BLUE, ORANGE, AQUA = "#2a78d6", "#eb6834", "#1baf7a"      # dataviz slots 1-3, fixed order
INK, MUTED, GRID = "#0b0b0b", "#52514e", "#d9d8d4"
GAP_COLOUR = {"close": BLUE, "medium": ORANGE, "single": AQUA}
SET_COLOUR = {"mixed": INK, "close pairs": BLUE, "medium pairs": ORANGE, "120 s only": AQUA}

plt.rcParams.update({"font.size": 10, "axes.spines.top": False, "axes.spines.right": False,
                     "axes.edgecolor": MUTED, "xtick.color": MUTED, "ytick.color": MUTED,
                     "axes.labelcolor": INK})


# ---------------------------------------------------------------- the synthetic recordings

def schedule(rng, n_close: int, n_medium: int, n_total: int = len(LEVELS) * PER_LEVEL):
    """Moment times (s) and each one's gap type. Pairs and singles are slots; slot starts sit
    at least SLOT_SEP + the slot's own span apart, so every gap between slots is >= 120 s."""
    n_single = n_total - 2 * (n_close + n_medium)
    kinds = ["close"] * n_close + ["medium"] * n_medium + ["single"] * n_single
    rng.shuffle(kinds)
    spans = [CLOSE_GAP if k == "close" else rng.uniform(*MEDIUM_GAPS) if k == "medium" else 0.0
             for k in kinds]
    need = sum(spans) + SLOT_SEP * (len(kinds) - 1)
    slack = T - 2 * MARGIN - need
    assert slack > 0, "the schedule does not fit in the recording"
    # Spread the slack at random between slots, so slot positions vary by seed.
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


def recording(seed: int, bg_hz: float, n_close=2, n_medium=2, planted=True,
              stretch_hz=0.0, ramp=1.0, n_total=len(LEVELS) * PER_LEVEL):
    """Onset frames per cell, the moments (times, gap types, participant counts) and the count
    of planted onsets that survived frame rounding. ``stretch_hz``: every cell's rate raised to
    that over one 300 s stretch. ``ramp``: the background rises linearly to ``ramp`` times its
    start over the recording (mean kept at ``bg_hz``)."""
    rng = np.random.RandomState(seed)
    L = int(round(T / DT))
    rates = rng.gamma(SHAPE, bg_hz / SHAPE, N)
    cells = []
    for r in rates:
        if ramp == 1.0:
            bg = rng.uniform(0, T, rng.poisson(r * T))
        else:   # thinning: density rises from a to a*ramp, mean r
            a = 2 * r / (1 + ramp)
            cand = rng.uniform(0, T, rng.poisson(a * ramp * T))
            bg = cand[rng.rand(cand.size) < (1 + (ramp - 1) * cand / T) / ramp]
        cells.append([bg])
    if stretch_hz > 0:
        s0 = rng.uniform(MARGIN, T - MARGIN - STRETCH)
        for c, r in zip(cells, rates):
            add = max(stretch_hz - r, 0.0)
            c.append(rng.uniform(s0, s0 + STRETCH, rng.poisson(add * STRETCH)))
    times, gap = schedule(rng, n_close, n_medium, n_total) if planted else (np.zeros(0), [])
    ks = np.repeat([int(round(p * N)) for p in LEVELS], PER_LEVEL)
    rng.shuffle(ks)
    ks = ks[:times.size]
    planted_onsets = [np.zeros(0)] * N
    who = [[] for _ in range(N)]
    for t, k in zip(times, ks):
        for c in rng.choice(N, k, replace=False):
            who[c].append(t + rng.randn() * JITTER)
    for i in range(N):
        planted_onsets[i] = np.asarray(who[i])
    trains, n_bg, n_pl = [], 0, 0
    for i in range(N):
        bgf = np.round(np.concatenate(cells[i]) / DT).astype(int)
        plf = np.round(planted_onsets[i] / DT).astype(int)
        bgf, plf = bgf[(bgf >= 0) & (bgf < L)], plf[(plf >= 0) & (plf < L)]
        plf = np.unique(plf)
        bgf = np.setdiff1d(np.unique(bgf), plf)
        trains.append(np.sort(np.concatenate([bgf, plf])))
        n_bg += bgf.size
        n_pl += plf.size
    truth = dict(share=n_pl / max(n_bg + n_pl, 1), events=n_bg + n_pl, moments=int(times.size),
                 k=float(ks.mean()) if ks.size else float("nan"), lam=times.size / T)
    return dict(trains=trains, L=L, times=times, gap=gap, ks=ks, truth=truth)


def _measure(args):
    seed, bg, kw = args
    rec = recording(seed, bg, **kw)
    m = mcr.measure(rec["trains"], rec["L"], np.random.RandomState(seed))
    return m, rec["truth"]


def run_set(pool, kw, bgs=(QUIET, BUSY), seeds=SEEDS):
    jobs = [(s, bg, kw) for bg in bgs for s in seeds]
    return list(pool.map(_measure, jobs))


def recovered(results, w, model):
    """Each recording's recovered share of events, the way the tool computes it: f3/f2 pooled
    over the set, then each recording's own f2 and rate."""
    recs = [m for m, _ in results]
    pr = mcr.per_recording(recs, w, model)
    return np.array([x["share"] / m["rate"] for x, m in zip(pr, recs)])


def recovered_moments(results, w, model):
    """Each recording's participants per moment (k) and moments per second (λ), as the tool
    computes them."""
    pr = mcr.per_recording([m for m, _ in results], w, model)
    return np.array([x["k"] for x in pr]), np.array([x["lam"] for x in pr])


def planted(results, key="share"):
    return np.array([t[key] for _, t in results])


# ---------------------------------------------------------------- figure helpers

def minutes(t):
    m, s = divmod(int(round(t)), 60)
    return f"{m}m" if s == 0 else (f"{s}s" if m == 0 else f"{m}m{s:02d}s")


def time_axis(ax, t0, t1, step=30):
    ticks = np.arange(np.ceil(t0 / step) * step, t1 + 1e-9, step)
    ax.set_xticks(ticks, [minutes(t) for t in ticks])
    ax.set_xlim(t0, t1)


def heading(ax, letter):
    ax.text(-0.08, 1.04, letter, transform=ax.transAxes, fontsize=14, fontweight="bold")


def artifact_name(topic: str, ext: str) -> str:
    out = subprocess.run([sys.executable, str(REPO / "tools" / "naming" / "artifact_name.py"),
                          "build", "--type", "explainer", "--topic", topic, "--ext", ext,
                          "--date", "20261014"], capture_output=True, text=True, check=True)
    return out.stdout.strip()


# ---------------------------------------------------------------- the figures

def figure1(out: Path):
    """The recording, the count in 1 s windows, and why no event needs defining."""
    # Show the 6 minutes, over the quiet recordings, where a close pair and a medium pair are
    # both in view and their moments are largest, so the pairs can be seen in the raster.
    best = (-1, None, 0.0)
    for seed in SEEDS:
        r = recording(seed, QUIET)
        for start in np.arange(0, T - 360, 10.0):
            sel = (r["times"] >= start + 10) & (r["times"] <= start + 350)
            kinds = {g for g, s in zip(r["gap"], sel) if s}
            if not {"close", "medium"} <= kinds:
                continue
            score = sum(k for g, k, s in zip(r["gap"], r["ks"], sel) if s and g != "single")
            if score > best[0]:
                best = (score, seed, float(start))
    _, seed, t0 = best
    rec = recording(seed, QUIET)
    t1 = t0 + 360.0
    fig = plt.figure(figsize=(12, 7.2))
    gs = fig.add_gridspec(3, 1, height_ratios=[0.5, 6, 2.2], hspace=0.08)
    lane = fig.add_subplot(gs[0])
    for kind, c in GAP_COLOUR.items():
        sel = np.array([g == kind for g in rec["gap"]], bool) & (rec["times"] >= t0) \
            & (rec["times"] <= t1)
        lane.scatter(rec["times"][sel], np.zeros(sel.sum()), marker="v", s=60, color=c,
                     label={"close": "moment in a close pair (2 s)",
                            "medium": "moment in a medium pair (10 to 20 s)",
                            "single": "single moment (120 s or more from the next)"}[kind])
    lane.set_xlim(t0, t1)
    lane.set_ylim(-0.6, 0.6)
    lane.set_yticks([0], ["planted"])
    lane.tick_params(axis="y", length=0)
    lane.tick_params(axis="x", bottom=False, labelbottom=False)
    for s in lane.spines.values():
        s.set_visible(False)
    lane.legend(loc="lower left", bbox_to_anchor=(0, 1.0), ncol=3, frameon=False, fontsize=9)
    ax = fig.add_subplot(gs[1], sharex=lane)
    for r, tr in enumerate(rec["trains"]):
        on = tr * DT
        on = on[(on >= t0) & (on <= t1)]
        ax.vlines(on, r + 0.6, r + 1.4, color=INK, lw=1.2)
    ax.set_ylim(N + 0.7, 0.3)
    ax.set_yticks([1, 8, 16, 24, 32])
    ax.set_ylabel(f"cell · {N} cells")
    ax.tick_params(labelbottom=False)
    cx = fig.add_subplot(gs[2], sharex=lane)
    allf = np.concatenate(rec["trains"]) * DT
    edges = np.arange(t0, t1 + 1, 1.0)
    X = np.histogram(allf, edges)[0]
    cx.bar(edges[:-1] + 0.5, X, width=0.8, color=MUTED)
    cx.set_ylabel("onsets per\n1 s window (X)")
    cx.yaxis.set_major_locator(matplotlib.ticker.MaxNLocator(integer=True))
    time_axis(cx, t0, t1)
    cx.set_xlabel("time in the recording")
    path = out / artifact_name("coordinated-share-fig1-the-count", "png")
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    return path.name, dict(window=[t0, t1], seed=seed, background_hz=QUIET)


def figure2(out: Path):
    """Same mean, different spread: the real count against one rigidly shifted copy."""
    rec = recording(3, BUSY)
    L, wf = rec["L"], int(round(1.0 / DT))
    rng = np.random.RandomState(11)
    sur = mcr.shifted(rec["trains"], L, 2 * wf, rng)

    def counts(trains):
        allf = np.concatenate(trains)
        return np.bincount(allf // wf, minlength=L // wf)[:L // wf]

    Xr, Xs = counts(rec["trains"]), counts(sur)
    f2r, f3r = mcr.population_cumulants(rec["trains"], L, wf)
    surs = np.array([mcr.population_cumulants(mcr.shifted(rec["trains"], L, 2 * wf, rng), L, wf)
                     for _ in range(mcr.N_SURR)])
    fig, (axA, axB) = plt.subplots(1, 2, figsize=(12, 4.4), gridspec_kw=dict(wspace=0.3))
    top = int(max(Xr.max(), Xs.max()))
    bins = np.arange(-0.5, top + 1.5)
    hr, hs = np.histogram(Xr, bins)[0], np.histogram(Xs, bins)[0]
    x = np.arange(top + 1)
    axA.bar(x - 0.2, hs, width=0.38, color=AQUA, label=f"shifted copy · mean {Xs.mean():.2f} onsets")
    axA.bar(x + 0.2, hr, width=0.38, color=INK, label=f"recording · mean {Xr.mean():.2f} onsets")
    axA.set_yscale("log")
    axA.set_xlabel("onsets in one 1 s window (X)")
    axA.set_ylabel(f"1 s windows (count, of {Xr.size} windows)")
    axA.legend(frameon=False, fontsize=9)
    axA.xaxis.set_major_locator(matplotlib.ticker.MaxNLocator(integer=True))
    heading(axA, "A")
    labels = ["f₂ (pairs beyond chance)", "f₃ (triples beyond chance)"]
    for i, (real, s) in enumerate(((f2r, surs[:, 0]), (f3r, surs[:, 1]))):
        axB.scatter(np.full(s.size, i - 0.12) + rng.uniform(-0.04, 0.04, s.size), s, s=18,
                    color=AQUA, label="each of 20 shifted copies" if i == 0 else None)
        axB.scatter([i + 0.12], [real], s=70, color=INK, marker="D",
                    label="the recording" if i == 0 else None)
        axB.annotate("", xy=(i + 0.12, real), xytext=(i + 0.12, s.mean()),
                     arrowprops=dict(arrowstyle="<->", color=MUTED, lw=1.2))
        axB.text(i + 0.18, (real + s.mean()) / 2, f"excess\n{real - s.mean():.3f}",
                 fontsize=9, va="center")
    axB.axhline(0, color=GRID, lw=1)
    axB.set_xticks([0, 1], labels)
    axB.set_xlim(-0.5, 1.7)
    axB.set_ylabel("factorial cumulant (per 1 s window)")
    axB.legend(frameon=False, fontsize=9, loc="upper left")
    heading(axB, "B")
    path = out / artifact_name("coordinated-share-fig2-wider-spread", "png")
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    return path.name, dict(mean_real=float(Xr.mean()), mean_shifted=float(Xs.mean()),
                           f2=f2r, f3=f3r, f2_shifted_mean=float(surs[:, 0].mean()),
                           f3_shifted_mean=float(surs[:, 1].mean()))


def figure3(out: Path, mixed):
    """Planted against recovered, both models, the mixed-gap set at 1 s."""
    p = planted(mixed)
    fig, ax = plt.subplots(figsize=(6.6, 6.0))
    lim = max(p.max(), 0.4) * 1.15
    xs = np.linspace(0, lim, 50)
    ax.fill_between(xs, xs * (1 - mcr.CAL_TOL), xs * (1 + mcr.CAL_TOL), color=GRID, alpha=0.6,
                    lw=0, label=f"within ±{mcr.CAL_TOL:.0%} of planted (the pass band)")
    ax.plot(xs, xs, color=MUTED, lw=1)
    stats = {}
    for model, face in (("fixed", INK), ("binomial", "none")):
        r = recovered(mixed, 1.0, model)
        err = float(np.nanmedian(r / p - 1))
        stats[model] = err
        ax.scatter(p, r, s=34, facecolor=face, edgecolor=INK, lw=1.1,
                   label=f"{model} model · median error {err:+.0%}"
                   + (" (adopted)" if model == mcr.ADOPTED_MODEL else ""))
    ax.set_xlim(0, lim)
    ax.set_ylim(0, lim)
    ax.set_xlabel("planted share of events that are coordinated")
    ax.set_ylabel("recovered share of events")
    ax.xaxis.set_major_formatter(matplotlib.ticker.PercentFormatter(1.0, decimals=0))
    ax.yaxis.set_major_formatter(matplotlib.ticker.PercentFormatter(1.0, decimals=0))
    ax.legend(frameon=False, fontsize=9, loc="upper left")
    path = out / artifact_name("coordinated-share-fig3-planted-vs-recovered", "png")
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    return path.name, dict(median_error=stats, recordings=len(mixed),
                           planted_share_range=[float(p.min()), float(p.max())])


def figure4(out: Path, sets):
    """Window and spacing: median error of the recovered share, per gap schedule and window."""
    model = mcr.ADOPTED_MODEL
    fig, axes = plt.subplots(1, 3, figsize=(13, 4.4), sharey=True, gridspec_kw=dict(wspace=0.08))
    quantities = (("share", "share of events coordinated"), ("k", "participants per moment (k)"),
                  ("lam", "moments per minute (λ)"))
    table = {}
    for ax, (key, what), letter in zip(axes, quantities, "ABC"):
        ax.axhspan(-mcr.CAL_TOL, mcr.CAL_TOL, color=GRID, alpha=0.6, lw=0)
        ax.axhline(0, color=MUTED, lw=1)
        for i, (name, res) in enumerate(sets.items()):
            p = planted(res, key)
            meds = []
            for w in mcr.WINDOWS:
                if key == "share":
                    got = recovered(res, w, model)
                else:
                    k, lam = recovered_moments(res, w, model)
                    got = k if key == "k" else lam
                meds.append(float(np.nanmedian(got / p - 1)))
                table.setdefault(name, {}).setdefault(key, {})[str(w)] = meds[-1]
                if key == "share":
                    table[name].setdefault("share_binomial", {})[str(w)] = float(
                        np.nanmedian(recovered(res, w, "binomial") / p - 1))
            x = np.arange(len(mcr.WINDOWS)) + (i - 1.5) * 0.06
            ax.plot(x, meds, color=SET_COLOUR[name], lw=2, marker="o", ms=8, label=name)
        ax.set_xticks(range(len(mcr.WINDOWS)), [f"{w:.0f} s" for w in mcr.WINDOWS])
        ax.set_xlabel(f"window w · {what}")
        ax.yaxis.set_major_formatter(matplotlib.ticker.PercentFormatter(1.0, decimals=0))
        heading(ax, letter)
    axes[0].set_ylabel(f"recovered ÷ planted − 1, {model} model\n(median over 48 recordings)")
    axes[-1].legend(frameon=False, fontsize=9, title="gap schedule", title_fontsize=9,
                    loc="upper left", bbox_to_anchor=(1.02, 1.0))
    path = out / artifact_name("coordinated-share-fig4-window-and-spacing", "png")
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    return path.name, table


def figure5(out: Path, busy_stretch, ramp, null, few, low):
    """What it cannot see: a field-wide busy stretch and a slow rise, with nothing planted; and
    how far one recording's own answer strays when it holds few shared moments."""
    fig, (axA, axB) = plt.subplots(1, 2, figsize=(13, 4.6), gridspec_kw=dict(wspace=0.45))
    rows = [("nothing planted,\nsteady background", null),
            (f"nothing planted, one {STRETCH / 60:.0f}-minute stretch\nat {PROBE_HZ} onsets per "
             "second per cell", busy_stretch),
            ("nothing planted, background\nrising 3× over 45 minutes", ramp)]
    a_stats = {}
    for i, (label, res) in enumerate(rows):
        r = recovered(res, 1.0, mcr.ADOPTED_MODEL)
        ok = np.isfinite(r)
        a_stats[label.replace("\n", " ")] = dict(
            recordings=int(r.size), answered=int(ok.sum()),
            median=float(np.median(r[ok])) if ok.any() else None,
            max=float(r[ok].max()) if ok.any() else None)
        if ok.any():
            axA.scatter(r[ok], np.full(ok.sum(), i)
                        + np.random.RandomState(i).uniform(-0.15, 0.15, ok.sum()), s=16, color=INK)
            axA.text(r[ok].max() + 0.003, i, f"median {np.median(r[ok]):.1%}", va="center",
                     fontsize=9)
        else:
            axA.text(0.002, i, f"no coordination reported in any of {r.size} recordings",
                     va="center", fontsize=9, color=MUTED)
    axA.set_yticks(range(len(rows)), [r[0] for r in rows])
    axA.set_ylim(len(rows) - 0.5, -0.5)
    axA.axvline(0, color=MUTED, lw=1)
    axA.set_xlim(-0.003, 0.075)
    axA.set_xlabel(f"share of events reported coordinated\n({mcr.ADOPTED_MODEL} model, 1 s window)")
    axA.xaxis.set_major_formatter(matplotlib.ticker.PercentFormatter(1.0, decimals=0))
    heading(axA, "A")
    b_stats = {}
    for j, (n_mom, res) in enumerate(few.items()):
        p = planted(res)
        recs = [m for m, _ in res]
        own, none = [], 0
        for m, pp in zip(recs, p):
            c = m["cum"]["1.0"]
            s = mcr.solve(c["f2"], c["f3"], m["N"], 1.0, mcr.ADOPTED_MODEL)["share"]
            if np.isfinite(s):
                own.append(s / m["rate"] / pp)
            else:
                none += 1
        pooled = recovered(res, 1.0, mcr.ADOPTED_MODEL) / p
        axB.scatter(np.full(len(own), j) + np.random.RandomState(j).uniform(-0.12, 0.12, len(own)),
                    own, s=16, color=INK, label="each recording on its own" if j == 0 else None)
        axB.scatter([j + 0.3], [np.nanmedian(pooled)], s=80, marker="D", facecolor="none",
                    edgecolor=INK, lw=1.4,
                    label="f₃/f₂ pooled over the 24 recordings, as the tool does (median)"
                    if j == 0 else None)
        b_stats[f"{n_mom} moments"] = dict(
            recordings=len(recs), no_answer=none,
            median_rate_hz=float(np.median([m["rate"] for m in recs])),
            own_q10=float(np.percentile(own, 10)) if own else None,
            own_median=float(np.median(own)) if own else None,
            own_q90=float(np.percentile(own, 90)) if own else None,
            pooled_median=float(np.nanmedian(pooled)))
    axB.axhline(1, color=MUTED, lw=1)
    axB.set_xticks(range(len(few)), [f"{n} moments" for n in few])
    axB.set_xlim(-0.5, len(few) - 0.3)
    axB.set_ylim(0, None)
    axB.set_xlabel("shared moments planted in a 45-minute recording")
    axB.set_ylabel("answer ÷ planted share")
    axB.legend(frameon=False, fontsize=8, loc="upper left")
    heading(axB, "B")
    b_stats["background lowered, 15 moments"] = {
        f"{s}x quiet": dict(pooled_median=float(np.nanmedian(
            recovered(res, 1.0, mcr.ADOPTED_MODEL) / planted(res))),
            median_rate_hz=float(np.median([m["rate"] for m, _ in res])))
        for s, res in low.items()}
    path = out / artifact_name("coordinated-share-fig5-blind-spots", "png")
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    return path.name, dict(A=a_stats, B=b_stats)


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--out", type=Path, default=None,
                    help="default: <darkroom>/bugarach/2026-10-14-coordination-share-explainer")
    ap.add_argument("--also", action="store_true", help="also write the repo copy beside this script")
    ap.add_argument("--jobs", type=int, default=8)
    a = ap.parse_args()
    if a.out is None:
        from bugarach.paths import darkroom
        a.out = darkroom() / "2026-10-14-coordination-share-explainer"
    a.out.mkdir(parents=True, exist_ok=True)
    record = dict(note="synthetic recordings only; no real recording read",
                  cells=N, duration_sec=T, levels=list(LEVELS), per_level=PER_LEVEL,
                  jitter_sec=JITTER, quiet_hz=QUIET, busy_hz=BUSY, seeds=len(SEEDS),
                  schedules={k: dict(close_pairs=v[0], medium_pairs=v[1])
                             for k, v in SCHEDULES.items()}, figures={})
    with ProcessPoolExecutor(a.jobs) as pool:
        sets = {name: run_set(pool, dict(n_close=c, n_medium=m))
                for name, (c, m) in SCHEDULES.items()}
        null = run_set(pool, dict(planted=False), bgs=(QUIET,))
        stretch = run_set(pool, dict(planted=False, stretch_hz=PROBE_HZ), bgs=(QUIET,))
        ramp = run_set(pool, dict(planted=False, ramp=3.0), bgs=(QUIET,))
        low = {s: run_set(pool, dict(), bgs=(QUIET * s,)) for s in (1.0, 0.5, 0.25)}
        few = {n: run_set(pool, dict(n_close=0, n_medium=0, n_total=n), bgs=(QUIET,))
               for n in (15, 6, 3)}
    for name, fn in (("1", lambda: figure1(a.out)), ("2", lambda: figure2(a.out)),
                     ("3", lambda: figure3(a.out, sets["mixed"])),
                     ("4", lambda: figure4(a.out, sets)),
                     ("5", lambda: figure5(a.out, stretch, ramp, null, few, low))):
        fname, stats = fn()
        record["figures"][name] = dict(file=fname, numbers=stats)
        print(f"figure {name}: {fname}", file=sys.stderr)
    (a.out / "numbers.json").write_text(json.dumps(record, indent=1, default=float))
    if a.also:
        for f in list(a.out.glob("*.png")) + [a.out / "numbers.json"]:
            shutil.copy2(f, HERE / f.name)
    print(json.dumps(record["figures"], indent=1, default=float))


if __name__ == "__main__":
    main()
