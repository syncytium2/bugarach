"""Sapper wired into the normal suite: every rule proves it can fire, and the
tracked tree is clear of BLOCK findings — so CI enforces the rules even for
contributors without the pre-commit hook."""

import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).parent.parent
SAPPER = REPO / "tools" / "sapper.py"


def test_every_rule_can_fire():
    r = subprocess.run([sys.executable, str(SAPPER), "--selftest"],
                       capture_output=True, text=True, cwd=REPO)
    assert r.returncode == 0, r.stdout + r.stderr


def test_tracked_tree_is_clear():
    r = subprocess.run([sys.executable, str(SAPPER), "--all"],
                       capture_output=True, text=True, cwd=REPO)
    assert r.returncode == 0, r.stdout + r.stderr
