"""The sweep deletes worktrees, so its refusals are the part that has to be proved.

`tools/worktree_sweep.sh` removes a worktree when it is merged, clean and idle.
Two of those three are cheap facts about git. The third is a guess about a
PERSON — is somebody working in here right now — and it is made from file
timestamps, which is the only signal that cannot go stale the way a board block
does.

That guess has two failure modes and only one of them is loud:

  * saying "live" about an idle worktree costs a stale directory,
  * saying "idle" about a live one DELETES SOMEBODY'S WORKING TREE.

So the probe must fail towards "live". The version these tests were added
against did the opposite: it sent find's stderr to /dev/null and read no-output
as not-recently-touched, so an environment where `find` cannot parse `-newermt`
— a `find` shadowed by a wrapper on the session's PATH, which is a real
configuration on this machine — turned the guard off silently and offered four
worktrees for deletion, one of them written to 44 minutes earlier. `test_probe_failure_*`
is that scenario.

The ordering test is the other half. Liveness used to be checked AFTER
uncommitted-changes, so a worktree that was both dirty and live printed only its
dirtiness. A session read that line, plus an unpushed branch and a board block
with no DONE on it, and concluded the work was abandoned — while its author was
still typing. The evidence was there and the report did not show it.
"""

from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path

import pytest

SWEEP = Path(__file__).resolve().parents[1] / "tools" / "worktree_sweep.sh"
OLD = "200001010000"  # far enough back to be idle under any --hours


def git(*args: str, cwd: Path) -> str:
    return subprocess.run(
        ["git", *args], cwd=cwd, check=True, capture_output=True, text=True
    ).stdout


def backdate(path: Path) -> None:
    """Make every file look old. A worktree created seconds ago is 'live' by
    construction, which would make the idle branch of these tests untestable."""
    for f in path.rglob("*"):
        if f.is_file():
            os.utime(f, (946684800, 946684800))


def sweep(repo: Path, *args: str, path_prefix: Path | None = None) -> str:
    env = dict(os.environ)
    if path_prefix is not None:
        env["PATH"] = f"{path_prefix}{os.pathsep}{env['PATH']}"
    r = subprocess.run(
        ["bash", str(SWEEP), *args],
        cwd=repo, capture_output=True, text=True, env=env,
    )
    return r.stdout + r.stderr


@pytest.fixture
def tree(tmp_path: Path):
    """An origin, a primary checkout, and two worktrees: one merged, one not."""
    origin = tmp_path / "origin.git"
    subprocess.run(["git", "init", "-q", "--bare", "-b", "main", str(origin)], check=True)

    primary = tmp_path / "primary"
    subprocess.run(["git", "clone", "-q", str(origin), str(primary)], check=True)
    git("config", "user.email", "t@example.com", cwd=primary)
    git("config", "user.name", "t", cwd=primary)
    (primary / "seed.txt").write_text("seed\n")
    git("add", "-A", cwd=primary)
    git("commit", "-qm", "seed", cwd=primary)
    git("push", "-q", "origin", "main", cwd=primary)

    # merged: a branch pointing at main, so it is an ancestor of origin/main
    merged = tmp_path / "wt-merged"
    git("worktree", "add", "-q", "-b", "done-work", str(merged), "main", cwd=primary)

    # unmerged: one commit origin/main does not have
    ahead = tmp_path / "wt-ahead"
    git("worktree", "add", "-q", "-b", "live-work", str(ahead), "main", cwd=primary)
    (ahead / "new.txt").write_text("x\n")
    git("add", "-A", cwd=ahead)
    git("commit", "-qm", "ahead", cwd=ahead)

    for p in (primary, merged, ahead):
        backdate(p)
    return primary, merged, ahead


@pytest.fixture
def broken_find(tmp_path: Path) -> Path:
    """A `find` that cannot answer — stderr and a non-zero exit, like a find
    whose -newermt does not take a relative string."""
    d = tmp_path / "badfind"
    d.mkdir()
    f = d / "find"
    f.write_text("#!/bin/sh\necho 'find: -newermt: invalid timestamp' >&2\nexit 1\n")
    f.chmod(0o755)
    return d


def test_an_idle_merged_worktree_is_offered(tree):
    primary, merged, _ = tree
    out = sweep(primary, )
    assert "wt-merged" in out
    assert "REMOVE" in out, out
    assert "idle" in out, out


def test_an_unmerged_worktree_is_never_offered(tree):
    primary, _, ahead = tree
    out = sweep(primary)
    line = next(l for l in out.splitlines() if "wt-ahead" in l)
    assert "REMOVE" not in line, line
    assert "not on main" in line, line


def test_a_live_worktree_is_kept_and_named_live(tree):
    """The whole point. Same worktree as test_an_idle_merged_worktree_is_offered,
    one file touched."""
    primary, merged, _ = tree
    (merged / "seed.txt").touch()
    out = sweep(primary)
    line = next(l for l in out.splitlines() if "wt-merged" in l)
    assert "live" in line, line
    assert "REMOVE" not in line, line
    assert "0 removable" in out, out


def test_liveness_is_reported_before_dirtiness(tree):
    """A worktree that is BOTH dirty and live must say live. Reporting only the
    dirtiness is what let a session read an active worktree as abandoned."""
    primary, merged, _ = tree
    (merged / "scratch.txt").write_text("uncommitted\n")
    line = next(l for l in sweep(primary).splitlines() if "wt-merged" in l)
    assert "live" in line, line


def test_probe_failure_keeps_everything(tree, broken_find):
    """FAIL CLOSED. An unanswerable probe must not read as idle."""
    primary, *_ = tree
    out = sweep(primary, path_prefix=broken_find)
    assert "0 removable" in out, out
    assert "unknown" in out, out
    assert "REMOVE" not in out, out


