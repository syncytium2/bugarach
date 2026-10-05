"""The run-status mirror's own selftest, plus the one property no selftest of its
own can check: that it runs without the package's dependencies.

That second test is the point of the tool. `tools/mirror_run_status.py` exists so an
unattended run's status is readable from a machine other than the one it runs on, and
it is meant to be driven by a scheduled task at three in the morning. If it needs the
virtual environment, it fails in exactly the conditions it was written for — so this
runs it with `sys.path` stripped of anything that would let `import bugarach` succeed,
and requires it to work anyway.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).parent.parent
TOOL = REPO / "tools" / "mirror_run_status.py"


def test_selftest_passes():
    r = subprocess.run([sys.executable, str(TOOL), "--selftest"],
                       capture_output=True, text=True, cwd=REPO)
    assert r.returncode == 0, r.stdout + r.stderr


def test_runs_without_the_package_importable(tmp_path):
    """No venv, no scipy, no `bugarach` package — the mirror still resolves the
    darkroom and writes. `paths.py` is pure stdlib; the package's `__init__`
    imports the store, which is why this tool loads that module by path."""
    run, dark = tmp_path / "run", tmp_path / "darkroom" / "bugarach"
    run.mkdir(parents=True)
    dark.mkdir(parents=True)
    (run / "progress.json").write_text('{"stage": "rounds done"}')

    env = dict(os.environ, BUGARACH_DARKROOM=str(dark))
    # Strip the repo's src/ from anything inherited, so `import bugarach` cannot work.
    env.pop("PYTHONPATH", None)

    r = subprocess.run(
        [sys.executable, "-S", str(TOOL), str(run), "--into", "a-run"],
        capture_output=True, text=True, cwd=tmp_path, env=env,
    )
    assert r.returncode == 0, r.stdout + r.stderr

    out = dark / "a-run"
    assert json.loads((out / "progress.json").read_text())["stage"] == "rounds done"
    assert (out / "STATUS.txt").exists()
    assert json.loads((out / "mirror.json").read_text())["source_present"] is True


def test_refuses_to_write_outside_the_darkroom(tmp_path):
    """bugarach owns `<darkroom>/bugarach/` and nothing above it. Five stray
    folders reached the darkroom root on 2026-09-17 through a different tool."""
    run, dark = tmp_path / "run", tmp_path / "darkroom" / "bugarach"
    run.mkdir(parents=True)
    dark.mkdir(parents=True)
    (run / "progress.json").write_text("{}")
    env = dict(os.environ, BUGARACH_DARKROOM=str(dark))

    for bad in ("../escape", str(tmp_path / "elsewhere")):
        r = subprocess.run(
            [sys.executable, str(TOOL), str(run), "--into", bad],
            capture_output=True, text=True, cwd=REPO, env=env,
        )
        assert r.returncode != 0, f"{bad!r} was not refused: {r.stdout}"
        assert not (tmp_path / "elsewhere").exists()
