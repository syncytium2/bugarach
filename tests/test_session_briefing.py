"""The session briefing must actually carry the facts that bind.

CLAUDE.md's first line says to read docs/FOUNDATIONS.md at session start. A
session on 2026-08-13 did not, and spent a day building on the assumption that
TTX silences the field — which this project's data refutes and FOUNDATIONS
forbids. Tony: *"claude.md is the first thing you ignore. we have built tools
for this purpose."*

So the fix is not another sentence in a file that has to be read to work. The
briefing injects the binding facts into every session's context whether anyone
opens the file or not — and these tests are the sapper-style proof that it can
fire, because a channel nobody verifies is the same as no channel.
"""

import json
import subprocess
import time
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "tools" / "session_briefing.sh"


@pytest.fixture(scope="module")
def briefing():
    t0 = time.monotonic()
    out = subprocess.run(["bash", str(SCRIPT)], cwd=ROOT,
                         capture_output=True, text=True, timeout=30)
    return out, time.monotonic() - t0


def test_it_runs_and_succeeds(briefing):
    out, _ = briefing
    assert out.returncode == 0, out.stderr


def test_it_is_fast_enough_to_be_unconditional(briefing):
    """It runs on the blocking session-start path, ahead of the generic hook.
    interface2 lost half a day to a SessionStart hook that took the whole
    session down at 60 s; this one is local-only and must stay trivial, because
    the moment it needs a budget it becomes droppable — and a channel dropped
    for budget is the failure it exists to prevent."""
    _, elapsed = briefing
    assert elapsed < 3.0, f"briefing took {elapsed:.1f}s on the blocking path"


def test_it_carries_the_ttx_fact(briefing):
    """The specific thing a session got wrong, and the reason this file exists."""
    out, _ = briefing
    assert "TTX IS NOT A SILENCING CONTROL" in out.stdout
    assert "min_rois" in out.stdout, "the consequence must travel with the fact"


def test_it_carries_the_held_out_treatment(briefing):
    out, _ = briefing
    assert "Senktide is not one effect" in out.stdout


def test_the_facts_are_read_from_foundations_not_restated():
    """If the briefing restated them, the two would drift and the canonical file
    would quietly stop being canonical."""
    text = SCRIPT.read_text()
    assert "docs/FOUNDATIONS.md" in text
    assert "TTX IS NOT" not in text, "the fact is extracted, never hardcoded here"


def test_foundations_still_has_the_section_the_briefing_extracts():
    """The other half of the same guard: renaming or deleting section 9 would
    make the briefing silently print nothing."""
    foundations = (ROOT / "docs" / "FOUNDATIONS.md").read_text()
    assert "## 9. Facts about the preparation" in foundations
    assert "## 10." in foundations, "the extractor needs a terminating heading"


def test_it_names_the_gates_that_get_skipped(briefing):
    out, _ = briefing
    for gate in ("murderboard", "never commit on main", "render the figure"):
        assert gate in out.stdout, f"gate not surfaced: {gate}"


def test_it_reports_whether_the_commit_gates_are_installed(briefing):
    """core.hooksPath is per clone and travels with nothing, so a fresh clone
    silently has no branch guard and no sapper."""
    out, _ = briefing
    assert "commit gates:" in out.stdout


def test_it_is_wired_into_both_session_start_matchers():
    """Wired as its own entry so the vendored generic hook stays byte-identical
    and re-copyable, and placed FIRST so the binding facts land even if the
    later git briefing truncates."""
    cfg = json.loads((ROOT / ".claude" / "settings.json").read_text())
    blocks = cfg["hooks"]["SessionStart"]
    assert {b["matcher"] for b in blocks} == {"startup", "resume"}
    for block in blocks:
        assert block["hooks"][0]["command"] == "bash tools/session_briefing.sh"
