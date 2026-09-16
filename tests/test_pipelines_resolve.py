"""`docs/pipelines.md` and `docs/pipelines/` must agree, in both directions.

Wired here rather than left as a `tools/` script for the reason `test_milestones_resolve.py`
records: a document that asserts a gate it does not have is the defect the index exists to
catch. `pipelines.md` tells a session it is the first place to look, and that claim is worth
something only while the page is true — so the gate runs with `pytest` or the claim comes out
of the document.

Pattern follows `tests/test_sapper.py` and `tests/test_milestones_resolve.py`: subprocess the
tool, assert the return code, so the CLI a person types and the check CI runs are one code path.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
TOOL = REPO / "tools" / "check_pipelines.py"
INDEX = REPO / "docs" / "pipelines.md"
PIPELINE_DIR = REPO / "docs" / "pipelines"


def run(*args):
    return subprocess.run([sys.executable, str(TOOL), *args],
                          cwd=REPO, capture_output=True, text=True)


def test_the_tool_exists():
    """`pipelines.md` names this path in its own 'this index is checked' section."""
    assert TOOL.is_file(), f"{TOOL} is missing, and pipelines.md claims it runs"


def test_the_index_exists():
    assert INDEX.is_file(), "docs/pipelines.md is the page sessions are told to read first"


def test_every_rule_can_still_fire():
    """A rule that cannot fail is not a check — and this repo has shipped four of those."""
    r = run("--selftest")
    assert r.returncode == 0, f"selftest failed:\n{r.stdout}\n{r.stderr}"


def test_the_index_and_the_directory_agree():
    """Every row resolves, and every pipeline on disk is listed."""
    r = run()
    assert r.returncode == 0, (
        f"docs/pipelines.md and docs/pipelines/ disagree:\n{r.stdout}\n{r.stderr}")


def test_the_index_is_not_empty():
    """An index listing nothing passes every other rule vacuously."""
    assert PIPELINE_DIR.is_dir(), "docs/pipelines/ is missing"
    assert list(PIPELINE_DIR.glob("*.md")), "docs/pipelines/ holds no routes"
