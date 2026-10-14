#!/usr/bin/env python3
"""The coordinated fraction of calcium events under treatment 1, each recording against its own baseline.

ADR-0017's first exception (Tony, 2026-10-14): coordination under a treatment is bugarach's to
measure, because the measure only means something with the checks that live here. The
quantity is the one ``tools/measure_coordination_rates.py`` defines, imported from it and not
copied: per recording and window, the excess factorial cumulants of the population onset
count over a rigid-shift surrogate, solved for the rate of shared moments (λ) and the cells
per moment (*k*), so that the coordinated rate per cell is λ·*k*/*N* and **the coordinated
fraction is that divided by the cell's event rate**. Read that tool's docstring first.

**What this tool adds.**

* **Two windows per recording.** Baseline is ``assess_folder.generation_window`` (the longest
  baseline region, the producer's analysis window inside it). Treatment 1 is the first region
  after the baseline in time, its analysis window wherever the folder states one, the same
  ordering ``make_group_raster_summary.treatment_one`` uses. Nothing after treatment 1 is read
  (Tony, 2026-10-14: treatment 2 and high K+ are out for now).
* **The f3/f2 ratio is pooled per condition, within one folder.** The baseline tool pools it
  over every recording because one recording's *f*₃ is noisy. Pooled across both conditions,
  it would force the cells per moment to be the same in both, which is one of the things a
  treatment might change.
* **Blank windows are respected.** A hand-reviewed folder carries ``review_blank_windows.tsv``:
  spans in which the producer removed events because a person marked them as artifacts. A
  span covering every ROI silences the whole field at once, which this statistic would read
  as shared modulation, so it is **cut out of the timeline** of the window it falls in. A span
  covering only some ROIs cannot be cut from a shared timeline, so **those ROIs are dropped
  from that recording in both windows**, keeping the pair like for like. Both are recorded.

**What it does not do.** It fits nothing and tunes nothing on a treatment window (FOUNDATIONS
§9: calibrate from baseline only); the estimator and its calibration are the baseline
tool's. It reports per folder and per group and never pools across folders: the two 2026
pilots differ in group *and* treatment, so a comparison between them is confounded.

**Reading the number.** The surrogate keeps shared changes slower than its offsets span
(about a minute at a 1 s window), and they count as coordination. A recording whose
treatment window has a slow drift that its baseline does not will read higher for that
reason. ``shape_usable`` is reported per window, because at low rates *f*₃ is noisy.

Usage::

    python tools/measure_coordination_under_treatment.py --folder <name or path> [--folder ...]

Each folder is resolved by name through ``bugarach.dataset`` (an eval folder is read by name
on purpose), which also names it on stderr. Output defaults to a dated darkroom folder.
"""
from __future__ import annotations

import argparse
import csv
import json
import sys
from concurrent.futures import ProcessPoolExecutor
from datetime import date
from pathlib import Path

import numpy as np

REPO = Path(__file__).resolve().parents[1]
for _p in (REPO / "src", REPO / "tools"):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

import measure_coordination_rates as mcr  # noqa: E402  the statistic, imported not copied

DT = mcr.DT
CONDITIONS = ("baseline", "treatment_1")
STREAMS = ("fast", "slow", "combined")
BLANKS = "review_blank_windows.tsv"


# ---------------------------------------------------------------- windows and blanks

def treatment_one_window(s) -> tuple[str, tuple[float, float]] | None:
    """(label, (start, end)) of the first region after the baseline, analysis window first."""
    from bugarach.assess_folder import is_baseline

    regions = sorted(s.regions or [], key=lambda r: float(r.start_sec))
    base_end = max((float(r.end_sec) for r in regions if is_baseline(r, None)), default=None)
    if base_end is None:
        return None
    for r in regions:
        if not is_baseline(r, None) and float(r.start_sec) >= base_end - 1e-6:
            if r.has_analysis_window:
                return r.name, (float(r.analysis_start_sec), float(r.analysis_end_sec))
            return r.name, (float(r.start_sec), float(r.end_sec))
    return None


def read_blanks(folder: Path) -> dict[str, list[tuple[set[str] | None, float, float]]]:
    """slice_id -> [(rois or None for every ROI, start_sec, end_sec)]. Empty if no file.

    The two 2026 pilots spell the ROI column differently (``window_rois`` in August,
    ``rois`` in September); both are read.
    """
    path = folder / BLANKS
    out: dict[str, list] = {}
    if not path.is_file():
        return out
    with path.open(encoding="utf-8", newline="") as fh:
        for row in csv.DictReader(fh, delimiter="\t"):
            spec = (row.get("window_rois") or row.get("rois") or "").strip()
            rois = None if spec.upper() == "ALL" else {
                str(int(float(x))) for x in spec.split(",") if x.strip()}
            out.setdefault(row["slice_id"], []).append(
                (rois, float(row["start_sec"]), float(row["end_sec"])))
    return out


