#!/usr/bin/env python3
"""Search every declared setting of all six detectors — a measurement, not a retune.

    python tools/search_all_settings.py                       # -> the darkroom
    python tools/search_all_settings.py --full loco           # also LoCo's whole grid
    python tools/search_all_settings.py --smoke               # tiny grids, 2 recordings

**Why it exists.** ``tools/retune_operating_points.py`` searched one setting per
detector and held the rest where they were, so its "best" is best *for that setting*.
The question this answers is whether the settings it never touched are worth anything:
if a search over all of them cannot beat the shipped point on recordings it did not
choose on, the one-setting result is as good as the bench can say. **It changes no
operating point.** Adopting anything it finds is a separate decision.

**What is searched.** The settings each detector declares in
``bench.OPERATING_POINTS`` (see :data:`SPACE`), excluding surrogate counts, which trade
precision for compute time, and ``grid_dt``, which is the recording's frame interval.
Undeclared signature defaults — ``min_rois``, the merge gaps — are **not** searched:
``min_rois`` is the participation floor, and tuning it to the bench's planted
participation levels would fit the generator rather than the tissue.

**How, in three stages, each saved to ``search.json`` as it finishes:**

1. **Coordinate rounds.** Starting from the shipped point, sweep one setting at a time
   with the others held at the current best, move to the best admissible value if it
   beats the current point by more than :data:`MOVE_EPS` mean F1, widen a grid whose
   best value sits on its edge, and repeat until a whole round moves nothing (at most
   :data:`MAX_ROUNDS`).
2. **Two-setting grids** for the pairs known or suspected to interact (:data:`PAIRS`),
   every combination, the other settings at their shipped values.
3. **Held-out confirmation.** Stages 1 and 2 choose on recordings 1–N. Every candidate
   — shipped, stage 1's, stage 2's, and ``--full``'s — is then re-scored on recordings
   N+1–2N, which nothing was chosen on, and its gain over the shipped point there gets a
   95% bootstrap interval. **The held-out gain is the number to quote**; the
   selection-set gain is reported beside it so the optimism of choosing is visible.

**Admissible** means under all three budgets ``bench.py`` holds: ``MAX_PROBE_PER_MIN`` on both
backgrounds, ``MAX_FALSE_POSITIVES_PER_HOUR`` on the empty recording, and
``MAX_PRECISION_DROP`` between the backgrounds.

**LoCo and CoactDetect are searched in their sliding form** (``window_mode="sliding"``, shipped
2026-09-16): their counts slide and their nulls are exact, so ``thr_step_sec`` and the surrogate
counts no longer apply and are not searched. **Best** means F1 averaged over the quiet and busy backgrounds.

**What this cannot tell you:** everything is F1 against planted events on the simulator.
Settings that shape a detector's window (context, integration, bin width) are the ones
most exposed to the bench's structure — planted events at least 120 s apart, widths that
carry no signal — so a gain there needs checking on crowded recordings and on real calls
before anyone adopts it.
"""
from __future__ import annotations

import argparse
import datetime
import itertools
import json
import math
import sys
import time
from multiprocessing import Pool
from pathlib import Path

REGIMES = ("baseline_quiet", "baseline_busy")
NULL = "null"
MAX_ROUNDS = 4
MAX_EXTENSIONS = 3
MOVE_EPS = 0.002
BOOTSTRAP = 400
BOOTSTRAP_SEED = 20260917

