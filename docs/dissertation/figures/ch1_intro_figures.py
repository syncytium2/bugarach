"""The three opening figures of Chapter 1: the problem, three simple detectors, and the tools.

Tony's first read of the chapter (2026-11-13) asked for an opening a reader outside the field can
follow: lead with a picture of coordinated events on a noisy background; walk through the simplest
detector (count cells in fixed bins), then a sliding window, then an adaptive threshold (CFAR), and
show where each succeeds and fails on one raster built for the purpose; then introduce the tools
that characterize coordination, the correlogram's half-width at half maximum first, on two sets,
one sharp and one with much jitter. These are those figures.

  problem    background alone, coordinated events alone, and the two together (Figure 1.1)
  detectors  fixed bins, a sliding window and CFAR on one designed recording (Figure 1.2, Table 1.1)
  twosets    a sharp set and a jittered set: correlogram and HWHM, pair counts against window
             width, and the count of active cells per bin against chance (Figure 1.4)

**What is simulated, and by what.** Figures 1.1 and 1.2 need events at chosen times, which the
repository's generator does not take, so ``plant`` below writes the chapter's model out in a few
lines: each cell has Poisson background onsets; each event is joined by k cells chosen at random,
each onset the event time plus Gaussian jitter of SD sigma; every onset is rounded to the 0.1 s
frame (half away from zero, as the generator rounds); unlike the generator, ``plant`` keeps one
onset per cell per frame. The
two-sets figure uses the repository's generator (``bugarach.simulate.simulate_coordination``) at
the first experiment's settings, so its sets are the chapter's own.

**What is computed, and by what.**
* The fixed-bin and sliding detectors are the repository's ``count_detect`` and
  ``count_sliding_detect``.
* The CFAR detector is written here. The repository's CFAR-shaped code is the guarded context of
  ``detectors.rate.event_rate_context`` and ``rate_detect``'s multiplicative mode, whose window
  edges differ slightly from ``local_rate`` below. Its count is the sliding count on whole frames,
  and its calls are formed with the sliding detector's helpers: runs joined by
  ``detectors.sliding.merge_runs`` and spanned by ``detectors.sliding.span_of``. Two edge cases
  differ from ``count_sliding_detect``: runs exactly the merge gap apart are joined here (whole
  frames) and may not be there (float piece edges). Its threshold at
  each instant is the chance floor for a local background estimate made from 30 s on either side,
  leaving out 5 s nearest the instant (the guard).
* The chance floor is the analytic up-crossing rule of
  ``docs/learned/synthetic_validation/blind_a/theory_floor.py`` (u_K, with its guard that every
  larger K also meets the budget), restated here because that file runs its checks on import.
  ``main`` asserts that it gives the count detector's simulated floors quoted in the chapter (6 cells
  at 0.01 Hz, 12 at 0.05 Hz).
* Scoring: a planted event is found when a call's span, widened by 1 s, contains it; one call finds
  at most one event. The repository's scorer (``bugarach.score.score_detections``) gives the same
  counts on these draws; which event of a merged pair a call credits can differ (time order here,
  nearest midpoint there), so Figure 1.2's lanes may colour 3a and 3b the other way round. Its rule
  that events under the floor are "don't care" is deliberately not applied, so that event 5 can be
  shown.
* The correlogram is the repository's correlogram tool's statistic
  (``tools/measure_jitter_correlogram.py``: ``pairs`` and ``hwhm``, which subtracts the mean
  excess at 5-10 s lag and takes the half-width of what is left), summed over recordings, with a
  bootstrap over recordings for its uncertainty.
* The excess pair counts are the coordination-rates tool's own (``measure_coordination_rates.
  excess_cumulants``) and their prediction is ``theory.predicted_excess_cumulants``.

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
from ch1_new_figures import letter, minutes_axis, plt, style  # noqa: E402
from matplotlib.lines import Line2D  # noqa: E402
from scipy import stats  # noqa: E402

import measure_coordination_rates as mcr  # noqa: E402  (tools/)
import measure_jitter_correlogram as mjc  # noqa: E402  (tools/)
import theory  # noqa: E402  (docs/learned/synthetic_validation/)

base.META = "bugarach dissertation, chapter 1 (docs/dissertation/figures/ch1_intro_figures.py)"
DATE = "20261113"
DT = 0.1                     # s, the frame
N = 33                       # cells
INK = base.INK
HIT, MISS, FALSE = "#1a9850", "#d73027", "#f08c00"   # verdict colours; the shape is always ▼
SET_COL = {"sharp": "#2a78d6", "jittered": "#d0453b"}
# Drawn about 7 in wide so that, placed at a 5.8-6.5 in text width, 9-10 pt text stays near 8 pt.
FONT = {"font.size": 10, "axes.labelsize": 10, "xtick.labelsize": 9, "ytick.labelsize": 9,
        "legend.fontsize": 9}


def name(topic, type_):
    from naming import artifact_name
    return artifact_name.build(artifact_name.load_codes(), source="synth", type=type_,
                               form="plot", topic=topic, ext="png", date=DATE)


def save(fig, fname, title, out):
    base.META = "bugarach dissertation, chapter 1 (docs/dissertation/figures/ch1_intro_figures.py)"
    return base.save(fig, fname, title, out)


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
        # round half away from zero (times are positive), as the generator's matlab_round does
        f = np.unique(np.floor(np.asarray(tr) / DT + 0.5).astype(int))
        f = f[(f >= 0) & (f < int(round(T / DT)))]
        out.append(f * DT)
    return out, members


def raster(ax, trains, t0, t1, ms=2.0):
    """One ink, one mark per onset, nothing else on it (CLAUDE.md). Cell 1 at the bottom."""
    for r, tr in enumerate(trains):
        x = tr[(tr >= t0) & (tr < t1)]
        ax.plot(x, np.full(x.size, r + 1), "|", color=INK, ms=ms, mew=1.0)
    ax.set_ylim(0.3, len(trains) + 0.7)
    ax.set_yticks([1, len(trains)])
    for sp in ("top", "right"):
        ax.spines[sp].set_visible(False)


def lane(ax, label):
    ax.set_ylim(0, 1)
    ax.set_yticks([])
    ax.set_ylabel(label, rotation=0, ha="right", va="center", fontsize=9.5)
    for sp in ("top", "right", "left", "bottom"):
        ax.spines[sp].set_visible(False)
    ax.tick_params(axis="x", length=0, labelbottom=False)


# --------------------------------------------------------------------------- chance and CFAR

def chance_calls_per_hour(K, b, w=2.0, n=N):
    """u_K of theory_floor.py, per hour: the rate at which background alone lifts the count of
    distinct cells active in a sliding window of ``w`` s to ``K``. The count sits at K - 1 with
    binomial probability, and one of the n - K + 1 inactive cells then has an onset, at rate b each
    (the scan-statistic up-crossing approximation; Poisson cells of equal rate)."""
    p = 1 - np.exp(-b * w)
    return 3600.0 * stats.binom.pmf(K - 1, n, p) * (n - K + 1) * b


def chance_floor(b, budget=1.0, w=2.0, n=N):
    """theory_floor.floor_analytic: the smallest K, at least 3, such that K and every larger count
    are reached by chance at most ``budget`` times per hour (ADR-0008's rule, analytic)."""
    for K in range(3, n + 2):
        if all(chance_calls_per_hour(j, b, w, n) <= budget for j in range(K, n + 1)):
            return K
    return n + 1


def sliding_count(trains, w=2.0, T=None):
    """Distinct cells with an onset in (t - w, t], at every frame t = 1..L, on whole frames."""
    L = int(round(T / DT))
    wf = int(round(w / DT))
    S = np.zeros(L + 1, int)
    for tr in trains:
        f = np.unique(np.floor(np.asarray(tr) / DT + 0.5).astype(int))
        act = np.zeros(L + wf + 2, int)
        for x in f:                         # active at frames x .. x + wf - 1 (t - w < x <= t)
            act[x:x + wf] = 1
        S += act[:L + 1]
    return S                                 # S[i] is the count at t = i * DT


def local_rate(trains, T, ref=30.0, guard=5.0):
    """Background rate per cell at every frame from the onsets in two reference stretches of
    ``ref`` s on either side, leaving out ``guard`` s on each side (the guard band), so an event at
    the instant under test cannot raise its own threshold. Clipped at the recording's ends."""
    allt = np.sort(np.concatenate(trains))
    t = np.arange(0, int(round(T / DT)) + 1) * DT
    lo1, hi1 = np.maximum(0.0, t - guard - ref), np.maximum(0.0, t - guard)
    lo2, hi2 = np.minimum(T, t + guard), np.minimum(T, t + guard + ref)
    cnt = (np.searchsorted(allt, hi1) - np.searchsorted(allt, lo1)
           + np.searchsorted(allt, hi2) - np.searchsorted(allt, lo2))
    span = (hi1 - lo1) + (hi2 - lo2)
    return cnt / (len(trains) * span)


def cfar_calls(trains, S, K_t, w, merge):
    """Calls on the sliding count where it reaches the local threshold, formed as
    ``count_sliding_detect`` forms them: runs of frames at or above threshold, joined when the gap
    between runs is at most ``merge`` (``sliding.merge_runs``), each call spanning its first to its
    last participating onset (``sliding.span_of``)."""
    from bugarach.detectors import sliding as sl
    on = S >= K_t
    idx = np.flatnonzero(on)
    if idx.size == 0:
        return []
    brk = np.flatnonzero(np.diff(idx) > 1)
    rs = np.concatenate(([idx[0]], idx[brk + 1]))
    re_ = np.concatenate((idx[brk], [idx[-1]]))
    starts, ends = rs * DT, (re_ + 1) * DT          # a run covers [start, end) in time
    ev = [np.sort(np.asarray(t)) for t in trains]
    calls = []
    for a, b in sl.merge_runs(starts, ends, merge):
        # onsets that put the count up during the run: in (start - w, end - DT]
        t0, t1, n = sl.span_of(ev, starts[a] - w, ends[b] - DT / 2)
        if n:
            calls.append((t0, t1))
    return calls


def score(calls, ev_times, tol=1.0):
    """Hits, misses and false alarms. A planted event is found when a call's span, widened by
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
    bg_tr, _ = plant(d["T"], [], lambda t: d["b"], rng)
    ev_tr, _ = plant(d["T"], evs, lambda t: 1e-12, rng)
    both = [np.unique(np.round(np.concatenate([a, c]) / DT).astype(int)) * DT
            for a, c in zip(bg_tr, ev_tr)]

    with plt.rc_context(FONT):
        fig = plt.figure(figsize=(7.2, 7.6))
        gs = fig.add_gridspec(4, 1, height_ratios=[0.3, 2.6, 2.6, 2.6], hspace=0.3,
                              left=0.15, right=0.98, top=0.975, bottom=0.075)
        ln = fig.add_subplot(gs[0])
        axes = [fig.add_subplot(gs[i], sharex=ln) for i in (1, 2, 3)]
        for t in d["times"]:
            ln.plot(t, 0.5, "v", ms=8, color=SET_COL["sharp"])
        lane(ln, "planted\nevents")
        titles = ("background\nalone", "coordinated\nevents alone", "what the\nanalyst receives")
        for ax, tr, lab, L in zip(axes, (bg_tr, ev_tr, both), titles, "ABC"):
            raster(ax, tr, 0, d["T"], ms=1.8)
            ax.set_ylabel(f"{lab}\ncell (of {N})", fontsize=9.5)
            letter(ax, L, x=-0.12)
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

# Fixed 2 s bins start at 0 s, and an onset rounds into the bin that starts at an even second s
# when it falls at s - 0.05 or later, so after rounding the bin borders sit at x.95 s. Event 2 is
# put on a border on purpose (45.95 s); every other event sits mid-bin.
DET = dict(T=240.0, b_quiet=0.0096, b_busy=0.05, busy=(120.0, 180.0), w=2.0, merge=3.0,
           K_fixed=6, seed=1000, n_draws=200, ref=30.0, guard=5.0,
           events=[(15.0, 12, 0.05, "1"),     # sharp and large
                   (45.95, 7, 0.5, "2"),      # jittered, centred on a fixed-bin border
                   (81.0, 10, 0.1, "3a"),     # two events 4 s apart
                   (85.0, 10, 0.1, "3b"),
                   (151.0, 12, 0.1, "4"),     # inside the busier stretch
                   (211.0, 5, 0.05, "5")])    # one cell below the fixed threshold
KEYS = ("fixed", "sliding", "cfar")
LABEL = {"fixed": "fixed bins", "sliding": "sliding window", "cfar": "CFAR"}


def detector_runs(seed, events=None, merge=None):
    from bugarach.detectors.count import count_detect, count_sliding_detect
    d = DET
    events = d["events"] if events is None else events
    merge = d["merge"] if merge is None else merge
    rng = np.random.RandomState(seed)
    lo, hi = d["busy"]
    bg = (lambda t: d["b_busy"] if lo <= t < hi else d["b_quiet"])
    trains, _ = plant(d["T"], [(t, k, s) for t, k, s, _ in events], bg, rng)
    ev_t = [e[0] for e in events]
    fx = count_detect(trains, (0.0, d["T"]), bin_sec=d["w"], min_rois=d["K_fixed"],
                      merge_gap_sec=merge)
    fx_calls = [(o, o + w) for o, w in zip(fx.onset_sec, fx.width_sec)]
    sl = count_sliding_detect(trains, (0.0, d["T"]), win_sec=d["w"], min_rois=d["K_fixed"],
                              merge_gap_sec=merge)
    sl_calls = [(o, o + w) for o, w in zip(sl.onset_sec, sl.width_sec)]
    S = sliding_count(trains, d["w"], d["T"])
    b_hat = local_rate(trains, d["T"], d["ref"], d["guard"])
    floors = {}
    K_t = np.array([floors.setdefault(round(b, 6), chance_floor(b)) for b in b_hat])
    cf_calls = cfar_calls(trains, S, K_t, d["w"], merge)
    res = {"fixed": (fx_calls, score(fx_calls, ev_t)),
           "sliding": (sl_calls, score(sl_calls, ev_t)),
           "cfar": (cf_calls, score(cf_calls, ev_t))}
    return trains, fx, S, b_hat, K_t, res


def outcomes(res):
    """One draw's outcome per detector: whether each situation was found (event 3 counts as found
    only when both of its events are), and whether there was any false alarm in the busier
    stretch and in the 0.0096 Hz stretches."""
    d = DET
    lo, hi = d["busy"]
    o = {}
    for k in KEYS:
        hit, _, false = res[k][1]
        f = {lab: (t in hit) for t, _, _, lab in d["events"]}
        o[k] = (f["1"], f["2"], f["3a"] and f["3b"], f["4"], f["5"],
                any(lo <= x < hi for x in false), any(not lo <= x < hi for x in false))
    return o


def _frames_near(t, a, b):
    return slice(int(round((t + a) / DT)), int(round((t + b) / DT)) + 1)


def fig_detectors(out):
    d = DET
    lo, hi = d["busy"]
    n = d["n_draws"]
    tally = {k: np.zeros(7) for k in KEYS}
    false_busy = {k: 0 for k in KEYS}
    false_quiet = {k: 0 for k in KEYS}
    per_draw, k_ev2, k_ev5, b_quiet = [], [], [], []
    k_busy_lo, k_busy_hi, fa_edge = [], [], []
    for i in range(n):
        trains, fx, S, b_hat, K_t, res = detector_runs(d["seed"] + i)
        o = outcomes(res)
        per_draw.append(o)
        for k in KEYS:
            tally[k] += np.array(o[k], float)
            false_busy[k] += sum(lo <= x < hi for x in res[k][1][2])
            false_quiet[k] += sum(not lo <= x < hi for x in res[k][1][2])
        k_ev2.append(K_t[_frames_near(45.95, 0.0, 2.0)].min())
        k_ev5.append(K_t[_frames_near(211.0, 0.0, 2.0)].min())
        k_busy_lo.append(K_t[int(lo / DT):int(hi / DT)].min())
        k_busy_hi.append(K_t[int(lo / DT):int(hi / DT)].max())
        fa_edge += [min(x - lo, hi - x) for x in res["cfar"][1][2] if lo <= x < hi]
        q = np.r_[np.arange(0, int(lo / DT)), np.arange(int(hi / DT), int(d["T"] / DT) + 1)]
        b_quiet.append(np.median(b_hat[q]))
    share = {k: tally[k] / n for k in KEYS}
    busy_min = n * (hi - lo) / 60.0
    quiet_h = n * (d["T"] - (hi - lo)) / 3600.0
    print(f"[detectors] over {n} draws (seeds {d['seed']}-{d['seed'] + n - 1}): share found for "
          "events 1, 2, 3 (both), 4, 5; false alarms per busier-stretch minute; per quiet hour")
    for k in KEYS:
        print(f"[detectors]   {LABEL[k]:15s} " + "  ".join(f"{v:.2f}" for v in share[k][:5])
              + f"   {false_busy[k] / busy_min:.2f} per min ({false_busy[k]} in {busy_min:.0f} min)"
              + f"   {false_quiet[k] / quiet_h:.2f} per h ({false_quiet[k]} in {quiet_h:.0f} h)")

    def dist(v):
        u, c = np.unique(v, return_counts=True)
        return ", ".join(f"{a} cells in {b}" for a, b in zip(u, c))
    print(f"[detectors] CFAR threshold near event 2 (lowest over 45.95-47.95 s): {dist(k_ev2)}")
    print(f"[detectors] CFAR threshold near event 5 (lowest over 211-213 s): {dist(k_ev5)}")
    print(f"[detectors] CFAR threshold in the busier stretch over the {n} draws: lowest "
          f"{dist(k_busy_lo)}; highest {dist(k_busy_hi)}")
    print(f"[detectors] CFAR false alarms in the busier stretch, distance to its nearer end: "
          + ", ".join(f"{x:.1f} s" for x in sorted(fa_edge)))
    lo95, hi95 = stats.chi2.ppf(0.025, 2 * false_busy['cfar']) / 2, stats.chi2.ppf(0.975, 2 * false_busy['cfar'] + 2) / 2
    print(f"[detectors] CFAR busier-stretch false alarms: {false_busy['cfar']} in {busy_min:.0f} min, "
          f"{60 * false_busy['cfar'] / busy_min:.1f} per hour (exact Poisson 95 % interval "
          f"{60 * lo95 / busy_min:.1f}-{60 * hi95 / busy_min:.1f} per hour)")
    print(f"[detectors] CFAR's background estimate in the 0.0096 Hz stretches: median "
          f"{np.median(b_quiet):.4f} Hz (true 0.0096 Hz), from the events in its reference "
          f"stretches and the edges of the busier stretch")
    print(f"[detectors] analytic floor, 2 s window: {chance_floor(0.0096)} cells at 0.0096 Hz, "
          f"{chance_floor(0.05)} at 0.05 Hz; 0.2 s window at 0.0096 Hz: "
          f"{chance_floor(0.0096, w=0.2)} cells; chance calls per hour at the 2 s floor, "
          f"0.0096 Hz: {chance_calls_per_hour(6, 0.0096):.2f}")

    # Control for situation 4: the same draws with event 4 left out. A call near 151 s then can
    # only be chance, so this is how often "found" would be scored with nothing there.
    ev_no4 = [e for e in d["events"] if e[3] != "4"]
    chance4 = {k: 0 for k in KEYS}
    for i in range(n):
        res = detector_runs(d["seed"] + i, events=ev_no4)[-1]
        for k in KEYS:
            chance4[k] += bool(score(res[k][0], [151.0])[0])
    print("[detectors] event 4 left out, a call within 1 s of 151 s anyway (chance hit): "
          + ", ".join(f"{LABEL[k]} {chance4[k] / n:.2f}" for k in KEYS))
    # Masking control: events 1 and 3 left out, so nothing but background sits in event 2's
    # reference stretches
    ev_mask = [e for e in d["events"] if e[3] not in ("1", "3a", "3b")]
    found2 = {k: 0 for k in KEYS}
    for i in range(n):
        res = detector_runs(d["seed"] + i, events=ev_mask)[-1]
        for k in KEYS:
            found2[k] += 45.95 in res[k][1][0]
    print("[detectors] events 1 and 3 left out, event 2 found: "
          + ", ".join(f"{LABEL[k]} {found2[k] / n:.2f}" for k in KEYS))
    binned = [theory.chance_clusters_per_min(N, d["b_quiet"], K, bin_sec=2.0, merge_bins=0) * 60
              for K in (5, 6)]
    print(f"[detectors] fixed 2 s bins at {d['b_quiet']} Hz, chance calls per hour "
          f"(theory.chance_clusters_per_min): {binned[0]:.2f} at 5 cells, {binned[1]:.2f} at 6")
    # Situation 3 with a shorter merge gap
    both3 = {k: 0 for k in KEYS}
    for i in range(n):
        o = outcomes(detector_runs(d["seed"] + i, merge=0.5)[-1])
        for k in KEYS:
            both3[k] += o[k][2]
    print("[detectors] merge gap 0.5 s instead of 3 s, both events of situation 3 found: "
          + ", ".join(f"{LABEL[k]} {both3[k] / n:.2f}" for k in KEYS))

    typical = {k: tuple(v >= 0.5 for v in share[k]) for k in KEYS}
    n_typ = sum(all(o[k] == typical[k] for k in KEYS) for o in per_draw)
    pick = next(i for i, o in enumerate(per_draw) if all(o[k] == typical[k] for k in KEYS))
    seed = d["seed"] + pick
    trains, fx, S, b_hat, K_t, res = detector_runs(seed)
    print(f"[detectors] draw shown: seed {seed}, the first whose every outcome is the most "
          f"common one ({n_typ} of {n} draws are)")
    for k in KEYS:
        hit, miss, false = res[k][1]
        print(f"[detectors] {k}: {len(res[k][0])} calls; found {len(hit)} of {len(d['events'])}; "
              f"false alarms at {', '.join(f'{x:.0f} s' for x in false) or 'none'}")
    print(f"[detectors] CFAR threshold in the draw shown: near event 2 "
          f"{sorted(set(K_t[_frames_near(45.95, 0, 2)].tolist()))} cells, in the busier stretch "
          f"{sorted(set(K_t[int(lo / DT):int(hi / DT)].tolist()))} cells")

    grid = np.arange(S.size) * DT
    with plt.rc_context(FONT):
        fig = plt.figure(figsize=(7.4, 9.6))
        gs = fig.add_gridspec(8, 1, height_ratios=[0.3, 0.45, 0.38, 0.38, 0.38, 2.9, 1.15, 1.15],
                              hspace=0.24, left=0.17, right=0.98, top=0.985, bottom=0.085)
        bgl = fig.add_subplot(gs[0])
        ax = [fig.add_subplot(gs[i], sharex=bgl) for i in range(1, 8)]
        pl, lf, ls_, lc, ras, cnt_fx, cnt_sl = ax
        bgl.axvspan(lo, hi, ymin=0.15, ymax=0.85, color="#d4d4d4", lw=0)
        bgl.text(0.5 * (lo + hi), 0.5, f"{d['b_busy']} Hz per cell", ha="center", va="center",
                 fontsize=9)
        bgl.text(0.5 * lo, 0.5, f"{d['b_quiet']} Hz per cell", ha="center", va="center",
                 fontsize=9)
        bgl.text(0.5 * (hi + d["T"]), 0.5, f"{d['b_quiet']} Hz per cell", ha="center",
                 va="center", fontsize=9)
        lane(bgl, "background")
        for t, k, s, lab in d["events"]:
            pl.plot(t, 0.4, "v", ms=8, color=INK)
        vign = {}
        for t, _, _, lab in d["events"]:
            vign.setdefault(lab[0], []).append(t)
        for lab, ts in vign.items():
            pl.text(np.mean(ts), 0.98, lab, ha="center", va="center", fontsize=9.5,
                    fontweight="bold")
        lane(pl, "planted\nevents")
        for a, key, lab in ((lf, "fixed", "fixed\nbins"), (ls_, "sliding", "sliding\nwindow"),
                            (lc, "cfar", "CFAR")):
            hit, miss, false = res[key][1]
            a.plot(hit, [0.5] * len(hit), "v", ms=7.5, color=HIT, ls="none")
            a.plot(miss, [0.5] * len(miss), "v", ms=7.5, color=MISS, ls="none")
            a.plot(false, [0.5] * len(false), "v", ms=7.5, color=FALSE, ls="none")
            lane(a, lab)
        raster(ras, trains, 0, d["T"], ms=1.7)
        ras.set_ylabel(f"cell (of {N})")
        ras.tick_params(labelbottom=False)
        cnt_fx.bar(fx.ctr, fx.obs, width=d["w"] * 0.92, color="#7a7a7a", lw=0)
        cnt_fx.axhline(d["K_fixed"], color=INK, ls="--", lw=1.0)
        cnt_fx.set_ylabel("cells per\n2 s bin")
        cnt_fx.tick_params(labelbottom=False)
        cnt_sl.step(grid, S, where="post", color="#7a7a7a", lw=0.9)
        cnt_sl.axhline(d["K_fixed"], color=INK, ls="--", lw=1.0)
        cnt_sl.step(grid, K_t, where="post", color="#7b3294", lw=1.5)
        cnt_sl.set_ylabel("cells in the\nlast 2 s")
        top = max(16, int(S.max()) + 2, int(K_t.max()) + 2)
        for a in (cnt_fx, cnt_sl):
            style(a)
            a.set_ylim(0, top)
        minutes_axis(cnt_sl, 0, d["T"])
        cnt_sl.set_xlabel("time")
        for a, L in zip((pl, ras, cnt_fx, cnt_sl), "ABCD"):
            letter(a, L, x=-0.14)
        handles = [Line2D([], [], marker="v", color=HIT, ls="none", ms=7.5, label="found"),
                   Line2D([], [], marker="v", color=MISS, ls="none", ms=7.5, label="missed"),
                   Line2D([], [], marker="v", color=FALSE, ls="none", ms=7.5,
                          label="false alarm"),
                   Line2D([], [], color=INK, ls="--", label=f"fixed threshold, {d['K_fixed']} cells"),
                   Line2D([], [], color="#7b3294", lw=1.5, label="CFAR threshold")]
        fig.legend(handles=handles, loc="lower center", ncol=3, frameon=False,
                   bbox_to_anchor=(0.57, 0.0))
    title = "Three simple detectors on one recording: fixed bins, a sliding window and CFAR"
    return save(fig, name("three-simple-detectors-found-and-missed", "raster"), title, out)


# --------------------------------------------------------------------------- Figure 1.4

SETS = dict(k=10, b=0.0096, E=45, T=2700.0, n_rec=10, n_boot=500,
            sigma={"sharp": 0.1, "jittered": 0.5}, lag_show=3.0,
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


def tool_pairs(recs, T):
    """The correlogram tool's (observed, expected) onset pairs per lag 0..10 s, per recording."""
    L = int(round(T / DT))
    out = []
    for trains, _ in recs:
        fr = [np.floor(np.asarray(t) / DT + 0.5).astype(int) for t in trains]
        out.append(mjc.pairs(fr, L))
    return np.array([o for o, _ in out]), np.array([e for _, e in out])


