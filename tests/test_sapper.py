"""Sapper wired into the normal suite: every rule proves it can fire, and the
tracked tree is clear of BLOCK findings — so CI enforces the rules even for
contributors without the pre-commit hook."""

import os
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).parent.parent
SAPPER = REPO / "tools" / "sapper.py"
QUOTES = REPO / "tools" / "check_quotes.py"

#: A console that cannot encode this tree's arrows, warning signs or em dashes.
#: Native Windows uses it; forcing it here reproduces that console everywhere.
CP1252 = {**os.environ, "PYTHONIOENCODING": "cp1252"}


def test_every_rule_can_fire():
    r = subprocess.run([sys.executable, str(SAPPER), "--selftest"],
                       capture_output=True, text=True, cwd=REPO)
    assert r.returncode == 0, r.stdout + r.stderr


def test_tracked_tree_is_clear():
    r = subprocess.run([sys.executable, str(SAPPER), "--all"],
                       capture_output=True, text=True, cwd=REPO)
    assert r.returncode == 0, r.stdout + r.stderr


def test_the_gate_survives_a_console_that_cannot_encode_the_line():
    """A gate lost to its own error message is worse than no gate.

    Sapper echoes the offending line. On a cp1252 console that raised
    UnicodeEncodeError, which on 2026-09-22 took `--staged` — the pre-commit
    hook — down on a merge commit over a `→`, and made `--all` die part-way
    through the tree, reading as a broken tool rather than a finished scan.
    CI runs UTF-8, so only the Windows workstation ever saw it.
    """
    for mode in ("--selftest", "--all"):
        r = subprocess.run([sys.executable, str(SAPPER), mode],
                           capture_output=True, text=True, cwd=REPO, env=CP1252)
        assert "UnicodeEncodeError" not in r.stderr, (
            f"{mode} crashed printing its own output:\n{r.stderr}")
        assert r.returncode == 0, r.stdout + r.stderr


def test_the_quote_gate_survives_it_too():
    """`check_quotes.py` echoes the offending line as well, and runs BEFORE
    sapper in `.githooks/pre-commit`, so it is the first gate that console can
    take down. Its own suite is `tests/test_check_quotes.py`; this check lives
    here beside sapper's so the twin fixes cannot drift apart unnoticed."""
    r = subprocess.run([sys.executable, str(QUOTES), "--all"],
                       capture_output=True, text=True, cwd=REPO, env=CP1252)
    assert "UnicodeEncodeError" not in r.stderr, r.stderr
    assert r.returncode == 0, r.stdout + r.stderr
