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


def test_sap004_sees_a_windows_home():
    """SAP004 once knew only forward-slash homes, and 29 lines of Windows home paths
    reached the public tree past it. Plain and JSON-escaped forms both block; Windows'
    own folders, a placeholder and a program path do not."""
    import importlib.util
    import re
    spec = importlib.util.spec_from_file_location("sapper", SAPPER)
    sapper = importlib.util.module_from_spec(spec)
    sys.modules["sapper"] = sapper           # its dataclasses look the module up
    spec.loader.exec_module(sapper)
    rx = re.compile(next(r for r in sapper.RULES if r.id == "SAP004").pattern)
    one, two = "\\", "\\\\"                    # a backslash, and a JSON-escaped one
    home = "C:" + one + "Users" + one + "someone"
    for bad in (home + one + "runs",
                "C:" + two + "Users" + two + "someone" + two + "runs",
                "wrote " + home + one + "x.png"):
        assert rx.search(bad), bad
    for good in ("C:" + one + "Users" + one + "Public" + one + "x",
                 "C:" + one + "Users" + one + "Default" + one + "x",
                 "%USERPROFILE%" + one + "runs",
                 "C:" + two + "Users" + two + "...",
                 "C:" + one + "Program Files" + one + "MATLAB"):
        assert not rx.search(good), good
