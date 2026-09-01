"""Serve the built site and walk it, because nothing else in this suite renders a page.

`docs/deploy.md` says it in terms — *"So: serve the payload and open it"* — and then
asks a human to click every nav link on every page before uploading. That
instruction has already paid twice:

- **2026-08-23.** Somebody finally served the build and walked it. Two of the four
  pages had no nav bar at all and the front page's hero had been built with no
  detections in it. Neither was visible from `file://`, and neither was loud
  enough to notice in the build's own output.
- **2026-09-01.** The same walk found `diagnostic.html` scrolling 231px sideways
  at a 1280 viewport and dragging the nav bar off the left edge — see
  ``docs/todo/2026-09-01-the-diagnostic-page-scrolls-sideways-and-takes-the-nav-with-it.md``.

Both times the instruction was right and both times it ran **on a deploy** rather
than on a commit, which is to say: only when someone remembered. `tests/
test_site_coherence.py` proves every link on every page resolves, and it does that
against the markup in 0.06s without ever laying a page out. A nav bar can resolve
perfectly and still not be on the page.

**What this costs, stated honestly.** One site build, measured at 37s, in a
session-scoped fixture, plus a few seconds of chromium per page. CI already
installs chromium (`.github/workflows/ci.yml` runs `playwright install --with-deps
chromium`), so nothing new is provisioned. It skips rather than fails wherever
Playwright is absent, which is the same bargain every other browser test here makes.

**Why 1280.** It is the narrowest common desktop width, so a page that overflows
here overflows on a laptop. Narrow-viewport behaviour is deliberately not asserted:
the front page's figure is *supposed* to scroll inside its own box below 44rem,
which is what #439 built, and a blanket no-overflow rule at phone widths would
forbid the fix rather than check it.
"""

from __future__ import annotations

import http.server
import socketserver
import subprocess
import sys
import threading
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
SITE = REPO / "site"

#: The four pages the build declares, and the four links every nav bar carries.
#: Deliberately written out rather than derived from `build_site.PAGES`: a test
#: that imports the builder's own list agrees with the builder by construction
#: and would have passed on the day two pages shipped with no bar at all.
PAGES = ["index.html", "viewer.html", "diagnostic.html", "learned_detector.html"]

VIEWPORT = {"width": 1280, "height": 900}


@pytest.fixture(scope="session")
def built_site():
    """The real payload, built the way `npm run predeploy` builds it.

    Not a fixture directory and not a stripped-down build: the thing this checks
    is the artifact that gets uploaded, and a cheaper stand-in would be checking
    something nobody serves. `site/` is gitignored, so this leaves no diff.
    """
    pytest.importorskip(
        "playwright.sync_api",
        reason="this test renders pages; with no browser there is nothing to render in")
    proc = subprocess.run(
        [sys.executable, str(REPO / "tools" / "build_site.py")],
        cwd=REPO, capture_output=True, text=True)
    if proc.returncode != 0:
        pytest.fail(
            f"the site build refused, so there is nothing to walk:\n"
            f"{proc.stderr[-2000:]}")
    missing = [p for p in PAGES if not (SITE / p).exists()]
    assert not missing, f"the build reported success but did not write {missing}"
    return SITE


@pytest.fixture(scope="session")
def served(built_site):
    """`site/` over HTTP on an ephemeral port.

    **Port 0 on purpose.** Several sessions run against this repo at once
    (`docs/session_protocol.md`), so a hardcoded port is a collision waiting for
    a busy afternoon. The OS picks one and the test never claims a shared
    resource.

    HTTP rather than `file://` is the entire point — see the module docstring.
    It still does not reproduce the edge: `docs/deploy.md` has the table of what
    localhost cannot tell you, and the biggest item is that Cloudflare serves
    `/viewer` where this serves `/viewer.html`.
    """
    handler = _handler_for(built_site)
    with socketserver.TCPServer(("127.0.0.1", 0), handler) as httpd:
        t = threading.Thread(target=httpd.serve_forever, daemon=True)
        t.start()
        try:
            yield f"http://127.0.0.1:{httpd.server_address[1]}"
        finally:
            httpd.shutdown()


