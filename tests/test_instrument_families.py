"""The instrument-family vocabulary lives here, because nowhere else held it.

`bfbc375` gave every instrument in this repo a `# instrument: <family>` line, and
argued the family belongs in the file rather than in a registry one directory away.
That argument is right and this file does not undo it: **the per-instrument family
stays in the instrument.** What has to live somewhere central is the *vocabulary* —
the five legal values — and until now it lived in exactly one place, the body of
`bfbc375`'s commit message. A commit message is not a lookup. Three things followed
from that, and all three were true on `main` when this file was written:

  * **`staleness` had zero members.** The family was defined and never used, while
    `tools/site_staleness.py` — a tool whose entire subject is a published copy
    falling behind its source — carried no declaration at all.
  * **Four other instruments carried none either**, including
    `tools/merge_when_green.sh`, which is one of the two gates CLAUDE.md names as
    mechanized, and `tools/check_milestones.py`.
  * **A typo would have been invisible.** Nothing read the values, so
    `# instrument: verifcation` would have sat there indefinitely looking declared.

So the vocabulary is here, next to the checks that read it, and a family that
nobody uses now goes red.

WHY THE THIRD CHECK IS ABOUT VENDORING, WHICH LOOKS UNRELATED
--------------------------------------------------------------
It is the defect the declaration commit actually shipped. Five of its seventeen
lines went into **vendored** copies, inserted at line 2 — directly beneath the
shebang and directly *above* the `vendored from <repo> @ <sha>` stamp, pushing the
stamp to line 3.

Line 2 is the only line `murderboard_revendor.stamp_line_index` will look at in a
file with a shebang. Measured here, not reasoned about: with the declaration on
line 2, `python3 tools/murderboard_revendor.py --check --root .` reported

    !! STAMP IN THE WRONG PLACE — the gate sees it, this tool will not
       touch it, so it would stay unbumped behind a green check

for all three murderboard-vendored tools, one of which is the re-vendor tool
itself. The freshness gate reads the stamp with a looser scan and went on saying
"current", so the two instruments disagreed about the same file — which is the
`propagation` family describing its own breakage. Upstream anticipated exactly
this (`misplaced_stamp_line`, and its docstring calls it "the quiet one"), so the
repair was to put the stamp back on line 2 and the declaration below it.

The check imports that function rather than restating the rule, so this test cannot
drift away from the parser it is protecting.

WHAT THIS DOES NOT CATCH, said plainly so nobody reads it as more
-----------------------------------------------------------------
**It cannot tell you that an instrument is missing its declaration.** Which files
are instruments is a judgement — that is the whole reason `bfbc375` declared the
families instead of deriving them, after a classifier filed every `murderboard_*`
tool as a session board on the strength of the word "board". A test that demanded
a declaration everywhere would have to carry the list of instruments, which is the
registry the declaration exists to avoid. So the five misses above were found by
reading, and the next one will be too.

It also does not stop a re-vendor from **erasing** a declaration in a vendored
copy: `recopy_with_stamp` preserves the stamp line and nothing else, and
`.murderboard-vendor.json` lists no adapted files. That is filed as
`docs/todo/2026-09-04-a-declaration-in-a-vendored-copy-does-not-survive.md`; the
fix is upstream declaring, not this repo annotating someone else's file harder.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "tools"))

# The vocabulary, verbatim from bfbc375. Each value is the failure the family is
# for -- not the kind of thing the tool is, which is what a name-based classifier
# gets wrong.
FAMILIES = {
    "concurrency": "several sessions, and none can see the others",
    "retrieval": "the rule existed and did not reach the decision",
    "verification": "the check passed and meant nothing",
    "staleness": "the published copy fell behind its source",
    "propagation": "an instrument and the copy of it elsewhere have diverged",
}

SEARCH_DIRS = ("tools", ".claude/hooks", ".githooks")
SKIP_PARTS = {"__pycache__", "matlab_ref"}

DECL_RE = re.compile(r"^#\s*instrument:\s*(.*?)\s*$", re.M)
STAMP_RE = re.compile(r"vendored from ")


def _candidates():
    """Every file in this repo that could carry a declaration.

    Extension is not the filter: `.githooks/pre-commit` has none and is an
    instrument. A shebang or a known script suffix is.
    """
    for d in SEARCH_DIRS:
        base = REPO / d
        if not base.is_dir():
            continue
        for p in sorted(base.rglob("*")):
            if not p.is_file() or SKIP_PARTS & set(p.parts):
                continue
            if p.suffix in {".py", ".sh"}:
                yield p
                continue
            try:
                if p.open("rb").read(2) == b"#!":
                    yield p
            except OSError:
                continue


def _text(p):
    return p.read_text(encoding="utf-8")


def _declarations():
    """{path: family} for every file that declares one."""
    out = {}
    for p in _candidates():
        m = DECL_RE.search(_text(p))
        if m:
            out[p.relative_to(REPO)] = m.group(1)
    return out


def test_every_declared_family_is_a_known_one():
    """A typo or an invented sixth family is a red suite, not a silent tag."""
    declared = _declarations()
    assert declared, "no declarations found at all -- the scan is looking in the wrong place"
    unknown = {str(p): fam for p, fam in declared.items() if fam not in FAMILIES}
    assert not unknown, (
        "instrument declarations naming a family that is not in FAMILIES: %s\n"
        "Either it is a typo, or the vocabulary has genuinely grown -- in which case "
        "add it HERE with the failure it names, so the next reader can look it up." % unknown
    )


def test_no_family_is_defined_without_a_single_member():
    """`staleness` was defined by bfbc375 and used by nothing for three days."""
    used = set(_declarations().values())
    empty = sorted(set(FAMILIES) - used)
    assert not empty, (
        "families defined here but declared by no instrument: %s\n"
        "A family with no members is either a missed declaration (the case that "
        "prompted this check -- tools/site_staleness.py) or a name worth deleting." % empty
    )


def test_a_declaration_never_displaces_a_vendoring_stamp():
    """The line-2 collision that bfbc375 shipped into five vendored copies.

    Asserted through the re-vendor tool's own parser, so this cannot pass while
    the tool it protects disagrees.
    """
    revendor = pytest.importorskip("murderboard_revendor")
    displaced = {}
    for p in _candidates():
        text = _text(p)
        if not STAMP_RE.search(text):
            continue
        line = revendor.misplaced_stamp_line(text, is_json=False)
        if line is not None:
            displaced[str(p.relative_to(REPO))] = line
    assert not displaced, (
        "vendoring stamp is not on the line murderboard_revendor will read, so a "
        "re-vendor would leave it unbumped behind a green check: %s\n"
        "Something was inserted above it. Put the stamp back directly under the "
        "shebang and move the other line below it." % displaced
    )
