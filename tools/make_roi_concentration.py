#!/usr/bin/env python3
"""Where a real field's events actually live, against where the generator puts them.

    python tools/make_roi_concentration.py                     # -> $BUGARACH_DARKROOM
    python tools/make_roi_concentration.py --out DIR           # somewhere else
    python tools/make_roi_concentration.py --numbers-only      # no figure, just the table

Writes `roi_concentration.html` and `roi_concentration.png` — the figure id is
`roi_concentration`, and it is the same on every machine so a claim on the
session board names something unambiguous.

**What it measures.** For the baseline window of every archived slice that has
one, the per-ROI event counts, sorted busiest-first and expressed as a
cumulative share of the recording's events. A perfectly flat field is the
diagonal; a field where a handful of ROIs carry everything bows hard away from
it. The generator's two bench regimes are drawn on the same axes.

**Why it exists.** `docs/generator.md` argued the generator's background is flat
from a *single* slice, which cannot say whether that slice was typical. Tony,
2026-08-15: *"what is generally missing in the simulation is 1-3 highly active
ROIs as shown in the real data. it seems like most read data sets have at least
one."* This is that claim, checked across the archive — see
`docs/todo/2026-08-14-generator-background-model-is-flat.md` for the result and
what it implies for recalibration.

**Baseline windows only** (FOUNDATIONS §9, and Tony 2026-08-14: *"do not use senk
or ttx as sources for the properties of coordination"*). A slice that carries a
treatment region still contributes — but only the events inside its `baseline`
region, and no before/after comparison is computed or drawn, so nothing here is
a treatment result.

Needs `$BUGARACH_DATA_ROOT`; without it the script says so and writes nothing,
because real stores are machine-local (FOUNDATIONS §5) and guessing a path is
worse than not drawing. Output goes to `$BUGARACH_DARKROOM` — the darkroom is
mounted on every machine, so **claim `roi_concentration.*` on
`docs/SESSIONS.md` before running this**.
"""

from __future__ import annotations

import argparse
import os
import sys
import tempfile
from pathlib import Path

import numpy as np

FIGURE_ID = "roi_concentration"
ARCHIVE = "processed_archive/event_store_onset_revised_2v"
STREAM = "fast"

# A window too short or too sparse cannot support a concentration statistic:
# with a handful of events the busiest ROI's share is set by counting noise.
MIN_DURATION_SEC = 300.0
MIN_EVENTS = 20
MIN_ROIS = 8

# "Highly active" needs a threshold, and an absolute rate would just re-measure
# how busy the slice is. Relative to the slice's OWN median ROI, it asks the
# question that matters here: does this field have a few ROIs that dominate it?
HOT_MULTIPLE = 5.0


def baseline_counts(path: Path):
    """Per-ROI event counts inside a slice's baseline region, or None.

    Returns None rather than raising for every reason a slice is unusable, so
    one bad file cannot end a survey of eighty.
    """
    from bugarach.store import load_slice

    try:
        sl = load_slice(path)
    except Exception:                                    # noqa: BLE001
        return None
    reg = next((r for r in sl.regions
                if (r.name or "").strip().lower() == "baseline"), None)
    if reg is None or STREAM not in sl.streams:
        return None
    lo, hi = float(reg.start_sec), float(reg.end_sec)
    if hi - lo < MIN_DURATION_SEC:
        return None
    stream = sl.streams[STREAM]
    counts = []
    for v in (stream.t50rise or stream.locs):
        v = np.asarray(v, dtype=float)
        v = v[np.isfinite(v)]
        counts.append(int(((v >= lo) & (v < hi)).sum()))
    c = np.asarray(counts, dtype=float)
    if c.sum() < MIN_EVENTS or c.size < MIN_ROIS:
        return None
    return c


def concentration(counts: np.ndarray) -> dict:
    """The four numbers, plus the cumulative-share curve they summarise."""
    c = np.sort(np.asarray(counts, dtype=float))[::-1]
    total = c.sum()
    med = float(np.median(c))
    hot = c >= HOT_MULTIPLE * med if med > 0 else c >= HOT_MULTIPLE
    return dict(
        n_roi=int(c.size),
        top1=float(c[0] / total),
        top3=float(c[:3].sum() / total),
        cv=float(c.std(ddof=0) / c.mean()) if c.mean() else float("nan"),
        n_hot=int(hot.sum()),
        rank=np.arange(1, c.size + 1) / c.size,
        share=np.cumsum(c) / total,
    )


