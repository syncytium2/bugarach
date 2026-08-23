#!/usr/bin/env python3
"""Assess a store of real recordings, and derive generator settings from them.

    python tools/assess_archive.py --store <dir> --out docs/learned

This is the first half of the per-lab loop: point it at real recordings, measure
how coordinated they are **without using a detector**, and turn that measurement
into settings for the generator. The second half (calibrate the six and train the
learned models on what comes out) is `tools/fair_bakeoff.py`.

**Baseline regions only.** FOUNDATIONS §9, Tony 2026-08-14: *"everything should be
based on baseline recordings. do not use senk or ttx as sources for the properties
of coordination."* Treatments are what the instruments are pointed at; taking
coordination properties from them assumes the answer. Every non-baseline region is
counted and skipped, and the count is reported so the skip is visible.

**K is reported as a scan, never chosen here.** `assess.py` says a caller quoting
one number must say which K produced it, and `docs/todo/2026-08-16-assessment-needs-
a-human-in-the-loop.md` says a human signs off before an assessment parameterizes
anything shipped. This writes every K and marks the default; it does not decide.
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _dataset_arg  # noqa: E402

# The baseline rule lives in the library now, so this driver and `bugarach assess`
# cannot drift apart on which regions may source coordination properties.
from bugarach.assess_folder import BASELINE_TOKENS, is_baseline as _is_baseline  # noqa: E402,F401


def assess_store(store: Path, *, stream: str | None, n_surrogates: int,
                 limit: int | None = None, assemblies: bool = False,
                 assembly_surrogates: int = 1000) -> dict:
    """Assess every baseline recording under ``store``.

    **Takes an export folder or a `.mat` store, and prefers the folder.** The
    folder is this project's input contract: it carries the producer's own
    identity columns (group, subject) and — the part that changes numbers — the
    ANALYSIS window, which is the producer saying which part of a period to
    score. A `.mat` store carries neither. Reading `.mat` when a conforming
    folder exists beside it re-derives metadata that was already given and
    scores windows the producer did not intend; that happened here on
    2026-08-18 and is written up in
    ``docs/todo/2026-08-18-experimental-groups-are-not-in-the-import-contract.md``.
    """
    from bugarach.assess import DEFAULT_MIN_ROIS, assess_coactivity
    from bugarach.store import load_slice
    if assemblies:
        from bugarach.assembly import assess_assemblies

    is_folder = (store / "slices.csv").is_file() or (store / "regions.csv").is_file()
    if is_folder:
        from bugarach.io import load_folder
        slices = load_folder(store)
        if limit:
            slices = slices[:limit]
        files = slices
        print(f"reading EXPORT FOLDER: {len(files)} recordings, "
              f"identity and analysis windows from the contract")
    else:
        files = sorted(store.glob("*.mat"))
        if limit:
            files = files[:limit]
        print(f"reading .mat store: {len(files)} files. NOTE: a .mat store carries "
              f"no identity columns and no analysis windows — prefer an export "
              f"folder where one exists.")
    if not files:
        raise SystemExit(f"no recordings under {store}")

    rows: list[dict] = []
    skipped = {"no_baseline_region": 0, "too_short": 0, "load_error": 0,
               "no_stream": 0}
    seen_regions: dict[str, int] = {}
    t0 = time.time()

    n_analysis_window = 0
    for i, f in enumerate(files):
        if is_folder:
            s = f
        else:
            try:
                # dt=None: this pass counts windows and ROIs and builds no
                # sampling grid, so the store's silence about its interval is
                # carried rather than filled in.
                s = load_slice(f, dt=None)
            except Exception as e:                   # noqa: BLE001
                skipped["load_error"] += 1
                print(f"  ! {f.name}: {type(e).__name__}: {e}", file=sys.stderr)
                continue

        for r in (s.regions or []):
            nm = (getattr(r, "name", None) or "<unnamed>").strip().lower()
            seen_regions[nm] = seen_regions.get(nm, 0) + 1

        base = [r for r in (s.regions or []) if _is_baseline(r)]
        if not base:
            skipped["no_baseline_region"] += 1
            continue
        # The longest baseline region; assess.py has its own floor and returns
        # NaN under it, which is reported rather than silently dropped.
        r = max(base, key=lambda r: r.end_sec - r.start_sec)
        # **What to score, not what happened.** A producer that has already
        # decided which part of a period is analysable says so in
        # analysis_start_sec / analysis_end_sec, and that decision is theirs to
        # make. Scoring the raw period instead silently analyses recording the
        # producer excluded — on this folder that was up to 660 s of extra window
        # on 24 of 84 slices, which is more clusters and more power on some
        # slices than others.
        if getattr(r, "has_analysis_window", False):
            win = (r.analysis_start_sec, r.analysis_end_sec)
            n_analysis_window += 1
        else:
            win = (r.start_sec, r.end_sec)

        names = list(s.streams)
        want = stream if stream in names else (stream and None) or names[0]
        if want is None:
            skipped["no_stream"] += 1
            continue

        try:
            res = assess_coactivity(s, stream=want, window=win,
                                    n_surrogates=n_surrogates)
        except Exception as e:                       # noqa: BLE001
            skipped["too_short"] += 1
            print(f"  ~ {f.name}: {type(e).__name__}: {e}", file=sys.stderr)
            continue

        n_roi = s.streams[want].n_rois
        for a in res:
            asm = {}
            if assemblies:
                # Same clusters, asked a different question: not how much
                # coactivity there is, but whether the same cells make it.
                # Both nulls run; `verdict` is only readable as a pair —
                # see bugarach.assembly.
                q = assess_assemblies(a, n_surrogates=assembly_surrogates)
                asm = dict(
                    asm_defined=bool(q.defined), asm_verdict=q.verdict(),
                    asm_n_events=int(q.n_events),
                    asm_mean_pair_count=float(q.mean_pair_count),
                    asm_p_margin_disp=float(q.p_margin_disp),
                    asm_p_margin_eig=float(q.p_margin_eig),
                    asm_p_uniform_disp=float(q.p_uniform_disp),
                    asm_p_uniform_eig=float(q.p_uniform_eig),
                )
            ident = {k: v for k, v in (getattr(s, "meta", None) or {}).items()
                     if k not in ("slice_id",)}
            rows.append(dict(
                **asm, **ident,
                slice_id=s.slice_id, stream=want, n_roi=int(n_roi),
                region=(getattr(r, "name", None) or ""),
                window_sec=float(win[1] - win[0]),
                raw_window_sec=float(r.end_sec - r.start_sec),
                used_analysis_window=bool(getattr(r, "has_analysis_window", False)),
                K=int(a.min_rois),
                part_n_obs=float(a.part_n_obs), jit_obs=float(a.jit_obs),
                jit_null=float(a.jit_null), jit_excess=float(a.jit_excess),
                jit_defined=bool(a.jit_defined),
                span_med=float(a.span_med),
                clusters_permin=float(a.clusters_permin),
                coact_excess=float(a.coact_excess),
                # The assessor's own per-ROI rate. Recovering it downstream from
                # cluster rate x participants gives only the COORDINATED part and
                # lands roughly half the tree's measured baseline floor, which
                # would hand the generator a background nobody records.
                roi_rate_med=float(a.roi_rate_med),
                ev_rate_permin=float(a.ev_rate_permin),
                n_events_win=int(a.n_events_win),
            ))
        if (i + 1) % 20 == 0:
            print(f"  ... {i + 1}/{len(files)} slices, {time.time() - t0:.0f}s")

    if not rows:
        raise SystemExit("no slice yielded an assessment — nothing to report")
    print(f"  scored the producer's ANALYSIS window on {n_analysis_window} "
          f"recording(s); the raw period on {len(files) - n_analysis_window}")

    ks = sorted({r["K"] for r in rows})

    def _agg(k, field):
        v = np.array([r[field] for r in rows if r["K"] == k], dtype=float)
        v = v[np.isfinite(v)]
        if v.size == 0:
            return dict(n=0, median=None, iqr=[None, None])
        return dict(n=int(v.size), median=float(np.median(v)),
                    iqr=[float(np.percentile(v, 25)),
                         float(np.percentile(v, 75))])

    by_k = {}
    for k in ks:
        sub = [r for r in rows if r["K"] == k]
        by_k[str(k)] = {
            "n_slices": len(sub),
            "n_jit_defined": int(sum(r["jit_defined"] for r in sub)),
            **{f: _agg(k, f) for f in ("part_n_obs", "jit_obs", "jit_null",
                                       "jit_excess", "span_med",
                                       "clusters_permin", "coact_excess",
                                       "roi_rate_med", "ev_rate_permin")},
        }

    n_roi = np.array([r["n_roi"] for r in rows if r["K"] == ks[0]], float)
    return {
        "store": store.name,
        "n_files": len(files),
        "n_slices_assessed": len({r["slice_id"] for r in rows}),
        "skipped": skipped,
        "region_labels_seen": dict(sorted(seen_regions.items(),
                                          key=lambda kv: -kv[1])),
        "n_surrogates": n_surrogates,
        "elapsed_sec": round(time.time() - t0, 1),
        "n_roi": dict(median=float(np.median(n_roi)),
                      iqr=[float(np.percentile(n_roi, 25)),
                           float(np.percentile(n_roi, 75))],
                      min=float(n_roi.min()), max=float(n_roi.max())),
        "by_k": by_k,
        "background": _fit_background(files if is_folder else None),
        "rows": rows,
    }


def _fit_background(slices):
    """The per-ROI heterogeneity of THIS folder, measured rather than inherited.

    The generator needs a background shape, and until now the only one available
    was ``bench.MEASURED_RATE_SHAPE`` — a maximum-likelihood fit over *this
    lab's* 81 baseline windows. Handing that number to another lab's folder is
    the same category of error as handing them a flat field: a constant standing
    in for a measurement. Whether their field is flat is their empirical
    question, so the assessment answers it while it already has the recordings
    open.

    Returns ``None`` for a ``.mat`` store, which carries no analysis windows to
    take a baseline from — the export folder is the input (FOUNDATIONS §5).
    """
    if slices is None:
        return None
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    try:
        from fit_background_shape import (_this_labs_reference,
                                          fit_shape_from_slices)
    except ImportError as e:                              # noqa: BLE001
        return {"rate_shape": None, "why": f"fitter unavailable: {e}"}

    shape, n_win, n_roi = fit_shape_from_slices(slices)
    out = {"rate_shape": shape, "n_windows": n_win, "n_rois": n_roi,
           "this_lab_reference": _this_labs_reference()}
    if shape is None:
        out["why"] = (
            f"only {n_win} usable baseline windows — too few to fit a shape. "
            "The consumer must choose a background explicitly rather than "
            "inherit one")
    else:
        # A genuinely uniform field drives the shape to the fitter's ceiling,
        # which is the right answer and an unreadable one — "9998" is a bound,
        # not a measurement. Say which of the two the folder is.
        out["reads_as"] = "flat" if shape > 100 else "heterogeneous"
        shown = "flat (shape -> infinity)" if shape > 100 else f"{shape:.3f}"
        print(f"background: per-ROI heterogeneity {shown} from "
              f"{n_win} baseline windows / {n_roi} ROIs "
              f"(this lab's reference: {_this_labs_reference()})")
    return out


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    # "any": this one genuinely reads both shapes — `assess_store` dispatches on
    # whether the directory holds .mat files or an export folder.
    _dataset_arg.add(p, want="any", aliases=("--store",))
    p.add_argument("--out", type=Path, required=True)
    p.add_argument("--stream", default="fast")
    p.add_argument("--n-surrogates", type=int, default=1000)
    p.add_argument("--limit", type=int, default=None)
    p.add_argument("--assemblies", action="store_true",
                   help="also ask whether the same cells recur across events "
                        "(both nulls; see bugarach.assembly). Roughly doubles "
                        "the run.")
    p.add_argument("--assembly-surrogates", type=int, default=1000)
    a = p.parse_args(argv)

    a.out.mkdir(parents=True, exist_ok=True)
    res = assess_store(_dataset_arg.get(a, want="any"),
                       stream=a.stream, n_surrogates=a.n_surrogates,
                       limit=a.limit, assemblies=a.assemblies,
                       assembly_surrogates=a.assembly_surrogates)

    f = a.out / "assessment_real.json"
    f.write_text(json.dumps(res, indent=1, sort_keys=True))
    print(f"\nwrote {f}")
    print(f"  {res['n_slices_assessed']} slices assessed of {res['n_files']}, "
          f"{res['elapsed_sec']}s")
    print(f"  skipped: {res['skipped']}")
    print(f"  region labels seen: {res['region_labels_seen']}")
    for k, v in res["by_k"].items():
        print(f"  K={k}: participants {v['part_n_obs']['median']}, "
              f"onset SD {v['jit_obs']['median']} "
              f"(null {v['jit_null']['median']}), "
              f"events/min {v['clusters_permin']['median']}, "
              f"jit_defined {v['n_jit_defined']}/{v['n_slices']}")

    if a.assemblies:
        from bugarach.assembly import fisher
        print("\n  do the same cells recur across events?")
        for k in sorted({r["K"] for r in res["rows"]}):
            sub = [r for r in res["rows"] if r["K"] == k]
            ok = [r for r in sub if r["asm_defined"]]
            if not ok:
                print(f"  K={k}: no slice had enough clusters for a null — "
                      f"undefined, not negative")
                continue
            tally: dict[str, int] = {}
            for r in ok:
                tally[r["asm_verdict"]] = tally.get(r["asm_verdict"], 0) + 1
            # Corpus-level combination. FOUNDATIONS §9 says a pooled
            # across-group number can hide a sign change, so this is quoted as
            # what it is — pooled — and a per-group split is the caller's job
            # once the group of each slice is known here.
            fm = fisher([r["asm_p_margin_disp"] for r in ok])
            fu = fisher([r["asm_p_uniform_disp"] for r in ok])
            print(f"  K={k}: {len(ok)}/{len(sub)} slices testable · "
                  + " · ".join(f"{n} {v}" for v, n in
                               sorted(tally.items(), key=lambda kv: -kv[1])))
            # Two independence assumptions this combination makes and the folder
            # does not honour, so it is printed with them attached rather than as
            # a headline. Group: FOUNDATIONS §9. Preparation: 85 slices come from
            # 48 dates, up to three apiece, so per-slice p-values are correlated
            # and Fisher is anti-conservative. The per-slice tally above is the
            # number to quote.
            print(f"        pooled p (margin {fm:.3g}, uniform {fu:.3g}) — NOT "
                  f"group-split, and slices from one preparation are not "
                  f"independent; quote the tally, not this")
    return 0


if __name__ == "__main__":
    sys.exit(main())
