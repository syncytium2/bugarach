#!/usr/bin/env python3
"""The bake-off as intervals, by family, with the two columns F1 cannot see.

    python tools/make_bakeoff_summary_figure.py --bakeoff RUN/bakeoff.json --out DIR

Three lettered panels, one row per detector, grouped by family (hand-written, then
learned) and NOT sorted by score — a bar chart sorted by F1 says "ranking" before
its label is read, and at four folds this table is intervals, not a ranking
(murderboard 2026-09-07, roles 4, 8 and 10 on `make_bakeoff_figures.py`'s output).

  A · F1 on the held-out fold: the fold range as a line, the mean as a dot.
  B · distractor hits, of the correlated bursts planted per held-out fold — the
      scorer counts each as a false alarm, so a detector that recovers every
      planted event and fires on every burst sits on a ceiling the panel draws.
  C · firings into the promiscuity probe, the dense block with nothing planted.

Every colour and glyph is keyed in the header, in its colour, at body size.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

HAND = [("rate", "rate+context"), ("coact", "CoactDetect"), ("loco", "LoCo"),
        ("sce", "binned SCE"), ("cicada", "locust"), ("sync", "SPIKE-synch")]
LEARNED = [("tube", "tube (center-surround)"), ("tube_guard", "tube_guard"),
           ("tube_ratio", "tube_ratio"), ("tube_ratio_guard", "tube_ratio_guard"),
           ("trace", "pooled trace"), ("tiny", "per-cell bank")]
INK_HAND, INK_LEARNED = "#3b6ea5", "#8b1a1a"


def rows_of(d):
    out = []
    for grp, names, ink in (("hand_written", HAND, INK_HAND), ("learned", LEARNED, INK_LEARNED)):
        for key, label in names:
            r = d[grp].get(key)
            if r is None:
                continue
            pf = r["per_fold"]
            out.append(dict(
                key=key, label=label, ink=ink,
                f1=r["f1"]["mean"], f1_lo=r["f1"]["min"], f1_hi=r["f1"]["max"],
                folds=[f["f1"] for f in pf],
                distractor=sum(f.get("distractor_hits", 0) for f in pf) / len(pf),
                n_distractor=max((f.get("n_distractors", 0) for f in pf), default=0),
                probe=r["hot_fa"]["mean"],
                n_planted=pf[0].get("n_planted", 0),
            ))
    return out


def ceiling(n_planted: int, n_distractor: int) -> float:
    """F1 of a detector that recovers every planted event and fires on every distractor."""
    if not n_planted:
        return float("nan")
    p = n_planted / (n_planted + n_distractor)
    return 2 * p * 1.0 / (p + 1.0)


def build(d, *, width=400, row_h=26):
    import holoviews as hv
    hv.extension("bokeh")
    rows = rows_of(d)
    n_dis = max(r["n_distractor"] for r in rows) or 12
    n_planted = rows[0]["n_planted"] if rows else 0
    ceil = ceiling(n_planted, n_dis)
    labels = [r["label"] for r in rows][::-1]         # top row first
    height = row_h * len(rows) + 60

    def panel(letter, xlabel, xs, lo=None, hi=None, xlim=None, vline=None):
        els = []
        for i, r in enumerate(rows):
            y = labels.index(r["label"])
            if lo is not None:
                els.append(hv.Curve([(lo[i], y), (hi[i], y)]).opts(color=r["ink"], line_width=2))
            els.append(hv.Scatter([(xs[i], y)]).opts(color=r["ink"], size=8))
        if vline is not None:
            els.append(hv.VLine(vline).opts(color="#999", line_dash="dashed", line_width=1))
        ov = hv.Overlay(els).opts(
            width=width, height=height, toolbar=None, show_legend=False,
            xlabel=f"{letter} · {xlabel}", ylabel="",
            yticks=list(enumerate(labels)), ylim=(-0.7, len(labels) - 0.3),
            xlim=xlim, padding=0.05, show_grid=False)
        return ov

    a = panel("A", "F1 on the held-out fold (dot: mean of 4 folds; line: fold range)",
              [r["f1"] for r in rows], [r["f1_lo"] for r in rows], [r["f1_hi"] for r in rows],
              xlim=(0, 1), vline=ceil)
    b = panel("B", f"distractor hits per fold, of {n_dis} planted (each scored as a false alarm)",
              [r["distractor"] for r in rows], xlim=(-0.5, n_dis + 0.5))
    c = panel("C", "firings into the promiscuity probe per fold (nothing planted there)",
              [r["probe"] for r in rows], xlim=(-5, max(r["probe"] for r in rows) * 1.1 + 5))
    for p in (b, c):
        p.opts(yaxis=None, width=int(width * 0.8))
    return hv.Layout([a, b, c]).cols(3).opts(shared_axes=False, toolbar=None), ceil, n_dis, n_planted


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--bakeoff", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--stem", default="bakeoff_intervals")
    a = ap.parse_args(argv)

    import panel as pn
    from make_generator_figures import _write

    d = json.loads(a.bakeoff.read_text())
    fig, ceil, n_dis, n_planted = build(d)
    folds, spf = d.get("folds"), d.get("seeds_per_fold")

    def chip(colour, text):
        return (f"<span style='display:inline-block;width:11px;height:11px;background:{colour};"
                f"vertical-align:-1px;margin-right:5px'></span><span style='color:{colour}'>{text}</span>")

    header = pn.pane.HTML(
        f"<div style='font:13px system-ui,sans-serif;color:#111;max-width:1180px;white-space:normal'>"
        f"<b style='font-size:16px'>the bake-off, as intervals</b> &nbsp;—&nbsp; twelve detectors on "
        f"simulated recordings, {folds} folds × {spf} seeds, {n_planted} planted events and {n_dis} "
        f"correlated-burst distractors per held-out fold. Rows are grouped by family and are not ranked."
        f"<div style='margin:5px 0 0'>{chip(INK_HAND, 'hand-written detector')} &nbsp; "
        f"{chip(INK_LEARNED, 'learned model (the tube and its variants, two baselines)')} &nbsp; "
        f"<span style='color:#999'>- - -</span> the F1 ceiling for a detector that recovers every planted "
        f"event and fires on every distractor: {ceil:.3f}</div>"
        f"<div style='margin:4px 0 0;color:#777;font-size:11px'>{a.bakeoff.parent.name}/{a.bakeoff.name}</div></div>",
        width=1180)
    a.out.mkdir(parents=True, exist_ok=True)
    _write(pn.Column(header, pn.pane.HoloViews(fig)), a.out, a.stem, png=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
