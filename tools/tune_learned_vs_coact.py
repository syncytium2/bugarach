#!/usr/bin/env python3
"""Tune the leading learned detectors and CoactDetect/LoCo under nested cross-validation.

    python tools/tune_learned_vs_coact.py --out %USERPROFILE%\\runs\\<name> --device cuda --gpu-jobs 2 --jobs 12
    python tools/tune_learned_vs_coact.py --out <scratch> --jobs 4 --quick

The plan this implements, and every decision behind it, is ``HANDOFF-workstation-tuning.md``;
this docstring only says how the code maps onto it.

**Which simulation.** ``--simulation bench`` (the default) is goal 2's next comparison, as Tony
decided it on 2026-09-17 (``docs/goals/learned-model-family.md``): the bench's fitted field at its
two backgrounds, every seed at both, scored on each background's pooled F1 averaged over the two
(goal 1's rule); training half quiet, half busy; the gate's empty recording is the bench's own
(``bench.make_null_recording``), a busy-rate one reported only; the budget's reference is
CoactDetect at ``bench.OPERATING_POINTS`` as the run finds it. ``--simulation home`` is the retired
home spec the 2026-09-16 design was declared on. Below, "recording" means a named recording
(``quiet:1000``, or ``1000`` on the home spec), and "empty recording" the home spec's null twins or
the bench's null recordings.

**Nothing about a configuration is chosen with the fold it is scored on.** The bake-off folds
(``bench.fold_split``, recording seeds 1000-1023) are the outer loop. For held-out fold *h*, a
learned configuration's inner score pools, over training seeds 0, 1 and 2, the recordings of
each other fold *j* scored by a fit on the remaining folds; a hand-written configuration is
scored directly on the training recordings. The chosen configuration is refitted on all the
training folds at training seeds 0-4 and scored on *h*, once.

**Two selections read the same scores**, both declared before any result: *ungated*, the highest
pooled F1 with each learned fit at the threshold ``train`` picked; *gated*, the highest pooled F1
among candidates whose busy-window and quiet-field (0.54 twin) false-alarm rates are within one
budget shared by every model (1.6 times sliding CoactDetect's own rates at its shipped setting,
on the same training recordings). On the learned side the threshold is part of the gated
candidate, so every score is kept at every threshold of ``train.THRESHOLD_GRID``.

**Storage: one fact, one home** (Tony, 2026-09-16, via the Mac unsupervised session: the tuned
parameters are stored persistently, rationally and separably). Under ``--out``:

    meta.json                                   the declaration, machine, commit, budgets, estimate
    configs/<model|detector>/<config_key>.json  what to build and how to fit it; written before any fit
    fits/<model>/<config_key>/seed<s>__recs-<h>.json      a fit, via learn.checkpoint.save
    fits/<model>/<config_key>/seed<s>__recs-<h>.run.json  that fit's run: recordings, timings, warnings
    scores/<model>/<config_key>/seed<s>__recs-<h>__fold<j>.json  counts per recording, every threshold
    scores/<detector>/<config_key>.json         a hand-written configuration's counts, every recording
    selections/<ungated|gated>/outer<h>/<name>.json       the choice, by config_key; never parameters
    chosen/<ungated|gated>/outer<h>/<model>/seed<s>.json  the refits, loadable by `bugarach detect --model`
    chosen/<ungated|gated>/outer<h>/<detector>/detector_settings.csv  loadable by `detect --settings`
    results.json, progress.json, errors/

``config_key`` is ``learn.checkpoint.config_key``: the architecture, the full as-built config and
the training choices, in one spelling (``8 == 8.0``), and not the seed. Scores and selections name
a configuration by it and never restate its parameters.

**Priority order**, so a night cut short still leaves complete answers for the most important
models: the shipped-CoactDetect reference (the budget's source), the hand-written grids, then
``chorus_norm``, ``tube``, ``chorus_gain_norm`` and ``line_length``, each through its inner fits,
both selections and outer refits. Idle workers take the next model's work rather than wait.

``--quick`` is a smoke run, not a result: 3 folds of 2 recordings (two folds cannot nest: an outer
fold with one training fold has no inner split), 2 configurations per model (the first drawn and
the untuned), 100 training steps, one training recording per fit, training seed 0 for tuning and
0-1 for refits, and the hand-written grids thinned to their end values.
"""

from __future__ import annotations

import argparse
import dataclasses
import hashlib
import itertools
import json
import math
import os
import platform
import random
import socket
import subprocess
import sys
import time
import traceback
from concurrent.futures import FIRST_COMPLETED, ProcessPoolExecutor, wait
from pathlib import Path
from types import SimpleNamespace

# One intra-op thread per process for numpy's BLAS as well as torch (`train.THREADS`): 22
# processes each starting 48 BLAS threads would inflate every fit's wall time. Set before numpy
# is imported, and inherited by the spawned workers.
for _var in ("OMP_NUM_THREADS", "MKL_NUM_THREADS", "OPENBLAS_NUM_THREADS"):
    os.environ.setdefault(_var, "1")

import numpy as np  # noqa: E402

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "tools"))
sys.path.insert(0, str(REPO / "src"))

from fair_bakeoff import NULL_SEED_OFFSET, _make_recording, _null_twin  # noqa: E402

# ---- the declaration (HANDOFF-workstation-tuning.md, *Search spaces* and decisions 1-8) ---------

SPEC_PATH = "docs/learned/generator_spec.json"
SIMULATIONS = ("bench", "home")
# Goal 2's next comparison (docs/goals/learned-model-family.md, Tony, 2026-09-17). Decision 1: the
# bench's two backgrounds, the same as goal 1, every seed at both, scored on the mean of the two.
BENCH_REGIMES = {"quiet": "baseline_quiet", "busy": "baseline_busy"}
# Decision 3: the bench's own empty recording (bench.make_null_recording) at the quiet rate gates;
# the same at the busy rate is reported and never selects.
BENCH_NULLS = {"null_quiet": "baseline_quiet", "null_busy": "baseline_busy"}
BENCH_GATE_NULL = "null_quiet"
MAX_HAND_CONFIGS = 5000   # a full product past this is not what a coordinate-search grid means
# search_all_settings.MOVE_EPS, the epsilon a move must beat. This tool's objective is F1-sized, so
# the search's own default is the right one; it is passed rather than defaulted because a caller
# scoring anything else silently never moves (WSMIP065, 2026-09-17).
SEARCH_MIN_GAIN = 0.002
GPU_LONE_FIT_SEC = {"tube": 4.2, "chorus_norm": 6.4, "chorus_gain_norm": 6.4,
                    "line_length": 10.4}   # WSMIP064, RTX A4000, untuned 900 steps, one process
MODELS = ("chorus_norm", "tube", "chorus_gain_norm", "line_length")   # priority order
HAND = ("coact", "loco")
N_FOLDS, SEEDS_PER_FOLD = 4, 6
TUNE_SEEDS = (0, 1, 2)            # decision 8
REFIT_SEEDS = (0, 1, 2, 3, 4)
N_CONFIGS = 24
DRAW_SEED = 20260916
BUDGET_MARGIN = 1.6
GATE_TWIN = 0.54
TWIN_FACTORS = (1.0, 0.54, 0.25)
CROP, BATCH, N_TRAIN = 4096, 3, 10    # the bake-off's; n_train is min(10, n_fit) = 10 at every fit
SELECTIONS = ("ungated", "gated")

_LR_STEPS = [("lr", [3e-3, 1e-2, 3e-2]), ("steps", [900, 1800, 3600])]
LEARNED_AXES = {
    "chorus_norm": _LR_STEPS + [("roi_width", [4, 8]), ("roi_depth", [4, 6]),
                                ("top_m", [2, 4, 8])],
    "chorus_gain_norm": _LR_STEPS + [("roi_width", [4, 8]), ("roi_depth", [4, 6]),
                                     ("top_m", [2, 4, 8]), ("vote_gain", [4, 8, 16])],
    "line_length": _LR_STEPS + [("n_scales", [3, 4, 6]), ("width", [8, 16]),
                                ("vote_gain", [4, 8, 16])],
    "tube": _LR_STEPS + [("n_scales", [3, 4, 6]), ("width", [8, 16]), ("max_ratio", [40, 80])],
}
UNTUNED = {
    "chorus_norm": dict(lr=1e-2, steps=900, roi_width=4, roi_depth=4, top_m=4),
    "chorus_gain_norm": dict(lr=1e-2, steps=900, roi_width=4, roi_depth=4, top_m=4, vote_gain=8),
    "line_length": dict(lr=1e-2, steps=900, n_scales=4, width=8, vote_gain=8),
    "tube": dict(lr=1e-2, steps=900, n_scales=4, width=8, max_ratio=40),
}
HAND_AXES = {   # the tip's grids after #597, written out (decision 3); sliding (decision 7)
    "coact": [("alpha", [1e-1, 3e-2, 1e-2, 3e-3, 1e-3, 3e-4, 1e-4, 3e-5, 1e-5, 1e-6, 1e-7]),
              ("int_win_sec", [1.0, 2.0, 4.0]), ("context_win_sec", [30.0, 60.0, 120.0])],
    "loco": [("threshold_pctile", [97.0, 98.0, 99.0, 99.5, 99.9, 99.99, 99.999, 99.9999]),
             ("bin_width_sec", [0.5, 1.0, 2.0]), ("context_win_sec", [60.0, 120.0, 240.0])],
}
TIE_RULES = {
    "learned_ungated": "highest pooled F1; then fewer parameters; then fewer training steps; "
                       "then earlier in the draw",
    "learned_gated": "highest pooled F1 among admissible; then fewer parameters; then fewer "
                     "training steps; then the higher threshold; then earlier in the draw",
    "hand": "highest pooled F1 (among admissible, when gated); then earlier in grid order",
    "nan_f1": "a NaN pooled F1 counts as 0, in selection and in comparisons",
}
LONE_FIT_SEC = {"tube": 11.7, "chorus_norm": 202.8, "chorus_gain_norm": 204.0,
                "line_length": 204.0}   # Gate 1, this machine, untuned 900 steps, one process
