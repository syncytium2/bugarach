#!/usr/bin/env python3
"""The distribution of `roiRate` in real baseline windows, against the generator's.

    python tools/make_roi_rate_distribution.py                 # -> $BUGARACH_DARKROOM
    python tools/make_roi_rate_distribution.py --out DIR       # somewhere else
    python tools/make_roi_rate_distribution.py --numbers-only  # table, no figure

Figure id `roi_rate_distribution`, the same on every machine, so a claim on the
session board names something unambiguous.

**`roiRate`** is this project's existing quantity and this script does not invent
another: *events inside the window divided by the window's duration, per ROI, in
Hz* — the definition `measure_coordination_timescale.m` uses and
`bugarach.bench.MEASURED_PROVENANCE` quotes (`roiRate = events/win_dur`). Rates
are printed in **mHz** purely because baseline values run to a few thousandths of
a Hz; they are the same number.

**What it is for.** `bg_rate_hz` gives *every* ROI the same rate. This measures
whether real baseline windows look like that, on the axis the calibration itself
was taken on. They do not, and the shape of the disagreement is the point: the
calibration used the **mean** `roiRate` of a right-skewed distribution and then
applied it homogeneously, so the generated field is simultaneously far busier
than a typical ROI and missing the high-rate ROIs entirely. See
`docs/todo/2026-08-14-generator-background-model-is-flat.md`.

**Why not interval distributions.** Tony, 2026-08-15: those are the tool for
postsynaptic currents, and that is the reason they do not transfer here. A PSC
recording gives one cell hundreds of events, so its intervals are well sampled.
A baseline window gives the *median* ROI under one event — 35% of ROIs fire not
at all — so most ROIs have no interval to measure. Requiring five intervals per
ROI keeps 37% of them and drops precisely the quiet ones the finding is about,
and the surviving CV of intervals does not separate the two anyway (real median
1.21; generator 1.15 busy, 1.50 quiet, inflated by the planted events sitting on
top of its background). An interval-based check would return a false pass. The
rate axis is the one that discriminates, and it is already the project's unit.

**Baseline windows only** (FOUNDATIONS §9; Tony, 2026-08-14: *"do not use senk or
ttx as sources for the properties of coordination"*). A slice carrying a
treatment contributes only the events inside its `baseline` region, and no
before/after comparison is computed or drawn.

Needs `$BUGARACH_DATA_ROOT`; without it the script says so and writes nothing,
because real stores are machine-local (FOUNDATIONS §5) and guessing a path is
worse than not drawing. Output goes to `$BUGARACH_DARKROOM` — the darkroom is
mounted on every machine, so **claim `roi_rate_distribution.*` on
`docs/SESSIONS.md` before running this**.
"""

from __future__ import annotations

import argparse
import os
import sys
import tempfile
from pathlib import Path

import numpy as np

FIGURE_ID = "roi_rate_distribution"
ARCHIVE = "processed_archive/event_store_onset_revised_2v"
STREAM = "fast"

# A window too short or too sparse cannot support a rate distribution: with a
# handful of events the spread across ROIs is set by counting noise.
MIN_DURATION_SEC = 300.0
MIN_EVENTS = 20
MIN_ROIS = 8

# A zero-rate ROI has no place on a log axis but is a real and common
# observation — a third of them — so it is drawn at a floor and labelled rather
# than dropped. Well below the smallest nonzero rate a window can resolve
# (one event in the longest window).
ZERO_FLOOR_MHZ = 0.05


def baseline_rates(sl):
    """(slice id, per-ROI roiRate in Hz) inside the baseline region, or None.

    Returns None rather than raising for every reason a recording is unusable,
    so one bad file cannot end a survey of eighty.

    Takes a loaded recording rather than a path, because the caller now reads an
    export folder in one go. That folder is the corpus the lab approved; a store
    holds every recording ever processed, withdrawn ones included. The
    interquartile range this figure reports is quoted as the project's
    difficulty axis, so which recordings are in it is not a detail.
    """
    reg = next((r for r in sl.regions
                if (r.name or "").strip().lower() == "baseline"), None)
    if reg is None or STREAM not in sl.streams:
        return None
    lo, hi = float(reg.start_sec), float(reg.end_sec)
    dur = hi - lo
    if dur < MIN_DURATION_SEC:
        return None
    stream = sl.streams[STREAM]
    rates = []
    for v in (stream.t50rise or stream.locs):
        v = np.asarray(v, dtype=float)
        v = v[np.isfinite(v)]
        rates.append(int(((v >= lo) & (v < hi)).sum()) / dur)
    r = np.asarray(rates, dtype=float)
    if r.sum() * dur < MIN_EVENTS or r.size < MIN_ROIS:
        return None
    return r


def generator_rates(regime: str, seeds=(1, 2, 3)):
    """The same quantity off bench recordings, pooled over seeds."""
    from bugarach import bench

    dur = float(bench.BENCH_RECORDING["duration_sec"])
    out = []
    for seed in seeds:
        s, _ = bench.make_recording(regime, seed=seed)
        for v in s.streams["events"].t50rise:
            v = np.asarray(v, dtype=float)
            out.append(int(np.isfinite(v).sum()) / dur)
    return np.asarray(out, dtype=float)


