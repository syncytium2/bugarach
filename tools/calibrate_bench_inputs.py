#!/usr/bin/env python3
"""Can count (sliding) measure the bench's jitter and participation, once calibrated?

    python tools/calibrate_bench_inputs.py --out <folder> [--workers 40] [--seeds 12]

Orchestrator's brief, 2026-09-28 (Tony approving): one function, count (sliding), should both
extract the simulation's inputs from real data and be the detector (ADR-0012, Proposed, #848).
Its raw readings disagree with the current measures: participation 0.31 / 0.62 / 0.63 against
0.20 / 0.38 / 0.25, and jitter calibrated through its calls 0.332 / 0.320 / 0.364 s against the
correlogram's 0.105 / 0.131 / 0.150 s. This tool settles what it can with planted truth.

**Vocabulary** (``docs/GLOSSARY.md``): *jitter*, the spread of onsets within one coordinated event;
*participation*, the share of ROIs in one coordinated event; *intervals*, the time between them.

**Step 1, jitter.** Recordings are planted at known ``jitter_sec`` over a grid, at single
participation levels spanning the bench's and #848's, on both backgrounds, at the realistic
spacing. Each is read two ways, each method exactly as it produced its real-data number:

* **the correlogram** (``tools/measure_jitter_correlogram.py``): the half-width at half height of
  the cross-ROI onset correlogram's shoulder-subtracted peak, pooled over a cell's recordings,
  converted through that tool's stored calibration curve for the current dataset
  (``docs/learned/runs/2026-09-23-jitter-correlogram*-senktide-ttx``);
* **through the calls** (#848, ``tools/extract_bench_inputs.py``): count (sliding) at its untuned
  defaults with the recording's own floor; the SD of the participating ROIs' first onsets within
  each call's span, median over calls, converted through #848's stored curve
  (``inputs-count_sliding/calibration.json``).

A method that recovers the planted value whatever the participation and background is one whose
real-data number can be believed.

**Step 2, participation through count (sliding).** Each call's peak distinct-ROI count, minus the
ROIs a 2 s window catches by chance (``n_roi × (1 − exp(−r × 2 s))``, ``r`` each recording's mean
per-ROI event rate), over the ROI count; median over calls. A round trip calibrates it: bench
recordings planted at known participation (the bench's three levels, their middle swept), read by
the identical code, give the map from measured to true, and the real reading is read off it. With
an interval from resampling mice, per stream, pooled and in group order.

**Step 3, participation without a threshold.** The correlogram's shoulder-subtracted peak area is
the number of excess cross-ROI onset pairs within 3 s. Divided by the number of events it is the
mean pairs per event, ``C(n, 2)``, which gives ``n``. The event count is count (sliding)'s calls,
the intervals' own source, which #848 found robust; nothing else uses a threshold. Calibrated the
same round-trip way.

Baseline windows only (FOUNDATIONS §9). The default dataset (``dataset.default()``). Writes into
``--out``: ``jitter.json``, ``participation.json``, ``real_units.json``, figures and ``run.json``.
"""
from __future__ import annotations

import argparse
import importlib
import json
import math
import multiprocessing as mp
import os
import sys
import warnings
from pathlib import Path

import numpy as np

REPO = Path(__file__).resolve().parents[1]
for _p in (REPO / "src", REPO / "tools"):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

STREAMS = ("fast", "slow", "combined")
BENCHES = {"fast": "bugarach.bench", "slow": "bugarach.bench_slow",
           "combined": "bugarach.bench_combined"}
REGIMES = ("baseline_quiet", "baseline_busy")
WINDOW = 2.0                    # count (sliding)'s extraction window (#848, ADR-0012)
JITTERS = (0.05, 0.08, 0.1, 0.15, 0.2, 0.3, 0.4, 0.5)
#: Single planted participation levels for step 1: the bench's middle and #848's raw reading.
JITTER_LEVELS = {"fast": (0.2, 0.31, 0.45), "slow": (0.38, 0.62, 0.8),
                 "combined": (0.25, 0.4, 0.63)}
