#!/usr/bin/env python3
"""Run the surrogate screen's grid on one export folder and write the measurements.

    python tools/build_surrogate_screen.py --role steps_excluded
    python tools/build_surrogate_screen.py --role cossart --jobs 12
    python tools/build_surrogate_screen.py --dataset some/export --J-frames 1 2 4

**Measures; decides nothing.** The plan
(``docs/proposals/2026-09-10-surrogate-evaluation-overnight.md``) runs every
candidate on both folders and shortlists none — the verdict rule is designed from
these numbers afterwards. So every statistic is written beside all three
yardsticks, raw and Holm-adjusted, and nothing here ranks, gates or picks.

What it writes to ``--out`` (default ``darkroom()/2026-09-11-surrogate-screen/<role>/``;
real recordings never reach a git tree — FOUNDATIONS §5):

* ``meta.json`` — the folder, the grid, the provisional dead times *f*, every
  skipped recording and why, the K asked for, and what each window was.
* ``<stream>/yardsticks.json`` — per scope (``all`` and each group): the
  mouse-split band per statistic, and the exchangeable-negative flag rates
  (a real held-out half, and fresh synthetic draws).
* ``<stream>/cells/<cell>.json`` — one grid cell: status, the K it reached, cost,
  movement, every statistic in every scope with its paired and band P (raw and
  Holm per cell), the adapter's counters, and the destruction measure.
* ``cells.csv``, ``stats.csv``, ``destruction.csv``, ``yardsticks.csv``,
  ``control_power.csv`` and ``summary.json``, rebuilt from the JSON at the end.

**Cost caps.** Each cell runs in its own process. Generation stops taking draws
once ``--cell-seconds`` is spent (never below ``--min-K``); a cell that cannot
reach ``--min-K``, runs past ``--cell-hard-seconds`` or grows past
``--cell-mem-gb`` is killed and recorded as **intractable** with the reason,
and the grid carries on. Finished cells are kept, so a rerun resumes
(``--force`` to redo). ``--jobs 0`` runs in-process with no kill (tests).
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import os
import pickle
import shutil
import subprocess
import sys
import tempfile
import time
import traceback
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _dataset_arg  # noqa: E402

from bugarach import surrogate_stats as ss  # noqa: E402

OUT_DIRNAME = "2026-09-11-surrogate-screen"

# ---- the grid (the plan's Table 4) ----------------------------------------
J_SEC = {"fast": (0.1, 0.2, 0.4, 0.8, 1.6, 2.5),
         "slow": (0.7, 1.4, 2.5, 2.8, 5.6, 11.2)}
J_FRAMES_COSSART = (1, 2, 4, 8, 16, 32)
SHIPPED_EXTRA_SEC = 20.0
F_MULTS = (0.5, 0.75, 1.0)
F_FRAMES_COSSART = (1, 2)
OT_BANDWIDTH_MIN = (2, 5, 10)
JISI_SIGMA_RATIOS = (0.5, 1.0)
JISI_SQRT = (True, False)

NO_PARAMS = ("circular_shift", "do_nothing", "interval_shuffle",
             "homogeneous_resample")
J_ONLY = ("uniform_dither", "shipped_dither", "rigid_shift", "interval_jitter",
          "window_shuffle")
EDGE = ("edge_thinning", "edge_piling")
J_AND_F = ("dead_time_dither", "trial_shift", "pattern_jitter")
JISI = ("joint_isi", "isi_dither")


def _round_half_up(x: float) -> int:
    return int(math.floor(x + 0.5))


def _kind(name: str) -> str:
    from bugarach import surrogates
    return "control" if name in surrogates.CONTROLS else "candidate"


def build_grid(*, J_values, J_unit: str, f_frames: dict, only=None,
               shipped_extra: bool = True) -> list[dict]:
    """Every grid cell for one stream, cheapest first.

    ``f_frames`` maps an *f* label to whole frames. Generators that do not use
    *f* get one cell per *J*; their *f*-dependent statistics are computed at every
    *f* from the same draws. The freeze-half destruction control is its own cell.
    """
    cells = []

    def add(name, **kw):
        if only and name not in only and not (name == "freeze_half" and
                                              "circular_shift" in only):
            return
        c = {"name": name, "J": None, "J_unit": J_unit, "f": None, "f_label": None,
             "sigma_ratio": None, "use_sqrt": None, "bandwidth_min": None,
             "freeze_half": False, "destruction_only": False}
        c.update(kw)
        parts = [c["name"] if name != "freeze_half" else "freeze_half"]
        if c["J"] is not None:
            parts.append(f"J{c['J']:g}{'s' if c['J_unit'] == 'sec' else 'fr'}")
        if c["f"] is not None:
            parts.append(f"f{c['f']}")
        if c["sigma_ratio"] is not None:
            parts.append(f"sig{c['sigma_ratio']:g}J")
        if c["use_sqrt"] is not None:
            parts.append("sqrt" if c["use_sqrt"] else "nosqrt")
        if c["bandwidth_min"] is not None:
            parts.append(f"bw{c['bandwidth_min']:g}min")
        c["id"] = "__".join(parts)
        if name == "freeze_half":
            c["name"] = "circular_shift"
        cells.append(c)

    for n in NO_PARAMS:
        add(n)
    add("freeze_half", freeze_half=True, destruction_only=True)
    add("window_circular_shift")
    for n in J_ONLY:
        for J in J_values:
            add(n, J=J)
    if shipped_extra:
        add("shipped_dither", J=SHIPPED_EXTRA_SEC, J_unit="sec")
    for n in EDGE:
        for J in J_values:
            add(n, J=J)
    for n in J_AND_F:
        for J in J_values:
            for lab, f in f_frames.items():
                add(n, J=J, f=f, f_label=lab)
    for J in J_values:
        for bw in OT_BANDWIDTH_MIN:
            add("operational_time", J=J, bandwidth_min=bw)
    for n in JISI:
        for J in J_values:
            for lab, f in f_frames.items():
                for sr in JISI_SIGMA_RATIOS:
                    for sq in JISI_SQRT:
                        add(n, J=J, f=f, f_label=lab, sigma_ratio=sr, use_sqrt=sq)
    for c in cells:
        c["kind"] = _kind(c["name"])
    return cells


def params_for(cell: dict, dt: float) -> dict:
    """The adapter's parameters for one cell on a recording of interval ``dt``.

    Every parameter the adapter takes is in frames; *J* given in seconds is
    converted with the recording's own ``dt``.
    """
    name = cell["name"]
    Jf = None
    if cell["J"] is not None:
        Jf = cell["J"] / dt if cell["J_unit"] == "sec" else float(cell["J"])
        Jf = round(Jf, 9)
    aw = max(1, _round_half_up(ss.ANALYSIS_WINDOW_SEC / dt))
    if name in NO_PARAMS:
        return {}
    if name in J_ONLY:
        return {"J": Jf}
    if name in EDGE:
        return {"J": Jf, "analysis_window": aw}
    if name == "window_circular_shift":
        return {"analysis_window": aw}
    if name in J_AND_F:
        return {"J": Jf, "f": int(cell["f"])}
    if name in JISI:
        return {"J": Jf, "f": int(cell["f"]), "sigma": cell["sigma_ratio"] * Jf,
                "use_sqrt": bool(cell["use_sqrt"])}
    if name == "operational_time":
        return {"J": Jf,
                "bandwidth": float(_round_half_up(cell["bandwidth_min"] * 60.0 / dt))}
    raise KeyError(f"no parameter rule for {name!r}")


# ---- JSON ------------------------------------------------------------------

def _clean(x):
    """JSON-ready: numpy scalars to Python, NaN and infinities to null."""
    if isinstance(x, dict):
        return {str(k): _clean(v) for k, v in x.items()}
    if isinstance(x, (list, tuple)):
        return [_clean(v) for v in x]
    if isinstance(x, np.ndarray):
        return _clean(x.tolist())
    if isinstance(x, (np.bool_, bool)):
        return bool(x)
    if isinstance(x, np.integer):
        return int(x)
    if isinstance(x, (np.floating, float)):
        v = float(x)
        return v if math.isfinite(v) else None
    return x


# ON WINDOWS, A FILE DROPBOX IS SYNCING CANNOT BE REPLACED, AND ONE REFUSAL KILLED A CELL.
# The run folder lives in the darkroom, so Dropbox uploads every record and progress file
# as it changes; while it holds one, Windows refuses the swap below with PermissionError
# (WinError 5). It killed two cells of the 2026-09-11 run on the workstation -- at 12:45
# and 15:06, both while replacing a `.progress` file after a draw -- and each became an
# error record the resume then skips. Dropbox lets go within moments, so the swap is
# retried with doubling waits (about 6 s in all) before the refusal is allowed to stand.
# Only the refusal is retried: any other error still fails at once.
_REPLACE_ATTEMPTS = 8
_REPLACE_FIRST_WAIT_SEC = 0.05


def _write_json(path: Path, obj) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(_clean(obj), indent=1, sort_keys=True), encoding="utf-8")
    wait = _REPLACE_FIRST_WAIT_SEC
    for attempt in range(_REPLACE_ATTEMPTS):
        try:
            os.replace(tmp, path)
            return
        except PermissionError:
            if attempt == _REPLACE_ATTEMPTS - 1:
                raise
            time.sleep(wait)
            wait *= 2


# ---- the adapter's counters, aggregated per cell ---------------------------

def aggregate_info(infos: list[dict]) -> dict:
    """Sum the adapter's counters over every (recording, draw) of a cell."""
    out = {"n_calls": len(infos), "n_in": 0, "n_out": 0, "outside_window": 0,
           "counts": {}, "per_roi_sums": {}, "dead_time_in_effect": None}
    dte = []
    for inf in infos:
        out["n_in"] += int(np.sum(inf.get("n_in", 0)))
        out["n_out"] += int(np.sum(inf.get("n_out", 0)))
        out["outside_window"] += int(inf.get("outside_window", 0) or 0)
        for k, v in (inf.get("counts") or {}).items():
            out["counts"][k] = out["counts"].get(k, 0) + int(v)
        # flat_at_onset: operational-time onsets with no rate of their own, which
        # move even at J = 0 — its author asked for it to reach the record.
        for k in ("dropped", "clipped", "jisi_fallback_steps", "jisi_too_few",
                  "jisi_moved_nothing", "jisi_intractable", "flat_at_onset"):
            if k in inf:
                out["per_roi_sums"][k] = (out["per_roi_sums"].get(k, 0)
                                          + int(np.sum(np.asarray(inf[k]))))
        if "dead_time_in_effect" in inf:
            a = np.asarray(inf["dead_time_in_effect"], dtype=float)
            dte.append(a[np.isfinite(a)])
    if dte:
        a = np.concatenate(dte)
        if a.size:
            out["dead_time_in_effect"] = {"min": float(a.min()),
                                          "median": float(np.median(a)),
                                          "max": float(a.max())}
    if infos:
        out["params_first"] = infos[0].get("params")
    return out


