#!/usr/bin/env python3
"""Step 1 of the readiness route on the tracked cohorts: what the baselines look like.

    python docs/learned/runs/2026-11-12-baseline-characterization-3x-4x/characterize.py --figure <dir>

Statistics of when onsets occur relative to each other, with no event defined and no model of
coordination fitted: the cross-ROI onset correlogram, the excess pair and triple counts of the
population in sliding windows (each recording against shifted copies of its own trains), and the
per-ROI onset rates. The functions are those of the measuring tools
(`tools/measure_jitter_correlogram.py`, `tools/measure_coordination_rates.py`); nothing is
re-derived here.

Reads the default folder (4 x sigma_est) and `tracked_cohorts_3x`, the three streams the export
carries (fast, slow and combined; ADR-0023), and each recording's **baseline analysis window only**
(`assess_folder.generation_window`). The window read is written into the record per recording.
Recordings are pooled three ways: all of them, DI and MALE. That split describes the data for
building synthetic recordings; it tests nothing between the groups (ADR-0017).
"""
from __future__ import annotations

import argparse
import json
import sys
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
sys.path.insert(0, str(REPO / "src"))
sys.path.insert(0, str(REPO / "tools"))

ROLES = {"4x": "tracked_cohorts", "3x": "tracked_cohorts_3x"}
STREAMS = ("fast", "slow", "combined")
SEED = 20261112


def _one(args):
    folder, i, stream = args
    import measure_coordination_rates as mcr
    import measure_jitter_correlogram as mjc
    from bugarach.assess_folder import generation_window
    from bugarach.io import load_folder

    s = load_folder(Path(folder))[i]
    (lo, hi), source = generation_window(s)
    label = next((r.name for r in s.regions if r.start_sec <= lo and hi <= r.end_sec), None)
    assert label is not None and label.lower() == "baseline", (s.slice_id, label)
    L = int(round((hi - lo) / mcr.DT))
    st = s.streams[stream]
    onsets = st.t50rise or st.locs
    trains = [mcr._frames(v, lo, hi) for v in onsets]
    obs, exp = mjc.pairs(trains, L)
    m = mcr.measure(trains, L, np.random.RandomState(SEED + i))
    T = L * mcr.DT
    return {"slice_id": s.slice_id, "group": str(s.meta.get("group_id")),
            "mouse": str(s.meta.get("mouse_id") or s.meta.get("subject_id")),
            "window_sec": [float(lo), float(hi)], "window_label": label, "window_source": source,
            "n_roi": len(trains), "n_onsets": int(sum(len(t) for t in trains)),
            "roi_rates_hz": [len(t) / T for t in trains], "rate_hz": m["rate"],
            "cum": m["cum"], "obs": obs.tolist(), "exp": exp.tolist(),
            # this recording's own correlogram: pairs expected by chance at zero lag (how much
            # there is to read a peak from), the peak over chance, and its half-width
            "corr_expected_pairs_at_zero_lag": float(exp[0]),
            "corr_excess_at_zero_lag": (float(obs[0] / exp[0] - 1.0) if exp[0] > 0 else None),
            "corr_half_width_sec": (lambda h: None if not np.isfinite(h) else float(h))(
                mjc.hwhm(obs, exp))}


def pool(recs):
    import measure_jitter_correlogram as mjc

    obs = np.sum([r["obs"] for r in recs], axis=0)
    exp = np.sum([r["exp"] for r in recs], axis=0)
    x = mjc.excess(obs, exp)
    out = {"recordings": len(recs), "mice": len({r["mouse"] for r in recs}),
           "rois": int(sum(r["n_roi"] for r in recs)), "onsets": int(sum(r["n_onsets"] for r in recs)),
           "baseline_minutes": float(sum(r["window_sec"][1] - r["window_sec"][0] for r in recs) / 60),
           "correlogram_excess": [None if not np.isfinite(v) else float(v) for v in x],
           "correlogram_excess_at_zero_lag": float(x[0]),
           "correlogram_shoulder_5_to_10_sec": float(np.nanmean(x[50:101])),
           "correlogram_half_width_sec": mjc.hwhm(obs, exp),
           "rate_hz_per_recording_quartiles": [float(v) for v in np.percentile(
               [r["rate_hz"] for r in recs], (25, 50, 75))],
           "cumulants": {}}
    for w in recs[0]["cum"]:
        f2 = np.array([r["cum"][w]["f2"] for r in recs]) / float(w)
        f3 = np.array([r["cum"][w]["f3"] for r in recs]) / float(w)
        out["cumulants"][w] = {"excess_pairs_per_sec_median": float(np.median(f2)),
                               "excess_pairs_per_sec_range": [float(f2.min()), float(f2.max())],
                               "excess_triples_per_sec_median": float(np.median(f3)),
                               "excess_triples_per_sec_range": [float(f3.min()), float(f3.max())],
                               "recordings_with_positive_pairs": int((f2 > 0).sum())}
    return out


def measure_all(jobs):
    from bugarach import dataset
    from bugarach.groups import in_group_order
    from bugarach.io import load_folder

    rec = {"what": "baseline analysis windows only; fast, slow and combined as exported", "by_threshold": {}}
    with ProcessPoolExecutor(jobs) as ex:
        for thr, role in ROLES.items():
            folder = dataset.current(role)
            n = len(load_folder(folder))
            block = {"dataset": dataset.stamp(role), "streams": {}}
            for stream in STREAMS:
                recs = list(ex.map(_one, [(str(folder), i, stream) for i in range(n)]))
                groups = in_group_order({r["group"] for r in recs})
                block["streams"][stream] = {
                    "pooled": {"all": pool(recs),
                               **{g: pool([r for r in recs if r["group"] == g]) for g in groups}},
                    "per_recording": [{k: v for k, v in r.items() if k not in ("obs", "exp")}
                                      for r in recs]}
            rec["by_threshold"][thr] = block
    return rec


