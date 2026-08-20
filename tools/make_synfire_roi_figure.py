#!/usr/bin/env python3
"""How much of the synfire indicator was cells that never fired?

    python tools/make_synfire_roi_figure.py \
        --published <dir>/synfire_fast_relabel_silentkept.json \
        --corrected <dir>/synfire_fast_relabel.json --stream fast

Figure id `synfire_roi`, the same on every machine.

`tools/synfire_scan.py` used to hand every ROI to the sorter, silent ones included.
PySpike scores a pair of trains that are **both empty** as `(e=1, m=1)` — the value a
perfectly ordered pair gets — so each pair of silent ROIs added a maximal-order term,
quadratic in the number of cells that never fired. This draws what that cost.

**Two panels, because the answer has two halves that point opposite ways.**

- **A — the magnitude was contaminated, and worst where it mattered most.** Each
  recording's indicator as published against the same recording with silent ROIs
  dropped, marks sized by how many ROIs were silent. Points on the diagonal had
  nothing to lose. The excursions are all sparse recordings, and they are the ones
  that sat at the top of the published distribution.
- **B — the verdict was not.** The relabel null preserves each ROI's own event count,
  so silent ROIs stay silent in the surrogates and the inflation lands on both sides
  of the comparison. What a recording was *called* barely moves; what it *scored*
  does.

Reads two `synfire_scan.py` runs of the same stream and nothing else.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

FIGURE_ID = "synfire_roi"

INK = "#111111"
SILENT = "#b03a48"
GUIDE = "#9a9a9a"

#: The scan's own significance line.
ALPHA = 0.05


def load(path: Path) -> dict[str, dict]:
    return {r["slice_id"]: r for r in json.loads(path.read_text())["rows"]}


def pair_up(published: dict, corrected: dict) -> list[dict]:
    """Recordings present in both runs, with the silent-ROI count that separates them.

    ``n_roi`` is the recording's ROI count in both files; ``n_trains_scored`` is what
    actually reached the sorter and exists only in the corrected run, so the silent
    count is derived from the published side, where every ROI was scored.
    """
    out = []
    for sid in sorted(set(published) & set(corrected)):
        p, c = published[sid], corrected[sid]
        out.append(dict(slice_id=sid,
                        f_pub=float(p["synfire"]), f_cor=float(c["synfire"]),
                        p_pub=float(p["p"]), p_cor=float(c["p"]),
                        n_roi=int(p["n_roi"]), n_active=int(p["n_active"]),
                        n_silent=int(p["n_roi"]) - int(p["n_active"]),
                        spikes=int(p["n_spikes"])))
    return out


def build(rows: list[dict], stream: str, width: int):
    import holoviews as hv

    f_pub = np.array([r["f_pub"] for r in rows])
    f_cor = np.array([r["f_cor"] for r in rows])
    sil = np.array([r["n_silent"] for r in rows])
    lo = float(min(f_pub.min(), f_cor.min()))
    hi = float(max(f_pub.max(), f_cor.max()))
    pad = 0.05 * (hi - lo)

    # Marks scale with silent-ROI count, so the excursions explain themselves.
    size = 5 + 22 * (sil / max(1, sil.max()))
    pts = hv.Points(
        {"pub": f_pub, "cor": f_cor, "size": size, "silent": sil,
         "slice": [r["slice_id"] for r in rows],
         "spikes": [r["spikes"] for r in rows]},
        kdims=["pub", "cor"], vdims=["size", "silent", "slice", "spikes"])
    a = (hv.Curve([(lo - pad, lo - pad), (hi + pad, hi + pad)])
         .opts(color=GUIDE, line_width=1, line_dash="dotted") * pts.opts(
             size=hv.dim("size"), color=SILENT, alpha=0.55, line_color=INK,
             line_width=0.4,
             tools=["hover"],
             xlabel=f"indicator as published · {stream} · {len(rows)} rec",
             ylabel="silent ROIs dropped",
             xlim=(lo - pad, hi + pad), ylim=(lo - pad, hi + pad),
             width=width // 2, height=380, title="", show_legend=False,
             fontsize={"labels": "10pt", "ticks": "9pt"}))

    # Panel B: the verdict, as a 2x2 of what changed. Counts, not rates — the whole
    # point is that the cells off the diagonal are nearly empty.
    both = sum(1 for r in rows if r["p_pub"] < ALPHA and r["p_cor"] < ALPHA)
    lost = sum(1 for r in rows if r["p_pub"] < ALPHA and r["p_cor"] >= ALPHA)
    gain = sum(1 for r in rows if r["p_pub"] >= ALPHA and r["p_cor"] < ALPHA)
    neither = len(rows) - both - lost - gain
    bars = hv.Bars([("above null, both", both), ("above null only as published", lost),
                    ("above null only once corrected", gain), ("below null, both", neither)],
                   kdims=["outcome"], vdims=["n"])
    b = bars.opts(color=INK, alpha=0.85, invert_axes=True,
                  xlabel="", ylabel=f"recordings ({len(rows)})",
                  width=width // 2, height=380, title="", show_legend=False,
                  fontsize={"labels": "10pt", "ticks": "9pt"})

    return (a + b).cols(2).opts(shared_axes=False, toolbar=None)


def _render_png(html_path: Path, png_path: Path, *, wait_ms: int = 2500,
                width: int = 1320, height: int = 470) -> bool:
    """Imported rather than copied: `_render_png` is already duplicated across eight
    figure tools (`docs/todo/2026-08-18-render-png-duplicated-across-figure-tools.md`)
    and a ninth copy would make that todo worse."""
    sys.path.insert(0, str(Path(__file__).parent))
    from make_modularity_figure import _render_png as impl
    return impl(html_path, png_path, wait_ms=wait_ms, width=width, height=height)


def main(argv=None):
    p = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--published", type=Path, required=True,
                   help="a --keep-silent-rois run (the pre-fix behaviour)")
    p.add_argument("--corrected", type=Path, required=True)
    p.add_argument("--stream", default="fast")
    p.add_argument("--width", type=int, default=1240)
    p.add_argument("--out", default=None,
                   help="destination directory; default $BUGARACH_DARKROOM")
    p.add_argument("--also", type=Path, default=None)
    p.add_argument("--no-png", dest="png", action="store_false", default=True)
    a = p.parse_args(argv)

    rows = pair_up(load(a.published), load(a.corrected))
    if not rows:
        print("no recordings in common between the two runs", file=sys.stderr)
        return 1

    d = np.array([r["f_pub"] - r["f_cor"] for r in rows])
    sil = np.array([r["n_silent"] for r in rows])
    print(f"{a.stream}: {len(rows)} recordings, {int(sil.sum())} silent ROIs "
          f"({100 * sil.sum() / sum(r['n_roi'] for r in rows):.0f}% of all ROIs)")
    print(f"  |change| in indicator: median {np.median(np.abs(d)):.4f}  "
          f"p90 {np.percentile(np.abs(d), 90):.4f}  max {np.abs(d).max():.4f}")
    print(f"  above null: {sum(1 for r in rows if r['p_pub'] < ALPHA)} as published, "
          f"{sum(1 for r in rows if r['p_cor'] < ALPHA)} corrected")

    from bugarach.paths import darkroom, unresolved_message
    dest = Path(a.out) if a.out else darkroom()
    if dest is None:
        print(unresolved_message(), file=sys.stderr)
        return 1

    import holoviews as hv
    import panel as pn
    hv.extension("bokeh")
    layout = build(rows, a.stream, a.width)

    dests = [dest] + ([a.also] if a.also else [])
    for i, dd in enumerate(dests):
        dd.mkdir(parents=True, exist_ok=True)
        html = dd / f"{FIGURE_ID}_{a.stream}.html"
        pn.panel(pn.pane.HoloViews(layout)).save(str(html))
        print(f"wrote {html}")
        if a.png:
            shot = dd / f"{FIGURE_ID}_{a.stream}.png"
            if i == 0:
                if _render_png(html, shot):
                    print(f"wrote {shot}")
            else:
                src = dests[0] / f"{FIGURE_ID}_{a.stream}.png"
                if src.is_file():
                    shot.write_bytes(src.read_bytes())
                    print(f"wrote {shot}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
