"""The three opening figures of Chapter 1: the problem, three simple detectors, and the tools.

Tony's first read of the chapter (2026-11-13) asked for an opening a reader outside the field can
follow: lead with a picture of coordinated events on a noisy background; walk through the simplest
detector (count cells in fixed bins), then a sliding window, then an adaptive threshold (CFAR), and
show where each succeeds and fails on one raster built for the purpose; then introduce the tools
that characterize coordination, the correlogram's half-width at half maximum first, on two sets,
one sharp and one with much jitter. These are those figures.

  problem    background alone, coordinated events alone, and the two together (Figure 1.1)
  detectors  fixed bins, a sliding window and CFAR on one designed recording (Figure 1.2)
  twosets    a sharp set and a jittered set: correlogram and HWHM, pair counts against window
             width, and the count of active cells per bin against chance (Figure 1.3)

**What is simulated, and by what.** Figures 1.1 and 1.2 need events at chosen times, which the
repository's generator does not take, so ``plant`` below writes the chapter's model out in a few
lines: each cell has Poisson background onsets; each event is joined by k cells chosen at random,
each onset the event time plus Gaussian jitter of SD sigma; every onset is rounded to the 0.1 s
frame, one onset per cell per frame. Figure 1.3 uses the repository's generator
(``bugarach.simulate.simulate_coordination``) at the first experiment's settings, so its sets are
the chapter's own.

**What is computed, and by what.** The fixed-bin and sliding detectors are the repository's
``count_detect`` and ``count_sliding_detect``. The CFAR detector is written here (no coded
detector in the repository is CFAR in this simple form): its threshold at each instant is the
smallest count that background alone would reach at most once per hour, computed from a local
estimate of the background rate that leaves out a guard band around the instant under test. The
chance rate is the binomial up-crossing rate of the sliding count, and ``main`` asserts that it
gives the count detector's floors quoted in the chapter (6 cells at 0.01 Hz, 12 at 0.05 Hz). The
excess pair counts are the coordination-rates tool's own (``measure_coordination_rates.
excess_cumulants``) and their prediction is ``theory.predicted_excess_cumulants``. The correlogram
is counted here, as onset pairs between different cells per lag of one frame over the count
expected from the cells' own totals (Perkel, Gerstein & Moore 1967), which is the statistic of
``tools/measure_jitter_correlogram.py`` before its calibration step.

Every number the chapter quotes from these figures is printed by this script.

    PYTHONPATH=src python docs/dissertation/figures/ch1_intro_figures.py [--out DIR] [--only ...]
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import ch1_new_figures as base  # noqa: E402  (helpers, style, naming; puts src, tools on the path)
from ch1_new_figures import letter, minutes_axis, plt, save, style  # noqa: E402
from matplotlib.lines import Line2D  # noqa: E402
from scipy import stats  # noqa: E402

import measure_coordination_rates as mcr  # noqa: E402  (tools/)
import theory  # noqa: E402  (docs/learned/synthetic_validation/)

DATE = "20261113"
DT = 0.1                     # s, the frame
N = 33                       # cells
INK = base.INK
HIT, MISS, FALSE = "#1a9850", "#d73027", "#f08c00"   # verdict colours; the shape is always ▼
SET_COL = {"sharp": "#2a78d6", "jittered": "#d0453b"}


def name(topic, type_):
    from naming import artifact_name
    return artifact_name.build(artifact_name.load_codes(), source="synth", type=type_,
                               form="plot", topic=topic, ext="png", date=DATE)


# --------------------------------------------------------------------------- the model, written out

def plant(T, events, bg, rng, n=N):
    """Onset trains (s) for ``n`` cells over ``T`` s.

    ``events``: (time, k, sigma) per coordinated event. ``bg``: a function of time giving the
    background rate per cell (Hz); it is sampled by thinning against its maximum. Returns the
    trains and, per event, the cells that joined it."""
    grid = np.arange(0.0, T, DT)
    bmax = max(bg(t) for t in grid)
    trains = [[] for _ in range(n)]
    for c in range(n):
        m = rng.poisson(bmax * T)
        t = rng.uniform(0, T, m)
        keep = rng.uniform(0, bmax, m) < np.array([bg(x) for x in t])
        trains[c].extend(t[keep])
    members = []
    for (te, k, sg) in events:
        cells = rng.choice(n, k, replace=False)
        members.append(cells)
        for c in cells:
            trains[c].append(te + sg * rng.standard_normal())
    out = []
    for tr in trains:
        f = np.unique(np.round(np.asarray(tr) / DT).astype(int))
        f = f[(f >= 0) & (f < int(round(T / DT)))]
        out.append(f * DT)
    return out, members


def raster(ax, trains, t0, t1, ms=2.2):
    """One ink, one mark per onset, nothing else on it (CLAUDE.md)."""
    for r, tr in enumerate(trains):
        x = tr[(tr >= t0) & (tr < t1)]
        ax.plot(x, np.full(x.size, r + 1), "|", color=INK, ms=ms, mew=1.1)
    ax.set_ylim(0.3, len(trains) + 0.7)
    ax.set_yticks([1, len(trains)])
    for sp in ("top", "right"):
        ax.spines[sp].set_visible(False)


def lane(ax, label):
    ax.set_ylim(0, 1)
    ax.set_yticks([])
    ax.set_ylabel(label, rotation=0, ha="right", va="center", fontsize=10.5)
    for sp in ("top", "right", "left", "bottom"):
        ax.spines[sp].set_visible(False)
    ax.tick_params(axis="x", length=0, labelbottom=False)


# --------------------------------------------------------------------------- chance and CFAR

def chance_calls_per_hour(K, b, w=2.0, n=N):
    """Rate per hour at which background alone lifts the count of distinct cells active in a
    sliding window of ``w`` s to ``K``: the count sits at K - 1 with binomial probability, and one
    of the n - K + 1 inactive cells then has an onset, at rate b each (the scan-statistic
    up-crossing approximation; Poisson cells of equal rate)."""
    p = 1 - np.exp(-b * w)
    return 3600.0 * stats.binom.pmf(K - 1, n, p) * (n - K + 1) * b


def chance_floor(b, budget=1.0, w=2.0, n=N):
    """Smallest K >= 3 at which chance gives at most ``budget`` calls per hour (ADR-0008's rule,
    with the analytic rate in place of the repository's simulated null)."""
    for K in range(3, n + 1):
        if chance_calls_per_hour(K, b, w, n) <= budget:
            return K
    return n + 1


def sliding_count(trains, grid, w=2.0):
    """Distinct cells with an onset in (t - w, t], at each grid time."""
    S = np.zeros(grid.size, int)
    for tr in trains:
        if tr.size == 0:
            continue
        i = np.searchsorted(tr, grid, side="right")       # onsets <= t
        j = np.searchsorted(tr, grid - w + 1e-9, side="right")  # onsets <= t - w
        S += (i - j) > 0
    return S


def local_rate(trains, grid, T, ref=30.0, guard=5.0):
    """Background rate per cell from the onsets in two reference windows of ``ref`` s on either
    side of each instant, leaving out ``guard`` s on each side (the guard band), so an event at
    the instant under test cannot raise its own threshold."""
    allt = np.sort(np.concatenate(trains))
    b = np.zeros(grid.size)
    for i, t in enumerate(grid):
        lo1, hi1 = max(0.0, t - guard - ref), max(0.0, t - guard)
        lo2, hi2 = min(T, t + guard), min(T, t + guard + ref)
        span = (hi1 - lo1) + (hi2 - lo2)
        cnt = (np.searchsorted(allt, hi1) - np.searchsorted(allt, lo1)
               + np.searchsorted(allt, hi2) - np.searchsorted(allt, lo2))
        b[i] = cnt / (len(trains) * span)
    return b


def runs_to_calls(mask, grid, w, merge_gap):
    """Called runs of a sliding count as (start, end) spans in s, joined across gaps of at most
    ``merge_gap``. A run of the trailing window (t - w, t] covers onsets from start - w."""
    calls = []
    i, n = 0, mask.size
    while i < n:
        if mask[i]:
            j = i
            while j + 1 < n and mask[j + 1]:
                j += 1
            s, e = grid[i] - w, grid[j]
            if calls and s - calls[-1][1] <= merge_gap:
                calls[-1] = (calls[-1][0], e)
            else:
                calls.append((s, e))
            i = j + 1
        else:
            i += 1
    return calls


def score(calls, ev_times, tol=1.0):
    """Hits, misses and false calls. A planted event is found when a call's span, widened by
    ``tol`` s, contains it; one call finds at most one event, so a call over two events finds
    one and the other is missed (merged)."""
    used, hit, miss = set(), [], []
    for te in ev_times:
        for ci, (s, e) in enumerate(calls):
            if ci not in used and s - tol <= te <= e + tol:
                used.add(ci)
                hit.append(te)
                break
        else:
            miss.append(te)
    false = [0.5 * (s + e) for ci, (s, e) in enumerate(calls) if ci not in used]
    return hit, miss, false


# --------------------------------------------------------------------------- Figure 1.1

PROBLEM = dict(T=120.0, b=0.05, k=10, sigma=0.2, times=(17.0, 46.0, 78.0, 104.0), seed=3)


def fig_problem(out):
    d = PROBLEM
    rng = np.random.RandomState(d["seed"])
    evs = [(t, d["k"], d["sigma"]) for t in d["times"]]
    # one draw, split into its two parts so the panels show the same onsets
    bg_tr, _ = plant(d["T"], [], lambda t: d["b"], rng)
    ev_tr, _ = plant(d["T"], evs, lambda t: 0.0 + 1e-12, rng)
    both = [np.unique(np.round(np.concatenate([a, c]) / DT).astype(int)) * DT
            for a, c in zip(bg_tr, ev_tr)]

    fig = plt.figure(figsize=(11, 10.2))
    gs = fig.add_gridspec(4, 1, height_ratios=[0.35, 2.6, 2.6, 2.6], hspace=0.32,
                          left=0.12, right=0.985, top=0.975, bottom=0.06)
    ln = fig.add_subplot(gs[0])
    axes = [fig.add_subplot(gs[i], sharex=ln) for i in (1, 2, 3)]
    for t in d["times"]:
        ln.plot(t, 0.5, "v", ms=10, color=SET_COL["sharp"])
    lane(ln, "planted\nevents")
    titles = ("background alone", "coordinated events alone", "what the analyst receives")
    for ax, tr, lab, L in zip(axes, (bg_tr, ev_tr, both), titles, "ABC"):
        raster(ax, tr, 0, d["T"])
        ax.set_ylabel(f"{lab}\ncell (of {N})", fontsize=11)
        letter(ax, L, x=-0.075)
        if ax is not axes[-1]:
            ax.tick_params(labelbottom=False)
    minutes_axis(axes[-1], 0, d["T"])
    axes[-1].set_xlabel("time")
    n_bg = sum(t.size for t in bg_tr)
    n_ev = sum(t.size for t in ev_tr)
    print(f"[problem] {n_bg} background onsets, {n_ev} event onsets "
          f"({len(d['times'])} events of {d['k']} cells), {d['T']:.0f} s")
    title = "Coordinated events hidden in a background of independent onsets"
    return save(fig, name("coordinated-events-on-a-noisy-background", "raster"), title, out)


# --------------------------------------------------------------------------- Figure 1.2

DET = dict(T=240.0, b_quiet=0.0096, b_busy=0.05, busy=(120.0, 180.0), w=2.0, merge=3.0,
           K_fixed=6, seed=1000, n_draws=200,
           # an onset rounds into the bin from 46 s when it falls at 45.95 s or later, so an
           # event at 45.95 s is centred on that border after rounding
           events=[(15.0, 12, 0.05, "1"),     # sharp and large
                   (45.95, 7, 0.5, "2"),      # jittered, centred on a fixed-bin border
                   (80.0, 10, 0.1, "3a"),     # two events 3 s apart
                   (83.0, 10, 0.1, "3b"),
                   (150.0, 12, 0.1, "4"),     # inside the busier stretch
                   (210.0, 5, 0.05, "5")])    # one cell below the fixed threshold


def detector_runs(seed):
    from bugarach.detectors.count import count_detect, count_sliding_detect
    d = DET
    rng = np.random.RandomState(seed)
    lo, hi = d["busy"]
    bg = (lambda t: d["b_busy"] if lo <= t < hi else d["b_quiet"])
    evs = [(t, k, s) for t, k, s, _ in d["events"]]
    trains, _ = plant(d["T"], evs, bg, rng)
    ev_t = [e[0] for e in d["events"]]
    grid = np.arange(DT, d["T"] + 1e-9, DT)

    fx = count_detect(trains, (0.0, d["T"]), bin_sec=d["w"], min_rois=d["K_fixed"],
                      merge_gap_sec=d["merge"])
    fx_calls = [(o, o + w) for o, w in zip(fx.onset_sec, fx.width_sec)]
    sl = count_sliding_detect(trains, (0.0, d["T"]), win_sec=d["w"], min_rois=d["K_fixed"],
                              merge_gap_sec=d["merge"])
    sl_calls = [(o, o + w) for o, w in zip(sl.onset_sec, sl.width_sec)]
    S = sliding_count(trains, grid, d["w"])
    b_hat = local_rate(trains, grid, d["T"])
    K_t = np.array([chance_floor(b) for b in b_hat])
    cf_calls = runs_to_calls(S >= K_t, grid, d["w"], d["merge"])
    res = {"fixed": (fx_calls, score(fx_calls, ev_t)),
           "sliding": (sl_calls, score(sl_calls, ev_t)),
           "cfar": (cf_calls, score(cf_calls, ev_t))}
    return trains, grid, fx, S, b_hat, K_t, res


KEYS = ("fixed", "sliding", "cfar")
LABEL = {"fixed": "fixed bins", "sliding": "sliding window", "cfar": "CFAR"}


def outcomes(res):
    """One draw's outcome per detector: whether each vignette was found (event 3 counts as
    found only when both of its events are), and whether there was any false call in the busy
    stretch and in the quiet ones."""
    d = DET
    lo, hi = d["busy"]
    o = {}
    for k in KEYS:
        hit, _, false = res[k][1]
        f = {lab: (t in hit) for t, _, _, lab in d["events"]}
        o[k] = (f["1"], f["2"], f["3a"] and f["3b"], f["4"], f["5"],
                any(lo <= x < hi for x in false), any(not lo <= x < hi for x in false))
    return o


def fig_detectors(out):
    d = DET
    # 1. the rates: n_draws independent draws of the same designed recording
    tally = {k: np.zeros(7) for k in KEYS}
    false_busy = {k: 0 for k in KEYS}
    false_quiet = {k: 0 for k in KEYS}
    per_draw = []
    lo, hi = d["busy"]
    for i in range(d["n_draws"]):
        res = detector_runs(d["seed"] + i)[-1]
        o = outcomes(res)
        per_draw.append(o)
        for k in KEYS:
            tally[k] += np.array(o[k], float)
            false_busy[k] += sum(lo <= x < hi for x in res[k][1][2])
            false_quiet[k] += sum(not lo <= x < hi for x in res[k][1][2])
    share = {k: tally[k] / d["n_draws"] for k in KEYS}
    busy_min = (hi - lo) / 60.0
    quiet_h = (d["T"] - (hi - lo)) / 3600.0
    print(f"[detectors] over {d['n_draws']} draws (seeds {d['seed']}-{d['seed'] + d['n_draws'] - 1}): "
          "share found for events 1, 2, 3 (both), 4, 5; false calls per busy minute; per quiet hour")
    for k in KEYS:
        print(f"[detectors]   {LABEL[k]:15s} " + "  ".join(f"{v:.2f}" for v in share[k][:5])
              + f"   {false_busy[k] / (d['n_draws'] * busy_min):.2f} per min"
              + f"   {false_quiet[k] / (d['n_draws'] * quiet_h):.2f} per h")
    # 2. the draw shown: the first whose every outcome is the most common one
    typical = {k: tuple(v >= 0.5 for v in share[k]) for k in KEYS}
    n_typ = sum(all(o[k] == typical[k] for k in KEYS) for o in per_draw)
    pick = next(i for i, o in enumerate(per_draw) if all(o[k] == typical[k] for k in KEYS))
    seed = d["seed"] + pick
    trains, grid, fx, S, b_hat, K_t, res = detector_runs(seed)
    print(f"[detectors] draw shown: seed {seed}, the first whose every outcome is the most "
          f"common one ({n_typ} of {d['n_draws']} draws are)")

    fig = plt.figure(figsize=(11, 13.2))
    gs = fig.add_gridspec(8, 1, height_ratios=[0.35, 0.45, 0.4, 0.4, 0.4, 3.0, 1.15, 1.15],
                          hspace=0.22, left=0.15, right=0.985, top=0.985, bottom=0.075)
    bgl = fig.add_subplot(gs[0])
    ax = [fig.add_subplot(gs[i], sharex=bgl) for i in range(1, 8)]
    pl, lf, ls_, lc, ras, cnt_fx, cnt_sl = ax

    lo, hi = d["busy"]
    bgl.axvspan(lo, hi, ymin=0.25, ymax=0.75, color="#cfcfcf", lw=0)
    bgl.text(0.5 * (lo + hi), 0.5, f"background {d['b_busy']} Hz per cell", ha="center",
             va="center", fontsize=10)
    bgl.text(3, 0.5, f"background {d['b_quiet']} Hz per cell", ha="left", va="center",
             fontsize=10, color="#555555")
    lane(bgl, "background")
    for t, k, s, lab in d["events"]:
        pl.plot(t, 0.42, "v", ms=10, color=INK)
    # one number per vignette, centred over its events (event 3 is a pair)
    vign = {}
    for t, _, _, lab in d["events"]:
        vign.setdefault(lab[0], []).append(t)
    for lab, ts in vign.items():
        pl.text(np.mean(ts), 0.95, lab, ha="center", va="center", fontsize=10.5,
                fontweight="bold")
    lane(pl, "planted\nevents")
    for a, key, lab in ((lf, "fixed", "fixed\nbins"), (ls_, "sliding", "sliding\nwindow"),
                        (lc, "cfar", "CFAR")):
        hit, miss, false = res[key][1]
        a.plot(hit, [0.5] * len(hit), "v", ms=9, color=HIT, ls="none")
        a.plot(miss, [0.5] * len(miss), "v", ms=9, color=MISS, ls="none")
        a.plot(false, [0.5] * len(false), "v", ms=9, color=FALSE, ls="none")
        lane(a, lab)
    raster(ras, trains, 0, d["T"], ms=2.0)
    ras.set_ylabel(f"cell (of {N})", fontsize=11)
    ras.tick_params(labelbottom=False)

    # the counts each detector thresholds, below the raster
    cnt_fx.bar(fx.ctr, fx.obs, width=d["w"] * 0.92, color="#7a7a7a", lw=0)
    cnt_fx.axhline(d["K_fixed"], color=INK, ls="--", lw=1.1)
    cnt_fx.set_ylabel("cells per\n2 s bin", fontsize=10.5)
    cnt_fx.tick_params(labelbottom=False)
    cnt_sl.step(grid, S, where="post", color="#7a7a7a", lw=1.0)
    cnt_sl.axhline(d["K_fixed"], color=INK, ls="--", lw=1.1)
    cnt_sl.step(grid, K_t, where="post", color="#7b3294", lw=1.6)
    cnt_sl.set_ylabel("cells in sliding\n2 s window", fontsize=10.5)
    for a in (cnt_fx, cnt_sl):
        style(a)
        a.set_ylim(0, 16)
    minutes_axis(cnt_sl, 0, d["T"])
    cnt_sl.set_xlabel("time")
    for a, L in zip((pl, ras, cnt_fx, cnt_sl), "ABCD"):
        letter(a, L, x=-0.1)
    handles = [Line2D([], [], marker="v", color=HIT, ls="none", ms=9, label="found"),
               Line2D([], [], marker="v", color=MISS, ls="none", ms=9, label="missed"),
               Line2D([], [], marker="v", color=FALSE, ls="none", ms=9, label="false call"),
               Line2D([], [], color=INK, ls="--", label=f"fixed threshold, {d['K_fixed']} cells"),
               Line2D([], [], color="#7b3294", lw=1.6, label="CFAR threshold")]
    fig.legend(handles=handles, loc="lower center", ncol=5, frameon=False, fontsize=10.5,
               bbox_to_anchor=(0.56, 0.0))

    for key in res:
        hit, miss, false = res[key][1]
        print(f"[detectors] {key}: {len(res[key][0])} calls; found {len(hit)} of "
              f"{len(d['events'])} planted; false calls {len(false)} at "
              f"{', '.join(f'{x:.0f} s' for x in false) or 'none'}")
    inq = (grid < lo) | (grid >= hi)
    print(f"[detectors] CFAR threshold: {sorted(set(K_t[inq].tolist()))} cells in the quiet "
          f"stretches, {sorted(set(K_t[~inq].tolist()))} in the busy one; local rate "
          f"{np.median(b_hat[inq]):.4f} and {np.median(b_hat[~inq]):.4f} Hz (medians)")
    print(f"[detectors] analytic floor at {d['b_quiet']} Hz: {chance_floor(d['b_quiet'])} cells, "
          f"at {d['b_busy']} Hz: {chance_floor(d['b_busy'])} cells")
    for t, k, s, lab in d["events"]:
        i = np.searchsorted(grid, t)
        print(f"[detectors] event {lab} at {t:.0f} s: k {k}, sigma {s} s; peak sliding count "
              f"{S[max(0, i - 5):i + 25].max()} cells; peak fixed-bin count "
              f"{fx.obs[max(0, int(t // d['w']) - 1):int(t // d['w']) + 2].max()} cells")
    title = "Three simple detectors on one recording: fixed bins, a sliding window and CFAR"
    return save(fig, name("three-simple-detectors-found-and-missed", "raster"), title, out)


# --------------------------------------------------------------------------- Figure 1.3

SETS = dict(k=10, b=0.0096, E=45, T=2700.0, n_rec=10,
            sigma={"sharp": 0.1, "jittered": 0.5}, lag_max=3.0,
            windows=(0.2, 0.5, 1.0, 2.0, 4.0, 8.0), seed0=101)


def _set_recordings(sigma, seeds):
    from bugarach.simulate import simulate_coordination
    d = SETS
    recs = []
    for sd in seeds:
        s, gt = simulate_coordination(duration_sec=d["T"], n_roi=N, bg_rate_hz=d["b"],
                                      participation=(d["k"] / N,), n_per_level=(d["E"],),
                                      jitter_sec=sigma, min_sep_sec=20.0, grid_sec=DT, seed=sd)
        trains = [np.asarray(t, float) for t in next(iter(s.streams.values())).t50rise]
        recs.append((trains, sorted(e.time for e in gt.events)))
    return recs


def correlogram(recs, T, lag_max):
    """Ordered onset pairs between different cells per one-frame lag, pooled over recordings,
    and the count expected from each pair of cells' totals if they were independent."""
    m = int(round(lag_max / DT))
    obs = np.zeros(2 * m + 1)
    exp_ = np.zeros(2 * m + 1)
    for trains, _ in recs:
        fr = [np.round(t / DT).astype(int) for t in trains]
        L = int(round(T / DT))
        cnt = np.array([f.size for f in fr], float)
        R = np.zeros((len(fr), L), np.int8)
        for i, f in enumerate(fr):
            R[i, f[(f >= 0) & (f < L)]] = 1
        pop = R.sum(0).astype(float)
        for lag in range(-m, m + 1):
            tot = np.dot(pop, np.roll(pop, -lag))        # all ordered (i at t, j at t + lag)
            same = sum(np.dot(r, np.roll(r, -lag)) for r in R.astype(float))  # i = j
            obs[lag + m] += tot - same
        exp_ += (cnt.sum() ** 2 - (cnt ** 2).sum()) / L   # per lag, circular, i != j
    return np.arange(-m, m + 1) * DT, obs, exp_


def predicted_lag_pmf(sigma, lags):
    """Chance that two participants' rounded onsets differ by each lag: the continuous lag
    D ~ N(0, 2 sigma^2), spread over the two neighbouring frames in proportion to its distance
    from each (rounding at a uniform frame phase)."""
    from scipy import integrate
    s = sigma * np.sqrt(2.0) / DT          # in frames
    out = []
    for L in np.round(lags / DT):
        f = (lambda u: max(0.0, 1 - abs(u - L)) * stats.norm.pdf(u, 0, s))
        out.append(integrate.quad(f, L - 1, L + 1, points=[L])[0])
    return np.array(out)


def hwhm(lags, y):
    """Half-width at half maximum of a peak at zero lag, by linear interpolation, averaged over
    the two sides."""
    pk = y.max()
    half = pk / 2
    i0 = int(np.argmax(y))
    sides = []
    for step in (1, -1):
        i = i0
        while 0 <= i + step < y.size and y[i + step] > half:
            i += step
        j = i + step
        if not 0 <= j < y.size:
            return float("nan")
        x0, x1, y0, y1 = abs(lags[i]), abs(lags[j]), y[i], y[j]
        sides.append(x0 + (y0 - half) * (x1 - x0) / (y0 - y1))
    return float(np.mean(sides))


def bin_count_survival(recs, T, bin_s=1.0):
    """Share of 1 s bins with at least K distinct active cells, K = 0..N, pooled."""
    nb = int(T // bin_s)
    tally = np.zeros(N + 2)
    for trains, _ in recs:
        c = np.zeros(nb, int)
        for tr in trains:
            b = np.unique((tr // bin_s).astype(int))
            c[b[b < nb]] += 1
        tally[:N + 1] += np.bincount(c, minlength=N + 1)[:N + 1]
    pmf = tally / tally.sum()
    return pmf[::-1].cumsum()[::-1]


def fig_twosets(out):
    d = SETS
    rng = np.random.RandomState(7)
    data, rows = {}, {}
    for j, (key, sg) in enumerate(d["sigma"].items()):
        seeds = [d["seed0"] + 100 * j + i for i in range(d["n_rec"])]
        recs = _set_recordings(sg, seeds)
        lags, obs, exp_ = correlogram(recs, d["T"], d["lag_max"])
        ratio = obs / exp_
        lam = d["E"] / d["T"]
        pairs_pred = d["n_rec"] * d["E"] * d["k"] * (d["k"] - 1) * predicted_lag_pmf(sg, lags)
        ratio_pred = 1 + pairs_pred / exp_
        L = int(round(d["T"] / DT))
        f2m = []
        for w in d["windows"]:
            vals = []
            for trains, _ in recs:
                fr = [np.round(t / DT).astype(int) for t in trains]
                vals.append(mcr.excess_cumulants(fr, L, int(round(w / DT)), mcr.N_SURR, rng)[0])
            f2m.append(np.mean(vals) / (lam * w * d["k"] * (d["k"] - 1)))
        ww = np.geomspace(0.1, 10, 80)
        f2p = [theory.predicted_excess_cumulants(d["k"], sg, w, lam, N)[0]
               / (lam * w * d["k"] * (d["k"] - 1)) for w in ww]
        g2p = [theory.g(2, w, sg) for w in ww]
        surv = bin_count_survival(recs, d["T"])
        data[key] = dict(recs=recs, lags=lags, ratio=ratio, ratio_pred=ratio_pred,
                         f2m=f2m, ww=ww, f2p=f2p, g2p=g2p, surv=surv)
        hm = hwhm(lags, ratio - 1)
        hp = hwhm(lags, ratio_pred - 1)
        rows[key] = (sg, hm, hp)
        print(f"[twosets] {key} (sigma {sg} s): correlogram peak {ratio.max():.1f} x chance "
              f"(predicted {ratio_pred.max():.1f}); HWHM measured {hm:.3f} s, predicted with "
              f"frame rounding {hp:.3f} s, 2 sqrt(ln 2) sigma = {2 * np.sqrt(np.log(2)) * sg:.3f} s")
        print(f"[twosets] {key}: pair excess / (lambda w k(k-1)) at w = "
              + ", ".join(f"{w:g} s: {v:.2f}" for w, v in zip(d["windows"], f2m)))
        print(f"[twosets] {key}: g2 at w = " + ", ".join(
            f"{w:g} s: {theory.g(2, w, sg):.2f}" for w in d["windows"]))
        print(f"[twosets] {key}: predicted (hard-core form) at w = " + ", ".join(
            f"{w:g} s: {theory.predicted_excess_cumulants(d['k'], sg, w, lam, N)[0] / (lam * w * d['k'] * (d['k'] - 1)):.2f}"
            for w in d["windows"]))

    rates = [np.mean([t.size for t in tr]) / d["T"] for k in data for tr, _ in data[k]["recs"]]
    p_bin = 1 - np.exp(-np.mean(rates) * 1.0)
    chance = stats.binom.sf(np.arange(N + 2) - 1, N, p_bin)
    print(f"[twosets] mean onset rate per cell {np.mean(rates):.4f} Hz "
          f"(background {d['b']} Hz plus coordinated {d['E'] * d['k'] / (N * d['T']):.4f} Hz)")
    for key in data:
        s = data[key]["surv"]
        print(f"[twosets] {key}: share of 1 s bins with >= 5 cells {s[5]:.2e}, >= 8 {s[8]:.2e}; "
              f"chance {chance[5]:.2e}, {chance[8]:.2e}")

    fig = plt.figure(figsize=(11.5, 12.6))
    gs = fig.add_gridspec(4, 2, height_ratios=[0.22, 2.0, 2.6, 2.6], hspace=0.36, wspace=0.28,
                          left=0.09, right=0.985, top=0.975, bottom=0.06)
    for j, key in enumerate(("sharp", "jittered")):
        recs = data[key]["recs"]
        trains, evt = recs[0]
        te = evt[len(evt) // 2]
        ln = fig.add_subplot(gs[0, j])
        ra = fig.add_subplot(gs[1, j], sharex=ln)
        ln.plot(te, 0.5, "v", ms=10, color=SET_COL[key])
        lane(ln, "planted" if j == 0 else "")
        ln.set_title(f"{key} set: jitter SD {d['sigma'][key]} s", fontsize=12,
                     color=SET_COL[key], pad=2)
        raster(ra, trains, te - 6, te + 6)
        ra.set_xlim(te - 6, te + 6)
        ra.set_xticks(np.arange(te - 6, te + 6.01, 2))
        ra.set_xticklabels([f"{x:+.0f}s" for x in np.arange(-6, 6.01, 2)])
        ra.set_xlabel("time from the planted event")
        if j == 0:
            ra.set_ylabel(f"cell (of {N})")
        letter(ra, "AB"[j], x=-0.06)

    c = fig.add_subplot(gs[2, 0])
    for key in data:
        D = data[key]
        c.plot(D["lags"], D["ratio"], "o", ms=3.5, color=SET_COL[key],
               label=f"{key}, measured")
        c.plot(D["lags"], D["ratio_pred"], "-", lw=1.2, color=SET_COL[key], alpha=0.7)
        sg, hm, hp = rows[key]
        half = 1 + (D["ratio"].max() - 1) / 2
        c.plot([-hm, hm], [half, half], color=SET_COL[key], lw=2.4)
        c.text(hm + 0.08, half, f"HWHM {hm:.2f} s", color=SET_COL[key], va="center",
               fontsize=10.5)
    c.axhline(1, color=base.GREY, ls=":", lw=1)
    c.set_xlabel("lag between two different cells' onsets (s)")
    c.set_ylabel("onset pairs ÷ chance")
    c.set_xlim(-d["lag_max"], d["lag_max"])
    style(c)
    c.legend(handles=[Line2D([], [], color=SET_COL["sharp"], marker="o", ls="none", ms=4,
                             label="sharp, measured"),
                      Line2D([], [], color=SET_COL["jittered"], marker="o", ls="none", ms=4,
                             label="jittered, measured"),
                      Line2D([], [], color="k", lw=1.2, alpha=0.7, label="predicted"),
                      Line2D([], [], color="k", lw=2.4, label="half-width at half maximum")],
             frameon=False, fontsize=10, loc="upper left")
    letter(c, "C", x=-0.06)

    w_ax = fig.add_subplot(gs[2, 1])
    for key in data:
        D = data[key]
        w_ax.plot(d["windows"], D["f2m"], "o", ms=6, color=SET_COL[key], label=f"{key}, measured")
        w_ax.plot(D["ww"], D["f2p"], "-", color=SET_COL[key], lw=1.4)
        w_ax.plot(D["ww"], D["g2p"], ":", color=SET_COL[key], lw=1.2)
    w_ax.set_xscale("log")
    w_ax.set_xticks([0.1, 0.2, 0.5, 1, 2, 4, 8])
    w_ax.set_xticklabels(["0.1", "0.2", "0.5", "1", "2", "4", "8"])
    w_ax.set_xlabel("window width w (s)")
    w_ax.set_ylabel("excess pairs ÷ all of the events' pairs")
    w_ax.set_ylim(0, 1.08)
    style(w_ax)
    w_ax.legend(handles=[Line2D([], [], color="k", marker="o", ls="none", label="measured"),
                         Line2D([], [], color="k", lw=1.4, label="predicted"),
                         Line2D([], [], color="k", ls=":", lw=1.2, label="window sharing g₂")],
                frameon=False, fontsize=10, loc="lower right")
    letter(w_ax, "D", x=-0.06)

    s_ax = fig.add_subplot(gs[3, :])
    K = np.arange(N + 1)
    for key in data:
        sv = data[key]["surv"][1:16]
        nz = sv > 0           # a share of zero has no place on a log axis; it is left off
        s_ax.semilogy(K[1:16][nz], sv[nz], "o-", ms=5, color=SET_COL[key], label=key)
    s_ax.semilogy(K[1:16], chance[1:16], "--", color=INK,
                  label="chance: every cell independent, at the sets' mean onset rate")
    s_ax.set_xlabel("K: distinct cells active in one 1 s bin")
    s_ax.set_ylabel("share of bins with at least K cells")
    s_ax.set_xticks(range(1, 16))
    s_ax.set_ylim(1e-7, 1.5)
    style(s_ax)
    s_ax.legend(frameon=False, fontsize=10.5)
    letter(s_ax, "E", x=-0.03)
    title = "Two sets, sharp and jittered: correlogram width, pair counts by window, bin counts"
    return save(fig, name("sharp-and-jittered-sets-each-tool", "recovery"), title, out)


FIGS = {"problem": fig_problem, "detectors": fig_detectors, "twosets": fig_twosets}


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--out", type=Path, default=HERE)
    ap.add_argument("--only", nargs="*", choices=sorted(FIGS))
    a = ap.parse_args(argv)
    # the analytic floor must give the count detector's floors the chapter quotes (section 1.6)
    assert chance_floor(0.01) == 6 and chance_floor(0.05) == 12, (
        chance_floor(0.01), chance_floor(0.05))
    for k in (a.only or FIGS):
        FIGS[k](a.out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
