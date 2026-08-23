#!/usr/bin/env python3
"""Are the coordinated cells a *module*? Both streams, against each graph's own surrogates.

    python tools/make_modularity_figure.py --fast docs/learned/eval_modularity_null_fast.csv \\
        --slow docs/learned/eval_modularity_null_slow.csv --also docs/learned

Figure id `assembly_modularity`, the same on every machine.

**This is the other instrument, and it is the one that makes the assembly answer a
negative.** The membership test in `assembly_closed` asks whether *who participates*
departs from uniform, and it fires almost everywhere. That is a positive, and on its own it
is compatible with a field of recurring groups. Modularity asks the complementary question
— are there groups of cells more coupled to each other than to the rest of the field — and
finding none is what turns "participation is uneven" into "uneven, but not organised into
assemblies".

**What is plotted is z, not Q.** Louvain finds *some* partition in any graph, and it finds
higher-scoring partitions in sparser, weaker ones — so a raw Q is uninterpretable without
its own null. Each slice's Q is therefore compared against 200 jitter surrogates of *that
slice*, which hold node count, event counts and sparsity fixed and differ only in timing.
`z` is how many null standard deviations the observed Q sits above its own surrogate mean.
Zero is "exactly as modular as timing alone predicts".

**The threshold is the 95th percentile of a slice's own surrogates**, so under the null
about 5% of slices should clear it by chance. That 5% is the line the observed rates are
read against, and it is why 3 of 81 is not a small positive — it is chance.

Reads the two CSVs produced by interface2's `eval_modularity_null`; computes nothing.
"""
from __future__ import annotations

import argparse
import csv
import math
import sys

import numpy as np
from pathlib import Path

FIGURE_ID = "assembly_modularity"

FAST_C = "#111111"
SLOW_C = "#1f6fb4"
GUIDE = "#9a9a9a"
ABOVE = "#b03a48"

#: The test calls a slice modular when its Q clears the 95th percentile of its own
#: surrogates, so this is the rate structureless data produces.
NOMINAL = 0.05


def _finite(v) -> bool:
    """True only for a real number — `nan`, `NaN`, `` and None all mean untestable."""
    try:
        return np.isfinite(float(v))
    except (TypeError, ValueError):
        return False


def load(path: Path) -> list[dict]:
    with open(path) as fh:
        return [r for r in csv.DictReader(fh)]


