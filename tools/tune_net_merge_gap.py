#!/usr/bin/env python3
"""The nets' merge gap, tuned like any other setting, from the fair comparison's saved fits.

    python tools/tune_net_merge_gap.py score   --run R --work W     # every fit, every gap and threshold
    python tools/tune_net_merge_gap.py crowded --run R --work W     # the crowded recordings, chosen configs
    python tools/tune_net_merge_gap.py select  --run R --work W     # the selections; writes --out

``R`` is the run folder (``%USERPROFILE%/runs/fair-comparison-2026-09-18``: ``fits/``, ``scores/``,
``selections/``, ``configs/``, ``meta.json``, ``results.json``), ``W`` a scratch folder outside the
repository. Run with branch ``tune-bench-comparison``'s ``src`` and ``tools`` first on
``PYTHONPATH``: the nets and the tuning tool whose rules this reuses live there.

**Why.** In goal 2's fair comparison (2026-09-18) the coded detectors' searches tuned their merge
gap, and chose the top of goal 1's grid in every fold, while the nets decoded at a fixed 20 frames
(2 s), ``pick_threshold``'s default. The report's ablation re-scored the nets at wider gaps keeping
every other choice, which bounds what the gap could do but does not measure it. Tony, 2026-09-19:
tune the nets' merge gap like any other setting. No retraining: every fit is saved, and a gap is
applied when the network's output is decoded, after the network has run.

**The selection**, per net, outer fold and selection, on the training folds' inner fits only,
exactly as ``tune_learned_vs_coact.select_learned`` chooses and with its functions:

- *Ungated* (F1 alone). The gap is a configuration setting; each fit's threshold is still picked
  by its own rule, ``pick_threshold`` on its two threshold recordings, now **at that gap**. So a
  gap candidate is scored at the threshold each fit would have picked had it been decoded that way.
- *Gated* (under the shared budget). Threshold and gap are chosen together over the threshold grid,
  admissible only if the pooled inner rates are within the fold's budget, as the run chose the
  threshold alone.
- **Goal 1's move rule.** The search starts from the run's own choice at 2 s and moves only for a
  gain of at least ``min_gain`` (0.002 inner F1, the coded search's) that also passes goal 1's
  crowded-recording check: no more than ``bench.MAX_CROWDED_DROP`` (0.02) lower mean F1 on the
  crowded recordings (``bench.make_tail_recording``, seeds 1 to 12, both backgrounds) than the
  choice it would replace, measured on the same inner fits. Goal 1 applies that check inside its
  search; the coded side of the fair comparison did not, and the report says what it would have
  refused.
- Two variants: **the run's configuration kept** (only the gap, and the threshold under the
  budget, move), and **configuration re-chosen too**, over every configuration's inner fits. When
  the second picks a configuration with no outer refits, it is reported and not scored: no
  retraining.

The held-out number is the run's own: the five outer refits of the chosen configuration, scored on
the held-out fold at the chosen gap, each at the threshold its own rule picks there (ungated) or at
the chosen threshold (gated). Every step first reproduces the run at 2 s, and the output records
how closely: ``pick_threshold`` at 20 frames must return each fit's recorded threshold, the rows
at 2 s must equal the run's score files, and the selection and held-out F1 at 2 s must equal the
run's.
"""

from __future__ import annotations

import argparse
import json
import math
import os
import sys
import time
import warnings
from multiprocessing import Pool
from pathlib import Path
from types import SimpleNamespace

import numpy as np

REPO = Path(__file__).resolve().parent.parent
DEFAULT_OUT = (REPO / "docs" / "learned" / "tuned_vs_coact" / "fair_comparison_2026_09_18"
               / "net_merge_gap.json")

NETS = ("chorus_norm", "chorus_gain_norm", "line_length", "tube")
SELECTIONS = ("ungated", "gated")
#: Seconds. Every value of CoactDetect's own grid (0 to 8 s), plus 15 s and binned SCE's top of 30 s,
#: so the grid spans the whole range any coded detector was allowed. It is coarser than the union of
#: their grids, which also holds 0.5, 4, 10 and 20 s. The run's gap is 2 s.
GAPS_SEC = (0.0, 1.0, 2.0, 3.0, 5.0, 8.0, 15.0, 30.0)
AS_RUN_SEC = 2.0
FIELDS = ("n_planted", "n_detected", "n_hit", "n_fa", "hot_fa", "distractor_hits")
TWIN_KEYS = ("null_quiet", "null_busy")
TAIL_SEEDS = tuple(range(1, 13))     # goal 1's selection-stage crowded recordings (search_all_settings)
TAIL = {"tail_quiet": "baseline_quiet", "tail_busy": "baseline_busy"}
#: Nadeau and Bengio's corrected resampled t, as the report computes it: the variance's 1/J becomes
#: 1/J + n2/n1. Derived from the run's own fold count rather than hardcoded for four folds.
def nb_factor(folds: int) -> float:
    return math.sqrt((1.0 / folds) / (1.0 / folds + 1.0 / (folds - 1)))
