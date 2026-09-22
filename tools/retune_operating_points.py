#!/usr/bin/env python3
"""Retune every detector's swept setting through the gated picker, and draw the result.

    python tools/retune_operating_points.py                   # 48 recordings -> the darkroom
    python tools/retune_operating_points.py --seeds 12 --workers 8
    python tools/retune_operating_points.py --report retune.json   # redraw only

**What "best" means here, stated once so it can be argued with.** For each detector:

1. Sweep its knob (``bench.OPERATING_POINTS[name].knob``) over a grid widened past
   every edge the 2026-09-15 review's sweeps hit, on both bench backgrounds, pooling
   ``--seeds`` simulated recordings per point. Where the gated picker still reports
   ``EdgeOfRange``, the grid is widened and re-run, up to four rounds.
2. Candidates are the values under **both** false-alarm budgets: the probe stretch with
   nothing planted (``bench.MAX_PROBE_PER_MIN``) on both backgrounds — one stored value
   runs on every recording, so it has to be admissible at both ends of the real rate
   axis — and a whole recording with nothing planted
   (``bench.MAX_FALSE_POSITIVES_PER_HOUR``). The first version of this tool applied only
   the first, and proposed binned SCE at a setting that reports 32 calls an hour on the
   empty recording against a budget of 6.
3. The best candidate has the highest F1 averaged over the two backgrounds.
4. **It replaces the stored value only if its gain has a 95% bootstrap interval that
   excludes zero** (400 resamples of recordings, the same indices for both
   backgrounds). A gain inside the noise is not a reason to move every published
   number.

Each point is scored one recording per job so any subset can be pooled afterwards —
all recordings for the curve, resamples for the interval, halves for a stability
check (``half_verdicts``, the picker's answer on each half separately).

**What this cannot tell you.** Every number is F1 against planted events on the
simulator; real recordings have no answer key. And only the one swept knob per
detector moves — the others were never varied (see the 2026-09-16 optimization
handoff, §4).

Writes, to ``<darkroom>/<date>-best-parameters/`` unless ``--out`` says otherwise:
``retune.json`` and Figure 1 as ``best_parameters.html`` and ``best_parameters.png``
(the PNG needs Playwright chromium).
"""
from __future__ import annotations

import argparse
import datetime
import json
import math
import sys
import time
from multiprocessing import Pool
from pathlib import Path

GRIDS = {
    "sce": [10.0, 20.0, 30.0, 40.0, 50.0, 60.0, 70.0, 75.0, 80.0, 85.0, 90.0, 95.0,
            98.0, 99.0, 99.5, 99.9],
    "sync": [0.005, 0.01, 0.02, 0.04, 0.06, 0.08, 0.1, 0.12, 0.16, 0.2, 0.3],
    "loco": [95.0, 97.0, 98.0, 99.0, 99.5, 99.9, 99.99, 99.999, 99.9999],
    "coact": [1e-1, 3e-2, 1e-2, 3e-3, 1e-3, 3e-4, 1e-4, 3e-5, 1e-5, 1e-6, 1e-7],
    "rate": [0.5, 1.0, 2.0, 3.0, 3.5, 4.0, 4.5, 5.0, 6.0, 8.0],
    "cicada": [90.0, 99.0, 99.9, 99.95, 99.99, 99.995, 99.999, 99.9995, 99.9999,
               99.99999],
}
#: How a grid grows past an edge: (below its lowest value, above its highest).
EXTEND = {
    "sce": (lambda v: v / 2, lambda v: 100 - (100 - v) / 2),
    "sync": (lambda v: v / 2, lambda v: min(1.0, v * 1.5)),
    "loco": (lambda v: 100 - (100 - v) * 2, lambda v: 100 - (100 - v) / 10),
    "coact": (lambda v: min(0.5, v * 3), lambda v: v / 10),
    "rate": (lambda v: v / 2, lambda v: v * 1.5),
    "cicada": (lambda v: 100 - (100 - v) * 10, lambda v: 100 - (100 - v) / 10),
}
REGIMES = ("baseline_quiet", "baseline_busy")
NULL = "null"          # bench.make_null_recording: nothing planted anywhere
MAX_ROUNDS = 4
BOOTSTRAP = 400
BOOTSTRAP_SEED = 20260916


def _job(args):
    name, regime, value, seed = args
    from bugarach import bench
    from bugarach.score import score_stream

    if regime == NULL:
        rate = bench.false_positives_per_hour(
            name, seeds=(seed,), **{bench.OPERATING_POINTS[name].knob: value})
        return name, regime, value, seed, rate
    s, gt = bench.make_recording(regime, seed)
    det = bench.run_detector(name, s, **{bench.OPERATING_POINTS[name].knob: value})
    return name, regime, value, seed, score_stream(gt, det)


