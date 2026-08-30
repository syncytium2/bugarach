"""Every path `docs/INDEX.md` points at must exist.

An index is a promise that a lookup will land. A dead row is worse than a missing
row, because a reader who follows it concludes the thing is gone rather than that
the index is stale — and this repo's whole argument for the file is that the
information was already here and unfindable.

The index was written on 2026-08-30 after a session spent several turns
re-deriving machinery that `tools/import_dandi.py` already had. It carries one
deliberately unresolvable pointer -- `docs/decisions.md`, which is owed and not
written -- and that row says so in its own text rather than linking. If someone
writes that file, the row becomes a link and this test starts guarding it.
"""
from __future__ import annotations

import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "docs" / "INDEX.md"

# ](path) — skipping anchors, URLs, and the bare-code spans the table uses for
# things that are not links.
LINK = re.compile(r"\]\(([^)#][^)]*)\)")


def _links():
    text = INDEX.read_text(encoding="utf-8")
    for m in LINK.finditer(text):
        target = m.group(1).strip()
        if target.startswith(("http://", "https://", "mailto:")):
            continue
        yield target


def test_the_index_exists():
    """It is referenced from CLAUDE.md, so its absence is a broken instruction."""
    assert INDEX.is_file(), f"{INDEX} is missing"


def test_the_index_is_announced():
    """An index nobody is pointed at is the defect it was written to fix.

    The first version of this file shipped with a docstring claiming CLAUDE.md
    referenced it, and CLAUDE.md did not. Checked rather than asserted now, in
    both places a session actually reads: the instructions file it loads at start,
    and the briefing the SessionStart hook prints.
    """
    claude_md = (ROOT / "CLAUDE.md").read_text(encoding="utf-8")
    assert "docs/INDEX.md" in claude_md, (
        "CLAUDE.md does not point at docs/INDEX.md — an index with no address is "
        "the exact failure it exists to fix")

    briefing = (ROOT / "tools" / "session_briefing.sh").read_text(encoding="utf-8")
    assert "docs/INDEX.md" in briefing, (
        "the session briefing does not mention docs/INDEX.md; a session that "
        "never reads CLAUDE.md in full would never learn the index exists")


@pytest.mark.parametrize("target", sorted(set(_links())))
def test_every_index_link_resolves(target):
    """A row that points nowhere reads as 'the thing is gone', not 'fix the row'."""
    path = (INDEX.parent / target).resolve()
    assert path.exists(), (
        f"docs/INDEX.md points at {target!r}, which does not exist. Either the "
        f"file moved — update the row in the same commit — or the row was "
        f"written for something not built yet, in which case say so in the row "
        f"instead of linking, the way the decisions.md row does.")


def test_the_index_has_not_quietly_emptied():
    """A guard against the file surviving as a heading with no rows.

    Cheap, and this repo has twice shipped a check that could not fail.
    """
    rows = [ln for ln in INDEX.read_text(encoding="utf-8").splitlines()
            if ln.startswith("| ") and "---" not in ln]
    assert len(rows) > 25, f"only {len(rows)} table rows — did the index lose content?"
