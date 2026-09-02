#!/usr/bin/env python3
"""The Cossart K scan under four aggregators, and the argmax that moves between them.

    python tools/make_k_scan_figure.py --also docs/learned/cossart_transfer

Figure id `k_scan_cossart`, the same on every machine.

`docs/todo/2026-09-01-the-k12-peak-does-not-reproduce.md` asks a question that
reads like arithmetic — *which summary statistic of this scan yields K=12?* — and
turns out to have a curve as its answer.

**Panel A** is `coact_excess` across `K=3…24` under four aggregations of the same
531 rows. **Panel B** is the per-slice argmax histogram, which is the statistic
`80b8db6` named. **Panel C** is the bootstrap: resample the 59 recordings, ask
each aggregator for its winner, and count how often it names the same K twice.

**What it shows, and it is not what either side of the argument expected.** The
two blind reviewers are right — the per-slice argmax median and mode are **16**,
not the 12 the commit message claims, and this reproduces their distribution
exactly. But 12 is not thereby undefended: the pooled *mean*, the 10% trimmed
mean and the mean per-slice rank all peak there. And under resampling it is the
**median-based** reading that will not hold still. So the correction is narrower
and more awkward than "12 was wrong": the number outlives the reason given for
it, and the honest statement is that this scan does not identify an argmax.

**This measures and decides nothing.** Choosing K is Tony's and is on the
`docs/MILESTONES.md` Open list; `derive_spec --k` still refuses. No spec is
re-derived, no transfer is re-run, and the only input is
`docs/learned/assessment_cossart.json`, which is already in git.
"""
from __future__ import annotations

import argparse
import json
import random
import statistics as st
import sys
from collections import Counter, defaultdict
from pathlib import Path

FIGURE_ID = "k_scan_cossart"

INK = "#16202b"
GUIDE = "#9a9a9a"
MUTED = "#5c6773"

#: One colour per aggregator, used in all three panels so a reader tracks a
#: criterion across them by hue alone.
COLOURS = {
    "median": "#b03a48",
    "mean": "#1f6fb4",
    "trim10": "#2e8b57",
    "rank": "#7a4fa3",
}
LABELS = {
    "median": "pooled median",
    "mean": "pooled mean",
    "trim10": "pooled 10% trimmed mean",
    "rank": "mean per-slice rank",
}

METRIC = "coact_excess"
N_BOOT = 2000
BOOT_SEED = 0

#: The two numbers the argument is between. Panel A marks both.
CLAIMED = 12
POOLED_MEDIAN_PEAK = 16

DEFAULT_SOURCE = Path("docs/learned/assessment_cossart.json")


def _trimmed_mean(values: list[float], p: float = 0.10) -> float:
    v = sorted(values)
    c = int(len(v) * p)
    return st.mean(v[c: len(v) - c])


def _mean_rank(per_slice: dict[str, dict[int, float]], ks: list[int],
               slices: list[str]) -> dict[int, float]:
    """Mean of each K's within-slice rank, 1 (worst) to len(ks) (best).

    Scale-free by construction, which is why it is here: `coact_excess` spans
    two orders of magnitude across these recordings, so a pooled mean is a
    handful of large slices voting and a pooled median is one slice voting.
    This asks each recording the same question and weights them equally.
    """
    total = {k: 0.0 for k in ks}
    for s in slices:
        order = sorted(ks, key=lambda k: per_slice[s][k])
        for i, k in enumerate(order):
            total[k] += i + 1
    return {k: total[k] / len(slices) for k in ks}


def _argmax(series: dict[int, float]) -> int:
    """Largest value, ties going to the smaller K."""
    best = max(series.values())
    return min(k for k, v in series.items() if v == best)


