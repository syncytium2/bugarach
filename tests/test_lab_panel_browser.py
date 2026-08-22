"""The training panel, in a real browser, against a real server.

Everything else about the panel can be checked by reading the file: that it
defines no transport, that the shim is not on disk under `docs/site/`. None of
that says the panel *works* — that it appears when the capability exists, stays
hidden when it does not, and that its request reaches the server in a shape the
server accepts.

So this drives the actual page in chromium, served by the actual
`bugarach lab`, with the stub trainer standing in for the fit. The stub is what
makes it affordable: the seam is what is under test, not the numerics.

**CI runs this now**, on the GitHub runner, since the workflow started installing
chromium. That is what makes a green tick say something about the webapp — and it
also means a race in here blocks every pull request, not just the ones that touch
the panel. Wait for the thing you are about to assert on, never for a proxy that
happens to appear first.
"""

from __future__ import annotations

import threading
from pathlib import Path

import pytest

from bugarach import lab as lab_mod

ROOT = Path(__file__).resolve().parents[1]
VIEWER = ROOT / "docs" / "site" / "raster_viewer.html"


@pytest.fixture(scope="module")
def served():
    """The page as `bugarach lab` hands it out — with the shim appended."""
    httpd = lab_mod.make_server(port=0, trainer=lab_mod.StubTrainer(), quiet=True)
    t = threading.Thread(target=httpd.serve_forever, daemon=True)
    t.start()
    try:
        yield f"http://127.0.0.1:{httpd.server_address[1]}"
    finally:
        httpd.shutdown()
        httpd.server_close()
        t.join(timeout=5)


@pytest.fixture(scope="module")
def page_ctx():
    pw = pytest.importorskip("playwright.sync_api",
                             reason="playwright is not installed")
    with pw.sync_playwright() as p:
        try:
            browser = p.chromium.launch()
        except Exception as e:                              # noqa: BLE001
            pytest.skip(f"no chromium available: {type(e).__name__}")
        try:
            yield browser
        finally:
            browser.close()


def _open(browser, url):
    page = browser.new_page()
    page.goto(url, wait_until="load")
    return page


def _reveal_lab(page, timeout: int = 15_000):
    """Wait for the shim to publish the stage, then go to it.

    Two steps now, and they mean different things. Dropping `hidden` is the
    SERVER's doing — the capability arrived, so the stage exists. Putting the
    panel on screen is the READER's, and since the panels became a rail rather
    than an accordion it is a navigation act: exactly one panel is in the column
    at a time, so an un-hidden panel is available, not visible. These tests used
    to wait for visibility and get both at once.
    """
    page.wait_for_selector("#accLab:not([hidden])", state="attached",
                           timeout=timeout)
    page.evaluate("() => showSection('accLab')")
    page.wait_for_selector("#accLab.on", timeout=timeout)


def test_the_panel_is_absent_from_the_page_as_published(page_ctx):
    """The file on disk, opened directly — nobody defined the capability, so the
    panel must stay hidden. This is the published site's behaviour, checked
    rather than argued."""
    page = _open(page_ctx, VIEWER.as_uri())
    try:
        assert page.locator("#accLab").count() == 1, (
            "the panel's markup should be in the page — it is inert, not absent")
        assert page.locator("#accLab").is_hidden(), (
            "the panel is visible on a page nobody injected a shim into. It is "
            "gated on `window.__lab`, which only `bugarach lab` defines.")
        assert page.evaluate("() => window.__lab === undefined")
    finally:
        page.close()


def test_the_panel_appears_when_the_server_serves_it(page_ctx, served):
    """The same file, served by the lab — the shim defines the capability and
    the panel wires itself up."""
    page = _open(page_ctx, served + "/")
    try:
        _reveal_lab(page)
        assert page.evaluate("() => typeof window.__lab.train === 'function'")
        # The chip reports what the server said it can do, rather than assuming.
        #
        # Wait for the CHIP, not for the panel. The panel un-hides as soon as the
        # shim defines the capability; the chip is filled later, by an async
        # capabilities() roundtrip the un-hide does not wait for. Reading it
        # straight afterwards is a race, and on 2026-08-20 it lost — CI failed on
        # 3.13 while the same commit passed on 3.11 and 3.14, on the first day
        # these tests ran in CI at all.
        page.wait_for_function(
            "() => { const el = document.getElementById('cntLab');"
            " const t = el && el.textContent.trim();"
            " return !!t && t !== 'local only'; }", timeout=15000)
        chip = page.locator("#cntLab").inner_text().strip()
        assert chip and chip != "local only", (
            "the chip still reads its published-page placeholder, so "
            "capabilities() never came back")
    finally:
        page.close()


# Delay the capabilities roundtrip inside the page. Doing it from a Playwright
# route handler instead stalls goto() as well, which closes the very window this
# is trying to hold open — 40 unthrottled loads reproduced nothing.
_SLOW_CAPABILITIES = """
const _f = window.fetch;
window.fetch = function (...a) {
  if (String(a[0]).includes('capabilities')) {
    return new Promise(r => setTimeout(() => r(_f.apply(window, a)), 1500));
  }
  return _f.apply(window, a);
};
"""