#: Grids per declared setting. The shipped value is added if missing.
SPACE = {
    "loco": {
        "threshold_pctile": [97.0, 98.0, 99.0, 99.5, 99.9, 99.99],
        "bin_width_sec": [0.5, 1.0, 2.0, 3.0, 5.0],
        "context_win_sec": [30.0, 60.0, 120.0, 240.0, 480.0],
        "merge_gap_sec": [0.5, 1.0, 2.0, 4.0, 8.0],
    },
    "sync": {
        "C_threshold": [0.02, 0.04, 0.06, 0.08, 0.1, 0.12, 0.16],
        "C_min": [0.02, 0.05, 0.1, 0.15, 0.2],
        "tau_max": [0.1, 0.25, 0.5, 1.0, 2.0],
        "max_gap": [0.1, 0.25, 0.5, 1.0, 2.0],
    },
    "coact": {
        "alpha": [1e-2, 3e-3, 1e-3, 3e-4, 1e-4, 3e-5, 1e-5, 1e-6],
        "int_win_sec": [0.5, 1.0, 2.0, 3.0, 5.0],
        "context_win_sec": [20.0, 30.0, 60.0, 120.0, 240.0],
    },
    "rate": {
        "excess_threshold_hz": [3.0, 3.5, 4.0, 4.5, 5.0, 6.0, 8.0],
        "context_win": [20.0, 30.0, 60.0, 120.0, 240.0],
        "rate_win": [0.5, 1.0, 2.0, 3.0, 5.0],
    },
    "sce": {
        "threshold_pctile": [70.0, 75.0, 80.0, 85.0, 90.0, 95.0, 98.0, 99.0, 99.5],
        "bin_width_sec": [2.0, 5.0, 10.0, 15.0, 20.0, 30.0],
    },
    "cicada": {
        "sce_percentile": [99.9, 99.95, 99.99, 99.995, 99.999, 99.9995, 99.9999],
        "n_synchronous_frames": [1, 2, 3, 5, 10],
        "sce_min_distance_frames": [1, 2, 4, 8, 16],
    },
}
#: Pairs searched as full two-setting grids.
PAIRS = {
    "sce": ("threshold_pctile", "bin_width_sec"),
    "loco": ("threshold_pctile", "context_win_sec"),
    "cicada": ("sce_percentile", "n_synchronous_frames"),
}
PERCENTILE = {"threshold_pctile", "sce_percentile"}
INTEGER = {"n_synchronous_frames", "sce_min_distance_frames"}
FRACTION = {"C_threshold", "C_min"}


def shipped_value(det: str, setting: str):
    """The shipped value: declared in OPERATING_POINTS, or the detector's own default."""
    import inspect

    from bugarach import bench
    from bugarach.detectors import (cicada_detect, coact_detect, loco_detect,
                                    rate_detect, sce_detect, sync_detect)
    params = bench.OPERATING_POINTS[det].params
    if setting in params:
        return params[setting]
    fn = {"loco": loco_detect, "sce": sce_detect, "cicada": cicada_detect,
          "coact": coact_detect, "rate": rate_detect, "sync": sync_detect}[det]
    return inspect.signature(fn).parameters[setting].default


def valid(det: str, p: dict) -> bool:
    """Settings that make sense together. Rejects a window shorter than what fills it."""
    if det == "loco":
        return (p["bin_width_sec"] * 4 <= p["context_win_sec"]
                and p["merge_gap_sec"] < p["context_win_sec"])
    if det == "coact":
        return p["int_win_sec"] * 4 <= p["context_win_sec"]
    if det == "rate":
        return p["rate_win"] * 4 <= p["context_win"]
    if det == "sync":
        return p["C_min"] <= p["C_threshold"]
    return True


