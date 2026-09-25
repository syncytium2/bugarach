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
``min_rois`` and SPIKE-synch's ``min_n`` are **not** searched: since 2026-09-25 each recording's
ADR-0008 floor sets them (``bench.run_detector``; ADR-0008 decision 6, ADR-0009 decision 3), and a
planted event under that floor is "don't care" in the score (ADR-0009 decision 2). Every run
record says so: ``"floor": bench.FLOOR_LABEL``.

**Bracketing.** A setting is extended past a grid edge up to :data:`MAX_EXTENSIONS` times. Every
candidate whose chosen value still sits at an edge of the final grid, or on an axis that used up
its extensions, is recorded as **unbracketed** in ``search.json`` (``bracketing``), and
``tools/score_bench_candidates.py`` carries that into ``candidates.json`` as not adoptable.

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
``MAX_PRECISION_DROP`` between the backgrounds. Since ADR-0009 the probe is read off the
elevated-rate recording (``bench.evaluate_elevated_rate``, seeds + ``ELEVATED_SEED_OFFSET``), and
that recording's calls outside its stretch are held to ``MAX_FALSE_POSITIVES_PER_HOUR`` at the
quiet background too.

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
import dataclasses
import datetime
import itertools
import json
import math
import sys
import time
from multiprocessing import Pool
from pathlib import Path

BENCH_ENV = "BUGARACH_BENCH"
#: Which bench module every stage and every worker reads. ``--bench`` sets it before the pool
#: starts, and workers spawned on Windows re-import this module and read it again, so no
#: stage can score one stream's recordings against the other's settings. Always set by
#: ``main`` — a value left in the shell cannot redirect a run silently.
BENCHES = {"fast": "bugarach.bench", "slow": "bugarach.bench_slow",
           "combined": "bugarach.bench_combined"}


def _load_bench():
    """The bench module this run searches: ``bugarach.bench`` unless ``--bench slow``."""
    import importlib
    import os

    name = os.environ.get(BENCH_ENV, BENCHES["fast"])
    if name not in BENCHES.values():
        raise ValueError(f"{BENCH_ENV}={name!r} is not one of {sorted(BENCHES.values())}")
    return importlib.import_module(name)


_bench = _load_bench()

REGIMES = ("baseline_quiet", "baseline_busy")
NULL = "null"
#: The crowded tail (bench.TAIL_RECORDING): planted events 6 s apart and more of them,
#: fitted to the most crowded real recordings. A CHECK on held-out candidates, never a
#: selection input — bench.py forbids calibrating on it. It exists here because the
#: settings a search is most likely to fit to the bench's 120 s spacing (context windows,
#: minimum distances) are exactly the ones this recording punishes.
TAIL = ("tail_quiet", "tail_busy")
N_TAIL = 12
MAX_ROUNDS = 4
MAX_EXTENSIONS = 6
"""Extensions per axis over a whole search. 3 until 2026-09-25, when fast SPIKE-synch's ``dt`` and
``C_min`` stopped at it unbracketed; raised for the final-parameters night, value set from the
pilot's timings."""
MOVE_EPS = 0.002
BOOTSTRAP = 400
BOOTSTRAP_SEED = 20260917

#: Grids per declared setting. The shipped value is added if missing.
#:
#: **Declared in `bugarach.bench.FULL_GRIDS`** since 2026-09-17, so goal 2's nested
#: cross-validation searches the same axes this search does rather than a second copy of
#: them. Kept under the old name here because this module's own stages read it.
def _space(b):
    return {d: {k: list(v) for k, v in axes.items()} for d, axes in b.FULL_GRIDS.items()}


SPACE = _space(_bench)
#: Pairs searched as full two-setting grids (`bench.FULL_GRID_PAIRS`).
PAIRS = dict(_bench.FULL_GRID_PAIRS)


def use_bench(which: str):
    """Point this module, and every worker it starts, at the ``fast`` or ``slow`` bench."""
    import os

    global _bench, SPACE, PAIRS
    os.environ[BENCH_ENV] = BENCHES[which]
    _bench = _load_bench()
    SPACE = _space(_bench)
    PAIRS = dict(_bench.FULL_GRID_PAIRS)
    return _bench


PERCENTILE = {"threshold_pctile", "sce_percentile"}
INTEGER = {"n_synchronous_frames", "sce_min_distance_frames", "min_rois", "min_n"}
#: A count is extended as a count. Until 2026-09-23 only the first two were listed, so
#: `min_rois` and `min_n` fell through to halving: the slow search walked `sce.min_rois`
#: 3 → 1.5 → 0.75 → 0.375, and the combined search returned SPIKE-synch at `min_n` 0.25 with
#: its largest gain of the six, which could not be installed (PR #754). An all-integer grid
#: is treated the same way even when its name is missing here.
COUNT_FLOOR = {"min_rois": 3, "min_n": 2}
"""The smallest value a count may be extended to, for a caller that still searches one: since
2026-09-25 neither ``min_rois`` nor ``min_n`` is in ``FULL_GRIDS`` (ADR-0008's floor sets both)."""
FRACTION = {"C_threshold", "C_min"}


