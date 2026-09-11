"""`tools/build_surrogate_screen.py` on a synthetic export folder.

Pins the grid (every cell's parameters bind to its generator), the output
contract (JSON per cell and the CSV tables, to the darkroom by default), the
do-nothing control reading as it must, resumption, and intractable cells being
recorded rather than stopping the run. Synthetic data only.
"""

from __future__ import annotations

import csv
import importlib.util
import inspect
import json
import os
import subprocess
import sys
from pathlib import Path

import numpy as np
import pytest

from bugarach import surrogates
from bugarach.simulate import simulate_coordination

TOOL = Path(__file__).resolve().parents[1] / "tools" / "build_surrogate_screen.py"


@pytest.fixture(scope="module")
def bss():
    spec = importlib.util.spec_from_file_location("_bss", TOOL)
    m = importlib.util.module_from_spec(spec)
    sys.modules["_bss"] = m
    spec.loader.exec_module(m)
    return m


def _folder(root: Path, n_mice=6, per_mouse=2) -> Path:
    """An export folder with mice, groups and a baseline region per recording."""
    root.mkdir(parents=True, exist_ok=True)
    slices = ["slice_id,frame_interval_sec,subject_id,group_id"]
    regions = ["slice_id,region_idx,label,start_sec,end_sec"]
    i = 0
    for m in range(n_mice):
        for _ in range(per_mouse):
            s, _ = simulate_coordination(
                duration_sec=900.0, n_roi=10, bg_floor_sec=0.4,
                bg_roi_counts=np.random.RandomState(i).poisson(12, size=10),
                participation=(0.5,), n_per_level=(6,), jitter_sec=0.1,
                grid_sec=0.1, seed=100 + i)
            rows = ["roi,time_sec"]
            for r, v in enumerate(s.streams["events"].locs):
                if not len(v):
                    rows.append(f"{r + 1},NA")
                for t in v:
                    rows.append(f"{r + 1},{t:.1f}")
            (root / f"rec_{i + 1}.csv").write_text("\n".join(rows) + "\n",
                                                   encoding="utf-8")
            slices.append(f"rec_{i + 1},0.1,mouse{m},{'G1' if m % 2 else 'G2'}")
            regions.append(f"rec_{i + 1},1,baseline,0,900")
            i += 1
    (root / "slices.csv").write_text("\n".join(slices) + "\n", encoding="utf-8")
    (root / "regions.csv").write_text("\n".join(regions) + "\n", encoding="utf-8")
    return root


def test_every_cell_binds_to_its_generator(bss):
    """The grid's parameters are exactly what each generator takes — an unknown
    or missing parameter is a TypeError in the adapter, and here, not overnight."""
    fs = {"0.5x": 2, "0.75x": 3, "1x": 4}
    cells = bss.build_grid(J_values=bss.J_SEC["fast"], J_unit="sec", f_frames=fs)
    ids = [c["id"] for c in cells]
    assert len(ids) == len(set(ids))
    names = {c["name"] for c in cells}
    assert names == set(surrogates.CANDIDATES) | set(surrogates.CONTROLS)
    for c in cells:
        fn = surrogates.CANDIDATES.get(c["name"]) or surrogates.CONTROLS[c["name"]]
        inspect.signature(fn).bind([np.zeros(0, np.int64)], (0, 10), ("k",),
                                   **bss.params_for(c, 0.1))
    # 4 without J + freeze-half + per-window shift + 5x6 J-only + the shipped
    # dither's 20 s + 2x6 edge + 3x6x3 J-and-f + 6x3 operational-time + 2x6x3x2x2
    assert len(cells) == 4 + 1 + 1 + 30 + 1 + 12 + 54 + 18 + 144


def test_seconds_convert_with_each_recordings_own_interval(bss):
    c = {"name": "uniform_dither", "J": 0.4, "J_unit": "sec"}
    assert bss.params_for(c, 0.1) == {"J": 4.0}
    assert bss.params_for(c, 0.2) == {"J": 2.0}
    c = {"name": "operational_time", "J": 2, "J_unit": "frames", "bandwidth_min": 2}
    assert bss.params_for(c, 0.1) == {"J": 2.0, "bandwidth": 1200.0}


