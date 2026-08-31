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

# TWO KINDS OF POINTER, and the first version of this file only checked one.
#
# Markdown links — `](path)` — were 18 of the ~49 pointers in the index. The other
# 31 are bare code spans, which is how most rows cite a file because that is how it
# reads on the page. That set included EVERY pointer in the Known-traps section and
# `docs/learned/assessment_cossart.json` — the Cossart row the index was written
# for. So the suite went green over a dead row: a todo that existed only on an
# unmerged branch.
#
# Third check in this repo that could not fail, and this one was in the test whose
# own docstring argues a dead row is worse than a missing one. Caught by review, not
# by the check.
LINK = re.compile(r"\]\(([^)#][^)]*)\)")
# A code span that names a file: has an extension this repo actually uses, or ends
# in `/` for a directory. Deliberately narrow — `n_hit / n_scored` and `--score-spec`
# are code spans too and are not pointers.
SPAN = re.compile(r"`([A-Za-z0-9_][A-Za-z0-9_./-]*"
                  r"(?:\.(?:md|py|json|toml|sh|awk|cff|html|txt)|/))`")

# Owed and not written; its row says so in prose instead of linking. Listed here so
# the exemption is one named line rather than a silently loose pattern.
EXEMPT = {"docs/decisions.md"}


def _pointers():
    """Every pointer in the index, markdown link or code span, as (kind, target)."""
    text = INDEX.read_text(encoding="utf-8")
    for m in LINK.finditer(text):
        t = m.group(1).strip()
        if not t.startswith(("http://", "https://", "mailto:")):
            # links are written relative to docs/
            yield "link", t
    for m in SPAN.finditer(text):
        t = m.group(1).strip()
        if t not in EXEMPT:
            # code spans read as repo-root-relative, which is how they read on the page
            yield "span", t


def _links():
    return [t for kind, t in _pointers() if kind == "link"]


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


@pytest.mark.parametrize("kind,target", sorted(set(_pointers())))
def test_every_index_pointer_resolves(kind, target):
    """Both kinds, because only checking one is how a dead row shipped.

    A row may only point at something on `main`. Citing a file that exists on an
    unmerged branch is dead for every reader who has not checked that branch out,
    and this repo runs 14 worktrees at once.
    """
    # Markdown links are relative to docs/. Code spans are written BOTH ways in the
    # index — `tools/sapper.py` from the repo root, `generator.md` and `handoffs/...`
    # from docs/, because inside a section the shorthand is what reads well. This
    # resolves against either root and passes if the pointer lands anywhere real:
    # the job is catching a pointer to NOTHING, which is what shipped, not enforcing
    # one path style on prose.
    roots = [INDEX.parent] if kind == "link" else [ROOT, INDEX.parent]
    assert any((r / target).resolve().exists() for r in roots), (
        f"docs/INDEX.md points at {target!r} ({kind}), which does not exist. If it "
        f"lives on an unmerged branch, land it before indexing it; if it moved, fix "
        f"the row in the same commit; if it is not built yet, say so in the row "
        f"instead of naming a path, the way the decisions.md row does.")


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