def measure(source: Path) -> dict:
    doc = json.loads(source.read_text())
    ks = list(doc["k_scan"])

    per_slice: dict[str, dict[int, float]] = defaultdict(dict)
    for row in doc["rows"]:
        per_slice[row["slice_id"]][row["K"]] = row[METRIC]
    slices = sorted(per_slice)

    # Every slice must carry every K, or a "pooled median across 59" is a
    # median across whichever subset happened to be defined at that K.
    ragged = [s for s in slices if sorted(per_slice[s]) != sorted(ks)]
    if ragged:
        raise SystemExit(
            f"{len(ragged)} slice(s) do not span the whole K scan: {ragged[:3]}")

    curves = {
        "median": {k: st.median([per_slice[s][k] for s in slices]) for k in ks},
        "mean": {k: st.mean([per_slice[s][k] for s in slices]) for k in ks},
        "trim10": {k: _trimmed_mean([per_slice[s][k] for s in slices]) for k in ks},
        "rank": _mean_rank(per_slice, ks, slices),
    }

    # The statistic the commit message named, computed the way it reads.
    argmaxes = [_argmax(per_slice[s]) for s in slices]
    hist = Counter(argmaxes)

    rng = random.Random(BOOT_SEED)
    wins = {name: Counter() for name in curves}
    for _ in range(N_BOOT):
        draw = [rng.choice(slices) for _ in slices]
        vals = {k: [per_slice[s][k] for s in draw] for k in ks}
        wins["median"][_argmax({k: st.median(vals[k]) for k in ks})] += 1
        wins["mean"][_argmax({k: st.mean(vals[k]) for k in ks})] += 1
        wins["trim10"][_argmax({k: _trimmed_mean(vals[k]) for k in ks})] += 1
        wins["rank"][_argmax(_mean_rank(per_slice, ks, draw))] += 1

    return {
        "ks": ks,
        "n_slices": len(slices),
        "n_rows": len(doc["rows"]),
        "curves": curves,
        "argmax": {name: _argmax(c) for name, c in curves.items()},
        "hist": {k: hist.get(k, 0) for k in ks},
        "hist_median": st.median(sorted(argmaxes)),
        "hist_mode": hist.most_common(1)[0][0],
        "hist_mean": st.mean(argmaxes),
        "boot": {name: {k: wins[name][k] / N_BOOT for k in ks} for name in wins},
        "store": doc.get("store", "?"),
        "n_surrogates": doc.get("n_surrogates", "?"),
        "source": str(source),
    }


