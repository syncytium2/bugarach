"""Every ADR in ``docs/adr/`` is listed in its index, and every index row names a file that exists.

ADR-0005 was the last one written before the habit lapsed for 25 days, and it was also the one
that never reached the index (found 2026-09-23, when the habit restarted). A decision nobody can
find from the index is the failure ADRs exist to prevent.
"""
from __future__ import annotations

import re
from pathlib import Path

ADR = Path(__file__).resolve().parents[1] / "docs" / "adr"


def _files() -> set[str]:
    return {p.name for p in ADR.glob("[0-9][0-9][0-9][0-9]-*.md")}


def _index_rows() -> set[str]:
    text = (ADR / "README.md").read_text(encoding="utf-8")
    return set(re.findall(r"^\| \[\d{4}\]\(([^)]+\.md)\)", text, flags=re.M))


def test_every_adr_is_in_the_index():
    missing = _files() - _index_rows()
    assert not missing, f"ADRs not in docs/adr/README.md's index: {sorted(missing)}"


def test_every_index_row_names_an_adr_that_exists():
    dangling = _index_rows() - _files()
    assert not dangling, f"index rows naming no file: {sorted(dangling)}"


def test_numbers_are_unique():
    nums = [name[:4] for name in _files()]
    assert len(nums) == len(set(nums)), sorted(nums)