def test_probe_failure_says_so_rather_than_passing_quietly(tree, broken_find):
    primary, *_ = tree
    out = sweep(primary, path_prefix=broken_find)
    assert "liveness probe failed" in out, out


def test_live_mode_lists_only_the_live(tree):
    primary, merged, _ = tree
    (merged / "seed.txt").touch()
    out = sweep(primary, "--live")
    assert "wt-merged" in out
    assert "wt-ahead" not in out, out
    assert "IN USE" in out, out


def test_live_mode_says_so_when_nobody_is_there(tree):
    primary, *_ = tree
    out = sweep(primary, "--live")
    assert "nobody is live" in out, out
    # and it must not be read as permission
    assert "not a promise" in out, out


def test_live_mode_refuses_to_remove(tree):
    primary, *_ = tree
    out = sweep(primary, "--apply", "--live")
    assert "does not remove" in out, out


def test_the_primary_checkout_is_never_listed(tree):
    """It offered to delete the primary once already."""
    primary, *_ = tree
    out = sweep(primary)
    assert "primary" not in out.replace(str(primary), ""), out


# --- --board: the claims, judged against the worktrees ----------------------
#
# The sweep's own header says board blocks "go stale the moment a session stops
# updating them", and then it never reads one. On 2026-08-28 the board carried 26
# ACTIVE claims against 16 worktrees, and a session that trusted the count
# reported an area unclaimed while two sessions were working in it.
#
# These pin the two parsing rules that decide every row, because both have a
# recorded failure behind them: a status must be read INSIDE its own block, and a
# claim must match a heading EXACTLY rather than appearing anywhere in the prose.


def board(tmp_path: Path, text: str) -> Path:
    p = tmp_path / "SESSIONS.md"
    p.write_text("# Machine-local session board — test\n\n" + text)
    return p


def test_an_active_claim_with_no_worktree_is_stale(tree, tmp_path):
    primary, *_ = tree
    b = board(tmp_path, "### m/ghost — long gone\n- **Status:** ACTIVE\n")
    out = sweep(primary, "--board", "--board-file", str(b))
    assert "STALE" in out and "ghost" in out, out


def test_a_done_block_is_not_a_claim(tree, tmp_path):
    """DONE blocks stay in the file forever; counting them would report every
    finished task as a live session."""
    primary, *_ = tree
    b = board(tmp_path, "### m/ghost — finished\n- **Status:** DONE 2026-08-28\n")
    out = sweep(primary, "--board", "--board-file", str(b))
    assert "ghost" not in out, out
    assert "0 ACTIVE claim(s)" in out, out


def test_a_later_active_block_does_not_vouch_for_an_earlier_done_one(tree, tmp_path):
    """The status has to be read within its own block's span.

    Reading the file globally — "does ACTIVE appear anywhere" — would let one
    live block certify every finished block above it, which on a 237-block board
    means the report says nothing at all.
    """
    primary, *_ = tree
    b = board(tmp_path,
              "### m/finished — done\n- **Status:** DONE 2026-08-28\n\n"
              "### m/working — live\n- **Status:** ACTIVE\n")
    out = sweep(primary, "--board", "--board-file", str(b))
    assert "finished" not in out, out
    assert "working" in out, out
    assert "1 ACTIVE claim(s)" in out, out


def test_prose_naming_another_worktree_is_not_a_claim(tree, tmp_path):
    """`guard_local_board.sh` matched by substring once, and a block that merely
    MENTIONED another worktree counted as claiming it. This reuses its heading
    rule, so the same text must not produce a claim here either."""
    primary, *_ = tree
    b = board(tmp_path,
              "### m/working — live\n- **Status:** ACTIVE\n"
              "- **Notes:** overlaps wt-merged, which is another session's.\n")
    out = sweep(primary, "--board", "--board-file", str(b))
    assert "1 ACTIVE claim(s)" in out, out
    # wt-merged is a real worktree here; if the prose claimed it, it would not
    # be reported as unclaimed.
    assert "UNCLAIM" in out and "wt-merged" in out, out


def test_a_worktree_with_no_claim_is_reported(tree, tmp_path):
    primary, *_ = tree
    b = board(tmp_path, "### m/working — live\n- **Status:** ACTIVE\n")
    out = sweep(primary, "--board", "--board-file", str(b))
    assert "UNCLAIM" in out, out
    assert "wt-merged" in out and "wt-ahead" in out, out


def test_a_block_headed_with_the_branch_counts_as_a_claim(tree, tmp_path):
    """A block may legitimately be headed with the branch rather than the
    directory; the commit gate accepts either, so this must too or it reports
    claimed worktrees as unclaimed."""
    primary, *_ = tree
    b = board(tmp_path, "### m/done-work — by branch\n- **Status:** ACTIVE\n")
    out = sweep(primary, "--board", "--board-file", str(b))
    assert "STALE" not in out, out
    assert not [ln for ln in out.splitlines()
                if "wt-merged" in ln and "UNCLAIM" in ln], out


def test_board_mode_refuses_to_apply(tree, tmp_path):
    """It reports intent, which git state cannot adjudicate. Closing a claim is
    the claimant's call."""
    primary, *_ = tree
    b = board(tmp_path, "### m/ghost — gone\n- **Status:** ACTIVE\n")
    out = sweep(primary, "--board", "--apply", "--board-file", str(b))
    assert "never edits the board" in out, out


def test_a_missing_board_is_not_reported_as_nothing_claimed(tree, tmp_path):
    """"No board" and "no claims" must not read alike — the first means the
    check could not run."""
    primary, *_ = tree
    out = sweep(primary, "--board", "--board-file", str(tmp_path / "absent.md"))
    assert "nothing can be checked" in out, out
