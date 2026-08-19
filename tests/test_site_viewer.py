"""The published raster viewer promises the reader something. Check it.

The page tells whoever opens it that their recordings never leave their
computer. That is not a policy, it is a property of the file: a page with no
way to reach the network cannot send anything, and a page that grows one can,
whatever the paragraph still says. So the claim is tested rather than trusted —
the same reason `tools/build_site.py` refuses to publish it otherwise.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
VIEWER = ROOT / "docs" / "site" / "raster_viewer.html"

# every way a page can talk to a host, including the ones that do not look
# like a request: a script/style/img/iframe src is a fetch the browser makes
# on the page's behalf
NETWORK = (
    "fetch(", "XMLHttpRequest", "sendBeacon", "WebSocket(", "EventSource(",
    "import(", "<script src", "<link rel=\"stylesheet\"", "<iframe", "<img",
    "@import",
)


def _body() -> str:
    """The page with every comment removed.

    Comments are stripped because they NAME the things the page must not do —
    the header explains there is no `fetch(`, and a note in the script quotes
    the injection that motivated building nodes instead of markup. A check that
    reads those as code fires on the explanation of why it will never fire,
    which is the fastest way to get a real check deleted.
    """
    text = VIEWER.read_text(encoding="utf-8")
    text = re.sub(r"<!--.*?-->", " ", text, flags=re.S)       # HTML
    text = re.sub(r"/\*.*?\*/", " ", text, flags=re.S)        # JS block
    return re.sub(r"^\s*//[^\n]*", " ", text, flags=re.M)     # JS line


def test_the_viewer_page_exists():
    assert VIEWER.is_file(), f"{VIEWER} is what the site publishes as viewer.html"


@pytest.mark.parametrize("needle", NETWORK)
def test_the_viewer_cannot_reach_the_network(needle):
    assert needle not in _body(), (
        f"{VIEWER.name} contains {needle!r}. The page tells the reader their "
        f"files never leave their computer; that is only true while it reaches "
        f"nothing. Draw it inline or drop the claim — do not keep both.")


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
