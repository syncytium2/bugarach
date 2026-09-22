#!/usr/bin/env python3
"""Onset jitter without bins: the width of the cross-ROI correlogram's peak, calibrated on the simulator.

    python tools/measure_jitter_correlogram.py --jobs 12 --out docs/learned/runs/<dated-name>

**Why.** Both benches' ``jitter_sec`` came from a bin-bound instrument. ``assess_coactivity``'s
within-cluster onset spread tracks bin/√12 from 0.5 s to 5 s on both streams
(``tools/measure_slow_bench.py``, ``BINS``), and the MATLAB summary the fast bench's 0.36 s came
from (``bench.MEASURED_PROVENANCE``) is the same measure. Tony, 2026-09-22: *"we don't have our
own measure of jitter?"* — this is one.

**The statistic.** Onset pairs between distinct ROIs at each lag of one frame (0.1 s) out to
10 s, divided by the count expected if every pair fired independently at its observed totals —
``tools/measure_slow_comodulation.py``'s definition (Perkel, Gerstein & Moore 1967), not re-derived:
its ``raster`` and ``_autocorr_rows`` are imported, and zero lag is counted once per pair as there.
Numerator and denominator are pooled over recordings before dividing. If participants' onsets
scatter with SD σ around a shared time, the pairwise lag scatters with SD σ√2, so the excess
forms a peak at short lags whose width grows with σ.

**The width.** The mean excess at 5–10 s lag — the broad shoulder of slow shared modulation —
is subtracted, and the **half-width at half height** of what is left (:func:`hwhm`) is the
primary width. The RMS lag over 0–3 s (:func:`width`) is also recorded, and on real data it is
the wrong statistic: it weights the tail by lag squared, so noise there moves it.

**Why calibrate instead of dividing by √2.** Frames quantise onsets, distractors and the
elevated-rate stretch add their own pairs, participation sets the peak's height against the
background — so width is not exactly σ√2. The same measure is run on simulated recordings of
each bench (``bench`` for fast, ``bench_slow`` for slow; both backgrounds; seeds 1–24) at a
grid of planted ``jitter_sec``, and a real width is read off that curve. **The calibration is
the test**: a width that does not grow with planted jitter would refuse the method, and the
record says whether it grew.

**What it reads.** The default dataset (``dataset.default()``), each recording's baseline
analysis window (``assess_folder.generation_window``, 15-minute floor), ``t50rise`` onsets.
Baseline only (FOUNDATIONS §9).

**By group** (``--by-group``, added 2026-09-22 on Tony's question *"are the widths different
between the groups?"*). FOUNDATIONS §9: effects run in opposite directions by group, so a pooled
width is not admissible on its own. The split pools each group's recordings into its own
correlogram and reads a width off the **same** simulator calibration, which is group-independent —
the benches know nothing about group, so the curve is computed once per stream and shared.

Three things the split needs that the pooled measure does not:

* **The resampling unit is the mouse, not the recording.** 84 recordings come from 44 mice, so
  recordings within a mouse are not independent draws; each group's interval comes from resampling
  its own mice with replacement (``group_boot``). The pooled block above keeps its recording-level
  bootstrap unchanged, so the 2026-09-22 numbers still reproduce.
* **The answer is a test, not four intervals.** Whether the widths differ at all is a permutation
  test: mouse→group labels are shuffled with the group sizes held fixed, and the spread
  (widest group minus narrowest) is recomputed. Group sizes differ — 25, 22, 20 and 17 recordings —
  and a smaller group's width is the noisier estimate, which permuting labels at fixed sizes
  accounts for and four separate intervals do not.
* **A width is not yet a jitter, per group.** The calibration converts width to σ at the *bench's*
  participation and rate. Groups differ in both, so the primary per-group comparison is the measured
  half-width; the converted σ is recorded beside it and carries that caveat.
"""
from __future__ import annotations

import argparse
import json
import sys
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np

REPO = Path(__file__).resolve().parents[1]
for _p in (REPO / "src", REPO / "tools"):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