def figure(rec, out_dir: Path):
    import subprocess

    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    colors = {"all": "#222222", "DI": "#0072B2", "MALE": "#D55E00"}
    styles = {"4x": "-", "3x": "--"}
    lags = np.arange(101) * 0.1
    written = []
    for stream in STREAMS:
        fig, axes = plt.subplots(1, 4, figsize=(17, 4.2))
        a_c, a_2, a_3, a_r = axes
        for thr in ROLES:
            S = rec["by_threshold"][thr]["streams"][stream]
            for g, P in S["pooled"].items():
                kw = dict(color=colors[g], ls=styles[thr], lw=1.8 if g == "all" else 1.1)
                x = np.array([np.nan if v is None else v for v in P["correlogram_excess"]])
                a_c.plot(lags, x, label=f"{g}, {thr}", **kw)
                ws = sorted(P["cumulants"], key=float)
                a_2.plot([float(w) for w in ws],
                         [P["cumulants"][w]["excess_pairs_per_sec_median"] for w in ws],
                         marker="o", ms=4, **kw)
                a_3.plot([float(w) for w in ws],
                         [P["cumulants"][w]["excess_triples_per_sec_median"] for w in ws],
                         marker="o", ms=4, **kw)
            names = [k for k in S["pooled"] if k != "all"]
            for j, g in enumerate(names):
                rs = [r["rate_hz"] for r in S["per_recording"] if r["group"] == g]
                xs = np.full(len(rs), j + (-0.15 if thr == "4x" else 0.15))
                a_r.scatter(xs, rs, color=colors[g], marker="o" if thr == "4x" else "x", s=30,
                            label=f"{g}, {thr}")
            a_r.set_xticks(range(len(names)))
            a_r.set_xticklabels(names)
            a_r.set_xlim(-0.6, len(names) - 0.4)
        a_c.set_xscale("symlog", linthresh=1.0)
        a_c.set_xlim(0, 10)
        a_c.set_xticks([0, 0.5, 1, 2, 5, 10])
        a_c.set_xticklabels(["0", "0.5", "1", "2", "5", "10"])
        a_c.set_ylabel(f"{stream} stream: onset pairs over chance, minus 1")
        a_c.set_xlabel("lag between the onsets of two ROIs (s)")
        a_2.set_ylabel("excess onset pairs per second of window")
        a_3.set_ylabel("excess onset triples per second of window")
        for ax in (a_2, a_3):
            ax.set_xlabel("window (s)")
            ax.set_xticks([1, 2, 4])
            ax.set_ylim(bottom=0)
        a_r.set_ylabel("onsets per ROI per second (one mark per recording)")
        a_r.set_yscale("log")
        a_c.legend(fontsize=7, ncol=2, frameon=False)
        a_r.legend(fontsize=7, ncol=2, frameon=False)
        fig.tight_layout()
        name = subprocess.run(
            [sys.executable, str(REPO / "tools/naming/artifact_name.py"), "build", "--type",
             "baseline-by-group", "--signal", "roi", "--stream", stream, "--treatment", "baseline",
             "--groups", "di+male", "--win", "win20min", "--date", "20261112", "--ext", "png"],
            capture_output=True, text=True)
        if name.returncode != 0 or not name.stdout.strip():
            raise SystemExit(f"naming tool refused: {name.stderr or name.stdout}")
        out_dir.mkdir(parents=True, exist_ok=True)
        path = out_dir / name.stdout.strip().splitlines()[-1]
        fig.savefig(path, dpi=150)
        plt.close(fig)
        written.append(path)
    return written


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--jobs", type=int, default=12)
    ap.add_argument("--figure", type=Path, help="directory for the figure (a claimed darkroom folder)")
    ap.add_argument("--from-record", action="store_true", help="redraw from the saved record")
    a = ap.parse_args(argv)
    path = HERE / "baseline_characterization.json"
    rec = json.loads(path.read_text(encoding="utf-8")) if a.from_record else measure_all(a.jobs)
    if not a.from_record:
        path.write_text(json.dumps(rec, indent=1) + "\n", encoding="utf-8")
    if a.figure:
        print("figures:", [p.name for p in figure(rec, a.figure)])
    for thr, B in rec["by_threshold"].items():
        for stream, S in B["streams"].items():
            for g, P in S["pooled"].items():
                c = P["cumulants"]
                print(f"{thr} {stream} {g}: {P['recordings']} rec, {P['mice']} mice, {P['rois']} ROIs, "
                      f"{P['onsets']} onsets, {P['baseline_minutes']:.0f} min | zero-lag "
                      f"{P['correlogram_excess_at_zero_lag']:.1f}, shoulder "
                      f"{P['correlogram_shoulder_5_to_10_sec']:.2f}, half-width "
                      f"{P['correlogram_half_width_sec']:.2f} s | pairs/s "
                      + ", ".join(f"{w}s {c[w]['excess_pairs_per_sec_median']:.3g}" for w in c)
                      + " | triples/s "
                      + ", ".join(f"{w}s {c[w]['excess_triples_per_sec_median']:.3g}" for w in c)
                      + f" | rate quartiles {[round(v, 4) for v in P['rate_hz_per_recording_quartiles']]}")
    windows = {(r["window_label"], round(r["window_sec"][1] - r["window_sec"][0]))
               for B in rec["by_threshold"].values() for S in B["streams"].values()
               for r in S["per_recording"]}
    print("windows read (label, seconds):", sorted(windows))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