def _handler_for(directory: Path):
    class Handler(http.server.SimpleHTTPRequestHandler):
        def __init__(self, *a, **kw):
            super().__init__(*a, directory=str(directory), **kw)

        def log_message(self, *a):        # a served page per test is not news
            pass

    return Handler


@pytest.fixture(scope="session")
def browser():
    from playwright.sync_api import sync_playwright

    with sync_playwright() as p:
        b = p.chromium.launch()
        try:
            yield b
        finally:
            b.close()


def _open(browser, url):
    """Load one page and report what a reader would meet: status, nav, errors, layout."""
    page = browser.new_page(viewport=VIEWPORT)
    errors = []
    page.on("console", lambda m: errors.append(m.text) if m.type == "error" else None)
    page.on("pageerror", lambda e: errors.append(f"pageerror: {e}"))
    resp = page.goto(url, wait_until="load")
    # The diagnostic and the viewer lay out through Bokeh, which sizes itself
    # after load; measuring before it settles reads a layout no human sees.
    page.wait_for_timeout(3000)
    facts = page.evaluate("""() => {
        const doc = document.documentElement;
        return {scrollW: doc.scrollWidth, clientW: doc.clientWidth,
                navLinks: [...document.querySelectorAll('nav.site a')]
                            .map(a => a.getAttribute('href'))};
    }""")
    facts["status"] = resp.status
    facts["errors"] = errors
    page.close()
    return facts


@pytest.mark.parametrize("page_name", PAGES)
def test_every_page_serves_and_carries_the_whole_nav(browser, served, page_name):
    """200, and a bar that reaches every other page.

    The 2026-08-23 failure was not a broken link — it was a bar that was not
    rendered at all, on a page whose links all resolved.
    """
    f = _open(browser, f"{served}/{page_name}")
    assert f["status"] == 200, f"{page_name} served HTTP {f['status']}"
    assert f["navLinks"] == PAGES, (
        f"{page_name} carries nav links {f['navLinks']}, expected every page: "
        f"{PAGES}. A page a reader cannot leave is a dead end, and link-resolution "
        f"tests cannot see this because the links they check are in the template.")


@pytest.mark.parametrize("page_name", PAGES)
def test_no_page_reports_a_console_error(browser, served, page_name):
    f = _open(browser, f"{served}/{page_name}")
    assert not f["errors"], (
        f"{page_name} logged {len(f['errors'])} console error(s); first: "
        f"{f['errors'][0][:300]}")


@pytest.mark.parametrize("page_name", PAGES)
def test_no_page_scrolls_sideways_at_desktop_width(browser, served, page_name):
    """Wide content scrolls in its own box; the page body does not.

    `diagnostic.html` is a **strict** xfail rather than an exclusion. Marking it
    `strict` is the point: the day somebody fixes the Panel layout, this test goes
    red and names the todo to close, instead of passing quietly and leaving a
    finished repair looking like unfinished work.
    """
    if page_name == "diagnostic.html":
        pytest.xfail(
            "known, filed, and not this test's to fix: docs/todo/"
            "2026-09-01-the-diagnostic-page-scrolls-sideways-and-takes-the-nav-"
            "with-it.md — the figure's Panel column declares 1511px against a "
            "1280 viewport, so the page scrolls 231px sideways and the nav bar "
            "leaves the window. The width is the layout's, not the page shell's")
    f = _open(browser, f"{served}/{page_name}")
    assert f["scrollW"] <= f["clientW"], (
        f"{page_name} scrolls {f['scrollW'] - f['clientW']}px sideways at "
        f"{VIEWPORT['width']}px. Whatever is wide belongs in a container with "
        f"`overflow-x: auto` — the treatment `.arch` got in #439 and the one "
        f"`learned_detector.src.html` already gives the same figure via `.archwrap` "
        f"— because a page that scrolls sideways takes its nav bar off the screen "
        f"with it.")
