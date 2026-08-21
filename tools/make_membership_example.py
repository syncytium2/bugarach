#!/usr/bin/env python3
"""What the question looks like before any statistic is applied.

    python tools/make_membership_example.py --folder DIR
    python tools/make_membership_example.py --folder DIR --out DIR

Figure id `assembly_membership`, the same on every machine.

Every other figure in this line reports a p-value. This one reports **the data**:
who took part in each coordinated event, drawn as a grid. One row per event, one
column per cell, a mark where that cell took part. Cells are ordered by how often
they took part, so a recording in which the same cells recur shows **vertical
stripes on the left** and a recording in which participation is fresh each time
shows an even speckle.

Three panels, chosen to be read against each other:

- **A** — a real recording the test calls structured.
- **B** — a real recording the test does not.
- **C** — a generated recording, whose participants are drawn uniformly at random
  by construction (`simulate.py`, `rng.choice`), so it is what "no recurring group"
  looks like when it is true by definition.

The point of C is that A and B are both *real*, so neither on its own tells you
what the instrument would do on data with no structure in it. C does.

Reads an export folder and nothing else.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import tempfile
from pathlib import Path

import numpy as np

FIGURE_ID = "assembly_membership"
K = 3
MARK = "#111111"
GEN = "#a9540f"


def membership(slice_obj, stream: str, n_surr: int = 50):
    """The events x cells grid for one recording's baseline window."""
    from bugarach.assess import assess_coactivity
    from bugarach.assembly import membership_matrix

    base = [r for r in (slice_obj.regions or [])
            if (getattr(r, "name", "") or "").strip().lower().startswith("base")]
    if base:
        r = max(base, key=lambda r: r.end_sec - r.start_sec)
        win = ((r.analysis_start_sec, r.analysis_end_sec)
               if getattr(r, "has_analysis_window", False)
               else (r.start_sec, r.end_sec))
    else:
        # A generated recording carries no regions — the whole of it is baseline
        # by construction. A REAL recording with no baseline region is a different
        # thing entirely and is skipped, which is why this is not a general
        # fallback: it applies only where there are no regions at all.
        if slice_obj.regions:
            return None, None
        win = None
    if stream not in slice_obj.streams:
        return None, None
    a = [x for x in assess_coactivity(slice_obj, stream=stream, window=win,
                                      n_surrogates=n_surr) if x.min_rois == K]
    if not a:
        return None, None
    return membership_matrix(a[0].members, a[0].n_roi), a[0]


def ordered(M):
    """Cells ordered by how often they took part, busiest first.

    The ordering is cosmetic and it is the whole readability of the panel: without
    it a recurring group is scattered across the width and looks like noise. It
    cannot manufacture the pattern — sorting columns of a matrix with no structure
    still gives no stripes, only a smooth left-to-right gradient.
    """
    if M is None or M.size == 0:
        return M
    return M[:, np.argsort(-M.sum(axis=0))]


def panel(M, colour, label, width, height=330):
    """One membership matrix, drawn as a MATRIX and not as a raster.

    This mattered enough to be rebuilt. Drawn as scattered square markers on
    continuous axes it read as a spike raster — the dominant idiom in this field
    and in this project's own viewer — where the horizontal axis is TIME and each
    row is a cell. Here the horizontal axis is a *cell* and each row is a
    *coordinated event*, so a reader fluent in rasters read both axes wrong and
    saw structure in the wrong dimension (Tony, 2026-08-18: "showing something
    that looks like a raster when it is not a raster is really mind blowing").

    So: bordered tiles on integer axes, one tile per (event, cell) pair, filled
    when that cell took part. A gridded matrix cannot be mistaken for a raster,
    and the empty tiles carry the same information as the filled ones — which a
    scatter of markers never showed at all.
    """
    import holoviews as hv
    Mo = ordered(M)
    n_ev, n_cell = Mo.shape
    tiles = [(int(c), int(e), float(Mo[e, c]))
             for e in range(n_ev) for c in range(n_cell)]
    return hv.HeatMap(tiles, kdims=["cell", "event"], vdims=["took part"]).opts(
        cmap=["#f2f2f2", colour], line_color="white", line_width=0.6,
        width=width, height=height, colorbar=False, tools=[],
        xlabel=f"one column per cell, ordered by participation  (1–{n_cell});  one row per event",
        ylabel=label, title="", show_legend=False,
        xticks=0, yticks=0,
        fontsize={"labels": "10pt", "ticks": "9pt"})


