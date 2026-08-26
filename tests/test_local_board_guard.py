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


# ---------------------------------------------------------------------------------
# A MENTION IS NOT A CLAIM.
#
# Until 2026-08-26 the gate grepped the whole board for a bare substring, so the
# primary checkout — directory basename `bugarach`, which appears in every path
# written on a 3,000-line board — could never be refused:
#
#     $ grep -cF -- bugarach ../bugarach-worktrees/SESSIONS.md
#     267
#     $ bash tools/guard_local_board.sh ; echo $?      # from an unclaimed checkout
#     0
#
# CLAUDE.md calls claiming "a precondition for working, not a courtesy" and says the
# gate is mechanized. It was mechanized everywhere except the checkout most likely to
# be shared. Every case below returned 0 under the old rule.
# ---------------------------------------------------------------------------------

REALISTIC_BOARD = """# Machine-local session board for bugarach

### Mac/known-branch — a task
- **Worktree:** `bugarach-worktrees/known-branch`
- **Touches:** `tools/guard_local_board.sh`, and docs under bugarach

### Mac/known-branch-extended — a different task
- **Status:** ACTIVE

### Mac/branch-merger — fix all the branches
- **Worktrees touched:** `generator-revision-input`, `parameter-spec-v2`
- **Status:** DONE
"""


def _board(tmp_path):
    b = tmp_path / "SESSIONS.md"
    b.write_text(REALISTIC_BOARD, encoding="utf-8")
    return str(b)


def test_the_repo_name_in_every_path_is_not_a_claim(tmp_path):
    """The one that mattered. The primary checkout is named after the repo, and the
    repo name is in every worktree path anyone writes down."""
    assert run("--board", _board(tmp_path), "--name", "bugarach").returncode == 1


def test_being_named_in_someone_elses_block_is_not_a_claim(tmp_path):
    """Both worktrees this caught on the live board were 'claimed' this way: a
    session that finished six days earlier had listed them under its own
    'Worktrees touched' line. Somebody else's record of having been there is not
    this session's claim to be there now."""
    for name in ("generator-revision-input", "parameter-spec-v2"):
        assert run("--board", _board(tmp_path), "--name", name).returncode == 1


def test_a_prefix_of_another_block_is_not_a_claim(tmp_path):
    assert run("--board", _board(tmp_path), "--name", "known").returncode == 1


def test_a_superstring_of_a_block_is_not_a_claim(tmp_path):
    assert run("--board", _board(tmp_path), "--name", "known-branch-extra").returncode == 1


def test_neighbouring_headings_stay_distinct(tmp_path):
    """`known-branch` must not be satisfied by `known-branch-extended`, nor the
    reverse. Anchoring is worthless if it only anchors one end."""
    b = _board(tmp_path)
    assert run("--board", b, "--name", "known-branch").returncode == 0
    assert run("--board", b, "--name", "known-branch-extended").returncode == 0


def test_a_heading_without_a_host_prefix_still_claims(tmp_path):
    """The template says `### <host>/<id>`, but boards in the wild carry both."""
    b = tmp_path / "SESSIONS.md"
    b.write_text("# board\n\n### solo-block — a task\n", encoding="utf-8")
    assert run("--board", str(b), "--name", "solo-block").returncode == 0


def test_a_name_carrying_regex_syntax_is_compared_literally(tmp_path):
    """The old rule used `grep -F` for this; the new one parses headings and must
    not have traded a substring bug for a metacharacter bug."""
    b = tmp_path / "SESSIONS.md"
    b.write_text("# board\n\n### Mac/v1.2+rc — a task\n", encoding="utf-8")
    assert run("--board", str(b), "--name", "v1.2+rc").returncode == 0
    assert run("--board", str(b), "--name", "v1X2+rc").returncode == 1


def test_audit_reports_who_changes_verdict(tmp_path):
    """A stricter gate starts refusing commits that pass today, and the sessions it
    will refuse are mid-task. --audit is what lets that list be read before the
    change lands rather than discovered at somebody's next commit.

    Driven against a fixture board rather than this machine's, and the fixture is
    derived rather than written down. This test has been wrong twice in the same way
    now, which is worth recording, because it is the way the guard itself was wrong:
    depending on ambient setup that happened to be there.

    First cut read the LIVE board — CI has none, so every row came back NOBOARD and
    the table this exists to check was never printed. Second cut wrote the repo name
    into the fixture as the literal "bugarach", which only produces a changing row
    when the checkout directory is called that; it passed here and in CI and failed
    in a clone named anything else.
    """
    board = tmp_path / "SESSIONS.md"
    # THIS checkout's directory name in prose, with no heading for it — the primary
    # checkout's exact situation, and the row the audit must mark as changing.
    here = REPO.name
    board.write_text(
        f"# board\n\n### Mac/somebody-else — their task\n"
        f"- **Touches:** paths under {here}\n", encoding="utf-8")
    r = run("--audit", str(board))
    assert r.returncode == 0, r.stderr
    assert "was" in r.stdout and "now" in r.stdout
    assert "worktree(s) change verdict" in r.stdout
    assert "CHANGES" in r.stdout, r.stdout


def test_audit_says_so_when_there_is_no_board(tmp_path):
    """Quiet and successful, never a crash — it is a report, not a gate."""
    r = run("--audit", str(tmp_path / "absent.md"))
    assert r.returncode == 0
    assert "no board" in r.stdout


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
