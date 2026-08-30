#!/usr/bin/env python3
"""The 2x2 mechanism screen, on the axis F1 cannot see.

    python tools/make_guard_screen_figure.py                      # -> the darkroom
    python tools/make_guard_screen_figure.py --also docs/learned  # + the repo copy

**What this exists to show.** The four tube cells differ by two independent
kernel changes — a GUARD interval (the reference stops abutting the sample it
judges) and a RATIO form (divide where the original subtracts). On F1 alone the
screen looks almost null: `tube` 0.681 against `tube_guard` 0.673, a difference
four folds of thirty events cannot resolve. Read only from the bake-off bar
chart, the guard did nothing.

It is not nothing. On **probe firings** — the block that contains no planted
events, so every firing inside it is a false alarm by construction — `tube` fires
20.5 times a fold and `tube_guard` 4.8. Same accuracy, a quarter of the false
alarms, and the bake-off's headline column is structurally blind to it because
probe firings enter neither the numerator nor the denominator of F1
(`docs/todo/2026-08-16-promiscuity-probe-cannot-fail.md`).

**Why that is a prediction coming true rather than a lucky seed.** Guard cells
are the fix the radar literature reached for exactly this failure, and
`detector_history.md` §5 derived the same defect in this project's detectors
independently before anyone here had read that literature: *"none of the three
excludes the moment under test from its own measurement, so a coordinated event
contributes to the estimate of the background it is judged against."* Finn &
Johnson 1968 names the masking; §5.1 says guard cells are the documented answer.
This is the first time it has been measured on a learned model here.

**The honest limit, drawn rather than written.** Four folds, one training run per
fold, no seed replication. The fold points are drawn so the overlap is visible —
the same discipline the bake-off panel uses, and for the same reason: a bar of
means invites a ranking these counts cannot support. The *ratio* arm is a
separate matter and moves F1 down (0.503 and 0.471); it is drawn so the screen is
a screen and not a highlight reel.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

CELLS = {
    "tube": ("plain", "subtract, no guard"),
    "tube_guard": ("guard", "subtract + GUARD"),
    "tube_ratio": ("ratio", "ratio, no guard"),
    "tube_ratio_guard": ("both", "ratio + GUARD"),
}
GUARDED = "#1b7f3b"
UNGUARDED = "#c0392b"


def _rows(doc: dict) -> list[dict]:
    out = []
    for key, (short, label) in CELLS.items():
        v = doc["learned"].get(key)
        if v is None:                       # a cell that did not run this time
            continue
        out.append(dict(
            key=key, short=short, label=label,
            f1=v["f1"]["mean"], probe=v["hot_fa"]["mean"],
            folds=[p["f1"] for p in v["per_fold"]],
            guarded="guard" in key,
        ))
    return out


def build(rows, width=980):
    import holoviews as hv

    # PROBE ON A LOG AXIS WITH A FLOOR. Two cells fire zero times, which a log
    # axis cannot draw at all; they are placed at the floor and the axis label
    # says so, rather than being dropped — a cell that never fires into the trap
    # is the strongest result on this axis and must not vanish from it.
    floor = 0.5
    # One overlay per cell rather than one Points with a colour list: holoviews
    # will not take a bare list as `color` (it reads it as a dimension name), and
    # a per-cell overlay is also what lets each carry its own label placement.
    # HAND-PLACED, and checked against the render. The two ratio cells sit at the
    # same x — both fire nothing into the probe — so a uniform "label above"
    # dropped each one's text onto the other's fold dots. Offsets are
    # (x-factor, y-offset, alignment).
    PLACE = {
        "tube": (0.88, +0.048, "right"),
        "tube_guard": (0.85, +0.048, "right"),
        "tube_ratio": (1.45, +0.012, "left"),
        "tube_ratio_guard": (1.45, -0.012, "left"),
    }
    layers = []
    for r in rows:
        x = max(r["probe"], floor)
        colour = GUARDED if r["guarded"] else UNGUARDED
        layers.append(hv.Points([(x, f) for f in r["folds"]]).opts(
            size=6, color=colour, alpha=0.55))
        layers.append(hv.Points([(x, r["f1"])]).opts(
            size=17, color=colour, line_color="black", line_width=1))
        fx, fy, align = PLACE.get(r["key"], (1.0, 0.045, "center"))
        layers.append(hv.Text(x * fx, r["f1"] + fy, r["label"],
                              halign=align, fontsize=9))

    return hv.Overlay(layers).opts(
        width=width, height=520, logx=True,
        xlim=(floor * 0.5, 60), ylim=(0.35, 0.85),
        xlabel="probe firings a fold — the block with nothing planted in it "
               f"(log; a cell at {floor} fired none)",
        ylabel="F1 on the held-out fold · 4 folds, dots are folds",
        show_grid=True, toolbar=None)


def main(argv=None) -> int:
    from bugarach.paths import darkroom

    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--bakeoff", type=Path,
                    default=Path("docs/learned/bakeoff.json"))
    ap.add_argument("--out", type=Path, default=None,
                    help="defaults to the darkroom — a figure is written to be "
                         "looked at, and the repo is not where a person looks")
    ap.add_argument("--also", type=Path, default=None,
                    help="extra copy, e.g. the repo's docs/learned")
    a = ap.parse_args(argv)

    doc = json.loads(a.bakeoff.read_text())
    rows = _rows(doc)
    if len(rows) < 2:
        print("guard screen: fewer than two tube cells in this bake-off — "
              "nothing to screen. Run fair_bakeoff without --quick.")
        return 1

    import importlib.util

    import holoviews as hv
    import panel as pn
    hv.extension("bokeh")
    fig = build(rows)

    # The project's own writer, reused rather than reimplemented: bokeh's PNG
    # export wants selenium, and this repo already renders through Playwright
    # chromium everywhere else. Two ways to save a figure would drift.
    spec = importlib.util.spec_from_file_location(
        "_mgf", Path(__file__).parent / "make_generator_figures.py")
    mgf = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mgf)

    outs = [a.out or darkroom()]
    if a.also:
        outs.append(a.also)
    for d in outs:
        d.mkdir(parents=True, exist_ok=True)
        mgf._write(pn.Column(pn.pane.HoloViews(fig)), d, "guard_screen", png=True)
        print(f"wrote {d / 'guard_screen.html'}")

    g = {r["key"]: r for r in rows}
    if "tube" in g and "tube_guard" in g:
        print(f"  tube       F1 {g['tube']['f1']:.3f}  probe {g['tube']['probe']:.1f}")
        print(f"  tube_guard F1 {g['tube_guard']['f1']:.3f}  "
              f"probe {g['tube_guard']['probe']:.1f}")
    return 0


if __name__ == "__main__":       # pragma: no cover
    raise SystemExit(main())