#: Middle participation levels for the step 2 and 3 round trip.
MIDS = {"fast": (0.08, 0.12, 0.16, 0.2, 0.25, 0.31, 0.4, 0.5, 0.6),
        "slow": (0.15, 0.22, 0.3, 0.38, 0.46, 0.55, 0.62, 0.7, 0.8, 0.9),
        "combined": (0.1, 0.15, 0.2, 0.25, 0.32, 0.4, 0.5, 0.63, 0.75, 0.9)}
TEST_SEED0 = 7000
CAL_SEED0 = 7500
RUN_ONE = "docs/learned/runs/2026-09-28-one-function-bench/inputs-count_sliding/calibration.json"
CORR = {"fast": "docs/learned/runs/2026-09-23-jitter-correlogram-senktide-ttx/jitter_correlogram.json",
        "slow": "docs/learned/runs/2026-09-23-jitter-correlogram-senktide-ttx/jitter_correlogram.json",
        "combined": "docs/learned/runs/2026-09-23-jitter-correlogram-combined-senktide-ttx/"
                    "jitter_correlogram.json"}


# ------------------------------------------------------------------ one recording or window

def measure(trains, t_range, dt: float, floor: int) -> dict:
    """Everything the three steps read off one recording or window, by one code path."""
    import measure_jitter_correlogram as mjc
    from extract_bench_inputs import EXTRACTION, spread_of
    from bugarach.detectors.count import count_sliding_detect

    lo, hi = t_range
    d = count_sliding_detect(trains, t_range, min_rois=int(floor), **EXTRACTION)
    on, wd, pk = (np.asarray(d.onset_sec, float), np.asarray(d.width_sec, float),
                  np.asarray(d.nrois, float))
    keep = (on >= lo) & (on < hi)
    on, wd, pk = on[keep], wd[keep], pk[keep]
    spreads = [spread_of(trains, float(a), float(b)) for a, b in zip(on, wd)]
    # Each participating ROI's first onset in the call's span, minus the call's median of them:
    # the shape the spread statistic summarises, for the step 1 shape check.
    offsets = []
    for a, b in zip(on, wd):
        w = b if np.isfinite(b) and b > 0 else 0.0
        firsts = []
        for t in trains:
            t = np.asarray(t, float)
            m = (t >= a - 1e-9) & (t <= a + w + 1e-9)
            if m.any():
                firsts.append(float(t[m][0]))
        if len(firsts) >= 2:
            offsets += list(np.round(np.asarray(firsts) - np.median(firsts), 3))
    n_roi = len(trains)
    dur = hi - lo
    n_on = int(sum(np.sum((np.asarray(t) >= lo) & (np.asarray(t) < hi)) for t in trains))
    rate = n_on / (n_roi * dur) if n_roi and dur > 0 else 0.0
    L = int(round(dur / dt))
    frames = [np.round((np.asarray(t, float)[(np.asarray(t) >= lo) & (np.asarray(t) < hi)] - lo)
                       / dt).astype(int) for t in trains]
    o, e = mjc.pairs(frames, L)
    return dict(n_roi=n_roi, hours=dur / 3600.0, rate_hz=rate, floor=int(floor),
                n_calls=int(on.size), peaks=pk.tolist(),
                spreads=[s for s in spreads if s is not None], offsets=offsets,
                obs=o.tolist(), exp=e.tolist())