GATE1_FACTS = [
    "tube at 7fc052d differs from the Mac per fold by -0.0034, -0.0212, -0.0053 and +0.0069 F1, "
    "and is deterministic on this machine",
    "the committed training code is identical between 239f176 and 7fc052d",
    "the Mac recorded neither its torch version nor its uncommitted changes, so CPU float "
    "differences cannot be separated from those changes",
    "step 3, training seed 0, this machine minus the Mac's seed 0 per fold: chorus_norm -0.0124, "
    "-0.0065, +0.0231, -0.0014; chorus_gain_norm -0.0553, -0.0571, -0.0421, +0.0101 (at seed 1 "
    "here, every fold within 0.03 of a Mac seed); line_length -0.0023, +0.0000, +0.0213, -0.0061",
    "record: docs/learned/tuned_vs_coact/gate1/README.md",
]


# ---- configurations -------------------------------------------------------------------------

def draw(model: str) -> list[dict]:
    """The declared draw: product in axis order, minus the untuned, 23 sampled, untuned last."""
    from bugarach.learn.checkpoint import canonical

    axes = LEARNED_AXES[model]
    names = [a for a, _ in axes]
    every = [dict(zip(names, vals)) for vals in itertools.product(*[v for _, v in axes])]
    untuned = UNTUNED[model]
    remaining = [c for c in every if canonical(c) != canonical(untuned)]
    assert len(remaining) == len(every) - 1, f"{model}: the untuned setting is not in its grid"
    return random.Random(DRAW_SEED).sample(remaining, N_CONFIGS - 1) + [dict(untuned)]


def learned_config(model: str, choice: dict, *, index: int, is_untuned: bool,
                   steps=None, n_train=N_TRAIN) -> dict:
    """A drawn choice as the files store it: the full as-built cfg, the training choices, the key."""
    from bugarach.learn.checkpoint import config_key
    from bugarach.learn.nets import ARCHITECTURES

    over = {k: v for k, v in choice.items() if k not in ("lr", "steps")}
    cfg = {**ARCHITECTURES[model].cfg, **over}
    training = dict(optimizer="Adam", lr=float(choice["lr"]),
                    steps=int(steps if steps is not None else choice["steps"]),
                    crop_frames=CROP, batch=BATCH, n_train=int(n_train))
    return dict(arch=model, cfg=cfg, overrides=over, training=training, draw_index=index,
                is_untuned=is_untuned, config_key=config_key(model, cfg, training))


def hand_config(det: str, grid_values: dict | None, *, index) -> dict:
    from bugarach.bench import OPERATING_POINTS
    from bugarach.learn.checkpoint import config_key

    shipped = dict(OPERATING_POINTS[det].params)
    params = {**shipped, **(grid_values or {})}
    from bugarach.learn.checkpoint import canonical
    return dict(detector=det, params=params, grid_index=index,
                is_shipped=canonical(params) == canonical(shipped),
                config_key=config_key(det, params))


def hand_axes(det: str, quick: bool) -> tuple[list, str, str]:
    """A coded detector's grid, where it came from, and how it is searched.

    Goal 1 (WSMIP065) declares every knob's grid once, in ``bench.FULL_GRIDS``, for this tool and
    its own search to import (``HANDOFF-coded-detectors.md`` §3 step 3). Those grids are a
    **coordinate search's**, per axis and never a product, so a detector that has one is searched
    per outer fold through ``search_all_settings.choose_settings`` (option A,
    ``docs/todo/2026-09-17-how-is-the-coded-side-searched-inside-nested-cross-validation.md``).
    A detector without one falls back to this tool's own grids, walked as a product.
    """
    from bugarach import bench

    full = getattr(bench, "FULL_GRIDS", None)
    if full is not None and det in full:
        return [(a, list(v)) for a, v in full[det].items()], "bench.FULL_GRIDS", "search"
    if det not in HAND_AXES:
        raise SystemExit(f"{det}: no grid. bench.FULL_GRIDS does not declare it and this tool has "
                         "none of its own; goal 1 supplies every coded detector's grid.")
    axes = HAND_AXES[det]
    if quick:
        axes = [(a, [v[0], v[-1]]) for a, v in axes]
    n = math.prod(len(v) for _, v in axes)
    if n > MAX_HAND_CONFIGS:
        raise SystemExit(f"{det}: {n} configurations as a full product. A grid that size is a "
                         "coordinate search's; declare it in bench.FULL_GRIDS instead.")
    return axes, "tune_learned_vs_coact.HAND_AXES (bench.FULL_GRIDS does not declare it)", "product"


class Plan:
    """What this invocation runs: the declaration, shrunk by ``--quick`` or subset flags.

    **Recordings are named.** On the home spec a recording is its seed (``"1000"``); on the bench it
    is its background and seed (``"quiet:1000"``, ``"busy:1000"``), because every seed is simulated at
    both. :meth:`recordings` lists a set of seeds' recordings with the backgrounds ALTERNATING, and
    that order is what makes training mixed (decision 2): ``fold_maker`` takes the last two as the
    threshold block (one quiet, one busy) and ``train`` fits on a contiguous run of the rest, which in
    an alternating list is half of each.
    """

    def __init__(self, *, quick: bool, models=MODELS, detectors=HAND, spec_path=SPEC_PATH,
                 device: str = "cpu", simulation: str = "bench"):
        from bugarach import bench
        from bugarach.bench import fold_split

        assert simulation in SIMULATIONS, simulation
        self.quick = quick
        self.device = device   # where learned fits train and score; part of the declaration
        self.simulation = simulation
        self.models = tuple(models)
        self.detectors = tuple(detectors)
        self.spec_path = spec_path if simulation == "home" else None
        if simulation == "home":
            self.spec = json.loads((REPO / spec_path).read_text())["generator"]
            hot = self.spec["hot_window"]
            self.regimes = ("home",)
            self.twin_keys = [f"{f:g}" for f in TWIN_FACTORS]
            self.gate_key = f"{GATE_TWIN:g}"
        else:
            self.spec = None
            hot = bench.BENCH_RECORDING["hot_window"]
            self.regimes = tuple(BENCH_REGIMES)
            self.twin_keys = list(BENCH_NULLS)
            self.gate_key = BENCH_GATE_NULL
        # What a worker needs to rebuild any recording; picklable, and nothing else.
        self.sim = dict(simulation=simulation, spec=self.spec)
        self.n_folds, self.seeds_per_fold = (3, 2) if quick else (N_FOLDS, SEEDS_PER_FOLD)
        self.split = fold_split(n_folds=self.n_folds, seeds_per_fold=self.seeds_per_fold)
        self.tune_seeds = (0,) if quick else TUNE_SEEDS
        self.refit_seeds = (0, 1) if quick else REFIT_SEEDS
        self.n_train = 1 if quick else N_TRAIN
        self.busy_sec = float(hot[1] - hot[0])
        self.configs = {}
        for m in self.models:
            d = draw(m)
            idx = [0, len(d) - 1] if quick else range(len(d))
            self.configs[m] = [learned_config(m, d[i], index=i, is_untuned=(i == len(d) - 1),
                                              steps=100 if quick else None, n_train=self.n_train)
                               for i in idx]
        # The planted spacing a context window must fit inside; the simulation's, not always the
        # bench's (120 s on the bench, 171 s on the home spec).
        self.min_sep_sec = float(min_sep_sec(self))
        self.hand, self.hand_axes, self.hand_grid_source, self.hand_mode = {}, {}, {}, {}
        self.hand_refused: dict = {}
        for det in self.detectors:
            axes, source, mode = hand_axes(det, quick)
            self.hand_axes[det], self.hand_grid_source[det], self.hand_mode[det] = axes, source, mode
            if mode == "search":
                # The candidates are not enumerable here: choose_settings walks them per fold.
                self.hand[det] = []
                continue
            names = [a for a, _ in axes]
            every = [hand_config(det, dict(zip(names, vals)), index=i) for i, vals in
                     enumerate(itertools.product(*[v for _, v in axes]))]
            # The same two validity rules the searched path applies, so a product-grid detector
            # cannot admit a combination the search would refuse — including a context window that
            # contaminates its own null.
            self.hand[det] = [c for c in every
                              if candidate_is_valid(det, c["params"], self.min_sep_sec)]
            self.hand_refused[det] = [c["config_key"] for c in every if c not in self.hand[det]]
        # Decision 4: the budget's reference is CoactDetect at OPERATING_POINTS as this code finds it,
        # which is goal 1's landed values once they land; the declaration writes the parameters out.
        shipped_in_grid = [c for c in self.hand.get("coact", []) if c["is_shipped"]]
        self.reference = (shipped_in_grid[0] if shipped_in_grid
                          else hand_config("coact", None, index=None))

    def folds(self):
        return range(self.n_folds)

    def fold_seeds(self, folds) -> list[int]:
        return sorted(s for s in self.split.seeds if self.split.fold_of(s) in set(folds))

    def recordings(self, seeds) -> list[str]:
        """The named recordings of these seeds, backgrounds alternating (see the class docstring)."""
        if self.simulation == "home":
            return [str(s) for s in sorted(seeds)]
        return [f"{r}:{s}" for s in sorted(seeds) for r in self.regimes]

    def fold_recordings(self, folds) -> list[str]:
        return self.recordings(self.fold_seeds(folds))

    def training_folds(self, h):
        return [f for f in self.folds() if f != h]


CONTEXT_KEYS = ("context_win_sec", "context_win")


def context_fits_the_null(params: dict, min_sep_sec: float) -> bool:
    """Is every context window narrow enough that the null it estimates is uncontaminated?

    A context window wider than the spacing between planted events estimates its threshold from a
    window that contains other planted events. The null sits too high, the detector calls less, and
    precision — so F1 — rises. **The setting wins by breaking the measurement**, which is the trap
    `tests/test_bench.py::test_the_bench_recording_keeps_the_null_clean` exists for and the one that
    made the first upstream benchmark unusable.

    Found by WSMIP065 on 2026-09-17, whose sliding search chose 240 s contexts for LoCo and
    CoactDetect, passed all four budgets including the crowded veto, and was refused by that test
    after the fact. **`bugarach.bench.context_fits_the_null` is the canonical rule** and is used
    whenever this tree has it; this is the same check, kept so the rule binds before it lands.
    The spacing is the SIMULATION's, not always the bench's: 120 s on the bench, 171 s on the home
    spec.
    """
    from bugarach import bench

    theirs = getattr(bench, "context_fits_the_null", None)
    if theirs is not None:
        return bool(theirs(params, min_sep_sec))
    return all(float(params[k]) <= float(min_sep_sec) for k in CONTEXT_KEYS if k in params)


