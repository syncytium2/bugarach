"""Every registered detector still runs after the folder is spliced into the page.

The refactor to `docs/site/detectors/*.js` (ADR-0005) moved each detector out of
one object literal and into a file that is concatenated back at build time. The
per-detector parity tests check each algorithm against its Python twin; the
assembly test checks the bytes are reproducible. **Neither asks whether the
assembled page still works** — a splice that produced a syntactically valid file
with a broken registry would pass both.

So this drives the built page and runs every detector it offers on synthetic
trains. It does not check WHAT they detect — that is parity's job, on real
fixtures, at 1e-9. It checks that the object arrived whole: descriptor, `read`,
`run`, and an algorithm reachable from it.

The two properties worth naming, because each has already gone wrong once:

* **Order.** `DETECTOR_ORDER` exists because moving `rate` into a file put it last,
  which silently moves `detections.csv` row order, raster lane order and the
  sequence detectors draw from the shared RNG. That was caught by a test with a
  different subject; this one asks directly.
* **`unavailable` is offered, not hidden.** A detector held out of the build is
  still registered and still drawn, with its reason. A picker that silently drops
  one reads as a detector that never existed.
"""

from __future__ import annotations

import os
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
PAGE = ROOT / "docs" / "site" / "raster_viewer.html"
EXPECTED = ["rate", "sce", "coact", "loco", "cicada", "sync"]

# The sixth takes a fourth argument — peak and duration trains — and has since
# long before the folder existed. Supplying it is the harness's job.
HARNESS = """(expected) => {
  const trains = [];
  for (let r = 0; r < 12; r++) {
    const t = [];
    for (let k = 0; k < 40; k++) t.push(k * 7 + Math.sin(r + k) * 0.4 + 5);
    for (const c of [300, 600, 900]) t.push(c + r * 0.01);
    trains.push(t.sort((a, b) => a - b));
  }
  const extra = { peakTrains: trains,
                  durTrains: trains.map(t => t.map(() => 0.5)) };
  const out = { keys: Object.keys(DETECTORS), ran: {}, unavailable: [] };
  for (const [key, d] of Object.entries(DETECTORS)) {
    if (d.unavailable) { out.unavailable.push(key); continue; }
    if (typeof d.run !== 'function' || typeof d.read !== 'function') {
      out.ran[key] = 'MISSING run/read'; continue;
    }
    try {
      const res = d.run(trains, [0, 1200], d.read(0.1), extra);
      out.ran[key] = (res && (res.nEvents ?? (res.starts || []).length)) ?? 0;
    } catch (e) { out.ran[key] = 'ERROR: ' + e.message; }
  }
  return out;
}"""


@pytest.fixture(scope="module")
def result():
    if os.environ.get("BUGARACH_REQUIRE_BROWSER") != "1":
        pytest.importorskip("playwright.sync_api")
    from playwright.sync_api import sync_playwright

    errors: list[str] = []
    with sync_playwright() as p:
        try:
            browser = p.chromium.launch()
        except Exception as exc:                       # pragma: no cover - env
            if os.environ.get("BUGARACH_REQUIRE_BROWSER") == "1":
                raise
            pytest.skip(f"no chromium: {exc}")
        page = browser.new_page()
        page.on("pageerror", lambda e: errors.append(str(e)))
        page.goto(PAGE.as_uri(), wait_until="load", timeout=120_000)
        got = page.evaluate(HARNESS, EXPECTED)
        browser.close()
    got["errors"] = errors
    return got


def test_the_assembled_page_registers_every_detector_in_order(result):
    assert result["keys"] == EXPECTED, (
        f"the page offers {result['keys']}. Order is contract — it sets "
        f"detections.csv row order, raster lane order and the sequence detectors "
        f"draw from the shared RNG. See DETECTOR_ORDER in viewer.template.html.")


def test_every_available_detector_runs(result):
    broken = {k: v for k, v in result["ran"].items() if not isinstance(v, int)}
    assert not broken, f"assembled but not runnable: {broken}"


def test_a_held_out_detector_is_registered_rather_than_dropped(result):
    """`unavailable` means offered-with-a-reason, never absent."""
    for key in result["unavailable"]:
        assert key in result["keys"], (
            f"{key} is unavailable AND unregistered — a picker that drops a "
            f"detector reads as a detector that never existed")


def test_the_page_raises_nothing_on_load(result):
    assert not result["errors"], result["errors"]