def kept_spans(lo: float, hi: float, cuts) -> list[tuple[float, float]]:
    """[lo, hi) with every (a, b) in ``cuts`` removed, as sorted disjoint spans."""
    spans = [(lo, hi)]
    for a, b in sorted(cuts):
        nxt = []
        for s, e in spans:
            if b <= s or a >= e:
                nxt.append((s, e))
                continue
            if a > s:
                nxt.append((s, a))
            if b < e:
                nxt.append((b, e))
        spans = nxt
    return spans


def excised_frames(v, spans) -> np.ndarray:
    """Onset times mapped onto the timeline with the cut spans closed up, in frames."""
    v = np.asarray(v, float)
    v = v[np.isfinite(v)]
    parts, offset = [], 0.0
    for s, e in spans:
        sel = v[(v >= s) & (v < e)]
        parts.append(np.round((sel - s + offset) / DT).astype(int))
        offset += e - s
    return np.unique(np.concatenate(parts)) if parts else np.zeros(0, int)


def _roi_key(rid) -> str:
    try:
        return str(int(float(rid)))
    except (TypeError, ValueError):
        return str(rid)


# ---------------------------------------------------------------- one recording

def _one(args):
    folder, i, seed = args
    from bugarach.assess_folder import NoBaselineRegion, generation_window
    from bugarach.combined import COMBINED, has_sources, stream_of
    from bugarach.io import load_folder

    s = load_folder(Path(folder))[i]
    dt = s.require_dt()
    assert abs(dt - DT) < 1e-9, f"{s.slice_id}: frame interval {dt}, this tool assumes {DT}"
    try:
        base, _ = generation_window(s)
    except NoBaselineRegion:
        return {"slice_id": s.slice_id, "skipped": "no baseline region"}
    t1 = treatment_one_window(s)
    if base is None or t1 is None:
        return {"slice_id": s.slice_id,
                "skipped": "no regions" if base is None else "no treatment after baseline"}
    label, treat = t1
    windows = {"baseline": base, "treatment_1": treat}

    blanks = read_blanks(Path(folder)).get(s.slice_id, [])
    roi_keys = [_roi_key(r) for r in (s.roi_ids or [])]
    dropped = sorted({r for rois, a, b in blanks if rois is not None
                      for w in windows.values() if a < w[1] and b > w[0]
                      for r in rois if r in roi_keys}, key=lambda r: (len(r), r))
    keep = [j for j, r in enumerate(roi_keys) if r not in dropped] if roi_keys else None

    out = {"slice_id": s.slice_id, "treatment_1": label, "dropped_rois": dropped,
           "group": (str((s.meta or {}).get("group_id") or "").strip() or None),
           "mouse": str((s.meta or {}).get("subject_id") or s.slice_id), "windows": {}}
    rng = np.random.RandomState(seed + i)
    for cond, (lo, hi) in windows.items():
        cuts = [(max(a, lo), min(b, hi)) for rois, a, b in blanks
                if rois is None and a < hi and b > lo]
        spans = kept_spans(lo, hi, cuts)
        T = sum(e - s_ for s_, e in spans)
        L = int(round(T / DT))
        rec = {"start_sec": lo, "end_sec": hi, "cut_sec": round((hi - lo) - T, 3),
               "streams": {}}
        for stream in STREAMS:
            if not (stream in s.streams or (stream == COMBINED and has_sources(s))):
                continue
            st = stream_of(s, stream)
            rows = st.t50rise or st.locs
            if keep is not None:
                rows = [rows[j] for j in keep]
            trains = [np.minimum(excised_frames(v, spans), L - 1) for v in rows]
            rec["streams"][stream] = mcr.measure(trains, L, rng)
        out["windows"][cond] = rec
    return out


# ---------------------------------------------------------------- the comparison