def candidate_is_valid(det: str, params: dict, min_sep_sec: float) -> bool:
    """Both validity rules a candidate must pass: the project's own, and an uncontaminated null."""
    from bugarach import bench

    return bool(bench.settings_are_valid(det, params)) and context_fits_the_null(params, min_sep_sec)


def seed_of(rid) -> int:
    return int(str(rid).rsplit(":", 1)[-1])


def regime_of(rid) -> str:
    return str(rid).split(":", 1)[0] if ":" in str(rid) else "home"


# ---- files --------------------------------------------------------------------------------------

def write_json(path: Path, doc) -> None:
    """Atomically: a crash leaves the old file or none, never half of one."""
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + f".tmp{os.getpid()}")
    tmp.write_text(json.dumps(doc, indent=1, default=float) + "\n", encoding="utf-8")
    os.replace(tmp, path)


def read_json(path: Path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def recs_hash(seeds) -> str:
    return hashlib.sha1(",".join(map(str, sorted(seeds))).encode()).hexdigest()[:10]


def config_path(out, name, key):
    return Path(out) / "configs" / name / f"{key}.json"


def fit_stem(out, model, key, seed, recs):
    return Path(out) / "fits" / model / key / f"seed{seed}__recs-{recs_hash(recs)}"


def score_path(out, model, key, seed, recs, fold):
    return Path(out) / "scores" / model / key / f"seed{seed}__recs-{recs_hash(recs)}__fold{fold}.json"


def hand_score_path(out, det, key):
    return Path(out) / "scores" / det / f"{key}.json"


def searched_score_path(out, det, h, w):
    """A searched detector's held-out scores: one file per outer fold and selection."""
    return Path(out) / "scores" / det / f"outer{h}__{w}.json"


def selection_path(out, which, h, name):
    return Path(out) / "selections" / which / f"outer{h}" / f"{name}.json"


def chosen_path(out, which, h, name, seed=None):
    base = Path(out) / "chosen" / which / f"outer{h}" / name
    return base / f"seed{seed}.json" if seed is not None else base / "detector_settings.csv"


def error_path(out, job_key):
    return Path(out) / "errors" / f"{job_key.replace('/', '__')}.json"


# ---- scoring rows ------------------------------------------------------------------------------

def score_row(sc) -> dict:
    """What ``bench.pool_scores`` reads off a ``score.Score``, as plain JSON."""
    return dict(n_planted=int(sc.n_planted), n_detected=int(sc.n_detected), n_hit=int(sc.n_hit),
                n_fa=int(sc.n_fa), hot_fa=int(sc.hot_fa),
                distractor_hits=int(sc.distractor_hits),
                by_frac={f"{f:g}": [int(n), int(h)] for f, (n, h) in sc.by_frac.items()},
                tol_sec=None if sc.tol_sec is None else float(sc.tol_sec))


def pooled(rows, name="tuning"):
    """Pool stored rows through ``bench.pool_scores``, the one pooling rule."""
    from bugarach.bench import pool_scores
    return pool_scores([SimpleNamespace(**{**r, "by_frac": {float(f): (n, h) for f, (n, h)
                                                            in r["by_frac"].items()}})
                        for r in rows], detector=name, regime="tuning")


def f1_or_zero(p) -> float:
    return float(p.f1) if np.isfinite(p.f1) else 0.0


def by_regime(items) -> dict:
    """``(recording name, row)`` pairs grouped by background: ``{"quiet": [rows], "busy": [rows]}``."""
    groups: dict = {}
    for rid, row in items:
        groups.setdefault(regime_of(rid), []).append(row)
    return groups


def objective(items, name="tuning") -> float:
    """The score every selection maximises: each background's pooled F1, averaged over backgrounds.

    Goal 1's search uses the same rule (decision 1). On the home spec there is one background, so it
    is the pooled F1 it always was.
    """
    groups = by_regime(items)
    return float(np.mean([f1_or_zero(pooled(rows, name)) for rows in groups.values()]))


def probe_rates(items, plan) -> dict:
    """False alarms per hour inside the probe (the busy stretch with nothing planted), per background.

    Per background because the bench's own probe budget must hold at both ends of the rate axis."""
    return {reg: sum(r["hot_fa"] for r in rows) / (len(rows) * plan.busy_sec / 3600.0)
            for reg, rows in by_regime(items).items()}


def within(budget, probes: dict, quiet: float) -> bool:
    return (all(v <= budget["probe_per_hour"][reg] for reg, v in probes.items())
            and quiet <= budget["quiet_per_hour"])


def quiet_rate(twins, index=None) -> float:
    dets = sum(t["n_detected"][index] if index is not None else t["n_detected"] for t in twins)
    return dets / (sum(t["duration_sec"] for t in twins) / 3600.0)


# ---- the worker -----------------------------------------------------------------------------------

_RECORDINGS: dict = {}


def _planted(sim, rid):
    """A named recording with planted events: ``"1000"`` on the home spec, ``"quiet:1000"`` on the bench."""
    k = ("planted", sim["simulation"], str(rid))
    if k not in _RECORDINGS:
        if sim["simulation"] == "home":
            _RECORDINGS[k] = _make_recording(sim["spec"], seed_of(rid))
        else:
            from bugarach.bench import make_recording
            _RECORDINGS[k] = make_recording(BENCH_REGIMES[regime_of(rid)], seed_of(rid))
    return _RECORDINGS[k]


def _empty(sim, key, seed):
    """The recording with nothing planted that belongs to ``seed``, at seed + NULL_SEED_OFFSET.

    Home spec: the null twin at ``key`` times its background rate. Bench: ``bench.make_null_recording``
    at the named background's rate (``null_quiet`` is exactly the bench's own empty recording).
    """
    k = ("empty", sim["simulation"], key, int(seed))
    if k not in _RECORDINGS:
        if sim["simulation"] == "home":
            _RECORDINGS[k] = _make_recording(_null_twin(sim["spec"], float(key)),
                                             int(seed) + NULL_SEED_OFFSET)
        else:
            from bugarach.bench import REGIMES, make_null_recording
            _RECORDINGS[k] = make_null_recording(int(seed) + NULL_SEED_OFFSET,
                                                 **REGIMES[BENCH_NULLS[key]])
    return _RECORDINGS[k]


def probabilities(trained, slice_):
    """Per-frame probabilities, exactly as ``Trained.predict`` computes them, on the model's device."""
    from bugarach.learn import train as T
    from bugarach.learn.encode import encode
    enc = encode(slice_, dt=trained.dt)
    return T.probabilities(trained.model, enc.raster), enc


def decode_at(trained, p, enc, threshold):
    """Detections at ``threshold``, exactly as ``Trained.predict`` decodes them."""
    from bugarach.learn.encode import decode
    return decode(p, threshold=float(threshold),
                  merge_gap_frames=trained.merge_gap_frames).to_seconds(enc)


def torch_version() -> str:
    import torch
    return torch.__version__


def run_job(job, out, sim, spec_path):
    """Run one job in a worker process. Never raises: an exception becomes an error file."""
    t0 = time.perf_counter()
    try:
        if job["kind"] == "hand":
            _run_hand(job, sim)
        elif job["kind"] == "search":
            _run_search(job, Path(out), sim)
        else:
            _run_fit(job, Path(out), sim, spec_path)
        return dict(key=job["key"], status="ok", seconds=time.perf_counter() - t0)
    except Exception:  # noqa: BLE001 -- recorded, listed in results.json, never retried silently
        write_json(error_path(Path(out), job["key"]),
                   dict(job={k: v for k, v in job.items() if k != "outputs"},
                        traceback=traceback.format_exc(), torch=torch_version(),
                        at=time.strftime("%Y-%m-%dT%H:%M:%S%z")))
        return dict(key=job["key"], status="error", seconds=time.perf_counter() - t0)


def _score_settings(det, params, sim, rids, seeds, twin_keys, busy_sec):
    """One candidate on one set of recordings: the objective, the probe rates, the empty rate.

    Everything the budget needs, measured where the recordings are. Goal 1's search never sees any
    of it: it calls back for a number and a yes or no.
    """
    from bugarach.bench import run_detector
    from bugarach.score import score_stream

    items, twins = [], {}
    for rid in rids:
        sl, gt = _planted(sim, rid)
        items.append((rid, score_row(score_stream(gt, run_detector(det, sl, **params)))))
    for key in twin_keys:
        twins[key] = {}
        for sd in seeds:
            tsl, tgt = _empty(sim, key, sd)
            twins[key][str(sd)] = dict(
                twin_seed=sd + NULL_SEED_OFFSET, duration_sec=float(tgt.params["duration_sec"]),
                n_detected=int(score_stream(tgt, run_detector(det, tsl, **params)).n_detected))
    plan_like = SimpleNamespace(busy_sec=busy_sec)
    return dict(objective=objective(items, det), probe_per_hour=probe_rates(items, plan_like),
                items=items, twins=twins)


def _run_search(job, out, sim):
    """Goal 1's coordinate search, run inside one outer fold, once per selection.

    The recordings it is given are that fold's TRAINING recordings; the held-out fold is scored
    only after the search has finished, with what it chose.
    """
    sys.path.insert(0, str(REPO / "tools"))
    from search_all_settings import MOVE_EPS, choose_settings

    from bugarach.learn.checkpoint import canonical, config_key

    assert MOVE_EPS == SEARCH_MIN_GAIN, (
        f"search_all_settings.MOVE_EPS is {MOVE_EPS}, this tool declares {SEARCH_MIN_GAIN}; "
        "the declaration must say the epsilon the search actually used")

    det, h = job["det"], job["outer_fold"]
    budget = read_json(Path(out) / "meta.json")["budgets"][str(h)]
    train, seeds = job["train_recordings"], job["train_seeds"]
    gate, busy_sec = job["gate_key"], job["busy_sec"]
    cache: dict = {}

    def measured(params):
        key = json.dumps(canonical(params), sort_keys=True)
        if key not in cache:
            cache[key] = _score_settings(det, params, sim, train, seeds, [gate], busy_sec)
        return cache[key]

    def score(params):
        return measured(params)["objective"]

    def admissible(params):
        m = measured(params)
        return within(budget, m["probe_per_hour"],
                      quiet_rate(list(m["twins"][gate].values())))

    t0 = time.perf_counter()
    min_sep = float(job["min_sep_sec"])
    for w in SELECTIONS:
        got = choose_settings(det, score=score,
                              admissible=None if w == "ungated" else admissible,
                              # A context wider than the planted spacing estimates its threshold
                              # from a window holding other planted events (WSMIP065, 2026-09-17).
                              is_valid=lambda d, p: candidate_is_valid(d, p, min_sep),
                              # An F1-sized objective, so MOVE_EPS is the right epsilon; passed
                              # rather than defaulted because a caller scoring something else
                              # silently never moves (WSMIP065, 2026-09-17).
                              min_gain=MOVE_EPS, max_rounds=job["max_rounds"])
        params = dict(got.params)
        key = config_key(det, params)
        write_json(config_path(Path(out), det, key),
                   dict(detector=det, params=params, config_key=key, grid_index=None,
                        is_shipped=None, chosen_by="search_all_settings.choose_settings",
                        outer_fold=h, selection=w))
        # The held-out fold, once, with what the search chose — and every empty recording, since
        # the ones outside the gate are reported.
        held = _score_settings(det, params, sim, job["test_recordings"], job["test_seeds"],
                               job["twins"], busy_sec)
        write_json(searched_score_path(Path(out), det, h, w),
                   dict(config=f"configs/{det}/{key}.json", config_key=key, outer_fold=h,
                        selection=w, rows=dict(held["items"]), twins=held["twins"],
                        torch=torch_version(), host=socket.gethostname()))
        train_m = measured(params)
        write_json(selection_path(Path(out), w, h, det), dict(
            detector=det, outer_fold=h, selection=w, config_key=key,
            config=f"configs/{det}/{key}.json", budget=f"meta.json budgets[{h}]",
            searched_by="search_all_settings.choose_settings (goal 1's grids, per fold)",
            grids=got.grids, min_gain=MOVE_EPS, max_rounds=job["max_rounds"],
            inner_f1=got.score, moves=got.moves, edge_flags=got.edges,
            n_scored=got.n_scored, n_refused=got.n_refused,
            inner_probe_per_hour=train_m["probe_per_hour"],
            inner_quiet_per_hour=quiet_rate(list(train_m["twins"][gate].values())),
            pooled=dict(recordings=list(train), recording_seeds=list(seeds),
                        twin_seeds=[s + NULL_SEED_OFFSET for s in seeds]),
            seconds=time.perf_counter() - t0))


def _run_hand(job, sim):
    from bugarach.bench import run_detector
    from bugarach.score import score_stream

    det, params = job["det"], job["params"]
    t0 = time.perf_counter()
    rows, twins = {}, {key: {} for key in job["twins"]}
    for rid in job["recordings"]:
        sl, gt = _planted(sim, rid)
        rows[rid] = score_row(score_stream(gt, run_detector(det, sl, **params)))
    for sd in job["seeds"]:
        for key in job["twins"]:
            tsl, tgt = _empty(sim, key, sd)
            twins[key][str(sd)] = dict(
                twin_seed=sd + NULL_SEED_OFFSET, duration_sec=float(tgt.params["duration_sec"]),
                n_detected=int(score_stream(tgt, run_detector(det, tsl, **params)).n_detected))
    write_json(Path(job["outputs"][0]),
               dict(config=f"configs/{det}/{job['config_key']}.json", rows=rows, twins=twins,
                    seconds=time.perf_counter() - t0, torch=torch_version(),
                    host=socket.gethostname()))


def _run_fit(job, out, sim, spec_path):
    import warnings

    from bugarach.learn import checkpoint
    from bugarach.learn.train import THRESHOLD_GRID, VAL_SEED_BLOCK, fold_maker, train
    from bugarach.score import score_stream

    conf = read_json(config_path(out, job["model"], job["config_key"]))
    seed, recs = int(job["seed"]), job["train_recordings"]   # backgrounds alternating: see Plan
    mk, n_fit, n_val = fold_maker(lambda r: _planted(sim, r), recs)
    n_train = int(conf["training"]["n_train"])
    assert n_train <= n_fit, f"n_train {n_train} exceeds the {n_fit} fitting recordings"
    fit_pool, val_pool = recs[:-n_val], recs[-n_val:]
    fitted = sorted({fit_pool[(seed * 1000 + i) % n_fit] for i in range(n_train)})
    picked = sorted({val_pool[(seed * 1000 + i) % n_val] for i in range(4)})   # pick_threshold n_val=4

    t0 = time.perf_counter()
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        tr = train(job["model"], mk, n_train=n_train, steps=int(conf["training"]["steps"]),
                   crop=int(conf["training"]["crop_frames"]),
                   batch=int(conf["training"]["batch"]), lr=float(conf["training"]["lr"]),
                   seed=seed, device=job.get("device"), **conf["overrides"])
    train_sec = time.perf_counter() - t0
    assert VAL_SEED_BLOCK   # the threshold block is fold_maker's validation recordings, above
    grid = [float(t) for t in THRESHOLD_GRID]
    own = int(np.argmin(np.abs(np.asarray(grid) - tr.threshold)))
    assert abs(grid[own] - tr.threshold) < 1e-12, "the picked threshold is not on the grid"

    stem = fit_stem(out, job["model"], job["config_key"], seed, recs)
    t1 = time.perf_counter()
    for fold, rids in job["score_folds"].items():
        assert not {seed_of(r) for r in rids} & {seed_of(r) for r in recs}, \
            "a scored recording's seed was fitted on"
        rows = {}
        for rid in rids:
            sl, gt = _planted(sim, rid)
            p, enc = probabilities(tr, sl)
            rows[rid] = [score_row(score_stream(gt, decode_at(tr, p, enc, t))) for t in grid]
        twins = {}
        for key in job["twins"]:
            twins[key] = {}
            for sd in sorted({seed_of(r) for r in rids}):
                tsl, tgt = _empty(sim, key, sd)
                p, enc = probabilities(tr, tsl)
                twins[key][str(sd)] = dict(
                    twin_seed=sd + NULL_SEED_OFFSET, duration_sec=float(tgt.params["duration_sec"]),
                    n_detected=[int(score_stream(tgt, decode_at(tr, p, enc, t)).n_detected)
                                for t in grid])
        write_json(score_path(out, job["model"], job["config_key"], seed, recs, int(fold)),
                   dict(fit=str(stem.relative_to(out)) + ".json", fold=int(fold),
                        own_index=own, thresholds="meta.json declaration.threshold_grid",
                        rows=rows, twins=twins, torch=torch_version()))
    score_sec = time.perf_counter() - t1

    ck = stem.with_suffix(".json")
    tmp = ck.with_name(ck.name + f".tmp{os.getpid()}")
    where = spec_path if sim["simulation"] == "home" else "bugarach.bench.make_recording"
    checkpoint.save(tr, tmp, trained_on=(f"{where}: fitted on recordings {fitted} (fitting "
                                         f"pool {fit_pool}); threshold picked on {picked}"),
                    train_seed=seed, steps=int(conf["training"]["steps"]), n_fit=n_fit,
                    n_threshold_val=n_val, note=f"tune_learned_vs_coact {job['role']} fit")
    saved = read_json(tmp)
    from bugarach.learn.checkpoint import canonical
    if saved["config_key"] != job["config_key"] or canonical(saved["cfg"]) != canonical(conf["cfg"]):
        tmp.unlink()
        raise RuntimeError(f"checkpoint config_key {saved['config_key']} / cfg does not match "
                           f"configs/{job['model']}/{job['config_key']}.json; not written")
    os.replace(tmp, ck)
    write_json(stem.with_suffix(".run.json"),
               dict(fit=str(ck.relative_to(out)), role=job["role"], train_folds=job["train_folds"],
                    recordings=recs, fitted_recordings=fitted, threshold_recordings=picked,
                    own_index=own, train_sec=train_sec, score_sec=score_sec,
                    warnings=[str(w.message) for w in caught], torch=torch_version(),
                    host=socket.gethostname()))


# ---- jobs ---------------------------------------------------------------------------------------

def fit_job(plan, out, model, ci, seed, train_folds, score_folds, role, priority):
    conf = plan.configs[model][ci]
    recs = plan.fold_recordings(train_folds)
    stem = fit_stem(out, model, conf["config_key"], seed, recs)
    return dict(kind="fit", role=role, key=f"fit/{model}/{conf['config_key']}/{stem.name}",
                model=model, ci=ci, config_key=conf["config_key"], seed=seed,
                # None on the CPU, so a CPU fit calls `train` exactly as it did before --device
                device=None if plan.device == "cpu" else plan.device,
                train_folds=sorted(train_folds), train_recordings=recs,
                score_folds={int(f): plan.fold_recordings([f]) for f in sorted(score_folds)},
                twins=list(plan.twin_keys) if role == "outer" else [plan.gate_key],
                outputs=[str(score_path(out, model, conf["config_key"], seed, recs, f))
                         for f in sorted(score_folds)]
                + [str(stem.with_suffix(".json")), str(stem.with_suffix(".run.json"))],
                priority=priority)


def search_job(plan, out, det, h, priority):
    """One coded detector, one outer fold: goal 1's coordinate search under both selections.

    Both selections in one job because they share a score cache: the ungated search's work is the
    gated one's too, and a second process could not reuse it.
    """
    return dict(kind="search", key=f"search/{det}/outer{h}", det=det, outer_fold=h,
                train_recordings=plan.fold_recordings(plan.training_folds(h)),
                train_seeds=sorted(plan.split.train(h)),
                test_recordings=plan.fold_recordings([h]), test_seeds=sorted(plan.split.test(h)),
                gate_key=plan.gate_key, twins=list(plan.twin_keys), busy_sec=plan.busy_sec,
                min_sep_sec=min_sep_sec(plan), max_rounds=2 if plan.quick else None,
                outputs=[str(selection_path(out, w, h, det)) for w in SELECTIONS]
                + [str(searched_score_path(out, det, h, w)) for w in SELECTIONS],
                priority=priority)


def hand_job(plan, out, conf, priority):
    det = conf["detector"]
    return dict(kind="hand", key=f"hand/{det}/{conf['config_key']}", det=det,
                params=conf["params"], config_key=conf["config_key"],
                recordings=plan.recordings(plan.split.seeds), seeds=list(plan.split.seeds),
                twins=list(plan.twin_keys),
                outputs=[str(hand_score_path(out, det, conf["config_key"]))], priority=priority)


def job_done(job) -> bool:
    return all(Path(p).exists() for p in job["outputs"])


def plan_jobs(plan, out) -> list[dict]:
    jobs = []
    for d in plan.detectors:
        if plan.hand_mode[d] == "search":
            for h in plan.folds():
                jobs.append(search_job(plan, out, d, h, (1, 0, 0, h)))
            continue
        for conf in plan.hand[d]:
            jobs.append(hand_job(plan, out, conf, (1, 0, 0, conf["grid_index"])))
    pairs = list(itertools.combinations(plan.folds(), plan.n_folds - 2))
    for rank, m in enumerate(plan.models):
        for ci in range(len(plan.configs[m])):
            for seed in plan.tune_seeds:
                for pair in pairs:
                    jobs.append(fit_job(plan, out, m, ci, seed, pair,
                                        [f for f in plan.folds() if f not in pair], "inner",
                                        (2, rank, 0, seed, ci)))
        untuned = len(plan.configs[m]) - 1
        for h in plan.folds():
            for seed in plan.refit_seeds:
                jobs.append(fit_job(plan, out, m, untuned, seed, plan.training_folds(h), [h],
                                    "outer", (2, rank, 1, seed, h)))
    return jobs


def stage_of(job) -> str:
    if job["kind"] == "hand":
        return f"hand:{job['det']}"
    if job["kind"] == "search":
        return f"search:{job['det']}"
    return f"{job['role']}:{job['model']}"


# ---- budgets and selections ----------------------------------------------------------------------

def budgets(plan, out) -> dict:
    """Per outer fold, from the shipped-CoactDetect reference on training recordings only."""
    ref = read_json(hand_score_path(out, "coact", plan.reference["config_key"]))
    res = {}
    for h in plan.folds():
        seeds = list(plan.split.train(h))
        items = [(rid, ref["rows"][rid]) for rid in plan.recordings(seeds)]
        tw = [ref["twins"][plan.gate_key][str(s)] for s in seeds]
        probe = probe_rates(items, plan)
        probe_h = {reg: len(rows) * plan.busy_sec / 3600.0 for reg, rows in by_regime(items).items()}
        quiet_h = sum(t["duration_sec"] for t in tw) / 3600.0
        res[str(h)] = dict(
            reference_config_key=plan.reference["config_key"], recording_seeds=seeds,
            recordings=[rid for rid, _ in items], twin_seeds=[t["twin_seed"] for t in tw],
            gate_empty_recording=plan.gate_key,
            reference_probe_per_hour=probe, reference_quiet_per_hour=quiet_rate(tw),
            # Floor: never below one false alarm in the measured time, so a reference that fired
            # zero times does not refuse everything.
            probe_per_hour={reg: max(BUDGET_MARGIN * v, 1.0 / probe_h[reg]) for reg, v in probe.items()},
            quiet_per_hour=max(BUDGET_MARGIN * quiet_rate(tw), 1.0 / quiet_h))
    return res


def edge_flags(values: dict, axes) -> dict:
    """Per axis of three values or more: is the chosen value at either end? Two-value axes exempt."""
    return {a: float(values[a]) in (float(v[0]), float(v[-1])) for a, v in axes if len(v) >= 3}


def _inner(plan, out, model, ci, h):
    """(own_index, rows, twins, n_params) per inner (fit, fold) for outer fold h, and what is missing."""
    from bugarach.learn.checkpoint import peek

    key = plan.configs[model][ci]["config_key"]
    got, missing = [], []
    for j in plan.training_folds(h):
        recs = plan.fold_recordings([f for f in plan.training_folds(h) if f != j])
        for seed in plan.tune_seeds:
            sp = score_path(out, model, key, seed, recs, j)
            ck = fit_stem(out, model, key, seed, recs).with_suffix(".json")
            if sp.exists() and ck.exists():
                got.append((read_json(sp), peek(ck)["n_params"], recs))
            else:
                missing.append(str(sp.relative_to(out)))
    return got, missing


def select_learned(plan, out, model, h, budget) -> dict:
    from bugarach.learn.train import THRESHOLD_GRID

    grid = [float(t) for t in THRESHOLD_GRID]
    test = set(plan.split.test(h))
    best = {w: None for w in SELECTIONS}
    missing, n_adm = [], 0
    audit = dict(fitted=set(), scored=set(), twin=set())
    for ci, conf in enumerate(plan.configs[model]):
        files, miss = _inner(plan, out, model, ci, h)
        if miss:
            missing.append(dict(config_key=conf["config_key"], missing=miss))
            continue
        for sc, _, recs in files:
            audit["fitted"].update(recs)
            audit["scored"].update(sc["rows"])
            audit["twin"].update(int(t["twin_seed"]) for t in sc["twins"][plan.gate_key].values())
        n_params, steps = files[0][1], conf["training"]["steps"]
        own_items = [(rid, r[sc["own_index"]]) for sc, _, _ in files for rid, r in sc["rows"].items()]
        f1 = objective(own_items, model)
        rank = (f1, -n_params, -steps, -ci)
        if best["ungated"] is None or rank > best["ungated"][0]:
            best["ungated"] = (rank, dict(ci=ci, inner_f1=f1))
        for ti, thr in enumerate(grid):
            items = [(rid, r[ti]) for sc, _, _ in files for rid, r in sc["rows"].items()]
            tw = [t for sc, _, _ in files for t in sc["twins"][plan.gate_key].values()]
            probe, quiet = probe_rates(items, plan), quiet_rate(tw, ti)
            if not within(budget, probe, quiet):
                continue
            n_adm += 1
            f1t = objective(items, model)
            rank = (f1t, -n_params, -steps, thr, -ci)
            if best["gated"] is None or rank > best["gated"][0]:
                best["gated"] = (rank, dict(ci=ci, inner_f1=f1t, threshold=thr, threshold_index=ti,
                                            inner_probe_per_hour=probe, inner_quiet_per_hour=quiet))
    audit_seeds = ({seed_of(r) for r in audit["fitted"]} | {seed_of(r) for r in audit["scored"]}
                   | {s - NULL_SEED_OFFSET for s in audit["twin"]})
    leak = sorted(audit_seeds & test)
    assert not leak, f"{model}, outer fold {h}: held-out recordings reached the selection: {leak}"
    common = dict(model=model, outer_fold=h, budget=f"meta.json budgets[{h}]",
                  pooled=dict(training_seeds=list(plan.tune_seeds),
                              recordings=sorted(audit["scored"]),
                              recording_seeds=sorted({seed_of(r) for r in audit["scored"]}),
                              fitted_on=sorted(audit["fitted"]), twin_seeds=sorted(audit["twin"])),
                  n_configurations=len(plan.configs[model]), missing_configurations=missing)
    out_ = {}
    for w in SELECTIONS:
        if best[w] is None:
            out_[w] = dict(common, selection=w, config_key=None,
                           result="no admissible configuration" if w == "gated" else "no complete "
                           "configuration", n_admissible=n_adm if w == "gated" else None)
            continue
        c = best[w][1]
        conf = plan.configs[model][c["ci"]]
        choice = {**conf["overrides"], "lr": conf["training"]["lr"],
                  "steps": conf["training"]["steps"]}
        doc = dict(common, selection=w, config_key=conf["config_key"],
                   config=f"configs/{model}/{conf['config_key']}.json",
                   draw_index=conf["draw_index"], inner_f1=c["inner_f1"],
                   edge_flags=edge_flags(choice, LEARNED_AXES[model]))
        if w == "gated":
            doc.update(threshold=c["threshold"], threshold_index=c["threshold_index"],
                       threshold_at_grid_edge=c["threshold_index"] in (0, len(grid) - 1),
                       inner_probe_per_hour=c["inner_probe_per_hour"],
                       inner_quiet_per_hour=c["inner_quiet_per_hour"], n_admissible=n_adm)
        out_[w] = doc
    return out_


def select_hand(plan, out, det, h, budget) -> dict:
    seeds = list(plan.split.train(h))
    assert not set(seeds) & set(plan.split.test(h))
    best = {w: None for w in SELECTIONS}
    n_adm, missing = 0, []
    for conf in plan.hand[det]:
        path = hand_score_path(out, det, conf["config_key"])
        if not path.exists():
            missing.append(conf["config_key"])
            continue
        doc = read_json(path)
        items = [(rid, doc["rows"][rid]) for rid in plan.recordings(seeds)]
        tw = [doc["twins"][plan.gate_key][str(s)] for s in seeds]
        f1, probe, quiet = objective(items, det), probe_rates(items, plan), quiet_rate(tw)
        rank = (f1, -conf["grid_index"])
        if best["ungated"] is None or rank > best["ungated"][0]:
            best["ungated"] = (rank, dict(conf=conf, inner_f1=f1))
        if within(budget, probe, quiet):
            n_adm += 1
            if best["gated"] is None or rank > best["gated"][0]:
                best["gated"] = (rank, dict(conf=conf, inner_f1=f1, inner_probe_per_hour=probe,
                                            inner_quiet_per_hour=quiet))
    common = dict(detector=det, outer_fold=h, budget=f"meta.json budgets[{h}]",
                  pooled=dict(recording_seeds=seeds, recordings=plan.recordings(seeds),
                              twin_seeds=[s + NULL_SEED_OFFSET for s in seeds]),
                  n_configurations=len(plan.hand[det]), missing_configurations=missing)
    out_ = {}
    for w in SELECTIONS:
        if best[w] is None:
            out_[w] = dict(common, selection=w, config_key=None,
                           result="no admissible configuration",
                           n_admissible=n_adm if w == "gated" else None)
            continue
        c = best[w][1]
        doc = dict(common, selection=w, config_key=c["conf"]["config_key"],
                   config=f"configs/{det}/{c['conf']['config_key']}.json",
                   grid_index=c["conf"]["grid_index"], inner_f1=c["inner_f1"],
                   edge_flags=edge_flags(c["conf"]["params"], plan.hand_axes[det]))
        if w == "gated":
            doc.update(inner_probe_per_hour=c["inner_probe_per_hour"],
                       inner_quiet_per_hour=c["inner_quiet_per_hour"], n_admissible=n_adm)
        out_[w] = doc
    return out_


# ---- meta ------------------------------------------------------------------------------------------

def git_state() -> dict:
    def run(*a):
        return subprocess.run(["git", "-C", str(REPO), *a], capture_output=True,
                              text=True).stdout.strip()
    return {"commit": run("rev-parse", "HEAD"), "dirty": bool(run("status", "--porcelain"))}


def gpu() -> dict | None:
    """The GPU a CUDA run trains on, and its driver; ``None`` when there is none."""
    import torch

    if not torch.cuda.is_available():
        return None
    driver = subprocess.run(["nvidia-smi", "--query-gpu=driver_version", "--format=csv,noheader"],
                            capture_output=True, text=True).stdout.strip() or None
    return dict(name=torch.cuda.get_device_name(0), driver=driver, cuda=torch.version.cuda,
                memory_gb=round(torch.cuda.get_device_properties(0).total_memory / 2 ** 30, 1))


def machine() -> dict:
    rel = platform.release()
    cores = set()
    try:
        phys = None
        for line in Path("/proc/cpuinfo").read_text().splitlines():
            if line.startswith("physical id"):
                phys = line.split(":")[1].strip()
            elif line.startswith("core id"):
                cores.add((phys, line.split(":")[1].strip()))
    except OSError:
        pass
    ram_gb = os_name = None
    try:
        kb = int(next(l for l in Path("/proc/meminfo").read_text().splitlines()
                      if l.startswith("MemTotal")).split()[1])
        ram_gb = round(kb / 1024 ** 2, 1)
        os_name = next(l.split("=", 1)[1].strip('"') for l in
                       Path("/etc/os-release").read_text().splitlines()
                       if l.startswith("PRETTY_NAME="))
    except (OSError, StopIteration):
        pass
    return {"hostname": socket.gethostname(), "os": os_name or platform.platform(),
            "kernel": rel, "wsl": "microsoft" in rel.lower(), "cpus_logical": os.cpu_count(),
            "cpus_physical": len(cores) or None, "ram_gb": ram_gb,
            "python": platform.python_version(), "torch": torch_version(),
            "numpy": np.__version__, "gpu": gpu()}


def estimate(plan, jobs: int, gpu_jobs: int = 1) -> dict:
    on_gpu = plan.device != "cpu"
    lone = GPU_LONE_FIT_SEC if on_gpu else LONE_FIT_SEC
    parallel = gpu_jobs if on_gpu else jobs
    total = 0.0
    n_pairs = len(list(itertools.combinations(plan.folds(), plan.n_folds - 2)))
    for m in plan.models:
        t = lone.get(m, 200.0)
        ratios = [c["training"]["steps"] / 900.0 for c in plan.configs[m]]
        inner = sum(ratios) * n_pairs * len(plan.tune_seeds)
        outer = 3 * plan.n_folds * len(plan.refit_seeds) * float(np.mean(ratios))
        total += (inner + outer) * t
    return dict(training_device_hours_floor=total / 3600.0, jobs=jobs, gpu_jobs=gpu_jobs if on_gpu else None,
                training_wall_hours_floor=total / 3600.0 / parallel, lone_fit_sec=lone,
                basis=("lone untuned fit times on this machine's " + ("GPU" if on_gpu else "CPU")
                       + ", scaled by each drawn configuration's steps; ignores the larger "
                       "configurations' cost per step, contention between concurrent fits, "
                       "scoring and the hand-written grids. A floor, and not a gate (decision 8)."))


def simulation_declaration(plan) -> dict:
    """What the recordings are, written out so the declaration does not move if the bench does."""
    if plan.simulation == "home":
        return dict(simulation="home", spec=plan.spec_path, spec_generator=plan.spec,
                    empty_recordings={f"{f:g}": f"_null_twin(spec, {f:g}) at seed + {NULL_SEED_OFFSET}"
                                      for f in TWIN_FACTORS},
                    gate_empty_recording=plan.gate_key, backgrounds=["home"])
    from bugarach import bench
    return dict(
        simulation="bench",
        decisions="docs/goals/learned-model-family.md, 'How the next comparison runs on the bench' "
                  "(Tony, 2026-09-17)",
        bench_recording=bench.BENCH_RECORDING,
        backgrounds={r: dict(regime=BENCH_REGIMES[r], **bench.REGIMES[BENCH_REGIMES[r]])
                     for r in plan.regimes},
        recording_names="'<background>:<seed>', every seed at every background",
        score="each background's pooled F1, averaged over backgrounds (goal 1's rule)",
        training_mix="the training folds' recordings alternate backgrounds; fold_maker's threshold "
                     "block is the last two (one of each), and train fits on a contiguous run of "
                     "the rest (half of each)",
        probe="the bench's hot window, counted per background; admissible only if within budget "
              "at every background",
        empty_recordings={k: dict(builder="bench.make_null_recording", seed=f"seed + {NULL_SEED_OFFSET}",
                                  **bench.REGIMES[BENCH_NULLS[k]]) for k in BENCH_NULLS},
        null_recording=bench.NULL_RECORDING,
        gate_empty_recording=plan.gate_key,
        reported_only_empty_recordings=[k for k in plan.twin_keys if k != plan.gate_key],
        measured_record=getattr(bench, "MEASURED_RECORD", None),
        measured_outside_interval=getattr(bench, "MEASURED_OUTSIDE_INTERVAL", None))


def declaration(plan) -> dict:
    from bugarach.learn.nets import ARCHITECTURES
    from bugarach.learn.train import THRESHOLD_GRID

    return dict(
        **simulation_declaration(plan), quick=plan.quick,
        folds=plan.n_folds, seeds_per_fold=plan.seeds_per_fold,
        recording_seeds=list(plan.split.seeds), tune_seeds=list(plan.tune_seeds),
        refit_seeds=list(plan.refit_seeds), models=list(plan.models),
        learned_axes={m: LEARNED_AXES[m] for m in plan.models},
        untuned={m: UNTUNED[m] for m in plan.models}, draw_seed=DRAW_SEED,
        configurations={m: [c["config_key"] for c in plan.configs[m]] for m in plan.models},
        detectors=list(plan.detectors), hand_axes=dict(plan.hand_axes),
        hand_grid_source=dict(plan.hand_grid_source), hand_mode=dict(plan.hand_mode),
        hand_search=dict(
            how="search_all_settings.choose_settings per detector and outer fold, once per "
                "selection, on that fold's training recordings only (option A, decided with "
                "WSMIP065 on 2026-09-17)",
            min_gain=SEARCH_MIN_GAIN, extend_ranges=False, pairs=False,
            is_valid="bench.settings_are_valid AND context_fits_the_null(params, min_sep_sec)",
            min_sep_sec=plan.min_sep_sec,
            context_rule=("a context window wider than the planted spacing estimates its threshold "
                          "from a window holding other planted events, so the setting wins by "
                          "breaking the measurement (WSMIP065, 2026-09-17; "
                          "test_the_bench_recording_keeps_the_null_clean)"),
            hand_refused_by_validity=dict(plan.hand_refused),
            note="the grids are goal 1's, per axis and never a product; an axis whose chosen value "
                 "sits at an end is reported, not refused"),
        hand_configurations={d: [c["config_key"] for c in plan.hand[d]] for d in plan.detectors},
        reference=dict(config_key=plan.reference["config_key"], params=plan.reference["params"],
                       note="CoactDetect at bench.OPERATING_POINTS as this code found it (goal 2 "
                            "decision 4: goal 1's landed every-knob values once they land); the "
                            "parameters above are the ones the budget was measured with"),
        budget_margin=BUDGET_MARGIN, busy_window_sec=plan.busy_sec,
        threshold_grid=[float(t) for t in THRESHOLD_GRID],
        tie_rules=TIE_RULES, registered=sorted(ARCHITECTURES),
        registered_but_not_run=sorted(set(ARCHITECTURES) - set(plan.models)),
        device=dict(learned=plan.device, hand="cpu",
                    note="GPU and CPU arithmetic differ, so every learned fit in one run comes from "
                         "one device; on CUDA, train.deterministic_cuda makes a rerun fit identical"))


def min_sep_sec(plan):
    """The least spacing between planted events, which a context window can straddle."""
    if plan.simulation == "home":
        return plan.spec.get("min_sep_sec")
    from bugarach.bench import BENCH_RECORDING
    return BENCH_RECORDING.get("min_sep_sec")


def write_declaration(plan, out, jobs, gpu_jobs=1) -> dict:
    """meta.json and configs/, before any job. A declaration on disk never changes."""
    from bugarach.learn.checkpoint import canonical

    configs = {}
    for m in plan.models:
        for c in plan.configs[m]:
            configs[config_path(out, m, c["config_key"])] = c
    for d in plan.detectors:
        for c in plan.hand[d]:
            configs[config_path(out, d, c["config_key"])] = c
    configs[config_path(out, "coact", plan.reference["config_key"])] = plan.reference
    path = out / "meta.json"
    decl = declaration(plan)
    now = dict(at=time.strftime("%Y-%m-%dT%H:%M:%S%z"), git=git_state(), machine=machine(),
               jobs=jobs, argv=sys.argv)
    if path.exists():
        meta = read_json(path)
        if canonical(json.loads(json.dumps(meta["declaration"], default=float))) != \
                canonical(json.loads(json.dumps(decl, default=float))):
            raise SystemExit(f"{path}: the declaration on disk differs from this code's. A "
                             "declared run does not change after it starts; use a new --out.")
        for p, c in configs.items():
            if not p.exists() or canonical(read_json(p)) != canonical(c):
                raise SystemExit(f"{p}: missing or different from this code's declaration")
        meta.setdefault("resumed", []).append(now)
    else:
        for p, c in configs.items():
            write_json(p, c)
        meta = dict(declaration=decl, started=now, estimate=estimate(plan, jobs, gpu_jobs),
                    gate1_reproduction=GATE1_FACTS, sliding_branch="sliding-loco-coact 005ae98",
                    checkpoint_format_branch=dict(
                        branch="learn-checkpoint-records-what-it-built", commit="36dc5ab",
                        pr=602, note="merged before #602 reached main, at the Mac unsupervised "
                                     "session's request; a checkpoint written here is that "
                                     "commit's format"),
                    storage_rule="Tony, 2026-09-16, via the Mac unsupervised session: tuned "
                                 "parameters stored persistently, rationally and separably",
                    event_spacing=dict(
                        min_sep_sec=min_sep_sec(plan),
                        note="planted events are at least this far apart; a chosen context longer "
                             "than this spans more than one spacing and is flagged in the readout"))
    write_json(path, meta)
    return meta


def write_progress(out, state, git):
    now = time.time()
    rate = sum(1 for t, kind in state["finished"] if kind == "fit" and now - t <= 3600)
    remaining = sum(1 for j in list(state["pending"].values()) + list(state["running"].values())
                    if j["kind"] == "fit")
    write_json(Path(out) / "progress.json", dict(
        at=time.strftime("%Y-%m-%dT%H:%M:%S%z"), commit=git["commit"], torch=torch_version(),
        stages=state["stages"], errors=sorted(state["errors"]), fits_last_hour=rate,
        running=len(state["running"]), queued=len(state["pending"]),
        remaining_fits_known=remaining,
        projected_finish=(time.strftime("%Y-%m-%dT%H:%M:%S%z",
                                        time.localtime(now + 3600.0 * remaining / rate))
                          if rate else None),
        note="remaining_fits_known excludes outer refits not yet queued: a model's are queued "
             "when its selections are made"))


# ---- the driver --------------------------------------------------------------------------------------

def run(plan, out: Path, jobs: int, retry_errors: bool = False, gpu_jobs: int = 1) -> dict:
    """With a GPU, learned fits run in their OWN pool of ``gpu_jobs`` worker processes, and the
    ``jobs`` CPU workers run only hand-written configurations.

    One pool used to serve both, capped by counting running fits. Any of the 12 CPU workers could
    then pick up a GPU fit, and each worker that had kept its CUDA context and cached memory: on the
    2026-09-17 shakedown GPU memory climbed from 2.8 to 9.1 GB of 16 in its first hour. A GPU pool
    of its own caps the contexts at ``gpu_jobs``. One GPU is the limit on fits: on WSMIP064 more
    than one ``chorus_norm`` process at a time lost about 30% of fits per hour on the training loop.
    """
    import contextlib
    import multiprocessing as mp

    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)
    if retry_errors and (out / "errors").exists():
        for p in (out / "errors").glob("*.json"):
            p.unlink()
    assert gpu_jobs >= 1
    meta = write_declaration(plan, out, jobs, gpu_jobs)
    git = git_state()
    ran = []
    state = dict(pending={}, running={}, finished=[], errors=set(), stages={}, seen=set())

    def bump(stage, field):
        state["stages"].setdefault(stage, dict(total=0, done=0, errors=0))[field] += 1

    def enqueue(job):
        if job["key"] in state["seen"]:
            return
        state["seen"].add(job["key"])
        bump(stage_of(job), "total")
        if job_done(job):
            bump(stage_of(job), "done")
        elif error_path(out, job["key"]).exists():
            bump(stage_of(job), "errors")
            state["errors"].add(job["key"])
        else:
            state["pending"][job["key"]] = job

    selected = set()

    def on_idle():
        if "budgets" not in meta:
            return
        open_ = list(state["pending"].values()) + list(state["running"].values())
        # A searched detector writes its own selections, in the worker that ran its search.
        product = [d for d in plan.detectors if plan.hand_mode[d] == "product"]
        if product and "hand" not in selected and not any(j["kind"] == "hand" for j in open_):
            selected.add("hand")
            for d in product:
                for h in plan.folds():
                    for w, doc in select_hand(plan, out, d, h, meta["budgets"][str(h)]).items():
                        write_json(selection_path(out, w, h, d), doc)
        for rank, m in enumerate(plan.models):
            if m in selected or any(j.get("model") == m and j.get("role") == "inner"
                                    for j in open_):
                continue
            selected.add(m)
            for h in plan.folds():
                sels = select_learned(plan, out, m, h, meta["budgets"][str(h)])
                for w, doc in sels.items():
                    write_json(selection_path(out, w, h, m), doc)
                    if doc["config_key"] is None:
                        continue
                    ci = next(i for i, c in enumerate(plan.configs[m])
                              if c["config_key"] == doc["config_key"])
                    for seed in plan.refit_seeds:
                        enqueue(fit_job(plan, out, m, ci, seed, plan.training_folds(h), [h],
                                        "outer", (2, rank, 1, seed, h)))

    with contextlib.ExitStack() as stack:
        ctx = mp.get_context("spawn")
        pools = {"cpu": stack.enter_context(ProcessPoolExecutor(max_workers=jobs, mp_context=ctx))}
        caps = {"cpu": jobs}
        if plan.device != "cpu":
            pools["gpu"] = stack.enter_context(ProcessPoolExecutor(max_workers=gpu_jobs, mp_context=ctx))
            caps["gpu"] = gpu_jobs
        futures = {}

        def pool_of(job):
            return "gpu" if "gpu" in pools and job["kind"] == "fit" else "cpu"

        def startable(k):
            p = pool_of(state["pending"][k])
            return sum(1 for j in futures.values() if pool_of(j) == p) < caps[p]

        def drain():
            while state["pending"] or futures:
                while state["pending"]:
                    ready = [k for k in state["pending"] if startable(k)]
                    if not ready:
                        break
                    key = min(ready, key=lambda k: state["pending"][k]["priority"])
                    job = state["pending"].pop(key)
                    state["running"][key] = job
                    futures[pools[pool_of(job)].submit(run_job, job, str(out), plan.sim,
                                                       plan.spec_path)] = job
                done, _ = wait(list(futures), return_when=FIRST_COMPLETED)
                for fu in done:
                    job = futures.pop(fu)
                    state["running"].pop(job["key"], None)
                    res = fu.result()
                    ran.append(dict(res, stage=stage_of(job)))
                    state["finished"].append((time.time(), job["kind"]))
                    bump(stage_of(job), "done" if res["status"] == "ok" else "errors")
                    if res["status"] != "ok":
                        state["errors"].add(job["key"])
                    write_progress(out, state, git)
                on_idle()

        # 1. The reference alone, then the budgets into meta.json before any learned fit.
        enqueue(hand_job(plan, out, plan.reference, (0,)))
        drain()
        if not hand_score_path(out, "coact", plan.reference["config_key"]).exists():
            raise SystemExit("the shipped-CoactDetect reference failed (see errors/): no budget, "
                             "so nothing else runs")
        if "budgets" not in meta:
            meta["budgets"] = budgets(plan, out)
            write_json(out / "meta.json", meta)
        # 2. Everything else in priority order; each model's selections queue its outer refits.
        for job in plan_jobs(plan, out):
            enqueue(job)
        write_progress(out, state, git)
        on_idle()
        drain()

    write_chosen(plan, out)
    results = summarize(plan, out)
    write_json(out / "results.json", results)
    write_json(out / "ran.json", ran)
    write_progress(out, state, git)
    return dict(ran=ran, results=results)


