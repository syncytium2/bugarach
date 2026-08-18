"""The commit gates prove they are INSTALLED, not merely that they work.

`tests/test_branch_guard.py`, `test_sapper.py` and `test_merge_gate.py` all prove
their gate can fire. None of them proves the gate is wired to anything. It is
not, by default: git ignores `.githooks/` until someone runs

    git config core.hooksPath .githooks

which is per clone, lives in `.git/config`, and travels with nothing — not with a
clone, not with a pull, not with `pip install -e`. This Mac clone went its whole
life without it, so every commit made here bypassed the branch guard and sapper
while the briefing, the docs and the hook's own header all said the gates ran.
Nothing failed. That is the dangerous shape: an absent gate reads exactly like a
passed one.

The briefing says so at session start, which catches a session and only a
session. This catches anyone who runs the suite, on any machine, on their first
`pytest` — and tells them the one command to fix it.

**It asserts about the developer's clone, not about the code**, which is unusual
enough to be worth stating. Two places where the assertion is meaningless and the
test says so instead of failing: CI, where hooks never run and the branch guard is
replaced by branch protection, and any tree that is not a git checkout at all.
"""

import os
import shutil
import subprocess
from pathlib import Path

import pytest

REPO = Path(__file__).parent.parent

FIX = "git config core.hooksPath .githooks"

#: What the hook must actually invoke for the gates to be running. Checking the
#: config VALUE would pass on a `.githooks` that had been emptied; checking the
#: hook's contents is the property we care about.
GUARDS = ("guard_branch.sh", "guard_local_board.sh", "sapper.py")


def hooks_state(hooks_path: str | None, repo: Path) -> tuple[str, str]:
    """Decide whether this clone's commit gates are installed.

    Pure, so it can be driven in every direction from a test rather than by
    breaking someone's git config. Returns ``(state, message)`` where state is
    ``ok`` | ``unset`` | ``missing`` | ``inert``.
    """
    if not hooks_path:
        return "unset", (
            "core.hooksPath is not set, so this clone has NO commit gates: the "
            "branch guard is not stopping a commit on main, sapper is not "
            f"scanning what you stage, and the board guard is not asking whether "
            f"another session on this machine is already in that file.\n\n    {FIX}\n\n"
            "It is per clone and travels with nothing, which is why nothing "
            "warned you until now.")

    hook = Path(hooks_path)
    if not hook.is_absolute():
        hook = repo / hook
    hook = hook / "pre-commit"
    if not hook.exists():
        return "missing", (
            f"core.hooksPath is {hooks_path!r}, but {hook} does not exist, so no "
            f"pre-commit hook runs at all.\n\n    {FIX}")

    body = hook.read_text(encoding="utf-8", errors="replace")
    absent = [g for g in GUARDS if g not in body]
    if absent:
        return "inert", (
            f"core.hooksPath points at {hooks_path!r}, whose pre-commit does not "
            f"run {', '.join(absent)}. A hook is installed but this repo's gates "
            f"are not in it — if you keep your own hooks, chain ours from them:\n\n"
            f"    bash {REPO.name}/.githooks/pre-commit")
    return "ok", f"gates installed via {hooks_path}"


def _configured_hooks_path() -> str | None:
    r = subprocess.run(["git", "config", "--get", "core.hooksPath"],
                       capture_output=True, text=True, cwd=REPO)
    return r.stdout.strip() or None


def test_the_check_can_fire_in_every_direction(tmp_path):
    """The gate proves it can fail before it is trusted to pass.

    Without this, a broken check and an installed hook are indistinguishable —
    the same reason sapper rules ship with self-test fixtures.
    """
    state, msg = hooks_state(None, tmp_path)
    assert state == "unset" and FIX in msg

    state, msg = hooks_state("nowhere", tmp_path)
    assert state == "missing" and FIX in msg

    empty = tmp_path / "hooks"
    empty.mkdir()
    (empty / "pre-commit").write_text("#!/bin/sh\nexit 0\n")
    state, msg = hooks_state("hooks", tmp_path)
    assert state == "inert"
    assert "guard_branch.sh" in msg and "sapper.py" in msg

    real = tmp_path / "ok"
    real.mkdir()
    (real / "pre-commit").write_text(
        "bash tools/guard_branch.sh\nbash tools/guard_local_board.sh\n"
        "python tools/sapper.py --staged\n")
    assert hooks_state("ok", tmp_path)[0] == "ok"

    assert hooks_state(str(real), tmp_path)[0] == "ok", "an absolute path is legal too"


@pytest.mark.skipif(
    os.environ.get("CI") or os.environ.get("GITHUB_ACTIONS"),
    reason="hooks never run in CI; branch protection and the CI sapper job cover it there")
@pytest.mark.skipif(
    shutil.which("git") is None or not (REPO / ".git").exists(),
    reason="not a git checkout, so there is no clone to configure")
def test_this_clone_has_its_commit_gates_installed():
    state, msg = hooks_state(_configured_hooks_path(), REPO)
    assert state == "ok", msg