def _sim_job(args):
    stream, regime, seed, jitter, part, tag = args
    os.environ["BUGARACH_BENCH_SPACING"] = "realistic"
    from bugarach import bench as B
    from bugarach.detectors.rate import stream_trains

    mod = importlib.import_module(BENCHES[stream])
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        kw = dict(participation=tuple(part))
        if jitter is not None:
            kw["jitter_sec"] = jitter
        s, gt = mod.make_recording(regime, seed, **kw)
        ext = B.recording_extent(s)
        tr = stream_trains(s.streams[B.STREAM], ext)
        m = measure(tr, ext, s.require_dt(), gt.params["event_floor"])
    planted = [e for e in gt.events if getattr(e, "kind", "coordinated") == "coordinated"]
    return dict(stream=stream, regime=regime, seed=seed, tag=tag,
                jitter=gt.params["jitter_sec"], part=list(part),
                planted_events=len(planted),
                planted_share=float(np.mean([e.n_part / m["n_roi"] for e in planted]))
                if planted else None, **m)


def _real_job(args):
    folder, i = args
    from bugarach import event_floor as ef
    from bugarach.combined import COMBINED, has_sources, stream_of
    from bugarach.detect_folder import _region_index, folder_analysis_windows
    from bugarach.detectors.rate import stream_trains
    from bugarach.io import load_folder
    from extract_bench_inputs import DRAWS, TAG

    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        s = load_folder(Path(folder))[i]
        meta = getattr(s, "meta", {}) or {}
        s, windows = folder_analysis_windows(s)
    if has_sources(s) and COMBINED not in s.streams:
        s.streams[COMBINED] = stream_of(s, COMBINED)
    dt = s.require_dt()
    out = []
    for w in windows:
        if not (w.label or "").strip().lower().startswith("baseline"):
            continue
        lo, hi = float(w.win_start), float(w.win_end)
        idx = _region_index(w)
        for sname in STREAMS:
            if sname not in s.streams:
                continue
            tr = stream_trains(s.streams[sname], (lo, hi))
            frames = [np.unique(np.floor((np.asarray(t, float) - lo) / dt + 1e-9).astype(np.int64))
                      for t in tr]
            try:
                f = ef.window_floor(frames, int(round((hi - lo) / dt)), dt,
                                    key=(TAG, s.slice_id, sname, idx), draws=DRAWS)
            except ValueError:
                continue
            m = measure(tr, (lo, hi), dt, f.floor)
            out.append(dict(slice_id=s.slice_id, region_idx=idx, stream=sname,
                            group=str(meta.get("group_id") or "").strip() or None,
                            mouse=str(meta.get("subject_id") or s.slice_id), **m))
    return out


# ------------------------------------------------------------------ the statistics

def pooled_hwhm(units) -> float:
    import measure_jitter_correlogram as mjc
    o = np.sum([u["obs"] for u in units], axis=0)
    e = np.sum([u["exp"] for u in units], axis=0)
    return float(mjc.hwhm(o, e))


def spread_median(units) -> float:
    v = [x for u in units for x in u["spreads"]]
    return float(np.median(v)) if v else float("nan")


def chance_rois(u) -> float:
    """ROIs a 2 s window catches by chance at this unit's mean per-ROI rate."""
    return u["n_roi"] * (1.0 - math.exp(-u["rate_hz"] * WINDOW))


def sliding_share(units, subtract=True) -> float:
    """Median over calls of (peak − chance ROIs) / ROI count; the raw reading with subtract off."""
    v = [(p - (chance_rois(u) if subtract else 0.0)) / u["n_roi"]
         for u in units for p in u["peaks"] if u["n_roi"]]
    return float(np.median(v)) if v else float("nan")


def excess_pairs(u) -> float:
    """Shoulder-subtracted excess cross-ROI onset pairs at lags 0-3 s."""
    import measure_jitter_correlogram as mjc
    o, e = np.asarray(u["obs"]), np.asarray(u["exp"])
    with np.errstate(invalid="ignore", divide="ignore"):
        b = np.nanmean(o[mjc.SHOULDER[0]:mjc.SHOULDER[1] + 1]
                       / e[mjc.SHOULDER[0]:mjc.SHOULDER[1] + 1]) - 1.0
    b = 0.0 if not np.isfinite(b) else b
    k = slice(mjc.PEAK[0], mjc.PEAK[1] + 1)
    return float(np.sum(o[k] - e[k] * (1.0 + b)))