DT = 0.1
MAX_LAG = 100            # frames: 10 s
PEAK = (0, 30)           # frames: 0-3 s
SHOULDER = (50, 100)     # frames: 5-10 s
JITTERS = (0.05, 0.1, 0.15, 0.2, 0.3, 0.36, 0.46, 0.6, 0.8, 1.0)
SIM_SEEDS = tuple(range(1, 25))
BENCHES = {"fast": "bugarach.bench", "slow": "bugarach.bench_slow"}


def pairs(trains, L: int, max_lag: int = MAX_LAG):
    """(observed, expected) cross-ROI onset pairs at each frame lag 0..max_lag, zero lag once."""
    import measure_slow_comodulation as msc

    max_lag = min(max_lag, L - 1)
    X = msc.raster(trains, L)
    n = X.sum(axis=1)
    obs = msc._autocorr_rows(X.sum(axis=0, keepdims=True), max_lag) - msc._autocorr_rows(X, max_lag)
    k = np.arange(max_lag + 1)
    exp = (n.sum() ** 2 - (n ** 2).sum()) * (L - k) / L ** 2
    obs[0] /= 2.0
    exp[0] /= 2.0
    out_o, out_e = np.zeros(MAX_LAG + 1), np.zeros(MAX_LAG + 1)
    out_o[:max_lag + 1], out_e[:max_lag + 1] = obs, exp
    return out_o, out_e


def excess(obs, exp):
    with np.errstate(invalid="ignore", divide="ignore"):
        return obs / exp - 1.0


def width(obs, exp) -> float:
    """RMS lag (s) of the shoulder-subtracted peak over 0-3 s."""
    x = excess(obs, exp)
    peak = x[PEAK[0]:PEAK[1] + 1] - np.nanmean(x[SHOULDER[0]:SHOULDER[1] + 1])
    w = np.clip(np.nan_to_num(peak), 0, None)
    w[0] *= 0.5
    k = np.arange(len(w)) * DT
    return float(np.sqrt((w * k ** 2).sum() / w.sum())) if w.sum() > 0 else float("nan")


def hwhm(obs, exp) -> float:
    """Half-width at half height (s) of the shoulder-subtracted peak, linearly interpolated.

    The primary width. The RMS lag (:func:`width`) is kept for the record, but it weights the
    0-3 s tail by lag squared, so noise there moves it: on the first run a real fast bump near 3 s
    read as jitter 0.48 s while the peak's own shape sat between 0.1 and 0.36 (Figure 1)."""
    x = excess(obs, exp)
    p = x[PEAK[0]:PEAK[1] + 1] - np.nanmean(x[SHOULDER[0]:SHOULDER[1] + 1])
    if not np.isfinite(p[0]) or p[0] <= 0:
        return float("nan")
    q = p / p[0]
    below = np.nonzero(q < 0.5)[0]
    if below.size == 0:
        return float("nan")
    i = int(below[0])
    return float(DT * (i - 1 + (q[i - 1] - 0.5) / (q[i - 1] - q[i])))


def _real(args):
    folder, i, stream = args
    from bugarach.assess_folder import NoBaselineRegion, generation_window
    from bugarach.io import load_folder

    s = load_folder(Path(folder))[i]
    if stream not in s.streams:
        return None
    try:
        w, _ = generation_window(s)
    except NoBaselineRegion:
        return None
    if w is None or w[1] - w[0] < 900.0:
        return None
    dt = s.require_dt()
    assert abs(dt - DT) < 1e-9, f"{s.slice_id}: frame interval {dt}, this tool assumes {DT}"
    lo, hi = w
    L = int(round((hi - lo) / DT))
    st = s.streams[stream]
    trains = []
    for v in st.t50rise or st.locs:
        v = np.asarray(v, float)
        v = v[np.isfinite(v) & (v >= lo) & (v < hi)]
        trains.append(np.round((v - lo) / DT).astype(int))
    info = {"slice_id": s.slice_id,
            "group": (str(s.meta.get("group_id") or "").strip() or None),
            "mouse": (str(s.meta.get("mouse_id") or s.meta.get("subject_id") or "").strip() or None),
            "rois": len(trains), "onsets": int(sum(t.size for t in trains)),
            "window_sec": round(hi - lo, 1)}
    o, e = pairs(trains, L)
    return info, o, e


