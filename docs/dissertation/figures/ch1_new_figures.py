"""New figures for Chapter 1 (Aim 0): the data, the tools and the theory, drawn.

The committee review of the chapter (docs/reviews/chapter-1-aim0_2026-10-29-roles/, roles 8
and 9) found no figure in its first ~3,100 words. The first five fill that gap; the last two
answer the round-2 review (docs/reviews/chapter-1-aim0_2026-10-29-round2-roles/, role 9):

  data       what one simulated recording looks like, and what each tool sees of it
  sharing    window sharing g2, g3 (Gaussian and uniform jitter) and the participant bias k-hat/k
  chance     chance clusters per minute against the assessor's threshold K
  order      power to detect order against events per recording (exact-size 5 % test)
  regime     realistic parameter values (fast and slow streams) against the tested grid, both records
  residuals  participant residuals per condition-window, first experiment and held-out record
  jointfit   the joint fit against the correlogram tool, and per recording at realistic values

Every computed curve comes from the repository's own code: theory.py (g2, g3, the
chance-cluster rate), bugarach.simulate.simulate_coordination (the raster), the tools' own
binning (bugarach.assess, bugarach.detectors.count), bugarach.event_floor.floor_of (the first K
under one chance cluster per hour), and the run records theory_check.json and
aim1_one_source.json beside theory.py, and ch1_followups/ (order_power, theory_check_heldout,
correlogram_vs_joint, realistic_counts or lab_values). Nothing here is
re-derived, except the uniform-jitter window sharing, which has no repository code and is
computed by numerical integration over the range of n uniform onsets (see `g_uniform`).

The raster follows CLAUDE.md: one ink, one mark per onset, nothing drawn on it. Event times
sit in a lane above it, and everything that identifies an event's cells is in separate panels.

    PYTHONPATH=src python docs/dissertation/figures/ch1_new_figures.py [--out DIR] [--only ...]
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.lines import Line2D  # noqa: E402
from matplotlib.patches import Patch, Rectangle  # noqa: E402
import numpy as np  # noqa: E402
from scipy import integrate  # noqa: E402

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
SV = ROOT / "docs" / "learned" / "synthetic_validation"
for p in (ROOT / "src", ROOT / "tools", SV):
    sys.path.insert(0, str(p))

import theory  # noqa: E402  (docs/learned/synthetic_validation/theory.py)
from bugarach import time_axis  # noqa: E402

DATE = "20261029"
META = "bugarach dissertation, chapter 1 (docs/dissertation/figures/ch1_new_figures.py)"
plt.rcParams.update({"font.size": 12, "axes.labelsize": 12, "xtick.labelsize": 11,
                     "ytick.labelsize": 11, "legend.fontsize": 11})

GREY = "#9a9a9a"
INK = "#222222"
EV1 = "#eb6834"      # event 1 in the data figure (split by a 1 s border)
EV2 = "#2a78d6"      # event 2 in the data figure (caught whole)
# participants per event, light to dark, as in the chapter's existing figures
K_COL = {5: "#9cc5f3", 10: "#3b8ee6", 20: "#0a2550"}
BG_COL = {0.0096: "#2ca58d", 0.01: "#2a78d6", 0.05: "#d0453b"}


# --------------------------------------------------------------------------- helpers

def style(ax):
    for sp in ("top", "right"):
        ax.spines[sp].set_visible(False)
    ax.grid(True, color="#e5e5e5", lw=0.6)


def letter(ax, c, x=-0.02, y=1.03):
    ax.text(x, y, c, transform=ax.transAxes, fontsize=14, fontweight="bold",
            va="bottom", ha="right")


def name(topic, type_):
    """The file name, from the estate scheme's builder (tools/naming, vendored from armory)."""
    from naming import artifact_name
    return artifact_name.build(artifact_name.load_codes(), source="synth", type=type_,
                               form="plot", topic=topic, ext="png", date=DATE)


def save(fig, fname, title, out):
    out.mkdir(parents=True, exist_ok=True)
    fig.savefig(out / fname, dpi=150, metadata={
        "Title": title, "Author": META,
        "Creation Time": datetime.now().isoformat(timespec="seconds")})
    plt.close(fig)
    print(out / fname)
    return out / fname


def minutes_axis(ax, lo, hi):
    """The repository's 60-base time axis (bugarach.time_axis, the viewer's ticks and labels)."""
    tk = time_axis.ticks(lo, hi)
    ax.set_xticks(tk)
    ax.set_xticklabels([time_axis.label(t) for t in tk])
    ax.set_xlim(lo, hi)


def wilson(p, n, z=1.96):
    """95 % Wilson interval of a binomial share p of n."""
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * np.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return max(0.0, c - h), min(1.0, c + h)


# --------------------------------------------------------------------------- A. the data

DATA = dict(n_roi=33, bg=0.0096, k=10, sigma=0.2, n_events=45, duration=2700.0,
            min_sep=20.0, seed=1, t0=1256.0, t1=1316.0, K=5)


def _simulate():
    """One 45-minute, 33-cell recording from the repository's generator at the lab-like setting.

    The 60 s stretch shown (DATA t0..t1) was chosen by searching this recording's events for two
    within 40 s of each other, one whose onsets fall in a single 1 s window and one split across
    a 1 s window border with at least 3 onsets on each side but held whole by a 2 s and a 4 s
    window. Seed 1 is the first seed with such a pair. The stretch is selected for illustration;
    the onsets in it are the generator's, unedited."""
    from bugarach.simulate import simulate_coordination
    d = DATA
    s, gt = simulate_coordination(duration_sec=d["duration"], n_roi=d["n_roi"],
                                  bg_rate_hz=d["bg"], participation=(d["k"] / d["n_roi"],),
                                  n_per_level=(d["n_events"],), jitter_sec=d["sigma"],
                                  min_sep_sec=d["min_sep"], grid_sec=0.1, seed=d["seed"])
    trains = [np.asarray(t, float) for t in next(iter(s.streams.values())).t50rise]
    evs = sorted([e for e in gt.events if d["t0"] <= e.time < d["t1"]], key=lambda e: e.time)
    return trains, evs


def fig_data(out):
    from bugarach.assess import _coact_count
    from bugarach.detectors.count import count_detect

    d = DATA
    t0, t1, K = d["t0"], d["t1"], d["K"]
    trains, evs = _simulate()
    assert len(evs) == 2, f"expected two planted events in the stretch, found {len(evs)}"
    cols = (EV1, EV2)

    raster_xy = [(o, r + 1) for r, tr in enumerate(trains) for o in tr[(tr >= t0) & (tr < t1)]]

    fig = plt.figure(figsize=(10.5, 13.8))
    gs = fig.add_gridspec(8, 2, width_ratios=[3.0, 1.15],
                          height_ratios=[0.32, 3.4, 0.62, 0.62, 0.62, 0.95, 0.95, 1.45],
                          hspace=0.28, wspace=0.3, left=0.15, right=0.985, top=0.98,
                          bottom=0.01)
    lane = fig.add_subplot(gs[0, 0])
    ras = fig.add_subplot(gs[1, 0], sharex=lane)
    win_axes = [fig.add_subplot(gs[2 + j, 0], sharex=lane) for j in range(3)]
    asx = fig.add_subplot(gs[5, 0], sharex=lane)
    cdx = fig.add_subplot(gs[6, 0], sharex=lane)
    zg = gs[0:7, 1].subgridspec(9, 1, hspace=0.12,
                                height_ratios=[0.3, 1.45, 0.8, 0.9, 0.75, 0.3, 1.45, 0.8, 0.9])
    leg_ax = fig.add_subplot(gs[7, :]); leg_ax.axis("off")

    # lane above the raster: planted event times, pointing down at it
    for i, e in enumerate(evs):
        lane.plot(e.time, 0.5, marker="v", ms=11, color=cols[i], ls="none")
        lane.text(e.time + 1.2, 0.5, f"event {i + 1}", color=cols[i], va="center",
                  fontsize=10.5)
    lane.set_ylim(0, 1); lane.set_yticks([])
    lane.set_ylabel("planted\nevents", rotation=0, ha="right", va="center", fontsize=11)
    for sp in ("top", "right", "left", "bottom"):
        lane.spines[sp].set_visible(False)
    lane.tick_params(axis="x", length=0, labelbottom=False)
    letter(lane, "A", x=LX, y=0.2)

    # the raster: one row per cell, one ink, one mark per onset
    raster = ras
    x, y = zip(*raster_xy)
    raster.plot(x, y, color="black", marker="|", ls="none", ms=7.5, mew=1.6)
    raster.set_ylim(0.3, d["n_roi"] + 0.7); raster.invert_yaxis()
    raster.set_yticks([1, 10, 20, 30, 33])
    raster.set_ylabel(f"cell ({d['n_roi']} cells)")
    for sp in ("top", "right"):
        raster.spines[sp].set_visible(False)
    raster.tick_params(axis="x", labelbottom=False)

    # the coordination-rates tool: onsets per window, at three widths
    allon = np.concatenate([tr[(tr >= t0) & (tr < t1)] for tr in trains])
    evon = [np.asarray(e.onsets) for e in evs]
    for j, w in enumerate(theory.WINDOWS):
        ax = win_axes[j]
        edges = np.arange(np.floor(t0 / w) * w, t1 + w, w)
        n_all, _ = np.histogram(allon, edges)
        n_ev = [np.histogram(evon[i], edges)[0] for i in range(2)]
        _stack(ax, edges, n_all, n_ev, cols)
        ax.set_ylim(0, 15); ax.set_yticks([0, 10])
        ax.text(0.006, 0.97, f"{w:g} s windows", transform=ax.transAxes, ha="left", va="top",
                fontsize=11, zorder=5, bbox=dict(facecolor="white", edgecolor="none", pad=1))
        ax.tick_params(axis="x", labelbottom=False)
    letter(win_axes[0], "D", x=LX, y=1.1)
    fig.text(0.012, 0.5 * (win_axes[0].get_position().y1 + win_axes[2].get_position().y0),
             "coordination-rates tool:\nonsets per window", rotation=90, ha="left",
             va="center", fontsize=11.5)

    # the assessor: distinct cells per 1 s bin, threshold K, and its +-1.5 s gather
    n_bins = int(np.ceil(d["duration"] / 1.0))
    obs = _coact_count(trains, d["duration"], 1.0, n_bins)
    _bars(asx, obs, 1.0, t0, t1, K, cols, evs)
    over = np.flatnonzero(obs >= K)
    groups, cur = [], [over[0]]
    for q in over[1:]:                       # the assessor's merge rule (merge_bins = 2)
        if q - cur[-1] <= 2:
            cur.append(q)
        else:
            groups.append(cur); cur = [q]
    groups.append(cur)
    for g in groups:
        tc = float(np.mean((np.asarray(g) + 0.5) * 1.0))
        if t0 <= tc < t1:
            asx.annotate("", xy=(tc - 1.5, 15), xytext=(tc + 1.5, 15),
                         arrowprops=dict(arrowstyle="|-|", color=INK, lw=1.1,
                                         mutation_scale=4))
            if tc < evs[1].time - 5:
                asx.text(tc + 2.0, 15, "±1.5 s gather", va="center", fontsize=10.5, color=INK)
    asx.set_ylim(0, 17)
    asx.set_ylabel("assessor\ncells per 1 s bin", fontsize=11.5)
    asx.tick_params(axis="x", labelbottom=False)
    letter(asx, "E", x=LX, y=0.95)

    # the count detector: distinct cells per 2 s bin
    cd = count_detect(trains, (0.0, d["duration"]), bin_sec=2.0, min_rois=K)
    _bars(cdx, cd.obs, 2.0, t0, t1, cd.threshold, cols, evs)
    cdx.set_ylabel("count detector\ncells per 2 s bin", fontsize=11.5)
    letter(cdx, "F", x=LX, y=0.95)
    minutes_axis(cdx, t0, t1)
    cdx.set_xlabel("time in the recording")

    # enlargements: one event each, in four stacked panels
    for zi, e in enumerate(evs):
        base = 5 * zi
        zl = fig.add_subplot(zg[base])
        zr = fig.add_subplot(zg[base + 1], sharex=zl)
        zh = fig.add_subplot(zg[base + 2], sharex=zl)
        zw = fig.add_subplot(zg[base + 3], sharex=zl)
        _zoom(zl, zr, zh, zw, e, cols[zi], trains, sigma=d["sigma"], label=f"event {zi + 1}")
        letter(zl, "BC"[zi], x=-0.3, y=0.0)

    handles = [Line2D([], [], color="black", marker="|", ls="none", ms=11, mew=2,
                      label="onset (any cell)"),
               Line2D([], [], color=EV1, marker="v", ls="none", ms=9,
                      label="event 1 time: split\nby a 1 s window border"),
               Line2D([], [], color=EV2, marker="v", ls="none", ms=9,
                      label="event 2 time: caught\nwhole at every width"),
               Patch(color=EV1, label=f"count from event 1's\n{evs[0].n_part} cells"),
               Patch(color=EV2, label=f"count from event 2's\n{evs[1].n_part} cells"),
               Patch(color=GREY, label="count from other\nonsets (on top)"),
               Patch(facecolor="#f4f4f4", edgecolor="#dddddd",
                     label="alternate windows\nor bins shaded"),
               Line2D([], [], color=INK, ls="--", lw=1.2, label=f"threshold K = {K} cells"),
               Line2D([], [], color=INK, lw=1.2,
                      label=f"expected onsets per frame,\nGaussian SD σ = {d['sigma']:g} s")]
    leg_ax.legend(handles=handles, loc="lower center", frameon=False, fontsize=10.5, ncol=4,
                  handlelength=1.6, columnspacing=1.4)
    title = "What the data look like, and what each tool sees"
    return save(fig, name("data-and-what-each-tool-sees", "raster"), title, out)