def generator_counts(regime: str, seed: int):
    """The same per-ROI counts, off a bench recording."""
    from bugarach import bench

    s, _ = bench.make_recording(regime, seed=seed)
    stream = s.streams["events"]
    return np.asarray(
        [np.isfinite(np.asarray(v, dtype=float)).sum() for v in stream.t50rise],
        dtype=float)


def survey(root: Path, seed: int):
    """Every usable baseline window, plus the generator at both bench regimes."""
    from bugarach.bench import REGIMES

    arc = root / ARCHIVE
    if not arc.is_dir():
        raise SystemExit(f"no archive at {arc}")
    real = []
    for p in sorted(arc.glob("*.mat")):
        c = baseline_counts(p)
        if c is not None:
            real.append((p.stem, concentration(c)))
    if not real:
        raise SystemExit(f"no usable baseline windows under {arc}")
    gen = [(name, concentration(generator_counts(name, seed)))
           for name in REGIMES]
    return real, gen


def summarise(real, gen) -> str:
    """The table, in text so it can travel into a commit message or a todo."""
    def col(key):
        return np.array([m[key] for _, m in real], dtype=float)

    top1, top3, cv, hot = col("top1"), col("top3"), col("cv"), col("n_hot")
    n = len(real)
    lines = [
        f"{n} baseline windows · stream {STREAM!r} · "
        f"≥{MIN_DURATION_SEC:.0f}s, ≥{MIN_EVENTS} events, ≥{MIN_ROIS} ROI",
        "",
        f"{'statistic':<34}{'real (median, IQR)':<28}generator",
    ]
    gen_txt = " / ".join(f"{m['top1']*100:.1f}%" for _, m in gen)
    lines.append(f"{'busiest ROI share of all events':<34}"
                 f"{np.median(top1)*100:>5.0f}%  "
                 f"({np.percentile(top1,25)*100:.0f}–{np.percentile(top1,75)*100:.0f}%)"
                 f"{'':<8}{gen_txt}")
    gen_txt = " / ".join(f"{m['top3']*100:.1f}%" for _, m in gen)
    lines.append(f"{'top three ROIs share':<34}"
                 f"{np.median(top3)*100:>5.0f}%  "
                 f"({np.percentile(top3,25)*100:.0f}–{np.percentile(top3,75)*100:.0f}%)"
                 f"{'':<8}{gen_txt}")
    gen_txt = " / ".join(f"{m['cv']:.2f}" for _, m in gen)
    lines.append(f"{'CV of per-ROI counts':<34}"
                 f"{np.median(cv):>5.2f}  "
                 f"({np.percentile(cv,25):.2f}–{np.percentile(cv,75):.2f})"
                 f"{'':<9}{gen_txt}")
    gen_txt = " / ".join(str(m["n_hot"]) for _, m in gen)
    with_any = int((hot >= 1).sum())
    lines += [
        f"{f'ROIs firing ≥{HOT_MULTIPLE:.0f}× the median ROI':<34}"
        f"{np.median(hot):>5.0f}   (range {hot.min():.0f}–{hot.max():.0f})"
        f"{'':<6}{gen_txt}",
        "",
        f"windows with at least one such ROI: {with_any} of {n} "
        f"({100*with_any/n:.0f}%)",
        f"windows with one to three:          "
        f"{int(((hot >= 1) & (hot <= 3)).sum())} of {n} "
        f"({100*((hot >= 1) & (hot <= 3)).sum()/n:.0f}%)",
    ]
    return "\n".join(lines)


REAL_LINE = "#9a9a9a"
MEDIAN_LINE = "#1f1f1f"
FLAT_LINE = "#7b4a9c"
GEN_COLOURS = ("#e69d00", "#b3261e")