def summarise(rows: list[dict]) -> dict:
    """Per-slice (z, above-null) pairs, kept together on purpose.

    The two must travel as a pair. `above_null_Q` is ``Q_obs > 95th percentile of
    that slice's surrogates`` — it is NOT ``z > 0``, and colouring the strip by
    the sign of z would mark ~5x as many points as the count in the label. An
    earlier draft of this figure did exactly that.
    """
    def _testable(r) -> bool:
        # Prefer the explicit column where the producer supplies one; fall back to
        # "is the statistic finite". The string check alone was case-sensitive and
        # let a lowercase `nan` through as a number — which would have put NaNs in
        # the median and counted an untestable recording in the denominator, the
        # exact defect this figure exists to correct.
        if "defined" in r:
            return str(r["defined"]).strip() in ("1", "True", "true")
        try:
            return np.isfinite(float(r["z_Q"])) and np.isfinite(float(r["above_null_Q"]))
        except (TypeError, ValueError):
            return False

    # TWO populations, and conflating them put NaN into a sort and corrupted the
    # median. `scored` is every recording the test could decide — that is the
    # denominator of the RATE. `pairs` is the subset with a finite z, which is what
    # can be drawn: z is undefined when the surrogates have no spread, and the
    # recording still has a verdict.
    scored = [r for r in rows if _testable(r)]
    pairs = sorted((float(r["z_Q"]), float(r["above_null_Q"]))
                   for r in scored if _finite(r.get("z_Q")))
    z = [p_[0] for p_ in pairs]
    k = sum(1 for r in scored if float(r["above_null_Q"]) == 1)
    n = len(scored)
    return {"pairs": pairs, "z": z, "k": k, "n": n,
            "n_plotted": len(pairs),
            "rate": (k / n) if n else float("nan"),
            "median_z": z[len(z) // 2] if z else float("nan"),
            "ci": wilson(k, n)}


def wilson(k: int, n: int) -> tuple[float, float]:
    if n == 0:
        return (float("nan"), float("nan"))
    p, zc = k / n, 1.96
    den = 1 + zc * zc / n
    c = (p + zc * zc / (2 * n)) / den
    h = zc * math.sqrt(p * (1 - p) / n + zc * zc / (4 * n * n)) / den
    return max(0.0, c - h), min(1.0, c + h)


def build(fast: dict, slow: dict, width: int):
    import holoviews as hv
    import numpy as np

    # ---- A: every slice's z, one row per stream --------------------------------
    # A strip rather than a histogram: with ~80 slices per stream the individual
    # points are legible, and the reader can see there is no cluster on the right
    # rather than having to trust a binning choice.
    items = [hv.VLine(0).opts(color=GUIDE, line_width=1.5, line_dash="dotted")]
    ticks = []
    for i, (label, s, col) in enumerate((("fast", fast, FAST_C), ("slow", slow, SLOW_C))):
        y = 1 - i
        ticks.append((y, f"{label}\n{s['k']}/{s['n']} above null"))
        zs = np.array([p_[0] for p_ in s["pairs"]])
        # deterministic vertical spread; no RNG, so the figure is reproducible
        jit = (np.arange(len(zs)) % 7 - 3) * 0.035
        # By the TEST's own verdict, never by the sign of z — see `summarise`.
        above = np.array([p_[1] == 1 for p_ in s["pairs"]])
        for mask, colour, size in ((~above, col, 7), (above, ABOVE, 9)):
            if mask.any():
                items.append(hv.Scatter((zs[mask], y + jit[mask])).opts(
                    color=colour, size=size, alpha=0.8,
                    line_color="white", line_width=0.7))
        # A median marker per row. It carries information — where the bulk of the
        # distribution sits — and it also DE-RASTERIZES the panel: two rows of marks
        # on a horizontal axis read as a spike raster to anyone fluent in one, which
        # is the dominant idiom in this field and in this project's own viewer, and a
        # raster has no per-row summary glyph. The murderboard rule is to name the
        # chart an image resembles before reading its axis labels; this one resembled
        # the wrong chart, and this is the cheapest honest fix.
        # White fill, thick stream-coloured edge: a same-coloured diamond among
        # same-coloured dots is present but not legible, and presence is not the
        # check — identification is.
        items.append(hv.Scatter(([float(np.median(zs))], [y])).opts(
            color="#ffffff", size=17, marker="diamond",
            line_color=col, line_width=2.4))
    a = hv.Overlay(items).opts(
        width=int(width * 0.62), height=330, ylim=(-0.6, 1.6),
        yticks=ticks, invert_yaxis=False,
        xlabel="observed modularity minus its own surrogate mean, in null SDs  (z)",
        ylabel="A · one dot per recording, diamond = median", title="", show_legend=False,
        fontsize={"labels": "11pt", "ticks": "9pt"})

    # ---- B: the rate, against the rate chance produces --------------------------
    bars = [("fast", fast["rate"]), ("slow", slow["rate"])]
    # The guide is named in the AXIS LABEL rather than by a Text glyph: a text
    # annotation on a categorical axis needs an x coordinate, and giving it a
    # numeric one invented a phantom "0.5" category and shifted the bars.
    b = hv.Bars(bars, kdims=["stream"], vdims=["rate"]).opts(
        width=int(width * 0.34), height=330, ylim=(0, 0.16),
        color=hv.dim("stream").categorize({"fast": FAST_C, "slow": SLOW_C}),
        line_color="white", line_width=1,
        xlabel="", ylabel="B · above null   (dotted: chance, 5%)",
        title="", show_legend=False,
        fontsize={"labels": "10pt", "ticks": "9pt"})
    b = b * hv.HLine(NOMINAL).opts(color=GUIDE, line_width=1.5, line_dash="dotted")

    return (a + b).cols(2).opts(shared_axes=False, toolbar=None), ""


def _render_png(html_path: Path, png_path: Path, *, wait_ms: int = 2500,
                width: int = 1320, height: int = 430) -> bool:
    try:
        from playwright.sync_api import sync_playwright
    except Exception as exc:                                   # noqa: BLE001
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
    except Exception as exc:                                   # noqa: BLE001
        print(f"(PNG render failed: {type(exc).__name__}: {exc})", file=sys.stderr)
        return False


def main(argv=None):
    p = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--fast", type=Path, required=True)
    p.add_argument("--slow", type=Path, required=True)
    p.add_argument("--width", type=int, default=1240)
    p.add_argument("--out", default=None,
                   help="destination directory; default $BUGARACH_DARKROOM")
    p.add_argument("--also", type=Path, default=None)
    p.add_argument("--no-png", dest="png", action="store_false", default=True)
    a = p.parse_args(argv)

    for label, path in (("fast", a.fast), ("slow", a.slow)):
        rows = load(path)
        dropped = [r for r in rows if not _finite(r.get("Q_obs"))]
        if dropped:
            # `above_null_Q` is `double(Q_obs > q_hi)`, and NaN > x is false — so a
            # slice too sparse for Louvain to score lands in the CSV as a 0 and reads
            # as "tested, not modular". It was not tested. Leaving it in the
            # denominator is the same confusion this project refuses everywhere else:
            # undefined is not negative.
            print(f"{label}: excluding {len(dropped)} recording(s) with no computable "
                  f"Q (n_active "
                  f"{', '.join(r['n_active'] for r in dropped)}) — undefined, not negative")
    fast, slow = summarise(load(a.fast)), summarise(load(a.slow))
    for label, s in (("fast", fast), ("slow", slow)):
        extra = ("" if s["n_plotted"] == s["n"] else
                 f"  [{s['n'] - s['n_plotted']} scored but z undefined, not drawn]")
        print(f"{label}: {s['k']}/{s['n']} above null = {s['rate']*100:.1f}% "
              f"(95% CI {s['ci'][0]*100:.1f}-{s['ci'][1]*100:.1f}), "
              f"median z {s['median_z']:+.2f}{extra}")

    from bugarach.paths import darkroom, unresolved_message
    dest = Path(a.out) if a.out else darkroom()
    if dest is None:
        print(unresolved_message(), file=sys.stderr)
        return 1

    import holoviews as hv
    import panel as pn
    hv.extension("bokeh")
    layout, header = build(fast, slow, a.width)

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
