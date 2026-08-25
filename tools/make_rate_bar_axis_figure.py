#!/usr/bin/env python3
"""Two scoring rules, opposite answers: the multiplicative bar across the background axis.

    python tools/make_rate_bar_axis_figure.py --also docs/learned

Figure id `rate_bar_across_background`, the same on every machine.

**The claim under test.** `rate_detect` fires where `rate − context ≥ 5 Hz`, an
**additive** offset, where cell-averaging CFAR multiplies: `θ = α · μ̂`. Forks §3
measured the multiplicative alternative on `baseline_quiet`, 3 seeds — F1 0.636 →
0.667, probe firings 2.0 → 0.0 — and item 8 of the revision plan predicts *why*:
an additive bar has no constant-false-alarm property, so its effective threshold
ratio `1 + excess/μ̂` is a function of the background.

**A one-point measurement is exactly what this project just stopped accepting**
(`BACKGROUND_GRID`, 2026-08-24), so this sweeps the axis and sweeps **both**
mechanisms over their own knob at every point — comparing a swept mechanism
against a fixed-knob one credits the sweep, not the mechanism.

**What it found is in front of the question it asked.** The two scoring rules in
this repo disagree about which mechanism wins, and nothing decides between them:

- `BenchResult.precision` is `n_hit / n_scored` and deliberately **excludes** the
  promiscuity probe — a block with nothing planted — because the probe is severe
  enough to dominate any precision it enters.
- `tools/probe_rate_mechanism.py`, which produced forks §3's evidence, pools by
  hand as `n_hit / n_detected`, which **includes** it, under a docstring saying it
  mirrors `bench.evaluate`. It does not. That is the exact fork `pool_scores`' own
  docstring was written to stop — *"the rule for what counts forked in silence.
  Import this."* — reappearing in a tool written after it.

Measured across the grid: **multiplicative wins 1 of 7 points with the probe
excluded and 5 of 7 with it included.** Same runs, same seeds, same knob grids.

Neither rule is simply right. The probe-blind one picks additive thresholds that
fire up to 92 times in an empty block and cannot see it
(`docs/todo/2026-08-16-promiscuity-probe-cannot-fail.md`); the probe-inclusive one
lets how hard the probe was set drive the headline. **The revision plan already
says this must be settled before the re-fit** — Phase 2, *"or the campaign
re-selects operating points against a score that cannot see promiscuity"*. This is
what walking into that looks like.

On the original question, for what it is worth: the best α ranges 4× across the
grid, so there is no single α to calibrate under either rule, and forks §3's
reason for leaving the default alone still stands.

**Nothing here changes a default and nothing here changes a scorer.** `rate.py`
already carries both flags and is not edited.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np

FIGURE_ID = "rate_bar_across_background"

INK = "#16202b"
GUIDE = "#9a9a9a"
ADD_C = "#b03a48"
MUL_C = "#1f6fb4"

SEEDS = (1, 2, 3)
REGIME = "baseline_quiet"

#: Wide on purpose. Forks §3: *"the α grid must be wide — the optimum sat at 15–20
#: on this bench and an initial grid topping out at 8 put it at the edge."* An
#: optimum at the edge is not an optimum (`bench.EdgeOfRange`), and this grid has
#: room above and below what that probe found.
ALPHA_GRID = (1.5, 2.0, 3.0, 5.0, 8.0, 12.0, 16.0, 20.0, 26.0, 34.0)

#: The additive bar's own knob, swept for the same reason: comparing a swept
#: mechanism against a fixed-knob one would credit the sweep, not the mechanism.
EXCESS_GRID = (0.5, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 8.0, 12.0)


def _probe_f1(r) -> float:
    """F1 with the promiscuity probe folded into precision — the OTHER rule.

    `BenchResult.precision` is `n_hit / n_scored` and deliberately **excludes**
    the probe window, because the probe is severe enough to dominate any
    precision it enters: fold it in and *"the headline stops measuring the
    detector and starts measuring how hard the probe was set"*.

    `tools/probe_rate_mechanism.py` — the tool that produced forks §3's evidence
    — pools by hand as `n_hit / n_detected`, which **includes** it, under a
    docstring saying it mirrors `bench.evaluate`. It does not. That is the exact
    fork `pool_scores`' own docstring was written to stop (*"the rule for what
    counts forked in silence. Import this."*), reappearing in a tool written
    after it.

    Both rules are computed here rather than one being called correct, because
    which one is right is an open question — see
    `docs/todo/2026-08-16-promiscuity-probe-cannot-fail.md` — and they give
    opposite answers to the question this figure asks.
    """
    p = r.n_hit / r.n_detected if r.n_detected else float("nan")
    rec = r.recall
    if not np.isfinite(p) or not np.isfinite(rec) or (p + rec) == 0:
        return float("nan")
    return 2 * p * rec / (p + rec)


def _sweep(gen, mode, grid):
    """Every knob on the grid, with both F1 rules and the probe count."""
    from bugarach.bench import evaluate

    rows = []
    for v in grid:
        kw = ({"threshold_mode": "multiplicative", "threshold_alpha": float(v)}
              if mode == "multiplicative" else
              {"excess_threshold_hz": float(v)})
        r = evaluate("rate", REGIME, SEEDS, gen=gen, **kw)
        rows.append({"knob": float(v), "bench_f1": r.f1,
                     "probe_f1": _probe_f1(r), "hot_fa": r.hot_fa,
                     "recall": r.recall, "precision": r.precision})
    return rows


def _pick(rows, key, grid):
    best = max(rows, key=lambda d: (d[key] if np.isfinite(d[key]) else -1.0))
    return {**best, "at_edge": best["knob"] in (grid[0], grid[-1])}


def measure() -> dict:
    from bugarach.bench import BACKGROUND_GRID, REGIMES

    rates = list(BACKGROUND_GRID)
    out = {"rates": rates,
           "quiet": REGIMES["baseline_quiet"]["bg_rate_hz"],
           "busy": REGIMES["baseline_busy"]["bg_rate_hz"],
           "additive": {}, "multiplicative": {}}

    for rate in rates:
        gen = {"bg_rate_hz": float(rate)}
        for mode, grid in (("additive", EXCESS_GRID),
                           ("multiplicative", ALPHA_GRID)):
            rows = _sweep(gen, mode, grid)
            out[mode][rate] = {
                "rows": rows,
                "by_bench": _pick(rows, "bench_f1", grid),
                "by_probe": _pick(rows, "probe_f1", grid),
            }
    return out


def spread(d: dict, rates, rule="by_bench") -> float:
    key = "bench_f1" if rule == "by_bench" else "probe_f1"
    f1s = [d[r][rule][key] for r in rates]
    return max(f1s) - min(f1s)


def build(m: dict, width: int):
    import holoviews as hv

    x = [r * 1000.0 for r in m["rates"]]
    marks = [m["quiet"] * 1000.0, m["busy"] * 1000.0]

    def guides():
        return [hv.VLine(r).opts(color=GUIDE, line_dash="dashed", line_width=1)
                for r in marks]

    # ---- Panel A: the same runs under both scoring rules. The inversion.
    items = guides()
    series = [
        ("additive", "by_bench", "bench_f1", ADD_C, "solid",
         "additive · probe EXCLUDED"),
        ("multiplicative", "by_bench", "bench_f1", MUL_C, "solid",
         "multiplicative · probe EXCLUDED"),
        ("additive", "by_probe", "probe_f1", ADD_C, "dashed",
         "additive · probe INCLUDED"),
        ("multiplicative", "by_probe", "probe_f1", MUL_C, "dashed",
         "multiplicative · probe INCLUDED"),
    ]
    for mode, rule, key, colour, dash, label in series:
        y = [m[mode][r][rule][key] for r in m["rates"]]
        items.append(hv.Curve((x, y), label=label).opts(
            color=colour, line_width=2.2, line_dash=dash))
        items.append(hv.Scatter((x, y)).opts(
            color=colour, size=6, line_color=INK, line_width=0.4))
    panel_a = hv.Overlay(items).opts(
        width=width // 2, height=420, logx=True,
        xlabel="background rate (mHz per ROI) · dashed: the two REGIMES",
        ylabel="F1, each mechanism at its own best knob under that rule",
        ylim=(0.0, 1.0),
        fontsize={"xlabel": "9pt", "ylabel": "9pt", "ticks": "8pt",
                  "legend": "8pt"},
        legend_position="bottom_left", legend_cols=2,
        toolbar=None, show_grid=True)

    # ---- Panel B: what the probe-blind rule buys with its win
    ritems = guides() + [hv.HLine(1.0).opts(color=GUIDE, line_width=1)]
    for mode, colour, label in (("additive", ADD_C, "additive"),
                                ("multiplicative", MUL_C, "multiplicative")):
        y = [max(m[mode][r]["by_bench"]["hot_fa"], 0.05) for r in m["rates"]]
        ritems.append(hv.Curve((x, y), label=label).opts(
            color=colour, line_width=2.4))
        ritems.append(hv.Scatter((x, y)).opts(
            color=colour, size=8, line_color=INK, line_width=0.5))
    panel_b = hv.Overlay(ritems).opts(
        width=width // 2, height=420, logx=True, logy=True,
        xlabel="background rate (mHz per ROI)",
        ylabel="firings in a block with NOTHING planted, at the knob the "
               "probe-blind rule chose",
        fontsize={"xlabel": "9pt", "ylabel": "8pt", "ticks": "8pt",
                  "legend": "9pt"},
        legend_position="top_left", toolbar=None, show_grid=True)

    return hv.Layout([panel_a, panel_b]).cols(2).opts(
        shared_axes=False, toolbar=None)


def header_html(m: dict) -> str:
    rates = m["rates"]
    bench_wins = sum(1 for r in rates
                     if m["multiplicative"][r]["by_bench"]["bench_f1"]
                     > m["additive"][r]["by_bench"]["bench_f1"])
    probe_wins = sum(1 for r in rates
                     if m["multiplicative"][r]["by_probe"]["probe_f1"]
                     > m["additive"][r]["by_probe"]["probe_f1"])
    add_hot = [m["additive"][r]["by_bench"]["hot_fa"] for r in rates]
    mul_hot = [m["multiplicative"][r]["by_bench"]["hot_fa"] for r in rates]
    alphas = [m["multiplicative"][r]["by_bench"]["knob"] for r in rates]
    a_ratio = max(alphas) / min(alphas)
    rows = "".join(
        f"<tr><td style='padding:2px 12px 2px 0'>{r*1000:.1f}</td>"
        f"<td style='padding:2px 12px 2px 0;text-align:right'>"
        f"{m['additive'][r]['by_bench']['bench_f1']:.3f}"
        f"<span style='color:#5c6773'> @{m['additive'][r]['by_bench']['knob']:g}</span></td>"
        f"<td style='padding:2px 12px 2px 0;text-align:right'>"
        f"<b>{m['additive'][r]['by_bench']['hot_fa']:.0f}</b></td>"
        f"<td style='padding:2px 12px 2px 0;text-align:right'>"
        f"{m['multiplicative'][r]['by_bench']['bench_f1']:.3f}"
        f"<span style='color:#5c6773'> @&alpha;={m['multiplicative'][r]['by_bench']['knob']:g}</span></td>"
        f"<td style='padding:2px 12px 2px 0;text-align:right'>"
        f"<b>{m['multiplicative'][r]['by_bench']['hot_fa']:.0f}</b></td>"
        f"<td style='padding:2px 12px 2px 0;text-align:right'>"
        f"{m['additive'][r]['by_probe']['probe_f1']:.3f}</td>"
        f"<td style='padding:2px 0;text-align:right'>"
        f"{m['multiplicative'][r]['by_probe']['probe_f1']:.3f}</td></tr>"
        for r in rates)
    return f"""