NOISE_F1 = 0.010                     # median F1 change from a recordings-only change (WSMIP065)


def _tool():
    try:
        import tune_learned_vs_coact as T
    except ImportError as e:
        raise SystemExit("tune_learned_vs_coact is not importable: put branch tune-bench-comparison's "
                         f"src and tools first on PYTHONPATH ({e})")
    return T


def read_json(p):
    return json.loads(Path(p).read_text(encoding="utf-8"))


def _provenance() -> dict:
    """What the re-decoding ran on. The run records the same of itself, and nobody can repeat this
    without it: the nets and the tuning tool live on another branch, in another worktree."""
    import socket
    import subprocess
    import torch

    def head(path):
        try:
            return subprocess.run(["git", "-C", str(path), "rev-parse", "--short", "HEAD"],
                                  capture_output=True, text=True, timeout=30).stdout.strip() or None
        except Exception:                                        # noqa: BLE001 - recorded as unknown
            return None
    T = _tool()
    return dict(host=socket.gethostname(), torch=torch.__version__,
                cuda=torch.cuda.is_available(),
                this_tree=head(REPO), tuning_tool=Path(T.__file__).name,
                tuning_tree=head(Path(T.__file__).resolve().parent.parent))


def gap_index(sec) -> int:
    return GAPS_SEC.index(float(sec))


# ---- which fits there are ------------------------------------------------------------------------

def fit_records(run: Path) -> list[dict]:
    """Every saved fit of the four nets, from its ``.run.json``."""
    decl = read_json(run / "meta.json")["declaration"]
    folds = list(range(decl["folds"]))
    out = []
    for m in NETS:
        for p in sorted((run / "fits" / m).rglob("*.run.json")):
            r = read_json(p)
            scored = [f for f in folds if f not in r["train_folds"]]
            out.append(dict(model=m, config_key=p.parent.name,
                            seed=int(p.name[len("seed"):].split("__")[0]), role=r["role"],
                            train_folds=list(r["train_folds"]), recordings=list(r["recordings"]),
                            own_index=int(r["own_index"]), fit=str(run / r["fit"].replace("\\", "/")),
                            stem=p.name[:-len(".run.json")], scored_folds=scored))
    return out


def fold_rids(decl, f) -> list[str]:
    spf = decl["seeds_per_fold"]
    return [f"{b}:{s}" for s in decl["recording_seeds"][f * spf:(f + 1) * spf] for b in ("quiet", "busy")]


def work_path(work: Path, kind: str, rec: dict) -> Path:
    return work / kind / rec["model"] / rec["config_key"] / f"{rec['stem']}.npz"


# ---- scoring: one fit at every gap and threshold -----------------------------------------------

def _load(fit_path):
    import torch

    from bugarach.learn import checkpoint
    tr = checkpoint.load(fit_path)
    if torch.cuda.is_available():
        tr.model.to("cuda")
    return tr


def _grid():
    from bugarach.learn.train import THRESHOLD_GRID
    return [float(t) for t in THRESHOLD_GRID]


def _rows(tr, p, enc, gt, grid, gaps_f):
    from bugarach.learn.encode import decode
    from bugarach.score import score_stream
    a = np.zeros((len(gaps_f), len(grid), len(FIELDS)), np.int32)
    tol = None
    for gi, gf in enumerate(gaps_f):
        for ti, thr in enumerate(grid):
            sc = score_stream(gt, decode(p, threshold=thr, merge_gap_frames=gf).to_seconds(enc))
            a[gi, ti] = [getattr(sc, k) for k in FIELDS]
            tol = sc.tol_sec
    return a, tol


