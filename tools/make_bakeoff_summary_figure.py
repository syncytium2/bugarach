#!/usr/bin/env python3
"""The bake-off as intervals, by family, with the columns F1 cannot see.

    python tools/make_bakeoff_summary_figure.py --bakeoff RUN/bakeoff.json [--out DIR] [--also DIR]

Two pages. `bakeoff_intervals`: four lettered panels, one row per detector, grouped
by family (hand-written, then learned) and NOT sorted by score — a bar chart sorted
by F1 says "ranking" before its label is read, and at four folds this table is
intervals, not a ranking (murderboard 2026-09-07, roles 4, 8 and 10 on
`make_bakeoff_figures.py`'s output).

  A · F1 on the held-out fold: the fold range as a line, the mean as a dot, and the
      ceiling a detector reaches by finding every planted event and firing on every
      distractor.
  B · distractor hits per fold, of the correlated bursts planted — the scorer counts
      each as a false alarm.
  C · firings into the promiscuity probe, PER MINUTE of probe, which is the unit the
      bench gates on (`bench.MAX_PROBE_PER_MIN`); each hand-written detector's gate
      is drawn as a tick, so a calibrated point the gate would refuse is visible.
  D · recall against precision, with the iso-F1 curve at the ceiling and the
      precision a detector has when it fires on every distractor.

`bakeoff_knobs`: one row per hand-written detector, its search grid as ticks, the
knob each fold chose as filled dots and the shipped operating point as an open dot,
grid ends shaded — how far the calibrated instrument sits from the shipped one, and
whether the search ended on an edge.

Distractor and probe conversions come from the file's own spec through
`performance.fold_scores_from_bakeoff`, never from a constant. Every colour and
glyph is keyed in the header, in its colour, at body size.
"""
from __future__ import annotations

import argparse
import json
import math
from collections import Counter
import os
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from bugarach import paths  # noqa: E402
from bugarach.bench import MAX_PROBE_PER_MIN, OPERATING_POINTS  # noqa: E402
from bugarach.detect_folder import DETECTORS  # noqa: E402
from bugarach.ui.app import TITLES  # noqa: E402

#: The public build withholds locust as "sixth" (ui.app.TITLES); the darkroom is not
#: the public build, so the one key is overridden here and nowhere else.
NAMES = {**TITLES, "cicada": "locust"}
LEARNED = [("tube", "tube (center-surround)"), ("tube_guard", "tube_guard"),
           ("tube_ratio", "tube_ratio"), ("tube_ratio_guard", "tube_ratio_guard"),
           # `tiny` is ONE filter shared across every ROI, with a bounded per-ROI vote
           # pooled in rate bands — the baseline that KEEPS ROI distinctness, where
           # `trace` is the one that gives it up. "per-cell bank" said the opposite of
           # both halves of that and is not what the module builds.
           ("trace", "pooled trace"), ("tiny", "shared per-ROI filter")]
INK_HAND, INK_LEARNED, INK_GATE = "#3b6ea5", "#8b1a1a", "#c0392b"


def rows_of(d):
    """One row per detector with the per-fold conversions the spec dictates."""
    spf = int(d["seeds_per_fold"])
    n_dis = int(d["spec"]["n_distractors"]) * spf
    hw = d["spec"]["hot_window"]
    probe_min = (float(hw[1]) - float(hw[0])) / 60.0 * spf
    out = []
    for grp, names, ink in (("hand_written", [(k, NAMES[k]) for k in DETECTORS], INK_HAND),
                            ("learned", LEARNED, INK_LEARNED)):
        for key, label in names:
            r = d[grp].get(key)
            if r is None:
                continue
            pf = r["per_fold"]
            dis = [f["distractor_hits"] for f in pf]
            probe = [f["hot_fa"] / probe_min for f in pf]
            out.append(dict(
                key=key, label=label, ink=ink, grp=grp,
                f1=r["f1"]["mean"], f1_lo=r["f1"]["min"], f1_hi=r["f1"]["max"],
                recall=r["recall"]["mean"], precision=r["precision"]["mean"],
                dis=sum(dis) / len(dis), dis_lo=min(dis), dis_hi=max(dis),
                probe=sum(probe) / len(probe), probe_lo=min(probe), probe_hi=max(probe),
                gate=MAX_PROBE_PER_MIN.get(key),
                knobs=[f.get("knob_value") for f in pf],   # learned rows carry a threshold, not a knob
            ))
    return out, n_dis, probe_min, int(pf[0]["n_planted"]) if out else 0