<div style="font:13px/1.5 -apple-system,Segoe UI,sans-serif;color:{INK};
            max-width:66rem;margin:0 auto 0.5rem">
<p><b>This set out to ask whether the multiplicative bar holds across the
background axis. It found something in front of that question: the two scoring
rules in this repo give opposite answers, and nothing decides between them.</b></p>

<p><code>BenchResult.precision</code> is <code>n_hit / n_scored</code> and
deliberately <b>excludes</b> the promiscuity probe — a block with nothing planted
in it — because the probe is severe enough to dominate any precision it enters.
<code>tools/probe_rate_mechanism.py</code>, which produced forks §3's evidence,
pools by hand as <code>n_hit / n_detected</code>, which <b>includes</b> it, under a
docstring saying it mirrors <code>bench.evaluate</code>. It does not. That is the
exact fork <code>pool_scores</code>' own docstring was written to stop — <i>"the
rule for what counts forked in silence. Import this."</i> — reappearing in a tool
written after it.</p>

<table style="border-collapse:collapse;font-size:12px">
<tr style="border-bottom:1px solid #c8d6e4">
  <th style="text-align:left;padding-right:12px" rowspan="2">bg<br>mHz</th>
  <th colspan="4" style="text-align:center;padding-right:12px">probe EXCLUDED
    (<code>bench.evaluate</code>)</th>
  <th colspan="2" style="text-align:center">probe INCLUDED (forks §3's tool)</th></tr>
<tr style="border-bottom:1px solid #c8d6e4">
  <th style="text-align:right;padding-right:12px">additive F1</th>
  <th style="text-align:right;padding-right:12px">its empty-block firings</th>
  <th style="text-align:right;padding-right:12px">mult. F1</th>
  <th style="text-align:right;padding-right:12px">its firings</th>
  <th style="text-align:right;padding-right:12px">additive F1</th>
  <th style="text-align:right">mult. F1</th></tr>
{rows}
</table>

<p><b>The inversion.</b> With the probe excluded, multiplicative wins at
<b>{bench_wins} of {len(rates)}</b> points. With it included, <b>{probe_wins} of
{len(rates)}</b>. Same runs, same knob grids, same seeds — only the rule for what
counts as a false positive differs.</p>

<p><b>Panel B is why the probe-blind rule is not simply the right one.</b> It picks
additive knobs that fire up to <b>{max(add_hot):.0f}</b> times in a block with
<i>nothing planted in it</i> (against multiplicative's {max(mul_hot):.0f}), and its
F1 cannot see that — which is
<code>docs/todo/2026-08-16-promiscuity-probe-cannot-fail.md</code> in action:
<i>"its firings leave both numerator and denominator."</i> A campaign that selects
operating points this way selects for promiscuity and cannot report it. <b>The
revision plan already says this must be fixed before the re-fit</b>; this figure is
what that warning looks like when you walk into it.</p>

<p><b>One asymmetry survives the open question, and it is the useful part.</b>
Multiplicative's two curves in panel A lie exactly on top of each other — its F1 is
<b>the same number under both rules</b>, because it never fires in the empty block
and so the rules cannot disagree about it. Additive's two curves are
{max(abs(m['additive'][r]['by_bench']['bench_f1']
        - m['additive'][r]['by_probe']['probe_f1']) for r in rates):.3f} apart at
their widest. So whichever way the promiscuity question is settled, the
multiplicative bar's score does not move — which is a weaker claim than "it wins"
and a much more robust one.</p>

<p><b>What the original question got, for what it is worth.</b> The multiplicative
bar's best &alpha; ranges <b>{a_ratio:.1f}&times;</b> across the grid, so it is not
background-invariant on this bench and there is no single &alpha; to calibrate —
under either rule. Whatever else is true, forks §3's <i>"switching the default
before Phase 4 would ship an uncalibrated operating point"</i> still holds.</p>

<p style="color:#5c6773">{len(SEEDS)} seeds per point, base recording
<code>{REGIME}</code>, tolerance 1.5&nbsp;s. &alpha; over
{min(ALPHA_GRID):g}&ndash;{max(ALPHA_GRID):g}; additive threshold over
{min(EXCESS_GRID):g}&ndash;{max(EXCESS_GRID):g}&nbsp;Hz. Both mechanisms swept at
every point, so neither is credited a sweep the other did not get.
<b>No default moves and no scorer is changed here</b> — deciding how promiscuity
enters the score is the open question this feeds.</p>
</div>"""


def _render_png(html_path: Path, png_path: Path, *, wait_ms: int = 2500,
                width: int = 1500, height: int = 1000) -> bool:
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
    p.add_argument("--width", type=int, default=1240)
    p.add_argument("--out", default=None,
                   help="destination; defaults to the darkroom")
    p.add_argument("--also", type=Path, default=None,
                   help="second destination, e.g. docs/learned")
    p.add_argument("--no-png", dest="png", action="store_false", default=True)
    a = p.parse_args()

    print("sweeping both bars across the background grid, under both rules…")
    m = measure()
    print(f"  {'bg mHz':>7}  {'probe EXCLUDED: add / mult (empty-block firings)':<48}"
          f"  {'probe INCLUDED: add / mult':<26}")
    for r in m["rates"]:
        a_b, m_b = m["additive"][r]["by_bench"], m["multiplicative"][r]["by_bench"]
        a_p, m_p = m["additive"][r]["by_probe"], m["multiplicative"][r]["by_probe"]
        print(f"  {r*1000:7.1f}  {a_b['bench_f1']:.3f}@{a_b['knob']:<4g}"
              f"({a_b['hot_fa']:>5.0f}) / {m_b['bench_f1']:.3f}@a{m_b['knob']:<4g}"
              f"({m_b['hot_fa']:>5.0f})"
              f"        {a_p['probe_f1']:.3f} / {m_p['probe_f1']:.3f}")
    bw = sum(1 for r in m["rates"]
             if m["multiplicative"][r]["by_bench"]["bench_f1"]
             > m["additive"][r]["by_bench"]["bench_f1"])
    pw = sum(1 for r in m["rates"]
             if m["multiplicative"][r]["by_probe"]["probe_f1"]
             > m["additive"][r]["by_probe"]["probe_f1"])
    print(f"  multiplicative wins {bw}/{len(m['rates'])} with the probe excluded, "
          f"{pw}/{len(m['rates'])} with it included")

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