def score_job(args):
    """One fit: its threshold at every gap, and its scored folds' rows and empty recordings."""
    rec, run, work, decl = args
    out = work_path(Path(work), "bench", rec)
    if out.exists():
        return rec["stem"], "cached"
    T = _tool()
    from bugarach.learn.train import fold_maker, pick_threshold
    run = Path(run)
    sim = dict(simulation="bench")
    grid = _grid()
    tr = _load(rec["fit"])
    gaps_f = [int(round(g / tr.dt)) for g in GAPS_SEC]
    stream = (tr.training or {}).get("stream")
    mk, _, _ = fold_maker(lambda r: T._planted(sim, r), rec["recordings"])
    own, caught_all = [], []
    for gf in gaps_f:
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            thr, _ = pick_threshold(tr.model, mk, dt=tr.dt, seed=rec["seed"], stream=stream,
                                    merge_gap_frames=gf)
        caught_all += [f"{gf} frames: {w.message}" for w in caught]
        own.append(int(np.argmin(np.abs(np.asarray(grid) - thr))))
        assert abs(grid[own[-1]] - thr) < 1e-12
    arrays = dict(own=np.asarray(own, np.int16))
    repro = dict(own_index=own[gap_index(AS_RUN_SEC)] == rec["own_index"], rows=True, twins=True)
    tol = None
    for f in rec["scored_folds"]:
        rids = fold_rids(decl, f)
        rows = np.zeros((len(rids), len(gaps_f), len(grid), len(FIELDS)), np.int32)
        for i, rid in enumerate(rids):
            sl, gt = T._planted(sim, rid)
            p, enc = T.probabilities(tr, sl)
            rows[i], tol = _rows(tr, p, enc, gt, grid, gaps_f)
        seeds = sorted({T.seed_of(r) for r in rids})
        twins = np.zeros((len(TWIN_KEYS), len(seeds), len(gaps_f), len(grid)), np.int32)
        dur = np.zeros((len(TWIN_KEYS), len(seeds)))
        for k, key in enumerate(TWIN_KEYS):
            for j, sd in enumerate(seeds):
                tsl, tgt = T._empty(sim, key, sd)
                p, enc = T.probabilities(tr, tsl)
                dur[k, j] = float(tgt.params["duration_sec"])
                twins[k, j] = _rows(tr, p, enc, tgt, grid, gaps_f)[0][..., FIELDS.index("n_detected")]
        # Reproduce the run's own score file at 2 s: the same rows and the same empty-recording counts.
        sp = T.score_path(run, rec["model"], rec["config_key"], rec["seed"], rec["recordings"], f)
        if sp.exists():
            sf = read_json(sp)
            g2 = gap_index(AS_RUN_SEC)
            for i, rid in enumerate(rids):
                theirs = np.asarray([[r[k] for k in FIELDS] for r in sf["rows"][rid]], np.int32)
                repro["rows"] &= bool(np.array_equal(theirs, rows[i, g2]))
            for k, key in enumerate(TWIN_KEYS):
                for j, sd in enumerate(seeds):
                    t = sf["twins"].get(key, {}).get(str(sd))
                    if t is not None:
                        repro["twins"] &= bool(np.array_equal(np.asarray(t["n_detected"]),
                                                              twins[k, j, g2]))
        else:
            repro["rows"] = repro["twins"] = None
        arrays.update({f"rows{f}": rows, f"twins{f}": twins, f"dur{f}": dur,
                       f"rids{f}": np.asarray(rids), f"twin_seeds{f}": np.asarray(seeds)})
    out.parent.mkdir(parents=True, exist_ok=True)
    tmp = out.with_name(out.stem + f".tmp{os.getpid()}.npz")
    np.savez_compressed(tmp, **arrays,
                        meta=np.asarray(json.dumps(dict(tol_sec=tol, repro=repro,
                                                        warnings=caught_all))))
    os.replace(tmp, out)
    return rec["stem"], repro


