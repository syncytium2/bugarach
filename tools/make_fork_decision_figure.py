#!/usr/bin/env python3
"""Decision 1 drawn: fork the assessor's excess, or keep parity and caveat it.

    python tools/make_fork_decision_figure.py --also docs/learned

Figure id `assess_fork_decision`, the same on every machine.

The null test (`docs/todo/2026-08-24-the-null-leaks-and-the-excess-is-mostly-selection.md`)
established that the coactivity excess is mostly selection rule. It left the
decision open and listed three uncosted remedies. **This costs the first one**, so
the choice is between two measured outcomes rather than between a defect and a
principle.

**CURRENT (parity-held).** Select the bins where the observed count reaches K,
sum `obs - null_mean` over those bins.

**CORRECTED (the fork on offer).** Do exactly the same thing to every surrogate,
each selecting on *itself*, and subtract the median surrogate's excess. It is the
standard remedy for a selection-biased statistic and it reuses the ensemble that
is already being computed — no new sampling, no new parameter.

Panel A is what each reports against K, with and without planted events. Panel B
is the same twelve planted events measured at two backgrounds, which is the
comparison a treatment contrast has to make.

**Nothing here changes `assess.py`.** The corrected estimator is computed in this
tool precisely so the figure can show the consequence without a session
pre-empting Tony's call. If the fork is taken it lands in `assess.py` behind a
flag defaulting to current behaviour, like every other mechanism change
(`docs/forks.md` §1).
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np

FIGURE_ID = "assess_fork_decision"

INK = "#16202b"
GUIDE = "#9a9a9a"
ZERO = "#2a7f3f"
CUR_C = "#b03a48"
COR_C = "#1f6fb4"

DUR = 1800.0
N_ROI = 40
BIN = 1.0
N_SUR = 300
WIN_MIN = DUR / 60.0
KS = (3, 4, 5, 6, 8)

QUIET_HZ = 0.0052
BUSY_HZ = 0.0190

N_PLANTED = 12
PLANT_ROIS = 8
PLANT_JITTER = 0.30


def independent(rate: float, seed: int):
    rng = np.random.default_rng(seed)
    return [np.sort(rng.uniform(0.0, DUR, size=rng.poisson(rate * DUR)))
            for _ in range(N_ROI)]


def plant(trains, seed: int, n: int = N_PLANTED):
    """The same twelve events wherever this is called: same seed, same times."""
    rng = np.random.default_rng(10_000 + seed)
    out = [t.copy() for t in trains]
    times: list[float] = []
    while len(times) < n:
        t = float(rng.uniform(120.0, DUR - 120.0))
        if all(abs(t - u) > 60.0 for u in times):
            times.append(t)
    for t in sorted(times):
        for r in rng.choice(len(out), size=PLANT_ROIS, replace=False):
            out[r] = np.sort(np.append(out[r], t + rng.normal(0, PLANT_JITTER)))
    return out, np.asarray(sorted(times))


def both_estimators(trains, ks=KS, n_sur=N_SUR, seed=20260722) -> dict:
    """Current and corrected, off ONE surrogate ensemble.

    Built together on purpose: the corrected estimator's whole claim is that it
    needs no extra sampling, so computing it from a second ensemble would be
    quietly costing it something it does not cost.
    """
    from bugarach.assess import _coact_count

    n_bins = int(np.ceil(DUR / BIN))
    obs = _coact_count(trains, DUR, BIN, n_bins)

    rng = np.random.RandomState(seed)
    sur = np.empty((n_sur, n_bins))
    for i in range(n_sur):
        off = rng.random_sample(len(trains)) * DUR
        sur[i] = _coact_count(
            [np.mod(v + off[r], DUR) if v.size else v
             for r, v in enumerate(trains)], DUR, BIN, n_bins)
    nm = sur.mean(axis=0)

    out = {}
    for K in ks:
        bk = obs >= K
        current = float(obs[bk].sum() - nm[bk].sum()) / WIN_MIN
        sur_ex = np.array([float((s[s >= K] - nm[s >= K]).sum()) / WIN_MIN
                           for s in sur])
        out[K] = {"current": current,
                  "corrected": current - float(np.median(sur_ex)),
                  "sur_med": float(np.median(sur_ex))}
    return out


def measure() -> dict:
    cases = {}
    for label, rate, planted in (("busy_null", BUSY_HZ, False),
                                 ("busy_planted", BUSY_HZ, True),
                                 ("quiet_null", QUIET_HZ, False),
                                 ("quiet_planted", QUIET_HZ, True)):
        tr = independent(rate, 1)
        if planted:
            tr, _ = plant(tr, 2)
        cases[label] = both_estimators(tr)
    return cases


def build(m: dict, width: int):
    import holoviews as hv

    ks = list(KS)

    # ---- Panel A: what each estimator reports against K, at the busy background
    items = [hv.HLine(0.0).opts(color=ZERO, line_width=2)]
    series = [
        ("busy_planted", "current", CUR_C, "solid", "current · 12 planted"),
        ("busy_null", "current", CUR_C, "dashed", "current · nothing planted"),
        ("busy_planted", "corrected", COR_C, "solid", "corrected · 12 planted"),
        ("busy_null", "corrected", COR_C, "dashed", "corrected · nothing planted"),
    ]
    for case, est, colour, dash, label in series:
        y = [m[case][k][est] for k in ks]
        items.append(hv.Curve((ks, y), label=label).opts(
            color=colour, line_width=2.4, line_dash=dash))
        items.append(hv.Scatter((ks, y)).opts(
            color=colour, size=8, line_color=INK, line_width=0.5))
    panel_a = hv.Overlay(items).opts(
        width=width // 2, height=420,
        xlabel="K · the minimum participating ROIs, which is the decision",
        ylabel="excess co-active ROI·events/min",
        fontsize={"xlabel": "9pt", "ylabel": "9pt", "ticks": "8pt",
                  "legend": "8pt"},
        legend_position="top_right", toolbar=None, show_grid=True)

    # ---- Panel B: the same twelve events at two backgrounds
    bars = []
    for est, est_label in (("current", "current"), ("corrected", "corrected")):
        for case, bg_label in (("quiet_planted", "quiet 5.2 mHz"),
                               ("busy_planted", "busy 19.0 mHz")):
            bars.append((est_label, bg_label, m[case][3][est]))
    panel_b = hv.Bars(bars, kdims=["estimator", "background"],
                      vdims=["excess"]).opts(
        width=width // 2, height=420, multi_level=False,
        cmap=["#7fa9d0", "#2c5f8a"],
        xlabel="", ylabel="excess at K = 3 · the SAME 12 planted events",
        fontsize={"xlabel": "9pt", "ylabel": "9pt", "ticks": "8pt",
                  "legend": "9pt"},
        legend_position="top_left", toolbar=None, show_grid=True)

    return hv.Layout([panel_a, panel_b]).cols(2).opts(
        shared_axes=False, toolbar=None)


def header_html(m: dict) -> str:
    bn, bp = m["busy_null"], m["busy_planted"]
    qp = m["quiet_planted"]
    cur_ratio = bp[3]["current"] / qp[3]["current"]
    cor_ratio = bp[3]["corrected"] / qp[3]["corrected"]
    cur_k = [bp[k]["current"] for k in KS]
    cor_k = [bp[k]["corrected"] for k in KS]
    cur_fall = 1.0 - min(cur_k[:4]) / max(cur_k[:4])
    cor_fall = 1.0 - min(cor_k[:4]) / max(cor_k[:4])
    return f"""