# ---- chosen artifacts and the summary ------------------------------------------------------------------

def write_chosen(plan, out) -> None:
    """The deployable record of each choice: checkpoints at the selection's operating point, and
    settings files. Weights are the outer refits'; a gated checkpoint carries the gated threshold."""
    from bugarach.bench import STREAM
    from bugarach.emit import write_detector_settings
    from bugarach.learn import checkpoint
    from bugarach.learn.train import THRESHOLD_GRID

    for h in plan.folds():
        for w in SELECTIONS:
            for d in plan.detectors:
                sp = selection_path(out, w, h, d)
                if not sp.exists() or read_json(sp)["config_key"] is None:
                    continue
                sel = read_json(sp)
                params = read_json(config_path(out, d, sel["config_key"]))["params"]
                p = chosen_path(out, w, h, d)
                p.parent.mkdir(parents=True, exist_ok=True)
                write_detector_settings({(d, STREAM): {
                    **params, "fitted_config_key": sel["config_key"], "fitted_selection": w,
                    "fitted_outer_fold": h,
                    "fitted_on": f"simulated recordings {sel['pooled']['recordings']}"}}, p)
            for m in plan.models:
                sp = selection_path(out, w, h, m)
                if not sp.exists() or read_json(sp)["config_key"] is None:
                    continue
                sel = read_json(sp)
                recs = plan.fold_recordings(plan.training_folds(h))
                for seed in plan.refit_seeds:
                    ck = fit_stem(out, m, sel["config_key"], seed, recs).with_suffix(".json")
                    dst = chosen_path(out, w, h, m, seed)
                    if not ck.exists() or dst.exists():
                        continue
                    tr = checkpoint.load(ck)
                    if w == "gated":
                        tr = dataclasses.replace(tr, threshold=float(THRESHOLD_GRID[sel["threshold_index"]]))
                    prov = checkpoint.peek(ck)["provenance"]
                    dst.parent.mkdir(parents=True, exist_ok=True)
                    tmp = dst.with_name(dst.name + ".tmp")
                    checkpoint.save(tr, tmp, trained_on=prov.get("trained_on"), train_seed=seed,
                                    steps=prov.get("steps"), n_fit=prov.get("n_fit"),
                                    n_threshold_val=prov.get("n_threshold_val"),
                                    note=(f"tune_learned_vs_coact: chosen by the {w} selection for "
                                          f"outer fold {h}; weights from {ck.relative_to(out)}"
                                          + (gated_note(plan, out, h, sel) if w == "gated" else "")))
                    os.replace(tmp, dst)


