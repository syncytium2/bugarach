"""The committed page is what the detector folder assembles to.

`docs/site/raster_viewer.html` is generated from `viewer.template.html` plus
`docs/site/detectors/*.js`, and it is **committed** — so `git diff` still shows
what an outside lab will actually run, which is how three separate sessions
caught each other's mistakes in that file on 2026-08-29.

The cost of committing a generated file is that it can go stale, and the failure
is quiet: somebody edits a detector object, does not rebuild, and the page keeps
the old code while the source says otherwise. That is what this pins.

The other half — somebody hand-edits the page between the markers and the next
build discards it — has the same test: the page and the sources disagree, and it
fails here rather than in a browser.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SITE = ROOT / "docs" / "site"


def test_the_page_matches_what_its_sources_assemble_to():
    out = subprocess.run(
        [sys.executable, str(ROOT / "tools" / "assemble_viewer.py"), "--check"],
        capture_output=True, text=True, cwd=ROOT)
    assert out.returncode == 0, out.stderr or out.stdout


def test_every_object_file_registers_exactly_one_detector():
    """One file, one detector — the property that makes deletion a removal.

    A file registering two detectors would make "delete the file" ambiguous, and
    one registering none is a file that looks like a detector and is not.
    """
    import re
    files = sorted(p for p in (SITE / "detectors").glob("*.js")
                   if not p.name.startswith("_"))
    assert files, "docs/site/detectors is empty — the folder is the mechanism"
    for p in files:
        keys = re.findall(r'registerDetector\(\s*\{\s*key:\s*"([a-z_]+)"',
                          p.read_text(encoding="utf-8"))
        assert len(keys) == 1, f"{p.name} registers {keys}, expected exactly one"
        assert keys[0] == p.stem, (
            f"{p.name} registers '{keys[0]}' — the filename is the key, so that a "
            f"reader can find a detector's code from its name on screen")


def test_a_detector_that_left_the_literal_is_not_in_it_twice():
    """Converted detectors must be gone from `const DETECTORS`, not duplicated.

    `registerDetector` throws on a duplicate key, so this would be caught at run
    time in a browser — which is the worst place to find it and the least likely
    to be looked at.
    """
    import re
    page = (SITE / "raster_viewer.html").read_text(encoding="utf-8")
    registered = set(re.findall(r'registerDetector\(\s*\{\s*key:\s*"([a-z_]+)"', page))
    literal_start = page.index("const DETECTORS = {")
    literal_end = page.index("\n};\n", literal_start)
    literal = page[literal_start:literal_end]
    for key in registered:
        assert not re.search(rf"^\s{{2}}{key}:\s*\{{", literal, re.M), (
            f"'{key}' is both registered from its object file and still an entry "
            f"in the DETECTORS literal")
