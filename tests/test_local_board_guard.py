"""The machine-local board guard proves it can fire, in CI, like the branch guard.

"Claim your work on the board" was in the session briefing, and a session read it
at startup, worked for hours, wrote to the shared darkroom and never created the
board — with several other sessions live on the same machine. So it is a gate now.

The properties worth pinning: a missing board blocks, a board with no block for
this worktree blocks, either of the two names this worktree answers to releases
it, the override works, and an indeterminate state is a refusal rather than a
silent pass.
"""

import shutil
import subprocess
from pathlib import Path

import pytest

REPO = Path(__file__).parent.parent
GUARD = REPO / "tools" / "guard_local_board.sh"
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


def test_missing_board_blocks(tmp_path):
    r = run("--board", str(tmp_path / "absent.md"), "--name", "some-worktree")
    assert r.returncode == 1
    assert "does not exist" in r.stderr


def test_board_without_this_worktree_blocks(tmp_path):
    b = tmp_path / "SESSIONS.md"
    b.write_text("# board\n\n### Mac/someone-else — their task\n", encoding="utf-8")
    r = run("--board", str(b), "--name", "my-worktree")
    assert r.returncode == 1
    assert "no block" in r.stderr


def test_a_claim_releases_the_gate(tmp_path):
    b = tmp_path / "SESSIONS.md"
    b.write_text("# board\n\n### Mac/my-worktree — my task\n", encoding="utf-8")
    assert run("--board", str(b), "--name", "my-worktree").returncode == 0


def test_the_block_message_hands_over_the_fix(tmp_path):
    """A gate that only says no gets overridden; one that hands you the stanza
    gets obeyed. Pin that the refusal names the board and offers the escape."""
    r = run("--board", str(tmp_path / "absent.md"), "--name", "my-worktree")
    assert "absent.md" in r.stderr
    assert "**Status:** ACTIVE" in r.stderr
    assert "ALLOW_UNCLAIMED_BOARD=1" in r.stderr


def test_override_releases_it(tmp_path):
    import os
    env = dict(os.environ, ALLOW_UNCLAIMED_BOARD="1")
    r = run("--board", str(tmp_path / "absent.md"), "--name", "w", env=env)
    assert r.returncode == 0


def test_hook_invokes_the_guard():
    """A guard nothing calls is decoration — pin the wiring, not just the logic."""
    assert "guard_local_board.sh" in HOOK.read_text(encoding="utf-8")


def test_guard_and_hook_agree_on_the_board_path():
    """The guard resolves the board the same way the vendored session-start hook
    does. If either drifts, a session claims one file while the gate reads
    another — which is worse than no gate, because it looks obeyed."""
    r = run("--path")
    assert r.returncode == 0
    resolved = r.stdout.strip()
    assert resolved.endswith("-worktrees/SESSIONS.md"), resolved
    hook = (REPO / ".claude" / "hooks" / "session-start.sh").read_text(encoding="utf-8")
    assert 'board="${wt_dir}/SESSIONS.md"' in hook
    assert 'wt_dir="$(dirname "$base")/${repo}-worktrees"' in hook
