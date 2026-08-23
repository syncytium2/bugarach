#!/usr/bin/env python3
"""How strong must a cell assembly be before these recordings could show it?

    python tools/assembly_power.py --numbers-only     # the table
    python tools/assembly_power.py --out DIR          # + figure

Figure id `assembly_power`, the same on every machine.

**Why this runs before the measurement.** `docs/todo/2026-08-18-do-real-slices-
have-recurring-assemblies.md` asks whether the same cells recur across coordinated
events in the 85 baseline recordings. A negative answer is only worth publishing
if a positive one was reachable, and the folder's geometry is thin: the derived
spec (`docs/learned/generator_spec.json`, medians over all 85 slices) gives the
median slice **32 ROIs** and, at K=3, **0.35 clusters/min over a 3525 s window ~
21 clusters** of **4.5 participants**. That is ~206 co-participation observations
spread over 496 pairs — under half an observation per pair. So this script asks
the prior question: planting an assembly of known strength at exactly that
geometry, how often does the test find it?

**What is simulated is membership, not time.** The question is *who* participates
given that an event happened, so a slice here is an events x ROI boolean matrix.
Onsets, jitter, background and the detector are all irrelevant to it and are not
modelled — which also keeps this independent of any detector's operating point.

**The null preserves both margins.** Event sizes (rows) and each ROI's total
participation (columns) are held fixed by curveball swap randomisation, so the
statistic can only respond to *which* cells co-occur, never to how busy they are
or how large the events were. This is the null the todo argues for, and it is
deliberately conservative: a small assembly shows up partly as inflated column
sums, which this null absorbs. That cost is real and is part of what the curve
below measures.

**Two statistics, so a null result cannot be blamed on one bad choice.** Pair-count
dispersion (variance of the co-participation counts) and the leading eigenvalue of
the ROI correlation matrix, which is the classical assembly instrument. Power is
reported for both; the better one is the folder's best case, not the average case.

**The positive control is the point of the strength=1.0 column.** There every
event draws from the assembly, so a test that cannot fire there is broken rather
than the data being thin — the failure mode written up in
`docs/todo/2026-08-16-promiscuity-probe-cannot-fail.md`.

Baseline geometry only (FOUNDATIONS §9). No real recording is read: this script
runs on a bare clone and needs no `BUGARACH_DATA_ROOT`.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import tempfile
from pathlib import Path

import numpy as np

FIGURE_ID = "assembly_power"

#: Median slice geometry, read from the derived spec rather than transcribed —
#: `docs/todo/2026-08-14-generator-doc-numbers-are-transcribed.md` is about
#: exactly this kind of number going stale in prose.
SPEC = Path(__file__).resolve().parents[1] / "docs" / "learned" / "generator_spec.json"

ALPHA = 0.05
GROUP_N = 20          # slices per group; 85 across the groups in FOUNDATIONS §9
BITS = np.arange(64, dtype=np.uint64)


def geometry(spec_path: Path = SPEC, k: str | None = None) -> dict:
    """Median slice geometry from the spec derived over all 85 baseline slices."""
    d = json.loads(spec_path.read_text())
    kk = k or str(d["k_chosen"])
    scan = d["k_scan"][kk]
    win = float(d["generator"]["duration_sec"])
    return {
        "k": int(kk),
        "n_roi": int(d["generator"]["n_roi"]),
        "win_sec": win,
        "n_events": int(round(scan["clusters_permin"] * win / 60.0)),
        "part": float(scan["part_n_obs"]),
    }


# ---- one simulated slice ---------------------------------------------------

def _sizes(rng, n_events: int, part: float, n_roi: int) -> np.ndarray:
    """Participant counts per event, averaging `part`, never below 2 or above n_roi.

    The spec records a median participant count, not a distribution. Splitting
    the fractional part between the two neighbouring integers reproduces that
    median without inventing a spread the recordings have not been measured for.
    """
    lo = int(np.floor(part))
    frac = part - lo
    s = lo + (rng.random(n_events) < frac).astype(int)
    return np.clip(s, 2, n_roi)


def simulate_slice(rng, n_roi: int, n_events: int, part: float,
                   assembly_size: int, strength: float) -> np.ndarray:
    """An events x ROI membership matrix with a planted assembly.

    `strength` is the fraction of events recruited from the assembly; at 0.0 this
    is exactly what `simulate.py` does today (`rng.choice`, uniform, no
    replacement) and at 1.0 every event is the assembly. The assembly occupies
    ROI indices 0..assembly_size-1, which costs no generality — the statistics
    below are invariant to ROI labelling and the null shuffles membership anyway.
    """
    sizes = _sizes(rng, n_events, part, n_roi)
    M = np.zeros((n_events, n_roi), dtype=bool)
    is_asm = rng.random(n_events) < strength
    for e in range(n_events):
        k = int(sizes[e])
        if is_asm[e] and assembly_size >= 2:
            take = min(k, assembly_size)
            pick = rng.choice(assembly_size, size=take, replace=False)
            if take < k:
                rest = rng.choice(np.arange(assembly_size, n_roi),
                                  size=k - take, replace=False)
                pick = np.concatenate([pick, rest])
        else:
            pick = rng.choice(n_roi, size=k, replace=False)
        M[e, pick] = True
    return M


# ---- the statistics and both nulls come from the package -------------------
#
# Deliberately NOT re-implemented here. The whole value of this power curve is
# that it validates the instrument the recordings will actually be measured with; a
# second copy would let the two drift and quietly invalidate the curve.
from bugarach.assembly import (          # noqa: E402
    stat_dispersion, stat_eigen, pvalues_margin, pvalues_uniform,
    _to_masks, _from_masks, _trade,      # selftest reaches in; see tests
)

pvalues = pvalues_margin                 # the name this script used before


from bugarach.assembly import fisher  # noqa: E402,F811


# ---- the sweep -------------------------------------------------------------

def sweep(geo: dict, sizes, strengths, n_slices: int, n_surr: int,
          seed: int = 7) -> dict:
    """Per-slice p-values for every (assembly size, strength) cell of the grid."""
    rng = np.random.RandomState(seed)
    out = {}
    for A in sizes:
        for s in strengths:
            pd_, pe_ = [], []
            for _ in range(n_slices):
                M = simulate_slice(rng, geo["n_roi"], geo["n_events"],
                                   geo["part"], A, s)
                a, b = pvalues(rng, M, n_surr)
                pd_.append(a)
                pe_.append(b)
            out[(A, s)] = (np.array(pd_), np.array(pe_))
    return out


def powers(cell: tuple[np.ndarray, np.ndarray], group_n: int = GROUP_N) -> dict:
    """Rejection rate per slice, and for the group-level combination."""
    pd_, pe_ = cell
    n_groups = len(pd_) // group_n
    def grouped(p):
        if n_groups == 0:
            return float("nan")
        g = p[: n_groups * group_n].reshape(n_groups, group_n)
        return float(np.mean([fisher(row) < ALPHA for row in g]))
    return {
        "slice_disp": float(np.mean(pd_ < ALPHA)),
        "slice_eig": float(np.mean(pe_ < ALPHA)),
        "group_disp": grouped(pd_),
        "group_eig": grouped(pe_),
        "n_groups": n_groups,
    }


# ---- the sweep under BOTH nulls --------------------------------------------
#
# Why both: `bugarach.assembly` explains it at length. Short version — the
# double-margin null goes blind at full assembly strength and the uniform null
# answers a broader question, so the curve has to show each one's failure mode.

def sweep2(geo: dict, sizes, strengths, n_slices: int, n_surr: int,
           seed: int = 7) -> dict:
    """The grid under both nulls, on the same simulated slices."""
    rng = np.random.RandomState(seed)
    out = {}
    for A in sizes:
        for s in strengths:
            acc = {k: [] for k in ("md", "me", "ud", "ue")}
            for _ in range(n_slices):
                M = simulate_slice(rng, geo["n_roi"], geo["n_events"],
                                   geo["part"], A, s)
                a, b = pvalues(rng, M, n_surr)
                c, d = pvalues_uniform(rng, M, n_surr)
                acc["md"].append(a); acc["me"].append(b)
                acc["ud"].append(c); acc["ue"].append(d)
            out[(A, s)] = {k: np.array(v) for k, v in acc.items()}
    return out


def powers2(cell: dict, group_n: int = GROUP_N) -> dict:
    n = len(cell["md"]) // group_n
    def grouped(p):
        if n == 0:
            return float("nan")
        g = p[: n * group_n].reshape(n, group_n)
        return float(np.mean([fisher(row) < ALPHA for row in g]))
    out = {}
    for k, v in cell.items():
        out[f"slice_{k}"] = float(np.mean(v < ALPHA))
        out[f"group_{k}"] = grouped(v)
    return out


# ---- the decision rule recordings are ACTUALLY scored by -------------------
#
# Everything above reports power for ONE statistic under ONE null at `alpha`,
# and combines a group of 20 by Fisher. **No recording was ever scored that
# way.** `tools/assess_archive.py --assemblies` builds an `AssemblyResult` per
# recording and reads `verdict()`, which Bonferroni-corrects across the two
# statistics *within* each null and then reads the two nulls together. That is a
# different, and strictly more conservative, test: alpha/2 twice over.
#
# A negative result is only a result if the test that produced it could have
# failed, so the power curve has to be computed under the rule that produced it.
# That is what this section adds, and it is step 1 of the handoff that closes
# the assembly question.

from bugarach.assembly import AssemblyResult  # noqa: E402


#: The four verdict words `AssemblyResult.verdict()` can return for a defined
#: recording. "no-assembly" is the only one that is a miss when something was
#: planted; the other three all mean the instrument fired.
VERDICTS = ("structure-beyond-rate", "uniform-only", "margin-only", "no-assembly")


def verdicts_for(cell: dict, geo: dict) -> list[str]:
    """One verdict per simulated slice, from the package's own decision rule.

    Deliberately constructs the real `AssemblyResult` rather than re-deriving
    the comparison here — same reason the statistics and nulls are imported
    rather than copied. If `verdict()` changes, this curve changes with it.
    """
    out = []
    for md, me, ud, ue in zip(cell["md"], cell["me"], cell["ud"], cell["ue"]):
        r = AssemblyResult(
            min_rois=int(geo.get("k", 3)), n_events=int(geo["n_events"]),
            n_roi=int(geo["n_roi"]), defined=True,
            p_margin_disp=float(md), p_margin_eig=float(me),
            p_uniform_disp=float(ud), p_uniform_eig=float(ue),
        )
        out.append(r.verdict(ALPHA))
    return out


def powers_verdict(cell: dict, geo: dict) -> dict:
    """Per-recording rejection rate under `verdict()`, plus the word breakdown.

    `power` is the fraction of simulated recordings the instrument called
    something other than `no-assembly` — the quantity a reader needs to know
    before believing a `no-assembly` tally from the real recordings. The breakdown
    is reported alongside because *which* word it fires with is itself
    interpretable: at high assembly strength the double-margin null goes blind
    and the verdict degrades to `uniform-only`, which is the documented failure
    mode rather than a bug.
    """
    words = verdicts_for(cell, geo)
    n = len(words)
    counts = {w: sum(1 for x in words if x == w) for w in VERDICTS}
    return {
        "verdict_power": (n - counts["no-assembly"]) / n if n else float("nan"),
        "verdict_both": counts["structure-beyond-rate"] / n if n else float("nan"),
        **{f"n_{w}": counts[w] for w in VERDICTS},
    }


# ---- the folder's own geometry, not the median slice ------------------------

def folder_geometry(path: Path, k: int = 3, stream: str | None = None) -> list[dict]:
    """Per-recording geometry read from an `assess_archive.py` assessment.

    The median slice is enough to *size* the test and is what the tables above
    use. It is not enough to report a negative on: a recording well below the
    median may be individually unpowered, and pooling it with the rest would let
    "we could not look" pass as "we looked and found nothing" — the distinction
    `assess_assemblies` refuses to blur by returning `undefined`.

    Only rows the assembly test could actually define are returned, because an
    undefined recording contributes no verdict and so has no power to report.
    """
    d = json.loads(Path(path).read_text())
    rows = d["rows"] if isinstance(d, dict) and "rows" in d else d
    out = []
    for r in rows:
        if int(r.get("K", -1)) != int(k):
            continue
        if stream and r.get("stream") != stream:
            continue
        if not r.get("asm_defined", False):
            continue
        ne = int(r.get("asm_n_events", 0))
        part = float(r.get("part_n_obs", float("nan")))
        nr = int(r.get("n_roi", 0))
        if ne < 2 or nr < 2 or not np.isfinite(part):
            continue
        out.append({"k": int(k), "n_roi": nr, "n_events": ne, "part": part,
                    "slice_id": r.get("slice_id", ""), "stream": r.get("stream", "")})
    return out


def sweep_folder(geos: list[dict], sizes, strengths, n_surr: int,
                 seed: int = 7) -> dict:
    """The grid run at each real recording's OWN geometry, one slice each.

    So `verdict_power` below is the fraction of *this folder's actual
    recordings* at which an assembly of that size and strength would have been
    found — not the fraction of hypothetical median slices.
    """
    rng = np.random.RandomState(seed)
    out = {}
    for A in sizes:
        for s in strengths:
            acc = {kk: [] for kk in ("md", "me", "ud", "ue")}
            per_slice = []
            n_too_small = 0
            for g in geos:
                # An assembly cannot be larger than the recording it lives in.
                # Skip rather than clamp: clamping would silently relabel a
                # 16-cell assembly as a 14-cell one and report its power under
                # the wrong heading. The count is carried out so the denominator
                # is visible — this is exactly the "no silent caps" rule.
                if g["n_roi"] < A:
                    n_too_small += 1
                    continue
                M = simulate_slice(rng, g["n_roi"], g["n_events"], g["part"], A, s)
                a, b = pvalues(rng, M, n_surr)
                c, d = pvalues_uniform(rng, M, n_surr)
                acc["md"].append(a); acc["me"].append(b)
                acc["ud"].append(c); acc["ue"].append(d)
                per_slice.append(g)
            out[(A, s)] = ({kk: np.array(v) for kk, v in acc.items()},
                           per_slice, n_too_small)
    return out


def powers_verdict_folder(cell) -> dict:
    """`powers_verdict` where every simulated recording has its own geometry."""
    arrs, per_slice, n_too_small = cell
    words = []
    for i, g in enumerate(per_slice):
        one = {kk: arrs[kk][i:i + 1] for kk in ("md", "me", "ud", "ue")}
        words.extend(verdicts_for(one, g))
    n = len(words)
    counts = {w: sum(1 for x in words if x == w) for w in VERDICTS}
    return {
        "verdict_power": (n - counts["no-assembly"]) / n if n else float("nan"),
        "verdict_both": counts["structure-beyond-rate"] / n if n else float("nan"),
        "n_slices": n,
        "n_too_small_for_assembly": n_too_small,
        **{f"n_{w}": counts[w] for w in VERDICTS},
    }


# ---- figure ----------------------------------------------------------------

#: One colour per assembly size, dark to light as the assembly gets more diffuse.
SIZE_COLOURS = ["#111111", "#1f6fb4", "#3fa34d", "#d98324", "#b03a48"]
ALPHA_LINE = "#9a9a9a"


def build(rows, geo, sizes, strengths, width: int):
    import holoviews as hv

    def panel(key_slice, key_group, ylabel):
        items = [hv.HLine(ALPHA).opts(color=ALPHA_LINE, line_width=1.5,
                                      line_dash="dotted")]
        for A, colour in zip(sizes, SIZE_COLOURS):
            r = [x for x in rows if x["A"] == A]
            r.sort(key=lambda x: x["strength"])
            xs = [x["strength"] for x in r]
            items.append(hv.Curve((xs, [x[key_group] for x in r])).opts(
                color=colour, line_width=3))
            items.append(hv.Curve((xs, [x[key_slice] for x in r])).opts(
                color=colour, line_width=1.6, line_dash="dashed", alpha=0.85))
        return hv.Overlay(items).opts(
            width=width, height=430, ylim=(-0.03, 1.05),
            xlim=(-0.03, 1.03), xlabel="fraction of events drawn from the assembly",
            ylabel=ylabel, title="", show_legend=False,
            fontsize={"labels": "11pt", "ticks": "10pt"})

    left = panel("slice_md", "group_md", "power · both margins fixed")
    right = panel("slice_ud", "group_ud", "power · uniform participation")

    swatches = " · ".join(
        f'<span style="color:{c}"><b>{A}</b></span>'
        for A, c in zip(sizes, SIZE_COLOURS))
    header = (
        '<div style="font:13px/1.6 system-ui,sans-serif;color:#222;'
        'max-width:1240px">'
        '<b>How strong an assembly would have to be before these recordings could '
        'see it</b><br>'
        f'Median baseline slice from the derived spec: <b>{geo["n_roi"]} ROIs</b>, '
        f'<b>{geo["n_events"]} clusters</b> at K={geo["k"]} over '
        f'{geo["win_sec"]/60:.0f} min, <b>{geo["part"]} participants</b> each — '
        f'{geo["n_roi"]*(geo["n_roi"]-1)//2} pairs sharing about '
        f'{geo["n_events"]*geo["part"]*(geo["part"]-1)/2:.0f} co-participation '
        'observations. Assembly size (cells): ' + swatches + '. '
        '<b>Solid</b> = the group-level test over 20 slices · '
        '<b>dashed</b> = one slice alone · '
        f'<span style="color:{ALPHA_LINE}">dotted</span> = alpha {ALPHA}.<br>'
        '<b>Left, both margins fixed</b> — the conservative null, and it '
        '<b>collapses to chance at full strength</b>: when every event is the '
        'assembly the non-members never fire, so the whole signal sits in the '
        'column sums this null holds fixed and there is nothing left to shuffle. '
        'Power is not monotonic in the thing being measured, which is why this '
        'null cannot be run alone.<br>'
        '<b>Right, uniform participation</b> — the generator\'s own assumption. '
        'It rises monotonically and passes the full-strength control, but it '
        'answers a broader question: a few unusually busy cells move it too.<br>'
        'Membership is simulated directly — no onsets, no detector, no operating '
        'point, and no real recording is read.</div>')
    return (left + right).cols(2).opts(shared_axes=False, toolbar=None), header


def _render_png(html_path: Path, png_path: Path, *, wait_ms: int = 2500,
                width: int = 1500, height: int = 660) -> bool:
    try:
        from playwright.sync_api import sync_playwright
    except Exception:
        return False
    try:
        with sync_playwright() as pw:
            b = pw.chromium.launch()
            pg = b.new_page(viewport={"width": width, "height": height})
            pg.goto(html_path.as_uri())
            pg.wait_for_timeout(wait_ms)
            with tempfile.TemporaryDirectory() as td:
                tmp = Path(td) / "shot.png"
                pg.screenshot(path=str(tmp), full_page=True)
                b.close()
                os.replace(tmp, png_path)
        return True
    except Exception as exc:
        print(f"(PNG render failed: {type(exc).__name__}: {exc})", file=sys.stderr)
        return False


def _payload(args, geo, rows, verdict_rows) -> dict:
    """Everything a downstream figure or report needs, in one place.

    Shared by the full run and by ``--verdict-only`` so the two cannot drift on
    what a result file contains — a figure built from one and a claim quoted
    from the other must be the same numbers.
    """
    return {"geometry": geo, "alpha": ALPHA, "group_n": GROUP_N,
            "slices": args.slices, "surrogates": args.surrogates,
            "seed": args.seed, "rows": rows,
            "verdict_rule": "AssemblyResult.verdict",
            "verdict_geometry_from": args.geometry_from,
            "verdict_stream": args.stream,
            "verdict_rows": verdict_rows}


def _write_json(args, geo, rows, verdict_rows) -> int:
    """Write the result file only — no figure. The ``--verdict-only`` path."""
    from bugarach.paths import darkroom, unresolved_message
    dest = Path(args.out) if args.out else darkroom()
    if dest is None:
        print(unresolved_message(), file=sys.stderr)
        return 1
    dest.mkdir(parents=True, exist_ok=True)
    out = dest / f"{FIGURE_ID}.json"
    out.write_text(json.dumps(_payload(args, geo, rows, verdict_rows), indent=1))
    print(f"wrote {out}")
    return 0


def main(argv=None):
    p = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--sizes", type=int, nargs="+", default=[4, 6, 8, 12, 16],
                   help="assembly sizes, in cells")
    p.add_argument("--strengths", type=float, nargs="+",
                   default=[0.0, 0.05, 0.10, 0.15, 0.25, 0.50, 0.75, 1.0])
    p.add_argument("--slices", type=int, default=200,
                   help="simulated slices per grid cell")
    p.add_argument("--surrogates", type=int, default=200)
    p.add_argument("--k", default=None, help="K to take the geometry at (default: k_chosen)")
    p.add_argument("--seed", type=int, default=7)
    p.add_argument("--width", type=int, default=620)
    p.add_argument("--out", default=None,
                   help="destination directory; default $BUGARACH_DARKROOM")
    p.add_argument("--numbers-only", action="store_true")
    p.add_argument("--geometry-from", default=None, metavar="ASSESSMENT_JSON",
                   help="an assess_archive.py assessment_real.json; run the grid at "
                        "each real recording's OWN geometry instead of the median "
                        "slice, and report power under AssemblyResult.verdict()")
    p.add_argument("--stream", default=None,
                   help="with --geometry-from: restrict to this stream (fast|slow)")
    p.add_argument("--verdict-only", action="store_true",
                   help="with --geometry-from: skip the median-slice grid and "
                        "write only the folder-geometry verdict curve")
    p.add_argument("--no-png", dest="png", action="store_false", default=True)
    args = p.parse_args(argv)

    geo = geometry(k=args.k)

    # ---- step 1 of the assembly handoff: the folder's own geometry, scored by
    # the rule the folder is actually scored by. Reported and returned before
    # the median-slice grid below, because this is the one a negative rests on.
    verdict_rows = None
    if args.geometry_from:
        geos = folder_geometry(Path(args.geometry_from), k=int(geo["k"]),
                               stream=args.stream)
        if not geos:
            print(f"no testable recordings at K={geo['k']} in "
                  f"{args.geometry_from}", file=sys.stderr)
            return 1
        cres = sweep_folder(geos, args.sizes, args.strengths, args.surrogates,
                            seed=args.seed)
        verdict_rows = [dict(A=A, strength=s_, **powers_verdict_folder(cres[(A, s_)]))
                        for A in args.sizes for s_ in args.strengths]
        nr = sorted(g["n_roi"] for g in geos)
        ne = sorted(g["n_events"] for g in geos)
        mid = len(geos) // 2
        print(f"folder geometry: {len(geos)} testable recordings"
              + (f" (stream {args.stream})" if args.stream else "")
              + f" at K={geo['k']}")
        print(f"  ROIs     median {nr[mid]}  range {nr[0]}-{nr[-1]}")
        print(f"  clusters median {ne[mid]}  range {ne[0]}-{ne[-1]}")
        print(f"  decision rule: AssemblyResult.verdict(alpha={ALPHA}) "
              f"— Bonferroni over 2 statistics within each null, both nulls read "
              f"together, ONE decision per recording\n")
        print(f"{'A':>3} {'str':>5} | {'fires':>6} {'both':>6} | "
              f"{'sbr':>4} {'uni':>4} {'mar':>4} {'none':>5} | {'n':>3} {'skip':>4}")
        for r in verdict_rows:
            print(f"{r['A']:>3} {r['strength']:>5.2f} | "
                  f"{r['verdict_power']:>6.2f} {r['verdict_both']:>6.2f} | "
                  f"{r['n_structure-beyond-rate']:>4} {r['n_uniform-only']:>4} "
                  f"{r['n_margin-only']:>4} {r['n_no-assembly']:>5} | "
                  f"{r['n_slices']:>3} {r['n_too_small_for_assembly']:>4}")
        print("  skip = recordings with fewer ROIs than the assembly size; "
              "they cannot host it and are excluded from that row's denominator")
        print()

    if args.verdict_only:
        if verdict_rows is None:
            print("--verdict-only requires --geometry-from", file=sys.stderr)
            return 1
        rows = []
    else:
        res = sweep2(geo, args.sizes, args.strengths, args.slices, args.surrogates,
                     seed=args.seed)
        rows = [dict(A=A, strength=s, **powers2(res[(A, s)]))
                for A in args.sizes for s in args.strengths]

    if args.verdict_only:
        return _write_json(args, geo, rows, verdict_rows)

    print(f"geometry (median of 85 baseline slices, K={geo['k']}): "
          f"{geo['n_roi']} ROIs, {geo['n_events']} clusters, "
          f"{geo['part']} participants")
    print(f"{args.slices} slices x {args.surrogates} surrogates per cell, "
          f"alpha {ALPHA}, groups of {GROUP_N}\n")
    print("                double-margin null        uniform null")
    print(f"{'A':>3} {'str':>5} | {'slice':>6} {'grp':>6} | {'slice':>6} {'grp':>6}")
    for r in rows:
        print(f"{r['A']:>3} {r['strength']:>5.2f} | {r['slice_md']:>6.2f} "
              f"{r['group_md']:>6.2f} | {r['slice_ud']:>6.2f} {r['group_ud']:>6.2f}")
    if args.numbers_only:
        return 0

    from bugarach.paths import darkroom, unresolved_message
    dest = Path(args.out) if args.out else darkroom()
    if dest is None:
        print(unresolved_message(), file=sys.stderr)
        return 1
    dest.mkdir(parents=True, exist_ok=True)

    import holoviews as hv
    import panel as pn
    hv.extension("bokeh")
    layout, header = build(rows, geo, args.sizes, args.strengths, args.width)
    html = dest / f"{FIGURE_ID}.html"
    pn.panel(pn.Column(pn.pane.HTML(header), pn.pane.HoloViews(layout))).save(str(html))
    (dest / f"{FIGURE_ID}.json").write_text(
        json.dumps(_payload(args, geo, rows, verdict_rows), indent=1))
    print(f"\nwrote {html}")
    if args.png:
        shot = dest / f"{FIGURE_ID}.png"
        if _render_png(html, shot):
            print(f"wrote {shot}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
