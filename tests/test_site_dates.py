"""Every published page says when the site was born and when this version was made.

Tony, 2026-08-23: *"all our websites need a born on date and the date of the
current version."*

Both halves earn their place. The born-on date is what tells a reader the thing
has existed for a while rather than appearing yesterday. The version date is what
tells them whether what they are looking at is current — which on this site is a
live question, because nothing publishes it automatically and the page can sit
weeks behind `main` while looking exactly like a fresh one
(`docs/todo/2026-08-20-nothing-publishes-the-site-so-it-goes-stale.md`, and
`tools/site_staleness.py`, which exists because of it).

The interesting test here is the last one: the version date must come from the
commit, not the clock.
"""

from __future__ import annotations

import re
import subprocess
from pathlib import Path

import pytest

from tools.build_site import (SITE_BORN, STAMP_MARKER, date_stamp, meta_stamp,
                              stamp_html)

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "site"

#: Built pages that must carry the stamp. `viewer.html` is deliberately absent —
#: it is a byte-for-byte copy of the hand-written source page, pinned that way by
#: `test_lab_server.py`, so its dates belong in the source rather than injected
#: by the build. See the comment at that copy in `tools/build_site.py`.
STAMPED = ("index.html", "landscape.html", "diagnostic.html")

ISO = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def test_the_born_date_is_a_written_down_constant_not_a_derivation():
    """A born-on date computed at build time is one rename away from being wrong.

    `git log --reverse -- <path>` resets the day a directory moves, and a
    first-published date that quietly becomes last Tuesday is worse than none:
    it is a fabricated provenance value that reads exactly like a real one. So
    the date is a constant with its commit named in the docstring, and the only
    way it changes is somebody editing it on purpose.
    """
    assert ISO.match(SITE_BORN), f"{SITE_BORN!r} is not an ISO date"
    assert SITE_BORN == "2026-08-13", (
        "the born-on date moved. It is the day the site first existed (f84e8d2) "
        "and there is no legitimate reason for it to change — if the site was "
        "genuinely restarted, say so in SITE_BORN's docstring as well.")


def test_the_version_date_is_the_commits_date_not_todays():
    """Two builds of one commit must produce identical bytes.

    `test_lab_server.py` pins the viewer copy byte-for-byte, and
    `tools/site_staleness.py` identifies the deployed version by hashing what is
    served. A wall-clock timestamp would break both, and would tell a reader
    nothing the commit does not already say.
    """
    head = subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=ROOT,
                          capture_output=True, text=True).stdout.strip()
    want = subprocess.run(["git", "log", "-1", "--format=%cs", head], cwd=ROOT,
                          capture_output=True, text=True).stdout.strip()
    if not head or not want:
        pytest.skip("no git history here")
    stamp = date_stamp(head)
    assert want in stamp, f"expected the commit date {want} in {stamp!r}"
    assert date_stamp(head) == stamp, "the stamp is not reproducible"


def test_a_page_with_no_head_or_body_still_gets_its_dates():
    """Half this site's pages are HTML5 without explicit html/head/body tags.

    `index.html` and `landscape.html` both are. The first version of the build's
    own check looked for the `<meta>` marker and reported those two unstamped
    when they were fine — so the marker lives on the visible element, which every
    shape gets.
    """
    out = stamp_html("<p>a fragment</p>", "abc1234")
    assert STAMP_MARKER in out
    assert "First published" in out


def test_a_page_with_a_head_gets_the_machine_readable_half_too():
    # A whole document, doctype first, because SAP005 reads how the literal
    # OPENS: a string starting `<html`/`<head`/`<title` is a page being built
    # without a charset in front of it. Writing the fixture as a real document
    # satisfies the rule honestly instead of dodging it.
    page = '<!doctype html>\n<meta charset="utf-8">\n<head></head><body>x</body>'
    out = stamp_html(page, "abc1234")
    assert 'name="bugarach:born"' in out
    assert STAMP_MARKER in out
    assert out.index("bugarach:born") < out.index("</head>")


def test_stamping_twice_does_not_stack_footers():
    once = stamp_html("<body>x</body>", "abc1234")
    assert stamp_html(once, "abc1234") == once
    assert once.count("First published") == 1


def test_the_commit_is_shown_beside_the_dates():
    """The date says how current; the sha says exactly which. A reader reporting
    a problem can quote one line and it is enough to reproduce the page."""
    assert "abc1234" in date_stamp("abc1234")
    assert "abc1234" in meta_stamp("abc1234")


@pytest.mark.parametrize("page", STAMPED)
def test_every_built_page_carries_both_dates(page):
    p = SITE / page
    if not p.is_file():
        pytest.skip("no built site/ here — run tools/build_site.py")
    body = p.read_text(encoding="utf-8")
    assert STAMP_MARKER in body, (
        f"{page} was published with no born-on date and no version date")
    m = re.search(r'First published (\S+) · this version (\S+)', body)
    assert m, f"{page} carries the marker but not the readable line"
    assert m.group(1) == SITE_BORN
    assert ISO.match(m.group(2)) or m.group(2) == "unknown"


def test_the_viewer_is_the_one_page_the_build_does_not_stamp():
    """And it is on purpose, so record why here rather than leaving a hole.

    `site/viewer.html` is a byte-for-byte copy of `docs/site/raster_viewer.html`,
    guarded by `test_lab_server.py` so the build cannot quietly transform a page
    that promises its reader it reaches nothing. Injecting a footer would mean
    loosening that guard. The dates belong in the source page instead, where a
    reader auditing the promise can see them.
    """
    p = SITE / "viewer.html"
    if not p.is_file():
        pytest.skip("no built site/ here — run tools/build_site.py")
    src = (ROOT / "docs" / "site" / "raster_viewer.html").read_bytes()
    assert p.read_bytes() == src, (
        "the build has started transforming viewer.html — if that is deliberate, "
        "this test and test_lab_server.py's byte-identity guard both need to say "
        "what transformation is allowed")