def compare(recs: list[dict], stream: str, w: float, model: str) -> dict:
    """Per-recording baseline and treatment-1 fractions, the ratio pooled per condition."""
    paired = [r for r in recs if "windows" in r
              and all(stream in r["windows"][c]["streams"] for c in CONDITIONS)]
    per = {c: mcr.per_recording([r["windows"][c]["streams"][stream] for r in paired], w, model)
           for c in CONDITIONS}
    rows = []
    for j, r in enumerate(paired):
        row = {"slice_id": r["slice_id"], "group": r["group"], "mouse": r["mouse"]}
        for c in CONDITIONS:
            m = r["windows"][c]["streams"][stream]
            est = per[c][j]
            rate = m["rate"]
            row[c] = {"N": m["N"], "seconds": m["T"], "rate_hz": rate,
                      "shape_usable": bool(m["shape_usable"]),
                      "shared_moments_per_min": est["lam"] * 60,
                      "participants_per_moment": est["k"],
                      "coordinated_hz": est["share"],
                      "fraction": (est["share"] / rate if rate > 0 and np.isfinite(est["share"])
                                   else float("nan"))}
        fb, ft = row["baseline"]["fraction"], row["treatment_1"]["fraction"]
        row["ratio"] = ft / fb if np.isfinite(fb) and fb > 0 and np.isfinite(ft) else float("nan")
        rows.append(row)

    def med(xs):
        xs = [x for x in xs if np.isfinite(x)]
        return float(np.median(xs)) if xs else float("nan")

    def summary(sub):
        ratios = [x["ratio"] for x in sub]
        loo = ([med(ratios[:j] + ratios[j + 1:]) for j in range(len(ratios))]
               if len(ratios) > 2 else [])
        return {
            "recordings": len(sub), "mice": len({x["mouse"] for x in sub}),
            "median_fraction": {c: med([x[c]["fraction"] for x in sub]) for c in CONDITIONS},
            "median_rate_hz": {c: med([x[c]["rate_hz"] for x in sub]) for c in CONDITIONS},
            "median_shared_moments_per_min": {
                c: med([x[c]["shared_moments_per_min"] for x in sub]) for c in CONDITIONS},
            "median_ratio": med(ratios),
            "ratio_leave_one_out": [min(loo), max(loo)] if loo else None,
            "treatment_at_or_above_baseline": int(sum(1 for x in ratios
                                                      if np.isfinite(x) and x >= 1)),
        }

    # A window below shape_usable's floors (too few events) has an f3 too noisy to trust,
    # and a treatment that cuts the event rate puts many treatment windows there. The
    # fraction of almost nothing is not a measurement, so the headline is taken over the
    # recordings usable in BOTH windows; the all-recordings summary stays beside it.
    usable = [x for x in rows if all(x[c]["shape_usable"] for c in CONDITIONS)]
    return {
        **summary(usable),
        "usable_in_both": [x["slice_id"] for x in usable],
        "all_recordings": summary(rows),
        "pooled_participants_per_moment": {c: med([x[c]["participants_per_moment"] for x in rows])
                                           for c in CONDITIONS},
        "per_recording": rows,
    }


# ---------------------------------------------------------------- figure