def build(m: dict, width: int):
    import holoviews as hv

    ks = m["ks"]
    half, third = width // 2, width // 3

    # ---- Panel A: the four aggregations, each on its own scale.
    #
    # Rank runs 1..9 and excess runs 90..160, so they cannot share an axis and
    # must not be forced onto one. Each curve is rescaled to its own span; the
    # y-axis says so, and the marked argmaxes are what the panel is for.
    items = []
    for k, dash in ((CLAIMED, "dashed"), (POOLED_MEDIAN_PEAK, "dotted")):
        items.append(hv.VLine(k).opts(color=GUIDE, line_dash=dash, line_width=1))
    for name in ("median", "mean", "trim10", "rank"):
        series = m["curves"][name]
        lo, hi = min(series.values()), max(series.values())
        y = [(series[k] - lo) / (hi - lo) for k in ks]
        c = COLOURS[name]
        items.append(hv.Curve((ks, y), label=LABELS[name]).opts(
            color=c, line_width=2.2))
        items.append(hv.Scatter((ks, y)).opts(color=c, size=6, line_color=None))
        peak = m["argmax"][name]
        items.append(hv.Scatter(([peak], [y[ks.index(peak)]])).opts(
            color=c, size=15, marker="diamond", line_color=INK, line_width=0.8))
    panel_a = hv.Overlay(items).opts(
        width=half, height=380,
        xlabel="K · dashed 12, the claimed peak · dotted 16, the pooled median's",
        ylabel="coact_excess, scaled per curve · diamond = argmax",
        ylim=(-0.06, 1.12), xticks=[(k, str(k)) for k in ks],
        fontsize={"xlabel": "9pt", "ylabel": "9pt", "ticks": "8pt",
                  "legend": "8pt"},
        legend_position="bottom_right", legend_cols=1,
        toolbar=None, show_grid=True)

    # ---- Panel B: the statistic the commit message named.
    #
    # Drawn on the same numeric K axis as A and C rather than as categories:
    # the scan grid is uneven (3,4,6,8,10,12,16,20,24), and evenly spacing it
    # would put a third of the mass to the right of 16 without showing that
    # those bars are twice as far apart as the ones on the left.
    bars = hv.Rectangles(
        [(k - 0.55, 0, k + 0.55, m["hist"][k]) for k in ks]).opts(
        color=MUTED, line_color=INK, line_width=0.6)
    panel_b = hv.Overlay([bars] + [
        hv.VLine(m["hist_median"]).opts(
            color=COLOURS["median"], line_dash="dashed", line_width=1.6),
        hv.VLine(CLAIMED).opts(color=GUIDE, line_dash="dashed", line_width=1),
    ]).opts(
        width=third, height=380,
        xlabel=f"per-slice argmax K · red: median and mode, both {m['hist_mode']}",
        ylabel=f"recordings ({m['n_slices']})",
        xticks=[(k, str(k)) for k in ks], xlim=(1.5, 25.5),
        ylim=(0, max(m["hist"].values()) * 1.12),
        fontsize={"xlabel": "9pt", "ylabel": "9pt", "ticks": "8pt"},
        toolbar=None, show_grid=True)

    # ---- Panel C: does the winner hold still under resampling?
    citems = []
    for name in ("median", "mean", "trim10", "rank"):
        b = m["boot"][name]
        c = COLOURS[name]
        citems.append(hv.Curve((ks, [100 * b[k] for k in ks]),
                               label=LABELS[name]).opts(color=c, line_width=2.2))
        citems.append(hv.Scatter((ks, [100 * b[k] for k in ks])).opts(
            color=c, size=6, line_color=None))
    panel_c = hv.Overlay(citems).opts(
        width=third, height=380,
        xlabel=f"K · {N_BOOT} bootstrap resamples of the {m['n_slices']} recordings",
        ylabel="% of resamples in which this K wins",
        ylim=(-4, 100), xticks=[(k, str(k)) for k in ks],
        fontsize={"xlabel": "9pt", "ylabel": "9pt", "ticks": "8pt",
                  "legend": "8pt"},
        legend_position="top_right", legend_cols=1,
        toolbar=None, show_grid=True)

    return hv.Layout([panel_a, panel_b, panel_c]).cols(3).opts(
        shared_axes=False, toolbar=None)