# ---- one cell, in a worker -------------------------------------------------

def run_cell(cell: dict, ctx_path: str, out_path: str) -> None:
    """Draw, score and measure destruction for one cell; write its JSON."""
    t0 = time.perf_counter()
    rec = {"cell": cell, "status": "error", "stream": None}
    try:
        with open(ctx_path, "rb") as fh:
            ctx = pickle.load(fh)
        rec["stream"] = ctx["stream"]
        recs, fs = ctx["recs"], ctx["fs"]
        st = ctx["settings"]
        dest = None
        if not cell["destruction_only"]:
            prog = Path(out_path + ".progress")
            draws = ss.draw_surrogates(
                cell["name"], recs, st["K"], cell["id"],
                lambda r: params_for(cell, r.dt),
                min_K=st["min_K"], time_budget=st["cell_seconds"],
                progress=lambda d: _write_json(prog, d))
            prog.unlink(missing_ok=True)
            rec["K"] = draws.K
            rec["stopped"] = draws.stopped
            n_roi = max(1, draws.n_roi)
            rec["cost"] = {
                "seconds_generation": draws.seconds,
                "seconds_per_roi_per_draw": draws.seconds / n_roi / max(1, draws.K),
                "peak_bytes_first_draw": draws.peak_bytes,
                "peak_bytes_per_roi": draws.peak_bytes / n_roi,
                "n_roi": draws.n_roi}
            ne = int(sum(int(v.sum()) for v in draws.not_estimable.values()))
            rec["not_estimable_rois"] = ne
            rec["adapter"] = aggregate_info(draws.info)
            if draws.K < st["min_K"]:
                rec["status"] = "intractable"
                rec["why"] = draws.stopped or f"reached only {draws.K} draws"
                _write_json(Path(out_path), rec)
                return
            rec["result"] = ss.score_cell(recs, draws, fs, cell["id"], ctx["scopes"],
                                          ctx["split_info"], alpha=st["alpha"])
            del draws
        if ctx.get("twins") is not None and not st.get("skip_destruction"):
            tw = ctx["twins"]
            dest = ss.destruction(
                cell["name"], params_for(cell, tw["dt"]), tw["pairs"], tw["n_frames"],
                tw["dt"], n_draws=st["destruction_draws"], cell_id=cell["id"],
                stream=ctx["stream"], freeze_half=cell["freeze_half"],
                n_assess_surrogates=st["destruction_assess_surrogates"])
        rec["destruction"] = dest
        rec["status"] = "ok"
    except Exception as e:                                 # noqa: BLE001
        rec["status"] = "error"
        rec["why"] = f"{type(e).__name__}: {e}"
        rec["traceback"] = traceback.format_exc()
    rec["seconds_total"] = time.perf_counter() - t0
    _write_json(Path(out_path), rec)