def _pooled(scores, name, regime, value, seeds):
    from bugarach import bench
    return bench.pool_scores([scores[(name, regime, value, s)] for s in seeds],
                             detector=name, regime=regime, seeds=tuple(seeds),
                             knob_value=value)


def _verdict(curve):
    from bugarach import bench
    try:
        return dict(kind="accept", value=bench.pick_operating_point(curve).knob_value)
    except (bench.EdgeOfRange, bench.TooPromiscuous, bench.DegenerateSweep) as e:
        return dict(kind=type(e).__name__, msg=str(e))


def run(n_seeds: int, workers: int) -> dict:
    import numpy as np
    from bugarach import bench

    seeds = list(range(1, n_seeds + 1))
    grids = {n: sorted(set(g) | {bench.OPERATING_POINTS[n].params[bench.OPERATING_POINTS[n].knob]})
             for n, g in GRIDS.items()}
    scores = {}
    with Pool(workers) as pool:
        for rnd in range(1, MAX_ROUNDS + 1):
            todo = [(n, r, v, s) for n, g in grids.items() for r in (*REGIMES, NULL)
                    for v in g for s in seeds if (n, r, v, s) not in scores]
            if not todo:
                break
            t0 = time.time()
            for n, r, v, s, sc in pool.imap_unordered(_job, todo, chunksize=2):
                scores[(n, r, v, s)] = sc
            print(f"round {rnd}: {len(todo)} recordings scored in {time.time() - t0:.0f} s",
                  flush=True)
            widened = False
            for n in grids:
                for r in REGIMES:
                    curve = [_pooled(scores, n, r, v, seeds) for v in grids[n]]
                    if _verdict(curve)["kind"] != "EdgeOfRange":
                        continue
                    best = max(curve, key=lambda c: c.f1).knob_value
                    lo_fn, hi_fn = EXTEND[n]
                    edge = min(grids[n]) if best == min(grids[n]) else max(grids[n])
                    new = lo_fn(edge) if edge == min(grids[n]) else hi_fn(edge)
                    if new not in grids[n] and abs(new - edge) > 1e-12:
                        grids[n] = sorted(grids[n] + [new])
                        widened = True
                        print(f"  {n} ({r}) peaked at the grid edge {edge:g}; adding {new:g}",
                              flush=True)
            if not widened:
                break

    rng = np.random.RandomState(BOOTSTRAP_SEED)
    halves = (seeds[: len(seeds) // 2], seeds[len(seeds) // 2:])
    report = {"seeds": seeds, "bootstrap_resamples": BOOTSTRAP, "detectors": {},
              "tol_sec": __import__("bugarach.score", fromlist=["TOL_SEC"]).TOL_SEC}
    for n in grids:
        op = bench.OPERATING_POINTS[n]
        shipped = op.params[op.knob]
        d = {"knob": op.knob, "shipped": shipped,
             "ceiling_per_min": bench.MAX_PROBE_PER_MIN[n],
             "null_ceiling_per_hour": bench.MAX_FALSE_POSITIVES_PER_HOUR[n],
             "null_per_hour": {repr(v): float(np.mean([scores[(n, NULL, v, s)] for s in seeds]))
                               for v in grids[n]},
             "grid": grids[n], "backgrounds": {}}
        for r in REGIMES:
            curve = [_pooled(scores, n, r, v, seeds) for v in grids[n]]
            d["backgrounds"][r] = {
                "rows": [dict(v=c.knob_value, f1=c.f1, recall=c.recall,
                              precision=c.precision, probe_per_min=c.hot_fa_per_min,
                              n_hit=c.n_hit, n_planted=c.n_planted) for c in curve],
                "verdict": _verdict(curve),
                "half_verdicts": [_verdict([_pooled(scores, n, r, v, h) for v in grids[n]])
                                  for h in halves],
            }
        gains = {v: [] for v in grids[n]}
        for _ in range(BOOTSTRAP):
            idx = list(rng.choice(seeds, size=len(seeds), replace=True))
            mean = {v: float(np.mean([_pooled(scores, n, r, v, idx).f1 for r in REGIMES]))
                    for v in grids[n]}
            for v in grids[n]:
                gains[v].append(mean[v] - mean[shipped])
        d["bootstrap_gain_vs_shipped"] = {
            repr(v): dict(lo=float(np.nanpercentile(g, 2.5)) if np.isfinite(g).any() else None,
                          mid=float(np.nanmedian(g)) if np.isfinite(g).any() else None,
                          hi=float(np.nanpercentile(g, 97.5)) if np.isfinite(g).any() else None)
            for v, g in gains.items()}
        report["detectors"][n] = d
    return report


def admissible(d: dict, v: float, *, null_gate: bool = True) -> bool:
    """Under both false-alarm budgets: the probe on both backgrounds, and the null recording."""
    q = {r["v"]: r for r in d["backgrounds"]["baseline_quiet"]["rows"]}
    b = {r["v"]: r for r in d["backgrounds"]["baseline_busy"]["rows"]}
    c = d["ceiling_per_min"]
    ok = (q[v]["probe_per_min"] <= c and b[v]["probe_per_min"] <= c
          and math.isfinite(q[v]["f1"]) and math.isfinite(b[v]["f1"]))
    if null_gate:
        ok = ok and d["null_per_hour"][repr(v)] <= d["null_ceiling_per_hour"]
    return ok


def choose(d: dict, *, null_gate: bool = True) -> dict:
    """Apply the rule in the module docstring to one detector's report."""
    q = {r["v"]: r for r in d["backgrounds"]["baseline_quiet"]["rows"]}
    b = {r["v"]: r for r in d["backgrounds"]["baseline_busy"]["rows"]}
    cands = [v for v in q if admissible(d, v, null_gate=null_gate)]
    best = max(cands, key=lambda v: (q[v]["f1"] + b[v]["f1"]) / 2)
    gain = d["bootstrap_gain_vs_shipped"][repr(best)]
    chosen = best if best != d["shipped"] and gain["lo"] > 0 else d["shipped"]
    mean = {v: (q[v]["f1"] + b[v]["f1"]) / 2 for v in q}
    return dict(best=best, chosen=chosen, gain=gain, quiet=q, busy=b, mean=mean)


NAMES = {"coact": "CoactDetect", "loco": "LoCo", "rate": "rate+context",
         "sce": "binned SCE", "cicada": "locust", "sync": "SPIKE-synch"}
KNOB_LABEL = {"threshold_pctile": "threshold percentile", "C_threshold": "C threshold",
              "alpha": "alpha", "excess_threshold_hz": "excess threshold (Hz)",
              "sce_percentile": "percentile"}
ORDER = ["coact", "loco", "rate", "sce", "cicada", "sync"]


def _fmt(v: float) -> str:
    return f"{v:.0e}".replace("e-0", "e-") if v < 0.001 else f"{v:.10g}"


def render(rep: dict, dest: Path) -> list[Path]:
    """Figure 1 as HTML, and a PNG of it when Playwright chromium is available."""
    quiet_ink, busy_ink = "#2a78d6", "#eb6834"
    W, H, ML, MR, MT, MB = 400, 250, 52, 14, 14, 58
    panels, rows = [], []
    for n in ORDER:
        d = rep["detectors"][n]
        ch = choose(d)
        q, b, sv = ch["quiet"], ch["busy"], d["shipped"]
        vals = sorted(q, reverse=(n == "coact"))       # stricter to the right in every panel
        xs = {v: ML + (W - ML - MR) * k / (len(vals) - 1) for k, v in enumerate(vals)}

        def y(f):
            return MT + (H - MT - MB) * (1 - f / 0.8)

        s = [f'<svg viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img">']
        for t in (0.0, 0.2, 0.4, 0.6, 0.8):
            s.append(f'<line x1="{ML}" x2="{W-MR}" y1="{y(t):.1f}" y2="{y(t):.1f}" class="grid"/>'
                     f'<text x="{ML-6}" y="{y(t)+4:.1f}" class="tick" text-anchor="end">{t:.1f}</text>')
        for v in vals:
            s.append(f'<text x="{xs[v]:.1f}" y="{H-MB+14}" class="tick" text-anchor="end" '
                     f'transform="rotate(-45 {xs[v]:.1f} {H-MB+14})">{_fmt(v)}</text>')
        s.append(f'<line x1="{xs[sv]:.1f}" x2="{xs[sv]:.1f}" y1="{MT}" y2="{H-MB}" class="shipped"/>')
        if ch["chosen"] != sv:
            x = xs[ch["chosen"]]
            s.append(f'<line x1="{x:.1f}" x2="{x:.1f}" y1="{MT}" y2="{H-MB}" class="chosen"/>')
        for bg, ink in ((q, quiet_ink), (b, busy_ink)):
            pts = [(xs[v], y(bg[v]["f1"])) for v in vals if math.isfinite(bg[v]["f1"])]
            s.append('<polyline fill="none" stroke="%s" stroke-width="2" points="%s"/>'
                     % (ink, " ".join(f"{px:.1f},{py:.1f}" for px, py in pts)))
            for v in vals:
                f = bg[v]["f1"]
                if not math.isfinite(f):
                    continue
                null = d["null_per_hour"][repr(v)]
                over = (bg[v]["probe_per_min"] > d["ceiling_per_min"]
                        or null > d["null_ceiling_per_hour"])
                fill = "var(--surface)" if over else ink
                s.append(f'<circle cx="{xs[v]:.1f}" cy="{y(f):.1f}" r="4" fill="{fill}" '
                         f'stroke="{ink}" stroke-width="2"><title>{NAMES[n]} {_fmt(v)}: F1 {f:.3f}; '
                         f'{bg[v]["probe_per_min"]:.2f} firings/min in the empty stretch; '
                         f'{null:.1f} calls/hour on the empty recording</title></circle>')
        mid = (MT + H - MB) / 2
        s.append(f'<text x="14" y="{mid:.1f}" class="lab" text-anchor="middle" '
                 f'transform="rotate(-90 14 {mid:.1f})">F1 · {NAMES[n]}</text>'
                 f'<text x="{(ML + W - MR) / 2:.1f}" y="{H-4}" class="lab" text-anchor="middle">'
                 f'{KNOB_LABEL[d["knob"]]} (stricter →)</text></svg>')
        g = ch["gain"]
        if ch["chosen"] != sv:
            note = (f'<b>{_fmt(sv)} → {_fmt(ch["chosen"])}</b>: mean F1 {g["mid"]:+.3f} '
                    f'(95% interval {g["lo"]:+.3f} to {g["hi"]:+.3f})')
        elif ch["best"] != sv:
            note = (f'<b>stays {_fmt(sv)}</b>: {_fmt(ch["best"])} was {g["mid"]:+.3f} '
                    f'(95% interval {g["lo"]:+.3f} to {g["hi"]:+.3f}, includes zero)')
        else:
            note = f'<b>stays {_fmt(sv)}</b>: already the best value within both false-alarm limits'
        loose = choose(d, null_gate=False)
        if loose["chosen"] != ch["chosen"]:
            lv, lg = loose["chosen"], loose["gain"]
            note += (f'<br>Without the empty-recording limit: <b>{_fmt(lv)}</b>, {lg["mid"]:+.3f} '
                     f'(95% interval {lg["lo"]:+.3f} to {lg["hi"]:+.3f}), at '
                     f'{d["null_per_hour"][repr(lv)]:.0f} calls/hour on the empty recording '
                     f'against a limit of {d["null_ceiling_per_hour"]:g}')
        panels.append(f'<div>{"".join(s)}<p class="note">{note}</p></div>')
        c = ch["chosen"]
        rows.append(f"<tr><td>{NAMES[n]}</td><td><code>{d['knob']}</code></td><td>{_fmt(sv)}</td>"
                    f"<td>{_fmt(c)}</td><td>{ch['mean'][sv]:.3f}</td><td>{ch['mean'][c]:.3f}</td>"
                    f"<td>{q[c]['probe_per_min']:.2f} / {b[c]['probe_per_min']:.2f} "
                    f"(limit {d['ceiling_per_min']:g})</td>"
                    f"<td>{d['null_per_hour'][repr(c)]:.1f} (limit {d['null_ceiling_per_hour']:g})</td></tr>")

    n_rec = len(rep["seeds"])
    html = f"""<meta charset="utf-8"><title>Best parameters</title>
<style>
:root {{ --surface:#fcfcfb; --ink:#1b1b1a; --muted:#6b6a64; --rule:#e4e3de; }}
body {{ background:var(--surface); color:var(--ink); font:14px/1.45 system-ui, sans-serif;
        margin:0; padding:20px 24px; max-width:1260px; }}
.six {{ display:grid; grid-template-columns:repeat(3, {W}px); gap:6px 20px; }}
.note {{ margin:0 0 10px {ML}px; font-size:12.5px; }}
svg .grid {{ stroke:var(--rule); }} svg .tick {{ font-size:10.5px; fill:var(--muted); }}
svg .lab {{ font-size:12px; fill:var(--ink); }}
svg .shipped {{ stroke:#8a8983; stroke-width:1.5; stroke-dasharray:4 3; }}
svg .chosen {{ stroke:#1b1b1a; stroke-width:2; }}
.legend {{ display:flex; gap:22px; font-size:13px; margin:6px 0 12px; }}
.sw {{ display:inline-block; width:22px; border-top:2px solid; vertical-align:middle; margin-right:6px; }}
table {{ border-collapse:collapse; font-size:13px; margin-top:10px; }}
td, th {{ padding:3px 10px; border-bottom:1px solid var(--rule); text-align:left; }}
</style>
<p><b>Figure 1. Each detector's F1 across its swept setting, on both simulated backgrounds, with the
setting it shipped at and the one that replaces it.</b> Blue: quiet background; orange: busy background
(the 25th and 75th percentiles of per-ROI event rate across real untreated recordings). Each point pools
{n_rec} simulated recordings. A hollow point breaks one of the detector's two false-alarm limits and cannot
be chosen: firings per minute in a dense stretch with nothing planted, on that background
(<code>MAX_PROBE_PER_MIN</code>), or calls per hour on a whole recording with nothing planted
(<code>MAX_FALSE_POSITIVES_PER_HOUR</code>; {n_rec} such recordings). Dashed grey
line: the shipped setting. Solid black line: its replacement. A setting is replaced only when the best
allowed value's gain in F1, averaged over both backgrounds, has a 95% bootstrap interval
({rep["bootstrap_resamples"]} resamples of recordings) that excludes zero. F1 is the harmonic mean of recall
and precision; a call is a hit when its span comes within {rep["tol_sec"]:g} s of a planted event.</p>
<div class="legend"><span><span class="sw" style="border-color:{quiet_ink}"></span>quiet background</span>
<span><span class="sw" style="border-color:{busy_ink}"></span>busy background</span>
<span><span class="sw" style="border-color:#8a8983;border-top-style:dashed"></span>shipped</span>
<span><span class="sw" style="border-color:#1b1b1a"></span>replacement</span></div>
<div class="six">{"".join(panels)}</div>
<table><tr><th>detector</th><th>setting</th><th>shipped</th><th>best</th><th>mean F1, shipped</th>
<th>mean F1, best</th><th>firings/min in the empty stretch, at best (quiet / busy)</th>
<th>calls/hour on the empty recording, at best</th></tr>{"".join(rows)}</table>
"""
    page = dest / "best_parameters.html"
    page.write_text(html, encoding="utf-8")
    written = [page]
    try:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as p:
            br = p.chromium.launch()
            pg = br.new_page(viewport={"width": 1300, "height": 900}, device_scale_factor=2)
            pg.goto(page.resolve().as_uri())
            pg.screenshot(path=str(dest / "best_parameters.png"), full_page=True)
            br.close()
        written.append(dest / "best_parameters.png")
    except Exception as exc:  # noqa: BLE001 — the HTML is the figure; the PNG is a preview
        print(f"(no PNG: {exc})", file=sys.stderr)
    return written


def main(argv=None) -> int:
    from bugarach.paths import darkroom, unresolved_message

    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--seeds", type=int, default=48,
                    help="simulated recordings per point, per background (default 48)")
    ap.add_argument("--workers", type=int, default=8)
    ap.add_argument("--report", type=Path, default=None,
                    help="redraw from a saved retune.json instead of sweeping")
    ap.add_argument("--out", type=Path, default=None,
                    help="destination (default: <darkroom>/<date>-best-parameters)")
    a = ap.parse_args(argv)

    if a.out:
        dest = a.out.expanduser()
    else:
        root = darkroom(create=True)
        if root is None:
            print(unresolved_message(), file=sys.stderr)
            return 2
        dest = root / f"{datetime.date.today().isoformat()}-best-parameters"
    dest.mkdir(parents=True, exist_ok=True)

    if a.report:
        rep = json.loads(a.report.read_text())
    else:
        rep = run(a.seeds, a.workers)
        (dest / "retune.json").write_text(json.dumps(rep, indent=1))
    for n in ORDER:
        d, ch = rep["detectors"][n], choose(rep["detectors"][n])
        g = ch["gain"]
        loose = choose(d, null_gate=False)
        print(f"{NAMES[n]:13s} {d['knob']:20s} shipped {_fmt(d['shipped']):>8s}  "
              f"best {_fmt(ch['best']):>8s}  gain {g['mid']:+.3f} [{g['lo']:+.3f}, {g['hi']:+.3f}]"
              f"  -> {_fmt(ch['chosen'])}   (without the empty-recording limit: "
              f"{_fmt(loose['chosen'])})")
    for p in render(rep, dest):
        print("wrote", p)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
