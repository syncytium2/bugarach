#!/usr/bin/env python3
"""Do the same cells recur across coordinated events in the real recordings?

    python tools/make_assembly_figure.py --fast DIR --slow DIR      # -> $BUGARACH_DARKROOM
    python tools/make_assembly_figure.py --fast DIR --slow DIR --numbers-only

Figure id `assembly_answer`, the same on every machine.

Takes the two ``assess_archive.py --assemblies`` runs (one per stream) and draws
the answer beside its control. The control is not decoration: the generator draws
every event's participants with ``rng.choice``, so recordings it produced contain
coordinated events and **no** recurring group. Plotted on the same axes, they show
where "no assembly" lands for this instrument at this corpus's geometry — which is
the only thing that makes the real cloud's position mean anything.

**Two nulls per slice, and the axes are the two of them.** Horizontal: uniform
participation, which answers to any departure from ``rng.choice`` including plain
rate heterogeneity. Vertical: both margins fixed, which can only answer to *which*
cells co-occur. A slice in the lower-left rejects both — co-participation structure
beyond what per-cell rates explain. Bottom-right rejects only the broader null and
is not assembly evidence on its own. Thresholds are drawn at alpha/2 because each
null is read through two statistics and the smaller of two p-values is a third
test; see ``bugarach.assembly``.

**Baseline windows only** (FOUNDATIONS §9), and the combination this figure's
caption quotes is **pooled across groups** — slice group does not travel with the
store, so a per-group split is not available here and a pooled number is not
admissible on its own.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import tempfile
from pathlib import Path

import numpy as np

FIGURE_ID = "assembly_answer"
ALPHA = 0.05
FLOOR = 5e-4          # p-value floor for the log axes; 1/(1+1000) surrogates
K_SHOWN = 3

REAL_FAST = "#111111"
REAL_SLOW = "#1f6fb4"
CONTROL = "#c46a1e"
GUIDE = "#9a9a9a"


def _rows(path: Path, k: int) -> list[dict]:
    d = json.loads((path / "assessment_real.json").read_text())
    return [r for r in d["rows"]
            if r["K"] == k and r.get("asm_defined")]


def controls(n: int, geometry: dict, *, seed0: int = 500) -> list[dict]:
    """Generated recordings at the real corpus's geometry: no assembly, by
    construction. Assessed and tested through exactly the same code path."""
    from bugarach.assess import assess_coactivity
    from bugarach.assembly import assess_assemblies
    from bugarach.simulate import simulate_coordination

    out = []
    for i in range(n):
        s, _ = simulate_coordination(
            n_roi=geometry["n_roi"], duration_sec=geometry["win_sec"],
            bg_rate_hz=geometry["bg_rate_hz"],
            participation=(geometry["participation"],),
            n_per_level=(geometry["n_events"],),
            jitter_sec=geometry["jitter_sec"],
            # Real cluster centres sit as close as 3 s apart (median gap ~20 s),
            # and a control has to be able to hold as many events as the data it
            # stands beside — 30 s would not fit them in the window.
            min_sep_sec=5.0,
            spacing="uniform", seed=seed0 + i)
        # The assessor's own surrogate count is irrelevant here: membership comes
        # from the observed clusters only, so a small ensemble saves time without
        # touching anything this figure reads.
        a = [x for x in assess_coactivity(s, stream="events", n_surrogates=50)
             if x.min_rois == K_SHOWN]
        if not a:
            continue
        q = assess_assemblies(a[0], n_surrogates=1000)
        if q.defined:
            out.append(dict(asm_p_margin_disp=q.p_margin_disp,
                            asm_p_margin_eig=q.p_margin_eig,
                            asm_p_uniform_disp=q.p_uniform_disp,
                            asm_p_uniform_eig=q.p_uniform_eig,
                            asm_verdict=q.verdict()))
    return out


def _xy(rows):
    """Each slice at (uniform p, margin p), each taken as the smaller of its two
    statistics — the quantity the verdict actually thresholds."""
    x = np.array([min(r["asm_p_uniform_disp"], r["asm_p_uniform_eig"]) for r in rows])
    y = np.array([min(r["asm_p_margin_disp"], r["asm_p_margin_eig"]) for r in rows])
    return np.maximum(x, FLOOR), np.maximum(y, FLOOR)


def tally(rows) -> dict:
    t: dict[str, int] = {}
    for r in rows:
        t[r["asm_verdict"]] = t.get(r["asm_verdict"], 0) + 1
    return t


def build(fast, slow, ctrl, per_k, width: int):
    import holoviews as hv

    a2 = ALPHA / 2.0
    items = [
        hv.VLine(a2).opts(color=GUIDE, line_width=1.5, line_dash="dotted"),
        hv.HLine(a2).opts(color=GUIDE, line_width=1.5, line_dash="dotted"),
    ]
    for rows, colour, marker, size in ((ctrl, CONTROL, "diamond", 9),
                                       (fast, REAL_FAST, "circle", 9),
                                       (slow, REAL_SLOW, "square", 9)):
        if not rows:
            continue
        x, y = _xy(rows)
        items.append(hv.Scatter((x, y)).opts(
            color=colour, size=size, marker=marker, alpha=0.75,
            line_color="white", line_width=0.8))
    left = hv.Overlay(items).opts(
        width=width, height=470, logx=True, logy=True,
        xlim=(FLOOR * 0.7, 1.4), ylim=(FLOOR * 0.7, 1.4),
        xlabel="p · uniform participation (any departure)",
        ylabel="p · both margins fixed (beyond per-cell rate)",
        title="", show_legend=False,
        fontsize={"labels": "11pt", "ticks": "10pt"})

    ks = sorted(per_k)
    order = ["structure-beyond-rate", "uniform-only", "margin-only", "no-assembly"]
    cols = {"structure-beyond-rate": "#1a7f4b", "uniform-only": "#d98324",
            "margin-only": "#8a6fb4", "no-assembly": "#b9b9b9"}
    # Stacking is a Bars option over a second key dimension, not an Overlay of
    # separate Bars — one element, two kdims.
    recs = [(f"K{k} {st}", v, per_k[k][st].get(v, 0))
            for k in ks for st in ("fast", "slow") for v in order]
    right = hv.Bars(recs, kdims=["cell", "verdict"], vdims=["slices"]).opts(
        width=int(width * 0.95), height=470, xrotation=45,
        xlabel="", ylabel="slices with a testable answer",
        title="", stacked=True, show_legend=False,
        cmap=[cols[v] for v in order], line_color="white", line_width=1,
        fontsize={"labels": "11pt", "ticks": "9pt"})

    tf, ts, tc = tally(fast), tally(slow), tally(ctrl)
    def frac(t):
        n = sum(t.values())
        return f"{t.get('structure-beyond-rate', 0)}/{n}" if n else "0/0"
    header = (
        '<div style="font:13px/1.6 system-ui,sans-serif;color:#222;'
        'max-width:1240px">'
        '<b>The same cells do recur — in both streams, at every coactivity '
        'floor</b><br>'
        f'<b>Left</b> — one point per recording at K={K_SHOWN}, its two nulls as '
        f'the two axes. <span style="color:{REAL_FAST}"><b>circles</b></span> = '
        f'real FAST · <span style="color:{REAL_SLOW}"><b>squares</b></span> = '
        f'real SLOW · <span style="color:{CONTROL}"><b>diamonds</b></span> = '
        'generated recordings, whose participants are drawn at random by '
        'construction. Dotted lines are alpha/2, the threshold each null is '
        'actually read at. <b>Lower-left rejects both nulls</b>: co-participation '
        'beyond what per-cell rates explain. Bottom-right rejects only the broader '
        'null and is not assembly evidence by itself — this corpus has strongly '
        'heterogeneous ROI rates, which is exactly what lands a slice there.<br>'
        f'<b>Right</b> — every testable slice by verdict. FAST {frac(tf)} and '
        f'SLOW {frac(ts)} reject both nulls at K={K_SHOWN}; the generated control '
        f'gives {frac(tc)}. Slices with fewer than four clusters have no '
        'permutation null and are counted nowhere here — <b>undefined, never '
        'negative</b>.<br>'
        'Baseline windows only. The pooled combination is <b>pooled across '
        'groups</b> and not admissible alone: slice group does not travel with '
        'the store (FOUNDATIONS §9).</div>')
    return (left + right).cols(2).opts(shared_axes=False, toolbar=None), header


def _render_png(html_path: Path, png_path: Path, *, wait_ms: int = 2500,
                width: int = 1500, height: int = 700) -> bool:
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
    p.add_argument("--fast", type=Path, required=True,
                   help="output dir of assess_archive --stream fast --assemblies")
    p.add_argument("--slow", type=Path, required=True)
    p.add_argument("--controls", type=int, default=40,
                   help="generated recordings to place beside the real ones")
    p.add_argument("--width", type=int, default=620)
    p.add_argument("--out", default=None)
    p.add_argument("--numbers-only", action="store_true")
    p.add_argument("--no-png", dest="png", action="store_false", default=True)
    args = p.parse_args(argv)

    ks = (3, 4, 6, 8)
    per_k = {k: {"fast": tally(_rows(args.fast, k)),
                 "slow": tally(_rows(args.slow, k))} for k in ks}
    fast, slow = _rows(args.fast, K_SHOWN), _rows(args.slow, K_SHOWN)

    # Control geometry: read from the real FAST run, so the comparison is at this
    # corpus's own numbers rather than remembered ones.
    d = json.loads((args.fast / "assessment_real.json").read_text())
    bk = d["by_k"][str(K_SHOWN)]
    win = float(np.median([r["window_sec"] for r in d["rows"]
                           if r["K"] == K_SHOWN]))
    # Cluster count is matched to the slices that actually GOT an answer, not to
    # the corpus median. `clusters_permin` is a median over all 85 slices and most
    # of the way down it are the ones with too few clusters to test at all, so
    # using it would build a control three times thinner than the data it is meant
    # to stand beside. A control must be at least as informative as the real thing
    # or "the real slices reject and the control does not" says nothing.
    testable = [r["asm_n_events"] for r in d["rows"]
                if r["K"] == K_SHOWN and r.get("asm_defined")]
    n_events = max(4, int(round(float(np.median(testable))))) if testable else 8
    geo = dict(n_roi=int(round(d["n_roi"]["median"])), win_sec=win,
               n_events=n_events,
               participation=bk["part_n_obs"]["median"] / max(d["n_roi"]["median"], 1),
               jitter_sec=bk["jit_obs"]["median"],
               bg_rate_hz=bk["roi_rate_med"]["median"] or 0.004)
    print(f"control geometry from the real run: {geo}")
    ctrl = controls(args.controls, geo)

    for name, rows in (("real FAST", fast), ("real SLOW", slow),
                       ("generated control", ctrl)):
        t = tally(rows)
        n = sum(t.values())
        print(f"{name:>18}: {n:>3} testable · " + " · ".join(
            f"{c} {v}" for v, c in sorted(t.items(), key=lambda kv: -kv[1])))
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
    layout, header = build(fast, slow, ctrl, per_k, args.width)
    html = dest / f"{FIGURE_ID}.html"
    pn.panel(pn.Column(pn.pane.HTML(header), pn.pane.HoloViews(layout))).save(str(html))
    (dest / f"{FIGURE_ID}.json").write_text(json.dumps(
        {"k_shown": K_SHOWN, "alpha": ALPHA, "control_geometry": geo,
         "per_k": {str(k): v for k, v in per_k.items()},
         "n_controls": len(ctrl)}, indent=1))
    print(f"\nwrote {html}")
    if args.png and _render_png(html, dest / f"{FIGURE_ID}.png"):
        print(f"wrote {dest / f'{FIGURE_ID}.png'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