def survey(folder: Path, seeds):
    from bugarach.bench import REGIMES
    from bugarach.io import load_folder

    per_slice = []
    for sl in load_folder(folder):
        r = baseline_rates(sl)
        if r is not None:
            per_slice.append((str(sl.slice_id), r))
    if not per_slice:
        raise SystemExit(f"no usable baseline windows in {folder}")
    gen = [(name, generator_rates(name, seeds)) for name in REGIMES]
    return per_slice, gen


def summarise(per_slice, gen) -> str:
    """The table, in text so it can travel into a commit message or a todo."""
    pooled = np.concatenate([r for _, r in per_slice])
    means = np.array([r.mean() for _, r in per_slice])
    medians = np.array([np.median(r) for _, r in per_slice])

    def mhz(a):
        return f"{np.median(a)*1000:6.1f}  ({np.percentile(a,25)*1000:.1f}–" \
               f"{np.percentile(a,75)*1000:.1f})"

    lines = [
        f"roiRate = events/win_dur, per ROI, in mHz · stream {STREAM!r} · "
        f"{len(per_slice)} baseline windows, {pooled.size} ROIs",
        "",
        f"{'':<46}{'median (IQR)':<24}max",
        f"{'real, across all ROIs':<46}{mhz(pooled):<24}{pooled.max()*1000:.0f}",
        f"{'real, slice MEAN roiRate':<46}{mhz(means):<24}"
        f"{means.max()*1000:.0f}     <- what bg_rate_hz was calibrated to",
        f"{'real, slice MEDIAN roiRate':<46}{mhz(medians):<24}"
        f"{medians.max()*1000:.0f}",
    ]
    for name, r in gen:
        lines.append(f"{'generator, ' + name:<46}{mhz(r):<24}{r.max()*1000:.0f}")
    ratio = means / np.where(medians > 0, medians, np.nan)
    lines += [
        "",
        f"ROIs firing zero times in their baseline window: "
        f"{100*(pooled == 0).mean():.0f}%  (generator: "
        + ", ".join(f"{100*(r == 0).mean():.0f}%" for _, r in gen) + ")",
        f"within a slice, mean/median roiRate: median {np.nanmedian(ratio):.1f}× "
        "— a symmetric distribution gives 1.0",
    ]
    return "\n".join(lines)


REAL_LINE = "#1f1f1f"
GEN_COLOURS = ("#e69d00", "#b3261e")
CALIB_LINE = "#7b4a9c"


def _ecdf(values_mhz):
    x = np.sort(np.where(values_mhz > 0, values_mhz, ZERO_FLOOR_MHZ))
    return x, np.arange(1, x.size + 1) / x.size


def build(per_slice, gen, width: int):
    import holoviews as hv

    pooled = np.concatenate([r for _, r in per_slice]) * 1000.0
    means = np.array([r.mean() for _, r in per_slice]) * 1000.0
    medians = np.array([np.median(r) for _, r in per_slice]) * 1000.0

    items = []
    x, y = _ecdf(pooled)
    items.append(hv.Curve((x, y)).opts(color=REAL_LINE, line_width=3))
    for (name, r), colour in zip(gen, GEN_COLOURS):
        gx, gy = _ecdf(r * 1000.0)
        items.append(hv.Curve((gx, gy)).opts(
            color=colour, line_width=3, line_dash="dashed"))
    items.append(hv.VLine(float(np.median(means))).opts(
        color=CALIB_LINE, line_width=2, line_dash="dotted"))
    left = hv.Overlay(items).opts(
        width=width, height=440, logx=True, ylim=(0, 1.02),
        xlim=(ZERO_FLOOR_MHZ * 0.8, max(pooled.max(), 1000.0) * 1.2),
        xlabel="roiRate (mHz, log scale)",
        ylabel="fraction of ROIs at or below this rate",
        title="", show_legend=False,
        fontsize={"labels": "11pt", "ticks": "10pt"})

    hi = max(means.max(), medians.max()) * 1.1
    right = (hv.Curve(([0, hi], [0, hi])).opts(
                 color="#9a9a9a", line_width=1.5, line_dash="dotted")
             * hv.Scatter((medians, means)).opts(
                 color=REAL_LINE, size=7, alpha=0.7))
    for (name, r), colour in zip(gen, GEN_COLOURS):
        right = right * hv.Scatter(([np.median(r) * 1000.0],
                                    [r.mean() * 1000.0])).opts(
            color=colour, size=13, marker="diamond", line_color="white",
            line_width=1.5)
    right = right.opts(
        width=int(width * 0.82), height=440, xlim=(0, hi), ylim=(0, hi),
        xlabel="slice MEDIAN roiRate (mHz)", ylabel="slice MEAN roiRate (mHz)",
        title="", show_legend=False,
        fontsize={"labels": "11pt", "ticks": "10pt"})

    zero_pct = 100 * (pooled == 0).mean()
    header = (
        '<div style="font:13px/1.6 system-ui,sans-serif;color:#222;'
        'max-width:1240px">'
        f'<b>roiRate across {len(per_slice)} baseline windows, against the '
        'generator</b><br>'
        '<b>Left</b> — every ROI, cumulative. '
        f'<span style="color:{REAL_LINE}"><b>black</b></span> = real · '
        + ' · '.join(
            f'<span style="color:{c}"><b>dashed</b></span> = generator, '
            f'{name.replace("baseline_", "")}'
            for (name, _), c in zip(gen, GEN_COLOURS))
        + f' · <span style="color:{CALIB_LINE}">dotted</span> = the mean '
        'roiRate the calibration was taken from. '
        f'The {zero_pct:.0f}% of ROIs that fired zero times are drawn at the '
        f'left edge ({ZERO_FLOOR_MHZ} mHz), not dropped.<br>'
        '<b>Right</b> — one point per window: its mean roiRate against its '
        'median. A symmetric distribution would sit on the dotted line; every '
        'window sits above it, which is what a right-skewed field looks like. '
        'Diamonds are the generator, which sits on the line by construction.'
        '<br>roiRate = events/win_dur (Hz per ROI), the definition '
        '<i>measure_coordination_timescale.m</i> uses; shown in mHz. Baseline '
        'regions only — no before/after comparison is drawn.</div>')
    return (left + right).cols(2).opts(shared_axes=False, toolbar=None), header


