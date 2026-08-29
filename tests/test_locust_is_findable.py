"""Whatever a person sees on screen, grepping the source for it must land.

The detector shown everywhere as **locust** is keyed `cicada` in the code, and
that split is deliberate: the key is the value in `detections.csv`'s `detector`
column, which is output contract shared with interface2 and fireflies, so it does
not move on this repo's say-so (ADR-0002;
`docs/todo/2026-08-24-the-identifier-still-says-cicada.md`).

**What the split cost, until this file existed.** `src/bugarach/detectors/
cicada.py` implements locust and never once contained the word. Neither did
`bench.py`, `detect_folder.py`, `emit.py` or `store.py`. Across all of `src/` the
name appeared on eight lines in three files, none of them the implementation — so
a reader who saw `locust` on a screen, in a figure, in the README or in the
glossary and went looking for it in the source found nothing, and the todo had
predicted exactly that ("a reader who greps for what they saw on screen finds
nothing"). Tony, 2026-08-29: *"i see cicada.py that makes it difficult to use
locust without confusion."*

The repair was not a rename. It is that **every file where `cicada` is an
identifier also says `locust`**, which is what these tests hold in place. That is
a file-level property — "if a file contains X it must also contain Y" — and
sapper's rules are per-line regexes, so it lives here rather than as a SAP rule.

Three things are spelled similarly and the module docstring of `detectors/
cicada.py` is where the difference is written down once: *locust* the detector,
`cicada` the identifier, and **CICADA** the Cossart lab's upstream tool.
"""

from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]


def _tracked(pattern: str) -> list[str]:
    out = subprocess.run(["git", "ls-files", pattern], cwd=ROOT,
                         capture_output=True, text=True, check=True)
    return [p for p in out.stdout.splitlines() if p.endswith(".py")]


def _uses_the_key(text: str) -> bool:
    """Does this file use `cicada` as an IDENTIFIER, rather than discussing it?

    The quoted key (`"cicada"`), the function, and the module path are uses. A
    file that only mentions CICADA the upstream tool in prose is not making the
    reader's problem and is not asked to carry the signpost.
    """
    return any(n in text for n in ('"cicada"', "'cicada'", "cicada_detect",
                                   "detectors.cicada", "detectors import cicada"))


SRC = [p for p in _tracked("src/bugarach")
       if _uses_the_key((ROOT / p).read_text(encoding="utf-8"))]


def test_the_survey_found_the_files_it_is_about():
    """If this drops to nothing the tests below pass by vacuum."""
    assert len(SRC) >= 5, (
        f"expected the cicada key across several modules, found {SRC}")
    assert "src/bugarach/detectors/cicada.py" in SRC


@pytest.mark.parametrize("rel", SRC)
def test_every_file_using_the_cicada_key_also_names_locust(rel):
    """The property, stated once and checked per file.

    A new module that reaches for the key inherits the obligation automatically,
    which is the point: the next person to add a detector does not have to have
    read the ADR to be told about the split.
    """
    text = (ROOT / rel).read_text(encoding="utf-8")
    assert "locust" in text, (
        f"{rel} uses `cicada` as an identifier and never says `locust`. The "
        f"detector is called locust everywhere a person can see it, and the key "
        f"stays `cicada` because it is the detections.csv contract value — but a "
        f"reader grepping for what they saw on screen has to land somewhere. Add "
        f"a line saying which detector this is and why the key differs; "
        f"`bugarach/detectors/cicada.py` carries the long form.")


def test_the_implementation_says_it_is_locust_in_its_first_lines():
    """Not merely somewhere in the file — where a reader opening it will look.

    `bench.py` mentioning locust in a comment 900 lines down would satisfy the
    test above and none of its purpose.
    """
    head = (ROOT / "src/bugarach/detectors/cicada.py").read_text(
        encoding="utf-8")[:2000]
    assert "locust" in head, (
        "the module that IS locust must name itself in its opening docstring")


def test_the_three_way_split_is_written_down_where_it_is_needed():
    """key vs name vs upstream tool — all three, in the one canonical place."""
    doc = (ROOT / "src/bugarach/detectors/cicada.py").read_text(encoding="utf-8")
    head = doc[:3000]
    for needle, why in (
            ("locust", "the name a person sees"),
            ("detections.csv", "why the key cannot move unilaterally"),
            ("Cossart", "CICADA the upstream tool, the third referent")):
        assert needle in head, (
            f"the docstring must name {needle} — {why} — or the reader has two "
            f"of the three things and no way to tell which they are holding")