def crowded_job(args):
    """One fit on goal 1's crowded recordings, at every gap and threshold, or only at ``pairs``.

    ``pairs`` is a list of ``[gap index, threshold index or None]``, None meaning the threshold this
    fit's own rule picks at that gap. It exists for fits whose full grid is impractical: the four
    inner fits of one ``chorus_norm`` configuration ran for more than three hours each on the full
    grid without finishing (2026-09-19), where the rest took well under a minute. A partial file
    holds -1 in every cell not scored, and ``Scored.crowded`` refuses to read one.
    """
    rec, work = args[:2]
    pairs = args[2] if len(args) > 2 else None
    out = work_path(Path(work), "crowded", rec)
    prev = None
    if out.exists():
        with np.load(out) as z:    # closed before os.replace below: Windows refuses to replace an open file
            if not bool(json.loads(str(z["meta"])).get("partial")):
                return rec["stem"], "cached"
            prev = z["rows"].copy()
    if pairs is None and prev is not None:
        raise RuntimeError(f"{rec['stem']}: a partial file exists; say which pairs to add")
    from bugarach import bench
    from bugarach.learn.encode import decode
    from bugarach.score import score_stream
    grid = _grid()
    tr = _load(rec["fit"])
    gaps_f = [int(round(g / tr.dt)) for g in GAPS_SEC]
    T = _tool()
    rids = [f"{name}:{s}" for name in TAIL for s in TAIL_SEEDS]
    if pairs is None:
        rows = np.zeros((len(rids), len(gaps_f), len(grid), len(FIELDS)), np.int32)
    else:
        own = np.load(work_path(Path(work), "bench", rec))["own"]
        cells = sorted({(int(gi), int(own[gi]) if ti is None else int(ti)) for gi, ti in pairs})
        rows = (prev.copy() if prev is not None
                else np.full((len(rids), len(gaps_f), len(grid), len(FIELDS)), -1, np.int32))
        cells = [c for c in cells if rows[0, c[0], c[1], 0] < 0]
        if not cells:
            return rec["stem"], "cached"
    tol = None
    for i, rid in enumerate(rids):
        name, s = rid.split(":")
        sl, gt = bench.make_tail_recording(TAIL[name], int(s))
        p, enc = T.probabilities(tr, sl)
        if pairs is None:
            rows[i], tol = _rows(tr, p, enc, gt, grid, gaps_f)
            continue
        for gi, ti in cells:
            sc = score_stream(gt, decode(p, threshold=grid[ti],
                                         merge_gap_frames=gaps_f[gi]).to_seconds(enc))
            rows[i, gi, ti] = [getattr(sc, k) for k in FIELDS]
            tol = sc.tol_sec
    out.parent.mkdir(parents=True, exist_ok=True)
    tmp = out.with_name(out.stem + f".tmp{os.getpid()}.npz")
    np.savez_compressed(tmp, rows=rows, rids=np.asarray(rids),
                        meta=np.asarray(json.dumps(dict(tol_sec=tol, partial=pairs is not None))))
    os.replace(tmp, out)
    return rec["stem"], "ok" if pairs is None else f"partial, {len(cells)} cells"


def _init_worker():
    import torch
    torch.set_num_threads(2)


def _pool_run(fn, jobs, workers):
    t0, n = time.perf_counter(), 0
    with Pool(workers, initializer=_init_worker) as pool:
        for stem, status in pool.imap_unordered(fn, jobs, chunksize=1):
            n += 1
            if status != "cached" and (not isinstance(status, dict) or not all(
                    v is not False for v in status.values())):
                print(f"  {stem}: {status}", flush=True)
            if n % 50 == 0 or n == len(jobs):
                print(f"{n}/{len(jobs)} in {time.perf_counter() - t0:.0f} s", flush=True)


# ---- reading the scored arrays back as the tuning tool's rows ----------------------------------

class Scored:
    """The npz files, read back into the row and empty-recording shapes the tuning tool's rules read."""

    def __init__(self, work: Path):
        self.work = Path(work)
        self._cache: dict = {}

    def _npz(self, kind, rec):
        k = (kind, rec["stem"], rec["config_key"], rec["model"])
        if k not in self._cache:
            p = work_path(self.work, kind, rec)
            if not p.exists():
                return None
            z = np.load(p)
            self._cache[k] = {n: z[n] for n in z.files}
            self._cache[k]["meta"] = json.loads(str(self._cache[k]["meta"]))
        return self._cache[k]

    @staticmethod
    def _row(a, tol):
        return dict(zip(FIELDS, (int(x) for x in a)), by_frac={}, tol_sec=tol)

    def own(self, rec, gi) -> int:
        return int(self._npz("bench", rec)["own"][gi])

    def items(self, rec, f, gi, ti):
        z = self._npz("bench", rec)
        tol = z["meta"]["tol_sec"]
        return [(str(rid), self._row(z[f"rows{f}"][i, gi, ti], tol))
                for i, rid in enumerate(z[f"rids{f}"])]

    def twins(self, rec, f, key, gi, ti):
        z = self._npz("bench", rec)
        k = TWIN_KEYS.index(key)
        return [dict(n_detected=int(z[f"twins{f}"][k, j, gi, ti]), duration_sec=float(z[f"dur{f}"][k, j]))
                for j in range(z[f"twins{f}"].shape[1])]

    def crowded(self, rec, gi, ti):
        z = self._npz("crowded", rec)
        if z is None or z["rows"][0, gi, ti, 0] < 0:     # absent, or a partial file without this cell
            return None
        return [(str(rid), self._row(z["rows"][i, gi, ti], z["meta"]["tol_sec"]))
                for i, rid in enumerate(z["rids"])]

    def repro(self, rec):
        z = self._npz("bench", rec)
        return z["meta"]["repro"]


