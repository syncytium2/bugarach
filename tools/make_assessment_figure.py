#!/usr/bin/env python3
"""What the assessor called on real recordings, and how much, before anything else runs.

    python tools/make_assessment_figure.py --folder EXPORT_FOLDER --assess-dir RUN/01_assess \
        --k 3 --show STRONG_ID WEAK_ID [--stream fast] [--out DIR] [--also DIR]

The assessment is the ground the rest of a run stands on — the spec is derived from its
clusters and, when nobody has judged them, they stand in for confirmed events. A report
that quotes its numbers and never shows one of its calls asks the reader to trust what
they could have seen (murderboard 2026-09-07, role 9, blocking). This page shows it:

  A, B · the baseline of two named recordings — a strong one and a weak one — as a raster,
         with the assessor's clusters at K in a lane ABOVE the raster, never on it, each
         cluster a bar from its first participant's onset to its last (CLAUDE.md).
  C    · coordinated events per minute of baseline, per recording, fast and slow, on a
         log axis so an order-of-magnitude gap is a visible gap.
  D    · within-cluster onset spread against each recording's own surrogate null — a
         recording whose spread is wider than its null is one where the assessor found
         no coordination tighter than chance.
  E    · the K arithmetic: 10 % of each field's ROI count, rounded, and the floor.

The clusters drawn are the clusters counted: they are recomputed with the assessor's own
functions on the same baseline window, and the count is asserted against the assessment
file's row. Nothing here measures anything new.
"""
from __future__ import annotations

import argparse
import json
import math
import os
import sys
import tempfile
import warnings
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from bugarach import paths  # noqa: E402
from bugarach.assess import _coact_count, k_from_fraction  # noqa: E402
from bugarach.detect_folder import folder_analysis_windows  # noqa: E402
from bugarach.io import load_folder  # noqa: E402
from make_assessor_calls_figure import cluster_calls  # noqa: E402
from make_group_raster_summary import _shift_stream  # noqa: E402

BIN, MERGE_BINS, WM_FACTOR = 1.0, 2, 1.5      # assess.py's defaults
INK_FAST, INK_SLOW, INK_NULL = "#1f5fa8", "#b5651d", "#999999"


def baseline_trains(s, stream: str):
    """Onsets per ROI inside the baseline window, re-zeroed, as assess_coactivity clips them."""
    _, wins = folder_analysis_windows(s)
    w = next((w for w in wins if (w.label or "").strip().lower() == "baseline"), None)
    if w is None:
        raise SystemExit(f"{s.slice_id}: no baseline window")
    st = s.streams[stream]
    trains = []
    for v in st.t50rise:
        v = np.asarray(v, float).ravel()
        v = v[np.isfinite(v) & (v >= w.win_start) & (v <= w.win_end)] - w.win_start
        trains.append(np.sort(v))
    return trains, (float(w.win_start), float(w.win_end)), st


def assessor_calls(trains, dur, k):
    n_bins = max(1, int(math.ceil(dur / BIN)))
    counts = _coact_count(trains, dur, BIN, n_bins)
    return cluster_calls(trains, counts, k=k, bin_width=BIN, merge_bins=MERGE_BINS, wm_factor=WM_FACTOR)


def rows_at_k(assess_json: Path, k: int):
    a = json.loads(assess_json.read_text())
    return {r["slice_id"]: r for r in a["rows"] if int(r["K"]) == k}