LX = -0.2      # panel letters of the left column, in axes units


def _stack(ax, edges, n_all, n_ev, cols, label_counts=True):
    """One bar per window or bin: each event's share in its color, the rest in grey on top."""
    for b in range(len(n_all)):
        lo, w = edges[b], edges[b + 1] - edges[b]
        ax.axvspan(lo, lo + w, color="#f4f4f4" if b % 2 else "white", lw=0, zorder=0,
                   ymin=0, ymax=1)   # full height of the panel, no edge
        base = 0
        for i in range(2):
            if n_ev[i][b]:
                ax.bar(lo, n_ev[i][b], width=w, bottom=base, align="edge", color=cols[i],
                       edgecolor="white", lw=0.4, zorder=2)
                if label_counts:
                    ax.text(lo + w / 2, n_all[b] + 0.5, str(int(n_ev[i][b])), ha="center",
                            va="bottom", fontsize=10.5, color=cols[i], fontweight="bold")
                base += n_ev[i][b]
        rest = n_all[b] - base
        if rest > 0:
            ax.bar(lo, rest, width=w, bottom=base, align="edge", color=GREY,
                   edgecolor="white", lw=0.4, zorder=2)
    for sp in ("top", "right"):
        ax.spines[sp].set_visible(False)


def _bars(ax, obs, bw, t0, t1, K, cols, evs):
    """Distinct cells per bin, as the tool counts them (from 0 s), with its threshold."""
    b0, b1 = int(np.floor(t0 / bw)), int(np.ceil(t1 / bw))
    edges = np.arange(b0, b1 + 1) * bw
    n_all = obs[b0:b1]
    n_ev = []
    for e in evs:
        cnt = np.zeros(b1 - b0)
        for b in range(b0, b1):         # distinct participant cells with an onset in the bin
            on = np.asarray(e.onsets)
            cnt[b - b0] = len(set(np.asarray(e.rois)[(on >= b * bw) & (on < (b + 1) * bw)]))
        n_ev.append(cnt)
    _stack(ax, edges, n_all, n_ev, cols)
    ax.axhline(K, color=INK, ls="--", lw=1.2, zorder=3)
    ax.set_ylim(0, 15); ax.set_yticks([0, K, 10])


def _zoom(zl, zr, zh, zw, e, col, trains, sigma, label):
    """One event enlarged: its time (lane), its cells' onsets (raster, one ink), the spread of
    its onsets about the event time with sigma marked, and the tools' three window grids."""
    half = 1.6
    lo, hi = e.time - half, e.time + half
    rois = sorted(int(r) for r in e.rois)
    n = len(rois)
    # lane: the planted time, pointing down at the raster
    zl.plot(0, 0.5, marker="v", ms=10, color=col)
    zl.text(0.15, 0.5, label, color=col, va="center", fontsize=10.5)
    zl.set_ylim(0, 1); zl.axis("off")
    # raster: every onset in view, of the event's cells (one row each) and of all other cells
    xs, ys = [], []
    for j, r in enumerate(rois):
        tr = trains[r]
        for o in tr[(tr >= lo) & (tr < hi)]:
            xs.append(o - e.time); ys.append(j)
    for r, tr in enumerate(trains):
        if r in rois:
            continue
        for o in tr[(tr >= lo) & (tr < hi)]:
            xs.append(o - e.time); ys.append(n + 0.9)
    zr.plot(xs, ys, color="black", marker="|", ls="none", ms=8, mew=1.8)
    zr.set_ylim(n + 1.6, -0.8)
    zr.set_yticks([(n - 1) / 2, n + 0.9])
    zr.set_yticklabels([f"its {n}\ncells", "other\ncells"], fontsize=10)
    zr.tick_params(axis="y", length=0)
    zr.tick_params(axis="x", labelbottom=False)
    for sp in ("top", "right", "left"):
        zr.spines[sp].set_visible(False)
    # spread: the event's onsets per 0.1 s frame, the Gaussian they were drawn from, and sigma
    rel = np.asarray(e.onsets) - e.time
    edges = np.arange(-half, half + 1e-9, 0.1) - 0.05
    zh.hist(rel, bins=edges, color=col, edgecolor="white", lw=0.4)
    g = np.linspace(-half, half, 300)
    dens = n * 0.1 * np.exp(-0.5 * (g / sigma) ** 2) / (sigma * np.sqrt(2 * np.pi))
    zh.plot(g, dens, color=INK, lw=1.2)
    ytop = max(dens.max(), np.histogram(rel, edges)[0].max())
    ya = dens.max() * np.exp(-0.5)
    zh.annotate("", xy=(-sigma, ya), xytext=(sigma, ya),
                arrowprops=dict(arrowstyle="<->", color=INK, lw=1.1, shrinkA=0, shrinkB=0))
    zh.text(sigma + 0.1, ya, f"σ = {sigma:g} s", fontsize=10, va="center")
    zh.set_ylim(0, ytop * 1.25)
    zh.set_ylabel("onsets\nper frame", fontsize=10)
    zh.tick_params(axis="x", labelbottom=False)
    zh.tick_params(axis="y", labelsize=10)
    for sp in ("top", "right"):
        zh.spines[sp].set_visible(False)
    # window grids: one band per width, each window shaded by its share of the event's onsets
    yb = {1.0: 2, 2.0: 1, 4.0: 0}
    on = np.asarray(e.onsets)
    for w, y in yb.items():
        for b in range(int(np.floor(lo / w)) - 1, int(np.ceil(hi / w)) + 1):
            a = b * w
            holds = int(np.sum((on >= a) & (on < a + w)))
            zw.add_patch(Rectangle((a - e.time, y - 0.42), w, 0.84,
                                   facecolor=col if holds else "white",
                                   alpha=min(1.0, 0.15 + 0.85 * holds / len(on)),
                                   edgecolor="#555", lw=0.8))
            if holds:
                xm = np.clip(a + w / 2, lo + 0.15, hi - 0.15) - e.time
                zw.text(xm, y, f"{holds}", ha="center", va="center", fontsize=10.5,
                        color="white" if holds / len(on) > 0.55 else INK)
    zw.set_ylim(-0.6, 2.6)
    zw.set_yticks(list(yb.values()))
    zw.set_yticklabels([f"{w:g} s windows" if w == 1 else f"{w:g} s" for w in yb], fontsize=10)
    zw.tick_params(axis="y", length=0)
    zw.set_xlim(-half, half)
    ticks = [-1.5, -1, -0.5, 0, 0.5, 1, 1.5]
    zw.set_xticks(ticks)
    zw.set_xticklabels([time_axis.label(t) if t in (-1, 0, 1) else "" for t in ticks])
    zw.set_xlabel("time from the event", fontsize=10.5)
    for sp in ("top", "right", "left"):
        zw.spines[sp].set_visible(False)


# --------------------------------------------------------------------------- B. window sharing

def g_uniform(n: int, w: float, s: float) -> float:
    """Window sharing for onsets jittered uniformly on [-s, s]: E[max(0, 1 - R_n / w)].

    R_n = 2 s U, U the range of n iid uniforms on [0, 1], density n (n - 1) u^(n-2) (1 - u).
    Computed by numerical integration (scipy.integrate.quad) up to u = w / 2s, where the
    integrand reaches zero."""
    a = min(1.0, w / (2 * s))
    f = lambda u: (1 - 2 * s * u / w) * n * (n - 1) * u ** (n - 2) * (1 - u)  # noqa: E731
    return float(integrate.quad(f, 0.0, a, limit=200)[0])