def run_negatives(ctx_path: str, out_path: str) -> None:
    """The fresh-synthetic exchangeable negative, per scope (a worker task)."""
    t0 = time.perf_counter()
    with open(ctx_path, "rb") as fh:
        ctx = pickle.load(fh)
    st = ctx["settings"]
    out = {"stream": ctx["stream"], "scopes": {}}
    try:
        by_id = {r.recording_id: r for r in ctx["recs"]}
        for scope, ids in ctx["scopes"].items():
            out["scopes"][scope] = ss.negative_rates_synthetic(
                [by_id[i] for i in ids], ctx["split_info"][scope], ctx["fs"],
                ctx["f_synthetic"], n_rep=st["neg_reps"], n_draws=st["neg_draws"],
                key=("negative", ctx["role"], ctx["stream"], scope), alpha=st["alpha"])
        out["status"] = "ok"
    except Exception as e:                                 # noqa: BLE001
        out["status"] = "error"
        out["why"] = f"{type(e).__name__}: {e}"
        out["traceback"] = traceback.format_exc()
    out["seconds_total"] = time.perf_counter() - t0
    _write_json(Path(out_path), out)


def _worker(kind, *args):
    if kind == "cell":
        run_cell(*args)
    else:
        run_negatives(*args)


# ON WINDOWS BOTH MEMORY CAPS WERE DISARMED, AND NOTHING SAID SO. `ps -o rss=` is a
# procps flag; Git for Windows puts a Cygwin `ps` on PATH that has no -o, so the call
# failed, the except returned 0, and every worker read as holding nothing — measured
# 2026-09-11 on the workstation: 0 bytes with 300 MB allocated. Neither the per-cell
# cap nor the all-workers cap could fire. `os.sysconf` does not exist there either, so
# the machine read as the 16 GB fallback rather than its 127 GB, and the all-workers
# default was computed from a guess. Both now ask the Windows API directly (ctypes,
# still no psutil). The same resident measure — the working set — keeps the recorded
# reason meaning one thing on every platform. tests/test_build_surrogate_screen.py
# asserts a live process reads nonzero, which is the check that would have caught it.
def _rss_bytes_windows(pid: int) -> int:
    import ctypes
    from ctypes import wintypes

    class _Counters(ctypes.Structure):
        _fields_ = [("cb", wintypes.DWORD), ("PageFaultCount", wintypes.DWORD),
                    ("PeakWorkingSetSize", ctypes.c_size_t),
                    ("WorkingSetSize", ctypes.c_size_t),
                    ("QuotaPeakPagedPoolUsage", ctypes.c_size_t),
                    ("QuotaPagedPoolUsage", ctypes.c_size_t),
                    ("QuotaPeakNonPagedPoolUsage", ctypes.c_size_t),
                    ("QuotaNonPagedPoolUsage", ctypes.c_size_t),
                    ("PagefileUsage", ctypes.c_size_t),
                    ("PeakPagefileUsage", ctypes.c_size_t)]

    k32 = ctypes.WinDLL("kernel32", use_last_error=True)
    k32.OpenProcess.restype = wintypes.HANDLE
    k32.OpenProcess.argtypes = [wintypes.DWORD, wintypes.BOOL, wintypes.DWORD]
    k32.K32GetProcessMemoryInfo.argtypes = [wintypes.HANDLE,
                                            ctypes.POINTER(_Counters), wintypes.DWORD]
    k32.CloseHandle.argtypes = [wintypes.HANDLE]
    handle = k32.OpenProcess(0x1000, False, pid)   # PROCESS_QUERY_LIMITED_INFORMATION
    if not handle:
        return 0
    try:
        c = _Counters()
        c.cb = ctypes.sizeof(_Counters)
        ok = k32.K32GetProcessMemoryInfo(handle, ctypes.byref(c), c.cb)
        return int(c.WorkingSetSize) if ok else 0
    finally:
        k32.CloseHandle(handle)


