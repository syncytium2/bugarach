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

BASELINE_TOKENS = ("baseline", "base", "pre", "control", "acsf")


def _is_baseline(region) -> bool:
    """A region counts as baseline if its own name says so.

    Deliberately does not fall back to "the first region is baseline" — the
    export contract calls that out as a thing producers must not do, and this
    project's own MATLAB exporter has done it. A region with no name is skipped
    and counted, not guessed at.
    """
    name = (getattr(region, "name", None) or "").strip().lower()
    return bool(name) and any(name.startswith(t) for t in BASELINE_TOKENS)


def assess_store(store: Path, *, stream: str | None, n_surrogates: int,
                 limit: int | None = None, assemblies: bool = False,
                 assembly_surrogates: int = 1000) -> dict:
    from bugarach.assess import DEFAULT_MIN_ROIS, assess_coactivity
    from bugarach.store import load_slice
    if assemblies:
        from bugarach.assembly import assess_assemblies

    files = sorted(store.glob("*.mat"))
    if limit:
        files = files[:limit]
    if not files:
        raise SystemExit(f"no .mat slices under {store}")

    rows: list[dict] = []
    skipped = {"no_baseline_region": 0, "too_short": 0, "load_error": 0,
               "no_stream": 0}
    seen_regions: dict[str, int] = {}
    t0 = time.time()

    for i, f in enumerate(files):
        try:
            s = load_slice(f)
        except Exception as e:                       # noqa: BLE001
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

        names = list(s.streams)
        want = stream if stream in names else (stream and None) or names[0]
        if want is None:
            skipped["no_stream"] += 1
            continue

        try:
            res = assess_coactivity(s, stream=want,
                                    window=(r.start_sec, r.end_sec),
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
            rows.append(dict(
                **asm,
                slice_id=s.slice_id, stream=want, n_roi=int(n_roi),
                region=(getattr(r, "name", None) or ""),
                window_sec=float(r.end_sec - r.start_sec),
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
        "rows": rows,
    }


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--store", type=Path, required=True,
                   help="directory of *.mat event stores")
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
    res = assess_store(a.store, stream=a.stream, n_surrogates=a.n_surrogates,
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
            # Two independence assumptions this combination makes and the corpus
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