<div style="font:13px/1.5 -apple-system,Segoe UI,sans-serif;color:{INK};
            max-width:64rem;margin:0 auto 0.5rem">
<p><b>Decision 1, with both outcomes measured.</b> The
<span style="color:{CUR_C}"><b>current</b></span> estimator selects the bins where
the observed count reaches K and sums <code>obs&nbsp;&minus;&nbsp;null_mean</code>
over them. The <span style="color:{COR_C}"><b>corrected</b></span> one does the
same to every surrogate, each selecting on <i>itself</i>, and subtracts the median
surrogate's excess — the standard remedy for a selection-biased statistic, reusing
the ensemble already being computed. No new sampling, no new parameter.</p>

<table style="border-collapse:collapse;font-size:12px;margin-bottom:0.6rem">
<tr style="border-bottom:1px solid #c8d6e4">
  <th style="text-align:left;padding-right:16px">at the busy background, K = 3</th>
  <th style="text-align:right;padding-right:16px">current</th>
  <th style="text-align:right">corrected</th></tr>
<tr><td style="padding:2px 16px 2px 0">nothing planted &mdash; the answer is zero</td>
  <td style="padding:2px 16px 2px 0;text-align:right"><b>{bn[3]['current']:.2f}</b></td>
  <td style="padding:2px 0;text-align:right"><b>{bn[3]['corrected']:.2f}</b></td></tr>
<tr><td style="padding:2px 16px 2px 0">12 events planted</td>
  <td style="padding:2px 16px 2px 0;text-align:right">{bp[3]['current']:.2f}</td>
  <td style="padding:2px 0;text-align:right">{bp[3]['corrected']:.2f}</td></tr>
