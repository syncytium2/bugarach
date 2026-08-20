"""A skipped test and a passing test look identical in a summary line.

Every check of the webapp needs a real browser, because the webapp is JavaScript.
Where there is no browser those tests skip — quietly, by design, so a contributor
without one can still run the suite. The cost is that **an environment which is
supposed to have a browser and has lost it reports success**: the parity
comparisons for five detectors, the tuning sweep, the assessment and the windows
panel all vanish, and the tick stays green.

That is not hypothetical. It is exactly the state CI was in until this file
existed, and the reason every webapp change had to be verified by hand and
described in a pull request as "trust the local run".

So an environment can *declare* that it has a browser, and then it has to have
one. `BUGARACH_REQUIRE_BROWSER=1` turns the silent skip into a loud failure.
Nothing else changes: unset, the suite behaves as before.
"""

from __future__ import annotations

import os

import pytest

REQUIRED = os.environ.get("BUGARACH_REQUIRE_BROWSER") == "1"


def test_a_browser_is_available_where_one_is_required():
    """Fails only where the environment says a browser is expected — CI sets
    that. Everywhere else this reports why it stood aside rather than passing
    silently, because "skipped" and "there is nothing to check" are different
    statements and only one of them is true here."""
    if not REQUIRED:
        pytest.skip("BUGARACH_REQUIRE_BROWSER is not set — browser tests may "
                    "skip, and a green run here says nothing about the webapp")

    try:
        from playwright.sync_api import sync_playwright
    except ImportError as e:                              # pragma: no cover
        pytest.fail(
            f"BUGARACH_REQUIRE_BROWSER=1 but playwright is not installed ({e}). "
            f"Every webapp parity test is skipping and the run is green anyway.")

    with sync_playwright() as p:
        try:
            browser = p.chromium.launch()
        except Exception as e:                            # noqa: BLE001
            pytest.fail(
                f"BUGARACH_REQUIRE_BROWSER=1 but chromium will not launch "
                f"({type(e).__name__}: {e}). Install it with "
                f"`python -m playwright install --with-deps chromium`. Until "
                f"then every webapp parity test skips and green means only that "
                f"the Python passed.")
        browser.close()


def test_the_webapp_suite_is_not_empty():
    """The other half of the same worry. A browser that launches proves nothing
    if the files that would drive it have been renamed or removed, so the count
    is asserted rather than assumed."""
    from pathlib import Path

    files = sorted(Path(__file__).parent.glob("test_webapp_*.py"))
    assert len(files) >= 4, (
        f"only {len(files)} webapp test file(s) found — if these were renamed, "
        f"the browser guard above is now guarding nothing")
