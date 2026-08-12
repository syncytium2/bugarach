"""The branch guard proves it can fire, in CI, like sapper and the merge gate.

"Never commit on main" was prose in two documents and was obeyed only when
someone remembered. `tools/guard_branch.sh` refuses the commit instead, from
`.githooks/pre-commit`.

The properties worth pinning: it blocks the protected branches, it does NOT block
a branch that merely starts with "main", the override works, and an
indeterminate state (detached HEAD) is a refusal rather than a silent pass.
"""

import shutil
import subprocess
from pathlib import Path

import pytest

REPO = Path(__file__).parent.parent
GUARD = REPO / "tools" / "guard_branch.sh"
HOOK = REPO / ".githooks" / "pre-commit"

pytestmark = pytest.mark.skipif(
    shutil.which("bash") is None, reason="bash unavailable (guard is a shell script)"
)


def run(*args, env=None):
    return subprocess.run(["bash", str(GUARD), *args],
                          capture_output=True, text=True, cwd=REPO, env=env)


def test_decision_logic_can_fire_in_every_direction():
    r = run("--selftest")
    assert r.returncode == 0, r.stdout + r.stderr
    assert "all checks pass" in r.stdout


def test_syntax_is_valid():
    r = subprocess.run(["bash", "-n", str(GUARD)], capture_output=True, text=True)
    assert r.returncode == 0, r.stderr


@pytest.mark.parametrize("branch", ["main", "master"])
def test_protected_branches_are_blocked(branch):
    assert run("--branch", branch).returncode == 1


@pytest.mark.parametrize("branch", ["fix-thing", "main-menu", "wip/port"])
def test_other_branches_pass(branch):
    assert run("--branch", branch).returncode == 0


def test_hook_invokes_the_guard():
    """A guard nothing calls is decoration — pin the wiring, not just the logic."""
    assert "guard_branch.sh" in HOOK.read_text(encoding="utf-8")