def fig_sharing(out):
    tc_rows = json.loads((SV / "aim1_one_source.json").read_text())["rows"]
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(11, 5.6),
                                 gridspec_kw=dict(wspace=0.3, left=0.085, right=0.985,
                                                  top=0.93, bottom=0.3))
    # A: g2 and g3 against w / sigma. Both jitters have SD sigma; the uniform one is
    # uniform on [-s, s] with s = sqrt(3) sigma.
    u = np.geomspace(0.2, 60, 400)
    s_u = np.sqrt(3.0)
    for n_, col in ((2, "#2a78d6"), (3, "#0d366b")):
        a1.plot(u, [theory.g(n_, x, 1.0) for x in u], color=col, lw=2.2)
        a1.plot(u, [g_uniform(n_, x, s_u) for x in u], color=col, lw=1.6, ls="--")
    a1.axvline(2 * s_u, color=GREY, ls=":", lw=1.2)
    a1.text(2 * s_u * 1.07, 0.04, "window = full width\nof uniform jitter\n(2√3 σ)",
            fontsize=10, color="#555", va="bottom")
    gap = [max(abs(theory.g(n_, x, 1.0) - g_uniform(n_, x, s_u)) for x in u) for n_ in (2, 3)]
    a1.text(0.03, 0.97, f"Gaussian and uniform differ by\nat most {gap[0]:.2f} (g$_2$) "
            f"and {gap[1]:.2f} (g$_3$)",
            transform=a1.transAxes, ha="left", va="top", fontsize=10.5, color="#333")
    a1.set_xscale("log"); a1.set_xlim(u[0], u[-1]); a1.set_ylim(0, 1.02)
    a1.set_xticks([0.2, 0.5, 1, 2, 5, 10, 20, 50])
    a1.set_xticklabels(["0.2", "0.5", "1", "2", "5", "10", "20", "50"])
    a1.set_xlabel("window ÷ jitter SD, w/σ")
    a1.set_ylabel("chance one window holds all\nn onsets of an event, g$_n$")
    style(a1); letter(a1, "A")
    h1 = [Line2D([], [], color="#2a78d6", lw=2.2, label="2 onsets (g$_2$), Gaussian jitter"),
          Line2D([], [], color="#0d366b", lw=2.2, label="3 onsets (g$_3$), Gaussian jitter"),
          Line2D([], [], color="#555", lw=1.6, ls="--",
                 label="uniform jitter of the same SD\n(numerical integration)")]
    a1.legend(handles=h1, loc="upper center", bbox_to_anchor=(0.5, -0.17), ncol=1,
              frameon=False, fontsize=10.5)

    # B: k-hat / k against sigma / w, and the first experiment's medians
    x = np.geomspace(0.008, 2.0, 300)
    for k, col in K_COL.items():
        kh = [(2 + (k - 2) * theory.g(3, 1.0, xx) / theory.g(2, 1.0, xx)) / k for xx in x]
        a2.plot(x, kh, color=col, lw=2.2)
    mk = {1.0: "o", 2.0: "s", 4.0: "^"}
    n_nan = 0
    for k in (10, 20):
        for sig in (0.05, 0.2, 0.5, 1.0):
            for w in theory.WINDOWS:
                v = [r["coord_rates"][str(w)]["k"] / r["true"]["k"] for r in tc_rows
                     if r["true"]["bg_rate"] == 0.01 and r["true"]["k"] == k
                     and r["true"]["jitter"] == sig]
                fin = np.asarray([y for y in v if y is not None and np.isfinite(y)])
                n_nan += len(v) - fin.size
                if not fin.size:
                    continue
                q1, med, q3 = np.percentile(fin, [25, 50, 75])
                a2.errorbar(sig / w, med, yerr=[[med - q1], [q3 - med]], fmt=mk[w], ms=7,
                            color=K_COL[k], mec="white", mew=0.6, elinewidth=1, capsize=0,
                            zorder=3)
                # the full prediction (with the at-most-one-event term), mean over the
                # condition's two event counts, through the tool's own solve()
                full = np.mean([theory.predict_solve(k, sig, w, E / 2700.0, 33)["k"]
                                for E in (15, 45)])
                a2.plot(sig / w, full, marker="_", ms=13, mew=2.2, color="#e0a100", zorder=2)
    a2.set_xscale("log"); a2.set_xlim(x[0], x[-1]); a2.set_ylim(0, 1.12)
    a2.axhline(1, color="#888", lw=0.8, ls=":")
    a2.text(1.9, 1.015, "no bias", ha="right", va="bottom", fontsize=10, color="#555")
    a2.set_xticks([0.01, 0.02, 0.05, 0.1, 0.2, 0.5, 1, 2])
    a2.set_xticklabels(["0.01", "0.02", "0.05", "0.1", "0.2", "0.5", "1", "2"])
    a2.set_xlabel("jitter SD ÷ window, σ/w")
    a2.set_ylabel(r"participants reported ÷ planted, $\hat{k}/k$")
    style(a2); letter(a2, "B")
    h2 = [Line2D([], [], color=c, lw=2.2, label=f"{k} cells per event") for k, c in K_COL.items()]
    h2 += [Line2D([], [], color="#555", marker=m, ls="none", ms=7,
                  label=f"measured, {w:g} s window") for w, m in mk.items()]
    h2 += [Line2D([], [], color="#e0a100", marker="_", ls="none", ms=14, mew=2.2,
                  label="full prediction")]
    a2.legend(handles=h2, loc="upper center", bbox_to_anchor=(0.5, -0.17), ncol=2,
              frameon=False, fontsize=10.5, columnspacing=1.2)
    note = ("lines: [2 + (k − 2) g$_3$/g$_2$] ÷ k, no at-most-one-event term\n"
            "points: median of 10 recordings (bars, quartiles),\n"
            "background 0.01 Hz, 10- and 20-cell events")
    a2.text(0.03, 0.04, note, transform=a2.transAxes, fontsize=10, va="bottom", color="#333")
    if n_nan:
        print(f"  sharing: {n_nan} measured estimates were refused by the tool and left out")
    title = "Window sharing, and the participant bias it causes"
    return save(fig, name("window-sharing-and-participant-bias", "recovery"), title, out)


# --------------------------------------------------------------------------- C. chance clusters

def fig_chance(out):
    """Chance clusters per minute against the assessor's threshold K. The first K under one per
    hour is bugarach.event_floor.floor_of at the estate's FA_PER_HOUR, the same rule the event
    floor uses, applied to the predicted rate."""
    from bugarach.event_floor import FA_PER_HOUR, floor_of
    tc = json.loads((SV / "theory_check.json").read_text())
    aim = json.loads((SV / "aim1_one_source.json").read_text())
    n_rec = {bg: sum(1 for r in aim["chance_arm"] if r["bg_rate"] == bg) for bg in (0.01, 0.05)}
    minutes = aim["duration_sec"] / 60.0
    N = aim["n_roi"]
    Ks = np.arange(3, 11)
    budget = FA_PER_HOUR / 60.0              # per minute
    y_lo = 1e-8
    fig, ax = plt.subplots(figsize=(10, 6.2))
    fig.subplots_adjust(left=0.1, right=0.985, top=0.97, bottom=0.2)
    # direct labels at each line's right end; 0.01 and 0.0096 Hz end together, so one goes
    # above and one below
    dy = {0.0096: -11, 0.01: 11, 0.05: 0}
    for bg, col in BG_COL.items():
        per_hour = [theory.chance_clusters_per_min(N, bg, K) * 60 for K in range(0, N + 1)]
        safe = floor_of(per_hour, FA_PER_HOUR)
        pred = np.array([per_hour[int(K)] / 60 for K in Ks])
        vis = pred >= y_lo
        ax.plot(Ks[vis], pred[vis], color=col, lw=2, marker="o", mfc="white", mec=col, ms=7,
                mew=1.5, zorder=2)
        xe, ye = Ks[vis][-1], pred[vis][-1]
        real = ", realistic" if bg == 0.0096 else ""
        ax.annotate(f"{bg:g} Hz{real}: first K under\none per hour: {safe} cells "
                    f"({per_hour[safe]:.2f} per hour)",
                    (xe, ye), textcoords="offset points", xytext=(12, dy[bg]), color=col,
                    fontsize=10.5, va="center", ha="left")
    for bg in (0.01, 0.05):
        col = BG_COL[bg]
        for c in (c for c in tc["chance"] if c["bg"] == bg):
            x = c["K"] + (0.1 if bg == 0.05 else -0.1)
            if c["pooled_count"] == 0:
                ax.plot(x, c["pooled_rate_ci"][1], marker="v", color=col, ms=9, ls="none",
                        zorder=3)
                ax.annotate(f"0 clusters in {n_rec[bg] * minutes:,.0f} min:\n95 % upper bound",
                            (x, c["pooled_rate_ci"][1]), textcoords="offset points",
                            xytext=(10, -4), fontsize=10, color="#333", va="top")
            else:
                y = c["pooled_rate"]
                ax.errorbar(x, y, yerr=[[y - c["pooled_rate_ci"][0]], [c["pooled_rate_ci"][1] - y]],
                            fmt="o", color=col, ms=7, capsize=3, zorder=3)
    ax.axhline(budget, color=INK, ls="--", lw=1.2)
    ax.text(4.6, budget * 1.25, "one chance cluster per hour", ha="left", va="bottom",
            fontsize=10.5)
    # 0.0096 and 0.01 Hz are one line at this scale but labeled 4 and 5: say why (role 8 F4)
    ph4 = theory.chance_clusters_per_min(N, 0.0096, 4) * 60
    ax.annotate(f"0.0096 Hz sits on the budget line at K = 4\n({ph4:.2f} per hour), so K = 5 is "
                "the safe\nchoice there, as at 0.01 Hz", (4, ph4 / 60), xytext=(2.65, 3e-6),
                fontsize=10, color=BG_COL[0.0096], ha="left", va="center",
                arrowprops=dict(arrowstyle="-", color=BG_COL[0.0096], lw=0.9, shrinkB=5))
    measured_K = sorted({c["K"] for c in tc["chance"]})
    for K in Ks:
        if K not in measured_K:
            ax.axvspan(K - 0.5, K + 0.5, color="#f0f0f0", zorder=0, lw=0)
    ax.set_yscale("log"); ax.set_ylim(y_lo, 30); ax.set_xlim(2.5, 13.6)
    ax.set_xticks(Ks)
    ax.spines["bottom"].set_bounds(2.5, 10.5)
    ax.set_xlabel("assessor's threshold K (cells in one 1 s bin, of 33)", x=0.36)
    ax.set_ylabel("chance clusters per minute\n(background only)")
    for sp in ("top", "right"):
        ax.spines[sp].set_visible(False)
    ax.grid(True, axis="y", color="#e5e5e5", lw=0.6)
    handles = [Line2D([], [], color="#555", lw=2, marker="o", mfc="white", mec="#555",
                      label="predicted"),
               Line2D([], [], color="#555", marker="o", ls="none", ms=7,
                      label=f"measured, {n_rec[0.01]} background-only recordings "
                            f"({n_rec[0.01] * minutes:,.0f} min) each,\n95 % interval "
                            "(intervals smaller than markers)"),
               Patch(facecolor="#f0f0f0", edgecolor="#cccccc", label="K not measured")]
    fig.legend(handles=handles, loc="lower center", bbox_to_anchor=(0.5, 0.0), ncol=3,
               frameon=False, fontsize=10.5, columnspacing=1.6, handlelength=1.8)
    title = "Chance clusters against the assessor's threshold"
    return save(fig, name("chance-clusters-against-threshold", "recovery"), title, out)