def _rss_bytes(pid: int) -> int:
    """Resident memory of ``pid``: ``ps`` on POSIX, the Windows API on Windows
    (no psutil here). 0 when the process cannot be read."""
    try:
        if sys.platform == "win32":
            return _rss_bytes_windows(pid)
        out = subprocess.run(["ps", "-o", "rss=", "-p", str(pid)],
                             capture_output=True, text=True, timeout=5).stdout
        return int(out.strip() or 0) * 1024
    except Exception:                                      # noqa: BLE001
        return 0


def _machine_ram_bytes() -> float:
    try:
        if sys.platform == "win32":
            import ctypes
            from ctypes import wintypes

            class _Status(ctypes.Structure):
                _fields_ = [("dwLength", wintypes.DWORD),
                            ("dwMemoryLoad", wintypes.DWORD),
                            ("ullTotalPhys", ctypes.c_ulonglong),
                            ("ullAvailPhys", ctypes.c_ulonglong),
                            ("ullTotalPageFile", ctypes.c_ulonglong),
                            ("ullAvailPageFile", ctypes.c_ulonglong),
                            ("ullTotalVirtual", ctypes.c_ulonglong),
                            ("ullAvailVirtual", ctypes.c_ulonglong),
                            ("ullAvailExtendedVirtual", ctypes.c_ulonglong)]

            s = _Status()
            s.dwLength = ctypes.sizeof(_Status)
            if ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(s)):
                return float(s.ullTotalPhys)
            return 16e9
        return float(os.sysconf("SC_PAGE_SIZE") * os.sysconf("SC_PHYS_PAGES"))
    except (ValueError, OSError, AttributeError):
        return 16e9