def _sim(args):
    bench_name, regime, seed, jitter = args
    import importlib

    b = importlib.import_module(bench_name)
    s, gt = b.make_recording(regime, seed, jitter_sec=jitter)
    L = int(round(gt.params["duration_sec"] / DT))
    trains = [np.round(np.asarray(t, float) / DT).astype(int) for t in s.streams[b.STREAM].t50rise]
    return pairs(trains, L)


def pooled(results):
    """Sum observed and expected pair counts. Takes ``(obs, exp)`` or ``(info, obs, exp)``."""
    o = sum(r[-2] for r in results)
    e = sum(r[-1] for r in results)
    return o, e


def by_group(real):
    """``{group: [record, ...]}`` for the recordings that name a group, in first-seen order."""
    out = {}
    for r in real:
        g = r[0]["group"]
        if g:
            out.setdefault(g, []).append(r)
    return out


def mice_of(records):
    """``{mouse: [record, ...]}``. A recording with no mouse id is its own cluster."""
    out = {}
    for r in records:
        out.setdefault(r[0]["mouse"] or f"?{r[0]['slice_id']}", []).append(r)
    return out


def group_boot(records, stat, n_boot, rs):
    """``stat`` over ``n_boot`` draws that resample this group's MICE with replacement.

    Recordings within a mouse are not independent draws — 84 recordings come from 44 mice — so the
    cluster is the mouse and a drawn mouse brings all of its recordings.
    """
    mice = list(mice_of(records).values())
    out = []
    for _ in range(n_boot):
        pick = rs.randint(0, len(mice), len(mice))
        out.append(stat(*pooled([r for j in pick for r in mice[j]])))
    return np.array(out, float)


def spread(widths):
    """Widest group minus narrowest, over the groups whose width is finite."""
    w = np.array([x for x in widths if np.isfinite(x)], float)
    return float(w.max() - w.min()) if w.size >= 2 else float("nan")


def label_permutation(real, stat, n_perm, rs):
    """Null distribution of :func:`spread` when group labels carry nothing.

    Mouse→group labels are shuffled with each group's number of MICE held fixed, so a group keeps
    its size and therefore its share of the measurement noise: a group of 17 recordings gives a
    noisier width than one of 25, and that is what makes the observed spread hard to read without
    this test. Returns (null spreads, how many draws had no measurable width).
    """
    groups = by_group(real)
    names = list(groups)
    mice = {g: list(mice_of(rs_g).values()) for g, rs_g in groups.items()}
    all_mice = [m for g in names for m in mice[g]]
    sizes = [len(mice[g]) for g in names]
    null, dropped = [], 0
    for _ in range(n_perm):
        order = rs.permutation(len(all_mice))
        at, widths = 0, []
        for n in sizes:
            take = [r for j in order[at:at + n] for r in all_mice[j]]
            widths.append(stat(*pooled(take)))
            at += n
        s = spread(widths)
        if np.isfinite(s):
            null.append(s)
        else:
            dropped += 1
    return np.array(null, float), dropped