# --------------------------------------------------------------------------- D. order power

ORDER_POWER = SV / "ch1_followups" / "order_power.json"
R_COL = {1.0: "#86b6ef", 2.5: "#2a78d6", 5.0: "#0d366b"}


def fig_order(out):
    """Power to detect order against events per recording, from the exact-size (randomized)
    5 % test in ch1_followups/order_power.json (order_power.py beside it)."""
    op = json.loads(ORDER_POWER.read_text())
    Es, n_cells, reps = op["Es"], op["N"], op["reps"]
    fig, axes = plt.subplots(1, 2, figsize=(10.5, 5.0), sharey=True,
                             gridspec_kw=dict(wspace=0.08, left=0.085, right=0.985,
                                              top=0.93, bottom=0.22))
    for ax, k in zip(axes, op["ks"]):
        rows = sorted((r for r in op["rows"] if r["k"] == k), key=lambda r: r["E"])
        for rr in op["rs"]:
            for M, ls in ((1, "-"), (2, "--")):
                key = f"r={rr:g},M={M}"
                p = [r["power_randomized"][key] for r in rows]
                ax.plot([r["E"] for r in rows], p, color=R_COL[rr], ls=ls, lw=2,
                        marker="o" if M == 1 else "s", ms=6,
                        mfc=R_COL[rr] if M == 1 else "white", mec=R_COL[rr], mew=1.5)
        ax.axhline(0.8, color=INK, ls="-.", lw=1.2)
        ax.axhline(0.05, color=INK, ls=":", lw=1.2)
        ax.set_xticks(Es); ax.set_xlim(0.7, max(Es) + 0.3); ax.set_ylim(0, 1.04)
        ax.set_xlabel(f"events per recording, E ({k} of {n_cells} cells per event)")
        style(ax)
    axes[0].annotate("E = 1, both panels: the indicator\nis 1 under the null too, so no test\n"
                     "has power; it equals the test size", (1, 0.05), textcoords="axes fraction",
                     xytext=(0.03, 0.97), va="top", fontsize=10.5, color="#333",
                     arrowprops=dict(arrowstyle="-", color="#888", lw=0.8))
    axes[0].set_ylabel(f"power to detect order\n(share of {reps} recordings)")
    letter(axes[0], "A"); letter(axes[1], "B")
    tr = axes[1].get_yaxis_transform()
    axes[1].text(0.02, 0.8 + 0.015, "power 0.8", transform=tr, fontsize=10.5, va="bottom")
    axes[1].text(0.98, 0.05 + 0.015, "test size 0.05", transform=tr, fontsize=10.5,
                 va="bottom", ha="right")
    handles = [Line2D([], [], color=c, lw=2, label=f"r = {rr:g}") for rr, c in R_COL.items()]
    handles += [Line2D([], [], color="#555", lw=2, ls="-", marker="o", ms=6,
                       label="one template"),
                Line2D([], [], color="#555", lw=2, ls="--", marker="s", ms=6, mfc="white",
                       label="two templates")]
    # one row; the reference lines are labeled in panel B, and the test and r are defined in
    # the caption (round 3, role 9 F10)
    fig.legend(handles=handles, loc="lower center", bbox_to_anchor=(0.5, 0.0), ncol=5,
               frameon=False, fontsize=10.5, columnspacing=1.5, handlelength=2.4)
    title = "Power to detect order against the number of events"
    return save(fig, name("order-power-against-event-count", "recovery"), title, out)


# --------------------------------------------------------------------------- E. regime map

LAB = (("fast stream, realistic values", 0.105, 7, "#eb6834", "fast"),
       ("slow stream, realistic values", 0.131, 13, "#8e44ad", "slow"))
HELDOUT = SV / "ch1_followups" / "theory_check_heldout.json"
LAB_VALUES = SV / "ch1_followups" / "lab_values.json"
JF_COL = "#2a78d6"


def _jf_ranges(path):
    """{(sigma, k): [recovered / planted jitter per condition]} from a check() record's joint fit
    (median of each condition's recordings, four conditions per point)."""
    jf = json.loads(path.read_text())["joint_fit"]
    out = {}
    for r in jf:
        out.setdefault((r["sigma"], r["k"]), []).append(r["sigma_q"][1] / r["sigma"])
    return out


def fig_regime(out):
    """The tested grid, judged on both records: the first experiment (theory_check.json) and the
    held-out rerun on fresh seeds (ch1_followups/theory_check_heldout.json). A point is resolved on
    a record when all four of its condition medians fall within 0.8-1.25 of planted. Left half of
    the marker: first experiment; right half: held-out record."""
    first, held = _jf_ranges(SV / "theory_check.json"), _jf_ranges(HELDOUT)
    strips, _ = _lab_strips()      # the same per-recording record as fig_jointfit C
    lo_ok, hi_ok = 0.8, 1.25
    fig, ax = plt.subplots(figsize=(10, 6.4))
    fig.subplots_adjust(left=0.085, right=0.985, top=0.97, bottom=0.2)
    for (sig, k) in sorted(first):
        ok = [all(lo_ok <= q <= hi_ok for q in rec[(sig, k)]) for rec in (first, held)]
        if all(ok):
            kw = dict(color=JF_COL, mec=JF_COL)
        elif not any(ok):
            kw = dict(color="white", mec="#888")
        else:
            kw = dict(color=JF_COL, mec=JF_COL, markerfacecoloralt="white",
                      fillstyle="left" if ok[0] else "right")
        ax.plot(sig, k, marker="o", ms=15, ls="none", mew=2, zorder=3, **kw)
        r1, r2 = first[(sig, k)], held[(sig, k)]
        ax.text(sig * 1.09, k - 1.55, f"{min(r1):.2f}–{max(r1):.2f}\n{min(r2):.2f}–{max(r2):.2f}",
                fontsize=10, color="#444", ha="left", va="center", linespacing=1.15)
    for lab_name, sig, k, col, stream in LAB:
        ax.add_patch(Rectangle((sig / 1.1, k - 1), sig * 1.1 - sig / 1.1, 2, facecolor=col,
                               alpha=0.25, edgecolor=col, lw=2, zorder=2))
        d = strips[(stream, k, "general")]
        within = int(np.sum((d["ratio"] >= lo_ok) & (d["ratio"] <= hi_ok)))
        ax.annotate(f"{lab_name}\nσ {sig:g} s, ~{k} cells\nsimulated there:\n"
                    f"{within} of {d['ratio'].size} recordings\n"
                    f"within {lo_ok}–{hi_ok}", (sig / 1.1, k), xytext=(0.04, k + 0.6),
                    ha="right", va="center", fontsize=10, color=col,
                    arrowprops=dict(arrowstyle="-", color=col, lw=1, shrinkA=2, shrinkB=0))
    ax.set_xscale("log"); ax.set_xlim(0.012, 1.8); ax.set_ylim(2, 23)
    ax.set_xticks([0.05, 0.1, 0.2, 0.5, 1.0])
    ax.set_xticklabels(["0.05", "0.1", "0.2", "0.5", "1"])
    ax.set_yticks([5, 7, 10, 13, 20])
    ax.set_xlabel("planted jitter σ (s)")
    ax.set_ylabel("cells per event, k (of 33)")
    style(ax)
    handles = [Line2D([], [], color=JF_COL, marker="o", ls="none", ms=12, mew=2,
                      label="resolved on both records"),
               Line2D([], [], color=JF_COL, mec=JF_COL, markerfacecoloralt="white",
                      fillstyle="left", marker="o", ls="none", ms=12, mew=2,
                      label="first experiment only\n(left half filled)"),
               Line2D([], [], color="white", mec="#888", marker="o", ls="none", ms=12, mew=2,
                      label="resolved on neither"),
               Line2D([], [], ls="none", label="numbers: range of the four ratios,\n"
                                               "first experiment over held-out")]
    # no point is resolved on the held-out record only, so that key entry is drawn only if one is
    if any((not all(lo_ok <= q <= hi_ok for q in first[c])) and all(lo_ok <= q <= hi_ok
                                                                    for q in held[c])
           for c in first):
        handles.insert(2, Line2D([], [], color=JF_COL, mec=JF_COL, markerfacecoloralt="white",
                                 fillstyle="right", marker="o", ls="none", ms=12, mew=2,
                                 label="held-out record only\n(right half filled)"))
    handles += [Patch(facecolor=col, alpha=0.35, edgecolor=col, lw=1.5, label=lab_name)
                for lab_name, _, _, col, _ in LAB]
    fig.legend(handles=handles, loc="lower center", bbox_to_anchor=(0.5, 0.0), ncol=3,
               frameon=False, fontsize=10.5, columnspacing=1.6, handletextpad=0.5)
    title = "Realistic parameter values against the tested grid, on both records"
    return save(fig, name("realistic-values-against-tested-grid", "recovery"), title, out)


# --------------------------------------------------------------------------- F. residuals

REC_COL = {"first experiment": "#2a78d6", "held-out record": "#eb6834"}
K_MARK = {10: "o", 20: "s"}


def _resid_rows(path, bg):
    """Condition-windows with events of 10+ cells: signed residual (measured - predicted) / planted
    and its SE, in theory.summary's convention: 1.2533 SD / sqrt(n) for a median of n."""
    cr = json.loads(path.read_text())["coord_rates"]
    rows = []
    for r in cr:
        m = r["meas"]["k"]
        if r["bg"] != bg or r["k"] < 10 or m is None or not np.isfinite(m):
            continue
        se = 1.2533 * max(r["meas_sd"]["k"], 1e-9) / np.sqrt(r["n"] - r["n_nan"])
        rows.append(dict(sigma=r["sigma"], w=r["w"], k=r["k"], E=r["n_events"],
                         res=m - r["exact"]["k"], se=se))
    return rows