def ceiling(n_planted: int, n_distractor: int) -> float:
    """F1 of a detector that recovers every planted event and fires on every distractor."""
    if not n_planted:
        return float("nan")
    p = n_planted / (n_planted + n_distractor)
    return 2 * p / (p + 1.0)


def build_intervals(d, *, width=270, row_h=26):
    import holoviews as hv
    hv.extension("bokeh")
    rows, n_dis, probe_min, n_planted = rows_of(d)
    ceil = ceiling(n_planted, n_dis)
    p_ceil = n_planted / (n_planted + n_dis)
    labels = [r["label"] for r in rows][::-1]
    height = row_h * len(rows) + 60
    ypos = {r["label"]: labels.index(r["label"]) for r in rows}

    def panel(letter, xlabel, xs, lo, hi, xlim, vline=None, gates=False):
        els = []
        for r in rows:
            y = ypos[r["label"]]
            els.append(hv.Curve([(lo[r["key"]], y), (hi[r["key"]], y)]).opts(color=r["ink"], line_width=2))
            els.append(hv.Scatter([(xs[r["key"]], y)]).opts(color=r["ink"], size=8))
            if gates and r["gate"] is not None:
                els.append(hv.Scatter([(r["gate"], y)]).opts(color=INK_GATE, marker="dash", size=14, line_width=2))
        if vline is not None:
            els.append(hv.VLine(vline).opts(color="#999", line_dash="dashed", line_width=1))
        return hv.Overlay(els).opts(
            width=width, height=height, toolbar=None, show_legend=False,
            xlabel=f"{letter} · {xlabel}", ylabel="",
            yticks=list(enumerate(labels)), ylim=(-0.7, len(labels) - 0.3),
            xlim=xlim, padding=0.05, show_grid=False)

    by = lambda k: {r["key"]: r[k] for r in rows}  # noqa: E731
    a = panel("A", "F1 on the held-out fold",
              by("f1"), by("f1_lo"), by("f1_hi"), (0, 1), vline=ceil)
    b = panel("B", f"distractors covered per fold, of {n_dis}",
              by("dis"), by("dis_lo"), by("dis_hi"), (-0.5, n_dis + 0.5))
    pmax = max(r["probe_hi"] for r in rows)
    gmax = max(g for g in MAX_PROBE_PER_MIN.values())
    c = panel("C", "probe firings per minute",
              by("probe"), by("probe_lo"), by("probe_hi"), (-0.5, max(pmax, gmax) * 1.1 + 0.5),
              gates=True)
    for p in (b, c):
        p.opts(yaxis=None, width=int(width * 0.8))

    # D, E · recall and precision, as dot columns on the SAME rows as A-C.
    #
    # These were one recall-against-precision scatter carrying a text label per point,
    # and the five detectors the argument is about all land in one small region of it:
    # LoCo was drawn entirely underneath CoactDetect, the tube's label ran off the right
    # frame, and tube_guard overprinted the tube. A scatter that is illegible exactly
    # where the argument is has negative value. The iso-F1 curve it also carried is
    # already a vertical line in A, so nothing is lost by putting both quantities back
    # into the row idiom, where the shared y-axis names every detector once.
    dpanel = panel("D", "recall (of the planted events)",
                   by("recall"), by("recall"), by("recall"), (0, 1.05))
    epanel = panel("E", "precision (hits ÷ scored calls)",
                   by("precision"), by("precision"), by("precision"), (0.3, 1.02),
                   vline=p_ceil)
    for p in (dpanel, epanel):
        p.opts(yaxis=None, width=int(width * 0.8))
    return (hv.Layout([a, b, c, dpanel, epanel]).cols(5).opts(shared_axes=False, toolbar=None),
            ceil, n_dis, probe_min, n_planted)


