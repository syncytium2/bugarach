#!/usr/bin/env python3
"""Draw the regime shift: calibrate in one background, deploy in the other.

    python tools/make_regime_figure.py --shift docs/learned/regime_shift.json \
        --out docs/learned

Two panels, one per direction, and both are needed because **the cost is not
symmetric** — a detector that survives one direction can fail the other, and a
single averaged number would hide exactly that.

Each detector is a line from where it scored **at home** (calibrated and tested
in the same background) to where it scored **after the shift** (same knob, same
threshold, other background). Nothing is re-tuned at the target: re-picking the
threshold on arrival is the failure being tested for, because it is the one thing
a lab deploying a fitted model cannot do.

Slopes, not bars. The question is not "which detector is best" — panel A of the
bake-off answers that — it is "what does moving cost this detector", and a
quantity about *change* should be drawn as a change. Reading two bar heights and
subtracting them by eye is how a 0.45 collapse and a 0.09 wobble end up looking
similar.

Only the **matched** test is drawn for the six: calibrated on one regime, carried
over unchanged. Their shipped fixed operating points are in the JSON too, but a
detector with no fitted state cannot exhibit a transfer collapse, so putting that
column on this figure would compare a test against a non-test.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from pathlib import Path

QUIET, BUSY = "baseline_quiet", "baseline_busy"

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
from bugarach.bench import REGIMES as _REGIMES  # noqa: E402

#: Read off `bench.REGIMES`, not transcribed. These were typed as "0.0038"/"0.0175"
#: and went stale the moment the axis was re-derived from the export folder on
#: 2026-08-20 — a figure captioned with the old endpoints while drawing the new ones
#: is worse than one with no caption at all.
RATES = {k: f"{_REGIMES[k]['bg_rate_hz']:g}" for k in (QUIET, BUSY)}


def _bakeoff_module():
    """Borrow the palette and the architecture names from the bake-off figure.

    Not tidiness. These two figures sit in the same report, and a report whose
    two figures disagree about which colour means "learned" has taught the
    reader nothing except to distrust the colour. One definition, one place.
    """
    spec = importlib.util.spec_from_file_location(
        "_mbf", Path(__file__).parent / "make_bakeoff_figures.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


_MBF = _bakeoff_module()
HAND, LEARN = _MBF.HAND, _MBF.LEARN
#: The bake-off spells these out for a standalone table ("centre−surround
#: (learned)"); here the colour already carries that, so the suffix is dropped.
ARCH = {k: v.replace(" (learned)", "") for k, v in _MBF.ARCH.items()}


def _pairs(d, metric: str, train_on: str):
    """One row per detector: where it lands at home, and after the shift."""
    test_on = BUSY if train_on == QUIET else QUIET
    rows = []

    for name, byreg in d.get("six_transfer", {}).items():
        cell = byreg.get(train_on, {})
        if "edge_of_range" in cell or train_on not in cell:
            continue                      # no operating point — nothing to plot
        from bugarach.ui.app import TITLES
        rows.append(dict(name=TITLES.get(name, name), kind="hand",
                         home=cell[train_on][metric], away=cell[test_on][metric]))

    for name, byreg in d.get("learned", {}).items():
        cell = byreg.get(train_on, {})
        if train_on not in cell:
            continue
        rows.append(dict(name=ARCH.get(name, name), kind="learned",
                         home=cell[train_on][metric], away=cell[test_on][metric]))

    return sorted(rows, key=lambda r: -r["home"])


def _spread(values, gap=0.052, lo=0.0, hi=1.03):
    """Nudge label heights apart, keeping their order.

    Nine detectors land within 0.02 of each other in places, and the first draft
    printed "CoactDetect" through "LoCo" and "CICADA" through "centre-surround"
    — four names, two legible. The line ends still sit at the true values; only
    the text moves, which is the trade a slope chart is allowed to make.
    """
    out = list(values)
    order = sorted(range(len(out)), key=lambda i: out[i])
    for k in range(1, len(order)):
        i, j = order[k - 1], order[k]
        if out[j] - out[i] < gap:
            out[j] = out[i] + gap
    over = max(out, default=0) - hi
    if over > 0:                      # pushed off the top: slide the stack down
        out = [max(lo, v - over) for v in out]
    return out


def _panel(d, metric, train_on, letter, width, height):
    import holoviews as hv

    rows = _pairs(d, metric, train_on)
    test_on = BUSY if train_on == QUIET else QUIET
    label_y = _spread([r["away"] for r in rows])
    ov = None
    for r, ly in zip(rows, label_y):
        c = LEARN if r["kind"] == "learned" else HAND
        line = hv.Curve([(0, r["home"]), (1, r["away"])],
                        kdims=["x"], vdims=[metric]).opts(
            color=c, line_width=2.6 if r["kind"] == "learned" else 1.5,
            alpha=0.95)
        ends = hv.Scatter([(0, r["home"]), (1, r["away"])]).opts(color=c, size=7)
        # Labelled at the away end, outside the plot, because a label at the home
        # end sits in the middle of eight other lines. A hairline connects the
        # text to its own line end once the de-collision has moved it.
        tie = hv.Curve([(1, r["away"]), (1.06, ly)]).opts(
            color=c, line_width=0.7, alpha=0.55)
        lab = hv.Text(1.09, ly, f'{r["name"]}  {r["away"]:.2f}').opts(
            color=c, text_font_size="8pt", text_align="left")
        layer = line * ends * tie * lab
        ov = layer if ov is None else ov * layer

    direction = ("calibrated quiet → deployed busy" if train_on == QUIET
                 else "calibrated busy → deployed quiet")
    return ov.opts(
        width=width, height=height, xlim=(-0.14, 2.05), ylim=(0, 1.06),
        xticks=[(0, f"at home ({RATES[train_on]} Hz/ROI)"),
                (1, f"after the shift ({RATES[test_on]} Hz/ROI)")],
        xlabel=f"{letter} · {direction} — knob and threshold carried over, never re-picked",
        ylabel=metric.upper() if metric == "f1" else metric, show_grid=True,
        fontsize={"ylabel": "10pt", "xlabel": "10pt", "ticks": "9pt"},
        toolbar=None)


def build(d, width=920, height=300):
    """Three panels, and they must fit the PNG renderer's viewport.

    `_render_png` clips to the ink by ignoring any element as tall as the
    viewport — which is how it avoids measuring Panel's full-height body. At
    400 px per panel the content column grew past the 1,200 px viewport, got
    excluded by that same rule, and the export measured 920x0 and wrote nothing.
    The HTML was fine, so the failure was invisible except in the log.
    """
    a = _panel(d, "f1", QUIET, "A", width, height)
    b = _panel(d, "f1", BUSY, "B", width, height)
    c = _panel(d, "precision", QUIET, "C", width, height)
    return (a + b + c).cols(1).opts(shared_axes=False, toolbar=None)


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--shift", type=Path, required=True)
    p.add_argument("--out", type=Path, required=True)
    p.add_argument("--width", type=int, default=920)
    p.add_argument("--height", type=int, default=300)
    p.add_argument("--name", default="regime_shift")
    a = p.parse_args(argv)

    import holoviews as hv
    import panel as pn
    hv.extension("bokeh")

    spec = importlib.util.spec_from_file_location(
        "_mgf", Path(__file__).parent / "make_generator_figures.py")
    mgf = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mgf)

    d = json.loads(a.shift.read_text())
    a.out.mkdir(parents=True, exist_ok=True)
    mgf._write(pn.Column(pn.pane.HoloViews(build(d, a.width, a.height))),
               a.out, a.name, png=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
