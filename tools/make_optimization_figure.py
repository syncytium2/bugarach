#!/usr/bin/env python3
"""What the calibration actually chose, fold by fold — the optimisation, drawn.

    python tools/make_optimization_figure.py                      # -> the darkroom
    python tools/make_optimization_figure.py --also docs/learned  # + the repo copy

Every detector's knob is swept on the calibration folds and the winner is carried
to the held-out fold. The bake-off reports the F1 that comes back and says nothing
about the choice that produced it, so two things stay invisible:

**Whether the choice is stable.** If a detector picks a different operating point
depending on which three folds it saw, its "calibrated setting" is a property of
the sample and not of the detector. On the 2026-08-29 run four of six varied
across folds — and a mean F1 over four folds calibrated four different ways is a
weaker quantity than it looks.

**Whether the optimum is real or just the end of the grid.** `bugarach.bench` has
a standing refusal — *it will not report an optimum sitting on the edge of the
grid it searched* — because an edge value means the search was still climbing
when it ran out of room. That refusal governs `bench`; this figure shows the same
condition arising inside the bake-off, where it is reported rather than refused.

Each detector gets a row, its grid drawn as ticks, and the value chosen on each
fold marked. A grid-edge choice is drawn hollow. Nothing is aggregated: the point
is the spread, and a mean over four different settings would erase it.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

LABELS = {"rate": "rate+context", "sce": "binned SCE", "coact": "CoactDetect",
          "loco": "LoCo", "cicada": "the sixth", "sync": "SPIKE-synch"}
STABLE = "#1b7f3b"
VARIES = "#c0392b"


def _rows(doc: dict) -> list[dict]:
    swept = doc.get("provenance", {}).get("detectors_swept", {})
    out = []
    for key, v in doc["hand_written"].items():
        folds = v.get("per_fold", [])
        if not folds or folds[0].get("knob") is None:
            continue
        grid = list(swept.get(key, {}).get("grid") or [])
        chosen = [p["knob_value"] for p in folds]
        out.append(dict(key=key, label=LABELS.get(key, key),
                        knob=folds[0]["knob"], grid=grid, chosen=chosen,
                        stable=len(set(chosen)) == 1,
                        edge={c for c in chosen if grid and c in (grid[0], grid[-1])}))
    return out


def build(rows, width=980):
    import holoviews as hv

    # RANK, NOT VALUE, ON THE X AXIS. The grids are wildly different scales —
    # alpha runs 1e-2..1e-7 and a percentile 99..99.9999 — so a shared value axis
    # would put every detector's whole grid in one pixel column. Rank keeps each
    # row readable and the question is positional anyway: WHERE in its own grid
    # did this land, and did it land in the same place twice.
    layers, yticks = [], []
    for i, r in enumerate(reversed(rows)):
        y = i
        yticks.append((y, f"{r['label']}  ·  {r['knob']}"))
        n = len(r["grid"])
        if n:
            layers.append(hv.Points([(j, y) for j in range(n)]).opts(
                size=7, color="#cccccc", marker="dash", angle=90))
        colour = STABLE if r["stable"] else VARIES
        for c in r["chosen"]:
            j = r["grid"].index(c) if c in r["grid"] else 0
            hollow = c in r["edge"]
            layers.append(hv.Points([(j, y)]).opts(
                size=16, color="white" if hollow else colour,
                line_color=colour, line_width=2.5, alpha=0.9))
        if n:
            layers.append(hv.Text(n - 0.5 + 0.35, y,
                                  ("edge of grid" if r["edge"] else
                                   ("one setting" if r["stable"] else "varies")),
                                  halign="left", fontsize=8))

    return hv.Overlay(layers).opts(
        width=width, height=90 + 46 * len(rows),
        xlim=(-0.7, max((len(r["grid"]) for r in rows), default=8) + 2.6),
        ylim=(-0.8, len(rows) - 0.2),
        yticks=yticks, xaxis="bare",
        xlabel="", ylabel="",
        show_grid=False, toolbar=None)


def main(argv=None) -> int:
    from bugarach.paths import darkroom

    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--bakeoff", type=Path,
                    default=Path("docs/learned/bakeoff.json"))
    ap.add_argument("--out", type=Path, default=None)
    ap.add_argument("--also", type=Path, default=None)
    a = ap.parse_args(argv)

    doc = json.loads(a.bakeoff.read_text())
    rows = _rows(doc)
    if not rows:
        print("optimisation figure: this bake-off records no per-fold knob "
              "choices — nothing to draw.")
        return 1

    import importlib.util

    import holoviews as hv
    import panel as pn
    hv.extension("bokeh")

    spec = importlib.util.spec_from_file_location(
        "_mgf", Path(__file__).parent / "make_generator_figures.py")
    mgf = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mgf)

    fig = build(rows)
    for d in [a.out or darkroom()] + ([a.also] if a.also else []):
        d.mkdir(parents=True, exist_ok=True)
        mgf._write(pn.Column(pn.pane.HoloViews(fig)), d, "optimization", png=True)
        print(f"wrote {d / 'optimization.html'}")

    for r in rows:
        note = "one setting" if r["stable"] else f"{len(set(r['chosen']))} settings"
        edge = "  EDGE OF GRID" if r["edge"] else ""
        print(f"  {r['label']:14s} {r['knob']:20s} {note}{edge}")
    return 0


if __name__ == "__main__":       # pragma: no cover
    raise SystemExit(main())