def _group_block(real, converters, a, stream):
    """Per-group widths with mouse-clustered intervals, plus the test that the widths differ.

    ``converters`` maps a statistic's name to the calibration curve's width→σ interpolation, which
    is the same curve the pooled numbers use: the simulator knows nothing about group.
    """
    groups = by_group(real)
    ungrouped = [r for r in real if not r[0]["group"]]
    rows = {}
    for g, recs in sorted(groups.items()):
        mice = mice_of(recs)
        o, e = pooled(recs)
        rows[g] = {"recordings": len(recs), "mice": len(mice),
                   "rois": sum(r[0]["rois"] for r in recs),
                   "onsets": sum(r[0]["onsets"] for r in recs),
                   "slice_ids": sorted(r[0]["slice_id"] for r in recs),
                   "real_excess": excess(o, e).tolist()}
    contrasts = {}
    for name, stat in (("hwhm", hwhm), ("width", width)):
        to_jitter = converters[name]
        rs = np.random.RandomState(20260922)
        boots = {}
        for g, recs in sorted(groups.items()):
            w = stat(*pooled(recs))
            wb = group_boot(recs, stat, a.boot, rs)
            # One width per recording, in the order of this group's `slice_ids`. Not what the
            # group's number is — that is read off the pooled counts — but what it is drawn over,
            # and the count of recordings with no measurable peak is why the two differ.
            per = [stat(r[-2], r[-1]) for r in sorted(recs, key=lambda r: r[0]["slice_id"])]
            boots[g] = wb
            jb = np.array([to_jitter(x) for x in wb])
            rows[g][name] = {
                "real_sec": w,
                "real_interval": np.nanpercentile(wb, [2.5, 97.5]).tolist(),
                "jitter_sec": to_jitter(w),
                "jitter_interval": (np.nanpercentile(jb, [2.5, 97.5]).tolist()
                                    if np.isfinite(jb).any() else None),
                "boot_outside_calibration": int(np.isnan(jb).sum()),
                "boot_unmeasurable": int(np.isnan(wb).sum()),
                "per_recording_sec": [None if not np.isfinite(x) else float(x) for x in per],
                "mean_of_recordings_sec": float(np.nanmean(per)),
                "median_of_recordings_sec": float(np.nanmedian(per)),
                "recordings_with_no_peak": int(np.isnan(per).sum())}
        names = sorted(groups)
        obs_widths = [rows[g][name]["real_sec"] for g in names]
        obs_spread = spread(obs_widths)
        null, dropped = label_permutation(real, stat, a.perm, np.random.RandomState(1_20260922))
        p = (float((null >= obs_spread).sum() + 1) / (null.size + 1)
             if null.size and np.isfinite(obs_spread) else None)
        pairwise = {}
        for i, g in enumerate(names):
            for h in names[i + 1:]:
                d = boots[g] - boots[h]
                pairwise[f"{g} - {h}"] = {
                    "diff_sec": rows[g][name]["real_sec"] - rows[h][name]["real_sec"],
                    "interval": np.nanpercentile(d, [2.5, 97.5]).tolist()}
        contrasts[name] = {"groups": names, "widths_sec": obs_widths,
                           "spread_sec": obs_spread,
                           "permutation": {"draws": int(null.size), "unmeasurable": dropped,
                                           "null_median_sec": (float(np.median(null))
                                                               if null.size else None),
                                           "null_95th_sec": (float(np.percentile(null, 95))
                                                             if null.size else None),
                                           "p_any_difference": p},
                           "pairwise": pairwise}
        print(f"  [{stream}] {name} by group_id "
              f"(mouse-clustered {a.boot} draws, {a.perm} label permutations):", flush=True)
        for g in names:
            r = rows[g][name]
            ci = r["real_interval"]
            ji = r["jitter_interval"]
            print(f"    {g:5s} {rows[g]['recordings']:2d} recordings / {rows[g]['mice']:2d} mice / "
                  f"{rows[g]['rois']:4d} ROIs / {rows[g]['onsets']:6d} onsets: "
                  f"{r['real_sec']:.3f} s [{ci[0]:.3f}, {ci[1]:.3f}]"
                  + (f", sigma {r['jitter_sec']:.3f} s [{ji[0]:.3f}, {ji[1]:.3f}]" if ji else ""),
                  flush=True)
        nul = contrasts[name]["permutation"]
        print(f"    spread {obs_spread:.3f} s; null median {nul['null_median_sec']:.3f} s, "
              f"95th {nul['null_95th_sec']:.3f} s; p(any difference) = {p:.4f}", flush=True)
    if ungrouped:
        contrasts["ungrouped_recordings"] = [r[0]["slice_id"] for r in ungrouped]
        print(f"  [{stream}] {len(ungrouped)} recordings name no group_id and are in the pooled "
              f"numbers only", flush=True)
    return rows, contrasts


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--jobs", type=int, default=12)
    ap.add_argument("--boot", type=int, default=200)
    ap.add_argument("--by-group", action="store_true",
                    help="also split by group_id: per-group widths, mouse-clustered intervals, "
                         "and a label-permutation test of whether the widths differ at all")
    ap.add_argument("--perm", type=int, default=2000, help="label permutations for --by-group")
    ap.add_argument("--out", type=Path, required=True)
    a = ap.parse_args(argv)
    a.out.mkdir(parents=True, exist_ok=True)

    from bugarach import dataset
    from bugarach.io import load_folder

    folder = dataset.default()
    n = len(load_folder(folder))
    rec = {"dataset": dataset.stamp(), "dt": DT, "peak_sec": [PEAK[0] * DT, PEAK[1] * DT],
           "shoulder_sec": [SHOULDER[0] * DT, SHOULDER[1] * DT], "jitters": list(JITTERS),
           "sim_seeds": [SIM_SEEDS[0], SIM_SEEDS[-1]], "boot_draws": a.boot,
           "permutations": (a.perm if a.by_group else None),
           "by_group": bool(a.by_group), "streams": {}}
    with ProcessPoolExecutor(a.jobs) as ex:
        for stream, bench_name in BENCHES.items():
            real = [r for r in ex.map(_real, [(str(folder), i, stream) for i in range(n)]) if r]
            o, e = pooled(real)
            rng = np.random.RandomState(20260922)
            draws = [pooled([real[j] for j in rng.randint(0, len(real), len(real))])
                     for _ in range(a.boot)]

            sims, curves = {}, {}
            for j in JITTERS:
                jobs = [(bench_name, r, s, j) for r in ("baseline_quiet", "baseline_busy")
                        for s in SIM_SEEDS]
                sims[j] = pooled(list(ex.map(_sim, jobs)))
                curves[j] = excess(*sims[j]).tolist()

            converters = {}
            out = dict(recordings=len(real), real_excess=excess(o, e).tolist(),
                       sim_excess={str(j): c for j, c in curves.items()},
                       bench_jitter_sec=__import__(bench_name, fromlist=["x"]).BENCH_RECORDING["jitter_sec"])
            print(f"{stream}: {len(real)} recordings (bench jitter now {out['bench_jitter_sec']} s)",
                  flush=True)
            for stat in (hwhm, width):
                ws = np.array([stat(*sims[j]) for j in JITTERS])
                monotone = bool(np.all(np.diff(ws) > 0))

                def to_jitter(w, ws=ws, monotone=monotone):
                    return (float(np.interp(w, ws, JITTERS, left=np.nan, right=np.nan))
                            if monotone else float("nan"))

                converters[stat.__name__] = to_jitter
                w_real = stat(o, e)
                wb = np.array([stat(*d) for d in draws])
                jb = np.array([to_jitter(w) for w in wb])
                row = dict(real_sec=w_real, real_interval=np.nanpercentile(wb, [2.5, 97.5]).tolist(),
                           calibration_sec={str(j): float(w) for j, w in zip(JITTERS, ws)},
                           calibration_monotone=monotone, jitter_sec=to_jitter(w_real),
                           jitter_interval=(np.nanpercentile(jb, [2.5, 97.5]).tolist()
                                            if np.isfinite(jb).any() else None),
                           boot_outside_calibration=int(np.isnan(jb).sum()))
                out[stat.__name__] = row
                ji = row["jitter_interval"]
                print(f"  {stat.__name__:5s} real {w_real:.3f} s "
                      f"[{row['real_interval'][0]:.3f}, {row['real_interval'][1]:.3f}]; calibration "
                      + ", ".join(f"{j:g}->{w:.3f}" for j, w in zip(JITTERS, ws))
                      + ("" if monotone else " NOT MONOTONE")
                      + f"; jitter {row['jitter_sec']:.3f} s "
                      + (f"[{ji[0]:.3f}, {ji[1]:.3f}]" if ji else "[none]")
                      + f" ({row['boot_outside_calibration']} of {a.boot} draws off the curve)",
                      flush=True)
            out["primary"] = "hwhm"
            if a.by_group:
                out["groups"], out["contrasts"] = _group_block(real, converters, a, stream)
            rec["streams"][stream] = out
    (a.out / "jitter_correlogram.json").write_text(json.dumps(rec, indent=1) + "\n", encoding="utf-8")
    print(f"wrote {a.out / 'jitter_correlogram.json'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
