"""The cloud-container Python hook is wired, stays silent, and never runs off-cloud.

`tools/cloud_python.sh` installs the interpreter ADR-0011 requires into a Claude Code
cloud container, from the SessionStart hook, because the environment's setup script
could not be reached from the phone app (2026-09-26). Its output shares the
session-start channel, whose byte budget is the reason the briefing is trimmed, so
the properties that matter are: it is wired for both startup and resume, it prints
nothing when there is nothing wrong, and it does nothing on a machine that is not a
cloud container.
"""
from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
HOOK = REPO / "tools" / "cloud_python.sh"


def _run(env_extra: dict) -> subprocess.CompletedProcess:
    env = {k: v for k, v in os.environ.items()
           if k not in ("CLAUDE_CODE_REMOTE", "BUGARACH_CLOUD_PYTHON_FORCE")}
    env.update(env_extra)
    return subprocess.run(["bash", str(HOOK)], capture_output=True, text=True, env=env,
                          timeout=60)


def test_it_is_wired_for_startup_and_resume():
    settings = json.loads((REPO / ".claude" / "settings.json").read_text(encoding="utf-8"))
    for block in settings["hooks"]["SessionStart"]:
        cmds = [h["command"] for h in block["hooks"]]
        assert "bash tools/cloud_python.sh" in cmds, block["matcher"]


def test_off_cloud_it_does_nothing_and_says_nothing():
    got = _run({})
    assert got.returncode == 0 and got.stdout == "" and got.stderr == ""


def test_with_the_wanted_python_present_it_says_nothing():
    """Asking for a version this interpreter already is: the fast path, no output."""
    import sys
    here = f"{sys.version_info.major}.{sys.version_info.minor}"
    got = _run({"BUGARACH_CLOUD_PYTHON_FORCE": "1", "BUGARACH_CLOUD_PYTHON_VERSION": here})
    assert got.returncode == 0 and got.stdout == ""