def schedule(tasks, *, jobs: int, hard_seconds: float, mem_bytes: float,
             total_mem_bytes: float | None = None, log=print) -> None:
    """Run ``tasks`` (``(kind, args, out_path, label)``) with at most ``jobs``
    processes, killing any that pass the time or memory cap.

    A killed task gets an ``intractable`` record naming the cap it hit. While
    the workers together hold more than ``total_mem_bytes``, no new task starts
    — the per-cell cap alone would let a dozen workers take the machine. ``jobs``
    of 0 runs everything in this process, in order, with no caps.
    """
    if jobs <= 0:
        for i, (kind, args, out_path, label) in enumerate(tasks):
            log(f"[{i + 1}/{len(tasks)}] {label}")
            _worker(kind, *args)
        return
    import multiprocessing as mp

    ctx = mp.get_context("spawn")
    pending = list(tasks)
    active = {}
    done = 0
    rss_now = {}
    while pending or active:
        # A new worker starts only while the running ones leave room for it.
        while (pending and len(active) < jobs
               and (total_mem_bytes is None or not active
                    or sum(rss_now.get(pid, 0) for pid in active)
                    < total_mem_bytes)):
            kind, args, out_path, label = pending.pop(0)
            p = ctx.Process(target=_worker, args=(kind, *args), daemon=False)
            p.start()
            active[p.pid] = (p, kind, args, out_path, label, time.time())
        time.sleep(0.5)
        for pid in list(active):
            p, kind, args, out_path, label, t_start = active[pid]
            el = time.time() - t_start
            why = None
            if p.is_alive():
                if el > hard_seconds:
                    why = f"killed after {el:.0f} s (cap {hard_seconds:.0f} s)"
                else:
                    rss = _rss_bytes(pid)
                    rss_now[pid] = rss
                    if rss > mem_bytes:
                        why = (f"killed at {rss / 1e9:.2f} GB resident "
                               f"(cap {mem_bytes / 1e9:.2f} GB)")
                if why is None:
                    continue
                p.terminate()
                p.join(10)
                if p.is_alive():
                    p.kill()
                    p.join(5)
            else:
                p.join()
            del active[pid]
            done += 1
            if why is not None or not Path(out_path).exists():
                rec = {"status": "intractable" if why else "error",
                       "why": why or f"worker exited with code {p.exitcode} "
                                     f"and wrote nothing",
                       "seconds_total": el}
                if kind == "cell":
                    rec["cell"] = args[0]
                # How far a killed cell got: the worker leaves this after each
                # draw, so "no draw finished" and "stopped at draw 12" differ.
                prog = Path(out_path + ".progress")
                if prog.exists():
                    try:
                        rec["progress_at_kill"] = json.loads(
                            prog.read_text(encoding="utf-8"))
                    except (OSError, ValueError):
                        pass
                    prog.unlink(missing_ok=True)
                else:
                    rec["progress_at_kill"] = {"draws_completed": 0}
                _write_json(Path(out_path), rec)
            log(f"[{done}/{done + len(active) + len(pending)}] {label} "
                f"{'— ' + why if why else ''}({el:.0f} s)")


# ---- per-stream preparation -------------------------------------------------

def prepare_stream(recs, *, role: str, stream: str, J_values, J_unit, f_frames,
                   f_labels, n_splits: int, alpha: float, no_destruction: bool):
    """Everything a worker needs for one stream, computed once in the parent."""
    fs = dict(zip(f_labels, f_frames))
    groups = sorted({r.group for r in recs if r.group})
    scopes = {"all": [r.recording_id for r in recs]}
    for g in groups:
        scopes[g] = [r.recording_id for r in recs if r.group == g]
    strata = {r.mouse: r.group for r in recs}
    real = {r.recording_id: ss.summarize(r.trains, r.window, r.dt, fs, widths=r.widths,
                                         rng=ss.serial_rng(r))
            for r in recs}
    split_info, heldout, bands, n_mice = {}, {}, {}, {}
    for scope, ids in scopes.items():
        sub = [r for r in recs if r.recording_id in ids]
        mice = sorted({r.mouse for r in sub})
        n_mice[scope] = len(mice)
        if len(mice) < 2:
            split_info[scope] = {}
            heldout[scope] = {"why": "fewer than two mice"}
            continue
        splits = ss.mouse_splits(mice, n_splits, key=("splits", role, stream, scope),
                                 strata=strata if scope == "all" else None)
        diffs, halves = ss.split_diffs(real, sub, splits, fs)
        split_info[scope] = diffs
        bands[scope] = {nm: ss.band(d) for nm, d in diffs.items()}
        heldout[scope] = ss.negative_rates_heldout(halves, fs, alpha=alpha)
    twins = None
    if not no_destruction and recs:
        dt = float(np.median([r.dt for r in recs]))
        n_frames = int(np.median([r.n_frames for r in recs]))
        n_roi = int(np.median([len(r.trains) for r in recs]))
        rates = np.concatenate([[v.size / max(1, r.n_frames) for v in r.trains]
                                for r in recs])
        f_tw = int(max(f_frames))
        pairs = {}
        for p in ss.DESTRUCTION_PARTICIPATION:
            g = ss.rng_of(("twins", role, stream, p))
            counts = g.poisson(g.choice(rates, size=n_roi, replace=True) * n_frames)
            pl, un, gt = ss.destruction_twins(n_roi, n_frames, dt, f_tw, counts, p,
                                              seed=ss.seed_of(("twin-seed", role,
                                                               stream, p)))
            pairs[p] = (pl, un)
        twins = {"dt": dt, "n_frames": n_frames, "n_roi": n_roi, "f_frames": f_tw,
                 "pairs": pairs,
                 "describe": {"n_roi": n_roi, "n_frames": n_frames, "dt": dt,
                              "f_frames": f_tw,
                              "planted_jitter_frames": ss.DESTRUCTION_JITTER_FRAMES,
                              "coincidence_half_window_frames":
                                  ss.DESTRUCTION_HALF_WINDOW_FRAMES,
                              "participation": list(ss.DESTRUCTION_PARTICIPATION)}}
    return {"fs": fs, "scopes": scopes, "split_info": split_info, "bands": bands,
            "heldout": heldout, "twins": twins, "n_mice": n_mice, "groups": groups}