def gated_note(plan, out, h, sel) -> str:
    """Enough to trace a gated threshold without the selection file beside the checkpoint."""
    b = read_json(Path(out) / "meta.json")["budgets"][str(h)]
    probe = ", ".join(f"{reg} <= {v:.4g}/h" for reg, v in b["probe_per_hour"].items())
    return (f"; operating point is the gated threshold {sel['threshold']:.6g}, not the fit's own. "
            f"It is the best inner score among (configuration, threshold) candidates within outer "
            f"fold {h}'s budget: probe false alarms {probe}, and on the empty recording "
            f"({b['gate_empty_recording']}) <= {b['quiet_per_hour']:.4g}/h, which is "
            f"{BUDGET_MARGIN:g} x CoactDetect {b['reference_config_key']}'s own rates on training "
            f"recordings {b['recordings']}; inner scores pooled training seeds {list(plan.tune_seeds)}")


def _heldout(plan, out, model, key, h, seed, index=None):
    recs = plan.fold_recordings(plan.training_folds(h))
    sp = score_path(out, model, key, seed, recs, h)
    run_p = fit_stem(out, model, key, seed, recs).with_suffix(".run.json")
    if not (sp.exists() and run_p.exists()):
        return None
    sc, run_ = read_json(sp), read_json(run_p)
    ti = sc["own_index"] if index is None else index
    items = [(rid, r[ti]) for rid, r in sc["rows"].items()]
    p = pooled([r for _, r in items], model)
    from bugarach.learn.train import THRESHOLD_GRID
    thr = float(THRESHOLD_GRID[ti])
    return dict(seed=seed, f1=objective(items, model), f1_was_nan=not np.isfinite(p.f1),
                f1_by_background={reg: f1_or_zero(pooled(rows, model))
                                  for reg, rows in by_regime(items).items()},
                recall=p.recall, precision=p.precision, threshold_index=ti,
                probe_per_hour=probe_rates(items, plan),
                quiet_per_hour={f: quiet_rate(list(sc["twins"][f].values()), ti)
                                for f in sc["twins"]},
                train_sec=run_["train_sec"],
                failed_training_signature=bool(np.isfinite(p.f1) and abs(p.f1 - 0.125) < 0.01
                                               and thr <= 1e-4 + 1e-12))