def main(argv=None):
    p = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--seeds", type=int, nargs="+", default=[1, 2, 3],
                   help="seeds for the generator recordings compared against")
    p.add_argument("--width", type=int, default=640)
    p.add_argument("--folder", default=None,
                   help="export folder holding the real corpus "
                        "(docs/export_folder_spec.md)")
    p.add_argument("--out", default=None,
                   help="destination directory; default $BUGARACH_DARKROOM")
    p.add_argument("--numbers-only", action="store_true",
                   help="print the table and write nothing")
    p.add_argument("--no-png", dest="png", action="store_false", default=True,
                   help="skip the flat render (needs playwright chromium)")
    args = p.parse_args(argv)

    if not args.folder:
        raise SystemExit(
            "--folder is required: this survey needs the real corpus, and the "
            "corpus is an export folder (docs/export_folder_spec.md). It used "
            "to walk a .mat archive under BUGARACH_DATA_ROOT, which is every "
            "recording ever processed rather than the ones the lab kept — and "
            "the interquartile range printed below is quoted as this project's "
            "difficulty axis. Nothing written.")

    per_slice, gen = survey(Path(args.folder).expanduser(), tuple(args.seeds))
    table = summarise(per_slice, gen)
    print(table)
    if args.numbers_only:
        return 0

    from bugarach.paths import darkroom, unresolved_message

    if args.out:
        dest = Path(args.out).expanduser()
        dest.mkdir(parents=True, exist_ok=True)
    else:
        dest = darkroom(create=True)
        if dest is None:
            print("\n" + unresolved_message(), file=sys.stderr)
            return 2

    import holoviews as hv
    import panel as pn

    hv.extension("bokeh")
    fig, header = build(per_slice, gen, args.width)
    page = pn.Column(pn.pane.HTML(header),
                     pn.pane.HoloViews(fig),
                     pn.pane.HTML(f"<pre style='font:12px/1.45 ui-monospace,"
                                  f"monospace;color:#222'>{table}</pre>"))

    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td) / "page.html"
        page.save(str(tmp))
        html = dest / f"{FIGURE_ID}.html"
        os.replace(tmp, html)
    written = [html]
    if args.png:
        shot = dest / f"{FIGURE_ID}.png"
        if _render_png(html, shot):
            written.append(shot)
        else:
            print("(no PNG: pip install playwright && python -m playwright "
                  "install chromium, or pass --no-png)", file=sys.stderr)
    print("\nwrote " + "\n      ".join(str(w) for w in written))
    return 0


def _render_png(html_path: Path, png_path: Path, *, wait_ms: int = 3000,
                scale: int = 2) -> bool:
    """Flatten the page to a PNG. False rather than raising when the browser is
    unavailable — a missing screenshot must not cost you the measurement, which
    has already been printed by the time this runs."""
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        return False
    try:
        with tempfile.TemporaryDirectory() as td:
            tmp = Path(td) / "shot.png"
            with sync_playwright() as pw:
                browser = pw.chromium.launch()
                page = browser.new_page(
                    viewport={"width": 1280, "height": 640},
                    device_scale_factor=scale)
                page.goto(html_path.resolve().as_uri())
                page.wait_for_timeout(wait_ms)      # bokeh draws after load
                page.screenshot(path=str(tmp), full_page=True)
                browser.close()
            os.replace(tmp, png_path)
        return True
    except Exception as exc:                        # noqa: BLE001
        print(f"(PNG render failed: {type(exc).__name__}: {exc})",
              file=sys.stderr)
        return False


if __name__ == "__main__":
    raise SystemExit(main())