def fig_residuals(out):
    """Participant residuals on both records, per condition-window, ordered by sigma / w.
    Counts beyond 2 SE and the sign tests are theory.summary's (one sign per condition: the
    three windows reuse the same recordings)."""
    from scipy import stats
    recs = {"first experiment": SV / "theory_check.json", "held-out record": HELDOUT}
    fig, axes = plt.subplots(2, 1, figsize=(11, 10),
                             gridspec_kw=dict(hspace=0.62, left=0.1, right=0.985, top=0.885,
                                              bottom=0.13))
    for ax, bg, let in zip(axes, (0.01, 0.05), "AB"):
        data = {lab: _resid_rows(p, bg) for lab, p in recs.items()}
        key = lambda r: (r["sigma"] / r["w"], r["sigma"], r["k"], r["E"])  # noqa: E731
        order = sorted({key(r) for r in data["first experiment"]})
        pos = {c: i for i, c in enumerate(order)}
        notes = []
        for j, (lab, rows) in enumerate(data.items()):
            col = REC_COL[lab]
            for r in rows:
                x = pos[key(r)] + (-0.18 if j == 0 else 0.18)
                ax.errorbar(x, r["res"], yerr=2 * r["se"], fmt=K_MARK[r["k"]], color=col, ms=5,
                            mec=col, mfc=col if r["E"] == 45 else "white", mew=1.2,
                            elinewidth=1, capsize=0, zorder=3)
            nz = sum(abs(r["res"]) > 2 * r["se"] for r in rows)
            byc = defaultdict(list)
            for r in rows:
                byc[(r["sigma"], r["k"], r["E"])].append(r["res"])
            below = sum(np.mean(v) < 0 for v in byc.values())
            p = stats.binomtest(below, len(byc)).pvalue
            med = np.median([r["res"] for r in rows])
            notes.append((col, f"{lab}: {nz} of {len(rows)} beyond 2 SE; median {med:+.3f}; "
                               f"below predicted in {below} of {len(byc)} conditions "
                               f"(sign test p = {p:.2f})"))
        # group separators and sigma / w ticks
        groups = defaultdict(list)
        for c, i in pos.items():
            groups[round(c[0], 6)].append(i)
        for gi, (sw, idx) in enumerate(sorted(groups.items())):
            if gi:
                ax.axvline(min(idx) - 0.5, color="#dddddd", lw=0.8, zorder=0)
        ax.set_xticks([np.mean(idx) for _, idx in sorted(groups.items())])
        ax.set_xticklabels([f"{sw:g}" for sw, _ in sorted(groups.items())])
        ax.set_xlim(-0.7, len(order) - 0.3)
        ax.axhline(0, color=INK, lw=1.1, zorder=1)
        ax.set_ylabel("participants: (measured −\npredicted) ÷ planted")
        ax.set_xlabel("jitter SD ÷ window, σ/w (condition-windows of 10 and 20 cells, "
                      "15 and 45 events)", fontsize=11)
        for sp in ("top", "right"):
            ax.spines[sp].set_visible(False)
        ax.grid(True, axis="y", color="#e5e5e5", lw=0.6)
        lo = min(r["res"] - 2 * r["se"] for rows in data.values() for r in rows)
        hi = max(r["res"] + 2 * r["se"] for rows in data.values() for r in rows)
        pad = 0.05 * (hi - lo)
        ax.set_ylim(lo - pad, hi + pad)
        n_lines = len(notes) + (1 if bg == 0.01 else 0)
        y_top = 1.03 + 0.075 * n_lines
        ax.text(0.0, y_top, f"background {bg:g} Hz per cell", transform=ax.transAxes,
                fontsize=11.5, va="bottom", fontweight="bold")
        for i, (col, t) in enumerate(notes):
            ax.text(0.0, y_top - 0.075 * (i + 1), t, transform=ax.transAxes, ha="left",
                    va="bottom", fontsize=10.5, color=col)
        letter(ax, let, x=-0.07, y=y_top)
        if bg == 0.01:
            # one sign per condition, both records together (theory.summary's per-condition rule)
            tot_b = tot_n = 0
            for p_ in recs.values():
                byc = defaultdict(list)
                for r in _resid_rows(p_, bg):
                    byc[(r["sigma"], r["k"], r["E"])].append(r["res"])
                tot_b += sum(np.mean(v) < 0 for v in byc.values()); tot_n += len(byc)
            pb = stats.binomtest(tot_b, tot_n).pvalue
            ax.text(0.0, y_top - 0.075 * (len(notes) + 1), f"both records: below predicted "
                    f"in {tot_b} of {tot_n} conditions (sign test p = {pb:.3f})",
                    transform=ax.transAxes, ha="left", va="bottom", fontsize=10.5, color=INK)
    handles = [Line2D([], [], color=c, marker="o", ls="none", ms=6, label=lab)
               for lab, c in REC_COL.items()]
    handles += [Line2D([], [], color="#555", marker="o", ls="none", ms=6, label="10 cells"),
                Line2D([], [], color="#555", marker="s", ls="none", ms=6, label="20 cells"),
                Line2D([], [], color="#555", marker="o", ls="none", ms=6, label="45 events"),
                Line2D([], [], color="#555", marker="o", mfc="white", ls="none", ms=6,
                       label="15 events"),
                Line2D([], [], color="#555", lw=1, label="±2 SE (1.2533 SD / √n, n = 5)"),
                Line2D([], [], color=INK, lw=1.1, label="zero: measured = predicted")]
    fig.legend(handles=handles, loc="lower center", bbox_to_anchor=(0.5, 0.0), ncol=4,
               frameon=False, fontsize=10.5, columnspacing=1.5)
    title = "Participant residuals on the first experiment and the held-out record"
    return save(fig, name("participant-residuals-two-records", "recovery"), title, out)


# --------------------------------------------------------------------------- G. joint fit

CVJ = SV / "ch1_followups" / "correlogram_vs_joint.json"
METH_COL = {"correlogram": "#8a8a8a", "joint": "#7b3fb5"}
FORM_COL = {"page": "#7b3fb5", "general": "#178f6a"}   # hard-core in the joint fit's violet, as in A, B


REALISTIC_COUNTS = SV / "ch1_followups" / "realistic_counts.json"


def _lab_strips():
    """Per-recording fitted / planted jitter at the realistic values, per (stream, k, form), and
    a label for the event counts.

    From ch1_followups/realistic_counts.json when it exists: the round-2 rerun at the tabulated
    event counts (9.7 and 22.0 per hour, the measured interval lists thinned), where "general" is
    the general form given the true train and "page" the hard-core form theory.check runs.
    Otherwise from ch1_followups/lab_values.json (lam = 1 / mean interval, 25.5 and 53.6 events
    per recording)."""
    if REALISTIC_COUNTS.exists():
        rc = json.loads(REALISTIC_COUNTS.read_text())
        strips = {}
        for stream in ("fast", "slow"):
            sig = rc[stream]["sigma"]
            for k in rc[stream]["ks"]:
                for form, key in (("page", "page"), ("general", "true")):
                    s_ = np.array([f["sigma"] for f in rc[stream]["fits"][str(k)][key]])
                    # at bound: within 2 % of the fit's sigma limits, 0.005 s and 5 s (as the
                    # run's own summary counts it)
                    nb = int(np.sum((s_ <= 0.005 * 1.02) | (s_ >= 5.0 / 1.02)))
                    fs = next(f for f in rc[stream]["fit_summary"]
                              if f["k"] == k and f["form"] == key)
                    assert nb == fs["sigma_lo"] + fs["sigma_hi"], (stream, k, key, nb)
                    strips[(stream, k, form)] = dict(ratio=s_ / sig, at_bound=nb, sigma=sig)
        ev = {s: np.mean(rc[s]["events_per_recording"]) for s in ("fast", "slow")}
        src = (f"tabulated event counts, {ev['fast']:.1f} (fast) and {ev['slow']:.1f} (slow) "
               "events per recording")
        return strips, src
    lab = json.loads(LAB_VALUES.read_text())
    strips = {}
    for stream in ("fast", "slow"):
        sig = lab[stream]["sigma"]
        for k in lab[stream]["ks"]:
            for form in ("page", "general"):
                fits = [f for f in lab[stream]["fits"] if f["k"] == k and f["form"] == form]
                strips[(stream, k, form)] = dict(
                    ratio=np.array([f["sigma"] / sig for f in fits]),
                    at_bound=sum(bool(f["sigma_at_bound"]) for f in fits), sigma=sig)
    counts = {s: lab[s]["events_per_recording_mean"] for s in ("fast", "slow")}
    src = (f"{counts['fast']:.1f} (fast) and {counts['slow']:.1f} (slow) events per "
           "45-minute recording")
    return strips, src


