"""The decision records pass armory's ADR kit, vendored at ``tools/adr/adr.py``.

Tony, 2026-11-13: *"vendor and wire the armory adr kit"*, on the day a session wrote a numbered
record ten days after the lab had moved to date-and-hash IDs. The kit is wired in three places:
the CI step, the Claude Code hook in ``.claude/settings.json`` (which blocks a git commit, merge,
push, pull or rebase while a rule fails), and this test, so plain ``pytest`` runs the same gate.

Which rules fail and which only warn is in ``.adr-kit.json``. Four are lowered to warnings for
records written before the kit arrived; the kit has no setting that turns a rule off.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
KIT = REPO / "tools" / "adr" / "adr.py"

# The rules a record written today has to pass. Lowering one of these in .adr-kit.json would
# let a numbered-after-0023 mistake, an unindexed record or a shared ID back in.
MUST_FAIL = ("filename", "heading", "index", "links", "collision")


def test_the_kit_names_where_it_came_from():
    lines = KIT.read_text(encoding="utf-8").splitlines()
    assert lines[1].startswith("# vendored from syncytium2/armory @ "), lines[1]
    assert lines[2] == "# instrument: verification"


def test_the_rules_a_new_record_must_pass_are_not_lowered():
    severity = json.loads((REPO / ".adr-kit.json").read_text(encoding="utf-8")).get("severity", {})
    lowered = sorted(r for r in MUST_FAIL if severity.get(r, "fail") != "fail")
    assert not lowered, f"lowered to a warning in .adr-kit.json: {lowered}"


def test_the_hook_is_wired():
    settings = json.loads((REPO / ".claude" / "settings.json").read_text(encoding="utf-8"))
    commands = [h["command"] for e in settings["hooks"]["PreToolUse"] if e["matcher"] == "Bash"
                for h in e["hooks"]]
    assert any("tools/adr/adr.py" in c and c.rstrip().endswith("hook || exit 0") for c in commands)


def test_the_decision_records_pass_the_kit():
    shallow = subprocess.run(["git", "rev-parse", "--is-shallow-repository"], cwd=REPO,
                             capture_output=True, text=True, encoding="utf-8")
    if shallow.stdout.strip() == "true":
        pytest.skip("a shallow clone: the kit fails its immutability rule by design")
    # -X utf8: without it the kit can lose git output on Windows and still pass
    # (armory, docs/handoffs/2026-11-09-adr-kit-and-project-state-on-windows.md).
    run = subprocess.run([sys.executable, "-X", "utf8", str(KIT), "check"], cwd=REPO,
                         capture_output=True, text=True, encoding="utf-8")
    failures = [ln for ln in (run.stdout + run.stderr).splitlines() if ln.startswith("FAIL")]
    assert run.returncode == 0, "\n".join(failures[:20])