def test_the_chip_survives_a_slow_capabilities_roundtrip(page_ctx, served):
    """The regression guard for the flake above, made deterministic.

    `wireLab()` sets `acc.hidden = false` and only then awaits
    `api.capabilities()`, so there is a window where the panel is up and the chip
    still reads its published-page placeholder. On this machine the roundtrip beats
    Playwright's own latency and the window never shows; on a loaded CI runner it
    did, and the assertion read `'local only'` — the placeholder itself, not the
    `'unreachable'` that a failed capabilities() would have written. That is what
    identifies it as a race rather than a broken server.

    Slowing the fetch holds the window open on any machine. What is asserted is
    that waiting for the chip still yields the server's answer; the window itself
    is the page's current behaviour, not a contract, so nothing here forbids
    fixing `wireLab()` to await before it un-hides.
    """
    page = page_ctx.new_page()
    page.add_init_script(_SLOW_CAPABILITIES)
    page.goto(served + "/", wait_until="load")
    try:
        _reveal_lab(page)
        page.wait_for_function(
            "() => { const el = document.getElementById('cntLab');"
            " const t = el && el.textContent.trim();"
            " return !!t && t !== 'local only'; }", timeout=15000)
        assert page.locator("#cntLab").inner_text().strip() == "stub", (
            "the chip should report the stub trainer the server actually has")
    finally:
        page.close()


def test_training_through_the_panel_reaches_the_server_and_comes_back(
        page_ctx, served):
    """The seam: the panel builds a spec, the shim posts it, the server runs, and
    a terminal result gets rendered.

    **The stub reports a fold COUNT and no per-fold scores**, deliberately — it
    exists to make the routes testable without paying for a fit. So what is
    asserted here is the round trip, and that the panel says plainly there is
    nothing to read as performance rather than drawing an empty table. The
    table itself is exercised below, on a result shaped like the real trainer's.
    """
    page = _open(page_ctx, served + "/")
    try:
        _reveal_lab(page)
        page.locator("#runLab").click()
        page.wait_for_function(
            "() => /no per-fold|F1/.test("
            "document.getElementById('labOut').textContent)", timeout=60000)
        assert page.evaluate("() => LAB_MODEL") , (
            "the model handle never came back, so detect() would have nothing "
            "to run")
    finally:
        page.close()


def test_the_fold_table_draws_the_spread_and_the_caveat(page_ctx, served):
    """`paintFolds` on a result shaped like the real trainer's.

    Two things it must not omit. The **spread**, because every learned number is
    one training run per fold, so fold-to-fold variation confounds the data with
    the training and a lone mean would hide that. And the **caveat**, because the
    corpus is simulated and nothing measured on it says the model is right about
    a real recording.
    """
    page = _open(page_ctx, served + "/")
    try:
        _reveal_lab(page)
        page.evaluate("""() => {
            paintFolds({ threshold: 0.5, n_params: 1149, per_fold: [
                {fold: 0, f1: 0.60, recall: 0.7, precision: 0.55},
                {fold: 1, f1: 0.70, recall: 0.8, precision: 0.62},
                {fold: 2, f1: 0.65, recall: 0.75, precision: 0.58}] });
        }""")
        assert page.locator("#labOut table tr").count() - 1 == 3
        text = page.locator("#labOut").text_content()
        assert "±" in text, "no spread reported across folds"
        assert "held-out" in text
        assert "simulation" in text.lower(), (
            "the panel must say the score is on a simulation")
    finally:
        page.close()


def test_the_panel_names_which_settings_were_measured_and_which_were_not(
        page_ctx, served):
    """A default must not read as a measurement. The corpus comes from a handful
    of measured statistics and a larger handful of published defaults, and the
    panel says which are which before it is run.

    `text_content` rather than `inner_text`: the note lives inside a collapsed
    `<details>`, and un-rendered text reads as empty otherwise.
    """
    page = _open(page_ctx, served + "/")
    try:
        _reveal_lab(page)
        note = page.locator("#labWhat").text_content()
        assert "not measured from your recordings" in note
        for measured in ("duration_sec", "n_roi", "bg_rate_hz", "jitter_sec"):
            assert measured in note
    finally:
        page.close()


def test_the_panel_offers_no_control_that_re_picks_the_threshold(page_ctx, served):
    """ADR-0001's refusal, at the surface that would have to offer it. The server
    also refuses a threshold in the detect request; this is the half that stops a
    user being invited to send one in the first place.

    Scoped to the **controls**, not the whole panel: the explanatory copy says
    the words "re-tune" and "re-picking" precisely in order to explain why there
    is no such button, and a check that cannot tell a control from the prose
    describing its absence would forbid saying so.
    """
    page = _open(page_ctx, served + "/")
    try:
        _reveal_lab(page)
        controls = page.locator("#accLab .ctl").inner_html().lower()
        for offered in ("thr", "threshold", "retune", "re-tune", "calibrate"):
            assert offered not in controls, (
                f"the panel's controls offer {offered!r}")
    finally:
        page.close()
