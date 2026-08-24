#!/usr/bin/env python3
"""Plant nothing, and see what the assessor says is there.

    python tools/make_null_leak_figure.py --also docs/learned

Figure id `assess_null_leak`, the same on every machine.

`docs/RESET.md` §7 puts the null test first in the order of work: *"plant
nothing, and the excess must read zero. A rate-matched null that leaks is a
defect in the arithmetic whatever convention sits on top, and every generator
spec derived afterwards inherits it."*

**It leaks, and this draws how much.** Panel A is the excess against background
rate on recordings with no coordination in them at all — every ROI's train drawn
on its own — for K = 3, 4, 6. Zero is where every one of those lines should sit.
Panel B is the decisive comparison: the same estimator handed a circular shift
of the same trains, which is by construction a draw FROM the null it compares
against, beside the real recording. The two bars are nearly the same height, so
the excess is nearly all selection rule.

Where it comes from, read off `assess.py` rather than inferred::

    bk = np.flatnonzero(obs >= K)      # bins chosen BY THE OBSERVED counts
    coact_excess = (obs[bk].sum() - null_mean[bk].sum()) / win_min

Bins are selected where the observed count reaches K, then the observed is
compared against the null's mean in those same bins. Selecting on the observed
guarantees it is high there; the null mean is the ensemble average and is not.
Positive by construction whenever any bin reaches K, coordination or no.

**This measures; it changes nothing.** `assess_coactivity` is 1e-9 parity-held
against `measure_coordination_timescale.m` and parity is the product
(FOUNDATIONS §2), so the same bias is in the MATLAB. Whether to fork it is
Tony's call — `docs/forks.md`, and the todo this figure belongs to.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np

FIGURE_ID = "assess_null_leak"

INK = "#16202b"
GUIDE = "#9a9a9a"
ZERO = "#2a7f3f"
K_COLOURS = {3: "#b03a48", 4: "#1f6fb4", 6: "#7a4fa3"}
REAL_C = "#b03a48"
NULL_C = "#5c6773"

DUR = 1800.0
N_ROI = 40
BIN = 1.0
WIN_MIN = DUR / 60.0
N_SUR = 200
SEEDS = (1, 2, 3)

#: The endpoints of this project's own difficulty axis (`bench.REGIMES`,
#: corrected 2026-08-20) with points either side, so the shape of the growth is
#: visible rather than two dots joined by a line.
RATES_HZ = (0.002, 0.0052, 0.010, 0.0190, 0.030, 0.050)
QUIET_HZ, BUSY_HZ = 0.0052, 0.0190
KS = (3, 4, 6)


def independent_trains(rate_hz: float, seed: int):
    """Nothing planted: every ROI drawn on its own, no shared process."""
    rng = np.random.default_rng(seed)
    return [np.sort(rng.uniform(0.0, DUR, size=rng.poisson(rate_hz * DUR)))
            for _ in range(N_ROI)]


def _null_mean(trains, n_bins, seed=20260722, n_sur=N_SUR):
    from bugarach.assess import _coact_count

    rng = np.random.RandomState(seed)
    total = np.zeros(n_bins)
    for _ in range(n_sur):
        off = rng.random_sample(len(trains)) * DUR
        total += _coact_count(
            [np.mod(v + off[r], DUR) if v.size else v
             for r, v in enumerate(trains)], DUR, BIN, n_bins)
    return total / float(n_sur)


def _excess(counts, null_mean, K):
    bk = np.flatnonzero(counts >= K)
    return (counts[bk].sum() - null_mean[bk].sum()) / WIN_MIN, int(bk.size)


def sweep() -> dict:
    """Excess against background rate, on data with nothing in it."""
    from bugarach.assess import _coact_count

    n_bins = int(np.ceil(DUR / BIN))
    out = {K: {"rate": [], "mean": [], "lo": [], "hi": []} for K in KS}
    for rate in RATES_HZ:
        per_k = {K: [] for K in KS}
        for seed in SEEDS:
            trains = independent_trains(rate, seed)
            obs = _coact_count(trains, DUR, BIN, n_bins)
            nm = _null_mean(trains, n_bins)
            for K in KS:
                per_k[K].append(_excess(obs, nm, K)[0])
        for K in KS:
            v = np.asarray(per_k[K], dtype=float)
            out[K]["rate"].append(rate * 1000.0)
            out[K]["mean"].append(float(v.mean()))
            out[K]["lo"].append(float(v.min()))
            out[K]["hi"].append(float(v.max()))
    return out


def decisive() -> dict:
    """The real recording beside a draw from the null the estimator uses."""
    from bugarach.assess import _coact_count

    n_bins = int(np.ceil(DUR / BIN))
    rows = []
    for rate, label in ((QUIET_HZ, "quiet"), (BUSY_HZ, "busy"),
                        (0.050, "crowded")):
        trains = independent_trains(rate, seed=1)
        obs = _coact_count(trains, DUR, BIN, n_bins)
        nm = _null_mean(trains, n_bins)
        off = np.random.RandomState(999).random_sample(len(trains)) * DUR
        as_obs = _coact_count(
            [np.mod(v + off[r], DUR) if v.size else v
             for r, v in enumerate(trains)], DUR, BIN, n_bins)
        real, _ = _excess(obs, nm, 3)
        from_null, _ = _excess(as_obs, nm, 3)
        rows.append({"label": f"{label}\n{rate*1000:.1f} mHz",
                     "real": real, "from_null": from_null,
                     "ratio": from_null / real if real else float("nan")})
    return {"rows": rows}


def build(sw: dict, dec: dict, width: int):
    import holoviews as hv

    # ---- Panel A: the leak against background rate
    curves = [hv.HLine(0.0).opts(color=ZERO, line_width=2, line_dash="solid")]
    for K in KS:
        d = sw[K]
        c = K_COLOURS[K]
        curves.append(hv.Area((d["rate"], d["lo"], d["hi"]),
                              vdims=["lo", "hi"]).opts(
            color=c, alpha=0.16, line_alpha=0.0))
        curves.append(hv.Curve((d["rate"], d["mean"]), label=f"K = {K}").opts(
            color=c, line_width=2.2))
        curves.append(hv.Scatter((d["rate"], d["mean"])).opts(
            color=c, size=6, line_color=None))
    for x in (QUIET_HZ * 1000, BUSY_HZ * 1000):
        curves.append(hv.VLine(x).opts(color=GUIDE, line_dash="dashed",
                                       line_width=1))
    panel_a = hv.Overlay(curves).opts(
        width=width // 2, height=400,
        xlabel="background rate (mHz per ROI) · dashed: the bench's own axis",
        ylabel="excess co-active ROI·events/min · nothing planted",
        fontsize={"xlabel": "9pt", "ylabel": "9pt", "ticks": "8pt",
                  "legend": "9pt"},
        legend_position="top_left", toolbar=None, show_grid=True)

    # ---- Panel B: the recording beside a draw from the null
    rows = dec["rows"]
    labels = [r["label"] for r in rows]
    bars = []
    for r in rows:
        bars.append((r["label"], "the recording", r["real"]))
        bars.append((r["label"], "a draw from the null", r["from_null"]))
    panel_b = hv.Bars(bars, kdims=["case", "series"], vdims=["excess"]).opts(
        width=width // 2, height=400, multi_level=False,
        cmap=[REAL_C, NULL_C],
        xlabel="", ylabel="excess at K = 3 · nothing planted",
        fontsize={"xlabel": "9pt", "ylabel": "9pt", "ticks": "8pt",
                  "legend": "9pt"},
        legend_position="top_left", toolbar=None, show_grid=True)
    _ = labels
    # toolbar off on the LAYOUT as well as the panels: bokeh hoists a shared one
    # onto the layout, so a panel-level `toolbar=None` leaves it drawn anyway.
    return hv.Layout([panel_a, panel_b]).cols(2).opts(
        shared_axes=False, toolbar=None)


def header_html(sw: dict, dec: dict) -> str:
    busy = [(K, np.interp(BUSY_HZ * 1000, sw[K]["rate"], sw[K]["mean"]))
            for K in KS]
    busy_txt = " · ".join(f"K={K}: <b>{v:.2f}</b>" for K, v in busy)
    rows = "".join(
        f"<tr><td style='padding:2px 14px 2px 0'>{r['label'].replace(chr(10), ' ')}</td>"
        f"<td style='padding:2px 14px 2px 0;text-align:right'>{r['real']:.2f}</td>"
        f"<td style='padding:2px 14px 2px 0;text-align:right'>{r['from_null']:.2f}</td>"
        f"<td style='padding:2px 0;text-align:right'><b>{r['ratio']:.0%}</b></td></tr>"
        for r in dec["rows"])
    return f"""