def main(argv=None):
    p = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--folder", type=Path, required=True,
                   help="an export folder (the input contract)")
    p.add_argument("--runs", type=Path, required=True,
                   help="output dir of assess_archive --assemblies, same stream")
    p.add_argument("--stream", default="fast")
    p.add_argument("--width", type=int, default=400)
    p.add_argument("--out", default=None)
    p.add_argument("--no-png", dest="png", action="store_false", default=True)
    args = p.parse_args(argv)

    from bugarach.io import load_folder

    rows = [r for r in json.loads(
        (args.runs / "assessment_real.json").read_text())["rows"]
        if r["K"] == K and r.get("asm_defined")]
    hits = [r for r in rows if r["asm_verdict"] == "structure-beyond-rate"]
    misses = [r for r in rows if r["asm_verdict"] == "no-assembly"]
    if not hits or not misses:
        raise SystemExit("need one structured and one unstructured recording")
    # The median-sized example of each, so the panel is typical rather than the
    # most flattering one available.
    hits.sort(key=lambda r: r["asm_n_events"])
    misses.sort(key=lambda r: r["asm_n_events"])
    pick_hit = hits[len(hits) // 2]["slice_id"]
    pick_miss = misses[len(misses) // 2]["slice_id"]

    slices = {s.slice_id: s for s in load_folder(args.folder)}
    Ma, aa = membership(slices[pick_hit], args.stream)
    Mb, ab = membership(slices[pick_miss], args.stream)

    from bugarach.simulate import simulate_coordination

    def matched_control(a, seed):
        """A generated recording at ONE real panel's geometry.

        Matched per panel, because the quantity being compared is a share of the
        busiest few cells and that is not comparable across recordings with
        different cell counts. Comparing a 33-cell recording against a 24-cell
        control is how this figure previously appeared to show a paradox it did
        not have.
        """
        g, _ = simulate_coordination(
            n_roi=int(a.n_roi), duration_sec=1200.0, bg_rate_hz=0.0008,
            participation=(float(a.part_n_obs) / max(a.n_roi, 1),),
            n_per_level=(max(4, int(a.n_clusters_obs)),),
            jitter_sec=0.3, min_sep_sec=5.0, spacing="uniform", seed=seed)
        return membership(g, "events")

    Mc, ac = matched_control(aa, 11)          # control at A's geometry
    Mc_b, ac_b = matched_control(ab, 12)      # control at B's geometry

    print(f"A real structured : {pick_hit}  {Ma.shape[0]} events x {Ma.shape[1]} cells")
    print(f"B real unstructured: {pick_miss}  {Mb.shape[0]} x {Mb.shape[1]}")
    print(f"C generated        : {Mc.shape[0]} x {Mc.shape[1]}")

    from bugarach.paths import darkroom, unresolved_message
    dest = Path(args.out) if args.out else darkroom()
    if dest is None:
        print(unresolved_message(), file=sys.stderr)
        return 1
    dest.mkdir(parents=True, exist_ok=True)

    import holoviews as hv
    import panel as pn
    hv.extension("bokeh")

    def frac_top(M, n=5):
        c = np.sort(M.sum(axis=0))[::-1]
        return float(c[:n].sum() / max(M.sum(), 1))

    layout = (panel(Ma, MARK, f"A · real, structured — {Ma.shape[0]} events", args.width)
              + panel(Mb, MARK, f"B · real, not structured — {Mb.shape[0]} events", args.width)
              + panel(Mc, GEN, f"C · generated control — {Mc.shape[0]} events",
                      args.width)).cols(3).opts(shared_axes=False, toolbar=None)

    # No baked header — the caption lives in the document, in the document's own
    # type, where it can be selected, searched and read by a screen reader. What
    # the figure keeps is what labels the thing it sits next to.
    header = ""

    print(f"top-5 share — A {frac_top(Ma):.0%} (control at A's geometry "
          f"{frac_top(Mc):.0%}) · B {frac_top(Mb):.0%} (control at B's geometry "
          f"{frac_top(Mc_b):.0%})")

    html = dest / f"{FIGURE_ID}.html"
    pane = (pn.Column(pn.pane.HTML(header), pn.pane.HoloViews(layout))
            if header else pn.Column(pn.pane.HoloViews(layout)))
    pn.panel(pane).save(str(html))
    print(f"wrote {html}")

    if args.png:
        try:
            from playwright.sync_api import sync_playwright
            with sync_playwright() as pw:
                b = pw.chromium.launch()
                pg = b.new_page(viewport={"width": 1400, "height": 400},
                              device_scale_factor=2)
                pg.goto(html.resolve().as_uri())
                pg.wait_for_timeout(2500)
                with tempfile.TemporaryDirectory() as td:
                    tmp = Path(td) / "s.png"
                    pg.screenshot(path=str(tmp), full_page=True)
                    b.close()
                    os.replace(tmp, dest / f"{FIGURE_ID}.png")
            print(f"wrote {dest / f'{FIGURE_ID}.png'}")
        except Exception as exc:                       # noqa: BLE001
            print(f"(PNG render failed: {type(exc).__name__}: {exc})", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
