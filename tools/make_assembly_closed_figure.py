#!/usr/bin/env python3
"""The assembly question, closed: the problem, the test, and the result.

    python tools/make_assembly_closed_figure.py \\
        --power   <dir>/power_verdict_fast.json \\
        --pensub  <dir>/pensub_cmp_fast_k3.json <dir>/pensub_cmp_slow_k3.json \\
        --folder  <export folder> --slice 20240708_13

Figure id `assembly_closed`, the same on every machine.

**One figure, three panels, in the order a reader needs them.**

- **A — the problem.** Who took part in each coordinated event, drawn as a
  matrix: a real recording beside a generated one whose participants are drawn
  uniformly at random. If recurring groups were obvious, this panel would settle
  the question and the other two would be unnecessary. It does not, which is why
  there is an instrument at all.

- **B — the test, and the proof it could have failed.** Power under the rule
  recordings are *actually* scored by — `AssemblyResult.verdict()`, Bonferroni
  across the two statistics within each null — evaluated at **each real
  recording's own geometry**, not at a median slice. The leftmost point of every
  curve is the size of the test with nothing planted; it sits at the nominal
  level, so a `no-assembly` tally means something. A negative result is only a
  result if a positive one was reachable, and this panel is that proof.

- **C — the result.** The verdict on every testable recording, before and after
  the largest alternative explanation is removed. Optical crosstalk between
  neighbouring ROIs puts one cell's transient into its neighbour's trace; no
  reshuffle of a membership table can undo it, because the artifact is already
  in the table. So the table is rebuilt from the penumbra-subtracted store and
  re-measured, **paired**, on the recordings testable in both.

**What the figure must not be read as saying.** Panel C shows a departure from
uniform participation, not assemblies. The companion BCT modularity measurement
on the same preparation finds no modular partition above its null, and the two
together describe a **core–periphery** field — a few cells in most events, a long
tail in few — which is weaker and more ordinary than a cell assembly.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import tempfile
from pathlib import Path

import numpy as np

FIGURE_ID = "assembly_closed"

sys.path.insert(0, str(Path(__file__).resolve().parent))

#: One colour per assembly size, dark to light as the assembly gets more diffuse.
#: Same ramp as `assembly_power`, so the two figures can be read together.
SIZE_COLOURS = ["#111111", "#1f6fb4", "#3fa34d", "#d98324", "#b03a48"]
REAL = "#111111"
CONTROL = "#b4521f"
GUIDE = "#9a9a9a"
BEFORE = "#1f6fb4"
AFTER = "#d98324"
LOST = "#c9c9c9"


# ---- panel A: the data, before any statistic -------------------------------

def real_and_control(folder: Path, slice_id: str, stream: str, seed: int = 3):
    """One real recording's membership matrix, and a uniform control beside it.

    Reads an **export folder** — the input contract, and the whole input. This
    took a `.mat` store until 2026-08-20; see the note in `bugarach.assembly` for
    what going around the contract cost.

    The control is drawn at the real recording's **own** geometry — same number
    of events, same event sizes, same ROI count — because a top-five
    participation share means different things in recordings of different size.
    An earlier figure in this line compared panels of different widths directly
    and appeared to show the statistic ranking a structureless recording above a
    real one; it was a denominator, not a finding.
    """
    from make_membership_example import membership
    from bugarach.io import load_folder

    by_id = {s.slice_id: s for s in load_folder(folder)}
    if slice_id not in by_id:
        raise SystemExit(f"{slice_id} is not in {folder} — "
                         f"{len(by_id)} recordings there. A recording the producer "
                         f"withdrew is simply absent; pick one that is present.")
    M, a = membership(by_id[slice_id], stream)
    if M is None:
        raise SystemExit(f"{slice_id}: no testable {stream} clusters at K")

    rng = np.random.RandomState(seed)
    sizes = M.sum(axis=1)
    n_roi = M.shape[1]
    C = np.zeros_like(M)
    for e, k in enumerate(sizes):
        C[e, rng.choice(n_roi, size=int(k), replace=False)] = True
    return M, C, a


# ---- panel B: power under the rule the folder is scored by -----------------

def power_curves(power_json: Path) -> tuple[list, list, dict]:
    """`verdict_rows` from `assembly_power.py --geometry-from`."""
    d = json.loads(Path(power_json).read_text())
    rows = d.get("verdict_rows")
    if not rows:
        raise SystemExit(f"{power_json} carries no verdict_rows — rerun "
                         f"assembly_power.py with --geometry-from")
    sizes = sorted({r["A"] for r in rows})
    strengths = sorted({r["strength"] for r in rows})
    return sizes, strengths, {(r["A"], r["strength"]): r for r in rows}


# ---- panel C: the paired crosstalk control ---------------------------------

def pensub_bars(paths: list[Path]) -> list[dict]:
    out = []
    for p in paths:
        d = json.loads(Path(p).read_text())
        out.append(d)
    return out


def build(M, C, power, pensub, width: int, alpha: float = 0.05):
    import holoviews as hv
    from make_membership_example import panel

    sizes, strengths, cells = power

    # ---- A -----------------------------------------------------------------
    # `panel` writes a long self-describing xlabel that suits a three-across
    # figure; here the panels are half that width and it clips. The axis is
    # relabelled, not redrawn — the ordering and the tile grammar are what stop
    # this being misread as a spike raster, and both are `panel`'s.
    n_cell = M.shape[1]
    ax = f"cells, ordered by participation (1–{n_cell})  →"
    a1 = panel(M, REAL, "A · real recording", int(width * 0.46),
               height=330).opts(xlabel=ax)
    a2 = panel(C, CONTROL, "A · uniform control, same geometry",
               int(width * 0.46), height=330).opts(xlabel=ax)

    # ---- B -----------------------------------------------------------------
    # The horizontal guide is the size of the test, not a target: with nothing
    # planted the curves must START there or the negative below is not quotable.
    # The guide is labelled ON the figure, not only in the caption: an
    # unexplained line is a defect, and this one carries the whole claim that
    # the curves start where a test with nothing planted should start.
    bits = [hv.HLine(alpha).opts(color=GUIDE, line_width=1.5, line_dash="dotted"),
            hv.Text(0.42, alpha + 0.055,
                    f"{alpha:.0%} — size of the test, nothing planted").opts(
                        color=GUIDE, text_font_size="8pt", text_align="left")]
    for i, A in enumerate(sizes):
        xs = [s for s in strengths if (A, s) in cells]
        ys = [cells[(A, s)]["verdict_power"] for s in xs]
        col = SIZE_COLOURS[i % len(SIZE_COLOURS)]
        bits.append(hv.Curve((xs, ys), label=f"{A} cells").opts(
            color=col, line_width=2.5))
        bits.append(hv.Scatter((xs, ys)).opts(
            color=col, size=7, line_color="white", line_width=0.8))
    b = hv.Overlay(bits).opts(
        width=int(width * 0.95), height=380, ylim=(-0.04, 1.06),
        xlabel="fraction of a recording's events drawn from the assembly",
        # A FRACTION, and the axis must say so — it runs 0-1 and "recordings
        # where the test fires" reads as a count of them.
        ylabel="B · fraction of recordings where the test fires",
        title="", show_legend=True, legend_position="bottom_right",
        fontsize={"labels": "11pt", "ticks": "9pt", "legend": "9pt"})

    # ---- C -----------------------------------------------------------------
    # Paired, and the lost-testability bar is drawn beside the verdicts rather
    # than folded into them. Penumbra subtraction removes events, removing events
    # removes coactive clusters, and a recording that drops below the floor
    # returns `undefined`. Folding those into "did not fire" would read a loss of
    # POWER as a loss of SIGNAL — the single most likely way to get this wrong.
    recs = []
    for d in pensub:
        st = d.get("stream") or "?"
        n = d["n_testable_both"]
        recs.append((f"{st} · {n} paired", "original", d["fired_main"]))
        recs.append((f"{st} · {n} paired", "penumbra-subtracted",
                     d["fired_pensub"]))
        recs.append((f"{st} · {n} paired", "lost testability",
                     d["n_lost_testability"]))
    # Explicit category order. Left to default, holoviews sorts alphabetically
    # and the bars read "lost testability, penumbra-subtracted, original" — the
    # story backwards, with the colour ramp reassigned to match.
    series = hv.Dimension("series", values=["original", "penumbra-subtracted",
                                            "lost testability"])
    c = hv.Bars(recs, kdims=["cell", series], vdims=["recordings"]).opts(
        width=int(width * 0.95), height=380, stacked=False,
        cmap=[BEFORE, AFTER, LOST], line_color="white", line_width=1,
        xlabel="recordings testable in BOTH stores",
        # NOT "recordings where the test fires" — the third bar counts
        # recordings that dropped below the testable floor, which is a different
        # quantity sharing the axis. The category names carry the distinction.
        ylabel="C · recordings", title="",
        show_legend=True, legend_position="top_right", legend_cols=1,
        xrotation=0, ylim=(0, 33),
        fontsize={"labels": "11pt", "ticks": "8pt", "legend": "9pt"})

    # No baked header: the caption lives in the document, in the document's type.
    # A rasterized paragraph is unselectable, unreachable by a screen reader, and
    # renders at a few pixels on a phone.
    return ((a1 + a2).cols(2) + (b + c).cols(2)).cols(2).opts(
        shared_axes=False, toolbar=None), ""


def _render_png(html_path: Path, png_path: Path, *, wait_ms: int = 3000,
                width: int = 1620, height: int = 810) -> bool:
    """Screenshot the built page with Playwright chromium, as the other tools do."""
    try:
        from playwright.sync_api import sync_playwright
    except Exception as exc:                                  # noqa: BLE001
        print(f"(PNG render skipped: {exc})", file=sys.stderr)
        return False
    try:
        with sync_playwright() as pw:
            b = pw.chromium.launch()
            pg = b.new_page(viewport={"width": width, "height": height},
                            device_scale_factor=2)
            pg.goto(html_path.resolve().as_uri())
            pg.wait_for_timeout(wait_ms)
            pg.screenshot(path=str(png_path), full_page=False)
            b.close()
        return True
    except Exception as exc:                                  # noqa: BLE001
        print(f"(PNG render failed: {type(exc).__name__}: {exc})", file=sys.stderr)
        return False


def main(argv=None):
    p = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--power", type=Path, required=True,
                   help="assembly_power.py --geometry-from JSON (has verdict_rows)")
    p.add_argument("--pensub", type=Path, nargs="+", required=True,
                   help="assembly_pensub_compare.py --json-out, one per stream")
    p.add_argument("--folder", type=Path, required=True,
                   help="export folder holding the recording drawn in panel A")
    p.add_argument("--slice", required=True, help="slice id for panel A")
    p.add_argument("--stream", default="fast")
    p.add_argument("--width", type=int, default=760)
    p.add_argument("--seed", type=int, default=3)
    # A figure is something a person looks at, so it goes where a person can open
    # it. `--also` puts a copy in the repo for review and git history.
    p.add_argument("--out", default=None,
                   help="destination directory; default $BUGARACH_DARKROOM")
    p.add_argument("--also", type=Path, default=None,
                   help="additional destination, e.g. a repo copy")
    p.add_argument("--no-png", dest="png", action="store_false", default=True)
    a = p.parse_args(argv)

    M, C, ass = real_and_control(a.folder, a.slice, a.stream, seed=a.seed)
    power = power_curves(a.power)
    pensub = pensub_bars(a.pensub)

    print(f"panel A: {a.slice} · {a.stream} · {M.shape[0]} events x {M.shape[1]} cells")
    for d in pensub:
        print(f"panel C: {d.get('stream')} K={d.get('k')} · "
              f"{d['fired_main']}/{d['n_testable_both']} -> "
              f"{d['fired_pensub']}/{d['n_testable_both']} fire, "
              f"{d['n_lost_testability']} lost testability, "
              f"McNemar p={d['mcnemar_p']:.3g}")

    from bugarach.paths import darkroom, unresolved_message
    dest = Path(a.out) if a.out else darkroom()
    if dest is None:
        print(unresolved_message(), file=sys.stderr)
        return 1

    import holoviews as hv
    import panel as pn
    hv.extension("bokeh")
    layout, header = build(M, C, power, pensub, a.width)

    dests = [dest] + ([a.also] if a.also else [])
    for i, d in enumerate(dests):
        d.mkdir(parents=True, exist_ok=True)
        html = d / f"{FIGURE_ID}.html"
        pn.panel(pn.Column(pn.pane.HTML(header),
                           pn.pane.HoloViews(layout))).save(str(html))
        print(f"wrote {html}")
        if a.png:
            shot = d / f"{FIGURE_ID}.png"
            if i == 0:
                if _render_png(html, shot):
                    print(f"wrote {shot}")
            else:
                src = dests[0] / f"{FIGURE_ID}.png"
                if src.is_file():
                    shot.write_bytes(src.read_bytes())
                    print(f"wrote {shot}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