def _paired(a, b):
    d = [x - y for x, y in zip(a, b)]
    if len(d) < 2:
        return dict(per_fold=d, mean=float(np.mean(d)) if d else None, t=None, df=None)
    sd = float(np.std(d, ddof=1))
    return dict(per_fold=d, mean=float(np.mean(d)), sd=sd,
                t=float(np.mean(d) / (sd / math.sqrt(len(d)))) if sd > 0 else None, df=len(d) - 1)


def summarize(plan, out) -> dict:
    """results.json: held-out numbers per selection, named by config_key, never by parameters."""
    out = Path(out)
    meta = read_json(out / "meta.json")
    runs = [read_json(p) for p in (out / "fits").rglob("*.run.json")] if (out / "fits").exists() else []
    res = dict(budgets="meta.json budgets", n_fits=len(runs),
               cpu_hours_training=sum(r["train_sec"] for r in runs) / 3600.0,
               cpu_hours_scoring_learned=sum(r["score_sec"] for r in runs) / 3600.0,
               errors=sorted(p.stem for p in (out / "errors").glob("*.json"))
               if (out / "errors").exists() else [], hand={}, learned={}, comparisons={})
    for d in plan.detectors:
        res["hand"][d] = []
        for h in plan.folds():
            entry = dict(outer_fold=h)
            for w in SELECTIONS:
                sp = selection_path(out, w, h, d)
                sel = read_json(sp) if sp.exists() else None
                if sel is None or sel["config_key"] is None:
                    entry[w] = dict(config_key=None, f1=0.0, note="no admissible configuration"
                                    if sel else "not selected")
                    continue
                doc = read_json(searched_score_path(out, d, h, w) if plan.hand_mode[d] == "search"
                                else hand_score_path(out, d, sel["config_key"]))
                seeds = plan.split.test(h)
                items = [(rid, doc["rows"][rid]) for rid in plan.recordings(seeds)]
                p = pooled([r for _, r in items], d)
                entry[w] = dict(config_key=sel["config_key"], f1=objective(items, d),
                                f1_was_nan=not np.isfinite(p.f1),
                                # Window-shaped settings are the ones the bench's event spacing can
                                # flatter, and both machines' searches drift towards long windows
                                # (WSMIP065, 2026-09-17: its 240 s context winner lost 0.022 mean F1
                                # on crowded recordings). Carried here so a readout sees an edge
                                # without opening the selection file.
                                edge_flags=sel.get("edge_flags"),
                                chosen_params=read_json(config_path(out, d, sel["config_key"]))["params"],
                                f1_by_background={reg: f1_or_zero(pooled(rows, d))
                                                  for reg, rows in by_regime(items).items()},
                                recall=p.recall, precision=p.precision,
                                probe_per_hour=probe_rates(items, plan),
                                quiet_per_hour={k: quiet_rate([doc["twins"][k][str(x)]
                                                               for x in seeds])
                                                for k in doc["twins"]},
                                over_budget=None)
                if w == "gated":
                    b = meta["budgets"][str(h)]
                    entry[w]["over_budget"] = not within(
                        b, entry[w]["probe_per_hour"], entry[w]["quiet_per_hour"][plan.gate_key])
            res["hand"][d].append(entry)
    for m in plan.models:
        res["learned"][m] = []
        untuned_key = plan.configs[m][-1]["config_key"]
        for h in plan.folds():
            entry = dict(outer_fold=h)
            for w in ("untuned",) + SELECTIONS:
                if w == "untuned":
                    key, idx, sel = untuned_key, None, None
                else:
                    sp = selection_path(out, w, h, m)
                    sel = read_json(sp) if sp.exists() else None
                    if sel is None or sel["config_key"] is None:
                        entry[w] = dict(config_key=None, f1_mean=0.0,
                                        note="no admissible configuration" if sel else "not selected")
                        continue
                    key = sel["config_key"]
                    idx = sel.get("threshold_index") if w == "gated" else None
                per = [x for x in (_heldout(plan, out, m, key, h, s, idx) for s in plan.refit_seeds)
                       if x is not None]
                entry[w] = dict(config_key=key, per_seed=per, n_seeds=len(per),
                                f1_mean=float(np.mean([x["f1"] for x in per])) if per else None)
                if w == "gated" and per:
                    b = meta["budgets"][str(h)]
                    entry[w]["seeds_over_budget"] = sum(
                        1 for x in per
                        if not within(b, x["probe_per_hour"], x["quiet_per_hour"][plan.gate_key]))
            res["learned"][m].append(entry)

    def column(entries, w, field):
        return [(e[w].get(field) if isinstance(e.get(w), dict) else None) or 0.0 for e in entries]

    for w in SELECTIONS:
        comp = {}
        for m in plan.models:
            lf = column(res["learned"][m], w, "f1_mean")
            for d in plan.detectors:
                comp[f"{m} - {d}"] = _paired(lf, column(res["hand"][d], w, "f1"))
            comp[f"{m} tuned - untuned"] = _paired(lf, column(res["learned"][m], "untuned", "f1_mean"))
        res["comparisons"][w] = comp
    return res


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--out", type=Path, required=True,
                   help="output folder, outside the repository while the run is going")
    p.add_argument("--jobs", type=int, default=22)
    p.add_argument("--quick", action="store_true")
    p.add_argument("--models", default=",".join(MODELS))
    p.add_argument("--detectors", default=",".join(HAND))
    p.add_argument("--retry-errors", action="store_true",
                   help="delete error files first, so those jobs run again")
    p.add_argument("--device", default="cpu",
                   help="where learned fits train and score: cpu (default) or cuda. Declared: a "
                        "run cannot be resumed on the other device")
    p.add_argument("--gpu-jobs", type=int, default=1,
                   help="with --device cuda, how many learned fits run at once, in a pool of their "
                        "own (default 1)")
    p.add_argument("--allow-binned-reference", action="store_true",
                   help="run even though the budget's CoactDetect reference is the binned shipped "
                        "point rather than goal 1's landed sliding values")
    p.add_argument("--simulation", choices=SIMULATIONS, default="bench",
                   help="bench (default): the bench's fitted field at its two backgrounds, goal 2's "
                        "next comparison. home: the retired home spec, docs/learned/generator_spec.json")
    a = p.parse_args(argv)
    models = tuple(x for x in a.models.split(",") if x)
    dets = tuple(x for x in a.detectors.split(",") if x)
    from bugarach.bench import DETECTORS
    assert set(models) <= set(MODELS), f"unknown models {sorted(set(models) - set(MODELS))}"
    assert set(dets) <= set(DETECTORS), f"unknown detectors {sorted(set(dets) - set(DETECTORS))}"
    assert "coact" in dets, "the budget's reference is CoactDetect"
    if a.device != "cpu":
        import torch
        if not torch.cuda.is_available():
            raise SystemExit(f"--device {a.device}: torch {torch.__version__} sees no CUDA device. "
                             "See docs/windows_workstation_setup.md, section 4.")
    plan = Plan(quick=a.quick, models=models, detectors=dets, device=a.device,
                simulation=a.simulation)
    # Decision 4: the budget is anchored to goal 1's landed every-knob CoactDetect. Its values
    # reach this run through bench.OPERATING_POINTS, and until goal 1 lands them the shipped point
    # is the binned one it is about to replace. A real run against that anchor would be measured
    # against a reference nobody intends to ship.
    if not a.quick and plan.reference["params"].get("window_mode") != "sliding" \
            and not a.allow_binned_reference:
        raise SystemExit(
            "the budget's reference is CoactDetect at bench.OPERATING_POINTS, and this tree's is "
            f"{plan.reference['params'].get('window_mode') or 'binned'}, not sliding. Goal 1 lands "
            "the sliding every-knob values (HANDOFF-coded-detectors.md §3 step 4); wait for them, "
            "or pass --allow-binned-reference and say in the readout which reference was used.")
    t0 = time.time()
    r = run(plan, a.out.expanduser(), a.jobs, retry_errors=a.retry_errors, gpu_jobs=a.gpu_jobs)
    n_ok = sum(1 for x in r["ran"] if x["status"] == "ok")
    print(f"ran {len(r['ran'])} jobs ({n_ok} ok, {len(r['ran']) - n_ok} errors) in "
          f"{(time.time() - t0) / 60:.1f} min; results in {a.out / 'results.json'}")
    return 1 if r["results"]["errors"] else 0


if __name__ == "__main__":
    sys.exit(main())
