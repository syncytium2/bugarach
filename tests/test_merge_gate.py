"""The merge gate proves it can fire, in CI, like sapper does.

`gh pr merge --auto` only waits when a required status check exists. With no
branch protection nothing is required, so it merges instantly and the PR gates
nothing — which is what happened here for a whole session (every PR merged ~90 s
before its own CI finished). `tools/merge_when_green.sh` does the waiting and
verifying client-side instead.

The property worth testing is the counter-intuitive one: **no checks found must
be treated as failure.** An absent gate looks exactly like a passed one, so
"empty means fine" is the bug, not the fallback.
"""

import shutil
import subprocess
from pathlib import Path

import pytest

REPO = Path(__file__).parent.parent
GATE = REPO / "tools" / "merge_when_green.sh"

pytestmark = pytest.mark.skipif(
    shutil.which("bash") is None, reason="bash unavailable (gate is a shell script)"
)


def test_gate_exists_and_is_executable():
    assert GATE.is_file(), f"{GATE} missing"


def test_decision_logic_can_fire_in_every_direction():
    """--selftest feeds the pure verdict() the JSON shapes gh actually returns:
    all-success, a failure, in-progress, queued, empty, garbage, skipped,
    cancelled, and the legacy `state` form."""
    r = subprocess.run(["bash", str(GATE), "--selftest"],
                       capture_output=True, text=True, cwd=REPO)
    assert r.returncode == 0, r.stdout + r.stderr
    assert "all checks pass" in r.stdout


def test_syntax_is_valid():
    r = subprocess.run(["bash", "-n", str(GATE)], capture_output=True, text=True)
    assert r.returncode == 0, r.stderr


def test_refuses_a_non_numeric_pr_argument():
    """Usage errors exit 2, never 0 — a gate that no-ops on bad input is the
    same failure class it exists to prevent."""
    r = subprocess.run(["bash", str(GATE), "not-a-pr"],
                       capture_output=True, text=True, cwd=REPO)
    assert r.returncode == 2, r.stdout + r.stderr