<div style="font:13px/1.5 -apple-system,Segoe UI,sans-serif;color:{INK};
            max-width:60rem;margin:0 auto 0.5rem">
<p><b>Plant nothing, and the assessor still reports coordination.</b> Every ROI's
train here is drawn on its own — homogeneous Poisson, no shared process, no
injected event — so every co-active moment is a coincidence and the rate-matched
null is exactly the right model of what produced it. The green line at zero in
panel A is where all three curves should sit. At the busy end of this project's
own difficulty axis ({BUSY_HZ*1000:.1f} mHz/ROI) the excess reads {busy_txt}
excess co-active ROI·events per minute.</p>

<p><b>Panel B is what it actually measures.</b> The grey bar is the same
estimator handed a circular shift of the same trains — by construction a draw
<i>from</i> the null it compares against, so it should read zero if the excess
measures anything about the data. It reads almost what the recording reads:</p>

<table style="border-collapse:collapse;font-size:12px">
<tr style="border-bottom:1px solid #c8d6e4">
  <th style="text-align:left;padding-right:14px">background</th>
  <th style="text-align:right;padding-right:14px">the recording</th>
  <th style="text-align:right;padding-right:14px">a draw from the null</th>
  <th style="text-align:right">ratio</th></tr>
{rows}
</table>