def shipped_value(det: str, setting: str):
    """The shipped value: declared in OPERATING_POINTS, or the detector's own default."""
    import inspect

    bench = _load_bench()
    from bugarach.detectors import (cicada_detect, coact_detect, loco_detect,
                                    rate_detect, sce_detect, sync_detect)
    params = bench.OPERATING_POINTS[det].params
    if setting in params:
        return params[setting]
    fn = {"loco": loco_detect, "sce": sce_detect, "cicada": cicada_detect,
          "coact": coact_detect, "rate": rate_detect, "sync": sync_detect}[det]
    return inspect.signature(fn).parameters[setting].default


def valid(det: str, p: dict) -> bool:
    """Settings that make sense together, AND that this bench can honestly measure.

    `bench.settings_are_valid` is the detectors' own rule, read by goal 2's per-fold search
    too, so neither admits a combination the other rejects. On top of it, a context window
    wider than the planted spacing puts other events inside the null the threshold comes
    from — and a contaminated null sits high, so the setting that breaks this scores BETTER
    here. The 2026-09-17 sliding search chose 240 s contexts on a bench that plants at 120 s
    for exactly that reason, and `tests/test_bench.py` refused the result after the run.
    """
    return (_bench.settings_are_valid(det, p)
            and _bench.context_fits_the_null(p, _bench.BENCH_RECORDING["min_sep_sec"]))