# ---- the selection ------------------------------------------------------------------------------

def _paired(a, b):
    d = [x - y for x, y in zip(a, b)]
    sd = float(np.std(d, ddof=1)) if len(d) > 1 else float("nan")
    t = float(np.mean(d) / (sd / math.sqrt(len(d)))) if len(d) > 1 and sd > 0 else None
    return dict(per_fold=d, mean=float(np.mean(d)), sd=sd, t=t,
                t_corrected=None if t is None else t * nb_factor(len(d)), df=len(d) - 1,
                folds_ahead=sum(x > 0 for x in d), folds=len(d),
                within_noise=bool(abs(float(np.mean(d))) < NOISE_F1))


class Selector:
    def __init__(self, run: Path, work: Path):
        from bugarach import bench
        self.T = _tool()
        self.run = Path(run)
        self.meta = read_json(self.run / "meta.json")
        self.decl = self.meta["declaration"]
        self.results = read_json(self.run / "results.json")
        self.recs = fit_records(self.run)
        self.S = Scored(work)
        self.grid = _grid()
        self.plan = SimpleNamespace(busy_sec=float(self.decl["busy_window_sec"]))
        self.gate = self.decl["gate_empty_recording"]
        self.min_gain = float(self.decl["hand_search"]["min_gain"])
        self.max_drop = float(bench.MAX_CROWDED_DROP)
        self.folds = list(range(self.decl["folds"]))
        self.tune_seeds = list(self.decl["tune_seeds"])
        self.configs = {m: sorted((read_json(p) for p in (self.run / "configs" / m).glob("*.json")),
                                  key=lambda c: c["draw_index"]) for m in NETS}
        from bugarach.learn.checkpoint import peek
        self.n_params = {}
        for r in self.recs:
            k = (r["model"], r["config_key"])
            if k not in self.n_params:
                self.n_params[k] = int(peek(Path(r["fit"]))["n_params"])
        self.needs_crowded: set = set()
        self.needs_pairs: set = set()
        # The run's recorded threshold indices only mean anything against the grid they were written
        # against: a grid that changed length or spacing since would re-point every gated selection.
        declared = [float(t) for t in self.decl["threshold_grid"]]
        assert self.grid == declared, ("the live THRESHOLD_GRID is not the one the run recorded: "
                                       f"{len(self.grid)} values against {len(declared)}")

    def training_folds(self, h):
        return [f for f in self.folds if f != h]

    def inner(self, m, key, h):
        """(fit record, scored fold) for every inner fit feeding outer fold h, as ``_inner`` reads them."""
        got = []
        for j in self.training_folds(h):
            pair = sorted(f for f in self.training_folds(h) if f != j)
            for r in self.recs:
                if (r["model"], r["config_key"], r["role"]) == (m, key, "inner") \
                        and r["train_folds"] == pair and r["seed"] in self.tune_seeds:
                    got.append((r, j))
        assert len(got) == len(self.training_folds(h)) * len(self.tune_seeds), (m, key, h, len(got))
        return got

    def outer(self, m, key, h):
        return [r for r in self.recs if (r["model"], r["config_key"], r["role"]) == (m, key, "outer")
                and r["train_folds"] == self.training_folds(h)]

    def _ti(self, w, r, gi, ti):
        return self.S.own(r, gi) if w == "ungated" else ti

    def inner_score(self, m, key, h, w, gi, ti=None):
        fits = self.inner(m, key, h)
        items = [it for r, j in fits for it in self.S.items(r, j, gi, self._ti(w, r, gi, ti))]
        f1 = self.T.objective(items, m)
        out = dict(f1=f1)
        if w == "gated":
            tw = [t for r, j in fits for t in self.S.twins(r, j, self.gate, gi, ti)]
            out.update(probe=self.T.probe_rates(items, self.plan), quiet=self.T.quiet_rate(tw))
            out["within"] = self.T.within(self.meta["budgets"][str(h)], out["probe"], out["quiet"])
        return out

    def crowded(self, m, key, h, w, gi, ti=None, fits=None):
        """Goal 1's crowded F1: each crowded background's pooled F1, averaged, over the given fits."""
        fits = [r for r, _ in self.inner(m, key, h)] if fits is None else fits
        items = []
        for r in fits:
            got = self.S.crowded(r, gi, self._ti(w, r, gi, ti))
            if got is None:
                self.needs_crowded.add((m, key))
                # Every fit of the set, so one `crowded --pairs` pass completes this candidate.
                self.needs_pairs |= {(x["model"], x["config_key"], x["stem"], gi,
                                      None if w == "ungated" else ti) for x in fits}
                return None
            items += got
        return self.T.objective(items, m)

    def candidates(self, m, h, w, keys):
        """Every (config, gap[, threshold]) candidate with its inner score and the tool's tie rank."""
        out = []
        for key in keys:
            conf = next(c for c in self.configs[m] if c["config_key"] == key)
            steps, ci = int(conf["training"]["steps"]), int(conf["draw_index"])
            for gi, g in enumerate(GAPS_SEC):
                for ti in ([None] if w == "ungated" else range(len(self.grid))):
                    s = self.inner_score(m, key, h, w, gi, ti)
                    if w == "gated" and not s["within"]:
                        continue
                    rank = ((s["f1"], -self.n_params[(m, key)], -steps, -ci, -g) if w == "ungated"
                            else (s["f1"], -self.n_params[(m, key)], -steps, self.grid[ti], -ci, -g))
                    out.append(dict(config_key=key, gap_sec=g, gi=gi, ti=ti, rank=rank, **s))
        return sorted(out, key=lambda c: c["rank"], reverse=True)

    def choose(self, m, h, w, keys, start):
        """Goal 1's move rule from the run's choice: best candidate gaining ``min_gain`` that passes
        the crowded check against the start; otherwise the start."""
        start_f1 = start["f1"]
        ref = self.crowded(m, start["config_key"], h, w, start["gi"], start["ti"])
        walked = []
        for c in self.candidates(m, h, w, keys):
            if c["f1"] < start_f1 + self.min_gain:
                break
            cr = self.crowded(m, c["config_key"], h, w, c["gi"], c["ti"])
            if cr is None or ref is None:
                return None, walked
            # Not scored there is not admissible, as goal 1's search has it (make_admissible) and as
            # the coded side's after-the-fact check has it: both sides must be finite, or the veto
            # would switch itself off in the direction that admits.
            ok = bool(math.isfinite(cr) and math.isfinite(ref) and cr >= ref - self.max_drop)
            walked.append(dict(config_key=c["config_key"], gap_sec=c["gap_sec"],
                               threshold=None if c["ti"] is None else self.grid[c["ti"]],
                               inner_f1=c["f1"], crowded_f1=cr, reference_crowded_f1=ref,
                               passes_crowded=ok))
            if ok:
                return dict(c, crowded_f1=cr, reference_crowded_f1=ref, moved=True), walked
        return dict(start, crowded_f1=ref, reference_crowded_f1=ref, moved=False), walked

    def heldout(self, m, key, h, w, gi, ti=None):
        per = []
        for r in sorted(self.outer(m, key, h), key=lambda r: r["seed"]):
            if r["seed"] not in self.decl["refit_seeds"]:
                continue
            t = self._ti(w, r, gi, ti)
            items = self.S.items(r, h, gi, t)
            # The run's own two flags, by its own expressions (_heldout): a refit that scores low
            # because it collapsed to one call is not the same thing as one that called nothing at
            # the threshold its selection chose, and the report's set-aside rule covers both.
            p = self.T.pooled([row for _, row in items], m)
            f1 = self.T.objective(items, m)
            x = dict(seed=r["seed"], f1=f1, threshold=self.grid[t],
                     f1_was_nan=not bool(np.isfinite(p.f1)),
                     failed_training_signature=bool(np.isfinite(p.f1) and abs(p.f1 - 0.125) < 0.01
                                                    and self.grid[t] <= 1e-4 + 1e-12),
                     threshold_at_grid_edge=t in (0, len(self.grid) - 1))
            if w == "gated":
                probe = self.T.probe_rates(items, self.plan)
                quiet = self.T.quiet_rate(self.S.twins(r, h, self.gate, gi, t))
                x.update(probe_per_hour=probe, quiet_per_hour=quiet,
                         over_budget=not self.T.within(self.meta["budgets"][str(h)], probe, quiet))
            per.append(x)
        if not per:
            return None
        doc = dict(per_seed=per, f1_mean=float(np.mean([x["f1"] for x in per])), n_seeds=len(per))
        if w == "gated":
            doc["seeds_over_budget"] = sum(x["over_budget"] for x in per)
        return doc

    def one(self, m, h, w):
        row = next(x for x in self.results["learned"][m] if x["outer_fold"] == h)[w]
        sel = read_json(self.run / "selections" / w / f"outer{h}" / f"{m}.json")
        key = sel["config_key"]
        g2 = gap_index(AS_RUN_SEC)
        ti0 = sel.get("threshold_index") if w == "gated" else None
        s0 = self.inner_score(m, key, h, w, g2, ti0)
        start = dict(config_key=key, gap_sec=AS_RUN_SEC, gi=g2, ti=ti0, **s0)
        held0 = self.heldout(m, key, h, w, g2, ti0)
        rep = dict(inner_f1=abs(s0["f1"] - sel["inner_f1"]), heldout_f1=abs(held0["f1_mean"] - row["f1_mean"]))
        doc = dict(outer_fold=h, selection=w, as_run=dict(config_key=key, gap_sec=AS_RUN_SEC,
                                                          threshold=None if ti0 is None else self.grid[ti0],
                                                          inner_f1=s0["f1"], heldout=held0),
                   reproduces_run=rep)
        for variant, keys in (("config_kept", [key]),
                              ("config_rechosen", [c["config_key"] for c in self.configs[m]])):
            c, walked = self.choose(m, h, w, keys, start)
            if c is None:
                doc[variant] = dict(result="crowded recordings not scored yet", walked=walked)
                continue
            held = self.heldout(m, c["config_key"], h, w, c["gi"], c["ti"])
            ent = dict(config_key=c["config_key"], config_changed=c["config_key"] != key,
                       gap_sec=c["gap_sec"], gap_at_grid_edge=c["gi"] in (0, len(GAPS_SEC) - 1),
                       threshold=None if c["ti"] is None else self.grid[c["ti"]],
                       inner_f1=c["f1"], inner_gain=c["f1"] - s0["f1"], moved=c["moved"],
                       crowded_f1=c["crowded_f1"], reference_crowded_f1=c["reference_crowded_f1"],
                       refused_by_crowded=[x for x in walked if not x["passes_crowded"]],
                       heldout=held,
                       heldout_note=None if held is not None else "no outer refits of this "
                       "configuration: the run refitted only the configurations it chose, and this "
                       "re-selection does not retrain")
            if held is not None and variant == "config_kept":
                # What the held-out fold would have said at every gap, for the chosen threshold rule:
                # descriptive, never used to choose.
                ent["heldout_f1_by_gap"] = {
                    f"{g:g}": self.heldout(m, c["config_key"], h, w, gi, c["ti"])["f1_mean"]
                    for gi, g in enumerate(GAPS_SEC)}
                ent["outer_crowded_f1"] = self.crowded(m, c["config_key"], h, w, c["gi"], c["ti"],
                                                       fits=self.outer(m, c["config_key"], h))
                ent["outer_crowded_f1_as_run"] = self.crowded(m, key, h, w, g2, ti0,
                                                              fits=self.outer(m, key, h))
            doc[variant] = ent
        return doc

    def select(self) -> dict:
        from bugarach import bench
        coact = {row["outer_fold"]: row for row in self.results["hand"]["coact"]}
        crowded_coded = read_json(self.run_summary / "crowded_check.json") if self.run_summary else None
        out = dict(nets={}, comparisons={})
        for m in NETS:
            out["nets"][m] = {w: [self.one(m, h, w) for h in self.folds] for w in SELECTIONS}
            print(m, "selected", flush=True)
        for w in SELECTIONS:
            cf = [coact[h][w]["f1"] for h in self.folds]
            comp = {}
            for m in NETS:
                rows = out["nets"][m][w]
                for variant in ("as_run", "config_kept", "config_rechosen"):
                    vals = []
                    for r in rows:
                        e = r[variant]
                        held = e.get("heldout") if isinstance(e, dict) else None
                        vals.append(None if held is None else held["f1_mean"])
                    if all(v is not None for v in vals):
                        comp[f"{m} {variant} - coact"] = _paired(vals, cf)
            out["comparisons"][w] = comp
        coact_pass = None
        if crowded_coded:
            coact_pass = {f"{c['outer_fold']} {c['selection']}": c["passes_veto"]
                          for c in crowded_coded["choices"] if c["detector"] == "coact"}
        out["coact"] = dict(f1={w: [coact[h][w]["f1"] for h in self.folds] for w in SELECTIONS},
                            merge_gap_sec={w: [coact[h][w]["chosen_params"]["merge_gap_sec"]
                                               for h in self.folds] for w in SELECTIONS},
                            passes_crowded_check=coact_pass)
        return out

    run_summary = None


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("stage", choices=("score", "crowded", "select"))
    ap.add_argument("--run", type=Path, required=True, help="the run folder, with fits/ and scores/")
    ap.add_argument("--work", type=Path, required=True, help="a scratch folder outside the repository")
    ap.add_argument("--summary", type=Path, default=DEFAULT_OUT.parent,
                    help="the run's committed summary folder (crowded_check.json)")
    ap.add_argument("--out", type=Path, default=DEFAULT_OUT)
    ap.add_argument("--workers", type=int, default=12)
    ap.add_argument("--all", action="store_true",
                    help="crowded: every configuration, not only the ones a selection reaches. The "
                         "re-chosen walk passes over every candidate the crowded check refuses, so "
                         "it can reach most configurations one pass at a time")
    ap.add_argument("--pairs", action="store_true",
                    help="crowded: only the (gap, threshold) pairs `select` found missing, listed in "
                         "crowded_pairs.json, for fits whose full grid is impractical")
    a = ap.parse_args(argv)
    decl = read_json(a.run / "meta.json")["declaration"]
    recs = fit_records(a.run)

    if a.stage == "score":
        print(f"{len(recs)} fits x {len(GAPS_SEC)} gaps", flush=True)
        _pool_run(score_job, [(r, str(a.run), str(a.work), decl) for r in recs], a.workers)
        return 0

    if a.stage == "crowded":
        want = set()
        for w in SELECTIONS:
            for h in range(decl["folds"]):
                for m in NETS:
                    want.add((m, read_json(a.run / "selections" / w / f"outer{h}" / f"{m}.json")["config_key"]))
        extra = a.work / "crowded_wanted.json"
        if extra.exists():
            want |= {tuple(x) for x in read_json(extra)}
        if a.all:
            want = {(r["model"], r["config_key"]) for r in recs}
        jobs = [(r, str(a.work)) for r in recs if (r["model"], r["config_key"]) in want]
        if a.pairs:
            got: dict = {}
            for m, key, stem, gi, ti in read_json(a.work / "crowded_pairs.json"):
                got.setdefault((m, key, stem), []).append([gi, ti])
            jobs = [(r, str(a.work), got[(r["model"], r["config_key"], r["stem"])]) for r in recs
                    if (r["model"], r["config_key"], r["stem"]) in got]
            want = {(r["model"], r["config_key"]) for r, *_ in jobs}
        print(f"{len(want)} configurations, {len(jobs)} fits on {len(TAIL) * len(TAIL_SEEDS)} "
              f"crowded recordings", flush=True)
        _pool_run(crowded_job, jobs, a.workers)
        return 0

    sel = Selector(a.run, a.work)
    sel.run_summary = a.summary if (a.summary / "crowded_check.json").exists() else None
    doc = sel.select()
    if sel.needs_crowded:
        p = a.work / "crowded_wanted.json"
        prev = {tuple(x) for x in read_json(p)} if p.exists() else set()
        p.write_text(json.dumps(sorted(prev | sel.needs_crowded)) + "\n")
        pp = a.work / "crowded_pairs.json"
        prev_p = {tuple(x) for x in read_json(pp)} if pp.exists() else set()
        pp.write_text(json.dumps(sorted(prev_p | sel.needs_pairs,
                                        key=lambda x: tuple(-1 if v is None else v for v in x)))
                      + "\n")
        print(f"{len(sel.needs_crowded)} more configurations need the crowded recordings: "
              f"run `crowded`, then `select` again", flush=True)
        return 1
    repro = [sel.S.repro(r) for r in sel.recs]
    doc = dict(
        what="the nets' merge gap tuned like any other setting, re-selected from the fair "
             "comparison's saved fits without retraining",
        generator="tools/tune_net_merge_gap.py", run=a.run.name, provenance=_provenance(),
        gaps_sec=list(GAPS_SEC), as_run_gap_sec=AS_RUN_SEC, min_gain=sel.min_gain,
        max_crowded_drop=sel.max_drop, crowded_recordings=dict(builder="bench.make_tail_recording",
                                                               backgrounds=list(TAIL.values()),
                                                               seeds=list(TAIL_SEEDS)),
        noise_f1=NOISE_F1, nb_factor=nb_factor(sel.decl["folds"]),
        reproduction=dict(
            fits=len(repro),
            own_threshold_at_2s=sum(bool(x["own_index"]) for x in repro),
            rows_at_2s=sum(x["rows"] is True for x in repro),
            rows_without_score_file=sum(x["rows"] is None for x in repro),
            empty_recordings_at_2s=sum(x["twins"] is True for x in repro)),
        **doc)
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps(doc, indent=1, default=float) + "\n", encoding="utf-8")
    print(a.out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