def _distinct_labels(grid: list[float]) -> list[str]:
    """Tick text that tells every grid value apart, however close together they are.

    `f"{g:g}"` renders locust's top three percentiles — 99.99999, 99.999999 and
    99.9999999 — as "100", "100", "100", which a reader takes for a broken axis rather
    than for a search that keeps going. So: take the fewest significant digits that
    still separate every value in the row, and only then fall back to repr.
    """
    for sig in range(2, 16):
        out = [f"{g:.{sig}g}" for g in grid]
        if len(set(out)) == len(out):
            return out
    return [repr(g) for g in grid]


def build_knobs(d, *, width=900, row_h=44):
    """Each hand-written detector's grid as ticks; calibrated folds filled, shipped open."""
    import holoviews as hv
    hv.extension("bokeh")
    rows, _, _, _ = rows_of(d)
    hand = [r for r in rows if r["grp"] == "hand_written"]
    els = []
    labels = []
    for i, r in enumerate(hand[::-1]):
        op = OPERATING_POINTS[r["key"]]
        grid = list(op.grid)
        shipped = op.params.get(op.knob)
        y = i
        labels.append((y, f"{r['label']} · {op.knob}"))
        n = len(grid)
        xs = [j / (n - 1) for j in range(n)]
        texts = _distinct_labels(grid)
        for j, g in enumerate(grid):
            els.append(hv.Scatter([(xs[j], y)]).opts(color="#bbb", size=5))
            els.append(hv.Text(xs[j], y - 0.38, texts[j], halign="center", fontsize=7).opts(color="#666"))
        # A grid END is only worth marking where a fold actually stopped on it — that is
        # the case the mark is about (the search was still climbing when the grid ran
        # out). Painting both ends of every row made the mark mean "this row has ends",
        # which every row does, and the key then read as an accusation against all six.
        for end, at in ((grid[0], (-0.02, 0.0)), (grid[-1], (1.0, 1.02))):
            if end in r["knobs"]:
                els.append(hv.Curve([(at[0], y), (at[1], y)]).opts(color=INK_GATE, line_width=6, alpha=0.55))
        # Folds that agree land on one point. Without a count, one dot reads as one fold.
        for k, times in Counter(k for k in r["knobs"] if k in grid).items():
            els.append(hv.Scatter([(xs[grid.index(k)], y + 0.12)]).opts(color=INK_HAND, size=9))
            if times > 1:
                els.append(hv.Text(xs[grid.index(k)], y + 0.30, f"×{times}", halign="center",
                                   fontsize=7).opts(color=INK_HAND))
        if shipped in grid:
            els.append(hv.Scatter([(xs[grid.index(shipped)], y - 0.12)]).opts(
                color="white", line_color=INK_HAND, line_width=2, size=10))
    fig = hv.Overlay(els).opts(
        width=width, height=row_h * len(hand) + 70, toolbar=None, show_legend=False,
        ylabel="", yticks=labels, ylim=(-0.8, len(hand) - 0.2), xlim=(-0.06, 1.06),
        xaxis=None, show_grid=False)
    return fig