def corr_share(units) -> float:
    """Threshold-free participation: pooled excess pairs per call → n with C(n, 2) pairs → share.
    Pooled over units (sums), so a unit with few calls does not dominate."""
    A = sum(excess_pairs(u) for u in units)
    n_ev = sum(u["n_calls"] for u in units)
    N = np.average([u["n_roi"] for u in units], weights=[max(u["n_calls"], 1) for u in units])
    if n_ev <= 0 or A <= 0:
        return float("nan")
    S = A / n_ev
    n = 0.5 * (1.0 + math.sqrt(1.0 + 8.0 * S))
    return float(n / N)


def invert(x_true, y_meas, y):
    """Read ``y`` off a measured-vs-true curve, made non-decreasing first; NaN outside it."""
    xs, ys = np.asarray(x_true, float), np.asarray(y_meas, float)
    ok = np.isfinite(ys)
    xs, ys = xs[ok], np.maximum.accumulate(ys[ok])
    keep = np.concatenate([[True], np.diff(ys) > 0])
    if keep.sum() < 2 or not np.isfinite(y):
        return float("nan")
    return float(np.interp(y, ys[keep], xs[keep], left=np.nan, right=np.nan))


def curves():
    """Each method's stored calibration curve, as it produced its real-data number."""
    one = json.loads((REPO / RUN_ONE).read_text(encoding="utf-8"))
    out = {}
    for s in STREAMS:
        c = json.loads((REPO / CORR[s]).read_text(encoding="utf-8"))["streams"][s]["hwhm"]
        cal = c["calibration_sec"]
        cal = json.loads(cal.replace("'", '"')) if isinstance(cal, str) else cal
        cj = sorted((float(k), float(v)) for k, v in cal.items())
        out[s] = dict(
            correlogram=dict(jitter=[a for a, _ in cj], stat=[b for _, b in cj],
                             real_stat=c["real_sec"], real_jitter=c["jitter_sec"]),
            calls=dict(jitter=[p["jitter_sec"] for p in one[s]["curve"]],
                       stat=[p["spread_median_sec"] for p in one[s]["curve"]],
                       real_stat=one[s]["real_spread_median_sec"],
                       real_jitter=one[s]["jitter_sec"]))
    return out


def boot_units(units, fn, n=400, key="seed", seed=20260928):
    """Percentile interval of ``fn`` over resamples of ``key`` groups (seeds, or mice), and the
    share of resamples whose reading fell off the calibration curve. With more than half off it,
    no interval is given: the few that land on the curve are not a sample of the reading."""
    rs = np.random.default_rng(seed)
    ids = sorted({u[key] for u in units}, key=str)
    by = {i: [u for u in units if u[key] == i] for i in ids}
    vals = []
    for _ in range(n):
        pick = rs.choice(len(ids), size=len(ids), replace=True)
        vals.append(fn([u for j in pick for u in by[ids[j]]]))
    v = np.asarray(vals, float)
    off = float(np.mean(~np.isfinite(v)))
    v = v[np.isfinite(v)]
    lohi = ([float(np.percentile(v, 2.5)), float(np.percentile(v, 97.5))]
            if v.size and off <= 0.5 else [None, None])
    return dict(lo=lohi[0], hi=lohi[1], off_curve_share=off)


# ------------------------------------------------------------------ figures

