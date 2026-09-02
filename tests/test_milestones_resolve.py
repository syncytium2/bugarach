"""`docs/MILESTONES.md` must resolve against the tree it describes.

Wired here rather than left as a `tools/` script, because the first draft of that script
claimed in `MILESTONES.md`'s own prose that a test enforced it — and no test did. A
document asserting a gate it does not have is the exact defect the milestone index exists
to catch, so the gate runs with `pytest` or the claim comes out of the document.

Pattern follows `tests/test_sapper.py`: subprocess the tool, assert the return code, so
the CLI a person types and the check CI runs are the same code path.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
TOOL = REPO / "tools" / "check_milestones.py"
DOC = REPO / "docs" / "MILESTONES.md"


def run(*args):
    return subprocess.run([sys.executable, str(TOOL), *args],
                          cwd=REPO, capture_output=True, text=True)


def test_the_tool_exists():
    """`MILESTONES.md` names this path in its own 'how to add to it' section."""
    assert TOOL.exists(), f"{TOOL} is named by docs/MILESTONES.md and must exist"


def test_every_rule_can_still_fire():
    """The rule that matters most shipped BACKWARDS in the first draft — it failed
    'K was never decided' and passed 'was never an open question', the exact sentence
    the real decay used. A rule that cannot fail is not a check, so each one proves
    itself here, in both directions where it has two."""
    r = run("--selftest")
    assert r.returncode == 0, f"selftest failed:\n{r.stdout}\n{r.stderr}"
    assert "0 failures" in r.stdout


def test_the_milestones_document_resolves():
    r = run(str(DOC))
    assert r.returncode == 0, f"docs/MILESTONES.md has unresolved rows:\n{r.stdout}"


def test_a_broken_row_is_caught(tmp_path):
    """The negative control for the document itself: a fabricated commit and a
    fabricated path must both be reported, or a clean run means nothing."""
    broken = tmp_path / "broken.md"
    broken.write_text(DOC.read_text() +
                      "\n| bogus | fabricated | measured | `0000000` | `docs/nope.md` | current |\n")
    r = run(str(broken))
    assert r.returncode == 1
    assert "no such commit" in r.stdout and "does not exist" in r.stdout


@pytest.mark.parametrize("legend", ["built", "measured", "decided", "evidence"])
def test_the_strength_legend_is_the_one_the_checker_enforces(legend):
    """The document declares four strengths and the checker validates against four.
    The first draft declared four and enforced none, so a fifth value (`done`) shipped
    in the row that was supposed to demonstrate the vocabulary."""
    from importlib.util import module_from_spec, spec_from_file_location
    spec = spec_from_file_location("check_milestones", TOOL)
    mod = module_from_spec(spec)
    spec.loader.exec_module(mod)
    assert legend in mod.STRENGTHS
    assert f"`{legend}`" in DOC.read_text(), f"{legend} is enforced but not documented"