# ---- tables at the end ------------------------------------------------------

def write_tables(out: Path, streams: list[str]) -> dict:
    """Rebuild every CSV from the per-cell JSON; return the summary."""
    cells_rows, stat_rows, dest_rows, yard_rows, power_rows = [], [], [], [], []
    status_counts = {}
    destruction_status = {}
    for stream in streams:
        cdir = out / stream / "cells"
        for p in sorted(cdir.glob("*.json")) if cdir.exists() else []:
            rec = json.loads(p.read_text(encoding="utf-8"))
            c = rec.get("cell") or {}
            status_counts[rec.get("status")] = status_counts.get(rec.get("status"), 0) + 1
            cost = rec.get("cost") or {}
            mv = ((rec.get("result") or {}).get("movement")) or {}
            cells_rows.append({
                "stream": stream, "cell_id": c.get("id"), "name": c.get("name"),
                "kind": c.get("kind"), "J": c.get("J"), "J_unit": c.get("J_unit"),
                "f": c.get("f"), "f_label": c.get("f_label"),
                "sigma_ratio": c.get("sigma_ratio"), "use_sqrt": c.get("use_sqrt"),
                "bandwidth_min": c.get("bandwidth_min"), "status": rec.get("status"),
                "why": rec.get("why"), "K": rec.get("K"), "stopped": rec.get("stopped"),
                "seconds_total": rec.get("seconds_total"),
                "seconds_generation": cost.get("seconds_generation"),
                "seconds_per_roi_per_draw": cost.get("seconds_per_roi_per_draw"),
                "peak_bytes_per_roi": cost.get("peak_bytes_per_roi"),
                "not_estimable_rois": rec.get("not_estimable_rois"),
                **{f"movement_{k}": v for k, v in mv.items()}})
            for scope, rows in ((rec.get("result") or {}).get("scopes") or {}).items():
                for stat, r in rows.items():
                    stat_rows.append({"stream": stream, "cell_id": c.get("id"),
                                      "name": c.get("name"), "kind": c.get("kind"),
                                      "scope": scope, "stat": stat, **r})
                    targets = ss.CONTROL_TARGETS.get(c.get("name"), ())
                    if any(stat == t or stat.startswith(t + "@") for t in targets):
                        power_rows.append({
                            "stream": stream, "control": c.get("name"),
                            "cell_id": c.get("id"), "scope": scope, "stat": stat,
                            "paired_p": r.get("paired_p"),
                            "moved_paired": (r.get("paired_p") is not None
                                             and r["paired_p"] < ss.ALPHA),
                            "band_flag": r.get("band_flag"), "delta": r.get("delta")})
            for part, byk in (rec.get("destruction") or {}).items():
                for K, r in byk.items():
                    dest_rows.append({"stream": stream, "cell_id": c.get("id"),
                                      "name": c.get("name"),
                                      "freeze_half": c.get("freeze_half"),
                                      "participation": part, "K": K, **r})
                    if c.get("name") == "do_nothing":
                        # Two different reasons the measure cannot run at a K, and
                        # they are kept apart: the plant never showed (too few
                        # participants for this K), or it showed and do-nothing
                        # failed to keep it — the plan's "the measure is broken".
                        ret = r.get("retained")
                        if not r.get("planted_visible"):
                            why = ("not run: the planted events carry no excess at "
                                   "this K, so there is nothing for do-nothing to keep")
                        elif ret is None or abs(ret - 1.0) > 0.05:
                            why = (f"not run: do-nothing lost the planted excess "
                                   f"(retained {ret})")
                        else:
                            why = "ok"
                        destruction_status.setdefault(stream, {})[f"p{part}_K{K}"] = why
        yp = out / stream / "yardsticks.json"
        if yp.exists():
            y = json.loads(yp.read_text(encoding="utf-8"))
            neg = y.get("negative_synthetic", {}).get("scopes", {}) or {}
            for scope, bd in (y.get("bands") or {}).items():
                for stat, b in bd.items():
                    ho = (y.get("negative_heldout", {}).get(scope) or {}).get(stat) or {}
                    sy = (neg.get(scope) or {}).get(stat) or {}
                    yard_rows.append({
                        "stream": stream, "scope": scope, "stat": stat,
                        "band_q025": b.get("q025"), "band_q975": b.get("q975"),
                        "band_abs_q95": b.get("abs_q95"), "n_splits": b.get("n"),
                        "neg_heldout_band": ho.get("band"),
                        "neg_heldout_paired": ho.get("paired"),
                        "neg_synthetic_band": sy.get("band"),
                        "neg_synthetic_paired": sy.get("paired")})
    for name, rows in (("cells.csv", cells_rows), ("stats.csv", stat_rows),
                       ("destruction.csv", dest_rows), ("yardsticks.csv", yard_rows),
                       ("control_power.csv", power_rows)):
        _write_csv(out / name, rows)
    return {"status_counts": status_counts, "destruction_status": destruction_status,
            "n_cells": len(cells_rows)}