def extend(setting: str, grid: list, low_end: bool):
    """One more value past an edge of ``grid``, or None when the setting cannot go further."""
    edge = min(grid) if low_end else max(grid)
    if setting in PERCENTILE:
        new = 100 - (100 - edge) * 2 if low_end else 100 - (100 - edge) / 2
        new = max(new, 1.0)
    elif setting in INTEGER or all(isinstance(g, int) and not isinstance(g, bool) for g in grid):
        floor = COUNT_FLOOR.get(setting, 1)
        if low_end:
            new = max(floor, int(edge) - 1 if edge <= 4 else int(edge) // 2)
        else:
            new = int(edge) + 1 if edge < 4 else int(edge) * 2
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

#: What a NaN setting is called in a cache key. Binned SCE ships `merge_gap_sec` NaN ("do
#: not merge"), and NaN never equals itself — so a key holding one matches nothing, INCLUDING
#: the copy of itself that comes back from a worker process through pickling. That is a cache
#: that silently never hits, and here it was a KeyError two axes into the search.
NAN_KEY = "__nan__"


def _key(det, params):
    """A hashable, NaN-safe key for one (detector, settings) pair."""
    return det, tuple(sorted(
        (k, NAN_KEY if isinstance(v, float) and math.isnan(v) else v)
        for k, v in params.items()))


def _job(args):
    """One (detector, settings, regime) over a list of recordings.

    Returns a compact summary for selection, and the per-recording Scores (or empty-
    recording rates) when ``keep`` — only the held-out stage needs those.
    """
    det, key_items, param_items, regime, seeds, keep = args
    bench = _load_bench()
    from bugarach.score import score_stream

    # `key_items` is what the cache is keyed by (NaN-safe); `param_items` is what the
    # detector is actually run with, NaN and all.
    items = key_items
    params = dict(param_items)
    try:
        if regime == NULL:
            rates = [bench.false_positives_per_hour(det, seeds=(s,), **params) for s in seeds]
            return (det, items, regime), dict(null_per_hour=sum(rates) / len(rates),
                                              per_seed=rates if keep else None)
        scores = []
        for s in seeds:
            if regime in TAIL:
                rec, gt = bench.make_tail_recording("baseline_" + regime.split("_", 1)[1], s)
            else:
                rec, gt = bench.make_recording(regime, s)
            scores.append(score_stream(gt, bench.run_detector(det, rec, **params)))
        # ADR-0009: the stretch is no longer inside the scored recording, so the probe is read off
        # the elevated-rate recording, same seeds + ELEVATED_SEED_OFFSET. Skipping it would leave
        # the probe NaN, and NaN fails every budget: loud, not silent.
        probe = (None if regime in TAIL
                 else bench.evaluate_elevated_rate(det, regime, seeds, **params))
    except (ValueError, NotImplementedError) as e:
        # A detector refusing a COMBINATION of settings is a fact about the detector, not a
        # crash: `loco` refuses a guard under the symmetric null, and an hour of search must
        # not die on one such pair. Recorded and reported, never retried and never silent —
        # `Evaluator.run` prints each distinct refusal once, and the candidate is
        # inadmissible rather than missing.
        return (det, items, regime), dict(refused=f"{type(e).__name__}: {e}")
    r = bench.pool_scores(scores, detector=det, regime=regime, seeds=tuple(seeds), probe=probe)
    return (det, items, regime), dict(f1=r.f1, recall=r.recall, precision=r.precision,
                                      probe_per_min=r.hot_fa_per_min,
                                      elevated_out_per_hour=r.elevated_out_per_hour,
                                      n_hit=r.n_hit,
                                      n_planted=r.n_planted,
                                      merged_calls=r.n_merged_calls,
                                      under_floor=bench.under_floor_report(r),
                                      per_seed=scores if keep else None)


ELEVATED = "elevated_"
"""Prefix of the elevated-rate recording's kind in :func:`warm_floors`, one per regime."""


def _warm(args):
    """Compute one recording's ADR-0008 floor into the shared cache (``bench.FLOOR_CACHE_ENV``)."""
    kind, seed = args
    bench = _load_bench()
    if kind == NULL:
        rec, gt = bench.make_null_recording(seed)
    elif kind in TAIL:
        rec, gt = bench.make_tail_recording("baseline_" + kind.split("_", 1)[1], seed)
    elif kind.startswith(ELEVATED):
        rec, gt = bench.make_elevated_rate_recording(kind[len(ELEVATED):], seed)
    else:
        rec, gt = bench.make_recording(kind, seed)
    f = gt.params.get("event_floor")
    return kind, seed, None if f is None else int(f)


def warm_floors(pool, sel, ho, log=print) -> dict:
    """Every recording's floor once, in parallel, before anything is scored — so no worker
    recomputes one another worker already has. Returns ``{kind: {seed: floor}}``."""
    jobs = [(k, s) for k in (*REGIMES, NULL) for s in (*sel, *ho)]
    jobs += [(k, s) for k in TAIL for s in (*list(sel)[:N_TAIL], *list(ho)[:N_TAIL])]
    if hasattr(_load_bench(), "make_elevated_rate_recording"):     # ADR-0009 decision 1
        jobs += [(ELEVATED + k, s) for k in REGIMES for s in (*sel, *ho)]
    t0 = time.time()
    out: dict = {}
    for kind, seed, f in pool.imap_unordered(_warm, jobs, chunksize=1):
        out.setdefault(kind, {})[seed] = f
    log(f"  floors: {len(jobs)} recordings in {time.time() - t0:.0f} s")
    return out


def bracketing(det: str, params: dict, grids: dict, declared: dict,
               max_extensions: int) -> dict:
    """Is this candidate an interior optimum on every axis it could move along?

    An axis is unbracketed when the chosen value sits at an end of the final grid. ``reason``
    says why it stayed there: ``cap`` (the axis used up :data:`MAX_EXTENSIONS`), ``limit`` (the
    grid cannot go further, e.g. a guard of 0), or ``edge`` (extension stopped for another
    reason). The runbook's rule is that any of the three makes the candidate not adoptable;
    ``only_at_limits`` says when every one of them is a ``limit``, for the reader.
    """
    axes = {}
    for k, values in grids.items():
        numeric = all(isinstance(v, (int, float)) and not isinstance(v, bool) for v in values)
        if not (numeric and len(values) > 1) or not _bench.setting_applies(det, k, params):
            continue
        v = params.get(k)
        if v is None or (isinstance(v, float) and math.isnan(v)):
            continue
        if v not in (min(values), max(values)):
            continue
        low = v == min(values)
        used = len(values) - len(declared.get(k, values))
        can = extend(k, list(values), low_end=low) is not None
        reason = "limit" if not can else "cap" if used >= max_extensions else "edge"
        axes[k] = dict(side="low" if low else "high", value=v, extensions_used=max(used, 0),
                       reason=reason)
    return dict(bracketed=not axes, unbracketed_axes=axes,
                only_at_limits=bool(axes) and all(a["reason"] == "limit" for a in axes.values()))


class Evaluator:
    """Caches pooled results per (detector, settings, regime) and runs batches in parallel."""

    def __init__(self, pool, seeds, log=print):
        self.pool, self.seeds, self.log = pool, list(seeds), log
        self.cache: dict = {}
        self.n_points = 0
        self.refusals: dict = {}      # message -> the detector that refused, logged once each
        self.crowded = False          # set True to score the crowded recordings per candidate

    def run(self, points):
        """``points``: iterable of (det, params). Fills the cache for every recording kind.

        The crowded recordings are scored here, for EVERY candidate, because they are a veto
        now and a veto has to be in front of the choice. Scoring them only for the survivors
        is what let the 2026-09-17 search propose four settings that lose 0.25 to 0.32 mean
        F1 there (`bench.MAX_CROWDED_DROP`). They cost about a quarter more per candidate:
        12 recordings per background against 48.
        """
        todo = []
        for det, params in points:
            k = _key(det, params)
            real = tuple(sorted(params.items()))
            for regime in (*REGIMES, NULL):
                if (k[0], k[1], regime) not in self.cache:
                    todo.append((det, k[1], real, regime, self.seeds, False))
            if self.crowded:
                for regime in TAIL:
                    if (k[0], k[1], regime) not in self.cache:
                        todo.append((det, k[1], real, regime, self.seeds[:N_TAIL], False))
        if not todo:
            return
        t0 = time.time()
        for key, val in self.pool.imap_unordered(_job, todo, chunksize=1):
            self.cache[key] = val
            why = val.get("refused")
            if why and why not in self.refusals:
                self.refusals[why] = key[0]
                self.log(f"    {key[0]}: a combination is refused — {why}")
        self.n_points += len(todo) // 3
        self.log(f"    {len(todo)} evaluations in {time.time() - t0:.0f} s")

    def summary(self, det, params):
        k = _key(det, params)
        q, b, n = (self.cache[(k[0], k[1], r)] for r in (*REGIMES, NULL))
        if any(r.get("refused") for r in (q, b, n)):
            # Scored nowhere, so it cannot win: admissibility reads mean_f1 and every budget
            # here, and NaN fails all of them.
            nan = float("nan")
            return dict(f1_quiet=nan, f1_busy=nan, mean_f1=nan,
                        precision_quiet=nan, precision_busy=nan,
                        probe_quiet=nan, probe_busy=nan, null_per_hour=nan,
                        elevated_out_quiet=nan, elevated_out_busy=nan,
                        refused=next(r["refused"] for r in (q, b, n) if r.get("refused")))
        out = dict(f1_quiet=q["f1"], f1_busy=b["f1"],
                   mean_f1=(q["f1"] + b["f1"]) / 2,
                   precision_quiet=q["precision"], precision_busy=b["precision"],
                   probe_quiet=q["probe_per_min"], probe_busy=b["probe_per_min"],
                   null_per_hour=n["null_per_hour"],
                   elevated_out_quiet=q["elevated_out_per_hour"],
                   elevated_out_busy=b["elevated_out_per_hour"])
        if self.crowded:
            tq, tb = (self.cache.get((k[0], k[1], r)) for r in TAIL)
            if tq and tb and not (tq.get("refused") or tb.get("refused")):
                out["crowded_mean_f1"] = (tq["f1"] + tb["f1"]) / 2
        return out


def make_admissible(reference_crowded=None):
    """The admissibility rule, with the crowded-recording veto bound to a reference.

    ``reference_crowded`` maps a detector to the crowded mean F1 of the setting a candidate
    would replace — the shipped one. Without it the rule is the three budgets alone, which
    is what every search before 2026-09-17 applied and what let the merge-gap artifact
    through.
    """
    bench = _load_bench()

    def admissible(det: str, s: dict) -> bool:
        ceiling = bench.MAX_PROBE_PER_MIN[det]
        swing = abs(s["precision_quiet"] - s["precision_busy"])
        ok = (math.isfinite(s["f1_quiet"]) and math.isfinite(s["f1_busy"])
              and s["probe_quiet"] <= ceiling and s["probe_busy"] <= ceiling
              and s["null_per_hour"] <= bench.MAX_FALSE_POSITIVES_PER_HOUR[det]
              # ADR-0009: outside its stretch the elevated-rate recording is a recording with
              # nothing planted, held to the same budget. At the quiet background only, the one
              # that budget was measured on; the busy figure is reported beside it, not gated.
              and s["elevated_out_quiet"] <= bench.MAX_FALSE_POSITIVES_PER_HOUR[det]
              and math.isfinite(swing) and swing <= bench.MAX_PRECISION_DROP[det])
        if not ok or reference_crowded is None:
            return ok
        ref = reference_crowded.get(det)
        got = s.get("crowded_mean_f1")
        if ref is None:
            return ok
        # Not scored there = not admissible. A candidate whose crowded score is missing is a
        # candidate nobody checked, and this budget exists because an unchecked one won.
        if got is None or not math.isfinite(got):
            return False
        return got >= ref - bench.MAX_CROWDED_DROP

    return admissible


#: The three-budget rule, for callers that have no crowded reference (and for tests).
admissible = make_admissible()


# ------------------------------------------------------------------ the search

def coordinate_rounds(dets, start, space, evaluate, summarize, is_admissible,
                      is_valid=lambda d, p: True, log=print,
                      max_rounds=None, max_extensions=None, min_gain=None):
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
    # `max_extensions=0` keeps the declared grid fixed. Goal 2 searches inside each outer
    # fold and needs that: a grid that grows per fold makes the candidate set differ
    # between folds, and then `meta.json` no longer describes what ran (WSMIP064,
    # 2026-09-17). Goal 1's own search still extends until the optimum is bracketed.
    max_rounds = MAX_ROUNDS if max_rounds is None else max_rounds
    max_extensions = MAX_EXTENSIONS if max_extensions is None else max_extensions
    # MOVE_EPS is an F1-sized epsilon: a move has to be worth more than the noise between
    # two settings. A caller scoring something else needs its own, or the search silently
    # never moves — which is what a test caught on 2026-09-17.
    min_gain = MOVE_EPS if min_gain is None else min_gain
    active = set(dets)
    for rnd in range(1, max_rounds + 1):
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
                    if not _bench.setting_applies(d, setting, state[d]):
                        continue
                    for v in space[d][setting]:
                        p = {**state[d], setting: v}
                        if is_valid(d, p):
                            points.append((d, p))
                evaluate(points)
                nxt = {}
                for d, setting in pending.items():
                    # A conditional axis under a parent that is switched off is dead weight:
                    # every value gives the same answer, and reporting it as searched is a
                    # claim nobody can back. It comes back when its parent moves, because a
                    # parent that moves reopens the round.
                    if not _bench.setting_applies(d, setting, state[d]):
                        continue
                    cands = [(v, summarize(d, {**state[d], setting: v}))
                             for v in space[d][setting]
                             if is_valid(d, {**state[d], setting: v})]
                    ok = [(v, s) for v, s in cands if is_admissible(d, s)]
                    if not ok:
                        continue
                    best_v, best_s = max(ok, key=lambda vs: vs[1]["mean_f1"])
                    grid = space[d][setting]
                    # Names have no ends: "peak" is not an edge of ("threshold", "peak"), and
                    # `extend` has nothing to double. Only a numeric axis can be at an edge
                    # or grow.
                    numeric = all(isinstance(v, (int, float)) and not isinstance(v, bool)
                                  for v in grid)
                    at_edge = (numeric and len(grid) > 1
                               and best_v in (min(grid), max(grid)))
                    if at_edge and extensions[(d, setting)] < max_extensions:
                        new = extend(setting, grid, low_end=(best_v == min(grid)))
                        if new is not None:
                            grid.append(new)
                            grid.sort()
                            extensions[(d, setting)] += 1
                            nxt[d] = setting
                            log(f"  {d}.{setting}: best at the edge {best_v:g}; adding {new:g}")
                            continue
                    current = summarize(d, state[d])
                    # WHEN THE STARTING POINT IS ITSELF INADMISSIBLE, any admissible setting
                    # beats it and the F1 comparison is the wrong question. Without this the
                    # search reports "nothing moved" and leaves a point that breaks a budget:
                    # sliding LoCo at its binned threshold fires 4.0 calls an hour on an empty
                    # recording against a limit of 3, scores a high F1 for that reason, and no
                    # admissible candidate could beat that F1. Found 2026-09-17 by the first
                    # search whose starting point was out of budget.
                    rescue = not is_admissible(d, current)
                    if best_v != state[d][setting] and (
                            rescue or best_s["mean_f1"] > current["mean_f1"] + min_gain):
                        why = " (the starting point breaks a budget)" if rescue else ""
                        log(f"  round {rnd} {d}.{setting}: {_fmt(state[d][setting])} -> "
                            f"{_fmt(best_v)} (mean F1 {current['mean_f1']:.3f} -> "
                            f"{best_s['mean_f1']:.3f}){why}")
                        history[d].append(dict(round=rnd, setting=setting,
                                               old=state[d][setting], new=best_v,
                                               old_f1=current["mean_f1"],
                                               new_f1=best_s["mean_f1"],
                                               rescued_from_inadmissible=rescue))
                        state[d][setting] = best_v
                        moved.add(d)
                pending = nxt
        log(f"round {rnd}: moved {sorted(moved) or 'nothing'}")
        active = moved
    return state, history, space


@dataclasses.dataclass(frozen=True)
class ChosenSettings:
    """What :func:`choose_settings` chose, and everything a readout needs to say about it."""

    detector: str
    params: dict
    """The chosen settings: every parameter of the starting point, with what moved moved."""
    score: float
    """``score(params)`` at the chosen settings."""
    moves: list
    """One entry per accepted move: round, setting, old, new, and both scores."""
    edges: dict
    """``{setting: "low" | "high"}`` for every axis whose chosen value sits at an end of its
    declared grid. **Data, not a refusal** — a refusal inside one fold of a cross-validation
    kills the fold, and a fold counted as zero says more about the grid than the detector
    (WSMIP064, 2026-09-17). Goal 1's own search still treats an edge as unfinished."""
    n_scored: int
    """Distinct settings ``score`` was called on. The cost, for a readout to quote."""
    n_refused: int
    """Settings ``admissible`` rejected. Zero when no gate was given."""
    grids: dict
    """The grids actually walked, so a caller can record what the search could have chosen."""


def choose_settings(detector, *, score, admissible=None, grids=None, start=None,
                    pairs=False, max_rounds=None, extend_ranges=False, min_gain=None,
                    is_valid=None, log=lambda _msg: None) -> ChosenSettings:
    """Search one detector's settings against a caller's own objective.

    **The search never sees a recording.** ``score(params) -> float`` (higher is better)
    and ``admissible(params) -> bool`` are the caller's; everything about which recordings
    are scored, how they are pooled and what budget applies stays on the caller's side.
    That is what lets goal 2 call this inside each outer fold of its nested
    cross-validation without this search ever being able to touch the held-out fold —
    the guarantee the whole comparison rests on, kept by construction rather than by care
    (option A of
    ``docs/todo/2026-09-17-how-is-the-coded-side-searched-inside-nested-cross-validation.md``,
    decided 2026-09-17; the interface is WSMIP064's).

    ``admissible=None`` means an ungated selection: every setting in the grid is a
    candidate. Goal 2 calls this twice per detector and fold, once each way.

    ``extend_ranges`` is **off** here and on in this module's own search. Goal 1 grows a
    range until the optimum is bracketed, because it ships the value. Inside a fold that
    would make the candidate set differ per fold, and the declaration on `main` would stop
    describing what ran, so the declared grid stays fixed and the edge is reported instead.

    ``pairs`` walks :data:`PAIRS` for this detector as a full two-setting grid after the
    rounds. It is a product, so it is off by default; goal 2 leaves it off.

    ``min_gain`` is how much better a setting has to be before the search moves to it, and
    it defaults to :data:`MOVE_EPS`, which is **F1-sized**. A caller whose objective is not
    an F1 must pass its own, or the search will find nothing worth moving to and return the
    starting point without saying anything was wrong.
    """
    grids = {k: list(v) for k, v in (grids or _bench.FULL_GRIDS[detector]).items()}
    start = dict(start if start is not None else
                 {k: shipped_value(detector, k) for k in grids})
    for k, values in grids.items():
        # NaN is a state, not a value to search: binned SCE ships `merge_gap_sec` NaN,
        # meaning "do not merge". Adding it to the grid would put a value in there that is
        # not equal to itself, so `min`, `max` and "is the start still the best" all stop
        # meaning what they say. The search carries it as the starting point instead.
        if isinstance(start[k], float) and math.isnan(start[k]):
            continue
        if start[k] not in values:
            grids[k] = sorted(values + [start[k]], key=lambda v: (isinstance(v, str), v))
    is_valid = is_valid or (lambda d, p: _bench.settings_are_valid(d, p))

    cache: dict = {}
    refused: set = set()

    def _score(params):
        key = tuple(sorted(params.items()))
        if key not in cache:
            cache[key] = float(score(dict(params)))
        return cache[key]

    def evaluate(points):
        for _d, p in points:
            _score(p)

    def summarize(_d, params):
        return {"mean_f1": _score(params), "params": dict(params)}

    def is_admissible(_d, summary):
        if admissible is None:
            return True
        ok = bool(admissible(dict(summary["params"])))
        if not ok:
            refused.add(tuple(sorted(summary["params"].items())))
        return ok

    state, history, grown = coordinate_rounds(
        [detector], {detector: start}, {detector: grids}, evaluate, summarize,
        is_admissible, is_valid, log, max_rounds=max_rounds,
        max_extensions=None if extend_ranges else 0, min_gain=min_gain)
    chosen = state[detector]

    if pairs and detector in PAIRS:
        got = pair_grids([detector], {detector: chosen}, grown, PAIRS, evaluate,
                         summarize, is_admissible, is_valid)
        best = got[detector]["best"]
        if best is not None and _score(best) > _score(chosen) + (MOVE_EPS if min_gain is None
                                                                 else min_gain):
            history[detector].append(dict(round="pair", setting="+".join(PAIRS[detector]),
                                          old=None, new=None,
                                          old_f1=_score(chosen), new_f1=_score(best)))
            chosen = best

    edges = {}
    for k, values in grown[detector].items():
        numeric = all(isinstance(v, (int, float)) and not isinstance(v, bool) for v in values)
        if not (numeric and len(values) > 1) or not _bench.setting_applies(detector, k, chosen):
            continue                      # a name has no ends; a switched-off axis has no choice
        if isinstance(chosen[k], float) and math.isnan(chosen[k]):
            continue                      # NaN is the starting state, not a value in the grid
        if chosen[k] in (min(values), max(values)):
            edges[k] = "low" if chosen[k] == min(values) else "high"
    return ChosenSettings(detector=detector, params=chosen, score=_score(chosen),
                          moves=history[detector], edges=edges, n_scored=len(cache),
                          n_refused=len(refused), grids=grown[detector])


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
    bench = _load_bench()

    jobs = []
    tail_seeds = list(seeds)[:N_TAIL]
    for d, cands in candidates.items():
        for name, p in cands.items():
            k = _key(d, p)
            real = tuple(sorted(p.items()))
            for regime in (*REGIMES, NULL):
                jobs.append((d, k[1], real, regime, list(seeds), True))
            for regime in TAIL:
                jobs.append((d, k[1], real, regime, tail_seeds, False))
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

        def tail_f1(name):
            k = _key(d, cands[name])
            return sum(res[(d, k[1], r)]["f1"] for r in TAIL) / len(TAIL)

        out[d] = {}
        for name, p in cands.items():
            q, b, n = (per[name][r] for r in (*REGIMES, NULL))
            gains = [mean_f1(name, idx) - bb for idx, bb in zip(idx_draws, base)]
            gains = [g for g in gains if math.isfinite(g)]
            under_floor = {r: bench.under_floor_report(bench.pool_scores(
                per[name][r]["per_seed"], detector=d, regime=r)) for r in REGIMES}
            out[d][name] = dict(
                params=p, under_floor=under_floor, f1_quiet=q["f1"], f1_busy=b["f1"],
                mean_f1=mean_f1(name, full),
                probe_quiet_per_hour=60 * q["probe_per_min"],
                probe_busy_per_hour=60 * b["probe_per_min"],
                null_per_hour=n["null_per_hour"],
                elevated_out_quiet_per_hour=q["elevated_out_per_hour"],
                elevated_out_busy_per_hour=b["elevated_out_per_hour"],
                crowded_mean_f1=tail_f1(name),
                crowded_gain_vs_shipped=tail_f1(name) - tail_f1("shipped"),
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
            crowd = f"{c['crowded_mean_f1']:.3f}"
            if name != "shipped":
                crowd += f" ({c['crowded_gain_vs_shipped']:+.3f})"
            rows.append(
                f"<tr class='{'ship' if name == 'shipped' else ''}'><td>{NAMES[d]}</td>"
                f"<td>{name}</td><td>{changed}</td>"
                f"<td>{'' if sel is None else f'{sel:.3f}'}</td>"
                f"<td>{c['f1_quiet']:.3f}</td><td>{c['f1_busy']:.3f}</td><td>{c['mean_f1']:.3f}</td>"
                f"<td>{gain}</td><td>{c['probe_quiet_per_hour']:.0f} / {c['probe_busy_per_hour']:.0f}</td>"
                f"<td>{c['null_per_hour']:.1f}</td>"
                f"<td>{crowd}</td></tr>")

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
Only candidates under all three limits in bench.py were eligible — the two false-alarm limits and the
largest allowed precision difference between the backgrounds. False alarms are per hour: in a dense
stretch with nothing planted inside an ordinary recording (quiet / busy background), and on a whole
recording with nothing planted. The last column scores each candidate on {N_TAIL} crowded recordings per background (planted events as little as 6 s apart, fitted to the most crowded real recordings), never used for choosing: a setting that only works because the ordinary bench spaces planted events 120 s apart loses here. F1 is the harmonic mean of recall and precision.</p>
<table><tr><th>detector</th><th>candidate</th><th>settings that differ from shipped</th>
<th>mean F1, chosen on</th><th>F1 quiet</th><th>F1 busy</th><th>mean F1</th>
<th>gain vs shipped (95% interval)</th><th>false alarms/hour, empty stretch (quiet / busy)</th>
<th>false alarms/hour, empty recording</th>
<th>mean F1, crowded recordings (change vs shipped)</th></tr>{"".join(rows)}</table>
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
    ap.add_argument("--sliding", action="store_true",
                    help="search LoCo and CoactDetect in their SLIDING window mode: the mode "
                         "is fixed, everything else is searched. Their shipped points are "
                         "binned because no calibrated sliding value exists yet, and this is "
                         "what produces one")
    ap.add_argument("--no-crowded-veto", action="store_true",
                    help="do NOT refuse a candidate that loses on the crowded recordings. The "
                         "2026-09-17 search ran this way by default and proposed four settings "
                         "that lose 0.25 to 0.32 mean F1 there (bench.MAX_CROWDED_DROP)")
    ap.add_argument("--bench", choices=sorted(BENCHES), default="fast",
                    help="which stream's bench to search: bugarach.bench (fast, the default) "
                         "or bugarach.bench_slow. Every stage and every worker reads the one "
                         "chosen here (docs/handoffs/2026-09-21-slow-bench.md)")
    ap.add_argument("--max-extensions", type=int, default=MAX_EXTENSIONS,
                    help=f"extensions per axis past a grid edge (default {MAX_EXTENSIONS})")
    ap.add_argument("--out", type=Path, default=None,
                    help="destination (default: <darkroom>/<date>-full-search, with -slow "
                         "appended for --bench slow, so a fast and a slow search on the same "
                         "day never write one folder)")
    a = ap.parse_args(argv)
    use_bench(a.bench)

    if a.out:
        dest = a.out.expanduser()
    else:
        root = darkroom(create=True)
        if root is None:
            print(unresolved_message(), file=sys.stderr)
            return 2
        suffix = "" if a.bench == "fast" else f"-{a.bench}"
        dest = root / f"{datetime.date.today().isoformat()}-full-search{suffix}"
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
    if a.sliding:
        # The mode is FIXED, not searched: sliding is chosen because calls should not move
        # with the grid, which F1 on this bench cannot see (`bench.NOT_SEARCHED`). What is
        # searched is every other setting, in that mode.
        for d in ("loco", "coact"):
            if d in shipped:
                shipped[d]["window_mode"] = "sliding"
                shipped[d]["detection_mode"] = "threshold"
                space[d].pop("detection_mode", None)
                space[d].pop("peak_prominence", None)
                space[d].pop("peak_min_distance_sec", None)
    for d in dets:
        for k in space[d]:
            if shipped[d][k] not in space[d][k]:
                space[d][k] = sorted(space[d][k] + [shipped[d][k]],
                                     key=lambda v: (isinstance(v, str), v))
    # THE STARTING POINT HAS TO BE ONE THIS BENCH CAN MEASURE. A shipped point the validity
    # rules refuse is never evaluated, so the first thing that asks for its score gets a
    # cache miss — which is how this failed on 2026-09-17, a KeyError several hundred lines
    # from the cause. Say it instead.
    bad = {d: shipped[d] for d in dets if not valid(d, shipped[d])}
    if bad:
        for d, p in bad.items():
            context = p.get("context_win_sec", p.get("context_win"))
            print(f"{NAMES[d]}: the shipped operating point is not measurable on this bench "
                  f"— context {context} s against planted events "
                  f"{_bench.BENCH_RECORDING['min_sep_sec']:.0f} s apart"
                  if not _bench.context_fits_the_null(
                      p, _bench.BENCH_RECORDING["min_sep_sec"])
                  else f"{NAMES[d]}: the shipped operating point is not a valid combination",
                  file=sys.stderr)
        print("Nothing was searched. Fix the operating point, or search a detector that has "
              "a measurable one with --only.", file=sys.stderr)
        return 2

    sel, ho = list(range(1, n + 1)), list(range(n + 1, 2 * n + 1))
    rep = dict(started=datetime.datetime.now().isoformat(timespec="seconds"),
               bench=_bench.__name__,
               floor=(_bench.FLOOR_LABEL if _bench.floor_enabled()
                      else f"pre-ADR-0008 ({_bench.FLOOR_SWITCH_ENV}=off)"),
               max_extensions=a.max_extensions,
               selection_seeds=sel, held_out_seeds=ho, space=space, shipped=shipped,
               stage="started", selection={})
    # Set before the pool starts: workers spawned on Windows inherit it, and each recording's
    # floor is then computed once between all of them (`warm_floors`), not once per worker.
    # A cache already named in the environment wins: an --out in the Dropbox darkroom would
    # otherwise sync hundreds of small files, and a machine-local cache is shared across runs.
    import os
    os.environ.setdefault(_bench.FLOOR_CACHE_ENV, str(dest / "floor_cache"))

    def save():
        (dest / "search.json").write_text(json.dumps(rep, indent=1, default=str))

    save()
    t_start = time.time()
    with Pool(a.workers) as pool:
        ev = Evaluator(pool, sel, log)
        ev.crowded = not a.no_crowded_veto
        log("floors: each recording's ADR-0008 floor, once")
        floors = warm_floors(pool, sel, ho, log)
        rep["recording_floors"] = {k: {str(s): f for s, f in sorted(v.items())}
                                   for k, v in floors.items()}
        save()
        gate = admissible
        if ev.crowded:
            # The reference is what the setting a candidate would REPLACE scores on the
            # crowded recordings — and under `--sliding` that is the point the detector
            # actually ships at, not the sliding-forced starting point.
            #
            # Getting this wrong cost a run on 2026-09-17. Anchoring to sliding-at-binned-
            # values held every candidate to the crowded score of a point that ships
            # NOWHERE and is itself over budget, and sliding LoCo came out with no
            # admissible setting at all. Against what LoCo really ships, the same candidate
            # is an improvement on both axes. A veto is only as honest as its reference.
            reference_points = {d: dict(_bench.OPERATING_POINTS[d].params) for d in dets}
            log("crowded reference: scoring the SHIPPED operating points on the crowded "
                "recordings — what a candidate would replace")
            ev.run([(d, reference_points[d]) for d in dets])
            reference = {d: ev.summary(d, reference_points[d]).get("crowded_mean_f1")
                         for d in dets}
            rep["crowded_reference_points"] = reference_points
            for d in dets:
                log(f"  {NAMES[d]:14s} crowded mean F1 {reference[d]:.3f}  "
                    f"(a candidate may not fall below {reference[d] - _bench.MAX_CROWDED_DROP:.3f})")
            rep["crowded_reference"] = reference
            gate = make_admissible(reference)
            save()

        log("stage 1: coordinate rounds")
        state, history, grown = coordinate_rounds(
            dets, shipped, space, ev.run, ev.summary, gate, valid, log,
            max_extensions=a.max_extensions)
        rep.update(stage="rounds done", rounds=dict(state=state, history=history, grids=grown))
        save()

        log("stage 2: two-setting grids")
        pairs = pair_grids(dets, shipped, grown, PAIRS, ev.run, ev.summary, gate, valid)
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
            rep.setdefault("bracketing", {})[d] = {
                name: bracketing(d, p, grown[d], space[d], a.max_extensions)
                for name, p in c.items()}
            for name, br in rep["bracketing"][d].items():
                if name != "shipped" and not br["bracketed"]:
                    log(f"  {NAMES[d]} {name}: UNBRACKETED on "
                        + ", ".join(f"{k} ({v['side']} {v['reason']})"
                                    for k, v in br["unbracketed_axes"].items()))

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
