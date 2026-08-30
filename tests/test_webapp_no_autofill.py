"""No control on this page may be offered to a password manager.

Tony, 2026-08-27, on the sweep range boxes the day they shipped: *"lastpass is
trying to put a password into the from box on the sweep page."*

Not cosmetic, which is why it is tested rather than noted. A manager that fills
one of these writes a number the sweep then **searches**, and nothing on the
panel distinguishes a value somebody typed from one something typed for them.

The decision recorded here is the scope. The page had no autofill hint anywhere
— fifty inputs, not one attribute — so "only the new boxes are broken" and "they
always were and nobody looked" were both live readings, and only a manager
installed in a real browser could tell them apart. Covering every input settles
it without needing that: none of them is a credential, so the cost of the
superset is zero and the cost of guessing wrong is a silently altered sweep.

The count is asserted as "every input", never as a number, so adding a control
does not fail this file — shipping one without the attributes does.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
VIEWER = ROOT / "docs" / "site" / "raster_viewer.html"

# Comments NAME the thing being checked — the block above `noAutofill` writes
# `<input>` in prose to say that every one of them carries these attributes — so
# a scan that reads comments fires on its own explanation. `test_site_viewer.py`
# learned this first, about the network guard; same import, same reason.
sys.path.insert(0, str(ROOT / "tools"))
from build_site import strip_comments  # noqa: E402

# Five, because the managers do not agree on one and `autocomplete` is the one
# they most reliably ignore on a field they think is credential-shaped.
REQUIRED = ["autocomplete=\"off\"", "data-lpignore=\"true\"", "data-1p-ignore",
            "data-bwignore", "data-form-type=\"other\""]

INPUT = re.compile(r"<input\b[^>]*>")


def _inputs() -> list[str]:
    return INPUT.findall(strip_comments(VIEWER.read_text(encoding="utf-8")))


def test_the_page_still_has_inputs_to_check():
    """A guard that passes because it found nothing is not a guard."""
    assert len(_inputs()) > 40, (
        "fewer inputs than expected — if the panel was rewritten, check this "
        "file still points at the controls")


@pytest.mark.parametrize("attr", REQUIRED)
def test_every_input_in_the_markup_refuses_autofill(attr):
    missing = [t for t in _inputs() if attr not in t]
    assert not missing, (
        f"{len(missing)} input(s) carry no {attr}. A password manager will "
        f"offer to fill them, and in the sweep range boxes that writes a "
        f"setting the sweep then searches. First: {missing[0][:120]}")


def test_inputs_built_in_javascript_get_it_too():
    """The range boxes are created at runtime, so markup cannot carry theirs."""
    body = VIEWER.read_text(encoding="utf-8")
    made = re.findall(r'document\.createElement\("input"\)', body)
    wrapped = re.findall(r'noAutofill\(document\.createElement\("input"\)\)', body)
    assert made and len(made) == len(wrapped), (
        f"{len(made) - len(wrapped)} input(s) are created in JS without going "
        f"through noAutofill()")


def test_the_helper_sets_every_attribute_the_markup_carries():
    """One list, two places, and they have to agree — otherwise a runtime
    control is protected against a different set of managers than a static one."""
    body = VIEWER.read_text(encoding="utf-8")
    block = body[body.index("const NO_AUTOFILL"):body.index("function noAutofill")]
    for attr in REQUIRED:
        name = attr.split("=")[0]
        assert name in block, (
            f"NO_AUTOFILL does not set {name}, but the markup carries it")


# ---------------------------------------------------------------------------
# and the same thing on the page as it actually runs


@pytest.fixture(scope="module")
def page():
    pytest.importorskip("playwright.sync_api",
                        reason="the runtime controls only exist in a browser")
    from playwright.sync_api import sync_playwright

    with sync_playwright() as p:
        try:
            browser = p.chromium.launch()
        except Exception as e:                        # noqa: BLE001
            pytest.skip(f"no chromium available: {type(e).__name__}")
        try:
            pg = browser.new_page()
            pg.goto(VIEWER.as_uri(), wait_until="load")
            yield pg
        finally:
            browser.close()


def test_every_input_on_the_live_page_refuses_autofill(page):
    """Markup and runtime together — this is the check that would have caught
    the original defect, because the range boxes did not exist in the file."""
    bad = page.evaluate(
        """(attrs) => [...document.querySelectorAll("input")]
             .filter(n => attrs.some(a => !n.hasAttribute(a)))
             .map(n => n.id || n.type)""",
        ["autocomplete", "data-lpignore", "data-1p-ignore", "data-bwignore",
         "data-form-type"])
    assert bad == [], f"inputs a manager may still fill: {bad}"


def test_the_sweep_range_boxes_specifically(page):
    """The three Tony reported, named, so the report cannot regress quietly."""
    page.evaluate("""() => {
      for (const k of buildDetectors()) {
        const b = document.getElementById("tPick_" + k);
        if (b && !b.disabled) b.checked = true;
      }
      paintRanges();
    }""")
    bad = page.evaluate(
        """() => sweptDetectors().flatMap(k => ["from", "to", "n"]
             .map(p => document.getElementById("tRange_" + k + "_" + p))
             .filter(n => !n || n.getAttribute("data-lpignore") !== "true")
             .map(n => n ? n.id : "missing"))""")
    assert bad == [], bad
