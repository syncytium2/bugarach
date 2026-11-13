"""Every ADR in ``docs/adr/`` is listed in its index, and every index row names a file that exists.

ADR-0005 was the last one written before the habit lapsed for 25 days, and it was also the one
that never reached the index (found 2026-09-23, when the habit restarted). A decision nobody can
find from the index is the failure ADRs exist to prevent.
"""
from __future__ import annotations

import re
from pathlib import Path

ADR = Path(__file__).resolve().parents[1] / "docs" / "adr"


# A record's ID is a number (0001 to 0023, closed) or a date and four random hex characters
# (every record since; armory's ADR kit, and docs/adr/README.md, Convention).
NUMBERED = re.compile(r"^(\d{4})-[a-z0-9-]+\.md$")
DATED = re.compile(r"^(\d{4}-\d{2}-\d{2}-[0-9a-f]{4})-[a-z0-9-]+\.md$")
LAST_NUMBER = 23


def _id(name: str) -> str | None:
    m = DATED.match(name) or NUMBERED.match(name)
    return m.group(1) if m else None


def _files() -> set[str]:
    return {p.name for p in ADR.glob("[0-9]*.md")}


def _index_rows() -> set[str]:
    text = (ADR / "README.md").read_text(encoding="utf-8")
    return set(re.findall(r"^\| \[[0-9a-f-]+\]\(([^)]+\.md)\)", text, flags=re.M))


def test_every_record_is_named_by_a_number_or_by_a_date_and_hash():
    odd = sorted(n for n in _files() if _id(n) is None)
    assert not odd, f"not NNNN-title.md or YYYY-MM-DD-hhhh-title.md: {odd}"


def test_no_record_takes_a_number_after_the_last_one():
    """Tony, 2026-11-13: numbered ADRs are banned. That day a session wrote a record numbered
    0024, ten days after the lab moved to date-and-hash IDs, because nothing here said so."""
    # a dated name also fits the numbered pattern (its year reads as a number), so rule it out
    late = sorted(n for n in _files()
                  if not DATED.match(n) and NUMBERED.match(n) and int(n[:4]) > LAST_NUMBER)
    assert not late, (f"numbered records are closed at {LAST_NUMBER:04d}; name these "
                      f"YYYY-MM-DD-<4 hex>-title.md: {late}")


def test_the_heading_carries_the_files_id():
    for name in sorted(n for n in _files() if DATED.match(n)):
        first = (ADR / name).read_text(encoding="utf-8").splitlines()[0]
        assert first.startswith(f"# ADR {_id(name)}: "), f"{name}: heading is {first!r}"


def test_every_adr_is_in_the_index():
    missing = _files() - _index_rows()
    assert not missing, f"ADRs not in docs/adr/README.md's index: {sorted(missing)}"


def test_every_index_row_names_an_adr_that_exists():
    dangling = _index_rows() - _files()
    assert not dangling, f"index rows naming no file: {sorted(dangling)}"


def test_ids_are_unique():
    ids = [_id(name) for name in _files()]
    assert len(ids) == len(set(ids)), sorted(ids)