<tr style="border-top:1px solid #e3e9ef">
  <td style="padding:2px 16px 2px 0">same 12 events, busy &divide; quiet
    <span style="color:#5c6773">(1.0 = comparable across windows)</span></td>
  <td style="padding:2px 16px 2px 0;text-align:right"><b>{cur_ratio:.2f}&times;</b></td>
  <td style="padding:2px 0;text-align:right"><b>{cor_ratio:.2f}&times;</b></td></tr>
<tr><td style="padding:2px 16px 2px 0">fall from K=3 to K=6, 12 events planted</td>
  <td style="padding:2px 16px 2px 0;text-align:right"><b>&minus;{cur_fall:.0%}</b></td>
  <td style="padding:2px 0;text-align:right"><b>&minus;{cor_fall:.0%}</b></td></tr>
</table>

<p><b>Panel A is the K decision itself.</b> Under the current estimator the excess
falls {cur_fall:.0%} between K=3 and K=6 on the planted data, and an analyst
reading that curve concludes the coordination lives at low K. <b>Most of that fall
is the bias dying out</b> — the dashed red line is the same curve on data with
nothing in it, and it has the same shape. Corrected, the signal is flat across
K=3&ndash;6, so the choice of K stops changing the answer. Those are opposite
readings of the same recording.</p>

<p><b>Panel B is the treatment contrast.</b> The same twelve planted events,
measured at the two <code>REGIMES</code> backgrounds. The current estimator reports
them {cur_ratio:.1f}&times; larger at the busy background than the quiet one — a
difference of {abs(bp[3]['current'] - qp[3]['current']):.1f} excess/min
manufactured entirely by the field the events sit in. Corrected, the same events
read within {abs(cor_ratio - 1):.0%} of each other. RESET §6 said whether two
windows at different rates yield comparable excesses was
<i>&ldquo;established nowhere&rdquo;</i>; this is what establishing it looks like
under each option.</p>

<table style="border-collapse:collapse;font-size:12px">
<tr style="border-bottom:1px solid #c8d6e4">
  <th style="text-align:left;padding-right:16px;width:50%">Option A &mdash; fork it</th>
  <th style="text-align:left;width:50%">Option B &mdash; keep parity, caveat the number</th></tr>
<tr style="vertical-align:top">
<td style="padding:8px 16px 0 0">
  &#10003; the null reads zero<br>
  &#10003; K stops moving the answer, so the choice becomes about what a person
     can see rather than about where the bias dies<br>
  &#10003; two windows at different backgrounds become comparable, which is what
     the treatment contrast needs<br>
  &#10007; <b>parity breaks</b> with <code>measure_coordination_timescale.m</code><br>
  &#10007; bugarach and <code>darkroom/constellation/</code> go onto different
     definitions of one word<br>
  &#10007; every spec, bake-off and figure derived from an assessment needs
     regenerating &mdash; one pass, RESET §5
</td>
<td style="padding:8px 0 0 0">
  &#10003; the ports stay 1e-9 faithful, which is the product (FOUNDATIONS §2)<br>
  &#10003; nothing downstream regenerates<br>
  &#10003; one definition shared with the producer<br>
  &#10007; K is chosen off a curve whose shape is mostly bias<br>
  &#10007; the excess stays uncomparable across backgrounds, so the treatment
     contrast cannot be built on it honestly<br>
  &#10007; the caveat has to be carried by every reader forever, and nothing
     enforces it &mdash; unless a <code>describe_</code>-style refusal is added,
     which is a third option nobody has costed
</td></tr>
</table>

<p style="color:#5c6773;margin-top:0.7rem">{N_ROI} ROIs, {DUR/60:.0f}-minute
window, {BIN:.0f}&nbsp;s bins, {N_SUR} surrogates, {N_PLANTED} planted events of
{PLANT_ROIS} ROIs at {PLANT_JITTER*1000:.0f}&nbsp;ms jitter; the planted times are
identical between the two backgrounds. <b>This changes nothing:</b> the corrected
estimator is computed in the figure tool, not in <code>assess.py</code>. If the
fork is taken it lands behind a flag defaulting to current behaviour, like every
other mechanism change.</p>
</div>"""


def _render_png(html_path: Path, png_path: Path, *, wait_ms: int = 3000,
                width: int = 1500, height: int = 1200) -> bool:
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

    print("measuring both estimators on the same ensembles…")
    m = measure()
    for case in ("busy_null", "busy_planted", "quiet_null", "quiet_planted"):
        row = " ".join(f"K{k}: {m[case][k]['current']:6.2f}/"
                       f"{m[case][k]['corrected']:6.2f}" for k in KS)
        print(f"  {case:<14} current/corrected  {row}")

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