def _chip(colour, text):
    return (f"<span style='display:inline-block;width:11px;height:11px;background:{colour};"
            f"vertical-align:-1px;margin-right:5px'></span><span style='color:{colour}'>{text}</span>")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--bakeoff", type=Path, required=True)
    ap.add_argument("--out", type=Path, default=None, help="destination (default: the darkroom)")
    ap.add_argument("--also", type=Path, default=None, help="write a second copy here")
    a = ap.parse_args(argv)

    import panel as pn
    from make_generator_figures import _write

    d = json.loads(a.bakeoff.read_text())
    fig, ceil, n_dis, probe_min, n_planted = build_intervals(d)
    folds, spf = d.get("folds"), d.get("seeds_per_fold")
    if a.out is None:
        root = paths.darkroom(create=True)
        if root is None:
            print(paths.unresolved_message(), file=sys.stderr)
            return 2
        a.out = root / "bakeoff"
    a.out.mkdir(parents=True, exist_ok=True)
    src = f"{a.bakeoff.parent.name}/{a.bakeoff.name}"

    header = pn.pane.HTML(
        f"<div style='font:13px system-ui,sans-serif;color:#111;max-width:1060px'>"
        f"<b style='font-size:16px'>the bake-off, as intervals</b> &nbsp;—&nbsp; twelve detectors on "
        f"simulated recordings; {folds} folds × {spf} seeds.<br>"
        f"Per held-out fold: {n_planted} planted events and {n_dis} correlated-burst distractors, "
        f"plus {probe_min:g} min of promiscuity probe with nothing coordinated planted "
        f"(probe firings are excluded from precision). A call on a distractor matches no "
        f"planted event, so it costs precision like any other false alarm.<br>"
        f"<b>B counts distractors COVERED by some call</b>, not calls made on them: a detector "
        f"emitting few very wide spans can cover all {n_dis} while making no false alarm at all, "
        f"which is what the two learned baselines do here.<br>"
        f"Dot: mean over folds; line: range over folds; red tick in C: the gate. Rows are grouped by family and are <b>not ranked</b>."
        f"<div style='margin:5px 0 0'>{_chip(INK_HAND, 'hand-written detector')} &nbsp; "
        f"{_chip(INK_LEARNED, 'learned model (the tube, its variants, two baselines)')} &nbsp; "
        f"{_chip(INK_GATE, 'the probe gate the bench applies to that detector (max firings/min)')} &nbsp; "
        f"<span style='color:#999'>- - -</span> in A, F1 {ceil:.3f} — the most a detector can score "
        f"if it finds every planted event AND fires once on every distractor; in E, the precision "
        f"that goes with it, {n_planted}/{n_planted + n_dis}. A detector that told a distractor "
        f"from a coordinated event would pass both.</div>"
        f"<div style='margin:4px 0 0;color:#777;font-size:11px'>{src}</div></div>")
    _write(pn.Column(header, pn.pane.HoloViews(fig)), a.out, "bakeoff_intervals", png=True)

    header2 = pn.pane.HTML(
        f"<div style='font:13px system-ui,sans-serif;color:#111;max-width:1060px'>"
        f"<b style='font-size:16px'>calibrated against shipped, on each detector's own grid</b> &nbsp;—&nbsp; "
        f"one row per hand-written detector, each on its own grid — positions are steps, "
        f"not a shared scale. &quot;×n&quot; means n folds agreed on that value. A shipped point "
        f"lying between two grid values is not drawn.<br>"
        f"<div style='margin:5px 0 0'>{_chip(INK_HAND, 'filled dot: the knob a fold chose (one per fold)')} &nbsp; "
        f"<span style='display:inline-block;width:11px;height:11px;border:2px solid {INK_HAND};"
        f"vertical-align:-1px;margin-right:5px'></span>open dot: the shipped operating point &nbsp; "
        f"{_chip(INK_GATE, 'a fold stopped on the end of the grid — that search was still climbing')}</div>"
        f"<div style='margin:4px 0 0;color:#777;font-size:11px'>{src}</div></div>")
    _write(pn.Column(header2, pn.pane.HoloViews(build_knobs(d))), a.out, "bakeoff_knobs", png=True)

    if a.also:
        a.also.mkdir(parents=True, exist_ok=True)
        for f in list(a.out.glob("bakeoff_intervals.*")) + list(a.out.glob("bakeoff_knobs.*")):
            with tempfile.TemporaryDirectory() as td:
                tmp = Path(td) / f.name
                tmp.write_bytes(f.read_bytes())
                os.replace(tmp, a.also / f.name)
        print(f"also {a.also}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