def build(folder: Path, assess_dir: Path, k: int, show: list[str], stream: str, *, width=1040):
    import holoviews as hv
    from bugarach.ui.diagnostic import lane_panel, raster_panel
    hv.extension("bokeh")

    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        slices = {s.slice_id: s for s in load_folder(folder)}
    fast = rows_at_k(assess_dir / "assessment_fast.json", k)
    slow = rows_at_k(assess_dir / "assessment_slow.json", k)
    ids = sorted(slices)

    panels = []
    letters = iter("ABCDEFGH")
    for sid in show:
        s = slices[sid]
        trains, (ws, we), st = baseline_trains(s, stream)
        dur = we - ws
        calls = assessor_calls(trains, dur, k)
        n_row = fast[sid]["clusters_permin"] * dur / 60.0 if stream == "fast" else slow[sid]["clusters_permin"] * dur / 60.0
        assert abs(len(calls) - n_row) < 0.51, (sid, len(calls), n_row)
        letter = next(letters)
        # Start the drawn extent slightly BEFORE zero. A cluster at t = 0 lands on the
        # axis spine and disappears — and on 20260812_381, which has two clusters in
        # twenty minutes, the one at t = 0 is half of the recording's evidence and the
        # one the report goes on to discuss. Found in review, 2026-09-07.
        ext = (-8.0, dur)
        onsets = np.asarray([c["t0"] for c in calls])
        widths = np.asarray([c["t1"] - c["t0"] for c in calls])
        lane = lane_panel({f"assessor K={k}": (onsets, widths)}, ext=ext, width=width, row_px=26)
        # Re-zero the stream to the baseline start so the raster and the lane share x.
        # `_shift_stream` is the same operation written in the same run, with the reason
        # `width` must not move and the reason each field is assigned on its own line.
        shifted = _shift_stream(st, ws)
        ras = raster_panel(shifted, ext=ext, width=width, height=max(265, 4 * st.n_rois + 40),
                           name=f"{letter} · {sid}",
                           ydim=f"roi_{sid}", ticks="minimal")
        lane.opts(xaxis=None, toolbar=None)
        ras.opts(toolbar=None)
        panels += [lane, ras]

    # C · clusters per minute, fast and slow, log x
    ylab = [(i, sid) for i, sid in enumerate(ids[::-1])]
    ypos = {sid: i for i, sid in ylab}
    els = []
    for sid in ids:
        y = ypos[sid]
        for rows, ink, dy in ((fast, INK_FAST, 0.15), (slow, INK_SLOW, -0.15)):
            v = max(rows[sid]["clusters_permin"], 0.02)
            els.append(hv.Scatter([(v, y + dy)]).opts(color=ink, size=9))
    c = hv.Overlay(els).opts(width=380, height=26 * len(ids) + 70, toolbar=None, show_legend=False,
                             logx=True, xlim=(0.02, 5), yticks=ylab, ylim=(-0.7, len(ids) - 0.3),
                             xlabel="C · coordinated events/min of baseline (log)", ylabel="",
                             show_grid=False)
    # D · onset spread observed vs null
    els = []
    for sid in ids:
        y = ypos[sid]
        for rows, ink, dy in ((fast, INK_FAST, 0.15), (slow, INK_SLOW, -0.15)):
            r = rows[sid]
            if r.get("jit_obs") is not None and r.get("jit_null") is not None:
                els.append(hv.Curve([(r["jit_null"], y + dy), (r["jit_obs"], y + dy)]).opts(color=ink, line_width=1.5))
                els.append(hv.Scatter([(r["jit_obs"], y + dy)]).opts(color=ink, size=9))
                els.append(hv.Scatter([(r["jit_null"], y + dy)]).opts(color="white", line_color=INK_NULL,
                                                                        line_width=2, size=9))
    d = hv.Overlay(els).opts(width=340, height=26 * len(ids) + 70, toolbar=None, show_legend=False,
                             yaxis=None, ylim=(-0.7, len(ids) - 0.3), xlim=(0, 0.7),
                             xlabel="D · onset spread, s (filled: seen; open: null)",
                             show_grid=False)
    # E · the K arithmetic
    els = []
    kmax = 0
    for sid in ids:
        y = ypos[sid]
        n = int(fast[sid]["n_roi"])
        kf = k_from_fraction(0.10, n)
        kmax = max(kmax, kf, k)
        els.append(hv.Scatter([(kf, y)]).opts(color="#444", size=9))
        els.append(hv.Text(kf, y + 0.30, f"10 % of {n} → {kf}", halign="center",
                           fontsize=8).opts(color="#444"))
    # The floor goes UNDER the dots and clear of the text. Drawn over them it struck
    # through two labels and hid the fill of every dot already sitting at K.
    els.insert(0, hv.VLine(k).opts(color="#b00", line_dash="dashed", line_width=1.5, alpha=0.7))
    e = hv.Overlay(els).opts(width=320, height=26 * len(ids) + 70, toolbar=None, show_legend=False,
                             yaxis=None, ylim=(-0.7, len(ids) - 0.1), xlim=(0, kmax + 1.6),
                             xlabel=f"E · K at 10 % (dot) and the floor {k} (dashed)", show_grid=False)
    bottom = hv.Layout([c, d, e]).cols(3).opts(shared_axes=False, toolbar=None)
    return panels, bottom, fast, slow


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--folder", required=True, type=Path)
    ap.add_argument("--assess-dir", required=True, type=Path, help="holds assessment_fast.json and assessment_slow.json")
    ap.add_argument("--k", type=int, required=True)
    ap.add_argument("--show", nargs="+", required=True, help="recording ids to draw, strong first")
    ap.add_argument("--stream", default="fast")
    ap.add_argument("--out", type=Path, default=None, help="destination (default: the darkroom)")
    ap.add_argument("--also", type=Path, default=None)
    ap.add_argument("--stem", default="assessment_overview")
    a = ap.parse_args(argv)

    import panel as pn
    from make_generator_figures import _write

    panels, bottom, fast, slow = build(a.folder, a.assess_dir, a.k, a.show, a.stream)
    if a.out is None:
        root = paths.darkroom(create=True)
        if root is None:
            print(paths.unresolved_message(), file=sys.stderr)
            return 2
        a.out = root / "assessment"
    a.out.mkdir(parents=True, exist_ok=True)

    def chip(colour, text, hollow=False):
        style = (f"border:2px solid {colour};background:white" if hollow else f"background:{colour}")
        return (f"<span style='display:inline-block;width:11px;height:11px;{style};border-radius:50%;"
                f"vertical-align:-1px;margin-right:5px'></span><span style='color:{colour}'>{text}</span>")

    header = pn.pane.HTML(
        f"<div style='font:13px system-ui,sans-serif;color:#111;max-width:1030px'>"
        f"<b style='font-size:16px'>what the assessor called, at K = {a.k}</b> &nbsp;—&nbsp; "
        f"A, B: the {a.stream} baseline of {' and '.join(a.show)}, the assessor's clusters as bars in the "
        f"lane above the raster (first to last participant onset); nothing is drawn on the raster.<br>"
        f"C–E: all six recordings. {chip(INK_FAST, 'fast')} &nbsp; {chip(INK_SLOW, 'slow')} &nbsp; "
        f"{chip(INK_NULL, 'surrogate null', hollow=True)}. A cluster is ≥ K ROIs with onsets in one "
        f"1-second bin, gathered within ±1.5 s; 1000 circular-shift surrogates per recording; baseline only."
        f"<div style='margin:4px 0 0;color:#777;font-size:11px'>{a.folder.name} · {a.assess_dir.name}/"
        f"assessment_{{fast,slow}}.json</div></div>")
    items = [header] + [pn.pane.HoloViews(p) for p in panels] + [pn.pane.HoloViews(bottom)]
    _write(pn.Column(*items), a.out, a.stem, png=True)
    if a.also:
        a.also.mkdir(parents=True, exist_ok=True)
        for f in a.out.glob(f"{a.stem}.*"):
            with tempfile.TemporaryDirectory() as td:
                tmp = Path(td) / f.name
                tmp.write_bytes(f.read_bytes())
                os.replace(tmp, a.also / f.name)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