def before_after_png(rows: list[dict], label: str, stream: str, group: str, path: Path) -> None:
    """One line per recording, baseline to treatment 1, the median as a heavier line."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(figsize=(3.4, 3.6), dpi=150)
    good = []
    for r in rows:
        b, t = r["baseline"]["fraction"] * 100, r["treatment_1"]["fraction"] * 100
        if not (np.isfinite(b) and np.isfinite(t)):
            continue
        ok = all(r[c]["shape_usable"] for c in CONDITIONS)
        if ok:
            good.append((b, t))
        # A pair with a window below shape_usable's floors is drawn hollow and dashed: it is
        # shown, because hiding it would hide what the treatment did to the event rate, and
        # it is kept out of the median, because its fraction is not a measurement.
        ax.plot([0, 1], [b, t], color="0.45" if ok else "0.7", lw=1,
                ls="-" if ok else "--", marker="o", ms=3.5,
                mfc="0.45" if ok else "white", mec="0.45" if ok else "0.6")
    if good:
        ax.plot([0, 1], np.median(np.array(good), axis=0), color="black", lw=2.5,
                marker="o", ms=5)
    ax.set_xticks([0, 1], ["baseline", label])
    ax.set_xlim(-0.3, 1.3)
    ax.set_ylim(bottom=min(0, ax.get_ylim()[0]))
    ax.set_ylabel(f"coordinated fraction of events (%)\n{stream} · {group} · "
                  f"{len(good)} of {len(rows)} usable")
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    fig.tight_layout()
    fig.savefig(path)
    plt.close(fig)


# ---------------------------------------------------------------- main

def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--folder", action="append", required=True,
                    help="an export folder, by name or path; repeat for several. A folder "
                         "under exports/bugarach_eval/ is not searched by name: pass its path")
    ap.add_argument("--source", action="append", default=None,
                    help="the naming scheme's source for each --folder, in order "
                         "(e.g. pilot-20260811); 'none' for the main series")
    ap.add_argument("--treatment-name", action="append", default=None,
                    help="the naming scheme's treatment code for each --folder, in order")
    ap.add_argument("--win", default="win20min",
                    help="the naming scheme's analysis-window code (the 2026 pilots: win20min)")
    ap.add_argument("--jobs", type=int, default=12)
    ap.add_argument("--seed", type=int, default=20261014)
    ap.add_argument("--out", type=Path, default=None,
                    help="default: <darkroom>/<today>-coordinated-fraction-under-treatment/")
    a = ap.parse_args(argv)

    from bugarach import dataset, paths
    from bugarach.groups import in_group_order
    from bugarach.io import load_folder
    from naming import artifact_name

    today = date.today().strftime("%Y%m%d")
    out = a.out or (paths.darkroom(create=True) / f"{date.today():%Y-%m-%d}-coordinated-fraction-under-treatment")
    out.mkdir(parents=True, exist_ok=True)
    codes = artifact_name.load_codes()

    with ProcessPoolExecutor(a.jobs) as ex:
        for k, spec in enumerate(a.folder):
            folder = dataset.require(spec, want="export_folder", flag="--folder")
            # ADR-0018: say which folder is read. dataset.report names declared folders
            # only, and an eval folder read by name may not be declared.
            print(f"dataset: {folder.name} — {dataset.describe(folder)}", file=sys.stderr)
            n = len(load_folder(folder))
            recs = list(ex.map(_one, [(str(folder), i, a.seed) for i in range(n)]))
            skipped = [r for r in recs if "skipped" in r]
            recs = [r for r in recs if "skipped" not in r]
            labels = sorted({r["treatment_1"] for r in recs})
            groups = in_group_order({r["group"] for r in recs if r["group"]})
            rec = {"folder": folder.name, "readme_first_line": _first_line(folder / "README.md"),
                   "recordings": n, "skipped": skipped, "treatment_1": labels, "groups": groups,
                   "dt": DT, "windows_sec": list(mcr.WINDOWS), "primary_window_sec": mcr.PRIMARY_W,
                   "adopted_model": mcr.ADOPTED_MODEL, "surrogates": mcr.N_SURR, "seed": a.seed,
                   "blanks": {r["slice_id"]: {"dropped_rois": r["dropped_rois"],
                                              "cut_sec": {c: r["windows"][c]["cut_sec"]
                                                          for c in CONDITIONS}} for r in recs},
                   "streams": {}}
            for stream in STREAMS:
                rec["streams"][stream] = {
                    f"{m}@{w}": compare(recs, stream, w, m)
                    for w in mcr.WINDOWS for m in mcr.MODELS}
                head = rec["streams"][stream][f"{mcr.ADOPTED_MODEL}@{mcr.PRIMARY_W}"]
                print(f"{folder.name} {stream}: {head['recordings']} of "
                      f"{head['all_recordings']['recordings']} recordings usable in both; "
                      f"fraction baseline {head['median_fraction']['baseline']:.4f} -> "
                      f"treatment_1 {head['median_fraction']['treatment_1']:.4f}; median ratio "
                      f"{head['median_ratio']:.2f}, leave-one-out {head['ratio_leave_one_out']}, "
                      f"{head['treatment_at_or_above_baseline']} at or above", flush=True)
                if a.source and a.treatment_name:
                    name = artifact_name.build(
                        codes, type="before-after", ext="png", date=today,
                        source=None if a.source[k] == "none" else a.source[k], signal="roi",
                        stream=stream, treatment=a.treatment_name[k],
                        groups="-".join(g.lower() for g in groups), win=a.win)
                    before_after_png(head["per_recording"], " / ".join(labels), stream,
                                     "-".join(groups), out / name)
                    print(f"  wrote {out / name}")
            dest = out / folder.name
            dest.mkdir(exist_ok=True)
            (dest / "coordination_under_treatment.json").write_text(
                json.dumps(rec, indent=1, default=float) + "\n")
            print(f"wrote {dest / 'coordination_under_treatment.json'}")
    return 0


def _first_line(p: Path) -> str | None:
    try:
        return next((ln.strip() for ln in p.read_text(encoding="utf-8").splitlines()
                     if ln.strip() and not ln.startswith("#")), None)
    except OSError:
        return None


if __name__ == "__main__":
    raise SystemExit(main())