<p><b>Why.</b> <code>assess.py</code> selects bins where the <i>observed</i> count
reaches K, then compares the observed against the null's <i>mean</i> in those same
bins. Selecting on the observed value guarantees it is high there; the null mean
is the ensemble average and is not. The difference is positive by construction
whenever any bin reaches K, with or without coordination — the winner's curse,
not a measurement. More surrogates estimate the null mean better and do not
touch it.</p>

<p style="color:#5c6773">{len(SEEDS)} seeds per rate, {N_ROI} ROIs,
{DUR/60:.0f}-minute window, {BIN:.0f} s bins, {N_SUR} surrogates; the band is
the seed range. <b>This measures and changes nothing:</b>
<code>assess_coactivity</code> is held to 1e-9 against
<code>measure_coordination_timescale.m</code> and parity is the product, so the
same bias is in the MATLAB. Whether to fork it is Tony's call.</p>
</div>"""


def _render_png(html_path: Path, png_path: Path, *, wait_ms: int = 2500,
                width: int = 1400, height: int = 1000) -> bool:
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


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--width", type=int, default=1240)
    p.add_argument("--out", default=None,
                   help="destination; defaults to the darkroom")
    p.add_argument("--also", type=Path, default=None,
                   help="second destination, e.g. docs/learned")
    p.add_argument("--no-png", dest="png", action="store_false", default=True)
    a = p.parse_args()

    print("sweeping the background axis with nothing planted…")
    sw = sweep()
    for K in KS:
        at_busy = np.interp(BUSY_HZ * 1000, sw[K]["rate"], sw[K]["mean"])
        print(f"  K={K}: {at_busy:8.3f} excess/min at the busy endpoint")
    dec = decisive()
    for r in dec["rows"]:
        print(f"  {r['label'].replace(chr(10), ' '):<18} recording "
              f"{r['real']:8.3f} · from the null {r['from_null']:8.3f} "
              f"· {r['ratio']:.0%}")

    from bugarach.paths import darkroom, unresolved_message
    dest = Path(a.out) if a.out else darkroom()
    if dest is None:
        print(unresolved_message(), file=sys.stderr)
        return 1

    import holoviews as hv
    import panel as pn
    hv.extension("bokeh")
    layout = build(sw, dec, a.width)

    dests = [dest] + ([a.also] if a.also else [])
    for i, d in enumerate(dests):
        d.mkdir(parents=True, exist_ok=True)
        html = d / f"{FIGURE_ID}.html"
        pn.panel(pn.Column(pn.pane.HTML(header_html(sw, dec)),
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