def fig_jitter(rows, path):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, axes = plt.subplots(1, 3, figsize=(13, 4.3))
    col = {"correlogram": "#1f77b4", "calls": "#d62728"}
    mk = {0: "o", 1: "s", 2: "^"}
    for ax, s in zip(axes, STREAMS):
        R = [r for r in rows if r["stream"] == s]
        lv = sorted({r["part"] for r in R})
        for meth in ("correlogram", "calls"):
            for i, p in enumerate(lv):
                for reg, fill in (("baseline_quiet", True), ("baseline_busy", False)):
                    pts = sorted((r["jitter"], r[meth]) for r in R
                                 if r["part"] == p and r["regime"] == reg)
                    x = [a for a, b in pts]
                    y = [b if np.isfinite(b) else np.nan for a, b in pts]
                    ax.plot(x, y, marker=mk[i], ms=5, lw=0.8, color=col[meth],
                            mfc=col[meth] if fill else "white", alpha=0.85)
        ax.plot([0, 0.55], [0, 0.55], color="#888", lw=1, ls="--")
        ax.set_xlim(0, 0.55)
        ax.set_ylim(0, 0.8)
        ax.set_xlabel(f"{s} · planted jitter (s)")
        ax.set_ylabel("recovered jitter (s)")
        ax.text(0.02, 0.77, "blue: correlogram · red: through the calls\n"
                + " · ".join(f"{m} participation {p:g}" for m, p in
                             zip(("circle", "square", "triangle"), lv))
                + "\nfilled: quiet background · open: busy", fontsize=7, va="top")
    fig.suptitle("Figure 1. Planted jitter against jitter recovered by each method; dashed: "
                 "identity. Each point pools 12 recordings.", fontsize=10, x=0.01, ha="left")
    fig.tight_layout()
    fig.savefig(path, dpi=150)


def fig_participation(cal, path):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, axes = plt.subplots(1, 3, figsize=(13, 4.3))
    for ax, s in zip(axes, STREAMS):
        c = cal[s]
        x = c["planted_share"]
        for key, color, lab in (("raw", "#aaaaaa", "sliding, raw (#848)"),
                                ("sliding", "#d62728", "sliding, chance subtracted"),
                                ("correlogram", "#1f77b4", "correlogram, no threshold")):
            ax.plot(x, c[key], marker="o", ms=4, color=color, label=lab)
            if key in c.get("real", {}):
                ax.axhline(c["real"][key], color=color, lw=0.8, ls=":")
        ax.plot([0, 1], [0, 1], color="#888", lw=1, ls="--")
        ax.set_xlim(0, max(x) * 1.1)
        ax.set_ylim(0, 1)
        ax.set_xlabel(f"{s} · planted participation (share of ROIs, calls' mean)")
        ax.set_ylabel("measured participation (share of ROIs)")
        ax.legend(fontsize=7, frameon=False, loc="upper left")
    fig.suptitle("Figure 2. The round trip: planted participation against each measure; dotted: "
                 "each measure's real-data reading; dashed: identity.", fontsize=10, x=0.01,
                 ha="left")
    fig.tight_layout()
    fig.savefig(path, dpi=150)


def peak_shape(units) -> list:
    """Pooled shoulder-subtracted excess at lags 0-3 s, over its zero-lag value."""
    import measure_jitter_correlogram as mjc
    o = np.sum([u["obs"] for u in units], axis=0)
    e = np.sum([u["exp"] for u in units], axis=0)
    x = mjc.excess(o, e)
    p = x[mjc.PEAK[0]:mjc.PEAK[1] + 1] - np.nanmean(x[mjc.SHOULDER[0]:mjc.SHOULDER[1] + 1])
    return (p / p[0]).tolist() if np.isfinite(p[0]) and p[0] > 0 else []