def fig_jointfit(out):
    """The joint fit against the correlogram tool on the 240 first-experiment recordings
    (ch1_followups/correlogram_vs_joint.json, events of 10+ cells), and the joint fit per
    recording at the realistic values (see _lab_strips for which record)."""
    cv = json.loads(CVJ.read_text())
    h_lo, h_hi = cv["calibration"]["hwhm"][0], cv["calibration"]["hwhm"][-1]
    fig = plt.figure(figsize=(11, 10.4))
    gs = fig.add_gridspec(2, 2, height_ratios=[1, 1.1], hspace=0.45, wspace=0.08, left=0.1,
                          right=0.985, top=0.95, bottom=0.13)
    axA = fig.add_subplot(gs[0, 0])
    axB = fig.add_subplot(gs[0, 1], sharey=axA)
    axC = fig.add_subplot(gs[1, :])
    for ax, bg, let in ((axA, 0.01, "A"), (axB, 0.05, "B")):
        ax.axhspan(0.8, 1.25, color="#eeeeee", zorder=0, lw=0)
        ax.axhline(1, color=INK, lw=0.9, ls=":", zorder=1)
        rows = sorted((r for r in cv["summary"] if r["bg"] == bg and r["cells"] == "10+"),
                      key=lambda r: r["sigma"])
        for r in rows:
            sig = r["sigma"]
            recs = [p for p in cv["per_recording"] if p["bg"] == bg and p["sigma"] == sig
                    and p["k"] >= 10]
            off = [p for p in recs if p["corr_sigma"] is None]
            below = sum(p["hwhm"] is not None and p["hwhm"] < h_lo for p in off)
            above = sum(p["hwhm"] is not None and p["hwhm"] > h_hi for p in off)
            assert below + above == r["correlogram_off"], "an off-curve recording had no width"
            for meth, f, key, mk in (("correlogram", 1 / 1.09, "correlogram_ratio_q", "s"),
                                     ("joint", 1.09, "joint_ratio_q", "o")):
                q1, med, q3 = r[key]
                col = METH_COL[meth]
                ax.errorbar(sig * f, med, yerr=[[med - q1], [q3 - med]], fmt=mk, color=col,
                            ms=8, mec=col, elinewidth=1.4, capsize=3, zorder=3)
                if meth == "correlogram":
                    t = ", ".join(s for s in (f"{above} above" if above else "",
                                              f"{below} below" if below else "") if s)
                    if t:
                        # placed where it clears the other marks and the y = 1 line: above
                        # and left of the 0.05 s marker, beside the 0.05 Hz markers, and
                        # below the 0.01 Hz marker at 1 s
                        txt = t.replace(", ", "\n") + "\nthe curve"
                        if sig < 0.1:
                            ax.text(sig * f / 1.08, q3 + 0.12, txt, ha="right", va="bottom",
                                    fontsize=9.5, color="#555", linespacing=1.05)
                        elif bg == 0.05:
                            ax.text(sig * f / 1.1, med, txt, ha="right", va="center",
                                    fontsize=9.5, color="#555", linespacing=1.05)
                        else:
                            ax.text(sig * f, q1 - 0.05, txt, ha="center", va="top",
                                    fontsize=9.5, color="#555", linespacing=1.05)
                elif r["joint_at_bound"]:
                    ax.text(sig * f, q3 + 0.05, f"{r['joint_at_bound']} at\nthe bound",
                            ha="center", va="bottom", fontsize=9.5, color=col,
                            linespacing=1.05)
        ax.set_xscale("log"); ax.set_xlim(0.019, 1.9)
        ax.set_xticks([0.05, 0.1, 0.2, 0.5, 1.0])
        ax.set_xticklabels(["0.05", "0.1", "0.2", "0.5", "1"])
        ax.minorticks_off()
        ax.set_xlabel("planted jitter σ (s)")
        ax.set_ylim(0, 2.1)
        ax.text(0.0, 1.03, f"background {bg:g} Hz per cell", transform=ax.transAxes,
                fontsize=11, va="bottom")
        style(ax); letter(ax, let, x=-0.03, y=1.03)
    axB.tick_params(labelleft=False)
    axA.set_ylabel("recovered ÷ planted jitter\n(median, interquartile range)")

    # C: per-recording ratio at the realistic values
    strips, src = _lab_strips()
    rng = np.random.default_rng(0)
    axC.axhspan(0.8, 1.25, color="#eeeeee", zorder=0, lw=0)
    axC.axhline(1, color=INK, lw=0.9, ls=":", zorder=1)
    ticks, labels = [], []
    groups = sorted({(s, k) for s, k, _ in strips}, key=lambda g: (g[0] != "fast", g[1]))
    for gi, (stream, k) in enumerate(groups):
        for fi, form in enumerate(("page", "general")):
            d = strips[(stream, k, form)]
            x0 = gi * 2.6 + fi
            xs = x0 + rng.uniform(-0.28, 0.28, d["ratio"].size)
            axC.plot(xs, d["ratio"], "o", ms=4.5, color=FORM_COL[form], alpha=0.75, mew=0,
                     zorder=3)
            med = np.median(d["ratio"])
            axC.plot([x0 - 0.36, x0 + 0.36], [med, med], color=INK, lw=2, zorder=4)
            within = int(np.sum((d["ratio"] >= 0.8) & (d["ratio"] <= 1.25)))
            t = f"{within} of {d['ratio'].size}\nin band"
            if d["at_bound"]:
                t += f" ·\n{d['at_bound']} at\nbound"
            axC.text(x0, 6.2, t, ha="center", va="bottom", fontsize=9.5,
                     color=FORM_COL[form], linespacing=1.05)
        ticks.append(gi * 2.6 + 0.5)
        labels.append(f"{stream} stream, σ {d['sigma']:g} s\n{k} cells per event")
    axC.set_yscale("log"); axC.set_ylim(0.03, 17)
    axC.set_yticks([0.05, 0.1, 0.2, 0.5, 0.8, 1.25, 2, 5])
    axC.set_yticklabels(["0.05", "0.1", "0.2", "0.5", "0.8", "1.25", "2", "5"])
    axC.minorticks_off()
    axC.set_xticks(ticks); axC.set_xticklabels(labels)
    axC.set_xlim(-0.6, (len(groups) - 1) * 2.6 + 1.6)
    axC.set_ylabel("fitted ÷ planted jitter\n(one point per recording)")
    axC.text(0.0, 1.03, f"realistic values (0.0096 Hz per cell), {src}",
             transform=axC.transAxes, fontsize=11, va="bottom")
    style(axC); letter(axC, "C", x=-0.03, y=1.03)
    handles = [Line2D([], [], color=METH_COL["correlogram"], marker="s", ls="none", ms=7,
                      label="A, B: correlogram tool (shipped calibration)"),
               Line2D([], [], color=METH_COL["joint"], marker="o", ls="none", ms=7,
                      label="A, B: joint fit"),
               Line2D([], [], color=FORM_COL["page"], marker="o", ls="none", ms=6,
                      label="C: joint fit, hard-core form"),
               Line2D([], [], color=FORM_COL["general"], marker="o", ls="none", ms=6,
                      label="C: joint fit, general form"),
               Line2D([], [], color=INK, lw=2, label="C: median of 40 recordings"),
               Patch(facecolor="#eeeeee", label="within 0.8–1.25 of planted"),
               Line2D([], [], color=INK, lw=0.9, ls=":", label="recovered = planted")]
    fig.legend(handles=handles, loc="lower center", bbox_to_anchor=(0.5, 0.0), ncol=3,
               frameon=False, fontsize=10.5, columnspacing=1.4)
    title = "The joint fit against the correlogram tool, and at realistic values"
    return save(fig, name("joint-fit-against-correlogram", "recovery"), title, out)


# --------------------------------------------------------------------------- H. schematic

SWAP_COL = "#eb6834"


def _toy_trains(seed=8):
    """Panel A's toy: 4 cells, 60 s, Poisson background (0.05 Hz per cell) and two events of all
    4 cells at 17 s and 41 s, jitter SD 0.2 s. Illustrative values, not a run."""
    rng = np.random.default_rng(seed)
    T, ev = 60.0, (17.0, 41.0)
    trains = []
    for _ in range(4):
        bg = rng.uniform(0, T, rng.poisson(0.05 * T))
        on = np.array([e + rng.normal(0, 0.2) for e in ev])
        trains.append(np.sort(np.concatenate([bg, on])))
    return T, ev, trains


def _count_in(trains, lo, hi):
    return int(sum(np.sum((t >= lo) & (t < hi)) for t in trains))


def _tiles(ax, m, outline=(), row_ref=None):
    """A membership matrix as gridded tiles: rows cells, columns events, filled = joined. Row
    sums to the right, column sums below; a row sum that differs from row_ref is in color."""
    nr, nc = m.shape
    for i in range(nr):
        for j in range(nc):
            ax.add_patch(Rectangle((j, i), 1, 1, facecolor=INK if m[i, j] else "white",
                                   edgecolor="#999999", lw=1))
    for (i, j) in outline:
        ax.add_patch(Rectangle((j + 0.06, i + 0.06), 0.88, 0.88, fill=False,
                               edgecolor=SWAP_COL, lw=2.6, zorder=3))
    for i, rs in enumerate(m.sum(1)):
        changed = row_ref is not None and rs != row_ref[i]
        ax.text(nc + 0.3, i + 0.5, f"{rs}", va="center", ha="left", fontsize=11,
                color=SWAP_COL if changed else INK, fontweight="bold" if changed else None)
    for j, cs in enumerate(m.sum(0)):
        ax.text(j + 0.5, nr + 0.3, f"{cs}", va="top", ha="center", fontsize=11, color=INK)
    ax.set_xlim(-0.1, nc + 1.1); ax.set_ylim(nr + 1.1, -0.1)
    ax.set_aspect("equal")
    ax.set_xticks([j + 0.5 for j in range(nc)])
    ax.set_xticklabels([f"e{j + 1}" for j in range(nc)], fontsize=10)
    ax.xaxis.tick_top()
    ax.set_yticks([i + 0.5 for i in range(nr)])
    ax.set_yticklabels([f"cell {i + 1}" for i in range(nr)], fontsize=10)
    ax.tick_params(length=0)
    for sp in ax.spines.values():
        sp.set_visible(False)