# `newline=""` AND an explicit `\n`, the way emit.py and windows.py write theirs: csv's
# default terminator is `\r\n`, so the same table written on Windows and on macOS differs
# byte for byte — and both machines wrote into this run folder on 2026-09-11.
def _write_csv(path: Path, rows: list[dict]) -> None:
    keys = []
    for r in rows:
        for k in r:
            if k not in keys:
                keys.append(k)
    with open(path, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=keys or ["empty"], lineterminator="\n")
        w.writeheader()
        for r in rows:
            w.writerow({k: ("" if r.get(k) is None else r.get(k)) for k in keys})


# ---- main -------------------------------------------------------------------

def _default_out(role: str) -> Path:
    from bugarach.paths import darkroom
    return darkroom() / OUT_DIRNAME / role


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    src = p.add_mutually_exclusive_group(required=True)
    src.add_argument("--role", help="export role from current_export.toml "
                     "(steps_excluded, senktide, cossart)")
    _dataset_arg.add(src, want="export_folder", aliases=("--folder",), required=False)
    p.add_argument("--label", default=None,
                   help="name for the output folder when --dataset is used "
                        "(default: the folder's name)")
    p.add_argument("--out", default=None,
                   help=f"output folder (default darkroom()/{OUT_DIRNAME}/<role>/)")
    p.add_argument("--streams", nargs="*", default=None,
                   help="streams to run (default: every stream the folder carries)")
    p.add_argument("--only", nargs="*", default=None,
                   help="run only these generators (names from surrogates)")
    p.add_argument("--J-sec", nargs="*", type=float, default=None,
                   help="J values in seconds, overriding the per-stream default")
    p.add_argument("--J-frames", nargs="*", type=float, default=None,
                   help="J values in frames, overriding the per-stream default")
    p.add_argument("--f-frames", nargs="*", type=int, default=None,
                   help="provisional dead times f in whole frames (default: 0.5, "
                        "0.75, 1.0 x the observed floor; Cossart 1 and 2)")
    p.add_argument("--no-shipped-extra", action="store_true",
                   help="skip the shipped dither's production 20 s cell")
    p.add_argument("--K", type=int, default=99, help="surrogate draws per cell (99)")
    p.add_argument("--min-K", type=int, default=19,
                   help="fewest draws a cell may report (19); below it, intractable")
    p.add_argument("--splits", type=int, default=100, help="mouse-grouped splits (100)")
    p.add_argument("--alpha", type=float, default=ss.ALPHA)
    p.add_argument("--neg-reps", type=int, default=20,
                   help="replicates of the fresh-synthetic negative (20)")
    p.add_argument("--neg-draws", type=int, default=19,
                   help="fresh draws per negative replicate (19)")
    p.add_argument("--destruction-draws", type=int, default=19)
    p.add_argument("--destruction-assess-surrogates", type=int, default=200,
                   help="circular-shift surrogates inside each coactivity score (200)")
    p.add_argument("--no-destruction", action="store_true")
    p.add_argument("--cell-seconds", type=float, default=300.0,
                   help="generation budget per cell; draws stop once spent (300)")
    p.add_argument("--cell-hard-seconds", type=float, default=None,
                   help="kill a cell after this long (default 4 x --cell-seconds)")
    p.add_argument("--cell-mem-gb", type=float, default=4.0,
                   help="kill a cell whose resident memory passes this (4)")
    p.add_argument("--total-mem-gb", type=float,
                   default=round(0.6 * _machine_ram_bytes() / 1e9, 1),
                   help="start no new cell while the workers together hold more "
                        "than this (default 60%% of this machine's RAM)")
    p.add_argument("--jobs", type=int, default=max(1, (os.cpu_count() or 2) - 2),
                   help="parallel cell processes; 0 runs in-process with no caps")
    p.add_argument("--limit", type=int, default=None,
                   help="use only the first N recordings (smoke runs)")
    p.add_argument("--force", action="store_true", help="redo finished cells")
    p.add_argument("--baseline-labels", nargs="*", default=None)
    args = p.parse_args(argv)

    from bugarach import dataset
    from bugarach.io import load_folder

    if args.role:
        folder = dataset.current(args.role)
        role = args.role
    else:
        folder = _dataset_arg.get(args, want="export_folder")
        role = args.label or Path(folder).name
    out = Path(args.out) if args.out else _default_out(role)
    out.mkdir(parents=True, exist_ok=True)
    print(f"surrogate screen: {role} -> {out}")

    slices = load_folder(folder)
    if args.limit:
        slices = slices[: args.limit]
    names = sorted({n for s in slices for n in s.streams})
    streams = args.streams or names
    is_cossart = role == "cossart"
    hard = args.cell_hard_seconds or 4.0 * args.cell_seconds
    settings = {"K": args.K, "min_K": args.min_K, "cell_seconds": args.cell_seconds,
                "alpha": args.alpha, "neg_reps": args.neg_reps,
                "neg_draws": args.neg_draws,
                "destruction_draws": args.destruction_draws,
                "destruction_assess_surrogates": args.destruction_assess_surrogates,
                "skip_destruction": args.no_destruction}
    meta = {"role": role, "folder": str(folder), "streams": {}, "settings": settings,
            "cell_hard_seconds": hard, "cell_mem_gb": args.cell_mem_gb,
            "jobs": args.jobs, "started": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
            "holm_family": "per grid cell, separately for each yardstick's P "
                           "(every statistic in every scope)",
            "n_recordings_loaded": len(slices)}
    work = Path(tempfile.mkdtemp(prefix="surrogate-screen-"))
    tasks = []
    try:
        for stream in streams:
            recs, skipped = ss.recordings_from_slices(
                slices, stream, baseline_labels=tuple(args.baseline_labels)
                if args.baseline_labels else None)
            floor = ss.observed_floor(recs)
            if args.J_frames:
                J_values, J_unit = tuple(args.J_frames), "frames"
            elif args.J_sec:
                J_values, J_unit = tuple(args.J_sec), "sec"
            elif is_cossart:
                J_values, J_unit = J_FRAMES_COSSART, "frames"
            elif stream in J_SEC:
                J_values, J_unit = J_SEC[stream], "sec"
            else:
                print(f"error: no default J for stream {stream!r}; pass --J-sec or "
                      f"--J-frames", file=sys.stderr)
                return 2
            if args.f_frames:
                f_frames = tuple(int(x) for x in args.f_frames)
                f_labels = tuple(f"{x}fr" for x in f_frames)
            elif is_cossart:
                f_frames = F_FRAMES_COSSART
                f_labels = tuple(f"{x}fr" for x in f_frames)
            else:
                if not floor:
                    print(f"error: stream {stream!r} has no within-ROI interval to "
                          f"take a floor from; pass --f-frames", file=sys.stderr)
                    return 2
                f_frames = tuple(max(1, _round_half_up(m * floor)) for m in F_MULTS)
                f_labels = tuple(f"{m:g}x" for m in F_MULTS)
            prep = prepare_stream(recs, role=role, stream=stream, J_values=J_values,
                                  J_unit=J_unit, f_frames=f_frames, f_labels=f_labels,
                                  n_splits=args.splits, alpha=args.alpha,
                                  no_destruction=args.no_destruction)
            cells = build_grid(J_values=J_values, J_unit=J_unit, f_frames=prep["fs"],
                               only=set(args.only) if args.only else None,
                               shipped_extra=not args.no_shipped_extra and not is_cossart)
            ctx = {"role": role, "stream": stream, "recs": recs, "fs": prep["fs"],
                   "scopes": prep["scopes"], "split_info": prep["split_info"],
                   "twins": prep["twins"], "settings": settings,
                   "f_synthetic": int(max(f_frames))}
            ctx_path = work / f"{stream}.pkl"
            with open(ctx_path, "wb") as fh:
                pickle.dump(ctx, fh)
            sdir = out / stream
            (sdir / "cells").mkdir(parents=True, exist_ok=True)
            n_groups = {g: len(ids) for g, ids in prep["scopes"].items()}
            meta["streams"][stream] = {
                "n_recordings": len(recs), "skipped": skipped,
                "n_mice": prep["n_mice"], "recordings_per_scope": n_groups,
                "groups": prep["groups"], "observed_floor_frames": floor,
                "f_frames": prep["fs"], "J_values": list(J_values), "J_unit": J_unit,
                "n_cells": len(cells),
                "window_sources": sorted({r.window_source for r in recs}),
                "dt_values": sorted({r.dt for r in recs}),
                "destruction_twins": (prep["twins"] or {}).get("describe")}
            yard = {"stream": stream, "bands": prep["bands"],
                    "negative_heldout": prep["heldout"], "alpha": args.alpha,
                    "n_splits": args.splits}
            _write_json(sdir / "yardsticks.json", yard)
            neg_path = sdir / "negative_synthetic.json"
            if args.force or not neg_path.exists():
                tasks.append(("negatives", (str(ctx_path), str(neg_path)),
                              str(neg_path), f"{stream} synthetic negative"))
            for c in cells:
                op = sdir / "cells" / f"{c['id']}.json"
                if op.exists() and not args.force:
                    continue
                tasks.append(("cell", (c, str(ctx_path), str(op)), str(op),
                              f"{stream} {c['id']}"))
        _write_json(out / "meta.json", meta)
        print(f"{len(tasks)} task(s) to run with jobs={args.jobs}")
        schedule(tasks, jobs=args.jobs, hard_seconds=hard,
                 mem_bytes=args.cell_mem_gb * 1e9,
                 total_mem_bytes=args.total_mem_gb * 1e9)
        # Fold the synthetic negative into each stream's yardsticks file.
        for stream in streams:
            sdir = out / stream
            yp, npth = sdir / "yardsticks.json", sdir / "negative_synthetic.json"
            if yp.exists() and npth.exists():
                y = json.loads(yp.read_text(encoding="utf-8"))
                y["negative_synthetic"] = json.loads(npth.read_text(encoding="utf-8"))
                _write_json(yp, y)
        summary = write_tables(out, streams)
        meta["finished"] = time.strftime("%Y-%m-%dT%H:%M:%S%z")
        meta["summary"] = summary
        _write_json(out / "meta.json", meta)
        _write_json(out / "summary.json", summary)
        print(json.dumps(_clean(summary), indent=1))
    finally:
        shutil.rmtree(work, ignore_errors=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
