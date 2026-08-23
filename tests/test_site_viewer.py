"""The published raster viewer promises the reader something. Check it.

The page tells whoever opens it that their recordings never leave their
computer. That is not a policy, it is a property of the file: a page with no
way to reach the network cannot send anything, and a page that grows one can,
whatever the paragraph still says. So the claim is tested rather than trusted —
the same reason `tools/build_site.py` refuses to publish it otherwise.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
VIEWER = ROOT / "docs" / "site" / "raster_viewer.html"

# The scan lives in the build, and this imports it rather than restating it.
# Restating it is what went wrong: this file already stripped comments before
# scanning, and said in its docstring why, while the build neutralised a single
# hard-coded phrase. The build was the copy that mattered and it was the wrong
# one, so the site sat 233 lines stale behind a guard tripping on a comment.
sys.path.insert(0, str(ROOT / "tools"))
from build_site import NETWORK, strip_comments, viewer_network_leaks  # noqa: E402


def _body() -> str:
    """The page with every comment removed.

    Comments NAME the things the page must not do — the header explains there is
    no `fetch(`, and a note in the script quotes the injection that motivated
    building nodes instead of markup. A check that reads those as code fires on
    the explanation of why it will never fire.
    """
    return strip_comments(VIEWER.read_text(encoding="utf-8"))

def test_the_viewer_page_exists():
    assert VIEWER.is_file(), f"{VIEWER} is what the site publishes as viewer.html"


@pytest.mark.parametrize("needle", NETWORK)
def test_the_viewer_cannot_reach_the_network(needle):
    assert needle not in viewer_network_leaks(
        VIEWER.read_text(encoding="utf-8")), (
        f"{VIEWER.name} contains {needle!r}. The page tells the reader their "
        f"files never leave their computer; that is only true while it reaches "
        f"nothing. Draw it inline or drop the claim — do not keep both.")


@pytest.mark.parametrize("needle", NETWORK)
def test_the_scan_still_fires_on_a_real_call(needle):
    """Prove it can fire, for every primitive, on the real page plus one line.

    Making the scan ignore comments is a loosening, and a loosened guard has to
    show it still catches the thing it was loosened around. Without this, the
    change that unblocked the build would be indistinguishable from one that
    quietly stopped checking.
    """
    poisoned = VIEWER.read_text(encoding="utf-8") + f"\n<script>{needle}</script>\n"
    assert needle in viewer_network_leaks(poisoned)


def test_prose_about_the_network_is_not_a_leak():
    """The specific thing that froze the site for a day: the page *discusses*
    network primitives it does not use, and the scan must tell those apart.

    **This asserts that some primitive is discussed, not how many times.** The
    first version required ``body.count("fetch(") >= 2`` — the header promise plus
    an ADR comment reading "contains no ``fetch(`` and must not grow one". That
    comment arrived in ``6c37e0a``; the guard pinning the count landed in
    ``dc33bb7`` while it happened to be there; ``2b4da41`` reworded it to "a page
    that fetches" three commits later. `main` went red and nothing about the page's
    safety had changed — a comment had been rephrased.

    The count was a property of the prose. The property worth guarding is that
    **the comment-stripping path is exercised by the real page at all**: if nothing
    is ever discussed, ``viewer_network_leaks`` could stop stripping comments and
    every test in this file would still pass. That vacuum is what the original was
    reaching for and missed by naming a number.

    Written over the whole ``NETWORK`` tuple rather than ``fetch(`` alone, so
    rewording one comment cannot empty it while another still carries prose. Two do
    today: ``fetch(`` in the header promise and ``<img`` in a note about why the
    page builds nodes instead of markup.
    """
    raw = VIEWER.read_text(encoding="utf-8")
    leaks = viewer_network_leaks(raw)

    discussed = [n for n in NETWORK if n in raw and n not in leaks]
    assert discussed, (
        "no network primitive is mentioned anywhere in the page, so the "
        "comment-stripping in viewer_network_leaks is never exercised by the real "
        "file and could break silently. Either the page lost the prose explaining "
        "what it deliberately does not do — worth restoring — or this test should "
        "be re-aimed at whatever now carries that explanation.")
    assert not leaks, (
        f"{VIEWER.name} reaches the network via {leaks}. The page tells the reader "
        f"their files never leave their computer; that is only true while it "
        f"reaches nothing.")


def _discussed_but_unused(body: str) -> list[str]:
    """What the test above asserts, factored out so it can be checked adversarially."""
    leaks = viewer_network_leaks(body)
    return [n for n in NETWORK if n in body and n not in leaks]


def test_the_prose_check_notices_a_page_that_stopped_explaining_itself():
    """The vacuum the previous version aimed at and could not express.

    Strip every comment out of the real page and nothing is discussed any more —
    which is exactly the state where `viewer_network_leaks` could stop stripping
    and no test here would notice. The old form tried to catch this by requiring
    two `fetch(` occurrences and instead caught a rewording.
    """
    gutted = strip_comments(VIEWER.read_text(encoding="utf-8"))
    assert not _discussed_but_unused(gutted)


def test_the_prose_check_notices_stripping_being_switched_off(monkeypatch):
    """If comment-stripping regresses, the prose stops reading as prose.

    This is the failure the whole file exists around, from the other direction:
    with stripping disabled the page's own explanations are reported as leaks.
    """
    import build_site
    monkeypatch.setattr(build_site, "strip_comments", lambda b: b)
    leaks = build_site.viewer_network_leaks(VIEWER.read_text(encoding="utf-8"))
    assert leaks, "stripping is disabled and the page's prose is no longer flagged"


def test_a_comment_cannot_hide_a_call_on_the_same_line():
    """Stripping JS line comments must not swallow code that precedes them."""
    assert "fetch(" in viewer_network_leaks("<script>fetch(x); // and a note</script>")


def test_the_viewer_carries_no_data():
    """It ships an empty reader. A recording baked into the page would be
    publishing real data, which FOUNDATIONS §5 does not allow."""
    body = _body()
    assert "data:" not in body, "no embedded payloads"
    # An event train is a long run of DECIMALS: 513.200000, 893.900000, …
    # Integers are not the tell — the tick-step table is `1, 2, 5, 10, 15, 30`
    # and a check that cannot separate those two fires on the wrong thing and
    # gets deleted by the next person, which is worse than not checking.
    #
    # A PARAMETER GRID is the other thing that looks like this, and the warning
    # above came true the first time one arrived: the sweep the tuning step runs
    # over SPIKE-synch's threshold is `0.005, 0.01, 0.02, 0.04, 0.08, 0.12`, six
    # decimals in a row and not a recording of anything. So the run has to be
    # longer than any grid, and has to reach past a minute — a smuggled train is
    # hundreds of onsets over a recording tens of minutes long, and a knob is
    # neither. Sharpened rather than loosened: the run below still matches any
    # real train.
    for run in re.finditer(r"(\d+\.\d+\s*,\s*){7,}\d+\.\d+", body):
        values = [float(v) for v in re.findall(r"\d+\.\d+", run.group(0))]
        assert max(values) < 60.0, (
            f"the page must not carry event times: {run.group(0)[:80]}…")


def test_the_viewer_reads_the_contract_it_claims_to():
    """The reserved names and the missing-value spellings must match
    `bugarach.io`, or the page and the library disagree about the same folder."""
    from bugarach.io import NO_EVENT, RESERVED

    body = _body()
    for name in RESERVED:
        assert f'"{name}"' in body, f"{name} is reserved in io.py but not here"
    for spelling in NO_EVENT:
        token = '""' if spelling == "" else f'"{spelling}"'
        assert token in body, f"{spelling!r} means no-event in io.py but not here"


def test_no_value_is_ever_concatenated_into_markup():
    """The page renders text somebody else wrote — a region label out of
    `regions.csv`, a recording name off a filename — and folders get shared the
    way any file does. Both reached `innerHTML` by concatenation in the first
    version, and a label containing an image tag with an onerror handler ran
    its script. Proven, not theorised: `window.__pwned` came back `1`.

    The rule that replaced it is not "escape it" but "never build markup from a
    value": text goes into a node's `textContent`, which cannot become an
    element however hostile the string. So every `innerHTML` assignment on the
    page must be a literal, and there is nothing to escape.
    """
    script = _body().split("<script>", 1)[-1]
    # mask string literals before splitting on `;`, because a literal here
    # contains one ("…are not recordings;") and a naive split cuts it in half
    masked = re.sub(r'"(?:[^"\\\n]|\\.)*"|\'(?:[^\'\\\n]|\\.)*\'|`(?:[^`\\]|\\.)*`',
                    '""', script)

    bad = []
    for stmt in masked.split(";"):
        if "innerHTML" not in stmt or "=" not in stmt:
            continue
        rhs = stmt.split("innerHTML", 1)[1].split("=", 1)[1]
        if rhs.replace('""', "").strip(" \n+"):        # anything but literals
            bad.append(" ".join(stmt.split())[:120])
    assert not bad, (
        "innerHTML built from a value rather than a literal — build a node and "
        "set textContent instead:\n  " + "\n  ".join(bad))


def test_the_index_links_the_viewer_and_says_where_the_files_go():
    """Read the builder rather than import it: `tools/` is a directory of
    scripts, not an installed package, so importing it passes locally (where
    the repo root happens to be on sys.path) and fails in CI."""
    build = (ROOT / "tools" / "build_site.py").read_text(encoding="utf-8")
    assert 'href="viewer.html"' in build, "the index must link the viewer"
    assert "never leave your computer" in build, (
        "the index sends people to a page that reads their data; it has to say "
        "where that data goes, on the page that sends them")
    assert 'SITE / "viewer.html"' in build, "the build must publish the page"


# --------------------------------------------------------------------------
# When the page was born, and when this version was made.
#
# Tony, 2026-08-23: "all our websites need a born on date and the date of the
# current version." `tools/build_site.py` injects that line into every page it
# generates and deliberately skips this one — `site/viewer.html` is a
# byte-for-byte copy of the source, pinned by `test_lab_server.py` so the build
# cannot quietly transform a page whose promise is that it reaches nothing. A
# build that may not touch the page cannot stamp it, so the stamp is
# hand-written here and these tests are what keep a hand-written date honest.


def _stamp_attr(name: str) -> str:
    m = re.search(rf'{name}="([^"]*)"', VIEWER.read_text(encoding="utf-8"))
    assert m, f"the viewer page carries no {name}"
    return m.group(1)


def test_the_viewer_says_when_it_was_born_and_when_this_version_was_made():
    body = VIEWER.read_text(encoding="utf-8")
    from build_site import SITE_BORN, STAMP_MARKER  # noqa: PLC0415

    assert STAMP_MARKER in body, (
        "the page the README sends people to carries no born-on date and no "
        "version date, so a reader arriving on it cannot tell this month's "
        "build from February's")
    assert _stamp_attr("data-bugarach-born") == SITE_BORN, (
        "the viewer's born-on date disagrees with build_site.SITE_BORN — one "
        "site, one birthday")
    assert re.search(r"First published \d{4}-\d{2}-\d{2} · this version "
                     r"\d{4}-\d{2}-\d{2}", body), (
        "the dates are in the attributes but not in a line a person can read")


def test_the_readable_line_and_the_attributes_say_the_same_thing():
    """Two copies of a fact drift. These are checked against each other, and the
    prose is checked against the one the build writes, so this page cannot end
    up phrasing the same stamp differently from the other three."""
    from build_site import date_stamp  # noqa: PLC0415

    body = VIEWER.read_text(encoding="utf-8")
    born = _stamp_attr("data-bugarach-born")
    version = _stamp_attr("data-bugarach-version-date")
    assert f"First published {born} · this version {version}" in body
    for name, want in (("bugarach:born", born),
                       ("bugarach:version-date", version),
                       ("bugarach:commit", _stamp_attr("data-bugarach-commit"))):
        assert f'<meta name="{name}" content="{want}">' in body, (
            f"the {name} meta disagrees with the visible stamp")
    # The shared phrasing, read off the builder rather than restated here: this
    # page's line has to be recognisable as the same stamp as the other three.
    built = date_stamp("0000000")
    assert f"First published {born} · this version " in built, (
        "build_site.date_stamp no longer phrases the stamp the way this page "
        "mirrors it, so the site now says the same thing two ways:\n"
        f"  builder: {' '.join(built.split())[:120]}\n"
        f"  viewer:  First published {born} · this version {version}")


def test_the_version_date_is_the_date_this_page_last_changed():
    """The whole risk of a hand-written date, closed.

    A date somebody has to remember to bump is a date that stops being true and
    goes on reading exactly as authoritative — the same defect class as the
    fabricated frame interval this page was just fixed for. So it is derived
    from git and compared against what the page says.

    TWO THINGS THIS DELIBERATELY DOES NOT ASK GIT, because either would make the
    answer depend on when the test ran rather than on when the page changed —
    and a gate that goes red on a rerun of an unchanged commit is a gate the next
    lane learns to ignore:

    * **Merge commits are skipped.** A `pull_request` build runs against a merge
      ref GitHub creates *at test time*, so that commit's date is today and is
      not when anybody edited this page. `--no-merges` names the commit that
      actually wrote the content, and its date does not move.
    * **A shallow checkout is skipped, not guessed.** `actions/checkout` clones
      one commit deep by default, which leaves nothing to attribute a change to.
      Saying so is honest; comparing would compare against the boundary commit.
    """
    import datetime  # noqa: PLC0415
    import subprocess  # noqa: PLC0415

    rel = str(VIEWER.relative_to(ROOT))

    def git(*args: str) -> str:
        r = subprocess.run(("git", *args), cwd=ROOT, capture_output=True,
                           text=True)
        return r.stdout.strip() if r.returncode == 0 else ""

    said = _stamp_attr("data-bugarach-version-date")

    # Being edited right now — the one moment the date is easy to get right and
    # easy to forget.
    if git("status", "--porcelain", "--", rel):
        today = datetime.date.today().isoformat()
        assert said == today, (
            f"this page has uncommitted changes, so its version date is being "
            f"set today ({today}) and it says {said}")
        return

    when = git("log", "-1", "--no-merges", "--format=%cs", "--", rel)
    if not when:
        pytest.skip("no non-merge history for the page here — a depth-1 "
                    "checkout does this, and guessing would be worse")
    assert said == when, (
        f"the page says it was last revised {said}; the last commit to write it "
        f"was dated {when}. Bump data-bugarach-version-date, the "
        f"bugarach:version-date meta and the readable line at the bottom of "
        f"docs/site/raster_viewer.html when you edit the page — a version date "
        f"nobody maintains is worse than none, because it still reads as a fact.")


def test_the_page_does_not_claim_a_commit_it_could_not_know():
    """A hand-written page cannot name the commit that contains it — the sha
    does not exist until the commit is made, and naming the previous one would
    have every published copy pointing at the revision before itself.

    `tools/site_staleness.py` resolves the served viewer's commit by hashing its
    bytes against every committed `raster_viewer.html`, which cannot disagree
    with the file it describes. So the attribute names that scheme instead, and
    this test stops a well-meaning edit from filling in a sha that would be
    wrong the moment it was committed.
    """
    got = _stamp_attr("data-bugarach-commit")
    assert got == "content-addressed", (
        f"data-bugarach-commit reads {got!r}. If that is a sha, it names some "
        f"commit other than the one carrying this file.")