def build(real, gen, width: int):
    """Cumulative share against ROI rank, and the busiest-ROI distribution."""
    import holoviews as hv

    curves = [hv.Curve((m["rank"], m["share"])).opts(
        color=REAL_LINE, alpha=0.30, line_width=1) for _, m in real]
    # one grid so a median across curves of different ROI counts is well defined
    grid = np.linspace(0.0, 1.0, 101)
    stack = np.stack([np.interp(grid, m["rank"], m["share"]) for _, m in real])
    curves.append(hv.Curve((grid, np.median(stack, axis=0))).opts(
        color=MEDIAN_LINE, line_width=3))
    for (_, m), colour in zip(gen, GEN_COLOURS):
        curves.append(hv.Curve((m["rank"], m["share"])).opts(
            color=colour, line_width=3, line_dash="dashed"))
    # the diagonal IS the flat field: every ROI carrying an equal share
    curves.append(hv.Curve(([0, 1], [0, 1])).opts(
        color=FLAT_LINE, line_width=1.5, line_dash="dotted"))

    left = hv.Overlay(curves).opts(
        width=width, height=440, xlim=(0, 1), ylim=(0, 1.02),
        xlabel="ROI rank (busiest → quietest, as a fraction of the population)",
        ylabel="cumulative share of all events", title="", show_legend=False,
        fontsize={"labels": "11pt", "ticks": "10pt"})

    top1 = np.array([m["top1"] for _, m in real], dtype=float)
    edges = np.linspace(0.0, max(0.8, float(top1.max()) * 1.05), 17)
    hist, _ = np.histogram(top1, bins=edges)
    right = hv.Histogram((edges, hist)).opts(
        color="#c9c9c9", line_color="#8a8a8a")
    right = right * hv.VLine(float(np.median(top1))).opts(
        color=MEDIAN_LINE, line_width=3)
    for (_, m), colour in zip(gen, GEN_COLOURS):
        right = right * hv.VLine(m["top1"]).opts(
            color=colour, line_width=3, line_dash="dashed")
    right = right.opts(
        width=int(width * 0.82), height=440,
        xlabel="share of all events held by the single busiest ROI",
        ylabel=f"baseline windows ({len(real)})", title="", show_legend=False,
        fontsize={"labels": "11pt", "ticks": "10pt"})

    header = (
        '<div style="font:13px/1.6 system-ui,sans-serif;color:#222;'
        'max-width:1200px">'
        f'<b>Where the events actually live — {len(real)} baseline windows '
        'against the generator</b><br>'
        f'<span style="color:{REAL_LINE}">grey</span> = one real baseline '
        f'window · <b>black</b> = their median · '
        + ' · '.join(
            f'<span style="color:{c}"><b>dashed</b></span> = generator, '
            f'{name.replace("baseline_", "")} regime'
            for (name, _), c in zip(gen, GEN_COLOURS))
        + f' · <span style="color:{FLAT_LINE}">dotted</span> = a perfectly flat '
        'field, every ROI equal<br>'
        'Baseline windows only — a slice carrying a treatment contributes only '
        'the events inside its <i>baseline</i> region, and no before/after '
        'comparison is drawn.</div>')
    return (left + right).cols(2).opts(shared_axes=False, toolbar=None), header


def main(argv=None):
    p = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--seed", type=int, default=1,
                   help="seed for the generator recordings it is compared to")
    p.add_argument("--width", type=int, default=640)
    p.add_argument("--out", default=None,
                   help="destination directory; default $BUGARACH_DARKROOM")
    p.add_argument("--numbers-only", action="store_true",
                   help="print the table and write nothing")
    p.add_argument("--no-png", dest="png", action="store_false", default=True,
                   help="skip the flat render (needs playwright chromium)")
    args = p.parse_args(argv)

    root = os.environ.get("BUGARACH_DATA_ROOT", "").strip()
    if not root:
        raise SystemExit(
            "BUGARACH_DATA_ROOT is not set — this survey needs the real "
            "archive, and real stores are machine-local. Nothing written.")

    real, gen = survey(Path(root).expanduser(), args.seed)
    table = summarise(real, gen)
    print(table)
    if args.numbers_only:
        return 0

    from bugarach.paths import ENV_VAR, darkroom

    if args.out:
        dest = Path(args.out).expanduser()
        dest.mkdir(parents=True, exist_ok=True)
    else:
        dest = darkroom(create=True)
        if dest is None:
            print(f"\n{ENV_VAR} is not set and --out was not given — writing "
                  "nothing rather than guessing.", file=sys.stderr)
            return 2

    import holoviews as hv
    import panel as pn

    hv.extension("bokeh")
    fig, header = build(real, gen, args.width)
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
                    viewport={"width": 1280, "height": 620},
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
