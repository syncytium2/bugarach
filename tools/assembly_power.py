#!/usr/bin/env python3
"""How strong must a cell assembly be before this corpus could see it?

    python tools/assembly_power.py --numbers-only     # the table
    python tools/assembly_power.py --out DIR          # + figure

Figure id `assembly_power`, the same on every machine.

**Why this runs before the measurement.** `docs/todo/2026-08-18-do-real-slices-
have-recurring-assemblies.md` asks whether the same cells recur across coordinated
events in the 85 baseline recordings. A negative answer is only worth publishing
if a positive one was reachable, and the corpus geometry is thin: the derived
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
reported for both; the better one is the corpus's best case, not the average case.

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
    median without inventing a spread the corpus has not been measured for.
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
# that it validates the instrument the corpus will actually be measured with; a
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
        '<b>How strong an assembly would have to be before this corpus could '
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
    p.add_argument("--no-png", dest="png", action="store_false", default=True)
    args = p.parse_args(argv)

    geo = geometry(k=args.k)
    res = sweep2(geo, args.sizes, args.strengths, args.slices, args.surrogates,
                 seed=args.seed)
    rows = [dict(A=A, strength=s, **powers2(res[(A, s)]))
            for A in args.sizes for s in args.strengths]

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
        json.dumps({"geometry": geo, "alpha": ALPHA, "group_n": GROUP_N,
                    "slices": args.slices, "surrogates": args.surrogates,
                    "seed": args.seed, "rows": rows}, indent=1))
    print(f"\nwrote {html}")
    if args.png:
        shot = dest / f"{FIGURE_ID}.png"
        if _render_png(html, shot):
            print(f"wrote {shot}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
