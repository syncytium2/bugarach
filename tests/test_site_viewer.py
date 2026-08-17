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
    text = VIEWER.read_text(encoding="utf-8")
    # the comment at the top NAMES the things it must not contain, so strip
    # comments before looking — otherwise the promise trips its own check
    return re.sub(r"<!--.*?-->", "", text, flags=re.S)


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
    smuggled = re.search(r"(\d+\.\d+\s*,\s*){5}\d+\.\d+", body)
    assert not smuggled, f"the page must not carry event times: {smuggled}"


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


def test_the_index_links_the_viewer():
    from tools.build_site import INDEX

    assert 'href="viewer.html"' in INDEX
    assert "never leave your computer" in INDEX