def fig_peak(shape, path):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, axes = plt.subplots(1, 3, figsize=(13, 4.0))
    style = {"real": ("black", 2.0, "real recordings"),
             "correlogram": ("#1f77b4", 1.4, "planted at the correlogram's jitter"),
             "calls": ("#d62728", 1.4, "planted at #848's jitter")}
    for ax, s in zip(axes, STREAMS):
        for k, (c, lw, lab) in style.items():
            y = shape[s][k].get("peak_shape") or []
            if y:
                j = shape[s][k]["jitter_planted"]
                ax.plot(np.arange(len(y)) * 0.1, y, color=c, lw=lw,
                        label=lab + ("" if j is None else f" ({j:g} s)")
                        + f", half-width {shape[s][k]['hwhm_sec']:.3f} s")
        ax.axhline(0.5, color="#888", lw=0.8, ls=":")
        ax.axhline(0, color="#888", lw=0.6)
        ax.set_xlabel(f"{s} · lag between two ROIs' onsets (s)")
        ax.set_ylabel("excess pairs, share of zero lag")
        ax.legend(fontsize=7, frameon=False, loc="upper right")
    fig.suptitle("Figure 4. The correlogram's peak: real recordings against planted recordings at "
                 "the two candidate jitters; dotted: half height.", fontsize=10, x=0.01, ha="left")
    fig.tight_layout()
    fig.savefig(path, dpi=150)


def fig_shape(shape, path):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, axes = plt.subplots(1, 3, figsize=(13, 4.0))
    x = np.arange(-2.0, 2.05, 0.1)
    style = {"real": ("black", 2.0, "real calls"),
             "correlogram": ("#1f77b4", 1.4, "planted at the correlogram's jitter"),
             "calls": ("#d62728", 1.4, "planted at #848's jitter")}
    for ax, s in zip(axes, STREAMS):
        for k, (c, lw, lab) in style.items():
            h = np.asarray(shape[s][k]["hist"], float)
            if h.sum():
                j = shape[s][k]["jitter_planted"]
                ax.step(x, h / h.sum(), where="mid", color=c, lw=lw,
                        label=lab + ("" if j is None else f" ({j:g} s)")
                        + f", {shape[s][k]['n']:,} onsets")
        ax.set_yscale("log")
        ax.set_xlabel(f"{s} · onset minus the call's median onset (s)")
        ax.set_ylabel("share of participating onsets")
        ax.legend(fontsize=7, frameon=False, loc="lower center")
    fig.suptitle("Figure 3. Where participants' onsets fall around their call's centre: real calls "
                 "against planted recordings at the two candidate jitters (log scale).",
                 fontsize=10, x=0.01, ha="left")
    fig.tight_layout()
    fig.savefig(path, dpi=150)


# ------------------------------------------------------------------ main