def predicted_lag_pmf(sigma, lags):
    """Chance that two participants' rounded onsets differ by each lag: the continuous lag
    D ~ N(0, 2 sigma^2), spread over the two neighbouring frames in proportion to its distance
    from each (rounding at a uniform frame phase)."""
    from scipy import integrate
    s = sigma * np.sqrt(2.0) / DT
    out = []
    for Lg in np.round(lags / DT):
        f = (lambda u: max(0.0, 1 - abs(u - Lg)) * stats.norm.pdf(u, 0, s))
        out.append(integrate.quad(f, Lg - 1, Lg + 1, points=[Lg])[0])
    return np.array(out)


def hwhm_from_zero(lags, y):
    """Half-width at half maximum of a one-sided peak at lag 0 (lags >= 0), linear
    interpolation; the same reading as the tool's ``hwhm`` applied to an excess curve."""
    q = y / y[0]
    below = np.nonzero(q < 0.5)[0]
    if below.size == 0:
        return float("nan")
    i = int(below[0])
    return float(lags[i - 1] + (q[i - 1] - 0.5) / (q[i - 1] - q[i]) * (lags[i] - lags[i - 1]))


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


def events_reaching(recs, K, bin_s=1.0, reach=1.5):
    """Share of planted events with at least K distinct active cells in some 1 s bin that
    overlaps the event time +-``reach`` s."""
    hit = tot = 0
    for trains, evt in recs:
        for te in evt:
            b0, b1 = int((te - reach) // bin_s), int((te + reach) // bin_s)
            best = 0
            for bi in range(b0, b1 + 1):
                lo, hi = bi * bin_s, (bi + 1) * bin_s
                best = max(best, sum(bool(((tr >= lo) & (tr < hi)).any()) for tr in trains))
            hit += best >= K
            tot += 1
    return hit, tot


def fig_twosets(out):
    d = SETS
    rng = np.random.RandomState(7)
    lam = d["E"] / d["T"]
    data = {}
    for j, (key, sg) in enumerate(d["sigma"].items()):
        seeds = [d["seed0"] + 100 * j + i for i in range(d["n_rec"])]
        recs = _set_recordings(sg, seeds)
        O, X = tool_pairs(recs, d["T"])
        lags1 = np.arange(O.shape[1]) * DT
        ratio1 = O.sum(0) / X.sum(0)
        w_tool = mjc.hwhm(O.sum(0), X.sum(0))
        boot = []
        brng = np.random.RandomState(11 + j)
        for _ in range(d["n_boot"]):
            ix = brng.randint(0, len(recs), len(recs))
            boot.append(mjc.hwhm(O[ix].sum(0), X[ix].sum(0)))
        se = float(np.nanstd(boot))
        shoulder = float(np.mean(ratio1[(lags1 >= 5) & (lags1 <= 10)]))
        far = float(np.mean(ratio1[(lags1 >= 2) & (lags1 <= 3)]))
        # predicted: chance level lowered by the pairs the hard core forbids, plus the peak
        n_on = np.mean([sum(t.size for t in tr) for tr, _ in recs])
        deficit = (d["E"] * d["k"]) ** 2 * (1 - 1 / d["E"]) / n_on ** 2
        pmf = predicted_lag_pmf(sg, lags1[:31])
        exp1 = X.sum(0)[:31]
        peak_pred = len(recs) * d["E"] * d["k"] * (d["k"] - 1) * pmf
        peak_pred[0] /= 2.0                      # zero lag counted once, as the tool counts it
        ratio_pred = 1 - deficit + peak_pred / exp1
        w_pred = hwhm_from_zero(lags1[:31], ratio_pred - (1 - deficit))
        w_ideal = 2 * np.sqrt(np.log(2)) * sg
        print(f"[twosets] {key} (sigma {sg} s): peak {ratio1[0]:.1f} x chance (predicted "
              f"{ratio_pred[0]:.1f}); level at 2-3 s lag {far:.3f}, at 5-10 s {shoulder:.3f} "
              f"(predicted {1 - deficit:.3f}); HWHM by the correlogram tool {w_tool:.3f} s "
              f"(bootstrap SE over recordings {se:.3f} s), predicted with frame rounding "
              f"{w_pred:.3f} s, 2 sqrt(ln 2) sigma = {w_ideal:.3f} s")
        f2m = []
        L = int(round(d["T"] / DT))
        for w in d["windows"]:
            vals = [mcr.excess_cumulants([np.minimum(mcr._frames(t, 0.0, d["T"]), L - 1)
                                          for t in trains],
                                         L, int(round(w / DT)), mcr.N_SURR, rng)[0]
                    for trains, _ in recs]
            f2m.append(np.mean(vals) / (lam * w * d["k"] * (d["k"] - 1)))
        ww = np.geomspace(0.1, 10, 80)
        f2p = [theory.predicted_excess_cumulants(d["k"], sg, w, lam, N)[0]
               / (lam * w * d["k"] * (d["k"] - 1)) for w in ww]
        g2p = [theory.g(2, w, sg) for w in ww]
        print(f"[twosets] {key}: excess pairs / (lambda w k(k-1)), measured at w = "
              + ", ".join(f"{w:g} s: {v:.3f}" for w, v in zip(d["windows"], f2m)))
        print(f"[twosets] {key}: predicted (hard-core form): " + ", ".join(
            f"{w:g} s: {theory.predicted_excess_cumulants(d['k'], sg, w, lam, N)[0] / (lam * w * d['k'] * (d['k'] - 1)):.3f}"
            for w in d["windows"]))
        print(f"[twosets] {key}: g2: " + ", ".join(
            f"{w:g} s: {theory.g(2, w, sg):.3f}" for w in d["windows"]))
        surv = bin_count_survival(recs, d["T"])
        r5, r8 = events_reaching(recs, 5), events_reaching(recs, 8)
        print(f"[twosets] {key}: share of 1 s bins with >= 5 cells {surv[5]:.4f}, >= 8 "
              f"{surv[8]:.4f}; events reaching >= 5 cells in some 1 s bin {r5[0]}/{r5[1]}, "
              f">= 8 cells {r8[0]}/{r8[1]}")
        data[key] = dict(recs=recs, lags1=lags1, ratio1=ratio1, ratio_pred=ratio_pred,
                         w_tool=w_tool, se=se, shoulder=shoulder, f2m=f2m, ww=ww, f2p=f2p,
                         g2p=g2p, surv=surv)
    p_bg = 1 - np.exp(-d["b"] * 1.0)
    chance = stats.binom.sf(np.arange(N + 2) - 1, N, p_bg)
    print(f"[twosets] chance (background {d['b']} Hz alone): share of 1 s bins with >= 5 cells "
          f"{chance[5]:.2e}, >= 8 {chance[8]:.2e}")

    with plt.rc_context(FONT):
        fig = plt.figure(figsize=(7.6, 9.6))
        gs = fig.add_gridspec(4, 2, height_ratios=[0.18, 1.7, 2.5, 2.4], hspace=0.42,
                              wspace=0.32, left=0.1, right=0.98, top=0.975, bottom=0.06)
        for j, key in enumerate(("sharp", "jittered")):
            trains, evt = data[key]["recs"][0]
            te = evt[len(evt) // 2]
            ln = fig.add_subplot(gs[0, j])
            ra = fig.add_subplot(gs[1, j], sharex=ln)
            ln.plot(te, 0.3, "v", ms=8, color=SET_COL[key])
            lane(ln, "planted" if j == 0 else "")
            ln.set_title(f"{key} set: jitter SD {d['sigma'][key]} s", fontsize=10,
                         color=SET_COL[key], pad=1)
            raster(ra, trains, te - 6, te + 6, ms=2.2)
            ra.set_xlim(te - 6, te + 6)
            ra.set_xticks(np.arange(te - 6, te + 6.01, 3))
            ra.set_xticklabels([f"{x:+.0f}s" for x in np.arange(-6, 6.01, 3)])
            ra.set_xlabel("time from the planted event")
            if j == 0:
                ra.set_ylabel(f"cell (of {N})")
            letter(ra, "AB"[j], x=-0.1)

        c = fig.add_subplot(gs[2, 0])
        for key in data:
            D = data[key]
            lg = D["lags1"][:31]
            lags2 = np.r_[-lg[::-1], lg[1:]]
            r2 = np.r_[D["ratio1"][:31][::-1], D["ratio1"][1:31]]
            p2 = np.r_[D["ratio_pred"][::-1], D["ratio_pred"][1:]]
            c.plot(lags2, r2, "o", ms=2.6, color=SET_COL[key])
            c.plot(lags2, p2, "-", lw=1.1, color=SET_COL[key], alpha=0.75)
            half = D["shoulder"] + (D["ratio1"][0] - D["shoulder"]) / 2
            c.plot([-D["w_tool"], D["w_tool"]], [half, half], color=SET_COL[key], lw=2.2)
            c.axhline(D["shoulder"], color=SET_COL[key], ls=":", lw=0.9)
            c.annotate(f"HWHM {D['w_tool']:.2f} s", xy=(-D["w_tool"], half),
                       xytext=(-2.9, half + (2.2 if key == "sharp" else 2.6)), fontsize=9,
                       color=SET_COL[key], arrowprops=dict(arrowstyle="-", color=SET_COL[key],
                                                           lw=0.7))
        c.axhline(1, color=base.GREY, ls="--", lw=0.9)
        c.set_xlabel("lag between two cells' onsets (s)")
        c.set_ylabel("onset pairs ÷ independent cells")
        c.set_xlim(-d["lag_show"], d["lag_show"])
        style(c)
        # Two entries only: the dashed independence line and the dotted far-lag levels are
        # named in the caption, and a longer legend lands on the sharp peak.
        c.legend(handles=[Line2D([], [], color="k", marker="o", ls="none", ms=3,
                                 label="measured"),
                          Line2D([], [], color="k", lw=1.1, label="predicted")],
                 frameon=False, loc="upper right", fontsize=8.5)
        letter(c, "C", x=-0.12)

        w_ax = fig.add_subplot(gs[2, 1])
        for key in data:
            D = data[key]
            w_ax.plot(d["windows"], D["f2m"], "o", ms=5, color=SET_COL[key])
            w_ax.plot(D["ww"], D["f2p"], "-", color=SET_COL[key], lw=1.3)
            w_ax.plot(D["ww"], D["g2p"], ":", color=SET_COL[key], lw=1.1)
        w_ax.set_xscale("log")
        w_ax.set_xticks([0.1, 0.2, 0.5, 1, 2, 4, 8])
        w_ax.set_xticklabels(["0.1", "0.2", "0.5", "1", "2", "4", "8"])
        w_ax.set_xlabel("window width w (s)")
        w_ax.set_ylabel("excess pairs ÷ all the events' pairs")
        w_ax.set_ylim(0, 1.08)
        style(w_ax)
        w_ax.legend(handles=[Line2D([], [], color="k", marker="o", ls="none", label="measured"),
                             Line2D([], [], color="k", lw=1.3, label="predicted"),
                             Line2D([], [], color="k", ls=":", lw=1.1, label="g₂ alone")],
                    frameon=False, loc="lower right", fontsize=8.5)
        letter(w_ax, "D", x=-0.12)

        s_ax = fig.add_subplot(gs[3, :])
        K = np.arange(N + 1)
        for key in data:
            sv = data[key]["surv"][1:16]
            nz = sv > 0           # a share of zero has no place on a log axis; it is left off
            s_ax.semilogy(K[1:16][nz], sv[nz], "o-", ms=4, color=SET_COL[key], label=f"{key} set")
        s_ax.semilogy(K[1:16], chance[1:16], "--", color=INK,
                      label=f"background alone ({d['b']} Hz per cell)")
        s_ax.set_xlabel("K: distinct cells active in one 1 s bin")
        s_ax.set_ylabel("share of bins with ≥ K cells")
        s_ax.set_xticks(range(1, 16))
        s_ax.set_ylim(1e-10, 1.5)
        style(s_ax)
        s_ax.legend(frameon=True, framealpha=0.95, edgecolor="none", loc="lower right")
        letter(s_ax, "E", x=-0.06)
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