def test_the_default_output_is_the_darkroom(bss, tmp_path, monkeypatch):
    monkeypatch.setenv("BUGARACH_DARKROOM", str(tmp_path))
    assert bss._default_out("cossart") == tmp_path / bss.OUT_DIRNAME / "cossart"


@pytest.fixture(scope="module")
def run(bss, tmp_path_factory):
    root = tmp_path_factory.mktemp("screen")
    folder = _folder(root / "export")
    out = root / "out"
    rc = bss.main(["--dataset", str(folder), "--out", str(out), "--jobs", "0",
                   "--J-frames", "2", "--only", "do_nothing", "circular_shift",
                   "shipped_dither", "window_circular_shift",
                   "--K", "5", "--min-K", "3", "--splits", "12", "--neg-reps", "2",
                   "--neg-draws", "4", "--destruction-draws", "3",
                   "--destruction-assess-surrogates", "30"])
    assert rc == 0
    return folder, out


def _rows(path):
    with open(path, newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def test_it_writes_the_machine_readable_results(run):
    _, out = run
    for name in ("meta.json", "summary.json", "cells.csv", "stats.csv",
                 "destruction.csv", "yardsticks.csv", "control_power.csv"):
        assert (out / name).exists(), name
    meta = json.loads((out / "meta.json").read_text())
    st = meta["streams"]["events"]
    assert st["observed_floor_frames"] >= 4
    assert st["f_frames"] == {"0.5x": 2, "0.75x": 3, "1x": 4} or \
        list(st["f_frames"].values())[-1] == st["observed_floor_frames"]
    assert set(st["recordings_per_scope"]) == {"all", "G1", "G2"}
    cells = _rows(out / "cells.csv")
    assert {c["status"] for c in cells} == {"ok"}, [c["why"] for c in cells]
    y = json.loads((out / "events" / "yardsticks.json").read_text())
    assert y["negative_synthetic"]["status"] == "ok"
    assert set(y["bands"]) == {"all", "G1", "G2"}


def test_do_nothing_reads_as_it_must(run):
    _, out = run
    rec = json.loads((out / "events" / "cells" / "do_nothing.json").read_text())
    assert rec["result"]["movement"]["share_moved"] == 0.0
    for scope in rec["result"]["scopes"].values():
        for nm, row in scope.items():
            assert row["paired_p"] in (1.0, None), nm
    d = rec["destruction"]
    assert d["0.5"]["3"]["planted_visible"]
    assert d["0.5"]["3"]["retained"] == pytest.approx(1.0)
    summ = json.loads((out / "summary.json").read_text())
    assert summ["destruction_status"]["events"]["p0.5_K3"] == "ok"


def test_destruction_rows_carry_the_controls(run):
    _, out = run
    rows = _rows(out / "destruction.csv")
    by = {(r["cell_id"], r["participation"], r["K"]): r for r in rows}
    circ = float(by[("circular_shift", "0.5", "3")]["retained"])
    assert circ < 0.5
    assert ("freeze_half", "0.5", "3") in by


def test_control_power_rows_name_each_controls_statistic(run):
    _, out = run
    rows = _rows(out / "control_power.csv")
    assert {r["control"] for r in rows} >= {"window_circular_shift"}
    assert all(r["stat"].startswith("subfloor") for r in rows
               if r["control"] == "window_circular_shift")


def test_a_rerun_resumes_rather_than_redoing(bss, run, capsys):
    folder, out = run
    before = (out / "events" / "cells" / "do_nothing.json").stat().st_mtime
    rc = bss.main(["--dataset", str(folder), "--out", str(out), "--jobs", "0",
                   "--J-frames", "2", "--only", "do_nothing", "--K", "5",
                   "--min-K", "3", "--splits", "12", "--no-destruction"])
    assert rc == 0
    assert "0 task(s)" in capsys.readouterr().out
    assert (out / "events" / "cells" / "do_nothing.json").stat().st_mtime == before


def test_a_cell_short_of_min_K_is_recorded_intractable(bss, tmp_path):
    folder = _folder(tmp_path / "export", n_mice=2, per_mouse=1)
    out = tmp_path / "out"
    rc = bss.main(["--dataset", str(folder), "--out", str(out), "--jobs", "0",
                   "--J-frames", "2", "--only", "circular_shift", "--K", "50",
                   "--min-K", "40", "--cell-seconds", "0", "--splits", "4",
                   "--neg-reps", "1", "--neg-draws", "2", "--no-destruction"])
    assert rc == 0
    rec = json.loads((out / "events" / "cells" / "circular_shift.json").read_text())
    assert rec["status"] == "intractable" and "budget" in rec["why"]


# THE MEMORY CAPS HAD NEVER BEEN SHOWN TO FIRE, and on Windows they could not: the meter
# read 0 for every process, so a cell could grow without limit and the all-workers cap
# never held a task back. A meter that reads zero looks exactly like a machine with
# room to spare. These pin the meter to a live process and the kill to a real worker.

def test_the_memory_meter_reads_a_live_process(bss):
    before = bss._rss_bytes(os.getpid())
    assert before > 0, "the meter reads 0 for a live process: both memory caps are off"
    blob = bytearray(200_000_000)
    after = bss._rss_bytes(os.getpid())
    del blob
    assert after - before > 100_000_000


def test_machine_ram_is_measured_not_the_fallback(bss):
    assert bss._machine_ram_bytes() != 16e9


@pytest.mark.parametrize("cap, value, why", [
    ("--cell-mem-gb", "0.001", "resident"),
    ("--cell-hard-seconds", "0.5", "killed after"),
])
def test_a_worker_past_its_cap_is_killed_and_recorded(tmp_path, cap, value, why):
    """Through the real process pool, run as a script: spawned workers import the
    tool as ``__mp_main__``, which a module loaded under a private name cannot give
    them."""
    folder = _folder(tmp_path / "export", n_mice=2, per_mouse=1)
    out = tmp_path / "out"
    r = subprocess.run(
        [sys.executable, str(TOOL), "--dataset", str(folder), "--out", str(out),
         "--jobs", "1", "--J-frames", "2", "--only", "circular_shift", "--K", "5",
         "--min-K", "3", "--splits", "4", "--neg-reps", "1", "--neg-draws", "2",
         "--no-destruction", cap, value],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
        timeout=600)   # a Windows child prints in cp1252; the dashes must not kill the reader
    assert r.returncode == 0, r.stderr[-2000:]
    rec = json.loads((out / "events" / "cells" / "circular_shift.json").read_text())
    assert rec["status"] == "intractable", rec
    assert why in rec["why"], rec["why"]


# Dropbox holds a file while it syncs it, and Windows then refuses to replace it. Two
# cells of the 2026-09-11 run died of exactly that, mid-draw, on a progress file.

def test_a_refused_swap_is_retried(bss, tmp_path, monkeypatch):
    real, calls = os.replace, {"n": 0}

    def refuses_twice(src, dst):
        calls["n"] += 1
        if calls["n"] <= 2:
            raise PermissionError(13, "Access is denied")
        real(src, dst)
    monkeypatch.setattr(bss.os, "replace", refuses_twice)
    monkeypatch.setattr(bss.time, "sleep", lambda s: None)
    bss._write_json(tmp_path / "cell.json.progress", {"draws_completed": 3})
    assert json.loads((tmp_path / "cell.json.progress").read_text()) == {"draws_completed": 3}
    assert calls["n"] == 3


def test_a_swap_refused_every_time_still_fails(bss, tmp_path, monkeypatch):
    def always_refuses(src, dst):
        raise PermissionError(13, "Access is denied")
    monkeypatch.setattr(bss.os, "replace", always_refuses)
    monkeypatch.setattr(bss.time, "sleep", lambda s: None)
    with pytest.raises(PermissionError):
        bss._write_json(tmp_path / "cell.json", {"status": "ok"})