def fig_schematic(out):
    """Three mechanisms the chapter explains in words, drawn on toy values: the coordination-rates
    tool's time-shift surrogate (A), the assembly test's two nulls (B), and the score sort and F
    (C), whose numbers come from order_limit.py's own functions."""
    import order_limit                                    # beside theory.py
    fig = plt.figure(figsize=(11, 13.2))
    outer = fig.add_gridspec(3, 1, height_ratios=[1.35, 1.0, 1.0], hspace=0.42, left=0.1,
                             right=0.9, top=0.97, bottom=0.03)

    # A: original and time-shifted trains, each raster with its lane above
    T, ev, trains = _toy_trains()
    w = 2.0
    wlo, whi = ev[0] - w / 2, ev[0] + w / 2
    # the tool's own surrogate (tools/measure_coordination_rates.shifted): each cell moved
    # circularly by a DISTINCT offset, a random permutation of multiples of SURR_SPACING windows,
    # centred; on the 0.1 s frame grid the tool works in
    import copy
    import measure_coordination_rates as mcr_tool
    dt = 0.1
    L, wf = int(round(T / dt)), int(round(w / dt))
    spacing = mcr_tool.SURR_SPACING * wf
    rng = np.random.RandomState(5)
    frames = [np.floor(t / dt + 0.5).astype(int) % L for t in trains]
    probe = mcr_tool.shifted([np.zeros(1, int)] * 4, L, spacing, copy.deepcopy(rng))
    shifts = np.array([((int(p[0]) + L // 2) % L - L // 2) * dt for p in probe])
    shifted = [np.sort(f * dt) for f in mcr_tool.shifted(frames, L, spacing, rng)]
    ga = outer[0].subgridspec(4, 1, height_ratios=[0.35, 1, 0.35, 1], hspace=0.12)
    lane1 = fig.add_subplot(ga[0]); ras1 = fig.add_subplot(ga[1], sharex=lane1)
    lane2 = fig.add_subplot(ga[2], sharex=lane1); ras2 = fig.add_subplot(ga[3], sharex=lane1)
    for lane, src, show_ev in ((lane1, trains, True), (lane2, shifted, False)):
        if show_ev:
            for e in ev:
                lane.plot(e, 0.3, marker="v", ms=10, color=EV2, ls="none")
        n_w = _count_in(src, wlo, whi)
        lane.annotate("", xy=(wlo, 0.78), xytext=(whi, 0.78),
                      arrowprops=dict(arrowstyle="|-|", color=SWAP_COL, lw=1.4,
                                      mutation_scale=4))
        lane.text(whi + 0.6, 0.78, f"window w = {w:g} s: {n_w} onset{'s' if n_w != 1 else ''}",
                  va="center", fontsize=10.5, color=SWAP_COL)
        lane.set_ylim(0, 1.1); lane.axis("off")
    lane1.text(-0.01, 0.3, "planted\nevents", transform=lane1.get_yaxis_transform(),
               ha="right", va="center", fontsize=10)
    for ras, src, lab in ((ras1, trains, "recording"), (ras2, shifted, "surrogate")):
        raster = ras
        for r, t in enumerate(src):
            raster.plot(t, np.full(t.size, r + 1), color="black", marker="|", ls="none",
                        ms=13, mew=1.8)
        raster.set_ylim(0.4, 4.6); raster.invert_yaxis()
        raster.set_yticks([1, 2, 3, 4])
        raster.set_yticklabels([f"cell {i}" for i in range(1, 5)], fontsize=10)
        raster.set_ylabel(lab, fontsize=11)
        for sp in ("top", "right"):
            raster.spines[sp].set_visible(False)
        raster.set_xlim(0, T)
    sec = ras2.secondary_yaxis("right")
    sec.set_yticks([1, 2, 3, 4])
    sec.set_yticklabels([f"shift {s:+.1f} s".replace("-", "−") for s in shifts], fontsize=10)
    sec.tick_params(length=0); sec.spines["right"].set_visible(False)
    ras1.tick_params(labelbottom=False)
    minutes_axis(ras2, 0, T)
    ras2.set_xlabel(f"time (toy recording, 60 s); surrogate: each cell's train shifted "
                    f"circularly by a distinct multiple of {mcr_tool.SURR_SPACING} windows "
                    f"({spacing * dt:g} s), centered", fontsize=10.5)
    letter(lane1, "A", x=-0.06, y=0.85)

    # B: membership matrix, a margin-preserving swap, and a uniform-null draw
    obs = np.array([[1, 1, 1, 0], [1, 1, 1, 0], [1, 1, 0, 0],
                    [0, 0, 1, 1], [0, 0, 0, 1], [0, 1, 0, 1]])
    swap = obs.copy()
    sw = [(2, 1), (2, 2), (3, 1), (3, 2)]                 # a checkerboard 2 x 2: 10/01 -> 01/10
    for (i, j) in sw:
        swap[i, j] = 1 - swap[i, j]
    assert (swap.sum(0) == obs.sum(0)).all() and (swap.sum(1) == obs.sum(1)).all()
    rng = np.random.default_rng(5)
    uni = np.zeros_like(obs)
    for j, cs in enumerate(obs.sum(0)):
        uni[rng.choice(obs.shape[0], cs, replace=False), j] = 1
    gb = outer[1].subgridspec(1, 3, wspace=0.35)
    labels = ("recording: who joined\neach event",
              "margin-preserving null: one swap;\nrow and column sums kept",
              "uniform null: random participants;\ncolumn sums kept only")
    axb = []
    for g, m, out_, lab in zip(gb, (obs, swap, uni), ((), sw, ()), labels):
        ax = fig.add_subplot(g)
        _tiles(ax, m, outline=out_, row_ref=obs.sum(1))
        ax.set_xlabel(lab, fontsize=10.5)
        axb.append(ax)
    letter(axb[0], "B", x=-0.25, y=1.08)
    fig.text(0.5, outer[1].get_position(fig).y0 - 0.052,
             "filled tile: the cell joined the event · right: the cell's event count (row sum) · "
             "below: the event's size (column sum)\norange: the swapped tiles, and row sums the "
             "uniform null changed", ha="center", va="top", fontsize=10, color="#333")

    # C: who leads whom, net lead counts, the score-sort order, and F
    events = [(np.array([0, 1, 2, 3]), np.array([0.0, 0.1, 0.2, 0.3])),
              (np.array([0, 1, 3]), np.array([0.1, 0.0, 0.3])),
              (np.array([1, 2, 3]), np.array([0.0, 0.2, 0.1]))]
    n, d = order_limit.pair_matrices(events, 4)
    order = order_limit.score_order(d)
    F = order_limit.f_of(order, n, d)
    pos = {c: i for i, c in enumerate(order)}
    agree = disagree = 0
    for cells, t in events:
        for a_ in range(len(cells)):
            for b_ in range(a_ + 1, len(cells)):
                i, j = cells[a_], cells[b_]
                lead_i = t[a_] < t[b_]
                if lead_i == (pos[i] < pos[j]):
                    agree += 1
                else:
                    disagree += 1
    co = int(n[np.triu_indices(4, 1)].sum())
    assert agree + disagree == co and abs((agree - disagree) / co - F) < 1e-12
    axc = fig.add_subplot(outer[2]); axc.axis("off")
    letter(axc, "C", x=-0.06, y=0.97)
    x_col = [0.0, 0.12, 0.25, 0.38, 0.51]
    head = ["pair", "event 1", "event 2", "event 3", "net"]
    y0, dy = 0.92, 0.095
    for x, h in zip(x_col, head):
        axc.text(x, y0, h, transform=axc.transAxes, fontsize=11, fontweight="bold", va="top")
    ev_txt = ["order 1, 2, 3, 4", "order 2, 1, 4", "order 2, 4, 3"]
    for x, t in zip(x_col[1:4], ev_txt):
        axc.text(x, y0 - 0.06, t, transform=axc.transAxes, fontsize=9, color="#555", va="top")
    r = 0
    for i in range(4):
        for j in range(i + 1, 4):
            y = y0 - 0.15 - dy * r
            axc.text(x_col[0], y, f"{i + 1}–{j + 1}", transform=axc.transAxes, fontsize=11,
                     va="top")
            for e_i, (cells, t) in enumerate(events):
                if i in cells and j in cells:
                    ti, tj = t[list(cells).index(i)], t[list(cells).index(j)]
                    s = f"{i + 1} leads" if ti < tj else f"{j + 1} leads"
                else:
                    s = "–"
                axc.text(x_col[1 + e_i], y, s, transform=axc.transAxes, fontsize=11, va="top")
            net = int(d[i, j])
            axc.text(x_col[4], y, f"{net:+d}".replace("-", "−") if net else "0", transform=axc.transAxes,
                     fontsize=11, va="top")
            r += 1
    axc.text(x_col[0], y0 - 0.15 - dy * r - 0.01,
             "net: the first cell's leads minus the second's, over the events they share",
             transform=axc.transAxes, fontsize=9.5, color="#555", va="top")
    xr = 0.6
    axc.text(xr, y0, "net lead count per cell (wins − losses)", transform=axc.transAxes,
             fontsize=11, fontweight="bold", va="top")
    for c in range(4):
        axc.text(xr, y0 - 0.1 - 0.08 * c, f"cell {c + 1}:  {int(d[c].sum()):+d}".replace("-", "−"),
                 transform=axc.transAxes, fontsize=11, va="top")
    yo = y0 - 0.1 - 0.08 * 4 - 0.04
    axc.text(xr, yo, "score-sort order:  " + " → ".join(str(c + 1) for c in order),
             transform=axc.transAxes, fontsize=11, fontweight="bold", va="top")
    axc.text(xr, yo - 0.1,
             f"pair co-participations: 6 + 3 + 3 = {co}\n"
             f"agree with the order: {agree}; disagree: {disagree}\n"
             f"F = ({agree} − {disagree}) ÷ {co} = {F:.2f}",
             transform=axc.transAxes, fontsize=11, va="top", linespacing=1.4)
    title = "Three mechanisms on toy values: surrogate, assembly nulls, score sort and F"
    return save(fig, name("surrogate-nulls-and-order-schematic", "recovery"), title, out)


# --------------------------------------------------------------------------- I. assessor jitter

ASSESSOR_JITTER = SV / "ch1_followups" / "assessor_jitter.json"
AJ_PANELS = ((0.01, 4), (0.05, 3), (0.05, 4), (0.05, 6))


def fig_assessor_jitter(out):
    """The assessor's jitter reading against planted jitter, measured and predicted as a mixture
    of chance and event clusters (ch1_followups/assessor_jitter.py and its record).

    Measured: the median over recordings of jit_obs, events of 10+ cells (20 recordings per
    planted jitter, pooled as Figure 1.1 D/H pools), with quartile bars. The chance-only level is
    the median jit_obs of the background-only recordings (the record's summary). The two curves
    are computed on a fine jitter grid with assessor_jitter.py's own functions: event-only is the
    median SD of its truncated-Gaussian event clusters (k = 10 and 20 pooled); the mixture pools
    the four conditions (k 10, 20; E 15, 45) with equal weight, each a mixture of the record's
    chance-cluster SDs (weight c / (c + e)) and model event clusters, as the script pools it. The
    record's own pooled mixture at the four planted values is checked against the curve."""
    sys.path.insert(0, str(SV / "ch1_followups"))
    import assessor_jitter as aj
    rec = json.loads(ASSESSOR_JITTER.read_text())
    a1 = aj.a1
    rng = np.random.default_rng(20261029)
    grid = np.geomspace(0.03, 1.5, 15)
    E_per_min = {E: E / (a1.DURATION / 60) for E in a1.N_EVENTS}
    fig, axes = plt.subplots(2, 2, figsize=(10.5, 10.2), sharex=True, sharey=True,
                             gridspec_kw=dict(hspace=0.28, wspace=0.08, left=0.1, right=0.985,
                                              top=0.95, bottom=0.22))
    for ax, (bg, K), let in zip(axes.ravel(), AJ_PANELS, "ABCD"):
        chance_sd = np.array([v for x in rec["bg"] if x["bg"] == bg for v in x["res"][str(K)]["sd"]])
        c = theory.chance_clusters_per_min(a1.N_ROI, bg, K)
        shares = {E: c / (c + e) for E, e in E_per_min.items()}
        ev_only, mix = [], []
        for sig in grid:
            msd = {k: aj.event_sd_model(k, sig, bg, K, rng, n=3000) for k in (10, 20)}
            ev_only.append(float(np.median(np.concatenate(list(msd.values())))))
            pooled = []
            for k in (10, 20):
                for E in a1.N_EVENTS:
                    nc = rng.binomial(10000, shares[E])
                    pooled.append(np.concatenate([rng.choice(chance_sd, nc) if nc else np.zeros(0),
                                                  rng.choice(msd[k], 10000 - nc)]))
            mix.append(float(np.median(np.concatenate(pooled))))
        ax.plot(grid, grid, color="#888", ls=":", lw=1, zorder=0)
        chance_lvl = next(b["jit_obs_median"] for b in rec["summary"]["background"]
                          if b["bg"] == bg and b["K"] == K)
        ax.axhline(chance_lvl, color=INK, ls="--", lw=1.3, zorder=1)
        ax.plot(grid, ev_only, color="#2a78d6", ls=(0, (1.2, 1.6)), lw=2.2, zorder=2)
        ax.plot(grid, mix, color="#7b3fb5", lw=2.2, zorder=3)
        for sig in sorted({e["jit"] for e in rec["ev"]}):
            jo = np.array([e["res"][str(K)]["jit_obs"] for e in rec["ev"]
                           if e["bg"] == bg and e["jit"] == sig and e["k"] >= 10])
            jo = jo[np.isfinite(jo)]
            q1, med, q3 = np.percentile(jo, [25, 50, 75])
            ax.errorbar(sig, med, yerr=[[med - q1], [q3 - med]], fmt="o", color="#eb6834",
                        ms=8, mec="white", mew=0.8, elinewidth=1.4, capsize=0, zorder=4)
            stored = next(p["mixture"] for p in rec["summary"]["pooled"]
                          if p["bg"] == bg and p["K"] == K and p["sigma"] == sig)
            assert abs(np.interp(np.log(sig), np.log(grid), mix) - stored) < 0.05, (bg, K, sig)
        lo_s, hi_s = min(shares.values()), max(shares.values())
        ax.text(0.97, 0.03, f"background {bg:g} Hz per cell, K = {K} cells\n"
                f"chance share c/(c + e): {lo_s:.2f}–{hi_s:.2f}\n(45 and 15 events)",
                transform=ax.transAxes, ha="right", va="bottom", fontsize=10.5,
                bbox=dict(facecolor="white", edgecolor="none", pad=1, alpha=0.85))
        ax.set_xscale("log"); ax.set_yscale("log")
        ax.set_xlim(0.03, 1.5); ax.set_ylim(0.03, 1.5)
        ticks = [0.05, 0.1, 0.2, 0.5, 1]
        ax.set_xticks(ticks); ax.set_xticklabels([f"{t:g}" for t in ticks])
        ax.set_yticks(ticks); ax.set_yticklabels([f"{t:g}" for t in ticks])
        ax.minorticks_off()
        style(ax); letter(ax, let)
    for ax in axes[1]:
        ax.set_xlabel("planted jitter SD σ (s)")
    for ax in axes[:, 0]:
        ax.set_ylabel("assessor's jitter reading (s)")
    handles = [Line2D([], [], color="#eb6834", marker="o", ls="none", ms=8,
                      label="measured: median over 20 recordings, events of 10 or 20 cells "
                            "(bars: quartiles)"),
               Line2D([], [], color="#7b3fb5", lw=2.2,
                      label="mixture prediction: chance and event clusters, weighted c/(c + e)"),
               Line2D([], [], color=INK, ls="--", lw=1.3,
                      label="chance clusters only (background-only recordings)"),
               Line2D([], [], color="#2a78d6", ls=(0, (1.2, 1.6)), lw=2.2,
                      label="event clusters only (Gaussian truncated at ±1.5 s, plus caught "
                            "background)"),
               Line2D([], [], color="#888", ls=":", lw=1, label="reading = planted")]
    fig.legend(handles=handles, loc="lower left", bbox_to_anchor=(0.09, 0.0), ncol=1,
               frameon=False, fontsize=10.5)
    title = "The assessor's jitter reading as a mixture of chance and event clusters"
    return save(fig, name("assessor-jitter-reading-as-mixture", "recovery"), title, out)


# --------------------------------------------------------------------------- J. real intervals

REAL_INTERVALS = SV / "separation" / "real_intervals" / "intervals_results.json"
W_COL = {1.0: "#1b9e77", 2.0: "#d95f02", 4.0: "#7570b3"}
S_MARK = {"fast": "o", "slow": "s"}


def _interval_rows():
    """Two records of the coordination-rates tool on event trains built from the measured interval
    lists: (label, rows), each row with stream, k, w, measured (pooled solve()), its SE, and the
    hard-core and general predictions, all as ratios to planted."""
    real = json.loads(REAL_INTERVALS.read_text())["real"]
    a = [dict(stream=r["stream"], k=r["k"], w=r["w"], meas=r["pooled"], se=r["pooled_se"],
              hard=r["pred"]["page"], gen=r["pred"]["general"]) for r in real]
    rc = json.loads(REALISTIC_COUNTS.read_text())
    b = [dict(stream=s, k=r["k"], w=r["w"], meas=r["pooled"], se=r["pooled_se"],
              hard=r["predicted"]["page"], gen=r["predicted"]["general"])
         for s in ("fast", "slow") for r in rc[s]["windows"]]
    lab = json.loads(LAB_VALUES.read_text())
    ev_a = {s: lab[s]["events_per_recording_mean"] for s in ("fast", "slow")}
    ev_b = {s: float(np.mean(rc[s]["events_per_recording"])) for s in ("fast", "slow")}
    return [(f"one event per mean interval: {ev_a['fast']:.1f} (fast) and {ev_a['slow']:.1f} "
             "(slow) events per recording", a),
            (f"tabulated event counts: {ev_b['fast']:.1f} (fast) and {ev_b['slow']:.1f} (slow) "
             "events per recording", b)]


def fig_intervals(out):
    """Measured against predicted rate and participants on event trains drawn from the measured
    interval lists (separation/real_intervals/intervals.py; ch1_followups/realistic_counts.py).
    Each measurement is drawn twice, at its hard-core prediction (open) and its general-form
    prediction (filled), joined by a thin line; the vertical bar is +-1 bootstrap SE of the
    measurement. Adapted from intervals.py's panels D and E; its residual, term-by-term and
    joint-fit panels are not measured-against-predicted and are left out."""
    recs = _interval_rows()
    fig, axes = plt.subplots(2, 2, figsize=(10.5, 11.0),
                             gridspec_kw=dict(hspace=0.5, wspace=0.3, left=0.1, right=0.985,
                                              top=0.94, bottom=0.19))
    for i, (head, rows) in enumerate(recs):
        for j, (q, lab) in enumerate((("lam", "event rate"), ("k", "participants"))):
            ax = axes[i, j]
            for r in rows:
                col, mk = W_COL[r["w"]], S_MARK[r["stream"]]
                ms = 8 if r["k"] == 13 else 5.5
                ax.plot([r["hard"][q], r["gen"][q]], [r["meas"][q]] * 2, color=col, lw=0.8,
                        alpha=0.7, zorder=1)
                ax.errorbar(r["gen"][q], r["meas"][q], yerr=r["se"][q], fmt=mk, ms=ms, color=col,
                            mfc=col, mec=col, elinewidth=0.9, capsize=0, zorder=3)
                ax.plot(r["hard"][q], r["meas"][q], mk, ms=ms, mfc="white", mec=col, mew=1.3,
                        zorder=2)
            vals = [v for r in rows for v in (r["hard"][q], r["gen"][q], r["meas"][q] - r["se"][q],
                                               r["meas"][q] + r["se"][q])]
            lo, hi = min(vals), max(vals)
            pad = 0.07 * (hi - lo)
            ax.plot([lo - pad, hi + pad], [lo - pad, hi + pad], color="#666", lw=0.9, zorder=0)
            ax.set_xlim(lo - pad, hi + pad); ax.set_ylim(lo - pad, hi + pad)
            ax.set_aspect("equal", adjustable="box")
            slow = [r for r in rows if r["stream"] == "slow"]
            above = sum(r["meas"][q] > r["gen"][q] for r in slow)
            side = "above" if above * 2 > len(slow) else "below"
            n_side = above if side == "above" else len(slow) - above
            ax.set_xlabel(f"predicted {lab} ÷ planted\n(slow stream: {n_side} of {len(slow)} "
                          f"{side} the general form)")
            ax.set_ylabel(f"measured {lab} ÷ planted\n(pooled over 40 recordings, ±1 SE)")
            style(ax); letter(ax, "ABCD"[2 * i + j], x=-0.04, y=1.03)
        fig.text(0.5, axes[i, 0].get_position().y1 + 0.022, head, ha="center", va="bottom",
                 fontsize=11.5)
    handles = [Line2D([], [], color=c, marker="o", ls="none", ms=7, label=f"{w:g} s window")
               for w, c in W_COL.items()]
    handles += [Line2D([], [], color="#555", marker="o", ls="none", ms=7, mfc="white",
                       label="at its hard-core prediction (open)"),
                Line2D([], [], color="#555", marker="o", ls="none", ms=7,
                       label="at its general-form prediction (filled)"),
                Line2D([], [], color="#555", lw=0.8, label="joins one measurement's two "
                                                           "predictions"),
                Line2D([], [], color="#555", marker="o", ls="none", ms=7, mfc="#bbb",
                       label="fast stream (σ 0.105 s)"),
                Line2D([], [], color="#555", marker="s", ls="none", ms=7, mfc="#bbb",
                       label="slow stream (σ 0.131 s)"),
                Line2D([], [], color="#555", marker="o", ls="none", ms=8, mfc="#bbb",
                       label="large: 13 cells per event; small: 7"),
                Line2D([], [], color="#666", lw=0.9, label="measured = predicted")]
    fig.legend(handles=handles, loc="lower center", bbox_to_anchor=(0.5, 0.0), ncol=3,
               frameon=False, fontsize=10.5, columnspacing=1.3)
    title = "The coordination-rates tool on event trains built from measured intervals"
    return save(fig, name("coordination-rates-on-real-intervals", "recovery"), title, out)


# --------------------------------------------------------------------------- main

FIGS = ["data", "sharing", "chance", "order", "regime", "residuals", "jointfit", "schematic",
        "assessor", "intervals"]


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--out", type=Path, default=HERE, help="folder for the PNGs")
    ap.add_argument("--only", nargs="*", default=None,
                    choices=FIGS)
    a = ap.parse_args(argv)
    todo = a.only or FIGS
    if "data" in todo:
        fig_data(a.out)
    if "sharing" in todo:
        fig_sharing(a.out)
    if "chance" in todo:
        fig_chance(a.out)
    if "order" in todo:
        fig_order(a.out)
    if "regime" in todo:
        fig_regime(a.out)
    if "residuals" in todo:
        fig_residuals(a.out)
    if "jointfit" in todo:
        fig_jointfit(a.out)
    if "schematic" in todo:
        fig_schematic(a.out)
    if "assessor" in todo:
        fig_assessor_jitter(a.out)
    if "intervals" in todo:
        fig_intervals(a.out)


if __name__ == "__main__":
    main()
