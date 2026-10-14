"""A session messages another only once it has a name the other can reply to.

Tony, 2026-10-14, after a cross-machine test showed an auto-titled session's handle
follows its title: rename every session at its start, and mechanize it rather than
write it into CLAUDE.md, "the least reliable option of all the tools we have for this
persisting behavior". The hook is `.claude/hooks/require-a-name-before-message.sh`.

Following `test_hooks_installed.py`, it is checked for being WIRED as well as for
working: an unwired gate reads exactly like a passed one.
"""

import json
import shutil
import subprocess
from pathlib import Path

import pytest

REPO = Path(__file__).parent.parent
HOOK = REPO / ".claude" / "hooks" / "require-a-name-before-message.sh"
SETTINGS = REPO / ".claude" / "settings.json"

pytestmark = pytest.mark.skipif(shutil.which("bash") is None, reason="no bash")


def test_the_hook_passes_its_own_selftest():
    out = subprocess.run(["bash", str(HOOK), "--selftest"],
                         capture_output=True, text=True, cwd=REPO)
    assert out.returncode == 0, out.stdout + out.stderr
    assert "PASS" in out.stdout and "FAIL" not in out.stdout


def _commands(event: str, matcher: str) -> list[str]:
    hooks = json.loads(SETTINGS.read_text(encoding="utf-8"))["hooks"][event]
    return [h["command"] for block in hooks if block.get("matcher") == matcher
            for h in block["hooks"]]


def test_it_gates_every_send():
    assert "bash .claude/hooks/require-a-name-before-message.sh" in _commands(
        "PreToolUse", "SendMessage")


@pytest.mark.parametrize("matcher", ["startup", "resume"])
def test_it_speaks_at_every_start(matcher):
    assert ("bash .claude/hooks/require-a-name-before-message.sh --session-start"
            in _commands("SessionStart", matcher))
