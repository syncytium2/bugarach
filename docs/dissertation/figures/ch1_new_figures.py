"""New figures for Chapter 1 (Aim 0): the data, the tools and the theory, drawn.

The committee review of the chapter (docs/reviews/chapter-1-aim0_2026-10-29-roles/, roles 8
and 9) found no figure in its first ~3,100 words. These five fill that gap:

  data      what one simulated recording looks like, and what each tool sees of it
  sharing   window sharing g2, g3 (Gaussian and uniform jitter) and the participant bias k-hat/k
  chance    chance clusters per minute against the assessor's threshold K
  order     power to detect order against events per recording (exact-size 5 % test)
  regime    realistic parameter values (the bench levels) against the tested grid

Every computed curve comes from the repository's own code: theory.py (g2, g3, the
chance-cluster rate), bugarach.simulate.simulate_coordination (the raster), the tools' own
binning (bugarach.assess, bugarach.detectors.count), and the run records theory_check.json and
aim1_one_source.json beside theory.py, and ch1_followups/order_power.json. Nothing here is
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
K_COL = {5: "#86b6ef", 10: "#2a78d6", 20: "#0d366b"}
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

    fig = plt.figure(figsize=(10.5, 13.2))
    gs = fig.add_gridspec(8, 2, width_ratios=[3.0, 1.15],
                          height_ratios=[0.32, 3.4, 0.62, 0.62, 0.62, 0.95, 0.95, 1.05],
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
        ax.axvspan(lo, lo + w, color="#f1f1f1" if b % 2 else "white", lw=0, zorder=0)
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
    tc = json.loads((SV / "theory_check.json").read_text())
    aim = json.loads((SV / "aim1_one_source.json").read_text())
    n_rec = {bg: sum(1 for r in aim["chance_arm"] if r["bg_rate"] == bg) for bg in (0.01, 0.05)}
    minutes = aim["duration_sec"] / 60.0
    N = aim["n_roi"]
    Ks = np.arange(3, 11)
    budget = 1.0 / 60.0
    fig, ax = plt.subplots(figsize=(10, 5.8))
    fig.subplots_adjust(left=0.105, right=0.6, top=0.97, bottom=0.12)
    handles = []
    for bg, col in BG_COL.items():
        pred = np.array([theory.chance_clusters_per_min(N, bg, int(K)) for K in Ks])
        safe = int(Ks[np.argmax(pred < budget)])
        ax.plot(Ks, pred, color=col, lw=2, marker="o", mfc="white", mec=col, ms=7, mew=1.5,
                zorder=2)
        meas = " (realistic value), predicted only" if bg not in n_rec else ", predicted"
        handles.append(Line2D([], [], color=col, lw=2, marker="o", mfc="white", mec=col,
                              label=f"{bg:g} Hz per cell{meas};\n"
                                    f"  first K under one per hour: {safe} cells"
                                    f"\n  ({pred[safe - Ks[0]] * 60:.2f} per hour at that K)"))
    for i, (bg, col) in enumerate(((0.01, BG_COL[0.01]), (0.05, BG_COL[0.05]))):
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
        handles.append(Line2D([], [], color=col, marker="o", ls="none", ms=7,
                              label=f"{bg:g} Hz, measured: {n_rec[bg]} background-only\n"
                                    f"  recordings, {n_rec[bg] * minutes:,.0f} min; 95 % interval"))
    ax.axhline(budget, color=INK, ls="--", lw=1.2)
    ax.text(10.25, budget * 1.25, "one per hour", ha="right", va="bottom", fontsize=10.5)
    measured_K = sorted({c["K"] for c in tc["chance"]})
    for K in Ks:
        if K not in measured_K:
            ax.axvspan(K - 0.5, K + 0.5, color="#f3f3f3", zorder=0, lw=0)
    ax.set_yscale("log"); ax.set_ylim(1e-7, 30); ax.set_xlim(2.5, 10.5)
    ax.set_xticks(Ks)
    ax.set_xlabel("assessor's threshold K (cells in one 1 s bin, of 33)")
    ax.set_ylabel("chance clusters per minute\n(background only)")
    for sp in ("top", "right"):
        ax.spines[sp].set_visible(False)
    ax.grid(True, axis="y", color="#e5e5e5", lw=0.6)
    handles += [Line2D([], [], color=INK, ls="--", label="budget: one chance cluster per hour"),
                Patch(color="#f3f3f3", label=f"K not measured (only K = "
                                             f"{', '.join(str(k) for k in measured_K)} were)")]
    ax.legend(handles=handles, loc="upper left", bbox_to_anchor=(1.02, 1.0), frameon=False,
              fontsize=10.5, labelspacing=0.9)
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
    fig, axes = plt.subplots(1, 2, figsize=(10.5, 5.6), sharey=True,
                             gridspec_kw=dict(wspace=0.08, left=0.085, right=0.985,
                                              top=0.93, bottom=0.34))
    for ax, k in zip(axes, op["ks"]):
        rows = sorted((r for r in op["rows"] if r["k"] == k), key=lambda r: r["E"])
        for rr in op["rs"]:
            for M, ls in ((1, "-"), (2, "--")):
                key = f"r={rr:g},M={M}"
                p = [r["power_randomized"][key] for r in rows]
                ax.plot([r["E"] for r in rows], p, color=R_COL[rr], ls=ls, lw=2,
                        marker="o" if M == 1 else "s", ms=6,
                        mfc=R_COL[rr] if M == 1 else "white", mec=R_COL[rr], mew=1.5)
        ax.axhline(0.8, color=INK, ls="--", lw=1.2)
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
                       label="one latency template (M = 1)"),
                Line2D([], [], color="#555", lw=2, ls="--", marker="s", ms=6, mfc="white",
                       label="two templates (M = 2)"),
                Line2D([], [], color=INK, ls="--", lw=1.2, label="power 0.8"),
                Line2D([], [], color=INK, ls=":", lw=1.2, label="test size 0.05")]
    fig.legend(handles=handles, loc="lower left", bbox_to_anchor=(0.06, 0.0), ncol=3,
               frameon=False, fontsize=10.5, columnspacing=1.5)
    fig.text(0.985, 0.025,
             "r = δ/σ: a template's spread of latencies\nover the onset jitter (σ = "
             f"{op['sigma_sec']:g} s).\nTest: exact-size 5 %, randomized at the\n"
             "threshold, against 3,000 order-free\nrecordings of the same size.",
             ha="right", va="bottom", fontsize=10.5, color="#333")
    title = "Power to detect order against the number of events"
    return save(fig, name("order-power-against-event-count", "recovery"), title, out)


# --------------------------------------------------------------------------- E. regime map

LAB = (("fast bench level", 0.105, 7, "#eb6834"), ("slow bench level", 0.131, 13, "#8e44ad"))


def fig_regime(out):
    tc = json.loads((SV / "theory_check.json").read_text())
    jf = tc["joint_fit"]
    fig, ax = plt.subplots(figsize=(9.6, 5.8))
    fig.subplots_adjust(left=0.1, right=0.6, top=0.97, bottom=0.12)
    lo_ok, hi_ok = 0.8, 1.25
    for sig in sorted({r["sigma"] for r in jf}):
        for k in sorted({r["k"] for r in jf}):
            ratios = [r["sigma_q"][1] / r["sigma"] for r in jf
                      if r["sigma"] == sig and r["k"] == k]
            ok = all(lo_ok <= q <= hi_ok for q in ratios)
            ax.plot(sig, k, marker="o", ms=13, ls="none",
                    color="#2a78d6" if ok else "white", mec="#2a78d6" if ok else "#888",
                    mew=2, zorder=3)
            ax.text(sig * 1.1, k - 1.25, f"{min(ratios):.2f}–{max(ratios):.2f}", fontsize=10,
                    color="#444", ha="left", va="center")
    for lab, sig, k, col in LAB:
        ax.add_patch(Rectangle((sig / 1.1, k - 1), sig * 1.1 - sig / 1.1, 2, facecolor=col,
                               alpha=0.25, edgecolor=col, lw=2, zorder=2))
        ax.text(sig / 1.17, k, f"{lab}\nσ {sig:g} s\n~{k} cells", ha="right", va="center",
                fontsize=10.5, color=col)
    ax.set_xscale("log"); ax.set_xlim(0.03, 1.8); ax.set_ylim(2, 24.5)
    ax.set_xticks([0.05, 0.1, 0.2, 0.5, 1.0])
    ax.set_xticklabels(["0.05", "0.1", "0.2", "0.5", "1"])
    ax.set_yticks([5, 7, 10, 13, 20])
    ax.set_xlabel("planted jitter σ (s)")
    ax.set_ylabel("cells per event, k (of 33)")
    style(ax)
    handles = [Line2D([], [], color="#2a78d6", marker="o", ls="none", ms=11, mew=2,
                      label="resolved by the joint fit"),
               Line2D([], [], color="white", mec="#888", marker="o", ls="none", ms=11, mew=2,
                      label="not resolved"),
               Line2D([], [], ls="none", label="resolved: recovered ÷ planted\n"
                      f"jitter within {lo_ok}–{hi_ok} in all four\nconditions (15 and 45 events,\n"
                      "0.01 and 0.05 Hz), each the median\nof 5 recordings; the numbers\n"
                      "give the range of the four"),
               Patch(facecolor=LAB[0][3], alpha=0.35, edgecolor=LAB[0][3],
                     label="realistic parameter values,\nfast bench level: σ 0.105 s,\n"
                           "7 cells (0.20 of 33)"),
               Patch(facecolor=LAB[1][3], alpha=0.35, edgecolor=LAB[1][3],
                     label="realistic parameter values,\nslow bench level: σ 0.131 s,\n"
                           "13 cells (0.38 of 33)")]
    ax.legend(handles=handles, loc="upper left", bbox_to_anchor=(1.02, 1.0), frameon=False,
              fontsize=10.5, labelspacing=1.0, handletextpad=0.6)
    title = "Realistic parameter values against the tested grid"
    return save(fig, name("realistic-values-against-tested-grid", "recovery"), title, out)


# --------------------------------------------------------------------------- main

def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--out", type=Path, default=HERE, help="folder for the PNGs")
    ap.add_argument("--only", nargs="*", default=None,
                    choices=["data", "sharing", "chance", "order", "regime"])
    a = ap.parse_args(argv)
    todo = a.only or ["data", "sharing", "chance", "order", "regime"]
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


if __name__ == "__main__":
    main()