def header_html(m: dict) -> str:
    rows = "".join(
        f"<tr><td style='padding:2px 14px 2px 0'>"
        f"<span style='color:{COLOURS[n]}'>&#9632;</span> {LABELS[n]}</td>"
        f"<td style='padding:2px 14px 2px 0;text-align:right'><b>"
        f"K&nbsp;=&nbsp;{m['argmax'][n]}</b></td>"
        f"<td style='padding:2px 0;text-align:right'>"
        f"{100 * m['boot'][n][m['argmax'][n]]:.0f}%</td></tr>"
        for n in ("median", "mean", "trim10", "rank"))
    med_peak = m["argmax"]["median"]
    return f"""
<div style="font:13px/1.5 -apple-system,Segoe UI,sans-serif;color:{INK};
            max-width:70rem;margin:0 auto 0.5rem">
<p><b>The same {m['n_rows']} rows, four ways of summarising them, and the peak
moves.</b> `80b8db6` gave <i>"their per-slice median argmax is K=12"</i> as the
reason the cross-lab transfer was re-run at 12. Panel B is that statistic, and it
is <b>{m['hist_mode']}</b> — reproducing what two blind reviewers computed
independently. The reason given for K=12 does not survive.</p>

<p><b>The number does, and not for the reason anyone wrote down.</b> Three
aggregations of the same scan peak at 12: the pooled mean, the 10% trimmed mean,
and the mean per-slice rank. Panel C is why that matters more than the count of
criteria on each side — resample the {m['n_slices']} recordings and ask each
criterion for its winner again. The median-based reading, the one that produces
{med_peak}, names the same K in only
<b>{100 * m['boot']['median'][med_peak]:.0f}%</b> of resamples. Mean per-slice
rank names 12 in <b>{100 * m['boot']['rank'][12]:.0f}%</b>.</p>

<table style="border-collapse:collapse;font-size:12px;margin:0 0 0.8rem">
<tr style="border-bottom:1px solid #c8d6e4">
  <th style="text-align:left;padding-right:14px">aggregation of coact_excess</th>
  <th style="text-align:right;padding-right:14px">argmax</th>
  <th style="text-align:right">holds under resampling</th></tr>
{rows}
</table>

<p><b>So the honest statement is neither 12 nor 16.</b> Panel A is a broad
non-monotonic plateau in which four values of K sit inside a few percent of each
other, and which one tops it is a decision about aggregation rather than a
measurement. A third reviewer said exactly this and was right. The correction
owed to <code>current_export.toml</code>, the transfer README and
<code>docs/MILESTONES.md</code> is not <i>"12 should have been 16"</i>; it is
that this scan does not identify an argmax, and the sentence in the transfer
README reading <i>"was never an open question"</i> is the one that has to go.</p>

<p style="color:{MUTED}">Store <code>{m['store']}</code>,
{m['n_slices']} recordings &times; {len(m['ks'])} values of K,
{m['n_surrogates']} surrogates, from <code>{m['source']}</code>.
Bootstrap seed {BOOT_SEED}, {N_BOOT} resamples, ties to the smaller K.
<b>This decides nothing:</b> choosing K is on the <code>MILESTONES.md</code> Open
list, <code>derive_spec --k</code> still refuses, and no spec was re-derived and
no transfer re-run to make this figure.</p>
</div>"""


def _render_png(html_path: Path, png_path: Path, *, wait_ms: int = 2500,
                width: int = 1560, height: int = 1000) -> bool:
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
            pg.screenshot(path=str(png_path), full_page=True)
            b.close()
        return True
    except Exception as exc:                                   # noqa: BLE001
        print(f"(PNG render failed: {type(exc).__name__}: {exc})", file=sys.stderr)
        return False


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--width", type=int, default=1500)
    p.add_argument("--source", type=Path, default=DEFAULT_SOURCE,
                   help=f"assessment JSON (default {DEFAULT_SOURCE})")
    p.add_argument("--out", default=None,
                   help="destination; defaults to the darkroom")
    p.add_argument("--also", type=Path, default=None,
                   help="second destination, e.g. docs/learned/cossart_transfer")
    p.add_argument("--no-png", dest="png", action="store_false", default=True)
    a = p.parse_args()

    print(f"reading {a.source}…")
    m = measure(a.source)
    print(f"  {m['n_rows']} rows, {m['n_slices']} recordings, K in {m['ks']}")
    for n in ("median", "mean", "trim10", "rank"):
        k = m["argmax"][n]
        print(f"  {LABELS[n]:<24} argmax K={k:<3} "
              f"holds in {100 * m['boot'][n][k]:.0f}% of resamples")
    print(f"  per-slice argmax: median {m['hist_median']}, "
          f"mode {m['hist_mode']}, mean {m['hist_mean']:.2f} · "
          + " ".join(f"{k}:{m['hist'][k]}" for k in m["ks"]))

    from bugarach.paths import darkroom, unresolved_message
    dest = Path(a.out) if a.out else darkroom()
    if dest is None:
        print(unresolved_message(), file=sys.stderr)
        return 1

    import holoviews as hv
    import panel as pn
    hv.extension("bokeh")
    layout = build(m, a.width)

    dests = [dest] + ([a.also] if a.also else [])
    for i, d in enumerate(dests):
        d.mkdir(parents=True, exist_ok=True)
        html = d / f"{FIGURE_ID}.html"
        pn.panel(pn.Column(pn.pane.HTML(header_html(m)),
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