def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--workers", type=int, default=max(1, (os.cpu_count() or 2) - 6))
    ap.add_argument("--seeds", type=int, default=12, help="recordings per cell and background")
    ap.add_argument("--steps", default="1,2", help="1 = jitter; 2 = participation (steps 2 and 3)")
    a = ap.parse_args(argv)
    a.out.mkdir(parents=True, exist_ok=True)
    steps = set(a.steps.split(","))
    CUR = curves()
    run = dict(argv=sys.argv, seeds=a.seeds, jitters=JITTERS, jitter_levels=JITTER_LEVELS,
               mids=MIDS, curves_from=dict(calls=RUN_ONE, correlogram=CORR))

    if "1" in steps:
        jobs = [(s, reg, TEST_SEED0 + k, j, (p, p, p), "jitter")
                for s in STREAMS for j in JITTERS for p in JITTER_LEVELS[s] for reg in REGIMES
                for k in range(a.seeds)]
        with mp.Pool(a.workers) as pool:
            got = pool.map(_sim_job, jobs, chunksize=2)
        rows = []
        for s in STREAMS:
            for j in JITTERS:
                for p in JITTER_LEVELS[s]:
                    for reg in REGIMES:
                        U = [g for g in got if g["stream"] == s and g["jitter"] == j
                             and g["part"][0] == p and g["regime"] == reg]
                        cc, ca = CUR[s]["correlogram"], CUR[s]["calls"]
                        h, sp = pooled_hwhm(U), spread_median(U)
                        rc = invert(cc["jitter"], cc["stat"], h)
                        rk = invert(ca["jitter"], ca["stat"], sp)
                        rows.append(dict(stream=s, jitter=j, part=p, regime=reg, n=len(U),
                                         hwhm=h, spread=sp, correlogram=rc, calls=rk,
                                         calls_below_curve=bool(np.isfinite(sp) and
                                                                sp < min(ca["stat"]))))
        summ = {}
        for s in STREAMS:
            summ[s] = {}
            for meth in ("correlogram", "calls"):
                R = [r for r in rows if r["stream"] == s]
                err = np.array([r[meth] - r["jitter"] for r in R if np.isfinite(r[meth])])
                rel = np.array([(r[meth] - r["jitter"]) / r["jitter"] for r in R
                                if np.isfinite(r[meth])])
                summ[s][meth] = dict(
                    cells=len(R), recovered=int(err.size),
                    bias_sec=float(np.mean(err)) if err.size else None,
                    abs_error_median_sec=float(np.median(np.abs(err))) if err.size else None,
                    rel_bias=float(np.mean(rel)) if rel.size else None,
                    spread_sec=float(np.std(err)) if err.size else None,
                    real_stat=CUR[s][meth]["real_stat"], real_jitter=CUR[s][meth]["real_jitter"])
        (a.out / "jitter.json").write_text(json.dumps(dict(summary=summ, cells=rows, curves=CUR),
                                                      indent=1), encoding="utf-8")
        fig_jitter(rows, a.out / "fig1_jitter_recovery.png")
        print(json.dumps(summ, indent=1))

    real = None
    if steps & {"2", "shape"}:
        from bugarach import dataset
        from bugarach.io import load_folder

        folder = dataset.default()
        run["dataset"] = dataset.stamp()
        n = len(load_folder(folder))
        with mp.Pool(a.workers) as pool:
            real = [u for part in pool.map(_real_job, [(str(folder), i) for i in range(n)])
                    for u in part]
        (a.out / "real_units.json").write_text(json.dumps(real), encoding="utf-8")

    if "shape" in steps:
        # Is the within-call onset spread one Gaussian? Real calls against planted recordings at
        # the two candidate jitters, the bench's own participation, both backgrounds.
        jobs = [(s, reg, TEST_SEED0 + 100 + k, round(CUR[s][m]["real_jitter"], 3),
                 importlib.import_module(BENCHES[s]).BENCH_RECORDING["participation"], m)
                for s in STREAMS for m in ("correlogram", "calls") for reg in REGIMES
                for k in range(a.seeds)]
        with mp.Pool(a.workers) as pool:
            sims = pool.map(_sim_job, jobs, chunksize=2)
        shape = {}
        for s in STREAMS:
            sets = {"real": [x for u in real if u["stream"] == s for x in u["offsets"]]}
            for m in ("correlogram", "calls"):
                sets[m] = [x for g in sims if g["stream"] == s and g["tag"] == m
                           for x in g["offsets"]]
            shape[s] = {}
            for k, v in sets.items():
                v = np.asarray(v, float)
                v = v[v != 0]          # the median participant itself carries no spread
                mad = float(np.median(np.abs(v))) * 1.4826 if v.size else None
                shape[s][k] = dict(
                    n=int(v.size), sd_sec=float(np.std(v)) if v.size else None,
                    mad_sd_sec=mad,
                    share_beyond_half_sec=float(np.mean(np.abs(v) > 0.5)) if v.size else None,
                    share_beyond_one_sec=float(np.mean(np.abs(v) > 1.0)) if v.size else None,
                    jitter_planted=None if k == "real" else round(CUR[s][k]["real_jitter"], 3),
                    hist=np.histogram(v, bins=np.arange(-2.05, 2.1, 0.1))[0].tolist())
        # The correlogram's own peak, the same comparison: shoulder-subtracted excess, 0-3 s, as a
        # share of its zero-lag height. One Gaussian jitter has one width; a narrow pairwise
        # component on top of a broad event spread would show as a spike on a wider base.
        for s in STREAMS:
            for k, U in (("real", [u for u in real if u["stream"] == s]),
                         ("correlogram", [g for g in sims if g["stream"] == s
                                          and g["tag"] == "correlogram"]),
                         ("calls", [g for g in sims if g["stream"] == s and g["tag"] == "calls"])):
                shape[s][k]["peak_shape"] = peak_shape(U)
                shape[s][k]["hwhm_sec"] = pooled_hwhm(U)
        (a.out / "shape.json").write_text(json.dumps(shape, indent=1), encoding="utf-8")
        fig_shape(shape, a.out / "fig3_within_call_shape.png")
        fig_peak(shape, a.out / "fig4_correlogram_peak_shape.png")
        print(json.dumps({s: {k: {q: v[q] for q in ("n", "sd_sec", "mad_sd_sec",
                                                     "share_beyond_half_sec")}
                              for k, v in d.items()} for s, d in shape.items()}, indent=1))

    if "2" in steps:
        from bugarach.groups import in_group_order

        jobs = []
        for s in STREAMS:
            cur = importlib.import_module(BENCHES[s]).BENCH_RECORDING["participation"]
            mid0 = cur[len(cur) // 2]
            for m in MIDS[s]:
                lv = tuple(round(min(0.95, m * x / mid0), 4) for x in cur)
                for reg in REGIMES:
                    for k in range(a.seeds):
                        jobs.append((s, reg, CAL_SEED0 + k, None, lv, f"mid={m}"))
        with mp.Pool(a.workers) as pool:
            sims = pool.map(_sim_job, jobs, chunksize=2)
        groups = in_group_order({u["group"] for u in real if u["group"]})
        cal = {}
        for s in STREAMS:
            X, raw, sl, co = [], [], [], []
            for m in MIDS[s]:
                U = [g for g in sims if g["stream"] == s and g["tag"] == f"mid={m}"]
                # "True" is the planted share of the events the calls can see: the mean over
                # planted events of n_part / n_roi, pooled over the cell's recordings.
                X.append(float(np.mean([g["planted_share"] for g in U if g["planted_share"]])))
                raw.append(sliding_share(U, subtract=False))
                sl.append(sliding_share(U))
                co.append(corr_share(U))
            R = [u for u in real if u["stream"] == s]

            def readings(units):
                return dict(raw=sliding_share(units, subtract=False), sliding=sliding_share(units),
                            correlogram=corr_share(units))

            def calibrated(units, X=X, sl=sl, co=co):
                r = readings(units)
                return dict(sliding=invert(X, sl, r["sliding"]),
                            correlogram=invert(X, co, r["correlogram"]))

            def ci(units, which):
                return boot_units(units, lambda us: calibrated(us)[which], key="mouse")

            entry = dict(planted_share=X, raw=raw, sliding=sl, correlogram=co,
                         real=readings(R), calibrated=calibrated(R),
                         interval=dict(sliding=ci(R, "sliding"),
                                       correlogram=ci(R, "correlogram")),
                         by_group={})
            for grp in groups:
                G = [u for u in R if u["group"] == grp]
                entry["by_group"][grp] = dict(
                    recordings=len({u["slice_id"] for u in G}), mice=len({u["mouse"] for u in G}),
                    real=readings(G), calibrated=calibrated(G),
                    interval=dict(sliding=ci(G, "sliding"), correlogram=ci(G, "correlogram")))
            cal[s] = entry
        (a.out / "participation.json").write_text(json.dumps(cal, indent=1), encoding="utf-8")
        fig_participation(cal, a.out / "fig2_participation_round_trip.png")
        print(json.dumps({s: dict(real=c["real"], calibrated=c["calibrated"],
                                  interval=c["interval"]) for s, c in cal.items()}, indent=1))
    (a.out / "run.json").write_text(json.dumps(run, indent=1, default=str), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