def extend(setting: str, grid: list, low_end: bool):
    """One more value past an edge of ``grid``, or None when the setting cannot go further."""
    edge = min(grid) if low_end else max(grid)
    if setting in PERCENTILE:
        new = 100 - (100 - edge) * 2 if low_end else 100 - (100 - edge) / 2
        new = max(new, 1.0)
    elif setting in INTEGER:
        new = max(1, int(edge) // 2) if low_end else int(edge) * 2
    elif setting == "alpha":
        new = edge / 3 if low_end else min(0.5, edge * 3)
    elif setting in FRACTION:
        new = edge / 2 if low_end else min(1.0, edge * 1.5)
    else:
        new = edge / 2 if low_end else edge * 2
    if any(math.isclose(new, g, rel_tol=1e-12, abs_tol=1e-15) for g in grid):
        return None
    return new


# ------------------------------------------------------------------ evaluation

def _key(det, params):
    return det, tuple(sorted(params.items()))


def _job(args):
    """One (detector, settings, regime) over a list of recordings.

    Returns a compact summary for selection, and the per-recording Scores (or empty-
    recording rates) when ``keep`` — only the held-out stage needs those.
    """
    det, items, regime, seeds, keep = args
    from bugarach import bench
    from bugarach.score import score_stream

    params = dict(items)
    if regime == NULL:
        rates = [bench.false_positives_per_hour(det, seeds=(s,), **params) for s in seeds]
        return (det, items, regime), dict(null_per_hour=sum(rates) / len(rates),
                                          per_seed=rates if keep else None)
    scores = []
    for s in seeds:
        rec, gt = bench.make_recording(regime, s)
        scores.append(score_stream(gt, bench.run_detector(det, rec, **params)))
    r = bench.pool_scores(scores, detector=det, regime=regime, seeds=tuple(seeds))
    return (det, items, regime), dict(f1=r.f1, recall=r.recall, precision=r.precision,
                                      probe_per_min=r.hot_fa_per_min, n_hit=r.n_hit,
                                      n_planted=r.n_planted,
                                      per_seed=scores if keep else None)


class Evaluator:
    """Caches pooled results per (detector, settings, regime) and runs batches in parallel."""

    def __init__(self, pool, seeds, log=print):
        self.pool, self.seeds, self.log = pool, list(seeds), log
        self.cache: dict = {}
        self.n_points = 0

    def run(self, points):
        """``points``: iterable of (det, params). Fills the cache for all three recordings."""
        todo = []
        for det, params in points:
            k = _key(det, params)
            for regime in (*REGIMES, NULL):
                if (k[0], k[1], regime) not in self.cache:
                    todo.append((det, k[1], regime, self.seeds, False))
        if not todo:
            return
        t0 = time.time()
        for key, val in self.pool.imap_unordered(_job, todo, chunksize=1):
            self.cache[key] = val
        self.n_points += len(todo) // 3
        self.log(f"    {len(todo)} evaluations in {time.time() - t0:.0f} s")

    def summary(self, det, params):
        k = _key(det, params)
        q, b, n = (self.cache[(k[0], k[1], r)] for r in (*REGIMES, NULL))
        return dict(f1_quiet=q["f1"], f1_busy=b["f1"],
                    mean_f1=(q["f1"] + b["f1"]) / 2,
                    precision_quiet=q["precision"], precision_busy=b["precision"],
                    probe_quiet=q["probe_per_min"], probe_busy=b["probe_per_min"],
                    null_per_hour=n["null_per_hour"])


def admissible(det: str, s: dict) -> bool:
    """Under all three budgets bench.py holds: the probe on both backgrounds, the empty
    recording, and the precision swing between the backgrounds."""
    from bugarach import bench
    ceiling = bench.MAX_PROBE_PER_MIN[det]
    swing = abs(s["precision_quiet"] - s["precision_busy"])
    return (math.isfinite(s["f1_quiet"]) and math.isfinite(s["f1_busy"])
            and s["probe_quiet"] <= ceiling and s["probe_busy"] <= ceiling
            and s["null_per_hour"] <= bench.MAX_FALSE_POSITIVES_PER_HOUR[det]
            and math.isfinite(swing) and swing <= bench.MAX_PRECISION_DROP[det])


# ------------------------------------------------------------------ the search

def coordinate_rounds(dets, start, space, evaluate, summarize, is_admissible,
                      is_valid=lambda d, p: True, log=print):
    """Stage 1, with the evaluator injected so the logic is testable without detectors.

    ``evaluate(points)`` fills results for a batch of (det, params); ``summarize(det,
    params)`` returns a dict with ``mean_f1``; ``is_admissible(det, summary)``.
    Returns ``(state, history)``.
    """
    state = {d: dict(start[d]) for d in dets}
    space = {d: {k: list(v) for k, v in space[d].items()} for d in dets}
    history = {d: [] for d in dets}
    # Per setting over the WHOLE search, not per round: reset each round, a setting whose
    # score keeps rising with its value doubled thirteen times in the test that caught it.
    extensions = {(d, k): 0 for d in dets for k in space[d]}
    active = set(dets)
    for rnd in range(1, MAX_ROUNDS + 1):
        if not active:
            break
        moved = set()
        n_steps = max(len(space[d]) for d in active)
        for step in range(n_steps):
            work = {d: list(space[d])[step] for d in active if step < len(space[d])}
            pending = dict(work)
            while pending:
                points = []
                for d, setting in pending.items():
                    for v in space[d][setting]:
                        p = {**state[d], setting: v}
                        if is_valid(d, p):
                            points.append((d, p))
                evaluate(points)
                nxt = {}
                for d, setting in pending.items():
                    cands = [(v, summarize(d, {**state[d], setting: v}))
                             for v in space[d][setting]
                             if is_valid(d, {**state[d], setting: v})]
                    ok = [(v, s) for v, s in cands if is_admissible(d, s)]
                    if not ok:
                        continue
                    best_v, best_s = max(ok, key=lambda vs: vs[1]["mean_f1"])
                    grid = space[d][setting]
                    at_edge = best_v in (min(grid), max(grid)) and len(grid) > 1
                    if at_edge and extensions[(d, setting)] < MAX_EXTENSIONS:
                        new = extend(setting, grid, low_end=(best_v == min(grid)))
                        if new is not None:
                            grid.append(new)
                            grid.sort()
                            extensions[(d, setting)] += 1
                            nxt[d] = setting
                            log(f"  {d}.{setting}: best at the edge {best_v:g}; adding {new:g}")
                            continue
                    current = summarize(d, state[d])
                    if best_v != state[d][setting] and \
                            best_s["mean_f1"] > current["mean_f1"] + MOVE_EPS:
                        log(f"  round {rnd} {d}.{setting}: {state[d][setting]:g} -> {best_v:g} "
                            f"(mean F1 {current['mean_f1']:.3f} -> {best_s['mean_f1']:.3f})")
                        history[d].append(dict(round=rnd, setting=setting,
                                               old=state[d][setting], new=best_v,
                                               old_f1=current["mean_f1"],
                                               new_f1=best_s["mean_f1"]))
                        state[d][setting] = best_v
                        moved.add(d)
                pending = nxt
        log(f"round {rnd}: moved {sorted(moved) or 'nothing'}")
        active = moved
    return state, history, space


def pair_grids(dets, start, space, pairs, evaluate, summarize, is_admissible,
               is_valid=lambda d, p: True):
    """Stage 2: every combination of each pair, other settings at ``start``."""
    out = {}
    for d in dets:
        if d not in pairs:
            continue
        a, b = pairs[d]
        points = [(d, {**start[d], a: va, b: vb})
                  for va in space[d][a] for vb in space[d][b]]
        points = [(dd, p) for dd, p in points if is_valid(dd, p)]
        evaluate(points)
        cells = []
        best = None
        for _, p in points:
            s = summarize(d, p)
            ok = is_admissible(d, s)
            cells.append(dict(a=p[a], b=p[b], admissible=ok, **s))
            if ok and (best is None or s["mean_f1"] > best[1]["mean_f1"]):
                best = (p, s)
        out[d] = dict(settings=[a, b], cells=cells,
                      best=None if best is None else best[0])
    return out


def held_out(pool, candidates, seeds, log=print):
    """Stage 3: every candidate on recordings nothing was chosen on, with a bootstrap."""
    import numpy as np
    from bugarach import bench

    jobs = []
    for d, cands in candidates.items():
        for name, p in cands.items():
            k = _key(d, p)
            for regime in (*REGIMES, NULL):
                jobs.append((d, k[1], regime, list(seeds), True))
    t0 = time.time()
    res = {key: val for key, val in pool.imap_unordered(_job, jobs, chunksize=1)}
    log(f"  held-out: {len(jobs)} evaluations in {time.time() - t0:.0f} s")

    rng = np.random.RandomState(BOOTSTRAP_SEED)
    out = {}
    for d, cands in candidates.items():
        per = {}
        for name, p in cands.items():
            k = _key(d, p)
            per[name] = {r: res[(d, k[1], r)] for r in (*REGIMES, NULL)}
        idx_draws = [rng.randint(0, len(seeds), size=len(seeds)) for _ in range(BOOTSTRAP)]

        def mean_f1(name, idx):
            f = []
            for r in REGIMES:
                sc = [per[name][r]["per_seed"][i] for i in idx]
                f.append(bench.pool_scores(sc, detector=d, regime=r).f1)
            return sum(f) / 2

        full = list(range(len(seeds)))
        base = [mean_f1("shipped", idx) for idx in idx_draws]
        out[d] = {}
        for name, p in cands.items():
            q, b, n = (per[name][r] for r in (*REGIMES, NULL))
            gains = [mean_f1(name, idx) - bb for idx, bb in zip(idx_draws, base)]
            gains = [g for g in gains if math.isfinite(g)]
            out[d][name] = dict(
                params=p, f1_quiet=q["f1"], f1_busy=b["f1"],
                mean_f1=mean_f1(name, full),
                probe_quiet_per_hour=60 * q["probe_per_min"],
                probe_busy_per_hour=60 * b["probe_per_min"],
                null_per_hour=n["null_per_hour"],
                gain_vs_shipped=dict(
                    mid=float(np.median(gains)) if gains else None,
                    lo=float(np.percentile(gains, 2.5)) if gains else None,
                    hi=float(np.percentile(gains, 97.5)) if gains else None))
    return out


def full_grid(ev, det, space, is_valid, top=5):
    """Every combination of every setting for one detector, on the selection recordings."""
    names = list(space[det])
    combos = [dict(zip(names, vals)) for vals in itertools.product(*(space[det][n] for n in names))]
    combos = [c for c in combos if is_valid(det, c)]
    ev.log(f"  full grid {det}: {len(combos)} valid combinations")
    for i in range(0, len(combos), 400):
        ev.run([(det, c) for c in combos[i:i + 400]])
        ev.log(f"    {min(i + 400, len(combos))}/{len(combos)}")
    scored = [(c, ev.summary(det, c)) for c in combos]
    ok = sorted([cs for cs in scored if admissible(det, cs[1])],
                key=lambda cs: -cs[1]["mean_f1"])
    return dict(n=len(combos), n_admissible=len(ok),
                top=[dict(params=c, **s) for c, s in ok[:top]])


# ------------------------------------------------------------------ figure

NAMES = {"coact": "CoactDetect", "loco": "LoCo", "rate": "rate+context",
         "sce": "binned SCE", "cicada": "locust", "sync": "SPIKE-synch"}
ORDER = ["coact", "loco", "rate", "sce", "cicada", "sync"]


def _fmt(v):
    if isinstance(v, float) and 0 < abs(v) < 0.001:
        return f"{v:.0e}".replace("e-0", "e-")
    return f"{v:.10g}" if isinstance(v, float) else str(v)


def render(rep: dict, dest: Path) -> list[Path]:
    ho = rep.get("held_out", {})
    n_sel, n_ho = len(rep["selection_seeds"]), len(rep.get("held_out_seeds", []))
    rows = []
    for d in ORDER:
        if d not in ho:
            continue
        ship = ho[d]["shipped"]["params"]
        for name, c in ho[d].items():
            changed = ", ".join(f"{k} {_fmt(ship[k])} → {_fmt(v)}"
                                for k, v in c["params"].items() if v != ship[k]) or "—"
            g = c["gain_vs_shipped"]
            gain = ("" if name == "shipped" or g["mid"] is None else
                    f"{g['mid']:+.3f} ({g['lo']:+.3f} to {g['hi']:+.3f})")
            sel = rep["selection"].get(d, {}).get(name)
            rows.append(
                f"<tr class='{'ship' if name == 'shipped' else ''}'><td>{NAMES[d]}</td>"
                f"<td>{name}</td><td>{changed}</td>"
                f"<td>{'' if sel is None else f'{sel:.3f}'}</td>"
                f"<td>{c['f1_quiet']:.3f}</td><td>{c['f1_busy']:.3f}</td><td>{c['mean_f1']:.3f}</td>"
                f"<td>{gain}</td><td>{c['probe_quiet_per_hour']:.0f} / {c['probe_busy_per_hour']:.0f}</td>"
                f"<td>{c['null_per_hour']:.1f}</td></tr>")

    heat = []
    for fig_i, (d, pg) in enumerate(rep.get("pairs", {}).items(), start=2):
        a, b = pg["settings"]
        va = sorted({c["a"] for c in pg["cells"]})
        vb = sorted({c["b"] for c in pg["cells"]})
        f1s = [c["mean_f1"] for c in pg["cells"] if math.isfinite(c["mean_f1"])]
        lo, hi = (min(f1s), max(f1s)) if f1s else (0, 1)
        cw, ch, ml, mt = 58, 30, 110, 10
        svg = [f'<svg viewBox="0 0 {ml + cw * len(va) + 10} {mt + ch * len(vb) + 50}" '
               f'width="{ml + cw * len(va) + 10}" height="{mt + ch * len(vb) + 50}">']
        ship = rep["shipped"][d]
        for c in pg["cells"]:
            x = ml + cw * va.index(c["a"])
            y = mt + ch * (len(vb) - 1 - vb.index(c["b"]))
            t = 0 if not math.isfinite(c["mean_f1"]) or hi == lo else (c["mean_f1"] - lo) / (hi - lo)
            light = 95 - 55 * t
            fill = f"hsl(213,70%,{light:.0f}%)" if c["admissible"] else "var(--surface)"
            stroke = ("#1b1b1a" if pg["best"] and c["a"] == pg["best"][a] and c["b"] == pg["best"][b]
                      else "#8a8983" if c["a"] == ship[a] and c["b"] == ship[b] else "#d8d7d2")
            sw = 2.5 if stroke != "#d8d7d2" else 1
            dash = ' stroke-dasharray="4 3"' if stroke == "#8a8983" else ""
            svg.append(f'<rect x="{x + 1}" y="{y + 1}" width="{cw - 2}" height="{ch - 2}" fill="{fill}" '
                       f'stroke="{stroke}" stroke-width="{sw}"{dash}><title>{a} {_fmt(c["a"])}, '
                       f'{b} {_fmt(c["b"])}: mean F1 {c["mean_f1"]:.3f}, '
                       f'{c["null_per_hour"]:.1f} false alarms/hour on the empty recording'
                       f'{"" if c["admissible"] else " — over a false-alarm limit"}</title></rect>')
        for i, v in enumerate(va):
            svg.append(f'<text x="{ml + cw * i + cw / 2}" y="{mt + ch * len(vb) + 14}" class="tick" '
                       f'text-anchor="middle">{_fmt(v)}</text>')
        for j, v in enumerate(vb):
            svg.append(f'<text x="{ml - 6}" y="{mt + ch * (len(vb) - 1 - j) + ch / 2 + 4}" class="tick" '
                       f'text-anchor="end">{_fmt(v)}</text>')
        svg.append(f'<text x="{ml + cw * len(va) / 2}" y="{mt + ch * len(vb) + 36}" class="lab" '
                   f'text-anchor="middle">{a}</text>')
        svg.append(f'<text x="14" y="{mt + ch * len(vb) / 2}" class="lab" text-anchor="middle" '
                   f'transform="rotate(-90 14 {mt + ch * len(vb) / 2})">{b}</text></svg>')
        heat.append(f'<div class="heat"><p class="cap"><b>Figure {fig_i}. {NAMES[d]}: mean F1 over every '
                    f'combination of {a} and {b}</b>, the other settings shipped, on the {n_sel} selection '
                    f'recordings. Darker is higher F1 (range {lo:.3f} to {hi:.3f}); an empty cell breaks a '
                    f'false-alarm limit. Solid black outline: the best admissible cell. Dashed grey: '
                    f'shipped.</p>{"".join(svg)}</div>')

    full = ""
    for d, fg in rep.get("full", {}).items():
        full += (f"<p><b>{NAMES[d]}, every combination</b>: {fg['n']} valid, "
                 f"{fg['n_admissible']} under both limits; the best on the selection recordings is "
                 f"mean F1 {fg['top'][0]['mean_f1']:.3f} at "
                 + ", ".join(f"{k} {_fmt(v)}" for k, v in fg['top'][0]['params'].items())
                 + (". Its held-out score is the row <i>full</i> above.</p>" if "full" in ho.get(d, {})
                    else ". Those are the same settings as a candidate already in the table.</p>")
                 ) if fg["top"] else ""

    html = f"""<meta charset="utf-8"><title>Full settings search</title>
<style>
:root {{ --surface:#fcfcfb; --ink:#1b1b1a; --muted:#6b6a64; --rule:#e4e3de; }}
body {{ background:var(--surface); color:var(--ink); font:14px/1.45 system-ui, sans-serif;
        margin:0; padding:20px 24px; max-width:1300px; }}
table {{ border-collapse:collapse; font-size:13px; }}
td, th {{ padding:3px 8px; border-bottom:1px solid var(--rule); text-align:left; vertical-align:top; }}
tr.ship td {{ border-top:2px solid #b9b8b2; }}
.cap {{ max-width:1250px; }}
.heats {{ display:flex; flex-wrap:wrap; gap:24px; }}
.heat .cap {{ max-width:520px; font-size:13px; }}
svg .tick {{ font-size:10.5px; fill:var(--muted); }} svg .lab {{ font-size:12px; fill:var(--ink); }}
</style>
<p class="cap"><b>Figure 1. Every declared setting of the six detectors, searched on the simulator and
scored on recordings the search never saw.</b> <i>shipped</i> is the stored operating point; <i>rounds</i>
moved one setting at a time with the others at their current best; <i>pair</i> searched every
combination of two settings; <i>full</i>, where present, searched every combination of all of them.
Each candidate was chosen on {n_sel} simulated recordings per background ("chosen on" column: mean F1
there) and then scored on {n_ho} different ones (every other F1 column). Gain is the held-out mean F1
minus the shipped point's, with its 95% bootstrap interval ({BOOTSTRAP} resamples of recordings); where
the interval includes zero the search found nothing the bench can tell apart from the shipped point.
Only candidates under both false-alarm limits were eligible. False alarms are per hour: in a dense
stretch with nothing planted inside an ordinary recording (quiet / busy background), and on a whole
recording with nothing planted. F1 is the harmonic mean of recall and precision.</p>
<table><tr><th>detector</th><th>candidate</th><th>settings that differ from shipped</th>
<th>mean F1, chosen on</th><th>F1 quiet</th><th>F1 busy</th><th>mean F1</th>
<th>gain vs shipped (95% interval)</th><th>false alarms/hour, empty stretch (quiet / busy)</th>
<th>false alarms/hour, empty recording</th></tr>{"".join(rows)}</table>
{full}
<div class="heats">{"".join(heat)}</div>
"""
    page = dest / "full_search.html"
    page.write_text(html, encoding="utf-8")
    written = [page]
    try:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as p:
            br = p.chromium.launch()
            pg = br.new_page(viewport={"width": 1340, "height": 900}, device_scale_factor=2)
            pg.goto(page.resolve().as_uri())
            pg.screenshot(path=str(dest / "full_search.png"), full_page=True)
            br.close()
        written.append(dest / "full_search.png")
    except Exception as exc:  # noqa: BLE001 — the HTML is the figure; the PNG is a preview
        print(f"(no PNG: {exc})", file=sys.stderr)
    return written


# ------------------------------------------------------------------ main

def main(argv=None) -> int:
    from bugarach.paths import darkroom, unresolved_message

    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--seeds", type=int, default=48,
                    help="recordings per point for selection; held-out uses as many more")
    ap.add_argument("--workers", type=int, default=8)
    ap.add_argument("--full", nargs="*", default=[], choices=list(SPACE),
                    help="also search every combination for these detectors")
    ap.add_argument("--only", nargs="*", default=None, choices=list(SPACE))
    ap.add_argument("--smoke", action="store_true", help="2 recordings, 2 values per setting")
    ap.add_argument("--out", type=Path, default=None,
                    help="destination (default: <darkroom>/<date>-full-search)")
    a = ap.parse_args(argv)

    if a.out:
        dest = a.out.expanduser()
    else:
        root = darkroom(create=True)
        if root is None:
            print(unresolved_message(), file=sys.stderr)
            return 2
        dest = root / f"{datetime.date.today().isoformat()}-full-search"
    dest.mkdir(parents=True, exist_ok=True)

    def log(msg):
        print(f"{datetime.datetime.now():%H:%M:%S} {msg}", flush=True)

    dets = a.only or list(SPACE)
    space = {d: {k: list(v) for k, v in SPACE[d].items()} for d in dets}
    n = a.seeds
    if a.smoke:
        n = 2
        for d in dets:
            for k, v in space[d].items():
                sv = shipped_value(d, k)
                space[d][k] = sorted({sv, v[0] if v[0] != sv else v[-1]})
    shipped = {d: {k: shipped_value(d, k) for k in space[d]} for d in dets}
    for d in dets:
        for k in space[d]:
            if shipped[d][k] not in space[d][k]:
                space[d][k] = sorted(space[d][k] + [shipped[d][k]])
    sel, ho = list(range(1, n + 1)), list(range(n + 1, 2 * n + 1))
    rep = dict(started=datetime.datetime.now().isoformat(timespec="seconds"),
               selection_seeds=sel, held_out_seeds=ho, space=space, shipped=shipped,
               stage="started", selection={})

    def save():
        (dest / "search.json").write_text(json.dumps(rep, indent=1, default=str))

    save()
    t_start = time.time()
    with Pool(a.workers) as pool:
        ev = Evaluator(pool, sel, log)
        log("stage 1: coordinate rounds")
        state, history, grown = coordinate_rounds(
            dets, shipped, space, ev.run, ev.summary, admissible, valid, log)
        rep.update(stage="rounds done", rounds=dict(state=state, history=history, grids=grown))
        save()

        log("stage 2: two-setting grids")
        pairs = pair_grids(dets, shipped, grown, PAIRS, ev.run, ev.summary, admissible, valid)
        rep.update(stage="pairs done", pairs=pairs)
        save()

        candidates = {}
        for d in dets:
            c = {"shipped": shipped[d]}
            if state[d] != shipped[d]:
                c["rounds"] = state[d]
            if d in pairs and pairs[d]["best"] and pairs[d]["best"] not in c.values():
                c["pair"] = pairs[d]["best"]
            candidates[d] = c
            rep["selection"][d] = {name: ev.summary(d, p)["mean_f1"] for name, p in c.items()}

        log("stage 3: held-out confirmation")
        rep["held_out"] = held_out(pool, candidates, ho, log)
        rep.update(stage="held-out done")
        save()
        for p in render(rep, dest):
            log(f"wrote {p}")

        for d in a.full:
            if d not in dets:
                continue
            log(f"stage 4: every combination for {d}")
            # The base grids, not the ones stage 1 widened: a widened LoCo grid runs to
            # ~30,000 combinations, against 3,000 for the base one.
            rep.setdefault("full", {})[d] = full_grid(ev, d, space, valid)
            save()
            top = rep["full"][d]["top"]
            if top and top[0]["params"] not in candidates[d].values():
                cand = {"shipped": shipped[d], "full": top[0]["params"]}
                rep["held_out"][d]["full"] = held_out(pool, {d: cand}, ho, log)[d]["full"]
                rep["selection"][d]["full"] = top[0]["mean_f1"]
            rep.update(stage=f"full {d} done")
            save()
            for p in render(rep, dest):
                log(f"wrote {p}")

    rep.update(stage="finished", finished=datetime.datetime.now().isoformat(timespec="seconds"),
               elapsed_min=round((time.time() - t_start) / 60, 1),
               evaluations=ev.n_points)
    save()
    log(f"finished in {rep['elapsed_min']} min")
    for d in dets:
        for name, c in rep["held_out"][d].items():
            g = c["gain_vs_shipped"]
            gain = "" if name == "shipped" or g["mid"] is None else \
                f"gain {g['mid']:+.3f} [{g['lo']:+.3f}, {g['hi']:+.3f}]"
            log(f"  {NAMES[d]:13s} {name:8s} held-out mean F1 {c['mean_f1']:.3f} {gain}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
